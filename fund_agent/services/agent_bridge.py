"""Service 到 Agent runner 的桥接层，见基金分析模板第 1-6 章。

Service 仍拥有用例、provider 构造、ExecutionContract 与最终装配语义。本模块
只把当前 Service 章节编排输入映射到 Agent body runner，再把 Agent body
readiness 和 accepted conclusions 投影回现有 Service 结果类型。
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from fund_agent.agent import (
    AgentLLMClients,
    AgentRepairPolicy,
    AgentRunPolicy,
    AgentSchedulerInterruption,
    ChapterAttempt,
    ChapterTask,
    run_agent_body_chapters,
)
from fund_agent.fund.chapter_auditor import ChapterAuditResult
from fund_agent.fund.chapter_facts import ChapterFactProjection
from fund_agent.fund.chapter_writer import ChapterWriteResult
from fund_agent.host import HostRunContext

if TYPE_CHECKING:
    from fund_agent.services.chapter_orchestrator import (
        ChapterOrchestrationInput,
        ChapterOrchestrationResult,
        ChapterOrchestratorLLMClients,
    )


def run_agent_chapter_orchestration_bridge(
    input_data: ChapterOrchestrationInput,
    *,
    projection: ChapterFactProjection,
    llm_clients: ChapterOrchestratorLLMClients,
    host_context: HostRunContext | None = None,
) -> ChapterOrchestrationResult:
    """通过 Agent runner 执行正文章节并投影为 Service 编排结果。

    Args:
        input_data: Service 章节编排输入。
        projection: 已解析并校验覆盖的 Gate 1 投影。
        llm_clients: Service 显式注入的 writer/auditor clients。
        host_context: 可选 Host run context；只在 bridge 层翻译为 Agent 中断。

    Returns:
        Service `ChapterOrchestrationResult`。

    Raises:
        ValueError: 当 Agent 或 Service dataclass 校验失败时抛出。
    """

    from fund_agent.services.chapter_orchestrator import (
        ChapterOrchestrationResult,
    )

    agent_run = run_agent_body_chapters(
        projection,
        llm_clients=AgentLLMClients(writer=llm_clients.writer, auditor=llm_clients.auditor),
        policy=_agent_policy_from_service(input_data),
        evidence_availability=_service_evidence_availability(input_data, projection),
        interruption_checker=_interruption_checker(host_context),
    )
    _record_agent_phase_events(agent_run.tasks, host_context=host_context)
    chapter_results = tuple(
        _service_chapter_result_from_task(task, projection=projection) for task in agent_run.tasks
    )
    accepted_conclusions = tuple(
        result.accepted_conclusion
        for result in chapter_results
        if result.accepted_conclusion is not None
    )
    if len(accepted_conclusions) == len(input_data.policy.target_chapter_ids):
        status = "accepted"
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
        blocked_reasons=tuple(reason for task in agent_run.tasks for reason in task.blocked_reasons),
        generated_chapter_ids=tuple(task.chapter_id for task in agent_run.tasks if task.status != "skipped"),
        skipped_chapter_ids=(),
    )


def _agent_policy_from_service(input_data: ChapterOrchestrationInput) -> AgentRunPolicy:
    """把 Service policy 映射为 Agent policy。

    Args:
        input_data: Service 编排输入。

    Returns:
        Agent run policy。

    Raises:
        ValueError: 当 policy 字段非法时由 AgentRunPolicy 抛出。
    """

    service_policy = input_data.policy
    return AgentRunPolicy(
        target_chapter_ids=service_policy.target_chapter_ids,
        repair_policy=AgentRepairPolicy(
            max_content_repair_attempts=service_policy.max_repair_attempts,
        ),
        max_output_chars=service_policy.max_output_chars,
        prompt_payload_mode=service_policy.prompt_payload_mode,
        run_programmatic_audit=service_policy.run_programmatic_audit,
        run_llm_audit=service_policy.run_llm_audit,
        typed_template_path=service_policy.typed_template_path,
    )


def _service_evidence_availability(
    input_data: ChapterOrchestrationInput,
    projection: ChapterFactProjection,
) -> object | None:
    """按 Service 当前入口派生 typed availability。

    Args:
        input_data: Service 编排输入。
        projection: Gate 1 投影。

    Returns:
        typed path 的 `EvidenceAvailability`；legacy path 返回 `None`。

    Raises:
        ValueError: 当 availability 派生失败时由 Service/Fund 抛出。
    """

    if input_data.policy.typed_template_path != "typed_template_contract":
        return None
    from fund_agent.services import chapter_orchestrator

    return chapter_orchestrator.derive_evidence_availability(projection)


def _record_agent_phase_events(
    tasks: tuple[ChapterTask, ...],
    *,
    host_context: HostRunContext | None,
) -> None:
    """按 Agent tool traces 回放 Host 安全 phase events。

    Args:
        tasks: Agent 正文章节任务。
        host_context: 可选 Host run context。

    Returns:
        无返回值。

    Raises:
        HostRuntimeError: 当 Host 事件诊断字段非法时由 Host 抛出。
    """

    if host_context is None:
        return
    for task in tasks:
        for attempt in task.attempts:
            for trace in attempt.tool_traces:
                phase = _phase_from_tool_name(trace.request.tool_name)
                if phase is None:
                    continue
                host_context.record_phase_started(
                    phase=phase,
                    chapter_id=task.chapter_id,
                    attempt=attempt.attempt_index,
                )
                host_context.record_phase_completed(
                    phase=phase,
                    chapter_id=task.chapter_id,
                    attempt=attempt.attempt_index,
                    elapsed_ms=trace.elapsed_ms,
                )
            if _attempt_entered_repair(attempt):
                host_context.record_phase_started(
                    phase="repair",
                    chapter_id=task.chapter_id,
                    attempt=attempt.attempt_index,
                )
                host_context.record_phase_completed(
                    phase="repair",
                    chapter_id=task.chapter_id,
                    attempt=attempt.attempt_index,
                    elapsed_ms=0,
                )


def _phase_from_tool_name(tool_name: str) -> str | None:
    """把 Agent tool name 映射为 Host phase。

    Args:
        tool_name: Agent tool name。

    Returns:
        Host phase；非 writer/auditor 工具返回 `None`。

    Raises:
        无。
    """

    if tool_name == "fund.write_chapter":
        return "writer"
    if tool_name == "fund.audit_chapter_llm":
        return "auditor"
    return None


def _attempt_entered_repair(attempt: ChapterAttempt) -> bool:
    """判断 Agent attempt 是否进入显式 repair phase。

    Args:
        attempt: Agent 单章 attempt。

    Returns:
        `True` 表示该 attempt 的 repair decision 要求 regenerate。

    Raises:
        无。
    """

    decision = attempt.repair_decision
    return getattr(decision, "action", None) == "regenerate"


def _interruption_checker(host_context: HostRunContext | None):
    """构造 Host 到 Agent 的中断翻译器。

    Args:
        host_context: 可选 Host run context。

    Returns:
        Agent runner 可调用的 interruption checker。

    Raises:
        无。
    """

    return _HostInterruptionChecker(host_context=host_context)


@dataclass(frozen=True, slots=True)
class _HostInterruptionChecker:
    """HostContext 到 AgentSchedulerInterruption 的可调用翻译器。"""

    host_context: HostRunContext | None

    def __call__(
        self,
        phase: str,
        chapter_id: int | None,
        attempt_index: int | None,
    ) -> AgentSchedulerInterruption:
        """检查 Host cancel/deadline 并返回 Agent normalized interruption。

        Args:
            phase: 当前 Agent phase。
            chapter_id: 当前章节编号。
            attempt_index: 当前 attempt。

        Returns:
            Agent scheduler interruption。

        Raises:
            无。
        """

        if self.host_context is None:
            return AgentSchedulerInterruption(
                status="none",
                reason=None,
                phase=phase,
                chapter_id=chapter_id,
                attempt_index=attempt_index,
            )
        exceeded = self.host_context.cancel_if_deadline_exceeded()
        if exceeded:
            return AgentSchedulerInterruption(
                status="deadline_exceeded",
                reason="host deadline exceeded",
                phase=phase,
                chapter_id=chapter_id,
                attempt_index=attempt_index,
            )
        if self.host_context.cancellation_token.is_cancelled():
            reason = self.host_context.cancellation_token.reason
            return AgentSchedulerInterruption(
                status="cancelled",
                reason=reason.value if reason is not None else "host cancelled",
                phase=phase,
                chapter_id=chapter_id,
                attempt_index=attempt_index,
            )
        return AgentSchedulerInterruption(
            status="none",
            reason=None,
            phase=phase,
            chapter_id=chapter_id,
            attempt_index=attempt_index,
        )


def _service_chapter_result_from_task(task: ChapterTask, *, projection: ChapterFactProjection):
    """把 Agent task 投影为 Service ChapterRunResult。

    Args:
        task: Agent 正文章节 task。
        projection: 同源章节事实投影。

    Returns:
        Service `ChapterRunResult`。

    Raises:
        ValueError: 当 accepted task 缺少 conclusion 时抛出。
    """

    from fund_agent.services.chapter_orchestrator import ChapterRunResult

    accepted_conclusion = (
        _service_conclusion_from_agent(task.accepted_conclusion)
        if task.accepted_conclusion is not None
        else None
    )
    return ChapterRunResult(
        chapter_id=task.chapter_id,
        title=task.title,
        status=_service_status_from_task(task),
        stop_reason=_service_stop_reason_from_task(task),
        accepted_draft=task.accepted_draft,  # type: ignore[arg-type]
        accepted_conclusion=accepted_conclusion,
        attempts=tuple(
            _service_attempt_from_agent(attempt, task=task, projection=projection)
            for attempt in task.attempts
        ),
        issues=task.blocked_reasons,
        failure_category=_failure_category_from_task(task),  # type: ignore[arg-type]
        failure_subcategory=_failure_subcategory_from_task(task),  # type: ignore[arg-type]
        prompt_contract_diagnostics=_prompt_contract_diagnostics_from_task(task),
        runtime_diagnostics=_runtime_diagnostics_from_task(task, projection=projection),
    )


def _service_attempt_from_agent(
    attempt: ChapterAttempt,
    *,
    task: ChapterTask,
    projection: ChapterFactProjection,
):
    """把 Agent attempt 投影为 Service attempt record。

    Args:
        attempt: Agent attempt。
        task: Agent task。
        projection: 同源章节事实投影。

    Returns:
        Service `ChapterAttemptRecord`。

    Raises:
        ValueError: 当 writer_result 类型缺失时抛出。
    """

    from fund_agent.services.chapter_orchestrator import ChapterAttemptRecord

    writer_result = attempt.writer_result
    if writer_result is not None and not isinstance(writer_result, ChapterWriteResult):
        raise ValueError("Agent attempt writer_result 类型不符合 Fund writer result")
    audit_result = attempt.audit_result
    if audit_result is not None and not isinstance(audit_result, ChapterAuditResult):
        raise ValueError("Agent attempt audit_result 类型不符合 Fund audit result")
    return ChapterAttemptRecord(
        attempt_index=attempt.attempt_index,
        writer_result=writer_result,  # type: ignore[arg-type]
        audit_result=audit_result,
        repair_decision=_service_repair_decision_from_agent(attempt.repair_decision),
        runtime_diagnostics=_attempt_runtime_diagnostics(attempt, task=task, projection=projection),
    )


def _service_repair_decision_from_agent(decision: object | None):
    """把 Agent repair decision 投影为 Service repair decision。

    Args:
        decision: Agent repair decision 或 `None`。

    Returns:
        Service `ChapterRepairDecision` 或 `None`。

    Raises:
        ValueError: 当 decision 缺少必要字段时抛出。
    """

    if decision is None:
        return None
    from fund_agent.services.chapter_orchestrator import ChapterRepairDecision

    return ChapterRepairDecision(
        action=decision.action,  # type: ignore[attr-defined,arg-type]
        reason=decision.reason,  # type: ignore[attr-defined]
        stop_reason=decision.stop_reason,  # type: ignore[attr-defined,arg-type]
        source_repair_hint=decision.source_repair_hint,  # type: ignore[attr-defined]
        issue_ids=decision.issue_ids,  # type: ignore[attr-defined]
    )


def _service_conclusion_from_agent(conclusion: object):
    """把 Agent accepted conclusion 投影为 Service conclusion。

    Args:
        conclusion: Agent accepted conclusion。

    Returns:
        Service `AcceptedChapterConclusion`。

    Raises:
        无。
    """

    from fund_agent.services.chapter_orchestrator import AcceptedChapterConclusion

    return AcceptedChapterConclusion(
        chapter_id=conclusion.chapter_id,  # type: ignore[attr-defined]
        title=conclusion.title,  # type: ignore[attr-defined]
        conclusion_markdown=conclusion.conclusion_markdown,  # type: ignore[attr-defined]
        conclusion_truncated=conclusion.conclusion_truncated,  # type: ignore[attr-defined]
        conclusion_source=conclusion.conclusion_source,  # type: ignore[attr-defined,arg-type]
        used_fact_ids=conclusion.used_fact_ids,  # type: ignore[attr-defined]
        used_anchor_ids=conclusion.used_anchor_ids,  # type: ignore[attr-defined]
        declared_missing_reasons=conclusion.declared_missing_reasons,  # type: ignore[attr-defined,arg-type]
        audit_checked_rules=conclusion.audit_checked_rules,  # type: ignore[attr-defined,arg-type]
    )


def _service_status_from_task(task: ChapterTask) -> str:
    """映射 Agent task status 到 Service status。

    Args:
        task: Agent task。

    Returns:
        Service status 字符串。

    Raises:
        无。
    """

    if task.status == "accepted":
        return "accepted"
    if task.status == "failed":
        return "failed"
    if task.status == "skipped":
        return "skipped"
    return "blocked"


def _service_stop_reason_from_task(task: ChapterTask) -> str:
    """映射 Agent terminal 到 Service stop reason。

    Args:
        task: Agent task。

    Returns:
        Service stop reason。

    Raises:
        无。
    """

    if task.status == "accepted":
        return "none"
    if task.stop_reason is not None and task.stop_reason != "scheduler_interrupted":
        return task.stop_reason
    if task.terminal_state == "blocked_repair_budget_exhausted":
        return "repair_budget_exhausted"
    if task.terminal_state == "blocked_needs_more_facts":
        return "needs_more_facts"
    if task.terminal_state == "blocked_dependency_missing":
        return "dependency_missing"
    if task.terminal_state == "blocked_fund_identity_fact_gap":
        return "fund_type_unknown"
    if task.terminal_state == "blocked_fact_gap":
        return "missing_required_facts"
    if task.terminal_state == "blocked_provider_runtime":
        if task.failure_category == "llm_timeout":
            return "llm_timeout"
        return "llm_exception"
    if task.terminal_state == "blocked_prompt_contract":
        return _prompt_contract_stop_reason(task)
    if task.terminal_state == "blocked_audit_contract":
        return "auditor_blocked"
    if task.terminal_state == "blocked_audit_failed":
        return "auditor_failed"
    if task.terminal_state == "blocked_scheduler_interrupted":
        return "llm_exception"
    if task.terminal_state == "blocked_internal_code_bug":
        return "llm_exception"
    return "writer_blocked"


def _prompt_contract_diagnostics_from_task(task: ChapterTask) -> tuple[object, ...]:
    """从 Agent task 生成 Service prompt-contract diagnostics。

    Args:
        task: Agent task。

    Returns:
        prompt diagnostics。

    Raises:
        无。
    """

    from fund_agent.services.chapter_orchestrator import (
        _audit_prompt_contract_diagnostic,
        _writer_prompt_contract_diagnostic,
    )

    diagnostics: list[object] = []
    for attempt in task.attempts:
        if isinstance(attempt.writer_result, ChapterWriteResult) and attempt.writer_result.status == "blocked":
            diagnostic = _writer_prompt_contract_diagnostic(
                attempt.writer_result,
                chapter_id=task.chapter_id,
                attempt_index=attempt.attempt_index,
            )
            if diagnostic is not None:
                diagnostics.append(diagnostic)
        if isinstance(attempt.audit_result, ChapterAuditResult) and not attempt.audit_result.accepted:
            diagnostic = _audit_prompt_contract_diagnostic(
                attempt.audit_result,
                chapter_id=task.chapter_id,
                attempt_index=attempt.attempt_index,
            )
            if diagnostic is not None:
                diagnostics.append(diagnostic)
    return tuple(diagnostics)


def _attempt_runtime_diagnostics(
    attempt: ChapterAttempt,
    *,
    task: ChapterTask,
    projection: ChapterFactProjection,
) -> tuple[object, ...]:
    """从 Agent attempt 生成 Service attempt-level runtime diagnostics。

    Args:
        attempt: Agent attempt。
        task: Agent task。
        projection: 同源章节事实投影。

    Returns:
        runtime diagnostics。

    Raises:
        无。
    """

    from fund_agent.services.chapter_orchestrator import (
        _exception_runtime_diagnostics,
        _audit_runtime_diagnostic,
        _writer_runtime_diagnostic,
    )

    if (
        isinstance(task.exception, Exception)
        and task.exception_attempt_index == attempt.attempt_index
        and any(trace.request.tool_name == "fund.audit_chapter_llm" for trace in attempt.tool_traces)
    ):
        return _exception_runtime_diagnostics(
            projection,
            chapter_id=task.chapter_id,
            operation="auditor",
            attempt_index=attempt.attempt_index,
            exc=task.exception,
        )
    if isinstance(attempt.writer_result, ChapterWriteResult) and attempt.writer_result.status == "blocked":
        return (
            _writer_runtime_diagnostic(
                projection,
                chapter_id=task.chapter_id,
                operation="writer",
                attempt_index=attempt.attempt_index,
                writer_result=attempt.writer_result,
            ),
        )
    if isinstance(attempt.audit_result, ChapterAuditResult) and not attempt.audit_result.accepted:
        return (
            _audit_runtime_diagnostic(
                projection,
                chapter_id=task.chapter_id,
                operation="auditor",
                attempt_index=attempt.attempt_index,
                audit_result=attempt.audit_result,
            ),
        )
    return ()


def _runtime_diagnostics_from_task(
    task: ChapterTask,
    *,
    projection: ChapterFactProjection,
) -> tuple[object, ...]:
    """从 Agent task 生成 Service chapter-level runtime diagnostics。

    Args:
        task: Agent task。
        projection: 同源章节事实投影。

    Returns:
        runtime diagnostics。

    Raises:
        无。
    """

    if not isinstance(task.exception, Exception):
        return ()
    if any(
        attempt.attempt_index == task.exception_attempt_index
        and any(trace.request.tool_name == "fund.audit_chapter_llm" for trace in attempt.tool_traces)
        for attempt in task.attempts
    ):
        return ()
    from fund_agent.services.chapter_orchestrator import _exception_runtime_diagnostics

    return _exception_runtime_diagnostics(
        projection,
        chapter_id=task.chapter_id,
        operation="writer",
        attempt_index=task.exception_attempt_index or 0,
        exc=task.exception,
    )


def _failure_category_from_task(task: ChapterTask) -> str | None:
    """从 Agent task 投影 Service failure category。

    Args:
        task: Agent task。

    Returns:
        failure category。

    Raises:
        无。
    """

    if task.status == "accepted":
        return None
    if isinstance(task.exception, Exception):
        return task.failure_category
    last_audit = _last_audit_result(task)
    if last_audit is not None:
        from fund_agent.services.chapter_orchestrator import _chapter_failure_category_from_audit_result

        return _chapter_failure_category_from_audit_result(last_audit)
    return task.failure_category


def _failure_subcategory_from_task(task: ChapterTask) -> str | None:
    """从 Service prompt diagnostic 投影 failure subcategory。

    Args:
        task: Agent task。

    Returns:
        failure subcategory。

    Raises:
        无。
    """

    diagnostics = _prompt_contract_diagnostics_from_task(task)
    if diagnostics:
        primary = getattr(diagnostics[-1], "primary_subcategory", None)
        if primary is not None:
            return primary
    return task.failure_subcategory


def _last_audit_result(task: ChapterTask) -> ChapterAuditResult | None:
    """读取最后一个 audit result。

    Args:
        task: Agent task。

    Returns:
        最后一个 audit result；不存在时返回 `None`。

    Raises:
        无。
    """

    for attempt in reversed(task.attempts):
        if isinstance(attempt.audit_result, ChapterAuditResult):
            return attempt.audit_result
    return None


def _prompt_contract_stop_reason(task: ChapterTask) -> str:
    """从 Agent blocked reason 尽量恢复 writer prompt-contract stop reason。

    Args:
        task: Agent task。

    Returns:
        Service writer stop reason。

    Raises:
        无。
    """

    joined = " ".join(task.blocked_reasons)
    for stop_reason in (
        "missing_required_structure",
        "missing_required_output_marker",
        "unknown_anchor",
        "response_too_long",
        "response_incomplete",
        "llm_contract_violation",
    ):
        if stop_reason in joined:
            return stop_reason
    return "llm_contract_violation"
