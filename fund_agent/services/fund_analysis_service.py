"""基金分析 Service 编排层。

本模块属于 Service 层，负责把 P1 结构化抽取、P2 Capability 分析、
模板渲染和程序审计串成一个用例。它不直接读取年报文件、PDF 或缓存，
所有基金文档访问都通过 `FundDataExtractor` 进入 Capability 边界。
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Literal, Protocol

from fund_agent.fund.analysis import (
    ChecklistResult,
    ConsistencyCheckResult,
    InvestorExperienceResult,
    RabcAttribution,
    RiskCheckResult,
    StressTestResult,
    analyze_investor_experience,
    calculate_r_abc_from_bundle,
    check_consistency,
    judge_alpha_nature,
    run_checklist,
    run_risk_checks,
    run_stress_test,
)
from fund_agent.fund.audit import ProgrammaticAuditResult, run_programmatic_audit
from fund_agent.fund.data_extractor import FundDataExtractor, StructuredFundDataBundle
from fund_agent.fund.fund_type import FundType
from fund_agent.fund.template import TemplateFinalJudgment, TemplateRenderInput, TemplateRenderResult, render_template_report

ValuationState = Literal["low", "fair", "high", "unavailable"]
MoneyHorizon = Literal["long_enough", "uncertain", "too_short"]


class _FundDataExtractor(Protocol):
    """基金结构化抽取器协议。

    该协议让 Service 测试可以注入 fake extractor，同时保持生产路径使用
    `FundDataExtractor`，避免 Service 直接读取基金文档。
    """

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
            force_refresh: 是否强制刷新底层仓库和缓存。

        Returns:
            P1 结构化基金数据包。

        Raises:
            Exception: 允许具体抽取器传播异常。
        """


@dataclass(frozen=True, slots=True)
class FundAnalysisRequest:
    """基金分析 Service 请求。

    Attributes:
        fund_code: 基金代码。
        report_year: 年报年份。
        equity_position: R=A+B-C 使用的显式股票仓位，见模板第 2 章。
        actual_style: 言行一致性使用的显式实际持仓风格，见模板第 3 章。
        actual_equity_position: 言行一致性使用的显式实际股票仓位，见模板第 3 章。
        manager_tenure_months: 基金经理管理本基金月数，见模板第 6 章。
        peer_fee_median: 同类总费率中位数，见模板第 6 章。
        tracking_error: 指数基金跟踪误差，见模板第 6 章。
        investment_amount: 压力测试投入金额，见模板第 6 章。
        max_tolerable_loss_rate: 最大可承受亏损比例，见模板第 6 章。
        valuation_state: 估值状态，见 7 问题检查清单。
        money_horizon: 用户资金期限分类，见 7 问题检查清单。
        user_money_horizon_years: 用户资金不用年限，见 7 问题检查清单。
        current_stage: 当前阶段与关键变化说明，见模板第 5 章。
        final_judgment: 最终持有判断，见模板第 7 章。
        force_refresh: 是否强制刷新底层数据。
    """

    fund_code: str
    report_year: int = 2024
    equity_position: Decimal | str | int | float | None = None
    actual_style: str | None = None
    actual_equity_position: Decimal | str | int | float | None = None
    manager_tenure_months: int | None = None
    peer_fee_median: Decimal | str | int | float | None = None
    tracking_error: Decimal | str | int | float | None = None
    investment_amount: Decimal | str | int | float = Decimal("10000")
    max_tolerable_loss_rate: Decimal | str | int | float | None = None
    valuation_state: ValuationState = "unavailable"
    money_horizon: MoneyHorizon | None = None
    user_money_horizon_years: Decimal | str | int | float | None = None
    current_stage: str | None = None
    final_judgment: TemplateFinalJudgment = "needs_attention"
    force_refresh: bool = False


@dataclass(frozen=True, slots=True)
class FundAnalysisResult:
    """基金分析 Service 结果。

    Attributes:
        structured_data: P1 结构化基金数据包。
        rabc_attribution: R=A+B-C 单期归因结果。
        consistency_result: 言行一致性检查结果。
        investor_experience: 投资者获得感分析结果。
        risk_check_result: 否决项检查结果。
        stress_test_result: 压力测试结果。
        checklist_result: 7 问题检查清单结果。
        render_result: 模板渲染结果。
        audit_result: 程序审计结果。
    """

    structured_data: StructuredFundDataBundle
    rabc_attribution: RabcAttribution
    consistency_result: ConsistencyCheckResult
    investor_experience: InvestorExperienceResult
    risk_check_result: RiskCheckResult
    stress_test_result: StressTestResult
    checklist_result: ChecklistResult
    render_result: TemplateRenderResult
    audit_result: ProgrammaticAuditResult

    @property
    def report_markdown(self) -> str:
        """返回完整 8 章 Markdown 报告。

        Args:
            无。

        Returns:
            完整 Markdown 报告文本。

        Raises:
            无显式抛出。
        """

        return self.render_result.report_markdown


class FundAnalysisService:
    """基金分析用例编排 Service。

    Service 只负责按当前 MVP 流程协调 Capability 模块，不承载基金领域规则。
    领域判断、审计和模板规则均保留在 `fund_agent.fund`。
    """

    def __init__(self, extractor: _FundDataExtractor | None = None) -> None:
        """初始化基金分析 Service。

        Args:
            extractor: P1 结构化抽取器；未提供时使用默认 `FundDataExtractor`。

        Returns:
            无返回值。

        Raises:
            无显式抛出。
        """

        self._extractor = extractor or FundDataExtractor()

    async def analyze(self, request: FundAnalysisRequest) -> FundAnalysisResult:
        """执行单只基金完整分析并生成 8 章报告。

        Args:
            request: 显式分析参数，不使用 `extra_payload`。

        Returns:
            基金分析 Service 结果，包含 Markdown 报告和程序审计结果。

        Raises:
            ValueError: 当基金代码、年份、基金类型或审计结果非法时抛出。
            Exception: 允许底层抽取器或 Capability 模块传播异常。
        """

        _validate_request(request)
        structured_data = await self._extractor.extract(
            request.fund_code,
            request.report_year,
            force_refresh=request.force_refresh,
        )
        fund_type = _extract_fund_type(structured_data)
        rabc_attribution = calculate_r_abc_from_bundle(
            structured_data,
            period=str(structured_data.report_year),
            equity_position=request.equity_position,
        )
        alpha_judgment = judge_alpha_nature((), fund_type=fund_type)
        consistency_result = check_consistency(
            manager_strategy_text=structured_data.manager_strategy_text,
            holdings_snapshot=structured_data.holdings_snapshot,
            turnover_rate=structured_data.turnover_rate,
            actual_style=request.actual_style,
            actual_equity_position=request.actual_equity_position,
        )
        investor_experience = analyze_investor_experience(
            nav_benchmark_performance=structured_data.nav_benchmark_performance,
            investor_return=structured_data.investor_return,
            share_change=structured_data.share_change,
        )
        risk_check_result = run_risk_checks(
            basic_identity=structured_data.basic_identity,
            fee_schedule=structured_data.fee_schedule,
            consistency_result=consistency_result,
            fund_type=fund_type,
            manager_tenure_months=request.manager_tenure_months,
            peer_fee_median=request.peer_fee_median,
            tracking_error=request.tracking_error,
        )
        stress_test_result = run_stress_test(
            fund_type=fund_type,
            investment_amount=request.investment_amount,
            max_tolerable_loss_rate=request.max_tolerable_loss_rate,
            anchors=structured_data.basic_identity.anchors,
        )
        checklist_result = run_checklist(
            rabc_attribution=rabc_attribution,
            manager_alignment=structured_data.manager_alignment,
            investor_experience=investor_experience,
            consistency_result=consistency_result,
            risk_check_result=risk_check_result,
            valuation_state=request.valuation_state,
            money_horizon=request.money_horizon,
            user_money_horizon_years=request.user_money_horizon_years,
        )
        render_result = render_template_report(
            TemplateRenderInput(
                structured_data=structured_data,
                rabc_attributions=(rabc_attribution,),
                alpha_judgment=alpha_judgment,
                consistency_result=consistency_result,
                investor_experience=investor_experience,
                risk_check_result=risk_check_result,
                stress_test_result=stress_test_result,
                checklist_result=checklist_result,
                final_judgment=request.final_judgment,
                current_stage=request.current_stage,
            )
        )
        audit_result = run_programmatic_audit(render_result.audit_input)
        if not audit_result.passed:
            issue_text = "；".join(issue.message for issue in audit_result.issues)
            raise ValueError(f"程序审计未通过：{issue_text}")
        return FundAnalysisResult(
            structured_data=structured_data,
            rabc_attribution=rabc_attribution,
            consistency_result=consistency_result,
            investor_experience=investor_experience,
            risk_check_result=risk_check_result,
            stress_test_result=stress_test_result,
            checklist_result=checklist_result,
            render_result=render_result,
            audit_result=audit_result,
        )


def _validate_request(request: FundAnalysisRequest) -> None:
    """校验 Service 请求的基础字段。

    Args:
        request: 基金分析请求。

    Returns:
        无返回值。

    Raises:
        ValueError: 当基金代码或年报年份非法时抛出。
    """

    if not request.fund_code.strip():
        raise ValueError("fund_code 不能为空")
    if request.report_year <= 0:
        raise ValueError("report_year 必须为正整数")


def _extract_fund_type(structured_data: StructuredFundDataBundle) -> FundType:
    """从 P1 结构化数据读取已识别基金类型。

    Args:
        structured_data: P1 结构化基金数据包。

    Returns:
        标准化基金类型。

    Raises:
        ValueError: 当 P1 未提供有效 `classified_fund_type` 时抛出。
    """

    identity = structured_data.basic_identity.value or {}
    fund_type = identity.get("classified_fund_type")
    if fund_type in {
        "index_fund",
        "active_fund",
        "bond_fund",
        "enhanced_index",
        "qdii_fund",
        "fof_fund",
    }:
        return fund_type  # type: ignore[return-value]
    raise ValueError("P1 结构化数据缺少有效 classified_fund_type，不能选择 preferred_lens")
