"""`§8/§10` 持仓快照与份额变动表格抽取。"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
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
_ALL_STOCK_DETAILS_KEYWORDS: Final[tuple[str, ...]] = ("股票代码", "股票名称", "数量", "公允价值", "占基金资产净值比例")
_INDUSTRY_TABLE_KEYWORDS: Final[tuple[str, ...]] = ("行业", "占比")
_SHARE_CHANGE_REQUIRED_KEYWORDS: Final[tuple[str, ...]] = ("期初", "期末", "基金份额总额")
_SHARE_CHANGE_NET_KEYWORDS: Final[tuple[str, ...]] = ("净变动", "本期申购赎回净额")
_SHARE_CHANGE_FLOW_KEYWORDS: Final[tuple[str, ...]] = ("申购", "赎回")
_TOTAL_SHARE_HEADER_KEYWORDS: Final[tuple[str, ...]] = ("合计", "总计", "基金份额总额", "总份额")
_SUBORDINATE_FUND_NAME_KEYWORDS: Final[tuple[str, ...]] = ("下属分级基金的基金简称", "下属分级基金的基\n金简称")
_SUBORDINATE_FUND_CODE_KEYWORDS: Final[tuple[str, ...]] = ("下属分级基金的交易代码", "下属分级基金的交\n易代码")
_SUPPORTED_SHARE_CLASS_LABELS: Final[tuple[str, ...]] = tuple("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
_REASON_SINGLE_VALUE_COLUMN: Final[str] = "single_value_column"
_REASON_FUND_CODE_HEADER_MATCH: Final[str] = "fund_code_header_match"
_REASON_SECTION_TWO_CLASS_EVIDENCE: Final[str] = "section_2_share_class_evidence"
_TOP_HOLDINGS_STATUS_DIRECT_TOP_TEN: Final[str] = "direct_top_ten"
_TOP_HOLDINGS_STATUS_DIRECT_ALL_STOCK_DETAILS: Final[str] = "direct_all_stock_details"
_TOP_HOLDINGS_STATUS_MISSING: Final[str] = "missing"
_TOP_HOLDINGS_SOURCE_TOP_TEN: Final[str] = "top_ten"
_TOP_HOLDINGS_SOURCE_ALL_STOCK_DETAILS: Final[str] = "all_stock_investment_details"
_TOP_HOLDINGS_SOURCE_NONE: Final[str] = "none"
_BOND_TOP_HOLDING_SCHEMA_VERSION: Final[str] = "bond_top_holding_row.v1"
_BOND_TOP_HOLDING_TABLE_KEYWORDS: Final[tuple[str, ...]] = (
    "债券代码",
    "债券名称",
    "公允价值",
    "占基金资产净值比例",
)
_BOND_TOP_HOLDING_SECTION_TITLE: Final[str] = "§8.6 前五名债券投资明细"
_BOND_CODE_HEADER_KEYWORDS: Final[tuple[str, ...]] = ("债券代码",)
_BOND_NAME_HEADER_KEYWORDS: Final[tuple[str, ...]] = ("债券名称",)
_BOND_FAIR_VALUE_HEADER_KEYWORDS: Final[tuple[str, ...]] = ("公允价值",)
_BOND_NET_ASSET_RATIO_HEADER_KEYWORDS: Final[tuple[str, ...]] = ("占基金资产净值比例",)
_TARGET_FUND_HOLDING_SCHEMA_VERSION: Final[str] = "target_fund_holding_row.v1"
_TARGET_FUND_HOLDING_TABLE_KEYWORDS: Final[tuple[str, ...]] = (
    "基金名称",
    "公允价值",
    "占基金资产净值比例",
)
_TARGET_FUND_HOLDING_SECTION_TITLE: Final[str] = "§8.2 期末投资目标基金明细"
_TARGET_FUND_NAME_HEADER_KEYWORDS: Final[tuple[str, ...]] = ("基金名称",)
_TARGET_FUND_FAIR_VALUE_HEADER_KEYWORDS: Final[tuple[str, ...]] = ("公允价值",)
_TARGET_FUND_NET_ASSET_RATIO_HEADER_KEYWORDS: Final[tuple[str, ...]] = ("占基金资产净值比例",)
_INDUSTRY_STATUS_DIRECT: Final[str] = "direct"
_INDUSTRY_STATUS_MISSING: Final[str] = "missing"
_MAX_TOP_HOLDINGS_ROWS: Final[int] = 10


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


@dataclass(frozen=True, slots=True)
class _HoldingsSource:
    """股票持仓明细来源。

    Attributes:
        match: 命中的表格；缺失时为 `None`。
        status: `top_holdings_status` 机器状态。
        source: `top_holdings_source` 机器来源。
    """

    match: _TableMatch | None
    status: str
    source: str


@dataclass(frozen=True, slots=True)
class _ShareClassEvidence:
    """同源 §2 份额类别证据。

    Attributes:
        class_label: 当前基金代码对应的份额类别。
        source_note: 证据说明。
    """

    class_label: str
    source_note: str


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


def _merge_adjacent_split_tables(tables: tuple[ParsedTable, ...]) -> tuple[ParsedTable, ...]:
    """合并相邻的份额变动表头表和数据表。

    Args:
        tables: parser 输出的原始表格序列。

    Returns:
        已合并相邻拆表后的表格序列。

    Raises:
        无显式抛出。
    """

    merged: list[ParsedTable] = []
    index = 0
    while index < len(tables):
        table = tables[index]
        next_table = tables[index + 1] if index + 1 < len(tables) else None
        if next_table is not None and _can_merge_split_share_tables(table, next_table):
            merged.append(_merge_split_share_table(table, next_table))
            index += 2
            continue
        merged.append(table)
        index += 1
    return tuple(merged)


def _can_merge_split_share_tables(header_table: ParsedTable, data_table: ParsedTable) -> bool:
    """判断拆出的份额表头表和数据表是否可安全合并。

    Args:
        header_table: 候选表头表。
        data_table: 候选数据表。

    Returns:
        表格物理位置相邻且份额列数量可确定时返回 `True`。

    Raises:
        无显式抛出。
    """

    return (
        _is_bounded_split_table_continuation(header_table, data_table)
        and _is_split_share_header_table(header_table)
        and _is_split_share_data_table(data_table)
        and _split_share_header_count(header_table) == _split_share_value_column_count(data_table)
    )


def _is_bounded_split_table_continuation(header_table: ParsedTable, data_table: ParsedTable) -> bool:
    """判断两个拆表是否满足同页相邻或下一页延续边界。

    Args:
        header_table: 候选表头表。
        data_table: 候选数据表。

    Returns:
        同页相邻表序号或下一页首表延续时返回 `True`。

    Raises:
        无显式抛出。
    """

    if header_table.page_number == data_table.page_number:
        return data_table.table_index == header_table.table_index + 1
    return (
        data_table.page_number == header_table.page_number + 1
        and data_table.table_index == 0
    )


def _is_split_share_header_table(table: ParsedTable) -> bool:
    """判断表格是否为 parser 拆出的份额变动表头表。

    Args:
        table: 待检查表格。

    Returns:
        至少包含两个份额类别列且不含完整期初/期末数据时返回 `True`。

    Raises:
        无显式抛出。
    """

    table_text = _compact_text(_joined_table_text(table))
    return _table_share_class_label_count(table) >= 2 and "期初" not in table_text and "期末" not in table_text


def _is_split_share_data_table(table: ParsedTable) -> bool:
    """判断表格是否为 parser 拆出的份额变动数据表。

    Args:
        table: 待检查表格。

    Returns:
        缺少份额类别表头但含期初/期末/申购/赎回数据时返回 `True`。

    Raises:
        无显式抛出。
    """

    table_text = _compact_text(_joined_table_text(table))
    return (
        "期初" in table_text
        and "期末" in table_text
        and all(keyword in table_text for keyword in _SHARE_CHANGE_FLOW_KEYWORDS)
        and _table_share_class_label_count(table) == 0
    )


def _merge_split_share_table(header_table: ParsedTable, data_table: ParsedTable) -> ParsedTable:
    """把份额变动拆表合并为带 A/C 表头的数据表。

    Args:
        header_table: 相邻表头表。
        data_table: 相邻数据表。

    Returns:
        合并后的份额变动表。

    Raises:
        无显式抛出。
    """

    headers = _share_headers_from_split_header(header_table, data_table)
    return ParsedTable(
        page_number=data_table.page_number,
        table_index=data_table.table_index,
        headers=headers,
        rows=data_table.rows,
    )


def _share_headers_from_split_header(
    header_table: ParsedTable,
    data_table: ParsedTable,
) -> tuple[str, ...]:
    """从拆出的表头表生成份额变动数据表表头。

    Args:
        header_table: parser 拆出的表头表。
        data_table: parser 拆出的数据表。

    Returns:
        与数据表列数对齐的表头。

    Raises:
        无显式抛出。
    """

    header_texts = [_normalize_cell(header) for header in header_table.headers]
    for row in header_table.rows:
        header_texts.extend(_normalize_cell(cell) for cell in row)
    class_headers = [
        text
        for text in header_texts
        if _share_class_label_from_text(text) is not None
    ]
    first_header = _normalize_cell(data_table.headers[0]) if data_table.headers else "项目"
    return (first_header, *class_headers[: max(len(data_table.headers) - 1, 0)])


def _split_share_header_count(table: ParsedTable) -> int:
    """统计拆表表头中的份额类别列数量。

    Args:
        table: 候选表头表。

    Returns:
        份额类别表头数量。

    Raises:
        无显式抛出。
    """

    header_texts = [_normalize_cell(header) for header in table.headers]
    for row in table.rows:
        header_texts.extend(_normalize_cell(cell) for cell in row)
    return sum(1 for text in header_texts if _share_class_label_from_text(text) is not None)


def _split_share_value_column_count(table: ParsedTable) -> int:
    """统计拆表数据表中的值列数量。

    Args:
        table: 候选数据表。

    Returns:
        扣除项目列后的值列数量。

    Raises:
        无显式抛出。
    """

    return max(len(table.headers) - 1, 0)


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

    for table in _merge_adjacent_split_tables(report.tables):
        if _is_share_change_table(table):
            return _TableMatch(table=table, table_kind="share_change")
    return None


def _find_holdings_source(report: ParsedAnnualReport) -> _HoldingsSource:
    """查找股票持仓明细来源。

    Args:
        report: 已解析年报对象。

    Returns:
        股票持仓来源状态；优先前十大/重仓，其次 §8 所有股票投资明细。

    Raises:
        无显式抛出。
    """

    top_holdings_match = _find_table(report, _TOP_HOLDINGS_TABLE_KEYWORDS, "top_holdings")
    if top_holdings_match is not None:
        return _HoldingsSource(
            match=top_holdings_match,
            status=_TOP_HOLDINGS_STATUS_DIRECT_TOP_TEN,
            source=_TOP_HOLDINGS_SOURCE_TOP_TEN,
        )
    all_stock_match = _find_table(
        report,
        _ALL_STOCK_DETAILS_KEYWORDS,
        "all_stock_investment_details",
    )
    if all_stock_match is not None:
        return _HoldingsSource(
            match=all_stock_match,
            status=_TOP_HOLDINGS_STATUS_DIRECT_ALL_STOCK_DETAILS,
            source=_TOP_HOLDINGS_SOURCE_ALL_STOCK_DETAILS,
        )
    return _HoldingsSource(
        match=None,
        status=_TOP_HOLDINGS_STATUS_MISSING,
        source=_TOP_HOLDINGS_SOURCE_NONE,
    )


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


def _find_header_index(headers: tuple[str, ...], keywords: tuple[str, ...]) -> int | None:
    """按任一关键词查找表头下标。

    Args:
        headers: 表头元组。
        keywords: 候选语义关键词。

    Returns:
        命中时返回下标，否则返回 `None`。

    Raises:
        无显式抛出。
    """

    for index, header in enumerate(headers):
        normalized_header = _compact_text(header)
        if any(keyword in normalized_header for keyword in keywords):
            return index
    return None


def _cell_at(row: tuple[str, ...], index: int | None) -> str | None:
    """安全读取表格单元格。

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


def _extract_top_holdings(table: ParsedTable, *, limit_rows: bool = False) -> list[dict[str, str]]:
    """从股票持仓表中提取行数据。

    Args:
        table: 前十大重仓或所有股票投资明细表。
        limit_rows: 是否只保留前 10 行，见模板第 3 章“实际投资行为”。

    Returns:
        股票持仓行数据列表。

    Raises:
        无显式抛出。
    """

    rows = table.rows[:_MAX_TOP_HOLDINGS_ROWS] if limit_rows else table.rows
    return [_row_to_dict(table.headers, row) for row in rows]


def _build_bond_top_holding_source_anchor(
    *,
    table: ParsedTable,
    bond_code: str,
    bond_name: str,
) -> dict[str, object]:
    """构造 `bond_top_holding_row.v1` 行级来源锚点。

    Args:
        table: 命中的前五名债券投资明细表。
        bond_code: 债券代码。
        bond_name: 债券名称。

    Returns:
        可序列化的行级来源锚点。

    Raises:
        无显式抛出。
    """

    table_id = _table_id(table)
    return {
        "section_id": _SECTION_PORTFOLIO,
        "section_title": _BOND_TOP_HOLDING_SECTION_TITLE,
        "page_number": table.page_number,
        "table_id": table_id,
        "row_locator": f"bond_top_holding:{bond_code}:{bond_name}",
    }


def _extract_bond_top_holdings(table: ParsedTable) -> list[dict[str, object]]:
    """从前五名债券投资明细表抽取债券持仓行。

    Args:
        table: 前五名债券投资明细表。

    Returns:
        `bond_top_holding_row.v1` 行数据列表。

    Raises:
        无显式抛出。
    """

    code_index = _find_header_index(table.headers, _BOND_CODE_HEADER_KEYWORDS)
    name_index = _find_header_index(table.headers, _BOND_NAME_HEADER_KEYWORDS)
    fair_value_index = _find_header_index(table.headers, _BOND_FAIR_VALUE_HEADER_KEYWORDS)
    net_asset_ratio_index = _find_header_index(table.headers, _BOND_NET_ASSET_RATIO_HEADER_KEYWORDS)
    rows: list[dict[str, object]] = []
    for row in table.rows:
        code = _cell_at(row, code_index)
        name = _cell_at(row, name_index)
        fair_value = _cell_at(row, fair_value_index)
        net_asset_ratio = _cell_at(row, net_asset_ratio_index)
        if code is None or name is None or fair_value is None or net_asset_ratio is None:
            continue
        rows.append(
            {
                "code": code,
                "name": name,
                "fair_value_cny": fair_value,
                "net_asset_ratio": net_asset_ratio,
                "source_anchor": _build_bond_top_holding_source_anchor(
                    table=table,
                    bond_code=code,
                    bond_name=name,
                ),
            }
        )
    return rows


def _build_target_fund_holding_source_anchor(
    *,
    table: ParsedTable,
    target_fund_name: str,
) -> dict[str, object]:
    """构造 `target_fund_holding_row.v1` 行级来源锚点。

    Args:
        table: 命中的期末投资目标基金明细表。
        target_fund_name: 目标基金名称。

    Returns:
        可序列化的行级来源锚点。

    Raises:
        无显式抛出。
    """

    table_id = _table_id(table)
    return {
        "section_id": _SECTION_PORTFOLIO,
        "section_title": _TARGET_FUND_HOLDING_SECTION_TITLE,
        "page_number": table.page_number,
        "table_id": table_id,
        "row_locator": f"target_fund_holding:{target_fund_name}",
    }


def _extract_target_fund_holdings(table: ParsedTable) -> list[dict[str, object]]:
    """从期末投资目标基金明细表抽取目标基金持仓行。

    Args:
        table: 期末投资目标基金明细表。

    Returns:
        `target_fund_holding_row.v1` 行数据列表。

    Raises:
        无显式抛出。
    """

    name_index = _find_header_index(table.headers, _TARGET_FUND_NAME_HEADER_KEYWORDS)
    fair_value_index = _find_header_index(table.headers, _TARGET_FUND_FAIR_VALUE_HEADER_KEYWORDS)
    net_asset_ratio_index = _find_header_index(table.headers, _TARGET_FUND_NET_ASSET_RATIO_HEADER_KEYWORDS)
    rows: list[dict[str, object]] = []
    for row in table.rows:
        name = _cell_at(row, name_index)
        fair_value = _cell_at(row, fair_value_index)
        net_asset_ratio = _cell_at(row, net_asset_ratio_index)
        if name is None or fair_value is None or net_asset_ratio is None:
            continue
        rows.append(
            {
                "name": name,
                "fair_value_cny": fair_value,
                "net_asset_ratio": net_asset_ratio,
                "source_anchor": _build_target_fund_holding_source_anchor(
                    table=table,
                    target_fund_name=name,
                ),
            }
        )
    return rows


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
    share_class_evidence: _ShareClassEvidence | None,
) -> dict[str, str | None] | None:
    """从份额变动表中提取期初、期末与净变动。

    Args:
        table: 份额变动表。
        fund_code: 当前基金代码，用于精确匹配份额列表头。
        share_class_evidence: §2 直接确认的当前份额类别证据。

    Returns:
        份额变动结构化结果；多值列无法消歧时返回 `None`。

    Raises:
        无显式抛出。
    """

    selection = _select_share_change_value_column(
        table,
        fund_code=fund_code,
        share_class_evidence=share_class_evidence,
    )
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
    share_class_evidence: _ShareClassEvidence | None,
) -> _ShareColumnSelection | None:
    """选择份额变动表的值列。

    Args:
        table: 份额变动表。
        fund_code: 当前基金代码。
        share_class_evidence: §2 直接确认的当前份额类别证据。

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
    if len(value_columns) == 1:
        index, header = value_columns[0]
        if not header:
            return None
        return _ShareColumnSelection(
            column_index=index,
            header=header,
            reason=_REASON_SINGLE_VALUE_COLUMN,
        )
    class_matches = _share_class_column_matches(value_columns, share_class_evidence)
    if len(class_matches) == 1:
        index, header = class_matches[0]
        return _ShareColumnSelection(
            column_index=index,
            header=header,
            reason=_REASON_SECTION_TWO_CLASS_EVIDENCE,
        )
    if class_matches:
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


def _share_class_column_matches(
    value_columns: list[tuple[int, str]],
    share_class_evidence: _ShareClassEvidence | None,
) -> list[tuple[int, str]]:
    """按 §2 份额类别证据选择份额变动列。

    Args:
        value_columns: 候选值列。
        share_class_evidence: 同源 §2 确认的份额类别证据。

    Returns:
        匹配当前份额类别且不含总份额语义的列。

    Raises:
        无显式抛出。
    """

    if share_class_evidence is None:
        return []
    target_class = share_class_evidence.class_label
    return [
        (index, header)
        for index, header in value_columns
        if _contains_share_class_label(header, target_class) and not _is_total_share_header(header)
    ]


def _share_class_evidence(report: ParsedAnnualReport) -> _ShareClassEvidence | None:
    """从同源 §2 识别当前基金代码对应的份额类别。

    Args:
        report: 已解析年报对象。

    Returns:
        当前基金代码对应的份额类别；缺少明确证据或证据歧义时返回 `None`。

    Raises:
        无显式抛出。
    """

    evidence_from_tables = _share_class_evidence_from_section_two_tables(report)
    if evidence_from_tables is not None:
        return evidence_from_tables
    return _share_class_evidence_from_section_two_text(report)


def _share_class_evidence_from_section_two_tables(
    report: ParsedAnnualReport,
) -> _ShareClassEvidence | None:
    """从 §2 分级基金简称/交易代码表识别份额类别。

    Args:
        report: 已解析年报对象。

    Returns:
        表格直接证明的份额类别；缺失或歧义时返回 `None`。

    Raises:
        无显式抛出。
    """

    section_two_tables = [
        table for table in report.tables if _table_likely_belongs_to_section_two(table)
    ]
    matches: list[str] = []
    for table in section_two_tables:
        label_row = _row_by_keywords(table, _SUBORDINATE_FUND_NAME_KEYWORDS)
        code_row = _row_by_keywords(table, _SUBORDINATE_FUND_CODE_KEYWORDS)
        if label_row is None or code_row is None:
            continue
        matches.extend(_class_matches_from_rows(label_row, code_row, report.key.fund_code))
    unique_matches = sorted(set(matches))
    if len(unique_matches) != 1:
        return None
    return _ShareClassEvidence(
        class_label=unique_matches[0],
        source_note="§2 下属分级基金简称/交易代码表",
    )


def _share_class_evidence_from_section_two_text(
    report: ParsedAnnualReport,
) -> _ShareClassEvidence | None:
    """从 §2 正文识别份额类别。

    Args:
        report: 已解析年报对象。

    Returns:
        正文直接证明的份额类别；缺失或歧义时返回 `None`。

    Raises:
        无显式抛出。
    """

    section_two = _compact_text(report.get_section_text("§2") or "")
    if not section_two or report.key.fund_code not in section_two:
        return None
    matches = [
        class_label
        for class_label in _SUPPORTED_SHARE_CLASS_LABELS
        if _section_two_text_contains_class_mapping(section_two, report.key.fund_code, class_label)
    ]
    unique_matches = sorted(set(matches))
    if len(unique_matches) != 1:
        return None
    return _ShareClassEvidence(
        class_label=unique_matches[0],
        source_note="§2 下属分级基金正文",
    )


def _table_likely_belongs_to_section_two(table: ParsedTable) -> bool:
    """判断表格是否属于 §2 基金简介范围。

    Args:
        table: 待检查表格。

    Returns:
        包含 §2 基金简介关键行时返回 `True`。

    Raises:
        无显式抛出。
    """

    table_text = _compact_text(_joined_table_text(table))
    has_profile_identity = "基金名称" in table_text and "基金主代码" in table_text
    has_subordinate_mapping = any(
        _compact_text(keyword) in table_text for keyword in _SUBORDINATE_FUND_NAME_KEYWORDS
    ) and any(_compact_text(keyword) in table_text for keyword in _SUBORDINATE_FUND_CODE_KEYWORDS)
    return has_profile_identity or has_subordinate_mapping


def _row_by_keywords(
    table: ParsedTable,
    keywords: tuple[str, ...],
) -> tuple[str, ...] | None:
    """按关键词查找表格行。

    Args:
        table: 待查找表格。
        keywords: 任一命中即可的关键词。

    Returns:
        命中的表格行；未命中返回 `None`。

    Raises:
        无显式抛出。
    """

    for row in table.rows:
        first_cell = _normalize_cell(row[0]) if row else ""
        compact_first = _compact_text(first_cell)
        if any(_compact_text(keyword) in compact_first for keyword in keywords):
            return row
    return None


def _class_matches_from_rows(
    label_row: tuple[str, ...],
    code_row: tuple[str, ...],
    fund_code: str,
) -> list[str]:
    """从简称行与交易代码行配对识别份额类别。

    Args:
        label_row: 下属分级基金简称行。
        code_row: 下属分级基金交易代码行。
        fund_code: 当前基金代码。

    Returns:
        匹配当前基金代码的份额类别列表。

    Raises:
        无显式抛出。
    """

    matches: list[str] = []
    for index, code_cell in enumerate(code_row):
        if index == 0 or fund_code not in _compact_text(code_cell):
            continue
        label = _compact_text(label_row[index]) if index < len(label_row) else ""
        class_label = _share_class_label_from_text(label)
        if class_label is not None:
            matches.append(class_label)
    return matches


def _section_two_text_contains_class_mapping(section_two: str, fund_code: str, class_label: str) -> bool:
    """判断 §2 正文是否直接包含代码到份额类别的映射。

    Args:
        section_two: 已压缩空白的 §2 文本。
        fund_code: 当前基金代码。
        class_label: 目标份额类别。

    Returns:
        代码与类别在同一分级基金区域内出现时返回 `True`。

    Raises:
        无显式抛出。
    """

    class_index = section_two.find(class_label)
    code_index = section_two.find(fund_code)
    if class_index < 0 or code_index < 0:
        return False
    return abs(class_index - code_index) <= 80


def _contains_share_class_label(text: str, class_label: str) -> bool:
    """判断文本是否包含明确份额类别标签。

    Args:
        text: 待检查文本。
        class_label: 份额类别标签。

    Returns:
        包含 `A类`、`A份额` 或基金简称后缀等明确标签时返回 `True`。

    Raises:
        无显式抛出。
    """

    compact_text = _compact_text(text).upper()
    normalized_class_label = class_label.upper()
    return (
        f"{normalized_class_label}类" in compact_text
        or f"{normalized_class_label}份额" in compact_text
        or _endswith_bare_share_class_label(compact_text, normalized_class_label)
    )


def _endswith_bare_share_class_label(text: str, class_label: str) -> bool:
    """判断文本是否以安全的裸份额类别标签结尾。

    Args:
        text: 已压缩并大写的文本。
        class_label: 份额类别标签。

    Returns:
        末尾标签前不是拉丁字母时返回 `True`。

    Raises:
        无显式抛出。
    """

    if not text.endswith(class_label):
        return False
    prefix = text[: -len(class_label)]
    if not prefix:
        return False
    return not prefix[-1].isascii() or not prefix[-1].isalpha()


def _share_class_label_from_text(text: str) -> str | None:
    """从份额简称或表头中识别明确份额类别标签。

    Args:
        text: 待检查文本。

    Returns:
        唯一份额类别标签；缺失或歧义时返回 `None`。

    Raises:
        无显式抛出。
    """

    compact_text = _compact_text(text)
    if not compact_text:
        return None
    matches = [
        class_label
        for class_label in _SUPPORTED_SHARE_CLASS_LABELS
        if _contains_share_class_label(compact_text, class_label)
    ]
    unique_matches = sorted(set(matches))
    if len(unique_matches) != 1:
        return None
    return unique_matches[0]


def _share_class_label_count(text: str) -> int:
    """统计文本中出现的唯一份额类别数量。

    Args:
        text: 待检查文本。

    Returns:
        唯一份额类别数量。

    Raises:
        无显式抛出。
    """

    return len(
        {
            class_label
            for class_label in _SUPPORTED_SHARE_CLASS_LABELS
            if _contains_share_class_label(text, class_label)
        }
    )


def _table_share_class_label_count(table: ParsedTable) -> int:
    """统计表格单元格中的唯一份额类别数量。

    Args:
        table: 待检查表格。

    Returns:
        唯一份额类别数量。

    Raises:
        无显式抛出。
    """

    labels: set[str] = set()
    cells = list(table.headers)
    for row in table.rows:
        cells.extend(row)
    for cell in cells:
        class_label = _share_class_label_from_text(cell)
        if class_label is not None:
            labels.add(class_label)
    return len(labels)


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

    holdings_source = _find_holdings_source(report)
    industry_match = _find_table(report, _INDUSTRY_TABLE_KEYWORDS, "industry_distribution")
    bond_top_holding_match = _find_table(
        report,
        _BOND_TOP_HOLDING_TABLE_KEYWORDS,
        "bond_top_holding_row",
    )
    target_fund_holding_match = _find_table(
        report,
        _TARGET_FUND_HOLDING_TABLE_KEYWORDS,
        "target_fund_holding_row",
    )
    if (
        holdings_source.match is None
        and industry_match is None
        and bond_top_holding_match is None
        and target_fund_holding_match is None
    ):
        return _missing_field("§8 未披露可规则化抽取的股票持仓明细或行业分布表")

    anchors: list[EvidenceAnchor] = []
    top_holdings: list[dict[str, str]] | None = None
    if holdings_source.match is not None:
        row_locator = holdings_source.source
        limit_rows = holdings_source.source == _TOP_HOLDINGS_SOURCE_ALL_STOCK_DETAILS
        top_holdings = _extract_top_holdings(holdings_source.match.table, limit_rows=limit_rows)
        anchors.append(
            _build_table_anchor(report, holdings_source.match.table, _SECTION_PORTFOLIO, row_locator)
        )
    industry_distribution: list[dict[str, str]] | None = None
    industry_status = _INDUSTRY_STATUS_MISSING
    if industry_match is not None:
        industry_distribution = _extract_industry_distribution(industry_match.table)
        industry_status = _INDUSTRY_STATUS_DIRECT
        anchors.append(
            _build_table_anchor(report, industry_match.table, _SECTION_PORTFOLIO, "industry_distribution")
        )

    bond_top_holdings: list[dict[str, object]] | None = None
    if bond_top_holding_match is not None:
        bond_top_holdings = _extract_bond_top_holdings(bond_top_holding_match.table)
        if bond_top_holdings:
            anchors.append(
                _build_table_anchor(
                    report,
                    bond_top_holding_match.table,
                    _SECTION_PORTFOLIO,
                    "bond_top_holdings",
                )
            )

    target_fund_holdings: list[dict[str, object]] | None = None
    if target_fund_holding_match is not None:
        target_fund_holdings = _extract_target_fund_holdings(target_fund_holding_match.table)
        if target_fund_holdings:
            anchors.append(
                _build_table_anchor(
                    report,
                    target_fund_holding_match.table,
                    _SECTION_PORTFOLIO,
                    "target_fund_holdings",
                )
            )

    value: dict[str, object] = {
        "top_holdings": top_holdings,
        "top_holdings_status": holdings_source.status,
        "top_holdings_source": holdings_source.source,
        "industry_distribution": industry_distribution,
        "industry_distribution_status": industry_status,
    }
    if bond_top_holdings:
        value.update(
            {
                "schema_version": _BOND_TOP_HOLDING_SCHEMA_VERSION,
                "fund_code": report.key.fund_code,
                "report_year": report.key.year,
                "bond_top_holdings": bond_top_holdings,
            }
        )
    if target_fund_holdings:
        value.update(
            {
                "schema_version": _TARGET_FUND_HOLDING_SCHEMA_VERSION,
                "fund_code": report.key.fund_code,
                "report_year": report.key.year,
                "target_fund_holdings": target_fund_holdings,
            }
        )

    return ExtractedField(
        value=value,
        anchors=tuple(anchors),
        extraction_mode="direct",
        note=_holdings_snapshot_note(holdings_source, industry_match),
    )


def _holdings_snapshot_note(
    holdings_source: _HoldingsSource,
    industry_match: _TableMatch | None,
) -> str | None:
    """生成持仓快照缺失说明。

    Args:
        holdings_source: 股票持仓来源状态。
        industry_match: 行业分布表命中结果。

    Returns:
        缺失说明；无缺口时返回 `None`。

    Raises:
        无显式抛出。
    """

    notes: list[str] = []
    if holdings_source.match is None:
        notes.append("§8 未披露可规则化抽取的股票持仓明细表。")
    if industry_match is None:
        notes.append("§8 未披露可规则化抽取的行业分布表。")
    return " ".join(notes) or None


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
    share_change = _extract_share_change(
        share_change_match.table,
        fund_code=report.key.fund_code,
        share_class_evidence=_share_class_evidence(report),
    )
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
