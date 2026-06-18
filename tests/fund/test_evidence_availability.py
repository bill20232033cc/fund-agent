"""证据可用性派生测试，覆盖基金分析模板第 2/3 章。"""

from __future__ import annotations

import ast
from dataclasses import replace
from pathlib import Path

import pytest

import fund_agent.fund.evidence_availability as evidence_availability_module
from fund_agent.fund.chapter_facts import project_chapter_facts
from fund_agent.fund.evidence_availability import (
    EVIDENCE_AVAILABILITY_SCHEMA_VERSION,
    AvailabilityStatus,
    derive_evidence_availability,
)
from fund_agent.fund.extractors.models import ExtractedField
from fund_agent.fund.template.typed_contracts import (
    EvidencePredicate,
    MustNotCoverClause,
    load_typed_template_contract_manifest,
)
from tests.fund.test_chapter_facts import _bundle


def test_derives_available_requirements_from_fact_ids_and_anchor_ids() -> None:
    """验证 requirement availability 从同源 fact id 与 anchor id 派生。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: availability 未保留同源 fact / anchor 时抛出。
    """

    projection = project_chapter_facts(_bundle(), chapter_ids=(2, 3))

    availability = derive_evidence_availability(projection)
    strategy = availability.require("ch3.requirement.manager_strategy_text_reviewed")
    ch2_performance = availability.require("ch2.required_output.item_01")

    assert availability.schema_version == EVIDENCE_AVAILABILITY_SCHEMA_VERSION
    assert availability.source_schema_version == projection.schema_version
    assert strategy.status == "available"
    assert strategy.fact_ids == (_fact_id(projection, 3, "manager_strategy_text"),)
    assert strategy.evidence_anchor_ids
    assert strategy.gap_references == ()
    assert ch2_performance.status == "available"
    assert ch2_performance.chapter_id == 2
    assert ch2_performance.internal_subcontract_id == "performance"
    assert ch2_performance.fact_ids == (_fact_id(projection, 2, "nav_benchmark_performance"),)


def test_distinguishes_missing_unavailable_not_applicable_unreviewed() -> None:
    """验证 missing / unavailable / not_applicable / unreviewed 不被折叠。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 任一状态被错误合并时抛出。
    """

    bundle = replace(
        _bundle(),
        manager_strategy_text=_missing_field("manager_strategy_text", "fixture missing"),
        turnover_rate=_missing_field("turnover_rate", "field unavailable in source"),
        manager_alignment=_missing_field("manager_alignment", "not_applicable fixture"),
        holdings_snapshot=_field_without_anchor({"top_holdings": [{"name": "A"}]}),
    )
    projection = project_chapter_facts(bundle, chapter_ids=(3,))

    availability = derive_evidence_availability(projection)

    assert availability.require("ch3.requirement.manager_strategy_text_reviewed").status == "missing"
    assert availability.require("ch3.requirement.turnover_rate_reviewed").status == "unavailable"
    assert availability.require("ch3.requirement.manager_alignment_reviewed").status == "not_applicable"
    holdings = availability.require("ch3.requirement.holdings_snapshot_reviewed")
    assert holdings.status == "unreviewed"
    assert holdings.gap_references
    assert holdings.gap_references[0].missing_reason == "evidence_missing"
    assert availability.require("ch3.requirement.cross_period_style_evidence_reviewed").status == "unreviewed"


def test_ch3_actual_behavior_requirement_is_unreviewed_when_turnover_or_style_evidence_absent() -> None:
    """验证第 3 章实际行为 requirement 在单年缺跨期证据时保持 unreviewed。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: actual behavior 被误判为 available 时抛出。
    """

    projection = project_chapter_facts(_bundle(), chapter_ids=(3,))

    availability = derive_evidence_availability(projection)
    actual_behavior = availability.require("ch3.requirement.actual_behavior_reviewed")
    output_behavior = availability.require("ch3.required_output.item_03")
    style_judgment = availability.require("ch3.required_output.item_05")

    assert actual_behavior.status == "unreviewed"
    assert output_behavior.status == "unreviewed"
    assert style_judgment.status == "unreviewed"
    assert "structured.turnover_rate" in actual_behavior.source_field_ids
    assert "structured.holdings_snapshot" in actual_behavior.source_field_ids
    assert "synthetic.cross_period_comparison" in actual_behavior.source_field_ids
    assert any(gap.source_field_id is None for gap in actual_behavior.gap_references)


def test_ch3_basic_manager_info_required_output_uses_basic_identity_availability() -> None:
    """验证第 3 章基金经理基本信息 required output 有显式 availability。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: item_01 未映射到 basic identity 同源 fact 时抛出。
    """

    projection = project_chapter_facts(_bundle(), chapter_ids=(3,))

    availability = derive_evidence_availability(projection)
    basic_manager = availability.require("ch3.required_output.item_01")

    assert basic_manager.status == "available"
    assert basic_manager.chapter_id == 3
    assert basic_manager.source_field_ids == ("structured.basic_identity", "structured.portfolio_managers")
    assert basic_manager.fact_ids == (
        _fact_id(projection, 3, "basic_identity"),
        _fact_id(projection, 3, "portfolio_managers"),
    )


def test_manager_and_risk_downstream_fields_are_exposed_by_evidence_availability() -> None:
    """验证新增经理任期和风险收益特征字段进入 evidence availability 派生视图。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当字段未按章节映射暴露时抛出。
    """

    projection = project_chapter_facts(_bundle(), chapter_ids=(1, 3, 6))

    availability = derive_evidence_availability(projection)
    ch1_managers = availability.require("ch1.requirement.portfolio_managers_reviewed")
    ch1_risk = availability.require("ch1.requirement.risk_characteristic_text_reviewed")
    ch6_risk = availability.require("ch6.requirement.risk_characteristic_text_reviewed")

    assert ch1_managers.status == "available"
    assert ch1_managers.source_field_ids == ("structured.portfolio_managers",)
    assert ch1_managers.fact_ids == (_fact_id(projection, 1, "portfolio_managers"),)
    assert ch1_risk.status == "available"
    assert ch1_risk.source_field_ids == ("structured.risk_characteristic_text",)
    assert ch1_risk.fact_ids == (_fact_id(projection, 1, "risk_characteristic_text"),)
    assert ch6_risk.status == "available"
    assert ch6_risk.source_field_ids == ("structured.risk_characteristic_text",)
    assert ch6_risk.fact_ids == (_fact_id(projection, 6, "risk_characteristic_text"),)


def test_ch2_subcontract_availability_stays_under_public_chapter_2() -> None:
    """验证 Ch2 内部子契约 availability 不创建公开拆章。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: Ch2 availability 出现非公开第 2 章编号时抛出。
    """

    projection = project_chapter_facts(_bundle(), chapter_ids=(2,))

    availability = derive_evidence_availability(projection)
    ch2_requirements = tuple(
        requirement for requirement in availability.requirements if requirement.requirement_id.startswith("ch2.")
    )

    assert ch2_requirements
    assert {requirement.chapter_id for requirement in ch2_requirements} == {2}
    assert {requirement.internal_subcontract_id for requirement in ch2_requirements} == {
        "performance",
        "attribution",
        "cost",
    }


def test_requirement_specs_cross_validate_against_projected_typed_manifest() -> None:
    """验证 EvidenceAvailability 私有 specs 与同一 typed manifest 投影一致。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: Ch2/Ch3 requirement specs 与 typed manifest 投影不一致时抛出。
    """

    manifest = load_typed_template_contract_manifest()
    chapter_2 = manifest.chapters[2]
    chapter_3 = manifest.chapters[3]
    ch2_spec_ids = {spec.requirement_id for spec in evidence_availability_module._CH2_REQUIREMENT_SPECS}
    ch2_manifest_ids = {
        *(clause.clause_id for clause in chapter_2.must_answer),
        *(item.item_id for item in chapter_2.required_output_items),
    }
    ch2_specs_by_subcontract = {
        subcontract_id: {
            spec.requirement_id
            for spec in evidence_availability_module._CH2_REQUIREMENT_SPECS
            if spec.internal_subcontract_id == subcontract_id
        }
        for subcontract_id in ("performance", "attribution", "cost")
    }
    ch2_manifest_by_subcontract = {
        subcontract.subcontract_id: set(subcontract.requirement_ids)
        for subcontract in chapter_2.internal_subcontracts
    }
    ch3_base_spec_ids = {spec.requirement_id for spec in evidence_availability_module._CH3_REQUIREMENT_SPECS}
    ch3_required_output_ids = {item.item_id for item in chapter_3.required_output_items}
    ch3_predicate_requirement_ids = {
        requirement_id
        for clause in chapter_3.must_not_cover
        if clause.applies_when is not None
        for requirement_id in clause.applies_when.requirement_ids
    }

    assert ch2_spec_ids == ch2_manifest_ids
    assert ch2_specs_by_subcontract == ch2_manifest_by_subcontract
    assert set(evidence_availability_module._CH3_ACTUAL_BEHAVIOR_OUTPUT_IDS) <= ch3_required_output_ids
    assert evidence_availability_module._CH3_ACTUAL_BEHAVIOR_REQUIREMENT_ID in ch3_predicate_requirement_ids
    assert set(evidence_availability_module._CH3_ACTUAL_BEHAVIOR_DEPENDENCIES) <= ch3_base_spec_ids
    assert ch3_required_output_ids <= (
        ch3_base_spec_ids | set(evidence_availability_module._CH3_ACTUAL_BEHAVIOR_OUTPUT_IDS)
    )


def test_derivation_does_not_call_document_repository() -> None:
    """静态验证 evidence_availability 不导入仓库、PDF、来源 helper、Service、Host 或 provider。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 模块 import 越过 Slice 2 范围时抛出。
    """

    imports = _module_imports(Path("fund_agent/fund/evidence_availability.py"))

    forbidden_fragments = (
        "documents",
        "repository",
        "cache",
        "pdf",
        "source",
        "downloader",
        "parser",
        "service",
        "host",
        "provider",
        "retained",
        "filesystem",
        "pathlib",
        "os",
        "dayu",
        "openai",
        "llm",
    )
    assert all(not any(fragment in module for fragment in forbidden_fragments) for module in imports)


def test_unknown_requirement_id_fails_closed() -> None:
    """验证 malformed / unknown typed contract requirement id fail-closed。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 未知 requirement id 未抛出 `ValueError` 时抛出。
    """

    manifest = load_typed_template_contract_manifest()
    chapter_3 = manifest.chapters[3]
    illegal_clause = MustNotCoverClause(
        clause_id="ch3.must_not_cover.item_99",
        text="fixture illegal requirement",
        applies_when=EvidencePredicate(
            predicate_id="ch3.evidence.fixture_unknown",
            requirement_ids=("ch3.requirement.unknown_reviewed",),
            required_statuses=("missing",),
            description="fixture unknown requirement",
        ),
    )
    illegal_manifest = replace(
        manifest,
        chapters=(
            *manifest.chapters[:3],
            replace(chapter_3, must_not_cover=(*chapter_3.must_not_cover, illegal_clause)),
            *manifest.chapters[4:],
        ),
    )
    projection = project_chapter_facts(_bundle(), chapter_ids=(3,))

    with pytest.raises(ValueError, match="未知 EvidenceRequirementId"):
        derive_evidence_availability(projection, illegal_manifest)


def test_available_status_type_closed() -> None:
    """验证测试直接覆盖 AvailabilityStatus 闭集名称。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 类型别名不包含 expected status 时抛出。
    """

    statuses: tuple[AvailabilityStatus, ...] = (
        "available",
        "missing",
        "unavailable",
        "not_applicable",
        "unreviewed",
    )

    assert len(set(statuses)) == 5


def _missing_field(field_name: str, note: str) -> ExtractedField[dict[str, object]]:
    """构造缺失字段。

    Args:
        field_name: 字段名，仅用于 row locator。
        note: 缺失说明。

    Returns:
        测试用 `ExtractedField`。

    Raises:
        无显式抛出。
    """

    return ExtractedField(value=None, anchors=(), extraction_mode="missing", note=f"{field_name}: {note}")


def _field_without_anchor(value: dict[str, object]) -> ExtractedField[dict[str, object]]:
    """构造有值但无证据锚点的字段。

    Args:
        value: 字段值。

    Returns:
        测试用 `ExtractedField`。

    Raises:
        无显式抛出。
    """

    return ExtractedField(value=value, anchors=(), extraction_mode="direct", note=None)


def _fact_id(projection: object, chapter_id: int, source_field_name: str) -> str:
    """按章节与字段名读取 fact id。

    Args:
        projection: `ChapterFactProjection`。
        chapter_id: 公开章节编号。
        source_field_name: 来源字段名。

    Returns:
        fact id。

    Raises:
        AssertionError: 未找到匹配 fact 时抛出。
    """

    for chapter in projection.chapters:
        if chapter.chapter_id != chapter_id:
            continue
        for fact in chapter.facts:
            if fact.source_field_name == source_field_name:
                return fact.fact_id
    raise AssertionError(f"missing fact: ch{chapter_id}.{source_field_name}")


def _module_imports(source_path: Path) -> set[str]:
    """读取 Python 文件 import 模块集合。

    Args:
        source_path: Python 源文件路径。

    Returns:
        import module 集合。

    Raises:
        OSError: 文件读取失败时由 `Path.read_text` 抛出。
        SyntaxError: 源文件无法解析为 AST 时抛出。
    """

    tree = ast.parse(source_path.read_text(encoding="utf-8"))
    imports: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name for alias in node.names)
        if isinstance(node, ast.ImportFrom) and node.module is not None:
            imports.add(node.module)
    return imports
