"""五类基金 ProcessorRegistry 与 extractor-output 集成正确性测试。

本测试只使用 accepted retained excerpt oracle 构造内存 `ParsedAnnualReport`，
通过 fake repository/provider 验证 active/index/enhanced_index/bond/QDII 五类
基金默认抽取路径经 `FundProcessorRegistry` 分派，并显式保存 extractor output JSON。
它不读取真实 PDF、不调用真实 `FundDocumentRepository`、不触发 fallback、provider 或网络。
"""

from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Any

import pytest

from fund_agent.fund.data.nav_data import NavDataResult
from fund_agent.fund.data.nav_models import FundNavSeries, NavDataContractError
from fund_agent.fund.data_extractor import FundDataExtractor
from fund_agent.fund.documents.models import ParsedAnnualReport
from fund_agent.fund.extractor_output_repository import (
    EXTRACTOR_OUTPUT_FILENAME,
    ExtractorOutputRepository,
)
from fund_agent.fund.fund_type import FundType
from fund_agent.fund.processors.contracts import FundProcessorDispatchKey
from fund_agent.fund.processors.registry import FundProcessorRegistry
from tests.fund.small_golden_oracle_helpers import (
    EQUITY_LIKE_HOLDINGS_ROWS,
    EXPECTED_ACCEPTED_FUND_CODES,
    EXPECTED_FUND_TYPE_BY_CODE,
    EXPECTED_REPORT_YEAR,
    build_report_from_oracle_row,
    oracle_expected,
    oracle_rows_by_fund_code,
)

EXPECTED_FIVE_TYPE_CODES = ("004393", "004194", "006597", "110020", "017641")
EXPECTED_TRACKING_ERROR_DIRECT_CODES = {"110020"}
EXPECTED_QDII_CODE = "017641"


class _FakeAnnualReportRepository:
    """测试用年报仓库，只返回预置内存年报。"""

    def __init__(self, reports: dict[str, ParsedAnnualReport]) -> None:
        """初始化测试仓库。

        Args:
            reports: 以基金代码为 key 的内存年报。

        Returns:
            无返回值。

        Raises:
            无显式抛出。
        """

        self.reports = reports
        self.calls: list[tuple[str, int, bool]] = []

    async def load_annual_report(
        self,
        fund_code: str,
        year: int,
        *,
        force_refresh: bool = False,
    ) -> ParsedAnnualReport:
        """返回指定基金代码和年份的内存年报。

        Args:
            fund_code: 基金代码。
            year: 年报年份。
            force_refresh: 是否强制刷新。

        Returns:
            对应的 `ParsedAnnualReport`。

        Raises:
            AssertionError: 请求身份不是当前 gate 的 accepted oracle 行。
        """

        self.calls.append((fund_code, year, force_refresh))
        assert year == EXPECTED_REPORT_YEAR
        return self.reports[fund_code]


class _FakeNavProvider:
    """测试用 NAV provider，避免真实 provider 或网络。"""

    def __init__(self) -> None:
        """初始化测试 provider。

        Args:
            无。

        Returns:
            无返回值。

        Raises:
            无显式抛出。
        """

        self.calls: list[tuple[str, bool]] = []

    async def load_nav_data(self, fund_code: str, *, force_refresh: bool = False) -> NavDataResult:
        """返回稳定空 NAV fixture。

        Args:
            fund_code: 基金代码。
            force_refresh: 是否强制刷新。

        Returns:
            测试用 NAV 数据。

        Raises:
            无显式抛出。
        """

        self.calls.append((fund_code, force_refresh))
        return NavDataResult(
            fund_code=fund_code,
            records=[{"date": "2024-12-31", "nav": 1.0}],
            source="fixture",
            cached=True,
        )


class _FakeNavSeriesRepository:
    """测试用 typed NAV repository，避免债券回撤触发真实 NAV source。"""

    def __init__(self) -> None:
        """初始化测试 repository。

        Args:
            无。

        Returns:
            无返回值。

        Raises:
            无显式抛出。
        """

        self.calls: list[tuple[str, str | None, date | None, date | None, int | None, bool]] = []

    async def load_nav_series(
        self,
        fund_code: str,
        *,
        share_class: str | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
        minimum_records: int | None = None,
        force_refresh: bool = False,
    ) -> FundNavSeries:
        """记录债券基金 typed NAV 请求并返回显式 unavailable。

        Args:
            fund_code: 基金代码。
            share_class: 份额类别。
            start_date: 起始日期。
            end_date: 截止日期。
            minimum_records: 最少记录数。
            force_refresh: 是否强制刷新。

        Returns:
            无返回值。

        Raises:
            NavDataContractError: 始终抛出，作为离线测试的显式 unavailable 缺口。
        """

        self.calls.append(
            (fund_code, share_class, start_date, end_date, minimum_records, force_refresh)
        )
        raise NavDataContractError(
            category="unavailable",
            message="offline fixture does not provide typed NAV series",
            source="fixture",
            fund_code=fund_code,
        )


class _RecordingRegistry:
    """记录 resolve context 并委托默认 `FundProcessorRegistry`。"""

    def __init__(self) -> None:
        """初始化记录型 registry。

        Args:
            无。

        Returns:
            无返回值。

        Raises:
            无显式抛出。
        """

        self.delegate = FundProcessorRegistry.create_default()
        self.resolved_contexts: list[FundProcessorDispatchKey] = []

    def resolve(self, context: FundProcessorDispatchKey):
        """记录 processor resolve 请求并委托默认 registry。

        Args:
            context: Processor 路由键。

        Returns:
            默认 registry 解析出的 processor。

        Raises:
            UnsupportedFundProcessorError: 默认 registry 不支持当前 context 时抛出。
        """

        self.resolved_contexts.append(context)
        return self.delegate.resolve(context)


def _build_reports() -> dict[str, ParsedAnnualReport]:
    """从 accepted retained excerpt oracle 构造五类内存年报。

    Args:
        无。

    Returns:
        以基金代码为 key 的 `ParsedAnnualReport`。

    Raises:
        KeyError: oracle 缺少当前 gate 必需字段。
    """

    rows = oracle_rows_by_fund_code()
    assert tuple(sorted(EXPECTED_ACCEPTED_FUND_CODES)) == tuple(sorted(EXPECTED_FIVE_TYPE_CODES))
    return {
        fund_code: build_report_from_oracle_row(
            rows[fund_code],
            include_manager=True,
            include_holdings=fund_code in EQUITY_LIKE_HOLDINGS_ROWS,
            include_bond_holdings=fund_code == "006597",
            include_target_fund_holding=fund_code == "110020",
        )
        for fund_code in EXPECTED_FIVE_TYPE_CODES
    }


def _expected_fund_type(fund_code: str) -> FundType:
    """返回当前 gate 接受的基金类型。

    Args:
        fund_code: 基金代码。

    Returns:
        标准基金类型。

    Raises:
        AssertionError: oracle 中的基金类型不是 `FundType` 闭集成员。
    """

    fund_type = EXPECTED_FUND_TYPE_BY_CODE[fund_code]
    assert fund_type in {
        "active_fund",
        "index_fund",
        "enhanced_index",
        "bond_fund",
        "qdii_fund",
    }
    return fund_type  # type: ignore[return-value]


def _assert_bundle_matches_oracle(
    *,
    fund_code: str,
    bundle_payload: dict[str, Any],
) -> None:
    """断言 bundle JSON payload 保留 oracle 驱动的核心字段。

    Args:
        fund_code: 基金代码。
        bundle_payload: `ExtractorOutputRepository` 保存或加载的 bundle payload。

    Returns:
        无返回值。

    Raises:
        AssertionError: 任一核心字段未匹配 oracle。
    """

    row = oracle_rows_by_fund_code()[fund_code]
    identity_expected = oracle_expected(row, "identity")
    benchmark_expected = oracle_expected(row, "benchmark")
    fee_expected = oracle_expected(row, "fee")
    return_expected = oracle_expected(row, "return")

    basic_identity = bundle_payload["basic_identity"]
    benchmark = bundle_payload["benchmark"]
    fee_schedule = bundle_payload["fee_schedule"]
    performance = bundle_payload["nav_benchmark_performance"]
    risk_text = bundle_payload["risk_characteristic_text"]
    portfolio_managers = bundle_payload["portfolio_managers"]
    tracking_error = bundle_payload["tracking_error"]

    assert basic_identity["value"]["fund_code"] == fund_code
    assert basic_identity["value"]["fund_name"] == identity_expected["fund_name"]
    assert basic_identity["value"]["classified_fund_type"] == _expected_fund_type(fund_code)
    assert benchmark["value"]["benchmark_text"] == benchmark_expected
    assert fee_schedule["value"]["management_fee"] == fee_expected["management_fee_rate"]
    assert fee_schedule["value"]["custody_fee"] == fee_expected["custodian_fee_rate"]
    assert (
        performance["value"]["nav_growth_rate"]
        == return_expected["target_share_one_year_nav_growth"]
    )
    assert (
        performance["value"]["benchmark_return_rate"]
        == return_expected["one_year_benchmark_return"]
    )
    assert risk_text["value"]["risk_characteristic_text"] == oracle_expected(row, "risk")
    assert portfolio_managers["value"]["schema_version"] == "portfolio_manager_tenure_list.v1"
    actual_managers = portfolio_managers["value"]["portfolio_managers"]
    expected_managers = oracle_expected(row, "manager")
    assert len(actual_managers) == len(expected_managers)
    for actual_manager, expected_manager in zip(
        actual_managers,
        expected_managers,
        strict=True,
    ):
        assert actual_manager["name"] == expected_manager["name"]
        assert actual_manager["role"] == expected_manager["role"]
        assert actual_manager["start_date"] == expected_manager["start_date"]
        if "end_date" in expected_manager:
            assert actual_manager["end_date"] == expected_manager["end_date"]
    if fund_code in EXPECTED_TRACKING_ERROR_DIRECT_CODES:
        assert tracking_error["value"]["value_text"] == return_expected["annual_tracking_error"]
    elif fund_code == EXPECTED_QDII_CODE:
        assert tracking_error["extraction_mode"] == "missing"
        assert tracking_error["note"] == "QDII 基金当前不适用 P13 跟踪误差规则"
    elif _expected_fund_type(fund_code) in {"index_fund", "enhanced_index"}:
        assert tracking_error["extraction_mode"] == "missing"
        assert tracking_error["note"] == "field_not_in_family:return_attribution.v1:tracking_error"
    else:
        assert tracking_error["extraction_mode"] == "missing"
        assert tracking_error["note"] == "非指数基金不适用跟踪误差"


@pytest.mark.asyncio
@pytest.mark.parametrize("fund_code", EXPECTED_FIVE_TYPE_CODES)
async def test_five_accepted_fund_types_route_through_registry_and_save_output(
    fund_code: str,
    tmp_path: Path,
) -> None:
    """验证五类 accepted fund 经 registry 抽取并显式保存 extractor output。

    Args:
        fund_code: 参数化基金代码。
        tmp_path: extractor output 临时根目录。

    Returns:
        无返回值。

    Raises:
        AssertionError: route、字段或落盘结构不符合当前 gate 契约。
    """

    reports = _build_reports()
    annual_report_repository = _FakeAnnualReportRepository(reports)
    nav_provider = _FakeNavProvider()
    nav_series_repository = _FakeNavSeriesRepository()
    processor_registry = _RecordingRegistry()
    extractor = FundDataExtractor(
        repository=annual_report_repository,
        nav_provider=nav_provider,
        nav_series_repository=nav_series_repository,
        processor_registry=processor_registry,  # type: ignore[arg-type]
    )

    bundle = await extractor.extract(fund_code, EXPECTED_REPORT_YEAR)

    assert annual_report_repository.calls == [(fund_code, EXPECTED_REPORT_YEAR, False)]
    assert nav_provider.calls == [(fund_code, False)]
    assert len(processor_registry.resolved_contexts) == 1
    context = processor_registry.resolved_contexts[0]
    assert context.fund_code == fund_code
    assert context.document_year == EXPECTED_REPORT_YEAR
    assert context.fund_type == _expected_fund_type(fund_code)
    assert context.report_type == "annual_report"
    assert context.intermediate_kind == "parsed_annual_report.v1"
    assert context.source_kind == "annual_report"
    if fund_code == "006597":
        assert nav_series_repository.calls == [
            (fund_code, "A", date(2024, 1, 1), date(2024, 12, 31), 30, False)
        ]
    else:
        assert nav_series_repository.calls == []

    output_repository = ExtractorOutputRepository(root_dir=tmp_path)
    saved_record = output_repository.save(bundle=bundle)
    loaded_record = output_repository.load(
        fund_code=fund_code,
        report_type="annual_report",
        report_year=EXPECTED_REPORT_YEAR,
    )

    expected_path = (
        tmp_path
        / fund_code
        / "annual_report"
        / str(EXPECTED_REPORT_YEAR)
        / EXTRACTOR_OUTPUT_FILENAME
    )
    assert saved_record.path == expected_path
    assert loaded_record.path == expected_path
    assert saved_record.bundle_payload == loaded_record.bundle_payload
    assert loaded_record.bundle_payload["fund_code"] == fund_code
    assert loaded_record.bundle_payload["report_year"] == EXPECTED_REPORT_YEAR
    assert loaded_record.bundle_payload["source_provenance"][
        "source_provenance_schema_version"
    ] == "repository_source_provenance.v2"
    assert loaded_record.bundle_payload["nav_data"]["source"] == "fixture"
    _assert_bundle_matches_oracle(
        fund_code=fund_code,
        bundle_payload=loaded_record.bundle_payload,
    )
