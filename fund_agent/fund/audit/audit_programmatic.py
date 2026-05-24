"""程序化审计规则。

本模块属于 Agent 层基金能力，服务 `docs/design.md` 第 5.2 节的 MVP 程序审计。
它只消费报告文本和 P2 结构化结果，不直接读取年报、PDF、缓存或文档仓库。
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from decimal import Decimal
from typing import Final, Literal

from fund_agent.fund.analysis.checklist import ChecklistItem, ChecklistResult
from fund_agent.fund.analysis.final_judgment import FinalJudgment, FinalJudgmentSource
from fund_agent.fund.analysis.r_abc import RabcAttribution
from fund_agent.fund.analysis.valuation_state import ValuationStateResolution
from fund_agent.fund.audit.contract_rules import (
    ContractMustAnswerCoverageRule,
    load_contract_audit_coverage_manifest,
    load_programmatic_contract_rules,
)
from fund_agent.fund.extractors.models import ExtractedField, IndexProfileValue, TrackingErrorValue
from fund_agent.fund.template.chapter_blocks import (
    EVIDENCE_APPENDIX_HEADING,
    RenderedChapterBlock,
    get_template_chapter_heading,
    split_rendered_chapter_blocks,
)
from fund_agent.fund.template.contracts import load_template_contract_manifest
from fund_agent.fund.template.item_rules import (
    TemplateItemRuleAuditContext,
    TemplateItemRuleDecision,
    get_template_item_rule,
    rendered_segment_present,
)

AuditRuleCode = Literal["P1", "P2", "P3", "C2", "L1", "R1", "R2"]
AuditSeverity = Literal["blocker", "reviewable"]
AuditStatus = Literal["pass", "fail"]

_MIN_CONTENT_LENGTH: Final[int] = 10
_L1_TOLERANCE: Final[Decimal] = Decimal("0.0001")
_EVIDENCE_MARKER_PATTERN: Final[re.Pattern[str]] = re.compile(r"(证据与出处|📎\s*证据|年报\d{4}§)")
_CHAPTER_EVIDENCE_LINE_PATTERN: Final[re.Pattern[str]] = re.compile(r"(?m)^>\s*📎\s*证据：")
_HEADING_PATTERN: Final[re.Pattern[str]] = re.compile(r"^#{1,6}\s+(.+?)\s*$", re.MULTILINE)
_CHAPTER_HEADING_PATTERN: Final[re.Pattern[str]] = re.compile(r"^#\s+(.+?)\s*$", re.MULTILINE)
_REQUIRED_CHAPTER_TITLES: Final[tuple[str, ...]] = tuple(
    chapter.title for chapter in load_template_contract_manifest().chapters
)
_CHECKED_RULES: Final[tuple[AuditRuleCode, ...]] = ("P1", "P2", "P3", "C2", "L1", "R1", "R2")
_CHECKLIST_SIGNAL_ORDER: Final[dict[str, int]] = {
    "green": 0,
    "gray": 1,
    "yellow": 2,
    "red": 3,
}


@dataclass(frozen=True, slots=True)
class AuditIssue:
    """单条程序审计问题。

    Attributes:
        code: 审计规则码。
        status: 审计状态。
        severity: 阻断级别。
        message: 问题说明。
        location: 问题位置。
    """

    code: AuditRuleCode
    status: AuditStatus
    severity: AuditSeverity
    message: str
    location: str | None = None


@dataclass(frozen=True, slots=True)
class ProgrammaticAuditResult:
    """程序审计结果。

    Attributes:
        passed: 是否通过。
        issues: 所有失败问题。
        checked_rules: 已执行规则码。
    """

    passed: bool
    issues: tuple[AuditIssue, ...]
    checked_rules: tuple[AuditRuleCode, ...]


@dataclass(frozen=True, slots=True)
class ProgrammaticAuditInput:
    """程序审计输入。

    Attributes:
        report_markdown: 已渲染报告 Markdown，用于 P1/P2/P3 结构审计。
        rabc_attributions: R=A+B-C 归因结果，用于 L1 计算闭合审计。
        checklist_result: 检查清单结果，用于 R1/R2 规则审计。
        final_judgment: 最终 selected 判断，用于 R2 与检查清单信号一致性审计。
        derived_final_judgment: Agent 层基金能力派生判断，用于 R2 source 冲突审计。
        final_judgment_source: selected 判断来源，用于区分系统派生与开发覆盖。
        valuation_state_resolution: 估值状态结构化真源，用于 R1 第 6 问证据审计。
        required_chapter_titles: 必要章节标题列表。
        chapter_blocks: 已渲染章节块，用于 P3 每章证据和 C2 契约审计。
        item_rule_decisions: renderer 产生的 ITEM_RULE 渲染/删除决策。
        item_rule_audit_context: ITEM_RULE 审计上下文，用于区分身份缺失与身份存在路径。
        index_profile: 指数画像结构化字段，用于确定性来源边界审计。
        tracking_error: 跟踪误差结构化字段，用于确定性来源边界审计。
    """

    report_markdown: str | None = None
    rabc_attributions: tuple[RabcAttribution, ...] = ()
    checklist_result: ChecklistResult | None = None
    final_judgment: FinalJudgment | None = None
    derived_final_judgment: FinalJudgment | None = None
    final_judgment_source: FinalJudgmentSource | None = None
    valuation_state_resolution: ValuationStateResolution | None = None
    required_chapter_titles: tuple[str, ...] = _REQUIRED_CHAPTER_TITLES
    chapter_blocks: tuple[RenderedChapterBlock, ...] = ()
    item_rule_decisions: tuple[TemplateItemRuleDecision, ...] = ()
    item_rule_audit_context: TemplateItemRuleAuditContext = "identity_missing"
    index_profile: ExtractedField[IndexProfileValue] | None = None
    tracking_error: ExtractedField[TrackingErrorValue] | None = None


def run_programmatic_audit(input_data: ProgrammaticAuditInput) -> ProgrammaticAuditResult:
    """执行 P1/P2/P3/C2/L1/R1/R2 程序审计。

    Args:
        input_data: 程序审计输入。

    Returns:
        程序审计结果。

    Raises:
        无显式抛出。
    """

    chapter_blocks, block_issues = _resolve_chapter_blocks_for_audit(input_data)
    issues = (
        *_audit_required_inputs(input_data),
        *_audit_report_structure(input_data.report_markdown, input_data.required_chapter_titles),
        *block_issues,
        *_audit_minimum_chapter_evidence(chapter_blocks),
        *_audit_contract_conformance(chapter_blocks),
        *_audit_item_rule_compliance(
            chapter_blocks,
            input_data.item_rule_decisions,
            input_data.item_rule_audit_context,
        ),
        *_audit_tracking_error_source_guard(chapter_blocks, input_data.tracking_error),
        *_audit_index_profile_source_guard(chapter_blocks, input_data.index_profile),
        *_audit_rabc_closure(input_data.rabc_attributions),
        *_audit_checklist_rules(
            input_data.checklist_result,
            input_data.valuation_state_resolution,
            input_data.report_markdown,
        ),
        *_audit_final_judgment(
            input_data.checklist_result,
            input_data.final_judgment,
            input_data.derived_final_judgment,
            input_data.final_judgment_source,
        ),
    )
    return ProgrammaticAuditResult(
        passed=not issues,
        issues=issues,
        checked_rules=_CHECKED_RULES,
    )


def _audit_required_inputs(input_data: ProgrammaticAuditInput) -> tuple[AuditIssue, ...]:
    """审计程序审计必需输入是否齐备。

    Args:
        input_data: 程序审计输入。

    Returns:
        必需输入缺失问题。

    Raises:
        无显式抛出。
    """

    issues: list[AuditIssue] = []
    if input_data.report_markdown is None:
        issues.append(
            _issue(
                code="P1",
                message="缺少报告 Markdown，无法执行 P1/P2/P3 结构审计。",
                location="report_markdown",
            ),
        )
    if not input_data.rabc_attributions:
        issues.append(
            _issue(
                code="L1",
                message="缺少 R=A+B-C 结构化归因结果，无法执行 L1 闭合审计。",
                location="rabc_attributions",
            ),
        )
    if input_data.checklist_result is None:
        issues.append(
            _issue(
                code="R1",
                message="缺少检查清单结构化结果，无法执行 R1 规则审计。",
                location="checklist_result",
            ),
        )
    if input_data.final_judgment is None:
        issues.append(
            _issue(
                code="R2",
                message="缺少显式最终判断，无法执行 R2 判定一致性审计。",
                location="final_judgment",
            ),
        )
    if input_data.derived_final_judgment is None:
        issues.append(
            _issue(
                code="R2",
                message="缺少系统派生最终判断，无法执行 R2 判定一致性审计。",
                location="derived_final_judgment",
            ),
        )
    if input_data.final_judgment_source is None:
        issues.append(
            _issue(
                code="R2",
                message="缺少最终判断来源，无法执行 R2 判定一致性审计。",
                location="final_judgment_source",
            ),
        )
    return tuple(issues)


def _audit_report_structure(
    report_markdown: str | None,
    required_chapter_titles: tuple[str, ...],
) -> tuple[AuditIssue, ...]:
    """执行 P1/P2/P3 报告结构审计。

    Args:
        report_markdown: 报告 Markdown。
        required_chapter_titles: 必要章节标题。

    Returns:
        结构审计问题。

    Raises:
        无显式抛出。
    """

    if report_markdown is None:
        return ()
    issues: list[AuditIssue] = []
    headings = _extract_headings(report_markdown)
    missing_titles = _missing_chapter_titles(headings, required_chapter_titles)
    if missing_titles:
        issues.append(
            _issue(
                code="P1",
                message=f"报告缺少必要章节：{'、'.join(missing_titles)}。",
                location="report_markdown",
            ),
        )
    short_locations = _short_content_locations(report_markdown)
    for location in short_locations:
        issues.append(
            _issue(
                code="P2",
                message="章节内容过短。",
                location=location,
                severity="reviewable",
            ),
        )
    if not _EVIDENCE_MARKER_PATTERN.search(report_markdown):
        issues.append(
            _issue(
                code="P3",
                message="报告缺少证据与出处或证据锚点。",
                location="report_markdown",
                severity="reviewable",
            ),
        )
    return tuple(issues)


def _resolve_chapter_blocks_for_audit(
    input_data: ProgrammaticAuditInput,
) -> tuple[tuple[RenderedChapterBlock, ...], tuple[AuditIssue, ...]]:
    """解析程序审计所需的渲染章节块。

    Args:
        input_data: 程序审计输入。

    Returns:
        章节块与解析问题；解析失败时返回空章节块和 P1 问题。

    Raises:
        无显式抛出。
    """

    if input_data.chapter_blocks:
        return input_data.chapter_blocks, ()
    if input_data.report_markdown is None:
        return (), ()
    try:
        return split_rendered_chapter_blocks(input_data.report_markdown), ()
    except ValueError as exc:
        return (), (
            _issue(
                code="P1",
                message=f"报告无法按 CHAPTER_CONTRACT 切分章节：{exc}",
                location="report_markdown",
            ),
        )


def _audit_minimum_chapter_evidence(
    chapter_blocks: tuple[RenderedChapterBlock, ...],
) -> tuple[AuditIssue, ...]:
    """执行每章最小证据行审计。

    Args:
        chapter_blocks: 已渲染章节块。

    Returns:
        P3 证据格式问题。

    Raises:
        无显式抛出。
    """

    issues: list[AuditIssue] = []
    for block in chapter_blocks:
        location = _chapter_location(block)
        if not _CHAPTER_EVIDENCE_LINE_PATTERN.search(block.body_markdown):
            issues.append(
                _issue(
                    code="P3",
                    message=f"模板第{block.chapter_id}章缺少章节内证据行。",
                    location=location,
                )
            )
        if EVIDENCE_APPENDIX_HEADING in block.body_markdown:
            issues.append(
                _issue(
                    code="P3",
                    message=f"模板第{block.chapter_id}章正文不应包含证据与出处附录。",
                    location=location,
                )
            )
    return tuple(issues)


def _audit_contract_conformance(
    chapter_blocks: tuple[RenderedChapterBlock, ...],
) -> tuple[AuditIssue, ...]:
    """执行确定性 CHAPTER_CONTRACT C2 审计。

    Args:
        chapter_blocks: 已渲染章节块。

    Returns:
        C2 契约问题。

    Raises:
        无显式抛出。
    """

    if not chapter_blocks:
        return ()

    issues: list[AuditIssue] = []
    issues.extend(_audit_chapter_block_metadata(chapter_blocks))
    rules = load_programmatic_contract_rules()
    coverage_manifest = load_contract_audit_coverage_manifest()
    marker_coverage_rules = tuple(
        rule
        for rule in coverage_manifest.must_answer_coverages
        if rule.coverage_kind == "programmatic_marker"
    )
    for block in chapter_blocks:
        for rule in rules.required_items:
            if rule.chapter_id != block.chapter_id:
                continue
            if not any(marker in block.body_markdown for marker in rule.markers_any):
                issues.append(
                    _issue(
                        code="C2",
                        message=f"模板第{block.chapter_id}章缺少 required_output_item：{rule.item_text}。",
                        location=f"{_chapter_location(block)}:{rule.item_text}",
                    )
                )
        issues.extend(_audit_must_answer_programmatic_markers(block, marker_coverage_rules))
        for rule in rules.forbidden_contents:
            if rule.chapter_id != block.chapter_id:
                continue
            matched_markers = tuple(
                marker for marker in rule.forbidden_markers_any if marker in block.body_markdown
            )
            if matched_markers:
                issues.append(
                    _issue(
                        code="C2",
                        message=(
                            f"模板第{block.chapter_id}章包含 must_not_cover 禁止内容："
                            f"{'、'.join(matched_markers)}。"
                        ),
                        location=f"{_chapter_location(block)}:{rule.item_text}",
                    )
                )
    return tuple(issues)


def _audit_must_answer_programmatic_markers(
    block: RenderedChapterBlock,
    marker_coverage_rules: tuple[ContractMustAnswerCoverageRule, ...],
) -> list[AuditIssue]:
    """审计 must_answer 的独立确定性 marker 规则。

    Args:
        block: 已渲染章节块。
        marker_coverage_rules: 覆盖类型为 `programmatic_marker` 的 must_answer 规则。

    Returns:
        C2 契约问题列表。

    Raises:
        无显式抛出。
    """

    issues: list[AuditIssue] = []
    for rule in marker_coverage_rules:
        if rule.chapter_id != block.chapter_id:
            continue
        if any(marker in block.body_markdown for marker in rule.markers_any):
            continue
        issues.append(
            _issue(
                code="C2",
                message=f"模板第{block.chapter_id}章缺少 must_answer marker：{rule.question_text}。",
                location=f"{_chapter_location(block)}:{rule.question_text}",
            )
        )
    return issues


def _audit_chapter_block_metadata(
    chapter_blocks: tuple[RenderedChapterBlock, ...],
) -> tuple[AuditIssue, ...]:
    """审计章节块与契约元数据一致性。

    Args:
        chapter_blocks: 已渲染章节块。

    Returns:
        C2 元数据问题。

    Raises:
        无显式抛出。
    """

    issues: list[AuditIssue] = []
    chapter_ids = tuple(block.chapter_id for block in chapter_blocks)
    if chapter_ids != tuple(range(8)):
        issues.append(
            _issue(
                code="C2",
                message=f"渲染章节块必须按 0..7 顺序完整出现，实际为 {chapter_ids}。",
                location="chapter_blocks",
            )
        )
    for block in chapter_blocks:
        location = _chapter_location(block)
        expected_heading = get_template_chapter_heading(block.chapter_id)
        if block.chapter_id != block.contract.chapter_id:
            issues.append(_issue(code="C2", message="章节编号与契约编号不一致。", location=location))
        if block.title != block.contract.title:
            issues.append(_issue(code="C2", message="章节标题与契约标题不一致。", location=location))
        if block.heading != expected_heading:
            issues.append(_issue(code="C2", message="章节 Markdown 标题与契约标题不一致。", location=location))
    return tuple(issues)


def _audit_item_rule_compliance(
    chapter_blocks: tuple[RenderedChapterBlock, ...],
    decisions: tuple[TemplateItemRuleDecision, ...],
    audit_context: TemplateItemRuleAuditContext,
) -> tuple[AuditIssue, ...]:
    """执行 ITEM_RULE 确定性渲染/删除合规审计。

    Args:
        chapter_blocks: 已渲染章节块。
        decisions: renderer 产生的 ITEM_RULE 决策。
        audit_context: ITEM_RULE 审计上下文。

    Returns:
        C2 ITEM_RULE 合规问题。

    Raises:
        无显式抛出。
    """

    if not chapter_blocks:
        return ()
    if audit_context == "identity_missing" and not decisions:
        return ()
    if audit_context == "identity_present" and not decisions:
        return (
            _issue(
                code="C2",
                message="基金身份存在但缺少 ITEM_RULE 决策，无法验证条件型段落合规。",
                location="item_rule_decisions",
            ),
        )

    issues: list[AuditIssue] = []
    seen_rule_ids: set[str] = set()
    blocks_by_id = {block.chapter_id: block for block in chapter_blocks}
    for decision in decisions:
        if decision.rule_id in seen_rule_ids:
            issues.append(
                _issue(
                    code="C2",
                    message=f"ITEM_RULE 决策重复：{decision.rule_id}。",
                    location="item_rule_decisions",
                )
            )
            continue
        seen_rule_ids.add(decision.rule_id)
        issues.extend(_audit_single_item_rule_decision(decision, blocks_by_id))
    return tuple(issues)


def _audit_single_item_rule_decision(
    decision: TemplateItemRuleDecision,
    blocks_by_id: dict[int, RenderedChapterBlock],
) -> list[AuditIssue]:
    """审计单条 ITEM_RULE 决策与对应章节块是否一致。

    Args:
        decision: renderer 产生的 ITEM_RULE 决策。
        blocks_by_id: 按章节编号索引的渲染章节块。

    Returns:
        单条决策产生的 C2 问题。

    Raises:
        无显式抛出。
    """

    issues: list[AuditIssue] = []
    try:
        rule = get_template_item_rule(decision.rule_id)
    except ValueError:
        return [
            _issue(
                code="C2",
                message=f"ITEM_RULE 决策引用未知规则：{decision.rule_id}。",
                location="item_rule_decisions",
            )
        ]

    if decision.chapter_id != rule.chapter_id:
        issues.append(
            _issue(
                code="C2",
                message=(
                    f"ITEM_RULE {decision.rule_id} 决策章节 {decision.chapter_id} "
                    f"与 manifest 章节 {rule.chapter_id} 不一致。"
                ),
                location=f"item_rule_decisions:{decision.rule_id}",
            )
        )
    block = blocks_by_id.get(decision.chapter_id)
    if block is None:
        issues.append(
            _issue(
                code="C2",
                message=f"ITEM_RULE {decision.rule_id} 指向的章节块不存在：{decision.chapter_id}。",
                location=f"item_rule_decisions:{decision.rule_id}",
            )
        )
        return issues

    present = rendered_segment_present(block.body_markdown, rule)
    location = f"{_chapter_location(block)}:{decision.rule_id}"
    if decision.status == "render" and not present:
        issues.append(
            _issue(
                code="C2",
                message=f"ITEM_RULE {decision.rule_id} 要求渲染，但章节内缺少对应段落标记。",
                location=location,
            )
        )
    elif decision.status == "delete" and present:
        issues.append(
            _issue(
                code="C2",
                message=f"ITEM_RULE {decision.rule_id} 要求删除，但章节内仍包含对应段落标记。",
                location=location,
            )
        )
    elif decision.status not in {"render", "delete"}:
        issues.append(
            _issue(
                code="C2",
                message=f"ITEM_RULE {decision.rule_id} 决策状态不受支持：{decision.status}。",
                location=location,
            )
        )
    return issues


def _audit_tracking_error_source_guard(
    chapter_blocks: tuple[RenderedChapterBlock, ...],
    tracking_error: ExtractedField[TrackingErrorValue] | None,
) -> tuple[AuditIssue, ...]:
    """审计跟踪误差段落是否由结构化跟踪误差字段支撑。

    Args:
        chapter_blocks: 已渲染章节块。
        tracking_error: 跟踪误差结构化字段。

    Returns:
        跟踪误差来源边界问题。

    Raises:
        无显式抛出。
    """

    chapter_2 = _block_by_id(chapter_blocks, 2)
    if chapter_2 is None or "#### 跟踪误差分析" not in chapter_2.body_markdown:
        return ()
    segment = _segment_after_heading(chapter_2.body_markdown, "#### 跟踪误差分析")
    if "- 跟踪误差：数据不足" in segment:
        return ()
    if (
        tracking_error is None
        or tracking_error.value is None
        or tracking_error.extraction_mode not in {"direct", "derived"}
    ):
        return (
            _issue(
                code="C2",
                message="跟踪误差非数据不足输出缺少 structured_data.tracking_error 支撑。",
                location="chapter_2:tracking_error",
            ),
        )
    if tracking_error.value.source_type == "direct_disclosure" and not _has_annual_report_anchor(
        tracking_error.anchors
    ):
        return (
            _issue(
                code="C2",
                message="年报直接披露跟踪误差缺少 annual_report 锚点。",
                location="chapter_2:tracking_error",
            ),
        )
    if tracking_error.value.source_type == "derived" and not tracking_error.value.provenance_note:
        return (
            _issue(
                code="C2",
                message="派生跟踪误差缺少公式或来源 provenance。",
                location="chapter_2:tracking_error",
            ),
        )
    return ()


def _audit_index_profile_source_guard(
    chapter_blocks: tuple[RenderedChapterBlock, ...],
    index_profile: ExtractedField[IndexProfileValue] | None,
) -> tuple[AuditIssue, ...]:
    """审计指数编制方法和成分股没有被 benchmark-only 证据误支撑。

    Args:
        chapter_blocks: 已渲染章节块。
        index_profile: 指数画像结构化字段。

    Returns:
        指数画像来源边界问题。

    Raises:
        无显式抛出。
    """

    chapter_1 = _block_by_id(chapter_blocks, 1)
    if chapter_1 is None or "#### 指数编制规则与成分股" not in chapter_1.body_markdown:
        return ()
    segment = _segment_after_heading(chapter_1.body_markdown, "#### 指数编制规则与成分股")
    issues: list[AuditIssue] = []
    profile_value = index_profile.value if index_profile is not None else None
    if _line_is_not_insufficient(segment, "- 编制方法：") and not (
        profile_value is not None
        and profile_value.methodology_availability in {"direct_disclosure", "source_reference"}
    ):
        issues.append(
            _issue(
                code="C2",
                message="指数编制方法不能由 benchmark-only 证据替代。",
                location="chapter_1:index_methodology",
            )
        )
    if _line_is_not_insufficient(segment, "- 成分股：") and not (
        profile_value is not None
        and profile_value.constituents_availability in {"direct_disclosure", "source_reference"}
    ):
        issues.append(
            _issue(
                code="C2",
                message="指数成分股不能由 benchmark-only 证据替代。",
                location="chapter_1:index_constituents",
            )
        )
    return tuple(issues)


def _block_by_id(
    chapter_blocks: tuple[RenderedChapterBlock, ...],
    chapter_id: int,
) -> RenderedChapterBlock | None:
    """按章节编号查找章节块。

    Args:
        chapter_blocks: 已渲染章节块。
        chapter_id: 章节编号。

    Returns:
        命中的章节块；不存在时返回 `None`。

    Raises:
        无显式抛出。
    """

    for block in chapter_blocks:
        if block.chapter_id == chapter_id:
            return block
    return None


def _segment_after_heading(markdown: str, heading: str) -> str:
    """截取指定四级标题后的段落。

    Args:
        markdown: 章节 Markdown。
        heading: 四级标题。

    Returns:
        标题和后续 bullet 文本。

    Raises:
        无显式抛出。
    """

    lines = markdown.splitlines()
    try:
        start = lines.index(heading)
    except ValueError:
        return ""
    end = len(lines)
    for index in range(start + 1, len(lines)):
        if lines[index].startswith("#### ") or lines[index].startswith("> 📎 证据"):
            end = index
            break
    return "\n".join(lines[start:end])


def _line_is_not_insufficient(segment: str, prefix: str) -> bool:
    """判断段落中某个 bullet 是否不是数据不足。

    Args:
        segment: ITEM_RULE 段落文本。
        prefix: 待检查 bullet 前缀。

    Returns:
        找到对应行且不含数据不足时返回 `True`。

    Raises:
        无显式抛出。
    """

    for line in segment.splitlines():
        if line.startswith(prefix):
            return "数据不足" not in line
    return False


def _has_annual_report_anchor(anchors: tuple[object, ...]) -> bool:
    """判断锚点集合是否包含年报锚点。

    Args:
        anchors: 待检查锚点集合。

    Returns:
        任一锚点来源为 annual_report 时返回 `True`。

    Raises:
        无显式抛出。
    """

    return any(getattr(anchor, "source_kind", None) == "annual_report" for anchor in anchors)


def _audit_rabc_closure(rabc_attributions: tuple[RabcAttribution, ...]) -> tuple[AuditIssue, ...]:
    """执行 L1 R=A+B-C 计算闭合审计。

    Args:
        rabc_attributions: R=A+B-C 归因结果列表。

    Returns:
        L1 审计问题。

    Raises:
        无显式抛出。
    """

    issues: list[AuditIssue] = []
    for attribution in rabc_attributions:
        if attribution.status != "computed":
            continue
        if _rabc_has_missing_components(attribution):
            issues.append(
                _issue(
                    code="L1",
                    message="R=A+B-C 已标记 computed，但关键计算字段缺失。",
                    location=attribution.period,
                ),
            )
            continue
        components = (
            attribution.total_return_r,
            attribution.beta_return_b,
            attribution.alpha_return_a,
            attribution.explicit_cost_c,
            attribution.net_excess_return,
        )
        if any(v is None for v in components):
            issues.append(
                _issue(
                    code="L1",
                    message="R=A+B-C 关键计算字段在 computed 状态下意外为 None。",
                    location=attribution.period,
                ),
            )
            continue
        alpha_expected = attribution.total_return_r - attribution.beta_return_b
        net_excess_expected = attribution.alpha_return_a - attribution.explicit_cost_c
        if _abs_decimal(alpha_expected - attribution.alpha_return_a) > _L1_TOLERANCE:
            issues.append(
                _issue(
                    code="L1",
                    message="A 不等于 R-B。",
                    location=attribution.period,
                ),
            )
        if _abs_decimal(net_excess_expected - attribution.net_excess_return) > _L1_TOLERANCE:
            issues.append(
                _issue(
                    code="L1",
                    message="净超额收益不等于 A-C。",
                    location=attribution.period,
                ),
            )
    return tuple(issues)


def _audit_checklist_rules(
    checklist_result: ChecklistResult | None,
    valuation_state_resolution: ValuationStateResolution | None,
    report_markdown: str | None,
) -> tuple[AuditIssue, ...]:
    """执行 R1 检查清单规则审计。

    Args:
        checklist_result: 检查清单结果。
        valuation_state_resolution: 估值状态结构化真源。
        report_markdown: 报告 Markdown，用于免责声明显式展示审计。

    Returns:
        R1 审计问题。

    Raises:
        无显式抛出。
    """

    if checklist_result is None:
        return ()
    issues: list[AuditIssue] = []
    if len(checklist_result.items) != 7:
        issues.append(_issue(code="R1", message="检查清单不是 7 个问题。", location="checklist"))
    expected_signal = _expected_overall_signal(checklist_result.items)
    if checklist_result.overall_signal != expected_signal:
        issues.append(
            _issue(
                code="R1",
                message=f"检查清单汇总信号应为 {expected_signal}，实际为 {checklist_result.overall_signal}。",
                location="checklist.overall_signal",
            ),
        )
    for item in checklist_result.items:
        expected_status = _status_for_signal(item.signal)
        if expected_status is None:
            issues.append(
                _issue(
                    code="R1",
                    message=f"问题 {item.code} 的信号未知：{item.signal}。",
                    location=item.code,
                ),
            )
            continue
        if item.status != expected_status:
            issues.append(
                _issue(
                    code="R1",
                    message=f"问题 {item.code} 的状态应为 {expected_status}，实际为 {item.status}。",
                    location=item.code,
                ),
            )
    issues.extend(
        _audit_valuation_resolution(
            checklist_result=checklist_result,
            valuation_state_resolution=valuation_state_resolution,
            report_markdown=report_markdown,
        )
    )
    return tuple(issues)


def _audit_valuation_resolution(
    *,
    checklist_result: ChecklistResult,
    valuation_state_resolution: ValuationStateResolution | None,
    report_markdown: str | None,
) -> tuple[AuditIssue, ...]:
    """审计检查清单第 6 问与估值结构化真源一致性。

    Args:
        checklist_result: 检查清单结果。
        valuation_state_resolution: 估值状态结构化真源。
        report_markdown: 报告 Markdown。

    Returns:
        R1 估值证据问题。

    Raises:
        无显式抛出。
    """

    valuation_item = _valuation_item(checklist_result)
    if valuation_item is None:
        return (
            _issue(
                code="R1",
                message="检查清单缺少 valuation 问题。",
                location="checklist.valuation",
            ),
        )
    if valuation_state_resolution is None:
        if any(anchor.source_kind == "external_api" for anchor in valuation_item.anchors):
            return (
                _issue(
                    code="R1",
                    message="估值检查项包含外部温度计锚点但缺少结构化估值真源。",
                    location="valuation_state_resolution",
                ),
            )
        # 兼容历史手工构造的审计输入；Service/renderer 新路径必须显式传入 resolution。
        return ()
    issues: list[AuditIssue] = []
    expected_signal = _valuation_signal_for_state(valuation_state_resolution.state)
    if valuation_item.signal != expected_signal:
        issues.append(
            _issue(
                code="R1",
                message=(
                    f"valuation 信号应与结构化估值状态一致："
                    f"{expected_signal}，实际为 {valuation_item.signal}。"
                ),
                location="checklist.valuation.signal",
            )
        )
    if not set(valuation_state_resolution.anchors).issubset(set(valuation_item.anchors)):
        issues.append(
            _issue(
                code="R1",
                message="valuation 检查项锚点必须覆盖估值结构化真源锚点。",
                location="checklist.valuation.anchors",
            )
        )
    issues.extend(_audit_valuation_resolution_fields(valuation_state_resolution, report_markdown))
    return tuple(issues)


def _valuation_item(checklist_result: ChecklistResult) -> ChecklistItem | None:
    """读取检查清单估值问题。

    Args:
        checklist_result: 检查清单结果。

    Returns:
        valuation 检查项；缺失时返回 `None`。

    Raises:
        无显式抛出。
    """

    for item in checklist_result.items:
        if item.code == "valuation":
            return item
    return None


def _valuation_signal_for_state(state: str) -> str:
    """把估值状态映射为检查清单信号。

    Args:
        state: 估值状态。

    Returns:
        检查清单信号。

    Raises:
        无显式抛出。
    """

    return {"low": "green", "fair": "yellow", "high": "red"}.get(state, "gray")


def _audit_valuation_resolution_fields(
    resolution: ValuationStateResolution,
    report_markdown: str | None,
) -> list[AuditIssue]:
    """审计估值结构化真源字段完整性。

    Args:
        resolution: 估值状态结构化真源。
        report_markdown: 报告 Markdown。

    Returns:
        R1 问题列表。

    Raises:
        无显式抛出。
    """

    issues: list[AuditIssue] = []
    if resolution.source == "self_owned_thermometer" and resolution.state != "unavailable":
        missing_fields = _missing_available_thermometer_fields(resolution)
        if missing_fields:
            issues.append(
                _issue(
                    code="R1",
                    message=f"自动估值缺少必要温度计字段：{'、'.join(missing_fields)}。",
                    location="valuation_state_resolution",
                )
            )
        if not any(anchor.source_kind == "external_api" for anchor in resolution.anchors):
            issues.append(
                _issue(
                    code="R1",
                    message="自动估值必须携带 external_api 温度计锚点。",
                    location="valuation_state_resolution.anchors",
                )
            )
        issues.extend(_audit_thermometer_anchor_identity(resolution))
    if resolution.source == "explicit_user_input" and not any(
        anchor.source_kind == "derived" and anchor.section_id == "user_input"
        for anchor in resolution.anchors
    ):
        issues.append(
            _issue(
                code="R1",
                message="显式估值输入必须携带 user_input derived 锚点。",
                location="valuation_state_resolution.anchors",
            )
        )
    if resolution.source in {"unavailable_mapping", "unavailable_thermometer"}:
        if resolution.state != "unavailable":
            issues.append(
                _issue(
                    code="R1",
                    message="不可用估值来源必须映射为 unavailable 灰灯。",
                    location="valuation_state_resolution.state",
                )
            )
        if not (resolution.reason.strip() or resolution.unavailable_reason):
            issues.append(
                _issue(
                    code="R1",
                    message="不可用估值来源必须保留原因。",
                    location="valuation_state_resolution.reason",
                )
            )
        if resolution.source == "unavailable_thermometer":
            issues.extend(_audit_unavailable_thermometer_anchor(resolution))
    if resolution.disclaimer_required:
        if not resolution.disclaimer:
            issues.append(
                _issue(
                    code="R1",
                    message="温度计估值要求展示免责声明但缺少 disclaimer 字段。",
                    location="valuation_state_resolution.disclaimer",
                )
            )
        elif report_markdown is not None and resolution.disclaimer not in report_markdown:
            issues.append(
                _issue(
                    code="R1",
                    message="报告未显式展示自建温度计免责声明。",
                    location="report_markdown",
                )
            )
    return issues


def _audit_unavailable_thermometer_anchor(
    resolution: ValuationStateResolution,
) -> list[AuditIssue]:
    """审计不可用温度计路径是否保留失败 provenance 锚点。

    Args:
        resolution: 估值状态结构化真源。

    Returns:
        R1 问题列表。

    Raises:
        无显式抛出。
    """

    if any(anchor.source_kind == "external_api" and anchor.section_id == "thermometer" for anchor in resolution.anchors):
        return []
    unavailable_reason = resolution.unavailable_reason or resolution.reason
    for anchor in resolution.anchors:
        if (
            anchor.source_kind == "derived"
            and anchor.section_id == "thermometer"
            and anchor.row_locator is not None
            and anchor.row_locator.endswith(":calculation_error")
            and anchor.note is not None
            and unavailable_reason in anchor.note
        ):
            return []
    return [
        _issue(
            code="R1",
            message="不可用温度计路径必须携带 external_api 温度计锚点或包含失败原因的 derived thermometer failure 锚点。",
            location="valuation_state_resolution.anchors",
        )
    ]


def _missing_available_thermometer_fields(
    resolution: ValuationStateResolution,
) -> tuple[str, ...]:
    """列出自动估值可用读数缺失字段。

    Args:
        resolution: 估值状态结构化真源。

    Returns:
        缺失字段名元组。

    Raises:
        无显式抛出。
    """

    required = {
        "index_code": resolution.index_code,
        "index_name": resolution.index_name,
        "temperature": resolution.temperature,
        "pe_percentile": resolution.pe_percentile,
        "pb_percentile": resolution.pb_percentile,
        "data_date": resolution.data_date,
        "lookback_start": resolution.lookback_start,
        "lookback_end": resolution.lookback_end,
        "thermometer_source": resolution.thermometer_source,
        "cached": resolution.cached,
        "stale": resolution.stale,
        "disclaimer": resolution.disclaimer,
    }
    return tuple(name for name, value in required.items() if value is None or value == "")


def _audit_thermometer_anchor_identity(
    resolution: ValuationStateResolution,
) -> list[AuditIssue]:
    """审计温度计锚点是否标识同一指数和数据日期。

    Args:
        resolution: 估值状态结构化真源。

    Returns:
        R1 问题列表。

    Raises:
        无显式抛出。
    """

    issues: list[AuditIssue] = []
    external_anchors = tuple(anchor for anchor in resolution.anchors if anchor.source_kind == "external_api")
    if not external_anchors:
        return issues
    expected_row = f"{resolution.index_code}:{resolution.data_date}"
    if not any(anchor.row_locator == expected_row for anchor in external_anchors):
        issues.append(
            _issue(
                code="R1",
                message="温度计锚点未标识结构化真源中的指数代码和数据日期。",
                location="valuation_state_resolution.anchors",
            )
        )
    if not any(anchor.table_id == resolution.thermometer_source for anchor in external_anchors):
        issues.append(
            _issue(
                code="R1",
                message="温度计锚点未标识结构化真源中的数据来源。",
                location="valuation_state_resolution.anchors",
            )
        )
    return issues


def _audit_final_judgment(
    checklist_result: ChecklistResult | None,
    final_judgment: FinalJudgment | None,
    derived_final_judgment: FinalJudgment | None,
    final_judgment_source: FinalJudgmentSource | None,
) -> tuple[AuditIssue, ...]:
    """执行 R2 最终判定一致性审计。

    Args:
        checklist_result: 检查清单结果。
        final_judgment: selected 最终判断。
        derived_final_judgment: 系统派生最终判断。
        final_judgment_source: selected 判断来源。

    Returns:
        R2 审计问题。

    Raises:
        无显式抛出。
    """

    issues: list[AuditIssue] = []
    if final_judgment is not None and derived_final_judgment is not None:
        if final_judgment_source == "derived" and final_judgment != derived_final_judgment:
            issues.append(
                _issue(
                    code="R2",
                    message="系统派生路径下 selected 判断必须等于 derived 判断。",
                    location="final_judgment",
                ),
            )
        elif final_judgment_source == "developer_override" and final_judgment != derived_final_judgment:
            issues.append(
                _issue(
                    code="R2",
                    message="开发覆盖与系统派生判断冲突。",
                    location="final_judgment",
                ),
            )
        elif final_judgment_source not in {"derived", "developer_override", None}:
            issues.append(
                _issue(
                    code="R2",
                    message="最终判断来源必须是 derived 或 developer_override。",
                    location="final_judgment_source",
                ),
            )
    if checklist_result is None or final_judgment is None:
        return tuple(issues)
    if checklist_result.red_items and final_judgment != "suggest_replace":
        issues.append(
            _issue(
                code="R2",
                message="存在红灯检查项时，最终判断不能是值得持有或仅需关注。",
                location="final_judgment",
            ),
        )
    if checklist_result.overall_signal == "green" and final_judgment == "suggest_replace":
        issues.append(
            _issue(
                code="R2",
                message="检查清单全绿时，最终判断不应建议替换。",
                location="final_judgment",
            ),
        )
    return tuple(issues)


def _extract_headings(report_markdown: str) -> tuple[str, ...]:
    """提取 Markdown 标题文本。

    Args:
        report_markdown: 报告 Markdown。

    Returns:
        标题文本元组。

    Raises:
        无显式抛出。
    """

    return tuple(match.group(1).strip() for match in _HEADING_PATTERN.finditer(report_markdown))


def _missing_chapter_titles(
    headings: tuple[str, ...],
    required_chapter_titles: tuple[str, ...],
) -> tuple[str, ...]:
    """计算缺失章节标题。

    Args:
        headings: 已提取标题。
        required_chapter_titles: 必要章节标题。

    Returns:
        缺失章节标题。

    Raises:
        无显式抛出。
    """

    missing: list[str] = []
    for required_title in required_chapter_titles:
        if not any(required_title in heading for heading in headings):
            missing.append(required_title)
    return tuple(missing)


def _chapter_location(block: RenderedChapterBlock) -> str:
    """渲染章节块审计位置。

    Args:
        block: 已渲染章节块。

    Returns:
        章节位置文本。

    Raises:
        无显式抛出。
    """

    return f"chapter_{block.chapter_id}:{block.title}"


def _short_content_locations(report_markdown: str) -> tuple[str, ...]:
    """查找内容过短章节。

    Args:
        report_markdown: 报告 Markdown。

    Returns:
        内容过短章节标题。

    Raises:
        无显式抛出。
    """

    heading_matches = list(_CHAPTER_HEADING_PATTERN.finditer(report_markdown))
    locations: list[str] = []
    for index, match in enumerate(heading_matches):
        start = match.end()
        end = heading_matches[index + 1].start() if index + 1 < len(heading_matches) else len(report_markdown)
        content = report_markdown[start:end].strip()
        if len(content) < _MIN_CONTENT_LENGTH:
            locations.append(match.group(1).strip())
    return tuple(locations)


def _rabc_has_missing_components(attribution: RabcAttribution) -> bool:
    """判断 R=A+B-C 归因是否缺少闭合字段。

    Args:
        attribution: R=A+B-C 归因结果。

    Returns:
        存在缺失字段时返回 `True`。

    Raises:
        无显式抛出。
    """

    return any(
        value is None
        for value in (
            attribution.total_return_r,
            attribution.beta_return_b,
            attribution.alpha_return_a,
            attribution.explicit_cost_c,
            attribution.net_excess_return,
        )
    )


def _expected_overall_signal(items: tuple[ChecklistItem, ...]) -> str:
    """按检查清单问题信号计算预期汇总信号。

    Args:
        items: 检查清单问题。

    Returns:
        预期汇总信号。

    Raises:
        无显式抛出。
    """

    if not items:
        return "gray"
    return max((item.signal for item in items), key=lambda signal: _CHECKLIST_SIGNAL_ORDER.get(signal, 3))


def _status_for_signal(signal: str) -> str | None:
    """按信号计算预期状态。

    Args:
        signal: 红黄绿灰灯。

    Returns:
        预期状态。

    Raises:
        无显式抛出。
    """

    status_by_signal = {
        "green": "pass",
        "yellow": "watch",
        "red": "block",
        "gray": "insufficient_data",
    }
    return status_by_signal.get(signal)


def _abs_decimal(value: Decimal) -> Decimal:
    """计算 Decimal 绝对值。

    Args:
        value: Decimal 数值。

    Returns:
        绝对值。

    Raises:
        无显式抛出。
    """

    return abs(value)


def _issue(
    *,
    code: AuditRuleCode,
    message: str,
    location: str | None = None,
    severity: AuditSeverity = "blocker",
) -> AuditIssue:
    """构造程序审计问题。

    Args:
        code: 审计规则码。
        message: 问题说明。
        location: 问题位置。
        severity: 阻断级别，默认 blocker。

    Returns:
        审计问题。

    Raises:
        无显式抛出。
    """

    return AuditIssue(
        code=code,
        status="fail",
        severity=severity,
        message=message,
        location=location,
    )
