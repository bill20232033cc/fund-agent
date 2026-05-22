"""CHAPTER_CONTRACT 审计规则与覆盖路由。

本模块属于基金 Capability 层，服务 `docs/design.md` 第 5.2 节的确定性 C2 审计。
它维护 manifest 到确定性程序审计 marker 的显式映射，也维护 must_answer 到后续审计层的覆盖路由。
本模块只做规则声明和 fail-closed 校验，不执行 LLM 判断、语义推断或证据复核。
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final, Literal

from fund_agent.fund.template.contracts import TemplateContractManifest, load_template_contract_manifest

MustAnswerCoverageKind = Literal[
    "covered_by_required_item",
    "programmatic_marker",
    "structured_data_availability",
    "llm_semantic_audit",
    "evidence_confirm",
    "narrative_guidance",
]

_MUST_ANSWER_COVERAGE_KINDS: Final[frozenset[str]] = frozenset(
    (
        "covered_by_required_item",
        "programmatic_marker",
        "structured_data_availability",
        "llm_semantic_audit",
        "evidence_confirm",
        "narrative_guidance",
    )
)

MustNotCoverCoverageKind = Literal[
    "narrative_guidance",
]

_MUST_NOT_COVER_COVERAGE_KINDS: Final[frozenset[str]] = frozenset(("narrative_guidance",))


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
class ContractMustAnswerCoverageRule:
    """模板 must_answer 的审计覆盖路由规则。

    Attributes:
        chapter_id: 模板章节编号。
        question_text: manifest 中的 must_answer 原文。
        coverage_kind: 当前问题的审计覆盖类型。
        required_item_texts: 当 `coverage_kind` 为 `covered_by_required_item` 时，
            用于证明该问题至少有显式输出位置的 required_output_items 原文列表。
        markers_any: 当 `coverage_kind` 为 `programmatic_marker` 时，任一出现即可判定该问题有显式 marker。
        rationale: 非程序化覆盖或复合映射的说明。
    """

    chapter_id: int
    question_text: str
    coverage_kind: MustAnswerCoverageKind
    required_item_texts: tuple[str, ...] = ()
    markers_any: tuple[str, ...] = ()
    rationale: str = ""


@dataclass(frozen=True, slots=True)
class ContractMustNotCoverCoverageRule:
    """模板 must_not_cover 的非程序化覆盖路由规则。

    Attributes:
        chapter_id: 模板章节编号。
        item_text: manifest 中的 must_not_cover 原文。
        coverage_kind: 当前禁止项的非程序化覆盖类型。
        rationale: 非程序化覆盖说明；用于声明为什么不能靠字面 marker 稳定证明。
    """

    chapter_id: int
    item_text: str
    coverage_kind: MustNotCoverCoverageKind
    rationale: str


@dataclass(frozen=True, slots=True)
class ContractAuditCoverageManifest:
    """CHAPTER_CONTRACT 审计覆盖路由清单。

    Attributes:
        must_answer_coverages: 每条 must_answer 的显式覆盖路由。
        must_not_cover_coverages: 无法用 forbidden marker 稳定审计的 must_not_cover 覆盖路由。
    """

    must_answer_coverages: tuple[ContractMustAnswerCoverageRule, ...]
    must_not_cover_coverages: tuple[ContractMustNotCoverCoverageRule, ...] = ()


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
    ContractRequiredItemRule(0, "一句话这是什么基金", ("这是什么基金：",)),
    ContractRequiredItemRule(0, "基金简介", ("基金简介：",)),
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

_MUST_NOT_COVER_COVERAGE_RULES: Final[tuple[ContractMustNotCoverCoverageRule, ...]] = (
    ContractMustNotCoverCoverageRule(
        0,
        "不把本章写成后续章节的摘要、材料摘抄、按顺序复述，或信息罗列式导读。",
        "narrative_guidance",
        "这是第 0 章封面叙事约束，不能靠稳定字面 marker 完整判定，只能由后续语义审计或人工复核覆盖。",
    ),
    ContractMustNotCoverCoverageRule(
        0,
        "不把“基金简介 / 业绩概览 / 风险提示”拆成并列分栏。",
        "narrative_guidance",
        "这是第 0 章版式约束；当前 renderer 使用线性封面 bullet，C2 不用单一 forbidden marker 证明全部分栏形态。",
    ),
    ContractMustNotCoverCoverageRule(
        0,
        "不把本章写成优点/缺点清单、投资亮点清单。",
        "narrative_guidance",
        "这是第 0 章表达形态约束，标题和同义表达不稳定，保留为非程序化覆盖。",
    ),
    ContractMustNotCoverCoverageRule(
        0,
        "不把“最主要的理由”写成多条优点堆砌；默认只保留 1 条。",
        "narrative_guidance",
        "这是数量和语义压缩约束，当前 C2 marker 只能定位输出项，不能证明理由是否堆砌。",
    ),
    ContractMustNotCoverCoverageRule(
        0,
        "不把“最大风险”写成并列风险列表；默认只写一个主要风险。",
        "narrative_guidance",
        "这是数量和语义压缩约束，当前 C2 marker 只能定位输出项，不能证明是否并列罗列。",
    ),
    ContractMustNotCoverCoverageRule(
        0,
        "不把“下一步最小验证问题”写成愿望清单；默认先写 1 个。",
        "narrative_guidance",
        "这是验证问题的语义质量约束，不能靠固定 forbidden marker 稳定覆盖。",
    ),
    ContractMustNotCoverCoverageRule(
        0,
        "不把本章拆成“结论要点 / 详细情况 / 证据与出处”三段结构；第 0 章是封面页。",
        "narrative_guidance",
        "这是第 0 章章节结构约束，其中“证据与出处”由程序规则覆盖，其余分段形态由非程序化覆盖。",
    ),
    ContractMustNotCoverCoverageRule(
        1,
        "不展开基金经理选股能力的分析（属于第 3 章）。",
        "narrative_guidance",
        "这是跨章节职责边界，不能靠单一字面 marker 判断是否展开选股能力分析。",
    ),
    ContractMustNotCoverCoverageRule(
        1,
        "不展开收益率的详细计算（属于第 2 章）。",
        "narrative_guidance",
        "这是跨章节职责边界，收益率计算存在多种表达，保留为非程序化覆盖。",
    ),
    ContractMustNotCoverCoverageRule(
        1,
        "不分析市场竞争或同业比较（属于横向比较模块，不在本报告范围内）。",
        "narrative_guidance",
        "这是报告范围约束，同义表达不稳定，保留为非程序化覆盖。",
    ),
    ContractMustNotCoverCoverageRule(
        2,
        "不展开基金经理选股能力的详细归因（属于第 3 章）。",
        "narrative_guidance",
        "这是模板第 2/3 章职责边界，不能靠固定 forbidden marker 完整判定。",
    ),
    ContractMustNotCoverCoverageRule(
        2,
        "不展开市场走势分析（不属于本报告范围）。",
        "narrative_guidance",
        "这是报告范围约束；“市场走势分析”同义表达较多，保留为非程序化覆盖。",
    ),
    ContractMustNotCoverCoverageRule(
        3,
        "不展开选股能力的量化分析（属于第 2 章超额收益范畴）。",
        "narrative_guidance",
        "这是模板第 2/3 章职责边界，不能靠固定 forbidden marker 完整判定。",
    ),
    ContractMustNotCoverCoverageRule(
        5,
        "不罗列所有变化，只保留最关键的 1-3 个。",
        "narrative_guidance",
        "这是数量和重要性排序约束，C2 marker 不能证明是否罗列了所有变化。",
    ),
    ContractMustNotCoverCoverageRule(
        5,
        "不给最终持有/替换结论。",
        "narrative_guidance",
        "这是第 5 章跨章节职责约束，具体最终判断词与上下文相关，保留为非程序化覆盖。",
    ),
    ContractMustNotCoverCoverageRule(
        5,
        "不展开风险清单；变化事实只有转译为风险或否决项时才进入第 6 章。",
        "narrative_guidance",
        "这是第 5/6 章职责边界，不能靠单一 forbidden marker 完整判定风险清单形态。",
    ),
    ContractMustNotCoverCoverageRule(
        5,
        "不重复基金经理长期画像或成本收益总评。",
        "narrative_guidance",
        "这是重复内容约束，依赖上下文比较，保留为非程序化覆盖。",
    ),
    ContractMustNotCoverCoverageRule(
        6,
        "不把本章写成所有可能风险的罗列。",
        "narrative_guidance",
        "这是第 6 章风险筛选语义约束，不能靠固定 marker 判定是否穷举罗列。",
    ),
    ContractMustNotCoverCoverageRule(
        6,
        "不把“最大风险”写成并列列表；默认只写 1 个最致命的。",
        "narrative_guidance",
        "这是数量和语义压缩约束，当前 C2 marker 不能证明是否并列罗列。",
    ),
    ContractMustNotCoverCoverageRule(
        6,
        "不复述当前阶段事实，除非明确转译为风险、压力测试或否决项。",
        "narrative_guidance",
        "这是第 5/6 章职责边界，是否复述依赖上下文比较，保留为非程序化覆盖。",
    ),
    ContractMustNotCoverCoverageRule(
        6,
        "不给最终持有/替换结论。",
        "narrative_guidance",
        "这是第 6/7 章职责边界，具体最终判断词与上下文相关，保留为非程序化覆盖。",
    ),
    ContractMustNotCoverCoverageRule(
        6,
        "不预测收益或市场走势。",
        "narrative_guidance",
        "这是复合禁止项；未来收益由第 2 章程序规则覆盖，市场走势部分保留为非程序化覆盖。",
    ),
    ContractMustNotCoverCoverageRule(
        7,
        "不把本章写成前 6 章的摘要复述。",
        "narrative_guidance",
        "这是第 7 章最终判断叙事约束，依赖跨章内容比较，保留为非程序化覆盖。",
    ),
    ContractMustNotCoverCoverageRule(
        7,
        "不把“为什么”写成多条理由堆砌；默认只保留 1-2 条核心依据。",
        "narrative_guidance",
        "这是数量和语义压缩约束，当前 C2 marker 不能证明是否堆砌理由。",
    ),
)

_MUST_ANSWER_COVERAGE_RULES: Final[tuple[ContractMustAnswerCoverageRule, ...]] = (
    ContractMustAnswerCoverageRule(0, "用一句话定义这只基金到底是什么产品。", "covered_by_required_item", ("一句话这是什么基金",)),
    ContractMustAnswerCoverageRule(
        0,
        "给出一个极简基金简介，帮助第一次接触这只基金的读者快速建立产品画像；只保留基金类型、基金经理、管理规模、成立时间中最必要的信息。",
        "covered_by_required_item",
        ("基金简介",),
    ),
    ContractMustAnswerCoverageRule(
        0,
        "回答当前判断应是值得持有、需要关注还是建议替换。",
        "covered_by_required_item",
        ("当前动作（🟢 值得持有 / 🟡 需要关注 / 🔴 建议替换）",),
    ),
    ContractMustAnswerCoverageRule(
        0,
        "回答这只基金当前业绩和运作处在什么状态，但只保留最能支撑当前动作判断的净值表现、超额收益或风险指标。",
        "covered_by_required_item",
        ("当前业绩与运作状态",),
    ),
    ContractMustAnswerCoverageRule(
        0,
        "回答支撑当前动作的最主要理由，默认压缩成 1 条；只有在第二条判断彼此独立且缺一不可时才允许写第 2 条。",
        "covered_by_required_item",
        ("支撑当前动作的最主要理由",),
    ),
    ContractMustAnswerCoverageRule(
        0,
        "回答当前最值得盯住的变量是什么；先点出看这类基金时通常最先要看的东西；如果基金还有一个更能决定整份报告判断的特别情况，就把它放到最前面来写。",
        "covered_by_required_item",
        ("当前最值得盯住的变量",),
    ),
    ContractMustAnswerCoverageRule(0, "回答当前最大的风险是什么，默认只保留一个主要风险。", "covered_by_required_item", ("当前最大的风险",)),
    ContractMustAnswerCoverageRule(0, "回答下一步最小验证问题是什么，默认先写 1 个最关键问题。", "covered_by_required_item", ("下一步最小验证问题",)),
    ContractMustAnswerCoverageRule(
        0,
        "回答什么变化会升级、降级或终止当前动作，优先压缩成 1 个升级阈值和 1 个降级或终止阈值。",
        "covered_by_required_item",
        ("什么变化会升级、降级或终止当前动作",),
    ),
    ContractMustAnswerCoverageRule(1, "用最低认知负担定义这只基金到底是什么产品。", "covered_by_required_item", ("基金类型与分类标签",)),
    ContractMustAnswerCoverageRule(
        1,
        "说明基金的投资目标和投资策略（从招募说明书和年报§2提取）。",
        "covered_by_required_item",
        ("投资目标（一句话）", "投资策略概述"),
        rationale="这是复合问题，必须同时具备投资目标和投资策略两个输出位置。",
    ),
    ContractMustAnswerCoverageRule(1, "说明基金的业绩基准是什么，为什么选这个基准。", "covered_by_required_item", ("业绩基准及合理性",)),
    ContractMustAnswerCoverageRule(1, "说明基金的类型分类（按有知有行三维标签：市值×风格×管理方式）。", "covered_by_required_item", ("基金类型与分类标签",)),
    ContractMustAnswerCoverageRule(1, "回答看这类基金时，通常最先要看什么。", "covered_by_required_item", ("看这类基金最先看什么",)),
    ContractMustAnswerCoverageRule(
        1,
        "如果基金有一个不太符合常规、却会直接改变你对“这是什么产品”理解的特别情况，要说明它为什么重要。",
        "covered_by_required_item",
        ("会改变产品理解的特别情况（如有）",),
    ),
    ContractMustAnswerCoverageRule(2, "近 1 年、3 年、5 年的基金净值增长率（R）。", "covered_by_required_item", ("近 1/3/5 年净值增长率",)),
    ContractMustAnswerCoverageRule(2, "同期业绩基准收益率（B）。", "covered_by_required_item", ("近 1/3/5 年业绩基准收益率",)),
    ContractMustAnswerCoverageRule(2, "计算超额收益（A = R - B）。", "covered_by_required_item", ("超额收益（A = R - B）及稳定性",)),
    ContractMustAnswerCoverageRule(2, "判断超额收益是结构性的还是阶段性的。", "covered_by_required_item", ("超额收益性质判断（结构性 vs 阶段性）",)),
    ContractMustAnswerCoverageRule(2, "拆解成本 C：管理费 + 托管费 + 销售服务费 + 交易成本（估算）。", "covered_by_required_item", ("成本拆解（管理费、托管费、交易成本）",)),
    ContractMustAnswerCoverageRule(
        2,
        "判断超额收益是否为正且稳定、是否覆盖成本。",
        "covered_by_required_item",
        ("超额收益（A = R - B）及稳定性", "R=A+B-C 综合评估"),
        rationale="稳定性由超额收益条目承载，覆盖成本结论由 R=A+B-C 综合评估承载。",
    ),
    ContractMustAnswerCoverageRule(3, "基金经理的基本信息（从业年限、管理本基金时间、管理规模）。", "covered_by_required_item", ("基金经理基本信息",)),
    ContractMustAnswerCoverageRule(3, "基金经理宣称的投资策略和风格（从年报§4提取）。", "covered_by_required_item", ("宣称的投资策略（§4）",)),
    ContractMustAnswerCoverageRule(
        3,
        "基金经理实际的投资行为（从年报§8提取：行业配置、持仓集中度、换手率）。",
        "covered_by_required_item",
        ("实际投资行为（§8）",),
    ),
    ContractMustAnswerCoverageRule(3, "言行一致性判断：说的和做的一样吗？", "covered_by_required_item", ("言行一致性判断",)),
    ContractMustAnswerCoverageRule(3, "风格稳定性判断：跨期风格是否漂移？", "covered_by_required_item", ("风格稳定性判断",)),
    ContractMustAnswerCoverageRule(3, "利益一致性判断：基金经理是否持有本基金？", "covered_by_required_item", ("利益一致性判断",)),
    ContractMustAnswerCoverageRule(4, "基金产品收益（净值增长率）。", "covered_by_required_item", ("基金产品收益 vs 投资者实际收益",)),
    ContractMustAnswerCoverageRule(
        4,
        "投资者实际收益（盈利投资者占比、加权平均收益率）。",
        "covered_by_required_item",
        ("基金产品收益 vs 投资者实际收益", "盈利投资者占比"),
        rationale="投资者实际收益由收益对比条目承载，盈利投资者占比由独立条目承载。",
    ),
    ContractMustAnswerCoverageRule(4, "行为损益 = 投资者实际收益 - 基金产品收益。", "covered_by_required_item", ("行为损益估算",)),
    ContractMustAnswerCoverageRule(4, "份额变动趋势（资金是在追涨还是在抄底？）。", "covered_by_required_item", ("份额变动趋势",)),
    ContractMustAnswerCoverageRule(5, "当前阶段是什么（建仓期/稳定期/膨胀期/萎缩期/转型期）。", "covered_by_required_item", ("基金当前所处阶段",)),
    ContractMustAnswerCoverageRule(
        5,
        "相比上一期或历史，过去一年最关键的 1-3 个变化是什么（基金经理、规模、策略、费率、仓位或大额申赎）。",
        "covered_by_required_item",
        ("过去一年最关键的变化（1-3 个）",),
    ),
    ContractMustAnswerCoverageRule(5, "这些变化是否影响原始投资假设或第 1-4 章判断。", "covered_by_required_item", ("变化是否改变前文判断",)),
    ContractMustAnswerCoverageRule(
        5,
        "为什么偏偏是现在需要关注这只基金。",
        "narrative_guidance",
        rationale="这是第 5 章“当前阶段”叙事约束，当前模板没有独立输出项；C2 marker 不能证明“为什么是现在”的语义质量。",
    ),
    ContractMustAnswerCoverageRule(5, "下一步最小验证问题是什么。", "covered_by_required_item", ("接下来最该跟踪的变量",)),
    ContractMustAnswerCoverageRule(
        6,
        "核心风险是什么，其中哪些是结构性风险、哪些是阶段性风险。",
        "narrative_guidance",
        rationale="这是第 6 章风险分类语义约束，当前模板通过风险条目承载但 C2 marker 不能证明结构性/阶段性分类质量。",
    ),
    ContractMustAnswerCoverageRule(6, "最关键的风险或否决项（1-2 个最致命的风险）。", "covered_by_required_item", ("最关键的风险或否决项",)),
    ContractMustAnswerCoverageRule(6, "为什么足以改变结论——这个风险推翻了哪条核心假设。", "covered_by_required_item", ("为什么足以改变结论",)),
    ContractMustAnswerCoverageRule(6, "是否触发一票否决，还是仍可跟踪。", "covered_by_required_item", ("否决 vs 跟踪判断",)),
    ContractMustAnswerCoverageRule(
        6,
        "压力测试结论是什么。",
        "structured_data_availability",
        rationale="压力测试结果由 TemplateRenderInput.stress_test_result 和第 6 章压力测试段落承载；当前 C2 marker 只验证章节契约 marker，不证明压力测试数值质量。",
    ),
    ContractMustAnswerCoverageRule(6, "哪个信息缺口最可能改变最终判断，下一轮先验证什么。", "covered_by_required_item", ("下一轮先验证什么",)),
    ContractMustAnswerCoverageRule(7, "三选一明确立场：值得持有、需要关注、建议替换。", "covered_by_required_item", ("最终判断（🟢 值得持有 / 🟡 需要关注 / 🔴 建议替换）",)),
    ContractMustAnswerCoverageRule(7, "为什么现在更适合这个判断，而不是另外两个。", "covered_by_required_item", ("支撑判断的核心依据（1-2 条）",)),
    ContractMustAnswerCoverageRule(7, "当前最容易看错的地方是什么。", "covered_by_required_item", ("当前最容易看错的地方",)),
    ContractMustAnswerCoverageRule(7, "下一轮先核实什么（1-2 个最小验证问题）。", "covered_by_required_item", ("下一轮最小验证计划",)),
    ContractMustAnswerCoverageRule(7, "什么变化会升级、降级或终止当前判断。", "covered_by_required_item", ("危级/降级阈值",)),
)


def load_contract_audit_coverage_manifest() -> ContractAuditCoverageManifest:
    """读取 CHAPTER_CONTRACT 审计覆盖路由清单。

    Returns:
        已通过 manifest 校验的审计覆盖路由清单。

    Raises:
        ValueError: 覆盖规则缺失、重复、引用未知条目或类型字段无效时抛出。
    """

    manifest = ContractAuditCoverageManifest(
        must_answer_coverages=_MUST_ANSWER_COVERAGE_RULES,
        must_not_cover_coverages=_MUST_NOT_COVER_COVERAGE_RULES,
    )
    validate_contract_audit_coverage_manifest(manifest)
    return manifest


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
    load_contract_audit_coverage_manifest()
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
    coverage_manifest = load_contract_audit_coverage_manifest()
    _validate_must_not_cover_coverage_rules(
        coverage_manifest,
        manifest,
        rules.forbidden_contents,
    )


def validate_contract_audit_coverage_manifest(
    coverage_manifest: ContractAuditCoverageManifest,
) -> None:
    """校验 CHAPTER_CONTRACT 审计覆盖路由清单。

    Args:
        coverage_manifest: 待校验的 must_answer 覆盖清单。

    Returns:
        校验通过时返回 `None`。

    Raises:
        ValueError: 覆盖规则缺失、重复、引用未知条目或类型字段无效时抛出。
    """

    template_manifest = load_template_contract_manifest()
    manifest_questions = _manifest_must_answer_questions(template_manifest)
    manifest_required_items = _manifest_required_output_items(template_manifest)
    required_rule_items = {(rule.chapter_id, rule.item_text) for rule in _REQUIRED_ITEM_RULES}

    seen_questions: set[tuple[int, str]] = set()
    for rule in coverage_manifest.must_answer_coverages:
        key = (rule.chapter_id, rule.question_text)
        if key in seen_questions:
            raise ValueError(f"must_answer 覆盖规则重复：chapter_id={rule.chapter_id}, question={rule.question_text}")
        seen_questions.add(key)
        if key not in manifest_questions:
            raise ValueError(f"must_answer 覆盖规则未匹配 manifest：chapter_id={rule.chapter_id}, question={rule.question_text}")
        _validate_must_answer_coverage_rule(rule, manifest_required_items, required_rule_items)

    missing_questions = manifest_questions - seen_questions
    if missing_questions:
        missing_text = "、".join(f"{chapter_id}:{question}" for chapter_id, question in sorted(missing_questions))
        raise ValueError(f"must_answer 未被覆盖规则覆盖：{missing_text}")

    _validate_must_not_cover_coverage_rules(coverage_manifest, template_manifest)


def _manifest_must_answer_questions(
    manifest: TemplateContractManifest,
) -> set[tuple[int, str]]:
    """提取模板中的 must_answer 问题集合。

    Args:
        manifest: 模板契约清单。

    Returns:
        `(chapter_id, question_text)` 集合。

    Raises:
        无显式抛出。
    """

    return {
        (chapter.chapter_id, question)
        for chapter in manifest.chapters
        for question in chapter.must_answer
    }


def _manifest_required_output_items(
    manifest: TemplateContractManifest,
) -> set[tuple[int, str]]:
    """提取模板中的 required_output_items 集合。

    Args:
        manifest: 模板契约清单。

    Returns:
        `(chapter_id, item_text)` 集合。

    Raises:
        无显式抛出。
    """

    return {
        (chapter.chapter_id, item)
        for chapter in manifest.chapters
        for item in chapter.required_output_items
    }


def _manifest_must_not_cover_items(
    manifest: TemplateContractManifest,
) -> set[tuple[int, str]]:
    """提取模板中的 must_not_cover 禁止项集合。

    Args:
        manifest: 模板契约清单。

    Returns:
        `(chapter_id, item_text)` 集合。

    Raises:
        无显式抛出。
    """

    return {
        (chapter.chapter_id, item)
        for chapter in manifest.chapters
        for item in chapter.must_not_cover
    }


def _validate_must_not_cover_coverage_rules(
    coverage_manifest: ContractAuditCoverageManifest,
    template_manifest: TemplateContractManifest,
    forbidden_content_rules: tuple[ContractForbiddenContentRule, ...] = _FORBIDDEN_CONTENT_RULES,
) -> None:
    """校验 must_not_cover 的反向完整覆盖。

    Args:
        coverage_manifest: 审计覆盖路由清单。
        template_manifest: 模板契约清单。
        forbidden_content_rules: 当前程序 forbidden marker 规则集合。

    Returns:
        校验通过时返回 `None`。

    Raises:
        ValueError: 禁止项缺失覆盖、重复覆盖、引用未知条目或覆盖类型非法时抛出。
    """

    manifest_items = _manifest_must_not_cover_items(template_manifest)
    programmatic_items = {
        (rule.chapter_id, rule.item_text)
        for rule in forbidden_content_rules
    }
    seen_items: set[tuple[int, str]] = set()
    for rule in coverage_manifest.must_not_cover_coverages:
        key = (rule.chapter_id, rule.item_text)
        if key in seen_items:
            raise ValueError(f"must_not_cover 覆盖规则重复：chapter_id={rule.chapter_id}, item={rule.item_text}")
        seen_items.add(key)
        if key not in manifest_items:
            raise ValueError(f"must_not_cover 覆盖规则未匹配 manifest：chapter_id={rule.chapter_id}, item={rule.item_text}")
        _validate_must_not_cover_coverage_rule(rule)

    overlap_items = programmatic_items & seen_items
    if overlap_items:
        overlap_text = "、".join(f"{chapter_id}:{item}" for chapter_id, item in sorted(overlap_items))
        raise ValueError(f"must_not_cover 同时声明程序规则和非程序覆盖：{overlap_text}")

    covered_items = programmatic_items | seen_items
    missing_items = manifest_items - covered_items
    if missing_items:
        missing_text = "、".join(f"{chapter_id}:{item}" for chapter_id, item in sorted(missing_items))
        raise ValueError(f"must_not_cover 未被覆盖规则覆盖：{missing_text}")


def _validate_must_not_cover_coverage_rule(rule: ContractMustNotCoverCoverageRule) -> None:
    """校验单条 must_not_cover 非程序化覆盖规则。

    Args:
        rule: 待校验的 must_not_cover 覆盖规则。

    Returns:
        校验通过时返回 `None`。

    Raises:
        ValueError: 覆盖类型非法或缺少 rationale 时抛出。
    """

    if rule.coverage_kind not in _MUST_NOT_COVER_COVERAGE_KINDS:
        raise ValueError(f"未知 must_not_cover 覆盖类型：{rule.coverage_kind}")
    if not rule.rationale:
        raise ValueError(f"非程序化 must_not_cover 覆盖必须声明 rationale：chapter_id={rule.chapter_id}")


def _validate_must_answer_coverage_rule(
    rule: ContractMustAnswerCoverageRule,
    manifest_required_items: set[tuple[int, str]],
    required_rule_items: set[tuple[int, str]],
) -> None:
    """校验单条 must_answer 覆盖规则。

    Args:
        rule: 待校验的 must_answer 覆盖规则。
        manifest_required_items: 模板 required_output_items 集合。
        required_rule_items: 已配置确定性 marker 的 required_output_items 集合。

    Returns:
        校验通过时返回 `None`。

    Raises:
        ValueError: 覆盖类型、marker 或 required item 映射无效时抛出。
    """

    if rule.coverage_kind not in _MUST_ANSWER_COVERAGE_KINDS:
        raise ValueError(f"未知 must_answer 覆盖类型：{rule.coverage_kind}")
    if rule.coverage_kind == "covered_by_required_item":
        _validate_required_item_coverage_rule(rule, manifest_required_items, required_rule_items)
        return
    if rule.coverage_kind == "programmatic_marker":
        _validate_programmatic_marker_coverage_rule(rule)
        return
    _validate_non_programmatic_coverage_rule(rule)


def _validate_required_item_coverage_rule(
    rule: ContractMustAnswerCoverageRule,
    manifest_required_items: set[tuple[int, str]],
    required_rule_items: set[tuple[int, str]],
) -> None:
    """校验 required_output_item 覆盖类型规则。

    Args:
        rule: 待校验的 must_answer 覆盖规则。
        manifest_required_items: 模板 required_output_items 集合。
        required_rule_items: 已配置确定性 marker 的 required_output_items 集合。

    Returns:
        校验通过时返回 `None`。

    Raises:
        ValueError: required item 缺失、未知或未配置确定性 marker 时抛出。
    """

    if not rule.required_item_texts:
        raise ValueError(f"covered_by_required_item 必须声明 required item：chapter_id={rule.chapter_id}")
    if rule.markers_any:
        raise ValueError(f"covered_by_required_item 不应直接声明 marker：chapter_id={rule.chapter_id}")
    for item_text in rule.required_item_texts:
        key = (rule.chapter_id, item_text)
        if key not in manifest_required_items:
            raise ValueError(f"must_answer 覆盖引用未知 required item：chapter_id={rule.chapter_id}, item={item_text}")
        if key not in required_rule_items:
            raise ValueError(f"must_answer 覆盖引用未配置 marker 的 required item：chapter_id={rule.chapter_id}, item={item_text}")


def _validate_programmatic_marker_coverage_rule(
    rule: ContractMustAnswerCoverageRule,
) -> None:
    """校验 programmatic_marker 覆盖类型规则。

    Args:
        rule: 待校验的 must_answer 覆盖规则。

    Returns:
        校验通过时返回 `None`。

    Raises:
        ValueError: marker 缺失或同时声明 required item 时抛出。
    """

    if not rule.markers_any:
        raise ValueError(f"programmatic_marker 必须声明 marker：chapter_id={rule.chapter_id}")
    if rule.required_item_texts:
        raise ValueError(f"programmatic_marker 不应声明 required item：chapter_id={rule.chapter_id}")


def _validate_non_programmatic_coverage_rule(
    rule: ContractMustAnswerCoverageRule,
) -> None:
    """校验非程序化覆盖类型规则。

    Args:
        rule: 待校验的 must_answer 覆盖规则。

    Returns:
        校验通过时返回 `None`。

    Raises:
        ValueError: 缺少 rationale 或错误声明 marker/required item 时抛出。
    """

    if rule.markers_any:
        raise ValueError(f"非程序化 must_answer 覆盖不应声明 marker：chapter_id={rule.chapter_id}")
    if rule.required_item_texts:
        raise ValueError(f"非程序化 must_answer 覆盖不应声明 required item：chapter_id={rule.chapter_id}")
    if not rule.rationale:
        raise ValueError(f"非程序化 must_answer 覆盖必须声明 rationale：chapter_id={rule.chapter_id}")


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
