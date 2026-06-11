"""年报公共来源 provenance 投影。

本模块位于 Agent 层基金能力包，只把 `FundDocumentRepository` 已暴露的
年报来源元数据投影为公共输出字段，不读取来源策略、下载器、缓存或 fallback 内部实现。
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Final, Literal

from fund_agent.fund.documents.models import AnnualReportSourceMetadata

PUBLIC_SOURCE_PROVENANCE_SCHEMA_VERSION: Final[str] = "repository_source_provenance.v2"
CURRENT_SOURCE_STRATEGY: Final[str] = "single_source_only"
LEGACY_OR_UNKNOWN_SOURCE_STRATEGY: Final[str] = "legacy_or_unknown"
SOURCE_PROVENANCE_REASON_SOURCE_METADATA_ABSENT: Final[str] = (
    "source_metadata_absent_no_fallback_evidence"
)
SOURCE_PROVENANCE_REASON_PRIMARY_NO_FALLBACK: Final[str] = "primary_source_success_no_fallback"
SOURCE_PROVENANCE_REASON_FALLBACK_CATEGORY_ABSENT: Final[str] = (
    "fallback_used_primary_failure_category_absent"
)
SOURCE_PROVENANCE_REASON_FALLBACK_ELIGIBLE: Final[str] = (
    "fallback_used_primary_failure_category_eligible"
)
SOURCE_PROVENANCE_REASON_FALLBACK_FAIL_CLOSED: Final[str] = (
    "fallback_used_primary_failure_category_fail_closed"
)

SourceStrategy = Literal["single_source_only", "legacy_or_unknown"]
ResolvedSourceName = Literal["eid", "eastmoney"]
SelectedSourceName = Literal["eid", "eastmoney"]
SourceMode = Literal["single_source_only", "legacy_or_unknown"]
PrimaryFailureCategory = Literal[
    "not_found",
    "unavailable",
    "schema_drift",
    "identity_mismatch",
    "integrity_error",
]
FallbackEligibility = Literal[
    "eligible",
    "fail_closed",
    "not_applicable",
    "unknown_public_metadata_absent",
]
SourceProvenanceStatus = Literal["complete", "incomplete", "not_applicable"]

_ELIGIBLE_FAILURE_CATEGORIES: Final[frozenset[PrimaryFailureCategory]] = frozenset(
    ("not_found", "unavailable")
)
_FAIL_CLOSED_FAILURE_CATEGORIES: Final[frozenset[PrimaryFailureCategory]] = frozenset(
    ("schema_drift", "identity_mismatch", "integrity_error")
)


@dataclass(frozen=True, slots=True)
class PublicSourceProvenance:
    """公共年报来源 provenance。

    Attributes:
        source_provenance_schema_version: 公共 provenance schema 版本。
        source_strategy: 兼容字段；当前等同于 `source_mode`，不是来源获取策略或
            fallback 授权。
        selected_source: 当前来源策略选中的来源；缺失元数据或旧元数据时为 `None`。
        source_mode: 当前公共来源模式；旧元数据缺失策略字段时为 `legacy_or_unknown`。
        fallback_enabled: 当前来源策略是否启用 fallback；旧元数据缺失时为 `None`。
        resolved_source_name: 仓库元数据解析出的公开来源名。
        fallback_used: 本次成功年报是否来自 fallback 来源。
        primary_failure_category: 主来源失败分类；只来自仓库元数据或显式测试覆盖。
        fallback_eligibility: fallback 是否符合公开安全分类。
        source_provenance_status: provenance 完整性状态。
        source_provenance_reason: 稳定短原因码，不包含原始异常文本。
    """

    source_provenance_schema_version: str
    source_strategy: SourceStrategy
    selected_source: SelectedSourceName | None
    source_mode: SourceMode
    fallback_enabled: bool | None
    resolved_source_name: ResolvedSourceName | None
    fallback_used: bool
    primary_failure_category: PrimaryFailureCategory | None
    fallback_eligibility: FallbackEligibility
    source_provenance_status: SourceProvenanceStatus
    source_provenance_reason: str


def default_public_source_provenance() -> PublicSourceProvenance:
    """返回无 fallback 证据时的安全默认公共 provenance。

    Args:
        无。

    Returns:
        `not_applicable` 状态的公共 provenance；用于测试 fixture 与旧调用方默认值。

    Raises:
        无显式抛出。
    """

    return PublicSourceProvenance(
        source_provenance_schema_version=PUBLIC_SOURCE_PROVENANCE_SCHEMA_VERSION,
        source_strategy=LEGACY_OR_UNKNOWN_SOURCE_STRATEGY,
        selected_source=None,
        source_mode=LEGACY_OR_UNKNOWN_SOURCE_STRATEGY,
        fallback_enabled=None,
        resolved_source_name=None,
        fallback_used=False,
        primary_failure_category=None,
        fallback_eligibility="not_applicable",
        source_provenance_status="not_applicable",
        source_provenance_reason=SOURCE_PROVENANCE_REASON_SOURCE_METADATA_ABSENT,
    )


def project_public_source_provenance(
    source_metadata: AnnualReportSourceMetadata | None,
    *,
    primary_failure_category: PrimaryFailureCategory | None = None,
) -> PublicSourceProvenance:
    """把年报仓库来源元数据投影为公共 provenance。

    Args:
        source_metadata: `ParsedAnnualReport.metadata.source` 暴露的来源元数据。
        primary_failure_category: 显式传入的主来源失败分类；生产路径优先使用元数据字段。

    Returns:
        可写入公共 snapshot / summary 的稳定 provenance。

    Raises:
        无显式抛出。
    """

    if source_metadata is None:
        return default_public_source_provenance()

    resolved_source_name = _resolved_source_name(source_metadata.source)
    selected_source = _selected_source_name(source_metadata.selected_source)
    source_mode = _source_mode(source_metadata.source_mode)
    fallback_enabled = _fallback_enabled(source_metadata.fallback_enabled)
    source_strategy = source_mode
    if not source_metadata.fallback_used:
        return PublicSourceProvenance(
            source_provenance_schema_version=PUBLIC_SOURCE_PROVENANCE_SCHEMA_VERSION,
            source_strategy=source_strategy,
            selected_source=selected_source,
            source_mode=source_mode,
            fallback_enabled=fallback_enabled,
            resolved_source_name=resolved_source_name,
            fallback_used=False,
            primary_failure_category=None,
            fallback_eligibility="not_applicable",
            source_provenance_status="not_applicable",
            source_provenance_reason=SOURCE_PROVENANCE_REASON_PRIMARY_NO_FALLBACK,
        )

    effective_category = (
        source_metadata.primary_failure_category
        if source_metadata.primary_failure_category is not None
        else primary_failure_category
    )

    if effective_category in _ELIGIBLE_FAILURE_CATEGORIES:
        return PublicSourceProvenance(
            source_provenance_schema_version=PUBLIC_SOURCE_PROVENANCE_SCHEMA_VERSION,
            source_strategy=source_strategy,
            selected_source=selected_source,
            source_mode=source_mode,
            fallback_enabled=fallback_enabled,
            resolved_source_name=resolved_source_name,
            fallback_used=True,
            primary_failure_category=effective_category,
            fallback_eligibility="eligible",
            source_provenance_status="complete",
            source_provenance_reason=SOURCE_PROVENANCE_REASON_FALLBACK_ELIGIBLE,
        )
    if effective_category in _FAIL_CLOSED_FAILURE_CATEGORIES:
        return PublicSourceProvenance(
            source_provenance_schema_version=PUBLIC_SOURCE_PROVENANCE_SCHEMA_VERSION,
            source_strategy=source_strategy,
            selected_source=selected_source,
            source_mode=source_mode,
            fallback_enabled=fallback_enabled,
            resolved_source_name=resolved_source_name,
            fallback_used=True,
            primary_failure_category=effective_category,
            fallback_eligibility="fail_closed",
            source_provenance_status="incomplete",
            source_provenance_reason=SOURCE_PROVENANCE_REASON_FALLBACK_FAIL_CLOSED,
        )
    return PublicSourceProvenance(
        source_provenance_schema_version=PUBLIC_SOURCE_PROVENANCE_SCHEMA_VERSION,
        source_strategy=source_strategy,
        selected_source=selected_source,
        source_mode=source_mode,
        fallback_enabled=fallback_enabled,
        resolved_source_name=resolved_source_name,
        fallback_used=True,
        primary_failure_category=None,
        fallback_eligibility="unknown_public_metadata_absent",
        source_provenance_status="incomplete",
        source_provenance_reason=SOURCE_PROVENANCE_REASON_FALLBACK_CATEGORY_ABSENT,
    )


def source_provenance_to_dict(provenance: PublicSourceProvenance) -> dict[str, object]:
    """把公共 provenance 转为 JSON 兼容字典。

    Args:
        provenance: 公共来源 provenance。

    Returns:
        可直接写入 JSON 的字典。

    Raises:
        无显式抛出。
    """

    return asdict(provenance)


def _resolved_source_name(source_name: object) -> ResolvedSourceName | None:
    """把来源名限制在公共稳定枚举内。

    Args:
        source_name: 仓库来源元数据中的原始来源名。

    Returns:
        `eid`、`eastmoney` 或 `None`。

    Raises:
        无显式抛出。
    """

    if source_name in {"eid", "eastmoney"}:
        return source_name  # type: ignore[return-value]
    return None


def _selected_source_name(source_name: object) -> SelectedSourceName | None:
    """把策略选中来源限制在公共稳定枚举内。

    Args:
        source_name: 仓库来源元数据中的 `selected_source`。

    Returns:
        `eid`、`eastmoney` 或 `None`；不会从 resolved source 间接推断。

    Raises:
        无显式抛出。
    """

    if source_name in {"eid", "eastmoney"}:
        return source_name  # type: ignore[return-value]
    return None


def _source_mode(source_mode: object) -> SourceMode:
    """投影公共来源模式。

    Args:
        source_mode: 仓库来源元数据中的 `source_mode`。

    Returns:
        当前 `single_source_only` 或旧元数据的 `legacy_or_unknown`。

    Raises:
        无显式抛出。
    """

    if source_mode == CURRENT_SOURCE_STRATEGY:
        return CURRENT_SOURCE_STRATEGY
    return LEGACY_OR_UNKNOWN_SOURCE_STRATEGY


def _fallback_enabled(fallback_enabled: object) -> bool | None:
    """投影公共 fallback 开关。

    Args:
        fallback_enabled: 仓库来源元数据中的 `fallback_enabled`。

    Returns:
        布尔值；旧元数据缺失时为 `None`。

    Raises:
        无显式抛出。
    """

    if isinstance(fallback_enabled, bool):
        return fallback_enabled
    return None
