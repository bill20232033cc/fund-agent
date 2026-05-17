"""P1 结构化基金数据 façade。"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from fund_agent.fund.data.nav_data import FundNavDataAdapter, NavDataResult
from fund_agent.fund.documents import FundDocumentRepository
from fund_agent.fund.documents.models import ParsedAnnualReport
from fund_agent.fund.extractors import (
    ExtractedField,
    extract_holdings_share_change,
    extract_manager_ownership,
    extract_performance,
    extract_profile,
)


class _AnnualReportRepository(Protocol):
    """年报仓库协议。"""

    async def load_annual_report(
        self,
        fund_code: str,
        year: int,
        *,
        force_refresh: bool = False,
    ) -> ParsedAnnualReport:
        """加载年报。

        Args:
            fund_code: 基金代码。
            year: 年报年份。
            force_refresh: 是否强制刷新缓存。

        Returns:
            已解析年报对象。

        Raises:
            Exception: 允许具体仓库传播加载异常。
        """


class _NavDataProvider(Protocol):
    """净值数据提供者协议。"""

    async def load_nav_data(self, fund_code: str, *, force_refresh: bool = False) -> NavDataResult:
        """加载净值数据。

        Args:
            fund_code: 基金代码。
            force_refresh: 是否强制刷新缓存。

        Returns:
            净值数据结果。

        Raises:
            Exception: 允许具体适配器传播加载异常。
        """


@dataclass(frozen=True, slots=True)
class StructuredFundDataBundle:
    """P1 结构化基金数据包。

    Attributes:
        fund_code: 基金代码。
        report_year: 年报年份。
        basic_identity: 基础身份信息。
        product_profile: 产品本质与投资范围摘要。
        benchmark: 业绩比较基准信息。
        fee_schedule: 费率信息。
        turnover_rate: 年度换手率。
        nav_benchmark_performance: 净值增长率与基准收益率。
        investor_return: 投资者收益率披露或 fallback 状态。
        share_change: 份额变动。
        manager_alignment: 基金经理/从业人员持有原始披露。
        manager_strategy_text: 管理人报告策略原文。
        holdings_snapshot: 前十大重仓与行业分布。
        holder_structure: 机构/个人持有人结构。
        nav_data: 净值数据结果。
    """

    fund_code: str
    report_year: int
    basic_identity: ExtractedField[dict[str, object]]
    product_profile: ExtractedField[dict[str, object]]
    benchmark: ExtractedField[dict[str, object]]
    fee_schedule: ExtractedField[dict[str, object]]
    turnover_rate: ExtractedField[dict[str, object]]
    nav_benchmark_performance: ExtractedField[dict[str, object]]
    investor_return: ExtractedField[dict[str, object]]
    share_change: ExtractedField[dict[str, object]]
    manager_alignment: ExtractedField[dict[str, object]]
    manager_strategy_text: ExtractedField[dict[str, object]]
    holdings_snapshot: ExtractedField[dict[str, object]]
    holder_structure: ExtractedField[dict[str, object]]
    nav_data: NavDataResult


class FundDataExtractor:
    """P1 结构化数据 façade。

    该类只负责编排文档仓库、净值适配器和章节 extractor，不直接读文件、不直接写缓存。
    """

    def __init__(
        self,
        repository: _AnnualReportRepository | None = None,
        nav_provider: _NavDataProvider | None = None,
    ) -> None:
        """初始化结构化数据 façade。

        Args:
            repository: 年报仓库；未提供时使用 `FundDocumentRepository`。
            nav_provider: 净值数据提供者；未提供时使用 `FundNavDataAdapter`。

        Returns:
            无返回值。

        Raises:
            无显式抛出。
        """

        self._repository = repository or FundDocumentRepository()
        self._nav_provider = nav_provider or FundNavDataAdapter()

    async def extract(
        self,
        fund_code: str,
        report_year: int,
        *,
        force_refresh: bool = False,
    ) -> StructuredFundDataBundle:
        """抽取 P1 结构化基金数据。

        Args:
            fund_code: 基金代码。
            report_year: 年报年份。
            force_refresh: 是否强制刷新底层仓库和净值缓存。

        Returns:
            P1 结构化基金数据包。

        Raises:
            Exception: 允许仓库、净值适配器或 extractor 异常向上抛出。
        """

        report = await self._repository.load_annual_report(
            fund_code,
            report_year,
            force_refresh=force_refresh,
        )
        nav_data = await self._nav_provider.load_nav_data(fund_code, force_refresh=force_refresh)
        profile_result = extract_profile(report)
        performance_result = extract_performance(report)
        manager_ownership_result = extract_manager_ownership(report)
        holdings_share_change_result = extract_holdings_share_change(report)

        return StructuredFundDataBundle(
            fund_code=report.key.fund_code,
            report_year=report.key.year,
            basic_identity=profile_result.basic_identity,
            product_profile=profile_result.product_profile,
            benchmark=profile_result.benchmark,
            fee_schedule=profile_result.fee_schedule,
            turnover_rate=manager_ownership_result.turnover_rate,
            nav_benchmark_performance=performance_result.nav_benchmark_performance,
            investor_return=performance_result.investor_return,
            share_change=holdings_share_change_result.share_change,
            manager_alignment=manager_ownership_result.manager_alignment,
            manager_strategy_text=manager_ownership_result.manager_strategy_text,
            holdings_snapshot=holdings_share_change_result.holdings_snapshot,
            holder_structure=manager_ownership_result.holder_structure,
            nav_data=nav_data,
        )
