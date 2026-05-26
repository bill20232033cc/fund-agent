"""P4-S1 精选基金池字段级抽取快照测试。"""

from __future__ import annotations

import json
from dataclasses import asdict
from decimal import Decimal
from pathlib import Path

import pytest

from fund_agent.fund.data.nav_data import NavDataResult, unavailable_nav_data_result
from fund_agent.fund.data_extractor import StructuredFundDataBundle
from fund_agent.fund.extraction_snapshot import (
    SNAPSHOT_FIELD_ORDER,
    SelectedFundRecord,
    build_snapshot_records,
    load_selected_funds,
    run_extraction_snapshot,
    validate_selected_fund_pool,
)
from fund_agent.fund.extractors import (
    EvidenceAnchor,
    ExtractedField,
    IndexProfileValue,
    TrackingErrorValue,
)


class _FakeExtractor:
    """快照测试用 fake extractor，不触发真实 PDF 或网络。"""

    def __init__(self, bundles: dict[str, StructuredFundDataBundle], failures: dict[str, Exception] | None = None) -> None:
        """初始化 fake extractor。

        Args:
            bundles: 基金代码到 fake bundle 的映射。
            failures: 基金代码到异常的映射。

        Returns:
            无返回值。

        Raises:
            无显式抛出。
        """

        self._bundles = bundles
        self._failures = failures or {}
        self.calls: list[tuple[str, int, bool]] = []

    async def extract(
        self,
        fund_code: str,
        report_year: int,
        *,
        force_refresh: bool = False,
    ) -> StructuredFundDataBundle:
        """返回 fake bundle 或抛出预设异常。

        Args:
            fund_code: 基金代码。
            report_year: 年报年份。
            force_refresh: 是否强制刷新。

        Returns:
            fake 结构化数据包。

        Raises:
            Exception: 当基金代码在 failures 中时抛出对应异常。
        """

        self.calls.append((fund_code, report_year, force_refresh))
        if fund_code in self._failures:
            raise self._failures[fund_code]
        return self._bundles[fund_code]


def test_selected_fund_csv_validation_flags_missing_bad_code_and_duplicates(tmp_path: Path) -> None:
    """验证 CSV 校验覆盖缺失字段、非法代码和重复代码。

    Args:
        tmp_path: pytest 临时目录 fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当校验结果不符合预期时抛出。
    """

    csv_path = tmp_path / "funds.csv"
    csv_path.write_text(
        "\n".join(
            [
                "基金名称,基金代码,类别",
                "安信企业价值优选混合A,004393,国内股票类",
                "重复基金,004393,国内股票类",
                ",ABC,海外股票类",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    funds = load_selected_funds(csv_path)
    validation = validate_selected_fund_pool(funds)

    assert validation.missing_rows == (4,)
    assert validation.bad_code_rows == ((4, "ABC"),)
    assert validation.duplicate_codes == ("004393",)
    assert validation.has_blocking_errors is True


def test_build_snapshot_records_contains_required_schema_and_all_fields() -> None:
    """验证 snapshot 记录包含 schema 与 P13 观测字段。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当字段数量或 schema 不符合契约时抛出。
    """

    bundle = _build_bundle("110011", "active_fund")
    selected_fund = SelectedFundRecord(
        line_number=2,
        fund_name="易方达中小盘混合",
        fund_code="110011",
        app_category="国内股票类",
    )

    records = build_snapshot_records(
        bundle=bundle,
        selected_fund=selected_fund,
        run_id="unit-run",
        extraction_timestamp="2026-05-19T00:00:00+00:00",
        source_csv="docs/code_20260519.csv",
    )

    assert [(record.field_group, record.field_name) for record in records] == list(SNAPSHOT_FIELD_ORDER)
    first_payload = asdict(records[0])
    assert set(first_payload) == {
        "run_id",
        "extraction_timestamp",
        "source_csv",
        "fund_code",
        "fund_name",
        "app_category",
        "report_year",
        "classified_fund_type",
        "classification_basis",
        "field_name",
        "field_group",
        "extraction_mode",
        "value_present",
        "anchor_present",
        "section_id",
        "page",
        "table_id",
        "row_id",
        "comparable_values",
        "note",
    }
    records_by_name = {record.field_name: record for record in records}
    assert records[0].section_id == "§2"
    assert records[0].anchor_present is True
    assert records[-1].field_name == "nav_data"
    assert records[-1].anchor_present is False
    assert records_by_name["basic_identity"].comparable_values == {
        "fund_name": "安信企业价值优选混合A",
        "fund_code": "110011",
        "fund_category": "混合型",
        "management_company": "安信基金管理有限责任公司",
        "custodian": "中国银行股份有限公司",
        "inception_date": "2022 年 8 月 8 日",
        "classified_fund_type": "active_fund",
    }
    assert records_by_name["benchmark"].comparable_values == {
        "benchmark_name": "沪深300指数收益率",
        "benchmark_text": "沪深300指数收益率",
    }
    assert records_by_name["nav_benchmark_performance"].comparable_values == {
        "nav_growth_rate": "1%",
        "benchmark_return_rate": "0.5%",
    }
    assert records_by_name["classified_fund_type"].comparable_values == {
        "fund_type": "active_fund"
    }
    assert records_by_name["index_profile"].comparable_values == {}
    assert records_by_name["tracking_error"].comparable_values == {}
    assert records_by_name["product_profile"].comparable_values == {}
    assert records_by_name["fee_schedule"].comparable_values == {}
    assert records_by_name["holdings_snapshot"].comparable_values == {
        "top_holdings_status": "direct_top_ten",
        "top_holdings_source": "top_ten",
    }


def test_build_snapshot_records_preserves_unavailable_nav_reason() -> None:
    """验证 NAV 降级原因进入 snapshot note。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 NAV 降级 note 缺少来源、记录数或原因时抛出。
    """

    bundle = _build_bundle("110011", "active_fund")
    unavailable_bundle = StructuredFundDataBundle(
        fund_code=bundle.fund_code,
        report_year=bundle.report_year,
        basic_identity=bundle.basic_identity,
        product_profile=bundle.product_profile,
        benchmark=bundle.benchmark,
        index_profile=bundle.index_profile,
        fee_schedule=bundle.fee_schedule,
        turnover_rate=bundle.turnover_rate,
        nav_benchmark_performance=bundle.nav_benchmark_performance,
        investor_return=bundle.investor_return,
        tracking_error=bundle.tracking_error,
        share_change=bundle.share_change,
        manager_alignment=bundle.manager_alignment,
        manager_strategy_text=bundle.manager_strategy_text,
        holdings_snapshot=bundle.holdings_snapshot,
        holder_structure=bundle.holder_structure,
        nav_data=unavailable_nav_data_result(
            "110011",
            reason="RuntimeError: network down",
        ),
    )
    selected_fund = SelectedFundRecord(
        line_number=2,
        fund_name="易方达中小盘混合",
        fund_code="110011",
        app_category="国内股票类",
    )

    records = build_snapshot_records(
        bundle=unavailable_bundle,
        selected_fund=selected_fund,
        run_id="unit-run",
        extraction_timestamp="2026-05-19T00:00:00+00:00",
        source_csv="docs/code_20260519.csv",
    )

    nav_record = next(record for record in records if record.field_name == "nav_data")
    assert nav_record.extraction_mode == "missing"
    assert nav_record.value_present is False
    assert nav_record.note is not None
    assert "source=nav_unavailable" in nav_record.note
    assert "cached=False" in nav_record.note
    assert "records=0" in nav_record.note
    assert "unavailable=True" in nav_record.note
    assert "reason=RuntimeError: network down" in nav_record.note


def test_build_snapshot_records_serializes_index_quality_dataclass_comparable_values() -> None:
    """验证指数质量 dataclass 值会写入稳定可比子字段。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 dataclass 子字段未进入 comparable_values 时抛出。
    """

    bundle = _build_bundle("510300", "index_fund", include_index_quality=True)
    selected_fund = SelectedFundRecord(
        line_number=3,
        fund_name="沪深300ETF",
        fund_code="510300",
        app_category="国内股票类",
    )

    records = build_snapshot_records(
        bundle=bundle,
        selected_fund=selected_fund,
        run_id="unit-run",
        extraction_timestamp="2026-05-19T00:00:00+00:00",
        source_csv="docs/code_20260519.csv",
    )

    records_by_name = {record.field_name: record for record in records}
    assert records_by_name["index_profile"].comparable_values == {
        "benchmark_text": "沪深300指数收益率",
        "benchmark_identity_status": "identified",
        "benchmark_index_name": "沪深300指数",
        "benchmark_index_code": "000300",
        "methodology_availability": "benchmark_only",
        "constituents_availability": "benchmark_only",
        "source_tier": "benchmark_context",
    }
    assert records_by_name["tracking_error"].comparable_values == {
        "value_text": "1.23%",
        "period_label": "报告期",
        "annualized": "True",
        "source_type": "direct_disclosure",
        "calculation_method": "disclosed",
        "benchmark_identity_status": "identified",
        "benchmark_index_name": "沪深300指数",
        "benchmark_index_code": "000300",
        "frequency": "annual_report_period",
        "input_period_complete": "False",
    }


def test_build_snapshot_records_omits_composite_index_null_and_tuple_values() -> None:
    """验证复合指数画像只序列化可比 scalar，保留不补单一指数名。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 tuple/null 字段进入 comparable_values 时抛出。
    """

    bundle = _build_bundle("004194", "enhanced_index", include_composite_index_profile=True)
    selected_fund = SelectedFundRecord(
        line_number=38,
        fund_name="招商中证1000指数增强A",
        fund_code="004194",
        app_category="国内股票类",
    )

    records = build_snapshot_records(
        bundle=bundle,
        selected_fund=selected_fund,
        run_id="unit-run",
        extraction_timestamp="2026-05-19T00:00:00+00:00",
        source_csv="docs/code_20260519.csv",
    )

    comparable_values = {
        record.field_name: record.comparable_values for record in records
    }["index_profile"]
    assert comparable_values == {
        "benchmark_text": "中证1000指数收益率×95%+同期银行活期存款利率（税后）×5%",
        "benchmark_identity_status": "composite",
        "methodology_availability": "benchmark_only",
        "constituents_availability": "benchmark_only",
        "source_tier": "benchmark_context",
    }
    assert "benchmark_index_name" not in comparable_values
    assert "benchmark_index_code" not in comparable_values
    assert "benchmark_component_text" not in comparable_values


@pytest.mark.asyncio
async def test_run_snapshot_summary_highlights_duplicates_and_continues_failures(tmp_path: Path) -> None:
    """验证 summary 标红重复代码，且单基金失败继续写 errors.jsonl。

    Args:
        tmp_path: pytest 临时目录 fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当输出产物或 fake 调用不符合契约时抛出。
    """

    csv_path = tmp_path / "funds.csv"
    csv_path.write_text(
        "\n".join(
            [
                "基金名称,基金代码,类别",
                "安信企业价值优选混合A,004393,国内股票类",
                "失败基金,000001,国内股票类",
                "重复基金,004393,国内股票类",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    output_dir = tmp_path / "snapshot-output"
    extractor = _FakeExtractor(
        bundles={"004393": _build_bundle("004393", "index_fund")},
        failures={"000001": RuntimeError("fixture failure")},
    )

    result = await run_extraction_snapshot(
        fund_code=None,
        report_year=2024,
        source_csv=csv_path,
        run_id="unit-run",
        output_dir=output_dir,
        force_refresh=True,
        sample_per_category=2,
        extractor=extractor,
    )

    summary_text = result.summary_path.read_text(encoding="utf-8")
    error_lines = result.errors_path.read_text(encoding="utf-8").splitlines()
    snapshot_lines = result.snapshot_path.read_text(encoding="utf-8").splitlines()

    assert extractor.calls == [("004393", 2024, True), ("000001", 2024, True)]
    assert result.succeeded_fund_codes == ("004393",)
    assert result.failed_fund_codes == ("000001",)
    assert result.record_count == len(SNAPSHOT_FIELD_ORDER)
    assert len(snapshot_lines) == len(SNAPSHOT_FIELD_ORDER)
    assert len(error_lines) == 1
    assert json.loads(error_lines[0])["error_message"] == "fixture failure"
    assert "<mark>004393</mark>" in summary_text
    assert "failed_funds: 1" in summary_text


@pytest.mark.asyncio
async def test_004393_known_failure_classification_is_captured(tmp_path: Path) -> None:
    """验证 004393 被误判为 index_fund 时 snapshot 明确记录当前事实。

    Args:
        tmp_path: pytest 临时目录 fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 known failure 没有被记录时抛出。
    """

    csv_path = tmp_path / "funds.csv"
    csv_path.write_text("基金名称,基金代码,类别\n安信企业价值优选混合A,004393,国内股票类\n", encoding="utf-8")
    extractor = _FakeExtractor(bundles={"004393": _build_bundle("004393", "index_fund")})

    result = await run_extraction_snapshot(
        fund_code="004393",
        report_year=2024,
        source_csv=csv_path,
        run_id="unit-004393",
        output_dir=tmp_path / "snapshot-output",
        force_refresh=False,
        extractor=extractor,
    )

    records = [json.loads(line) for line in result.snapshot_path.read_text(encoding="utf-8").splitlines()]
    classification_record = next(record for record in records if record["field_name"] == "classified_fund_type")

    assert classification_record["classified_fund_type"] == "index_fund"
    assert classification_record["value_present"] is True
    assert "known_failure:P4-S1" in classification_record["note"]
    assert "known_failure:P4-S1" in result.summary_path.read_text(encoding="utf-8")


def _build_bundle(
    fund_code: str,
    classified_fund_type: str,
    *,
    include_index_quality: bool = False,
    include_composite_index_profile: bool = False,
) -> StructuredFundDataBundle:
    """构造测试用结构化基金数据包。

    Args:
        fund_code: 基金代码。
        classified_fund_type: fake 分类结果。
        include_index_quality: 是否填充指数画像和跟踪误差 dataclass 值。
        include_composite_index_profile: 是否填充复合基准指数画像 fixture。

    Returns:
        fake 结构化基金数据包。

    Raises:
        无显式抛出。
    """

    missing_index_profile: ExtractedField[IndexProfileValue] = ExtractedField(
        value=None,
        anchors=(),
        extraction_mode="missing",
        note="fixture index profile missing",
    )
    missing_tracking_error: ExtractedField[TrackingErrorValue] = ExtractedField(
        value=None,
        anchors=(),
        extraction_mode="missing",
        note="fixture tracking error missing",
    )
    index_profile = missing_index_profile
    tracking_error = missing_tracking_error
    if include_index_quality and include_composite_index_profile:
        raise ValueError("include_index_quality 与 include_composite_index_profile 不能同时启用")
    if include_index_quality:
        index_profile = ExtractedField(
            value=IndexProfileValue(
                benchmark_text="沪深300指数收益率",
                benchmark_identity_status="identified",
                benchmark_index_name="沪深300指数",
                benchmark_index_code="000300",
                benchmark_component_text=(),
                methodology_availability="benchmark_only",
                methodology_summary=None,
                methodology_source_title=None,
                constituents_availability="benchmark_only",
                constituents_summary=None,
                constituents_as_of_date=None,
                source_tier="benchmark_context",
                missing_reasons=(),
            ),
            anchors=(
                EvidenceAnchor(
                    source_kind="annual_report",
                    document_year=2024,
                    section_id="§2",
                    page_number=3,
                    table_id="page-3-table-0",
                    row_locator="benchmark",
                    note="业绩比较基准：沪深300指数收益率",
                ),
            ),
            extraction_mode="direct",
        )
    if include_composite_index_profile:
        index_profile = ExtractedField(
            value=IndexProfileValue(
                benchmark_text="中证1000指数收益率×95%+同期银行活期存款利率（税后）×5%",
                benchmark_identity_status="composite",
                benchmark_index_name=None,
                benchmark_index_code=None,
                benchmark_component_text=("中证1000指数收益率", "95%", "同期银行活期存款利率（税后）", "5%"),
                methodology_availability="benchmark_only",
                methodology_summary=None,
                methodology_source_title=None,
                constituents_availability="benchmark_only",
                constituents_summary=None,
                constituents_as_of_date=None,
                source_tier="benchmark_context",
                missing_reasons=(
                    "methodology_not_directly_disclosed",
                    "constituents_not_directly_disclosed",
                ),
            ),
            anchors=(
                EvidenceAnchor(
                    source_kind="annual_report",
                    document_year=2024,
                    section_id="§2",
                    page_number=5,
                    table_id="page-5-table-1",
                    row_locator="benchmark",
                    note="业绩比较基准：中证1000指数收益率×95%+同期银行活期存款利率（税后）×5%",
                ),
            ),
            extraction_mode="direct",
        )
    if include_index_quality:
        tracking_error = ExtractedField(
            value=TrackingErrorValue(
                value=Decimal("0.0123"),
                value_text="1.23%",
                unit="ratio",
                period_label="报告期",
                period_start=None,
                period_end=None,
                annualized=True,
                source_type="direct_disclosure",
                calculation_method="disclosed",
                benchmark_identity_status="identified",
                benchmark_index_name="沪深300指数",
                benchmark_index_code="000300",
                fund_series_source=None,
                index_series_source=None,
                observation_count=None,
                frequency="annual_report_period",
                annualization_factor=None,
                input_period_complete=False,
                provenance_note="年报直接披露。",
            ),
            anchors=(
                EvidenceAnchor(
                    source_kind="annual_report",
                    document_year=2024,
                    section_id="§3",
                    page_number=6,
                    table_id=None,
                    row_locator="tracking_error",
                    note="报告期年化跟踪误差：1.23%",
                ),
            ),
            extraction_mode="direct",
        )
    return StructuredFundDataBundle(
        fund_code=fund_code,
        report_year=2024,
        basic_identity=_field(
            {
                "fund_name": "安信企业价值优选混合A",
                "fund_code": fund_code,
                "fund_category": "混合型",
                "management_company": "安信基金管理有限责任公司",
                "custodian": "中国银行股份有限公司",
                "inception_date": "2022 年 8 月 8 日",
                "classified_fund_type": classified_fund_type,
                "classification_basis": ("fixture basis",),
            },
            "basic_identity",
        ),
        product_profile=_field({"investment_scope": "股票等"}, "investment_scope"),
        benchmark=_field({"benchmark_text": "沪深300指数收益率"}, "benchmark"),
        index_profile=index_profile,
        fee_schedule=_field({"management_fee": "1.20%", "custody_fee": "0.20%"}, "fee_schedule"),
        turnover_rate=_field(None, "turnover_rate", extraction_mode="missing", note="fixture missing"),
        nav_benchmark_performance=_field({"nav_growth_rate": "1%", "benchmark_return_rate": "0.5%"}, "performance"),
        investor_return=_field(
            {"investor_return_rate": None, "disclosure_status": "missing"},
            "investor_return",
            extraction_mode="missing",
            note="fixture investor return missing",
        ),
        tracking_error=tracking_error,
        share_change=_field({"beginning_share": "1", "ending_share": "2", "net_change": "1"}, "share_change"),
        manager_alignment=_field(None, "manager_alignment", extraction_mode="missing", note="fixture missing"),
        manager_strategy_text=_field({"strategy_summary": "精选个股"}, "manager_strategy_text"),
        holdings_snapshot=_field(
            {
                "top_holdings": [{"name": "A"}],
                "top_holdings_status": "direct_top_ten",
                "top_holdings_source": "top_ten",
                "industry_distribution_status": "missing",
            },
            "holdings_snapshot",
        ),
        holder_structure=_field({"institutional_holder": "10%", "individual_holder": "90%"}, "holder_structure"),
        nav_data=NavDataResult(
            fund_code=fund_code,
            records=[{"date": "2024-12-31", "nav": "1.00"}],
            source="fixture",
            cached=True,
        ),
    )


def _field(
    value: dict[str, object] | None,
    row_locator: str,
    *,
    extraction_mode: str = "direct",
    note: str | None = None,
) -> ExtractedField[dict[str, object]]:
    """构造测试用抽取字段。

    Args:
        value: 字段值。
        row_locator: 行级定位。
        extraction_mode: 抽取模式。
        note: 附加说明。

    Returns:
        fake `ExtractedField`。

    Raises:
        无显式抛出。
    """

    anchors = ()
    if extraction_mode != "missing":
        anchors = (
            EvidenceAnchor(
                source_kind="annual_report",
                document_year=2024,
                section_id="§2",
                page_number=3,
                table_id="page-3-table-0",
                row_locator=row_locator,
                note=f"{row_locator}: fixture",
            ),
        )
    return ExtractedField(
        value=value,
        anchors=anchors,
        extraction_mode=extraction_mode,  # type: ignore[arg-type]
        note=note,
    )
