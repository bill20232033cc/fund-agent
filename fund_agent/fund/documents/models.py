"""基金文档仓库公共数据模型。

这些模型承载年报解析后的稳定契约，供后续模板第 1-4 章与证据锚点提取使用。
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final, Literal

# P1-S1 当前只支持年报文档类型，避免在多个模块散落同一个魔法字符串。
ANNUAL_REPORT_DOCUMENT_KIND: Final[Literal["annual_report"]] = "annual_report"


@dataclass(frozen=True, slots=True)
class DocumentKey:
    """年报文档唯一标识。

    Attributes:
        fund_code: 基金代码。
        year: 报告年份。
        document_kind: 文档类型，P1-S1 仅支持 annual_report。
    """

    fund_code: str
    year: int
    document_kind: Literal["annual_report"] = ANNUAL_REPORT_DOCUMENT_KIND


@dataclass(frozen=True, slots=True)
class ReportSection:
    """年报章节索引。

    Attributes:
        section_id: 章节编号，如 ``§3``。
        title: 章节标题行。
        start_offset: 章节在全文中的起始偏移。
        end_offset: 章节在全文中的结束偏移。
        matched_rule: 当前用于定位章节的规则来源。
        confidence: 当前章节定位结果的置信度。
    """

    section_id: str
    title: str
    start_offset: int
    end_offset: int
    matched_rule: str
    confidence: float


@dataclass(frozen=True, slots=True)
class ParsedTable:
    """年报表格结构化结果。

    Attributes:
        page_number: 表格所在页码，从 1 开始。
        table_index: 同页内的表格序号，从 0 开始。
        headers: 表头元组。
        rows: 表格数据行。
    """

    page_number: int
    table_index: int
    headers: tuple[str, ...]
    rows: tuple[tuple[str, ...], ...]


@dataclass(frozen=True, slots=True)
class ParsedAnnualReport:
    """统一年报读取结果。

    Attributes:
        key: 文档主键。
        raw_text: 全文文本。
        sections: 章节索引映射。
        tables: 结构化表格列表。
    """

    key: DocumentKey
    raw_text: str
    sections: dict[str, ReportSection]
    tables: tuple[ParsedTable, ...]

    def get_section_text(self, section_id: str) -> str | None:
        """按章节编号返回正文片段。

        Args:
            section_id: 章节编号，如 ``§4``。

        Returns:
            命中时返回章节文本；未命中时返回 ``None``。

        Raises:
            无显式抛出；若对象状态被外部破坏，可能传播底层切片异常。
        """

        section = self.sections.get(section_id)
        if section is None:
            return None
        return self.raw_text[section.start_offset:section.end_offset].strip()
