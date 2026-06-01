"""NAV 派生风险指标。

本模块位于 Agent 层 Fund data 包，只消费 `FundNavSeries` typed contract，
不读取外部 source、缓存或年报文件。当前实现模板第 6 章“核心风险”所需的
累计净值路径最大回撤；波动率不是本模块当前目标。
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Final, Literal

from fund_agent.fund.data.nav_models import (
    AdjustmentBasis,
    DividendAdjustmentStatus,
    FundNavRecord,
    FundNavSeries,
    NavDataContractError,
    NavIdentityStatus,
    NavSourceMetadata,
    NavType,
)

_REQUIRED_NAV_TYPE: Final[NavType] = "accumulated_nav"
_REQUIRED_ADJUSTED_BASIS: Final[AdjustmentBasis] = "accumulated_nav"
_REQUIRED_IDENTITY_STATUS: Final[NavIdentityStatus] = "verified"
_CALCULATION_METHOD: Final[Literal["max_drawdown_on_accumulated_nav_path"]] = (
    "max_drawdown_on_accumulated_nav_path"
)
_PERCENT_QUANT: Final[Decimal] = Decimal("0.01")


@dataclass(frozen=True, slots=True, kw_only=True)
class NavMaxDrawdownMetric:
    """NAV 最大回撤派生指标。

    Attributes:
        fund_code: 基金代码。
        share_class: 份额类别。
        period_start: 指标期起点，含当日。
        period_end: 指标期终点，含当日。
        record_count: 指标期内净值记录数。
        max_drawdown_ratio: 最大回撤比例；负数表示从峰值到谷值的跌幅。
        peak_date: 最大回撤对应峰值日期。
        peak_value: 最大回撤对应峰值累计净值。
        trough_date: 最大回撤对应谷值日期。
        trough_value: 最大回撤对应谷值累计净值。
        calculation_method: 固定计算方法标识。
        source: NAV 来源元数据。
        nav_type: NAV 数学形态。
        adjusted_basis: NAV 调整基础。
        dividend_adjustment_status: 分红调整状态。
        identity_status: source identity 状态。
    """

    fund_code: str
    share_class: str
    period_start: date
    period_end: date
    record_count: int
    max_drawdown_ratio: Decimal
    peak_date: date
    peak_value: Decimal
    trough_date: date
    trough_value: Decimal
    calculation_method: Literal["max_drawdown_on_accumulated_nav_path"]
    source: NavSourceMetadata
    nav_type: NavType
    adjusted_basis: AdjustmentBasis
    dividend_adjustment_status: DividendAdjustmentStatus
    identity_status: NavIdentityStatus


def calculate_max_drawdown_from_nav_series(
    series: FundNavSeries,
    *,
    period_start: date,
    period_end: date,
    minimum_records: int,
) -> NavMaxDrawdownMetric:
    """按累计净值路径计算最大回撤，见模板第 6 章“核心风险”。

    Args:
        series: 已通过 typed repository 构造的 NAV 序列。
        period_start: 指标期起点，含当日。
        period_end: 指标期终点，含当日。
        minimum_records: 指标期过滤后的最少记录数。

    Returns:
        最大回撤派生指标。

    Raises:
        NavDataContractError: 当 series 类型、身份、强证据资格、期内样本或数值完整性
            不满足强回撤证据要求时抛出。
    """

    _validate_metric_request(series, period_start, period_end, minimum_records)
    period_records = _period_records(series, period_start=period_start, period_end=period_end)
    _validate_period_records(series, period_records, minimum_records)

    first = period_records[0]
    peak_record = first
    max_drawdown = Decimal("0")
    max_peak_record = first
    trough_record = first

    for record in period_records:
        if record.nav_value > peak_record.nav_value:
            peak_record = record
        drawdown = record.nav_value / peak_record.nav_value - Decimal("1")
        # 相同最大回撤保留最早谷值，避免后续同值覆盖已审计日期。
        if drawdown < max_drawdown:
            max_drawdown = drawdown
            max_peak_record = peak_record
            trough_record = record

    return NavMaxDrawdownMetric(
        fund_code=series.fund_code,
        share_class=series.share_class,
        period_start=period_start,
        period_end=period_end,
        record_count=len(period_records),
        max_drawdown_ratio=max_drawdown,
        peak_date=max_peak_record.date,
        peak_value=max_peak_record.nav_value,
        trough_date=trough_record.date,
        trough_value=trough_record.nav_value,
        calculation_method=_CALCULATION_METHOD,
        source=series.source,
        nav_type=series.nav_type,
        adjusted_basis=series.adjusted_basis,
        dividend_adjustment_status=series.dividend_adjustment_status,
        identity_status=series.identity_status,
    )


def format_max_drawdown_percent(value: Decimal) -> str:
    """把最大回撤比例格式化为百分比文本。

    Args:
        value: 比例值，例如 `Decimal("-0.0123")`。

    Returns:
        两位小数百分比文本，例如 `-1.23%`。

    Raises:
        无显式抛出。
    """

    return f"{(value * Decimal('100')).quantize(_PERCENT_QUANT)}%"


def _validate_metric_request(
    series: FundNavSeries,
    period_start: date,
    period_end: date,
    minimum_records: int,
) -> None:
    """校验最大回撤指标请求和 series 资格。

    Args:
        series: NAV 序列。
        period_start: 指标期起点。
        period_end: 指标期终点。
        minimum_records: 期内最少记录数。

    Returns:
        无返回值。

    Raises:
        NavDataContractError: 当请求或 series 不满足强回撤证据要求时抛出。
    """

    if period_start > period_end:
        _raise_metric_error(
            series=series,
            category="missing_date_range",
            message="最大回撤指标 period_start 不得晚于 period_end。",
        )
    if minimum_records < 1:
        _raise_metric_error(
            series=series,
            category="schema_drift",
            message="最大回撤指标 minimum_records 必须为正整数。",
        )
    if series.nav_type != _REQUIRED_NAV_TYPE or series.adjusted_basis != _REQUIRED_ADJUSTED_BASIS:
        _raise_metric_error(
            series=series,
            category="adjustment_basis_unknown",
            message=(
                "最大回撤指标只接受 accumulated_nav/accumulated_nav typed series，"
                f"实际为 {series.nav_type}/{series.adjusted_basis}。"
            ),
        )
    if series.identity_status != _REQUIRED_IDENTITY_STATUS:
        _raise_metric_error(
            series=series,
            category="identity_mismatch",
            message=f"最大回撤指标要求 verified identity，实际为 {series.identity_status}。",
        )
    if series.strong_drawdown_evidence_eligible is not True:
        _raise_metric_error(
            series=series,
            category="adjustment_basis_unknown",
            message=series.strong_drawdown_ineligibility_reason
            or "NAV series 不具备 strong drawdown evidence 资格。",
        )


def _period_records(
    series: FundNavSeries,
    *,
    period_start: date,
    period_end: date,
) -> tuple[FundNavRecord, ...]:
    """按指标期过滤并排序 NAV 记录。

    Args:
        series: NAV 序列。
        period_start: 指标期起点。
        period_end: 指标期终点。

    Returns:
        期内按日期升序排列的记录。

    Raises:
        无显式抛出。
    """

    return tuple(
        sorted(
            (
                record
                for record in series.records
                if period_start <= record.date <= period_end
            ),
            key=lambda record: record.date,
        )
    )


def _validate_period_records(
    series: FundNavSeries,
    records: tuple[FundNavRecord, ...],
    minimum_records: int,
) -> None:
    """校验指标期内记录完整性。

    Args:
        series: NAV 序列。
        records: 期内记录。
        minimum_records: 期内最少记录数。

    Returns:
        无返回值。

    Raises:
        NavDataContractError: 当期内记录不足、重复日期或 NAV 非正时抛出。
    """

    if len(records) < minimum_records:
        _raise_metric_error(
            series=series,
            category="insufficient_records",
            message="最大回撤指标期内 NAV records 数量不足。",
        )
    seen_dates: set[date] = set()
    for record in records:
        if record.date in seen_dates:
            _raise_metric_error(
                series=series,
                category="integrity_error",
                message=f"最大回撤指标期内 NAV records 出现重复日期 {record.date.isoformat()}。",
            )
        seen_dates.add(record.date)
        if record.nav_value <= 0:
            _raise_metric_error(
                series=series,
                category="integrity_error",
                message=f"最大回撤指标期内 NAV 非正：{record.date.isoformat()}。",
            )


def _raise_metric_error(
    *,
    series: FundNavSeries,
    category: str,
    message: str,
) -> None:
    """抛出 NAV 指标契约错误。

    Args:
        series: 当前 NAV 序列。
        category: `NavFailureCategory` 字符串。
        message: 错误说明。

    Returns:
        无返回值。

    Raises:
        NavDataContractError: 始终抛出，用于 fail-closed。
    """

    raise NavDataContractError(
        category=category,  # type: ignore[arg-type]
        message=message,
        source=series.source.source_name,
        fund_code=series.fund_code,
    )
