"""ReportEvidenceBundle typed model / projection 测试。"""

from __future__ import annotations

from dataclasses import replace
from decimal import Decimal

import pytest

from fund_agent.fund.data.nav_data import NavDataResult
from fund_agent.fund.data_extractor import StructuredFundDataBundle
from fund_agent.fund.extractors import EvidenceAnchor, ExtractedField, IndexProfileValue, TrackingErrorValue
from fund_agent.fund.report_evidence import (
    ReportDataGapOverride,
    ReportEvidenceProjectionContext,
    ReportPreferredLensChapter,
    ReportScoreIssueLink,
    build_gap_id,
    build_score_issue_id,
    project_report_evidence_bundle,
)


def test_projects_current_extracted_field_groups_to_report_facts() -> None:
    """验证当前 ExtractedField 组会投影为报告事实。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 投影结果不符合字段契约时抛出。
    """

    result = project_report_evidence_bundle(_build_bundle(), _reviewed_context())

    fact_paths = {fact.field_path for fact in result.facts}
    assert {
        "basic_identity",
        "classified_fund_type",
        "product_profile",
        "benchmark",
        "index_profile",
        "fee_schedule",
        "turnover_rate",
        "nav_benchmark_performance",
        "investor_return",
        "tracking_error",
        "share_change",
        "manager_alignment",
        "manager_strategy_text",
        "portfolio_managers",
        "holdings_snapshot",
        "risk_characteristic_text",
        "holder_structure",
    } <= fact_paths
    classified_fact = _fact(result, "classified_fund_type")
    assert classified_fact.fact_id == "fact:fund_type.classified_fund_type"
    assert classified_fact.value == "active_fund"
    assert "nav_data" not in fact_paths


def test_preferred_lens_projection_is_serializable_and_covers_8_chapters() -> None:
    """验证 preferred_lens 投影覆盖模板第 0-7 章且不泄漏运行时对象。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: lens 投影不符合契约时抛出。
    """

    result = project_report_evidence_bundle(_build_bundle(), _reviewed_context())

    assert tuple(chapter.chapter_id for chapter in result.preferred_lens.chapters) == tuple(
        f"chapter_{index}" for index in range(8)
    )
    assert all(isinstance(chapter, ReportPreferredLensChapter) for chapter in result.preferred_lens.chapters)
    assert all(isinstance(chapter.source_statements, tuple) for chapter in result.preferred_lens.chapters)


def test_missing_classified_fund_type_derives_unknown_and_gap() -> None:
    """验证缺少基金类型时进入 unknown、单一缺口和双向引用。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 分类缺口不符合预期时抛出。
    """

    bundle = _build_bundle(classified_fund_type=None)
    result = project_report_evidence_bundle(bundle, _reviewed_context())

    assert result.classified_fund_type == "unknown"
    classified_fact = _fact(result, "classified_fund_type")
    missing_gaps = [
        gap
        for gap in result.data_gaps
        if gap.reason_code == "classified_fund_type_missing"
        and gap.gap_kind == "missing_fact"
        and gap.field_path == "classified_fund_type"
    ]
    assert len(missing_gaps) == 1
    assert missing_gaps[0].related_fact_id == "fact:fund_type.classified_fund_type"
    assert missing_gaps[0].gap_id in classified_fact.data_gap_refs
    assert result.review_status != "scoring_ready"


def test_illegal_classified_fund_type_blocks_scoring_ready() -> None:
    """验证非法基金类型阻断 scoring_ready。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 非法类型未被识别时抛出。
    """

    bundle = _build_bundle(classified_fund_type="money_market")
    result = project_report_evidence_bundle(bundle, _reviewed_context())

    assert result.classified_fund_type == "unknown"
    assert any(
        gap.gap_kind == "type_slot_gap" and gap.reason_code == "classified_fund_type_invalid"
        for gap in result.data_gaps
    )
    assert result.review_status != "scoring_ready"


@pytest.mark.parametrize(
    ("classified_fund_type", "fund_type_slot", "expected"),
    (
        ("active_fund", "active_fund", "matches_slot"),
        ("active_fund", "index_fund", "type_gap"),
        ("qdii_fund", "fof_fund", "taxonomy_pending"),
    ),
)
def test_type_slot_membership_status_distinguishes_matches_type_gap_taxonomy_pending(
    classified_fund_type: str,
    fund_type_slot: str,
    expected: str,
) -> None:
    """验证类型 slot 状态区分匹配、类型缺口与 taxonomy_pending。

    Args:
        classified_fund_type: fake 分类。
        fund_type_slot: 目标 slot。
        expected: 期望状态。

    Returns:
        无返回值。

    Raises:
        AssertionError: 状态派生错误时抛出。
    """

    result = project_report_evidence_bundle(
        _build_bundle(classified_fund_type=classified_fund_type),
        _reviewed_context(fund_type_slot=fund_type_slot),
    )

    assert result.type_slot_membership_status == expected


def test_multi_anchor_field_preserves_all_source_anchor_ids() -> None:
    """验证多锚点字段不会丢弃次级锚点。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 锚点未完整保留时抛出。
    """

    field = _field({"strategy_summary": "精选个股"}, "manager_strategy_text", anchor_count=2)
    bundle = replace(_build_bundle(), manager_strategy_text=field)

    result = project_report_evidence_bundle(bundle, _reviewed_context())

    fact = _fact(result, "manager_strategy_text")
    assert len(fact.source_anchor_ids) == 2
    assert set(fact.source_anchor_ids) <= {anchor.anchor_id for anchor in result.evidence_anchors}


def test_anchor_id_hash_is_stable_for_same_locator() -> None:
    """验证相同 locator 与空白归一化得到稳定锚点 id。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 锚点 id 不稳定时抛出。
    """

    first = _anchor(row_locator=" fund_name ", note="基金名称： 测试基金")
    second = _anchor(row_locator="fund_name", note="基金名称： 测试基金")

    first_result = project_report_evidence_bundle(_build_bundle(identity_anchor=first), _reviewed_context())
    second_result = project_report_evidence_bundle(_build_bundle(identity_anchor=second), _reviewed_context())

    assert _fact(first_result, "basic_identity").source_anchor_ids == _fact(
        second_result, "basic_identity"
    ).source_anchor_ids


def test_anchor_id_collision_suffix_is_deterministic(monkeypatch: pytest.MonkeyPatch) -> None:
    """验证短哈希冲突时按稳定顺序添加 suffix。

    Args:
        monkeypatch: pytest monkeypatch fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: suffix 不稳定时抛出。
    """

    import fund_agent.fund.report_evidence as report_evidence

    monkeypatch.setattr(report_evidence, "_short_locator_hash", lambda _locator_json: "deadbeef")
    field = ExtractedField(
        value={"strategy_summary": "精选个股"},
        anchors=(
            _anchor(row_locator="b", note="BBBB"),
            _anchor(row_locator="a", note="AAAA"),
        ),
        extraction_mode="direct",
    )
    bundle = replace(_build_bundle(), manager_strategy_text=field)

    result = project_report_evidence_bundle(bundle, _reviewed_context())
    fact = _fact(result, "manager_strategy_text")

    assert fact.source_anchor_ids == (
        "anchor:004393:2024:annual_report:sec2:deadbeef-2",
        "anchor:004393:2024:annual_report:sec2:deadbeef",
    )
    assert any("collision suffix" in message for message in result.validation_messages)


def test_extraction_mode_missing_produces_data_gap_ref() -> None:
    """验证 missing 字段与显式换手率缺口会回填 data_gap_refs。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 缺口 id 或引用不符合契约时抛出。
    """

    override = ReportDataGapOverride(
        field_path="turnover_rate",
        gap_kind="not_reviewed",
        failure_category="not_reviewed_in_current_slice",
        reason_code="not_reviewed_in_current_slice",
        chapter_ids=("chapter_3",),
        required_report_wording=(
            "当前 slice 未复核换手率，不能据此判断风格稳定、风格一致或言行一致；"
            "下一步最小验证问题：复核年报§8换手率及跨期行业配置/持仓集中度变化后，"
            "风格稳定性和言行一致性判断是否仍成立？"
        ),
    )

    result = project_report_evidence_bundle(
        _build_bundle(turnover_rate=_field(None, "turnover_rate", extraction_mode="missing")),
        _reviewed_context(corpus_id="ad_hoc", data_gap_overrides=(override,)),
    )

    expected_gap_id = "gap:004393:2024:not_reviewed:manager.turnover_rate:not_reviewed_in_current_slice"
    gap = next(gap for gap in result.data_gaps if gap.gap_id == expected_gap_id)
    assert gap.required_report_wording == override.required_report_wording
    assert "不能据此判断风格稳定、风格一致或言行一致" in gap.required_report_wording
    assert "下一步最小验证问题：" in gap.required_report_wording
    assert expected_gap_id in _fact(result, "turnover_rate").data_gap_refs


def test_extraction_mode_missing_with_non_null_value_rejects_bundle() -> None:
    """验证 missing 模式携带非空值会构造 rejected bundle。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 矛盾状态未被拒绝时抛出。
    """

    bundle = _build_bundle(turnover_rate=_field({"turnover": "100%"}, "turnover_rate", extraction_mode="missing"))
    result = project_report_evidence_bundle(bundle, _reviewed_context())

    assert result.review_status == "rejected"
    assert any("extraction_mode=missing but value is not None" in message for message in result.validation_messages)


def test_direct_value_without_anchor_creates_traceability_gap() -> None:
    """验证有值但无锚点的直接事实产生可追溯性缺口。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 缺锚点未生成缺口时抛出。
    """

    no_anchor_field = ExtractedField(value={"investment_scope": "股票等"}, anchors=(), extraction_mode="direct")
    result = project_report_evidence_bundle(
        replace(_build_bundle(), product_profile=no_anchor_field),
        _reviewed_context(),
    )

    fact = _fact(result, "product_profile")
    assert any(gap.failure_category == "manual_review_required" for gap in result.data_gaps)
    assert fact.data_gap_refs
    assert result.review_status in {"deferred", "rejected"}


def test_nav_data_is_excluded_from_initial_fact_projection() -> None:
    """验证首个 slice 不把 nav_data 投影为事实。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: nav_data 被错误投影时抛出。
    """

    result = project_report_evidence_bundle(_build_bundle(), _reviewed_context())

    assert all(fact.field_path != "nav_data" for fact in result.facts)
    assert all(fact.category != "nav" for fact in result.facts)


def test_review_status_priority_rejected_before_deferred() -> None:
    """验证 rejected 优先级高于 deferred。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 状态优先级错误时抛出。
    """

    context = _reviewed_context(
        source_failure_category="schema_drift",
        quality_context=None,
    )

    result = project_report_evidence_bundle(_build_bundle(), context)

    assert result.review_status == "rejected"


def test_unknown_upstream_failure_category_defers_not_scoring_ready() -> None:
    """验证 unknown upstream failure category 派生 deferred。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: unknown upstream 未阻断 scoring_ready 时抛出。
    """

    result = project_report_evidence_bundle(
        _build_bundle(),
        _reviewed_context(source_failure_category="unknown_upstream_failure_category"),
    )

    assert result.review_status == "deferred"


def test_scoring_ready_requires_non_ad_hoc_reviewed_verified_matching_bundle() -> None:
    """验证满足全部条件时才得到 scoring_ready。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: scoring_ready 派生失败时抛出。
    """

    result = project_report_evidence_bundle(_build_bundle(), _reviewed_context())

    assert result.review_status == "scoring_ready"


def test_ad_hoc_bundle_cannot_be_scoring_ready() -> None:
    """验证 ad_hoc 语料不能进入 scoring_ready。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: ad_hoc 被错误提升时抛出。
    """

    result = project_report_evidence_bundle(_build_bundle(), _reviewed_context(corpus_id="ad_hoc"))

    assert result.review_status == "fact_prefill_reviewed"


def test_score_issue_links_validate_data_gap_refs() -> None:
    """验证评分 issue 的 data_gap_refs 必须引用同 bundle gap。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 缺失 gap ref 未被拒绝时抛出。
    """

    issue = _score_issue(data_gap_refs=("gap:missing",))

    result = project_report_evidence_bundle(
        _build_bundle(),
        _reviewed_context(score_issue_links=(issue,)),
    )

    assert result.review_status == "rejected"
    assert any("references missing gaps" in message for message in result.validation_messages)


def test_score_issue_pass_with_blocking_gap_is_invalid() -> None:
    """验证 pass issue 不能引用阻断性缺口。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: pass 与 blocking gap 冲突未阻断时抛出。
    """

    gap_id = build_gap_id(
        "004393",
        2024,
        "missing_fact",
        "turnover_rate",
        "missing_from_extractor",
    )
    issue = _score_issue(
        status="pass",
        field_path="turnover_rate",
        data_gap_refs=(gap_id,),
        severity=None,
    )
    result = project_report_evidence_bundle(
        _build_bundle(turnover_rate=_field(None, "turnover_rate", extraction_mode="missing")),
        _reviewed_context(score_issue_links=(issue,)),
    )

    assert result.review_status == "rejected"
    assert any("pass status conflicts" in message for message in result.validation_messages)


def test_na_and_chapter_summary_score_semantics() -> None:
    """验证 N/A 与 chapter_summary 评分语义。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 评分语义未被校验时抛出。
    """

    na_issue = _score_issue(status="N/A", severity=None, field_path="turnover_rate")
    summary_issue = _score_issue(
        issue_id="issue:summary",
        dimension="chapter_summary",
        status="pass",
        severity=None,
        field_path=None,
        contract_item_id="chapter_3_summary",
    )

    result = project_report_evidence_bundle(
        _build_bundle(),
        _reviewed_context(score_issue_links=(na_issue, summary_issue)),
    )

    assert result.review_status == "rejected"
    assert any("N/A requires" in message for message in result.validation_messages)
    assert any("chapter_summary requires skipped" in message for message in result.validation_messages)


def test_projection_does_not_call_repository_or_source_helpers() -> None:
    """静态验证投影模块不导入仓库、来源 helper 或 PDF/cache 操作入口。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 模块暴露边界违规名称时抛出。
    """

    import fund_agent.fund.report_evidence as report_evidence

    names = set(report_evidence.__dict__)
    assert "FundDocumentRepository" not in names
    assert "AnnualReportDocumentCache" not in names
    assert "AnnualReportPdfAdapter" not in names

    result = project_report_evidence_bundle(_build_bundle(), _reviewed_context())
    assert result.fund_code == "004393"


def test_accepted_baseline_cannot_be_derived_or_forced() -> None:
    """验证当前 slice 不派生或接受 accepted_baseline。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: accepted_baseline 被错误使用时抛出。
        ValueError: 强制 attempted_review_status 时的期望异常。
    """

    result = project_report_evidence_bundle(_build_bundle(), _reviewed_context())
    assert result.review_status == "scoring_ready"
    assert result.review_status != "accepted_baseline"

    with pytest.raises(ValueError, match="accepted_baseline"):
        project_report_evidence_bundle(
            _build_bundle(),
            _reviewed_context(attempted_review_status="accepted_baseline"),
        )


def _reviewed_context(
    *,
    corpus_id: str = "corpus:rqb_s0:20260525",
    source_failure_category: str = "none",
    fund_type_slot: str | None = "active_fund",
    data_gap_overrides: tuple[ReportDataGapOverride, ...] = (),
    score_issue_links: tuple[ReportScoreIssueLink, ...] = (),
    attempted_review_status: str | None = None,
    quality_context: object | None = object(),
) -> ReportEvidenceProjectionContext:
    """构造测试用投影上下文。

    Args:
        corpus_id: 语料标识。
        source_failure_category: 来源失败分类。
        fund_type_slot: 类型 slot。
        data_gap_overrides: 显式数据缺口。
        score_issue_links: 评分 issue 链接。
        attempted_review_status: 尝试强制的 review status。
        quality_context: 保留参数，用于测试调用可读性。

    Returns:
        投影上下文。

    Raises:
        无显式抛出。
    """

    del quality_context
    return ReportEvidenceProjectionContext(
        run_id="unit-run",
        corpus_id=corpus_id,
        source_boundary="repository_derived",
        source_failure_category=source_failure_category,  # type: ignore[arg-type]
        fund_type_slot=fund_type_slot,  # type: ignore[arg-type]
        fact_review_status="reviewed",
        data_gap_overrides=data_gap_overrides,
        score_issue_links=score_issue_links,
        attempted_review_status=attempted_review_status,  # type: ignore[arg-type]
    )


def _build_bundle(
    *,
    classified_fund_type: str | None = "active_fund",
    identity_anchor: EvidenceAnchor | None = None,
    turnover_rate: ExtractedField[dict[str, object]] | None = None,
) -> StructuredFundDataBundle:
    """构造测试用结构化数据包。

    Args:
        classified_fund_type: 基金类型；`None` 表示删除 key。
        identity_anchor: 基础身份锚点。
        turnover_rate: 可覆盖的换手率字段。

    Returns:
        fake 结构化数据包。

    Raises:
        无显式抛出。
    """

    identity = {
        "fund_name": "安信企业价值优选混合A",
        "fund_code": "004393",
        "fund_category": "混合型",
        "classification_basis": ("fixture basis",),
    }
    if classified_fund_type is not None:
        identity["classified_fund_type"] = classified_fund_type
    return StructuredFundDataBundle(
        fund_code="004393",
        report_year=2024,
        basic_identity=ExtractedField(
            value=identity,
            anchors=(identity_anchor or _anchor(row_locator="basic_identity"),),
            extraction_mode="direct",
        ),
        product_profile=_field({"investment_scope": "股票等"}, "product_profile"),
        benchmark=_field({"benchmark_text": "沪深300指数收益率"}, "benchmark"),
        index_profile=ExtractedField(
            value=IndexProfileValue(
                benchmark_text="沪深300指数收益率",
                benchmark_identity_status="identified",
                benchmark_index_name="沪深300指数",
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
            ),
            anchors=(_anchor(row_locator="index_profile"),),
            extraction_mode="direct",
        ),
        fee_schedule=_field({"management_fee": "1.20%", "custody_fee": "0.20%"}, "fee_schedule"),
        turnover_rate=turnover_rate or _field({"turnover_rate": "120%"}, "turnover_rate"),
        nav_benchmark_performance=_field(
            {"nav_growth_rate": "1%", "benchmark_return_rate": "0.5%"},
            "nav_benchmark_performance",
        ),
        investor_return=_field({"investor_return_rate": "0.8%"}, "investor_return"),
        tracking_error=ExtractedField(
            value=TrackingErrorValue(
                value=Decimal("0.0123"),
                value_text="1.23%",
                unit="ratio",
                period_label="报告期",
                period_start=None,
                period_end=None,
                annualized=True,
                source_type="direct_disclosure",
                calculation_method="disclosed",
                benchmark_identity_status="identified",
                benchmark_index_name="沪深300指数",
                benchmark_index_code="000300",
                fund_series_source=None,
                index_series_source=None,
                observation_count=None,
                frequency="annual_report_period",
                annualization_factor=None,
                input_period_complete=True,
                provenance_note="年报直接披露。",
            ),
            anchors=(_anchor(row_locator="tracking_error", section_id="§3"),),
            extraction_mode="direct",
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
        holder_structure=_field({"institutional_holder": "10%"}, "holder_structure"),
        risk_characteristic_text=_field(
            {
                "schema_version": "risk_characteristic_text.v1",
                "risk_characteristic_text": "本基金为混合型基金，风险收益特征高于债券型基金。",
            },
            "risk_characteristic_text",
        ),
        nav_data=NavDataResult(
            fund_code="004393",
            records=[{"date": "2024-12-31", "nav": "1.00"}],
            source="fixture",
            cached=True,
        ),
    )


def _field(
    value: dict[str, object] | None,
    row_locator: str,
    *,
    extraction_mode: str = "direct",
    note: str | None = None,
    anchor_count: int = 1,
) -> ExtractedField[dict[str, object]]:
    """构造测试用抽取字段。

    Args:
        value: 字段值。
        row_locator: 行级定位。
        extraction_mode: 抽取模式。
        note: 附加说明。
        anchor_count: 生成锚点数量。

    Returns:
        fake `ExtractedField`。

    Raises:
        无显式抛出。
    """

    anchors = ()
    if extraction_mode != "missing":
        anchors = tuple(
            _anchor(row_locator=f"{row_locator}_{index}" if anchor_count > 1 else row_locator)
            for index in range(anchor_count)
        )
    return ExtractedField(
        value=value,
        anchors=anchors,
        extraction_mode=extraction_mode,  # type: ignore[arg-type]
        note=note,
    )


def _anchor(
    *,
    row_locator: str,
    section_id: str = "§2",
    note: str | None = None,
) -> EvidenceAnchor:
    """构造测试用证据锚点。

    Args:
        row_locator: 行级定位。
        section_id: 年报章节。
        note: 附加说明。

    Returns:
        fake 证据锚点。

    Raises:
        无显式抛出。
    """

    return EvidenceAnchor(
        source_kind="annual_report",
        document_year=2024,
        section_id=section_id,
        page_number=3,
        table_id="page-3-table-0",
        row_locator=row_locator,
        note=note or f"{row_locator}: fixture",
    )


def _fact(result, field_path: str):
    """按 field_path 读取报告事实。

    Args:
        result: 报告证据包。
        field_path: 字段路径。

    Returns:
        匹配的报告事实。

    Raises:
        StopIteration: 未找到事实时抛出。
    """

    return next(fact for fact in result.facts if fact.field_path == field_path)


def _score_issue(
    *,
    issue_id: str | None = None,
    status: str = "issue",
    severity: str | None = "material",
    dimension: str = "fact_coverage",
    field_path: str | None = "turnover_rate",
    contract_item_id: str | None = None,
    data_gap_refs: tuple[str, ...] = (),
) -> ReportScoreIssueLink:
    """构造测试用评分 issue 链接。

    Args:
        issue_id: issue id。
        status: 评分状态。
        severity: 严重程度。
        dimension: 评分维度。
        field_path: 字段路径。
        contract_item_id: 契约条目标识。
        data_gap_refs: 缺口引用。

    Returns:
        评分 issue 链接。

    Raises:
        无显式抛出。
    """

    return ReportScoreIssueLink(
        issue_id=issue_id
        or build_score_issue_id(
            "score-run",
            "004393",
            2024,
            "chapter_3",
            dimension,  # type: ignore[arg-type]
            field_path=field_path,
            contract_item_id=contract_item_id,
        ),
        score_run_id="score-run",
        chapter_id="chapter_3",
        dimension=dimension,  # type: ignore[arg-type]
        status=status,  # type: ignore[arg-type]
        severity=severity,  # type: ignore[arg-type]
        field_path=field_path,
        contract_item_id=contract_item_id,
        data_gap_refs=data_gap_refs,
        next_gate_recommendation="manual_review",
    )
