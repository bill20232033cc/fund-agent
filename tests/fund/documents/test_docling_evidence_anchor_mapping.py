"""Docling 候选 EvidenceAnchor 映射测试。"""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import pytest

from fund_agent.fund.documents.candidates.evidence_anchor_mapping import (
    CandidateEvidenceAnchorMapping,
    map_candidate_document_anchor_candidates,
    map_candidate_locator_to_anchor_candidate,
)
from fund_agent.fund.documents.candidates.representation_export import (
    CandidateExportMode,
    CandidateRepresentationExportEntry,
    CandidateRepresentationRoute,
    build_representation_envelope,
)
from fund_agent.fund.documents.candidates.representation_projection import project_candidate_representation


def _entry(route: CandidateRepresentationRoute = CandidateRepresentationRoute.DOCLING_PDF) -> CandidateRepresentationExportEntry:
    """构造 synthetic candidate entry。

    Args:
        route: 候选 route。

    Returns:
        候选导出 entry。

    Raises:
        无显式抛出。
    """

    return CandidateRepresentationExportEntry(
        sample_id="S1",
        fund_code="004393",
        document_year=2025,
        route=route,
        mode=CandidateExportMode.HANDLED,
        input_artifact_path=Path("cache/eid-artifact-capture/sample/pdf/004393_2025.pdf"),
        accepted_input_sha256="abc123",
        provenance_judgment_path=Path("docs/reviews/docling-full-document-coverage-evidence-controller-judgment-20260616.md"),
        output_path=Path("reports/docling-candidate/004393_2025.json"),
    )


def _summary_metrics() -> dict[str, int | bool]:
    """返回完整 summary metrics。

    Args:
        无。

    Returns:
        summary metrics 字典。

    Raises:
        无显式抛出。
    """

    return {
        "page_count": 100,
        "section_count": 1,
        "heading_count": 1,
        "paragraph_count": 1,
        "table_count": 1,
        "table_cell_count": 1,
        "has_page_number": True,
        "has_bbox": True,
        "has_section_tree": True,
        "has_table_cell_locator": True,
        "has_content_hash": True,
        "has_url_or_source_locator": True,
    }


def _payload(
    *,
    sections: tuple[dict[str, object], ...] | None = None,
    text_blocks: tuple[dict[str, object], ...] | None = None,
    tables: tuple[dict[str, object], ...] | None = None,
    route: CandidateRepresentationRoute = CandidateRepresentationRoute.DOCLING_PDF,
) -> dict[str, object]:
    """构造 candidate representation payload。

    Args:
        sections: section payloads。
        text_blocks: text block payloads。
        tables: table payloads。
        route: 候选 route。

    Returns:
        candidate envelope。

    Raises:
        无显式抛出。
    """

    return build_representation_envelope(
        _entry(route),
        summary_metrics=_summary_metrics(),
        sections=sections if sections is not None else (_section(),),
        headings=(),
        paragraphs=(),
        text_blocks=text_blocks if text_blocks is not None else (_paragraph(),),
        tables=tables if tables is not None else (_table_with_cell(),),
    )


def _section(section_id: str = "sec_8", heading_text: str = "§8 投资组合报告", page_number: int = 60) -> dict[str, object]:
    """构造 section payload。

    Args:
        section_id: section id。
        heading_text: 标题文本。
        page_number: 页码。

    Returns:
        section 字典。

    Raises:
        无显式抛出。
    """

    return {
        "section_id": section_id,
        "source_ref": f"#/texts/{section_id}",
        "heading_text": heading_text,
        "page_number": page_number,
        "bbox": {"l": 1, "t": 2, "r": 3, "b": 4},
    }


def _paragraph(section_id: str = "sec_8", page_number: int = 61) -> dict[str, object]:
    """构造 paragraph payload。

    Args:
        section_id: section id。
        page_number: 页码。

    Returns:
        paragraph 字典。

    Raises:
        无显式抛出。
    """

    return {
        "block_id": "para_1",
        "block_type": "paragraph",
        "section_id": section_id,
        "heading_path": ["§8 投资组合报告"],
        "text": "报告期末股票投资组合文本。",
        "page_number": page_number,
        "bbox": {"l": 10, "t": 20, "r": 30, "b": 40},
    }


def _table_with_cell(
    *,
    table_id: str = "tbl_8_1",
    section_id: str = "sec_8",
    page_number: int = 62,
    cells: list[dict[str, object]] | None = None,
) -> dict[str, object]:
    """构造 table payload。

    Args:
        table_id: 表格 ID。
        section_id: section id。
        page_number: 页码。
        cells: cell payloads。

    Returns:
        table 字典。

    Raises:
        无显式抛出。
    """

    return {
        "table_id": table_id,
        "self_ref": table_id,
        "table_index": 0,
        "section_id": section_id,
        "heading_path": ["§8 投资组合报告"],
        "page_number": page_number,
        "bbox": {"l": 0, "t": 0, "r": 100, "b": 100},
        "row_count": 2,
        "column_count": 2,
        "cell_count": len(cells or [_cell()]),
        "cells": cells or [_cell()],
    }


def _cell(
    *,
    cell_index: int = 0,
    row_start: int | None = 1,
    column_start: int | None = 1,
    source_ref: str = "tbl_8_1",
    page_number: int = 62,
    bbox: dict[str, float | int] | None = None,
) -> dict[str, object]:
    """构造 cell payload。

    Args:
        cell_index: cell index。
        row_start: 起始行。
        column_start: 起始列。
        source_ref: source ref。
        page_number: 页码。
        bbox: bbox。

    Returns:
        cell 字典。

    Raises:
        无显式抛出。
    """

    payload: dict[str, object] = {
        "cell_index": cell_index,
        "row_end": 2,
        "column_end": 2,
        "row_span": 1,
        "column_span": 1,
        "row_header": False,
        "column_header": False,
        "row_label_path": ["股票A"],
        "column_header_path": ["占基金资产净值比例"],
        "text": "1.23%",
        "source_ref": source_ref,
        "bbox": bbox or {"l": 10, "t": 10, "r": 20, "b": 20},
        "cell_hash": f"cell_hash_{cell_index}",
        "locator_hash": f"locator_hash_{cell_index}",
    }
    if row_start is not None:
        payload["row_start"] = row_start
    if column_start is not None:
        payload["column_start"] = column_start
    payload["page_number"] = page_number
    return payload


def test_document_mapping_emits_candidate_wrappers_for_heading_paragraph_table_and_cell() -> None:
    """验证文档级映射输出 candidate wrapper 而非生产 EvidenceAnchor。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 映射结果不符合 candidate-only 边界时抛出。
    """

    document = project_candidate_representation(_payload())
    result = map_candidate_document_anchor_candidates(document, schema_family="S1_full")

    assert len(result.mapped) == 4
    assert result.blocked == ()
    assert all(isinstance(item, CandidateEvidenceAnchorMapping) for item in result.mapped)
    assert "EvidenceAnchor" not in {type(item).__name__ for item in result.mapped}
    assert {item.block_type for item in result.mapped} == {"heading", "paragraph", "table", "cell"}
    cell_mapping = next(item for item in result.mapped if item.block_type == "cell")
    assert cell_mapping.fields.source_kind == "annual_report"
    assert cell_mapping.fields.document_year == 2025
    assert cell_mapping.fields.section_id == "§8"
    assert cell_mapping.fields.table_id == "tbl_8_1"
    assert cell_mapping.fields.row_locator == (
        "cell:r1:c1:idx0;row_label=股票A;column_header=占基金资产净值比例"
    )
    assert cell_mapping.candidate_only is True
    assert cell_mapping.field_correctness_status == "not_proven"
    assert "candidate_only=true" in cell_mapping.fields.note


def test_s1_cell_can_resolve_parent_by_unique_bbox_containment_without_parent_argument() -> None:
    """验证 S1 cell 可通过唯一 bbox containment 定位父表。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: bbox 父表解析失败时抛出。
    """

    document = project_candidate_representation(_payload())
    cell = document.tables[0].cells[0]
    result = map_candidate_locator_to_anchor_candidate(document, cell, schema_family="S1_full")

    assert result.blocked == ()
    assert result.mapped[0].fields.table_id == "tbl_8_1"


def test_s1_cell_blocks_ambiguous_bbox_parent_resolution() -> None:
    """验证 S1 cell 在多表 bbox 同时包含时 fail-closed。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: ambiguous bbox 未阻断时抛出。
    """

    tables = (
        _table_with_cell(table_id="tbl_a", cells=[]),
        _table_with_cell(table_id="tbl_b", cells=[]),
    )
    payload = _payload(tables=tables)
    document = project_candidate_representation(payload)
    cell_document = project_candidate_representation(_payload())
    cell = cell_document.tables[0].cells[0]

    result = map_candidate_locator_to_anchor_candidate(document, cell, schema_family="S1_full")

    assert result.mapped == ()
    assert result.blocked[0].reason_code == "cannot_resolve_parent_table"


def test_s4_s5_s6_cell_blocks_missing_tuple_member() -> None:
    """验证 S4/S5/S6 缺 tuple 成员时阻断 cell 映射。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 缺失 tuple 字段未阻断时抛出。
    """

    table = _table_with_cell(cells=[_cell(row_start=None)])
    document = project_candidate_representation(_payload(tables=(table,)))

    result = map_candidate_document_anchor_candidates(document, schema_family="S4_S5_S6_lightweight")

    assert any(block.reason_code == "missing_cell_position" for block in result.blocked)
    assert not any(item.block_type == "cell" for item in result.mapped)


def test_s4_s5_s6_cell_happy_path_maps_with_exact_tuple() -> None:
    """验证 S4/S5/S6 完整 tuple 能映射 cell candidate。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 完整 tuple 未生成 cell candidate 时抛出。
    """

    document = project_candidate_representation(_payload())

    result = map_candidate_document_anchor_candidates(document, schema_family="S4_S5_S6_lightweight")

    cell_mapping = next(item for item in result.mapped if item.block_type == "cell")
    assert cell_mapping.fields.table_id == "tbl_8_1"
    assert cell_mapping.fields.page_number == 62
    assert cell_mapping.fields.row_locator == (
        "cell:r1:c1:idx0;row_label=股票A;column_header=占基金资产净值比例"
    )


def test_s4_s5_s6_cell_blocks_duplicate_tuple() -> None:
    """验证 S4/S5/S6 重复 tuple 时阻断 cell 映射。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 重复 tuple 未阻断时抛出。
    """

    table = _table_with_cell(
        cells=[
            _cell(cell_index=3, row_start=1, column_start=1),
            _cell(cell_index=3, row_start=1, column_start=1),
        ]
    )
    document = project_candidate_representation(_payload(tables=(table,)))

    result = map_candidate_document_anchor_candidates(document, schema_family="S4_S5_S6_lightweight")

    assert any(block.reason_code == "ambiguous_cell_tuple" for block in result.blocked)
    assert not any(item.block_type == "cell" for item in result.mapped)


def test_s4_s5_s6_maps_without_section_nodes_when_heading_path_is_one_to_one() -> None:
    """验证 S4/S5/S6 缺 section tree 但 heading path 一一映射时可映射。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 一一映射 heading path 未闭环时抛出。
    """

    payload = _payload(sections=())
    document = project_candidate_representation(payload)

    result = map_candidate_document_anchor_candidates(document, schema_family="S4_S5_S6_lightweight")

    assert any(item.block_type == "cell" and item.fields.section_id == "§8" for item in result.mapped)


def test_s4_s5_s6_blocks_without_section_nodes_when_heading_path_is_ambiguous() -> None:
    """验证 S4/S5/S6 缺 section tree 且 heading path 多匹配时阻断。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 多章节 heading path 未阻断时抛出。
    """

    table = {
        **_table_with_cell(),
        "heading_path": ["§8 投资组合报告", "§9 基金份额持有人信息"],
    }
    payload = _payload(sections=(), text_blocks=(), tables=(table,))
    document = project_candidate_representation(payload)

    result = map_candidate_document_anchor_candidates(document, schema_family="S4_S5_S6_lightweight")

    assert result.mapped == ()
    assert {block.reason_code for block in result.blocked} == {"unstable_section_context"}


def test_missing_section_context_blocks_mapping() -> None:
    """验证缺少章节上下文时不生成候选锚点。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 缺章节上下文仍生成锚点时抛出。
    """

    payload = _payload(
        sections=(),
        text_blocks=({**_paragraph(section_id="unknown"), "heading_path": []},),
        tables=(),
    )
    document = project_candidate_representation(payload)

    result = map_candidate_document_anchor_candidates(document, schema_family="S1_full")

    assert result.mapped == ()
    assert result.blocked[0].reason_code == "missing_section_context"


def test_unstable_section_context_blocks_mapping() -> None:
    """验证多章节 heading path 映射为 unstable_section_context。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 不稳定章节上下文未阻断时抛出。
    """

    payload = _payload(
        text_blocks=(
            {
                **_paragraph(),
                "heading_path": ["§8 投资组合报告", "§9 基金份额持有人信息"],
            },
        ),
        tables=(),
    )
    document = project_candidate_representation(payload)

    result = map_candidate_document_anchor_candidates(document, schema_family="S1_full")

    assert result.mapped[0].block_type == "heading"
    assert result.blocked[0].reason_code == "unstable_section_context"


def test_missing_page_blocks_mapping() -> None:
    """验证缺少页码时不生成候选锚点。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 缺页码仍生成锚点时抛出。
    """

    paragraph = _paragraph()
    paragraph.pop("page_number")
    payload = _payload(text_blocks=(paragraph,), tables=())
    document = project_candidate_representation(payload)

    result = map_candidate_document_anchor_candidates(document, schema_family="S1_full")

    assert any(block.reason_code == "missing_page_number" for block in result.blocked)


def test_non_docling_candidate_is_blocked() -> None:
    """验证非 Docling candidate 不进入本映射 helper。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 非 Docling route 未阻断时抛出。
    """

    document = project_candidate_representation(_payload(route=CandidateRepresentationRoute.PDFPLUMBER_PDF))

    result = map_candidate_document_anchor_candidates(document, schema_family="S1_full")

    assert result.mapped == ()
    assert result.blocked[0].reason_code == "unsupported_source_kind"


@pytest.mark.parametrize(
    ("heading", "expected_section"),
    [
        ("2.1 基金基本情况", "§2"),
        ("§ 2 基金简介", "§2"),
        ("２．１ 基金基本情况", "§2"),
        ("8.4 报告期末按行业分类的股票投资组合", "§8"),
    ],
)
def test_numeric_heading_positive_examples_map_with_closed_family(
    heading: str,
    expected_section: str,
) -> None:
    """验证数字标题 positive case 只在闭合标题族命中时映射。

    Args:
        heading: 合成标题。
        expected_section: 期望年报章节。

    Returns:
        无返回值。

    Raises:
        AssertionError: 标题映射不符合预期时抛出。
    """

    paragraph = {**_paragraph(section_id=""), "heading_path": [heading]}
    document = project_candidate_representation(_payload(sections=(), text_blocks=(paragraph,), tables=()))

    result = map_candidate_document_anchor_candidates(document, schema_family="S1_full")

    assert result.blocked == ()
    assert result.mapped[0].fields.section_id == expected_section


@pytest.mark.parametrize(
    "heading",
    [
        "8.3 任意无关文本",
        "11.1 任意文本",
        "二、基金简介",
        "（二）基金基本情况",
        "第八节 基金投资组合报告",
        "2、基金简介",
    ],
)
def test_unsupported_numeric_heading_patterns_block_as_unsupported_heading_number(heading: str) -> None:
    """验证未授权数字/中文编号标题统一 fail-closed。

    Args:
        heading: 合成标题。

    Returns:
        无返回值。

    Raises:
        AssertionError: 未授权编号标题未阻断时抛出。
    """

    paragraph = {**_paragraph(section_id=""), "heading_path": [heading]}
    document = project_candidate_representation(_payload(sections=(), text_blocks=(paragraph,), tables=()))

    result = map_candidate_document_anchor_candidates(document, schema_family="S1_full")

    assert result.mapped == ()
    assert result.blocked[0].reason_code == "unsupported_heading_number"


def test_toc_section_node_is_excluded_from_body_span_seed() -> None:
    """验证确定性目录节点不作为正文 span 起点。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 目录页被误用为正文起点时抛出。
    """

    sections = (
        _section(section_id="toc_sec_2", heading_text="目录 §2 基金简介", page_number=2),
        _section(section_id="body_sec_2", heading_text="§2 基金简介", page_number=5),
    )
    table = {**_table_with_cell(section_id="", page_number=5, cells=[]), "heading_path": []}
    document = project_candidate_representation(_payload(sections=sections, text_blocks=(), tables=(table,)))

    result = map_candidate_document_anchor_candidates(document, schema_family="S1_full")

    table_mapping = next(item for item in result.mapped if item.block_type == "table")
    assert table_mapping.fields.section_id == "§2"
    assert table_mapping.fields.page_number == 5


def test_unsafe_toc_body_ambiguity_blocks_as_duplicate_section_heading() -> None:
    """验证无法区分 TOC/body 的重复章节 fail-closed。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 不安全重复章节未阻断时抛出。
    """

    sections = (
        _section(section_id="sec_2_a", heading_text="§2 基金简介", page_number=2),
        _section(section_id="sec_2_b", heading_text="§2 基金简介", page_number=5),
    )
    table = {**_table_with_cell(section_id="", page_number=5, cells=[]), "heading_path": []}
    document = project_candidate_representation(_payload(sections=sections, text_blocks=(), tables=(table,)))

    result = map_candidate_document_anchor_candidates(document, schema_family="S1_full")

    assert any(block.reason_code == "duplicate_section_heading" for block in result.blocked)
    assert not any(item.block_type == "table" for item in result.mapped)


def test_duplicate_body_heading_blocks_page_based_propagation() -> None:
    """验证重复正文章节标题阻断受影响 span 内表格映射。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 重复正文标题未阻断时抛出。
    """

    sections = (
        _section(section_id="sec_8_a", heading_text="§8 投资组合报告", page_number=60),
        _section(section_id="sec_8_b", heading_text="§8 投资组合报告", page_number=70),
    )
    table = {**_table_with_cell(section_id="", page_number=62, cells=[]), "heading_path": []}
    document = project_candidate_representation(_payload(sections=sections, text_blocks=(), tables=(table,)))

    result = map_candidate_document_anchor_candidates(document, schema_family="S1_full")

    assert any(block.reason_code == "duplicate_section_heading" for block in result.blocked)
    assert not any(item.block_type == "table" for item in result.mapped)


def test_duplicate_same_page_top_level_body_heading_blocks_page_based_propagation() -> None:
    """验证同页 distinct 顶层章节节点重复时 fail-closed。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 同页重复顶层章节未阻断时抛出。
    """

    sections = (
        _section(section_id="sec_8_a", heading_text="§8 投资组合报告", page_number=60),
        _section(section_id="sec_8_b", heading_text="§8 投资组合报告", page_number=60),
    )
    table = {**_table_with_cell(section_id="", page_number=60, cells=[]), "heading_path": []}
    document = project_candidate_representation(_payload(sections=sections, text_blocks=(), tables=(table,)))

    result = map_candidate_document_anchor_candidates(document, schema_family="S1_full")

    assert any(block.reason_code == "duplicate_section_heading" for block in result.blocked)
    assert not any(item.block_type == "table" for item in result.mapped)


def test_inter_section_monotonic_violation_blocks_affected_span() -> None:
    """验证跨顶层章节起始页倒序时阻断 page propagation。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 倒序章节未阻断时抛出。
    """

    sections = (
        _section(section_id="sec_3", heading_text="§3 主要财务指标", page_number=10),
        _section(section_id="sec_8", heading_text="§8 投资组合报告", page_number=5),
    )
    table = {**_table_with_cell(section_id="", page_number=6, cells=[]), "heading_path": []}
    document = project_candidate_representation(_payload(sections=sections, text_blocks=(), tables=(table,)))

    result = map_candidate_document_anchor_candidates(document, schema_family="S1_full")

    assert any(block.reason_code == "section_order_not_monotonic" for block in result.blocked)
    assert not any(item.block_type == "table" for item in result.mapped)


def test_same_section_child_nodes_do_not_break_monotonic_ordering() -> None:
    """验证同一章节子标题不独立触发跨章节倒序。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 同章节子标题误触发倒序时抛出。
    """

    sections = (
        _section(section_id="sec_3", heading_text="§3 主要财务指标", page_number=10),
        _section(section_id="sec_8_child", heading_text="8.4 报告期末按行业分类的股票投资组合", page_number=58),
        _section(section_id="sec_8", heading_text="§8 投资组合报告", page_number=60),
    )
    table = {**_table_with_cell(section_id="", page_number=59, cells=[]), "heading_path": []}
    document = project_candidate_representation(_payload(sections=sections, text_blocks=(), tables=(table,)))

    result = map_candidate_document_anchor_candidates(document, schema_family="S1_full")

    table_mapping = next(item for item in result.mapped if item.block_type == "table")
    assert table_mapping.fields.section_id == "§8"
    assert not any(block.reason_code == "section_order_not_monotonic" for block in result.blocked)


def test_page_based_table_inherits_stable_section_span() -> None:
    """验证无显式章节的 table 可从稳定页码 span 继承章节。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: page-based 章节继承失败时抛出。
    """

    sections = (
        _section(section_id="sec_3", heading_text="§3 主要财务指标", page_number=10),
        _section(section_id="sec_8", heading_text="§8 投资组合报告", page_number=60),
    )
    table = {**_table_with_cell(section_id="", page_number=62, cells=[]), "heading_path": []}
    document = project_candidate_representation(_payload(sections=sections, text_blocks=(), tables=(table,)))

    result = map_candidate_document_anchor_candidates(document, schema_family="S1_full")

    table_mapping = next(item for item in result.mapped if item.block_type == "table")
    assert table_mapping.fields.section_id == "§8"


def test_half_open_section_span_boundary_belongs_to_next_section() -> None:
    """验证页码等于 next_start 时归入下一章节。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 半开区间边界归属错误时抛出。
    """

    sections = (
        _section(section_id="sec_3", heading_text="§3 主要财务指标", page_number=10),
        _section(section_id="sec_8", heading_text="§8 投资组合报告", page_number=60),
    )
    table = {**_table_with_cell(section_id="", page_number=60, cells=[]), "heading_path": []}
    document = project_candidate_representation(_payload(sections=sections, text_blocks=(), tables=(table,)))

    result = map_candidate_document_anchor_candidates(document, schema_family="S1_full")

    table_mapping = next(item for item in result.mapped if item.block_type == "table")
    assert table_mapping.fields.section_id == "§8"


def test_unsupported_section_node_closes_previous_stable_section_span() -> None:
    """验证后续不支持 section node 会截断上一稳定章节 span。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 不支持 section node 未作为 span 上界时抛出。
    """

    sections = (
        _section(section_id="sec_8", heading_text="§8 投资组合报告", page_number=60),
        _section(section_id="appendix", heading_text="附录", page_number=80),
    )
    inside_table = {**_table_with_cell(table_id="tbl_inside", section_id="", page_number=62, cells=[]), "heading_path": []}
    outside_table = {**_table_with_cell(table_id="tbl_outside", section_id="", page_number=81, cells=[]), "heading_path": []}
    document = project_candidate_representation(
        _payload(sections=sections, text_blocks=(), tables=(inside_table, outside_table))
    )

    inside_result = map_candidate_locator_to_anchor_candidate(document, document.tables[0], schema_family="S1_full")
    outside_result = map_candidate_locator_to_anchor_candidate(document, document.tables[1], schema_family="S1_full")

    assert inside_result.blocked == ()
    assert inside_result.mapped[0].fields.section_id == "§8"
    assert outside_result.mapped == ()
    assert outside_result.blocked[0].reason_code == "missing_section_context"


def test_missing_page_without_explicit_section_blocks_as_missing_section_context() -> None:
    """验证无法传播章节且缺页码时返回 missing_section_context。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 缺页码传播未按章节上下文缺失阻断时抛出。
    """

    table = {**_table_with_cell(section_id="", cells=[]), "heading_path": []}
    table.pop("page_number")
    document = project_candidate_representation(_payload(sections=(), text_blocks=(), tables=(table,)))

    result = map_candidate_document_anchor_candidates(document, schema_family="S1_full")

    assert result.mapped == ()
    assert result.blocked[0].reason_code == "missing_section_context"


def test_cross_section_multi_page_table_blocks_before_page_number_selection() -> None:
    """验证跨两个稳定 section span 的多页表格 fail-closed。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 跨章节表格未阻断时抛出。
    """

    sections = (
        _section(section_id="sec_3", heading_text="§3 主要财务指标", page_number=10),
        _section(section_id="sec_8", heading_text="§8 投资组合报告", page_number=60),
    )
    table_payload = {**_table_with_cell(section_id="", cells=[]), "heading_path": []}
    table_payload.pop("page_number")
    document = project_candidate_representation(_payload(sections=sections, text_blocks=(), tables=(table_payload,)))
    table = replace(document.tables[0], page_numbers=(58, 62))
    document = replace(document, tables=(table,))

    result = map_candidate_document_anchor_candidates(document, schema_family="S1_full")

    assert not any(item.block_type == "table" for item in result.mapped)
    assert any(block.reason_code == "section_span_crosses_multiple_sections" for block in result.blocked)


def test_cell_inherits_parent_table_section_without_row_or_column_label_inference() -> None:
    """验证 cell 只继承父表章节，不从行列标签推断章节。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: cell 被行列标签章节覆盖时抛出。
    """

    cell = {
        **_cell(),
        "row_label_path": ["§2 基金基本情况"],
        "column_header_path": ["§9 期末基金份额持有人户数及持有人结构"],
    }
    table = _table_with_cell(cells=[cell])
    document = project_candidate_representation(_payload(tables=(table,)))

    result = map_candidate_document_anchor_candidates(document, schema_family="S1_full")

    cell_mapping = next(item for item in result.mapped if item.block_type == "cell")
    assert cell_mapping.fields.section_id == "§8"


def test_cover_report_title_heading_without_section_context_is_blocked() -> None:
    """验证封面/报告标题不生成章节上下文。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 封面标题被误映射为章节时抛出。
    """

    paragraph = {**_paragraph(section_id="", page_number=1), "heading_path": ["某某基金2025年年度报告"]}
    document = project_candidate_representation(_payload(sections=(), text_blocks=(paragraph,), tables=()))

    result = map_candidate_document_anchor_candidates(document, schema_family="S1_full")

    assert result.mapped == ()
    assert result.blocked[0].reason_code == "missing_section_context"


def test_s1_full_json_schema_mismatch_remains_rejected() -> None:
    """验证 S1 full JSON 仍不被当前 envelope helper 静默接受。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: schema mismatch 未保持阻断时抛出。
    """

    payload = {**_payload(), "schema_version": "s1.full.json"}

    with pytest.raises(ValueError, match="unsupported candidate representation schema_version"):
        project_candidate_representation(payload)
