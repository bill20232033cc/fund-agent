"""基金 extractor 数据模型。"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Generic, Literal, TypeVar

ExtractedValueT = TypeVar("ExtractedValueT")
ExtractionMode = Literal["direct", "derived", "estimated", "missing"]
EvidenceSourceKind = Literal["annual_report", "external_api", "derived"]
BondRiskEvidenceStatus = Literal["accepted", "accepted_absence", "weak", "ambiguous", "missing"]
BondRiskEvidenceStrength = Literal[
    "quantitative_direct",
    "quantitative_absence",
    "qualitative_direct",
    "qualitative_control_intent",
    "ambiguous",
    "missing",
]
BondRiskEvidenceGroupId = Literal[
    "duration_rate_risk",
    "credit_risk",
    "leverage_liquidity",
    "asset_allocation_holdings_mix",
    "drawdown_stress",
    "redemption_share_pressure",
    "convertible_bond_equity_exposure",
]
BondRiskEvidenceMeasurementKind = Literal[
    "actual_metric",
    "actual_exposure",
    "explicit_absence",
    "risk_disclosure",
    "strategy_text",
    "control_intent",
    "not_found",
]
BondRiskEvidenceContractStatus = Literal["satisfied", "partial", "missing"]
BondRiskEvidenceSchemaVersion = Literal["bond_risk_evidence.v1"]

BOND_RISK_EVIDENCE_CONTRACT_ID: BondRiskEvidenceSchemaVersion = "bond_risk_evidence.v1"
BOND_RISK_EVIDENCE_GROUP_IDS: tuple[BondRiskEvidenceGroupId, ...] = (
    "duration_rate_risk",
    "credit_risk",
    "leverage_liquidity",
    "asset_allocation_holdings_mix",
    "drawdown_stress",
    "redemption_share_pressure",
    "convertible_bond_equity_exposure",
)

_BOND_RISK_EVIDENCE_STATUSES = frozenset(
    ("accepted", "accepted_absence", "weak", "ambiguous", "missing")
)
_BOND_RISK_EVIDENCE_STRENGTHS = frozenset(
    (
        "quantitative_direct",
        "quantitative_absence",
        "qualitative_direct",
        "qualitative_control_intent",
        "ambiguous",
        "missing",
    )
)
_BOND_RISK_EVIDENCE_MEASUREMENT_KINDS = frozenset(
    (
        "actual_metric",
        "actual_exposure",
        "explicit_absence",
        "risk_disclosure",
        "strategy_text",
        "control_intent",
        "not_found",
    )
)
_BOND_RISK_ACCEPTED_STRENGTHS = frozenset(("quantitative_direct", "qualitative_direct"))
_BOND_RISK_ACCEPTED_ANCHORED_STATUSES = frozenset(("accepted", "accepted_absence", "weak"))


@dataclass(frozen=True, slots=True)
class EvidenceAnchor:
    """证据锚点。

    Attributes:
        source_kind: 证据来源类型。
        document_year: 文档年份；非文档来源时可为 `None`。
        section_id: 年报章节编号。
        page_number: 页码；当前 `§1/§2` 文本抽取阶段可为 `None`。
        table_id: 表格标识；当前文本抽取阶段可为 `None`。
        row_locator: 行级定位说明。
        note: 附加说明，通常记录命中的原始行文本。
    """

    source_kind: EvidenceSourceKind
    document_year: int | None
    section_id: str | None
    page_number: int | None
    table_id: str | None
    row_locator: str | None
    note: str | None


@dataclass(frozen=True, slots=True)
class BondRiskEvidenceAnchorRef:
    """债券风险证据组级锚点引用，见模板第 6 章“核心风险”。

    Attributes:
        anchor_id: 稳定锚点 ID，格式为 `bond-risk:<fund_code>:<report_year>:<group_id>:<ordinal>`。
        section_id: 年报章节编号。
        page_number: 年报页码；文本来源无法确定时可为 `None`。
        table_id: 表格标识；非表格文本证据可为 `None`。
        row_locator: 行级或段落级定位说明。
        evidence_role: 证据在风险组内承担的角色。
    """

    anchor_id: str
    section_id: str
    page_number: int | None
    table_id: str | None
    row_locator: str
    evidence_role: str


@dataclass(frozen=True, slots=True)
class BondRiskEvidenceGroupRecord:
    """债券基金模板第 6 章“核心风险”的单个风险组证据记录。

    Attributes:
        group_id: 七个债券风险证据组之一。
        status: 该组证据状态；只有 `accepted` 与 `accepted_absence` 可满足组要求。
        strength: 证据强度，区分定量、定性、控制意图、歧义和缺失。
        summary: 证据摘要，禁止替代锚点本身。
        measurement_kind: 度量或披露类型。
        metric_name: 指标名称；非指标证据可为 `None`。
        metric_value: 指标值原文；非指标证据可为 `None`。
        metric_unit: 指标单位；非指标证据可为 `None`。
        period_label: 指标或披露对应期间。
        source_anchor_ids: 关联的组级锚点 ID。
        na_reason: 缺失、不适用或未满足原因。
        reviewer_note: 人工复核说明。
    """

    group_id: BondRiskEvidenceGroupId
    status: BondRiskEvidenceStatus
    strength: BondRiskEvidenceStrength
    summary: str
    measurement_kind: BondRiskEvidenceMeasurementKind
    metric_name: str | None
    metric_value: str | None
    metric_unit: str | None
    period_label: str | None
    source_anchor_ids: tuple[str, ...]
    na_reason: str | None
    reviewer_note: str | None


@dataclass(frozen=True, slots=True)
class BondRiskEvidenceValue:
    """债券风险证据契约值，见模板第 6 章“核心风险”。

    该结构只表达年报中可追溯的债券风险证据状态，不降低 FQ0-FQ6
    门槛，也不把弱证据或歧义证据静默提升为通过。

    Attributes:
        schema_version: 当前固定为 `bond_risk_evidence.v1`。
        contract_id: 当前固定为 `bond_risk_evidence.v1`。
        fund_code: 6 位基金代码。
        report_year: 年报年份。
        groups: 七个债券风险证据组记录。
        anchors: 可被组记录引用的稳定组级锚点。
        satisfied_group_ids: 已满足组 ID，必须由 `accepted` / `accepted_absence` 状态派生。
        missing_group_ids: 缺失组 ID，必须由 `missing` 状态派生。
        weak_group_ids: 弱证据组 ID，必须由 `weak` 状态派生。
        ambiguous_group_ids: 歧义组 ID，必须由 `ambiguous` 状态派生。
        contract_status: 整体契约状态。
    """

    schema_version: BondRiskEvidenceSchemaVersion
    contract_id: BondRiskEvidenceSchemaVersion
    fund_code: str
    report_year: int
    groups: tuple[BondRiskEvidenceGroupRecord, ...]
    anchors: tuple[BondRiskEvidenceAnchorRef, ...]
    satisfied_group_ids: tuple[BondRiskEvidenceGroupId, ...]
    missing_group_ids: tuple[BondRiskEvidenceGroupId, ...]
    weak_group_ids: tuple[BondRiskEvidenceGroupId, ...]
    ambiguous_group_ids: tuple[BondRiskEvidenceGroupId, ...]
    contract_status: BondRiskEvidenceContractStatus


def validate_bond_risk_evidence_value(value: BondRiskEvidenceValue) -> None:
    """校验债券风险证据契约值，见模板第 6 章“核心风险”。

    Args:
        value: 待校验的 `bond_risk_evidence.v1` 结构化值。

    Returns:
        校验通过时返回 `None`。

    Raises:
        ValueError: 当 schema、七组完整性、锚点引用、派生组 ID 或整体状态不一致时抛出。
    """

    if value.schema_version != BOND_RISK_EVIDENCE_CONTRACT_ID:
        raise ValueError("bond_risk_evidence schema_version 必须是 bond_risk_evidence.v1")
    if value.contract_id != BOND_RISK_EVIDENCE_CONTRACT_ID:
        raise ValueError("bond_risk_evidence contract_id 必须是 bond_risk_evidence.v1")
    if not value.fund_code:
        raise ValueError("bond_risk_evidence fund_code 不能为空")
    if value.report_year <= 0:
        raise ValueError("bond_risk_evidence report_year 必须为正整数")

    _validate_bond_risk_group_records(value.groups)
    anchor_ids = _validate_bond_risk_anchor_refs(value)

    for group in value.groups:
        _validate_bond_risk_group_anchor_refs(group, anchor_ids, value.fund_code, value.report_year)

    satisfied_ids, missing_ids, weak_ids, ambiguous_ids = _derive_bond_risk_group_id_sets(value.groups)
    _require_same_group_ids("satisfied_group_ids", value.satisfied_group_ids, satisfied_ids)
    _require_same_group_ids("missing_group_ids", value.missing_group_ids, missing_ids)
    _require_same_group_ids("weak_group_ids", value.weak_group_ids, weak_ids)
    _require_same_group_ids("ambiguous_group_ids", value.ambiguous_group_ids, ambiguous_ids)

    expected_contract_status = _derive_bond_risk_contract_status(
        satisfied_ids=satisfied_ids,
        missing_ids=missing_ids,
        weak_ids=weak_ids,
        ambiguous_ids=ambiguous_ids,
    )
    if value.contract_status != expected_contract_status:
        raise ValueError(
            "bond_risk_evidence contract_status 与组状态不一致："
            f"expected={expected_contract_status}, actual={value.contract_status}"
        )


def _validate_bond_risk_group_records(groups: tuple[BondRiskEvidenceGroupRecord, ...]) -> None:
    """校验模板第 6 章七个债券风险组记录完整性。

    Args:
        groups: 债券风险证据组记录。

    Returns:
        校验通过时返回 `None`。

    Raises:
        ValueError: 当组数量、组 ID 或组内状态字段非法时抛出。
    """

    group_ids = tuple(group.group_id for group in groups)
    if len(group_ids) != len(BOND_RISK_EVIDENCE_GROUP_IDS):
        raise ValueError("bond_risk_evidence 必须恰好包含七个风险证据组")
    if len(set(group_ids)) != len(group_ids):
        raise ValueError("bond_risk_evidence group_id 不允许重复")
    if set(group_ids) != set(BOND_RISK_EVIDENCE_GROUP_IDS):
        raise ValueError("bond_risk_evidence group_id 必须匹配七个必需风险证据组")

    for group in groups:
        if group.status not in _BOND_RISK_EVIDENCE_STATUSES:
            raise ValueError(f"bond_risk_evidence status 不受支持：{group.status}")
        if group.strength not in _BOND_RISK_EVIDENCE_STRENGTHS:
            raise ValueError(f"bond_risk_evidence strength 不受支持：{group.strength}")
        if group.measurement_kind not in _BOND_RISK_EVIDENCE_MEASUREMENT_KINDS:
            raise ValueError(f"bond_risk_evidence measurement_kind 不受支持：{group.measurement_kind}")
        if not group.summary:
            raise ValueError(f"bond_risk_evidence {group.group_id} summary 不能为空")
        _validate_bond_risk_status_strength(group)


def _validate_bond_risk_status_strength(group: BondRiskEvidenceGroupRecord) -> None:
    """校验模板第 6 章单组状态与证据强度兼容性。

    Args:
        group: 单个债券风险证据组记录。

    Returns:
        校验通过时返回 `None`。

    Raises:
        ValueError: 当状态与强度组合会错误提升或弱化证据时抛出。
    """

    if group.status == "accepted" and group.strength not in _BOND_RISK_ACCEPTED_STRENGTHS:
        raise ValueError(f"bond_risk_evidence {group.group_id} accepted 强度不兼容")
    if group.status == "accepted_absence":
        if group.strength != "quantitative_absence" or group.measurement_kind != "explicit_absence":
            raise ValueError(f"bond_risk_evidence {group.group_id} accepted_absence 必须是显式定量缺席")
    if group.status == "weak" and group.strength not in {
        "qualitative_direct",
        "qualitative_control_intent",
        "ambiguous",
    }:
        raise ValueError(f"bond_risk_evidence {group.group_id} weak 强度不兼容")
    if group.status == "ambiguous" and group.strength != "ambiguous":
        raise ValueError(f"bond_risk_evidence {group.group_id} ambiguous 必须使用 ambiguous 强度")
    if group.status == "missing" and group.strength != "missing":
        raise ValueError(f"bond_risk_evidence {group.group_id} missing 必须使用 missing 强度")


def _validate_bond_risk_anchor_refs(value: BondRiskEvidenceValue) -> frozenset[str]:
    """校验模板第 6 章组级锚点唯一性与基础字段。

    Args:
        value: 债券风险证据契约值。

    Returns:
        可被组记录引用的锚点 ID 集合。

    Raises:
        ValueError: 当锚点重复、格式错误或缺少定位字段时抛出。
    """

    anchor_ids: set[str] = set()
    for anchor in value.anchors:
        if not anchor.anchor_id:
            raise ValueError("bond_risk_evidence anchor_id 不能为空")
        if anchor.anchor_id in anchor_ids:
            raise ValueError(f"bond_risk_evidence anchor_id 重复：{anchor.anchor_id}")
        anchor_ids.add(anchor.anchor_id)

        group_id = _parse_bond_risk_anchor_id(anchor.anchor_id, value.fund_code, value.report_year)
        if group_id not in BOND_RISK_EVIDENCE_GROUP_IDS:
            raise ValueError(f"bond_risk_evidence anchor_id 包含未知 group_id：{group_id}")
        if not anchor.section_id:
            raise ValueError(f"bond_risk_evidence {anchor.anchor_id} section_id 不能为空")
        if not anchor.row_locator:
            raise ValueError(f"bond_risk_evidence {anchor.anchor_id} row_locator 不能为空")
        if not anchor.evidence_role:
            raise ValueError(f"bond_risk_evidence {anchor.anchor_id} evidence_role 不能为空")

    return frozenset(anchor_ids)


def _parse_bond_risk_anchor_id(anchor_id: str, fund_code: str, report_year: int) -> str:
    """解析模板第 6 章债券风险稳定锚点 ID。

    Args:
        anchor_id: 稳定组级锚点 ID。
        fund_code: 当前契约基金代码。
        report_year: 当前契约年报年份。

    Returns:
        锚点所属风险组 ID。

    Raises:
        ValueError: 当锚点格式、基金代码、年份或序号不匹配时抛出。
    """

    parts = anchor_id.split(":")
    if len(parts) != 5 or parts[0] != "bond-risk":
        raise ValueError(f"bond_risk_evidence anchor_id 格式错误：{anchor_id}")
    _, anchor_fund_code, anchor_year, group_id, ordinal = parts
    if anchor_fund_code != fund_code:
        raise ValueError(f"bond_risk_evidence anchor_id 基金代码不匹配：{anchor_id}")
    if anchor_year != str(report_year):
        raise ValueError(f"bond_risk_evidence anchor_id 年份不匹配：{anchor_id}")
    if not ordinal.isdigit() or int(ordinal) <= 0:
        raise ValueError(f"bond_risk_evidence anchor_id 序号必须为正整数：{anchor_id}")
    return group_id


def _validate_bond_risk_group_anchor_refs(
    group: BondRiskEvidenceGroupRecord,
    anchor_ids: frozenset[str],
    fund_code: str,
    report_year: int,
) -> None:
    """校验模板第 6 章单组记录对锚点的引用。

    Args:
        group: 单个债券风险证据组记录。
        anchor_ids: 当前契约内可解析的锚点 ID 集合。
        fund_code: 当前契约基金代码。
        report_year: 当前契约年报年份。

    Returns:
        校验通过时返回 `None`。

    Raises:
        ValueError: 当 accepted/weak 记录无锚点或引用不存在锚点时抛出。
    """

    if group.status in _BOND_RISK_ACCEPTED_ANCHORED_STATUSES and not group.source_anchor_ids:
        raise ValueError(f"bond_risk_evidence {group.group_id} 需要至少一个可解析年报锚点")

    for anchor_id in group.source_anchor_ids:
        if anchor_id not in anchor_ids:
            raise ValueError(f"bond_risk_evidence {group.group_id} 引用缺失锚点：{anchor_id}")
        anchor_group_id = _parse_bond_risk_anchor_id(anchor_id, fund_code, report_year)
        if anchor_group_id and anchor_group_id != group.group_id:
            raise ValueError(f"bond_risk_evidence {group.group_id} 引用其他风险组锚点：{anchor_id}")


def _derive_bond_risk_group_id_sets(
    groups: tuple[BondRiskEvidenceGroupRecord, ...],
) -> tuple[
    tuple[BondRiskEvidenceGroupId, ...],
    tuple[BondRiskEvidenceGroupId, ...],
    tuple[BondRiskEvidenceGroupId, ...],
    tuple[BondRiskEvidenceGroupId, ...],
]:
    """从模板第 6 章组状态派生满足、缺失、弱证据和歧义组。

    Args:
        groups: 债券风险证据组记录。

    Returns:
        依次返回满足组、缺失组、弱证据组、歧义组。
    """

    by_id = {group.group_id: group for group in groups}
    satisfied_ids: list[BondRiskEvidenceGroupId] = []
    missing_ids: list[BondRiskEvidenceGroupId] = []
    weak_ids: list[BondRiskEvidenceGroupId] = []
    ambiguous_ids: list[BondRiskEvidenceGroupId] = []

    for group_id in BOND_RISK_EVIDENCE_GROUP_IDS:
        group = by_id[group_id]
        if group.status in {"accepted", "accepted_absence"}:
            satisfied_ids.append(group_id)
        elif group.status == "missing":
            missing_ids.append(group_id)
        elif group.status == "weak":
            weak_ids.append(group_id)
        elif group.status == "ambiguous":
            ambiguous_ids.append(group_id)

    return tuple(satisfied_ids), tuple(missing_ids), tuple(weak_ids), tuple(ambiguous_ids)


def _require_same_group_ids(
    field_name: str,
    actual: tuple[BondRiskEvidenceGroupId, ...],
    expected: tuple[BondRiskEvidenceGroupId, ...],
) -> None:
    """校验模板第 6 章派生组 ID 字段未被调用方篡改。

    Args:
        field_name: 被校验字段名。
        actual: 调用方提供的组 ID。
        expected: 由组状态派生的组 ID。

    Returns:
        校验通过时返回 `None`。

    Raises:
        ValueError: 当调用方提供值与派生值不一致时抛出。
    """

    if actual != expected:
        raise ValueError(
            f"bond_risk_evidence {field_name} 与组状态不一致："
            f"expected={expected}, actual={actual}"
        )


def _derive_bond_risk_contract_status(
    *,
    satisfied_ids: tuple[BondRiskEvidenceGroupId, ...],
    missing_ids: tuple[BondRiskEvidenceGroupId, ...],
    weak_ids: tuple[BondRiskEvidenceGroupId, ...],
    ambiguous_ids: tuple[BondRiskEvidenceGroupId, ...],
) -> BondRiskEvidenceContractStatus:
    """从模板第 6 章风险组状态派生整体契约状态。

    Args:
        satisfied_ids: 已满足组 ID。
        missing_ids: 缺失组 ID。
        weak_ids: 弱证据组 ID。
        ambiguous_ids: 歧义组 ID。

    Returns:
        `satisfied`、`partial` 或 `missing`。
    """

    if len(satisfied_ids) == len(BOND_RISK_EVIDENCE_GROUP_IDS):
        return "satisfied"
    if satisfied_ids or weak_ids or ambiguous_ids:
        return "partial"
    if missing_ids:
        return "missing"
    return "missing"


@dataclass(frozen=True, slots=True)
class ExtractedField(Generic[ExtractedValueT]):
    """带证据的抽取字段。

    Attributes:
        value: 抽取到的结构化值；缺失时可为 `None`。
        anchors: 证据锚点列表。
        extraction_mode: 抽取模式。
        note: 附加说明。
    """

    value: ExtractedValueT | None
    anchors: tuple[EvidenceAnchor, ...]
    extraction_mode: ExtractionMode
    note: str | None = None


@dataclass(frozen=True, slots=True)
class ProfileExtractionResult:
    """基础画像抽取结果。

    Attributes:
        basic_identity: 基础身份信息。
        product_profile: 产品本质与投资范围摘要。
        benchmark: 业绩比较基准信息。
        index_profile: 指数画像信息，见模板第 1 章“指数编制规则与成分股”。
        fee_schedule: 费率信息。
    """

    basic_identity: ExtractedField[dict[str, object]]
    product_profile: ExtractedField[dict[str, object]]
    benchmark: ExtractedField[dict[str, object]]
    index_profile: ExtractedField["IndexProfileValue"]
    fee_schedule: ExtractedField[dict[str, object]]


@dataclass(frozen=True, slots=True)
class PerformanceExtractionResult:
    """`§3` 表现抽取结果。

    Attributes:
        nav_benchmark_performance: 净值增长率与业绩基准收益率。
        investor_return: 投资者收益率披露或 fallback 状态。
        tracking_error: 年报直接披露的跟踪误差，见模板第 2 章 R=A+B-C。
    """

    nav_benchmark_performance: ExtractedField[dict[str, object]]
    investor_return: ExtractedField[dict[str, object]]
    tracking_error: ExtractedField["TrackingErrorValue"]


@dataclass(frozen=True, slots=True)
class IndexProfileValue:
    """指数画像结构化值，见模板第 1 章“这只基金到底是什么产品”。

    Attributes:
        benchmark_text: 年报披露的业绩比较基准文本。
        benchmark_identity_status: 基准身份识别状态。
        benchmark_index_name: 可确定的单一指数名称。
        benchmark_index_code: 可确定的指数代码；禁止从基金代码猜测。
        benchmark_component_text: 复合基准组成文本。
        methodology_availability: 编制方法可用性层级。
        methodology_summary: 编制方法摘要。
        methodology_source_title: 编制方法来源标题。
        constituents_availability: 成分股可用性层级。
        constituents_summary: 成分股摘要。
        constituents_as_of_date: 成分股日期。
        source_tier: 当前画像来源层级。
        missing_reasons: 缺失或不可用原因。
    """

    benchmark_text: str | None
    benchmark_identity_status: Literal["identified", "composite", "ambiguous", "missing"]
    benchmark_index_name: str | None
    benchmark_index_code: str | None
    benchmark_component_text: tuple[str, ...]
    methodology_availability: Literal[
        "direct_disclosure",
        "source_reference",
        "benchmark_only",
        "missing",
    ]
    methodology_summary: str | None
    methodology_source_title: str | None
    constituents_availability: Literal[
        "direct_disclosure",
        "source_reference",
        "benchmark_only",
        "missing",
    ]
    constituents_summary: str | None
    constituents_as_of_date: str | None
    source_tier: Literal["annual_report", "prospectus", "index_document", "benchmark_context", "missing"]
    missing_reasons: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class TrackingErrorValue:
    """跟踪误差结构化值，见模板第 2 章 R=A+B-C。

    Attributes:
        value: 标准化小数比例，例如 `0.015` 表示 `1.5%`。
        value_text: 年报披露原文数值。
        unit: 数值单位，当前固定为比例。
        period_label: 跟踪误差对应期间。
        period_start: 期间开始日期；直接披露无法确定时为 `None`。
        period_end: 期间结束日期；直接披露无法确定时为 `None`。
        annualized: 是否年化。
        source_type: 来源类型。
        calculation_method: 计算或披露方法。
        benchmark_identity_status: 基准身份识别状态。
        benchmark_index_name: 可确定的单一指数名称。
        benchmark_index_code: 可确定的指数代码。
        fund_series_source: 基金序列来源；直接披露为 `None`。
        index_series_source: 指数序列来源；直接披露为 `None`。
        observation_count: 观测数量；直接披露为 `None`。
        frequency: 数据频率。
        annualization_factor: 年化因子；直接披露为 `None`。
        input_period_complete: 输入期间是否完整。
        provenance_note: 来源和证据边界说明。
    """

    value: Decimal
    value_text: str
    unit: Literal["ratio"]
    period_label: str
    period_start: str | None
    period_end: str | None
    annualized: bool
    source_type: Literal["direct_disclosure", "calculated_from_series"]
    calculation_method: Literal["disclosed", "annualized_stddev_active_return"]
    benchmark_identity_status: Literal["identified", "composite", "ambiguous", "missing"]
    benchmark_index_name: str | None
    benchmark_index_code: str | None
    fund_series_source: str | None
    index_series_source: str | None
    observation_count: int | None
    frequency: Literal["daily", "weekly", "monthly", "annual_report_period"]
    annualization_factor: Decimal | None
    input_period_complete: bool
    provenance_note: str


@dataclass(frozen=True, slots=True)
class ManagerOwnershipExtractionResult:
    """`§4/§8/§9` 管理人文本、换手率、利益一致性与持有人结构抽取结果。

    Attributes:
        manager_strategy_text: 管理人报告中的策略与展望原文。
        turnover_rate: 年报 `§8` 披露的换手率。
        manager_alignment: 年报 `§9` 披露的基金经理/从业人员持有原始数据。
        holder_structure: 年报 `§9` 披露的机构/个人持有人结构。
    """

    manager_strategy_text: ExtractedField[dict[str, object]]
    turnover_rate: ExtractedField[dict[str, object]]
    manager_alignment: ExtractedField[dict[str, object]]
    holder_structure: ExtractedField[dict[str, object]]


@dataclass(frozen=True, slots=True)
class HoldingsShareChangeExtractionResult:
    """`§8/§10` 持仓快照与份额变动抽取结果。

    Attributes:
        holdings_snapshot: 前十大重仓与行业分布原始披露。
        share_change: 期初份额、期末份额和净变动原始披露。
    """

    holdings_snapshot: ExtractedField[dict[str, object]]
    share_change: ExtractedField[dict[str, object]]
