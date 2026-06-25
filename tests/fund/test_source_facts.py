"""Atomic source fact 契约测试。"""

from __future__ import annotations

from dataclasses import FrozenInstanceError
from decimal import Decimal

import pytest

from fund_agent.fund.data.nav_data import NavDataResult
from fund_agent.fund.data_extractor import (
    StructuredFundDataBundle,
    _legacy_field_from_composite_view,
)
from fund_agent.fund.extractors.models import EvidenceAnchor, ExtractedField
from fund_agent.fund.processors.contracts import FundProcessorResult
from fund_agent.fund.source_facts import (
    AtomicSourceFact,
    AtomicSourceFactStore,
    CompositeAnalysisView,
    FactDependencyMetadata,
    build_composite_analysis_view,
    empty_atomic_source_fact_store,
)


def _anchor(row_locator: str = "field=fee_schedule.management_fee") -> EvidenceAnchor:
    """构造测试证据锚点。

    Args:
        row_locator: 行级定位字符串。

    Returns:
        测试用证据锚点。

    Raises:
        无显式抛出。
    """

    return EvidenceAnchor(
        source_kind="annual_report",
        document_year=2024,
        section_id="§7",
        page_number=10,
        table_id="fee-table",
        row_locator=row_locator,
        note="fixture",
    )


def _fact(
    fact_id: str = "fee_schedule.management_fee",
    *,
    status: str = "accepted",
    value: object | None = Decimal("1.20"),
    gaps: tuple[str, ...] = (),
) -> AtomicSourceFact:
    """构造测试 atomic source fact。

    Args:
        fact_id: 稳定事实 ID。
        status: 事实状态。
        value: 事实值。
        gaps: 事实缺口。

    Returns:
        测试用 atomic source fact。

    Raises:
        ValueError: 当参数违反 atomic source fact 契约时由被测类抛出。
    """

    return AtomicSourceFact(
        fact_id=fact_id,
        family_id="return_attribution.v1",
        value=value,
        status=status,
        extraction_mode="direct" if status == "accepted" else "missing",
        anchors=() if status == "missing" else (_anchor(f"field={fact_id}"),),
        provenance=None,
        gaps=gaps,
        source_field_path=fact_id,
    )


def _field(value: object | None = None) -> ExtractedField[dict[str, object]]:
    """构造测试用 legacy 字段。

    Args:
        value: 字段值；缺省时使用空 dict。

    Returns:
        测试用 `ExtractedField`。

    Raises:
        无显式抛出。
    """

    return ExtractedField(
        value={} if value is None else value,  # type: ignore[arg-type]
        anchors=(),
        extraction_mode="direct",
    )


def _bundle() -> StructuredFundDataBundle:
    """构造最小结构化基金数据包。

    Args:
        无。

    Returns:
        测试用 `StructuredFundDataBundle`。

    Raises:
        无显式抛出。
    """

    return StructuredFundDataBundle(
        fund_code="110011",
        report_year=2024,
        basic_identity=_field(),
        product_profile=_field(),
        benchmark=_field(),
        index_profile=ExtractedField(value=None, anchors=(), extraction_mode="missing"),
        fee_schedule=_field({"management_fee": "1.20%"}),
        turnover_rate=_field(),
        nav_benchmark_performance=_field(),
        investor_return=_field(),
        tracking_error=ExtractedField(value=None, anchors=(), extraction_mode="missing"),
        share_change=_field(),
        manager_alignment=_field(),
        manager_strategy_text=_field(),
        holdings_snapshot=_field(),
        holder_structure=_field(),
        nav_data=NavDataResult(fund_code="110011", records=[], source="fixture", cached=False),
    )


def test_atomic_source_fact_rejects_mismatched_source_path() -> None:
    """Atomic fact 必须让 fact_id 等于 source_field_path。"""

    with pytest.raises(ValueError, match="fact_id"):
        AtomicSourceFact(
            fact_id="fee_schedule.management_fee",
            family_id="return_attribution.v1",
            value=Decimal("1.20"),
            status="accepted",
            extraction_mode="direct",
            anchors=(_anchor(),),
            provenance=None,
            gaps=(),
            source_field_path="fee_schedule.custody_fee",
        )


def test_atomic_source_fact_rejects_sibling_dependencies() -> None:
    """Atomic fact 不能携带 sibling fact 依赖。"""

    with pytest.raises(ValueError, match="不得依赖"):
        AtomicSourceFact(
            fact_id="fee_schedule.management_fee",
            family_id="return_attribution.v1",
            value=Decimal("1.20"),
            status="accepted",
            extraction_mode="direct",
            anchors=(_anchor(),),
            provenance=None,
            gaps=(),
            source_field_path="fee_schedule.management_fee",
            dependency_metadata=FactDependencyMetadata(
                dependency_fact_ids=("fee_schedule.custody_fee",),
                dependency_policy="all_required",
            ),
        )


def test_atomic_source_fact_store_is_immutable_and_indexed_by_fact_id() -> None:
    """Store 按 fact id 索引且对外不可变。"""

    fact = _fact()
    store = AtomicSourceFactStore((fact,))

    assert store.get_required("fee_schedule.management_fee") == fact
    assert store.get_optional("missing") is None
    assert store.by_family("return_attribution.v1") == (fact,)
    with pytest.raises(TypeError):
        store.facts["other"] = fact  # type: ignore[index]
    with pytest.raises(FrozenInstanceError):
        store.facts = {}  # type: ignore[misc]


def test_atomic_source_fact_store_rejects_duplicate_or_mismatched_keys() -> None:
    """Store 拒绝重复 fact id 和映射 key 不一致。"""

    fact = _fact()
    with pytest.raises(ValueError, match="重复"):
        AtomicSourceFactStore((fact, fact))
    with pytest.raises(ValueError, match="key"):
        AtomicSourceFactStore({"other": fact})


def test_atomic_source_fact_store_merge_strict_allows_equal_and_rejects_conflict() -> None:
    """严格合并允许相同事实，拒绝同 ID 不同事实。"""

    fact = _fact()
    same = AtomicSourceFactStore((fact,))
    merged = same.merge_strict(AtomicSourceFactStore((fact,)))

    assert merged.get_required(fact.fact_id) == fact
    with pytest.raises(ValueError, match="冲突"):
        same.merge_strict(
            AtomicSourceFactStore(
                (_fact(value=Decimal("1.50")),)
            )
        )


def test_build_composite_analysis_view_aggregates_dependencies() -> None:
    """复合视图从依赖事实聚合状态、锚点和缺口。"""

    management = _fact("fee_schedule.management_fee")
    custody = _fact("fee_schedule.custody_fee", status="missing", value=None, gaps=("missing",))
    store = AtomicSourceFactStore((management, custody))
    view = build_composite_analysis_view(
        view_id="fee_schedule",
        source_facts=store,
        dependency_fact_ids=("fee_schedule.management_fee", "fee_schedule.custody_fee"),
    )

    assert view.status == "partial"
    assert view.value == {
        "fee_schedule.management_fee": Decimal("1.20"),
        "fee_schedule.custody_fee": None,
    }
    assert view.dependency_fact_ids == (
        "fee_schedule.management_fee",
        "fee_schedule.custody_fee",
    )
    assert view.anchors == management.anchors
    assert view.gaps == ("missing",)


def test_build_composite_analysis_view_derives_accepted_value_from_dependencies() -> None:
    """accepted 复合视图的可见值只能来自依赖 atomic facts。"""

    management = _fact("fee_schedule.management_fee", value="1.20%")
    custody = _fact("fee_schedule.custody_fee", value="0.20%")
    store = AtomicSourceFactStore((management, custody))
    view = build_composite_analysis_view(
        view_id="fee_schedule",
        source_facts=store,
        dependency_fact_ids=("fee_schedule.management_fee", "fee_schedule.custody_fee"),
    )

    assert view.status == "accepted"
    assert view.value == {
        "fee_schedule.management_fee": "1.20%",
        "fee_schedule.custody_fee": "0.20%",
    }
    assert view.value != {"management_fee": "9.99%", "custody_fee": "9.99%"}


def test_build_composite_analysis_view_rejects_caller_supplied_value() -> None:
    """helper 不接受 caller-supplied composite value，避免形成第二真源。"""

    store = AtomicSourceFactStore((_fact(),))

    with pytest.raises(TypeError, match="value"):
        build_composite_analysis_view(
            view_id="fee_schedule",
            source_facts=store,
            dependency_fact_ids=("fee_schedule.management_fee",),
            value={"fee_schedule.management_fee": "fabricated"},
        )


def test_build_composite_analysis_view_absent_dependency_fails_closed_with_gap() -> None:
    """缺失 dependency fact 返回 partial/missing 视图和明确缺口，不泄漏 KeyError。"""

    management = _fact("fee_schedule.management_fee", value="1.20%")
    store = AtomicSourceFactStore((management,))
    view = build_composite_analysis_view(
        view_id="fee_schedule",
        source_facts=store,
        dependency_fact_ids=("fee_schedule.management_fee", "fee_schedule.custody_fee"),
    )

    assert view.status == "partial"
    assert view.value == {"fee_schedule.management_fee": "1.20%"}
    assert view.gaps == ("missing dependency fact: fee_schedule.custody_fee",)


def test_build_composite_analysis_view_missing_all_dependencies_returns_missing() -> None:
    """全部依赖缺失时返回 missing 视图且 value 为 None。"""

    view = build_composite_analysis_view(
        view_id="fee_schedule",
        source_facts=empty_atomic_source_fact_store(),
        dependency_fact_ids=("fee_schedule.management_fee",),
    )

    assert view.status == "missing"
    assert view.value is None
    assert view.gaps == ("missing dependency fact: fee_schedule.management_fee",)


def test_build_composite_analysis_view_rejects_required_ids_outside_dependencies() -> None:
    """required_fact_ids 必须是 dependency_fact_ids 子集。"""

    store = AtomicSourceFactStore((_fact(),))

    with pytest.raises(ValueError, match="子集"):
        build_composite_analysis_view(
            view_id="fee_schedule",
            source_facts=store,
            dependency_fact_ids=("fee_schedule.management_fee",),
            required_fact_ids=("fee_schedule.custody_fee",),
        )


def test_build_composite_analysis_view_empty_dependencies_has_null_value() -> None:
    """空 dependency_fact_ids 不会保留任何非空 value。"""

    view = build_composite_analysis_view(
        view_id="fee_schedule",
        source_facts=AtomicSourceFactStore((_fact(),)),
        dependency_fact_ids=(),
    )

    assert view.status == "missing"
    assert view.value is None
    assert view.gaps == ()


def test_legacy_field_from_composite_view_preserves_bundle_shape() -> None:
    """复合视图可投影为 legacy `ExtractedField[dict]`。"""

    view = CompositeAnalysisView(
        view_id="fee_schedule",
        value={"management_fee": "1.20%"},
        status="accepted",
        anchors=(_anchor(),),
        gaps=(),
        dependency_fact_ids=("fee_schedule.management_fee",),
    )
    field = _legacy_field_from_composite_view(view)

    assert field.value == {"management_fee": "1.20%"}
    assert field.anchors == view.anchors
    assert field.extraction_mode == "derived"
    assert field.note is None


def test_processor_result_exposes_only_default_source_fact_surface() -> None:
    """Processor result 默认只通过 `source_facts` 暴露 atomic store。"""

    result = FundProcessorResult(
        processor_id="fixture",
        output_schema_version="v1",
        fund_code="110011",
        report_year=2024,
        fund_type="active_fund",
        report_type="annual_report",
        input_intermediate_kind="parsed_annual_report.v1",
        field_families=(),
        gaps=(),
        anchors=(),
        source_provenance=None,
        candidate_boundary=None,
        contract_status="missing",
    )

    assert result.source_facts.facts == {}
    assert not hasattr(result, "source_fact_ids")


def test_structured_bundle_default_source_facts_preserves_constructor_compatibility() -> None:
    """Bundle trailing default store 保持既有构造兼容。"""

    bundle = _bundle()

    assert bundle.source_facts.facts == {}
    assert bundle.fee_schedule.value == {"management_fee": "1.20%"}


def test_structured_bundle_can_mirror_processor_source_facts() -> None:
    """Bundle 可携带 processor source facts 镜像。"""

    store = AtomicSourceFactStore((_fact(),))
    bundle = StructuredFundDataBundle(
        fund_code="110011",
        report_year=2024,
        basic_identity=_field(),
        product_profile=_field(),
        benchmark=_field(),
        index_profile=ExtractedField(value=None, anchors=(), extraction_mode="missing"),
        fee_schedule=_field({"management_fee": "1.20%"}),
        turnover_rate=_field(),
        nav_benchmark_performance=_field(),
        investor_return=_field(),
        tracking_error=ExtractedField(value=None, anchors=(), extraction_mode="missing"),
        share_change=_field(),
        manager_alignment=_field(),
        manager_strategy_text=_field(),
        holdings_snapshot=_field(),
        holder_structure=_field(),
        nav_data=NavDataResult(fund_code="110011", records=[], source="fixture", cached=False),
        source_facts=store,
    )

    assert bundle.source_facts is store


def test_empty_atomic_source_fact_store_returns_independent_empty_store() -> None:
    """空 store factory 返回不可变空存储。"""

    first = empty_atomic_source_fact_store()
    second = empty_atomic_source_fact_store()

    assert first.facts == {}
    assert second.facts == {}
    assert first is not second
