"""债券风险证据抽取器。

本模块只从已经加载完成的 ``ParsedAnnualReport`` 中抽取模板第 6 章“核心风险”
所需的 ``bond_risk_evidence.v1`` 七组证据，不访问文档仓库、PDF 缓存或来源 helper。
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Final

from fund_agent.fund.documents.models import ParsedAnnualReport, ParsedTable
from fund_agent.fund.extractors.models import (
    BOND_RISK_EVIDENCE_CONTRACT_ID,
    BOND_RISK_EVIDENCE_GROUP_IDS,
    BondRiskEvidenceAnchorRef,
    BondRiskEvidenceGroupId,
    BondRiskEvidenceGroupRecord,
    BondRiskEvidenceMeasurementKind,
    BondRiskEvidenceStatus,
    BondRiskEvidenceStrength,
    BondRiskEvidenceValue,
    EvidenceAnchor,
    ExtractedField,
    validate_bond_risk_evidence_value,
)

_BOND_FUND_TYPE: Final[str] = "bond_fund"
_SECTION_PROFILE: Final[str] = "§2"
_SECTION_MANAGER: Final[str] = "§4"
_SECTION_PORTFOLIO: Final[str] = "§8"
_SECTION_HOLDER: Final[str] = "§9"
_SECTION_SHARE_CHANGE: Final[str] = "§10"
_SECTION_RISK_DISCLOSURE: Final[str] = "§5"
_NOT_APPLICABLE_NOTE: Final[str] = "not_applicable_non_bond_fund"
_MISSING_NOTE: Final[str] = "bond_risk_evidence_missing"
_MAX_TEXT_ANCHOR_LENGTH: Final[int] = 120
_SHARE_CLASS_LABELS: Final[tuple[str, ...]] = tuple("ABCDEFGHIJKLMNOPQRSTUVWXYZ")


@dataclass(frozen=True, slots=True)
class _GroupExtraction:
    """模板第 6 章单组抽取结果。

    Attributes:
        record: 单组风险证据记录。
        anchors: 与记录对应的 extractor 层年报锚点。
        anchor_refs: 与记录对应的稳定组级锚点引用。
    """

    record: BondRiskEvidenceGroupRecord
    anchors: tuple[EvidenceAnchor, ...]
    anchor_refs: tuple[BondRiskEvidenceAnchorRef, ...]


@dataclass(frozen=True, slots=True)
class _AnchorDraft:
    """模板第 6 章组级锚点草稿。

    Attributes:
        group_id: 风险组 ID。
        section_id: 年报章节编号。
        page_number: 年报页码。
        table_id: 表格 ID。
        row_locator: 行级或段落级定位。
        evidence_role: 证据角色。
        note: extractor 层锚点备注。
    """

    group_id: BondRiskEvidenceGroupId
    section_id: str
    page_number: int | None
    table_id: str | None
    row_locator: str
    evidence_role: str
    note: str


@dataclass(frozen=True, slots=True)
class _TextMatch:
    """模板第 6 章文本证据命中。

    Attributes:
        section_id: 命中章节。
        line_index: 章节内行号。
        line_text: 命中行文本。
    """

    section_id: str
    line_index: int
    line_text: str


@dataclass(frozen=True, slots=True)
class _ShareClassEvidence:
    """模板第 6 章赎回压力组的份额类别消歧证据。

    Attributes:
        class_label: 当前基金代码对应的份额类别。
        source_note: 证据来源说明。
    """

    class_label: str
    source_note: str


def extract_bond_risk_evidence(
    report: ParsedAnnualReport,
    classified_fund_type: str | None,
) -> ExtractedField[BondRiskEvidenceValue]:
    """抽取模板第 6 章债券风险证据。

    Args:
        report: 已通过统一文档仓库加载并解析的年报。
        classified_fund_type: 上游显式基金类型；只有精确 ``bond_fund`` 才执行七组扫描。

    Returns:
        债券基金返回带 ``BondRiskEvidenceValue`` 的字段；非债券或未知类型返回不适用缺失字段。

    Raises:
        ValueError: 当内部构造出的 ``bond_risk_evidence.v1`` 与模型契约不一致时抛出。
    """

    if classified_fund_type != _BOND_FUND_TYPE:
        return ExtractedField(
            value=None,
            anchors=(),
            extraction_mode="missing",
            note=_NOT_APPLICABLE_NOTE,
        )

    extractions = (
        _extract_duration_rate_risk(report),
        _extract_credit_risk(report),
        _extract_leverage_liquidity(report),
        _extract_asset_allocation_holdings_mix(report),
        _extract_drawdown_stress(report),
        _extract_redemption_share_pressure(report),
        _extract_convertible_bond_equity_exposure(report),
    )
    value = _build_value(report, extractions)
    validate_bond_risk_evidence_value(value)

    return ExtractedField(
        value=value,
        anchors=tuple(anchor for extraction in extractions for anchor in extraction.anchors),
        extraction_mode=_extraction_mode(value),
        note=_field_note(value),
    )


def _extract_duration_rate_risk(report: ParsedAnnualReport) -> _GroupExtraction:
    """抽取模板第 6 章久期和利率风险证据。

    Args:
        report: 已解析年报。

    Returns:
        久期/利率风险组抽取结果。

    Raises:
        无显式抛出。
    """

    group_id: BondRiskEvidenceGroupId = "duration_rate_risk"
    match = _find_text_match(
        report,
        section_ids=(_SECTION_PROFILE, _SECTION_MANAGER, _SECTION_RISK_DISCLOSURE),
        keyword_groups=(("久期",), ("利率风险", "管理"), ("利率风险", "控制"), ("利率风险", "调整")),
    )
    if match is None:
        return _missing_group(group_id, "年报未定位到久期或利率风险披露")
    draft = _text_anchor_draft(group_id, match, "duration_or_rate_risk_disclosure")
    return _anchored_group(
        report,
        group_id=group_id,
        status="accepted",
        strength="qualitative_direct",
        summary="年报披露久期或利率风险管理信息",
        measurement_kind="risk_disclosure",
        drafts=(draft,),
    )


def _extract_credit_risk(report: ParsedAnnualReport) -> _GroupExtraction:
    """抽取模板第 6 章信用风险证据。

    Args:
        report: 已解析年报。

    Returns:
        信用风险组抽取结果。

    Raises:
        无显式抛出。
    """

    group_id: BondRiskEvidenceGroupId = "credit_risk"
    table_draft = _first_row_anchor_draft(
        report.tables,
        group_id=group_id,
        section_id=_SECTION_PORTFOLIO,
        table_keywords=("信用", "评级"),
        row_keywords=("信用", "评级"),
        evidence_role="credit_rating_distribution",
    )
    if table_draft is not None:
        return _anchored_group(
            report,
            group_id=group_id,
            status="accepted",
            strength="quantitative_direct",
            summary="年报表格披露信用评级或信用风险暴露",
            measurement_kind="actual_exposure",
            metric_name="信用风险暴露",
            metric_value=table_draft.note,
            drafts=(table_draft,),
        )

    text_match = _find_text_match(
        report,
        section_ids=(_SECTION_PROFILE, _SECTION_MANAGER, _SECTION_RISK_DISCLOSURE),
        keyword_groups=(("信用风险",), ("中高等级",), ("信用债",)),
    )
    if text_match is not None:
        return _anchored_group(
            report,
            group_id=group_id,
            status="weak",
            strength="qualitative_direct",
            summary="年报仅定位到信用策略或信用风险控制文本",
            measurement_kind="risk_disclosure",
            drafts=(_text_anchor_draft(group_id, text_match, "credit_risk_text"),),
            na_reason="credit_risk_table_not_found",
        )
    return _missing_group(group_id, "年报未定位到信用风险表格或披露文本")


def _extract_leverage_liquidity(report: ParsedAnnualReport) -> _GroupExtraction:
    """抽取模板第 6 章杠杆和流动性风险证据。

    Args:
        report: 已解析年报。

    Returns:
        杠杆/流动性风险组抽取结果。

    Raises:
        无显式抛出。
    """

    group_id: BondRiskEvidenceGroupId = "leverage_liquidity"
    repo_draft = _first_row_anchor_draft(
        report.tables,
        group_id=group_id,
        section_id=_SECTION_PORTFOLIO,
        table_keywords=("回购",),
        row_keywords=("回购",),
        evidence_role="repo_or_financing_exposure",
    )
    liquidity_match = _find_text_match(
        report,
        section_ids=(_SECTION_MANAGER, _SECTION_RISK_DISCLOSURE),
        keyword_groups=(("流动性风险",),),
    )
    if repo_draft is not None:
        drafts = (repo_draft,)
        if liquidity_match is not None:
            drafts = (
                repo_draft,
                _text_anchor_draft(group_id, liquidity_match, "liquidity_risk_disclosure"),
            )
        return _anchored_group(
            report,
            group_id=group_id,
            status="accepted",
            strength="quantitative_direct",
            summary="年报披露回购/融资表格行，且可与流动性风险披露共同定位",
            measurement_kind="actual_exposure",
            metric_name="回购或融资暴露",
            metric_value=repo_draft.note,
            drafts=drafts,
        )

    leverage_match = _find_text_match(
        report,
        section_ids=(_SECTION_MANAGER, _SECTION_RISK_DISCLOSURE),
        keyword_groups=(("杠杆策略",), ("杠杆",)),
    )
    support_match = leverage_match or liquidity_match
    if support_match is not None:
        return _anchored_group(
            report,
            group_id=group_id,
            status="weak",
            strength="qualitative_direct",
            summary="年报仅披露杠杆策略或流动性风险控制文本",
            measurement_kind="strategy_text",
            drafts=(_text_anchor_draft(group_id, support_match, "leverage_or_liquidity_text"),),
            na_reason="repo_or_liquidity_table_not_found",
        )
    return _missing_group(group_id, "年报未定位到杠杆、回购或流动性风险证据")


def _extract_asset_allocation_holdings_mix(report: ParsedAnnualReport) -> _GroupExtraction:
    """抽取模板第 6 章资产配置和持仓结构证据。

    Args:
        report: 已解析年报。

    Returns:
        资产配置/持仓结构组抽取结果。

    Raises:
        无显式抛出。
    """

    group_id: BondRiskEvidenceGroupId = "asset_allocation_holdings_mix"
    draft = _first_row_anchor_draft(
        report.tables,
        group_id=group_id,
        section_id=_SECTION_PORTFOLIO,
        table_keywords=("债券",),
        row_keywords=("债券",),
        evidence_role="bond_allocation_or_mix",
    )
    if draft is not None:
        return _anchored_group(
            report,
            group_id=group_id,
            status="accepted",
            strength="quantitative_direct",
            summary="年报表格披露债券资产配置或持仓结构",
            measurement_kind="actual_exposure",
            metric_name="债券配置",
            metric_value=draft.note,
            drafts=(draft,),
        )
    return _missing_group(group_id, "年报未定位到债券资产配置或持仓结构表格")


def _extract_drawdown_stress(report: ParsedAnnualReport) -> _GroupExtraction:
    """抽取模板第 6 章回撤和压力证据。

    Args:
        report: 已解析年报。

    Returns:
        回撤/压力组抽取结果。

    Raises:
        无显式抛出。
    """

    group_id: BondRiskEvidenceGroupId = "drawdown_stress"
    metric_draft = _first_row_anchor_draft(
        report.tables,
        group_id=group_id,
        section_id=_SECTION_MANAGER,
        table_keywords=("回撤",),
        row_keywords=("最大回撤",),
        evidence_role="max_drawdown_metric",
    )
    if metric_draft is not None:
        return _anchored_group(
            report,
            group_id=group_id,
            status="accepted",
            strength="quantitative_direct",
            summary="年报表格披露最大回撤指标",
            measurement_kind="actual_metric",
            metric_name="最大回撤",
            metric_value=metric_draft.note,
            drafts=(metric_draft,),
        )

    control_match = _find_text_match(
        report,
        section_ids=(_SECTION_MANAGER, _SECTION_RISK_DISCLOSURE),
        keyword_groups=(("控制回撤",), ("回撤",)),
    )
    if control_match is not None:
        return _anchored_group(
            report,
            group_id=group_id,
            status="weak",
            strength="qualitative_control_intent",
            summary="年报仅披露回撤控制意图，不能等同于最大回撤或波动率指标",
            measurement_kind="control_intent",
            drafts=(_text_anchor_draft(group_id, control_match, "drawdown_control_intent"),),
            na_reason="drawdown_metric_not_found",
        )
    return _missing_group(group_id, "年报未定位到回撤指标或回撤控制文本")


def _extract_redemption_share_pressure(report: ParsedAnnualReport) -> _GroupExtraction:
    """抽取模板第 6 章赎回和份额压力证据。

    Args:
        report: 已解析年报。

    Returns:
        赎回/份额压力组抽取结果。

    Raises:
        无显式抛出。
    """

    group_id: BondRiskEvidenceGroupId = "redemption_share_pressure"
    share_table = _find_share_change_table(report.tables)
    if share_table is None:
        return _missing_group(group_id, "年报未定位到基金份额变动表")

    selection = _select_share_change_column(
        share_table,
        fund_code=report.key.fund_code,
        share_class_evidence=_share_class_evidence(report),
    )
    if selection is None:
        return _plain_group(
            group_id=group_id,
            status="ambiguous",
            strength="ambiguous",
            summary="份额变动表存在多份额类别但无法明确选择当前基金代码对应列",
            measurement_kind="actual_exposure",
            na_reason="ambiguous_share_class_selection",
        )

    roles = (
        ("share_beginning", ("期初",)),
        ("subscription", ("申购",)),
        ("redemption", ("赎回",)),
        ("share_ending", ("期末",)),
    )
    drafts = tuple(
        draft
        for draft in (
            _row_anchor_draft(
                share_table,
                group_id=group_id,
                section_id=_SECTION_SHARE_CHANGE,
                row_keywords=keywords,
                evidence_role=role,
                value_column_index=selection,
            )
            for role, keywords in roles
        )
        if draft is not None
    )
    if len(drafts) < len(roles):
        return _plain_group(
            group_id=group_id,
            status="ambiguous",
            strength="ambiguous",
            summary="份额变动表缺少期初、申购、赎回或期末的完整行级定位",
            measurement_kind="actual_exposure",
            na_reason="incomplete_share_change_rows",
        )
    return _anchored_group(
        report,
        group_id=group_id,
        status="accepted",
        strength="quantitative_direct",
        summary="年报份额变动表可明确选择当前基金份额类别并定位申购赎回数据",
        measurement_kind="actual_exposure",
        metric_name="份额变动",
        metric_value="; ".join(draft.note for draft in drafts),
        drafts=drafts,
    )


def _extract_convertible_bond_equity_exposure(report: ParsedAnnualReport) -> _GroupExtraction:
    """抽取模板第 6 章可转债与权益暴露显式缺席证据。

    Args:
        report: 已解析年报。

    Returns:
        可转债/权益暴露组抽取结果。

    Raises:
        无显式抛出。
    """

    group_id: BondRiskEvidenceGroupId = "convertible_bond_equity_exposure"
    equity_draft = _absence_row_anchor_draft(
        report.tables,
        group_id=group_id,
        section_id=_SECTION_PORTFOLIO,
        row_keywords=("股票",),
        evidence_role="equity_absence",
    )
    convertible_draft = _absence_row_anchor_draft(
        report.tables,
        group_id=group_id,
        section_id=_SECTION_PORTFOLIO,
        row_keywords=("可转债",),
        evidence_role="convertible_bond_absence",
    )
    drafts = tuple(draft for draft in (equity_draft, convertible_draft) if draft is not None)
    if drafts:
        return _anchored_group(
            report,
            group_id=group_id,
            status="accepted_absence",
            strength="quantitative_absence",
            summary="年报表格以 '-' 或零值明确披露权益/可转债暴露缺席",
            measurement_kind="explicit_absence",
            metric_name="权益或可转债暴露",
            metric_value="; ".join(draft.note for draft in drafts),
            drafts=drafts,
        )
    return _missing_group(group_id, "年报未定位到权益或可转债显式缺席表格行")


def _build_value(report: ParsedAnnualReport, extractions: tuple[_GroupExtraction, ...]) -> BondRiskEvidenceValue:
    """构造模板第 6 章债券风险证据契约值。

    Args:
        report: 已解析年报。
        extractions: 七组抽取结果。

    Returns:
        可通过模型校验的 ``BondRiskEvidenceValue``。

    Raises:
        无显式抛出；契约不一致由调用方 validator 抛出。
    """

    groups = tuple(extraction.record for extraction in extractions)
    anchor_refs = tuple(anchor_ref for extraction in extractions for anchor_ref in extraction.anchor_refs)
    satisfied_ids = tuple(group.group_id for group in groups if group.status in {"accepted", "accepted_absence"})
    missing_ids = tuple(group.group_id for group in groups if group.status == "missing")
    weak_ids = tuple(group.group_id for group in groups if group.status == "weak")
    ambiguous_ids = tuple(group.group_id for group in groups if group.status == "ambiguous")
    if len(satisfied_ids) == len(BOND_RISK_EVIDENCE_GROUP_IDS):
        contract_status = "satisfied"
    elif satisfied_ids or weak_ids or ambiguous_ids:
        contract_status = "partial"
    else:
        contract_status = "missing"
    return BondRiskEvidenceValue(
        schema_version=BOND_RISK_EVIDENCE_CONTRACT_ID,
        contract_id=BOND_RISK_EVIDENCE_CONTRACT_ID,
        fund_code=report.key.fund_code,
        report_year=report.key.year,
        groups=groups,
        anchors=anchor_refs,
        satisfied_group_ids=satisfied_ids,
        missing_group_ids=missing_ids,
        weak_group_ids=weak_ids,
        ambiguous_group_ids=ambiguous_ids,
        contract_status=contract_status,
    )


def _anchored_group(
    report: ParsedAnnualReport,
    *,
    group_id: BondRiskEvidenceGroupId,
    status: BondRiskEvidenceStatus,
    strength: BondRiskEvidenceStrength,
    summary: str,
    measurement_kind: BondRiskEvidenceMeasurementKind,
    drafts: tuple[_AnchorDraft, ...],
    metric_name: str | None = None,
    metric_value: str | None = None,
    na_reason: str | None = None,
) -> _GroupExtraction:
    """构造带锚点的模板第 6 章风险组记录。

    Args:
        report: 已解析年报。
        group_id: 风险组 ID。
        status: 证据状态。
        strength: 证据强度。
        summary: 证据摘要。
        measurement_kind: 证据类型。
        drafts: 组级锚点草稿。
        metric_name: 指标名称。
        metric_value: 指标值原文。
        na_reason: 未满足原因。

    Returns:
        单组抽取结果。

    Raises:
        无显式抛出。
    """

    anchors, anchor_refs = _build_group_anchors(report, group_id, drafts)
    record = BondRiskEvidenceGroupRecord(
        group_id=group_id,
        status=status,
        strength=strength,
        summary=summary,
        measurement_kind=measurement_kind,
        metric_name=metric_name,
        metric_value=metric_value,
        metric_unit=None,
        period_label=f"{report.key.year} 年报",
        source_anchor_ids=tuple(anchor.anchor_id for anchor in anchor_refs),
        na_reason=na_reason,
        reviewer_note=None,
    )
    return _GroupExtraction(record=record, anchors=anchors, anchor_refs=anchor_refs)


def _missing_group(group_id: BondRiskEvidenceGroupId, reason: str) -> _GroupExtraction:
    """构造模板第 6 章缺失风险组记录。

    Args:
        group_id: 风险组 ID。
        reason: 缺失原因。

    Returns:
        缺失组抽取结果。

    Raises:
        无显式抛出。
    """

    return _plain_group(
        group_id=group_id,
        status="missing",
        strength="missing",
        summary=reason,
        measurement_kind="not_found",
        na_reason=reason,
    )


def _plain_group(
    *,
    group_id: BondRiskEvidenceGroupId,
    status: BondRiskEvidenceStatus,
    strength: BondRiskEvidenceStrength,
    summary: str,
    measurement_kind: BondRiskEvidenceMeasurementKind,
    na_reason: str | None,
) -> _GroupExtraction:
    """构造不带锚点的模板第 6 章风险组记录。

    Args:
        group_id: 风险组 ID。
        status: 证据状态。
        strength: 证据强度。
        summary: 证据摘要。
        measurement_kind: 证据类型。
        na_reason: 未满足原因。

    Returns:
        单组抽取结果。

    Raises:
        无显式抛出。
    """

    return _GroupExtraction(
        record=BondRiskEvidenceGroupRecord(
            group_id=group_id,
            status=status,
            strength=strength,
            summary=summary,
            measurement_kind=measurement_kind,
            metric_name=None,
            metric_value=None,
            metric_unit=None,
            period_label=None,
            source_anchor_ids=(),
            na_reason=na_reason,
            reviewer_note=None,
        ),
        anchors=(),
        anchor_refs=(),
    )


def _build_group_anchors(
    report: ParsedAnnualReport,
    group_id: BondRiskEvidenceGroupId,
    drafts: tuple[_AnchorDraft, ...],
) -> tuple[tuple[EvidenceAnchor, ...], tuple[BondRiskEvidenceAnchorRef, ...]]:
    """把模板第 6 章锚点草稿转换为稳定锚点。

    Args:
        report: 已解析年报。
        group_id: 风险组 ID。
        drafts: 锚点草稿。

    Returns:
        extractor 层锚点与组级锚点引用。

    Raises:
        无显式抛出。
    """

    sorted_drafts = sorted(
        drafts,
        key=lambda draft: (
            draft.section_id,
            draft.page_number if draft.page_number is not None else -1,
            draft.table_id or "",
            draft.row_locator,
            draft.evidence_role,
        ),
    )
    evidence_anchors: list[EvidenceAnchor] = []
    anchor_refs: list[BondRiskEvidenceAnchorRef] = []
    for ordinal, draft in enumerate(sorted_drafts, start=1):
        anchor_id = f"bond-risk:{report.key.fund_code}:{report.key.year}:{group_id}:{ordinal}"
        evidence_anchors.append(
            EvidenceAnchor(
                source_kind="annual_report",
                document_year=report.key.year,
                section_id=draft.section_id,
                page_number=draft.page_number,
                table_id=draft.table_id,
                row_locator=draft.row_locator,
                note=draft.note,
            )
        )
        anchor_refs.append(
            BondRiskEvidenceAnchorRef(
                anchor_id=anchor_id,
                section_id=draft.section_id,
                page_number=draft.page_number,
                table_id=draft.table_id,
                row_locator=draft.row_locator,
                evidence_role=draft.evidence_role,
            )
        )
    return tuple(evidence_anchors), tuple(anchor_refs)


def _text_anchor_draft(
    group_id: BondRiskEvidenceGroupId,
    match: _TextMatch,
    evidence_role: str,
) -> _AnchorDraft:
    """构造模板第 6 章文本锚点草稿。

    Args:
        group_id: 风险组 ID。
        match: 文本命中。
        evidence_role: 证据角色。

    Returns:
        文本锚点草稿。

    Raises:
        无显式抛出。
    """

    row_locator = f"line:{match.line_index}"
    note = _trim_note(match.line_text)
    return _AnchorDraft(
        group_id=group_id,
        section_id=match.section_id,
        page_number=None,
        table_id=None,
        row_locator=row_locator,
        evidence_role=evidence_role,
        note=note,
    )


def _first_row_anchor_draft(
    tables: tuple[ParsedTable, ...],
    *,
    group_id: BondRiskEvidenceGroupId,
    section_id: str,
    table_keywords: tuple[str, ...],
    row_keywords: tuple[str, ...],
    evidence_role: str,
) -> _AnchorDraft | None:
    """按表格和行关键词构造第一条模板第 6 章表格锚点草稿。

    Args:
        tables: 年报表格。
        group_id: 风险组 ID。
        section_id: 章节编号。
        table_keywords: 表格级关键词。
        row_keywords: 行级关键词。
        evidence_role: 证据角色。

    Returns:
        命中时返回锚点草稿，否则返回 ``None``。

    Raises:
        无显式抛出。
    """

    for table in tables:
        if not _table_contains_all(table, table_keywords):
            continue
        draft = _row_anchor_draft(
            table,
            group_id=group_id,
            section_id=section_id,
            row_keywords=row_keywords,
            evidence_role=evidence_role,
        )
        if draft is not None:
            return draft
    return None


def _row_anchor_draft(
    table: ParsedTable,
    *,
    group_id: BondRiskEvidenceGroupId,
    section_id: str,
    row_keywords: tuple[str, ...],
    evidence_role: str,
    value_column_index: int | None = None,
) -> _AnchorDraft | None:
    """构造模板第 6 章表格行锚点草稿。

    Args:
        table: 年报表格。
        group_id: 风险组 ID。
        section_id: 章节编号。
        row_keywords: 行级关键词。
        evidence_role: 证据角色。
        value_column_index: 需要记录的值列下标。

    Returns:
        命中时返回锚点草稿，否则返回 ``None``。

    Raises:
        无显式抛出。
    """

    for row_index, row in enumerate(table.rows, start=1):
        row_text = _compact_text(" ".join(row))
        if not all(keyword in row_text for keyword in row_keywords):
            continue
        row_label = _normalize_cell(row[0]) if row else f"row-{row_index}"
        row_locator = f"row:{row_index}:{row_label}"
        note = _format_row_note(row, value_column_index=value_column_index)
        return _AnchorDraft(
            group_id=group_id,
            section_id=section_id,
            page_number=table.page_number,
            table_id=_table_id(table),
            row_locator=row_locator,
            evidence_role=evidence_role,
            note=note,
        )
    return None


def _absence_row_anchor_draft(
    tables: tuple[ParsedTable, ...],
    *,
    group_id: BondRiskEvidenceGroupId,
    section_id: str,
    row_keywords: tuple[str, ...],
    evidence_role: str,
) -> _AnchorDraft | None:
    """构造模板第 6 章显式缺席表格行锚点草稿。

    Args:
        tables: 年报表格。
        group_id: 风险组 ID。
        section_id: 章节编号。
        row_keywords: 行级关键词。
        evidence_role: 证据角色。

    Returns:
        命中显式缺席行时返回锚点草稿，否则返回 ``None``。

    Raises:
        无显式抛出。
    """

    for table in tables:
        for row_index, row in enumerate(table.rows, start=1):
            row_text = _compact_text(" ".join(row))
            if not all(keyword in row_text for keyword in row_keywords):
                continue
            if not _row_has_absence_value(row):
                continue
            row_label = _normalize_cell(row[0]) if row else f"row-{row_index}"
            return _AnchorDraft(
                group_id=group_id,
                section_id=section_id,
                page_number=table.page_number,
                table_id=_table_id(table),
                row_locator=f"row:{row_index}:{row_label}",
                evidence_role=evidence_role,
                note=_format_row_note(row),
            )
    return None


def _find_text_match(
    report: ParsedAnnualReport,
    *,
    section_ids: tuple[str, ...],
    keyword_groups: tuple[tuple[str, ...], ...],
) -> _TextMatch | None:
    """查找模板第 6 章文本证据。

    Args:
        report: 已解析年报。
        section_ids: 候选章节。
        keyword_groups: 任一组全部关键词命中即可。

    Returns:
        第一条命中文本；未命中返回 ``None``。

    Raises:
        无显式抛出。
    """

    for section_id in section_ids:
        section_text = report.get_section_text(section_id) or ""
        for line_index, line_text in enumerate(section_text.splitlines(), start=1):
            compact_line = _compact_text(line_text)
            if not compact_line:
                continue
            if any(all(keyword in compact_line for keyword in keywords) for keywords in keyword_groups):
                return _TextMatch(
                    section_id=section_id,
                    line_index=line_index,
                    line_text=_normalize_cell(line_text),
                )
    return None


def _find_share_change_table(tables: tuple[ParsedTable, ...]) -> ParsedTable | None:
    """查找模板第 6 章份额变动表。

    Args:
        tables: 年报表格。

    Returns:
        命中时返回份额变动表，否则返回 ``None``。

    Raises:
        无显式抛出。
    """

    for table in tables:
        table_text = _compact_text(_joined_table_text(table))
        if "期初" in table_text and "期末" in table_text and ("申购" in table_text or "赎回" in table_text):
            return table
    return None


def _select_share_change_column(
    table: ParsedTable,
    *,
    fund_code: str,
    share_class_evidence: _ShareClassEvidence | None,
) -> int | None:
    """选择模板第 6 章份额变动表值列。

    Args:
        table: 份额变动表。
        fund_code: 当前基金代码。
        share_class_evidence: §2 当前基金代码到份额类别的显式映射。

    Returns:
        可确定时返回值列下标；歧义时返回 ``None``。

    Raises:
        无显式抛出。
    """

    value_columns = [(index, _normalize_cell(header)) for index, header in enumerate(table.headers) if index > 0]
    code_matches = [(index, header) for index, header in value_columns if fund_code in _compact_text(header)]
    if len(code_matches) == 1:
        return code_matches[0][0]
    if code_matches:
        return None
    if len(value_columns) == 1:
        return value_columns[0][0]
    if share_class_evidence is None:
        return None
    class_matches = [
        (index, header)
        for index, header in value_columns
        if _contains_share_class_label(header, share_class_evidence.class_label)
        and not _is_total_share_header(header)
    ]
    if len(class_matches) == 1:
        return class_matches[0][0]
    return None


def _share_class_evidence(report: ParsedAnnualReport) -> _ShareClassEvidence | None:
    """从 §2 识别当前基金代码对应的份额类别。

    Args:
        report: 已解析年报。

    Returns:
        唯一匹配时返回份额类别证据，否则返回 ``None``。

    Raises:
        无显式抛出。
    """

    raw_section_two = report.get_section_text(_SECTION_PROFILE) or ""
    evidence_from_lines = _share_class_evidence_from_profile_lines(raw_section_two, report.key.fund_code)
    if evidence_from_lines is not None:
        return evidence_from_lines

    section_two = _compact_text(raw_section_two)
    if report.key.fund_code not in section_two:
        return None
    matches = [
        class_label
        for class_label in _SHARE_CLASS_LABELS
        if _section_two_contains_class_mapping(section_two, report.key.fund_code, class_label)
    ]
    unique_matches = tuple(sorted(set(matches)))
    if len(unique_matches) != 1:
        return None
    return _ShareClassEvidence(
        class_label=unique_matches[0],
        source_note="§2 下属分级基金代码/简称映射",
    )


def _share_class_evidence_from_profile_lines(section_two: str, fund_code: str) -> _ShareClassEvidence | None:
    """从 §2 简称行与交易代码行按顺序配对识别份额类别。

    Args:
        section_two: §2 原始文本。
        fund_code: 当前基金代码。

    Returns:
        唯一配对命中时返回份额类别证据，否则返回 ``None``。

    Raises:
        无显式抛出。
    """

    lines = [_normalize_cell(line) for line in section_two.splitlines()]
    for line_index, line in enumerate(lines):
        if "基金简称" not in line:
            continue
        code_line = _next_profile_code_line(lines, line_index + 1)
        if code_line is None:
            continue
        class_labels = _share_class_labels_from_profile_name_line(line)
        fund_codes = re.findall(r"\d{6}", code_line)
        if len(class_labels) != len(fund_codes):
            continue
        matches = [
            class_label
            for class_label, candidate_code in zip(class_labels, fund_codes, strict=True)
            if candidate_code == fund_code
        ]
        unique_matches = tuple(sorted(set(matches)))
        if len(unique_matches) == 1:
            return _ShareClassEvidence(
                class_label=unique_matches[0],
                source_note="§2 下属分级基金简称/交易代码行",
            )
    return None


def _next_profile_code_line(lines: list[str], start_index: int) -> str | None:
    """查找 §2 简称行之后最近的交易代码行。

    Args:
        lines: §2 文本行。
        start_index: 开始查找的行号。

    Returns:
        命中的交易代码行；未命中返回 ``None``。

    Raises:
        无显式抛出。
    """

    for line in lines[start_index : start_index + 4]:
        if "交易代码" in line and re.search(r"\d{6}", line):
            return line
    return None


def _share_class_labels_from_profile_name_line(line: str) -> tuple[str, ...]:
    """从 §2 下属基金简称行提取份额类别序列。

    Args:
        line: 下属分级基金简称行。

    Returns:
        按出现顺序排列的份额类别。

    Raises:
        无显式抛出。
    """

    compact_line = _compact_text(line).upper()
    return tuple(
        match.group("label")
        for match in re.finditer(r"(?P<label>[A-Z])(?:类|份额)?(?=[\u4e00-\u9fff]|$)", compact_line)
    )


def _section_two_contains_class_mapping(section_two: str, fund_code: str, class_label: str) -> bool:
    """判断 §2 文本是否包含代码到份额类别的直接映射。

    Args:
        section_two: 已压缩的 §2 文本。
        fund_code: 当前基金代码。
        class_label: 候选份额类别。

    Returns:
        代码与类别距离足够近时返回 ``True``。

    Raises:
        无显式抛出。
    """

    code_index = section_two.find(fund_code)
    class_index = section_two.upper().find(class_label.upper())
    if code_index < 0 or class_index < 0:
        return False
    return abs(code_index - class_index) <= 80


def _contains_share_class_label(text: str, class_label: str) -> bool:
    """判断表头是否包含明确份额类别。

    Args:
        text: 表头文本。
        class_label: 份额类别。

    Returns:
        命中 ``A类``、``A份额`` 或裸后缀时返回 ``True``。

    Raises:
        无显式抛出。
    """

    compact_text = _compact_text(text).upper()
    normalized_class = class_label.upper()
    return (
        f"{normalized_class}类" in compact_text
        or f"{normalized_class}份额" in compact_text
        or compact_text.endswith(normalized_class)
    )


def _is_total_share_header(text: str) -> bool:
    """判断表头是否为总份额列。

    Args:
        text: 表头文本。

    Returns:
        包含合计、总计或总份额语义时返回 ``True``。

    Raises:
        无显式抛出。
    """

    compact_text = _compact_text(text)
    return any(keyword in compact_text for keyword in ("合计", "总计", "总份额", "基金份额总额"))


def _table_contains_all(table: ParsedTable, keywords: tuple[str, ...]) -> bool:
    """判断表格是否包含全部关键词。

    Args:
        table: 待检查表格。
        keywords: 必须全部出现的关键词。

    Returns:
        全部命中时返回 ``True``。

    Raises:
        无显式抛出。
    """

    table_text = _compact_text(_joined_table_text(table))
    return all(keyword in table_text for keyword in keywords)


def _row_has_absence_value(row: tuple[str, ...]) -> bool:
    """判断表格行是否披露显式缺席值。

    Args:
        row: 表格行。

    Returns:
        存在 ``-``、``0``、``0.00`` 或 ``0.00%`` 等缺席值时返回 ``True``。

    Raises:
        无显式抛出。
    """

    for cell in row[1:] or row:
        normalized = _normalize_cell(cell)
        if normalized in {"-", "－", "0", "0.0", "0.00", "0%", "0.00%"}:
            return True
    return False


def _joined_table_text(table: ParsedTable) -> str:
    """拼接表格文本。

    Args:
        table: 年报表格。

    Returns:
        表头和数据行拼接文本。

    Raises:
        无显式抛出。
    """

    cells = list(table.headers)
    for row in table.rows:
        cells.extend(row)
    return " ".join(_normalize_cell(cell) for cell in cells)


def _format_row_note(row: tuple[str, ...], *, value_column_index: int | None = None) -> str:
    """格式化模板第 6 章表格行备注。

    Args:
        row: 表格行。
        value_column_index: 需要强调的值列下标。

    Returns:
        行文本备注。

    Raises:
        无显式抛出。
    """

    if value_column_index is not None and value_column_index < len(row):
        return _trim_note(f"{row[0]}={row[value_column_index]}")
    return _trim_note(" | ".join(row))


def _table_id(table: ParsedTable) -> str:
    """构造稳定表格 ID。

    Args:
        table: 年报表格。

    Returns:
        ``page-<页码>-table-<序号>`` 格式 ID。

    Raises:
        无显式抛出。
    """

    return f"page-{table.page_number}-table-{table.table_index}"


def _normalize_cell(value: str) -> str:
    """规范化单元格或文本。

    Args:
        value: 原始文本。

    Returns:
        去除首尾空白后的文本。

    Raises:
        无显式抛出。
    """

    return str(value).strip()


def _compact_text(value: str) -> str:
    """压缩文本空白。

    Args:
        value: 原始文本。

    Returns:
        删除全部空白后的文本。

    Raises:
        无显式抛出。
    """

    return "".join(str(value).split())


def _trim_note(value: str) -> str:
    """截断锚点备注。

    Args:
        value: 原始备注。

    Returns:
        长度受控的备注。

    Raises:
        无显式抛出。
    """

    normalized = _normalize_cell(value)
    if len(normalized) <= _MAX_TEXT_ANCHOR_LENGTH:
        return normalized
    return normalized[:_MAX_TEXT_ANCHOR_LENGTH]


def _extraction_mode(value: BondRiskEvidenceValue) -> str:
    """把模板第 6 章契约状态映射为 ExtractedField 模式。

    Args:
        value: 债券风险证据契约值。

    Returns:
        ``direct``、``estimated`` 或 ``missing``。

    Raises:
        无显式抛出。
    """

    if value.contract_status == "satisfied":
        return "direct"
    if value.contract_status == "partial":
        return "estimated"
    return "missing"


def _field_note(value: BondRiskEvidenceValue) -> str:
    """构造模板第 6 章字段备注。

    Args:
        value: 债券风险证据契约值。

    Returns:
        稳定字段备注。

    Raises:
        无显式抛出。
    """

    return (
        f"contract_id={value.contract_id}; "
        f"contract_status={value.contract_status}; "
        f"satisfied_groups={','.join(value.satisfied_group_ids)}; "
        f"missing_groups={','.join(value.missing_group_ids)}; "
        f"weak_groups={','.join(value.weak_group_ids)}; "
        f"ambiguous_groups={','.join(value.ambiguous_group_ids)}"
    )
