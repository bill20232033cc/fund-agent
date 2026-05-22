"""自建温度计纯计算器。

本模块属于 Fund Capability analysis 层，负责 P19 自建温度计的 PE/PB
历史分位数和综合温度计算。它不读取 akshare、不访问缓存，也不决定 CLI 输出。
"""

from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
from typing import Final

from fund_agent.fund.data.thermometer_types import PePbHistory, ThermometerReading

LOW_THRESHOLD: Final[Decimal] = Decimal("30")
HIGH_THRESHOLD: Final[Decimal] = Decimal("70")
PERCENT_SCALE: Final[Decimal] = Decimal("100")
DISPLAY_QUANT: Final[Decimal] = Decimal("0.01")


class ThermometerCalculationError(ValueError):
    """温度计计算输入不满足契约。"""


def calculate_thermometer_reading(
    history: PePbHistory,
    *,
    cached: bool = False,
    stale: bool = False,
) -> ThermometerReading:
    """根据 PE/PB 历史序列计算温度计读数。

    Args:
        history: PE/PB 历史序列，必须按日期包含至少一个有效点。
        cached: 读数是否基于缓存数据。
        stale: 缓存数据是否 stale。

    Returns:
        温度计读数。

    Raises:
        ThermometerCalculationError: 历史序列为空或包含非法值时抛出。
    """

    if not history.points:
        raise ThermometerCalculationError("PE/PB 历史序列为空")

    pe_values = tuple(point.pe for point in history.points)
    pb_values = tuple(point.pb for point in history.points)
    _validate_values(pe_values, field_name="PE")
    _validate_values(pb_values, field_name="PB")

    current = history.points[-1]
    pe_percentile = percentile_rank(current.pe, pe_values)
    pb_percentile = percentile_rank(current.pb, pb_values)
    temperature = _quantize((pe_percentile + pb_percentile) / Decimal("2"))

    return ThermometerReading(
        index_code=history.index_code,
        index_name=history.index_name,
        temperature=temperature,
        pe_percentile=pe_percentile,
        pb_percentile=pb_percentile,
        valuation_state_candidate=_valuation_state(temperature),
        data_date=current.date,
        lookback_start=history.points[0].date,
        lookback_end=current.date,
        source=history.source,
        cached=cached,
        stale=stale,
        unavailable=False,
        unavailable_reason=None,
        fetched_at=history.fetched_at,
    )


def percentile_rank(value: Decimal, values: tuple[Decimal, ...]) -> Decimal:
    """计算值在历史序列中的百分位。

    Args:
        value: 当前值。
        values: 历史值序列。

    Returns:
        百分位，范围 0 到 100。

    Raises:
        ThermometerCalculationError: 历史序列为空时抛出。
    """

    if not values:
        raise ThermometerCalculationError("百分位计算需要至少一个历史值")

    less_or_equal_count = sum(1 for item in values if item <= value)
    percentile = Decimal(less_or_equal_count) / Decimal(len(values)) * PERCENT_SCALE
    return _quantize(percentile)


def _validate_values(values: tuple[Decimal, ...], *, field_name: str) -> None:
    """校验估值序列。

    Args:
        values: 待校验数值序列。
        field_name: 字段名称，用于错误信息。

    Returns:
        无返回值。

    Raises:
        ThermometerCalculationError: 序列为空或包含非正值时抛出。
    """

    if not values:
        raise ThermometerCalculationError(f"{field_name} 历史序列为空")
    if any(value <= 0 for value in values):
        raise ThermometerCalculationError(f"{field_name} 历史序列包含非正值")


def _valuation_state(temperature: Decimal) -> str:
    """根据温度映射估值状态候选。

    Args:
        temperature: 综合温度。

    Returns:
        `low`、`fair` 或 `high`。

    Raises:
        无显式抛出。
    """

    if temperature <= LOW_THRESHOLD:
        return "low"
    if temperature >= HIGH_THRESHOLD:
        return "high"
    return "fair"


def _quantize(value: Decimal) -> Decimal:
    """统一温度计小数位。

    Args:
        value: 原始 Decimal。

    Returns:
        保留两位小数的 Decimal。

    Raises:
        无显式抛出。
    """

    return value.quantize(DISPLAY_QUANT, rounding=ROUND_HALF_UP)
