"""P1 结构化基金数据 façade。"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Protocol

from fund_agent.fund.data.nav_data import (
    FundNavDataAdapter,
    NavDataResult,
    unavailable_nav_data_result,
)
from fund_agent.fund.data.nav_metrics import NavMaxDrawdownMetric, calculate_max_drawdown_from_nav_series
from fund_agent.fund.data.nav_models import FundNavSeries, NavDataContractError
from fund_agent.fund.data.nav_repository import FundNavRepository
from fund_agent.fund.documents import FundDocumentRepository
from fund_agent.fund.documents.models import ParsedAnnualReport
from fund_agent.fund.extractors import (
    BondRiskEvidenceValue,
    ExtractedField,
    IndexProfileValue,
    TrackingErrorValue,
    extract_bond_risk_evidence,
    extract_holdings_share_change,
    extract_manager_ownership,
    extract_performance,
    extract_profile,
)
from fund_agent.fund.fund_type import FundType
from fund_agent.fund.source_provenance import (
    PublicSourceProvenance,
    default_public_source_provenance,
    project_public_source_provenance,
)

_TRACKING_ERROR_APPLICABLE_FUND_TYPES: frozenset[FundType] = frozenset(
    ("index_fund", "enhanced_index")
)
_BOND_DRAWDOWN_SHARE_CLASS = "A"
_BOND_DRAWDOWN_MINIMUM_RECORDS = 30


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


class _NavSeriesRepository(Protocol):
    """typed NAV 序列仓库协议。"""

    async def load_nav_series(
        self,
        fund_code: str,
        *,
        share_class: str | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
        minimum_records: int | None = None,
        force_refresh: bool = False,
    ) -> FundNavSeries:
        """加载 typed NAV series。

        Args:
            fund_code: 基金代码。
            share_class: 份额类别。
            start_date: 起始日期约束。
            end_date: 截止日期约束。
            minimum_records: 最少记录数约束。
            force_refresh: 是否强制刷新 source。

        Returns:
            typed NAV series。

        Raises:
            Exception: 允许具体 repository 传播 source 或契约异常。
        """


def _default_bond_risk_evidence_field() -> ExtractedField[BondRiskEvidenceValue]:
    """构造测试夹具默认债券风险证据字段，见模板第 6 章“核心风险”。

    Args:
        无。

    Returns:
        未执行生产抽取时使用的显式缺失字段。

    Raises:
        无显式抛出。
    """

    return ExtractedField(
        value=None,
        anchors=(),
        extraction_mode="missing",
        note="bond_risk_evidence_not_extracted",
    )


@dataclass(frozen=True, slots=True)
class StructuredFundDataBundle:
    """P1 结构化基金数据包。

    Attributes:
        fund_code: 基金代码。
        report_year: 年报年份。
        basic_identity: 基础身份信息。
        product_profile: 产品本质与投资范围摘要。
        benchmark: 业绩比较基准信息。
        index_profile: 指数画像信息，见模板第 1 章“指数编制规则与成分股”。
        fee_schedule: 费率信息。
        turnover_rate: 年度换手率。
        nav_benchmark_performance: 净值增长率与基准收益率。
        investor_return: 投资者收益率披露或 fallback 状态。
        tracking_error: 年报直接披露或后续计算的跟踪误差，见模板第 2 章 R=A+B-C。
        share_change: 份额变动。
        manager_alignment: 基金经理/从业人员持有原始披露。
        manager_strategy_text: 管理人报告策略原文。
        holdings_snapshot: 前十大重仓与行业分布。
        holder_structure: 机构/个人持有人结构。
        bond_risk_evidence: 债券基金模板第 6 章“核心风险”七组证据；非债券基金为不适用缺失字段。
        nav_data: 净值数据结果。
        source_provenance: 年报公共来源 provenance，不暴露 `None`。
    """

    fund_code: str
    report_year: int
    basic_identity: ExtractedField[dict[str, object]]
    product_profile: ExtractedField[dict[str, object]]
    benchmark: ExtractedField[dict[str, object]]
    index_profile: ExtractedField[IndexProfileValue]
    fee_schedule: ExtractedField[dict[str, object]]
    turnover_rate: ExtractedField[dict[str, object]]
    nav_benchmark_performance: ExtractedField[dict[str, object]]
    investor_return: ExtractedField[dict[str, object]]
    tracking_error: ExtractedField[TrackingErrorValue]
    share_change: ExtractedField[dict[str, object]]
    manager_alignment: ExtractedField[dict[str, object]]
    manager_strategy_text: ExtractedField[dict[str, object]]
    holdings_snapshot: ExtractedField[dict[str, object]]
    holder_structure: ExtractedField[dict[str, object]]
    nav_data: NavDataResult
    source_provenance: PublicSourceProvenance = field(
        default_factory=default_public_source_provenance
    )
    bond_risk_evidence: ExtractedField[BondRiskEvidenceValue] = field(
        default_factory=_default_bond_risk_evidence_field
    )


class FundDataExtractor:
    """P1 结构化数据 façade。

    该类只负责编排文档仓库、净值适配器和章节 extractor，不直接读文件、不直接写缓存。
    """

    def __init__(
        self,
        repository: _AnnualReportRepository | None = None,
        nav_provider: _NavDataProvider | None = None,
        nav_series_repository: _NavSeriesRepository | None = None,
    ) -> None:
        """初始化结构化数据 façade。

        Args:
            repository: 年报仓库；未提供时使用 `FundDocumentRepository`。
            nav_provider: 净值数据提供者；未提供时使用 `FundNavDataAdapter`。
            nav_series_repository: typed NAV 序列仓库；未提供时使用 `FundNavRepository`。

        Returns:
            无返回值。

        Raises:
            无显式抛出。
        """

        self._repository = repository or FundDocumentRepository()
        self._nav_provider = nav_provider or FundNavDataAdapter()
        self._nav_series_repository = nav_series_repository or FundNavRepository()

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
            Exception: 允许仓库或年报 extractor 异常向上抛出；净值外部数据异常会降级为不可用结果。
        """

        report = await self._repository.load_annual_report(
            fund_code,
            report_year,
            force_refresh=force_refresh,
        )
        nav_data = await _load_nav_data_or_unavailable(
            self._nav_provider,
            fund_code,
            force_refresh=force_refresh,
        )
        profile_result = extract_profile(report)
        performance_result = extract_performance(report)
        manager_ownership_result = extract_manager_ownership(report)
        holdings_share_change_result = extract_holdings_share_change(report)
        classified_fund_type = _classified_fund_type(profile_result.basic_identity)
        drawdown_metric, drawdown_metric_error = await _load_drawdown_metric_for_bond_fund(
            self._nav_series_repository,
            fund_code=report.key.fund_code,
            report_year=report.key.year,
            classified_fund_type=classified_fund_type,
            force_refresh=force_refresh,
        )
        bond_risk_evidence = extract_bond_risk_evidence(
            report,
            classified_fund_type=classified_fund_type,
            drawdown_metric=drawdown_metric,
            drawdown_metric_error=drawdown_metric_error,
        )

        return StructuredFundDataBundle(
            fund_code=report.key.fund_code,
            report_year=report.key.year,
            basic_identity=profile_result.basic_identity,
            product_profile=profile_result.product_profile,
            benchmark=profile_result.benchmark,
            index_profile=profile_result.index_profile,
            fee_schedule=profile_result.fee_schedule,
            turnover_rate=manager_ownership_result.turnover_rate,
            nav_benchmark_performance=performance_result.nav_benchmark_performance,
            investor_return=performance_result.investor_return,
            tracking_error=_tracking_error_for_fund_type(
                performance_result.tracking_error,
                classified_fund_type,
            ),
            share_change=holdings_share_change_result.share_change,
            manager_alignment=manager_ownership_result.manager_alignment,
            manager_strategy_text=manager_ownership_result.manager_strategy_text,
            holdings_snapshot=holdings_share_change_result.holdings_snapshot,
            holder_structure=manager_ownership_result.holder_structure,
            nav_data=nav_data,
            source_provenance=project_public_source_provenance(report.metadata.source),
            bond_risk_evidence=bond_risk_evidence,
        )


async def _load_drawdown_metric_for_bond_fund(
    nav_series_repository: _NavSeriesRepository,
    *,
    fund_code: str,
    report_year: int,
    classified_fund_type: FundType | None,
    force_refresh: bool,
) -> tuple[NavMaxDrawdownMetric | None, NavDataContractError | None]:
    """为债券基金加载并计算 NAV 派生最大回撤，见模板第 6 章“核心风险”。

    Args:
        nav_series_repository: typed NAV 序列仓库。
        fund_code: 基金代码。
        report_year: 年报年份。
        classified_fund_type: 标准基金类型。
        force_refresh: 是否强制刷新 NAV source。

    Returns:
        `(metric, error)`；非债券基金或失败时 metric 为空。

    Raises:
        无显式抛出；NAV source 与指标失败都会降级为结构化缺口原因。
    """

    if classified_fund_type != "bond_fund":
        return None, None

    period_start = date(report_year, 1, 1)
    period_end = date(report_year, 12, 31)
    try:
        series = await nav_series_repository.load_nav_series(
            fund_code,
            share_class=_BOND_DRAWDOWN_SHARE_CLASS,
            start_date=period_start,
            end_date=period_end,
            minimum_records=_BOND_DRAWDOWN_MINIMUM_RECORDS,
            force_refresh=force_refresh,
        )
        metric = calculate_max_drawdown_from_nav_series(
            series,
            period_start=period_start,
            period_end=period_end,
            minimum_records=_BOND_DRAWDOWN_MINIMUM_RECORDS,
        )
    except NavDataContractError as exc:
        return None, exc
    except Exception as exc:
        return None, NavDataContractError(
            category="unavailable",
            message=f"NAV drawdown metric 不可用: {type(exc).__name__}: {exc}",
            source="nav_series_repository",
            fund_code=fund_code,
            cause=exc,
        )
    return metric, None


async def _load_nav_data_or_unavailable(
    nav_provider: _NavDataProvider,
    fund_code: str,
    *,
    force_refresh: bool,
) -> NavDataResult:
    """加载净值数据，失败时返回显式不可用结果。

    Args:
        nav_provider: 净值数据提供者。
        fund_code: 基金代码。
        force_refresh: 是否强制刷新净值缓存。

    Returns:
        净值数据结果；外部数据失败时返回 `unavailable=True` 的空结果。

    Raises:
        无显式抛出；仅捕获净值 provider 单次调用中的异常并降级。
    """

    try:
        return await nav_provider.load_nav_data(fund_code, force_refresh=force_refresh)
    except Exception as exc:
        return unavailable_nav_data_result(
            fund_code,
            reason=f"{type(exc).__name__}: {exc}",
        )


def _classified_fund_type(
    basic_identity: ExtractedField[dict[str, object]],
) -> FundType | None:
    """从基础身份字段读取标准基金类型。

    Args:
        basic_identity: 基础身份字段。

    Returns:
        标准基金类型；缺失或非法时返回 `None`。

    Raises:
        无显式抛出。
    """

    if basic_identity.value is None:
        return None
    fund_type = basic_identity.value.get("classified_fund_type")
    if fund_type in _TRACKING_ERROR_APPLICABLE_FUND_TYPES or fund_type in {
        "active_fund",
        "bond_fund",
        "qdii_fund",
        "fof_fund",
    }:
        return fund_type  # type: ignore[return-value]
    return None


def _tracking_error_for_fund_type(
    tracking_error: ExtractedField[TrackingErrorValue],
    fund_type: FundType | None,
) -> ExtractedField[TrackingErrorValue]:
    """按基金类型裁剪结构化跟踪误差适用性。

    Args:
        tracking_error: `§3` 直接披露跟踪误差字段。
        fund_type: 标准基金类型。

    Returns:
        指数/指数增强基金保留字段；其他基金返回不适用 missing。

    Raises:
        无显式抛出。
    """

    if fund_type in _TRACKING_ERROR_APPLICABLE_FUND_TYPES:
        return tracking_error
    note = "QDII 基金当前不适用 P13 跟踪误差规则" if fund_type == "qdii_fund" else "非指数基金不适用跟踪误差"
    return ExtractedField(
        value=None,
        anchors=(),
        extraction_mode="missing",
        note=note,
    )
