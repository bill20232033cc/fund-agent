"""Application 层公共入口。

本包提供 UI-facing use-case facade。Application 只负责把 CLI 构造的
typed request 委托给 Service，不实现基金领域规则、审计规则或证据锚点规则。
"""

from fund_agent.application.use_cases import (
    ExtractionScoreUseCase,
    ExtractionSnapshotUseCase,
    FundAnalysisUseCase,
    GoldenAnswerUseCase,
    GoldenPrefillUseCase,
    QualityGateUseCase,
    ThermometerUseCase,
)
from fund_agent.services import (
    AnalyzeMode,
    ExtractionScoreRequest,
    ExtractionSnapshotRequest,
    FinalJudgment,
    FundAnalysisDeveloperOverrides,
    FundAnalysisRequest,
    FundAnalysisResult,
    FundChecklistResult,
    GoldenAnswerBuildRequest,
    GoldenPrefillRequest,
    MoneyHorizon,
    QualityGateBlockedError,
    QualityGateNotRunBlockedError,
    QualityGatePolicy,
    QualityGateRequest,
    ThermometerBatchResult,
    ThermometerReading,
    ThermometerRequest,
    ValuationState,
)

__all__ = [
    "AnalyzeMode",
    "ExtractionScoreRequest",
    "ExtractionScoreUseCase",
    "ExtractionSnapshotRequest",
    "ExtractionSnapshotUseCase",
    "FinalJudgment",
    "FundAnalysisDeveloperOverrides",
    "FundAnalysisRequest",
    "FundAnalysisResult",
    "FundAnalysisUseCase",
    "FundChecklistResult",
    "GoldenAnswerBuildRequest",
    "GoldenAnswerUseCase",
    "GoldenPrefillRequest",
    "GoldenPrefillUseCase",
    "MoneyHorizon",
    "QualityGateBlockedError",
    "QualityGateNotRunBlockedError",
    "QualityGatePolicy",
    "QualityGateRequest",
    "QualityGateUseCase",
    "ThermometerBatchResult",
    "ThermometerReading",
    "ThermometerRequest",
    "ThermometerUseCase",
    "ValuationState",
]
