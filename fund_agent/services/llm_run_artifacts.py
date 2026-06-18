"""LLM 未完成运行的本地诊断 artifact 写入器。

本模块属于 Service 层，只消费 `FundLLMAnalysisResult` 已形成的 typed 结果，
把模板第 1-6 章 write-audit-repair 过程中的安全字段写入本地 ignored 目录。
它不调用 provider、Host、质量 gate、文档仓库或确定性 renderer。
"""

from __future__ import annotations

from collections.abc import Callable, Iterable
from dataclasses import dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
import re
from typing import Final, Literal

from fund_agent.config.paths import DEFAULT_LLM_RUN_ARTIFACT_ROOT as _CONFIG_LLM_RUN_ARTIFACT_ROOT
from fund_agent.fund.chapter_auditor import ChapterAuditIssue
from fund_agent.fund.chapter_writer import ChapterWriteIssue
from fund_agent.services.chapter_orchestrator import (
    ChapterAttemptRecord,
    ChapterLLMRuntimeDiagnostic,
    ChapterOrchestrationResult,
    ChapterPromptContractDiagnostic,
    ChapterRepairDecision,
    ChapterRunResult,
    attempt_runtime_diagnostic_consistency_payload,
    runtime_diagnostic_consistency_payload,
    serialize_chapter_prompt_contract_diagnostics,
    serialize_chapter_runtime_diagnostics,
)
from fund_agent.services.fund_analysis_service import FundLLMAnalysisResult

DEFAULT_LLM_RUN_ARTIFACT_ROOT: Final[Path] = _CONFIG_LLM_RUN_ARTIFACT_ROOT
MANIFEST_SCHEMA_VERSION: Final[str] = "llm_incomplete_run_artifact_manifest.v1"
SUMMARY_SCHEMA_VERSION: Final[str] = "llm_incomplete_run_summary.v1"
CHAPTER_SCHEMA_VERSION: Final[str] = "llm_incomplete_run_chapter_artifact.v1"
ARTIFACT_KIND: Final[str] = "llm_incomplete_run_diagnostic"
DEFAULT_TRIGGER: Final[str] = "use_llm_incomplete"
RETENTION_POLICY: Final[str] = "manual_local_cleanup"
REDACTION_REPLACEMENT: Final[str] = "[REDACTED]"
_RUN_ID_MAX_CHARS: Final[int] = 24
_FEEDBACK_EMPTY_TEXT: Final[str] = "无结构化审计反馈。"
_REDACTION_POLICY_ID: Final[str] = "llm_incomplete_artifact_redaction.v1"
_SECRET_PATTERNS: Final[tuple[re.Pattern[str], ...]] = (
    re.compile(r"Bearer\s+[^\s`\"'<>]+", re.IGNORECASE),
    re.compile(r"sk-[A-Za-z0-9_-]+"),
    re.compile(r"\bAuthorization\b", re.IGNORECASE),
    re.compile(r"\bapi[_-]?key\b", re.IGNORECASE),
    re.compile(r"\bx-api-key\b", re.IGNORECASE),
    re.compile(r"\bset-cookie\b", re.IGNORECASE),
    re.compile(r"\bcookie\b", re.IGNORECASE),
    re.compile(r"\bpassword\b", re.IGNORECASE),
    re.compile(r"\bsecret\b", re.IGNORECASE),
    re.compile(r"\bsystem_prompt\b", re.IGNORECASE),
    re.compile(r"\buser_prompt\b", re.IGNORECASE),
    re.compile(r"\bdraft_markdown\b", re.IGNORECASE),
    re.compile(r"\braw_response\b", re.IGNORECASE),
    re.compile(r"\bprovider_response\b", re.IGNORECASE),
    re.compile(r"provider\s+body", re.IGNORECASE),
    re.compile(r"\bheaders?\b", re.IGNORECASE),
)


@dataclass(frozen=True, slots=True)
class LLMRunArtifactWriteResult:
    """LLM incomplete 诊断 artifact 写入结果。

    Attributes:
        artifact_dir: 本次运行 artifact 目录。
        manifest_path: manifest JSON 路径。
        summary_path: summary JSON 路径。
        redaction_applied: 是否发生过脱敏替换。
        written_files: 已写入文件路径，按写入顺序排列。
    """

    artifact_dir: Path
    manifest_path: Path
    summary_path: Path
    redaction_applied: bool
    written_files: tuple[Path, ...]


@dataclass(slots=True)
class _RedactionStats:
    """单次 artifact 写入过程的脱敏计数器。

    Attributes:
        count: 发生的脱敏替换次数。
    """

    count: int = 0


def write_llm_incomplete_run_artifacts(
    result: FundLLMAnalysisResult,
    *,
    host_run_id: str | None,
    output_root: Path = DEFAULT_LLM_RUN_ARTIFACT_ROOT,
    clock: Callable[[], datetime] | None = None,
    trigger: Literal["use_llm_incomplete"] = DEFAULT_TRIGGER,
) -> LLMRunArtifactWriteResult:
    """写入 typed incomplete LLM 运行的本地诊断 artifact。

    Args:
        result: Service 返回的 typed LLM 分析结果，必须处于未总装完成状态。
        host_run_id: Host run id；无 Host 结果时为 `None`。
        output_root: artifact 根目录。
        clock: 测试可注入的当前时间函数。
        trigger: artifact 触发来源；当前只允许默认 incomplete 触发。

    Returns:
        写入结果，包含 manifest 和 summary 路径。

    Raises:
        TypeError: 当传入结果不是 `FundLLMAnalysisResult` 时抛出。
        ValueError: 当结果已包含完整报告或 trigger 非法时抛出。
        OSError: 当目录创建或文件写入失败时由文件系统操作抛出。
    """

    if not isinstance(result, FundLLMAnalysisResult):
        raise TypeError("LLM incomplete artifact 只接受 FundLLMAnalysisResult typed 结果")
    if trigger != DEFAULT_TRIGGER:
        raise ValueError(f"未知 LLM artifact trigger：{trigger}")
    if result.final_assembly_result.report_markdown is not None:
        raise ValueError("LLM incomplete artifact writer 禁止保存 accepted final report")

    created_at = _current_time(clock)
    orchestration_result = result.llm_orchestration_result
    run_dir = _run_artifact_dir(
        output_root,
        fund_code=orchestration_result.fund_code,
        report_year=orchestration_result.report_year,
        created_at=created_at,
        host_run_id=host_run_id,
    )
    chapters_dir = run_dir / "chapters"
    chapters_dir.mkdir(parents=True, exist_ok=False)

    stats = _RedactionStats()
    written_files: list[Path] = []
    chapter_files: list[str] = []
    artifact_files: list[str] = []

    for chapter_result in orchestration_result.chapter_results:
        chapter_payload = _build_chapter_payload(
            chapter_result,
            fund_code=orchestration_result.fund_code,
            report_year=orchestration_result.report_year,
            run_dir=run_dir,
            chapters_dir=chapters_dir,
            stats=stats,
            artifact_files=artifact_files,
            written_files=written_files,
        )
        chapter_json_path = chapters_dir / f"chapter-{chapter_result.chapter_id:02d}.json"
        _atomic_write_json(chapter_json_path, chapter_payload)
        relative_chapter_json = _relative_posix(chapter_json_path, run_dir)
        chapter_files.append(relative_chapter_json)
        artifact_files.append(relative_chapter_json)
        written_files.append(chapter_json_path)

    summary_payload = _build_summary_payload(
        result,
        run_id=host_run_id,
        artifact_files=tuple(artifact_files),
        stats=stats,
    )
    summary_path = run_dir / "summary.json"
    _atomic_write_json(summary_path, summary_payload)
    written_files.append(summary_path)

    manifest_path = run_dir / "manifest.json"
    manifest_payload = _build_manifest_payload(
        result,
        created_at=created_at,
        run_id=host_run_id,
        trigger=trigger,
        chapter_files=tuple(chapter_files),
        redaction_count=stats.count,
    )
    _atomic_write_json(manifest_path, manifest_payload)
    written_files.append(manifest_path)

    return LLMRunArtifactWriteResult(
        artifact_dir=run_dir,
        manifest_path=manifest_path,
        summary_path=summary_path,
        redaction_applied=stats.count > 0,
        written_files=tuple(written_files),
    )


def _build_manifest_payload(
    result: FundLLMAnalysisResult,
    *,
    created_at: datetime,
    run_id: str | None,
    trigger: str,
    chapter_files: tuple[str, ...],
    redaction_count: int,
) -> dict[str, object]:
    """构造 manifest JSON payload。

    Args:
        result: typed LLM 分析结果。
        created_at: artifact 创建时间。
        run_id: Host run id。
        trigger: artifact 触发来源。
        chapter_files: 相对章节 JSON 路径。
        redaction_count: 本次写入脱敏次数。

    Returns:
        manifest JSON payload。

    Raises:
        无显式抛出。
    """

    orchestration_result = result.llm_orchestration_result
    return {
        "schema_version": MANIFEST_SCHEMA_VERSION,
        "created_at": _isoformat(created_at),
        "artifact_kind": ARTIFACT_KIND,
        "fund_code": orchestration_result.fund_code,
        "report_year": orchestration_result.report_year,
        "run_id": run_id,
        "trigger": trigger,
        "cli_command": "analyze --use-llm",
        "orchestration_status": orchestration_result.status,
        "final_assembly_status": result.final_assembly_result.status,
        "chapter_count": len(orchestration_result.chapter_results),
        "chapter_files": chapter_files,
        "summary_file": "summary.json",
        "retention_policy": RETENTION_POLICY,
        "redaction_applied": redaction_count > 0,
        "redaction_count": redaction_count,
        "redaction_policy": {
            "policy_id": _REDACTION_POLICY_ID,
            "replacement": REDACTION_REPLACEMENT,
            "forbidden_categories": (
                "secret_headers",
                "provider_credentials",
                "prompt_request_payloads",
                "raw_provider_payloads",
                "cookies_and_passwords",
            ),
        },
    }


def _build_summary_payload(
    result: FundLLMAnalysisResult,
    *,
    run_id: str | None,
    artifact_files: tuple[str, ...],
    stats: _RedactionStats,
) -> dict[str, object]:
    """构造 summary JSON payload。

    Args:
        result: typed LLM 分析结果。
        run_id: Host run id。
        artifact_files: 本次运行已写入的相对文件路径。
        stats: 脱敏计数器。

    Returns:
        summary JSON payload。

    Raises:
        无显式抛出。
    """

    orchestration_result = result.llm_orchestration_result
    return {
        "schema_version": SUMMARY_SCHEMA_VERSION,
        "fund_code": orchestration_result.fund_code,
        "report_year": orchestration_result.report_year,
        "run_id": run_id,
        "orchestration_status": orchestration_result.status,
        "final_assembly_status": result.final_assembly_result.status,
        "final_assembly_issues": tuple(
            _final_assembly_issue_summary(issue, stats=stats)
            for issue in result.final_assembly_result.issues
        ),
        "first_failed": _first_failed_payload(orchestration_result),
        "chapter_matrix": tuple(
            _chapter_matrix_row(chapter_result)
            for chapter_result in orchestration_result.chapter_results
        ),
        "prompt_contract_diagnostics": serialize_chapter_prompt_contract_diagnostics(
            orchestration_result
        ),
        "runtime_diagnostics": serialize_chapter_runtime_diagnostics(orchestration_result),
        "artifact_files": artifact_files,
        "redaction_applied": stats.count > 0,
        "redaction_count": stats.count,
    }


def _build_chapter_payload(
    chapter_result: ChapterRunResult,
    *,
    fund_code: str,
    report_year: int,
    run_dir: Path,
    chapters_dir: Path,
    stats: _RedactionStats,
    artifact_files: list[str],
    written_files: list[Path],
) -> dict[str, object]:
    """构造并写入单章 text artifact 后返回章节 JSON payload。

    Args:
        chapter_result: 单章编排结果。
        fund_code: 基金代码。
        report_year: 年报年份。
        run_dir: 本次运行 artifact 根目录。
        chapters_dir: 章节 artifact 目录。
        stats: 脱敏计数器。
        artifact_files: 累积相对 artifact 文件路径。
        written_files: 累积实际写入文件路径。

    Returns:
        单章 JSON payload。

    Raises:
        OSError: 当文件写入失败时由底层写入函数抛出。
    """

    chapter_redaction_start = stats.count
    attempts_payload: list[dict[str, object]] = []
    accepted_draft_file = None

    for attempt in chapter_result.attempts:
        attempt_payload = _build_attempt_payload(
            chapter_result,
            attempt,
            run_dir=run_dir,
            chapters_dir=chapters_dir,
            stats=stats,
            artifact_files=artifact_files,
            written_files=written_files,
        )
        attempts_payload.append(attempt_payload)
        writer_draft_file = attempt_payload.get("writer_draft_file")
        draft = attempt.writer_result.draft
        if (
            accepted_draft_file is None
            and writer_draft_file is not None
            and chapter_result.accepted_draft is not None
            and draft is not None
            and draft.markdown == chapter_result.accepted_draft.markdown
        ):
            accepted_draft_file = writer_draft_file

    if accepted_draft_file is None and chapter_result.accepted_draft is not None:
        accepted_path = chapters_dir / f"chapter-{chapter_result.chapter_id:02d}-accepted-draft.md"
        _atomic_write_text(accepted_path, _redact_text(chapter_result.accepted_draft.markdown, stats))
        accepted_draft_file = _relative_posix(accepted_path, run_dir)
        artifact_files.append(accepted_draft_file)
        written_files.append(accepted_path)

    return {
        "schema_version": CHAPTER_SCHEMA_VERSION,
        "fund_code": fund_code,
        "report_year": report_year,
        "chapter_id": chapter_result.chapter_id,
        "title": chapter_result.title,
        "status": chapter_result.status,
        "stop_reason": chapter_result.stop_reason,
        "failure_category": chapter_result.failure_category,
        "failure_subcategory": chapter_result.failure_subcategory,
        "accepted": chapter_result.status == "accepted",
        "accepted_draft_file": accepted_draft_file,
        "accepted_conclusion_present": chapter_result.accepted_conclusion is not None,
        "issues": tuple(_safe_text(issue, stats=stats) for issue in chapter_result.issues),
        "attempts": tuple(attempts_payload),
        "chapter_prompt_contract_diagnostics": tuple(
            _prompt_contract_diagnostic_payload(diagnostic)
            for diagnostic in chapter_result.prompt_contract_diagnostics
        ),
        **runtime_diagnostic_consistency_payload(chapter_result),
        "chapter_runtime_diagnostics": tuple(
            _runtime_diagnostic_payload(diagnostic)
            for diagnostic in _runtime_diagnostics_for_chapter(chapter_result)
        ),
        "redaction_applied": stats.count > chapter_redaction_start,
        "redaction_count": stats.count - chapter_redaction_start,
    }


def _build_attempt_payload(
    chapter_result: ChapterRunResult,
    attempt: ChapterAttemptRecord,
    *,
    run_dir: Path,
    chapters_dir: Path,
    stats: _RedactionStats,
    artifact_files: list[str],
    written_files: list[Path],
) -> dict[str, object]:
    """构造单次 attempt JSON payload 并写入关联 markdown 文件。

    Args:
        chapter_result: 单章编排结果。
        attempt: write/audit attempt 记录。
        run_dir: 本次运行 artifact 根目录。
        chapters_dir: 章节 artifact 目录。
        stats: 脱敏计数器。
        artifact_files: 累积相对 artifact 文件路径。
        written_files: 累积实际写入文件路径。

    Returns:
        attempt JSON payload。

    Raises:
        OSError: 当文件写入失败时由底层写入函数抛出。
    """

    writer_result = attempt.writer_result
    writer_draft_file = None
    draft = writer_result.draft
    if draft is not None:
        suffix = "writer" if attempt.attempt_index == 0 else "repair"
        writer_path = (
            chapters_dir
            / f"chapter-{chapter_result.chapter_id:02d}-attempt-{attempt.attempt_index:02d}-{suffix}.md"
        )
        _atomic_write_text(writer_path, _redact_text(draft.markdown, stats))
        writer_draft_file = _relative_posix(writer_path, run_dir)
        artifact_files.append(writer_draft_file)
        written_files.append(writer_path)

    audit_feedback_file = None
    if attempt.audit_result is not None or attempt.repair_decision is not None:
        feedback_path = (
            chapters_dir
            / f"chapter-{chapter_result.chapter_id:02d}-attempt-{attempt.attempt_index:02d}-auditor-feedback.md"
        )
        _atomic_write_text(feedback_path, _auditor_feedback_text(attempt, stats=stats))
        audit_feedback_file = _relative_posix(feedback_path, run_dir)
        artifact_files.append(audit_feedback_file)
        written_files.append(feedback_path)

    audit_result = attempt.audit_result
    repair_decision = attempt.repair_decision
    return {
        "attempt_index": attempt.attempt_index,
        "writer_status": writer_result.status,
        "writer_stop_reason": writer_result.stop_reason,
        "writer_finish_reason": writer_result.finish_reason,
        "writer_response_chars": writer_result.response_chars,
        "writer_max_output_chars": writer_result.max_output_chars,
        "writer_draft_file": writer_draft_file,
        "writer_used_fact_ids": draft.used_fact_ids if draft is not None else (),
        "writer_used_anchor_ids": draft.used_anchor_ids if draft is not None else (),
        "writer_declared_missing_reasons": (
            draft.declared_missing_reasons if draft is not None else ()
        ),
        "writer_deleted_item_rule_ids": draft.deleted_item_rule_ids if draft is not None else (),
        "writer_issues": tuple(
            _writer_issue_summary(issue, stats=stats) for issue in writer_result.issues
        ),
        "audit_status": audit_result.status if audit_result is not None else None,
        "audit_accepted": audit_result.accepted if audit_result is not None else None,
        "audit_repair_hint": audit_result.repair_hint if audit_result is not None else None,
        "audit_feedback_file": audit_feedback_file,
        "programmatic_issues": tuple(
            _audit_issue_summary(issue, stats=stats)
            for issue in _programmatic_issues(audit_result)
        ),
        "llm_issues": tuple(
            _audit_issue_summary(issue, stats=stats) for issue in _llm_issues(audit_result)
        ),
        "repair_decision": _repair_decision_payload(repair_decision, stats=stats),
        **attempt_runtime_diagnostic_consistency_payload(chapter_result, attempt),
        "runtime_diagnostics": tuple(
            _runtime_diagnostic_payload(diagnostic)
            for diagnostic in attempt.runtime_diagnostics
        ),
    }


def _auditor_feedback_text(
    attempt: ChapterAttemptRecord,
    *,
    stats: _RedactionStats,
) -> str:
    """把结构化审计结果归一化为 markdown 反馈文本。

    Args:
        attempt: 单次 write/audit attempt。
        stats: 脱敏计数器。

    Returns:
        归一化审计反馈 markdown，不包含 raw auditor response。

    Raises:
        无显式抛出。
    """

    audit_result = attempt.audit_result
    repair_decision = attempt.repair_decision
    lines = [f"# Attempt {attempt.attempt_index} Auditor Feedback", ""]
    if audit_result is None:
        lines.append(_FEEDBACK_EMPTY_TEXT)
    else:
        lines.extend(
            (
                f"- audit_status: {audit_result.status}",
                f"- audit_accepted: {audit_result.accepted}",
                f"- aggregate_repair_hint: {audit_result.repair_hint}",
                "",
                "## Programmatic Issues",
            )
        )
        lines.extend(_feedback_issue_lines(audit_result.programmatic.issues, stats=stats))
        lines.extend(("", "## LLM Issues"))
        lines.extend(_feedback_issue_lines(audit_result.llm.issues, stats=stats))
    lines.extend(("", "## Repair Decision"))
    if repair_decision is None:
        lines.append("- none")
    else:
        lines.extend(
            (
                f"- action: {repair_decision.action}",
                f"- reason: {_safe_text(repair_decision.reason, stats=stats)}",
                f"- stop_reason: {repair_decision.stop_reason}",
                f"- source_repair_hint: {repair_decision.source_repair_hint}",
                f"- issue_ids: {', '.join(repair_decision.issue_ids) or 'none'}",
            )
        )
    return "\n".join(lines).rstrip() + "\n"


def _feedback_issue_lines(
    issues: Iterable[ChapterAuditIssue],
    *,
    stats: _RedactionStats,
) -> list[str]:
    """把审计 issue 转为 markdown 列表行。

    Args:
        issues: 审计 issue 序列。
        stats: 脱敏计数器。

    Returns:
        markdown 列表行。

    Raises:
        无显式抛出。
    """

    lines: list[str] = []
    for issue in issues:
        location = issue.location or "unknown"
        lines.append(
            "- "
            f"[{issue.layer}/{issue.rule_code}/{issue.severity}] "
            f"{issue.issue_id} location={location} "
            f"repair_hint={issue.repair_hint}: {_safe_text(issue.message, stats=stats)}"
        )
    if not lines:
        lines.append("- none")
    return lines


def _final_assembly_issue_summary(issue: object, *, stats: _RedactionStats) -> dict[str, object]:
    """构造最终总装 issue 的 allowlist 摘要。

    Args:
        issue: `FinalAssemblyIssue` 或测试替身。
        stats: 脱敏计数器。

    Returns:
        safe issue 摘要。

    Raises:
        无显式抛出。
    """

    return {
        "issue_id": _optional_text(getattr(issue, "issue_id", None), stats=stats),
        "severity": _optional_text(getattr(issue, "severity", None), stats=stats),
        "reason": _optional_text(getattr(issue, "reason", None), stats=stats),
        "message": _optional_text(getattr(issue, "message", None), stats=stats),
        "chapter_ids": tuple(getattr(issue, "chapter_ids", ()) or ()),
    }


def _writer_issue_summary(issue: ChapterWriteIssue, *, stats: _RedactionStats) -> dict[str, object]:
    """构造 writer issue 的 allowlist 摘要。

    Args:
        issue: writer issue。
        stats: 脱敏计数器。

    Returns:
        safe issue 摘要。

    Raises:
        无显式抛出。
    """

    return {
        "issue_id": _safe_text(issue.issue_id, stats=stats),
        "severity": issue.severity,
        "reason": issue.reason,
        "message": _safe_text(issue.message, stats=stats),
        "fact_ids": issue.fact_ids,
        "anchor_ids": issue.anchor_ids,
        "item_rule_ids": issue.item_rule_ids,
    }


def _audit_issue_summary(issue: ChapterAuditIssue, *, stats: _RedactionStats) -> dict[str, object]:
    """构造 audit issue 的 allowlist 摘要。

    Args:
        issue: 审计 issue。
        stats: 脱敏计数器。

    Returns:
        safe issue 摘要。

    Raises:
        无显式抛出。
    """

    return {
        "issue_id": _safe_text(issue.issue_id, stats=stats),
        "layer": issue.layer,
        "rule_code": issue.rule_code,
        "severity": issue.severity,
        "message": _safe_text(issue.message, stats=stats),
        "location": _optional_text(issue.location, stats=stats),
        "fact_ids": issue.fact_ids,
        "anchor_ids": issue.anchor_ids,
        "item_rule_ids": issue.item_rule_ids,
        "repair_hint": issue.repair_hint,
    }


def _repair_decision_payload(
    repair_decision: ChapterRepairDecision | None,
    *,
    stats: _RedactionStats,
) -> dict[str, object] | None:
    """构造 repair decision 的 allowlist 摘要。

    Args:
        repair_decision: repair 决策；未进入 repair 时为 `None`。
        stats: 脱敏计数器。

    Returns:
        safe repair 决策摘要或 `None`。

    Raises:
        无显式抛出。
    """

    if repair_decision is None:
        return None
    return {
        "action": repair_decision.action,
        "reason": _safe_text(repair_decision.reason, stats=stats),
        "stop_reason": repair_decision.stop_reason,
        "source_repair_hint": repair_decision.source_repair_hint,
        "issue_ids": repair_decision.issue_ids,
    }


def _first_failed_payload(orchestration_result: ChapterOrchestrationResult) -> dict[str, object] | None:
    """提取首个未 accepted 章节的诊断摘要。

    Args:
        orchestration_result: 章节编排结果。

    Returns:
        首个失败章节摘要；没有失败章节时返回 `None`。

    Raises:
        无显式抛出。
    """

    for chapter_result in orchestration_result.chapter_results:
        if chapter_result.status == "accepted":
            continue
        return {
            "chapter_id": chapter_result.chapter_id,
            "status": chapter_result.status,
            "stop_reason": chapter_result.stop_reason,
            "failure_category": chapter_result.failure_category,
            "failure_subcategory": chapter_result.failure_subcategory,
            "attempt_count": len(chapter_result.attempts),
        }
    return None


def _chapter_matrix_row(chapter_result: ChapterRunResult) -> dict[str, object]:
    """构造 summary 中的单章矩阵行。

    Args:
        chapter_result: 单章编排结果。

    Returns:
        单章状态矩阵行。

    Raises:
        无显式抛出。
    """

    return {
        "chapter_id": chapter_result.chapter_id,
        "title": chapter_result.title,
        "status": chapter_result.status,
        "stop_reason": chapter_result.stop_reason,
        "failure_category": chapter_result.failure_category,
        "failure_subcategory": chapter_result.failure_subcategory,
        "attempt_count": len(chapter_result.attempts),
        "accepted_draft_present": chapter_result.accepted_draft is not None,
        "accepted_conclusion_present": chapter_result.accepted_conclusion is not None,
    }


def _prompt_contract_diagnostic_payload(
    diagnostic: ChapterPromptContractDiagnostic,
) -> dict[str, object]:
    """把 prompt-contract 诊断转为 allowlist payload。

    Args:
        diagnostic: Service 层 prompt-contract 诊断。

    Returns:
        不含 prompt、draft 或 raw response 的诊断 payload。

    Raises:
        无显式抛出。
    """

    return {
        "schema_version": diagnostic.schema_version,
        "chapter_id": diagnostic.chapter_id,
        "phase": diagnostic.phase,
        "attempt_index": diagnostic.attempt_index,
        "primary_subcategory": diagnostic.primary_subcategory,
        "issue_reason_counts": diagnostic.issue_reason_counts,
        "issue_id_prefix_counts": diagnostic.issue_id_prefix_counts,
        "required_structure_missing_count": diagnostic.required_structure_missing_count,
        "required_output_missing_count": diagnostic.required_output_missing_count,
        "unknown_anchor_count": diagnostic.unknown_anchor_count,
        "invalid_marker_count": diagnostic.invalid_marker_count,
        "forbidden_phrase_count": diagnostic.forbidden_phrase_count,
        "l1_numerical_closure_count": diagnostic.l1_numerical_closure_count,
        "candidate_facet_assertion_count": diagnostic.candidate_facet_assertion_count,
        "response_length_incomplete_count": diagnostic.response_length_incomplete_count,
        "response_chars": diagnostic.response_chars,
        "max_output_chars": diagnostic.max_output_chars,
        "finish_reason": diagnostic.finish_reason,
        "accepted_draft_present": diagnostic.accepted_draft_present,
    }


def _runtime_diagnostic_payload(
    diagnostic: ChapterLLMRuntimeDiagnostic,
) -> dict[str, object]:
    """把 runtime 诊断转为 allowlist scalar payload。

    Args:
        diagnostic: Service 层 runtime 诊断。

    Returns:
        不含 message、model_name、prompt、draft 或 raw response 的 payload。

    Raises:
        无显式抛出。
    """

    return {
        "operation": diagnostic.operation,
        "repair_attempt_index": diagnostic.repair_attempt_index,
        "provider_attempt_index": diagnostic.provider_attempt_index,
        "provider_max_attempts": diagnostic.provider_max_attempts,
        "provider_runtime_category": diagnostic.provider_runtime_category,
        "chapter_failure_category": diagnostic.chapter_failure_category,
        "elapsed_ms": diagnostic.elapsed_ms,
        "status_code": _safe_status_code(diagnostic.status_code),
        "request_id": diagnostic.request_id,
        "finish_reason": diagnostic.finish_reason,
        "response_chars": diagnostic.response_chars,
        "error_type": diagnostic.error_type,
        "system_prompt_chars": diagnostic.system_prompt_chars,
        "user_prompt_chars": diagnostic.user_prompt_chars,
        "approx_prompt_tokens": diagnostic.approx_prompt_tokens,
        "allowed_fact_count": diagnostic.allowed_fact_count,
        "allowed_anchor_count": diagnostic.allowed_anchor_count,
        "max_output_chars": diagnostic.max_output_chars,
        "timeout_seconds": diagnostic.timeout_seconds,
        "timeout_max_attempts": diagnostic.timeout_max_attempts,
        "timeout_backoff_seconds": diagnostic.timeout_backoff_seconds,
        "timeout_budget_kind": diagnostic.timeout_budget_kind,
        "repair_timeout_fallback_used": diagnostic.repair_timeout_fallback_used,
        "timeout_root_cause_hint": diagnostic.timeout_root_cause_hint,
    }


def _runtime_diagnostics_for_chapter(
    chapter_result: ChapterRunResult,
) -> tuple[ChapterLLMRuntimeDiagnostic, ...]:
    """收集章节级和 attempt 级 runtime 诊断。

    Args:
        chapter_result: 单章编排结果。

    Returns:
        runtime 诊断元组。

    Raises:
        无显式抛出。
    """

    return (
        *chapter_result.runtime_diagnostics,
        *(
            diagnostic
            for attempt in chapter_result.attempts
            for diagnostic in attempt.runtime_diagnostics
        ),
    )


def _safe_status_code(status_code: int | None) -> int | None:
    """过滤非标准 HTTP 状态码。

    Args:
        status_code: provider 诊断中的状态码。

    Returns:
        标准 HTTP 状态码整数；其他值返回 `None`。

    Raises:
        无显式抛出。
    """

    if isinstance(status_code, bool) or not isinstance(status_code, int):
        return None
    if 100 <= status_code <= 599:
        return status_code
    return None


def _programmatic_issues(audit_result: object | None) -> tuple[ChapterAuditIssue, ...]:
    """提取 programmatic audit issues。

    Args:
        audit_result: 审计结果或 `None`。

    Returns:
        programmatic issues。

    Raises:
        无显式抛出。
    """

    if audit_result is None:
        return ()
    return tuple(audit_result.programmatic.issues)


def _llm_issues(audit_result: object | None) -> tuple[ChapterAuditIssue, ...]:
    """提取 LLM audit issues。

    Args:
        audit_result: 审计结果或 `None`。

    Returns:
        LLM issues。

    Raises:
        无显式抛出。
    """

    if audit_result is None:
        return ()
    return tuple(audit_result.llm.issues)


def _redact_text(text: str, stats: _RedactionStats) -> str:
    """对即将写入本地 artifact 的文本执行 canary 脱敏。

    Args:
        text: 原始文本。
        stats: 脱敏计数器。

    Returns:
        脱敏后的文本。

    Raises:
        无显式抛出。
    """

    redacted = text
    for pattern in _SECRET_PATTERNS:
        redacted, count = pattern.subn(REDACTION_REPLACEMENT, redacted)
        stats.count += count
    return redacted


def _safe_text(value: object, *, stats: _RedactionStats) -> str:
    """把 allowlist 字符串字段转换为已脱敏文本。

    Args:
        value: 原始值。
        stats: 脱敏计数器。

    Returns:
        字符串形式的脱敏文本。

    Raises:
        无显式抛出。
    """

    return _redact_text(str(value), stats)


def _optional_text(value: object | None, *, stats: _RedactionStats) -> str | None:
    """把可空字符串字段转换为已脱敏文本。

    Args:
        value: 原始值。
        stats: 脱敏计数器。

    Returns:
        `None` 或字符串形式的脱敏文本。

    Raises:
        无显式抛出。
    """

    if value is None:
        return None
    return _safe_text(value, stats=stats)


def _atomic_write_json(path: Path, payload: dict[str, object]) -> None:
    """原子写入 JSON 文件。

    Args:
        path: 目标路径。
        payload: JSON payload。

    Returns:
        无返回值。

    Raises:
        OSError: 当文件写入失败时抛出。
        TypeError: 当 payload 无法 JSON 序列化时抛出。
    """

    text = json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    _atomic_write_text(path, text)


def _atomic_write_text(path: Path, text: str) -> None:
    """原子写入 UTF-8 文本文件。

    Args:
        path: 目标路径。
        text: 文件内容。

    Returns:
        无返回值。

    Raises:
        OSError: 当文件写入失败时抛出。
    """

    temp_path = path.with_name(f".{path.name}.tmp")
    temp_path.write_text(text, encoding="utf-8")
    temp_path.replace(path)


def _run_artifact_dir(
    output_root: Path,
    *,
    fund_code: str,
    report_year: int,
    created_at: datetime,
    host_run_id: str | None,
) -> Path:
    """构造本次运行 artifact 目录。

    Args:
        output_root: artifact 根目录。
        fund_code: 基金代码。
        report_year: 年报年份。
        created_at: 创建时间。
        host_run_id: Host run id。

    Returns:
        本次运行 artifact 目录路径。

    Raises:
        无显式抛出。
    """

    run_id_suffix = _safe_path_component(host_run_id or "no-host-run")[:_RUN_ID_MAX_CHARS]
    return output_root / (
        f"{_safe_path_component(fund_code)}-{report_year}-"
        f"{_timestamp_for_path(created_at)}-{run_id_suffix}"
    )


def _current_time(clock: Callable[[], datetime] | None) -> datetime:
    """取得带时区的当前时间。

    Args:
        clock: 可选时间函数。

    Returns:
        带时区的当前时间。

    Raises:
        无显式抛出。
    """

    now = clock() if clock is not None else datetime.now(timezone.utc)
    if now.tzinfo is None:
        return now.replace(tzinfo=timezone.utc)
    return now


def _timestamp_for_path(value: datetime) -> str:
    """把时间转换为路径安全的紧凑格式。

    Args:
        value: 带时区时间。

    Returns:
        路径安全时间戳。

    Raises:
        无显式抛出。
    """

    if value.utcoffset() == timezone.utc.utcoffset(value):
        return value.astimezone(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return value.strftime("%Y%m%dT%H%M%S%z")


def _isoformat(value: datetime) -> str:
    """把时间转换为 ISO-8601 字符串。

    Args:
        value: 带时区时间。

    Returns:
        ISO-8601 时间字符串。

    Raises:
        无显式抛出。
    """

    if value.utcoffset() == timezone.utc.utcoffset(value):
        return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
    return value.isoformat()


def _safe_path_component(value: str) -> str:
    """把任意短字符串转换为路径安全片段。

    Args:
        value: 原始字符串。

    Returns:
        仅包含字母、数字、点、下划线和短横线的路径片段。

    Raises:
        无显式抛出。
    """

    cleaned = re.sub(r"[^A-Za-z0-9_.-]+", "-", value).strip(".-")
    return cleaned or "unknown"


def _relative_posix(path: Path, root: Path) -> str:
    """生成相对 artifact 根目录的 POSIX 路径。

    Args:
        path: 子路径。
        root: artifact 根目录。

    Returns:
        POSIX 风格相对路径。

    Raises:
        ValueError: 当路径无法相对化时由 `Path.relative_to()` 抛出。
    """

    return path.relative_to(root).as_posix()
