"""章节审计 primitive，见基金分析模板第 0-7 章。

本模块属于 Agent 层 `fund_agent/fund` 基金能力，只消费 Gate 2
`ChapterWriterInput` / `ChapterDraft` 以及 Gate 1 的章节事实输入。它不读取
年报仓库、PDF、cache、source helper、下载器、parser、Service、Host 或 dayu。
E2 证据与断言源文核验显式延后到后续 Evidence Confirm gate。
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from typing import Final, Literal, Protocol

from fund_agent.fund.chapter_writer import (
    ChapterDraft,
    ChapterWriterInput,
)

ChapterAuditSchemaVersion = Literal["chapter_audit.v1"]
ChapterAuditLayer = Literal["programmatic", "llm"]
ChapterAuditStatus = Literal["pass", "fail", "blocked"]
ChapterAuditSeverity = Literal["blocking", "reviewable", "informational"]
ChapterAuditRuleCode = Literal[
    "P1",
    "P2",
    "E1",
    "E2",
    "E3",
    "C1",
    "C2",
    "L1",
    "L2",
    "R1",
    "R2",
    "LLM_UNAVAILABLE",
]
ChapterAuditRepairHint = Literal["none", "patch", "regenerate", "needs_more_facts"]

CHAPTER_AUDIT_SCHEMA_VERSION: ChapterAuditSchemaVersion = "chapter_audit.v1"
CHAPTER_AUDIT_LLM_REQUEST_SCHEMA_VERSION: Final[str] = "chapter_audit_llm_request.v1"
CHAPTER_AUDIT_LLM_RESPONSE_SCHEMA_VERSION: Final[str] = "chapter_audit_llm_response.v1"
DEFAULT_AUDIT_FOCUS: Final[tuple[str, ...]] = (
    "evidence_support",
    "must_not_cover_boundary",
    "missing_semantics",
    "readability",
    "non_asserted_facet_boundary",
)
_REPAIR_HINT_ORDER: Final[dict[ChapterAuditRepairHint, int]] = {
    "none": 0,
    "patch": 1,
    "regenerate": 2,
    "needs_more_facts": 3,
}
_PLACEHOLDER_PATTERNS: Final[tuple[str, ...]] = ("[基金类型]", "X.XX%", "[列出")
_FORBIDDEN_PHRASES: Final[tuple[str, ...]] = (
    "建议买入",
    "可以买入",
    "立即买入",
    "建议卖出",
    "应该卖出",
    "清仓",
    "加仓",
    "减仓",
    "仓位比例",
    "目标价",
    "预测收益",
    "基金经理动机",
)
_EVIDENCE_LINE_RE: Final[re.Pattern[str]] = re.compile(r"(?m)^>\s*📎\s*证据：")
_CHAPTER5_ASSERTION_PHRASES: Final[tuple[str, ...]] = (
    "风格稳定",
    "风格保持稳定",
    "风格一致",
    "风格延续",
    "言行一致",
    "投资框架稳定",
    "没有明显变化",
    "变化不大",
    "持续改善",
    "明显漂移",
    "发生转型",
    "阶段切换",
    "相比上一期",
    "过去一年变化",
)
_CHAPTER5_NEGATION_PREFIXES: Final[tuple[str, ...]] = (
    "不判断",
    "不能判断",
    "无法判断",
    "不足以判断",
    "不能据此判断",
    "证据不足",
    "数据不足",
    "缺少跨期",
    "未披露上期",
)
_QUESTION_PREFIXES: Final[tuple[str, ...]] = ("是否", "能否", "下一步验证")
_NON_ASSERTED_QUALIFIERS: Final[tuple[str, ...]] = (
    "未断言",
    "未确认",
    "候选",
    "可能",
    "不可据此判断",
    "不能据此判断",
    "仅为 lens 候选",
)
_MUST_NOT_COVER_PREFIX_RE: Final[re.Pattern[str]] = re.compile(r"^不(?:得|要)?(?:把|将)?(?:本章)?(?:写成|展开|分析|覆盖|输出|拆成)?")
_MUST_NOT_COVER_PARENS_RE: Final[re.Pattern[str]] = re.compile(r"[（(][^（）()]*[）)]")
_MUST_NOT_COVER_SPLIT_RE: Final[re.Pattern[str]] = re.compile(r"[，。、；;：:/]|或|和|及|与")
_MUST_NOT_COVER_STOPWORDS: Final[tuple[str, ...]] = (
    "属于第",
    "属于",
    "本报告范围内",
    "本报告范围",
    "后续章节",
    "基金",
    "分析",
    "详细",
    "并列",
    "默认",
    "只写",
    "只保留",
    "小节",
)
_NUMERICAL_CLOSURE_RE: Final[re.Pattern[str]] = re.compile(
    r"(?:A\s*=\s*R\s*-\s*B|A\s*-\s*C|R\s*=\s*A\s*\+\s*B\s*-\s*C|R=A\+B-C)"
)
_NUMERIC_TEXT_RE: Final[re.Pattern[str]] = re.compile(r"\d+(?:\.\d+)?\s*%")
_ANCHOR_MARKER_TEXT: Final[str] = "<!-- anchor:"


@dataclass(frozen=True, slots=True, kw_only=True)
class ChapterAuditLLMRequest:
    """章节 LLM 审计请求，见模板第 0-7 章。

    Attributes:
        schema_version: 请求 schema 版本。
        chapter_id: 模板章节编号。
        fund_code: 基金代码。
        report_year: 年报年份。
        system_prompt: 系统提示词。
        user_prompt: 用户提示词。
        draft_markdown: 待审计章节 Markdown。
        allowed_fact_ids: 允许使用的 fact id。
        allowed_anchor_ids: 允许引用的 anchor id。
        audit_focus: 审计关注点。
    """

    schema_version: Literal["chapter_audit_llm_request.v1"] = "chapter_audit_llm_request.v1"
    chapter_id: int
    fund_code: str
    report_year: int
    system_prompt: str
    user_prompt: str
    draft_markdown: str
    allowed_fact_ids: tuple[str, ...]
    allowed_anchor_ids: tuple[str, ...]
    audit_focus: tuple[str, ...]


@dataclass(frozen=True, slots=True, kw_only=True)
class ChapterAuditLLMResponse:
    """章节 LLM 审计响应，见模板第 0-7 章。

    Attributes:
        schema_version: 响应 schema 版本。
        raw_text: LLM 返回的行协议文本。
        model_name: 模型名称；未知时为 `None`。
        finish_reason: provider 返回的结束原因；未知时为 `None`。
    """

    schema_version: Literal["chapter_audit_llm_response.v1"] = "chapter_audit_llm_response.v1"
    raw_text: str
    model_name: str | None
    finish_reason: str | None


class ChapterAuditLLMClient(Protocol):
    """章节审计 LLM client Protocol，见模板第 0-7 章。"""

    def audit_chapter(self, request: ChapterAuditLLMRequest) -> ChapterAuditLLMResponse:
        """审计单章草稿。

        Args:
            request: 章节审计请求。

        Returns:
            章节审计响应。

        Raises:
            由调用方注入的 client 自行定义；本模块不捕获并伪装为成功。
        """


@dataclass(frozen=True, slots=True, kw_only=True)
class ChapterAuditInput:
    """章节审计输入，见模板第 0-7 章。

    Attributes:
        schema_version: 审计 schema 版本。
        writer_input: 写作输入。
        draft: 待审计草稿。
        run_programmatic: 是否执行程序审计。
        run_llm: 是否执行 LLM 审计。
    """

    schema_version: ChapterAuditSchemaVersion = CHAPTER_AUDIT_SCHEMA_VERSION
    writer_input: ChapterWriterInput
    draft: ChapterDraft
    run_programmatic: bool = True
    run_llm: bool = True


@dataclass(frozen=True, slots=True, kw_only=True)
class ChapterAuditIssue:
    """章节审计 issue，见模板第 0-7 章。

    Attributes:
        issue_id: 稳定 issue id。
        layer: 审计层。
        rule_code: 审计规则码。
        severity: 严重程度。
        message: 中文问题说明。
        location: 问题位置。
        fact_ids: 相关 fact id。
        anchor_ids: 相关 anchor id。
        item_rule_ids: 相关 ITEM_RULE id。
        repair_hint: 修复建议。
    """

    issue_id: str
    layer: ChapterAuditLayer
    rule_code: ChapterAuditRuleCode
    severity: ChapterAuditSeverity
    message: str
    location: str | None
    fact_ids: tuple[str, ...] = ()
    anchor_ids: tuple[str, ...] = ()
    item_rule_ids: tuple[str, ...] = ()
    repair_hint: ChapterAuditRepairHint = "none"


@dataclass(frozen=True, slots=True, kw_only=True)
class ChapterProgrammaticAuditResult:
    """章节程序审计结果，见模板第 0-7 章。

    Attributes:
        status: 审计状态。
        issues: 程序审计 issue。
        checked_rules: 已检查规则码。
    """

    status: ChapterAuditStatus
    issues: tuple[ChapterAuditIssue, ...]
    checked_rules: tuple[ChapterAuditRuleCode, ...]


@dataclass(frozen=True, slots=True, kw_only=True)
class ChapterLLMAuditResult:
    """章节 LLM 审计结果，见模板第 0-7 章。

    Attributes:
        status: 审计状态。
        issues: LLM 审计 issue。
        raw_response: 原始 LLM 响应。
        model_name: 模型名称。
        finish_reason: 模型结束原因。
    """

    status: ChapterAuditStatus
    issues: tuple[ChapterAuditIssue, ...]
    raw_response: str | None
    model_name: str | None
    finish_reason: str | None


@dataclass(frozen=True, slots=True, kw_only=True)
class ChapterAuditResult:
    """章节审计汇总结果，见模板第 0-7 章。

    Attributes:
        schema_version: 审计 schema 版本。
        status: 汇总状态。
        programmatic: 程序审计结果。
        llm: LLM 审计结果。
        accepted: 是否接受章节。
        repair_hint: 聚合修复建议。
    """

    schema_version: ChapterAuditSchemaVersion = CHAPTER_AUDIT_SCHEMA_VERSION
    status: ChapterAuditStatus
    programmatic: ChapterProgrammaticAuditResult
    llm: ChapterLLMAuditResult
    accepted: bool
    repair_hint: ChapterAuditRepairHint


@dataclass(frozen=True, slots=True)
class ChapterAuditor:
    """章节审计 façade，见模板第 0-7 章。"""

    def audit(
        self,
        input_data: ChapterAuditInput,
        *,
        llm_client: ChapterAuditLLMClient | None,
    ) -> ChapterAuditResult:
        """审计单章草稿。

        Args:
            input_data: 章节审计输入。
            llm_client: 调用方显式注入的 LLM 审计 client。

        Returns:
            章节审计汇总结果。

        Raises:
            无显式抛出。
        """

        return audit_chapter(input_data, llm_client=llm_client)


def audit_chapter_programmatic(input_data: ChapterAuditInput) -> ChapterProgrammaticAuditResult:
    """执行确定性章节程序审计，见模板第 0-7 章。

    Args:
        input_data: 章节审计输入。

    Returns:
        程序审计结果。

    Raises:
        无显式抛出。
    """

    issues = (
        *_audit_structure(input_data),
        *_audit_placeholders(input_data),
        *_audit_anchor_refs(input_data),
        *_audit_contract_markers(input_data),
        *_audit_must_not_cover(input_data),
        *_audit_item_rule_deleted_sections(input_data),
        *_audit_non_asserted_facets(input_data),
        *_audit_forbidden_content(input_data),
        *_audit_numerical_closure(input_data),
        *_audit_missing_semantics(input_data),
    )
    return ChapterProgrammaticAuditResult(
        status="fail" if issues else "pass",
        issues=issues,
        checked_rules=("P1", "P2", "E1", "E3", "C1", "C2", "L1", "R1", "R2"),
    )


def audit_chapter_llm(
    input_data: ChapterAuditInput,
    *,
    llm_client: ChapterAuditLLMClient | None,
) -> ChapterLLMAuditResult:
    """执行章节 LLM 审计，见模板第 0-7 章。

    Args:
        input_data: 章节审计输入。
        llm_client: 调用方显式注入的 LLM 审计 client。

    Returns:
        LLM 审计结果。

    Raises:
        无显式抛出。
    """

    if llm_client is None:
        issue = _issue(
            "llm:unavailable",
            "llm",
            "LLM_UNAVAILABLE",
            "blocking",
            "缺少显式注入的章节 LLM 审计 client。",
            "llm_client",
            repair_hint="regenerate",
        )
        return ChapterLLMAuditResult(
            status="blocked",
            issues=(issue,),
            raw_response=None,
            model_name=None,
            finish_reason=None,
        )
    response = llm_client.audit_chapter(_llm_request(input_data))
    parsed = _parse_llm_audit_response(response)
    return parsed


def audit_chapter(
    input_data: ChapterAuditInput,
    *,
    llm_client: ChapterAuditLLMClient | None,
) -> ChapterAuditResult:
    """执行章节程序审计和可选 LLM 审计，见模板第 0-7 章。

    Args:
        input_data: 章节审计输入。
        llm_client: 调用方显式注入的 LLM 审计 client。

    Returns:
        章节审计汇总结果。

    Raises:
        无显式抛出。
    """

    programmatic = (
        audit_chapter_programmatic(input_data)
        if input_data.run_programmatic
        else ChapterProgrammaticAuditResult(status="pass", issues=(), checked_rules=())
    )
    llm = (
        audit_chapter_llm(input_data, llm_client=llm_client)
        if input_data.run_llm
        else ChapterLLMAuditResult(status="pass", issues=(), raw_response=None, model_name=None, finish_reason=None)
    )
    all_issues = (*programmatic.issues, *llm.issues)
    if programmatic.status == "blocked" or llm.status == "blocked":
        status: ChapterAuditStatus = "blocked"
    elif programmatic.status == "fail" or llm.status == "fail":
        status = "fail"
    else:
        status = "pass"
    return ChapterAuditResult(
        status=status,
        programmatic=programmatic,
        llm=llm,
        accepted=status == "pass",
        repair_hint=_aggregate_repair_hint(all_issues, status),
    )


def _audit_structure(input_data: ChapterAuditInput) -> tuple[ChapterAuditIssue, ...]:
    """审计章节结构。

    Args:
        input_data: 章节审计输入。

    Returns:
        结构问题。

    Raises:
        无显式抛出。
    """

    chapter = input_data.writer_input.chapter
    markdown = input_data.draft.markdown
    issues: list[ChapterAuditIssue] = []
    if input_data.draft.chapter_id != chapter.chapter_id or input_data.draft.title != chapter.title:
        issues.append(_program_issue("P1", "章节编号或标题与 ChapterFactInput 不一致。", "draft"))
    if chapter.chapter_id in range(1, 7):
        for marker in ("结论要点", "详细情况", "证据与出处"):
            if marker not in markdown:
                issues.append(_program_issue("P1", f"第 1-6 章缺少结构段落：{marker}", marker))
    if chapter.chapter_id == 0 and "证据与出处" in markdown:
        issues.append(_program_issue("P1", "第 0 章不得输出证据与出处小节。", "证据与出处"))
    if not markdown.strip():
        issues.append(_program_issue("P2", "章节 Markdown 为空。", "markdown"))
    return tuple(issues)


def _audit_placeholders(input_data: ChapterAuditInput) -> tuple[ChapterAuditIssue, ...]:
    """审计模板占位符残留。

    Args:
        input_data: 章节审计输入。

    Returns:
        占位符问题。

    Raises:
        无显式抛出。
    """

    return tuple(
        _program_issue("P2", f"章节残留模板占位符：{pattern}", pattern)
        for pattern in _PLACEHOLDER_PATTERNS
        if pattern in input_data.draft.markdown
    )


def _audit_anchor_refs(input_data: ChapterAuditInput) -> tuple[ChapterAuditIssue, ...]:
    """审计证据锚点引用。

    Args:
        input_data: 章节审计输入。

    Returns:
        证据锚点问题。

    Raises:
        无显式抛出。
    """

    chapter = input_data.writer_input.chapter
    allowed = {anchor.anchor_id for anchor in chapter.evidence_anchors}
    issues: list[ChapterAuditIssue] = []
    for anchor_id in input_data.draft.used_anchor_ids:
        if anchor_id not in allowed:
            issues.append(
                _program_issue(
                    "E1",
                    f"草稿引用未授权锚点：{anchor_id}",
                    "used_anchor_ids",
                    anchor_ids=(anchor_id,),
                )
            )
    if _EVIDENCE_LINE_RE.search(input_data.draft.markdown) and not input_data.draft.used_anchor_ids:
        issues.append(_program_issue("E1", "正文证据行缺少可解析 anchor marker。", "evidence"))
    for fact in chapter.facts:
        if fact.missing_reason == "evidence_missing" and _fact_used(input_data.draft, fact.fact_id):
            issues.append(
                _program_issue(
                    "E3",
                    f"缺锚点 fact 被用于章节判断：{fact.source_field_name}",
                    fact.fact_id,
                    fact_ids=(fact.fact_id,),
                    repair_hint="needs_more_facts",
                )
            )
    return tuple(issues)


def _audit_contract_markers(input_data: ChapterAuditInput) -> tuple[ChapterAuditIssue, ...]:
    """审计 CHAPTER_CONTRACT required output markers。

    Args:
        input_data: 章节审计输入。

    Returns:
        contract 问题。

    Raises:
        无显式抛出。
    """

    markdown = input_data.draft.markdown
    return tuple(
        _program_issue("C2", f"缺少 required output item marker：{item}", item, repair_hint="patch")
        for item in input_data.writer_input.chapter.contract.required_output_items
        if item and item not in markdown
    )


def _audit_must_not_cover(input_data: ChapterAuditInput) -> tuple[ChapterAuditIssue, ...]:
    """审计 CHAPTER_CONTRACT must_not_cover 明确禁区。

    Args:
        input_data: 章节审计输入。

    Returns:
        must_not_cover 命中问题。

    Raises:
        无显式抛出。
    """

    markdown = input_data.draft.markdown
    issues: list[ChapterAuditIssue] = []
    for clause in input_data.writer_input.chapter.contract.must_not_cover:
        for phrase in _must_not_cover_phrases(clause):
            if phrase in markdown:
                issues.append(
                    _program_issue(
                        "C2",
                        f"章节覆盖了 CHAPTER_CONTRACT must_not_cover 禁区：{phrase}",
                        phrase,
                        repair_hint="patch",
                    )
                )
                break
    return tuple(issues)


def _audit_item_rule_deleted_sections(input_data: ChapterAuditInput) -> tuple[ChapterAuditIssue, ...]:
    """审计 ITEM_RULE 删除段落未被输出。

    Args:
        input_data: 章节审计输入。

    Returns:
        ITEM_RULE 问题。

    Raises:
        无显式抛出。
    """

    markdown = input_data.draft.markdown
    issues: list[ChapterAuditIssue] = []
    for decision in input_data.writer_input.chapter.item_rule_projection.decisions:
        if decision.status != "delete":
            continue
        if decision.item_title in markdown or _deleted_rule_marker_present(decision.rule_id, markdown):
            issues.append(
                _program_issue(
                    "C2",
                    f"ITEM_RULE 要求删除的段落仍出现在草稿中：{decision.item_title}",
                    decision.rule_id,
                    item_rule_ids=(decision.rule_id,),
                    repair_hint="patch",
                )
            )
    return tuple(issues)


def _audit_non_asserted_facets(input_data: ChapterAuditInput) -> tuple[ChapterAuditIssue, ...]:
    """审计 non_asserted_facets 没有被写成已断言事实。

    Args:
        input_data: 章节审计输入。

    Returns:
        facet 误用问题。

    Raises:
        无显式抛出。
    """

    markdown = input_data.draft.markdown
    issues: list[ChapterAuditIssue] = []
    if input_data.writer_input.chapter.facet_resolution.facets:
        return ()
    for facet in input_data.writer_input.chapter.facet_resolution.non_asserted_facets:
        start = 0
        while True:
            index = markdown.find(facet, start)
            if index < 0:
                break
            window = markdown[max(0, index - 12) : index + len(facet) + 12]
            prefix = markdown[max(0, index - 4) : index]
            if not any(qualifier in window for qualifier in _NON_ASSERTED_QUALIFIERS) or any(
                verb in prefix for verb in ("属于", "是", "为", "定位为")
            ):
                issues.append(
                    _program_issue(
                        "C2",
                        f"候选 facet 被写成已断言事实：{facet}",
                        facet,
                        repair_hint="patch",
                    )
                )
            start = index + len(facet)
    return tuple(issues)


def _audit_forbidden_content(input_data: ChapterAuditInput) -> tuple[ChapterAuditIssue, ...]:
    """审计禁用交易建议和越界内容。

    Args:
        input_data: 章节审计输入。

    Returns:
        禁用内容问题。

    Raises:
        无显式抛出。
    """

    return tuple(
        _program_issue("C1", f"章节包含禁用措辞：{phrase}", phrase, repair_hint="regenerate")
        for phrase in _FORBIDDEN_PHRASES
        if phrase in input_data.draft.markdown
    )


def _audit_numerical_closure(input_data: ChapterAuditInput) -> tuple[ChapterAuditIssue, ...]:
    """审计 R=A+B-C 数字闭环断言必须有邻近证据 marker。

    Args:
        input_data: 章节审计输入。

    Returns:
        L1 数字闭环问题。

    Raises:
        无显式抛出。
    """

    lines = input_data.draft.markdown.splitlines()
    issues: list[ChapterAuditIssue] = []
    for index, line in enumerate(lines):
        if not _NUMERICAL_CLOSURE_RE.search(line) or not _NUMERIC_TEXT_RE.search(line):
            continue
        context = "\n".join(lines[max(0, index - 2) : min(len(lines), index + 3)])
        if _ANCHOR_MARKER_TEXT not in context:
            issues.append(
                _program_issue(
                    "L1",
                    "R=A+B-C / A=R-B / A-C 数字闭环断言缺少邻近 anchor marker。",
                    f"line:{index + 1}",
                    repair_hint="patch",
                )
            )
    return tuple(issues)


def _audit_missing_semantics(input_data: ChapterAuditInput) -> tuple[ChapterAuditIssue, ...]:
    """审计缺失语义没有被补写成确定事实。

    Args:
        input_data: 章节审计输入。

    Returns:
        缺失语义问题。

    Raises:
        无显式抛出。
    """

    chapter = input_data.writer_input.chapter
    if chapter.chapter_id != 5 or "cross_period_comparison_missing" not in chapter.missing_reasons:
        return ()
    markdown = input_data.draft.markdown
    issues: list[ChapterAuditIssue] = []
    for phrase in _CHAPTER5_ASSERTION_PHRASES:
        start = 0
        while True:
            index = markdown.find(phrase, start)
            if index < 0:
                break
            prefix = markdown[max(0, index - 12) : index]
            question_prefix = markdown[max(0, index - 6) : index]
            if not any(item in prefix for item in _CHAPTER5_NEGATION_PREFIXES) and not any(
                item in question_prefix for item in _QUESTION_PREFIXES
            ):
                issues.append(
                    _program_issue(
                        "C2",
                        f"缺少跨期比较时输出了确定性跨期断言：{phrase}",
                        phrase,
                        repair_hint="needs_more_facts",
                    )
                )
            start = index + len(phrase)
    return tuple(issues)


def _must_not_cover_phrases(clause: str) -> tuple[str, ...]:
    """从 must_not_cover 契约句抽取可确定匹配的禁止主题短语。

    Args:
        clause: 单条 must_not_cover 契约句。

    Returns:
        可用于正文匹配的短语集合。

    Raises:
        无显式抛出。
    """

    normalized = _MUST_NOT_COVER_PARENS_RE.sub("", clause).strip()
    normalized = _MUST_NOT_COVER_PREFIX_RE.sub("", normalized).strip(" 。")
    phrases: list[str] = []
    for fragment in _MUST_NOT_COVER_SPLIT_RE.split(normalized):
        phrase = _clean_must_not_cover_fragment(fragment)
        if len(phrase) >= 4 and phrase not in phrases:
            phrases.append(phrase)
    return tuple(phrases)


def _clean_must_not_cover_fragment(fragment: str) -> str:
    """清理 must_not_cover 片段中的泛化词。

    Args:
        fragment: 待清理片段。

    Returns:
        清理后的主题短语。

    Raises:
        无显式抛出。
    """

    phrase = fragment.strip(" “”，、。；;：: ")
    for word in _MUST_NOT_COVER_STOPWORDS:
        phrase = phrase.replace(word, "")
    return phrase.strip(" 的地得")


def _llm_request(input_data: ChapterAuditInput) -> ChapterAuditLLMRequest:
    """构造 LLM 审计请求。

    Args:
        input_data: 章节审计输入。

    Returns:
        LLM 审计请求。

    Raises:
        无显式抛出。
    """

    chapter = input_data.writer_input.chapter
    return ChapterAuditLLMRequest(
        chapter_id=chapter.chapter_id,
        fund_code=input_data.writer_input.fund_code,
        report_year=input_data.writer_input.report_year,
        system_prompt="你是基金分析章节审计器，只按固定行协议返回审计结果。",
        user_prompt=(
            "按 SEVERITY|LOCATION|MESSAGE 返回。检查 evidence_support、must_not_cover_boundary、"
            "missing_semantics、readability 和 non_asserted_facet_boundary。"
        ),
        draft_markdown=input_data.draft.markdown,
        allowed_fact_ids=tuple(fact.fact_id for fact in chapter.facts),
        allowed_anchor_ids=tuple(anchor.anchor_id for anchor in chapter.evidence_anchors),
        audit_focus=DEFAULT_AUDIT_FOCUS,
    )


def _parse_llm_audit_response(response: ChapterAuditLLMResponse) -> ChapterLLMAuditResult:
    """解析 LLM 审计行协议。

    Args:
        response: LLM 审计响应。

    Returns:
        LLM 审计结果。

    Raises:
        无显式抛出。
    """

    raw_text = response.raw_text
    lines = tuple(line.strip() for line in raw_text.splitlines() if line.strip())
    if not lines:
        return _llm_parse_failure(raw_text, response.model_name, response.finish_reason)
    if lines == ("PASS|chapter|no issues",):
        return ChapterLLMAuditResult(
            status="pass",
            issues=(),
            raw_response=raw_text,
            model_name=response.model_name,
            finish_reason=response.finish_reason,
        )
    issues: list[ChapterAuditIssue] = []
    for index, line in enumerate(lines):
        parts = line.split("|", 2)
        if len(parts) != 3:
            return _llm_parse_failure(raw_text, response.model_name, response.finish_reason)
        severity_text, location, message = parts
        if not location or not message or severity_text not in ("BLOCKING", "REVIEWABLE", "INFO"):
            return _llm_parse_failure(raw_text, response.model_name, response.finish_reason)
        issues.append(_llm_issue(index, severity_text, location, message))
    status: ChapterAuditStatus = "pass"
    if any(issue.severity == "blocking" for issue in issues):
        status = "fail"
    elif any(issue.severity == "reviewable" for issue in issues):
        status = "fail"
    return ChapterLLMAuditResult(
        status=status,
        issues=tuple(issues),
        raw_response=raw_text,
        model_name=response.model_name,
        finish_reason=response.finish_reason,
    )


def _llm_parse_failure(
    raw_text: str,
    model_name: str | None,
    finish_reason: str | None,
) -> ChapterLLMAuditResult:
    """构造 LLM parse failure 结果。

    Args:
        raw_text: 原始响应。
        model_name: 模型名称。
        finish_reason: 结束原因。

    Returns:
        blocked LLM 审计结果。

    Raises:
        无显式抛出。
    """

    issue = _issue(
        "llm:parse_failure",
        "llm",
        "C1",
        "blocking",
        "LLM audit response parse failure，禁止 silent pass。",
        "raw_response",
        repair_hint="regenerate",
    )
    return ChapterLLMAuditResult(
        status="blocked",
        issues=(issue,),
        raw_response=raw_text,
        model_name=model_name,
        finish_reason=finish_reason,
    )


def _llm_issue(index: int, severity_text: str, location: str, message: str) -> ChapterAuditIssue:
    """构造 LLM 审计 issue。

    Args:
        index: 行号序号。
        severity_text: LLM 行协议严重程度。
        location: 问题位置。
        message: 问题说明。

    Returns:
        LLM 审计 issue。

    Raises:
        无显式抛出。
    """

    if severity_text == "INFO":
        severity: ChapterAuditSeverity = "informational"
        hint: ChapterAuditRepairHint = "none"
    elif severity_text == "REVIEWABLE":
        severity = "reviewable"
        hint = "patch"
    else:
        severity = "blocking"
        hint = "regenerate"
    return _issue(
        f"llm:{index}:{severity_text.lower()}",
        "llm",
        "C1",
        severity,
        message,
        location,
        repair_hint=hint,
    )


def _aggregate_repair_hint(
    issues: tuple[ChapterAuditIssue, ...],
    status: ChapterAuditStatus,
) -> ChapterAuditRepairHint:
    """聚合章节修复建议。

    Args:
        issues: 所有审计 issue。
        status: 汇总审计状态。

    Returns:
        顶层修复建议。

    Raises:
        无显式抛出。
    """

    if not issues:
        return "regenerate" if status == "blocked" else "none"
    return max((issue.repair_hint for issue in issues), key=lambda item: _REPAIR_HINT_ORDER[item])


def _program_issue(
    rule_code: ChapterAuditRuleCode,
    message: str,
    location: str | None,
    *,
    fact_ids: tuple[str, ...] = (),
    anchor_ids: tuple[str, ...] = (),
    item_rule_ids: tuple[str, ...] = (),
    repair_hint: ChapterAuditRepairHint = "patch",
) -> ChapterAuditIssue:
    """构造程序审计 issue。

    Args:
        rule_code: 审计规则码。
        message: 中文问题说明。
        location: 问题位置。
        fact_ids: 相关 fact id。
        anchor_ids: 相关 anchor id。
        item_rule_ids: 相关 ITEM_RULE id。
        repair_hint: 修复建议。

    Returns:
        程序审计 issue。

    Raises:
        无显式抛出。
    """

    return _issue(
        f"programmatic:{rule_code}:{location or 'chapter'}:{_stable_issue_suffix(rule_code, message, location)}",
        "programmatic",
        rule_code,
        "blocking",
        message,
        location,
        fact_ids=fact_ids,
        anchor_ids=anchor_ids,
        item_rule_ids=item_rule_ids,
        repair_hint=repair_hint,
    )


def _issue(
    issue_id: str,
    layer: ChapterAuditLayer,
    rule_code: ChapterAuditRuleCode,
    severity: ChapterAuditSeverity,
    message: str,
    location: str | None,
    *,
    fact_ids: tuple[str, ...] = (),
    anchor_ids: tuple[str, ...] = (),
    item_rule_ids: tuple[str, ...] = (),
    repair_hint: ChapterAuditRepairHint = "none",
) -> ChapterAuditIssue:
    """构造章节审计 issue。

    Args:
        issue_id: 稳定 issue id。
        layer: 审计层。
        rule_code: 审计规则码。
        severity: 严重程度。
        message: 中文问题说明。
        location: 问题位置。
        fact_ids: 相关 fact id。
        anchor_ids: 相关 anchor id。
        item_rule_ids: 相关 ITEM_RULE id。
        repair_hint: 修复建议。

    Returns:
        章节审计 issue。

    Raises:
        无显式抛出。
    """

    return ChapterAuditIssue(
        issue_id=issue_id,
        layer=layer,
        rule_code=rule_code,
        severity=severity,
        message=message,
        location=location,
        fact_ids=fact_ids,
        anchor_ids=anchor_ids,
        item_rule_ids=item_rule_ids,
        repair_hint=repair_hint,
    )


def _stable_issue_suffix(
    rule_code: ChapterAuditRuleCode,
    message: str,
    location: str | None,
) -> str:
    """构造稳定 issue id 后缀。

    Args:
        rule_code: 审计规则码。
        message: 中文问题说明。
        location: 问题位置。

    Returns:
        稳定短 hash 后缀。

    Raises:
        无显式抛出。
    """

    raw = f"{rule_code}|{location or ''}|{message}".encode("utf-8")
    return hashlib.sha1(raw).hexdigest()[:10]


def _deleted_rule_marker_present(rule_id: str, markdown: str) -> bool:
    """判断已删除 ITEM_RULE 的唯一段落 marker 是否存在。

    Args:
        rule_id: ITEM_RULE 编号。
        markdown: 章节 Markdown。

    Returns:
        命中 marker 时返回 `True`。

    Raises:
        无显式抛出。
    """

    markers = {
        "chapter_1_index_constituents": ("指数编制规则与成分股", "跟踪指数"),
        "chapter_1_manager_philosophy": ("基金经理投资哲学", "选股标准"),
        "chapter_2_alpha_yearly_breakdown": ("超额收益分年度拆解", "超额收益稳定性"),
        "chapter_2_tracking_error_analysis": ("跟踪误差分析", "日均偏离度"),
    }
    return any(marker in markdown for marker in markers.get(rule_id, ()))


def _fact_used(draft: ChapterDraft, fact_id: str) -> bool:
    """判断草稿是否声明使用了某个 fact。

    Args:
        draft: 章节草稿。
        fact_id: fact id。

    Returns:
        使用时返回 `True`。

    Raises:
        无显式抛出。
    """

    return fact_id in draft.used_fact_ids
