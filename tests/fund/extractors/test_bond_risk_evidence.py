"""债券风险证据模型契约测试。"""

from __future__ import annotations

from dataclasses import replace
from datetime import date, datetime, timezone
from decimal import Decimal

import pytest

import fund_agent.fund.extractors.bond_risk_evidence as bond_risk_module
from fund_agent.fund.data.nav_metrics import NavMaxDrawdownMetric
from fund_agent.fund.data.nav_models import NavDataContractError, NavSourceMetadata
from fund_agent.fund.documents.models import DocumentKey, ParsedAnnualReport, ParsedTable, ReportSection
from fund_agent.fund.extractors.bond_risk_evidence import extract_bond_risk_evidence
from fund_agent.fund.extractors.models import (
    BOND_RISK_EVIDENCE_CONTRACT_ID,
    BOND_RISK_EVIDENCE_GROUP_IDS,
    BondRiskEvidenceAnchorRef,
    BondRiskEvidenceGroupId,
    BondRiskEvidenceGroupRecord,
    BondRiskEvidenceValue,
    EvidenceAnchor,
    validate_bond_risk_evidence_value,
)


def test_complete_seven_group_bond_risk_evidence_value_validates() -> None:
    """完整七组债券风险证据值应通过模板第 6 章契约校验。"""

    value = _complete_value()

    validate_bond_risk_evidence_value(value)

    assert value.satisfied_group_ids == BOND_RISK_EVIDENCE_GROUP_IDS
    assert value.missing_group_ids == ()
    assert value.weak_group_ids == ()
    assert value.ambiguous_group_ids == ()
    assert value.contract_status == "satisfied"


def test_missing_anchor_for_accepted_group_fails_validation() -> None:
    """accepted 组缺少可解析年报锚点时必须失败。"""

    value = _complete_value()
    broken_group = replace(value.groups[0], source_anchor_ids=("missing-anchor",))
    broken_value = replace(value, groups=(broken_group, *value.groups[1:]))

    with pytest.raises(ValueError, match="引用缺失锚点"):
        validate_bond_risk_evidence_value(broken_value)


def test_incomplete_group_set_fails_validation() -> None:
    """风险组不是恰好七组时必须失败。"""

    value = _complete_value()
    broken_value = replace(value, groups=value.groups[:-1])

    with pytest.raises(ValueError, match="恰好包含七个"):
        validate_bond_risk_evidence_value(broken_value)


def test_duplicate_group_id_fails_validation() -> None:
    """模板第 6 章风险组 ID 重复时必须失败。"""

    value = _complete_value()
    duplicate_group = replace(value.groups[1], group_id=value.groups[0].group_id)
    broken_value = replace(value, groups=(value.groups[0], duplicate_group, *value.groups[2:]))

    with pytest.raises(ValueError, match="group_id 不允许重复"):
        validate_bond_risk_evidence_value(broken_value)


def test_caller_provided_derived_group_ids_must_match_statuses() -> None:
    """派生组 ID 与状态不一致时必须拒绝调用方提供值。"""

    value = _complete_value()
    broken_value = replace(value, satisfied_group_ids=value.satisfied_group_ids[:-1])

    with pytest.raises(ValueError, match="satisfied_group_ids 与组状态不一致"):
        validate_bond_risk_evidence_value(broken_value)


def test_caller_provided_weak_group_ids_must_match_statuses() -> None:
    """weak_group_ids 与状态不一致时必须拒绝调用方提供值。"""

    value = _complete_value(
        overrides={
            "drawdown_stress": _group_record(
                "drawdown_stress",
                status="weak",
                strength="qualitative_control_intent",
                measurement_kind="control_intent",
            )
        }
    )
    broken_value = replace(value, weak_group_ids=())

    with pytest.raises(ValueError, match="weak_group_ids 与组状态不一致"):
        validate_bond_risk_evidence_value(broken_value)


def test_caller_provided_ambiguous_group_ids_must_match_statuses() -> None:
    """ambiguous_group_ids 与状态不一致时必须拒绝调用方提供值。"""

    value = _complete_value(
        overrides={
            "credit_risk": _group_record(
                "credit_risk",
                status="ambiguous",
                strength="ambiguous",
                measurement_kind="risk_disclosure",
            )
        }
    )
    broken_value = replace(value, ambiguous_group_ids=())

    with pytest.raises(ValueError, match="ambiguous_group_ids 与组状态不一致"):
        validate_bond_risk_evidence_value(broken_value)


def test_cross_group_anchor_reference_fails_validation() -> None:
    """风险组引用其他组锚点时必须失败。"""

    value = _complete_value()
    source_group = value.groups[0]
    other_group = value.groups[1]
    broken_group = replace(source_group, source_anchor_ids=other_group.source_anchor_ids)
    broken_value = replace(value, groups=(broken_group, *value.groups[1:]))

    with pytest.raises(ValueError, match="引用其他风险组锚点"):
        validate_bond_risk_evidence_value(broken_value)


@pytest.mark.parametrize(
    ("anchor_id", "message"),
    (
        ("bond-risk:006597:2024:duration_rate_risk", "anchor_id 格式错误"),
        ("bond-risk:000000:2024:duration_rate_risk:1", "anchor_id 基金代码不匹配"),
        ("bond-risk:006597:2023:duration_rate_risk:1", "anchor_id 年份不匹配"),
    ),
)
def test_malformed_or_wrong_anchor_id_fails_validation(anchor_id: str, message: str) -> None:
    """格式错误或归属不匹配的锚点 ID 必须失败。"""

    value = _complete_value()
    broken_anchor = replace(value.anchors[0], anchor_id=anchor_id)
    broken_value = replace(value, anchors=(broken_anchor, *value.anchors[1:]))

    with pytest.raises(ValueError, match=message):
        validate_bond_risk_evidence_value(broken_value)


def test_invalid_status_fails_validation() -> None:
    """不支持的模板第 6 章证据状态必须失败。"""

    value = _complete_value()
    broken_group = replace(value.groups[0], status="unsupported_status")
    broken_value = replace(value, groups=(broken_group, *value.groups[1:]))

    with pytest.raises(ValueError, match="status 不受支持"):
        validate_bond_risk_evidence_value(broken_value)


def test_invalid_strength_fails_validation() -> None:
    """不支持的模板第 6 章证据强度必须失败。"""

    value = _complete_value()
    broken_group = replace(value.groups[0], strength="unsupported_strength")
    broken_value = replace(value, groups=(broken_group, *value.groups[1:]))

    with pytest.raises(ValueError, match="strength 不受支持"):
        validate_bond_risk_evidence_value(broken_value)


def test_weak_drawdown_control_record_validates_but_is_unsatisfied() -> None:
    """回撤控制意图只能作为弱证据，不能进入 satisfied 组。"""

    value = _complete_value(
        overrides={
            "drawdown_stress": _group_record(
                "drawdown_stress",
                status="weak",
                strength="qualitative_control_intent",
                measurement_kind="control_intent",
            )
        }
    )

    validate_bond_risk_evidence_value(value)

    assert "drawdown_stress" not in value.satisfied_group_ids
    assert value.weak_group_ids == ("drawdown_stress",)
    assert value.contract_status == "partial"


def test_quantitative_derived_drawdown_requires_derived_metric_kind() -> None:
    """验证派生定量回撤证据必须使用 derived_metric，见模板第 6 章“核心风险”。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当语义矛盾组合通过契约校验时抛出。
    """

    good_group = _group_record(
        "drawdown_stress",
        status="accepted",
        strength="quantitative_derived",
        measurement_kind="derived_metric",
    )
    good_value = _complete_value(overrides={"drawdown_stress": good_group})

    validate_bond_risk_evidence_value(good_value)

    for measurement_kind in ("actual_metric", "actual_exposure", "risk_disclosure"):
        bad_group = replace(good_group, measurement_kind=measurement_kind)
        bad_value = _complete_value(overrides={"drawdown_stress": bad_group})
        with pytest.raises(ValueError, match="quantitative_derived 必须使用 derived_metric"):
            validate_bond_risk_evidence_value(bad_value)


def test_explicit_absence_convertible_equity_record_is_accepted() -> None:
    """可转债和权益暴露显式缺席可作为 accepted_absence 正向证据。"""

    value = _complete_value()
    group = _group_by_id(value, "convertible_bond_equity_exposure")

    validate_bond_risk_evidence_value(value)

    assert group.status == "accepted_absence"
    assert group.strength == "quantitative_absence"
    assert group.measurement_kind == "explicit_absence"
    assert "convertible_bond_equity_exposure" in value.satisfied_group_ids


def test_table_backed_credit_risk_is_accepted_with_row_level_anchor() -> None:
    """信用评级表格行应形成模板第 6 章信用风险 accepted 证据。"""

    report = _build_report(
        raw_text=_base_bond_raw_text(),
        tables=(
            ParsedTable(
                page_number=53,
                table_index=0,
                headers=("长期信用评级", "本期末公允价值", "占基金资产净值比例"),
                rows=(("AAA 债券", "1,000,000.00", "80.00%"), ("合计", "1,000,000.00", "80.00%")),
            ),
        ),
    )

    field = extract_bond_risk_evidence(report, "bond_fund")
    assert field.value is not None
    group = _group_by_id(field.value, "credit_risk")

    assert group.status == "accepted"
    assert group.strength == "quantitative_direct"
    assert group.measurement_kind == "actual_exposure"
    assert group.metric_name == "持仓评级分布"
    assert group.source_anchor_ids == (
        "bond-risk:006597:2024:credit_risk:1",
        "bond-risk:006597:2024:credit_risk:2",
    )
    anchor = _anchor_ref_by_id(field.value, group.source_anchor_ids[0])
    assert anchor.table_id == "page-53-table-0"
    assert anchor.row_locator.startswith("row:1:")


def test_holding_rating_distribution_table_is_credit_risk_portfolio_exposure_not_fund_rating() -> None:
    """持仓评级分布表应作为组合信用暴露证据，不能写成基金自身评级。"""

    report = _build_report(
        raw_text=_base_bond_raw_text(),
        tables=(
            _rating_distribution_table(
                page_number=54,
                table_index=0,
                headers=("长期信用评级", "本期末公允价值", "上年度末公允价值"),
                rows=(
                    ("AAA", "10,000,000.00", "9,000,000.00"),
                    ("AAA以下", "2,000,000.00", "1,000,000.00"),
                    ("未评级", "500,000.00", "-"),
                    ("合计", "12,500,000.00", "10,000,000.00"),
                ),
            ),
        ),
    )

    field = extract_bond_risk_evidence(report, "bond_fund")
    assert field.value is not None
    group = _group_by_id(field.value, "credit_risk")
    combined_text = " ".join(
        text
        for text in (group.summary, group.metric_name or "", group.metric_value or "")
    )

    assert group.status == "accepted"
    assert group.strength == "quantitative_direct"
    assert group.measurement_kind == "actual_exposure"
    assert group.metric_name == "持仓评级分布"
    assert "持有债券/证券" in group.summary
    assert "holding_rating_distribution" in (group.metric_value or "")
    assert "合计=12500000" in (group.metric_value or "")
    assert "基金评级" not in combined_text
    assert "本基金评级" not in combined_text
    anchor = _anchor_ref_by_id(field.value, group.source_anchor_ids[0])
    assert anchor.page_number == 54
    assert anchor.table_id == "page-54-table-0"
    assert anchor.row_locator.startswith("row:1:")


def test_credit_risk_uses_current_period_column_when_prior_period_appears_first() -> None:
    """评级分布表前期列在前时，metric_value 必须使用本期末金额列。"""

    report = _build_report(
        raw_text=_base_bond_raw_text(),
        tables=(
            _rating_distribution_table(
                page_number=54,
                table_index=0,
                headers=("长期信用评级", "上年度末公允价值", "本期末公允价值"),
                rows=(
                    ("AAA", "9,000,000.00", "10,000,000.00"),
                    ("合计", "9,000,000.00", "10,000,000.00"),
                ),
            ),
        ),
    )

    field = extract_bond_risk_evidence(report, "bond_fund")
    assert field.value is not None
    group = _group_by_id(field.value, "credit_risk")
    anchor = _extractor_anchor_by_locator(field, "row:1:AAA")

    assert group.status == "accepted"
    assert "AAA=10000000" in (group.metric_value or "")
    assert "AAA=9000000" not in (group.metric_value or "")
    assert anchor.note == "AAA=10,000,000.00"


def test_fund_own_rating_table_is_rejected_for_credit_risk() -> None:
    """本基金评级语义即使出现 AAA 行，也不能满足持仓信用风险组。"""

    report = _build_report(
        raw_text=_base_bond_raw_text(section_four_extra="本基金主要投资中高等级信用债。"),
        tables=(
            ParsedTable(
                page_number=54,
                table_index=0,
                headers=("本基金评级", "评级机构", "评级结果"),
                rows=(("基金评级信息", "示例机构", "AAA"), ("合计", "1", "AAA")),
            ),
        ),
    )

    field = extract_bond_risk_evidence(report, "bond_fund")
    assert field.value is not None
    group = _group_by_id(field.value, "credit_risk")

    assert group.status == "weak"
    assert group.na_reason == "credit_risk_table_not_found"
    assert "credit_risk" not in field.value.satisfied_group_ids


def test_fund_own_credit_rating_table_is_rejected_for_credit_risk() -> None:
    """基金自身信用评级表即使含信用评级字样，也不能被当作持仓评级分布。"""

    report = _build_report(
        raw_text=_base_bond_raw_text(section_four_extra="本基金主要投资中高等级信用债。"),
        tables=(
            ParsedTable(
                page_number=54,
                table_index=0,
                headers=("本基金信用评级", "本期末公允价值"),
                rows=(("AAA", "1,000,000.00"), ("合计", "1,000,000.00")),
            ),
        ),
    )

    field = extract_bond_risk_evidence(report, "bond_fund")
    assert field.value is not None
    group = _group_by_id(field.value, "credit_risk")

    assert group.status == "weak"
    assert group.na_reason == "credit_risk_table_not_found"
    assert "credit_risk" not in field.value.satisfied_group_ids


def test_compound_rating_labels_are_matched_without_loose_substring_false_positive() -> None:
    """复合持仓标签可识别，但不把 AAAA 这类非评级标签误识别为 AAA/A。"""

    report = _build_report(
        raw_text=_base_bond_raw_text(),
        tables=(
            _rating_distribution_table(
                page_number=54,
                table_index=0,
                headers=("长期信用评级", "本期末公允价值"),
                rows=(
                    ("AAA 债券", "1,000.00"),
                    ("AAAA 说明行", "9,999.00"),
                    ("合计", "1,000.00"),
                ),
            ),
        ),
    )

    field = extract_bond_risk_evidence(report, "bond_fund")
    assert field.value is not None
    group = _group_by_id(field.value, "credit_risk")

    assert group.status == "accepted"
    assert "AAA=1000" in (group.metric_value or "")
    assert "9999" not in (group.metric_value or "")


def test_multiple_holding_rating_distribution_tables_preserve_all_anchors() -> None:
    """短期和长期持仓评级分布表都有效时，应保留所有表的行级锚点。"""

    report = _build_report(
        raw_text=_base_bond_raw_text(),
        tables=(
            _rating_distribution_table(
                page_number=54,
                table_index=0,
                headers=("短期信用评级", "本期末公允价值"),
                rows=(("A-1", "1,000.00"), ("合计", "1,000.00")),
            ),
            _rating_distribution_table(
                page_number=55,
                table_index=1,
                headers=("长期信用评级", "本期末公允价值"),
                rows=(("AAA", "2,000.00"), ("未评级", "300.00"), ("合计", "2,300.00")),
            ),
        ),
    )

    field = extract_bond_risk_evidence(report, "bond_fund")
    assert field.value is not None
    group = _group_by_id(field.value, "credit_risk")
    anchors = tuple(_anchor_ref_by_id(field.value, anchor_id) for anchor_id in group.source_anchor_ids)

    assert group.status == "accepted"
    assert len(group.source_anchor_ids) == 5
    assert {anchor.table_id for anchor in anchors} == {"page-54-table-0", "page-55-table-1"}
    assert "A-1=1000" in (group.metric_value or "")
    assert "合计=1000" in (group.metric_value or "")


def test_credit_risk_qualitative_text_without_rating_distribution_remains_weak() -> None:
    """只有信用策略文本时，信用风险仍为弱证据。"""

    report = _build_report(
        raw_text=_base_bond_raw_text(section_four_extra="本基金主要投资中高等级信用债，控制信用风险。"),
        tables=(),
    )

    field = extract_bond_risk_evidence(report, "bond_fund")
    assert field.value is not None
    group = _group_by_id(field.value, "credit_risk")

    assert group.status == "weak"
    assert group.strength == "qualitative_direct"
    assert group.na_reason == "credit_risk_table_not_found"
    assert "credit_risk" not in field.value.satisfied_group_ids


def test_credit_risk_percentage_only_table_not_accepted() -> None:
    """评级表只有百分比列时不能形成 accepted 锚点。"""

    report = _build_report(
        raw_text=_base_bond_raw_text(section_four_extra="本基金控制信用风险。"),
        tables=(
            _rating_distribution_table(
                page_number=54,
                table_index=0,
                headers=("长期信用评级", "占基金资产净值比例"),
                rows=(("AAA", "80.00%"), ("合计", "80.00%")),
            ),
        ),
    )

    field = extract_bond_risk_evidence(report, "bond_fund")
    assert field.value is not None
    group = _group_by_id(field.value, "credit_risk")

    assert group.status == "weak"
    assert group.source_anchor_ids
    assert "credit_risk" not in field.value.satisfied_group_ids


def test_flexible_leverage_strategy_text_alone_is_weak() -> None:
    """杠杆策略文本没有回购/融资行时只能作为弱证据。"""

    report = _build_report(
        raw_text=_base_bond_raw_text(
            section_four_extra="本基金报告期内灵活运用杠杆策略，注重组合收益弹性。",
        ),
        tables=(),
    )

    field = extract_bond_risk_evidence(report, "bond_fund")
    assert field.value is not None
    group = _group_by_id(field.value, "leverage_liquidity")

    assert group.status == "weak"
    assert group.strength == "qualitative_direct"
    assert group.na_reason == "repo_or_liquidity_table_not_found"
    assert "leverage_liquidity" in field.value.weak_group_ids
    assert "leverage_liquidity" not in field.value.satisfied_group_ids


def test_repo_table_row_plus_liquidity_text_satisfies_leverage_liquidity() -> None:
    """回购表格行配合流动性风险文本可满足模板第 6 章杠杆/流动性组。"""

    report = _build_report(
        raw_text=_base_bond_raw_text(section_four_extra="管理人严格控制流动性风险，保持组合流动性。"),
        tables=(
            ParsedTable(
                page_number=59,
                table_index=1,
                headers=("项目", "金额"),
                rows=(("买入返售金融资产-回购", "10,000,000.00"),),
            ),
        ),
    )

    field = extract_bond_risk_evidence(report, "bond_fund")
    assert field.value is not None
    group = _group_by_id(field.value, "leverage_liquidity")

    assert group.status == "accepted"
    assert group.strength == "quantitative_direct"
    assert group.measurement_kind == "actual_exposure"
    assert len(group.source_anchor_ids) == 2
    assert "leverage_liquidity" in field.value.satisfied_group_ids


def test_drawdown_control_text_alone_is_weak() -> None:
    """回撤控制意图不能被提升为最大回撤或压力测试证据。"""

    report = _build_report(
        raw_text=_base_bond_raw_text(section_four_extra="本基金力争保持净值稳定并控制回撤。"),
        tables=(),
    )

    field = extract_bond_risk_evidence(report, "bond_fund")
    assert field.value is not None
    group = _group_by_id(field.value, "drawdown_stress")

    assert group.status == "weak"
    assert group.strength == "qualitative_control_intent"
    assert group.measurement_kind == "control_intent"
    assert "drawdown_stress" in field.value.weak_group_ids
    assert "drawdown_stress" not in field.value.satisfied_group_ids


def test_nav_derived_drawdown_metric_satisfies_drawdown_group() -> None:
    """验证 NAV 派生最大回撤可作为 drawdown_stress 派生定量证据。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当派生指标没有形成 accepted 证据或 provenance 缺失时抛出。
    """

    report = _build_report(
        raw_text=_base_bond_raw_text(section_four_extra="本基金力争保持净值稳定并控制回撤。"),
        tables=(),
    )

    field = extract_bond_risk_evidence(
        report,
        "bond_fund",
        drawdown_metric=_drawdown_metric(),
    )

    assert field.value is not None
    group = _group_by_id(field.value, "drawdown_stress")
    assert group.status == "accepted"
    assert group.strength == "quantitative_derived"
    assert group.summary == "CSRC EID A 类累计净值路径计算 2024 年报期间最大回撤"
    assert group.measurement_kind == "derived_metric"
    assert group.metric_name == "最大回撤"
    assert group.metric_value == "-10.00%"
    assert group.metric_unit == "ratio"
    assert group.period_label == "2024-01-01 至 2024-12-31"
    assert group.na_reason is None
    assert "drawdown_stress" in field.value.satisfied_group_ids
    assert "drawdown_stress" not in field.value.weak_group_ids

    anchor_ref = _anchor_ref_by_id(field.value, group.source_anchor_ids[0])
    extractor_anchor = next(anchor for anchor in field.anchors if anchor.section_id == "derived:nav")
    assert anchor_ref.section_id == "derived:nav"
    assert anchor_ref.row_locator == "metric:max_drawdown:A:2024-01-01:2024-12-31"
    assert anchor_ref.evidence_role == "derived_max_drawdown_metric"
    assert extractor_anchor.source_kind == "derived"
    assert extractor_anchor.note is not None
    for token in (
        "source=CSRC EID",
        "source_name=csrc_eid",
        "source_id=5755:2030-1010",
        "source_url=https://eid.csrc.gov.cn/fund/5755",
        "source_query_params=fund_code=006597,share_class=A",
        "retrieved_at=2026-05-29T00:00:00+00:00",
        "fund_code=006597",
        "share_class=A",
        "date_range=2024-01-01..2024-12-31",
        "record_count=244",
        "nav_type=accumulated_nav",
        "adjusted_basis=accumulated_nav",
        "dividend_adjustment_status=not_applicable",
        "identity_status=verified",
        "calculation_method=max_drawdown_on_accumulated_nav_path",
        "peak_date=2024-03-01",
        "trough_date=2024-04-01",
        "max_drawdown_ratio=-0.10",
    ):
        assert token in extractor_anchor.note


def test_nav_derived_drawdown_metric_summary_uses_report_year() -> None:
    """验证派生最大回撤摘要使用年报上下文年份而非硬编码年份。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当摘要没有使用年报年份时抛出。
    """

    report = _build_report(
        raw_text=_base_bond_raw_text(section_four_extra="本基金力争保持净值稳定并控制回撤。"),
        tables=(),
        year=2023,
    )

    field = extract_bond_risk_evidence(
        report,
        "bond_fund",
        drawdown_metric=_drawdown_metric(),
    )

    assert field.value is not None
    group = _group_by_id(field.value, "drawdown_stress")
    assert group.summary == "CSRC EID A 类累计净值路径计算 2023 年报期间最大回撤"


def test_nav_metric_error_keeps_drawdown_control_text_weak() -> None:
    """验证 NAV 指标失败时，年报回撤控制意图仍只是弱证据。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当弱文本被错误提升为 accepted 时抛出。
    """

    report = _build_report(
        raw_text=_base_bond_raw_text(section_four_extra="本基金力争保持净值稳定并控制回撤。"),
        tables=(),
    )
    field = extract_bond_risk_evidence(
        report,
        "bond_fund",
        drawdown_metric_error=NavDataContractError(
            category="unavailable",
            message="fixture unavailable",
            source="csrc_eid",
            fund_code="006597",
        ),
    )

    assert field.value is not None
    group = _group_by_id(field.value, "drawdown_stress")
    assert group.status == "weak"
    assert group.strength == "qualitative_control_intent"
    assert group.measurement_kind == "control_intent"
    assert group.na_reason == "drawdown_nav_unavailable"
    assert "drawdown_stress" in field.value.weak_group_ids
    assert "drawdown_stress" not in field.value.satisfied_group_ids


def test_share_class_evidence_from_section_two_table() -> None:
    """§2 表格式代码/简称映射应支持 A/C/E/F 全类别聚合。"""

    report = _build_report(
        raw_text=_base_bond_raw_text(),
        tables=(
            _share_class_mapping_table(),
            _share_change_table_ac_ef(),
        ),
    )

    field = extract_bond_risk_evidence(report, "bond_fund")
    assert field.value is not None
    group = _group_by_id(field.value, "redemption_share_pressure")

    assert group.status == "accepted"
    assert "mapping=§2 下属分级基金简称/交易代码表" in (group.metric_value or "")
    assert "A=006597" in (group.metric_value or "")
    assert "C=006598" in (group.metric_value or "")
    assert "E=014217" in (group.metric_value or "")
    assert "F=022176" in (group.metric_value or "")
    mapping_anchors = tuple(anchor for anchor in field.value.anchors if anchor.evidence_role == "share_class_mapping")
    assert len(mapping_anchors) == 1


def test_share_class_evidence_from_section_two_table_with_intervening_rows() -> None:
    """§2 简称行和交易代码行之间有注释/空行时，仍应识别 A/C/E/F 映射。"""

    report = _build_report(
        raw_text=_base_bond_raw_text(),
        tables=(
            _share_class_mapping_table(
                rows=(
                    ("下属分级基金的基金简称", "易方达安悦 A", "易方达安悦 C", "易方达安悦 E", "易方达安悦 F"),
                    ("注：本表披露各份额类别简称", "", "", "", ""),
                    ("", "", "", "", ""),
                    ("下属分级基金的交易代码", "006597", "006598", "014217", "022176"),
                ),
            ),
            _share_change_table_ac_ef(),
        ),
    )

    field = extract_bond_risk_evidence(report, "bond_fund")
    assert field.value is not None
    group = _group_by_id(field.value, "redemption_share_pressure")

    assert group.status == "accepted"
    assert "A=006597" in (group.metric_value or "")
    assert "F=022176" in (group.metric_value or "")


def test_ambiguous_multi_share_class_share_change_stays_ambiguous() -> None:
    """缺少 §2 消歧证据时，多份额类别份额变动表不能满足赎回压力组。"""

    report = _build_report(raw_text=_base_bond_raw_text(), tables=(_share_change_table(),))

    field = extract_bond_risk_evidence(report, "bond_fund")
    assert field.value is not None
    group = _group_by_id(field.value, "redemption_share_pressure")

    assert group.status == "ambiguous"
    assert group.strength == "ambiguous"
    assert group.na_reason == "ambiguous_share_class_selection"
    assert "redemption_share_pressure" in field.value.ambiguous_group_ids
    assert "redemption_share_pressure" not in field.value.satisfied_group_ids


def test_redemption_share_pressure_aggregates_all_a_c_e_f_classes() -> None:
    """赎回压力必须聚合 A/C/E/F 全类别，并保留类别 breakdown 与行锚点。"""

    report = _build_report(
        raw_text=_base_bond_raw_text(
            section_two_extra="下属分级基金的基金简称 易方达安悦 A 易方达安悦 C 易方达安悦 E 易方达安悦 F\n"
            "下属分级基金的交易代码 006597 006598 014217 022176",
        ),
        tables=(_share_change_table_ac_ef(),),
    )

    field = extract_bond_risk_evidence(report, "bond_fund")
    assert field.value is not None
    group = _group_by_id(field.value, "redemption_share_pressure")

    assert group.status == "accepted"
    assert group.strength == "quantitative_direct"
    assert group.measurement_kind == "actual_exposure"
    assert group.metric_name == "A/C/E/F 份额变动汇总"
    assert "all_classes: beginning=3000000" in (group.metric_value or "")
    assert "subscription=1200000" in (group.metric_value or "")
    assert "redemption=1000000" in (group.metric_value or "")
    assert "ending=3200000" in (group.metric_value or "")
    assert "net_change=200000" in (group.metric_value or "")
    assert "A(code=006597" in (group.metric_value or "")
    assert "C(code=006598" in (group.metric_value or "")
    assert "E(code=014217" in (group.metric_value or "")
    assert "F(code=022176" in (group.metric_value or "")
    assert "class_beginning_zero" in (group.metric_value or "")
    assert "column_alignment=explicit_headers" in (group.metric_value or "")
    assert "column_alignment=section2_order_unlabeled_headers" not in (group.metric_value or "")
    row_anchors = tuple(anchor for anchor in field.value.anchors if anchor.section_id == "§10")
    assert len(row_anchors) >= 4


def test_redemption_share_pressure_aligns_real_unlabeled_section_ten_by_section_two_order() -> None:
    """真实 §10 无类别表头可在 §2 同表期末份额校验后按 A/C/E/F 顺序对齐。"""

    report = _build_report(
        raw_text=_base_bond_raw_text(),
        tables=(
            _real_profile_cross_check_table(),
            _real_unlabeled_share_change_table(),
        ),
    )

    field = extract_bond_risk_evidence(report, "bond_fund")
    assert field.value is not None
    group = _group_by_id(field.value, "redemption_share_pressure")
    metric = group.metric_value or ""
    anchors = tuple(_anchor_ref_by_id(field.value, anchor_id) for anchor_id in group.source_anchor_ids)

    assert group.status == "accepted"
    assert group.na_reason is None
    assert "redemption_share_pressure" in field.value.satisfied_group_ids
    assert "A(code=006597" in metric
    assert "C(code=006598" in metric
    assert "E(code=014217" in metric
    assert "F(code=022176" in metric
    assert "beginning=12982005127.5" in metric
    assert "subscription=41674250439.28" in metric
    assert "redemption=44106675403.46" in metric
    assert "ending=10549580163.32" in metric
    assert "net_change=-2432424964.18" in metric
    assert "net_change_ratio=-0.187368" in metric
    assert "class_beginning_zero" in metric
    assert "column_alignment=section2_order_unlabeled_headers" in metric
    assert {anchor.evidence_role for anchor in anchors} >= {
        "share_beginning",
        "subscription",
        "redemption",
        "share_ending",
        "share_class_mapping",
        "share_class_ending_cross_check",
    }
    cross_check_anchor = next(anchor for anchor in anchors if anchor.evidence_role == "share_class_ending_cross_check")
    assert cross_check_anchor.table_id == "page-5-table-0"
    assert cross_check_anchor.row_locator == "rows:9,10,11:share_class_ending_cross_check"


def test_redemption_share_pressure_aligns_real_profile_unit_suffix_newline_values() -> None:
    """真实 §2 profile 期末份额带换行和“份”后缀时仍应通过交叉校验。"""

    report = _build_report(
        raw_text=_base_bond_raw_text(),
        tables=(
            _real_profile_cross_check_table(
                ending_row=(
                    "报告期末下属分级基金的份\n额总额",
                    "5,711,224,267\n.09份",
                    "4,760,029,01\n5.27份",
                    "25,795,859.1\n2份",
                    "52,531,021.8\n4份",
                ),
            ),
            _real_unlabeled_share_change_table(),
        ),
    )

    field = extract_bond_risk_evidence(report, "bond_fund")
    assert field.value is not None
    group = _group_by_id(field.value, "redemption_share_pressure")

    assert group.status == "accepted"
    assert group.na_reason is None
    assert "redemption_share_pressure" in field.value.satisfied_group_ids


def test_redemption_share_pressure_keeps_invalid_unit_suffix_value_fail_closed() -> None:
    """“N/A份”这类非数值不得因单位后缀剥离被解析为合法 Decimal。"""

    assert bond_risk_module._parse_share_decimal("N/A份") is None

    report = _build_report(
        raw_text=_base_bond_raw_text(),
        tables=(
            _real_profile_cross_check_table(
                ending_row=(
                    "报告期末下属分级基金的份额总额",
                    "N/A份",
                    "4,760,029,015.27份",
                    "25,795,859.12份",
                    "52,531,021.84份",
                ),
            ),
            _real_unlabeled_share_change_table(),
        ),
    )

    field = extract_bond_risk_evidence(report, "bond_fund")
    assert field.value is not None
    group = _group_by_id(field.value, "redemption_share_pressure")

    assert group.status == "ambiguous"
    assert group.na_reason == "share_class_ending_cross_check_missing"
    assert "redemption_share_pressure" not in field.value.satisfied_group_ids


def test_redemption_share_pressure_not_a_only() -> None:
    """A 类单列数值不同于全类别合计时，metric 必须使用全类别汇总。"""

    report = _build_report(
        raw_text=_base_bond_raw_text(
            section_two_extra="下属分级基金的基金简称 易方达安悦 A 易方达安悦 C 易方达安悦 E 易方达安悦 F\n"
            "下属分级基金的交易代码 006597 006598 014217 022176",
        ),
        tables=(_share_change_table_ac_ef(),),
    )

    field = extract_bond_risk_evidence(report, "bond_fund")
    assert field.value is not None
    group = _group_by_id(field.value, "redemption_share_pressure")

    assert group.status == "accepted"
    assert "all_classes: beginning=3000000" in (group.metric_value or "")
    assert "all_classes: beginning=1000000" not in (group.metric_value or "")


def test_redemption_share_pressure_rejects_net_asset_statement_table() -> None:
    """财务报表表格在真 §10 份额变动表之前出现时，不能被误选。"""

    report = _build_report(
        raw_text=_base_bond_raw_text(
            section_two_extra="下属分级基金的基金简称 易方达安悦 A 易方达安悦 C 易方达安悦 E 易方达安悦 F\n"
            "下属分级基金的交易代码 006597 006598 014217 022176",
        ),
        tables=(_net_asset_statement_like_table(), _share_change_table_ac_ef()),
    )

    field = extract_bond_risk_evidence(report, "bond_fund")
    assert field.value is not None
    group = _group_by_id(field.value, "redemption_share_pressure")

    assert group.status == "accepted"
    anchor = _anchor_ref_by_id(field.value, group.source_anchor_ids[0])
    assert anchor.table_id == "page-65-table-0"


def test_redemption_share_pressure_uses_total_subscription_and_redemption_rows() -> None:
    """净申购/累计申购等干扰行在前时，仍应选择总申购/总赎回行。"""

    report = _build_report(
        raw_text=_base_bond_raw_text(
            section_two_extra="下属分级基金的基金简称 易方达安悦 A 易方达安悦 C 易方达安悦 E 易方达安悦 F\n"
            "下属分级基金的交易代码 006597 006598 014217 022176",
        ),
        tables=(
            _share_change_table_ac_ef(
                rows=(
                    ("期初基金份额总额", "1,000,000.00", "2,000,000.00", "0.00", "-", "3,000,000.00"),
                    ("净申购份额", "1.00", "1.00", "1.00", "1.00", "4.00"),
                    ("累计申购份额", "2.00", "2.00", "2.00", "2.00", "8.00"),
                    ("本期基金总申购份额", "200,000.00", "400,000.00", "500,000.00", "100,000.00", "1,200,000.00"),
                    ("净赎回份额", "1.00", "1.00", "1.00", "1.00", "4.00"),
                    ("累计赎回份额", "2.00", "2.00", "2.00", "2.00", "8.00"),
                    ("本期基金总赎回份额", "300,000.00", "100,000.00", "500,000.00", "100,000.00", "1,000,000.00"),
                    ("本期基金拆分变动份额", "-", "-", "-", "-", "-"),
                    ("期末基金份额总额", "900,000.00", "2,300,000.00", "0.00", "-", "3,200,000.00"),
                ),
            ),
        ),
    )

    field = extract_bond_risk_evidence(report, "bond_fund")
    assert field.value is not None
    group = _group_by_id(field.value, "redemption_share_pressure")
    anchors = tuple(_anchor_ref_by_id(field.value, anchor_id) for anchor_id in group.source_anchor_ids)
    subscription_anchor = next(anchor for anchor in anchors if anchor.evidence_role == "subscription")
    redemption_anchor = next(anchor for anchor in anchors if anchor.evidence_role == "redemption")

    assert group.status == "accepted"
    assert "subscription=1200000" in (group.metric_value or "")
    assert "redemption=1000000" in (group.metric_value or "")
    assert subscription_anchor.row_locator.startswith("row:4:本期基金总申购份额")
    assert redemption_anchor.row_locator.startswith("row:7:本期基金总赎回份额")


def test_redemption_share_pressure_fails_closed_when_class_columns_do_not_align() -> None:
    """§2 有 A/C/E/F 但 §10 列数不一致时必须失败关闭。"""

    report = _build_report(
        raw_text=_base_bond_raw_text(
            section_two_extra="下属分级基金的基金简称 易方达安悦 A 易方达安悦 C 易方达安悦 E 易方达安悦 F\n"
            "下属分级基金的交易代码 006597 006598 014217 022176",
        ),
        tables=(_share_change_table_ac_ef(headers=("项目", "易方达安悦 A", "易方达安悦 C", "易方达安悦 E", "合计")),),
    )

    field = extract_bond_risk_evidence(report, "bond_fund")
    assert field.value is not None
    group = _group_by_id(field.value, "redemption_share_pressure")

    assert group.status == "ambiguous"
    assert group.na_reason == "share_class_column_count_mismatch"
    assert "redemption_share_pressure" not in field.value.satisfied_group_ids


def test_redemption_share_pressure_fails_closed_on_mixed_header_signal() -> None:
    """§10 部分列有类别信号、部分列无信号时不得混用显式和位置对齐。"""

    report = _build_report(
        raw_text=_base_bond_raw_text(section_four_extra="基金份额申购赎回期初期末数据见表。"),
        tables=(
            _real_profile_cross_check_table(),
            _real_unlabeled_share_change_table(
                headers=("项目", "易方达安悦 A", "46,593,432.66", "-", "-"),
            ),
        ),
    )

    field = extract_bond_risk_evidence(report, "bond_fund")
    assert field.value is not None
    group = _group_by_id(field.value, "redemption_share_pressure")

    assert group.status == "ambiguous"
    assert group.na_reason == "share_class_column_alignment_ambiguous"
    assert "redemption_share_pressure" not in field.value.satisfied_group_ids


def test_redemption_share_pressure_fails_closed_on_mixed_fund_code_header_signal() -> None:
    """§10 只有部分表头出现基金代码时必须 ambiguous，不能退回位置猜测。"""

    report = _build_report(
        raw_text=_base_bond_raw_text(),
        tables=(
            _real_profile_cross_check_table(),
            _real_unlabeled_share_change_table(
                headers=("项目", "006597", "46,593,432.66", "-", "-"),
            ),
        ),
    )

    field = extract_bond_risk_evidence(report, "bond_fund")
    assert field.value is not None
    group = _group_by_id(field.value, "redemption_share_pressure")

    assert group.status == "ambiguous"
    assert group.na_reason == "share_class_column_alignment_ambiguous"


def test_redemption_share_pressure_fails_closed_when_unlabeled_cross_check_missing() -> None:
    """无标签 §10 缺少 §2 profile 期末份额三行校验时必须失败关闭。"""

    report = _build_report(
        raw_text=_base_bond_raw_text(),
        tables=(
            _share_class_mapping_table(),
            _real_unlabeled_share_change_table(),
        ),
    )

    field = extract_bond_risk_evidence(report, "bond_fund")
    assert field.value is not None
    group = _group_by_id(field.value, "redemption_share_pressure")

    assert group.status == "ambiguous"
    assert group.na_reason == "share_class_ending_cross_check_missing"


def test_redemption_share_pressure_fails_closed_when_unlabeled_cross_check_mismatch() -> None:
    """无标签 §10 与 §2 profile 期末份额不一致时必须失败关闭。"""

    report = _build_report(
        raw_text=_base_bond_raw_text(),
        tables=(
            _real_profile_cross_check_table(
                ending_row=(
                    "报告期末下属分级基金的份额总额",
                    "5,711,224,268.10",
                    "4,760,029,015.27",
                    "25,795,859.12",
                    "52,531,021.84",
                ),
            ),
            _real_unlabeled_share_change_table(),
        ),
    )

    field = extract_bond_risk_evidence(report, "bond_fund")
    assert field.value is not None
    group = _group_by_id(field.value, "redemption_share_pressure")

    assert group.status == "ambiguous"
    assert group.na_reason == "share_class_ending_cross_check_mismatch"


def test_redemption_share_pressure_does_not_self_certify_cross_check_with_section_ten() -> None:
    """§2 期末份额交叉校验不得用当前 §10 份额变动表自证。"""

    report = _build_report(
        raw_text=_base_bond_raw_text(),
        tables=(
            _real_profile_cross_check_table(page_number=65, table_index=0),
            _real_unlabeled_share_change_table(),
        ),
    )

    field = extract_bond_risk_evidence(report, "bond_fund")
    assert field.value is not None
    group = _group_by_id(field.value, "redemption_share_pressure")

    assert group.status == "ambiguous"
    assert group.na_reason == "share_class_ending_cross_check_missing"


def test_redemption_share_pressure_unlabeled_path_fails_closed_on_arithmetic_mismatch() -> None:
    """无标签列路径仍必须先通过 §10 类别与汇总算术对账。"""

    report = _build_report(
        raw_text=_base_bond_raw_text(),
        tables=(
            _real_profile_cross_check_table(),
            _real_unlabeled_share_change_table(
                rows=(
                    ("本报告期期\n初基金份额\n总额", "7,699,969,800.13", "5,252,561,821.84", "29,473,505.53", "-"),
                    ("本报告期基\n金总申购份\n额", "27,623,952,157.07", "13,075,203,360.10", "910,677,227.41", "64,417,694.70"),
                    ("减：本报告期\n基金总赎回\n份额", "29,612,697,690.11", "13,567,736,166.67", "914,354,873.82", "11,886,672.86"),
                    ("本报告期基\n金拆分变动\n份额", "-", "-", "-", "-"),
                    ("本报告期期\n末基金份额\n总额", "5,711,224,268.10", "4,760,029,015.27", "25,795,859.12", "52,531,021.84"),
                ),
            ),
        ),
    )

    field = extract_bond_risk_evidence(report, "bond_fund")
    assert field.value is not None
    group = _group_by_id(field.value, "redemption_share_pressure")

    assert group.status == "ambiguous"
    assert group.na_reason == "share_change_arithmetic_mismatch"


def test_redemption_share_pressure_unlabeled_path_fails_closed_on_numeric_row_label_header() -> None:
    """无标签列路径下 headers[0] 是普通数值时不得把首列当作行标签列。"""

    report = _build_report(
        raw_text=_base_bond_raw_text(),
        tables=(
            _real_profile_cross_check_table(),
            _real_unlabeled_share_change_table(headers=("123,456.78", "191,879,496.71", "46,593,432.66", "-", "-")),
        ),
    )

    field = extract_bond_risk_evidence(report, "bond_fund")
    assert field.value is not None
    group = _group_by_id(field.value, "redemption_share_pressure")

    assert group.status == "ambiguous"
    assert group.na_reason == "share_class_column_count_mismatch"


def test_redemption_share_pressure_unlabeled_path_fails_closed_on_non_standard_body_shape() -> None:
    """无标签列路径下 body 首列没有份额变动语义时必须失败关闭。"""

    report = _build_report(
        raw_text=_base_bond_raw_text(section_four_extra="基金份额申购赎回期初期末数据见表。"),
        tables=(
            _real_profile_cross_check_table(),
            _real_unlabeled_share_change_table(
                rows=(
                    ("alpha", "期初基金份额总额", "5,252,561,821.84", "29,473,505.53", "-"),
                    ("beta", "本期基金总申购份额", "13,075,203,360.10", "910,677,227.41", "64,417,694.70"),
                    ("gamma", "本期基金总赎回份额", "13,567,736,166.67", "914,354,873.82", "11,886,672.86"),
                    ("delta", "本期基金拆分变动份额", "-", "-", "-"),
                    ("omega", "期末基金份额总额", "4,760,029,015.27", "25,795,859.12", "52,531,021.84"),
                ),
            ),
        ),
    )

    field = extract_bond_risk_evidence(report, "bond_fund")
    assert field.value is not None
    group = _group_by_id(field.value, "redemption_share_pressure")

    assert group.status == "ambiguous"
    assert group.na_reason == "share_class_column_count_mismatch"


def test_redemption_share_pressure_unlabeled_path_fails_closed_on_all_zero_aggregate_beginning() -> None:
    """无标签列路径下全类别期初为零时不得 accepted。"""

    zero_rows = (
        ("本报告期期初基金份额总额", "-", "-", "-", "-"),
        ("本报告期基金总申购份额", "-", "-", "-", "-"),
        ("减：本报告期基金总赎回份额", "-", "-", "-", "-"),
        ("本报告期基金拆分变动份额", "-", "-", "-", "-"),
        ("本报告期期末基金份额总额", "-", "-", "-", "-"),
    )
    report = _build_report(
        raw_text=_base_bond_raw_text(),
        tables=(
            _real_profile_cross_check_table(
                ending_row=("报告期末下属分级基金的份额总额", "-", "-", "-", "-"),
            ),
            _real_unlabeled_share_change_table(rows=zero_rows),
        ),
    )

    field = extract_bond_risk_evidence(report, "bond_fund")
    assert field.value is not None
    group = _group_by_id(field.value, "redemption_share_pressure")

    assert group.status == "ambiguous"
    assert group.na_reason == "aggregate_beginning_zero"


def test_redemption_share_pressure_fails_closed_on_arithmetic_mismatch() -> None:
    """类别或汇总份额变动对账不平时必须失败关闭。"""

    report = _build_report(
        raw_text=_base_bond_raw_text(
            section_two_extra="下属分级基金的基金简称 易方达安悦 A 易方达安悦 C 易方达安悦 E 易方达安悦 F\n"
            "下属分级基金的交易代码 006597 006598 014217 022176",
        ),
        tables=(
            _share_change_table_ac_ef(
                rows=(
                    ("期初基金份额总额", "1,000,000.00", "2,000,000.00", "0.00", "-"),
                    ("本期基金总申购份额", "200,000.00", "400,000.00", "500,000.00", "100,000.00"),
                    ("本期基金总赎回份额", "300,000.00", "100,000.00", "500,000.00", "100,000.00"),
                    ("本期基金拆分变动份额", "-", "-", "-", "-"),
                    ("期末基金份额总额", "901,000.00", "2,300,000.00", "0.00", "-"),
                ),
            ),
        ),
    )

    field = extract_bond_risk_evidence(report, "bond_fund")
    assert field.value is not None
    group = _group_by_id(field.value, "redemption_share_pressure")

    assert group.status == "ambiguous"
    assert group.na_reason == "share_change_arithmetic_mismatch"


def test_redemption_share_pressure_fails_closed_on_non_parseable_share_value() -> None:
    """份额数值无法 Decimal 解析时必须 ambiguous 且记录原因。"""

    report = _build_report(
        raw_text=_base_bond_raw_text(
            section_two_extra="下属分级基金的基金简称 易方达安悦 A 易方达安悦 C 易方达安悦 E 易方达安悦 F\n"
            "下属分级基金的交易代码 006597 006598 014217 022176",
        ),
        tables=(
            _share_change_table_ac_ef(
                rows=(
                    ("期初基金份额总额", "1,000,000.00", "2,000,000.00", "0.00", "-"),
                    ("本期基金总申购份额", "bad-value", "400,000.00", "500,000.00", "100,000.00"),
                    ("本期基金总赎回份额", "300,000.00", "100,000.00", "500,000.00", "100,000.00"),
                    ("本期基金拆分变动份额", "-", "-", "-", "-"),
                    ("期末基金份额总额", "900,000.00", "2,300,000.00", "0.00", "-"),
                ),
            ),
        ),
    )

    field = extract_bond_risk_evidence(report, "bond_fund")
    assert field.value is not None
    group = _group_by_id(field.value, "redemption_share_pressure")

    assert group.status == "ambiguous"
    assert group.na_reason == "non_parseable_share_value"


def test_redemption_share_pressure_parses_full_width_dash_as_zero() -> None:
    """全角横线应按零解析，并参与全类别聚合对账。"""

    report = _build_report(
        raw_text=_base_bond_raw_text(
            section_two_extra="下属分级基金的基金简称 易方达安悦 A 易方达安悦 C 易方达安悦 E 易方达安悦 F\n"
            "下属分级基金的交易代码 006597 006598 014217 022176",
        ),
        tables=(
            _share_change_table_ac_ef(
                rows=(
                    ("期初基金份额总额", "1,000,000.00", "2,000,000.00", "0.00", "－"),
                    ("本期基金总申购份额", "200,000.00", "400,000.00", "500,000.00", "100,000.00"),
                    ("本期基金总赎回份额", "300,000.00", "100,000.00", "500,000.00", "100,000.00"),
                    ("本期基金拆分变动份额", "－", "－", "－", "－"),
                    ("期末基金份额总额", "900,000.00", "2,300,000.00", "0.00", "－"),
                ),
            ),
        ),
    )

    field = extract_bond_risk_evidence(report, "bond_fund")
    assert field.value is not None
    group = _group_by_id(field.value, "redemption_share_pressure")

    assert group.status == "accepted"
    assert "F(code=022176, beginning=0" in (group.metric_value or "")


def test_redemption_share_pressure_anchor_missing_not_accepted() -> None:
    """缺少期末等必需行级锚点时不能 accepted。"""

    report = _build_report(
        raw_text=_base_bond_raw_text(
            section_two_extra="下属分级基金的基金简称 易方达安悦 A 易方达安悦 C 易方达安悦 E 易方达安悦 F\n"
            "下属分级基金的交易代码 006597 006598 014217 022176",
        ),
        tables=(
            _share_change_table_ac_ef(
                rows=(
                    ("期初基金份额总额", "1,000,000.00", "2,000,000.00", "0.00", "-"),
                    ("本期基金总申购份额", "200,000.00", "400,000.00", "500,000.00", "100,000.00"),
                    ("本期基金总赎回份额", "300,000.00", "100,000.00", "500,000.00", "100,000.00"),
                ),
            ),
        ),
    )

    field = extract_bond_risk_evidence(report, "bond_fund")
    assert field.value is not None
    group = _group_by_id(field.value, "redemption_share_pressure")

    assert group.status == "ambiguous"
    assert group.na_reason == "incomplete_share_change_rows"


def test_convertible_and_equity_dash_rows_become_accepted_absence() -> None:
    """权益和可转债 '-' 行应形成 accepted_absence 证据。"""

    report = _build_report(
        raw_text=_base_bond_raw_text(),
        tables=(
            ParsedTable(
                page_number=59,
                table_index=1,
                headers=("项目", "金额", "占基金总资产比例"),
                rows=(("股票", "-", "-"), ("可转债（可交换债）", "-", "-")),
            ),
        ),
    )

    field = extract_bond_risk_evidence(report, "bond_fund")
    assert field.value is not None
    group = _group_by_id(field.value, "convertible_bond_equity_exposure")

    assert group.status == "accepted_absence"
    assert group.strength == "quantitative_absence"
    assert group.measurement_kind == "explicit_absence"
    assert len(group.source_anchor_ids) == 2
    assert "convertible_bond_equity_exposure" in field.value.satisfied_group_ids


def test_non_bond_type_returns_missing_without_scanning_group_extractors(monkeypatch: pytest.MonkeyPatch) -> None:
    """非债券或未知类型必须早退，不扫描七组风险 extractor。"""

    def _fail_group_scan(_report: ParsedAnnualReport) -> object:
        raise AssertionError("non-bond path must not scan bond evidence groups")

    monkeypatch.setattr(bond_risk_module, "_extract_duration_rate_risk", _fail_group_scan)
    field = extract_bond_risk_evidence(_build_report(raw_text=_base_bond_raw_text(), tables=()), "active_fund")

    assert field.value is None
    assert field.anchors == ()
    assert field.extraction_mode == "missing"
    assert field.note == "not_applicable_non_bond_fund"


def test_none_fund_type_returns_missing_without_scanning_group_extractors(monkeypatch: pytest.MonkeyPatch) -> None:
    """classified_fund_type 为 None 时必须早退，不扫描七组风险 extractor。"""

    def _fail_group_scan(_report: ParsedAnnualReport) -> object:
        raise AssertionError("None fund type must not scan bond evidence groups")

    monkeypatch.setattr(bond_risk_module, "_extract_duration_rate_risk", _fail_group_scan)
    field = extract_bond_risk_evidence(_build_report(raw_text=_base_bond_raw_text(), tables=()), None)

    assert field.value is None
    assert field.anchors == ()
    assert field.extraction_mode == "missing"
    assert field.note == "not_applicable_non_bond_fund"


def test_partial_extraction_with_mixed_groups_produces_estimated_mode() -> None:
    """部分组满足时 extraction_mode 应为 estimated，不得伪装为 direct 或 missing。"""

    report = _build_report(
        raw_text=_base_bond_raw_text(section_four_extra="本基金通过久期管理控制利率风险。"),
        tables=(
            ParsedTable(
                page_number=53,
                table_index=0,
                headers=("长期信用评级", "本期末公允价值", "占基金资产净值比例"),
                rows=(("AAA 债券", "1,000,000.00", "80.00%"), ("合计", "1,000,000.00", "80.00%")),
            ),
        ),
    )

    field = extract_bond_risk_evidence(report, "bond_fund")
    assert field.value is not None
    assert field.value.contract_status == "partial"
    assert field.extraction_mode == "estimated"
    assert "duration_rate_risk" in field.value.satisfied_group_ids
    assert "credit_risk" in field.value.satisfied_group_ids
    assert len(field.value.satisfied_group_ids) < len(BOND_RISK_EVIDENCE_GROUP_IDS)
    assert len(field.value.missing_group_ids) > 0
    assert field.extraction_mode != "direct"
    assert field.value.contract_status != "satisfied"


def test_incomplete_seven_group_coverage_does_not_masquerade_as_complete() -> None:
    """不完整七组覆盖不得伪装为 satisfied 或 direct。"""

    report = _build_report(
        raw_text=_base_bond_raw_text(section_four_extra="本基金力争保持净值稳定并控制回撤。"),
        tables=(),
    )

    field = extract_bond_risk_evidence(report, "bond_fund")
    assert field.value is not None
    assert field.extraction_mode != "direct"
    assert field.value.contract_status != "satisfied"
    assert len(field.value.satisfied_group_ids) < len(BOND_RISK_EVIDENCE_GROUP_IDS)


def test_non_zero_equity_row_does_not_produce_accepted_absence() -> None:
    """股票行值为非零或非横线时不应产生 accepted_absence 证据。"""

    report = _build_report(
        raw_text=_base_bond_raw_text(),
        tables=(
            ParsedTable(
                page_number=59,
                table_index=1,
                headers=("项目", "金额", "占基金总资产比例"),
                rows=(("股票", "100,000.00", "5.00%"),),
            ),
        ),
    )

    field = extract_bond_risk_evidence(report, "bond_fund")
    assert field.value is not None
    group = _group_by_id(field.value, "convertible_bond_equity_exposure")

    assert group.status == "missing"
    assert group.strength == "missing"
    assert "convertible_bond_equity_exposure" not in field.value.satisfied_group_ids


def test_boilerplate_rate_risk_text_alone_does_not_satisfy_duration_group() -> None:
    """样板利率风险披露文本不应满足久期/利率风险组。"""

    report = _build_report(
        raw_text=_base_bond_raw_text(section_four_extra="本基金面临利率风险。"),
        tables=(),
    )

    field = extract_bond_risk_evidence(report, "bond_fund")
    assert field.value is not None
    group = _group_by_id(field.value, "duration_rate_risk")

    assert group.status == "missing"
    assert "duration_rate_risk" not in field.value.satisfied_group_ids


def _complete_value(
    *,
    overrides: dict[BondRiskEvidenceGroupId, BondRiskEvidenceGroupRecord] | None = None,
) -> BondRiskEvidenceValue:
    """构造模板第 6 章七组完整债券风险证据值。

    Args:
        overrides: 按风险组 ID 覆盖默认记录。

    Returns:
        可用于模型契约测试的债券风险证据值。
    """

    overrides = overrides or {}
    groups = tuple(overrides.get(group_id, _default_group_record(group_id)) for group_id in BOND_RISK_EVIDENCE_GROUP_IDS)
    anchors = tuple(_anchor(group.group_id) for group in groups if group.source_anchor_ids)
    satisfied_ids = tuple(
        group.group_id for group in groups if group.status in {"accepted", "accepted_absence"}
    )
    missing_ids = tuple(group.group_id for group in groups if group.status == "missing")
    weak_ids = tuple(group.group_id for group in groups if group.status == "weak")
    ambiguous_ids = tuple(group.group_id for group in groups if group.status == "ambiguous")
    if len(satisfied_ids) == len(BOND_RISK_EVIDENCE_GROUP_IDS):
        contract_status = "satisfied"
    elif satisfied_ids or weak_ids or ambiguous_ids:
        contract_status = "partial"
    else:
        contract_status = "missing"

    return BondRiskEvidenceValue(
        schema_version=BOND_RISK_EVIDENCE_CONTRACT_ID,
        contract_id=BOND_RISK_EVIDENCE_CONTRACT_ID,
        fund_code="006597",
        report_year=2024,
        groups=groups,
        anchors=anchors,
        satisfied_group_ids=satisfied_ids,
        missing_group_ids=missing_ids,
        weak_group_ids=weak_ids,
        ambiguous_group_ids=ambiguous_ids,
        contract_status=contract_status,
    )


def _default_group_record(group_id: BondRiskEvidenceGroupId) -> BondRiskEvidenceGroupRecord:
    """构造模板第 6 章默认已满足风险组记录。

    Args:
        group_id: 债券风险证据组 ID。

    Returns:
        默认风险组记录。
    """

    if group_id == "convertible_bond_equity_exposure":
        return _group_record(
            group_id,
            status="accepted_absence",
            strength="quantitative_absence",
            measurement_kind="explicit_absence",
        )
    return _group_record(
        group_id,
        status="accepted",
        strength="quantitative_direct",
        measurement_kind="actual_exposure",
    )


def _group_record(
    group_id: BondRiskEvidenceGroupId,
    *,
    status: str,
    strength: str,
    measurement_kind: str,
) -> BondRiskEvidenceGroupRecord:
    """构造模板第 6 章单组风险证据记录。

    Args:
        group_id: 债券风险证据组 ID。
        status: 证据状态。
        strength: 证据强度。
        measurement_kind: 度量或披露类型。

    Returns:
        单组风险证据记录。
    """

    return BondRiskEvidenceGroupRecord(
        group_id=group_id,
        status=status,
        strength=strength,
        summary=f"{group_id} fixture summary",
        measurement_kind=measurement_kind,
        metric_name=None,
        metric_value=None,
        metric_unit=None,
        period_label="2024 年报",
        source_anchor_ids=(f"bond-risk:006597:2024:{group_id}:1",),
        na_reason=None,
        reviewer_note=None,
    )


def _anchor(group_id: BondRiskEvidenceGroupId) -> BondRiskEvidenceAnchorRef:
    """构造模板第 6 章单组稳定锚点引用。

    Args:
        group_id: 债券风险证据组 ID。

    Returns:
        稳定组级锚点引用。
    """

    return BondRiskEvidenceAnchorRef(
        anchor_id=f"bond-risk:006597:2024:{group_id}:1",
        section_id="§6",
        page_number=42,
        table_id="table-fixture",
        row_locator=f"{group_id} row",
        evidence_role="fixture",
    )


def _drawdown_metric() -> NavMaxDrawdownMetric:
    """构造 NAV 派生最大回撤指标 fixture。

    Args:
        无。

    Returns:
        `NavMaxDrawdownMetric` fixture。

    Raises:
        无显式抛出。
    """

    return NavMaxDrawdownMetric(
        fund_code="006597",
        share_class="A",
        period_start=date(2024, 1, 1),
        period_end=date(2024, 12, 31),
        record_count=244,
        max_drawdown_ratio=Decimal("-0.10"),
        peak_date=date(2024, 3, 1),
        peak_value=Decimal("1.20"),
        trough_date=date(2024, 4, 1),
        trough_value=Decimal("1.08"),
        calculation_method="max_drawdown_on_accumulated_nav_path",
        source=NavSourceMetadata(
            source_name="csrc_eid",
            origin_source="csrc_eid",
            source_id="5755:2030-1010",
            source_url="https://eid.csrc.gov.cn/fund/5755",
            cached=False,
            retrieved_at=datetime(2026, 5, 29, tzinfo=timezone.utc),
            cache_updated_at=None,
            requested_fund_code="006597",
            returned_fund_code="006597",
            returned_fund_name="国泰利享中短债债券A",
            source_query_params=(("fund_code", "006597"), ("share_class", "A")),
        ),
        nav_type="accumulated_nav",
        adjusted_basis="accumulated_nav",
        dividend_adjustment_status="not_applicable",
        identity_status="verified",
    )


def _group_by_id(
    value: BondRiskEvidenceValue,
    group_id: BondRiskEvidenceGroupId,
) -> BondRiskEvidenceGroupRecord:
    """按风险组 ID 读取模板第 6 章证据记录。

    Args:
        value: 债券风险证据契约值。
        group_id: 目标风险组 ID。

    Returns:
        匹配的风险组记录。
    """

    return next(group for group in value.groups if group.group_id == group_id)


def _anchor_ref_by_id(value: BondRiskEvidenceValue, anchor_id: str) -> BondRiskEvidenceAnchorRef:
    """按锚点 ID 读取模板第 6 章稳定锚点。

    Args:
        value: 债券风险证据契约值。
        anchor_id: 目标锚点 ID。

    Returns:
        匹配的组级锚点。
    """

    return next(anchor for anchor in value.anchors if anchor.anchor_id == anchor_id)


def _extractor_anchor_by_locator(field: object, row_locator: str) -> EvidenceAnchor:
    """按行定位读取 extractor 层锚点。

    Args:
        field: 抽取字段。
        row_locator: 目标行定位。

    Returns:
        匹配的 extractor 层证据锚点。
    """

    return next(anchor for anchor in field.anchors if anchor.row_locator == row_locator)


def _build_report(
    *,
    raw_text: str,
    tables: tuple[ParsedTable, ...],
    year: int = 2024,
) -> ParsedAnnualReport:
    """构造模板第 6 章 extractor 测试用最小年报。

    Args:
        raw_text: 年报全文。
        tables: 年报表格。
        year: 年报年份。

    Returns:
        最小 ``ParsedAnnualReport``。
    """

    sections = {}
    section_order = ("§2", "§4", "§5", "§8", "§9", "§10")
    for index, section_id in enumerate(section_order):
        start = raw_text.index(section_id)
        if index + 1 < len(section_order):
            end = raw_text.index(section_order[index + 1])
        else:
            end = len(raw_text)
        sections[section_id] = ReportSection(
            section_id=section_id,
            title=f"{section_id} fixture",
            start_offset=start,
            end_offset=end,
            matched_rule="fixture",
            confidence=1.0,
        )
    return ParsedAnnualReport(
        key=DocumentKey(fund_code="006597", year=year),
        raw_text=raw_text,
        sections=sections,
        tables=tables,
    )


def _base_bond_raw_text(section_two_extra: str = "", section_four_extra: str = "") -> str:
    """构造含 §2/§4/§5/§8/§9/§10 的最小年报文本。

    Args:
        section_two_extra: §2 追加文本。
        section_four_extra: §4 追加文本。

    Returns:
        年报全文。
    """

    return (
        "§2 基金简介\n"
        f"{section_two_extra}\n"
        "§4 管理人报告\n"
        f"{section_four_extra}\n"
        "§5 托管人报告\n"
        "§8 投资组合报告\n"
        "§9 基金份额持有人信息\n"
        "§10 开放式基金份额变动\n"
    )


def _rating_distribution_table(
    *,
    page_number: int,
    table_index: int,
    headers: tuple[str, ...],
    rows: tuple[tuple[str, ...], ...],
) -> ParsedTable:
    """构造持仓评级分布表。

    Args:
        page_number: 表格页码。
        table_index: 同页表格序号。
        headers: 表头。
        rows: 数据行。

    Returns:
        年报解析表格。
    """

    return ParsedTable(
        page_number=page_number,
        table_index=table_index,
        headers=headers,
        rows=rows,
    )


def _share_class_mapping_table(
    rows: tuple[tuple[str, ...], ...] = (
        ("下属分级基金的基金简称", "易方达安悦 A", "易方达安悦 C", "易方达安悦 E", "易方达安悦 F"),
        ("下属分级基金的交易代码", "006597", "006598", "014217", "022176"),
    ),
) -> ParsedTable:
    """构造 §2 A/C/E/F 份额类别映射表。

    Args:
        rows: 表格行。

    Returns:
        年报解析表格。
    """

    return ParsedTable(
        page_number=8,
        table_index=0,
        headers=("项目", "A类", "C类", "E类", "F类"),
        rows=rows,
    )


def _real_profile_cross_check_table(
    *,
    page_number: int = 5,
    table_index: int = 0,
    ending_row: tuple[str, ...] = (
        "报告期末下属分级基金的份额总额",
        "5,711,224,267.09",
        "4,760,029,015.27",
        "25,795,859.12",
        "52,531,021.84",
    ),
) -> ParsedTable:
    """构造真实 006597 §2 profile 三行交叉校验表形状。

    Args:
        page_number: 表格页码。
        table_index: 同页表格序号。
        ending_row: §2 报告期末下属分级基金份额总额行。

    Returns:
        年报解析表格。
    """

    return ParsedTable(
        page_number=page_number,
        table_index=table_index,
        headers=("项目", "A类", "C类", "E类", "F类"),
        rows=(
            ("基金管理人", "示例", "", "", ""),
            ("基金托管人", "示例", "", "", ""),
            ("基金合同生效日", "2018年12月3日", "", "", ""),
            ("基金类型", "债券型", "", "", ""),
            ("运作方式", "契约型开放式", "", "", ""),
            ("基金经理", "示例", "", "", ""),
            ("投资目标", "示例", "", "", ""),
            ("投资策略", "示例", "", "", ""),
            ("下属分级基金的基金简称", "易方达安悦 A", "易方达安悦 C", "易方达安悦 E", "易方达安悦 F"),
            ("下属分级基金的交易代码", "006597", "006598", "014217", "022176"),
            ending_row,
        ),
    )


def _share_change_table() -> ParsedTable:
    """构造多份额类别份额变动表。

    Args:
        无。

    Returns:
        份额变动表。
    """

    return ParsedTable(
        page_number=65,
        table_index=0,
        headers=("项目", "易方达安悦 A", "易方达安悦 C", "合计"),
        rows=(
            ("期初基金份额总额", "1,000,000.00", "2,000,000.00", "3,000,000.00"),
            ("本期基金总申购份额", "200,000.00", "400,000.00", "600,000.00"),
            ("本期基金总赎回份额", "300,000.00", "100,000.00", "400,000.00"),
            ("期末基金份额总额", "900,000.00", "2,300,000.00", "3,200,000.00"),
        ),
    )


def _real_unlabeled_share_change_table(
    *,
    headers: tuple[str, ...] = (
        "基金合同生\n效日（2018\n年12月3日）\n基金份额总\n额",
        "191,879,496.71",
        "46,593,432.66",
        "-",
        "-",
    ),
    rows: tuple[tuple[str, ...], ...] = (
        ("本报告期期\n初基金份额\n总额", "7,699,969,800.13", "5,252,561,821.84", "29,473,505.53", "-"),
        ("本报告期基\n金总申购份\n额", "27,623,952,157.07", "13,075,203,360.10", "910,677,227.41", "64,417,694.70"),
        ("减：本报告期\n基金总赎回\n份额", "29,612,697,690.11", "13,567,736,166.67", "914,354,873.82", "11,886,672.86"),
        ("本报告期基\n金拆分变动\n份额", "-", "-", "-", "-"),
        ("本报告期期\n末基金份额\n总额", "5,711,224,267.09", "4,760,029,015.27", "25,795,859.12", "52,531,021.84"),
    ),
) -> ParsedTable:
    """构造真实 006597 §10 无类别表头份额变动表形状。

    Args:
        headers: 表头。
        rows: 数据行。

    Returns:
        年报解析表格。
    """

    return ParsedTable(
        page_number=65,
        table_index=0,
        headers=headers,
        rows=rows,
    )


def _share_change_table_ac_ef(
    *,
    headers: tuple[str, ...] = ("项目", "易方达安悦 A", "易方达安悦 C", "易方达安悦 E", "易方达安悦 F", "合计"),
    rows: tuple[tuple[str, ...], ...] = (
        ("期初基金份额总额", "1,000,000.00", "2,000,000.00", "0.00", "-", "3,000,000.00"),
        ("本期基金总申购份额", "200,000.00", "400,000.00", "500,000.00", "100,000.00", "1,200,000.00"),
        ("本期基金总赎回份额", "300,000.00", "100,000.00", "500,000.00", "100,000.00", "1,000,000.00"),
        ("本期基金拆分变动份额", "-", "-", "-", "-", "-"),
        ("期末基金份额总额", "900,000.00", "2,300,000.00", "0.00", "-", "3,200,000.00"),
    ),
) -> ParsedTable:
    """构造 A/C/E/F 多份额类别份额变动表。

    Args:
        headers: 表头。
        rows: 数据行。

    Returns:
        年报解析表格。
    """

    return ParsedTable(
        page_number=65,
        table_index=0,
        headers=headers,
        rows=rows,
    )


def _net_asset_statement_like_table() -> ParsedTable:
    """构造包含申购/赎回字样但属于财务报表的干扰表。

    Args:
        无。

    Returns:
        年报解析表格。
    """

    return ParsedTable(
        page_number=60,
        table_index=0,
        headers=("项目", "实收基金", "未分配利润", "净资产合计"),
        rows=(
            ("期初基金份额总额", "1,000,000.00", "2,000,000.00", "3,000,000.00"),
            ("本期申购", "200,000.00", "400,000.00", "600,000.00"),
            ("本期赎回", "300,000.00", "100,000.00", "400,000.00"),
            ("期末基金份额总额", "900,000.00", "2,300,000.00", "3,200,000.00"),
        ),
    )
