"""基金 extractor 数据模型。"""

from __future__ import annotations

from dataclasses import dataclass
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
        fee_schedule: 费率信息。
    """

    basic_identity: ExtractedField[dict[str, object]]
    product_profile: ExtractedField[dict[str, object]]
    benchmark: ExtractedField[dict[str, object]]
    fee_schedule: ExtractedField[dict[str, object]]


@dataclass(frozen=True, slots=True)
class PerformanceExtractionResult:
    """`§3` 表现抽取结果。

    Attributes:
        nav_benchmark_performance: 净值增长率与业绩基准收益率。
        investor_return: 投资者收益率披露或 fallback 状态。
    """

    nav_benchmark_performance: ExtractedField[dict[str, object]]
    investor_return: ExtractedField[dict[str, object]]
