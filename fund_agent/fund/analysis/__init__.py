"""基金分析计算公共入口。"""

from fund_agent.fund.analysis.alpha_judge import (
    AlphaJudgment,
    AlphaJudgmentRule,
    AlphaObservation,
    judge_alpha_nature,
    observations_from_attributions,
)
from fund_agent.fund.analysis.checklist import (
    ChecklistItem,
    ChecklistResult,
    ChecklistRule,
    run_checklist,
)
from fund_agent.fund.analysis.consistency_check import (
    ConsistencyCheckResult,
    ConsistencyDimensionResult,
    ConsistencyRule,
    check_consistency,
)
from fund_agent.fund.analysis.final_judgment import (
    FinalJudgment,
    FinalJudgmentDecision,
    FinalJudgmentQualityGateStatus,
    FinalJudgmentSource,
    derive_final_judgment,
)
from fund_agent.fund.analysis.investor_return import (
    BehaviorGapResult,
    FundFlowResult,
    InvestorExperienceResult,
    analyze_investor_experience,
    calculate_behavior_gap,
    judge_fund_flow,
)
from fund_agent.fund.analysis.r_abc import (
    RabcAttribution,
    RabcInput,
    calculate_r_abc,
    calculate_r_abc_from_bundle,
    calculate_r_abc_series,
)
from fund_agent.fund.analysis.risk_check import (
    RiskCheckItem,
    RiskCheckResult,
    RiskCheckRule,
    StressScenarioResult,
    StressTestResult,
    StressTestRule,
    run_risk_checks,
    run_stress_test,
)

__all__ = [
    "AlphaJudgment",
    "AlphaJudgmentRule",
    "AlphaObservation",
    "BehaviorGapResult",
    "ChecklistItem",
    "ChecklistResult",
    "ChecklistRule",
    "ConsistencyCheckResult",
    "ConsistencyDimensionResult",
    "ConsistencyRule",
    "FinalJudgment",
    "FinalJudgmentDecision",
    "FinalJudgmentQualityGateStatus",
    "FinalJudgmentSource",
    "FundFlowResult",
    "InvestorExperienceResult",
    "RabcAttribution",
    "RabcInput",
    "RiskCheckItem",
    "RiskCheckResult",
    "RiskCheckRule",
    "StressScenarioResult",
    "StressTestResult",
    "StressTestRule",
    "analyze_investor_experience",
    "calculate_behavior_gap",
    "calculate_r_abc",
    "calculate_r_abc_from_bundle",
    "calculate_r_abc_series",
    "check_consistency",
    "derive_final_judgment",
    "judge_alpha_nature",
    "judge_fund_flow",
    "observations_from_attributions",
    "run_checklist",
    "run_risk_checks",
    "run_stress_test",
]
