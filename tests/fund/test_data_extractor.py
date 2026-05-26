"""P1 结构化数据 façade 测试。"""

from __future__ import annotations

import pytest

from fund_agent.fund.data.nav_data import NavDataResult
from fund_agent.fund.data_extractor import FundDataExtractor
from fund_agent.fund.documents.models import DocumentKey, ParsedAnnualReport


class _FakeRepository:
    """测试用年报仓库。"""

    def __init__(self, result: ParsedAnnualReport | Exception) -> None:
        """初始化测试仓库。

        Args:
            result: 预置年报或待抛异常。

        Returns:
            无返回值。

        Raises:
            无显式抛出。
        """

        self.result = result
        self.calls: list[tuple[str, int, bool]] = []

    async def load_annual_report(
        self,
        fund_code: str,
        year: int,
        *,
        force_refresh: bool = False,
    ) -> ParsedAnnualReport:
        """返回预置年报或抛出预置异常。

        Args:
            fund_code: 基金代码。
            year: 年报年份。
            force_refresh: 是否强制刷新。

        Returns:
            预置年报。

        Raises:
            Exception: 当初始化传入异常时抛出。
        """

        self.calls.append((fund_code, year, force_refresh))
        if isinstance(self.result, Exception):
            raise self.result
        return self.result


class _FailingNavProvider:
    """测试用失败净值 provider。"""

    def __init__(self) -> None:
        """初始化测试 provider。

        Args:
            无。

        Returns:
            无返回值。

        Raises:
            无显式抛出。
        """

        self.calls: list[tuple[str, bool]] = []

    async def load_nav_data(self, fund_code: str, *, force_refresh: bool = False) -> NavDataResult:
        """记录调用并模拟外部净值失败。

        Args:
            fund_code: 基金代码。
            force_refresh: 是否强制刷新。

        Returns:
            无返回值。

        Raises:
            RuntimeError: 始终抛出网络失败。
        """

        self.calls.append((fund_code, force_refresh))
        raise RuntimeError("network down")


class _RecordingNavProvider:
    """测试用记录调用的净值 provider。"""

    def __init__(self) -> None:
        """初始化测试 provider。

        Args:
            无。

        Returns:
            无返回值。

        Raises:
            无显式抛出。
        """

        self.calls: list[tuple[str, bool]] = []

    async def load_nav_data(self, fund_code: str, *, force_refresh: bool = False) -> NavDataResult:
        """记录调用并返回空净值数据。

        Args:
            fund_code: 基金代码。
            force_refresh: 是否强制刷新。

        Returns:
            空净值数据。

        Raises:
            无显式抛出。
        """

        self.calls.append((fund_code, force_refresh))
        return NavDataResult(fund_code=fund_code, records=[], source="fixture", cached=False)


@pytest.mark.asyncio
async def test_data_extractor_degrades_nav_failure_without_blocking_annual_report() -> None:
    """验证 NAV 外部失败不会阻断年报结构化抽取。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 NAV 失败阻断年报抽取或原因丢失时抛出。
    """

    repository = _FakeRepository(_annual_report())
    nav_provider = _FailingNavProvider()
    extractor = FundDataExtractor(repository=repository, nav_provider=nav_provider)

    bundle = await extractor.extract("110011", 2024, force_refresh=True)

    assert repository.calls == [("110011", 2024, True)]
    assert nav_provider.calls == [("110011", True)]
    assert bundle.fund_code == "110011"
    assert bundle.basic_identity.value is not None
    assert bundle.nav_data.records == []
    assert bundle.nav_data.source == "nav_unavailable"
    assert bundle.nav_data.cached is False
    assert bundle.nav_data.unavailable is True
    assert bundle.nav_data.unavailable_reason == "RuntimeError: network down"


@pytest.mark.asyncio
async def test_data_extractor_does_not_mask_repository_failure() -> None:
    """验证年报仓库失败不会被 NAV 降级吞掉。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当仓库异常被误吞或 NAV 被误调用时抛出。
    """

    repository = _FakeRepository(RuntimeError("identity_mismatch fixture"))
    nav_provider = _RecordingNavProvider()
    extractor = FundDataExtractor(repository=repository, nav_provider=nav_provider)

    with pytest.raises(RuntimeError, match="identity_mismatch fixture"):
        await extractor.extract("110011", 2024, force_refresh=True)

    assert repository.calls == [("110011", 2024, True)]
    assert nav_provider.calls == []


def _annual_report() -> ParsedAnnualReport:
    """构造可被当前 extractor 解析的最小年报。

    Args:
        无。

    Returns:
        最小年报解析结果。

    Raises:
        无显式抛出。
    """

    raw_text = "\n".join(
        [
            "基金名称：测试成长基金",
            "基金代码：110011",
            "基金类别：混合型",
            "管理人：测试基金管理有限公司",
            "托管人：中国银行股份有限公司",
            "基金合同生效日：2020年1月1日",
            "投资目标：追求长期资本增值",
            "投资范围：主要投资股票和债券",
            "业绩比较基准：沪深300指数收益率",
            "管理费率：1.20%",
            "托管费率：0.20%",
            "基金净值增长率：10.00%",
            "业绩比较基准收益率：5.00%",
            "投资者收益率：12.00%",
            "4.4 报告期内基金投资策略和运作分析",
            "长期均衡配置消费和制造行业。",
            "4.5 管理人对宏观经济、证券市场及行业走势的简要展望",
            "保持审慎。",
            "换手率：80.00%",
            "基金经理持有本基金：0份",
            "从业人员持有本基金：100份",
            "机构投资者持有比例：30%",
            "个人投资者持有比例：70%",
            "期初份额：100",
            "期末份额：110",
            "净变动：10",
        ]
    )
    return ParsedAnnualReport(
        key=DocumentKey(fund_code="110011", year=2024),
        raw_text=raw_text,
        sections={},
        tables=(),
    )
