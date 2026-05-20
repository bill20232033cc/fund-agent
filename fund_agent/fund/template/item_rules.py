"""基金分析模板 ITEM_RULE 机器契约。

本模块在 Capability 层维护模板第 1/2 章中当前已声明的 ITEM_RULE。
规则只表达确定性的 optional / conditional 渲染策略，不调用 LLM、不解析
基金文档，也不接入程序审计或质量门禁。
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final, Literal, get_args

from fund_agent.fund.fund_type import FundType
from fund_agent.fund.template.contracts import load_template_contract_manifest

TemplateItemRuleMode = Literal["optional", "conditional"]
TemplateItemRuleMissingBehavior = Literal["render_unavailable", "delete_segment"]
TemplateItemRuleDecisionStatus = Literal["render", "delete"]

_TEMPLATE_ID: Final[str] = "fund-analysis-template-v1"
_SOURCE_PATH: Final[str] = "docs/fund-analysis-template-draft.md"
_SUPPORTED_FUND_TYPES: Final[tuple[FundType, ...]] = get_args(FundType)
_SUPPORTED_MODES: Final[frozenset[str]] = frozenset(("optional", "conditional"))
_SUPPORTED_MISSING_BEHAVIORS: Final[frozenset[str]] = frozenset(
    ("render_unavailable", "delete_segment")
)
_BUILT_IN_RULE_IDS: Final[tuple[str, ...]] = (
    "chapter_1_index_constituents",
    "chapter_1_manager_philosophy",
    "chapter_2_alpha_yearly_breakdown",
    "chapter_2_tracking_error_analysis",
)
_FORBIDDEN_SEGMENT_MARKERS: Final[frozenset[str]] = frozenset(
    ("跟踪指数", "投资哲学", "选股标准", "超额收益稳定性", "日均偏离度")
)

_FACET_FUND_TYPE_MAP: Final[dict[str, FundType]] = {
    "宽基指数基金": "index_fund",
    "行业/主题指数基金": "index_fund",
    "策略指数基金": "index_fund",
    "指数增强基金": "enhanced_index",
    "主动权益基金（价值风格）": "active_fund",
    "主动权益基金（均衡风格）": "active_fund",
    "主动权益基金（成长风格）": "active_fund",
    "债券基金": "bond_fund",
    "纯债基金": "bond_fund",
    "混合债基金": "bond_fund",
    "二级债基/混合债基": "bond_fund",
    "偏债混合基金": "bond_fund",
    "QDII基金": "qdii_fund",
    "QDII 基金": "qdii_fund",
    "境外权益基金": "qdii_fund",
    "FOF基金": "fof_fund",
    "FOF 基金": "fof_fund",
    "基金中基金": "fof_fund",
}


@dataclass(frozen=True, slots=True)
class TemplateItemRule:
    """模板单条 ITEM_RULE。

    Attributes:
        rule_id: 稳定规则编号。
        chapter_id: 模板章节编号，必须指向已存在的 CHAPTER_CONTRACT。
        item_title: 模板 ITEM_RULE 对应的条目标题。
        mode: 条目渲染模式，支持 `optional` 与 `conditional`。
        when_text: 模板草稿中的适用条件原文。
        facets_any: 模板草稿声明的任一适用细分标签。
        fund_types_any: 由细分标签确定性映射出的任一标准基金类型。
        segment_markers_any: 用于定位已渲染段落的唯一小节标记。
        missing_behavior: 未满足条件或数据缺失时的渲染策略。
    """

    rule_id: str
    chapter_id: int
    item_title: str
    mode: TemplateItemRuleMode
    when_text: str
    facets_any: tuple[str, ...]
    fund_types_any: tuple[FundType, ...]
    segment_markers_any: tuple[str, ...]
    missing_behavior: TemplateItemRuleMissingBehavior


@dataclass(frozen=True, slots=True)
class TemplateItemRuleManifest:
    """模板 ITEM_RULE 清单。

    Attributes:
        template_id: 模板规则清单标识。
        source_path: 人工维护 ITEM_RULE 文本的来源文档路径。
        rules: 当前模板声明的 ITEM_RULE 列表。
    """

    template_id: str
    source_path: str
    rules: tuple[TemplateItemRule, ...]


@dataclass(frozen=True, slots=True)
class TemplateItemRuleDecision:
    """模板 ITEM_RULE 的确定性评估结果。

    Attributes:
        rule_id: 被评估的规则编号。
        chapter_id: 规则所属模板章节编号。
        item_title: 规则对应的条目标题。
        mode: 规则渲染模式。
        triggered: 当前基金类型或显式细分标签是否触发规则。
        status: 当前规则要求渲染还是删除段落。
        missing_behavior: 未满足条件或数据缺失时的渲染策略。
        reason: 供测试与审计调用方理解的确定性原因说明。
    """

    rule_id: str
    chapter_id: int
    item_title: str
    mode: TemplateItemRuleMode
    triggered: bool
    status: TemplateItemRuleDecisionStatus
    missing_behavior: TemplateItemRuleMissingBehavior
    reason: str


_MANIFEST: Final[TemplateItemRuleManifest] = TemplateItemRuleManifest(
    template_id=_TEMPLATE_ID,
    source_path=_SOURCE_PATH,
    rules=(
        TemplateItemRule(
            rule_id="chapter_1_index_constituents",
            chapter_id=1,
            item_title="指数编制规则与成分股",
            mode="conditional",
            when_text="仅对指数基金（含指数增强）输出",
            facets_any=("宽基指数基金", "行业/主题指数基金", "策略指数基金", "指数增强基金"),
            fund_types_any=("index_fund", "enhanced_index"),
            segment_markers_any=("#### 指数编制规则与成分股", "指数编制规则与成分股（仅指数基金）"),
            missing_behavior="delete_segment",
        ),
        TemplateItemRule(
            rule_id="chapter_1_manager_philosophy",
            chapter_id=1,
            item_title="基金经理投资哲学",
            mode="conditional",
            when_text="仅对主动基金输出",
            facets_any=(
                "主动权益基金（价值风格）",
                "主动权益基金（均衡风格）",
                "主动权益基金（成长风格）",
            ),
            fund_types_any=("active_fund",),
            segment_markers_any=("#### 基金经理投资哲学", "基金经理投资哲学（仅主动基金）"),
            missing_behavior="delete_segment",
        ),
        TemplateItemRule(
            rule_id="chapter_2_alpha_yearly_breakdown",
            chapter_id=2,
            item_title="超额收益分年度拆解",
            mode="conditional",
            when_text="对主动基金和指数增强基金输出；纯指数基金跳过此项",
            facets_any=(
                "主动权益基金（价值风格）",
                "主动权益基金（均衡风格）",
                "主动权益基金（成长风格）",
                "指数增强基金",
            ),
            fund_types_any=("active_fund", "enhanced_index"),
            segment_markers_any=("#### 超额收益分年度拆解", "超额收益分年度拆解（仅主动基金和指数增强）"),
            missing_behavior="delete_segment",
        ),
        TemplateItemRule(
            rule_id="chapter_2_tracking_error_analysis",
            chapter_id=2,
            item_title="跟踪误差分析",
            mode="conditional",
            when_text="仅对指数基金（含指数增强）输出",
            facets_any=("宽基指数基金", "行业/主题指数基金", "策略指数基金", "指数增强基金"),
            fund_types_any=("index_fund", "enhanced_index"),
            segment_markers_any=("#### 跟踪误差分析", "跟踪误差分析（仅指数基金）"),
            missing_behavior="delete_segment",
        ),
    ),
)


def load_template_item_rule_manifest() -> TemplateItemRuleManifest:
    """读取基金分析模板 ITEM_RULE 清单。

    Returns:
        当前内置的 `TemplateItemRuleManifest`。

    Raises:
        ValueError: 内置清单不满足 fail-closed 校验时抛出。
    """

    validate_template_item_rule_manifest(_MANIFEST)
    return _MANIFEST


def get_template_item_rule(rule_id: str) -> TemplateItemRule:
    """按规则编号读取模板 ITEM_RULE。

    Args:
        rule_id: 稳定规则编号。

    Returns:
        对应的 `TemplateItemRule`。

    Raises:
        ValueError: 规则编号不存在或内置清单校验失败时抛出。
    """

    manifest = load_template_item_rule_manifest()
    for rule in manifest.rules:
        if rule.rule_id == rule_id:
            return rule
    raise ValueError(f"未找到模板 ITEM_RULE：rule_id={rule_id}")


def validate_template_item_rule_manifest(manifest: TemplateItemRuleManifest) -> None:
    """校验模板 ITEM_RULE 清单是否满足 fail-closed 约束。

    Args:
        manifest: 待校验的 ITEM_RULE 清单。

    Returns:
        校验通过时返回 `None`。

    Raises:
        ValueError: 清单元数据、规则编号、章节、模式、基金类型、facet 或段落标记无效时抛出。
    """

    if not manifest.template_id.strip():
        raise ValueError("template_id 不能为空")
    if not manifest.source_path.strip():
        raise ValueError("source_path 不能为空")

    rule_ids = tuple(rule.rule_id for rule in manifest.rules)
    if len(set(rule_ids)) != len(rule_ids):
        raise ValueError("ITEM_RULE rule_id 存在重复")

    known_chapter_ids = {chapter.chapter_id for chapter in load_template_contract_manifest().chapters}
    for rule in manifest.rules:
        _validate_template_item_rule(rule, known_chapter_ids)

    if _is_builtin_manifest(manifest):
        _validate_builtin_manifest_rule_ids(rule_ids)


def evaluate_template_item_rule(
    rule: TemplateItemRule,
    *,
    fund_type: FundType,
    facets: tuple[str, ...] = (),
) -> TemplateItemRuleDecision:
    """按基金类型和显式 facet 评估单条 ITEM_RULE。

    Args:
        rule: 待评估的 ITEM_RULE。
        fund_type: 已完成基金类型识别后的标准基金类型。
        facets: 调用方显式提供的细分标签；本函数不会从文本中推断 facet。

    Returns:
        确定性的 `TemplateItemRuleDecision`。

    Raises:
        ValueError: 基金类型不受支持、显式 facet 与基金类型冲突，或规则本身无效时抛出。
    """

    _validate_fund_type(fund_type)
    _validate_template_item_rule(rule, {chapter.chapter_id for chapter in load_template_contract_manifest().chapters})
    supported_facets = _validate_explicit_facets(fund_type, facets)

    # 基金类型判断优先；facet 只能作为显式且兼容的补充触发信号。
    fund_type_matched = fund_type in rule.fund_types_any
    facet_matched = any(facet in rule.facets_any for facet in supported_facets)
    triggered = fund_type_matched or facet_matched

    if triggered:
        reason = _render_triggered_reason(
            fund_type=fund_type,
            fund_type_matched=fund_type_matched,
            facet_matched=facet_matched,
            supported_facets=supported_facets,
        )
        return _decision(rule, triggered=True, status="render", reason=reason)

    if rule.mode == "conditional":
        reason = f"基金类型 {fund_type} 和显式 facet 均未触发条件，按 conditional 删除段落"
        return _decision(rule, triggered=False, status="delete", reason=reason)

    reason = f"基金类型 {fund_type} 和显式 facet 均未触发条件，按 optional 渲染不可用占位"
    return _decision(rule, triggered=False, status="render", reason=reason)


def evaluate_template_item_rules(
    *,
    fund_type: FundType,
    facets: tuple[str, ...] = (),
) -> tuple[TemplateItemRuleDecision, ...]:
    """评估内置清单中的全部 ITEM_RULE。

    Args:
        fund_type: 已完成基金类型识别后的标准基金类型。
        facets: 调用方显式提供的细分标签；本函数不会从文本中推断 facet。

    Returns:
        与内置规则顺序一致的 `TemplateItemRuleDecision` 元组。

    Raises:
        ValueError: 基金类型不受支持、显式 facet 与基金类型冲突，或内置清单无效时抛出。
    """

    manifest = load_template_item_rule_manifest()
    return tuple(evaluate_template_item_rule(rule, fund_type=fund_type, facets=facets) for rule in manifest.rules)


def rendered_segment_present(markdown: str, rule: TemplateItemRule) -> bool:
    """判断渲染后的 Markdown 是否包含某条 ITEM_RULE 的唯一段落标记。

    Args:
        markdown: 已渲染的报告 Markdown。
        rule: 待检查的 ITEM_RULE。

    Returns:
        任一 `segment_markers_any` 以字面量方式出现时返回 `True`，否则返回 `False`。

    Raises:
        ValueError: 规则没有配置段落标记时抛出。
    """

    if not rule.segment_markers_any:
        raise ValueError("segment_markers_any 不能为空")
    return any(marker in markdown for marker in rule.segment_markers_any)


def _validate_template_item_rule(rule: TemplateItemRule, known_chapter_ids: set[int]) -> None:
    """校验单条 ITEM_RULE。

    Args:
        rule: 待校验规则。
        known_chapter_ids: CHAPTER_CONTRACT 已知章节编号集合。

    Returns:
        校验通过时返回 `None`。

    Raises:
        ValueError: 任一规则字段不满足 fail-closed 约束时抛出。
    """

    if not rule.rule_id.strip():
        raise ValueError("ITEM_RULE rule_id 不能为空")
    if rule.chapter_id not in known_chapter_ids:
        raise ValueError(f"ITEM_RULE 指向未知章节：chapter_id={rule.chapter_id}")
    if not rule.item_title.strip():
        raise ValueError(f"ITEM_RULE {rule.rule_id} item_title 不能为空")
    if rule.mode not in _SUPPORTED_MODES:
        raise ValueError(f"ITEM_RULE {rule.rule_id} mode 不受支持：{rule.mode}")
    if rule.missing_behavior not in _SUPPORTED_MISSING_BEHAVIORS:
        raise ValueError(f"ITEM_RULE {rule.rule_id} missing_behavior 不受支持：{rule.missing_behavior}")
    if rule.mode == "conditional" and rule.missing_behavior != "delete_segment":
        raise ValueError(f"ITEM_RULE {rule.rule_id} conditional 必须 delete_segment")
    if rule.mode == "optional" and rule.missing_behavior != "render_unavailable":
        raise ValueError(f"ITEM_RULE {rule.rule_id} optional 必须 render_unavailable")
    if rule.mode == "conditional" and not rule.facets_any:
        raise ValueError(f"ITEM_RULE {rule.rule_id} conditional facets_any 不能为空")
    if not rule.fund_types_any:
        raise ValueError(f"ITEM_RULE {rule.rule_id} fund_types_any 不能为空")
    _validate_rule_fund_types(rule)
    _validate_rule_facets(rule)
    _validate_rule_segment_markers(rule)


def _validate_rule_fund_types(rule: TemplateItemRule) -> None:
    """校验规则配置的基金类型。

    Args:
        rule: 待校验规则。

    Returns:
        校验通过时返回 `None`。

    Raises:
        ValueError: 基金类型不受支持时抛出。
    """

    for fund_type in rule.fund_types_any:
        _validate_fund_type(fund_type)


def _validate_rule_facets(rule: TemplateItemRule) -> None:
    """校验规则配置的 facet 与基金类型映射一致。

    Args:
        rule: 待校验规则。

    Returns:
        校验通过时返回 `None`。

    Raises:
        ValueError: facet 不受支持或映射基金类型未列入规则触发类型时抛出。
    """

    for facet in rule.facets_any:
        if facet not in _FACET_FUND_TYPE_MAP:
            raise ValueError(f"ITEM_RULE {rule.rule_id} facet 不受支持：{facet}")
        mapped_fund_type = _FACET_FUND_TYPE_MAP[facet]
        if mapped_fund_type not in rule.fund_types_any:
            raise ValueError(
                f"ITEM_RULE {rule.rule_id} facet {facet} 映射到 {mapped_fund_type}，"
                "但 fund_types_any 未包含该类型"
            )


def _validate_rule_segment_markers(rule: TemplateItemRule) -> None:
    """校验规则配置的段落定位标记。

    Args:
        rule: 待校验规则。

    Returns:
        校验通过时返回 `None`。

    Raises:
        ValueError: 段落标记为空或使用普通正文短语时抛出。
    """

    if not rule.segment_markers_any:
        raise ValueError(f"ITEM_RULE {rule.rule_id} segment_markers_any 不能为空")
    for marker in rule.segment_markers_any:
        if not marker.strip():
            raise ValueError(f"ITEM_RULE {rule.rule_id} segment marker 不能为空")
        if marker in _FORBIDDEN_SEGMENT_MARKERS:
            raise ValueError(f"ITEM_RULE {rule.rule_id} segment marker 不能使用普通正文短语：{marker}")


def _validate_fund_type(fund_type: object) -> None:
    """校验基金类型是否为当前标准类型。

    Args:
        fund_type: 待校验基金类型。

    Returns:
        校验通过时返回 `None`。

    Raises:
        ValueError: 基金类型不受支持时抛出。
    """

    if fund_type not in _SUPPORTED_FUND_TYPES:
        raise ValueError(f"不支持的基金类型：{fund_type}")


def _validate_explicit_facets(fund_type: FundType, facets: tuple[str, ...]) -> tuple[str, ...]:
    """校验显式 facet 与已识别基金类型是否相容。

    Args:
        fund_type: 已识别基金类型。
        facets: 调用方显式传入的细分标签。

    Returns:
        当前实现支持且与基金类型相容的 facet 元组。

    Raises:
        ValueError: 任一已知 facet 与基金类型冲突时抛出。
    """

    supported_facets: list[str] = []
    for facet in facets:
        mapped_fund_type = _FACET_FUND_TYPE_MAP.get(facet)
        if mapped_fund_type is None:
            continue
        if mapped_fund_type != fund_type:
            raise ValueError(f"显式 facet {facet} 与基金类型 {fund_type} 冲突")
        supported_facets.append(facet)
    return tuple(supported_facets)


def _render_triggered_reason(
    *,
    fund_type: FundType,
    fund_type_matched: bool,
    facet_matched: bool,
    supported_facets: tuple[str, ...],
) -> str:
    """生成规则触发原因说明。

    Args:
        fund_type: 当前基金类型。
        fund_type_matched: 基金类型是否直接命中规则。
        facet_matched: 显式 facet 是否命中规则。
        supported_facets: 已验证相容的显式 facet。

    Returns:
        确定性触发原因说明。

    Raises:
        无显式抛出。
    """

    if fund_type_matched and facet_matched:
        return f"基金类型 {fund_type} 与显式 facet {supported_facets} 均触发规则"
    if fund_type_matched:
        return f"基金类型 {fund_type} 触发规则"
    return f"显式 facet {supported_facets} 触发规则"


def _decision(
    rule: TemplateItemRule,
    *,
    triggered: bool,
    status: TemplateItemRuleDecisionStatus,
    reason: str,
) -> TemplateItemRuleDecision:
    """构造 ITEM_RULE 评估结果。

    Args:
        rule: 被评估的 ITEM_RULE。
        triggered: 规则是否被触发。
        status: 渲染或删除段落的决策。
        reason: 决策原因说明。

    Returns:
        构造后的 `TemplateItemRuleDecision`。

    Raises:
        无显式抛出。
    """

    return TemplateItemRuleDecision(
        rule_id=rule.rule_id,
        chapter_id=rule.chapter_id,
        item_title=rule.item_title,
        mode=rule.mode,
        triggered=triggered,
        status=status,
        missing_behavior=rule.missing_behavior,
        reason=reason,
    )


def _is_builtin_manifest(manifest: TemplateItemRuleManifest) -> bool:
    """判断清单是否为当前内置模板 ITEM_RULE manifest。

    Args:
        manifest: 待判断的 ITEM_RULE 清单。

    Returns:
        元数据匹配当前内置 manifest 时返回 `True`。

    Raises:
        无显式抛出。
    """

    return manifest.template_id == _TEMPLATE_ID and manifest.source_path == _SOURCE_PATH


def _validate_builtin_manifest_rule_ids(rule_ids: tuple[str, ...]) -> None:
    """校验内置 ITEM_RULE 是否只包含当前模板草稿声明的四条规则。

    Args:
        rule_ids: 内置清单中的规则编号序列。

    Returns:
        校验通过时返回 `None`。

    Raises:
        ValueError: 内置规则缺失、增加或顺序漂移时抛出。
    """

    if rule_ids != _BUILT_IN_RULE_IDS:
        raise ValueError("内置 ITEM_RULE 必须且只能包含当前模板草稿声明的四条规则")
