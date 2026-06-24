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
from typing import Final, Literal, Protocol, cast, get_args

from fund_agent.fund.chapter_facts import (
    ChapterEvidenceAnchor,
    ChapterFactEntry,
    ChapterFactInput,
    ChapterFactMissingReason,
    ChapterFactProjection,
    ChapterFactSchemaVersion,
)
from fund_agent.fund.evidence_availability import (
    AvailabilityStatus,
    EvidenceAvailability,
    EvidenceRequirementId,
    RequirementAvailability,
)
from fund_agent.fund.template.typed_contracts import (
    MissingEvidenceBehavior,
    RequiredOutputItem,
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
    "missing_required_structure",
    "missing_required_output_marker",
    "unknown_anchor",
    "response_too_long",
    "response_incomplete",
]
ChapterWriterMode = Literal["llm", "prompt_only"]
ChapterCitationStyle = Literal["body_quote"]
ChapterPromptPayloadMode = Literal["full", "compact"]

CHAPTER_WRITER_SCHEMA_VERSION: ChapterWriterSchemaVersion = "chapter_writer.v1"
CHAPTER_LLM_REQUEST_SCHEMA_VERSION: Final[str] = "chapter_llm_request.v1"
CHAPTER_LLM_RESPONSE_SCHEMA_VERSION: Final[str] = "chapter_llm_response.v1"
CHAPTER_WRITER_PROMPT_SCHEMA_VERSION: Final[str] = "chapter_writer_prompt.v1"
CHAPTER_DRAFT_SCHEMA_VERSION: Final[str] = "chapter_draft.v1"
CHAPTER_PROMPT_COST_DIAGNOSTIC_SCHEMA_VERSION: Final[str] = (
    "chapter_prompt_cost_diagnostic_payload.v1"
)
_COMPACT_VALUE_CHAR_THRESHOLD: Final[int] = 1200
_ANCHOR_MARKER_RE: Final[re.Pattern[str]] = re.compile(r"<!-- anchor:([^<>\s]+) -->")
_MISSING_MARKER_RE: Final[re.Pattern[str]] = re.compile(r"<!-- missing:([a-z_]+) -->")
_COMMENT_RE: Final[re.Pattern[str]] = re.compile(r"<!--\s*([^>]*)-->")
_EVIDENCE_LINE_RE: Final[re.Pattern[str]] = re.compile(r"(?m)^>\s*📎\s*证据：")
_SUPPORTED_MISSING_REASONS: Final[frozenset[str]] = frozenset(get_args(ChapterFactMissingReason))
REQUIRED_BODY_SECTION_HEADINGS: Final[tuple[str, ...]] = (
    "### 结论要点",
    "### 详细情况",
    "### 证据与出处",
)
REQUIRED_OUTPUT_MARKER_PREFIX: Final[str] = "<!-- required_output:"
INCOMPLETE_FINISH_REASONS: Final[frozenset[str]] = frozenset(
    ("length", "max_tokens", "content_filter")
)
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
_MISSING_EVIDENCE_STATUSES: Final[frozenset[AvailabilityStatus]] = frozenset(
    ("missing", "unavailable", "not_applicable", "unreviewed")
)
_GAP_OUTPUT_PHRASES: Final[tuple[str, ...]] = (
    "证据不足",
    "数据不足",
    "未披露",
    "缺少",
    "不可用",
    "未复核",
    "无法判断",
    "不能据此判断",
)
_VERIFICATION_OUTPUT_PHRASES: Final[tuple[str, ...]] = (
    "下一步最小验证问题",
    "最小验证问题",
    "需要验证",
    "后续验证",
    "下一步验证",
)


@dataclass(frozen=True, slots=True, kw_only=True)
class RequiredOutputEvidencePlan:
    """typed required output 缺证写作计划，见模板第 2/3 章。

    Attributes:
        item_id: typed required output item id。
        text: required output 原始展示文本。
        marker: writer 要求输出的 exact marker。
        availability_status: 同源证据可用性；无 requirement 时为 `None`。
        when_evidence_missing: typed 缺证行为。
        missing_evidence_reason: reviewed typed 缺证原因。
        action: writer 对该项采取的动作。
        prompt_instruction: 传给 writer 的安全输出说明。
        requirement_fact_ids: 关联 availability fact ids。
        requirement_anchor_ids: 关联 availability anchor ids。
    """

    item_id: str
    text: str
    marker: str
    availability_status: AvailabilityStatus | None
    when_evidence_missing: MissingEvidenceBehavior | None
    missing_evidence_reason: str | None
    action: Literal["render", "render_evidence_gap", "render_minimum_verification_question", "delete", "block"]
    prompt_instruction: str
    requirement_fact_ids: tuple[str, ...] = ()
    requirement_anchor_ids: tuple[str, ...] = ()


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
        repair_context: 可选重写上下文。
        prompt_cost_diagnostic: writer prompt-cost 安全诊断；不含 prompt 文本。
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
    repair_context: ChapterRepairContext | None = None
    prompt_cost_diagnostic: ChapterPromptCostDiagnostic | None = None


@dataclass(frozen=True, slots=True, kw_only=True)
class ChapterRepairContext:
    """章节重写上下文，见模板第 1-6 章 write-audit-repair。

    Attributes:
        attempt_index: 本次重写 attempt 序号。
        previous_issue_ids: 上一轮审计 issue id。
        previous_messages: 上一轮审计 issue 脱敏消息。
        required_corrections: 本轮必须完成的确定性修正项。
    """

    attempt_index: int
    previous_issue_ids: tuple[str, ...]
    previous_messages: tuple[str, ...]
    required_corrections: tuple[str, ...]


@dataclass(frozen=True, slots=True, kw_only=True)
class ChapterPromptComponentCosts:
    """writer prompt 组件字符成本，见模板第 1-6 章写作路径。

    Attributes:
        protocol_chars: 输出协议与安全边界字符数。
        contract_chars: 章节身份、fund type、lens、facet 与 ITEM_RULE 字符数。
        must_answer_chars: CHAPTER_CONTRACT.must_answer 字符数。
        must_not_cover_chars: CHAPTER_CONTRACT.must_not_cover 字符数。
        required_output_chars: required_output_items 字符数。
        facts_chars: facts payload 字符数。
        anchors_chars: anchors payload 字符数。
        repair_context_chars: repair context 字符数。
    """

    protocol_chars: int
    contract_chars: int
    must_answer_chars: int
    must_not_cover_chars: int
    required_output_chars: int
    facts_chars: int
    anchors_chars: int
    repair_context_chars: int


@dataclass(frozen=True, slots=True, kw_only=True)
class ChapterPromptFactCostRow:
    """writer prompt fact 成本行，见模板 CHAPTER_CONTRACT 输入。

    Attributes:
        fact_id: fact id。
        source_field_id: 稳定来源字段 ID。
        status: fact 状态。
        missing_reason: 缺失原因；可为 `None`。
        value_chars: 原始 value 的安全序列化字符数。
        serialized_fact_chars: 实际 prompt fact 行字符数。
        evidence_anchor_count: fact 引用的证据锚点数量。
        required_by_count: fact 支撑的 contract / ITEM_RULE 数量。
    """

    fact_id: str
    source_field_id: str
    status: str
    missing_reason: str | None
    value_chars: int
    serialized_fact_chars: int
    evidence_anchor_count: int
    required_by_count: int


@dataclass(frozen=True, slots=True, kw_only=True)
class ChapterPromptAnchorCostRow:
    """writer prompt anchor 成本行，见模板证据锚点约束。

    Attributes:
        anchor_id: anchor id。
        source_kind: 证据来源类型。
        document_year: 文档年份。
        section_id: 年报章节或派生来源。
        table_id: 表格编号。
        row_locator_present: 是否存在行级定位。
        serialized_anchor_chars: 实际 prompt anchor 行字符数。
    """

    anchor_id: str
    source_kind: str
    document_year: int | None
    section_id: str | None
    table_id: str | None
    row_locator_present: bool
    serialized_anchor_chars: int


@dataclass(frozen=True, slots=True, kw_only=True)
class ChapterPromptCostDiagnostic:
    """writer prompt-cost 安全诊断，见模板第 1-6 章。

    该结构只保存 component 字符数、fact/anchor id 和标量成本，不保存完整 prompt、
    fact 原文、anchor note、draft、provider request 或 response。
    """

    schema_version: str = CHAPTER_PROMPT_COST_DIAGNOSTIC_SCHEMA_VERSION
    chapter_id: int
    operation: Literal["writer"] = "writer"
    system_prompt_chars: int
    user_prompt_chars: int
    approx_prompt_tokens: int
    max_output_chars: int
    repair_attempt_index: int
    component_costs: ChapterPromptComponentCosts
    fact_cost_rows: tuple[ChapterPromptFactCostRow, ...]
    anchor_cost_rows: tuple[ChapterPromptAnchorCostRow, ...]


@dataclass(frozen=True, slots=True, kw_only=True)
class ChapterPromptFragments:
    """writer prompt 渲染片段，见模板第 1-6 章。

    Attributes:
        protocol: 输出协议与安全边界片段。
        contract: 章节身份、lens、facet 与 ITEM_RULE 片段。
        must_answer: must_answer 片段。
        must_not_cover: must_not_cover 片段。
        required_output: required_output_items 片段。
        facts: facts payload 片段。
        anchors: anchors payload 片段。
        repair_context: repair context 片段。
    """

    protocol: str
    contract: str
    must_answer: str
    must_not_cover: str
    required_output: str
    facts: str
    anchors: str
    repair_context: str


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
        repair_context: 可选重写上下文。
        prompt_payload_mode: writer prompt payload 模式；compact 只压缩表达，不放松事实边界。
        typed_required_output_items: 可选 typed required output 条目；为空时保持当前生产默认。
        evidence_availability: 可选同源证据可用性；typed required output 路径必须显式传入。
    """

    schema_version: ChapterWriterSchemaVersion = CHAPTER_WRITER_SCHEMA_VERSION
    projection_schema_version: ChapterFactSchemaVersion
    fund_code: str
    report_year: int
    chapter: ChapterFactInput
    mode: ChapterWriterMode = "llm"
    citation_style: ChapterCitationStyle = "body_quote"
    max_output_chars: int = 12000
    repair_context: ChapterRepairContext | None = None
    prompt_payload_mode: ChapterPromptPayloadMode = "full"
    typed_required_output_items: tuple[RequiredOutputItem, ...] = ()
    evidence_availability: EvidenceAvailability | None = None


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
        required_output_evidence_plan: typed required output 缺证计划；默认路径为空。
        allowed_fact_ids: 允许使用的 fact id。
        allowed_anchor_ids: 允许引用的 anchor id。
        deleted_item_rule_ids: 必须删除的 ITEM_RULE id。
        required_gap_phrases: 建议缺口措辞。
        prompt_cost_diagnostic: writer prompt-cost 安全诊断。
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
    required_output_evidence_plan: tuple[RequiredOutputEvidencePlan, ...] = ()
    prompt_cost_diagnostic: ChapterPromptCostDiagnostic | None = None


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
        response_chars: LLM 响应字符数；未调用 LLM 时为 `None`。
        finish_reason: LLM 响应结束原因；未调用 LLM 或未知时为 `None`。
        max_output_chars: 本次 writer 输出硬上限。
    """

    schema_version: ChapterWriterSchemaVersion = CHAPTER_WRITER_SCHEMA_VERSION
    status: ChapterWriteStatus
    stop_reason: ChapterWriteStopReason
    prompt: ChapterWriterPrompt
    draft: ChapterDraft | None
    issues: tuple[ChapterWriteIssue, ...]
    response_chars: int | None = None
    finish_reason: str | None = None
    max_output_chars: int | None = None


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
    repair_context: ChapterRepairContext | None = None,
    prompt_payload_mode: ChapterPromptPayloadMode = "full",
    typed_required_output_items: tuple[RequiredOutputItem, ...] = (),
    evidence_availability: EvidenceAvailability | None = None,
) -> ChapterWriterInput:
    """从 Gate 1 投影构造单章写作输入，见模板第 0-7 章。

    Args:
        projection: Gate 1 `ChapterFactProjection`。
        chapter_id: 需要写作的模板章节编号。
        mode: 写作模式。
        citation_style: 证据引用样式。
        max_output_chars: LLM 输出硬上限。
        repair_context: 可选重写上下文。
        prompt_payload_mode: writer prompt payload 模式。
        typed_required_output_items: 可选 typed required output 条目；为空时保持默认路径。
        evidence_availability: 可选同源证据可用性；typed 路径必须显式传入。

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
    if prompt_payload_mode not in get_args(ChapterPromptPayloadMode):
        raise ValueError(f"未知 prompt payload 模式：{prompt_payload_mode}")
    return ChapterWriterInput(
        projection_schema_version=projection.schema_version,
        fund_code=projection.fund_code,
        report_year=projection.report_year,
        chapter=_chapter_by_id(projection, chapter_id),
        mode=mode,
        citation_style=citation_style,
        max_output_chars=max_output_chars,
        repair_context=repair_context,
        prompt_payload_mode=prompt_payload_mode,
        typed_required_output_items=typed_required_output_items,
        evidence_availability=evidence_availability,
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
    required_output_plan = _required_output_evidence_plan(input_data)
    system_prompt = (
        "你是基金分析章节写作器。只能使用输入 facts、missing reasons 和 evidence anchors；"
        "不得读取外部资料，不得输出买入/卖出/仓位/收益预测。"
    )
    fragments = _chapter_prompt_fragments(
        input_data,
        deleted_item_rule_ids=deleted_item_rule_ids,
        required_output_plan=required_output_plan,
    )
    user_prompt = "\n".join(
        (
            fragments.protocol,
            fragments.contract,
            fragments.must_answer,
            fragments.must_not_cover,
            fragments.required_output,
            fragments.facts,
            fragments.anchors,
            fragments.repair_context,
        )
    )
    return ChapterWriterPrompt(
        chapter_id=chapter.chapter_id,
        title=chapter.title,
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        must_answer=contract.must_answer,
        must_not_cover=contract.must_not_cover,
        required_output_items=_prompt_required_output_marker_items(input_data, required_output_plan),
        allowed_fact_ids=tuple(fact.fact_id for fact in chapter.facts),
        allowed_anchor_ids=allowed_anchor_ids,
        deleted_item_rule_ids=deleted_item_rule_ids,
        required_gap_phrases=("未披露", "数据不足", "下一步最小验证问题"),
        required_output_evidence_plan=required_output_plan,
        prompt_cost_diagnostic=_prompt_cost_diagnostic(
            input_data,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            fragments=fragments,
        ),
    )


def _chapter_prompt_fragments(
    input_data: ChapterWriterInput,
    *,
    deleted_item_rule_ids: tuple[str, ...],
    required_output_plan: tuple[RequiredOutputEvidencePlan, ...],
) -> ChapterPromptFragments:
    """构造 writer prompt 命名片段，见模板第 1-6 章。

    Args:
        input_data: 章节写作输入。
        deleted_item_rule_ids: 已裁定删除的 ITEM_RULE id。
        required_output_plan: typed required output 缺证计划。

    Returns:
        可独立计费的 prompt 片段。

    Raises:
        无显式抛出。
    """

    chapter = input_data.chapter
    contract = chapter.contract
    protocol = "\n".join(
        (
            "先遵守输出协议，后写内容：",
            "1. 只输出章节 Markdown 正文。",
            "2. 顶层结构只能使用：### 结论要点 / ### 详细情况 / ### 证据与出处。",
            "3. 对每个 required_output_items 先复制 exact marker，再写 1-3 句。",
            "4. 有同源事实时在事实句附近放 allowed anchor marker；无事实时用 allowed missing marker 写缺口。",
            "5. 宁可简短覆盖全部 required markers，不要扩写长段落；不得输出附录、JSON 或分析过程。",
            _compact_payload_protocol(input_data.prompt_payload_mode),
            "输出协议：只输出章节 Markdown 正文，不得输出 JSON、解释性前后缀或“以下是章节”。",
            "第 1-6 章必须包含且只用这些顶层结构段落："
            + " / ".join(REQUIRED_BODY_SECTION_HEADINGS),
            "每个 required_output_items 必须先输出 exact marker："
            "`<!-- required_output:<exact required output item> -->`；"
            "typed 路径使用 `<!-- required_output:<typed item id> -->`；"
            "marker 后再写同源证据内容或 approved 缺口/验证问题。",
            "证据断言只能使用 allowed anchor set 中的 marker：`<!-- anchor:<anchor_id> -->`；"
            "required_anchor_ids 是允许集合，不要求全量使用。",
            "禁止根据 fact_id、source_field_id、source_field_name 或 fact value 自行合成 anchor id；"
            "若 fact 可用但没有 evidence_anchor_ids，只能无 anchor 概述或写 approved 缺口/验证问题。",
            _bond_risk_anchor_contract_prompt(chapter),
            _ch2_numerical_closure_contract_prompt(chapter),
            _missing_marker_contract_prompt(chapter.missing_reasons),
            "缺少同源事实时写“未披露 / 数据不足 / 下一步最小验证问题”，不得编造。",
            f"输出长度硬上限：{input_data.max_output_chars} 字符；每个 required item 后写 1-3 句，"
            "优先覆盖 marker，不输出附录、JSON 或分析过程。",
        )
    )
    contract_fragment = "\n".join(
        (
            f"章节：{chapter.chapter_id} {chapter.title}",
            f"基金：{input_data.fund_code} / 年报年份：{input_data.report_year}",
            f"基金类型：{chapter.fund_type}",
            f"分类依据：{'; '.join(chapter.classification_basis) or '未披露'}",
            f"preferred_lens：{'; '.join(chapter.lens_resolution.statements) or 'unknown'}",
            "候选 facet 只能写成未断言，不得作为事实："
            + (", ".join(chapter.facet_resolution.non_asserted_facets) or "无"),
            "候选 facet 固定写法：候选/未断言信息：<facet> 仅为候选标签，"
            "当前结构化证据不足，不能写成本基金属于/是/定位为该 facet。",
            "候选 facet 禁止断言形式：是<facet>、为<facet>、属于<facet>、定位为<facet>、可判定为<facet>。",
            "删除的 ITEM_RULE：" + _json_text(deleted_item_rule_ids),
            "删除的 ITEM_RULE 只禁止对应 optional/conditional 段落标题和专属段落；"
            "不得因此省略 required_output marker。若相关语义属于 required_output，只能在 required_output 下用同源证据或缺口措辞简短说明。",
        )
    )
    return ChapterPromptFragments(
        protocol=protocol,
        contract=contract_fragment,
        must_answer="必须回答：" + _json_text(contract.must_answer),
        must_not_cover="禁止覆盖：" + _json_text(contract.must_not_cover),
        required_output="必须输出项："
        + _json_text(_prompt_required_output_payload(input_data, required_output_plan)),
        facts="允许 facts：" + _json_text(_prompt_fact_payload(chapter.facts, mode=input_data.prompt_payload_mode)),
        anchors="允许 anchors："
        + _json_text(_prompt_anchor_payload(chapter.evidence_anchors, mode=input_data.prompt_payload_mode)),
        repair_context="\n".join(
            fragment
            for fragment in (
                _repair_context_prompt(input_data.repair_context),
                _ch2_l1_repair_guidance_prompt(chapter, input_data.repair_context),
                _ch5_forbidden_phrase_repair_guidance_prompt(
                    chapter,
                    input_data.repair_context,
                ),
            )
            if fragment
        ),
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
        return _blocked_result(
            prompt,
            _stop_reason(issues),
            issues,
            response_chars=len(response.text),
            finish_reason=response.finish_reason,
            max_output_chars=input_data.max_output_chars,
        )
    if draft is None:
        issue = _issue(
            "writer:llm_contract_violation",
            "llm_contract_violation",
            "LLM 响应未能生成可接受章节草稿。",
        )
        return _blocked_result(
            prompt,
            "llm_contract_violation",
            (issue,),
            response_chars=len(response.text),
            finish_reason=response.finish_reason,
            max_output_chars=input_data.max_output_chars,
        )
    return ChapterWriteResult(
        status="drafted",
        stop_reason="none",
        prompt=prompt,
        draft=draft,
        issues=(),
        response_chars=len(response.text),
        finish_reason=response.finish_reason,
        max_output_chars=input_data.max_output_chars,
    )


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
    issues.extend(_required_output_preflight_issues(input_data))
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


def _required_output_evidence_plan(input_data: ChapterWriterInput) -> tuple[RequiredOutputEvidencePlan, ...]:
    """构造 typed required output 缺证计划。

    Args:
        input_data: 章节写作输入。

    Returns:
        typed required output 缺证计划；未启用 typed 路径时为空。

    Raises:
        ValueError: typed 条目启用但完全缺少 availability，或 typed 条目不属于当前章节时抛出。
    """

    typed_items = input_data.typed_required_output_items
    if not typed_items:
        return ()
    if input_data.evidence_availability is None:
        raise ValueError("typed required output 写作路径必须显式传入 EvidenceAvailability")
    plan = tuple(
        _required_output_plan_item(input_data.chapter.chapter_id, item, input_data.evidence_availability)
        for item in typed_items
    )
    _validate_required_output_plan(plan, input_data.chapter.chapter_id)
    return plan


def _required_output_plan_item(
    chapter_id: int,
    item: RequiredOutputItem,
    evidence_availability: EvidenceAvailability,
) -> RequiredOutputEvidencePlan:
    """构造单个 typed required output 缺证计划。

    Args:
        chapter_id: 当前公开章节编号。
        item: typed required output item。
        evidence_availability: 同源证据可用性。

    Returns:
        单项 required output 缺证计划。

    Raises:
        ValueError: item id 不属于当前章节，或 availability 缺失且需要缺证行为时抛出。
    """

    if not item.item_id.startswith(f"ch{chapter_id}.required_output."):
        raise ValueError(f"typed required output item 不属于当前章节：{item.item_id}")
    requirement = _availability_for_required_output(item, evidence_availability)
    status = requirement.status if requirement is not None else None
    missing = status in _MISSING_EVIDENCE_STATUSES
    missing_availability = requirement is None and item.when_evidence_missing is not None
    action = "block" if missing_availability else _required_output_action(item, status)
    return RequiredOutputEvidencePlan(
        item_id=item.item_id,
        text=item.text,
        marker=_required_output_marker(item.item_id),
        availability_status=status,
        when_evidence_missing=item.when_evidence_missing,
        missing_evidence_reason=item.missing_evidence_reason,
        action=action,
        prompt_instruction=_required_output_prompt_instruction(item, action, status),
        requirement_fact_ids=requirement.fact_ids if requirement is not None else (),
        requirement_anchor_ids=requirement.evidence_anchor_ids if requirement is not None and not missing else (),
    )


def _availability_for_required_output(
    item: RequiredOutputItem,
    evidence_availability: EvidenceAvailability,
) -> RequirementAvailability | None:
    """读取 required output 对应 availability。

    Args:
        item: typed required output item。
        evidence_availability: 同源证据可用性。

    Returns:
        匹配的 availability；availability 对象缺少当前 item mapping 时返回 `None`。

    Raises:
        无显式抛出。
    """

    try:
        return evidence_availability.require(cast(EvidenceRequirementId, item.item_id))
    except ValueError:
        return None


def _required_output_action(
    item: RequiredOutputItem,
    status: AvailabilityStatus | None,
) -> Literal["render", "render_evidence_gap", "render_minimum_verification_question", "delete", "block"]:
    """按 availability 和 typed 行为裁定 writer 动作。

    Args:
        item: typed required output item。
        status: 当前 evidence availability 状态。

    Returns:
        writer 动作。

    Raises:
        ValueError: 静默删除缺少 typed reason，或缺证但没有 approved 行为时抛出。
    """

    if status == "available" or status is None:
        return "render"
    behavior = item.when_evidence_missing
    if behavior is None:
        raise ValueError(f"typed required output 缺证但未声明 when_evidence_missing：{item.item_id}")
    if behavior == "render_evidence_gap":
        return "render_evidence_gap"
    if behavior == "render_minimum_verification_question":
        return "render_minimum_verification_question"
    if behavior == "delete_if_not_applicable":
        if status != "not_applicable" or item.missing_evidence_reason is None:
            raise ValueError(f"delete_if_not_applicable 需要 not_applicable 状态和 typed reason：{item.item_id}")
        return "delete"
    return "block"


def _required_output_prompt_instruction(
    item: RequiredOutputItem,
    action: Literal["render", "render_evidence_gap", "render_minimum_verification_question", "delete", "block"],
    status: AvailabilityStatus | None,
) -> str:
    """渲染 required output plan 的安全写作说明。

    Args:
        item: typed required output item。
        action: writer 动作。
        status: availability 状态。

    Returns:
        prompt instruction。

    Raises:
        无显式抛出。
    """

    if action == "render":
        return "使用同源 facts 和 allowed anchors 输出该项，不得超出证据。"
    if action == "render_evidence_gap":
        return (
            f"必须输出该 marker，但只能写证据缺口；状态={status}；"
            f"原因={item.missing_evidence_reason or 'typed reason absent'}；"
            "必须包含“证据不足/数据不足/未披露/未复核/不能据此判断”之一，不得给出正向结论。"
        )
    if action == "render_minimum_verification_question":
        return (
            f"必须输出该 marker，但只能写下一步最小验证问题；状态={status}；"
            f"原因={item.missing_evidence_reason or 'typed reason absent'}；"
            "必须包含“下一步最小验证问题”或等价验证措辞，不得给出正向结论。"
        )
    if action == "delete":
        return f"该项 not_applicable，允许删除；typed reason={item.missing_evidence_reason}。"
    return f"缺少支持该项的证据且无安全降级，必须在 writer preflight fail-closed；状态={status}。"


def _validate_required_output_plan(
    plan: tuple[RequiredOutputEvidencePlan, ...],
    chapter_id: int,
) -> None:
    """校验 typed required output plan。

    Args:
        plan: required output 缺证计划。
        chapter_id: 当前章节编号。

    Returns:
        校验通过时返回 `None`。

    Raises:
        ValueError: item id 重复、章节不匹配或删除缺少 typed reason 时抛出。
    """

    item_ids = tuple(item.item_id for item in plan)
    if len(set(item_ids)) != len(item_ids):
        raise ValueError(f"typed 章节 {chapter_id} required output plan item_id 存在重复")
    for item in plan:
        if item.action == "delete" and item.missing_evidence_reason is None:
            raise ValueError(f"typed 章节 {chapter_id} required output 删除缺少 typed reason：{item.item_id}")


def _required_output_preflight_issues(input_data: ChapterWriterInput) -> tuple[ChapterWriteIssue, ...]:
    """生成 typed required output preflight 阻断 issue。

    Args:
        input_data: 章节写作输入。

    Returns:
        block 行为对应的 fail-closed issue。

    Raises:
        无显式抛出；typed plan 构造错误由调用链抛出 `ValueError`。
    """

    return tuple(
        _issue(
            f"writer:required_output_block:{plan.item_id}",
            "missing_required_facts",
            f"typed required output 缺少证据且无安全降级：{plan.item_id}；{plan.prompt_instruction}",
            fact_ids=plan.requirement_fact_ids,
            anchor_ids=plan.requirement_anchor_ids,
        )
        for plan in _required_output_evidence_plan(input_data)
        if plan.action == "block"
    )


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


def _bond_risk_anchor_contract_prompt(chapter: ChapterFactInput) -> str:
    """构造债券风险证据内部锚点引用约束，见模板第 6 章核心风险。

    Args:
        chapter: 单章事实输入。

    Returns:
        当前章节含债券风险证据时返回内部锚点禁止引用说明；否则返回空字符串。

    Raises:
        无显式抛出。
    """

    if not any(fact.source_field_name == "bond_risk_evidence" for fact in chapter.facts):
        return ""
    return (
        "bond_risk_evidence 只能引用“允许 anchors”列表中的 anchor_id，"
        "不得根据 fact value、内部 source_anchor_ids 或 source_field_id 自行合成 anchor id。"
    )


def _ch2_numerical_closure_contract_prompt(chapter: ChapterFactInput) -> str:
    """构造第 2 章 R=A+B-C 数字闭环锚点约束，见模板第 2 章。

    Args:
        chapter: 单章事实输入。

    Returns:
        第 2 章返回数字闭环锚点约束；其他章节返回空字符串。

    Raises:
        无显式抛出。
    """

    if chapter.chapter_id != 2:
        return ""
    return (
        "第2章 L1 数字闭环安全输出契约：若写 R/A/B/C/A-C、Alpha/Beta/Cost 或百分比闭合断言，"
        "allowed anchor marker 必须与该具体断言同句或上下2行；"
        "只能二选一：1. 有邻近 allowed anchor 的具体数字闭环；"
        "2. 不写具体百分比，改写为数据不足/下一步最小验证问题。"
        "`### 结论要点` 和 `### 证据与出处` 不得重复无邻近 anchor 的 R/A/B/C/A-C 具体百分比；"
        "来源标签、年报章节名或出处列表不能替代 `<!-- anchor:<anchor_id> -->`；"
        "缺同源事实或不确定 anchor 是否支撑精确数值时，省略 R、A、B、C、A-C 或 Alpha/Beta/Cost 百分比，不得近似或编造。"
    )


def _has_l1_numerical_closure_repair_issue(repair_context: ChapterRepairContext | None) -> bool:
    """判断 repair context 是否包含 L1 数字闭环问题，见模板第 2 章 R=A+B-C。

    Args:
        repair_context: 可选章节重写上下文。

    Returns:
        当上一轮 issue id 以 `programmatic:L1` 开头时返回 `True`。

    Raises:
        无显式抛出。
    """

    if repair_context is None:
        return False
    return any(issue_id.startswith("programmatic:L1") for issue_id in repair_context.previous_issue_ids)


def _ch2_l1_repair_guidance_prompt(
    chapter: ChapterFactInput,
    repair_context: ChapterRepairContext | None,
) -> str:
    """构造第 2 章 L1 repair 局部锚点放置清单，见模板第 2 章 R=A+B-C。

    Args:
        chapter: 单章事实输入。
        repair_context: 可选章节重写上下文。

    Returns:
        命中第 2 章且上一轮存在 `programmatic:L1` 时返回 checklist，否则返回空字符串。

    Raises:
        无显式抛出。
    """

    if chapter.chapter_id != 2 or not _has_l1_numerical_closure_repair_issue(repair_context):
        return ""
    return "\n".join(
        (
            "第2章 L1 repair 必须改写规则：",
            "1. 先删除上一轮无邻近 anchor 的具体数字闭环断言。",
            "2. 只有确认 allowed `<!-- anchor:<anchor_id> -->` 支撑该具体数值时，才重新写入百分比，"
            "且 anchor 必须在同一句或上下2行内。",
            "3. 不确定时写数据不足或下一步最小验证问题，且不写具体百分比。",
            "4. `### 结论要点` 和 `### 证据与出处` 不得无邻近 anchor 复述 R/A/B/C/A-C/Alpha/Beta/Cost 百分比。",
            "5. 输出前逐行自查 R/A/B/C/A-C/Alpha/Beta/Cost/%；命中这些词且缺少邻近 allowed anchor 的行必须改写为缺口或验证问题。",
        )
    )


def _ch5_forbidden_phrase_repair_guidance_prompt(
    chapter: ChapterFactInput,
    repair_context: ChapterRepairContext | None,
) -> str:
    """构造第 5 章 forbidden phrase repair 局部改写清单，见模板第 5 章当前阶段。

    Args:
        chapter: 单章事实输入。
        repair_context: 可选章节重写上下文。

    Returns:
        命中第 5 章 repair attempt 时返回 checklist，否则返回空字符串。

    Raises:
        无显式抛出。
    """

    if chapter.chapter_id != 5 or repair_context is None:
        return ""
    return "\n".join(
        (
            "第5章 forbidden phrase repair 必须改写规则：",
            "1. 输出前逐句删除交易动作建议、仓位动作、收益预测、目标价和基金经理动机推断。",
            "2. 只使用“值得持有 / 需要关注 / 建议替换”边界表达；不得写买入、卖出、加仓、减仓、清仓或仓位比例。",
            "3. 事实不足或锚点不足时，只写数据不足或下一步最小验证问题，不用行动指令补足。",
            "4. 输出前逐句自查；命中交易动作、仓位动作、收益预测或经理动机推断的句子必须删除或改写为边界表达。",
        )
    )


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
        repair_context=input_data.repair_context,
        prompt_cost_diagnostic=prompt.prompt_cost_diagnostic,
    )


def _prompt_cost_diagnostic(
    input_data: ChapterWriterInput,
    *,
    system_prompt: str,
    user_prompt: str,
    fragments: ChapterPromptFragments,
) -> ChapterPromptCostDiagnostic:
    """构造 writer prompt-cost 安全诊断，见模板第 1-6 章。

    Args:
        input_data: 章节写作输入。
        system_prompt: 实际 system prompt。
        user_prompt: 实际 user prompt。
        fragments: 实际 user prompt 片段。

    Returns:
        不含 prompt 文本的成本诊断。

    Raises:
        无显式抛出。
    """

    return ChapterPromptCostDiagnostic(
        chapter_id=input_data.chapter.chapter_id,
        system_prompt_chars=len(system_prompt),
        user_prompt_chars=len(user_prompt),
        approx_prompt_tokens=_approx_prompt_tokens(len(system_prompt), len(user_prompt)),
        max_output_chars=input_data.max_output_chars,
        repair_attempt_index=input_data.repair_context.attempt_index
        if input_data.repair_context is not None
        else 0,
        component_costs=ChapterPromptComponentCosts(
            protocol_chars=len(fragments.protocol),
            contract_chars=len(fragments.contract),
            must_answer_chars=len(fragments.must_answer),
            must_not_cover_chars=len(fragments.must_not_cover),
            required_output_chars=len(fragments.required_output),
            facts_chars=len(fragments.facts),
            anchors_chars=len(fragments.anchors),
            repair_context_chars=len(fragments.repair_context),
        ),
        fact_cost_rows=_prompt_fact_cost_rows(
            input_data.chapter.facts,
            mode=input_data.prompt_payload_mode,
        ),
        anchor_cost_rows=_prompt_anchor_cost_rows(
            input_data.chapter.evidence_anchors,
            mode=input_data.prompt_payload_mode,
        ),
    )


def _approx_prompt_tokens(system_prompt_chars: int, user_prompt_chars: int) -> int:
    """按固定 heuristic 估算 prompt token 数。

    Args:
        system_prompt_chars: system prompt 字符数。
        user_prompt_chars: user prompt 字符数。

    Returns:
        `ceil((system + user) / 4)` 的近似 token 数。

    Raises:
        无显式抛出。
    """

    return (system_prompt_chars + user_prompt_chars + 3) // 4


def _compact_payload_protocol(mode: ChapterPromptPayloadMode) -> str:
    """渲染 compact payload 安全说明。

    Args:
        mode: prompt payload 模式。

    Returns:
        writer 必须遵守的 compact 安全约束。

    Raises:
        无显式抛出。
    """

    if mode != "compact":
        return "FACT_PAYLOAD_MODE: full；可使用 provided fact value 和 anchors，但不得超出输入事实。"
    return (
        "FACT_PAYLOAD_MODE: compact；若 fact 标记 value_available_but_detail_compacted=true，"
        "只能使用 value_kind/value_chars/value_summary 与 provided anchors，不得引用、复述或推断被省略的 raw detail。"
    )


def _repair_context_prompt(repair_context: ChapterRepairContext | None) -> str:
    """把重写上下文渲染为 prompt 片段，见模板第 1-6 章。

    Args:
        repair_context: 可选重写上下文。

    Returns:
        prompt 片段；无上下文时返回初始 attempt 说明。

    Raises:
        无显式抛出。
    """

    if repair_context is None:
        return "重写上下文：初始 attempt，无上一轮失败原因。"
    return "\n".join(
        (
            f"重写上下文：attempt_index={repair_context.attempt_index}",
            "上一轮 issue ids：" + _json_text(repair_context.previous_issue_ids),
            "上一轮 issue messages：" + _json_text(repair_context.previous_messages),
            "本轮必须修复项：" + _json_text(repair_context.required_corrections),
            "不得重复上一轮 issue；不得用自由文本绕过 required_output、anchor 或 missing markers。",
        )
    )


def _missing_marker_contract_prompt(
    missing_reasons: tuple[ChapterFactMissingReason, ...],
) -> str:
    """渲染 missing marker exact contract，见模板第 1-6 章数据缺口语义。

    Args:
        missing_reasons: 当前章节允许声明的数据缺口原因。

    Returns:
        prompt contract 片段。

    Raises:
        无显式抛出。
    """

    if not missing_reasons:
        return "\n".join(
            (
                "MISSING_MARKER_CONTRACT:",
                "ALLOWED_MISSING_REASONS: none",
                "MISSING_MARKER_RULES:",
                "- Do not output any missing marker in this chapter.",
                "- You may still write 未披露 / 数据不足 / 下一步最小验证问题 when facts are insufficient.",
            )
        )
    return "\n".join(
        (
            "MISSING_MARKER_CONTRACT:",
            "ALLOWED_MISSING_REASONS: " + ", ".join(missing_reasons),
            "MISSING_MARKER_EXACT_FORM:",
            "<!-- missing:{reason} -->",
            "MISSING_MARKER_RULES:",
            "- Replace {reason} with exactly one token from ALLOWED_MISSING_REASONS.",
            "- Do not output {reason}, <reason>, or any placeholder.",
            "- Do not add spaces around the colon.",
            "- Do not change case, translate missing, or use a fullwidth colon.",
            "- Do not wrap the marker in backticks or code fences.",
            "- Do not add Chinese explanation, JSON, Markdown bullet text, or extra labels inside the marker.",
        )
    )


def _prompt_required_output_payload(
    input_data: ChapterWriterInput,
    required_output_plan: tuple[RequiredOutputEvidencePlan, ...],
) -> tuple[str, ...]:
    """把 required output items 转为带 exact marker 的 prompt payload。

    Args:
        input_data: 章节写作输入。
        required_output_plan: typed required output 缺证计划。

    Returns:
        每项以 exact marker 开头的 prompt 文本。

    Raises:
        无显式抛出。
    """

    if required_output_plan:
        return tuple(_prompt_required_output_plan_item(plan) for plan in required_output_plan)
    return tuple(f"{_required_output_marker(item)}\n{item}" for item in input_data.chapter.contract.required_output_items)


def _prompt_required_output_plan_item(plan: RequiredOutputEvidencePlan) -> str:
    """渲染 typed required output plan 的单项 prompt。

    Args:
        plan: typed required output 缺证计划。

    Returns:
        writer prompt 中的单项要求。

    Raises:
        无显式抛出。
    """

    return "\n".join(
        (
            plan.marker,
            f"{plan.item_id} | {plan.text}",
            f"availability={plan.availability_status or 'not_mapped'}; action={plan.action}",
            f"instruction={plan.prompt_instruction}",
        )
    )


def _prompt_required_output_marker_items(
    input_data: ChapterWriterInput,
    required_output_plan: tuple[RequiredOutputEvidencePlan, ...],
) -> tuple[str, ...]:
    """读取 parser 必须检查的 required output marker items。

    Args:
        input_data: 章节写作输入。
        required_output_plan: typed required output 缺证计划。

    Returns:
        marker item 元组；typed 路径使用 stable item id，默认路径使用原文。

    Raises:
        无显式抛出。
    """

    if required_output_plan:
        return tuple(plan.item_id for plan in required_output_plan if plan.action != "delete")
    return input_data.chapter.contract.required_output_items


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
    if response.finish_reason in INCOMPLETE_FINISH_REASONS:
        return None, (
            _issue(
                f"writer:response_incomplete:{response.finish_reason}",
                "response_incomplete",
                f"LLM finish_reason={response.finish_reason} 表示输出不完整或内容被过滤，禁止部分接受。",
            ),
        )
    if len(text) > input_data.max_output_chars:
        return None, (
            _issue(
                "writer:llm_response_too_long",
                "response_too_long",
                "LLM 输出超过 max_output_chars，禁止截断或部分接受。",
            ),
        )
    issues.extend(_invalid_marker_issues(text))
    issues.extend(_required_structure_issues(text, input_data.chapter))
    issues.extend(_required_output_marker_issues(text, prompt))
    issues.extend(_required_output_degrade_issues(text, prompt))
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


def _required_structure_issues(
    text: str,
    chapter: ChapterFactInput,
) -> tuple[ChapterWriteIssue, ...]:
    """检查第 1-6 章固定结构段落。

    Args:
        text: LLM 输出文本。
        chapter: 单章事实输入。

    Returns:
        缺失结构段落 issue。

    Raises:
        无显式抛出。
    """

    if chapter.chapter_id not in range(1, 7):
        return ()
    return tuple(
        _issue(
            f"writer:missing_required_structure:{heading}",
            "missing_required_structure",
            f"第 1-6 章缺少固定结构段落：{heading}",
        )
        for heading in REQUIRED_BODY_SECTION_HEADINGS
        if heading not in text
    )


def _required_output_marker_issues(
    text: str,
    prompt: ChapterWriterPrompt,
) -> tuple[ChapterWriteIssue, ...]:
    """检查 required output exact marker。

    Args:
        text: LLM 输出文本。
        prompt: 章节写作 prompt。

    Returns:
        缺失 required output marker issue。

    Raises:
        无显式抛出。
    """

    return tuple(
        _issue(
            f"writer:missing_required_output_marker:{index}",
            "missing_required_output_marker",
            f"缺少 required output item marker：{item}",
        )
        for index, item in enumerate(prompt.required_output_items)
        if item and _required_output_marker(item) not in text
    )


def _required_output_degrade_issues(
    text: str,
    prompt: ChapterWriterPrompt,
) -> tuple[ChapterWriteIssue, ...]:
    """检查 typed required output 缺证降级是否按 approved 输出满足。

    Args:
        text: LLM 输出文本。
        prompt: 章节写作 prompt。

    Returns:
        降级输出不合格的 issue。

    Raises:
        无显式抛出。
    """

    issues: list[ChapterWriteIssue] = []
    for plan in prompt.required_output_evidence_plan:
        if plan.action == "render_evidence_gap" and not _required_output_segment_contains(
            text,
            plan.item_id,
            _GAP_OUTPUT_PHRASES,
        ):
            issues.append(
                _issue(
                    f"writer:required_output_gap_missing:{plan.item_id}",
                    "missing_required_output_marker",
                    f"缺证 required output 未通过 approved evidence gap 输出满足：{plan.item_id}",
                    fact_ids=plan.requirement_fact_ids,
                    anchor_ids=plan.requirement_anchor_ids,
                )
            )
        if plan.action == "render_minimum_verification_question" and not _required_output_segment_contains(
            text,
            plan.item_id,
            _VERIFICATION_OUTPUT_PHRASES,
        ):
            issues.append(
                _issue(
                    f"writer:required_output_verification_missing:{plan.item_id}",
                    "missing_required_output_marker",
                    f"缺证 required output 未通过 approved minimum verification question 输出满足：{plan.item_id}",
                    fact_ids=plan.requirement_fact_ids,
                    anchor_ids=plan.requirement_anchor_ids,
                )
            )
    return tuple(issues)


def _required_output_segment_contains(
    text: str,
    item_id: str,
    phrases: tuple[str, ...],
) -> bool:
    """判断 required output marker 后的局部内容是否包含要求措辞。

    Args:
        text: LLM 输出文本。
        item_id: typed required output item id。
        phrases: 必须出现的安全措辞集合。

    Returns:
        marker 后到下一个 required output marker 前包含任一措辞时返回 `True`。

    Raises:
        无显式抛出。
    """

    marker = _required_output_marker(item_id)
    start = text.find(marker)
    if start < 0:
        return False
    segment_start = start + len(marker)
    next_start = text.find(REQUIRED_OUTPUT_MARKER_PREFIX, segment_start)
    segment = text[segment_start:] if next_start < 0 else text[segment_start:next_start]
    return any(phrase in segment for phrase in phrases)


def _required_output_marker(item: str) -> str:
    """构造 required output exact marker。

    Args:
        item: required output item 原文。

    Returns:
        exact marker 文本。

    Raises:
        无显式抛出。
    """

    return f"{REQUIRED_OUTPUT_MARKER_PREFIX}{item} -->"


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
        message = "bond_risk_evidence anchor 不在 allowed anchors 中，禁止自行合成或引用内部 source_anchor_ids"
    return _issue(
        f"writer:unknown_anchor:{anchor_id}",
        "unknown_anchor",
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
    *,
    response_chars: int | None = None,
    finish_reason: str | None = None,
    max_output_chars: int | None = None,
) -> ChapterWriteResult:
    """构造 blocked 写作结果。

    Args:
        prompt: 章节 prompt。
        stop_reason: 停止原因。
        issues: 问题列表。
        response_chars: LLM 响应字符数。
        finish_reason: LLM 响应结束原因。
        max_output_chars: 本次 writer 输出硬上限。

    Returns:
        blocked 写作结果。

    Raises:
        无显式抛出。
    """

    return ChapterWriteResult(
        status="blocked",
        stop_reason=stop_reason,
        prompt=prompt,
        draft=None,
        issues=issues,
        response_chars=response_chars,
        finish_reason=finish_reason,
        max_output_chars=max_output_chars,
    )


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


def _prompt_fact_payload(
    facts: tuple[ChapterFactEntry, ...],
    *,
    mode: ChapterPromptPayloadMode = "full",
) -> tuple[dict[str, object], ...]:
    """把 facts 转为 prompt 负载。

    Args:
        facts: 章节 facts。
        mode: prompt payload 模式。

    Returns:
        可 JSON 序列化的 prompt fact 列表。

    Raises:
        无显式抛出。
    """

    return tuple(
        _prompt_fact_row(fact, mode=mode)
        for fact in facts
    )


def _prompt_fact_row(
    fact: ChapterFactEntry,
    *,
    mode: ChapterPromptPayloadMode,
) -> dict[str, object]:
    """把单个 fact 转为 prompt 行。

    Args:
        fact: 章节 fact。
        mode: prompt payload 模式。

    Returns:
        可 JSON 序列化的 fact prompt 行。

    Raises:
        无显式抛出。
    """

    row: dict[str, object] = {
            "fact_id": fact.fact_id,
            "source_field_id": fact.source_field_id,
            "source_field_name": fact.source_field_name,
            "status": fact.status,
            "evidence_anchor_ids": fact.evidence_anchor_ids,
            "missing_reason": fact.missing_reason,
            "required_by": fact.required_by,
        }
    if mode == "compact" and _should_compact_value(fact.value):
        row.update(_compact_value_payload(fact.value))
        return row
    row["value"] = _jsonable_value(fact.value)
    return row


def _prompt_anchor_payload(
    anchors: tuple[ChapterEvidenceAnchor, ...],
    *,
    mode: ChapterPromptPayloadMode = "full",
) -> tuple[dict[str, object], ...]:
    """把 anchors 转为 prompt 负载。

    Args:
        anchors: 章节证据锚点。
        mode: prompt payload 模式。

    Returns:
        可 JSON 序列化的锚点列表。

    Raises:
        无显式抛出。
    """

    return tuple(
        _prompt_anchor_row(anchor, mode=mode)
        for anchor in anchors
    )


def _prompt_anchor_row(
    anchor: ChapterEvidenceAnchor,
    *,
    mode: ChapterPromptPayloadMode,
) -> dict[str, object]:
    """把单个 anchor 转为 prompt 行。

    Args:
        anchor: 章节证据锚点。
        mode: prompt payload 模式。

    Returns:
        可 JSON 序列化的 anchor prompt 行。

    Raises:
        无显式抛出。
    """

    row: dict[str, object] = {
            "anchor_id": anchor.anchor_id,
            "source_kind": anchor.source_kind,
            "document_year": anchor.document_year,
            "section_id": anchor.section_id,
            "table_id": anchor.table_id,
            "row_locator": anchor.row_locator,
        }
    if mode == "full":
        row["note"] = anchor.note
    return row


def _prompt_fact_cost_rows(
    facts: tuple[ChapterFactEntry, ...],
    *,
    mode: ChapterPromptPayloadMode,
) -> tuple[ChapterPromptFactCostRow, ...]:
    """构造 fact prompt-cost 行。

    Args:
        facts: 章节 facts。
        mode: prompt payload 模式。

    Returns:
        不含 fact value 文本的成本行。

    Raises:
        无显式抛出。
    """

    return tuple(
        ChapterPromptFactCostRow(
            fact_id=fact.fact_id,
            source_field_id=fact.source_field_id,
            status=fact.status,
            missing_reason=fact.missing_reason,
            value_chars=len(_json_text(_jsonable_value(fact.value))),
            serialized_fact_chars=len(_json_text(_prompt_fact_row(fact, mode=mode))),
            evidence_anchor_count=len(fact.evidence_anchor_ids),
            required_by_count=len(fact.required_by),
        )
        for fact in facts
    )


def _prompt_anchor_cost_rows(
    anchors: tuple[ChapterEvidenceAnchor, ...],
    *,
    mode: ChapterPromptPayloadMode,
) -> tuple[ChapterPromptAnchorCostRow, ...]:
    """构造 anchor prompt-cost 行。

    Args:
        anchors: 章节证据锚点。
        mode: prompt payload 模式。

    Returns:
        不含 anchor note 文本的成本行。

    Raises:
        无显式抛出。
    """

    return tuple(
        ChapterPromptAnchorCostRow(
            anchor_id=anchor.anchor_id,
            source_kind=anchor.source_kind,
            document_year=anchor.document_year,
            section_id=anchor.section_id,
            table_id=anchor.table_id,
            row_locator_present=bool(anchor.row_locator),
            serialized_anchor_chars=len(_json_text(_prompt_anchor_row(anchor, mode=mode))),
        )
        for anchor in anchors
    )


def _should_compact_value(value: object) -> bool:
    """判断 fact value 是否需要 compact 表达。

    Args:
        value: fact value。

    Returns:
        超过 compact 阈值时返回 `True`。

    Raises:
        无显式抛出。
    """

    return len(_json_text(_jsonable_value(value))) > _COMPACT_VALUE_CHAR_THRESHOLD


def _compact_value_payload(value: object) -> dict[str, object]:
    """把大 value 转为确定性 compact payload。

    Args:
        value: 原始结构化 value。

    Returns:
        只含结构化摘要和成本标量的 compact payload。

    Raises:
        无显式抛出。
    """

    jsonable = _jsonable_value(value)
    return {
        "value_kind": _value_kind(jsonable),
        "value_chars": len(_json_text(jsonable)),
        "value_summary": _value_summary(jsonable),
        "value_available_but_detail_compacted": True,
        "compact_reason": "prompt_budget_compaction",
    }


def _value_kind(value: object) -> str:
    """读取 value 的稳定类型标签。

    Args:
        value: JSON 可消费值。

    Returns:
        稳定类型标签。

    Raises:
        无显式抛出。
    """

    if value is None:
        return "null"
    if isinstance(value, bool):
        return "bool"
    if isinstance(value, (int, float, Decimal)):
        return "number"
    if isinstance(value, str):
        return "string"
    if isinstance(value, dict):
        return "dict"
    if isinstance(value, (list, tuple)):
        return "list"
    return type(value).__name__


def _value_summary(value: object) -> dict[str, object]:
    """生成确定性 value 摘要，不做自然语言推断。

    仅提取顶层标量字段名和值、列表长度、嵌套 dict key 名。该摘要只服务
    prompt-budget compaction，不能被当作源文完整事实。

    Args:
        value: JSON 可消费值。

    Returns:
        确定性结构摘要。

    Raises:
        无显式抛出。
    """

    if isinstance(value, dict):
        scalar_fields: dict[str, object] = {}
        list_lengths: dict[str, int] = {}
        nested_dict_keys: dict[str, tuple[str, ...]] = {}
        for key in sorted(value):
            item = value[key]
            key_text = str(key)
            if _is_summary_scalar(item):
                scalar_fields[key_text] = item
            elif isinstance(item, (list, tuple)):
                list_lengths[key_text] = len(item)
            elif isinstance(item, dict):
                nested_dict_keys[key_text] = tuple(str(nested_key) for nested_key in sorted(item))
        return {
            "top_level_keys": tuple(str(key) for key in sorted(value)),
            "top_level_scalar_fields": scalar_fields,
            "top_level_list_lengths": list_lengths,
            "top_level_nested_dict_keys": nested_dict_keys,
        }
    if isinstance(value, (list, tuple)):
        return {"list_length": len(value)}
    if _is_summary_scalar(value):
        return {"scalar_value": value}
    return {"summary_available": False}


def _is_summary_scalar(value: object) -> bool:
    """判断 value 是否可作为顶层标量摘要。

    Args:
        value: 任意 value。

    Returns:
        是 JSON 标量时返回 `True`。

    Raises:
        无显式抛出。
    """

    return value is None or isinstance(value, (str, bool, int, float, Decimal))


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
