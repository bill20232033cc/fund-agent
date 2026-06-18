"""Agent 工具适配层，见基金分析模板第 1-6 章。

本模块只把现有 Fund primitives 包成 Agent tool envelopes 和安全
`ToolTrace`。它不实现基金领域规则，不读取年报仓库，不构造 provider，
不导入 Service 或 Host，也不把 prompt、draft、raw response、fact value 或
provider config 写入 trace。
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Generic, TypeVar

from fund_agent.agent.contracts import (
    AgentTerminalState,
    ToolCallRequest,
    ToolCallResult,
    ToolTrace,
)
from fund_agent.fund.chapter_auditor import (
    ChapterAuditInput,
    ChapterAuditLLMClient,
    ChapterLLMAuditResult,
    ChapterProgrammaticAuditResult,
    audit_chapter_llm,
    audit_chapter_programmatic,
)
from fund_agent.fund.chapter_facts import (
    ChapterFactProjection,
    project_chapter_facts,
)
from fund_agent.fund.chapter_writer import (
    ChapterLLMClient,
    ChapterWriteResult,
    ChapterWriteStopReason,
    ChapterWriterInput,
    write_chapter,
)
from fund_agent.fund.data_extractor import StructuredFundDataBundle

T = TypeVar("T")

PROJECT_CHAPTER_FACTS_TOOL_NAME = "fund.project_chapter_facts"
WRITE_CHAPTER_TOOL_NAME = "fund.write_chapter"
AUDIT_CHAPTER_PROGRAMMATIC_TOOL_NAME = "fund.audit_chapter_programmatic"
AUDIT_CHAPTER_LLM_TOOL_NAME = "fund.audit_chapter_llm"
SUPPORTED_TOOL_NAMES: tuple[str, ...] = (
    PROJECT_CHAPTER_FACTS_TOOL_NAME,
    WRITE_CHAPTER_TOOL_NAME,
    AUDIT_CHAPTER_PROGRAMMATIC_TOOL_NAME,
    AUDIT_CHAPTER_LLM_TOOL_NAME,
)


@dataclass(frozen=True, slots=True, kw_only=True)
class AgentToolExecution(Generic[T]):
    """Agent 工具调用结果与安全 trace。

    Args:
        output: Fund primitive 的原始 typed 输出；调用异常时为 `None`。
        trace: 本次工具调用的安全 trace。
        exception: 工具调用异常；无异常时为 `None`。

    Raises:
        无显式抛出。
    """

    output: T | None
    trace: ToolTrace
    exception: Exception | None = None


def project_chapter_facts_tool(
    bundle: StructuredFundDataBundle,
    *,
    chapter_ids: tuple[int, ...],
    attempt_index: int = 0,
) -> AgentToolExecution[ChapterFactProjection]:
    """执行 Gate 1 章节事实投影工具。

    Args:
        bundle: 内存中的结构化基金数据包。
        chapter_ids: 请求投影的章节编号。
        attempt_index: run-level 工具 attempt 序号。

    Returns:
        章节事实投影及安全 ToolTrace。

    Raises:
        无显式抛出；异常写入 `AgentToolExecution.exception`。
    """

    started_at = time.perf_counter()
    request = ToolCallRequest(
        tool_name=PROJECT_CHAPTER_FACTS_TOOL_NAME,
        chapter_id=None,
        attempt_index=attempt_index,
        safe_metadata={
            "fund_code": bundle.fund_code,
            "report_year": bundle.report_year,
            "chapter_count": len(chapter_ids),
        },
    )
    try:
        projection = project_chapter_facts(bundle, chapter_ids=chapter_ids)
    except Exception as exc:  # pragma: no cover - covered through tests with fake bad input
        return _failed_execution(
            request,
            started_at=started_at,
            terminal_state="blocked_internal_code_bug",
            exception=exc,
        )
    result = ToolCallResult(
        status="succeeded",
        terminal_state="accepted",
        safe_metadata={
            "projected_chapter_count": len(projection.chapters),
            "fact_count": sum(len(chapter.facts) for chapter in projection.chapters),
            "anchor_count": sum(len(chapter.evidence_anchors) for chapter in projection.chapters),
        },
    )
    return AgentToolExecution(
        output=projection,
        trace=_trace(request, result, started_at=started_at),
    )


def write_chapter_tool(
    input_data: ChapterWriterInput,
    *,
    llm_client: ChapterLLMClient | None,
    attempt_index: int,
    request_id: str | None = None,
) -> AgentToolExecution[ChapterWriteResult]:
    """执行 Fund 章节写作工具。

    Args:
        input_data: Fund writer typed 输入。
        llm_client: Service 显式构造并传入的 writer client。
        attempt_index: Agent 章节 attempt 序号。
        request_id: 显式 allowlist 得到的可选请求 ID。

    Returns:
        写作结果及安全 ToolTrace。

    Raises:
        无显式抛出；异常写入 `AgentToolExecution.exception`。
    """

    started_at = time.perf_counter()
    request = ToolCallRequest(
        tool_name=WRITE_CHAPTER_TOOL_NAME,
        chapter_id=input_data.chapter.chapter_id,
        attempt_index=attempt_index,
        safe_metadata={
            "fund_code": input_data.fund_code,
            "report_year": input_data.report_year,
            "max_output_chars": input_data.max_output_chars,
            "repair_attempt_index": _repair_attempt_index(input_data),
        },
    )
    try:
        write_result = write_chapter(input_data, llm_client=llm_client)
    except Exception as exc:
        return _failed_execution(
            request,
            started_at=started_at,
            terminal_state=_terminal_from_exception(exc),
            exception=exc,
            request_id=request_id,
        )
    result = ToolCallResult(
        status="succeeded" if write_result.status == "drafted" else "blocked",
        terminal_state=_terminal_from_writer_stop_reason(write_result.stop_reason),
        issue_ids=tuple(issue.issue_id for issue in write_result.issues),
        safe_metadata=_writer_safe_metadata(write_result),
    )
    return AgentToolExecution(
        output=write_result,
        trace=_trace(
            request,
            result,
            started_at=started_at,
            response_chars=write_result.response_chars,
            request_id=request_id,
        ),
    )


def audit_chapter_programmatic_tool(
    input_data: ChapterAuditInput,
    *,
    attempt_index: int,
) -> AgentToolExecution[ChapterProgrammaticAuditResult]:
    """执行 Fund 程序审计工具。

    Args:
        input_data: Fund auditor typed 输入。
        attempt_index: Agent 章节 attempt 序号。

    Returns:
        程序审计结果及安全 ToolTrace。

    Raises:
        无显式抛出；异常写入 `AgentToolExecution.exception`。
    """

    started_at = time.perf_counter()
    request = ToolCallRequest(
        tool_name=AUDIT_CHAPTER_PROGRAMMATIC_TOOL_NAME,
        chapter_id=input_data.writer_input.chapter.chapter_id,
        attempt_index=attempt_index,
        safe_metadata={
            "fund_code": input_data.writer_input.fund_code,
            "report_year": input_data.writer_input.report_year,
            "run_programmatic": input_data.run_programmatic,
        },
    )
    try:
        audit_result = audit_chapter_programmatic(input_data)
    except Exception as exc:
        return _failed_execution(
            request,
            started_at=started_at,
            terminal_state="blocked_internal_code_bug",
            exception=exc,
        )
    result = ToolCallResult(
        status="succeeded" if audit_result.status == "pass" else "blocked",
        terminal_state="accepted" if audit_result.status == "pass" else "blocked_audit_failed",
        issue_ids=tuple(issue.issue_id for issue in audit_result.issues),
        safe_metadata={
            "audit_status": audit_result.status,
            "checked_rule_count": len(audit_result.checked_rules),
        },
    )
    return AgentToolExecution(
        output=audit_result,
        trace=_trace(request, result, started_at=started_at),
    )


def audit_chapter_llm_tool(
    input_data: ChapterAuditInput,
    *,
    llm_client: ChapterAuditLLMClient | None,
    attempt_index: int,
    request_id: str | None = None,
) -> AgentToolExecution[ChapterLLMAuditResult]:
    """执行 Fund bounded semantic LLM 审计工具。

    Args:
        input_data: Fund auditor typed 输入。
        llm_client: Service 显式构造并传入的 auditor client。
        attempt_index: Agent 章节 attempt 序号。
        request_id: 显式 allowlist 得到的可选请求 ID。

    Returns:
        LLM 审计结果及安全 ToolTrace。

    Raises:
        无显式抛出；异常写入 `AgentToolExecution.exception`。
    """

    started_at = time.perf_counter()
    request = ToolCallRequest(
        tool_name=AUDIT_CHAPTER_LLM_TOOL_NAME,
        chapter_id=input_data.writer_input.chapter.chapter_id,
        attempt_index=attempt_index,
        safe_metadata={
            "fund_code": input_data.writer_input.fund_code,
            "report_year": input_data.writer_input.report_year,
            "run_llm": input_data.run_llm,
        },
    )
    try:
        audit_result = audit_chapter_llm(input_data, llm_client=llm_client)
    except Exception as exc:
        return _failed_execution(
            request,
            started_at=started_at,
            terminal_state=_terminal_from_exception(exc),
            exception=exc,
            request_id=request_id,
        )
    result = ToolCallResult(
        status="succeeded" if audit_result.status == "pass" else "blocked",
        terminal_state=_terminal_from_llm_audit_status(audit_result.status),
        issue_ids=tuple(issue.issue_id for issue in audit_result.issues),
        safe_metadata={"audit_status": audit_result.status},
    )
    response_chars = len(audit_result.raw_response) if audit_result.raw_response is not None else None
    return AgentToolExecution(
        output=audit_result,
        trace=_trace(
            request,
            result,
            started_at=started_at,
            response_chars=response_chars,
            request_id=request_id,
        ),
    )


def _failed_execution(
    request: ToolCallRequest,
    *,
    started_at: float,
    terminal_state: AgentTerminalState,
    exception: Exception,
    request_id: str | None = None,
) -> AgentToolExecution[object]:
    """构造异常工具调用的安全结果。

    Args:
        request: 工具调用请求。
        started_at: `time.perf_counter()` 起点。
        terminal_state: Agent terminal state。
        exception: 捕获的异常。
        request_id: 显式 allowlist 得到的可选请求 ID。

    Returns:
        异常工具调用结果。

    Raises:
        无。
    """

    result = ToolCallResult(
        status="failed",
        terminal_state=terminal_state,
        issue_ids=(f"{request.tool_name}:exception",),
        safe_metadata={"error_type": type(exception).__name__},
    )
    return AgentToolExecution(
        output=None,
        trace=_trace(request, result, started_at=started_at, request_id=request_id),
        exception=exception,
    )


def _trace(
    request: ToolCallRequest,
    result: ToolCallResult,
    *,
    started_at: float,
    response_chars: int | None = None,
    request_id: str | None = None,
) -> ToolTrace:
    """构造安全 ToolTrace。

    Args:
        request: 工具调用请求。
        result: 工具调用结果。
        started_at: `time.perf_counter()` 起点。
        response_chars: 响应字符数标量。
        request_id: 显式 allowlist 得到的可选请求 ID。

    Returns:
        安全 ToolTrace。

    Raises:
        ValueError: 由 `ToolTrace` 字段校验抛出。
    """

    elapsed_ms = max(0, int((time.perf_counter() - started_at) * 1000))
    return ToolTrace(
        request=request,
        result=result,
        elapsed_ms=elapsed_ms,
        response_chars=response_chars,
        request_id=request_id,
    )


def _writer_safe_metadata(write_result: ChapterWriteResult) -> dict[str, int | str | None]:
    """抽取 writer 安全标量 metadata。

    Args:
        write_result: Fund writer 结果。

    Returns:
        不含 prompt/draft/raw response 的安全标量。

    Raises:
        无。
    """

    system_prompt_chars = len(write_result.prompt.system_prompt)
    user_prompt_chars = len(write_result.prompt.user_prompt)
    prompt_chars = system_prompt_chars + user_prompt_chars
    return {
        "writer_status": write_result.status,
        "stop_reason": write_result.stop_reason,
        "system_prompt_chars": system_prompt_chars,
        "user_prompt_chars": user_prompt_chars,
        "prompt_chars": prompt_chars,
        "approx_prompt_tokens": _approx_prompt_tokens(prompt_chars),
        "max_output_chars": write_result.max_output_chars,
        "finish_reason": write_result.finish_reason,
    }


def _approx_prompt_tokens(prompt_chars: int) -> int:
    """用本地字符数启发式估算 prompt token。

    Args:
        prompt_chars: prompt 字符数。

    Returns:
        估算 token 数。

    Raises:
        无。
    """

    return max(1, (prompt_chars + 3) // 4) if prompt_chars else 0


def _repair_attempt_index(input_data: ChapterWriterInput) -> int:
    """读取 writer repair attempt 序号。

    Args:
        input_data: writer typed 输入。

    Returns:
        repair attempt 序号；无 repair context 时为 `0`。

    Raises:
        无。
    """

    if input_data.repair_context is None:
        return 0
    return input_data.repair_context.attempt_index


def _terminal_from_writer_stop_reason(stop_reason: ChapterWriteStopReason) -> AgentTerminalState:
    """把 writer 停止原因映射到 Agent terminal。

    Args:
        stop_reason: Fund writer 停止原因。

    Returns:
        Agent terminal state。

    Raises:
        无。
    """

    if stop_reason == "none":
        return "accepted"
    if stop_reason in {
        "llm_contract_violation",
        "missing_required_structure",
        "missing_required_output_marker",
        "unknown_anchor",
        "response_too_long",
        "response_incomplete",
    }:
        return "blocked_prompt_contract"
    if stop_reason in {"llm_unavailable", "llm_empty_response"}:
        return "blocked_provider_runtime"
    if stop_reason == "fund_type_unknown":
        return "blocked_fund_identity_fact_gap"
    if stop_reason in {
        "missing_required_facts",
        "evidence_anchor_missing",
        "item_rule_deleted_required_content",
    }:
        return "blocked_fact_gap"
    if stop_reason == "chapter_requires_accepted_conclusions":
        return "blocked_dependency_missing"
    return "blocked_writer_precondition"


def _terminal_from_llm_audit_status(status: str) -> AgentTerminalState:
    """把 LLM 审计状态映射到 Agent terminal。

    Args:
        status: LLM 审计状态。

    Returns:
        Agent terminal state。

    Raises:
        无。
    """

    if status == "pass":
        return "accepted"
    if status == "blocked":
        return "blocked_audit_contract"
    return "blocked_audit_failed"


def _terminal_from_exception(exc: Exception) -> AgentTerminalState:
    """按异常类型映射工具失败 terminal。

    Args:
        exc: 捕获到的异常。

    Returns:
        provider runtime 异常返回 `blocked_provider_runtime`，未知异常返回
        `blocked_internal_code_bug`。

    Raises:
        无。
    """

    if type(exc).__name__ in {
        "LLMProviderTimeoutError",
        "LLMProviderRateLimitError",
        "LLMProviderMalformedResponseError",
        "LLMProviderNetworkError",
        "LLMProviderRuntimeError",
    }:
        return "blocked_provider_runtime"
    return "blocked_internal_code_bug"
