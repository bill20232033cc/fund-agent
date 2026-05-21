"""基金分析 Service 编排层。

本模块属于 Service 层，负责把 P1 结构化抽取、P2 Capability 分析、
模板渲染和程序审计串成一个用例。它不直接读取年报文件、PDF 或缓存，
所有基金文档访问都通过 `FundDataExtractor` 进入 Capability 边界。
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path
from datetime import datetime, timezone
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
from fund_agent.fund.extraction_snapshot import DEFAULT_SELECTED_FUNDS_CSV
from fund_agent.fund.fund_type import FundType
from fund_agent.fund.quality_gate import GATE_STATUS_BLOCK, QualityGateResult
from fund_agent.fund.quality_gate_integration import check_quality_gate_fund_membership, run_quality_gate_for_bundle
from fund_agent.fund.template import TemplateFinalJudgment, TemplateRenderInput, TemplateRenderResult, render_template_report

ValuationState = Literal["low", "fair", "high", "unavailable"]
MoneyHorizon = Literal["long_enough", "uncertain", "too_short"]
FinalJudgment = TemplateFinalJudgment
QualityGatePolicy = Literal["off", "warn", "block"]
DEFAULT_GOLDEN_ANSWER_PATH = Path("reports/golden-answers/golden-answer.json")


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
        quality_gate_policy: 报告质量 gate 策略。
        quality_gate_source_csv: 精选基金池 CSV，用于取得 App 类别。
        quality_gate_output_dir: quality gate 显式输出目录。
        quality_gate_run_id: quality gate 运行 ID；为空时 Service 生成唯一 ID。
        quality_gate_golden_answer_path: strict golden answer JSON 路径。
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
    quality_gate_policy: QualityGatePolicy = "block"
    quality_gate_source_csv: Path | None = DEFAULT_SELECTED_FUNDS_CSV
    quality_gate_output_dir: Path | None = None
    quality_gate_run_id: str | None = None
    quality_gate_golden_answer_path: Path | None = DEFAULT_GOLDEN_ANSWER_PATH


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
        quality_gate_result: quality gate 结果；未运行时为空。
        quality_gate_not_run_reason: quality gate 未运行原因。
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
    quality_gate_result: QualityGateResult | None = None
    quality_gate_not_run_reason: str | None = None

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


class QualityGateBlockedError(ValueError):
    """quality gate 阻断报告输出的结构化异常。

    Attributes:
        quality_gate_result: 阻断报告的 quality gate 结果。
        policy: 触发阻断的策略，固定为 `block`。
    """

    def __init__(self, quality_gate_result: QualityGateResult) -> None:
        """初始化 quality gate 阻断异常。

        Args:
            quality_gate_result: 阻断报告的 quality gate 结果。

        Returns:
            无返回值。

        Raises:
            无显式抛出。
        """

        self.quality_gate_result = quality_gate_result
        self.policy: QualityGatePolicy = "block"
        super().__init__(
            f"质量 gate 阻断报告输出：status={quality_gate_result.status}, "
            f"issues={len(quality_gate_result.issues)}"
        )


class QualityGateNotRunBlockedError(ValueError):
    """quality gate 在 block 策略下未运行的结构化异常。

    Attributes:
        reason: quality gate 未运行原因。
        policy: 触发阻断的策略，固定为 `block`。
    """

    def __init__(self, reason: str) -> None:
        """初始化未运行阻断异常。

        Args:
            reason: quality gate 未运行原因。

        Returns:
            无返回值。

        Raises:
            无显式抛出。
        """

        self.reason = reason
        self.policy: QualityGatePolicy = "block"
        super().__init__(f"质量 gate 未运行：{reason}")


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
            QualityGateBlockedError: 当 quality gate 在 block 策略下阻断报告时抛出。
            Exception: 允许底层抽取器或 Capability 模块传播异常。
        """

        _validate_request(request)
        _check_pool_membership_before_extraction(request)
        structured_data = await self._extractor.extract(
            request.fund_code,
            request.report_year,
            force_refresh=request.force_refresh,
        )
        quality_gate_result, quality_gate_not_run_reason = _run_quality_gate_if_enabled(
            structured_data=structured_data,
            request=request,
        )
        if request.quality_gate_policy == "block":
            if quality_gate_result is None:
                raise QualityGateNotRunBlockedError(quality_gate_not_run_reason or "unknown")
            if quality_gate_result.status == GATE_STATUS_BLOCK:
                raise QualityGateBlockedError(quality_gate_result)
        fund_type = _extract_fund_type(structured_data)
        rabc_attribution = calculate_r_abc_from_bundle(
            structured_data,
            period=str(structured_data.report_year),
            equity_position=request.equity_position,
        )
        # MVP 限制：judge_alpha_nature 需要 observations_from_attributions，
        # 但该函数要求 market_environments 和 source_confidences，
        # 当前 Service 层无法提供这些外部输入，故传空元组，
        # alpha judgment 将返回 insufficient_data。
        alpha_judgment = judge_alpha_nature((), fund_type=fund_type)
        consistency_result = check_consistency(
            product_profile=structured_data.product_profile,
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
            quality_gate_result=quality_gate_result,
            quality_gate_not_run_reason=quality_gate_not_run_reason,
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

    normalized_fund_code = request.fund_code.strip()
    if not normalized_fund_code:
        raise ValueError("fund_code 不能为空")
    if len(normalized_fund_code) != 6 or not normalized_fund_code.isdigit():
        raise ValueError("fund_code 必须是 6 位数字")
    if request.report_year <= 0:
        raise ValueError("report_year 必须为正整数")
    if request.quality_gate_policy not in {"off", "warn", "block"}:
        raise ValueError("quality_gate_policy 必须是 off / warn / block")
    if request.quality_gate_run_id is not None and not request.quality_gate_run_id.strip():
        raise ValueError("quality_gate_run_id 不能为空")
    if (
        request.quality_gate_output_dir is not None
        and request.quality_gate_output_dir.exists()
        and not request.quality_gate_output_dir.is_dir()
    ):
        raise ValueError("quality_gate_output_dir 必须是目录")


def _check_pool_membership_before_extraction(request: FundAnalysisRequest) -> None:
    """在抽取前轻量检查基金是否在精选池中。

    仅当 quality gate policy 为 block 时生效。不在池中时提前阻断，
    避免浪费昂贵的年报抽取 I/O。

    Args:
        request: 基金分析请求。

    Returns:
        无返回值。

    Raises:
        QualityGateNotRunBlockedError: 基金不在精选池中时抛出。
    """

    if request.quality_gate_policy != "block":
        return
    if request.quality_gate_source_csv is None:
        return
    not_run_reason = check_quality_gate_fund_membership(
        source_csv=request.quality_gate_source_csv,
        fund_code=request.fund_code,
    )
    if not_run_reason is not None:
        raise QualityGateNotRunBlockedError(not_run_reason)


def _run_quality_gate_if_enabled(
    *,
    structured_data: StructuredFundDataBundle,
    request: FundAnalysisRequest,
) -> tuple[QualityGateResult | None, str | None]:
    """按请求策略运行输入质量 gate。

    Args:
        structured_data: 已抽取的结构化基金数据包，避免重复读取年报。
        request: 基金分析请求。

    Returns:
        `(quality_gate_result, not_run_reason)`。

    Raises:
        Exception: 允许 Capability quality gate 传播 JSON 或写文件异常。
    """

    if request.quality_gate_policy == "off":
        return None, "policy=off"
    if request.quality_gate_source_csv is None:
        return None, "quality_gate_source_csv not provided"
    golden_answer_path = _resolve_golden_answer_path(request.quality_gate_golden_answer_path)
    integration_result = run_quality_gate_for_bundle(
        bundle=structured_data,
        source_csv=request.quality_gate_source_csv,
        output_dir=request.quality_gate_output_dir,
        run_id=request.quality_gate_run_id or _default_quality_gate_run_id(structured_data),
        golden_answer_path=golden_answer_path,
    )
    return integration_result.quality_gate_result, integration_result.not_run_reason


def _resolve_golden_answer_path(path: Path | None) -> Path | None:
    """解析 strict golden answer 路径。

    Args:
        path: 请求中的 golden answer 路径。

    Returns:
        文件存在时返回路径，否则返回 `None`，让 correctness 显式 unavailable。

    Raises:
        无显式抛出。
    """

    if path is None:
        return None
    if path.exists():
        return path
    if path != DEFAULT_GOLDEN_ANSWER_PATH:
        raise FileNotFoundError(f"quality_gate_golden_answer_path 不存在：{path}")
    return None


def _default_quality_gate_run_id(structured_data: StructuredFundDataBundle) -> str:
    """生成默认 quality gate 运行 ID。

    Args:
        structured_data: 已抽取的结构化基金数据包。

    Returns:
        包含基金代码、年报年份和 UTC 时间戳的运行 ID。

    Raises:
        无显式抛出。
    """

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    return f"analyze-{structured_data.fund_code}-{structured_data.report_year}-{timestamp}"


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
