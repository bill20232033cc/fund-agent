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
    assert provenance.source_strategy == "legacy_or_unknown"
    assert provenance.selected_source is None
    assert provenance.source_mode == "legacy_or_unknown"
    assert provenance.fallback_enabled is None
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
    assert provenance.selected_source is None
    assert provenance.source_mode == "legacy_or_unknown"
    assert provenance.fallback_enabled is None
    assert provenance.fallback_used is False
    assert provenance.fallback_eligibility == "not_applicable"
    assert provenance.source_provenance_status == "not_applicable"


def test_eid_single_source_metadata_projects_current_policy_fields() -> None:
    """验证当前 EID single-source 元数据投影公共策略字段。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当当前 EID 策略字段没有进入公共 provenance 时抛出。
    """

    provenance = project_public_source_provenance(
        AnnualReportSourceMetadata(
            source="eid",
            fallback_used=False,
            selected_source="eid",
            source_mode="single_source_only",
            fallback_enabled=False,
        )
    )

    assert provenance.source_provenance_schema_version == "repository_source_provenance.v2"
    assert provenance.source_strategy == "single_source_only"
    assert provenance.selected_source == "eid"
    assert provenance.source_mode == "single_source_only"
    assert provenance.fallback_enabled is False
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
    assert provenance.selected_source is None
    assert provenance.source_mode == "legacy_or_unknown"
    assert provenance.fallback_enabled is None
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
    assert provenance.selected_source is None
    assert provenance.source_mode == "legacy_or_unknown"
    assert provenance.fallback_enabled is None
    assert provenance.fallback_used is True
    assert provenance.primary_failure_category is None
    assert provenance.fallback_eligibility == "unknown_public_metadata_absent"
    assert provenance.source_provenance_status == "incomplete"
    assert provenance.source_provenance_reason == "fallback_used_primary_failure_category_absent"


@pytest.mark.parametrize("category", ["not_found", "unavailable"])
def test_fallback_with_metadata_owned_eligible_category_is_complete(
    category: PrimaryFailureCategory,
) -> None:
    """验证元数据持久化的 eligible 分类会被生产投影消费。

    Args:
        category: 主源失败分类。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当元数据分类没有优先用于投影时抛出。
    """

    provenance = project_public_source_provenance(
        AnnualReportSourceMetadata(
            source="eastmoney",
            fallback_used=True,
            primary_failure_category=category,
        )
    )

    assert provenance.primary_failure_category == category
    assert provenance.selected_source is None
    assert provenance.source_mode == "legacy_or_unknown"
    assert provenance.fallback_enabled is None
    assert provenance.fallback_eligibility == "eligible"
    assert provenance.source_provenance_status == "complete"


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
    assert provenance.selected_source is None
    assert provenance.source_mode == "legacy_or_unknown"
    assert provenance.fallback_enabled is None
    assert provenance.fallback_eligibility == "eligible"
    assert provenance.source_provenance_status == "complete"


@pytest.mark.parametrize("category", ["schema_drift", "identity_mismatch", "integrity_error"])
def test_fallback_with_metadata_owned_fail_closed_category_is_incomplete(
    category: PrimaryFailureCategory,
) -> None:
    """验证元数据中的 fail-closed 分类不会被下游状态覆盖。

    Args:
        category: 主源失败分类。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 fail-closed 分类被误标为 eligible 时抛出。
    """

    provenance = project_public_source_provenance(
        AnnualReportSourceMetadata(
            source="eastmoney",
            fallback_used=True,
            primary_failure_category=category,
        )
    )

    assert provenance.primary_failure_category == category
    assert provenance.selected_source is None
    assert provenance.source_mode == "legacy_or_unknown"
    assert provenance.fallback_enabled is None
    assert provenance.fallback_eligibility == "fail_closed"
    assert provenance.source_provenance_status == "incomplete"


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
    assert provenance.selected_source is None
    assert provenance.source_mode == "legacy_or_unknown"
    assert provenance.fallback_enabled is None
    assert provenance.fallback_eligibility == "fail_closed"
    assert provenance.source_provenance_status == "incomplete"
    assert provenance.source_provenance_status != "not_applicable"


def test_metadata_failure_category_wins_over_keyword_override() -> None:
    """验证元数据字段优先于显式测试覆盖参数。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 kwarg 覆盖了元数据同源分类时抛出。
    """

    provenance = project_public_source_provenance(
        AnnualReportSourceMetadata(
            source="eastmoney",
            fallback_used=True,
            primary_failure_category="schema_drift",
        ),
        primary_failure_category="not_found",
    )

    assert provenance.primary_failure_category == "schema_drift"
    assert provenance.selected_source is None
    assert provenance.source_mode == "legacy_or_unknown"
    assert provenance.fallback_enabled is None
    assert provenance.fallback_eligibility == "fail_closed"
    assert provenance.source_provenance_reason == "fallback_used_primary_failure_category_fail_closed"


def test_keyword_failure_category_still_applies_when_metadata_category_missing() -> None:
    """验证元数据缺分类时仍保留测试用显式分类兼容路径。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当兼容 kwarg 路径失效时抛出。
    """

    provenance = project_public_source_provenance(
        AnnualReportSourceMetadata(source="eastmoney", fallback_used=True),
        primary_failure_category="unavailable",
    )

    assert provenance.primary_failure_category == "unavailable"
    assert provenance.selected_source is None
    assert provenance.source_mode == "legacy_or_unknown"
    assert provenance.fallback_enabled is None
    assert provenance.fallback_eligibility == "eligible"
    assert provenance.source_provenance_status == "complete"


def test_source_provenance_no_primary_then_fallback_value_in_current_eid_path() -> None:
    """验证当前 EID 路径不会输出旧 fallback 策略值。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当当前 EID payload 仍暴露旧策略值时抛出。
    """

    provenance = project_public_source_provenance(
        AnnualReportSourceMetadata(
            source="eid",
            fallback_used=False,
            selected_source="eid",
            source_mode="single_source_only",
            fallback_enabled=False,
        )
    )

    assert "primary_then_fallback" not in source_provenance_to_dict(provenance).values()


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
        "source_provenance_schema_version": "repository_source_provenance.v2",
        "source_strategy": "legacy_or_unknown",
        "selected_source": None,
        "source_mode": "legacy_or_unknown",
        "fallback_enabled": None,
        "resolved_source_name": None,
        "fallback_used": False,
        "primary_failure_category": None,
        "fallback_eligibility": "not_applicable",
        "source_provenance_status": "not_applicable",
        "source_provenance_reason": "source_metadata_absent_no_fallback_evidence",
    }
