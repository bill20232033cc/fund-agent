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
    "investment_objective": ("投资目标",),
    "investment_scope": ("投资范围",),
    "investment_strategy": ("投资策略",),
    "style_positioning": ("风格定位", "风险收益特征", "产品定位"),
    "benchmark": ("业绩比较基准",),
    "management_fee": ("管理费率", "管理费"),
    "custody_fee": ("托管费率", "托管费"),
}
_SECTION_TWO_TABLE_MIN_PAGE: Final[int] = 1
_INDEX_APPLICABLE_FUND_TYPES: Final[frozenset[FundType]] = frozenset(
    ("index_fund", "enhanced_index")
)
_COMPOSITE_BENCHMARK_SEPARATORS: Final[tuple[str, ...]] = ("＋", "+", "×", "*", "和", "及")
_INDEX_NAME_PATTERN: Final[re.Pattern[str]] = re.compile(
    r"(?P<name>[\u4e00-\u9fa5A-Za-z0-9]+(?:指数|Index|ETF))"
)


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
    ]
    value = {
        "fund_name": matched_fields[0].value if matched_fields[0] else None,
        "fund_code": matched_fields[1].value if matched_fields[1] else report.key.fund_code,
        "fund_category": matched_fields[2].value if matched_fields[2] else None,
        "fund_scale": matched_fields[3].value if matched_fields[3] else None,
        "fund_manager": matched_fields[4].value if matched_fields[4] else None,
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
    return ExtractedField(
        value={"benchmark_text": matched_field.value},
        anchors=(_build_anchor(report, matched_field),),
        extraction_mode="direct",
        note=None,
    )


def _build_fee_schedule(report: ParsedAnnualReport) -> ExtractedField[dict[str, object]]:
    """构造费率字段。

    Args:
        report: 已解析年报对象。

    Returns:
        带证据的费率字段。

    Raises:
        无显式抛出。
    """

    management_fee = _extract_field(report, "management_fee")
    custody_fee = _extract_field(report, "custody_fee")
    anchors = tuple(
        _build_anchor(report, matched_field)
        for matched_field in (management_fee, custody_fee)
        if matched_field is not None
    )
    if not anchors:
        return _missing_field("§2 未披露管理费/托管费")
    return ExtractedField(
        value={
            "management_fee": management_fee.value if management_fee else None,
            "custody_fee": custody_fee.value if custody_fee else None,
        },
        anchors=anchors,
        extraction_mode="direct",
        note=None,
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
    return ProfileExtractionResult(
        basic_identity=_build_basic_identity(report, classification),
        product_profile=_build_product_profile(report),
        benchmark=benchmark,
        index_profile=_build_index_profile(classification, benchmark),
        fee_schedule=_build_fee_schedule(report),
    )
