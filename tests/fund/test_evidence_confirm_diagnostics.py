"""Evidence Confirm V2 安全诊断聚合测试。"""

from __future__ import annotations

from fund_agent.fund.evidence_confirm import (
    EVIDENCE_CONFIRM_V2_SCHEMA_VERSION,
    EvidenceConfirmDimensionResult,
    EvidenceConfirmFactResultV2,
    EvidenceConfirmHardGate,
    EvidenceConfirmIssue,
    EvidenceConfirmResultV2,
)
from fund_agent.fund.evidence_confirm_diagnostics import (
    EVIDENCE_CONFIRM_DIAGNOSTIC_SCHEMA_VERSION,
    summarize_evidence_confirm_diagnostics,
)


def test_summarize_evidence_confirm_diagnostics_groups_failed_dimensions() -> None:
    """验证 V2 诊断按维度、字段和章节聚合失败/警告。"""

    result = _result(
        (
            _fact(
                fact_id="chapter-fact:110011:2024:ch3:structured.manager_strategy_text",
                source_field_id="structured.manager_strategy_text",
                status="fail",
                dimensions=(
                    _dimension("missing_evidence", "fail", ("issue-missing",), "evidence_anchor"),
                    _dimension("value_match", "fail", ("issue-value",), "value_matching"),
                ),
            ),
            _fact(
                fact_id="chapter-fact:110011:2024:ch3:structured.manager_strategy_text:second",
                source_field_id="structured.manager_strategy_text",
                status="fail",
                dimensions=(
                    _dimension("missing_evidence", "fail", ("issue-missing-2",), "evidence_anchor"),
                ),
            ),
            _fact(
                fact_id="chapter-fact:110011:2024:ch4:structured.investor_return",
                source_field_id="structured.investor_return",
                status="warn",
                dimensions=(
                    _dimension("anchor_precision", "warn", ("issue-precision",), "evidence_anchor"),
                ),
            ),
        )
    )

    summary = summarize_evidence_confirm_diagnostics(result)

    assert summary.schema_version == EVIDENCE_CONFIRM_DIAGNOSTIC_SCHEMA_VERSION
    assert summary.fund_code == "110011"
    assert summary.report_year == 2024
    assert summary.checked_fact_count == 3
    assert summary.failed_fact_count == 2
    assert summary.warning_fact_count == 1
    assert summary.issue_count == 4
    assert len(summary.diagnostic_buckets) == 3
    missing_bucket = summary.diagnostic_buckets[0]
    value_bucket = summary.diagnostic_buckets[1]
    precision_bucket = summary.diagnostic_buckets[2]
    assert missing_bucket.dimension == "missing_evidence"
    assert missing_bucket.status == "fail"
    assert missing_bucket.source_field_id == "structured.manager_strategy_text"
    assert missing_bucket.chapter_id == 3
    assert missing_bucket.fact_count == 2
    assert missing_bucket.issue_ids == ("issue-missing", "issue-missing-2")
    assert missing_bucket.root_cause_classification == "projection_attachment_defect"
    assert value_bucket.dimension == "value_match"
    assert value_bucket.root_cause_classification == "undetermined"
    assert precision_bucket.dimension == "anchor_precision"
    assert precision_bucket.status == "warn"
    assert precision_bucket.root_cause_classification == "true_anchor_precision_gap"
    assert summary.dominant_root_cause_classifications == (
        "projection_attachment_defect",
        "undetermined",
        "true_anchor_precision_gap",
    )


def test_summarize_evidence_confirm_diagnostics_omits_raw_text_and_paths() -> None:
    """验证诊断输出只包含安全标量和稳定 ID。"""

    result = _result(
        (
            _fact(
                fact_id="chapter-fact:110011:2024:ch3:structured.manager_strategy_text",
                source_field_id="structured.manager_strategy_text",
                status="fail",
                dimensions=(
                    _dimension("source_support", "fail", ("issue-source",), "source_truth_proof"),
                ),
            ),
        )
    )

    safe_payload = summarize_evidence_confirm_diagnostics(result).to_safe_dict()
    rendered = repr(safe_payload)

    assert "issue-source" in rendered
    assert "source_support" in rendered
    assert "原文" not in rendered
    assert "excerpt" not in rendered
    assert "cache/pdf" not in rendered
    assert ".pdf" not in rendered
    assert "/Users/" not in rendered
    assert "Evidence Confirm issue message with raw text" not in rendered


def _result(
    fact_results: tuple[EvidenceConfirmFactResultV2, ...],
) -> EvidenceConfirmResultV2:
    """构造测试用 V2 聚合结果。"""

    issues = tuple(
        EvidenceConfirmIssue(
            issue_id=issue_id,
            rule_code="E3",
            severity="blocking",
            fact_id=fact.fact_id,
            source_field_id=fact.source_field_id,
            anchor_id=None,
            message="Evidence Confirm issue message with raw text",
        )
        for fact in fact_results
        for issue_id in fact.issue_ids
    )
    hard_gate = EvidenceConfirmHardGate(
        status="fail",
        blocking_issue_ids=tuple(issue.issue_id for issue in issues),
        reviewable_issue_ids=(),
        informational_issue_ids=(),
        passed_dimension_count=0,
        failed_dimension_count=sum(
            1
            for fact in fact_results
            for dimension in fact.dimension_results
            if dimension.status == "fail"
        ),
        warn_dimension_count=sum(
            1
            for fact in fact_results
            for dimension in fact.dimension_results
            if dimension.status == "warn"
        ),
        not_applicable_dimension_count=0,
    )
    return EvidenceConfirmResultV2(
        schema_version=EVIDENCE_CONFIRM_V2_SCHEMA_VERSION,
        fund_code="110011",
        report_year=2024,
        fact_results=fact_results,
        issues=issues,
        checked_rules=("E1", "E2", "E3"),
        hard_gate=hard_gate,
        overall_status="fail",
        auditability_score=0,
    )


def _fact(
    *,
    fact_id: str,
    source_field_id: str,
    status: str,
    dimensions: tuple[EvidenceConfirmDimensionResult, ...],
) -> EvidenceConfirmFactResultV2:
    """构造测试用 V2 fact result。"""

    issue_ids = tuple(
        issue_id for dimension in dimensions for issue_id in dimension.issue_ids
    )
    hard_gate = EvidenceConfirmHardGate(
        status=status,  # type: ignore[arg-type]
        blocking_issue_ids=issue_ids if status == "fail" else (),
        reviewable_issue_ids=issue_ids if status == "warn" else (),
        informational_issue_ids=(),
        passed_dimension_count=0,
        failed_dimension_count=sum(1 for dimension in dimensions if dimension.status == "fail"),
        warn_dimension_count=sum(1 for dimension in dimensions if dimension.status == "warn"),
        not_applicable_dimension_count=0,
    )
    return EvidenceConfirmFactResultV2(
        fact_id=fact_id,
        source_field_id=source_field_id,
        status=status,  # type: ignore[arg-type]
        hard_gate=hard_gate,
        dimension_results=dimensions,
        matched_anchor_ids=(),
        issue_ids=issue_ids,
        auditability_score=0 if status == "fail" else 94,
    )


def _dimension(
    dimension: str,
    status: str,
    issue_ids: tuple[str, ...],
    next_gate: str,
) -> EvidenceConfirmDimensionResult:
    """构造测试用 V2 dimension result。"""

    return EvidenceConfirmDimensionResult(
        dimension=dimension,  # type: ignore[arg-type]
        status=status,  # type: ignore[arg-type]
        score=0 if status == "fail" else 70,
        issue_ids=issue_ids,
        matched_anchor_ids=(),
        next_gate_recommendation=next_gate,  # type: ignore[arg-type]
    )
