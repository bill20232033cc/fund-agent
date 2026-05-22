"""否决项检查模块。

本模块属于基金 Capability 层，服务模板第 6 章“核心风险与否决项”。
它只消费结构化字段和调用方显式输入的外部指标，不直接读取年报文件。
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import Final, Literal

from fund_agent.fund.analysis._ratios import parse_ratio
from fund_agent.fund.analysis.consistency_check import ConsistencyCheckResult
from fund_agent.fund.extractors.models import EvidenceAnchor, ExtractedField, TrackingErrorValue
from fund_agent.fund.fund_type import FundType

RiskCheckCode = Literal[
    "liquidation_risk",
    "manager_tenure",
    "style_drift",
    "excessive_fee",
    "tracking_error",
]
RiskCheckStatus = Literal["pass", "watch", "veto", "insufficient_data"]
StressScenarioCode = Literal["minus_20", "minus_40", "minus_60"]
StressSeverity = Literal["normal", "extreme", "historical_worst", "beyond_historical"]
StressCapacityStatus = Literal["within_tolerance", "near_limit", "beyond_tolerance", "not_provided"]
RiskTrackingErrorSource = Literal[
    "direct_disclosure",
    "calculated_from_series",
    "developer_override",
    "missing",
    "not_applicable",
]
RiskTrackingErrorAuthority = Literal[
    "capability_structured_data",
    "developer_override",
    "missing",
    "not_applicable",
]
RiskTrackingErrorFieldMode = Literal["direct", "derived", "missing", "not_applicable"]

_LIQUIDATION_THRESHOLD_YUAN: Final[Decimal] = Decimal("50000000")
_MANAGER_TENURE_MONTHS_THRESHOLD: Final[int] = 6
_FEE_MULTIPLE_THRESHOLD: Final[Decimal] = Decimal("2")
_TRACKING_ERROR_THRESHOLD: Final[Decimal] = Decimal("0.02")
_INDEX_FUND_TYPES: Final[frozenset[FundType]] = frozenset({"index_fund", "enhanced_index"})
_NUMBER_PATTERN: Final[re.Pattern[str]] = re.compile(r"[-+]?\d+(?:,\d{3})*(?:\.\d+)?")
_DEFAULT_STRESS_SCENARIOS: Final[tuple[tuple[StressScenarioCode, Decimal], ...]] = (
    ("minus_20", Decimal("-0.20")),
    ("minus_40", Decimal("-0.40")),
    ("minus_60", Decimal("-0.60")),
)
_DEFAULT_STRESS_THRESHOLDS: Final[dict[FundType, tuple[Decimal, Decimal, Decimal]]] = {
    "index_fund": (Decimal("0.30"), Decimal("0.50"), Decimal("0.70")),
    "active_fund": (Decimal("0.25"), Decimal("0.45"), Decimal("0.65")),
    "bond_fund": (Decimal("0.05"), Decimal("0.10"), Decimal("0.20")),
    "enhanced_index": (Decimal("0.25"), Decimal("0.45"), Decimal("0.60")),
    "qdii_fund": (Decimal("0.35"), Decimal("0.55"), Decimal("0.75")),
    "fof_fund": (Decimal("0.20"), Decimal("0.40"), Decimal("0.55")),
}
_NEAR_TOLERANCE_BUFFER: Final[Decimal] = Decimal("0.90")


@dataclass(frozen=True, slots=True)
class RiskCheckRule:
    """否决项检查规则配置。

    Attributes:
        liquidation_threshold_yuan: 清盘风险规模阈值。
        manager_tenure_months_threshold: 基金经理管理本基金最短月数。
        fee_multiple_threshold: 总成本超过同类中位数的倍数阈值。
        tracking_error_threshold: 指数基金跟踪误差阈值。
    """

    liquidation_threshold_yuan: Decimal = _LIQUIDATION_THRESHOLD_YUAN
    manager_tenure_months_threshold: int = _MANAGER_TENURE_MONTHS_THRESHOLD
    fee_multiple_threshold: Decimal = _FEE_MULTIPLE_THRESHOLD
    tracking_error_threshold: Decimal = _TRACKING_ERROR_THRESHOLD


@dataclass(frozen=True, slots=True)
class RiskCheckItem:
    """单个否决项检查结果。

    Attributes:
        code: 检查项编码。
        status: 检查结果。
        current_value: 当前值。
        threshold: 阈值。
        anchors: 参与判断的证据锚点。
        reason: 判断依据。
    """

    code: RiskCheckCode
    status: RiskCheckStatus
    current_value: str | None
    threshold: str
    anchors: tuple[EvidenceAnchor, ...]
    reason: str


@dataclass(frozen=True, slots=True)
class RiskCheckResult:
    """否决项检查汇总结果。

    Attributes:
        overall_status: 汇总结果。
        items: 5 项否决检查结果。
        veto_items: 触发一票否决的检查项。
        watch_items: 需要跟踪或验证的检查项。
        next_minimum_verification: 下一步最小验证问题。
    """

    overall_status: RiskCheckStatus
    items: tuple[RiskCheckItem, ...]
    veto_items: tuple[RiskCheckItem, ...]
    watch_items: tuple[RiskCheckItem, ...]
    next_minimum_verification: str


@dataclass(frozen=True, slots=True)
class ResolvedTrackingErrorForRisk:
    """风险检查使用的跟踪误差解析结果，见模板第 6 章否决项。

    Attributes:
        value: 标准化小数比例。
        value_text: 人类可读数值文本。
        source_type: 跟踪误差来源类型。
        authority: 当前风险检查采用的数据权威。
        field_extraction_mode: Capability 字段抽取模式。
        anchors: Capability 证据锚点；开发覆盖为空。
        provenance_note: 来源说明。
        missing_reason: 缺失原因。
        conflict_note: 开发覆盖和 Capability 数据冲突说明。
        is_product_evidence: 是否可作为产品证据。
    """

    value: Decimal | None
    value_text: str | None
    source_type: RiskTrackingErrorSource
    authority: RiskTrackingErrorAuthority
    field_extraction_mode: RiskTrackingErrorFieldMode
    anchors: tuple[EvidenceAnchor, ...]
    provenance_note: str
    missing_reason: str | None
    conflict_note: str | None
    is_product_evidence: bool


@dataclass(frozen=True, slots=True)
class StressTestRule:
    """压力测试规则配置，见模板第 6 章。

    Attributes:
        scenarios: 固定压力场景，默认模拟 -20% / -40% / -60%。
        severity_thresholds: 按基金类型配置的正常、极端、历史最差阈值。
    """

    scenarios: tuple[tuple[StressScenarioCode, Decimal], ...] = _DEFAULT_STRESS_SCENARIOS
    severity_thresholds: dict[FundType, tuple[Decimal, Decimal, Decimal]] | None = None


@dataclass(frozen=True, slots=True)
class StressScenarioResult:
    """单个压力场景结果。

    Attributes:
        code: 场景编码。
        decline_rate: 场景跌幅，小数比例。
        investment_amount: 投入金额。
        account_balance: 场景下账户余额。
        floating_loss_amount: 场景下浮亏金额，使用正数表示亏损额。
        severity: 按基金类型阈值划分的承压等级。
        capacity_status: 与显式最大可承受亏损比较后的承受状态。
        threshold: 当前基金类型的压力阈值说明。
        reason: 判断依据。
    """

    code: StressScenarioCode
    decline_rate: Decimal
    investment_amount: Decimal
    account_balance: Decimal
    floating_loss_amount: Decimal
    severity: StressSeverity
    capacity_status: StressCapacityStatus
    threshold: str
    reason: str


@dataclass(frozen=True, slots=True)
class StressTestResult:
    """压力测试汇总结果。

    Attributes:
        fund_type: 基金类型。
        investment_amount: 投入金额。
        max_tolerable_loss_rate: 显式最大可承受亏损比例。
        scenarios: 压力场景结果。
        worst_scenario: 浮亏最大的场景。
        anchors: 参与判断的证据锚点。
        next_minimum_verification: 下一步最小验证问题。
    """

    fund_type: FundType
    investment_amount: Decimal
    max_tolerable_loss_rate: Decimal | None
    scenarios: tuple[StressScenarioResult, ...]
    worst_scenario: StressScenarioResult
    anchors: tuple[EvidenceAnchor, ...]
    next_minimum_verification: str


def run_risk_checks(
    *,
    basic_identity: ExtractedField[dict[str, object]],
    fee_schedule: ExtractedField[dict[str, object]],
    consistency_result: ConsistencyCheckResult | None,
    fund_type: FundType,
    manager_tenure_months: int | None = None,
    peer_fee_median: Decimal | str | int | float | None = None,
    tracking_error: ResolvedTrackingErrorForRisk | None = None,
    rule: RiskCheckRule | None = None,
) -> RiskCheckResult:
    """执行 5 项否决条件检查，见模板第 6 章。

    Args:
        basic_identity: P1 基础身份字段，需包含基金规模。
        fee_schedule: P1 费率字段。
        consistency_result: P2-S3 言行一致性结果。
        fund_type: 标准化基金类型。
        manager_tenure_months: 基金经理管理本基金月数，需显式提供。
        peer_fee_median: 同类总费率中位数，需显式提供。
        tracking_error: 已解析的指数基金跟踪误差风险输入。
        rule: 规则配置。

    Returns:
        5 项否决检查汇总结果。

    Raises:
        ValueError: 当显式费率格式非法时抛出。
    """

    active_rule = rule or RiskCheckRule()
    items = (
        _check_liquidation_risk(basic_identity, active_rule),
        _check_manager_tenure(manager_tenure_months, active_rule),
        _check_style_drift(consistency_result),
        _check_excessive_fee(fee_schedule, peer_fee_median, active_rule),
        _check_tracking_error(
            fund_type,
            tracking_error or _missing_tracking_error_for_risk(fund_type),
            active_rule,
        ),
    )
    veto_items = tuple(item for item in items if item.status == "veto")
    watch_items = tuple(item for item in items if item.status in {"watch", "insufficient_data"})
    overall_status = _overall_status(veto_items, watch_items)
    return RiskCheckResult(
        overall_status=overall_status,
        items=items,
        veto_items=veto_items,
        watch_items=watch_items,
        next_minimum_verification=_next_minimum_verification(veto_items, watch_items),
    )


def resolve_tracking_error_for_risk(
    *,
    tracking_error_field: ExtractedField[TrackingErrorValue],
    developer_override: Decimal | str | int | float | None,
    developer_override_enabled: bool,
    fund_type: FundType,
) -> ResolvedTrackingErrorForRisk:
    """解析风险检查的唯一跟踪误差输入，见模板第 6 章否决项。

    Args:
        tracking_error_field: Fund Capability 结构化跟踪误差字段。
        developer_override: 开发模式显式覆盖值。
        developer_override_enabled: 是否允许开发覆盖参与风险检查。
        fund_type: 标准化基金类型。

    Returns:
        风险检查消费的解析对象。

    Raises:
        ValueError: 当开发覆盖格式非法时抛出。
    """

    if fund_type not in _INDEX_FUND_TYPES:
        return _not_applicable_tracking_error_for_risk()
    if (
        tracking_error_field.extraction_mode in {"direct", "derived"}
        and tracking_error_field.value is not None
    ):
        value = tracking_error_field.value
        conflict_note = None
        if developer_override_enabled and developer_override is not None:
            conflict_note = "结构化跟踪误差优先于开发覆盖；开发覆盖未作为产品证据。"
        return ResolvedTrackingErrorForRisk(
            value=value.value,
            value_text=value.value_text,
            source_type=value.source_type,
            authority="capability_structured_data",
            field_extraction_mode=tracking_error_field.extraction_mode,  # type: ignore[arg-type]
            anchors=tracking_error_field.anchors,
            provenance_note=value.provenance_note,
            missing_reason=None,
            conflict_note=conflict_note,
            is_product_evidence=True,
        )
    if developer_override_enabled and developer_override is not None:
        parsed_override = parse_ratio(developer_override, field_name="tracking_error")
        return ResolvedTrackingErrorForRisk(
            value=parsed_override,
            value_text=str(developer_override),
            source_type="developer_override",
            authority="developer_override",
            field_extraction_mode="missing",
            anchors=(),
            provenance_note="开发覆盖仅用于本地风险检查夹具，不是产品证据。",
            missing_reason=None,
            conflict_note=None,
            is_product_evidence=False,
        )
    return ResolvedTrackingErrorForRisk(
        value=None,
        value_text=None,
        source_type="missing",
        authority="missing",
        field_extraction_mode="missing",
        anchors=(),
        provenance_note="未取得结构化跟踪误差。",
        missing_reason=tracking_error_field.note or "缺少指数基金跟踪误差",
        conflict_note=None,
        is_product_evidence=False,
    )


def run_stress_test(
    *,
    fund_type: FundType,
    investment_amount: Decimal | str | int | float,
    max_tolerable_loss_rate: Decimal | str | int | float | None = None,
    anchors: tuple[EvidenceAnchor, ...] = (),
    rule: StressTestRule | None = None,
) -> StressTestResult:
    """执行 -20% / -40% / -60% 压力测试，见模板第 6 章。

    Args:
        fund_type: 标准化基金类型，用于选择 preferred_lens 压力阈值。
        investment_amount: 投入金额，必须由调用方显式提供。
        max_tolerable_loss_rate: 最大可承受亏损比例；缺失时只输出浮亏，不判断承受能力。
        anchors: 投入金额或风险承受能力的证据锚点。
        rule: 压力测试规则配置。

    Returns:
        压力测试汇总结果。

    Raises:
        ValueError: 当投入金额、可承受亏损比例或规则配置非法时抛出。
    """

    active_rule = rule or StressTestRule()
    thresholds = _stress_thresholds(fund_type, active_rule)
    parsed_amount = _parse_positive_amount(investment_amount, field_name="investment_amount")
    parsed_tolerance = _parse_optional_loss_rate(max_tolerable_loss_rate)
    scenario_results = tuple(
        _stress_scenario_result(
            scenario_code=scenario_code,
            decline_rate=decline_rate,
            investment_amount=parsed_amount,
            thresholds=thresholds,
            max_tolerable_loss_rate=parsed_tolerance,
        )
        for scenario_code, decline_rate in active_rule.scenarios
    )
    if not scenario_results:
        raise ValueError("压力测试场景不能为空")
    worst_scenario = max(scenario_results, key=lambda item: item.floating_loss_amount)
    return StressTestResult(
        fund_type=fund_type,
        investment_amount=parsed_amount,
        max_tolerable_loss_rate=parsed_tolerance,
        scenarios=scenario_results,
        worst_scenario=worst_scenario,
        anchors=anchors,
        next_minimum_verification=_stress_next_minimum_verification(worst_scenario),
    )


def _check_liquidation_risk(
    basic_identity: ExtractedField[dict[str, object]],
    rule: RiskCheckRule,
) -> RiskCheckItem:
    """检查清盘风险。

    Args:
        basic_identity: 基础身份字段。
        rule: 规则配置。

    Returns:
        清盘风险检查结果。

    Raises:
        无显式抛出。
    """

    scale_text = _field_value(basic_identity, "fund_scale")
    threshold = f">{rule.liquidation_threshold_yuan} 元"
    if scale_text is None:
        return _risk_item(
            code="liquidation_risk",
            status="insufficient_data",
            current_value=None,
            threshold=threshold,
            anchors=basic_identity.anchors,
            reason="缺少基金规模，不能判断清盘风险。",
        )
    scale_yuan = _parse_scale_to_yuan(scale_text)
    if scale_yuan is None:
        return _risk_item(
            code="liquidation_risk",
            status="insufficient_data",
            current_value=scale_text,
            threshold=threshold,
            anchors=basic_identity.anchors,
            reason="基金规模格式无法规则化解析，不能判断清盘风险。",
        )
    if scale_yuan < rule.liquidation_threshold_yuan:
        return _risk_item(
            code="liquidation_risk",
            status="veto",
            current_value=str(scale_yuan),
            threshold=threshold,
            anchors=basic_identity.anchors,
            reason="基金规模低于 5000 万元清盘风险阈值。",
        )
    return _risk_item(
        code="liquidation_risk",
        status="pass",
        current_value=str(scale_yuan),
        threshold=threshold,
        anchors=basic_identity.anchors,
        reason="基金规模高于清盘风险阈值。",
    )


def _check_manager_tenure(
    manager_tenure_months: int | None,
    rule: RiskCheckRule,
) -> RiskCheckItem:
    """检查基金经理管理本基金时间。

    Args:
        manager_tenure_months: 基金经理管理本基金月数。
        rule: 规则配置。

    Returns:
        基金经理任期检查结果。

    Raises:
        无显式抛出。
    """

    threshold = f">= {rule.manager_tenure_months_threshold} 个月"
    if manager_tenure_months is None:
        return _risk_item(
            code="manager_tenure",
            status="insufficient_data",
            current_value=None,
            threshold=threshold,
            anchors=(),
            reason="缺少基金经理管理本基金月数，不能判断基金经理离职/新任风险。",
        )
    if manager_tenure_months < rule.manager_tenure_months_threshold:
        return _risk_item(
            code="manager_tenure",
            status="veto",
            current_value=f"{manager_tenure_months} 个月",
            threshold=threshold,
            anchors=(),
            reason="基金经理管理本基金时间少于 6 个月。",
        )
    return _risk_item(
        code="manager_tenure",
        status="pass",
        current_value=f"{manager_tenure_months} 个月",
        threshold=threshold,
        anchors=(),
        reason="基金经理管理本基金时间达到最低要求。",
    )


def _check_style_drift(consistency_result: ConsistencyCheckResult | None) -> RiskCheckItem:
    """检查严重风格漂移。

    Args:
        consistency_result: 言行一致性结果。

    Returns:
        风格漂移检查结果。

    Raises:
        无显式抛出。
    """

    if consistency_result is None:
        return _risk_item(
            code="style_drift",
            status="insufficient_data",
            current_value=None,
            threshold="言行一致性不能为红灯",
            anchors=(),
            reason="缺少言行一致性检验结果，不能判断严重风格漂移。",
        )
    anchors = _dimension_anchors(consistency_result)
    if consistency_result.overall_signal == "red":
        return _risk_item(
            code="style_drift",
            status="veto",
            current_value=consistency_result.overall_signal,
            threshold="言行一致性不能为红灯",
            anchors=anchors,
            reason="言行一致性检验为红灯，触发严重风格漂移否决项。",
        )
    if consistency_result.overall_signal in {"yellow", "gray"}:
        return _risk_item(
            code="style_drift",
            status="watch",
            current_value=consistency_result.overall_signal,
            threshold="言行一致性不能为红灯",
            anchors=anchors,
            reason="言行一致性未触发红灯，但仍需跟踪或补证。",
        )
    return _risk_item(
        code="style_drift",
        status="pass",
        current_value=consistency_result.overall_signal,
        threshold="言行一致性不能为红灯",
        anchors=anchors,
        reason="言行一致性未触发严重风格漂移。",
    )


def _check_excessive_fee(
    fee_schedule: ExtractedField[dict[str, object]],
    peer_fee_median: Decimal | str | int | float | None,
    rule: RiskCheckRule,
) -> RiskCheckItem:
    """检查费率是否远超同类。

    Args:
        fee_schedule: P1 费率字段。
        peer_fee_median: 同类总费率中位数。
        rule: 规则配置。

    Returns:
        费率检查结果。

    Raises:
        ValueError: 当显式同类中位数格式非法时抛出。
    """

    threshold = f"<= 同类中位数 × {rule.fee_multiple_threshold}"
    missing_reasons = _fee_missing_reasons(fee_schedule, peer_fee_median)
    if missing_reasons:
        return _risk_item(
            code="excessive_fee",
            status="insufficient_data",
            current_value=None,
            threshold=threshold,
            anchors=fee_schedule.anchors,
            reason="；".join(missing_reasons),
        )
    assert fee_schedule.value is not None
    assert peer_fee_median is not None
    total_fee = parse_ratio(fee_schedule.value["management_fee"], field_name="management_fee") + parse_ratio(
        fee_schedule.value["custody_fee"],
        field_name="custody_fee",
    )
    median_fee = parse_ratio(peer_fee_median, field_name="peer_fee_median")
    if total_fee > median_fee * rule.fee_multiple_threshold:
        return _risk_item(
            code="excessive_fee",
            status="veto",
            current_value=str(total_fee),
            threshold=threshold,
            anchors=fee_schedule.anchors,
            reason="总费率超过同类中位数 2 倍。",
        )
    return _risk_item(
        code="excessive_fee",
        status="pass",
        current_value=str(total_fee),
        threshold=threshold,
        anchors=fee_schedule.anchors,
        reason="总费率未超过同类中位数 2 倍。",
    )


def _check_tracking_error(
    fund_type: FundType,
    tracking_error: ResolvedTrackingErrorForRisk,
    rule: RiskCheckRule,
) -> RiskCheckItem:
    """检查指数基金跟踪误差。

    Args:
        fund_type: 基金类型。
        tracking_error: 已解析的跟踪误差风险输入。
        rule: 规则配置。

    Returns:
        跟踪误差检查结果。

    Raises:
        无显式抛出。
    """

    threshold = f"<= {rule.tracking_error_threshold}"
    if tracking_error.source_type == "not_applicable" or fund_type not in _INDEX_FUND_TYPES:
        return _risk_item(
            code="tracking_error",
            status="pass",
            current_value=None,
            threshold=threshold,
            anchors=tracking_error.anchors,
            reason="非指数基金不适用跟踪误差否决项。",
        )
    if tracking_error.value is None:
        return _risk_item(
            code="tracking_error",
            status="insufficient_data",
            current_value=None,
            threshold=threshold,
            anchors=tracking_error.anchors,
            reason=tracking_error.missing_reason or "缺少指数基金跟踪误差，不能判断跟踪误差否决项。",
        )
    parsed_tracking_error = tracking_error.value
    if parsed_tracking_error > rule.tracking_error_threshold:
        return _risk_item(
            code="tracking_error",
            status="veto",
            current_value=str(parsed_tracking_error),
            threshold=threshold,
            anchors=tracking_error.anchors,
            reason="指数基金跟踪误差超过 2%。",
        )
    return _risk_item(
        code="tracking_error",
        status="pass",
        current_value=str(parsed_tracking_error),
        threshold=threshold,
        anchors=tracking_error.anchors,
        reason="指数基金跟踪误差未超过阈值。",
    )


def _missing_tracking_error_for_risk(fund_type: FundType) -> ResolvedTrackingErrorForRisk:
    """构造调用方未传入解析对象时的保守默认值。

    Args:
        fund_type: 标准化基金类型。

    Returns:
        非指数基金返回不适用；指数基金返回缺失。

    Raises:
        无显式抛出。
    """

    if fund_type not in _INDEX_FUND_TYPES:
        return _not_applicable_tracking_error_for_risk()
    return ResolvedTrackingErrorForRisk(
        value=None,
        value_text=None,
        source_type="missing",
        authority="missing",
        field_extraction_mode="missing",
        anchors=(),
        provenance_note="调用方未提供跟踪误差解析对象。",
        missing_reason="缺少指数基金跟踪误差，不能判断跟踪误差否决项。",
        conflict_note=None,
        is_product_evidence=False,
    )


def _not_applicable_tracking_error_for_risk() -> ResolvedTrackingErrorForRisk:
    """构造非指数基金跟踪误差不适用对象。

    Args:
        无。

    Returns:
        跟踪误差不适用解析对象。

    Raises:
        无显式抛出。
    """

    return ResolvedTrackingErrorForRisk(
        value=None,
        value_text=None,
        source_type="not_applicable",
        authority="not_applicable",
        field_extraction_mode="not_applicable",
        anchors=(),
        provenance_note="非指数基金不适用跟踪误差否决项。",
        missing_reason=None,
        conflict_note=None,
        is_product_evidence=False,
    )


def _fee_missing_reasons(
    fee_schedule: ExtractedField[dict[str, object]],
    peer_fee_median: Decimal | str | int | float | None,
) -> list[str]:
    """检查费率判断缺失输入。

    Args:
        fee_schedule: 费率字段。
        peer_fee_median: 同类费率中位数。

    Returns:
        缺失原因列表。

    Raises:
        无显式抛出。
    """

    reasons: list[str] = []
    if fee_schedule.value is None or not fee_schedule.value.get("management_fee"):
        reasons.append("缺少管理费")
    if fee_schedule.value is None or not fee_schedule.value.get("custody_fee"):
        reasons.append("缺少托管费")
    if peer_fee_median is None:
        reasons.append("缺少同类总费率中位数")
    return reasons


def _field_value(field: ExtractedField[dict[str, object]], key: str) -> str | None:
    """读取抽取字段中的字符串子值。

    Args:
        field: 抽取字段。
        key: 子字段名。

    Returns:
        子值文本；缺失时返回 `None`。

    Raises:
        无显式抛出。
    """

    if field.value is None or not field.value.get(key):
        return None
    return str(field.value[key])


def _parse_scale_to_yuan(value: str) -> Decimal | None:
    """解析基金规模为人民币元。

    Args:
        value: 基金规模文本。

    Returns:
        规模对应的元；无法解析时返回 `None`。

    Raises:
        无显式抛出。
    """

    match = _NUMBER_PATTERN.search(value.replace(",", ""))
    if match is None:
        return None
    try:
        number = Decimal(match.group(0))
    except InvalidOperation:
        return None
    if "亿元" in value or "亿" in value:
        return number * Decimal("100000000")
    if "万元" in value or "万" in value:
        return number * Decimal("10000")
    return number


def _dimension_anchors(consistency_result: ConsistencyCheckResult) -> tuple[EvidenceAnchor, ...]:
    """合并言行一致性维度证据锚点。

    Args:
        consistency_result: 言行一致性结果。

    Returns:
        去重后的证据锚点。

    Raises:
        无显式抛出。
    """

    anchors: list[EvidenceAnchor] = []
    seen: set[EvidenceAnchor] = set()
    for dimension in consistency_result.dimensions:
        for anchor in dimension.anchors:
            if anchor in seen:
                continue
            anchors.append(anchor)
            seen.add(anchor)
    return tuple(anchors)


def _overall_status(
    veto_items: tuple[RiskCheckItem, ...],
    watch_items: tuple[RiskCheckItem, ...],
) -> RiskCheckStatus:
    """生成否决项汇总状态。

    Args:
        veto_items: 一票否决项。
        watch_items: 跟踪或证据不足项。

    Returns:
        汇总状态。

    Raises:
        无显式抛出。
    """

    if veto_items:
        return "veto"
    if watch_items:
        return "watch"
    return "pass"


def _next_minimum_verification(
    veto_items: tuple[RiskCheckItem, ...],
    watch_items: tuple[RiskCheckItem, ...],
) -> str:
    """生成下一步最小验证问题。

    Args:
        veto_items: 一票否决项。
        watch_items: 跟踪或证据不足项。

    Returns:
        下一步最小验证问题。

    Raises:
        无显式抛出。
    """

    if veto_items:
        return f"先复核否决项 `{veto_items[0].code}` 的原始证据是否准确。"
    if watch_items:
        return f"先补齐或复核 `{watch_items[0].code}` 的关键输入。"
    return "当前无一票否决项，下一步进入压力测试。"


def _risk_item(
    *,
    code: RiskCheckCode,
    status: RiskCheckStatus,
    current_value: str | None,
    threshold: str,
    anchors: tuple[EvidenceAnchor, ...],
    reason: str,
) -> RiskCheckItem:
    """构造单个否决项结果。

    Args:
        code: 检查项编码。
        status: 检查状态。
        current_value: 当前值。
        threshold: 阈值。
        anchors: 证据锚点。
        reason: 判断依据。

    Returns:
        否决项结果。

    Raises:
        无显式抛出。
    """

    return RiskCheckItem(
        code=code,
        status=status,
        current_value=current_value,
        threshold=threshold,
        anchors=anchors,
        reason=reason,
    )


def _stress_thresholds(
    fund_type: FundType,
    rule: StressTestRule,
) -> tuple[Decimal, Decimal, Decimal]:
    """读取基金类型对应的压力测试阈值。

    Args:
        fund_type: 标准化基金类型。
        rule: 压力测试规则配置。

    Returns:
        正常、极端、历史最差三个阈值，均为正数小数比例。

    Raises:
        ValueError: 当基金类型没有阈值配置，或阈值配置非法时抛出。
    """

    threshold_map = rule.severity_thresholds or _DEFAULT_STRESS_THRESHOLDS
    if fund_type not in threshold_map:
        raise ValueError(f"缺少基金类型压力测试阈值：{fund_type}")
    thresholds = threshold_map[fund_type]
    if len(thresholds) != 3:
        raise ValueError(f"基金类型压力测试阈值必须包含 3 档：{fund_type}")
    normal, extreme, historical_worst = tuple(Decimal(str(threshold)) for threshold in thresholds)
    if not (Decimal("0") < normal <= extreme <= historical_worst):
        raise ValueError(f"基金类型压力测试阈值顺序非法：{fund_type}")
    return normal, extreme, historical_worst


def _parse_positive_amount(value: Decimal | str | int | float, *, field_name: str) -> Decimal:
    """解析正数金额。

    Args:
        value: 原始金额。
        field_name: 字段名，用于错误信息。

    Returns:
        Decimal 金额。

    Raises:
        ValueError: 当金额为空、无法解析或非正数时抛出。
    """

    amount = _parse_decimal(value, field_name=field_name)
    if amount <= Decimal("0"):
        raise ValueError(f"{field_name} 必须大于 0")
    return amount


def _parse_optional_loss_rate(value: Decimal | str | int | float | None) -> Decimal | None:
    """解析可选最大可承受亏损比例。

    Args:
        value: 原始亏损比例。

    Returns:
        小数比例；缺失时返回 `None`。

    Raises:
        ValueError: 当比例不在 0 到 100% 之间时抛出。
    """

    if value is None:
        return None
    parsed = parse_ratio(value, field_name="max_tolerable_loss_rate")
    if parsed < Decimal("0") or parsed > Decimal("1"):
        raise ValueError("max_tolerable_loss_rate 必须在 0 到 100% 之间")
    return parsed


def _parse_decimal(value: Decimal | str | int | float, *, field_name: str) -> Decimal:
    """解析普通 Decimal 数值。

    Args:
        value: 原始数值。
        field_name: 字段名，用于错误信息。

    Returns:
        Decimal 数值。

    Raises:
        ValueError: 当输入为空或无法解析为数值时抛出。
    """

    if isinstance(value, bool):
        raise ValueError(f"{field_name} 不能为布尔值")
    if isinstance(value, Decimal):
        return value
    if isinstance(value, int | float):
        return Decimal(str(value))
    text = str(value).strip().replace(",", "")
    if not text:
        raise ValueError(f"{field_name} 不能为空")
    try:
        return Decimal(text)
    except InvalidOperation as exc:
        raise ValueError(f"{field_name} 无法解析为数值：{value}") from exc


def _stress_scenario_result(
    *,
    scenario_code: StressScenarioCode,
    decline_rate: Decimal,
    investment_amount: Decimal,
    thresholds: tuple[Decimal, Decimal, Decimal],
    max_tolerable_loss_rate: Decimal | None,
) -> StressScenarioResult:
    """生成单个压力测试场景结果。

    Args:
        scenario_code: 场景编码。
        decline_rate: 场景跌幅，小数比例，应为负数。
        investment_amount: 投入金额。
        thresholds: 基金类型压力阈值。
        max_tolerable_loss_rate: 最大可承受亏损比例。

    Returns:
        单个压力测试场景结果。

    Raises:
        ValueError: 当场景跌幅不是负数时抛出。
    """

    if decline_rate >= Decimal("0"):
        raise ValueError(f"压力测试跌幅必须为负数：{scenario_code}")
    loss_rate = abs(decline_rate)
    floating_loss_amount = investment_amount * loss_rate
    account_balance = investment_amount - floating_loss_amount
    severity = _stress_severity(loss_rate, thresholds)
    capacity_status = _stress_capacity_status(loss_rate, max_tolerable_loss_rate)
    return StressScenarioResult(
        code=scenario_code,
        decline_rate=decline_rate,
        investment_amount=investment_amount,
        account_balance=account_balance,
        floating_loss_amount=floating_loss_amount,
        severity=severity,
        capacity_status=capacity_status,
        threshold=_format_stress_threshold(thresholds),
        reason=_stress_reason(loss_rate, severity, capacity_status, max_tolerable_loss_rate),
    )


def _stress_severity(
    loss_rate: Decimal,
    thresholds: tuple[Decimal, Decimal, Decimal],
) -> StressSeverity:
    """按基金类型阈值划分压力等级。

    Args:
        loss_rate: 亏损比例，正数。
        thresholds: 正常、极端、历史最差三个阈值。

    Returns:
        压力等级。

    Raises:
        无显式抛出。
    """

    normal, extreme, historical_worst = thresholds
    if loss_rate <= normal:
        return "normal"
    if loss_rate <= extreme:
        return "extreme"
    if loss_rate <= historical_worst:
        return "historical_worst"
    return "beyond_historical"


def _stress_capacity_status(
    loss_rate: Decimal,
    max_tolerable_loss_rate: Decimal | None,
) -> StressCapacityStatus:
    """判断压力场景是否超过显式承受能力。

    Args:
        loss_rate: 亏损比例，正数。
        max_tolerable_loss_rate: 最大可承受亏损比例。

    Returns:
        承受能力状态。

    Raises:
        无显式抛出。
    """

    if max_tolerable_loss_rate is None:
        return "not_provided"
    if loss_rate > max_tolerable_loss_rate:
        return "beyond_tolerance"
    if loss_rate >= max_tolerable_loss_rate * _NEAR_TOLERANCE_BUFFER:
        return "near_limit"
    return "within_tolerance"


def _format_stress_threshold(thresholds: tuple[Decimal, Decimal, Decimal]) -> str:
    """格式化压力测试阈值说明。

    Args:
        thresholds: 正常、极端、历史最差三个阈值。

    Returns:
        阈值说明文本。

    Raises:
        无显式抛出。
    """

    normal, extreme, historical_worst = thresholds
    return f"正常≤{normal}；极端≤{extreme}；历史最差≤{historical_worst}"


def _stress_reason(
    loss_rate: Decimal,
    severity: StressSeverity,
    capacity_status: StressCapacityStatus,
    max_tolerable_loss_rate: Decimal | None,
) -> str:
    """生成压力测试判断依据。

    Args:
        loss_rate: 亏损比例，正数。
        severity: 压力等级。
        capacity_status: 承受能力状态。
        max_tolerable_loss_rate: 最大可承受亏损比例。

    Returns:
        判断依据文本。

    Raises:
        无显式抛出。
    """

    if max_tolerable_loss_rate is None:
        return f"场景亏损比例为 {loss_rate}，压力等级为 {severity}；未提供最大可承受亏损比例。"
    return (
        f"场景亏损比例为 {loss_rate}，压力等级为 {severity}；"
        f"最大可承受亏损比例为 {max_tolerable_loss_rate}，承受状态为 {capacity_status}。"
    )


def _stress_next_minimum_verification(worst_scenario: StressScenarioResult) -> str:
    """生成压力测试下一步最小验证问题。

    Args:
        worst_scenario: 浮亏最大的压力场景。

    Returns:
        下一步最小验证问题。

    Raises:
        无显式抛出。
    """

    if worst_scenario.capacity_status == "beyond_tolerance":
        return f"先确认 `{worst_scenario.code}` 场景下的浮亏金额是否超出真实可承受范围。"
    if worst_scenario.capacity_status == "near_limit":
        return f"先复核 `{worst_scenario.code}` 场景是否已接近用户最大可承受亏损。"
    if worst_scenario.capacity_status == "not_provided":
        return "先补充最大可承受亏损比例，再判断压力场景能否承受。"
    return "当前压力场景未超过显式承受能力，下一步进入检查清单。"
