"""Service 层最终章节总装器，见基金分析模板第 0 章和第 7 章。

本模块实现 Route C Gate 4 Slice 4A 的 `final_chapter_assembler.v1`：
只消费 Gate 3 已接受的第 1-6 章草稿/结论，以及 Agent/Fund 层已经派生的
`FinalJudgmentDecision`。它不读取年报仓库、PDF、cache、source helper、下载器
或 parser，不调用 LLM，不重新应用 preferred_lens、ITEM_RULE 或基金类型规则，
也不改变最终判断语义。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Final, Literal, get_args

from fund_agent.fund.analysis.final_judgment import (
    FinalJudgment,
    FinalJudgmentDecision,
)
from fund_agent.services.chapter_orchestrator import (
    AcceptedChapterConclusion,
    ChapterOrchestrationResult,
    ChapterRunResult,
)

FinalChapterAssemblerSchemaVersion = Literal["final_chapter_assembler.v1"]
FinalAssemblyStatus = Literal["accepted", "incomplete", "blocked"]
FinalAssemblyIssueSeverity = Literal["blocking", "informational"]
FinalAssemblyReadinessStatus = Literal["ready", "blocked"]
FinalAssemblyEvidenceStatus = Literal["accepted_body_chapters", "incomplete_body_chapters"]
FinalAssemblyIssueReason = Literal[
    "identity_mismatch",
    "invalid_policy",
    "orchestration_not_accepted",
    "missing_required_chapter",
    "duplicate_chapter",
    "chapter_not_accepted",
    "missing_accepted_draft",
    "missing_accepted_conclusion",
    "final_judgment_missing",
    "chapter7_readiness_blocked",
    "chapter7_missing",
    "chapter7_readiness_mismatch",
    "chapter0_source_missing",
    "chapter0_contract_violation",
    "chapter7_contract_violation",
    "chapter0_source_sparse",
]

FINAL_CHAPTER_ASSEMBLER_SCHEMA_VERSION: FinalChapterAssemblerSchemaVersion = (
    "final_chapter_assembler.v1"
)
DEFAULT_REQUIRED_BODY_CHAPTER_IDS: Final[tuple[int, ...]] = (1, 2, 3, 4, 5, 6)
CHAPTER0_ID: Final[int] = 0
CHAPTER7_ID: Final[int] = 7
CHAPTER0_TITLE: Final[str] = "投资要点概览"
CHAPTER7_TITLE: Final[str] = "是否值得持有--最终判断"
_CHAPTER0_MAX_CHARS: Final[int] = 5000
_SUPPORTING_SNIPPET_CHAPTER_LIMIT: Final[int] = 3
_JUDGMENT_LABELS: Final[dict[FinalJudgment, str]] = {
    "worth_holding": "🟢 值得持有",
    "needs_attention": "🟡 需要关注",
    "suggest_replace": "🔴 建议替换",
}


@dataclass(frozen=True, slots=True, kw_only=True)
class FinalAssemblyPolicy:
    """最终章节总装策略，见模板第 0 章和第 7 章。

    Attributes:
        require_orchestration_accepted: 是否要求 Gate 3 总状态为 accepted。
        required_body_chapter_ids: 必须进入总装的正文章节编号，默认第 1-6 章。
        include_chapter0: 是否生成模板第 0 章投资要点概览。
        include_chapter7: 是否生成模板第 7 章最终判断。
        allow_incomplete_debug_markdown: incomplete/blocked 时是否保留 debug markdown。
        max_chapter0_chars: 第 0 章输出字符硬上限。
    """

    require_orchestration_accepted: bool = True
    required_body_chapter_ids: tuple[int, ...] = DEFAULT_REQUIRED_BODY_CHAPTER_IDS
    include_chapter0: bool = True
    include_chapter7: bool = True
    allow_incomplete_debug_markdown: bool = False
    max_chapter0_chars: int = _CHAPTER0_MAX_CHARS

    def __post_init__(self) -> None:
        """校验最终章节总装策略。

        Args:
            无。

        Returns:
            无返回值。

        Raises:
            ValueError: 当章节范围、章节唯一性或输出上限非法时抛出。
        """

        _validate_policy(self)


@dataclass(frozen=True, slots=True, kw_only=True)
class FinalChapterAssemblyInput:
    """最终章节总装输入，见模板第 0 章和第 7 章。

    Attributes:
        fund_code: 基金代码。
        report_year: 年报年份。
        orchestration_result: Gate 3 第 1-6 章编排结果。
        final_judgment_decision: Agent/Fund 层已派生的最终判断决策。
        policy: 最终章节总装策略。
        schema_version: final assembler schema 版本。
    """

    fund_code: str
    report_year: int
    orchestration_result: ChapterOrchestrationResult
    final_judgment_decision: FinalJudgmentDecision
    policy: FinalAssemblyPolicy = field(default_factory=FinalAssemblyPolicy)
    schema_version: FinalChapterAssemblerSchemaVersion = FINAL_CHAPTER_ASSEMBLER_SCHEMA_VERSION

    def __post_init__(self) -> None:
        """校验总装输入 schema 与 identity。

        Args:
            无。

        Returns:
            无返回值。

        Raises:
            ValueError: 当 schema 或 fund identity 不一致时抛出。
        """

        _validate_input(self)


@dataclass(frozen=True, slots=True, kw_only=True)
class FinalAssemblyIssue:
    """最终章节总装问题。

    Attributes:
        issue_id: 稳定问题编号。
        severity: 问题严重程度。
        reason: typed 问题原因。
        message: 中文问题说明。
        chapter_ids: 相关章节编号。
    """

    issue_id: str
    severity: FinalAssemblyIssueSeverity
    reason: FinalAssemblyIssueReason
    message: str
    chapter_ids: tuple[int, ...] = ()


@dataclass(frozen=True, slots=True, kw_only=True)
class FinalAssemblyReadiness:
    """最终章节总装 readiness，见模板第 0 章消费第 7 章的依赖关系。

    Attributes:
        status: 第 7 章和第 0 章是否可进入 accepted 总装。
        required_body_chapter_ids: 必需正文章节编号，当前固定为模板第 1-6 章。
        accepted_body_chapter_ids: 同时具备 accepted draft 和 accepted conclusion 的章节编号。
        chapter7_required: 第 0 章是否要求第 7 章 typed bundle。
        chapter7_ready: 第 7 章 typed bundle 是否可作为第 0 章唯一动作来源。
        evidence_status: 证据/readiness 状态，用于第 7 章 typed bundle。
        issues: readiness 阻断或提示问题。
    """

    status: FinalAssemblyReadinessStatus
    required_body_chapter_ids: tuple[int, ...]
    accepted_body_chapter_ids: tuple[int, ...]
    chapter7_required: bool
    chapter7_ready: bool
    evidence_status: FinalAssemblyEvidenceStatus
    issues: tuple[FinalAssemblyIssue, ...]


@dataclass(frozen=True, slots=True, kw_only=True)
class FinalChapter7Summary:
    """Gate 4 本地第 7 章 typed 摘要，避免第 0 章反解析 markdown。

    Attributes:
        selected_judgment: `FinalJudgmentDecision.selected_judgment` 原始枚举值。
        selected_judgment_label: 面向报告展示的三选一动作。
        core_basis: 第 7 章支撑依据短句。
        easiest_misread: 当前最容易看错的地方。
        next_validation_plan: 下一轮最小验证计划。
        threshold_events: 升级/降级或终止当前判断的阈值事件。
        readiness_status: 第 7 章自身 readiness 状态。
        evidence_status: 第 7 章依据的正文章节证据/readiness 状态。
        accepted_body_chapter_ids: 支撑第 7 章的 accepted 正文章节编号。
        source: 最终判断来源。
        conflict_reasons: developer override 冲突原因。
    """

    selected_judgment: FinalJudgment
    selected_judgment_label: str
    core_basis: tuple[str, ...]
    easiest_misread: str
    next_validation_plan: str
    threshold_events: tuple[str, ...]
    readiness_status: FinalAssemblyReadinessStatus
    evidence_status: FinalAssemblyEvidenceStatus
    accepted_body_chapter_ids: tuple[int, ...]
    source: str
    conflict_reasons: tuple[str, ...]


@dataclass(frozen=True, slots=True, kw_only=True)
class FinalChapterAssemblyResult:
    """最终章节总装结果，见模板第 0 章和第 7 章。

    Attributes:
        status: 总装状态。
        fund_code: 基金代码。
        report_year: 年报年份。
        report_markdown: 完整报告 Markdown；未 accepted 时默认为 `None`。
        chapter0_markdown: 第 0 章 Markdown。
        chapter7_markdown: 第 7 章 Markdown。
        chapter7_summary: Gate 4 本地第 7 章 typed 摘要。
        assembled_chapter_ids: 最终报告渲染顺序中的章节编号。
        source_accepted_chapter_ids: Gate 3 accepted conclusions 来源章节编号。
        final_judgment_selected: 最终判断枚举值。
        issues: 总装问题列表。
        schema_version: final assembler schema 版本。
    """

    status: FinalAssemblyStatus
    fund_code: str
    report_year: int
    report_markdown: str | None
    chapter0_markdown: str | None
    chapter7_markdown: str | None
    chapter7_summary: FinalChapter7Summary | None
    assembled_chapter_ids: tuple[int, ...]
    source_accepted_chapter_ids: tuple[int, ...]
    final_judgment_selected: FinalJudgment
    issues: tuple[FinalAssemblyIssue, ...]
    schema_version: FinalChapterAssemblerSchemaVersion = FINAL_CHAPTER_ASSEMBLER_SCHEMA_VERSION


class FinalChapterAssembler:
    """Service 层最终章节总装 façade，见模板第 0 章和第 7 章。"""

    def assemble(self, input_data: FinalChapterAssemblyInput) -> FinalChapterAssemblyResult:
        """总装完整 LLM 路径报告。

        Args:
            input_data: 最终章节总装输入。

        Returns:
            最终章节总装结果。

        Raises:
            无显式抛出；输入 dataclass 会在构造期抛出 `ValueError`。
        """

        return assemble_final_chapters(input_data)


def assemble_final_chapters(
    input_data: FinalChapterAssemblyInput,
) -> FinalChapterAssemblyResult:
    """总装模板第 0 章、第 1-6 章和第 7 章报告。

    Args:
        input_data: 最终章节总装输入。

    Returns:
        最终章节总装结果；默认只有所有必需章节和第 7/0 章契约满足时才 accepted。

    Raises:
        无显式抛出；输入 dataclass 会在构造期抛出 `ValueError`。
    """

    policy = input_data.policy
    chapter_map = _chapter_result_map(input_data.orchestration_result)
    readiness = _build_final_assembly_readiness(input_data, chapter_map)
    issues = list(readiness.issues)
    body_conclusions = tuple(
        conclusion
        for chapter_id in policy.required_body_chapter_ids
        if (result := chapter_map.get(chapter_id)) is not None
        and (conclusion := result.accepted_conclusion) is not None
    )
    source_chapter_ids = tuple(conclusion.chapter_id for conclusion in body_conclusions)

    if issues:
        return _incomplete_result(input_data, issues=tuple(issues), source_chapter_ids=source_chapter_ids)

    chapter7_summary = _build_chapter7_summary(
        input_data.final_judgment_decision,
        body_conclusions,
        readiness,
    )
    if chapter7_summary is None:
        return _incomplete_result(
            input_data,
            issues=(
                FinalAssemblyIssue(
                    issue_id="final_assembly:chapter_7:missing",
                    severity="blocking",
                    reason="chapter7_missing",
                    message="第 7 章 typed bundle 缺失，第 0 章不能独立派生最终动作。",
                    chapter_ids=(CHAPTER7_ID,),
                ),
            ),
            source_chapter_ids=source_chapter_ids,
        )
    chapter7_issues = _validate_chapter7_summary(chapter7_summary, readiness)
    if chapter7_issues:
        return _incomplete_result(
            input_data,
            issues=chapter7_issues,
            source_chapter_ids=source_chapter_ids,
        )
    chapter7_markdown = _render_chapter7_markdown(chapter7_summary)
    chapter7_conclusion = _chapter7_accepted_conclusion(chapter7_summary)
    chapter0_markdown: str | None = None

    all_conclusions = (*body_conclusions, chapter7_conclusion)
    if policy.include_chapter0:
        chapter0_markdown, chapter0_issues = _render_chapter0_markdown(
            all_conclusions,
            chapter7_summary,
            max_chars=policy.max_chapter0_chars,
        )
        issues.extend(chapter0_issues)
        if chapter0_markdown is not None:
            issues.extend(_validate_chapter0_action(chapter0_markdown, chapter7_summary))

    status: FinalAssemblyStatus = "accepted"
    blocking_issues = tuple(issue for issue in issues if issue.severity == "blocking")
    if blocking_issues:
        status = "incomplete"

    assembled_ids = _assembled_chapter_ids(policy)
    report_markdown = None
    if status == "accepted" or policy.allow_incomplete_debug_markdown:
        report_markdown = _render_report_markdown(
            chapter0_markdown=chapter0_markdown,
            body_chapter_results=tuple(chapter_map[chapter_id] for chapter_id in policy.required_body_chapter_ids),
            chapter7_markdown=chapter7_markdown,
            policy=policy,
        )

    return FinalChapterAssemblyResult(
        status=status,
        fund_code=input_data.fund_code,
        report_year=input_data.report_year,
        report_markdown=report_markdown,
        chapter0_markdown=chapter0_markdown,
        chapter7_markdown=chapter7_markdown,
        chapter7_summary=chapter7_summary,
        assembled_chapter_ids=assembled_ids,
        source_accepted_chapter_ids=source_chapter_ids,
        final_judgment_selected=input_data.final_judgment_decision.selected_judgment,
        issues=tuple(issues),
    )


def _validate_policy(policy: FinalAssemblyPolicy) -> None:
    """校验最终章节总装策略。

    Args:
        policy: 待校验策略。

    Returns:
        无返回值。

    Raises:
        ValueError: 当策略非法时抛出。
    """

    chapter_ids = policy.required_body_chapter_ids
    if not chapter_ids:
        raise ValueError("required_body_chapter_ids 不能为空")
    if chapter_ids != DEFAULT_REQUIRED_BODY_CHAPTER_IDS:
        raise ValueError("Slice 4A 只允许按模板第 1-6 章顺序总装正文")
    if not policy.include_chapter7:
        raise ValueError("Slice 4A 必须生成模板第 7 章最终判断")
    if policy.max_chapter0_chars <= 0:
        raise ValueError("max_chapter0_chars 必须为正数")


def _validate_input(input_data: FinalChapterAssemblyInput) -> None:
    """校验最终章节总装输入。

    Args:
        input_data: 待校验输入。

    Returns:
        无返回值。

    Raises:
        ValueError: 当 schema、identity 或最终判断缺失时抛出。
    """

    if input_data.schema_version != FINAL_CHAPTER_ASSEMBLER_SCHEMA_VERSION:
        raise ValueError(f"未知最终章节总装 schema：{input_data.schema_version}")
    result = input_data.orchestration_result
    if input_data.fund_code != result.fund_code or input_data.report_year != result.report_year:
        raise ValueError(
            "最终章节总装输入 identity 不一致："
            f"request={input_data.fund_code}/{input_data.report_year}, "
            f"orchestration={result.fund_code}/{result.report_year}"
        )
    judgment = input_data.final_judgment_decision.selected_judgment
    if judgment not in get_args(FinalJudgment):
        raise ValueError(f"未知最终判断：{judgment}")


def _validate_orchestration(
    input_data: FinalChapterAssemblyInput,
) -> tuple[FinalAssemblyIssue, ...]:
    """校验 Gate 3 结果是否可进入最终总装。

    Args:
        input_data: 最终章节总装输入。

    Returns:
        总装问题列表。

    Raises:
        无显式抛出。
    """

    result = input_data.orchestration_result
    policy = input_data.policy
    issues: list[FinalAssemblyIssue] = []
    if policy.require_orchestration_accepted and result.status != "accepted":
        issues.append(
            FinalAssemblyIssue(
                issue_id="final_assembly:orchestration_not_accepted",
                severity="blocking",
                reason="orchestration_not_accepted",
                message=f"Gate 3 结果状态为 {result.status}，不能总装完整报告。",
            )
        )

    chapter_counts: dict[int, int] = {}
    for chapter_result in result.chapter_results:
        chapter_counts[chapter_result.chapter_id] = chapter_counts.get(chapter_result.chapter_id, 0) + 1
    duplicate_ids = tuple(chapter_id for chapter_id, count in chapter_counts.items() if count > 1)
    if duplicate_ids:
        issues.append(
            FinalAssemblyIssue(
                issue_id="final_assembly:duplicate_chapter",
                severity="blocking",
                reason="duplicate_chapter",
                message=f"Gate 3 结果存在重复章节：{duplicate_ids}。",
                chapter_ids=duplicate_ids,
            )
        )

    chapter_map = _chapter_result_map(result)
    for chapter_id in policy.required_body_chapter_ids:
        chapter_result = chapter_map.get(chapter_id)
        if chapter_result is None:
            issues.append(
                FinalAssemblyIssue(
                    issue_id=f"final_assembly:chapter_{chapter_id}:missing_required_chapter",
                    severity="blocking",
                    reason="missing_required_chapter",
                    message=f"缺少模板第 {chapter_id} 章 Gate 3 结果。",
                    chapter_ids=(chapter_id,),
                )
            )
            continue
        issues.extend(_validate_required_chapter(chapter_result))
    return tuple(issues)


def _build_final_assembly_readiness(
    input_data: FinalChapterAssemblyInput,
    chapter_map: dict[int, ChapterRunResult],
) -> FinalAssemblyReadiness:
    """构造第 7 章 required-body readiness，见模板第 7 章最终判断。

    Args:
        input_data: 最终章节总装输入。
        chapter_map: Gate 3 单章结果映射。

    Returns:
        typed readiness；只有第 1-6 章均 accepted 且有 draft/conclusion 才 ready。

    Raises:
        无显式抛出。
    """

    issues = list(_validate_orchestration(input_data))
    policy = input_data.policy
    accepted_body_chapter_ids = tuple(
        chapter_id
        for chapter_id in policy.required_body_chapter_ids
        if (result := chapter_map.get(chapter_id)) is not None
        and result.status == "accepted"
        and result.accepted_draft is not None
        and result.accepted_conclusion is not None
    )
    status: FinalAssemblyReadinessStatus = "ready" if not issues else "blocked"
    evidence_status: FinalAssemblyEvidenceStatus = (
        "accepted_body_chapters" if status == "ready" else "incomplete_body_chapters"
    )
    readiness_issues = tuple(issues)
    if status == "blocked" and not any(
        issue.reason == "chapter7_readiness_blocked" for issue in readiness_issues
    ):
        readiness_issues = (
            *readiness_issues,
            FinalAssemblyIssue(
                issue_id="final_assembly:chapter_7:readiness_blocked",
                severity="blocking",
                reason="chapter7_readiness_blocked",
                message="第 7 章要求模板第 1-6 章均 accepted 且具备 accepted draft/conclusion。",
                chapter_ids=(CHAPTER7_ID, *policy.required_body_chapter_ids),
            ),
        )
    return FinalAssemblyReadiness(
        status=status,
        required_body_chapter_ids=policy.required_body_chapter_ids,
        accepted_body_chapter_ids=accepted_body_chapter_ids,
        chapter7_required=policy.include_chapter7 and policy.include_chapter0,
        chapter7_ready=status == "ready",
        evidence_status=evidence_status,
        issues=readiness_issues,
    )


def _validate_required_chapter(chapter_result: ChapterRunResult) -> tuple[FinalAssemblyIssue, ...]:
    """校验单个必需正文章节。

    Args:
        chapter_result: Gate 3 单章结果。

    Returns:
        当前章节总装问题。

    Raises:
        无显式抛出。
    """

    issues: list[FinalAssemblyIssue] = []
    chapter_id = chapter_result.chapter_id
    if chapter_result.status != "accepted":
        issues.append(
            FinalAssemblyIssue(
                issue_id=f"final_assembly:chapter_{chapter_id}:not_accepted",
                severity="blocking",
                reason="chapter_not_accepted",
                message=f"模板第 {chapter_id} 章状态为 {chapter_result.status}，不能进入完整报告总装。",
                chapter_ids=(chapter_id,),
            )
        )
    if chapter_result.accepted_draft is None:
        issues.append(
            FinalAssemblyIssue(
                issue_id=f"final_assembly:chapter_{chapter_id}:missing_accepted_draft",
                severity="blocking",
                reason="missing_accepted_draft",
                message=f"模板第 {chapter_id} 章缺少 accepted draft。",
                chapter_ids=(chapter_id,),
            )
        )
    if chapter_result.accepted_conclusion is None:
        issues.append(
            FinalAssemblyIssue(
                issue_id=f"final_assembly:chapter_{chapter_id}:missing_accepted_conclusion",
                severity="blocking",
                reason="missing_accepted_conclusion",
                message=f"模板第 {chapter_id} 章缺少 accepted conclusion。",
                chapter_ids=(chapter_id,),
            )
        )
    return tuple(issues)


def _chapter_result_map(result: ChapterOrchestrationResult) -> dict[int, ChapterRunResult]:
    """按章节编号索引 Gate 3 单章结果。

    Args:
        result: Gate 3 总结果。

    Returns:
        章节编号到单章结果的映射；重复章节保留最后一个，重复本身由校验报告。

    Raises:
        无显式抛出。
    """

    return {chapter_result.chapter_id: chapter_result for chapter_result in result.chapter_results}


def _build_chapter7_summary(
    decision: FinalJudgmentDecision,
    body_conclusions: tuple[AcceptedChapterConclusion, ...],
    readiness: FinalAssemblyReadiness,
) -> FinalChapter7Summary | None:
    """构造第 7 章 typed 摘要，不重新派生最终判断。

    Args:
        decision: Agent/Fund 层已派生的最终判断。
        body_conclusions: Gate 3 第 1-6 章 accepted conclusions。
        readiness: 第 7 章 required-body readiness。

    Returns:
        第 7 章 typed 摘要；readiness 未 ready 时返回 `None`。

    Raises:
        无显式抛出。
    """

    if readiness.status != "ready" or not readiness.chapter7_ready:
        return None
    basis = _chapter7_core_basis(decision, body_conclusions)
    return FinalChapter7Summary(
        selected_judgment=decision.selected_judgment,
        selected_judgment_label=_JUDGMENT_LABELS[decision.selected_judgment],
        core_basis=basis,
        easiest_misread=_easiest_misread(decision, body_conclusions),
        next_validation_plan=_next_validation_plan(decision, body_conclusions),
        threshold_events=_threshold_events(decision),
        readiness_status=readiness.status,
        evidence_status=readiness.evidence_status,
        accepted_body_chapter_ids=readiness.accepted_body_chapter_ids,
        source=decision.source,
        conflict_reasons=decision.conflict_reasons,
    )


def _validate_chapter7_summary(
    summary: FinalChapter7Summary,
    readiness: FinalAssemblyReadiness,
) -> tuple[FinalAssemblyIssue, ...]:
    """校验第 7 章 typed bundle 与 required-body readiness 一致。

    Args:
        summary: 第 7 章 typed 摘要。
        readiness: 第 7 章 readiness。

    Returns:
        阻断问题；无问题时为空元组。

    Raises:
        无显式抛出。
    """

    if (
        summary.readiness_status == readiness.status
        and summary.evidence_status == readiness.evidence_status
        and summary.accepted_body_chapter_ids == readiness.accepted_body_chapter_ids
    ):
        return ()
    return (
        FinalAssemblyIssue(
            issue_id="final_assembly:chapter_7:readiness_mismatch",
            severity="blocking",
            reason="chapter7_readiness_mismatch",
            message="第 7 章 typed bundle 的 readiness/evidence 状态与 required-body readiness 不一致。",
            chapter_ids=(CHAPTER7_ID, *readiness.required_body_chapter_ids),
        ),
    )


def _chapter7_core_basis(
    decision: FinalJudgmentDecision,
    body_conclusions: tuple[AcceptedChapterConclusion, ...],
) -> tuple[str, ...]:
    """合成第 7 章核心依据，合并规则 reasons 与既有章节短句。

    Args:
        decision: 最终判断决策。
        body_conclusions: Gate 3 第 1-6 章 accepted conclusions。

    Returns:
        1-2 条核心依据短句。

    Raises:
        无显式抛出。
    """

    basis: list[str] = []
    if decision.reasons:
        basis.append(f"规则依据：{decision.reasons[0]}")
    snippets = _supporting_conclusion_snippets(body_conclusions)
    if snippets:
        basis.append("章节结论语境：" + "；".join(snippets))
    if not basis:
        basis.append("缺少可压缩为核心依据的 accepted conclusions，需回看第 1-6 章。")
    return tuple(basis[:2])


def _supporting_conclusion_snippets(
    conclusions: tuple[AcceptedChapterConclusion, ...],
) -> tuple[str, ...]:
    """从 accepted conclusions 中截取支撑短句。

    Args:
        conclusions: Gate 3 accepted conclusions。

    Returns:
        按章节顺序排列的短句。

    Raises:
        无显式抛出。
    """

    snippets: list[str] = []
    for conclusion in conclusions:
        first_line = _first_non_empty_line(conclusion.conclusion_markdown)
        if not first_line:
            continue
        snippets.append(f"第 {conclusion.chapter_id} 章：{_strip_markdown_bullet(first_line)}")
        if len(snippets) >= _SUPPORTING_SNIPPET_CHAPTER_LIMIT:
            break
    return tuple(snippets)


def _easiest_misread(
    decision: FinalJudgmentDecision,
    body_conclusions: tuple[AcceptedChapterConclusion, ...],
) -> str:
    """生成第 7 章“当前最容易看错的地方”。

    Args:
        decision: 最终判断决策。
        body_conclusions: Gate 3 第 1-6 章 accepted conclusions。

    Returns:
        不引入新事实的风险理解提示。

    Raises:
        无显式抛出。
    """

    if decision.conflict_reasons:
        return "开发覆盖与系统派生判断存在冲突，必须先复核覆盖原因与系统规则信号。"
    if decision.reasons:
        return f"容易把规则信号当成完整事实结论；当前应回到原章节核对：{decision.reasons[0]}"
    risk_line = _conclusion_line_for_chapter(body_conclusions, 6)
    if risk_line:
        return f"容易低估第 6 章风险章节已经提示的问题：{_strip_markdown_bullet(risk_line)}"
    return "缺少可压缩风险结论，最容易看错的是把数据不足误当成风险已经排除。"


def _next_validation_plan(
    decision: FinalJudgmentDecision,
    body_conclusions: tuple[AcceptedChapterConclusion, ...],
) -> str:
    """生成第 7 章下一轮最小验证计划。

    Args:
        decision: 最终判断决策。
        body_conclusions: Gate 3 第 1-6 章 accepted conclusions。

    Returns:
        下一轮最小验证计划文本。

    Raises:
        无显式抛出。
    """

    if decision.reasons:
        return f"优先验证最终判断触发项是否仍成立：{decision.reasons[0]}"
    risk_line = _conclusion_line_for_chapter(body_conclusions, 6)
    if risk_line:
        return f"优先回看第 6 章主要风险是否已有新披露：{_strip_markdown_bullet(risk_line)}"
    return "先补齐第 1-6 章 accepted conclusion 中缺少的关键验证问题。"


def _threshold_events(decision: FinalJudgmentDecision) -> tuple[str, ...]:
    """生成第 7 章升级/降级阈值，不新增具体数值。

    Args:
        decision: 最终判断决策。

    Returns:
        阈值事件文本。

    Raises:
        无显式抛出。
    """

    label = _JUDGMENT_LABELS[decision.selected_judgment]
    return (
        f"升级阈值：后续章节结论与规则依据均支持比 {label} 更低风险的判断。",
        f"降级或终止阈值：后续章节结论出现否决项、质量 gate 阻断或与当前 {label} 相反的规则信号。",
    )


def _render_chapter7_markdown(summary: FinalChapter7Summary) -> str:
    """渲染模板第 7 章 Markdown。

    Args:
        summary: 第 7 章 typed 摘要。

    Returns:
        第 7 章 Markdown。

    Raises:
        无显式抛出。
    """

    basis_lines = "\n".join(f"  - {basis}" for basis in summary.core_basis)
    conflict_lines = _render_conflict_lines(summary)
    threshold_lines = "\n".join(f"  - {event}" for event in summary.threshold_events)
    return (
        f"## 第 7 章：{CHAPTER7_TITLE}\n\n"
        "### 结论要点\n"
        f"- **最终判断**：{summary.selected_judgment_label}\n"
        "- **支撑判断的核心依据**：\n"
        f"{basis_lines}\n"
        f"- **当前最容易看错的地方**：{summary.easiest_misread}\n"
        f"- **下一轮最小验证计划**：{summary.next_validation_plan}\n"
        "- **什么变化会改变判断**：\n"
        f"{threshold_lines}\n"
        f"- **证据/readiness 状态**：{summary.evidence_status}；{summary.readiness_status}；"
        f"accepted_body_chapters={summary.accepted_body_chapter_ids}\n"
        f"{conflict_lines}\n"
    ).strip()


def _render_conflict_lines(summary: FinalChapter7Summary) -> str:
    """渲染 developer override 信息。

    Args:
        summary: 第 7 章 typed 摘要。

    Returns:
        override 相关 Markdown 行；无 override 时为空字符串。

    Raises:
        无显式抛出。
    """

    if summary.source != "developer_override":
        return ""
    conflict_lines = "\n".join(f"  - {reason}" for reason in summary.conflict_reasons)
    if not conflict_lines:
        conflict_lines = "  - 开发覆盖判断与系统派生判断一致。"
    return (
        "\n- **判断来源**：developer_override\n"
        "- **覆盖冲突说明**：\n"
        f"{conflict_lines}"
    )


def _chapter7_accepted_conclusion(summary: FinalChapter7Summary) -> AcceptedChapterConclusion:
    """把第 7 章 typed 摘要转为第 0 章可消费的 accepted conclusion。

    Args:
        summary: 第 7 章 typed 摘要。

    Returns:
        synthetic accepted conclusion。

    Raises:
        无显式抛出。
    """

    basis = "；".join(summary.core_basis)
    threshold = "；".join(summary.threshold_events)
    return AcceptedChapterConclusion(
        chapter_id=CHAPTER7_ID,
        title=CHAPTER7_TITLE,
        conclusion_markdown=(
            f"- **最终判断**：{summary.selected_judgment_label}\n"
            f"- **支撑判断的核心依据**：{basis}\n"
            f"- **当前最容易看错的地方**：{summary.easiest_misread}\n"
            f"- **下一轮最小验证计划**：{summary.next_validation_plan}\n"
            f"- **什么变化会改变判断**：{threshold}\n"
            f"- **证据/readiness 状态**：{summary.evidence_status}；{summary.readiness_status}"
        ),
        conclusion_truncated=False,
        conclusion_source="heading",
        used_fact_ids=(),
        used_anchor_ids=(),
        declared_missing_reasons=(),
        audit_checked_rules=(),
    )


def _render_chapter0_markdown(
    conclusions: tuple[AcceptedChapterConclusion, ...],
    chapter7_summary: FinalChapter7Summary,
    *,
    max_chars: int,
) -> tuple[str, tuple[FinalAssemblyIssue, ...]]:
    """只从 accepted conclusions 和第 7 章 typed 摘要渲染第 0 章。

    Args:
        conclusions: 第 1-7 章 accepted conclusions。
        chapter7_summary: 第 7 章 typed 摘要，用于 typed 当前动作来源。
        max_chars: 第 0 章输出字符硬上限。

    Returns:
        `(第 0 章 Markdown, informational/blocking issues)`。

    Raises:
        无显式抛出。
    """

    issues = list(_chapter0_source_issues(conclusions))
    conclusion_map = {conclusion.chapter_id: conclusion for conclusion in conclusions}
    lines = [
        f"## 第 0 章：{CHAPTER0_TITLE}",
        "",
        "### 一眼看懂",
        f"- **一句话这是什么基金**：{_cover_value(conclusion_map, 1, fallback='见第 1 章产品画像。')}",
        f"- **基金简介**：{_cover_value(conclusion_map, 1, fallback='见第 1 章产品画像。')}",
        f"- **当前动作**：{chapter7_summary.selected_judgment_label}",
        "",
        "### 为什么现在是这个动作",
        (
            "- **当前业绩与运作状态**："
            f"{_first_cover_value(conclusion_map, (2, 4, 5), fallback='见第 2/4/5 章 accepted conclusion，当前缺少可压缩为封面项的结论。')}"
        ),
        f"- **支撑当前动作的最主要理由**：{_first_text(chapter7_summary.core_basis)}",
        (
            "- **当前最值得盯住的变量**："
            f"{_cover_value(conclusion_map, 6, fallback=chapter7_summary.next_validation_plan)}"
        ),
        f"- **当前最大的风险**：{_cover_value(conclusion_map, 6, fallback=chapter7_summary.easiest_misread)}",
        "",
        "### 下一步怎么验证",
        f"- **下一步最小验证问题**：{chapter7_summary.next_validation_plan}",
        (
            "- **什么变化会升级、降级或终止当前动作**："
            f"{'；'.join(chapter7_summary.threshold_events)}"
        ),
    ]
    markdown = "\n".join(lines).strip()
    if len(markdown) > max_chars:
        markdown = markdown[:max_chars].rstrip()
        issues.append(
            FinalAssemblyIssue(
                issue_id="final_assembly:chapter_0:truncated",
                severity="informational",
                reason="chapter0_contract_violation",
                message="模板第 0 章因 max_chapter0_chars 被截断；未补写新事实。",
                chapter_ids=(CHAPTER0_ID,),
            )
        )
    return markdown, tuple(issues)


def _validate_chapter0_action(
    chapter0_markdown: str,
    chapter7_summary: FinalChapter7Summary,
) -> tuple[FinalAssemblyIssue, ...]:
    """校验第 0 章当前动作与第 7 章 typed action 完全一致。

    Args:
        chapter0_markdown: 第 0 章 Markdown。
        chapter7_summary: 第 7 章 typed 摘要。

    Returns:
        阻断问题；动作一致时为空元组。

    Raises:
        无显式抛出。
    """

    expected_line = f"- **当前动作**：{chapter7_summary.selected_judgment_label}"
    if expected_line in chapter0_markdown:
        return ()
    return (
        FinalAssemblyIssue(
            issue_id="final_assembly:chapter_0:action_mismatch",
            severity="blocking",
            reason="chapter0_contract_violation",
            message="第 0 章当前动作必须与第 7 章 typed action 完全一致。",
            chapter_ids=(CHAPTER0_ID, CHAPTER7_ID),
        ),
    )


def _chapter0_source_issues(
    conclusions: tuple[AcceptedChapterConclusion, ...],
) -> tuple[FinalAssemblyIssue, ...]:
    """检查第 0 章 accepted conclusion 来源完整性。

    Args:
        conclusions: 第 0 章可消费的 accepted conclusions。

    Returns:
        第 0 章来源问题。

    Raises:
        无显式抛出。
    """

    ids = {conclusion.chapter_id for conclusion in conclusions}
    issues: list[FinalAssemblyIssue] = []
    if CHAPTER7_ID not in ids:
        issues.append(
            FinalAssemblyIssue(
                issue_id="final_assembly:chapter_0:chapter7_source_missing",
                severity="blocking",
                reason="chapter0_source_missing",
                message="第 0 章缺少第 7 章 accepted conclusion，不能确定当前动作。",
                chapter_ids=(CHAPTER0_ID, CHAPTER7_ID),
            )
        )
    for chapter_id in DEFAULT_REQUIRED_BODY_CHAPTER_IDS:
        conclusion = next((item for item in conclusions if item.chapter_id == chapter_id), None)
        if conclusion is None or not _first_non_empty_line(conclusion.conclusion_markdown):
            issues.append(
                FinalAssemblyIssue(
                    issue_id=f"final_assembly:chapter_0:chapter_{chapter_id}:sparse_source",
                    severity="informational",
                    reason="chapter0_source_sparse",
                    message=f"第 {chapter_id} 章 accepted conclusion 稀疏，第 0 章只能输出回看提示。",
                    chapter_ids=(CHAPTER0_ID, chapter_id),
                )
            )
        elif conclusion.conclusion_truncated:
            issues.append(
                FinalAssemblyIssue(
                    issue_id=f"final_assembly:chapter_0:chapter_{chapter_id}:truncated_source",
                    severity="informational",
                    reason="chapter0_source_sparse",
                    message=f"第 {chapter_id} 章 accepted conclusion 已截断，第 0 章只使用截断后的既有短句。",
                    chapter_ids=(CHAPTER0_ID, chapter_id),
                )
            )
    return tuple(issues)


def _cover_value(
    conclusion_map: dict[int, AcceptedChapterConclusion],
    chapter_id: int,
    *,
    fallback: str,
) -> str:
    """取第 0 章封面项来源短句。

    Args:
        conclusion_map: accepted conclusion 映射。
        chapter_id: 来源章节编号。
        fallback: 缺失时的安全回看提示。

    Returns:
        来源短句或 fallback。

    Raises:
        无显式抛出。
    """

    conclusion = conclusion_map.get(chapter_id)
    if conclusion is None:
        return fallback
    line = _first_non_empty_line(conclusion.conclusion_markdown)
    if not line:
        return fallback
    return _strip_markdown_bullet(line)


def _first_cover_value(
    conclusion_map: dict[int, AcceptedChapterConclusion],
    chapter_ids: tuple[int, ...],
    *,
    fallback: str,
) -> str:
    """按优先级读取第 0 章封面项来源短句。

    Args:
        conclusion_map: accepted conclusion 映射。
        chapter_ids: 候选章节编号。
        fallback: 缺失时的安全回看提示。

    Returns:
        第一个可用来源短句或 fallback。

    Raises:
        无显式抛出。
    """

    for chapter_id in chapter_ids:
        value = _cover_value(conclusion_map, chapter_id, fallback="")
        if value:
            return value
    return fallback


def _conclusion_line_for_chapter(
    conclusions: tuple[AcceptedChapterConclusion, ...],
    chapter_id: int,
) -> str | None:
    """读取指定章节 accepted conclusion 第一行。

    Args:
        conclusions: accepted conclusions。
        chapter_id: 章节编号。

    Returns:
        第一条非空短句；缺失时返回 `None`。

    Raises:
        无显式抛出。
    """

    for conclusion in conclusions:
        if conclusion.chapter_id == chapter_id:
            return _first_non_empty_line(conclusion.conclusion_markdown) or None
    return None


def _first_non_empty_line(text: str) -> str:
    """读取文本第一条非空行。

    Args:
        text: 输入文本。

    Returns:
        第一条非空行；无内容时返回空字符串。

    Raises:
        无显式抛出。
    """

    for line in text.splitlines():
        stripped = line.strip()
        if stripped:
            return stripped
    return ""


def _strip_markdown_bullet(text: str) -> str:
    """去掉 accepted conclusion 短句中的轻量 Markdown 列表前缀。

    Args:
        text: 输入短句。

    Returns:
        清理后的短句。

    Raises:
        无显式抛出。
    """

    stripped = text.strip()
    for prefix in ("- ", "* "):
        if stripped.startswith(prefix):
            return stripped[len(prefix) :].strip()
    return stripped


def _first_text(values: tuple[str, ...]) -> str:
    """读取第一个非空文本。

    Args:
        values: 候选文本。

    Returns:
        第一条非空文本；无内容时返回安全缺口提示。

    Raises:
        无显式抛出。
    """

    for value in values:
        if value.strip():
            return value.strip()
    return "见第 7 章 accepted conclusion，当前缺少可压缩为封面项的结论。"


def _assembled_chapter_ids(policy: FinalAssemblyPolicy) -> tuple[int, ...]:
    """生成最终报告渲染顺序章节编号。

    Args:
        policy: 最终章节总装策略。

    Returns:
        渲染顺序章节编号。

    Raises:
        无显式抛出。
    """

    ids: list[int] = []
    if policy.include_chapter0:
        ids.append(CHAPTER0_ID)
    ids.extend(policy.required_body_chapter_ids)
    if policy.include_chapter7:
        ids.append(CHAPTER7_ID)
    return tuple(ids)


def _render_report_markdown(
    *,
    chapter0_markdown: str | None,
    body_chapter_results: tuple[ChapterRunResult, ...],
    chapter7_markdown: str | None,
    policy: FinalAssemblyPolicy,
) -> str:
    """按 0 -> 1-6 -> 7 顺序渲染完整报告。

    Args:
        chapter0_markdown: 第 0 章 Markdown。
        body_chapter_results: 第 1-6 章 Gate 3 accepted 结果。
        chapter7_markdown: 第 7 章 Markdown。
        policy: 最终章节总装策略。

    Returns:
        完整报告 Markdown。

    Raises:
        ValueError: 当 accepted draft 缺失时抛出。
    """

    parts: list[str] = []
    if policy.include_chapter0 and chapter0_markdown:
        parts.append(chapter0_markdown)
    for chapter_result in body_chapter_results:
        if chapter_result.accepted_draft is None:
            raise ValueError("完整报告渲染要求正文 accepted draft 不为空")
        parts.append(chapter_result.accepted_draft.markdown.strip())
    if policy.include_chapter7 and chapter7_markdown:
        parts.append(chapter7_markdown)
    return "\n\n".join(part for part in parts if part).strip()


def _incomplete_result(
    input_data: FinalChapterAssemblyInput,
    *,
    issues: tuple[FinalAssemblyIssue, ...],
    source_chapter_ids: tuple[int, ...],
) -> FinalChapterAssemblyResult:
    """构造未完成总装结果。

    Args:
        input_data: 最终章节总装输入。
        issues: 阻断或提示问题。
        source_chapter_ids: 已可识别的 accepted conclusion 来源章节。

    Returns:
        incomplete 结果。

    Raises:
        无显式抛出。
    """

    return FinalChapterAssemblyResult(
        status="incomplete",
        fund_code=input_data.fund_code,
        report_year=input_data.report_year,
        report_markdown=None,
        chapter0_markdown=None,
        chapter7_markdown=None,
        chapter7_summary=None,
        assembled_chapter_ids=(),
        source_accepted_chapter_ids=source_chapter_ids,
        final_judgment_selected=input_data.final_judgment_decision.selected_judgment,
        issues=issues,
    )
