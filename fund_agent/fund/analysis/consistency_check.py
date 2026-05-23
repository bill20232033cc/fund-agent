"""言行一致性检验模块。

本模块属于 Agent 层基金能力，服务模板第 3 章“基金经理画像与言行一致性”。
它只消费 P1 结构化字段与调用方显式传入的实际风格/仓位证据，不直接读取年报文件。
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Final, Literal

from fund_agent.fund.analysis._ratios import parse_ratio
from fund_agent.fund.extractors.models import EvidenceAnchor, ExtractedField

ConsistencyDimension = Literal[
    "investment_style",
    "industry_preference",
    "position_management",
    "turnover_level",
]
ConsistencySignal = Literal["green", "yellow", "red", "gray"]
ConsistencyStatus = Literal["aligned", "partial", "misaligned", "insufficient_data"]

_DEFAULT_LOW_TURNOVER_THRESHOLD: Final[Decimal] = Decimal("1.0")
_DEFAULT_HIGH_TURNOVER_THRESHOLD: Final[Decimal] = Decimal("2.0")
_DEFAULT_LOW_POSITION_THRESHOLD: Final[Decimal] = Decimal("0.4")
_DEFAULT_HIGH_POSITION_THRESHOLD: Final[Decimal] = Decimal("0.8")
_STYLE_KEYWORDS: Final[dict[str, tuple[str, ...]]] = {
    "value": ("价值", "低估值", "安全边际", "高股息", "红利"),
    "growth": ("成长", "高成长", "研发", "创新"),
    "balanced": ("均衡", "平衡", "分散", "多元"),
    "quality": ("质量", "优质", "龙头", "护城河"),
}
_INDUSTRY_KEYWORDS: Final[tuple[str, ...]] = (
    "制造",
    "消费",
    "医药",
    "金融",
    "科技",
    "新能源",
    "电子",
    "银行",
    "地产",
    "周期",
    "传媒",
    "军工",
    "港股",
)
_LOW_TURNOVER_DECLARATION_KEYWORDS: Final[tuple[str, ...]] = ("长期", "低换手", "买入并持有", "持有周期")
_HIGH_TURNOVER_DECLARATION_KEYWORDS: Final[tuple[str, ...]] = ("灵活", "波段", "交易", "择时")
_HIGH_POSITION_KEYWORDS: Final[tuple[str, ...]] = ("高仓位", "较高仓位", "中高仓位")
_LOW_POSITION_KEYWORDS: Final[tuple[str, ...]] = ("低仓位", "控制仓位", "降低仓位")
_BALANCED_POSITION_KEYWORDS: Final[tuple[str, ...]] = ("均衡配置", "分散配置", "适度仓位")


@dataclass(frozen=True, slots=True)
class ConsistencyRule:
    """言行一致性规则配置。

    Attributes:
        low_turnover_threshold: 低换手宣称对应的绿色阈值。
        high_turnover_threshold: 低换手宣称对应的红色阈值。
        low_position_threshold: 低仓位阈值。
        high_position_threshold: 高仓位阈值。
    """

    low_turnover_threshold: Decimal = _DEFAULT_LOW_TURNOVER_THRESHOLD
    high_turnover_threshold: Decimal = _DEFAULT_HIGH_TURNOVER_THRESHOLD
    low_position_threshold: Decimal = _DEFAULT_LOW_POSITION_THRESHOLD
    high_position_threshold: Decimal = _DEFAULT_HIGH_POSITION_THRESHOLD


@dataclass(frozen=True, slots=True)
class ConsistencyDimensionResult:
    """单个言行一致性维度结果。

    Attributes:
        dimension: 维度名称。
        status: 一致性状态。
        signal: 红黄绿灰信号。
        declared: §4 宣称内容或规则化摘要。
        actual: §8 实际行为或规则化摘要。
        anchors: 参与判断的证据锚点。
        reason: 判断依据。
    """

    dimension: ConsistencyDimension
    status: ConsistencyStatus
    signal: ConsistencySignal
    declared: str | None
    actual: str | None
    anchors: tuple[EvidenceAnchor, ...]
    reason: str


@dataclass(frozen=True, slots=True)
class ConsistencyCheckResult:
    """言行一致性 4 维度检查结果。

    Attributes:
        dimensions: 四个维度的检查结果。
        overall_status: 汇总状态。
        overall_signal: 汇总信号。
        reasons: 汇总判断依据。
    """

    dimensions: tuple[ConsistencyDimensionResult, ...]
    overall_status: ConsistencyStatus
    overall_signal: ConsistencySignal
    reasons: tuple[str, ...]


def check_consistency(
    *,
    product_profile: ExtractedField[dict[str, object]],
    manager_strategy_text: ExtractedField[dict[str, object]],
    holdings_snapshot: ExtractedField[dict[str, object]],
    turnover_rate: ExtractedField[dict[str, object]],
    actual_style: str | None = None,
    actual_equity_position: Decimal | str | int | float | None = None,
    rule: ConsistencyRule | None = None,
) -> ConsistencyCheckResult:
    """执行言行一致性 4 维度检验，见模板第 3 章。

    Args:
        product_profile: P1 从 §2 抽取的产品本质、投资策略和风格定位。
        manager_strategy_text: P1 从 §4 抽取的策略和展望。
        holdings_snapshot: P1 从 §8 抽取的持仓快照。
        turnover_rate: P1 从 §8 抽取的换手率。
        actual_style: 调用方显式提供的实际持仓风格；缺失时风格维度返回证据不足。
        actual_equity_position: 调用方显式提供的实际股票仓位；缺失时仓位维度返回证据不足。
        rule: 规则配置；未提供时使用默认阈值。

    Returns:
        四维度言行一致性检查结果。

    Raises:
        ValueError: 当显式仓位格式非法时抛出。
    """

    active_rule = rule or ConsistencyRule()
    dimensions = (
        _check_investment_style(product_profile, manager_strategy_text, actual_style),
        _check_industry_preference(manager_strategy_text, holdings_snapshot),
        _check_position_management(manager_strategy_text, actual_equity_position, active_rule),
        _check_turnover_level(manager_strategy_text, turnover_rate, active_rule),
    )
    return _build_overall_result(dimensions)


def _check_investment_style(
    product_profile: ExtractedField[dict[str, object]],
    manager_strategy_text: ExtractedField[dict[str, object]],
    actual_style: str | None,
) -> ConsistencyDimensionResult:
    """检查投资风格维度。

    Args:
        product_profile: §2 产品画像字段。
        manager_strategy_text: §4 策略文本字段。
        actual_style: 显式实际持仓风格。

    Returns:
        投资风格维度结果。

    Raises:
        无显式抛出。
    """

    declared_text = _field_text(product_profile, ("style_positioning", "investment_strategy", "investment_objective"))
    if not declared_text:
        declared_text = _field_text(manager_strategy_text, ("strategy_summary",))
    declared_style = _style_bucket(declared_text)
    actual_style_bucket = _style_bucket(actual_style)
    anchors = _merge_anchors(product_profile, manager_strategy_text)
    if declared_style is None or actual_style_bucket is None:
        return _insufficient_result(
            dimension="investment_style",
            declared=declared_text,
            actual=actual_style,
            anchors=anchors,
            reason="缺少 §2 风格定位或显式实际持仓风格，不能判断投资风格言行一致性。",
        )
    if declared_style == actual_style_bucket:
        return _dimension_result(
            dimension="investment_style",
            status="aligned",
            signal="green",
            declared=declared_style,
            actual=actual_style_bucket,
            anchors=anchors,
            reason="§2 宣称风格与显式实际持仓风格一致。",
        )
    return _dimension_result(
        dimension="investment_style",
        status="misaligned",
        signal="red",
        declared=declared_style,
        actual=actual_style_bucket,
        anchors=anchors,
        reason="§2 宣称风格与显式实际持仓风格不一致。",
    )


def _check_industry_preference(
    manager_strategy_text: ExtractedField[dict[str, object]],
    holdings_snapshot: ExtractedField[dict[str, object]],
) -> ConsistencyDimensionResult:
    """检查行业偏好维度。

    Args:
        manager_strategy_text: §4 策略文本字段。
        holdings_snapshot: §8 持仓快照字段。

    Returns:
        行业偏好维度结果。

    Raises:
        无显式抛出。
    """

    declared_text = _field_text(manager_strategy_text, ("strategy_summary", "market_outlook"))
    declared_industries = _extract_industry_keywords(declared_text)
    actual_industries = _extract_actual_industries(holdings_snapshot)
    anchors = _merge_anchors(manager_strategy_text, holdings_snapshot)
    if not declared_industries or not actual_industries:
        return _insufficient_result(
            dimension="industry_preference",
            declared="、".join(declared_industries) if declared_industries else declared_text,
            actual="、".join(actual_industries) if actual_industries else None,
            anchors=anchors,
            reason="缺少 §4 行业偏好宣称或 §8 行业分布，不能判断行业偏好一致性。",
        )
    overlap = tuple(industry for industry in declared_industries if industry in actual_industries)
    if overlap:
        return _dimension_result(
            dimension="industry_preference",
            status="aligned",
            signal="green",
            declared="、".join(declared_industries),
            actual="、".join(actual_industries),
            anchors=anchors,
            reason=f"§4 宣称行业与 §8 行业分布存在交集：{'、'.join(overlap)}。",
        )
    return _dimension_result(
        dimension="industry_preference",
        status="misaligned",
        signal="red",
        declared="、".join(declared_industries),
        actual="、".join(actual_industries),
        anchors=anchors,
        reason="§4 宣称行业未出现在 §8 行业分布中。",
    )


def _check_position_management(
    manager_strategy_text: ExtractedField[dict[str, object]],
    actual_equity_position: Decimal | str | int | float | None,
    rule: ConsistencyRule,
) -> ConsistencyDimensionResult:
    """检查仓位管理维度。

    Args:
        manager_strategy_text: §4 策略文本字段。
        actual_equity_position: 显式实际股票仓位。
        rule: 规则配置。

    Returns:
        仓位管理维度结果。

    Raises:
        ValueError: 当显式仓位格式非法时抛出。
    """

    declared_text = _field_text(manager_strategy_text, ("strategy_summary",))
    declared_bucket = _position_bucket_from_text(declared_text)
    anchors = manager_strategy_text.anchors
    if actual_equity_position is None:
        return _insufficient_result(
            dimension="position_management",
            declared=declared_bucket or declared_text,
            actual=None,
            anchors=anchors,
            reason="缺少显式实际股票仓位，不能判断仓位管理一致性。",
        )
    actual_ratio = _parse_ratio(actual_equity_position, field_name="actual_equity_position")
    actual_bucket = _position_bucket_from_ratio(actual_ratio, rule)
    if declared_bucket is None:
        return _insufficient_result(
            dimension="position_management",
            declared=declared_text,
            actual=actual_bucket,
            anchors=anchors,
            reason="缺少 §4 仓位策略宣称，不能判断仓位管理一致性。",
        )
    if declared_bucket == actual_bucket:
        return _dimension_result(
            dimension="position_management",
            status="aligned",
            signal="green",
            declared=declared_bucket,
            actual=actual_bucket,
            anchors=anchors,
            reason="§4 仓位策略宣称与显式实际股票仓位一致。",
        )
    if "balanced" in {declared_bucket, actual_bucket}:
        return _dimension_result(
            dimension="position_management",
            status="partial",
            signal="yellow",
            declared=declared_bucket,
            actual=actual_bucket,
            anchors=anchors,
            reason="§4 仓位策略宣称与显式实际股票仓位存在轻微偏差。",
        )
    return _dimension_result(
        dimension="position_management",
        status="misaligned",
        signal="red",
        declared=declared_bucket,
        actual=actual_bucket,
        anchors=anchors,
        reason="§4 仓位策略宣称与显式实际股票仓位不一致。",
    )


def _check_turnover_level(
    manager_strategy_text: ExtractedField[dict[str, object]],
    turnover_rate: ExtractedField[dict[str, object]],
    rule: ConsistencyRule,
) -> ConsistencyDimensionResult:
    """检查换手水平维度。

    Args:
        manager_strategy_text: §4 策略文本字段。
        turnover_rate: §8 换手率字段。
        rule: 规则配置。

    Returns:
        换手水平维度结果。

    Raises:
        ValueError: 当换手率格式非法时抛出。
    """

    declared_text = _field_text(manager_strategy_text, ("strategy_summary",))
    declared_turnover = _turnover_declaration(declared_text)
    anchors = _merge_anchors(manager_strategy_text, turnover_rate)
    if turnover_rate.value is None or turnover_rate.value.get("turnover_rate") is None:
        return _insufficient_result(
            dimension="turnover_level",
            declared=declared_turnover or declared_text,
            actual=None,
            anchors=anchors,
            reason="缺少 §8 换手率，不能判断换手水平一致性。",
        )
    if declared_turnover is None:
        return _insufficient_result(
            dimension="turnover_level",
            declared=declared_text,
            actual=str(turnover_rate.value.get("turnover_rate")),
            anchors=anchors,
            reason="缺少 §4 持有周期或换手水平宣称，不能判断换手水平一致性。",
        )

    actual_turnover = _parse_ratio(turnover_rate.value["turnover_rate"], field_name="turnover_rate")
    return _turnover_result(
        declared_turnover=declared_turnover,
        actual_turnover=actual_turnover,
        anchors=anchors,
        rule=rule,
    )


def _turnover_result(
    *,
    declared_turnover: str,
    actual_turnover: Decimal,
    anchors: tuple[EvidenceAnchor, ...],
    rule: ConsistencyRule,
) -> ConsistencyDimensionResult:
    """根据宣称换手水平与实际换手率生成维度结果。

    Args:
        declared_turnover: 宣称换手水平。
        actual_turnover: 实际换手率。
        anchors: 证据锚点。
        rule: 规则配置。

    Returns:
        换手水平维度结果。

    Raises:
        无显式抛出。
    """

    actual_text = f"{actual_turnover:.4f}"
    if declared_turnover == "low":
        if actual_turnover <= rule.low_turnover_threshold:
            return _dimension_result(
                dimension="turnover_level",
                status="aligned",
                signal="green",
                declared="low",
                actual=actual_text,
                anchors=anchors,
                reason="§4 宣称长期/低换手，且 §8 换手率处于低换手阈值内。",
            )
        if actual_turnover <= rule.high_turnover_threshold:
            return _dimension_result(
                dimension="turnover_level",
                status="partial",
                signal="yellow",
                declared="low",
                actual=actual_text,
                anchors=anchors,
                reason="§4 宣称长期/低换手，但 §8 换手率偏高。",
            )
        return _dimension_result(
            dimension="turnover_level",
            status="misaligned",
            signal="red",
            declared="low",
            actual=actual_text,
            anchors=anchors,
            reason="§4 宣称长期/低换手，但 §8 换手率明显偏高。",
        )

    if actual_turnover >= rule.low_turnover_threshold:
        return _dimension_result(
            dimension="turnover_level",
            status="aligned",
            signal="green",
            declared="active",
            actual=actual_text,
            anchors=anchors,
            reason="§4 宣称灵活交易，且 §8 换手率支持该说法。",
        )
    return _dimension_result(
        dimension="turnover_level",
        status="partial",
        signal="yellow",
        declared="active",
        actual=actual_text,
        anchors=anchors,
        reason="§4 宣称灵活交易，但 §8 换手率不高。",
    )


def _build_overall_result(
    dimensions: tuple[ConsistencyDimensionResult, ...],
) -> ConsistencyCheckResult:
    """构造 4 维度汇总结果。

    Args:
        dimensions: 各维度结果。

    Returns:
        言行一致性汇总结果。

    Raises:
        无显式抛出。
    """

    statuses = tuple(dimension.status for dimension in dimensions)
    if "misaligned" in statuses:
        overall_status: ConsistencyStatus = "misaligned"
        overall_signal: ConsistencySignal = "red"
    elif "partial" in statuses:
        overall_status = "partial"
        overall_signal = "yellow"
    elif all(status == "aligned" for status in statuses):
        overall_status = "aligned"
        overall_signal = "green"
    else:
        overall_status = "insufficient_data"
        overall_signal = "gray"
    return ConsistencyCheckResult(
        dimensions=dimensions,
        overall_status=overall_status,
        overall_signal=overall_signal,
        reasons=tuple(dimension.reason for dimension in dimensions),
    )


def _field_text(field: ExtractedField[dict[str, object]], keys: tuple[str, ...]) -> str | None:
    """按子字段拼接抽取字段文本。

    Args:
        field: 抽取字段。
        keys: 子字段名。

    Returns:
        拼接后的文本；没有文本时返回 `None`。

    Raises:
        无显式抛出。
    """

    if field.value is None:
        return None
    values = [str(field.value[key]).strip() for key in keys if field.value.get(key)]
    return "；".join(values) if values else None


def _style_bucket(text: str | None) -> str | None:
    """从文本中识别风格桶。

    Args:
        text: 待识别文本。

    Returns:
        风格桶；未识别时返回 `None`。

    Raises:
        无显式抛出。
    """

    if not text:
        return None
    for bucket, keywords in _STYLE_KEYWORDS.items():
        if any(keyword in text for keyword in keywords):
            return bucket
    return None


def _extract_industry_keywords(text: str | None) -> tuple[str, ...]:
    """从文本中提取行业关键词。

    Args:
        text: 待提取文本。

    Returns:
        去重后的行业关键词。

    Raises:
        无显式抛出。
    """

    if not text:
        return ()
    return tuple(keyword for keyword in _INDUSTRY_KEYWORDS if keyword in text)


def _extract_actual_industries(holdings_snapshot: ExtractedField[dict[str, object]]) -> tuple[str, ...]:
    """从持仓快照中提取实际行业分布关键词。

    Args:
        holdings_snapshot: §8 持仓快照字段。

    Returns:
        实际行业关键词。

    Raises:
        无显式抛出。
    """

    if holdings_snapshot.value is None:
        return ()
    industry_distribution = holdings_snapshot.value.get("industry_distribution")
    if not isinstance(industry_distribution, list):
        return ()
    joined_rows = " ".join(str(row) for row in industry_distribution)
    return _extract_industry_keywords(joined_rows)


def _position_bucket_from_text(text: str | None) -> str | None:
    """从 §4 文本中识别仓位宣称。

    Args:
        text: §4 策略文本。

    Returns:
        `low / balanced / high` 之一；未识别时返回 `None`。

    Raises:
        无显式抛出。
    """

    if not text:
        return None
    if any(keyword in text for keyword in _HIGH_POSITION_KEYWORDS):
        return "high"
    if any(keyword in text for keyword in _LOW_POSITION_KEYWORDS):
        return "low"
    if any(keyword in text for keyword in _BALANCED_POSITION_KEYWORDS):
        return "balanced"
    return None


def _position_bucket_from_ratio(value: Decimal, rule: ConsistencyRule) -> str:
    """从实际股票仓位识别仓位桶。

    Args:
        value: 实际股票仓位。
        rule: 规则配置。

    Returns:
        `low / balanced / high`。

    Raises:
        无显式抛出。
    """

    if value >= rule.high_position_threshold:
        return "high"
    if value <= rule.low_position_threshold:
        return "low"
    return "balanced"


def _turnover_declaration(text: str | None) -> str | None:
    """从 §4 文本中识别换手宣称。

    Args:
        text: §4 策略文本。

    Returns:
        `low / active` 之一；未识别时返回 `None`。

    Raises:
        无显式抛出。
    """

    if not text:
        return None
    if any(keyword in text for keyword in _LOW_TURNOVER_DECLARATION_KEYWORDS):
        return "low"
    if any(keyword in text for keyword in _HIGH_TURNOVER_DECLARATION_KEYWORDS):
        return "active"
    return None


def _parse_ratio(value: object, *, field_name: str) -> Decimal:
    """调用分析模块公共比例解析工具。

    Args:
        value: 原始比例值。
        field_name: 字段名。

    Returns:
        Decimal 小数比例。

    Raises:
        ValueError: 当输入为空或无法解析为比例时抛出。
    """

    return parse_ratio(value, field_name=field_name)


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


def _dimension_result(
    *,
    dimension: ConsistencyDimension,
    status: ConsistencyStatus,
    signal: ConsistencySignal,
    declared: str | None,
    actual: str | None,
    anchors: tuple[EvidenceAnchor, ...],
    reason: str,
) -> ConsistencyDimensionResult:
    """构造单维度结果。

    Args:
        dimension: 维度。
        status: 状态。
        signal: 信号。
        declared: 宣称内容。
        actual: 实际行为。
        anchors: 证据锚点。
        reason: 判断依据。

    Returns:
        单维度结果。

    Raises:
        无显式抛出。
    """

    return ConsistencyDimensionResult(
        dimension=dimension,
        status=status,
        signal=signal,
        declared=declared,
        actual=actual,
        anchors=anchors,
        reason=reason,
    )


def _insufficient_result(
    *,
    dimension: ConsistencyDimension,
    declared: str | None,
    actual: str | None,
    anchors: tuple[EvidenceAnchor, ...],
    reason: str,
) -> ConsistencyDimensionResult:
    """构造证据不足结果。

    Args:
        dimension: 维度。
        declared: 宣称内容。
        actual: 实际行为。
        anchors: 证据锚点。
        reason: 证据不足原因。

    Returns:
        证据不足的单维度结果。

    Raises:
        无显式抛出。
    """

    return _dimension_result(
        dimension=dimension,
        status="insufficient_data",
        signal="gray",
        declared=declared,
        actual=actual,
        anchors=anchors,
        reason=reason,
    )
