"""自建温度计历史缓存测试。"""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from decimal import Decimal

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
    assert cached.history.points[-1].pe == Decimal("20")
    assert cached.history.fetched_at == saved.fetched_at


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


def _history() -> PePbHistory:
    """构造测试 PE/PB 历史。

    Args:
        无。

    Returns:
        测试历史。

    Raises:
        无显式抛出。
    """

    return PePbHistory(
        index_code="000300",
        index_name="沪深300",
        source="fixture",
        points=(
            PePbPoint(date="2026-05-21", pe=Decimal("10"), pb=Decimal("1")),
            PePbPoint(date="2026-05-22", pe=Decimal("20"), pb=Decimal("2")),
        ),
    )
