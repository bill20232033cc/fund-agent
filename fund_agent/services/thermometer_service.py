"""温度计查询 Service 编排层。

本模块属于 Service 层，只负责把 UI 输入收敛为显式请求对象并调用
Capability data 层的温度计适配器。它不解析温度计页面，不决定估值状态，
也不把温度计结果写入基金分析报告。
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Protocol

from fund_agent.fund.analysis.thermometer_calculator import calculate_thermometer_reading
from fund_agent.fund.data import (
    FundThermometerAdapter,
    PePbHistory,
    ThermometerBatchResult,
    ThermometerReading,
    ThermometerSnapshot,
    ThermometerUnavailable,
)
from fund_agent.fund.data.thermometer_cache import ThermometerHistoryCache
from fund_agent.fund.data.thermometer_source import (
    ALL_A_MARKET_CODE,
    AkshareThermometerSource,
    ThermometerSourceError,
    classify_thermometer_code,
    thermometer_display_name,
)


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
    """自建温度计数据源协议。"""

    async def load_index_history(self, index_code: str) -> PePbHistory:
        """读取指定指数或市场 PE/PB 历史。

        Args:
            index_code: 指数或市场代码。

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
        index_code: 指定单个自建温度计代码；为空时默认查询全 A 市场。
        index_codes: 指定多个自建温度计代码；与 `index_code` 互斥。
    """

    cache_dir: Path | None = None
    force_refresh: bool = False
    index_code: str | None = None
    index_codes: tuple[str, ...] | None = None


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
            index_source: 可注入自建温度计数据源；未提供时使用 akshare 复合数据源。
            history_cache_factory: 可注入历史缓存工厂；未提供时使用 JSON 历史缓存。

        Returns:
            无返回值。

        Raises:
            无显式抛出。
        """

        self._adapter_factory = adapter_factory or _default_adapter_factory
        self._index_source = index_source or AkshareThermometerSource()
        self._history_cache_factory = history_cache_factory or ThermometerHistoryCache

    async def run(
        self, request: ThermometerRequest
    ) -> ThermometerSnapshot | ThermometerReading | ThermometerBatchResult:
        """查询温度计快照。

        Args:
            request: 显式温度计查询参数，不使用 `extra_payload`。

        Returns:
            温度计快照或自建温度计读数；上游不可用时返回 `unavailable=True`。

        Raises:
            ValueError: 请求参数非法时抛出。
            Exception: 允许适配器传播非数据态异常。
        """

        normalized = _normalize_request(request)
        if normalized.index_codes is not None:
            return await self._load_index_batch(request, normalized.index_codes)
        if normalized.index_code is not None:
            return await self._load_index_reading(request, normalized.index_code)
        adapter = self._adapter_factory(request.cache_dir)
        return await adapter.load_thermometer(force_refresh=request.force_refresh)

    async def _load_index_batch(
        self, request: ThermometerRequest, index_codes: tuple[str, ...]
    ) -> ThermometerBatchResult:
        """读取批量自建温度计读数。

        Args:
            request: 温度计请求。
            index_codes: Service 规范化后的指数或市场代码序列。

        Returns:
            批量温度计读数。

        Raises:
            ValueError: 请求参数非法时抛出。
        """

        readings = tuple(
            [await self._load_index_reading(request, index_code) for index_code in index_codes]
        )
        unavailable_count = sum(1 for reading in readings if reading.unavailable)
        return ThermometerBatchResult(
            readings=readings,
            requested_index_codes=index_codes,
            generated_at=datetime.now(timezone.utc).isoformat(),
            unavailable=unavailable_count == len(readings),
            partial_unavailable=0 < unavailable_count < len(readings),
            unavailable_count=unavailable_count,
        )

    async def _load_index_reading(
        self, request: ThermometerRequest, index_code: str
    ) -> ThermometerReading:
        """读取自建温度计读数。

        Args:
            request: 温度计请求。
            index_code: Service 规范化后的指数或市场代码。

        Returns:
            自建指数温度计读数；数据不可用时返回 unavailable 读数。

        Raises:
            ValueError: 温度计代码格式非法时抛出。
        """

        if classify_thermometer_code(index_code) == "unsupported":
            return ThermometerUnavailable(
                index_code=index_code,
                index_name=thermometer_display_name(index_code),
                reason=f"自建温度计数据不可用：暂不支持温度计代码：{index_code}",
            ).to_reading()

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
        except ThermometerSourceError as exc:
            cached = cache.load(index_code, allow_stale=True)
            if cached is not None:
                return calculate_thermometer_reading(
                    cached.history,
                    cached=True,
                    stale=cached.stale,
                )
            return ThermometerUnavailable(
                index_code=index_code,
                index_name=thermometer_display_name(index_code),
                reason=f"自建温度计数据不可用：{exc}",
            ).to_reading()
        try:
            saved_history = cache.save(history)
        except OSError:
            saved_history = history
        return calculate_thermometer_reading(saved_history, cached=False, stale=False)


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


@dataclass(frozen=True, slots=True)
class _NormalizedThermometerRequest:
    """Service 内部规范化温度计请求。"""

    index_code: str | None
    index_codes: tuple[str, ...] | None


def _normalize_request(request: ThermometerRequest) -> _NormalizedThermometerRequest:
    """规范化并校验温度计查询请求。

    Args:
        request: 温度计查询请求。

    Returns:
        规范化后的单代码或批量代码字段。

    Raises:
        ValueError: 当缓存路径、请求状态机或温度计代码非法时抛出。
    """

    if request.cache_dir is not None and request.cache_dir.exists() and not request.cache_dir.is_dir():
        raise ValueError("cache_dir 必须是目录")
    if request.index_code is not None and request.index_codes is not None:
        raise ValueError("index_code 与 index_codes 不能同时设置")
    if request.index_codes is not None:
        index_codes = _normalize_index_codes(request.index_codes, field_name="index_codes")
        return _NormalizedThermometerRequest(index_code=None, index_codes=index_codes)
    if request.index_code is not None:
        index_codes = _normalize_index_codes((request.index_code,), field_name="index_code")
        return _NormalizedThermometerRequest(index_code=index_codes[0], index_codes=None)
    return _NormalizedThermometerRequest(index_code=ALL_A_MARKET_CODE, index_codes=None)


def _normalize_index_codes(index_codes: tuple[str, ...], *, field_name: str) -> tuple[str, ...]:
    """规范化温度计代码序列。

    Args:
        index_codes: 原始温度计代码序列。
        field_name: 错误信息使用的字段名。

    Returns:
        preserve-order de-duplication 后的温度计代码序列。

    Raises:
        ValueError: 温度计代码为空、不是 `wind_all_a` 且不是 6 位 ASCII 数字时抛出。
    """

    if not index_codes:
        raise ValueError(f"{field_name} 不能为空")

    normalized: list[str] = []
    seen: set[str] = set()
    for index_code in index_codes:
        text = index_code.strip()
        if not text:
            raise ValueError(f"{field_name} 不能包含空温度计代码")
        if text != ALL_A_MARKET_CODE and not _is_six_ascii_digits(text):
            raise ValueError(f"{field_name} 必须是 wind_all_a 或 6 位 ASCII 数字")
        if text not in seen:
            normalized.append(text)
            seen.add(text)
    if not normalized:
        raise ValueError(f"{field_name} 不能为空")
    return tuple(normalized)


def _is_six_ascii_digits(value: str) -> bool:
    """判断字符串是否为 6 位 ASCII 数字。

    Args:
        value: 待验证字符串。

    Returns:
        是 6 位 ASCII 数字返回 True，否则返回 False。

    Raises:
        无显式抛出。
    """

    return len(value) == 6 and all("0" <= char <= "9" for char in value)
