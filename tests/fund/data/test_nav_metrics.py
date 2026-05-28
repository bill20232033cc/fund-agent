"""NAV 路径型指标测试。"""

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from decimal import Decimal

import pytest

from fund_agent.fund.data.nav_metrics import (
    calculate_max_drawdown_from_nav_series,
    format_max_drawdown_percent,
)
from fund_agent.fund.data.nav_models import (
    FundNavRecord,
    FundNavSeries,
    NavDataContractError,
    NavSourceMetadata,
    ShareClassMapping,
)


def test_calculate_max_drawdown_from_accumulated_nav_path() -> None:
    """验证累计净值路径最大回撤公式、峰值和谷值日期，见模板第 6 章“核心风险”。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当最大回撤结果与预期不一致时抛出。
    """

    series = _series(
        (
            (date(2024, 1, 2), Decimal("1.00")),
            (date(2024, 1, 3), Decimal("1.10")),
            (date(2024, 1, 4), Decimal("1.05")),
            (date(2024, 1, 5), Decimal("1.20")),
            (date(2024, 1, 8), Decimal("1.08")),
        )
    )

    metric = calculate_max_drawdown_from_nav_series(
        series,
        period_start=date(2024, 1, 1),
        period_end=date(2024, 12, 31),
        minimum_records=5,
    )

    assert metric.max_drawdown_ratio == Decimal("-0.1")
    assert metric.peak_date == date(2024, 1, 5)
    assert metric.peak_value == Decimal("1.20")
    assert metric.trough_date == date(2024, 1, 8)
    assert metric.trough_value == Decimal("1.08")
    assert metric.record_count == 5
    assert format_max_drawdown_percent(metric.max_drawdown_ratio) == "-10.00%"


def test_calculate_max_drawdown_monotonic_path_is_zero() -> None:
    """验证单调上涨累计净值路径的最大回撤为零。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当单调路径产生负回撤时抛出。
    """

    series = _series(
        (
            (date(2024, 1, 2), Decimal("1.00")),
            (date(2024, 1, 3), Decimal("1.01")),
            (date(2024, 1, 4), Decimal("1.02")),
        )
    )

    metric = calculate_max_drawdown_from_nav_series(
        series,
        period_start=date(2024, 1, 1),
        period_end=date(2024, 12, 31),
        minimum_records=3,
    )

    assert metric.max_drawdown_ratio == Decimal("0")
    assert metric.peak_date == date(2024, 1, 2)
    assert metric.trough_date == date(2024, 1, 2)


def test_period_filtered_records_are_checked_independently() -> None:
    """验证 helper 独立检查 period-filtered 记录数，不依赖 repository 全序列阈值。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当期内记录不足未失败关闭时抛出。
    """

    points = tuple(
        (date(2023, 1, 2) + timedelta(days=index), Decimal("1.00") + Decimal(index) / Decimal("1000"))
        for index in range(30)
    )
    series = _series(points)

    with pytest.raises(NavDataContractError) as exc_info:
        calculate_max_drawdown_from_nav_series(
            series,
            period_start=date(2024, 1, 1),
            period_end=date(2024, 12, 31),
            minimum_records=1,
        )

    assert exc_info.value.category == "insufficient_records"


def test_calculate_max_drawdown_rejects_duplicate_dates() -> None:
    """验证重复日期在指标层按完整性错误失败关闭。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当重复日期未被拒绝时抛出。
    """

    series = _series(
        (
            (date(2024, 1, 2), Decimal("1.00")),
            (date(2024, 1, 3), Decimal("1.02")),
        )
    )
    duplicate_records = (*series.records, _record(date(2024, 1, 3), Decimal("1.01")))
    object.__setattr__(series, "records", duplicate_records)
    object.__setattr__(series, "record_count", len(duplicate_records))

    with pytest.raises(NavDataContractError) as exc_info:
        calculate_max_drawdown_from_nav_series(
            series,
            period_start=date(2024, 1, 1),
            period_end=date(2024, 12, 31),
            minimum_records=1,
        )

    assert exc_info.value.category == "integrity_error"


def test_calculate_max_drawdown_rejects_non_positive_nav() -> None:
    """验证非正累计净值在指标层按完整性错误失败关闭。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当非正 NAV 未被拒绝时抛出。
    """

    series = _series(
        (
            (date(2024, 1, 2), Decimal("1.00")),
            (date(2024, 1, 3), Decimal("1.01")),
        )
    )
    bad_records = (series.records[0], _record(date(2024, 1, 3), Decimal("0")))
    object.__setattr__(series, "records", bad_records)

    with pytest.raises(NavDataContractError) as exc_info:
        calculate_max_drawdown_from_nav_series(
            series,
            period_start=date(2024, 1, 1),
            period_end=date(2024, 12, 31),
            minimum_records=1,
        )

    assert exc_info.value.category == "integrity_error"


def test_calculate_max_drawdown_rejects_raw_unit_or_ineligible_series() -> None:
    """验证 raw_unit_nav 或非强证据资格 series 不会生成模板第 6 章强回撤指标。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当不合格 series 被接受时抛出。
    """

    series = _series(
        (
            (date(2024, 1, 2), Decimal("1.00")),
            (date(2024, 1, 3), Decimal("1.01")),
        )
    )
    object.__setattr__(series, "nav_type", "unit_nav")
    object.__setattr__(series, "adjusted_basis", "raw_unit_nav")
    object.__setattr__(series, "strong_drawdown_evidence_eligible", False)

    with pytest.raises(NavDataContractError) as exc_info:
        calculate_max_drawdown_from_nav_series(
            series,
            period_start=date(2024, 1, 1),
            period_end=date(2024, 12, 31),
            minimum_records=1,
        )

    assert exc_info.value.category == "adjustment_basis_unknown"


def _series(points: tuple[tuple[date, Decimal], ...]) -> FundNavSeries:
    """构造累计净值 typed series fixture。

    Args:
        points: 日期与累计净值点。

    Returns:
        可用于指标测试的 `FundNavSeries`。

    Raises:
        NavDataContractError: 当 fixture 自身不满足 typed contract 时抛出。
    """

    records = tuple(_record(record_date, value) for record_date, value in points)
    return FundNavSeries(
        fund_code="006597",
        share_class="A",
        records=records,
        nav_type="accumulated_nav",
        adjusted_basis="accumulated_nav",
        dividend_adjustment_status="not_applicable",
        identity_status="verified",
        completeness_status="complete_enough",
        strong_drawdown_evidence_eligible=True,
        strong_drawdown_ineligibility_reason=None,
        source=_source(),
        share_class_mapping=_mapping(),
        date_range_start=min(record.date for record in records),
        date_range_end=max(record.date for record in records),
        record_count=len(records),
    )


def _record(record_date: date, value: Decimal) -> FundNavRecord:
    """构造单日累计净值记录 fixture。

    Args:
        record_date: 净值日期。
        value: 累计净值。

    Returns:
        `FundNavRecord` fixture。

    Raises:
        无显式抛出。
    """

    return FundNavRecord(
        date=record_date,
        share_class="A",
        nav_value=value,
        nav_type="accumulated_nav",
        adjusted_basis="accumulated_nav",
        raw_change_rate=None,
        raw_payload={},
    )


def _source() -> NavSourceMetadata:
    """构造 NAV 来源元数据 fixture。

    Args:
        无。

    Returns:
        `NavSourceMetadata` fixture。

    Raises:
        无显式抛出。
    """

    return NavSourceMetadata(
        source_name="csrc_eid",
        origin_source="csrc_eid",
        source_id="5755:2030-1010",
        source_url="https://eid.csrc.gov.cn/fund/5755",
        cached=False,
        retrieved_at=datetime(2026, 5, 29, tzinfo=timezone.utc),
        cache_updated_at=None,
        requested_fund_code="006597",
        returned_fund_code="006597",
        returned_fund_name="国泰利享中短债债券A",
        source_query_params=(("fund_code", "006597"), ("share_class", "A")),
    )


def _mapping() -> ShareClassMapping:
    """构造份额类别映射 fixture。

    Args:
        无。

    Returns:
        `ShareClassMapping` fixture。

    Raises:
        无显式抛出。
    """

    return ShareClassMapping(
        requested_fund_code="006597",
        requested_share_class="A",
        resolved_fund_code="006597",
        resolved_share_class="A",
        mapping_status="verified",
        identity_status="verified",
        mapping_evidence=("fixture",),
    )
