"""否决项检查测试。"""

from __future__ import annotations

from decimal import Decimal

from fund_agent.fund.analysis import (
    ConsistencyCheckResult,
    ConsistencyDimensionResult,
    ResolvedTrackingErrorForRisk,
    StressTestRule,
    resolve_tracking_error_for_risk,
    run_risk_checks,
    run_stress_test,
)
from fund_agent.fund.extractors.models import EvidenceAnchor, ExtractedField, TrackingErrorValue


def _anchor(section_id: str, row_locator: str) -> EvidenceAnchor:
    """构造测试证据锚点。

    Args:
        section_id: 年报章节编号。
        row_locator: 行定位说明。

    Returns:
        证据锚点。

    Raises:
        无显式抛出。
    """

    return EvidenceAnchor(
        source_kind="annual_report",
        document_year=2024,
        section_id=section_id,
        page_number=None,
        table_id=None,
        row_locator=row_locator,
        note=f"{row_locator}: fixture",
    )


def _field(value: dict[str, object] | None, section_id: str, row_locator: str) -> ExtractedField[dict[str, object]]:
    """构造测试抽取字段。

    Args:
        value: 字段值。
        section_id: 年报章节编号。
        row_locator: 行定位说明。

    Returns:
        抽取字段。

    Raises:
        无显式抛出。
    """

    return ExtractedField(
        value=value,
        anchors=() if value is None else (_anchor(section_id, row_locator),),
        extraction_mode="missing" if value is None else "direct",
        note=None,
    )


def _basic_identity(scale: str | None = "10.00亿元") -> ExtractedField[dict[str, object]]:
    """构造基础身份字段。

    Args:
        scale: 基金规模文本。

    Returns:
        基础身份字段。

    Raises:
        无显式抛出。
    """

    return _field(
        {
            "fund_name": "测试基金",
            "fund_code": "110011",
            "fund_scale": scale,
            "classified_fund_type": "active_fund",
        },
        "§1",
        "basic_identity",
    )


def _fee_schedule(
    management_fee: str | None = "1.20%",
    custody_fee: str | None = "0.20%",
) -> ExtractedField[dict[str, object]]:
    """构造费率字段。

    Args:
        management_fee: 管理费。
        custody_fee: 托管费。

    Returns:
        费率字段。

    Raises:
        无显式抛出。
    """

    return _field(
        {"management_fee": management_fee, "custody_fee": custody_fee},
        "§2",
        "fee_schedule",
    )


def _tracking_error_field(value_text: str | None = None) -> ExtractedField[TrackingErrorValue]:
    """构造跟踪误差字段。

    Args:
        value_text: 跟踪误差百分比文本；为空时返回 missing。

    Returns:
        跟踪误差抽取字段。

    Raises:
        无显式抛出。
    """

    if value_text is None:
        return ExtractedField(value=None, anchors=(), extraction_mode="missing", note="fixture missing")
    value = TrackingErrorValue(
        value=Decimal(value_text.replace("%", "")) / Decimal("100"),
        value_text=value_text,
        unit="ratio",
        period_label="报告期",
        period_start=None,
        period_end=None,
        annualized=True,
        source_type="direct_disclosure",
        calculation_method="disclosed",
        benchmark_identity_status="identified",
        benchmark_index_name="沪深300指数",
        benchmark_index_code=None,
        fund_series_source=None,
        index_series_source=None,
        observation_count=None,
        frequency="annual_report_period",
        annualization_factor=None,
        input_period_complete=True,
        provenance_note="fixture direct disclosure",
    )
    return ExtractedField(
        value=value,
        anchors=(_anchor("§3", "tracking_error"),),
        extraction_mode="direct",
        note=None,
    )


def _consistency(signal: str = "green") -> ConsistencyCheckResult:
    """构造言行一致性结果。

    Args:
        signal: 整体信号。

    Returns:
        言行一致性结果。

    Raises:
        无显式抛出。
    """

    status = "misaligned" if signal == "red" else "aligned"
    dimension = ConsistencyDimensionResult(
        dimension="investment_style",
        status=status,  # type: ignore[arg-type]
        signal=signal,  # type: ignore[arg-type]
        declared="value",
        actual="value",
        anchors=(_anchor("§4", "style_positioning"),),
        reason="fixture",
    )
    return ConsistencyCheckResult(
        dimensions=(dimension,),
        overall_status=status,  # type: ignore[arg-type]
        overall_signal=signal,  # type: ignore[arg-type]
        reasons=("fixture",),
    )


def _resolved_tracking_error(value_text: str | None, fund_type: str = "index_fund") -> ResolvedTrackingErrorForRisk:
    """构造风险检查使用的 resolved 跟踪误差。

    Args:
        value_text: 跟踪误差百分比文本。
        fund_type: 基金类型。

    Returns:
        风险检查解析对象。

    Raises:
        ValueError: 当输入格式非法时抛出。
    """

    return resolve_tracking_error_for_risk(
        tracking_error_field=_tracking_error_field(value_text),
        developer_override=None,
        developer_override_enabled=False,
        fund_type=fund_type,  # type: ignore[arg-type]
    )


def test_run_risk_checks_passes_when_all_inputs_safe() -> None:
    """验证 5 项否决检查在安全输入下全部通过。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当安全输入触发否决时抛出。
    """

    result = run_risk_checks(
        basic_identity=_basic_identity("10.00亿元"),
        fee_schedule=_fee_schedule("1.20%", "0.20%"),
        consistency_result=_consistency("green"),
        fund_type="active_fund",
        manager_tenure_months=36,
        peer_fee_median="1.00%",
    )

    assert result.overall_status == "pass"
    assert not result.veto_items
    assert {item.code for item in result.items} == {
        "liquidation_risk",
        "manager_tenure",
        "style_drift",
        "excessive_fee",
        "tracking_error",
    }


def test_run_risk_checks_vetoes_liquidation_risk_and_short_tenure() -> None:
    """验证规模低于 5000 万和经理任期少于 6 个月触发否决。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当否决项未触发时抛出。
    """

    result = run_risk_checks(
        basic_identity=_basic_identity("0.30亿元"),
        fee_schedule=_fee_schedule("1.20%", "0.20%"),
        consistency_result=_consistency("green"),
        fund_type="active_fund",
        manager_tenure_months=3,
        peer_fee_median="1.00%",
    )

    assert result.overall_status == "veto"
    assert {item.code for item in result.veto_items} == {"liquidation_risk", "manager_tenure"}


def test_run_risk_checks_vetoes_style_drift_and_excessive_fee() -> None:
    """验证言行一致性红灯和费率超过同类 2 倍触发否决。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当风格或费率否决未触发时抛出。
    """

    result = run_risk_checks(
        basic_identity=_basic_identity("10.00亿元"),
        fee_schedule=_fee_schedule("2.50%", "0.50%"),
        consistency_result=_consistency("red"),
        fund_type="active_fund",
        manager_tenure_months=36,
        peer_fee_median="1.00%",
    )

    assert result.overall_status == "veto"
    assert {item.code for item in result.veto_items} == {"style_drift", "excessive_fee"}


def test_run_risk_checks_vetoes_index_tracking_error() -> None:
    """验证指数基金跟踪误差超过 2% 触发否决。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当跟踪误差否决未触发时抛出。
    """

    result = run_risk_checks(
        basic_identity=_basic_identity("10.00亿元"),
        fee_schedule=_fee_schedule("0.50%", "0.10%"),
        consistency_result=_consistency("green"),
        fund_type="index_fund",
        manager_tenure_months=36,
        peer_fee_median="0.50%",
        tracking_error=_resolved_tracking_error("2.50%"),
    )

    assert result.overall_status == "veto"
    assert {item.code for item in result.veto_items} == {"tracking_error"}
    item = result.veto_items[0]
    assert item.anchors[0].row_locator == "tracking_error"


def test_resolve_tracking_error_prefers_structured_data_over_developer_override() -> None:
    """验证结构化跟踪误差优先于开发覆盖。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当开发覆盖覆盖产品证据时抛出。
    """

    resolved = resolve_tracking_error_for_risk(
        tracking_error_field=_tracking_error_field("1.50%"),
        developer_override="3.00%",
        developer_override_enabled=True,
        fund_type="index_fund",
    )

    assert resolved.value == Decimal("0.015")
    assert resolved.source_type == "direct_disclosure"
    assert resolved.authority == "capability_structured_data"
    assert resolved.is_product_evidence is True
    assert resolved.conflict_note is not None


def test_resolve_tracking_error_uses_developer_override_only_when_missing_and_enabled() -> None:
    """验证开发覆盖只在结构化数据缺失且开发模式启用时作为风险 fallback。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当开发覆盖被当作产品证据时抛出。
    """

    resolved = resolve_tracking_error_for_risk(
        tracking_error_field=_tracking_error_field(None),
        developer_override="1.00%",
        developer_override_enabled=True,
        fund_type="index_fund",
    )

    assert resolved.value == Decimal("0.01")
    assert resolved.source_type == "developer_override"
    assert resolved.authority == "developer_override"
    assert resolved.anchors == ()
    assert resolved.is_product_evidence is False


def test_resolve_tracking_error_ignores_developer_override_in_product_mode() -> None:
    """验证 product mode 不使用开发覆盖。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 product mode 使用开发覆盖时抛出。
    """

    resolved = resolve_tracking_error_for_risk(
        tracking_error_field=_tracking_error_field(None),
        developer_override="1.00%",
        developer_override_enabled=False,
        fund_type="index_fund",
    )

    assert resolved.value is None
    assert resolved.source_type == "missing"
    assert resolved.authority == "missing"


def test_resolve_tracking_error_marks_qdii_not_applicable() -> None:
    """验证 QDII 当前不适用 P13 跟踪误差规则。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 QDII 被纳入当前跟踪误差规则时抛出。
    """

    resolved = resolve_tracking_error_for_risk(
        tracking_error_field=_tracking_error_field("1.00%"),
        developer_override="3.00%",
        developer_override_enabled=True,
        fund_type="qdii_fund",
    )

    assert resolved.source_type == "not_applicable"
    assert resolved.authority == "not_applicable"
    assert resolved.value is None


def test_run_risk_checks_reports_insufficient_data_without_explicit_inputs() -> None:
    """验证显式输入缺失时返回证据不足而非强判。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当缺失输入被强行判断时抛出。
    """

    result = run_risk_checks(
        basic_identity=_basic_identity(None),
        fee_schedule=_fee_schedule("1.20%", "0.20%"),
        consistency_result=None,
        fund_type="index_fund",
        tracking_error=_resolved_tracking_error(None),
    )

    assert result.overall_status == "watch"
    insufficient_codes = {
        item.code
        for item in result.items
        if item.status == "insufficient_data"
    }
    assert insufficient_codes == {
        "liquidation_risk",
        "manager_tenure",
        "style_drift",
        "excessive_fee",
        "tracking_error",
    }
    assert "先补齐或复核" in result.next_minimum_verification


def test_run_stress_test_simulates_three_fixed_scenarios_for_active_fund() -> None:
    """验证主动基金压力测试输出 -20%/-40%/-60% 三个固定场景。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当场景计算或压力等级不符合规则时抛出。
    """

    result = run_stress_test(
        fund_type="active_fund",
        investment_amount="100000",
        max_tolerable_loss_rate="50%",
        anchors=(_anchor("§6", "user_amount"),),
    )

    assert [scenario.code for scenario in result.scenarios] == ["minus_20", "minus_40", "minus_60"]
    assert [scenario.floating_loss_amount for scenario in result.scenarios] == [20000, 40000, 60000]
    assert [scenario.account_balance for scenario in result.scenarios] == [80000, 60000, 40000]
    assert [scenario.severity for scenario in result.scenarios] == ["normal", "extreme", "historical_worst"]
    assert [scenario.capacity_status for scenario in result.scenarios] == [
        "within_tolerance",
        "within_tolerance",
        "beyond_tolerance",
    ]
    assert result.worst_scenario.code == "minus_60"
    assert "minus_60" in result.next_minimum_verification
    assert result.anchors[0].section_id == "§6"


def test_run_stress_test_uses_bond_fund_preferred_lens_thresholds() -> None:
    """验证债券基金使用更低的压力测试阈值。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当债券基金阈值未生效时抛出。
    """

    result = run_stress_test(
        fund_type="bond_fund",
        investment_amount=100000,
        max_tolerable_loss_rate="60%",
    )

    assert [scenario.severity for scenario in result.scenarios] == [
        "historical_worst",
        "beyond_historical",
        "beyond_historical",
    ]


def test_run_stress_test_reports_missing_tolerance_without_guessing_capacity() -> None:
    """验证缺少最大可承受亏损比例时不强行判断能否承受。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当缺失承受能力被强行判断时抛出。
    """

    result = run_stress_test(
        fund_type="index_fund",
        investment_amount=50000,
    )

    assert {scenario.capacity_status for scenario in result.scenarios} == {"not_provided"}
    assert "最大可承受亏损比例" in result.next_minimum_verification


def test_run_stress_test_rejects_invalid_amount_and_tolerance() -> None:
    """验证投入金额和最大可承受亏损比例非法时抛出异常。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当非法输入未抛出异常时抛出。
    """

    try:
        run_stress_test(fund_type="active_fund", investment_amount=0)
    except ValueError as exc:
        assert "必须大于 0" in str(exc)
    else:
        raise AssertionError("investment_amount=0 应抛出 ValueError")

    try:
        run_stress_test(
            fund_type="active_fund",
            investment_amount=100000,
            max_tolerable_loss_rate="120%",
        )
    except ValueError as exc:
        assert "0 到 100%" in str(exc)
    else:
        raise AssertionError("max_tolerable_loss_rate=120% 应抛出 ValueError")


def test_run_stress_test_allows_configured_thresholds() -> None:
    """验证压力测试阈值通过规则配置注入，不硬编码在判断调用处。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当自定义阈值未生效时抛出。
    """

    rule = StressTestRule(
        severity_thresholds={
            "index_fund": (0.20, 0.40, 0.60),  # type: ignore[dict-item]
            "active_fund": (0.20, 0.40, 0.60),  # type: ignore[dict-item]
            "bond_fund": (0.20, 0.40, 0.60),  # type: ignore[dict-item]
            "enhanced_index": (0.20, 0.40, 0.60),  # type: ignore[dict-item]
            "qdii_fund": (0.20, 0.40, 0.60),  # type: ignore[dict-item]
            "fof_fund": (0.20, 0.40, 0.60),  # type: ignore[dict-item]
        },
    )

    result = run_stress_test(
        fund_type="qdii_fund",
        investment_amount=100000,
        max_tolerable_loss_rate="70%",
        rule=rule,
    )

    assert [scenario.severity for scenario in result.scenarios] == [
        "normal",
        "extreme",
        "historical_worst",
    ]
