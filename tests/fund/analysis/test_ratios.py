"""分析模块比例解析工具测试。"""

from __future__ import annotations

from decimal import Decimal

import pytest

from fund_agent.fund.analysis._ratios import normalize_numeric_ratio, parse_ratio


@pytest.mark.parametrize(
    ("raw_value", "expected"),
    (
        ("12.34%", Decimal("0.1234")),
        ("管理费率 1.20%/年", Decimal("0.012")),
        ("123.45%", Decimal("1.2345")),
        ("0.80", Decimal("0.80")),
        ("80", Decimal("0.8")),
    ),
)
def test_parse_ratio_parses_disclosure_text_to_decimal_ratio(
    raw_value: str,
    expected: Decimal,
) -> None:
    """验证披露文本会解析为小数比例。

    Args:
        raw_value: 原始披露文本。
        expected: 期望小数比例。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当文本比例解析错误时抛出。
    """

    assert parse_ratio(raw_value, field_name="ratio") == expected


@pytest.mark.parametrize(
    ("raw_value", "expected"),
    (
        (Decimal("1.2345"), Decimal("1.2345")),
        (Decimal("2"), Decimal("2")),
        (1.2345, Decimal("1.2345")),
        (2, Decimal("2")),
    ),
)
def test_parse_ratio_keeps_numeric_inputs_as_already_normalized_decimal_ratio(
    raw_value: Decimal | int | float,
    expected: Decimal,
) -> None:
    """验证数值型输入视为已标准化小数比例，不按大于 1 二次除以 100。

    Args:
        raw_value: 数值型比例。
        expected: 期望解析结果。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当数值型比例被错误归一时抛出。
    """

    assert parse_ratio(raw_value, field_name="ratio") == expected


def test_parse_ratio_rejects_bool_before_numeric_handling() -> None:
    """验证 bool 不会被 Python 的 int 子类关系误当作数值比例。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 bool 未被拒绝时抛出。
    """

    with pytest.raises(ValueError, match="不能为布尔值"):
        parse_ratio(True, field_name="ratio")
    with pytest.raises(ValueError, match="不能为布尔值"):
        parse_ratio(False, field_name="ratio")


def test_normalize_numeric_ratio_remains_available_for_known_percent_numeric_inputs() -> None:
    """验证保留的数值百分比归一 helper 行为不变。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当显式数值百分比 helper 行为漂移时抛出。
    """

    assert normalize_numeric_ratio(Decimal("80")) == Decimal("0.8")
    assert normalize_numeric_ratio(Decimal("0.8")) == Decimal("0.8")


def test_parse_ratio_rejects_empty_or_unparseable_values() -> None:
    """验证空值和不可解析文本 fail closed。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当非法输入未抛出 `ValueError` 时抛出。
    """

    with pytest.raises(ValueError, match="不能为空"):
        parse_ratio(None, field_name="ratio")
    with pytest.raises(ValueError, match="无法解析为比例"):
        parse_ratio("未披露", field_name="ratio")
