"""Service 层 LLM 执行契约类型，见基金分析模板第 0-7 章。

本模块只定义 Service-owned 的业务契约、运行计划和显式请求类型。
业务事实放入 `FundLLMExecutionContract`，provider runtime、章节策略、最终总装
策略和 LLM clients 只存在于 Service 内部 request/runtime plan 中，避免 Host
或底层 provider 语义泄漏进稳定业务契约。
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path
from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from fund_agent.services.chapter_orchestrator import (
        ChapterOrchestrationPolicy,
        ChapterOrchestratorLLMClients,
    )
    from fund_agent.services.final_chapter_assembler import FinalAssemblyPolicy
    from fund_agent.services.fund_analysis_service import (
        FundAnalysisDeveloperOverrides,
        FundAnalysisRequest,
    )

FundLLMExecutionContractSchemaVersion = Literal["fund_llm_execution_contract.v1"]
FundLLMReportMode = Literal["llm_report"]
FundLLMOptInMode = Literal["explicit_cli_flag"]
FundLLMAnalysisCommandSource = Literal["analyze"]
QualityGatePolicy = Literal["off", "warn", "block"]
AnalyzeMode = Literal["product", "developer_override"]
ValuationState = Literal["low", "fair", "high", "unavailable"]
PromptPayloadMode = Literal["compact", "full"]
SafeDiagnosticPolicySchemaVersion = Literal["safe_diagnostic_policy.v1"]

FUND_LLM_EXECUTION_CONTRACT_SCHEMA_VERSION: FundLLMExecutionContractSchemaVersion = (
    "fund_llm_execution_contract.v1"
)
SAFE_DIAGNOSTIC_POLICY_SCHEMA_VERSION: SafeDiagnosticPolicySchemaVersion = (
    "safe_diagnostic_policy.v1"
)
_ALLOWED_QUALITY_GATE_POLICIES = frozenset(("off", "warn", "block"))
_ALLOWED_PROMPT_PAYLOAD_MODES = frozenset(("compact", "full"))
_ALLOWED_RUNTIME_CHAPTER_IDS = frozenset((1, 2, 3, 4, 5, 6))


@dataclass(frozen=True, slots=True, kw_only=True)
class FundLLMAnalysisInput:
    """LLM 报告用例的规范化业务输入，见模板第 0-7 章。

    Attributes:
        fund_code: 已规范化的 6 位基金代码。
        report_year: 年报年份。
        command_source: LLM 报告固定归一为 analyze。
        investment_amount: 压力测试投入金额，见模板第 6 章。
        max_tolerable_loss_rate: 最大可承受亏损比例，见模板第 6 章。
        valuation_state: 估值状态，见 7 问题检查清单。
        thermometer_cache_dir: 自动温度计缓存目录。
        user_money_horizon_years: 用户资金不用年限，见 7 问题检查清单。
        force_refresh: 是否强制刷新底层数据。
        mode: analyze 契约模式。
        developer_overrides: developer override 显式业务参数。
    """

    fund_code: str
    report_year: int
    command_source: FundLLMAnalysisCommandSource = "analyze"
    investment_amount: Decimal | str | int | float = Decimal("10000")
    max_tolerable_loss_rate: Decimal | str | int | float | None = None
    valuation_state: ValuationState | None = None
    thermometer_cache_dir: Path | None = None
    user_money_horizon_years: Decimal | str | int | float | None = None
    force_refresh: bool = False
    mode: AnalyzeMode = "product"
    developer_overrides: FundAnalysisDeveloperOverrides | None = None

    def __post_init__(self) -> None:
        """校验规范化业务输入。

        Args:
            无。

        Returns:
            无返回值。

        Raises:
            ValueError: 当基金身份、年份、命令来源或模式非法时抛出。
        """

        _validate_fund_identity(self.fund_code, self.report_year)
        if self.command_source != "analyze":
            raise ValueError("LLM analysis_input.command_source 必须归一为 analyze")
        if self.mode not in {"product", "developer_override"}:
            raise ValueError("mode 必须是 product / developer_override")


@dataclass(frozen=True, slots=True, kw_only=True)
class QualityPolicyDeclaration:
    """LLM 执行业务质量策略声明。

    Attributes:
        quality_gate_policy: 已解析的 quality gate 策略。
        deterministic_fallback_allowed: 是否允许回退到确定性报告；本 gate 固定禁止。
    """

    quality_gate_policy: QualityGatePolicy = "block"
    deterministic_fallback_allowed: bool = False

    def __post_init__(self) -> None:
        """校验业务质量策略声明。

        Args:
            无。

        Returns:
            无返回值。

        Raises:
            ValueError: 当 quality gate 策略非法或允许确定性 fallback 时抛出。
        """

        _validate_quality_gate_policy(self.quality_gate_policy)
        if self.deterministic_fallback_allowed:
            raise ValueError("LLM ExecutionContract 禁止 deterministic fallback")


@dataclass(frozen=True, slots=True, kw_only=True)
class ProviderRuntimeBudget:
    """Service 内部 provider runtime 预算，见模板第 1-6 章写作/审计路径。

    Attributes:
        writer_timeout_seconds: writer 初次请求 timeout 秒数。
        auditor_timeout_seconds: auditor 请求 timeout 秒数。
        repair_timeout_seconds: writer repair 请求 timeout 秒数。
        timeout_max_attempts: 单次 provider 请求 timeout 后最大总尝试次数。
        timeout_backoff_seconds: timeout retry 前等待秒数。
        max_output_chars: 单章 writer 输出字符上限。
        prompt_payload_mode: writer prompt payload 模式。
    """

    writer_timeout_seconds: float
    auditor_timeout_seconds: float
    repair_timeout_seconds: float
    timeout_max_attempts: int
    timeout_backoff_seconds: float
    max_output_chars: int
    prompt_payload_mode: PromptPayloadMode

    def __post_init__(self) -> None:
        """校验 provider runtime 预算。

        Args:
            无。

        Returns:
            无返回值。

        Raises:
            ValueError: 当 timeout、attempt、输出上限或 prompt payload 模式非法时抛出。
        """

        _validate_positive_number(
            self.writer_timeout_seconds,
            field_name="writer_timeout_seconds",
        )
        _validate_positive_number(
            self.auditor_timeout_seconds,
            field_name="auditor_timeout_seconds",
        )
        _validate_positive_number(
            self.repair_timeout_seconds,
            field_name="repair_timeout_seconds",
        )
        if self.timeout_max_attempts < 1:
            raise ValueError("timeout_max_attempts 必须大于等于 1")
        if self.timeout_backoff_seconds < 0:
            raise ValueError("timeout_backoff_seconds 必须大于等于 0")
        if self.max_output_chars <= 0:
            raise ValueError("max_output_chars 必须为正整数")
        if self.prompt_payload_mode not in _ALLOWED_PROMPT_PAYLOAD_MODES:
            raise ValueError("prompt_payload_mode 必须为 compact 或 full")


@dataclass(frozen=True, slots=True, kw_only=True)
class QualityFailClosedPolicy:
    """Service 内部 fail-closed 策略。

    Attributes:
        quality_gate_policy: 已解析的 quality gate 策略。
        fail_on_quality_gate_block: quality gate block 时是否失败关闭。
        fail_on_quality_gate_not_run: quality gate 未运行时是否失败关闭。
        fail_on_partial_orchestration: 章节编排 partial 时是否失败关闭。
        fail_on_incomplete_final_assembly: 最终总装 incomplete 时是否失败关闭。
        deterministic_fallback_allowed: 是否允许确定性 fallback；本 gate 固定禁止。
    """

    quality_gate_policy: QualityGatePolicy = "block"
    fail_on_quality_gate_block: bool = True
    fail_on_quality_gate_not_run: bool = True
    fail_on_partial_orchestration: bool = True
    fail_on_incomplete_final_assembly: bool = True
    deterministic_fallback_allowed: bool = False

    def __post_init__(self) -> None:
        """校验 fail-closed 策略。

        Args:
            无。

        Returns:
            无返回值。

        Raises:
            ValueError: 当 quality gate 策略非法或允许确定性 fallback 时抛出。
        """

        _validate_quality_gate_policy(self.quality_gate_policy)
        if self.deterministic_fallback_allowed:
            raise ValueError("LLM runtime plan 禁止 deterministic fallback")


@dataclass(frozen=True, slots=True, kw_only=True)
class SafeDiagnosticPolicy:
    """Service 内部安全诊断策略。

    Attributes:
        schema_version: 安全诊断策略 schema 版本。
        host_summary_enabled: 是否允许 Host 摘要级诊断。
        chapter_matrix_enabled: 是否允许章节矩阵诊断。
        runtime_scalar_diagnostics_enabled: 是否允许 runtime 标量诊断。
        forbid_prompt: 是否禁止输出 prompt。
        forbid_draft: 是否禁止输出章节草稿。
        forbid_raw_provider_response: 是否禁止输出 provider 原始响应。
        forbid_raw_audit_response: 是否禁止输出审计原始响应。
        forbid_secrets: 是否禁止输出密钥或认证信息。
    """

    schema_version: SafeDiagnosticPolicySchemaVersion = SAFE_DIAGNOSTIC_POLICY_SCHEMA_VERSION
    host_summary_enabled: bool = True
    chapter_matrix_enabled: bool = True
    runtime_scalar_diagnostics_enabled: bool = True
    forbid_prompt: bool = True
    forbid_draft: bool = True
    forbid_raw_provider_response: bool = True
    forbid_raw_audit_response: bool = True
    forbid_secrets: bool = True

    def __post_init__(self) -> None:
        """校验安全诊断策略。

        Args:
            无。

        Returns:
            无返回值。

        Raises:
            ValueError: 当 schema 版本非法时抛出。
        """

        if self.schema_version != SAFE_DIAGNOSTIC_POLICY_SCHEMA_VERSION:
            raise ValueError("SafeDiagnosticPolicy schema_version 非法")


@dataclass(frozen=True, slots=True, kw_only=True)
class FundLLMRuntimePlan:
    """Service 内部 LLM runtime plan，见模板第 1-7 章。

    Attributes:
        chapter_policy: 第 1-6 章章节编排策略。
        assembly_policy: 第 0/7 章最终总装策略。
        provider_runtime_budget: provider runtime 预算。
        quality_fail_closed_policy: fail-closed 策略。
        safe_diagnostic_policy: 安全诊断策略。
        host_timeout_seconds: Host 可读取的唯一 runtime deadline 标量。
    """

    chapter_policy: ChapterOrchestrationPolicy
    assembly_policy: FinalAssemblyPolicy
    provider_runtime_budget: ProviderRuntimeBudget
    quality_fail_closed_policy: QualityFailClosedPolicy
    safe_diagnostic_policy: SafeDiagnosticPolicy
    host_timeout_seconds: int

    def __post_init__(self) -> None:
        """校验 Service 内部 runtime plan。

        Args:
            无。

        Returns:
            无返回值。

        Raises:
            ValueError: 当 Host timeout 或目标章节范围非法时抛出。
        """

        if self.host_timeout_seconds <= 0:
            raise ValueError("host_timeout_seconds 必须为正整数")
        _validate_runtime_chapter_ids(self.chapter_policy)


@dataclass(frozen=True, slots=True, kw_only=True)
class FundLLMExecutionContract:
    """Service-owned LLM 执行业务契约。

    Attributes:
        schema_version: 契约 schema 版本。
        fund_code: 基金代码。
        report_year: 年报年份。
        report_mode: 报告模式，本 gate 固定为 llm_report。
        llm_opt_in_mode: LLM 显式启用模式，本 gate 固定为 explicit_cli_flag。
        analysis_input: 规范化业务输入。
        quality_policy: 业务质量策略声明。
    """

    fund_code: str
    report_year: int
    analysis_input: FundLLMAnalysisInput
    quality_policy: QualityPolicyDeclaration
    schema_version: FundLLMExecutionContractSchemaVersion = (
        FUND_LLM_EXECUTION_CONTRACT_SCHEMA_VERSION
    )
    report_mode: FundLLMReportMode = "llm_report"
    llm_opt_in_mode: FundLLMOptInMode = "explicit_cli_flag"

    def __post_init__(self) -> None:
        """校验 LLM 执行业务契约。

        Args:
            无。

        Returns:
            无返回值。

        Raises:
            ValueError: 当 schema、身份同源、报告模式、opt-in 模式或 fallback 策略非法时抛出。
        """

        if self.schema_version != FUND_LLM_EXECUTION_CONTRACT_SCHEMA_VERSION:
            raise ValueError("FundLLMExecutionContract schema_version 非法")
        _validate_fund_identity(self.fund_code, self.report_year)
        if self.fund_code != self.analysis_input.fund_code:
            raise ValueError("fund_code 必须与 analysis_input.fund_code 一致")
        if self.report_year != self.analysis_input.report_year:
            raise ValueError("report_year 必须与 analysis_input.report_year 一致")
        if self.analysis_input.command_source != "analyze":
            raise ValueError("analysis_input.command_source 必须为 analyze")
        if self.report_mode != "llm_report":
            raise ValueError("report_mode 必须为 llm_report")
        if self.llm_opt_in_mode != "explicit_cli_flag":
            raise ValueError("llm_opt_in_mode 必须为 explicit_cli_flag")
        if self.quality_policy.deterministic_fallback_allowed:
            raise ValueError("LLM ExecutionContract 禁止 deterministic fallback")


@dataclass(frozen=True, slots=True, kw_only=True)
class FundLLMExecutionRequest:
    """Service 内部 LLM 执行请求。

    Attributes:
        contract: 稳定业务契约，只包含业务事实和质量声明。
        runtime_plan: Service 内部 runtime plan，包含章节、总装、预算和安全诊断策略。
        llm_clients: Service 构造或显式注入的章节 LLM clients。
    """

    contract: FundLLMExecutionContract
    runtime_plan: FundLLMRuntimePlan
    llm_clients: ChapterOrchestratorLLMClients


def normalize_fund_llm_analysis_input(
    request: FundAnalysisRequest,
) -> FundLLMAnalysisInput:
    """把 `FundAnalysisRequest` 归一化为 LLM 报告业务输入。

    Args:
        request: Service analyze 请求。

    Returns:
        归一化后的 LLM 报告业务输入；`command_source` 固定为 analyze。

    Raises:
        ValueError: 当基金代码、年份、模式或 developer overrides 契约非法时抛出。
    """

    fund_code = request.fund_code.strip()
    if request.mode == "product" and request.developer_overrides is not None:
        raise ValueError("product mode 不允许 developer_overrides")
    return FundLLMAnalysisInput(
        fund_code=fund_code,
        report_year=request.report_year,
        command_source="analyze",
        investment_amount=request.investment_amount,
        max_tolerable_loss_rate=request.max_tolerable_loss_rate,
        valuation_state=request.valuation_state,
        thermometer_cache_dir=request.thermometer_cache_dir,
        user_money_horizon_years=request.user_money_horizon_years,
        force_refresh=request.force_refresh,
        mode=request.mode,
        developer_overrides=request.developer_overrides,
    )


def derive_host_timeout_seconds(
    budget: ProviderRuntimeBudget,
    *,
    chapter_count: int,
) -> int:
    """按 provider runtime 预算推导 Host 全局 deadline。

    公式来自已接受 plan：`max(1, (writer + auditor + repair) * attempts * chapter_count)`。

    Args:
        budget: provider runtime 预算。
        chapter_count: 本次计划生成的章节数量。

    Returns:
        Host run timeout 秒数，向下取整为整数且至少为 1。

    Raises:
        ValueError: 当章节数量非法时抛出。
    """

    if chapter_count <= 0:
        raise ValueError("chapter_count 必须为正整数")
    phase_budget = (
        budget.writer_timeout_seconds
        + budget.auditor_timeout_seconds
        + budget.repair_timeout_seconds
    )
    timeout_seconds = int(max(1.0, phase_budget * budget.timeout_max_attempts * chapter_count))
    return timeout_seconds


def _validate_fund_identity(fund_code: str, report_year: int) -> None:
    """校验基金身份字段。

    Args:
        fund_code: 基金代码。
        report_year: 年报年份。

    Returns:
        无返回值。

    Raises:
        ValueError: 当基金代码或年报年份非法时抛出。
    """

    if not fund_code:
        raise ValueError("fund_code 不能为空")
    if len(fund_code) != 6 or not fund_code.isdigit():
        raise ValueError("fund_code 必须是 6 位数字")
    if report_year <= 0:
        raise ValueError("report_year 必须为正整数")


def _validate_quality_gate_policy(quality_gate_policy: str) -> None:
    """校验 quality gate 策略。

    Args:
        quality_gate_policy: 待校验的策略名称。

    Returns:
        无返回值。

    Raises:
        ValueError: 当策略名称非法时抛出。
    """

    if quality_gate_policy not in _ALLOWED_QUALITY_GATE_POLICIES:
        raise ValueError("quality_gate_policy 必须是 off / warn / block")


def _validate_positive_number(value: float, *, field_name: str) -> None:
    """校验正数 runtime 标量。

    Args:
        value: 待校验数值。
        field_name: 错误信息使用的字段名。

    Returns:
        无返回值。

    Raises:
        ValueError: 当数值小于等于 0 时抛出。
    """

    if value <= 0:
        raise ValueError(f"{field_name} 必须为正数")


def _validate_runtime_chapter_ids(chapter_policy: ChapterOrchestrationPolicy) -> None:
    """校验 runtime plan 中的模板章节范围。

    Args:
        chapter_policy: 章节编排策略。

    Returns:
        无返回值。

    Raises:
        ValueError: 当目标章节为空、重复或不在第 1-6 章范围内时抛出。
    """

    chapter_ids = tuple(chapter_policy.target_chapter_ids)
    if not chapter_ids:
        raise ValueError("target_chapter_ids 不能为空")
    if len(set(chapter_ids)) != len(chapter_ids):
        raise ValueError("target_chapter_ids 不能重复")
    invalid_ids = tuple(
        chapter_id for chapter_id in chapter_ids if chapter_id not in _ALLOWED_RUNTIME_CHAPTER_IDS
    )
    if invalid_ids:
        raise ValueError(f"FundLLMRuntimePlan 只允许模板第 1-6 章：{invalid_ids}")
