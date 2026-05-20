"""程序化审计规则。

本模块属于基金 Capability 层，服务 `docs/design.md` 第 5.2 节的 MVP 程序审计。
它只消费报告文本和 P2 结构化结果，不直接读取年报、PDF、缓存或文档仓库。
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from decimal import Decimal
from typing import Final, Literal

from fund_agent.fund.analysis.checklist import ChecklistItem, ChecklistResult
from fund_agent.fund.analysis.r_abc import RabcAttribution
from fund_agent.fund.audit.contract_rules import load_programmatic_contract_rules
from fund_agent.fund.template.chapter_blocks import (
    EVIDENCE_APPENDIX_HEADING,
    RenderedChapterBlock,
    get_template_chapter_heading,
    split_rendered_chapter_blocks,
)
from fund_agent.fund.template.contracts import load_template_contract_manifest

AuditRuleCode = Literal["P1", "P2", "P3", "C2", "L1", "R1", "R2"]
AuditSeverity = Literal["blocker", "reviewable"]
AuditStatus = Literal["pass", "fail"]
FinalJudgment = Literal["worth_holding", "needs_attention", "suggest_replace"]

_MIN_CONTENT_LENGTH: Final[int] = 10
_L1_TOLERANCE: Final[Decimal] = Decimal("0.0001")
_EVIDENCE_MARKER_PATTERN: Final[re.Pattern[str]] = re.compile(r"(证据与出处|📎\s*证据|年报\d{4}§)")
_CHAPTER_EVIDENCE_LINE_PATTERN: Final[re.Pattern[str]] = re.compile(r"(?m)^>\s*📎\s*证据：")
_HEADING_PATTERN: Final[re.Pattern[str]] = re.compile(r"^#{1,6}\s+(.+?)\s*$", re.MULTILINE)
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
        final_judgment: 最终判断，用于 R2 与检查清单信号一致性审计。
        required_chapter_titles: 必要章节标题列表。
        chapter_blocks: 已渲染章节块，用于 P3 每章证据和 C2 契约审计。
    """

    report_markdown: str | None = None
    rabc_attributions: tuple[RabcAttribution, ...] = ()
    checklist_result: ChecklistResult | None = None
    final_judgment: FinalJudgment | None = None
    required_chapter_titles: tuple[str, ...] = _REQUIRED_CHAPTER_TITLES
    chapter_blocks: tuple[RenderedChapterBlock, ...] = ()


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
        *_audit_rabc_closure(input_data.rabc_attributions),
        *_audit_checklist_rules(input_data.checklist_result),
        *_audit_final_judgment(input_data.checklist_result, input_data.final_judgment),
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
            ),
        )
    if not _EVIDENCE_MARKER_PATTERN.search(report_markdown):
        issues.append(
            _issue(
                code="P3",
                message="报告缺少证据与出处或证据锚点。",
                location="report_markdown",
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
        assert attribution.total_return_r is not None
        assert attribution.beta_return_b is not None
        assert attribution.alpha_return_a is not None
        assert attribution.explicit_cost_c is not None
        assert attribution.net_excess_return is not None
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


def _audit_checklist_rules(checklist_result: ChecklistResult | None) -> tuple[AuditIssue, ...]:
    """执行 R1 检查清单规则审计。

    Args:
        checklist_result: 检查清单结果。

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
    return tuple(issues)


def _audit_final_judgment(
    checklist_result: ChecklistResult | None,
    final_judgment: FinalJudgment | None,
) -> tuple[AuditIssue, ...]:
    """执行 R2 最终判定一致性审计。

    Args:
        checklist_result: 检查清单结果。
        final_judgment: 最终判断。

    Returns:
        R2 审计问题。

    Raises:
        无显式抛出。
    """

    if checklist_result is None or final_judgment is None:
        return ()
    if checklist_result.red_items and final_judgment != "suggest_replace":
        return (
            _issue(
                code="R2",
                message="存在红灯检查项时，最终判断不能是值得持有或仅需关注。",
                location="final_judgment",
            ),
        )
    if checklist_result.overall_signal == "green" and final_judgment == "suggest_replace":
        return (
            _issue(
                code="R2",
                message="检查清单全绿时，最终判断不应建议替换。",
                location="final_judgment",
            ),
        )
    return ()


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

    heading_matches = list(_HEADING_PATTERN.finditer(report_markdown))
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
) -> AuditIssue:
    """构造程序审计问题。

    Args:
        code: 审计规则码。
        message: 问题说明。
        location: 问题位置。

    Returns:
        审计问题。

    Raises:
        无显式抛出。
    """

    return AuditIssue(
        code=code,
        status="fail",
        severity="blocker",
        message=message,
        location=location,
    )
