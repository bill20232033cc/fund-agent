"""Evidence Confirm atomic bridge audit 测试，覆盖模板第 2 章 R=A+B-C。"""

from __future__ import annotations

from dataclasses import replace

from fund_agent.fund.chapter_facts import (
    ChapterFactEntry,
    ChapterFactProjection,
    project_chapter_facts,
)
from fund_agent.fund.evidence_confirm import (
    EvidenceConfirmReference,
    confirm_projection_evidence_v2,
)
from fund_agent.fund.evidence_confirm_value_diagnostics import (
    summarize_value_match_diagnostics,
)
from fund_agent.fund.extractors.models import EvidenceAnchor
from fund_agent.fund.source_facts import AtomicSourceFact, AtomicSourceFactStore
from tests.fund.test_chapter_facts import _anchor, _bundle


def test_atomic_management_fee_value_match_ignores_custody_sibling() -> None:
    """验证 atomic bridge 只用 management_fee 单值，不展开 custody sibling。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 value_match 误用 composite sibling 时抛出。
    """

    projection = _projection_with_source_facts(
        _source_fact("fee_schedule.management_fee", "return_attribution.v1", "1.20%"),
        _source_fact("fee_schedule.custody_fee", "return_attribution.v1", "0.20%"),
    )
    fact = _source_fact_entry(projection, "fee_schedule.management_fee")
    projection = _replace_fact_value(
        projection,
        fact,
        {"management_fee": "1.20%", "custody_fee": "0.20%"},
    )
    fact = _source_fact_entry(projection, "fee_schedule.management_fee")

    result = confirm_projection_evidence_v2(
        projection,
        (_reference(fact.evidence_anchor_ids[0], "同源摘录只包含托管费 0.20%。"),),
    )

    fact_result = _fact_result(result, fact)
    assert _dimension_status(fact_result, "value_match") == "fail"
    assert fact_result.status == "fail"


def test_atomic_diagnostics_use_source_fact_id_material_tokens() -> None:
    """验证 diagnostics 通过 `source_fact_ids` 解析 atomic material tokens。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 diagnostics 误用 legacy composite value 时抛出。
    """

    projection = _projection_with_source_facts(
        _source_fact("fee_schedule.management_fee", "return_attribution.v1", "1.20%"),
        _source_fact("fee_schedule.custody_fee", "return_attribution.v1", "0.20%"),
    )
    fact = _source_fact_entry(projection, "fee_schedule.management_fee")
    projection = _replace_fact_value(
        projection,
        fact,
        {"management_fee": "1.20%", "custody_fee": "0.20%"},
    )
    fact = _source_fact_entry(projection, "fee_schedule.management_fee")
    references = (_reference(fact.evidence_anchor_ids[0], "同源摘录只包含托管费 0.20%。"),)
    result = confirm_projection_evidence_v2(projection, references)

    summary = summarize_value_match_diagnostics(
        projection=projection,
        references=references,
        result=result,
    )

    record = next(item for item in summary.records if item.fact_id == fact.fact_id)
    assert fact.source_fact_ids == ("fee_schedule.management_fee",)
    assert record.token_count == 1
    assert record.unmatched_token_category_counts == {"numeric_percent": 1}


def test_dual_bridge_identity_returns_unresolved_e3_blocking() -> None:
    """验证同时携带 atomic id 和 derived view id 的 fact fail closed。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 ambiguous bridge 被静默解析为任意来源时抛出。
    """

    projection = _projection_with_source_facts(
        _source_fact("fee_schedule.management_fee", "return_attribution.v1", "1.20%"),
        _source_fact("fee_schedule.custody_fee", "return_attribution.v1", "0.20%"),
    )
    original_fact = _source_fact_entry(projection, "fee_schedule.management_fee")
    ambiguous_fact = replace(original_fact, derived_view_id="fee_schedule")
    projection = _replace_fact_entry(projection, ambiguous_fact)
    references = (_reference(ambiguous_fact.evidence_anchor_ids[0], "年报披露管理费为 1.20%。"),)

    result = confirm_projection_evidence_v2(projection, references)
    summary = summarize_value_match_diagnostics(
        projection=projection,
        references=references,
        result=result,
    )

    fact_result = _fact_result(result, ambiguous_fact)
    record = next(item for item in summary.records if item.fact_id == ambiguous_fact.fact_id)
    assert fact_result.status == "fail"
    assert _dimension_status(fact_result, "value_match") == "fail"
    assert record.token_count == 0
    assert record.unmatched_token_category_counts == {}
    assert _has_blocking_issue(result, ambiguous_fact, "bridge fact 无法解析 material value")


def test_duplicate_derived_view_id_returns_e3_blocking() -> None:
    """验证重复 derived view target 不会被任意选取。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 duplicate view_id 被静默解析为第一个 view 时抛出。
    """

    projection = _projection_with_source_facts(
        _source_fact("fee_schedule.management_fee", "return_attribution.v1", "1.20%"),
        _source_fact("fee_schedule.custody_fee", "return_attribution.v1", "0.20%"),
    )
    derived_fact = _derived_fact(projection, "fee_schedule")
    duplicate_view = replace(projection.derived_views[0], value={"management_fee": "9.99%"})
    projection = replace(projection, derived_views=projection.derived_views + (duplicate_view,))

    result = confirm_projection_evidence_v2(projection, ())

    fact_result = _fact_result(result, derived_fact)
    assert fact_result.status == "fail"
    assert _dimension_status(fact_result, "missing_evidence") == "fail"
    assert _has_blocking_issue(result, derived_fact, "derived_view_id 未在 projection.derived_views 中解析")


def test_valid_single_atomic_bridge_still_passes_value_match() -> None:
    """验证唯一 atomic bridge 继续按 atomic 单值确认。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当合法单一 atomic bridge 被误判为未解析时抛出。
    """

    projection = _projection_with_source_facts(
        _source_fact("fee_schedule.management_fee", "return_attribution.v1", "1.20%"),
        _source_fact("fee_schedule.custody_fee", "return_attribution.v1", "0.20%"),
    )
    fact = _source_fact_entry(projection, "fee_schedule.management_fee")

    result = confirm_projection_evidence_v2(
        projection,
        (_reference(fact.evidence_anchor_ids[0], "年报披露管理费为 1.20%。"),),
    )

    fact_result = _fact_result(result, fact)
    assert fact.source_fact_ids == ("fee_schedule.management_fee",)
    assert fact.derived_view_id is None
    assert _dimension_status(fact_result, "value_match") == "pass"


def test_derived_fee_schedule_missing_child_provenance_fails_safely() -> None:
    """验证 derived view 依赖 child fact provenance，缺 child provenance 时失败。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 derived view 静默 not_applicable/pass 时抛出。
    """

    projection = _projection_with_source_facts(
        _source_fact("fee_schedule.management_fee", "return_attribution.v1", "1.20%"),
        _source_fact(
            "fee_schedule.custody_fee",
            "return_attribution.v1",
            "0.20%",
            anchors=(_anchor_without_section("fee_schedule.custody_fee"),),
        ),
    )
    derived_fact = _derived_fact(projection, "fee_schedule")

    result = confirm_projection_evidence_v2(projection, ())

    fact_result = _fact_result(result, derived_fact)
    assert fact_result.status == "fail"
    assert _dimension_status(fact_result, "missing_evidence") == "fail"
    assert any("section-or-better provenance" in issue.message for issue in result.issues)


def test_missing_child_anchor_is_not_fabricated_from_composite_or_locator() -> None:
    """验证缺 child anchor 不从 composite dict 或 row locator 伪造 provenance。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当缺锚点 atomic fact 被误确认时抛出。
    """

    projection = _projection_with_source_facts(
        _source_fact("fee_schedule.management_fee", "return_attribution.v1", "1.20%", anchors=()),
    )
    fact = _source_fact_entry(projection, "fee_schedule.management_fee")
    projection = _replace_fact_value(
        projection,
        fact,
        {"management_fee": "1.20%", "custody_fee": "0.20%"},
    )
    fact = _source_fact_entry(projection, "fee_schedule.management_fee")

    result = confirm_projection_evidence_v2(projection, ())

    fact_result = _fact_result(result, fact)
    assert fact_result.status == "fail"
    assert fact_result.matched_anchor_ids == ()
    assert _dimension_status(fact_result, "missing_evidence") == "fail"


def test_legacy_no_bridge_keeps_existing_composite_value_behavior() -> None:
    """验证无 bridge id 的 legacy fact 继续使用 `fact.value` 展开行为。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 legacy no-bridge 行为被 atomic resolver 改写时抛出。
    """

    projection = project_chapter_facts(_bundle(), chapter_ids=(2,))
    fact = next(
        item
        for item in projection.chapters[0].facts
        if item.source_field_id == "structured.fee_schedule"
    )

    result = confirm_projection_evidence_v2(
        projection,
        (_reference(fact.evidence_anchor_ids[0], "年报披露托管费为 0.20%。"),),
    )

    fact_result = _fact_result(result, fact)
    assert fact.source_fact_ids == ()
    assert fact.derived_view_id is None
    assert _dimension_status(fact_result, "value_match") == "pass"


def test_no_atomic_facts_available_preserves_legacy_summary_status() -> None:
    """验证没有 atomic facts 时现有 Evidence Confirm summary 不被迁移改变。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 no-bridge projection 聚合状态变化时抛出。
    """

    projection = project_chapter_facts(_bundle(), chapter_ids=(2,))
    fact = next(
        item
        for item in projection.chapters[0].facts
        if item.source_field_id == "structured.fee_schedule"
    )

    result = confirm_projection_evidence_v2(
        projection,
        (_reference(fact.evidence_anchor_ids[0], "年报披露管理费为 1.20%，托管费为 0.20%。"),),
    )

    assert projection.source_facts.facts == {}
    assert projection.derived_views == ()
    fact_result = _fact_result(result, fact)
    assert _dimension_status(fact_result, "value_match") == "pass"
    assert fact_result.status == "warn"


def _projection_with_source_facts(*facts: AtomicSourceFact) -> ChapterFactProjection:
    """构造带 atomic store 的第 2 章 projection。

    Args:
        facts: atomic source facts。

    Returns:
        第 2 章章节事实投影。

    Raises:
        ValueError: 当 atomic store 发现重复 fact id 时抛出。
    """

    return project_chapter_facts(
        replace(_bundle(), source_facts=AtomicSourceFactStore(facts)),
        chapter_ids=(2,),
    )


def _source_fact(
    fact_id: str,
    family_id: str,
    value: object | None,
    *,
    anchors: tuple[EvidenceAnchor, ...] | None = None,
) -> AtomicSourceFact:
    """构造 accepted atomic source fact。

    Args:
        fact_id: 稳定 atomic source fact ID。
        family_id: 所属字段族 ID。
        value: atomic fact 单值。
        anchors: 显式锚点；未传入时使用 section-level annual_report 锚点。

    Returns:
        测试用 atomic source fact。

    Raises:
        ValueError: 当 atomic source fact 契约非法时抛出。
    """

    return AtomicSourceFact(
        fact_id=fact_id,
        family_id=family_id,
        value=value,
        status="accepted",
        extraction_mode="direct",
        anchors=(_atomic_anchor(fact_id),) if anchors is None else anchors,
        provenance=None,
        gaps=(),
        source_field_path=fact_id,
    )


def _atomic_anchor(fact_id: str) -> EvidenceAnchor:
    """构造 atomic source fact 锚点。

    Args:
        fact_id: 稳定 atomic source fact ID。

    Returns:
        section-level annual_report 锚点。

    Raises:
        无显式抛出。
    """

    return replace(_anchor(f"source_field_path={fact_id}; locator=fixture"), note=f"field={fact_id}")


def _anchor_without_section(fact_id: str) -> EvidenceAnchor:
    """构造缺 section provenance 的 annual_report 锚点。

    Args:
        fact_id: 稳定 atomic source fact ID。

    Returns:
        缺 section_id 的锚点。

    Raises:
        无显式抛出。
    """

    return replace(_atomic_anchor(fact_id), section_id=None)


def _source_fact_entry(
    projection: ChapterFactProjection,
    source_fact_id: str,
) -> ChapterFactEntry:
    """按 source fact id 读取章节事实。

    Args:
        projection: 章节事实投影。
        source_fact_id: atomic source fact ID。

    Returns:
        匹配的章节事实。

    Raises:
        AssertionError: 当 fact 不存在时抛出。
    """

    for chapter in projection.chapters:
        for fact in chapter.facts:
            if fact.source_fact_ids == (source_fact_id,):
                return fact
    raise AssertionError(f"missing source fact entry: {source_fact_id}")


def _derived_fact(projection: ChapterFactProjection, view_id: str) -> ChapterFactEntry:
    """按 derived view id 读取章节事实。

    Args:
        projection: 章节事实投影。
        view_id: derived view ID。

    Returns:
        匹配的章节事实。

    Raises:
        AssertionError: 当 fact 不存在时抛出。
    """

    for chapter in projection.chapters:
        for fact in chapter.facts:
            if fact.derived_view_id == view_id:
                return fact
    raise AssertionError(f"missing derived view fact: {view_id}")


def _replace_fact_value(
    projection: ChapterFactProjection,
    target: ChapterFactEntry,
    value: object,
) -> ChapterFactProjection:
    """替换指定章节 fact 的 legacy value。

    Args:
        projection: 原章节事实投影。
        target: 需要替换的 fact。
        value: 替换后的 legacy value。

    Returns:
        新 projection。

    Raises:
        无显式抛出。
    """

    updated_chapters = tuple(
        replace(
            chapter,
            facts=tuple(
                replace(fact, value=value) if fact.fact_id == target.fact_id else fact
                for fact in chapter.facts
            ),
        )
        for chapter in projection.chapters
    )
    return replace(projection, chapters=updated_chapters)


def _replace_fact_entry(
    projection: ChapterFactProjection,
    replacement: ChapterFactEntry,
) -> ChapterFactProjection:
    """替换指定章节 fact 条目。

    Args:
        projection: 原章节事实投影。
        replacement: 替换后的 fact 条目。

    Returns:
        新 projection。

    Raises:
        无显式抛出。
    """

    updated_chapters = tuple(
        replace(
            chapter,
            facts=tuple(
                replacement if fact.fact_id == replacement.fact_id else fact
                for fact in chapter.facts
            ),
        )
        for chapter in projection.chapters
    )
    return replace(projection, chapters=updated_chapters)


def _reference(anchor_id: str, excerpt_text: str) -> EvidenceConfirmReference:
    """构造 proven annual_report reference。

    Args:
        anchor_id: 章节 anchor id。
        excerpt_text: 同源摘录。

    Returns:
        Evidence Confirm reference。

    Raises:
        无显式抛出。
    """

    return EvidenceConfirmReference(
        anchor_id=anchor_id,
        reference_kind="annual_report_excerpt",
        source_kind="annual_report",
        document_year=2024,
        section_id="§2",
        page_number=12,
        table_id=None,
        row_locator=None,
        excerpt_text=excerpt_text,
        source_truth_status="proven",
        candidate_only=False,
    )


def _fact_result(result: object, fact: ChapterFactEntry) -> object:
    """从 V2 result 中读取指定 fact result。

    Args:
        result: Evidence Confirm V2 result。
        fact: 章节事实。

    Returns:
        匹配的 fact result。

    Raises:
        AssertionError: 当结果不存在时抛出。
    """

    for item in result.fact_results:  # type: ignore[attr-defined]
        if item.fact_id == fact.fact_id:
            return item
    raise AssertionError(f"missing fact result: {fact.fact_id}")


def _dimension_status(fact_result: object, dimension_name: str) -> str:
    """读取指定维度状态。

    Args:
        fact_result: V2 fact result。
        dimension_name: 维度名称。

    Returns:
        维度状态。

    Raises:
        StopIteration: 当维度不存在时抛出。
    """

    return next(
        dimension.status
        for dimension in fact_result.dimension_results  # type: ignore[attr-defined]
        if dimension.dimension == dimension_name
    )


def _has_blocking_issue(result: object, fact: ChapterFactEntry, message_fragment: str) -> bool:
    """判断 V2 result 是否包含指定 fact 的 blocking issue。

    Args:
        result: Evidence Confirm V2 result。
        fact: 章节事实。
        message_fragment: 需要匹配的 issue message 片段。

    Returns:
        存在匹配 issue 时返回 ``True``。

    Raises:
        无显式抛出。
    """

    return any(
        issue.fact_id == fact.fact_id
        and issue.severity == "blocking"
        and message_fragment in issue.message
        for issue in result.issues  # type: ignore[attr-defined]
    )
