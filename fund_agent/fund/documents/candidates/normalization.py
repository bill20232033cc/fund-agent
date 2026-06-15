"""Docling candidate 文本级归一化 helper。

本模块只处理 locator/text stability，不解析 Decimal、不选择业务字段、不证明字段正确性。
"""

from __future__ import annotations

import re

from .models import (
    CandidateFailureCode,
    DOCUMENT_TEXT_NORMALIZATION_RULE_NAMES,
    NormalizationRuleName,
    NormalizedText,
)

_CJK_SPACE_RE = re.compile(r"(?<=[\u4e00-\u9fff])\s+(?=[\u4e00-\u9fff])")
_DATE_SPACE_RE = re.compile(r"(\d{4})\s*年\s*(\d{1,2})\s*月\s*(\d{1,2})\s*日")
_NUMERIC_TOKEN_RE = re.compile(r"(?<![A-Za-z0-9])[-+]?\d[\d,\.\s]*\d(?![A-Za-z0-9])")
_VALID_COMMA_DECIMAL_RE = re.compile(r"^[-+]?\d{1,3}(?:,\d{3})+(?:\.\d+)?$")
_VALID_GROUPED_DECIMAL_RE = re.compile(r"^[-+]?\d+(?:\.\d+)?$")


def normalize_text(raw_text: str) -> NormalizedText:
    """按闭合规则执行文本级归一化。

    Args:
        raw_text: 待归一化的原始文本。

    Returns:
        包含 raw/normalized/rules/failure 的 ``NormalizedText``。

    Raises:
        无显式抛出。
    """

    current = raw_text
    rules: list[NormalizationRuleName] = []
    failure_code: CandidateFailureCode | None = None

    current, changed = repair_cjk_spaces(current)
    if changed:
        rules.append("cjk_space_repair")

    current, changed = repair_date_spaces(current)
    if changed:
        rules.append("date_space_repair")

    current, changed = repair_numeric_punctuation(current)
    if changed:
        rules.append("numeric_punctuation_repair")

    whitespace_result = repair_numeric_whitespace_grouping(current)
    current = whitespace_result.normalized_text
    if whitespace_result.rules_applied:
        rules.append("numeric_whitespace_grouping_repair_or_block")
    if whitespace_result.failure_code is not None:
        failure_code = whitespace_result.failure_code

    return NormalizedText(
        raw_text=raw_text,
        normalized_text=current,
        rules_applied=tuple(dict.fromkeys(rules)),
        failure_code=failure_code,
    )


def repair_cjk_spaces(text: str) -> tuple[str, bool]:
    """删除相邻 CJK 字符之间的 ASCII 空白。

    Args:
        text: 原始文本。

    Returns:
        二元组：归一化文本、是否发生变更。

    Raises:
        无显式抛出。
    """

    normalized = _CJK_SPACE_RE.sub("", text)
    return normalized, normalized != text


def repair_date_spaces(text: str) -> tuple[str, bool]:
    """规范中文日期内部空白。

    Args:
        text: 原始文本。

    Returns:
        二元组：归一化文本、是否发生变更。

    Raises:
        无显式抛出。
    """

    normalized = _DATE_SPACE_RE.sub(r"\1年\2月\3日", text)
    return normalized, normalized != text


def repair_numeric_punctuation(text: str) -> tuple[str, bool]:
    """修复数字标点附近的确定性空白。

    Args:
        text: 原始文本。

    Returns:
        二元组：归一化文本、是否发生变更。

    Raises:
        无显式抛出。
    """

    changed = False

    def _replace(match: re.Match[str]) -> str:
        nonlocal changed
        token = match.group(0)
        if " " not in token or "," not in token:
            return token
        collapsed = re.sub(r"\s+", "", token)
        if _VALID_COMMA_DECIMAL_RE.fullmatch(collapsed):
            changed = True
            return collapsed
        return token

    normalized = _NUMERIC_TOKEN_RE.sub(_replace, text)
    return normalized, changed


def repair_numeric_whitespace_grouping(text: str) -> NormalizedText:
    """修复或阻断 whitespace-only 数字分组。

    Args:
        text: 原始文本。

    Returns:
        ``NormalizedText``，其中 failure_code 表示歧义分组需要 fail-closed。

    Raises:
        无显式抛出。
    """

    changed = False
    blocked = False

    def _replace(match: re.Match[str]) -> str:
        nonlocal changed, blocked
        token = match.group(0)
        if "," in token or " " not in token:
            return token
        previous_char = _previous_non_space(text, match.start())
        next_char = _next_non_space(text, match.end())
        if _is_adjacent_business_char(previous_char) or _is_adjacent_business_char(next_char):
            blocked = True
            return token
        unsigned = token.lstrip("+-")
        integer_part, dot, decimal_part = unsigned.partition(".")
        groups = integer_part.split()
        has_sign = token.startswith(("+", "-"))
        sign = token[0] if has_sign else ""
        accepted_group = _is_accepted_whitespace_group(groups) or (
            bool(dot)
            and len(groups) == 2
            and 1 <= len(groups[0]) <= 3
            and len(groups[1]) == 3
            and all(group.isdigit() for group in groups)
        )
        if accepted_group and (not dot or decimal_part.isdigit()):
            collapsed = sign + "".join(groups) + (dot + decimal_part if dot else "")
            if _VALID_GROUPED_DECIMAL_RE.fullmatch(collapsed):
                changed = True
                return collapsed
        blocked = True
        return token

    normalized = _NUMERIC_TOKEN_RE.sub(_replace, text)
    rules: tuple[NormalizationRuleName, ...] = (
        ("numeric_whitespace_grouping_repair_or_block",) if changed or blocked else ()
    )
    return NormalizedText(
        raw_text=text,
        normalized_text=normalized,
        rules_applied=rules,
        failure_code=CandidateFailureCode.NUMERIC_REPAIR_AMBIGUOUS if blocked else None,
    )


def implemented_text_normalization_rules() -> tuple[NormalizationRuleName, ...]:
    """返回文本级归一化 helper 实现的规则名。

    Args:
        无。

    Returns:
        文本级规则名闭集。

    Raises:
        无显式抛出。
    """

    return DOCUMENT_TEXT_NORMALIZATION_RULE_NAMES


def _is_accepted_whitespace_group(groups: list[str]) -> bool:
    """判断 whitespace-only 数字分组是否可确定性修复。

    Args:
        groups: 已按空白拆分的数字组。

    Returns:
        可确定性修复时返回 ``True``。

    Raises:
        无显式抛出。
    """

    if len(groups) < 2:
        return False
    if not all(group.isdigit() for group in groups):
        return False
    if len(groups[0]) > 3:
        return False
    if any(len(group) != 3 for group in groups[1:]):
        return False
    if len(groups) == 2 and len(groups[0]) < 3:
        return False
    return True


def _is_adjacent_business_char(value: str) -> bool:
    """判断相邻字符是否会造成数字 token 边界歧义。

    Args:
        value: 单个相邻字符。

    Returns:
        CJK/Latin 字符返回 ``True``。

    Raises:
        无显式抛出。
    """

    if not value:
        return False
    return bool(re.match(r"[A-Za-z\u4e00-\u9fff]", value))


def _previous_non_space(text: str, index: int) -> str:
    """查找 index 前的最近非空白字符。

    Args:
        text: 完整文本。
        index: 当前匹配起点。

    Returns:
        最近非空白字符；不存在时返回空字符串。

    Raises:
        无显式抛出。
    """

    cursor = index - 1
    while cursor >= 0:
        if not text[cursor].isspace():
            return text[cursor]
        cursor -= 1
    return ""


def _next_non_space(text: str, index: int) -> str:
    """查找 index 后的最近非空白字符。

    Args:
        text: 完整文本。
        index: 当前匹配终点。

    Returns:
        最近非空白字符；不存在时返回空字符串。

    Raises:
        无显式抛出。
    """

    cursor = index
    while cursor < len(text):
        if not text[cursor].isspace():
            return text[cursor]
        cursor += 1
    return ""
