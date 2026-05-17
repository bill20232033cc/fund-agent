"""超额收益性质判断测试。"""

from __future__ import annotations

from decimal import Decimal

import pytest

from fund_agent.fund.analysis import (
    AlphaObservation,
    RabcAttribution,
    judge_alpha_nature,
    observations_from_attributions,
)


def _observation(
    period: str,
    alpha: str,
    environment: str,
    source_confidence: str,
) -> AlphaObservation:
    """构造测试用超额收益观察值。

    Args:
        period: 周期标识。
        alpha: 超额收益 A，小数比例字符串。
        environment: 市场环境。
        source_confidence: 来源解释强度。

    Returns:
        超额收益观察值。

    Raises:
        无显式抛出。
    """

    return AlphaObservation(
        period=period,
        alpha_return=Decimal(alpha),
        net_excess_return=Decimal(alpha) - Decimal("0.01"),
        market_environment=environment,  # type: ignore[arg-type]
        source_confidence=source_confidence,  # type: ignore[arg-type]
        source_note="fixture",
    )


def _attribution(period: str, alpha: str) -> RabcAttribution:
    """构造测试用 R=A+B-C 归因结果。

    Args:
        period: 周期标识。
        alpha: 超额收益 A，小数比例字符串。

    Returns:
        R=A+B-C 归因结果。

    Raises:
        无显式抛出。
    """

    return RabcAttribution(
        period=period,
        status="computed",
        total_return_r=Decimal("0.10"),
        beta_return_b=Decimal("0.08"),
        alpha_return_a=Decimal(alpha),
        explicit_cost_c=Decimal("0.01"),
        net_excess_return=Decimal(alpha) - Decimal("0.01"),
        turnover_cost=Decimal("0.003"),
        anchors=(),
        note=None,
    )


def test_judge_alpha_nature_identifies_structural_alpha() -> None:
    """验证多年度为正、牛熊都为正且来源可解释时判为结构性超额。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当结构性规则判断错误时抛出。
    """

    judgment = judge_alpha_nature(
        (
            _observation("2020", "0.03", "bull", "explained"),
            _observation("2021", "0.02", "range_bound", "explained"),
            _observation("2022", "0.01", "bear", "partial"),
            _observation("2023", "-0.01", "range_bound", "partial"),
            _observation("2024", "0.04", "bull", "explained"),
        ),
        fund_type="active_fund",
    )

    assert judgment.nature == "structural"
    assert judgment.positive_alpha_count == 4
    assert judgment.positive_market_environments == ("bull", "bear", "range_bound")
    assert judgment.explained_source_count == 3
    assert not judgment.risks


def test_judge_alpha_nature_identifies_partial_structural_alpha() -> None:
    """验证正 Alpha 较多但缺少牛熊覆盖时判为部分结构性。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当部分结构性规则判断错误时抛出。
    """

    judgment = judge_alpha_nature(
        (
            _observation("2020", "0.03", "bull", "explained"),
            _observation("2021", "0.02", "bull", "explained"),
            _observation("2022", "0.01", "range_bound", "partial"),
            _observation("2023", "-0.02", "bear", "partial"),
            _observation("2024", "-0.01", "range_bound", "partial"),
        ),
        fund_type="active_fund",
    )

    assert judgment.nature == "partial_structural"
    assert judgment.positive_alpha_count == 3
    assert "正 Alpha 尚未同时覆盖牛市和熊市环境。" in judgment.risks


def test_judge_alpha_nature_identifies_cyclical_alpha() -> None:
    """验证正 Alpha 集中在少数年份时判为阶段性超额。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当阶段性规则判断错误时抛出。
    """

    judgment = judge_alpha_nature(
        (
            _observation("2020", "0.03", "bull", "unexplained"),
            _observation("2021", "-0.02", "range_bound", "unexplained"),
            _observation("2022", "-0.01", "bear", "unexplained"),
            _observation("2023", "0.01", "bull", "unexplained"),
            _observation("2024", "-0.03", "range_bound", "unexplained"),
        ),
        fund_type="active_fund",
    )

    assert judgment.nature == "cyclical"
    assert judgment.positive_alpha_count == 2
    assert "超额收益集中在少数时期，更接近阶段性风格顺风或运气。" in judgment.risks


def test_judge_alpha_nature_skips_index_fund() -> None:
    """验证纯指数基金不做结构性/阶段性超额判断。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当指数基金未返回不适用时抛出。
    """

    judgment = judge_alpha_nature(
        (_observation("2024", "0.01", "bull", "explained"),),
        fund_type="index_fund",
    )

    assert judgment.nature == "not_applicable"
    assert judgment.reasons == ("纯指数基金的核心不是超额收益性质，而是跟踪误差和费率。",)


def test_judge_alpha_nature_requires_enough_observations() -> None:
    """验证有效观察期不足时不强行判断性质。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当样本不足仍输出性质判断时抛出。
    """

    judgment = judge_alpha_nature(
        (
            _observation("2023", "0.01", "bear", "explained"),
            _observation("2024", "0.02", "bull", "explained"),
        ),
        fund_type="active_fund",
    )

    assert judgment.nature == "insufficient_data"
    assert judgment.observation_count == 2
    assert "不能用不足样本判断结构性或阶段性超额。" in judgment.risks


def test_observations_from_attributions_requires_market_environment() -> None:
    """验证从归因结果适配时必须显式提供市场环境。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当缺少市场环境未报错时抛出。
    """

    with pytest.raises(ValueError, match="2024 缺少市场环境"):
        observations_from_attributions(
            (_attribution("2024", "0.02"),),
            market_environments={},
            source_confidences={"2024": "explained"},
        )


def test_observations_from_attributions_skips_missing_attribution() -> None:
    """验证 missing 归因不会进入超额收益性质判断样本。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 missing 归因被纳入样本时抛出。
    """

    missing_attribution = RabcAttribution(
        period="2023",
        status="missing",
        total_return_r=None,
        beta_return_b=None,
        alpha_return_a=None,
        explicit_cost_c=None,
        net_excess_return=None,
        turnover_cost=None,
        anchors=(),
        note="fixture missing",
    )

    observations = observations_from_attributions(
        (missing_attribution, _attribution("2024", "0.02")),
        market_environments={"2024": "bull"},
        source_confidences={"2024": "explained"},
    )

    assert len(observations) == 1
    assert observations[0].period == "2024"
