"""`§4/§8/§9` 管理人文本、换手率与持有人信息抽取。"""

from __future__ import annotations

from decimal import Decimal, InvalidOperation
import re
from dataclasses import dataclass
from typing import Final

from fund_agent.fund.documents.models import ParsedAnnualReport, ParsedTable
from fund_agent.fund.extractors.models import (
    EvidenceAnchor,
    ExtractedField,
    ManagerOwnershipExtractionResult,
)

_SECTION_MANAGER_REPORT: Final[str] = "§4"
_SECTION_PORTFOLIO: Final[str] = "§8"
_SECTION_HOLDER: Final[str] = "§9"
_STRATEGY_HEADING_PATTERN: Final[re.Pattern[str]] = re.compile(
    r"^4\.\d+(?:\.\d+)?\s*报告期内基金投资策略和运作分析\s*$"
)
_OUTLOOK_HEADING_PATTERN: Final[re.Pattern[str]] = re.compile(
    r"^4\.\d+(?:\.\d+)?\s*管理人对宏观经济、证券市场及行业走势的简要展望\s*$"
)
_SECTION_HEADING_PATTERN: Final[re.Pattern[str]] = re.compile(
    r"^\d{1,2}\.\d{1,2}(?:\.\d{1,2})?\s+.+$"
)
_EMPLOYEE_HOLDING_TABLE_KEYWORDS: Final[tuple[str, ...]] = ("从业人员", "持有", "份额")
_MANAGER_HOLDING_TABLE_KEYWORDS: Final[tuple[str, ...]] = ("基金经理", "持有", "基金份额")
_HOLDER_STRUCTURE_TABLE_KEYWORDS: Final[tuple[str, ...]] = ("持有人户数", "机构投资者", "个人投资者")
_RATIO_VALUE_PATTERN: Final[re.Pattern[str]] = re.compile(r"^-?\d+(?:\.\d+)?%?$")

_FIELD_PATTERNS: Final[dict[str, tuple[tuple[str, tuple[str, ...]], ...]]] = {
    "strategy_summary": (
        (_SECTION_MANAGER_REPORT, (r"投资策略\s*[：:]\s*(.+)", r"报告期内投资策略\s*[：:]\s*(.+)")),
    ),
    "market_outlook": (
        (_SECTION_MANAGER_REPORT, (r"后市展望\s*[：:]\s*(.+)", r"对后市的看法\s*[：:]\s*(.+)")),
    ),
    "turnover_rate": (
        (_SECTION_PORTFOLIO, (r"(?:股票)?换手率\s*[：:]\s*(.+)", r"报告期内(?:股票)?换手率\s*[：:]\s*(.+)")),
    ),
    "turnover_basis": (
        (_SECTION_PORTFOLIO, (r"换手率口径\s*[：:]\s*(.+)", r"换手率计算口径\s*[：:]\s*(.+)")),
    ),
    "manager_holding": (
        (_SECTION_HOLDER, (r"基金经理持有本基金\s*[：:]\s*(.+)", r"基金经理持有份额\s*[：:]\s*(.+)")),
    ),
    "employee_holding": (
        (_SECTION_HOLDER, (r"从业人员持有本基金\s*[：:]\s*(.+)", r"基金管理人从业人员持有本基金\s*[：:]\s*(.+)")),
    ),
    "institutional_holder": (
        (_SECTION_HOLDER, (r"机构投资者持有(?:比例|份额)\s*[：:]\s*(.+)", r"机构投资者\s*[：:]\s*(.+)")),
    ),
    "individual_holder": (
        (_SECTION_HOLDER, (r"个人投资者持有(?:比例|份额)\s*[：:]\s*(.+)", r"个人投资者\s*[：:]\s*(.+)")),
    ),
}


@dataclass(frozen=True, slots=True)
class _MatchedField:
    """`§4/§8/§9` 字段命中结果。

    Attributes:
        field_name: 字段名。
        value: 抽取到的字段值。
        section_id: 命中章节。
        matched_line: 命中的原始行文本。
        table: 命中的表格；非表格命中时为 `None`。
    """

    field_name: str
    value: str
    section_id: str
    matched_line: str
    table: ParsedTable | None = None


def _extract_field(report: ParsedAnnualReport, field_name: str) -> _MatchedField | None:
    """从 `§4/§8/§9` 中提取单个字段。

    Args:
        report: 已解析年报对象。
        field_name: 目标字段名。

    Returns:
        命中时返回字段命中结果，否则返回 `None`。

    Raises:
        KeyError: 请求未知字段时抛出。
    """

    rules = _FIELD_PATTERNS[field_name]
    for section_id, patterns in rules:
        section_text = report.get_section_text(section_id)
        if not section_text:
            continue
        for line in section_text.splitlines():
            normalized_line = line.strip()
            for pattern in patterns:
                match = re.match(pattern, normalized_line)
                if match:
                    return _MatchedField(
                        field_name=field_name,
                        value=match.group(1).strip(),
                        section_id=section_id,
                        matched_line=normalized_line,
                    )
    return None


def _normalize_cell(value: str) -> str:
    """规范化单元格或正文行文本。

    Args:
        value: 原始文本。

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
    """拼接表格表头与数据行。

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


def _table_contains_all(table: ParsedTable, keywords: tuple[str, ...]) -> bool:
    """判断表格是否包含全部语义关键词。

    Args:
        table: 待检查的表格。
        keywords: 必须同时存在的关键词。

    Returns:
        全部存在时返回 `True`，否则返回 `False`。

    Raises:
        无显式抛出。
    """

    table_text = _compact_text(_table_text(table))
    return all(keyword in table_text for keyword in keywords)


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


def _find_header_index_all(headers: tuple[str, ...], keywords: tuple[str, ...]) -> int | None:
    """按全部关键词查找表头下标。

    Args:
        headers: 表头元组。
        keywords: 必须同时存在的语义关键词。

    Returns:
        命中时返回下标，否则返回 `None`。

    Raises:
        无显式抛出。
    """

    for index, header in enumerate(headers):
        normalized_header = _compact_text(header)
        if all(keyword in normalized_header for keyword in keywords):
            return index
    return None


def _first_present(*values: int | None) -> int | None:
    """返回第一个非 `None` 的下标。

    Args:
        *values: 候选下标。

    Returns:
        第一个非 `None` 值；全部为空时返回 `None`。

    Raises:
        无显式抛出。
    """

    for value in values:
        if value is not None:
            return value
    return None


def _row_contains_any(row: tuple[str, ...], keywords: tuple[str, ...]) -> bool:
    """判断行文本是否包含任一关键词。

    Args:
        row: 表格行。
        keywords: 候选关键词。

    Returns:
        任一关键词存在时返回 `True`，否则返回 `False`。

    Raises:
        无显式抛出。
    """

    joined_row = _compact_text(" ".join(_normalize_cell(cell) for cell in row))
    return any(keyword in joined_row for keyword in keywords)


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


def _matched_table_field(field_name: str, value: str, table: ParsedTable) -> _MatchedField:
    """把表格命中转换为既有字段命中对象。

    Args:
        field_name: 字段名。
        value: 抽取到的值。
        table: 命中的表格。

    Returns:
        可复用既有 anchor 构造逻辑的字段命中对象。

    Raises:
        无显式抛出。
    """

    return _MatchedField(
        field_name=field_name,
        value=value,
        section_id=_SECTION_HOLDER,
        matched_line=f"page-{table.page_number}-table-{table.table_index}: {'; '.join(table.headers)}",
        table=table,
    )


def _extract_heading_block(
    report: ParsedAnnualReport,
    heading_pattern: re.Pattern[str],
    field_name: str,
) -> _MatchedField | None:
    """按 `§4` 小节标题抽取连续正文块，见模板第 3 章“投资策略与风格”。

    Args:
        report: 已解析年报对象。
        heading_pattern: 小节标题匹配规则。
        field_name: 输出字段名。

    Returns:
        命中时返回字段命中结果，否则返回 `None`。

    Raises:
        无显式抛出。
    """

    section_text = report.get_section_text(_SECTION_MANAGER_REPORT)
    if not section_text:
        return None
    lines = [_normalize_cell(line) for line in section_text.splitlines()]
    collecting = False
    collected: list[str] = []
    matched_heading = ""
    for line in lines:
        if not line:
            continue
        if collecting and _SECTION_HEADING_PATTERN.match(line):
            break
        if collecting:
            collected.append(line)
            continue
        if heading_pattern.match(line):
            collecting = True
            matched_heading = line
    value = " ".join(collected).strip()
    if not value:
        return None
    return _MatchedField(
        field_name=field_name,
        value=value,
        section_id=_SECTION_MANAGER_REPORT,
        matched_line=matched_heading,
    )


def _extract_manager_alignment_from_tables(
    report: ParsedAnnualReport,
) -> tuple[_MatchedField | None, _MatchedField | None]:
    """从 `§9` 表格抽取基金经理/从业人员持有披露。

    Args:
        report: 已解析年报对象。

    Returns:
        基金经理持有与从业人员持有字段命中结果。

    Raises:
        无显式抛出。
    """

    manager_holding = None
    employee_holding = None
    for table in report.tables:
        if employee_holding is None and _table_contains_all(table, _EMPLOYEE_HOLDING_TABLE_KEYWORDS):
            employee_holding = _matched_table_field(
                "employee_holding",
                _table_text(table),
                table,
            )
        if manager_holding is None and _table_contains_all(table, _MANAGER_HOLDING_TABLE_KEYWORDS):
            manager_holding = _matched_table_field(
                "manager_holding",
                _table_text(table),
                table,
            )
    return manager_holding, employee_holding


def _extract_holder_structure_from_table(
    report: ParsedAnnualReport,
) -> tuple[_MatchedField | None, _MatchedField | None]:
    """从 `§9` 持有人结构表抽取机构/个人持有人比例。

    Args:
        report: 已解析年报对象。

    Returns:
        机构持有人与个人持有人字段命中结果。

    Raises:
        无显式抛出。
    """

    for index, table in enumerate(report.tables):
        table_candidates = (table,)
        if _table_contains_all(table, _HOLDER_STRUCTURE_TABLE_KEYWORDS):
            table_candidates = (table,)
        elif index > 0 and _is_holder_structure_continuation(report.tables[index - 1], table):
            table_candidates = (table,)
        else:
            continue
        for candidate in table_candidates:
            institutional_value, individual_value = _extract_holder_values(candidate)
            institutional_holder = (
                _matched_table_field("institutional_holder", institutional_value, candidate)
                if institutional_value
                else None
            )
            individual_holder = (
                _matched_table_field("individual_holder", individual_value, candidate)
                if individual_value
                else None
            )
            if institutional_holder is not None or individual_holder is not None:
                return institutional_holder, individual_holder
    return None, None


def _is_holder_structure_continuation(previous_table: ParsedTable, table: ParsedTable) -> bool:
    """判断当前表是否为跨页持有人结构数据表。

    Args:
        previous_table: 前一张表。
        table: 当前表。

    Returns:
        前表包含持有人结构组表头且当前表包含持有份额/比例列时返回 `True`。

    Raises:
        无显式抛出。
    """

    previous_text = _compact_text(_table_text(previous_table))
    current_text = _compact_text(_table_text(table))
    has_previous_group_header = all(keyword in previous_text for keyword in _HOLDER_STRUCTURE_TABLE_KEYWORDS)
    has_current_value_columns = all(keyword in current_text for keyword in ("持有份额", "比例"))
    return has_previous_group_header and has_current_value_columns


def _extract_holder_values(table: ParsedTable) -> tuple[str | None, str | None]:
    """从持有人结构数据表中读取机构/个人占比。

    Args:
        table: 持有人结构表或跨页续表。

    Returns:
        机构占比与个人占比。

    Raises:
        无显式抛出。
    """

    institution_index = _first_present(
        _find_header_index_all(table.headers, ("机构投资者", "比例")),
        _find_header_index(table.headers, ("机构投资者",)),
        _find_header_index_all(table.headers, ("占总份额", "比例")),
    )
    individual_index = _first_present(
        _find_header_index_all(table.headers, ("个人投资者", "比例")),
        _find_header_index(table.headers, ("个人投资者",)),
    )
    ratio_index = _find_header_index(table.headers, ("占总份额比例", "占基金总份额比例", "比例"))
    institutional_value = None
    individual_value = None
    for row in table.rows:
        if institutional_value is None and _row_contains_any(row, ("机构投资者", "机构")):
            institutional_value = _cell_at(row, ratio_index) or _cell_at(row, institution_index)
        if individual_value is None and _row_contains_any(row, ("个人投资者", "个人")):
            individual_value = _cell_at(row, ratio_index) or _cell_at(row, individual_index)
    if institutional_value is None and table.rows:
        institutional_value = _cell_at(table.rows[0], institution_index)
    if institutional_value is None and table.rows:
        institutional_value = _cell_at(table.rows[0], ratio_index)
    if individual_value is None and table.rows:
        individual_value = _cell_at(table.rows[0], individual_index)
    if individual_value is None and table.rows and institutional_value is not None:
        individual_value = _infer_adjacent_personal_ratio(table, institutional_value)
    return institutional_value, individual_value


def _infer_adjacent_personal_ratio(table: ParsedTable, institutional_value: str) -> str | None:
    """从跨页续表中按机构比例右侧相邻列推断个人比例。

    Args:
        table: 持有人结构续表。
        institutional_value: 已命中的机构占比。

    Returns:
        个人占比文本；无法定位时返回 `None`。

    Raises:
        无显式抛出。
    """

    if not table.rows:
        return None
    row = table.rows[0]
    for index, cell in enumerate(row):
        if _normalize_cell(cell) == institutional_value:
            return _find_adjacent_ratio_value(row, (index + 1, index + 2))
    return None


def _find_adjacent_ratio_value(row: tuple[str, ...], candidate_indexes: tuple[int, ...]) -> str | None:
    """从候选相邻列中选择形似比例的单元格。

    Args:
        row: 跨页持有人结构续表数据行。
        candidate_indexes: 候选下标；`+1` 适配仅披露比例列，`+2` 适配“个人份额 + 个人比例”标准布局。

    Returns:
        首个形似比例的单元格文本；不存在时返回 `None`。

    Raises:
        无显式抛出。
    """

    for index in candidate_indexes:
        value = _cell_at(row, index)
        if value is not None and _is_ratio_value(value):
            return value
    return None


def _is_ratio_value(value: str) -> bool:
    """判断单元格是否可作为持有人比例。

    Args:
        value: 候选单元格文本。

    Returns:
        单元格是 0 到 100 之间的比例数值时返回 `True`；带千分位的份额值返回 `False`。

    Raises:
        无显式抛出。
    """

    normalized_value = value.strip()
    if "," in normalized_value or not _RATIO_VALUE_PATTERN.match(normalized_value):
        return False
    try:
        numeric_value = Decimal(normalized_value.rstrip("%"))
    except InvalidOperation:
        return False
    return Decimal("0") <= numeric_value <= Decimal("100")


def _build_anchor(report: ParsedAnnualReport, matched_field: _MatchedField) -> EvidenceAnchor:
    """根据字段命中结果构造证据锚点。

    Args:
        report: 已解析年报对象。
        matched_field: 字段命中结果。

    Returns:
        对应的证据锚点。

    Raises:
        无显式抛出。
    """

    page_number = None
    table_id = None
    if matched_field.table is not None:
        page_number = matched_field.table.page_number
        table_id = f"page-{matched_field.table.page_number}-table-{matched_field.table.table_index}"
    return EvidenceAnchor(
        source_kind="annual_report",
        document_year=report.key.year,
        section_id=matched_field.section_id,
        page_number=page_number,
        table_id=table_id,
        row_locator=matched_field.field_name,
        note=matched_field.matched_line,
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


def _build_field_from_matches(
    report: ParsedAnnualReport,
    matched_fields: tuple[_MatchedField | None, ...],
    value: dict[str, object],
    missing_note: str,
) -> ExtractedField[dict[str, object]]:
    """根据多字段命中结果构造抽取字段。

    Args:
        report: 已解析年报对象。
        matched_fields: 多个候选字段命中结果。
        value: 结构化输出值。
        missing_note: 完全未命中时的缺失说明。

    Returns:
        带证据锚点的抽取字段；完全未命中时返回 `missing`。

    Raises:
        无显式抛出。
    """

    anchors = tuple(
        _build_anchor(report, matched_field)
        for matched_field in matched_fields
        if matched_field is not None
    )
    if not anchors:
        return _missing_field(missing_note)
    partial = any(mf is None for mf in matched_fields)
    return ExtractedField(
        value=value,
        anchors=anchors,
        extraction_mode="direct",
        note="部分子字段缺失，仅抽取到部分信息" if partial else None,
    )


def _build_manager_strategy_text(report: ParsedAnnualReport) -> ExtractedField[dict[str, object]]:
    """构造管理人策略文本字段，见模板第 3 章“投资策略与风格”。

    Args:
        report: 已解析年报对象。

    Returns:
        管理人报告中的策略与后市展望原文。

    Raises:
        无显式抛出。
    """

    strategy_summary = _extract_field(report, "strategy_summary")
    market_outlook = _extract_field(report, "market_outlook")
    if strategy_summary is None:
        strategy_summary = _extract_heading_block(
            report,
            _STRATEGY_HEADING_PATTERN,
            "strategy_summary",
        )
    if market_outlook is None:
        market_outlook = _extract_heading_block(
            report,
            _OUTLOOK_HEADING_PATTERN,
            "market_outlook",
        )
    return _build_field_from_matches(
        report=report,
        matched_fields=(strategy_summary, market_outlook),
        value={
            "strategy_summary": strategy_summary.value if strategy_summary else None,
            "market_outlook": market_outlook.value if market_outlook else None,
        },
        missing_note="§4 未披露可规则化抽取的投资策略/后市展望",
    )


def _build_turnover_rate(report: ParsedAnnualReport) -> ExtractedField[dict[str, object]]:
    """构造换手率字段，见模板第 2 章 C 成本侵蚀。

    Args:
        report: 已解析年报对象。

    Returns:
        年报 `§8` 披露的换手率与披露口径。

    Raises:
        无显式抛出。
    """

    turnover_rate = _extract_field(report, "turnover_rate")
    turnover_basis = _extract_field(report, "turnover_basis")
    if turnover_rate is None:
        if turnover_basis is None:
            return _missing_field("§8 未披露可规则化抽取的换手率")
        anchors = (
            _build_anchor(report, turnover_basis),
        )
        return ExtractedField(
            value={
                "turnover_rate": None,
                "turnover_basis": turnover_basis.value,
            },
            anchors=anchors,
            extraction_mode="missing",
            note="§8 未披露换手率数值；当前不把口径说明单独视为换手率披露。",
        )
    return ExtractedField(
        value={
            "turnover_rate": turnover_rate.value,
            "turnover_basis": turnover_basis.value if turnover_basis else None,
        },
        anchors=tuple(
            _build_anchor(report, matched_field)
            for matched_field in (turnover_rate, turnover_basis)
            if matched_field is not None
        ),
        extraction_mode="direct",
        note=None,
    )


def _build_manager_alignment(report: ParsedAnnualReport) -> ExtractedField[dict[str, object]]:
    """构造基金经理/从业人员持有字段，见模板第 3 章利益一致性判断。

    Args:
        report: 已解析年报对象。

    Returns:
        年报 `§9` 披露的基金经理与从业人员持有原始数据。

    Raises:
        无显式抛出。
    """

    manager_holding = _extract_field(report, "manager_holding")
    employee_holding = _extract_field(report, "employee_holding")
    if manager_holding is None or employee_holding is None:
        table_manager_holding, table_employee_holding = _extract_manager_alignment_from_tables(report)
        manager_holding = manager_holding or table_manager_holding
        employee_holding = employee_holding or table_employee_holding
    return _build_field_from_matches(
        report=report,
        matched_fields=(manager_holding, employee_holding),
        value={
            "manager_holding": manager_holding.value if manager_holding else None,
            "employee_holding": employee_holding.value if employee_holding else None,
            "judgment": None,
        },
        missing_note="§9 未披露可规则化抽取的基金经理/从业人员持有信息",
    )


def _build_holder_structure(report: ParsedAnnualReport) -> ExtractedField[dict[str, object]]:
    """构造持有人结构字段，见模板第 6 章核心风险与否决项。

    Args:
        report: 已解析年报对象。

    Returns:
        年报 `§9` 披露的机构与个人持有人结构。

    Raises:
        无显式抛出。
    """

    institutional_holder = _extract_field(report, "institutional_holder")
    individual_holder = _extract_field(report, "individual_holder")
    if institutional_holder is None or individual_holder is None:
        table_institutional_holder, table_individual_holder = _extract_holder_structure_from_table(
            report
        )
        institutional_holder = institutional_holder or table_institutional_holder
        individual_holder = individual_holder or table_individual_holder
    return _build_field_from_matches(
        report=report,
        matched_fields=(institutional_holder, individual_holder),
        value={
            "institutional_holder": institutional_holder.value if institutional_holder else None,
            "individual_holder": individual_holder.value if individual_holder else None,
        },
        missing_note="§9 未披露可规则化抽取的机构/个人持有人结构",
    )


def extract_manager_ownership(report: ParsedAnnualReport) -> ManagerOwnershipExtractionResult:
    """抽取 `§4/§8/§9` 管理人文本、换手率、持有披露与持有人结构。

    Args:
        report: 已解析年报对象。

    Returns:
        `manager_strategy_text`、`turnover_rate`、`manager_alignment`、`holder_structure` 四类结果。

    Raises:
        无显式抛出。
    """

    return ManagerOwnershipExtractionResult(
        manager_strategy_text=_build_manager_strategy_text(report),
        turnover_rate=_build_turnover_rate(report),
        manager_alignment=_build_manager_alignment(report),
        holder_structure=_build_holder_structure(report),
    )
