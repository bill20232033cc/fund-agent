"""债券风险证据抽取器。

本模块只从已经加载完成的 ``ParsedAnnualReport`` 中抽取模板第 6 章“核心风险”
所需的 ``bond_risk_evidence.v1`` 七组证据，不访问文档仓库、PDF 缓存或来源 helper。
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import Final

from fund_agent.fund.data.nav_metrics import NavMaxDrawdownMetric, format_max_drawdown_percent
from fund_agent.fund.data.nav_models import NavDataContractError
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
_DECIMAL_TOLERANCE: Final[Decimal] = Decimal("0.01")
_DECIMAL_UNIT_SUFFIXES: Final[tuple[str, ...]] = ("份",)
_DASH_ZERO_VALUES: Final[tuple[str, ...]] = ("-", "－", "—", "--")
_CURRENT_PERIOD_HEADER_KEYWORDS: Final[tuple[str, ...]] = ("本期", "本期末", "期末", "报告期末")
_PRIOR_PERIOD_HEADER_KEYWORDS: Final[tuple[str, ...]] = ("上年度", "上年", "上期", "期初", "年初")
_PERCENTAGE_HEADER_KEYWORDS: Final[tuple[str, ...]] = ("比例", "占比")
_CREDIT_RATING_LABELS: Final[tuple[str, ...]] = (
    "A-1",
    "AAA以下",
    "未评级",
    "AAA",
    "AA+",
    "AA-",
    "AA",
    "A+",
    "A-",
    "A",
    "BBB",
    "合计",
)
_FUND_OWN_RATING_KEYWORDS: Final[tuple[str, ...]] = ("本基金评级", "基金评级信息", "基金自身评级", "基金信用评级")
_HOLDING_RATING_QUALIFIERS: Final[tuple[str, ...]] = ("持有", "持仓", "证券", "债券", "投资组合", "组合")
_SHARE_CHANGE_FINANCIAL_STATEMENT_KEYWORDS: Final[tuple[str, ...]] = ("实收基金", "未分配利润", "净资产合计")
_SHARE_SUBSCRIPTION_KEYWORD_GROUPS: Final[tuple[tuple[str, ...], ...]] = (("总申购",), ("申购份额",))
_SHARE_REDEMPTION_KEYWORD_GROUPS: Final[tuple[tuple[str, ...], ...]] = (("总赎回",), ("赎回份额",))
_SHARE_SUBSCRIPTION_EXCLUDED_KEYWORDS: Final[tuple[str, ...]] = ("净申购", "累计申购")
_SHARE_REDEMPTION_EXCLUDED_KEYWORDS: Final[tuple[str, ...]] = ("净赎回", "累计赎回")
_SHARE_CHANGE_ROW_LABEL_KEYWORDS: Final[tuple[str, ...]] = (
    "期初",
    "申购",
    "赎回",
    "期末",
    "拆分",
    "变动",
    "份额",
    "项目",
)
_PROFILE_CLASS_NAME_ROW_KEYWORD: Final[str] = "下属分级基金的基金简称"
_PROFILE_CLASS_CODE_ROW_KEYWORD: Final[str] = "下属分级基金的交易代码"
_PROFILE_CLASS_ENDING_ROW_KEYWORD: Final[str] = "报告期末下属分级基金的份额总额"
_SHARE_CHANGE_ALIGNMENT_EXPLICIT: Final[str] = "explicit_headers"
_SHARE_CHANGE_ALIGNMENT_UNLABELED: Final[str] = "section2_order_unlabeled_headers"


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
class _CreditRatingDistributionEvidence:
    """模板第 6 章信用评级分布表证据。

    Attributes:
        drafts: 评级分布表行级锚点草稿。
        metric_value: 代表性当前期持仓评级分布摘要。
    """

    drafts: tuple[_AnchorDraft, ...]
    metric_value: str


@dataclass(frozen=True, slots=True)
class _ShareClassMapping:
    """模板第 6 章份额类别映射。

    Attributes:
        class_labels: 份额类别标签序列。
        fund_codes: 与份额类别一一对应的基金代码序列。
        source_note: 映射来源说明。
        source_anchor_draft: 可选 §2 表格锚点草稿。
    """

    class_labels: tuple[str, ...]
    fund_codes: tuple[str, ...]
    source_note: str
    source_anchor_draft: _AnchorDraft | None = None


@dataclass(frozen=True, slots=True)
class _ShareChangeTableSelection:
    """模板第 6 章份额变动表选择结果。

    Attributes:
        table: 唯一命中的 §10 份额变动表。
        na_reason: 未能唯一选择时的失败原因。
    """

    table: ParsedTable | None
    na_reason: str | None


@dataclass(frozen=True, slots=True)
class _ShareChangeColumnMapping:
    """模板第 6 章份额变动表列映射。

    Attributes:
        class_to_column: 份额类别到 §10 表格列下标的映射。
        alignment_note: 列对齐方式说明。
        na_reason: 无法对齐时的失败原因。
    """

    class_to_column: dict[str, int]
    alignment_note: str | None
    na_reason: str | None


@dataclass(frozen=True, slots=True)
class _ShareClassEndingCrossCheck:
    """模板第 6 章 §2 份额类别期末份额交叉校验。

    Attributes:
        ending_by_class: 按份额类别记录的 §2 期末份额。
        source_anchor_draft: §2 profile 表交叉校验锚点草稿。
    """

    ending_by_class: dict[str, Decimal]
    source_anchor_draft: _AnchorDraft


@dataclass(frozen=True, slots=True)
class _ShareChangeRows:
    """模板第 6 章份额变动表行定位结果。

    Attributes:
        beginning: 期初份额行。
        subscription: 申购份额行。
        redemption: 赎回份额行。
        split: 拆分变动行；未披露时为 ``None`` 并按零处理。
        ending: 期末份额行。
    """

    beginning: tuple[int, tuple[str, ...]]
    subscription: tuple[int, tuple[str, ...]]
    redemption: tuple[int, tuple[str, ...]]
    split: tuple[int, tuple[str, ...]] | None
    ending: tuple[int, tuple[str, ...]]


@dataclass(frozen=True, slots=True)
class _ShareClassChange:
    """模板第 6 章单一份额类别变动计算结果。

    Attributes:
        class_label: 份额类别。
        fund_code: 基金代码。
        beginning: 期初份额。
        subscription: 申购份额。
        redemption: 赎回份额。
        split: 拆分变动份额。
        ending: 期末份额。
        net_change: 净变动份额。
        net_change_ratio: 净变动比例；期初为零时为 ``None``。
        note: 类别级补充说明。
    """

    class_label: str
    fund_code: str
    beginning: Decimal
    subscription: Decimal
    redemption: Decimal
    split: Decimal
    ending: Decimal
    net_change: Decimal
    net_change_ratio: Decimal | None
    note: str | None


@dataclass(frozen=True, slots=True)
class _ShareChangeAggregation:
    """模板第 6 章全份额类别赎回压力汇总。

    Attributes:
        metric_value: 确定性指标摘要。
        drafts: §10 必需行级锚点及可选 §2 映射锚点。
        na_reason: 失败关闭原因。
    """

    metric_value: str | None
    drafts: tuple[_AnchorDraft, ...]
    na_reason: str | None


def extract_bond_risk_evidence(
    report: ParsedAnnualReport,
    classified_fund_type: str | None,
    *,
    drawdown_metric: NavMaxDrawdownMetric | None = None,
    drawdown_metric_error: NavDataContractError | None = None,
) -> ExtractedField[BondRiskEvidenceValue]:
    """抽取模板第 6 章债券风险证据。

    Args:
        report: 已通过统一文档仓库加载并解析的年报。
        classified_fund_type: 上游显式基金类型；只有精确 ``bond_fund`` 才执行七组扫描。
        drawdown_metric: 可选 NAV 派生最大回撤指标；由上游通过 `FundNavRepository`
            显式加载并计算，本 extractor 不执行 IO。
        drawdown_metric_error: NAV 派生指标失败分类；仅用于保留失败关闭原因。

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
        _extract_drawdown_stress(
            report,
            drawdown_metric=drawdown_metric,
            drawdown_metric_error=drawdown_metric_error,
        ),
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
    rating_distribution = _credit_rating_distribution_evidence(report.tables, group_id)
    if rating_distribution is not None:
        return _anchored_group(
            report,
            group_id=group_id,
            status="accepted",
            strength="quantitative_direct",
            summary="年报表格披露持有债券/证券的信用评级分布",
            measurement_kind="actual_exposure",
            metric_name="持仓评级分布",
            metric_value=rating_distribution.metric_value,
            drafts=rating_distribution.drafts,
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


def _extract_drawdown_stress(
    report: ParsedAnnualReport,
    *,
    drawdown_metric: NavMaxDrawdownMetric | None = None,
    drawdown_metric_error: NavDataContractError | None = None,
) -> _GroupExtraction:
    """抽取模板第 6 章回撤和压力证据。

    Args:
        report: 已解析年报。
        drawdown_metric: 可选 NAV 派生最大回撤指标。
        drawdown_metric_error: NAV 派生指标失败分类。

    Returns:
        回撤/压力组抽取结果。

    Raises:
        无显式抛出。
    """

    group_id: BondRiskEvidenceGroupId = "drawdown_stress"
    if drawdown_metric is not None:
        return _derived_drawdown_metric_group(report, drawdown_metric)

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
            na_reason=_drawdown_error_reason(drawdown_metric_error) or "drawdown_metric_not_found",
        )
    if drawdown_metric_error is not None:
        return _missing_group(group_id, _drawdown_error_reason(drawdown_metric_error) or drawdown_metric_error.message)
    return _missing_group(group_id, "年报未定位到回撤指标或回撤控制文本")


def _derived_drawdown_metric_group(
    report: ParsedAnnualReport,
    drawdown_metric: NavMaxDrawdownMetric,
) -> _GroupExtraction:
    """构造 NAV 派生最大回撤强证据组，见模板第 6 章“核心风险”。

    Args:
        report: 已解析年报。
        drawdown_metric: NAV 派生最大回撤指标。

    Returns:
        accepted 派生定量证据组。

    Raises:
        无显式抛出。
    """

    group_id: BondRiskEvidenceGroupId = "drawdown_stress"
    draft = _derived_nav_metric_anchor_draft(group_id, drawdown_metric)
    anchors, anchor_refs = _build_group_anchors(report, group_id, (draft,))
    record = BondRiskEvidenceGroupRecord(
        group_id=group_id,
        status="accepted",
        strength="quantitative_derived",
        summary=f"CSRC EID A 类累计净值路径计算 {report.key.year} 年报期间最大回撤",
        measurement_kind="derived_metric",
        metric_name="最大回撤",
        metric_value=format_max_drawdown_percent(drawdown_metric.max_drawdown_ratio),
        metric_unit="ratio",
        period_label=(
            f"{drawdown_metric.period_start.isoformat()} 至 {drawdown_metric.period_end.isoformat()}"
        ),
        source_anchor_ids=tuple(anchor.anchor_id for anchor in anchor_refs),
        na_reason=None,
        reviewer_note=(
            "annual-report drawdown control intent remains weak companion; "
            "quantitative source is CSRC EID accumulated NAV"
        ),
    )
    return _GroupExtraction(record=record, anchors=anchors, anchor_refs=anchor_refs)


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
    table_selection = _find_share_change_table(report.tables)
    if table_selection.table is None:
        if table_selection.na_reason is not None:
            return _plain_group(
                group_id=group_id,
                status="ambiguous",
                strength="ambiguous",
                summary="份额变动表候选无法唯一确定，已失败关闭",
                measurement_kind="actual_exposure",
                na_reason=table_selection.na_reason,
            )
        return _missing_group(group_id, "年报未定位到基金份额变动表")

    mapping = _share_class_mapping(report, group_id)
    if mapping is None:
        return _plain_group(
            group_id=group_id,
            status="ambiguous",
            strength="ambiguous",
            summary="份额变动表存在但 §2 份额类别映射不完整，不能聚合全份额类别",
            measurement_kind="actual_exposure",
            na_reason="ambiguous_share_class_selection",
        )

    aggregation = _aggregate_share_change(
        table_selection.table,
        report=report,
        group_id=group_id,
        mapping=mapping,
    )
    if aggregation.metric_value is None:
        return _plain_group(
            group_id=group_id,
            status="ambiguous",
            strength="ambiguous",
            summary="份额变动表无法完成 A/C/E/F 全类别聚合与对账，已失败关闭",
            measurement_kind="actual_exposure",
            na_reason=aggregation.na_reason or "ambiguous_share_change_aggregation",
        )

    drafts = aggregation.drafts
    if mapping.source_anchor_draft is not None:
        drafts = (*drafts, mapping.source_anchor_draft)

    return _anchored_group(
        report,
        group_id=group_id,
        status="accepted",
        strength="quantitative_direct",
        summary="年报份额变动表可按 §2 A/C/E/F 映射聚合全份额类别申购赎回数据",
        measurement_kind="actual_exposure",
        metric_name="A/C/E/F 份额变动汇总",
        metric_value=aggregation.metric_value,
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
        source_kind = "derived" if draft.section_id.startswith("derived:") else "annual_report"
        evidence_anchors.append(
            EvidenceAnchor(
                source_kind=source_kind,
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


def _derived_nav_metric_anchor_draft(
    group_id: BondRiskEvidenceGroupId,
    metric: NavMaxDrawdownMetric,
) -> _AnchorDraft:
    """构造 NAV 派生指标锚点草稿。

    Args:
        group_id: 风险组 ID。
        metric: NAV 派生最大回撤指标。

    Returns:
        派生 NAV 指标锚点草稿。

    Raises:
        无显式抛出。
    """

    row_locator = (
        "metric:max_drawdown:"
        f"{metric.share_class}:{metric.period_start.isoformat()}:{metric.period_end.isoformat()}"
    )
    note = "; ".join(
        (
            "source=CSRC EID",
            f"source_name={metric.source.source_name}",
            f"source_id={metric.source.source_id}",
            f"source_url={metric.source.source_url}",
            f"source_query_params={_stable_query_params(metric.source.source_query_params)}",
            f"retrieved_at={_optional_isoformat(metric.source.retrieved_at)}",
            f"fund_code={metric.fund_code}",
            f"share_class={metric.share_class}",
            f"date_range={metric.period_start.isoformat()}..{metric.period_end.isoformat()}",
            f"record_count={metric.record_count}",
            f"nav_type={metric.nav_type}",
            f"adjusted_basis={metric.adjusted_basis}",
            f"dividend_adjustment_status={metric.dividend_adjustment_status}",
            f"identity_status={metric.identity_status}",
            f"calculation_method={metric.calculation_method}",
            f"peak_date={metric.peak_date.isoformat()}",
            f"peak_value={metric.peak_value}",
            f"trough_date={metric.trough_date.isoformat()}",
            f"trough_value={metric.trough_value}",
            f"max_drawdown_ratio={metric.max_drawdown_ratio}",
        )
    )
    return _AnchorDraft(
        group_id=group_id,
        section_id="derived:nav",
        page_number=None,
        table_id=None,
        row_locator=row_locator,
        evidence_role="derived_max_drawdown_metric",
        note=note,
    )


def _drawdown_error_reason(error: NavDataContractError | None) -> str | None:
    """把 NAV 指标失败映射为模板第 6 章回撤组缺口原因。

    Args:
        error: NAV 数据契约错误。

    Returns:
        稳定 `drawdown_` 前缀原因；无错误时返回 `None`。

    Raises:
        无显式抛出。
    """

    if error is None:
        return None
    return f"drawdown_nav_{error.category}"


def _stable_query_params(params: tuple[tuple[str, str], ...]) -> str:
    """稳定序列化 NAV source query params。

    Args:
        params: source 元数据中的 query params。

    Returns:
        按 key/value 排序后的文本。

    Raises:
        无显式抛出。
    """

    return ",".join(f"{key}={value}" for key, value in sorted(params))


def _optional_isoformat(value: object) -> str:
    """把可选 datetime-like 值转为 ISO 文本。

    Args:
        value: 可选对象。

    Returns:
        ISO 文本或 `None`。

    Raises:
        无显式抛出。
    """

    if hasattr(value, "isoformat"):
        return str(value.isoformat())  # type: ignore[attr-defined]
    return "None"


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


def _credit_rating_distribution_evidence(
    tables: tuple[ParsedTable, ...],
    group_id: BondRiskEvidenceGroupId,
) -> _CreditRatingDistributionEvidence | None:
    """识别模板第 6 章持仓信用评级分布表。

    Args:
        tables: 年报表格。
        group_id: 风险组 ID。

    Returns:
        命中持仓评级分布且具备当前期数值和行级锚点时返回证据，否则返回 ``None``。

    Raises:
        无显式抛出。
    """

    drafts: list[_AnchorDraft] = []
    representative_metric: str | None = None
    for table in tables:
        table_rows = _credit_rating_distribution_rows(table, group_id)
        if not table_rows:
            continue
        if representative_metric is None:
            representative_metric = _credit_rating_distribution_metric(table_rows)
        drafts.extend(draft for draft, _label, _value in table_rows)

    if not drafts or representative_metric is None:
        return None
    return _CreditRatingDistributionEvidence(
        drafts=tuple(drafts),
        metric_value=_trim_note(representative_metric),
    )


def _credit_rating_distribution_rows(
    table: ParsedTable,
    group_id: BondRiskEvidenceGroupId,
) -> tuple[tuple[_AnchorDraft, str, Decimal], ...]:
    """抽取单张持仓信用评级分布表的有效评级行。

    Args:
        table: 候选年报表格。
        group_id: 风险组 ID。

    Returns:
        行锚点、评级标签和当前期数值三元组；不满足契约时返回空元组。

    Raises:
        无显式抛出。
    """

    if not _is_holding_rating_distribution_table(table):
        return ()

    rows: list[tuple[_AnchorDraft, str, Decimal]] = []
    non_zero_numeric_rows = 0
    for row_index, row in enumerate(table.rows, start=1):
        rating_label = _rating_label_from_row(row)
        if rating_label is None:
            continue
        current_value_column_index = _current_period_value_column_index(table.headers, row)
        if current_value_column_index is None:
            continue
        current_value = _parse_plain_decimal(row[current_value_column_index])
        if current_value is None:
            continue
        if current_value != Decimal("0"):
            non_zero_numeric_rows += 1
        row_label = _normalize_cell(row[0]) if row else f"row-{row_index}"
        drafts_note = _format_row_note(row, value_column_index=current_value_column_index)
        rows.append(
            (
                _AnchorDraft(
                    group_id=group_id,
                    section_id=_SECTION_PORTFOLIO,
                    page_number=table.page_number,
                    table_id=_table_id(table),
                    row_locator=f"row:{row_index}:{row_label}",
                    evidence_role="holding_rating_distribution",
                    note=drafts_note,
                ),
                rating_label,
                current_value,
            )
        )

    if len(rows) < 2 or non_zero_numeric_rows == 0:
        return ()
    return tuple(rows)


def _is_holding_rating_distribution_table(table: ParsedTable) -> bool:
    """判断表格是否为持仓债券/证券信用评级分布，而非基金自身评级。

    Args:
        table: 候选年报表格。

    Returns:
        满足持仓评级分布语义时返回 ``True``。

    Raises:
        无显式抛出。
    """

    table_text = _compact_text(_joined_table_text(table))
    if any(keyword in table_text for keyword in _FUND_OWN_RATING_KEYWORDS):
        return False
    has_rating_semantics = "信用评级" in table_text or "短期信用评级" in table_text or "长期信用评级" in table_text
    if not has_rating_semantics:
        return False
    has_holding_qualifier = any(keyword in table_text for keyword in _HOLDING_RATING_QUALIFIERS)
    if "本基金" in table_text and "评级" in table_text and not has_holding_qualifier:
        return False
    return True


def _rating_label_from_row(row: tuple[str, ...]) -> str | None:
    """从评级分布行识别评级标签。

    Args:
        row: 表格行。

    Returns:
        评级标签；未识别时返回 ``None``。

    Raises:
        无显式抛出。
    """

    row_label = _compact_text(row[0]).upper() if row else ""
    for label in _CREDIT_RATING_LABELS:
        if row_label == label.upper():
            return label
    for label in _CREDIT_RATING_LABELS:
        if _is_compound_rating_label(row_label, label.upper()):
            return label
    return None


def _is_compound_rating_label(row_label: str, label: str) -> bool:
    """判断复合评级行是否包含可接受的评级标签。

    Args:
        row_label: 已规整并大写的行标签。
        label: 已大写的候选评级标签。

    Returns:
        复合行标签可映射到候选评级时返回 ``True``。

    Raises:
        无显式抛出。
    """

    if label not in row_label:
        return False
    before, _matched, after = row_label.partition(label)
    rating_token_chars = set("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789+-")
    if before and before[-1] in rating_token_chars:
        return False
    if after and after[0] in rating_token_chars:
        return False
    return True


def _current_period_value_column_index(headers: tuple[str, ...], row: tuple[str, ...]) -> int | None:
    """查找评级分布行当前期金额列。

    Args:
        headers: 表格表头。
        row: 表格行。

    Returns:
        当前期金额列下标；无有效金额或多列无法可靠区分时返回 ``None``。

    Raises:
        无显式抛出。
    """

    numeric_columns = []
    for index, cell in enumerate(row[1:], start=1):
        if "%" in str(cell):
            continue
        if _parse_plain_decimal(cell) is not None:
            numeric_columns.append(index)
    if not numeric_columns:
        return None

    current_columns = tuple(
        index
        for index in numeric_columns
        if _is_current_period_amount_header(_header_at(headers, index))
    )
    if len(current_columns) == 1:
        return current_columns[0]
    if len(current_columns) > 1:
        return None

    non_prior_columns = tuple(
        index
        for index in numeric_columns
        if not _is_prior_period_header(_header_at(headers, index))
    )
    if len(numeric_columns) == 1 and len(non_prior_columns) == 1:
        return non_prior_columns[0]
    return None


def _header_at(headers: tuple[str, ...], index: int) -> str:
    """读取指定表头单元格。

    Args:
        headers: 表格表头。
        index: 列下标。

    Returns:
        对应表头；越界时返回空字符串。

    Raises:
        无显式抛出。
    """

    if index >= len(headers):
        return ""
    return headers[index]


def _is_current_period_amount_header(header: str) -> bool:
    """判断表头是否表达当前期金额列。

    Args:
        header: 表头文本。

    Returns:
        具备当前期语义且非前期/比例语义时返回 ``True``。

    Raises:
        无显式抛出。
    """

    compact_header = _compact_text(header)
    has_current_period = any(keyword in compact_header for keyword in _CURRENT_PERIOD_HEADER_KEYWORDS)
    has_percentage = any(keyword in compact_header for keyword in _PERCENTAGE_HEADER_KEYWORDS)
    return has_current_period and not has_percentage and not _is_prior_period_header(header)


def _is_prior_period_header(header: str) -> bool:
    """判断表头是否表达前期或期初列。

    Args:
        header: 表头文本。

    Returns:
        命中前期/期初语义时返回 ``True``。

    Raises:
        无显式抛出。
    """

    compact_header = _compact_text(header)
    return any(keyword in compact_header for keyword in _PRIOR_PERIOD_HEADER_KEYWORDS)


def _credit_rating_distribution_metric(rows: tuple[tuple[_AnchorDraft, str, Decimal], ...]) -> str:
    """格式化代表性持仓评级分布摘要。

    Args:
        rows: 单张表的有效评级行。

    Returns:
        当前期评级分布摘要。

    Raises:
        无显式抛出。
    """

    parts = [f"{label}={_format_decimal(value)}" for _draft, label, value in rows]
    return f"holding_rating_distribution: {', '.join(parts)}"


def _find_share_change_table(tables: tuple[ParsedTable, ...]) -> _ShareChangeTableSelection:
    """查找模板第 6 章份额变动表。

    Args:
        tables: 年报表格。

    Returns:
        唯一命中时返回份额变动表；无命中或歧义时携带失败原因。

    Raises:
        无显式抛出。
    """

    candidates: list[tuple[int, ParsedTable]] = []
    for table in tables:
        score = _share_change_table_score(table)
        if score > 0:
            candidates.append((score, table))

    if not candidates:
        return _ShareChangeTableSelection(table=None, na_reason=None)
    best_score = max(score for score, _table in candidates)
    best_tables = tuple(table for score, table in candidates if score == best_score)
    if len(best_tables) != 1:
        return _ShareChangeTableSelection(table=None, na_reason="ambiguous_share_change_table")
    return _ShareChangeTableSelection(table=best_tables[0], na_reason=None)


def _share_change_table_score(table: ParsedTable) -> int:
    """为 §10 份额变动表候选打分。

    Args:
        table: 候选年报表格。

    Returns:
        正数表示候选表；零表示拒绝。

    Raises:
        无显式抛出。
    """

    table_text = _compact_text(_joined_table_text(table))
    if any(keyword in table_text for keyword in _SHARE_CHANGE_FINANCIAL_STATEMENT_KEYWORDS):
        return 0
    has_boundary_row = "期初" in table_text or "期末" in table_text
    has_flow_row = "申购" in table_text or "赎回" in table_text
    has_share_semantics = "基金份额" in table_text or "份额总额" in table_text
    if not (has_boundary_row and has_flow_row and has_share_semantics):
        return 0

    score = 1
    for keyword in ("基金份额", "份额总额", "基金总申购份额", "基金总赎回份额", "基金份额总额"):
        if keyword in table_text:
            score += 2
    if "拆分" in table_text or "变动" in table_text:
        score += 1
    return score


def _share_class_mapping(report: ParsedAnnualReport, group_id: BondRiskEvidenceGroupId) -> _ShareClassMapping | None:
    """从 §2 表格或文本识别全份额类别映射。

    Args:
        report: 已解析年报。
        group_id: 风险组 ID。

    Returns:
        A/C/E/F 等份额类别到基金代码的完整映射；无法唯一识别时返回 ``None``。

    Raises:
        无显式抛出。
    """

    table_mapping = _share_class_mapping_from_profile_tables(report.tables, group_id)
    if table_mapping is not None:
        return table_mapping

    section_two = report.get_section_text(_SECTION_PROFILE) or ""
    return _share_class_mapping_from_profile_lines(section_two)


def _share_class_mapping_from_profile_tables(
    tables: tuple[ParsedTable, ...],
    group_id: BondRiskEvidenceGroupId,
) -> _ShareClassMapping | None:
    """从 §2 表格式简称/交易代码行识别份额类别映射。

    Args:
        tables: 年报表格。
        group_id: 风险组 ID。

    Returns:
        唯一完整映射；否则返回 ``None``。

    Raises:
        无显式抛出。
    """

    for table in tables:
        for name_index, name_row in enumerate(table.rows, start=1):
            if not name_row or "基金简称" not in _compact_text(name_row[0]):
                continue
            code_match = _next_profile_code_row(table.rows, name_index)
            if code_match is None:
                continue
            code_index, code_row = code_match
            class_labels = _share_class_labels_from_profile_name_cells(name_row)
            fund_codes = tuple(_normalize_cell(cell) for cell in code_row[1:] if re.fullmatch(r"\d{6}", _compact_text(cell)))
            if len(class_labels) != len(fund_codes) or len(set(class_labels)) != len(class_labels):
                continue
            note = "; ".join(
                f"{class_label}={fund_code}" for class_label, fund_code in zip(class_labels, fund_codes, strict=True)
            )
            return _ShareClassMapping(
                class_labels=class_labels,
                fund_codes=fund_codes,
                source_note=f"§2 下属分级基金简称/交易代码表: {note}",
                source_anchor_draft=_AnchorDraft(
                    group_id=group_id,
                    section_id=_SECTION_PROFILE,
                    page_number=table.page_number,
                    table_id=_table_id(table),
                    row_locator=f"rows:{name_index},{code_index}:share_class_mapping",
                    evidence_role="share_class_mapping",
                    note=_trim_note(note),
                ),
            )
    return None


def _next_profile_code_row(
    rows: tuple[tuple[str, ...], ...],
    start_row_number: int,
) -> tuple[int, tuple[str, ...]] | None:
    """查找 §2 基金简称行之后最近的交易代码行。

    Args:
        rows: 表格行。
        start_row_number: 简称行的一基行号。

    Returns:
        交易代码行号和行内容；未命中返回 ``None``。

    Raises:
        无显式抛出。
    """

    for row_number, row in enumerate(rows[start_row_number:], start=start_row_number + 1):
        row_text = _compact_text(" ".join(row))
        if "交易代码" in row_text and re.search(r"\d{6}", row_text):
            return row_number, row
    return None


def _share_class_mapping_from_profile_lines(section_two: str) -> _ShareClassMapping | None:
    """从 §2 文本行识别全份额类别映射。

    Args:
        section_two: §2 原始文本。

    Returns:
        唯一完整映射；否则返回 ``None``。

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
        fund_codes = tuple(re.findall(r"\d{6}", code_line))
        if len(class_labels) != len(fund_codes) or len(set(class_labels)) != len(class_labels):
            continue
        note = "; ".join(
            f"{class_label}={fund_code}" for class_label, fund_code in zip(class_labels, fund_codes, strict=True)
        )
        return _ShareClassMapping(
            class_labels=class_labels,
            fund_codes=fund_codes,
            source_note=f"§2 下属分级基金简称/交易代码行: {note}",
        )
    return None


def _share_class_labels_from_profile_name_cells(row: tuple[str, ...]) -> tuple[str, ...]:
    """从 §2 简称表格行提取份额类别序列。

    Args:
        row: 下属基金简称行。

    Returns:
        按列顺序排列的份额类别。

    Raises:
        无显式抛出。
    """

    return tuple(
        label
        for cell in row[1:]
        for label in _share_class_labels_from_profile_name_line(cell)
    )


def _aggregate_share_change(
    table: ParsedTable,
    *,
    report: ParsedAnnualReport,
    group_id: BondRiskEvidenceGroupId,
    mapping: _ShareClassMapping,
) -> _ShareChangeAggregation:
    """聚合模板第 6 章 A/C/E/F 全份额类别份额变动。

    Args:
        table: §10 份额变动表。
        report: 已解析年报。
        group_id: 风险组 ID。
        mapping: §2 份额类别映射。

    Returns:
        成功时返回 metric 和锚点；失败时返回 ``na_reason``。

    Raises:
        无显式抛出。
    """

    column_mapping = _align_share_change_columns(table, mapping)
    if column_mapping.na_reason is not None:
        return _ShareChangeAggregation(metric_value=None, drafts=(), na_reason=column_mapping.na_reason)

    rows = _find_share_change_rows(table)
    if rows is None:
        return _ShareChangeAggregation(metric_value=None, drafts=(), na_reason="incomplete_share_change_rows")

    class_changes = _calculate_share_class_changes(rows, mapping, column_mapping.class_to_column)
    if isinstance(class_changes, str):
        return _ShareChangeAggregation(metric_value=None, drafts=(), na_reason=class_changes)

    aggregate_beginning = sum((item.beginning for item in class_changes), Decimal("0"))
    aggregate_subscription = sum((item.subscription for item in class_changes), Decimal("0"))
    aggregate_redemption = sum((item.redemption for item in class_changes), Decimal("0"))
    aggregate_split = sum((item.split for item in class_changes), Decimal("0"))
    aggregate_ending = sum((item.ending for item in class_changes), Decimal("0"))
    aggregate_net_change = aggregate_subscription - aggregate_redemption + aggregate_split
    if aggregate_beginning == Decimal("0"):
        return _ShareChangeAggregation(metric_value=None, drafts=(), na_reason="aggregate_beginning_zero")
    if not _decimal_close(aggregate_beginning + aggregate_net_change, aggregate_ending):
        return _ShareChangeAggregation(metric_value=None, drafts=(), na_reason="share_change_arithmetic_mismatch")

    cross_check_draft: _AnchorDraft | None = None
    if column_mapping.alignment_note == _SHARE_CHANGE_ALIGNMENT_UNLABELED:
        cross_check = _share_class_ending_cross_check_from_profile_tables(
            report.tables,
            mapping=mapping,
            group_id=group_id,
            excluded_table=table,
        )
        if cross_check is None:
            return _ShareChangeAggregation(
                metric_value=None,
                drafts=(),
                na_reason="share_class_ending_cross_check_missing",
            )
        cross_check_result = _validate_share_class_ending_cross_check(class_changes, cross_check)
        if cross_check_result is not None:
            return _ShareChangeAggregation(metric_value=None, drafts=(), na_reason=cross_check_result)
        cross_check_draft = cross_check.source_anchor_draft

    metric_value = _format_share_change_metric(
        class_changes=class_changes,
        aggregate_beginning=aggregate_beginning,
        aggregate_subscription=aggregate_subscription,
        aggregate_redemption=aggregate_redemption,
        aggregate_split=aggregate_split,
        aggregate_ending=aggregate_ending,
        aggregate_net_change=aggregate_net_change,
        aggregate_net_change_ratio=aggregate_net_change / aggregate_beginning,
        source_note=mapping.source_note,
        alignment_note=column_mapping.alignment_note,
    )
    drafts = _share_change_row_anchor_drafts(table, group_id, rows)
    if len(drafts) < 4:
        return _ShareChangeAggregation(metric_value=None, drafts=(), na_reason="incomplete_share_change_rows")
    if cross_check_draft is not None:
        drafts = (*drafts, cross_check_draft)
    return _ShareChangeAggregation(metric_value=metric_value, drafts=drafts, na_reason=None)


def _align_share_change_columns(
    table: ParsedTable,
    mapping: _ShareClassMapping,
) -> _ShareChangeColumnMapping:
    """把 §10 份额变动表值列对齐到 §2 份额类别映射。

    Args:
        table: §10 份额变动表。
        mapping: §2 份额类别映射。

    Returns:
        类别到值列下标的映射；失败时给出原因。

    Raises:
        无显式抛出。
    """

    value_columns = tuple(
        (index, _normalized_header_text(table.headers[index]))
        for index in _share_change_value_columns(table)
    )
    if len(value_columns) != len(mapping.class_labels):
        return _ShareChangeColumnMapping(
            class_to_column={},
            alignment_note=None,
            na_reason="share_class_column_count_mismatch",
        )

    class_to_column: dict[str, int] = {}
    used_columns: set[int] = set()
    for class_label, fund_code in zip(mapping.class_labels, mapping.fund_codes, strict=True):
        matches = [
            index
            for index, header in value_columns
            if _header_has_explicit_share_class(header, class_label, fund_code)
        ]
        unique_matches = tuple(dict.fromkeys(matches))
        if len(unique_matches) != 1 or unique_matches[0] in used_columns:
            break
        class_to_column[class_label] = unique_matches[0]
        used_columns.add(unique_matches[0])
    else:
        return _ShareChangeColumnMapping(
            class_to_column=class_to_column,
            alignment_note=_SHARE_CHANGE_ALIGNMENT_EXPLICIT,
            na_reason=None,
        )

    signal_count = sum(
        1
        for _index, header in value_columns
        for class_label, fund_code in zip(mapping.class_labels, mapping.fund_codes, strict=True)
        if _header_has_explicit_share_class(header, class_label, fund_code)
    )
    if signal_count > 0:
        return _ShareChangeColumnMapping(
            class_to_column={},
            alignment_note=None,
            na_reason="share_class_column_alignment_ambiguous",
        )

    return _ShareChangeColumnMapping(
        class_to_column={
            class_label: column_index
            for class_label, (column_index, _header) in zip(mapping.class_labels, value_columns, strict=True)
        },
        alignment_note=_SHARE_CHANGE_ALIGNMENT_UNLABELED,
        na_reason=None,
    )


def _share_change_value_columns(table: ParsedTable) -> tuple[int, ...]:
    """识别 §10 份额变动表的类别值列。

    Args:
        table: §10 份额变动表。

    Returns:
        类别值列下标；首列行标签语义无法确认时返回空元组。

    Raises:
        无显式抛出。
    """

    if not table.headers:
        return ()
    if _parse_plain_decimal(table.headers[0]) is not None:
        return ()
    if not any(
        row
        and any(keyword in _compact_text(row[0]) for keyword in _SHARE_CHANGE_ROW_LABEL_KEYWORDS)
        for row in table.rows
    ):
        return ()
    return tuple(
        index
        for index, header in enumerate(table.headers)
        if index > 0 and not _is_total_share_header(header)
    )


def _normalized_header_text(header: str) -> str:
    """规范化表头文本以支持跨行份额类别匹配。

    Args:
        header: 原始表头。

    Returns:
        删除空白后的表头文本。

    Raises:
        无显式抛出。
    """

    return _compact_text(_normalize_cell(header))


def _header_has_explicit_share_class(header: str, class_label: str, fund_code: str) -> bool:
    """判断 §10 表头是否显式指向某个份额类别。

    Args:
        header: 规范化或原始表头。
        class_label: §2 份额类别。
        fund_code: §2 基金代码。

    Returns:
        表头包含基金代码或明确份额类别标签时返回 ``True``。

    Raises:
        无显式抛出。
    """

    compact_header = _compact_text(header)
    return fund_code in compact_header or _contains_share_class_label(compact_header, class_label)


def _share_class_ending_cross_check_from_profile_tables(
    tables: tuple[ParsedTable, ...],
    *,
    mapping: _ShareClassMapping,
    group_id: BondRiskEvidenceGroupId,
    excluded_table: ParsedTable,
) -> _ShareClassEndingCrossCheck | None:
    """从 §2 profile 同表三行读取份额类别期末份额交叉校验。

    Args:
        tables: 年报表格。
        mapping: §2 份额类别映射。
        group_id: 风险组 ID。
        excluded_table: 当前 §10 份额变动表，必须排除以避免自证。

    Returns:
        可证明 A/C/E/F 顺序的期末份额交叉校验；无法证明时返回 ``None``。

    Raises:
        无显式抛出。
    """

    excluded_identity = (excluded_table.page_number, excluded_table.table_index)
    for table in tables:
        if (table.page_number, table.table_index) == excluded_identity:
            continue
        row_matches = _profile_cross_check_rows(table)
        if row_matches is None:
            continue
        name_match, code_match, ending_match = row_matches
        name_index, name_row = name_match
        code_index, code_row = code_match
        ending_index, ending_row = ending_match
        class_labels = _share_class_labels_from_profile_name_cells(name_row)
        fund_codes = tuple(
            _normalize_cell(cell)
            for cell in code_row[1:]
            if re.fullmatch(r"\d{6}", _compact_text(cell))
        )
        if class_labels != mapping.class_labels or fund_codes != mapping.fund_codes:
            continue
        ending_values = _profile_ending_values_by_class(ending_row, mapping.class_labels)
        if ending_values is None:
            continue
        note = "; ".join(
            f"{class_label}={_format_decimal(ending_values[class_label])}"
            for class_label in mapping.class_labels
        )
        return _ShareClassEndingCrossCheck(
            ending_by_class=ending_values,
            source_anchor_draft=_AnchorDraft(
                group_id=group_id,
                section_id=_SECTION_PROFILE,
                page_number=table.page_number,
                table_id=_table_id(table),
                row_locator=f"rows:{name_index},{code_index},{ending_index}:share_class_ending_cross_check",
                evidence_role="share_class_ending_cross_check",
                note=_trim_note(note),
            ),
        )
    return None


def _profile_cross_check_rows(
    table: ParsedTable,
) -> tuple[
    tuple[int, tuple[str, ...]],
    tuple[int, tuple[str, ...]],
    tuple[int, tuple[str, ...]],
] | None:
    """定位同一 §2 profile 表内的简称、代码和期末份额三行。

    Args:
        table: 候选 profile 表。

    Returns:
        三行一基行号和行内容；三类行不齐全时返回 ``None``。

    Raises:
        无显式抛出。
    """

    name_match: tuple[int, tuple[str, ...]] | None = None
    code_match: tuple[int, tuple[str, ...]] | None = None
    ending_match: tuple[int, tuple[str, ...]] | None = None
    for row_index, row in enumerate(table.rows, start=1):
        if not row:
            continue
        row_label = _compact_text(row[0])
        if _PROFILE_CLASS_NAME_ROW_KEYWORD in row_label:
            name_match = (row_index, row)
        elif _PROFILE_CLASS_CODE_ROW_KEYWORD in row_label:
            code_match = (row_index, row)
        elif _PROFILE_CLASS_ENDING_ROW_KEYWORD in row_label:
            ending_match = (row_index, row)
    if name_match is None or code_match is None or ending_match is None:
        return None
    return name_match, code_match, ending_match


def _profile_ending_values_by_class(
    ending_row: tuple[str, ...],
    class_labels: tuple[str, ...],
) -> dict[str, Decimal] | None:
    """解析 §2 profile 期末份额行中的类别期末份额。

    Args:
        ending_row: ``报告期末下属分级基金的份额总额`` 行。
        class_labels: §2 份额类别顺序。

    Returns:
        类别到期末份额的映射；数量或解析失败时返回 ``None``。

    Raises:
        无显式抛出。
    """

    value_cells = ending_row[1 : 1 + len(class_labels)]
    if len(value_cells) != len(class_labels):
        return None
    ending_values: dict[str, Decimal] = {}
    for class_label, cell in zip(class_labels, value_cells, strict=True):
        parsed = _parse_share_decimal(cell)
        if parsed is None:
            return None
        ending_values[class_label] = parsed
    return ending_values


def _validate_share_class_ending_cross_check(
    class_changes: tuple[_ShareClassChange, ...],
    cross_check: _ShareClassEndingCrossCheck,
) -> str | None:
    """校验 §10 各类别期末份额与 §2 profile 期末份额一致。

    Args:
        class_changes: §10 份额变动计算结果。
        cross_check: §2 profile 期末份额交叉校验。

    Returns:
        通过时返回 ``None``；不一致时返回失败原因。

    Raises:
        无显式抛出。
    """

    for item in class_changes:
        expected_ending = cross_check.ending_by_class.get(item.class_label)
        if expected_ending is None:
            return "share_class_ending_cross_check_missing"
        if not _decimal_close(item.ending, expected_ending):
            return "share_class_ending_cross_check_mismatch"
    return None


def _find_share_change_rows(table: ParsedTable) -> _ShareChangeRows | None:
    """定位 §10 份额变动表的必需行。

    Args:
        table: §10 份额变动表。

    Returns:
        必需行定位结果；缺少任一必需行时返回 ``None``。

    Raises:
        无显式抛出。
    """

    beginning = _find_share_change_row(table, required_keywords=("期初", "基金份额总额"))
    subscription = _find_share_change_row(
        table,
        required_keywords=("申购",),
        preferred_keyword_groups=_SHARE_SUBSCRIPTION_KEYWORD_GROUPS,
        excluded_keywords=_SHARE_SUBSCRIPTION_EXCLUDED_KEYWORDS,
    )
    redemption = _find_share_change_row(
        table,
        required_keywords=("赎回",),
        preferred_keyword_groups=_SHARE_REDEMPTION_KEYWORD_GROUPS,
        excluded_keywords=_SHARE_REDEMPTION_EXCLUDED_KEYWORDS,
    )
    split = _find_share_change_row(table, required_keywords=("拆分",))
    ending = _find_share_change_row(table, required_keywords=("期末", "基金份额总额"))
    if beginning is None or subscription is None or redemption is None or ending is None:
        return None
    return _ShareChangeRows(
        beginning=beginning,
        subscription=subscription,
        redemption=redemption,
        split=split,
        ending=ending,
    )


def _find_share_change_row(
    table: ParsedTable,
    *,
    required_keywords: tuple[str, ...],
    preferred_keyword_groups: tuple[tuple[str, ...], ...] = (),
    excluded_keywords: tuple[str, ...] = (),
) -> tuple[int, tuple[str, ...]] | None:
    """按关键词定位 §10 份额变动表行。

    Args:
        table: §10 份额变动表。
        required_keywords: 行文本必须包含的关键词。
        preferred_keyword_groups: 优先命中的强语义关键词组。
        excluded_keywords: 不能命中的干扰关键词。

    Returns:
        一基行号和行内容；未命中返回 ``None``。

    Raises:
        无显式抛出。
    """

    matches = []
    for row_index, row in enumerate(table.rows, start=1):
        row_text = _compact_text(" ".join(row))
        if any(keyword in row_text for keyword in excluded_keywords):
            continue
        if all(keyword in row_text for keyword in required_keywords):
            matches.append((row_index, row, row_text))
    if preferred_keyword_groups:
        for row_index, row, row_text in matches:
            if any(all(keyword in row_text for keyword in keywords) for keywords in preferred_keyword_groups):
                return row_index, row
        return None
    if matches:
        row_index, row, _row_text = matches[0]
        return row_index, row
    return None


def _calculate_share_class_changes(
    rows: _ShareChangeRows,
    mapping: _ShareClassMapping,
    class_to_column: dict[str, int],
) -> tuple[_ShareClassChange, ...] | str:
    """计算 §10 各份额类别的份额变动并执行类别级对账。

    Args:
        rows: §10 份额变动行。
        mapping: §2 份额类别映射。
        class_to_column: 类别到列下标映射。

    Returns:
        成功时返回类别计算结果；失败时返回 ``na_reason`` 字符串。

    Raises:
        无显式抛出。
    """

    changes: list[_ShareClassChange] = []
    for class_label, fund_code in zip(mapping.class_labels, mapping.fund_codes, strict=True):
        column_index = class_to_column[class_label]
        parsed_values = _parse_share_change_values(rows, column_index)
        if isinstance(parsed_values, str):
            return parsed_values
        beginning, subscription, redemption, split, ending = parsed_values
        net_change = subscription - redemption + split
        if not _decimal_close(beginning + net_change, ending):
            return "share_change_arithmetic_mismatch"
        ratio = None if beginning == Decimal("0") else net_change / beginning
        changes.append(
            _ShareClassChange(
                class_label=class_label,
                fund_code=fund_code,
                beginning=beginning,
                subscription=subscription,
                redemption=redemption,
                split=split,
                ending=ending,
                net_change=net_change,
                net_change_ratio=ratio,
                note="class_beginning_zero" if beginning == Decimal("0") else None,
            )
        )
    return tuple(changes)


def _parse_share_change_values(
    rows: _ShareChangeRows,
    column_index: int,
) -> tuple[Decimal, Decimal, Decimal, Decimal, Decimal] | str:
    """解析单一类别的 §10 份额变动数值。

    Args:
        rows: §10 份额变动行。
        column_index: 当前类别值列下标。

    Returns:
        期初、申购、赎回、拆分、期末五元组；失败时返回 ``na_reason`` 字符串。

    Raises:
        无显式抛出。
    """

    row_values = (
        rows.beginning[1],
        rows.subscription[1],
        rows.redemption[1],
        rows.split[1] if rows.split is not None else None,
        rows.ending[1],
    )
    parsed: list[Decimal] = []
    for row in row_values:
        if row is None:
            parsed.append(Decimal("0"))
            continue
        if column_index >= len(row):
            return "share_class_column_count_mismatch"
        value = _parse_share_decimal(row[column_index])
        if value is None:
            return "non_parseable_share_value"
        parsed.append(value)
    return parsed[0], parsed[1], parsed[2], parsed[3], parsed[4]


def _share_change_row_anchor_drafts(
    table: ParsedTable,
    group_id: BondRiskEvidenceGroupId,
    rows: _ShareChangeRows,
) -> tuple[_AnchorDraft, ...]:
    """构造 §10 份额变动必需行级锚点。

    Args:
        table: §10 份额变动表。
        group_id: 风险组 ID。
        rows: §10 份额变动行定位。

    Returns:
        期初、申购、赎回、期末和可选拆分行锚点。

    Raises:
        无显式抛出。
    """

    row_specs = (
        ("share_beginning", rows.beginning),
        ("subscription", rows.subscription),
        ("redemption", rows.redemption),
        ("split_or_change", rows.split),
        ("share_ending", rows.ending),
    )
    drafts = []
    for evidence_role, row_match in row_specs:
        if row_match is None:
            continue
        row_index, row = row_match
        row_label = _normalize_cell(row[0]) if row else f"row-{row_index}"
        drafts.append(
            _AnchorDraft(
                group_id=group_id,
                section_id=_SECTION_SHARE_CHANGE,
                page_number=table.page_number,
                table_id=_table_id(table),
                row_locator=f"row:{row_index}:{row_label}",
                evidence_role=evidence_role,
                note=_format_row_note(row),
            )
        )
    return tuple(drafts)


def _format_share_change_metric(
    *,
    class_changes: tuple[_ShareClassChange, ...],
    aggregate_beginning: Decimal,
    aggregate_subscription: Decimal,
    aggregate_redemption: Decimal,
    aggregate_split: Decimal,
    aggregate_ending: Decimal,
    aggregate_net_change: Decimal,
    aggregate_net_change_ratio: Decimal,
    source_note: str,
    alignment_note: str | None,
) -> str:
    """格式化 A/C/E/F 全份额类别份额变动摘要。

    Args:
        class_changes: 类别级计算结果。
        aggregate_beginning: 全类别期初份额。
        aggregate_subscription: 全类别申购份额。
        aggregate_redemption: 全类别赎回份额。
        aggregate_split: 全类别拆分变动份额。
        aggregate_ending: 全类别期末份额。
        aggregate_net_change: 全类别净变动。
        aggregate_net_change_ratio: 全类别净变动比例。
        source_note: §2 映射来源说明。
        alignment_note: §10 列对齐方式说明。

    Returns:
        可写入 ``metric_value`` 的紧凑摘要。

    Raises:
        无显式抛出。
    """

    class_parts = []
    for item in class_changes:
        ratio = "None" if item.net_change_ratio is None else _format_decimal(item.net_change_ratio)
        note = f", note={item.note}" if item.note else ""
        class_parts.append(
            f"{item.class_label}(code={item.fund_code}, beginning={_format_decimal(item.beginning)}, "
            f"subscription={_format_decimal(item.subscription)}, redemption={_format_decimal(item.redemption)}, "
            f"split={_format_decimal(item.split)}, ending={_format_decimal(item.ending)}, "
            f"net_change={_format_decimal(item.net_change)}, net_change_ratio={ratio}{note})"
        )

    alignment_part = f"; column_alignment={alignment_note}" if alignment_note else ""
    metric = (
        "all_classes: "
        f"beginning={_format_decimal(aggregate_beginning)}, "
        f"subscription={_format_decimal(aggregate_subscription)}, "
        f"redemption={_format_decimal(aggregate_redemption)}, "
        f"split={_format_decimal(aggregate_split)}, "
        f"ending={_format_decimal(aggregate_ending)}, "
        f"net_change={_format_decimal(aggregate_net_change)}, "
        f"net_change_ratio={_format_decimal(aggregate_net_change_ratio)}; "
        f"{'; '.join(class_parts)}; mapping={source_note}"
        f"{alignment_part}"
    )
    return metric


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


def _parse_share_decimal(value: str) -> Decimal | None:
    """解析 §10 份额变动数值。

    Args:
        value: 原始份额数值。

    Returns:
        可解析时返回 ``Decimal``；不可解析时返回 ``None``。

    Raises:
        无显式抛出。
    """

    return _parse_plain_decimal(value, dash_as_zero=True)


def _parse_plain_decimal(value: str, *, dash_as_zero: bool = False) -> Decimal | None:
    """解析不含百分号的普通十进制数值。

    Args:
        value: 原始文本。
        dash_as_zero: 是否把横线变体解析为零。

    Returns:
        可解析时返回 ``Decimal``；不可解析时返回 ``None``。

    Raises:
        无显式抛出。
    """

    normalized = _compact_text(str(value)).replace(",", "")
    for suffix in _DECIMAL_UNIT_SUFFIXES:
        if normalized.endswith(suffix):
            normalized = normalized[: -len(suffix)]
            break
    if not normalized:
        return None
    if normalized in _DASH_ZERO_VALUES:
        return Decimal("0") if dash_as_zero else None
    if "%" in normalized:
        return None
    try:
        return Decimal(normalized)
    except InvalidOperation:
        return None


def _decimal_close(left: Decimal, right: Decimal) -> bool:
    """判断两个 Decimal 是否在份额对账容忍度内。

    Args:
        left: 左侧计算值。
        right: 右侧披露值。

    Returns:
        绝对差不超过 ``0.01`` 时返回 ``True``。

    Raises:
        无显式抛出。
    """

    return abs(left - right) <= _DECIMAL_TOLERANCE


def _format_decimal(value: Decimal) -> str:
    """格式化 Decimal，避免无意义的科学计数法和尾随零。

    Args:
        value: 待格式化数值。

    Returns:
        稳定文本表示。

    Raises:
        无显式抛出。
    """

    normalized = value.normalize()
    if normalized == normalized.to_integral():
        return str(normalized.quantize(Decimal("1")))
    return format(normalized, "f")


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
