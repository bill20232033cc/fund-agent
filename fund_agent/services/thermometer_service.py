"""温度计查询 Service 编排层。

本模块属于 Service 层，只负责把 UI 输入收敛为显式请求对象并调用
Capability data 层的温度计适配器。它不解析温度计页面，不决定估值状态，
也不把温度计结果写入基金分析报告。
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from fund_agent.fund.analysis.thermometer_calculator import calculate_thermometer_reading
from fund_agent.fund.data import (
    FundThermometerAdapter,
    PePbHistory,
    ThermometerReading,
    ThermometerSnapshot,
    ThermometerUnavailable,
)
from fund_agent.fund.data.thermometer_cache import ThermometerHistoryCache
from fund_agent.fund.data.thermometer_source import AkshareIndexThermometerSource


class _ThermometerAdapter(Protocol):
    """温度计适配器协议。

    该协议用于 Service 测试注入 fake adapter，避免 Service 测试触发真实网络。
    """

    async def load_thermometer(self, *, force_refresh: bool = False) -> ThermometerSnapshot:
        """读取温度计快照。

        Args:
            force_refresh: 是否绕过 fresh cache 强制抓取。

        Returns:
            温度计快照。

        Raises:
            Exception: 允许具体适配器传播非数据态异常。
        """


class _ThermometerAdapterFactory(Protocol):
    """温度计适配器工厂协议。"""

    def __call__(self, cache_dir: Path | None) -> _ThermometerAdapter:
        """按缓存目录创建温度计适配器。

        Args:
            cache_dir: 温度计缓存目录；为空时使用 Capability 默认目录。

        Returns:
            温度计适配器。

        Raises:
            Exception: 允许具体工厂传播初始化异常。
        """


class _IndexThermometerSource(Protocol):
    """自建指数温度计数据源协议。"""

    async def load_index_history(self, index_code: str) -> PePbHistory:
        """读取指定指数 PE/PB 历史。

        Args:
            index_code: 指数代码。

        Returns:
            PE/PB 历史序列。

        Raises:
            Exception: 允许具体数据源传播数据不可用异常。
        """


class _ThermometerHistoryCacheFactory(Protocol):
    """温度计历史缓存工厂协议。"""

    def __call__(self, cache_dir: Path | None) -> ThermometerHistoryCache:
        """按缓存目录创建温度计历史缓存。

        Args:
            cache_dir: 温度计缓存目录。

        Returns:
            温度计历史缓存。

        Raises:
            Exception: 允许具体工厂传播初始化异常。
        """


@dataclass(frozen=True, slots=True)
class ThermometerRequest:
    """温度计查询请求。

    Attributes:
        cache_dir: 温度计缓存目录；为空时使用 Capability 默认目录。
        force_refresh: 是否绕过 fresh cache 强制抓取。
        index_code: 指定自建指数温度计代码；为空时保留当前公开页快照行为。
    """

    cache_dir: Path | None = None
    force_refresh: bool = False
    index_code: str | None = None


class ThermometerService:
    """温度计查询用例编排 Service。"""

    def __init__(
        self,
        adapter_factory: _ThermometerAdapterFactory | None = None,
        index_source: _IndexThermometerSource | None = None,
        history_cache_factory: _ThermometerHistoryCacheFactory | None = None,
    ) -> None:
        """初始化温度计 Service。

        Args:
            adapter_factory: 可注入适配器工厂；未提供时创建默认 `FundThermometerAdapter`。
            index_source: 可注入自建指数温度计数据源；未提供时使用 akshare 数据源。
            history_cache_factory: 可注入历史缓存工厂；未提供时使用 JSON 历史缓存。

        Returns:
            无返回值。

        Raises:
            无显式抛出。
        """

        self._adapter_factory = adapter_factory or _default_adapter_factory
        self._index_source = index_source or AkshareIndexThermometerSource()
        self._history_cache_factory = history_cache_factory or ThermometerHistoryCache

    async def run(self, request: ThermometerRequest) -> ThermometerSnapshot | ThermometerReading:
        """查询温度计快照。

        Args:
            request: 显式温度计查询参数，不使用 `extra_payload`。

        Returns:
            温度计快照；上游不可用时由 Capability 返回 `unavailable=True`。

        Raises:
            ValueError: 请求参数非法时抛出。
            Exception: 允许适配器传播非数据态异常。
        """

        _validate_request(request)
        if request.index_code is not None:
            return await self._load_index_reading(request)
        adapter = self._adapter_factory(request.cache_dir)
        return await adapter.load_thermometer(force_refresh=request.force_refresh)

    async def _load_index_reading(self, request: ThermometerRequest) -> ThermometerReading:
        """读取自建指数温度计读数。

        Args:
            request: 温度计请求，必须包含 `index_code`。

        Returns:
            自建指数温度计读数；数据不可用时返回 unavailable 读数。

        Raises:
            ValueError: 指数代码格式非法时抛出。
        """

        index_code = request.index_code.strip() if request.index_code is not None else None
        if index_code is None:
            raise ValueError("index_code 不能为空")

        cache = self._history_cache_factory(request.cache_dir)
        if not request.force_refresh:
            cached = cache.load(index_code)
            if cached is not None:
                return calculate_thermometer_reading(
                    cached.history,
                    cached=True,
                    stale=cached.stale,
                )

        try:
            history = await self._index_source.load_index_history(index_code)
            history = cache.save(history)
            return calculate_thermometer_reading(history, cached=False, stale=False)
        except Exception as exc:
            cached = cache.load(index_code, allow_stale=True)
            if cached is not None:
                return calculate_thermometer_reading(
                    cached.history,
                    cached=True,
                    stale=cached.stale,
                )
            return ThermometerUnavailable(
                index_code=index_code,
                index_name=index_code,
                reason=f"自建温度计数据不可用：{exc}",
            ).to_reading()


def _default_adapter_factory(cache_dir: Path | None) -> FundThermometerAdapter:
    """创建默认温度计适配器。

    Args:
        cache_dir: 温度计缓存目录；为空时使用 Capability 默认目录。

    Returns:
        默认温度计适配器。

    Raises:
        无显式抛出。
    """

    return FundThermometerAdapter(root_dir=cache_dir)


def _validate_request(request: ThermometerRequest) -> None:
    """校验温度计查询请求。

    Args:
        request: 温度计查询请求。

    Returns:
        无返回值。

    Raises:
        ValueError: 当缓存路径指向已存在文件时抛出。
    """

    if request.cache_dir is not None and request.cache_dir.exists() and not request.cache_dir.is_dir():
        raise ValueError("cache_dir 必须是目录")
    if request.index_code is not None:
        index_code = request.index_code.strip()
        if not index_code.isdigit() or len(index_code) != 6:
            raise ValueError("index_code 必须是 6 位数字")
