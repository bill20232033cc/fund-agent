"""基金净值数据适配器与缓存。"""

from __future__ import annotations

import asyncio
import json
import sqlite3
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Final

from fund_agent.config.paths import DEFAULT_NAV_CACHE_ROOT
from fund_agent.fund.data.nav_source_contract import _RawNavSourceResult

NAV_CACHE_ROOT: Final[Path] = DEFAULT_NAV_CACHE_ROOT
NAV_SQLITE_FILENAME: Final[str] = "nav.sqlite3"
NavPayload = list[dict[str, object]]
NavFetcher = Callable[[str], Awaitable[NavPayload] | NavPayload]


def _utc_timestamp() -> str:
    """生成 UTC 时间戳字符串。

    Args:
        无。

    Returns:
        ISO 8601 UTC 时间戳。

    Raises:
        无显式抛出。
    """

    return datetime.now(timezone.utc).isoformat()


async def _default_nav_fetcher(fund_code: str) -> NavPayload:
    """通过 akshare 获取基金历史净值。

    Args:
        fund_code: 基金代码。

    Returns:
        JSON 兼容的净值记录列表。

    Raises:
        ImportError: akshare 不可用时抛出。
        Exception: akshare 查询异常时向上抛出。
    """

    return await asyncio.to_thread(_fetch_nav_with_akshare, fund_code)


def _fetch_nav_with_akshare(fund_code: str) -> NavPayload:
    """同步调用 akshare 获取基金历史净值。

    Args:
        fund_code: 基金代码。

    Returns:
        JSON 兼容的净值记录列表。

    Raises:
        ImportError: akshare 不可用时抛出。
        AttributeError: akshare 接口不存在时抛出。
        Exception: akshare 查询异常时向上抛出。
    """

    import akshare as ak

    dataframe = ak.fund_open_fund_info_em(symbol=fund_code, indicator="单位净值走势")
    return [
        {str(column): _json_safe_value(value) for column, value in row.items()}
        for row in dataframe.to_dict(orient="records")
    ]


def _json_safe_value(value: object) -> object:
    """把常见 pandas/numpy 值转换为 JSON 兼容值。

    Args:
        value: 原始值。

    Returns:
        JSON 兼容值。

    Raises:
        无显式抛出。
    """

    if hasattr(value, "item"):
        return value.item()
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return value


@dataclass(frozen=True, slots=True)
class NavDataResult:
    """基金净值数据读取结果。

    Attributes:
        fund_code: 基金代码。
        records: 净值记录列表。
        source: 数据来源。
        cached: 是否命中缓存。
        unavailable: 净值外部数据是否不可用。
        unavailable_reason: 净值数据不可用原因。
    """

    fund_code: str
    records: NavPayload
    source: str
    cached: bool
    unavailable: bool = False
    unavailable_reason: str | None = None


@dataclass(frozen=True, slots=True)
class _NavCacheEntry:
    """净值缓存条目。

    该私有模型只在 source adapter 内部使用，用于让 typed repository 能看到
    cache hit 背后的 origin source 和缓存更新时间，同时保持旧 `load_nav_data()`
    的 `source="nav_cache"` 兼容行为。
    """

    records: NavPayload
    source: str
    updated_at: str


def unavailable_nav_data_result(
    fund_code: str,
    *,
    reason: str,
    source: str = "nav_unavailable",
) -> NavDataResult:
    """构造净值数据不可用的降级结果。

    Args:
        fund_code: 基金代码。
        reason: 不可用原因，调用方应包含异常类型和异常信息。
        source: 降级来源标记。

    Returns:
        空净值序列的不可用结果。

    Raises:
        ValueError: 基金代码、原因或来源为空时抛出。
    """

    normalized_fund_code = fund_code.strip()
    normalized_reason = reason.strip()
    normalized_source = source.strip()
    if not normalized_fund_code:
        raise ValueError("fund_code 不能为空")
    if not normalized_reason:
        raise ValueError("reason 不能为空")
    if not normalized_source:
        raise ValueError("source 不能为空")
    return NavDataResult(
        fund_code=normalized_fund_code,
        records=[],
        source=normalized_source,
        cached=False,
        unavailable=True,
        unavailable_reason=normalized_reason,
    )


class FundNavDataAdapter:
    """基金净值数据适配器。

    该适配器位于 Agent 层基金能力的 data 层，负责净值数据获取与自身缓存。
    """

    def __init__(self, root_dir: Path | None = None, fetcher: NavFetcher | None = None) -> None:
        """初始化净值数据适配器。

        Args:
            root_dir: 缓存根目录；未提供时使用默认 `cache/nav`。
            fetcher: 自定义净值抓取函数；未提供时使用 akshare。

        Returns:
            无返回值。

        Raises:
            无显式抛出。
        """

        self.root_dir = root_dir or NAV_CACHE_ROOT
        self.sqlite_path = self.root_dir / NAV_SQLITE_FILENAME
        self._fetcher = fetcher or _default_nav_fetcher

    async def initialize(self) -> None:
        """初始化缓存目录与 SQLite schema。

        Args:
            无。

        Returns:
            无返回值。

        Raises:
            OSError: 创建目录失败时抛出。
            sqlite3.Error: 初始化 SQLite 失败时抛出。
        """

        await asyncio.to_thread(self._initialize_sync)

    def _initialize_sync(self) -> None:
        """同步初始化缓存目录与 SQLite schema。

        Args:
            无。

        Returns:
            无返回值。

        Raises:
            OSError: 创建目录失败时抛出。
            sqlite3.Error: 初始化 SQLite 失败时抛出。
        """

        self.root_dir.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.sqlite_path) as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS nav_cache (
                    fund_code TEXT PRIMARY KEY,
                    payload_json TEXT NOT NULL,
                    source TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )
            connection.commit()

    async def load_nav_data(self, fund_code: str, *, force_refresh: bool = False) -> NavDataResult:
        """读取基金净值数据。

        Args:
            fund_code: 基金代码。
            force_refresh: 是否强制刷新缓存。

        Returns:
            净值数据读取结果。

        Raises:
            ValueError: 基金代码为空时抛出。
            sqlite3.Error: 缓存读写失败时抛出。
            Exception: 抓取函数异常时向上抛出。
        """

        normalized_fund_code = fund_code.strip()
        if not normalized_fund_code:
            raise ValueError("fund_code 不能为空")

        await self.initialize()
        if not force_refresh:
            cached_records = await asyncio.to_thread(self._load_cached_sync, normalized_fund_code)
            if cached_records is not None:
                return NavDataResult(
                    fund_code=normalized_fund_code,
                    records=cached_records,
                    source="nav_cache",
                    cached=True,
                )

        fetched_records = await self._call_fetcher(normalized_fund_code)
        await asyncio.to_thread(self._save_cached_sync, normalized_fund_code, fetched_records)
        return NavDataResult(
            fund_code=normalized_fund_code,
            records=fetched_records,
            source="akshare",
            cached=False,
        )

    async def load_raw_nav_source(
        self,
        fund_code: str,
        *,
        share_class: str | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
        force_refresh: bool = False,
    ) -> _RawNavSourceResult:
        """读取原始 NAV source 结果及缓存元数据。

        Args:
            fund_code: 基金代码。
            share_class: 份额类别；legacy raw-unit adapter 不使用，仅为 Protocol 兼容。
            start_date: 日期窗口起点；legacy raw-unit adapter 不使用，仅为 Protocol 兼容。
            end_date: 日期窗口终点；legacy raw-unit adapter 不使用，仅为 Protocol 兼容。
            force_refresh: 是否强制刷新缓存。

        Returns:
            原始 records 与 source/cache 元数据。

        Raises:
            ValueError: 基金代码为空时抛出。
            sqlite3.Error: 缓存读写失败时抛出。
            Exception: 抓取函数异常时向上抛出。
        """

        normalized_fund_code = fund_code.strip()
        if not normalized_fund_code:
            raise ValueError("fund_code 不能为空")
        _ = (share_class, start_date, end_date)

        await self.initialize()
        if not force_refresh:
            cache_entry = await asyncio.to_thread(
                self._load_cached_with_metadata,
                normalized_fund_code,
            )
            if cache_entry is not None:
                return _RawNavSourceResult(
                    fund_code=normalized_fund_code,
                    records=cache_entry.records,
                    source="nav_cache",
                    origin_source=cache_entry.source,
                    source_id=normalized_fund_code,
                    source_url=None,
                    source_query_params=(),
                    source_nav_type="unit_nav",
                    source_adjustment_basis="raw_unit_nav",
                    cached=True,
                    retrieved_at=None,
                    cache_updated_at=cache_entry.updated_at,
                )

        fetched_records = await self._call_fetcher(normalized_fund_code)
        retrieved_at = _utc_timestamp()
        await asyncio.to_thread(
            self._save_cached_sync,
            normalized_fund_code,
            fetched_records,
            retrieved_at,
        )
        return _RawNavSourceResult(
            fund_code=normalized_fund_code,
            records=fetched_records,
            source="akshare",
            origin_source="akshare",
            source_id=normalized_fund_code,
            source_url=None,
            source_query_params=(),
            source_nav_type="unit_nav",
            source_adjustment_basis="raw_unit_nav",
            cached=False,
            retrieved_at=retrieved_at,
            cache_updated_at=None,
        )

    async def _call_fetcher(self, fund_code: str) -> NavPayload:
        """调用净值抓取函数。

        Args:
            fund_code: 基金代码。

        Returns:
            净值记录列表。

        Raises:
            Exception: 抓取函数异常时向上抛出。
        """

        payload = self._fetcher(fund_code)
        if asyncio.iscoroutine(payload):
            return await payload
        return payload

    def _load_cached_with_metadata(self, fund_code: str) -> _NavCacheEntry | None:
        """同步读取带元数据的净值缓存。

        Args:
            fund_code: 基金代码。

        Returns:
            命中时返回缓存条目，否则返回 `None`。

        Raises:
            sqlite3.Error: 查询 SQLite 失败时抛出。
            json.JSONDecodeError: 缓存 JSON 非法时抛出。
        """

        with sqlite3.connect(self.sqlite_path) as connection:
            row = connection.execute(
                "SELECT payload_json, source, updated_at FROM nav_cache WHERE fund_code = ?",
                (fund_code,),
            ).fetchone()
        if row is None:
            return None
        return _NavCacheEntry(
            records=list(json.loads(str(row[0]))),
            source=str(row[1]),
            updated_at=str(row[2]),
        )

    def _load_cached_sync(self, fund_code: str) -> NavPayload | None:
        """同步读取净值缓存 records。

        Args:
            fund_code: 基金代码。

        Returns:
            命中时返回净值记录，否则返回 `None`。

        Raises:
            sqlite3.Error: 查询 SQLite 失败时抛出。
            json.JSONDecodeError: 缓存 JSON 非法时抛出。
        """

        cache_entry = self._load_cached_with_metadata(fund_code)
        if cache_entry is None:
            return None
        return cache_entry.records

    def _save_cached_sync(
        self,
        fund_code: str,
        records: NavPayload,
        updated_at: str | None = None,
    ) -> None:
        """同步写入净值缓存。

        Args:
            fund_code: 基金代码。
            records: 净值记录列表。
            updated_at: 缓存更新时间；为空时使用当前 UTC 时间。

        Returns:
            无返回值。

        Raises:
            sqlite3.Error: 写入 SQLite 失败时抛出。
        """

        with sqlite3.connect(self.sqlite_path) as connection:
            connection.execute(
                """
                INSERT INTO nav_cache (
                    fund_code,
                    payload_json,
                    source,
                    updated_at
                ) VALUES (?, ?, ?, ?)
                ON CONFLICT(fund_code) DO UPDATE SET
                    payload_json = excluded.payload_json,
                    source = excluded.source,
                    updated_at = excluded.updated_at
                """,
                (
                    fund_code,
                    json.dumps(records, ensure_ascii=False),
                    "akshare",
                    updated_at or _utc_timestamp(),
                ),
            )
            connection.commit()
