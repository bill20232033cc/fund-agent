"""P4-S2 精选基金池字段级评分测试。"""

from __future__ import annotations

import json
from pathlib import Path

from fund_agent.fund.extraction_score import (
    BOND_RISK_EVIDENCE_GROUPS,
    CORRECTNESS_MATCH,
    CORRECTNESS_MISMATCH,
    CORRECTNESS_COVERAGE_COVERED,
    CORRECTNESS_COVERAGE_FUND_NOT_COVERED,
    CORRECTNESS_COVERAGE_NO_COMPARABLE_FIELDS,
    CORRECTNESS_COVERAGE_NOT_CONFIGURED,
    CORRECTNESS_COVERAGE_PARTIALLY_COVERED,
    CORRECTNESS_COVERAGE_YEAR_NOT_COVERED,
    CORRECTNESS_STATUS_AVAILABLE,
    CORRECTNESS_STATUS_UNAVAILABLE,
    CORRECTNESS_UNAVAILABLE,
    EXCLUDED_GOLDEN_CATEGORIES,
    FIELD_PRIORITY_BY_NAME,
    MANDATORY_GOLDEN_CODE,
    MONEY_MARKET_CATEGORY,
    STATUS_FAIL,
    STATUS_PASS,
    STATUS_WATCH,
    derive_fund_quality_records,
    derive_field_applicability_decisions,
    derive_score_applicability_issues,
    load_snapshot_error_records,
    run_extraction_score,
    compare_snapshot_correctness,
    score_fund_records,
    score_snapshot_records,
    select_minimal_golden_set,
)
from fund_agent.fund.extraction_snapshot import load_selected_funds

_SCORE_JSON_TOP_LEVEL_KEYS = {
    "snapshot_path",
    "source_csv",
    "thresholds",
    "field_count",
    "fund_count",
    "status_counts",
    "p0_status",
    "field_scores",
    "fund_scores",
    "fund_quality",
    "field_applicability_decisions",
    "score_applicability_issues",
    "failed_funds",
    "golden_set",
    "correctness",
}
_PUBLIC_SOURCE_PROVENANCE_PAYLOAD = {
    "source_provenance_schema_version": "repository_source_provenance.v2",
    "source_strategy": "legacy_or_unknown",
    "selected_source": None,
    "source_mode": "legacy_or_unknown",
    "fallback_enabled": None,
    "resolved_source_name": "eastmoney",
    "fallback_used": True,
    "primary_failure_category": None,
    "fallback_eligibility": "unknown_public_metadata_absent",
    "source_provenance_status": "incomplete",
    "source_provenance_reason": "fallback_used_primary_failure_category_absent",
}
_BOND_RISK_GROUP_IDS = tuple(group.group_id for group in BOND_RISK_EVIDENCE_GROUPS)


def test_score_snapshot_records_computes_coverage_traceability_status_and_priority() -> None:
    """验证字段级评分覆盖 coverage、traceability、status 和 priority 映射。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当评分结果不符合 P4-S2 契约时抛出。
    """

    records = [
        _snapshot_record("profile", "basic_identity", value_present=True, anchor_present=True),
        _snapshot_record("profile", "basic_identity", value_present=True, anchor_present=False),
        _snapshot_record("profile", "product_profile", value_present=True, anchor_present=True),
        _snapshot_record("profile", "product_profile", value_present=False, anchor_present=True),
        _snapshot_record(
            "manager",
            "turnover_rate",
            report_year=2026,
            value_present=True,
            anchor_present=False,
        ),
        _snapshot_record(
            "manager",
            "turnover_rate",
            report_year=2026,
            value_present=False,
            anchor_present=False,
        ),
        _snapshot_record("nav", "nav_data", value_present=True, anchor_present=False),
        _snapshot_record("nav", "nav_data", value_present=False, anchor_present=False),
    ]

    rows = score_snapshot_records(records)
    rows_by_name = {row.field_name: row for row in rows}

    assert rows_by_name["basic_identity"].priority == "P0"
    assert rows_by_name["basic_identity"].records == 2
    assert rows_by_name["basic_identity"].coverage_rate == 1.0
    assert rows_by_name["basic_identity"].traceability_rate == 0.5
    assert rows_by_name["basic_identity"].status == STATUS_FAIL
    assert rows_by_name["product_profile"].priority == "P1"
    assert rows_by_name["product_profile"].coverage_rate == 0.5
    assert rows_by_name["product_profile"].traceability_rate == 1.0
    assert rows_by_name["product_profile"].status == STATUS_FAIL
    assert rows_by_name["turnover_rate"].priority == "P1"
    assert rows_by_name["nav_data"].priority == "P2"
    assert set(FIELD_PRIORITY_BY_NAME) >= {row.field_name for row in rows}


def test_score_snapshot_records_status_thresholds_are_deterministic() -> None:
    """验证 pass / watch / fail 阈值是确定性的。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当阈值状态不符合预期时抛出。
    """

    records = []
    records.extend(
        _snapshot_record("profile", "basic_identity", value_present=True, anchor_present=True)
        for _ in range(10)
    )
    records.extend(
        _snapshot_record("profile", "benchmark", value_present=index < 8, anchor_present=index < 8)
        for index in range(10)
    )
    records.extend(
        _snapshot_record(
            "profile", "fee_schedule", value_present=index < 6, anchor_present=index < 6
        )
        for index in range(10)
    )

    rows_by_name = {row.field_name: row for row in score_snapshot_records(records)}

    assert rows_by_name["basic_identity"].status == STATUS_PASS
    assert rows_by_name["benchmark"].status == STATUS_WATCH
    assert rows_by_name["fee_schedule"].status == STATUS_FAIL


def test_source_provenance_keys_do_not_change_score_outputs() -> None:
    """验证 additive provenance 字段不改变 score / FQ0-FQ6 敏感输出。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 provenance 字段影响评分语义时抛出。
    """

    legacy_records = [
        _snapshot_record("profile", "basic_identity", value_present=True, anchor_present=True),
        _snapshot_record("profile", "benchmark", value_present=False, anchor_present=False),
    ]
    provenance_records = [
        _snapshot_record(
            "profile",
            "basic_identity",
            value_present=True,
            anchor_present=True,
            include_source_provenance=True,
        ),
        _snapshot_record(
            "profile",
            "benchmark",
            value_present=False,
            anchor_present=False,
            include_source_provenance=True,
        ),
    ]

    assert score_snapshot_records(provenance_records) == score_snapshot_records(legacy_records)
    assert score_fund_records(provenance_records) == score_fund_records(legacy_records)
    assert derive_fund_quality_records(provenance_records) == derive_fund_quality_records(
        legacy_records
    )
    assert derive_field_applicability_decisions(
        provenance_records
    ) == derive_field_applicability_decisions(legacy_records)
    assert derive_score_applicability_issues(
        provenance_records
    ) == derive_score_applicability_issues(legacy_records)


def test_score_fund_records_exposes_single_fund_p0_failure_when_aggregate_can_pass() -> None:
    """验证单基金 P0 失败不会被字段级聚合均值掩盖。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当单基金 P0 状态未被识别时抛出。
    """

    records = [
        _snapshot_record(
            "profile",
            "basic_identity",
            fund_code=f"{index:06d}",
            value_present=index != 0,
            anchor_present=index != 0,
        )
        for index in range(10)
    ]

    field_row = score_snapshot_records(records)[0]
    fund_rows = score_fund_records(records)
    rows_by_code = {row.fund_code: row for row in fund_rows}

    assert field_row.status == STATUS_PASS
    assert rows_by_code["000000"].p0_status == STATUS_FAIL
    assert rows_by_code["000000"].p0_failed_fields == ("basic_identity",)
    assert rows_by_code["000001"].p0_status == STATUS_PASS


def test_derive_fund_quality_records_outputs_category_lens_and_missing_rate() -> None:
    """验证 fund_quality 输出类别匹配、模板契约适用性和缺失率。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 fund_quality 派生结果不符合契约时抛出。
    """

    records = [
        _snapshot_record("profile", "basic_identity", value_present=True, anchor_present=True),
        _snapshot_record(
            "profile", "classified_fund_type", value_present=True, anchor_present=True
        ),
        _snapshot_record("profile", "benchmark", value_present=False, anchor_present=False),
        _snapshot_record("manager", "turnover_rate", value_present=False, anchor_present=False),
    ]

    row = derive_fund_quality_records(records)[0]

    assert row.app_category_status == "match"
    assert row.preferred_lens_status == "resolved"
    assert row.preferred_lens_key == "active_fund"
    assert row.contract_template_id == "fund-analysis-template-v1"
    assert row.item_rule_template_id == "fund-analysis-template-v1"
    assert len(row.preferred_lens_chapters) == 8
    assert row.preferred_lens_unresolved_chapter_ids == ()
    assert row.missing_field_count == 1
    assert row.total_field_count == 3
    assert row.missing_field_rate == 1 / 3
    assert row.missing_p0_fields == ("benchmark",)
    assert row.missing_p1_fields == ()


def test_pre_2026_turnover_rate_is_excluded_from_p1_scoring_with_decision() -> None:
    """验证 2026 前换手率缺失不进入 P1 分母并输出适用性决策。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 2026 前换手率仍触发 P1 失败时抛出。
    """

    records = [
        _snapshot_record("profile", "basic_identity", value_present=True, anchor_present=True),
        _snapshot_record("profile", "benchmark", value_present=False, anchor_present=False),
        _snapshot_record("profile", "product_profile", value_present=False, anchor_present=False),
        _snapshot_record("manager", "turnover_rate", value_present=False, anchor_present=False),
    ]

    field_rows = {row.field_name: row for row in score_snapshot_records(records)}
    fund_row = score_fund_records(records)[0]
    quality_row = derive_fund_quality_records(records)[0]
    decisions = derive_field_applicability_decisions(records)
    issues = derive_score_applicability_issues(records)

    assert "turnover_rate" not in field_rows
    assert field_rows["product_profile"].priority == "P1"
    assert field_rows["product_profile"].status == STATUS_FAIL
    assert fund_row.p0_failed_fields == ("benchmark",)
    assert fund_row.p1_failed_fields == ("product_profile",)
    assert quality_row.missing_p0_fields == ("benchmark",)
    assert quality_row.missing_p1_fields == ("product_profile",)
    assert len(decisions) == 1
    assert decisions[0].field_name == "turnover_rate"
    assert decisions[0].applicability_status == "not_applicable_excluded"
    assert decisions[0].reason_code == "turnover_rate_pre_effective_report_year"
    assert decisions[0].denominator_effect == "excluded_no_replacement_issue"
    assert decisions[0].excluded_non_applicable_fields == ("turnover_rate",)
    assert decisions[0].replacement_issue_ids == ()
    assert issues == ()


def test_2026_turnover_rate_missing_still_fails_p1_scoring() -> None:
    """验证 2026 及以后换手率缺失仍按 P1 失败处理。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 2026 换手率缺失被错误排除时抛出。
    """

    records = [
        _snapshot_record(
            "profile",
            "basic_identity",
            report_year=2026,
            value_present=True,
            anchor_present=True,
        ),
        _snapshot_record(
            "manager",
            "turnover_rate",
            report_year=2026,
            value_present=False,
            anchor_present=False,
        ),
    ]

    field_rows = {row.field_name: row for row in score_snapshot_records(records)}
    fund_row = score_fund_records(records)[0]
    decisions = derive_field_applicability_decisions(records)

    assert field_rows["turnover_rate"].priority == "P1"
    assert field_rows["turnover_rate"].status == STATUS_FAIL
    assert fund_row.p1_failed_fields == ("turnover_rate",)
    assert decisions == ()


def test_explicit_non_annual_turnover_rate_is_excluded_even_after_2026() -> None:
    """验证显式非年报换手率记录不进入 P1 分母。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当非年报换手率记录被纳入评分时抛出。
    """

    records = [
        _snapshot_record(
            "profile",
            "basic_identity",
            report_year=2026,
            value_present=True,
            anchor_present=True,
        ),
        _snapshot_record(
            "manager",
            "turnover_rate",
            report_year=2026,
            value_present=False,
            anchor_present=False,
            extra_fields={"source_kind": "quarterly_report"},
        ),
    ]

    field_rows = {row.field_name: row for row in score_snapshot_records(records)}
    fund_row = score_fund_records(records)[0]
    decisions = derive_field_applicability_decisions(records)

    assert "turnover_rate" not in field_rows
    assert fund_row.p1_failed_fields == ()
    assert len(decisions) == 1
    assert decisions[0].field_name == "turnover_rate"
    assert decisions[0].reason_code == "turnover_rate_non_annual_report"


def test_unknown_report_year_turnover_rate_fails_closed() -> None:
    """验证年份非法的换手率记录不被静默排除。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当非法年份换手率记录被排除时抛出。
    """

    records = [
        _snapshot_record(
            "profile",
            "basic_identity",
            value_present=True,
            anchor_present=True,
            extra_fields={"report_year": "unknown"},
        ),
        _snapshot_record(
            "manager",
            "turnover_rate",
            value_present=False,
            anchor_present=False,
            extra_fields={"report_year": "unknown"},
        ),
    ]

    field_rows = {row.field_name: row for row in score_snapshot_records(records)}
    fund_row = score_fund_records(records)[0]
    decisions = derive_field_applicability_decisions(records)

    assert field_rows["turnover_rate"].priority == "P1"
    assert field_rows["turnover_rate"].status == STATUS_FAIL
    assert fund_row.p1_failed_fields == ("turnover_rate",)
    assert decisions == ()


def test_index_quality_fields_are_p1_only_for_applicable_fund_types() -> None:
    """验证指数质量字段按基金类型条件进入 P1 分母。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当非指数基金被计入或未知类型未保守计入时抛出。
    """

    records = [
        _snapshot_record(
            "profile",
            "index_profile",
            fund_code="110011",
            classified_fund_type="active_fund",
            value_present=False,
            anchor_present=False,
        ),
        _snapshot_record(
            "performance",
            "tracking_error",
            fund_code="110011",
            classified_fund_type="active_fund",
            value_present=False,
            anchor_present=False,
        ),
        _snapshot_record(
            "profile",
            "index_profile",
            fund_code="510300",
            classified_fund_type="index_fund",
            value_present=False,
            anchor_present=False,
        ),
        _snapshot_record(
            "performance",
            "tracking_error",
            fund_code="161725",
            classified_fund_type="enhanced_index",
            value_present=False,
            anchor_present=False,
        ),
        _snapshot_record(
            "profile",
            "index_profile",
            fund_code="000000",
            classified_fund_type="",
            value_present=False,
            anchor_present=False,
        ),
    ]

    rows_by_name = {row.field_name: row for row in score_snapshot_records(records)}
    fund_scores = {row.fund_code: row for row in score_fund_records(records)}
    quality_rows = {row.fund_code: row for row in derive_fund_quality_records(records)}

    assert rows_by_name["index_profile"].priority == "P1"
    assert rows_by_name["index_profile"].records == 2
    assert rows_by_name["tracking_error"].records == 1
    assert fund_scores["110011"].records == 0
    assert fund_scores["110011"].p1_failed_fields == ()
    assert fund_scores["510300"].p1_failed_fields == ("index_profile",)
    assert fund_scores["161725"].p1_failed_fields == ("tracking_error",)
    assert fund_scores["000000"].p1_failed_fields == ("index_profile",)
    assert quality_rows["110011"].total_field_count == 0
    assert quality_rows["110011"].missing_p1_fields == ()
    assert quality_rows["510300"].missing_p1_fields == ("index_profile",)
    assert quality_rows["161725"].missing_p1_fields == ("tracking_error",)
    assert quality_rows["000000"].missing_p1_fields == ("index_profile",)


def test_holdings_snapshot_requires_stock_holdings_status_for_coverage() -> None:
    """验证只有行业分布不会满足股票持仓覆盖。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 industry-only 被误计为 holdings coverage 时抛出。
    """

    records = [
        _snapshot_record(
            "holdings",
            "holdings_snapshot",
            fund_code="004393",
            value_present=True,
            anchor_present=True,
            comparable_values={
                "top_holdings_status": "missing",
                "top_holdings_source": "none",
            },
        ),
        _snapshot_record(
            "holdings",
            "holdings_snapshot",
            fund_code="110011",
            value_present=True,
            anchor_present=True,
            comparable_values={
                "top_holdings_status": "direct_all_stock_details",
                "top_holdings_source": "all_stock_investment_details",
            },
        ),
    ]

    field_row = score_snapshot_records(records)[0]
    fund_scores = {row.fund_code: row for row in score_fund_records(records)}
    quality_rows = {row.fund_code: row for row in derive_fund_quality_records(records)}

    assert field_row.field_name == "holdings_snapshot"
    assert field_row.records == 2
    assert field_row.covered_records == 1
    assert field_row.coverage_rate == 0.5
    assert fund_scores["004393"].p1_failed_fields == ("holdings_snapshot",)
    assert fund_scores["110011"].p1_failed_fields == ()
    assert quality_rows["004393"].missing_p1_fields == ("holdings_snapshot",)
    assert quality_rows["004393"].missing_field_rate == 1.0
    assert quality_rows["110011"].missing_field_rate == 0.0


def test_holdings_snapshot_coverage_requires_explicit_status_source_allowlist() -> None:
    """验证持仓覆盖必须由显式 status/source allowlist 决定。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当缺失、空白、未知或不一致 status/source 被计为覆盖时抛出。
    """

    records = [
        _snapshot_record(
            "holdings",
            "holdings_snapshot",
            fund_code="004390",
            value_present=True,
            anchor_present=True,
        ),
        _snapshot_record(
            "holdings",
            "holdings_snapshot",
            fund_code="004391",
            value_present=True,
            anchor_present=True,
            comparable_values={
                "top_holdings_status": "",
                "top_holdings_source": "",
            },
        ),
        _snapshot_record(
            "holdings",
            "holdings_snapshot",
            fund_code="004392",
            value_present=True,
            anchor_present=True,
            comparable_values={
                "top_holdings_status": "direct_unknown",
                "top_holdings_source": "unknown",
            },
        ),
        _snapshot_record(
            "holdings",
            "holdings_snapshot",
            fund_code="004393",
            value_present=True,
            anchor_present=True,
            comparable_values={
                "top_holdings_status": "direct_all_stock_details",
                "top_holdings_source": "top_ten",
            },
        ),
        _snapshot_record(
            "holdings",
            "holdings_snapshot",
            fund_code="004394",
            value_present=True,
            anchor_present=True,
            comparable_values={
                "top_holdings_status": "direct_top_ten",
                "top_holdings_source": "top_ten",
            },
        ),
        _snapshot_record(
            "holdings",
            "holdings_snapshot",
            fund_code="004395",
            value_present=True,
            anchor_present=True,
            comparable_values={
                "top_holdings_status": "direct_all_stock_details",
                "top_holdings_source": "all_stock_investment_details",
            },
        ),
    ]

    field_row = score_snapshot_records(records)[0]
    fund_scores = {row.fund_code: row for row in score_fund_records(records)}
    quality_rows = {row.fund_code: row for row in derive_fund_quality_records(records)}

    assert field_row.field_name == "holdings_snapshot"
    assert field_row.records == 6
    assert field_row.covered_records == 2
    assert fund_scores["004390"].p1_failed_fields == ("holdings_snapshot",)
    assert fund_scores["004391"].p1_failed_fields == ("holdings_snapshot",)
    assert fund_scores["004392"].p1_failed_fields == ("holdings_snapshot",)
    assert fund_scores["004393"].p1_failed_fields == ("holdings_snapshot",)
    assert fund_scores["004394"].p1_failed_fields == ()
    assert fund_scores["004395"].p1_failed_fields == ()
    assert quality_rows["004390"].missing_p1_fields == ("holdings_snapshot",)
    assert quality_rows["004393"].missing_p1_fields == ("holdings_snapshot",)
    assert quality_rows["004394"].missing_p1_fields == ()
    assert quality_rows["004395"].missing_p1_fields == ()


def test_bond_fund_excludes_equity_holdings_with_replacement_issue() -> None:
    """验证债券基金权益持仓字段排除时必须输出替代风险证据 issue。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当分母排除或替代 issue 不符合契约时抛出。
    """

    records = [
        _snapshot_record(
            "profile",
            "classified_fund_type",
            fund_code="006597",
            app_category="国内债券类",
            classified_fund_type="bond_fund",
            value_present=True,
            anchor_present=True,
        ),
        _snapshot_record(
            "holdings",
            "holdings_snapshot",
            fund_code="006597",
            app_category="国内债券类",
            classified_fund_type="bond_fund",
            value_present=True,
            anchor_present=True,
            comparable_values={
                "top_holdings_status": "missing",
                "top_holdings_source": "none",
            },
        ),
    ]

    field_rows = {row.field_name: row for row in score_snapshot_records(records)}
    fund_score = score_fund_records(records)[0]
    fund_quality = derive_fund_quality_records(records)[0]
    decisions = derive_field_applicability_decisions(records)
    issues = derive_score_applicability_issues(records)

    assert "holdings_snapshot" not in field_rows
    assert fund_score.records == 1
    assert fund_score.p1_failed_fields == ()
    assert fund_quality.total_field_count == 1
    assert fund_quality.missing_p1_fields == ()
    assert len(decisions) == 1
    assert decisions[0].applicability_status == "not_applicable_replaced"
    assert decisions[0].reason_code == "not_applicable_to_bond_fund_equity_holdings"
    assert decisions[0].raw_total_field_count == 2
    assert decisions[0].applicable_total_field_count == 1
    assert decisions[0].replacement_issue_ids == (
        "score-applicability:006597:2024:holdings_snapshot:bond_risk_evidence_missing:bond_risk_evidence.v1",
    )
    assert len(issues) == 1
    assert issues[0].issue_id == decisions[0].replacement_issue_ids[0]
    assert issues[0].issue_code == "bond_risk_evidence_missing"
    assert issues[0].contract_id == "bond_risk_evidence.v1"
    assert issues[0].baseline_blocking is True
    assert "convertible_bond_equity_exposure" in issues[0].missing_evidence_groups
    assert len(issues[0].missing_evidence_groups) == 7


def test_field_priority_includes_bond_risk_evidence_as_p1() -> None:
    """验证债券风险替代证据字段进入 P1 优先级。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 `bond_risk_evidence` 未注册为 P1 时抛出。
    """

    assert FIELD_PRIORITY_BY_NAME["bond_risk_evidence"] == "P1"


def test_complete_bond_risk_evidence_record_scores_p1_pass_without_issue() -> None:
    """验证完整债券风险证据行满足 P1 coverage/traceability 且不再发缺口 issue。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当完整结构化证据仍触发 blocker 或分数异常时抛出。
    """

    records = [
        _snapshot_record(
            "profile",
            "classified_fund_type",
            fund_code="006597",
            app_category="国内债券类",
            classified_fund_type="bond_fund",
            value_present=True,
            anchor_present=True,
        ),
        _snapshot_record(
            "holdings",
            "holdings_snapshot",
            fund_code="006597",
            app_category="国内债券类",
            classified_fund_type="bond_fund",
            value_present=True,
            anchor_present=True,
        ),
        _bond_risk_snapshot_record(
            fund_code="006597",
            contract_status="satisfied",
            satisfied_groups=_BOND_RISK_GROUP_IDS,
            anchor_present=True,
        ),
    ]

    field_rows = {row.field_name: row for row in score_snapshot_records(records)}
    fund_score = score_fund_records(records)[0]
    fund_quality = derive_fund_quality_records(records)[0]
    decisions = derive_field_applicability_decisions(records)

    assert field_rows["bond_risk_evidence"].priority == "P1"
    assert field_rows["bond_risk_evidence"].records == 1
    assert field_rows["bond_risk_evidence"].coverage_rate == 1.0
    assert field_rows["bond_risk_evidence"].traceability_rate == 1.0
    assert field_rows["bond_risk_evidence"].status == STATUS_PASS
    assert fund_score.p1_status == STATUS_PASS
    assert fund_quality.missing_p1_fields == ()
    assert decisions[0].replacement_issue_ids == ()
    assert derive_score_applicability_issues(records) == ()


def test_weak_drawdown_bond_risk_evidence_issue_lists_only_drawdown_group() -> None:
    """验证弱回撤证据只让 drawdown_stress 保持阻断。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当弱证据组扩散到其他组时抛出。
    """

    issue = _single_bond_issue(
        _bond_risk_snapshot_record(
            contract_status="partial",
            satisfied_groups=tuple(
                group_id for group_id in _BOND_RISK_GROUP_IDS if group_id != "drawdown_stress"
            ),
            weak_groups=("drawdown_stress",),
            anchor_present=True,
        )
    )

    assert issue.required_evidence_groups == _BOND_RISK_GROUP_IDS
    assert issue.missing_evidence_groups == ("drawdown_stress",)
    assert issue.baseline_blocking is True


def test_ambiguous_redemption_bond_risk_evidence_issue_lists_only_redemption_group() -> None:
    """验证申赎压力歧义只让 redemption_share_pressure 保持阻断。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当歧义证据组扩散到其他组时抛出。
    """

    issue = _single_bond_issue(
        _bond_risk_snapshot_record(
            contract_status="partial",
            satisfied_groups=tuple(
                group_id
                for group_id in _BOND_RISK_GROUP_IDS
                if group_id != "redemption_share_pressure"
            ),
            ambiguous_groups=("redemption_share_pressure",),
            anchor_present=True,
        )
    )

    assert issue.required_evidence_groups == _BOND_RISK_GROUP_IDS
    assert issue.missing_evidence_groups == ("redemption_share_pressure",)


def test_partial_bond_risk_evidence_keeps_required_groups_full_and_missing_dynamic() -> None:
    """验证 partial 记录 required 全量固定、missing 只列实际未满足组。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当动态缺口组或契约全量组不符合预期时抛出。
    """

    unsatisfied = ("leverage_liquidity", "drawdown_stress", "redemption_share_pressure")
    issue = _single_bond_issue(
        _bond_risk_snapshot_record(
            contract_status="partial",
            satisfied_groups=tuple(
                group_id for group_id in _BOND_RISK_GROUP_IDS if group_id not in unsatisfied
            ),
            missing_groups=("leverage_liquidity",),
            weak_groups=("drawdown_stress",),
            ambiguous_groups=("redemption_share_pressure",),
            anchor_present=True,
        )
    )

    assert issue.required_evidence_groups == _BOND_RISK_GROUP_IDS
    assert issue.missing_evidence_groups == unsatisfied


def test_anchor_missing_accepted_bond_risk_evidence_remains_all_seven_blocking() -> None:
    """验证缺少锚点的 accepted-looking 记录按整条契约不满足处理。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当无锚点记录被误判为满足时抛出。
    """

    issue = _single_bond_issue(
        _bond_risk_snapshot_record(
            contract_status="satisfied",
            satisfied_groups=_BOND_RISK_GROUP_IDS,
            anchor_present=False,
        )
    )

    assert issue.required_evidence_groups == _BOND_RISK_GROUP_IDS
    assert issue.missing_evidence_groups == _BOND_RISK_GROUP_IDS
    assert issue.baseline_blocking is True


def test_value_missing_accepted_bond_risk_evidence_remains_all_seven_blocking() -> None:
    """验证缺少字段值的 accepted-looking 记录按整条契约不满足处理。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 value_present=false 的记录被误判为满足时抛出。
    """

    issue = _single_bond_issue(
        _bond_risk_snapshot_record(
            contract_status="satisfied",
            satisfied_groups=_BOND_RISK_GROUP_IDS,
            value_present=False,
            anchor_present=True,
        )
    )

    assert issue.issue_code == "bond_risk_evidence_missing"
    assert issue.required_evidence_groups == _BOND_RISK_GROUP_IDS
    assert issue.missing_evidence_groups == _BOND_RISK_GROUP_IDS
    assert issue.baseline_blocking is True


def test_malformed_bond_risk_evidence_record_remains_all_seven_blocking() -> None:
    """验证结构化组字段 malformed 时 fail-closed 为全量缺口。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 malformed 结构化字段被当作满足时抛出。
    """

    record = _bond_risk_snapshot_record(
        contract_status="satisfied",
        satisfied_groups=_BOND_RISK_GROUP_IDS,
        anchor_present=True,
    )
    record["bond_risk_satisfied_groups"] = "duration_rate_risk"

    issue = _single_bond_issue(record)

    assert issue.missing_evidence_groups == _BOND_RISK_GROUP_IDS


def test_missing_contract_status_bond_risk_evidence_remains_all_seven_blocking() -> None:
    """验证缺少 contract_status 时 fail-closed 为全量缺口。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当缺少契约状态的记录被误判为满足时抛出。
    """

    issue = _single_bond_issue(
        _bond_risk_snapshot_record(
            contract_status=None,
            satisfied_groups=_BOND_RISK_GROUP_IDS,
            anchor_present=True,
        )
    )

    assert issue.missing_evidence_groups == _BOND_RISK_GROUP_IDS


def test_non_bond_fund_ignores_bond_risk_evidence_record() -> None:
    """验证非债基不因债券风险替代证据进入 P1 分母或触发 issue。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当非债基被 bond_risk_evidence 影响评分时抛出。
    """

    records = [
        _snapshot_record(
            "holdings",
            "holdings_snapshot",
            fund_code="004393",
            classified_fund_type="active_fund",
            value_present=True,
            anchor_present=True,
            comparable_values={
                "top_holdings_status": "direct_top_ten",
                "top_holdings_source": "top_ten",
            },
        ),
        _bond_risk_snapshot_record(
            fund_code="004393",
            classified_fund_type="active_fund",
            contract_status="missing",
            missing_groups=_BOND_RISK_GROUP_IDS,
            value_present=False,
            anchor_present=False,
        ),
    ]

    field_rows = {row.field_name: row for row in score_snapshot_records(records)}
    fund_quality = derive_fund_quality_records(records)[0]

    assert "bond_risk_evidence" not in field_rows
    assert fund_quality.missing_p1_fields == ()
    assert derive_score_applicability_issues(records) == ()


def test_bond_risk_score_does_not_parse_note_for_satisfaction() -> None:
    """验证评分不读取 note 文本来决定债券风险证据是否满足。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 note 伪造满足状态影响评分时抛出。
    """

    record = _bond_risk_snapshot_record(
        contract_status="missing",
        missing_groups=_BOND_RISK_GROUP_IDS,
        value_present=False,
        anchor_present=True,
    )
    record["note"] = "contract_status=satisfied; all seven groups satisfied"

    issue = _single_bond_issue(record)

    assert issue.missing_evidence_groups == _BOND_RISK_GROUP_IDS


def test_bond_score_applicability_issue_id_is_deterministic() -> None:
    """验证债券替代 issue id 使用计划要求的稳定格式。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 issue id 不稳定时抛出。
    """

    records = [
        _snapshot_record(
            "holdings",
            "holdings_snapshot",
            fund_code="006597",
            report_year=2023,
            app_category="国内债券类",
            classified_fund_type="bond_fund",
            value_present=False,
            anchor_present=False,
        )
    ]

    issue = derive_score_applicability_issues(records)[0]

    assert issue.issue_id == (
        "score-applicability:006597:2023:holdings_snapshot:bond_risk_evidence_missing:bond_risk_evidence.v1"
    )


def test_active_fund_keeps_holdings_snapshot_applicable() -> None:
    """验证主动基金持仓字段继续进入 P1 分母。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当主动基金被错误套用债券排除时抛出。
    """

    records = [
        _snapshot_record(
            "holdings",
            "holdings_snapshot",
            classified_fund_type="active_fund",
            value_present=True,
            anchor_present=True,
            comparable_values={
                "top_holdings_status": "missing",
                "top_holdings_source": "none",
            },
        )
    ]

    field_row = score_snapshot_records(records)[0]
    fund_quality = derive_fund_quality_records(records)[0]

    assert field_row.field_name == "holdings_snapshot"
    assert field_row.records == 1
    assert fund_quality.missing_p1_fields == ("holdings_snapshot",)
    assert derive_score_applicability_issues(records) == ()


def test_index_and_enhanced_keep_holdings_snapshot_applicable() -> None:
    """验证指数和增强指数基金不被债券持仓替代规则影响。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当非债券基金 holdings_snapshot 被排除时抛出。
    """

    records = [
        _snapshot_record(
            "holdings",
            "holdings_snapshot",
            fund_code="510300",
            classified_fund_type="index_fund",
            value_present=False,
            anchor_present=False,
        ),
        _snapshot_record(
            "holdings",
            "holdings_snapshot",
            fund_code="161725",
            classified_fund_type="enhanced_index",
            value_present=False,
            anchor_present=False,
        ),
    ]

    fund_quality = {row.fund_code: row for row in derive_fund_quality_records(records)}

    assert all(row.field_name == "holdings_snapshot" for row in score_snapshot_records(records))
    assert fund_quality["510300"].missing_p1_fields == ("holdings_snapshot",)
    assert fund_quality["161725"].missing_p1_fields == ("holdings_snapshot",)
    assert derive_score_applicability_issues(records) == ()


def test_unknown_or_conflicted_fund_type_keeps_holdings_fail_closed() -> None:
    """验证未知或冲突基金类型不排除 holdings_snapshot，也不生成债券替代 issue。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 fail-closed 分母被错误排除时抛出。
    """

    unknown_records = [
        _snapshot_record(
            "holdings",
            "holdings_snapshot",
            fund_code="000001",
            classified_fund_type="",
            value_present=False,
            anchor_present=False,
        )
    ]
    conflicted_records = [
        _snapshot_record(
            "profile",
            "classified_fund_type",
            fund_code="000002",
            classified_fund_type="active_fund",
            value_present=True,
            anchor_present=True,
        ),
        _snapshot_record(
            "holdings",
            "holdings_snapshot",
            fund_code="000002",
            classified_fund_type="bond_fund",
            value_present=False,
            anchor_present=False,
        ),
    ]

    unknown_quality = derive_fund_quality_records(unknown_records)[0]
    conflicted_quality = derive_fund_quality_records(conflicted_records)[0]
    unknown_decision = derive_field_applicability_decisions(unknown_records)[0]
    conflicted_decision = derive_field_applicability_decisions(conflicted_records)[0]

    assert unknown_quality.missing_p1_fields == ("holdings_snapshot",)
    assert conflicted_quality.missing_p1_fields == ("holdings_snapshot",)
    assert unknown_decision.applicability_status == "unknown_fail_closed"
    assert conflicted_decision.applicability_status == "unknown_fail_closed"
    assert derive_score_applicability_issues(unknown_records) == ()
    assert derive_score_applicability_issues(conflicted_records) == ()


def test_derive_fund_quality_records_resolves_all_standard_fund_types() -> None:
    """验证所有标准基金类型都能解析当前模板契约。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 任一标准基金类型无法解析 8 章 preferred_lens 时抛出。
    """

    cases = (
        ("index_fund", "国内股票类"),
        ("active_fund", "国内股票类"),
        ("bond_fund", "国内债券类"),
        ("enhanced_index", "国内股票类"),
        ("qdii_fund", "海外股票类"),
        ("fof_fund", "海外债券/稳健类"),
    )

    for fund_type, app_category in cases:
        row = derive_fund_quality_records(
            [
                _snapshot_record(
                    "profile",
                    "classified_fund_type",
                    app_category=app_category,
                    classified_fund_type=fund_type,
                    value_present=True,
                    anchor_present=True,
                )
            ]
        )[0]

        assert row.preferred_lens_status == "resolved"
        assert row.preferred_lens_key == fund_type
        assert len(row.preferred_lens_chapters) == 8
        assert row.preferred_lens_unresolved_chapter_ids == ()


def test_derive_fund_quality_records_marks_conflicting_fund_type_without_first_row_fallback() -> (
    None
):
    """验证同一基金多行基金类型冲突时不取第一行静默通过。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当冲突字段未进入 mismatch/unknown 时抛出。
    """

    records = [
        _snapshot_record(
            "profile",
            "basic_identity",
            value_present=True,
            anchor_present=True,
            classified_fund_type="active_fund",
        ),
        _snapshot_record(
            "profile",
            "index_profile",
            value_present=False,
            anchor_present=False,
            classified_fund_type="bond_fund",
        ),
    ]

    row = derive_fund_quality_records(records)[0]

    assert row.classified_fund_type is None
    assert row.app_category_status == "unknown"
    assert row.preferred_lens_status == "mismatch"
    assert row.missing_p1_fields == ("index_profile",)
    assert row.preferred_lens_chapters == ()
    assert row.item_rule_decisions == ()
    assert "classified_fund_type 存在冲突值" in row.reason


def test_fund_score_keeps_index_quality_fields_when_fund_type_conflicts() -> None:
    """验证 fund_score 与 fund_quality 在基金类型冲突时一致保守计分。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 fund_score 排除冲突类型下的指数质量字段时抛出。
    """

    records = [
        _snapshot_record(
            "profile",
            "basic_identity",
            value_present=True,
            anchor_present=True,
            classified_fund_type="active_fund",
        ),
        _snapshot_record(
            "profile",
            "index_profile",
            value_present=False,
            anchor_present=False,
            classified_fund_type="bond_fund",
        ),
    ]

    fund_score = score_fund_records(records)[0]
    fund_quality = derive_fund_quality_records(records)[0]

    assert fund_score.records == 2
    assert fund_score.p1_failed_fields == ("index_profile",)
    assert fund_quality.total_field_count == 2
    assert fund_quality.missing_p1_fields == ("index_profile",)


def test_derive_fund_quality_records_marks_missing_fund_type_not_applicable() -> None:
    """验证基金类型缺失时 FQ5 不声明模板契约适用性。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 缺失基金类型被错误阻断或生成契约事实时抛出。
    """

    row = derive_fund_quality_records(
        [
            _snapshot_record(
                "profile",
                "classified_fund_type",
                value_present=True,
                anchor_present=True,
                classified_fund_type="",
            )
        ]
    )[0]

    assert row.classified_fund_type is None
    assert row.preferred_lens_status == "not_applicable"
    assert row.preferred_lens_chapters == ()
    assert row.item_rule_decisions == ()


def test_derive_fund_quality_records_marks_unsupported_fund_type_mismatch() -> None:
    """验证不受支持但已存在的基金类型触发 FQ5 mismatch。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 不受支持基金类型未触发 mismatch 时抛出。
    """

    row = derive_fund_quality_records(
        [
            _snapshot_record(
                "profile",
                "classified_fund_type",
                app_category="未知类别",
                classified_fund_type="money_market_fund",
                value_present=True,
                anchor_present=True,
            )
        ]
    )[0]

    assert row.preferred_lens_status == "mismatch"
    assert row.preferred_lens_key == "money_market_fund"
    assert "不受当前模板契约支持" in row.reason


def test_derive_fund_quality_records_marks_money_market_category_not_applicable() -> None:
    """验证货币基金类显式标记为当前 8 章模板不适用。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 货币基金类未进入 not_applicable 时抛出。
    """

    row = derive_fund_quality_records(
        [
            _snapshot_record(
                "profile",
                "classified_fund_type",
                app_category="货币基金类",
                classified_fund_type="money_market_fund",
                value_present=True,
                anchor_present=True,
            )
        ]
    )[0]

    assert row.preferred_lens_status == "not_applicable"
    assert row.preferred_lens_key is None
    assert row.preferred_lens_chapters == ()
    assert row.item_rule_decisions == ()


def test_derive_fund_quality_records_marks_lens_mismatch_on_app_category_conflict() -> None:
    """验证 App 类别冲突会让 preferred_lens 状态变为 mismatch。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当类别冲突未影响 lens 可解析性时抛出。
    """

    records = [
        _snapshot_record(
            "profile",
            "classified_fund_type",
            app_category="国内债券类",
            classified_fund_type="active_fund",
            value_present=True,
            anchor_present=True,
        )
    ]

    row = derive_fund_quality_records(records)[0]

    assert row.app_category_status == "conflict"
    assert row.preferred_lens_key == "active_fund"
    assert row.preferred_lens_status == "mismatch"
    assert "明确冲突" in row.reason


def test_run_extraction_score_writes_score_outputs(tmp_path: Path) -> None:
    """验证评分 API 从 snapshot.jsonl 写出 score.json、score.md 和 golden_set.json。

    Args:
        tmp_path: pytest 临时目录 fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当输出产物缺失或内容不符合契约时抛出。
    """

    snapshot_path = tmp_path / "snapshot.jsonl"
    snapshot_path.write_text(
        "\n".join(
            json.dumps(record, ensure_ascii=False)
            for record in [
                _snapshot_record(
                    "profile", "basic_identity", value_present=True, anchor_present=True
                ),
                _snapshot_record("profile", "benchmark", value_present=False, anchor_present=False),
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    output_dir = tmp_path / "score-output"

    result = run_extraction_score(
        snapshot_path=snapshot_path,
        source_csv=Path("docs/code_20260519.csv"),
        output_dir=output_dir,
    )

    score_payload = json.loads(result.score_json_path.read_text(encoding="utf-8"))
    markdown = result.score_markdown_path.read_text(encoding="utf-8")
    golden_payload = json.loads(result.golden_set_path.read_text(encoding="utf-8"))

    assert result.score_json_path.exists()
    assert result.score_markdown_path.exists()
    assert result.golden_set_path.exists()
    assert set(score_payload) == _SCORE_JSON_TOP_LEVEL_KEYS
    assert score_payload["fund_count"] == 1
    assert score_payload["failed_funds"] == []
    assert score_payload["fund_scores"][0]["fund_code"] == "004393"
    quality_row = score_payload["fund_quality"][0]
    assert quality_row["preferred_lens_status"] == "resolved"
    assert quality_row["preferred_lens_key"] == "active_fund"
    assert quality_row["contract_template_id"] == "fund-analysis-template-v1"
    assert quality_row["item_rule_template_id"] == "fund-analysis-template-v1"
    assert len(quality_row["preferred_lens_chapters"]) == 8
    assert quality_row["preferred_lens_unresolved_chapter_ids"] == []
    decisions_by_rule = {
        decision["rule_id"]: decision for decision in quality_row["item_rule_decisions"]
    }
    assert decisions_by_rule["chapter_1_manager_philosophy"]["status"] == "render"
    assert decisions_by_rule["chapter_2_alpha_yearly_breakdown"]["status"] == "render"
    assert decisions_by_rule["chapter_1_index_constituents"]["status"] == "delete"
    assert decisions_by_rule["chapter_2_tracking_error_analysis"]["status"] == "delete"
    assert "## Fund Quality" in markdown
    assert score_payload["field_applicability_decisions"] == []
    assert score_payload["score_applicability_issues"] == []
    assert "## Score Applicability Issues" in markdown
    assert "delete=2/render=2" in markdown
    assert score_payload["correctness"]["status"] == CORRECTNESS_STATUS_UNAVAILABLE
    assert score_payload["p0_status"] == STATUS_FAIL
    assert "## Correctness" in markdown
    assert "## Fund Scores" in markdown
    assert "## Field Scores" in markdown
    assert MANDATORY_GOLDEN_CODE in {record["fund_code"] for record in golden_payload["records"]}


def test_run_extraction_score_output_ignores_additive_source_provenance(
    tmp_path: Path,
) -> None:
    """验证 score.json key 集合和 gate 敏感输出不因 provenance 字段变化。

    Args:
        tmp_path: pytest 临时目录 fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 additive provenance 改变 score.json 或 FQ 输出时抛出。
    """

    legacy_snapshot_path = tmp_path / "legacy-snapshot.jsonl"
    provenance_snapshot_path = tmp_path / "provenance-snapshot.jsonl"
    legacy_records = [
        _snapshot_record("profile", "basic_identity", value_present=True, anchor_present=True),
        _snapshot_record("profile", "benchmark", value_present=False, anchor_present=False),
    ]
    provenance_records = [
        _snapshot_record(
            "profile",
            "basic_identity",
            value_present=True,
            anchor_present=True,
            include_source_provenance=True,
        ),
        _snapshot_record(
            "profile",
            "benchmark",
            value_present=False,
            anchor_present=False,
            include_source_provenance=True,
        ),
    ]
    legacy_snapshot_path.write_text(
        "\n".join(json.dumps(record, ensure_ascii=False) for record in legacy_records) + "\n",
        encoding="utf-8",
    )
    provenance_snapshot_path.write_text(
        "\n".join(json.dumps(record, ensure_ascii=False) for record in provenance_records) + "\n",
        encoding="utf-8",
    )

    legacy_result = run_extraction_score(
        snapshot_path=legacy_snapshot_path,
        source_csv=Path("docs/code_20260519.csv"),
        output_dir=tmp_path / "legacy-score",
    )
    provenance_result = run_extraction_score(
        snapshot_path=provenance_snapshot_path,
        source_csv=Path("docs/code_20260519.csv"),
        output_dir=tmp_path / "provenance-score",
    )

    legacy_payload = json.loads(legacy_result.score_json_path.read_text(encoding="utf-8"))
    provenance_payload = json.loads(
        provenance_result.score_json_path.read_text(encoding="utf-8")
    )
    for payload in (legacy_payload, provenance_payload):
        assert set(payload) == _SCORE_JSON_TOP_LEVEL_KEYS

    gate_sensitive_keys = (
        "thresholds",
        "field_count",
        "fund_count",
        "status_counts",
        "p0_status",
        "field_scores",
        "fund_scores",
        "fund_quality",
        "field_applicability_decisions",
        "score_applicability_issues",
        "failed_funds",
        "golden_set",
        "correctness",
    )
    assert {
        key: legacy_payload[key] for key in gate_sensitive_keys
    } == {key: provenance_payload[key] for key in gate_sensitive_keys}


def test_run_extraction_score_includes_failed_funds_from_errors_path(tmp_path: Path) -> None:
    """验证 errors.jsonl 中的完全失败基金进入 score failed_funds。

    Args:
        tmp_path: pytest 临时目录 fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当失败基金 accounting 缺失时抛出。
    """

    snapshot_path = tmp_path / "snapshot.jsonl"
    snapshot_path.write_text(
        json.dumps(
            _snapshot_record("profile", "basic_identity", value_present=True, anchor_present=True),
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )
    errors_path = tmp_path / "errors.jsonl"
    errors_path.write_text(
        json.dumps(
            {
                "fund_code": "000001",
                "fund_name": "失败基金",
                "app_category": "国内股票类",
                "report_year": 2024,
                "error_type": "RuntimeError",
                "error_message": "fixture failure",
            },
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )

    result = run_extraction_score(
        snapshot_path=snapshot_path,
        source_csv=Path("docs/code_20260519.csv"),
        output_dir=tmp_path / "score-output",
        errors_path=errors_path,
    )

    score_payload = json.loads(result.score_json_path.read_text(encoding="utf-8"))
    markdown = result.score_markdown_path.read_text(encoding="utf-8")

    assert len(result.failed_funds) == 1
    assert score_payload["failed_funds"] == [
        {
            "fund_code": "000001",
            "fund_name": "失败基金",
            "app_category": "国内股票类",
            "report_year": 2024,
            "error_type": "RuntimeError",
            "error_message": "fixture failure",
        }
    ]
    assert "## Failed Funds" in markdown
    assert "000001" in markdown


def test_load_snapshot_error_records_rejects_malformed_rows(tmp_path: Path) -> None:
    """验证 errors.jsonl 行级 schema 非法时 fail fast。

    Args:
        tmp_path: pytest 临时目录 fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当非法错误记录未被拒绝时抛出。
    """

    errors_path = tmp_path / "errors.jsonl"
    errors_path.write_text(json.dumps({"error_type": "RuntimeError"}) + "\n", encoding="utf-8")

    try:
        load_snapshot_error_records(errors_path)
    except ValueError as exc:
        assert "fund_code" in str(exc)
    else:
        raise AssertionError("expected ValueError for missing fund_code")


def test_compare_snapshot_correctness_perfect_match_and_skipped_denominator(tmp_path: Path) -> None:
    """验证 correctness 可比子字段 perfect match 且 skipped 不进入分母。

    Args:
        tmp_path: pytest 临时目录 fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 correctness 分母或匹配状态不符合契约时抛出。
    """

    golden_path = _golden_answer_json(
        tmp_path,
        expected_fund_type="active_fund",
        skipped_fields=["fee_schedule"],
    )
    records = [
        _snapshot_record(
            "profile",
            "classified_fund_type",
            value_present=True,
            anchor_present=True,
            classified_fund_type="active_fund",
            comparable_values={"fund_type": "active_fund"},
        ),
        _snapshot_record(
            "profile",
            "basic_identity",
            value_present=True,
            anchor_present=True,
            comparable_values={"fund_name": "测试基金"},
        ),
    ]

    summary = compare_snapshot_correctness(records=records, golden_answer_path=golden_path)

    assert summary.status == CORRECTNESS_STATUS_AVAILABLE
    assert summary.total_records == 2
    assert summary.comparable_records == 2
    assert summary.matched_records == 2
    assert summary.mismatched_records == 0
    assert summary.unavailable_records == 0
    assert summary.skipped_records == 1
    assert summary.accuracy_rate == 1.0
    assert summary.coverage_scope == CORRECTNESS_COVERAGE_COVERED
    assert summary.coverage_reason == CORRECTNESS_COVERAGE_COVERED
    assert summary.covered_fund_codes == ("004393",)
    assert summary.missing_fund_codes == ()
    assert summary.coverage_required is False
    assert {row.report_year for row in summary.record_results} == {2024}
    statuses = {(row.field_name, row.sub_field): row.status for row in summary.record_results}
    assert statuses[("classified_fund_type", "fund_type")] == CORRECTNESS_MATCH
    assert statuses[("basic_identity", "fund_name")] == CORRECTNESS_MATCH


def test_compare_snapshot_correctness_without_golden_path_is_not_configured() -> None:
    """验证未配置 strict golden path 时输出 not_configured coverage。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 coverage 状态不符合 P9-S2 契约时抛出。
    """

    summary = compare_snapshot_correctness(
        records=[
            _snapshot_record(
                "profile",
                "classified_fund_type",
                value_present=True,
                anchor_present=True,
            )
        ],
        golden_answer_path=None,
    )

    assert summary.status == CORRECTNESS_STATUS_UNAVAILABLE
    assert summary.coverage_scope == CORRECTNESS_COVERAGE_NOT_CONFIGURED
    assert summary.coverage_reason == CORRECTNESS_COVERAGE_NOT_CONFIGURED
    assert summary.missing_fund_codes == ("004393",)
    assert summary.record_results == ()


def test_compare_snapshot_correctness_malformed_existing_golden_file_fails_closed(
    tmp_path: Path,
) -> None:
    """验证已有 malformed golden 文件不会退化成 not_configured。

    Args:
        tmp_path: pytest 临时目录 fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 malformed strict golden 被静默降级时抛出。
    """

    golden_path = tmp_path / "golden-answer.json"
    golden_path.write_text("{ malformed", encoding="utf-8")

    try:
        compare_snapshot_correctness(
            records=[
                _snapshot_record(
                    "profile",
                    "classified_fund_type",
                    value_present=True,
                    anchor_present=True,
                )
            ],
            golden_answer_path=golden_path,
        )
    except json.JSONDecodeError:
        return
    raise AssertionError("expected malformed golden file to fail closed")


def test_compare_snapshot_correctness_missing_explicit_golden_file_fails_closed(
    tmp_path: Path,
) -> None:
    """验证显式 golden 路径缺失时抛出 FileNotFoundError。

    Args:
        tmp_path: pytest 临时目录 fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当缺失路径被误判为 not_configured 时抛出。
    """

    try:
        compare_snapshot_correctness(
            records=[
                _snapshot_record(
                    "profile",
                    "classified_fund_type",
                    value_present=True,
                    anchor_present=True,
                )
            ],
            golden_answer_path=tmp_path / "missing.json",
        )
    except FileNotFoundError:
        return
    raise AssertionError("expected missing explicit golden file to fail closed")


def test_compare_snapshot_correctness_marks_current_fund_not_covered(tmp_path: Path) -> None:
    """验证 golden 文件存在但当前基金缺记录时为 fund_not_covered。

    Args:
        tmp_path: pytest 临时目录 fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当当前基金覆盖缺口未被识别时抛出。
    """

    golden_path = _golden_answer_json(tmp_path, expected_fund_type="active_fund")
    records = [
        _snapshot_record(
            "profile",
            "classified_fund_type",
            fund_code="000216",
            value_present=True,
            anchor_present=True,
            comparable_values={"fund_type": "active_fund"},
        )
    ]

    summary = compare_snapshot_correctness(records=records, golden_answer_path=golden_path)

    assert summary.status == CORRECTNESS_STATUS_AVAILABLE
    assert summary.coverage_scope == CORRECTNESS_COVERAGE_FUND_NOT_COVERED
    assert summary.coverage_reason == CORRECTNESS_COVERAGE_FUND_NOT_COVERED
    assert summary.covered_fund_codes == ()
    assert summary.missing_fund_codes == ("000216",)


def test_compare_snapshot_correctness_marks_current_year_not_covered(
    tmp_path: Path,
) -> None:
    """验证同基金不同年报年份不会误用其它年份 golden answer。

    Args:
        tmp_path: pytest 临时目录 fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 2025 snapshot 被 2024 golden 误杀时抛出。
    """

    golden_path = _golden_answer_json(tmp_path, expected_fund_type="active_fund")
    records = [
        _snapshot_record(
            "profile",
            "classified_fund_type",
            report_year=2025,
            value_present=True,
            anchor_present=True,
            classified_fund_type="index_fund",
            comparable_values={"fund_type": "index_fund"},
        )
    ]

    summary = compare_snapshot_correctness(records=records, golden_answer_path=golden_path)

    assert summary.status == CORRECTNESS_STATUS_AVAILABLE
    assert summary.coverage_scope == CORRECTNESS_COVERAGE_YEAR_NOT_COVERED
    assert summary.coverage_reason == CORRECTNESS_COVERAGE_YEAR_NOT_COVERED
    assert summary.comparable_records == 0
    assert summary.mismatched_records == 0
    assert summary.covered_fund_codes == ()
    assert summary.missing_fund_codes == ("004393",)
    assert {row.report_year for row in summary.record_results} == {2024}
    assert all(row.status == CORRECTNESS_UNAVAILABLE for row in summary.record_results)


def test_compare_snapshot_correctness_marks_current_fund_no_comparable_fields(
    tmp_path: Path,
) -> None:
    """验证当前基金有 golden 记录但无可比字段时为 no_comparable_fields。

    Args:
        tmp_path: pytest 临时目录 fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当不可比 coverage 缺口未被识别时抛出。
    """

    golden_path = _golden_answer_json_from_records(
        tmp_path,
        records=[
            {
                "fund_code": "004393",
                "field_name": "fee_schedule",
                "sub_field": "management_fee",
                "expected_value": "1.20%",
                "confidence": "high",
                "source": "年报2024 §2 page-5",
            }
        ],
    )
    records = [
        _snapshot_record(
            "fee",
            "fee_schedule",
            value_present=True,
            anchor_present=True,
            comparable_values={},
        )
    ]

    summary = compare_snapshot_correctness(records=records, golden_answer_path=golden_path)

    assert summary.status == CORRECTNESS_STATUS_AVAILABLE
    assert summary.comparable_records == 0
    assert summary.unavailable_records == 1
    assert summary.coverage_scope == CORRECTNESS_COVERAGE_NO_COMPARABLE_FIELDS
    assert summary.coverage_reason == CORRECTNESS_COVERAGE_NO_COMPARABLE_FIELDS
    assert summary.missing_fund_codes == ("004393",)


def test_compare_snapshot_correctness_keeps_legacy_classification_compatibility(
    tmp_path: Path,
) -> None:
    """验证旧 snapshot 没有 comparable_values 时只兼容基金类型字段。

    Args:
        tmp_path: pytest 临时目录 fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当旧 snapshot 兼容路径不符合契约时抛出。
    """

    golden_path = _golden_answer_json(tmp_path, expected_fund_type="active_fund")
    records = [
        _snapshot_record(
            "profile",
            "classified_fund_type",
            value_present=True,
            anchor_present=True,
            classified_fund_type="active_fund",
        ),
        _snapshot_record(
            "profile",
            "basic_identity",
            value_present=False,
            anchor_present=False,
        ),
    ]

    summary = compare_snapshot_correctness(records=records, golden_answer_path=golden_path)

    assert summary.comparable_records == 1
    assert summary.matched_records == 1
    assert summary.unavailable_records == 1
    assert summary.coverage_scope == CORRECTNESS_COVERAGE_PARTIALLY_COVERED
    statuses = {(row.field_name, row.sub_field): row.status for row in summary.record_results}
    assert statuses[("classified_fund_type", "fund_type")] == CORRECTNESS_MATCH
    assert statuses[("basic_identity", "fund_name")] == CORRECTNESS_UNAVAILABLE


def test_compare_snapshot_correctness_distinguishes_whitelist_missing_from_unavailable(
    tmp_path: Path,
) -> None:
    """验证只有白名单子字段明确缺失会进入 mismatch。

    Args:
        tmp_path: pytest 临时目录 fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当白名单缺失和非白名单缺失语义不符合契约时抛出。
    """

    golden_path = _golden_answer_json_from_records(
        tmp_path,
        records=[
            {
                "fund_code": "004393",
                "field_name": "basic_identity",
                "sub_field": "fund_name",
                "expected_value": "测试基金",
                "confidence": "high",
                "source": "年报2024 §2 page-5",
            },
            {
                "fund_code": "004393",
                "field_name": "fee_schedule",
                "sub_field": "management_fee",
                "expected_value": "1.20%",
                "confidence": "high",
                "source": "年报2024 §2 page-5",
            },
        ],
    )
    records = [
        _snapshot_record(
            "profile",
            "basic_identity",
            value_present=False,
            anchor_present=False,
            comparable_values={},
        ),
        _snapshot_record(
            "profile",
            "fee_schedule",
            value_present=False,
            anchor_present=False,
            comparable_values={},
        ),
    ]

    summary = compare_snapshot_correctness(records=records, golden_answer_path=golden_path)

    assert summary.comparable_records == 1
    assert summary.mismatched_records == 1
    assert summary.unavailable_records == 1
    statuses = {(row.field_name, row.sub_field): row.status for row in summary.record_results}
    assert statuses[("basic_identity", "fund_name")] == CORRECTNESS_MISMATCH
    assert statuses[("fee_schedule", "management_fee")] == CORRECTNESS_UNAVAILABLE


def test_compare_snapshot_correctness_marks_missing_whitelist_subfield_as_mismatch(
    tmp_path: Path,
) -> None:
    """验证新 snapshot 中白名单子字段省略时按明确缺失处理。

    Args:
        tmp_path: pytest 临时目录 fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当白名单子字段缺失被误记为 unavailable 时抛出。
    """

    golden_path = _golden_answer_json_from_records(
        tmp_path,
        records=[
            {
                "fund_code": "004393",
                "field_name": "basic_identity",
                "sub_field": "fund_name",
                "expected_value": "测试基金",
                "confidence": "high",
                "source": "年报2024 §2 page-5",
            },
        ],
    )
    records = [
        _snapshot_record(
            "profile",
            "basic_identity",
            value_present=True,
            anchor_present=True,
            comparable_values={"fund_code": "004393"},
        )
    ]

    summary = compare_snapshot_correctness(records=records, golden_answer_path=golden_path)

    assert summary.comparable_records == 1
    assert summary.mismatched_records == 1
    assert summary.unavailable_records == 0
    assert summary.record_results[0].status == CORRECTNESS_MISMATCH


def test_compare_snapshot_correctness_handles_index_quality_comparable_fields(
    tmp_path: Path,
) -> None:
    """验证 index_profile 和 tracking_error 可比子字段进入 correctness。

    Args:
        tmp_path: pytest 临时目录 fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当指数质量字段 correctness 状态不符合预期时抛出。
    """

    golden_path = _golden_answer_json_from_records(
        tmp_path,
        records=[
            {
                "fund_code": "004393",
                "field_name": "index_profile",
                "sub_field": "benchmark_index_name",
                "expected_value": "沪深300指数",
                "confidence": "high",
                "source": "年报2024 §2 page-5",
            },
            {
                "fund_code": "004393",
                "field_name": "tracking_error",
                "sub_field": "annualized",
                "expected_value": "True",
                "confidence": "high",
                "source": "年报2024 §3 page-6",
            },
            {
                "fund_code": "004393",
                "field_name": "tracking_error",
                "sub_field": "value_text",
                "expected_value": "1.23%",
                "confidence": "high",
                "source": "年报2024 §3 page-6",
            },
        ],
    )
    records = [
        _snapshot_record(
            "profile",
            "index_profile",
            value_present=True,
            anchor_present=True,
            classified_fund_type="index_fund",
            comparable_values={"benchmark_index_name": "沪深300指数"},
        ),
        _snapshot_record(
            "performance",
            "tracking_error",
            value_present=True,
            anchor_present=True,
            classified_fund_type="index_fund",
            comparable_values={"annualized": "False", "value_text": "1.23%"},
        ),
    ]

    summary = compare_snapshot_correctness(records=records, golden_answer_path=golden_path)
    statuses = {(row.field_name, row.sub_field): row.status for row in summary.record_results}

    assert summary.comparable_records == 3
    assert summary.matched_records == 2
    assert summary.mismatched_records == 1
    assert statuses[("index_profile", "benchmark_index_name")] == CORRECTNESS_MATCH
    assert statuses[("tracking_error", "annualized")] == CORRECTNESS_MISMATCH
    assert statuses[("tracking_error", "value_text")] == CORRECTNESS_MATCH


def test_compare_snapshot_correctness_normalizes_benchmark_chinese_visual_whitespace(
    tmp_path: Path,
) -> None:
    """验证 benchmark 字段级中文视觉空白可归一化。

    Args:
        tmp_path: pytest 临时目录 fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 benchmark 视觉空白未匹配时抛出。
    """

    golden_path = _golden_answer_json_from_records(
        tmp_path,
        records=[
            {
                "fund_code": "004393",
                "field_name": "benchmark",
                "sub_field": "benchmark_text",
                "expected_value": "中债综合（全价）指数收益率",
                "confidence": "high",
                "source": "年报2024 §2 page-5",
            }
        ],
    )
    records = [
        _snapshot_record(
            "profile",
            "benchmark",
            value_present=True,
            anchor_present=True,
            comparable_values={"benchmark_text": "中债综 合（全价）指数收益率"},
        )
    ]

    summary = compare_snapshot_correctness(records=records, golden_answer_path=golden_path)

    assert summary.comparable_records == 1
    assert summary.matched_records == 1
    assert summary.record_results[0].status == CORRECTNESS_MATCH
    assert summary.record_results[0].normalized_actual == "中债综合（全价）指数收益率"


def test_compare_snapshot_correctness_keeps_visual_whitespace_for_non_benchmark_fields(
    tmp_path: Path,
) -> None:
    """验证非 benchmark 字段不获得中文视觉空白归一化。

    Args:
        tmp_path: pytest 临时目录 fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当非 benchmark 字段被过度归一化时抛出。
    """

    golden_path = _golden_answer_json_from_records(
        tmp_path,
        records=[
            {
                "fund_code": "004393",
                "field_name": "basic_identity",
                "sub_field": "fund_name",
                "expected_value": "中债综合",
                "confidence": "high",
                "source": "年报2024 §2 page-5",
            }
        ],
    )
    records = [
        _snapshot_record(
            "profile",
            "basic_identity",
            value_present=True,
            anchor_present=True,
            comparable_values={"fund_name": "中债综 合"},
        )
    ]

    summary = compare_snapshot_correctness(records=records, golden_answer_path=golden_path)

    assert summary.comparable_records == 1
    assert summary.mismatched_records == 1
    assert summary.record_results[0].status == CORRECTNESS_MISMATCH
    assert summary.record_results[0].normalized_actual == "中债综 合"


def test_compare_snapshot_correctness_normalizes_basic_identity_chinese_date_spacing(
    tmp_path: Path,
) -> None:
    """验证 basic_identity.inception_date 中文日期视觉空白可归一化。

    Args:
        tmp_path: pytest 临时目录 fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当中文年月日日期空白差异未匹配时抛出。
    """

    golden_path = _golden_answer_json_from_records(
        tmp_path,
        records=[
            {
                "fund_code": "004393",
                "field_name": "basic_identity",
                "sub_field": "inception_date",
                "expected_value": "2022 年 8 月 8 日",
                "confidence": "high",
                "source": "年报2024 §2 page-5 page-5-table-0 inception_date",
            }
        ],
    )
    records = [
        _snapshot_record(
            "profile",
            "basic_identity",
            value_present=True,
            anchor_present=True,
            comparable_values={"inception_date": "2022年8月8日"},
        )
    ]

    summary = compare_snapshot_correctness(records=records, golden_answer_path=golden_path)

    assert summary.comparable_records == 1
    assert summary.matched_records == 1
    assert summary.record_results[0].status == CORRECTNESS_MATCH
    assert summary.record_results[0].normalized_expected == "2022年8月8日"
    assert summary.record_results[0].normalized_actual == "2022年8月8日"


def test_compare_snapshot_correctness_keeps_non_date_basic_identity_spacing(
    tmp_path: Path,
) -> None:
    """验证 basic_identity 非日期字符串不会被中文日期规则过度归一化。

    Args:
        tmp_path: pytest 临时目录 fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当非日期字符串被错误移除空格时抛出。
    """

    golden_path = _golden_answer_json_from_records(
        tmp_path,
        records=[
            {
                "fund_code": "004393",
                "field_name": "basic_identity",
                "sub_field": "inception_date",
                "expected_value": "成立 日期 待确认",
                "confidence": "high",
                "source": "年报2024 §2 page-5 page-5-table-0 inception_date",
            }
        ],
    )
    records = [
        _snapshot_record(
            "profile",
            "basic_identity",
            value_present=True,
            anchor_present=True,
            comparable_values={"inception_date": "成立日期待确认"},
        )
    ]

    summary = compare_snapshot_correctness(records=records, golden_answer_path=golden_path)

    assert summary.comparable_records == 1
    assert summary.mismatched_records == 1
    assert summary.record_results[0].status == CORRECTNESS_MISMATCH
    assert summary.record_results[0].normalized_expected == "成立 日期 待确认"
    assert summary.record_results[0].normalized_actual == "成立日期待确认"


def test_compare_snapshot_correctness_preserves_ascii_word_spacing_for_benchmark(
    tmp_path: Path,
) -> None:
    """验证 benchmark 归一化不移除 ASCII 单词间空格。

    Args:
        tmp_path: pytest 临时目录 fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 ASCII word spacing 被错误移除时抛出。
    """

    golden_path = _golden_answer_json_from_records(
        tmp_path,
        records=[
            {
                "fund_code": "004393",
                "field_name": "benchmark",
                "sub_field": "benchmark_name",
                "expected_value": "MSCI China Index",
                "confidence": "high",
                "source": "年报2024 §2 page-5",
            }
        ],
    )
    records = [
        _snapshot_record(
            "profile",
            "benchmark",
            value_present=True,
            anchor_present=True,
            comparable_values={"benchmark_name": "MSCIChinaIndex"},
        )
    ]

    summary = compare_snapshot_correctness(records=records, golden_answer_path=golden_path)

    assert summary.record_results[0].status == CORRECTNESS_MISMATCH
    assert summary.record_results[0].normalized_expected == "msci china index"
    assert summary.record_results[0].normalized_actual == "mscichinaindex"


def test_compare_snapshot_correctness_matches_composite_index_profile_scalars(
    tmp_path: Path,
) -> None:
    """验证复合指数画像 golden 只按计划内 scalar 子字段匹配。

    Args:
        tmp_path: pytest 临时目录 fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当非计划字段进入 correctness 分母或 scalar 不匹配时抛出。
    """

    golden_path = _golden_answer_json_from_records(
        tmp_path,
        records=_composite_index_profile_golden_records("004194"),
    )
    records = [
        _snapshot_record(
            "profile",
            "index_profile",
            fund_code="004194",
            classified_fund_type="enhanced_index",
            value_present=True,
            anchor_present=True,
            comparable_values={
                "benchmark_text": "中证1000指数收益率×95%+同期银行活期存款利率（税后）×5%",
                "benchmark_identity_status": "composite",
                "methodology_availability": "benchmark_only",
                "constituents_availability": "benchmark_only",
                "source_tier": "benchmark_context",
            },
        )
    ]

    summary = compare_snapshot_correctness(records=records, golden_answer_path=golden_path)
    result_keys = {
        (row.field_name, row.sub_field, row.status) for row in summary.record_results
    }

    assert summary.status == CORRECTNESS_STATUS_AVAILABLE
    assert summary.coverage_scope == CORRECTNESS_COVERAGE_COVERED
    assert summary.comparable_records == 5
    assert summary.matched_records == 5
    assert summary.mismatched_records == 0
    assert summary.unavailable_records == 0
    assert result_keys == {
        ("index_profile", "benchmark_text", CORRECTNESS_MATCH),
        ("index_profile", "benchmark_identity_status", CORRECTNESS_MATCH),
        ("index_profile", "methodology_availability", CORRECTNESS_MATCH),
        ("index_profile", "constituents_availability", CORRECTNESS_MATCH),
        ("index_profile", "source_tier", CORRECTNESS_MATCH),
    }


def test_compare_snapshot_correctness_flags_composite_index_scalar_mismatch(
    tmp_path: Path,
) -> None:
    """验证复合指数画像 scalar golden 会捕获 correctness 退化。

    Args:
        tmp_path: pytest 临时目录 fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 source_tier mismatch 未进入 FQ1 输入时抛出。
    """

    golden_path = _golden_answer_json_from_records(
        tmp_path,
        records=_composite_index_profile_golden_records("004194"),
    )
    records = [
        _snapshot_record(
            "profile",
            "index_profile",
            fund_code="004194",
            classified_fund_type="enhanced_index",
            value_present=True,
            anchor_present=True,
            comparable_values={
                "benchmark_text": "中证1000指数收益率×95%+同期银行活期存款利率（税后）×5%",
                "benchmark_identity_status": "composite",
                "methodology_availability": "benchmark_only",
                "constituents_availability": "benchmark_only",
                "source_tier": "missing",
            },
        )
    ]

    summary = compare_snapshot_correctness(records=records, golden_answer_path=golden_path)
    mismatch = next(row for row in summary.record_results if row.status == CORRECTNESS_MISMATCH)

    assert summary.comparable_records == 5
    assert summary.matched_records == 4
    assert summary.mismatched_records == 1
    assert mismatch.field_name == "index_profile"
    assert mismatch.sub_field == "source_tier"
    assert mismatch.expected_value == "benchmark_context"
    assert mismatch.actual_value == "missing"


def test_run_extraction_score_writes_correctness_mismatch(tmp_path: Path) -> None:
    """验证 run_extraction_score 会把 strict golden answer mismatch 写入 score.json。

    Args:
        tmp_path: pytest 临时目录 fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 score.json 缺少 correctness mismatch 时抛出。
    """

    snapshot_path = tmp_path / "snapshot.jsonl"
    snapshot_path.write_text(
        json.dumps(
            _snapshot_record(
                "profile",
                "classified_fund_type",
                value_present=True,
                anchor_present=True,
                classified_fund_type="index_fund",
            ),
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )
    golden_path = _golden_answer_json(tmp_path, expected_fund_type="active_fund")

    result = run_extraction_score(
        snapshot_path=snapshot_path,
        source_csv=Path("docs/code_20260519.csv"),
        output_dir=tmp_path / "score-output",
        golden_answer_path=golden_path,
    )

    score_payload = json.loads(result.score_json_path.read_text(encoding="utf-8"))
    mismatch_rows = [
        row
        for row in score_payload["correctness"]["record_results"]
        if row["status"] == CORRECTNESS_MISMATCH
    ]
    assert score_payload["correctness"]["status"] == CORRECTNESS_STATUS_AVAILABLE
    assert score_payload["correctness"]["coverage_scope"] == CORRECTNESS_COVERAGE_PARTIALLY_COVERED
    assert score_payload["correctness"]["coverage_required"] is False
    assert score_payload["correctness"]["covered_fund_codes"] == ["004393"]
    assert score_payload["correctness"]["comparable_records"] == 1
    assert score_payload["correctness"]["mismatched_records"] == 1
    assert mismatch_rows[0]["expected_value"] == "active_fund"
    assert mismatch_rows[0]["actual_value"] == "index_fund"


def test_select_minimal_golden_set_uses_only_csv_codes_and_excludes_money_market() -> None:
    """验证最小 golden set 只从真实 CSV 选码，包含必需类别并排除货币基金。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 golden set 不符合 P4-S2 选择规则时抛出。
    """

    source_csv = Path("docs/code_20260519.csv")
    selection = select_minimal_golden_set(source_csv)
    selected_codes = {record.fund_code for record in selection.records}
    selected_categories = {record.app_category for record in selection.records}
    csv_codes = _csv_codes(source_csv)

    assert MANDATORY_GOLDEN_CODE in selected_codes
    assert selected_codes <= csv_codes
    assert MONEY_MARKET_CATEGORY not in selected_categories
    assert EXCLUDED_GOLDEN_CATEGORIES == (MONEY_MARKET_CATEGORY,)
    assert selection.excluded_categories == (MONEY_MARKET_CATEGORY,)
    assert {"黄金类", "海外股票类", "海外债券/稳健类", "国内债券类"} <= selected_categories
    assert sum(1 for record in selection.records if record.app_category == "国内股票类") >= 2


def _single_bond_issue(bond_risk_record: dict[str, object]) -> object:
    """构造单只债基评分输入并返回唯一债券风险缺口 issue。

    Args:
        bond_risk_record: 待测试的 `bond_risk_evidence` snapshot 行。

    Returns:
        唯一 `bond_risk_evidence_missing` issue。

    Raises:
        AssertionError: 当 issue 数量不为 1 时抛出。
    """

    records = [
        _snapshot_record(
            "profile",
            "classified_fund_type",
            fund_code="006597",
            app_category="国内债券类",
            classified_fund_type="bond_fund",
            value_present=True,
            anchor_present=True,
        ),
        _snapshot_record(
            "holdings",
            "holdings_snapshot",
            fund_code="006597",
            app_category="国内债券类",
            classified_fund_type="bond_fund",
            value_present=True,
            anchor_present=True,
        ),
        bond_risk_record,
    ]
    issues = derive_score_applicability_issues(records)
    assert len(issues) == 1
    return issues[0]


def _bond_risk_snapshot_record(
    *,
    fund_code: str = "006597",
    report_year: int = 2024,
    app_category: str = "国内债券类",
    classified_fund_type: str = "bond_fund",
    value_present: bool = True,
    anchor_present: bool,
    contract_status: str | None,
    satisfied_groups: tuple[str, ...] = (),
    missing_groups: tuple[str, ...] = (),
    weak_groups: tuple[str, ...] = (),
    ambiguous_groups: tuple[str, ...] = (),
) -> dict[str, object]:
    """构造 Slice 4 结构化债券风险 snapshot 记录。

    Args:
        fund_code: 基金代码。
        report_year: 年报年份。
        app_category: App 类别。
        classified_fund_type: 系统识别基金类型。
        value_present: 是否存在字段值。
        anchor_present: 是否存在年报证据锚点。
        contract_status: 债券风险证据契约状态。
        satisfied_groups: 已满足证据组。
        missing_groups: 缺失证据组。
        weak_groups: 弱证据组。
        ambiguous_groups: 歧义证据组。

    Returns:
        带 Slice 4 结构化字段的 snapshot 字典。

    Raises:
        无显式抛出。
    """

    record = _snapshot_record(
        "risk",
        "bond_risk_evidence",
        fund_code=fund_code,
        report_year=report_year,
        app_category=app_category,
        classified_fund_type=classified_fund_type,
        value_present=value_present,
        anchor_present=anchor_present,
    )
    record.update(
        {
            "bond_risk_contract_status": contract_status,
            "bond_risk_satisfied_groups": satisfied_groups,
            "bond_risk_missing_groups": missing_groups,
            "bond_risk_weak_groups": weak_groups,
            "bond_risk_ambiguous_groups": ambiguous_groups,
        }
    )
    return record


def _snapshot_record(
    field_group: str,
    field_name: str,
    *,
    fund_code: str = "004393",
    report_year: int = 2024,
    app_category: str = "国内股票类",
    value_present: bool,
    anchor_present: bool,
    classified_fund_type: str = "active_fund",
    comparable_values: dict[str, str] | None = None,
    include_source_provenance: bool = False,
    extra_fields: dict[str, object] | None = None,
) -> dict[str, object]:
    """构造测试用 snapshot 记录。

    Args:
        field_group: 字段组。
        field_name: 字段名。
        fund_code: 基金代码。
        report_year: 年报年份。
        app_category: App 类别。
        value_present: 是否存在字段值。
        anchor_present: 是否存在证据锚点。
        classified_fund_type: 系统识别基金类型。
        comparable_values: correctness 可比子字段；为空时模拟旧 snapshot。
        include_source_provenance: 是否追加 additive 公共来源 provenance 字段。
        extra_fields: 测试专用额外行级字段。

    Returns:
        符合评分最小输入契约的字典。

    Raises:
        无显式抛出。
    """

    record: dict[str, object] = {
        "fund_code": fund_code,
        "fund_name": f"测试基金{fund_code}",
        "app_category": app_category,
        "report_year": report_year,
        "classified_fund_type": classified_fund_type,
        "field_group": field_group,
        "field_name": field_name,
        "value_present": value_present,
        "anchor_present": anchor_present,
    }
    if comparable_values is not None:
        record["comparable_values"] = comparable_values
    if include_source_provenance:
        record.update(_PUBLIC_SOURCE_PROVENANCE_PAYLOAD)
    if extra_fields is not None:
        record.update(extra_fields)
    return record


def _golden_answer_json(
    tmp_path: Path,
    *,
    expected_fund_type: str,
    skipped_fields: list[str] | None = None,
) -> Path:
    """写入测试用 strict golden answer JSON。

    Args:
        tmp_path: pytest 临时目录 fixture。
        expected_fund_type: golden answer 中的基金类型真值。
        skipped_fields: 明确跳过字段。

    Returns:
        strict JSON 路径。

    Raises:
        OSError: 写入失败时抛出。
    """

    records = [
        {
            "fund_code": "004393",
            "report_year": 2024,
            "field_name": "classified_fund_type",
            "sub_field": "fund_type",
            "expected_value": expected_fund_type,
            "confidence": "high",
            "source": "年报2024 §2 page-5",
        },
        {
            "fund_code": "004393",
            "report_year": 2024,
            "field_name": "basic_identity",
            "sub_field": "fund_name",
            "expected_value": "测试基金",
            "confidence": "high",
            "source": "年报2024 §2 page-5",
        },
    ]
    return _golden_answer_json_from_records(
        tmp_path, records=records, skipped_fields=skipped_fields
    )


def _golden_answer_json_from_records(
    tmp_path: Path,
    *,
    records: list[dict[str, object]],
    skipped_fields: list[str] | None = None,
) -> Path:
    """按指定记录写入测试用 strict golden answer JSON。

    Args:
        tmp_path: pytest 临时目录 fixture。
        records: golden answer 有效记录。
        skipped_fields: 明确跳过字段。

    Returns:
        strict JSON 路径。

    Raises:
        OSError: 写入失败时抛出。
    """

    path = tmp_path / "golden-answer.json"
    fund_code = records[0]["fund_code"] if records else "004393"
    report_year = int(records[0].get("report_year", "2024")) if records else 2024
    path.write_text(
        json.dumps(
            {
                "schema_version": "fund-agent.golden-answer.v1",
                "source_markdown": "fixture.md",
                "fund_count": 1,
                "record_count": len(records),
                "funds": [
                    {
                        "fund_code": fund_code,
                        "report_year": report_year,
                        "title": "测试基金（国内股票类）",
                        "records": records,
                        "skipped_fields": skipped_fields or [],
                    }
                ],
                "records": records,
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    return path


def _composite_index_profile_golden_records(fund_code: str) -> list[dict[str, str]]:
    """构造 P16-S2 复合指数画像测试用 golden records。

    Args:
        fund_code: 基金代码。

    Returns:
        只包含计划内 scalar 子字段的 strict golden records。

    Raises:
        无显式抛出。
    """

    return [
        {
            "fund_code": fund_code,
            "field_name": "index_profile",
            "sub_field": "benchmark_text",
            "expected_value": "中证1000指数收益率×95%+同期银行活期存款利率（税后）×5%",
            "confidence": "high",
            "source": "年报2024 §2 page-5 page-5-table-1 benchmark",
        },
        {
            "fund_code": fund_code,
            "field_name": "index_profile",
            "sub_field": "benchmark_identity_status",
            "expected_value": "composite",
            "confidence": "high",
            "source": "年报2024 §2 page-5 page-5-table-1 benchmark",
        },
        {
            "fund_code": fund_code,
            "field_name": "index_profile",
            "sub_field": "methodology_availability",
            "expected_value": "benchmark_only",
            "confidence": "high",
            "source": "年报2024 §2 page-5 page-5-table-1 benchmark",
        },
        {
            "fund_code": fund_code,
            "field_name": "index_profile",
            "sub_field": "constituents_availability",
            "expected_value": "benchmark_only",
            "confidence": "high",
            "source": "年报2024 §2 page-5 page-5-table-1 benchmark",
        },
        {
            "fund_code": fund_code,
            "field_name": "index_profile",
            "sub_field": "source_tier",
            "expected_value": "benchmark_context",
            "confidence": "high",
            "source": "年报2024 §2 page-5 page-5-table-1 benchmark",
        },
    ]


def _csv_codes(source_csv: Path) -> set[str]:
    """读取 CSV 中所有基金代码。

    Args:
        source_csv: 精选基金池 CSV 路径。

    Returns:
        CSV 中的基金代码集合。

    Raises:
        OSError: 文件读取失败时抛出。
    """

    return {fund.fund_code for fund in load_selected_funds(source_csv)}
