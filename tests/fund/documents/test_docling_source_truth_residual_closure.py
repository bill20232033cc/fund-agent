"""Docling source-truth residual closure helper 的 no-live 单元测试。"""

from __future__ import annotations

import builtins

import pytest

from fund_agent.fund.documents.candidates import source_truth_residual_closure as closure
from fund_agent.fund.documents.candidates.source_truth_residual_closure import (
    RepositoryReferenceBundle,
    RepositoryReferenceCell,
    RepositoryReferenceTextSpan,
    close_source_truth_residuals,
)


def _anchor(
    *,
    section_id: str,
    table_id: str | None = "docling_table_1",
    row_locator: str | None = "cell:r0:c1:idx1",
    source_kind: str = "annual_report",
    candidate_source_kind: str = "docling_pdf_candidate",
    source_truth_status: str = "not_proven",
) -> dict[str, object]:
    """构造 candidate-only anchor fixture。

    Args:
        section_id: 候选章节。
        table_id: 候选表格 ID。
        row_locator: 候选行定位。
        source_kind: 模拟 EvidenceAnchor.source_kind 的年报语义来源。
        candidate_source_kind: candidate processor route 身份。
        source_truth_status: candidate source truth 状态。

    Returns:
        JSON-like anchor 字典。

    Raises:
        无显式抛出。
    """

    return {
        "section_id": section_id,
        "page_number": 5,
        "table_id": table_id,
        "row_locator": row_locator,
        "candidate_only": True,
        "source_kind": source_kind,
        "candidate_source_kind": candidate_source_kind,
        "source_truth_status": source_truth_status,
        "field_correctness_status": "not_proven",
    }


def _row(
    *,
    fact_id: str,
    field_name: str,
    value: str,
    section_id: str,
    sample_id: str = "S1",
    fund_code: str = "004393",
    row_disposition: str = "ambiguous_source_body_match",
    table_id: str | None = "docling_table_1",
    row_locator: str | None = "cell:r0:c1:idx1",
    anchor_extra: dict[str, object] | None = None,
) -> dict[str, object]:
    """构造 source_truth_matrix residual row fixture。

    Args:
        fact_id: fact id。
        field_name: 字段名。
        value: 归一化候选值。
        section_id: 候选章节。
        sample_id: 样本 ID。
        fund_code: 基金代码。
        row_disposition: 上游 residual disposition。
        table_id: 候选表格 ID。
        row_locator: 候选行定位。
        anchor_extra: anchor 额外覆盖字段。

    Returns:
        JSON-like residual row。

    Raises:
        无显式抛出。
    """

    anchor = _anchor(section_id=section_id, table_id=table_id, row_locator=row_locator)
    if anchor_extra:
        anchor.update(anchor_extra)
    return {
        "sample_id": sample_id,
        "fact_id": fact_id,
        "fund_code": fund_code,
        "document_year": 2025,
        "field_name": field_name,
        "candidate_anchor": anchor,
        "normalized_candidate": value,
        "row_disposition": row_disposition,
        "residual_reason": "test residual",
    }


def _cell(
    *,
    value: str,
    row_label_path: tuple[str, ...],
    section_id: str = "§2",
    column_header_path: tuple[str, ...] = ("项目", "值"),
    table_context: tuple[str, ...] = ("基金概况",),
    table_id: str = "source_table_1",
    repository_source_name: str = "eid",
    table_title_path: tuple[str, ...] = (),
    heading_path: tuple[str, ...] = (),
    column_header_band_path: tuple[str, ...] = (),
    table_family: closure.TableFamily = "unknown",
    row_parent_label_path: tuple[str, ...] = (),
    row_hierarchy_path: tuple[str, ...] = (),
    row_hierarchy_role: closure.RowHierarchyRole = "unknown",
    bounded_neighbor_row_labels: tuple[str, ...] = (),
    share_class_context: closure.ShareClassContext = "unknown",
    share_class_context_source: closure.ShareClassContextSource = "unknown",
    period_context: closure.PeriodContext = "unknown",
    period_context_source: closure.PeriodContextSource = "unknown",
) -> RepositoryReferenceCell:
    """构造 repository-mediated reference cell fixture。

    Args:
        value: 单元格值。
        row_label_path: 行标签路径。
        section_id: 年报章节。
        column_header_path: 列表头路径。
        table_context: 表格上下文。
        table_id: 表格 ID。
        repository_source_name: 仓库来源名。
        table_title_path: 表格标题路径。
        heading_path: 标题路径。
        column_header_band_path: 多层表头路径。
        table_family: 表族分类。
        row_parent_label_path: 父行标签。
        row_hierarchy_path: 行层级路径。
        row_hierarchy_role: 行层级角色。
        bounded_neighbor_row_labels: 邻近行诊断标签。
        share_class_context: 规范份额类别。
        share_class_context_source: 份额类别证明来源。
        period_context: 规范期间。
        period_context_source: 期间证明来源。

    Returns:
        仓库引用单元格。

    Raises:
        无显式抛出。
    """

    return RepositoryReferenceCell(
        fund_code="004393",
        document_year=2025,
        repository_source_name=repository_source_name,
        source_mode="single_source_only",
        fallback_used=False,
        section_id=section_id,
        page_number=5,
        table_id=table_id,
        row_index=0,
        column_index=1,
        row_label_path=row_label_path,
        column_header_path=column_header_path,
        raw_text=value,
        normalized_text=value,
        table_context=table_context,
        table_title_path=table_title_path,
        heading_path=heading_path,
        column_header_band_path=column_header_band_path,
        table_family=table_family,
        row_parent_label_path=row_parent_label_path,
        row_hierarchy_path=row_hierarchy_path,
        row_hierarchy_role=row_hierarchy_role,
        bounded_neighbor_row_labels=bounded_neighbor_row_labels,
        share_class_context=share_class_context,
        share_class_context_source=share_class_context_source,
        period_context=period_context,
        period_context_source=period_context_source,
    )


def _span(
    *,
    value: str,
    context_label: str,
    semantic_context_label: closure.TextSemanticContext = "unknown",
    section_id: str = "§2",
    heading_path: tuple[str, ...] = (),
) -> RepositoryReferenceTextSpan:
    """构造 repository-mediated text span fixture。

    Args:
        value: 文本值。
        context_label: 原始上下文标签。
        semantic_context_label: 规范语义上下文。
        section_id: 年报章节。
        heading_path: 标题路径。

    Returns:
        仓库引用文本。

    Raises:
        无显式抛出。
    """

    return RepositoryReferenceTextSpan(
        fund_code="004393",
        document_year=2025,
        repository_source_name="eid",
        source_mode="single_source_only",
        fallback_used=False,
        section_id=section_id,
        page_number=5,
        raw_text=value,
        normalized_text=value,
        context_label=context_label,
        semantic_context_label=semantic_context_label,
        heading_path=heading_path,
    )


def _bundle(
    *cells: RepositoryReferenceCell,
    metadata_ok: bool = True,
    text_spans: tuple[RepositoryReferenceTextSpan, ...] = (),
) -> RepositoryReferenceBundle:
    """构造 repository reference bundle fixture。

    Args:
        *cells: 仓库引用单元格。
        metadata_ok: metadata guard 是否通过。
        text_spans: 仓库引用文本。

    Returns:
        仓库引用 bundle。

    Raises:
        无显式抛出。
    """

    return RepositoryReferenceBundle(
        sample_id="S1",
        fund_code="004393",
        document_year=2025,
        metadata_ok=metadata_ok,
        metadata_reason=None if metadata_ok else "unsafe metadata",
        cells=cells,
        text_spans=text_spans,
    )


def _matrix(*rows: dict[str, object]) -> dict[str, object]:
    """构造 source_truth_matrix fixture。

    Args:
        *rows: residual rows。

    Returns:
        JSON-like matrix。

    Raises:
        无显式抛出。
    """

    return {"rows": list(rows), "input_artifacts": [{"path": "accepted/source_truth_matrix.json"}]}


def _close_one(row: dict[str, object], bundle: RepositoryReferenceBundle) -> dict[str, object]:
    """执行 helper 并返回第一行结果字典。

    Args:
        row: residual row fixture。
        bundle: 仓库引用 bundle fixture。

    Returns:
        第一行输出字典。

    Raises:
        AssertionError: 输出行数不是 1 时抛出。
    """

    result = close_source_truth_residuals(
        source_truth_matrix=_matrix(row),
        repository_reference_rows={"S1": bundle},
    ).to_dict()
    assert result["summary"]["rows_total"] == 1
    return result["rows"][0]


def test_reference_bundle_serialization_emits_new_default_fields() -> None:
    """验证 reference bundle v2 新字段按默认值序列化。"""

    bundle = _bundle(
        _cell(value="004393", row_label_path=("基金主代码",)),
        text_spans=(_span(value="基准", context_label="业绩比较基准"),),
    ).to_dict()

    cell = bundle["cells"][0]
    span = bundle["text_spans"][0]
    assert bundle["reference_bundle_schema_version"] == "repository_reference_bundle.v2"
    assert bundle["enrichment_status"] == "not_enriched"
    assert bundle["enrichment_notes"] == []
    assert cell["table_title_path"] == []
    assert cell["heading_path"] == []
    assert cell["column_header_band_path"] == []
    assert cell["table_family"] == "unknown"
    assert cell["row_parent_label_path"] == []
    assert cell["row_hierarchy_path"] == []
    assert cell["row_hierarchy_role"] == "unknown"
    assert cell["bounded_neighbor_row_labels"] == []
    assert cell["share_class_context"] == "unknown"
    assert cell["share_class_context_source"] == "unknown"
    assert cell["period_context"] == "unknown"
    assert cell["period_context_source"] == "unknown"
    assert span["heading_path"] == []
    assert span["semantic_context_label"] == "unknown"


def test_legacy_reference_bundle_payload_deserializes_with_unknown_defaults() -> None:
    """验证 legacy payload 缺失 enriched 字段时落到 v1/unknown/default。"""

    bundle = closure._coerce_bundle(
        {
            "sample_id": "S1",
            "fund_code": "004393",
            "document_year": 2025,
            "metadata_ok": True,
            "metadata_reason": None,
            "cells": [
                {
                    "fund_code": "004393",
                    "document_year": 2025,
                    "repository_source_name": "eid",
                    "source_mode": "single_source_only",
                    "section_id": "§8",
                    "page_number": 5,
                    "table_id": "t1",
                    "row_index": 0,
                    "column_index": 1,
                    "row_label_path": ["权益投资"],
                    "column_header_path": ["金额"],
                    "raw_text": "1",
                    "normalized_text": "1",
                    "table_context": ["基金资产组合"],
                }
            ],
            "text_spans": [
                {
                    "fund_code": "004393",
                    "document_year": 2025,
                    "repository_source_name": "eid",
                    "source_mode": "single_source_only",
                    "section_id": "§2",
                    "page_number": 5,
                    "raw_text": "基准",
                    "normalized_text": "基准",
                    "context_label": "页内文本",
                }
            ],
            "reference_generation_status": "available",
        }
    )

    assert bundle.reference_bundle_schema_version == "repository_reference_bundle.v1"
    assert bundle.enrichment_status == "not_enriched"
    assert bundle.cells[0].table_family == "unknown"
    assert bundle.cells[0].row_hierarchy_path == ()
    assert bundle.cells[0].row_hierarchy_role == "unknown"
    assert bundle.cells[0].share_class_context == "unknown"
    assert bundle.cells[0].period_context == "unknown"
    assert bundle.text_spans[0].semantic_context_label == "unknown"


@pytest.mark.parametrize(
    ("status_value", "expected"),
    [
        (None, "disambiguated_source_body_match"),
        ("typo", "disambiguated_source_body_match"),
        ("blocked_reference_unavailable", "blocked_reference_unavailable"),
    ],
)
def test_reference_generation_status_coerces_invalid_to_available_but_preserves_blocked(
    status_value: object,
    expected: str,
) -> None:
    """验证 reference_generation_status 只接受 literal，非法/缺失默认 available。"""

    row = _row(fact_id="F002", field_name="fund_code", value="004393", section_id="§2")
    payload = _bundle(_cell(value="004393", row_label_path=("基金主代码",))).to_dict()
    if status_value is None:
        payload.pop("reference_generation_status")
    else:
        payload["reference_generation_status"] = status_value

    coerced = closure._coerce_bundle(payload)
    result = close_source_truth_residuals(
        source_truth_matrix=_matrix(row),
        repository_reference_rows={"S1": payload},
    ).to_dict()["rows"][0]
    expected_status = (
        "blocked_reference_unavailable"
        if status_value == "blocked_reference_unavailable"
        else "available"
    )

    assert coerced.reference_generation_status == expected_status
    assert result["closure_disposition"] == expected


def test_coerce_cell_sets_standalone_hierarchy_only_when_role_proven() -> None:
    """验证 standalone 角色才把 row_label_path 作为 hierarchy 默认值。"""

    standalone = closure._coerce_cell(
        {
            "fund_code": "004393",
            "document_year": 2025,
            "repository_source_name": "eid",
            "source_mode": "single_source_only",
            "section_id": "§8",
            "page_number": 5,
            "table_id": "t1",
            "row_index": 0,
            "column_index": 1,
            "row_label_path": ["权益投资"],
            "column_header_path": ["金额"],
            "raw_text": "1",
            "normalized_text": "1",
            "table_context": ["基金资产组合"],
            "row_hierarchy_role": "standalone",
        }
    )
    unproven = closure._coerce_cell(
        {
            "fund_code": "004393",
            "document_year": 2025,
            "repository_source_name": "eid",
            "source_mode": "single_source_only",
            "section_id": "§8",
            "page_number": 5,
            "table_id": "t1",
            "row_index": 0,
            "column_index": 1,
            "row_label_path": ["权益投资"],
            "column_header_path": ["金额"],
            "raw_text": "1",
            "normalized_text": "1",
            "table_context": ["基金资产组合"],
        }
    )

    assert standalone.row_hierarchy_path == ("权益投资",)
    assert standalone.row_hierarchy_role == "standalone"
    assert unproven.row_hierarchy_path == ()
    assert unproven.row_hierarchy_role == "unknown"


def test_invalid_literals_become_unknown_and_fail_target_predicates() -> None:
    """验证非法 literal 被降级为 unknown，不能被 raw context 反向闭合。"""

    row = _row(
        fact_id="F015",
        field_name="sales_service_fee_C_current_year",
        value="75815.59",
        section_id="§7",
    )
    payload = _bundle(
        _cell(
            value="75815.59",
            row_label_path=("销售服务费",),
            section_id="§7",
            column_header_path=("C类", "本期"),
            table_context=("销售服务费",),
        )
    ).to_dict()
    payload["cells"][0]["table_family"] = "expense_fee_typo"
    payload["cells"][0]["share_class_context"] = "Z"
    payload["cells"][0]["period_context"] = "this_period"
    result = close_source_truth_residuals(
        source_truth_matrix=_matrix(row),
        repository_reference_rows={"S1": payload},
    ).to_dict()["rows"][0]
    coerced = closure._coerce_bundle(payload)

    assert coerced.cells[0].table_family == "unknown"
    assert coerced.cells[0].share_class_context == "unknown"
    assert coerced.cells[0].period_context == "unknown"
    assert result["closure_disposition"] == "semantic_assignment_residual"


def test_raw_legacy_bundle_entrypoint_enriches_before_closure_and_still_rejects_prior() -> None:
    """验证 raw legacy bundle 经入口 enrichment 后按派生谓词闭合或保留 residual。"""

    row = _row(
        fact_id="F015",
        field_name="sales_service_fee_C_current_year",
        value="75815.59",
        section_id="§7",
    )
    current_payload = {
        "sample_id": "S1",
        "fund_code": "004393",
        "document_year": 2025,
        "metadata_ok": True,
        "metadata_reason": None,
        "cells": [
            {
                "fund_code": "004393",
                "document_year": 2025,
                "repository_source_name": "eid",
                "source_mode": "single_source_only",
                "fallback_used": False,
                "section_id": "§7",
                "page_number": 5,
                "table_id": "fee_table",
                "row_index": 0,
                "column_index": 1,
                "row_label_path": ["销售服务费"],
                "column_header_path": ["C类", "本期"],
                "raw_text": "75815.59",
                "normalized_text": "75815.59",
                "table_context": ["销售服务费"],
            }
        ],
        "text_spans": [],
    }
    prior_payload = {
        **current_payload,
        "cells": [
            {
                **current_payload["cells"][0],
                "column_header_path": ["C类", "上年度"],
            }
        ],
    }

    current = close_source_truth_residuals(
        source_truth_matrix=_matrix(row),
        repository_reference_rows={"S1": current_payload},
    ).to_dict()["rows"][0]
    prior = close_source_truth_residuals(
        source_truth_matrix=_matrix(row),
        repository_reference_rows={"S1": prior_payload},
    ).to_dict()["rows"][0]

    assert closure._coerce_bundle(current_payload).reference_bundle_schema_version == (
        "repository_reference_bundle.v1"
    )
    assert current["closure_disposition"] == "disambiguated_source_body_match"
    assert prior["closure_disposition"] == "semantic_assignment_residual"


@pytest.mark.parametrize(
    ("cell", "expected"),
    [
        (
            _cell(
                value="1",
                row_label_path=("销售服务费",),
                section_id="§7",
                table_context=("销售服务费",),
            ),
            "expense_fee_table",
        ),
        (
            _cell(
                value="1",
                row_label_path=("本基金基金经理持有本开放式基金",),
                section_id="§10",
                table_context=("基金经理持有",),
            ),
            "manager_holding_table",
        ),
        (
            _cell(
                value="1",
                row_label_path=("固定收益投资",),
                section_id="§8",
                table_context=("报告期末基金资产组合",),
            ),
            "portfolio_asset_composition_table",
        ),
        (
            _cell(
                value="1",
                row_label_path=("第二层次",),
                section_id="§8",
                table_context=("公允价值层次", "基金资产组合"),
            ),
            "fair_value_hierarchy_table",
        ),
        (
            _cell(
                value="1",
                row_label_path=("资产",),
                section_id="§8",
                table_context=("资产负债表",),
            ),
            "financial_statement_table",
        ),
        (
            _cell(
                value="1",
                row_label_path=("股票",),
                section_id="§8",
                table_context=("股票投资明细",),
            ),
            "holding_detail_table",
        ),
        (
            _cell(
                value="1",
                row_label_path=("未知",),
                section_id="§8",
                table_context=(),
            ),
            "unknown",
        ),
    ],
)
def test_table_family_classifier_labels_target_families(
    cell: RepositoryReferenceCell,
    expected: closure.TableFamily,
) -> None:
    """验证 deterministic table-family classifier 覆盖目标表族。"""

    assert closure._classify_table_family((cell,)) == expected


def test_table_family_classifier_resolves_conflicts_fail_closed_or_by_precedence() -> None:
    """验证同优先级冲突按 accepted precedence 或 unknown 处理。"""

    fair_value = _cell(
        value="1",
        row_label_path=("固定收益投资",),
        section_id="§8",
        table_context=("基金资产组合", "公允价值层次"),
    )
    explicit_portfolio = _cell(
        value="1",
        row_label_path=("资产",),
        section_id="§8",
        table_context=("报告期末基金资产组合", "资产负债表"),
    )
    ambiguous = _cell(
        value="1",
        row_label_path=("基准",),
        section_id="§2",
        table_context=("基金概况", "业绩比较基准"),
    )

    assert closure._classify_table_family((fair_value,)) == "fair_value_hierarchy_table"
    assert closure._classify_table_family((explicit_portfolio,)) == (
        "portfolio_asset_composition_table"
    )
    assert closure._classify_table_family((ambiguous,)) == "unknown"


def test_header_band_participates_in_share_and_period_derivation() -> None:
    """验证 column_header_band_path 参与 canonical share/period 派生并冲突 fail closed。"""

    cell = _cell(
        value="75815.59",
        row_label_path=("销售服务费",),
        section_id="§7",
        column_header_path=("本期",),
        column_header_band_path=("C类",),
        table_context=("销售服务费",),
    )
    conflict = _cell(
        value="75815.59",
        row_label_path=("销售服务费",),
        section_id="§7",
        column_header_path=("A类", "本期"),
        column_header_band_path=("C类", "上期"),
        table_context=("销售服务费",),
    )

    assert closure._derive_share_class_context(cell) == ("C", "header_band")
    assert closure._derive_period_context(cell) == ("current_period", "column_header")
    assert closure._derive_share_class_context(conflict) == ("unknown", "unknown")
    assert closure._derive_period_context(conflict) == ("unknown", "unknown")


def test_identity_code_disambiguates_main_code_from_trading_code() -> None:
    """验证 fund_code 只闭合到基金主代码，不闭合到交易代码。"""

    row = _row(fact_id="F002", field_name="fund_code", value="004393", section_id="§2")
    result = _close_one(
        row,
        _bundle(
            _cell(value="004393", row_label_path=("交易代码",)),
            _cell(value="004393", row_label_path=("基金主代码",)),
            _cell(value="004393", row_label_path=("下属分级基金的交易代码",)),
        ),
    )

    assert result["closure_disposition"] == "disambiguated_source_body_match"
    assert result["matched_row_label_path"] == ["基金主代码"]
    assert result["fund_layer_status"] == "semantic_rule_satisfied"


def test_identity_name_closes_only_on_labeled_profile_row() -> None:
    """验证 fund_name 只闭合到 §2 基金名称行。"""

    row = _row(fact_id="S4-F001", field_name="fund_name", value="安信基金", section_id="§2")
    result = _close_one(
        row,
        _bundle(
            _cell(value="安信基金", row_label_path=("页眉",)),
            _cell(value="安信基金", row_label_path=("基金名称",)),
        ),
    )

    assert result["closure_disposition"] == "disambiguated_source_body_match"
    assert result["matched_row_label_path"] == ["基金名称"]


def test_manager_and_custodian_close_on_labeled_profile_rows() -> None:
    """验证管理人与托管人只用 §2 已标注行闭合。"""

    manager = _row(
        fact_id="S6-F037",
        field_name="manager",
        value="易方达基金管理有限公司",
        section_id="§2",
    )
    custodian = _row(
        fact_id="S6-F038",
        field_name="custodian",
        value="中国建设银行股份有限公司",
        section_id="§2",
    )
    matrix = close_source_truth_residuals(
        source_truth_matrix=_matrix(manager, custodian),
        repository_reference_rows={
            "S1": _bundle(
                _cell(value="易方达基金管理有限公司", row_label_path=("封面",)),
                _cell(value="易方达基金管理有限公司", row_label_path=("基金管理人",)),
                _cell(value="中国建设银行股份有限公司", row_label_path=("页脚",)),
                _cell(value="中国建设银行股份有限公司", row_label_path=("基金托管人名称",)),
            )
        },
    ).to_dict()

    rows = {item["field_name"]: item for item in matrix["rows"]}
    assert rows["manager"]["closure_disposition"] == "disambiguated_source_body_match"
    assert rows["manager"]["matched_row_label_path"] == ["基金管理人"]
    assert rows["custodian"]["closure_disposition"] == "disambiguated_source_body_match"
    assert rows["custodian"]["matched_row_label_path"] == ["基金托管人名称"]


def test_identical_portfolio_values_remain_residual_without_proven_hierarchy() -> None:
    """验证权益与股票同值时不能只靠 flat row label 闭合。"""

    equity = _row(
        fact_id="S6-F049",
        field_name="equity_investment_amount",
        value="149698325.51",
        section_id="§8",
    )
    stock = _row(
        fact_id="S6-F050",
        field_name="stock_investment_amount",
        value="149698325.51",
        section_id="§8",
    )
    matrix = close_source_truth_residuals(
        source_truth_matrix=_matrix(equity, stock),
        repository_reference_rows={
            "S1": _bundle(
                _cell(
                    value="149698325.51",
                    row_label_path=("权益投资",),
                    section_id="§8",
                    table_context=("基金资产组合",),
                ),
                _cell(
                    value="149698325.51",
                    row_label_path=("其中：股票",),
                    section_id="§8",
                    table_context=("基金资产组合",),
                ),
            )
        },
    ).to_dict()

    rows = {item["field_name"]: item for item in matrix["rows"]}
    assert rows["equity_investment_amount"]["closure_disposition"] == (
        "semantic_assignment_residual"
    )
    assert rows["stock_investment_amount"]["closure_disposition"] == (
        "semantic_assignment_residual"
    )


def test_fixed_income_rejects_fair_value_hierarchy_and_accepts_portfolio_row() -> None:
    """验证固定收益投资拒绝公允价值层级行，只接受组合表行。"""

    row = _row(
        fact_id="S4-F015",
        field_name="fixed_income_investment_amount",
        value="12106715596.39",
        section_id="§8",
    )
    result = _close_one(
        row,
        _bundle(
            _cell(
                value="12106715596.39",
                row_label_path=("第二层次",),
                section_id="§8",
                table_context=("公允价值层级",),
                table_family="fair_value_hierarchy_table",
            ),
            _cell(
                value="12106715596.39",
                row_label_path=("固定收益投资",),
                section_id="§8",
                table_context=("基金资产组合",),
                table_family="portfolio_asset_composition_table",
            ),
        ),
    )

    assert result["closure_disposition"] == "disambiguated_source_body_match"
    assert result["matched_row_label_path"] == ["固定收益投资"]


def test_new_table_family_rejection_overrides_legacy_raw_context_match() -> None:
    """验证新表族拒绝字段优先于 legacy required_table_family_any。"""

    row = _row(
        fact_id="S4-F015",
        field_name="fixed_income_investment_amount",
        value="12106715596.39",
        section_id="§8",
    )
    result = _close_one(
        row,
        _bundle(
            _cell(
                value="12106715596.39",
                row_label_path=("固定收益投资",),
                section_id="§8",
                table_context=("基金资产组合",),
                table_family="fair_value_hierarchy_table",
            )
        ),
    )

    assert result["closure_disposition"] == "semantic_assignment_residual"


def test_benchmark_guard_keeps_investment_objective_context_residual() -> None:
    """验证 benchmark 不被投资目标上下文强行闭合。"""

    row = _row(
        fact_id="S6-F041",
        field_name="benchmark",
        value="紧密跟踪业绩比较基准",
        section_id="§2",
        row_disposition="semantic_assignment_residual",
    )
    result = _close_one(
        row,
        _bundle(
            _cell(
                value="紧密跟踪业绩比较基准",
                row_label_path=("投资目标",),
                table_context=("投资目标",),
            )
        ),
    )

    assert result["closure_disposition"] == "semantic_assignment_residual"
    assert result["fund_layer_status"] == "semantic_rule_rejected"


def test_benchmark_closes_only_with_benchmark_semantic_label() -> None:
    """验证 S6-F041 只由 benchmark semantic text context 闭合。"""

    row = _row(
        fact_id="S6-F041",
        field_name="benchmark",
        value="沪深300指数收益率",
        section_id="§2",
        row_disposition="semantic_assignment_residual",
    )
    investment_objective = _close_one(
        row,
        _bundle(
            text_spans=(
                _span(
                    value="沪深300指数收益率",
                    context_label="投资目标",
                    semantic_context_label="investment_objective",
                ),
            )
        ),
    )
    benchmark = _close_one(
        row,
        _bundle(
            text_spans=(
                _span(
                    value="沪深300指数收益率",
                    context_label="业绩比较基准",
                    semantic_context_label="benchmark",
                ),
            )
        ),
    )

    assert investment_objective["closure_disposition"] == "semantic_assignment_residual"
    assert benchmark["closure_disposition"] == "disambiguated_source_body_match"


def test_neighbor_row_labels_do_not_prove_positive_hierarchy() -> None:
    """验证 bounded_neighbor_row_labels 不作为正向层级证明。"""

    row = _row(
        fact_id="S6-F050",
        field_name="stock_investment_amount",
        value="149698325.51",
        section_id="§8",
    )
    result = _close_one(
        row,
        _bundle(
            _cell(
                value="149698325.51",
                row_label_path=("其中：股票",),
                section_id="§8",
                table_family="portfolio_asset_composition_table",
                bounded_neighbor_row_labels=("权益投资",),
            )
        ),
    )

    assert result["closure_disposition"] == "semantic_assignment_residual"


def test_investment_objective_without_same_source_body_stays_mismatch() -> None:
    """验证 S5-F023 没有同源正文 proof 时保持 source_body_mismatch。"""

    row = _row(
        fact_id="S5-F023",
        field_name="investment_objective",
        value="在严格控制风险的前提下追求回报",
        section_id="§2",
        row_disposition="source_body_mismatch",
    )
    result = _close_one(row, _bundle())

    assert result["closure_disposition"] == "source_body_mismatch"
    assert result["source_layer_status"] == "same_source_text_absent"


def test_unresolved_expense_duplicate_remains_semantic_equivalent_residual() -> None:
    """验证销售服务费 C 本期重复行不会被强制唯一闭合。"""

    row = _row(
        fact_id="F015",
        field_name="sales_service_fee_C_current_year",
        value="75815.59",
        section_id="§7",
    )
    result = _close_one(
        row,
        _bundle(
            _cell(
                value="75815.59",
                row_label_path=("销售服务费",),
                section_id="§7",
                column_header_path=("C类", "本期"),
                table_context=("销售服务费",),
                table_id="fee_1",
                table_family="expense_fee_table",
                share_class_context="C",
                share_class_context_source="column_header",
                period_context="current_period",
                period_context_source="column_header",
            ),
            _cell(
                value="75815.59",
                row_label_path=("销售服务费",),
                section_id="§7",
                column_header_path=("C类", "本报告期"),
                table_context=("销售服务费",),
                table_id="fee_2",
                table_family="expense_fee_table",
                share_class_context="C",
                share_class_context_source="column_header",
                period_context="current_period",
                period_context_source="column_header",
            ),
        ),
    )

    assert result["closure_disposition"] == "semantic_equivalent_duplicate_residual"
    assert result["fund_layer_status"] == "semantic_rule_unresolved"


@pytest.mark.parametrize(
    ("share_class", "period", "table_family", "expected"),
    [
        ("C", "current_period", "expense_fee_table", "disambiguated_source_body_match"),
        ("A", "current_period", "expense_fee_table", "semantic_assignment_residual"),
        ("C", "prior_period", "expense_fee_table", "semantic_assignment_residual"),
        ("C", "unknown", "expense_fee_table", "semantic_assignment_residual"),
        ("C", "current_period", "unknown", "semantic_assignment_residual"),
    ],
)
def test_f015_closes_only_with_c_current_expense_fee_context(
    share_class: closure.ShareClassContext,
    period: closure.PeriodContext,
    table_family: closure.TableFamily,
    expected: str,
) -> None:
    """验证 F015 只由 C 类、本期、费用表闭合。"""

    row = _row(
        fact_id="F015",
        field_name="sales_service_fee_C_current_year",
        value="75815.59",
        section_id="§7",
    )
    result = _close_one(
        row,
        _bundle(
            _cell(
                value="75815.59",
                row_label_path=("销售服务费",),
                section_id="§7",
                table_family=table_family,
                share_class_context=share_class,
                share_class_context_source="column_header",
                period_context=period,
                period_context_source="column_header",
            )
        ),
    )

    assert result["closure_disposition"] == expected


def test_manager_holding_range_a_requires_fund_share_class_label() -> None:
    """验证基金经理持有 A 类区间只接受基金份额类别表头。"""

    row = _row(
        fact_id="F030",
        field_name="manager_holding_range_A",
        value="10万份至50万份",
        section_id="§10",
    )
    result = _close_one(
        row,
        _bundle(
            _cell(
                value="10万份至50万份",
                row_label_path=("本基金基金经理持有本开放式基金",),
                section_id="§10",
                column_header_path=("beta",),
                table_context=("基金经理持有",),
                table_id="manager_holding_1",
                table_family="manager_holding_table",
                share_class_context="unknown",
            ),
            _cell(
                value="10万份至50万份",
                row_label_path=("本基金基金经理持有本开放式基金",),
                section_id="§10",
                column_header_path=("混合A",),
                table_context=("基金经理持有",),
                table_id="manager_holding_2",
                table_family="manager_holding_table",
                share_class_context="A",
                share_class_context_source="column_header",
            ),
        ),
    )

    assert result["closure_disposition"] == "disambiguated_source_body_match"
    assert result["matched_column_header_path"] == ["混合A"]


@pytest.mark.parametrize(
    ("share_class", "table_family", "row_label", "expected"),
    [
        (
            "A",
            "manager_holding_table",
            "本基金基金经理持有本开放式基金",
            "disambiguated_source_body_match",
        ),
        (
            "C",
            "manager_holding_table",
            "本基金基金经理持有本开放式基金",
            "semantic_assignment_residual",
        ),
        ("A", "unknown", "本基金基金经理持有本开放式基金", "semantic_assignment_residual"),
        ("A", "manager_holding_table", "员工持有本基金", "semantic_assignment_residual"),
    ],
)
def test_f020_closes_only_with_a_share_manager_holding_table(
    share_class: closure.ShareClassContext,
    table_family: closure.TableFamily,
    row_label: str,
    expected: str,
) -> None:
    """验证 F020 只由 A 类基金经理持有表闭合。"""

    row = _row(
        fact_id="F020",
        field_name="manager_holding_range_A",
        value="10万份至50万份",
        section_id="§10",
    )
    result = _close_one(
        row,
        _bundle(
            _cell(
                value="10万份至50万份",
                row_label_path=(row_label,),
                section_id="§10",
                table_family=table_family,
                share_class_context=share_class,
                share_class_context_source="column_header",
            )
        ),
    )

    assert result["closure_disposition"] == expected


def test_equity_amount_closes_only_aggregate_row_not_stock_child_or_detail() -> None:
    """验证 S5-F032/S6-F049 只接受组合表权益投资 aggregate 行。"""

    row = _row(
        fact_id="S6-F049",
        field_name="equity_investment_amount",
        value="149698325.51",
        section_id="§8",
    )
    aggregate = _close_one(
        row,
        _bundle(
            _cell(
                value="149698325.51",
                row_label_path=("权益投资",),
                section_id="§8",
                table_family="portfolio_asset_composition_table",
                row_hierarchy_path=("权益投资",),
                row_hierarchy_role="aggregate",
            )
        ),
    )
    stock_child = _close_one(
        row,
        _bundle(
            _cell(
                value="149698325.51",
                row_label_path=("其中：股票",),
                section_id="§8",
                table_family="portfolio_asset_composition_table",
                row_parent_label_path=("权益投资",),
                row_hierarchy_path=("权益投资", "其中：股票"),
                row_hierarchy_role="child",
            )
        ),
    )
    detail = _close_one(
        row,
        _bundle(
            _cell(
                value="149698325.51",
                row_label_path=("权益投资",),
                section_id="§8",
                table_family="holding_detail_table",
                row_hierarchy_path=("权益投资",),
                row_hierarchy_role="aggregate",
            )
        ),
    )

    assert aggregate["closure_disposition"] == "disambiguated_source_body_match"
    assert stock_child["closure_disposition"] == "semantic_assignment_residual"
    assert detail["closure_disposition"] == "semantic_assignment_residual"


def test_stock_amount_closes_only_child_stock_row_under_equity_parent() -> None:
    """验证 S6-F050 只接受权益投资父行下的股票 child 行。"""

    row = _row(
        fact_id="S6-F050",
        field_name="stock_investment_amount",
        value="149698325.51",
        section_id="§8",
    )
    child = _close_one(
        row,
        _bundle(
            _cell(
                value="149698325.51",
                row_label_path=("其中：股票",),
                section_id="§8",
                table_family="portfolio_asset_composition_table",
                row_parent_label_path=("权益投资",),
                row_hierarchy_path=("权益投资", "其中：股票"),
                row_hierarchy_role="child",
            )
        ),
    )
    aggregate = _close_one(
        row,
        _bundle(
            _cell(
                value="149698325.51",
                row_label_path=("股票",),
                section_id="§8",
                table_family="portfolio_asset_composition_table",
                row_hierarchy_path=("股票",),
                row_hierarchy_role="aggregate",
            )
        ),
    )

    assert child["closure_disposition"] == "disambiguated_source_body_match"
    assert aggregate["closure_disposition"] == "semantic_assignment_residual"


@pytest.mark.parametrize(
    ("share_class", "header"),
    [
        ("A", "A"),
        ("A", "A类"),
        ("A", "混合A"),
        ("A", "债券A"),
        ("C", "C"),
        ("C", "C类"),
    ],
)
def test_share_class_context_accepts_fund_share_labels(
    share_class: str,
    header: str,
) -> None:
    """验证份额类别 guard 接受基金份额标签。"""

    assert closure._has_share_class_context((header,), share_class) is True


@pytest.mark.parametrize("header", ["beta", "alpha", "clinic"])
def test_share_class_context_rejects_arbitrary_latin_suffix_words(header: str) -> None:
    """验证短份额类别 guard 不接受任意英文尾字母。"""

    assert closure._has_share_class_context((header,), header[-1].upper()) is False


def test_decimal_separator_placement_is_preserved_during_value_match() -> None:
    """验证数值归一化保留小数点位置并仍支持千分位逗号。"""

    assert closure._normalize_for_match("149,698,325.51") == "149698325.51"
    assert closure._normalize_for_match("149698325.51") != closure._normalize_for_match(
        "1496.9832551"
    )


def test_decimal_placement_difference_does_not_close_source_body_match() -> None:
    """验证仅小数点位置不同的数值不会命中同源正文。"""

    row = _row(
        fact_id="S6-F049",
        field_name="equity_investment_amount",
        value="149698325.51",
        section_id="§8",
    )
    result = _close_one(
        row,
        _bundle(
            _cell(
                value="1496.9832551",
                row_label_path=("权益投资",),
                section_id="§8",
                table_context=("基金资产组合",),
            ),
        ),
    )

    assert result["closure_disposition"] == "source_body_mismatch"
    assert result["source_layer_status"] == "same_source_text_absent"


def test_locator_context_conflict_blocks_locator_layer() -> None:
    """验证 candidate 章节与字段规则冲突时 fail-closed。"""

    row = _row(fact_id="F002", field_name="fund_code", value="004393", section_id="§8")
    result = _close_one(row, _bundle(_cell(value="004393", row_label_path=("基金主代码",))))

    assert result["closure_disposition"] == "blocked_locator_unavailable"
    assert result["processed_layer_status"] == "locator_context_conflict"


def test_unknown_field_name_returns_blocked_rule_missing() -> None:
    """验证未知字段名不会进入语义闭合。"""

    row = _row(
        fact_id="F999",
        field_name="unknown_field",
        value="004393",
        section_id="§2",
    )
    matrix = close_source_truth_residuals(
        source_truth_matrix=_matrix(row),
        repository_reference_rows={},
    ).to_dict()

    result = matrix["rows"][0]
    assert result["closure_disposition"] == "blocked_rule_missing"
    assert result["fund_layer_status"] == "semantic_rule_missing"


def test_boundary_fields_keep_repository_processor_and_anchor_kind_separate() -> None:
    """验证 repository source、processor route、EvidenceAnchor.source_kind 不混同。"""

    row = _row(fact_id="F002", field_name="fund_code", value="004393", section_id="§2")
    result = _close_one(
        row,
        _bundle(
            _cell(
                value="004393",
                row_label_path=("基金主代码",),
                repository_source_name="eid",
            )
        ),
    )

    assert result["matched_repository_source_name"] == "eid"
    assert result["candidate_processor_source_kind"] == "docling_pdf_candidate"
    assert result["evidence_anchor_source_kind"] == "annual_report"
    assert result["matched_repository_source_name"] != result["evidence_anchor_source_kind"]


def test_output_guard_flags_are_preserved() -> None:
    """验证输出矩阵保留所有 non-proof guard flags。"""

    row = _row(fact_id="F002", field_name="fund_code", value="004393", section_id="§2")
    matrix = close_source_truth_residuals(
        source_truth_matrix=_matrix(row),
        repository_reference_rows={"S1": _bundle(_cell(value="004393", row_label_path=("基金主代码",)))},
    ).to_dict()

    assert matrix["not_baseline_promotion"] is True
    assert matrix["not_parser_replacement"] is True
    assert matrix["not_release_readiness"] is True
    assert matrix["not_full_field_correctness"] is True
    assert matrix["not_raw_pdf_bbox_truth"] is True
    assert matrix["candidate_only"] is True


def test_candidate_boundary_guard_rejects_truth_claims() -> None:
    """验证 candidate anchor 越过 not_proven guard 时 fail-closed。"""

    row = _row(
        fact_id="F002",
        field_name="fund_code",
        value="004393",
        section_id="§2",
        anchor_extra={"source_truth_status": "proven"},
    )
    result = _close_one(row, _bundle(_cell(value="004393", row_label_path=("基金主代码",))))

    assert result["closure_disposition"] == "blocked_candidate_metadata_violation"
    assert result["processed_layer_status"] == "candidate_metadata_violation"


@pytest.mark.parametrize(
    "anchor_extra",
    [
        {"source_kind": "docling_pdf_candidate"},
        {"evidence_anchor_source_kind": "docling_pdf_candidate"},
    ],
)
def test_evidence_anchor_source_kind_guard_rejects_non_annual_report(
    anchor_extra: dict[str, object],
) -> None:
    """验证 EvidenceAnchor.source_kind 非 annual_report 时 fail-closed。"""

    row = _row(
        fact_id="F002",
        field_name="fund_code",
        value="004393",
        section_id="§2",
        anchor_extra=anchor_extra,
    )
    result = _close_one(row, _bundle(_cell(value="004393", row_label_path=("基金主代码",))))

    assert result["closure_disposition"] == "blocked_candidate_metadata_violation"
    assert result["processed_layer_status"] == "candidate_metadata_violation"


def test_pure_helper_boundary_does_not_read_or_call_repository(monkeypatch: pytest.MonkeyPatch) -> None:
    """验证 pure helper 在 open 被禁用时仍只处理已加载输入。"""

    def _blocked_open(*args: object, **kwargs: object) -> object:
        """在测试中阻断任何文件读取。

        Args:
            *args: 位置参数。
            **kwargs: 关键字参数。

        Returns:
            不返回。

        Raises:
            AssertionError: 任何 open 调用都会抛出。
        """

        raise AssertionError("pure helper must not read files")

    monkeypatch.setattr(builtins, "open", _blocked_open)
    row = _row(fact_id="F002", field_name="fund_code", value="004393", section_id="§2")
    result = _close_one(row, _bundle(_cell(value="004393", row_label_path=("基金主代码",))))

    assert result["closure_disposition"] == "disambiguated_source_body_match"
    assert not hasattr(closure, "FundDocumentRepository")
    assert not hasattr(closure, "load_annual_report")


def test_missing_reference_bundle_blocks_reference_layer() -> None:
    """验证缺失 repository reference bundle 时返回 blocked_reference_unavailable。"""

    row = _row(fact_id="F002", field_name="fund_code", value="004393", section_id="§2")
    matrix = close_source_truth_residuals(
        source_truth_matrix=_matrix(row),
        repository_reference_rows={},
    ).to_dict()

    result = matrix["rows"][0]
    assert result["closure_disposition"] == "blocked_reference_unavailable"
    assert result["source_layer_status"] == "blocked_reference_unavailable"
