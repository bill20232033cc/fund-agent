"""LLM incomplete 运行 artifact 写入器测试。"""

from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path

import pytest

from fund_agent.fund.analysis.final_judgment import FinalJudgmentDecision
from fund_agent.fund.chapter_auditor import (
    ChapterAuditIssue,
    ChapterAuditResult,
    ChapterLLMAuditResult,
    ChapterProgrammaticAuditResult,
)
from fund_agent.fund.chapter_facts import project_chapter_facts
from fund_agent.fund.chapter_writer import (
    ChapterDraft,
    ChapterWriteIssue,
    ChapterWriteResult,
    build_chapter_prompt,
    build_chapter_writer_input,
)
from fund_agent.services.chapter_orchestrator import (
    ChapterAttemptRecord,
    ChapterRepairDecision,
    ChapterRunResult,
)
from fund_agent.services.final_chapter_assembler import (
    FinalAssemblyIssue,
    FinalChapterAssemblyResult,
)
from fund_agent.services.fund_analysis_service import FundLLMAnalysisResult
from fund_agent.services.llm_run_artifacts import write_llm_incomplete_run_artifacts
from tests.fund.test_chapter_facts import _bundle


def test_write_llm_incomplete_run_artifacts_writes_manifest_summary_and_chapters(
    tmp_path: Path,
) -> None:
    """验证 incomplete LLM 结果会写入 manifest、summary 和单章 artifact。

    Args:
        tmp_path: pytest 临时目录 fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当核心 artifact 缺失或诊断摘要错误时抛出。
    """

    result = _incomplete_result()

    written = write_llm_incomplete_run_artifacts(
        result,
        host_run_id="host_run_fixture",
        output_root=tmp_path,
        clock=_fixed_clock,
    )

    assert written.artifact_dir == tmp_path / "110011-2024-20260602T010203Z-host_run_fixture"
    manifest = _read_json(written.manifest_path)
    summary = _read_json(written.summary_path)
    assert manifest["schema_version"] == "llm_incomplete_run_artifact_manifest.v1"
    assert manifest["trigger"] == "use_llm_incomplete"
    assert manifest["retention_policy"] == "manual_local_cleanup"
    assert manifest["chapter_count"] == 2
    assert "chapters/chapter-01.json" in manifest["chapter_files"]
    assert "chapters/chapter-02.json" in manifest["chapter_files"]
    assert summary["first_failed"]["chapter_id"] == 2
    assert summary["first_failed"]["failure_category"] == "prompt_contract"
    assert summary["first_failed"]["failure_subcategory"] == "l1_numerical_closure"
    assert summary["chapter_matrix"][0]["status"] == "accepted"
    assert summary["chapter_matrix"][1]["status"] == "failed"
    assert (written.artifact_dir / "chapters/chapter-01.json").exists()
    assert (written.artifact_dir / "chapters/chapter-02.json").exists()


def test_artifact_includes_writer_repair_and_auditor_feedback(tmp_path: Path) -> None:
    """验证 writer 初稿、repair 草稿和归一化审计反馈会被保留。

    Args:
        tmp_path: pytest 临时目录 fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当关键诊断文本或 JSON 链接缺失时抛出。
    """

    result = _incomplete_result()

    written = write_llm_incomplete_run_artifacts(
        result,
        host_run_id="host_run_fixture",
        output_root=tmp_path,
        clock=_fixed_clock,
    )

    chapter_payload = _read_json(written.artifact_dir / "chapters/chapter-02.json")
    attempts = chapter_payload["attempts"]
    assert attempts[0]["writer_draft_file"] == "chapters/chapter-02-attempt-00-writer.md"
    assert attempts[1]["writer_draft_file"] == "chapters/chapter-02-attempt-01-repair.md"
    assert attempts[1]["audit_feedback_file"] == (
        "chapters/chapter-02-attempt-01-auditor-feedback.md"
    )
    feedback = (
        written.artifact_dir
        / "chapters/chapter-02-attempt-01-auditor-feedback.md"
    ).read_text(encoding="utf-8")
    assert "programmatic/L1/blocking" in feedback
    assert "R=A+B-C" in feedback
    assert "source_repair_hint: patch" in feedback
    repair_text = (
        written.artifact_dir / "chapters/chapter-02-attempt-01-repair.md"
    ).read_text(encoding="utf-8")
    assert "repair draft for chapter 2" in repair_text


def test_artifact_redacts_secret_canaries(tmp_path: Path) -> None:
    """验证 writer/auditor 文本中的 secret canary 会被脱敏并记录。

    Args:
        tmp_path: pytest 临时目录 fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 secret canary 泄漏或 manifest 未记录脱敏时抛出。
    """

    result = _incomplete_result(secret_canaries=True)

    written = write_llm_incomplete_run_artifacts(
        result,
        host_run_id="host_run_fixture",
        output_root=tmp_path,
        clock=_fixed_clock,
    )

    for path in written.written_files:
        content = path.read_text(encoding="utf-8")
        assert "Authorization" not in content
        assert "Bearer abc" not in content
        assert "sk-secret" not in content
        assert "api_key" not in content
    manifest = _read_json(written.manifest_path)
    chapter = _read_json(written.artifact_dir / "chapters/chapter-02.json")
    assert manifest["redaction_applied"] is True
    assert manifest["redaction_count"] > 0
    assert chapter["redaction_applied"] is True


def test_artifact_schema_does_not_serialize_prompts_or_raw_provider_payloads(
    tmp_path: Path,
) -> None:
    """验证 artifact 不保存 prompt 或 raw auditor response。

    Args:
        tmp_path: pytest 临时目录 fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 prompt 或 raw provider payload 泄漏时抛出。
    """

    result = _incomplete_result(prompt_and_raw_canaries=True)

    written = write_llm_incomplete_run_artifacts(
        result,
        host_run_id="host_run_fixture",
        output_root=tmp_path,
        clock=_fixed_clock,
    )

    for path in written.written_files:
        content = path.read_text(encoding="utf-8")
        assert "SYSTEM_PROMPT_CANARY" not in content
        assert "USER_PROMPT_CANARY" not in content
        assert "RAW_AUDITOR_RESPONSE_CANARY" not in content
        assert "raw_response" not in content


def test_artifact_writer_rejects_accepted_final_report_by_default(tmp_path: Path) -> None:
    """验证 direct helper 禁止保存 accepted final report。

    Args:
        tmp_path: pytest 临时目录 fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 accepted 结果被写入 artifact 时抛出。
    """

    result = _incomplete_result(report_markdown="# accepted\n")

    with pytest.raises(ValueError, match="accepted final report"):
        write_llm_incomplete_run_artifacts(
            result,
            host_run_id="host_run_fixture",
            output_root=tmp_path,
            clock=_fixed_clock,
        )


def test_gitignore_ignores_llm_run_artifacts() -> None:
    """验证本地 LLM run artifact 目录默认被 git 忽略。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 `.gitignore` 未包含目录规则时抛出。
    """

    gitignore = Path(".gitignore").read_text(encoding="utf-8")

    assert "reports/llm-runs/" in gitignore


def _incomplete_result(
    *,
    secret_canaries: bool = False,
    prompt_and_raw_canaries: bool = False,
    report_markdown: str | None = None,
) -> FundLLMAnalysisResult:
    """构造含 accepted/failed 两章的 typed incomplete LLM 结果。

    Args:
        secret_canaries: 是否在可保存文本中注入 secret canary。
        prompt_and_raw_canaries: 是否在禁止保存字段中注入 canary。
        report_markdown: 可选最终报告 Markdown，用于 accepted guard 测试。

    Returns:
        typed LLM 分析结果。

    Raises:
        AssertionError: 当章节 fixture 无法形成预期状态时抛出。
    """

    projection = _projection()
    accepted_run = _accepted_chapter_run(projection)
    failed_run = _failed_chapter_run(
        projection,
        secret_canaries=secret_canaries,
        prompt_and_raw_canaries=prompt_and_raw_canaries,
    )
    orchestration_result = _projection_orchestration_result(
        projection,
        chapter_results=(accepted_run, failed_run),
    )
    return FundLLMAnalysisResult(
        structured_data=_bundle(),
        final_judgment_decision=_final_judgment_decision(),
        llm_orchestration_result=orchestration_result,
        final_assembly_result=FinalChapterAssemblyResult(
            status="accepted" if report_markdown is not None else "incomplete",
            fund_code="110011",
            report_year=2024,
            report_markdown=report_markdown,
            chapter0_markdown=None,
            chapter7_markdown=None,
            chapter7_summary=None,
            assembled_chapter_ids=(1,),
            source_accepted_chapter_ids=(1,),
            final_judgment_selected="needs_attention",
            issues=(
                FinalAssemblyIssue(
                    issue_id="final:chapter_not_accepted:2",
                    severity="blocking",
                    reason="chapter_not_accepted",
                    message="第 2 章未 accepted。",
                    chapter_ids=(2,),
                ),
            ),
        ),
    )


def _projection() -> object:
    """构造第 1-2 章投影。

    Args:
        无。

    Returns:
        章节事实投影。

    Raises:
        无显式抛出。
    """

    return project_chapter_facts(_bundle(), chapter_ids=(1, 2))


def _projection_orchestration_result(
    projection: object,
    *,
    chapter_results: tuple[ChapterRunResult, ...],
):
    """构造章节编排结果。

    Args:
        projection: 章节事实投影。
        chapter_results: 单章运行结果。

    Returns:
        `ChapterOrchestrationResult`。

    Raises:
        无显式抛出。
    """

    from fund_agent.services.chapter_orchestrator import ChapterOrchestrationResult

    return ChapterOrchestrationResult(
        status="partial",
        fund_code="110011",
        report_year=2024,
        projection=projection,
        chapter_results=chapter_results,
        accepted_conclusions=(),
        blocked_reasons=("chapter_2_failed",),
        generated_chapter_ids=(1, 2),
        skipped_chapter_ids=(),
    )


def _accepted_chapter_run(projection: object) -> ChapterRunResult:
    """构造 accepted 第 1 章运行结果。

    Args:
        projection: 章节事实投影。

    Returns:
        accepted 单章结果。

    Raises:
        无显式抛出。
    """

    writer_input = build_chapter_writer_input(projection, chapter_id=1)
    draft = _draft(
        chapter_id=1,
        title="第 1 章",
        markdown="accepted draft for chapter 1\n<!-- anchor:anchor-1 -->\n",
    )
    attempt = ChapterAttemptRecord(
        attempt_index=0,
        writer_result=ChapterWriteResult(
            status="drafted",
            stop_reason="none",
            prompt=build_chapter_prompt(writer_input),
            draft=draft,
            issues=(),
            response_chars=len(draft.markdown),
            finish_reason="stop",
            max_output_chars=writer_input.max_output_chars,
        ),
        audit_result=_audit_result(accepted=True),
        repair_decision=None,
    )
    return ChapterRunResult(
        chapter_id=1,
        title="第 1 章",
        status="accepted",
        stop_reason="none",
        accepted_draft=draft,
        accepted_conclusion=None,
        attempts=(attempt,),
        issues=(),
    )


def _failed_chapter_run(
    projection: object,
    *,
    secret_canaries: bool,
    prompt_and_raw_canaries: bool,
) -> ChapterRunResult:
    """构造第 2 章 L1 失败运行结果。

    Args:
        projection: 章节事实投影。
        secret_canaries: 是否在可保存文本中注入 secret canary。
        prompt_and_raw_canaries: 是否在禁止保存字段中注入 canary。

    Returns:
        failed 单章结果。

    Raises:
        无显式抛出。
    """

    writer_input = build_chapter_writer_input(projection, chapter_id=2)
    prompt = build_chapter_prompt(writer_input)
    if prompt_and_raw_canaries:
        prompt = prompt.__class__(
            chapter_id=prompt.chapter_id,
            title=prompt.title,
            system_prompt="SYSTEM_PROMPT_CANARY",
            user_prompt="USER_PROMPT_CANARY",
            must_answer=prompt.must_answer,
            must_not_cover=prompt.must_not_cover,
            required_output_items=prompt.required_output_items,
            allowed_fact_ids=prompt.allowed_fact_ids,
            allowed_anchor_ids=prompt.allowed_anchor_ids,
            deleted_item_rule_ids=prompt.deleted_item_rule_ids,
            required_gap_phrases=prompt.required_gap_phrases,
            prompt_cost_diagnostic=prompt.prompt_cost_diagnostic,
        )
    draft_text = "writer draft for chapter 2\nR=A+B-C 1.00%\n"
    repair_text = "repair draft for chapter 2\nR=A+B-C 2.00%\n"
    issue_message = "R=A+B-C / A=R-B / A-C 数字闭环断言缺少邻近 anchor marker。"
    if secret_canaries:
        draft_text += "Authorization Bearer abc sk-secret api_key\n"
        issue_message += " Authorization Bearer abc sk-secret api_key"
    first_audit = _audit_result(
        accepted=False,
        issue_message=issue_message,
        raw_response="RAW_AUDITOR_RESPONSE_CANARY" if prompt_and_raw_canaries else None,
    )
    repair_decision = ChapterRepairDecision(
        action="regenerate",
        reason="按 L1 issue 重新生成。",
        stop_reason="none",
        source_repair_hint="patch",
        issue_ids=("programmatic:L1:line:2:abcdef",),
    )
    attempts = (
        ChapterAttemptRecord(
            attempt_index=0,
            writer_result=_write_result(
                writer_input=writer_input,
                prompt=prompt,
                draft=_draft(chapter_id=2, title="第 2 章", markdown=draft_text),
            ),
            audit_result=first_audit,
            repair_decision=repair_decision,
        ),
        ChapterAttemptRecord(
            attempt_index=1,
            writer_result=_write_result(
                writer_input=writer_input,
                prompt=prompt,
                draft=_draft(chapter_id=2, title="第 2 章", markdown=repair_text),
            ),
            audit_result=_audit_result(
                accepted=False,
                issue_message=issue_message,
                raw_response="RAW_AUDITOR_RESPONSE_CANARY" if prompt_and_raw_canaries else None,
            ),
            repair_decision=ChapterRepairDecision(
                action="stop",
                reason="repair budget exhausted",
                stop_reason="repair_budget_exhausted",
                source_repair_hint="patch",
                issue_ids=("programmatic:L1:line:2:abcdef",),
            ),
        ),
    )
    return ChapterRunResult(
        chapter_id=2,
        title="第 2 章",
        status="failed",
        stop_reason="repair_budget_exhausted",
        accepted_draft=None,
        accepted_conclusion=None,
        attempts=attempts,
        issues=(issue_message,),
        failure_category="prompt_contract",
        failure_subcategory="l1_numerical_closure",
    )


def _write_result(*, writer_input: object, prompt: object, draft: ChapterDraft) -> ChapterWriteResult:
    """构造 drafted writer result。

    Args:
        writer_input: writer input。
        prompt: writer prompt。
        draft: 章节草稿。

    Returns:
        writer result。

    Raises:
        无显式抛出。
    """

    return ChapterWriteResult(
        status="drafted",
        stop_reason="none",
        prompt=prompt,
        draft=draft,
        issues=(
            ChapterWriteIssue(
                issue_id="writer:fixture",
                severity="reviewable",
                reason="none",
                message="fixture writer issue",
            ),
        ),
        response_chars=len(draft.markdown),
        finish_reason="stop",
        max_output_chars=writer_input.max_output_chars,
    )


def _audit_result(
    *,
    accepted: bool,
    issue_message: str = "fixture audit issue",
    raw_response: str | None = None,
) -> ChapterAuditResult:
    """构造章节审计结果。

    Args:
        accepted: 是否 accepted。
        issue_message: 程序审计 issue message。
        raw_response: LLM raw response；artifact 不应保存。

    Returns:
        审计结果。

    Raises:
        无显式抛出。
    """

    issues = () if accepted else (_l1_issue(issue_message),)
    return ChapterAuditResult(
        status="pass" if accepted else "fail",
        programmatic=ChapterProgrammaticAuditResult(
            status="pass" if accepted else "fail",
            issues=issues,
            checked_rules=("L1",),
        ),
        llm=ChapterLLMAuditResult(
            status="pass",
            issues=(),
            raw_response=raw_response,
            model_name="fake-auditor",
            finish_reason="stop",
        ),
        accepted=accepted,
        repair_hint="none" if accepted else "patch",
    )


def _l1_issue(message: str) -> ChapterAuditIssue:
    """构造 L1 审计 issue。

    Args:
        message: issue message。

    Returns:
        L1 issue。

    Raises:
        无显式抛出。
    """

    return ChapterAuditIssue(
        issue_id="programmatic:L1:line:2:abcdef",
        layer="programmatic",
        rule_code="L1",
        severity="blocking",
        message=message,
        location="line:2",
        repair_hint="patch",
    )


def _draft(*, chapter_id: int, title: str, markdown: str) -> ChapterDraft:
    """构造章节草稿。

    Args:
        chapter_id: 模板章节编号。
        title: 章节标题。
        markdown: 草稿 Markdown。

    Returns:
        章节草稿。

    Raises:
        无显式抛出。
    """

    return ChapterDraft(
        chapter_id=chapter_id,
        title=title,
        markdown=markdown,
        used_fact_ids=(f"fact:{chapter_id}",),
        used_anchor_ids=(f"anchor:{chapter_id}",),
        declared_missing_reasons=(),
        deleted_item_rule_ids=(),
        model_name="fake-writer",
        finish_reason="stop",
    )


def _final_judgment_decision() -> FinalJudgmentDecision:
    """构造最终判断 fixture。

    Args:
        无。

    Returns:
        最终判断决策。

    Raises:
        无显式抛出。
    """

    return FinalJudgmentDecision(
        selected_judgment="needs_attention",
        derived_judgment="needs_attention",
        source="derived",
        override_judgment=None,
        reasons=("fixture",),
        conflict_reasons=(),
    )


def _fixed_clock() -> datetime:
    """返回固定 UTC 时间。

    Args:
        无。

    Returns:
        固定时间。

    Raises:
        无显式抛出。
    """

    return datetime(2026, 6, 2, 1, 2, 3, tzinfo=timezone.utc)


def _read_json(path: Path) -> dict[str, object]:
    """读取 JSON 文件。

    Args:
        path: JSON 文件路径。

    Returns:
        JSON object。

    Raises:
        json.JSONDecodeError: 当文件不是合法 JSON 时抛出。
    """

    return json.loads(path.read_text(encoding="utf-8"))
