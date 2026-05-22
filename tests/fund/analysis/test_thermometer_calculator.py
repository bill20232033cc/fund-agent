"""自建温度计计算器测试。"""

from __future__ import annotations

from decimal import Decimal

import pytest

from fund_agent.fund.analysis.thermometer_calculator import (
    ThermometerCalculationError,
    calculate_thermometer_reading,
    percentile_rank,
)
from fund_agent.fund.data.thermometer_types import PePbHistory, PePbPoint


def test_percentile_rank_uses_less_or_equal_count() -> None:
    """验证百分位按小于等于当前值的历史样本占比计算。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当百分位计算不符合契约时抛出。
    """

    result = percentile_rank(
        Decimal("20"),
        (Decimal("10"), Decimal("20"), Decimal("30"), Decimal("40")),
    )

    assert result == Decimal("50.00")


def test_calculate_thermometer_reading_maps_thresholds() -> None:
    """验证 PE/PB 分位、综合温度和估值状态映射。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当读数不符合预期时抛出。
    """

    history = PePbHistory(
        index_code="000300",
        index_name="沪深300",
        source="fixture",
        fetched_at="2026-05-23T00:00:00+00:00",
        points=(
            PePbPoint(date="2026-05-20", pe=Decimal("10"), pb=Decimal("1")),
            PePbPoint(date="2026-05-21", pe=Decimal("20"), pb=Decimal("2")),
            PePbPoint(date="2026-05-22", pe=Decimal("30"), pb=Decimal("3")),
        ),
    )

    reading = calculate_thermometer_reading(history)

    assert reading.index_code == "000300"
    assert reading.temperature == Decimal("100.00")
    assert reading.pe_percentile == Decimal("100.00")
    assert reading.pb_percentile == Decimal("100.00")
    assert reading.valuation_state_candidate == "high"
    assert reading.data_date == "2026-05-22"
    assert reading.lookback_start == "2026-05-20"


def test_calculate_thermometer_reading_rejects_empty_history() -> None:
    """验证空历史序列 fail-closed。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当空历史未被拒绝时抛出。
    """

    history = PePbHistory(index_code="000300", index_name="沪深300", points=(), source="fixture")

    with pytest.raises(ThermometerCalculationError, match="为空"):
        calculate_thermometer_reading(history)


def test_calculate_thermometer_reading_rejects_non_positive_values() -> None:
    """验证 PE/PB 非正值会被拒绝。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当非法估值未被拒绝时抛出。
    """

    history = PePbHistory(
        index_code="000300",
        index_name="沪深300",
        source="fixture",
        points=(
            PePbPoint(date="2026-05-20", pe=Decimal("0"), pb=Decimal("1")),
            PePbPoint(date="2026-05-21", pe=Decimal("20"), pb=Decimal("2")),
        ),
    )

    with pytest.raises(ThermometerCalculationError, match="非正值"):
        calculate_thermometer_reading(history)
