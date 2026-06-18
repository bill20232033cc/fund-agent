"""Docling candidate failure 到年报来源失败类别的映射。"""

from __future__ import annotations

from fund_agent.fund.documents.models import AnnualReportSourceFailureCategory

from .models import CandidateFailureCode

CANONICAL_FAILURE_CATEGORIES: tuple[AnnualReportSourceFailureCategory, ...] = (
    "not_found",
    "unavailable",
    "schema_drift",
    "identity_mismatch",
    "integrity_error",
)

_FAILURE_MAPPING: dict[CandidateFailureCode, AnnualReportSourceFailureCategory] = {
    CandidateFailureCode.CANDIDATE_NOT_FOUND: "not_found",
    CandidateFailureCode.CANDIDATE_UNAVAILABLE: "unavailable",
    CandidateFailureCode.CANDIDATE_IDENTITY_MISSING: "identity_mismatch",
    CandidateFailureCode.CANDIDATE_IDENTITY_MISMATCH: "identity_mismatch",
    CandidateFailureCode.CANDIDATE_ARTIFACT_HASH_MISSING: "integrity_error",
    CandidateFailureCode.CANDIDATE_ARTIFACT_HASH_MISMATCH: "integrity_error",
    CandidateFailureCode.CANDIDATE_SCHEMA_VERSION_UNSUPPORTED: "schema_drift",
    CandidateFailureCode.PAGE_PROVENANCE_MISSING: "schema_drift",
    CandidateFailureCode.SECTION_HIERARCHY_UNSTABLE: "schema_drift",
    CandidateFailureCode.TABLE_CELLS_MISSING: "schema_drift",
    CandidateFailureCode.TABLE_PROVENANCE_MISSING: "schema_drift",
    CandidateFailureCode.TABLE_SECTION_UNASSIGNED: "schema_drift",
    CandidateFailureCode.TABLE_HEADER_UNSTABLE: "schema_drift",
    CandidateFailureCode.TABLE_SHAPE_INCONSISTENT: "schema_drift",
    CandidateFailureCode.TABLE_CONTINUATION_AMBIGUOUS: "schema_drift",
    CandidateFailureCode.CELL_TEXT_EMPTY: "schema_drift",
    CandidateFailureCode.CELL_BBOX_MISSING: "schema_drift",
    CandidateFailureCode.CELL_HEADER_PATH_MISSING: "schema_drift",
    CandidateFailureCode.CELL_ROW_LABEL_PATH_MISSING: "schema_drift",
    CandidateFailureCode.CELL_SPAN_CONFLICT: "schema_drift",
    CandidateFailureCode.CELL_LOCATOR_UNSTABLE: "schema_drift",
    CandidateFailureCode.NUMERIC_REPAIR_AMBIGUOUS: "schema_drift",
    CandidateFailureCode.EXCERPT_HASH_MISMATCH: "integrity_error",
    CandidateFailureCode.EXCERPT_TRUNCATED: "integrity_error",
}


def map_candidate_failure_to_source_category(
    failure_code: CandidateFailureCode,
) -> AnnualReportSourceFailureCategory:
    """把 candidate 内部失败代码映射为当前年报来源失败类别。

    Args:
        failure_code: candidate 内部失败代码。

    Returns:
        当前生产来源契约中的 canonical failure category。

    Raises:
        KeyError: 失败代码未被显式映射时抛出。
    """

    return _FAILURE_MAPPING[failure_code]


def mapped_candidate_failure_codes() -> frozenset[CandidateFailureCode]:
    """返回已映射的 candidate 失败代码集合。

    Args:
        无。

    Returns:
        已映射失败代码集合。

    Raises:
        无显式抛出。
    """

    return frozenset(_FAILURE_MAPPING)

