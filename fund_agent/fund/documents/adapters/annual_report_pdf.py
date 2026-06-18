"""年报 PDF 适配器。

该适配器负责把底层 PDF 下载与解析 helper 适配为统一的 `ParsedAnnualReport`
契约，供文档仓库对外返回稳定对象。
"""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Callable

from fund_agent.fund.documents.models import (
    AnnualReportPdfFetchResult,
    DocumentKey,
    ParsedAnnualReport,
    ParsedTable,
    ReportSection,
)
from fund_agent.fund.documents.sources import AnnualReportSourceOrchestrator
from fund_agent.fund.pdf.parser import extract_tables, extract_text, locate_sections

SectionOffsets = dict[str, tuple[int, int]]
TablePayload = dict[str, object]
TextExtractor = Callable[[Path], str]
TableExtractor = Callable[[Path], list[TablePayload]]
SectionLocator = Callable[[str], SectionOffsets]

_SECTION_MATCH_RULE = "fund_agent.fund.pdf.parser.locate_sections"
_SECTION_CONFIDENCE = 1.0


def _extract_section_title(raw_text: str, start_offset: int) -> str:
    """从全文中提取章节标题行。

    Args:
        raw_text: 年报全文。
        start_offset: 章节起始位置。

    Returns:
        章节标题行；如果当前行为空，则回退为空字符串。

    Raises:
        无显式抛出；若 ``start_offset`` 越界，将按字符串切片语义返回空字符串。
    """

    line_end = raw_text.find("\n", start_offset)
    if line_end == -1:
        return raw_text[start_offset:].strip()
    return raw_text[start_offset:line_end].strip()


def _build_sections(raw_text: str, section_offsets: SectionOffsets) -> dict[str, ReportSection]:
    """把 parser 的章节偏移结果转换为仓库公共模型。

    Args:
        raw_text: 年报全文。
        section_offsets: parser 返回的章节偏移映射。

    Returns:
        章节编号到 `ReportSection` 的映射。

    Raises:
        无显式抛出；若章节偏移非法，标题提取可能返回空字符串。
    """

    sections: dict[str, ReportSection] = {}
    for section_id, (start_offset, end_offset) in section_offsets.items():
        title = _extract_section_title(raw_text, start_offset) or section_id
        sections[section_id] = ReportSection(
            section_id=section_id,
            title=title,
            start_offset=start_offset,
            end_offset=end_offset,
            matched_rule=_SECTION_MATCH_RULE,
            confidence=_SECTION_CONFIDENCE,
        )
    return sections


def _normalize_page_number(raw_table: TablePayload) -> int:
    """规范化表格页码。

    Args:
        raw_table: parser 返回的单个原始表格。

    Returns:
        规范化后的页码整数。

    Raises:
        ValueError: 当页码字段缺失或无法转换为整数时抛出。
    """

    raw_page_number = raw_table.get("page_number")
    try:
        return int(raw_page_number)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"page_number 非法: {raw_page_number!r}") from exc


def _resolve_table_index(
    raw_table: TablePayload,
    page_number: int,
    page_table_counters: dict[int, int],
) -> int:
    """计算表格在所在页中的序号。

    Args:
        raw_table: parser 返回的单个原始表格。
        page_number: 该表格所在页码。
        page_table_counters: 各页当前已分配的表格序号计数器。

    Returns:
        当前表格在所在页中的序号，从 0 开始。

    Raises:
        ValueError: 当显式传入的 ``table_index`` 无法转换为整数时抛出。
    """

    raw_table_index = raw_table.get("table_index")
    if raw_table_index is None:
        table_index = page_table_counters.get(page_number, 0)
    else:
        try:
            table_index = int(raw_table_index)
        except (TypeError, ValueError) as exc:
            raise ValueError(f"table_index 非法: {raw_table_index!r}") from exc
    page_table_counters[page_number] = max(
        page_table_counters.get(page_number, 0),
        table_index + 1,
    )
    return table_index


def _build_tables(raw_tables: list[TablePayload]) -> tuple[ParsedTable, ...]:
    """把 parser 的表格结果转换为仓库公共模型。

    Args:
        raw_tables: parser 返回的原始表格列表。

    Returns:
        规范化后的表格元组。

    Raises:
        ValueError: 当页码无法转换为整数时抛出。
    """

    normalized_tables: list[ParsedTable] = []
    page_table_counters: dict[int, int] = {}
    for raw_table in raw_tables:
        page_number = _normalize_page_number(raw_table)
        table_index = _resolve_table_index(raw_table, page_number, page_table_counters)
        headers = tuple(str(value) for value in raw_table.get("headers", []))
        rows = tuple(
            tuple(str(cell) for cell in row)
            for row in raw_table.get("rows", [])
        )
        normalized_tables.append(
            ParsedTable(
                page_number=page_number,
                table_index=table_index,
                headers=headers,
                rows=rows,
            )
        )
    return tuple(normalized_tables)


class AnnualReportPdfAdapter:
    """基于 EID single-source 来源编排和 PDF parser 的年报加载器。

    P1-S1 不修改 parser 能力本身，只负责把现有 helper 适配到统一仓库契约。
    """

    def __init__(
        self,
        source_orchestrator: AnnualReportSourceOrchestrator | None = None,
        text_extractor: TextExtractor = extract_text,
        table_extractor: TableExtractor = extract_tables,
        section_locator: SectionLocator = locate_sections,
    ) -> None:
        """初始化 PDF 适配器。

        Args:
            source_orchestrator: 年报来源编排器；未提供时使用当前默认 EID 来源。
            text_extractor: PDF 全文提取函数。
            table_extractor: PDF 表格提取函数。
            section_locator: 章节定位函数。

        Returns:
            无返回值。

        Raises:
            无显式抛出。
        """

        self._source_orchestrator = source_orchestrator or AnnualReportSourceOrchestrator()
        self._text_extractor = text_extractor
        self._table_extractor = table_extractor
        self._section_locator = section_locator

    async def fetch_pdf(
        self,
        fund_code: str,
        year: int,
        *,
        force_refresh: bool = False,
    ) -> AnnualReportPdfFetchResult:
        """确保原始 PDF 已下载到本地并返回路径与来源元数据。

        Args:
            fund_code: 基金代码。
            year: 年报年份。
            force_refresh: 是否强制刷新底层 PDF 缓存。

        Returns:
            本地 PDF 文件路径和同一次来源调用产生的元数据。

        Raises:
            FileNotFoundError: 未找到对应年报时抛出。
            Exception: 允许底层下载异常直接传播。
        """

        result = await self._source_orchestrator.fetch_annual_report_pdf(
            fund_code,
            year,
            force_refresh=force_refresh,
        )
        return AnnualReportPdfFetchResult(
            pdf_path=result.pdf_path,
            source_metadata=result.metadata,
        )

    async def fetch_pdf_path(
        self,
        fund_code: str,
        year: int,
        *,
        force_refresh: bool = False,
    ) -> Path:
        """确保原始 PDF 已下载到本地并返回其路径。

        Args:
            fund_code: 基金代码。
            year: 年报年份。
            force_refresh: 是否强制刷新底层 PDF 缓存。

        Returns:
            本地 PDF 文件路径。

        Raises:
            FileNotFoundError: 未找到对应年报时抛出。
            Exception: 允许底层下载异常直接传播。
        """

        result = await self.fetch_pdf(
            fund_code,
            year,
            force_refresh=force_refresh,
        )
        return result.pdf_path

    async def parse_pdf(
        self,
        pdf_path: Path,
        fund_code: str,
        year: int,
    ) -> ParsedAnnualReport:
        """基于本地 PDF 路径解析统一年报对象。

        Args:
            pdf_path: 本地 PDF 路径。
            fund_code: 基金代码。
            year: 年报年份。

        Returns:
            统一的年报解析对象。

        Raises:
            Exception: 允许底层文本提取、表格提取或章节定位异常直接传播。
        """

        # parser 仍是同步实现，P1-S1 fix 只在适配层把阻塞调用隔离到线程。
        raw_text = await asyncio.to_thread(self._text_extractor, pdf_path)
        raw_tables = await asyncio.to_thread(self._table_extractor, pdf_path)
        section_offsets = await asyncio.to_thread(self._section_locator, raw_text)
        return ParsedAnnualReport(
            key=DocumentKey(fund_code=fund_code, year=year),
            raw_text=raw_text,
            sections=_build_sections(raw_text, section_offsets),
            tables=_build_tables(raw_tables),
        )

    async def load_annual_report(
        self,
        fund_code: str,
        year: int,
        *,
        force_refresh: bool = False,
    ) -> ParsedAnnualReport:
        """下载并解析指定基金年报。

        Args:
            fund_code: 基金代码。
            year: 年报年份。
            force_refresh: 是否强制刷新底层 PDF 缓存。

        Returns:
            统一的年报解析对象。

        Raises:
            FileNotFoundError: 未找到对应年报时抛出。
            Exception: 允许底层下载、文本提取、表格提取或章节定位异常直接传播。
        """

        pdf_path = await self.fetch_pdf_path(
            fund_code,
            year,
            force_refresh=force_refresh,
        )
        return await self.parse_pdf(
            pdf_path,
            fund_code,
            year,
        )
