"""报告质量评分 JSONL 内容校验测试。"""

from __future__ import annotations

import json
from pathlib import Path

from fund_agent.fund.report_evidence import (
    REPORT_EVIDENCE_SCHEMA_VERSION,
    ReportEvidenceBundle,
    ReportEvidenceAnchor,
    ReportFact,
    ReportPreferredLensChapter,
    ReportPreferredLensProjection,
    ReportQualityContext,
    ReportSourceDocument,
)
from fund_agent.fund.report_quality_validation import (
    ReportQualityValidationIssue,
    validate_report_quality_bundle,
    validate_report_quality_jsonl,
)


def test_valid_scoring_ready_bundle_passes_without_issues() -> None:
    """验证最小 scoring_ready bundle 可通过校验。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 校验结果不符合预期时抛出。
    """

    result = validate_report_quality_bundle(_valid_bundle_dict(), run_id="score-run:test")

    assert result.issues == ()
    assert result.summary.total_records == 1
    assert result.summary.scoring_ready_record_count == 1
    assert result.summary.failed_closed is False
    assert result.run_id == "score-run:test"


def test_dataclass_bundle_input_is_supported() -> None:
    """验证 dataclass bundle 输入会在 validator 内部序列化。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: dataclass 输入校验失败时抛出。
    """

    bundle = ReportEvidenceBundle(
        bundle_id="bundle:004393:2024",
        schema_version=REPORT_EVIDENCE_SCHEMA_VERSION,
        corpus_id="corpus:baseline:v1",
        fund_code="004393",
        report_year=2024,
        classified_fund_type="active_fund",
        type_slot_membership_status="matches_slot",
        fund_type_slot="active_fund",
        preferred_lens=ReportPreferredLensProjection(
            fund_type="active_fund",
            chapters=tuple(
                ReportPreferredLensChapter(
                    chapter_id=f"chapter_{index}",  # type: ignore[arg-type]
                    lens_key="active_fund",
                    used_default=False,
                    primary_focus="超额收益稳定性",
                )
                for index in range(8)
            ),
        ),
        quality_context=ReportQualityContext(
            fq_gate_status="pass",
            programmatic_audit_status="pass",
            judgment_constraint="cautious_only",
        ),
        review_status="scoring_ready",
        source_documents=(
            ReportSourceDocument(
                document_id="doc:004393:2024:annual_report",
                document_type="annual_report",
                identity_status="verified_annual_report",
                source_boundary="repository_derived",
                source_failure_category="none",
                fallback_allowed=False,
                fallback_used=False,
            ),
        ),
        facts=(
            ReportFact(
                fact_id="fact:basic_identity",
                category="identity",
                field_path="basic_identity",
                value={"fund_name": "测试基金"},
                unit="object",
                source_boundary="repository_derived",
                extraction_mode="direct",
                review_status="reviewed",
                source_anchor_ids=("anchor:004393:2024:annual_report:sec2:abc12345",),
                source_document_ids=("doc:004393:2024:annual_report",),
            ),
        ),
        evidence_anchors=(
            ReportEvidenceAnchor(
                anchor_id="anchor:004393:2024:annual_report:sec2:abc12345",
                source_kind="annual_report",
                source_strength="fund_disclosure",
                document_id="doc:004393:2024:annual_report",
                document_year=2024,
                section_id="sec2",
            ),
        ),
        data_gaps=(),
        score_issue_links=(),
        derived_calculations=(),
        validation_messages=(),
    )

    result = validate_report_quality_bundle(bundle)

    assert result.issues == ()
    assert result.schema_version == REPORT_EVIDENCE_SCHEMA_VERSION


def test_jsonl_accepts_bundle_record_and_score_issue_records(tmp_path) -> None:
    """验证 JSONL 同时支持 bundle record 和 score_issue record。

    Args:
        tmp_path: pytest 临时目录。

    Returns:
        无返回值。

    Raises:
        AssertionError: JSONL 校验失败时抛出。
    """

    jsonl_path = tmp_path / "quality.jsonl"
    bundle = {"record_type": "bundle", **_valid_bundle_dict(review_status="fact_prefill_reviewed")}
    score_issue = {
        "record_type": "score_issue",
        "issue_id": "issue:chapter2:pass",
        "score_run_id": "score-run:test",
        "chapter_id": "chapter_2",
        "dimension": "fact_coverage",
        "status": "pass",
        "next_gate_recommendation": "review_acceptance",
        "evidence_anchor_refs": ["anchor:004393:2024:annual_report:sec2:abc12345"],
        "data_gap_refs": [],
    }
    jsonl_path.write_text(
        json.dumps(bundle, ensure_ascii=False) + "\n" + json.dumps(score_issue, ensure_ascii=False),
        encoding="utf-8",
    )

    result = validate_report_quality_jsonl(jsonl_path)

    assert result.summary.total_records == 2
    assert result.summary.failed_closed is False
    assert result.run_id == "score-run:test"


def test_jsonl_multi_bundle_score_issue_records_use_nearest_preceding_bundle(tmp_path) -> None:
    """验证多 bundle JSONL 的 score_issue 归属到最近前置 bundle。

    Args:
        tmp_path: pytest 临时目录。

    Returns:
        无返回值。

    Raises:
        AssertionError: 多 bundle score_issue 归属错误时抛出。
    """

    jsonl_path = tmp_path / "multi-bundle-quality.jsonl"
    first_bundle = {"record_type": "bundle", **_valid_bundle_dict(review_status="fact_prefill_reviewed")}
    second_bundle = {"record_type": "bundle", **_second_bundle_dict()}
    first_issue = _external_score_issue(
        issue_id="issue:first-pass",
        evidence_anchor_refs=["anchor:004393:2024:annual_report:sec2:abc12345"],
    )
    second_issue = _external_score_issue(
        issue_id="issue:second-pass",
        evidence_anchor_refs=["anchor:004194:2024:annual_report:sec2:def67890"],
    )
    _write_jsonl_records(jsonl_path, (first_bundle, first_issue, second_bundle, second_issue))

    result = validate_report_quality_jsonl(jsonl_path)

    assert result.summary.total_records == 4
    assert result.issues == ()
    assert result.summary.failed_closed is False


def test_jsonl_score_issue_after_second_bundle_cannot_reference_first_bundle_ids(tmp_path) -> None:
    """验证 score_issue 不得引用所属 bundle 之外的 anchor 或 gap。

    Args:
        tmp_path: pytest 临时目录。

    Returns:
        无返回值。

    Raises:
        AssertionError: 跨 bundle 引用未阻断时抛出。
    """

    jsonl_path = tmp_path / "cross-bundle-ref.jsonl"
    first_bundle = {"record_type": "bundle", **_valid_bundle_dict(review_status="fact_prefill_reviewed")}
    first_bundle["data_gaps"] = [_gap_dict(gap_id="gap:first")]
    second_bundle = {"record_type": "bundle", **_second_bundle_dict()}
    second_bundle["data_gaps"] = [_gap_dict(gap_id="gap:second")]
    cross_bundle_issue = _external_score_issue(
        issue_id="issue:cross-bundle",
        status="issue",
        severity="material",
        field_path="turnover_rate",
        evidence_anchor_refs=["anchor:004393:2024:annual_report:sec2:abc12345"],
        data_gap_refs=["gap:first"],
        next_gate_recommendation="data_extraction",
    )
    _write_jsonl_records(jsonl_path, (first_bundle, second_bundle, cross_bundle_issue))

    result = validate_report_quality_jsonl(jsonl_path)

    assert _has_issue(
        result.issues,
        "RQV_REF_MISSING",
        "blocking",
        "line:3/score_issue/data_gap_refs/0",
    )
    assert _has_issue(
        result.issues,
        "RQV_REF_MISSING",
        "blocking",
        "line:3/score_issue/evidence_anchor_refs/0",
    )
    assert result.summary.failed_closed is True


def test_jsonl_score_issue_before_bundle_is_blocking(tmp_path) -> None:
    """验证 bundle 前的裸 score_issue 会 fail-closed。

    Args:
        tmp_path: pytest 临时目录。

    Returns:
        无返回值。

    Raises:
        AssertionError: 前置裸 score_issue 未阻断时抛出。
    """

    jsonl_path = tmp_path / "score-issue-before-bundle.jsonl"
    score_issue = _external_score_issue(
        issue_id="issue:orphan",
        evidence_anchor_refs=["anchor:004393:2024:annual_report:sec2:abc12345"],
    )
    bundle = {"record_type": "bundle", **_valid_bundle_dict(review_status="fact_prefill_reviewed")}
    _write_jsonl_records(jsonl_path, (score_issue, bundle))

    result = validate_report_quality_jsonl(jsonl_path)

    assert _has_issue(result.issues, "RQV_SCORE_ISSUE_ORPHANED", "blocking", "line:1")
    assert result.summary.failed_closed is True


def test_missing_required_bundle_field_is_blocking() -> None:
    """验证缺少 bundle 必填字段会阻断。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 未输出阻断 issue 时抛出。
    """

    bundle = _valid_bundle_dict()
    del bundle["fund_code"]

    result = validate_report_quality_bundle(bundle)

    assert _has_issue(result.issues, "RQV_FIELD_MISSING", "blocking", "/bundle/fund_code")
    assert result.summary.failed_closed is True


def test_invalid_nested_enum_value_is_blocking() -> None:
    """验证 nested enum 非法值会阻断。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 未输出 enum issue 时抛出。
    """

    bundle = _valid_bundle_dict(review_status="fact_prefill_reviewed")
    bundle["source_documents"][0]["source_boundary"] = "invalid_value"

    result = validate_report_quality_bundle(bundle)

    assert _has_issue(
        result.issues,
        "RQV_ENUM_INVALID",
        "blocking",
        "/bundle/source_documents/0/source_boundary",
    )


def test_duplicate_ids_are_blocking() -> None:
    """验证重复 bundle-local id 会阻断。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 未输出重复 id issue 时抛出。
    """

    bundle = _valid_bundle_dict(review_status="fact_prefill_reviewed")
    bundle["facts"].append(dict(bundle["facts"][0]))

    result = validate_report_quality_bundle(bundle)

    assert _has_issue(result.issues, "RQV_ID_DUPLICATE", "blocking", "/bundle/facts/1/fact_id")


def test_missing_anchor_gap_fact_issue_document_refs_are_reported() -> None:
    """验证 anchor、gap、fact、issue、document 引用缺失会报告。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 缺失引用未被发现时抛出。
    """

    bundle = _valid_bundle_dict(review_status="fact_prefill_reviewed")
    bundle["facts"][0]["source_anchor_ids"] = ["anchor:missing"]
    bundle["facts"][0]["source_document_ids"] = ["doc:missing"]
    bundle["facts"][0]["data_gap_refs"] = ["gap:missing"]
    bundle["facts"][0]["score_issue_ids"] = ["issue:missing"]
    bundle["data_gaps"] = [
        _gap_dict(
            score_issue_ids=["issue:missing"],
            related_fact_id="fact:missing",
        )
    ]
    bundle["score_issue_links"] = [_issue_dict(data_gap_refs=["gap:missing"])]

    result = validate_report_quality_bundle(bundle)

    assert _count_issues(result.issues, "RQV_REF_MISSING") >= 6


def test_scoring_ready_blocks_ad_hoc_unknown_type_probe_boundary_unreviewed_facts_and_fail_closed_source() -> None:
    """验证 scoring_ready 前置条件集中输出 canonical blocking issue。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: scoring_ready 前置条件未阻断时抛出。
    """

    bundle = _valid_bundle_dict()
    bundle["corpus_id"] = "ad_hoc"
    bundle["classified_fund_type"] = "unknown"
    bundle["type_slot_membership_status"] = "unknown"
    bundle["source_documents"][0]["source_boundary"] = "probe_only"
    bundle["source_documents"][0]["source_failure_category"] = "unknown_upstream_failure_category"
    bundle["facts"][0]["review_status"] = "not_reviewed"

    result = validate_report_quality_bundle(bundle)
    scoring_issues = [issue for issue in result.issues if issue.error_code == "RQV_SCORING_READY_PRECONDITION"]

    assert len(scoring_issues) == 1
    assert scoring_issues[0].severity == "blocking"
    assert "all facts must have review_status=reviewed" in scoring_issues[0].actual
    assert result.summary.failed_closed is True


def test_fallback_flags_must_match_failure_category() -> None:
    """验证 fallback flags 与 failure category 必须一致。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: fallback 矛盾未阻断时抛出。
    """

    none_conflict = _valid_bundle_dict(review_status="fact_prefill_reviewed")
    none_conflict["source_documents"][0]["fallback_allowed"] = True
    used_conflict = _valid_bundle_dict(review_status="fact_prefill_reviewed")
    used_conflict["source_documents"][0]["fallback_used"] = True
    fail_closed = _valid_bundle_dict(review_status="fact_prefill_reviewed")
    fail_closed["source_documents"][0]["source_failure_category"] = "schema_drift"
    fail_closed["source_documents"][0]["fallback_allowed"] = True
    fail_closed["source_documents"][0]["fallback_used"] = True

    none_result = validate_report_quality_bundle(none_conflict)
    used_result = validate_report_quality_bundle(used_conflict)
    fail_closed_result = validate_report_quality_bundle(fail_closed)

    assert _has_issue(none_result.issues, "RQV_FALLBACK_CONFLICT", "blocking")
    assert _has_issue(used_result.issues, "RQV_FALLBACK_CONFLICT", "blocking")
    assert _has_issue(fail_closed_result.issues, "RQV_FAIL_CLOSED_SOURCE", "blocking")


def test_fallback_conflict_and_fail_closed_source_do_not_cascade_duplicates() -> None:
    """验证 fail-closed 与 fallback 矛盾不会对同一来源文档级联重复输出。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: fallback 或 fail-closed issue 数量不符合预期时抛出。
    """

    fail_closed = _valid_bundle_dict(review_status="fact_prefill_reviewed")
    fail_closed["source_documents"][0]["source_failure_category"] = "schema_drift"
    fail_closed["source_documents"][0]["fallback_allowed"] = True
    fail_closed["source_documents"][0]["fallback_used"] = True
    fallback_eligible = _valid_bundle_dict(review_status="fact_prefill_reviewed")
    fallback_eligible["source_documents"][0]["source_failure_category"] = "not_found"
    fallback_eligible["source_documents"][0]["fallback_allowed"] = False
    fallback_eligible["source_documents"][0]["fallback_used"] = False

    fail_closed_result = validate_report_quality_bundle(fail_closed)
    fallback_result = validate_report_quality_bundle(fallback_eligible)

    assert _count_issues(fail_closed_result.issues, "RQV_FAIL_CLOSED_SOURCE") == 1
    assert _count_issues(fail_closed_result.issues, "RQV_FALLBACK_CONFLICT") == 0
    assert _count_issues(fallback_result.issues, "RQV_FALLBACK_CONFLICT") == 1


def test_missing_extraction_mode_with_value_is_blocking() -> None:
    """验证 missing extraction_mode 不允许携带 value。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: extraction mode 矛盾未阻断时抛出。
    """

    bundle = _valid_bundle_dict(review_status="fact_prefill_reviewed")
    bundle["facts"][0]["extraction_mode"] = "missing"

    result = validate_report_quality_bundle(bundle)

    assert _has_issue(result.issues, "RQV_EXTRACTION_MODE_CONFLICT", "blocking")


def test_na_requires_reason_uses_material_for_severity_and_does_not_allow_blocking_gap() -> None:
    """验证 N/A 原因、severity 和 blocking gap 语义。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: N/A 语义未被校验时抛出。
    """

    bundle = _valid_bundle_dict(review_status="fact_prefill_reviewed")
    bundle["data_gaps"] = [
        _gap_dict(
            gap_kind="source_failure",
            failure_category="integrity_error",
            score_issue_ids=["issue:na"],
        )
    ]
    bundle["score_issue_links"] = [
        _issue_dict(
            issue_id="issue:na",
            status="N/A",
            severity="minor",
            data_gap_refs=["gap:turnover"],
            na_reason=None,
            reviewer_note=None,
        )
    ]

    result = validate_report_quality_bundle(bundle)

    assert _has_issue(result.issues, "RQV_NA_SEMANTICS", "material")
    assert _has_issue(result.issues, "RQV_NA_SEMANTICS", "blocking")


def test_chapter_summary_requires_skipped_chapter_scope_and_canonical_issue() -> None:
    """验证 chapter_summary 与 N/A 同时违反时只出 canonical chapter_summary issue。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: chapter_summary canonical issue 不符合预期时抛出。
    """

    bundle = _valid_bundle_dict(review_status="fact_prefill_reviewed")
    bundle["score_issue_links"] = [
        _issue_dict(
            issue_id="issue:chapter-summary",
            chapter_id="report_level",
            dimension="chapter_summary",
            status="N/A",
            severity="minor",
            reviewer_note=None,
            problem=None,
        )
    ]

    result = validate_report_quality_bundle(bundle)

    assert _has_issue(result.issues, "RQV_CHAPTER_SUMMARY_SEMANTICS", "blocking")
    assert not _has_issue(result.issues, "RQV_NA_SEMANTICS")


def test_chapter_summary_report_level_pointer_is_not_duplicated_for_scoring_ready() -> None:
    """验证 scoring_ready 下 chapter_summary/report_level 只输出 canonical pointer issue。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: chapter_summary pointer issue 重复时抛出。
    """

    bundle = _valid_bundle_dict()
    bundle["score_issue_links"] = [
        _issue_dict(
            issue_id="issue:chapter-summary",
            chapter_id="report_level",
            dimension="chapter_summary",
            status="skipped",
            severity=None,
            field_path=None,
            reviewer_note="章节无可评分内容",
        )
    ]

    result = validate_report_quality_bundle(bundle)
    chapter_pointer_issues = [
        issue
        for issue in result.issues
        if issue.error_code == "RQV_CHAPTER_SUMMARY_SEMANTICS"
        and issue.record_pointer == "/bundle/score_issue_links/0/chapter_id"
    ]

    assert len(chapter_pointer_issues) == 1


def test_gap_issue_fact_bidirectional_links_are_material() -> None:
    """验证 gap、issue、fact 双向链接缺失会输出 material。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 链接不完整未被报告时抛出。
    """

    bundle = _valid_bundle_dict(review_status="fact_prefill_reviewed")
    bundle["facts"][0]["value"] = None
    bundle["facts"][0]["extraction_mode"] = "missing"
    bundle["facts"][0]["source_anchor_ids"] = []
    bundle["data_gaps"] = [_gap_dict(related_fact_id="fact:basic_identity", score_issue_ids=[])]
    bundle["score_issue_links"] = [
        _issue_dict(
            issue_id="issue:gap",
            status="issue",
            severity="material",
            field_path="basic_identity",
            data_gap_refs=["gap:turnover"],
        )
    ]

    result = validate_report_quality_bundle(bundle)

    assert _has_issue(result.issues, "RQV_GAP_LINK_INCOMPLETE", "material")


def test_scoring_ready_treats_any_non_not_applicable_gap_as_blocking() -> None:
    """验证 blocking gap 语义与 report_evidence.py 保持一致。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 普通缺口未阻断 scoring_ready 时抛出。
    """

    bundle = _valid_bundle_dict()
    bundle["data_gaps"] = [
        _gap_dict(
            gap_kind="missing_fact",
            failure_category="not_disclosed",
            score_issue_ids=["issue:pass"],
        )
    ]
    bundle["score_issue_links"] = [
        _issue_dict(
            issue_id="issue:pass",
            status="pass",
            severity=None,
            field_path=None,
            problem=None,
            reviewer_note=None,
            data_gap_refs=["gap:turnover"],
        )
    ]

    result = validate_report_quality_bundle(bundle)

    assert _has_issue(result.issues, "RQV_SCORING_READY_PRECONDITION", "blocking")
    assert _has_issue(result.issues, "RQV_REF_MISSING", "blocking", "/bundle/score_issue_links/0/data_gap_refs")


def test_source_boundary_external_official_cannot_be_annual_report_only_source() -> None:
    """验证 external_official 不能作为 scoring_ready 年报唯一来源边界。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: external_official 未阻断时抛出。
    """

    bundle = _valid_bundle_dict()
    bundle["source_documents"][0]["source_boundary"] = "external_official"
    bundle["facts"][0]["source_boundary"] = "external_official"

    result = validate_report_quality_bundle(bundle)

    assert _has_issue(result.issues, "RQV_SCORING_READY_PRECONDITION", "blocking")


def test_jsonl_bad_line_returns_blocking_pointer(tmp_path) -> None:
    """验证 JSONL 坏行返回 blocking issue 且保留行 pointer。

    Args:
        tmp_path: pytest 临时目录。

    Returns:
        无返回值。

    Raises:
        AssertionError: 坏行未被定位时抛出。
    """

    jsonl_path = tmp_path / "bad.jsonl"
    jsonl_path.write_text('{"record_type": "bundle"}\n{bad json}\n', encoding="utf-8")

    result = validate_report_quality_jsonl(jsonl_path)

    assert _has_issue(result.issues, "RQV_JSONL_INVALID", "blocking", "line:2")
    assert result.summary.failed_closed is True


def test_jsonl_invalid_record_type_is_blocking(tmp_path) -> None:
    """验证 JSONL 非法 record_type 阻断。

    Args:
        tmp_path: pytest 临时目录。

    Returns:
        无返回值。

    Raises:
        AssertionError: 非法 record_type 未阻断时抛出。
    """

    jsonl_path = tmp_path / "bad-record-type.jsonl"
    jsonl_path.write_text('{"record_type": "bad"}\n', encoding="utf-8")

    result = validate_report_quality_jsonl(jsonl_path)

    assert _has_issue(result.issues, "RQV_RECORD_TYPE_INVALID", "blocking", "line:1/record_type")


def test_accepted_baseline_is_blocking() -> None:
    """验证当前 slice 不允许 accepted_baseline 输入。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: accepted_baseline 未阻断时抛出。
    """

    bundle = _valid_bundle_dict(review_status="accepted_baseline")

    result = validate_report_quality_bundle(bundle)

    assert _has_issue(result.issues, "RQV_SCORING_READY_PRECONDITION", "blocking", "/bundle/review_status")


def test_skipped_outside_chapter_summary_is_blocking() -> None:
    """验证非 chapter_summary 维度不允许 skipped。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: skipped outside chapter_summary 未阻断时抛出。
    """

    bundle = _valid_bundle_dict(review_status="fact_prefill_reviewed")
    bundle["score_issue_links"] = [
        _issue_dict(
            issue_id="issue:skipped",
            dimension="fact_coverage",
            status="skipped",
            severity=None,
            field_path=None,
        )
    ]

    result = validate_report_quality_bundle(bundle)

    assert _has_issue(result.issues, "RQV_CHAPTER_SUMMARY_SEMANTICS", "blocking")


def test_preferred_lens_chapter_required_fields_are_validated() -> None:
    """验证 preferred_lens.chapters 必填字段。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: preferred_lens 缺字段未被发现时抛出。
    """

    bundle = _valid_bundle_dict(review_status="fact_prefill_reviewed")
    del bundle["preferred_lens"]["chapters"][0]["primary_focus"]

    result = validate_report_quality_bundle(bundle)

    assert _has_issue(
        result.issues,
        "RQV_FIELD_MISSING",
        "material",
        "/bundle/preferred_lens/chapters/0/primary_focus",
    )


def test_anchor_document_id_must_exist_in_source_documents() -> None:
    """验证 anchor document_id 必须指向 source_documents。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: anchor document_id 缺失引用未被发现时抛出。
    """

    bundle = _valid_bundle_dict(review_status="fact_prefill_reviewed")
    bundle["evidence_anchors"][0]["document_id"] = "doc:missing"

    result = validate_report_quality_bundle(bundle)

    assert _has_issue(
        result.issues,
        "RQV_REF_MISSING",
        "material",
        "/bundle/evidence_anchors/0/document_id",
    )


def test_validator_does_not_import_forbidden_runtime_boundaries() -> None:
    """验证 validator 源码没有越界导入关键字。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 源码出现禁止边界关键字时抛出。
    """

    source = _validator_source()

    forbidden = (
        "Fund" + "Document" + "Repository",
        "Annual" + "Report" + "Document" + "Cache",
        "Annual" + "Report" + "Pdf" + "Adapter",
        "documents" + "." + "sources",
        "annual" + "_" + "report" + "_" + "pdf",
        "extra" + "_" + "payload",
        "dayu" + "." + "host",
        "dayu" + "." + "engine",
        "quality" + "_" + "gate",
    )
    assert all(token not in source for token in forbidden)


def test_no_navigation_projection_requirement_is_introduced() -> None:
    """验证 validator 不引入净值数据投影要求。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 源码出现净值数据投影标识时抛出。
    """

    assert "nav" + "_" + "data" not in _validator_source()


def _valid_bundle_dict(review_status: str = "scoring_ready") -> dict[str, object]:
    """构造最小合法 bundle serialization。

    Args:
        review_status: bundle review_status。

    Returns:
        fake bundle dict。
    """

    return {
        "bundle_id": "bundle:004393:2024",
        "schema_version": REPORT_EVIDENCE_SCHEMA_VERSION,
        "corpus_id": "corpus:baseline:v1",
        "fund_code": "004393",
        "report_year": 2024,
        "classified_fund_type": "active_fund",
        "type_slot_membership_status": "matches_slot",
        "fund_type_slot": "active_fund",
        "preferred_lens": {
            "fund_type": "active_fund",
            "chapters": [
                {
                    "chapter_id": f"chapter_{index}",
                    "lens_key": "active_fund",
                    "used_default": False,
                    "primary_focus": "超额收益稳定性",
                    "watch_variable_label": "换手率",
                    "risk_focus_label": "风格漂移",
                    "source_statements": [],
                }
                for index in range(8)
            ],
        },
        "quality_context": {
            "fq_gate_status": "pass",
            "fq_issue_refs": [],
            "programmatic_audit_status": "pass",
            "report_quality_score_refs": [],
            "known_residual_refs": [],
            "judgment_constraint": "cautious_only",
        },
        "review_status": review_status,
        "source_documents": [
            {
                "document_id": "doc:004393:2024:annual_report",
                "document_type": "annual_report",
                "identity_status": "verified_annual_report",
                "source_boundary": "repository_derived",
                "source_failure_category": "none",
                "fallback_allowed": False,
                "fallback_used": False,
                "review_artifact_refs": [],
            }
        ],
        "facts": [
            {
                "fact_id": "fact:basic_identity",
                "category": "identity",
                "field_path": "basic_identity",
                "value": {"fund_name": "测试基金"},
                "unit": "object",
                "source_boundary": "repository_derived",
                "extraction_mode": "direct",
                "review_status": "reviewed",
                "period": None,
                "source_anchor_ids": ["anchor:004393:2024:annual_report:sec2:abc12345"],
                "source_document_ids": ["doc:004393:2024:annual_report"],
                "failure_category": None,
                "data_gap_refs": [],
                "score_issue_ids": [],
            }
        ],
        "derived_calculations": [],
        "evidence_anchors": [
            {
                "anchor_id": "anchor:004393:2024:annual_report:sec2:abc12345",
                "source_kind": "annual_report",
                "source_strength": "fund_disclosure",
                "document_id": "doc:004393:2024:annual_report",
                "document_year": 2024,
                "section_id": "sec2",
                "page_number": 12,
                "table_id": None,
                "row_locator": "row:1",
                "review_artifact_ref": None,
                "note": "基金基本信息",
            }
        ],
        "data_gaps": [],
        "score_issue_links": [],
        "validation_messages": [],
    }


def _gap_dict(
    *,
    gap_id: str = "gap:turnover",
    gap_kind: str = "missing_fact",
    failure_category: str = "not_disclosed",
    reason_code: str = "not_disclosed",
    related_fact_id: str | None = None,
    score_issue_ids: list[str] | None = None,
) -> dict[str, object]:
    """构造 fake data gap。

    Args:
        gap_id: gap id。
        gap_kind: gap kind。
        failure_category: failure category。
        reason_code: reason code。
        related_fact_id: 关联 fact id。
        score_issue_ids: 回链 issue ids。

    Returns:
        fake gap dict。
    """

    return {
        "gap_id": gap_id,
        "gap_kind": gap_kind,
        "field_path": "turnover_rate",
        "related_fact_id": related_fact_id,
        "related_claim_id": None,
        "chapter_ids": ["chapter_3"],
        "failure_category": failure_category,
        "reason_code": reason_code,
        "fallback_allowed": False,
        "fallback_used": False,
        "required_report_wording": "数据不足，需复核该字段后再作判断",
        "blocks_claim_ids": [],
        "blocks_scoring_dimensions": ["fact_coverage"] if gap_kind == "source_failure" else [],
        "score_issue_ids": score_issue_ids or [],
    }


def _second_bundle_dict() -> dict[str, object]:
    """构造第二只基金的最小合法 bundle serialization。

    Args:
        无。

    Returns:
        第二只 fake bundle dict。
    """

    bundle = _valid_bundle_dict(review_status="fact_prefill_reviewed")
    bundle["bundle_id"] = "bundle:004194:2024"
    bundle["fund_code"] = "004194"
    bundle["classified_fund_type"] = "enhanced_index"
    bundle["fund_type_slot"] = "enhanced_index"
    bundle["preferred_lens"]["fund_type"] = "enhanced_index"  # type: ignore[index]
    bundle["source_documents"][0]["document_id"] = "doc:004194:2024:annual_report"  # type: ignore[index]
    bundle["facts"][0]["source_anchor_ids"] = [  # type: ignore[index]
        "anchor:004194:2024:annual_report:sec2:def67890"
    ]
    bundle["facts"][0]["source_document_ids"] = ["doc:004194:2024:annual_report"]  # type: ignore[index]
    bundle["evidence_anchors"][0]["anchor_id"] = (  # type: ignore[index]
        "anchor:004194:2024:annual_report:sec2:def67890"
    )
    bundle["evidence_anchors"][0]["document_id"] = "doc:004194:2024:annual_report"  # type: ignore[index]
    return bundle


def _issue_dict(
    *,
    issue_id: str = "issue:turnover",
    score_run_id: str = "score-run:test",
    chapter_id: str = "chapter_3",
    dimension: str = "fact_coverage",
    status: str = "issue",
    severity: str | None = "material",
    field_path: str | None = "turnover_rate",
    claim_id: str | None = None,
    contract_item_id: str | None = None,
    problem: str | None = "缺少换手率",
    data_gap_refs: list[str] | None = None,
    evidence_anchor_refs: list[str] | None = None,
    next_gate_recommendation: str = "data_extraction",
    na_reason: str | None = None,
    reviewer_note: str | None = "人工审阅说明",
) -> dict[str, object]:
    """构造 fake score issue。

    Args:
        issue_id: issue id。
        score_run_id: score run id。
        chapter_id: 章节 id。
        dimension: 评分维度。
        status: issue 状态。
        severity: 严重程度。
        field_path: 字段路径。
        claim_id: claim id。
        contract_item_id: contract item id。
        problem: 问题说明。
        data_gap_refs: gap refs。
        evidence_anchor_refs: anchor refs。
        next_gate_recommendation: 下一 gate 建议。
        na_reason: N/A 原因。
        reviewer_note: 审阅说明。

    Returns:
        fake issue dict。
    """

    return {
        "issue_id": issue_id,
        "score_run_id": score_run_id,
        "chapter_id": chapter_id,
        "dimension": dimension,
        "status": status,
        "next_gate_recommendation": next_gate_recommendation,
        "severity": severity,
        "field_path": field_path,
        "claim_id": claim_id,
        "contract_item_id": contract_item_id,
        "problem": problem,
        "expected": None,
        "observed_ref": None,
        "evidence_anchor_refs": evidence_anchor_refs or [],
        "data_gap_refs": data_gap_refs or [],
        "na_reason": na_reason,
        "reviewer_note": reviewer_note,
    }


def _external_score_issue(
    *,
    issue_id: str,
    status: str = "pass",
    severity: str | None = None,
    field_path: str | None = None,
    evidence_anchor_refs: list[str] | None = None,
    data_gap_refs: list[str] | None = None,
    next_gate_recommendation: str = "review_acceptance",
) -> dict[str, object]:
    """构造 JSONL 独立 score_issue record。

    Args:
        issue_id: issue id。
        status: issue 状态。
        severity: 严重程度。
        field_path: 字段路径。
        evidence_anchor_refs: anchor refs。
        data_gap_refs: gap refs。
        next_gate_recommendation: 下一 gate 建议。

    Returns:
        独立 score_issue record。
    """

    return {
        "record_type": "score_issue",
        "issue_id": issue_id,
        "score_run_id": "score-run:test",
        "chapter_id": "chapter_2",
        "dimension": "fact_coverage",
        "status": status,
        "next_gate_recommendation": next_gate_recommendation,
        "severity": severity,
        "field_path": field_path,
        "evidence_anchor_refs": evidence_anchor_refs or [],
        "data_gap_refs": data_gap_refs or [],
    }


def _write_jsonl_records(path: Path, records: tuple[dict[str, object], ...]) -> None:
    """写入测试 JSONL records。

    Args:
        path: JSONL 输出路径。
        records: 待写入 records。

    Returns:
        无返回值。
    """

    path.write_text(
        "\n".join(json.dumps(record, ensure_ascii=False) for record in records),
        encoding="utf-8",
    )


def _has_issue(
    issues: tuple[ReportQualityValidationIssue, ...],
    error_code: str,
    severity: str | None = None,
    pointer: str | None = None,
) -> bool:
    """判断 issue 列表是否包含目标 issue。

    Args:
        issues: issue 列表。
        error_code: 错误码。
        severity: 严重程度。
        pointer: record pointer。

    Returns:
        匹配时返回 True。
    """

    return any(
        issue.error_code == error_code
        and (severity is None or issue.severity == severity)
        and (pointer is None or issue.record_pointer == pointer)
        for issue in issues
    )


def _count_issues(issues: tuple[ReportQualityValidationIssue, ...], error_code: str) -> int:
    """统计指定错误码 issue 数。

    Args:
        issues: issue 列表。
        error_code: 错误码。

    Returns:
        issue 数。
    """

    return sum(1 for issue in issues if issue.error_code == error_code)


def _validator_source() -> str:
    """读取 validator 源码。

    Args:
        无。

    Returns:
        validator 源码文本。
    """

    source_path = __import__(
        "fund_agent.fund.report_quality_validation",
        fromlist=["__file__"],
    ).__file__
    assert source_path is not None
    with open(source_path, encoding="utf-8") as source_file:
        return source_file.read()
