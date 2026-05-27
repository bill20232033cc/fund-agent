"""债券风险证据模型契约测试。"""

from __future__ import annotations

from dataclasses import replace

import pytest

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
