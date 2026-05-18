"""有知有行温度计数据适配器测试。"""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from pathlib import Path

import pytest

from fund_agent.fund.data import FundThermometerAdapter, parse_thermometer_pages
from fund_agent.fund.data.thermometer import ThermometerSnapshot

DATA_HTML = """
<html>
  <body>
    <section>
      <h1>有知有行数据</h1>
      <p>更新时间：2026-05-18 16:00</p>
      <p>全市场温度：32.5</p>
      <p>估值状态：偏低</p>
      <p>趋势：较上周下降</p>
    </section>
    <table>
      <thead>
        <tr>
          <th>指数名称</th>
          <th>代码</th>
          <th>温度</th>
          <th>内在收益率</th>
          <th>股息率</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>沪深300</td>
          <td>000300</td>
          <td>28.4</td>
          <td>8.1%</td>
          <td>2.6%</td>
        </tr>
        <tr>
          <td>中证500</td>
          <td>000905</td>
          <td>41.2</td>
          <td>10.5%</td>
          <td>1.8%</td>
        </tr>
      </tbody>
    </table>
  </body>
</html>
"""

MACRO_HTML = """
<html>
  <body>
    <p>更新时间：2026-05-18</p>
    <p>债券温度：67.8</p>
    <p>10年期国债收益率：2.25%</p>
  </body>
</html>
"""


def _fetcher_factory(calls: list[str], *, fail: bool = False):
    """构造测试 fetcher。

    Args:
        calls: 记录被请求 URL 的列表。
        fail: 是否模拟抓取失败。

    Returns:
        fake fetcher。

    Raises:
        无显式抛出。
    """

    async def _fetcher(url: str) -> str:
        """返回对应测试 HTML。

        Args:
            url: 请求 URL。

        Returns:
            HTML 文本。

        Raises:
            RuntimeError: 当 `fail=True` 时抛出。
        """

        calls.append(url)
        if fail:
            raise RuntimeError("network down")
        if url.endswith("/macro"):
            return MACRO_HTML
        return DATA_HTML

    return _fetcher


@pytest.mark.asyncio
async def test_thermometer_adapter_fetches_and_parses_market_indexes_and_macro(tmp_path: Path) -> None:
    """验证成功抓取并解析全市场、指数和宏观温度。

    Args:
        tmp_path: pytest 临时目录。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当解析结果不符合预期时抛出。
    """

    calls: list[str] = []
    adapter = FundThermometerAdapter(root_dir=tmp_path, fetcher=_fetcher_factory(calls))

    snapshot = await adapter.load_thermometer()

    assert snapshot.unavailable is False
    assert snapshot.cached is False
    assert snapshot.stale is False
    assert snapshot.source == "youzhiyouxing"
    assert snapshot.as_of_date == "2026-05-18 16:00"
    assert snapshot.market is not None
    assert snapshot.market.value == Decimal("32.5")
    assert snapshot.market.valuation_band == "偏低"
    assert snapshot.market.trend_text == "较上周下降"
    assert len(snapshot.indexes) == 2
    assert snapshot.indexes[0].name == "沪深300"
    assert snapshot.indexes[0].code == "000300"
    assert snapshot.indexes[0].temperature == Decimal("28.4")
    assert snapshot.indexes[0].intrinsic_return == Decimal("8.1")
    assert snapshot.indexes[0].dividend_yield == Decimal("2.6")
    assert snapshot.macro is not None
    assert snapshot.macro.bond_temperature == Decimal("67.8")
    assert snapshot.macro.ten_year_treasury_yield == Decimal("2.25")
    assert calls == ["https://youzhiyouxing.cn/data", "https://youzhiyouxing.cn/data/macro"]


@pytest.mark.asyncio
async def test_thermometer_adapter_reuses_fresh_cache(tmp_path: Path) -> None:
    """验证 24h 内缓存会被复用。

    Args:
        tmp_path: pytest 临时目录。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 fresh cache 未命中时抛出。
    """

    calls: list[str] = []
    adapter = FundThermometerAdapter(root_dir=tmp_path, fetcher=_fetcher_factory(calls))

    first = await adapter.load_thermometer()
    second = await adapter.load_thermometer()

    assert first.cached is False
    assert second.cached is True
    assert second.stale is False
    assert second.market is not None
    assert second.market.value == Decimal("32.5")
    assert calls == ["https://youzhiyouxing.cn/data", "https://youzhiyouxing.cn/data/macro"]


@pytest.mark.asyncio
async def test_thermometer_adapter_force_refresh_bypasses_cache(tmp_path: Path) -> None:
    """验证 force refresh 会重新抓取页面。

    Args:
        tmp_path: pytest 临时目录。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当强制刷新未重新调用 fetcher 时抛出。
    """

    calls: list[str] = []
    adapter = FundThermometerAdapter(root_dir=tmp_path, fetcher=_fetcher_factory(calls))

    await adapter.load_thermometer()
    refreshed = await adapter.load_thermometer(force_refresh=True)

    assert refreshed.cached is False
    assert calls == [
        "https://youzhiyouxing.cn/data",
        "https://youzhiyouxing.cn/data/macro",
        "https://youzhiyouxing.cn/data",
        "https://youzhiyouxing.cn/data/macro",
    ]


@pytest.mark.asyncio
async def test_thermometer_adapter_uses_stale_cache_when_fetch_fails(tmp_path: Path) -> None:
    """验证抓取失败时使用 7 天内过期缓存。

    Args:
        tmp_path: pytest 临时目录。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 stale cache 未被使用时抛出。
    """

    adapter = FundThermometerAdapter(root_dir=tmp_path, fetcher=_fetcher_factory([]))
    await adapter.load_thermometer()
    _rewrite_cache_time(tmp_path / "thermometer.json", datetime.now(timezone.utc) - timedelta(days=2))
    failing_adapter = FundThermometerAdapter(root_dir=tmp_path, fetcher=_fetcher_factory([], fail=True))

    snapshot = await failing_adapter.load_thermometer(force_refresh=True)

    assert snapshot.cached is True
    assert snapshot.stale is True
    assert snapshot.unavailable is False
    assert snapshot.source == "thermometer_cache"
    assert snapshot.market is not None
    assert snapshot.market.value == Decimal("32.5")


@pytest.mark.asyncio
async def test_thermometer_adapter_returns_unavailable_when_fetch_fails_without_cache(tmp_path: Path) -> None:
    """验证无缓存且抓取失败时返回 unavailable 快照。

    Args:
        tmp_path: pytest 临时目录。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当失败路径向外抛出或伪造可用数据时抛出。
    """

    adapter = FundThermometerAdapter(root_dir=tmp_path, fetcher=_fetcher_factory([], fail=True))

    snapshot = await adapter.load_thermometer()

    assert snapshot.unavailable is True
    assert snapshot.cached is False
    assert snapshot.market is None
    assert snapshot.indexes == ()
    assert "network down" in (snapshot.unavailable_reason or "")


@pytest.mark.asyncio
async def test_thermometer_adapter_returns_unavailable_for_malformed_html_without_cache(tmp_path: Path) -> None:
    """验证 HTML 结构不可解析且无缓存时返回 unavailable。

    Args:
        tmp_path: pytest 临时目录。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 malformed HTML 被错误标记为可用时抛出。
    """

    async def _malformed_fetcher(url: str) -> str:
        """返回不可解析 HTML。

        Args:
            url: 请求 URL。

        Returns:
            不含温度计数据的 HTML。

        Raises:
            无显式抛出。
        """

        return "<html><body><p>暂无数据</p></body></html>"

    adapter = FundThermometerAdapter(root_dir=tmp_path, fetcher=_malformed_fetcher)

    snapshot = await adapter.load_thermometer()

    assert snapshot.unavailable is True
    assert snapshot.cached is False
    assert "解析失败" in (snapshot.unavailable_reason or "")


@pytest.mark.asyncio
async def test_thermometer_adapter_returns_fetched_snapshot_when_cache_write_fails(tmp_path: Path) -> None:
    """验证缓存写入失败不阻断已抓取成功的数据。

    Args:
        tmp_path: pytest 临时目录。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当缓存失败错误污染成功抓取结果时抛出。
    """

    class FailingCacheAdapter(FundThermometerAdapter):
        """测试用缓存写入失败适配器。"""

        def _save_snapshot(self, snapshot: ThermometerSnapshot) -> None:
            """模拟缓存写入失败。

            Args:
                snapshot: 温度计快照。

            Returns:
                无返回值。

            Raises:
                OSError: 始终模拟磁盘写入失败。
            """

            raise OSError("disk readonly")

    adapter = FailingCacheAdapter(root_dir=tmp_path, fetcher=_fetcher_factory([]))

    snapshot = await adapter.load_thermometer()

    assert snapshot.unavailable is False
    assert snapshot.cached is False
    assert snapshot.market is not None
    assert snapshot.market.value == Decimal("32.5")


def test_parse_thermometer_pages_returns_unavailable_for_empty_html() -> None:
    """验证空 HTML 解析路径显式不可用。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当空 HTML 产生伪造数据时抛出。
    """

    snapshot = parse_thermometer_pages("", "")

    assert snapshot.unavailable is True
    assert snapshot.market is None
    assert snapshot.indexes == ()


def test_parse_thermometer_pages_parses_current_market_degree_layout() -> None:
    """验证当前有知有行页面无冒号温度布局可被解析。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当全市场温度布局解析失败时抛出。
    """

    html = """
    <section>
      <p>温度更新时间：2026年5月15日 20:00</p>
      <h2>全市场温度</h2>
      <div>70°</div>
      <div>高估</div>
      <div>温度不变</div>
    </section>
    """

    snapshot = parse_thermometer_pages(html, "")

    assert snapshot.unavailable is False
    assert snapshot.market is not None
    assert snapshot.market.value == Decimal("70")
    assert snapshot.market.valuation_band == "高估"
    assert snapshot.market.trend_text == "温度不变"


def test_parse_thermometer_pages_prefers_degree_market_value_over_nearby_number() -> None:
    """验证全市场温度优先读取带温度符号的数值。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当全市场温度误读邻近数字时抛出。
    """

    html = """
    <section>
      <h2>全市场温度</h2>
      <p>统计样本 1234 只基金</p>
      <div>70℃</div>
      <div>高估</div>
    </section>
    """

    snapshot = parse_thermometer_pages(html, "")

    assert snapshot.market is not None
    assert snapshot.market.value == Decimal("70")


def test_parse_thermometer_pages_parses_index_code_inside_name_cell() -> None:
    """验证当前指数表代码位于名称单元格时列位仍正确。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当指数表列位解析错误时抛出。
    """

    html = """
    <table>
      <tr>
        <th>指数名称</th>
        <th>指数温度</th>
        <th>内在收益率</th>
        <th>股息率</th>
      </tr>
      <tr>
        <td>沪深300 000300.SH</td>
        <td>59°</td>
        <td>5.11%</td>
        <td>2.42%</td>
      </tr>
    </table>
    """

    snapshot = parse_thermometer_pages(html, "")

    assert len(snapshot.indexes) == 1
    assert snapshot.indexes[0].name == "沪深300"
    assert snapshot.indexes[0].code == "000300"
    assert snapshot.indexes[0].temperature == Decimal("59")
    assert snapshot.indexes[0].intrinsic_return == Decimal("5.11")
    assert snapshot.indexes[0].dividend_yield == Decimal("2.42")


def test_parse_thermometer_pages_skips_non_index_table_before_index_table() -> None:
    """验证页面前置说明表不会被误当作指数表。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当前置非指数表污染指数解析时抛出。
    """

    html = """
    <table>
      <tr><th>温带</th><th>发生概率</th><th>买入并持有5年盈利概率</th></tr>
      <tr><td>低估</td><td>40%</td><td>95%</td></tr>
    </table>
    <table>
      <tr>
        <th>指数名称</th>
        <th>指数温度</th>
        <th>内在收益率</th>
        <th>股息率</th>
      </tr>
      <tr>
        <td>沪深300 000300.SH</td>
        <td>59°</td>
        <td>5.11%</td>
        <td>2.42%</td>
      </tr>
    </table>
    """

    snapshot = parse_thermometer_pages(html, "")

    assert len(snapshot.indexes) == 1
    assert snapshot.indexes[0].temperature == Decimal("59")
    assert snapshot.indexes[0].intrinsic_return == Decimal("5.11")
    assert snapshot.indexes[0].dividend_yield == Decimal("2.42")


def test_parse_thermometer_pages_parses_ten_year_treasury_maturity_yield_label() -> None:
    """验证当前宏观页国债到期收益率标签可被解析。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当宏观收益率标签解析失败时抛出。
    """

    html = """
    <section>
      <p>债市温度：77°</p>
      <p>10年期国债到期收益率：1.77%</p>
    </section>
    """

    snapshot = parse_thermometer_pages("", html)

    assert snapshot.macro is not None
    assert snapshot.macro.bond_temperature == Decimal("77")
    assert snapshot.macro.ten_year_treasury_yield == Decimal("1.77")


def _rewrite_cache_time(cache_path: Path, updated_at: datetime) -> None:
    """改写缓存时间戳。

    Args:
        cache_path: 缓存文件路径。
        updated_at: 新缓存时间。

    Returns:
        无返回值。

    Raises:
        OSError: 读写缓存失败时抛出。
    """

    payload = json.loads(cache_path.read_text(encoding="utf-8"))
    payload["cache_updated_at"] = updated_at.isoformat()
    cache_path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
