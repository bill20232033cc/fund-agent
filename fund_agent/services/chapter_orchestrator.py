"""Service 层章节编排器，见基金分析模板第 1-6 章。

本模块负责 Service 层章节编排入口：解析输入、执行早期 fail-closed 校验，
再委托 Service bridge 调用 Agent body runner。它不读取年报仓库、PDF、cache、
source helper、下载器或 parser，不构造真实 LLM provider；Host cancel/deadline
只透传给 bridge 翻译，不由本模块解释基金业务语义。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Final, Literal, get_args

from fund_agent.fund.chapter_auditor import (
    ChapterAuditIssue,
    ChapterAuditLLMClient,
    ChapterAuditRepairHint,
    ChapterAuditResult,
    ChapterAuditRuleCode,
)
from fund_agent.fund.chapter_facts import (
    ChapterFactMissingReason,
    ChapterFactProjection,
    ChapterFactProvider,
)
from fund_agent.fund.evidence_availability import (
    EvidenceAvailability,
    derive_evidence_availability,
)
from fund_agent.fund.chapter_writer import (
    ChapterRepairContext,
    ChapterDraft,
    ChapterLLMClient,
    ChapterWriteResult,
    ChapterWriteStopReason,
)
from fund_agent.fund.data_extractor import StructuredFundDataBundle
from fund_agent.fund.template.typed_contracts import (
    RequiredOutputItem,
    TypedChapterContract,
    get_typed_chapter_contract,
)
from fund_agent.host import HostRunContext

ChapterOrchestratorSchemaVersion = Literal["chapter_orchestrator.v1"]
ChapterOrchestrationStatus = Literal["accepted", "partial", "blocked"]
ChapterRunStatus = Literal["accepted", "blocked", "failed", "skipped"]
ChapterRunStopReason = Literal[
    "none",
    "chapter_not_in_scope",
    "dependency_missing",
    "fund_type_unknown",
    "missing_required_facts",
    "writer_blocked",
    "auditor_failed",
    "auditor_blocked",
    "repair_budget_exhausted",
    "needs_more_facts",
    "llm_unavailable",
    "llm_empty_response",
    "llm_contract_violation",
    "missing_required_structure",
    "missing_required_output_marker",
    "unknown_anchor",
    "response_too_long",
    "response_incomplete",
    "llm_timeout",
    "llm_rate_limited",
    "llm_malformed_response",
    "llm_network_error",
    "llm_exception",
]
ChapterRepairAction = Literal["none", "regenerate", "needs_more_facts", "stop"]
ChapterOrchestrationInputKind = Literal["structured_bundle", "chapter_projection"]
TypedTemplatePathMode = Literal["legacy_contract", "typed_template_contract"]
AcceptedChapterConclusionSource = Literal["heading", "fallback_lines"]
ProviderOperation = Literal["writer", "auditor"]
TimeoutBudgetKind = Literal["writer_initial", "auditor", "writer_repair"]
TimeoutRootCauseHint = Literal[
    "large_writer_prompt_cost",
    "small_prompt_provider_timeout",
    "provider_runtime_timeout_uncalibrated",
    "non_timeout_provider_runtime",
    "not_provider_runtime",
]
ProviderRuntimeCategory = Literal[
    "success",
    "timeout",
    "rate_limit",
    "malformed",
    "network",
    "http_error",
]
DiagnosticConsistencyStatus = Literal[
    "consistent",
    "missing_terminal_runtime_diagnostic",
    "terminal_category_conflict",
    "non_runtime_terminal_without_scalar",
]
ChapterFailureCategory = Literal[
    "provider_runtime",
    "llm_timeout",
    "prompt_contract",
    "audit_parse",
    "audit_rule_too_strict",
    "fact_gap",
    "code_bug",
]
ChapterFailureSubcategory = Literal[
    "missing_structure",
    "missing_required_marker",
    "unknown_anchor",
    "invalid_marker",
    "candidate_facet_assertion",
    "forbidden_phrase",
    "l1_numerical_closure",
    "response_length_incomplete",
    "code_bug_other",
]

CHAPTER_ORCHESTRATOR_SCHEMA_VERSION: ChapterOrchestratorSchemaVersion = (
    "chapter_orchestrator.v1"
)
DEFAULT_TARGET_CHAPTER_IDS: Final[tuple[int, ...]] = (1, 2, 3, 4, 5, 6)
MAX_ACCEPTED_CONCLUSION_CHARS: Final[int] = 500
_TARGET_CHAPTER_ID_SET: Final[frozenset[int]] = frozenset(DEFAULT_TARGET_CHAPTER_IDS)
_ALLOWED_TYPED_TEMPLATE_PATH_MODES: Final[frozenset[str]] = frozenset(
    ("legacy_contract", "typed_template_contract")
)
_CONCLUSION_HEADINGS: Final[tuple[str, ...]] = ("### 结论要点", "## 结论要点")
_WRITER_STOP_REASON_MAPPING: Final[
    dict[ChapterWriteStopReason, tuple[ChapterRunStatus, ChapterRunStopReason]]
] = {
    "none": ("accepted", "none"),
    "fund_type_unknown": ("blocked", "fund_type_unknown"),
    "missing_required_facts": ("blocked", "missing_required_facts"),
    "evidence_anchor_missing": ("blocked", "missing_required_facts"),
    "item_rule_deleted_required_content": ("blocked", "missing_required_facts"),
    "chapter_requires_accepted_conclusions": ("blocked", "dependency_missing"),
    "prompt_only": ("blocked", "writer_blocked"),
    "llm_unavailable": ("blocked", "llm_unavailable"),
    "llm_empty_response": ("blocked", "llm_empty_response"),
    "llm_contract_violation": ("blocked", "llm_contract_violation"),
    "missing_required_structure": ("blocked", "missing_required_structure"),
    "missing_required_output_marker": ("blocked", "missing_required_output_marker"),
    "unknown_anchor": ("blocked", "unknown_anchor"),
    "response_too_long": ("blocked", "response_too_long"),
    "response_incomplete": ("blocked", "response_incomplete"),
}
_MAX_REPAIR_MESSAGE_CHARS: Final[int] = 180
_DIAGNOSTIC_SCHEMA_VERSION: Final[str] = "chapter_prompt_contract_diagnostic.v1"
_RUNTIME_DIAGNOSTIC_PAYLOAD_SCHEMA_VERSION: Final[str] = (
    "chapter_runtime_diagnostic_payload.v1"
)
_INCOMPLETE_FINISH_REASONS: Final[frozenset[str]] = frozenset(
    ("length", "max_tokens", "content_filter")
)
_INVALID_MARKER_PREFIXES: Final[tuple[str, ...]] = (
    "writer:invalid_anchor_marker",
    "writer:invalid_missing_marker",
    "writer:unknown_missing_reason",
    "writer:evidence_line_without_anchor_marker",
)
_FORBIDDEN_PHRASE_PREFIX: Final[str] = "writer:forbidden_phrase"
_PROGRAMMATIC_L1_PREFIX: Final[str] = "programmatic:L1"
_SUBCATEGORY_PRECEDENCE: Final[tuple[ChapterFailureSubcategory, ...]] = (
    "response_length_incomplete",
    "invalid_marker",
    "unknown_anchor",
    "missing_required_marker",
    "missing_structure",
    "candidate_facet_assertion",
    "forbidden_phrase",
    "l1_numerical_closure",
    "code_bug_other",
)
_RUNTIME_TERMINAL_STOP_REASONS: Final[frozenset[ChapterRunStopReason]] = frozenset(
    (
        "llm_timeout",
        "llm_rate_limited",
        "llm_malformed_response",
        "llm_network_error",
        "llm_exception",
    )
)
_RUNTIME_STOP_REASON_CATEGORY: Final[
    dict[ChapterRunStopReason, ProviderRuntimeCategory]
] = {
    "llm_timeout": "timeout",
    "llm_rate_limited": "rate_limit",
    "llm_malformed_response": "malformed",
    "llm_network_error": "network",
}


@dataclass(frozen=True, slots=True, kw_only=True)
class ChapterLLMRuntimeDiagnostic:
    """Service 层 LLM runtime 安全诊断记录。

    Attributes:
        operation: writer 或 auditor。
        chapter_id: 模板章节编号；provider 层记录为 `None`，orchestrator enrich。
        fund_code: 基金代码；provider 层记录为 `None`。
        report_year: 年报年份；provider 层记录为 `None`。
        repair_attempt_index: 章节 repair attempt；provider 层记录为 `None`。
        provider_attempt_index: provider `_complete()` 内从 1 开始的尝试序号。
        provider_max_attempts: 本次 `_complete()` 最大尝试次数。
        provider_runtime_category: provider runtime 分类。
        chapter_failure_category: 章节失败分类。
        elapsed_ms: provider attempt 耗时毫秒。
        status_code: HTTP 状态码。
        request_id: provider request id。
        model_name: provider 返回模型名。
        finish_reason: provider finish reason。
        response_chars: provider content 字符数。
        error_type: 异常类型。
        system_prompt_chars: provider-bound system prompt 字符数。
        user_prompt_chars: provider-bound user prompt 字符数。
        approx_prompt_tokens: 以固定 heuristic 估算的 prompt token 数。
        allowed_fact_count: provider-bound 上下文允许 fact 数。
        allowed_anchor_count: provider-bound 上下文允许 anchor 数。
        max_output_chars: writer 输出字符上限；auditor 不适用时为 `None`。
        timeout_seconds: 本次 provider attempt 使用的 effective timeout。
        timeout_max_attempts: 本次 provider request 允许的最大 timeout attempts。
        timeout_backoff_seconds: timeout retry backoff 秒数。
        timeout_budget_kind: writer_initial / auditor / writer_repair。
        repair_timeout_fallback_used: repair timeout 是否回落到 writer timeout。
        timeout_root_cause_hint: timeout root-cause 粗分类。
        prompt_cost_diagnostic: writer prompt-cost 安全诊断；auditor 为 `None`。
        message: 已脱敏、限长的安全摘要。
        schema_version: 诊断 schema 版本。
    """

    operation: ProviderOperation
    chapter_id: int | None
    fund_code: str | None
    report_year: int | None
    repair_attempt_index: int | None
    provider_attempt_index: int | None
    provider_max_attempts: int | None
    provider_runtime_category: ProviderRuntimeCategory | None
    chapter_failure_category: ChapterFailureCategory | None
    elapsed_ms: int | None
    status_code: int | None
    request_id: str | None
    model_name: str | None
    finish_reason: str | None
    response_chars: int | None
    error_type: str | None
    system_prompt_chars: int | None = None
    user_prompt_chars: int | None = None
    approx_prompt_tokens: int | None = None
    allowed_fact_count: int | None = None
    allowed_anchor_count: int | None = None
    max_output_chars: int | None = None
    timeout_seconds: float | None = None
    timeout_max_attempts: int | None = None
    timeout_backoff_seconds: float | None = None
    timeout_budget_kind: TimeoutBudgetKind | None = None
    repair_timeout_fallback_used: bool | None = None
    timeout_root_cause_hint: TimeoutRootCauseHint | str | None = None
    prompt_cost_diagnostic: object | None = None
    message: str | None = None
    schema_version: str = "chapter_llm_runtime_diagnostic.v1"


@dataclass(frozen=True, slots=True, kw_only=True)
class ChapterPromptContractDiagnostic:
    """Service 层 prompt-contract 脱敏诊断摘要，见模板第 1-6 章。

    该结构只保存枚举、计数和响应长度等标量，不保存 prompt、draft、provider
    response、audit raw response 或具体 anchor/facet/phrase 文本。

    Attributes:
        schema_version: 诊断 schema 版本。
        chapter_id: 模板章节编号。
        phase: 失败阶段。
        attempt_index: 章节 attempt 序号。
        primary_subcategory: 按固定优先级选择的主子类。
        issue_reason_counts: writer issue reason 计数。
        issue_id_prefix_counts: 剥离 raw suffix 后的 issue id prefix 计数。
        required_structure_missing_count: 缺固定结构段落计数。
        required_output_missing_count: 缺 required output marker 计数。
        unknown_anchor_count: 未授权 anchor 计数。
        invalid_marker_count: 非法 marker 计数。
        forbidden_phrase_count: 禁用措辞计数。
        l1_numerical_closure_count: L1 数字闭环缺邻近证据计数。
        candidate_facet_assertion_count: 候选 facet 被断言计数。
        response_length_incomplete_count: 响应超长或不完整计数。
        response_chars: LLM 响应字符数。
        max_output_chars: writer 输出硬上限。
        finish_reason: provider finish reason。
        accepted_draft_present: 本阶段是否已有 accepted draft。
    """

    schema_version: str
    chapter_id: int
    phase: str
    attempt_index: int
    primary_subcategory: ChapterFailureSubcategory
    issue_reason_counts: dict[str, int]
    issue_id_prefix_counts: dict[str, int]
    required_structure_missing_count: int
    required_output_missing_count: int
    unknown_anchor_count: int
    invalid_marker_count: int
    forbidden_phrase_count: int
    l1_numerical_closure_count: int
    candidate_facet_assertion_count: int
    response_length_incomplete_count: int
    response_chars: int | None
    max_output_chars: int | None
    finish_reason: str | None
    accepted_draft_present: bool


@dataclass(frozen=True, slots=True, kw_only=True)
class ChapterOrchestratorLLMClients:
    """章节编排 LLM client 显式注入包，见模板第 1-6 章。

    Attributes:
        writer: Gate 2 writer LLM Protocol client。
        auditor: Gate 2 auditor LLM Protocol client。
    """

    writer: ChapterLLMClient | None
    auditor: ChapterAuditLLMClient | None


@dataclass(frozen=True, slots=True, kw_only=True)
class ChapterOrchestrationPolicy:
    """章节 write-audit-repair 策略，见模板第 1-6 章。

    Attributes:
        target_chapter_ids: 本次允许生成的模板章节编号，只能为第 1-6 章。
        max_repair_attempts: 每章审计失败后的最大 regenerate 次数。
        max_output_chars: 传给 Gate 2 writer 的章节输出硬上限。
        prompt_payload_mode: 传给 Gate 2 writer 的 prompt payload 模式。
        fail_fast: 兼容旧调用方的遗留参数；模板第 1-6 章固定独立执行，不因前章失败跳过后章。
        run_programmatic_audit: 是否执行 Gate 2 programmatic audit。
        run_llm_audit: 是否执行 Gate 2 LLM audit。
        typed_template_path: 显式模板契约路径；默认 legacy，不消费 typed sidecar。
    """

    target_chapter_ids: tuple[int, ...] = DEFAULT_TARGET_CHAPTER_IDS
    max_repair_attempts: int = 1
    max_output_chars: int = 12000
    prompt_payload_mode: str = "full"
    fail_fast: bool = False
    run_programmatic_audit: bool = True
    run_llm_audit: bool = True
    typed_template_path: TypedTemplatePathMode = "legacy_contract"

    def __post_init__(self) -> None:
        """校验章节编排策略。

        Args:
            无。

        Returns:
            无返回值。

        Raises:
            ValueError: 当章节范围、retry budget 或输出上限非法时抛出。
        """

        _validate_policy(self)


@dataclass(frozen=True, slots=True, kw_only=True)
class ChapterOrchestrationInput:
    """章节编排输入，见模板第 1-6 章。

    Attributes:
        fund_code: 基金代码。
        report_year: 年报年份。
        input_kind: 输入来源类型。
        structured_data: 已抽取完成的结构化基金数据包。
        chapter_projection: 已投影的 Gate 1 章节事实。
        policy: write-audit-repair 策略。
        schema_version: orchestration schema 版本。
    """

    fund_code: str
    report_year: int
    input_kind: ChapterOrchestrationInputKind
    structured_data: StructuredFundDataBundle | None = None
    chapter_projection: ChapterFactProjection | None = None
    policy: ChapterOrchestrationPolicy = field(default_factory=ChapterOrchestrationPolicy)
    schema_version: ChapterOrchestratorSchemaVersion = CHAPTER_ORCHESTRATOR_SCHEMA_VERSION

    def __post_init__(self) -> None:
        """校验章节编排输入同源性和互斥 payload。

        Args:
            无。

        Returns:
            无返回值。

        Raises:
            ValueError: 当 input kind、payload 或 fund identity 不一致时抛出。
        """

        _validate_orchestration_input(self)


@dataclass(frozen=True, slots=True, kw_only=True)
class AcceptedChapterConclusion:
    """已接受章节结论摘要，供 Gate 4 final assembler 消费。

    Attributes:
        chapter_id: 模板章节编号。
        title: 章节标题。
        conclusion_markdown: 从 accepted draft 中抽取的“结论要点”段落或安全 fallback。
        conclusion_truncated: 结论是否因长度上限被截断。
        conclusion_source: 结论提取来源。
        used_fact_ids: 被 accepted draft 使用的 fact id。
        used_anchor_ids: 被 accepted draft 使用的 anchor id。
        declared_missing_reasons: accepted draft 显式声明的数据缺口。
        audit_checked_rules: programmatic audit checked rules。
    """

    chapter_id: int
    title: str
    conclusion_markdown: str
    conclusion_truncated: bool
    conclusion_source: AcceptedChapterConclusionSource
    used_fact_ids: tuple[str, ...]
    used_anchor_ids: tuple[str, ...]
    declared_missing_reasons: tuple[ChapterFactMissingReason, ...]
    audit_checked_rules: tuple[ChapterAuditRuleCode, ...]


@dataclass(frozen=True, slots=True, kw_only=True)
class ChapterRepairDecision:
    """单次审计后的 repair 决策，见模板第 1-6 章。

    Attributes:
        action: repair action。
        reason: 中文原因。
        stop_reason: 当 action 表示停止时的 typed Service stop reason。
        source_repair_hint: Gate 2 聚合 repair hint。
        issue_ids: 触发 repair 的 issue id。
    """

    action: ChapterRepairAction
    reason: str
    stop_reason: ChapterRunStopReason
    source_repair_hint: ChapterAuditRepairHint
    issue_ids: tuple[str, ...]


@dataclass(frozen=True, slots=True, kw_only=True)
class ChapterAttemptRecord:
    """单章一次 write/audit attempt 记录，见模板第 1-6 章。

    Attributes:
        attempt_index: 从 0 开始的 attempt 序号。
        writer_result: Gate 2 writer result。
        audit_result: Gate 2 audit result；writer blocked 时为 `None`。
        repair_decision: audit 后 repair 决策；未进入 audit 时为 `None`。
        runtime_diagnostics: Service 层安全 runtime 诊断。
    """

    attempt_index: int
    writer_result: ChapterWriteResult
    audit_result: ChapterAuditResult | None
    repair_decision: ChapterRepairDecision | None
    runtime_diagnostics: tuple[ChapterLLMRuntimeDiagnostic, ...] = ()


@dataclass(frozen=True, slots=True, kw_only=True)
class ChapterRunResult:
    """单章编排结果，见模板第 1-6 章。

    Attributes:
        chapter_id: 模板章节编号。
        title: 章节标题。
        status: 单章状态。
        stop_reason: 停止原因。
        accepted_draft: accepted 章节草稿。
        accepted_conclusion: accepted 章节结论摘要。
        attempts: attempt 记录。
        issues: 聚合 writer/auditor issue 文本。
        failure_category: 单章失败分类；accepted 时为 `None`。
        failure_subcategory: prompt-contract 失败子类；accepted 或非 prompt-contract 时为 `None`。
        prompt_contract_diagnostics: 脱敏 prompt-contract 诊断摘要。
        runtime_diagnostics: 无法挂到具体 attempt 的章节级安全 runtime 诊断。
    """

    chapter_id: int
    title: str
    status: ChapterRunStatus
    stop_reason: ChapterRunStopReason
    accepted_draft: ChapterDraft | None
    accepted_conclusion: AcceptedChapterConclusion | None
    attempts: tuple[ChapterAttemptRecord, ...]
    issues: tuple[str, ...]
    failure_category: ChapterFailureCategory | None = None
    failure_subcategory: ChapterFailureSubcategory | None = None
    prompt_contract_diagnostics: tuple[ChapterPromptContractDiagnostic, ...] = ()
    runtime_diagnostics: tuple[ChapterLLMRuntimeDiagnostic, ...] = ()


@dataclass(frozen=True, slots=True, kw_only=True)
class ChapterOrchestrationResult:
    """章节编排总结果，见模板第 1-6 章。

    Attributes:
        status: 总状态。
        fund_code: 基金代码。
        report_year: 年报年份。
        projection: Gate 1 章节事实投影。
        chapter_results: 按执行顺序排列的章节结果。
        accepted_conclusions: 按章节顺序排列的 accepted 结论摘要。
        blocked_reasons: 总体阻断原因。
        generated_chapter_ids: 实际尝试生成的章节。
        skipped_chapter_ids: 因真实 scope 或全局依赖阻断跳过的章节；前序正文章节失败不得写入此字段。
        schema_version: orchestration schema 版本。
    """

    status: ChapterOrchestrationStatus
    fund_code: str
    report_year: int
    projection: ChapterFactProjection
    chapter_results: tuple[ChapterRunResult, ...]
    accepted_conclusions: tuple[AcceptedChapterConclusion, ...]
    blocked_reasons: tuple[str, ...]
    generated_chapter_ids: tuple[int, ...]
    skipped_chapter_ids: tuple[int, ...]
    schema_version: ChapterOrchestratorSchemaVersion = CHAPTER_ORCHESTRATOR_SCHEMA_VERSION


@dataclass(frozen=True, slots=True, kw_only=True)
class _TypedTemplateInputs:
    """Service façade 内部 typed 模板输入。

    Attributes:
        evidence_availability: 从同源 `ChapterFactProjection` 派生的证据可用性。

    """

    evidence_availability: EvidenceAvailability


class ChapterOrchestrator:
    """Service 层章节编排 façade，见模板第 1-6 章。"""

    def __init__(self, fact_provider: ChapterFactProvider | None = None) -> None:
        """初始化章节编排器。

        Args:
            fact_provider: 可选 Gate 1 provider 注入；为 `None` 时按调用函数默认构造。

        Returns:
            无返回值。

        Raises:
            无显式抛出。
        """

        self._fact_provider = fact_provider

    def orchestrate(
        self,
        input_data: ChapterOrchestrationInput,
        *,
        llm_clients: ChapterOrchestratorLLMClients,
    ) -> ChapterOrchestrationResult:
        """编排模板第 1-6 章写作、审计和有限修复。

        Args:
            input_data: 章节编排输入。
            llm_clients: 显式注入的 writer/auditor LLM client。

        Returns:
            章节编排总结果。

        Raises:
            ValueError: 当输入投影缺少目标章节或参数非法时抛出。
        """

        return orchestrate_chapters(
            input_data,
            llm_clients=llm_clients,
            fact_provider=self._fact_provider,
        )


def build_chapter_orchestration_input(
    *,
    fund_code: str,
    report_year: int,
    structured_data: StructuredFundDataBundle | None = None,
    chapter_projection: ChapterFactProjection | None = None,
    policy: ChapterOrchestrationPolicy | None = None,
) -> ChapterOrchestrationInput:
    """构造章节编排输入，见模板第 1-6 章。

    Args:
        fund_code: 基金代码。
        report_year: 年报年份。
        structured_data: 已抽取完成的结构化基金数据包。
        chapter_projection: 已投影的 Gate 1 章节事实。
        policy: write-audit-repair 策略；未提供时使用默认策略。

    Returns:
        校验后的章节编排输入。

    Raises:
        ValueError: 当 payload 不是显式互斥或 identity 不一致时抛出。
    """

    has_bundle = structured_data is not None
    has_projection = chapter_projection is not None
    if has_bundle == has_projection:
        raise ValueError("必须且只能提供 structured_data 或 chapter_projection")
    input_kind: ChapterOrchestrationInputKind = (
        "structured_bundle" if has_bundle else "chapter_projection"
    )
    return ChapterOrchestrationInput(
        fund_code=fund_code,
        report_year=report_year,
        input_kind=input_kind,
        structured_data=structured_data,
        chapter_projection=chapter_projection,
        policy=policy or ChapterOrchestrationPolicy(),
    )


def orchestrate_chapters(
    input_data: ChapterOrchestrationInput,
    *,
    llm_clients: ChapterOrchestratorLLMClients,
    fact_provider: ChapterFactProvider | None = None,
    host_context: HostRunContext | None = None,
) -> ChapterOrchestrationResult:
    """编排模板第 1-6 章 write-audit-repair 流程。

    Args:
        input_data: 章节编排输入。
        llm_clients: 显式注入的 writer/auditor LLM client。
        fact_provider: 可选 Gate 1 provider；仅在 bundle 输入时使用。
        host_context: 可选 Host run 上下文；仅用于 deadline/cancel 检查和安全事件。

    Returns:
        章节编排总结果。

    Raises:
        ValueError: 当 projection 缺少目标章节或章节编号非法时抛出。
    """

    policy = input_data.policy
    projection = _resolve_projection(input_data, fact_provider=fact_provider)
    _validate_projection_coverage(projection, policy.target_chapter_ids)

    if projection.fund_type == "unknown":
        return _global_blocked_result(
            input_data,
            projection,
            stop_reason="fund_type_unknown",
            issue="基金类型 unknown，禁止生成模板第 1-6 章类型化章节。",
        )

    if policy.run_llm_audit and llm_clients.auditor is None:
        return _global_blocked_result(
            input_data,
            projection,
            stop_reason="llm_unavailable",
            issue="缺少显式注入的章节 LLM 审计 client，不能进入写作。",
        )

    from fund_agent.services.agent_bridge import run_agent_chapter_orchestration_bridge

    return run_agent_chapter_orchestration_bridge(
        input_data,
        projection=projection,
        llm_clients=llm_clients,
        host_context=host_context,
    )


def serialize_chapter_prompt_contract_diagnostics(
    orchestration_result: ChapterOrchestrationResult,
) -> dict[str, object]:
    """序列化脱敏章节 prompt-contract 诊断。

    该函数只输出章节状态、分类、计数和标量，不输出 prompt、draft、provider
    response、audit raw response、API key 或 header，供本 gate evidence 脚本安全消费。

    Args:
        orchestration_result: 章节编排结果。

    Returns:
        可 JSON 序列化的脱敏诊断 payload。

    Raises:
        无显式抛出。
    """

    return {
        "schema_version": "chapter_prompt_contract_diagnostic_payload.v1",
        "fund_code": orchestration_result.fund_code,
        "report_year": orchestration_result.report_year,
        "orchestration_status": orchestration_result.status,
        "first_failed": _first_failed_diagnostic(orchestration_result),
        "chapter_phase_matrix": tuple(
            _chapter_diagnostic_row(result) for result in orchestration_result.chapter_results
        ),
    }


def serialize_chapter_runtime_diagnostics(
    orchestration_result: ChapterOrchestrationResult,
) -> dict[str, object]:
    """序列化模板第 1-6 章 LLM runtime 安全诊断。

    该函数只输出 allowlisted scalar 字段，用于定位 provider runtime timeout
    发生点和 attempt budget。它不会输出 model_name、message、prompt、draft、
    raw response、raw audit、provider body、API key 或 header。

    Args:
        orchestration_result: 章节编排结果。

    Returns:
        可 JSON 序列化的 runtime 诊断 payload。

    Raises:
        无显式抛出。
    """

    return {
        "schema_version": _RUNTIME_DIAGNOSTIC_PAYLOAD_SCHEMA_VERSION,
        "fund_code": orchestration_result.fund_code,
        "report_year": orchestration_result.report_year,
        "orchestration_status": orchestration_result.status,
        "first_failed": _first_failed_runtime_diagnostic(orchestration_result),
        "chapter_runtime_matrix": tuple(
            _chapter_runtime_diagnostic_row(result)
            for result in orchestration_result.chapter_results
        ),
    }


def _validate_policy(policy: ChapterOrchestrationPolicy) -> None:
    """校验模板第 1-6 章编排策略。

    Args:
        policy: 待校验策略。

    Returns:
        无返回值。

    Raises:
        ValueError: 当策略非法时抛出。
    """

    chapter_ids = policy.target_chapter_ids
    if not chapter_ids:
        raise ValueError("target_chapter_ids 不能为空")
    if len(set(chapter_ids)) != len(chapter_ids):
        raise ValueError("target_chapter_ids 不能重复")
    invalid_ids = tuple(chapter_id for chapter_id in chapter_ids if chapter_id not in _TARGET_CHAPTER_ID_SET)
    if invalid_ids:
        raise ValueError(f"Gate 3 只允许生成模板第 1-6 章：{invalid_ids}")
    if policy.max_repair_attempts < 0:
        raise ValueError("max_repair_attempts 必须大于等于 0")
    if policy.max_output_chars <= 0:
        raise ValueError("max_output_chars 必须为正数")
    if policy.prompt_payload_mode not in {"full", "compact"}:
        raise ValueError("prompt_payload_mode 必须为 full 或 compact")
    if policy.typed_template_path not in _ALLOWED_TYPED_TEMPLATE_PATH_MODES:
        raise ValueError("typed_template_path 必须为 legacy_contract / typed_template_contract")


def _validate_orchestration_input(input_data: ChapterOrchestrationInput) -> None:
    """校验章节编排输入。

    Args:
        input_data: 待校验输入。

    Returns:
        无返回值。

    Raises:
        ValueError: 当输入来源或同源字段不一致时抛出。
    """

    if input_data.schema_version != CHAPTER_ORCHESTRATOR_SCHEMA_VERSION:
        raise ValueError(f"未知章节编排 schema：{input_data.schema_version}")
    if input_data.input_kind not in get_args(ChapterOrchestrationInputKind):
        raise ValueError(f"未知章节编排输入类型：{input_data.input_kind}")
    if input_data.input_kind == "structured_bundle":
        if input_data.structured_data is None or input_data.chapter_projection is not None:
            raise ValueError("structured_bundle 输入必须只提供 structured_data")
        _validate_identity(
            input_data.fund_code,
            input_data.report_year,
            input_data.structured_data.fund_code,
            input_data.structured_data.report_year,
        )
        return
    if input_data.chapter_projection is None or input_data.structured_data is not None:
        raise ValueError("chapter_projection 输入必须只提供 chapter_projection")
    _validate_identity(
        input_data.fund_code,
        input_data.report_year,
        input_data.chapter_projection.fund_code,
        input_data.chapter_projection.report_year,
    )


def _validate_identity(
    fund_code: str,
    report_year: int,
    actual_fund_code: str,
    actual_report_year: int,
) -> None:
    """校验基金代码和年报年份同源。

    Args:
        fund_code: 调用方声明基金代码。
        report_year: 调用方声明年报年份。
        actual_fund_code: payload 中的基金代码。
        actual_report_year: payload 中的年报年份。

    Returns:
        无返回值。

    Raises:
        ValueError: 当 identity 不一致时抛出。
    """

    if fund_code != actual_fund_code or report_year != actual_report_year:
        raise ValueError(
            "章节编排输入 identity 不一致："
            f"request={fund_code}/{report_year}, payload={actual_fund_code}/{actual_report_year}"
        )


def _resolve_projection(
    input_data: ChapterOrchestrationInput,
    *,
    fact_provider: ChapterFactProvider | None,
) -> ChapterFactProjection:
    """解析 Gate 1 章节事实投影。

    Args:
        input_data: 章节编排输入。
        fact_provider: 可选注入 provider，仅用于 bundle 输入。

    Returns:
        Gate 1 章节事实投影。

    Raises:
        ValueError: 当输入 payload 缺失时抛出。
    """

    if input_data.input_kind == "chapter_projection":
        if input_data.chapter_projection is None:
            raise ValueError("chapter_projection 输入缺少 projection")
        return input_data.chapter_projection
    if input_data.structured_data is None:
        raise ValueError("structured_bundle 输入缺少 structured_data")
    provider = fact_provider or ChapterFactProvider()
    return provider.project(input_data.structured_data, chapter_ids=input_data.policy.target_chapter_ids)


def _validate_projection_coverage(
    projection: ChapterFactProjection,
    chapter_ids: tuple[int, ...],
) -> None:
    """校验 projection 覆盖所有目标章节且唯一。

    Args:
        projection: Gate 1 章节事实投影。
        chapter_ids: 目标章节编号。

    Returns:
        无返回值。

    Raises:
        ValueError: 当章节缺失或重复时抛出。
    """

    counts = {chapter_id: 0 for chapter_id in chapter_ids}
    for chapter in projection.chapters:
        if chapter.chapter_id in counts:
            counts[chapter.chapter_id] += 1
    invalid = {chapter_id: count for chapter_id, count in counts.items() if count != 1}
    if invalid:
        raise ValueError(f"projection 必须唯一覆盖目标章节：{invalid}")


def _global_blocked_result(
    input_data: ChapterOrchestrationInput,
    projection: ChapterFactProjection,
    *,
    stop_reason: ChapterRunStopReason,
    issue: str,
) -> ChapterOrchestrationResult:
    """构造全局 fail-closed 阻断结果。

    Args:
        input_data: 章节编排输入。
        projection: Gate 1 投影。
        stop_reason: 每章停止原因。
        issue: 中文阻断原因。

    Returns:
        总体 blocked 的编排结果。

    Raises:
        ValueError: 当章节缺失时抛出。
    """

    chapter_results = tuple(
        ChapterRunResult(
            chapter_id=chapter_id,
            title=_chapter_title(projection, chapter_id),
            status="blocked",
            stop_reason=stop_reason,
            accepted_draft=None,
            accepted_conclusion=None,
            attempts=(),
            issues=(issue,),
            failure_category=_chapter_failure_category_from_stop_reason(stop_reason),
        )
        for chapter_id in input_data.policy.target_chapter_ids
    )
    return ChapterOrchestrationResult(
        status="blocked",
        fund_code=input_data.fund_code,
        report_year=input_data.report_year,
        projection=projection,
        chapter_results=chapter_results,
        accepted_conclusions=(),
        blocked_reasons=(issue,),
        generated_chapter_ids=(),
        skipped_chapter_ids=(),
    )


def _typed_template_inputs(
    projection: ChapterFactProjection,
    *,
    policy: ChapterOrchestrationPolicy,
) -> _TypedTemplateInputs | None:
    """按显式 policy 构造 typed contract / availability 输入。

    Args:
        projection: Gate 1 章节事实投影。
        policy: Service-owned 章节编排策略。

    Returns:
        typed path 开启时返回内部 typed 输入；默认 legacy path 返回 `None`。

    Raises:
        ValueError: 当 typed path 模式非法或 availability 派生失败时抛出。
    """

    if policy.typed_template_path == "legacy_contract":
        return None
    if policy.typed_template_path != "typed_template_contract":
        raise ValueError("typed_template_path 必须为 legacy_contract / typed_template_contract")
    return _TypedTemplateInputs(
        evidence_availability=derive_evidence_availability(projection),
    )


def _typed_chapter_contract(
    chapter_id: int,
    *,
    typed_inputs: _TypedTemplateInputs | None,
) -> TypedChapterContract | None:
    """读取 typed path 的单章 contract。

    Args:
        chapter_id: 模板章节编号。
        typed_inputs: typed path 内部输入；为空表示 legacy path。

    Returns:
        typed 单章 contract；legacy path 返回 `None`。

    Raises:
        ValueError: 当 typed sidecar 缺失或校验失败时由 Fund 层 loader 抛出。
    """

    if typed_inputs is None:
        return None
    return get_typed_chapter_contract(chapter_id)


def _typed_required_output_items(
    chapter_id: int,
    *,
    typed_inputs: _TypedTemplateInputs | None,
) -> tuple[RequiredOutputItem, ...]:
    """读取 typed path 的 required output items。

    Args:
        chapter_id: 模板章节编号。
        typed_inputs: typed path 内部输入；为空表示 legacy path。

    Returns:
        typed required output items；legacy path 返回空元组。

    Raises:
        ValueError: 当 typed sidecar 缺失或校验失败时由 Fund 层 loader 抛出。
    """

    typed_contract = _typed_chapter_contract(chapter_id, typed_inputs=typed_inputs)
    if typed_contract is None:
        return ()
    return typed_contract.required_output_items


def _typed_evidence_availability(
    typed_inputs: _TypedTemplateInputs | None,
) -> EvidenceAvailability | None:
    """读取 typed path 的同源 EvidenceAvailability。

    Args:
        typed_inputs: typed path 内部输入；为空表示 legacy path。

    Returns:
        `EvidenceAvailability` 或 `None`。

    Raises:
        无显式抛出。
    """

    if typed_inputs is None:
        return None
    return typed_inputs.evidence_availability


def _exception_runtime_diagnostics(
    projection: ChapterFactProjection,
    *,
    chapter_id: int,
    operation: ProviderOperation,
    attempt_index: int,
    exc: Exception,
) -> tuple[ChapterLLMRuntimeDiagnostic, ...]:
    """从 provider 或未知异常构造章节级安全诊断。

    Args:
        projection: Gate 1 投影。
        chapter_id: 模板章节编号。
        operation: writer 或 auditor。
        attempt_index: 章节 attempt 序号。
        exc: 捕获到的异常。

    Returns:
        已补齐章节 identity 和 failure category 的安全诊断。

    Raises:
        无显式抛出。
    """

    provider_diagnostics = getattr(exc, "diagnostics", ())
    if provider_diagnostics:
        return tuple(
            _enrich_provider_diagnostic(
                diagnostic,
                projection,
                chapter_id=chapter_id,
                attempt_index=attempt_index,
            )
            for diagnostic in provider_diagnostics
        )
    return (
        ChapterLLMRuntimeDiagnostic(
            operation=operation,
            chapter_id=chapter_id,
            fund_code=projection.fund_code,
            report_year=projection.report_year,
            repair_attempt_index=attempt_index,
            provider_attempt_index=None,
            provider_max_attempts=None,
            provider_runtime_category=_provider_runtime_category_from_exception(exc),
            chapter_failure_category=_chapter_failure_category_from_exception(exc),
            elapsed_ms=None,
            status_code=None,
            request_id=None,
            model_name=None,
            finish_reason=None,
            response_chars=None,
            error_type=type(exc).__name__,
            message=_safe_exception_message(exc),
        ),
    )


def _enrich_provider_diagnostic(
    diagnostic: ChapterLLMRuntimeDiagnostic,
    projection: ChapterFactProjection,
    *,
    chapter_id: int,
    attempt_index: int,
) -> ChapterLLMRuntimeDiagnostic:
    """给 provider-local diagnostic 补齐章节身份和失败分类。

    Args:
        diagnostic: provider-local 安全诊断。
        projection: Gate 1 投影。
        chapter_id: 模板章节编号。
        attempt_index: 章节 attempt 序号。

    Returns:
        章节级安全诊断。

    Raises:
        无显式抛出。
    """

    return ChapterLLMRuntimeDiagnostic(
        operation=diagnostic.operation,
        chapter_id=chapter_id,
        fund_code=projection.fund_code,
        report_year=projection.report_year,
        repair_attempt_index=attempt_index,
        provider_attempt_index=diagnostic.provider_attempt_index,
        provider_max_attempts=diagnostic.provider_max_attempts,
        provider_runtime_category=diagnostic.provider_runtime_category,
        chapter_failure_category=_chapter_failure_category_from_provider_runtime(
            diagnostic.provider_runtime_category
        ),
        elapsed_ms=diagnostic.elapsed_ms,
        status_code=diagnostic.status_code,
        request_id=diagnostic.request_id,
        model_name=diagnostic.model_name,
        finish_reason=diagnostic.finish_reason,
        response_chars=diagnostic.response_chars,
        error_type=diagnostic.error_type,
        system_prompt_chars=diagnostic.system_prompt_chars,
        user_prompt_chars=diagnostic.user_prompt_chars,
        approx_prompt_tokens=diagnostic.approx_prompt_tokens,
        allowed_fact_count=diagnostic.allowed_fact_count,
        allowed_anchor_count=diagnostic.allowed_anchor_count,
        max_output_chars=diagnostic.max_output_chars,
        timeout_seconds=diagnostic.timeout_seconds,
        timeout_max_attempts=diagnostic.timeout_max_attempts,
        timeout_backoff_seconds=diagnostic.timeout_backoff_seconds,
        timeout_budget_kind=diagnostic.timeout_budget_kind,
        repair_timeout_fallback_used=diagnostic.repair_timeout_fallback_used,
        timeout_root_cause_hint=_timeout_root_cause_hint(diagnostic),
        prompt_cost_diagnostic=diagnostic.prompt_cost_diagnostic,
        message=diagnostic.message,
    )


def _writer_runtime_diagnostic(
    projection: ChapterFactProjection,
    *,
    chapter_id: int,
    operation: ProviderOperation,
    attempt_index: int,
    writer_result: ChapterWriteResult,
) -> ChapterLLMRuntimeDiagnostic:
    """从 writer blocked result 构造章节级安全诊断。

    Args:
        projection: Gate 1 投影。
        chapter_id: 模板章节编号。
        operation: writer。
        attempt_index: 章节 attempt 序号。
        writer_result: writer 结果。

    Returns:
        章节级安全诊断。

    Raises:
        无显式抛出。
    """

    message = "; ".join(_writer_issue_messages(writer_result)) or writer_result.stop_reason
    return ChapterLLMRuntimeDiagnostic(
        operation=operation,
        chapter_id=chapter_id,
        fund_code=projection.fund_code,
        report_year=projection.report_year,
        repair_attempt_index=attempt_index,
        provider_attempt_index=None,
        provider_max_attempts=None,
        provider_runtime_category=None,
        chapter_failure_category=_chapter_failure_category_from_writer_result(writer_result),
        elapsed_ms=None,
        status_code=None,
        request_id=None,
        model_name=None,
        finish_reason=None,
        response_chars=None,
        error_type=None,
        message=_sanitize_text(message),
    )


def _audit_runtime_diagnostic(
    projection: ChapterFactProjection,
    *,
    chapter_id: int,
    operation: ProviderOperation,
    attempt_index: int,
    audit_result: ChapterAuditResult,
) -> ChapterLLMRuntimeDiagnostic:
    """从 audit failed/blocked result 构造章节级安全诊断。

    Args:
        projection: Gate 1 投影。
        chapter_id: 模板章节编号。
        operation: auditor。
        attempt_index: 章节 attempt 序号。
        audit_result: 审计结果。

    Returns:
        章节级安全诊断。

    Raises:
        无显式抛出。
    """

    message = "; ".join(_audit_issue_messages(audit_result)) or audit_result.status
    return ChapterLLMRuntimeDiagnostic(
        operation=operation,
        chapter_id=chapter_id,
        fund_code=projection.fund_code,
        report_year=projection.report_year,
        repair_attempt_index=attempt_index,
        provider_attempt_index=None,
        provider_max_attempts=None,
        provider_runtime_category=None,
        chapter_failure_category=_chapter_failure_category_from_audit_result(audit_result),
        elapsed_ms=None,
        status_code=None,
        request_id=None,
        model_name=audit_result.llm.model_name,
        finish_reason=audit_result.llm.finish_reason,
        response_chars=len(audit_result.llm.raw_response) if audit_result.llm.raw_response else None,
        error_type=None,
        message=_sanitize_text(message),
    )


def _provider_runtime_category_from_exception(
    exc: Exception,
) -> ProviderRuntimeCategory | None:
    """把异常类型映射为 provider runtime category。

    Args:
        exc: 捕获到的异常。

    Returns:
        provider runtime 分类；非 provider runtime 返回 `None`。

    Raises:
        无显式抛出。
    """

    type_name = type(exc).__name__
    if type_name == "LLMProviderTimeoutError":
        return "timeout"
    if type_name == "LLMProviderRateLimitError":
        return "rate_limit"
    if type_name == "LLMProviderMalformedResponseError":
        return "malformed"
    if type_name == "LLMProviderNetworkError":
        return "network"
    if type_name == "LLMProviderRuntimeError":
        return "http_error"
    return None


def _chapter_failure_category_from_exception(exc: Exception) -> ChapterFailureCategory:
    """把异常类型映射为章节失败分类。

    Args:
        exc: 捕获到的异常。

    Returns:
        章节失败分类。

    Raises:
        无显式抛出。
    """

    if _provider_runtime_category_from_exception(exc) is not None:
        return _chapter_failure_category_from_provider_runtime(
            _provider_runtime_category_from_exception(exc)
        )
    return "code_bug"


def _chapter_failure_category_from_provider_runtime(
    provider_runtime_category: ProviderRuntimeCategory | None,
) -> ChapterFailureCategory:
    """把 provider runtime 分类映射为章节失败分类。

    Args:
        provider_runtime_category: provider-local runtime 分类。

    Returns:
        timeout 独立归为 `llm_timeout`，其他 provider runtime 归为 `provider_runtime`。

    Raises:
        无显式抛出。
    """

    if provider_runtime_category == "timeout":
        return "llm_timeout"
    return "provider_runtime"


def _chapter_failure_category_from_stop_reason(
    stop_reason: ChapterRunStopReason,
) -> ChapterFailureCategory:
    """按全局阻断 stop reason 推导章节失败分类。

    Args:
        stop_reason: Service 层停止原因。

    Returns:
        章节失败分类。

    Raises:
        无显式抛出。
    """

    if stop_reason == "llm_timeout":
        return "llm_timeout"
    if stop_reason in ("fund_type_unknown", "missing_required_facts", "needs_more_facts", "dependency_missing"):
        return "fact_gap"
    if stop_reason in (
        "llm_empty_response",
        "llm_contract_violation",
        "missing_required_structure",
        "missing_required_output_marker",
        "unknown_anchor",
        "response_too_long",
        "response_incomplete",
    ):
        return "prompt_contract"
    if stop_reason.startswith("llm_"):
        return "provider_runtime"
    return "code_bug"


def _chapter_failure_category_from_writer_result(
    writer_result: ChapterWriteResult,
) -> ChapterFailureCategory:
    """把 writer blocked result 映射为章节失败分类。

    Args:
        writer_result: writer 结果。

    Returns:
        章节失败分类。

    Raises:
        无显式抛出。
    """

    if writer_result.stop_reason in {
        "missing_required_facts",
        "evidence_anchor_missing",
        "item_rule_deleted_required_content",
        "fund_type_unknown",
    }:
        return "fact_gap"
    if writer_result.stop_reason in {
        "llm_empty_response",
        "llm_contract_violation",
        "missing_required_structure",
        "missing_required_output_marker",
        "unknown_anchor",
        "response_too_long",
        "response_incomplete",
    }:
        return "prompt_contract"
    return "code_bug"


def _chapter_failure_category_from_audit_result(
    audit_result: ChapterAuditResult,
) -> ChapterFailureCategory:
    """把 audit failed/blocked result 映射为章节失败分类。

    Args:
        audit_result: 审计结果。

    Returns:
        章节失败分类。

    Raises:
        无显式抛出。
    """

    issue_ids = set(_audit_issue_ids(audit_result))
    if "llm:parse_failure" in issue_ids:
        return "audit_parse"
    if audit_result.repair_hint == "needs_more_facts":
        return "fact_gap"
    if _is_audit_rule_too_strict(audit_result):
        return "audit_rule_too_strict"
    if audit_result.status in ("fail", "blocked"):
        return "prompt_contract"
    return "code_bug"


def _writer_prompt_contract_diagnostic(
    writer_result: ChapterWriteResult,
    *,
    chapter_id: int,
    attempt_index: int,
) -> ChapterPromptContractDiagnostic | None:
    """从 writer 失败派生脱敏 prompt-contract 子类诊断。

    Args:
        writer_result: Gate 2 writer 结果。
        chapter_id: 模板章节编号。
        attempt_index: 章节 attempt 序号。

    Returns:
        prompt-contract 诊断；非 prompt-contract 失败返回 `None`。

    Raises:
        无显式抛出。
    """

    if _chapter_failure_category_from_writer_result(writer_result) != "prompt_contract":
        return None
    reason_counts = _writer_issue_reason_counts(writer_result)
    prefix_counts = _writer_issue_id_prefix_counts(writer_result)
    required_structure_missing_count = reason_counts.get("missing_required_structure", 0)
    required_output_missing_count = reason_counts.get("missing_required_output_marker", 0)
    unknown_anchor_count = max(reason_counts.get("unknown_anchor", 0), prefix_counts.get("writer:unknown_anchor", 0))
    invalid_marker_count = sum(prefix_counts.get(prefix, 0) for prefix in _INVALID_MARKER_PREFIXES)
    forbidden_phrase_count = prefix_counts.get(_FORBIDDEN_PHRASE_PREFIX, 0)
    response_length_incomplete_count = _writer_response_length_incomplete_count(writer_result)
    subcategory = _primary_subcategory(
        response_length_incomplete_count=response_length_incomplete_count,
        invalid_marker_count=invalid_marker_count,
        unknown_anchor_count=unknown_anchor_count,
        required_output_missing_count=required_output_missing_count,
        required_structure_missing_count=required_structure_missing_count,
        candidate_facet_assertion_count=0,
        forbidden_phrase_count=forbidden_phrase_count,
        l1_numerical_closure_count=0,
        has_any_counter=bool(reason_counts or prefix_counts),
    )
    return ChapterPromptContractDiagnostic(
        schema_version=_DIAGNOSTIC_SCHEMA_VERSION,
        chapter_id=chapter_id,
        phase="writer_parse",
        attempt_index=attempt_index,
        primary_subcategory=subcategory,
        issue_reason_counts=reason_counts,
        issue_id_prefix_counts=prefix_counts,
        required_structure_missing_count=required_structure_missing_count,
        required_output_missing_count=required_output_missing_count,
        unknown_anchor_count=unknown_anchor_count,
        invalid_marker_count=invalid_marker_count,
        forbidden_phrase_count=forbidden_phrase_count,
        l1_numerical_closure_count=0,
        candidate_facet_assertion_count=0,
        response_length_incomplete_count=response_length_incomplete_count,
        response_chars=writer_result.response_chars,
        max_output_chars=writer_result.max_output_chars,
        finish_reason=writer_result.finish_reason,
        accepted_draft_present=False,
    )


def _audit_prompt_contract_diagnostic(
    audit_result: ChapterAuditResult,
    *,
    chapter_id: int,
    attempt_index: int,
) -> ChapterPromptContractDiagnostic | None:
    """从 programmatic/LLM audit 失败派生脱敏 prompt-contract 子类诊断。

    Args:
        audit_result: Gate 2 审计结果。
        chapter_id: 模板章节编号。
        attempt_index: 章节 attempt 序号。

    Returns:
        prompt-contract 诊断；非 prompt-contract 失败返回 `None`。

    Raises:
        无显式抛出。
    """

    if _chapter_failure_category_from_audit_result(audit_result) != "prompt_contract":
        return None
    issues = _all_audit_issues(audit_result)
    prefix_counts = _audit_issue_id_prefix_counts(issues)
    candidate_facet_assertion_count = sum(1 for issue in issues if _is_candidate_facet_assertion_issue(issue))
    forbidden_phrase_count = sum(1 for issue in issues if _is_forbidden_phrase_issue(issue))
    l1_numerical_closure_count = prefix_counts.get(_PROGRAMMATIC_L1_PREFIX, 0)
    subcategory = _primary_subcategory(
        response_length_incomplete_count=0,
        invalid_marker_count=0,
        unknown_anchor_count=0,
        required_output_missing_count=0,
        required_structure_missing_count=0,
        candidate_facet_assertion_count=candidate_facet_assertion_count,
        forbidden_phrase_count=forbidden_phrase_count,
        l1_numerical_closure_count=l1_numerical_closure_count,
        has_any_counter=bool(prefix_counts),
    )
    return ChapterPromptContractDiagnostic(
        schema_version=_DIAGNOSTIC_SCHEMA_VERSION,
        chapter_id=chapter_id,
        phase="programmatic_audit",
        attempt_index=attempt_index,
        primary_subcategory=subcategory,
        issue_reason_counts={},
        issue_id_prefix_counts=prefix_counts,
        required_structure_missing_count=0,
        required_output_missing_count=0,
        unknown_anchor_count=0,
        invalid_marker_count=0,
        forbidden_phrase_count=forbidden_phrase_count,
        l1_numerical_closure_count=l1_numerical_closure_count,
        candidate_facet_assertion_count=candidate_facet_assertion_count,
        response_length_incomplete_count=0,
        response_chars=len(audit_result.llm.raw_response) if audit_result.llm.raw_response else None,
        max_output_chars=None,
        finish_reason=audit_result.llm.finish_reason,
        accepted_draft_present=False,
    )


def _primary_subcategory(
    *,
    response_length_incomplete_count: int,
    invalid_marker_count: int,
    unknown_anchor_count: int,
    required_output_missing_count: int,
    required_structure_missing_count: int,
    candidate_facet_assertion_count: int,
    forbidden_phrase_count: int,
    l1_numerical_closure_count: int,
    has_any_counter: bool,
) -> ChapterFailureSubcategory:
    """按固定优先级选择 prompt-contract 主子类。

    Args:
        response_length_incomplete_count: 响应长度/不完整计数。
        invalid_marker_count: 非法 marker 计数。
        unknown_anchor_count: 未授权 anchor 计数。
        required_output_missing_count: 缺 required output marker 计数。
        required_structure_missing_count: 缺结构段落计数。
        candidate_facet_assertion_count: 候选 facet 断言计数。
        forbidden_phrase_count: 禁用措辞计数。
        l1_numerical_closure_count: L1 数字闭环缺邻近证据计数。
        has_any_counter: 是否存在任何 issue 计数。

    Returns:
        主子类；无法映射时返回 `code_bug_other`。

    Raises:
        无显式抛出。
    """

    counters: dict[ChapterFailureSubcategory, int] = {
        "response_length_incomplete": response_length_incomplete_count,
        "invalid_marker": invalid_marker_count,
        "unknown_anchor": unknown_anchor_count,
        "missing_required_marker": required_output_missing_count,
        "missing_structure": required_structure_missing_count,
        "candidate_facet_assertion": candidate_facet_assertion_count,
        "forbidden_phrase": forbidden_phrase_count,
        "l1_numerical_closure": l1_numerical_closure_count,
    }
    for subcategory in _SUBCATEGORY_PRECEDENCE:
        if subcategory == "code_bug_other":
            continue
        if counters.get(subcategory, 0) > 0:
            return subcategory
    return "code_bug_other" if not has_any_counter else "code_bug_other"


def _writer_issue_reason_counts(writer_result: ChapterWriteResult) -> dict[str, int]:
    """统计 writer issue reason，不包含 issue message。

    Args:
        writer_result: Gate 2 writer 结果。

    Returns:
        reason 到计数的映射。

    Raises:
        无显式抛出。
    """

    counts: dict[str, int] = {}
    for issue in writer_result.issues:
        counts[issue.reason] = counts.get(issue.reason, 0) + 1
    return counts


def _writer_issue_id_prefix_counts(writer_result: ChapterWriteResult) -> dict[str, int]:
    """统计 writer issue id prefix，剥离 raw anchor/missing/phrase suffix。

    Args:
        writer_result: Gate 2 writer 结果。

    Returns:
        prefix 到计数的映射。

    Raises:
        无显式抛出。
    """

    counts: dict[str, int] = {}
    for issue in writer_result.issues:
        prefix = _writer_issue_id_prefix(issue.issue_id)
        counts[prefix] = counts.get(prefix, 0) + 1
    return counts


def _writer_issue_id_prefix(issue_id: str) -> str:
    """把 writer issue id 归一到安全 prefix。

    Args:
        issue_id: 原始 writer issue id。

    Returns:
        不含 raw suffix 的 issue id prefix。

    Raises:
        无显式抛出。
    """

    if not issue_id.startswith("writer:"):
        return issue_id.split(":", 1)[0]
    parts = issue_id.split(":")
    if len(parts) >= 2:
        return ":".join(parts[:2])
    return issue_id


def _audit_issue_id_prefix_counts(issues: tuple[ChapterAuditIssue, ...]) -> dict[str, int]:
    """统计 audit issue id prefix，剥离 raw location/hash suffix。

    Args:
        issues: audit issues。

    Returns:
        prefix 到计数的映射。

    Raises:
        无显式抛出。
    """

    counts: dict[str, int] = {}
    for issue in issues:
        prefix = _audit_issue_id_prefix(issue.issue_id)
        counts[prefix] = counts.get(prefix, 0) + 1
    return counts


def _audit_issue_id_prefix(issue_id: str) -> str:
    """把 audit issue id 归一到安全 prefix。

    Args:
        issue_id: 原始 audit issue id。

    Returns:
        不含 raw location/hash suffix 的 issue id prefix。

    Raises:
        无显式抛出。
    """

    parts = issue_id.split(":")
    if not parts:
        return issue_id
    if parts[0] == "programmatic" and len(parts) >= 2:
        return ":".join(parts[:2])
    if parts[0] == "llm" and len(parts) >= 3:
        return ":".join(parts[:3])
    return parts[0]


def _writer_response_length_incomplete_count(writer_result: ChapterWriteResult) -> int:
    """统计 writer 响应超长/不完整信号。

    Args:
        writer_result: Gate 2 writer 结果。

    Returns:
        命中的长度/不完整信号计数。

    Raises:
        无显式抛出。
    """

    count = 0
    reason_counts = _writer_issue_reason_counts(writer_result)
    count += reason_counts.get("response_too_long", 0)
    count += reason_counts.get("response_incomplete", 0)
    if writer_result.finish_reason in _INCOMPLETE_FINISH_REASONS:
        count += 1
    if (
        writer_result.response_chars is not None
        and writer_result.max_output_chars is not None
        and writer_result.response_chars > writer_result.max_output_chars
    ):
        count += 1
    return count


def _is_candidate_facet_assertion_issue(issue: ChapterAuditIssue) -> bool:
    """判断 audit issue 是否为候选 facet 被断言。

    Args:
        issue: audit issue。

    Returns:
        命中候选 facet 断言语义时返回 `True`。

    Raises:
        无显式抛出。
    """

    text = f"{issue.rule_code} {issue.message} {issue.location or ''}"
    return "候选 facet" in text and "断言" in text


def _is_forbidden_phrase_issue(issue: ChapterAuditIssue) -> bool:
    """判断 audit issue 是否为禁用措辞。

    Args:
        issue: audit issue。

    Returns:
        命中禁用措辞语义时返回 `True`。

    Raises:
        无显式抛出。
    """

    text = f"{issue.rule_code} {issue.message}"
    return issue.rule_code == "C1" and "禁用措辞" in text


def _is_audit_rule_too_strict(audit_result: ChapterAuditResult) -> bool:
    """判断失败是否满足 LLM 审计规则过严分类。

    Args:
        audit_result: Gate 2 审计结果。

    Returns:
        仅当 programmatic pass、LLM 可解析失败、无 parse failure、无事实缺口时返回 `True`。

    Raises:
        无显式抛出。
    """

    if audit_result.programmatic.status != "pass":
        return False
    if audit_result.llm.status not in ("fail", "blocked"):
        return False
    if not audit_result.llm.issues:
        return False
    if any(issue.rule_code == "LLM_UNAVAILABLE" for issue in audit_result.llm.issues):
        return False
    if any(issue.issue_id == "llm:parse_failure" for issue in audit_result.llm.issues):
        return False
    return not any(_is_fact_gap_issue(issue) for issue in audit_result.llm.issues)


def _is_fact_gap_issue(issue: ChapterAuditIssue) -> bool:
    """判断 LLM 审计 issue 是否表达事实缺口。

    Args:
        issue: LLM 审计 issue。

    Returns:
        命中 needs_more_facts 或 fact_gap 语义时返回 `True`。

    Raises:
        无显式抛出。
    """

    text = f"{issue.issue_id} {issue.message} {issue.repair_hint}".lower()
    return "needs_more_facts" in text or "fact_gap" in text


def _safe_exception_message(exc: Exception) -> str:
    """生成不包含 prompt/key/header 的异常摘要。

    Args:
        exc: 捕获到的异常。

    Returns:
        单行、限长异常摘要。

    Raises:
        无显式抛出。
    """

    return _sanitize_text(str(exc), max_chars=_MAX_REPAIR_MESSAGE_CHARS)


def _decide_repair(
    audit_result: ChapterAuditResult,
    *,
    remaining_budget: int,
    auditor_available: bool,
    run_llm_audit: bool,
) -> ChapterRepairDecision:
    """根据 Gate 2 审计结果决定 repair 行为，见模板第 1-6 章。

    Args:
        audit_result: Gate 2 章节审计结果。
        remaining_budget: 当前审计失败后剩余 regenerate 次数。
        auditor_available: 是否显式注入 auditor client。
        run_llm_audit: 当前策略是否要求 LLM 审计。

    Returns:
        单次 repair 决策。

    Raises:
        无显式抛出。
    """

    issue_ids = _audit_issue_ids(audit_result)
    repair_hint = audit_result.repair_hint
    if audit_result.accepted:
        return ChapterRepairDecision(
            action="none",
            reason="章节审计已通过，无需修复。",
            stop_reason="none",
            source_repair_hint=repair_hint,
            issue_ids=issue_ids,
        )
    if run_llm_audit and not auditor_available:
        return ChapterRepairDecision(
            action="stop",
            reason="缺少显式注入的章节 LLM 审计 client，不能通过重写修复。",
            stop_reason="llm_unavailable",
            source_repair_hint=repair_hint,
            issue_ids=issue_ids,
        )
    if audit_result.llm.status == "blocked" and _has_llm_unavailable_issue(audit_result):
        return ChapterRepairDecision(
            action="stop",
            reason="LLM 审计不可用，停止本章且不重试 writer。",
            stop_reason="llm_unavailable",
            source_repair_hint=repair_hint,
            issue_ids=issue_ids,
        )
    if repair_hint == "needs_more_facts":
        return ChapterRepairDecision(
            action="needs_more_facts",
            reason="审计要求更多同源事实，Service 不进行 source probing。",
            stop_reason="needs_more_facts",
            source_repair_hint=repair_hint,
            issue_ids=issue_ids,
        )
    if repair_hint == "none":
        return ChapterRepairDecision(
            action="stop",
            reason="审计未提供安全修复依据。",
            stop_reason=_auditor_failure_stop_reason(audit_result),
            source_repair_hint=repair_hint,
            issue_ids=issue_ids,
        )
    if remaining_budget <= 0:
        return ChapterRepairDecision(
            action="stop",
            reason="章节修复预算耗尽。",
            stop_reason="repair_budget_exhausted",
            source_repair_hint=repair_hint,
            issue_ids=issue_ids,
        )
    if audit_result.status in ("blocked", "fail") and repair_hint in ("patch", "regenerate"):
        return ChapterRepairDecision(
            action="regenerate",
            reason="MVP 暂无 typed patch API，将 patch/regenerate 映射为预算内整章重写。",
            stop_reason="none",
            source_repair_hint=repair_hint,
            issue_ids=issue_ids,
        )
    return ChapterRepairDecision(
        action="stop",
        reason="审计状态不支持安全修复。",
        stop_reason=_auditor_failure_stop_reason(audit_result),
        source_repair_hint=repair_hint,
        issue_ids=issue_ids,
    )


def _auditor_failure_stop_reason(audit_result: ChapterAuditResult) -> ChapterRunStopReason:
    """把审计失败状态转换为默认 typed stop reason，见模板第 1-6 章。

    Args:
        audit_result: Gate 2 章节审计结果。

    Returns:
        Service 层停止原因。

    Raises:
        无显式抛出。
    """

    if audit_result.status == "blocked":
        return "auditor_blocked"
    return "auditor_failed"


def _repair_context_from_audit(
    audit_result: ChapterAuditResult,
    *,
    attempt_index: int,
) -> ChapterRepairContext:
    """从上一轮审计结果构造 typed repair context。

    Args:
        audit_result: Gate 2 审计结果。
        attempt_index: 即将执行的重写 attempt 序号。

    Returns:
        章节重写上下文。

    Raises:
        无显式抛出。
    """

    issues = _all_audit_issues(audit_result)
    return ChapterRepairContext(
        attempt_index=attempt_index,
        previous_issue_ids=tuple(issue.issue_id for issue in issues),
        previous_messages=tuple(_sanitize_text(issue.message) for issue in issues),
        required_corrections=_required_corrections_from_issues(issues),
    )


def _required_corrections_from_issues(
    issues: tuple[ChapterAuditIssue, ...],
) -> tuple[str, ...]:
    """按确定性映射生成重写必须修复项。

    Args:
        issues: 上一轮审计 issue。

    Returns:
        去重后的修正项。

    Raises:
        无显式抛出。
    """

    corrections: list[str] = []
    for issue in issues:
        correction = _required_correction_from_issue(issue)
        if correction not in corrections:
            corrections.append(correction)
    return tuple(corrections)


def _required_correction_from_issue(issue: ChapterAuditIssue) -> str:
    """把单条审计 issue 映射为确定性修正项。

    Args:
        issue: 上一轮审计 issue。

    Returns:
        修正项文本。

    Raises:
        无显式抛出。
    """

    message = issue.message
    location = issue.location or ""
    if issue.rule_code == "P1" and _mentions_structure(message, location):
        return "补齐 ### 结论要点 / ### 详细情况 / ### 证据与出处 固定结构段落。"
    if issue.rule_code == "C2" and _mentions_required_output(message, location):
        return (
            "为对应 required output item 补齐 <!-- required_output:<item> --> marker，"
            "并在 marker 后只写有同源证据或明确缺口的内容。"
        )
    if issue.rule_code == "C2" and issue.item_rule_ids:
        return (
            "删除 ITEM_RULE 要求删除的 optional/conditional 段落标题和专属段落；"
            "不得删除 required output marker，若相关语义属于 required output，"
            "只能在 required output 下用同源证据或缺口措辞简短说明。"
        )
    if issue.rule_code == "C2" and "候选 facet" in message:
        return "将候选 facet 改写为候选/未断言信息，不得使用 是/为/属于/定位为/可判定为 等断言动词。"
    if issue.rule_code == "L1" or _audit_issue_id_prefix(issue.issue_id) == _PROGRAMMATIC_L1_PREFIX:
        return (
            "修复模板第2章 R=A+B-C 数字闭环：公式/百分比闭合断言必须在同一句或上下2行内放入"
            " allowed anchor marker；若没有同源事实支撑 R、A、B、C 或 A-C 数值关系，删除具体数值闭合断言，"
            "改写为未披露/数据不足/下一步最小验证问题；同时检查 ### 结论要点 与 ### 证据与出处，"
            "不得在这些段落无锚点复述 R/A/B/C/A-C 具体百分比；不得编造 Alpha、Beta、Cost 或 R 数值。"
        )
    if issue.rule_code == "E1" or "anchor" in message.lower() or "锚点" in message:
        return "只使用 allowed anchor marker，删除未知 anchor 或改用 allowed anchor。"
    if issue.issue_id == "llm:parse_failure":
        return (
            "按 auditor 原始行协议修复：无问题时只能输出一行 PASS|chapter|no issues；"
            "有问题时每行只能以 BLOCKING、REVIEWABLE 或 INFO 开头并恰好三段，"
            "禁止 SEVERITY 占位词、解释性前缀、Markdown、JSON、标题、总结句或额外 `|`。"
        )
    return _sanitize_text(message)


def _mentions_structure(message: str, location: str) -> bool:
    """判断 issue 是否命中固定结构段落。

    Args:
        message: issue 消息。
        location: issue 位置。

    Returns:
        命中结构段落时返回 `True`。

    Raises:
        无显式抛出。
    """

    text = f"{message} {location}"
    return any(item in text for item in ("结论要点", "详细情况", "证据与出处", "结构段落"))


def _mentions_required_output(message: str, location: str) -> bool:
    """判断 issue 是否命中 required output。

    Args:
        message: issue 消息。
        location: issue 位置。

    Returns:
        命中 required output 时返回 `True`。

    Raises:
        无显式抛出。
    """

    text = f"{message} {location}".lower()
    return "required output" in text or "required_output" in text


def _sanitize_text(text: str, *, max_chars: int = _MAX_REPAIR_MESSAGE_CHARS) -> str:
    """清理可能含敏感信息或过长上下文的文本。

    Args:
        text: 原始文本。
        max_chars: 最大字符数。

    Returns:
        单行、安全、限长文本。

    Raises:
        无显式抛出。
    """

    redacted = " ".join(text.replace("\r", " ").replace("\n", " ").split())
    for sensitive in ("Authorization", "Bearer", "FUND_AGENT_LLM_API_KEY", "api_key", "sk-", "prompt"):
        redacted = redacted.replace(sensitive, "[redacted]")
    if len(redacted) <= max_chars:
        return redacted
    return redacted[:max_chars].rstrip() + "..."


def _map_writer_stop_reason(
    stop_reason: ChapterWriteStopReason,
) -> tuple[ChapterRunStatus, ChapterRunStopReason]:
    """映射 Gate 2 writer stop reason 到 Service 运行状态。

    Args:
        stop_reason: Gate 2 writer 停止原因。

    Returns:
        `(run_status, run_stop_reason)` 二元组。

    Raises:
        ValueError: 当 stop reason 不在 Gate 3 接受表内时抛出。
    """

    mapping = _WRITER_STOP_REASON_MAPPING.get(stop_reason)
    if mapping is None:
        raise ValueError(f"未接受的 writer stop reason：{stop_reason}")
    return mapping


def _status_from_audit_stop(
    decision: ChapterRepairDecision,
    audit_result: ChapterAuditResult,
) -> ChapterRunStatus:
    """根据审计停止状态推导单章状态。

    Args:
        decision: repair 决策。
        audit_result: Gate 2 审计结果。

    Returns:
        单章状态。

    Raises:
        无显式抛出。
    """

    if decision.action == "needs_more_facts":
        return "blocked"
    if audit_result.status == "blocked":
        return "blocked"
    return "failed"


def _stop_reason_from_repair_decision(
    decision: ChapterRepairDecision,
) -> ChapterRunStopReason:
    """根据 repair 决策推导最终停止原因。

    Args:
        decision: repair 决策。

    Returns:
        Service 层停止原因。

    Raises:
        ValueError: 当非停止决策被用于生成最终停止原因时抛出。
    """

    if decision.stop_reason == "none":
        raise ValueError("非停止 repair 决策不能生成最终 stop reason")
    return decision.stop_reason


def _accepted_conclusion(
    draft: ChapterDraft,
    audit_result: ChapterAuditResult,
) -> AcceptedChapterConclusion:
    """从 accepted draft 抽取 Gate 4 可消费结论。

    Args:
        draft: 已通过审计的章节草稿。
        audit_result: 已通过的审计结果。

    Returns:
        已接受章节结论摘要。

    Raises:
        无显式抛出。
    """

    text, source = _extract_conclusion_text(draft.markdown)
    capped_text, truncated = _cap_conclusion(text)
    return AcceptedChapterConclusion(
        chapter_id=draft.chapter_id,
        title=draft.title,
        conclusion_markdown=capped_text,
        conclusion_truncated=truncated,
        conclusion_source=source,
        used_fact_ids=draft.used_fact_ids,
        used_anchor_ids=draft.used_anchor_ids,
        declared_missing_reasons=draft.declared_missing_reasons,
        audit_checked_rules=audit_result.programmatic.checked_rules,
    )


def _extract_conclusion_text(markdown: str) -> tuple[str, AcceptedChapterConclusionSource]:
    """确定性抽取“结论要点”段落。

    Args:
        markdown: 已通过审计的章节 Markdown。

    Returns:
        `(结论文本, 来源类型)`。

    Raises:
        无显式抛出。
    """

    lines = markdown.splitlines()
    for heading in _CONCLUSION_HEADINGS:
        extracted = _extract_heading_block(lines, heading)
        if extracted is not None:
            return extracted, "heading"
    fallback_lines = tuple(line.strip() for line in lines if line.strip())[:3]
    return "\n".join(fallback_lines), "fallback_lines"


def _extract_heading_block(lines: list[str], heading: str) -> str | None:
    """抽取指定 heading 到下一个同级或更高级 heading 前的内容。

    Args:
        lines: Markdown 行列表。
        heading: 目标 heading。

    Returns:
        抽取到的文本；未找到 heading 时返回 `None`。

    Raises:
        无显式抛出。
    """

    for index, line in enumerate(lines):
        if line.strip() != heading:
            continue
        body: list[str] = []
        for next_line in lines[index + 1 :]:
            stripped = next_line.strip()
            if heading.startswith("###") and (stripped.startswith("### ") or stripped.startswith("## ")):
                break
            if heading.startswith("##") and stripped.startswith("## "):
                break
            body.append(next_line)
        return "\n".join(body).strip()
    return None


def _cap_conclusion(text: str) -> tuple[str, bool]:
    """对 accepted conclusion 应用 500 字符硬上限。

    Args:
        text: 原始结论文本。

    Returns:
        `(截断后文本, 是否截断)`。

    Raises:
        无显式抛出。
    """

    if len(text) <= MAX_ACCEPTED_CONCLUSION_CHARS:
        return text, False
    return text[:MAX_ACCEPTED_CONCLUSION_CHARS], True


def _orchestration_result(
    input_data: ChapterOrchestrationInput,
    projection: ChapterFactProjection,
    chapter_results: tuple[ChapterRunResult, ...],
    skipped_chapter_ids: tuple[int, ...],
) -> ChapterOrchestrationResult:
    """汇总单章结果为总编排结果。

    Args:
        input_data: 章节编排输入。
        projection: Gate 1 投影。
        chapter_results: 单章结果。
        skipped_chapter_ids: 真实跳过章节；不得用于表示前序正文章节失败。

    Returns:
        总编排结果。

    Raises:
        无显式抛出。
    """

    accepted_conclusions = tuple(
        result.accepted_conclusion
        for result in chapter_results
        if result.accepted_conclusion is not None
    )
    generated_chapter_ids = tuple(result.chapter_id for result in chapter_results if result.status != "skipped")
    blocked_reasons = tuple(issue for result in chapter_results for issue in result.issues)
    if len(accepted_conclusions) == len(input_data.policy.target_chapter_ids):
        status: ChapterOrchestrationStatus = "accepted"
    elif accepted_conclusions:
        status = "partial"
    else:
        status = "blocked"
    return ChapterOrchestrationResult(
        status=status,
        fund_code=input_data.fund_code,
        report_year=input_data.report_year,
        projection=projection,
        chapter_results=chapter_results,
        accepted_conclusions=accepted_conclusions,
        blocked_reasons=blocked_reasons,
        generated_chapter_ids=generated_chapter_ids,
        skipped_chapter_ids=skipped_chapter_ids,
    )


def _first_failed_diagnostic(orchestration_result: ChapterOrchestrationResult) -> dict[str, object] | None:
    """读取首个未 accepted 章节的脱敏诊断摘要。

    Args:
        orchestration_result: 章节编排结果。

    Returns:
        首个失败章节摘要；没有失败章节时返回 `None`。

    Raises:
        无显式抛出。
    """

    for result in orchestration_result.chapter_results:
        if result.status == "accepted":
            continue
        diagnostic = result.prompt_contract_diagnostics[0] if result.prompt_contract_diagnostics else None
        return {
            "chapter_id": result.chapter_id,
            "phase": diagnostic.phase if diagnostic is not None else None,
            "attempt_index": diagnostic.attempt_index if diagnostic is not None else None,
            "category": result.failure_category,
            "subcategory": result.failure_subcategory,
        }
    return None


def _first_failed_runtime_diagnostic(
    orchestration_result: ChapterOrchestrationResult,
) -> dict[str, object] | None:
    """读取首个未 accepted 章节的 runtime 安全摘要。

    Args:
        orchestration_result: 章节编排结果。

    Returns:
        首个失败章节 runtime 摘要；没有失败章节时返回 `None`。

    Raises:
        无显式抛出。
    """

    for result in orchestration_result.chapter_results:
        if result.status == "accepted":
            continue
        diagnostics = _runtime_diagnostics_for_run(result)
        terminal_diagnostic = _terminal_runtime_diagnostic(result, diagnostics)
        representative_diagnostics = _representative_runtime_diagnostics(
            result,
            diagnostics,
            terminal_diagnostic,
        )
        return {
            "chapter_id": result.chapter_id,
            "status": result.status,
            "stop_reason": result.stop_reason,
            "category": result.failure_category,
            "subcategory": result.failure_subcategory,
            "diagnostic_consistency_status": _diagnostic_consistency_status(
                result,
                diagnostics,
                terminal_diagnostic,
            ),
            "terminal_runtime_diagnostic_present": terminal_diagnostic is not None,
            "terminal_stop_reason": result.stop_reason,
            "terminal_failure_category": result.failure_category,
            "terminal_runtime_operation": terminal_diagnostic.operation
            if terminal_diagnostic is not None
            else None,
            "terminal_repair_attempt_index": terminal_diagnostic.repair_attempt_index
            if terminal_diagnostic is not None
            else None,
            "terminal_issue_class": _terminal_issue_class(result),
            "runtime_operation": _first_runtime_operation(representative_diagnostics),
            "repair_attempt_index": _first_repair_attempt_index(
                representative_diagnostics
            ),
            "provider_attempt_count": _provider_attempt_count(representative_diagnostics),
            "provider_max_attempts": _provider_max_attempts(representative_diagnostics),
            "provider_runtime_categories": _provider_runtime_categories(
                representative_diagnostics
            ),
            "timeout_seconds": _max_optional_float(
                diagnostic.timeout_seconds for diagnostic in representative_diagnostics
            ),
            "timeout_max_attempts": _max_optional_int(
                diagnostic.timeout_max_attempts
                for diagnostic in representative_diagnostics
            ),
            "timeout_backoff_seconds": _max_optional_float(
                diagnostic.timeout_backoff_seconds
                for diagnostic in representative_diagnostics
            ),
            "timeout_budget_kind": _first_timeout_budget_kind(
                representative_diagnostics
            ),
            "timeout_root_cause_hint": _first_timeout_root_cause_hint(
                representative_diagnostics
            ),
            "system_prompt_chars": _max_optional_int(
                diagnostic.system_prompt_chars
                for diagnostic in representative_diagnostics
            ),
            "user_prompt_chars": _max_optional_int(
                diagnostic.user_prompt_chars for diagnostic in representative_diagnostics
            ),
            "approx_prompt_tokens": _max_optional_int(
                diagnostic.approx_prompt_tokens
                for diagnostic in representative_diagnostics
            ),
            "allowed_fact_count": _max_optional_int(
                diagnostic.allowed_fact_count
                for diagnostic in representative_diagnostics
            ),
            "allowed_anchor_count": _max_optional_int(
                diagnostic.allowed_anchor_count
                for diagnostic in representative_diagnostics
            ),
            "max_output_chars": _max_optional_int(
                diagnostic.max_output_chars for diagnostic in representative_diagnostics
            ),
        }
    return None


def _chapter_diagnostic_row(result: ChapterRunResult) -> dict[str, object]:
    """构造单章脱敏诊断行。

    Args:
        result: 单章编排结果。

    Returns:
        不含 prompt/draft/raw response 的章节诊断行。

    Raises:
        无显式抛出。
    """

    return {
        "chapter_id": result.chapter_id,
        "status": result.status,
        "stop_reason": result.stop_reason,
        "failure_category": result.failure_category,
        "failure_subcategory": result.failure_subcategory,
        "attempt_count": len(result.attempts),
        "phases": tuple(
            _prompt_contract_diagnostic_payload(diagnostic)
            for diagnostic in result.prompt_contract_diagnostics
        ),
    }


def _chapter_runtime_diagnostic_row(result: ChapterRunResult) -> dict[str, object]:
    """构造单章 runtime 诊断行。

    Args:
        result: 单章编排结果。

    Returns:
        只含 allowlisted scalar 的 runtime 诊断行。

    Raises:
        无显式抛出。
    """

    diagnostics = _runtime_diagnostics_for_run(result)
    terminal_diagnostic = _terminal_runtime_diagnostic(result, diagnostics)
    return {
        "chapter_id": result.chapter_id,
        "status": result.status,
        "stop_reason": result.stop_reason,
        "failure_category": result.failure_category,
        "failure_subcategory": result.failure_subcategory,
        "attempt_count": len(result.attempts),
        "diagnostic_consistency_status": _diagnostic_consistency_status(
            result,
            diagnostics,
            terminal_diagnostic,
        ),
        "terminal_runtime_diagnostic_present": terminal_diagnostic is not None,
        "terminal_stop_reason": result.stop_reason,
        "terminal_failure_category": result.failure_category,
        "terminal_runtime_operation": terminal_diagnostic.operation
        if terminal_diagnostic is not None
        else None,
        "terminal_repair_attempt_index": terminal_diagnostic.repair_attempt_index
        if terminal_diagnostic is not None
        else None,
        "terminal_issue_class": _terminal_issue_class(result),
        "runtime_diagnostics": tuple(
            _runtime_diagnostic_payload(diagnostic) for diagnostic in diagnostics
        ),
    }


def _runtime_diagnostics_for_run(
    result: ChapterRunResult,
) -> tuple[ChapterLLMRuntimeDiagnostic, ...]:
    """按章节级、attempt 级顺序收集 runtime 诊断。

    Args:
        result: 单章编排结果。

    Returns:
        章节级和 attempt 级 runtime 诊断。

    Raises:
        无显式抛出。
    """

    return (
        *result.runtime_diagnostics,
        *(diagnostic for attempt in result.attempts for diagnostic in attempt.runtime_diagnostics),
    )


def runtime_diagnostic_consistency_payload(
    result: ChapterRunResult,
    diagnostics: tuple[ChapterLLMRuntimeDiagnostic, ...] | None = None,
) -> dict[str, object]:
    """构造单章 terminal runtime lineage 安全摘要。

    Args:
        result: 单章编排结果。
        diagnostics: 可选 runtime 诊断序列；缺省时从 result 收集。

    Returns:
        只含 allowlisted scalar 的 terminal consistency payload。

    Raises:
        无显式抛出。
    """

    collected = diagnostics if diagnostics is not None else _runtime_diagnostics_for_run(result)
    terminal_diagnostic = _terminal_runtime_diagnostic(result, collected)
    return {
        "diagnostic_consistency_status": _diagnostic_consistency_status(
            result,
            collected,
            terminal_diagnostic,
        ),
        "terminal_runtime_diagnostic_present": terminal_diagnostic is not None,
        "terminal_stop_reason": result.stop_reason,
        "terminal_failure_category": result.failure_category,
        "terminal_runtime_operation": terminal_diagnostic.operation
        if terminal_diagnostic is not None
        else None,
        "terminal_repair_attempt_index": terminal_diagnostic.repair_attempt_index
        if terminal_diagnostic is not None
        else None,
        "terminal_issue_class": _terminal_issue_class(result),
    }


def attempt_runtime_diagnostic_consistency_payload(
    result: ChapterRunResult,
    attempt: ChapterAttemptRecord,
) -> dict[str, object]:
    """构造 attempt-level terminal runtime lineage 安全摘要。

    Args:
        result: 单章编排结果。
        attempt: 单次 write/audit attempt 记录。

    Returns:
        只含 allowlisted scalar 的 attempt terminal consistency payload。

    Raises:
        无显式抛出。
    """

    diagnostics = attempt.runtime_diagnostics
    terminal_diagnostic = _terminal_runtime_diagnostic(result, diagnostics)
    return {
        "diagnostic_consistency_status": _diagnostic_consistency_status(
            result,
            diagnostics,
            terminal_diagnostic,
        ),
        "terminal_runtime_diagnostic_present": terminal_diagnostic is not None,
        "terminal_stop_reason": result.stop_reason,
        "terminal_failure_category": result.failure_category,
        "terminal_runtime_operation": terminal_diagnostic.operation
        if terminal_diagnostic is not None
        else None,
        "terminal_repair_attempt_index": terminal_diagnostic.repair_attempt_index
        if terminal_diagnostic is not None
        else None,
        "terminal_issue_class": _terminal_issue_class(result),
    }


def _terminal_runtime_diagnostic(
    result: ChapterRunResult,
    diagnostics: tuple[ChapterLLMRuntimeDiagnostic, ...],
) -> ChapterLLMRuntimeDiagnostic | None:
    """按终态 stop reason 匹配 terminal runtime diagnostic。

    Args:
        result: 单章编排结果。
        diagnostics: runtime 诊断序列。

    Returns:
        匹配终态的 runtime diagnostic；没有匹配时返回 `None`。

    Raises:
        无显式抛出。
    """

    if result.stop_reason not in _RUNTIME_TERMINAL_STOP_REASONS:
        return None
    if result.stop_reason == "llm_timeout":
        for diagnostic in diagnostics:
            if _is_timeout_runtime_diagnostic(diagnostic):
                return diagnostic
        return None
    expected_category = _RUNTIME_STOP_REASON_CATEGORY.get(result.stop_reason)
    if expected_category is None:
        for diagnostic in diagnostics:
            if diagnostic.provider_runtime_category is not None:
                return diagnostic
        return None
    for diagnostic in diagnostics:
        if diagnostic.provider_runtime_category == expected_category:
            return diagnostic
    return None


def _representative_runtime_diagnostics(
    result: ChapterRunResult,
    diagnostics: tuple[ChapterLLMRuntimeDiagnostic, ...],
    terminal_diagnostic: ChapterLLMRuntimeDiagnostic | None,
) -> tuple[ChapterLLMRuntimeDiagnostic, ...]:
    """选择 first-failed 摘要使用的代表 runtime diagnostic 序列。

    Args:
        result: 单章编排结果。
        diagnostics: 全量 runtime 诊断序列。
        terminal_diagnostic: 已匹配的 terminal diagnostic。

    Returns:
        代表性 runtime 诊断序列。

    Raises:
        无显式抛出。
    """

    if terminal_diagnostic is None:
        if result.stop_reason in _RUNTIME_TERMINAL_STOP_REASONS:
            return ()
        return diagnostics
    return tuple(
        diagnostic
        for diagnostic in diagnostics
        if _diagnostic_matches_terminal(result, diagnostic, terminal_diagnostic)
    )


def _diagnostic_matches_terminal(
    result: ChapterRunResult,
    diagnostic: ChapterLLMRuntimeDiagnostic,
    terminal_diagnostic: ChapterLLMRuntimeDiagnostic,
) -> bool:
    """判断 diagnostic 是否属于同一个 terminal runtime failure。

    Args:
        result: 单章编排结果。
        diagnostic: 候选 runtime diagnostic。
        terminal_diagnostic: 已匹配的 terminal diagnostic。

    Returns:
        同一 terminal runtime failure 返回 `True`。

    Raises:
        无显式抛出。
    """

    if diagnostic.operation != terminal_diagnostic.operation:
        return False
    if diagnostic.repair_attempt_index != terminal_diagnostic.repair_attempt_index:
        return False
    if result.stop_reason == "llm_timeout":
        return _is_timeout_runtime_diagnostic(diagnostic)
    expected_category = _RUNTIME_STOP_REASON_CATEGORY.get(result.stop_reason)
    if expected_category is None:
        return diagnostic.provider_runtime_category is not None
    return diagnostic.provider_runtime_category == expected_category


def _diagnostic_consistency_status(
    result: ChapterRunResult,
    diagnostics: tuple[ChapterLLMRuntimeDiagnostic, ...],
    terminal_diagnostic: ChapterLLMRuntimeDiagnostic | None,
) -> DiagnosticConsistencyStatus:
    """计算 terminal diagnostic consistency 状态。

    Args:
        result: 单章编排结果。
        diagnostics: runtime 诊断序列。
        terminal_diagnostic: 已匹配的 terminal diagnostic。

    Returns:
        allowlisted consistency status。

    Raises:
        无显式抛出。
    """

    if result.stop_reason not in _RUNTIME_TERMINAL_STOP_REASONS:
        if _has_provider_runtime_scalar(diagnostics):
            return "non_runtime_terminal_without_scalar"
        return "consistent"
    if terminal_diagnostic is None:
        return "missing_terminal_runtime_diagnostic"
    expected_category = _RUNTIME_STOP_REASON_CATEGORY.get(result.stop_reason)
    if expected_category is not None and result.stop_reason != "llm_timeout":
        if terminal_diagnostic.provider_runtime_category != expected_category:
            return "terminal_category_conflict"
    if result.stop_reason == "llm_timeout" and not _is_timeout_runtime_diagnostic(
        terminal_diagnostic
    ):
        return "terminal_category_conflict"
    return "consistent"


def _is_timeout_runtime_diagnostic(diagnostic: ChapterLLMRuntimeDiagnostic) -> bool:
    """判断 runtime diagnostic 是否明确表示 provider timeout。

    Args:
        diagnostic: runtime 诊断。

    Returns:
        明确 timeout 返回 `True`。

    Raises:
        无显式抛出。
    """

    return (
        diagnostic.provider_runtime_category == "timeout"
        or diagnostic.timeout_budget_kind is not None
    )


def _has_provider_runtime_scalar(
    diagnostics: tuple[ChapterLLMRuntimeDiagnostic, ...],
) -> bool:
    """判断非 runtime terminal 是否意外携带 provider runtime scalar。

    Args:
        diagnostics: runtime 诊断序列。

    Returns:
        存在 provider runtime scalar 返回 `True`。

    Raises:
        无显式抛出。
    """

    return any(
        diagnostic.provider_runtime_category is not None
        or diagnostic.provider_attempt_index is not None
        or diagnostic.timeout_budget_kind is not None
        for diagnostic in diagnostics
    )


def _terminal_issue_class(result: ChapterRunResult) -> str | None:
    """提取安全 terminal issue class。

    Args:
        result: 单章编排结果。

    Returns:
        异常类型或 issue id prefix；缺失时返回 `None`。

    Raises:
        无显式抛出。
    """

    for diagnostic in result.runtime_diagnostics:
        if diagnostic.error_type:
            return diagnostic.error_type
    for attempt in result.attempts:
        for diagnostic in attempt.runtime_diagnostics:
            if diagnostic.error_type:
                return diagnostic.error_type
    if result.stop_reason in _RUNTIME_TERMINAL_STOP_REASONS:
        for issue in result.issues:
            issue_text = str(issue)
            if "LLMProviderTimeoutError" in issue_text:
                return "LLMProviderTimeoutError"
            if "LLMProviderRateLimitError" in issue_text:
                return "LLMProviderRateLimitError"
            if "LLMProviderMalformedResponseError" in issue_text:
                return "LLMProviderMalformedResponseError"
            if "LLMProviderNetworkError" in issue_text:
                return "LLMProviderNetworkError"
    return _first_safe_issue_prefix(result.issues)


def _first_safe_issue_prefix(issues: tuple[str, ...]) -> str | None:
    """提取首个安全 issue prefix。

    Args:
        issues: issue 文本序列。

    Returns:
        安全 issue prefix；没有时返回 `None`。

    Raises:
        无显式抛出。
    """

    for issue in issues:
        raw_prefix = str(issue).split(":", 2)
        if len(raw_prefix) >= 2:
            prefix = f"{raw_prefix[0]}:{raw_prefix[1]}"
        else:
            continue
        safe = "".join(
            ch for ch in prefix if ch.isascii() and (ch.isalnum() or ch in "_:-")
        )
        if not safe.startswith(("writer:", "programmatic:", "llm:", "audit:")):
            continue
        if safe:
            return safe[:80]
    return None


def _safe_status_code(status_code: int | None) -> int | None:
    """过滤非标准 HTTP 状态码。

    Args:
        status_code: provider 诊断中的状态码。

    Returns:
        标准 HTTP 状态码整数；其他值返回 `None`。

    Raises:
        无显式抛出。
    """

    if isinstance(status_code, bool) or not isinstance(status_code, int):
        return None
    if 100 <= status_code <= 599:
        return status_code
    return None


def _runtime_diagnostic_payload(
    diagnostic: ChapterLLMRuntimeDiagnostic,
) -> dict[str, object]:
    """把 runtime 诊断转为 allowlisted scalar payload。

    Args:
        diagnostic: Service 层 runtime 诊断。

    Returns:
        不含 message、model_name、prompt、draft、raw response 的 payload。

    Raises:
        无显式抛出。
    """

    return {
        "operation": diagnostic.operation,
        "repair_attempt_index": diagnostic.repair_attempt_index,
        "provider_attempt_index": diagnostic.provider_attempt_index,
        "provider_max_attempts": diagnostic.provider_max_attempts,
        "provider_runtime_category": diagnostic.provider_runtime_category,
        "chapter_failure_category": diagnostic.chapter_failure_category,
        "elapsed_ms": diagnostic.elapsed_ms,
        "status_code": _safe_status_code(diagnostic.status_code),
        "request_id": diagnostic.request_id,
        "finish_reason": diagnostic.finish_reason,
        "response_chars": diagnostic.response_chars,
        "error_type": diagnostic.error_type,
        "system_prompt_chars": diagnostic.system_prompt_chars,
        "user_prompt_chars": diagnostic.user_prompt_chars,
        "approx_prompt_tokens": diagnostic.approx_prompt_tokens,
        "allowed_fact_count": diagnostic.allowed_fact_count,
        "allowed_anchor_count": diagnostic.allowed_anchor_count,
        "max_output_chars": diagnostic.max_output_chars,
        "timeout_seconds": diagnostic.timeout_seconds,
        "timeout_max_attempts": diagnostic.timeout_max_attempts,
        "timeout_backoff_seconds": diagnostic.timeout_backoff_seconds,
        "timeout_budget_kind": diagnostic.timeout_budget_kind,
        "repair_timeout_fallback_used": diagnostic.repair_timeout_fallback_used,
        "timeout_root_cause_hint": _timeout_root_cause_hint(diagnostic),
        "prompt_cost_diagnostic": _prompt_cost_diagnostic_payload(
            diagnostic.prompt_cost_diagnostic
        ),
    }


def _first_runtime_operation(
    diagnostics: tuple[ChapterLLMRuntimeDiagnostic, ...],
) -> str | None:
    """读取首条 runtime diagnostic 的 operation。

    Args:
        diagnostics: runtime 诊断序列。

    Returns:
        operation 或 `None`。

    Raises:
        无显式抛出。
    """

    if not diagnostics:
        return None
    return diagnostics[0].operation


def _first_timeout_budget_kind(
    diagnostics: tuple[ChapterLLMRuntimeDiagnostic, ...],
) -> str | None:
    """读取首个 timeout budget kind。

    Args:
        diagnostics: runtime 诊断序列。

    Returns:
        budget kind 或 `None`。

    Raises:
        无显式抛出。
    """

    for diagnostic in diagnostics:
        if diagnostic.timeout_budget_kind is not None:
            return diagnostic.timeout_budget_kind
    return None


def _first_timeout_root_cause_hint(
    diagnostics: tuple[ChapterLLMRuntimeDiagnostic, ...],
) -> str | None:
    """读取首个 timeout root-cause hint。

    Args:
        diagnostics: runtime 诊断序列。

    Returns:
        root-cause hint 或 `None`。

    Raises:
        无显式抛出。
    """

    for diagnostic in diagnostics:
        hint = _timeout_root_cause_hint(diagnostic)
        if hint is not None:
            return hint
    return None


def _timeout_root_cause_hint(
    diagnostic: ChapterLLMRuntimeDiagnostic,
) -> TimeoutRootCauseHint | None:
    """按本 gate 阈值分类 provider timeout root-cause hint。

    Args:
        diagnostic: runtime 诊断。

    Returns:
        安全 root-cause hint。

    Raises:
        无显式抛出。
    """

    explicit_hint = diagnostic.timeout_root_cause_hint
    if explicit_hint in (
        "large_writer_prompt_cost",
        "small_prompt_provider_timeout",
        "provider_runtime_timeout_uncalibrated",
        "non_timeout_provider_runtime",
        "not_provider_runtime",
    ):
        return explicit_hint  # type: ignore[return-value]
    category = diagnostic.provider_runtime_category
    if category is None:
        return None
    if category != "timeout":
        return "non_timeout_provider_runtime"
    approx_tokens = diagnostic.approx_prompt_tokens
    if approx_tokens is None:
        return "provider_runtime_timeout_uncalibrated"
    if diagnostic.operation == "writer" and approx_tokens >= 8000:
        return "large_writer_prompt_cost"
    if approx_tokens <= 3000:
        return "small_prompt_provider_timeout"
    return "provider_runtime_timeout_uncalibrated"


def _first_repair_attempt_index(
    diagnostics: tuple[ChapterLLMRuntimeDiagnostic, ...],
) -> int | None:
    """读取首条 runtime diagnostic 的 repair attempt。

    Args:
        diagnostics: runtime 诊断序列。

    Returns:
        repair attempt index 或 `None`。

    Raises:
        无显式抛出。
    """

    if not diagnostics:
        return None
    return diagnostics[0].repair_attempt_index


def _provider_attempt_count(
    diagnostics: tuple[ChapterLLMRuntimeDiagnostic, ...],
) -> int:
    """统计 provider attempt 诊断条数。

    Args:
        diagnostics: runtime 诊断序列。

    Returns:
        带 provider attempt index 的诊断数量。

    Raises:
        无显式抛出。
    """

    return sum(1 for diagnostic in diagnostics if diagnostic.provider_attempt_index is not None)


def _provider_max_attempts(
    diagnostics: tuple[ChapterLLMRuntimeDiagnostic, ...],
) -> int | None:
    """读取 runtime 诊断中的最大 provider attempt budget。

    Args:
        diagnostics: runtime 诊断序列。

    Returns:
        最大 provider attempt budget；缺失时返回 `None`。

    Raises:
        无显式抛出。
    """

    values = tuple(
        diagnostic.provider_max_attempts
        for diagnostic in diagnostics
        if diagnostic.provider_max_attempts is not None
    )
    if not values:
        return None
    return max(values)


def _provider_runtime_categories(
    diagnostics: tuple[ChapterLLMRuntimeDiagnostic, ...],
) -> tuple[str, ...]:
    """汇总 runtime category，保留首次出现顺序。

    Args:
        diagnostics: runtime 诊断序列。

    Returns:
        去重后的 provider runtime category。

    Raises:
        无显式抛出。
    """

    categories: list[str] = []
    seen: set[str] = set()
    for diagnostic in diagnostics:
        category = diagnostic.provider_runtime_category
        if category is None or category in seen:
            continue
        categories.append(category)
        seen.add(category)
    return tuple(categories)


def _max_optional_int(values: object) -> int | None:
    """读取可选整型序列的最大值。

    Args:
        values: 可能包含 `None` 的整型 iterable。

    Returns:
        最大整型；全部缺失时返回 `None`。

    Raises:
        无显式抛出。
    """

    concrete_values = tuple(value for value in values if isinstance(value, int))
    if not concrete_values:
        return None
    return max(concrete_values)


def _max_optional_float(values: object) -> float | None:
    """读取可选数值序列的最大值。

    Args:
        values: 可能包含 `None` 的数值 iterable。

    Returns:
        最大数值；全部缺失时返回 `None`。

    Raises:
        无显式抛出。
    """

    concrete_values = tuple(value for value in values if isinstance(value, int | float))
    if not concrete_values:
        return None
    return float(max(concrete_values))


def _prompt_contract_diagnostic_payload(
    diagnostic: ChapterPromptContractDiagnostic,
) -> dict[str, object]:
    """把 prompt-contract 诊断转为安全 payload。

    Args:
        diagnostic: prompt-contract 诊断。

    Returns:
        只含标量与计数的 payload。

    Raises:
        无显式抛出。
    """

    return {
        "schema_version": diagnostic.schema_version,
        "chapter_id": diagnostic.chapter_id,
        "phase": diagnostic.phase,
        "attempt_index": diagnostic.attempt_index,
        "primary_subcategory": diagnostic.primary_subcategory,
        "issue_reason_counts": dict(diagnostic.issue_reason_counts),
        "issue_id_prefix_counts": dict(diagnostic.issue_id_prefix_counts),
        "required_structure_missing_count": diagnostic.required_structure_missing_count,
        "required_output_missing_count": diagnostic.required_output_missing_count,
        "unknown_anchor_count": diagnostic.unknown_anchor_count,
        "invalid_marker_count": diagnostic.invalid_marker_count,
        "forbidden_phrase_count": diagnostic.forbidden_phrase_count,
        "l1_numerical_closure_count": diagnostic.l1_numerical_closure_count,
        "candidate_facet_assertion_count": diagnostic.candidate_facet_assertion_count,
        "response_length_incomplete_count": diagnostic.response_length_incomplete_count,
        "response_chars": diagnostic.response_chars,
        "max_output_chars": diagnostic.max_output_chars,
        "finish_reason": diagnostic.finish_reason,
        "accepted_draft_present": diagnostic.accepted_draft_present,
    }


def _prompt_cost_diagnostic_payload(diagnostic: object | None) -> dict[str, object] | None:
    """把 writer prompt-cost 诊断转为 allowlisted payload。

    Args:
        diagnostic: writer prompt-cost 诊断；auditor 可为 `None`。

    Returns:
        只含 id、枚举和成本标量的 payload。

    Raises:
        无显式抛出。
    """

    if diagnostic is None:
        return None
    component_costs = getattr(diagnostic, "component_costs", None)
    return {
        "schema_version": getattr(diagnostic, "schema_version", None),
        "chapter_id": getattr(diagnostic, "chapter_id", None),
        "operation": getattr(diagnostic, "operation", None),
        "system_prompt_chars": getattr(diagnostic, "system_prompt_chars", None),
        "user_prompt_chars": getattr(diagnostic, "user_prompt_chars", None),
        "approx_prompt_tokens": getattr(diagnostic, "approx_prompt_tokens", None),
        "max_output_chars": getattr(diagnostic, "max_output_chars", None),
        "repair_attempt_index": getattr(diagnostic, "repair_attempt_index", None),
        "component_costs": _prompt_component_cost_payload(component_costs),
        "fact_cost_rows": tuple(
            _prompt_fact_cost_payload(row)
            for row in getattr(diagnostic, "fact_cost_rows", ())
        ),
        "anchor_cost_rows": tuple(
            _prompt_anchor_cost_payload(row)
            for row in getattr(diagnostic, "anchor_cost_rows", ())
        ),
    }


def _prompt_component_cost_payload(component_costs: object | None) -> dict[str, object] | None:
    """序列化 prompt component 成本。

    Args:
        component_costs: component cost dataclass。

    Returns:
        成本标量 payload。

    Raises:
        无显式抛出。
    """

    if component_costs is None:
        return None
    return {
        "protocol_chars": getattr(component_costs, "protocol_chars", None),
        "contract_chars": getattr(component_costs, "contract_chars", None),
        "must_answer_chars": getattr(component_costs, "must_answer_chars", None),
        "must_not_cover_chars": getattr(component_costs, "must_not_cover_chars", None),
        "required_output_chars": getattr(component_costs, "required_output_chars", None),
        "facts_chars": getattr(component_costs, "facts_chars", None),
        "anchors_chars": getattr(component_costs, "anchors_chars", None),
        "repair_context_chars": getattr(component_costs, "repair_context_chars", None),
    }


def _prompt_fact_cost_payload(row: object) -> dict[str, object]:
    """序列化 prompt fact cost 行。

    Args:
        row: fact cost dataclass。

    Returns:
        不含 fact value 文本的 payload。

    Raises:
        无显式抛出。
    """

    return {
        "fact_id": getattr(row, "fact_id", None),
        "source_field_id": getattr(row, "source_field_id", None),
        "status": getattr(row, "status", None),
        "missing_reason": getattr(row, "missing_reason", None),
        "value_chars": getattr(row, "value_chars", None),
        "serialized_fact_chars": getattr(row, "serialized_fact_chars", None),
        "evidence_anchor_count": getattr(row, "evidence_anchor_count", None),
        "required_by_count": getattr(row, "required_by_count", None),
    }


def _prompt_anchor_cost_payload(row: object) -> dict[str, object]:
    """序列化 prompt anchor cost 行。

    Args:
        row: anchor cost dataclass。

    Returns:
        不含 anchor note 文本的 payload。

    Raises:
        无显式抛出。
    """

    return {
        "anchor_id": getattr(row, "anchor_id", None),
        "source_kind": getattr(row, "source_kind", None),
        "document_year": getattr(row, "document_year", None),
        "section_id": getattr(row, "section_id", None),
        "table_id": getattr(row, "table_id", None),
        "row_locator_present": getattr(row, "row_locator_present", None),
        "serialized_anchor_chars": getattr(row, "serialized_anchor_chars", None),
    }


def _skipped_result(projection: ChapterFactProjection, chapter_id: int) -> ChapterRunResult:
    """构造真实 scope/dependency 跳过结果。

    Args:
        projection: Gate 1 投影。
        chapter_id: 模板章节编号。

    Returns:
        skipped 单章结果。

    Raises:
        ValueError: 当章节缺失时抛出。
    """

    return ChapterRunResult(
        chapter_id=chapter_id,
        title=_chapter_title(projection, chapter_id),
        status="skipped",
        stop_reason="dependency_missing",
        accepted_draft=None,
        accepted_conclusion=None,
        attempts=(),
        issues=("章节未进入本次可执行范围或被全局依赖阻断。",),
        failure_category="fact_gap",
    )


def _chapter_title(projection: ChapterFactProjection, chapter_id: int) -> str:
    """读取投影中的章节标题。

    Args:
        projection: Gate 1 投影。
        chapter_id: 模板章节编号。

    Returns:
        章节标题。

    Raises:
        ValueError: 当章节缺失或重复时抛出。
    """

    matches = tuple(chapter for chapter in projection.chapters if chapter.chapter_id == chapter_id)
    if len(matches) != 1:
        raise ValueError(f"章节输入必须唯一：chapter_id={chapter_id}, count={len(matches)}")
    return matches[0].title


def _writer_issue_messages(writer_result: ChapterWriteResult) -> tuple[str, ...]:
    """提取 writer issue 文本。

    Args:
        writer_result: Gate 2 writer 结果。

    Returns:
        issue 文本元组。

    Raises:
        无显式抛出。
    """

    return tuple(issue.message for issue in writer_result.issues)


def _audit_issue_messages(audit_result: ChapterAuditResult) -> tuple[str, ...]:
    """提取 auditor issue 文本。

    Args:
        audit_result: Gate 2 审计结果。

    Returns:
        issue 文本元组。

    Raises:
        无显式抛出。
    """

    return tuple(issue.message for issue in _all_audit_issues(audit_result))


def _audit_issue_ids(audit_result: ChapterAuditResult) -> tuple[str, ...]:
    """提取 auditor issue id。

    Args:
        audit_result: Gate 2 审计结果。

    Returns:
        issue id 元组；无 issue 时为空。

    Raises:
        无显式抛出。
    """

    return tuple(issue.issue_id for issue in _all_audit_issues(audit_result))


def _all_audit_issues(audit_result: ChapterAuditResult) -> tuple[ChapterAuditIssue, ...]:
    """读取 programmatic 与 LLM 审计 issue。

    Args:
        audit_result: Gate 2 审计结果。

    Returns:
        合并后的 issue 元组。

    Raises:
        无显式抛出。
    """

    return (*audit_result.programmatic.issues, *audit_result.llm.issues)


def _has_llm_unavailable_issue(audit_result: ChapterAuditResult) -> bool:
    """判断审计结果是否包含 LLM_UNAVAILABLE issue。

    Args:
        audit_result: Gate 2 审计结果。

    Returns:
        存在 LLM_UNAVAILABLE 时返回 `True`。

    Raises:
        无显式抛出。
    """

    return any(issue.rule_code == "LLM_UNAVAILABLE" for issue in audit_result.llm.issues)
