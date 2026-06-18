"""P1 结构化基金数据 façade。"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Any, Protocol

from fund_agent.fund.data.nav_data import (
    FundNavDataAdapter,
    NavDataResult,
    unavailable_nav_data_result,
)
from fund_agent.fund.data.nav_metrics import (
    NavMaxDrawdownMetric,
    calculate_max_drawdown_from_nav_series,
)
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
from fund_agent.fund.processors.contracts import (
    FundDisclosureDocumentIntermediate,
    FundFieldFamilyResult,
    FundProcessorDispatchKey,
    FundProcessorInput,
    FundProcessorResult,
)
from fund_agent.fund.processors.registry import FundProcessorRegistry
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


def _default_portfolio_managers_field() -> ExtractedField[dict[str, object]]:
    """构造默认基金经理任期列表缺失字段，见模板第 1/3 章。

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
        note="portfolio_managers_not_extracted",
    )


def _default_risk_characteristic_text_field() -> ExtractedField[dict[str, object]]:
    """构造默认风险收益特征文本缺失字段，见模板第 1/6 章。

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
        note="risk_characteristic_text_not_extracted",
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
        portfolio_managers: 基金经理任期列表，见模板第 1 章“产品本质”和第 3 章“基金经理画像”。
        risk_characteristic_text: 风险收益特征文本，见模板第 1 章“产品本质”和第 6 章“核心风险”。
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
    portfolio_managers: ExtractedField[dict[str, object]] = field(
        default_factory=_default_portfolio_managers_field
    )
    risk_characteristic_text: ExtractedField[dict[str, object]] = field(
        default_factory=_default_risk_characteristic_text_field
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
        processor_registry: FundProcessorRegistry | None = None,
    ) -> None:
        """初始化结构化数据 façade。

        Args:
            repository: 年报仓库；未提供时使用 `FundDocumentRepository`。
            nav_provider: 净值数据提供者；未提供时使用 `FundNavDataAdapter`。
            nav_series_repository: typed NAV 序列仓库；未提供时使用 `FundNavRepository`。
            processor_registry: processor 注册表；未提供时使用默认注册表。

        Returns:
            无返回值。

        Raises:
            无显式抛出。
        """

        self._repository = repository or FundDocumentRepository()
        self._nav_provider = nav_provider or FundNavDataAdapter()
        self._nav_series_repository = nav_series_repository or FundNavRepository()
        self._processor_registry = processor_registry or FundProcessorRegistry.create_default()

    async def extract(
        self,
        fund_code: str,
        report_year: int,
        *,
        force_refresh: bool = False,
        disclosure_intermediate: FundDisclosureDocumentIntermediate | None = None,
    ) -> StructuredFundDataBundle:
        """抽取 P1 结构化基金数据。

        Args:
            fund_code: 基金代码。
            report_year: 年报年份。
            force_refresh: 是否强制刷新底层仓库和净值缓存。
            disclosure_intermediate: 显式 opt-in 的 FundDisclosureDocument 中间态；
                仅用于 S5 Processor/Extractor admission 路由，默认不启用。

        Returns:
            P1 结构化基金数据包。

        Raises:
            Exception: 允许仓库或年报 extractor 异常向上抛出；净值外部数据异常会降级为不可用结果。
            UnsupportedFundProcessorError: 当 active fund 无可用 processor 时 fail-closed。
            RuntimeError: 当 active fund processor 结果状态为 unsupported 或 blocked 时 fail-closed。
        """

        report = await self._repository.load_annual_report(
            fund_code,
            report_year,
            force_refresh=force_refresh,
        )
        if report.key.fund_code != fund_code or report.key.year != report_year:
            raise RuntimeError(
                f"Report identity mismatch: requested {fund_code}/{report_year}, "
                f"loaded {report.key.fund_code}/{report.key.year}"
            )
        if disclosure_intermediate is not None:
            _validate_disclosure_intermediate_identity(
                disclosure_intermediate,
                fund_code=fund_code,
                report_year=report_year,
            )
        nav_data = await _load_nav_data_or_unavailable(
            self._nav_provider,
            fund_code,
            force_refresh=force_refresh,
        )
        profile_result = extract_profile(report)
        classified_fund_type = _classified_fund_type(profile_result.basic_identity)

        if disclosure_intermediate is not None:
            return await self._extract_active_fund_disclosure_via_processor(
                report=report,
                disclosure_intermediate=disclosure_intermediate,
                nav_data=nav_data,
                profile_result=profile_result,
                classified_fund_type=classified_fund_type,
                force_refresh=force_refresh,
            )

        if classified_fund_type == "active_fund":
            return await self._extract_active_fund_via_processor(
                report=report,
                fund_code=fund_code,
                report_year=report_year,
                nav_data=nav_data,
                profile_result=profile_result,
                classified_fund_type=classified_fund_type,
                force_refresh=force_refresh,
            )

        return await _extract_bundle_direct_legacy_path(
            report=report,
            nav_data=nav_data,
            profile_result=profile_result,
            classified_fund_type=classified_fund_type,
            nav_series_repository=self._nav_series_repository,
            force_refresh=force_refresh,
        )

    async def _extract_active_fund_via_processor(
        self,
        *,
        report: ParsedAnnualReport,
        fund_code: str,
        report_year: int,
        nav_data: NavDataResult,
        profile_result: Any,
        classified_fund_type: FundType,
        force_refresh: bool,
    ) -> StructuredFundDataBundle:
        """通过 processor registry 路径抽取 active fund 结构化数据。

        S2 接入：只覆盖 active_fund + annual_report + parsed_annual_report.v1。
        非 active fund 不得进入此路径。

        Raises:
            UnsupportedFundProcessorError: registry 无可用 processor。
            RuntimeError: processor 结果 unsupported 或 blocked。
        """

        dispatch_key = FundProcessorDispatchKey(
            fund_type="active_fund",
            report_type="annual_report",
            intermediate_kind="parsed_annual_report.v1",
            source_kind="annual_report",
            document_year=report.key.year,
            fund_code=report.key.fund_code,
        )
        source_provenance = project_public_source_provenance(report.metadata.source)
        processor = self._processor_registry.resolve(dispatch_key)
        processor_input = FundProcessorInput(
            context=dispatch_key,
            intermediate=report,
            source_provenance=source_provenance,
        )
        result = processor.extract(processor_input)
        if result.contract_status in ("unsupported", "blocked"):
            raise RuntimeError(
                f"active_fund processor {result.processor_id} returned "
                f"{result.contract_status}: {result.gaps}"
            )

        _validate_processor_result_identity(result, dispatch_key)

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

        return _active_processor_result_to_bundle(
            result,
            nav_data=nav_data,
            profile_result=profile_result,
            classified_fund_type=classified_fund_type,
            bond_risk_evidence=bond_risk_evidence,
            source_provenance=source_provenance,
        )

    async def _extract_active_fund_disclosure_via_processor(
        self,
        *,
        report: ParsedAnnualReport,
        disclosure_intermediate: FundDisclosureDocumentIntermediate,
        nav_data: NavDataResult,
        profile_result: Any,
        classified_fund_type: FundType | None,
        force_refresh: bool,
    ) -> StructuredFundDataBundle:
        """通过 processor registry 路由显式 FundDisclosureDocument 中间态。

        S5 仅允许显式 opt-in 的
        active_fund + annual_report + fund_disclosure_document.v1；分类仍来自已加载的
        ParsedAnnualReport，候选内容不得决定基金类型或绕过 production 年报身份校验。

        Args:
            report: 已通过 FundDocumentRepository 加载并完成身份校验的年报。
            disclosure_intermediate: 调用方显式传入的受控文档表示协议对象。
            nav_data: 已加载或降级后的 NAV 数据。
            profile_result: 基于 ParsedAnnualReport 抽取的 profile 结果。
            classified_fund_type: 从 ParsedAnnualReport 分类得到的基金类型。
            force_refresh: 是否强制刷新 NAV 派生指标来源。

        Returns:
            由 processor 结果投影得到的结构化数据包。

        Raises:
            UnsupportedFundProcessorError: registry 无可用 FDD processor。
            RuntimeError: 非 active fund、processor identity mismatch、blocked/unsupported
                status 或 provenance 缺失时 fail-closed。
        """

        if classified_fund_type != "active_fund":
            raise RuntimeError(
                "FundDisclosureDocument route supports only active_fund annual_report; "
                f"classified_fund_type={classified_fund_type}"
            )

        dispatch_key = FundProcessorDispatchKey(
            fund_type="active_fund",
            report_type="annual_report",
            intermediate_kind="fund_disclosure_document.v1",
            source_kind="annual_report",
            document_year=report.key.year,
            fund_code=report.key.fund_code,
        )
        source_provenance = disclosure_intermediate.source_provenance
        processor = self._processor_registry.resolve(dispatch_key)
        processor_input = FundProcessorInput(
            context=dispatch_key,
            intermediate=disclosure_intermediate,
            candidate_boundary=disclosure_intermediate.candidate_boundary,
            source_provenance=source_provenance,
        )
        result = processor.extract(processor_input)
        _validate_processor_result_identity(result, dispatch_key)
        if result.contract_status in ("unsupported", "blocked"):
            raise RuntimeError(
                f"fund_disclosure_document processor {result.processor_id} returned "
                f"{result.contract_status}: {result.gaps}"
            )
        if source_provenance is None:
            raise RuntimeError("FundDisclosureDocument source_provenance is required")

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

        return _active_processor_result_to_bundle(
            result,
            nav_data=nav_data,
            profile_result=profile_result,
            classified_fund_type=classified_fund_type,
            bond_risk_evidence=bond_risk_evidence,
            source_provenance=source_provenance,
        )


async def _extract_bundle_direct_legacy_path(
    *,
    report: ParsedAnnualReport,
    nav_data: NavDataResult,
    profile_result: Any,
    classified_fund_type: FundType | None,
    nav_series_repository: _NavSeriesRepository,
    force_refresh: bool,
) -> StructuredFundDataBundle:
    """S2 residual：非 active fund 直接窄 extractor 编排路径。

    该路径仅在 S2 未实现 processor 的基金类型（index、enhanced_index、bond、QDII、
    FOF 及未分类）上保留现有行为。每类基金后续需独立 planning/implementation gate
    接入对应 processor。不得被 Service/UI/Host/renderer/quality gate 直接消费。
    """

    performance_result = extract_performance(report)
    manager_ownership_result = extract_manager_ownership(report)
    holdings_share_change_result = extract_holdings_share_change(report)
    drawdown_metric, drawdown_metric_error = await _load_drawdown_metric_for_bond_fund(
        nav_series_repository,
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
        portfolio_managers=manager_ownership_result.portfolio_managers,
        risk_characteristic_text=profile_result.risk_characteristic_text,
    )


def _field_family_by_id(
    field_families: tuple[FundFieldFamilyResult, ...],
) -> dict[str, FundFieldFamilyResult]:
    """按 field_family_id 索引字段族结果。"""

    return {ff.field_family_id: ff for ff in field_families}


def _field_from_family(
    family_result: FundFieldFamilyResult | None,
    field_name: str,
) -> ExtractedField[Any]:
    """从字段族 value 投影单个 ExtractedField。

    字段缺失时返回 extraction_mode="missing" 且 note 含 source family/gap 信息。
    """

    if family_result is None:
        return ExtractedField(
            value=None,
            anchors=(),
            extraction_mode="missing",
            note=f"field_family_absent:{field_name}",
        )
    value = family_result.value.get(field_name)
    if value is None:
        return ExtractedField(
            value=None,
            anchors=(),
            extraction_mode="missing",
            note=f"field_not_in_family:{family_result.field_family_id}:{field_name}",
        )
    return ExtractedField(
        value=value,
        anchors=family_result.anchors,
        extraction_mode=family_result.extraction_mode,
        note=None,
    )


def _validate_processor_result_identity(
    result: FundProcessorResult,
    dispatch_key: FundProcessorDispatchKey,
) -> None:
    """校验 processor 结果身份与 dispatch key 一致。

    Args:
        result: processor 提取结果。
        dispatch_key: 本次 dispatch key。

    Returns:
        无返回值。

    Raises:
        RuntimeError: 任一身份字段不匹配时 fail-closed。
    """

    mismatches: list[str] = []
    if result.fund_code != dispatch_key.fund_code:
        mismatches.append(f"fund_code: result={result.fund_code} dispatch={dispatch_key.fund_code}")
    if result.report_year != dispatch_key.document_year:
        mismatches.append(
            f"report_year: result={result.report_year} dispatch={dispatch_key.document_year}"
        )
    if result.fund_type != dispatch_key.fund_type:
        mismatches.append(f"fund_type: result={result.fund_type} dispatch={dispatch_key.fund_type}")
    if result.report_type != dispatch_key.report_type:
        mismatches.append(
            f"report_type: result={result.report_type} dispatch={dispatch_key.report_type}"
        )
    if result.input_intermediate_kind != dispatch_key.intermediate_kind:
        mismatches.append(
            f"input_intermediate_kind: result={result.input_intermediate_kind} "
            f"dispatch={dispatch_key.intermediate_kind}"
        )
    if mismatches:
        raise RuntimeError(
            f"Processor result identity mismatch for {result.processor_id}: "
            + "; ".join(mismatches)
        )


def _validate_disclosure_intermediate_identity(
    disclosure_intermediate: FundDisclosureDocumentIntermediate,
    *,
    fund_code: str,
    report_year: int,
) -> None:
    """校验显式 FundDisclosureDocument 中间态身份，见模板第 1 章“产品本质”。

    Args:
        disclosure_intermediate: 显式 opt-in 的受控文档表示。
        fund_code: 请求基金代码。
        report_year: 请求年报年份。

    Returns:
        无返回值。

    Raises:
        RuntimeError: 任一身份字段不匹配时，在 NAV 和 processor resolution 前 fail-closed。
    """

    mismatches: list[str] = []
    if disclosure_intermediate.fund_code != fund_code:
        mismatches.append(
            f"fund_code: intermediate={disclosure_intermediate.fund_code} requested={fund_code}"
        )
    if disclosure_intermediate.report_year != report_year:
        mismatches.append(
            f"report_year: intermediate={disclosure_intermediate.report_year} "
            f"requested={report_year}"
        )
    if disclosure_intermediate.document_kind != "annual_report":
        mismatches.append(
            f"document_kind: intermediate={disclosure_intermediate.document_kind} "
            "required=annual_report"
        )
    if disclosure_intermediate.intermediate_kind != "fund_disclosure_document.v1":
        mismatches.append(
            f"intermediate_kind: intermediate={disclosure_intermediate.intermediate_kind} "
            "required=fund_disclosure_document.v1"
        )
    if mismatches:
        raise RuntimeError("FundDisclosureDocument identity mismatch: " + "; ".join(mismatches))


def _active_processor_result_to_bundle(
    result: FundProcessorResult,
    *,
    nav_data: NavDataResult,
    profile_result: Any,
    classified_fund_type: FundType,
    bond_risk_evidence: ExtractedField[BondRiskEvidenceValue],
    source_provenance: PublicSourceProvenance,
) -> StructuredFundDataBundle:
    """从 active_fund processor 结果投影 StructuredFundDataBundle。

    投影规则：
    - product_essence.v1 → basic_identity, product_profile, benchmark, risk_characteristic_text
    - return_attribution.v1 → fee_schedule, nav_benchmark_performance, tracking_error
    - manager_profile.v1 → portfolio_managers, turnover_rate, manager_alignment, manager_strategy_text, holdings_snapshot
    - investor_experience.v1 → investor_return, holder_structure, share_change
    - core_risk.v1 → 仅 risk_characteristic_text fallback
    - current_stage.v1 → informational/redundant，不投影
    - index_profile → 来自 bootstrap profile_result（S2 residual）
    """

    families = _field_family_by_id(result.field_families)
    product_essence = families.get("product_essence.v1")
    return_attribution = families.get("return_attribution.v1")
    manager_profile = families.get("manager_profile.v1")
    investor_experience = families.get("investor_experience.v1")
    core_risk = families.get("core_risk.v1")

    basic_identity = _field_from_family(product_essence, "basic_identity")
    product_profile = _field_from_family(product_essence, "product_profile")
    benchmark = _field_from_family(product_essence, "benchmark")
    risk_characteristic_text = _field_from_family(product_essence, "risk_characteristic_text")

    # core_risk.v1 fallback：仅 risk_characteristic_text
    if (
        risk_characteristic_text.extraction_mode == "missing"
        and risk_characteristic_text.value is None
        and core_risk is not None
    ):
        core_risk_text = core_risk.value.get("risk_characteristic_text")
        if core_risk_text is not None:
            risk_characteristic_text = ExtractedField(
                value=core_risk_text,
                anchors=core_risk.anchors,
                extraction_mode=core_risk.extraction_mode,
                note="fallback_from_core_risk.v1",
            )

    fee_schedule = _field_from_family(return_attribution, "fee_schedule")
    nav_benchmark_performance = _field_from_family(return_attribution, "nav_benchmark_performance")
    raw_tracking_error = _field_from_family(return_attribution, "tracking_error")
    tracking_error = _tracking_error_for_fund_type(raw_tracking_error, classified_fund_type)  # type: ignore[arg-type]

    portfolio_managers = _field_from_family(manager_profile, "portfolio_managers")
    turnover_rate = _field_from_family(manager_profile, "turnover_rate")
    manager_alignment = _field_from_family(manager_profile, "manager_alignment")
    manager_strategy_text = _field_from_family(manager_profile, "manager_strategy_text")
    holdings_snapshot = _field_from_family(manager_profile, "holdings_snapshot")

    investor_return = _field_from_family(investor_experience, "investor_return")
    holder_structure = _field_from_family(investor_experience, "holder_structure")
    share_change = _field_from_family(investor_experience, "share_change")

    return StructuredFundDataBundle(
        fund_code=result.fund_code,
        report_year=result.report_year,
        basic_identity=basic_identity,  # type: ignore[arg-type]
        product_profile=product_profile,  # type: ignore[arg-type]
        benchmark=benchmark,  # type: ignore[arg-type]
        index_profile=profile_result.index_profile,
        fee_schedule=fee_schedule,  # type: ignore[arg-type]
        turnover_rate=turnover_rate,  # type: ignore[arg-type]
        nav_benchmark_performance=nav_benchmark_performance,  # type: ignore[arg-type]
        investor_return=investor_return,  # type: ignore[arg-type]
        tracking_error=tracking_error,
        share_change=share_change,  # type: ignore[arg-type]
        manager_alignment=manager_alignment,  # type: ignore[arg-type]
        manager_strategy_text=manager_strategy_text,  # type: ignore[arg-type]
        holdings_snapshot=holdings_snapshot,  # type: ignore[arg-type]
        holder_structure=holder_structure,  # type: ignore[arg-type]
        nav_data=nav_data,
        source_provenance=source_provenance,
        bond_risk_evidence=bond_risk_evidence,
        portfolio_managers=portfolio_managers,  # type: ignore[arg-type]
        risk_characteristic_text=risk_characteristic_text,  # type: ignore[arg-type]
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
    note = (
        "QDII 基金当前不适用 P13 跟踪误差规则"
        if fund_type == "qdii_fund"
        else "非指数基金不适用跟踪误差"
    )
    return ExtractedField(
        value=None,
        anchors=(),
        extraction_mode="missing",
        note=note,
    )
