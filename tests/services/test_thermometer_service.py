"""温度计 Service 测试。"""

from __future__ import annotations

import asyncio
from decimal import Decimal
from pathlib import Path

import pytest

from fund_agent.fund.data.thermometer import (
    MacroTemperature,
    MarketTemperature,
    ThermometerSnapshot,
)
from fund_agent.services import ThermometerRequest, ThermometerService


class _FakeThermometerAdapter:
    """温度计 Service 测试用 fake adapter。"""

    def __init__(self, snapshot: ThermometerSnapshot) -> None:
        """初始化 fake adapter。

        Args:
            snapshot: 固定返回的温度计快照。

        Returns:
            无返回值。

        Raises:
            无显式抛出。
        """

        self.snapshot = snapshot
        self.force_refresh_values: list[bool] = []

    async def load_thermometer(self, *, force_refresh: bool = False) -> ThermometerSnapshot:
        """记录强制刷新参数并返回固定快照。

        Args:
            force_refresh: 是否强制刷新。

        Returns:
            固定温度计快照。

        Raises:
            无显式抛出。
        """

        self.force_refresh_values.append(force_refresh)
        return self.snapshot


def test_thermometer_service_delegates_to_injected_adapter(tmp_path: Path) -> None:
    """验证 Service 通过注入 adapter 查询温度计且不触发真实网络。

    Args:
        tmp_path: pytest 临时目录 fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当参数转发或返回值不符合契约时抛出。
    """

    snapshot = _available_snapshot()
    adapters: list[_FakeThermometerAdapter] = []
    cache_dirs: list[Path | None] = []

    def fake_factory(cache_dir: Path | None) -> _FakeThermometerAdapter:
        """创建并记录 fake adapter。

        Args:
            cache_dir: Service 转发的缓存目录。

        Returns:
            fake adapter。

        Raises:
            无显式抛出。
        """

        cache_dirs.append(cache_dir)
        adapter = _FakeThermometerAdapter(snapshot)
        adapters.append(adapter)
        return adapter

    service = ThermometerService(adapter_factory=fake_factory)
    result = asyncio.run(service.run(ThermometerRequest(cache_dir=tmp_path, force_refresh=True)))

    assert result is snapshot
    assert cache_dirs == [tmp_path]
    assert adapters[0].force_refresh_values == [True]


def test_thermometer_service_rejects_file_cache_dir(tmp_path: Path) -> None:
    """验证 cache_dir 指向文件时 Service 拒绝请求。

    Args:
        tmp_path: pytest 临时目录 fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当非法缓存路径未被拒绝时抛出。
    """

    file_path = tmp_path / "thermometer.json"
    file_path.write_text("{}", encoding="utf-8")
    service = ThermometerService(adapter_factory=lambda cache_dir: _FakeThermometerAdapter(_available_snapshot()))

    with pytest.raises(ValueError, match="cache_dir"):
        asyncio.run(service.run(ThermometerRequest(cache_dir=file_path)))


def _available_snapshot() -> ThermometerSnapshot:
    """构造可用温度计快照。

    Args:
        无。

    Returns:
        可用温度计快照。

    Raises:
        无显式抛出。
    """

    return ThermometerSnapshot(
        as_of_text="2026-05-20",
        as_of_date="2026-05-20",
        market=MarketTemperature(
            value=Decimal("32.5"),
            valuation_band="偏低",
            trend_text="低估",
        ),
        indexes=(),
        macro=MacroTemperature(
            bond_temperature=Decimal("55.5"),
            ten_year_treasury_yield=Decimal("2.1"),
        ),
        source="youzhiyouxing",
        cached=False,
        stale=False,
        unavailable=False,
        unavailable_reason=None,
        fetched_at="2026-05-20T00:00:00+00:00",
    )
