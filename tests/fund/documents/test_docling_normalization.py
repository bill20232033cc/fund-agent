"""Docling candidate 文本归一化测试。"""

from __future__ import annotations

from fund_agent.fund.documents.candidates.models import CandidateFailureCode
from fund_agent.fund.documents.candidates.normalization import (
    implemented_text_normalization_rules,
    normalize_text,
)


def test_cjk_and_date_space_repairs_preserve_raw_text() -> None:
    """验证 CJK 与日期空白修复。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 修复结果或规则名不符合预期时抛出。
    """

    result = normalize_text("本基金的 基 金 经 理，2022年8 月8日任职")
    assert result.raw_text == "本基金的 基 金 经 理，2022年8 月8日任职"
    assert result.normalized_text == "本基金的基金经理，2022年8月8日任职"
    assert "cjk_space_repair" in result.rules_applied
    assert "date_space_repair" in result.rules_applied


def test_numeric_punctuation_repairs_docling_splits() -> None:
    """验证数字标点 split 的确定性修复。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 修复结果不符合预期时抛出。
    """

    first = normalize_text("33,984,439 .75")
    second = normalize_text("154,973,70 4.60")
    assert first.normalized_text == "33,984,439.75"
    assert second.normalized_text == "154,973,704.60"
    assert first.rules_applied == ("numeric_punctuation_repair",)
    assert second.rules_applied == ("numeric_punctuation_repair",)


def test_numeric_whitespace_grouping_repairs_only_deterministic_cases() -> None:
    """验证 whitespace-only 数字分组的 repair/block 语义。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: repair/block 结果不符合预期时抛出。
    """

    assert normalize_text("100 000").normalized_text == "100000"
    assert normalize_text("1 234 567").normalized_text == "1234567"
    assert normalize_text("12 345.67").normalized_text == "12345.67"
    assert normalize_text("-1 234 567.89").normalized_text == "-1234567.89"
    ambiguous = normalize_text("1 23 456")
    range_like = normalize_text("50 100")
    adjacent = normalize_text("A 100 000")
    assert ambiguous.failure_code == CandidateFailureCode.NUMERIC_REPAIR_AMBIGUOUS
    assert range_like.failure_code == CandidateFailureCode.NUMERIC_REPAIR_AMBIGUOUS
    assert adjacent.failure_code == CandidateFailureCode.NUMERIC_REPAIR_AMBIGUOUS


def test_text_normalization_rule_contract_is_separate_from_locator_rules() -> None:
    """验证文本级 API 只声明文本级规则。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 文本级规则包含 locator 规则时抛出。
    """

    assert implemented_text_normalization_rules() == (
        "cjk_space_repair",
        "date_space_repair",
        "numeric_punctuation_repair",
        "numeric_whitespace_grouping_repair_or_block",
    )

