"""报告写作 dev-only 审计测试。"""

from __future__ import annotations

from fund_agent.fund.report_evidence import (
    REPORT_EVIDENCE_SCHEMA_VERSION,
    ReportDataGap,
    ReportEvidenceAnchor,
    ReportEvidenceBundle,
    ReportFact,
    ReportPreferredLensProjection,
    ReportQualityContext,
)
from fund_agent.fund.report_writing_audit import (
    ChapterDraftSurrogate,
    audit_report_writing_bundle,
    audit_report_writing_records,
    bundle_to_record,
    issue_records,
)
from fund_agent.fund.template.chapter_contract_constraints import (
    ACTIVE_CHAPTER_3_TURNOVER_REQUIREMENT_ID,
)


def test_active_chapter_3_turnover_missing_blocks_stability_claim() -> None:
    """验证缺少换手率/风格变化证据时禁止稳定性正向 claim。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 审计未产出 material issue 时抛出。
    """

    result = audit_report_writing_bundle(
        _bundle(),
        chapter_drafts=(
            ChapterDraftSurrogate(
                chapter_id=3,
                fund_type_slot="active_fund",
                markdown="基金经理风格稳定，言行一致。",
            ),
        ),
    )

    categories = {issue.failure_category for issue in result.issues}
    assert "unsupported_stability_claim" in categories
    assert "required_evidence_missing" in categories
    assert result.summary.material_count == 2
    assert result.summary.blocking_count == 0


def test_active_chapter_3_explicit_data_gap_allows_insufficient_evidence_wording() -> None:
    """验证兼容 data_gap 与证据不足措辞可放行稳定性相关写法。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 合规降级措辞被错误报错时抛出。
    """

    gap = _turnover_gap()
    result = audit_report_writing_bundle(
        _bundle(data_gaps=(gap,)),
        chapter_drafts=(
            ChapterDraftSurrogate(
                chapter_id=3,
                fund_type_slot="active_fund",
                markdown=(
                    "当前证据不足，不能据此判断风格稳定、风格一致或言行一致；"
                    "下一步最小验证问题：复核年报§8换手率及跨期行业配置变化后，"
                    "风格稳定性判断是否仍成立？"
                ),
                gap_refs=(gap.gap_id,),
            ),
        ),
    )

    assert result.summary.blocking_count == 0
    assert result.summary.material_count == 0
    assert result.issues == ()


def test_must_not_cover_hit_emits_issue() -> None:
    """验证 must_not_cover / 交易建议禁区会产出 forbidden_content。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: forbidden_content issue 缺失时抛出。
    """

    result = audit_report_writing_bundle(
        _bundle(facts=(_turnover_fact(),)),
        chapter_drafts=(
            ChapterDraftSurrogate(
                chapter_id=7,
                fund_type_slot="active_fund",
                markdown="建议买入 30% 仓位，并在短期回调时加仓。",
            ),
        ),
    )

    assert any(issue.failure_category == "forbidden_content" for issue in result.issues)
    assert any(issue.severity == "blocking" for issue in result.issues)
    assert result.summary.blocking_count >= 1


def test_required_evidence_missing_emits_gap() -> None:
    """验证主动基金第 3 章没有证据也没有 data_gap 时产出 required gap。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: required_evidence_missing issue 缺失时抛出。
    """

    result = audit_report_writing_bundle(
        _bundle(),
        chapter_drafts=(
            ChapterDraftSurrogate(
                chapter_id=3,
                fund_type_slot="active_fund",
                markdown="本章只描述基金经理任职背景，不判断风格稳定性。",
            ),
        ),
    )

    assert result.summary.material_count == 1
    issue = result.issues[0]
    assert issue.failure_category == "required_evidence_missing"
    assert issue.requirement_id == ACTIVE_CHAPTER_3_TURNOVER_REQUIREMENT_ID
    assert issue.evidence_requirement_gaps == (ACTIVE_CHAPTER_3_TURNOVER_REQUIREMENT_ID,)


def test_valid_minimal_active_chapter_3_case() -> None:
    """验证已复核换手率事实支撑下的最小有效第 3 章。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 有效事实被错误报错时抛出。
    """

    result = audit_report_writing_bundle(
        _bundle(facts=(_turnover_fact(),)),
        chapter_drafts=(
            ChapterDraftSurrogate(
                chapter_id=3,
                fund_type_slot="active_fund",
                markdown="年报已复核换手率，本文仅做谨慎描述。",
                anchor_refs=("anchor:turnover",),
            ),
        ),
    )

    assert result.issues == ()
    assert result.summary.issue_count == 0


def test_explicit_claim_tags_take_precedence_over_phrase_matching() -> None:
    """验证显式 claim_tags 优先触发稳定性 claim 检测。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 显式 claim tag 未触发 unsupported_stability_claim 时抛出。
    """

    result = audit_report_writing_bundle(
        _bundle(),
        chapter_drafts=(
            ChapterDraftSurrogate(
                chapter_id=3,
                fund_type_slot="active_fund",
                markdown="基金经理框架延续。",
                claim_tags=("style_consistency_positive",),
            ),
        ),
    )

    assert any(issue.failure_category == "unsupported_stability_claim" for issue in result.issues)


def test_bundle_fund_type_slot_none_defaults_unless_draft_supplies_fund_type() -> None:
    """验证 bundle fund_type_slot=None 时默认不触发 active 约束，草稿显式类型例外。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: default / 显式 active 解析不符合计划时抛出。
    """

    default_result = audit_report_writing_bundle(
        _bundle(fund_type_slot=None),
        chapter_drafts=(
            ChapterDraftSurrogate(
                chapter_id=3,
                fund_type_slot="unknown",
                markdown="基金经理风格稳定。",
            ),
        ),
    )
    explicit_result = audit_report_writing_bundle(
        _bundle(fund_type_slot=None),
        chapter_drafts=(
            ChapterDraftSurrogate(
                chapter_id=3,
                fund_type_slot="active_fund",
                markdown="基金经理风格稳定。",
            ),
        ),
    )

    assert default_result.issues == ()
    assert any(issue.failure_category == "unsupported_stability_claim" for issue in explicit_result.issues)


def test_records_helper_consumes_caller_supplied_parsed_records() -> None:
    """验证 records helper 只消费调用方已解析 bundle-like records。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: records helper 输出不稳定时抛出。
    """

    bundle = _bundle(facts=(_turnover_fact(),))
    result = audit_report_writing_records(
        (bundle_to_record(bundle),),
        chapter_drafts=(
            ChapterDraftSurrogate(
                chapter_id=3,
                fund_type_slot="active_fund",
                markdown="年报已复核换手率，本文仅做谨慎描述。",
            ),
        ),
    )

    assert result.issues == ()
    assert issue_records(result) == ()


def test_active_chapter_3_data_gap_missing_wording_emits_issue() -> None:
    """验证兼容 data_gap 缺少必要降级措辞时产出措辞 issue。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: insufficient_evidence_wording_missing 缺失时抛出。
    """

    result = audit_report_writing_bundle(
        _bundle(data_gaps=(_turnover_gap(),)),
        chapter_drafts=(
            ChapterDraftSurrogate(
                chapter_id=3,
                fund_type_slot="active_fund",
                markdown="本章只描述基金经理任职背景，不判断风格稳定性。",
            ),
        ),
    )

    assert any(
        issue.failure_category == "insufficient_evidence_wording_missing"
        for issue in result.issues
    )


def test_active_chapter_3_data_gap_with_positive_claim_emits_unsupported_issue() -> None:
    """验证仅有 data_gap 时仍禁止正向稳定性判断。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: unsupported_stability_claim 缺失时抛出。
    """

    result = audit_report_writing_bundle(
        _bundle(data_gaps=(_turnover_gap(),)),
        chapter_drafts=(
            ChapterDraftSurrogate(
                chapter_id=3,
                fund_type_slot="active_fund",
                markdown="基金经理风格稳定，言行一致。",
            ),
        ),
    )

    categories = {issue.failure_category for issue in result.issues}
    assert "insufficient_evidence_wording_missing" in categories
    assert "unsupported_stability_claim" in categories


def test_fact_with_dangling_anchor_does_not_satisfy_requirement() -> None:
    """验证 dangling anchor id 不能满足 required_evidence。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: dangling anchor 被错误放行时抛出。
    """

    fact = _turnover_fact(source_anchor_ids=("anchor:missing",))
    result = audit_report_writing_bundle(
        _bundle(facts=(fact,)),
        chapter_drafts=(
            ChapterDraftSurrogate(
                chapter_id=3,
                fund_type_slot="active_fund",
                markdown="年报已复核换手率，本文仅做谨慎描述。",
            ),
        ),
    )

    assert any(issue.failure_category == "required_evidence_missing" for issue in result.issues)


def test_fact_with_mixed_valid_and_dangling_anchors_does_not_satisfy_requirement() -> None:
    """验证混合有效与 dangling anchor id 不能满足 required_evidence。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 混合 anchor 被错误放行时抛出。
    """

    fact = _turnover_fact(source_anchor_ids=("anchor:turnover", "anchor:missing"))
    result = audit_report_writing_bundle(
        _bundle(facts=(fact,)),
        chapter_drafts=(
            ChapterDraftSurrogate(
                chapter_id=3,
                fund_type_slot="active_fund",
                markdown="年报已复核换手率，本文仅做谨慎描述。",
            ),
        ),
    )

    assert any(issue.failure_category == "required_evidence_missing" for issue in result.issues)


def test_malformed_records_report_year_fails_closed() -> None:
    """验证 malformed records report_year 不抛异常而是 fail-closed。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: records helper 未返回 blocking issue 时抛出。
    """

    result = audit_report_writing_records(
        (
            {
                "record_type": "bundle",
                "bundle_id": "bundle:test",
                "report_year": "bad",
            },
        ),
    )

    assert result.failed_closed is True
    assert result.summary.blocking_count == 1
    assert result.issues[0].failure_category == "invalid_audit_input"


def test_conflicting_explicit_chapter_3_fund_type_slots_fail_closed() -> None:
    """验证同一章节多个显式 fund_type_slot 冲突会 fail-closed。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: fund_type_slot 冲突被错误放行时抛出。
    """

    result = audit_report_writing_bundle(
        _bundle(fund_type_slot=None),
        chapter_drafts=(
            ChapterDraftSurrogate(
                chapter_id=3,
                fund_type_slot="index_fund",
                markdown="",
            ),
            ChapterDraftSurrogate(
                chapter_id=3,
                fund_type_slot="active_fund",
                markdown="基金经理风格稳定，言行一致。",
            ),
        ),
    )

    assert result.failed_closed is True
    assert result.summary.blocking_count == 1
    assert result.issues[0].failure_category == "input_conflict"


def test_records_data_gap_missing_reason_or_field_path_fails_closed() -> None:
    """验证 records data_gap 缺少显式兼容字段不能满足 requirement。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 不完整 data_gap 被错误当作兼容 gap 时抛出。
    """

    for gap_record in (
        {
            "gap_id": "gap:missing_reason",
            "chapter_ids": ("chapter_3",),
            "field_path": "manager.turnover_rate",
            "required_report_wording": _turnover_gap().required_report_wording,
        },
        {
            "gap_id": "gap:missing_field_path",
            "chapter_ids": ("chapter_3",),
            "reason_code": "not_reviewed_in_current_slice",
            "required_report_wording": _turnover_gap().required_report_wording,
        },
    ):
        result = audit_report_writing_records(
            (
                {
                    "record_type": "bundle",
                    "bundle_id": "bundle:test",
                    "report_year": 2024,
                    "fund_type_slot": "active_fund",
                    "data_gaps": (gap_record,),
                },
            ),
            chapter_drafts=(
                ChapterDraftSurrogate(
                    chapter_id=3,
                    fund_type_slot="active_fund",
                    markdown="本章只描述基金经理任职背景，不判断风格稳定性。",
                ),
            ),
        )
        assert result.failed_closed is True
        assert result.summary.blocking_count == 1
        assert result.issues[0].failure_category == "invalid_audit_input"


def _bundle(
    *,
    fund_type_slot: str | None = "active_fund",
    facts: tuple[ReportFact, ...] = (),
    data_gaps: tuple[ReportDataGap, ...] = (),
) -> ReportEvidenceBundle:
    """构造最小报告证据包。

    Args:
        fund_type_slot: 基金类型 slot；`None` 用于验证 default fallback。
        facts: 报告事实。
        data_gaps: 数据缺口。

    Returns:
        测试用 `ReportEvidenceBundle`。

    Raises:
        无显式抛出。
    """

    return ReportEvidenceBundle(
        bundle_id="bundle:004393:2024",
        schema_version=REPORT_EVIDENCE_SCHEMA_VERSION,
        corpus_id="ad_hoc",
        fund_code="004393",
        report_year=2024,
        classified_fund_type="active_fund",
        fund_type_slot=fund_type_slot,  # type: ignore[arg-type]
        type_slot_membership_status="matches_slot",
        preferred_lens=ReportPreferredLensProjection(fund_type="active_fund", chapters=()),
        quality_context=ReportQualityContext(),
        review_status="fact_prefill_reviewed",
        facts=facts,
        evidence_anchors=(
            ReportEvidenceAnchor(
                anchor_id="anchor:turnover",
                source_kind="annual_report",
                source_strength="fund_disclosure",
                document_id="doc:004393:2024:annual_report",
                document_year=2024,
                section_id="§8",
            ),
        ),
        data_gaps=data_gaps,
    )


def _turnover_fact(
    *,
    source_anchor_ids: tuple[str, ...] = ("anchor:turnover",),
) -> ReportFact:
    """构造已复核换手率事实。

    Args:
        无。

    Args:
        source_anchor_ids: 事实引用的证据锚点 id。

    Returns:
        可满足 active Chapter 3 约束的 `ReportFact`。

    Raises:
        无显式抛出。
    """

    return ReportFact(
        fact_id="fact:manager.turnover_rate",
        category="manager",
        field_path="turnover_rate",
        value={"turnover_rate": "88.00%"},
        unit="percent",
        source_boundary="repository_derived",
        extraction_mode="direct",
        review_status="reviewed",
        source_anchor_ids=source_anchor_ids,
        source_document_ids=("doc:004393:2024:annual_report",),
    )


def _turnover_gap() -> ReportDataGap:
    """构造兼容 active Chapter 3 的换手率 data_gap。

    Args:
        无。

    Returns:
        可降级满足 active Chapter 3 约束的 `ReportDataGap`。

    Raises:
        无显式抛出。
    """

    return ReportDataGap(
        gap_id="gap:004393:2024:not_reviewed:manager.turnover_rate:not_reviewed_in_current_slice",
        gap_kind="not_reviewed",
        field_path="manager.turnover_rate",
        chapter_ids=("chapter_3",),
        failure_category="not_reviewed_in_current_slice",
        reason_code="not_reviewed_in_current_slice",
        fallback_allowed=False,
        fallback_used=False,
        required_report_wording=(
            "当前证据不足，不能据此判断风格稳定、风格一致或言行一致；"
            "下一步最小验证问题：复核年报§8换手率及跨期行业配置/持仓集中度变化后，"
            "风格稳定性和言行一致性判断是否仍成立？"
        ),
    )
