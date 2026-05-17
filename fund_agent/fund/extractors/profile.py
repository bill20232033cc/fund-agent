"""基础画像与 §1/§2 信息抽取。"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Final

from fund_agent.fund.documents.models import ParsedAnnualReport
from fund_agent.fund.extractors.models import EvidenceAnchor, ExtractedField, ProfileExtractionResult
from fund_agent.fund.fund_type import FundTypeClassification, classify_fund_type

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
    "investment_objective": (
        ("§2", (r"投资目标\s*[：:]\s*(.+)",)),
    ),
    "investment_scope": (
        ("§2", (r"投资范围\s*[：:]\s*(.+)",)),
    ),
    "investment_strategy": (
        ("§2", (r"投资策略\s*[：:]\s*(.+)",)),
    ),
    "benchmark": (
        ("§2", (r"业绩比较基准\s*[：:]\s*(.+)",)),
    ),
    "management_fee": (
        ("§2", (r"管理费(?:率)?\s*[：:]\s*(.+)",)),
    ),
    "custody_fee": (
        ("§2", (r"托管费(?:率)?\s*[：:]\s*(.+)",)),
    ),
}


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
    return None


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
        page_number=None,
        table_id=None,
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
    """构造产品本质字段。

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
    anchors = tuple(
        _build_anchor(report, matched_field)
        for matched_field in (objective, scope, strategy)
        if matched_field is not None
    )
    if not anchors:
        return _missing_field("§2 未披露投资目标/范围/策略")
    return ExtractedField(
        value={
            "investment_objective": objective.value if objective else None,
            "investment_scope": scope.value if scope else None,
            "investment_strategy": strategy.value if strategy else None,
        },
        anchors=anchors,
        extraction_mode="direct",
        note=None,
    )


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
    return ProfileExtractionResult(
        basic_identity=_build_basic_identity(report, classification),
        product_profile=_build_product_profile(report),
        benchmark=_build_benchmark(report),
        fee_schedule=_build_fee_schedule(report),
    )
