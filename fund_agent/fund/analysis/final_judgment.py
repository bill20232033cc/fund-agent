"""最终判断派生策略。

本模块属于 Agent 层基金能力，服务模板第 7 章“是否值得持有--最终判断”
和检查清单第 7 问。它只消费已形成的结构化分析结果，不读取年报、PDF、
缓存、UI 或 Service 运行状态。
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final, Literal

from fund_agent.fund.analysis.checklist import ChecklistResult
from fund_agent.fund.analysis.risk_check import RiskCheckResult, StressTestResult

FinalJudgment = Literal["worth_holding", "needs_attention", "suggest_replace"]
FinalJudgmentSource = Literal["derived", "developer_override"]
FinalJudgmentQualityGateStatus = Literal["pass", "warn", "block", "not_run"]

_JUDGMENT_ORDER: Final[dict[FinalJudgment, int]] = {
    "worth_holding": 0,
    "needs_attention": 1,
    "suggest_replace": 2,
}
_RISK_VETO_REASON: Final[str] = "模板第 6 章存在否决项，最终判断应建议替换。"
_CHECKLIST_RED_REASON: Final[str] = "检查清单存在红灯问题，最终判断应建议替换。"
_STRESS_MINUS_20_REASON: Final[str] = "基础 -20% 压力场景超过用户可承受亏损，最终判断应建议替换。"
_QUALITY_BLOCK_REASON: Final[str] = "质量 gate 为 block，当前数据质量不足，只能判为需要关注。"
_QUALITY_NOT_RUN_REASON: Final[str] = "质量 gate 未运行，缺少质量证明，只能判为需要关注。"
_RISK_WATCH_REASON: Final[str] = "否决项存在跟踪或数据不足项目，需要最小验证。"
_CHECKLIST_WATCH_REASON: Final[str] = "检查清单存在黄灯或灰灯问题，需要最小验证。"
_STRESS_WATCH_REASON: Final[str] = "压力测试接近或超过承受边界，需要最小验证。"
_WORTH_HOLDING_REASON: Final[str] = "检查清单全绿、否决项通过、质量 gate 通过，当前证据下值得持有。"
_FAIL_SAFE_REASON: Final[str] = "未命中更明确的持有或替换条件，按 fail-safe 判为需要关注。"


@dataclass(frozen=True, slots=True)
class FinalJudgmentDecision:
    """最终判断选择结果。

    Attributes:
        selected_judgment: 报告实际采用的最终判断，见模板第 7 章。
        derived_judgment: Agent 层基金能力根据检查清单、否决项、压力测试与质量 gate 派生的判断。
        source: 实际采用判断的来源。
        override_judgment: 开发覆盖判断；未覆盖时为 `None`。
        reasons: 派生判断触发原因，按规则优先级去重。
        conflict_reasons: 开发覆盖与系统派生冲突时的原因，供 R2 审计使用。
    """

    selected_judgment: FinalJudgment
    derived_judgment: FinalJudgment
    source: FinalJudgmentSource
    override_judgment: FinalJudgment | None
    reasons: tuple[str, ...]
    conflict_reasons: tuple[str, ...]


def derive_final_judgment(
    *,
    checklist_result: ChecklistResult,
    risk_check_result: RiskCheckResult,
    stress_test_result: StressTestResult,
    quality_gate_status: FinalJudgmentQualityGateStatus,
    quality_gate_not_run_reason: str | None,
    override_judgment: FinalJudgment | None = None,
) -> FinalJudgmentDecision:
    """派生模板第 7 章最终持有判断。

    Args:
        checklist_result: 7 问题检查清单结果，包含第 7 问资金期限信号。
        risk_check_result: 模板第 6 章否决项检查结果。
        stress_test_result: 模板第 6 章压力测试结果。
        quality_gate_status: Service 已归一化的质量 gate 状态。
        quality_gate_not_run_reason: 质量 gate 未运行原因；仅用于补充派生说明。
        override_judgment: developer override 模式下的显式最终判断覆盖。

    Returns:
        最终判断选择结果。

    Raises:
        ValueError: 当质量 gate 状态不属于允许集合时抛出。
    """

    if quality_gate_status not in {"pass", "warn", "block", "not_run"}:
        raise ValueError("quality_gate_status 必须是 pass / warn / block / not_run")

    derived_judgment, reasons = _derive_without_override(
        checklist_result=checklist_result,
        risk_check_result=risk_check_result,
        stress_test_result=stress_test_result,
        quality_gate_status=quality_gate_status,
        quality_gate_not_run_reason=quality_gate_not_run_reason,
    )
    source: FinalJudgmentSource = "derived"
    selected_judgment = derived_judgment
    conflict_reasons: tuple[str, ...] = ()
    if override_judgment is not None:
        source = "developer_override"
        selected_judgment = override_judgment
        if override_judgment != derived_judgment:
            conflict_reasons = (
                f"开发覆盖判断 {override_judgment} 与系统派生判断 {derived_judgment} 不一致。",
            )
    return FinalJudgmentDecision(
        selected_judgment=selected_judgment,
        derived_judgment=derived_judgment,
        source=source,
        override_judgment=override_judgment,
        reasons=reasons,
        conflict_reasons=conflict_reasons,
    )


def _derive_without_override(
    *,
    checklist_result: ChecklistResult,
    risk_check_result: RiskCheckResult,
    stress_test_result: StressTestResult,
    quality_gate_status: FinalJudgmentQualityGateStatus,
    quality_gate_not_run_reason: str | None,
) -> tuple[FinalJudgment, tuple[str, ...]]:
    """执行不含开发覆盖的最终判断派生。

    Args:
        checklist_result: 7 问题检查清单结果。
        risk_check_result: 否决项检查结果。
        stress_test_result: 压力测试结果。
        quality_gate_status: Service 已归一化的质量 gate 状态。
        quality_gate_not_run_reason: 质量 gate 未运行原因。

    Returns:
        派生判断与原因列表。

    Raises:
        无显式抛出。
    """

    candidates: list[tuple[FinalJudgment, str]] = []
    if risk_check_result.veto_items:
        candidates.append(("suggest_replace", _RISK_VETO_REASON))
    if checklist_result.red_items:
        candidates.append(("suggest_replace", _CHECKLIST_RED_REASON))
    if _minus_20_beyond_tolerance(stress_test_result):
        candidates.append(("suggest_replace", _STRESS_MINUS_20_REASON))
    if quality_gate_status == "block":
        candidates.append(("needs_attention", _QUALITY_BLOCK_REASON))
    if quality_gate_status == "not_run":
        reason = _QUALITY_NOT_RUN_REASON
        if quality_gate_not_run_reason:
            reason = f"{reason}原因：{quality_gate_not_run_reason}。"
        candidates.append(("needs_attention", reason))
    if risk_check_result.watch_items:
        candidates.append(("needs_attention", _RISK_WATCH_REASON))
    if checklist_result.yellow_items or checklist_result.gray_items:
        candidates.append(("needs_attention", _CHECKLIST_WATCH_REASON))
    if _stress_needs_attention(stress_test_result):
        candidates.append(("needs_attention", _STRESS_WATCH_REASON))
    if not candidates and _all_green_pass(
        checklist_result=checklist_result,
        risk_check_result=risk_check_result,
        stress_test_result=stress_test_result,
        quality_gate_status=quality_gate_status,
    ):
        candidates.append(("worth_holding", _WORTH_HOLDING_REASON))
    if not candidates:
        candidates.append(("needs_attention", _FAIL_SAFE_REASON))

    return _highest_priority_judgment(candidates), _dedupe_reasons(candidates)


def _minus_20_beyond_tolerance(stress_test_result: StressTestResult) -> bool:
    """判断 -20% 基础压力场景是否超过用户承受能力。

    Args:
        stress_test_result: 压力测试结果。

    Returns:
        若 `minus_20` 场景为 `beyond_tolerance` 则返回 `True`。

    Raises:
        无显式抛出。
    """

    return any(
        scenario.code == "minus_20" and scenario.capacity_status == "beyond_tolerance"
        for scenario in stress_test_result.scenarios
    )


def _stress_needs_attention(stress_test_result: StressTestResult) -> bool:
    """判断压力测试是否存在需关注但非基础场景否决的信号。

    Args:
        stress_test_result: 压力测试结果。

    Returns:
        存在 `near_limit` 或非 `minus_20` 的 `beyond_tolerance` 时返回 `True`。

    Raises:
        无显式抛出。
    """

    return any(
        scenario.capacity_status == "near_limit"
        or (scenario.code != "minus_20" and scenario.capacity_status == "beyond_tolerance")
        for scenario in stress_test_result.scenarios
    )


def _all_green_pass(
    *,
    checklist_result: ChecklistResult,
    risk_check_result: RiskCheckResult,
    stress_test_result: StressTestResult,
    quality_gate_status: FinalJudgmentQualityGateStatus,
) -> bool:
    """判断是否满足值得持有的严格正向条件。

    Args:
        checklist_result: 7 问题检查清单结果。
        risk_check_result: 否决项检查结果。
        stress_test_result: 压力测试结果。
        quality_gate_status: Service 已归一化的质量 gate 状态。

    Returns:
        所有正向条件均满足时返回 `True`。

    Raises:
        无显式抛出。
    """

    return (
        checklist_result.overall_signal == "green"
        and not checklist_result.red_items
        and not checklist_result.yellow_items
        and not checklist_result.gray_items
        and risk_check_result.overall_status == "pass"
        and not risk_check_result.veto_items
        and not risk_check_result.watch_items
        and quality_gate_status in {"pass", "warn"}
        and not _stress_needs_attention(stress_test_result)
        and not _minus_20_beyond_tolerance(stress_test_result)
    )


def _highest_priority_judgment(candidates: list[tuple[FinalJudgment, str]]) -> FinalJudgment:
    """从候选判断中选择最高优先级。

    Args:
        candidates: 按规则顺序收集的判断候选。

    Returns:
        最高优先级判断。

    Raises:
        无显式抛出。
    """

    return max((judgment for judgment, _reason in candidates), key=_JUDGMENT_ORDER.__getitem__)


def _dedupe_reasons(candidates: list[tuple[FinalJudgment, str]]) -> tuple[str, ...]:
    """按规则顺序去重派生原因。

    Args:
        candidates: 按规则顺序收集的判断候选。

    Returns:
        去重后的原因元组。

    Raises:
        无显式抛出。
    """

    seen: set[str] = set()
    reasons: list[str] = []
    for _judgment, reason in candidates:
        if reason in seen:
            continue
        seen.add(reason)
        reasons.append(reason)
    return tuple(reasons)
