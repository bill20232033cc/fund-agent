"""`§8/§10` 持仓快照与份额变动表格抽取。"""

from __future__ import annotations

from decimal import Decimal, InvalidOperation
from dataclasses import dataclass
from typing import Final

from fund_agent.fund.documents.models import ParsedAnnualReport, ParsedTable
from fund_agent.fund.extractors.models import (
    EvidenceAnchor,
    ExtractedField,
    HoldingsShareChangeExtractionResult,
)

_SECTION_PORTFOLIO: Final[str] = "§8"
_SECTION_SHARE_CHANGE: Final[str] = "§10"
_TOP_HOLDINGS_TABLE_KEYWORDS: Final[tuple[str, ...]] = ("前十大", "重仓")
_INDUSTRY_TABLE_KEYWORDS: Final[tuple[str, ...]] = ("行业", "占比")
_SHARE_CHANGE_REQUIRED_KEYWORDS: Final[tuple[str, ...]] = ("期初", "期末", "基金份额总额")
_SHARE_CHANGE_NET_KEYWORDS: Final[tuple[str, ...]] = ("净变动", "本期申购赎回净额")
_SHARE_CHANGE_FLOW_KEYWORDS: Final[tuple[str, ...]] = ("申购", "赎回")
_TOTAL_SHARE_HEADER_KEYWORDS: Final[tuple[str, ...]] = ("合计", "总计", "基金份额总额", "总份额")
_REASON_SINGLE_VALUE_COLUMN: Final[str] = "single_value_column"
_REASON_FUND_CODE_HEADER_MATCH: Final[str] = "fund_code_header_match"


@dataclass(frozen=True, slots=True)
class _TableMatch:
    """表格命中结果。

    Attributes:
        table: 命中的表格。
        table_kind: 表格类型。
    """

    table: ParsedTable
    table_kind: str


@dataclass(frozen=True, slots=True)
class _ShareColumnSelection:
    """份额变动表值列选择结果。

    Attributes:
        column_index: 表格列下标。
        header: 选中列表头。
        reason: 稳定选择原因。
    """

    column_index: int
    header: str
    reason: str


def _normalize_cell(value: str) -> str:
    """规范化单元格文本。

    Args:
        value: 原始单元格文本。

    Returns:
        去除首尾空白后的文本。

    Raises:
        无显式抛出。
    """

    return value.strip()


def _joined_table_text(table: ParsedTable) -> str:
    """拼接表头与表格行文本。

    Args:
        table: 待检查的表格。

    Returns:
        表格全部文本的拼接结果。

    Raises:
        无显式抛出。
    """

    cells = list(table.headers)
    for row in table.rows:
        cells.extend(row)
    return " ".join(_normalize_cell(cell) for cell in cells)


def _compact_text(value: str) -> str:
    """压缩文本内部空白用于语义匹配。

    Args:
        value: 原始文本。

    Returns:
        移除全部空白后的文本。

    Raises:
        无显式抛出。
    """

    return "".join(value.split())


def _table_contains_all(table: ParsedTable, keywords: tuple[str, ...]) -> bool:
    """判断表格是否包含全部关键词。

    Args:
        table: 待检查的表格。
        keywords: 必须同时出现的关键词。

    Returns:
        全部关键词存在时返回 `True`，否则返回 `False`。

    Raises:
        无显式抛出。
    """

    table_text = _compact_text(_joined_table_text(table))
    return all(keyword in table_text for keyword in keywords)


def _is_share_change_table(table: ParsedTable) -> bool:
    """判断是否为份额变动表。

    Args:
        table: 待检查的表格。

    Returns:
        同时包含期初、期末，并披露净变动或申购/赎回拆分时返回 `True`。

    Raises:
        无显式抛出。
    """

    table_text = _compact_text(_joined_table_text(table))
    has_required_keywords = all(keyword in table_text for keyword in _SHARE_CHANGE_REQUIRED_KEYWORDS)
    has_net_keyword = any(keyword in table_text for keyword in _SHARE_CHANGE_NET_KEYWORDS)
    has_flow_keywords = all(keyword in table_text for keyword in _SHARE_CHANGE_FLOW_KEYWORDS)
    return has_required_keywords and (has_net_keyword or has_flow_keywords)


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


def _build_table_anchor(report: ParsedAnnualReport, table: ParsedTable, section_id: str, row_locator: str) -> EvidenceAnchor:
    """构造表格型证据锚点。

    Args:
        report: 已解析年报对象。
        table: 命中的表格。
        section_id: 章节编号。
        row_locator: 行定位说明。

    Returns:
        表格型证据锚点。

    Raises:
        无显式抛出。
    """

    return EvidenceAnchor(
        source_kind="annual_report",
        document_year=report.key.year,
        section_id=section_id,
        page_number=table.page_number,
        table_id=_table_id(table),
        row_locator=row_locator,
        note="; ".join(table.headers),
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

    return ExtractedField(value=None, anchors=(), extraction_mode="missing", note=note)


def _find_table(report: ParsedAnnualReport, keywords: tuple[str, ...], table_kind: str) -> _TableMatch | None:
    """按关键词查找表格。

    Args:
        report: 已解析年报对象。
        keywords: 表格关键词。
        table_kind: 表格类型。

    Returns:
        命中时返回表格匹配结果，否则返回 `None`。

    Raises:
        无显式抛出。
    """

    for table in report.tables:
        if _table_contains_all(table, keywords):
            return _TableMatch(table=table, table_kind=table_kind)
    return None


def _find_share_change_table(report: ParsedAnnualReport) -> _TableMatch | None:
    """查找份额变动表。

    Args:
        report: 已解析年报对象。

    Returns:
        命中时返回份额变动表格，否则返回 `None`。

    Raises:
        无显式抛出。
    """

    for table in report.tables:
        if _is_share_change_table(table):
            return _TableMatch(table=table, table_kind="share_change")
    return None


def _row_to_dict(headers: tuple[str, ...], row: tuple[str, ...]) -> dict[str, str]:
    """按表头把一行表格转换为字典。

    Args:
        headers: 表头元组。
        row: 数据行。

    Returns:
        字段名到单元格文本的映射。

    Raises:
        无显式抛出。
    """

    return {
        _normalize_cell(header): _normalize_cell(row[index]) if index < len(row) else ""
        for index, header in enumerate(headers)
    }


def _extract_top_holdings(table: ParsedTable) -> list[dict[str, str]]:
    """从前十大重仓表中提取行数据。

    Args:
        table: 前十大重仓表。

    Returns:
        前十大重仓行数据列表。

    Raises:
        无显式抛出。
    """

    return [_row_to_dict(table.headers, row) for row in table.rows]


def _extract_industry_distribution(table: ParsedTable) -> list[dict[str, str]]:
    """从行业分布表中提取行数据。

    Args:
        table: 行业分布表。

    Returns:
        行业分布行数据列表。

    Raises:
        无显式抛出。
    """

    return [_row_to_dict(table.headers, row) for row in table.rows]


def _extract_share_change(
    table: ParsedTable,
    *,
    fund_code: str,
) -> dict[str, str | None] | None:
    """从份额变动表中提取期初、期末与净变动。

    Args:
        table: 份额变动表。
        fund_code: 当前基金代码，用于精确匹配份额列表头。

    Returns:
        份额变动结构化结果；多值列无法消歧时返回 `None`。

    Raises:
        无显式抛出。
    """

    selection = _select_share_change_value_column(table, fund_code=fund_code)
    if selection is None:
        return None
    value: dict[str, str | None] = {
        "beginning_share": None,
        "ending_share": None,
        "net_change": None,
        "share_class_column": selection.header,
        "share_class_selection_reason": selection.reason,
    }
    for row in table.rows:
        joined_row = _compact_text(" ".join(_normalize_cell(cell) for cell in row))
        if "期初" in joined_row:
            value["beginning_share"] = _extract_share_value_from_row(row, selection.column_index)
        elif "期末" in joined_row:
            value["ending_share"] = _extract_share_value_from_row(row, selection.column_index)
        elif "净变动" in joined_row or "本期申购赎回净额" in joined_row:
            value["net_change"] = _extract_share_value_from_row(row, selection.column_index)
    if value["net_change"] is None:
        value["net_change"] = _calculate_net_change(
            beginning_share=value["beginning_share"],
            ending_share=value["ending_share"],
        )
    return value


def _select_share_change_value_column(
    table: ParsedTable,
    *,
    fund_code: str,
) -> _ShareColumnSelection | None:
    """选择份额变动表的值列。

    Args:
        table: 份额变动表。
        fund_code: 当前基金代码。

    Returns:
        选中的列与原因；多列无法消歧时返回 `None`。

    Raises:
        无显式抛出。
    """

    value_columns = [
        (index, _normalize_cell(header))
        for index, header in enumerate(table.headers)
        if index > 0
    ]
    if len(value_columns) == 1:
        index, header = value_columns[0]
        return _ShareColumnSelection(
            column_index=index,
            header=header,
            reason=_REASON_SINGLE_VALUE_COLUMN,
        )
    code_matches = [
        (index, header)
        for index, header in value_columns
        if fund_code and fund_code in _compact_text(header)
    ]
    if len(code_matches) == 1:
        index, header = code_matches[0]
        return _ShareColumnSelection(
            column_index=index,
            header=header,
            reason=_REASON_FUND_CODE_HEADER_MATCH,
        )
    if code_matches:
        return None
    if any(_contains_fund_code(header) for _, header in value_columns):
        return None
    return None


def _contains_fund_code(header: str) -> bool:
    """判断表头是否包含 6 位基金代码。

    Args:
        header: 表头文本。

    Returns:
        包含任意连续 6 位数字时返回 `True`。

    Raises:
        无显式抛出。
    """

    compact_header = _compact_text(header)
    return any(
        compact_header[index : index + 6].isdigit()
        for index in range(max(len(compact_header) - 5, 0))
    )


def _is_total_share_header(header: str) -> bool:
    """判断表头是否为总份额列。

    Args:
        header: 表头文本。

    Returns:
        含总计/合计语义时返回 `True`。

    Raises:
        无显式抛出。
    """

    compact_header = _compact_text(header)
    return any(keyword in compact_header for keyword in _TOTAL_SHARE_HEADER_KEYWORDS)


def _extract_share_value_from_row(row: tuple[str, ...], column_index: int) -> str | None:
    """从份额变动表行的指定列读取份额值。

    Args:
        row: 份额变动表数据行。
        column_index: 已选中的值列下标。

    Returns:
        非空、非横杠值；不存在时返回 `None`。

    Raises:
        无显式抛出。
    """

    if column_index >= len(row):
        return None
    value = _normalize_cell(row[column_index])
    if value and value != "-":
        return value
    return None


def _calculate_net_change(beginning_share: str | None, ending_share: str | None) -> str | None:
    """用期末份额减期初份额计算净变动，见模板第 4 章“投资者获得感”。

    Args:
        beginning_share: 期初基金份额。
        ending_share: 期末基金份额。

    Returns:
        两个输入均可解析时返回净变动字符串，否则返回 `None`。

    Raises:
        无显式抛出。
    """

    if beginning_share is None or ending_share is None:
        return None
    try:
        beginning_value = Decimal(beginning_share.replace(",", ""))
        ending_value = Decimal(ending_share.replace(",", ""))
    except InvalidOperation:
        return None
    net_change = ending_value - beginning_value
    return f"{net_change:,.2f}"


def _build_holdings_snapshot(report: ParsedAnnualReport) -> ExtractedField[dict[str, object]]:
    """构造持仓快照字段，见模板第 3 章“实际投资行为”。

    Args:
        report: 已解析年报对象。

    Returns:
        前十大重仓与行业分布原始披露。

    Raises:
        无显式抛出。
    """

    top_holdings_match = _find_table(report, _TOP_HOLDINGS_TABLE_KEYWORDS, "top_holdings")
    if top_holdings_match is None:
        return _missing_field("§8 未披露可规则化抽取的前十大重仓表")

    industry_match = _find_table(report, _INDUSTRY_TABLE_KEYWORDS, "industry_distribution")
    anchors = [
        _build_table_anchor(report, top_holdings_match.table, _SECTION_PORTFOLIO, "top_holdings"),
    ]
    industry_distribution: list[dict[str, str]] | None = None
    industry_status = "missing"
    if industry_match is not None:
        industry_distribution = _extract_industry_distribution(industry_match.table)
        industry_status = "direct"
        anchors.append(
            _build_table_anchor(report, industry_match.table, _SECTION_PORTFOLIO, "industry_distribution")
        )

    return ExtractedField(
        value={
            "top_holdings": _extract_top_holdings(top_holdings_match.table),
            "industry_distribution": industry_distribution,
            "industry_distribution_status": industry_status,
        },
        anchors=tuple(anchors),
        extraction_mode="direct",
        note=None if industry_match is not None else "§8 未披露可规则化抽取的行业分布表。",
    )


def _build_share_change(report: ParsedAnnualReport) -> ExtractedField[dict[str, object]]:
    """构造份额变动字段，见模板第 4 章“投资者获得感”。

    Args:
        report: 已解析年报对象。

    Returns:
        期初份额、期末份额和净变动。

    Raises:
        无显式抛出。
    """

    share_change_match = _find_share_change_table(report)
    if share_change_match is None:
        return _missing_field("§10 未披露可规则化抽取的份额变动表")
    share_change = _extract_share_change(share_change_match.table, fund_code=report.key.fund_code)
    if share_change is None:
        return _missing_field("§10 份额变动表存在多个份额列，当前规则无法可靠选择对应份额类别")

    return ExtractedField(
        value=share_change,
        anchors=(
            _build_table_anchor(report, share_change_match.table, _SECTION_SHARE_CHANGE, "share_change"),
        ),
        extraction_mode="direct",
        note=None,
    )


def extract_holdings_share_change(report: ParsedAnnualReport) -> HoldingsShareChangeExtractionResult:
    """抽取 `§8/§10` 持仓快照与份额变动。

    Args:
        report: 已解析年报对象。

    Returns:
        `holdings_snapshot` 与 `share_change` 两类结果。

    Raises:
        无显式抛出。
    """

    return HoldingsShareChangeExtractionResult(
        holdings_snapshot=_build_holdings_snapshot(report),
        share_change=_build_share_change(report),
    )
