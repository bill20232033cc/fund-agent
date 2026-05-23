"""自建温度计历史缓存测试。"""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from pathlib import Path

import pytest

from fund_agent.fund.data.thermometer_cache import ThermometerHistoryCache
from fund_agent.fund.data.thermometer_types import PePbHistory, PePbPoint


def test_thermometer_history_cache_persists_and_loads_fresh_history(tmp_path) -> None:  # type: ignore[no-untyped-def]
    """验证 JSON 缓存可写入并读取 fresh history。

    Args:
        tmp_path: pytest 临时目录 fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当缓存读写不符合契约时抛出。
    """

    cache = ThermometerHistoryCache(root_dir=tmp_path)
    saved = cache.save(_history())

    cached = cache.load("000300")

    assert cached is not None
    assert cached.stale is False
    assert cached.history.index_code == "000300"
    assert cached.history.points[-1].pe == Decimal("30")
    assert cached.history.fetched_at == saved.fetched_at


def test_thermometer_history_cache_uses_market_namespace_for_all_a(tmp_path: Path) -> None:
    """验证全 A 市场缓存写入 market namespace 且不落入 index namespace。

    Args:
        tmp_path: pytest 临时目录 fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当缓存路径命名空间不符合契约时抛出。
    """

    cache = ThermometerHistoryCache(root_dir=tmp_path)
    cache.save(_history(index_code="wind_all_a", index_name="万得全 A / 全 A 市场"))

    market_path = tmp_path / "market" / "wind_all_a_history.json"
    index_path = tmp_path / "index" / "wind_all_a_history.json"
    cached = cache.load("wind_all_a")

    assert market_path.exists()
    assert not index_path.exists()
    assert cached is not None
    assert cached.history.index_code == "wind_all_a"
    assert cached.history.index_name == "万得全 A / 全 A 市场"


def test_thermometer_history_cache_preserves_index_namespace(tmp_path: Path) -> None:
    """验证既有宽基指数缓存路径保持在 index namespace。

    Args:
        tmp_path: pytest 临时目录 fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当指数缓存路径发生回归时抛出。
    """

    cache = ThermometerHistoryCache(root_dir=tmp_path)
    cache.save(_history(index_code="000300", index_name="沪深300"))
    cache.save(_history(index_code="000905", index_name="中证500"))

    assert (tmp_path / "index" / "000300_history.json").exists()
    assert (tmp_path / "index" / "000905_history.json").exists()
    assert not (tmp_path / "market" / "000300_history.json").exists()


def test_thermometer_history_cache_respects_stale_policy(tmp_path) -> None:  # type: ignore[no-untyped-def]
    """验证 stale cache 只有显式允许时才返回。

    Args:
        tmp_path: pytest 临时目录 fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 stale 策略不符合契约时抛出。
    """

    cache = ThermometerHistoryCache(root_dir=tmp_path)
    cache.save(_history())
    path = tmp_path / "index" / "000300_history.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["cache_updated_at"] = (datetime.now(timezone.utc) - timedelta(days=2)).isoformat()
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")

    assert cache.load("000300") is None
    stale = cache.load("000300", allow_stale=True)
    assert stale is not None
    assert stale.stale is True


def test_thermometer_history_cache_ignores_corrupt_payload(tmp_path) -> None:  # type: ignore[no-untyped-def]
    """验证损坏缓存不向上抛出。

    Args:
        tmp_path: pytest 临时目录 fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当损坏缓存未降级为 miss 时抛出。
    """

    path = tmp_path / "index" / "000300_history.json"
    path.parent.mkdir(parents=True)
    path.write_text("{bad json", encoding="utf-8")
    cache = ThermometerHistoryCache(root_dir=tmp_path)

    assert cache.load("000300", allow_stale=True) is None


def test_thermometer_history_cache_does_not_load_unsupported_code(tmp_path: Path) -> None:
    """验证 unsupported 六位代码即使存在伪缓存也不会被读取。

    Args:
        tmp_path: pytest 临时目录 fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 unsupported code 绕过 classifier 读取缓存时抛出。
    """

    path = tmp_path / "index" / "999999_history.json"
    _write_history_cache(path, _history(index_code="999999", index_name="伪造指数"))
    cache = ThermometerHistoryCache(root_dir=tmp_path)

    assert cache.load("999999", allow_stale=True) is None


def test_thermometer_history_cache_rejects_unsupported_save(tmp_path: Path) -> None:
    """验证 unsupported 代码不能写入缓存。

    Args:
        tmp_path: pytest 临时目录 fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 unsupported code 被保存时抛出。
    """

    cache = ThermometerHistoryCache(root_dir=tmp_path)

    with pytest.raises(ValueError, match="不支持的温度计缓存代码"):
        cache.save(_history(index_code="999999", index_name="伪造指数"))


def _history(index_code: str = "000300", index_name: str = "沪深300") -> PePbHistory:
    """构造测试 PE/PB 历史。

    Args:
        index_code: 指数或市场代码。
        index_name: 指数或市场名称。

    Returns:
        测试历史。

    Raises:
        无显式抛出。
    """

    return PePbHistory(
        index_code=index_code,
        index_name=index_name,
        source="fixture",
        points=tuple(
            PePbPoint(
                date=f"2026-05-{day:02d}",
                pe=Decimal(day),
                pb=Decimal(day) / Decimal("10"),
            )
            for day in range(1, 31)
        ),
    )


def _write_history_cache(path: Path, history: PePbHistory) -> None:
    """写入测试用历史缓存文件。

    Args:
        path: 缓存文件路径。
        history: 待写入历史。

    Returns:
        无返回值。

    Raises:
        OSError: 目录创建或写入失败时抛出。
    """

    fetched_at = datetime.now(timezone.utc).isoformat()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "index_code": history.index_code,
                "index_name": history.index_name,
                "source": history.source,
                "fetched_at": history.fetched_at,
                "cache_updated_at": fetched_at,
                "points": [
                    {"date": point.date, "pe": str(point.pe), "pb": str(point.pb)}
                    for point in history.points
                ],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
