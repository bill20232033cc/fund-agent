"""`§4/§8/§9` 管理人文本、换手率与持有人信息抽取。"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Final

from fund_agent.fund.documents.models import ParsedAnnualReport
from fund_agent.fund.extractors.models import (
    EvidenceAnchor,
    ExtractedField,
    ManagerOwnershipExtractionResult,
)

_SECTION_MANAGER_REPORT: Final[str] = "§4"
_SECTION_PORTFOLIO: Final[str] = "§8"
_SECTION_HOLDER: Final[str] = "§9"

_FIELD_PATTERNS: Final[dict[str, tuple[tuple[str, tuple[str, ...]], ...]]] = {
    "strategy_summary": (
        (_SECTION_MANAGER_REPORT, (r"投资策略\s*[：:]\s*(.+)", r"报告期内投资策略\s*[：:]\s*(.+)")),
    ),
    "style_positioning": (
        (_SECTION_MANAGER_REPORT, (r"风格定位\s*[：:]\s*(.+)", r"投资风格\s*[：:]\s*(.+)")),
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
    """

    field_name: str
    value: str
    section_id: str
    matched_line: str


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
    return ExtractedField(value=value, anchors=anchors, extraction_mode="direct", note=None)


def _build_manager_strategy_text(report: ParsedAnnualReport) -> ExtractedField[dict[str, object]]:
    """构造管理人策略文本字段，见模板第 3 章“投资策略与风格”。

    Args:
        report: 已解析年报对象。

    Returns:
        管理人报告中的策略、风格与后市展望原文。

    Raises:
        无显式抛出。
    """

    strategy_summary = _extract_field(report, "strategy_summary")
    style_positioning = _extract_field(report, "style_positioning")
    market_outlook = _extract_field(report, "market_outlook")
    return _build_field_from_matches(
        report=report,
        matched_fields=(strategy_summary, style_positioning, market_outlook),
        value={
            "strategy_summary": strategy_summary.value if strategy_summary else None,
            "style_positioning": style_positioning.value if style_positioning else None,
            "market_outlook": market_outlook.value if market_outlook else None,
        },
        missing_note="§4 未披露可规则化抽取的投资策略/风格/后市展望",
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
