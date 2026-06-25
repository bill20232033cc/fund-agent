"""章节事实 atomic projection bridge 测试，覆盖模板第 2/3 章。"""

from __future__ import annotations

from dataclasses import replace

from fund_agent.fund.chapter_facts import project_chapter_facts
from fund_agent.fund.extractors.models import EvidenceAnchor
from fund_agent.fund.source_facts import AtomicSourceFact, AtomicSourceFactStore
from tests.fund.test_chapter_facts import _anchor, _bundle


def test_cost_chapter_projects_management_fee_without_custody_fee() -> None:
    """验证第 2 章成本事实可引用单个 atomic fee fact。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 management_fee 被 custody_fee sibling 耦合时抛出。
    """

    projection = project_chapter_facts(
        _bundle_with_source_facts(
            _source_fact("fee_schedule.management_fee", "return_attribution.v1", "1.20%"),
        ),
        chapter_ids=(2,),
    )

    fact_ids = tuple(
        fact.source_fact_ids[0]
        for fact in projection.chapters[0].facts
        if fact.source_fact_ids
    )
    derived_view_ids = tuple(
        fact.derived_view_id
        for fact in projection.chapters[0].facts
        if fact.derived_view_id is not None
    )
    management_fee = _source_fact_entry(projection.chapters[0], "fee_schedule.management_fee")

    assert "fee_schedule.management_fee" in fact_ids
    assert "fee_schedule.custody_fee" not in fact_ids
    assert management_fee.field_path == "AtomicSourceFact.fee_schedule.management_fee"
    assert management_fee.derived_view_id is None
    assert "fee_schedule" not in derived_view_ids
    assert all(view.view_id != "fee_schedule" for view in projection.derived_views)
    assert "field_missing" not in projection.chapters[0].missing_reasons


def test_return_attribution_projects_nav_and_benchmark_as_separate_facts() -> None:
    """验证第 2 章收益归因拆分 NAV 与 benchmark atomic facts。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 NAV 和 benchmark 被单个 composite fact 替代时抛出。
    """

    projection = project_chapter_facts(
        _bundle_with_source_facts(
            _source_fact(
                "nav_benchmark_performance.nav_growth_rate",
                "return_attribution.v1",
                "8.00%",
            ),
            _source_fact(
                "nav_benchmark_performance.benchmark_return_rate",
                "return_attribution.v1",
                "6.00%",
            ),
        ),
        chapter_ids=(2,),
    )

    nav_fact = _source_fact_entry(
        projection.chapters[0],
        "nav_benchmark_performance.nav_growth_rate",
    )
    benchmark_fact = _source_fact_entry(
        projection.chapters[0],
        "nav_benchmark_performance.benchmark_return_rate",
    )

    assert nav_fact.value == "8.00%"
    assert benchmark_fact.value == "6.00%"
    assert nav_fact.source_fact_ids == ("nav_benchmark_performance.nav_growth_rate",)
    assert benchmark_fact.source_fact_ids == (
        "nav_benchmark_performance.benchmark_return_rate",
    )


def test_manager_profile_projects_strategy_and_outlook_as_separate_facts() -> None:
    """验证第 3 章基金经理画像拆分策略与展望 atomic facts。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 strategy/outlook 被 composite dict sibling coupling 时抛出。
    """

    projection = project_chapter_facts(
        _bundle_with_source_facts(
            _source_fact(
                "manager_strategy_text.strategy_summary",
                "manager_profile.v1",
                "坚持均衡配置",
            ),
            _source_fact(
                "manager_strategy_text.market_outlook",
                "manager_profile.v1",
                "关注基本面变化",
            ),
        ),
        chapter_ids=(3,),
    )

    strategy = _source_fact_entry(
        projection.chapters[0],
        "manager_strategy_text.strategy_summary",
    )
    outlook = _source_fact_entry(
        projection.chapters[0],
        "manager_strategy_text.market_outlook",
    )

    assert strategy.value == "坚持均衡配置"
    assert outlook.value == "关注基本面变化"
    assert strategy.field_path == "AtomicSourceFact.manager_strategy_text.strategy_summary"
    assert outlook.field_path == "AtomicSourceFact.manager_strategy_text.market_outlook"


def test_derived_view_facts_carry_dependency_ids() -> None:
    """验证 derived view fact 与 projection.derived_views 记录依赖 facts。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 derived view 缺少 dependency_fact_ids 时抛出。
    """

    projection = project_chapter_facts(
        _bundle_with_source_facts(
            _source_fact("fee_schedule.management_fee", "return_attribution.v1", "1.20%"),
            _source_fact("fee_schedule.custody_fee", "return_attribution.v1", "0.20%"),
        ),
        chapter_ids=(2,),
    )

    derived_fact = next(
        fact
        for fact in projection.chapters[0].facts
        if fact.derived_view_id == "fee_schedule"
    )
    derived_view = next(view for view in projection.derived_views if view.view_id == "fee_schedule")

    assert derived_fact.field_path == "CompositeAnalysisView.fee_schedule"
    assert derived_fact.source_fact_ids == ()
    assert derived_view.dependency_fact_ids == (
        "fee_schedule.management_fee",
        "fee_schedule.custody_fee",
    )
    assert derived_view.value == {
        "fee_schedule.management_fee": "1.20%",
        "fee_schedule.custody_fee": "0.20%",
    }


def test_legacy_projection_with_empty_store_preserves_non_migrated_behavior() -> None:
    """验证空 atomic store 下非迁移字段保持 legacy bridge empty。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 legacy 字段被错误改写为 atomic/derived bridge 时抛出。
    """

    projection = project_chapter_facts(_bundle(), chapter_ids=(3,))
    turnover = next(
        fact for fact in projection.chapters[0].facts if fact.source_field_name == "turnover_rate"
    )

    assert projection.source_facts.facts == {}
    assert projection.derived_views == ()
    assert turnover.field_path == "StructuredFundDataBundle.turnover_rate"
    assert turnover.source_fact_ids == ()
    assert turnover.derived_view_id is None


def test_projection_source_facts_mirror_bundle_store() -> None:
    """验证 ChapterFactProjection.source_facts 镜像 bundle.source_facts。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 projection 复制或丢失 source fact store 时抛出。
    """

    bundle = _bundle_with_source_facts(
        _source_fact("manager_alignment.manager_holding", "manager_profile.v1", "100万份以上"),
    )

    projection = project_chapter_facts(bundle, chapter_ids=(3,))

    assert projection.source_facts is bundle.source_facts


def _bundle_with_source_facts(*facts: AtomicSourceFact) -> object:
    """构造带 atomic source facts 的章节事实测试 bundle。

    Args:
        facts: 需要挂载到 bundle 的 atomic source facts。

    Returns:
        测试用 `StructuredFundDataBundle`。

    Raises:
        ValueError: 当 fact store 发现重复 fact id 时由被测类抛出。
    """

    return replace(_bundle(), source_facts=AtomicSourceFactStore(facts))


def _source_fact(fact_id: str, family_id: str, value: object | None) -> AtomicSourceFact:
    """构造测试用 accepted atomic source fact。

    Args:
        fact_id: 稳定 atomic source fact ID。
        family_id: 所属字段族 ID。
        value: atomic fact 值。

    Returns:
        测试用 `AtomicSourceFact`。

    Raises:
        ValueError: 当参数违反 atomic source fact 契约时由被测类抛出。
    """

    return AtomicSourceFact(
        fact_id=fact_id,
        family_id=family_id,
        value=value,
        status="accepted",
        extraction_mode="direct",
        anchors=(_atomic_anchor(fact_id),),
        provenance=None,
        gaps=(),
        source_field_path=fact_id,
    )


def _atomic_anchor(fact_id: str) -> EvidenceAnchor:
    """构造携带 source_field_path 的测试锚点。

    Args:
        fact_id: 稳定 atomic source fact ID。

    Returns:
        测试用证据锚点。

    Raises:
        无显式抛出。
    """

    base = _anchor(f"source_field_path={fact_id}; locator=fixture")
    return replace(base, note=f"field={fact_id}")


def _source_fact_entry(chapter: object, fact_id: str) -> object:
    """按 source fact id 读取章节事实。

    Args:
        chapter: `ChapterFactInput` 对象。
        fact_id: 稳定 atomic source fact ID。

    Returns:
        匹配的章节事实。

    Raises:
        AssertionError: 当 fact 不存在时抛出。
    """

    for fact in chapter.facts:
        if fact.source_fact_ids == (fact_id,):
            return fact
    raise AssertionError(f"missing source fact entry: {fact_id}")
