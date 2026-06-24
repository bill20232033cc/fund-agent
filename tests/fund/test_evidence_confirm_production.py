"""Evidence Confirm 生产摘要测试。"""

from __future__ import annotations

from dataclasses import asdict

import pytest

from fund_agent.fund.evidence_confirm import (
    EVIDENCE_CONFIRM_V2_SCHEMA_VERSION,
    EvidenceConfirmDimensionResult,
    EvidenceConfirmFactResultV2,
    EvidenceConfirmHardGate,
    EvidenceConfirmIssue,
    EvidenceConfirmReference,
    EvidenceConfirmResultV2,
)
from fund_agent.fund.evidence_confirm_production import (
    EvidenceConfirmProductionSummary,
    not_run_evidence_confirm_summary,
    summary_from_repository_result,
)
from fund_agent.fund.evidence_confirm_sources import (
    EvidenceConfirmReferenceBuildResult,
    EvidenceConfirmRepositoryRunIssue,
    EvidenceConfirmRepositoryRunResult,
)


def test_summary_from_repository_fail_is_compact_and_no_excerpt() -> None:
    """验证 repository 失败结果会转为 compact fail 摘要且不泄漏 excerpt。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 摘要泄漏原文或未 fail-closed 时抛出。
    """

    result = EvidenceConfirmRepositoryRunResult(
        status="fail",
        pathway_status="fail",
        pathway_warning_reasons=(),
        fund_code="110011",
        report_year=2024,
        source_provenance=None,
        reference_build_result=None,
        evidence_confirm_result=None,
        issues=(
            EvidenceConfirmRepositoryRunIssue(
                issue_id="evidence-confirm-repository:repository_load_failed",
                severity="blocking",
                reason="repository_load_failed",
                message="repository failed with raw excerpt: SHOULD_NOT_LEAK",
                failure_category="unavailable",
            ),
        ),
    )

    summary = summary_from_repository_result(result, "block")
    payload = asdict(summary)

    assert summary.status == "fail"
    assert summary.pathway_status == "fail"
    assert summary.deterministic_status == "not_run"
    assert summary.provenance_status == "not_run"
    assert summary.minimum_provenance_tier == "none"
    assert summary.not_run_reason == "repository_failure:repository_load_failed"
    assert summary.blocking_issue_ids == ("evidence-confirm-repository:repository_load_failed",)
    assert "excerpt" not in payload
    assert "SHOULD_NOT_LEAK" not in repr(payload)


def test_summary_from_repository_pass_is_compact_and_counts_checked_facts() -> None:
    """验证 repository pass + deterministic pass 会转为 compact pass 摘要。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 摘要状态或 compact 边界不符合预期时抛出。
    """

    result = _repository_result(_v2_result(status="pass"))

    summary = summary_from_repository_result(result, "block")
    payload = asdict(summary)

    assert summary.status == "pass"
    assert summary.pathway_status == "pass"
    assert summary.deterministic_status == "pass"
    assert summary.provenance_status == "pass"
    assert summary.minimum_provenance_tier == "section"
    assert summary.provenance_missing_fact_count == 0
    assert summary.strict_precision_residual_count == 0
    assert summary.checked_fact_count == 1
    assert summary.failed_fact_count == 0
    assert summary.warning_fact_count == 0
    assert summary.issue_count == 0
    assert summary.blocking_issue_ids == ()
    assert summary.warning_issue_ids == ()
    assert "excerpt" not in payload


def test_summary_legacy_shape_defaults_provenance_to_not_run() -> None:
    """验证旧形状摘要构造会保守降级为 provenance not_run。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: provenance 默认值不是 fail-closed 语义时抛出。
    """

    summary = EvidenceConfirmProductionSummary(
        schema_version="evidence_confirm_production_summary.v2",
        policy="block",
        status="pass",
        fund_code="110011",
        report_year=2024,
        pathway_status="pass",
        deterministic_status="pass",
        semantic_status="not_run",
        checked_fact_count=1,
        failed_fact_count=0,
        warning_fact_count=0,
        not_applicable_fact_count=0,
        issue_count=0,
        auditability_score=100,
        blocking_issue_ids=(),
        warning_issue_ids=(),
        not_run_reason=None,
    )

    assert summary.provenance_status == "not_run"
    assert summary.minimum_provenance_tier == "none"
    assert summary.provenance_missing_fact_count == 0
    assert summary.strict_precision_residual_count == 0
    assert summary.strict_precision_issue_ids == ()


def test_summary_from_repository_warn_keeps_reviewable_and_informational_ids() -> None:
    """验证 V2 reviewable 与 informational issue 都进入生产可见非阻断 ID 列表。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: warning ids 或 issue_count 口径不一致时抛出。
    """

    reviewable_issue = _issue("evidence-confirm:e1:reviewable", "reviewable")
    informational_issue = _issue("evidence-confirm:e3:informational", "informational")
    result = _repository_result(
        _v2_result(
            status="warn",
            issues=(reviewable_issue, informational_issue),
            reviewable_issue_ids=(reviewable_issue.issue_id,),
            informational_issue_ids=(informational_issue.issue_id,),
        ),
        pathway_warning_reasons=("anchor_precision_warn",),
    )

    summary = summary_from_repository_result(result, "warn")

    assert summary.status == "warn"
    assert summary.deterministic_status == "warn"
    assert summary.warning_fact_count == 1
    assert summary.issue_count == 2
    assert summary.provenance_status == "pass"
    assert summary.minimum_provenance_tier == "section"
    assert summary.warning_issue_ids == (
        "pathway:anchor_precision_warn",
        "evidence-confirm:e1:reviewable",
        "evidence-confirm:e3:informational",
    )


@pytest.mark.parametrize(
    "reason",
    (
        "invalid_request",
        "runner_exception:RuntimeError",
        "repository_failure:source_unavailable",
    ),
)
def test_not_run_evidence_confirm_summary_accepts_stable_reason_variants(reason: str) -> None:
    """验证 not-run 摘要接受 EC-P4 Slice 1 稳定原因码变体。

    Args:
        reason: 待验证的稳定原因码。

    Returns:
        无返回值。

    Raises:
        AssertionError: 合法原因码未保留时抛出。
    """

    summary = not_run_evidence_confirm_summary(
        fund_code="110011",
        report_year=2024,
        policy="warn",
        reason=reason,
    )

    assert summary.status == "not_run"
    assert summary.schema_version == "evidence_confirm_production_summary.v2"
    assert summary.provenance_status == "not_run"
    assert summary.minimum_provenance_tier == "none"
    assert summary.not_run_reason == reason


def test_not_run_evidence_confirm_summary_rejects_invalid_reason() -> None:
    """验证 not-run 摘要拒绝未登记原因码。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 非法原因码未抛错时抛出。
    """

    with pytest.raises(ValueError, match="reason"):
        not_run_evidence_confirm_summary(
            fund_code="110011",
            report_year=2024,
            policy="warn",
            reason="temporary_unclassified_reason",
        )


def test_not_run_evidence_confirm_summary_rejects_invalid_policy() -> None:
    """验证 not-run 摘要拒绝非法 policy。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 非法 policy 未抛错时抛出。
    """

    with pytest.raises(ValueError, match="policy"):
        not_run_evidence_confirm_summary(
            fund_code="110011",
            report_year=2024,
            policy="fail",
            reason="invalid_request",
        )


def test_summary_from_repository_not_applicable_boundary_is_not_run() -> None:
    """验证 deterministic not_applicable 边界不会被聚合成 pass。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: not_applicable 聚合边界不符合预期时抛出。
    """

    summary = summary_from_repository_result(
        _repository_result(_v2_result(status="not_applicable")),
        "block",
    )

    assert summary.status == "not_run"
    assert summary.deterministic_status == "not_applicable"
    assert summary.provenance_status == "not_run"
    assert summary.minimum_provenance_tier == "none"
    assert summary.not_applicable_fact_count == 1
    assert summary.checked_fact_count == 1


def test_summary_from_repository_table_and_row_references_use_stronger_tiers() -> None:
    """验证 table / row reference 会产生强于 section 的 provenance tier。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: provenance tier 计算错误时抛出。
    """

    table_summary = summary_from_repository_result(
        _repository_result(
            _v2_result(status="pass"),
            references=(_reference(anchor_id="anchor-1", table_id="table-1"),),
        ),
        "block",
    )
    row_summary = summary_from_repository_result(
        _repository_result(
            _v2_result(status="pass"),
            references=(
                _reference(
                    anchor_id="anchor-1",
                    table_id="table-1",
                    row_locator="row-3",
                ),
            ),
        ),
        "block",
    )

    assert table_summary.provenance_status == "pass"
    assert table_summary.minimum_provenance_tier == "table"
    assert row_summary.provenance_status == "pass"
    assert row_summary.minimum_provenance_tier == "row"
    assert table_summary.minimum_provenance_tier != "cell"
    assert row_summary.minimum_provenance_tier != "cell"


def test_summary_from_repository_missing_source_support_fails_provenance() -> None:
    """验证 source_support / missing_evidence 失败会计入 provenance missing。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: provenance missing 口径错误时抛出。
    """

    summary = summary_from_repository_result(
        _repository_result(
            _v2_result(
                status="fail",
                source_support_status="fail",
                missing_evidence_status="pass",
                value_match_status="not_applicable",
            )
        ),
        "block",
    )

    assert summary.provenance_status == "fail"
    assert summary.minimum_provenance_tier == "section"
    assert summary.provenance_missing_fact_count == 1
    assert summary.strict_precision_residual_count == 0


def test_summary_from_repository_value_match_fail_with_provenance_is_strict_residual() -> None:
    """验证 provenance 通过但 value_match 失败会进入 strict precision residual。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: strict precision residual 统计错误时抛出。
    """

    summary = summary_from_repository_result(
        _repository_result(
            _v2_result(
                status="fail",
                source_support_status="pass",
                missing_evidence_status="pass",
                value_match_status="fail",
                value_match_issue_ids=("evidence-confirm:e2:value-mismatch",),
            )
        ),
        "warn",
    )

    assert summary.status == "fail"
    assert summary.provenance_status == "pass"
    assert summary.minimum_provenance_tier == "section"
    assert summary.provenance_missing_fact_count == 0
    assert summary.strict_precision_residual_count == 1
    assert summary.strict_precision_issue_ids == ("evidence-confirm:e2:value-mismatch",)


def test_summary_from_repository_v2_pass_without_reference_is_not_provenance_pass() -> None:
    """验证 reference_build_result 缺失时不能把 V2 pass 当作 provenance pass。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 缺失 reference 被误判为 provenance pass 时抛出。
    """

    result = _repository_result(_v2_result(status="pass"), references=None)

    summary = summary_from_repository_result(result, "block")

    assert summary.deterministic_status == "pass"
    assert summary.provenance_status == "not_run"
    assert summary.minimum_provenance_tier == "none"
    assert summary.provenance_missing_fact_count == 0
    assert summary.strict_precision_residual_count == 0


def _repository_result(
    evidence_confirm_result: EvidenceConfirmResultV2,
    *,
    pathway_warning_reasons: tuple[str, ...] = (),
    references: tuple[EvidenceConfirmReference, ...] | None = (
        EvidenceConfirmReference(
            anchor_id="anchor-1",
            reference_kind="annual_report_excerpt",
            source_kind="annual_report",
            document_year=2024,
            section_id="§2",
            page_number=12,
            table_id=None,
            row_locator=None,
            excerpt_text="section excerpt without raw payload",
        ),
    ),
) -> EvidenceConfirmRepositoryRunResult:
    """构造测试用 repository runner 结果。

    Args:
        evidence_confirm_result: V2 复核结果。
        pathway_warning_reasons: pathway warning 原因码。
        references: reference build result references；``None`` 表示未构建 reference。

    Returns:
        Repository runner 结果。

    Raises:
        无显式抛出。
    """

    return EvidenceConfirmRepositoryRunResult(
        status="pass",
        pathway_status="pass",
        pathway_warning_reasons=pathway_warning_reasons,
        fund_code="110011",
        report_year=2024,
        source_provenance=None,
        reference_build_result=(
            None
            if references is None
            else EvidenceConfirmReferenceBuildResult(
                references=references,
                issues=(),
                status="pass",
            )
        ),
        evidence_confirm_result=evidence_confirm_result,
        issues=(),
    )


def _v2_result(
    *,
    status: str,
    source_support_status: str | None = None,
    missing_evidence_status: str | None = None,
    value_match_status: str | None = None,
    value_match_issue_ids: tuple[str, ...] = (),
    issues: tuple[EvidenceConfirmIssue, ...] = (),
    reviewable_issue_ids: tuple[str, ...] = (),
    informational_issue_ids: tuple[str, ...] = (),
) -> EvidenceConfirmResultV2:
    """构造测试用 V2 复核结果。

    Args:
        status: V2 聚合状态。
        source_support_status: source_support 维度状态。
        missing_evidence_status: missing_evidence 维度状态。
        value_match_status: value_match 维度状态。
        value_match_issue_ids: value_match 维度 issue ids。
        issues: V2 issue 列表。
        reviewable_issue_ids: hard gate reviewable issue ids。
        informational_issue_ids: hard gate informational issue ids。

    Returns:
        V2 复核结果。

    Raises:
        无显式抛出。
    """

    dimension_results = _dimension_results(
        status=status,
        source_support_status=source_support_status,
        missing_evidence_status=missing_evidence_status,
        value_match_status=value_match_status,
        value_match_issue_ids=value_match_issue_ids,
    )
    hard_gate = EvidenceConfirmHardGate(
        status=status,
        blocking_issue_ids=(),
        reviewable_issue_ids=reviewable_issue_ids,
        informational_issue_ids=informational_issue_ids,
        passed_dimension_count=5 if status == "pass" else 0,
        failed_dimension_count=0,
        warn_dimension_count=1 if status == "warn" else 0,
        not_applicable_dimension_count=5 if status == "not_applicable" else 0,
    )
    fact_result = EvidenceConfirmFactResultV2(
        fact_id="fact-1",
        source_field_id="field-1",
        status=status,
        hard_gate=hard_gate,
        dimension_results=dimension_results,
        matched_anchor_ids=("anchor-1",) if status in {"pass", "warn"} else (),
        issue_ids=tuple(issue.issue_id for issue in issues) + value_match_issue_ids,
        auditability_score=100 if status == "pass" else None,
    )
    return EvidenceConfirmResultV2(
        schema_version=EVIDENCE_CONFIRM_V2_SCHEMA_VERSION,
        fund_code="110011",
        report_year=2024,
        fact_results=(fact_result,),
        issues=issues,
        checked_rules=("E1", "E2", "E3"),
        hard_gate=hard_gate,
        overall_status=status,
        auditability_score=100 if status == "pass" else None,
    )


def _dimension_results(
    *,
    status: str,
    source_support_status: str | None,
    missing_evidence_status: str | None,
    value_match_status: str | None,
    value_match_issue_ids: tuple[str, ...],
) -> tuple[EvidenceConfirmDimensionResult, ...]:
    """构造测试用 V2 dimension results。

    Args:
        status: fact/V2 聚合状态。
        source_support_status: source_support 维度状态。
        missing_evidence_status: missing_evidence 维度状态。
        value_match_status: value_match 维度状态。
        value_match_issue_ids: value_match 维度 issue ids。

    Returns:
        五维度结果。

    Raises:
        无显式抛出。
    """

    if status == "not_applicable":
        return tuple(
            EvidenceConfirmDimensionResult(
                dimension=dimension,  # type: ignore[arg-type]
                status="not_applicable",
                score=None,
                issue_ids=(),
                matched_anchor_ids=(),
                next_gate_recommendation="not_applicable",
            )
            for dimension in (
                "anchor_precision",
                "source_support",
                "missing_evidence",
                "proof_boundary",
                "value_match",
            )
        )
    source_status = source_support_status or ("pass" if status in {"pass", "warn"} else "fail")
    missing_status = missing_evidence_status or ("pass" if status in {"pass", "warn"} else "fail")
    value_status = value_match_status or ("pass" if status in {"pass", "warn"} else "fail")
    return (
        _dimension("anchor_precision", "warn" if status == "warn" else "pass"),
        _dimension("source_support", source_status, matched_anchor_ids=("anchor-1",)),
        _dimension("missing_evidence", missing_status, matched_anchor_ids=("anchor-1",)),
        _dimension("proof_boundary", "pass"),
        _dimension("value_match", value_status, issue_ids=value_match_issue_ids),
    )


def _dimension(
    dimension: str,
    status: str,
    *,
    issue_ids: tuple[str, ...] = (),
    matched_anchor_ids: tuple[str, ...] = (),
) -> EvidenceConfirmDimensionResult:
    """构造测试用单维度结果。

    Args:
        dimension: 维度名。
        status: 维度状态。
        issue_ids: issue ids。
        matched_anchor_ids: matched anchor ids。

    Returns:
        Evidence Confirm dimension result。

    Raises:
        无显式抛出。
    """

    return EvidenceConfirmDimensionResult(
        dimension=dimension,  # type: ignore[arg-type]
        status=status,  # type: ignore[arg-type]
        score=100 if status == "pass" else 0 if status == "fail" else None,
        issue_ids=issue_ids,
        matched_anchor_ids=matched_anchor_ids if status == "pass" else (),
        next_gate_recommendation="value_matching" if dimension == "value_match" else "evidence_anchor",
    )


def _reference(
    *,
    anchor_id: str,
    table_id: str | None = None,
    row_locator: str | None = None,
) -> EvidenceConfirmReference:
    """构造测试用 repository-bounded reference。

    Args:
        anchor_id: anchor id。
        table_id: 表格 id。
        row_locator: 行定位。

    Returns:
        Evidence Confirm reference。

    Raises:
        无显式抛出。
    """

    return EvidenceConfirmReference(
        anchor_id=anchor_id,
        reference_kind="annual_report_excerpt",
        source_kind="annual_report",
        document_year=2024,
        section_id="§2",
        page_number=12,
        table_id=table_id,
        row_locator=row_locator,
        excerpt_text="section excerpt without raw payload",
    )


def _issue(issue_id: str, severity: str) -> EvidenceConfirmIssue:
    """构造测试用 Evidence Confirm issue。

    Args:
        issue_id: 稳定 issue id。
        severity: issue 严重程度。

    Returns:
        Evidence Confirm issue。

    Raises:
        无显式抛出。
    """

    return EvidenceConfirmIssue(
        issue_id=issue_id,
        rule_code="E3",
        severity=severity,
        fact_id="fact-1",
        source_field_id="field-1",
        anchor_id="anchor-1",
        message="测试 issue，不含原文摘录。",
    )
