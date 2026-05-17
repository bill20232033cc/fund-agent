"""投资者获得感分析模块。

本模块属于基金 Capability 层，服务模板第 4 章“投资者获得感”。
它只消费 P1 结构化字段，不直接读取年报文件。
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import Literal

from fund_agent.fund.analysis._ratios import parse_ratio
from fund_agent.fund.extractors.models import EvidenceAnchor, ExtractedField

InvestorExperienceStatus = Literal["positive", "neutral", "negative", "insufficient_data"]
BehaviorGapStatus = Literal["computed", "missing"]
FundFlowSignal = Literal["chasing_performance", "bottom_fishing", "outflow", "normal", "missing"]


@dataclass(frozen=True, slots=True)
class BehaviorGapResult:
    """行为损益计算结果。

    Attributes:
        status: 计算状态。
        product_return: 基金产品收益，小数比例。
        investor_return: 投资者实际收益，小数比例。
        behavior_gap: 行为损益，投资者实际收益减基金产品收益。
        anchors: 参与计算字段的证据锚点。
        note: 缺失或口径说明。
    """

    status: BehaviorGapStatus
    product_return: Decimal | None
    investor_return: Decimal | None
    behavior_gap: Decimal | None
    anchors: tuple[EvidenceAnchor, ...]
    note: str | None = None


@dataclass(frozen=True, slots=True)
class FundFlowResult:
    """份额变动与资金流向判断结果。

    Attributes:
        signal: 资金流向信号。
        beginning_share: 期初份额。
        ending_share: 期末份额。
        net_change: 净变动份额。
        net_change_ratio: 净变动占期初份额比例。
        anchors: 参与判断字段的证据锚点。
        reason: 判断依据。
    """

    signal: FundFlowSignal
    beginning_share: Decimal | None
    ending_share: Decimal | None
    net_change: Decimal | None
    net_change_ratio: Decimal | None
    anchors: tuple[EvidenceAnchor, ...]
    reason: str


@dataclass(frozen=True, slots=True)
class InvestorExperienceResult:
    """投资者获得感分析结果。

    Attributes:
        status: 获得感状态。
        behavior_gap: 行为损益结果。
        fund_flow: 资金流向结果。
        reasons: 汇总判断依据。
    """

    status: InvestorExperienceStatus
    behavior_gap: BehaviorGapResult
    fund_flow: FundFlowResult
    reasons: tuple[str, ...]


def analyze_investor_experience(
    *,
    nav_benchmark_performance: ExtractedField[dict[str, object]],
    investor_return: ExtractedField[dict[str, object]],
    share_change: ExtractedField[dict[str, object]],
) -> InvestorExperienceResult:
    """分析投资者获得感，见模板第 4 章。

    Args:
        nav_benchmark_performance: P1 从 §3 抽取的基金净值增长率与基准收益率。
        investor_return: P1 从 §3 抽取的投资者收益率三态字段。
        share_change: P1 从 §10 抽取的份额变动字段。

    Returns:
        投资者获得感分析结果。

    Raises:
        ValueError: 当已披露字段格式非法时抛出。
    """

    behavior_gap = calculate_behavior_gap(
        nav_benchmark_performance=nav_benchmark_performance,
        investor_return=investor_return,
    )
    fund_flow = judge_fund_flow(
        share_change=share_change,
        product_return=behavior_gap.product_return,
    )
    status = _experience_status(behavior_gap)
    return InvestorExperienceResult(
        status=status,
        behavior_gap=behavior_gap,
        fund_flow=fund_flow,
        reasons=_experience_reasons(status, behavior_gap, fund_flow),
    )


def calculate_behavior_gap(
    *,
    nav_benchmark_performance: ExtractedField[dict[str, object]],
    investor_return: ExtractedField[dict[str, object]],
) -> BehaviorGapResult:
    """计算行为损益，见模板第 4 章。

    Args:
        nav_benchmark_performance: 基金产品收益字段。
        investor_return: 投资者实际收益字段。

    Returns:
        行为损益结果；关键输入缺失时返回 `missing`。

    Raises:
        ValueError: 当已披露收益率格式非法时抛出。
    """

    anchors = _merge_anchors(nav_benchmark_performance, investor_return)
    missing_reasons = _behavior_gap_missing_reasons(nav_benchmark_performance, investor_return)
    if missing_reasons:
        return BehaviorGapResult(
            status="missing",
            product_return=None,
            investor_return=None,
            behavior_gap=None,
            anchors=anchors,
            note="；".join(missing_reasons),
        )

    assert nav_benchmark_performance.value is not None
    assert investor_return.value is not None
    product_return = parse_ratio(
        nav_benchmark_performance.value["nav_growth_rate"],
        field_name="nav_growth_rate",
    )
    actual_investor_return = parse_ratio(
        investor_return.value["investor_return_rate"],
        field_name="investor_return_rate",
    )
    return BehaviorGapResult(
        status="computed",
        product_return=product_return,
        investor_return=actual_investor_return,
        behavior_gap=actual_investor_return - product_return,
        anchors=anchors,
        note="行为损益 = 投资者实际收益 - 基金产品收益。",
    )


def judge_fund_flow(
    *,
    share_change: ExtractedField[dict[str, object]],
    product_return: Decimal | None,
) -> FundFlowResult:
    """基于份额变动和产品收益方向判断资金流向，见模板第 4 章。

    Args:
        share_change: P1 从 §10 抽取的份额变动字段。
        product_return: 基金产品收益；缺失时只输出份额净流入/流出。

    Returns:
        资金流向判断结果。

    Raises:
        ValueError: 当份额字段格式非法时抛出。
    """

    if share_change.value is None:
        return FundFlowResult(
            signal="missing",
            beginning_share=None,
            ending_share=None,
            net_change=None,
            net_change_ratio=None,
            anchors=share_change.anchors,
            reason="缺少 §10 份额变动，不能判断资金流向。",
        )

    missing_fields = _share_change_missing_fields(share_change)
    if missing_fields:
        return FundFlowResult(
            signal="missing",
            beginning_share=None,
            ending_share=None,
            net_change=None,
            net_change_ratio=None,
            anchors=share_change.anchors,
            reason=f"§10 份额变动字段缺失：{'、'.join(missing_fields)}。",
        )

    beginning_share = _parse_decimal(share_change.value["beginning_share"], field_name="beginning_share")
    ending_share = _parse_decimal(share_change.value["ending_share"], field_name="ending_share")
    net_change = _parse_decimal(share_change.value["net_change"], field_name="net_change")
    net_change_ratio = net_change / beginning_share if beginning_share != Decimal("0") else None
    signal = _fund_flow_signal(net_change=net_change, product_return=product_return)
    return FundFlowResult(
        signal=signal,
        beginning_share=beginning_share,
        ending_share=ending_share,
        net_change=net_change,
        net_change_ratio=net_change_ratio,
        anchors=share_change.anchors,
        reason=_fund_flow_reason(signal),
    )


def _behavior_gap_missing_reasons(
    nav_benchmark_performance: ExtractedField[dict[str, object]],
    investor_return: ExtractedField[dict[str, object]],
) -> list[str]:
    """检查行为损益计算缺失输入。

    Args:
        nav_benchmark_performance: 产品收益字段。
        investor_return: 投资者收益字段。

    Returns:
        缺失原因列表。

    Raises:
        无显式抛出。
    """

    reasons: list[str] = []
    if nav_benchmark_performance.value is None or not nav_benchmark_performance.value.get("nav_growth_rate"):
        reasons.append("缺少 §3 基金净值增长率")
    if investor_return.value is None or not investor_return.value.get("investor_return_rate"):
        reasons.append("缺少 §3 投资者实际收益率")
    return reasons


def _share_change_missing_fields(share_change: ExtractedField[dict[str, object]]) -> tuple[str, ...]:
    """检查份额变动缺失子字段。

    Args:
        share_change: 份额变动字段。

    Returns:
        缺失字段名元组。

    Raises:
        无显式抛出。
    """

    if share_change.value is None:
        return ("beginning_share", "ending_share", "net_change")
    required_fields = ("beginning_share", "ending_share", "net_change")
    return tuple(field_name for field_name in required_fields if not share_change.value.get(field_name))


def _experience_status(behavior_gap: BehaviorGapResult) -> InvestorExperienceStatus:
    """根据行为损益判断获得感状态。

    Args:
        behavior_gap: 行为损益结果。

    Returns:
        获得感状态。

    Raises:
        无显式抛出。
    """

    if behavior_gap.status == "missing" or behavior_gap.behavior_gap is None:
        return "insufficient_data"
    if behavior_gap.investor_return is not None and behavior_gap.investor_return < Decimal("0"):
        return "negative"
    if behavior_gap.behavior_gap < Decimal("-0.02"):
        return "negative"
    if behavior_gap.behavior_gap < Decimal("0"):
        return "neutral"
    return "positive"


def _experience_reasons(
    status: InvestorExperienceStatus,
    behavior_gap: BehaviorGapResult,
    fund_flow: FundFlowResult,
) -> tuple[str, ...]:
    """生成投资者获得感汇总依据。

    Args:
        status: 获得感状态。
        behavior_gap: 行为损益结果。
        fund_flow: 资金流向结果。

    Returns:
        汇总依据元组。

    Raises:
        无显式抛出。
    """

    reasons: list[str] = [f"投资者获得感状态：{status}。"]
    if behavior_gap.behavior_gap is not None:
        reasons.append(f"行为损益为 {behavior_gap.behavior_gap}。")
    else:
        reasons.append(behavior_gap.note or "行为损益缺少输入。")
    reasons.append(fund_flow.reason)
    return tuple(reasons)


def _fund_flow_signal(
    *,
    net_change: Decimal,
    product_return: Decimal | None,
) -> FundFlowSignal:
    """判断资金流向信号。

    Args:
        net_change: 份额净变动。
        product_return: 产品收益。

    Returns:
        资金流向信号。

    Raises:
        无显式抛出。
    """

    if net_change == Decimal("0"):
        return "normal"
    if product_return is None:
        return "normal" if net_change > Decimal("0") else "outflow"
    if net_change > Decimal("0") and product_return > Decimal("0"):
        return "chasing_performance"
    if net_change > Decimal("0") and product_return <= Decimal("0"):
        return "bottom_fishing"
    return "outflow"


def _fund_flow_reason(signal: FundFlowSignal) -> str:
    """生成资金流向判断依据。

    Args:
        signal: 资金流向信号。

    Returns:
        判断依据。

    Raises:
        无显式抛出。
    """

    reasons: dict[FundFlowSignal, str] = {
        "chasing_performance": "产品收益为正且份额净流入，存在追涨信号。",
        "bottom_fishing": "产品收益不佳但份额净流入，存在抄底信号。",
        "outflow": "份额净流出，投资者在报告期内整体撤离。",
        "normal": "份额变动未显示明显追涨或抄底信号。",
        "missing": "缺少份额变动数据，不能判断资金流向。",
    }
    return reasons[signal]


def _parse_decimal(value: object, *, field_name: str) -> Decimal:
    """解析份额数值。

    Args:
        value: 原始份额值。
        field_name: 字段名。

    Returns:
        Decimal 数值。

    Raises:
        ValueError: 当值为空或无法解析时抛出。
    """

    if value is None:
        raise ValueError(f"{field_name} 不能为空")
    text = str(value).replace(",", "").strip()
    if not text:
        raise ValueError(f"{field_name} 不能为空")
    try:
        return Decimal(text)
    except InvalidOperation as exc:
        raise ValueError(f"{field_name} 无法解析为数值：{value}") from exc


def _merge_anchors(*fields: ExtractedField[dict[str, object]]) -> tuple[EvidenceAnchor, ...]:
    """合并并去重证据锚点。

    Args:
        fields: 抽取字段。

    Returns:
        证据锚点元组。

    Raises:
        无显式抛出。
    """

    anchors: list[EvidenceAnchor] = []
    seen: set[EvidenceAnchor] = set()
    for field in fields:
        for anchor in field.anchors:
            if anchor in seen:
                continue
            anchors.append(anchor)
            seen.add(anchor)
    return tuple(anchors)
