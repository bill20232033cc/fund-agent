"""基金 extractor 数据模型。"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Generic, Literal, TypeVar

ExtractedValueT = TypeVar("ExtractedValueT")
ExtractionMode = Literal["direct", "derived", "estimated", "missing"]
EvidenceSourceKind = Literal["annual_report", "external_api", "derived"]


@dataclass(frozen=True, slots=True)
class EvidenceAnchor:
    """证据锚点。

    Attributes:
        source_kind: 证据来源类型。
        document_year: 文档年份；非文档来源时可为 `None`。
        section_id: 年报章节编号。
        page_number: 页码；当前 `§1/§2` 文本抽取阶段可为 `None`。
        table_id: 表格标识；当前文本抽取阶段可为 `None`。
        row_locator: 行级定位说明。
        note: 附加说明，通常记录命中的原始行文本。
    """

    source_kind: EvidenceSourceKind
    document_year: int | None
    section_id: str | None
    page_number: int | None
    table_id: str | None
    row_locator: str | None
    note: str | None


@dataclass(frozen=True, slots=True)
class ExtractedField(Generic[ExtractedValueT]):
    """带证据的抽取字段。

    Attributes:
        value: 抽取到的结构化值；缺失时可为 `None`。
        anchors: 证据锚点列表。
        extraction_mode: 抽取模式。
        note: 附加说明。
    """

    value: ExtractedValueT | None
    anchors: tuple[EvidenceAnchor, ...]
    extraction_mode: ExtractionMode
    note: str | None = None


@dataclass(frozen=True, slots=True)
class ProfileExtractionResult:
    """基础画像抽取结果。

    Attributes:
        basic_identity: 基础身份信息。
        product_profile: 产品本质与投资范围摘要。
        benchmark: 业绩比较基准信息。
        index_profile: 指数画像信息，见模板第 1 章“指数编制规则与成分股”。
        fee_schedule: 费率信息。
    """

    basic_identity: ExtractedField[dict[str, object]]
    product_profile: ExtractedField[dict[str, object]]
    benchmark: ExtractedField[dict[str, object]]
    index_profile: ExtractedField["IndexProfileValue"]
    fee_schedule: ExtractedField[dict[str, object]]


@dataclass(frozen=True, slots=True)
class PerformanceExtractionResult:
    """`§3` 表现抽取结果。

    Attributes:
        nav_benchmark_performance: 净值增长率与业绩基准收益率。
        investor_return: 投资者收益率披露或 fallback 状态。
        tracking_error: 年报直接披露的跟踪误差，见模板第 2 章 R=A+B-C。
    """

    nav_benchmark_performance: ExtractedField[dict[str, object]]
    investor_return: ExtractedField[dict[str, object]]
    tracking_error: ExtractedField["TrackingErrorValue"]


@dataclass(frozen=True, slots=True)
class IndexProfileValue:
    """指数画像结构化值，见模板第 1 章“这只基金到底是什么产品”。

    Attributes:
        benchmark_text: 年报披露的业绩比较基准文本。
        benchmark_identity_status: 基准身份识别状态。
        benchmark_index_name: 可确定的单一指数名称。
        benchmark_index_code: 可确定的指数代码；禁止从基金代码猜测。
        benchmark_component_text: 复合基准组成文本。
        methodology_availability: 编制方法可用性层级。
        methodology_summary: 编制方法摘要。
        methodology_source_title: 编制方法来源标题。
        constituents_availability: 成分股可用性层级。
        constituents_summary: 成分股摘要。
        constituents_as_of_date: 成分股日期。
        source_tier: 当前画像来源层级。
        missing_reasons: 缺失或不可用原因。
    """

    benchmark_text: str | None
    benchmark_identity_status: Literal["identified", "composite", "ambiguous", "missing"]
    benchmark_index_name: str | None
    benchmark_index_code: str | None
    benchmark_component_text: tuple[str, ...]
    methodology_availability: Literal[
        "direct_disclosure",
        "source_reference",
        "benchmark_only",
        "missing",
    ]
    methodology_summary: str | None
    methodology_source_title: str | None
    constituents_availability: Literal[
        "direct_disclosure",
        "source_reference",
        "benchmark_only",
        "missing",
    ]
    constituents_summary: str | None
    constituents_as_of_date: str | None
    source_tier: Literal["annual_report", "prospectus", "index_document", "benchmark_context", "missing"]
    missing_reasons: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class TrackingErrorValue:
    """跟踪误差结构化值，见模板第 2 章 R=A+B-C。

    Attributes:
        value: 标准化小数比例，例如 `0.015` 表示 `1.5%`。
        value_text: 年报披露原文数值。
        unit: 数值单位，当前固定为比例。
        period_label: 跟踪误差对应期间。
        period_start: 期间开始日期；直接披露无法确定时为 `None`。
        period_end: 期间结束日期；直接披露无法确定时为 `None`。
        annualized: 是否年化。
        source_type: 来源类型。
        calculation_method: 计算或披露方法。
        benchmark_identity_status: 基准身份识别状态。
        benchmark_index_name: 可确定的单一指数名称。
        benchmark_index_code: 可确定的指数代码。
        fund_series_source: 基金序列来源；直接披露为 `None`。
        index_series_source: 指数序列来源；直接披露为 `None`。
        observation_count: 观测数量；直接披露为 `None`。
        frequency: 数据频率。
        annualization_factor: 年化因子；直接披露为 `None`。
        input_period_complete: 输入期间是否完整。
        provenance_note: 来源和证据边界说明。
    """

    value: Decimal
    value_text: str
    unit: Literal["ratio"]
    period_label: str
    period_start: str | None
    period_end: str | None
    annualized: bool
    source_type: Literal["direct_disclosure", "calculated_from_series"]
    calculation_method: Literal["disclosed", "annualized_stddev_active_return"]
    benchmark_identity_status: Literal["identified", "composite", "ambiguous", "missing"]
    benchmark_index_name: str | None
    benchmark_index_code: str | None
    fund_series_source: str | None
    index_series_source: str | None
    observation_count: int | None
    frequency: Literal["daily", "weekly", "monthly", "annual_report_period"]
    annualization_factor: Decimal | None
    input_period_complete: bool
    provenance_note: str


@dataclass(frozen=True, slots=True)
class ManagerOwnershipExtractionResult:
    """`§4/§8/§9` 管理人文本、换手率、利益一致性与持有人结构抽取结果。

    Attributes:
        manager_strategy_text: 管理人报告中的策略与展望原文。
        turnover_rate: 年报 `§8` 披露的换手率。
        manager_alignment: 年报 `§9` 披露的基金经理/从业人员持有原始数据。
        holder_structure: 年报 `§9` 披露的机构/个人持有人结构。
    """

    manager_strategy_text: ExtractedField[dict[str, object]]
    turnover_rate: ExtractedField[dict[str, object]]
    manager_alignment: ExtractedField[dict[str, object]]
    holder_structure: ExtractedField[dict[str, object]]


@dataclass(frozen=True, slots=True)
class HoldingsShareChangeExtractionResult:
    """`§8/§10` 持仓快照与份额变动抽取结果。

    Attributes:
        holdings_snapshot: 前十大重仓与行业分布原始披露。
        share_change: 期初份额、期末份额和净变动原始披露。
    """

    holdings_snapshot: ExtractedField[dict[str, object]]
    share_change: ExtractedField[dict[str, object]]
