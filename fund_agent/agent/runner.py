"""Agent body chapter runner，见基金分析模板第 1-6 章。

本模块内化当前正文章节 write-audit-repair 执行机制。Service 仍负责用例、
provider 构造和最终报告装配；Host 仍只提供生命周期信号，进入本模块前必须
被翻译为 `AgentSchedulerInterruption`。
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Final, Literal

from fund_agent.agent.contracts import (
    AgentAcceptedChapterConclusion,
    AgentRepairPolicy,
    AgentReportRun,
    AgentSchedulerInterruption,
    AgentTerminalState,
    ChapterAttempt,
    ChapterTask,
    FinalAssemblyReadiness,
    ToolTrace,
)
from fund_agent.agent.repair import AgentRepairDecision, decide_repair, repair_context_from_audit
from fund_agent.agent.tools import (
    audit_chapter_llm_tool,
    audit_chapter_programmatic_tool,
    write_chapter_tool,
)
from fund_agent.fund.chapter_auditor import (
    CHAPTER_AUDIT_SCHEMA_VERSION,
    ChapterAuditInput,
    ChapterAuditLLMClient,
    ChapterAuditResult,
    ChapterLLMAuditResult,
    ChapterProgrammaticAuditResult,
)
from fund_agent.fund.chapter_facts import ChapterFactProjection
from fund_agent.fund.chapter_writer import (
    ChapterDraft,
    ChapterLLMClient,
    ChapterWriteResult,
    ChapterWriteStopReason,
    build_chapter_writer_input,
)
from fund_agent.fund.evidence_availability import (
    EVIDENCE_AVAILABILITY_SCHEMA_VERSION,
    EvidenceAvailability,
    derive_evidence_availability,
)
from fund_agent.fund.template.typed_contracts import (
    RequiredOutputItem,
    TypedChapterContract,
    get_typed_chapter_contract,
)

AgentTypedTemplatePath = Literal["legacy_contract", "typed_template_contract"]
AgentInterruptionChecker = Callable[
    [str, int | None, int | None],
    AgentSchedulerInterruption,
]
AgentPhaseEvent = Literal["started", "completed"]
AgentPhaseRecorder = Callable[
    [AgentPhaseEvent, str, int, int, int | None],
    None,
]

DEFAULT_TARGET_CHAPTER_IDS: Final[tuple[int, ...]] = (1, 2, 3, 4, 5, 6)
MAX_ACCEPTED_CONCLUSION_CHARS: Final[int] = 500


@dataclass(frozen=True, slots=True, kw_only=True)
class AgentLLMClients:
    """Agent runner 显式 LLM client 输入。

    Args:
        writer: Service 构造的 writer client。
        auditor: Service 构造的 auditor client。

    Raises:
        无显式抛出。
    """

    writer: ChapterLLMClient | None
    auditor: ChapterAuditLLMClient | None


@dataclass(frozen=True, slots=True, kw_only=True)
class AgentRunPolicy:
    """Agent 正文章节执行策略。

    Args:
        target_chapter_ids: 本次执行的正文模板章节编号。
        repair_policy: 内容修复策略。
        max_output_chars: writer 输出字符硬上限。
        prompt_payload_mode: writer prompt payload 模式。
        run_programmatic_audit: 是否执行程序审计。
        run_llm_audit: 是否执行 LLM 审计。
        typed_template_path: 是否启用 typed template contract sidecar。

    Raises:
        ValueError: 当章节范围或输出上限非法时抛出。
    """

    target_chapter_ids: tuple[int, ...] = DEFAULT_TARGET_CHAPTER_IDS
    repair_policy: AgentRepairPolicy = AgentRepairPolicy(max_content_repair_attempts=1)
    max_output_chars: int = 12000
    prompt_payload_mode: str = "full"
    run_programmatic_audit: bool = True
    run_llm_audit: bool = True
    typed_template_path: AgentTypedTemplatePath = "legacy_contract"

    def __post_init__(self) -> None:
        """校验 Agent run policy。

        Args:
            无。

        Returns:
            无返回值。

        Raises:
            ValueError: 当参数非法时抛出。
        """

        if not self.target_chapter_ids:
            raise ValueError("target_chapter_ids 不能为空")
        if len(set(self.target_chapter_ids)) != len(self.target_chapter_ids):
            raise ValueError("target_chapter_ids 不能重复")
        invalid = tuple(chapter_id for chapter_id in self.target_chapter_ids if chapter_id not in range(1, 7))
        if invalid:
            raise ValueError(f"Agent runner 只允许模板第 1-6 章：{invalid}")
        if self.max_output_chars <= 0:
            raise ValueError("max_output_chars 必须为正数")
        if self.prompt_payload_mode not in {"full", "compact"}:
            raise ValueError("prompt_payload_mode 必须为 full 或 compact")
        if self.typed_template_path not in {"legacy_contract", "typed_template_contract"}:
            raise ValueError("typed_template_path 必须为 legacy_contract / typed_template_contract")


@dataclass(frozen=True, slots=True)
class AgentRunner:
    """Agent 正文章节 runner façade。"""

    def run(
        self,
        projection: ChapterFactProjection,
        *,
        llm_clients: AgentLLMClients,
        policy: AgentRunPolicy | None = None,
        evidence_availability: object | None = None,
        interruption_checker: AgentInterruptionChecker | None = None,
        phase_recorder: AgentPhaseRecorder | None = None,
    ) -> AgentReportRun:
        """执行模板第 1-6 章 Agent body run。

        Args:
            projection: 同源 Gate 1 章节事实投影。
            llm_clients: Service 显式注入的 writer/auditor client。
            policy: Agent 执行策略；为空时使用默认策略。
            evidence_availability: Service bridge 可显式传入的同源 availability。
            interruption_checker: Host 信号翻译后的可选中断检查器。
            phase_recorder: 可选 phase 事件记录器，由 Service bridge 翻译到 Host。

        Returns:
            Agent run 记录。

        Raises:
            ValueError: 当 projection 缺少目标章节或 policy 非法时抛出。
        """

        return run_agent_body_chapters(
            projection,
            llm_clients=llm_clients,
            policy=policy,
            evidence_availability=evidence_availability,
            interruption_checker=interruption_checker,
            phase_recorder=phase_recorder,
        )


def run_agent_body_chapters(
    projection: ChapterFactProjection,
    *,
    llm_clients: AgentLLMClients,
    policy: AgentRunPolicy | None = None,
    evidence_availability: object | None = None,
    interruption_checker: AgentInterruptionChecker | None = None,
    phase_recorder: AgentPhaseRecorder | None = None,
) -> AgentReportRun:
    """执行模板第 1-6 章 Agent body run。

    Args:
        projection: 同源 Gate 1 章节事实投影。
        llm_clients: Service 显式注入的 writer/auditor client。
        policy: Agent 执行策略；为空时使用默认策略。
        evidence_availability: 可选同源证据可用性；为空时 Agent 派生一次。
        interruption_checker: Host 信号翻译后的可选中断检查器。
        phase_recorder: 可选 phase 事件记录器，由 Service bridge 翻译到 Host。

    Returns:
        Agent run 记录，包含 body readiness handoff。

    Raises:
        ValueError: 当 projection 覆盖或 policy 非法时抛出。
    """

    run_policy = policy or AgentRunPolicy()
    _validate_projection_coverage(projection, run_policy.target_chapter_ids)
    run_evidence_availability = _run_evidence_availability(
        projection,
        policy=run_policy,
        evidence_availability=evidence_availability,
    )
    if projection.fund_type == "unknown":
        return _blocked_run(
            projection,
            policy=run_policy,
            evidence_availability=run_evidence_availability,
            terminal_state="blocked_fund_identity_fact_gap",
            reason="基金类型 unknown，禁止生成模板第 1-6 章类型化章节。",
            failure_category="fact_gap",
        )
    if run_policy.run_llm_audit and llm_clients.auditor is None:
        return _blocked_run(
            projection,
            policy=run_policy,
            evidence_availability=run_evidence_availability,
            terminal_state="blocked_provider_runtime",
            reason="缺少显式注入的章节 LLM 审计 client，不能进入写作。",
            failure_category="provider_runtime",
        )

    tasks: list[ChapterTask] = []
    for chapter_id in run_policy.target_chapter_ids:
        interruption = _check_interruption(
            interruption_checker,
            phase="before_chapter",
            chapter_id=chapter_id,
            attempt_index=None,
        )
        if interruption.status != "none":
            tasks.extend(
                _scheduler_blocked_tasks(
                    projection,
                    chapter_ids=run_policy.target_chapter_ids[len(tasks) :],
                    interruption=interruption,
                )
            )
            return _run_from_tasks(
                projection,
                policy=run_policy,
                evidence_availability=run_evidence_availability,
                tasks=tuple(tasks),
                scheduler_interruption=interruption,
            )
        tasks.append(
            _run_single_chapter(
                projection,
                chapter_id=chapter_id,
                policy=run_policy,
                llm_clients=llm_clients,
                evidence_availability=run_evidence_availability,
                interruption_checker=interruption_checker,
                phase_recorder=phase_recorder,
            )
        )
    return _run_from_tasks(
        projection,
        policy=run_policy,
        evidence_availability=run_evidence_availability,
        tasks=tuple(tasks),
        scheduler_interruption=None,
    )


def _run_single_chapter(
    projection: ChapterFactProjection,
    *,
    chapter_id: int,
    policy: AgentRunPolicy,
    llm_clients: AgentLLMClients,
    evidence_availability: object,
    interruption_checker: AgentInterruptionChecker | None,
    phase_recorder: AgentPhaseRecorder | None,
) -> ChapterTask:
    """执行单个正文章节。

    Args:
        projection: 同源章节事实投影。
        chapter_id: 模板章节编号。
        policy: Agent 执行策略。
        llm_clients: Service 显式注入的 writer/auditor client。
        evidence_availability: run-level 同源证据可用性。
        interruption_checker: 可选中断检查器。
        phase_recorder: 可选 phase 事件记录器。

    Returns:
        单章任务结果。

    Raises:
        ValueError: 当 writer drafted 缺少 draft 时抛出。
    """

    title = _chapter_title(projection, chapter_id)
    attempts: list[ChapterAttempt] = []
    attempt_index = 0
    try:
        writer_input = _writer_input(
            projection,
            chapter_id=chapter_id,
            policy=policy,
            evidence_availability=evidence_availability,
            repair_context=None,
        )
    except Exception as exc:
        return _exception_task(
            title,
            chapter_id=chapter_id,
            attempt_index=attempt_index,
            traces=(),
            exception=exc,
            previous_attempts=tuple(attempts),
        )
    while True:
        interruption = _check_interruption(
            interruption_checker,
            phase="before_writer",
            chapter_id=chapter_id,
            attempt_index=attempt_index,
        )
        if interruption.status != "none":
            return _scheduler_blocked_task(title, chapter_id=chapter_id, interruption=interruption, attempts=tuple(attempts))

        _record_phase_started(phase_recorder, "writer", chapter_id, attempt_index)
        writer_execution = write_chapter_tool(
            writer_input,
            llm_client=llm_clients.writer,
            attempt_index=attempt_index,
        )
        _record_phase_completed(
            phase_recorder,
            "writer",
            chapter_id,
            attempt_index,
            writer_execution.trace.elapsed_ms,
        )
        if writer_execution.exception is not None:
            return _exception_task(
                title,
                chapter_id=chapter_id,
                attempt_index=attempt_index,
                traces=(writer_execution.trace,),
                exception=writer_execution.exception,
                previous_attempts=tuple(attempts),
            )
        writer_result = _require_output(writer_execution.output, "writer")
        interruption = _check_interruption(
            interruption_checker,
            phase="after_tool_call",
            chapter_id=chapter_id,
            attempt_index=attempt_index,
        )
        if interruption.status != "none":
            attempts.append(
                ChapterAttempt(
                    attempt_index=attempt_index,
                    tool_traces=(writer_execution.trace,),
                    terminal_state="blocked_scheduler_interrupted",
                    writer_result=writer_result,
                )
            )
            return _scheduler_blocked_task(title, chapter_id=chapter_id, interruption=interruption, attempts=tuple(attempts))
        if writer_result.status == "blocked":
            terminal = _terminal_from_writer_stop_reason(writer_result.stop_reason)
            attempts.append(
                ChapterAttempt(
                    attempt_index=attempt_index,
                    tool_traces=(writer_execution.trace,),
                    terminal_state=terminal,
                    writer_result=writer_result,
                )
            )
            return ChapterTask(
                chapter_id=chapter_id,
                title=title,
                status="blocked" if terminal != "blocked_internal_code_bug" else "failed",
                terminal_state=terminal,
                attempts=tuple(attempts),
                stop_reason=writer_result.stop_reason,
                blocked_reasons=_writer_blocked_reasons(chapter_id, writer_result),
                failure_category=_failure_category_from_writer_result(writer_result),
                failure_subcategory=_failure_subcategory_from_writer_stop_reason(writer_result.stop_reason),
            )

        draft = writer_result.draft
        if draft is None:
            raise ValueError("writer drafted 状态必须包含 draft")
        interruption = _check_interruption(
            interruption_checker,
            phase="between_writer_and_auditor",
            chapter_id=chapter_id,
            attempt_index=attempt_index,
        )
        if interruption.status != "none":
            attempts.append(
                ChapterAttempt(
                    attempt_index=attempt_index,
                    tool_traces=(writer_execution.trace,),
                    terminal_state="blocked_scheduler_interrupted",
                    writer_result=writer_result,
                )
            )
            return _scheduler_blocked_task(title, chapter_id=chapter_id, interruption=interruption, attempts=tuple(attempts))

        audit_input = ChapterAuditInput(
            writer_input=writer_input,
            draft=draft,
            typed_chapter_contract=_typed_chapter_contract(chapter_id, policy=policy),
            run_programmatic=policy.run_programmatic_audit,
            run_llm=policy.run_llm_audit,
        )
        audit_traces: list[ToolTrace] = [writer_execution.trace]
        if policy.run_programmatic_audit:
            programmatic_execution = audit_chapter_programmatic_tool(audit_input, attempt_index=attempt_index)
            audit_traces.append(programmatic_execution.trace)
            if programmatic_execution.exception is not None:
                return _exception_task(
                    title,
                    chapter_id=chapter_id,
                    attempt_index=attempt_index,
                    traces=tuple(audit_traces),
                    exception=programmatic_execution.exception,
                    previous_attempts=tuple(attempts),
                    writer_result=writer_result,
                )
            programmatic_result = _require_output(programmatic_execution.output, "programmatic audit")
        else:
            programmatic_result = ChapterProgrammaticAuditResult(
                status="pass",
                issues=(),
                checked_rules=(),
            )
        interruption = _check_interruption(
            interruption_checker,
            phase="between_programmatic_and_llm_auditor",
            chapter_id=chapter_id,
            attempt_index=attempt_index,
        )
        if interruption.status != "none":
            attempts.append(
                ChapterAttempt(
                    attempt_index=attempt_index,
                    tool_traces=tuple(audit_traces),
                    terminal_state="blocked_scheduler_interrupted",
                    writer_result=writer_result,
                )
            )
            return _scheduler_blocked_task(title, chapter_id=chapter_id, interruption=interruption, attempts=tuple(attempts))
        if policy.run_llm_audit:
            _record_phase_started(phase_recorder, "auditor", chapter_id, attempt_index)
            llm_execution = audit_chapter_llm_tool(
                audit_input,
                llm_client=llm_clients.auditor,
                attempt_index=attempt_index,
            )
            _record_phase_completed(
                phase_recorder,
                "auditor",
                chapter_id,
                attempt_index,
                llm_execution.trace.elapsed_ms,
            )
            audit_traces.append(llm_execution.trace)
            if llm_execution.exception is not None:
                return _exception_task(
                    title,
                    chapter_id=chapter_id,
                    attempt_index=attempt_index,
                    traces=tuple(audit_traces),
                    exception=llm_execution.exception,
                    previous_attempts=tuple(attempts),
                    writer_result=writer_result,
                )
            llm_result = _require_output(llm_execution.output, "llm audit")
        else:
            llm_result = ChapterLLMAuditResult(
                status="pass",
                issues=(),
                raw_response=None,
                model_name=None,
                finish_reason=None,
            )
        traces = tuple(audit_traces)
        audit_result = _audit_result(
            programmatic=programmatic_result,  # type: ignore[arg-type]
            llm=llm_result,  # type: ignore[arg-type]
        )
        interruption = _check_interruption(
            interruption_checker,
            phase="after_tool_call",
            chapter_id=chapter_id,
            attempt_index=attempt_index,
        )
        if interruption.status != "none":
            attempts.append(
                ChapterAttempt(
                    attempt_index=attempt_index,
                    tool_traces=traces,
                    terminal_state="blocked_scheduler_interrupted",
                    writer_result=writer_result,
                    audit_result=audit_result,
                )
            )
            return _scheduler_blocked_task(title, chapter_id=chapter_id, interruption=interruption, attempts=tuple(attempts))
        if audit_result.accepted:
            attempts.append(
                ChapterAttempt(
                    attempt_index=attempt_index,
                    tool_traces=traces,
                    terminal_state="accepted",
                    writer_result=writer_result,
                    audit_result=audit_result,
                )
            )
            return ChapterTask(
                chapter_id=chapter_id,
                title=title,
                status="accepted",
                terminal_state="accepted",
                attempts=tuple(attempts),
                stop_reason="none",
                accepted_draft=draft,
                accepted_conclusion=_accepted_conclusion(draft, audit_result),
            )

        interruption = _check_interruption(
            interruption_checker,
            phase="before_repair_decision",
            chapter_id=chapter_id,
            attempt_index=attempt_index,
        )
        if interruption.status != "none":
            attempts.append(
                ChapterAttempt(
                    attempt_index=attempt_index,
                    tool_traces=traces,
                    terminal_state="blocked_scheduler_interrupted",
                    writer_result=writer_result,
                    audit_result=audit_result,
                )
            )
            return _scheduler_blocked_task(title, chapter_id=chapter_id, interruption=interruption, attempts=tuple(attempts))
        decision = decide_repair(
            audit_result,
            remaining_budget=policy.repair_policy.max_content_repair_attempts - attempt_index,
            auditor_available=llm_clients.auditor is not None,
            run_llm_audit=policy.run_llm_audit,
        )
        terminal = _terminal_from_repair_decision(decision, audit_result)
        attempts.append(
            ChapterAttempt(
                attempt_index=attempt_index,
                tool_traces=traces,
                terminal_state=terminal,
                writer_result=writer_result,
                audit_result=audit_result,
                repair_decision=decision,
            )
        )
        if decision.action == "regenerate":
            _record_phase_started(phase_recorder, "repair", chapter_id, attempt_index)
            _record_phase_completed(phase_recorder, "repair", chapter_id, attempt_index, 0)
            attempt_index += 1
            writer_input = _writer_input(
                projection,
                chapter_id=chapter_id,
                policy=policy,
                evidence_availability=evidence_availability,
                repair_context=repair_context_from_audit(audit_result, attempt_index=attempt_index),
            )
            continue
        return ChapterTask(
            chapter_id=chapter_id,
            title=title,
            status=_status_from_repair_decision(decision, audit_result),
            terminal_state=terminal,
            attempts=tuple(attempts),
            stop_reason=decision.stop_reason,
            blocked_reasons=_audit_blocked_reasons(chapter_id, audit_result, decision),
            failure_category=_failure_category_from_audit_result(audit_result),
        )


def _writer_input(
    projection: ChapterFactProjection,
    *,
    chapter_id: int,
    policy: AgentRunPolicy,
    evidence_availability: object,
    repair_context: object | None,
) -> object:
    """构造 Fund writer input。

    Args:
        projection: 同源章节事实投影。
        chapter_id: 模板章节编号。
        policy: Agent 执行策略。
        evidence_availability: run-level 同源证据可用性。
        repair_context: 可选 writer repair context。

    Returns:
        Fund writer input。

    Raises:
        ValueError: 当 Fund writer input 构造失败时抛出。
    """

    return build_chapter_writer_input(
        projection,
        chapter_id=chapter_id,
        max_output_chars=policy.max_output_chars,
        repair_context=repair_context,  # type: ignore[arg-type]
        prompt_payload_mode=policy.prompt_payload_mode,  # type: ignore[arg-type]
        typed_required_output_items=_typed_required_output_items(chapter_id, policy=policy),
        evidence_availability=evidence_availability
        if policy.typed_template_path == "typed_template_contract"
        else None,  # type: ignore[arg-type]
    )


def _run_evidence_availability(
    projection: ChapterFactProjection,
    *,
    policy: AgentRunPolicy,
    evidence_availability: object | None,
) -> EvidenceAvailability:
    """按 Agent policy 选择 run-level evidence availability。

    Args:
        projection: 同源章节事实投影。
        policy: Agent 执行策略。
        evidence_availability: Service bridge 可显式传入的 availability。

    Returns:
        typed path 返回完整同源 availability；legacy path 返回空 requirement 信封。

    Raises:
        ValueError: 当传入对象不是 `EvidenceAvailability` 时抛出。
    """

    if evidence_availability is not None:
        if not isinstance(evidence_availability, EvidenceAvailability):
            raise ValueError("Agent runner evidence_availability 必须是 EvidenceAvailability")
        return evidence_availability
    if policy.typed_template_path == "typed_template_contract":
        return derive_evidence_availability(projection)
    return EvidenceAvailability(
        schema_version=EVIDENCE_AVAILABILITY_SCHEMA_VERSION,
        source_schema_version=projection.schema_version,
        fund_code=projection.fund_code,
        report_year=projection.report_year,
        requirements=(),
    )


def _audit_result(
    *,
    programmatic: ChapterProgrammaticAuditResult,
    llm: ChapterLLMAuditResult,
) -> ChapterAuditResult:
    """汇总分层审计结果。

    Args:
        programmatic: 程序审计结果。
        llm: LLM 审计结果。

    Returns:
        Fund audit 汇总结果。

    Raises:
        无。
    """

    issues = (*programmatic.issues, *llm.issues)
    if programmatic.status == "blocked" or llm.status == "blocked":
        status = "blocked"
    elif programmatic.status == "fail" or llm.status == "fail":
        status = "fail"
    else:
        status = "pass"
    return ChapterAuditResult(
        schema_version=CHAPTER_AUDIT_SCHEMA_VERSION,
        status=status,
        programmatic=programmatic,
        llm=llm,
        accepted=status == "pass",
        repair_hint=_aggregate_repair_hint(issues, status),
    )


def _aggregate_repair_hint(
    issues: tuple[object, ...],
    status: str,
) -> Literal["none", "patch", "regenerate", "needs_more_facts"]:
    """聚合 audit repair hint。

    Args:
        issues: 审计 issue。
        status: 审计汇总状态。

    Returns:
        聚合 repair hint。

    Raises:
        无。
    """

    if status == "pass":
        return "none"
    order = {"none": 0, "patch": 1, "regenerate": 2, "needs_more_facts": 3}
    selected: Literal["none", "patch", "regenerate", "needs_more_facts"] = "none"
    for issue in issues:
        repair_hint = getattr(issue, "repair_hint", "none")
        if repair_hint in order and order[repair_hint] > order[selected]:
            selected = repair_hint
    return selected


def _run_from_tasks(
    projection: ChapterFactProjection,
    *,
    policy: AgentRunPolicy,
    evidence_availability: object,
    tasks: tuple[ChapterTask, ...],
    scheduler_interruption: AgentSchedulerInterruption | None,
) -> AgentReportRun:
    """从任务集合构造 Agent run。

    Args:
        projection: 同源章节事实投影。
        policy: Agent 执行策略。
        evidence_availability: 同源证据可用性。
        tasks: 正文章节任务。
        scheduler_interruption: 当前 scheduler 中断。

    Returns:
        Agent run。

    Raises:
        ValueError: 当 AgentReportRun 校验失败时抛出。
    """

    readiness = _final_readiness(tasks)
    if readiness.ready:
        status = "accepted"
    elif any(task.status == "accepted" for task in tasks):
        status = "partial"
    else:
        status = "blocked"
    return AgentReportRun(
        fund_code=projection.fund_code,
        report_year=projection.report_year,
        status=status,
        projection=projection,
        evidence_availability=evidence_availability,  # type: ignore[arg-type]
        repair_policy=policy.repair_policy,
        tasks=tasks,
        final_assembly_readiness=readiness,
        scheduler_interruption=scheduler_interruption,
    )


def _blocked_run(
    projection: ChapterFactProjection,
    *,
    policy: AgentRunPolicy,
    evidence_availability: object,
    terminal_state: AgentTerminalState,
    reason: str,
    failure_category: str,
) -> AgentReportRun:
    """构造全局阻断 Agent run。

    Args:
        projection: 同源章节事实投影。
        policy: Agent 执行策略。
        evidence_availability: 同源证据可用性。
        terminal_state: Agent terminal。
        reason: 安全阻断原因。
        failure_category: 失败分类。

    Returns:
        blocked Agent run。

    Raises:
        ValueError: 当 task 校验失败时抛出。
    """

    tasks = tuple(
        ChapterTask(
            chapter_id=chapter_id,
            title=_chapter_title(projection, chapter_id),
            status="blocked",
            terminal_state=terminal_state,
            stop_reason=_stop_reason_from_global_terminal(terminal_state),
            blocked_reasons=(f"{chapter_id}:{terminal_state}:{reason}",),
            failure_category=failure_category,
        )
        for chapter_id in policy.target_chapter_ids
    )
    return _run_from_tasks(
        projection,
        policy=policy,
        evidence_availability=evidence_availability,
        tasks=tasks,
        scheduler_interruption=None,
    )


def _scheduler_blocked_tasks(
    projection: ChapterFactProjection,
    *,
    chapter_ids: tuple[int, ...],
    interruption: AgentSchedulerInterruption,
) -> list[ChapterTask]:
    """构造未执行章节的 scheduler-blocked tasks。

    Args:
        projection: 同源章节事实投影。
        chapter_ids: 待阻断章节。
        interruption: scheduler 中断。

    Returns:
        blocked task 列表。

    Raises:
        ValueError: 当 task 校验失败时抛出。
    """

    return [
        _scheduler_blocked_task(
            _chapter_title(projection, chapter_id),
            chapter_id=chapter_id,
            interruption=interruption,
            attempts=(),
        )
        for chapter_id in chapter_ids
    ]


def _scheduler_blocked_task(
    title: str,
    *,
    chapter_id: int,
    interruption: AgentSchedulerInterruption,
    attempts: tuple[ChapterAttempt, ...],
) -> ChapterTask:
    """构造 scheduler 中断 task。

    Args:
        title: 章节标题。
        chapter_id: 模板章节编号。
        interruption: scheduler 中断。
        attempts: 已记录 attempts。

    Returns:
        blocked task。

    Raises:
        ValueError: 当 task 校验失败时抛出。
    """

    stop_reason = _scheduler_stop_reason(interruption)
    return ChapterTask(
        chapter_id=chapter_id,
        title=title,
        status="blocked",
        terminal_state="blocked_scheduler_interrupted",
        attempts=attempts,
        stop_reason=stop_reason,
        blocked_reasons=(f"{chapter_id}:blocked_scheduler_interrupted:{interruption.status}:{interruption.phase}",),
        failure_category=stop_reason,
    )


def _scheduler_stop_reason(interruption: AgentSchedulerInterruption) -> str:
    """把 Agent scheduler interruption 投影为安全停止原因。

    Args:
        interruption: scheduler 中断。

    Returns:
        可由 Service bridge 继续投影的 scheduler 停止原因。

    Raises:
        ValueError: 当 interruption status 非中断状态时抛出。
    """

    if interruption.status == "cancelled":
        return "scheduler_cancelled"
    if interruption.status == "deadline_exceeded":
        return "scheduler_deadline_exceeded"
    raise ValueError("scheduler blocked task 必须来自 cancelled 或 deadline_exceeded")


def _exception_task(
    title: str,
    *,
    chapter_id: int,
    attempt_index: int,
    traces: tuple[ToolTrace, ...],
    exception: Exception,
    previous_attempts: tuple[ChapterAttempt, ...] = (),
    writer_result: object | None = None,
) -> ChapterTask:
    """构造异常 fail-closed task。

    Args:
        title: 章节标题。
        chapter_id: 模板章节编号。
        attempt_index: attempt 序号。
        traces: 已记录工具 trace。
        exception: 捕获异常。
        previous_attempts: 当前异常前已经完成的 attempts。
        writer_result: auditor 异常前已生成的 writer result。

    Returns:
        failed task。

    Raises:
        ValueError: 当 task 校验失败时抛出。
    """

    terminal = _terminal_from_exception(exception)
    category = _failure_category_from_exception(exception)
    current_attempts = (
        previous_attempts
        if len(traces) == 0 or (len(traces) == 1 and traces[0].request.tool_name == "fund.write_chapter")
        else (
            *previous_attempts,
            ChapterAttempt(
                attempt_index=attempt_index,
                tool_traces=traces,
                terminal_state=terminal,
                writer_result=writer_result,
                audit_result=None,
            ),
        )
    )
    return ChapterTask(
        chapter_id=chapter_id,
        title=title,
        status="failed",
        terminal_state=terminal,
        attempts=current_attempts,
        stop_reason=_stop_reason_from_exception(exception),
        blocked_reasons=(f"{chapter_id}:{terminal}:{type(exception).__name__}",),
        failure_category=category,
        exception=exception,
        exception_attempt_index=attempt_index,
    )


def _final_readiness(tasks: tuple[ChapterTask, ...]) -> FinalAssemblyReadiness:
    """构造 final assembly readiness。

    Args:
        tasks: 正文章节任务。

    Returns:
        readiness handoff。

    Raises:
        ValueError: 当章节集合冲突时抛出。
    """

    accepted = tuple(task.chapter_id for task in tasks if task.status == "accepted")
    blocked = tuple(task.chapter_id for task in tasks if task.status != "accepted")
    return FinalAssemblyReadiness(
        ready=not blocked and bool(accepted),
        accepted_source_chapter_ids=accepted,
        blocked_chapter_ids=blocked,
        blocking_reasons=tuple(reason for task in tasks for reason in task.blocked_reasons),
    )


def _accepted_conclusion(
    draft: ChapterDraft,
    audit_result: ChapterAuditResult,
) -> AgentAcceptedChapterConclusion:
    """从 accepted draft 抽取 Agent conclusion handoff。

    Args:
        draft: accepted 章节草稿。
        audit_result: accepted 审计结果。

    Returns:
        Agent accepted conclusion。

    Raises:
        ValueError: 当 conclusion chapter_id 非正文时抛出。
    """

    text, source = _extract_conclusion_text(draft.markdown)
    capped_text, truncated = _cap_conclusion(text)
    return AgentAcceptedChapterConclusion(
        chapter_id=draft.chapter_id,
        title=draft.title,
        conclusion_markdown=capped_text,
        conclusion_truncated=truncated,
        conclusion_source=source,
        used_fact_ids=draft.used_fact_ids,
        used_anchor_ids=draft.used_anchor_ids,
        declared_missing_reasons=tuple(draft.declared_missing_reasons),
        audit_checked_rules=tuple(audit_result.programmatic.checked_rules),
    )


def _extract_conclusion_text(markdown: str) -> tuple[str, str]:
    """确定性抽取结论要点段落。

    Args:
        markdown: 章节 Markdown。

    Returns:
        `(结论文本, 来源)`。

    Raises:
        无。
    """

    lines = markdown.splitlines()
    for heading in ("### 结论要点", "## 结论要点"):
        extracted = _extract_heading_block(lines, heading)
        if extracted is not None:
            return extracted, "heading"
    fallback_lines = tuple(line.strip() for line in lines if line.strip())[:3]
    return "\n".join(fallback_lines), "fallback_lines"


def _extract_heading_block(lines: list[str], heading: str) -> str | None:
    """抽取 heading 内容块。

    Args:
        lines: Markdown 行。
        heading: 目标标题。

    Returns:
        内容块；未找到时为 `None`。

    Raises:
        无。
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
    """应用 accepted conclusion 字符上限。

    Args:
        text: 原始结论。

    Returns:
        `(截断后文本, 是否截断)`。

    Raises:
        无。
    """

    if len(text) <= MAX_ACCEPTED_CONCLUSION_CHARS:
        return text, False
    return text[:MAX_ACCEPTED_CONCLUSION_CHARS], True


def _typed_chapter_contract(
    chapter_id: int,
    *,
    policy: AgentRunPolicy,
) -> TypedChapterContract | None:
    """读取 typed chapter contract。

    Args:
        chapter_id: 模板章节编号。
        policy: Agent 执行策略。

    Returns:
        typed contract；legacy path 返回 `None`。

    Raises:
        ValueError: 当 typed sidecar 无法加载时抛出。
    """

    if policy.typed_template_path != "typed_template_contract":
        return None
    return get_typed_chapter_contract(chapter_id)


def _typed_required_output_items(
    chapter_id: int,
    *,
    policy: AgentRunPolicy,
) -> tuple[RequiredOutputItem, ...]:
    """读取 typed required output items。

    Args:
        chapter_id: 模板章节编号。
        policy: Agent 执行策略。

    Returns:
        required output items；legacy path 返回空元组。

    Raises:
        ValueError: 当 typed sidecar 无法加载时抛出。
    """

    contract = _typed_chapter_contract(chapter_id, policy=policy)
    if contract is None:
        return ()
    return contract.required_output_items


def _check_interruption(
    interruption_checker: AgentInterruptionChecker | None,
    *,
    phase: str,
    chapter_id: int | None,
    attempt_index: int | None,
) -> AgentSchedulerInterruption:
    """检查已归一化 scheduler 中断。

    Args:
        interruption_checker: 可选中断检查器。
        phase: 当前 Agent phase。
        chapter_id: 当前章节。
        attempt_index: 当前 attempt。

    Returns:
        scheduler interruption。

    Raises:
        无。
    """

    if interruption_checker is None:
        return AgentSchedulerInterruption(
            status="none",
            reason=None,
            phase=phase,
            chapter_id=chapter_id,
            attempt_index=attempt_index,
        )
    return interruption_checker(phase, chapter_id, attempt_index)


def _record_phase_started(
    phase_recorder: AgentPhaseRecorder | None,
    phase: str,
    chapter_id: int,
    attempt_index: int,
) -> None:
    """记录 Agent phase 开始事件。

    Args:
        phase_recorder: 可选 phase 事件记录器。
        phase: Agent phase 名称。
        chapter_id: 模板章节编号。
        attempt_index: attempt 序号。

    Returns:
        无返回值。

    Raises:
        HostRuntimeError: 当上层 recorder 连接 Host 且诊断字段非法时由 Host 抛出。
    """

    if phase_recorder is None:
        return
    phase_recorder("started", phase, chapter_id, attempt_index, None)


def _record_phase_completed(
    phase_recorder: AgentPhaseRecorder | None,
    phase: str,
    chapter_id: int,
    attempt_index: int,
    elapsed_ms: int | None,
) -> None:
    """记录 Agent phase 完成事件。

    Args:
        phase_recorder: 可选 phase 事件记录器。
        phase: Agent phase 名称。
        chapter_id: 模板章节编号。
        attempt_index: attempt 序号。
        elapsed_ms: phase 耗时毫秒。

    Returns:
        无返回值。

    Raises:
        HostRuntimeError: 当上层 recorder 连接 Host 且诊断字段非法时由 Host 抛出。
    """

    if phase_recorder is None:
        return
    phase_recorder("completed", phase, chapter_id, attempt_index, elapsed_ms)


def _validate_projection_coverage(
    projection: ChapterFactProjection,
    chapter_ids: tuple[int, ...],
) -> None:
    """校验 projection 唯一覆盖目标章节。

    Args:
        projection: Gate 1 投影。
        chapter_ids: 目标章节。

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


def _chapter_title(projection: ChapterFactProjection, chapter_id: int) -> str:
    """读取章节标题。

    Args:
        projection: Gate 1 投影。
        chapter_id: 模板章节编号。

    Returns:
        章节标题。

    Raises:
        ValueError: 当章节不存在时抛出。
    """

    for chapter in projection.chapters:
        if chapter.chapter_id == chapter_id:
            return chapter.title
    raise ValueError(f"projection 缺少章节：{chapter_id}")


def _require_output(output: object | None, operation: str) -> object:
    """校验工具成功路径必须有输出。

    Args:
        output: 工具输出。
        operation: 操作名。

    Returns:
        原始输出。

    Raises:
        ValueError: 当输出缺失时抛出。
    """

    if output is None:
        raise ValueError(f"{operation} 工具成功路径缺少输出")
    return output


def _terminal_from_writer_stop_reason(stop_reason: ChapterWriteStopReason) -> AgentTerminalState:
    """映射 writer stop reason 到 Agent terminal。

    Args:
        stop_reason: writer 停止原因。

    Returns:
        Agent terminal。

    Raises:
        无。
    """

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


def _terminal_from_repair_decision(
    decision: AgentRepairDecision,
    audit_result: ChapterAuditResult,
) -> AgentTerminalState:
    """映射 repair decision 到 Agent terminal。

    Args:
        decision: repair 决策。
        audit_result: Fund 审计结果。

    Returns:
        Agent terminal。

    Raises:
        无。
    """

    if decision.action == "regenerate":
        return "blocked_audit_failed" if audit_result.status == "fail" else "blocked_audit_contract"
    if decision.stop_reason == "repair_budget_exhausted":
        return "blocked_repair_budget_exhausted"
    if decision.stop_reason == "needs_more_facts":
        return "blocked_needs_more_facts"
    if decision.stop_reason == "llm_unavailable":
        return "blocked_provider_runtime"
    if decision.stop_reason == "auditor_blocked":
        return "blocked_audit_contract"
    return "blocked_audit_failed"


def _status_from_repair_decision(
    decision: AgentRepairDecision,
    audit_result: ChapterAuditResult,
) -> str:
    """从 repair decision 推导 Agent task status。

    Args:
        decision: repair 决策。
        audit_result: Fund 审计结果。

    Returns:
        `blocked` 或 `failed`。

    Raises:
        无。
    """

    if decision.stop_reason == "needs_more_facts":
        return "blocked"
    if audit_result.status == "blocked":
        return "blocked"
    return "failed"


def _stop_reason_from_global_terminal(terminal_state: AgentTerminalState) -> str:
    """从全局阻断 terminal 推导停止原因。

    Args:
        terminal_state: Agent terminal。

    Returns:
        停止原因字符串。

    Raises:
        无。
    """

    if terminal_state == "blocked_fund_identity_fact_gap":
        return "fund_type_unknown"
    if terminal_state == "blocked_provider_runtime":
        return "llm_unavailable"
    return terminal_state


def _terminal_from_exception(exc: Exception) -> AgentTerminalState:
    """映射异常到 Agent terminal。

    Args:
        exc: 捕获异常。

    Returns:
        Agent terminal。

    Raises:
        无。
    """

    if _is_provider_runtime_exception(exc):
        return "blocked_provider_runtime"
    return "blocked_internal_code_bug"


def _stop_reason_from_exception(exc: Exception) -> str:
    """从异常类型映射精确停止原因。

    Args:
        exc: 捕获异常。

    Returns:
        停止原因。

    Raises:
        无。
    """

    type_name = type(exc).__name__
    if type_name == "LLMProviderTimeoutError":
        return "llm_timeout"
    if type_name == "LLMProviderRateLimitError":
        return "llm_rate_limited"
    if type_name == "LLMProviderMalformedResponseError":
        return "llm_malformed_response"
    if type_name == "LLMProviderNetworkError":
        return "llm_network_error"
    return "llm_exception"


def _is_provider_runtime_exception(exc: Exception) -> bool:
    """判断异常是否属于 provider runtime。

    Args:
        exc: 捕获异常。

    Returns:
        provider runtime 异常返回 `True`。

    Raises:
        无。
    """

    return type(exc).__name__ in {
        "LLMProviderTimeoutError",
        "LLMProviderRateLimitError",
        "LLMProviderMalformedResponseError",
        "LLMProviderNetworkError",
        "LLMProviderRuntimeError",
    }


def _failure_category_from_exception(exc: Exception) -> str:
    """映射异常失败分类。

    Args:
        exc: 捕获异常。

    Returns:
        失败分类。

    Raises:
        无。
    """

    if type(exc).__name__ == "LLMProviderTimeoutError":
        return "llm_timeout"
    if _is_provider_runtime_exception(exc):
        return "provider_runtime"
    return "code_bug"


def _failure_category_from_writer_result(writer_result: ChapterWriteResult) -> str:
    """映射 writer blocked 失败分类。

    Args:
        writer_result: writer 结果。

    Returns:
        失败分类。

    Raises:
        无。
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
    if writer_result.stop_reason.startswith("llm_"):
        return "provider_runtime"
    return "code_bug"


def _failure_category_from_audit_result(audit_result: ChapterAuditResult) -> str:
    """映射 audit blocked/failed 失败分类。

    Args:
        audit_result: audit 结果。

    Returns:
        失败分类。

    Raises:
        无。
    """

    issue_ids = {issue.issue_id for issue in (*audit_result.programmatic.issues, *audit_result.llm.issues)}
    if "llm:parse_failure" in issue_ids:
        return "audit_parse"
    if audit_result.repair_hint == "needs_more_facts":
        return "fact_gap"
    if audit_result.status in ("fail", "blocked"):
        return "prompt_contract"
    return "code_bug"


def _failure_subcategory_from_writer_stop_reason(stop_reason: ChapterWriteStopReason) -> str | None:
    """映射 writer prompt-contract 子类。

    Args:
        stop_reason: writer 停止原因。

    Returns:
        子类；非 prompt-contract 返回 `None`。

    Raises:
        无。
    """

    mapping = {
        "missing_required_structure": "missing_structure",
        "missing_required_output_marker": "missing_required_marker",
        "unknown_anchor": "unknown_anchor",
        "response_too_long": "response_length_incomplete",
        "response_incomplete": "response_length_incomplete",
    }
    return mapping.get(stop_reason)


def _writer_blocked_reasons(
    chapter_id: int,
    writer_result: ChapterWriteResult,
) -> tuple[str, ...]:
    """构造 writer blocked reasons。

    Args:
        chapter_id: 模板章节编号。
        writer_result: writer 结果。

    Returns:
        安全阻断原因。

    Raises:
        无。
    """

    issue_ids = tuple(issue.issue_id for issue in writer_result.issues)
    if issue_ids:
        return tuple(f"{chapter_id}:{writer_result.stop_reason}:{issue_id}" for issue_id in issue_ids)
    return (f"{chapter_id}:{writer_result.stop_reason}",)


def _audit_blocked_reasons(
    chapter_id: int,
    audit_result: ChapterAuditResult,
    decision: AgentRepairDecision,
) -> tuple[str, ...]:
    """构造 audit blocked reasons。

    Args:
        chapter_id: 模板章节编号。
        audit_result: audit 结果。
        decision: repair 决策。

    Returns:
        安全阻断原因。

    Raises:
        无。
    """

    issues = (*audit_result.programmatic.issues, *audit_result.llm.issues)
    if issues:
        return tuple(f"{chapter_id}:{decision.stop_reason}:{issue.issue_id}" for issue in issues)
    return (f"{chapter_id}:{decision.stop_reason}",)
