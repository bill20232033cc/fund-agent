"""基础画像与 §1/§2 信息抽取。"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Final, Literal

from fund_agent.fund.documents.models import ParsedAnnualReport, ParsedTable
from fund_agent.fund.extractors.models import (
    EvidenceAnchor,
    ExtractedField,
    IndexProfileValue,
    ProfileExtractionResult,
)
from fund_agent.fund.fund_type import FundType, FundTypeClassification, classify_fund_type

_FIELD_PATTERNS: Final[dict[str, tuple[tuple[str, tuple[str, ...]], ...]]] = {
    "fund_name": (
        ("§1", (r"基金名称\s*[：:]\s*(.+)", r"基金简称\s*[：:]\s*(.+)")),
        ("§2", (r"基金名称\s*[：:]\s*(.+)",)),
    ),
    "fund_code": (
        ("§1", (r"基金代码\s*[：:]\s*(.+)",)),
        ("§2", (r"基金代码\s*[：:]\s*(.+)",)),
    ),
    "fund_category": (
        ("§1", (r"基金类别\s*[：:]\s*(.+)", r"基金类型\s*[：:]\s*(.+)")),
        ("§2", (r"基金类别\s*[：:]\s*(.+)",)),
    ),
    "fund_scale": (
        ("§1", (r"基金规模\s*[：:]\s*(.+)", r"基金份额总额\s*[：:]\s*(.+)")),
        ("§2", (r"基金规模\s*[：:]\s*(.+)",)),
    ),
    "fund_manager": (
        ("§1", (r"基金经理\s*[：:]\s*(.+)",)),
        ("§2", (r"基金经理\s*[：:]\s*(.+)",)),
    ),
    "management_company": (("§2", (r"基金管理人\s*[：:]\s*(.+)",)),),
    "custodian": (("§2", (r"基金托管人\s*[：:]\s*(.+)",)),),
    "inception_date": (("§2", (r"基金合同生效日\s*[：:]\s*(.+)",)),),
    "investment_objective": (("§2", (r"投资目标\s*[：:]\s*(.+)",)),),
    "investment_scope": (("§2", (r"投资范围\s*[：:]\s*(.+)",)),),
    "investment_strategy": (("§2", (r"投资策略\s*[：:]\s*(.+)",)),),
    "style_positioning": (
        (
            "§2",
            (
                r"风格定位\s*[：:]\s*(.+)",
                r"风险收益特征\s*[：:]\s*(.+)",
                r"产品定位\s*[：:]\s*(.+)",
            ),
        ),
    ),
    "risk_characteristic_text": (
        (
            "§2",
            (
                r"风险收益特征\s*[：:]\s*(.+)",
                r"基金风险收益特征\s*[：:]\s*(.+)",
            ),
        ),
    ),
    "benchmark": (("§2", (r"业绩比较基准\s*[：:]\s*(.+)",)),),
    "management_fee": (("§2", (r"管理费(?:率)?\s*[：:]\s*(.+)",)),),
    "custody_fee": (("§2", (r"托管费(?:率)?\s*[：:]\s*(.+)",)),),
}
_TABLE_FIELD_LABELS: Final[dict[str, tuple[str, ...]]] = {
    "fund_name": ("基金名称", "基金简称"),
    "fund_code": ("基金主代码", "基金代码"),
    "fund_category": ("基金类型", "基金类别"),
    "fund_scale": ("报告期末基金份额总额", "基金份额总额", "基金规模"),
    "fund_manager": ("基金管理人", "基金经理"),
    "management_company": ("基金管理人",),
    "custodian": ("基金托管人",),
    "inception_date": ("基金合同生效日",),
    "investment_objective": ("投资目标",),
    "investment_scope": ("投资范围",),
    "investment_strategy": ("投资策略",),
    "style_positioning": ("风格定位", "风险收益特征", "产品定位"),
    "risk_characteristic_text": ("风险收益特征", "基金风险收益特征"),
    "benchmark": ("业绩比较基准",),
    "management_fee": ("管理费率", "管理费"),
    "custody_fee": ("托管费率", "托管费"),
}
_SECTION_TWO_TABLE_MIN_PAGE: Final[int] = 1
_INDEX_APPLICABLE_FUND_TYPES: Final[frozenset[FundType]] = frozenset(
    ("index_fund", "enhanced_index")
)
_COMPOSITE_BENCHMARK_SEPARATORS: Final[tuple[str, ...]] = ("＋", "+", "×", "*", "和", "及")
_BENCHMARK_NEWLINE_RUN_PATTERN: Final[re.Pattern[str]] = re.compile(
    r"[ \t\f\v]*(?:\r\n|\r|\n)+[ \t\f\v]*"
)
_ASCII_WORD_CHAR_PATTERN: Final[re.Pattern[str]] = re.compile(r"[A-Za-z0-9]")
_INDEX_NAME_PATTERN: Final[re.Pattern[str]] = re.compile(
    r"(?P<name>[\u4e00-\u9fa5A-Za-z0-9]+(?:指数|Index|ETF))"
)
_FEE_RATE_PATTERN: Final[re.Pattern[str]] = re.compile(r"(?P<rate>\d+(?:\.\d+)?\s*%)")
_FEE_SUBSECTION_BOUNDARY_PATTERN: Final[re.Pattern[str]] = re.compile(
    r"\n\s*7\s*\.\s*4\s*\.\s*10\s*\.\s*(?:2\s*\.\s*\d+|[3-9])"
)
_FEE_FALLBACK_WINDOW_CHARS: Final[int] = 2000
_FEE_SCHEDULE_MANAGEMENT_FEE_PATH: Final[str] = "fee_schedule.management_fee"
_FEE_SCHEDULE_CUSTODY_FEE_PATH: Final[str] = "fee_schedule.custody_fee"


@dataclass(frozen=True, slots=True)
class _FeeFallbackRule:
    """费率 fallback 抽取规则，见模板第 2 章 R=A+B-C 的 Cost 项。

    Attributes:
        field_name: 输出字段名。
        subsection_number: parser 可见的年报子章节编号。
        subsection_title: 子章节标题。
        semantic_labels: 表格或文本中可确认费率类别的语义标签。
    """

    field_name: str
    subsection_number: str
    subsection_title: str
    semantic_labels: tuple[str, ...]


_FEE_FALLBACK_RULES: Final[dict[str, _FeeFallbackRule]] = {
    "management_fee": _FeeFallbackRule(
        field_name="management_fee",
        subsection_number="7.4.10.2.1",
        subsection_title="基金管理费",
        semantic_labels=("基金管理费", "管理费"),
    ),
    "custody_fee": _FeeFallbackRule(
        field_name="custody_fee",
        subsection_number="7.4.10.2.2",
        subsection_title="基金托管费",
        semantic_labels=("基金托管费", "托管费"),
    ),
}
_RISK_CHARACTERISTIC_SCHEMA_VERSION: Final[str] = "risk_characteristic_text.v1"


@dataclass(frozen=True, slots=True)
class _MatchedField:
    """字段命中结果。

    Attributes:
        field_name: 字段名。
        value: 抽取到的字段值。
        section_id: 命中章节。
        matched_line: 命中的原始行文本。
    """

    field_name: str
    value: str
    section_id: str
    matched_line: str
    page_number: int | None = None
    table_id: str | None = None


def _extract_field(report: ParsedAnnualReport, field_name: str) -> _MatchedField | None:
    """从 `§1/§2` 中提取单个字段。

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
    return _extract_field_from_section_two_tables(report, field_name)


def _extract_field_from_section_two_tables(
    report: ParsedAnnualReport, field_name: str
) -> _MatchedField | None:
    """从 `§2` 键值型表格提取单个字段，见模板第 1 章产品本质。

    Args:
        report: 已解析年报对象。
        field_name: 目标字段名。

    Returns:
        命中时返回字段命中结果，否则返回 `None`。

    Raises:
        KeyError: 请求未知字段时抛出。
    """

    labels = _TABLE_FIELD_LABELS[field_name]
    for table in report.tables:
        for row in _iter_key_value_rows(table):
            matched_value = _match_key_value_row(row, labels)
            if matched_value is None:
                continue
            label, value = matched_value
            return _MatchedField(
                field_name=field_name,
                value=value,
                section_id="§2",
                matched_line=f"{label}：{value}",
                page_number=table.page_number
                if table.page_number >= _SECTION_TWO_TABLE_MIN_PAGE
                else None,
                table_id=_table_id(table),
            )
    return None


def _extract_fee_from_fallback_subsection(
    report: ParsedAnnualReport, field_name: str
) -> _MatchedField | None:
    """从 parser 可见的 `7.4.10.2` 子章节语义中提取费率，见模板第 2 章 Cost。

    S0 证据表明 004393 的 parser cache 中没有可直接读取的 `§7`，且 `7.4.10.2`
    出现在 parser 可见的其它章节文本中。因此这里扫描 `raw_text` 和表格语义，
    而不是依赖 `get_section_text("§7")`。

    Args:
        report: 已解析年报对象。
        field_name: `management_fee` 或 `custody_fee`。

    Returns:
        命中时返回字段命中结果，否则返回 `None`。

    Raises:
        KeyError: 请求未知 fee fallback 字段时抛出。
    """

    rule = _FEE_FALLBACK_RULES[field_name]
    text_match = _extract_fee_from_fallback_text(report, rule)
    if text_match is not None:
        return text_match
    return _extract_fee_from_fallback_tables(report, rule)


def _extract_fee_from_fallback_text(
    report: ParsedAnnualReport, rule: _FeeFallbackRule
) -> _MatchedField | None:
    """从 `7.4.10.2` 子章节文本窗口提取费率，见模板第 2 章 Cost。

    Args:
        report: 已解析年报对象。
        rule: 目标费率 fallback 规则。

    Returns:
        命中时返回字段命中结果，否则返回 `None`。

    Raises:
        无显式抛出。
    """

    subsection_text = _fallback_subsection_text(report.raw_text, rule)
    if subsection_text is None:
        return None
    rate = _extract_scalar_fee_rate(subsection_text)
    if rate is None:
        return None
    section_id = _section_id_for_text_offset(report, report.raw_text.find(subsection_text))
    return _MatchedField(
        field_name=rule.field_name,
        value=rate,
        section_id=section_id,
        matched_line=f"{rule.subsection_number} {rule.subsection_title}：{rate}",
    )


def _extract_fee_from_fallback_tables(
    report: ParsedAnnualReport, rule: _FeeFallbackRule
) -> _MatchedField | None:
    """从 parser 表格语义提取 `7.4.10.2` 费率，见模板第 2 章 Cost。

    Args:
        report: 已解析年报对象。
        rule: 目标费率 fallback 规则。

    Returns:
        命中时返回字段命中结果，否则返回 `None`。

    Raises:
        无显式抛出。
    """

    for table in report.tables:
        in_target_context = False
        for row in _iter_key_value_rows(table):
            row_text = " ".join(cell.strip() for cell in row if cell.strip())
            row_context = _fee_row_context(row_text, rule)
            if row_context == "target":
                in_target_context = True
            elif row_context == "other_fee_subsection":
                in_target_context = False

            if not _row_matches_fee_semantics(row_text, in_target_context):
                continue
            rate = _extract_scalar_fee_rate(row_text)
            if rate is None:
                continue
            return _MatchedField(
                field_name=rule.field_name,
                value=rate,
                section_id=_section_id_for_fee_table(rule),
                matched_line=f"{rule.subsection_number} {rule.subsection_title}：{row_text}",
                page_number=table.page_number,
                table_id=_table_id(table),
            )
    return None


def _fallback_subsection_text(raw_text: str, rule: _FeeFallbackRule) -> str | None:
    """定位 `7.4.10.2.x` 子章节文本窗口，见模板第 2 章 Cost。

    Args:
        raw_text: parser 可见全文。
        rule: 目标费率 fallback 规则。

    Returns:
        子章节文本；未定位时返回 `None`。

    Raises:
        无显式抛出。
    """

    match = _fallback_subsection_heading_match(raw_text, rule)
    if match is None:
        return None
    window = raw_text[match.start() : match.start() + _FEE_FALLBACK_WINDOW_CHARS]
    boundary = _FEE_SUBSECTION_BOUNDARY_PATTERN.search(window, pos=max(match.end() - match.start(), 1))
    if boundary is not None:
        window = window[: boundary.start()]
    return window


def _fallback_subsection_heading_match(
    raw_text: str, rule: _FeeFallbackRule
) -> re.Match[str] | None:
    """定位目标 `7.4.10.2.x` 子章节标题，见模板第 2 章 Cost。

    Args:
        raw_text: parser 可见全文。
        rule: 目标费率 fallback 规则。

    Returns:
        命中的子章节标题；未命中时返回 `None`。

    Raises:
        无显式抛出。
    """

    return re.search(
        rf"{re.escape(rule.subsection_number)}\s*{re.escape(rule.subsection_title)}",
        raw_text,
    )


def _fee_row_context(
    row_text: str,
    rule: _FeeFallbackRule,
) -> Literal["target", "other_fee_subsection", "unchanged"]:
    """判断表格行是否切换到目标费率子章节上下文，见模板第 2 章 Cost。

    Args:
        row_text: 表格行合并文本。
        rule: 目标费率 fallback 规则。

    Returns:
        `target` 表示目标 `7.4.10.2.x` 上下文，`other_fee_subsection`
        表示其它费率子章节，`unchanged` 表示沿用前一行上下文。

    Raises:
        无显式抛出。
    """

    normalized_row = _normalize_fee_context_text(row_text)
    if _row_contains_fee_subsection(normalized_row, rule.subsection_number):
        return "target"
    if re.search(r"7\.4\.10\.2\.\d+", normalized_row):
        return "other_fee_subsection"
    return "unchanged"


def _row_contains_fee_subsection(normalized_row: str, subsection_number: str) -> bool:
    """判断行文本是否包含完整目标费率子章节编号，见模板第 2 章 Cost。

    Args:
        normalized_row: 已去除空白的表格行文本。
        subsection_number: 目标子章节编号。

    Returns:
        包含完整目标编号且不是更长编号前缀时返回 `True`。

    Raises:
        无显式抛出。
    """

    normalized_subsection = _normalize_fee_context_text(subsection_number)
    return re.search(rf"{re.escape(normalized_subsection)}(?!\d)", normalized_row) is not None


def _normalize_fee_context_text(value: str) -> str:
    """规范化费率子章节上下文文本，见模板第 2 章 Cost。

    Args:
        value: 原始表格行或章节编号。

    Returns:
        去除空白后的文本。

    Raises:
        无显式抛出。
    """

    return re.sub(r"\s+", "", value)


def _row_matches_fee_semantics(row_text: str, in_target_context: bool) -> bool:
    """判断表格行是否具备目标费率语义，见模板第 2 章 Cost。

    Args:
        row_text: 表格行合并文本。
        in_target_context: 当前行是否处于目标 `7.4.10.2.x` 子章节上下文。

    Returns:
        处于目标子章节上下文且存在非空文本时返回 `True`。

    Raises:
        无显式抛出。
    """

    return in_target_context and bool(row_text.strip())


def _extract_scalar_fee_rate(value: str) -> str | None:
    """从文本中提取用户可比较的标量费率，见模板第 2 章 Cost。

    Args:
        value: 含费率披露的文本。

    Returns:
        形如 `1.20%` 的费率；未命中时返回 `None`。

    Raises:
        无显式抛出。
    """

    match = _FEE_RATE_PATTERN.search(value)
    if match is None:
        return None
    return re.sub(r"\s+", "", match.group("rate"))


def _section_id_for_text_offset(report: ParsedAnnualReport, offset: int) -> str:
    """根据全文偏移反查 parser 章节编号。

    Args:
        report: 已解析年报对象。
        offset: raw_text 中的字符偏移。

    Returns:
        命中的章节编号；无法定位时返回 `§7.4.10.2` 语义锚点。

    Raises:
        无显式抛出。
    """

    if offset < 0:
        return "§7.4.10.2"
    for section in report.sections.values():
        if section.start_offset <= offset < section.end_offset:
            return section.section_id
    return "§7.4.10.2"


def _section_id_for_fee_table(rule: _FeeFallbackRule) -> str:
    """为费率表格 fallback 生成目标子章节锚点，见模板第 2 章 Cost。

    Args:
        rule: 目标费率 fallback 规则。

    Returns:
        目标子章节语义锚点。

    Raises:
        无显式抛出。
    """

    return f"§{rule.subsection_number}"


def _iter_key_value_rows(table: ParsedTable) -> tuple[tuple[str, ...], ...]:
    """返回可按键值行解释的表头与表格行。

    Args:
        table: 年报解析出的表格。

    Returns:
        先包含表头、再包含数据行的元组，便于处理真实年报中把首个键值对放入表头的情况。

    Raises:
        无显式抛出。
    """

    return (table.headers, *table.rows)


def _match_key_value_row(row: tuple[str, ...], labels: tuple[str, ...]) -> tuple[str, str] | None:
    """在一行表格中识别字段名和值。

    Args:
        row: 表格行。
        labels: 允许匹配的字段标签。

    Returns:
        命中时返回 `(标签, 值)`，否则返回 `None`。

    Raises:
        无显式抛出。
    """

    cells = tuple(cell.strip() for cell in row)
    for index, cell in enumerate(cells):
        normalized_cell = _normalize_label(cell)
        for label in labels:
            if _normalize_label(label) != normalized_cell:
                continue
            value = _first_non_empty_after(cells, index)
            if value:
                return label, value
    return None


def _first_non_empty_after(cells: tuple[str, ...], start_index: int) -> str | None:
    """读取字段名单元格之后第一个非空值。

    Args:
        cells: 当前表格行的单元格。
        start_index: 字段名单元格下标。

    Returns:
        第一个非空值；不存在时返回 `None`。

    Raises:
        无显式抛出。
    """

    for cell in cells[start_index + 1 :]:
        if cell.strip():
            return cell.strip()
    return None


def _normalize_label(value: str) -> str:
    """规范化表格字段标签。

    Args:
        value: 原始标签。

    Returns:
        去除空白和常见分隔符后的标签文本。

    Raises:
        无显式抛出。
    """

    return re.sub(r"[\s：:]+", "", value)


def _table_id(table: ParsedTable) -> str:
    """构造表格证据 ID。

    Args:
        table: 表格对象。

    Returns:
        可读表格 ID。

    Raises:
        无显式抛出。
    """

    return f"page-{table.page_number}-table-{table.table_index}"


def _previous_non_space_char(value: str, end_index: int) -> str | None:
    """读取指定位置之前最近的非空白字符。

    Args:
        value: 原始文本。
        end_index: 向前查找的结束下标。

    Returns:
        找到时返回单个字符，否则返回 `None`。

    Raises:
        无显式抛出。
    """

    for index in range(end_index - 1, -1, -1):
        if not value[index].isspace():
            return value[index]
    return None


def _next_non_space_char(value: str, start_index: int) -> str | None:
    """读取指定位置之后最近的非空白字符。

    Args:
        value: 原始文本。
        start_index: 向后查找的起始下标。

    Returns:
        找到时返回单个字符，否则返回 `None`。

    Raises:
        无显式抛出。
    """

    for index in range(start_index, len(value)):
        if not value[index].isspace():
            return value[index]
    return None


def _is_ascii_word_char(value: str | None) -> bool:
    """判断字符是否属于需要用空格隔开的 ASCII 词元。

    Args:
        value: 待判断字符。

    Returns:
        属于 ASCII 字母或数字时返回 `True`，否则返回 `False`。

    Raises:
        无显式抛出。
    """

    return value is not None and _ASCII_WORD_CHAR_PATTERN.fullmatch(value) is not None


def _benchmark_newline_replacement(value: str, match: re.Match[str]) -> str:
    """判断单个基准文本换行片段应删除还是替换为空格。

    Args:
        value: 原始业绩比较基准文本。
        match: 换行片段匹配结果。

    Returns:
        两侧均为 ASCII 词元时返回一个空格，否则返回空字符串。

    Raises:
        无显式抛出。
    """

    previous_char = _previous_non_space_char(value, match.start())
    next_char = _next_non_space_char(value, match.end())
    if _is_ascii_word_char(previous_char) and _is_ascii_word_char(next_char):
        return " "
    return ""


def _normalize_benchmark_text(value: str) -> str:
    """规范化业绩比较基准中的 PDF 表格视觉换行，见模板第 1 章产品本质。

    Args:
        value: 年报披露的业绩比较基准文本。

    Returns:
        去除视觉换行后的业绩比较基准文本；非换行空格与标点变体保持不变。

    Raises:
        无显式抛出。
    """

    normalized_parts: list[str] = []
    last_index = 0
    for match in _BENCHMARK_NEWLINE_RUN_PATTERN.finditer(value):
        normalized_parts.append(value[last_index : match.start()])
        normalized_parts.append(_benchmark_newline_replacement(value, match))
        last_index = match.end()
    normalized_parts.append(value[last_index:])
    return "".join(normalized_parts).strip()


def _normalize_benchmark_matched_field(matched_field: _MatchedField) -> _MatchedField:
    """创建业绩比较基准专用的规范化命中结果。

    Args:
        matched_field: 原始字段命中结果。

    Returns:
        值和锚点备注同步规范化后的新命中结果；原对象不被修改。

    Raises:
        无显式抛出。
    """

    normalized_value = _normalize_benchmark_text(matched_field.value)
    if normalized_value == matched_field.value:
        return matched_field
    normalized_line = matched_field.matched_line.replace(
        matched_field.value,
        normalized_value,
        1,
    )
    if normalized_line == matched_field.matched_line:
        normalized_line = _normalize_benchmark_text(matched_field.matched_line)
    return _MatchedField(
        field_name=matched_field.field_name,
        value=normalized_value,
        section_id=matched_field.section_id,
        matched_line=normalized_line,
        page_number=matched_field.page_number,
        table_id=matched_field.table_id,
    )


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

    return EvidenceAnchor(
        source_kind="annual_report",
        document_year=report.key.year,
        section_id=matched_field.section_id,
        page_number=matched_field.page_number,
        table_id=matched_field.table_id,
        row_locator=matched_field.field_name,
        note=matched_field.matched_line,
    )


def _build_child_anchor(anchor: EvidenceAnchor, source_field_path: str) -> EvidenceAnchor:
    """给子字段锚点附加 canonical `source_field_path`，见模板第 2 章 Cost。

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
    """构造缺失子字段，见模板第 2 章 R=A+B-C 的 Cost 项。

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


def _build_child_field(
    report: ParsedAnnualReport,
    matched_field: _MatchedField | None,
    source_field_path: str,
    missing_note: str,
) -> ExtractedField[object]:
    """根据直接命中构造费率子字段，见模板第 2 章 R=A+B-C 的 Cost 项。

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
    anchor = _build_anchor(report, matched_field)
    return ExtractedField(
        value=matched_field.value,
        anchors=(_build_child_anchor(anchor, source_field_path),),
        extraction_mode="direct",
        note=None,
    )


def _build_basic_identity(
    report: ParsedAnnualReport,
    classification: FundTypeClassification,
) -> ExtractedField[dict[str, object]]:
    """构造基础身份信息字段。

    Args:
        report: 已解析年报对象。
        classification: 已完成的基金类型识别结果。

    Returns:
        带证据的基础身份信息字段。

    Raises:
        无显式抛出。
    """

    matched_fields = [
        _extract_field(report, "fund_name"),
        _extract_field(report, "fund_code"),
        _extract_field(report, "fund_category"),
        _extract_field(report, "fund_scale"),
        _extract_field(report, "fund_manager"),
        _extract_field(report, "management_company"),
        _extract_field(report, "custodian"),
        _extract_field(report, "inception_date"),
    ]
    value = {
        "fund_name": matched_fields[0].value if matched_fields[0] else None,
        "fund_code": matched_fields[1].value if matched_fields[1] else report.key.fund_code,
        "fund_category": matched_fields[2].value if matched_fields[2] else None,
        "fund_scale": matched_fields[3].value if matched_fields[3] else None,
        "fund_manager": matched_fields[4].value if matched_fields[4] else None,
        "management_company": matched_fields[5].value if matched_fields[5] else None,
        "custodian": matched_fields[6].value if matched_fields[6] else None,
        "inception_date": matched_fields[7].value if matched_fields[7] else None,
        "classified_fund_type": classification.classified_fund_type,
        "classification_basis": classification.classification_basis,
    }
    anchors = tuple(
        _build_anchor(report, matched_field)
        for matched_field in matched_fields
        if matched_field is not None
    )
    return ExtractedField(
        value=value,
        anchors=anchors,
        extraction_mode="direct",
        note=None,
    )


def _build_product_profile(report: ParsedAnnualReport) -> ExtractedField[dict[str, object]]:
    """构造产品本质字段，见模板第 1 章“这只基金到底是什么产品”。

    Args:
        report: 已解析年报对象。

    Returns:
        带证据的产品本质字段。

    Raises:
        无显式抛出。
    """

    objective = _extract_field(report, "investment_objective")
    scope = _extract_field(report, "investment_scope")
    strategy = _extract_field(report, "investment_strategy")
    explicit_style = _extract_field(report, "style_positioning")
    style_positioning = (
        explicit_style.value if explicit_style else _derive_style_positioning(objective)
    )
    anchors = tuple(
        _build_anchor(report, matched_field)
        for matched_field in (objective, scope, strategy, explicit_style)
        if matched_field is not None
    )
    if not anchors:
        return _missing_field("§2 未披露投资目标/范围/策略")
    return ExtractedField(
        value={
            "investment_objective": objective.value if objective else None,
            "style_positioning": style_positioning,
            "investment_scope": scope.value if scope else None,
            "investment_strategy": strategy.value if strategy else None,
        },
        anchors=anchors,
        extraction_mode="direct",
        note=None,
    )


def _anchor_to_source_anchor(anchor: EvidenceAnchor) -> dict[str, object]:
    """把通用证据锚点投影为 `risk_characteristic_text.v1` 值内来源锚点。

    Args:
        anchor: 通用年报证据锚点。

    Returns:
        可序列化的来源锚点字典。

    Raises:
        无显式抛出。
    """

    return {
        "section_id": anchor.section_id,
        "page_number": anchor.page_number,
        "table_id": anchor.table_id,
        "row_locator": anchor.row_locator,
    }


def _build_risk_characteristic_text(report: ParsedAnnualReport) -> ExtractedField[dict[str, object]]:
    """构造 `risk_characteristic_text.v1` 风险收益特征字段。

    该字段只读取 `§2` 中显式标注的风险收益特征文本，见模板第 1 章产品本质和第 6 章核心风险；
    不从基金名称、基金类型或 `product_profile.style_positioning` 间接推断。

    Args:
        report: 已解析年报对象。

    Returns:
        带 `risk_characteristic_text.v1` 结构化值的抽取字段；缺少显式风险收益特征时返回 missing。

    Raises:
        无显式抛出。
    """

    matched_field = _extract_field(report, "risk_characteristic_text")
    if matched_field is None:
        return _missing_field("§2 未披露风险收益特征")
    anchor = _build_anchor(report, matched_field)
    return ExtractedField(
        value={
            "schema_version": _RISK_CHARACTERISTIC_SCHEMA_VERSION,
            "fund_code": report.key.fund_code,
            "report_year": report.key.year,
            "risk_characteristic_text": matched_field.value,
            "source_anchors": [_anchor_to_source_anchor(anchor)],
        },
        anchors=(anchor,),
        extraction_mode="direct",
        note=None,
    )


def _derive_style_positioning(objective: _MatchedField | None) -> str | None:
    """从投资目标中提炼产品定位短语。

    Args:
        objective: `§2` 投资目标命中结果。

    Returns:
        可作为 `product_profile.style_positioning` 的定位短语；无法可靠提炼时返回 `None`。

    Raises:
        无显式抛出。
    """

    if objective is None:
        return None
    normalized_value = re.sub(r"\s+", " ", objective.value).strip()
    patterns: tuple[re.Pattern[str], ...] = (
        re.compile(r"(?:力争实现|追求实现|争取实现|实现)(?P<style>.+)$"),
        re.compile(r"(?:追求|力求获得|力求取得)(?P<style>.+)$"),
    )
    for pattern in patterns:
        match = pattern.search(normalized_value)
        if match is None:
            continue
        style_text = match.group("style").strip()
        style_text = re.sub(r"^基金\s*", "", style_text)
        return style_text or None
    return None


def _build_benchmark(report: ParsedAnnualReport) -> ExtractedField[dict[str, object]]:
    """构造业绩比较基准字段。

    Args:
        report: 已解析年报对象。

    Returns:
        带证据的业绩比较基准字段。

    Raises:
        无显式抛出。
    """

    matched_field = _extract_field(report, "benchmark")
    if matched_field is None:
        return _missing_field("§2 未披露业绩比较基准")
    matched_field = _normalize_benchmark_matched_field(matched_field)
    return ExtractedField(
        value={"benchmark_text": matched_field.value},
        anchors=(_build_anchor(report, matched_field),),
        extraction_mode="direct",
        note=None,
    )


def _build_fee_schedule(
    report: ParsedAnnualReport,
) -> tuple[ExtractedField[dict[str, object]], ExtractedField[object], ExtractedField[object]]:
    """构造费率复合字段与子字段。

    Args:
        report: 已解析年报对象。

    Returns:
        费率兼容复合字段、管理费子字段、托管费子字段。

    Raises:
        无显式抛出。
    """

    management_fee = _extract_field(report, "management_fee")
    custody_fee = _extract_field(report, "custody_fee")
    if management_fee is None:
        management_fee = _extract_fee_from_fallback_subsection(report, "management_fee")
    if custody_fee is None:
        custody_fee = _extract_fee_from_fallback_subsection(report, "custody_fee")
    management_fee_field = _build_child_field(
        report,
        management_fee,
        _FEE_SCHEDULE_MANAGEMENT_FEE_PATH,
        "§2 与 7.4.10.2 均未披露管理费",
    )
    custody_fee_field = _build_child_field(
        report,
        custody_fee,
        _FEE_SCHEDULE_CUSTODY_FEE_PATH,
        "§2 与 7.4.10.2 均未披露托管费",
    )
    anchors = tuple(
        _build_anchor(report, matched_field)
        for matched_field in (management_fee, custody_fee)
        if matched_field is not None
    )
    if not anchors:
        return (
            _missing_field("§2 与 7.4.10.2 均未披露管理费/托管费"),
            management_fee_field,
            custody_fee_field,
        )
    return (
        ExtractedField(
            value={
                "management_fee": management_fee_field.value,
                "custody_fee": custody_fee_field.value,
            },
            anchors=anchors,
            extraction_mode="direct",
            note=None,
        ),
        management_fee_field,
        custody_fee_field,
    )


def _build_index_profile(
    classification: FundTypeClassification,
    benchmark: ExtractedField[dict[str, object]],
) -> ExtractedField[IndexProfileValue]:
    """构造指数画像字段，见模板第 1 章指数编制规则与成分股。

    Args:
        classification: 已完成的基金类型识别结果。
        benchmark: 业绩比较基准字段。

    Returns:
        指数画像字段；非指数基金返回 `missing`。

    Raises:
        无显式抛出。
    """

    fund_type = classification.classified_fund_type
    if fund_type not in _INDEX_APPLICABLE_FUND_TYPES:
        return ExtractedField(
            value=None,
            anchors=(),
            extraction_mode="missing",
            note="非指数基金不适用指数画像",
        )
    benchmark_text = _benchmark_text(benchmark)
    if benchmark_text is None:
        return ExtractedField(
            value=IndexProfileValue(
                benchmark_text=None,
                benchmark_identity_status="missing",
                benchmark_index_name=None,
                benchmark_index_code=None,
                benchmark_component_text=(),
                methodology_availability="missing",
                methodology_summary=None,
                methodology_source_title=None,
                constituents_availability="missing",
                constituents_summary=None,
                constituents_as_of_date=None,
                source_tier="missing",
                missing_reasons=("benchmark_missing",),
            ),
            anchors=(),
            extraction_mode="missing",
            note="指数基金未披露业绩比较基准，无法形成指数画像",
        )
    components = _benchmark_components(benchmark_text)
    identity_status = _benchmark_identity_status(benchmark_text, components)
    index_name = _benchmark_index_name(benchmark_text, identity_status)
    return ExtractedField(
        value=IndexProfileValue(
            benchmark_text=benchmark_text,
            benchmark_identity_status=identity_status,
            benchmark_index_name=index_name,
            benchmark_index_code=None,
            benchmark_component_text=components,
            methodology_availability="benchmark_only",
            methodology_summary=None,
            methodology_source_title=None,
            constituents_availability="benchmark_only",
            constituents_summary=None,
            constituents_as_of_date=None,
            source_tier="benchmark_context",
            missing_reasons=("methodology_not_directly_disclosed", "constituents_not_directly_disclosed"),
        ),
        anchors=benchmark.anchors,
        extraction_mode="direct",
        note="仅业绩比较基准上下文；不得作为指数编制方法或成分股证据。",
    )


def _benchmark_text(benchmark: ExtractedField[dict[str, object]]) -> str | None:
    """读取业绩比较基准文本。

    Args:
        benchmark: 业绩比较基准字段。

    Returns:
        非空基准文本；缺失时返回 `None`。

    Raises:
        无显式抛出。
    """

    if benchmark.value is None:
        return None
    value = benchmark.value.get("benchmark_text") or benchmark.value.get("benchmark")
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _benchmark_components(benchmark_text: str) -> tuple[str, ...]:
    """拆分复合业绩比较基准文本。

    Args:
        benchmark_text: 年报披露的业绩比较基准。

    Returns:
        基准组成文本；非复合时返回空元组。

    Raises:
        无显式抛出。
    """

    if not any(separator in benchmark_text for separator in _COMPOSITE_BENCHMARK_SEPARATORS):
        return ()
    components = tuple(
        part.strip()
        for part in re.split(r"[＋+×*]|和|及", benchmark_text)
        if part.strip()
    )
    return components or (benchmark_text,)


def _benchmark_identity_status(
    benchmark_text: str,
    components: tuple[str, ...],
) -> Literal["identified", "composite", "ambiguous", "missing"]:
    """判断基准身份状态。

    Args:
        benchmark_text: 年报披露的业绩比较基准。
        components: 复合基准组成文本。

    Returns:
        `identified`、`composite`、`ambiguous` 或 `missing`。

    Raises:
        无显式抛出。
    """

    if not benchmark_text.strip():
        return "missing"
    if len(components) > 1 or (
        components and any(keyword in benchmark_text for keyword in ("存款", "债券", "中债"))
    ):
        return "composite"
    if "或" in benchmark_text:
        return "ambiguous"
    return "identified"


def _benchmark_index_name(
    benchmark_text: str,
    identity_status: Literal["identified", "composite", "ambiguous", "missing"],
) -> str | None:
    """从基准文本中提取可确定的指数名称。

    Args:
        benchmark_text: 年报披露的业绩比较基准。
        identity_status: 基准身份状态。

    Returns:
        单一可确定指数名称；复合或模糊时返回 `None`。

    Raises:
        无显式抛出。
    """

    if identity_status != "identified":
        return None
    match = _INDEX_NAME_PATTERN.search(benchmark_text)
    if match is None:
        return None
    return match.group("name")


def extract_profile(report: ParsedAnnualReport) -> ProfileExtractionResult:
    """抽取基础画像与基金类型识别结果。

    Args:
        report: 已解析年报对象。

    Returns:
        `basic_identity`、`product_profile`、`benchmark`、`fee_schedule` 四类结果。

    Raises:
        无显式抛出。
    """

    classification = classify_fund_type(report)
    benchmark = _build_benchmark(report)
    basic_identity = _build_basic_identity(report, classification)
    product_profile = _build_product_profile(report)
    risk_characteristic_text = _build_risk_characteristic_text(report)
    index_profile = _build_index_profile(classification, benchmark)
    fee_schedule, management_fee, custody_fee = _build_fee_schedule(report)
    return ProfileExtractionResult(
        basic_identity=basic_identity,
        product_profile=product_profile,
        risk_characteristic_text=risk_characteristic_text,
        benchmark=benchmark,
        index_profile=index_profile,
        fee_schedule=fee_schedule,
        fee_schedule_management_fee=management_fee,
        fee_schedule_custody_fee=custody_fee,
    )
