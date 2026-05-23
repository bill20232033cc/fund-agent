"""最终判断派生策略测试。"""

from __future__ import annotations

from dataclasses import replace
from decimal import Decimal

from fund_agent.fund.analysis import (
    ChecklistItem,
    ChecklistResult,
    RiskCheckItem,
    RiskCheckResult,
    StressScenarioResult,
    StressTestResult,
    derive_final_judgment,
)


def _checklist(signal: str = "green") -> ChecklistResult:
    """构造检查清单 fixture。

    Args:
        signal: 汇总和单题信号。

    Returns:
        检查清单结果。

    Raises:
        无显式抛出。
    """

    status_by_signal = {
        "green": "pass",
        "yellow": "watch",
        "red": "block",
        "gray": "insufficient_data",
    }
    item = ChecklistItem(
        code="valuation",
        question="当前估值处于什么位置？",
        signal=signal,  # type: ignore[arg-type]
        status=status_by_signal[signal],  # type: ignore[index,arg-type]
        anchors=(),
        reason="fixture",
    )
    return ChecklistResult(
        items=(item,),
        overall_signal=signal,  # type: ignore[arg-type]
        overall_status=status_by_signal[signal],  # type: ignore[index,arg-type]
        red_items=(item,) if signal == "red" else (),
        yellow_items=(item,) if signal == "yellow" else (),
        gray_items=(item,) if signal == "gray" else (),
        next_minimum_verification="fixture",
    )


def _risk(status: str = "pass") -> RiskCheckResult:
    """构造否决项检查 fixture。

    Args:
        status: 单项否决状态。

    Returns:
        否决项检查结果。

    Raises:
        无显式抛出。
    """

    item = RiskCheckItem(
        code="liquidation_risk",
        status=status,  # type: ignore[arg-type]
        current_value="1000000000",
        threshold=">50000000 元",
        anchors=(),
        reason="fixture",
    )
    return RiskCheckResult(
        overall_status=status,  # type: ignore[arg-type]
        items=(item,),
        veto_items=(item,) if status == "veto" else (),
        watch_items=(item,) if status in {"watch", "insufficient_data"} else (),
        next_minimum_verification="fixture",
    )


def _stress(
    *,
    minus_20_status: str = "within_tolerance",
    minus_40_status: str = "within_tolerance",
) -> StressTestResult:
    """构造压力测试 fixture。

    Args:
        minus_20_status: `minus_20` 场景承受状态。
        minus_40_status: `minus_40` 场景承受状态。

    Returns:
        压力测试结果。

    Raises:
        无显式抛出。
    """

    scenarios = (
        StressScenarioResult(
            code="minus_20",
            decline_rate=Decimal("-0.20"),
            investment_amount=Decimal("10000"),
            account_balance=Decimal("8000"),
            floating_loss_amount=Decimal("2000"),
            severity="normal",
            capacity_status=minus_20_status,  # type: ignore[arg-type]
            threshold="fixture",
            reason="fixture",
        ),
        StressScenarioResult(
            code="minus_40",
            decline_rate=Decimal("-0.40"),
            investment_amount=Decimal("10000"),
            account_balance=Decimal("6000"),
            floating_loss_amount=Decimal("4000"),
            severity="extreme",
            capacity_status=minus_40_status,  # type: ignore[arg-type]
            threshold="fixture",
            reason="fixture",
        ),
    )
    return StressTestResult(
        fund_type="active_fund",
        investment_amount=Decimal("10000"),
        max_tolerable_loss_rate=Decimal("0.50"),
        scenarios=scenarios,
        worst_scenario=scenarios[-1],
        anchors=(),
        next_minimum_verification="fixture",
    )


def test_derive_final_judgment_replaces_on_risk_veto() -> None:
    """验证否决项优先派生建议替换。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当否决项未触发替换判断时抛出。
    """

    decision = derive_final_judgment(
        checklist_result=_checklist(),
        risk_check_result=_risk("veto"),
        stress_test_result=_stress(),
        quality_gate_status="pass",
        quality_gate_not_run_reason=None,
    )

    assert decision.selected_judgment == "suggest_replace"
    assert decision.source == "derived"


def test_derive_final_judgment_replaces_on_checklist_red() -> None:
    """验证检查清单红灯派生建议替换。"""

    decision = derive_final_judgment(
        checklist_result=_checklist("red"),
        risk_check_result=_risk(),
        stress_test_result=_stress(),
        quality_gate_status="pass",
        quality_gate_not_run_reason=None,
    )

    assert decision.derived_judgment == "suggest_replace"


def test_derive_final_judgment_replaces_on_minus_20_beyond_tolerance() -> None:
    """验证 -20% 基础压力场景越界派生建议替换。"""

    decision = derive_final_judgment(
        checklist_result=_checklist(),
        risk_check_result=_risk(),
        stress_test_result=_stress(minus_20_status="beyond_tolerance"),
        quality_gate_status="pass",
        quality_gate_not_run_reason=None,
    )

    assert decision.derived_judgment == "suggest_replace"


def test_derive_final_judgment_needs_attention_on_gate_block_or_not_run() -> None:
    """验证允许继续的质量 gate block/not_run 只派生需要关注。"""

    block_decision = derive_final_judgment(
        checklist_result=_checklist(),
        risk_check_result=_risk(),
        stress_test_result=_stress(),
        quality_gate_status="block",
        quality_gate_not_run_reason=None,
    )
    not_run_decision = derive_final_judgment(
        checklist_result=_checklist(),
        risk_check_result=_risk(),
        stress_test_result=_stress(),
        quality_gate_status="not_run",
        quality_gate_not_run_reason="policy=off",
    )

    assert block_decision.derived_judgment == "needs_attention"
    assert not_run_decision.derived_judgment == "needs_attention"
    assert "policy=off" in not_run_decision.reasons[0]


def test_derive_final_judgment_needs_attention_on_watch_signals() -> None:
    """验证黄灯、灰灯、watch 和压力接近边界派生需要关注。"""

    decision = derive_final_judgment(
        checklist_result=_checklist("yellow"),
        risk_check_result=_risk("watch"),
        stress_test_result=_stress(minus_40_status="near_limit"),
        quality_gate_status="pass",
        quality_gate_not_run_reason=None,
    )

    assert decision.derived_judgment == "needs_attention"
    assert len(decision.reasons) >= 3


def test_derive_final_judgment_worth_holding_on_all_green_pass() -> None:
    """验证全绿、否决项通过、质量 gate 通过时派生值得持有。"""

    decision = derive_final_judgment(
        checklist_result=_checklist(),
        risk_check_result=_risk(),
        stress_test_result=_stress(),
        quality_gate_status="pass",
        quality_gate_not_run_reason=None,
    )

    assert decision.derived_judgment == "worth_holding"


def test_derive_final_judgment_accumulates_reasons_and_keeps_highest_priority() -> None:
    """验证多规则同时触发时原因累积且最高优先级为建议替换。"""

    decision = derive_final_judgment(
        checklist_result=_checklist("red"),
        risk_check_result=_risk("watch"),
        stress_test_result=_stress(minus_40_status="near_limit"),
        quality_gate_status="block",
        quality_gate_not_run_reason=None,
    )

    assert decision.derived_judgment == "suggest_replace"
    assert len(decision.reasons) == len(set(decision.reasons))
    assert any("红灯" in reason for reason in decision.reasons)
    assert any("质量 gate" in reason for reason in decision.reasons)


def test_derive_final_judgment_override_selects_override_and_records_conflict() -> None:
    """验证开发覆盖选择 override，同时保留系统派生和冲突原因。"""

    decision = derive_final_judgment(
        checklist_result=replace(_checklist("gray"), overall_signal="gray"),
        risk_check_result=_risk(),
        stress_test_result=_stress(),
        quality_gate_status="pass",
        quality_gate_not_run_reason=None,
        override_judgment="worth_holding",
    )

    assert decision.selected_judgment == "worth_holding"
    assert decision.derived_judgment == "needs_attention"
    assert decision.source == "developer_override"
    assert decision.conflict_reasons
