"""分析模块比例解析工具。"""

from __future__ import annotations

import re
from decimal import Decimal, InvalidOperation
from typing import Final

_PERCENT_PATTERN: Final[re.Pattern[str]] = re.compile(r"[-+]?\d+(?:,\d{3})*(?:\.\d+)?\s*%?")


def parse_ratio(value: object, *, field_name: str) -> Decimal:
    """解析比例字段为小数比例。

    字符串输入按年报披露文本解析，带 `%` 或绝对值大于 1 的数字文本按百分比换算。
    数值型输入视为调用方已经标准化的小数比例，不再按绝对值二次归一，避免
    123.45% 换手率已表达为 `Decimal("1.2345")` 时被错误缩小为 `0.012345`。

    Args:
        value: 原始比例值。
        field_name: 字段名，用于错误信息。

    Returns:
        Decimal 小数比例。

    Raises:
        ValueError: 当输入为空或无法解析为比例时抛出。
    """

    if value is None:
        raise ValueError(f"{field_name} 不能为空")
    if isinstance(value, bool):
        raise ValueError(f"{field_name} 不能为布尔值")
    if isinstance(value, Decimal):
        return value
    if isinstance(value, int | float):
        return Decimal(str(value))
    text = str(value).strip()
    if not text:
        raise ValueError(f"{field_name} 不能为空")
    match = _PERCENT_PATTERN.search(text)
    if match is None:
        raise ValueError(f"{field_name} 无法解析为比例：{text}")

    raw_number = match.group(0).replace(",", "").replace("%", "").strip()
    try:
        parsed = Decimal(raw_number)
    except InvalidOperation as exc:
        raise ValueError(f"{field_name} 无法解析为比例：{text}") from exc

    if "%" in match.group(0) or abs(parsed) > Decimal("1"):
        return parsed / Decimal("100")
    return parsed


def normalize_numeric_ratio(value: Decimal) -> Decimal:
    """把明确标注为百分数口径的数值统一为小数比例。

    新代码优先直接调用 `parse_ratio()` 并传入标准小数比例；本函数仅保留给
    已知输入仍使用百分数数值口径的调用方。

    Args:
        value: 数值型比例。

    Returns:
        小数比例；绝对值大于 1 时按百分比口径换算。

    Raises:
        无显式抛出。
    """

    if abs(value) > Decimal("1"):
        return value / Decimal("100")
    return value
