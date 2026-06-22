"""基金分析 Service 测试。"""

from __future__ import annotations

from dataclasses import replace
from decimal import Decimal
from pathlib import Path
from time import perf_counter
from typing import Literal

import pytest

from fund_agent.fund.analysis.thermometer_calculator import ThermometerCalculationError
from fund_agent.fund.data.nav_data import NavDataResult
from fund_agent.fund.data.thermometer import ThermometerSnapshot
from fund_agent.fund.data.thermometer_types import ThermometerBatchResult, ThermometerReading
from fund_agent.fund.data_extractor import StructuredFundDataBundle
from fund_agent.fund.annual_evidence import (
    ANNUAL_EVIDENCE_BUNDLE_SCHEMA_VERSION,
    AnnualEvidenceBundle,
    AnnualEvidenceScopeRequest,
)
from fund_agent.fund.evidence_confirm import (
    EVIDENCE_CONFIRM_V2_SCHEMA_VERSION,
    EvidenceConfirmFactResultV2,
    EvidenceConfirmHardGate,
    EvidenceConfirmIssue,
    EvidenceConfirmResultV2,
)
from fund_agent.fund.evidence_confirm_sources import (
    EvidenceConfirmRepositoryRunRequest,
    EvidenceConfirmRepositoryRunResult,
)
from fund_agent.fund.extractors.models import (
    EvidenceAnchor,
    ExtractedField,
    IndexProfileValue,
    TrackingErrorValue,
)
from fund_agent.services import (
    FundAnalysisDeveloperOverrides,
    FundAnalysisRequest,
    FundAnalysisService,
    MultiYearAnnualAnalysisRequest,
    QualityGateBlockedError,
    QualityGateNotRunBlockedError,
)
from fund_agent.services.fund_analysis_service import EvidenceConfirmBlockedError
from fund_agent.services.thermometer_service import ThermometerRequest

_P3_S8_MAX_ANALYSIS_SECONDS = 30.0


def _developer_request(
    *,
    fund_code: str = "110011",
    report_year: int = 2024,
    equity_position: str | None = "80%",
    actual_style: str | None = "均衡",
    actual_equity_position: str | None = "70%",
    manager_tenure_months: int | None = 24,
    peer_fee_median: str | None = "1.00%",
    tracking_error: str | None = None,
    investment_amount: Decimal | str = Decimal("10000"),
    max_tolerable_loss_rate: str | None = "50%",
    valuation_state: str | None = "low",
    user_money_horizon_years: int | None = 4,
    current_stage: str | None = "规模稳定，继续观察结构性超额证据",
    final_judgment_override: str | None = None,
    force_refresh: bool = False,
    quality_gate_policy: str | None = "off",
    quality_gate_source_csv: Path | None = None,
    quality_gate_output_dir: Path | None = None,
    quality_gate_run_id: str | None = None,
    quality_gate_golden_answer_path: Path | None = None,
    evidence_confirm_policy: str | None = None,
    command_source: str = "analyze",
) -> FundAnalysisRequest:
    """构造 developer override 模式 Service 请求。

    Args:
        fund_code: 基金代码。
        report_year: 年报年份。
        equity_position: R=A+B-C 显式股票仓位。
        actual_style: 言行一致性显式风格。
        actual_equity_position: 言行一致性显式股票仓位。
        manager_tenure_months: 基金经理管理本基金月数。
        peer_fee_median: 同类总费率中位数。
        tracking_error: 指数基金跟踪误差。
        investment_amount: 压力测试投入金额。
        max_tolerable_loss_rate: 最大可承受亏损比例。
        valuation_state: 估值状态。
        user_money_horizon_years: 用户资金不用年限。
        current_stage: 当前阶段与关键变化。
        final_judgment_override: 开发覆盖最终判断。
        force_refresh: 是否强制刷新。
        quality_gate_policy: quality gate 策略。
        quality_gate_source_csv: quality gate 精选基金池 CSV 路径。
        quality_gate_output_dir: quality gate 输出目录。
        quality_gate_run_id: quality gate 运行 ID。
        quality_gate_golden_answer_path: strict golden answer JSON 路径。
        evidence_confirm_policy: Evidence Confirm developer override 策略。
        command_source: quality gate 默认运行 ID 的命令来源。

    Returns:
        developer override 模式请求。

    Raises:
        无显式抛出。
    """

    return FundAnalysisRequest(
        fund_code=fund_code,
        report_year=report_year,
        investment_amount=investment_amount,
        max_tolerable_loss_rate=max_tolerable_loss_rate,
        valuation_state=valuation_state,  # type: ignore[arg-type]
        user_money_horizon_years=user_money_horizon_years,
        force_refresh=force_refresh,
        mode="developer_override",
        developer_overrides=FundAnalysisDeveloperOverrides(
            equity_position=equity_position,
            actual_style=actual_style,
            actual_equity_position=actual_equity_position,
            manager_tenure_months=manager_tenure_months,
            peer_fee_median=peer_fee_median,
            tracking_error=tracking_error,
            current_stage=current_stage,
            final_judgment_override=final_judgment_override,  # type: ignore[arg-type]
            quality_gate_policy=quality_gate_policy,  # type: ignore[arg-type]
            quality_gate_source_csv=quality_gate_source_csv,
            quality_gate_output_dir=quality_gate_output_dir,
            quality_gate_run_id=quality_gate_run_id,
            quality_gate_golden_answer_path=quality_gate_golden_answer_path,
            evidence_confirm_policy=evidence_confirm_policy,  # type: ignore[arg-type]
        ),
        command_source=command_source,  # type: ignore[arg-type]
    )


def _anchor(section_id: str, row_locator: str, *, table_id: str | None = None) -> EvidenceAnchor:
    """构造测试证据锚点。

    Args:
        section_id: 年报章节编号。
        row_locator: 行定位说明。
        table_id: 表格编号。

    Returns:
        证据锚点。

    Raises:
        无显式抛出。
    """

    return EvidenceAnchor(
        source_kind="annual_report",
        document_year=2024,
        section_id=section_id,
        page_number=None,
        table_id=table_id,
        row_locator=row_locator,
        note=f"{row_locator}: fixture",
    )


def _field(value: dict[str, object], section_id: str, row_locator: str) -> ExtractedField[dict[str, object]]:
    """构造带证据的抽取字段。

    Args:
        value: 抽取字段值。
        section_id: 年报章节编号。
        row_locator: 行定位说明。

    Returns:
        抽取字段。

    Raises:
        无显式抛出。
    """

    return ExtractedField(
        value=value,
        anchors=(_anchor(section_id, row_locator),),
        extraction_mode="direct",
        note=None,
    )


def _bundle() -> StructuredFundDataBundle:
    """构造 Service 测试用结构化基金数据包。

    Args:
        无。

    Returns:
        P1 结构化基金数据包。

    Raises:
        无显式抛出。
    """

    missing_index_profile: ExtractedField[IndexProfileValue] = ExtractedField(
        value=None,
        anchors=(),
        extraction_mode="missing",
        note="fixture",
    )
    missing_tracking_error: ExtractedField[TrackingErrorValue] = ExtractedField(
        value=None,
        anchors=(),
        extraction_mode="missing",
        note="fixture",
    )
    return StructuredFundDataBundle(
        fund_code="110011",
        report_year=2024,
        basic_identity=_field(
            {
                "fund_name": "测试成长基金",
                "fund_code": "110011",
                "fund_category": "混合型",
                "fund_scale": "10.00亿元",
                "classified_fund_type": "active_fund",
                "classification_basis": ("基金类别：混合型",),
            },
            "§1",
            "basic_identity",
        ),
        product_profile=_field(
            {
                "investment_objective": "追求长期资本增值",
                "style_positioning": "均衡",
                "investment_scope": "主要投资股票和债券",
            },
            "§2",
            "product_profile",
        ),
        benchmark=_field({"benchmark": "沪深300指数收益率*80%+中债指数收益率*20%"}, "§2", "benchmark"),
        index_profile=missing_index_profile,
        fee_schedule=_field({"management_fee": "1.20%", "custody_fee": "0.20%"}, "§2", "fee_schedule"),
        turnover_rate=_field({"turnover_rate": "80.00%"}, "§8", "turnover_rate"),
        nav_benchmark_performance=_field(
            {"nav_growth_rate": "10.00%", "benchmark_return_rate": "5.00%"},
            "§3",
            "nav_benchmark_performance",
        ),
        investor_return=_field({"investor_return_rate": "12.00%", "disclosure_status": "direct"}, "§3", "investor_return"),
        tracking_error=missing_tracking_error,
        share_change=_field(
            {"beginning_share": "100", "ending_share": "110", "net_change": "10"},
            "§10",
            "share_change",
        ),
        manager_alignment=_field({"manager_holding": "基金经理持有本基金"}, "§9", "manager_alignment"),
        manager_strategy_text=_field({"strategy_summary": "长期均衡配置消费和制造行业"}, "§4", "manager_strategy_text"),
        holdings_snapshot=ExtractedField(
            value={
                "top_holdings": [{"股票名称": "测试股份"}],
                "top_holdings_status": "direct_top_ten",
                "top_holdings_source": "top_ten",
                "industry_distribution": [{"行业": "消费", "占比": "40%"}],
            },
            anchors=(_anchor("§8", "industry_distribution", table_id="T1"),),
            extraction_mode="direct",
            note=None,
        ),
        holder_structure=_field({"institutional_holder_ratio": "30%", "individual_holder_ratio": "70%"}, "§9", "holder_structure"),
        nav_data=NavDataResult(fund_code="110011", records=[{"date": "2024-12-31", "nav": 1.2}], source="fixture", cached=True),
    )


class _FakeExtractor:
    """Service 测试用 fake extractor。"""

    def __init__(self, bundle: StructuredFundDataBundle) -> None:
        """初始化 fake extractor。

        Args:
            bundle: 待返回的结构化基金数据包。

        Returns:
            无返回值。

        Raises:
            无显式抛出。
        """

        self.bundle = bundle
        self.calls: list[tuple[str, int, bool]] = []

    async def extract(
        self,
        fund_code: str,
        report_year: int,
        *,
        force_refresh: bool = False,
    ) -> StructuredFundDataBundle:
        """返回预置结构化数据包。

        Args:
            fund_code: 基金代码。
            report_year: 年报年份。
            force_refresh: 是否强制刷新。

        Returns:
            预置结构化数据包。

        Raises:
            无显式抛出。
        """

        self.calls.append((fund_code, report_year, force_refresh))
        return replace(self.bundle, fund_code=fund_code, report_year=report_year)


class _FakeEvidenceConfirmRunner:
    """Service 测试用 Evidence Confirm fake runner。"""

    def __init__(self, result: EvidenceConfirmRepositoryRunResult | Exception) -> None:
        """初始化 fake runner。

        Args:
            result: 运行时返回的 repository runner 结果或待抛异常。

        Returns:
            无返回值。

        Raises:
            无显式抛出。
        """

        self.result = result
        self.calls: list[EvidenceConfirmRepositoryRunRequest] = []

    async def __call__(
        self,
        request: EvidenceConfirmRepositoryRunRequest,
    ) -> EvidenceConfirmRepositoryRunResult:
        """记录请求并返回 fake 结果。

        Args:
            request: Service 构造的 Evidence Confirm runner 请求。

        Returns:
            fake repository runner 结果。

        Raises:
            Exception: 当初始化传入异常时抛出。
        """

        self.calls.append(request)
        if isinstance(self.result, Exception):
            raise self.result
        return self.result


class _FakeAnnualEvidenceLoader:
    """Service 多年年报测试用 fake loader。"""

    def __init__(self) -> None:
        """初始化 fake loader。

        Args:
            无。

        Returns:
            无返回值。

        Raises:
            无显式抛出。
        """

        self.calls: list[tuple[AnnualEvidenceScopeRequest, StructuredFundDataBundle]] = []

    async def load(
        self,
        scope: AnnualEvidenceScopeRequest,
        *,
        current_year_bundle: StructuredFundDataBundle,
    ) -> AnnualEvidenceBundle:
        """记录调用并返回最小多年证据 bundle。

        Args:
            scope: Fund 层年度证据 scope。
            current_year_bundle: 当前年份结构化数据包。

        Returns:
            最小多年证据 bundle。

        Raises:
            无显式抛出。
        """

        self.calls.append((scope, current_year_bundle))
        return AnnualEvidenceBundle(
            schema_version=ANNUAL_EVIDENCE_BUNDLE_SCHEMA_VERSION,
            fund_code=scope.fund_code,
            target_year=scope.target_year,
            canonical_years=scope.canonical_years,
            current_year_bundle=current_year_bundle,
            year_records=(),
            available_years=(scope.target_year,),
            gap_years=scope.optional_years,
            fail_closed_years=(),
            source_provenance_by_year={},
            source_documents_by_year={},
            anchors_by_year={},
            data_gaps=(),
            requirement_availability={},
            cross_year_facts=(),
            degradation_summary={"cross_year_claims_allowed": False},
            fallback_summary={"fallback_year_count": 0},
        )


class _FakeThermometerService:
    """Service 测试用 fake 自建温度计。"""

    def __init__(self, result: object | Exception) -> None:
        """初始化 fake 温度计。

        Args:
            result: 运行时返回值或待抛异常。

        Returns:
            无返回值。

        Raises:
            无显式抛出。
        """

        self.result = result
        self.calls: list[ThermometerRequest] = []

    async def run(self, request: ThermometerRequest) -> object:
        """记录请求并返回 fake 结果。

        Args:
            request: 温度计请求。

        Returns:
            fake 结果。

        Raises:
            Exception: 当初始化传入异常时抛出。
        """

        self.calls.append(request)
        if isinstance(self.result, Exception):
            raise self.result
        return self.result


def _reading(
    *,
    state: str = "low",
    unavailable: bool = False,
    index_code: str = "000300",
    index_name: str = "沪深300",
) -> ThermometerReading:
    """构造自建温度计读数。

    Args:
        state: 估值状态候选。
        unavailable: 是否不可用。
        index_code: 指数代码。
        index_name: 指数名称。

    Returns:
        温度计读数。

    Raises:
        无显式抛出。
    """

    return ThermometerReading(
        index_code=index_code,
        index_name=index_name,
        temperature=None if unavailable else Decimal("20.00"),
        pe_percentile=None if unavailable else Decimal("10.00"),
        pb_percentile=None if unavailable else Decimal("30.00"),
        valuation_state_candidate=state,  # type: ignore[arg-type]
        data_date=None if unavailable else "2024-12-31",
        lookback_start=None if unavailable else "2014-12-31",
        lookback_end=None if unavailable else "2024-12-31",
        source="akshare_index_value_hist_funddb",
        cached=False,
        stale=False,
        unavailable=unavailable,
        unavailable_reason="fixture unavailable" if unavailable else None,
        fetched_at="2025-01-01T00:00:00Z",
    )


def _index_bundle(
    *,
    fund_type: str = "index_fund",
    benchmark_text: str = "沪深300指数收益率",
    benchmark_index_name: str = "沪深300指数",
    benchmark_index_code: str | None = None,
    benchmark_component_text: tuple[str, ...] | None = None,
) -> StructuredFundDataBundle:
    """构造支持自动估值的指数基金数据包。

    Args:
        fund_type: P1 已识别的基金类型。
        benchmark_text: 业绩比较基准文本。
        benchmark_index_name: 指数画像中的基准指数名称。
        benchmark_index_code: 指数画像中的基准指数代码。
        benchmark_component_text: 指数画像中的基准成分文本。

    Returns:
        指数基金结构化数据包。

    Raises:
        无显式抛出。
    """

    bundle = _bundle()
    identity = dict(bundle.basic_identity.value or {})
    identity["classified_fund_type"] = fund_type
    identity["fund_category"] = "股票指数" if fund_type in {"index_fund", "enhanced_index"} else "混合型"
    components = benchmark_component_text or (benchmark_text,)
    index_profile = ExtractedField(
        value=IndexProfileValue(
            benchmark_text=benchmark_text,
            benchmark_identity_status="identified",
            benchmark_index_name=benchmark_index_name,
            benchmark_index_code=benchmark_index_code,
            benchmark_component_text=components,
            methodology_availability="missing",
            methodology_summary=None,
            methodology_source_title=None,
            constituents_availability="missing",
            constituents_summary=None,
            constituents_as_of_date=None,
            source_tier="benchmark_context",
            missing_reasons=(),
        ),
        anchors=(_anchor("§2", "index_profile"),),
        extraction_mode="derived",
        note=None,
    )
    return replace(
        bundle,
        basic_identity=replace(bundle.basic_identity, value=identity),
        benchmark=_field({"benchmark_text": benchmark_text}, "§2", "benchmark"),
        index_profile=index_profile,
    )


@pytest.mark.asyncio
async def test_fund_analysis_service_builds_render_and_audit_path_with_fake_extractor() -> None:
    """验证 Service 串起抽取、分析、渲染和程序审计。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 Service 未按契约编排时抛出。
    """

    extractor = _FakeExtractor(_bundle())
    evidence_runner = _FakeEvidenceConfirmRunner(_repository_run_result("pass"))
    service = FundAnalysisService(
        extractor=extractor,
        evidence_confirm_runner=evidence_runner,
    )

    result = await service.analyze(_developer_request(force_refresh=True))

    assert extractor.calls == [("110011", 2024, True)]
    assert evidence_runner.calls == []
    assert result.evidence_confirm_summary is None
    assert result.audit_result.passed
    assert result.quality_gate_result is None
    assert result.quality_gate_not_run_reason == "policy=off"
    assert result.final_judgment_decision.source == "derived"
    assert result.rabc_attribution.status == "computed"
    assert result.checklist_result.overall_signal in {"green", "yellow", "gray"}
    assert "# 0. 投资要点概览" in result.report_markdown
    assert "# 7. 是否值得持有——最终判断" in result.report_markdown
    assert "## 证据与出处" in result.report_markdown


@pytest.mark.asyncio
async def test_fund_analysis_service_checklist_returns_shared_core_without_rendering() -> None:
    """验证独立 checklist 用例复用分析核心并返回最终判断。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: checklist 未复用抽取或未返回 7 问结果时抛出。
    """

    extractor = _FakeExtractor(_bundle())
    evidence_runner = _FakeEvidenceConfirmRunner(_repository_run_result("pass"))
    service = FundAnalysisService(
        extractor=extractor,
        evidence_confirm_runner=evidence_runner,
    )

    result = await service.checklist(_developer_request(force_refresh=True))

    assert extractor.calls == [("110011", 2024, True)]
    assert evidence_runner.calls == []
    assert result.evidence_confirm_summary is None
    assert len(result.checklist_result.items) == 7
    assert result.valuation_state_resolution.state == "low"
    assert result.final_judgment_decision.derived_judgment in {
        "worth_holding",
        "needs_attention",
        "suggest_replace",
    }
    assert result.quality_gate_result is None
    assert result.quality_gate_not_run_reason == "policy=off"


@pytest.mark.asyncio
async def test_fund_analysis_service_evidence_confirm_warn_calls_runner_without_blocking() -> None:
    """验证 developer override warn 会调用 fake runner 并返回安全摘要。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: runner 未调用、摘要丢失或 warn 策略误阻断时抛出。
    """

    extractor = _FakeExtractor(_bundle())
    evidence_runner = _FakeEvidenceConfirmRunner(_repository_run_result("fail"))
    service = FundAnalysisService(
        extractor=extractor,
        evidence_confirm_runner=evidence_runner,
    )

    result = await service.analyze(
        _developer_request(
            quality_gate_policy="off",
            evidence_confirm_policy="warn",
            force_refresh=True,
        )
    )

    assert extractor.calls == [("110011", 2024, True)]
    assert len(evidence_runner.calls) == 1
    assert evidence_runner.calls[0].fund_code == "110011"
    assert evidence_runner.calls[0].report_year == 2024
    assert evidence_runner.calls[0].projection is not None
    assert evidence_runner.calls[0].force_refresh is True
    assert result.evidence_confirm_summary is not None
    assert result.evidence_confirm_summary.policy == "warn"
    assert result.evidence_confirm_summary.status == "fail"
    assert result.report_markdown


@pytest.mark.asyncio
async def test_fund_analysis_service_evidence_confirm_summary_does_not_render_to_report() -> None:
    """验证 Evidence Confirm 摘要不会写入报告 Markdown。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 EC 摘要影响渲染正文或暴露内部状态字段时抛出。
    """

    baseline_service = FundAnalysisService(extractor=_FakeExtractor(_bundle()))
    baseline_result = await baseline_service.analyze(
        _developer_request(quality_gate_policy="off")
    )
    evidence_runner = _FakeEvidenceConfirmRunner(_repository_run_result("fail"))
    service = FundAnalysisService(
        extractor=_FakeExtractor(_bundle()),
        evidence_confirm_runner=evidence_runner,
    )

    result = await service.analyze(
        _developer_request(
            quality_gate_policy="off",
            evidence_confirm_policy="warn",
        )
    )

    assert result.evidence_confirm_summary is not None
    assert result.report_markdown == baseline_result.report_markdown
    assert "Evidence Confirm" not in result.report_markdown
    assert "evidence_confirm_status" not in result.report_markdown


@pytest.mark.asyncio
async def test_fund_analysis_service_evidence_confirm_runner_exception_becomes_safe_summary() -> None:
    """验证 EC runner 异常在 warn 策略下转换为安全 fail 摘要。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: runner 异常未转换为安全摘要或报告未渲染时抛出。
    """

    evidence_runner = _FakeEvidenceConfirmRunner(RuntimeError("boom"))
    service = FundAnalysisService(
        extractor=_FakeExtractor(_bundle()),
        evidence_confirm_runner=evidence_runner,
    )

    result = await service.analyze(
        _developer_request(
            quality_gate_policy="off",
            evidence_confirm_policy="warn",
        )
    )

    assert len(evidence_runner.calls) == 1
    assert result.evidence_confirm_summary is not None
    assert result.evidence_confirm_summary.status == "fail"
    assert result.evidence_confirm_summary.not_run_reason == (
        "runner_exception:RuntimeError"
    )
    assert result.evidence_confirm_summary.pathway_status == "fail"
    assert result.evidence_confirm_summary.deterministic_status == "not_run"
    assert result.report_markdown


@pytest.mark.asyncio
async def test_fund_analysis_service_evidence_confirm_block_raises_when_gate_off() -> None:
    """验证 quality gate off 时 EC block fail 使用专属阻断异常。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 未抛出 EvidenceConfirmBlockedError 或摘要不安全时抛出。
    """

    evidence_runner = _FakeEvidenceConfirmRunner(_repository_run_result("fail"))
    service = FundAnalysisService(
        extractor=_FakeExtractor(_bundle()),
        evidence_confirm_runner=evidence_runner,
    )

    with pytest.raises(EvidenceConfirmBlockedError) as exc_info:
        await service.analyze(
            _developer_request(
                quality_gate_policy="off",
                evidence_confirm_policy="block",
            )
        )

    assert len(evidence_runner.calls) == 1
    assert exc_info.value.evidence_confirm_summary.policy == "block"
    assert exc_info.value.evidence_confirm_summary.status == "fail"
    assert exc_info.value.evidence_confirm_summary.deterministic_status == "fail"


@pytest.mark.asyncio
async def test_fund_analysis_service_quality_warn_evidence_confirm_block_fail_raises_ec_error(
    tmp_path: Path,
) -> None:
    """验证 quality gate warn 不吞掉 EC policy block 的 fail 语义。

    Args:
        tmp_path: pytest 临时目录 fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: EC fail 未按专属异常阻断时抛出。
    """

    evidence_runner = _FakeEvidenceConfirmRunner(
        _repository_run_result("fail", fund_code="004393")
    )
    service = FundAnalysisService(
        extractor=_FakeExtractor(_bundle()),
        evidence_confirm_runner=evidence_runner,
    )

    with pytest.raises(EvidenceConfirmBlockedError) as exc_info:
        await service.analyze(
            _developer_request(
                fund_code="004393",
                quality_gate_policy="warn",
                quality_gate_source_csv=Path("docs/code_20260519.csv"),
                quality_gate_output_dir=tmp_path / "gate",
                quality_gate_run_id="fixture-run",
                quality_gate_golden_answer_path=None,
                evidence_confirm_policy="block",
            )
        )

    assert len(evidence_runner.calls) == 1
    assert exc_info.value.evidence_confirm_summary.status == "fail"
    assert exc_info.value.evidence_confirm_summary.blocking_issue_ids == ("ec-v2:blocking",)


@pytest.mark.asyncio
async def test_fund_analysis_service_quality_block_evidence_confirm_fail_raises_quality_error(
    tmp_path: Path,
) -> None:
    """验证 quality gate block 下 ECQ2/block 并入既有 QualityGateBlockedError。

    Args:
        tmp_path: pytest 临时目录 fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 未抛出 quality gate 阻断或 ECQ2 未合并时抛出。
    """

    evidence_runner = _FakeEvidenceConfirmRunner(
        _repository_run_result("fail", fund_code="004393")
    )
    service = FundAnalysisService(
        extractor=_FakeExtractor(_bundle()),
        evidence_confirm_runner=evidence_runner,
    )

    with pytest.raises(QualityGateBlockedError) as exc_info:
        await service.analyze(
            _developer_request(
                fund_code="004393",
                quality_gate_policy="block",
                quality_gate_source_csv=Path("docs/code_20260519.csv"),
                quality_gate_output_dir=tmp_path / "gate",
                quality_gate_run_id="fixture-run",
                quality_gate_golden_answer_path=None,
                evidence_confirm_policy="block",
            )
        )

    assert len(evidence_runner.calls) == 1
    assert exc_info.value.quality_gate_result.status == "block"
    assert any(
        issue.rule_code == "ECQ2" and issue.severity == "block"
        for issue in exc_info.value.quality_gate_result.issues
    )


@pytest.mark.asyncio
async def test_fund_analysis_service_product_mode_rejects_evidence_confirm_override() -> None:
    """验证 product mode 下 EC developer override 仍走既有拒绝语义。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: product mode 接受 developer_overrides 时抛出。
    """

    evidence_runner = _FakeEvidenceConfirmRunner(_repository_run_result("pass"))
    service = FundAnalysisService(
        extractor=_FakeExtractor(_bundle()),
        evidence_confirm_runner=evidence_runner,
    )

    with pytest.raises(ValueError, match="product mode 不允许 developer_overrides"):
        await service.analyze(
            FundAnalysisRequest(
                fund_code="110011",
                mode="product",
                developer_overrides=FundAnalysisDeveloperOverrides(
                    evidence_confirm_policy="warn"
                ),
            )
        )

    assert evidence_runner.calls == []


def test_fund_analysis_service_evidence_confirm_boundary_static_imports() -> None:
    """验证 Service EC 集成不越过 Fund 公开边界。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 Service 引入禁止的文档/source/parser 依赖时抛出。
    """

    source = Path("fund_agent/services/fund_analysis_service.py").read_text(encoding="utf-8")
    forbidden_terms = (
        "FundDocumentRepository",
        "pdf_cache",
        "cache_helper",
        "source_adapter",
        "Docling",
        "docling",
        "pdfplumber",
    )

    for term in forbidden_terms:
        assert term not in source


@pytest.mark.asyncio
async def test_fund_analysis_service_normalizes_fund_code_before_extraction() -> None:
    """验证 Service 校验后的基金代码会规范化后再传入抽取器。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当抽取器收到未规范化基金代码时抛出。
    """

    extractor = _FakeExtractor(_bundle())
    service = FundAnalysisService(extractor=extractor)

    result = await service.checklist(
        _developer_request(
            fund_code=" 110011 ",
            force_refresh=True,
            quality_gate_policy="off",
        )
    )

    assert extractor.calls == [("110011", 2024, True)]
    assert result.structured_data.fund_code == "110011"


@pytest.mark.asyncio
async def test_fund_analysis_service_explicit_valuation_suppresses_thermometer() -> None:
    """验证显式估值输入不会调用温度计。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 显式输入仍调用温度计时抛出。
    """

    thermometer = _FakeThermometerService(_reading())
    service = FundAnalysisService(extractor=_FakeExtractor(_index_bundle()), thermometer_service=thermometer)

    result = await service.analyze(_developer_request(valuation_state="high"))

    assert thermometer.calls == []
    assert result.valuation_state_resolution.source == "explicit_user_input"
    assert result.valuation_state_resolution.state == "high"


@pytest.mark.asyncio
async def test_fund_analysis_service_explicit_unavailable_keeps_manual_gray() -> None:
    """验证显式 unavailable 是手动灰灯且不调用温度计。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 显式 unavailable 调用温度计或未灰灯时抛出。
    """

    thermometer = _FakeThermometerService(_reading())
    service = FundAnalysisService(extractor=_FakeExtractor(_index_bundle()), thermometer_service=thermometer)

    result = await service.analyze(_developer_request(valuation_state="unavailable"))

    valuation_item = next(item for item in result.checklist_result.items if item.code == "valuation")
    assert thermometer.calls == []
    assert result.valuation_state_resolution.source == "explicit_user_input"
    assert valuation_item.signal == "gray"


@pytest.mark.asyncio
async def test_fund_analysis_service_auto_calls_self_owned_thermometer_for_supported_index(
    tmp_path: Path,
) -> None:
    """验证缺省估值输入时支持指数基金会调用自建温度计。

    Args:
        tmp_path: pytest 临时目录。

    Returns:
        无返回值。

    Raises:
        AssertionError: 自动路径未调用温度计或请求字段错误时抛出。
    """

    thermometer = _FakeThermometerService(_reading(state="low"))
    service = FundAnalysisService(
        extractor=_FakeExtractor(_index_bundle(benchmark_index_code="000300")),
        thermometer_service=thermometer,
    )

    request = replace(
        _developer_request(
            valuation_state=None,
            force_refresh=True,
            quality_gate_policy="off",
        ),
        thermometer_cache_dir=tmp_path,
    )
    result = await service.analyze(request)

    assert len(thermometer.calls) == 1
    assert thermometer.calls[0].index_code == "000300"
    assert thermometer.calls[0].cache_dir == tmp_path
    assert thermometer.calls[0].force_refresh is True
    assert result.valuation_state_resolution.source == "self_owned_thermometer"
    assert result.valuation_state_resolution.state == "low"
    assert "本温度计基于有知有行公开方法论独立计算" in result.report_markdown


@pytest.mark.asyncio
async def test_fund_analysis_service_auto_calls_self_owned_thermometer_for_supported_500_index() -> None:
    """验证中证500 exact identity 会调用对应自建温度计。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 自动路径未请求中证500温度计时抛出。
    """

    thermometer = _FakeThermometerService(
        _reading(
            state="fair",
            index_code="000905",
            index_name="中证500",
        )
    )
    service = FundAnalysisService(
        extractor=_FakeExtractor(
            _index_bundle(
                fund_type="enhanced_index",
                benchmark_text="中证500指数收益率",
                benchmark_index_name="中证500指数",
                benchmark_index_code="000905",
            )
        ),
        thermometer_service=thermometer,
    )

    result = await service.analyze(_developer_request(valuation_state=None))

    assert len(thermometer.calls) == 1
    assert thermometer.calls[0].index_code == "000905"
    assert result.valuation_state_resolution.source == "self_owned_thermometer"
    assert result.valuation_state_resolution.state == "fair"


@pytest.mark.asyncio
async def test_fund_analysis_service_unsupported_exact_index_does_not_call_thermometer() -> None:
    """验证不支持的 exact benchmark code 保持灰灯且不调用温度计。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 不支持指数仍调用温度计时抛出。
    """

    thermometer = _FakeThermometerService(_reading())
    service = FundAnalysisService(
        extractor=_FakeExtractor(
            _index_bundle(
                benchmark_text="创业板指收益率",
                benchmark_index_name="创业板指",
                benchmark_index_code="399006",
            )
        ),
        thermometer_service=thermometer,
    )

    result = await service.analyze(_developer_request(valuation_state=None))

    assert thermometer.calls == []
    assert result.valuation_state_resolution.source == "unavailable_mapping"
    assert result.valuation_state_resolution.state == "unavailable"
    assert "399006" in (result.valuation_state_resolution.unavailable_reason or "")


@pytest.mark.asyncio
async def test_fund_analysis_service_ambiguous_supported_indices_do_not_call_thermometer() -> None:
    """验证多个支持权益指数的复合基准 fail-closed 且不调用温度计。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 歧义基准仍调用温度计时抛出。
    """

    thermometer = _FakeThermometerService(_reading())
    service = FundAnalysisService(
        extractor=_FakeExtractor(
            _index_bundle(
                benchmark_text="沪深300指数收益率*50%+中证500指数收益率*50%",
                benchmark_index_name="复合宽基指数",
                benchmark_component_text=("沪深300指数收益率*50%", "中证500指数收益率*50%"),
            )
        ),
        thermometer_service=thermometer,
    )

    result = await service.analyze(_developer_request(valuation_state=None))

    assert thermometer.calls == []
    assert result.valuation_state_resolution.source == "unavailable_mapping"
    assert result.valuation_state_resolution.state == "unavailable"
    assert "多个支持的权益指数" in (result.valuation_state_resolution.unavailable_reason or "")


@pytest.mark.asyncio
async def test_fund_analysis_service_unsupported_fund_type_does_not_call_thermometer() -> None:
    """验证主动基金默认自动路径返回灰灯且不调用温度计。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 不支持基金类型调用温度计时抛出。
    """

    thermometer = _FakeThermometerService(_reading())
    service = FundAnalysisService(extractor=_FakeExtractor(_bundle()), thermometer_service=thermometer)

    result = await service.analyze(_developer_request(valuation_state=None))

    assert thermometer.calls == []
    assert result.valuation_state_resolution.source == "unavailable_mapping"
    assert result.valuation_state_resolution.state == "unavailable"


@pytest.mark.asyncio
async def test_fund_analysis_service_thermometer_unavailable_reading_keeps_gray() -> None:
    """验证温度计不可用读数转为灰灯并保留来源。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 不可用读数未转灰灯时抛出。
    """

    thermometer = _FakeThermometerService(_reading(state="unavailable", unavailable=True))
    service = FundAnalysisService(extractor=_FakeExtractor(_index_bundle()), thermometer_service=thermometer)

    result = await service.analyze(_developer_request(valuation_state=None))

    assert len(thermometer.calls) == 1
    assert result.valuation_state_resolution.source == "unavailable_thermometer"
    assert result.valuation_state_resolution.state == "unavailable"
    assert result.valuation_state_resolution.unavailable_reason == "fixture unavailable"


@pytest.mark.asyncio
async def test_fund_analysis_service_thermometer_calculation_error_becomes_unavailable() -> None:
    """验证自建温度计计算错误转灰灯而不是公开页 fallback。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 计算错误未保留 unavailable reason 时抛出。
    """

    thermometer = _FakeThermometerService(ThermometerCalculationError("fixture calculation error"))
    service = FundAnalysisService(extractor=_FakeExtractor(_index_bundle()), thermometer_service=thermometer)

    result = await service.analyze(_developer_request(valuation_state=None))

    assert result.valuation_state_resolution.source == "unavailable_thermometer"
    assert result.valuation_state_resolution.state == "unavailable"
    assert "fixture calculation error" in (result.valuation_state_resolution.unavailable_reason or "")
    failure_anchor = result.valuation_state_resolution.anchors[-1]
    assert failure_anchor.source_kind == "derived"
    assert failure_anchor.section_id == "thermometer"
    assert failure_anchor.row_locator == "000300:calculation_error"
    assert "self_owned_thermometer failure" in (failure_anchor.note or "")
    assert result.valuation_state_resolution.unavailable_reason in (failure_anchor.note or "")


@pytest.mark.asyncio
async def test_fund_analysis_service_thermometer_identity_mismatch_fails_closed() -> None:
    """验证温度计返回指数与目标指数不一致时 fail-closed。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 错配指数未触发 ValueError 时抛出。
    """

    thermometer = _FakeThermometerService(
        _reading(index_code="000905", index_name="中证500")
    )
    service = FundAnalysisService(
        extractor=_FakeExtractor(_index_bundle()),
        thermometer_service=thermometer,
    )

    with pytest.raises(ValueError, match="返回指数与目标不一致"):
        await service.analyze(_developer_request(valuation_state=None))


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "bad_result",
    (
        None,
        ThermometerBatchResult(readings=(), requested_index_codes=(), generated_at=None),
        ThermometerSnapshot(
            as_of_text=None,
            as_of_date=None,
            market=None,
            indexes=(),
            macro=None,
            source="fixture",
            cached=False,
            stale=False,
            fetched_at="2025-01-01T00:00:00Z",
            unavailable=False,
            unavailable_reason=None,
        ),
    ),
)
async def test_fund_analysis_service_thermometer_contract_errors_fail_closed(
    bad_result: object,
) -> None:
    """验证 provider 返回非单指数读数时 fail-closed。

    Args:
        bad_result: 非法 provider 返回值。

    Returns:
        无返回值。

    Raises:
        AssertionError: contract error 未 fail-closed 时抛出。
    """

    thermometer = _FakeThermometerService(bad_result)
    service = FundAnalysisService(extractor=_FakeExtractor(_index_bundle()), thermometer_service=thermometer)

    with pytest.raises(ValueError, match="ThermometerReading"):
        await service.analyze(_developer_request(valuation_state=None))


@pytest.mark.asyncio
async def test_fund_analysis_service_completes_single_fund_under_p3_s8_limit_without_pdf_download() -> None:
    """验证不含 PDF 下载的单只基金完整分析低于 P3-S8 性能阈值。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 Service 编排耗时超过 30 秒或报告未通过审计时抛出。
    """

    extractor = _FakeExtractor(_bundle())
    service = FundAnalysisService(extractor=extractor)
    request = _developer_request(force_refresh=True)

    started_at = perf_counter()
    result = await service.analyze(request)
    elapsed_seconds = perf_counter() - started_at

    assert result.audit_result.passed
    assert elapsed_seconds < _P3_S8_MAX_ANALYSIS_SECONDS


@pytest.mark.asyncio
async def test_fund_analysis_service_rejects_bundle_without_fund_type() -> None:
    """验证 Service 不绕过基金类型优先约束。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当缺少基金类型仍继续分析时抛出。
    """

    bundle = _bundle()
    identity = dict(bundle.basic_identity.value or {})
    identity.pop("classified_fund_type")
    broken_bundle = replace(bundle, basic_identity=replace(bundle.basic_identity, value=identity))
    service = FundAnalysisService(extractor=_FakeExtractor(broken_bundle))

    with pytest.raises(ValueError, match="classified_fund_type"):
        await service.analyze(_developer_request(fund_code="110011", quality_gate_policy="off"))


@pytest.mark.asyncio
async def test_fund_analysis_service_warn_policy_keeps_report_and_gate_result(tmp_path: Path) -> None:
    """验证 warn 策略下 gate block 仍返回报告并携带 gate result。

    Args:
        tmp_path: pytest 临时目录 fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 warn 策略错误阻断或丢失 gate 结果时抛出。
    """

    extractor = _FakeExtractor(_low_quality_bundle())
    service = FundAnalysisService(extractor=extractor)

    result = await service.analyze(
        _developer_request(
            fund_code="004393",
            quality_gate_policy="warn",
            quality_gate_source_csv=Path("docs/code_20260519.csv"),
            quality_gate_output_dir=tmp_path / "gate",
            quality_gate_run_id="fixture-run",
            quality_gate_golden_answer_path=None,
        )
    )

    assert extractor.calls == [("004393", 2024, False)]
    assert result.quality_gate_result is not None
    assert result.quality_gate_result.status == "block"
    assert "# 0. 投资要点概览" in result.report_markdown


@pytest.mark.asyncio
async def test_fund_analysis_service_block_policy_raises_structured_error(tmp_path: Path) -> None:
    """验证 block 策略下 gate block 抛出结构化异常且只抽取一次。

    Args:
        tmp_path: pytest 临时目录 fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当阻断异常缺少 gate 结果时抛出。
    """

    extractor = _FakeExtractor(_low_quality_bundle())
    service = FundAnalysisService(extractor=extractor)

    with pytest.raises(QualityGateBlockedError) as exc_info:
        await service.analyze(
            _developer_request(
                fund_code="004393",
                quality_gate_policy="block",
                quality_gate_source_csv=Path("docs/code_20260519.csv"),
                quality_gate_output_dir=tmp_path / "gate",
                quality_gate_run_id="fixture-run",
                quality_gate_golden_answer_path=None,
            )
        )

    assert extractor.calls == [("004393", 2024, False)]
    assert exc_info.value.quality_gate_result.status == "block"
    assert exc_info.value.quality_gate_result.gate_json_path.exists()


@pytest.mark.asyncio
async def test_fund_analysis_service_block_policy_uses_normalized_fund_code_for_membership(
    tmp_path: Path,
) -> None:
    """验证 block 策略下精选池 membership 使用规范化基金代码。

    Args:
        tmp_path: pytest 临时目录 fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当带空白基金代码被误判为 quality gate not-run 时抛出。
    """

    extractor = _FakeExtractor(_low_quality_bundle())
    service = FundAnalysisService(extractor=extractor)

    with pytest.raises(QualityGateBlockedError) as exc_info:
        await service.analyze(
            _developer_request(
                fund_code=" 004393 ",
                quality_gate_policy="block",
                quality_gate_source_csv=Path("docs/code_20260519.csv"),
                quality_gate_output_dir=tmp_path / "gate",
                quality_gate_run_id="fixture-run",
                quality_gate_golden_answer_path=None,
            )
        )

    assert extractor.calls == [("004393", 2024, False)]
    assert exc_info.value.quality_gate_result.status == "block"


@pytest.mark.asyncio
async def test_fund_analysis_service_checklist_block_policy_raises_structured_error(
    tmp_path: Path,
) -> None:
    """验证 checklist 与 analyze 共享 block 策略阻断语义。

    Args:
        tmp_path: pytest 临时目录 fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 checklist 绕过 quality gate block 时抛出。
    """

    extractor = _FakeExtractor(_low_quality_bundle())
    service = FundAnalysisService(extractor=extractor)

    with pytest.raises(QualityGateBlockedError) as exc_info:
        await service.checklist(
            _developer_request(
                fund_code="004393",
                quality_gate_policy="block",
                quality_gate_source_csv=Path("docs/code_20260519.csv"),
                quality_gate_output_dir=tmp_path / "gate",
                quality_gate_run_id="fixture-run",
                quality_gate_golden_answer_path=None,
            )
        )

    assert extractor.calls == [("004393", 2024, False)]
    assert exc_info.value.quality_gate_result.status == "block"


@pytest.mark.asyncio
async def test_fund_analysis_service_block_policy_fails_when_fund_absent_from_quality_csv(
    tmp_path: Path,
) -> None:
    """验证 block 策略下基金不在 quality gate CSV 时不能成功出报告。

    Args:
        tmp_path: pytest 临时目录 fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 Service 伪造 App 类别或错误阻断时抛出。
    """

    service = FundAnalysisService(extractor=_FakeExtractor(_bundle()))

    with pytest.raises(QualityGateNotRunBlockedError, match="质量 gate 未运行") as exc_info:
        await service.analyze(
            _developer_request(
                fund_code="110011",
                quality_gate_policy="block",
                quality_gate_source_csv=_source_csv(tmp_path, "004393"),
                quality_gate_run_id="fixture-run",
                quality_gate_golden_answer_path=None,
            )
        )

    assert exc_info.value.reason == "fund_code `110011` not found in quality gate source csv"


@pytest.mark.asyncio
async def test_fund_analysis_service_rejects_invalid_fund_code_before_extraction() -> None:
    """验证 analyze 入口先拒绝非 6 位数字基金代码。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当非法基金代码穿透到抽取器时抛出。
    """

    extractor = _FakeExtractor(_bundle())
    service = FundAnalysisService(extractor=extractor)

    with pytest.raises(ValueError, match="fund_code 必须是 6 位数字"):
        await service.analyze(_developer_request(fund_code="ABCDEF", quality_gate_policy="off"))

    assert extractor.calls == []


@pytest.mark.asyncio
async def test_fund_analysis_service_warn_policy_keeps_not_run_reason_when_fund_absent(
    tmp_path: Path,
) -> None:
    """验证 warn 策略下基金不在 CSV 时保留 not-run reason。

    Args:
        tmp_path: pytest 临时目录 fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 not-run reason 丢失时抛出。
    """

    service = FundAnalysisService(extractor=_FakeExtractor(_bundle()))

    result = await service.analyze(
        _developer_request(
            fund_code="110011",
            quality_gate_policy="warn",
            quality_gate_source_csv=_source_csv(tmp_path, "004393"),
            quality_gate_run_id="fixture-run",
            quality_gate_golden_answer_path=None,
        )
    )

    assert result.quality_gate_result is None
    assert result.quality_gate_not_run_reason == (
        "fund_code `110011` not found in quality gate source csv"
    )


@pytest.mark.asyncio
async def test_fund_analysis_service_rejects_explicit_missing_golden_answer_path(
    tmp_path: Path,
) -> None:
    """验证显式 golden answer 路径不存在时不静默降级。

    Args:
        tmp_path: pytest 临时目录 fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当错误路径被静默忽略时抛出。
    """

    service = FundAnalysisService(extractor=_FakeExtractor(_bundle()))

    with pytest.raises(FileNotFoundError, match="quality_gate_golden_answer_path"):
        await service.analyze(
            _developer_request(
                fund_code="004393",
                quality_gate_policy="warn",
                quality_gate_source_csv=Path("docs/code_20260519.csv"),
                quality_gate_output_dir=tmp_path / "gate",
                quality_gate_run_id="fixture-run",
                quality_gate_golden_answer_path=tmp_path / "missing.json",
            )
        )


@pytest.mark.asyncio
async def test_fund_analysis_service_default_gate_run_id_does_not_overwrite(tmp_path: Path) -> None:
    """验证默认 quality gate 输出目录不会覆盖上一轮自动运行。

    Args:
        tmp_path: pytest 临时目录 fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当连续运行输出到同一目录时抛出。
    """

    service = FundAnalysisService(extractor=_FakeExtractor(_bundle()))
    request = _developer_request(
        fund_code="004393",
        quality_gate_policy="warn",
        quality_gate_source_csv=Path("docs/code_20260519.csv"),
        quality_gate_output_dir=None,
        quality_gate_golden_answer_path=None,
    )

    first = await service.analyze(request)
    second = await service.analyze(request)

    assert first.quality_gate_result is not None
    assert second.quality_gate_result is not None
    assert first.quality_gate_result.output_dir != second.quality_gate_result.output_dir
    assert first.quality_gate_result.output_dir.name.startswith("analyze-004393-2024-")
    assert second.quality_gate_result.output_dir.name.startswith("analyze-004393-2024-")


@pytest.mark.asyncio
async def test_fund_analysis_service_checklist_default_gate_run_id_uses_checklist_prefix(
    tmp_path: Path,
) -> None:
    """验证 checklist 默认 quality gate run_id 使用 checklist 前缀。

    Args:
        tmp_path: pytest 临时目录 fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 checklist 默认产物目录仍使用 analyze 前缀时抛出。
    """

    service = FundAnalysisService(extractor=_FakeExtractor(_bundle()))

    result = await service.checklist(
        _developer_request(
            fund_code="004393",
            quality_gate_policy="warn",
            quality_gate_source_csv=Path("docs/code_20260519.csv"),
            quality_gate_output_dir=None,
            quality_gate_golden_answer_path=None,
            command_source="analyze",
        )
    )

    assert result.quality_gate_result is not None
    assert result.quality_gate_result.output_dir.name.startswith("checklist-004393-2024-")


@pytest.mark.asyncio
async def test_fund_analysis_service_analyze_normalizes_command_source(
    tmp_path: Path,
) -> None:
    """验证 analyze 方法对 command_source 具有权威覆盖权。

    Args:
        tmp_path: pytest 临时目录 fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当直接调用者传入 checklist 仍影响 analyze run_id 时抛出。
    """

    service = FundAnalysisService(extractor=_FakeExtractor(_bundle()))

    result = await service.analyze(
        _developer_request(
            fund_code="004393",
            quality_gate_policy="warn",
            quality_gate_source_csv=Path("docs/code_20260519.csv"),
            quality_gate_output_dir=None,
            quality_gate_golden_answer_path=None,
            command_source="checklist",
        )
    )

    assert result.quality_gate_result is not None
    assert result.quality_gate_result.output_dir.name.startswith("analyze-004393-2024-")


@pytest.mark.asyncio
async def test_fund_analysis_service_explicit_gate_run_id_remains_authoritative(
    tmp_path: Path,
) -> None:
    """验证显式 quality_gate_run_id 不被 command_source 改写。

    Args:
        tmp_path: pytest 临时目录 fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当显式 run_id 被默认前缀覆盖时抛出。
    """

    service = FundAnalysisService(extractor=_FakeExtractor(_bundle()))

    result = await service.checklist(
        _developer_request(
            fund_code="004393",
            quality_gate_policy="warn",
            quality_gate_source_csv=Path("docs/code_20260519.csv"),
            quality_gate_output_dir=None,
            quality_gate_run_id="fixture-run",
            quality_gate_golden_answer_path=None,
        )
    )

    assert result.quality_gate_result is not None
    assert result.quality_gate_result.output_dir.name == "fixture-run"


@pytest.mark.asyncio
async def test_fund_analysis_service_pre_2026_missing_turnover_is_not_quality_warn(
    tmp_path: Path,
) -> None:
    """验证 2026 前缺失换手率不再投影为 quality warning。

    Args:
        tmp_path: pytest 临时目录 fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 2026 前缺失换手率仍触发 FQ2/FQ2F/FQ4 时抛出。
    """

    bundle = _bundle()
    missing_turnover = ExtractedField(
        value=None,
        anchors=(),
        extraction_mode="missing",
        note="§8 未披露可规则化抽取的换手率",
    )
    service = FundAnalysisService(extractor=_FakeExtractor(replace(bundle, turnover_rate=missing_turnover)))

    result = await service.analyze(
        _developer_request(
            fund_code="110011",
            quality_gate_policy="warn",
            quality_gate_source_csv=_source_csv(tmp_path, "110011"),
            quality_gate_output_dir=tmp_path / "gate",
            quality_gate_golden_answer_path=None,
        )
    )

    assert result.rabc_attribution.status == "missing"
    assert result.rabc_attribution.note is not None
    assert "缺少 §8 换手率" in result.rabc_attribution.note
    assert result.quality_gate_result is not None
    assert not any(
        issue.rule_code == "FQ2"
        and issue.field_name == "turnover_rate"
        for issue in result.quality_gate_result.issues
    )
    assert not any(
        issue.rule_code == "FQ2F"
        and issue.priority == "P1"
        and "turnover_rate" in issue.message
        for issue in result.quality_gate_result.issues
    )
    assert not any(issue.rule_code == "FQ4" for issue in result.quality_gate_result.issues)


@pytest.mark.asyncio
async def test_multi_year_annual_analysis_maps_service_request_to_fund_scope() -> None:
    """验证 Service 多年请求显式翻译为 Fund 年度证据 scope。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: scope 映射不符合 accepted plan 时抛出。
    """

    bundle = _bundle()
    annual_loader = _FakeAnnualEvidenceLoader()
    service = FundAnalysisService(
        extractor=_FakeExtractor(bundle),
        annual_evidence_loader=annual_loader,
    )

    result = await service.analyze_multi_year_annual(
        MultiYearAnnualAnalysisRequest(
            fund_code="110011",
            target_year=2025,
            start_year=2021,
            valuation_state="unavailable",
            quality_gate_policy="off",
        )
    )

    scope, current_year_bundle = annual_loader.calls[0]
    assert scope.required_years == (2025,)
    assert scope.optional_years == (2024, 2023, 2022, 2021)
    assert scope.canonical_years == (2025, 2024, 2023, 2022, 2021)
    assert current_year_bundle.report_year == 2025
    assert result.used_years == (2025,)
    assert result.gap_years == (2024, 2023, 2022, 2021)
    assert result.report_markdown == result.current_year_result.report_markdown
    assert result.annual_period_report.report_markdown != result.report_markdown
    assert "# 多年年报分析（2021-2025）" in result.annual_period_report.report_markdown
    assert "quality_gate_status=not_available" in result.annual_period_report.report_markdown
    assert "impact_status=insufficient_evidence" in result.annual_period_report.report_markdown


def _repository_run_result(
    status: Literal["pass", "warn", "fail"],
    *,
    fund_code: str = "110011",
    report_year: int = 2024,
) -> EvidenceConfirmRepositoryRunResult:
    """构造 Service 测试用 repository-bounded Evidence Confirm 结果。

    Args:
        status: V2 聚合状态。
        fund_code: 结果基金代码。
        report_year: 结果年报年份。

    Returns:
        最小 repository runner 结果。

    Raises:
        无显式抛出。
    """

    return EvidenceConfirmRepositoryRunResult(
        status="fail" if status == "fail" else "pass",
        pathway_status="pass",
        pathway_warning_reasons=(),
        fund_code=fund_code,
        report_year=report_year,
        source_provenance=None,
        reference_build_result=None,
        evidence_confirm_result=_v2_result(
            status,
            fund_code=fund_code,
            report_year=report_year,
        ),
        issues=(),
    )


def _v2_result(
    status: Literal["pass", "warn", "fail"],
    *,
    fund_code: str,
    report_year: int,
) -> EvidenceConfirmResultV2:
    """构造 Service 测试用 V2 Evidence Confirm 结果。

    Args:
        status: V2 聚合状态。
        fund_code: 基金代码。
        report_year: 年报年份。

    Returns:
        V2 复核结果。

    Raises:
        无显式抛出。
    """

    blocking_issue_ids = ("ec-v2:blocking",) if status == "fail" else ()
    reviewable_issue_ids = ("ec-v2:reviewable",) if status == "warn" else ()
    hard_gate = EvidenceConfirmHardGate(
        status=status,
        blocking_issue_ids=blocking_issue_ids,
        reviewable_issue_ids=reviewable_issue_ids,
        informational_issue_ids=(),
        passed_dimension_count=5 if status == "pass" else 0,
        failed_dimension_count=1 if status == "fail" else 0,
        warn_dimension_count=1 if status == "warn" else 0,
        not_applicable_dimension_count=0,
    )
    issue_ids = blocking_issue_ids or reviewable_issue_ids
    issues = tuple(
        _evidence_confirm_issue(issue_id, "blocking" if status == "fail" else "reviewable")
        for issue_id in issue_ids
    )
    fact_result = EvidenceConfirmFactResultV2(
        fact_id="fact-1",
        source_field_id="field-1",
        status=status,
        hard_gate=hard_gate,
        dimension_results=(),
        matched_anchor_ids=("anchor-1",) if status in {"pass", "warn"} else (),
        issue_ids=issue_ids,
        auditability_score=100 if status == "pass" else None,
    )
    return EvidenceConfirmResultV2(
        schema_version=EVIDENCE_CONFIRM_V2_SCHEMA_VERSION,
        fund_code=fund_code,
        report_year=report_year,
        fact_results=(fact_result,),
        issues=issues,
        checked_rules=("E1", "E2", "E3"),
        hard_gate=hard_gate,
        overall_status=status,
        auditability_score=100 if status == "pass" else None,
    )


def _evidence_confirm_issue(issue_id: str, severity: str) -> EvidenceConfirmIssue:
    """构造测试用 Evidence Confirm issue。

    Args:
        issue_id: 稳定 issue id。
        severity: issue 严重程度。

    Returns:
        Evidence Confirm issue。

    Raises:
        无显式抛出。
    """

    return EvidenceConfirmIssue(
        issue_id=issue_id,
        rule_code="E2",
        severity=severity,  # type: ignore[arg-type]
        fact_id="fact-1",
        source_field_id="field-1",
        anchor_id="anchor-1",
        message="fixture evidence confirm issue",
    )


def _source_csv(tmp_path: Path, fund_code: str) -> Path:
    """写入测试用精选基金池 CSV。

    Args:
        tmp_path: pytest 临时目录 fixture。
        fund_code: CSV 中的基金代码。

    Returns:
        CSV 路径。

    Raises:
        OSError: 写入失败时抛出。
    """

    source_csv = tmp_path / f"selected-{fund_code}.csv"
    source_csv.write_text(
        f"基金名称,基金代码,类别\n测试基金,{fund_code},国内股票类\n",
        encoding="utf-8",
    )
    return source_csv


def _low_quality_bundle() -> StructuredFundDataBundle:
    """构造会触发 P0 quality gate block 的低质量数据包。

    Args:
        无。

    Returns:
        P0 费率字段缺值且无锚点的结构化数据包。

    Raises:
        无显式抛出。
    """

    bundle = _bundle()
    return replace(
        bundle,
        fee_schedule=ExtractedField(
            value={},
            anchors=(),
            extraction_mode="missing",
            note="fixture missing fee_schedule",
        ),
    )
