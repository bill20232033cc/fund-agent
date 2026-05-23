"""preferred_lens 确定性应用计划。

本模块属于基金 Capability 的模板层，负责把 CHAPTER_CONTRACT 中的
preferred_lens 解析为渲染器可消费的确定性关注点。它不渲染报告、不读取
基金文档，也不执行 LLM 写作。
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final, get_args

from fund_agent.fund.fund_type import FundType
from fund_agent.fund.template.contracts import LensKey, resolve_preferred_lens

_DEFAULT_CHAPTER_IDS: Final[tuple[int, ...]] = tuple(range(8))
_SUPPORTED_FUND_TYPES: Final[tuple[FundType, ...]] = get_args(FundType)


@dataclass(frozen=True, slots=True)
class LensFocusLabels:
    """标准基金类型的确定性关注点标签。

    Attributes:
        primary_focus: 当前基金类型首要分析关注点。
        watch_variable_label: 第 0 章“当前最值得盯住的变量”使用的标签。
        risk_focus_label: 后续风险章节可复用的风险关注点标签。
    """

    primary_focus: str
    watch_variable_label: str
    risk_focus_label: str


@dataclass(frozen=True, slots=True)
class LensChapterApplication:
    """单章 preferred_lens 应用事实。

    Attributes:
        chapter_id: 模板章节编号。
        lens_key: 当前章节实际解析出的 lens key。
        used_default: 是否回退到 default lens。
        primary_focus: 当前基金类型首要分析关注点。
        watch_variable_label: 第 0 章变量 slot 可消费的关注点标签。
        risk_focus_label: 风险关注点标签。
        source_statements: CHAPTER_CONTRACT 中解析得到的原始 lens statement，仅用于追踪，不直接渲染。
    """

    chapter_id: int
    lens_key: LensKey
    used_default: bool
    primary_focus: str
    watch_variable_label: str | None
    risk_focus_label: str | None
    source_statements: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class LensApplicationPlan:
    """preferred_lens 应用计划。

    Attributes:
        fund_type: 请求应用的标准基金类型。
        chapters: 每个请求章节的 lens 应用事实。
    """

    fund_type: FundType
    chapters: tuple[LensChapterApplication, ...]


_FOCUS_LABELS_BY_FUND_TYPE: Final[dict[FundType, LensFocusLabels]] = {
    "active_fund": LensFocusLabels(
        primary_focus="基金经理、超额收益稳定性、言行一致性",
        watch_variable_label="基金经理言行一致性与超额收益稳定性",
        risk_focus_label="基金经理变更、风格漂移或超额收益失效",
    ),
    "index_fund": LensFocusLabels(
        primary_focus="跟踪误差、费率、规模/流动性",
        watch_variable_label="跟踪误差、费率和规模流动性",
        risk_focus_label="跟踪误差扩大、规模过小或流动性恶化",
    ),
    "bond_fund": LensFocusLabels(
        primary_focus="信用风险、久期稳定性、最大回撤",
        watch_variable_label="信用风险、久期稳定性和最大回撤",
        risk_focus_label="信用风险暴露、久期漂移或回撤失控",
    ),
    "enhanced_index": LensFocusLabels(
        primary_focus="超额收益稳定性、跟踪误差、费率",
        watch_variable_label="指数增强超额收益来源与跟踪误差",
        risk_focus_label="增强失效、跟踪误差扩大或费率侵蚀",
    ),
    "qdii_fund": LensFocusLabels(
        primary_focus="汇率风险、跨境市场暴露、成本",
        watch_variable_label="汇率风险、跟踪或管理能力和费率",
        risk_focus_label="汇率波动、跨境市场暴露或流动性风险",
    ),
    "fof_fund": LensFocusLabels(
        primary_focus="底层基金配置、双重费率、组合分散度",
        watch_variable_label="底层基金配置、双重费率和分散度",
        risk_focus_label="底层基金重叠、双重费率或配置失衡",
    ),
}


def build_lens_application_plan(
    fund_type: FundType,
    chapter_ids: tuple[int, ...] = _DEFAULT_CHAPTER_IDS,
) -> LensApplicationPlan:
    """构建 preferred_lens 应用计划。

    Args:
        fund_type: 标准基金类型。
        chapter_ids: 需要解析 lens 的模板章节编号。

    Returns:
        可供渲染器消费的 lens 应用计划。

    Raises:
        ValueError: 基金类型不受支持、章节列表为空、章节重复、章节越界或 lens 无法解析时抛出。
    """

    _validate_lens_application_inputs(fund_type=fund_type, chapter_ids=chapter_ids)
    focus_labels = _FOCUS_LABELS_BY_FUND_TYPE[fund_type]
    chapters = tuple(
        _build_lens_chapter_application(
            fund_type=fund_type,
            chapter_id=chapter_id,
            focus_labels=focus_labels,
        )
        for chapter_id in chapter_ids
    )
    return LensApplicationPlan(fund_type=fund_type, chapters=chapters)


def _validate_lens_application_inputs(
    *,
    fund_type: str,
    chapter_ids: tuple[int, ...],
) -> None:
    """校验 lens 应用计划入参。

    Args:
        fund_type: 待校验基金类型。
        chapter_ids: 待校验章节编号列表。

    Returns:
        校验通过时返回 `None`。

    Raises:
        ValueError: 基金类型不受支持、章节列表为空、章节重复或章节越界时抛出。
    """

    if fund_type not in _SUPPORTED_FUND_TYPES:
        raise ValueError(f"不支持的基金类型：{fund_type}")
    if not chapter_ids:
        raise ValueError("preferred_lens 应用章节不能为空")
    if len(set(chapter_ids)) != len(chapter_ids):
        raise ValueError(f"preferred_lens 应用章节存在重复：{chapter_ids}")
    invalid_chapter_ids = tuple(chapter_id for chapter_id in chapter_ids if chapter_id not in _DEFAULT_CHAPTER_IDS)
    if invalid_chapter_ids:
        raise ValueError(f"preferred_lens 应用章节越界：{invalid_chapter_ids}")


def _build_lens_chapter_application(
    *,
    fund_type: FundType,
    chapter_id: int,
    focus_labels: LensFocusLabels,
) -> LensChapterApplication:
    """构建单章 preferred_lens 应用事实。

    Args:
        fund_type: 标准基金类型。
        chapter_id: 模板章节编号。
        focus_labels: 当前基金类型对应的确定性关注点标签。

    Returns:
        单章 lens 应用事实。

    Raises:
        ValueError: 当前章节 lens 无法解析时由 `resolve_preferred_lens()` 抛出。
    """

    lens = resolve_preferred_lens(chapter_id, fund_type)
    return LensChapterApplication(
        chapter_id=chapter_id,
        lens_key=lens.fund_type,
        used_default=lens.fund_type == "default",
        primary_focus=focus_labels.primary_focus,
        watch_variable_label=focus_labels.watch_variable_label,
        risk_focus_label=focus_labels.risk_focus_label,
        source_statements=lens.statements,
    )
