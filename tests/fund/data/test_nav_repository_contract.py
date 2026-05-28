"""NAV repository/source adapter typed contract 测试。

本测试文件覆盖 Slice 1a 的 dataclass/validator 契约，以及 Slice 1b 的
repository raw-unit-only 归一化契约。测试不访问真实 Akshare；repository
集成测试使用 fake adapter 保证模板第 2 章「R=A+B-C」和第 6 章「核心风险」
使用 NAV 路径证据前，source identity、调整基础和完整性已经 fail-closed。
"""

from __future__ import annotations

import inspect
from dataclasses import fields
from datetime import date, datetime
from decimal import Decimal

import pytest

from fund_agent.fund.data import (
    FundNavRepository,
    FundNavRecord,
    FundNavSeries,
    NavDataContractError,
    NavSourceMetadata,
    ShareClassMapping,
)
from fund_agent.fund.data.nav_data import _RawNavSourceResult


class _FakeRawNavAdapter:
    """测试用 raw NAV source adapter。

    该 fake 只实现 repository 需要的 `load_raw_nav_source` 边界，避免测试直接
    访问 Akshare、SQLite 或 source-specific helper。
    """

    def __init__(
        self,
        records: list[dict[str, object]] | None = None,
        *,
        error: Exception | None = None,
    ) -> None:
        """初始化 fake adapter。

        Args:
            records: fake raw records；为空时使用空列表。
            error: 需要模拟的 source 异常。

        Returns:
            无返回值。

        Raises:
            无显式抛出。
        """

        self.records = records or []
        self.error = error
        self.calls: list[tuple[str, bool]] = []

    async def load_raw_nav_source(
        self,
        fund_code: str,
        *,
        force_refresh: bool = False,
    ) -> _RawNavSourceResult:
        """返回 fake raw NAV source 结果。

        Args:
            fund_code: 基金代码。
            force_refresh: 是否强制刷新缓存。

        Returns:
            fake `_RawNavSourceResult`。

        Raises:
            Exception: 当初始化传入 error 时抛出。
        """

        self.calls.append((fund_code, force_refresh))
        if self.error is not None:
            raise self.error
        return _RawNavSourceResult(
            fund_code=fund_code,
            records=self.records,
            source="fixture_source",
            origin_source="akshare",
            cached=True,
            retrieved_at=None,
            cache_updated_at="2026-05-28T10:00:00+00:00",
        )


def _raw_nav_row(
    *,
    nav_date: str = "2024-01-02",
    unit_nav: object = "1.2345",
    growth_rate: object = "0.12",
    fund_code: str | None = None,
    fund_name: str | None = None,
) -> dict[str, object]:
    """创建 006597-like 中文 raw NAV row。

    Args:
        nav_date: 净值日期。
        unit_nav: 单位净值。
        growth_rate: 日增长率。
        fund_code: 可选 source-returned fund code。
        fund_name: 可选 source-returned fund name。

    Returns:
        中文 raw NAV row。

    Raises:
        无显式抛出。
    """

    row: dict[str, object] = {
        "净值日期": nav_date,
        "单位净值": unit_nav,
        "日增长率": growth_rate,
    }
    if fund_code is not None:
        row["基金代码"] = fund_code
    if fund_name is not None:
        row["基金名称"] = fund_name
    return row


async def _load_repository_series(
    records: list[dict[str, object]],
    *,
    start_date: date | None = None,
    end_date: date | None = None,
    minimum_records: int | None = None,
) -> FundNavSeries:
    """使用 fake adapter 加载 repository series。

    Args:
        records: fake raw records。
        start_date: 显式起始日期约束。
        end_date: 显式结束日期约束。
        minimum_records: 显式最少记录数约束。

    Returns:
        repository 归一化后的 `FundNavSeries`。

    Raises:
        NavDataContractError: 当 repository fail-closed 时抛出。
    """

    repository = FundNavRepository(source_adapter=_FakeRawNavAdapter(records))
    return await repository.load_nav_series(
        "006597",
        start_date=start_date,
        end_date=end_date,
        minimum_records=minimum_records,
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


# ---------------------------------------------------------------------------
# Slice 1b: Repository integration tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_repository_raw_fixture_normalizes_to_typed_series() -> None:
    """验证 006597-like 中文 raw fixture 归一化为 typed FundNavSeries。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当归一化结果字段不符合 typed contract 时抛出。
    """

    records = [
        _raw_nav_row(nav_date="2024-01-02", unit_nav="1.2345", growth_rate="0.12"),
        _raw_nav_row(nav_date="2024-01-03", unit_nav="1.2400", growth_rate="0.45"),
    ]
    series = await _load_repository_series(records)

    assert series.fund_code == "006597"
    assert series.share_class == "A"
    assert series.record_count == 2
    assert series.nav_type == "unit_nav"
    assert series.adjusted_basis == "raw_unit_nav"
    assert series.dividend_adjustment_status == "not_adjusted"
    assert series.identity_status == "requested_code_only"
    assert series.strong_drawdown_evidence_eligible is False
    assert series.source.origin_source == "akshare"
    assert series.source.failure_category is None
    assert series.share_class_mapping.mapping_status == "requested_code_default_a"
    assert series.share_class_mapping.identity_status == "requested_code_only"
    # records 按 date 升序
    assert series.records[0].date < series.records[1].date
    assert series.records[0].nav_value == Decimal("1.2345")
    assert series.records[1].nav_value == Decimal("1.2400")
    assert series.records[0].raw_change_rate == Decimal("0.12")


@pytest.mark.asyncio
async def test_repository_requested_code_only_not_strong_eligible() -> None:
    """验证 repository 路径 requested_code_only 不得 strong eligible。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 strong eligibility 不符合预期时抛出。
    """

    records = [_raw_nav_row()]
    series = await _load_repository_series(records)

    assert series.identity_status == "requested_code_only"
    assert series.strong_drawdown_evidence_eligible is False
    assert "source-returned identity" in (series.strong_drawdown_ineligibility_reason or "")
    assert "未验证" in (series.strong_drawdown_ineligibility_reason or "")


@pytest.mark.asyncio
async def test_repository_identity_mismatch_raises() -> None:
    """验证 source-returned fund code 与请求冲突时 fail-closed。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当未抛出 identity_mismatch 错误时抛出。
    """

    records = [_raw_nav_row(fund_code="999999")]
    repository = FundNavRepository(source_adapter=_FakeRawNavAdapter(records))

    with pytest.raises(NavDataContractError) as exc_info:
        await repository.load_nav_series("006597")

    assert exc_info.value.category == "identity_mismatch"


@pytest.mark.asyncio
async def test_repository_missing_date_column_raises_schema_drift() -> None:
    """验证缺少净值日期列时 fail-closed schema_drift。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当未抛出 schema_drift 错误时抛出。
    """

    records: list[dict[str, object]] = [{"单位净值": "1.2345", "日增长率": "0.12"}]
    repository = FundNavRepository(source_adapter=_FakeRawNavAdapter(records))

    with pytest.raises(NavDataContractError) as exc_info:
        await repository.load_nav_series("006597")

    assert exc_info.value.category == "schema_drift"
    assert "净值日期" in exc_info.value.message


@pytest.mark.asyncio
async def test_repository_missing_nav_column_raises_schema_drift() -> None:
    """验证缺少单位净值列时 fail-closed schema_drift。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当未抛出 schema_drift 错误时抛出。
    """

    records: list[dict[str, object]] = [{"净值日期": "2024-01-02", "日增长率": "0.12"}]
    repository = FundNavRepository(source_adapter=_FakeRawNavAdapter(records))

    with pytest.raises(NavDataContractError) as exc_info:
        await repository.load_nav_series("006597")

    assert exc_info.value.category == "schema_drift"
    assert "单位净值" in exc_info.value.message


@pytest.mark.asyncio
async def test_repository_invalid_date_raises_schema_drift() -> None:
    """验证日期不可解析时 fail-closed schema_drift。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当未抛出 schema_drift 错误时抛出。
    """

    records: list[dict[str, object]] = [
        {"净值日期": "not-a-date", "单位净值": "1.2345", "日增长率": "0.12"},
    ]
    repository = FundNavRepository(source_adapter=_FakeRawNavAdapter(records))

    with pytest.raises(NavDataContractError) as exc_info:
        await repository.load_nav_series("006597")

    assert exc_info.value.category == "schema_drift"


@pytest.mark.asyncio
async def test_repository_invalid_growth_rate_raises_schema_drift() -> None:
    """验证日增长率不可解析时 fail-closed schema_drift。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当未抛出 schema_drift 错误时抛出。
    """

    records: list[dict[str, object]] = [
        {"净值日期": "2024-01-02", "单位净值": "1.2345", "日增长率": "not-a-number"},
    ]
    repository = FundNavRepository(source_adapter=_FakeRawNavAdapter(records))

    with pytest.raises(NavDataContractError) as exc_info:
        await repository.load_nav_series("006597")

    assert exc_info.value.category == "schema_drift"
    assert "日增长率" in exc_info.value.message


@pytest.mark.asyncio
async def test_repository_nonpositive_nav_raises_integrity_error() -> None:
    """验证非正单位净值时 fail-closed integrity_error。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当未抛出 integrity_error 错误时抛出。
    """

    records: list[dict[str, object]] = [
        {"净值日期": "2024-01-02", "单位净值": "0", "日增长率": "0.12"},
    ]
    repository = FundNavRepository(source_adapter=_FakeRawNavAdapter(records))

    with pytest.raises(NavDataContractError) as exc_info:
        await repository.load_nav_series("006597")

    assert exc_info.value.category == "integrity_error"


@pytest.mark.asyncio
async def test_repository_duplicate_raw_date_raises_integrity_error() -> None:
    """验证 raw records 中重复日期时 fail-closed integrity_error。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当未抛出 integrity_error 错误时抛出。
    """

    records = [
        _raw_nav_row(nav_date="2024-01-02", unit_nav="1.2345"),
        _raw_nav_row(nav_date="2024-01-02", unit_nav="1.2400"),
    ]
    repository = FundNavRepository(source_adapter=_FakeRawNavAdapter(records))

    with pytest.raises(NavDataContractError) as exc_info:
        await repository.load_nav_series("006597")

    assert exc_info.value.category == "integrity_error"


@pytest.mark.asyncio
async def test_repository_missing_date_range_raises() -> None:
    """验证显式日期范围未被 records 覆盖时 fail-closed missing_date_range。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当未抛出 missing_date_range 错误时抛出。
    """

    records = [_raw_nav_row(nav_date="2024-06-01")]
    repository = FundNavRepository(source_adapter=_FakeRawNavAdapter(records))

    with pytest.raises(NavDataContractError) as exc_info:
        await repository.load_nav_series(
            "006597",
            start_date=date(2024, 1, 1),
            end_date=date(2024, 12, 31),
        )

    assert exc_info.value.category == "missing_date_range"


@pytest.mark.asyncio
async def test_repository_insufficient_records_raises() -> None:
    """验证显式 minimum_records 不足时 fail-closed insufficient_records。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当未抛出 insufficient_records 错误时抛出。
    """

    records = [_raw_nav_row(nav_date="2024-01-02")]
    repository = FundNavRepository(source_adapter=_FakeRawNavAdapter(records))

    with pytest.raises(NavDataContractError) as exc_info:
        await repository.load_nav_series("006597", minimum_records=10)

    assert exc_info.value.category == "insufficient_records"


@pytest.mark.asyncio
async def test_repository_unavailable_cause_preserved() -> None:
    """验证 source adapter 异常包装为 unavailable 且 cause 可追溯。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当未抛出 unavailable 错误或 cause 丢失时抛出。
    """

    original_error = RuntimeError("network timeout")
    repository = FundNavRepository(
        source_adapter=_FakeRawNavAdapter(error=original_error),
    )

    with pytest.raises(NavDataContractError) as exc_info:
        await repository.load_nav_series("006597")

    assert exc_info.value.category == "unavailable"
    assert exc_info.value.cause is original_error


@pytest.mark.asyncio
async def test_repository_empty_records_raises_not_found() -> None:
    """验证 source 返回空 records 时 fail-closed not_found。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当未抛出 not_found 错误时抛出。
    """

    repository = FundNavRepository(source_adapter=_FakeRawNavAdapter(records=[]))

    with pytest.raises(NavDataContractError) as exc_info:
        await repository.load_nav_series("006597")

    assert exc_info.value.category == "not_found"


def test_load_nav_series_signature_has_no_extra_payload_or_kwargs() -> None:
    """验证 load_nav_series 签名不包含 extra_payload、kwargs 或自由 dict 参数。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当签名包含禁止参数时抛出。
    """

    sig = inspect.signature(FundNavRepository.load_nav_series)
    param_names = list(sig.parameters.keys())

    assert "extra_payload" not in param_names
    assert "kwargs" not in param_names
    # 验证所有参数都是显式命名参数
    for param in sig.parameters.values():
        assert param.kind in (
            inspect.Parameter.POSITIONAL_OR_KEYWORD,
            inspect.Parameter.KEYWORD_ONLY,
        ), f"参数 {param.name} 类型 {param.kind} 不允许"
