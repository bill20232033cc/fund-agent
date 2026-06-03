"""基金分析模板 typed CHAPTER_CONTRACT sidecar。

本模块只在 Agent 层 Fund 包内提供模板第 0-7 章的 typed schema sidecar。
它从当前 `contracts.py` 机器契约精确投影，不替换模板真源、不改变 renderer、
auditor、deterministic analyze/checklist 或 `--use-llm` fail-closed 行为。
见模板第 2 章 R=A+B-C：Ch2 的 performance / attribution / cost 只能作为
第 2 章内部 typed subcontract，不能成为公开章节。
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final, Literal, Mapping, TypeAlias, get_args

from fund_agent.fund.fund_type import FundType
from fund_agent.fund.template.contracts import (
    ChapterContract,
    TemplateContractManifest,
    load_template_contract_manifest,
)

TYPED_TEMPLATE_CONTRACT_SCHEMA_VERSION: Final[str] = "typed_chapter_contract.v1"
TYPED_TEMPLATE_CONTRACT_TEMPLATE_ID: Final[str] = "fund-analysis-template-typed-v1"
EXPECTED_PUBLIC_CHAPTER_IDS: Final[tuple[int, ...]] = tuple(range(8))

MissingEvidenceBehavior: TypeAlias = Literal[
    "render_evidence_gap",
    "render_minimum_verification_question",
    "delete_if_not_applicable",
    "block",
]
EvidenceAvailabilityStatus: TypeAlias = Literal[
    "available",
    "missing",
    "unavailable",
    "not_applicable",
    "unreviewed",
]
AllowedContextLiteral: TypeAlias = Literal[
    "required_label",
    "evidence_gap_statement",
    "quote",
    "anchor_caption",
]
AuditFocusLiteral: TypeAlias = Literal[
    "chapter_structure",
    "evidence_anchors",
    "r_abc",
    "manager_consistency",
    "investor_experience",
    "current_stage",
    "risk",
    "final_judgment",
]
LensKey: TypeAlias = FundType | Literal["default"]

SUPPORTED_AUDIT_FOCUS: Final[tuple[AuditFocusLiteral, ...]] = get_args(AuditFocusLiteral)
SUPPORTED_MISSING_EVIDENCE_BEHAVIORS: Final[tuple[MissingEvidenceBehavior, ...]] = get_args(
    MissingEvidenceBehavior
)
SUPPORTED_EVIDENCE_STATUSES: Final[tuple[EvidenceAvailabilityStatus, ...]] = get_args(
    EvidenceAvailabilityStatus
)
SUPPORTED_ALLOWED_CONTEXTS: Final[tuple[AllowedContextLiteral, ...]] = get_args(
    AllowedContextLiteral
)
AUDIT_FOCUS_IS_SEMANTIC_ONLY: Final[bool] = True


@dataclass(frozen=True, slots=True)
class EvidencePredicate:
    """证据谓词描述。

    Attributes:
        predicate_id: 稳定谓词编号。
        requirement_ids: 谓词依赖的 requirement id；Slice 1 只保存数据，不派生证据。
        required_statuses: 触发谓词所需的证据状态闭集。
        description: 面向 review 的中文说明。
    """

    predicate_id: str
    requirement_ids: tuple[str, ...]
    required_statuses: tuple[EvidenceAvailabilityStatus, ...]
    description: str


@dataclass(frozen=True, slots=True)
class MustAnswerClause:
    """typed must_answer 条款。

    Attributes:
        clause_id: 稳定条款编号。
        text: 当前 CHAPTER_CONTRACT 中的原始条款文本。
    """

    clause_id: str
    text: str


@dataclass(frozen=True, slots=True)
class MustNotCoverClause:
    """typed must_not_cover 条款。

    Attributes:
        clause_id: 稳定条款编号。
        text: 当前 CHAPTER_CONTRACT 中的原始禁写文本。
        applies_when: 证据条件；为空表示无条件禁写。Slice 1 不执行该谓词。
        allowed_contexts: 未来 deterministic allowed_contexts 的闭集数据。
    """

    clause_id: str
    text: str
    applies_when: EvidencePredicate | None = None
    allowed_contexts: tuple[AllowedContextLiteral, ...] = ()


@dataclass(frozen=True, slots=True)
class RequiredOutputItem:
    """typed required_output_items 条目。

    Attributes:
        item_id: 稳定输出条目编号。
        text: 当前 CHAPTER_CONTRACT 中的原始 required output 文本。
        when_evidence_missing: 未来缺证处理行为；Slice 1 仅保存 schema 字段。
        missing_evidence_reason: 缺证行为的 reviewed typed reason；删除行为必须填写。
    """

    item_id: str
    text: str
    when_evidence_missing: MissingEvidenceBehavior | None = None
    missing_evidence_reason: str | None = None


@dataclass(frozen=True, slots=True)
class TemplateLensRule:
    """typed preferred_lens 规则。

    Attributes:
        fund_type: 当前 lens 对应的标准基金类型或 default。
        statements: 当前 preferred_lens 的说明文本。
        facets_any: 当前 preferred_lens 的细分标签。
        priority: 当前 preferred_lens 的优先级。
    """

    fund_type: LensKey
    statements: tuple[str, ...]
    facets_any: tuple[str, ...] = ()
    priority: str | None = None


@dataclass(frozen=True, slots=True)
class ChapterInternalSubcontract:
    """章节内部 typed subcontract。

    Attributes:
        subcontract_id: 章节内部稳定编号，例如第 2 章的 performance / attribution / cost。
        title: 内部子契约标题。
        requirement_ids: 子契约覆盖的条款或 required output id。
        public_chapter_id: 必须为 `None`，防止 Ch2 子契约变成公开章节。
    """

    subcontract_id: str
    title: str
    requirement_ids: tuple[str, ...]
    public_chapter_id: int | None = None


@dataclass(frozen=True, slots=True)
class TypedChapterContract:
    """typed 单章 CHAPTER_CONTRACT。

    Attributes:
        schema_version: typed schema 版本。
        chapter_id: 公开章节编号，必须保持 0-7。
        title: 章节标题。
        narrative_mode: 当前叙事模式。
        must_answer: typed must_answer 条款。
        must_not_cover: typed must_not_cover 条款。
        required_output_items: typed required output 条目。
        preferred_lens: typed preferred_lens 规则。
        audit_focus: bounded semantic audit 的关注点数据，只作语义强调。
        consumes_chapter_conclusions: 本章消费的其它章节结论编号。
        independent_action_source: 是否允许本章独立派生动作判断；第 0 章必须为 False。
        internal_subcontracts: 章节内部子契约；当前仅第 2 章允许。
    """

    schema_version: str
    chapter_id: int
    title: str
    narrative_mode: str
    must_answer: tuple[MustAnswerClause, ...]
    must_not_cover: tuple[MustNotCoverClause, ...]
    required_output_items: tuple[RequiredOutputItem, ...]
    preferred_lens: Mapping[str, TemplateLensRule]
    audit_focus: tuple[AuditFocusLiteral, ...]
    consumes_chapter_conclusions: tuple[int, ...] = ()
    independent_action_source: bool = False
    internal_subcontracts: tuple[ChapterInternalSubcontract, ...] = ()


@dataclass(frozen=True, slots=True)
class TypedTemplateContractManifest:
    """typed 模板契约清单。

    Attributes:
        schema_version: typed schema 版本。
        template_id: typed 模板 id。
        source_template_id: 当前 `contracts.py` manifest 的 id。
        source_path: 当前模板真源路径。
        chapters: 第 0-7 章 typed contract。
    """

    schema_version: str
    template_id: str
    source_template_id: str
    source_path: str
    chapters: tuple[TypedChapterContract, ...]


@dataclass(frozen=True, slots=True)
class _TextIdMapping:
    """当前契约原文到 stable id 的精确映射。"""

    text: str
    stable_id: str


@dataclass(frozen=True, slots=True)
class _ChapterTextMapping:
    """单章当前契约原文映射。"""

    must_answer: tuple[_TextIdMapping, ...]
    must_not_cover: tuple[_TextIdMapping, ...]
    required_output_items: tuple[_TextIdMapping, ...]


_CURRENT_TEXT_MAPPING: Final[Mapping[int, _ChapterTextMapping]] = {
    0: _ChapterTextMapping(
        must_answer=(
            _TextIdMapping("用一句话定义这只基金到底是什么产品。", "ch0.must_answer.item_01"),
            _TextIdMapping(
                "给出一个极简基金简介，帮助第一次接触这只基金的读者快速建立产品画像；只保留基金类型、基金经理、管理规模、成立时间中最必要的信息。",
                "ch0.must_answer.item_02",
            ),
            _TextIdMapping("回答当前判断应是值得持有、需要关注还是建议替换。", "ch0.must_answer.item_03"),
            _TextIdMapping(
                "回答这只基金当前业绩和运作处在什么状态，但只保留最能支撑当前动作判断的净值表现、超额收益或风险指标。",
                "ch0.must_answer.item_04",
            ),
            _TextIdMapping(
                "回答支撑当前动作的最主要理由，默认压缩成 1 条；只有在第二条判断彼此独立且缺一不可时才允许写第 2 条。",
                "ch0.must_answer.item_05",
            ),
            _TextIdMapping(
                "回答当前最值得盯住的变量是什么；先点出看这类基金时通常最先要看的东西；如果基金还有一个更能决定整份报告判断的特别情况，就把它放到最前面来写。",
                "ch0.must_answer.item_06",
            ),
            _TextIdMapping("回答当前最大的风险是什么，默认只保留一个主要风险。", "ch0.must_answer.item_07"),
            _TextIdMapping(
                "回答下一步最小验证问题是什么，默认先写 1 个最关键问题。",
                "ch0.must_answer.item_08",
            ),
            _TextIdMapping(
                "回答什么变化会升级、降级或终止当前动作，优先压缩成 1 个升级阈值和 1 个降级或终止阈值。",
                "ch0.must_answer.item_09",
            ),
        ),
        must_not_cover=(
            _TextIdMapping(
                "不把本章写成后续章节的摘要、材料摘抄、按顺序复述，或信息罗列式导读。",
                "ch0.must_not_cover.item_01",
            ),
            _TextIdMapping(
                "不把“基金简介 / 业绩概览 / 风险提示”拆成并列分栏。",
                "ch0.must_not_cover.item_02",
            ),
            _TextIdMapping("不把本章写成优点/缺点清单、投资亮点清单。", "ch0.must_not_cover.item_03"),
            _TextIdMapping(
                "不把“最主要的理由”写成多条优点堆砌；默认只保留 1 条。",
                "ch0.must_not_cover.item_04",
            ),
            _TextIdMapping(
                "不把“最大风险”写成并列风险列表；默认只写一个主要风险。",
                "ch0.must_not_cover.item_05",
            ),
            _TextIdMapping(
                "不把“下一步最小验证问题”写成愿望清单；默认先写 1 个。",
                "ch0.must_not_cover.item_06",
            ),
            _TextIdMapping(
                "不把本章拆成“结论要点 / 详细情况 / 证据与出处”三段结构；第 0 章是封面页。",
                "ch0.must_not_cover.item_07",
            ),
            _TextIdMapping("不输出“证据与出处”小节。", "ch0.must_not_cover.item_08"),
        ),
        required_output_items=(
            _TextIdMapping("一句话这是什么基金", "ch0.required_output.item_01"),
            _TextIdMapping("基金简介", "ch0.required_output.item_02"),
            _TextIdMapping(
                "当前动作（🟢 值得持有 / 🟡 需要关注 / 🔴 建议替换）",
                "ch0.required_output.item_03",
            ),
            _TextIdMapping("当前业绩与运作状态", "ch0.required_output.item_04"),
            _TextIdMapping("支撑当前动作的最主要理由", "ch0.required_output.item_05"),
            _TextIdMapping("当前最值得盯住的变量", "ch0.required_output.item_06"),
            _TextIdMapping("当前最大的风险", "ch0.required_output.item_07"),
            _TextIdMapping("下一步最小验证问题", "ch0.required_output.item_08"),
            _TextIdMapping("什么变化会升级、降级或终止当前动作", "ch0.required_output.item_09"),
        ),
    ),
    1: _ChapterTextMapping(
        must_answer=(
            _TextIdMapping("用最低认知负担定义这只基金到底是什么产品。", "ch1.must_answer.item_01"),
            _TextIdMapping(
                "说明基金的投资目标和投资策略（从招募说明书和年报§2提取）。",
                "ch1.must_answer.item_02",
            ),
            _TextIdMapping("说明基金的业绩基准是什么，为什么选这个基准。", "ch1.must_answer.item_03"),
            _TextIdMapping(
                "说明基金的类型分类（按有知有行三维标签：市值×风格×管理方式）。",
                "ch1.must_answer.item_04",
            ),
            _TextIdMapping("回答看这类基金时，通常最先要看什么。", "ch1.must_answer.item_05"),
            _TextIdMapping(
                "如果基金有一个不太符合常规、却会直接改变你对“这是什么产品”理解的特别情况，要说明它为什么重要。",
                "ch1.must_answer.item_06",
            ),
        ),
        must_not_cover=(
            _TextIdMapping(
                "不展开基金经理选股能力的分析（属于第 3 章）。",
                "ch1.must_not_cover.item_01",
            ),
            _TextIdMapping(
                "不展开收益率的详细计算（属于第 2 章）。",
                "ch1.must_not_cover.item_02",
            ),
            _TextIdMapping(
                "不分析市场竞争或同业比较（属于横向比较模块，不在本报告范围内）。",
                "ch1.must_not_cover.item_03",
            ),
        ),
        required_output_items=(
            _TextIdMapping("基金类型与分类标签", "ch1.required_output.item_01"),
            _TextIdMapping("投资目标（一句话）", "ch1.required_output.item_02"),
            _TextIdMapping("投资策略概述", "ch1.required_output.item_03"),
            _TextIdMapping("业绩基准及合理性", "ch1.required_output.item_04"),
            _TextIdMapping("看这类基金最先看什么", "ch1.required_output.item_05"),
            _TextIdMapping("会改变产品理解的特别情况（如有）", "ch1.required_output.item_06"),
        ),
    ),
    2: _ChapterTextMapping(
        must_answer=(
            _TextIdMapping("近 1 年、3 年、5 年的基金净值增长率（R）。", "ch2.must_answer.item_01"),
            _TextIdMapping("同期业绩基准收益率（B）。", "ch2.must_answer.item_02"),
            _TextIdMapping("计算超额收益（A = R - B）。", "ch2.must_answer.item_03"),
            _TextIdMapping("判断超额收益是结构性的还是阶段性的。", "ch2.must_answer.item_04"),
            _TextIdMapping(
                "拆解成本 C：管理费 + 托管费 + 销售服务费 + 交易成本（估算）。",
                "ch2.must_answer.item_05",
            ),
            _TextIdMapping("判断超额收益是否为正且稳定、是否覆盖成本。", "ch2.must_answer.item_06"),
        ),
        must_not_cover=(
            _TextIdMapping(
                "不展开基金经理选股能力的详细归因（属于第 3 章）。",
                "ch2.must_not_cover.item_01",
            ),
            _TextIdMapping("不展开市场走势分析（不属于本报告范围）。", "ch2.must_not_cover.item_02"),
            _TextIdMapping("不做未来收益预测。", "ch2.must_not_cover.item_03"),
        ),
        required_output_items=(
            _TextIdMapping("近 1/3/5 年净值增长率", "ch2.required_output.item_01"),
            _TextIdMapping("近 1/3/5 年业绩基准收益率", "ch2.required_output.item_02"),
            _TextIdMapping("超额收益（A = R - B）及稳定性", "ch2.required_output.item_03"),
            _TextIdMapping("超额收益性质判断（结构性 vs 阶段性）", "ch2.required_output.item_04"),
            _TextIdMapping("成本拆解（管理费、托管费、交易成本）", "ch2.required_output.item_05"),
            _TextIdMapping("成本合理性判断（同类对比）", "ch2.required_output.item_06"),
            _TextIdMapping("R=A+B-C 综合评估", "ch2.required_output.item_07"),
        ),
    ),
    3: _ChapterTextMapping(
        must_answer=(
            _TextIdMapping(
                "基金经理的基本信息（从业年限、管理本基金时间、管理规模）。",
                "ch3.must_answer.item_01",
            ),
            _TextIdMapping(
                "基金经理宣称的投资策略和风格（从年报§4提取）。",
                "ch3.must_answer.item_02",
            ),
            _TextIdMapping(
                "基金经理实际的投资行为（从年报§8提取：行业配置、持仓集中度、换手率）。",
                "ch3.must_answer.item_03",
            ),
            _TextIdMapping(
                "言行一致性判断：说的和做的一样吗？主动基金如缺少已复核的换手率或风格变化证据，不得据此判断言行一致。",
                "ch3.must_answer.item_04",
            ),
            _TextIdMapping(
                "风格稳定性判断：跨期风格是否漂移？主动基金必须基于已复核的换手率或风格变化证据。",
                "ch3.must_answer.item_05",
            ),
            _TextIdMapping("利益一致性判断：基金经理是否持有本基金？", "ch3.must_answer.item_06"),
        ),
        must_not_cover=(
            _TextIdMapping("不做基金经理性格或人品的主观评价。", "ch3.must_not_cover.item_01"),
            _TextIdMapping("不猜测基金经理的动机。", "ch3.must_not_cover.item_02"),
            _TextIdMapping(
                "不展开选股能力的量化分析（属于第 2 章超额收益范畴）。",
                "ch3.must_not_cover.item_03",
            ),
            _TextIdMapping(
                "不在换手率或风格变化证据缺失、不可用、未复核时，推断主动基金风格稳定、风格一致或言行一致。",
                "ch3.must_not_cover.item_04",
            ),
        ),
        required_output_items=(
            _TextIdMapping("基金经理基本信息", "ch3.required_output.item_01"),
            _TextIdMapping("宣称的投资策略（§4）", "ch3.required_output.item_02"),
            _TextIdMapping("实际投资行为（§8）", "ch3.required_output.item_03"),
            _TextIdMapping("言行一致性判断", "ch3.required_output.item_04"),
            _TextIdMapping("风格稳定性判断", "ch3.required_output.item_05"),
            _TextIdMapping("利益一致性判断", "ch3.required_output.item_06"),
        ),
    ),
    4: _ChapterTextMapping(
        must_answer=(
            _TextIdMapping("基金产品收益（净值增长率）。", "ch4.must_answer.item_01"),
            _TextIdMapping(
                "投资者实际收益（盈利投资者占比、加权平均收益率）。",
                "ch4.must_answer.item_02",
            ),
            _TextIdMapping(
                "行为损益 = 投资者实际收益 - 基金产品收益。",
                "ch4.must_answer.item_03",
            ),
            _TextIdMapping("份额变动趋势（资金是在追涨还是在抄底？）。", "ch4.must_answer.item_04"),
        ),
        must_not_cover=(
            _TextIdMapping("不分析具体投资者的交易行为。", "ch4.must_not_cover.item_01"),
            _TextIdMapping("不做未来投资者行为预测。", "ch4.must_not_cover.item_02"),
        ),
        required_output_items=(
            _TextIdMapping("基金产品收益 vs 投资者实际收益", "ch4.required_output.item_01"),
            _TextIdMapping("盈利投资者占比", "ch4.required_output.item_02"),
            _TextIdMapping("行为损益估算", "ch4.required_output.item_03"),
            _TextIdMapping("份额变动趋势", "ch4.required_output.item_04"),
        ),
    ),
    5: _ChapterTextMapping(
        must_answer=(
            _TextIdMapping(
                "当前阶段是什么（建仓期/稳定期/膨胀期/萎缩期/转型期）。",
                "ch5.must_answer.item_01",
            ),
            _TextIdMapping(
                "相比上一期或历史，过去一年最关键的 1-3 个变化是什么（基金经理、规模、策略、费率、仓位或大额申赎）。",
                "ch5.must_answer.item_02",
            ),
            _TextIdMapping("这些变化是否影响原始投资假设或第 1-4 章判断。", "ch5.must_answer.item_03"),
            _TextIdMapping("为什么偏偏是现在需要关注这只基金。", "ch5.must_answer.item_04"),
            _TextIdMapping("下一步最小验证问题是什么。", "ch5.must_answer.item_05"),
        ),
        must_not_cover=(
            _TextIdMapping("不做市场整体走势预测。", "ch5.must_not_cover.item_01"),
            _TextIdMapping(
                "不罗列所有变化，只保留最关键的 1-3 个。",
                "ch5.must_not_cover.item_02",
            ),
            _TextIdMapping("不给最终持有/替换结论。", "ch5.must_not_cover.item_03"),
            _TextIdMapping(
                "不展开风险清单；变化事实只有转译为风险或否决项时才进入第 6 章。",
                "ch5.must_not_cover.item_04",
            ),
            _TextIdMapping("不重复基金经理长期画像或成本收益总评。", "ch5.must_not_cover.item_05"),
        ),
        required_output_items=(
            _TextIdMapping("过去一年最关键的变化（1-3 个）", "ch5.required_output.item_01"),
            _TextIdMapping("基金当前所处阶段", "ch5.required_output.item_02"),
            _TextIdMapping("变化是否改变前文判断", "ch5.required_output.item_03"),
            _TextIdMapping("接下来最该跟踪的变量", "ch5.required_output.item_04"),
        ),
    ),
    6: _ChapterTextMapping(
        must_answer=(
            _TextIdMapping(
                "核心风险是什么，其中哪些是结构性风险、哪些是阶段性风险。",
                "ch6.must_answer.item_01",
            ),
            _TextIdMapping(
                "最关键的风险或否决项（1-2 个最致命的风险）。",
                "ch6.must_answer.item_02",
            ),
            _TextIdMapping(
                "为什么足以改变结论——这个风险推翻了哪条核心假设。",
                "ch6.must_answer.item_03",
            ),
            _TextIdMapping("是否触发一票否决，还是仍可跟踪。", "ch6.must_answer.item_04"),
            _TextIdMapping("压力测试结论是什么。", "ch6.must_answer.item_05"),
            _TextIdMapping(
                "哪个信息缺口最可能改变最终判断，下一轮先验证什么。",
                "ch6.must_answer.item_06",
            ),
        ),
        must_not_cover=(
            _TextIdMapping("不把本章写成所有可能风险的罗列。", "ch6.must_not_cover.item_01"),
            _TextIdMapping(
                "不把“最大风险”写成并列列表；默认只写 1 个最致命的。",
                "ch6.must_not_cover.item_02",
            ),
            _TextIdMapping("不做风险发生概率的定量预测。", "ch6.must_not_cover.item_03"),
            _TextIdMapping(
                "不复述当前阶段事实，除非明确转译为风险、压力测试或否决项。",
                "ch6.must_not_cover.item_04",
            ),
            _TextIdMapping("不给最终持有/替换结论。", "ch6.must_not_cover.item_05"),
            _TextIdMapping("不预测收益或市场走势。", "ch6.must_not_cover.item_06"),
        ),
        required_output_items=(
            _TextIdMapping("最关键的风险或否决项", "ch6.required_output.item_01"),
            _TextIdMapping("为什么足以改变结论", "ch6.required_output.item_02"),
            _TextIdMapping("否决 vs 跟踪判断", "ch6.required_output.item_03"),
            _TextIdMapping("下一轮先验证什么", "ch6.required_output.item_04"),
        ),
    ),
    7: _ChapterTextMapping(
        must_answer=(
            _TextIdMapping("三选一明确立场：值得持有、需要关注、建议替换。", "ch7.must_answer.item_01"),
            _TextIdMapping("为什么现在更适合这个判断，而不是另外两个。", "ch7.must_answer.item_02"),
            _TextIdMapping("当前最容易看错的地方是什么。", "ch7.must_answer.item_03"),
            _TextIdMapping(
                "下一轮先核实什么（1-2 个最小验证问题）。",
                "ch7.must_answer.item_04",
            ),
            _TextIdMapping("什么变化会升级、降级或终止当前判断。", "ch7.must_answer.item_05"),
        ),
        must_not_cover=(
            _TextIdMapping(
                "不输出具体的买入金额、卖出时机或仓位比例。",
                "ch7.must_not_cover.item_01",
            ),
            _TextIdMapping("不把本章写成前 6 章的摘要复述。", "ch7.must_not_cover.item_02"),
            _TextIdMapping(
                "不把“为什么”写成多条理由堆砌；默认只保留 1-2 条核心依据。",
                "ch7.must_not_cover.item_03",
            ),
        ),
        required_output_items=(
            _TextIdMapping(
                "最终判断（🟢 值得持有 / 🟡 需要关注 / 🔴 建议替换）",
                "ch7.required_output.item_01",
            ),
            _TextIdMapping("支撑判断的核心依据（1-2 条）", "ch7.required_output.item_02"),
            _TextIdMapping("当前最容易看错的地方", "ch7.required_output.item_03"),
            _TextIdMapping("下一轮最小验证计划", "ch7.required_output.item_04"),
            _TextIdMapping("危级/降级阈值", "ch7.required_output.item_05"),
        ),
    ),
}

_AUDIT_FOCUS_BY_CHAPTER: Final[Mapping[int, tuple[AuditFocusLiteral, ...]]] = {
    0: ("final_judgment", "chapter_structure"),
    1: ("chapter_structure", "evidence_anchors"),
    2: ("r_abc", "evidence_anchors"),
    3: ("manager_consistency", "evidence_anchors"),
    4: ("investor_experience", "evidence_anchors"),
    5: ("current_stage", "evidence_anchors"),
    6: ("risk", "evidence_anchors"),
    7: ("final_judgment", "risk"),
}

_CH3_STYLE_EVIDENCE_UNREVIEWED: Final[EvidencePredicate] = EvidencePredicate(
    predicate_id="ch3.evidence.manager_behavior_style_unreviewed",
    requirement_ids=(
        "ch3.requirement.actual_behavior_reviewed",
    ),
    required_statuses=("missing", "unavailable", "unreviewed"),
    description="主动基金第 3 章缺少已复核换手率或跨期风格变化证据时，禁止正向一致性推断。",
)


def load_typed_template_contract_manifest(
    source_manifest: TemplateContractManifest | None = None,
) -> TypedTemplateContractManifest:
    """读取 typed 模板契约清单。

    Args:
        source_manifest: 可选的当前 `contracts.py` manifest；为空时读取内置 manifest。

    Returns:
        覆盖公开章节 0-7 的 `TypedTemplateContractManifest`。

    Raises:
        ValueError: 当前 manifest 与 reviewed exact mapping 不一致，或 typed 校验失败时抛出。
    """

    manifest = source_manifest if source_manifest is not None else load_template_contract_manifest()
    typed_manifest = TypedTemplateContractManifest(
        schema_version=TYPED_TEMPLATE_CONTRACT_SCHEMA_VERSION,
        template_id=TYPED_TEMPLATE_CONTRACT_TEMPLATE_ID,
        source_template_id=manifest.template_id,
        source_path=manifest.source_path,
        chapters=tuple(_project_chapter(chapter) for chapter in manifest.chapters),
    )
    validate_typed_template_contract_manifest(typed_manifest)
    return typed_manifest


def validate_typed_template_contract_manifest(manifest: TypedTemplateContractManifest) -> None:
    """校验 typed 模板契约清单。

    Args:
        manifest: 待校验的 typed manifest。

    Returns:
        校验通过时返回 `None`。

    Raises:
        ValueError: schema、章节 id、依赖、Ch2 内部子契约、required output id、
            clause id 或 `audit_focus` 闭集不满足 fail-closed 约束时抛出。
    """

    if manifest.schema_version != TYPED_TEMPLATE_CONTRACT_SCHEMA_VERSION:
        raise ValueError(f"typed schema_version 不受支持：{manifest.schema_version}")
    if not manifest.template_id.strip():
        raise ValueError("typed template_id 不能为空")
    if not manifest.source_template_id.strip():
        raise ValueError("typed source_template_id 不能为空")
    if not manifest.source_path.strip():
        raise ValueError("typed source_path 不能为空")

    chapter_ids = tuple(chapter.chapter_id for chapter in manifest.chapters)
    if chapter_ids != EXPECTED_PUBLIC_CHAPTER_IDS:
        raise ValueError("typed 公开章节 id 必须精确覆盖 0..7")
    if len(set(chapter_ids)) != len(chapter_ids):
        raise ValueError("typed 公开章节 id 存在重复")

    known_ids = frozenset(chapter_ids)
    all_clause_ids: list[str] = []
    for chapter in manifest.chapters:
        _validate_typed_chapter_contract(chapter, known_ids)
        all_clause_ids.extend(clause.clause_id for clause in chapter.must_answer)
        all_clause_ids.extend(clause.clause_id for clause in chapter.must_not_cover)
    if len(all_clause_ids) != len(set(all_clause_ids)):
        raise ValueError("typed clause_id 存在重复")


def get_typed_chapter_contract(chapter_id: int) -> TypedChapterContract:
    """按公开章节编号读取 typed CHAPTER_CONTRACT。

    Args:
        chapter_id: 公开章节编号，必须为 0-7。

    Returns:
        对应章节的 `TypedChapterContract`。

    Raises:
        ValueError: 章节编号不存在或 typed manifest 校验失败时抛出。
    """

    manifest = load_typed_template_contract_manifest()
    for chapter in manifest.chapters:
        if chapter.chapter_id == chapter_id:
            return chapter
    raise ValueError(f"未找到 typed 模板章节契约：chapter_id={chapter_id}")


def _project_chapter(chapter: ChapterContract) -> TypedChapterContract:
    """把当前单章契约精确投影为 typed 契约。

    Args:
        chapter: 当前 `contracts.py` 的单章契约。

    Returns:
        typed 单章契约。

    Raises:
        ValueError: 当前文本未命中 reviewed exact mapping 时抛出。
    """

    text_mapping = _CURRENT_TEXT_MAPPING.get(chapter.chapter_id)
    if text_mapping is None:
        raise ValueError(f"章节 {chapter.chapter_id} 缺少 typed exact mapping")

    return TypedChapterContract(
        schema_version=TYPED_TEMPLATE_CONTRACT_SCHEMA_VERSION,
        chapter_id=chapter.chapter_id,
        title=chapter.title,
        narrative_mode=chapter.narrative_mode,
        must_answer=_project_must_answer(chapter, text_mapping),
        must_not_cover=_project_must_not_cover(chapter, text_mapping),
        required_output_items=_project_required_output_items(chapter, text_mapping),
        preferred_lens=_project_lens_rules(chapter),
        audit_focus=_AUDIT_FOCUS_BY_CHAPTER[chapter.chapter_id],
        consumes_chapter_conclusions=(7,) if chapter.chapter_id == 0 else (),
        independent_action_source=False,
        internal_subcontracts=_build_internal_subcontracts(chapter.chapter_id),
    )


def _project_must_answer(
    chapter: ChapterContract,
    text_mapping: _ChapterTextMapping,
) -> tuple[MustAnswerClause, ...]:
    """投影单章 must_answer 条款。

    Args:
        chapter: 当前单章契约。
        text_mapping: 本章 reviewed exact mapping。

    Returns:
        typed must_answer 条款。

    Raises:
        ValueError: 当前 must_answer 文本与 reviewed mapping 不一致时抛出。
    """

    _assert_exact_text_mapping(chapter.chapter_id, "must_answer", chapter.must_answer, text_mapping.must_answer)
    return tuple(
        MustAnswerClause(clause_id=item.stable_id, text=item.text)
        for item in text_mapping.must_answer
    )


def _project_must_not_cover(
    chapter: ChapterContract,
    text_mapping: _ChapterTextMapping,
) -> tuple[MustNotCoverClause, ...]:
    """投影单章 must_not_cover 条款。

    Args:
        chapter: 当前单章契约。
        text_mapping: 本章 reviewed exact mapping。

    Returns:
        typed must_not_cover 条款。

    Raises:
        ValueError: 当前 must_not_cover 文本与 reviewed mapping 不一致时抛出。
    """

    _assert_exact_text_mapping(
        chapter.chapter_id,
        "must_not_cover",
        chapter.must_not_cover,
        text_mapping.must_not_cover,
    )
    clauses = []
    for item in text_mapping.must_not_cover:
        clauses.append(
            MustNotCoverClause(
                clause_id=item.stable_id,
                text=item.text,
                applies_when=_must_not_cover_predicate(item.stable_id),
                allowed_contexts=_must_not_cover_allowed_contexts(item.stable_id),
            )
        )
    return tuple(clauses)


def _project_required_output_items(
    chapter: ChapterContract,
    text_mapping: _ChapterTextMapping,
) -> tuple[RequiredOutputItem, ...]:
    """投影单章 required_output_items 条目。

    Args:
        chapter: 当前单章契约。
        text_mapping: 本章 reviewed exact mapping。

    Returns:
        typed required output 条目。

    Raises:
        ValueError: 当前 required_output_items 文本与 reviewed mapping 不一致时抛出。
    """

    _assert_exact_text_mapping(
        chapter.chapter_id,
        "required_output_items",
        chapter.required_output_items,
        text_mapping.required_output_items,
    )
    return tuple(
        RequiredOutputItem(
            item_id=item.stable_id,
            text=item.text,
            when_evidence_missing=_required_output_missing_behavior(item.stable_id),
            missing_evidence_reason=_required_output_missing_reason(item.stable_id),
        )
        for item in text_mapping.required_output_items
    )


def _required_output_missing_behavior(item_id: str) -> MissingEvidenceBehavior | None:
    """读取 required output 的缺证行为默认值。

    Args:
        item_id: typed required output item id。

    Returns:
        缺证行为；无需 typed 缺证处理时返回 `None`。

    Raises:
        无。
    """

    if item_id.startswith("ch2.required_output."):
        return "block"
    if item_id in {
        "ch3.required_output.item_02",
        "ch3.required_output.item_03",
        "ch3.required_output.item_04",
        "ch3.required_output.item_05",
    }:
        return "render_evidence_gap"
    if item_id == "ch3.required_output.item_06":
        return "render_minimum_verification_question"
    return None


def _required_output_missing_reason(item_id: str) -> str | None:
    """读取 required output 缺证行为的 reviewed reason。

    Args:
        item_id: typed required output item id。

    Returns:
        reviewed reason；仅需要显式原因的行为返回文本。

    Raises:
        无。
    """

    if item_id.startswith("ch2.required_output."):
        return "第 2 章 R=A+B-C 数值与成本判断缺少同源证据时不得生成替代结论。"
    if item_id in {
        "ch3.required_output.item_02",
        "ch3.required_output.item_03",
        "ch3.required_output.item_04",
        "ch3.required_output.item_05",
    }:
        return "第 3 章策略、实际行为、言行一致性和风格稳定性在缺少已复核证据时只能输出证据缺口。"
    if item_id == "ch3.required_output.item_06":
        return "第 3 章利益一致性证据缺失时只能输出下一步最小验证问题。"
    return None


def _project_lens_rules(chapter: ChapterContract) -> Mapping[str, TemplateLensRule]:
    """投影当前 preferred_lens 规则。

    Args:
        chapter: 当前单章契约。

    Returns:
        typed preferred_lens 映射。

    Raises:
        无显式抛出；当前 manifest 的 lens 合法性由 `contracts.py` 校验。
    """

    return {
        key: TemplateLensRule(
            fund_type=rule.fund_type,
            statements=rule.statements,
            facets_any=rule.facets_any,
            priority=rule.priority,
        )
        for key, rule in chapter.preferred_lens.items()
    }


def _build_internal_subcontracts(chapter_id: int) -> tuple[ChapterInternalSubcontract, ...]:
    """构造章节内部子契约。

    Args:
        chapter_id: 当前公开章节编号。

    Returns:
        第 2 章返回 performance / attribution / cost；其它章节返回空元组。

    Raises:
        无。
    """

    if chapter_id != 2:
        return ()
    return (
        ChapterInternalSubcontract(
            subcontract_id="performance",
            title="收益表现",
            requirement_ids=(
                "ch2.must_answer.item_01",
                "ch2.must_answer.item_02",
                "ch2.required_output.item_01",
                "ch2.required_output.item_02",
            ),
        ),
        ChapterInternalSubcontract(
            subcontract_id="attribution",
            title="超额归因",
            requirement_ids=(
                "ch2.must_answer.item_03",
                "ch2.must_answer.item_04",
                "ch2.required_output.item_03",
                "ch2.required_output.item_04",
            ),
        ),
        ChapterInternalSubcontract(
            subcontract_id="cost",
            title="成本拆解",
            requirement_ids=(
                "ch2.must_answer.item_05",
                "ch2.must_answer.item_06",
                "ch2.required_output.item_05",
                "ch2.required_output.item_06",
                "ch2.required_output.item_07",
            ),
        ),
    )


def _must_not_cover_predicate(clause_id: str) -> EvidencePredicate | None:
    """读取 must_not_cover 的证据谓词。

    Args:
        clause_id: typed must_not_cover clause id。

    Returns:
        需要证据条件的 clause 返回 `EvidencePredicate`，其它返回 `None`。

    Raises:
        无。
    """

    if clause_id == "ch3.must_not_cover.item_04":
        return _CH3_STYLE_EVIDENCE_UNREVIEWED
    return None


def _must_not_cover_allowed_contexts(clause_id: str) -> tuple[AllowedContextLiteral, ...]:
    """读取 must_not_cover 的 allowed_contexts 数据。

    Args:
        clause_id: typed must_not_cover clause id。

    Returns:
        未来 deterministic allowed_contexts 闭集数据；Slice 1 不执行匹配。

    Raises:
        无。
    """

    if clause_id == "ch3.must_not_cover.item_04":
        return ("required_label", "evidence_gap_statement", "quote", "anchor_caption")
    return ()


def _assert_exact_text_mapping(
    chapter_id: int,
    field_name: str,
    source_values: tuple[str, ...],
    mapped_values: tuple[_TextIdMapping, ...],
) -> None:
    """校验当前文本与 reviewed mapping 精确一致。

    Args:
        chapter_id: 当前章节编号。
        field_name: 字段名。
        source_values: 当前 manifest 中的原文序列。
        mapped_values: reviewed mapping 中的原文与 id 序列。

    Returns:
        校验通过时返回 `None`。

    Raises:
        ValueError: 长度、顺序或原文不一致时抛出。
    """

    mapped_text = tuple(item.text for item in mapped_values)
    if source_values != mapped_text:
        raise ValueError(f"章节 {chapter_id} {field_name} 未命中 typed reviewed exact mapping")


def _validate_typed_chapter_contract(
    chapter: TypedChapterContract,
    known_chapter_ids: frozenset[int],
) -> None:
    """校验 typed 单章契约。

    Args:
        chapter: 待校验的 typed 章节契约。
        known_chapter_ids: manifest 中已知公开章节 id 集合。

    Returns:
        校验通过时返回 `None`。

    Raises:
        ValueError: 单章 schema、依赖、条款、required output、audit_focus 或内部子契约无效时抛出。
    """

    if chapter.schema_version != TYPED_TEMPLATE_CONTRACT_SCHEMA_VERSION:
        raise ValueError(f"章节 {chapter.chapter_id} typed schema_version 不受支持")
    if chapter.chapter_id not in EXPECTED_PUBLIC_CHAPTER_IDS:
        raise ValueError(f"不支持的 typed 公开章节 id：{chapter.chapter_id}")
    if not chapter.title.strip():
        raise ValueError(f"typed 章节 {chapter.chapter_id} 标题不能为空")
    if not chapter.narrative_mode.strip():
        raise ValueError(f"typed 章节 {chapter.chapter_id} narrative_mode 不能为空")
    _validate_non_empty_unique_clause_ids(chapter.must_answer, "must_answer", chapter.chapter_id)
    _validate_non_empty_unique_clause_ids(chapter.must_not_cover, "must_not_cover", chapter.chapter_id)
    _validate_required_output_items(chapter)
    _validate_preferred_lens(chapter)
    _validate_dependencies(chapter, known_chapter_ids)
    _validate_audit_focus(chapter)
    _validate_internal_subcontracts(chapter)


def _validate_non_empty_unique_clause_ids(
    clauses: tuple[MustAnswerClause, ...] | tuple[MustNotCoverClause, ...],
    field_name: str,
    chapter_id: int,
) -> None:
    """校验 clause id 非空且局部唯一。

    Args:
        clauses: 待校验的 clause 序列。
        field_name: 字段名。
        chapter_id: 当前章节编号。

    Returns:
        校验通过时返回 `None`。

    Raises:
        ValueError: clause 为空、id 为空、文本为空或 id 重复时抛出。
    """

    if not clauses:
        raise ValueError(f"typed 章节 {chapter_id} {field_name} 不能为空")
    clause_ids = tuple(clause.clause_id for clause in clauses)
    if len(set(clause_ids)) != len(clause_ids):
        raise ValueError(f"typed 章节 {chapter_id} {field_name} clause_id 存在重复")
    for clause in clauses:
        if not clause.clause_id.strip():
            raise ValueError(f"typed 章节 {chapter_id} {field_name} clause_id 不能为空")
        if not clause.clause_id.startswith(f"ch{chapter_id}.{field_name}."):
            raise ValueError(f"typed 章节 {chapter_id} {field_name} clause_id 前缀不稳定")
        if not clause.text.strip():
            raise ValueError(f"typed 章节 {chapter_id} {field_name} text 不能为空")
        if isinstance(clause, MustNotCoverClause):
            _validate_must_not_cover_clause(chapter_id, clause)


def _validate_must_not_cover_clause(chapter_id: int, clause: MustNotCoverClause) -> None:
    """校验 typed must_not_cover clause。

    Args:
        chapter_id: 当前章节编号。
        clause: 待校验的 must_not_cover clause。

    Returns:
        校验通过时返回 `None`。

    Raises:
        ValueError: evidence predicate 或 allowed_contexts 不满足闭集约束时抛出。
    """

    if clause.applies_when is not None:
        _validate_evidence_predicate(chapter_id, clause.applies_when)
    for context in clause.allowed_contexts:
        if context not in SUPPORTED_ALLOWED_CONTEXTS:
            raise ValueError(f"typed 章节 {chapter_id} allowed_context 不受支持：{context}")


def _validate_evidence_predicate(chapter_id: int, predicate: EvidencePredicate) -> None:
    """校验证据谓词数据。

    Args:
        chapter_id: 当前章节编号。
        predicate: 待校验的证据谓词。

    Returns:
        校验通过时返回 `None`。

    Raises:
        ValueError: 谓词 id、requirement id、证据状态或说明无效时抛出。
    """

    if not predicate.predicate_id.strip():
        raise ValueError(f"typed 章节 {chapter_id} evidence predicate id 不能为空")
    if not predicate.requirement_ids:
        raise ValueError(f"typed 章节 {chapter_id} evidence predicate requirement_ids 不能为空")
    if any(not requirement_id.strip() for requirement_id in predicate.requirement_ids):
        raise ValueError(f"typed 章节 {chapter_id} evidence predicate requirement_id 不能为空")
    if not predicate.required_statuses:
        raise ValueError(f"typed 章节 {chapter_id} evidence predicate statuses 不能为空")
    for status in predicate.required_statuses:
        if status not in SUPPORTED_EVIDENCE_STATUSES:
            raise ValueError(f"typed 章节 {chapter_id} evidence status 不受支持：{status}")
    if not predicate.description.strip():
        raise ValueError(f"typed 章节 {chapter_id} evidence predicate description 不能为空")


def _validate_required_output_items(chapter: TypedChapterContract) -> None:
    """校验 required output 条目。

    Args:
        chapter: 当前 typed 章节契约。

    Returns:
        校验通过时返回 `None`。

    Raises:
        ValueError: required output 条目为空、id 重复、文本为空或缺证行为不在闭集中时抛出。
    """

    if not chapter.required_output_items:
        raise ValueError(f"typed 章节 {chapter.chapter_id} required_output_items 不能为空")
    item_ids = tuple(item.item_id for item in chapter.required_output_items)
    if len(set(item_ids)) != len(item_ids):
        raise ValueError(f"typed 章节 {chapter.chapter_id} required_output item_id 存在重复")
    for item in chapter.required_output_items:
        if not item.item_id.strip():
            raise ValueError(f"typed 章节 {chapter.chapter_id} required_output item_id 不能为空")
        if not item.item_id.startswith(f"ch{chapter.chapter_id}.required_output."):
            raise ValueError(f"typed 章节 {chapter.chapter_id} required_output item_id 前缀不稳定")
        if not item.text.strip():
            raise ValueError(f"typed 章节 {chapter.chapter_id} required_output text 不能为空")
        if (
            item.when_evidence_missing is not None
            and item.when_evidence_missing not in SUPPORTED_MISSING_EVIDENCE_BEHAVIORS
        ):
            raise ValueError(
                f"typed 章节 {chapter.chapter_id} missing evidence behavior 不受支持："
                f"{item.when_evidence_missing}"
            )
        if item.missing_evidence_reason is not None and not item.missing_evidence_reason.strip():
            raise ValueError(f"typed 章节 {chapter.chapter_id} missing evidence reason 不能为空")
        if item.when_evidence_missing == "delete_if_not_applicable" and item.missing_evidence_reason is None:
            raise ValueError(f"typed 章节 {chapter.chapter_id} delete_if_not_applicable 缺少 typed reason")


def _validate_preferred_lens(chapter: TypedChapterContract) -> None:
    """校验 typed preferred_lens 规则。

    Args:
        chapter: 当前 typed 章节契约。

    Returns:
        校验通过时返回 `None`。

    Raises:
        ValueError: preferred_lens 为空、key 与 fund_type 不一致或 lens 内容为空时抛出。
    """

    if not chapter.preferred_lens:
        raise ValueError(f"typed 章节 {chapter.chapter_id} preferred_lens 不能为空")
    for key, rule in chapter.preferred_lens.items():
        if key != rule.fund_type:
            raise ValueError(f"typed 章节 {chapter.chapter_id} lens key 与 fund_type 不一致：{key}")
        if not rule.statements:
            raise ValueError(f"typed 章节 {chapter.chapter_id} preferred_lens statements 不能为空")
        if any(not statement.strip() for statement in rule.statements):
            raise ValueError(f"typed 章节 {chapter.chapter_id} preferred_lens statements 存在空值")
        if any(not facet.strip() for facet in rule.facets_any):
            raise ValueError(f"typed 章节 {chapter.chapter_id} preferred_lens facets_any 存在空值")
        if rule.priority is not None and not rule.priority.strip():
            raise ValueError(f"typed 章节 {chapter.chapter_id} preferred_lens priority 不能为空")


def _validate_dependencies(
    chapter: TypedChapterContract,
    known_chapter_ids: frozenset[int],
) -> None:
    """校验章节依赖。

    Args:
        chapter: 当前 typed 章节契约。
        known_chapter_ids: manifest 中已知公开章节 id。

    Returns:
        校验通过时返回 `None`。

    Raises:
        ValueError: dependency id 未知、重复，或第 0 章未消费第 7 章时抛出。
    """

    dependencies = chapter.consumes_chapter_conclusions
    if len(set(dependencies)) != len(dependencies):
        raise ValueError(f"typed 章节 {chapter.chapter_id} consumes_chapter_conclusions 存在重复")
    unknown = tuple(chapter_id for chapter_id in dependencies if chapter_id not in known_chapter_ids)
    if unknown:
        raise ValueError(f"typed 章节 {chapter.chapter_id} 存在未知 dependency id：{unknown}")
    if chapter.chapter_id == 0 and 7 not in dependencies:
        raise ValueError("typed 第 0 章必须消费第 7 章最终判断结论")
    if chapter.chapter_id == 0 and chapter.independent_action_source:
        raise ValueError("typed 第 0 章不得独立派生动作判断")


def _validate_audit_focus(chapter: TypedChapterContract) -> None:
    """校验 audit_focus 闭集。

    Args:
        chapter: 当前 typed 章节契约。

    Returns:
        校验通过时返回 `None`。

    Raises:
        ValueError: audit_focus 为空或包含闭集外值时抛出。
    """

    if not chapter.audit_focus:
        raise ValueError(f"typed 章节 {chapter.chapter_id} audit_focus 不能为空")
    for focus in chapter.audit_focus:
        if focus not in SUPPORTED_AUDIT_FOCUS:
            raise ValueError(f"typed 章节 {chapter.chapter_id} audit_focus 不受支持：{focus}")


def _validate_internal_subcontracts(chapter: TypedChapterContract) -> None:
    """校验章节内部子契约。

    Args:
        chapter: 当前 typed 章节契约。

    Returns:
        校验通过时返回 `None`。

    Raises:
        ValueError: 非第 2 章存在子契约、第 2 章缺子契约、子契约携带公开章节 id、
            或子契约编号无效时抛出。
    """

    if chapter.chapter_id != 2:
        if chapter.internal_subcontracts:
            raise ValueError(f"typed 章节 {chapter.chapter_id} 不允许内部子契约")
        return

    subcontract_ids = tuple(item.subcontract_id for item in chapter.internal_subcontracts)
    if subcontract_ids != ("performance", "attribution", "cost"):
        raise ValueError("typed 第 2 章内部子契约必须为 performance / attribution / cost")
    known_requirement_ids = {
        *(clause.clause_id for clause in chapter.must_answer),
        *(item.item_id for item in chapter.required_output_items),
    }
    for subcontract in chapter.internal_subcontracts:
        if subcontract.public_chapter_id is not None:
            raise ValueError("typed 第 2 章内部子契约不得携带公开 chapter_id")
        if not subcontract.title.strip():
            raise ValueError(f"typed 第 2 章内部子契约 {subcontract.subcontract_id} 标题不能为空")
        if not subcontract.requirement_ids:
            raise ValueError(
                f"typed 第 2 章内部子契约 {subcontract.subcontract_id} requirement_ids 不能为空"
            )
        if any(not requirement_id.strip() for requirement_id in subcontract.requirement_ids):
            raise ValueError(
                f"typed 第 2 章内部子契约 {subcontract.subcontract_id} requirement_id 不能为空"
            )
        unknown_ids = tuple(
            requirement_id
            for requirement_id in subcontract.requirement_ids
            if requirement_id not in known_requirement_ids
        )
        if unknown_ids:
            raise ValueError(
                f"typed 第 2 章内部子契约 {subcontract.subcontract_id} 存在未知 requirement_id："
                f"{unknown_ids}"
            )


__all__ = [
    "AUDIT_FOCUS_IS_SEMANTIC_ONLY",
    "EXPECTED_PUBLIC_CHAPTER_IDS",
    "TYPED_TEMPLATE_CONTRACT_SCHEMA_VERSION",
    "TYPED_TEMPLATE_CONTRACT_TEMPLATE_ID",
    "AllowedContextLiteral",
    "AuditFocusLiteral",
    "ChapterInternalSubcontract",
    "EvidenceAvailabilityStatus",
    "EvidencePredicate",
    "MissingEvidenceBehavior",
    "MustAnswerClause",
    "MustNotCoverClause",
    "RequiredOutputItem",
    "SUPPORTED_AUDIT_FOCUS",
    "SUPPORTED_MISSING_EVIDENCE_BEHAVIORS",
    "TemplateLensRule",
    "TypedChapterContract",
    "TypedTemplateContractManifest",
    "get_typed_chapter_contract",
    "load_typed_template_contract_manifest",
    "validate_typed_template_contract_manifest",
]
