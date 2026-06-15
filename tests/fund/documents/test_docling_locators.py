"""Docling candidate locator 测试。"""

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import get_args

from fund_agent.fund.documents.candidates.locators import (
    build_candidate_anchor_note,
    build_table_block_from_excerpt,
    implemented_locator_normalization_rules,
    implemented_normalization_rules,
    stitch_candidate_tables,
)
from fund_agent.fund.documents.candidates.models import (
    NORMALIZATION_RULE_NAMES,
    CandidateFailureCode,
    NormalizationRuleName,
)
from fund_agent.fund.extractors.models import EvidenceAnchor

FIXTURE_PATH = Path("tests/fixtures/fund/docling_route_a/004393_2025/excerpt.json")


def _fixture() -> dict[str, object]:
    """读取 no-live fixture。

    Args:
        无。

    Returns:
        fixture 字典。

    Raises:
        AssertionError: fixture 不是 JSON object 时抛出。
    """

    payload = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    assert isinstance(payload, dict)
    return payload


def _table(case_id: str) -> dict[str, object]:
    """按 case_id 读取 table excerpt。

    Args:
        case_id: table case ID。

    Returns:
        table excerpt 字典。

    Raises:
        AssertionError: case 缺失时抛出。
    """

    table_excerpts = _fixture()["table_excerpts"]
    assert isinstance(table_excerpts, list)
    for item in table_excerpts:
        if isinstance(item, dict) and item["case_id"] == case_id:
            return item
    raise AssertionError(f"missing table case: {case_id}")


def test_implemented_normalization_rule_names_match_closed_vocabulary() -> None:
    """验证完整实现规则名与闭合词表完全一致。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 实现规则名漂移时抛出。
    """

    assert implemented_normalization_rules() == NORMALIZATION_RULE_NAMES
    assert set(implemented_normalization_rules()) == set(get_args(NormalizationRuleName))
    assert implemented_locator_normalization_rules() == (
        "header_path_reconstruction",
        "repeated_header_exclusion",
        "cross_page_table_stitching",
        "merged_cell_expansion",
        "toc_header_footer_exclusion",
        "row_label_path_generation",
        "column_header_path_generation",
    )


def test_stock_holding_locator_reconstructs_header_and_row_paths() -> None:
    """验证股票明细表 locator 的 header/row path。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: locator 不稳定时抛出。
    """

    table = build_table_block_from_excerpt(
        _table("stock-holding-table-74"),
        section_id="8.3",
        heading_path=("§8 投资组合报告", "8.3 股票投资明细"),
        table_family="portfolio_holding",
    )
    code_cell = next(cell for cell in table.normalized_cells if cell.text_normalized == "00939")
    assert code_cell.column_header_path == ("股票代码",)
    assert code_cell.row_label_path == ("1",)
    assert code_cell.cell_hash
    assert code_cell.locator_hash
    assert "column_header_path_generation" in code_cell.normalization_notes
    assert "row_label_path_generation" in code_cell.normalization_notes


def test_manager_holding_locator_uses_merged_group_label() -> None:
    """验证经理持有表 locator 使用跨行 group label。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: row path 或归一化规则不符合预期时抛出。
    """

    table = build_table_block_from_excerpt(
        _table("manager-holding-table-86"),
        section_id="§9",
        heading_path=("§9 基金份额持有人信息",),
        table_family="holder_info",
    )
    holding_cell = next(cell for cell in table.normalized_cells if cell.text_normalized == "50~100")
    assert holding_cell.row_label_path == (
        "本基金基金经理持有本开放式基金",
        "安信企业价值优选混合A",
    )
    assert holding_cell.column_header_path == ("持有基金份额总量的数量区间（万份）",)
    assert "merged_cell_expansion" in holding_cell.normalization_notes
    assert "cjk_space_repair" in holding_cell.normalization_notes


def test_toc_table_is_excluded_from_candidate_facts() -> None:
    """验证目录表被保留但排除出 fact candidate。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 目录表未被排除时抛出。
    """

    table = build_table_block_from_excerpt(
        _table("toc-table-0"),
        section_id=None,
        heading_path=(),
        table_family="unknown",
    )
    assert table.table_family == "document_index"
    assert table.excluded_reason == "toc"
    assert table.locator_stability == "blocked"


def test_cross_page_stitching_accepts_compatible_tables_and_rejects_header_mismatch() -> None:
    """验证 cross-page stitching 的接受和拒绝路径。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: stitching 结果不符合预期时抛出。
    """

    stock_first = build_table_block_from_excerpt(
        _table("stock-holding-table-74"),
        section_id="8.3",
        heading_path=("§8 投资组合报告", "8.3 股票投资明细"),
        table_family="portfolio_holding",
    )
    second_payload = copy.deepcopy(_table("stock-holding-table-74"))
    second_payload["source_table_index"] = 75
    second_payload["self_ref"] = "#/tables/75"
    second_payload["page_no"] = 54
    second_payload["prov"][0]["page_no"] = 54
    stock_second = build_table_block_from_excerpt(
        second_payload,
        section_id="8.3",
        heading_path=("§8 投资组合报告", "8.3 股票投资明细"),
        table_family="portfolio_holding",
    )
    accepted = stitch_candidate_tables((stock_first, stock_second))
    assert accepted.failure_code is None
    assert accepted.stitched_table is not None
    assert accepted.stitched_table.continuation_group_id == accepted.group_id

    current_period = build_table_block_from_excerpt(
        _table("financial-continuation-61"),
        section_id="7.4",
        heading_path=("§7 年度财务报表", "7.4 风险披露"),
        table_family="financial_statement",
    )
    prior_period = build_table_block_from_excerpt(
        _table("financial-continuation-62"),
        section_id="7.4",
        heading_path=("§7 年度财务报表", "7.4 风险披露"),
        table_family="financial_statement",
    )
    rejected = stitch_candidate_tables((current_period, prior_period))
    assert rejected.stitched_table is None
    assert rejected.failure_code == CandidateFailureCode.TABLE_HEADER_UNSTABLE


def test_candidate_anchor_note_keeps_docling_source_kind_inside_note() -> None:
    """验证 candidate anchor note 不改变 EvidenceAnchor source_kind。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: candidate source kind 泄漏到 public source_kind 时抛出。
    """

    table = build_table_block_from_excerpt(
        _table("stock-holding-table-74"),
        section_id="8.3",
        heading_path=("§8 投资组合报告", "8.3 股票投资明细"),
        table_family="portfolio_holding",
    )
    code_cell = next(cell for cell in table.normalized_cells if cell.text_normalized == "00939")
    note = build_candidate_anchor_note(code_cell)
    anchor = EvidenceAnchor(
        source_kind="annual_report",
        document_year=2025,
        section_id="8.3",
        page_number=code_cell.page_no,
        table_id=code_cell.table_id,
        row_locator="/".join(code_cell.row_label_path),
        note=json.dumps(note, ensure_ascii=False),
    )
    assert anchor.source_kind == "annual_report"
    assert note["candidate_source_kind"] == "docling_pdf_candidate"
    assert note["source_truth_status"] == "not_proven"
    assert note["field_correctness_status"] == "not_proven"

