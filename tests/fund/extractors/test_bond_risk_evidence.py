"""债券风险证据模型契约测试。"""

from __future__ import annotations

from dataclasses import replace

import pytest

import fund_agent.fund.extractors.bond_risk_evidence as bond_risk_module
from fund_agent.fund.documents.models import DocumentKey, ParsedAnnualReport, ParsedTable, ReportSection
from fund_agent.fund.extractors.bond_risk_evidence import extract_bond_risk_evidence
from fund_agent.fund.extractors.models import (
    BOND_RISK_EVIDENCE_CONTRACT_ID,
    BOND_RISK_EVIDENCE_GROUP_IDS,
    BondRiskEvidenceAnchorRef,
    BondRiskEvidenceGroupId,
    BondRiskEvidenceGroupRecord,
    BondRiskEvidenceValue,
    validate_bond_risk_evidence_value,
)


def test_complete_seven_group_bond_risk_evidence_value_validates() -> None:
    """完整七组债券风险证据值应通过模板第 6 章契约校验。"""

    value = _complete_value()

    validate_bond_risk_evidence_value(value)

    assert value.satisfied_group_ids == BOND_RISK_EVIDENCE_GROUP_IDS
    assert value.missing_group_ids == ()
    assert value.weak_group_ids == ()
    assert value.ambiguous_group_ids == ()
    assert value.contract_status == "satisfied"


def test_missing_anchor_for_accepted_group_fails_validation() -> None:
    """accepted 组缺少可解析年报锚点时必须失败。"""

    value = _complete_value()
    broken_group = replace(value.groups[0], source_anchor_ids=("missing-anchor",))
    broken_value = replace(value, groups=(broken_group, *value.groups[1:]))

    with pytest.raises(ValueError, match="引用缺失锚点"):
        validate_bond_risk_evidence_value(broken_value)


def test_incomplete_group_set_fails_validation() -> None:
    """风险组不是恰好七组时必须失败。"""

    value = _complete_value()
    broken_value = replace(value, groups=value.groups[:-1])

    with pytest.raises(ValueError, match="恰好包含七个"):
        validate_bond_risk_evidence_value(broken_value)


def test_duplicate_group_id_fails_validation() -> None:
    """模板第 6 章风险组 ID 重复时必须失败。"""

    value = _complete_value()
    duplicate_group = replace(value.groups[1], group_id=value.groups[0].group_id)
    broken_value = replace(value, groups=(value.groups[0], duplicate_group, *value.groups[2:]))

    with pytest.raises(ValueError, match="group_id 不允许重复"):
        validate_bond_risk_evidence_value(broken_value)


def test_caller_provided_derived_group_ids_must_match_statuses() -> None:
    """派生组 ID 与状态不一致时必须拒绝调用方提供值。"""

    value = _complete_value()
    broken_value = replace(value, satisfied_group_ids=value.satisfied_group_ids[:-1])

    with pytest.raises(ValueError, match="satisfied_group_ids 与组状态不一致"):
        validate_bond_risk_evidence_value(broken_value)


def test_caller_provided_weak_group_ids_must_match_statuses() -> None:
    """weak_group_ids 与状态不一致时必须拒绝调用方提供值。"""

    value = _complete_value(
        overrides={
            "drawdown_stress": _group_record(
                "drawdown_stress",
                status="weak",
                strength="qualitative_control_intent",
                measurement_kind="control_intent",
            )
        }
    )
    broken_value = replace(value, weak_group_ids=())

    with pytest.raises(ValueError, match="weak_group_ids 与组状态不一致"):
        validate_bond_risk_evidence_value(broken_value)


def test_caller_provided_ambiguous_group_ids_must_match_statuses() -> None:
    """ambiguous_group_ids 与状态不一致时必须拒绝调用方提供值。"""

    value = _complete_value(
        overrides={
            "credit_risk": _group_record(
                "credit_risk",
                status="ambiguous",
                strength="ambiguous",
                measurement_kind="risk_disclosure",
            )
        }
    )
    broken_value = replace(value, ambiguous_group_ids=())

    with pytest.raises(ValueError, match="ambiguous_group_ids 与组状态不一致"):
        validate_bond_risk_evidence_value(broken_value)


def test_cross_group_anchor_reference_fails_validation() -> None:
    """风险组引用其他组锚点时必须失败。"""

    value = _complete_value()
    source_group = value.groups[0]
    other_group = value.groups[1]
    broken_group = replace(source_group, source_anchor_ids=other_group.source_anchor_ids)
    broken_value = replace(value, groups=(broken_group, *value.groups[1:]))

    with pytest.raises(ValueError, match="引用其他风险组锚点"):
        validate_bond_risk_evidence_value(broken_value)


@pytest.mark.parametrize(
    ("anchor_id", "message"),
    (
        ("bond-risk:006597:2024:duration_rate_risk", "anchor_id 格式错误"),
        ("bond-risk:000000:2024:duration_rate_risk:1", "anchor_id 基金代码不匹配"),
        ("bond-risk:006597:2023:duration_rate_risk:1", "anchor_id 年份不匹配"),
    ),
)
def test_malformed_or_wrong_anchor_id_fails_validation(anchor_id: str, message: str) -> None:
    """格式错误或归属不匹配的锚点 ID 必须失败。"""

    value = _complete_value()
    broken_anchor = replace(value.anchors[0], anchor_id=anchor_id)
    broken_value = replace(value, anchors=(broken_anchor, *value.anchors[1:]))

    with pytest.raises(ValueError, match=message):
        validate_bond_risk_evidence_value(broken_value)


def test_invalid_status_fails_validation() -> None:
    """不支持的模板第 6 章证据状态必须失败。"""

    value = _complete_value()
    broken_group = replace(value.groups[0], status="unsupported_status")
    broken_value = replace(value, groups=(broken_group, *value.groups[1:]))

    with pytest.raises(ValueError, match="status 不受支持"):
        validate_bond_risk_evidence_value(broken_value)


def test_invalid_strength_fails_validation() -> None:
    """不支持的模板第 6 章证据强度必须失败。"""

    value = _complete_value()
    broken_group = replace(value.groups[0], strength="unsupported_strength")
    broken_value = replace(value, groups=(broken_group, *value.groups[1:]))

    with pytest.raises(ValueError, match="strength 不受支持"):
        validate_bond_risk_evidence_value(broken_value)


def test_weak_drawdown_control_record_validates_but_is_unsatisfied() -> None:
    """回撤控制意图只能作为弱证据，不能进入 satisfied 组。"""

    value = _complete_value(
        overrides={
            "drawdown_stress": _group_record(
                "drawdown_stress",
                status="weak",
                strength="qualitative_control_intent",
                measurement_kind="control_intent",
            )
        }
    )

    validate_bond_risk_evidence_value(value)

    assert "drawdown_stress" not in value.satisfied_group_ids
    assert value.weak_group_ids == ("drawdown_stress",)
    assert value.contract_status == "partial"


def test_explicit_absence_convertible_equity_record_is_accepted() -> None:
    """可转债和权益暴露显式缺席可作为 accepted_absence 正向证据。"""

    value = _complete_value()
    group = _group_by_id(value, "convertible_bond_equity_exposure")

    validate_bond_risk_evidence_value(value)

    assert group.status == "accepted_absence"
    assert group.strength == "quantitative_absence"
    assert group.measurement_kind == "explicit_absence"
    assert "convertible_bond_equity_exposure" in value.satisfied_group_ids


def test_table_backed_credit_risk_is_accepted_with_row_level_anchor() -> None:
    """信用评级表格行应形成模板第 6 章信用风险 accepted 证据。"""

    report = _build_report(
        raw_text=_base_bond_raw_text(),
        tables=(
            ParsedTable(
                page_number=53,
                table_index=0,
                headers=("信用评级", "占基金资产净值比例"),
                rows=(("AAA 信用评级债券", "80.00%"),),
            ),
        ),
    )

    field = extract_bond_risk_evidence(report, "bond_fund")
    assert field.value is not None
    group = _group_by_id(field.value, "credit_risk")

    assert group.status == "accepted"
    assert group.strength == "quantitative_direct"
    assert group.measurement_kind == "actual_exposure"
    assert group.source_anchor_ids == ("bond-risk:006597:2024:credit_risk:1",)
    anchor = _anchor_ref_by_id(field.value, group.source_anchor_ids[0])
    assert anchor.table_id == "page-53-table-0"
    assert anchor.row_locator.startswith("row:1:")


def test_flexible_leverage_strategy_text_alone_is_weak() -> None:
    """杠杆策略文本没有回购/融资行时只能作为弱证据。"""

    report = _build_report(
        raw_text=_base_bond_raw_text(
            section_four_extra="本基金报告期内灵活运用杠杆策略，注重组合收益弹性。",
        ),
        tables=(),
    )

    field = extract_bond_risk_evidence(report, "bond_fund")
    assert field.value is not None
    group = _group_by_id(field.value, "leverage_liquidity")

    assert group.status == "weak"
    assert group.strength == "qualitative_direct"
    assert group.na_reason == "repo_or_liquidity_table_not_found"
    assert "leverage_liquidity" in field.value.weak_group_ids
    assert "leverage_liquidity" not in field.value.satisfied_group_ids


def test_repo_table_row_plus_liquidity_text_satisfies_leverage_liquidity() -> None:
    """回购表格行配合流动性风险文本可满足模板第 6 章杠杆/流动性组。"""

    report = _build_report(
        raw_text=_base_bond_raw_text(section_four_extra="管理人严格控制流动性风险，保持组合流动性。"),
        tables=(
            ParsedTable(
                page_number=59,
                table_index=1,
                headers=("项目", "金额"),
                rows=(("买入返售金融资产-回购", "10,000,000.00"),),
            ),
        ),
    )

    field = extract_bond_risk_evidence(report, "bond_fund")
    assert field.value is not None
    group = _group_by_id(field.value, "leverage_liquidity")

    assert group.status == "accepted"
    assert group.strength == "quantitative_direct"
    assert group.measurement_kind == "actual_exposure"
    assert len(group.source_anchor_ids) == 2
    assert "leverage_liquidity" in field.value.satisfied_group_ids


def test_drawdown_control_text_alone_is_weak() -> None:
    """回撤控制意图不能被提升为最大回撤或压力测试证据。"""

    report = _build_report(
        raw_text=_base_bond_raw_text(section_four_extra="本基金力争保持净值稳定并控制回撤。"),
        tables=(),
    )

    field = extract_bond_risk_evidence(report, "bond_fund")
    assert field.value is not None
    group = _group_by_id(field.value, "drawdown_stress")

    assert group.status == "weak"
    assert group.strength == "qualitative_control_intent"
    assert group.measurement_kind == "control_intent"
    assert "drawdown_stress" in field.value.weak_group_ids
    assert "drawdown_stress" not in field.value.satisfied_group_ids


def test_multi_share_class_share_change_selects_target_class_when_disambiguated() -> None:
    """§2 代码/简称映射明确时，份额变动表只选择目标份额类别列。"""

    report = _build_report(
        raw_text=_base_bond_raw_text(
            section_two_extra="下属分级基金的基金简称 易方达安悦 A 易方达安悦 C\n"
            "下属分级基金的交易代码 006597 006598",
        ),
        tables=(_share_change_table(),),
    )

    field = extract_bond_risk_evidence(report, "bond_fund")
    assert field.value is not None
    group = _group_by_id(field.value, "redemption_share_pressure")

    assert group.status == "accepted"
    assert group.strength == "quantitative_direct"
    notes = tuple(anchor.note for anchor in field.anchors if anchor.section_id == "§10")
    assert "期初基金份额总额=1,000,000.00" in notes
    assert "本期基金总申购份额=200,000.00" in notes
    assert "本期基金总赎回份额=300,000.00" in notes
    assert "期末基金份额总额=900,000.00" in notes


def test_ambiguous_multi_share_class_share_change_stays_ambiguous() -> None:
    """缺少 §2 消歧证据时，多份额类别份额变动表不能满足赎回压力组。"""

    report = _build_report(raw_text=_base_bond_raw_text(), tables=(_share_change_table(),))

    field = extract_bond_risk_evidence(report, "bond_fund")
    assert field.value is not None
    group = _group_by_id(field.value, "redemption_share_pressure")

    assert group.status == "ambiguous"
    assert group.strength == "ambiguous"
    assert group.na_reason == "ambiguous_share_class_selection"
    assert "redemption_share_pressure" in field.value.ambiguous_group_ids
    assert "redemption_share_pressure" not in field.value.satisfied_group_ids


def test_convertible_and_equity_dash_rows_become_accepted_absence() -> None:
    """权益和可转债 '-' 行应形成 accepted_absence 证据。"""

    report = _build_report(
        raw_text=_base_bond_raw_text(),
        tables=(
            ParsedTable(
                page_number=59,
                table_index=1,
                headers=("项目", "金额", "占基金总资产比例"),
                rows=(("股票", "-", "-"), ("可转债（可交换债）", "-", "-")),
            ),
        ),
    )

    field = extract_bond_risk_evidence(report, "bond_fund")
    assert field.value is not None
    group = _group_by_id(field.value, "convertible_bond_equity_exposure")

    assert group.status == "accepted_absence"
    assert group.strength == "quantitative_absence"
    assert group.measurement_kind == "explicit_absence"
    assert len(group.source_anchor_ids) == 2
    assert "convertible_bond_equity_exposure" in field.value.satisfied_group_ids


def test_non_bond_type_returns_missing_without_scanning_group_extractors(monkeypatch: pytest.MonkeyPatch) -> None:
    """非债券或未知类型必须早退，不扫描七组风险 extractor。"""

    def _fail_group_scan(_report: ParsedAnnualReport) -> object:
        raise AssertionError("non-bond path must not scan bond evidence groups")

    monkeypatch.setattr(bond_risk_module, "_extract_duration_rate_risk", _fail_group_scan)
    field = extract_bond_risk_evidence(_build_report(raw_text=_base_bond_raw_text(), tables=()), "active_fund")

    assert field.value is None
    assert field.anchors == ()
    assert field.extraction_mode == "missing"
    assert field.note == "not_applicable_non_bond_fund"


def test_none_fund_type_returns_missing_without_scanning_group_extractors(monkeypatch: pytest.MonkeyPatch) -> None:
    """classified_fund_type 为 None 时必须早退，不扫描七组风险 extractor。"""

    def _fail_group_scan(_report: ParsedAnnualReport) -> object:
        raise AssertionError("None fund type must not scan bond evidence groups")

    monkeypatch.setattr(bond_risk_module, "_extract_duration_rate_risk", _fail_group_scan)
    field = extract_bond_risk_evidence(_build_report(raw_text=_base_bond_raw_text(), tables=()), None)

    assert field.value is None
    assert field.anchors == ()
    assert field.extraction_mode == "missing"
    assert field.note == "not_applicable_non_bond_fund"


def test_partial_extraction_with_mixed_groups_produces_estimated_mode() -> None:
    """部分组满足时 extraction_mode 应为 estimated，不得伪装为 direct 或 missing。"""

    report = _build_report(
        raw_text=_base_bond_raw_text(section_four_extra="本基金通过久期管理控制利率风险。"),
        tables=(
            ParsedTable(
                page_number=53,
                table_index=0,
                headers=("信用评级", "占基金资产净值比例"),
                rows=(("AAA 信用评级债券", "80.00%"),),
            ),
        ),
    )

    field = extract_bond_risk_evidence(report, "bond_fund")
    assert field.value is not None
    assert field.value.contract_status == "partial"
    assert field.extraction_mode == "estimated"
    assert "duration_rate_risk" in field.value.satisfied_group_ids
    assert "credit_risk" in field.value.satisfied_group_ids
    assert len(field.value.satisfied_group_ids) < len(BOND_RISK_EVIDENCE_GROUP_IDS)
    assert len(field.value.missing_group_ids) > 0
    assert field.extraction_mode != "direct"
    assert field.value.contract_status != "satisfied"


def test_incomplete_seven_group_coverage_does_not_masquerade_as_complete() -> None:
    """不完整七组覆盖不得伪装为 satisfied 或 direct。"""

    report = _build_report(
        raw_text=_base_bond_raw_text(section_four_extra="本基金力争保持净值稳定并控制回撤。"),
        tables=(),
    )

    field = extract_bond_risk_evidence(report, "bond_fund")
    assert field.value is not None
    assert field.extraction_mode != "direct"
    assert field.value.contract_status != "satisfied"
    assert len(field.value.satisfied_group_ids) < len(BOND_RISK_EVIDENCE_GROUP_IDS)


def test_non_zero_equity_row_does_not_produce_accepted_absence() -> None:
    """股票行值为非零或非横线时不应产生 accepted_absence 证据。"""

    report = _build_report(
        raw_text=_base_bond_raw_text(),
        tables=(
            ParsedTable(
                page_number=59,
                table_index=1,
                headers=("项目", "金额", "占基金总资产比例"),
                rows=(("股票", "100,000.00", "5.00%"),),
            ),
        ),
    )

    field = extract_bond_risk_evidence(report, "bond_fund")
    assert field.value is not None
    group = _group_by_id(field.value, "convertible_bond_equity_exposure")

    assert group.status == "missing"
    assert group.strength == "missing"
    assert "convertible_bond_equity_exposure" not in field.value.satisfied_group_ids


def test_boilerplate_rate_risk_text_alone_does_not_satisfy_duration_group() -> None:
    """样板利率风险披露文本不应满足久期/利率风险组。"""

    report = _build_report(
        raw_text=_base_bond_raw_text(section_four_extra="本基金面临利率风险。"),
        tables=(),
    )

    field = extract_bond_risk_evidence(report, "bond_fund")
    assert field.value is not None
    group = _group_by_id(field.value, "duration_rate_risk")

    assert group.status == "missing"
    assert "duration_rate_risk" not in field.value.satisfied_group_ids


def _complete_value(
    *,
    overrides: dict[BondRiskEvidenceGroupId, BondRiskEvidenceGroupRecord] | None = None,
) -> BondRiskEvidenceValue:
    """构造模板第 6 章七组完整债券风险证据值。

    Args:
        overrides: 按风险组 ID 覆盖默认记录。

    Returns:
        可用于模型契约测试的债券风险证据值。
    """

    overrides = overrides or {}
    groups = tuple(overrides.get(group_id, _default_group_record(group_id)) for group_id in BOND_RISK_EVIDENCE_GROUP_IDS)
    anchors = tuple(_anchor(group.group_id) for group in groups if group.source_anchor_ids)
    satisfied_ids = tuple(
        group.group_id for group in groups if group.status in {"accepted", "accepted_absence"}
    )
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
        fund_code="006597",
        report_year=2024,
        groups=groups,
        anchors=anchors,
        satisfied_group_ids=satisfied_ids,
        missing_group_ids=missing_ids,
        weak_group_ids=weak_ids,
        ambiguous_group_ids=ambiguous_ids,
        contract_status=contract_status,
    )


def _default_group_record(group_id: BondRiskEvidenceGroupId) -> BondRiskEvidenceGroupRecord:
    """构造模板第 6 章默认已满足风险组记录。

    Args:
        group_id: 债券风险证据组 ID。

    Returns:
        默认风险组记录。
    """

    if group_id == "convertible_bond_equity_exposure":
        return _group_record(
            group_id,
            status="accepted_absence",
            strength="quantitative_absence",
            measurement_kind="explicit_absence",
        )
    return _group_record(
        group_id,
        status="accepted",
        strength="quantitative_direct",
        measurement_kind="actual_exposure",
    )


def _group_record(
    group_id: BondRiskEvidenceGroupId,
    *,
    status: str,
    strength: str,
    measurement_kind: str,
) -> BondRiskEvidenceGroupRecord:
    """构造模板第 6 章单组风险证据记录。

    Args:
        group_id: 债券风险证据组 ID。
        status: 证据状态。
        strength: 证据强度。
        measurement_kind: 度量或披露类型。

    Returns:
        单组风险证据记录。
    """

    return BondRiskEvidenceGroupRecord(
        group_id=group_id,
        status=status,
        strength=strength,
        summary=f"{group_id} fixture summary",
        measurement_kind=measurement_kind,
        metric_name=None,
        metric_value=None,
        metric_unit=None,
        period_label="2024 年报",
        source_anchor_ids=(f"bond-risk:006597:2024:{group_id}:1",),
        na_reason=None,
        reviewer_note=None,
    )


def _anchor(group_id: BondRiskEvidenceGroupId) -> BondRiskEvidenceAnchorRef:
    """构造模板第 6 章单组稳定锚点引用。

    Args:
        group_id: 债券风险证据组 ID。

    Returns:
        稳定组级锚点引用。
    """

    return BondRiskEvidenceAnchorRef(
        anchor_id=f"bond-risk:006597:2024:{group_id}:1",
        section_id="§6",
        page_number=42,
        table_id="table-fixture",
        row_locator=f"{group_id} row",
        evidence_role="fixture",
    )


def _group_by_id(
    value: BondRiskEvidenceValue,
    group_id: BondRiskEvidenceGroupId,
) -> BondRiskEvidenceGroupRecord:
    """按风险组 ID 读取模板第 6 章证据记录。

    Args:
        value: 债券风险证据契约值。
        group_id: 目标风险组 ID。

    Returns:
        匹配的风险组记录。
    """

    return next(group for group in value.groups if group.group_id == group_id)


def _anchor_ref_by_id(value: BondRiskEvidenceValue, anchor_id: str) -> BondRiskEvidenceAnchorRef:
    """按锚点 ID 读取模板第 6 章稳定锚点。

    Args:
        value: 债券风险证据契约值。
        anchor_id: 目标锚点 ID。

    Returns:
        匹配的组级锚点。
    """

    return next(anchor for anchor in value.anchors if anchor.anchor_id == anchor_id)


def _build_report(*, raw_text: str, tables: tuple[ParsedTable, ...]) -> ParsedAnnualReport:
    """构造模板第 6 章 extractor 测试用最小年报。

    Args:
        raw_text: 年报全文。
        tables: 年报表格。

    Returns:
        最小 ``ParsedAnnualReport``。
    """

    sections = {}
    section_order = ("§2", "§4", "§5", "§8", "§9", "§10")
    for index, section_id in enumerate(section_order):
        start = raw_text.index(section_id)
        if index + 1 < len(section_order):
            end = raw_text.index(section_order[index + 1])
        else:
            end = len(raw_text)
        sections[section_id] = ReportSection(
            section_id=section_id,
            title=f"{section_id} fixture",
            start_offset=start,
            end_offset=end,
            matched_rule="fixture",
            confidence=1.0,
        )
    return ParsedAnnualReport(
        key=DocumentKey(fund_code="006597", year=2024),
        raw_text=raw_text,
        sections=sections,
        tables=tables,
    )


def _base_bond_raw_text(section_two_extra: str = "", section_four_extra: str = "") -> str:
    """构造含 §2/§4/§5/§8/§9/§10 的最小年报文本。

    Args:
        section_two_extra: §2 追加文本。
        section_four_extra: §4 追加文本。

    Returns:
        年报全文。
    """

    return (
        "§2 基金简介\n"
        f"{section_two_extra}\n"
        "§4 管理人报告\n"
        f"{section_four_extra}\n"
        "§5 托管人报告\n"
        "§8 投资组合报告\n"
        "§9 基金份额持有人信息\n"
        "§10 开放式基金份额变动\n"
    )


def _share_change_table() -> ParsedTable:
    """构造多份额类别份额变动表。

    Args:
        无。

    Returns:
        份额变动表。
    """

    return ParsedTable(
        page_number=65,
        table_index=0,
        headers=("项目", "易方达安悦 A", "易方达安悦 C", "合计"),
        rows=(
            ("期初基金份额总额", "1,000,000.00", "2,000,000.00", "3,000,000.00"),
            ("本期基金总申购份额", "200,000.00", "400,000.00", "600,000.00"),
            ("本期基金总赎回份额", "300,000.00", "100,000.00", "400,000.00"),
            ("期末基金份额总额", "900,000.00", "2,300,000.00", "3,200,000.00"),
        ),
    )
