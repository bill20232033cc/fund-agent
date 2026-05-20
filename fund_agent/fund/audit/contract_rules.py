"""CHAPTER_CONTRACT 程序审计规则。

本模块属于基金 Capability 层，服务 `docs/design.md` 第 5.2 节的确定性 C2 审计。
它只维护 manifest 到程序审计 marker 的显式映射，不做 LLM 判断或语义推断。
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

from fund_agent.fund.template.contracts import TemplateContractManifest, load_template_contract_manifest


@dataclass(frozen=True, slots=True)
class ContractRequiredItemRule:
    """模板 required_output_items 的确定性 marker 规则。

    Attributes:
        chapter_id: 模板章节编号。
        item_text: manifest 中的 required_output_items 原文。
        markers_any: 任一出现即可判定该条目存在的字面 marker。
    """

    chapter_id: int
    item_text: str
    markers_any: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class ContractForbiddenContentRule:
    """模板 must_not_cover 的确定性禁止 marker 规则。

    Attributes:
        chapter_id: 模板章节编号。
        item_text: manifest 中的 must_not_cover 原文。
        forbidden_markers_any: 任一出现即判定违反该禁止项的字面 marker。
    """

    chapter_id: int
    item_text: str
    forbidden_markers_any: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class ProgrammaticContractRules:
    """程序化 CHAPTER_CONTRACT 审计规则集合。

    Attributes:
        required_items: required_output_items 的字面 marker 规则。
        forbidden_contents: must_not_cover 的字面禁止 marker 规则。
    """

    required_items: tuple[ContractRequiredItemRule, ...]
    forbidden_contents: tuple[ContractForbiddenContentRule, ...]


_REQUIRED_ITEM_RULES: Final[tuple[ContractRequiredItemRule, ...]] = (
    ContractRequiredItemRule(0, "一句话这是什么基金", ("基金：",)),
    ContractRequiredItemRule(0, "基金简介", ("基金：",)),
    ContractRequiredItemRule(0, "当前动作（🟢 值得持有 / 🟡 需要关注 / 🔴 建议替换）", ("最终判断：",)),
    ContractRequiredItemRule(0, "当前业绩与运作状态", ("当前业绩与运作状态：",)),
    ContractRequiredItemRule(0, "支撑当前动作的最主要理由", ("支撑当前动作的最主要理由：",)),
    ContractRequiredItemRule(0, "当前最值得盯住的变量", ("当前最值得盯住的变量：",)),
    ContractRequiredItemRule(0, "当前最大的风险", ("当前最大的风险：",)),
    ContractRequiredItemRule(0, "下一步最小验证问题", ("下一步最小验证问题：",)),
    ContractRequiredItemRule(0, "什么变化会升级、降级或终止当前动作", ("什么变化会升级、降级或终止当前动作：",)),
    ContractRequiredItemRule(1, "基金类型与分类标签", ("基金类型与分类标签：",)),
    ContractRequiredItemRule(1, "投资目标（一句话）", ("投资目标（一句话）：",)),
    ContractRequiredItemRule(1, "投资策略概述", ("投资策略概述：",)),
    ContractRequiredItemRule(1, "业绩基准及合理性", ("业绩基准及合理性：",)),
    ContractRequiredItemRule(1, "看这类基金最先看什么", ("看这类基金最先看什么：",)),
    ContractRequiredItemRule(1, "会改变产品理解的特别情况（如有）", ("会改变产品理解的特别情况：",)),
    ContractRequiredItemRule(2, "近 1/3/5 年净值增长率", ("近 1/3/5 年净值增长率：",)),
    ContractRequiredItemRule(2, "近 1/3/5 年业绩基准收益率", ("近 1/3/5 年业绩基准收益率：",)),
    ContractRequiredItemRule(2, "超额收益（A = R - B）及稳定性", ("超额收益（A = R - B）及稳定性：",)),
    ContractRequiredItemRule(2, "超额收益性质判断（结构性 vs 阶段性）", ("超额收益性质：",)),
    ContractRequiredItemRule(2, "成本拆解（管理费、托管费、交易成本）", ("成本拆解：",)),
    ContractRequiredItemRule(2, "成本合理性判断（同类对比）", ("成本合理性判断：",)),
    ContractRequiredItemRule(2, "R=A+B-C 综合评估", ("R=A+B-C 综合评估：",)),
    ContractRequiredItemRule(3, "基金经理基本信息", ("基金经理基本信息：",)),
    ContractRequiredItemRule(3, "宣称的投资策略（§4）", ("宣称的投资策略（§4）：",)),
    ContractRequiredItemRule(3, "实际投资行为（§8）", ("实际投资行为（§8）：",)),
    ContractRequiredItemRule(3, "言行一致性判断", ("言行一致性判断：",)),
    ContractRequiredItemRule(3, "风格稳定性判断", ("风格稳定性判断：",)),
    ContractRequiredItemRule(3, "利益一致性判断", ("利益一致性判断：",)),
    ContractRequiredItemRule(4, "基金产品收益 vs 投资者实际收益", ("基金产品收益 vs 投资者实际收益：",)),
    ContractRequiredItemRule(4, "盈利投资者占比", ("盈利投资者占比：",)),
    ContractRequiredItemRule(4, "行为损益估算", ("行为损益估算：",)),
    ContractRequiredItemRule(4, "份额变动趋势", ("份额变动趋势：",)),
    ContractRequiredItemRule(5, "过去一年最关键的变化（1-3 个）", ("过去一年最关键的变化：",)),
    ContractRequiredItemRule(5, "基金当前所处阶段", ("基金当前所处阶段：",)),
    ContractRequiredItemRule(5, "变化是否改变前文判断", ("变化是否改变前文判断：",)),
    ContractRequiredItemRule(5, "接下来最该跟踪的变量", ("接下来最该跟踪的变量：",)),
    ContractRequiredItemRule(6, "最关键的风险或否决项", ("最关键的风险或否决项：",)),
    ContractRequiredItemRule(6, "为什么足以改变结论", ("为什么足以改变结论：",)),
    ContractRequiredItemRule(6, "否决 vs 跟踪判断", ("否决 vs 跟踪判断：",)),
    ContractRequiredItemRule(6, "下一轮先验证什么", ("下一轮先验证什么：",)),
    ContractRequiredItemRule(7, "最终判断（🟢 值得持有 / 🟡 需要关注 / 🔴 建议替换）", ("最终判断：",)),
    ContractRequiredItemRule(7, "支撑判断的核心依据（1-2 条）", ("支撑判断的核心依据：",)),
    ContractRequiredItemRule(7, "当前最容易看错的地方", ("当前最容易看错的地方：",)),
    ContractRequiredItemRule(7, "下一轮最小验证计划", ("下一轮最小验证计划：",)),
    ContractRequiredItemRule(7, "危级/降级阈值", ("危级/降级阈值：",)),
)

_FORBIDDEN_CONTENT_RULES: Final[tuple[ContractForbiddenContentRule, ...]] = (
    ContractForbiddenContentRule(0, "不输出“证据与出处”小节。", ("证据与出处",)),
    ContractForbiddenContentRule(2, "不做未来收益预测。", ("未来收益预测",)),
    ContractForbiddenContentRule(3, "不做基金经理性格或人品的主观评价。", ("性格", "人品")),
    ContractForbiddenContentRule(3, "不猜测基金经理的动机。", ("动机",)),
    ContractForbiddenContentRule(4, "不分析具体投资者的交易行为。", ("具体投资者的交易行为",)),
    ContractForbiddenContentRule(4, "不做未来投资者行为预测。", ("未来投资者行为预测",)),
    ContractForbiddenContentRule(5, "不做市场整体走势预测。", ("市场整体走势预测",)),
    ContractForbiddenContentRule(6, "不做风险发生概率的定量预测。", ("风险发生概率",)),
    ContractForbiddenContentRule(7, "不输出具体的买入金额、卖出时机或仓位比例。", ("买入金额", "卖出时机", "仓位比例")),
)


def load_programmatic_contract_rules() -> ProgrammaticContractRules:
    """读取程序化 CHAPTER_CONTRACT 审计规则。

    Returns:
        已通过 manifest 校验的程序审计规则集合。

    Raises:
        ValueError: 规则引用未知章节、未知条目、marker 为空或 required item 未覆盖时抛出。
    """

    rules = ProgrammaticContractRules(
        required_items=_REQUIRED_ITEM_RULES,
        forbidden_contents=_FORBIDDEN_CONTENT_RULES,
    )
    validate_programmatic_contract_rules(rules)
    return rules


def validate_programmatic_contract_rules(rules: ProgrammaticContractRules) -> None:
    """校验程序化 CHAPTER_CONTRACT 审计规则。

    Args:
        rules: 待校验的规则集合。

    Returns:
        校验通过时返回 `None`。

    Raises:
        ValueError: 规则引用未知章节、未知条目、marker 为空或 required item 未覆盖时抛出。
    """

    manifest = load_template_contract_manifest()
    _validate_required_item_rules(rules.required_items, manifest)
    _validate_forbidden_content_rules(rules.forbidden_contents, manifest)


def _validate_required_item_rules(
    rules: tuple[ContractRequiredItemRule, ...],
    manifest: TemplateContractManifest,
) -> None:
    """校验 required_output_items marker 规则。

    Args:
        rules: required item 规则。
        manifest: 模板契约清单。

    Returns:
        校验通过时返回 `None`。

    Raises:
        ValueError: 规则无效或 manifest required item 未覆盖时抛出。
    """

    manifest_items = {
        (chapter.chapter_id, item)
        for chapter in manifest.chapters
        for item in chapter.required_output_items
    }
    rule_items = set()
    for rule in rules:
        if not rule.markers_any:
            raise ValueError(f"required item marker 不能为空：chapter_id={rule.chapter_id}, item={rule.item_text}")
        key = (rule.chapter_id, rule.item_text)
        if key not in manifest_items:
            raise ValueError(f"required item 规则未匹配 manifest：chapter_id={rule.chapter_id}, item={rule.item_text}")
        rule_items.add(key)

    missing_items = manifest_items - rule_items
    if missing_items:
        missing_text = "、".join(f"{chapter_id}:{item}" for chapter_id, item in sorted(missing_items))
        raise ValueError(f"required_output_items 未被程序规则覆盖：{missing_text}")


def _validate_forbidden_content_rules(
    rules: tuple[ContractForbiddenContentRule, ...],
    manifest: TemplateContractManifest,
) -> None:
    """校验 must_not_cover forbidden marker 规则。

    Args:
        rules: forbidden content 规则。
        manifest: 模板契约清单。

    Returns:
        校验通过时返回 `None`。

    Raises:
        ValueError: 规则无效时抛出。
    """

    manifest_items = {
        (chapter.chapter_id, item)
        for chapter in manifest.chapters
        for item in chapter.must_not_cover
    }
    for rule in rules:
        if not rule.forbidden_markers_any:
            raise ValueError(f"forbidden marker 不能为空：chapter_id={rule.chapter_id}, item={rule.item_text}")
        key = (rule.chapter_id, rule.item_text)
        if key not in manifest_items:
            raise ValueError(f"forbidden 规则未匹配 manifest：chapter_id={rule.chapter_id}, item={rule.item_text}")
