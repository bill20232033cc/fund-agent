"""自建温度计数据源测试。"""

from __future__ import annotations

import asyncio
from datetime import date
from decimal import Decimal

import pytest

from fund_agent.fund.data.thermometer_source import (
    ALL_A_MARKET_CODE,
    ALL_A_MARKET_NAME,
    ALL_A_SOURCE_NAME,
    AkshareAllAMarketThermometerSource,
    AkshareIndexThermometerSource,
    AkshareThermometerSource,
    ThermometerSourceError,
    classify_thermometer_code,
    is_supported_index_code,
    is_supported_thermometer_code,
    thermometer_display_name,
)


class _FakeFrame:
    """DataFrame-like 测试对象。"""

    def __init__(self, records: list[dict[str, object]]) -> None:
        """初始化 fake frame。

        Args:
            records: records 数据。

        Returns:
            无返回值。

        Raises:
            无显式抛出。
        """

        self._records = records

    def to_dict(self, *, orient: str) -> list[dict[str, object]]:
        """返回 records。

        Args:
            orient: 输出方向，必须为 `records`。

        Returns:
            records 数据。

        Raises:
            AssertionError: orient 不符合预期时抛出。
        """

        assert orient == "records"
        return self._records


class _RecordingFetcher:
    """记录 akshare symbol 的 fake fetcher。"""

    def __init__(self, records: list[dict[str, object]]) -> None:
        """初始化 fake fetcher。

        Args:
            records: 待返回的 records 数据。

        Returns:
            无返回值。

        Raises:
            无显式抛出。
        """

        self.records = records
        self.symbols: list[str] = []

    def __call__(self, symbol: str) -> _FakeFrame:
        """记录 symbol 并返回 fake frame。

        Args:
            symbol: akshare 指数名称。

        Returns:
            fake frame。

        Raises:
            无显式抛出。
        """

        self.symbols.append(symbol)
        return _FakeFrame(self.records)


class _NoArgRecordingFetcher:
    """记录无参抓取次数的 fake fetcher。"""

    def __init__(self, records: list[dict[str, object]]) -> None:
        """初始化 fake fetcher。

        Args:
            records: 待返回的 records 数据。

        Returns:
            无返回值。

        Raises:
            无显式抛出。
        """

        self.records = records
        self.calls = 0

    def __call__(self) -> _FakeFrame:
        """记录调用并返回 fake frame。

        Args:
            无。

        Returns:
            fake frame。

        Raises:
            无显式抛出。
        """

        self.calls += 1
        return _FakeFrame(self.records)


class _FlakyNoArgFetcher:
    """按失败次数模拟 Legulegu 瞬态异常的 fake fetcher。"""

    def __init__(self, records: list[dict[str, object]], *, failures_before_success: int) -> None:
        """初始化 flaky fetcher。

        Args:
            records: 成功时返回的 records 数据。
            failures_before_success: 成功前失败次数。

        Returns:
            无返回值。

        Raises:
            无显式抛出。
        """

        self.records = records
        self.failures_before_success = failures_before_success
        self.calls = 0

    def __call__(self) -> _FakeFrame:
        """按配置失败或返回 fake frame。

        Args:
            无。

        Returns:
            fake frame。

        Raises:
            ConnectionResetError: 调用次数未超过失败阈值时抛出。
        """

        self.calls += 1
        if self.calls <= self.failures_before_success:
            raise ConnectionResetError("SSL EOF occurred in violation of protocol")
        return _FakeFrame(self.records)


def test_thermometer_code_classifier_distinguishes_index_market_and_unsupported() -> None:
    """验证 Capability 共享分类器区分指数、全 A 市场和不支持代码。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当分类或展示名不符合契约时抛出。
    """

    assert classify_thermometer_code("000300") == "index"
    assert classify_thermometer_code("000905") == "index"
    assert classify_thermometer_code(ALL_A_MARKET_CODE) == "market"
    assert classify_thermometer_code("999999") == "unsupported"
    assert is_supported_index_code("000300") is True
    assert is_supported_index_code(ALL_A_MARKET_CODE) is False
    assert is_supported_thermometer_code(ALL_A_MARKET_CODE) is True
    assert thermometer_display_name(ALL_A_MARKET_CODE) == ALL_A_MARKET_NAME
    assert thermometer_display_name("999999") == "999999"


@pytest.mark.parametrize(("index_code", "index_name"), [("000300", "沪深300"), ("000905", "中证500")])
def test_akshare_index_source_merges_pe_pb_rows(index_code: str, index_name: str) -> None:
    """验证数据源把 akshare-shaped PE/PB 表合并为历史序列。

    Args:
        index_code: 待验证的指数代码。
        index_name: 指数名称。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当合并结果不符合契约时抛出。
    """

    pe_fetcher = _RecordingFetcher(
        [
            {"日期": "2026-05-21", "滚动市盈率中位数": "20.5"},
            {"日期": "2026-05-22", "滚动市盈率中位数": "21.5"},
        ]
    )
    pb_fetcher = _RecordingFetcher(
        [
            {"日期": "2026-05-22", "市净率中位数": "2.2"},
            {"日期": "2026-05-21", "市净率中位数": "2.1"},
        ]
    )

    source = AkshareIndexThermometerSource(pe_fetcher=pe_fetcher, pb_fetcher=pb_fetcher)

    history = asyncio.run(source.load_index_history(index_code))

    assert pe_fetcher.symbols == [index_name]
    assert pb_fetcher.symbols == [index_name]
    assert history.index_code == index_code
    assert history.index_name == index_name
    assert history.source == "akshare_legulegu_index_pe_pb"
    assert [point.date for point in history.points] == ["2026-05-21", "2026-05-22"]
    assert history.points[-1].pe == Decimal("21.5")
    assert history.points[-1].pb == Decimal("2.2")


def test_akshare_index_source_rejects_unsupported_index() -> None:
    """验证 well-formed 但未纳入覆盖范围的指数仍由数据源拒绝。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当不支持指数未被拒绝时抛出。
    """

    source = AkshareIndexThermometerSource()

    with pytest.raises(ThermometerSourceError, match="暂不支持"):
        asyncio.run(source.load_index_history("999999"))


def test_akshare_index_source_fails_closed_on_schema_drift() -> None:
    """验证 PE/PB 表字段漂移会 fail-closed。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 schema drift 未被拒绝时抛出。
    """

    source = AkshareIndexThermometerSource(
        pe_fetcher=lambda symbol: _FakeFrame([{"日期": "2026-05-22", "PE": "20"}]),
        pb_fetcher=lambda symbol: _FakeFrame([{"日期": "2026-05-22", "市净率中位数": "2"}]),
    )

    with pytest.raises(ThermometerSourceError, match="缺少字段"):
        asyncio.run(source.load_index_history("000300"))


def test_akshare_index_source_rejects_bool_valuation_values() -> None:
    """验证估值字段拒绝 bool，避免被 Decimal 当作字符串兜底。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 bool 估值字段未被拒绝时抛出。
    """

    source = AkshareIndexThermometerSource(
        pe_fetcher=lambda symbol: _FakeFrame([{"日期": "2026-05-22", "滚动市盈率中位数": True}]),
        pb_fetcher=lambda symbol: _FakeFrame([{"日期": "2026-05-22", "市净率中位数": "2"}]),
    )

    with pytest.raises(ThermometerSourceError, match="不能为布尔值"):
        asyncio.run(source.load_index_history("000300"))


def test_akshare_index_source_fails_closed_on_date_schema_drift() -> None:
    """验证日期格式漂移会 fail-closed。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当日期 schema drift 未被拒绝时抛出。
    """

    source = AkshareIndexThermometerSource(
        pe_fetcher=lambda symbol: _FakeFrame([{"日期": "20260522", "滚动市盈率中位数": "20"}]),
        pb_fetcher=lambda symbol: _FakeFrame([{"日期": "20260522", "市净率中位数": "2"}]),
    )

    with pytest.raises(ThermometerSourceError, match="ISO"):
        asyncio.run(source.load_index_history("000300"))


@pytest.mark.parametrize(
    "date_text",
    [
        "2026-05-22T00:00:00",
        "2026-05-22 00:00:00",
        "2026-05-22abc",
        " 2026-05-22",
        "2026-05-22 ",
        " 2026-05-22 ",
    ],
)
def test_akshare_index_source_rejects_non_strict_iso_date_strings(date_text: str) -> None:
    """验证带时间、尾随字符或首尾空白的日期字符串会 fail-closed。

    Args:
        date_text: 待验证的非严格 ISO 日期字符串。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当非严格日期字符串未被拒绝时抛出。
    """

    source = AkshareIndexThermometerSource(
        pe_fetcher=lambda symbol: _FakeFrame([{"日期": date_text, "滚动市盈率中位数": "20"}]),
        pb_fetcher=lambda symbol: _FakeFrame([{"日期": date_text, "市净率中位数": "2"}]),
    )

    with pytest.raises(ThermometerSourceError, match="ISO"):
        asyncio.run(source.load_index_history("000300"))


def test_akshare_index_source_accepts_date_objects() -> None:
    """验证 date 对象可标准化为 ISO 日期。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 date 对象未被标准化时抛出。
    """

    source = AkshareIndexThermometerSource(
        pe_fetcher=lambda symbol: _FakeFrame([{"日期": date(2026, 5, 22), "滚动市盈率中位数": "20"}]),
        pb_fetcher=lambda symbol: _FakeFrame([{"日期": date(2026, 5, 22), "市净率中位数": "2"}]),
    )

    history = asyncio.run(source.load_index_history("000300"))

    assert history.points[0].date == "2026-05-22"


def test_akshare_all_a_source_merges_source_shaped_rows_on_common_dates() -> None:
    """验证全 A 数据源按 `date`、`middlePETTM`、`middlePB` 合并共同日期。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当合并结果不符合契约时抛出。
    """

    pe_fetcher = _NoArgRecordingFetcher(
        [
            {"date": "2026-05-22", "middlePETTM": "18.5"},
            {"date": "2026-05-20", "middlePETTM": "17.5"},
            {"date": "2026-05-21", "middlePETTM": "18.0"},
        ]
    )
    pb_fetcher = _NoArgRecordingFetcher(
        [
            {"date": "2026-05-21", "middlePB": "1.8"},
            {"date": "2026-05-22", "middlePB": "1.9"},
            {"date": "2026-05-23", "middlePB": "2.0"},
        ]
    )
    source = AkshareAllAMarketThermometerSource(pe_fetcher=pe_fetcher, pb_fetcher=pb_fetcher)

    history = asyncio.run(source.load_index_history(ALL_A_MARKET_CODE))

    assert pe_fetcher.calls == 1
    assert pb_fetcher.calls == 1
    assert history.index_code == ALL_A_MARKET_CODE
    assert history.index_name == ALL_A_MARKET_NAME
    assert history.source == ALL_A_SOURCE_NAME
    assert [point.date for point in history.points] == ["2026-05-21", "2026-05-22"]
    assert history.points[0].pe == Decimal("18.0")
    assert history.points[0].pb == Decimal("1.8")


def test_akshare_all_a_source_fails_closed_on_chinese_date_fixture() -> None:
    """验证全 A fixture 如果误用指数的中文 `日期` 字段会 fail-closed。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当中文日期字段未被拒绝时抛出。
    """

    source = AkshareAllAMarketThermometerSource(
        pe_fetcher=lambda: _FakeFrame([{"日期": "2026-05-22", "middlePETTM": "18"}]),
        pb_fetcher=lambda: _FakeFrame([{"date": "2026-05-22", "middlePB": "1.8"}]),
    )

    with pytest.raises(ThermometerSourceError, match="缺少字段"):
        asyncio.run(source.load_index_history(ALL_A_MARKET_CODE))


def test_akshare_all_a_source_uses_only_middle_columns() -> None:
    """验证全 A 解析只使用 middlePETTM 和 middlePB，忽略其它字段。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当无关字段影响输出时抛出。
    """

    source = AkshareAllAMarketThermometerSource(
        pe_fetcher=lambda: _FakeFrame(
            [
                {
                    "date": "2026-05-22",
                    "middlePETTM": "18.5",
                    "averagePETTM": "999",
                    "middlePELYR": "888",
                    "quantile": "0.99",
                }
            ]
        ),
        pb_fetcher=lambda: _FakeFrame(
            [
                {
                    "date": "2026-05-22",
                    "middlePB": "1.9",
                    "equalWeightAveragePB": "999",
                    "close": "10000",
                    "quantile": "0.01",
                }
            ]
        ),
    )

    history = asyncio.run(source.load_index_history(ALL_A_MARKET_CODE))

    assert history.points[0].pe == Decimal("18.5")
    assert history.points[0].pb == Decimal("1.9")


def test_akshare_all_a_source_fails_on_conflicting_duplicate_date() -> None:
    """验证全 A 同日期不同正数值会 fail-closed。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当重复日期冲突未被拒绝时抛出。
    """

    source = AkshareAllAMarketThermometerSource(
        pe_fetcher=lambda: _FakeFrame(
            [
                {"date": "2026-05-22", "middlePETTM": "18.5"},
                {"date": "2026-05-22", "middlePETTM": "18.6"},
            ]
        ),
        pb_fetcher=lambda: _FakeFrame([{"date": "2026-05-22", "middlePB": "1.9"}]),
    )

    with pytest.raises(ThermometerSourceError, match="重复日期冲突"):
        asyncio.run(source.load_index_history(ALL_A_MARKET_CODE))


def test_akshare_all_a_source_collapses_identical_duplicate_date() -> None:
    """验证全 A 同日期相同正数值可幂等折叠。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当相同重复行未折叠时抛出。
    """

    source = AkshareAllAMarketThermometerSource(
        pe_fetcher=lambda: _FakeFrame(
            [
                {"date": "2026-05-22", "middlePETTM": "18.50"},
                {"date": "2026-05-22", "middlePETTM": "18.5"},
            ]
        ),
        pb_fetcher=lambda: _FakeFrame(
            [
                {"date": "2026-05-22", "middlePB": "1.90"},
                {"date": "2026-05-22", "middlePB": "1.9"},
            ]
        ),
    )

    history = asyncio.run(source.load_index_history(ALL_A_MARKET_CODE))

    assert len(history.points) == 1
    assert history.points[0].pe == Decimal("18.50")
    assert history.points[0].pb == Decimal("1.90")


@pytest.mark.parametrize(
    "date_text",
    [
        "2026/05/22",
        "20260522",
        "2026-05-22T00:00:00",
        "2026-05-22 ",
        " 2026-05-22",
        "2026-02-30",
    ],
)
def test_akshare_all_a_source_rejects_non_strict_dates(date_text: str) -> None:
    """验证全 A 日期必须是严格 ISO 日期。

    Args:
        date_text: 待验证的非严格日期字符串。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当非严格日期未被拒绝时抛出。
    """

    source = AkshareAllAMarketThermometerSource(
        pe_fetcher=lambda: _FakeFrame([{"date": date_text, "middlePETTM": "18.5"}]),
        pb_fetcher=lambda: _FakeFrame([{"date": "2026-05-22", "middlePB": "1.9"}]),
    )

    with pytest.raises(ThermometerSourceError, match="ISO|日期非法"):
        asyncio.run(source.load_index_history(ALL_A_MARKET_CODE))


@pytest.mark.parametrize(
    "bad_value",
    [
        True,
        "not-a-number",
        "NaN",
        "Infinity",
        "-Infinity",
    ],
)
def test_akshare_all_a_source_rejects_invalid_numeric_values(bad_value: object) -> None:
    """验证全 A 估值字段拒绝 bool、非数值、NaN 和 Infinity。

    Args:
        bad_value: 待验证的非法估值。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当非法估值未被拒绝时抛出。
    """

    source = AkshareAllAMarketThermometerSource(
        pe_fetcher=lambda: _FakeFrame([{"date": "2026-05-22", "middlePETTM": bad_value}]),
        pb_fetcher=lambda: _FakeFrame([{"date": "2026-05-22", "middlePB": "1.9"}]),
    )

    with pytest.raises(ThermometerSourceError):
        asyncio.run(source.load_index_history(ALL_A_MARKET_CODE))


@pytest.mark.parametrize("drop_value", [None, "0", "-1"])
def test_akshare_all_a_source_drops_null_or_non_positive_until_empty_fails(drop_value: object) -> None:
    """验证全 A 空值和非正数行被丢弃，交集为空时失败。

    Args:
        drop_value: 待丢弃的空值或非正数。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当无有效共同日期未失败时抛出。
    """

    source = AkshareAllAMarketThermometerSource(
        pe_fetcher=lambda: _FakeFrame([{"date": "2026-05-22", "middlePETTM": drop_value}]),
        pb_fetcher=lambda: _FakeFrame([{"date": "2026-05-22", "middlePB": "1.9"}]),
    )

    with pytest.raises(ThermometerSourceError, match="没有有效正数记录|没有有效共同日期"):
        asyncio.run(source.load_index_history(ALL_A_MARKET_CODE))


def test_akshare_all_a_source_drops_invalid_rows_without_imputation() -> None:
    """验证全 A 缺失行只会被丢弃，不做跨日期插补。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当丢弃规则或共同日期不符合契约时抛出。
    """

    source = AkshareAllAMarketThermometerSource(
        pe_fetcher=lambda: _FakeFrame(
            [
                {"date": "2026-05-21", "middlePETTM": None},
                {"date": "2026-05-22", "middlePETTM": "18.5"},
                {"date": "2026-05-23", "middlePETTM": "-1"},
            ]
        ),
        pb_fetcher=lambda: _FakeFrame(
            [
                {"date": "2026-05-21", "middlePB": "1.8"},
                {"date": "2026-05-22", "middlePB": "1.9"},
                {"date": "2026-05-23", "middlePB": "2.0"},
            ]
        ),
    )

    history = asyncio.run(source.load_index_history(ALL_A_MARKET_CODE))

    assert [point.date for point in history.points] == ["2026-05-22"]


def test_akshare_all_a_source_retries_first_transient_failure_and_succeeds() -> None:
    """验证全 A 数据抓取第一次瞬态失败后会重试并成功。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当重试未发生或结果不符合契约时抛出。
    """

    pe_fetcher = _FlakyNoArgFetcher(
        [{"date": "2026-05-22", "middlePETTM": "18.5"}],
        failures_before_success=1,
    )
    pb_fetcher = _NoArgRecordingFetcher([{"date": "2026-05-22", "middlePB": "1.9"}])
    source = AkshareAllAMarketThermometerSource(pe_fetcher=pe_fetcher, pb_fetcher=pb_fetcher)

    history = asyncio.run(source.load_index_history(ALL_A_MARKET_CODE))

    assert pe_fetcher.calls == 2
    assert pb_fetcher.calls == 1
    assert history.points[0].date == "2026-05-22"


def test_akshare_all_a_source_raises_after_repeated_transient_failures() -> None:
    """验证全 A 数据抓取连续瞬态失败后抛出 ThermometerSourceError。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当重试耗尽未抛出统一异常时抛出。
    """

    pe_fetcher = _FlakyNoArgFetcher(
        [{"date": "2026-05-22", "middlePETTM": "18.5"}],
        failures_before_success=2,
    )
    source = AkshareAllAMarketThermometerSource(
        pe_fetcher=pe_fetcher,
        pb_fetcher=lambda: _FakeFrame([{"date": "2026-05-22", "middlePB": "1.9"}]),
    )

    with pytest.raises(ThermometerSourceError, match="全 A 估值数据获取失败"):
        asyncio.run(source.load_index_history(ALL_A_MARKET_CODE))
    assert pe_fetcher.calls == 2


def test_akshare_thermometer_source_dispatches_index_and_all_a() -> None:
    """验证复合 source 使用共享分类器分派指数和全 A 市场。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当分派结果不符合契约时抛出。
    """

    composite_source = AkshareThermometerSource(
        index_source=AkshareIndexThermometerSource(
            pe_fetcher=lambda symbol: _FakeFrame([{"日期": "2026-05-22", "滚动市盈率中位数": "20"}]),
            pb_fetcher=lambda symbol: _FakeFrame([{"日期": "2026-05-22", "市净率中位数": "2"}]),
        ),
        all_a_source=AkshareAllAMarketThermometerSource(
            pe_fetcher=lambda: _FakeFrame([{"date": "2026-05-22", "middlePETTM": "18.5"}]),
            pb_fetcher=lambda: _FakeFrame([{"date": "2026-05-22", "middlePB": "1.9"}]),
        ),
    )

    index_history = asyncio.run(composite_source.load_index_history("000300"))
    all_a_history = asyncio.run(composite_source.load_index_history(ALL_A_MARKET_CODE))

    assert index_history.index_name == "沪深300"
    assert all_a_history.index_name == ALL_A_MARKET_NAME
    with pytest.raises(ThermometerSourceError, match="暂不支持温度计代码"):
        asyncio.run(composite_source.load_index_history("999999"))
