"""基金净值数据适配器与缓存。"""

from __future__ import annotations

import asyncio
import json
import sqlite3
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Final

from fund_agent.config.paths import DEFAULT_NAV_CACHE_ROOT

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
    """

    fund_code: str
    records: NavPayload
    source: str
    cached: bool


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

    def _load_cached_sync(self, fund_code: str) -> NavPayload | None:
        """同步读取净值缓存。

        Args:
            fund_code: 基金代码。

        Returns:
            命中时返回净值记录，否则返回 `None`。

        Raises:
            sqlite3.Error: 查询 SQLite 失败时抛出。
            json.JSONDecodeError: 缓存 JSON 非法时抛出。
        """

        with sqlite3.connect(self.sqlite_path) as connection:
            row = connection.execute(
                "SELECT payload_json FROM nav_cache WHERE fund_code = ?",
                (fund_code,),
            ).fetchone()
        if row is None:
            return None
        return list(json.loads(str(row[0])))

    def _save_cached_sync(self, fund_code: str, records: NavPayload) -> None:
        """同步写入净值缓存。

        Args:
            fund_code: 基金代码。
            records: 净值记录列表。

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
                    _utc_timestamp(),
                ),
            )
            connection.commit()
