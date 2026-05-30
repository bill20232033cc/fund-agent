"""Service 层章节编排器，见基金分析模板第 1-6 章。

本模块只负责编排 Route C Gate 3 的 write-audit-repair policy：调用 Gate 1
`ChapterFactProvider` 投影和 Gate 2 `chapter_writer` / `chapter_auditor`
primitive。它不读取年报仓库、PDF、cache、source helper、下载器或 parser，
不构造真实 LLM provider，不接入 Host/Agent/dayu，也不生成第 0/7 章正文。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Final, Literal, get_args

from fund_agent.fund.chapter_auditor import (
    ChapterAuditInput,
    ChapterAuditIssue,
    ChapterAuditLLMClient,
    ChapterAuditRepairHint,
    ChapterAuditResult,
    ChapterAuditRuleCode,
    audit_chapter,
)
from fund_agent.fund.chapter_facts import (
    ChapterFactMissingReason,
    ChapterFactProjection,
    ChapterFactProvider,
)
from fund_agent.fund.chapter_writer import (
    ChapterDraft,
    ChapterLLMClient,
    ChapterWriteResult,
    ChapterWriteStopReason,
    build_chapter_writer_input,
    write_chapter,
)
from fund_agent.fund.data_extractor import StructuredFundDataBundle

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
    "llm_exception",
]
ChapterRepairAction = Literal["none", "regenerate", "needs_more_facts", "stop"]
ChapterOrchestrationInputKind = Literal["structured_bundle", "chapter_projection"]
AcceptedChapterConclusionSource = Literal["heading", "fallback_lines"]

CHAPTER_ORCHESTRATOR_SCHEMA_VERSION: ChapterOrchestratorSchemaVersion = (
    "chapter_orchestrator.v1"
)
DEFAULT_TARGET_CHAPTER_IDS: Final[tuple[int, ...]] = (1, 2, 3, 4, 5, 6)
MAX_ACCEPTED_CONCLUSION_CHARS: Final[int] = 500
_TARGET_CHAPTER_ID_SET: Final[frozenset[int]] = frozenset(DEFAULT_TARGET_CHAPTER_IDS)
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
}


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
        fail_fast: 任一章节 fail-closed 后是否停止后续章节。
        run_programmatic_audit: 是否执行 Gate 2 programmatic audit。
        run_llm_audit: 是否执行 Gate 2 LLM audit。
    """

    target_chapter_ids: tuple[int, ...] = DEFAULT_TARGET_CHAPTER_IDS
    max_repair_attempts: int = 1
    max_output_chars: int = 12000
    fail_fast: bool = True
    run_programmatic_audit: bool = True
    run_llm_audit: bool = True

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
    """

    attempt_index: int
    writer_result: ChapterWriteResult
    audit_result: ChapterAuditResult | None
    repair_decision: ChapterRepairDecision | None


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
    """

    chapter_id: int
    title: str
    status: ChapterRunStatus
    stop_reason: ChapterRunStopReason
    accepted_draft: ChapterDraft | None
    accepted_conclusion: AcceptedChapterConclusion | None
    attempts: tuple[ChapterAttemptRecord, ...]
    issues: tuple[str, ...]


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
        skipped_chapter_ids: 因 Gate 3 scope 或 fail_fast 跳过的章节。
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
) -> ChapterOrchestrationResult:
    """编排模板第 1-6 章 write-audit-repair 流程。

    Args:
        input_data: 章节编排输入。
        llm_clients: 显式注入的 writer/auditor LLM client。
        fact_provider: 可选 Gate 1 provider；仅在 bundle 输入时使用。

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

    chapter_results: list[ChapterRunResult] = []
    skipped_chapter_ids: list[int] = []
    stop_remaining = False
    for chapter_id in policy.target_chapter_ids:
        if stop_remaining:
            chapter_results.append(_skipped_result(projection, chapter_id))
            skipped_chapter_ids.append(chapter_id)
            continue

        run_result = _run_single_chapter(
            projection,
            chapter_id=chapter_id,
            policy=policy,
            llm_clients=llm_clients,
        )
        chapter_results.append(run_result)
        if policy.fail_fast and run_result.status != "accepted":
            stop_remaining = True

    return _orchestration_result(input_data, projection, tuple(chapter_results), tuple(skipped_chapter_ids))


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


def _run_single_chapter(
    projection: ChapterFactProjection,
    *,
    chapter_id: int,
    policy: ChapterOrchestrationPolicy,
    llm_clients: ChapterOrchestratorLLMClients,
) -> ChapterRunResult:
    """执行单章写作、审计和有限 regenerate。

    Args:
        projection: Gate 1 投影。
        chapter_id: 模板章节编号。
        policy: 编排策略。
        llm_clients: 显式注入的 writer/auditor LLM client。

    Returns:
        单章编排结果。

    Raises:
        ValueError: 当 writer stop reason 未被 Gate 3 接受时抛出。
    """

    title = _chapter_title(projection, chapter_id)
    attempts: list[ChapterAttemptRecord] = []
    issues: list[str] = []
    writer_input = build_chapter_writer_input(
        projection,
        chapter_id=chapter_id,
        max_output_chars=policy.max_output_chars,
    )
    attempt_index = 0
    while True:
        try:
            writer_result = write_chapter(writer_input, llm_client=llm_clients.writer)
        except Exception as exc:  # noqa: BLE001 - Service 层必须把 provider 异常 fail-closed。
            return _exception_result(chapter_id, title, attempts=tuple(attempts), exc=exc)

        if writer_result.status == "blocked":
            issues.extend(_writer_issue_messages(writer_result))
            attempts.append(
                ChapterAttemptRecord(
                    attempt_index=attempt_index,
                    writer_result=writer_result,
                    audit_result=None,
                    repair_decision=None,
                )
            )
            status, stop_reason = _map_writer_stop_reason(writer_result.stop_reason)
            return ChapterRunResult(
                chapter_id=chapter_id,
                title=title,
                status=status,
                stop_reason=stop_reason,
                accepted_draft=None,
                accepted_conclusion=None,
                attempts=tuple(attempts),
                issues=tuple(issues),
            )

        draft = writer_result.draft
        if draft is None:
            raise ValueError("writer drafted 状态必须包含 draft")
        audit_input = ChapterAuditInput(
            writer_input=writer_input,
            draft=draft,
            run_programmatic=policy.run_programmatic_audit,
            run_llm=policy.run_llm_audit,
        )
        try:
            audit_result = audit_chapter(audit_input, llm_client=llm_clients.auditor)
        except Exception as exc:  # noqa: BLE001 - Service 层必须把 provider 异常 fail-closed。
            attempts.append(
                ChapterAttemptRecord(
                    attempt_index=attempt_index,
                    writer_result=writer_result,
                    audit_result=None,
                    repair_decision=None,
                )
            )
            return _exception_result(chapter_id, title, attempts=tuple(attempts), exc=exc)

        if audit_result.accepted:
            attempts.append(
                ChapterAttemptRecord(
                    attempt_index=attempt_index,
                    writer_result=writer_result,
                    audit_result=audit_result,
                    repair_decision=None,
                )
            )
            conclusion = _accepted_conclusion(draft, audit_result)
            return ChapterRunResult(
                chapter_id=chapter_id,
                title=title,
                status="accepted",
                stop_reason="none",
                accepted_draft=draft,
                accepted_conclusion=conclusion,
                attempts=tuple(attempts),
                issues=tuple(issues),
            )

        issues.extend(_audit_issue_messages(audit_result))
        decision = _decide_repair(
            audit_result,
            remaining_budget=policy.max_repair_attempts - attempt_index,
            auditor_available=llm_clients.auditor is not None,
            run_llm_audit=policy.run_llm_audit,
        )
        attempts.append(
            ChapterAttemptRecord(
                attempt_index=attempt_index,
                writer_result=writer_result,
                audit_result=audit_result,
                repair_decision=decision,
            )
        )
        if decision.action == "regenerate":
            attempt_index += 1
            continue
        return ChapterRunResult(
            chapter_id=chapter_id,
            title=title,
            status=_status_from_audit_stop(decision, audit_result),
            stop_reason=_stop_reason_from_repair_decision(decision),
            accepted_draft=None,
            accepted_conclusion=None,
            attempts=tuple(attempts),
            issues=tuple(issues),
        )


def _exception_result(
    chapter_id: int,
    title: str,
    *,
    attempts: tuple[ChapterAttemptRecord, ...],
    exc: Exception,
) -> ChapterRunResult:
    """把 LLM client 异常转换为 fail-closed 单章结果。

    Args:
        chapter_id: 模板章节编号。
        title: 章节标题。
        attempts: 已记录的 attempt。
        exc: 捕获到的异常。

    Returns:
        单章 failed 结果。

    Raises:
        无显式抛出。
    """

    return ChapterRunResult(
        chapter_id=chapter_id,
        title=title,
        status="failed",
        stop_reason="llm_exception",
        accepted_draft=None,
        accepted_conclusion=None,
        attempts=attempts,
        issues=(f"LLM client exception: {type(exc).__name__}: {exc}",),
    )


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
        skipped_chapter_ids: fail_fast 跳过章节。

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
    generated_chapter_ids = tuple(
        result.chapter_id for result in chapter_results if result.attempts and result.status != "skipped"
    )
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


def _skipped_result(projection: ChapterFactProjection, chapter_id: int) -> ChapterRunResult:
    """构造 fail_fast 后续章节跳过结果。

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
        issues=("前序章节未 accepted，fail_fast 停止后续章节。",),
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
