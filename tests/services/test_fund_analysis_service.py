"""基金分析 Service 测试。"""

from __future__ import annotations

from dataclasses import replace
from decimal import Decimal
from pathlib import Path
from time import perf_counter

import pytest

from fund_agent.fund.data.nav_data import NavDataResult
from fund_agent.fund.data_extractor import StructuredFundDataBundle
from fund_agent.fund.extractors.models import EvidenceAnchor, ExtractedField
from fund_agent.services import FundAnalysisRequest, FundAnalysisService, QualityGateBlockedError

_P3_S8_MAX_ANALYSIS_SECONDS = 30.0


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
        fee_schedule=_field({"management_fee": "1.20%", "custody_fee": "0.20%"}, "§2", "fee_schedule"),
        turnover_rate=_field({"turnover_rate": "80.00%"}, "§8", "turnover_rate"),
        nav_benchmark_performance=_field(
            {"nav_growth_rate": "10.00%", "benchmark_return_rate": "5.00%"},
            "§3",
            "nav_benchmark_performance",
        ),
        investor_return=_field({"investor_return_rate": "12.00%", "disclosure_status": "direct"}, "§3", "investor_return"),
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
    service = FundAnalysisService(extractor=extractor)

    result = await service.analyze(
        FundAnalysisRequest(
            fund_code="110011",
            report_year=2024,
            equity_position="80%",
            actual_style="均衡",
            actual_equity_position="70%",
            manager_tenure_months=24,
            peer_fee_median="1.00%",
            investment_amount=Decimal("10000"),
            max_tolerable_loss_rate="50%",
            valuation_state="low",
            user_money_horizon_years=4,
            current_stage="规模稳定，继续观察结构性超额证据",
            final_judgment="worth_holding",
            force_refresh=True,
            quality_gate_policy="off",
        )
    )

    assert extractor.calls == [("110011", 2024, True)]
    assert result.audit_result.passed
    assert result.quality_gate_result is None
    assert result.quality_gate_not_run_reason == "policy=off"
    assert result.rabc_attribution.status == "computed"
    assert result.checklist_result.overall_signal in {"green", "yellow", "gray"}
    assert "# 0. 投资要点概览" in result.report_markdown
    assert "# 7. 是否值得持有——最终判断" in result.report_markdown
    assert "## 证据与出处" in result.report_markdown


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
    request = FundAnalysisRequest(
        fund_code="110011",
        report_year=2024,
        equity_position="80%",
        actual_style="均衡",
        actual_equity_position="70%",
        manager_tenure_months=24,
        peer_fee_median="1.00%",
        investment_amount=Decimal("10000"),
        max_tolerable_loss_rate="50%",
        valuation_state="low",
        user_money_horizon_years=4,
        current_stage="规模稳定，继续观察结构性超额证据",
        final_judgment="worth_holding",
        force_refresh=True,
        quality_gate_policy="off",
    )

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
        await service.analyze(FundAnalysisRequest(fund_code="110011", quality_gate_policy="off"))


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
        FundAnalysisRequest(
            fund_code="004393",
            equity_position="80%",
            actual_style="均衡",
            actual_equity_position="70%",
            manager_tenure_months=24,
            peer_fee_median="1.00%",
            max_tolerable_loss_rate="50%",
            valuation_state="low",
            user_money_horizon_years=4,
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
            FundAnalysisRequest(
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

    with pytest.raises(ValueError, match="质量 gate 未运行"):
        await service.analyze(
            FundAnalysisRequest(
                fund_code="110011",
                equity_position="80%",
                actual_style="均衡",
                actual_equity_position="70%",
                manager_tenure_months=24,
                peer_fee_median="1.00%",
                max_tolerable_loss_rate="50%",
                valuation_state="low",
                user_money_horizon_years=4,
                quality_gate_policy="block",
                quality_gate_source_csv=_source_csv(tmp_path, "004393"),
                quality_gate_run_id="fixture-run",
                quality_gate_golden_answer_path=None,
            )
        )


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
        FundAnalysisRequest(
            fund_code="110011",
            equity_position="80%",
            actual_style="均衡",
            actual_equity_position="70%",
            manager_tenure_months=24,
            peer_fee_median="1.00%",
            max_tolerable_loss_rate="50%",
            valuation_state="low",
            user_money_horizon_years=4,
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
            FundAnalysisRequest(
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
    request = FundAnalysisRequest(
        fund_code="004393",
        equity_position="80%",
        actual_style="均衡",
        actual_equity_position="70%",
        manager_tenure_months=24,
        peer_fee_median="1.00%",
        max_tolerable_loss_rate="50%",
        valuation_state="low",
        user_money_horizon_years=4,
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
