"""基金分析模板 CHAPTER_CONTRACT 机器契约。

本模块在 Agent 层基金能力维护可机器消费的模板章节契约，覆盖模板第 0-7 章。
契约内容来自 `docs/fund-analysis-template-draft.md` 的 CHAPTER_CONTRACT，
章节标题与 `docs/design.md` 第 3.1 节保持一致。本模块不在运行时解析
Markdown 注释，也不依赖模板渲染器的私有常量。
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final, Literal, Mapping, get_args

from fund_agent.fund.fund_type import FundType

LensKey = FundType | Literal["default"]

_TEMPLATE_ID: Final[str] = "fund-analysis-template-v1"
_SOURCE_PATH: Final[str] = "docs/fund-analysis-template-draft.md"
_EXPECTED_CHAPTER_IDS: Final[tuple[int, ...]] = tuple(range(8))
_SUPPORTED_FUND_TYPES: Final[tuple[FundType, ...]] = get_args(FundType)
_SUPPORTED_LENS_KEYS: Final[frozenset[str]] = frozenset((*_SUPPORTED_FUND_TYPES, "default"))
_SUPPORTED_LENS_PRIORITIES: Final[frozenset[str]] = frozenset(
    ("core", "high", "medium", "low")
)


@dataclass(frozen=True, slots=True)
class TemplateLensRule:
    """模板章节的基金类型视角规则。

    Attributes:
        fund_type: 当前 lens 对应的标准基金类型，或 `default` fallback。
        statements: 当前基金类型下的分析视角说明，见模板第 0-7 章 preferred_lens。
        facets_any: 模板草稿中声明的适用细分标签；没有声明时为空元组。
        priority: 模板草稿中声明的优先级；没有声明时为 `None`。
    """

    fund_type: LensKey
    statements: tuple[str, ...]
    facets_any: tuple[str, ...] = ()
    priority: str | None = None


@dataclass(frozen=True, slots=True)
class ChapterContract:
    """模板单章 CHAPTER_CONTRACT。

    Attributes:
        chapter_id: 模板章节编号，必须为 0-7。
        title: 章节标题，见 `docs/design.md` 第 3.1 节。
        narrative_mode: 叙事模式。
        must_answer: 本章必须回答的问题列表。
        must_not_cover: 本章禁止覆盖的内容。
        required_output_items: 本章必须输出的条目。
        preferred_lens: 按基金类型组织的分析视角规则。
    """

    chapter_id: int
    title: str
    narrative_mode: str
    must_answer: tuple[str, ...]
    must_not_cover: tuple[str, ...]
    required_output_items: tuple[str, ...]
    preferred_lens: Mapping[str, TemplateLensRule]


@dataclass(frozen=True, slots=True)
class TemplateContractManifest:
    """基金分析模板契约清单。

    Attributes:
        template_id: 模板契约标识。
        source_path: 人工维护契约文本的来源文档路径。
        chapters: 模板第 0-7 章的机器契约。
    """

    template_id: str
    source_path: str
    chapters: tuple[ChapterContract, ...]


def _lens(
    fund_type: LensKey,
    statements: tuple[str, ...],
    *,
    facets_any: tuple[str, ...] = (),
    priority: str | None = None,
) -> TemplateLensRule:
    """构造 preferred_lens 规则。

    Args:
        fund_type: 标准基金类型或 `default`。
        statements: lens 说明文本。
        facets_any: 适用细分标签。
        priority: lens 优先级。

    Returns:
        构造后的 `TemplateLensRule`。

    Raises:
        无显式抛出；统一由 `validate_template_contract_manifest()` 校验。
    """

    return TemplateLensRule(
        fund_type=fund_type,
        statements=statements,
        facets_any=facets_any,
        priority=priority,
    )


def _chapter(
    chapter_id: int,
    title: str,
    narrative_mode: str,
    must_answer: tuple[str, ...],
    must_not_cover: tuple[str, ...],
    required_output_items: tuple[str, ...],
    preferred_lens: Mapping[str, TemplateLensRule],
) -> ChapterContract:
    """构造单章契约。

    Args:
        chapter_id: 模板章节编号。
        title: 章节标题。
        narrative_mode: 叙事模式。
        must_answer: 必须回答的问题。
        must_not_cover: 禁止覆盖的内容。
        required_output_items: 必须输出的条目。
        preferred_lens: 基金类型视角规则。

    Returns:
        构造后的 `ChapterContract`。

    Raises:
        无显式抛出；统一由 `validate_template_contract_manifest()` 校验。
    """

    return ChapterContract(
        chapter_id=chapter_id,
        title=title,
        narrative_mode=narrative_mode,
        must_answer=must_answer,
        must_not_cover=must_not_cover,
        required_output_items=required_output_items,
        preferred_lens=preferred_lens,
    )


_CHAPTERS: Final[tuple[ChapterContract, ...]] = (
    _chapter(
        0,
        "投资要点概览",
        "封面→动作→验证",
        (
            "用一句话定义这只基金到底是什么产品。",
            "给出一个极简基金简介，帮助第一次接触这只基金的读者快速建立产品画像；只保留基金类型、基金经理、管理规模、成立时间中最必要的信息。",
            "回答当前判断应是值得持有、需要关注还是建议替换。",
            "回答这只基金当前业绩和运作处在什么状态，但只保留最能支撑当前动作判断的净值表现、超额收益或风险指标。",
            "回答支撑当前动作的最主要理由，默认压缩成 1 条；只有在第二条判断彼此独立且缺一不可时才允许写第 2 条。",
            "回答当前最值得盯住的变量是什么；先点出看这类基金时通常最先要看的东西；如果基金还有一个更能决定整份报告判断的特别情况，就把它放到最前面来写。",
            "回答当前最大的风险是什么，默认只保留一个主要风险。",
            "回答下一步最小验证问题是什么，默认先写 1 个最关键问题。",
            "回答什么变化会升级、降级或终止当前动作，优先压缩成 1 个升级阈值和 1 个降级或终止阈值。",
        ),
        (
            "不把本章写成后续章节的摘要、材料摘抄、按顺序复述，或信息罗列式导读。",
            "不把“基金简介 / 业绩概览 / 风险提示”拆成并列分栏。",
            "不把本章写成优点/缺点清单、投资亮点清单。",
            "不把“最主要的理由”写成多条优点堆砌；默认只保留 1 条。",
            "不把“最大风险”写成并列风险列表；默认只写一个主要风险。",
            "不把“下一步最小验证问题”写成愿望清单；默认先写 1 个。",
            "不把本章拆成“结论要点 / 详细情况 / 证据与出处”三段结构；第 0 章是封面页。",
            "不输出“证据与出处”小节。",
        ),
        (
            "一句话这是什么基金",
            "基金简介",
            "当前动作（🟢 值得持有 / 🟡 需要关注 / 🔴 建议替换）",
            "当前业绩与运作状态",
            "支撑当前动作的最主要理由",
            "当前最值得盯住的变量",
            "当前最大的风险",
            "下一步最小验证问题",
            "什么变化会升级、降级或终止当前动作",
        ),
        {
            "default": _lens(
                "default",
                (
                    "把本章当成基金体检封面页，读者应在最短时间内知道“这是什么基金、好不好、该不该继续持有”。",
                    "默认写成三层封面：先给“一眼看懂”，再回答“为什么现在是这个动作”，最后回答“下一步怎么验证”。",
                    "当前业绩状态要像给朋友的首屏导语，而不是迷你数据摘要。",
                    "默认只保留 1 条最主要的理由、1 个主要风险、1 个最关键验证问题和 2 个阈值事件。",
                ),
            ),
            "index_fund": _lens(
                "index_fund",
                ("指数基金优先回答：跟踪误差多大？费率多少？规模和流动性如何？",),
                facets_any=("宽基指数基金", "行业/主题指数基金", "策略指数基金"),
                priority="core",
            ),
            "active_fund": _lens(
                "active_fund",
                ("主动基金优先回答：超额收益是否稳定？基金经理是否靠谱？言行是否一致？",),
                facets_any=("主动权益基金（价值风格）", "主动权益基金（均衡风格）", "主动权益基金（成长风格）"),
                priority="core",
            ),
            "bond_fund": _lens(
                "bond_fund",
                ("债券基金优先回答：信用风险如何？久期多长？最大回撤多少？",),
                facets_any=("纯债基金", "二级债基/混合债基", "偏债混合基金"),
                priority="core",
            ),
            "enhanced_index": _lens(
                "enhanced_index",
                ("增强基金优先回答：超额收益是否稳定？跟踪误差多大？增强策略是什么？",),
                facets_any=("指数增强基金",),
                priority="core",
            ),
            "qdii_fund": _lens(
                "qdii_fund",
                ("QDII基金优先回答：投资哪个市场？汇率风险多大？费率是否合理？",),
                facets_any=("QDII 基金",),
                priority="core",
            ),
            "fof_fund": _lens(
                "fof_fund",
                ("FOF基金优先回答：底层基金配置策略是什么？双重收费问题如何？总费率多少？",),
                facets_any=("FOF 基金",),
                priority="core",
            ),
        },
    ),
    _chapter(
        1,
        "这只基金到底是什么产品",
        "定义→策略→基准",
        (
            "用最低认知负担定义这只基金到底是什么产品。",
            "说明基金的投资目标和投资策略（从招募说明书和年报§2提取）。",
            "说明基金的业绩基准是什么，为什么选这个基准。",
            "说明基金的类型分类（按有知有行三维标签：市值×风格×管理方式）。",
            "回答看这类基金时，通常最先要看什么。",
            "如果基金有一个不太符合常规、却会直接改变你对“这是什么产品”理解的特别情况，要说明它为什么重要。",
        ),
        (
            "不展开基金经理选股能力的分析（属于第 3 章）。",
            "不展开收益率的详细计算（属于第 2 章）。",
            "不分析市场竞争或同业比较（属于横向比较模块，不在本报告范围内）。",
        ),
        (
            "基金类型与分类标签",
            "投资目标（一句话）",
            "投资策略概述",
            "业绩基准及合理性",
            "看这类基金最先看什么",
            "会改变产品理解的特别情况（如有）",
        ),
        {
            "index_fund": _lens(
                "index_fund",
                (
                    "指数基金优先回答：跟踪什么指数？指数编制规则是什么？成分股定期调整机制？",
                    "lens: 指数基金的核心是“跟踪精度”和“费率”，先回答这两个问题。",
                ),
                facets_any=("宽基指数基金", "行业/主题指数基金", "策略指数基金"),
                priority="core",
            ),
            "active_fund": _lens(
                "active_fund",
                (
                    "主动基金优先回答：基金经理的投资哲学是什么？选股标准是什么？仓位管理策略是什么？",
                    "lens: 主动基金的核心是“基金经理”，先回答“这个人怎么想、怎么做”。",
                ),
                facets_any=("主动权益基金（价值风格）", "主动权益基金（均衡风格）", "主动权益基金（成长风格）"),
                priority="core",
            ),
            "bond_fund": _lens(
                "bond_fund",
                (
                    "债券基金优先回答：久期策略是什么？信用下沉程度如何？是否有转债/股票仓位？",
                    "lens: 债券基金的核心是“风险收益定位”，先回答“它到底有多安全”。",
                ),
                facets_any=("纯债基金", "二级债基/混合债基", "偏债混合基金"),
                priority="core",
            ),
            "enhanced_index": _lens(
                "enhanced_index",
                (
                    "增强基金优先回答：增强策略是什么（打新/量化/主观）？历史超额收益稳定性如何？跟踪误差多大？",
                    "lens: 增强基金的核心是“超额收益的来源和稳定性”，先回答“多出来的收益从哪来”。",
                ),
                facets_any=("指数增强基金",),
                priority="core",
            ),
            "qdii_fund": _lens(
                "qdii_fund",
                (
                    "QDII基金优先回答：投资哪个市场/地区？跟踪什么指数？汇率对冲策略是什么？",
                    "lens: QDII基金的核心是“跨境投资风险”，先回答“汇率风险和费率”。",
                ),
                facets_any=("QDII 基金",),
                priority="core",
            ),
            "fof_fund": _lens(
                "fof_fund",
                (
                    "FOF基金优先回答：资产配置策略是什么？底层基金筛选标准是什么？",
                    "lens: FOF基金的核心是“配置能力”，先回答“如何选基金、如何配比例”。",
                ),
                facets_any=("FOF 基金",),
                priority="core",
            ),
        },
    ),
    _chapter(
        2,
        "R=A+B-C 收益归因",
        "拆解→判断→成本",
        (
            "近 1 年、3 年、5 年的基金净值增长率（R）。",
            "同期业绩基准收益率（B）。",
            "计算超额收益（A = R - B）。",
            "判断超额收益是结构性的还是阶段性的。",
            "拆解成本 C：管理费 + 托管费 + 销售服务费 + 交易成本（估算）。",
            "判断超额收益是否为正且稳定、是否覆盖成本。",
        ),
        (
            "不展开基金经理选股能力的详细归因（属于第 3 章）。",
            "不展开市场走势分析（不属于本报告范围）。",
            "不做未来收益预测。",
        ),
        (
            "近 1/3/5 年净值增长率",
            "近 1/3/5 年业绩基准收益率",
            "超额收益（A = R - B）及稳定性",
            "超额收益性质判断（结构性 vs 阶段性）",
            "成本拆解（管理费、托管费、交易成本）",
            "成本合理性判断（同类对比）",
            "R=A+B-C 综合评估",
        ),
        {
            "default": _lens(
                "default",
                (
                    "核心区分：结构性超额（可持续的能力）vs 阶段性超额（风格顺风/运气）。",
                    "结构性超额的特征：多年度为正、不同市场环境都为正、超额收益来源可解释。",
                    "阶段性超额的特征：集中在某一年、与特定市场风格高度相关、无法解释来源。",
                ),
            ),
            "index_fund": _lens(
                "index_fund",
                ("指数基金的核心不是超额收益，而是跟踪误差和费率。本章重点回答：跟踪误差多大？费率是否合理？",),
                facets_any=("宽基指数基金", "行业/主题指数基金", "策略指数基金"),
                priority="core",
            ),
        },
    ),
    _chapter(
        3,
        "基金经理画像与言行一致性",
        "画像→验证→判断",
        (
            "基金经理的基本信息（从业年限、管理本基金时间、管理规模）。",
            "基金经理宣称的投资策略和风格（从年报§4提取）。",
            "基金经理实际的投资行为（从年报§8提取：行业配置、持仓集中度、换手率）。",
            "言行一致性判断：说的和做的一样吗？主动基金如缺少已复核的换手率或风格变化证据，不得据此判断言行一致。",
            "风格稳定性判断：跨期风格是否漂移？主动基金必须基于已复核的换手率或风格变化证据。",
            "利益一致性判断：基金经理是否持有本基金？",
        ),
        (
            "不做基金经理性格或人品的主观评价。",
            "不猜测基金经理的动机。",
            "不展开选股能力的量化分析（属于第 2 章超额收益范畴）。",
            "不在换手率或风格变化证据缺失、不可用、未复核时，推断主动基金风格稳定、风格一致或言行一致。",
        ),
        (
            "基金经理基本信息",
            "宣称的投资策略（§4）",
            "实际投资行为（§8）",
            "言行一致性判断",
            "风格稳定性判断",
            "利益一致性判断",
        ),
        {
            "default": _lens(
                "default",
                (
                    "核心区分：利益一致 vs 利益冲突。",
                    "✅ 一致信号：持有本基金、管理年限长、风格稳定、言行一致。",
                    "⚠️ 冲突信号：不持有本基金、频繁变更、风格漂移、言行不一致。",
                ),
            ),
            "index_fund": _lens(
                "index_fund",
                (
                    "指数基金对基金经理依赖度低，重点回答：跟踪误差是否稳定？规模是否稳定？",
                    "基金经理变更对指数基金影响较小，除非导致费率调整或清盘风险。",
                ),
                facets_any=("宽基指数基金", "行业/主题指数基金", "策略指数基金"),
                priority="low",
            ),
            "active_fund": _lens(
                "active_fund",
                (
                    "主动基金的核心是“基金经理”，本章是最关键章节。",
                    "重点回答：这个人怎么想？怎么做？说和做一样吗？利益绑定了吗？",
                ),
                facets_any=("主动权益基金（价值风格）", "主动权益基金（均衡风格）", "主动权益基金（成长风格）"),
                priority="core",
            ),
            "bond_fund": _lens(
                "bond_fund",
                ("债券基金重点回答：久期管理是否稳定？信用下沉程度是否与宣称一致？",),
                facets_any=("纯债基金", "二级债基/混合债基", "偏债混合基金"),
                priority="high",
            ),
            "enhanced_index": _lens(
                "enhanced_index",
                ("增强基金重点回答：增强策略是否稳定？基金经理是否过度偏离指数？",),
                facets_any=("指数增强基金",),
                priority="high",
            ),
            "qdii_fund": _lens(
                "qdii_fund",
                ("QDII基金重点回答：汇率风险管理是否稳定？投资地区配置是否与宣称一致？",),
                facets_any=("QDII 基金",),
                priority="high",
            ),
            "fof_fund": _lens(
                "fof_fund",
                ("FOF基金重点回答：底层基金配置是否稳定？是否频繁更换子基金？",),
                facets_any=("FOF 基金",),
                priority="high",
            ),
        },
    ),
    _chapter(
        4,
        "投资者获得感",
        "数据→对比→判断",
        (
            "基金产品收益（净值增长率）。",
            "投资者实际收益（盈利投资者占比、加权平均收益率）。",
            "行为损益 = 投资者实际收益 - 基金产品收益。",
            "份额变动趋势（资金是在追涨还是在抄底？）。",
        ),
        (
            "不分析具体投资者的交易行为。",
            "不做未来投资者行为预测。",
        ),
        (
            "基金产品收益 vs 投资者实际收益",
            "盈利投资者占比",
            "行为损益估算",
            "份额变动趋势",
        ),
        {
            "default": _lens(
                "default",
                (
                    "核心公式：投资者回报 = 基金产品收益 × 基民资金进出结构。",
                    "即使基金好，如果投资者追涨杀跌，实际回报也会大打折扣。",
                ),
            ),
            "index_fund": _lens(
                "index_fund",
                (
                    "指数基金投资者行为模式：通常在市场大跌时赎回（恐慌）、大涨时申购（追涨）。",
                    "重点回答：投资者是否在低点逃离？行为损益有多大？",
                ),
                facets_any=("宽基指数基金", "行业/主题指数基金", "策略指数基金"),
                priority="high",
            ),
            "active_fund": _lens(
                "active_fund",
                (
                    "主动基金投资者行为模式：受业绩排名影响大，容易追逐短期冠军。",
                    "重点回答：投资者是否在业绩高点追入？是否在业绩低谷逃离？",
                ),
                facets_any=("主动权益基金（价值风格）", "主动权益基金（均衡风格）", "主动权益基金（成长风格）"),
                priority="core",
            ),
            "bond_fund": _lens(
                "bond_fund",
                (
                    "债券基金投资者行为模式：通常较稳定，但在信用风险事件时可能集中赎回。",
                    "重点回答：是否有大额申赎波动？是否与债券市场波动相关？",
                ),
                facets_any=("纯债基金", "二级债基/混合债基", "偏债混合基金"),
                priority="medium",
            ),
        },
    ),
    _chapter(
        5,
        "当前阶段与关键变化",
        "变化→阶段→判断",
        (
            "当前阶段是什么（建仓期/稳定期/膨胀期/萎缩期/转型期）。",
            "相比上一期或历史，过去一年最关键的 1-3 个变化是什么（基金经理、规模、策略、费率、仓位或大额申赎）。",
            "这些变化是否影响原始投资假设或第 1-4 章判断。",
            "为什么偏偏是现在需要关注这只基金。",
            "下一步最小验证问题是什么。",
        ),
        (
            "不做市场整体走势预测。",
            "不罗列所有变化，只保留最关键的 1-3 个。",
            "不给最终持有/替换结论。",
            "不展开风险清单；变化事实只有转译为风险或否决项时才进入第 6 章。",
            "不重复基金经理长期画像或成本收益总评。",
        ),
        (
            "过去一年最关键的变化（1-3 个）",
            "基金当前所处阶段",
            "变化是否改变前文判断",
            "接下来最该跟踪的变量",
        ),
        {
            "default": _lens(
                "default",
                (
                    "核心区分：结构性变化 vs 阶段性变化。",
                    "结构性变化：基金经理变更、策略调整、费率调整、清盘风险。",
                    "阶段性变化：规模波动、市场环境变化、短期业绩波动。",
                ),
            ),
            "index_fund": _lens(
                "index_fund",
                (
                    "指数基金重点跟踪：规模变化（影响流动性）、跟踪误差变化、费率调整。",
                    "基金经理变更影响较小，除非导致清盘风险。",
                ),
                facets_any=("宽基指数基金", "行业/主题指数基金", "策略指数基金"),
                priority="high",
            ),
            "active_fund": _lens(
                "active_fund",
                ("主动基金重点跟踪：基金经理变更（最关键）、规模剧变（影响策略执行）、风格漂移。",),
                facets_any=("主动权益基金（价值风格）", "主动权益基金（均衡风格）", "主动权益基金（成长风格）"),
                priority="core",
            ),
            "bond_fund": _lens(
                "bond_fund",
                ("债券基金重点跟踪：久期调整、信用下沉程度变化、规模剧变（影响配置能力）。",),
                facets_any=("纯债基金", "二级债基/混合债基", "偏债混合基金"),
                priority="high",
            ),
            "enhanced_index": _lens(
                "enhanced_index",
                ("增强基金重点跟踪：增强策略调整、跟踪误差变化、基金经理变更。",),
                facets_any=("指数增强基金",),
                priority="core",
            ),
            "qdii_fund": _lens(
                "qdii_fund",
                ("QDII基金重点跟踪：汇率政策变化、投资地区配置变化、跨境政策风险。",),
                facets_any=("QDII 基金",),
                priority="high",
            ),
            "fof_fund": _lens(
                "fof_fund",
                ("FOF基金重点跟踪：底层基金更换、配置策略调整、双重费率变化。",),
                facets_any=("FOF 基金",),
                priority="high",
            ),
        },
    ),
    _chapter(
        6,
        "核心风险与否决项",
        "风险→否决→跟踪",
        (
            "核心风险是什么，其中哪些是结构性风险、哪些是阶段性风险。",
            "最关键的风险或否决项（1-2 个最致命的风险）。",
            "为什么足以改变结论——这个风险推翻了哪条核心假设。",
            "是否触发一票否决，还是仍可跟踪。",
            "压力测试结论是什么。",
            "哪个信息缺口最可能改变最终判断，下一轮先验证什么。",
        ),
        (
            "不把本章写成所有可能风险的罗列。",
            "不把“最大风险”写成并列列表；默认只写 1 个最致命的。",
            "不做风险发生概率的定量预测。",
            "不复述当前阶段事实，除非明确转译为风险、压力测试或否决项。",
            "不给最终持有/替换结论。",
            "不预测收益或市场走势。",
        ),
        (
            "最关键的风险或否决项",
            "为什么足以改变结论",
            "否决 vs 跟踪判断",
            "下一轮先验证什么",
        ),
        {
            "default": _lens(
                "default",
                (
                    "核心区分：否决项（一票否决）vs 跟踪项（持续关注）vs 一般风险（正常承受）。",
                    "否决项：清盘风险、基金经理离职、严重风格漂移、费率远超同类。",
                    "跟踪项：规模波动、换手率变化、集中度变化。",
                ),
            ),
            "index_fund": _lens(
                "index_fund",
                (
                    "指数基金否决项：清盘风险（规模<5000万）、跟踪误差>3%、费率远超同类。",
                    "指数基金跟踪项：规模变化、流动性变化、成分股调整。",
                    "压力测试默认阈值：-30%（正常）/ -50%（极端）/ -70%（历史最差）。",
                ),
                facets_any=("宽基指数基金", "行业/主题指数基金", "策略指数基金"),
                priority="core",
            ),
            "active_fund": _lens(
                "active_fund",
                (
                    "主动基金否决项：基金经理离职、严重风格漂移、清盘风险、费率>2%/年。",
                    "主动基金跟踪项：规模剧变、换手率异常、集中度变化。",
                    "压力测试默认阈值：-25%（正常）/ -45%（极端）/ -65%（历史最差）。",
                ),
                facets_any=("主动权益基金（价值风格）", "主动权益基金（均衡风格）", "主动权益基金（成长风格）"),
                priority="core",
            ),
            "bond_fund": _lens(
                "bond_fund",
                (
                    "债券基金否决项：信用风险事件、清盘风险、久期严重偏离宣称。",
                    "债券基金跟踪项：久期变化、信用下沉程度、规模变化。",
                    "压力测试默认阈值：-5%（正常）/ -10%（极端）/ -20%（历史最差）。",
                ),
                facets_any=("纯债基金", "二级债基/混合债基", "偏债混合基金"),
                priority="core",
            ),
            "enhanced_index": _lens(
                "enhanced_index",
                (
                    "增强基金否决项：清盘风险、跟踪误差>4%、增强策略失效（连续2年负超额）。",
                    "增强基金跟踪项：超额收益稳定性、规模变化、基金经理变更。",
                    "压力测试默认阈值：-25%（正常）/ -45%（极端）/ -60%（历史最差）。",
                ),
                facets_any=("指数增强基金",),
                priority="core",
            ),
            "qdii_fund": _lens(
                "qdii_fund",
                (
                    "QDII基金否决项：清盘风险、汇率严重不利、跨境政策限制、费率>2.5%/年。",
                    "QDII基金跟踪项：汇率变化、投资地区配置、流动性变化。",
                    "压力测试默认阈值：-35%（正常）/ -55%（极端）/ -75%（历史最差）。",
                ),
                facets_any=("QDII 基金",),
                priority="core",
            ),
            "fof_fund": _lens(
                "fof_fund",
                (
                    "FOF基金否决项：清盘风险、双重费率过高（>2%/年）、底层基金频繁更换。",
                    "FOF基金跟踪项：配置策略变化、底层基金表现、总费率变化。",
                    "压力测试默认阈值：-20%（正常）/ -40%（极端）/ -55%（历史最差）。",
                ),
                facets_any=("FOF 基金",),
                priority="core",
            ),
        },
    ),
    _chapter(
        7,
        "是否值得持有——最终判断",
        "判断→依据→验证",
        (
            "三选一明确立场：值得持有、需要关注、建议替换。",
            "为什么现在更适合这个判断，而不是另外两个。",
            "当前最容易看错的地方是什么。",
            "下一轮先核实什么（1-2 个最小验证问题）。",
            "什么变化会升级、降级或终止当前判断。",
        ),
        (
            "不输出具体的买入金额、卖出时机或仓位比例。",
            "不把本章写成前 6 章的摘要复述。",
            "不把“为什么”写成多条理由堆砌；默认只保留 1-2 条核心依据。",
        ),
        (
            "最终判断（🟢 值得持有 / 🟡 需要关注 / 🔴 建议替换）",
            "支撑判断的核心依据（1-2 条）",
            "当前最容易看错的地方",
            "下一轮最小验证计划",
            "危级/降级阈值",
        ),
        {
            "default": _lens(
                "default",
                (
                    "三选一明确立场：值得持有、需要关注、建议替换。",
                    "判断依据优先级：否决项 > 核心优势 > 一般特征。",
                ),
            ),
            "index_fund": _lens(
                "index_fund",
                (
                    "指数基金判断依据优先级：费率 > 跟踪误差 > 规模/流动性 > 基金公司。",
                    "“值得持有”的典型条件：费率低于同类中位数、跟踪误差<1%、规模>2亿。",
                ),
                facets_any=("宽基指数基金", "行业/主题指数基金", "策略指数基金"),
                priority="core",
            ),
            "active_fund": _lens(
                "active_fund",
                (
                    "主动基金判断依据优先级：基金经理 > 超额收益稳定性 > 言行一致性 > 费率。",
                    "“值得持有”的典型条件：基金经理任职>3年、超额收益稳定为正、言行一致、持有本基金。",
                ),
                facets_any=("主动权益基金（价值风格）", "主动权益基金（均衡风格）", "主动权益基金（成长风格）"),
                priority="core",
            ),
            "bond_fund": _lens(
                "bond_fund",
                (
                    "债券基金判断依据优先级：信用风险 > 久期稳定性 > 最大回撤 > 费率。",
                    "“值得持有”的典型条件：无信用风险事件、久期稳定、最大回撤可控、费率合理。",
                ),
                facets_any=("纯债基金", "二级债基/混合债基", "偏债混合基金"),
                priority="core",
            ),
            "enhanced_index": _lens(
                "enhanced_index",
                (
                    "增强基金判断依据优先级：超额收益稳定性 > 跟踪误差 > 费率 > 基金经理。",
                    "“值得持有”的典型条件：连续3年正超额、跟踪误差<2%、费率合理。",
                ),
                facets_any=("指数增强基金",),
                priority="core",
            ),
            "qdii_fund": _lens(
                "qdii_fund",
                (
                    "QDII基金判断依据优先级：费率 > 跟踪误差 > 汇率风险 > 规模/流动性。",
                    "“值得持有”的典型条件：费率合理、跟踪误差可控、汇率风险可承受、规模稳定。",
                ),
                facets_any=("QDII 基金",),
                priority="core",
            ),
            "fof_fund": _lens(
                "fof_fund",
                (
                    "FOF基金判断依据优先级：配置策略 > 总费率 > 底层基金质量 > 基金经理。",
                    "“值得持有”的典型条件：配置策略清晰、总费率<1.5%、底层基金质量稳定。",
                ),
                facets_any=("FOF 基金",),
                priority="core",
            ),
        },
    ),
)

_MANIFEST: Final[TemplateContractManifest] = TemplateContractManifest(
    template_id=_TEMPLATE_ID,
    source_path=_SOURCE_PATH,
    chapters=_CHAPTERS,
)


def load_template_contract_manifest() -> TemplateContractManifest:
    """读取基金分析模板契约清单。

    Returns:
        覆盖模板第 0-7 章的 `TemplateContractManifest`。

    Raises:
        ValueError: 内置 manifest 不满足章节数量、字段完整性或 lens 可解析性时抛出。
    """

    validate_template_contract_manifest(_MANIFEST)
    return _MANIFEST


def get_chapter_contract(chapter_id: int) -> ChapterContract:
    """按章节编号读取 CHAPTER_CONTRACT。

    Args:
        chapter_id: 模板章节编号，必须为 0-7。

    Returns:
        对应章节的 `ChapterContract`。

    Raises:
        ValueError: 章节编号不存在或 manifest 校验失败时抛出。
    """

    manifest = load_template_contract_manifest()
    for chapter in manifest.chapters:
        if chapter.chapter_id == chapter_id:
            return chapter
    raise ValueError(f"未找到模板章节契约：chapter_id={chapter_id}")


def resolve_preferred_lens(chapter_id: int, fund_type: FundType) -> TemplateLensRule:
    """解析指定章节与基金类型对应的 preferred_lens。

    Args:
        chapter_id: 模板章节编号，必须为 0-7。
        fund_type: 标准基金类型。

    Returns:
        精确命中基金类型的 `TemplateLensRule`；没有精确命中时返回 `default` 规则。

    Raises:
        ValueError: 章节不存在、基金类型不受支持，或没有精确 lens 且没有 default fallback 时抛出。
    """

    if fund_type not in _SUPPORTED_FUND_TYPES:
        raise ValueError(f"不支持的基金类型：{fund_type}")

    chapter = get_chapter_contract(chapter_id)
    if fund_type in chapter.preferred_lens:
        return chapter.preferred_lens[fund_type]
    if "default" in chapter.preferred_lens:
        return chapter.preferred_lens["default"]
    raise ValueError(f"章节 {chapter_id} 缺少基金类型 {fund_type} 的 preferred_lens fallback")


def validate_template_contract_manifest(manifest: TemplateContractManifest) -> None:
    """校验模板契约清单是否满足 fail-closed 约束。

    Args:
        manifest: 待校验的模板契约清单。

    Returns:
        校验通过时返回 `None`。

    Raises:
        ValueError: 章节数量、id 连续性、重复 id、空字段、unsupported lens key、
            lens 对象不一致或基金类型无 lens fallback 时抛出。
    """

    if not manifest.template_id.strip():
        raise ValueError("template_id 不能为空")
    if not manifest.source_path.strip():
        raise ValueError("source_path 不能为空")
    if len(manifest.chapters) != len(_EXPECTED_CHAPTER_IDS):
        raise ValueError("模板章节数量必须等于 8")

    chapter_ids = tuple(chapter.chapter_id for chapter in manifest.chapters)
    if len(set(chapter_ids)) != len(chapter_ids):
        raise ValueError("模板章节 id 存在重复")
    if chapter_ids != _EXPECTED_CHAPTER_IDS:
        raise ValueError("模板章节 id 必须连续覆盖 0..7")

    for chapter in manifest.chapters:
        _validate_chapter_contract(chapter)
        # 每个支持基金类型都必须能精确命中或回退 default，避免后续推理器无 lens 可用。
        for fund_type in _SUPPORTED_FUND_TYPES:
            if fund_type not in chapter.preferred_lens and "default" not in chapter.preferred_lens:
                raise ValueError(
                    f"章节 {chapter.chapter_id} 缺少基金类型 {fund_type} 的 preferred_lens fallback"
                )


def _validate_chapter_contract(chapter: ChapterContract) -> None:
    """校验单章契约字段。

    Args:
        chapter: 待校验的章节契约。

    Returns:
        校验通过时返回 `None`。

    Raises:
        ValueError: 章节字段为空、lens key 不受支持或 lens 内容无效时抛出。
    """

    if chapter.chapter_id not in _EXPECTED_CHAPTER_IDS:
        raise ValueError(f"不支持的章节 id：{chapter.chapter_id}")
    if not chapter.title.strip():
        raise ValueError(f"章节 {chapter.chapter_id} 标题不能为空")
    if not chapter.narrative_mode.strip():
        raise ValueError(f"章节 {chapter.chapter_id} narrative_mode 不能为空")
    _validate_non_empty_text_tuple(chapter.must_answer, "must_answer", chapter.chapter_id)
    _validate_non_empty_text_tuple(chapter.must_not_cover, "must_not_cover", chapter.chapter_id)
    _validate_non_empty_text_tuple(
        chapter.required_output_items,
        "required_output_items",
        chapter.chapter_id,
    )
    if not chapter.preferred_lens:
        raise ValueError(f"章节 {chapter.chapter_id} preferred_lens 不能为空")

    for key, lens_rule in chapter.preferred_lens.items():
        if key not in _SUPPORTED_LENS_KEYS:
            raise ValueError(f"章节 {chapter.chapter_id} 存在不支持的 lens key：{key}")
        if key != lens_rule.fund_type:
            raise ValueError(f"章节 {chapter.chapter_id} lens key 与 fund_type 不一致：{key}")
        _validate_lens_rule(chapter.chapter_id, lens_rule)


def _validate_lens_rule(chapter_id: int, lens_rule: TemplateLensRule) -> None:
    """校验单条 preferred_lens 规则。

    Args:
        chapter_id: 当前章节编号。
        lens_rule: 待校验的 lens 规则。

    Returns:
        校验通过时返回 `None`。

    Raises:
        ValueError: lens 类型、说明文本、facets 或 priority 无效时抛出。
    """

    if lens_rule.fund_type not in _SUPPORTED_LENS_KEYS:
        raise ValueError(f"章节 {chapter_id} 存在不支持的 lens fund_type：{lens_rule.fund_type}")
    _validate_non_empty_text_tuple(lens_rule.statements, "preferred_lens.statements", chapter_id)
    if any(not facet.strip() for facet in lens_rule.facets_any):
        raise ValueError(f"章节 {chapter_id} preferred_lens.facets_any 存在空值")
    if lens_rule.priority is not None and not lens_rule.priority.strip():
        raise ValueError(f"章节 {chapter_id} preferred_lens.priority 不能为空字符串")
    if lens_rule.priority is not None and lens_rule.priority not in _SUPPORTED_LENS_PRIORITIES:
        raise ValueError(f"章节 {chapter_id} preferred_lens.priority 不受支持：{lens_rule.priority}")


def _validate_non_empty_text_tuple(values: tuple[str, ...], field_name: str, chapter_id: int) -> None:
    """校验非空文本元组。

    Args:
        values: 待校验的文本元组。
        field_name: 字段名，用于错误信息。
        chapter_id: 当前章节编号。

    Returns:
        校验通过时返回 `None`。

    Raises:
        ValueError: 元组为空或包含空白文本时抛出。
    """

    if not values:
        raise ValueError(f"章节 {chapter_id} {field_name} 不能为空")
    if any(not value.strip() for value in values):
        raise ValueError(f"章节 {chapter_id} {field_name} 存在空值")
