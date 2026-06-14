"""Agent repair policy 测试，见模板第 1-6 章。"""

from __future__ import annotations

from dataclasses import replace

import fund_agent.agent.repair as repair_module
from fund_agent.agent.repair import decide_repair, repair_context_from_audit
from fund_agent.fund.chapter_auditor import (
    CHAPTER_AUDIT_SCHEMA_VERSION,
    ChapterAuditIssue,
    ChapterAuditResult,
    ChapterLLMAuditResult,
    ChapterProgrammaticAuditResult,
)
from fund_agent.fund.chapter_facts import project_chapter_facts
from fund_agent.fund.chapter_writer import (
    ChapterLLMResponse,
    ChapterWriteIssue,
    build_chapter_writer_input,
    write_chapter,
)
from tests.fund.test_chapter_facts import _bundle


class _InvalidAnchorWriter:
    """测试用非法 anchor writer。"""

    def generate_chapter(self, request: object) -> ChapterLLMResponse:
        """返回包含非法 anchor marker 的章节文本。"""

        input_data = build_chapter_writer_input(
            project_chapter_facts(_bundle(), chapter_ids=(6,)),
            chapter_id=6,
        )
        anchor_id = input_data.chapter.evidence_anchors[0].anchor_id
        text = (
            "### 结论要点\n"
            "<!-- ANCHOR:bad -->\n"
            "- 核心风险：仅记录已披露风险。\n"
            "### 详细情况\n"
            "本章只使用结构化 facts，不使用候选 facet 作为断言。\n"
            "### 证据与出处\n"
            f"<!-- anchor:{anchor_id} -->\n"
            "> 📎 证据：年报2024§§2表None行basic_identity（fixture）\n"
        )
        return ChapterLLMResponse(text=text, model_name="fake-writer", finish_reason="stop")


def test_patch_and_regenerate_use_recorded_whole_chapter_regenerate() -> None:
    """验证 patch/regenerate 当前都映射为整章重写且消耗内容预算。"""

    result = _audit_result(repair_hint="patch")

    decision = decide_repair(
        result,
        remaining_budget=1,
        auditor_available=True,
        run_llm_audit=True,
    )

    assert decision.action == "regenerate"
    assert decision.consumes_content_repair_budget is True
    assert decision.stop_reason == "none"


def test_needs_more_facts_is_terminal_without_source_probe_or_budget_use() -> None:
    """验证 needs_more_facts 终止且不消耗内容修复预算。"""

    result = _audit_result(repair_hint="needs_more_facts")

    decision = decide_repair(
        result,
        remaining_budget=1,
        auditor_available=True,
        run_llm_audit=True,
    )

    assert decision.action == "needs_more_facts"
    assert decision.stop_reason == "needs_more_facts"
    assert decision.consumes_content_repair_budget is False


def test_repair_budget_exhausted_stops_without_hidden_retry() -> None:
    """验证预算耗尽后停止，不允许 hidden retry。"""

    result = _audit_result(repair_hint="regenerate")

    decision = decide_repair(
        result,
        remaining_budget=0,
        auditor_available=True,
        run_llm_audit=True,
    )

    assert decision.action == "stop"
    assert decision.stop_reason == "repair_budget_exhausted"
    assert decision.consumes_content_repair_budget is False


def test_llm_unavailable_stops_without_content_budget_use() -> None:
    """验证 auditor unavailable 不触发内容修复预算。"""

    result = _audit_result(repair_hint="regenerate", rule_code="LLM_UNAVAILABLE")

    decision = decide_repair(
        result,
        remaining_budget=1,
        auditor_available=False,
        run_llm_audit=True,
    )

    assert decision.action == "stop"
    assert decision.stop_reason == "llm_unavailable"
    assert decision.consumes_content_repair_budget is False


def test_repair_context_records_issue_ids_and_sanitized_messages() -> None:
    """验证 repair context 只保存 issue id 和脱敏消息。"""

    result = _audit_result(message="Authorization Bearer sk-secret prompt raw")

    context = repair_context_from_audit(result, attempt_index=1)

    assert context.attempt_index == 1
    assert context.previous_issue_ids == ("programmatic:P1:fixture",)
    rendered = repr(context.previous_messages)
    assert "Authorization" not in rendered
    assert "Bearer" not in rendered
    assert "sk-secret" not in rendered
    assert "prompt" not in rendered


def test_writer_invalid_anchor_repair_context_is_sanitized_and_exact() -> None:
    """验证 writer invalid anchor repair context 精确指导语法且不泄漏原始坏 marker。"""

    input_data = build_chapter_writer_input(
        project_chapter_facts(_bundle(), chapter_ids=(6,)),
        chapter_id=6,
    )
    result = write_chapter(input_data, llm_client=_InvalidAnchorWriter())
    raw_issue = ChapterWriteIssue(
        issue_id="writer:invalid_anchor_marker:17",
        severity="blocking",
        reason="llm_contract_violation",
        message="bad marker <!-- ANCHOR:bad --> Authorization Bearer sk-secret prompt raw",
    )
    result = replace(result, issues=(raw_issue,))

    context = repair_module.repair_context_from_writer_invalid_marker(
        result,
        attempt_index=1,
    )

    assert context.attempt_index == 1
    assert context.previous_issue_ids == ("writer:invalid_anchor_marker:17",)
    rendered_messages = repr(context.previous_messages)
    rendered_corrections = repr(context.required_corrections)
    assert "<!-- ANCHOR:bad -->" not in rendered_messages
    assert "ANCHOR:bad" not in rendered_messages
    assert "Authorization" not in rendered_messages
    assert "Bearer" not in rendered_messages
    assert "sk-secret" not in rendered_messages
    assert "prompt raw" not in rendered_messages
    assert "<!-- anchor:<anchor_id> -->" in rendered_corrections
    assert "allowed anchor IDs" in rendered_corrections
    assert "bond_risk_evidence" in rendered_corrections
    assert "ANCHOR:bad" not in rendered_corrections


def _audit_result(
    *,
    repair_hint: str = "regenerate",
    rule_code: str = "P1",
    message: str = "缺少结构段落",
) -> ChapterAuditResult:
    """构造测试审计结果。"""

    issue = ChapterAuditIssue(
        issue_id="programmatic:P1:fixture",
        layer="programmatic",
        rule_code=rule_code,  # type: ignore[arg-type]
        severity="blocking",
        message=message,
        location="fixture",
        repair_hint=repair_hint,  # type: ignore[arg-type]
    )
    return ChapterAuditResult(
        schema_version=CHAPTER_AUDIT_SCHEMA_VERSION,
        status="blocked" if rule_code == "LLM_UNAVAILABLE" else "fail",
        programmatic=ChapterProgrammaticAuditResult(
            status="fail",
            issues=(issue,),
            checked_rules=("P1",),
        ),
        llm=ChapterLLMAuditResult(
            status="blocked" if rule_code == "LLM_UNAVAILABLE" else "pass",
            issues=(issue,) if rule_code == "LLM_UNAVAILABLE" else (),
            raw_response=None,
            model_name=None,
            finish_reason=None,
        ),
        accepted=False,
        repair_hint=repair_hint,  # type: ignore[arg-type]
    )
