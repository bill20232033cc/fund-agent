"""公共来源 provenance 投影测试。"""

from __future__ import annotations

import pytest

from fund_agent.fund.documents.models import AnnualReportSourceMetadata
from fund_agent.fund.source_provenance import (
    PUBLIC_SOURCE_PROVENANCE_SCHEMA_VERSION,
    PrimaryFailureCategory,
    default_public_source_provenance,
    project_public_source_provenance,
    source_provenance_to_dict,
)


def test_default_public_source_provenance_is_not_applicable() -> None:
    """验证缺少来源元数据时输出稳定 not_applicable 默认值。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当默认 provenance 暴露 fallback 或不一致状态时抛出。
    """

    provenance = default_public_source_provenance()

    assert provenance.source_provenance_schema_version == PUBLIC_SOURCE_PROVENANCE_SCHEMA_VERSION
    assert provenance.source_strategy == "primary_then_fallback"
    assert provenance.resolved_source_name is None
    assert provenance.fallback_used is False
    assert provenance.primary_failure_category is None
    assert provenance.fallback_eligibility == "not_applicable"
    assert provenance.source_provenance_status == "not_applicable"
    assert provenance.source_provenance_reason == "source_metadata_absent_no_fallback_evidence"


def test_primary_metadata_without_fallback_remains_not_applicable() -> None:
    """验证主源成功不会被来源名误判为 fallback。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当非 fallback 来源被标记为 eligible 时抛出。
    """

    provenance = project_public_source_provenance(
        AnnualReportSourceMetadata(source="eid", fallback_used=False)
    )

    assert provenance.resolved_source_name == "eid"
    assert provenance.fallback_used is False
    assert provenance.fallback_eligibility == "not_applicable"
    assert provenance.source_provenance_status == "not_applicable"
    assert provenance.primary_failure_category is None


def test_eastmoney_source_name_alone_does_not_imply_fallback() -> None:
    """验证 `eastmoney` 来源名本身不代表 fallback 已发生。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当来源名被用作间接 fallback 证据时抛出。
    """

    provenance = project_public_source_provenance(
        AnnualReportSourceMetadata(source="eastmoney", fallback_used=False)
    )

    assert provenance.resolved_source_name == "eastmoney"
    assert provenance.fallback_used is False
    assert provenance.fallback_eligibility == "not_applicable"
    assert provenance.source_provenance_status == "not_applicable"


def test_fallback_without_public_failure_category_is_incomplete_unknown() -> None:
    """验证 fallback 成功但缺少主源失败分类时保持 unknown。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当缺失分类被推断为 eligible 时抛出。
    """

    provenance = project_public_source_provenance(
        AnnualReportSourceMetadata(source="eastmoney", fallback_used=True)
    )

    assert provenance.resolved_source_name == "eastmoney"
    assert provenance.fallback_used is True
    assert provenance.primary_failure_category is None
    assert provenance.fallback_eligibility == "unknown_public_metadata_absent"
    assert provenance.source_provenance_status == "incomplete"
    assert provenance.source_provenance_reason == "fallback_used_primary_failure_category_absent"


@pytest.mark.parametrize("category", ["not_found", "unavailable"])
def test_fallback_with_eligible_category_is_complete(category: PrimaryFailureCategory) -> None:
    """验证允许 fallback 的失败分类映射为 eligible。

    Args:
        category: 主源失败分类。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 eligible 分类没有完整投影时抛出。
    """

    provenance = project_public_source_provenance(
        AnnualReportSourceMetadata(source="eastmoney", fallback_used=True),
        primary_failure_category=category,
    )

    assert provenance.primary_failure_category == category
    assert provenance.fallback_eligibility == "eligible"
    assert provenance.source_provenance_status == "complete"


@pytest.mark.parametrize("category", ["schema_drift", "identity_mismatch", "integrity_error"])
def test_fallback_with_fail_closed_category_is_incomplete(
    category: PrimaryFailureCategory,
) -> None:
    """验证 fail-closed 分类不会因下游抽取成功变成 eligible。

    Args:
        category: 主源失败分类。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 fail-closed 分类被误标为 clean 时抛出。
    """

    provenance = project_public_source_provenance(
        AnnualReportSourceMetadata(source="eastmoney", fallback_used=True),
        primary_failure_category=category,
    )

    assert provenance.primary_failure_category == category
    assert provenance.fallback_eligibility == "fail_closed"
    assert provenance.source_provenance_status == "incomplete"
    assert provenance.source_provenance_status != "not_applicable"


def test_source_provenance_to_dict_serializes_stable_keys() -> None:
    """验证公共 provenance 字典输出只包含稳定字段。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当字典 key 集合或默认值不稳定时抛出。
    """

    payload = source_provenance_to_dict(default_public_source_provenance())

    assert payload == {
        "source_provenance_schema_version": "repository_source_provenance.v1",
        "source_strategy": "primary_then_fallback",
        "resolved_source_name": None,
        "fallback_used": False,
        "primary_failure_category": None,
        "fallback_eligibility": "not_applicable",
        "source_provenance_status": "not_applicable",
        "source_provenance_reason": "source_metadata_absent_no_fallback_evidence",
    }
