"""温度计 Service 测试。"""

from __future__ import annotations

import asyncio
import json
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from pathlib import Path

import pytest

from fund_agent.fund.data.thermometer import (
    MacroTemperature,
    MarketTemperature,
    ThermometerSnapshot,
)
from fund_agent.fund.data.thermometer_cache import ThermometerHistoryCache
from fund_agent.fund.data.thermometer_types import PePbHistory, PePbPoint
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


class _FakeIndexSource:
    """自建指数温度计 fake 数据源。"""

    def __init__(self, history: PePbHistory | None = None, exc: Exception | None = None) -> None:
        """初始化 fake 数据源。

        Args:
            history: 固定返回的历史序列。
            exc: 固定抛出的异常。

        Returns:
            无返回值。

        Raises:
            无显式抛出。
        """

        self.history = history or _index_history()
        self.exc = exc
        self.index_codes: list[str] = []

    async def load_index_history(self, index_code: str) -> PePbHistory:
        """记录指数代码并返回固定历史。

        Args:
            index_code: 指数代码。

        Returns:
            固定历史序列。

        Raises:
            Exception: 初始化时传入的固定异常。
        """

        self.index_codes.append(index_code)
        if self.exc is not None:
            raise self.exc
        return self.history


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


def test_thermometer_service_routes_index_request_to_self_owned_source(tmp_path: Path) -> None:
    """验证指定指数时 Service 走自建温度计路径。

    Args:
        tmp_path: pytest 临时目录 fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 Service 路由或读数不符合契约时抛出。
    """

    source = _FakeIndexSource()
    service = ThermometerService(
        adapter_factory=lambda cache_dir: _FakeThermometerAdapter(_available_snapshot()),
        index_source=source,
        history_cache_factory=ThermometerHistoryCache,
    )

    result = asyncio.run(
        service.run(ThermometerRequest(cache_dir=tmp_path, index_code="000300"))
    )

    assert source.index_codes == ["000300"]
    assert result.index_code == "000300"
    assert result.temperature == Decimal("100.00")
    assert result.unavailable is False
    assert result.cached is False


def test_thermometer_service_uses_stale_index_cache_when_source_fails(tmp_path: Path) -> None:
    """验证自建数据源失败时可回退到 stale cache。

    Args:
        tmp_path: pytest 临时目录 fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 stale cache 未被复用时抛出。
    """

    cache = ThermometerHistoryCache(root_dir=tmp_path)
    cache.save(_index_history())
    cache_path = tmp_path / "index" / "000300_history.json"
    payload = json.loads(cache_path.read_text(encoding="utf-8"))
    payload["cache_updated_at"] = (datetime.now(timezone.utc) - timedelta(days=2)).isoformat()
    cache_path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    service = ThermometerService(
        index_source=_FakeIndexSource(exc=RuntimeError("network down")),
        history_cache_factory=lambda cache_dir: ThermometerHistoryCache(root_dir=tmp_path),
    )

    result = asyncio.run(
        service.run(ThermometerRequest(cache_dir=tmp_path, index_code="000300", force_refresh=True))
    )

    assert result.cached is True
    assert result.stale is True
    assert result.unavailable is False


def test_thermometer_service_returns_unavailable_without_index_cache(tmp_path: Path) -> None:
    """验证自建数据源失败且无缓存时返回 unavailable 读数。

    Args:
        tmp_path: pytest 临时目录 fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当失败路径不是 unavailable 数据态时抛出。
    """

    service = ThermometerService(
        index_source=_FakeIndexSource(exc=RuntimeError("network down")),
        history_cache_factory=lambda cache_dir: ThermometerHistoryCache(root_dir=tmp_path),
    )

    result = asyncio.run(service.run(ThermometerRequest(cache_dir=tmp_path, index_code="000300")))

    assert result.unavailable is True
    assert result.valuation_state_candidate == "unavailable"
    assert "network down" in str(result.unavailable_reason)


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


def _index_history() -> PePbHistory:
    """构造自建指数温度计历史。

    Args:
        无。

    Returns:
        PE/PB 历史。

    Raises:
        无显式抛出。
    """

    return PePbHistory(
        index_code="000300",
        index_name="沪深300",
        source="fixture",
        points=(
            PePbPoint(date="2026-05-20", pe=Decimal("10"), pb=Decimal("1")),
            PePbPoint(date="2026-05-21", pe=Decimal("20"), pb=Decimal("2")),
        ),
    )
