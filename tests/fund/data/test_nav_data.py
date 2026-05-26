"""基金净值数据适配器测试。"""

from __future__ import annotations

from pathlib import Path

import pytest

from fund_agent.fund.data.nav_data import FundNavDataAdapter, unavailable_nav_data_result


@pytest.mark.asyncio
async def test_nav_data_adapter_persists_and_reuses_cache(tmp_path: Path) -> None:
    """验证净值适配器会写入并复用自身缓存。

    Args:
        tmp_path: pytest 提供的临时目录。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当缓存未命中或重复调用 fetcher 时抛出。
    """

    calls: list[str] = []

    async def _fake_fetcher(fund_code: str) -> list[dict[str, object]]:
        """构造 fake 净值数据。

        Args:
            fund_code: 基金代码。

        Returns:
            fake 净值记录。

        Raises:
            无显式抛出。
        """

        calls.append(fund_code)
        return [{"date": "2024-12-31", "nav": "1.2345"}]

    adapter = FundNavDataAdapter(root_dir=tmp_path / "nav-cache", fetcher=_fake_fetcher)

    first_result = await adapter.load_nav_data("110011")
    second_result = await adapter.load_nav_data("110011")

    assert first_result.cached is False
    assert first_result.source == "akshare"
    assert first_result.unavailable is False
    assert first_result.unavailable_reason is None
    assert second_result.cached is True
    assert second_result.source == "nav_cache"
    assert second_result.unavailable is False
    assert second_result.unavailable_reason is None
    assert second_result.records == [{"date": "2024-12-31", "nav": "1.2345"}]
    assert calls == ["110011"]


@pytest.mark.asyncio
async def test_nav_data_adapter_force_refresh_bypasses_cache(tmp_path: Path) -> None:
    """验证强制刷新会绕过净值缓存。

    Args:
        tmp_path: pytest 提供的临时目录。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当强制刷新未重新调用 fetcher 时抛出。
    """

    calls: list[str] = []

    def _fake_fetcher(fund_code: str) -> list[dict[str, object]]:
        """构造同步 fake 净值数据。

        Args:
            fund_code: 基金代码。

        Returns:
            fake 净值记录。

        Raises:
            无显式抛出。
        """

        calls.append(fund_code)
        return [{"date": "2024-12-31", "nav": str(len(calls))}]

    adapter = FundNavDataAdapter(root_dir=tmp_path / "nav-cache", fetcher=_fake_fetcher)

    await adapter.load_nav_data("110011")
    refreshed_result = await adapter.load_nav_data("110011", force_refresh=True)

    assert refreshed_result.cached is False
    assert refreshed_result.unavailable is False
    assert refreshed_result.records == [{"date": "2024-12-31", "nav": "2"}]
    assert calls == ["110011", "110011"]


def test_unavailable_nav_data_result_returns_explicit_empty_result() -> None:
    """验证净值不可用 helper 返回兼容的空结果。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当降级结果契约不符合预期时抛出。
    """

    result = unavailable_nav_data_result(" 110011 ", reason="RuntimeError: network down")

    assert result.fund_code == "110011"
    assert result.records == []
    assert result.source == "nav_unavailable"
    assert result.cached is False
    assert result.unavailable is True
    assert result.unavailable_reason == "RuntimeError: network down"
