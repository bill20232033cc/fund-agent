"""基金模板 ITEM_RULE manifest 测试。"""

from __future__ import annotations

from dataclasses import replace
from typing import cast

import pytest

from fund_agent.fund.fund_type import FundType
from fund_agent.fund.template import (
    TemplateItemRule,
    TemplateItemRuleManifest,
    evaluate_template_item_rule,
    evaluate_template_item_rules,
    get_template_item_rule,
    load_template_item_rule_manifest,
    rendered_segment_present,
    validate_template_item_rule_manifest,
)

_EXPECTED_RULE_IDS = (
    "chapter_1_index_constituents",
    "chapter_1_manager_philosophy",
    "chapter_2_alpha_yearly_breakdown",
    "chapter_2_tracking_error_analysis",
)


def test_load_template_item_rule_manifest_returns_exact_four_conditional_rules() -> None:
    """验证内置 ITEM_RULE manifest 只包含模板草稿当前四条 conditional 规则。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当规则数量、编号、章节或模式不符合预期时抛出。
    """

    manifest = load_template_item_rule_manifest()

    assert tuple(rule.rule_id for rule in manifest.rules) == _EXPECTED_RULE_IDS
    assert len({rule.rule_id for rule in manifest.rules}) == 4
    assert {rule.chapter_id for rule in manifest.rules} == {1, 2}
    assert {rule.mode for rule in manifest.rules} == {"conditional"}
    assert {rule.missing_behavior for rule in manifest.rules} == {"delete_segment"}


def test_template_item_rule_manifest_preserves_source_titles_and_facets() -> None:
    """验证 ITEM_RULE 标题与 facet 标签忠实对应模板草稿。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当标题、条件文本或 facet 文案漂移时抛出。
    """

    rules = {rule.rule_id: rule for rule in load_template_item_rule_manifest().rules}

    assert rules["chapter_1_index_constituents"].item_title == "指数编制规则与成分股"
    assert rules["chapter_1_index_constituents"].when_text == "仅对指数基金（含指数增强）输出"
    assert rules["chapter_1_index_constituents"].facets_any == (
        "宽基指数基金",
        "行业/主题指数基金",
        "策略指数基金",
        "指数增强基金",
    )
    assert rules["chapter_1_manager_philosophy"].facets_any == (
        "主动权益基金（价值风格）",
        "主动权益基金（均衡风格）",
        "主动权益基金（成长风格）",
    )
    assert rules["chapter_2_alpha_yearly_breakdown"].when_text == "对主动基金和指数增强基金输出；纯指数基金跳过此项"
    assert "指数增强基金" in rules["chapter_2_alpha_yearly_breakdown"].facets_any
    assert rules["chapter_2_tracking_error_analysis"].item_title == "跟踪误差分析"


def test_template_item_rule_public_exports_can_get_rule_by_id() -> None:
    """验证 template 公共入口导出 ITEM_RULE 读取 helper。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当公共入口无法读取规则时抛出。
    """

    rule = get_template_item_rule("chapter_2_tracking_error_analysis")

    assert rule.chapter_id == 2
    assert rule.segment_markers_any == ("#### 跟踪误差分析", "跟踪误差分析（仅指数基金）")


def test_validate_template_item_rule_manifest_fails_closed_for_invalid_cases() -> None:
    """验证 ITEM_RULE manifest 对典型漂移场景 fail closed。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 非法 manifest 未抛出 `ValueError` 时抛出。
    """

    manifest = load_template_item_rule_manifest()
    first_rule = manifest.rules[0]

    duplicate_id = replace(
        manifest,
        rules=(first_rule, replace(manifest.rules[1], rule_id=first_rule.rule_id), *manifest.rules[2:]),
    )
    with pytest.raises(ValueError, match="重复"):
        validate_template_item_rule_manifest(duplicate_id)

    unknown_chapter = _replace_first_rule(manifest, replace(first_rule, chapter_id=99))
    with pytest.raises(ValueError, match="未知章节"):
        validate_template_item_rule_manifest(unknown_chapter)

    unsupported_mode = _replace_first_rule(
        manifest,
        replace(first_rule, mode=cast("object", "legacy")),
    )
    with pytest.raises(ValueError, match="mode 不受支持"):
        validate_template_item_rule_manifest(unsupported_mode)

    conditional_render_unavailable = _replace_first_rule(
        manifest,
        replace(first_rule, missing_behavior="render_unavailable"),
    )
    with pytest.raises(ValueError, match="conditional 必须 delete_segment"):
        validate_template_item_rule_manifest(conditional_render_unavailable)

    optional_delete_segment = _replace_first_rule(
        manifest,
        replace(_optional_rule(), missing_behavior="delete_segment"),
    )
    with pytest.raises(ValueError, match="optional 必须 render_unavailable"):
        validate_template_item_rule_manifest(optional_delete_segment)

    empty_markers = _replace_first_rule(manifest, replace(first_rule, segment_markers_any=()))
    with pytest.raises(ValueError, match="segment_markers_any"):
        validate_template_item_rule_manifest(empty_markers)

    unsupported_fund_type = _replace_first_rule(
        manifest,
        replace(first_rule, fund_types_any=cast("tuple[FundType, ...]", ("money_market_fund",))),
    )
    with pytest.raises(ValueError, match="不支持的基金类型"):
        validate_template_item_rule_manifest(unsupported_fund_type)

    unsupported_facet = _replace_first_rule(manifest, replace(first_rule, facets_any=("未知细分",)))
    with pytest.raises(ValueError, match="facet 不受支持"):
        validate_template_item_rule_manifest(unsupported_facet)

    ordinary_prose_marker = _replace_first_rule(
        manifest,
        replace(first_rule, segment_markers_any=("跟踪指数",)),
    )
    with pytest.raises(ValueError, match="普通正文短语"):
        validate_template_item_rule_manifest(ordinary_prose_marker)


def test_evaluate_template_item_rules_by_fund_type_without_semantic_nlp() -> None:
    """验证内置 ITEM_RULE 只按标准基金类型做确定性触发。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当任一基金类型触发集合不符合预期时抛出。
    """

    assert _render_rule_ids("index_fund") == {
        "chapter_1_index_constituents",
        "chapter_2_tracking_error_analysis",
    }
    assert _render_rule_ids("enhanced_index") == {
        "chapter_1_index_constituents",
        "chapter_2_alpha_yearly_breakdown",
        "chapter_2_tracking_error_analysis",
    }
    assert _render_rule_ids("active_fund") == {
        "chapter_1_manager_philosophy",
        "chapter_2_alpha_yearly_breakdown",
    }
    assert _render_rule_ids("bond_fund") == set()
    assert _render_rule_ids("qdii_fund") == set()
    assert _render_rule_ids("fof_fund") == set()


def test_evaluate_template_item_rule_validates_explicit_facets_against_fund_type() -> None:
    """验证显式 facet 只在与基金类型相容时触发规则。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 facet 冲突未 fail closed 或相容 facet 未触发时抛出。
    """

    rule = get_template_item_rule("chapter_2_alpha_yearly_breakdown")

    decision = evaluate_template_item_rule(
        rule,
        fund_type="enhanced_index",
        facets=("指数增强基金",),
    )
    assert decision.status == "render"
    assert decision.triggered is True
    assert "显式 facet" in decision.reason

    with pytest.raises(ValueError, match="冲突"):
        evaluate_template_item_rule(rule, fund_type="bond_fund", facets=("指数增强基金",))

    unknown_facet_decision = evaluate_template_item_rule(
        rule,
        fund_type="index_fund",
        facets=("用户自定义标签",),
    )
    assert unknown_facet_decision.status == "delete"
    assert unknown_facet_decision.triggered is False


@pytest.mark.parametrize(
    ("fund_type", "facets"),
    (
        ("bond_fund", ("债券基金", "纯债基金", "二级债基/混合债基", "偏债混合基金")),
        ("qdii_fund", ("QDII基金", "QDII 基金", "境外权益基金")),
        ("fof_fund", ("FOF基金", "FOF 基金", "基金中基金")),
    ),
)
def test_evaluate_template_item_rule_accepts_non_equity_explicit_facets(
    fund_type: FundType,
    facets: tuple[str, ...],
) -> None:
    """验证债券、QDII 与 FOF 的合法显式 facet 不会被静默丢弃。

    Args:
        fund_type: 标准基金类型。
        facets: 与基金类型相容的显式细分标签。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当合法非权益 facet 未进入 evaluator 原因说明时抛出。
    """

    decision = evaluate_template_item_rule(
        _non_equity_fixture_rule(fund_type, facets),
        fund_type=fund_type,
        facets=facets,
    )

    assert decision.status == "render"
    assert decision.triggered is True
    assert "显式 facet" in decision.reason
    assert facets[0] in decision.reason


@pytest.mark.parametrize(
    ("fund_type", "facets"),
    (
        ("bond_fund", ("QDII 基金",)),
        ("qdii_fund", ("FOF 基金",)),
        ("fof_fund", ("纯债基金",)),
    ),
)
def test_evaluate_template_item_rule_rejects_non_equity_facet_conflicts(
    fund_type: FundType,
    facets: tuple[str, ...],
) -> None:
    """验证债券、QDII 与 FOF 的显式 facet 冲突会 fail closed。

    Args:
        fund_type: 标准基金类型。
        facets: 与基金类型冲突的显式细分标签。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当冲突 facet 未抛出 `ValueError` 时抛出。
    """

    with pytest.raises(ValueError, match="冲突"):
        evaluate_template_item_rule(
            _non_equity_fixture_rule("bond_fund", ("债券基金",)),
            fund_type=fund_type,
            facets=facets,
        )


def test_optional_fixture_renders_unavailable_without_builtin_optional_rule() -> None:
    """验证 optional 模式只作为 schema/evaluator 能力存在，不进入内置 manifest。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 optional fixture 决策或内置规则模式不符合预期时抛出。
    """

    manifest = load_template_item_rule_manifest()
    assert all(rule.mode == "conditional" for rule in manifest.rules)

    decision = evaluate_template_item_rule(_optional_rule(), fund_type="bond_fund")

    assert decision.status == "render"
    assert decision.triggered is False
    assert decision.missing_behavior == "render_unavailable"


def test_rendered_segment_present_uses_unique_markers_not_ordinary_prose() -> None:
    """验证段落存在判断只消费唯一小节标记，不把普通正文短语当成命中。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当普通正文短语产生误判时抛出。
    """

    rule = get_template_item_rule("chapter_2_tracking_error_analysis")

    assert rendered_segment_present("正文提到跟踪指数，但没有 ITEM_RULE 小节。", rule) is False
    assert rendered_segment_present("#### 跟踪误差分析\n\n这里是段落。", rule) is True
    assert rendered_segment_present("跟踪误差分析（仅指数基金）\n\n这里是段落。", rule) is True

    inactive_decision = evaluate_template_item_rule(rule, fund_type="active_fund")
    assert inactive_decision.status == "delete"
    assert rendered_segment_present("正文提到日均偏离度，但没有唯一小节标记。", rule) is False


def test_evaluate_template_item_rule_rejects_unsupported_fund_type() -> None:
    """验证 evaluator 对不支持的基金类型 fail closed。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当不支持基金类型未抛出 `ValueError` 时抛出。
    """

    rule = get_template_item_rule("chapter_1_index_constituents")

    with pytest.raises(ValueError, match="不支持的基金类型"):
        evaluate_template_item_rule(
            rule,
            fund_type=cast(FundType, "money_market_fund"),
        )


def _render_rule_ids(fund_type: FundType) -> set[str]:
    """返回指定基金类型下需要渲染的内置 ITEM_RULE 编号集合。

    Args:
        fund_type: 标准基金类型。

    Returns:
        决策状态为 `render` 的规则编号集合。

    Raises:
        ValueError: 基金类型不受支持时抛出。
    """

    decisions = evaluate_template_item_rules(fund_type=fund_type)
    return {decision.rule_id for decision in decisions if decision.status == "render"}


def _optional_rule() -> TemplateItemRule:
    """构造仅用于测试 optional 模式的本地 ITEM_RULE。

    Args:
        无。

    Returns:
        optional 模式规则 fixture。

    Raises:
        无显式抛出。
    """

    return TemplateItemRule(
        rule_id="fixture_optional_unavailable",
        chapter_id=1,
        item_title="测试可选字段",
        mode="optional",
        when_text="测试 optional fixture",
        facets_any=(),
        fund_types_any=("active_fund",),
        segment_markers_any=("#### 测试可选字段",),
        missing_behavior="render_unavailable",
    )


def _non_equity_fixture_rule(fund_type: FundType, facets: tuple[str, ...]) -> TemplateItemRule:
    """构造用于验证非权益 facet 映射的本地 ITEM_RULE。

    Args:
        fund_type: 规则显式适用的标准基金类型。
        facets: 规则显式适用的细分标签。

    Returns:
        conditional 模式规则 fixture。

    Raises:
        无显式抛出。
    """

    return TemplateItemRule(
        rule_id=f"fixture_{fund_type}_facets",
        chapter_id=1,
        item_title="测试非权益细分标签",
        mode="conditional",
        when_text="测试 fixture",
        facets_any=facets,
        fund_types_any=(fund_type,),
        segment_markers_any=("#### 测试非权益细分标签",),
        missing_behavior="delete_segment",
    )


def _replace_first_rule(
    manifest: TemplateItemRuleManifest,
    replacement: TemplateItemRule,
) -> TemplateItemRuleManifest:
    """替换 manifest 中的第一条规则。

    Args:
        manifest: 原始 ITEM_RULE 清单。
        replacement: 替换后的第一条规则。

    Returns:
        替换第一条规则后的 manifest。

    Raises:
        无显式抛出。
    """

    return replace(manifest, rules=(replacement, *manifest.rules[1:]))
