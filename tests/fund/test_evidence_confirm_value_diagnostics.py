"""Evidence Confirm V2 value-match 安全诊断测试。"""

from __future__ import annotations

import ast
from dataclasses import dataclass, replace
from decimal import Decimal
from pathlib import Path

from fund_agent.fund.chapter_facts import (
    ChapterEvidenceAnchor,
    ChapterFactEntry,
    ChapterFactProjection,
    project_chapter_facts,
)
from fund_agent.fund.evidence_confirm import (
    EvidenceConfirmReference,
    confirm_projection_evidence_v2,
)
from fund_agent.fund.evidence_confirm_value_diagnostics import (
    VALUE_MATCH_DIAGNOSTIC_SCHEMA_VERSION,
    summarize_value_match_diagnostics,
)
from fund_agent.fund.extractors.models import (
    BOND_RISK_EVIDENCE_CONTRACT_ID,
    BOND_RISK_EVIDENCE_GROUP_IDS,
    BondRiskEvidenceAnchorRef,
    BondRiskEvidenceGroupRecord,
    BondRiskEvidenceValue,
)
from tests.fund.test_chapter_facts import _bundle


@dataclass(frozen=True, slots=True)
class _NestedDataclassValue:
    """测试用 dataclass value。"""

    value_text: str
    rows: tuple[dict[str, object], ...]


def test_value_diagnostic_reuses_v2_matcher_for_text_numeric_and_ignored_keys() -> None:
    """验证诊断命中信息与 V2 value-match 同源。"""

    projection = _projection_with_value(
        {
            "source_anchor": "raw-secret-anchor-token",
            "name": "Alpha Beta",
            "fee_rate": Decimal("1.20"),
            "rows": ({"period": "2024", "return_rate": "3.50%"},),
        }
    )
    fact = _only_fact(projection)
    result = confirm_projection_evidence_v2(
        projection,
        (
            _reference(
                fact.evidence_anchor_ids[0],
                excerpt_text="同源摘录显示 Alpha Beta，费率为 1.2 倍，年度 2024 年收益 3.50%。",
            ),
        ),
    )

    summary = summarize_value_match_diagnostics(
        projection=projection,
        references=(
            _reference(
                fact.evidence_anchor_ids[0],
                excerpt_text="同源摘录显示 Alpha Beta，费率为 1.2 倍，年度 2024 年收益 3.50%。",
            ),
        ),
        result=result,
    )

    record = summary.records[0]
    value_dimension = _dimension_status(result, "value_match")
    rendered = repr(summary.to_safe_dict())

    assert summary.schema_version == VALUE_MATCH_DIAGNOSTIC_SCHEMA_VERSION
    assert summary.token_match_source == "deterministic_v2_same_source_primitives"
    assert value_dimension == "pass"
    assert record.classification == "not_applicable"
    assert record.token_count == 4
    assert record.matched_token_category_counts == {"numeric_percent": 1, "numeric_plain": 2, "short_text": 1}
    assert record.unmatched_token_category_counts == {}
    assert "raw-secret-anchor-token" not in rendered
    assert "Alpha Beta" not in rendered
    assert "同源摘录" not in rendered
    assert "excerpt_text" not in rendered
    assert ".pdf" not in rendered
    assert "/Users/" not in rendered


def test_value_diagnostic_reports_percent_unit_mismatch_from_v2_matcher() -> None:
    """验证百分号单位不一致时诊断与 V2 fail 一致。"""

    projection = _projection_with_value({"fee_rate": "1.20%"})
    fact = _only_fact(projection)
    references = (
        _reference(
            fact.evidence_anchor_ids[0],
            excerpt_text="同源摘录显示费率 1.20。",
            row_locator=None,
        ),
    )
    result = confirm_projection_evidence_v2(projection, references)

    summary = summarize_value_match_diagnostics(
        projection=projection,
        references=references,
        result=result,
    )

    record = summary.records[0]

    assert _dimension_status(result, "value_match") == "fail"
    assert record.failing_dimensions == ("value_match",)
    assert record.unmatched_token_category_counts == {"numeric_percent": 1}
    assert record.unmatched_value_paths == ("value.fee_rate",)
    assert record.classification == "coarse_reference_insufficient"


def test_value_diagnostic_covers_dataclass_dict_order_and_nested_lists() -> None:
    """验证 dataclass、dict 排序和嵌套 list 诊断路径稳定。"""

    value = _NestedDataclassValue(
        value_text="债券久期",
        rows=(
            {"label": "久期", "ratio": "2.30%"},
            {"label": "杠杆", "ratio": "108.00%"},
        ),
    )
    projection = _projection_with_value(value)
    fact = _only_fact(projection)
    references = (_reference(fact.evidence_anchor_ids[0], excerpt_text="同源摘录只披露债券久期和 2.30%。"),)
    result = confirm_projection_evidence_v2(projection, references)

    summary = summarize_value_match_diagnostics(
        projection=projection,
        references=references,
        result=result,
    )

    record = summary.records[0]

    assert _dimension_status(result, "value_match") == "pass"
    assert record.token_count == 5
    assert record.matched_token_category_counts == {"numeric_percent": 1, "short_text": 2}
    assert record.unmatched_token_category_counts == {"numeric_percent": 1, "short_text": 1}
    assert record.unmatched_value_paths == (
        "value.rows[].label",
        "value.rows[].ratio",
    )


def test_value_diagnostic_classifies_anchor_attachment_mismatch() -> None:
    """验证 non-proof reference 被分类为 anchor attachment mismatch。"""

    projection = _projection_with_value({"fee_rate": "1.20%"})
    fact = _only_fact(projection)
    references = (
        _reference(
            fact.evidence_anchor_ids[0],
            excerpt_text="同源摘录显示费率 1.20%。",
            candidate_only=True,
        ),
    )
    result = confirm_projection_evidence_v2(projection, references)

    summary = summarize_value_match_diagnostics(
        projection=projection,
        references=references,
        result=result,
    )

    record = summary.records[0]

    assert record.reference_count == 1
    assert record.proof_reference_count == 0
    assert record.classification == "anchor_attachment_mismatch"


def test_value_diagnostic_classifies_bond_risk_group_anchor_projection_gap() -> None:
    """验证 bond_risk_evidence value anchors 未展开为章节 anchors 时分类明确。"""

    projection = _projection_with_fact(
        replace(
            _only_fact(_projection_with_value("placeholder")),
            source_field_id="structured.bond_risk_evidence",
            field_path="bond_risk_evidence",
            value=_bond_risk_value(),
            evidence_anchor_ids=(),
        ),
        anchors=(),
    )
    result = confirm_projection_evidence_v2(projection, ())

    summary = summarize_value_match_diagnostics(
        projection=projection,
        references=(),
        result=result,
    )

    record = summary.records[0]

    assert _dimension_status(result, "missing_evidence") == "fail"
    assert record.classification == "bond_risk_group_anchor_projection_gap"
    assert record.anchor_count == 0
    assert record.reference_count == 0
    assert "bond-risk:" not in repr(summary.to_safe_dict())


def test_value_diagnostic_module_does_not_import_runtime_boundaries() -> None:
    """验证 no-live 诊断模块不导入仓库、PDF、Service、Host、provider 或 CLI。"""

    module_path = Path("fund_agent/fund/evidence_confirm_value_diagnostics.py")
    tree = ast.parse(module_path.read_text(encoding="utf-8"))
    forbidden = {
        "FundDocumentRepository",
        "fund_agent.fund.documents.repository",
        "fund_agent.services",
        "fund_agent.host",
        "fund_agent.ui",
        "openai",
        "requests",
    }
    imported_names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_names.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module is not None:
            imported_names.add(node.module)
            imported_names.update(alias.name for alias in node.names)

    assert forbidden.isdisjoint(imported_names)


def _projection_with_value(value: object) -> ChapterFactProjection:
    """构造单 fact projection。"""

    base = project_chapter_facts(_bundle(), chapter_ids=(3,))
    chapter = base.chapters[0]
    base_fact = next(item for item in chapter.facts if item.source_field_id == "structured.turnover_rate")
    anchor_ids = set(base_fact.evidence_anchor_ids)
    anchors = tuple(anchor for anchor in chapter.evidence_anchors if anchor.anchor_id in anchor_ids)
    fact = replace(base_fact, value=value, field_path="diagnostic.value", source_field_id="structured.test_value")
    return _projection_with_fact(fact, anchors=anchors)


def _projection_with_fact(
    fact: ChapterFactEntry,
    *,
    anchors: tuple[ChapterEvidenceAnchor, ...],
) -> ChapterFactProjection:
    """用指定 fact 和 anchors 构造 projection。"""

    base = project_chapter_facts(_bundle(), chapter_ids=(3,))
    chapter = replace(
        base.chapters[0],
        facts=(fact,),
        evidence_anchors=anchors,
        source_field_ids=(fact.source_field_id,),
    )
    return replace(base, chapters=(chapter,), global_missing_reasons=())


def _only_fact(projection: ChapterFactProjection) -> ChapterFactEntry:
    """读取 projection 中唯一 fact。"""

    return projection.chapters[0].facts[0]


def _reference(
    anchor_id: str,
    *,
    excerpt_text: str,
    candidate_only: bool = False,
    row_locator: str | None = None,
) -> EvidenceConfirmReference:
    """构造测试 reference。"""

    return EvidenceConfirmReference(
        anchor_id=anchor_id,
        reference_kind="annual_report_excerpt",
        source_kind="annual_report",
        document_year=2024,
        section_id="§2",
        page_number=12,
        table_id="page-12-table-0",
        row_locator=row_locator,
        excerpt_text=excerpt_text,
        source_truth_status="proven",
        candidate_only=candidate_only,
    )


def _dimension_status(result: object, dimension_name: str) -> str:
    """读取单 fact 指定 dimension 状态。"""

    return next(
        dimension.status
        for dimension in result.fact_results[0].dimension_results  # type: ignore[attr-defined]
        if dimension.dimension == dimension_name
    )


def _bond_risk_value() -> BondRiskEvidenceValue:
    """构造带组级 anchors 的 bond_risk_evidence value。"""

    anchors = tuple(
        BondRiskEvidenceAnchorRef(
            anchor_id=f"bond-risk:006597:2024:{group_id}:1",
            section_id="§8",
            page_number=88,
            table_id=None,
            row_locator=f"line:{index}",
            evidence_role="diagnostic",
        )
        for index, group_id in enumerate(BOND_RISK_EVIDENCE_GROUP_IDS, start=1)
    )
    groups = tuple(
        BondRiskEvidenceGroupRecord(
            group_id=group_id,
            status="accepted",
            strength="qualitative_direct",
            summary=f"{group_id} disclosed",
            measurement_kind="risk_disclosure",
            metric_name=None,
            metric_value=None,
            metric_unit=None,
            period_label="2024",
            source_anchor_ids=(f"bond-risk:006597:2024:{group_id}:1",),
            na_reason=None,
            reviewer_note=None,
        )
        for group_id in BOND_RISK_EVIDENCE_GROUP_IDS
    )
    return BondRiskEvidenceValue(
        schema_version=BOND_RISK_EVIDENCE_CONTRACT_ID,
        contract_id=BOND_RISK_EVIDENCE_CONTRACT_ID,
        fund_code="006597",
        report_year=2024,
        groups=groups,
        anchors=anchors,
        satisfied_group_ids=BOND_RISK_EVIDENCE_GROUP_IDS,
        missing_group_ids=(),
        weak_group_ids=(),
        ambiguous_group_ids=(),
        contract_status="satisfied",
    )
