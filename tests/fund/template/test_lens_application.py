"""preferred_lens 应用计划测试。"""

from __future__ import annotations

import pytest

from fund_agent.fund.fund_type import FundType
from fund_agent.fund.template import build_lens_application_plan


@pytest.mark.parametrize(
    "fund_type",
    (
        "index_fund",
        "active_fund",
        "bond_fund",
        "enhanced_index",
        "qdii_fund",
        "fof_fund",
    ),
)
def test_build_lens_application_plan_resolves_all_chapters(fund_type: FundType) -> None:
    """验证所有标准基金类型都能构建 8 章 lens 应用计划。

    Args:
        fund_type: 标准基金类型。

    Returns:
        无返回值。

    Raises:
        AssertionError: 任一基金类型不能解析 8 章 lens 时抛出。
    """

    plan = build_lens_application_plan(fund_type)

    assert plan.fund_type == fund_type
    assert tuple(chapter.chapter_id for chapter in plan.chapters) == tuple(range(8))
    assert all(chapter.primary_focus for chapter in plan.chapters)
    assert all(chapter.watch_variable_label for chapter in plan.chapters)
    assert all(chapter.risk_focus_label for chapter in plan.chapters)
    assert all(chapter.source_statements for chapter in plan.chapters)


def test_build_lens_application_plan_records_default_fallback() -> None:
    """验证章节缺少精确 lens 时记录 default fallback。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 default fallback 未被标记时抛出。
    """

    plan = build_lens_application_plan("active_fund")

    fallback_chapters = tuple(chapter for chapter in plan.chapters if chapter.used_default)
    assert fallback_chapters
    assert all(chapter.lens_key == "default" for chapter in fallback_chapters)


@pytest.mark.parametrize(
    ("fund_type", "chapter_ids", "match_text"),
    (
        ("money_market_fund", tuple(range(8)), "不支持的基金类型"),
        ("active_fund", (), "不能为空"),
        ("active_fund", (0, 0), "存在重复"),
        ("active_fund", (8,), "越界"),
    ),
)
def test_build_lens_application_plan_fails_closed_for_invalid_inputs(
    fund_type: str,
    chapter_ids: tuple[int, ...],
    match_text: str,
) -> None:
    """验证 lens 应用计划对非法入参 fail closed。

    Args:
        fund_type: 待测试基金类型。
        chapter_ids: 待测试章节编号。
        match_text: 预期错误信息片段。

    Returns:
        无返回值。

    Raises:
        AssertionError: 非法入参未抛出 `ValueError` 时抛出。
    """

    with pytest.raises(ValueError, match=match_text):
        build_lens_application_plan(fund_type, chapter_ids=chapter_ids)  # type: ignore[arg-type]
