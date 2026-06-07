"""Agent 执行契约 dataclasses，见基金分析模板第 1-6 章。

本模块只定义 Agent 层执行状态、ToolTrace 安全信封、repair policy 和 body
readiness 契约。它可以引用 Fund 层 typed facts / availability，但不得导入
Service 或 Host；Host cancel/deadline 只能通过 `AgentSchedulerInterruption`
这种已归一化信号进入 Agent。
"""

from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Final, Literal, Mapping

from fund_agent.fund.chapter_facts import ChapterFactProjection
from fund_agent.fund.evidence_availability import EvidenceAvailability

AGENT_CONTRACTS_SCHEMA_VERSION: Final[str] = "agent_contracts.v1"

AgentReportRunStatus = Literal["prepared", "running", "accepted", "partial", "blocked"]
ChapterTaskStatus = Literal["prepared", "running", "accepted", "blocked", "failed", "skipped"]
AgentTerminalState = Literal[
    "accepted",
    "skipped_explicit_scope",
    "blocked_dependency_missing",
    "blocked_fund_identity_fact_gap",
    "blocked_fact_gap",
    "blocked_writer_precondition",
    "blocked_audit_failed",
    "blocked_audit_contract",
    "blocked_repair_budget_exhausted",
    "blocked_needs_more_facts",
    "blocked_provider_runtime",
    "blocked_prompt_contract",
    "blocked_internal_code_bug",
    "blocked_scheduler_interrupted",
]
AgentSchedulerInterruptionStatus = Literal["none", "cancelled", "deadline_exceeded"]
ToolCallStatus = Literal["succeeded", "blocked", "failed"]
ToolTraceSafeValue = str | int | float | bool | None

_FORBIDDEN_SAFE_METADATA_KEYS: Final[frozenset[str]] = frozenset(
    (
        "prompt",
        "system_prompt",
        "user_prompt",
        "draft",
        "draft_markdown",
        "fact_values",
        "raw_provider_response",
        "raw_audit_response",
        "raw_provider_request",
        "request_body",
        "api_key",
        "authorization",
        "bearer_token",
        "model",
        "model_name",
        "base_url",
        "headers",
        "provider_config",
    )
)


def _normalize_safe_metadata(
    metadata: Mapping[str, ToolTraceSafeValue] | None,
) -> Mapping[str, ToolTraceSafeValue]:
    """规范化 ToolTrace 安全 metadata。

    Args:
        metadata: 调用方提供的安全标量 metadata；为 `None` 时返回空映射。

    Returns:
        不可变的安全 metadata 映射。

    Raises:
        ValueError: 当 metadata key 命中不安全字段名时抛出。
    """

    if metadata is None:
        return MappingProxyType({})

    blocked_keys = tuple(
        key for key in metadata if key.lower() in _FORBIDDEN_SAFE_METADATA_KEYS
    )
    if blocked_keys:
        raise ValueError(f"ToolTrace metadata 包含不安全字段：{', '.join(blocked_keys)}")
    return MappingProxyType(dict(metadata))


@dataclass(frozen=True, slots=True, kw_only=True)
class AgentSchedulerInterruption:
    """Agent scheduler 已归一化中断信号。

    Args:
        status: 中断状态；`none` 表示没有中断。
        reason: 中断原因；`none` 状态必须为 `None`。
        phase: 中断发生的 Agent phase，如 `before_chapter` 或 `after_tool_call`。
        chapter_id: 中断关联章节；run-level 中断可为 `None`。
        attempt_index: 中断关联 attempt；非 attempt 阶段可为 `None`。

    Raises:
        ValueError: 当 `status` 与 `reason` 不一致时抛出。
    """

    status: AgentSchedulerInterruptionStatus
    reason: str | None
    phase: str
    chapter_id: int | None = None
    attempt_index: int | None = None

    def __post_init__(self) -> None:
        """校验中断状态与原因一致。

        Args:
            无。

        Returns:
            无返回值。

        Raises:
            ValueError: 当 `none` 带 reason 或中断状态缺 reason 时抛出。
        """

        if self.status == "none" and self.reason is not None:
            raise ValueError("AgentSchedulerInterruption status=none 不允许 reason")
        if self.status != "none" and not self.reason:
            raise ValueError("AgentSchedulerInterruption 中断状态必须提供 reason")


@dataclass(frozen=True, slots=True, kw_only=True)
class ToolCallRequest:
    """Agent 到 Fund primitive 的工具调用请求。

    Args:
        tool_name: 工具稳定名，如 `fund.write_chapter`。
        chapter_id: 关联章节编号；run-level 工具可为 `None`。
        attempt_index: 关联 attempt 序号。
        safe_metadata: 仅允许安全标量 metadata，不保存 prompt/fact/draft。

    Raises:
        ValueError: 当 `safe_metadata` 包含不安全字段名时抛出。
    """

    tool_name: str
    chapter_id: int | None
    attempt_index: int
    safe_metadata: Mapping[str, ToolTraceSafeValue] | None = None

    def __post_init__(self) -> None:
        """冻结并校验安全 metadata。

        Args:
            无。

        Returns:
            无返回值。

        Raises:
            ValueError: 当 `safe_metadata` 包含不安全字段名时抛出。
        """

        object.__setattr__(self, "safe_metadata", _normalize_safe_metadata(self.safe_metadata))


@dataclass(frozen=True, slots=True, kw_only=True)
class ToolCallResult:
    """Agent 工具调用结果信封。

    Args:
        status: 工具调用状态。
        terminal_state: 对应 Agent terminal；成功时可为 `accepted`。
        issue_ids: 安全 issue id 列表。
        safe_metadata: 仅允许安全标量 metadata。

    Raises:
        ValueError: 当 `safe_metadata` 包含不安全字段名时抛出。
    """

    status: ToolCallStatus
    terminal_state: AgentTerminalState
    issue_ids: tuple[str, ...] = ()
    safe_metadata: Mapping[str, ToolTraceSafeValue] | None = None

    def __post_init__(self) -> None:
        """冻结并校验安全 metadata。

        Args:
            无。

        Returns:
            无返回值。

        Raises:
            ValueError: 当 `safe_metadata` 包含不安全字段名时抛出。
        """

        object.__setattr__(self, "safe_metadata", _normalize_safe_metadata(self.safe_metadata))


@dataclass(frozen=True, slots=True, kw_only=True)
class ToolTrace:
    """ToolTrace 安全序列化信封。

    Args:
        request: 工具调用请求。
        result: 工具调用结果。
        elapsed_ms: 工具调用耗时毫秒。
        response_chars: 安全响应字符数；不得保存响应正文。
        request_id: 显式 response-header allowlist 得到的可选 request id。

    Raises:
        ValueError: 当耗时或字符数为负数时抛出。
    """

    request: ToolCallRequest
    result: ToolCallResult
    elapsed_ms: int
    response_chars: int | None = None
    request_id: str | None = None

    def __post_init__(self) -> None:
        """校验 trace 标量字段。

        Args:
            无。

        Returns:
            无返回值。

        Raises:
            ValueError: 当 `elapsed_ms` 或 `response_chars` 为负数时抛出。
        """

        if self.elapsed_ms < 0:
            raise ValueError("ToolTrace elapsed_ms 不能为负数")
        if self.response_chars is not None and self.response_chars < 0:
            raise ValueError("ToolTrace response_chars 不能为负数")

    def to_safe_dict(self) -> dict[str, object]:
        """输出 ToolTrace 安全序列化字典。

        Args:
            无。

        Returns:
            只包含工具名、章节、attempt、状态、terminal、issue id、耗时、字符数、
            request id 和安全 metadata 的字典。

        Raises:
            无。
        """

        return {
            "tool_name": self.request.tool_name,
            "chapter_id": self.request.chapter_id,
            "attempt_index": self.request.attempt_index,
            "status": self.result.status,
            "terminal_state": self.result.terminal_state,
            "issue_ids": self.result.issue_ids,
            "elapsed_ms": self.elapsed_ms,
            "response_chars": self.response_chars,
            "request_id": self.request_id,
            "request_metadata": dict(self.request.safe_metadata or {}),
            "result_metadata": dict(self.result.safe_metadata or {}),
        }


@dataclass(frozen=True, slots=True, kw_only=True)
class AgentRepairPolicy:
    """Agent 内容修复策略，见模板第 1-6 章。

    Args:
        max_content_repair_attempts: 内容修复最大次数。
        hidden_retry_allowed: 是否允许未记录 retry；当前必须为 `False`。

    Raises:
        ValueError: 当修复次数为负数或允许 hidden retry 时抛出。
    """

    max_content_repair_attempts: int
    hidden_retry_allowed: bool = False

    def __post_init__(self) -> None:
        """校验 repair policy 边界。

        Args:
            无。

        Returns:
            无返回值。

        Raises:
            ValueError: 当修复次数为负数或允许 hidden retry 时抛出。
        """

        if self.max_content_repair_attempts < 0:
            raise ValueError("max_content_repair_attempts 不能为负数")
        if self.hidden_retry_allowed:
            raise ValueError("Agent hidden retry 不允许开启")


@dataclass(frozen=True, slots=True, kw_only=True)
class ChapterAttempt:
    """Agent 单章 attempt 记录，见模板第 1-6 章。

    Args:
        attempt_index: 从 0 开始的 attempt 序号。
        tool_traces: 本次 attempt 产生的安全 ToolTrace。
        terminal_state: 本次 attempt 终态。
        writer_result: Fund writer typed 结果；未进入 writer 时为 `None`。
        audit_result: Fund audit typed 结果；writer blocked 或未进入 audit 时为 `None`。
        repair_decision: Agent repair 决策；未进入 repair decision 时为 `None`。

    Raises:
        ValueError: 当 attempt 序号为负数时抛出。
    """

    attempt_index: int
    tool_traces: tuple[ToolTrace, ...]
    terminal_state: AgentTerminalState
    writer_result: object | None = None
    audit_result: object | None = None
    repair_decision: object | None = None

    def __post_init__(self) -> None:
        """校验 attempt 序号。

        Args:
            无。

        Returns:
            无返回值。

        Raises:
            ValueError: 当 attempt 序号为负数时抛出。
        """

        if self.attempt_index < 0:
            raise ValueError("ChapterAttempt attempt_index 不能为负数")


@dataclass(frozen=True, slots=True, kw_only=True)
class AgentAcceptedChapterConclusion:
    """Agent 正文章节 accepted conclusion handoff，见模板第 1-6 章。

    Args:
        chapter_id: 模板章节编号。
        title: 章节标题。
        conclusion_markdown: 从 accepted draft 抽取的结论要点。
        conclusion_truncated: 结论是否被字符上限截断。
        conclusion_source: 结论来源。
        used_fact_ids: accepted draft 使用的 fact id。
        used_anchor_ids: accepted draft 使用的 anchor id。
        declared_missing_reasons: accepted draft 声明的缺口原因。
        audit_checked_rules: programmatic audit 检查过的规则码。

    Raises:
        ValueError: 当 chapter_id 不在第 1-6 章时抛出。
    """

    chapter_id: int
    title: str
    conclusion_markdown: str
    conclusion_truncated: bool
    conclusion_source: str
    used_fact_ids: tuple[str, ...]
    used_anchor_ids: tuple[str, ...]
    declared_missing_reasons: tuple[str, ...]
    audit_checked_rules: tuple[str, ...]

    def __post_init__(self) -> None:
        """校验 accepted conclusion 章节范围。

        Args:
            无。

        Returns:
            无返回值。

        Raises:
            ValueError: 当 chapter_id 不在 1-6 章时抛出。
        """

        if self.chapter_id not in range(1, 7):
            raise ValueError("Agent accepted conclusion 只覆盖模板第 1-6 章")


@dataclass(frozen=True, slots=True, kw_only=True)
class ChapterTask:
    """Agent 正文章节任务，见模板第 1-6 章。

    Args:
        chapter_id: 模板章节编号。
        title: 章节标题。
        status: 任务状态。
        terminal_state: Agent terminal state。
        attempts: attempt 记录。
        stop_reason: Agent runner 内部停止原因，供 Service bridge 投影；accepted 时为 `none`。
        accepted_draft: accepted 章节草稿；仅内存 handoff，不进入 ToolTrace。
        accepted_conclusion: accepted 章节结论 handoff。
        blocked_reasons: 安全阻断原因，必须可回溯到章节。
        failure_category: 当前失败分类；accepted 时为 `None`。
        failure_subcategory: prompt-contract 子类；无子类时为 `None`。
        exception: 工具调用异常对象；仅供 Service bridge 生成既有安全 diagnostics。
        exception_attempt_index: 异常发生的 attempt 序号。

    Raises:
        ValueError: 当 chapter_id 不在正文 1-6 章时抛出。
    """

    chapter_id: int
    title: str
    status: ChapterTaskStatus
    terminal_state: AgentTerminalState
    attempts: tuple[ChapterAttempt, ...] = ()
    stop_reason: str | None = None
    accepted_draft: object | None = None
    accepted_conclusion: AgentAcceptedChapterConclusion | None = None
    blocked_reasons: tuple[str, ...] = ()
    failure_category: str | None = None
    failure_subcategory: str | None = None
    exception: object | None = None
    exception_attempt_index: int | None = None

    def __post_init__(self) -> None:
        """校验正文 task 章节编号。

        Args:
            无。

        Returns:
            无返回值。

        Raises:
            ValueError: 当 chapter_id 不在 1-6 章时抛出。
        """

        if self.chapter_id not in range(1, 7):
            raise ValueError("Agent ChapterTask 只覆盖模板第 1-6 章")


@dataclass(frozen=True, slots=True, kw_only=True)
class FinalAssemblyReadiness:
    """Agent 正文章节 readiness handoff，见模板第 0/7 章。

    Args:
        ready: 正文章节是否满足 Service final assembly 前置条件。
        accepted_source_chapter_ids: 可作为 final assembly 来源的 accepted 正文章节。
        blocked_chapter_ids: 阻断章节。
        blocking_reasons: 安全阻断原因。

    Raises:
        ValueError: 当 accepted source chapter id 重复或与 blocked 交叉时抛出。
    """

    ready: bool
    accepted_source_chapter_ids: tuple[int, ...]
    blocked_chapter_ids: tuple[int, ...]
    blocking_reasons: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        """校验 readiness 章节集合。

        Args:
            无。

        Returns:
            无返回值。

        Raises:
            ValueError: 当 accepted source 重复或与 blocked 交叉时抛出。
        """

        if len(set(self.accepted_source_chapter_ids)) != len(self.accepted_source_chapter_ids):
            raise ValueError("accepted_source_chapter_ids 不允许重复")
        overlap = set(self.accepted_source_chapter_ids).intersection(self.blocked_chapter_ids)
        if overlap:
            raise ValueError(f"accepted 与 blocked 章节冲突：{sorted(overlap)}")


@dataclass(frozen=True, slots=True, kw_only=True)
class AgentReportRun:
    """Agent 单次报告执行记录，见模板第 1-6 章。

    Args:
        fund_code: 基金代码。
        report_year: 年报年份。
        status: Agent run 状态。
        projection: 同源章节事实投影。
        evidence_availability: run-level 证据可用性，仅派生一次后复用。
        repair_policy: 内容修复策略。
        tasks: 正文章节任务。
        final_assembly_readiness: 正文章节 readiness handoff。
        scheduler_interruption: 当前 normalized scheduler 中断。

    Raises:
        ValueError: 当身份与 `projection` 或 `evidence_availability` 不一致时抛出。
    """

    fund_code: str
    report_year: int
    status: AgentReportRunStatus
    projection: ChapterFactProjection
    evidence_availability: EvidenceAvailability
    repair_policy: AgentRepairPolicy
    tasks: tuple[ChapterTask, ...] = ()
    final_assembly_readiness: FinalAssemblyReadiness | None = None
    scheduler_interruption: AgentSchedulerInterruption | None = None
    schema_version: str = AGENT_CONTRACTS_SCHEMA_VERSION

    def __post_init__(self) -> None:
        """校验 Agent run 与同源 projection / availability 身份一致。

        Args:
            无。

        Returns:
            无返回值。

        Raises:
            ValueError: 当 fund_code 或 report_year 不一致时抛出。
        """

        if self.projection.fund_code != self.fund_code:
            raise ValueError("AgentReportRun fund_code 与 ChapterFactProjection 不一致")
        if self.projection.report_year != self.report_year:
            raise ValueError("AgentReportRun report_year 与 ChapterFactProjection 不一致")
        if self.evidence_availability.fund_code != self.fund_code:
            raise ValueError("AgentReportRun fund_code 与 EvidenceAvailability 不一致")
        if self.evidence_availability.report_year != self.report_year:
            raise ValueError("AgentReportRun report_year 与 EvidenceAvailability 不一致")
