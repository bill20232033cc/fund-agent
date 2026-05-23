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
from fund_agent.fund.data.thermometer_source import ThermometerSourceError
from fund_agent.fund.data.thermometer_types import PePbHistory, PePbPoint, ThermometerBatchResult
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

    def __init__(
        self,
        history: PePbHistory | None = None,
        histories: dict[str, PePbHistory] | None = None,
        exc: Exception | None = None,
        failures: dict[str, Exception] | None = None,
    ) -> None:
        """初始化 fake 数据源。

        Args:
            history: 固定返回的历史序列。
            histories: 按指数代码返回的历史序列。
            exc: 固定抛出的异常。
            failures: 按指数代码抛出的异常。

        Returns:
            无返回值。

        Raises:
            无显式抛出。
        """

        self.history = history or _index_history()
        self.histories = histories or {}
        self.exc = exc
        self.failures = failures or {}
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
        if index_code in self.failures:
            raise self.failures[index_code]
        if self.exc is not None:
            raise self.exc
        return self.histories.get(index_code, self.history)


class _FailingSaveThermometerHistoryCache(ThermometerHistoryCache):
    """保存失败的温度计历史缓存。"""

    def save(self, history: PePbHistory) -> PePbHistory:
        """模拟缓存写入失败。

        Args:
            history: 待保存历史。

        Returns:
            不返回。

        Raises:
            OSError: 始终抛出。
        """

        raise OSError("read-only cache")


def test_thermometer_service_defaults_to_all_a_source(tmp_path: Path) -> None:
    """验证默认请求改走自建全 A 温度计而不是公开页 adapter。

    Args:
        tmp_path: pytest 临时目录 fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当参数转发或返回值不符合契约时抛出。
    """

    source = _FakeIndexSource(
        history=_index_history(index_code="wind_all_a", index_name="万得全 A / 全 A 市场")
    )

    def forbidden_factory(cache_dir: Path | None) -> _FakeThermometerAdapter:
        """禁止默认请求退回公开页 adapter。

        Args:
            cache_dir: Service 转发的缓存目录。

        Returns:
            不返回。

        Raises:
            AssertionError: Service 错误调用公开页 adapter 时抛出。
        """

        raise AssertionError(f"不应调用公开页 adapter：{cache_dir}")

    service = ThermometerService(
        adapter_factory=forbidden_factory,
        index_source=source,
        history_cache_factory=ThermometerHistoryCache,
    )
    result = asyncio.run(service.run(ThermometerRequest(cache_dir=tmp_path, force_refresh=True)))

    assert source.index_codes == ["wind_all_a"]
    assert result.index_code == "wind_all_a"
    assert result.index_name == "万得全 A / 全 A 市场"
    assert result.unavailable is False


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
    service = ThermometerService(
        adapter_factory=lambda cache_dir: _FakeThermometerAdapter(_available_snapshot())
    )

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


def test_thermometer_service_routes_explicit_all_a_request_to_self_owned_source(
    tmp_path: Path,
) -> None:
    """验证显式 `wind_all_a` 请求走自建全 A 温度计路径。

    Args:
        tmp_path: pytest 临时目录 fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当全 A 路由或读数不符合契约时抛出。
    """

    source = _FakeIndexSource(
        history=_index_history(index_code="wind_all_a", index_name="万得全 A / 全 A 市场")
    )
    service = ThermometerService(
        adapter_factory=lambda cache_dir: _FakeThermometerAdapter(_available_snapshot()),
        index_source=source,
        history_cache_factory=ThermometerHistoryCache,
    )

    result = asyncio.run(
        service.run(ThermometerRequest(cache_dir=tmp_path, index_code="wind_all_a"))
    )

    assert source.index_codes == ["wind_all_a"]
    assert result.index_code == "wind_all_a"
    assert result.index_name == "万得全 A / 全 A 市场"
    assert result.temperature == Decimal("100.00")
    assert result.unavailable is False


def test_thermometer_service_returns_batch_readings_in_order(tmp_path: Path) -> None:
    """验证批量指数请求由 Service 编排并按请求顺序返回。

    Args:
        tmp_path: pytest 临时目录 fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当批量读数或顺序不符合契约时抛出。
    """

    source = _FakeIndexSource(
        histories={
            "000300": _index_history(index_code="000300", index_name="沪深300"),
            "000905": _index_history(index_code="000905", index_name="中证500"),
        }
    )
    service = ThermometerService(
        index_source=source,
        history_cache_factory=lambda cache_dir: ThermometerHistoryCache(root_dir=tmp_path),
    )

    result = asyncio.run(
        service.run(ThermometerRequest(cache_dir=tmp_path, index_codes=("000300", "000905")))
    )

    assert isinstance(result, ThermometerBatchResult)
    assert source.index_codes == ["000300", "000905"]
    assert result.requested_index_codes == ("000300", "000905")
    assert [reading.index_code for reading in result.readings] == ["000300", "000905"]
    assert len(result.readings) == 2
    assert result.unavailable is False
    assert result.partial_unavailable is False
    assert result.unavailable_count == 0


def test_thermometer_service_returns_all_a_batch_readings_in_order(tmp_path: Path) -> None:
    """验证批量请求支持 `wind_all_a` 并 preserve-order de-duplicate。

    Args:
        tmp_path: pytest 临时目录 fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当全 A 批量规范化不符合契约时抛出。
    """

    source = _FakeIndexSource(
        histories={
            "wind_all_a": _index_history(
                index_code="wind_all_a", index_name="万得全 A / 全 A 市场"
            ),
            "000300": _index_history(index_code="000300", index_name="沪深300"),
            "000905": _index_history(index_code="000905", index_name="中证500"),
        }
    )
    service = ThermometerService(
        index_source=source,
        history_cache_factory=lambda cache_dir: ThermometerHistoryCache(root_dir=tmp_path),
    )

    result = asyncio.run(
        service.run(
            ThermometerRequest(
                cache_dir=tmp_path,
                index_codes=("wind_all_a", "000300", "wind_all_a", "000905"),
            )
        )
    )

    assert isinstance(result, ThermometerBatchResult)
    assert source.index_codes == ["wind_all_a", "000300", "000905"]
    assert result.requested_index_codes == ("wind_all_a", "000300", "000905")
    assert [reading.index_code for reading in result.readings] == [
        "wind_all_a",
        "000300",
        "000905",
    ]
    assert result.unavailable is False
    assert result.partial_unavailable is False


def test_thermometer_service_batch_marks_well_formed_unsupported_item_unavailable(
    tmp_path: Path,
) -> None:
    """验证 well-formed 但不支持的指数是 item-level unavailable。

    Args:
        tmp_path: pytest 临时目录 fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 unsupported code 被当成请求错误时抛出。
    """

    source = _FakeIndexSource(
        histories={"000300": _index_history(index_code="000300", index_name="沪深300")},
        failures={"999999": ThermometerSourceError("暂不支持指数：999999")},
    )
    service = ThermometerService(
        index_source=source,
        history_cache_factory=lambda cache_dir: ThermometerHistoryCache(root_dir=tmp_path),
    )

    result = asyncio.run(
        service.run(ThermometerRequest(cache_dir=tmp_path, index_codes=("000300", "999999")))
    )

    assert isinstance(result, ThermometerBatchResult)
    assert result.requested_index_codes == ("000300", "999999")
    assert result.partial_unavailable is True
    assert result.unavailable is False
    assert result.unavailable_count == 1
    assert result.readings[0].unavailable is False
    assert result.readings[1].index_code == "999999"
    assert result.readings[1].unavailable is True
    assert "暂不支持温度计代码" in str(result.readings[1].unavailable_reason)


def test_thermometer_service_rejects_unsupported_batch_item_before_fresh_cache(
    tmp_path: Path,
) -> None:
    """验证 unsupported 指数即使存在 fresh cache 也不会返回 cached available。

    Args:
        tmp_path: pytest 临时目录 fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 unsupported code 绕过支持性校验读取缓存时抛出。
    """

    _write_history_cache(
        tmp_path / "index" / "999999_history.json",
        _index_history(index_code="999999", index_name="伪造指数"),
    )
    source = _FakeIndexSource(
        histories={"000300": _index_history(index_code="000300", index_name="沪深300")}
    )
    service = ThermometerService(
        index_source=source,
        history_cache_factory=lambda cache_dir: ThermometerHistoryCache(root_dir=tmp_path),
    )

    result = asyncio.run(
        service.run(ThermometerRequest(cache_dir=tmp_path, index_codes=("000300", "999999")))
    )

    assert isinstance(result, ThermometerBatchResult)
    assert source.index_codes == ["000300"]
    assert result.partial_unavailable is True
    assert result.unavailable_count == 1
    assert result.readings[0].index_code == "000300"
    assert result.readings[0].unavailable is False
    assert result.readings[1].index_code == "999999"
    assert result.readings[1].unavailable is True
    assert result.readings[1].cached is False
    assert result.readings[1].temperature is None
    assert "暂不支持温度计代码：999999" in str(result.readings[1].unavailable_reason)


def test_thermometer_service_batch_marks_all_failed_items_unavailable(tmp_path: Path) -> None:
    """验证批量请求所有指数失败时返回整体 unavailable 数据态。

    Args:
        tmp_path: pytest 临时目录 fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当全失败状态不符合契约时抛出。
    """

    service = ThermometerService(
        index_source=_FakeIndexSource(exc=ThermometerSourceError("network down")),
        history_cache_factory=lambda cache_dir: ThermometerHistoryCache(root_dir=tmp_path),
    )

    result = asyncio.run(
        service.run(ThermometerRequest(cache_dir=tmp_path, index_codes=("000300", "000905")))
    )

    assert isinstance(result, ThermometerBatchResult)
    assert result.unavailable is True
    assert result.partial_unavailable is False
    assert result.unavailable_count == 2
    assert [reading.unavailable for reading in result.readings] == [True, True]


def test_thermometer_service_de_duplicates_batch_codes_preserving_order(tmp_path: Path) -> None:
    """验证批量指数代码 preserve-order de-duplication。

    Args:
        tmp_path: pytest 临时目录 fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当去重策略不符合契约时抛出。
    """

    source = _FakeIndexSource(
        histories={
            "000300": _index_history(index_code="000300", index_name="沪深300"),
            "000905": _index_history(index_code="000905", index_name="中证500"),
        }
    )
    service = ThermometerService(
        index_source=source,
        history_cache_factory=lambda cache_dir: ThermometerHistoryCache(root_dir=tmp_path),
    )

    result = asyncio.run(
        service.run(
            ThermometerRequest(cache_dir=tmp_path, index_codes=("000300", "000300", "000905"))
        )
    )

    assert isinstance(result, ThermometerBatchResult)
    assert result.requested_index_codes == ("000300", "000905")
    assert source.index_codes == ["000300", "000905"]
    assert len(result.readings) == 2


def test_thermometer_service_rejects_mutually_exclusive_index_fields(tmp_path: Path) -> None:
    """验证 `index_code` 与 `index_codes` 互斥。

    Args:
        tmp_path: pytest 临时目录 fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当互斥字段未被拒绝时抛出。
    """

    service = ThermometerService()

    with pytest.raises(ValueError, match="不能同时设置"):
        asyncio.run(
            service.run(
                ThermometerRequest(
                    cache_dir=tmp_path,
                    index_code="000300",
                    index_codes=("000905",),
                )
            )
        )


def test_thermometer_service_rejects_unsupported_market_like_code_before_cache(
    tmp_path: Path,
) -> None:
    """验证非 `wind_all_a` 的市场样式字符串仍是 malformed 请求。

    Args:
        tmp_path: pytest 临时目录 fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 unsupported market-like code 被当成可用请求时抛出。
    """

    service = ThermometerService()

    with pytest.raises(ValueError, match="wind_all_a 或 6 位 ASCII 数字"):
        asyncio.run(service.run(ThermometerRequest(cache_dir=tmp_path, index_code="wind_market")))


@pytest.mark.parametrize(
    "index_codes",
    [
        (),
        ("000300", "abc"),
        ("000300", "wind_all_a1"),
        ("000300", ""),
        ("１２３４５６",),
        ("", "000905"),
        ("   ",),
    ],
)
def test_thermometer_service_rejects_malformed_batch_index_codes(
    tmp_path: Path, index_codes: tuple[str, ...]
) -> None:
    """验证 Service 单一规范化入口拒绝 malformed batch 请求。

    Args:
        tmp_path: pytest 临时目录 fixture。
        index_codes: 待验证的原始指数代码序列。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 malformed 请求未被拒绝时抛出。
    """

    service = ThermometerService()

    with pytest.raises(ValueError):
        asyncio.run(service.run(ThermometerRequest(cache_dir=tmp_path, index_codes=index_codes)))


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
        index_source=_FakeIndexSource(exc=ThermometerSourceError("network down")),
        history_cache_factory=lambda cache_dir: ThermometerHistoryCache(root_dir=tmp_path),
    )

    result = asyncio.run(
        service.run(ThermometerRequest(cache_dir=tmp_path, index_code="000300", force_refresh=True))
    )

    assert result.cached is True
    assert result.stale is True
    assert result.unavailable is False


def test_thermometer_service_uses_stale_all_a_cache_when_source_fails(tmp_path: Path) -> None:
    """验证全 A 数据源失败时可回退到 market namespace stale cache。

    Args:
        tmp_path: pytest 临时目录 fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当全 A stale cache 未被复用时抛出。
    """

    cache = ThermometerHistoryCache(root_dir=tmp_path)
    cache.save(_index_history(index_code="wind_all_a", index_name="万得全 A / 全 A 市场"))
    cache_path = tmp_path / "market" / "wind_all_a_history.json"
    payload = json.loads(cache_path.read_text(encoding="utf-8"))
    payload["cache_updated_at"] = (datetime.now(timezone.utc) - timedelta(days=2)).isoformat()
    cache_path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    service = ThermometerService(
        index_source=_FakeIndexSource(exc=ThermometerSourceError("network down")),
        history_cache_factory=lambda cache_dir: ThermometerHistoryCache(root_dir=tmp_path),
    )

    result = asyncio.run(
        service.run(ThermometerRequest(cache_dir=tmp_path, index_code="wind_all_a", force_refresh=True))
    )

    assert result.index_code == "wind_all_a"
    assert result.index_name == "万得全 A / 全 A 市场"
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
        index_source=_FakeIndexSource(exc=ThermometerSourceError("network down")),
        history_cache_factory=lambda cache_dir: ThermometerHistoryCache(root_dir=tmp_path),
    )

    result = asyncio.run(service.run(ThermometerRequest(cache_dir=tmp_path, index_code="000300")))

    assert result.unavailable is True
    assert result.valuation_state_candidate == "unavailable"
    assert "network down" in str(result.unavailable_reason)


def test_thermometer_service_returns_unavailable_without_all_a_cache(tmp_path: Path) -> None:
    """验证全 A 数据源失败且无缓存时返回带全 A 名称的 unavailable 读数。

    Args:
        tmp_path: pytest 临时目录 fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当失败路径不是全 A unavailable 数据态时抛出。
    """

    service = ThermometerService(
        index_source=_FakeIndexSource(exc=ThermometerSourceError("network down")),
        history_cache_factory=lambda cache_dir: ThermometerHistoryCache(root_dir=tmp_path),
    )

    result = asyncio.run(service.run(ThermometerRequest(cache_dir=tmp_path, index_code="wind_all_a")))

    assert result.index_code == "wind_all_a"
    assert result.index_name == "万得全 A / 全 A 市场"
    assert result.unavailable is True
    assert result.valuation_state_candidate == "unavailable"
    assert "network down" in str(result.unavailable_reason)


def test_thermometer_service_uses_fresh_history_when_cache_save_fails(tmp_path: Path) -> None:
    """验证缓存写失败不掩盖已成功取得的新鲜数据。

    Args:
        tmp_path: pytest 临时目录 fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当缓存写失败导致 unavailable 时抛出。
    """

    service = ThermometerService(
        index_source=_FakeIndexSource(),
        history_cache_factory=lambda cache_dir: _FailingSaveThermometerHistoryCache(
            root_dir=tmp_path
        ),
    )

    result = asyncio.run(service.run(ThermometerRequest(cache_dir=tmp_path, index_code="000300")))

    assert result.unavailable is False
    assert result.cached is False
    assert result.temperature == Decimal("100.00")


def test_thermometer_service_propagates_calculation_contract_error(tmp_path: Path) -> None:
    """验证计算契约错误不会被 stale cache 掩盖。

    Args:
        tmp_path: pytest 临时目录 fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当计算错误被包装为 unavailable 时抛出。
    """

    service = ThermometerService(
        index_source=_FakeIndexSource(history=_short_index_history()),
        history_cache_factory=lambda cache_dir: ThermometerHistoryCache(root_dir=tmp_path),
    )

    with pytest.raises(ValueError, match="样本不足"):
        asyncio.run(service.run(ThermometerRequest(cache_dir=tmp_path, index_code="000300")))


def test_thermometer_service_propagates_all_a_stale_cache_calculation_error(
    tmp_path: Path,
) -> None:
    """验证全 A stale cache 样本不足不会被包装为 unavailable。

    Args:
        tmp_path: pytest 临时目录 fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当计算契约错误被吞掉时抛出。
    """

    _write_history_cache(
        tmp_path / "market" / "wind_all_a_history.json",
        _short_index_history(index_code="wind_all_a", index_name="万得全 A / 全 A 市场"),
        cache_updated_at=(datetime.now(timezone.utc) - timedelta(days=2)).isoformat(),
    )
    service = ThermometerService(
        index_source=_FakeIndexSource(exc=ThermometerSourceError("network down")),
        history_cache_factory=lambda cache_dir: ThermometerHistoryCache(root_dir=tmp_path),
    )

    with pytest.raises(ValueError, match="样本不足"):
        asyncio.run(
            service.run(
                ThermometerRequest(cache_dir=tmp_path, index_code="wind_all_a", force_refresh=True)
            )
        )


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


def _index_history(index_code: str = "000300", index_name: str = "沪深300") -> PePbHistory:
    """构造自建指数温度计历史。

    Args:
        index_code: 指数或市场代码。
        index_name: 指数或市场名称。

    Returns:
        PE/PB 历史。

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


def _short_index_history(
    index_code: str = "000300", index_name: str = "沪深300"
) -> PePbHistory:
    """构造样本不足的自建指数温度计历史。

    Args:
        index_code: 指数或市场代码。
        index_name: 指数或市场名称。

    Returns:
        样本不足的 PE/PB 历史。

    Raises:
        无显式抛出。
    """

    return PePbHistory(
        index_code=index_code,
        index_name=index_name,
        source="fixture",
        points=(PePbPoint(date="2026-05-01", pe=Decimal("1"), pb=Decimal("0.1")),),
    )


def _write_history_cache(
    path: Path,
    history: PePbHistory,
    *,
    cache_updated_at: str | None = None,
) -> None:
    """写入测试用历史缓存文件。

    Args:
        path: 缓存文件路径。
        history: 待写入历史。
        cache_updated_at: 缓存更新时间；为空时使用当前 UTC 时间。

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
                "cache_updated_at": cache_updated_at or fetched_at,
                "points": [
                    {"date": point.date, "pe": str(point.pe), "pb": str(point.pb)}
                    for point in history.points
                ],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
