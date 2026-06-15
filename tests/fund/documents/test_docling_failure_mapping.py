"""Docling candidate failure mapping 测试。"""

from __future__ import annotations

from fund_agent.fund.documents.candidates.failures import (
    CANONICAL_FAILURE_CATEGORIES,
    map_candidate_failure_to_source_category,
    mapped_candidate_failure_codes,
)
from fund_agent.fund.documents.candidates.models import CandidateFailureCode


def test_every_candidate_failure_code_is_mapped() -> None:
    """验证每个 candidate failure 都有 canonical 映射。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 存在未映射失败代码时抛出。
    """

    assert mapped_candidate_failure_codes() == frozenset(CandidateFailureCode)


def test_failure_mapping_uses_only_current_canonical_categories() -> None:
    """验证 failure mapping 不引入 fallback/source 扩展类别。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 映射类别越界时抛出。
    """

    for failure_code in CandidateFailureCode:
        assert map_candidate_failure_to_source_category(failure_code) in CANONICAL_FAILURE_CATEGORIES
    assert map_candidate_failure_to_source_category(CandidateFailureCode.CANDIDATE_NOT_FOUND) == "not_found"
    assert (
        map_candidate_failure_to_source_category(CandidateFailureCode.CANDIDATE_UNAVAILABLE)
        == "unavailable"
    )
    assert (
        map_candidate_failure_to_source_category(CandidateFailureCode.CANDIDATE_IDENTITY_MISMATCH)
        == "identity_mismatch"
    )
    assert (
        map_candidate_failure_to_source_category(
            CandidateFailureCode.CANDIDATE_ARTIFACT_HASH_MISMATCH
        )
        == "integrity_error"
    )
    assert (
        map_candidate_failure_to_source_category(CandidateFailureCode.TABLE_CELLS_MISSING)
        == "schema_drift"
    )

