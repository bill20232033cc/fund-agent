"""买入前检查清单测试。"""

from __future__ import annotations

from decimal import Decimal

import pytest

from fund_agent.fund.analysis import (
    BehaviorGapResult,
    ChecklistRule,
    ConsistencyCheckResult,
    ConsistencyDimensionResult,
    FundFlowResult,
    InvestorExperienceResult,
    RabcAttribution,
    RiskCheckItem,
    RiskCheckResult,
    build_explicit_valuation_resolution,
    run_checklist,
)
from fund_agent.fund.analysis.valuation_state import ValuationStateResolution
from fund_agent.fund.extractors.models import EvidenceAnchor, ExtractedField


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


def _rabc(net_excess_return: Decimal | None = Decimal("0.03")) -> RabcAttribution:
    """构造 R=A+B-C 归因结果。

    Args:
        net_excess_return: 净超额收益。

    Returns:
        R=A+B-C 归因结果。

    Raises:
        无显式抛出。
    """

    return RabcAttribution(
        period="2024",
        status="missing" if net_excess_return is None else "computed",
        total_return_r=Decimal("0.10") if net_excess_return is not None else None,
        beta_return_b=Decimal("0.05") if net_excess_return is not None else None,
        alpha_return_a=Decimal("0.05") if net_excess_return is not None else None,
        explicit_cost_c=Decimal("0.02") if net_excess_return is not None else None,
        net_excess_return=net_excess_return,
        turnover_cost=Decimal("0.003") if net_excess_return is not None else None,
        anchors=(_anchor("§3", "rabc"),),
        note=None,
    )


def _manager_alignment(disclosure: str | None = "基金经理持有本基金") -> ExtractedField[dict[str, object]]:
    """构造 §9 持有披露字段。

    Args:
        disclosure: 持有披露文本。

    Returns:
        抽取字段。

    Raises:
        无显式抛出。
    """

    return ExtractedField(
        value=None if disclosure is None else {"manager_holding": disclosure},
        anchors=() if disclosure is None else (_anchor("§9", "manager_holding"),),
        extraction_mode="missing" if disclosure is None else "direct",
        note=None,
    )


def _investor_experience(status: str = "positive") -> InvestorExperienceResult:
    """构造投资者获得感结果。

    Args:
        status: 获得感状态。

    Returns:
        投资者获得感结果。

    Raises:
        无显式抛出。
    """

    behavior_gap = BehaviorGapResult(
        status="missing" if status == "insufficient_data" else "computed",
        product_return=Decimal("0.10") if status != "insufficient_data" else None,
        investor_return=Decimal("0.12") if status == "positive" else Decimal("0.08"),
        behavior_gap=Decimal("0.02") if status == "positive" else Decimal("-0.02"),
        anchors=(_anchor("§3", "investor_return"),),
        note=None,
    )
    fund_flow = FundFlowResult(
        signal="normal",
        beginning_share=Decimal("100"),
        ending_share=Decimal("110"),
        net_change=Decimal("10"),
        net_change_ratio=Decimal("0.1"),
        anchors=(_anchor("§10", "share_change"),),
        reason="fixture",
    )
    return InvestorExperienceResult(
        status=status,  # type: ignore[arg-type]
        behavior_gap=behavior_gap,
        fund_flow=fund_flow,
        reasons=("fixture",),
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
        anchors=(_anchor("§4", "style"),),
        reason="fixture",
    )
    return ConsistencyCheckResult(
        dimensions=(dimension,),
        overall_status=status,  # type: ignore[arg-type]
        overall_signal=signal,  # type: ignore[arg-type]
        reasons=("fixture",),
    )


def _risk_result(overall_status: str = "pass") -> RiskCheckResult:
    """构造否决项检查结果。

    Args:
        overall_status: 汇总状态。

    Returns:
        否决项检查结果。

    Raises:
        无显式抛出。
    """

    item_status = "veto" if overall_status == "veto" else "pass"
    item = RiskCheckItem(
        code="liquidation_risk",
        status=item_status,  # type: ignore[arg-type]
        current_value="100000000",
        threshold=">50000000",
        anchors=(_anchor("§1", "fund_scale"),),
        reason="fixture",
    )
    return RiskCheckResult(
        overall_status=overall_status,  # type: ignore[arg-type]
        items=(item,),
        veto_items=(item,) if overall_status == "veto" else (),
        watch_items=(item,) if overall_status == "watch" else (),
        next_minimum_verification="fixture",
    )


def _external_anchor() -> EvidenceAnchor:
    """构造温度计外部数据锚点。

    Args:
        无。

    Returns:
        external_api 证据锚点。

    Raises:
        无显式抛出。
    """

    return EvidenceAnchor(
        source_kind="external_api",
        document_year=None,
        section_id="thermometer",
        page_number=None,
        table_id="fixture_source",
        row_locator="000300:2024-12-31",
        note="fixture thermometer",
    )


def test_run_checklist_returns_seven_green_items_when_all_inputs_pass() -> None:
    """验证全部安全输入下 7 问题均为绿灯。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当检查清单未全绿时抛出。
    """

    result = run_checklist(
        rabc_attribution=_rabc(),
        manager_alignment=_manager_alignment(),
        investor_experience=_investor_experience("positive"),
        consistency_result=_consistency("green"),
        risk_check_result=_risk_result("pass"),
        valuation_state="low",
        user_money_horizon_years=4,
    )

    assert result.overall_signal == "green"
    assert result.overall_status == "pass"
    assert len(result.items) == 7
    assert [item.code for item in result.items] == [
        "net_excess_covers_cost",
        "manager_alignment",
        "investor_return",
        "consistency",
        "survival",
        "valuation",
        "money_horizon",
    ]
    assert not result.red_items
    assert result.next_minimum_verification == "7 个检查问题均为绿灯，下一步进入程序审计。"


def test_run_checklist_blocks_on_negative_core_signals() -> None:
    """验证核心红灯信号会让检查清单汇总阻断。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当红灯未阻断时抛出。
    """

    result = run_checklist(
        rabc_attribution=_rabc(Decimal("-0.01")),
        manager_alignment=_manager_alignment("基金经理未持有本基金"),
        investor_experience=_investor_experience("negative"),
        consistency_result=_consistency("red"),
        risk_check_result=_risk_result("veto"),
        valuation_state="high",
        money_horizon="too_short",
    )

    assert result.overall_signal == "red"
    assert result.overall_status == "block"
    assert {item.code for item in result.red_items} == {
        "net_excess_covers_cost",
        "investor_return",
        "consistency",
        "survival",
        "valuation",
        "money_horizon",
    }
    assert "net_excess_covers_cost" in result.next_minimum_verification


def test_run_checklist_reports_gray_when_explicit_inputs_are_missing() -> None:
    """验证缺失显式输入时返回灰灯而非强判。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当缺失输入被强行判定时抛出。
    """

    result = run_checklist(
        rabc_attribution=_rabc(None),
        manager_alignment=_manager_alignment(None),
        investor_experience=_investor_experience("insufficient_data"),
        consistency_result=_consistency("gray"),
        risk_check_result=_risk_result("pass"),
    )

    assert result.overall_signal == "gray"
    assert {item.code for item in result.gray_items} == {
        "net_excess_covers_cost",
        "manager_alignment",
        "investor_return",
        "consistency",
        "valuation",
        "money_horizon",
    }
    assert "显式输入" in result.next_minimum_verification


def test_run_checklist_warns_for_fair_valuation_and_uncertain_horizon() -> None:
    """验证估值合理和资金期限接近阈值时输出黄灯。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当黄灯规则未生效时抛出。
    """

    result = run_checklist(
        rabc_attribution=_rabc(),
        manager_alignment=_manager_alignment("从业人员持有本基金"),
        investor_experience=_investor_experience("neutral"),
        consistency_result=_consistency("yellow"),
        risk_check_result=_risk_result("watch"),
        valuation_state="fair",
        user_money_horizon_years="2.5",
    )

    assert result.overall_signal == "yellow"
    assert {item.code for item in result.yellow_items} == {
        "investor_return",
        "consistency",
        "survival",
        "valuation",
        "money_horizon",
    }


def test_run_checklist_uses_configured_money_horizon_threshold() -> None:
    """验证资金期限阈值可通过规则配置注入。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当配置阈值未生效时抛出。
    """

    result = run_checklist(
        rabc_attribution=_rabc(),
        manager_alignment=_manager_alignment(),
        investor_experience=_investor_experience("positive"),
        consistency_result=_consistency("green"),
        risk_check_result=_risk_result("pass"),
        valuation_state="low",
        user_money_horizon_years=4,
        rule=ChecklistRule(minimum_horizon_years=Decimal("5")),
    )

    money_horizon_item = result.items[-1]
    assert money_horizon_item.code == "money_horizon"
    assert money_horizon_item.signal == "yellow"


def test_run_checklist_rejects_bool_money_horizon_years() -> None:
    """验证用户资金年限拒绝 bool，避免被当作 0/1 年。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 bool 未被拒绝时抛出。
    """

    with pytest.raises(ValueError, match="不能为布尔值"):
        run_checklist(
            rabc_attribution=_rabc(),
            manager_alignment=_manager_alignment(),
            investor_experience=_investor_experience("positive"),
            consistency_result=_consistency("green"),
            risk_check_result=_risk_result("pass"),
            valuation_state="low",
            user_money_horizon_years=True,
        )


def test_run_checklist_handles_inconsistent_veto_result_without_crashing() -> None:
    """验证否决项结果内部不一致时检查清单不崩溃。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当检查清单因空 veto_items 崩溃或未红灯时抛出。
    """

    inconsistent_risk = RiskCheckResult(
        overall_status="veto",
        items=(),
        veto_items=(),
        watch_items=(),
        next_minimum_verification="fixture",
    )

    result = run_checklist(
        rabc_attribution=_rabc(),
        manager_alignment=_manager_alignment(),
        investor_experience=_investor_experience("positive"),
        consistency_result=_consistency("green"),
        risk_check_result=inconsistent_risk,
        valuation_state="low",
        user_money_horizon_years=4,
    )

    survival_item = next(item for item in result.items if item.code == "survival")
    assert survival_item.signal == "red"
    assert "unknown" in survival_item.reason


def test_run_checklist_uses_valuation_resolution_as_projection_truth() -> None:
    """验证第 6 问使用 valuation resolution 的状态、原因和锚点。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 检查清单未投影 resolution 时抛出。
    """

    anchor = _external_anchor()
    resolution = ValuationStateResolution(
        state="high",
        source="self_owned_thermometer",
        reason="自建温度计 fixture 高估。",
        anchors=(anchor,),
        disclaimer_required=True,
        index_code="000300",
        index_name="沪深300",
    )

    result = run_checklist(
        rabc_attribution=_rabc(),
        manager_alignment=_manager_alignment(),
        investor_experience=_investor_experience("positive"),
        consistency_result=_consistency("green"),
        risk_check_result=_risk_result("pass"),
        valuation_state="low",
        valuation_resolution=resolution,
        user_money_horizon_years=4,
    )

    valuation_item = next(item for item in result.items if item.code == "valuation")
    assert valuation_item.signal == "red"
    assert valuation_item.status == "block"
    assert valuation_item.anchors == (anchor,)
    assert valuation_item.reason == "自建温度计 fixture 高估。"


def test_run_checklist_explicit_unavailable_resolution_keeps_gray() -> None:
    """验证显式 unavailable 保留手动灰灯且携带 user_input 锚点。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 显式 unavailable 未灰灯时抛出。
    """

    result = run_checklist(
        rabc_attribution=_rabc(),
        manager_alignment=_manager_alignment(),
        investor_experience=_investor_experience("positive"),
        consistency_result=_consistency("green"),
        risk_check_result=_risk_result("pass"),
        valuation_resolution=build_explicit_valuation_resolution("unavailable"),
        user_money_horizon_years=4,
    )

    valuation_item = next(item for item in result.items if item.code == "valuation")
    assert valuation_item.signal == "gray"
    assert valuation_item.anchors[0].source_kind == "derived"
    assert valuation_item.anchors[0].section_id == "user_input"
