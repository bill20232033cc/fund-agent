"""`§3` 净值表现与投资者收益率抽取。"""

from __future__ import annotations

import re
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import Final

from fund_agent.fund.documents.models import ParsedAnnualReport, ParsedTable
from fund_agent.fund.extractors.models import (
    EvidenceAnchor,
    ExtractedField,
    PerformanceExtractionResult,
    TrackingErrorValue,
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
_NAV_GROWTH_RATE_PATH: Final[str] = "nav_benchmark_performance.nav_growth_rate"
_BENCHMARK_RETURN_RATE_PATH: Final[str] = (
    "nav_benchmark_performance.benchmark_return_rate"
)
_TRACKING_ERROR_KEYWORDS: Final[tuple[str, ...]] = ("跟踪误差", "跟踪偏离度")
_TRACKING_ERROR_NEGATIVE_KEYWORDS: Final[tuple[str, ...]] = (
    "控制在",
    "不超过",
    "力争",
    "争取",
    "目标",
    "限制",
    "控制目标",
    "风险控制",
    "最小化",
)
_TRACKING_ERROR_ACTUAL_KEYWORDS: Final[tuple[str, ...]] = (
    "实际",
    "报告期",
    "本报告期",
    "过去一年",
)
_TRACKING_ERROR_VALUE_PATTERN: Final[re.Pattern[str]] = re.compile(
    r"(?P<value>[-+]?\d+(?:,\d{3})*(?:\.\d+)?)\s*%"
)
_TRACKING_ERROR_NOTE_TARGET_OR_LIMIT: Final[str] = "tracking_error_target_or_limit"
_TRACKING_ERROR_NOTE_MANAGER_NARRATIVE: Final[str] = "tracking_error_manager_narrative"
_TRACKING_ERROR_NOTE_BENCHMARK_ONLY: Final[str] = "tracking_error_benchmark_only"
_TRACKING_ERROR_NOTE_STANDARD_DEVIATION_ONLY: Final[str] = "tracking_error_standard_deviation_only"
_TRACKING_ERROR_NOTE_MIXED_ACTUAL_AND_TARGET: Final[str] = "tracking_error_mixed_actual_and_target"
_TRACKING_ERROR_NOTE_UNPARSEABLE: Final[str] = "tracking_error_unparseable"
_TRACKING_ERROR_NOTE_INCOMPLETE_ANCHOR: Final[str] = "tracking_error_incomplete_anchor"
_TRACKING_ERROR_NOTE_TABLE_TEXT_INCONSISTENT: Final[str] = "tracking_error_table_text_inconsistent"
_TRACKING_ERROR_NOTE_MULTI_MATCH: Final[str] = "tracking_error_multi_match"
_TRACKING_ERROR_NOTE_MISSING: Final[str] = "年报未直接披露跟踪误差"
_TRACKING_ERROR_BLOCKER_PRECEDENCE: Final[tuple[str, ...]] = (
    _TRACKING_ERROR_NOTE_TABLE_TEXT_INCONSISTENT,
    _TRACKING_ERROR_NOTE_MULTI_MATCH,
    _TRACKING_ERROR_NOTE_INCOMPLETE_ANCHOR,
    _TRACKING_ERROR_NOTE_UNPARSEABLE,
    _TRACKING_ERROR_NOTE_MIXED_ACTUAL_AND_TARGET,
    _TRACKING_ERROR_NOTE_TARGET_OR_LIMIT,
    _TRACKING_ERROR_NOTE_MANAGER_NARRATIVE,
    _TRACKING_ERROR_NOTE_BENCHMARK_ONLY,
    _TRACKING_ERROR_NOTE_STANDARD_DEVIATION_ONLY,
    _TRACKING_ERROR_NOTE_MISSING,
)
_TRACKING_ERROR_MANAGER_NARRATIVE_KEYWORDS: Final[tuple[str, ...]] = (
    "基金经理",
    "投资经理",
    "组合管理",
    "投资管理",
    "管理组合",
)
_TRACKING_ERROR_BENCHMARK_ONLY_KEYWORDS: Final[tuple[str, ...]] = (
    "业绩比较基准",
    "比较基准",
    "基准指数",
)
_STANDARD_DEVIATION_KEYWORDS: Final[tuple[str, ...]] = (
    "净值增长率标准差",
    "基准收益率标准差",
    "业绩比较基准收益率标准差",
)


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


@dataclass(frozen=True, slots=True)
class _MatchedTrackingError:
    """跟踪误差命中结果。

    Attributes:
        value_text: 年报披露的数值文本。
        matched_text: 命中的行或表格上下文。
        period_label: 跟踪误差期间。
        annualized: 是否年化。
        section_id: 命中章节。
        table: 命中的表格；文本命中时为 `None`。
        row_label: 表格行标签。
        matched_header: 表格表头。
    """

    value_text: str
    matched_text: str
    period_label: str
    annualized: bool
    section_id: str = _SECTION_ID
    table: ParsedTable | None = None
    row_label: str | None = None
    matched_header: str | None = None


@dataclass(frozen=True, slots=True)
class _TrackingErrorExtractionOutcome:
    """跟踪误差抽取路径结果，见模板第 2 章 R=A+B-C。

    Attributes:
        match: 直接披露命中结果。
        blocker_note: 未能采信时的最具体 fail-closed 原因。
    """

    match: _MatchedTrackingError | None
    blocker_note: str | None = None


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


def _extract_tracking_error(report: ParsedAnnualReport) -> ExtractedField[TrackingErrorValue]:
    """从年报 `§3/§2` 提取直接披露的实际跟踪误差，见模板第 2 章 R=A+B-C。

    Args:
        report: 已解析年报对象。

    Returns:
        直接披露时返回 `direct`；缺失、目标值或语义模糊时返回 `missing`。

    Raises:
        无显式抛出。
    """

    table_outcome = _extract_tracking_error_from_tables(report)
    text_outcome = _extract_tracking_error_from_text(report)
    blocker_note = _select_tracking_error_blocker_note(
        (table_outcome.blocker_note, text_outcome.blocker_note)
    )
    if table_outcome.match is not None and text_outcome.match is not None:
        match = _select_consistent_tracking_error_match(table_outcome.match, text_outcome.match)
        if match is None:
            return _missing_tracking_error(_TRACKING_ERROR_NOTE_TABLE_TEXT_INCONSISTENT)
    else:
        match = table_outcome.match or text_outcome.match
    if match is None:
        return _missing_tracking_error(blocker_note or _TRACKING_ERROR_NOTE_MISSING)
    value = _parse_percent_ratio(match.value_text)
    if value is None:
        return _missing_tracking_error(_TRACKING_ERROR_NOTE_UNPARSEABLE)
    anchor = _build_tracking_error_anchor(report, match)
    return ExtractedField(
        value=TrackingErrorValue(
            value=value,
            value_text=match.value_text,
            unit="ratio",
            period_label=match.period_label,
            period_start=None,
            period_end=None,
            annualized=match.annualized,
            source_type="direct_disclosure",
            calculation_method="disclosed",
            benchmark_identity_status="missing",
            benchmark_index_name=None,
            benchmark_index_code=None,
            fund_series_source=None,
            index_series_source=None,
            observation_count=None,
            frequency="annual_report_period",
            annualization_factor=None,
            input_period_complete=True,
            provenance_note="年报§3直接披露的实际跟踪误差；未使用业绩基准收益率或标准差列推导。",
        ),
        anchors=(anchor,),
        extraction_mode="direct",
        note=None,
    )


def _select_consistent_tracking_error_match(
    table_match: _MatchedTrackingError,
    text_match: _MatchedTrackingError,
) -> _MatchedTrackingError | None:
    """在表格和正文同时命中时选择一致的跟踪误差披露。

    Args:
        table_match: 表格命中结果。
        text_match: 正文命中结果。

    Returns:
        两者解析值一致时优先返回表格命中；不一致时返回 `None` 代表语义模糊。

    Raises:
        无显式抛出。
    """

    table_value = _parse_percent_ratio(table_match.value_text)
    text_value = _parse_percent_ratio(text_match.value_text)
    if table_value is None or text_value is None:
        return None
    if table_value != text_value:
        return None
    return table_match


def _extract_tracking_error_from_tables(report: ParsedAnnualReport) -> _TrackingErrorExtractionOutcome:
    """从 `§3` 表格中提取实际跟踪误差。

    Args:
        report: 已解析年报对象。

    Returns:
        包含直接命中或具体 blocker note 的抽取结果。

    Raises:
        无显式抛出。
    """

    matches: list[_MatchedTrackingError] = []
    blocker_notes: list[str] = []
    for table in report.tables:
        header_index = _find_tracking_error_header_index(table.headers)
        if header_index is None:
            note = _classify_tracking_error_nonmatch_context(_table_text(table))
            if note is not None:
                blocker_notes.append(note)
            continue
        period_index = _find_header_index(table.headers, ("阶段",))
        for row in table.rows:
            value = _cell_at(row, header_index)
            context = " ".join((*table.headers, *row))
            if value is None:
                continue
            if _parse_percent_ratio(value) is None:
                blocker_notes.append(_TRACKING_ERROR_NOTE_UNPARSEABLE)
                continue
            if _tracking_error_context_is_target_or_ambiguous(context):
                blocker_notes.append(_classify_tracking_error_target_context(context))
                continue
            row_label = _cell_at(row, period_index) or "报告期"
            matches.append(
                _MatchedTrackingError(
                    value_text=value,
                    matched_text=context,
                    period_label=row_label,
                    annualized=_is_annualized_text(table.headers[header_index]),
                    table=table,
                    row_label=row_label,
                    matched_header=table.headers[header_index],
                )
            )
    if len(matches) > 1:
        return _TrackingErrorExtractionOutcome(match=None, blocker_note=_TRACKING_ERROR_NOTE_MULTI_MATCH)
    if not matches:
        return _TrackingErrorExtractionOutcome(
            match=None,
            blocker_note=_select_tracking_error_blocker_note(tuple(blocker_notes)),
        )
    return _TrackingErrorExtractionOutcome(match=matches[0])


def _extract_tracking_error_from_text(report: ParsedAnnualReport) -> _TrackingErrorExtractionOutcome:
    """从 `§3` 优先、`§2` 兜底的正文中提取实际跟踪误差。

    Args:
        report: 已解析年报对象。

    Returns:
        包含直接命中或具体 blocker note 的抽取结果。

    Raises:
        无显式抛出。
    """

    matches: list[_MatchedTrackingError] = []
    blocker_notes: list[str] = []
    for section_id in ("§3", "§2"):
        section_text = report.get_section_text(section_id)
        if not section_text:
            continue
        for line in section_text.splitlines():
            normalized_line = line.strip()
            if not _line_mentions_tracking_error(normalized_line):
                note = _classify_tracking_error_nonmatch_context(normalized_line)
                if note is not None:
                    blocker_notes.append(note)
                continue
            if not _line_has_tracking_error_value(normalized_line):
                note = _classify_tracking_error_line_without_parseable_value(normalized_line)
                if note is not None:
                    blocker_notes.append(note)
                continue
            if _tracking_error_context_is_target_or_ambiguous(normalized_line):
                blocker_notes.append(_classify_tracking_error_target_context(normalized_line))
                continue
            value_text = _extract_percent_text(normalized_line)
            if value_text is None:
                blocker_notes.append(_TRACKING_ERROR_NOTE_UNPARSEABLE)
                continue
            matches.append(
                _MatchedTrackingError(
                    value_text=value_text,
                    matched_text=normalized_line,
                    period_label=_period_label_from_text(normalized_line),
                    annualized=_is_annualized_text(normalized_line),
                    section_id=section_id,
                )
            )
    if len(matches) > 1:
        return _TrackingErrorExtractionOutcome(match=None, blocker_note=_TRACKING_ERROR_NOTE_MULTI_MATCH)
    if not matches:
        return _TrackingErrorExtractionOutcome(
            match=None,
            blocker_note=_select_tracking_error_blocker_note(tuple(blocker_notes)),
        )
    return _TrackingErrorExtractionOutcome(match=matches[0])


def _find_tracking_error_header_index(headers: tuple[str, ...]) -> int | None:
    """查找跟踪误差表头下标。

    Args:
        headers: 表头元组。

    Returns:
        命中时返回下标，否则返回 `None`。

    Raises:
        无显式抛出。
    """

    for index, header in enumerate(headers):
        normalized_header = _compact_text(header)
        if "标准差" in normalized_header:
            continue
        if any(keyword in normalized_header for keyword in _TRACKING_ERROR_KEYWORDS):
            return index
    return None


def _select_tracking_error_blocker_note(notes: tuple[str | None, ...]) -> str | None:
    """按固定优先级选择跟踪误差 fail-closed note。

    Args:
        notes: 各抽取路径记录的 blocker note。

    Returns:
        命中优先级最高的 note；没有有效 note 时返回 `None`。

    Raises:
        无显式抛出。
    """

    available_notes = {note for note in notes if note is not None}
    for note in _TRACKING_ERROR_BLOCKER_PRECEDENCE:
        if note in available_notes:
            return note
    return None


def _line_mentions_tracking_error(line: str) -> bool:
    """判断文本行是否提到跟踪误差语义。

    Args:
        line: 年报正文行。

    Returns:
        包含跟踪误差或跟踪偏离度语义时返回 `True`。

    Raises:
        无显式抛出。
    """

    normalized_line = _compact_text(line)
    return any(keyword in normalized_line for keyword in _TRACKING_ERROR_KEYWORDS)


def _line_has_tracking_error_value(line: str) -> bool:
    """判断文本行是否包含跟踪误差数值。

    Args:
        line: 年报正文行。

    Returns:
        同时包含跟踪误差语义和百分比数值时返回 `True`。

    Raises:
        无显式抛出。
    """

    return _line_mentions_tracking_error(line) and _extract_percent_text(line) is not None


def _classify_tracking_error_nonmatch_context(text: str) -> str | None:
    """分类未形成候选值的跟踪误差相关上下文。

    Args:
        text: 表格或正文上下文。

    Returns:
        可确定的 blocker note；无法确定时返回 `None`。

    Raises:
        无显式抛出。
    """

    normalized_text = _compact_text(text)
    if any(keyword in normalized_text for keyword in _STANDARD_DEVIATION_KEYWORDS):
        return _TRACKING_ERROR_NOTE_STANDARD_DEVIATION_ONLY
    if not any(keyword in normalized_text for keyword in _TRACKING_ERROR_KEYWORDS):
        return None
    if _tracking_error_context_is_target_or_ambiguous(normalized_text):
        return _classify_tracking_error_target_context(normalized_text)
    if _is_manager_tracking_error_narrative(normalized_text):
        return _TRACKING_ERROR_NOTE_MANAGER_NARRATIVE
    return None


def _classify_tracking_error_line_without_parseable_value(line: str) -> str | None:
    """分类提到跟踪误差但没有可解析百分比值的正文行。

    Args:
        line: 年报正文行。

    Returns:
        可确定的 blocker note；无法确定时返回 `None`。

    Raises:
        无显式抛出。
    """

    if _tracking_error_context_is_target_or_ambiguous(line):
        return _classify_tracking_error_target_context(line)
    if _line_has_unparseable_tracking_error_value(line):
        return _TRACKING_ERROR_NOTE_UNPARSEABLE
    if _is_manager_tracking_error_narrative(line):
        return _TRACKING_ERROR_NOTE_MANAGER_NARRATIVE
    if _is_benchmark_only_tracking_error_context(line):
        return _TRACKING_ERROR_NOTE_BENCHMARK_ONLY
    return None


def _classify_tracking_error_target_context(text: str) -> str:
    """把目标/限制上下文细分为纯目标或实际目标混杂。

    Args:
        text: 表格或正文上下文。

    Returns:
        具体 blocker note。

    Raises:
        无显式抛出。
    """

    if _has_actual_tracking_error_signal(text):
        return _TRACKING_ERROR_NOTE_MIXED_ACTUAL_AND_TARGET
    return _TRACKING_ERROR_NOTE_TARGET_OR_LIMIT


def _line_has_unparseable_tracking_error_value(line: str) -> bool:
    """判断文本是否像直接披露但数值不可解析。

    Args:
        line: 年报正文行。

    Returns:
        出现实际披露信号和常见占位百分号时返回 `True`。

    Raises:
        无显式抛出。
    """

    normalized_line = _compact_text(line)
    return _has_actual_tracking_error_signal(normalized_line) and any(
        token in normalized_line for token in ("--%", "-%", "—%", "不适用", "未披露")
    )


def _is_manager_tracking_error_narrative(text: str) -> bool:
    """判断是否为基金经理或组合管理层面的跟踪误差叙事。

    Args:
        text: 年报正文行。

    Returns:
        同时提到跟踪误差和明确管理叙事信号时返回 `True`。

    Raises:
        无显式抛出。
    """

    normalized_text = _compact_text(text)
    return any(keyword in normalized_text for keyword in _TRACKING_ERROR_KEYWORDS) and any(
        keyword in normalized_text for keyword in _TRACKING_ERROR_MANAGER_NARRATIVE_KEYWORDS
    )


def _is_benchmark_only_tracking_error_context(text: str) -> bool:
    """判断是否为仅围绕业绩基准的跟踪误差上下文。

    Args:
        text: 年报正文行。

    Returns:
        明确提到基准和跟踪误差、但没有本基金实际披露信号时返回 `True`。

    Raises:
        无显式抛出。
    """

    normalized_text = _compact_text(text)
    return (
        any(keyword in normalized_text for keyword in _TRACKING_ERROR_KEYWORDS)
        and any(keyword in normalized_text for keyword in _TRACKING_ERROR_BENCHMARK_ONLY_KEYWORDS)
        and not _has_actual_tracking_error_signal(normalized_text)
    )


def _tracking_error_context_is_target_or_ambiguous(text: str) -> bool:
    """判断上下文是否只是目标、限制或控制口径。

    Args:
        text: 表格或正文上下文。

    Returns:
        存在目标/限制语义时返回 `True`。

    Raises:
        无显式抛出。
    """

    normalized_text = _compact_text(text)
    return any(keyword in normalized_text for keyword in _TRACKING_ERROR_NEGATIVE_KEYWORDS)


def _has_actual_tracking_error_signal(text: str) -> bool:
    """判断文本是否同时出现实际披露和目标控制语义。

    Args:
        text: 年报正文行。

    Returns:
        语义混杂时返回 `True`，调用方应 fail closed。

    Raises:
        无显式抛出。
    """

    normalized_text = _compact_text(text)
    return any(keyword in normalized_text for keyword in _TRACKING_ERROR_ACTUAL_KEYWORDS)


def _extract_percent_text(text: str) -> str | None:
    """从文本中提取百分比数值原文。

    Args:
        text: 年报正文或表格单元格。

    Returns:
        首个百分比数值；不存在时返回 `None`。

    Raises:
        无显式抛出。
    """

    match = _TRACKING_ERROR_VALUE_PATTERN.search(text)
    if match is None:
        return None
    return f"{match.group('value').replace(',', '')}%"


def _parse_percent_ratio(value_text: str) -> Decimal | None:
    """把百分比文本解析为小数比例。

    Args:
        value_text: 百分比文本。

    Returns:
        小数比例；无法解析时返回 `None`。

    Raises:
        无显式抛出。
    """

    match = _TRACKING_ERROR_VALUE_PATTERN.search(value_text)
    if match is None:
        return None
    try:
        return Decimal(match.group("value").replace(",", "")) / Decimal("100")
    except InvalidOperation:
        return None


def _period_label_from_text(text: str) -> str:
    """从披露文本中提取期间标签。

    Args:
        text: 年报正文行。

    Returns:
        期间标签；无法精确定位时返回 `报告期`。

    Raises:
        无显式抛出。
    """

    if "过去一年" in text:
        return "过去一年"
    if "本报告期" in text:
        return "本报告期"
    if "报告期" in text:
        return "报告期"
    return "报告期"


def _is_annualized_text(text: str) -> bool:
    """判断文本是否标注年化口径。

    Args:
        text: 表头或正文。

    Returns:
        包含年化语义时返回 `True`。

    Raises:
        无显式抛出。
    """

    return "年化" in text or "年跟踪误差" in _compact_text(text)


def _build_tracking_error_anchor(
    report: ParsedAnnualReport,
    matched: _MatchedTrackingError,
) -> EvidenceAnchor:
    """构造跟踪误差证据锚点。

    Args:
        report: 已解析年报对象。
        matched: 跟踪误差命中结果。

    Returns:
        年报证据锚点。

    Raises:
        无显式抛出。
    """

    if matched.table is not None:
        return EvidenceAnchor(
            source_kind="annual_report",
            document_year=report.key.year,
            section_id=matched.section_id,
            page_number=matched.table.page_number,
            table_id=_table_id(matched.table),
            row_locator="tracking_error",
            note=f"{matched.row_label}; {matched.matched_header}",
        )
    return EvidenceAnchor(
        source_kind="annual_report",
        document_year=report.key.year,
        section_id=matched.section_id,
        page_number=None,
        table_id=None,
        row_locator="tracking_error",
        note=matched.matched_text,
    )


def _missing_tracking_error(note: str) -> ExtractedField[TrackingErrorValue]:
    """构造跟踪误差缺失字段。

    Args:
        note: 缺失或 fail closed 原因。

    Returns:
        `missing` 跟踪误差字段。

    Raises:
        无显式抛出。
    """

    return ExtractedField(
        value=None,
        anchors=(),
        extraction_mode="missing",
        note=note,
    )


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


def _build_child_anchor(anchor: EvidenceAnchor, source_field_path: str) -> EvidenceAnchor:
    """给净值表现子字段锚点附加 canonical `source_field_path`。

    Args:
        anchor: 直接命中的原始锚点。
        source_field_path: 子字段 canonical path。

    Returns:
        带子字段路径的锚点。

    Raises:
        无显式抛出。
    """

    return EvidenceAnchor(
        source_kind=anchor.source_kind,
        document_year=anchor.document_year,
        section_id=anchor.section_id,
        page_number=anchor.page_number,
        table_id=anchor.table_id,
        row_locator=f"source_field_path={source_field_path}; locator={anchor.row_locator}",
        note=anchor.note,
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


def _missing_child_field(source_field_path: str, note: str) -> ExtractedField[object]:
    """构造缺失子字段，见模板第 2 章 R=A+B-C。

    Args:
        source_field_path: 子字段 canonical path。
        note: 缺失说明。

    Returns:
        不带锚点的 `missing` 子字段。

    Raises:
        无显式抛出。
    """

    return ExtractedField(
        value=None,
        anchors=(),
        extraction_mode="missing",
        note=f"source_field_path={source_field_path}; gap={note}",
    )


def _anchor_for_nav_match(
    report: ParsedAnnualReport,
    matched_field: _MatchedField | _MatchedTableField,
) -> EvidenceAnchor:
    """为净值表现命中结果构造原始锚点。

    Args:
        report: 已解析年报对象。
        matched_field: 文本或表格命中结果。

    Returns:
        原始证据锚点。

    Raises:
        无显式抛出。
    """

    if isinstance(matched_field, _MatchedTableField):
        return _build_table_anchor(report, matched_field)
    return _build_anchor(report, matched_field)


def _build_child_field(
    report: ParsedAnnualReport,
    matched_field: _MatchedField | _MatchedTableField | None,
    source_field_path: str,
    missing_note: str,
) -> ExtractedField[object]:
    """根据直接命中构造净值表现子字段，见模板第 2 章 R=A+B-C。

    Args:
        report: 已解析年报对象。
        matched_field: 子字段直接命中结果。
        source_field_path: 子字段 canonical path。
        missing_note: 未命中时的缺口说明。

    Returns:
        独立子字段抽取结果。

    Raises:
        无显式抛出。
    """

    if matched_field is None:
        return _missing_child_field(source_field_path, missing_note)
    anchor = _anchor_for_nav_match(report, matched_field)
    return ExtractedField(
        value=matched_field.value,
        anchors=(_build_child_anchor(anchor, source_field_path),),
        extraction_mode="direct",
        note=None,
    )


def _build_nav_benchmark_performance(
    report: ParsedAnnualReport,
) -> tuple[ExtractedField[dict[str, object]], ExtractedField[object], ExtractedField[object]]:
    """构造 `§3` 净值增长率与基准收益率复合字段和子字段。

    Args:
        report: 已解析年报对象。

    Returns:
        表现兼容复合字段、净值增长率子字段、基准收益率子字段。

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
    nav_growth_rate_field = _build_child_field(
        report,
        nav_growth_rate,
        _NAV_GROWTH_RATE_PATH,
        "§3 未披露净值增长率",
    )
    benchmark_return_rate_field = _build_child_field(
        report,
        benchmark_return_rate,
        _BENCHMARK_RETURN_RATE_PATH,
        "§3 未披露业绩比较基准收益率",
    )
    if nav_growth_rate is None and benchmark_return_rate is None:
        return (
            _missing_field("§3 未披露净值增长率/业绩比较基准收益率"),
            nav_growth_rate_field,
            benchmark_return_rate_field,
        )
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
    return (
        ExtractedField(
            value={
                "nav_growth_rate": nav_growth_rate_field.value,
                "benchmark_return_rate": benchmark_return_rate_field.value,
            },
            anchors=tuple(anchors),
            extraction_mode=extraction_mode,
            note=note,
        ),
        nav_growth_rate_field,
        benchmark_return_rate_field,
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

    nav_benchmark_performance, nav_growth_rate, benchmark_return_rate = (
        _build_nav_benchmark_performance(report)
    )
    return PerformanceExtractionResult(
        nav_benchmark_performance=nav_benchmark_performance,
        investor_return=_build_investor_return(report),
        tracking_error=_extract_tracking_error(report),
        nav_benchmark_performance_nav_growth_rate=nav_growth_rate,
        nav_benchmark_performance_benchmark_return_rate=benchmark_return_rate,
    )
