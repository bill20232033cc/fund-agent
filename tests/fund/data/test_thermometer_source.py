"""自建温度计数据源测试。"""

from __future__ import annotations

import asyncio
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


def test_akshare_index_source_merges_pe_pb_rows() -> None:
    """验证数据源把 akshare-shaped PE/PB 表合并为历史序列。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当合并结果不符合契约时抛出。
    """

    source = AkshareIndexThermometerSource(
        pe_fetcher=lambda symbol: _FakeFrame(
            [
                {"日期": "2026-05-21", "滚动市盈率中位数": "20.5"},
                {"日期": "2026-05-22", "滚动市盈率中位数": "21.5"},
            ]
        ),
        pb_fetcher=lambda symbol: _FakeFrame(
            [
                {"日期": "2026-05-22", "市净率中位数": "2.2"},
                {"日期": "2026-05-21", "市净率中位数": "2.1"},
            ]
        ),
    )

    history = asyncio.run(source.load_index_history("000300"))

    assert history.index_code == "000300"
    assert history.index_name == "沪深300"
    assert history.source == "akshare_legulegu_index_pe_pb"
    assert [point.date for point in history.points] == ["2026-05-21", "2026-05-22"]
    assert history.points[-1].pe == Decimal("21.5")
    assert history.points[-1].pb == Decimal("2.2")


def test_akshare_index_source_rejects_unsupported_index() -> None:
    """验证 P19-S1 只支持沪深300。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当不支持指数未被拒绝时抛出。
    """

    source = AkshareIndexThermometerSource()

    with pytest.raises(ThermometerSourceError, match="暂不支持"):
        asyncio.run(source.load_index_history("000905"))


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
