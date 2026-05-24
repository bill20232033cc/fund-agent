"""超额收益性质判断模块。

本模块属于 Agent 层基金能力，服务模板第 2 章“R=A+B-C 收益归因”中
“结构性超额 vs 阶段性超额”的判断，不输出买卖建议。
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Final, Literal

from fund_agent.fund.analysis.r_abc import RabcAttribution
from fund_agent.fund.fund_type import FundType

MarketEnvironment = Literal["bull", "bear", "range_bound", "unknown"]
AlphaSourceConfidence = Literal["explained", "partial", "unexplained"]
AlphaNature = Literal[
    "structural",
    "partial_structural",
    "cyclical",
    "not_applicable",
    "insufficient_data",
]

_INDEX_FUND_TYPES: Final[frozenset[FundType]] = frozenset({"index_fund"})
_DEFAULT_MIN_OBSERVATIONS: Final[int] = 3
_DEFAULT_STRUCTURAL_POSITIVE_COUNT: Final[int] = 4
_DEFAULT_PARTIAL_POSITIVE_COUNT: Final[int] = 3


@dataclass(frozen=True, slots=True)
class AlphaJudgmentRule:
    """超额收益性质判断规则配置。

    Attributes:
        min_observations: 允许判断所需的最少有效年度数。
        structural_positive_count: 判为结构性超额所需的最少正 Alpha 年数。
        partial_positive_count: 判为部分结构性所需的最少正 Alpha 年数。
        require_bull_and_bear_positive: 结构性超额是否必须牛熊环境都为正。
        require_explained_source: 结构性超额是否必须来源可解释。
    """

    min_observations: int = _DEFAULT_MIN_OBSERVATIONS
    structural_positive_count: int = _DEFAULT_STRUCTURAL_POSITIVE_COUNT
    partial_positive_count: int = _DEFAULT_PARTIAL_POSITIVE_COUNT
    require_bull_and_bear_positive: bool = True
    require_explained_source: bool = True


@dataclass(frozen=True, slots=True)
class AlphaObservation:
    """单期超额收益观察值。

    Attributes:
        period: 周期标识，例如年度。
        alpha_return: 超额收益 A，小数比例。
        net_excess_return: 扣成本后净超额收益，小数比例；缺失时可为 `None`。
        market_environment: 市场环境。
        source_confidence: 超额收益来源解释强度。
        source_note: 来源解释说明。
    """

    period: str
    alpha_return: Decimal
    net_excess_return: Decimal | None
    market_environment: MarketEnvironment
    source_confidence: AlphaSourceConfidence
    source_note: str | None = None


@dataclass(frozen=True, slots=True)
class AlphaJudgment:
    """超额收益性质判断结果。

    Attributes:
        nature: 超额收益性质。
        positive_alpha_count: 正 Alpha 周期数。
        observation_count: 有效观察周期数。
        positive_market_environments: 正 Alpha 覆盖的市场环境。
        explained_source_count: 来源明确解释的周期数。
        observations: 参与判断的观察值。
        reasons: 判断依据。
        risks: 阶段性或证据不足风险。
    """

    nature: AlphaNature
    positive_alpha_count: int
    observation_count: int
    positive_market_environments: tuple[MarketEnvironment, ...]
    explained_source_count: int
    observations: tuple[AlphaObservation, ...]
    reasons: tuple[str, ...]
    risks: tuple[str, ...]


def judge_alpha_nature(
    observations: tuple[AlphaObservation, ...],
    *,
    fund_type: FundType,
    rule: AlphaJudgmentRule | None = None,
) -> AlphaJudgment:
    """判断超额收益属于结构性、部分结构性还是阶段性，见模板第 2 章。

    Args:
        observations: 多年度超额收益观察值。
        fund_type: 标准化基金类型；纯指数基金返回 `not_applicable`。
        rule: 判断规则配置；未提供时使用 MVP 默认规则。

    Returns:
        超额收益性质判断结果。

    Raises:
        ValueError: 当规则阈值非法时抛出。
    """

    active_rule = rule or AlphaJudgmentRule()
    _validate_rule(active_rule)
    if fund_type in _INDEX_FUND_TYPES:
        return _not_applicable_result(observations)

    valid_observations = tuple(observation for observation in observations if observation.period.strip())
    if len(valid_observations) < active_rule.min_observations:
        return _insufficient_data_result(valid_observations, active_rule)

    positive_observations = tuple(
        observation for observation in valid_observations if observation.alpha_return > Decimal("0")
    )
    positive_market_environments = _positive_market_environments(positive_observations)
    explained_source_count = sum(
        1 for observation in valid_observations if observation.source_confidence == "explained"
    )
    has_bull_and_bear = {"bull", "bear"} <= set(positive_market_environments)
    has_explained_source = explained_source_count > 0

    if _meets_structural_rule(
        positive_count=len(positive_observations),
        has_bull_and_bear=has_bull_and_bear,
        has_explained_source=has_explained_source,
        rule=active_rule,
    ):
        return _structural_result(
            observations=valid_observations,
            positive_count=len(positive_observations),
            positive_market_environments=positive_market_environments,
            explained_source_count=explained_source_count,
        )

    if len(positive_observations) >= active_rule.partial_positive_count or has_bull_and_bear:
        return _partial_structural_result(
            observations=valid_observations,
            positive_count=len(positive_observations),
            positive_market_environments=positive_market_environments,
            explained_source_count=explained_source_count,
            has_bull_and_bear=has_bull_and_bear,
            has_explained_source=has_explained_source,
        )

    return _cyclical_result(
        observations=valid_observations,
        positive_count=len(positive_observations),
        positive_market_environments=positive_market_environments,
        explained_source_count=explained_source_count,
    )


def observations_from_attributions(
    attributions: tuple[RabcAttribution, ...],
    *,
    market_environments: dict[str, MarketEnvironment],
    source_confidences: dict[str, AlphaSourceConfidence],
    source_notes: dict[str, str] | None = None,
) -> tuple[AlphaObservation, ...]:
    """从 R=A+B-C 归因结果构造超额收益观察值。

    Args:
        attributions: R=A+B-C 归因结果序列。
        market_environments: 周期到市场环境的映射。
        source_confidences: 周期到来源解释强度的映射。
        source_notes: 周期到来源解释说明的映射。

    Returns:
        可用于性质判断的观察值元组；`missing` 或 Alpha 缺失的归因会被跳过。

    Raises:
        ValueError: 当有效归因缺少市场环境或来源解释强度时抛出。
    """

    notes = source_notes or {}
    observations: list[AlphaObservation] = []
    for attribution in attributions:
        if attribution.status == "missing" or attribution.alpha_return_a is None:
            continue
        period = attribution.period
        if period not in market_environments:
            raise ValueError(f"{period} 缺少市场环境，不能判断结构性/阶段性超额")
        if period not in source_confidences:
            raise ValueError(f"{period} 缺少超额收益来源解释强度")
        observations.append(
            AlphaObservation(
                period=period,
                alpha_return=attribution.alpha_return_a,
                net_excess_return=attribution.net_excess_return,
                market_environment=market_environments[period],
                source_confidence=source_confidences[period],
                source_note=notes.get(period),
            )
        )
    return tuple(observations)


def _validate_rule(rule: AlphaJudgmentRule) -> None:
    """校验超额收益判断规则。

    Args:
        rule: 判断规则配置。

    Returns:
        无返回值。

    Raises:
        ValueError: 当规则阈值不合理时抛出。
    """

    if rule.min_observations <= 0:
        raise ValueError("min_observations 必须为正数")
    if rule.structural_positive_count < rule.partial_positive_count:
        raise ValueError("structural_positive_count 不能小于 partial_positive_count")
    if rule.partial_positive_count <= 0:
        raise ValueError("partial_positive_count 必须为正数")


def _positive_market_environments(
    positive_observations: tuple[AlphaObservation, ...],
) -> tuple[MarketEnvironment, ...]:
    """汇总正 Alpha 覆盖的市场环境。

    Args:
        positive_observations: Alpha 为正的观察值。

    Returns:
        去重且稳定排序的市场环境。

    Raises:
        无显式抛出。
    """

    order: tuple[MarketEnvironment, ...] = ("bull", "bear", "range_bound", "unknown")
    observed = {observation.market_environment for observation in positive_observations}
    return tuple(environment for environment in order if environment in observed)


def _meets_structural_rule(
    *,
    positive_count: int,
    has_bull_and_bear: bool,
    has_explained_source: bool,
    rule: AlphaJudgmentRule,
) -> bool:
    """判断是否满足结构性超额规则。

    Args:
        positive_count: 正 Alpha 周期数。
        has_bull_and_bear: 是否牛熊环境都为正。
        has_explained_source: 是否存在明确来源解释。
        rule: 判断规则配置。

    Returns:
        满足结构性超额时返回 `True`。

    Raises:
        无显式抛出。
    """

    if positive_count < rule.structural_positive_count:
        return False
    if rule.require_bull_and_bear_positive and not has_bull_and_bear:
        return False
    if rule.require_explained_source and not has_explained_source:
        return False
    return True


def _not_applicable_result(observations: tuple[AlphaObservation, ...]) -> AlphaJudgment:
    """构造指数基金不适用结果。

    Args:
        observations: 原始观察值。

    Returns:
        `not_applicable` 判断结果。

    Raises:
        无显式抛出。
    """

    return AlphaJudgment(
        nature="not_applicable",
        positive_alpha_count=0,
        observation_count=len(observations),
        positive_market_environments=(),
        explained_source_count=0,
        observations=observations,
        reasons=("纯指数基金的核心不是超额收益性质，而是跟踪误差和费率。",),
        risks=(),
    )


def _insufficient_data_result(
    observations: tuple[AlphaObservation, ...],
    rule: AlphaJudgmentRule,
) -> AlphaJudgment:
    """构造证据不足结果。

    Args:
        observations: 有效观察值。
        rule: 判断规则配置。

    Returns:
        `insufficient_data` 判断结果。

    Raises:
        无显式抛出。
    """

    positive_count = sum(1 for observation in observations if observation.alpha_return > Decimal("0"))
    positive_environments = _positive_market_environments(
        tuple(observation for observation in observations if observation.alpha_return > Decimal("0"))
    )
    return AlphaJudgment(
        nature="insufficient_data",
        positive_alpha_count=positive_count,
        observation_count=len(observations),
        positive_market_environments=positive_environments,
        explained_source_count=sum(
            1 for observation in observations if observation.source_confidence == "explained"
        ),
        observations=observations,
        reasons=(f"有效观察期 {len(observations)} 个，少于最小判断要求 {rule.min_observations} 个。",),
        risks=("不能用不足样本判断结构性或阶段性超额。",),
    )


def _structural_result(
    *,
    observations: tuple[AlphaObservation, ...],
    positive_count: int,
    positive_market_environments: tuple[MarketEnvironment, ...],
    explained_source_count: int,
) -> AlphaJudgment:
    """构造结构性超额结果。

    Args:
        observations: 有效观察值。
        positive_count: 正 Alpha 周期数。
        positive_market_environments: 正 Alpha 覆盖的市场环境。
        explained_source_count: 来源明确解释的周期数。

    Returns:
        `structural` 判断结果。

    Raises:
        无显式抛出。
    """

    return AlphaJudgment(
        nature="structural",
        positive_alpha_count=positive_count,
        observation_count=len(observations),
        positive_market_environments=positive_market_environments,
        explained_source_count=explained_source_count,
        observations=observations,
        reasons=(
            f"{positive_count}/{len(observations)} 个观察期 Alpha 为正。",
            "正 Alpha 同时覆盖牛市和熊市环境。",
            f"{explained_source_count} 个观察期存在明确来源解释。",
        ),
        risks=(),
    )


def _partial_structural_result(
    *,
    observations: tuple[AlphaObservation, ...],
    positive_count: int,
    positive_market_environments: tuple[MarketEnvironment, ...],
    explained_source_count: int,
    has_bull_and_bear: bool,
    has_explained_source: bool,
) -> AlphaJudgment:
    """构造部分结构性超额结果。

    Args:
        observations: 有效观察值。
        positive_count: 正 Alpha 周期数。
        positive_market_environments: 正 Alpha 覆盖的市场环境。
        explained_source_count: 来源明确解释的周期数。
        has_bull_and_bear: 是否牛熊环境都为正。
        has_explained_source: 是否存在明确来源解释。

    Returns:
        `partial_structural` 判断结果。

    Raises:
        无显式抛出。
    """

    risks = _partial_structural_risks(
        has_bull_and_bear=has_bull_and_bear,
        has_explained_source=has_explained_source,
    )
    return AlphaJudgment(
        nature="partial_structural",
        positive_alpha_count=positive_count,
        observation_count=len(observations),
        positive_market_environments=positive_market_environments,
        explained_source_count=explained_source_count,
        observations=observations,
        reasons=(f"{positive_count}/{len(observations)} 个观察期 Alpha 为正。",),
        risks=risks,
    )


def _partial_structural_risks(
    *,
    has_bull_and_bear: bool,
    has_explained_source: bool,
) -> tuple[str, ...]:
    """生成部分结构性超额的风险说明。

    Args:
        has_bull_and_bear: 是否牛熊环境都为正。
        has_explained_source: 是否存在明确来源解释。

    Returns:
        风险说明元组。

    Raises:
        无显式抛出。
    """

    risks: list[str] = []
    if not has_bull_and_bear:
        risks.append("正 Alpha 尚未同时覆盖牛市和熊市环境。")
    if not has_explained_source:
        risks.append("缺少可解释的超额收益来源。")
    return tuple(risks)


def _cyclical_result(
    *,
    observations: tuple[AlphaObservation, ...],
    positive_count: int,
    positive_market_environments: tuple[MarketEnvironment, ...],
    explained_source_count: int,
) -> AlphaJudgment:
    """构造阶段性超额结果。

    Args:
        observations: 有效观察值。
        positive_count: 正 Alpha 周期数。
        positive_market_environments: 正 Alpha 覆盖的市场环境。
        explained_source_count: 来源明确解释的周期数。

    Returns:
        `cyclical` 判断结果。

    Raises:
        无显式抛出。
    """

    return AlphaJudgment(
        nature="cyclical",
        positive_alpha_count=positive_count,
        observation_count=len(observations),
        positive_market_environments=positive_market_environments,
        explained_source_count=explained_source_count,
        observations=observations,
        reasons=(f"正 Alpha 仅出现在 {positive_count}/{len(observations)} 个观察期。",),
        risks=("超额收益集中在少数时期，更接近阶段性风格顺风或运气。",),
    )
