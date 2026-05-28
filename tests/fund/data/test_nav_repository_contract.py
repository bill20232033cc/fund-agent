"""NAV repository/source adapter typed contract 纯模型测试。

本测试文件只覆盖 Slice 1a 的 dataclass 与 validator 契约，不访问 Akshare、
SQLite、缓存或 repository IO。测试目标是保证未来模板第 2 章「R=A+B-C」和
第 6 章「核心风险」使用 NAV 路径证据前，模型已经完成 fail-closed 校验。
"""

from __future__ import annotations

from dataclasses import fields
from datetime import date, datetime
from decimal import Decimal

import pytest

from fund_agent.fund.data import (
    FundNavRecord,
    FundNavSeries,
    NavDataContractError,
    NavSourceMetadata,
    ShareClassMapping,
)


def _source_metadata(*, failure_category: str | None = None) -> NavSourceMetadata:
    """创建测试用 NAV source 元数据。

    Args:
        failure_category: 需要注入的来源失败分类；成功路径默认为空。

    Returns:
        测试用 NAV source 元数据。

    Raises:
        无显式抛出。
    """

    return NavSourceMetadata(
        source_name="test_source",
        origin_source="akshare",
        source_id="006597",
        source_url="https://example.test/nav/006597",
        cached=False,
        retrieved_at=datetime(2026, 5, 28, 10, 0, 0),
        cache_updated_at=None,
        requested_fund_code="006597",
        returned_fund_code="006597",
        returned_fund_name="test fund",
        failure_category=failure_category,
    )


def _share_class_mapping(
    *,
    identity_status: str = "verified",
    resolved_share_class: str = "A",
) -> ShareClassMapping:
    """创建测试用份额映射。

    Args:
        identity_status: source identity 验证状态。
        resolved_share_class: 已解析份额类别。

    Returns:
        测试用份额映射结果。

    Raises:
        无显式抛出。
    """

    return ShareClassMapping(
        requested_fund_code="006597",
        requested_share_class=None,
        resolved_fund_code="006597",
        resolved_share_class=resolved_share_class,
        mapping_status="requested_code_default_a",
        identity_status=identity_status,
        mapping_evidence=("requested fund code 006597 defaults to A share",),
    )


def _nav_record(
    *,
    record_date: date = date(2024, 1, 2),
    share_class: str = "A",
    nav_type: str = "adjusted_nav",
    adjusted_basis: str = "dividend_adjusted_nav",
    raw_payload: dict[str, object] | None = None,
) -> FundNavRecord:
    """创建测试用单日 NAV 记录。

    Args:
        record_date: NAV 记录日期。
        share_class: NAV 记录份额类别。
        nav_type: source 声称的 NAV 类型。
        adjusted_basis: 系统判定的调整基础。
        raw_payload: 原始 payload；仅测试 diagnostics 字段存在性。

    Returns:
        测试用单日 NAV 记录。

    Raises:
        无显式抛出。
    """

    return FundNavRecord(
        date=record_date,
        share_class=share_class,
        nav_value=Decimal("1.2345"),
        nav_type=nav_type,
        adjusted_basis=adjusted_basis,
        raw_change_rate=Decimal("0.0100"),
        raw_payload=raw_payload or {"raw_nav": "1.2345"},
    )


def _nav_series(
    *,
    records: tuple[FundNavRecord, ...] | None = None,
    nav_type: str = "adjusted_nav",
    adjusted_basis: str = "dividend_adjusted_nav",
    identity_status: str = "verified",
    completeness_status: str = "unchecked",
    strong_drawdown_evidence_eligible: bool = True,
    record_count: int | None = None,
    requested_start_date: date | None = None,
    requested_end_date: date | None = None,
    minimum_records: int | None = None,
) -> FundNavSeries:
    """创建测试用 NAV series。

    Args:
        records: NAV 记录集合；默认创建一条记录。
        nav_type: series-level NAV 类型。
        adjusted_basis: series-level 调整基础。
        identity_status: source identity 验证状态。
        completeness_status: 调用方传入的完整性状态。
        strong_drawdown_evidence_eligible: 调用方传入的强回撤证据资格。
        record_count: 调用方传入的记录数量；默认与 records 长度一致。
        requested_start_date: 显式要求覆盖的起始日期。
        requested_end_date: 显式要求覆盖的结束日期。
        minimum_records: 显式要求的最少记录数。

    Returns:
        测试用 NAV series。

    Raises:
        NavDataContractError: 当输入违反 typed contract 时抛出。
    """

    nav_records = records or (
        _nav_record(nav_type=nav_type, adjusted_basis=adjusted_basis),
    )
    return FundNavSeries(
        fund_code="006597",
        share_class="A",
        records=nav_records,
        nav_type=nav_type,
        adjusted_basis=adjusted_basis,
        dividend_adjustment_status="adjusted",
        identity_status=identity_status,
        completeness_status=completeness_status,
        strong_drawdown_evidence_eligible=strong_drawdown_evidence_eligible,
        strong_drawdown_ineligibility_reason=None,
        source=_source_metadata(),
        share_class_mapping=_share_class_mapping(identity_status=identity_status),
        date_range_start=None,
        date_range_end=None,
        record_count=record_count if record_count is not None else len(nav_records),
        requested_start_date=requested_start_date,
        requested_end_date=requested_end_date,
        minimum_records=minimum_records,
    )


def test_nav_series_success_path_normalizes_contract_fields() -> None:
    """验证成功路径的字段完整性与默认完整性语义。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        无显式抛出。
    """

    series = _nav_series()

    assert series.fund_code == "006597"
    assert series.share_class == "A"
    assert series.record_count == 1
    assert series.records[0].nav_value == Decimal("1.2345")
    assert series.date_range_start == date(2024, 1, 2)
    assert series.date_range_end == date(2024, 1, 2)
    assert series.completeness_status == "unchecked"
    assert series.strong_drawdown_evidence_eligible is True
    assert series.source.failure_category is None
    assert series.share_class_mapping.mapping_evidence == (
        "requested fund code 006597 defaults to A share",
    )


def test_nav_source_metadata_failure_category_defaults_to_none() -> None:
    """验证成功 source metadata 默认不携带失败分类。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        无显式抛出。
    """

    metadata = _source_metadata()

    assert metadata.failure_category is None


def test_requested_code_only_is_not_strong_drawdown_eligible() -> None:
    """验证 requested_code_only 会降级强回撤证据资格。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        无显式抛出。
    """

    series = _nav_series(identity_status="requested_code_only")

    assert series.strong_drawdown_evidence_eligible is False
    assert series.strong_drawdown_ineligibility_reason is not None
    assert "source-returned identity" in series.strong_drawdown_ineligibility_reason
    assert "未验证" in series.strong_drawdown_ineligibility_reason


def test_raw_unit_nav_is_not_strong_drawdown_eligible() -> None:
    """验证 raw_unit_nav 不能作为 strong drawdown evidence。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        无显式抛出。
    """

    series = _nav_series(
        nav_type="unit_nav",
        adjusted_basis="raw_unit_nav",
        records=(
            _nav_record(nav_type="unit_nav", adjusted_basis="raw_unit_nav"),
        ),
    )

    assert series.strong_drawdown_evidence_eligible is False
    assert series.strong_drawdown_ineligibility_reason is not None
    assert "raw_unit_nav" in series.strong_drawdown_ineligibility_reason
    assert "dividend" in series.strong_drawdown_ineligibility_reason
    assert "total-return basis" in series.strong_drawdown_ineligibility_reason


def test_illegal_nav_type_adjustment_basis_combination_raises_schema_drift() -> None:
    """验证非法 NAV 类型与调整基础组合触发 schema_drift。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        无显式抛出。
    """

    with pytest.raises(NavDataContractError) as exc_info:
        _nav_series(
            nav_type="unit_nav",
            adjusted_basis="dividend_adjusted_nav",
            records=(
                _nav_record(nav_type="unit_nav", adjusted_basis="dividend_adjusted_nav"),
            ),
        )

    assert exc_info.value.category == "schema_drift"


def test_duplicate_record_date_raises_integrity_error() -> None:
    """验证重复 NAV 日期触发 integrity_error。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        无显式抛出。
    """

    records = (
        _nav_record(record_date=date(2024, 1, 2)),
        _nav_record(record_date=date(2024, 1, 2)),
    )

    with pytest.raises(NavDataContractError) as exc_info:
        _nav_series(records=records)

    assert exc_info.value.category == "integrity_error"


def test_empty_records_raises_not_found() -> None:
    """验证空 records 直接触发 not_found，不经 helper 默认记录兜底。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        无显式抛出。
    """

    with pytest.raises(NavDataContractError) as exc_info:
        FundNavSeries(
            fund_code="006597",
            share_class="A",
            records=(),
            nav_type="adjusted_nav",
            adjusted_basis="dividend_adjusted_nav",
            dividend_adjustment_status="adjusted",
            identity_status="verified",
            completeness_status="unchecked",
            strong_drawdown_evidence_eligible=True,
            strong_drawdown_ineligibility_reason=None,
            source=_source_metadata(),
            share_class_mapping=_share_class_mapping(),
            date_range_start=None,
            date_range_end=None,
            record_count=0,
        )

    assert exc_info.value.category == "not_found"


def test_record_share_class_mismatch_raises_integrity_error() -> None:
    """验证 record share_class 与 series share_class 不一致时 fail-closed。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        无显式抛出。
    """

    with pytest.raises(NavDataContractError) as exc_info:
        _nav_series(
            nav_type="adjusted_nav",
            adjusted_basis="dividend_adjusted_nav",
            records=(
                _nav_record(
                    share_class="C",
                    nav_type="adjusted_nav",
                    adjusted_basis="dividend_adjusted_nav",
                ),
            ),
        )

    assert exc_info.value.category == "integrity_error"


def test_identity_mismatch_raises_identity_mismatch() -> None:
    """验证 source identity mismatch 直接触发 identity_mismatch。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        无显式抛出。
    """

    with pytest.raises(NavDataContractError) as exc_info:
        _nav_series(identity_status="identity_mismatch")

    assert exc_info.value.category == "identity_mismatch"


def test_adjusted_basis_unknown_raises_adjustment_basis_unknown() -> None:
    """验证 unknown 调整基础不能构造成功 series。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        无显式抛出。
    """

    with pytest.raises(NavDataContractError) as exc_info:
        _nav_series(
            nav_type="adjusted_nav",
            adjusted_basis="unknown",
            records=(_nav_record(adjusted_basis="unknown"),),
        )

    assert exc_info.value.category == "adjustment_basis_unknown"


def test_nav_type_unknown_raises_schema_drift() -> None:
    """验证 unknown NAV 类型不能构造成功 series。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        无显式抛出。
    """

    with pytest.raises(NavDataContractError) as exc_info:
        _nav_series(
            nav_type="unknown",
            adjusted_basis="raw_unit_nav",
            records=(_nav_record(nav_type="unknown", adjusted_basis="raw_unit_nav"),),
        )

    assert exc_info.value.category == "schema_drift"


def test_record_count_mismatch_raises_integrity_error() -> None:
    """验证 record_count 与 records 长度不一致时触发 integrity_error。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        无显式抛出。
    """

    with pytest.raises(NavDataContractError) as exc_info:
        _nav_series(record_count=2)

    assert exc_info.value.category == "integrity_error"


def test_explicit_constraints_mark_complete_enough_when_satisfied() -> None:
    """验证显式完整性约束通过时状态归一为 complete_enough。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        无显式抛出。
    """

    series = _nav_series(
        requested_start_date=date(2024, 1, 2),
        requested_end_date=date(2024, 1, 2),
        minimum_records=1,
    )

    assert series.completeness_status == "complete_enough"


def test_raw_payload_is_diagnostics_only_and_not_equality_bypass() -> None:
    """验证 raw_payload 只作为 diagnostics 字段，不参与业务等价判断。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        无显式抛出。
    """

    first = _nav_record(raw_payload={"raw_nav": "1.2345"})
    second = _nav_record(raw_payload={"raw_nav": "999.9999", "bypass": True})
    raw_payload_field = next(field for field in fields(FundNavRecord) if field.name == "raw_payload")

    assert first == second
    assert first.raw_payload["raw_nav"] == "1.2345"
    assert "diagnostics/debugging" in raw_payload_field.metadata["doc"]
    assert "不得读取 raw_payload 绕过 typed NAV 字段" in raw_payload_field.metadata["doc"]
