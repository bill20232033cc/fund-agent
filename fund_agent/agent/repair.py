"""Agent 修复策略，见基金分析模板第 1-6 章。

本模块只根据 Fund audit typed result 和 Agent repair budget 做确定性决策。
它不读取外部来源，不发起 source probing，不导入 Service/Host，也不隐藏 retry。
"""

from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Literal

from fund_agent.fund.chapter_auditor import (
    ChapterAuditIssue,
    ChapterAuditRepairHint,
    ChapterAuditResult,
)
from fund_agent.fund.chapter_writer import ChapterRepairContext, ChapterWriteResult

AgentRepairAction = Literal["none", "regenerate", "needs_more_facts", "stop"]
AgentRepairStopReason = Literal[
    "none",
    "llm_unavailable",
    "auditor_failed",
    "auditor_blocked",
    "repair_budget_exhausted",
    "needs_more_facts",
]
_COMMENT_RE: re.Pattern[str] = re.compile(r"<!--.*?-->")
_WRITER_INVALID_ANCHOR_CORRECTION: str = (
    "使用精确 anchor marker 语法 `<!-- anchor:<anchor_id> -->`；"
    "只使用 allowed anchor IDs；删除 malformed、extra-space、synthesized 或 free-form anchor comments；"
    "bond_risk_evidence 内部/组级 anchors 未列入 allowed ChapterEvidenceAnchor IDs 时不得引用。"
)


@dataclass(frozen=True, slots=True, kw_only=True)
class AgentRepairDecision:
    """Agent 单次审计后的 repair 决策。

    Args:
        action: repair action。
        reason: 中文原因。
        stop_reason: 当 action 表示停止时的停止原因。
        source_repair_hint: Fund audit 聚合 repair hint。
        issue_ids: 触发 repair 的 issue id。
        consumes_content_repair_budget: 本决策是否消耗内容修复预算。

    Raises:
        无显式抛出。
    """

    action: AgentRepairAction
    reason: str
    stop_reason: AgentRepairStopReason
    source_repair_hint: ChapterAuditRepairHint
    issue_ids: tuple[str, ...]
    consumes_content_repair_budget: bool = False


def decide_repair(
    audit_result: ChapterAuditResult,
    *,
    remaining_budget: int,
    auditor_available: bool,
    run_llm_audit: bool,
) -> AgentRepairDecision:
    """根据 Fund 审计结果决定 Agent repair 行为。

    Args:
        audit_result: Fund 章节审计结果。
        remaining_budget: 当前审计失败后剩余 regenerate 次数。
        auditor_available: 是否显式注入 auditor client。
        run_llm_audit: 当前策略是否要求 LLM 审计。

    Returns:
        Agent repair 决策。

    Raises:
        无显式抛出。
    """

    issue_ids = _audit_issue_ids(audit_result)
    repair_hint = audit_result.repair_hint
    if audit_result.accepted:
        return AgentRepairDecision(
            action="none",
            reason="章节审计已通过，无需修复。",
            stop_reason="none",
            source_repair_hint=repair_hint,
            issue_ids=issue_ids,
        )
    if run_llm_audit and not auditor_available:
        return AgentRepairDecision(
            action="stop",
            reason="缺少显式注入的章节 LLM 审计 client，不能通过重写修复。",
            stop_reason="llm_unavailable",
            source_repair_hint=repair_hint,
            issue_ids=issue_ids,
        )
    if audit_result.llm.status == "blocked" and _has_llm_unavailable_issue(audit_result):
        return AgentRepairDecision(
            action="stop",
            reason="LLM 审计不可用，停止本章且不重试 writer。",
            stop_reason="llm_unavailable",
            source_repair_hint=repair_hint,
            issue_ids=issue_ids,
        )
    if repair_hint == "needs_more_facts":
        return AgentRepairDecision(
            action="needs_more_facts",
            reason="审计要求更多同源事实，Agent 不进行 source probing。",
            stop_reason="needs_more_facts",
            source_repair_hint=repair_hint,
            issue_ids=issue_ids,
        )
    if repair_hint == "none":
        return AgentRepairDecision(
            action="stop",
            reason="审计未提供安全修复依据。",
            stop_reason=_auditor_failure_stop_reason(audit_result),
            source_repair_hint=repair_hint,
            issue_ids=issue_ids,
        )
    if remaining_budget <= 0:
        return AgentRepairDecision(
            action="stop",
            reason="章节修复预算耗尽。",
            stop_reason="repair_budget_exhausted",
            source_repair_hint=repair_hint,
            issue_ids=issue_ids,
        )
    if audit_result.status in ("blocked", "fail") and repair_hint in ("patch", "regenerate"):
        return AgentRepairDecision(
            action="regenerate",
            reason="MVP 暂无 typed patch API，将 patch/regenerate 映射为预算内整章重写。",
            stop_reason="none",
            source_repair_hint=repair_hint,
            issue_ids=issue_ids,
            consumes_content_repair_budget=True,
        )
    return AgentRepairDecision(
        action="stop",
        reason="审计状态不支持安全修复。",
        stop_reason=_auditor_failure_stop_reason(audit_result),
        source_repair_hint=repair_hint,
        issue_ids=issue_ids,
    )


def repair_context_from_audit(
    audit_result: ChapterAuditResult,
    *,
    attempt_index: int,
) -> ChapterRepairContext:
    """从上一轮审计结果构造 writer repair context。

    Args:
        audit_result: Fund 审计结果。
        attempt_index: 即将执行的重写 attempt 序号。

    Returns:
        章节重写上下文。

    Raises:
        无显式抛出。
    """

    issues = _all_audit_issues(audit_result)
    return ChapterRepairContext(
        attempt_index=attempt_index,
        previous_issue_ids=tuple(issue.issue_id for issue in issues),
        previous_messages=tuple(_sanitize_text(issue.message) for issue in issues),
        required_corrections=_required_corrections_from_issues(issues),
    )


def repair_context_from_writer_invalid_marker(
    writer_result: ChapterWriteResult,
    *,
    attempt_index: int,
) -> ChapterRepairContext:
    """从 writer invalid-anchor 阻断结果构造章节重写上下文。

    Args:
        writer_result: Fund writer 阻断结果。
        attempt_index: 即将执行的重写 attempt 序号。

    Returns:
        只包含安全 issue id、脱敏消息和精确 anchor marker 修正项的重写上下文。

    Raises:
        无显式抛出。
    """

    issues = tuple(
        issue
        for issue in writer_result.issues
        if issue.issue_id.startswith("writer:invalid_anchor_marker")
    )
    return ChapterRepairContext(
        attempt_index=attempt_index,
        previous_issue_ids=tuple(issue.issue_id for issue in issues),
        previous_messages=tuple(
            _sanitize_writer_issue_message(issue.message) for issue in issues
        ),
        required_corrections=(_WRITER_INVALID_ANCHOR_CORRECTION,),
    )


def _audit_issue_ids(audit_result: ChapterAuditResult) -> tuple[str, ...]:
    """读取全部审计 issue id。

    Args:
        audit_result: Fund 审计结果。

    Returns:
        issue id 列表。

    Raises:
        无。
    """

    return tuple(issue.issue_id for issue in _all_audit_issues(audit_result))


def _all_audit_issues(audit_result: ChapterAuditResult) -> tuple[ChapterAuditIssue, ...]:
    """合并 programmatic 与 LLM 审计 issue。

    Args:
        audit_result: Fund 审计结果。

    Returns:
        全部 issue。

    Raises:
        无。
    """

    return (*audit_result.programmatic.issues, *audit_result.llm.issues)


def _has_llm_unavailable_issue(audit_result: ChapterAuditResult) -> bool:
    """判断审计结果是否包含 LLM unavailable issue。

    Args:
        audit_result: Fund 审计结果。

    Returns:
        命中时返回 `True`。

    Raises:
        无。
    """

    return any(issue.rule_code == "LLM_UNAVAILABLE" for issue in audit_result.llm.issues)


def _auditor_failure_stop_reason(audit_result: ChapterAuditResult) -> AgentRepairStopReason:
    """把审计失败状态转换为停止原因。

    Args:
        audit_result: Fund 审计结果。

    Returns:
        停止原因。

    Raises:
        无。
    """

    if audit_result.status == "blocked":
        return "auditor_blocked"
    return "auditor_failed"


def _required_corrections_from_issues(
    issues: tuple[ChapterAuditIssue, ...],
) -> tuple[str, ...]:
    """按确定性映射生成重写修正项。

    Args:
        issues: 上一轮审计 issue。

    Returns:
        去重后的修正项。

    Raises:
        无。
    """

    corrections: list[str] = []
    for issue in issues:
        correction = _required_correction_from_issue(issue)
        if correction not in corrections:
            corrections.append(correction)
    return tuple(corrections)


def _required_correction_from_issue(issue: ChapterAuditIssue) -> str:
    """把单条审计 issue 映射为确定性修正项。

    Args:
        issue: 上一轮审计 issue。

    Returns:
        修正项文本。

    Raises:
        无。
    """

    message = issue.message
    location = issue.location or ""
    if issue.rule_code == "P1" and _mentions_structure(message, location):
        return "补齐 ### 结论要点 / ### 详细情况 / ### 证据与出处 固定结构段落。"
    if issue.rule_code == "C2" and _mentions_required_output(message, location):
        return (
            "为对应 required output item 补齐 <!-- required_output:<item> --> marker，"
            "并在 marker 后只写有同源证据或明确缺口的内容。"
        )
    if issue.rule_code == "C2" and issue.item_rule_ids:
        return (
            "删除 ITEM_RULE 要求删除的 optional/conditional 段落标题和专属段落；"
            "不得删除 required output marker。"
        )
    if issue.rule_code == "C2" and "候选 facet" in message:
        return "将候选 facet 改写为候选/未断言信息，不得使用断言动词。"
    if issue.rule_code == "L1" or issue.issue_id.startswith("programmatic:L1"):
        return (
            "修复模板第2章 R=A+B-C 数字闭环：公式/百分比闭合断言必须在同一句或上下2行内放入"
            " allowed anchor marker；若没有同源事实支撑 R、A、B、C 或 A-C 数值关系，删除具体数值闭合断言，"
            "改写为未披露/数据不足/下一步最小验证问题；同时检查 ### 结论要点 与 ### 证据与出处，"
            "不得在这些段落无锚点复述 R/A/B/C/A-C 具体百分比；不得编造 Alpha、Beta、Cost 或 R 数值。"
        )
    if issue.rule_code == "E1" or "anchor" in message.lower() or "锚点" in message:
        return "只使用 allowed anchor marker，删除未知 anchor 或改用 allowed anchor。"
    if issue.issue_id == "llm:parse_failure":
        return "按 auditor 行协议修复：PASS|chapter|no issues 或 BLOCKING/REVIEWABLE/INFO 三段格式。"
    return _sanitize_text(message)


def _mentions_structure(message: str, location: str) -> bool:
    """判断 issue 是否命中固定结构段落。

    Args:
        message: issue 消息。
        location: issue 位置。

    Returns:
        命中结构段落时返回 `True`。

    Raises:
        无。
    """

    text = f"{message} {location}"
    return any(item in text for item in ("结论要点", "详细情况", "证据与出处", "结构段落"))


def _mentions_required_output(message: str, location: str) -> bool:
    """判断 issue 是否命中 required output。

    Args:
        message: issue 消息。
        location: issue 位置。

    Returns:
        命中 required output 时返回 `True`。

    Raises:
        无。
    """

    text = f"{message} {location}".lower()
    return "required output" in text or "required_output" in text


def _sanitize_text(text: str, *, max_chars: int = 180) -> str:
    """清理可能含敏感信息或过长上下文的文本。

    Args:
        text: 原始文本。
        max_chars: 最大字符数。

    Returns:
        单行、脱敏、限长文本。

    Raises:
        无。
    """

    redacted = " ".join(text.replace("\r", " ").replace("\n", " ").split())
    for sensitive in ("Authorization", "Bearer", "FUND_AGENT_LLM_API_KEY", "api_key", "sk-", "prompt"):
        redacted = redacted.replace(sensitive, "[redacted]")
    if len(redacted) <= max_chars:
        return redacted
    return redacted[:max_chars].rstrip() + "..."


def _sanitize_writer_issue_message(text: str) -> str:
    """清理 writer issue 消息，额外移除原始 HTML marker 片段。

    Args:
        text: 原始 writer issue 消息。

    Returns:
        不含原始 marker 片段的安全单行消息。

    Raises:
        无。
    """

    without_markers = _COMMENT_RE.sub("[redacted-marker]", text)
    return _sanitize_text(without_markers)
