"""基金分析 Service 编排层。

本模块属于 Service 层，负责把 P1 结构化抽取、P2 Capability 分析、
模板渲染和程序审计串成一个用例。它不直接读取年报文件、PDF 或缓存，
所有基金文档访问都通过 `FundDataExtractor` 进入 Capability 边界。
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal, Protocol

from fund_agent.config.paths import DEFAULT_GOLDEN_ANSWER_JSON
from fund_agent.fund.analysis import (
    ChecklistResult,
    ConsistencyCheckResult,
    FinalJudgment,
    FinalJudgmentDecision,
    FinalJudgmentQualityGateStatus,
    InvestorExperienceResult,
    RabcAttribution,
    RiskCheckResult,
    StressTestResult,
    THERMOMETER_REPORT_DISCLAIMER,
    analyze_investor_experience,
    build_explicit_valuation_resolution,
    build_thermometer_valuation_resolution,
    build_unavailable_valuation_resolution,
    calculate_r_abc_from_bundle,
    check_consistency,
    derive_final_judgment,
    judge_alpha_nature,
    resolve_valuation_index_target,
    resolve_tracking_error_for_risk,
    run_checklist,
    run_risk_checks,
    run_stress_test,
    ValuationStateResolution,
)
from fund_agent.fund.analysis.thermometer_calculator import ThermometerCalculationError
from fund_agent.fund.audit import ProgrammaticAuditResult, run_programmatic_audit
from fund_agent.fund.data.thermometer import ThermometerSnapshot
from fund_agent.fund.data.thermometer_types import ThermometerBatchResult, ThermometerReading
from fund_agent.fund.data_extractor import FundDataExtractor, StructuredFundDataBundle
from fund_agent.fund.extraction_snapshot import DEFAULT_SELECTED_FUNDS_CSV
from fund_agent.fund.fund_type import FundType
from fund_agent.fund.quality_gate import GATE_STATUS_BLOCK, QualityGateResult
from fund_agent.fund.quality_gate_integration import check_quality_gate_fund_membership, run_quality_gate_for_bundle
from fund_agent.fund.template import TemplateRenderInput, TemplateRenderResult, render_template_report
from fund_agent.services.thermometer_service import ThermometerRequest, ThermometerService as IndexThermometerService

ValuationState = Literal["low", "fair", "high", "unavailable"]
MoneyHorizon = Literal["long_enough", "uncertain", "too_short"]
QualityGatePolicy = Literal["off", "warn", "block"]
AnalyzeMode = Literal["product", "developer_override"]
DEFAULT_GOLDEN_ANSWER_PATH = DEFAULT_GOLDEN_ANSWER_JSON


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


class _ThermometerService(Protocol):
    """自建温度计 Service 协议。

    该协议用于 P19-S3 自动估值路径测试注入 fake provider。Service 层只调用
    自建指数温度计请求，不使用公开页 `FundThermometerAdapter` 作为分析真源。
    """

    async def run(
        self,
        request: ThermometerRequest,
    ) -> ThermometerSnapshot | ThermometerReading | ThermometerBatchResult:
        """执行温度计查询。

        Args:
            request: 显式温度计请求。

        Returns:
            温度计结果；P19-S3 自动路径只接受 `ThermometerReading`。

        Raises:
            ThermometerCalculationError: 自建温度计计算或数据质量错误。
            Exception: 允许具体实现传播其他契约错误。
        """


@dataclass(frozen=True, slots=True)
class FundAnalysisDeveloperOverrides:
    """开发覆盖参数，只能在 developer override mode 使用。

    Attributes:
        equity_position: R=A+B-C 使用的显式股票仓位，见模板第 2 章。
        actual_style: 言行一致性使用的显式实际持仓风格，见模板第 3 章。
        actual_equity_position: 言行一致性使用的显式实际股票仓位，见模板第 3 章。
        manager_tenure_months: 基金经理管理本基金月数，见模板第 6 章。
        peer_fee_median: 同类总费率中位数，见模板第 6 章。
        tracking_error: 指数基金跟踪误差，见模板第 6 章。
        money_horizon: 用户资金期限分类，见 7 问题检查清单。
        current_stage: 当前阶段与关键变化说明，见模板第 5 章。
        final_judgment_override: 开发覆盖最终判断，见模板第 7 章。
        quality_gate_policy: 报告质量 gate 策略。
        quality_gate_source_csv: 精选基金池 CSV，用于取得 App 类别。
        quality_gate_output_dir: quality gate 显式输出目录。
        quality_gate_run_id: quality gate 运行 ID；为空时 Service 生成唯一 ID。
        quality_gate_golden_answer_path: strict golden answer JSON 路径。
    """

    equity_position: Decimal | str | int | float | None = None
    actual_style: str | None = None
    actual_equity_position: Decimal | str | int | float | None = None
    manager_tenure_months: int | None = None
    peer_fee_median: Decimal | str | int | float | None = None
    tracking_error: Decimal | str | int | float | None = None
    money_horizon: MoneyHorizon | None = None
    current_stage: str | None = None
    final_judgment_override: FinalJudgment | None = None
    quality_gate_policy: QualityGatePolicy | None = None
    quality_gate_source_csv: Path | None = None
    quality_gate_output_dir: Path | None = None
    quality_gate_run_id: str | None = None
    quality_gate_golden_answer_path: Path | None = None


@dataclass(frozen=True, slots=True)
class FundAnalysisRequest:
    """基金分析 Service 请求。

    Attributes:
        fund_code: 基金代码。
        report_year: 年报年份。
        investment_amount: 压力测试投入金额，见模板第 6 章。
        max_tolerable_loss_rate: 最大可承受亏损比例，见模板第 6 章。
        valuation_state: 估值状态，见 7 问题检查清单；`None` 表示允许自动温度计解析。
        thermometer_cache_dir: 自动温度计缓存目录。
        user_money_horizon_years: 用户资金不用年限，见 7 问题检查清单。
        force_refresh: 是否强制刷新底层数据。
        mode: analyze 契约模式，默认 product。
        developer_overrides: 开发覆盖参数；product mode 下必须为空。
    """

    fund_code: str
    report_year: int = 2024
    investment_amount: Decimal | str | int | float = Decimal("10000")
    max_tolerable_loss_rate: Decimal | str | int | float | None = None
    valuation_state: ValuationState | None = None
    thermometer_cache_dir: Path | None = None
    user_money_horizon_years: Decimal | str | int | float | None = None
    force_refresh: bool = False
    mode: AnalyzeMode = "product"
    developer_overrides: FundAnalysisDeveloperOverrides | None = None


@dataclass(frozen=True, slots=True)
class ResolvedAnalyzeContract:
    """Service 内部解析后的 analyze 契约。

    Attributes:
        mode: analyze 契约模式。
        equity_position: R=A+B-C 使用的显式股票仓位，见模板第 2 章。
        actual_style: 言行一致性使用的显式实际持仓风格，见模板第 3 章。
        actual_equity_position: 言行一致性使用的显式实际股票仓位，见模板第 3 章。
        manager_tenure_months: 基金经理管理本基金月数，见模板第 6 章。
        peer_fee_median: 同类总费率中位数，见模板第 6 章。
        tracking_error: 指数基金跟踪误差，见模板第 6 章。
        money_horizon: 用户资金期限分类，见 7 问题检查清单。
        current_stage: 当前阶段与关键变化说明，见模板第 5 章。
        final_judgment_override: 开发覆盖最终判断，见模板第 7 章。
        quality_gate_policy: 报告质量 gate 策略。
        quality_gate_source_csv: 精选基金池 CSV，用于取得 App 类别。
        quality_gate_output_dir: quality gate 显式输出目录。
        quality_gate_run_id: quality gate 运行 ID。
        quality_gate_golden_answer_path: strict golden answer JSON 路径。
    """

    mode: AnalyzeMode
    equity_position: Decimal | str | int | float | None
    actual_style: str | None
    actual_equity_position: Decimal | str | int | float | None
    manager_tenure_months: int | None
    peer_fee_median: Decimal | str | int | float | None
    tracking_error: Decimal | str | int | float | None
    money_horizon: MoneyHorizon | None
    current_stage: str | None
    final_judgment_override: FinalJudgment | None
    quality_gate_policy: QualityGatePolicy
    quality_gate_source_csv: Path | None
    quality_gate_output_dir: Path | None
    quality_gate_run_id: str | None
    quality_gate_golden_answer_path: Path | None


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
        valuation_state_resolution: 估值状态结构化真源。
        final_judgment_decision: 最终判断选择契约。
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
    valuation_state_resolution: ValuationStateResolution
    final_judgment_decision: FinalJudgmentDecision
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

    def __init__(
        self,
        extractor: _FundDataExtractor | None = None,
        thermometer_service: _ThermometerService | None = None,
    ) -> None:
        """初始化基金分析 Service。

        Args:
            extractor: P1 结构化抽取器；未提供时使用默认 `FundDataExtractor`。
            thermometer_service: 自建温度计 Service；未提供时使用默认实现。

        Returns:
            无返回值。

        Raises:
            无显式抛出。
        """

        self._extractor = extractor or FundDataExtractor()
        self._thermometer_service = thermometer_service or IndexThermometerService()

    async def analyze(self, request: FundAnalysisRequest) -> FundAnalysisResult:
        """执行单只基金完整分析并生成 8 章报告。

        Args:
            request: 显式分析参数，不使用 `extra_payload`。

        Returns:
            基金分析 Service 结果，包含 Markdown 报告和程序审计结果。

        Raises:
            ValueError: 当基金代码、年份、基金类型或审计结果非法时抛出。
            QualityGateBlockedError: 当 quality gate 在 block 策略下阻断报告时抛出。
            QualityGateNotRunBlockedError: 当 quality gate 在 block 策略下未运行时抛出。
            Exception: 允许底层抽取器或 Capability 模块传播异常。
        """

        resolved_contract = _resolve_analyze_contract(request)
        _validate_request(request, resolved_contract)
        _check_pool_membership_before_extraction(request, resolved_contract)
        structured_data = await self._extractor.extract(
            request.fund_code,
            request.report_year,
            force_refresh=request.force_refresh,
        )
        quality_gate_result, quality_gate_not_run_reason = _run_quality_gate_if_enabled(
            structured_data=structured_data,
            resolved_contract=resolved_contract,
        )
        if resolved_contract.quality_gate_policy == "block":
            if quality_gate_result is None:
                raise QualityGateNotRunBlockedError(quality_gate_not_run_reason or "unknown")
            if quality_gate_result.status == GATE_STATUS_BLOCK:
                raise QualityGateBlockedError(quality_gate_result)
        quality_gate_status = _resolve_final_judgment_quality_gate_status(
            quality_gate_result=quality_gate_result,
            quality_gate_not_run_reason=quality_gate_not_run_reason,
        )
        fund_type = _extract_fund_type(structured_data)
        rabc_attribution = calculate_r_abc_from_bundle(
            structured_data,
            period=str(structured_data.report_year),
            equity_position=resolved_contract.equity_position,
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
            actual_style=resolved_contract.actual_style,
            actual_equity_position=resolved_contract.actual_equity_position,
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
            manager_tenure_months=resolved_contract.manager_tenure_months,
            peer_fee_median=resolved_contract.peer_fee_median,
            tracking_error=resolve_tracking_error_for_risk(
                tracking_error_field=structured_data.tracking_error,
                developer_override=resolved_contract.tracking_error,
                developer_override_enabled=resolved_contract.mode == "developer_override",
                fund_type=fund_type,
            ),
        )
        stress_test_result = run_stress_test(
            fund_type=fund_type,
            investment_amount=request.investment_amount,
            max_tolerable_loss_rate=request.max_tolerable_loss_rate,
            anchors=structured_data.basic_identity.anchors,
        )
        valuation_state_resolution = await self._resolve_valuation_state(
            request=request,
            structured_data=structured_data,
            fund_type=fund_type,
        )
        checklist_result = run_checklist(
            rabc_attribution=rabc_attribution,
            manager_alignment=structured_data.manager_alignment,
            investor_experience=investor_experience,
            consistency_result=consistency_result,
            risk_check_result=risk_check_result,
            valuation_state=valuation_state_resolution.state,
            valuation_resolution=valuation_state_resolution,
            money_horizon=resolved_contract.money_horizon,
            user_money_horizon_years=request.user_money_horizon_years,
        )
        final_judgment_decision = derive_final_judgment(
            checklist_result=checklist_result,
            risk_check_result=risk_check_result,
            stress_test_result=stress_test_result,
            quality_gate_status=quality_gate_status,
            quality_gate_not_run_reason=quality_gate_not_run_reason,
            override_judgment=resolved_contract.final_judgment_override,
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
                valuation_state_resolution=valuation_state_resolution,
                final_judgment_decision=final_judgment_decision,
                current_stage=resolved_contract.current_stage,
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
            valuation_state_resolution=valuation_state_resolution,
            final_judgment_decision=final_judgment_decision,
            render_result=render_result,
            audit_result=audit_result,
            quality_gate_result=quality_gate_result,
            quality_gate_not_run_reason=quality_gate_not_run_reason,
        )

    async def _resolve_valuation_state(
        self,
        *,
        request: FundAnalysisRequest,
        structured_data: StructuredFundDataBundle,
        fund_type: FundType,
    ) -> ValuationStateResolution:
        """解析检查清单第 6 问估值状态，见模板第 7 章。

        Args:
            request: 基金分析请求。
            structured_data: P1 结构化基金数据。
            fund_type: 已识别基金类型。

        Returns:
            估值状态结构化真源。

        Raises:
            ValueError: 温度计 provider 返回不符合 P19-S3 自动路径契约的结果时抛出。
        """

        if request.valuation_state is not None:
            return build_explicit_valuation_resolution(request.valuation_state)

        target = resolve_valuation_index_target(
            fund_type=fund_type,
            index_profile=structured_data.index_profile,
            benchmark=structured_data.benchmark,
        )
        if target.status != "mapped" or target.index_code is None:
            return build_unavailable_valuation_resolution(target)

        try:
            result = await self._thermometer_service.run(
                ThermometerRequest(
                    cache_dir=request.thermometer_cache_dir,
                    force_refresh=request.force_refresh,
                    index_code=target.index_code,
                )
            )
        except ThermometerCalculationError as exc:
            return ValuationStateResolution(
                state="unavailable",
                source="unavailable_thermometer",
                reason=f"自动估值不可用：自建温度计计算失败：{exc}",
                anchors=target.anchors,
                disclaimer_required=True,
                index_code=target.index_code,
                index_name=target.index_name,
                unavailable_reason=f"自建温度计计算失败：{exc}",
                disclaimer=THERMOMETER_REPORT_DISCLAIMER,
            )
        if not isinstance(result, ThermometerReading):
            raise ValueError("自动估值温度计 provider 必须返回 ThermometerReading")
        return build_thermometer_valuation_resolution(result)


def _resolve_analyze_contract(request: FundAnalysisRequest) -> ResolvedAnalyzeContract:
    """解析 analyze 产品契约和开发覆盖契约。

    Args:
        request: 基金分析请求。

    Returns:
        Service 内部使用的解析后契约。

    Raises:
        ValueError: 当模式非法或 product mode 携带开发覆盖时抛出。
    """

    if request.mode not in {"product", "developer_override"}:
        raise ValueError("mode 必须是 product / developer_override")
    if request.mode == "product":
        if request.developer_overrides is not None:
            raise ValueError("product mode 不允许 developer_overrides")
        return ResolvedAnalyzeContract(
            mode="product",
            equity_position=None,
            actual_style=None,
            actual_equity_position=None,
            manager_tenure_months=None,
            peer_fee_median=None,
            tracking_error=None,
            money_horizon=None,
            current_stage=None,
            final_judgment_override=None,
            quality_gate_policy="block",
            quality_gate_source_csv=DEFAULT_SELECTED_FUNDS_CSV,
            quality_gate_output_dir=None,
            quality_gate_run_id=None,
            quality_gate_golden_answer_path=DEFAULT_GOLDEN_ANSWER_PATH,
        )
    overrides = request.developer_overrides or FundAnalysisDeveloperOverrides()
    return ResolvedAnalyzeContract(
        mode="developer_override",
        equity_position=overrides.equity_position,
        actual_style=overrides.actual_style,
        actual_equity_position=overrides.actual_equity_position,
        manager_tenure_months=overrides.manager_tenure_months,
        peer_fee_median=overrides.peer_fee_median,
        tracking_error=overrides.tracking_error,
        money_horizon=overrides.money_horizon,
        current_stage=overrides.current_stage,
        final_judgment_override=overrides.final_judgment_override,
        quality_gate_policy=overrides.quality_gate_policy or "block",
        quality_gate_source_csv=(
            DEFAULT_SELECTED_FUNDS_CSV
            if overrides.quality_gate_source_csv is None
            else overrides.quality_gate_source_csv
        ),
        quality_gate_output_dir=overrides.quality_gate_output_dir,
        quality_gate_run_id=overrides.quality_gate_run_id,
        quality_gate_golden_answer_path=(
            DEFAULT_GOLDEN_ANSWER_PATH
            if overrides.quality_gate_golden_answer_path is None
            else overrides.quality_gate_golden_answer_path
        ),
    )


def _validate_request(
    request: FundAnalysisRequest,
    resolved_contract: ResolvedAnalyzeContract,
) -> None:
    """校验 Service 请求的基础字段。

    Args:
        request: 基金分析请求。
        resolved_contract: 解析后的 analyze 契约。

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
    if resolved_contract.quality_gate_policy not in {"off", "warn", "block"}:
        raise ValueError("quality_gate_policy 必须是 off / warn / block")
    if (
        resolved_contract.quality_gate_run_id is not None
        and not resolved_contract.quality_gate_run_id.strip()
    ):
        raise ValueError("quality_gate_run_id 不能为空")
    if (
        resolved_contract.quality_gate_output_dir is not None
        and resolved_contract.quality_gate_output_dir.exists()
        and not resolved_contract.quality_gate_output_dir.is_dir()
    ):
        raise ValueError("quality_gate_output_dir 必须是目录")


def _check_pool_membership_before_extraction(
    request: FundAnalysisRequest,
    resolved_contract: ResolvedAnalyzeContract,
) -> None:
    """在抽取前轻量检查基金是否在精选池中。

    仅当 quality gate policy 为 block 时生效。不在池中时提前阻断，
    避免浪费昂贵的年报抽取 I/O。

    Args:
        request: 基金分析请求。
        resolved_contract: 解析后的 analyze 契约。

    Returns:
        无返回值。

    Raises:
        QualityGateNotRunBlockedError: 基金不在精选池中时抛出。
    """

    if resolved_contract.quality_gate_policy != "block":
        return
    if resolved_contract.quality_gate_source_csv is None:
        return
    not_run_reason = check_quality_gate_fund_membership(
        source_csv=resolved_contract.quality_gate_source_csv,
        fund_code=request.fund_code,
    )
    if not_run_reason is not None:
        raise QualityGateNotRunBlockedError(not_run_reason)


def _run_quality_gate_if_enabled(
    *,
    structured_data: StructuredFundDataBundle,
    resolved_contract: ResolvedAnalyzeContract,
) -> tuple[QualityGateResult | None, str | None]:
    """按请求策略运行输入质量 gate。

    Args:
        structured_data: 已抽取的结构化基金数据包，避免重复读取年报。
        resolved_contract: 解析后的 analyze 契约。

    Returns:
        `(quality_gate_result, not_run_reason)`。

    Raises:
        Exception: 允许 Capability quality gate 传播 JSON 或写文件异常。
    """

    if resolved_contract.quality_gate_policy == "off":
        return None, "policy=off"
    if resolved_contract.quality_gate_source_csv is None:
        return None, "quality_gate_source_csv not provided"
    golden_answer_path = _resolve_golden_answer_path(resolved_contract.quality_gate_golden_answer_path)
    integration_result = run_quality_gate_for_bundle(
        bundle=structured_data,
        source_csv=resolved_contract.quality_gate_source_csv,
        output_dir=resolved_contract.quality_gate_output_dir,
        run_id=resolved_contract.quality_gate_run_id or _default_quality_gate_run_id(structured_data),
        golden_answer_path=golden_answer_path,
    )
    return integration_result.quality_gate_result, integration_result.not_run_reason


def _resolve_final_judgment_quality_gate_status(
    *,
    quality_gate_result: QualityGateResult | None,
    quality_gate_not_run_reason: str | None,
) -> FinalJudgmentQualityGateStatus:
    """把 Service quality gate 执行结果归一化为最终判断输入。

    Args:
        quality_gate_result: quality gate 运行结果。
        quality_gate_not_run_reason: quality gate 未运行原因。

    Returns:
        `derive_final_judgment` 可消费的 gate 状态。

    Raises:
        ValueError: 当 gate 状态未知或结果与未运行原因同时存在时抛出。
    """

    if quality_gate_result is not None and quality_gate_not_run_reason is not None:
        raise ValueError("quality_gate_result 与 quality_gate_not_run_reason 不能同时存在")
    if quality_gate_result is None:
        return "not_run"
    if quality_gate_result.status in {"pass", "warn", "block"}:
        return quality_gate_result.status  # type: ignore[return-value]
    raise ValueError("quality_gate_result.status 必须是 pass / warn / block")


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
