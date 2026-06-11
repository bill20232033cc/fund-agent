"""基金分析 Service 编排层。

本模块属于 Service 层，负责把 P1 结构化抽取、P2 Agent 层基金分析、
模板渲染和程序审计串成一个用例。它不直接读取年报文件、PDF 或缓存，
所有基金文档访问都通过 `FundDataExtractor` 进入 Agent 层基金能力边界。
"""

from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass, replace
from decimal import Decimal
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Literal, Mapping, Protocol

from fund_agent.config.paths import DEFAULT_GOLDEN_ANSWER_JSON
from fund_agent.fund.analysis import (
    AlphaJudgment,
    ChecklistResult,
    ConsistencyCheckResult,
    FinalJudgment,
    FinalJudgmentDecision,
    FinalJudgmentQualityGateStatus,
    InvestorExperienceResult,
    RabcAttribution,
    RiskCheckResult,
    StressTestResult,
    THERMOMETER_REPORT_DISCLAIMER,
    analyze_investor_experience,
    build_explicit_valuation_resolution,
    build_thermometer_failure_anchor,
    build_thermometer_valuation_resolution,
    build_unavailable_valuation_resolution,
    calculate_r_abc_from_bundle,
    check_consistency,
    derive_final_judgment,
    judge_alpha_nature,
    resolve_valuation_index_target,
    resolve_tracking_error_for_risk,
    run_checklist,
    run_risk_checks,
    run_stress_test,
    ValuationStateResolution,
)
from fund_agent.fund.analysis.thermometer_calculator import ThermometerCalculationError
from fund_agent.fund.annual_evidence import (
    AnnualEvidenceBundle,
    AnnualEvidenceLoader,
    AnnualEvidenceScopeRequest,
    CURRENT_YEAR_REQUIRED_PRIOR_YEARS_OPTIONAL,
    MAX_ANNUAL_EVIDENCE_YEARS,
)
from fund_agent.fund.audit import ProgrammaticAuditResult, run_programmatic_audit
from fund_agent.fund.data.thermometer import ThermometerSnapshot
from fund_agent.fund.data.thermometer_types import ThermometerBatchResult, ThermometerReading
from fund_agent.fund.data_extractor import FundDataExtractor, StructuredFundDataBundle
from fund_agent.config.paths import DEFAULT_SELECTED_FUNDS_CSV
from fund_agent.fund.fund_type import FundType
from fund_agent.fund.quality_gate import GATE_STATUS_BLOCK, QualityGateResult
from fund_agent.fund.quality_gate_integration import check_quality_gate_fund_membership, run_quality_gate_for_bundle
from fund_agent.host import HostRunContext, HostRuntimeRunner
from fund_agent.fund.template import TemplateRenderInput, TemplateRenderResult, render_template_report
from fund_agent.services.chapter_orchestrator import (
    ChapterOrchestrationPolicy,
    ChapterOrchestrationResult,
    ChapterOrchestratorLLMClients,
    build_chapter_orchestration_input,
    orchestrate_chapters,
)
from fund_agent.services.final_chapter_assembler import (
    FinalAssemblyPolicy,
    FinalChapterAssemblyInput,
    FinalChapterAssemblyResult,
    assemble_final_chapters,
)
from fund_agent.config.llm import load_llm_provider_config_from_env
from fund_agent.services.execution_contract import (
    FundLLMAnalysisInput,
    FundLLMExecutionContract,
    FundLLMExecutionRequest,
    FundLLMRuntimePlan,
    ProviderRuntimeBudget,
    QualityFailClosedPolicy,
    QualityGatePolicy,
    QualityPolicyDeclaration,
    SafeDiagnosticPolicy,
    derive_host_timeout_seconds,
    normalize_fund_llm_analysis_input,
)
from fund_agent.services.llm_provider import build_chapter_llm_clients
from fund_agent.services.thermometer_service import ThermometerRequest, ThermometerService as IndexThermometerService

ValuationState = Literal["low", "fair", "high", "unavailable"]
MoneyHorizon = Literal["long_enough", "uncertain", "too_short"]
AnalyzeMode = Literal["product", "developer_override"]
AnalyzeCommandSource = Literal["analyze", "checklist"]
DEFAULT_GOLDEN_ANSWER_PATH = DEFAULT_GOLDEN_ANSWER_JSON
LLM_REPORT_HOST_TIMEOUT_CHAPTER_COUNT = 6


class _FundDataExtractor(Protocol):
    """基金结构化抽取器协议。

    该协议让 Service 测试可以注入 fake extractor，同时保持生产路径使用
    `FundDataExtractor`，避免 Service 直接读取基金文档。
    """

    async def extract(
        self,
        fund_code: str,
        report_year: int,
        *,
        force_refresh: bool = False,
    ) -> StructuredFundDataBundle:
        """抽取 P1 结构化基金数据。

        Args:
            fund_code: 基金代码。
            report_year: 年报年份。
            force_refresh: 是否强制刷新底层仓库和缓存。

        Returns:
            P1 结构化基金数据包。

        Raises:
            Exception: 允许具体抽取器传播异常。
        """


class _ThermometerService(Protocol):
    """自建温度计 Service 协议。

    该协议用于 P19-S3 自动估值路径测试注入 fake provider。Service 层只调用
    自建指数温度计请求，不使用公开页 `FundThermometerAdapter` 作为分析真源。
    """

    async def run(
        self,
        request: ThermometerRequest,
    ) -> ThermometerSnapshot | ThermometerReading | ThermometerBatchResult:
        """执行温度计查询。

        Args:
            request: 显式温度计请求。

        Returns:
            温度计结果；P19-S3 自动路径只接受 `ThermometerReading`。

        Raises:
            ThermometerCalculationError: 自建温度计计算或数据质量错误。
            Exception: 允许具体实现传播其他契约错误。
        """


class _AnnualEvidenceLoader(Protocol):
    """多年年报证据 loader 协议。

    该协议用于 Service 层注入 fake loader。Service 只传递显式 scope 和当前年份
    结构化数据包，不直接读取年报 repository、PDF cache 或来源 helper。
    """

    async def load(
        self,
        scope: AnnualEvidenceScopeRequest,
        *,
        current_year_bundle: StructuredFundDataBundle,
    ) -> AnnualEvidenceBundle:
        """加载多年年报证据。

        Args:
            scope: Fund 层年度证据作用域。
            current_year_bundle: 当前年份结构化数据包。

        Returns:
            多年年报证据 bundle。

        Raises:
            Exception: 允许 Fund 层 loader 传播异常。
        """


@dataclass(frozen=True, slots=True)
class FundAnalysisDeveloperOverrides:
    """开发覆盖参数，只能在 developer override mode 使用。

    Attributes:
        equity_position: R=A+B-C 使用的显式股票仓位，见模板第 2 章。
        actual_style: 言行一致性使用的显式实际持仓风格，见模板第 3 章。
        actual_equity_position: 言行一致性使用的显式实际股票仓位，见模板第 3 章。
        manager_tenure_months: 基金经理管理本基金月数，见模板第 6 章。
        peer_fee_median: 同类总费率中位数，见模板第 6 章。
        tracking_error: 指数基金跟踪误差，见模板第 6 章。
        money_horizon: 用户资金期限分类，见 7 问题检查清单。
        current_stage: 当前阶段与关键变化说明，见模板第 5 章。
        final_judgment_override: 开发覆盖最终判断，见模板第 7 章。
        quality_gate_policy: 报告质量 gate 策略。
        quality_gate_source_csv: 精选基金池 CSV，用于取得 App 类别。
        quality_gate_output_dir: quality gate 显式输出目录。
        quality_gate_run_id: quality gate 运行 ID；为空时 Service 生成唯一 ID。
        quality_gate_golden_answer_path: strict golden answer JSON 路径。
    """

    equity_position: Decimal | str | int | float | None = None
    actual_style: str | None = None
    actual_equity_position: Decimal | str | int | float | None = None
    manager_tenure_months: int | None = None
    peer_fee_median: Decimal | str | int | float | None = None
    tracking_error: Decimal | str | int | float | None = None
    money_horizon: MoneyHorizon | None = None
    current_stage: str | None = None
    final_judgment_override: FinalJudgment | None = None
    quality_gate_policy: QualityGatePolicy | None = None
    quality_gate_source_csv: Path | None = None
    quality_gate_output_dir: Path | None = None
    quality_gate_run_id: str | None = None
    quality_gate_golden_answer_path: Path | None = None


@dataclass(frozen=True, slots=True)
class FundAnalysisRequest:
    """基金分析 Service 请求。

    Attributes:
        fund_code: 基金代码。
        report_year: 年报年份。
        investment_amount: 压力测试投入金额，见模板第 6 章。
        max_tolerable_loss_rate: 最大可承受亏损比例，见模板第 6 章。
        valuation_state: 估值状态，见 7 问题检查清单；`None` 表示允许自动温度计解析。
        thermometer_cache_dir: 自动温度计缓存目录。
        user_money_horizon_years: 用户资金不用年限，见 7 问题检查清单。
        force_refresh: 是否强制刷新底层数据。
        mode: analyze 契约模式，默认 product。
        developer_overrides: 开发覆盖参数；product mode 下必须为空。
        command_source: 触发分析核心的命令来源，用于默认 quality gate run_id 命名。
    """

    fund_code: str
    report_year: int = 2024
    investment_amount: Decimal | str | int | float = Decimal("10000")
    max_tolerable_loss_rate: Decimal | str | int | float | None = None
    valuation_state: ValuationState | None = None
    thermometer_cache_dir: Path | None = None
    user_money_horizon_years: Decimal | str | int | float | None = None
    force_refresh: bool = False
    mode: AnalyzeMode = "product"
    developer_overrides: FundAnalysisDeveloperOverrides | None = None
    command_source: AnalyzeCommandSource = "analyze"


@dataclass(frozen=True, slots=True)
class MultiYearAnnualAnalysisRequest:
    """多年年报分析 Service 请求，见模板第 5 章“当前阶段”。

    Attributes:
        fund_code: 基金代码。
        target_year: 当前必需年报年份。
        start_year: 最早 optional prior 年报年份。
        max_years: 年报证据硬上限，MVP 为 1..5。
        investment_amount: 压力测试投入金额。
        max_tolerable_loss_rate: 最大可承受亏损比例。
        valuation_state: 估值状态；`None` 表示沿用单年分析自动估值行为。
        thermometer_cache_dir: 自动温度计缓存目录。
        user_money_horizon_years: 用户资金不用年限。
        force_refresh: 是否统一强制刷新。
        quality_gate_policy: quality gate 策略。
        quality_gate_source_csv: quality gate 精选基金池 CSV 路径。
        quality_gate_output_dir: quality gate 输出目录。
        quality_gate_run_id: quality gate 运行 ID。
        quality_gate_golden_answer_path: strict golden answer JSON 路径。
    """

    fund_code: str
    target_year: int = 2025
    start_year: int = 2021
    max_years: int = MAX_ANNUAL_EVIDENCE_YEARS
    investment_amount: Decimal | str | int | float = Decimal("10000")
    max_tolerable_loss_rate: Decimal | str | int | float | None = None
    valuation_state: ValuationState | None = None
    thermometer_cache_dir: Path | None = None
    user_money_horizon_years: Decimal | str | int | float | None = None
    force_refresh: bool = False
    quality_gate_policy: QualityGatePolicy = "block"
    quality_gate_source_csv: Path | None = None
    quality_gate_output_dir: Path | None = None
    quality_gate_run_id: str | None = None
    quality_gate_golden_answer_path: Path | None = None


@dataclass(frozen=True, slots=True)
class MultiYearAnnualAnalysisResult:
    """多年年报分析 Service 结果。

    Attributes:
        current_year_result: 当前必需年份的既有单年分析结果。
        annual_evidence_bundle: 多年年报证据 bundle。
        used_years: 已用于跨年证据的可用年份。
        gap_years: 可降级缺口年份。
        fail_closed_years: fail-closed 年份。
    """

    current_year_result: FundAnalysisResult
    annual_evidence_bundle: AnnualEvidenceBundle
    used_years: tuple[int, ...]
    gap_years: tuple[int, ...]
    fail_closed_years: tuple[int, ...]

    @property
    def report_markdown(self) -> str:
        """返回当前年份报告 Markdown。

        Args:
            无。

        Returns:
            当前必需年份的 8 章 Markdown 报告。

        Raises:
            无显式抛出。
        """

        return self.current_year_result.report_markdown


@dataclass(frozen=True, slots=True)
class ResolvedAnalyzeContract:
    """Service 内部解析后的 analyze 契约。

    Attributes:
        mode: analyze 契约模式。
        equity_position: R=A+B-C 使用的显式股票仓位，见模板第 2 章。
        actual_style: 言行一致性使用的显式实际持仓风格，见模板第 3 章。
        actual_equity_position: 言行一致性使用的显式实际股票仓位，见模板第 3 章。
        manager_tenure_months: 基金经理管理本基金月数，见模板第 6 章。
        peer_fee_median: 同类总费率中位数，见模板第 6 章。
        tracking_error: 指数基金跟踪误差，见模板第 6 章。
        money_horizon: 用户资金期限分类，见 7 问题检查清单。
        current_stage: 当前阶段与关键变化说明，见模板第 5 章。
        final_judgment_override: 开发覆盖最终判断，见模板第 7 章。
        quality_gate_policy: 报告质量 gate 策略。
        quality_gate_source_csv: 精选基金池 CSV，用于取得 App 类别。
        quality_gate_output_dir: quality gate 显式输出目录。
        quality_gate_run_id: quality gate 运行 ID。
        quality_gate_golden_answer_path: strict golden answer JSON 路径。
    """

    mode: AnalyzeMode
    equity_position: Decimal | str | int | float | None
    actual_style: str | None
    actual_equity_position: Decimal | str | int | float | None
    manager_tenure_months: int | None
    peer_fee_median: Decimal | str | int | float | None
    tracking_error: Decimal | str | int | float | None
    money_horizon: MoneyHorizon | None
    current_stage: str | None
    final_judgment_override: FinalJudgment | None
    quality_gate_policy: QualityGatePolicy
    quality_gate_source_csv: Path | None
    quality_gate_output_dir: Path | None
    quality_gate_run_id: str | None
    quality_gate_golden_answer_path: Path | None


@dataclass(frozen=True, slots=True)
class FundAnalysisResult:
    """基金分析 Service 结果。

    Attributes:
        structured_data: P1 结构化基金数据包。
        rabc_attribution: R=A+B-C 单期归因结果。
        consistency_result: 言行一致性检查结果。
        investor_experience: 投资者获得感分析结果。
        risk_check_result: 否决项检查结果。
        stress_test_result: 压力测试结果。
        checklist_result: 7 问题检查清单结果。
        valuation_state_resolution: 估值状态结构化真源。
        final_judgment_decision: 最终判断选择契约。
        render_result: 模板渲染结果。
        audit_result: 程序审计结果。
        quality_gate_result: quality gate 结果；未运行时为空。
        quality_gate_not_run_reason: quality gate 未运行原因。
    """

    structured_data: StructuredFundDataBundle
    rabc_attribution: RabcAttribution
    consistency_result: ConsistencyCheckResult
    investor_experience: InvestorExperienceResult
    risk_check_result: RiskCheckResult
    stress_test_result: StressTestResult
    checklist_result: ChecklistResult
    valuation_state_resolution: ValuationStateResolution
    final_judgment_decision: FinalJudgmentDecision
    render_result: TemplateRenderResult
    audit_result: ProgrammaticAuditResult
    quality_gate_result: QualityGateResult | None = None
    quality_gate_not_run_reason: str | None = None

    @property
    def report_markdown(self) -> str:
        """返回完整 8 章 Markdown 报告。

        Args:
            无。

        Returns:
            完整 Markdown 报告文本。

        Raises:
            无显式抛出。
        """

        return self.render_result.report_markdown


@dataclass(frozen=True, slots=True)
class FundLLMAnalysisResult:
    """Service LLM 分析用例结果，见模板第 0-7 章。

    Attributes:
        structured_data: P1 结构化基金数据包。
        final_judgment_decision: Agent/Fund 层确定性最终判断契约。
        llm_orchestration_result: Gate 3 第 1-6 章 LLM 编排结果。
        final_assembly_result: Gate 4 第 0/7 章与完整报告总装结果。
        quality_gate_result: quality gate 结果；未运行时为空。
        quality_gate_not_run_reason: quality gate 未运行原因。
    """

    structured_data: StructuredFundDataBundle
    final_judgment_decision: FinalJudgmentDecision
    llm_orchestration_result: ChapterOrchestrationResult
    final_assembly_result: FinalChapterAssemblyResult
    quality_gate_result: QualityGateResult | None = None
    quality_gate_not_run_reason: str | None = None

    @property
    def report_markdown(self) -> str:
        """返回 LLM 路径总装后的完整 Markdown 报告。

        Args:
            无。

        Returns:
            完整 Markdown 报告文本。

        Raises:
            ValueError: 当 Gate 3/4 未 accepted，或总装未产出完整报告时抛出。
        """

        report_markdown = self.final_assembly_result.report_markdown
        if report_markdown is not None:
            return report_markdown
        issue_reasons = ", ".join(
            issue.reason for issue in self.final_assembly_result.issues
        ) or "no final assembly issue recorded"
        raise ValueError(
            "LLM 分析报告尚未完成，不能读取 report_markdown："
            f"orchestration_status={self.llm_orchestration_result.status}, "
            f"final_assembly_status={self.final_assembly_result.status}, "
            f"issues={issue_reasons}"
        )


@dataclass(frozen=True, slots=True)
class FundLLMHostedRunResult:
    """Service 投影给 UI 的 Host 托管 LLM run 安全结果，见模板第 0-7 章。

    Attributes:
        analysis_result: LLM 分析结果；Host 未产出业务结果时为空。
        host_status: Host 终态字符串。
        host_run_id: Host run ID。
        host_elapsed_ms: Host run 耗时毫秒。
        host_timeout_classification: Host timeout 分类字符串。
        host_safe_diagnostics: Host 安全诊断。
        host_event_count: Host 事件数量。
        host_completed_at_iso: Host 完成时间 ISO 字符串。
        host_operation_result_present: Host operation result 是否存在。
    """

    analysis_result: FundLLMAnalysisResult | None
    host_status: str
    host_run_id: str
    host_elapsed_ms: int | None
    host_timeout_classification: str | None
    host_safe_diagnostics: Mapping[str, object]
    host_event_count: int
    host_completed_at_iso: str | None
    host_operation_result_present: bool


@dataclass(frozen=True, slots=True)
class FundChecklistResult:
    """基金检查清单 Service 结果。

    Attributes:
        structured_data: P1 结构化基金数据包。
        rabc_attribution: R=A+B-C 单期归因结果。
        consistency_result: 言行一致性检查结果。
        investor_experience: 投资者获得感分析结果。
        risk_check_result: 否决项检查结果。
        stress_test_result: 压力测试结果。
        checklist_result: 7 问题检查清单结果。
        valuation_state_resolution: 估值状态结构化真源。
        final_judgment_decision: 最终判断选择契约。
        quality_gate_result: quality gate 结果；未运行时为空。
        quality_gate_not_run_reason: quality gate 未运行原因。
    """

    structured_data: StructuredFundDataBundle
    rabc_attribution: RabcAttribution
    consistency_result: ConsistencyCheckResult
    investor_experience: InvestorExperienceResult
    risk_check_result: RiskCheckResult
    stress_test_result: StressTestResult
    checklist_result: ChecklistResult
    valuation_state_resolution: ValuationStateResolution
    final_judgment_decision: FinalJudgmentDecision
    quality_gate_result: QualityGateResult | None = None
    quality_gate_not_run_reason: str | None = None


@dataclass(frozen=True, slots=True)
class _AnalysisCoreResult:
    """Service 内部复用的分析核心结果。

    Attributes:
        structured_data: P1 结构化基金数据包。
        rabc_attribution: R=A+B-C 单期归因结果。
        alpha_judgment: 超额收益性质判断。
        consistency_result: 言行一致性检查结果。
        investor_experience: 投资者获得感分析结果。
        risk_check_result: 否决项检查结果。
        stress_test_result: 压力测试结果。
        checklist_result: 7 问题检查清单结果。
        valuation_state_resolution: 估值状态结构化真源。
        final_judgment_decision: 最终判断选择契约。
        current_stage: 当前阶段说明。
        quality_gate_result: quality gate 结果；未运行时为空。
        quality_gate_not_run_reason: quality gate 未运行原因。
    """

    structured_data: StructuredFundDataBundle
    rabc_attribution: RabcAttribution
    alpha_judgment: AlphaJudgment
    consistency_result: ConsistencyCheckResult
    investor_experience: InvestorExperienceResult
    risk_check_result: RiskCheckResult
    stress_test_result: StressTestResult
    checklist_result: ChecklistResult
    valuation_state_resolution: ValuationStateResolution
    final_judgment_decision: FinalJudgmentDecision
    current_stage: str | None
    quality_gate_result: QualityGateResult | None
    quality_gate_not_run_reason: str | None


@dataclass(frozen=True, slots=True)
class _ValidatedRequest:
    """Service 内部校验后的请求事实。

    Attributes:
        fund_code: 已规范化的 6 位基金代码。
    """

    fund_code: str


class QualityGateBlockedError(ValueError):
    """quality gate 阻断报告输出的结构化异常。

    Attributes:
        quality_gate_result: 阻断报告的 quality gate 结果。
        policy: 触发阻断的策略，固定为 `block`。
    """

    def __init__(self, quality_gate_result: QualityGateResult) -> None:
        """初始化 quality gate 阻断异常。

        Args:
            quality_gate_result: 阻断报告的 quality gate 结果。

        Returns:
            无返回值。

        Raises:
            无显式抛出。
        """

        self.quality_gate_result = quality_gate_result
        self.policy: QualityGatePolicy = "block"
        super().__init__(
            f"质量 gate 阻断报告输出：status={quality_gate_result.status}, "
            f"issues={len(quality_gate_result.issues)}"
        )


class QualityGateNotRunBlockedError(ValueError):
    """quality gate 在 block 策略下未运行的结构化异常。

    Attributes:
        reason: quality gate 未运行原因。
        policy: 触发阻断的策略，固定为 `block`。
    """

    def __init__(self, reason: str) -> None:
        """初始化未运行阻断异常。

        Args:
            reason: quality gate 未运行原因。

        Returns:
            无返回值。

        Raises:
            无显式抛出。
        """

        self.reason = reason
        self.policy: QualityGatePolicy = "block"
        super().__init__(f"质量 gate 未运行：{reason}")


class _LLMIncompleteHostRunError(RuntimeError):
    """LLM 分析未完成时用于让 Host runner 形成 failed 终态的内部异常。"""


class FundAnalysisService:
    """基金分析用例编排 Service。

    Service 只负责按当前 MVP 流程协调 Agent 层基金能力，不承载基金领域规则。
    领域判断、审计和模板规则均保留在 `fund_agent.fund`。
    """

    def __init__(
        self,
        extractor: _FundDataExtractor | None = None,
        thermometer_service: _ThermometerService | None = None,
        annual_evidence_loader: _AnnualEvidenceLoader | None = None,
    ) -> None:
        """初始化基金分析 Service。

        Args:
            extractor: P1 结构化抽取器；未提供时使用默认 `FundDataExtractor`。
            thermometer_service: 自建温度计 Service；未提供时使用默认实现。
            annual_evidence_loader: 多年年报证据 loader；未提供时使用默认实现。

        Returns:
            无返回值。

        Raises:
            无显式抛出。
        """

        self._extractor = extractor or FundDataExtractor()
        self._thermometer_service = thermometer_service or IndexThermometerService()
        self._annual_evidence_loader = annual_evidence_loader or AnnualEvidenceLoader()

    async def analyze(self, request: FundAnalysisRequest) -> FundAnalysisResult:
        """执行单只基金完整分析并生成 8 章报告。

        Args:
            request: 显式分析参数，不使用 `extra_payload`。

        Returns:
            基金分析 Service 结果，包含 Markdown 报告和程序审计结果。

        Raises:
            ValueError: 当基金代码、年份、基金类型或审计结果非法时抛出。
            QualityGateBlockedError: 当 quality gate 在 block 策略下阻断报告时抛出。
            QualityGateNotRunBlockedError: 当 quality gate 在 block 策略下未运行时抛出。
            Exception: 允许底层抽取器或 Agent 层基金能力传播异常。
        """

        core_result = await self._run_analysis_core(
            replace(request, command_source="analyze")
        )
        render_result = render_template_report(
            TemplateRenderInput(
                structured_data=core_result.structured_data,
                rabc_attributions=(core_result.rabc_attribution,),
                alpha_judgment=core_result.alpha_judgment,
                consistency_result=core_result.consistency_result,
                investor_experience=core_result.investor_experience,
                risk_check_result=core_result.risk_check_result,
                stress_test_result=core_result.stress_test_result,
                checklist_result=core_result.checklist_result,
                valuation_state_resolution=core_result.valuation_state_resolution,
                final_judgment_decision=core_result.final_judgment_decision,
                current_stage=core_result.current_stage,
            )
        )
        audit_result = run_programmatic_audit(render_result.audit_input)
        if not audit_result.passed:
            issue_text = "；".join(issue.message for issue in audit_result.issues)
            raise ValueError(f"程序审计未通过：{issue_text}")
        return FundAnalysisResult(
            structured_data=core_result.structured_data,
            rabc_attribution=core_result.rabc_attribution,
            consistency_result=core_result.consistency_result,
            investor_experience=core_result.investor_experience,
            risk_check_result=core_result.risk_check_result,
            stress_test_result=core_result.stress_test_result,
            checklist_result=core_result.checklist_result,
            valuation_state_resolution=core_result.valuation_state_resolution,
            final_judgment_decision=core_result.final_judgment_decision,
            render_result=render_result,
            audit_result=audit_result,
            quality_gate_result=core_result.quality_gate_result,
            quality_gate_not_run_reason=core_result.quality_gate_not_run_reason,
        )

    async def checklist(self, request: FundAnalysisRequest) -> FundChecklistResult:
        """执行单只基金买入前检查清单用例。

        Args:
            request: 显式分析参数，不使用 `extra_payload`。

        Returns:
            检查清单结果、估值状态和最终判断，不渲染完整 8 章报告。

        Raises:
            ValueError: 当基金代码、年份、基金类型或请求契约非法时抛出。
            QualityGateBlockedError: 当 quality gate 在 block 策略下阻断报告时抛出。
            QualityGateNotRunBlockedError: 当 quality gate 在 block 策略下未运行时抛出。
            Exception: 允许底层抽取器或 Agent 层基金能力传播异常。
        """

        core_result = await self._run_analysis_core(
            replace(request, command_source="checklist")
        )
        return FundChecklistResult(
            structured_data=core_result.structured_data,
            rabc_attribution=core_result.rabc_attribution,
            consistency_result=core_result.consistency_result,
            investor_experience=core_result.investor_experience,
            risk_check_result=core_result.risk_check_result,
            stress_test_result=core_result.stress_test_result,
            checklist_result=core_result.checklist_result,
            valuation_state_resolution=core_result.valuation_state_resolution,
            final_judgment_decision=core_result.final_judgment_decision,
            quality_gate_result=core_result.quality_gate_result,
            quality_gate_not_run_reason=core_result.quality_gate_not_run_reason,
        )

    async def analyze_multi_year_annual(
        self,
        request: MultiYearAnnualAnalysisRequest,
    ) -> MultiYearAnnualAnalysisResult:
        """执行多年年报分析产品用例。

        Args:
            request: 多年年报分析显式请求。

        Returns:
            当前年份分析结果和多年年报证据 bundle。

        Raises:
            ValueError: 当请求契约非法时抛出。
            Exception: 允许单年分析或 Fund 层多年证据 loader 传播异常。
        """

        normalized_fund_code = _normalize_fund_code(request.fund_code)
        prior_years = _prior_years_from_range(
            target_year=request.target_year,
            start_year=request.start_year,
            max_years=request.max_years,
        )
        annual_scope = AnnualEvidenceScopeRequest(
            fund_code=normalized_fund_code,
            target_year=request.target_year,
            required_years=(request.target_year,),
            optional_years=prior_years,
            max_years=request.max_years,
            force_refresh=request.force_refresh,
            degradation_policy=CURRENT_YEAR_REQUIRED_PRIOR_YEARS_OPTIONAL,
        )
        developer_overrides = _multi_year_developer_overrides(request)
        current_year_result = await self.analyze(
            FundAnalysisRequest(
                fund_code=normalized_fund_code,
                report_year=request.target_year,
                investment_amount=request.investment_amount,
                max_tolerable_loss_rate=request.max_tolerable_loss_rate,
                valuation_state=request.valuation_state,
                thermometer_cache_dir=request.thermometer_cache_dir,
                user_money_horizon_years=request.user_money_horizon_years,
                force_refresh=request.force_refresh,
                mode="developer_override" if developer_overrides is not None else "product",
                developer_overrides=developer_overrides,
                command_source="analyze",
            )
        )
        annual_bundle = await self._annual_evidence_loader.load(
            annual_scope,
            current_year_bundle=current_year_result.structured_data,
        )
        return MultiYearAnnualAnalysisResult(
            current_year_result=current_year_result,
            annual_evidence_bundle=annual_bundle,
            used_years=annual_bundle.available_years,
            gap_years=annual_bundle.gap_years,
            fail_closed_years=annual_bundle.fail_closed_years,
        )

    async def analyze_with_llm(
        self,
        request: FundAnalysisRequest,
        *,
        llm_clients: ChapterOrchestratorLLMClients,
        chapter_policy: ChapterOrchestrationPolicy | None = None,
        assembly_policy: FinalAssemblyPolicy | None = None,
        host_context: HostRunContext | None = None,
    ) -> FundLLMAnalysisResult:
        """执行显式 LLM 章节写作分析用例。

        该方法属于 Route C Gate 4 Slice 4B：先复用 `_run_analysis_core()` 得到
        结构化事实、quality gate 状态和最终判断，再编排模板第 1-6 章 LLM
        write-audit-repair，最后总装模板第 0 章与第 7 章。它不构造生产 LLM
        provider，不回退到确定性 renderer，不改变 `analyze()` / `checklist()`
        行为，也不把显式参数塞入 `extra_payload`。

        Args:
            request: 显式分析参数。
            llm_clients: Gate 3 writer/auditor LLM Protocol clients，必须显式注入。
            chapter_policy: 可选章节编排策略；默认生成模板第 1-6 章。
            assembly_policy: 可选最终总装策略；默认要求完整第 1-6 章 accepted。
            host_context: 可选 Host run 上下文；Service 只用它检查 run lifecycle。

        Returns:
            LLM 分析结果，包含 Gate 3 编排结果和 Gate 4 总装结果。

        Raises:
            ValueError: 当请求契约、章节编排输入或总装输入非法时抛出。
            QualityGateBlockedError: 当 quality gate 在 block 策略下阻断报告时抛出。
            QualityGateNotRunBlockedError: 当 quality gate 在 block 策略下未运行时抛出。
            Exception: 允许底层抽取器或 Agent 层基金能力传播异常。
        """

        _record_host_phase_started(host_context, phase="analysis_core")
        phase_started = time.monotonic()
        core_result = await self._run_analysis_core(
            replace(request, command_source="analyze")
        )
        _record_host_phase_completed(
            host_context,
            phase="analysis_core",
            phase_started=phase_started,
        )
        _raise_if_host_cancelled(host_context)
        orchestration_input = build_chapter_orchestration_input(
            fund_code=core_result.structured_data.fund_code,
            report_year=core_result.structured_data.report_year,
            structured_data=core_result.structured_data,
            policy=chapter_policy or ChapterOrchestrationPolicy(),
        )
        orchestration_result = orchestrate_chapters(
            orchestration_input,
            llm_clients=llm_clients,
            host_context=host_context,
        )
        _raise_if_host_cancelled(host_context)
        _record_host_phase_started(host_context, phase="final_assembly")
        phase_started = time.monotonic()
        final_assembly_result = assemble_final_chapters(
            FinalChapterAssemblyInput(
                fund_code=core_result.structured_data.fund_code,
                report_year=core_result.structured_data.report_year,
                orchestration_result=orchestration_result,
                final_judgment_decision=core_result.final_judgment_decision,
                policy=assembly_policy or FinalAssemblyPolicy(),
            )
        )
        _record_host_phase_completed(
            host_context,
            phase="final_assembly",
            phase_started=phase_started,
        )
        return FundLLMAnalysisResult(
            structured_data=core_result.structured_data,
            final_judgment_decision=core_result.final_judgment_decision,
            llm_orchestration_result=orchestration_result,
            final_assembly_result=final_assembly_result,
            quality_gate_result=core_result.quality_gate_result,
            quality_gate_not_run_reason=core_result.quality_gate_not_run_reason,
        )

    async def analyze_with_llm_execution(
        self,
        execution_request: FundLLMExecutionRequest,
        *,
        host_context: HostRunContext | None = None,
    ) -> FundLLMAnalysisResult:
        """执行 Service-owned typed LLM execution request。

        该方法只消费 `build_fund_llm_execution_request()` 已准备好的 Service
        runtime plan 和 provider clients，不读取环境变量、不重新构造 provider，
        并继续沿用 `analyze_with_llm()` 的 quality gate 异常传播和不完整总装
        fail-closed 语义。

        Args:
            execution_request: Service 内部 LLM 执行请求，包含业务契约、runtime plan
                和 provider clients。
            host_context: 可选 Host run 上下文；Service 只用它检查 run lifecycle。

        Returns:
            LLM 分析结果，包含 Gate 3 编排结果和 Gate 4 总装结果。

        Raises:
            ValueError: 当请求契约、章节编排输入或总装输入非法时抛出。
            QualityGateBlockedError: 当 quality gate 在 block 策略下阻断报告时抛出。
            QualityGateNotRunBlockedError: 当 quality gate 在 block 策略下未运行时抛出。
            Exception: 允许底层抽取器或 Agent 层基金能力传播异常。
        """

        _validate_llm_execution_fail_closed_policy(
            execution_request.runtime_plan.quality_fail_closed_policy
        )
        return await self.analyze_with_llm(
            _fund_analysis_request_from_llm_input(
                execution_request.contract.analysis_input
            ),
            llm_clients=execution_request.llm_clients,
            chapter_policy=execution_request.runtime_plan.chapter_policy,
            assembly_policy=execution_request.runtime_plan.assembly_policy,
            host_context=host_context,
        )

    def analyze_with_llm_hosted(
        self,
        request: FundAnalysisRequest,
        *,
        event_sink: Callable[[object], None] | None = None,
    ) -> FundLLMHostedRunResult:
        """通过 Service-owned Host run 执行显式 LLM 分析。

        该方法是 UI `--use-llm` 的唯一 hosted LLM 用例入口。Service 先构造
        `FundLLMExecutionRequest` 和 provider clients，再把同步 operation、
        operation name、Host timeout 标量和可选 event sink 交给 Host runner。
        Host 只接收通用 lifecycle 字段，不接收基金代码、章节策略或 provider
        runtime 业务字段。

        Args:
            request: CLI/UI 构造的显式分析请求。
            event_sink: 可选 Host 通用事件 sink，用于 UI stderr progress。

        Returns:
            Service 投影后的 hosted run 安全结果。

        Raises:
            LLMProviderConfigError: 当 provider 配置缺失或非法时抛出。
            LLMProviderConstructionError: 当 provider clients 构造失败时抛出。
            QualityGateBlockedError: 当 quality gate 在 block 策略下阻断报告时抛出。
            QualityGateNotRunBlockedError: 当 quality gate 在 block 策略下未运行时抛出。
            ValueError: 当请求或执行契约非法时抛出。
        """

        execution_request = build_fund_llm_execution_request(
            request,
            opt_in_mode="explicit_cli_flag",
        )
        quality_gate_exception: QualityGateBlockedError | QualityGateNotRunBlockedError | None = None
        incomplete_result: FundLLMAnalysisResult | None = None

        def operation(host_context: HostRunContext) -> FundLLMAnalysisResult:
            """Service-owned async bridge，Host runner 不管理 event loop。"""

            nonlocal incomplete_result, quality_gate_exception
            try:
                result = asyncio.run(
                    self.analyze_with_llm_execution(
                        execution_request,
                        host_context=host_context,
                    )
                )
                if result.final_assembly_result.report_markdown is None:
                    incomplete_result = result
                    host_context.record_diagnostic(
                        final_assembly_status=result.final_assembly_result.status,
                        error_type=_LLMIncompleteHostRunError.__name__,
                    )
                    raise _LLMIncompleteHostRunError("llm_result_incomplete")
                return result
            except (QualityGateBlockedError, QualityGateNotRunBlockedError) as exc:
                quality_gate_exception = exc
                host_context.record_diagnostic(error_type=type(exc).__name__)
                raise

        host_result = HostRuntimeRunner().run_sync(
            operation_name="fund_analysis_llm_report",
            operation=operation,
            timeout_seconds=execution_request.runtime_plan.host_timeout_seconds,
            event_sink=event_sink,
        )
        if quality_gate_exception is not None:
            raise quality_gate_exception
        if incomplete_result is not None:
            host_result = replace(host_result, operation_result=incomplete_result)
        return _project_hosted_llm_run_result(host_result)

    async def _resolve_valuation_state(
        self,
        *,
        request: FundAnalysisRequest,
        structured_data: StructuredFundDataBundle,
        fund_type: FundType,
    ) -> ValuationStateResolution:
        """解析检查清单第 6 问估值状态，见模板第 7 章。

        Args:
            request: 基金分析请求。
            structured_data: P1 结构化基金数据。
            fund_type: 已识别基金类型。

        Returns:
            估值状态结构化真源。

        Raises:
            ValueError: 温度计 provider 返回不符合 P19-S3 自动路径契约的结果时抛出。
        """

        if request.valuation_state is not None:
            return build_explicit_valuation_resolution(request.valuation_state)

        target = resolve_valuation_index_target(
            fund_type=fund_type,
            index_profile=structured_data.index_profile,
            benchmark=structured_data.benchmark,
        )
        if target.status != "mapped" or target.index_code is None:
            return build_unavailable_valuation_resolution(target)

        try:
            result = await self._thermometer_service.run(
                ThermometerRequest(
                    cache_dir=request.thermometer_cache_dir,
                    force_refresh=request.force_refresh,
                    index_code=target.index_code,
                )
            )
        except ThermometerCalculationError as exc:
            unavailable_reason = f"自建温度计计算失败：{exc}"
            return ValuationStateResolution(
                state="unavailable",
                source="unavailable_thermometer",
                reason=f"自动估值不可用：{unavailable_reason}",
                anchors=(
                    *target.anchors,
                    build_thermometer_failure_anchor(
                        index_code=target.index_code,
                        index_name=target.index_name or target.index_code,
                        unavailable_reason=unavailable_reason,
                    ),
                ),
                disclaimer_required=True,
                index_code=target.index_code,
                index_name=target.index_name,
                unavailable_reason=unavailable_reason,
                disclaimer=THERMOMETER_REPORT_DISCLAIMER,
            )
        if not isinstance(result, ThermometerReading):
            raise ValueError("自动估值温度计 provider 必须返回 ThermometerReading")
        if result.index_code != target.index_code:
            raise ValueError(
                f"自动估值温度计返回指数与目标不一致：target={target.index_code}, "
                f"result={result.index_code}"
            )
        return build_thermometer_valuation_resolution(result)

    async def _run_analysis_core(self, request: FundAnalysisRequest) -> _AnalysisCoreResult:
        """执行 `analyze` 和 `checklist` 共享的确定性分析核心。

        Args:
            request: 基金分析请求。

        Returns:
            共享分析核心结果。

        Raises:
            ValueError: 当请求契约或结构化数据非法时抛出。
            QualityGateBlockedError: 当 quality gate 在 block 策略下阻断输出时抛出。
            QualityGateNotRunBlockedError: 当 quality gate 在 block 策略下未运行时抛出。
            Exception: 允许底层抽取器或 Agent 层基金能力传播异常。
        """

        resolved_contract = _resolve_analyze_contract(request)
        validated_request = _validate_request(request, resolved_contract)
        _check_pool_membership_before_extraction(
            validated_request=validated_request,
            resolved_contract=resolved_contract,
        )
        structured_data = await self._extractor.extract(
            validated_request.fund_code,
            request.report_year,
            force_refresh=request.force_refresh,
        )
        quality_gate_result, quality_gate_not_run_reason = _run_quality_gate_if_enabled(
            structured_data=structured_data,
            resolved_contract=resolved_contract,
            command_source=request.command_source,
        )
        if resolved_contract.quality_gate_policy == "block":
            if quality_gate_result is None:
                raise QualityGateNotRunBlockedError(quality_gate_not_run_reason or "unknown")
            if quality_gate_result.status == GATE_STATUS_BLOCK:
                raise QualityGateBlockedError(quality_gate_result)
        quality_gate_status = _resolve_final_judgment_quality_gate_status(
            quality_gate_result=quality_gate_result,
            quality_gate_not_run_reason=quality_gate_not_run_reason,
        )
        fund_type = _extract_fund_type(structured_data)
        rabc_attribution = calculate_r_abc_from_bundle(
            structured_data,
            period=str(structured_data.report_year),
            equity_position=resolved_contract.equity_position,
        )
        # MVP 限制：judge_alpha_nature 需要 observations_from_attributions，
        # 但该函数要求 market_environments 和 source_confidences，
        # 当前 Service 层无法提供这些外部输入，故传空元组。
        alpha_judgment = judge_alpha_nature((), fund_type=fund_type)
        consistency_result = check_consistency(
            product_profile=structured_data.product_profile,
            manager_strategy_text=structured_data.manager_strategy_text,
            holdings_snapshot=structured_data.holdings_snapshot,
            turnover_rate=structured_data.turnover_rate,
            actual_style=resolved_contract.actual_style,
            actual_equity_position=resolved_contract.actual_equity_position,
        )
        investor_experience = analyze_investor_experience(
            nav_benchmark_performance=structured_data.nav_benchmark_performance,
            investor_return=structured_data.investor_return,
            share_change=structured_data.share_change,
        )
        risk_check_result = run_risk_checks(
            basic_identity=structured_data.basic_identity,
            fee_schedule=structured_data.fee_schedule,
            consistency_result=consistency_result,
            fund_type=fund_type,
            manager_tenure_months=resolved_contract.manager_tenure_months,
            peer_fee_median=resolved_contract.peer_fee_median,
            tracking_error=resolve_tracking_error_for_risk(
                tracking_error_field=structured_data.tracking_error,
                developer_override=resolved_contract.tracking_error,
                developer_override_enabled=resolved_contract.mode == "developer_override",
                fund_type=fund_type,
            ),
        )
        stress_test_result = run_stress_test(
            fund_type=fund_type,
            investment_amount=request.investment_amount,
            max_tolerable_loss_rate=request.max_tolerable_loss_rate,
            anchors=structured_data.basic_identity.anchors,
        )
        valuation_state_resolution = await self._resolve_valuation_state(
            request=request,
            structured_data=structured_data,
            fund_type=fund_type,
        )
        checklist_result = run_checklist(
            rabc_attribution=rabc_attribution,
            manager_alignment=structured_data.manager_alignment,
            investor_experience=investor_experience,
            consistency_result=consistency_result,
            risk_check_result=risk_check_result,
            valuation_state=valuation_state_resolution.state,
            valuation_resolution=valuation_state_resolution,
            money_horizon=resolved_contract.money_horizon,
            user_money_horizon_years=request.user_money_horizon_years,
        )
        final_judgment_decision = derive_final_judgment(
            checklist_result=checklist_result,
            risk_check_result=risk_check_result,
            stress_test_result=stress_test_result,
            quality_gate_status=quality_gate_status,
            quality_gate_not_run_reason=quality_gate_not_run_reason,
            override_judgment=resolved_contract.final_judgment_override,
        )
        return _AnalysisCoreResult(
            structured_data=structured_data,
            rabc_attribution=rabc_attribution,
            alpha_judgment=alpha_judgment,
            consistency_result=consistency_result,
            investor_experience=investor_experience,
            risk_check_result=risk_check_result,
            stress_test_result=stress_test_result,
            checklist_result=checklist_result,
            valuation_state_resolution=valuation_state_resolution,
            final_judgment_decision=final_judgment_decision,
            current_stage=resolved_contract.current_stage,
            quality_gate_result=quality_gate_result,
            quality_gate_not_run_reason=quality_gate_not_run_reason,
        )


def build_fund_llm_execution_request(
    request: FundAnalysisRequest,
    *,
    opt_in_mode: Literal["explicit_cli_flag"] = "explicit_cli_flag",
) -> FundLLMExecutionRequest:
    """构造 Service-owned LLM 执行请求，见模板第 0-7 章。

    Args:
        request: 显式基金分析请求；会被归一化为 LLM report `analyze` 输入。
        opt_in_mode: LLM 显式启用模式，本 gate 仅允许 `explicit_cli_flag`。

    Returns:
        包含业务契约、Service runtime plan 和 provider clients 的 typed request。

    Raises:
        LLMProviderConfigError: 当环境中的 provider 配置缺失或非法时抛出。
        LLMProviderConstructionError: 当 provider clients 构造失败时抛出。
        ValueError: 当业务请求或契约字段非法时抛出。
    """

    resolved_contract = _resolve_analyze_contract(request)
    analysis_input = normalize_fund_llm_analysis_input(request)
    quality_policy = QualityPolicyDeclaration(
        quality_gate_policy=resolved_contract.quality_gate_policy,
        deterministic_fallback_allowed=False,
    )
    contract = FundLLMExecutionContract(
        fund_code=analysis_input.fund_code,
        report_year=analysis_input.report_year,
        analysis_input=analysis_input,
        quality_policy=quality_policy,
        llm_opt_in_mode=opt_in_mode,
    )

    config = load_llm_provider_config_from_env()
    chapter_policy = ChapterOrchestrationPolicy(
        max_output_chars=config.max_output_chars,
        prompt_payload_mode="compact",
        typed_template_path="typed_template_contract",
    )
    provider_runtime_budget = ProviderRuntimeBudget(
        writer_timeout_seconds=config.writer_timeout_seconds,
        auditor_timeout_seconds=config.auditor_timeout_seconds,
        repair_timeout_seconds=config.repair_timeout_seconds,
        timeout_max_attempts=config.timeout_max_attempts,
        timeout_backoff_seconds=config.timeout_backoff_seconds,
        max_output_chars=config.max_output_chars,
        prompt_payload_mode="compact",
    )
    quality_fail_closed_policy = QualityFailClosedPolicy(
        quality_gate_policy=resolved_contract.quality_gate_policy,
        fail_on_quality_gate_block=True,
        fail_on_quality_gate_not_run=True,
        fail_on_partial_orchestration=True,
        fail_on_incomplete_final_assembly=True,
        deterministic_fallback_allowed=False,
    )
    runtime_plan = FundLLMRuntimePlan(
        chapter_policy=chapter_policy,
        assembly_policy=FinalAssemblyPolicy(),
        provider_runtime_budget=provider_runtime_budget,
        quality_fail_closed_policy=quality_fail_closed_policy,
        safe_diagnostic_policy=SafeDiagnosticPolicy(),
        typed_template_path="typed_template_contract",
        host_timeout_seconds=derive_host_timeout_seconds(
            provider_runtime_budget,
            chapter_count=LLM_REPORT_HOST_TIMEOUT_CHAPTER_COUNT,
        ),
    )
    llm_clients = build_chapter_llm_clients(config)
    return FundLLMExecutionRequest(
        contract=contract,
        runtime_plan=runtime_plan,
        llm_clients=llm_clients,
        typed_template_path="typed_template_contract",
    )


def _fund_analysis_request_from_llm_input(
    analysis_input: FundLLMAnalysisInput,
) -> FundAnalysisRequest:
    """把规范化 LLM 业务输入还原为现有 `analyze_with_llm()` 请求。

    Args:
        analysis_input: `FundLLMAnalysisInput` 实例。

    Returns:
        可传给既有 LLM 分析路径的 `FundAnalysisRequest`。

    Raises:
        AttributeError: 当传入对象不是规范化 LLM 输入时由属性访问自然抛出。
    """

    return FundAnalysisRequest(
        fund_code=analysis_input.fund_code,
        report_year=analysis_input.report_year,
        investment_amount=analysis_input.investment_amount,
        max_tolerable_loss_rate=analysis_input.max_tolerable_loss_rate,
        valuation_state=analysis_input.valuation_state,
        thermometer_cache_dir=analysis_input.thermometer_cache_dir,
        user_money_horizon_years=analysis_input.user_money_horizon_years,
        force_refresh=analysis_input.force_refresh,
        mode=analysis_input.mode,
        developer_overrides=analysis_input.developer_overrides,
        command_source="analyze",
    )


def _project_hosted_llm_run_result(host_result: object) -> FundLLMHostedRunResult:
    """把 HostRunResult 投影成 Service-owned 安全返回形状。

    Args:
        host_result: Host runner 返回的通用 run result。

    Returns:
        只包含 UI 安全消费字段的 hosted LLM run result。

    Raises:
        AttributeError: 当传入对象不具备 HostRunResult 必要字段时自然抛出。
    """

    operation_result = getattr(host_result, "operation_result")
    status = getattr(host_result, "status")
    timeout_classification = getattr(host_result, "timeout_classification")
    completed_at = getattr(host_result, "completed_at")
    analysis_result = (
        operation_result if isinstance(operation_result, FundLLMAnalysisResult) else None
    )
    return FundLLMHostedRunResult(
        analysis_result=analysis_result,
        host_status=_enum_value_or_str(status),
        host_run_id=str(getattr(host_result, "run_id")),
        host_elapsed_ms=getattr(host_result, "elapsed_ms"),
        host_timeout_classification=(
            None
            if timeout_classification is None
            else _enum_value_or_str(timeout_classification)
        ),
        host_safe_diagnostics=dict(getattr(host_result, "safe_diagnostics")),
        host_event_count=len(getattr(host_result, "events")),
        host_completed_at_iso=(
            None if completed_at is None else completed_at.isoformat()
        ),
        host_operation_result_present=operation_result is not None,
    )


def _enum_value_or_str(value: object) -> str:
    """返回 enum-like 对象的 value，否则返回字符串形式。

    Args:
        value: enum-like 对象或普通标量。

    Returns:
        可安全展示的字符串。

    Raises:
        无显式抛出。
    """

    enum_value = getattr(value, "value", None)
    if enum_value is not None:
        return str(enum_value)
    return str(value)


def _validate_llm_execution_fail_closed_policy(
    policy: QualityFailClosedPolicy,
) -> None:
    """验证 typed LLM 执行路径仍保持 fail-closed，见模板第 0-7 章。

    Args:
        policy: Service runtime plan 中的 fail-closed 策略。

    Returns:
        无返回值。

    Raises:
        ValueError: 当策略字段会放松当前 LLM fail-closed 语义时抛出。
    """

    weakening_fields = {
        "fail_on_quality_gate_block": policy.fail_on_quality_gate_block is not True,
        "fail_on_quality_gate_not_run": policy.fail_on_quality_gate_not_run is not True,
        "fail_on_partial_orchestration": policy.fail_on_partial_orchestration is not True,
        "fail_on_incomplete_final_assembly": (
            policy.fail_on_incomplete_final_assembly is not True
        ),
        "deterministic_fallback_allowed": policy.deterministic_fallback_allowed is not False,
    }
    invalid_fields = tuple(
        field_name
        for field_name, weakens_fail_closed in weakening_fields.items()
        if weakens_fail_closed
    )
    if invalid_fields:
        joined_fields = ", ".join(invalid_fields)
        raise ValueError(f"LLM execution fail-closed policy 不允许放松字段：{joined_fields}")


def _resolve_analyze_contract(request: FundAnalysisRequest) -> ResolvedAnalyzeContract:
    """解析 analyze 产品契约和开发覆盖契约。

    Args:
        request: 基金分析请求。

    Returns:
        Service 内部使用的解析后契约。

    Raises:
        ValueError: 当模式非法或 product mode 携带开发覆盖时抛出。
    """

    if request.mode not in {"product", "developer_override"}:
        raise ValueError("mode 必须是 product / developer_override")
    if request.mode == "product":
        if request.developer_overrides is not None:
            raise ValueError("product mode 不允许 developer_overrides")
        return ResolvedAnalyzeContract(
            mode="product",
            equity_position=None,
            actual_style=None,
            actual_equity_position=None,
            manager_tenure_months=None,
            peer_fee_median=None,
            tracking_error=None,
            money_horizon=None,
            current_stage=None,
            final_judgment_override=None,
            quality_gate_policy="block",
            quality_gate_source_csv=DEFAULT_SELECTED_FUNDS_CSV,
            quality_gate_output_dir=None,
            quality_gate_run_id=None,
            quality_gate_golden_answer_path=DEFAULT_GOLDEN_ANSWER_PATH,
        )
    overrides = request.developer_overrides or FundAnalysisDeveloperOverrides()
    return ResolvedAnalyzeContract(
        mode="developer_override",
        equity_position=overrides.equity_position,
        actual_style=overrides.actual_style,
        actual_equity_position=overrides.actual_equity_position,
        manager_tenure_months=overrides.manager_tenure_months,
        peer_fee_median=overrides.peer_fee_median,
        tracking_error=overrides.tracking_error,
        money_horizon=overrides.money_horizon,
        current_stage=overrides.current_stage,
        final_judgment_override=overrides.final_judgment_override,
        quality_gate_policy=overrides.quality_gate_policy or "block",
        quality_gate_source_csv=(
            DEFAULT_SELECTED_FUNDS_CSV
            if overrides.quality_gate_source_csv is None
            else overrides.quality_gate_source_csv
        ),
        quality_gate_output_dir=overrides.quality_gate_output_dir,
        quality_gate_run_id=overrides.quality_gate_run_id,
        quality_gate_golden_answer_path=(
            DEFAULT_GOLDEN_ANSWER_PATH
            if overrides.quality_gate_golden_answer_path is None
            else overrides.quality_gate_golden_answer_path
        ),
    )


def _validate_request(
    request: FundAnalysisRequest,
    resolved_contract: ResolvedAnalyzeContract,
) -> _ValidatedRequest:
    """校验 Service 请求的基础字段。

    Args:
        request: 基金分析请求。
        resolved_contract: 解析后的 analyze 契约。

    Returns:
        规范化后的请求事实。

    Raises:
        ValueError: 当基金代码或年报年份非法时抛出。
    """

    normalized_fund_code = _normalize_fund_code(request.fund_code)
    if request.report_year <= 0:
        raise ValueError("report_year 必须为正整数")
    if request.command_source not in {"analyze", "checklist"}:
        raise ValueError("command_source 必须是 analyze / checklist")
    if resolved_contract.quality_gate_policy not in {"off", "warn", "block"}:
        raise ValueError("quality_gate_policy 必须是 off / warn / block")
    if (
        resolved_contract.quality_gate_run_id is not None
        and not resolved_contract.quality_gate_run_id.strip()
    ):
        raise ValueError("quality_gate_run_id 不能为空")
    if (
        resolved_contract.quality_gate_output_dir is not None
        and resolved_contract.quality_gate_output_dir.exists()
        and not resolved_contract.quality_gate_output_dir.is_dir()
    ):
        raise ValueError("quality_gate_output_dir 必须是目录")
    return _ValidatedRequest(fund_code=normalized_fund_code)


def _normalize_fund_code(fund_code: str) -> str:
    """规范化基金代码。

    Args:
        fund_code: 原始基金代码。

    Returns:
        6 位数字基金代码。

    Raises:
        ValueError: 基金代码为空或格式非法时抛出。
    """

    normalized_fund_code = fund_code.strip()
    if not normalized_fund_code:
        raise ValueError("fund_code 不能为空")
    if len(normalized_fund_code) != 6 or not normalized_fund_code.isdigit():
        raise ValueError("fund_code 必须是 6 位数字")
    return normalized_fund_code


def _prior_years_from_range(
    *,
    target_year: int,
    start_year: int,
    max_years: int,
) -> tuple[int, ...]:
    """从用户范围参数派生 optional prior years。

    Args:
        target_year: 当前必需年报年份。
        start_year: 最早 optional prior 年份。
        max_years: 年报证据硬上限。

    Returns:
        降序排列的 optional prior 年份。

    Raises:
        ValueError: 年份范围或上限非法时抛出。
    """

    if target_year <= 0:
        raise ValueError("target_year 必须为正整数")
    if start_year <= 0:
        raise ValueError("start_year 必须为正整数")
    if max_years < 1 or max_years > MAX_ANNUAL_EVIDENCE_YEARS:
        raise ValueError("max_years 必须在 1..5 范围内")
    if start_year > target_year:
        raise ValueError("start_year 不能晚于 target_year")
    requested_year_count = target_year - start_year + 1
    if requested_year_count > max_years:
        raise ValueError("target_year 到 start_year 的闭区间不能超过 max_years")
    if requested_year_count < 1:
        raise ValueError("年报年份范围不能为空")
    return tuple(range(target_year - 1, start_year - 1, -1))


def _multi_year_developer_overrides(
    request: MultiYearAnnualAnalysisRequest,
) -> FundAnalysisDeveloperOverrides | None:
    """按现有单年 analyze 契约构造必要的开发覆盖参数。

    Args:
        request: 多年年报分析请求。

    Returns:
        需要 developer override mode 时返回覆盖参数；默认 product 契约返回 `None`。

    Raises:
        无显式抛出。
    """

    if (
        request.quality_gate_policy == "block"
        and request.quality_gate_source_csv is None
        and request.quality_gate_output_dir is None
        and request.quality_gate_run_id is None
        and request.quality_gate_golden_answer_path is None
    ):
        return None
    return FundAnalysisDeveloperOverrides(
        quality_gate_policy=request.quality_gate_policy,
        quality_gate_source_csv=request.quality_gate_source_csv,
        quality_gate_output_dir=request.quality_gate_output_dir,
        quality_gate_run_id=request.quality_gate_run_id,
        quality_gate_golden_answer_path=request.quality_gate_golden_answer_path,
    )


def _check_pool_membership_before_extraction(
    *,
    validated_request: _ValidatedRequest,
    resolved_contract: ResolvedAnalyzeContract,
) -> None:
    """在抽取前轻量检查基金是否在精选池中。

    仅当 quality gate policy 为 block 时生效。不在池中时提前阻断，
    避免浪费昂贵的年报抽取 I/O。

    Args:
        validated_request: 已规范化的请求事实。
        resolved_contract: 解析后的 analyze 契约。

    Returns:
        无返回值。

    Raises:
        QualityGateNotRunBlockedError: 基金不在精选池中时抛出。
    """

    if resolved_contract.quality_gate_policy != "block":
        return
    if resolved_contract.quality_gate_source_csv is None:
        return
    not_run_reason = check_quality_gate_fund_membership(
        source_csv=resolved_contract.quality_gate_source_csv,
        fund_code=validated_request.fund_code,
    )
    if not_run_reason is not None:
        raise QualityGateNotRunBlockedError(not_run_reason)


def _run_quality_gate_if_enabled(
    *,
    structured_data: StructuredFundDataBundle,
    resolved_contract: ResolvedAnalyzeContract,
    command_source: AnalyzeCommandSource,
) -> tuple[QualityGateResult | None, str | None]:
    """按请求策略运行输入质量 gate。

    Args:
        structured_data: 已抽取的结构化基金数据包，避免重复读取年报。
        resolved_contract: 解析后的 analyze 契约。
        command_source: 触发 quality gate 的命令来源。

    Returns:
        `(quality_gate_result, not_run_reason)`。

    Raises:
        Exception: 允许 Agent 层 quality gate 传播 JSON 或写文件异常。
    """

    if resolved_contract.quality_gate_policy == "off":
        return None, "policy=off"
    if resolved_contract.quality_gate_source_csv is None:
        return None, "quality_gate_source_csv not provided"
    golden_answer_path = _resolve_golden_answer_path(resolved_contract.quality_gate_golden_answer_path)
    integration_result = run_quality_gate_for_bundle(
        bundle=structured_data,
        source_csv=resolved_contract.quality_gate_source_csv,
        output_dir=resolved_contract.quality_gate_output_dir,
        run_id=resolved_contract.quality_gate_run_id
        or _default_quality_gate_run_id(
            structured_data,
            command_source=command_source,
        ),
        golden_answer_path=golden_answer_path,
    )
    return integration_result.quality_gate_result, integration_result.not_run_reason


def _resolve_final_judgment_quality_gate_status(
    *,
    quality_gate_result: QualityGateResult | None,
    quality_gate_not_run_reason: str | None,
) -> FinalJudgmentQualityGateStatus:
    """把 Service quality gate 执行结果归一化为最终判断输入。

    Args:
        quality_gate_result: quality gate 运行结果。
        quality_gate_not_run_reason: quality gate 未运行原因。

    Returns:
        `derive_final_judgment` 可消费的 gate 状态。

    Raises:
        ValueError: 当 gate 状态未知或结果与未运行原因同时存在时抛出。
    """

    if quality_gate_result is not None and quality_gate_not_run_reason is not None:
        raise ValueError("quality_gate_result 与 quality_gate_not_run_reason 不能同时存在")
    if quality_gate_result is None:
        return "not_run"
    if quality_gate_result.status in {"pass", "warn", "block"}:
        return quality_gate_result.status  # type: ignore[return-value]
    raise ValueError("quality_gate_result.status 必须是 pass / warn / block")


def _resolve_golden_answer_path(path: Path | None) -> Path | None:
    """解析 strict golden answer 路径。

    Args:
        path: 请求中的 golden answer 路径。

    Returns:
        文件存在时返回路径，否则返回 `None`，让 correctness 显式 unavailable。

    Raises:
        无显式抛出。
    """

    if path is None:
        return None
    if path.exists():
        return path
    if path != DEFAULT_GOLDEN_ANSWER_PATH:
        raise FileNotFoundError(f"quality_gate_golden_answer_path 不存在：{path}")
    return None


def _default_quality_gate_run_id(
    structured_data: StructuredFundDataBundle,
    *,
    command_source: AnalyzeCommandSource,
) -> str:
    """生成默认 quality gate 运行 ID。

    Args:
        structured_data: 已抽取的结构化基金数据包。
        command_source: 触发 quality gate 的命令来源。

    Returns:
        包含基金代码、年报年份和 UTC 时间戳的运行 ID。

    Raises:
        无显式抛出。
    """

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    return f"{command_source}-{structured_data.fund_code}-{structured_data.report_year}-{timestamp}"


def _raise_if_host_cancelled(host_context: HostRunContext | None) -> None:
    """在 Service phase 边界传播 Host deadline/cancel。

    Args:
        host_context: 可选 Host run 上下文。

    Returns:
        无返回值。

    Raises:
        HostRuntimeError: 当 Host run 已取消或超过 deadline 时抛出。
    """

    if host_context is None:
        return
    host_context.raise_if_cancelled_or_deadline_exceeded()


def _record_host_phase_started(
    host_context: HostRunContext | None,
    *,
    phase: str,
) -> None:
    """记录 Service 级 phase_started 安全事件。"""

    if host_context is None:
        return
    host_context.record_phase_started(phase=phase)


def _record_host_phase_completed(
    host_context: HostRunContext | None,
    *,
    phase: str,
    phase_started: float,
) -> None:
    """记录 Service 级 phase_completed 安全事件。"""

    if host_context is None:
        return
    host_context.record_phase_completed(
        phase=phase,
        elapsed_ms=max(0, int((time.monotonic() - phase_started) * 1000)),
    )


def _extract_fund_type(structured_data: StructuredFundDataBundle) -> FundType:
    """从 P1 结构化数据读取已识别基金类型。

    Args:
        structured_data: P1 结构化基金数据包。

    Returns:
        标准化基金类型。

    Raises:
        ValueError: 当 P1 未提供有效 `classified_fund_type` 时抛出。
    """

    identity = structured_data.basic_identity.value or {}
    fund_type = identity.get("classified_fund_type")
    if fund_type in {
        "index_fund",
        "active_fund",
        "bond_fund",
        "enhanced_index",
        "qdii_fund",
        "fof_fund",
    }:
        return fund_type  # type: ignore[return-value]
    raise ValueError("P1 结构化数据缺少有效 classified_fund_type，不能选择 preferred_lens")
