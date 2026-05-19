"""`§3` 净值表现与投资者收益率抽取。"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Final

from fund_agent.fund.documents.models import ParsedAnnualReport, ParsedTable
from fund_agent.fund.extractors.models import (
    EvidenceAnchor,
    ExtractedField,
    PerformanceExtractionResult,
)

_SECTION_ID: Final[str] = "§3"
_FIELD_PATTERNS: Final[dict[str, tuple[str, ...]]] = {
    "nav_growth_rate": (
        r"基金份额净值增长率\s*[：:]\s*(.+)",
        r"净值增长率\s*[：:]\s*(.+)",
    ),
    "benchmark_return_rate": (
        r"业绩比较基准收益率\s*[：:]\s*(.+)",
        r"基准收益率\s*[：:]\s*(.+)",
    ),
    "investor_return_rate": (
        r"加权平均投资者收益率\s*[：:]\s*(.+)",
        r"投资者收益率\s*[：:]\s*(.+)",
    ),
    "estimated_investor_return_rate": (
        r"加权平均投资者收益率（估算）\s*[：:]\s*(.+)",
        r"投资者收益率（估算）\s*[：:]\s*(.+)",
        r"估算投资者收益率\s*[：:]\s*(.+)",
    ),
}
_NAV_BENCHMARK_TABLE_HEADERS: Final[tuple[str, ...]] = ("阶段", "净值增长率", "业绩比较基准收益率")
_NAV_BENCHMARK_PREFERRED_PERIODS: Final[tuple[str, ...]] = ("过去一年", "过去一年内")


@dataclass(frozen=True, slots=True)
class _MatchedField:
    """`§3` 字段命中结果。

    Attributes:
        field_name: 字段名。
        value: 抽取到的字段值。
        matched_line: 命中的原始行文本。
    """

    field_name: str
    value: str
    matched_line: str


@dataclass(frozen=True, slots=True)
class _MatchedTableField:
    """`§3` 表格字段命中结果。

    Attributes:
        field_name: 字段名。
        value: 抽取到的字段值。
        table: 命中的表格。
        row_label: 命中的阶段行标签。
        matched_header: 命中的表头文本。
    """

    field_name: str
    value: str
    table: ParsedTable
    row_label: str
    matched_header: str


def _extract_field(report: ParsedAnnualReport, field_name: str) -> _MatchedField | None:
    """从 `§3` 中提取单个字段。

    Args:
        report: 已解析年报对象。
        field_name: 目标字段名。

    Returns:
        命中时返回字段命中结果，否则返回 `None`。

    Raises:
        KeyError: 请求未知字段时抛出。
    """

    section_text = report.get_section_text(_SECTION_ID)
    if not section_text:
        return None
    for line in section_text.splitlines():
        normalized_line = line.strip()
        for pattern in _FIELD_PATTERNS[field_name]:
            match = re.match(pattern, normalized_line)
            if match:
                return _MatchedField(
                    field_name=field_name,
                    value=match.group(1).strip(),
                    matched_line=normalized_line,
                )
    return None


def _normalize_cell(value: str) -> str:
    """规范化表格单元格文本。

    Args:
        value: 原始单元格文本。

    Returns:
        去除首尾空白后的文本。

    Raises:
        无显式抛出。
    """

    return value.strip()


def _compact_text(value: str) -> str:
    """压缩文本内部空白用于语义匹配。

    Args:
        value: 原始文本。

    Returns:
        移除全部空白后的文本。

    Raises:
        无显式抛出。
    """

    return re.sub(r"\s+", "", value)


def _table_text(table: ParsedTable) -> str:
    """拼接表格表头与行文本。

    Args:
        table: 待检查的表格。

    Returns:
        表格全文文本。

    Raises:
        无显式抛出。
    """

    cells = list(table.headers)
    for row in table.rows:
        cells.extend(row)
    return " ".join(_normalize_cell(cell) for cell in cells)


def _is_nav_benchmark_table(table: ParsedTable) -> bool:
    """判断表格是否为 `§3` 基金净值表现表，见模板第 2 章 R=A+B-C。

    Args:
        table: 待检查的表格。

    Returns:
        同时包含阶段、份额净值增长率和业绩比较基准收益率语义时返回 `True`。

    Raises:
        无显式抛出。
    """

    table_text = _compact_text(_table_text(table))
    return all(keyword in table_text for keyword in _NAV_BENCHMARK_TABLE_HEADERS)


def _find_header_index(
    headers: tuple[str, ...],
    required_keywords: tuple[str, ...],
    excluded_keywords: tuple[str, ...] = (),
) -> int | None:
    """按必含/排除关键词查找表头下标。

    Args:
        headers: 表头元组。
        required_keywords: 表头必须包含的语义关键词。
        excluded_keywords: 表头不得包含的语义关键词。

    Returns:
        命中时返回下标，否则返回 `None`。

    Raises:
        无显式抛出。
    """

    for index, header in enumerate(headers):
        normalized_header = _compact_text(header)
        if all(keyword in normalized_header for keyword in required_keywords) and not any(
            keyword in normalized_header for keyword in excluded_keywords
        ):
            return index
    return None


def _cell_at(row: tuple[str, ...], index: int | None) -> str | None:
    """安全读取行内单元格。

    Args:
        row: 表格行。
        index: 目标下标。

    Returns:
        下标有效且单元格非空时返回文本，否则返回 `None`。

    Raises:
        无显式抛出。
    """

    if index is None or index >= len(row):
        return None
    value = _normalize_cell(row[index])
    return value or None


def _select_nav_benchmark_row(table: ParsedTable, period_index: int | None) -> tuple[str, tuple[str, ...]] | None:
    """选择净值表现表中最适合作为年度表现的行。

    Args:
        table: 净值表现表。
        period_index: 阶段列下标。

    Returns:
        命中时返回阶段标签和行；否则返回 `None`。

    Raises:
        无显式抛出。
    """

    fallback: tuple[str, tuple[str, ...]] | None = None
    for row in table.rows:
        label = _cell_at(row, period_index)
        if label is None:
            continue
        if any(period in label for period in _NAV_BENCHMARK_PREFERRED_PERIODS):
            return label, row
        if fallback is None and "自基金合同生效" not in label:
            fallback = (label, row)
    return fallback


def _extract_nav_benchmark_table_fields(
    report: ParsedAnnualReport,
) -> tuple[_MatchedTableField | None, _MatchedTableField | None]:
    """从 `§3` 表格提取净值增长率与基准收益率。

    Args:
        report: 已解析年报对象。

    Returns:
        净值增长率与业绩比较基准收益率命中结果。

    Raises:
        无显式抛出。
    """

    for table in report.tables:
        if not _is_nav_benchmark_table(table):
            continue
        period_index = _find_header_index(table.headers, ("阶段",))
        nav_index = _find_header_index(table.headers, ("净值增长率",), ("标准差",))
        benchmark_index = _find_header_index(table.headers, ("业绩比较基准收益率",), ("标准差",))
        selected_row = _select_nav_benchmark_row(table, period_index)
        if selected_row is None:
            continue
        row_label, row = selected_row
        nav_value = _cell_at(row, nav_index)
        benchmark_value = _cell_at(row, benchmark_index)
        nav_match = None
        benchmark_match = None
        if nav_value is not None and nav_index is not None:
            nav_match = _MatchedTableField(
                field_name="nav_growth_rate",
                value=nav_value,
                table=table,
                row_label=row_label,
                matched_header=table.headers[nav_index],
            )
        if benchmark_value is not None and benchmark_index is not None:
            benchmark_match = _MatchedTableField(
                field_name="benchmark_return_rate",
                value=benchmark_value,
                table=table,
                row_label=row_label,
                matched_header=table.headers[benchmark_index],
            )
        return nav_match, benchmark_match
    return None, None


def _build_anchor(report: ParsedAnnualReport, matched_field: _MatchedField) -> EvidenceAnchor:
    """根据 `§3` 字段命中结果构造证据锚点。

    Args:
        report: 已解析年报对象。
        matched_field: 字段命中结果。

    Returns:
        对应的证据锚点。

    Raises:
        无显式抛出。
    """

    return EvidenceAnchor(
        source_kind="annual_report",
        document_year=report.key.year,
        section_id=_SECTION_ID,
        page_number=None,
        table_id=None,
        row_locator=matched_field.field_name,
        note=matched_field.matched_line,
    )


def _table_id(table: ParsedTable) -> str:
    """构造表格证据 ID。

    Args:
        table: 表格对象。

    Returns:
        可读的表格 ID。

    Raises:
        无显式抛出。
    """

    return f"page-{table.page_number}-table-{table.table_index}"


def _build_table_anchor(report: ParsedAnnualReport, matched_field: _MatchedTableField) -> EvidenceAnchor:
    """根据 `§3` 表格命中结果构造证据锚点。

    Args:
        report: 已解析年报对象。
        matched_field: 表格字段命中结果。

    Returns:
        对应的表格证据锚点。

    Raises:
        无显式抛出。
    """

    return EvidenceAnchor(
        source_kind="annual_report",
        document_year=report.key.year,
        section_id=_SECTION_ID,
        page_number=matched_field.table.page_number,
        table_id=_table_id(matched_field.table),
        row_locator=matched_field.field_name,
        note=f"{matched_field.row_label}; {matched_field.matched_header}",
    )


def _missing_field(note: str) -> ExtractedField[dict[str, object]]:
    """构造缺失状态字段。

    Args:
        note: 缺失说明。

    Returns:
        `missing` 模式的字段对象。

    Raises:
        无显式抛出。
    """

    return ExtractedField(
        value=None,
        anchors=(),
        extraction_mode="missing",
        note=note,
    )


def _build_nav_benchmark_performance(report: ParsedAnnualReport) -> ExtractedField[dict[str, object]]:
    """构造 `§3` 净值增长率与基准收益率字段。

    Args:
        report: 已解析年报对象。

    Returns:
        带证据的表现字段；若 `§3` 未披露则返回 `missing`。

    Raises:
        无显式抛出。
    """

    nav_growth_rate: _MatchedField | _MatchedTableField | None = _extract_field(
        report, "nav_growth_rate"
    )
    benchmark_return_rate: _MatchedField | _MatchedTableField | None = _extract_field(
        report, "benchmark_return_rate"
    )
    if nav_growth_rate is None or benchmark_return_rate is None:
        table_nav_growth_rate, table_benchmark_return_rate = _extract_nav_benchmark_table_fields(report)
        nav_growth_rate = nav_growth_rate or table_nav_growth_rate
        benchmark_return_rate = benchmark_return_rate or table_benchmark_return_rate
    if nav_growth_rate is None and benchmark_return_rate is None:
        return _missing_field("§3 未披露净值增长率/业绩比较基准收益率")
    anchors = []
    for matched_field in (nav_growth_rate, benchmark_return_rate):
        if matched_field is None:
            continue
        if isinstance(matched_field, _MatchedTableField):
            anchors.append(_build_table_anchor(report, matched_field))
        else:
            anchors.append(_build_anchor(report, matched_field))
    extraction_mode = "direct" if nav_growth_rate is not None and benchmark_return_rate is not None else "missing"
    note = None
    if extraction_mode == "missing":
        note = "§3 仅部分披露净值增长率/业绩比较基准收益率；当前显式保留缺失状态。"
    return ExtractedField(
        value={
            "nav_growth_rate": nav_growth_rate.value if nav_growth_rate else None,
            "benchmark_return_rate": benchmark_return_rate.value if benchmark_return_rate else None,
        },
        anchors=tuple(anchors),
        extraction_mode=extraction_mode,
        note=note,
    )


def _build_investor_return(report: ParsedAnnualReport) -> ExtractedField[dict[str, object]]:
    """构造投资者收益率字段。

    Args:
        report: 已解析年报对象。

    Returns:
        直接披露时返回 `direct`；当前未披露时返回 `missing`，并显式说明后续需要 fallback。

    Raises:
        无显式抛出。
    """

    investor_return_rate = _extract_field(report, "investor_return_rate")
    if investor_return_rate is not None:
        return ExtractedField(
            value={
                "investor_return_rate": investor_return_rate.value,
                "disclosure_status": "direct",
                "fallback_status": "not_needed",
            },
            anchors=(_build_anchor(report, investor_return_rate),),
            extraction_mode="direct",
            note=None,
        )

    estimated_investor_return_rate = _extract_field(report, "estimated_investor_return_rate")
    if estimated_investor_return_rate is not None:
        return ExtractedField(
            value={
                "investor_return_rate": estimated_investor_return_rate.value,
                "disclosure_status": "estimated",
                "fallback_status": "estimated_disclosure_in_section",
            },
            anchors=(_build_anchor(report, estimated_investor_return_rate),),
            extraction_mode="estimated",
            note="§3 以估算口径披露投资者收益率；当前按 estimated 返回。",
        )

    return ExtractedField(
        value={
            "investor_return_rate": None,
            "disclosure_status": "missing",
            "fallback_status": "pending_later_slice",
        },
        anchors=(),
        extraction_mode="missing",
        note="§3 未直接披露投资者收益率；当前 slice 仅显式标记 missing，后续再接入 fallback。",
    )


def extract_performance(report: ParsedAnnualReport) -> PerformanceExtractionResult:
    """抽取 `§3` 表现与投资者收益率结果。

    Args:
        report: 已解析年报对象。

    Returns:
        `nav_benchmark_performance` 与 `investor_return` 两类结果。

    Raises:
        无显式抛出。
    """

    return PerformanceExtractionResult(
        nav_benchmark_performance=_build_nav_benchmark_performance(report),
        investor_return=_build_investor_return(report),
    )
