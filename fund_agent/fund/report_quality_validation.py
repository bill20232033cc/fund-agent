"""报告质量评分 JSONL 内容校验器。

本模块属于 Agent 层 Fund 领域能力，负责校验 `ReportEvidenceBundle`
及其 JSONL 序列化内容是否满足评分前置契约。它只消费内存对象或
JSONL Mapping，不读取基金文档、不调用仓库、不改变模板第 0-7 章渲染、
不替代 FQ0-FQ6 质量门控。
"""

from __future__ import annotations

import json
from collections import Counter
from collections.abc import Mapping, Sequence
from dataclasses import asdict, dataclass, is_dataclass
from pathlib import Path
from typing import Literal, TypeAlias, get_args

from fund_agent.fund.report_evidence import (
    REPORT_EVIDENCE_SCHEMA_VERSION,
    CalculationFormulaName,
    CalculationStatus,
    ChapterRef,
    ClassifiedFundType,
    DataGapReasonCode,
    DocumentIdentityStatus,
    DocumentType,
    FQGateStatus,
    FactCategory,
    FactReviewStatus,
    FactUnit,
    GapFailureCategory,
    GapKind,
    JudgmentConstraint,
    NextGateRecommendation,
    ProgrammaticAuditStatus,
    ReportAnchorSourceKind,
    ReportEvidenceBundle,
    ReportExtractionMode,
    ReviewStatus,
    SchemaRevisionStatus,
    ScoreDimension,
    ScoreIssueSeverity,
    ScoreRecordStatus,
    SourceBoundary,
    SourceFailureCategory,
    SourceStrength,
    TypeSlotMembershipStatus,
)

ValidationSeverity = Literal["blocking", "material", "minor"]
_JsonRecord: TypeAlias = Mapping[str, object]

_BUNDLE_REQUIRED_FIELDS: tuple[str, ...] = (
    "bundle_id",
    "schema_version",
    "corpus_id",
    "fund_code",
    "report_year",
    "classified_fund_type",
    "type_slot_membership_status",
    "preferred_lens",
    "quality_context",
    "review_status",
    "source_documents",
    "facts",
    "derived_calculations",
    "evidence_anchors",
    "data_gaps",
    "score_issue_links",
    "validation_messages",
)
_SCORE_ISSUE_REQUIRED_FIELDS: tuple[str, ...] = (
    "issue_id",
    "score_run_id",
    "chapter_id",
    "dimension",
    "status",
    "next_gate_recommendation",
    "evidence_anchor_refs",
    "data_gap_refs",
)
_PREFERRED_LENS_CHAPTER_REQUIRED_FIELDS: tuple[str, ...] = (
    "chapter_id",
    "lens_key",
    "used_default",
    "primary_focus",
)
_TEMPLATE_CHAPTER_IDS: frozenset[str] = frozenset(f"chapter_{index}" for index in range(8))
_FAIL_CLOSED_SOURCE_FAILURES: frozenset[str] = frozenset(
    ("schema_drift", "identity_mismatch", "integrity_error")
)
_FALLBACK_ALLOWED_SOURCE_FAILURES: frozenset[str] = frozenset(("not_found", "unavailable"))
_SCORING_READY_STATUS = "scoring_ready"
_ACCEPTED_BASELINE_STATUS = "accepted_baseline"
_UNKNOWN_UPSTREAM_FAILURE = "unknown_upstream_failure_category"
_ANCHOR_REF_PREFIX = "anchor:"

_ENUM_FIELDS: dict[str, object] = {
    "classified_fund_type": ClassifiedFundType,
    "type_slot_membership_status": TypeSlotMembershipStatus,
    "review_status": ReviewStatus,
    "fund_type_slot": ClassifiedFundType,
    "source_documents[].document_type": DocumentType,
    "source_documents[].identity_status": DocumentIdentityStatus,
    "source_documents[].source_boundary": SourceBoundary,
    "source_documents[].source_failure_category": SourceFailureCategory,
    "evidence_anchors[].source_kind": ReportAnchorSourceKind,
    "evidence_anchors[].source_strength": SourceStrength,
    "data_gaps[].gap_kind": GapKind,
    "data_gaps[].chapter_ids[]": ChapterRef,
    "data_gaps[].failure_category": GapFailureCategory,
    "data_gaps[].reason_code": DataGapReasonCode,
    "data_gaps[].blocks_scoring_dimensions[]": ScoreDimension,
    "facts[].category": FactCategory,
    "facts[].unit": FactUnit,
    "facts[].source_boundary": SourceBoundary,
    "facts[].extraction_mode": ReportExtractionMode,
    "facts[].review_status": FactReviewStatus,
    "derived_calculations[].formula_name": CalculationFormulaName,
    "derived_calculations[].calculation_status": CalculationStatus,
    "score_issue_links[].chapter_id": ChapterRef,
    "score_issue_links[].dimension": ScoreDimension,
    "score_issue_links[].status": ScoreRecordStatus,
    "score_issue_links[].next_gate_recommendation": NextGateRecommendation,
    "score_issue_links[].severity": ScoreIssueSeverity,
    "quality_context.fq_gate_status": FQGateStatus,
    "quality_context.programmatic_audit_status": ProgrammaticAuditStatus,
    "quality_context.judgment_constraint": JudgmentConstraint,
    "schema_revision_status": SchemaRevisionStatus,
}


@dataclass(frozen=True, slots=True)
class ReportQualityValidationIssue:
    """单条 report-quality content validation issue。

    Args:
        无。

    Attributes:
        error_code: 稳定错误码。
        severity: 严重程度。
        record_pointer: 稳定 JSONL 行或 bundle 内字段定位。
        message: 中文错误说明。
        source_path: 输入来源路径。
        record_type: JSONL record_type 或 bundle。
        record_id: 记录稳定 id。
        field_name: 触发字段名。
        expected: 期望值说明。
        actual: 实际值说明。
    """

    error_code: str
    severity: ValidationSeverity
    record_pointer: str
    message: str
    source_path: str | None = None
    record_type: str | None = None
    record_id: str | None = None
    field_name: str | None = None
    expected: str | None = None
    actual: str | None = None


@dataclass(frozen=True, slots=True)
class ReportQualityValidationSummary:
    """report-quality content validation 汇总。

    Args:
        无。

    Attributes:
        total_records: 已解析记录数。
        blocking_count: blocking issue 数。
        material_count: material issue 数。
        minor_count: minor issue 数。
        error_code_counts: 按错误码汇总的稳定计数。
        scoring_ready_record_count: 声明 scoring_ready 的 bundle 数。
        failed_closed: 是否存在 blocking issue。
    """

    total_records: int
    blocking_count: int
    material_count: int
    minor_count: int
    error_code_counts: tuple[tuple[str, int], ...]
    scoring_ready_record_count: int
    failed_closed: bool


@dataclass(frozen=True, slots=True)
class ReportQualityValidationResult:
    """report-quality content validation 结果。

    Args:
        无。

    Attributes:
        source_path: 输入 JSONL 路径或调用方传入路径。
        run_id: 调用方显式 run id 或从 score issue 推断的 run id。
        schema_version: bundle schema 版本。
        issues: 校验问题列表。
        summary: 校验汇总。
    """

    source_path: str | None
    run_id: str | None
    schema_version: str | None
    issues: tuple[ReportQualityValidationIssue, ...]
    summary: ReportQualityValidationSummary


@dataclass(frozen=True, slots=True)
class _ValidationContext:
    """单次校验的上下文。

    Args:
        无。

    Attributes:
        source_path: 输入来源路径。
        run_id: 显式 run id。
        line_prefix: JSONL 行定位前缀。
        record_type: 当前记录类型。
    """

    source_path: str | None = None
    run_id: str | None = None
    line_prefix: str | None = None
    record_type: str = "bundle"


@dataclass(frozen=True, slots=True)
class _BundleIndexes:
    """bundle-local id 索引。

    Args:
        无。

    Attributes:
        anchor_ids: 证据锚点 id。
        gap_ids: 数据缺口 id。
        fact_ids: 事实 id。
        issue_ids: 评分 issue id。
        document_ids: 来源文档 id。
        calculation_ids: 派生计算 id。
        blocking_gap_ids: 阻断性数据缺口 id。
        facts_by_field_path: 按 field_path 索引的事实。
        gaps_by_id: 按 gap_id 索引的数据缺口。
        issues_by_id: 按 issue_id 索引的评分 issue。
    """

    anchor_ids: frozenset[str]
    gap_ids: frozenset[str]
    fact_ids: frozenset[str]
    issue_ids: frozenset[str]
    document_ids: frozenset[str]
    calculation_ids: frozenset[str]
    blocking_gap_ids: frozenset[str]
    facts_by_field_path: Mapping[str, _JsonRecord]
    gaps_by_id: Mapping[str, _JsonRecord]
    issues_by_id: Mapping[str, _JsonRecord]


@dataclass(slots=True)
class _ScoreIssueRecordGroup:
    """JSONL 中一个 bundle 及其后续独立 score_issue records。

    Args:
        无。

    Attributes:
        bundle: 所属 bundle record。
        score_issue_records: 归属于该 bundle 的独立 score_issue 行号与 record。
    """

    bundle: _JsonRecord
    score_issue_records: list[tuple[int, _JsonRecord]]


def validate_report_quality_bundle(
    bundle: ReportEvidenceBundle | Mapping[str, object],
    *,
    source_path: str | None = None,
    run_id: str | None = None,
) -> ReportQualityValidationResult:
    """校验单个 `ReportEvidenceBundle` 或其 Mapping 序列化。

    Args:
        bundle: typed bundle 或 JSON-like Mapping。
        source_path: 调用方传入的来源路径。
        run_id: 调用方显式评分运行标识。

    Returns:
        结构化校验结果；业务校验失败通过 issues 表达。

    Raises:
        TypeError: 输入既不是 dataclass bundle，也不是 Mapping 时抛出。
    """

    bundle_record = _normalize_record(bundle)
    context = _ValidationContext(source_path=source_path, run_id=run_id)
    issues = _validate_bundle_record(bundle_record, context)
    schema_version = _string_or_none(bundle_record.get("schema_version"))
    inferred_run_id = _resolve_run_id(run_id, (bundle_record,), issues, context)
    summary = _build_summary(
        issues=issues,
        total_records=1,
        scoring_ready_record_count=_scoring_ready_count((bundle_record,)),
    )
    return ReportQualityValidationResult(
        source_path=source_path,
        run_id=inferred_run_id,
        schema_version=schema_version,
        issues=tuple(issues),
        summary=summary,
    )


def validate_report_quality_jsonl(
    jsonl_path: Path,
    *,
    run_id: str | None = None,
) -> ReportQualityValidationResult:
    """校验 report-quality JSONL artifact。

    Args:
        jsonl_path: JSONL 文件路径。
        run_id: 调用方显式评分运行标识。

    Returns:
        结构化校验结果。坏行会转为 `RQV_JSONL_INVALID` blocking issue。

    Raises:
        FileNotFoundError: JSONL 文件不存在时抛出。
    """

    source_path = str(jsonl_path)
    records: list[tuple[int, str, _JsonRecord]] = []
    issues: list[ReportQualityValidationIssue] = []

    with jsonl_path.open("r", encoding="utf-8") as file_obj:
        for line_number, raw_line in enumerate(file_obj, start=1):
            stripped = raw_line.strip()
            if not stripped:
                continue
            try:
                parsed = json.loads(stripped)
            except json.JSONDecodeError as exc:
                issues.append(
                    _make_issue(
                        error_code="RQV_JSONL_INVALID",
                        severity="blocking",
                        pointer=f"line:{line_number}",
                        message="JSONL 行无法解析为 JSON object。",
                        context=_ValidationContext(source_path=source_path),
                        field_name="json",
                        expected="valid JSON object",
                        actual=exc.msg,
                    )
                )
                continue
            if not isinstance(parsed, Mapping):
                issues.append(
                    _make_issue(
                        error_code="RQV_JSONL_INVALID",
                        severity="blocking",
                        pointer=f"line:{line_number}",
                        message="JSONL 行必须是 JSON object。",
                        context=_ValidationContext(source_path=source_path),
                        field_name="record",
                        expected="object",
                        actual=type(parsed).__name__,
                    )
                )
                continue
            record_type = parsed.get("record_type")
            if record_type not in {"bundle", "score_issue"}:
                issues.append(
                    _make_issue(
                        error_code="RQV_RECORD_TYPE_INVALID",
                        severity="blocking",
                        pointer=f"line:{line_number}/record_type",
                        message="JSONL record_type 缺失或非法。",
                        context=_ValidationContext(source_path=source_path),
                        record_type=_string_or_none(record_type),
                        field_name="record_type",
                        expected="bundle or score_issue",
                        actual=_actual(record_type),
                    )
                )
                continue
            records.append((line_number, str(record_type), parsed))

    bundle_records = [(line, record) for line, record_type, record in records if record_type == "bundle"]
    score_issue_record_groups: list[_ScoreIssueRecordGroup] = []
    current_group: _ScoreIssueRecordGroup | None = None
    for line_number, record_type, record in records:
        if record_type == "bundle":
            current_group = _ScoreIssueRecordGroup(bundle=record, score_issue_records=[])
            score_issue_record_groups.append(current_group)
            continue
        if current_group is None:
            issues.append(
                _make_issue(
                    error_code="RQV_SCORE_ISSUE_ORPHANED",
                    severity="blocking",
                    pointer=f"line:{line_number}",
                    message="score_issue record 需要出现在所属 bundle record 之后。",
                    context=_ValidationContext(
                        source_path=source_path,
                        line_prefix=f"line:{line_number}",
                        record_type="score_issue",
                    ),
                    record_type="score_issue",
                    record_id=_string_or_none(record.get("issue_id")),
                    expected="bundle record",
                    actual="no preceding bundle",
                )
            )
            continue
        current_group.score_issue_records.append((line_number, record))

    for line_number, bundle_record in bundle_records:
        context = _ValidationContext(
            source_path=source_path,
            run_id=run_id,
            line_prefix=f"line:{line_number}",
            record_type="bundle",
        )
        issues.extend(_validate_bundle_record(bundle_record, context))

    for score_issue_record_group in score_issue_record_groups:
        if score_issue_record_group.score_issue_records:
            issues.extend(
                _validate_score_issue_records_against_bundle(
                    score_issue_record_group.bundle,
                    tuple(score_issue_record_group.score_issue_records),
                    _ValidationContext(source_path=source_path, run_id=run_id),
                )
            )

    all_record_mappings = tuple(record for _, _, record in records)
    schema_version = _first_schema_version(tuple(record for _, record in bundle_records))
    inferred_run_id = _resolve_run_id(run_id, all_record_mappings, issues, _ValidationContext(source_path))
    summary = _build_summary(
        issues=issues,
        total_records=len(records),
        scoring_ready_record_count=_scoring_ready_count(tuple(record for _, record in bundle_records)),
    )
    return ReportQualityValidationResult(
        source_path=source_path,
        run_id=inferred_run_id,
        schema_version=schema_version,
        issues=tuple(issues),
        summary=summary,
    )


def _validate_bundle_record(
    bundle: _JsonRecord,
    context: _ValidationContext,
) -> list[ReportQualityValidationIssue]:
    """执行单个 bundle record 的全部内容校验。

    Args:
        bundle: JSON-like bundle record。
        context: 校验上下文。

    Returns:
        校验 issue 列表。
    """

    issues: list[ReportQualityValidationIssue] = []
    pointer = _pointer(context, "bundle")
    scoring_ready = bundle.get("review_status") == _SCORING_READY_STATUS

    _validate_required_fields(bundle, _BUNDLE_REQUIRED_FIELDS, pointer, context, issues)
    _validate_schema_version(bundle, pointer, context, issues)
    _validate_bundle_enum_domains(bundle, pointer, context, issues)

    source_documents = _list_of_mappings(bundle.get("source_documents"))
    facts = _list_of_mappings(bundle.get("facts"))
    anchors = _list_of_mappings(bundle.get("evidence_anchors"))
    gaps = _list_of_mappings(bundle.get("data_gaps"))
    issues_records = _list_of_mappings(bundle.get("score_issue_links"))
    calculations = _list_of_mappings(bundle.get("derived_calculations"))
    indexes = _build_indexes(bundle, pointer, context, issues)

    _validate_preferred_lens(bundle, pointer, context, issues, scoring_ready)
    _validate_source_documents(source_documents, pointer, context, issues)
    _validate_facts(facts, indexes, pointer, context, issues, scoring_ready)
    _validate_evidence_anchors(anchors, indexes, pointer, context, issues, scoring_ready)
    _validate_data_gaps(gaps, indexes, pointer, context, issues)
    _validate_score_issue_links(issues_records, indexes, pointer, context, issues, scoring_ready)
    _validate_calculations(calculations, indexes, pointer, context, issues)
    _validate_link_completeness(facts, gaps, issues_records, indexes, pointer, context, issues, scoring_ready)
    _validate_scoring_ready_preconditions(
        bundle=bundle,
        source_documents=source_documents,
        facts=facts,
        gaps=gaps,
        score_issues=issues_records,
        indexes=indexes,
        pointer=pointer,
        context=context,
        issues=issues,
    )
    return issues


def _validate_score_issue_records_against_bundle(
    bundle: _JsonRecord,
    score_issue_records: tuple[tuple[int, _JsonRecord], ...],
    context: _ValidationContext,
) -> list[ReportQualityValidationIssue]:
    """校验 JSONL 单行 score_issue 与同 artifact bundle 的引用关系。

    Args:
        bundle: 同 JSONL artifact 的主 bundle。
        score_issue_records: 行号与 score_issue records。
        context: 校验上下文。

    Returns:
        校验 issue 列表。
    """

    issues: list[ReportQualityValidationIssue] = []
    indexes = _build_indexes(bundle, "/bundle", context, issues)
    for line_number, issue_record in score_issue_records:
        line_context = _ValidationContext(
            source_path=context.source_path,
            run_id=context.run_id,
            line_prefix=f"line:{line_number}",
            record_type="score_issue",
        )
        pointer = f"line:{line_number}/score_issue"
        _validate_required_fields(
            issue_record, _SCORE_ISSUE_REQUIRED_FIELDS, pointer, line_context, issues
        )
        _validate_score_issue_enum_domains(issue_record, pointer, line_context, issues)
        _validate_single_score_issue(issue_record, indexes, pointer, line_context, issues, False)
    return issues


def _validate_required_fields(
    record: _JsonRecord,
    required_fields: Sequence[str],
    pointer: str,
    context: _ValidationContext,
    issues: list[ReportQualityValidationIssue],
) -> None:
    """校验必填字段存在。

    Args:
        record: 待校验记录。
        required_fields: 必填字段名。
        pointer: 当前记录 pointer。
        context: 校验上下文。
        issues: issue accumulator。

    Returns:
        无返回值。
    """

    for field_name in required_fields:
        if field_name not in record:
            issues.append(
                _make_issue(
                    error_code="RQV_FIELD_MISSING",
                    severity="blocking",
                    pointer=f"{pointer}/{field_name}",
                    message="缺少必填字段。",
                    context=context,
                    record_id=_record_id(record),
                    field_name=field_name,
                    expected="present",
                    actual="missing",
                )
            )


def _validate_schema_version(
    bundle: _JsonRecord,
    pointer: str,
    context: _ValidationContext,
    issues: list[ReportQualityValidationIssue],
) -> None:
    """校验 bundle schema 版本。

    Args:
        bundle: bundle record。
        pointer: bundle pointer。
        context: 校验上下文。
        issues: issue accumulator。

    Returns:
        无返回值。
    """

    schema_version = bundle.get("schema_version")
    if schema_version != REPORT_EVIDENCE_SCHEMA_VERSION:
        issues.append(
            _make_issue(
                error_code="RQV_FIELD_MISSING",
                severity="blocking",
                pointer=f"{pointer}/schema_version",
                message="schema_version 缺失或不等于当前 ReportEvidenceBundle schema。",
                context=context,
                record_id=_record_id(bundle),
                field_name="schema_version",
                expected=REPORT_EVIDENCE_SCHEMA_VERSION,
                actual=_actual(schema_version),
            )
        )


def _validate_bundle_enum_domains(
    bundle: _JsonRecord,
    pointer: str,
    context: _ValidationContext,
    issues: list[ReportQualityValidationIssue],
) -> None:
    """校验 bundle 及嵌套记录的 Literal domain。

    Args:
        bundle: bundle record。
        pointer: bundle pointer。
        context: 校验上下文。
        issues: issue accumulator。

    Returns:
        无返回值。
    """

    _validate_enum(bundle, "classified_fund_type", "classified_fund_type", pointer, context, issues)
    _validate_enum(
        bundle,
        "type_slot_membership_status",
        "type_slot_membership_status",
        pointer,
        context,
        issues,
    )
    _validate_enum(bundle, "review_status", "review_status", pointer, context, issues)
    if bundle.get("fund_type_slot") is not None:
        _validate_enum(bundle, "fund_type_slot", "fund_type_slot", pointer, context, issues)

    quality_context = _mapping_or_empty(bundle.get("quality_context"))
    _validate_enum(
        quality_context,
        "fq_gate_status",
        "quality_context.fq_gate_status",
        f"{pointer}/quality_context",
        context,
        issues,
    )
    _validate_enum(
        quality_context,
        "programmatic_audit_status",
        "quality_context.programmatic_audit_status",
        f"{pointer}/quality_context",
        context,
        issues,
    )
    _validate_enum(
        quality_context,
        "judgment_constraint",
        "quality_context.judgment_constraint",
        f"{pointer}/quality_context",
        context,
        issues,
    )

    for index, document in enumerate(_list_of_mappings(bundle.get("source_documents"))):
        item_pointer = f"{pointer}/source_documents/{index}"
        _validate_enum(document, "document_type", "source_documents[].document_type", item_pointer, context, issues)
        _validate_enum(
            document,
            "identity_status",
            "source_documents[].identity_status",
            item_pointer,
            context,
            issues,
        )
        _validate_enum(
            document,
            "source_boundary",
            "source_documents[].source_boundary",
            item_pointer,
            context,
            issues,
        )
        _validate_enum(
            document,
            "source_failure_category",
            "source_documents[].source_failure_category",
            item_pointer,
            context,
            issues,
        )

    for index, anchor in enumerate(_list_of_mappings(bundle.get("evidence_anchors"))):
        item_pointer = f"{pointer}/evidence_anchors/{index}"
        _validate_enum(anchor, "source_kind", "evidence_anchors[].source_kind", item_pointer, context, issues)
        _validate_enum(
            anchor,
            "source_strength",
            "evidence_anchors[].source_strength",
            item_pointer,
            context,
            issues,
        )

    for index, gap in enumerate(_list_of_mappings(bundle.get("data_gaps"))):
        item_pointer = f"{pointer}/data_gaps/{index}"
        _validate_enum(gap, "gap_kind", "data_gaps[].gap_kind", item_pointer, context, issues)
        _validate_enum(gap, "failure_category", "data_gaps[].failure_category", item_pointer, context, issues)
        _validate_enum(gap, "reason_code", "data_gaps[].reason_code", item_pointer, context, issues)
        _validate_enum_sequence(
            gap,
            "chapter_ids",
            "data_gaps[].chapter_ids[]",
            f"{item_pointer}/chapter_ids",
            context,
            issues,
        )
        _validate_enum_sequence(
            gap,
            "blocks_scoring_dimensions",
            "data_gaps[].blocks_scoring_dimensions[]",
            f"{item_pointer}/blocks_scoring_dimensions",
            context,
            issues,
        )

    for index, fact in enumerate(_list_of_mappings(bundle.get("facts"))):
        item_pointer = f"{pointer}/facts/{index}"
        _validate_enum(fact, "category", "facts[].category", item_pointer, context, issues)
        _validate_enum(fact, "unit", "facts[].unit", item_pointer, context, issues)
        _validate_enum(fact, "source_boundary", "facts[].source_boundary", item_pointer, context, issues)
        _validate_enum(fact, "extraction_mode", "facts[].extraction_mode", item_pointer, context, issues)
        _validate_enum(fact, "review_status", "facts[].review_status", item_pointer, context, issues)

    for index, calculation in enumerate(_list_of_mappings(bundle.get("derived_calculations"))):
        item_pointer = f"{pointer}/derived_calculations/{index}"
        _validate_enum(
            calculation,
            "formula_name",
            "derived_calculations[].formula_name",
            item_pointer,
            context,
            issues,
        )
        _validate_enum(
            calculation,
            "calculation_status",
            "derived_calculations[].calculation_status",
            item_pointer,
            context,
            issues,
        )

    for index, score_issue in enumerate(_list_of_mappings(bundle.get("score_issue_links"))):
        _validate_score_issue_enum_domains(
            score_issue,
            f"{pointer}/score_issue_links/{index}",
            context,
            issues,
        )


def _validate_score_issue_enum_domains(
    score_issue: _JsonRecord,
    pointer: str,
    context: _ValidationContext,
    issues: list[ReportQualityValidationIssue],
) -> None:
    """校验单条 score issue 的 Literal domain。

    Args:
        score_issue: score issue record。
        pointer: issue pointer。
        context: 校验上下文。
        issues: issue accumulator。

    Returns:
        无返回值。
    """

    _validate_enum(score_issue, "chapter_id", "score_issue_links[].chapter_id", pointer, context, issues)
    _validate_enum(score_issue, "dimension", "score_issue_links[].dimension", pointer, context, issues)
    _validate_enum(score_issue, "status", "score_issue_links[].status", pointer, context, issues)
    _validate_enum(
        score_issue,
        "next_gate_recommendation",
        "score_issue_links[].next_gate_recommendation",
        pointer,
        context,
        issues,
    )
    if score_issue.get("severity") is not None:
        _validate_enum(score_issue, "severity", "score_issue_links[].severity", pointer, context, issues)


def _validate_enum(
    record: _JsonRecord,
    field_name: str,
    enum_key: str,
    pointer: str,
    context: _ValidationContext,
    issues: list[ReportQualityValidationIssue],
) -> None:
    """校验单个枚举字段。

    Args:
        record: 待校验记录。
        field_name: 字段名。
        enum_key: `_ENUM_FIELDS` 中的枚举键。
        pointer: 当前记录 pointer。
        context: 校验上下文。
        issues: issue accumulator。

    Returns:
        无返回值。
    """

    if field_name not in record or record.get(field_name) is None:
        return
    allowed = _enum_values(enum_key)
    value = record.get(field_name)
    if value not in allowed:
        issues.append(
            _make_issue(
                error_code="RQV_ENUM_INVALID",
                severity="blocking",
                pointer=f"{pointer}/{field_name}",
                message="字段值不在 report_evidence.py Literal domain 中。",
                context=context,
                record_id=_record_id(record),
                field_name=field_name,
                expected=", ".join(allowed),
                actual=_actual(value),
            )
        )


def _validate_enum_sequence(
    record: _JsonRecord,
    field_name: str,
    enum_key: str,
    pointer: str,
    context: _ValidationContext,
    issues: list[ReportQualityValidationIssue],
) -> None:
    """校验枚举数组字段。

    Args:
        record: 待校验记录。
        field_name: 字段名。
        enum_key: `_ENUM_FIELDS` 中的枚举键。
        pointer: 数组 pointer。
        context: 校验上下文。
        issues: issue accumulator。

    Returns:
        无返回值。
    """

    values = _list(record.get(field_name))
    allowed = _enum_values(enum_key)
    for index, value in enumerate(values):
        if value not in allowed:
            issues.append(
                _make_issue(
                    error_code="RQV_ENUM_INVALID",
                    severity="blocking",
                    pointer=f"{pointer}/{index}",
                    message="数组字段值不在 report_evidence.py Literal domain 中。",
                    context=context,
                    record_id=_record_id(record),
                    field_name=field_name,
                    expected=", ".join(allowed),
                    actual=_actual(value),
                )
            )


def _build_indexes(
    bundle: _JsonRecord,
    pointer: str,
    context: _ValidationContext,
    issues: list[ReportQualityValidationIssue],
) -> _BundleIndexes:
    """构建 bundle-local id 索引并校验重复 id。

    Args:
        bundle: bundle record。
        pointer: bundle pointer。
        context: 校验上下文。
        issues: issue accumulator。

    Returns:
        bundle-local id 索引。
    """

    anchors = _list_of_mappings(bundle.get("evidence_anchors"))
    gaps = _list_of_mappings(bundle.get("data_gaps"))
    facts = _list_of_mappings(bundle.get("facts"))
    score_issues = _list_of_mappings(bundle.get("score_issue_links"))
    documents = _list_of_mappings(bundle.get("source_documents"))
    calculations = _list_of_mappings(bundle.get("derived_calculations"))

    anchor_ids = _index_ids(anchors, "anchor_id", f"{pointer}/evidence_anchors", context, issues)
    gap_ids = _index_ids(gaps, "gap_id", f"{pointer}/data_gaps", context, issues)
    fact_ids = _index_ids(facts, "fact_id", f"{pointer}/facts", context, issues)
    issue_ids = _index_ids(
        score_issues, "issue_id", f"{pointer}/score_issue_links", context, issues
    )
    document_ids = _index_ids(
        documents, "document_id", f"{pointer}/source_documents", context, issues
    )
    calculation_ids = _index_ids(
        calculations, "calculation_id", f"{pointer}/derived_calculations", context, issues
    )
    facts_by_field_path = {
        str(fact.get("field_path")): fact
        for fact in facts
        if _non_empty_string(fact.get("field_path"))
    }
    gaps_by_id = {str(gap.get("gap_id")): gap for gap in gaps if _non_empty_string(gap.get("gap_id"))}
    issues_by_id = {
        str(issue.get("issue_id")): issue
        for issue in score_issues
        if _non_empty_string(issue.get("issue_id"))
    }
    blocking_gap_ids = frozenset(
        str(gap.get("gap_id"))
        for gap in gaps
        if _non_empty_string(gap.get("gap_id")) and _is_blocking_gap(gap)
    )
    return _BundleIndexes(
        anchor_ids=frozenset(anchor_ids),
        gap_ids=frozenset(gap_ids),
        fact_ids=frozenset(fact_ids),
        issue_ids=frozenset(issue_ids),
        document_ids=frozenset(document_ids),
        calculation_ids=frozenset(calculation_ids),
        blocking_gap_ids=blocking_gap_ids,
        facts_by_field_path=facts_by_field_path,
        gaps_by_id=gaps_by_id,
        issues_by_id=issues_by_id,
    )


def _index_ids(
    records: Sequence[_JsonRecord],
    id_field: str,
    pointer: str,
    context: _ValidationContext,
    issues: list[ReportQualityValidationIssue],
) -> set[str]:
    """索引 id 并输出重复 id issue。

    Args:
        records: 待索引记录。
        id_field: id 字段名。
        pointer: 数组 pointer。
        context: 校验上下文。
        issues: issue accumulator。

    Returns:
        id 集合。
    """

    seen: set[str] = set()
    duplicates: set[str] = set()
    for index, record in enumerate(records):
        value = record.get(id_field)
        if not _non_empty_string(value):
            continue
        value_text = str(value)
        if value_text in seen:
            duplicates.add(value_text)
            issues.append(
                _make_issue(
                    error_code="RQV_ID_DUPLICATE",
                    severity="blocking",
                    pointer=f"{pointer}/{index}/{id_field}",
                    message="bundle-local id 重复，会破坏复盘和跨 run diff。",
                    context=context,
                    record_id=value_text,
                    field_name=id_field,
                    expected="unique id",
                    actual=value_text,
                )
            )
        seen.add(value_text)
    return seen - duplicates


def _validate_preferred_lens(
    bundle: _JsonRecord,
    pointer: str,
    context: _ValidationContext,
    issues: list[ReportQualityValidationIssue],
    scoring_ready: bool,
) -> None:
    """校验 preferred_lens 章节字段与 scoring_ready 覆盖。

    Args:
        bundle: bundle record。
        pointer: bundle pointer。
        context: 校验上下文。
        issues: issue accumulator。
        scoring_ready: bundle 是否声明 scoring_ready。

    Returns:
        无返回值。
    """

    preferred_lens = _mapping_or_empty(bundle.get("preferred_lens"))
    chapters = _list_of_mappings(preferred_lens.get("chapters"))
    for index, chapter in enumerate(chapters):
        chapter_pointer = f"{pointer}/preferred_lens/chapters/{index}"
        severity: ValidationSeverity = "blocking" if scoring_ready else "material"
        if not scoring_ready:
            for field_name in _PREFERRED_LENS_CHAPTER_REQUIRED_FIELDS:
                if field_name not in chapter:
                    issues.append(
                        _make_issue(
                            error_code="RQV_FIELD_MISSING",
                            severity=severity,
                            pointer=f"{chapter_pointer}/{field_name}",
                            message="preferred_lens.chapters 缺少必填字段。",
                            context=context,
                            record_id=_record_id(chapter),
                            field_name=field_name,
                            expected="present",
                            actual="missing",
                        )
                    )
        else:
            _validate_required_fields(
                chapter,
                _PREFERRED_LENS_CHAPTER_REQUIRED_FIELDS,
                chapter_pointer,
                context,
                issues,
            )


def _validate_source_documents(
    documents: Sequence[_JsonRecord],
    pointer: str,
    context: _ValidationContext,
    issues: list[ReportQualityValidationIssue],
) -> None:
    """校验来源文档 fail-closed 与 fallback consistency。

    Args:
        documents: 来源文档 records。
        pointer: bundle pointer。
        context: 校验上下文。
        issues: issue accumulator。

    Returns:
        无返回值。
    """

    for index, document in enumerate(documents):
        document_pointer = f"{pointer}/source_documents/{index}"
        failure_category = document.get("source_failure_category")
        fallback_allowed = document.get("fallback_allowed")
        fallback_used = document.get("fallback_used")
        expected_fallback_allowed = failure_category in _FALLBACK_ALLOWED_SOURCE_FAILURES

        if failure_category in _FAIL_CLOSED_SOURCE_FAILURES:
            issues.append(
                _make_issue(
                    error_code="RQV_FAIL_CLOSED_SOURCE",
                    severity="blocking",
                    pointer=f"{document_pointer}/source_failure_category",
                    message="来源失败分类必须 fail-closed，不能进入评分消费或被 fallback 掩盖。",
                    context=context,
                    record_id=_record_id(document),
                    field_name="source_failure_category",
                    expected="none, not_found, unavailable",
                    actual=_actual(failure_category),
                )
            )
            continue

        conflict_reasons: list[str] = []
        if fallback_allowed is not expected_fallback_allowed:
            conflict_reasons.append(
                f"fallback_allowed must be {expected_fallback_allowed} for {failure_category}"
            )

        if fallback_used is True and fallback_allowed is not True:
            conflict_reasons.append("fallback_used=True requires fallback_allowed=True")

        if (
            failure_category in _FALLBACK_ALLOWED_SOURCE_FAILURES
            and fallback_allowed is True
            and fallback_used is not True
        ):
            conflict_reasons.append(
                "fallback-eligible upstream failure must record fallback_used=True"
            )

        if conflict_reasons:
            issues.append(
                _make_issue(
                    error_code="RQV_FALLBACK_CONFLICT",
                    severity="blocking",
                    pointer=f"{document_pointer}/fallback_allowed",
                    message="fallback flags 必须与 source_failure_category 保持一致。",
                    context=context,
                    record_id=_record_id(document),
                    field_name="fallback_allowed",
                    expected="; ".join(conflict_reasons),
                    actual=(
                        f"failure_category={failure_category}, "
                        f"fallback_allowed={fallback_allowed}, fallback_used={fallback_used}"
                    ),
                )
            )
            continue

        if failure_category == _UNKNOWN_UPSTREAM_FAILURE:
            issues.append(
                _make_issue(
                    error_code="RQV_FALLBACK_CONFLICT",
                    severity="material",
                    pointer=f"{document_pointer}/source_failure_category",
                    message="未知上游失败分类至少需要人工恢复，不得作为 durable baseline 输入。",
                    context=context,
                    record_id=_record_id(document),
                    field_name="source_failure_category",
                    expected="explicit failure category",
                    actual=_UNKNOWN_UPSTREAM_FAILURE,
                )
            )


def _validate_facts(
    facts: Sequence[_JsonRecord],
    indexes: _BundleIndexes,
    pointer: str,
    context: _ValidationContext,
    issues: list[ReportQualityValidationIssue],
    scoring_ready: bool,
) -> None:
    """校验事实记录字段、组合和引用。

    Args:
        facts: fact records。
        indexes: bundle id 索引。
        pointer: bundle pointer。
        context: 校验上下文。
        issues: issue accumulator。
        scoring_ready: bundle 是否声明 scoring_ready。

    Returns:
        无返回值。
    """

    for index, fact in enumerate(facts):
        fact_pointer = f"{pointer}/facts/{index}"
        extraction_mode = fact.get("extraction_mode")
        value = fact.get("value")
        source_boundary = fact.get("source_boundary")
        source_anchor_ids = _list(fact.get("source_anchor_ids"))
        data_gap_refs = _list(fact.get("data_gap_refs"))

        if extraction_mode == "missing" and value is not None:
            issues.append(
                _make_issue(
                    error_code="RQV_EXTRACTION_MODE_CONFLICT",
                    severity="blocking",
                    pointer=f"{fact_pointer}/value",
                    message="extraction_mode=missing 时 value 必须为空。",
                    context=context,
                    record_id=_record_id(fact),
                    field_name="value",
                    expected="None",
                    actual=_actual(value),
                )
            )

        if value is None or extraction_mode in {"missing", "estimated"}:
            if fact.get("failure_category") is None and not data_gap_refs:
                issues.append(
                    _make_issue(
                        error_code="RQV_FIELD_MISSING",
                        severity="material",
                        pointer=f"{fact_pointer}/failure_category",
                        message="缺失、估算或空值事实必须说明 failure_category 或 data_gap_refs。",
                        context=context,
                        record_id=_record_id(fact),
                        field_name="failure_category",
                        expected="failure_category or data_gap_refs",
                        actual="missing",
                    )
                )

        if extraction_mode in {"direct", "derived", "manual_reviewed"} and value is not None:
            if not source_anchor_ids and source_boundary != "manual_review":
                severity: ValidationSeverity = "blocking" if scoring_ready else "material"
                issues.append(
                    _make_issue(
                        error_code="RQV_TRACEABILITY_GAP",
                        severity=severity,
                        pointer=f"{fact_pointer}/source_anchor_ids",
                        message="有值事实必须有证据锚点，或显式使用 manual_review 来源边界。",
                        context=context,
                        record_id=_record_id(fact),
                        field_name="source_anchor_ids",
                        expected="anchor ids or source_boundary=manual_review",
                        actual="empty",
                    )
                )

        for ref_index, anchor_id in enumerate(source_anchor_ids):
            _validate_ref(
                anchor_id,
                indexes.anchor_ids,
                f"{fact_pointer}/source_anchor_ids/{ref_index}",
                "anchor_id",
                context,
                issues,
            )
        for ref_index, document_id in enumerate(_list(fact.get("source_document_ids"))):
            _validate_ref(
                document_id,
                indexes.document_ids,
                f"{fact_pointer}/source_document_ids/{ref_index}",
                "document_id",
                context,
                issues,
            )
        for ref_index, gap_id in enumerate(data_gap_refs):
            _validate_ref(
                gap_id,
                indexes.gap_ids,
                f"{fact_pointer}/data_gap_refs/{ref_index}",
                "gap_id",
                context,
                issues,
            )
        for ref_index, issue_id in enumerate(_list(fact.get("score_issue_ids"))):
            _validate_ref(
                issue_id,
                indexes.issue_ids,
                f"{fact_pointer}/score_issue_ids/{ref_index}",
                "issue_id",
                context,
                issues,
            )


def _validate_evidence_anchors(
    anchors: Sequence[_JsonRecord],
    indexes: _BundleIndexes,
    pointer: str,
    context: _ValidationContext,
    issues: list[ReportQualityValidationIssue],
    scoring_ready: bool,
) -> None:
    """校验证据锚点 document_id 引用。

    Args:
        anchors: anchor records。
        indexes: bundle id 索引。
        pointer: bundle pointer。
        context: 校验上下文。
        issues: issue accumulator。
        scoring_ready: bundle 是否声明 scoring_ready。

    Returns:
        无返回值。
    """

    for index, anchor in enumerate(anchors):
        document_id = anchor.get("document_id")
        if document_id is None:
            continue
        if document_id not in indexes.document_ids:
            severity: ValidationSeverity = "blocking" if scoring_ready else "material"
            issues.append(
                _make_issue(
                    error_code="RQV_REF_MISSING",
                    severity=severity,
                    pointer=f"{pointer}/evidence_anchors/{index}/document_id",
                    message="evidence anchor 的 document_id 必须指向 source_documents。",
                    context=context,
                    record_id=_record_id(anchor),
                    field_name="document_id",
                    expected="existing document_id",
                    actual=_actual(document_id),
                )
            )


def _validate_data_gaps(
    gaps: Sequence[_JsonRecord],
    indexes: _BundleIndexes,
    pointer: str,
    context: _ValidationContext,
    issues: list[ReportQualityValidationIssue],
) -> None:
    """校验 data gap 引用。

    Args:
        gaps: data gap records。
        indexes: bundle id 索引。
        pointer: bundle pointer。
        context: 校验上下文。
        issues: issue accumulator。

    Returns:
        无返回值。
    """

    for index, gap in enumerate(gaps):
        gap_pointer = f"{pointer}/data_gaps/{index}"
        related_fact_id = gap.get("related_fact_id")
        if related_fact_id is not None:
            _validate_ref(
                related_fact_id,
                indexes.fact_ids,
                f"{gap_pointer}/related_fact_id",
                "fact_id",
                context,
                issues,
            )
        for ref_index, issue_id in enumerate(_list(gap.get("score_issue_ids"))):
            _validate_ref(
                issue_id,
                indexes.issue_ids,
                f"{gap_pointer}/score_issue_ids/{ref_index}",
                "issue_id",
                context,
                issues,
            )


def _validate_score_issue_links(
    score_issues: Sequence[_JsonRecord],
    indexes: _BundleIndexes,
    pointer: str,
    context: _ValidationContext,
    issues: list[ReportQualityValidationIssue],
    scoring_ready: bool,
) -> None:
    """校验 bundle 内 score issue 记录。

    Args:
        score_issues: score issue records。
        indexes: bundle id 索引。
        pointer: bundle pointer。
        context: 校验上下文。
        issues: issue accumulator。
        scoring_ready: bundle 是否声明 scoring_ready。

    Returns:
        无返回值。
    """

    for index, score_issue in enumerate(score_issues):
        issue_pointer = f"{pointer}/score_issue_links/{index}"
        _validate_required_fields(
            score_issue, _SCORE_ISSUE_REQUIRED_FIELDS, issue_pointer, context, issues
        )
        _validate_single_score_issue(
            score_issue, indexes, issue_pointer, context, issues, scoring_ready
        )


def _validate_single_score_issue(
    score_issue: _JsonRecord,
    indexes: _BundleIndexes,
    pointer: str,
    context: _ValidationContext,
    issues: list[ReportQualityValidationIssue],
    scoring_ready: bool,
) -> None:
    """校验单条 score issue 的条件必填、语义和引用。

    Args:
        score_issue: score issue record。
        indexes: bundle id 索引。
        pointer: issue pointer。
        context: 校验上下文。
        issues: issue accumulator。
        scoring_ready: bundle 是否声明 scoring_ready。

    Returns:
        无返回值。
    """

    status = score_issue.get("status")
    dimension = score_issue.get("dimension")
    gap_refs = _list(score_issue.get("data_gap_refs"))

    if dimension == "chapter_summary":
        _validate_chapter_summary_issue(score_issue, pointer, context, issues)
    elif status == "N/A":
        _validate_na_issue(score_issue, indexes, pointer, context, issues)

    if status in {"issue", "blocked"}:
        if score_issue.get("severity") is None:
            issues.append(
                _make_issue(
                    error_code="RQV_FIELD_MISSING",
                    severity="blocking",
                    pointer=f"{pointer}/severity",
                    message="issue 或 blocked 状态必须提供 severity。",
                    context=context,
                    record_id=_record_id(score_issue),
                    field_name="severity",
                    expected="blocking, material, or minor",
                    actual="missing",
                )
            )
        if not any(score_issue.get(field) for field in ("field_path", "claim_id", "contract_item_id")):
            issues.append(
                _make_issue(
                    error_code="RQV_FIELD_MISSING",
                    severity="material",
                    pointer=pointer,
                    message="issue 或 blocked 状态至少需要 field_path、claim_id 或 contract_item_id。",
                    context=context,
                    record_id=_record_id(score_issue),
                    field_name="field_path",
                    expected="field_path, claim_id, or contract_item_id",
                    actual="missing",
                )
            )

    if status == "pass":
        blocking_refs = [gap_id for gap_id in gap_refs if gap_id in indexes.blocking_gap_ids]
        if blocking_refs:
            issues.append(
                _make_issue(
                    error_code="RQV_REF_MISSING",
                    severity="blocking",
                    pointer=f"{pointer}/data_gap_refs",
                    message="pass 状态不得引用阻断性 data gap。",
                    context=context,
                    record_id=_record_id(score_issue),
                    field_name="data_gap_refs",
                    expected="no blocking gap refs",
                    actual=", ".join(blocking_refs),
                )
            )

    if status == "skipped" and dimension != "chapter_summary":
        issues.append(
            _make_issue(
                error_code="RQV_CHAPTER_SUMMARY_SEMANTICS",
                severity="blocking",
                pointer=f"{pointer}/status",
                message="skipped 只允许用于 chapter_summary 维度。",
                context=context,
                record_id=_record_id(score_issue),
                field_name="status",
                expected="dimension=chapter_summary",
                actual=f"dimension={dimension}",
            )
        )

    for ref_index, gap_id in enumerate(gap_refs):
        _validate_ref(
            gap_id,
            indexes.gap_ids,
            f"{pointer}/data_gap_refs/{ref_index}",
            "gap_id",
            context,
            issues,
        )
    for ref_index, anchor_ref in enumerate(_list(score_issue.get("evidence_anchor_refs"))):
        if not _non_empty_string(anchor_ref):
            issues.append(
                _make_issue(
                    error_code="RQV_REF_MISSING",
                    severity="blocking",
                    pointer=f"{pointer}/evidence_anchor_refs/{ref_index}",
                    message="evidence_anchor_refs 不得为空白。",
                    context=context,
                    record_id=_record_id(score_issue),
                    field_name="evidence_anchor_refs",
                    expected="non-empty ref",
                    actual=_actual(anchor_ref),
                )
            )
            continue
        if str(anchor_ref).startswith(_ANCHOR_REF_PREFIX):
            _validate_ref(
                anchor_ref,
                indexes.anchor_ids,
                f"{pointer}/evidence_anchor_refs/{ref_index}",
                "anchor_id",
                context,
                issues,
            )


def _validate_na_issue(
    score_issue: _JsonRecord,
    indexes: _BundleIndexes,
    pointer: str,
    context: _ValidationContext,
    issues: list[ReportQualityValidationIssue],
) -> None:
    """校验 N/A 语义。

    Args:
        score_issue: score issue record。
        indexes: bundle id 索引。
        pointer: issue pointer。
        context: 校验上下文。
        issues: issue accumulator。

    Returns:
        无返回值。
    """

    if not score_issue.get("na_reason") and not score_issue.get("reviewer_note"):
        issues.append(
            _make_issue(
                error_code="RQV_NA_SEMANTICS",
                severity="material",
                pointer=f"{pointer}/na_reason",
                message="N/A 必须提供 na_reason 或 reviewer_note。",
                context=context,
                record_id=_record_id(score_issue),
                field_name="na_reason",
                expected="na_reason or reviewer_note",
                actual="missing",
            )
        )
    if score_issue.get("severity") is not None:
        issues.append(
            _make_issue(
                error_code="RQV_NA_SEMANTICS",
                severity="material",
                pointer=f"{pointer}/severity",
                message="N/A 表示不适用，不应携带 issue severity。",
                context=context,
                record_id=_record_id(score_issue),
                field_name="severity",
                expected="None",
                actual=_actual(score_issue.get("severity")),
            )
        )
    blocking_refs = [
        str(gap_id)
        for gap_id in _list(score_issue.get("data_gap_refs"))
        if gap_id in indexes.blocking_gap_ids
    ]
    if blocking_refs:
        issues.append(
            _make_issue(
                error_code="RQV_NA_SEMANTICS",
                severity="blocking",
                pointer=f"{pointer}/data_gap_refs",
                message="N/A 不应引用 blocking data gap；缺证据应使用 issue 或 blocked。",
                context=context,
                record_id=_record_id(score_issue),
                field_name="data_gap_refs",
                expected="no blocking gap refs",
                actual=", ".join(blocking_refs),
            )
        )


def _validate_chapter_summary_issue(
    score_issue: _JsonRecord,
    pointer: str,
    context: _ValidationContext,
    issues: list[ReportQualityValidationIssue],
) -> None:
    """校验 chapter_summary canonical 语义。

    Args:
        score_issue: score issue record。
        pointer: issue pointer。
        context: 校验上下文。
        issues: issue accumulator。

    Returns:
        无返回值。
    """

    status = score_issue.get("status")
    if status != "skipped":
        issues.append(
            _make_issue(
                error_code="RQV_CHAPTER_SUMMARY_SEMANTICS",
                severity="blocking",
                pointer=f"{pointer}/status",
                message="chapter_summary 必须且只能使用 skipped 状态。",
                context=context,
                record_id=_record_id(score_issue),
                field_name="status",
                expected="skipped",
                actual=_actual(status),
            )
        )
    if score_issue.get("chapter_id") == "report_level":
        issues.append(
            _make_issue(
                error_code="RQV_CHAPTER_SUMMARY_SEMANTICS",
                severity="blocking",
                pointer=f"{pointer}/chapter_id",
                message="chapter_summary 必须有具体章节 chapter_id，不得是 report_level。",
                context=context,
                record_id=_record_id(score_issue),
                field_name="chapter_id",
                expected="chapter_0..chapter_7",
                actual="report_level",
            )
        )
    if not score_issue.get("reviewer_note") and not score_issue.get("problem"):
        issues.append(
            _make_issue(
                error_code="RQV_CHAPTER_SUMMARY_SEMANTICS",
                severity="material",
                pointer=f"{pointer}/reviewer_note",
                message="chapter_summary skipped 必须解释跳过原因。",
                context=context,
                record_id=_record_id(score_issue),
                field_name="reviewer_note",
                expected="reviewer_note or problem",
                actual="missing",
            )
        )
    if score_issue.get("severity") is not None:
        issues.append(
            _make_issue(
                error_code="RQV_CHAPTER_SUMMARY_SEMANTICS",
                severity="material",
                pointer=f"{pointer}/severity",
                message="chapter_summary skipped 不应携带 severity。",
                context=context,
                record_id=_record_id(score_issue),
                field_name="severity",
                expected="None",
                actual=_actual(score_issue.get("severity")),
            )
        )


def _validate_calculations(
    calculations: Sequence[_JsonRecord],
    indexes: _BundleIndexes,
    pointer: str,
    context: _ValidationContext,
    issues: list[ReportQualityValidationIssue],
) -> None:
    """校验派生计算记录引用。

    Args:
        calculations: calculation records。
        indexes: bundle id 索引。
        pointer: bundle pointer。
        context: 校验上下文。
        issues: issue accumulator。

    Returns:
        无返回值。
    """

    for index, calculation in enumerate(calculations):
        calculation_pointer = f"{pointer}/derived_calculations/{index}"
        for ref_index, fact_id in enumerate(_list(calculation.get("input_fact_ids"))):
            _validate_ref(
                fact_id,
                indexes.fact_ids,
                f"{calculation_pointer}/input_fact_ids/{ref_index}",
                "fact_id",
                context,
                issues,
            )
        for ref_index, anchor_id in enumerate(_list(calculation.get("input_anchor_ids"))):
            _validate_ref(
                anchor_id,
                indexes.anchor_ids,
                f"{calculation_pointer}/input_anchor_ids/{ref_index}",
                "anchor_id",
                context,
                issues,
            )
        for ref_index, gap_id in enumerate(_list(calculation.get("data_gap_refs"))):
            _validate_ref(
                gap_id,
                indexes.gap_ids,
                f"{calculation_pointer}/data_gap_refs/{ref_index}",
                "gap_id",
                context,
                issues,
            )
        for ref_index, issue_id in enumerate(_list(calculation.get("score_issue_ids"))):
            _validate_ref(
                issue_id,
                indexes.issue_ids,
                f"{calculation_pointer}/score_issue_ids/{ref_index}",
                "issue_id",
                context,
                issues,
            )


def _validate_link_completeness(
    facts: Sequence[_JsonRecord],
    gaps: Sequence[_JsonRecord],
    score_issues: Sequence[_JsonRecord],
    indexes: _BundleIndexes,
    pointer: str,
    context: _ValidationContext,
    issues: list[ReportQualityValidationIssue],
    scoring_ready: bool,
) -> None:
    """校验 fact / gap / issue 双向链接完整性。

    Args:
        facts: fact records。
        gaps: data gap records。
        score_issues: score issue records。
        indexes: bundle id 索引。
        pointer: bundle pointer。
        context: 校验上下文。
        issues: issue accumulator。
        scoring_ready: bundle 是否声明 scoring_ready。

    Returns:
        无返回值。
    """

    severity: ValidationSeverity = "blocking" if scoring_ready else "material"
    gap_ids_by_issue: dict[str, set[str]] = {}
    for issue in score_issues:
        issue_id = issue.get("issue_id")
        if not _non_empty_string(issue_id):
            continue
        for gap_id in _list(issue.get("data_gap_refs")):
            if _non_empty_string(gap_id):
                gap_ids_by_issue.setdefault(str(issue_id), set()).add(str(gap_id))

    for gap_index, gap in enumerate(gaps):
        gap_id = gap.get("gap_id")
        if not _non_empty_string(gap_id):
            continue
        for issue_id, issue_gap_ids in gap_ids_by_issue.items():
            if str(gap_id) in issue_gap_ids and issue_id not in _list(gap.get("score_issue_ids")):
                issues.append(
                    _make_issue(
                        error_code="RQV_GAP_LINK_INCOMPLETE",
                        severity=severity,
                        pointer=f"{pointer}/data_gaps/{gap_index}/score_issue_ids",
                        message="issue 引用 gap 时，gap.score_issue_ids 应回链 issue。",
                        context=context,
                        record_id=str(gap_id),
                        field_name="score_issue_ids",
                        expected=issue_id,
                        actual=", ".join(str(item) for item in _list(gap.get("score_issue_ids"))),
                    )
                )

    for fact_index, fact in enumerate(facts):
        fact_id = fact.get("fact_id")
        if _is_blocked_fact(fact):
            related_gap_ids = [
                str(gap.get("gap_id"))
                for gap in gaps
                if gap.get("related_fact_id") == fact_id and _non_empty_string(gap.get("gap_id"))
            ]
            missing_gap_ids = [
                gap_id for gap_id in related_gap_ids if gap_id not in _list(fact.get("data_gap_refs"))
            ]
            if missing_gap_ids:
                issues.append(
                    _make_issue(
                        error_code="RQV_GAP_LINK_INCOMPLETE",
                        severity=severity,
                        pointer=f"{pointer}/facts/{fact_index}/data_gap_refs",
                        message="因缺口阻断的 fact 应包含相关 data_gap_refs。",
                        context=context,
                        record_id=_record_id(fact),
                        field_name="data_gap_refs",
                        expected=", ".join(missing_gap_ids),
                        actual=", ".join(str(item) for item in _list(fact.get("data_gap_refs"))),
                    )
                )

    for issue in score_issues:
        field_path = issue.get("field_path")
        issue_id = issue.get("issue_id")
        if not _non_empty_string(field_path) or not _non_empty_string(issue_id):
            continue
        fact = indexes.facts_by_field_path.get(str(field_path))
        if fact is None or issue_id in _list(fact.get("score_issue_ids")):
            continue
        issues.append(
            _make_issue(
                error_code="RQV_GAP_LINK_INCOMPLETE",
                severity=severity,
                pointer=f"{pointer}/facts/{_fact_index(facts, fact)}/score_issue_ids",
                message="关键评分 issue 定位到 field_path 时，对应 fact 应回链 issue id。",
                context=context,
                record_id=_record_id(fact),
                field_name="score_issue_ids",
                expected=str(issue_id),
                actual=", ".join(str(item) for item in _list(fact.get("score_issue_ids"))),
            )
        )


def _validate_scoring_ready_preconditions(
    bundle: _JsonRecord,
    source_documents: Sequence[_JsonRecord],
    facts: Sequence[_JsonRecord],
    gaps: Sequence[_JsonRecord],
    score_issues: Sequence[_JsonRecord],
    indexes: _BundleIndexes,
    pointer: str,
    context: _ValidationContext,
    issues: list[ReportQualityValidationIssue],
) -> None:
    """校验 scoring_ready canonical 前置条件。

    Args:
        bundle: bundle record。
        source_documents: 来源文档 records。
        facts: fact records。
        gaps: data gap records。
        score_issues: score issue records。
        indexes: bundle id 索引。
        pointer: bundle pointer。
        context: 校验上下文。
        issues: issue accumulator。

    Returns:
        无返回值。
    """

    review_status = bundle.get("review_status")
    if review_status == _ACCEPTED_BASELINE_STATUS:
        issues.append(
            _make_issue(
                error_code="RQV_SCORING_READY_PRECONDITION",
                severity="blocking",
                pointer=f"{pointer}/review_status",
                message="当前 slice 不允许 accepted_baseline 输入。",
                context=context,
                record_id=_record_id(bundle),
                field_name="review_status",
                expected="not accepted_baseline",
                actual=_ACCEPTED_BASELINE_STATUS,
            )
        )
        return
    if review_status != _SCORING_READY_STATUS:
        return

    failures: list[str] = []
    if bundle.get("corpus_id") == "ad_hoc":
        failures.append("corpus_id must not be ad_hoc")
    if bundle.get("classified_fund_type") == "unknown":
        failures.append("classified_fund_type must not be unknown")
    if bundle.get("type_slot_membership_status") != "matches_slot":
        failures.append("type_slot_membership_status must be matches_slot")

    document_failures = _scoring_ready_document_failures(source_documents)
    failures.extend(document_failures)

    preferred_lens = _mapping_or_empty(bundle.get("preferred_lens"))
    chapter_ids = {
        str(chapter.get("chapter_id"))
        for chapter in _list_of_mappings(preferred_lens.get("chapters"))
        if _non_empty_string(chapter.get("chapter_id"))
        and all(field in chapter for field in _PREFERRED_LENS_CHAPTER_REQUIRED_FIELDS)
    }
    if not _TEMPLATE_CHAPTER_IDS <= chapter_ids:
        failures.append("preferred_lens must cover chapter_0..chapter_7 with required fields")

    if indexes.blocking_gap_ids:
        failures.append("blocking data gaps must be resolved")
    if any(issue.get("severity") == "blocking" for issue in score_issues):
        failures.append("blocking score issues must be resolved")

    quality_context = _mapping_or_empty(bundle.get("quality_context"))
    if quality_context.get("fq_gate_status") == "block":
        failures.append("quality_context.fq_gate_status must not be block")
    if quality_context.get("programmatic_audit_status") == "block":
        failures.append("quality_context.programmatic_audit_status must not be block")
    if any(fact.get("review_status") != "reviewed" for fact in facts):
        failures.append("all facts must have review_status=reviewed")
    if any(document.get("source_failure_category") == _UNKNOWN_UPSTREAM_FAILURE for document in source_documents):
        failures.append("unknown upstream failure category must be recovered")
    if any(gap.get("failure_category") == _UNKNOWN_UPSTREAM_FAILURE for gap in gaps):
        failures.append("unknown gap failure category must be recovered")

    if failures:
        issues.append(
            _make_issue(
                error_code="RQV_SCORING_READY_PRECONDITION",
                severity="blocking",
                pointer=f"{pointer}/review_status",
                message="scoring_ready 前置条件不满足：" + "；".join(failures),
                context=context,
                record_id=_record_id(bundle),
                field_name="review_status",
                expected="all scoring_ready preconditions satisfied",
                actual="; ".join(failures),
            )
        )


def _scoring_ready_document_failures(documents: Sequence[_JsonRecord]) -> list[str]:
    """生成 scoring_ready 来源文档前置失败说明。

    Args:
        documents: 来源文档 records。

    Returns:
        失败说明列表。
    """

    annual_reports = [
        document for document in documents if document.get("document_type") == "annual_report"
    ]
    if not annual_reports:
        return ["verified annual report document is required"]

    failures: list[str] = []
    if not any(
        document.get("identity_status") == "verified_annual_report"
        for document in annual_reports
    ):
        failures.append("annual report identity must be verified")
    boundaries = {document.get("source_boundary") for document in annual_reports}
    if boundaries & {"unknown", "probe_only"}:
        failures.append("annual report source_boundary must not be unknown/probe_only")
    if boundaries == {"external_official"}:
        failures.append("external_official cannot be the only annual report source boundary")
    failure_categories = {document.get("source_failure_category") for document in annual_reports}
    if failure_categories != {"none"}:
        failures.append("annual report source_failure_category must be none")
    return failures


def _validate_ref(
    value: object,
    allowed_ids: frozenset[str],
    pointer: str,
    field_name: str,
    context: _ValidationContext,
    issues: list[ReportQualityValidationIssue],
) -> None:
    """校验单个 id reference。

    Args:
        value: 引用值。
        allowed_ids: 合法 id 集合。
        pointer: 引用字段 pointer。
        field_name: 字段名。
        context: 校验上下文。
        issues: issue accumulator。

    Returns:
        无返回值。
    """

    if not _non_empty_string(value) or value not in allowed_ids:
        issues.append(
            _make_issue(
                error_code="RQV_REF_MISSING",
                severity="blocking",
                pointer=pointer,
                message="id reference 指向不存在的 bundle-local 记录。",
                context=context,
                field_name=field_name,
                expected="existing id",
                actual=_actual(value),
            )
        )


def _build_summary(
    issues: Sequence[ReportQualityValidationIssue],
    total_records: int,
    scoring_ready_record_count: int,
) -> ReportQualityValidationSummary:
    """构建校验汇总。

    Args:
        issues: issue 列表。
        total_records: 已解析记录数。
        scoring_ready_record_count: scoring_ready bundle 数。

    Returns:
        校验汇总。
    """

    severity_counts = Counter(issue.severity for issue in issues)
    error_counts = Counter(issue.error_code for issue in issues)
    return ReportQualityValidationSummary(
        total_records=total_records,
        blocking_count=severity_counts["blocking"],
        material_count=severity_counts["material"],
        minor_count=severity_counts["minor"],
        error_code_counts=tuple(sorted(error_counts.items())),
        scoring_ready_record_count=scoring_ready_record_count,
        failed_closed=severity_counts["blocking"] > 0,
    )


def _resolve_run_id(
    explicit_run_id: str | None,
    records: Sequence[_JsonRecord],
    issues: list[ReportQualityValidationIssue],
    context: _ValidationContext,
) -> str | None:
    """解析或校验 run id。

    Args:
        explicit_run_id: 调用方显式 run id。
        records: 已解析记录。
        issues: issue accumulator。
        context: 校验上下文。

    Returns:
        resolved run id。
    """

    run_ids: set[str] = set()
    for record in records:
        if _non_empty_string(record.get("score_run_id")):
            run_ids.add(str(record["score_run_id"]))
        for score_issue in _list_of_mappings(record.get("score_issue_links")):
            if _non_empty_string(score_issue.get("score_run_id")):
                run_ids.add(str(score_issue["score_run_id"]))
    if explicit_run_id is not None:
        if run_ids and run_ids != {explicit_run_id}:
            issues.append(
                _make_issue(
                    error_code="RQV_FIELD_MISSING",
                    severity="material",
                    pointer="run_id",
                    message="调用方 run_id 与记录内 score_run_id 不一致。",
                    context=context,
                    field_name="run_id",
                    expected=explicit_run_id,
                    actual=", ".join(sorted(run_ids)),
                )
            )
        return explicit_run_id
    if len(run_ids) > 1:
        issues.append(
            _make_issue(
                error_code="RQV_FIELD_MISSING",
                severity="material",
                pointer="run_id",
                message="记录内存在多个 score_run_id，无法唯一推断 run_id。",
                context=context,
                field_name="run_id",
                expected="single score_run_id",
                actual=", ".join(sorted(run_ids)),
            )
        )
        return None
    return next(iter(run_ids), None)


def _first_schema_version(bundle_records: Sequence[_JsonRecord]) -> str | None:
    """读取首个 bundle schema_version。

    Args:
        bundle_records: bundle records。

    Returns:
        schema version 或 None。
    """

    for record in bundle_records:
        value = record.get("schema_version")
        if isinstance(value, str):
            return value
    return None


def _scoring_ready_count(bundle_records: Sequence[_JsonRecord]) -> int:
    """统计 scoring_ready bundle 数。

    Args:
        bundle_records: bundle records。

    Returns:
        scoring_ready 数量。
    """

    return sum(1 for record in bundle_records if record.get("review_status") == _SCORING_READY_STATUS)


def _normalize_record(record: ReportEvidenceBundle | Mapping[str, object]) -> _JsonRecord:
    """把 dataclass 或 Mapping 归一化为 Mapping。

    Args:
        record: dataclass 或 Mapping。

    Returns:
        JSON-like Mapping。

    Raises:
        TypeError: 输入类型不支持时抛出。
    """

    if is_dataclass(record):
        normalized = asdict(record)
        if not isinstance(normalized, Mapping):
            raise TypeError("dataclass record must serialize to a mapping")
        return normalized
    if isinstance(record, Mapping):
        return record
    raise TypeError("bundle must be ReportEvidenceBundle or Mapping[str, object]")


def _enum_values(enum_key: str) -> tuple[str, ...]:
    """读取 report_evidence.py Literal domain 值。

    Args:
        enum_key: `_ENUM_FIELDS` 中的枚举键。

    Returns:
        合法字符串元组。
    """

    return tuple(str(value) for value in _literal_values(_ENUM_FIELDS[enum_key]))


def _literal_values(domain: object) -> tuple[object, ...]:
    """递归展开 Literal 或 Union type alias 的值。

    Args:
        domain: Literal domain 或由 Literal 组成的 Union。

    Returns:
        展开后的枚举值。
    """

    args = get_args(domain)
    if not args:
        return (domain,)
    values: list[object] = []
    for arg in args:
        nested_args = get_args(arg)
        if nested_args:
            values.extend(_literal_values(arg))
        else:
            values.append(arg)
    return tuple(values)


def _make_issue(
    *,
    error_code: str,
    severity: ValidationSeverity,
    pointer: str,
    message: str,
    context: _ValidationContext,
    record_type: str | None = None,
    record_id: str | None = None,
    field_name: str | None = None,
    expected: str | None = None,
    actual: str | None = None,
) -> ReportQualityValidationIssue:
    """创建结构化 validation issue。

    Args:
        error_code: 稳定错误码。
        severity: 严重程度。
        pointer: 稳定 pointer。
        message: 中文说明。
        context: 校验上下文。
        record_type: 记录类型。
        record_id: 记录 id。
        field_name: 字段名。
        expected: 期望说明。
        actual: 实际说明。

    Returns:
        validation issue。
    """

    return ReportQualityValidationIssue(
        error_code=error_code,
        severity=severity,
        record_pointer=pointer,
        message=message,
        source_path=context.source_path,
        record_type=record_type or context.record_type,
        record_id=record_id,
        field_name=field_name,
        expected=expected,
        actual=actual,
    )


def _pointer(context: _ValidationContext, suffix: str) -> str:
    """拼接当前上下文 pointer。

    Args:
        context: 校验上下文。
        suffix: pointer suffix。

    Returns:
        稳定 pointer。
    """

    if context.line_prefix:
        return f"{context.line_prefix}/{suffix}"
    return f"/{suffix}"


def _mapping_or_empty(value: object) -> _JsonRecord:
    """把 Mapping 值安全转换为 Mapping，否则返回空 Mapping。

    Args:
        value: 输入值。

    Returns:
        Mapping 或空 dict。
    """

    if isinstance(value, Mapping):
        return value
    return {}


def _list_of_mappings(value: object) -> tuple[_JsonRecord, ...]:
    """读取 Mapping 数组。

    Args:
        value: 输入值。

    Returns:
        Mapping 元组，非 Mapping 项会被忽略，由字段校验负责报缺失。
    """

    return tuple(item for item in _list(value) if isinstance(item, Mapping))


def _list(value: object) -> tuple[object, ...]:
    """把 list / tuple 输入归一化为 tuple。

    Args:
        value: 输入值。

    Returns:
        tuple 值；非数组返回空 tuple。
    """

    if isinstance(value, list | tuple):
        return tuple(value)
    return ()


def _non_empty_string(value: object) -> bool:
    """判断值是否为非空字符串。

    Args:
        value: 输入值。

    Returns:
        是非空字符串时为 True。
    """

    return isinstance(value, str) and bool(value.strip())


def _record_id(record: _JsonRecord) -> str | None:
    """读取记录稳定 id。

    Args:
        record: 任意 record。

    Returns:
        记录 id 或 None。
    """

    for field_name in ("bundle_id", "issue_id", "fact_id", "gap_id", "anchor_id", "document_id"):
        value = record.get(field_name)
        if _non_empty_string(value):
            return str(value)
    return None


def _string_or_none(value: object) -> str | None:
    """把字符串值转成 str 或 None。

    Args:
        value: 输入值。

    Returns:
        字符串或 None。
    """

    return value if isinstance(value, str) else None


def _actual(value: object) -> str:
    """生成 issue actual 字段。

    Args:
        value: 输入值。

    Returns:
        可读字符串。
    """

    if value is None:
        return "None"
    return str(value)


def _is_blocking_gap(gap: _JsonRecord) -> bool:
    """判断 data gap 是否阻断评分。

    Args:
        gap: data gap record。

    Returns:
        阻断性 data gap 返回 True。
    """

    return gap.get("gap_kind") != "not_applicable" and gap.get("failure_category") != "not_applicable"


def _is_blocked_fact(fact: _JsonRecord) -> bool:
    """判断 fact 是否因缺口或不安全抽取而需要 gap 回链。

    Args:
        fact: fact record。

    Returns:
        需要 gap 回链时返回 True。
    """

    return fact.get("value") is None or fact.get("extraction_mode") in {"missing", "estimated"}


def _fact_index(facts: Sequence[_JsonRecord], target: _JsonRecord) -> int:
    """查找 fact 在数组中的位置。

    Args:
        facts: fact records。
        target: 目标 fact。

    Returns:
        fact index；找不到时返回 0。
    """

    for index, fact in enumerate(facts):
        if fact is target:
            return index
    return 0
