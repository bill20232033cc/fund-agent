"""自建温度计数据源测试。"""

from __future__ import annotations

import asyncio
from datetime import date
from decimal import Decimal

import pytest

from fund_agent.fund.data.thermometer_source import (
    AkshareIndexThermometerSource,
    ThermometerSourceError,
)


class _FakeFrame:
    """DataFrame-like 测试对象。"""

    def __init__(self, records: list[dict[str, object]]) -> None:
        """初始化 fake frame。

        Args:
            records: records 数据。

        Returns:
            无返回值。

        Raises:
            无显式抛出。
        """

        self._records = records

    def to_dict(self, *, orient: str) -> list[dict[str, object]]:
        """返回 records。

        Args:
            orient: 输出方向，必须为 `records`。

        Returns:
            records 数据。

        Raises:
            AssertionError: orient 不符合预期时抛出。
        """

        assert orient == "records"
        return self._records


class _RecordingFetcher:
    """记录 akshare symbol 的 fake fetcher。"""

    def __init__(self, records: list[dict[str, object]]) -> None:
        """初始化 fake fetcher。

        Args:
            records: 待返回的 records 数据。

        Returns:
            无返回值。

        Raises:
            无显式抛出。
        """

        self.records = records
        self.symbols: list[str] = []

    def __call__(self, symbol: str) -> _FakeFrame:
        """记录 symbol 并返回 fake frame。

        Args:
            symbol: akshare 指数名称。

        Returns:
            fake frame。

        Raises:
            无显式抛出。
        """

        self.symbols.append(symbol)
        return _FakeFrame(self.records)


@pytest.mark.parametrize(("index_code", "index_name"), [("000300", "沪深300"), ("000905", "中证500")])
def test_akshare_index_source_merges_pe_pb_rows(index_code: str, index_name: str) -> None:
    """验证数据源把 akshare-shaped PE/PB 表合并为历史序列。

    Args:
        index_code: 待验证的指数代码。
        index_name: 指数名称。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当合并结果不符合契约时抛出。
    """

    pe_fetcher = _RecordingFetcher(
        [
            {"日期": "2026-05-21", "滚动市盈率中位数": "20.5"},
            {"日期": "2026-05-22", "滚动市盈率中位数": "21.5"},
        ]
    )
    pb_fetcher = _RecordingFetcher(
        [
            {"日期": "2026-05-22", "市净率中位数": "2.2"},
            {"日期": "2026-05-21", "市净率中位数": "2.1"},
        ]
    )

    source = AkshareIndexThermometerSource(pe_fetcher=pe_fetcher, pb_fetcher=pb_fetcher)

    history = asyncio.run(source.load_index_history(index_code))

    assert pe_fetcher.symbols == [index_name]
    assert pb_fetcher.symbols == [index_name]
    assert history.index_code == index_code
    assert history.index_name == index_name
    assert history.source == "akshare_legulegu_index_pe_pb"
    assert [point.date for point in history.points] == ["2026-05-21", "2026-05-22"]
    assert history.points[-1].pe == Decimal("21.5")
    assert history.points[-1].pb == Decimal("2.2")


def test_akshare_index_source_rejects_unsupported_index() -> None:
    """验证 well-formed 但未纳入覆盖范围的指数仍由数据源拒绝。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当不支持指数未被拒绝时抛出。
    """

    source = AkshareIndexThermometerSource()

    with pytest.raises(ThermometerSourceError, match="暂不支持"):
        asyncio.run(source.load_index_history("999999"))


def test_akshare_index_source_fails_closed_on_schema_drift() -> None:
    """验证 PE/PB 表字段漂移会 fail-closed。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 schema drift 未被拒绝时抛出。
    """

    source = AkshareIndexThermometerSource(
        pe_fetcher=lambda symbol: _FakeFrame([{"日期": "2026-05-22", "PE": "20"}]),
        pb_fetcher=lambda symbol: _FakeFrame([{"日期": "2026-05-22", "市净率中位数": "2"}]),
    )

    with pytest.raises(ThermometerSourceError, match="缺少字段"):
        asyncio.run(source.load_index_history("000300"))


def test_akshare_index_source_rejects_bool_valuation_values() -> None:
    """验证估值字段拒绝 bool，避免被 Decimal 当作字符串兜底。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 bool 估值字段未被拒绝时抛出。
    """

    source = AkshareIndexThermometerSource(
        pe_fetcher=lambda symbol: _FakeFrame([{"日期": "2026-05-22", "滚动市盈率中位数": True}]),
        pb_fetcher=lambda symbol: _FakeFrame([{"日期": "2026-05-22", "市净率中位数": "2"}]),
    )

    with pytest.raises(ThermometerSourceError, match="不能为布尔值"):
        asyncio.run(source.load_index_history("000300"))


def test_akshare_index_source_fails_closed_on_date_schema_drift() -> None:
    """验证日期格式漂移会 fail-closed。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当日期 schema drift 未被拒绝时抛出。
    """

    source = AkshareIndexThermometerSource(
        pe_fetcher=lambda symbol: _FakeFrame([{"日期": "20260522", "滚动市盈率中位数": "20"}]),
        pb_fetcher=lambda symbol: _FakeFrame([{"日期": "20260522", "市净率中位数": "2"}]),
    )

    with pytest.raises(ThermometerSourceError, match="ISO"):
        asyncio.run(source.load_index_history("000300"))


@pytest.mark.parametrize(
    "date_text",
    [
        "2026-05-22T00:00:00",
        "2026-05-22 00:00:00",
        "2026-05-22abc",
        " 2026-05-22",
        "2026-05-22 ",
        " 2026-05-22 ",
    ],
)
def test_akshare_index_source_rejects_non_strict_iso_date_strings(date_text: str) -> None:
    """验证带时间、尾随字符或首尾空白的日期字符串会 fail-closed。

    Args:
        date_text: 待验证的非严格 ISO 日期字符串。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当非严格日期字符串未被拒绝时抛出。
    """

    source = AkshareIndexThermometerSource(
        pe_fetcher=lambda symbol: _FakeFrame([{"日期": date_text, "滚动市盈率中位数": "20"}]),
        pb_fetcher=lambda symbol: _FakeFrame([{"日期": date_text, "市净率中位数": "2"}]),
    )

    with pytest.raises(ThermometerSourceError, match="ISO"):
        asyncio.run(source.load_index_history("000300"))


def test_akshare_index_source_accepts_date_objects() -> None:
    """验证 date 对象可标准化为 ISO 日期。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 date 对象未被标准化时抛出。
    """

    source = AkshareIndexThermometerSource(
        pe_fetcher=lambda symbol: _FakeFrame([{"日期": date(2026, 5, 22), "滚动市盈率中位数": "20"}]),
        pb_fetcher=lambda symbol: _FakeFrame([{"日期": date(2026, 5, 22), "市净率中位数": "2"}]),
    )

    history = asyncio.run(source.load_index_history("000300"))

    assert history.points[0].date == "2026-05-22"
