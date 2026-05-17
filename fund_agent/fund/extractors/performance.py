"""`§3` 净值表现与投资者收益率抽取。"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Final

from fund_agent.fund.documents.models import ParsedAnnualReport
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

    nav_growth_rate = _extract_field(report, "nav_growth_rate")
    benchmark_return_rate = _extract_field(report, "benchmark_return_rate")
    if nav_growth_rate is None and benchmark_return_rate is None:
        return _missing_field("§3 未披露净值增长率/业绩比较基准收益率")
    anchors = tuple(
        _build_anchor(report, matched_field)
        for matched_field in (nav_growth_rate, benchmark_return_rate)
        if matched_field is not None
    )
    extraction_mode = "direct" if nav_growth_rate is not None and benchmark_return_rate is not None else "missing"
    note = None
    if extraction_mode == "missing":
        note = "§3 仅部分披露净值增长率/业绩比较基准收益率；当前显式保留缺失状态。"
    return ExtractedField(
        value={
            "nav_growth_rate": nav_growth_rate.value if nav_growth_rate else None,
            "benchmark_return_rate": benchmark_return_rate.value if benchmark_return_rate else None,
        },
        anchors=anchors,
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
