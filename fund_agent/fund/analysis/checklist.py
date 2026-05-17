"""买入前检查清单模块。

本模块属于基金 Capability 层，服务 `docs/design.md` 第 4.6 节的 7 问题检查清单。
它只消费 P2 分析结果和调用方显式输入，不直接读取年报、缓存或外部数据。
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import Literal

from fund_agent.fund.analysis.consistency_check import ConsistencyCheckResult
from fund_agent.fund.analysis.investor_return import InvestorExperienceResult
from fund_agent.fund.analysis.r_abc import RabcAttribution
from fund_agent.fund.analysis.risk_check import RiskCheckResult
from fund_agent.fund.extractors.models import EvidenceAnchor, ExtractedField

ChecklistQuestionCode = Literal[
    "net_excess_covers_cost",
    "manager_alignment",
    "investor_return",
    "consistency",
    "survival",
    "valuation",
    "money_horizon",
]
ChecklistSignal = Literal["green", "yellow", "red", "gray"]
ChecklistStatus = Literal["pass", "watch", "block", "insufficient_data"]
ValuationState = Literal["low", "fair", "high", "unavailable"]
MoneyHorizon = Literal["long_enough", "uncertain", "too_short"]


@dataclass(frozen=True, slots=True)
class ChecklistRule:
    """检查清单规则配置。

    Attributes:
        minimum_horizon_years: 用户资金最短不用期限，见检查清单第 7 问。
        manager_alignment_positive_keywords: §9 持有披露的正向关键词。
        manager_alignment_negative_keywords: §9 持有披露的负向关键词。
    """

    minimum_horizon_years: Decimal = Decimal("3")
    manager_alignment_positive_keywords: tuple[str, ...] = ("持有", "自购", "从业人员持有")
    manager_alignment_negative_keywords: tuple[str, ...] = ("未持有", "0.00", "无")


@dataclass(frozen=True, slots=True)
class ChecklistItem:
    """单个检查清单问题结果。

    Attributes:
        code: 问题编码。
        question: 问题文本。
        signal: 红黄绿灰灯。
        status: 规则状态。
        anchors: 参与判断的证据锚点。
        reason: 判断依据。
    """

    code: ChecklistQuestionCode
    question: str
    signal: ChecklistSignal
    status: ChecklistStatus
    anchors: tuple[EvidenceAnchor, ...]
    reason: str


@dataclass(frozen=True, slots=True)
class ChecklistResult:
    """买入前检查清单结果。

    Attributes:
        items: 7 个问题结果。
        overall_signal: 汇总红黄绿灰灯。
        overall_status: 汇总状态。
        red_items: 红灯问题。
        yellow_items: 黄灯问题。
        gray_items: 灰灯问题。
        next_minimum_verification: 下一步最小验证问题。
    """

    items: tuple[ChecklistItem, ...]
    overall_signal: ChecklistSignal
    overall_status: ChecklistStatus
    red_items: tuple[ChecklistItem, ...]
    yellow_items: tuple[ChecklistItem, ...]
    gray_items: tuple[ChecklistItem, ...]
    next_minimum_verification: str


def run_checklist(
    *,
    rabc_attribution: RabcAttribution,
    manager_alignment: ExtractedField[dict[str, object]],
    investor_experience: InvestorExperienceResult,
    consistency_result: ConsistencyCheckResult,
    risk_check_result: RiskCheckResult,
    valuation_state: ValuationState = "unavailable",
    money_horizon: MoneyHorizon | None = None,
    user_money_horizon_years: Decimal | str | int | float | None = None,
    rule: ChecklistRule | None = None,
) -> ChecklistResult:
    """生成 7 问题买入前检查清单，见 `docs/design.md` 第 4.6 节。

    Args:
        rabc_attribution: P2-S1 R=A+B-C 归因结果。
        manager_alignment: P1 从 §9 抽取的基金经理/从业人员持有披露。
        investor_experience: P2-S4 投资者获得感结果。
        consistency_result: P2-S3 言行一致性结果。
        risk_check_result: P2-S5 否决项检查结果。
        valuation_state: 当前估值状态，由温度计或调用方显式提供。
        money_horizon: 用户资金期限分类，由调用方显式提供。
        user_money_horizon_years: 用户资金不用年限；提供时优先转换为资金期限分类。
        rule: 检查清单规则配置。

    Returns:
        7 问题检查清单结果。

    Raises:
        ValueError: 当用户资金年限格式非法时抛出。
    """

    active_rule = rule or ChecklistRule()
    resolved_horizon = _resolve_money_horizon(
        money_horizon=money_horizon,
        user_money_horizon_years=user_money_horizon_years,
        rule=active_rule,
    )
    items = (
        _check_net_excess_covers_cost(rabc_attribution),
        _check_manager_alignment(manager_alignment, active_rule),
        _check_investor_return(investor_experience),
        _check_consistency(consistency_result),
        _check_survival(risk_check_result),
        _check_valuation(valuation_state),
        _check_money_horizon(resolved_horizon),
    )
    return _build_checklist_result(items)


def _resolve_money_horizon(
    *,
    money_horizon: MoneyHorizon | None,
    user_money_horizon_years: Decimal | str | int | float | None,
    rule: ChecklistRule,
) -> MoneyHorizon | None:
    """解析用户资金期限分类。

    Args:
        money_horizon: 显式资金期限分类。
        user_money_horizon_years: 用户资金不用年限。
        rule: 检查清单规则配置。

    Returns:
        资金期限分类；缺失时返回 `None`。

    Raises:
        ValueError: 当用户资金年限格式非法时抛出。
    """

    if money_horizon is not None:
        return money_horizon
    if user_money_horizon_years is None:
        return None
    years = _parse_decimal(user_money_horizon_years, field_name="user_money_horizon_years")
    if years >= _active_minimum_horizon(rule):
        return "long_enough"
    if years >= _active_minimum_horizon(rule) - Decimal("1"):
        return "uncertain"
    return "too_short"


def _active_minimum_horizon(rule: ChecklistRule) -> Decimal:
    """读取最短资金期限阈值。

    Args:
        rule: 检查清单规则配置。

    Returns:
        最短资金期限年数。

    Raises:
        ValueError: 当阈值非正数时抛出。
    """

    if rule.minimum_horizon_years <= Decimal("0"):
        raise ValueError("minimum_horizon_years 必须大于 0")
    return rule.minimum_horizon_years


def _check_net_excess_covers_cost(rabc_attribution: RabcAttribution) -> ChecklistItem:
    """检查超额收益能否覆盖成本，见检查清单第 1 问。

    Args:
        rabc_attribution: R=A+B-C 归因结果。

    Returns:
        第 1 问检查结果。

    Raises:
        无显式抛出。
    """

    if rabc_attribution.status != "computed" or rabc_attribution.net_excess_return is None:
        return _item(
            code="net_excess_covers_cost",
            signal="gray",
            status="insufficient_data",
            anchors=rabc_attribution.anchors,
            reason="缺少完整 R=A+B-C 归因，不能判断超额收益是否覆盖成本。",
        )
    if rabc_attribution.net_excess_return > Decimal("0"):
        return _item(
            code="net_excess_covers_cost",
            signal="green",
            status="pass",
            anchors=rabc_attribution.anchors,
            reason="净超额收益为正，超额收益已覆盖成本。",
        )
    return _item(
        code="net_excess_covers_cost",
        signal="red",
        status="block",
        anchors=rabc_attribution.anchors,
        reason="净超额收益不为正，超额收益未覆盖成本。",
    )


def _check_manager_alignment(
    manager_alignment: ExtractedField[dict[str, object]],
    rule: ChecklistRule,
) -> ChecklistItem:
    """检查基金经理是否跟投资者利益一致，见检查清单第 2 问。

    Args:
        manager_alignment: §9 基金经理/从业人员持有披露。
        rule: 检查清单规则配置。

    Returns:
        第 2 问检查结果。

    Raises:
        无显式抛出。
    """

    disclosure = _alignment_disclosure(manager_alignment)
    if disclosure is None:
        return _item(
            code="manager_alignment",
            signal="gray",
            status="insufficient_data",
            anchors=manager_alignment.anchors,
            reason="缺少 §9 基金经理或从业人员持有披露，不能判断利益一致性。",
        )
    if _contains_any(disclosure, rule.manager_alignment_negative_keywords):
        return _item(
            code="manager_alignment",
            signal="yellow",
            status="watch",
            anchors=manager_alignment.anchors,
            reason="§9 持有披露出现未持有或零持有信号，需要关注利益一致性。",
        )
    if _contains_any(disclosure, rule.manager_alignment_positive_keywords):
        return _item(
            code="manager_alignment",
            signal="green",
            status="pass",
            anchors=manager_alignment.anchors,
            reason="§9 持有披露存在持有或自购信号。",
        )
    return _item(
        code="manager_alignment",
        signal="yellow",
        status="watch",
        anchors=manager_alignment.anchors,
        reason="§9 持有披露存在，但未形成明确正向信号。",
    )


def _check_investor_return(investor_experience: InvestorExperienceResult) -> ChecklistItem:
    """检查投资者是否真的赚到钱，见检查清单第 3 问。

    Args:
        investor_experience: 投资者获得感结果。

    Returns:
        第 3 问检查结果。

    Raises:
        无显式抛出。
    """

    anchors = investor_experience.behavior_gap.anchors
    if investor_experience.status == "positive":
        return _item(
            code="investor_return",
            signal="green",
            status="pass",
            anchors=anchors,
            reason="投资者获得感为正向。",
        )
    if investor_experience.status == "neutral":
        return _item(
            code="investor_return",
            signal="yellow",
            status="watch",
            anchors=anchors,
            reason="投资者获得感中性，需要结合资金流向继续观察。",
        )
    if investor_experience.status == "negative":
        return _item(
            code="investor_return",
            signal="red",
            status="block",
            anchors=anchors,
            reason="投资者获得感为负向。",
        )
    return _item(
        code="investor_return",
        signal="gray",
        status="insufficient_data",
        anchors=anchors,
        reason="缺少投资者实际收益率，不能判断投资者是否真的赚到钱。",
    )


def _check_consistency(consistency_result: ConsistencyCheckResult) -> ChecklistItem:
    """检查说的和做的是否一致，见检查清单第 4 问。

    Args:
        consistency_result: 言行一致性结果。

    Returns:
        第 4 问检查结果。

    Raises:
        无显式抛出。
    """

    anchors = _consistency_anchors(consistency_result)
    if consistency_result.overall_signal == "green":
        return _item(
            code="consistency",
            signal="green",
            status="pass",
            anchors=anchors,
            reason="言行一致性整体为绿灯。",
        )
    if consistency_result.overall_signal == "red":
        return _item(
            code="consistency",
            signal="red",
            status="block",
            anchors=anchors,
            reason="言行一致性整体为红灯。",
        )
    if consistency_result.overall_signal == "gray":
        return _item(
            code="consistency",
            signal="gray",
            status="insufficient_data",
            anchors=anchors,
            reason="言行一致性证据不足。",
        )
    return _item(
        code="consistency",
        signal="yellow",
        status="watch",
        anchors=anchors,
        reason="言行一致性整体为黄灯，需要继续跟踪。",
    )


def _check_survival(risk_check_result: RiskCheckResult) -> ChecklistItem:
    """检查基金安全性，见检查清单第 5 问。

    Args:
        risk_check_result: 否决项检查结果。

    Returns:
        第 5 问检查结果。

    Raises:
        无显式抛出。
    """

    anchors = _risk_anchors(risk_check_result)
    if risk_check_result.overall_status == "pass":
        return _item(
            code="survival",
            signal="green",
            status="pass",
            anchors=anchors,
            reason="否决项检查通过，当前未触发清盘等安全性否决项。",
        )
    if risk_check_result.overall_status == "veto":
        veto_code = risk_check_result.veto_items[0].code if risk_check_result.veto_items else "unknown"
        return _item(
            code="survival",
            signal="red",
            status="block",
            anchors=anchors,
            reason=f"否决项检查触发红灯：{veto_code}。",
        )
    return _item(
        code="survival",
        signal="yellow",
        status="watch",
        anchors=anchors,
        reason="否决项检查存在跟踪项或证据不足项。",
    )


def _check_valuation(valuation_state: ValuationState) -> ChecklistItem:
    """检查当前估值位置，见检查清单第 6 问。

    Args:
        valuation_state: 当前估值状态。

    Returns:
        第 6 问检查结果。

    Raises:
        无显式抛出。
    """

    if valuation_state == "low":
        return _item(
            code="valuation",
            signal="green",
            status="pass",
            anchors=(),
            reason="温度计或调用方输入显示当前估值偏低。",
        )
    if valuation_state == "fair":
        return _item(
            code="valuation",
            signal="yellow",
            status="watch",
            anchors=(),
            reason="温度计或调用方输入显示当前估值处于合理区间。",
        )
    if valuation_state == "high":
        return _item(
            code="valuation",
            signal="red",
            status="block",
            anchors=(),
            reason="温度计或调用方输入显示当前估值偏高。",
        )
    return _item(
        code="valuation",
        signal="gray",
        status="insufficient_data",
        anchors=(),
        reason="温度计数据暂时不可用，请手动确认。",
    )


def _check_money_horizon(money_horizon: MoneyHorizon | None) -> ChecklistItem:
    """检查这笔钱 3-4 年内是否不用，见检查清单第 7 问。

    Args:
        money_horizon: 用户资金期限分类。

    Returns:
        第 7 问检查结果。

    Raises:
        无显式抛出。
    """

    if money_horizon == "long_enough":
        return _item(
            code="money_horizon",
            signal="green",
            status="pass",
            anchors=(),
            reason="用户显式确认资金期限满足长期持有要求。",
        )
    if money_horizon == "uncertain":
        return _item(
            code="money_horizon",
            signal="yellow",
            status="watch",
            anchors=(),
            reason="用户资金期限接近最低要求，需要进一步确认。",
        )
    if money_horizon == "too_short":
        return _item(
            code="money_horizon",
            signal="red",
            status="block",
            anchors=(),
            reason="用户资金期限不满足 3-4 年长期持有要求。",
        )
    return _item(
        code="money_horizon",
        signal="gray",
        status="insufficient_data",
        anchors=(),
        reason="缺少用户资金期限输入，不能判断这笔钱 3-4 年内是否不用。",
    )


def _build_checklist_result(items: tuple[ChecklistItem, ...]) -> ChecklistResult:
    """汇总检查清单结果。

    Args:
        items: 7 个问题结果。

    Returns:
        检查清单汇总结果。

    Raises:
        ValueError: 当问题数量不是 7 个时抛出。
    """

    if len(items) != 7:
        raise ValueError("检查清单必须包含 7 个问题")
    red_items = tuple(item for item in items if item.signal == "red")
    yellow_items = tuple(item for item in items if item.signal == "yellow")
    gray_items = tuple(item for item in items if item.signal == "gray")
    overall_signal = _overall_signal(red_items, yellow_items, gray_items)
    return ChecklistResult(
        items=items,
        overall_signal=overall_signal,
        overall_status=_overall_status(overall_signal),
        red_items=red_items,
        yellow_items=yellow_items,
        gray_items=gray_items,
        next_minimum_verification=_next_minimum_verification(red_items, yellow_items, gray_items),
    )


def _overall_signal(
    red_items: tuple[ChecklistItem, ...],
    yellow_items: tuple[ChecklistItem, ...],
    gray_items: tuple[ChecklistItem, ...],
) -> ChecklistSignal:
    """计算汇总红黄绿灰灯。

    Args:
        red_items: 红灯问题。
        yellow_items: 黄灯问题。
        gray_items: 灰灯问题。

    Returns:
        汇总信号。

    Raises:
        无显式抛出。
    """

    if red_items:
        return "red"
    if yellow_items:
        return "yellow"
    if gray_items:
        return "gray"
    return "green"


def _overall_status(signal: ChecklistSignal) -> ChecklistStatus:
    """把汇总信号转换为汇总状态。

    Args:
        signal: 汇总信号。

    Returns:
        汇总状态。

    Raises:
        无显式抛出。
    """

    if signal == "red":
        return "block"
    if signal == "yellow":
        return "watch"
    if signal == "gray":
        return "insufficient_data"
    return "pass"


def _next_minimum_verification(
    red_items: tuple[ChecklistItem, ...],
    yellow_items: tuple[ChecklistItem, ...],
    gray_items: tuple[ChecklistItem, ...],
) -> str:
    """生成下一步最小验证问题。

    Args:
        red_items: 红灯问题。
        yellow_items: 黄灯问题。
        gray_items: 灰灯问题。

    Returns:
        下一步最小验证问题。

    Raises:
        无显式抛出。
    """

    if red_items:
        return f"先复核红灯问题 `{red_items[0].code}` 是否基于准确输入。"
    if yellow_items:
        return f"先补充或复核黄灯问题 `{yellow_items[0].code}` 的关键证据。"
    if gray_items:
        return f"先补齐灰灯问题 `{gray_items[0].code}` 的显式输入。"
    return "7 个检查问题均为绿灯，下一步进入程序审计。"


def _alignment_disclosure(manager_alignment: ExtractedField[dict[str, object]]) -> str | None:
    """读取 §9 持有披露文本。

    Args:
        manager_alignment: §9 基金经理/从业人员持有披露。

    Returns:
        披露文本；缺失时返回 `None`。

    Raises:
        无显式抛出。
    """

    if manager_alignment.value is None:
        return None
    candidate_keys = ("manager_holding", "employee_holding", "raw_text", "disclosure")
    values = [str(manager_alignment.value[key]) for key in candidate_keys if manager_alignment.value.get(key)]
    if not values:
        return None
    return " ".join(values)


def _contains_any(text: str, keywords: tuple[str, ...]) -> bool:
    """判断文本是否包含任一关键词。

    Args:
        text: 待检测文本。
        keywords: 关键词列表。

    Returns:
        命中任一关键词时返回 `True`。

    Raises:
        无显式抛出。
    """

    return any(keyword in text for keyword in keywords)


def _consistency_anchors(consistency_result: ConsistencyCheckResult) -> tuple[EvidenceAnchor, ...]:
    """合并言行一致性证据锚点。

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


def _risk_anchors(risk_check_result: RiskCheckResult) -> tuple[EvidenceAnchor, ...]:
    """合并否决项证据锚点。

    Args:
        risk_check_result: 否决项检查结果。

    Returns:
        去重后的证据锚点。

    Raises:
        无显式抛出。
    """

    anchors: list[EvidenceAnchor] = []
    seen: set[EvidenceAnchor] = set()
    for item in risk_check_result.items:
        for anchor in item.anchors:
            if anchor in seen:
                continue
            anchors.append(anchor)
            seen.add(anchor)
    return tuple(anchors)


def _parse_decimal(value: Decimal | str | int | float, *, field_name: str) -> Decimal:
    """解析 Decimal 数值。

    Args:
        value: 原始数值。
        field_name: 字段名。

    Returns:
        Decimal 数值。

    Raises:
        ValueError: 当输入为空或无法解析为数值时抛出。
    """

    if isinstance(value, Decimal):
        parsed = value
    elif isinstance(value, int | float):
        parsed = Decimal(str(value))
    else:
        text = str(value).strip().replace(",", "")
        if not text:
            raise ValueError(f"{field_name} 不能为空")
        try:
            parsed = Decimal(text)
        except InvalidOperation as exc:
            raise ValueError(f"{field_name} 无法解析为数值：{value}") from exc
    if parsed < Decimal("0"):
        raise ValueError(f"{field_name} 不能为负数")
    return parsed


def _item(
    *,
    code: ChecklistQuestionCode,
    signal: ChecklistSignal,
    status: ChecklistStatus,
    anchors: tuple[EvidenceAnchor, ...],
    reason: str,
) -> ChecklistItem:
    """构造检查清单问题结果。

    Args:
        code: 问题编码。
        signal: 红黄绿灰灯。
        status: 规则状态。
        anchors: 证据锚点。
        reason: 判断依据。

    Returns:
        单个检查清单问题结果。

    Raises:
        无显式抛出。
    """

    return ChecklistItem(
        code=code,
        question=_question_text(code),
        signal=signal,
        status=status,
        anchors=anchors,
        reason=reason,
    )


def _question_text(code: ChecklistQuestionCode) -> str:
    """读取问题文本。

    Args:
        code: 问题编码。

    Returns:
        问题文本。

    Raises:
        无显式抛出。
    """

    questions: dict[ChecklistQuestionCode, str] = {
        "net_excess_covers_cost": "超额收益能覆盖成本吗？",
        "manager_alignment": "基金经理跟我一条心吗？",
        "investor_return": "投资者真的赚到钱了吗？",
        "consistency": "说的和做的一样吗？",
        "survival": "这只基金不死吗？",
        "valuation": "当前估值处于什么位置？",
        "money_horizon": "这笔钱 3-4 年内不会用吗？",
    }
    return questions[code]
