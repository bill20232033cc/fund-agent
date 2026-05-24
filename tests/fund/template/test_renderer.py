"""基金模板渲染器测试。"""

from __future__ import annotations

from dataclasses import replace
from decimal import Decimal
from pathlib import Path

import pytest

from fund_agent.fund.analysis import (
    AlphaJudgment,
    BehaviorGapResult,
    ChecklistItem,
    ChecklistResult,
    ConsistencyCheckResult,
    ConsistencyDimensionResult,
    FinalJudgmentDecision,
    FundFlowResult,
    InvestorExperienceResult,
    RabcAttribution,
    RiskCheckItem,
    RiskCheckResult,
    StressScenarioResult,
    StressTestResult,
    ValuationStateResolution,
)
from fund_agent.fund.audit import run_programmatic_audit
from fund_agent.fund.data.nav_data import NavDataResult
from fund_agent.fund.data_extractor import StructuredFundDataBundle
from fund_agent.fund.extractors.models import (
    EvidenceAnchor,
    ExtractedField,
    IndexProfileValue,
    TrackingErrorValue,
)
from fund_agent.fund.fund_type import FundType
from fund_agent.fund.template import (
    TemplateRenderInput,
    build_programmatic_audit_input,
    get_chapter_contract,
    get_template_chapter_heading,
    render_template_report,
    split_rendered_chapter_blocks,
)
from fund_agent.fund.template.renderer import (
    _validate_report_wording,
    _body_anchor_reference,
    _item_rule_evidence_bullet,
)

_REPO_ROOT = Path(__file__).resolve().parents[3]
_ITEM_RULE_MARKERS = (
    "#### 指数编制规则与成分股",
    "#### 基金经理投资哲学",
    "#### 超额收益分年度拆解",
    "#### 跟踪误差分析",
)
_ITEM_RULE_EMPTY_EVIDENCE_BOUNDARY = "- 证据边界：数据不足，当前段落未携带独立证据锚点。"


def _anchor(
    section_id: str,
    row_locator: str | None,
    *,
    table_id: str | None = None,
    page_number: int | None = None,
    source_kind: str = "annual_report",
    document_year: int | None = 2024,
) -> EvidenceAnchor:
    """构造测试证据锚点。

    Args:
        section_id: 年报章节编号。
        row_locator: 行定位说明。
        table_id: 表格编号。
        page_number: 页码。
        source_kind: 证据来源类型。
        document_year: 文档年份。

    Returns:
        证据锚点。

    Raises:
        无显式抛出。
    """

    return EvidenceAnchor(
        source_kind=source_kind,  # type: ignore[arg-type]
        document_year=document_year,
        section_id=section_id,
        page_number=page_number,
        table_id=table_id,
        row_locator=row_locator,
        note=f"{row_locator or section_id}: fixture",
    )


def _field(
    value: dict[str, object] | None,
    section_id: str,
    row_locator: str | None,
) -> ExtractedField[dict[str, object]]:
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
        anchors=() if value is None else (_anchor(section_id, row_locator),),
        extraction_mode="missing" if value is None else "direct",
        note=None,
    )


def _tracking_error_field(value_text: str = "1.23%") -> ExtractedField[TrackingErrorValue]:
    """构造直接披露跟踪误差字段。

    Args:
        value_text: 跟踪误差百分比文本。

    Returns:
        跟踪误差抽取字段。

    Raises:
        无显式抛出。
    """

    value = Decimal(value_text.replace("%", "")) / Decimal("100")
    return ExtractedField(
        value=TrackingErrorValue(
            value=value,
            value_text=value_text,
            unit="ratio",
            period_label="报告期",
            period_start=None,
            period_end=None,
            annualized=True,
            source_type="direct_disclosure",
            calculation_method="disclosed",
            benchmark_identity_status="identified",
            benchmark_index_name="沪深300指数",
            benchmark_index_code=None,
            fund_series_source=None,
            index_series_source=None,
            observation_count=None,
            frequency="annual_report_period",
            annualization_factor=None,
            input_period_complete=True,
            provenance_note="fixture direct disclosure",
        ),
        anchors=(_anchor("§3", "tracking_error"),),
        extraction_mode="direct",
        note=None,
    )


def _bundle(
    *,
    missing: bool = False,
    anchor_without_row: bool = False,
    fund_type: str = "active_fund",
    tracking_error: ExtractedField[TrackingErrorValue] | None = None,
) -> StructuredFundDataBundle:
    """构造 P1 结构化数据包。

    Args:
        missing: 是否构造关键字段缺失路径。
        anchor_without_row: 是否让部分证据缺少行定位。
        fund_type: classified_fund_type fixture 值。
        tracking_error: 显式跟踪误差字段。

    Returns:
        P1 结构化数据包。

    Raises:
        无显式抛出。
    """

    row_locator = None if anchor_without_row else "basic_identity"
    basic_identity = _field(
        None
        if missing
        else {
            "fund_name": "测试成长基金",
            "fund_code": "110011",
            "fund_category": "混合型",
            "fund_scale": "10.00亿元",
            "fund_manager": "张三",
            "inception_date": "2020-01-15",
            "classified_fund_type": fund_type,
            "classification_basis": ("基金类别：混合型",),
        },
        "§1",
        row_locator,
    )
    product_profile = _field(
        None
        if missing
        else {
            "investment_objective": "追求长期资本增值",
            "style_positioning": "价值成长均衡",
            "investment_scope": "主要投资股票和债券",
            "investment_strategy": "均衡配置",
        },
        "§2",
        "product_profile",
    )
    benchmark = _field({"benchmark_text": "沪深300指数收益率*80%+中债指数收益率*20%"}, "§2", "benchmark")
    index_profile: ExtractedField[IndexProfileValue]
    if fund_type in {"index_fund", "enhanced_index"}:
        index_profile = ExtractedField(
            value=IndexProfileValue(
                benchmark_text="沪深300指数收益率*80%+中债指数收益率*20%",
                benchmark_identity_status="composite",
                benchmark_index_name=None,
                benchmark_index_code=None,
                benchmark_component_text=("沪深300指数收益率*80%", "中债指数收益率*20%"),
                methodology_availability="benchmark_only",
                methodology_summary=None,
                methodology_source_title=None,
                constituents_availability="benchmark_only",
                constituents_summary=None,
                constituents_as_of_date=None,
                source_tier="benchmark_context",
                missing_reasons=("fixture",),
            ),
            anchors=benchmark.anchors,
            extraction_mode="direct",
            note="fixture",
        )
    else:
        index_profile = ExtractedField(
            value=None,
            anchors=(),
            extraction_mode="missing",
            note="非指数基金不适用指数画像",
        )
    fee_schedule = _field({"management_fee": "1.20%", "custody_fee": "0.20%"}, "§2", "fee_schedule")
    turnover_rate = _field({"turnover_rate": "100.00%"}, "§8", "turnover_rate")
    nav_performance = _field(
        {"nav_growth_rate": "10.00%", "benchmark_return_rate": "5.00%"},
        "§3",
        "nav_benchmark_performance",
    )
    investor_return = _field(
        None if missing else {"investor_return_rate": "12.00%", "disclosure_status": "direct"},
        "§3",
        "investor_return",
    )
    share_change = _field(
        {"beginning_share": "100", "ending_share": "110", "net_change": "10"},
        "§10",
        "share_change",
    )
    manager_alignment = _field({"manager_holding": "基金经理持有本基金"}, "§9", "manager_alignment")
    manager_strategy = _field(
        {"strategy_summary": "坚持价值与成长均衡配置"},
        "§4",
        "manager_strategy_text",
    )
    holdings = _field(
        {"top_holdings": [{"股票名称": "测试股份"}], "industry_distribution": [{"行业": "消费", "占比": "40%"}]},
        "§8",
        "holdings_snapshot",
    )
    holder_structure = _field({"institutional_holder_ratio": "30%", "individual_holder_ratio": "70%"}, "§9", "holder_structure")
    tracking_error_field = tracking_error or ExtractedField(
        value=None,
        anchors=(),
        extraction_mode="missing",
        note="fixture tracking error missing",
    )
    return StructuredFundDataBundle(
        fund_code="110011",
        report_year=2024,
        basic_identity=basic_identity,
        product_profile=product_profile,
        benchmark=benchmark,
        index_profile=index_profile,
        fee_schedule=fee_schedule,
        turnover_rate=turnover_rate,
        nav_benchmark_performance=nav_performance,
        investor_return=investor_return,
        tracking_error=tracking_error_field,
        share_change=share_change,
        manager_alignment=manager_alignment,
        manager_strategy_text=manager_strategy,
        holdings_snapshot=holdings,
        holder_structure=holder_structure,
        nav_data=NavDataResult(fund_code="110011", records=[{"date": "2024-12-31", "nav": 1.2}], source="fixture", cached=True),
    )


def _rabc(*, missing: bool = False) -> RabcAttribution:
    """构造 R=A+B-C 归因结果。

    Args:
        missing: 是否构造缺失状态。

    Returns:
        R=A+B-C 归因结果。

    Raises:
        无显式抛出。
    """

    if missing:
        return RabcAttribution(
            period="2024",
            status="missing",
            total_return_r=None,
            beta_return_b=None,
            alpha_return_a=None,
            explicit_cost_c=None,
            net_excess_return=None,
            turnover_cost=None,
            anchors=(_anchor("§3", "nav_benchmark_performance"),),
            note="缺少显式股票仓位",
        )
    return RabcAttribution(
        period="2024",
        status="computed",
        total_return_r=Decimal("0.10"),
        beta_return_b=Decimal("0.04"),
        alpha_return_a=Decimal("0.06"),
        explicit_cost_c=Decimal("0.02"),
        net_excess_return=Decimal("0.04"),
        turnover_cost=Decimal("0.003"),
        anchors=(_anchor("§3", "nav_benchmark_performance"), _anchor("§2", "fee_schedule")),
        note="fixture",
    )


def _alpha_judgment() -> AlphaJudgment:
    """构造超额收益性质判断。

    Args:
        无。

    Returns:
        超额收益性质判断。

    Raises:
        无显式抛出。
    """

    return AlphaJudgment(
        nature="structural",
        positive_alpha_count=4,
        observation_count=5,
        positive_market_environments=("bull", "bear", "range_bound"),
        explained_source_count=3,
        observations=(),
        reasons=("多年度正 Alpha 且覆盖牛熊环境。",),
        risks=(),
    )


def _consistency() -> ConsistencyCheckResult:
    """构造言行一致性结果。

    Args:
        无。

    Returns:
        言行一致性结果。

    Raises:
        无显式抛出。
    """

    dimensions = (
        ConsistencyDimensionResult(
            dimension="investment_style",
            status="aligned",
            signal="green",
            declared="value",
            actual="value",
            anchors=(_anchor("§2", "style_positioning"),),
            reason="风格一致。",
        ),
        ConsistencyDimensionResult(
            dimension="industry_preference",
            status="aligned",
            signal="green",
            declared="消费",
            actual="消费",
            anchors=(_anchor("§8", "industry_distribution", table_id="T1"),),
            reason="行业偏好一致。",
        ),
    )
    return ConsistencyCheckResult(
        dimensions=dimensions,
        overall_status="aligned",
        overall_signal="green",
        reasons=("言行一致性整体为绿灯。",),
    )


def _investor_experience(*, missing: bool = False) -> InvestorExperienceResult:
    """构造投资者获得感结果。

    Args:
        missing: 是否构造缺失状态。

    Returns:
        投资者获得感结果。

    Raises:
        无显式抛出。
    """

    behavior_gap = BehaviorGapResult(
        status="missing" if missing else "computed",
        product_return=None if missing else Decimal("0.10"),
        investor_return=None if missing else Decimal("0.12"),
        behavior_gap=None if missing else Decimal("0.02"),
        anchors=() if missing else (_anchor("§3", "investor_return"),),
        note="缺少 §3 投资者实际收益率" if missing else None,
    )
    fund_flow = FundFlowResult(
        signal="normal",
        beginning_share=Decimal("100"),
        ending_share=Decimal("110"),
        net_change=Decimal("10"),
        net_change_ratio=Decimal("0.1"),
        anchors=(_anchor("§10", "share_change"),),
        reason="份额变化正常。",
    )
    return InvestorExperienceResult(
        status="insufficient_data" if missing else "positive",
        behavior_gap=behavior_gap,
        fund_flow=fund_flow,
        reasons=("缺少投资者收益率。" if missing else "投资者收益高于产品收益。",),
    )


def _risk_check() -> RiskCheckResult:
    """构造否决项检查结果。

    Args:
        无。

    Returns:
        否决项检查结果。

    Raises:
        无显式抛出。
    """

    item = RiskCheckItem(
        code="liquidation_risk",
        status="pass",
        current_value="1000000000",
        threshold=">50000000 元",
        anchors=(_anchor("§1", "fund_scale"),),
        reason="基金规模高于清盘风险阈值。",
    )
    return RiskCheckResult(
        overall_status="pass",
        items=(item,),
        veto_items=(),
        watch_items=(),
        next_minimum_verification="继续复核披露口径。",
    )


def _risk_item(
    code: str,
    status: str,
    *,
    current_value: str | None,
    threshold: str,
    reason: str,
) -> RiskCheckItem:
    """构造单个风险检查项。

    Args:
        code: 风险检查编码。
        status: 风险检查状态。
        current_value: 当前风险值。
        threshold: 风险阈值。
        reason: 判断原因。

    Returns:
        风险检查项。

    Raises:
        无显式抛出。
    """

    return RiskCheckItem(
        code=code,  # type: ignore[arg-type]
        status=status,  # type: ignore[arg-type]
        current_value=current_value,
        threshold=threshold,
        anchors=(_anchor("§6", code),),
        reason=reason,
    )


def _risk_check_with_item(
    item: RiskCheckItem,
    *,
    overall_status: str,
) -> RiskCheckResult:
    """构造带单个动作项的风险检查汇总。

    Args:
        item: 风险检查项。
        overall_status: 汇总状态。

    Returns:
        风险检查汇总结果。

    Raises:
        无显式抛出。
    """

    return RiskCheckResult(
        overall_status=overall_status,  # type: ignore[arg-type]
        items=(item,),
        veto_items=(item,) if item.status == "veto" else (),
        watch_items=(item,) if item.status in {"watch", "insufficient_data"} else (),
        next_minimum_verification="复核风险动作项。",
    )


def _stress_test(*, fund_type: str = "active_fund") -> StressTestResult:
    """构造压力测试结果。

    Args:
        fund_type: 压力测试使用的标准基金类型。

    Returns:
        压力测试结果。

    Raises:
        无显式抛出。
    """

    scenarios = (
        StressScenarioResult(
            code="minus_20",
            decline_rate=Decimal("-0.20"),
            investment_amount=Decimal("10000"),
            account_balance=Decimal("8000"),
            floating_loss_amount=Decimal("2000"),
            severity="normal",
            capacity_status="within_tolerance",
            threshold="fixture",
            reason="fixture",
        ),
        StressScenarioResult(
            code="minus_40",
            decline_rate=Decimal("-0.40"),
            investment_amount=Decimal("10000"),
            account_balance=Decimal("6000"),
            floating_loss_amount=Decimal("4000"),
            severity="extreme",
            capacity_status="near_limit",
            threshold="fixture",
            reason="fixture",
        ),
        StressScenarioResult(
            code="minus_60",
            decline_rate=Decimal("-0.60"),
            investment_amount=Decimal("10000"),
            account_balance=Decimal("4000"),
            floating_loss_amount=Decimal("6000"),
            severity="historical_worst",
            capacity_status="beyond_tolerance",
            threshold="fixture",
            reason="fixture",
        ),
    )
    return StressTestResult(
        fund_type=fund_type,  # type: ignore[arg-type]
        investment_amount=Decimal("10000"),
        max_tolerable_loss_rate=Decimal("0.50"),
        scenarios=scenarios,
        worst_scenario=scenarios[-1],
        anchors=(_anchor("§1", "fund_type"),),
        next_minimum_verification="复核最大可承受亏损。",
    )


def _stress_test_all_within_tolerance(*, fund_type: str = "active_fund") -> StressTestResult:
    """构造全场景均未越过承受边界的压力测试结果。

    Args:
        fund_type: 压力测试使用的标准基金类型。

    Returns:
        压力测试结果。

    Raises:
        无显式抛出。
    """

    scenarios = (
        StressScenarioResult(
            code="minus_20",
            decline_rate=Decimal("-0.20"),
            investment_amount=Decimal("10000"),
            account_balance=Decimal("8000"),
            floating_loss_amount=Decimal("2000"),
            severity="normal",
            capacity_status="within_tolerance",
            threshold="fixture",
            reason="fixture",
        ),
        StressScenarioResult(
            code="minus_40",
            decline_rate=Decimal("-0.40"),
            investment_amount=Decimal("10000"),
            account_balance=Decimal("6000"),
            floating_loss_amount=Decimal("4000"),
            severity="extreme",
            capacity_status="within_tolerance",
            threshold="fixture",
            reason="fixture",
        ),
        StressScenarioResult(
            code="minus_60",
            decline_rate=Decimal("-0.60"),
            investment_amount=Decimal("10000"),
            account_balance=Decimal("4000"),
            floating_loss_amount=Decimal("6000"),
            severity="historical_worst",
            capacity_status="within_tolerance",
            threshold="fixture",
            reason="fixture",
        ),
    )
    return StressTestResult(
        fund_type=fund_type,  # type: ignore[arg-type]
        investment_amount=Decimal("10000"),
        max_tolerable_loss_rate=Decimal("0.80"),
        scenarios=scenarios,
        worst_scenario=scenarios[-1],
        anchors=(_anchor("§1", "fund_type"),),
        next_minimum_verification="复核最大可承受亏损。",
    )


def _checklist(signal: str = "green") -> ChecklistResult:
    """构造检查清单结果。

    Args:
        signal: 汇总和单题信号。

    Returns:
        检查清单结果。

    Raises:
        无显式抛出。
    """

    status_by_signal = {
        "green": "pass",
        "yellow": "watch",
        "red": "block",
        "gray": "insufficient_data",
    }
    items = tuple(
        ChecklistItem(
            code=code,  # type: ignore[arg-type]
            question=question,
            signal=signal,  # type: ignore[arg-type]
            status=status_by_signal[signal],  # type: ignore[arg-type]
            anchors=(_anchor("§3", code),),
            reason="fixture",
        )
        for code, question in (
            ("net_excess_covers_cost", "超额收益能覆盖成本吗？"),
            ("manager_alignment", "基金经理跟我一条心吗？"),
            ("investor_return", "投资者真的赚到钱了吗？"),
            ("consistency", "说的和做的一样吗？"),
            ("survival", "这只基金不死吗？"),
            ("valuation", "当前估值处于什么位置？"),
            ("money_horizon", "这笔钱 3-4 年内不会用吗？"),
        )
    )
    return ChecklistResult(
        items=items,
        overall_signal=signal,  # type: ignore[arg-type]
        overall_status=status_by_signal[signal],  # type: ignore[arg-type]
        red_items=items if signal == "red" else (),
        yellow_items=items if signal == "yellow" else (),
        gray_items=items if signal == "gray" else (),
        next_minimum_verification="fixture",
    )


def _thermometer_valuation_resolution() -> ValuationStateResolution:
    """构造温度计估值状态真源。

    Args:
        无。

    Returns:
        温度计来源估值状态。

    Raises:
        无显式抛出。
    """

    anchor = EvidenceAnchor(
        source_kind="external_api",
        document_year=None,
        section_id="thermometer",
        page_number=None,
        table_id="fixture_source",
        row_locator="000300:2024-12-31",
        note="fixture thermometer",
    )
    return ValuationStateResolution(
        state="low",
        source="self_owned_thermometer",
        reason="自建温度计 fixture 低估。",
        anchors=(anchor,),
        disclaimer_required=True,
        index_code="000300",
        index_name="沪深300",
        temperature=Decimal("20.00"),
        pe_percentile=Decimal("10.00"),
        pb_percentile=Decimal("30.00"),
        data_date="2024-12-31",
        lookback_start="2014-12-31",
        lookback_end="2024-12-31",
        thermometer_source="fixture_source",
        cached=False,
        stale=False,
        disclaimer=(
            "本温度计基于有知有行公开方法论独立计算，非有知有行官方数据。"
            "计算方法：等权 PE/PB 中位数历史分位数综合。"
            "与有知有行官方温度计可能存在合理偏差，仅供投资前风险检查参考。"
        ),
    )
def _render_input(
    *,
    missing: bool = False,
    final_judgment: str = "worth_holding",
    fund_type: str = "active_fund",
    tracking_error: ExtractedField[TrackingErrorValue] | None = None,
    valuation_state_resolution: ValuationStateResolution | None = None,
) -> TemplateRenderInput:
    """构造模板渲染输入。

    Args:
        missing: 是否构造缺失数据路径。
        final_judgment: 最终 selected 判断。
        fund_type: classified_fund_type fixture 值。
        tracking_error: 显式跟踪误差字段。
        valuation_state_resolution: 估值状态结构化真源。

    Returns:
        模板渲染输入。

    Raises:
        无显式抛出。
    """

    return TemplateRenderInput(
        structured_data=_bundle(
            missing=missing,
            anchor_without_row=True,
            fund_type=fund_type,
            tracking_error=tracking_error,
        ),
        rabc_attributions=(_rabc(missing=missing),),
        alpha_judgment=_alpha_judgment(),
        consistency_result=_consistency(),
        investor_experience=_investor_experience(missing=missing),
        risk_check_result=_risk_check(),
        stress_test_result=_stress_test(fund_type=fund_type),
        checklist_result=_checklist("gray" if missing else "green"),
        final_judgment_decision=FinalJudgmentDecision(
            selected_judgment=final_judgment,  # type: ignore[arg-type]
            derived_judgment=final_judgment,  # type: ignore[arg-type]
            source="derived",
            override_judgment=None,
            reasons=("fixture",),
            conflict_reasons=(),
        ),
        valuation_state_resolution=valuation_state_resolution,
        current_stage=None if missing else "规模稳定，收益归因仍需跨期观察",
    )


def _chapter_0_placeholder_case_input(case_name: str) -> TemplateRenderInput:
    """构造第 0 章旧占位文本回归测试输入。

    Args:
        case_name: 用例名称，支持 veto/watch/checklist_warning/stress_only/all_green。

    Returns:
        模板渲染输入。

    Raises:
        ValueError: 当用例名称不受支持时抛出。
    """

    input_data = _render_input()
    if case_name == "veto":
        veto_item = _risk_item(
            "liquidation_risk",
            "veto",
            current_value="30000000",
            threshold=">50000000 元",
            reason="基金规模低于清盘风险阈值。",
        )
        decision = replace(
            input_data.final_judgment_decision,
            selected_judgment="suggest_replace",
            derived_judgment="suggest_replace",
            reasons=("模板第 6 章存在否决项，最终判断应建议替换。",),
        )
        return replace(
            input_data,
            risk_check_result=_risk_check_with_item(veto_item, overall_status="veto"),
            final_judgment_decision=decision,
        )
    if case_name == "watch":
        watch_item = _risk_item(
            "style_drift",
            "watch",
            current_value="行业偏离声明风格",
            threshold="言行一致性需保持 aligned",
            reason="言行一致性出现黄灯。",
        )
        return replace(
            input_data,
            risk_check_result=_risk_check_with_item(watch_item, overall_status="watch"),
            final_judgment_decision=replace(
                input_data.final_judgment_decision,
                selected_judgment="needs_attention",
                derived_judgment="needs_attention",
            ),
        )
    if case_name == "checklist_warning":
        return replace(
            input_data,
            checklist_result=_checklist("yellow"),
            final_judgment_decision=replace(
                input_data.final_judgment_decision,
                selected_judgment="needs_attention",
                derived_judgment="needs_attention",
                reasons=("检查清单存在黄灯或灰灯问题，需要最小验证。",),
            ),
        )
    if case_name == "stress_only":
        return replace(
            input_data,
            final_judgment_decision=replace(
                input_data.final_judgment_decision,
                selected_judgment="needs_attention",
                derived_judgment="needs_attention",
                reasons=("压力测试接近或超过承受边界，需要最小验证。",),
            ),
        )
    if case_name == "all_green":
        return replace(
            input_data,
            stress_test_result=_stress_test_all_within_tolerance(),
            final_judgment_decision=replace(
                input_data.final_judgment_decision,
                reasons=("检查清单全绿、否决项通过、质量 gate 通过，当前证据下值得持有。",),
            ),
        )
    raise ValueError(f"未知第 0 章占位回归用例：{case_name}")


def _segment_lines(markdown: str, heading: str) -> tuple[str, ...]:
    """提取指定 ITEM_RULE 小节的正文行。

    Args:
        markdown: 章节 Markdown 正文。
        heading: ITEM_RULE 小节标题。

    Returns:
        小节行，包含标题行和标题后的 bullet 行。

    Raises:
        AssertionError: 当目标小节不存在时抛出。
    """

    lines = markdown.splitlines()
    try:
        start = lines.index(heading)
    except ValueError as exc:
        raise AssertionError(f"未找到 ITEM_RULE 小节：{heading}") from exc
    end = len(lines)
    for index in range(start + 1, len(lines)):
        if lines[index].startswith("#### ") or lines[index].startswith("> 📎 证据"):
            end = index
            break
    return tuple(lines[start:end])


def _evidence_boundary_line(markdown: str, heading: str) -> str:
    """提取指定 ITEM_RULE 小节的证据边界行。

    Args:
        markdown: 章节 Markdown 正文。
        heading: ITEM_RULE 小节标题。

    Returns:
        `- 证据边界：` bullet 行。

    Raises:
        AssertionError: 当小节内没有证据边界行时抛出。
    """

    for line in _segment_lines(markdown, heading):
        if line.startswith("- 证据边界："):
            return line
    raise AssertionError(f"ITEM_RULE 小节缺少证据边界行：{heading}")


def test_render_template_report_contains_exact_eight_design_chapters() -> None:
    """验证渲染报告包含设计要求的 8 章。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当章节结构不完整时抛出。
    """

    result = render_template_report(_render_input())
    chapter_titles = (
        "# 0. 投资要点概览",
        "# 1. 这只基金到底是什么产品",
        "# 2. R=A+B-C 收益归因",
        "# 3. 基金经理画像与言行一致性",
        "# 4. 投资者获得感",
        "# 5. 当前阶段与关键变化",
        "# 6. 核心风险与否决项",
        "# 7. 是否值得持有——最终判断",
    )

    assert all(title in result.report_markdown for title in chapter_titles)
    assert result.report_markdown.count("\n# ") == 7
    assert result.report_markdown.startswith("# 0. 投资要点概览")


def test_render_template_report_renders_chapter_0_profile_with_inception_date() -> None:
    """验证第 0 章基金简介渲染已披露成立时间。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当基金简介未渲染成立时间时抛出。
    """

    result = render_template_report(_render_input())

    assert "- 基金简介：基金经理 张三；管理规模 10.00亿元；成立时间 2020-01-15。" in result.report_markdown


def test_render_template_report_uses_veto_item_as_chapter_0_largest_risk() -> None:
    """验证第 0 章最大风险优先使用首个 veto 风险项。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当第 0 章未消费 veto 结构化结果时抛出。
    """

    input_data = _render_input(final_judgment="suggest_replace")
    veto_item = _risk_item(
        "liquidation_risk",
        "veto",
        current_value="30000000",
        threshold=">50000000 元",
        reason="基金规模低于清盘风险阈值。",
    )
    decision = replace(
        input_data.final_judgment_decision,
        selected_judgment="suggest_replace",
        derived_judgment="suggest_replace",
        reasons=("模板第 6 章存在否决项，最终判断应建议替换。",),
    )
    result = render_template_report(
        replace(
            input_data,
            risk_check_result=_risk_check_with_item(veto_item, overall_status="veto"),
            final_judgment_decision=decision,
        )
    )

    assert (
        "- 当前最大的风险：liquidation_risk 已触发否决，当前值=30000000，"
        "阈值=>50000000 元，原因=基金规模低于清盘风险阈值。"
    ) in result.chapter_blocks[0].body_markdown
    assert "终止阈值：liquidation_risk 维持 veto" in result.chapter_blocks[0].body_markdown
    assert "liquidation_risk 从 veto 复核为 pass" in result.chapter_blocks[0].body_markdown
    assert "当前未提供独立最大风险排序输入" not in result.chapter_blocks[0].body_markdown


def test_render_template_report_uses_watch_item_as_chapter_0_largest_risk() -> None:
    """验证第 0 章最大风险在无 veto 时使用首个 watch 风险项。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当第 0 章未消费 watch 结构化结果时抛出。
    """

    watch_item = _risk_item(
        "style_drift",
        "watch",
        current_value="行业偏离声明风格",
        threshold="言行一致性需保持 aligned",
        reason="言行一致性出现黄灯。",
    )
    input_data = replace(
        _render_input(final_judgment="needs_attention"),
        risk_check_result=_risk_check_with_item(watch_item, overall_status="watch"),
    )

    result = render_template_report(input_data)

    assert (
        "- 当前最大的风险：style_drift 需要跟踪或补证，当前值=行业偏离声明风格，"
        "阈值=言行一致性需保持 aligned，原因=言行一致性出现黄灯。"
    ) in result.chapter_blocks[0].body_markdown
    assert "降级或终止阈值：style_drift 从 watch 确认为 veto" in result.chapter_blocks[0].body_markdown
    assert "style_drift 从 watch 复核为 pass" in result.chapter_blocks[0].body_markdown


def test_render_template_report_uses_checklist_warning_for_chapter_0_thresholds() -> None:
    """验证第 0 章阈值可由检查清单黄灯驱动。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当第 0 章阈值未消费 checklist warning 时抛出。
    """

    input_data = _render_input(final_judgment="needs_attention")
    yellow_checklist = _checklist("yellow")
    decision = replace(
        input_data.final_judgment_decision,
        selected_judgment="needs_attention",
        derived_judgment="needs_attention",
        reasons=("检查清单存在黄灯或灰灯问题，需要最小验证。",),
    )
    result = render_template_report(
        replace(input_data, checklist_result=yellow_checklist, final_judgment_decision=decision)
    )

    assert "检查清单“超额收益能覆盖成本吗？”从 yellow/watch 复核为 green/pass" in result.chapter_blocks[0].body_markdown
    assert (
        "降级或终止阈值：检查清单“超额收益能覆盖成本吗？”从 yellow/watch 转为 red/block"
        in result.chapter_blocks[0].body_markdown
    )
    assert "需要后续跨期证据确认" not in result.chapter_blocks[0].body_markdown


def test_render_template_report_uses_stress_scenario_as_chapter_0_risk_fallback() -> None:
    """验证风险检查无动作项时第 0 章可使用压力测试场景作为最大风险。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当压力测试关注场景被错误渲染为无风险时抛出。
    """

    input_data = _chapter_0_placeholder_case_input("stress_only")
    result = render_template_report(input_data)
    chapter_0 = result.chapter_blocks[0].body_markdown

    assert "当前最大的风险：压力场景 minus_40 接近或超过承受边界" in chapter_0
    assert "压力场景 minus_40 从 near_limit 复核为 within_tolerance" in chapter_0
    assert "当前未发现一票否决或需跟踪风险" not in chapter_0


def test_render_template_report_chapter_0_all_green_pass_uses_monitoring_threshold() -> None:
    """验证第 0 章全绿通过时输出具体监控阈值。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当第 0 章仍输出旧 blanket placeholder 时抛出。
    """

    input_data = _render_input()
    decision = replace(
        input_data.final_judgment_decision,
        reasons=("检查清单全绿、否决项通过、质量 gate 通过，当前证据下值得持有。",),
    )
    result = render_template_report(
        replace(
            input_data,
            stress_test_result=_stress_test_all_within_tolerance(),
            final_judgment_decision=decision,
        )
    )
    chapter_0 = result.chapter_blocks[0].body_markdown

    assert "否决项检查为 pass，当前未发现一票否决或需跟踪风险" in chapter_0
    assert "任一否决项转为 watch/veto、检查清单转黄/灰/红" in chapter_0
    assert "当前未提供独立最大风险排序输入" not in chapter_0
    assert "需要后续跨期证据确认" not in chapter_0


@pytest.mark.parametrize(
    "case_name",
    ("veto", "watch", "checklist_warning", "stress_only", "all_green"),
)
def test_render_template_report_chapter_0_never_emits_old_blanket_placeholders(
    case_name: str,
) -> None:
    """验证第 0 章各结构化信号路径均不输出旧 blanket placeholder。

    Args:
        case_name: 第 0 章结构化信号路径。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当旧占位文本回归时抛出。
    """

    result = render_template_report(_chapter_0_placeholder_case_input(case_name))
    chapter_0 = result.chapter_blocks[0].body_markdown

    assert "当前最大的风险" in chapter_0
    assert "什么变化会升级、降级或终止当前动作" in chapter_0
    assert "当前未提供独立最大风险排序输入" not in chapter_0
    assert "需要后续跨期证据确认" not in chapter_0


def test_render_template_report_exposes_contract_aligned_chapter_blocks() -> None:
    """验证渲染结果暴露与 CHAPTER_CONTRACT 对齐的章节块。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当章节块未对齐 manifest 契约时抛出。
    """

    result = render_template_report(_render_input())

    assert len(result.chapter_blocks) == 8
    assert tuple(block.chapter_id for block in result.chapter_blocks) == tuple(range(8))
    for block in result.chapter_blocks:
        contract = get_chapter_contract(block.chapter_id)
        assert block.title == contract.title
        assert block.heading == get_template_chapter_heading(block.chapter_id)
        assert block.markdown.startswith(block.heading)
        assert block.body_markdown
        assert block.contract == contract
    assert result.chapter_blocks[2].contract.required_output_items
    assert result.audit_input.report_markdown == result.report_markdown
    assert result.report_markdown
    assert result.audit_input
    assert result.evidence_anchors


def test_split_rendered_chapter_blocks_matches_render_result_and_excludes_appendix() -> None:
    """验证公共 splitter 与渲染结果共用章节块语义。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 splitter 吞入附录或破坏 Markdown 兼容时抛出。
    """

    result = render_template_report(_render_input())
    blocks = split_rendered_chapter_blocks(result.report_markdown)
    joined_blocks = "\n\n".join(block.markdown for block in blocks)

    assert blocks == result.chapter_blocks
    assert "## 证据与出处" not in result.chapter_blocks[7].body_markdown
    assert result.report_markdown.startswith(joined_blocks)


@pytest.mark.parametrize(
    ("broken_markdown", "match_text"),
    (
        ("", "为空"),
        ("# 0. 错误标题\n\nbody", "不匹配"),
        ("# 8. 越界\n\nbody", "越界"),
        ("# 非模板标题\n\nbody", "非模板一级标题"),
    ),
)
def test_split_rendered_chapter_blocks_fails_closed_for_invalid_headings(
    broken_markdown: str,
    match_text: str,
) -> None:
    """验证 splitter 对非法标题 fail closed。

    Args:
        broken_markdown: 非法 Markdown fixture。
        match_text: 预期错误信息片段。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当非法标题未抛出 `ValueError` 时抛出。
    """

    with pytest.raises(ValueError, match=match_text):
        split_rendered_chapter_blocks(broken_markdown)


def test_split_rendered_chapter_blocks_fails_closed_for_missing_duplicate_and_order() -> None:
    """验证 splitter 对缺章、重复和乱序 fail closed。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当章节序列错误未抛出 `ValueError` 时抛出。
    """

    result = render_template_report(_render_input())
    chapter_1 = result.chapter_blocks[1].markdown
    chapter_2 = result.chapter_blocks[2].markdown

    missing = result.report_markdown.replace(f"\n\n{chapter_2}", "", 1)
    duplicate = result.report_markdown.replace(f"\n\n{chapter_2}", f"\n\n{chapter_1}\n\n{chapter_2}", 1)
    out_of_order = result.report_markdown.replace(f"\n\n{chapter_1}\n\n{chapter_2}", f"\n\n{chapter_2}\n\n{chapter_1}", 1)

    with pytest.raises(ValueError, match="0..7"):
        split_rendered_chapter_blocks(missing)
    with pytest.raises(ValueError, match="重复"):
        split_rendered_chapter_blocks(duplicate)
    with pytest.raises(ValueError, match="0..7"):
        split_rendered_chapter_blocks(out_of_order)


def test_split_rendered_chapter_blocks_fails_closed_for_embedded_non_template_heading() -> None:
    """验证 splitter 拒绝合法章节序列中混入的非模板一级标题。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当混入非模板一级标题未抛出 `ValueError` 时抛出。
    """

    result = render_template_report(_render_input())
    chapter_2 = result.chapter_blocks[2].markdown
    broken_markdown = result.report_markdown.replace(
        f"\n\n{chapter_2}",
        f"\n\n# 非法标题\n\nbody\n\n{chapter_2}",
        1,
    )

    with pytest.raises(ValueError, match="非模板一级标题"):
        split_rendered_chapter_blocks(broken_markdown)


def test_render_template_report_formats_evidence_anchors_with_year_section_and_optional_row() -> None:
    """验证正文证据锚点格式包含年份、章节和描述。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当证据格式不满足规范时抛出。
    """

    result = render_template_report(_render_input())

    assert "> 📎 证据：年报2024§1 §1: fixture" in result.report_markdown
    assert "> 📎 证据：年报§1" not in result.report_markdown


def test_render_template_report_formats_appendix_anchor_with_table_and_row_exactly() -> None:
    """验证附录年报锚点精确输出年份、章节、表格和行定位。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当附录格式偏离设计规范时抛出。
    """

    result = render_template_report(_render_input())

    assert "## 证据与出处" in result.report_markdown
    assert "年报2024§8表T1行industry_distribution：industry_distribution: fixture" in result.report_markdown


def test_render_template_report_formats_missing_row_fallback_without_dropping_year_or_section() -> None:
    """验证附录缺少表格或行定位时显式降级且不丢年份章节。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当缺失定位被静默省略时抛出。
    """

    result = render_template_report(_render_input())

    assert "- [1] 年报2024§1表未定位行未定位：§1: fixture" in result.report_markdown


def test_render_template_report_retains_page_number_as_location_metadata() -> None:
    """验证页码作为附加位置元数据保留。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当页码丢失时抛出。
    """

    input_data = _render_input()
    paged_anchor = _anchor("§1", "basic_identity", page_number=18)
    basic_identity = replace(input_data.structured_data.basic_identity, anchors=(paged_anchor,))
    structured_data = replace(input_data.structured_data, basic_identity=basic_identity)
    result = render_template_report(replace(input_data, structured_data=structured_data))

    assert "> 📎 证据：年报2024§1（第18页） basic_identity" in result.report_markdown
    assert "年报2024§1表未定位行basic_identity（第18页）：basic_identity: fixture" in result.report_markdown


def test_render_template_report_renders_non_annual_source_kind_explicitly() -> None:
    """验证非年报来源不会被伪装成年报。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当非年报来源被错误标成年报时抛出。
    """

    input_data = _render_input()
    api_anchor = _anchor(
        "nav_return",
        "2024-12-31",
        source_kind="external_api",
        document_year=None,
        page_number=1,
    )
    basic_identity = replace(input_data.structured_data.basic_identity, anchors=(api_anchor,))
    structured_data = replace(input_data.structured_data, basic_identity=basic_identity)
    result = render_template_report(replace(input_data, structured_data=structured_data))

    assert "> 📎 证据：外部数据(external_api)§nav_return行2024-12-31（第1页） 2024-12-31" in result.report_markdown
    assert "外部数据(external_api)§nav_return行2024-12-31（第1页）：2024-12-31: fixture" in result.report_markdown
    assert "年报2024§nav_return" not in result.report_markdown


def test_render_template_report_emits_missing_evidence_line_and_appendix_entry_per_chapter() -> None:
    """验证缺少章节证据时正文和附录都显式输出数据不足。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当缺证章节被静默省略时抛出。
    """

    input_data = _render_input()
    result = render_template_report(replace(input_data, rabc_attributions=()))

    assert "> 📎 证据：数据不足，当前章节未携带证据锚点" in result.report_markdown
    assert (
        "- [M2] 年报2024§未定位表未定位行未定位："
        "数据不足，模板第2章《R=A+B-C 收益归因》当前输入未携带证据锚点。"
    ) in result.report_markdown


def test_render_template_report_formats_manager_alignment_and_reason_punctuation() -> None:
    """验证第 3/4 章不会泄漏 Python 容器表示或重复句末标点。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当文本渲染格式退化时抛出。
    """

    result = render_template_report(_render_input())

    assert "dict_values" not in result.report_markdown
    assert "利益一致性原始披露：基金经理持有本基金" in result.report_markdown
    assert "投资者收益高于产品收益。。" not in result.report_markdown


def test_fund_readme_has_single_current_template_layer_entry() -> None:
    """验证 Fund 包 README 不保留重复过期的 template 分层说明。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 README 出现重复或过期条目时抛出。
    """

    readme_text = (_REPO_ROOT / "fund_agent/fund/README.md").read_text(encoding="utf-8")
    current_entry = (
        "- `template/`：模板渲染能力。当前包含 `renderer.py`，"
        "只消费 P1/P2 结构化结果并输出 8 章 Markdown、章节块与程序审计输入。"
    )

    assert readme_text.count(current_entry) == 1
    assert "- `template/`：后续模板能力的扩展位置" not in readme_text


def test_render_template_report_builds_audit_input_that_passes_p1_p2_p3_c2_l1_r1_r2() -> None:
    """验证渲染结果可直接通过程序审计。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当审计不通过时抛出。
    """

    result = render_template_report(_render_input())
    audit_input = build_programmatic_audit_input(result)
    audit_result = run_programmatic_audit(audit_input)

    assert audit_input.report_markdown == result.report_markdown
    assert audit_input.chapter_blocks == result.chapter_blocks
    assert audit_input.rabc_attributions == (_rabc(),)
    assert audit_result.passed
    assert audit_result.checked_rules == ("P1", "P2", "P3", "C2", "L1", "R1", "R2")


def test_render_template_report_applies_active_fund_lens_to_target_slots() -> None:
    """验证主动基金报告在第 0/1 章应用确定性 lens 关注点。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当主动基金 lens 未写入目标 slot 时抛出。
    """

    result = render_template_report(_render_input(fund_type="active_fund"))

    assert result.lens_application_plan is not None
    assert result.lens_application_plan.fund_type == "active_fund"
    assert "- 当前最值得盯住的变量：基金经理言行一致性与超额收益稳定性。当前公开输入仍需后续证据验证。" in result.chapter_blocks[0].body_markdown
    assert "- 看这类基金最先看什么：先看基金经理、超额收益稳定性、言行一致性。" in result.chapter_blocks[1].body_markdown
    assert "preferred_lens" not in result.report_markdown


def test_render_template_report_applies_index_fund_lens_to_target_slots() -> None:
    """验证指数基金报告在第 0/1 章应用确定性 lens 关注点。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当指数基金 lens 未写入目标 slot 时抛出。
    """

    active_result = render_template_report(_render_input(fund_type="active_fund"))
    index_result = render_template_report(_render_input(fund_type="index_fund"))
    index_audit_result = run_programmatic_audit(index_result.audit_input)

    assert index_result.lens_application_plan is not None
    assert index_result.lens_application_plan.fund_type == "index_fund"
    assert "- 当前最值得盯住的变量：跟踪误差、费率和规模流动性。当前公开输入仍需后续证据验证。" in index_result.chapter_blocks[0].body_markdown
    assert "- 看这类基金最先看什么：先看跟踪误差、费率、规模/流动性。" in index_result.chapter_blocks[1].body_markdown
    assert "基金经理言行一致性与超额收益稳定性" not in index_result.chapter_blocks[0].body_markdown
    assert active_result.chapter_blocks[0].body_markdown != index_result.chapter_blocks[0].body_markdown
    assert active_result.chapter_blocks[1].body_markdown != index_result.chapter_blocks[1].body_markdown
    assert index_audit_result.passed


@pytest.mark.parametrize(
    ("fund_type", "expected_markers"),
    (
        ("index_fund", ("#### 指数编制规则与成分股", "#### 跟踪误差分析")),
        ("active_fund", ("#### 基金经理投资哲学", "#### 超额收益分年度拆解")),
        (
            "enhanced_index",
            ("#### 指数编制规则与成分股", "#### 超额收益分年度拆解", "#### 跟踪误差分析"),
        ),
        ("bond_fund", ()),
        ("qdii_fund", ()),
        ("fof_fund", ()),
    ),
)
def test_render_template_report_applies_item_rule_segments_by_fund_type(
    fund_type: FundType,
    expected_markers: tuple[str, ...],
) -> None:
    """验证六类基金按 ITEM_RULE 决策渲染或删除条件段落。

    Args:
        fund_type: 标准基金类型。
        expected_markers: 当前基金类型应渲染的 ITEM_RULE 小节标题。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 ITEM_RULE 段落集合或审计上下文不符合预期时抛出。
    """

    result = render_template_report(_render_input(fund_type=fund_type))
    audit_result = run_programmatic_audit(result.audit_input)

    assert result.item_rule_audit_context == "identity_present"
    assert result.audit_input.item_rule_audit_context == "identity_present"
    assert result.item_rule_decisions == result.audit_input.item_rule_decisions
    assert audit_result.passed
    for marker in _ITEM_RULE_MARKERS:
        assert (marker in result.report_markdown) is (marker in expected_markers)


def test_render_template_report_replaces_tracking_error_only_from_structured_data() -> None:
    """验证跟踪误差段落只通过 structured_data.tracking_error 替换占位。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当跟踪误差未按结构化字段渲染时抛出。
    """

    result = render_template_report(
        _render_input(fund_type="index_fund", tracking_error=_tracking_error_field("1.23%"))
    )
    chapter_2 = result.chapter_blocks[2].body_markdown

    assert "- 跟踪误差：1.23%（报告期，年化，来源：年报直接披露）。" in chapter_2
    assert "fixture direct disclosure" in chapter_2
    assert "年报2024§3 tracking_error" in chapter_2


def test_render_template_report_defensively_handles_missing_tracking_error_value() -> None:
    """验证渲染器不用 assert 作为运行时完整性保护。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当值缺失路径抛异常或误渲染时抛出。
    """

    tracking_error: ExtractedField[TrackingErrorValue] = ExtractedField(
        value=None,
        anchors=(_anchor("§3", "tracking_error"),),
        extraction_mode="direct",
        note="fixture inconsistent field",
    )

    result = render_template_report(
        _render_input(fund_type="index_fund", tracking_error=tracking_error)
    )
    chapter_2 = result.chapter_blocks[2].body_markdown

    assert "- 跟踪误差：数据不足，当前输入未抽取跟踪误差。" in chapter_2


def test_render_template_report_keeps_methodology_and_constituents_insufficient_for_benchmark_only() -> None:
    """验证 benchmark-only 指数画像不替代编制方法或成分股。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当基准证据被误用为编制方法或成分股时抛出。
    """

    result = render_template_report(_render_input(fund_type="index_fund"))
    chapter_1 = result.chapter_blocks[1].body_markdown

    assert "- 业绩基准引用：沪深300指数收益率*80%+中债指数收益率*20%。" in chapter_1
    assert "- 编制方法：数据不足，当前输入未抽取指数编制方法。" in chapter_1
    assert "- 成分股：数据不足，当前输入未抽取指数成分股。" in chapter_1


def test_render_template_report_renders_item_rule_segments_with_fixed_bullets_and_evidence_boundaries() -> None:
    """验证 ITEM_RULE 段落使用固定 bullet 且不伪造证据边界。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当固定段落或数据不足边界被破坏时抛出。
    """

    result = render_template_report(_render_input(fund_type="enhanced_index"))
    chapter_1 = result.chapter_blocks[1].body_markdown
    chapter_2 = result.chapter_blocks[2].body_markdown
    input_data = _render_input(fund_type="enhanced_index")
    benchmark_reference = _body_anchor_reference(input_data.structured_data.benchmark.anchors[0])
    tracking_evidence_line = _evidence_boundary_line(chapter_2, "#### 跟踪误差分析")
    index_evidence_line = _evidence_boundary_line(chapter_1, "#### 指数编制规则与成分股")
    index_segment = _segment_lines(chapter_1, "#### 指数编制规则与成分股")

    assert "#### 指数编制规则与成分股\n- 业绩基准引用：" in chapter_1
    assert "- 编制方法：数据不足，当前输入未抽取指数编制方法。" in chapter_1
    assert "- 成分股：数据不足，当前输入未抽取指数成分股。" in chapter_1
    assert "#### 超额收益分年度拆解\n- 可用周期：2024。" in chapter_2
    assert "- 分年度结论：数据不足，当前输入未形成多年度完整序列时不得推断稳定性。" in chapter_2
    assert "#### 跟踪误差分析\n- 跟踪误差：数据不足，当前输入未抽取跟踪误差。" in chapter_2
    assert "- 后续最小验证：补充跟踪误差披露或净值/指数日频序列后再计算。" in chapter_2
    assert tracking_evidence_line == _ITEM_RULE_EMPTY_EVIDENCE_BOUNDARY
    assert index_evidence_line.count(benchmark_reference) == 1
    assert "；" not in index_evidence_line
    assert not any(line.startswith("> 📎 证据") for line in index_segment)


def test_render_template_report_renders_item_rule_empty_anchor_boundary_for_present_identity() -> None:
    """验证身份存在但 ITEM_RULE 相关锚点为空时输出精确缺证边界。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当空锚点路径未输出精确缺证文本时抛出。
    """

    input_data = _render_input(fund_type="index_fund")
    structured_data = replace(
        input_data.structured_data,
        benchmark=replace(input_data.structured_data.benchmark, anchors=()),
    )
    attribution = replace(input_data.rabc_attributions[0], anchors=())
    result = render_template_report(
        replace(input_data, structured_data=structured_data, rabc_attributions=(attribution,))
    )

    evidence_line = _evidence_boundary_line(result.chapter_blocks[2].body_markdown, "#### 跟踪误差分析")

    assert result.item_rule_audit_context == "identity_present"
    assert evidence_line == _ITEM_RULE_EMPTY_EVIDENCE_BOUNDARY


def test_item_rule_evidence_bullet_deduplicates_duplicate_anchors() -> None:
    """验证 ITEM_RULE 私有证据边界 helper 对重复锚点稳定去重。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当重复锚点被重复渲染时抛出。
    """

    anchor = _anchor("§2", "benchmark")
    reference = _body_anchor_reference(anchor)

    evidence_line = _item_rule_evidence_bullet((anchor, anchor))

    assert evidence_line == f"- 证据边界：{reference}。"
    assert evidence_line.count(reference) == 1


def test_render_template_report_missing_data_path_is_explicit_and_audit_compatible() -> None:
    """验证缺失数据路径显式输出未披露或数据不足且仍兼容审计输入。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当缺失数据被静默省略或审计输入不兼容时抛出。
    """

    result = render_template_report(_render_input(missing=True, final_judgment="needs_attention"))
    audit_result = run_programmatic_audit(result.audit_input)

    assert "未披露" in result.report_markdown
    assert "数据不足" in result.report_markdown
    assert result.lens_application_plan is None
    assert result.item_rule_decisions == ()
    assert result.item_rule_audit_context == "identity_missing"
    assert result.audit_input.item_rule_audit_context == "identity_missing"
    assert result.audit_input.final_judgment == "needs_attention"
    assert result.audit_input.derived_final_judgment == "needs_attention"
    assert result.audit_input.final_judgment_source == "derived"
    assert audit_result.passed


def test_render_template_report_rejects_present_identity_without_classified_fund_type() -> None:
    """验证存在身份数据但缺少基金类型时 renderer fail closed。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当缺少基金类型未抛出 `ValueError` 时抛出。
    """

    input_data = _render_input()
    identity = dict(input_data.structured_data.basic_identity.value or {})
    identity.pop("classified_fund_type")
    structured_data = replace(
        input_data.structured_data,
        basic_identity=replace(input_data.structured_data.basic_identity, value=identity),
    )

    with pytest.raises(ValueError, match="classified_fund_type"):
        render_template_report(replace(input_data, structured_data=structured_data))


def test_render_template_report_rejects_unsupported_classified_fund_type() -> None:
    """验证不受支持的基金类型在 renderer 入口 fail closed。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当非法基金类型未抛出 `ValueError` 时抛出。
    """

    with pytest.raises(ValueError, match="不支持的基金类型"):
        render_template_report(_render_input(fund_type="money_market_fund"))


def test_render_template_report_rejects_unsafe_final_judgment_wording() -> None:
    """验证最终判断只允许三类持有判断。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当非法最终判断未被拒绝时抛出。
    """

    with pytest.raises(ValueError, match="final_judgment"):
        render_template_report(_render_input(final_judgment="buy"))  # type: ignore[arg-type]


def test_render_template_report_does_not_emit_buy_sell_wording() -> None:
    """验证报告不输出明确买卖建议、收益预测或仓位比例措辞。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当报告包含禁用措辞时抛出。
    """

    result = render_template_report(_render_input(final_judgment="suggest_replace"))
    forbidden_terms = ("建议买入", "建议卖出", "收益预测", "仓位比例")

    assert "建议替换" in result.report_markdown
    assert all(term not in result.report_markdown for term in forbidden_terms)


@pytest.mark.parametrize("forbidden_text", ("买入金额", "建议买入", "建议卖出", "买入信号"))
def test_validate_report_wording_rejects_direct_trading_advice(
    forbidden_text: str,
) -> None:
    """验证 wording validator 仍拒绝明确交易建议措辞。

    Args:
        forbidden_text: 人工构造的禁用交易建议文本。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当明确交易建议未被拒绝时抛出。
    """

    with pytest.raises(ValueError, match="报告包含禁用投资建议措辞"):
        _validate_report_wording(f"# 7. 是否值得持有——最终判断\n- 后续动作：{forbidden_text}。")


@pytest.mark.parametrize(
    "strategy_summary",
    ("好价格可以买入并持有好公司", "市场波动时不宜卖出优质公司"),
)
def test_render_template_report_allows_disclosed_strategy_context(
    strategy_summary: str,
) -> None:
    """验证年报披露语境中的交易动词不会被误判为直接交易建议。

    Args:
        strategy_summary: §4 管理人策略披露原文。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当披露原文被阻断或报告输出直接买卖建议时抛出。
    """

    input_data = _render_input()
    strategy_field = _field(
        {"strategy_summary": strategy_summary},
        "§4",
        "manager_strategy_text",
    )
    structured_data = replace(
        input_data.structured_data,
        manager_strategy_text=strategy_field,
    )

    result = render_template_report(replace(input_data, structured_data=structured_data))

    assert f"披露策略：{strategy_summary}。" in result.report_markdown
    assert "建议买入" not in result.report_markdown
    assert "建议卖出" not in result.report_markdown


def test_render_template_report_keeps_l1_r1_r2_structured_inputs_unmodified() -> None:
    """验证 L1/R1/R2 所需结构化输入由渲染结果原样携带。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当结构化审计输入被模板改写时抛出。
    """

    input_data = _render_input()
    modified_checklist = replace(input_data.checklist_result, next_minimum_verification="确认当前估值输入。")
    input_data = replace(input_data, checklist_result=modified_checklist)

    result = render_template_report(input_data)

    assert result.audit_input.rabc_attributions == input_data.rabc_attributions
    assert result.audit_input.checklist_result == modified_checklist
    assert result.audit_input.final_judgment == input_data.final_judgment_decision.selected_judgment
    assert (
        result.audit_input.derived_final_judgment
        == input_data.final_judgment_decision.derived_judgment
    )
    assert result.audit_input.final_judgment_source == input_data.final_judgment_decision.source


def test_render_template_report_outputs_thermometer_disclaimer_and_anchor() -> None:
    """验证调用自建温度计时报告正文和附录展示免责声明与锚点。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 免责声明或 external_api 锚点缺失时抛出。
    """

    resolution = _thermometer_valuation_resolution()
    checklist = _checklist("green")
    valuation_item = next(item for item in checklist.items if item.code == "valuation")
    projected_item = replace(
        valuation_item,
        anchors=resolution.anchors,
        reason=resolution.reason,
    )
    checklist = replace(
        checklist,
        items=tuple(projected_item if item.code == "valuation" else item for item in checklist.items),
    )
    input_data = replace(
        _render_input(valuation_state_resolution=resolution),
        checklist_result=checklist,
    )

    result = render_template_report(input_data)

    assert resolution.disclaimer in result.report_markdown
    assert "外部数据(external_api)§thermometer表fixture_source行000300:2024-12-31" in result.report_markdown
    assert result.audit_input.valuation_state_resolution == resolution
    assert all(term not in resolution.disclaimer for term in ("买入", "卖出", "仓位比例", "收益预测"))
