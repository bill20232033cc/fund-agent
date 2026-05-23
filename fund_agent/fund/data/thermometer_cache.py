"""自建温度计历史数据 JSON 缓存。

本模块属于 Fund Capability data 层，只负责 P19 自建温度计历史序列的
版本化 JSON 缓存。它不访问 akshare，不计算温度。
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from pathlib import Path
from typing import Final

from fund_agent.config.paths import DEFAULT_THERMOMETER_CACHE_ROOT
from fund_agent.fund.data.thermometer_types import PePbHistory, PePbPoint

THERMOMETER_HISTORY_CACHE_SCHEMA_VERSION: Final[int] = 1
THERMOMETER_HISTORY_FRESH_TTL: Final[timedelta] = timedelta(hours=24)
THERMOMETER_HISTORY_STALE_TTL: Final[timedelta] = timedelta(days=7)


@dataclass(frozen=True, slots=True)
class CachedPePbHistory:
    """缓存读取结果。

    Attributes:
        history: PE/PB 历史序列。
        stale: 是否超过 fresh TTL。
    """

    history: PePbHistory
    stale: bool


class ThermometerHistoryCache:
    """温度计 PE/PB 历史 JSON 缓存。"""

    def __init__(self, root_dir: Path | None = None) -> None:
        """初始化缓存。

        Args:
            root_dir: 温度计缓存目录；为空时使用默认 `cache/thermometer`。

        Returns:
            无返回值。

        Raises:
            无显式抛出。
        """

        self.root_dir = root_dir or DEFAULT_THERMOMETER_CACHE_ROOT

    def load(self, index_code: str, *, allow_stale: bool = False) -> CachedPePbHistory | None:
        """读取缓存。

        Args:
            index_code: 指数代码。
            allow_stale: 是否允许 24 小时以上、7 天以内的 stale cache。

        Returns:
            可用缓存；不存在、损坏或过期时返回 `None`。

        Raises:
            无显式抛出。
        """

        path = self._path_for(index_code)
        if not path.exists():
            return None
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
            cached_at = _parse_timestamp(str(payload["cache_updated_at"]))
            age = datetime.now(timezone.utc) - cached_at
            stale = age > THERMOMETER_HISTORY_FRESH_TTL
            if stale and (not allow_stale or age > THERMOMETER_HISTORY_STALE_TTL):
                return None
            return CachedPePbHistory(history=_history_from_payload(payload), stale=stale)
        except Exception:
            return None

    def save(self, history: PePbHistory) -> PePbHistory:
        """保存历史序列。

        Args:
            history: 待保存 PE/PB 历史。

        Returns:
            写入 `fetched_at` 后的历史序列。

        Raises:
            OSError: 目录创建或写入失败时抛出。
        """

        path = self._path_for(history.index_code)
        path.parent.mkdir(parents=True, exist_ok=True)
        fetched_at = _utc_timestamp()
        history_to_save = PePbHistory(
            index_code=history.index_code,
            index_name=history.index_name,
            points=history.points,
            source=history.source,
            fetched_at=fetched_at,
        )
        payload = _history_to_payload(history_to_save, cache_updated_at=fetched_at)
        path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return history_to_save

    def _path_for(self, index_code: str) -> Path:
        """生成指数缓存路径。

        Args:
            index_code: 指数代码。

        Returns:
            缓存文件路径。

        Raises:
            无显式抛出。
        """

        return self.root_dir / "index" / f"{index_code}_history.json"


def _history_to_payload(history: PePbHistory, *, cache_updated_at: str) -> dict[str, object]:
    """转换历史序列为 JSON payload。

    Args:
        history: PE/PB 历史。
        cache_updated_at: 缓存更新时间。

    Returns:
        JSON payload。

    Raises:
        无显式抛出。
    """

    return {
        "schema_version": THERMOMETER_HISTORY_CACHE_SCHEMA_VERSION,
        "index_code": history.index_code,
        "index_name": history.index_name,
        "source": history.source,
        "fetched_at": history.fetched_at,
        "cache_updated_at": cache_updated_at,
        "points": [
            {"date": point.date, "pe": str(point.pe), "pb": str(point.pb)}
            for point in history.points
        ],
    }


def _history_from_payload(payload: dict[str, object]) -> PePbHistory:
    """从 JSON payload 恢复历史序列。

    Args:
        payload: JSON payload。

    Returns:
        PE/PB 历史序列。

    Raises:
        KeyError: 缺少必需字段时抛出。
        InvalidOperation: 数值无法转换时抛出。
        TypeError: 字段类型错误时抛出。
    """

    if payload["schema_version"] != THERMOMETER_HISTORY_CACHE_SCHEMA_VERSION:
        raise ValueError("温度计缓存 schema 版本不兼容")

    raw_points = payload["points"]
    if not isinstance(raw_points, list):
        raise TypeError("温度计缓存 points 必须是列表")

    points: list[PePbPoint] = []
    for raw_point in raw_points:
        if not isinstance(raw_point, dict):
            raise TypeError("温度计缓存 point 必须是对象")
        points.append(
            PePbPoint(
                date=str(raw_point["date"]),
                pe=Decimal(str(raw_point["pe"])),
                pb=Decimal(str(raw_point["pb"])),
            )
        )

    return PePbHistory(
        index_code=str(payload["index_code"]),
        index_name=str(payload["index_name"]),
        points=tuple(points),
        source=str(payload["source"]),
        fetched_at=str(payload["fetched_at"]) if payload.get("fetched_at") else None,
    )


def _parse_timestamp(value: str) -> datetime:
    """解析 ISO 时间戳。

    Args:
        value: ISO 时间戳。

    Returns:
        带 timezone 的 datetime。

    Raises:
        ValueError: 时间戳非法时抛出。
    """

    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed


def _utc_timestamp() -> str:
    """生成 UTC 时间戳。

    Args:
        无。

    Returns:
        ISO 8601 UTC 时间戳。

    Raises:
        无显式抛出。
    """

    return datetime.now(timezone.utc).isoformat()
