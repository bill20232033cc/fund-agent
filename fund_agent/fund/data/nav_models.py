"""NAV 数据源 typed contract 模型。

本模块定义基金净值数据进入后续路径型指标前必须满足的纯数据契约。它位于
Agent 层 Fund data 包内，只描述 NAV source adapter 与 repository 之间的
稳定 typed 边界，不读取缓存、不访问网络，也不参与报告渲染。

基金分析中净值路径主要服务模板第 2 章「R=A+B-C」和第 6 章「核心风险」的
回撤、收益归因证据。这里的校验目标是 fail-closed：当 source identity、
调整基础或完整性无法证明时，不构造可被强证据消费的成功 series。
"""

from __future__ import annotations

from dataclasses import InitVar, dataclass, field
from datetime import date, datetime
from decimal import Decimal
from types import MappingProxyType
from typing import Literal, Mapping


NavType = Literal[
    "unit_nav",
    "accumulated_nav",
    "adjusted_nav",
    "total_return_index",
    "unknown",
]
AdjustmentBasis = Literal[
    "raw_unit_nav",
    "accumulated_nav",
    "dividend_adjusted_nav",
    "total_return",
    "unknown",
]
DividendAdjustmentStatus = Literal[
    "not_adjusted",
    "adjusted",
    "unknown",
    "not_applicable",
]
NavIdentityStatus = Literal[
    "verified",
    "requested_code_only",
    "identity_mismatch",
    "unknown",
]
NavCompletenessStatus = Literal[
    "complete_enough",
    "missing_date_range",
    "insufficient_records",
    "unchecked",
]
NavFailureCategory = Literal[
    "not_found",
    "unavailable",
    "schema_drift",
    "identity_mismatch",
    "integrity_error",
    "adjustment_basis_unknown",
    "missing_date_range",
    "insufficient_records",
]

_ALLOWED_ADJUSTMENT_BASIS_BY_NAV_TYPE: Mapping[NavType, frozenset[AdjustmentBasis]] = {
    "unit_nav": frozenset({"raw_unit_nav"}),
    "accumulated_nav": frozenset({"accumulated_nav"}),
    "adjusted_nav": frozenset({"dividend_adjusted_nav"}),
    "total_return_index": frozenset({"total_return"}),
    "unknown": frozenset(),
}


class NavDataContractError(Exception):
    """NAV 数据契约错误。

    该异常用于所有 fail-closed 路径，调用方必须根据 `category` 决定是否允许
    fallback。NAV data 层的失败类别与年报 document source 类别保持语义对齐，
    但不依赖 document 层类型。
    """

    __slots__ = ("category", "message", "source", "fund_code", "cause")

    def __init__(
        self,
        *,
        category: NavFailureCategory,
        message: str,
        source: str | None = None,
        fund_code: str | None = None,
        cause: Exception | None = None,
    ) -> None:
        """初始化 NAV 数据契约错误。

        Args:
            category: 失败分类，用于 repository/source fallback 决策。
            message: 面向开发者的错误说明。
            source: 触发错误的数据源名称；未知时为空。
            fund_code: 触发错误的基金代码；未知时为空。
            cause: 原始异常；无原始异常时为空。

        Returns:
            无返回值。

        Raises:
            无显式抛出。
        """

        super().__init__(message)
        self.category = category
        self.message = message
        self.source = source
        self.fund_code = fund_code
        self.cause = cause


NavContractError = NavDataContractError


@dataclass(frozen=True, slots=True, kw_only=True)
class NavSourceMetadata:
    """NAV source 元数据。

    该模型只记录 source adapter 可证明的来源信息。成功 `FundNavSeries` 的
    `failure_category` 默认为 `None`；非空值保留给后续 fallback/diagnostic
    场景表达曾发生但未成为最终 fail-closed 的来源失败。
    """

    source_name: str
    origin_source: str
    source_id: str | None
    source_url: str | None
    cached: bool
    retrieved_at: datetime | None
    cache_updated_at: datetime | None
    requested_fund_code: str
    returned_fund_code: str | None
    returned_fund_name: str | None
    failure_category: NavFailureCategory | None = None


@dataclass(frozen=True, slots=True, kw_only=True)
class ShareClassMapping:
    """份额类别映射结果。

    `mapping_evidence` 使用显式字符串元组，避免 data 层反向依赖年报 extractor
    的 EvidenceAnchor 类型。该模型用于说明 requested fund code 如何映射到
    resolved fund code/share class，供模板第 2 章收益归因与第 6 章风险证据追溯。
    """

    requested_fund_code: str
    requested_share_class: str | None
    resolved_fund_code: str
    resolved_share_class: str
    mapping_status: str
    identity_status: NavIdentityStatus
    mapping_evidence: tuple[str, ...]

    def __post_init__(self) -> None:
        """规范化份额映射证据。

        Args:
            无。

        Returns:
            无返回值。

        Raises:
            无显式抛出。
        """

        object.__setattr__(self, "mapping_evidence", tuple(self.mapping_evidence))


@dataclass(frozen=True, slots=True, kw_only=True)
class FundNavRecord:
    """单日基金 NAV 记录。

    `raw_payload` 仅供 diagnostics/debugging 使用，生产 consumer 尤其是后续
    drawdown metric 不得读取它来绕过 `nav_type`、`adjusted_basis`、
    `raw_change_rate` 等 typed 字段。
    """

    date: date
    share_class: str
    nav_value: Decimal
    nav_type: NavType
    adjusted_basis: AdjustmentBasis
    raw_change_rate: Decimal | None
    raw_payload: Mapping[str, object] = field(
        compare=False,
        metadata={
            "doc": (
                "仅供 diagnostics/debugging；生产 consumer 不得读取 raw_payload "
                "绕过 typed NAV 字段。"
            )
        },
    )

    def __post_init__(self) -> None:
        """冻结原始 payload 快照。

        Args:
            无。

        Returns:
            无返回值。

        Raises:
            无显式抛出。
        """

        object.__setattr__(self, "raw_payload", MappingProxyType(dict(self.raw_payload)))


@dataclass(frozen=True, slots=True, kw_only=True)
class FundNavSeries:
    """基金 NAV 序列 typed contract。

    该模型是后续路径型指标的强证据入口。构造时会验证份额、source identity、
    NAV 类型与调整基础、记录完整性和强回撤证据资格；无法证明的场景会抛出
    `NavDataContractError`，避免半有效 series 进入模板第 6 章风险分析。
    """

    fund_code: str
    share_class: str
    records: tuple[FundNavRecord, ...]
    nav_type: NavType
    adjusted_basis: AdjustmentBasis
    dividend_adjustment_status: DividendAdjustmentStatus
    identity_status: NavIdentityStatus
    completeness_status: NavCompletenessStatus
    strong_drawdown_evidence_eligible: bool
    strong_drawdown_ineligibility_reason: str | None
    source: NavSourceMetadata
    share_class_mapping: ShareClassMapping
    date_range_start: date | None
    date_range_end: date | None
    record_count: int
    requested_start_date: InitVar[date | None] = None
    requested_end_date: InitVar[date | None] = None
    minimum_records: InitVar[int | None] = None

    def __post_init__(
        self,
        requested_start_date: date | None,
        requested_end_date: date | None,
        minimum_records: int | None,
    ) -> None:
        """验证并规范化 NAV 序列契约。

        Args:
            requested_start_date: 调用方要求覆盖的起始日期；未传表示不检查日期范围。
            requested_end_date: 调用方要求覆盖的结束日期；未传表示不检查日期范围。
            minimum_records: 调用方要求的最少记录数；未传表示不检查记录数量阈值。

        Returns:
            无返回值。

        Raises:
            NavDataContractError: 当记录完整性、身份、调整基础或完整性约束不满足时抛出。
        """

        records = tuple(self.records)
        object.__setattr__(self, "records", records)

        _validate_nav_type_adjustment_basis(
            nav_type=self.nav_type,
            adjusted_basis=self.adjusted_basis,
            source=self.source.source_name,
            fund_code=self.fund_code,
        )
        _validate_record_shape(series=self, records=records)
        _validate_identity(series=self)
        _apply_date_range_defaults(series=self, records=records)
        _apply_completeness_status(
            series=self,
            records=records,
            requested_start_date=requested_start_date,
            requested_end_date=requested_end_date,
            minimum_records=minimum_records,
        )
        _apply_strong_drawdown_eligibility(series=self)


def _raise_contract_error(
    *,
    category: NavFailureCategory,
    message: str,
    source: str | None,
    fund_code: str | None,
) -> None:
    """抛出 NAV 数据契约错误。

    Args:
        category: 失败分类。
        message: 错误说明。
        source: 数据源名称；未知时为空。
        fund_code: 基金代码；未知时为空。

    Returns:
        无返回值。

    Raises:
        NavDataContractError: 始终抛出，用于 fail-closed。
    """

    raise NavDataContractError(
        category=category,
        message=message,
        source=source,
        fund_code=fund_code,
    )


def _validate_nav_type_adjustment_basis(
    *,
    nav_type: NavType,
    adjusted_basis: AdjustmentBasis,
    source: str | None,
    fund_code: str | None,
) -> None:
    """验证 NAV 类型与调整基础兼容矩阵。

    Args:
        nav_type: source 声称的 NAV 数学形态。
        adjusted_basis: 本系统判定的调整基础。
        source: 数据源名称；未知时为空。
        fund_code: 基金代码；未知时为空。

    Returns:
        无返回值。

    Raises:
        NavDataContractError: 当调整基础未知或组合不兼容时抛出。
    """

    if adjusted_basis == "unknown":
        _raise_contract_error(
            category="adjustment_basis_unknown",
            message="NAV adjusted_basis 为 unknown，不能构造成功 series。",
            source=source,
            fund_code=fund_code,
        )
    if nav_type == "unknown":
        _raise_contract_error(
            category="schema_drift",
            message="NAV nav_type 为 unknown，不能构造成功 series。",
            source=source,
            fund_code=fund_code,
        )

    allowed_adjustment_basis = _ALLOWED_ADJUSTMENT_BASIS_BY_NAV_TYPE[nav_type]
    if adjusted_basis not in allowed_adjustment_basis:
        _raise_contract_error(
            category="schema_drift",
            message=f"NAV 类型 {nav_type} 与调整基础 {adjusted_basis} 不兼容。",
            source=source,
            fund_code=fund_code,
        )


def _validate_record_shape(
    *,
    series: FundNavSeries,
    records: tuple[FundNavRecord, ...],
) -> None:
    """验证 NAV 记录形态与 series-level 字段一致。

    Args:
        series: 待验证的 NAV 序列。
        records: 已规范为 tuple 的 NAV 记录。

    Returns:
        无返回值。

    Raises:
        NavDataContractError: 当记录为空、计数不匹配、日期重复或字段不一致时抛出。
    """

    if not records:
        _raise_contract_error(
            category="not_found",
            message="NAV records 为空，不能构造成功 series。",
            source=series.source.source_name,
            fund_code=series.fund_code,
        )
    if series.record_count != len(records):
        _raise_contract_error(
            category="integrity_error",
            message="NAV record_count 与 records 长度不一致。",
            source=series.source.source_name,
            fund_code=series.fund_code,
        )

    seen_dates: set[date] = set()
    for record in records:
        if record.date in seen_dates:
            _raise_contract_error(
                category="integrity_error",
                message=f"NAV records 出现重复日期 {record.date.isoformat()}。",
                source=series.source.source_name,
                fund_code=series.fund_code,
            )
        seen_dates.add(record.date)

        if record.share_class != series.share_class:
            # series identity 已在 source/share mapping 层表达；单条记录份额串线代表
            # 同一 series 内部数据完整性破坏，因此归类为 integrity_error。
            _raise_contract_error(
                category="integrity_error",
                message="NAV record share_class 与 series share_class 不一致。",
                source=series.source.source_name,
                fund_code=series.fund_code,
            )
        if record.nav_type != series.nav_type or record.adjusted_basis != series.adjusted_basis:
            _raise_contract_error(
                category="integrity_error",
                message="NAV record 类型字段与 series 类型字段不一致。",
                source=series.source.source_name,
                fund_code=series.fund_code,
            )


def _validate_identity(*, series: FundNavSeries) -> None:
    """验证 NAV source identity。

    Args:
        series: 待验证的 NAV 序列。

    Returns:
        无返回值。

    Raises:
        NavDataContractError: 当身份已知不匹配时抛出。
    """

    if series.identity_status == "identity_mismatch":
        _raise_contract_error(
            category="identity_mismatch",
            message="NAV source returned identity 与 requested fund identity 不匹配。",
            source=series.source.source_name,
            fund_code=series.fund_code,
        )


def _apply_date_range_defaults(
    *,
    series: FundNavSeries,
    records: tuple[FundNavRecord, ...],
) -> None:
    """填充 NAV 序列实际日期范围。

    Args:
        series: 待规范化的 NAV 序列。
        records: 已规范为 tuple 的 NAV 记录。

    Returns:
        无返回值。

    Raises:
        无显式抛出。
    """

    record_dates = tuple(record.date for record in records)
    if series.date_range_start is None:
        object.__setattr__(series, "date_range_start", min(record_dates))
    if series.date_range_end is None:
        object.__setattr__(series, "date_range_end", max(record_dates))


def _apply_completeness_status(
    *,
    series: FundNavSeries,
    records: tuple[FundNavRecord, ...],
    requested_start_date: date | None,
    requested_end_date: date | None,
    minimum_records: int | None,
) -> None:
    """应用日期范围和记录数完整性约束。

    Args:
        series: 待规范化的 NAV 序列。
        records: 已规范为 tuple 的 NAV 记录。
        requested_start_date: 调用方要求覆盖的起始日期；未传表示不检查。
        requested_end_date: 调用方要求覆盖的结束日期；未传表示不检查。
        minimum_records: 调用方要求的最少记录数；未传表示不检查。

    Returns:
        无返回值。

    Raises:
        NavDataContractError: 当日期范围或记录数不满足显式约束时抛出。
    """

    has_constraints = any(
        constraint is not None
        for constraint in (requested_start_date, requested_end_date, minimum_records)
    )
    if not has_constraints:
        object.__setattr__(series, "completeness_status", "unchecked")
        return

    if minimum_records is not None and len(records) < minimum_records:
        _raise_contract_error(
            category="insufficient_records",
            message="NAV records 数量不足，不能满足显式 minimum_records 约束。",
            source=series.source.source_name,
            fund_code=series.fund_code,
        )
    if requested_start_date is not None and series.date_range_start is not None:
        if series.date_range_start > requested_start_date:
            _raise_contract_error(
                category="missing_date_range",
                message="NAV records 未覆盖显式 requested_start_date。",
                source=series.source.source_name,
                fund_code=series.fund_code,
            )
    if requested_end_date is not None and series.date_range_end is not None:
        if series.date_range_end < requested_end_date:
            _raise_contract_error(
                category="missing_date_range",
                message="NAV records 未覆盖显式 requested_end_date。",
                source=series.source.source_name,
                fund_code=series.fund_code,
            )

    object.__setattr__(series, "completeness_status", "complete_enough")


def _apply_strong_drawdown_eligibility(*, series: FundNavSeries) -> None:
    """应用强回撤证据资格规则。

    Args:
        series: 待规范化的 NAV 序列。

    Returns:
        无返回值。

    Raises:
        无显式抛出。
    """

    reasons: list[str] = []
    if series.identity_status == "requested_code_only":
        reasons.append(
            "requested_code_only：source-returned identity 未验证，不能作为 strong drawdown evidence。"
        )
    elif series.identity_status != "verified":
        reasons.append("NAV source identity 未 verified，不能作为 strong drawdown evidence。")

    if series.adjusted_basis == "raw_unit_nav":
        reasons.append(
            "raw_unit_nav 未证明 dividend adjustment 或 total-return basis，不能作为 strong drawdown evidence。"
        )

    if reasons:
        object.__setattr__(series, "strong_drawdown_evidence_eligible", False)
        object.__setattr__(
            series,
            "strong_drawdown_ineligibility_reason",
            " ".join(reasons),
        )


__all__ = [
    "AdjustmentBasis",
    "DividendAdjustmentStatus",
    "FundNavRecord",
    "FundNavSeries",
    "NavCompletenessStatus",
    "NavContractError",
    "NavDataContractError",
    "NavFailureCategory",
    "NavIdentityStatus",
    "NavSourceMetadata",
    "NavType",
    "ShareClassMapping",
]
