"""章节写作 primitive，见基金分析模板第 0-7 章。

本模块属于 Agent 层 `fund_agent/fund` 基金能力，只消费 Gate 1
`ChapterFactProjection` / `ChapterFactInput`。它不读取年报仓库、PDF、cache、
source helper、下载器、parser、Service、Host 或 dayu，也不直接依赖任何真实 LLM
provider SDK。调用方必须显式注入 `ChapterLLMClient`。
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from decimal import Decimal
from typing import Final, Literal, Protocol, get_args

from fund_agent.fund.chapter_facts import (
    ChapterEvidenceAnchor,
    ChapterFactEntry,
    ChapterFactInput,
    ChapterFactMissingReason,
    ChapterFactProjection,
    ChapterFactSchemaVersion,
)

ChapterWriterSchemaVersion = Literal["chapter_writer.v1"]
ChapterWriteStatus = Literal["drafted", "blocked"]
ChapterWriteStopReason = Literal[
    "none",
    "fund_type_unknown",
    "missing_required_facts",
    "evidence_anchor_missing",
    "item_rule_deleted_required_content",
    "chapter_requires_accepted_conclusions",
    "prompt_only",
    "llm_unavailable",
    "llm_empty_response",
    "llm_contract_violation",
]
ChapterWriterMode = Literal["llm", "prompt_only"]
ChapterCitationStyle = Literal["body_quote"]

CHAPTER_WRITER_SCHEMA_VERSION: ChapterWriterSchemaVersion = "chapter_writer.v1"
CHAPTER_LLM_REQUEST_SCHEMA_VERSION: Final[str] = "chapter_llm_request.v1"
CHAPTER_LLM_RESPONSE_SCHEMA_VERSION: Final[str] = "chapter_llm_response.v1"
CHAPTER_WRITER_PROMPT_SCHEMA_VERSION: Final[str] = "chapter_writer_prompt.v1"
CHAPTER_DRAFT_SCHEMA_VERSION: Final[str] = "chapter_draft.v1"
_ANCHOR_MARKER_RE: Final[re.Pattern[str]] = re.compile(r"<!-- anchor:([^<>\s]+) -->")
_MISSING_MARKER_RE: Final[re.Pattern[str]] = re.compile(r"<!-- missing:([a-z_]+) -->")
_COMMENT_RE: Final[re.Pattern[str]] = re.compile(r"<!--\s*([^>]*)-->")
_EVIDENCE_LINE_RE: Final[re.Pattern[str]] = re.compile(r"(?m)^>\s*📎\s*证据：")
_SUPPORTED_MISSING_REASONS: Final[frozenset[str]] = frozenset(get_args(ChapterFactMissingReason))
_CRITICAL_SOURCE_FIELD_IDS: Final[frozenset[str]] = frozenset(
    (
        "structured.nav_benchmark_performance",
        "structured.investor_return",
        "structured.tracking_error",
        "structured.fee_schedule",
        "structured.turnover_rate",
        "structured.share_change",
        "structured.manager_alignment",
        "structured.holder_structure",
        "structured.holdings_snapshot",
        "structured.bond_risk_evidence",
        "structured.nav_data",
    )
)
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


@dataclass(frozen=True, slots=True, kw_only=True)
class ChapterLLMRequest:
    """章节 LLM 写作请求，见模板第 0-7 章。

    Attributes:
        schema_version: 请求 schema 版本。
        chapter_id: 模板章节编号。
        fund_code: 基金代码。
        report_year: 年报年份。
        system_prompt: 系统提示词。
        user_prompt: 用户提示词。
        required_anchor_ids: 允许引用的证据锚点 ID。
        forbidden_phrases: 禁用措辞。
        max_output_chars: 输出字符硬上限。
    """

    schema_version: Literal["chapter_llm_request.v1"] = "chapter_llm_request.v1"
    chapter_id: int
    fund_code: str
    report_year: int
    system_prompt: str
    user_prompt: str
    required_anchor_ids: tuple[str, ...]
    forbidden_phrases: tuple[str, ...]
    max_output_chars: int


@dataclass(frozen=True, slots=True, kw_only=True)
class ChapterLLMResponse:
    """章节 LLM 写作响应，见模板第 0-7 章。

    Attributes:
        schema_version: 响应 schema 版本。
        text: LLM 返回的章节 Markdown。
        model_name: 模型名称；未知时为 `None`。
        finish_reason: provider 返回的结束原因；未知时为 `None`。
    """

    schema_version: Literal["chapter_llm_response.v1"] = "chapter_llm_response.v1"
    text: str
    model_name: str | None
    finish_reason: str | None


class ChapterLLMClient(Protocol):
    """章节写作 LLM client Protocol，见模板第 0-7 章。

    该 Protocol 只定义调用契约，不提供真实 provider 实现。
    """

    def generate_chapter(self, request: ChapterLLMRequest) -> ChapterLLMResponse:
        """生成单章草稿。

        Args:
            request: 章节写作请求。

        Returns:
            章节写作响应。

        Raises:
            由调用方注入的 client 自行定义；本模块不捕获并伪装为成功。
        """


@dataclass(frozen=True, slots=True, kw_only=True)
class ChapterWriterInput:
    """章节写作输入，见模板第 0-7 章。

    Attributes:
        schema_version: writer schema 版本。
        projection_schema_version: Gate 1 投影 schema 版本。
        fund_code: 基金代码。
        report_year: 年报年份。
        chapter: 单章事实输入。
        mode: 写作模式；`prompt_only` 不生成草稿。
        citation_style: 证据引用样式。
        max_output_chars: LLM 输出硬上限。
    """

    schema_version: ChapterWriterSchemaVersion = CHAPTER_WRITER_SCHEMA_VERSION
    projection_schema_version: ChapterFactSchemaVersion
    fund_code: str
    report_year: int
    chapter: ChapterFactInput
    mode: ChapterWriterMode = "llm"
    citation_style: ChapterCitationStyle = "body_quote"
    max_output_chars: int = 12000


@dataclass(frozen=True, slots=True, kw_only=True)
class ChapterWriterPrompt:
    """章节写作 prompt contract，见模板第 0-7 章。

    Attributes:
        schema_version: prompt schema 版本。
        chapter_id: 模板章节编号。
        title: 章节标题。
        system_prompt: 系统提示词。
        user_prompt: 用户提示词。
        must_answer: CHAPTER_CONTRACT 必答项。
        must_not_cover: CHAPTER_CONTRACT 禁止项。
        required_output_items: 必须输出项目。
        allowed_fact_ids: 允许使用的 fact id。
        allowed_anchor_ids: 允许引用的 anchor id。
        deleted_item_rule_ids: 必须删除的 ITEM_RULE id。
        required_gap_phrases: 建议缺口措辞。
    """

    schema_version: Literal["chapter_writer_prompt.v1"] = "chapter_writer_prompt.v1"
    chapter_id: int
    title: str
    system_prompt: str
    user_prompt: str
    must_answer: tuple[str, ...]
    must_not_cover: tuple[str, ...]
    required_output_items: tuple[str, ...]
    allowed_fact_ids: tuple[str, ...]
    allowed_anchor_ids: tuple[str, ...]
    deleted_item_rule_ids: tuple[str, ...]
    required_gap_phrases: tuple[str, ...]


@dataclass(frozen=True, slots=True, kw_only=True)
class ChapterDraft:
    """章节草稿，见模板第 0-7 章。

    Attributes:
        schema_version: 草稿 schema 版本。
        chapter_id: 模板章节编号。
        title: 章节标题。
        markdown: 章节 Markdown。
        used_fact_ids: 已使用 fact id。
        used_anchor_ids: 已引用 anchor id。
        declared_missing_reasons: 草稿显式声明的数据缺口原因。
        deleted_item_rule_ids: 写作时必须删除的 ITEM_RULE id。
        model_name: 写作模型名称。
        finish_reason: 写作模型结束原因。
    """

    schema_version: Literal["chapter_draft.v1"] = "chapter_draft.v1"
    chapter_id: int
    title: str
    markdown: str
    used_fact_ids: tuple[str, ...]
    used_anchor_ids: tuple[str, ...]
    declared_missing_reasons: tuple[ChapterFactMissingReason, ...]
    deleted_item_rule_ids: tuple[str, ...]
    model_name: str | None
    finish_reason: str | None


@dataclass(frozen=True, slots=True, kw_only=True)
class ChapterWriteIssue:
    """章节写作问题，见模板第 0-7 章。

    Attributes:
        issue_id: 稳定 issue id。
        severity: 问题严重程度。
        reason: 阻断原因。
        message: 中文问题说明。
        fact_ids: 相关 fact id。
        anchor_ids: 相关 anchor id。
        item_rule_ids: 相关 ITEM_RULE id。
    """

    issue_id: str
    severity: Literal["blocking", "reviewable"]
    reason: ChapterWriteStopReason
    message: str
    fact_ids: tuple[str, ...] = ()
    anchor_ids: tuple[str, ...] = ()
    item_rule_ids: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True, kw_only=True)
class ChapterWriteResult:
    """章节写作结果，见模板第 0-7 章。

    Attributes:
        schema_version: writer schema 版本。
        status: 写作状态。
        stop_reason: 停止原因。
        prompt: 本次写作 prompt contract。
        draft: 章节草稿；未生成时为 `None`。
        issues: 写作问题列表。
    """

    schema_version: ChapterWriterSchemaVersion = CHAPTER_WRITER_SCHEMA_VERSION
    status: ChapterWriteStatus
    stop_reason: ChapterWriteStopReason
    prompt: ChapterWriterPrompt
    draft: ChapterDraft | None
    issues: tuple[ChapterWriteIssue, ...]


@dataclass(frozen=True, slots=True)
class ChapterWriter:
    """章节写作 façade，见模板第 0-7 章。

    该类不承担 Service 编排、retry、streaming、并发或 provider config。
    """

    def write(
        self,
        input_data: ChapterWriterInput,
        *,
        llm_client: ChapterLLMClient | None,
    ) -> ChapterWriteResult:
        """生成单章草稿或 fail-closed 返回问题。

        Args:
            input_data: 章节写作输入。
            llm_client: 调用方显式注入的 LLM client；可为 `None`。

        Returns:
            章节写作结果。

        Raises:
            无显式抛出；契约问题以 `ChapterWriteIssue` 表达。
        """

        return write_chapter(input_data, llm_client=llm_client)


def build_chapter_writer_input(
    projection: ChapterFactProjection,
    *,
    chapter_id: int,
    mode: ChapterWriterMode = "llm",
    citation_style: ChapterCitationStyle = "body_quote",
    max_output_chars: int = 12000,
) -> ChapterWriterInput:
    """从 Gate 1 投影构造单章写作输入，见模板第 0-7 章。

    Args:
        projection: Gate 1 `ChapterFactProjection`。
        chapter_id: 需要写作的模板章节编号。
        mode: 写作模式。
        citation_style: 证据引用样式。
        max_output_chars: LLM 输出硬上限。

    Returns:
        单章写作输入。

    Raises:
        ValueError: 当章节缺失、重复或参数非法时抛出。
    """

    if mode not in get_args(ChapterWriterMode):
        raise ValueError(f"未知章节写作模式：{mode}")
    if citation_style not in get_args(ChapterCitationStyle):
        raise ValueError(f"未知证据引用样式：{citation_style}")
    if max_output_chars <= 0:
        raise ValueError("max_output_chars 必须为正数")
    return ChapterWriterInput(
        projection_schema_version=projection.schema_version,
        fund_code=projection.fund_code,
        report_year=projection.report_year,
        chapter=_chapter_by_id(projection, chapter_id),
        mode=mode,
        citation_style=citation_style,
        max_output_chars=max_output_chars,
    )


def build_chapter_prompt(input_data: ChapterWriterInput) -> ChapterWriterPrompt:
    """构造章节写作 prompt contract，见模板第 0-7 章。

    Args:
        input_data: 章节写作输入。

    Returns:
        章节写作 prompt。

    Raises:
        无显式抛出。
    """

    chapter = input_data.chapter
    contract = chapter.contract
    allowed_anchor_ids = _allowed_anchor_ids(chapter)
    deleted_item_rule_ids = _deleted_item_rule_ids(chapter)
    system_prompt = (
        "你是基金分析章节写作器。只能使用输入 facts、missing reasons 和 evidence anchors；"
        "不得读取外部资料，不得输出买入/卖出/仓位/收益预测。"
    )
    user_prompt = "\n".join(
        (
            f"章节：{chapter.chapter_id} {chapter.title}",
            f"基金：{input_data.fund_code} / 年报年份：{input_data.report_year}",
            f"基金类型：{chapter.fund_type}",
            f"分类依据：{'; '.join(chapter.classification_basis) or '未披露'}",
            f"preferred_lens：{'; '.join(chapter.lens_resolution.statements) or 'unknown'}",
            "候选 facet 只能写成未断言，不得作为事实："
            + (", ".join(chapter.facet_resolution.non_asserted_facets) or "无"),
            "必须回答：" + _json_text(contract.must_answer),
            "禁止覆盖：" + _json_text(contract.must_not_cover),
            "必须输出项：" + _json_text(contract.required_output_items),
            "允许 facts：" + _json_text(_prompt_fact_payload(chapter.facts)),
            "允许 anchors：" + _json_text(_prompt_anchor_payload(chapter.evidence_anchors)),
            "删除的 ITEM_RULE：" + _json_text(deleted_item_rule_ids),
            "写作要求：每条证据行前后必须包含对应 HTML marker；格式为 "
            "`<!-- anchor:<anchor_id> -->`。声明缺口必须使用 `<!-- missing:<reason> -->`。",
            "可用缺口原因：" + _json_text(chapter.missing_reasons),
        )
    )
    return ChapterWriterPrompt(
        chapter_id=chapter.chapter_id,
        title=chapter.title,
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        must_answer=contract.must_answer,
        must_not_cover=contract.must_not_cover,
        required_output_items=contract.required_output_items,
        allowed_fact_ids=tuple(fact.fact_id for fact in chapter.facts),
        allowed_anchor_ids=allowed_anchor_ids,
        deleted_item_rule_ids=deleted_item_rule_ids,
        required_gap_phrases=("未披露", "数据不足", "下一步最小验证问题"),
    )


def write_chapter(
    input_data: ChapterWriterInput,
    *,
    llm_client: ChapterLLMClient | None,
) -> ChapterWriteResult:
    """生成单章草稿，见模板第 0-7 章。

    Args:
        input_data: 章节写作输入。
        llm_client: 调用方显式注入的 LLM client；`prompt_only` 可为 `None`。

    Returns:
        章节写作结果。任何契约问题都会 fail-closed 返回 `blocked`。

    Raises:
        无显式抛出。
    """

    prompt = build_chapter_prompt(input_data)
    preflight_issues = _preflight_issues(input_data)
    if preflight_issues:
        return _blocked_result(prompt, _stop_reason(preflight_issues), preflight_issues)
    if input_data.mode == "prompt_only":
        return _blocked_result(prompt, "prompt_only", ())
    if llm_client is None:
        issue = _issue(
            "writer:llm_unavailable",
            "llm_unavailable",
            "缺少显式注入的章节写作 LLM client，不能生成章节草稿。",
        )
        return _blocked_result(prompt, "llm_unavailable", (issue,))

    response = llm_client.generate_chapter(_llm_request_from_prompt(input_data, prompt))
    draft, issues = _draft_from_llm_response(input_data, prompt, response)
    if issues:
        return _blocked_result(prompt, _stop_reason(issues), issues)
    if draft is None:
        issue = _issue(
            "writer:llm_contract_violation",
            "llm_contract_violation",
            "LLM 响应未能生成可接受章节草稿。",
        )
        return _blocked_result(prompt, "llm_contract_violation", (issue,))
    return ChapterWriteResult(status="drafted", stop_reason="none", prompt=prompt, draft=draft, issues=())


def _chapter_by_id(projection: ChapterFactProjection, chapter_id: int) -> ChapterFactInput:
    """按章节编号读取唯一章节输入。

    Args:
        projection: Gate 1 章节事实投影。
        chapter_id: 模板章节编号。

    Returns:
        单章事实输入。

    Raises:
        ValueError: 当章节缺失或重复时抛出。
    """

    matches = tuple(chapter for chapter in projection.chapters if chapter.chapter_id == chapter_id)
    if len(matches) != 1:
        raise ValueError(f"章节输入必须唯一：chapter_id={chapter_id}, count={len(matches)}")
    return matches[0]


def _preflight_issues(input_data: ChapterWriterInput) -> tuple[ChapterWriteIssue, ...]:
    """执行写作前 fail-closed 检查。

    Args:
        input_data: 章节写作输入。

    Returns:
        写作前发现的问题。

    Raises:
        无显式抛出。
    """

    chapter = input_data.chapter
    issues: list[ChapterWriteIssue] = []
    if chapter.fund_type == "unknown":
        issues.append(
            _issue("writer:fund_type_unknown", "fund_type_unknown", "基金类型 unknown，禁止类型化写作。")
        )
    if "accepted_chapter_conclusions_missing" in chapter.missing_reasons and chapter.chapter_id in (0, 7):
        issues.append(
            _issue(
                f"writer:chapter_{chapter.chapter_id}:accepted_conclusions_missing",
                "chapter_requires_accepted_conclusions",
                "第 0/7 章需要 accepted chapter conclusions，本 gate 不生成该章。",
            )
        )
    if chapter.facts and all(fact.status != "available" for fact in chapter.facts):
        issues.append(
            _issue(
                f"writer:chapter_{chapter.chapter_id}:missing_required_facts",
                "missing_required_facts",
                "本章结构化 facts 全部不可用，不能生成章节草稿。",
            )
        )
    for fact in chapter.facts:
        if fact.missing_reason == "evidence_missing" and _fact_supports_critical_judgment(fact):
            issues.append(
                _issue(
                    f"writer:{fact.fact_id}:evidence_missing",
                    "evidence_anchor_missing",
                    f"关键 fact 缺少证据锚点：{fact.source_field_name}",
                    fact_ids=(fact.fact_id,),
                )
            )
    for decision in chapter.item_rule_projection.decisions:
        if decision.status == "delete" and decision.item_title in chapter.contract.required_output_items:
            issues.append(
                _issue(
                    f"writer:{decision.rule_id}:deleted_required_item",
                    "item_rule_deleted_required_content",
                    f"ITEM_RULE 要求删除但 required_output_items 仍强依赖：{decision.item_title}",
                    item_rule_ids=(decision.rule_id,),
                )
            )
    return tuple(issues)


def _available_facts(chapter: ChapterFactInput) -> tuple[ChapterFactEntry, ...]:
    """读取可用事实列表。

    Args:
        chapter: 单章事实输入。

    Returns:
        `status="available"` 的事实。

    Raises:
        无显式抛出。
    """

    return tuple(fact for fact in chapter.facts if fact.status == "available")


def _missing_issues(chapter: ChapterFactInput) -> tuple[ChapterWriteIssue, ...]:
    """把章节缺口转换为 reviewable 写作 issue。

    Args:
        chapter: 单章事实输入。

    Returns:
        缺口 issue 列表。

    Raises:
        无显式抛出。
    """

    return tuple(
        _issue(
            f"writer:chapter_{chapter.chapter_id}:missing:{reason}",
            "missing_required_facts",
            f"章节存在数据缺口：{reason}",
        )
        for reason in chapter.missing_reasons
    )


def _fact_supports_critical_judgment(fact: ChapterFactEntry) -> bool:
    """判断缺锚点 fact 是否支撑关键数值或判断。

    Args:
        fact: 章节 fact。

    Returns:
        支撑关键判断时返回 `True`。

    Raises:
        无显式抛出。
    """

    if any(item.startswith(("CHAPTER_CONTRACT.", "ITEM_RULE.")) for item in fact.required_by):
        return True
    if fact.source_field_id in _CRITICAL_SOURCE_FIELD_IDS:
        return True
    return _contains_number(fact.value)


def _contains_number(value: object) -> bool:
    """递归判断值中是否存在数值叶子。

    Args:
        value: 任意结构化值。

    Returns:
        包含数值叶子时返回 `True`。

    Raises:
        无显式抛出。
    """

    if isinstance(value, bool):
        return False
    if isinstance(value, (int, float, Decimal)):
        return True
    if isinstance(value, dict):
        return any(_contains_number(item) for item in value.values())
    if isinstance(value, (tuple, list)):
        return any(_contains_number(item) for item in value)
    return False


def _deleted_item_rule_ids(chapter: ChapterFactInput) -> tuple[str, ...]:
    """读取要求删除的 ITEM_RULE id。

    Args:
        chapter: 单章事实输入。

    Returns:
        status 为 `delete` 的规则编号。

    Raises:
        无显式抛出。
    """

    return tuple(
        decision.rule_id for decision in chapter.item_rule_projection.decisions if decision.status == "delete"
    )


def _allowed_anchor_ids(chapter: ChapterFactInput) -> tuple[str, ...]:
    """读取允许引用的章节锚点 ID。

    Args:
        chapter: 单章事实输入。

    Returns:
        允许引用的 anchor id。

    Raises:
        无显式抛出。
    """

    return tuple(anchor.anchor_id for anchor in chapter.evidence_anchors)


def _forbidden_phrases() -> tuple[str, ...]:
    """读取章节写作禁用措辞，见模板第 0-7 章。

    Args:
        无。

    Returns:
        禁用措辞元组。

    Raises:
        无显式抛出。
    """

    return _FORBIDDEN_PHRASES


def _llm_request_from_prompt(
    input_data: ChapterWriterInput,
    prompt: ChapterWriterPrompt,
) -> ChapterLLMRequest:
    """把 writer prompt 转为 LLM request。

    Args:
        input_data: 章节写作输入。
        prompt: 章节写作 prompt。

    Returns:
        LLM 写作请求。

    Raises:
        无显式抛出。
    """

    return ChapterLLMRequest(
        chapter_id=prompt.chapter_id,
        fund_code=input_data.fund_code,
        report_year=input_data.report_year,
        system_prompt=prompt.system_prompt,
        user_prompt=prompt.user_prompt,
        required_anchor_ids=prompt.allowed_anchor_ids,
        forbidden_phrases=_forbidden_phrases(),
        max_output_chars=input_data.max_output_chars,
    )


def _draft_from_llm_response(
    input_data: ChapterWriterInput,
    prompt: ChapterWriterPrompt,
    response: ChapterLLMResponse,
) -> tuple[ChapterDraft | None, tuple[ChapterWriteIssue, ...]]:
    """解析 LLM 响应为章节草稿。

    Args:
        input_data: 章节写作输入。
        prompt: 章节写作 prompt。
        response: LLM 响应。

    Returns:
        `(draft, issues)`；有 issue 时 draft 为 `None`。

    Raises:
        无显式抛出。
    """

    text = response.text
    issues: list[ChapterWriteIssue] = []
    if not text.strip():
        return None, (
            _issue("writer:llm_empty_response", "llm_empty_response", "LLM 返回空章节文本。"),
        )
    if len(text) > input_data.max_output_chars:
        return None, (
            _issue(
                "writer:llm_response_too_long",
                "llm_contract_violation",
                "LLM 输出超过 max_output_chars，禁止截断或部分接受。",
            ),
        )
    issues.extend(_invalid_marker_issues(text))
    used_anchor_ids, anchor_issues = _parse_anchor_markers(text, prompt, input_data.chapter)
    used_missing_reasons, missing_issues = _parse_missing_markers(text, input_data.chapter)
    issues.extend(anchor_issues)
    issues.extend(missing_issues)
    issues.extend(_evidence_line_issues(text, used_anchor_ids))
    issues.extend(_forbidden_phrase_issues(text))
    if issues:
        return None, tuple(issues)
    draft = ChapterDraft(
        chapter_id=input_data.chapter.chapter_id,
        title=input_data.chapter.title,
        markdown=text,
        used_fact_ids=_used_fact_ids(input_data.chapter, used_anchor_ids, used_missing_reasons),
        used_anchor_ids=used_anchor_ids,
        declared_missing_reasons=used_missing_reasons,
        deleted_item_rule_ids=prompt.deleted_item_rule_ids,
        model_name=response.model_name,
        finish_reason=response.finish_reason,
    )
    return draft, ()


def _invalid_marker_issues(text: str) -> tuple[ChapterWriteIssue, ...]:
    """识别 anchor / missing marker 的非法格式。

    Args:
        text: LLM 输出文本。

    Returns:
        非法 marker issue。

    Raises:
        无显式抛出。
    """

    issues: list[ChapterWriteIssue] = []
    for match in _COMMENT_RE.finditer(text):
        payload = match.group(1)
        if "anchor" in payload.lower() and _ANCHOR_MARKER_RE.fullmatch(match.group(0)) is None:
            issues.append(
                _issue(
                    f"writer:invalid_anchor_marker:{match.start()}",
                    "llm_contract_violation",
                    "anchor marker 格式非法，必须为 `<!-- anchor:<anchor_id> -->`。",
                )
            )
        if "missing" in payload.lower() and _MISSING_MARKER_RE.fullmatch(match.group(0)) is None:
            issues.append(
                _issue(
                    f"writer:invalid_missing_marker:{match.start()}",
                    "llm_contract_violation",
                    "missing marker 格式非法，必须为 `<!-- missing:<reason> -->`。",
                )
            )
    return tuple(issues)


def _parse_anchor_markers(
    text: str,
    prompt: ChapterWriterPrompt,
    chapter: ChapterFactInput,
) -> tuple[tuple[str, ...], tuple[ChapterWriteIssue, ...]]:
    """解析 anchor marker。

    Args:
        text: LLM 输出文本。
        prompt: 章节 prompt。
        chapter: 单章事实输入。

    Returns:
        `(used_anchor_ids, issues)`。

    Raises:
        无显式抛出。
    """

    allowed = set(prompt.allowed_anchor_ids)
    used: list[str] = []
    issues: list[ChapterWriteIssue] = []
    for anchor_id in _ANCHOR_MARKER_RE.findall(text):
        if anchor_id not in allowed:
            issues.append(_unknown_anchor_issue(anchor_id, chapter))
            continue
        if anchor_id not in used:
            used.append(anchor_id)
    return tuple(used), tuple(issues)


def _parse_missing_markers(
    text: str,
    chapter: ChapterFactInput,
) -> tuple[tuple[ChapterFactMissingReason, ...], tuple[ChapterWriteIssue, ...]]:
    """解析 missing marker。

    Args:
        text: LLM 输出文本。
        chapter: 单章事实输入。

    Returns:
        `(declared_missing_reasons, issues)`。

    Raises:
        无显式抛出。
    """

    allowed = set(chapter.missing_reasons)
    used: list[ChapterFactMissingReason] = []
    issues: list[ChapterWriteIssue] = []
    for reason in _MISSING_MARKER_RE.findall(text):
        if reason not in _SUPPORTED_MISSING_REASONS or reason not in allowed:
            issues.append(
                _issue(
                    f"writer:unknown_missing_reason:{reason}",
                    "llm_contract_violation",
                    f"missing marker 引用了未授权缺口原因：{reason}",
                )
            )
            continue
        if reason not in used:
            used.append(reason)  # type: ignore[arg-type]
    return tuple(used), tuple(issues)


def _evidence_line_issues(text: str, used_anchor_ids: tuple[str, ...]) -> tuple[ChapterWriteIssue, ...]:
    """检查证据行是否有对应 anchor marker。

    Args:
        text: LLM 输出文本。
        used_anchor_ids: 已解析的 anchor id。

    Returns:
        证据行 issue。

    Raises:
        无显式抛出。
    """

    if _EVIDENCE_LINE_RE.search(text) and not used_anchor_ids:
        return (
            _issue(
                "writer:evidence_line_without_anchor_marker",
                "llm_contract_violation",
                "正文证据行缺少对应 `<!-- anchor:<anchor_id> -->` marker。",
            ),
        )
    return ()


def _forbidden_phrase_issues(text: str) -> tuple[ChapterWriteIssue, ...]:
    """检查禁用交易建议和越界措辞。

    Args:
        text: LLM 输出文本。

    Returns:
        禁用措辞 issue。

    Raises:
        无显式抛出。
    """

    return tuple(
        _issue(
            f"writer:forbidden_phrase:{index}",
            "llm_contract_violation",
            f"章节草稿包含禁用措辞：{phrase}",
        )
        for index, phrase in enumerate(_FORBIDDEN_PHRASES)
        if phrase in text
    )


def _unknown_anchor_issue(anchor_id: str, chapter: ChapterFactInput) -> ChapterWriteIssue:
    """构造未知 anchor issue。

    Args:
        anchor_id: 未授权锚点 ID。
        chapter: 单章事实输入。

    Returns:
        写作 issue。

    Raises:
        无显式抛出。
    """

    message = f"anchor marker 引用了未授权锚点：{anchor_id}"
    if _looks_like_bond_risk_internal_anchor(anchor_id, chapter):
        message = "bond_risk_evidence 组级锚点未展开为 ChapterEvidenceAnchor，需后续 conversion helper 后才能引用"
    return _issue(
        f"writer:unknown_anchor:{anchor_id}",
        "llm_contract_violation",
        message,
        anchor_ids=(anchor_id,),
    )


def _looks_like_bond_risk_internal_anchor(anchor_id: str, chapter: ChapterFactInput) -> bool:
    """判断锚点是否疑似债券风险内部组级锚点。

    Args:
        anchor_id: 待判断锚点 ID。
        chapter: 单章事实输入。

    Returns:
        疑似内部组级锚点时返回 `True`。

    Raises:
        无显式抛出。
    """

    lowered = anchor_id.lower()
    if any(fragment in lowered for fragment in ("bond", "risk", "credit", "duration")):
        return True
    return any(
        fact.source_field_name == "bond_risk_evidence" and anchor_id in str(fact.value)
        for fact in chapter.facts
    )


def _used_fact_ids(
    chapter: ChapterFactInput,
    used_anchor_ids: tuple[str, ...],
    used_missing_reasons: tuple[ChapterFactMissingReason, ...],
) -> tuple[str, ...]:
    """按 marker 粗略映射草稿使用的 fact id。

    Args:
        chapter: 单章事实输入。
        used_anchor_ids: 草稿引用的 anchor id。
        used_missing_reasons: 草稿声明的缺口原因。

    Returns:
        使用过的 fact id。

    Raises:
        无显式抛出。
    """

    result: list[str] = []
    for fact in chapter.facts:
        if set(fact.evidence_anchor_ids) & set(used_anchor_ids) or fact.missing_reason in used_missing_reasons:
            result.append(fact.fact_id)
    return tuple(result)


def _blocked_result(
    prompt: ChapterWriterPrompt,
    stop_reason: ChapterWriteStopReason,
    issues: tuple[ChapterWriteIssue, ...],
) -> ChapterWriteResult:
    """构造 blocked 写作结果。

    Args:
        prompt: 章节 prompt。
        stop_reason: 停止原因。
        issues: 问题列表。

    Returns:
        blocked 写作结果。

    Raises:
        无显式抛出。
    """

    return ChapterWriteResult(status="blocked", stop_reason=stop_reason, prompt=prompt, draft=None, issues=issues)


def _stop_reason(issues: tuple[ChapterWriteIssue, ...]) -> ChapterWriteStopReason:
    """从 issue 列表提取停止原因。

    Args:
        issues: 写作 issue。

    Returns:
        第一条 issue 的原因；无 issue 时返回 `none`。

    Raises:
        无显式抛出。
    """

    return issues[0].reason if issues else "none"


def _issue(
    issue_id: str,
    reason: ChapterWriteStopReason,
    message: str,
    *,
    fact_ids: tuple[str, ...] = (),
    anchor_ids: tuple[str, ...] = (),
    item_rule_ids: tuple[str, ...] = (),
) -> ChapterWriteIssue:
    """构造章节写作 issue。

    Args:
        issue_id: 稳定 issue id。
        reason: 停止原因。
        message: 中文问题说明。
        fact_ids: 相关 fact id。
        anchor_ids: 相关 anchor id。
        item_rule_ids: 相关 ITEM_RULE id。

    Returns:
        写作 issue。

    Raises:
        无显式抛出。
    """

    return ChapterWriteIssue(
        issue_id=issue_id,
        severity="blocking",
        reason=reason,
        message=message,
        fact_ids=fact_ids,
        anchor_ids=anchor_ids,
        item_rule_ids=item_rule_ids,
    )


def _prompt_fact_payload(facts: tuple[ChapterFactEntry, ...]) -> tuple[dict[str, object], ...]:
    """把 facts 转为 prompt 负载。

    Args:
        facts: 章节 facts。

    Returns:
        可 JSON 序列化的 prompt fact 列表。

    Raises:
        无显式抛出。
    """

    return tuple(
        {
            "fact_id": fact.fact_id,
            "source_field_id": fact.source_field_id,
            "source_field_name": fact.source_field_name,
            "status": fact.status,
            "value": _jsonable_value(fact.value),
            "evidence_anchor_ids": fact.evidence_anchor_ids,
            "missing_reason": fact.missing_reason,
            "required_by": fact.required_by,
        }
        for fact in facts
    )


def _prompt_anchor_payload(anchors: tuple[ChapterEvidenceAnchor, ...]) -> tuple[dict[str, object], ...]:
    """把 anchors 转为 prompt 负载。

    Args:
        anchors: 章节证据锚点。

    Returns:
        可 JSON 序列化的锚点列表。

    Raises:
        无显式抛出。
    """

    return tuple(
        {
            "anchor_id": anchor.anchor_id,
            "source_kind": anchor.source_kind,
            "document_year": anchor.document_year,
            "section_id": anchor.section_id,
            "table_id": anchor.table_id,
            "row_locator": anchor.row_locator,
            "note": anchor.note,
        }
        for anchor in anchors
    )


def _jsonable_value(value: object) -> object:
    """用保守策略序列化任意 fact value。

    Args:
        value: 原始结构化值。

    Returns:
        JSON 可消费值；复杂对象回退为字符串。

    Raises:
        无显式抛出。
    """

    try:
        json.dumps(value, ensure_ascii=False, default=str)
    except TypeError:
        return str(value)
    return value


def _json_text(value: object) -> str:
    """输出稳定 JSON 文本。

    Args:
        value: 待序列化对象。

    Returns:
        JSON 字符串。

    Raises:
        无显式抛出。
    """

    return json.dumps(value, ensure_ascii=False, default=str, sort_keys=True)
