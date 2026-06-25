"""章节事实 typed projection 测试，覆盖基金分析模板第 0-7 章。"""

from __future__ import annotations

import ast
from dataclasses import replace
from decimal import Decimal
from pathlib import Path
from typing import cast

import pytest

from fund_agent.fund.chapter_facts import (
    CHAPTER_FACT_SCHEMA_VERSION,
    ChapterFactProvider,
    project_chapter_facts,
)
from fund_agent.fund.data.nav_data import NavDataResult
from fund_agent.fund.data_extractor import StructuredFundDataBundle
from fund_agent.fund.extractors.models import (
    BOND_RISK_EVIDENCE_CONTRACT_ID,
    BOND_RISK_EVIDENCE_GROUP_IDS,
    BondRiskEvidenceAnchorRef,
    BondRiskEvidenceContractStatus,
    BondRiskEvidenceGroupId,
    BondRiskEvidenceGroupRecord,
    BondRiskEvidenceStatus,
    BondRiskEvidenceValue,
    EvidenceAnchor,
    EvidenceSourceKind,
    ExtractedField,
    IndexProfileValue,
    TrackingErrorValue,
)


def test_projects_eight_chapter_inputs_from_structured_bundle() -> None:
    """验证结构化数据包可投影为模板第 0-7 章输入。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当章节数量、标题或字段映射不符合契约时抛出。
    """

    projection = project_chapter_facts(_bundle())

    assert projection.schema_version == CHAPTER_FACT_SCHEMA_VERSION
    assert projection.fund_code == "110011"
    assert projection.report_year == 2024
    assert tuple(chapter.chapter_id for chapter in projection.chapters) == tuple(range(8))
    assert projection.chapters[0].title == "投资要点概览"
    assert projection.chapters[1].title == "这只基金到底是什么产品"
    assert projection.chapters[2].title == "R=A+B-C 收益归因"
    chapter_1_fields = _field_names(projection.chapters[1])
    chapter_3_fields = _field_names(projection.chapters[3])
    assert {
        "basic_identity",
        "portfolio_managers",
        "product_profile",
        "risk_characteristic_text",
        "benchmark",
        "index_profile",
    }.issubset(chapter_1_fields)
    assert {
        "manager_strategy_text",
        "portfolio_managers",
        "holdings_snapshot",
        "turnover_rate",
        "manager_alignment",
    }.issubset(chapter_3_fields)
    assert "risk_characteristic_text" in _field_names(projection.chapters[6])
    assert _fact(projection.chapters[1], "portfolio_managers").source_field_id == "structured.portfolio_managers"
    assert (
        _fact(projection.chapters[1], "risk_characteristic_text").source_field_id
        == "structured.risk_characteristic_text"
    )
    assert _fact(projection.chapters[3], "holdings_snapshot").source_field_id == "structured.holdings_snapshot"


def test_chapter_fact_provider_delegates_to_project_chapter_facts() -> None:
    """验证 public provider façade 与函数入口一致，见模板第 0-7 章。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 provider 投影结果与函数入口不一致时抛出。
    """

    bundle = _bundle()

    assert ChapterFactProvider().project(bundle) == project_chapter_facts(bundle)


def test_chapter_id_validation_fails_closed() -> None:
    """验证非法章节编号 fail-closed，见模板第 0-7 章。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当非法章节编号未抛出 `ValueError` 时抛出。
    """

    bundle = _bundle()

    for chapter_ids in ((), (1, 1), (-1,), (8,)):
        with pytest.raises(ValueError):
            project_chapter_facts(bundle, chapter_ids=chapter_ids)


def test_chapter_id_validation_accepts_valid_range() -> None:
    """验证合法章节编号 happy path，见模板第 0-7 章。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当合法章节编号被误拒绝时抛出。
    """

    bundle = _bundle()

    assert tuple(chapter.chapter_id for chapter in project_chapter_facts(bundle, chapter_ids=(0,)).chapters) == (0,)
    assert tuple(chapter.chapter_id for chapter in project_chapter_facts(bundle, chapter_ids=(7,)).chapters) == (7,)
    assert (
        tuple(
            chapter.chapter_id
            for chapter in project_chapter_facts(bundle, chapter_ids=tuple(range(8))).chapters
        )
        == tuple(range(8))
    )


def test_missing_or_invalid_fund_type_yields_unknown_without_lens_or_item_rules() -> None:
    """验证基金类型缺失或非法时不调用 lens / ITEM_RULE 有效路径，见模板第 1 章。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 unknown 路径仍产生 lens 或 ITEM_RULE 决策时抛出。
    """

    missing_identity = _field({"classification_basis": ("fixture",)}, "basic_identity")
    invalid_identity = _field(
        {"classified_fund_type": "money_fund", "classification_basis": ("fixture",)},
        "basic_identity",
    )

    for identity, reason in (
        (missing_identity, "classified_fund_type_missing"),
        (invalid_identity, "classified_fund_type_invalid"),
    ):
        projection = project_chapter_facts(
            replace(_bundle(), basic_identity=identity),
            chapter_ids=(1, 2),
        )
        assert projection.fund_type == "unknown"
        assert reason in projection.global_missing_reasons
        for chapter in projection.chapters:
            assert chapter.lens_resolution.lens_key == "unknown"
            assert chapter.lens_resolution.statements == ()
            assert chapter.item_rule_projection.decisions == ()
            assert chapter.facet_resolution.facets == ()


def test_preferred_lens_resolution_preserves_default_and_exact_lens() -> None:
    """验证 preferred_lens 精确命中和 default fallback，见模板第 2/3 章。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 lens key、priority 或 fallback 状态错误时抛出。
    """

    projection = project_chapter_facts(_bundle(fund_type="active_fund"), chapter_ids=(2, 3))
    chapter_2, chapter_3 = projection.chapters

    assert chapter_2.lens_resolution.lens_key == "default"
    assert chapter_2.lens_resolution.used_default is True
    assert chapter_3.lens_resolution.lens_key == "active_fund"
    assert chapter_3.lens_resolution.used_default is False
    assert chapter_3.lens_resolution.priority == "core"


def test_item_rule_decisions_are_chapter_scoped_and_fund_type_deterministic() -> None:
    """验证 ITEM_RULE 按章节分发且只用基金类型触发，见模板第 1/2 章。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 ITEM_RULE 决策不符合基金类型规则时抛出。
    """

    active = project_chapter_facts(_bundle(fund_type="active_fund"), chapter_ids=(1, 2))
    index = project_chapter_facts(_bundle(fund_type="index_fund"), chapter_ids=(1, 2))

    assert _decision_status(active.chapters[0], "chapter_1_manager_philosophy") == "render"
    assert _decision_status(active.chapters[1], "chapter_2_alpha_yearly_breakdown") == "render"
    assert _decision_status(active.chapters[0], "chapter_1_index_constituents") == "delete"
    assert _decision_status(index.chapters[0], "chapter_1_index_constituents") == "render"
    assert _decision_status(index.chapters[1], "chapter_2_tracking_error_analysis") == "render"
    assert _decision_status(index.chapters[0], "chapter_1_manager_philosophy") == "delete"

    for fund_type in ("bond_fund", "qdii_fund", "fof_fund"):
        projection = project_chapter_facts(_bundle(fund_type=fund_type), chapter_ids=(1, 2))
        decisions = tuple(
            decision
            for chapter in projection.chapters
            for decision in chapter.item_rule_projection.decisions
        )
        assert decisions
        assert all(decision.status == "delete" for decision in decisions)


def test_facet_resolution_does_not_semantically_guess_subtype() -> None:
    """验证 facet 不从候选 catalog 猜 subtype，见模板 preferred_lens。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当候选 facet 被误放入 asserted facets 时抛出。
    """

    projection = project_chapter_facts(_bundle(fund_type="active_fund"), chapter_ids=(1,))
    facet_resolution = projection.chapters[0].facet_resolution

    assert facet_resolution.facets == ()
    assert "主动权益基金（价值风格）" in facet_resolution.non_asserted_facets
    assert "unsupported_facet_inference" in facet_resolution.reason
    assert "unsupported_facet_inference" in projection.chapters[0].missing_reasons
    assert all(
        "显式 facet 均未触发" in decision.reason or "基金类型 active_fund" in decision.reason
        for decision in projection.chapters[0].item_rule_projection.decisions
    )


def test_missing_field_semantics_and_anchor_traceability() -> None:
    """验证缺失字段、缺锚点和 fact anchor 引用完整性，见模板第 3 章。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当缺失语义或锚点引用错误时抛出。
    """

    no_anchor_strategy = ExtractedField(
        value={"strategy_summary": "精选个股"},
        anchors=(),
        extraction_mode="direct",
        note=None,
    )
    missing_turnover = ExtractedField(
        value=None,
        anchors=(),
        extraction_mode="missing",
        note="fixture missing",
    )
    projection = project_chapter_facts(
        replace(
            _bundle(),
            manager_strategy_text=no_anchor_strategy,
            turnover_rate=missing_turnover,
        ),
        chapter_ids=(3,),
    )
    chapter = projection.chapters[0]
    anchor_ids = {anchor.anchor_id for anchor in chapter.evidence_anchors}

    turnover_fact = _fact(chapter, "turnover_rate")
    strategy_fact = _fact(chapter, "manager_strategy_text")
    assert turnover_fact.status == "missing"
    assert turnover_fact.missing_reason == "field_missing"
    assert strategy_fact.status == "available"
    assert strategy_fact.missing_reason == "evidence_missing"
    assert strategy_fact.evidence_anchor_ids == ()
    for fact in chapter.facts:
        assert set(fact.evidence_anchor_ids).issubset(anchor_ids)


def test_nav_data_three_states() -> None:
    """验证 NAV 数据 available / missing / unavailable 三态，见模板第 2 章。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 NAV 三态映射错误时抛出。
    """

    available = project_chapter_facts(_bundle(), chapter_ids=(2,)).chapters[0]
    missing = project_chapter_facts(
        replace(
            _bundle(),
            nav_data=NavDataResult(fund_code="110011", records=[], source="fixture", cached=False),
        ),
        chapter_ids=(2,),
    ).chapters[0]
    unavailable = project_chapter_facts(
        replace(
            _bundle(),
            nav_data=NavDataResult(
                fund_code="110011",
                records=[],
                source="nav_unavailable",
                cached=False,
                unavailable=True,
                unavailable_reason="RuntimeError: network down",
            ),
        ),
        chapter_ids=(2,),
    ).chapters[0]

    assert _fact(available, "nav_data").status == "available"
    assert _fact(available, "nav_data").evidence_anchor_ids
    assert _fact(missing, "nav_data").status == "missing"
    assert _fact(missing, "nav_data").missing_reason == "field_missing"
    assert _fact(unavailable, "nav_data").status == "unavailable"
    assert _fact(unavailable, "nav_data").missing_reason == "field_unavailable"


def test_bond_risk_evidence_group_anchors_expand_to_chapter_anchors() -> None:
    """验证债券风险组级 anchors 展开为章节锚点，见模板第 6 章。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当组级 anchors 未展开为 ChapterEvidenceAnchor 时抛出。
    """

    value = _bond_risk_value()
    projection = project_chapter_facts(
        replace(
            _bundle(fund_type="bond_fund"),
            bond_risk_evidence=ExtractedField(
                value=value,
                anchors=(),
                extraction_mode="direct",
                note=None,
            ),
        ),
        chapter_ids=(6,),
    )
    chapter = projection.chapters[0]
    bond_fact = _fact(chapter, "bond_risk_evidence")

    assert bond_fact.status == "available"
    assert bond_fact.value == value
    assert bond_fact.evidence_anchor_ids
    assert value.anchors
    assert set(bond_fact.evidence_anchor_ids) <= {anchor.anchor_id for anchor in chapter.evidence_anchors}
    projected_anchor = next(anchor for anchor in chapter.evidence_anchors if anchor.anchor_id in bond_fact.evidence_anchor_ids)
    assert projected_anchor.source_kind == "annual_report"
    assert projected_anchor.document_year == 2024
    assert projected_anchor.section_id == "§8"
    assert projected_anchor.row_locator == "duration fixture"
    assert projected_anchor.note == (
        "bond_risk_evidence role=fixture; "
        "source_anchor=bond-risk:110011:2024:duration_rate_risk:1"
    )


def test_missing_bond_risk_evidence_still_has_no_chapter_anchors() -> None:
    """验证缺失债券风险证据不会伪造章节锚点，见模板第 6 章。"""

    projection = project_chapter_facts(_bundle(fund_type="bond_fund"), chapter_ids=(6,))
    chapter = projection.chapters[0]
    bond_fact = _fact(chapter, "bond_risk_evidence")

    assert bond_fact.status == "not_applicable"
    assert bond_fact.evidence_anchor_ids == ()
    assert all("bond_risk_evidence" not in (anchor.note or "") for anchor in chapter.evidence_anchors)


def test_source_kind_unknown_note() -> None:
    """验证 projection 层允许 unknown source kind 兜底，见模板第 0-7 章证据输入。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当未知来源锚点未被投影为 `unknown` 时抛出。
    """

    unknown_anchor = EvidenceAnchor(
        source_kind=cast(EvidenceSourceKind, "vendor_feed"),
        document_year=2024,
        section_id="§2",
        page_number=None,
        table_id=None,
        row_locator="identity",
        note="unknown source fixture",
    )
    projection = project_chapter_facts(
        replace(
            _bundle(),
            basic_identity=_field(
                {
                    "fund_code": "110011",
                    "classified_fund_type": "active_fund",
                    "classification_basis": ("fixture",),
                },
                "basic_identity",
                anchors=(unknown_anchor,),
            ),
        ),
        chapter_ids=(1,),
    )

    assert projection.chapters[0].evidence_anchors[0].source_kind == "unknown"


def test_projection_does_not_call_repository_or_source_helpers() -> None:
    """静态验证 chapter_facts 不导入仓库、PDF、来源 helper、LLM 或 dayu。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当模块 import 越过 Gate 1 范围时抛出。
    """

    source_path = Path("fund_agent/fund/chapter_facts.py")
    tree = ast.parse(source_path.read_text(encoding="utf-8"))
    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name for alias in node.names)
        if isinstance(node, ast.ImportFrom) and node.module is not None:
            imports.add(node.module)
    imports.discard("fund_agent.fund.source_facts")

    forbidden_fragments = (
        "documents",
        "repository",
        "cache",
        "pdf",
        "source",
        "downloader",
        "parser",
        "service",
        "dayu",
        "openai",
        "llm",
    )
    assert all(not any(fragment in module for fragment in forbidden_fragments) for module in imports)


def _bundle(
    *,
    fund_type: str = "active_fund",
) -> StructuredFundDataBundle:
    """构造章节事实投影测试用结构化数据包。

    Args:
        fund_type: 写入 `basic_identity.classified_fund_type` 的基金类型。

    Returns:
        测试用结构化数据包。

    Raises:
        无显式抛出。
    """

    basic_identity = _field(
        {
            "fund_name": "测试基金",
            "fund_code": "110011",
            "fund_category": "混合型",
            "classified_fund_type": fund_type,
            "classification_basis": ("fixture classification",),
        },
        "basic_identity",
    )
    return StructuredFundDataBundle(
        fund_code="110011",
        report_year=2024,
        basic_identity=basic_identity,
        product_profile=_field({"investment_objective": "长期增值"}, "product_profile"),
        benchmark=_field({"benchmark_text": "沪深300指数收益率"}, "benchmark"),
        index_profile=ExtractedField(
            value=_index_profile_value(),
            anchors=(_anchor("index_profile"),),
            extraction_mode="direct",
            note=None,
        ),
        fee_schedule=_field({"management_fee": "1.20%", "custody_fee": "0.20%"}, "fee_schedule"),
        turnover_rate=_field({"turnover_rate": "120%"}, "turnover_rate"),
        nav_benchmark_performance=_field(
            {"nav_growth_rate": "1.0%", "benchmark_return_rate": "0.5%"},
            "nav_benchmark_performance",
        ),
        investor_return=_field({"investor_return_rate": "0.8%"}, "investor_return"),
        tracking_error=ExtractedField(
            value=_tracking_error_value(),
            anchors=(_anchor("tracking_error"),),
            extraction_mode="direct",
            note=None,
        ),
        share_change=_field({"beginning_share": "1", "ending_share": "2"}, "share_change"),
        manager_alignment=_field({"manager_holding": "0"}, "manager_alignment"),
        manager_strategy_text=_field({"strategy_summary": "精选个股"}, "manager_strategy_text"),
        portfolio_managers=_field(
            {
                "schema_version": "portfolio_manager_tenure_list.v1",
                "manager_count": 1,
                "portfolio_managers": [{"name": "张三", "role": "基金经理"}],
            },
            "portfolio_managers",
        ),
        holdings_snapshot=_field({"top_holdings": [{"name": "A"}]}, "holdings_snapshot"),
        holder_structure=_field(
            {"institutional_holder": "10%", "individual_holder": "90%"},
            "holder_structure",
        ),
        risk_characteristic_text=_field(
            {
                "schema_version": "risk_characteristic_text.v1",
                "risk_characteristic_text": "本基金为混合型基金，风险收益特征高于债券型基金。",
            },
            "risk_characteristic_text",
        ),
        nav_data=NavDataResult(
            fund_code="110011",
            records=[{"date": "2024-12-31", "nav": "1.00"}],
            source="fixture",
            cached=True,
        ),
        bond_risk_evidence=ExtractedField(
            value=None,
            anchors=(),
            extraction_mode="missing",
            note="not_applicable_non_bond_fund",
        ),
    )


def _field(
    value: dict[str, object] | None,
    row_locator: str,
    *,
    anchors: tuple[EvidenceAnchor, ...] | None = None,
) -> ExtractedField[dict[str, object]]:
    """构造带普通证据锚点的测试字段。

    Args:
        value: 字段值。
        row_locator: 行级定位。
        anchors: 显式测试锚点；未提供时按 value 自动生成。

    Returns:
        测试用 `ExtractedField`。

    Raises:
        无显式抛出。
    """

    field_anchors = anchors if anchors is not None else (() if value is None else (_anchor(row_locator),))
    return ExtractedField(
        value=value,
        anchors=field_anchors,
        extraction_mode="missing" if value is None else "direct",
        note="fixture missing" if value is None else None,
    )


def _anchor(row_locator: str) -> EvidenceAnchor:
    """构造测试证据锚点。

    Args:
        row_locator: 行级定位。

    Returns:
        测试用证据锚点。

    Raises:
        无显式抛出。
    """

    return EvidenceAnchor(
        source_kind="annual_report",
        document_year=2024,
        section_id="§2",
        page_number=None,
        table_id=None,
        row_locator=row_locator,
        note=f"{row_locator}: fixture",
    )


def _index_profile_value() -> IndexProfileValue:
    """构造指数画像测试值，见模板第 1 章。

    Args:
        无。

    Returns:
        测试用 `IndexProfileValue`。

    Raises:
        无显式抛出。
    """

    return IndexProfileValue(
        benchmark_text="沪深300指数收益率",
        benchmark_identity_status="identified",
        benchmark_index_name="沪深300",
        benchmark_index_code="000300",
        benchmark_component_text=(),
        methodology_availability="benchmark_only",
        methodology_summary=None,
        methodology_source_title=None,
        constituents_availability="benchmark_only",
        constituents_summary=None,
        constituents_as_of_date=None,
        source_tier="benchmark_context",
        missing_reasons=(),
    )


def _tracking_error_value() -> TrackingErrorValue:
    """构造跟踪误差测试值，见模板第 2 章 R=A+B-C。

    Args:
        无。

    Returns:
        测试用 `TrackingErrorValue`。

    Raises:
        无显式抛出。
    """

    return TrackingErrorValue(
        value=Decimal("0.0123"),
        value_text="1.23%",
        unit="ratio",
        period_label="过去一年",
        period_start=None,
        period_end=None,
        annualized=True,
        source_type="direct_disclosure",
        calculation_method="disclosed",
        benchmark_identity_status="identified",
        benchmark_index_name="沪深300",
        benchmark_index_code="000300",
        fund_series_source=None,
        index_series_source=None,
        observation_count=None,
        frequency="annual_report_period",
        annualization_factor=None,
        input_period_complete=True,
        provenance_note="fixture",
    )


def _bond_risk_value() -> BondRiskEvidenceValue:
    """构造债券风险证据测试值，见模板第 6 章“核心风险”。

    Args:
        无。

    Returns:
        测试用 `BondRiskEvidenceValue`。

    Raises:
        无显式抛出。
    """

    groups = tuple(_bond_risk_group(group_id) for group_id in BOND_RISK_EVIDENCE_GROUP_IDS)
    anchors = (
        BondRiskEvidenceAnchorRef(
            anchor_id="bond-risk:110011:2024:duration_rate_risk:1",
            section_id="§8",
            page_number=None,
            table_id=None,
            row_locator="duration fixture",
            evidence_role="fixture",
        ),
    )
    contract_status: BondRiskEvidenceContractStatus = "satisfied"
    return BondRiskEvidenceValue(
        schema_version=BOND_RISK_EVIDENCE_CONTRACT_ID,
        contract_id=BOND_RISK_EVIDENCE_CONTRACT_ID,
        fund_code="110011",
        report_year=2024,
        groups=groups,
        anchors=anchors,
        satisfied_group_ids=BOND_RISK_EVIDENCE_GROUP_IDS,
        missing_group_ids=(),
        weak_group_ids=(),
        ambiguous_group_ids=(),
        contract_status=contract_status,
    )


def _bond_risk_group(group_id: BondRiskEvidenceGroupId) -> BondRiskEvidenceGroupRecord:
    """构造债券风险证据组记录，见模板第 6 章。

    Args:
        group_id: 债券风险证据组 ID。

    Returns:
        测试用风险组记录。

    Raises:
        无显式抛出。
    """

    status: BondRiskEvidenceStatus = "accepted"
    return BondRiskEvidenceGroupRecord(
        group_id=group_id,
        status=status,
        strength="qualitative_direct",
        summary="fixture accepted",
        measurement_kind="risk_disclosure",
        metric_name="fixture_metric",
        metric_value="fixture value",
        metric_unit=None,
        period_label=None,
        source_anchor_ids=("bond-risk:110011:2024:duration_rate_risk:1",),
        na_reason=None,
        reviewer_note=None,
    )


def _field_names(chapter: object) -> set[str]:
    """读取章节 fact 字段名集合。

    Args:
        chapter: `ChapterFactInput` 对象。

    Returns:
        字段名集合。

    Raises:
        AttributeError: 当传入对象不是章节事实输入时抛出。
    """

    return {fact.source_field_name for fact in chapter.facts}


def _fact(chapter: object, source_field_name: str) -> object:
    """按字段名读取章节 fact。

    Args:
        chapter: `ChapterFactInput` 对象。
        source_field_name: 来源字段名。

    Returns:
        匹配的章节 fact。

    Raises:
        AssertionError: 当未找到匹配 fact 时抛出。
    """

    for fact in chapter.facts:
        if fact.source_field_name == source_field_name:
            return fact
    raise AssertionError(f"missing fact: {source_field_name}")


def _decision_status(chapter: object, rule_id: str) -> str:
    """按 ITEM_RULE 编号读取当前章节决策状态。

    Args:
        chapter: `ChapterFactInput` 对象。
        rule_id: ITEM_RULE 编号。

    Returns:
        决策状态。

    Raises:
        AssertionError: 当未找到匹配 ITEM_RULE 决策时抛出。
    """

    for decision in chapter.item_rule_projection.decisions:
        if decision.rule_id == rule_id:
            return decision.status
    raise AssertionError(f"missing decision: {rule_id}")
