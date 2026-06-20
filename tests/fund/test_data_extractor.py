"""P1 结构化数据 façade 测试。"""

from __future__ import annotations

import ast
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from pathlib import Path
from typing import Literal

import pytest

from fund_agent.fund.data.nav_data import NavDataResult
from fund_agent.fund.data.nav_models import (
    FundNavRecord,
    FundNavSeries,
    NavDataContractError,
    NavSourceMetadata,
    ShareClassMapping,
)
from fund_agent.fund.data_extractor import FundDataExtractor, StructuredFundDataBundle
from fund_agent.fund.documents.models import (
    AnnualReportMetadata,
    AnnualReportSourceMetadata,
    DocumentKey,
    ParsedAnnualReport,
    ParsedTable,
    ReportSection,
)
from fund_agent.fund.extractors import ExtractedField
from fund_agent.fund.extractors import bond_risk_evidence as bond_risk_module
from fund_agent.fund.extractors.models import EvidenceAnchor
from fund_agent.fund.processors.contracts import (
    AnnualReportSourceFailureCategory,
    CandidateBoundaryStatus,
    FundDisclosureSourceTruthAdmissionProof,
    FundProcessorDispatchKey,
    FundFieldFamilyResult,
    FundProcessorInput,
    FundProcessorResult,
)
from fund_agent.fund.processors.registry import (
    FundProcessorRegistry,
    UnsupportedFundProcessorError,
)
from fund_agent.fund.source_provenance import (
    PublicSourceProvenance,
    default_public_source_provenance,
)


class _FakeRepository:
    """测试用年报仓库。"""

    def __init__(self, result: ParsedAnnualReport | Exception) -> None:
        """初始化测试仓库。

        Args:
            result: 预置年报或待抛异常。

        Returns:
            无返回值。

        Raises:
            无显式抛出。
        """

        self.result = result
        self.calls: list[tuple[str, int, bool]] = []

    async def load_annual_report(
        self,
        fund_code: str,
        year: int,
        *,
        force_refresh: bool = False,
    ) -> ParsedAnnualReport:
        """返回预置年报或抛出预置异常。

        Args:
            fund_code: 基金代码。
            year: 年报年份。
            force_refresh: 是否强制刷新。

        Returns:
            预置年报。

        Raises:
            Exception: 当初始化传入异常时抛出。
        """

        self.calls.append((fund_code, year, force_refresh))
        if isinstance(self.result, Exception):
            raise self.result
        return self.result


class _FailingNavProvider:
    """测试用失败净值 provider。"""

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
        """记录调用并模拟外部净值失败。

        Args:
            fund_code: 基金代码。
            force_refresh: 是否强制刷新。

        Returns:
            无返回值。

        Raises:
            RuntimeError: 始终抛出网络失败。
        """

        self.calls.append((fund_code, force_refresh))
        raise RuntimeError("network down")


class _RecordingNavProvider:
    """测试用记录调用的净值 provider。"""

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
        """记录调用并返回空净值数据。

        Args:
            fund_code: 基金代码。
            force_refresh: 是否强制刷新。

        Returns:
            空净值数据。

        Raises:
            无显式抛出。
        """

        self.calls.append((fund_code, force_refresh))
        return NavDataResult(fund_code=fund_code, records=[], source="fixture", cached=False)


class _RecordingNavSeriesRepository:
    """测试用 typed NAV series repository。"""

    def __init__(self, result: FundNavSeries | Exception) -> None:
        """初始化测试 repository。

        Args:
            result: 预置 NAV series 或待抛异常。

        Returns:
            无返回值。

        Raises:
            无显式抛出。
        """

        self.result = result
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
        """记录 typed NAV 请求并返回预置结果。

        Args:
            fund_code: 基金代码。
            share_class: 份额类别。
            start_date: 起始日期。
            end_date: 截止日期。
            minimum_records: 最少记录数。
            force_refresh: 是否强制刷新。

        Returns:
            预置 `FundNavSeries`。

        Raises:
            Exception: 当初始化传入异常时抛出。
        """

        self.calls.append(
            (fund_code, share_class, start_date, end_date, minimum_records, force_refresh)
        )
        if isinstance(self.result, Exception):
            raise self.result
        return self.result


@pytest.mark.asyncio
async def test_data_extractor_degrades_nav_failure_without_blocking_annual_report() -> None:
    """验证 NAV 外部失败不会阻断年报结构化抽取。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 NAV 失败阻断年报抽取或原因丢失时抛出。
    """

    repository = _FakeRepository(_annual_report())
    nav_provider = _FailingNavProvider()
    extractor = FundDataExtractor(repository=repository, nav_provider=nav_provider)

    bundle = await extractor.extract("110011", 2024, force_refresh=True)

    assert repository.calls == [("110011", 2024, True)]
    assert nav_provider.calls == [("110011", True)]
    assert bundle.fund_code == "110011"
    assert bundle.basic_identity.value is not None
    assert bundle.nav_data.records == []
    assert bundle.nav_data.source == "nav_unavailable"
    assert bundle.nav_data.cached is False
    assert bundle.nav_data.unavailable is True
    assert bundle.nav_data.unavailable_reason == "RuntimeError: network down"
    assert bundle.source_provenance.fallback_eligibility == "not_applicable"
    assert bundle.source_provenance.source_provenance_status == "not_applicable"
    assert bundle.bond_risk_evidence.value is None
    assert bundle.bond_risk_evidence.extraction_mode == "missing"
    assert bundle.bond_risk_evidence.note == "not_applicable_non_bond_fund"


@pytest.mark.asyncio
async def test_data_extractor_does_not_mask_repository_failure() -> None:
    """验证年报仓库失败不会被 NAV 降级吞掉。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当仓库异常被误吞或 NAV 被误调用时抛出。
    """

    repository = _FakeRepository(RuntimeError("identity_mismatch fixture"))
    nav_provider = _RecordingNavProvider()
    extractor = FundDataExtractor(repository=repository, nav_provider=nav_provider)

    with pytest.raises(RuntimeError, match="identity_mismatch fixture"):
        await extractor.extract("110011", 2024, force_refresh=True)

    assert repository.calls == [("110011", 2024, True)]
    assert nav_provider.calls == []


def test_structured_bundle_default_source_provenance_is_not_none() -> None:
    """验证 fake bundle 未显式传 provenance 时使用安全默认值。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 bundle provenance 为 `None` 或非 not_applicable 时抛出。
    """

    report = _annual_report()
    bundle = StructuredFundDataBundle(
        fund_code=report.key.fund_code,
        report_year=report.key.year,
        basic_identity=_fake_field(),
        product_profile=_fake_field(),
        benchmark=_fake_field(),
        index_profile=_fake_field(),
        fee_schedule=_fake_field(),
        turnover_rate=_fake_field(),
        nav_benchmark_performance=_fake_field(),
        investor_return=_fake_field(),
        tracking_error=_fake_field(),
        share_change=_fake_field(),
        manager_alignment=_fake_field(),
        manager_strategy_text=_fake_field(),
        holdings_snapshot=_fake_field(),
        holder_structure=_fake_field(),
        nav_data=NavDataResult(fund_code="110011", records=[], source="fixture", cached=False),
    )

    assert bundle.source_provenance is not None
    assert bundle.source_provenance.fallback_used is False
    assert bundle.source_provenance.fallback_eligibility == "not_applicable"
    assert bundle.source_provenance.source_provenance_status == "not_applicable"
    assert bundle.bond_risk_evidence.value is None
    assert bundle.bond_risk_evidence.note == "bond_risk_evidence_not_extracted"
    assert bundle.portfolio_managers.value is None
    assert bundle.portfolio_managers.note == "portfolio_managers_not_extracted"
    assert bundle.risk_characteristic_text.value is None
    assert bundle.risk_characteristic_text.note == "risk_characteristic_text_not_extracted"


@pytest.mark.asyncio
async def test_data_extractor_returns_bundle_with_bond_risk_evidence() -> None:
    """验证 fake 仓库抽取结果显式携带债券风险证据字段。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 bundle 未携带债券风险证据字段或 provenance 行为改变时抛出。
    """

    repository = _FakeRepository(_annual_report())
    nav_provider = _RecordingNavProvider()
    extractor = FundDataExtractor(repository=repository, nav_provider=nav_provider)

    bundle = await extractor.extract("110011", 2024)

    assert repository.calls == [("110011", 2024, False)]
    assert nav_provider.calls == [("110011", False)]
    assert bundle.bond_risk_evidence.value is None
    assert bundle.bond_risk_evidence.anchors == ()
    assert bundle.bond_risk_evidence.extraction_mode == "missing"
    assert bundle.bond_risk_evidence.note == "not_applicable_non_bond_fund"
    assert bundle.portfolio_managers.extraction_mode == "direct"
    assert bundle.portfolio_managers.note is None
    assert bundle.portfolio_managers.value is not None
    assert bundle.portfolio_managers.value["schema_version"] == "portfolio_manager_tenure_list.v1"
    assert bundle.portfolio_managers.value["fund_code"] == "110011"
    assert bundle.portfolio_managers.value["report_year"] == 2024
    assert bundle.portfolio_managers.value["portfolio_managers"] == [
        {
            "name": "张三",
            "role": "基金经理",
            "start_date": "2021-01-01",
            "source_anchor": {
                "section_id": "§4",
                "section_title": "4.1.2 基金经理简介",
                "page_number": 22,
                "table_id": "page-22-table-0",
                "row_locator": "portfolio_manager:张三",
            },
        }
    ]
    assert "portfolio_manager:张三" in {
        anchor.row_locator for anchor in bundle.portfolio_managers.anchors
    }
    assert bundle.risk_characteristic_text.extraction_mode == "direct"
    assert bundle.risk_characteristic_text.note is None
    assert bundle.risk_characteristic_text.value == {
        "schema_version": "risk_characteristic_text.v1",
        "fund_code": "110011",
        "report_year": 2024,
        "risk_characteristic_text": "本基金为混合型基金，风险收益特征高于债券型基金。",
        "source_anchors": [
            {
                "section_id": "§2",
                "page_number": 5,
                "table_id": "page-5-table-1",
                "row_locator": "risk_characteristic_text",
            }
        ],
    }
    assert "risk_characteristic_text" in {
        anchor.row_locator for anchor in bundle.risk_characteristic_text.anchors
    }
    assert bundle.source_provenance.fallback_used is False
    assert bundle.source_provenance.fallback_eligibility == "not_applicable"
    assert bundle.source_provenance.source_provenance_status == "not_applicable"


@pytest.mark.asyncio
async def test_data_extractor_non_bond_bond_risk_evidence_does_not_scan_groups(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """验证非债券基金通过显式分类早退，不扫描模板第 6 章七组债券风险证据。

    Args:
        monkeypatch: pytest 局部 monkeypatch 工具。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当非债券路径扫描七组 extractor 或产生满足组时抛出。
    """

    def _fail_group_scan(_report: ParsedAnnualReport) -> object:
        """非债券路径若触发七组扫描则使测试失败。

        Args:
            _report: 已解析年报。

        Returns:
            无返回值。

        Raises:
            AssertionError: 始终抛出，表示不应扫描七组债券风险证据。
        """

        raise AssertionError("non-bond path must not scan bond evidence groups")

    monkeypatch.setattr(bond_risk_module, "_extract_duration_rate_risk", _fail_group_scan)
    extractor = FundDataExtractor(
        repository=_FakeRepository(_annual_report()),
        nav_provider=_RecordingNavProvider(),
        nav_series_repository=_RecordingNavSeriesRepository(
            RuntimeError("must not call typed NAV")
        ),
    )

    bundle = await extractor.extract("110011", 2024)

    assert bundle.basic_identity.value is not None
    assert bundle.basic_identity.value["classified_fund_type"] == "active_fund"
    assert bundle.bond_risk_evidence.value is None
    assert bundle.bond_risk_evidence.anchors == ()
    assert bundle.bond_risk_evidence.extraction_mode == "missing"
    assert bundle.bond_risk_evidence.note == "not_applicable_non_bond_fund"


@pytest.mark.asyncio
async def test_data_extractor_bond_fund_uses_a_share_nav_metric_without_mixing_classes() -> None:
    """验证债券基金只通过 typed repository 加载 006597/A 年度最大回撤。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 typed NAV 调用参数、份额混合或证据投影错误时抛出。
    """

    nav_series_repository = _RecordingNavSeriesRepository(_nav_series())
    extractor = FundDataExtractor(
        repository=_FakeRepository(_bond_annual_report()),
        nav_provider=_RecordingNavProvider(),
        nav_series_repository=nav_series_repository,
    )

    bundle = await extractor.extract("006597", 2024, force_refresh=True)

    assert nav_series_repository.calls == [
        ("006597", "A", date(2024, 1, 1), date(2024, 12, 31), 30, True)
    ]
    assert bundle.bond_risk_evidence.value is not None
    group = next(
        group
        for group in bundle.bond_risk_evidence.value.groups
        if group.group_id == "drawdown_stress"
    )
    assert group.status == "accepted"
    assert group.strength == "quantitative_derived"
    assert group.measurement_kind == "derived_metric"
    assert group.metric_value == "-10.00%"
    assert "drawdown_stress" in bundle.bond_risk_evidence.value.satisfied_group_ids


@pytest.mark.asyncio
async def test_data_extractor_raw_unit_nav_error_keeps_drawdown_weak() -> None:
    """验证 raw-unit 或不合格 NAV 失败不会把回撤组提升为 accepted。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当不合格 NAV 被当成强回撤证据时抛出。
    """

    nav_series_repository = _RecordingNavSeriesRepository(
        NavDataContractError(
            category="adjustment_basis_unknown",
            message="raw_unit_nav fixture",
            source="fixture",
            fund_code="006597",
        )
    )
    extractor = FundDataExtractor(
        repository=_FakeRepository(_bond_annual_report()),
        nav_provider=_RecordingNavProvider(),
        nav_series_repository=nav_series_repository,
    )

    bundle = await extractor.extract("006597", 2024)

    assert nav_series_repository.calls == [
        ("006597", "A", date(2024, 1, 1), date(2024, 12, 31), 30, False)
    ]
    assert bundle.bond_risk_evidence.value is not None
    group = next(
        group
        for group in bundle.bond_risk_evidence.value.groups
        if group.group_id == "drawdown_stress"
    )
    assert group.status == "weak"
    assert group.strength == "qualitative_control_intent"
    assert group.na_reason == "drawdown_nav_adjustment_basis_unknown"
    assert "drawdown_stress" in bundle.bond_risk_evidence.value.weak_group_ids


@pytest.mark.asyncio
async def test_data_extractor_projects_primary_source_metadata() -> None:
    """验证生产 extractor 从年报元数据投影主源 provenance。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当生产路径没有读取 `ParsedAnnualReport.metadata.source` 时抛出。
    """

    repository = _FakeRepository(
        _annual_report(
            source_metadata=AnnualReportSourceMetadata(
                source="eid",
                fallback_used=False,
                selected_source="eid",
                source_mode="single_source_only",
                fallback_enabled=False,
            )
        )
    )
    extractor = FundDataExtractor(repository=repository, nav_provider=_RecordingNavProvider())

    bundle = await extractor.extract("110011", 2024)

    assert bundle.source_provenance.source_strategy == "single_source_only"
    assert bundle.source_provenance.selected_source == "eid"
    assert bundle.source_provenance.source_mode == "single_source_only"
    assert bundle.source_provenance.fallback_enabled is False
    assert bundle.source_provenance.resolved_source_name == "eid"
    assert bundle.source_provenance.fallback_used is False
    assert bundle.source_provenance.fallback_eligibility == "not_applicable"
    assert bundle.source_provenance.source_provenance_status == "not_applicable"


@pytest.mark.asyncio
async def test_data_extractor_projects_fallback_metadata_as_unknown_when_category_absent() -> None:
    """验证生产 extractor 对缺少失败分类的 fallback 保持 unknown。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当缺少失败分类的 fallback 被推断为 eligible 时抛出。
    """

    repository = _FakeRepository(
        _annual_report(
            source_metadata=AnnualReportSourceMetadata(source="eastmoney", fallback_used=True)
        )
    )
    extractor = FundDataExtractor(repository=repository, nav_provider=_RecordingNavProvider())

    bundle = await extractor.extract("110011", 2024)

    assert bundle.source_provenance.source_strategy == "legacy_or_unknown"
    assert bundle.source_provenance.selected_source is None
    assert bundle.source_provenance.source_mode == "legacy_or_unknown"
    assert bundle.source_provenance.fallback_enabled is None
    assert bundle.source_provenance.resolved_source_name == "eastmoney"
    assert bundle.source_provenance.fallback_used is True
    assert bundle.source_provenance.primary_failure_category is None
    assert bundle.source_provenance.fallback_eligibility == "unknown_public_metadata_absent"
    assert bundle.source_provenance.source_provenance_status == "incomplete"


@pytest.mark.asyncio
async def test_data_extractor_projects_metadata_primary_failure_category() -> None:
    """验证生产 extractor 使用年报来源元数据中的主源失败分类。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当生产投影没有消费 metadata 分类时抛出。
    """

    repository = _FakeRepository(
        _annual_report(
            source_metadata=AnnualReportSourceMetadata(
                source="eastmoney",
                fallback_used=True,
                primary_failure_category="not_found",
            )
        )
    )
    extractor = FundDataExtractor(repository=repository, nav_provider=_RecordingNavProvider())

    bundle = await extractor.extract("110011", 2024)

    assert bundle.source_provenance.source_strategy == "legacy_or_unknown"
    assert bundle.source_provenance.selected_source is None
    assert bundle.source_provenance.source_mode == "legacy_or_unknown"
    assert bundle.source_provenance.fallback_enabled is None
    assert bundle.source_provenance.resolved_source_name == "eastmoney"
    assert bundle.source_provenance.fallback_used is True
    assert bundle.source_provenance.primary_failure_category == "not_found"
    assert bundle.source_provenance.fallback_eligibility == "eligible"
    assert bundle.source_provenance.source_provenance_status == "complete"


_MARKER_BASIC_IDENTITY = {
    "fund_name": "MARKER_PROCESSOR_PROOF",
    "fund_code": "110011",
    "classified_fund_type": "active_fund",
    "classification_basis": ("marker_processor_test",),
}


@dataclass(frozen=True, slots=True)
class _StubDisclosureIntermediate:
    """测试专用 FundDisclosureDocumentIntermediate stub。"""

    document_kind: Literal["annual_report"] = "annual_report"
    fund_code: str = "110011"
    report_year: int = 2024
    intermediate_kind: Literal["fund_disclosure_document.v1"] = "fund_disclosure_document.v1"
    source_provenance: PublicSourceProvenance | None = None
    candidate_boundary: CandidateBoundaryStatus | None = None
    failure_class: AnnualReportSourceFailureCategory | None = None
    sections: tuple[object, ...] = ()
    paragraph_blocks: tuple[object, ...] = ()
    table_blocks: tuple[object, ...] = ()
    source_truth_admission: FundDisclosureSourceTruthAdmissionProof | None = None


@dataclass(frozen=True, slots=True)
class _DisclosureCell:
    """测试专用 FundDisclosureDocument cell stub。"""

    cell_id: str
    table_id: str
    row_index: int
    column_index: int
    cell_text: str
    row_label_path: tuple[str, ...] = ()
    column_header_path: tuple[str, ...] = ()
    section_anchor: str | None = "§2"
    heading_path: tuple[str, ...] = ("收益归因",)
    locator_stability: str = "stable"

    @property
    def cell_text_normalized(self) -> str:
        """返回规范化单元格文本。"""

        return self.cell_text


@dataclass(frozen=True, slots=True)
class _DisclosureParagraph:
    """测试专用 FundDisclosureDocument paragraph stub。"""

    block_id: str
    text_raw: str
    text_normalized: str
    section_id: str | None
    heading_path: tuple[str, ...]
    locator_stability: str = "stable"


@dataclass(frozen=True, slots=True)
class _DisclosureTable:
    """测试专用 FundDisclosureDocument table stub。"""

    table_id: str
    cells: tuple[_DisclosureCell, ...]
    section_id: str | None = "§2"
    heading_text: str | None = "收益归因"
    heading_path: tuple[str, ...] = ("收益归因",)
    table_caption_or_nearby_heading: str | None = "收益归因"
    locator_stability: str = "stable"


class _RecordingRegistry(FundProcessorRegistry):
    """记录 resolve context 的测试 registry。"""

    def __init__(self) -> None:
        """初始化记录型 registry。"""

        super().__init__()
        self.resolved_contexts: list[FundProcessorDispatchKey] = []

    def resolve(self, context: FundProcessorDispatchKey):
        """记录 resolve 请求并委托父类解析。"""

        self.resolved_contexts.append(context)
        return super().resolve(context)


class _MarkerActiveFundProcessor:
    """返回标记值以证明字段来自 processor 路径而非 direct extractor。"""

    processor_id = "marker_test.active_fund"
    priority = 999
    output_schema_version = "test_marker.v1"

    def supports(self, context: FundProcessorDispatchKey) -> bool:
        return (
            context.fund_type == "active_fund"
            and context.report_type == "annual_report"
            and context.intermediate_kind == "parsed_annual_report.v1"
        )

    def extract(self, input_data: FundProcessorInput) -> FundProcessorResult:
        marker_anchor = EvidenceAnchor(
            source_kind="annual_report",
            document_year=2024,
            section_id="marker",
            page_number=1,
            table_id="marker-table",
            row_locator="marker_row",
            note=None,
        )
        families: tuple[FundFieldFamilyResult, ...] = (
            FundFieldFamilyResult(
                field_family_id="product_essence.v1",
                chapter_ids=(1,),
                value={
                    "schema_version": "product_essence.v1",
                    "basic_identity": _MARKER_BASIC_IDENTITY,
                    "product_profile": {"marker": "product_profile_from_processor"},
                    "benchmark": {"marker": "benchmark_from_processor"},
                    "risk_characteristic_text": {"marker": "risk_text_from_processor"},
                },
                status="accepted",
                extraction_mode="direct",
                anchors=(marker_anchor,),
                gaps=(),
                source_provenance=input_data.source_provenance,
            ),
            FundFieldFamilyResult(
                field_family_id="return_attribution.v1",
                chapter_ids=(2,),
                value={
                    "schema_version": "return_attribution.v1",
                    "fee_schedule": {"marker": "fee_from_processor"},
                    "nav_benchmark_performance": {"marker": "perf_from_processor"},
                    "tracking_error": {"marker": "tracking_from_processor"},
                },
                status="accepted",
                extraction_mode="direct",
                anchors=(marker_anchor,),
                gaps=(),
                source_provenance=input_data.source_provenance,
            ),
            FundFieldFamilyResult(
                field_family_id="manager_profile.v1",
                chapter_ids=(3,),
                value={
                    "schema_version": "manager_profile.v1",
                    "portfolio_managers": {"marker": "portfolio_managers_from_processor"},
                    "turnover_rate": {"marker": "turnover_from_processor"},
                    "manager_alignment": {"marker": "alignment_from_processor"},
                    "manager_strategy_text": {"marker": "strategy_from_processor"},
                    "holdings_snapshot": {"marker": "holdings_from_processor"},
                },
                status="accepted",
                extraction_mode="direct",
                anchors=(marker_anchor,),
                gaps=(),
                source_provenance=input_data.source_provenance,
            ),
            FundFieldFamilyResult(
                field_family_id="investor_experience.v1",
                chapter_ids=(4,),
                value={
                    "schema_version": "investor_experience.v1",
                    "investor_return": {"marker": "investor_return_from_processor"},
                    "holder_structure": {"marker": "holder_from_processor"},
                    "share_change": {"marker": "share_change_from_processor"},
                },
                status="accepted",
                extraction_mode="direct",
                anchors=(marker_anchor,),
                gaps=(),
                source_provenance=input_data.source_provenance,
            ),
            FundFieldFamilyResult(
                field_family_id="current_stage.v1",
                chapter_ids=(5,),
                value={
                    "schema_version": "current_stage.v1",
                    "basic_identity": {"marker": "current_stage_basic_identity_must_not_project"},
                    "share_change": {"marker": "current_stage_share_must_not_project"},
                    "holdings_snapshot": {"marker": "current_stage_holdings_must_not_project"},
                    "portfolio_managers": {"marker": "current_stage_portfolio_must_not_project"},
                },
                status="accepted",
                extraction_mode="direct",
                anchors=(marker_anchor,),
                gaps=(),
                source_provenance=input_data.source_provenance,
            ),
            FundFieldFamilyResult(
                field_family_id="core_risk.v1",
                chapter_ids=(6,),
                value={"schema_version": "core_risk.v1"},
                status="not_applicable",
                extraction_mode="not_applicable",
                anchors=(),
                gaps=(),
                source_provenance=input_data.source_provenance,
            ),
        )
        return FundProcessorResult(
            processor_id=self.processor_id,
            output_schema_version=self.output_schema_version,
            fund_code=input_data.context.fund_code,
            report_year=input_data.context.document_year,
            fund_type="active_fund",
            report_type="annual_report",
            input_intermediate_kind="parsed_annual_report.v1",
            field_families=families,
            gaps=(),
            anchors=(marker_anchor,),
            source_provenance=input_data.source_provenance,
            candidate_boundary=None,
            contract_status="satisfied",
        )


class _MarkerDisclosureProcessor:
    """返回标记值以证明 explicit disclosure route 经过 registry。"""

    processor_id = "marker_test.fund_disclosure_document"
    priority = 999
    output_schema_version = "test_marker_disclosure.v1"

    def supports(self, context: FundProcessorDispatchKey) -> bool:
        return (
            context.fund_type == "active_fund"
            and context.report_type == "annual_report"
            and context.intermediate_kind == "fund_disclosure_document.v1"
        )

    def extract(self, input_data: FundProcessorInput) -> FundProcessorResult:
        marker_anchor = EvidenceAnchor(
            source_kind="annual_report",
            document_year=2024,
            section_id="marker",
            page_number=1,
            table_id="marker-table",
            row_locator="disclosure_marker_row",
            note=None,
        )
        families: tuple[FundFieldFamilyResult, ...] = (
            FundFieldFamilyResult(
                field_family_id="product_essence.v1",
                chapter_ids=(1,),
                value={
                    "schema_version": "product_essence.v1",
                    "basic_identity": {
                        **_MARKER_BASIC_IDENTITY,
                        "fund_name": "DISCLOSURE_MARKER_PROCESSOR_PROOF",
                    },
                    "product_profile": {"marker": "product_profile_from_disclosure_processor"},
                    "benchmark": {"marker": "benchmark_from_disclosure_processor"},
                    "risk_characteristic_text": {"marker": "risk_text_from_disclosure_processor"},
                },
                status="accepted",
                extraction_mode="direct",
                anchors=(marker_anchor,),
                gaps=(),
                source_provenance=input_data.source_provenance,
            ),
            FundFieldFamilyResult(
                field_family_id="return_attribution.v1",
                chapter_ids=(2,),
                value={
                    "schema_version": "return_attribution.v1",
                    "fee_schedule": {"marker": "fee_from_disclosure_processor"},
                    "nav_benchmark_performance": {"marker": "perf_from_disclosure_processor"},
                    "tracking_error": {"marker": "tracking_from_disclosure_processor"},
                },
                status="accepted",
                extraction_mode="direct",
                anchors=(marker_anchor,),
                gaps=(),
                source_provenance=input_data.source_provenance,
            ),
            FundFieldFamilyResult(
                field_family_id="manager_profile.v1",
                chapter_ids=(3,),
                value={
                    "schema_version": "manager_profile.v1",
                    "portfolio_managers": {"marker": "portfolio_from_disclosure_processor"},
                    "turnover_rate": {"marker": "turnover_from_disclosure_processor"},
                    "manager_alignment": {"marker": "alignment_from_disclosure_processor"},
                    "manager_strategy_text": {"marker": "strategy_from_disclosure_processor"},
                    "holdings_snapshot": {"marker": "holdings_from_disclosure_processor"},
                },
                status="accepted",
                extraction_mode="direct",
                anchors=(marker_anchor,),
                gaps=(),
                source_provenance=input_data.source_provenance,
            ),
            FundFieldFamilyResult(
                field_family_id="investor_experience.v1",
                chapter_ids=(4,),
                value={
                    "schema_version": "investor_experience.v1",
                    "investor_return": {"marker": "investor_from_disclosure_processor"},
                    "holder_structure": {"marker": "holder_from_disclosure_processor"},
                    "share_change": {"marker": "share_from_disclosure_processor"},
                },
                status="accepted",
                extraction_mode="direct",
                anchors=(marker_anchor,),
                gaps=(),
                source_provenance=input_data.source_provenance,
            ),
            FundFieldFamilyResult(
                field_family_id="current_stage.v1",
                chapter_ids=(5,),
                value={
                    "schema_version": "current_stage.v1",
                    "basic_identity": {"marker": "current_stage_basic_identity_must_not_project"},
                    "share_change": {"marker": "current_stage_share_must_not_project"},
                    "holdings_snapshot": {"marker": "current_stage_holdings_must_not_project"},
                    "portfolio_managers": {"marker": "current_stage_portfolio_must_not_project"},
                },
                status="accepted",
                extraction_mode="direct",
                anchors=(marker_anchor,),
                gaps=(),
                source_provenance=input_data.source_provenance,
            ),
            FundFieldFamilyResult(
                field_family_id="core_risk.v1",
                chapter_ids=(6,),
                value={"schema_version": "core_risk.v1"},
                status="not_applicable",
                extraction_mode="not_applicable",
                anchors=(),
                gaps=(),
                source_provenance=input_data.source_provenance,
            ),
        )
        return FundProcessorResult(
            processor_id=self.processor_id,
            output_schema_version=self.output_schema_version,
            fund_code=input_data.context.fund_code,
            report_year=input_data.context.document_year,
            fund_type=input_data.context.fund_type,
            report_type=input_data.context.report_type,
            input_intermediate_kind=input_data.context.intermediate_kind,
            field_families=families,
            gaps=(),
            anchors=(marker_anchor,),
            source_provenance=input_data.source_provenance,
            candidate_boundary=None,
            contract_status="satisfied",
        )


class _CoreRiskFallbackDisclosureProcessor:
    """返回 product 缺失 risk、core_risk accepted risk 的 FDD processor。"""

    processor_id = "marker_test.core_risk_fallback_disclosure"
    priority = 999
    output_schema_version = "test_core_risk_fallback.v1"

    def supports(self, context: FundProcessorDispatchKey) -> bool:
        return (
            context.fund_type == "active_fund"
            and context.report_type == "annual_report"
            and context.intermediate_kind == "fund_disclosure_document.v1"
        )

    def extract(self, input_data: FundProcessorInput) -> FundProcessorResult:
        marker_anchor = EvidenceAnchor(
            source_kind="annual_report",
            document_year=input_data.context.document_year,
            section_id="core-risk",
            page_number=None,
            table_id="core-risk-table",
            row_locator="field=risk_characteristic_text.risk_characteristic_text",
            note=None,
        )
        risk_text = {
            "schema_version": "risk_characteristic_text.v1",
            "fund_code": input_data.context.fund_code,
            "report_year": input_data.context.document_year,
            "risk_characteristic_text": "本基金为较高风险较高收益品种。",
            "source_anchors": (
                {
                    "section_id": "core-risk",
                    "page_number": None,
                    "table_id": "core-risk-table",
                    "row_locator": "field=risk_characteristic_text.risk_characteristic_text",
                },
            ),
        }
        families: tuple[FundFieldFamilyResult, ...] = (
            FundFieldFamilyResult(
                field_family_id="product_essence.v1",
                chapter_ids=(1,),
                value={
                    "schema_version": "product_essence.v1",
                    "basic_identity": _MARKER_BASIC_IDENTITY,
                },
                status="partial",
                extraction_mode="direct",
                anchors=(marker_anchor,),
                gaps=(),
                source_provenance=input_data.source_provenance,
            ),
            FundFieldFamilyResult(
                field_family_id="core_risk.v1",
                chapter_ids=(6,),
                value={
                    "schema_version": "core_risk.v1",
                    "risk_characteristic_text": risk_text,
                },
                status="accepted",
                extraction_mode="direct",
                anchors=(marker_anchor,),
                gaps=(),
                source_provenance=input_data.source_provenance,
            ),
        )
        return FundProcessorResult(
            processor_id=self.processor_id,
            output_schema_version=self.output_schema_version,
            fund_code=input_data.context.fund_code,
            report_year=input_data.context.document_year,
            fund_type=input_data.context.fund_type,
            report_type=input_data.context.report_type,
            input_intermediate_kind=input_data.context.intermediate_kind,
            field_families=families,
            gaps=(),
            anchors=(marker_anchor,),
            source_provenance=input_data.source_provenance,
            candidate_boundary=None,
            contract_status="partial",
        )


class _CoreRiskProductWinsDisclosureProcessor(_CoreRiskFallbackDisclosureProcessor):
    """返回 product/core 同时含 risk text 的 FDD processor。"""

    processor_id = "marker_test.core_risk_product_wins_disclosure"
    output_schema_version = "test_core_risk_product_wins.v1"

    def extract(self, input_data: FundProcessorInput) -> FundProcessorResult:
        result = super().extract(input_data)
        product_anchor = EvidenceAnchor(
            source_kind="annual_report",
            document_year=input_data.context.document_year,
            section_id="product-risk",
            page_number=None,
            table_id="product-risk-table",
            row_locator="field=risk_characteristic_text.risk_characteristic_text",
            note=None,
        )
        product_risk_text = {
            "schema_version": "risk_characteristic_text.v1",
            "fund_code": input_data.context.fund_code,
            "report_year": input_data.context.document_year,
            "risk_characteristic_text": "product_essence owns this risk text",
            "source_anchors": (
                {
                    "section_id": "product-risk",
                    "page_number": None,
                    "table_id": "product-risk-table",
                    "row_locator": "field=risk_characteristic_text.risk_characteristic_text",
                },
            ),
        }
        core_risk = result.field_families[1]
        product = FundFieldFamilyResult(
            field_family_id="product_essence.v1",
            chapter_ids=(1,),
            value={
                "schema_version": "product_essence.v1",
                "basic_identity": _MARKER_BASIC_IDENTITY,
                "risk_characteristic_text": product_risk_text,
            },
            status="partial",
            extraction_mode="direct",
            anchors=(product_anchor,),
            gaps=(),
            source_provenance=input_data.source_provenance,
        )
        return FundProcessorResult(
            processor_id=self.processor_id,
            output_schema_version=self.output_schema_version,
            fund_code=result.fund_code,
            report_year=result.report_year,
            fund_type=result.fund_type,
            report_type=result.report_type,
            input_intermediate_kind=result.input_intermediate_kind,
            field_families=(product, core_risk),
            gaps=(),
            anchors=(product_anchor, *core_risk.anchors),
            source_provenance=result.source_provenance,
            candidate_boundary=None,
            contract_status="partial",
        )


class _MismatchedDisclosureIdentityProcessor:
    """返回与 FDD dispatch key 不一致 identity 的 processor。"""

    processor_id = "mismatched_identity.disclosure_test"
    priority = 999
    output_schema_version = "test_disclosure_mismatch.v1"

    def supports(self, context: FundProcessorDispatchKey) -> bool:
        return context.intermediate_kind == "fund_disclosure_document.v1"

    def extract(self, input_data: FundProcessorInput) -> FundProcessorResult:
        return FundProcessorResult(
            processor_id=self.processor_id,
            output_schema_version=self.output_schema_version,
            fund_code="999999",
            report_year=input_data.context.document_year,
            fund_type=input_data.context.fund_type,
            report_type=input_data.context.report_type,
            input_intermediate_kind=input_data.context.intermediate_kind,
            field_families=(),
            gaps=(),
            anchors=(),
            source_provenance=input_data.source_provenance,
            candidate_boundary=None,
            contract_status="satisfied",
        )


class _MismatchedIdentityProcessor:
    """返回与 dispatch key 不一致 identity 的 processor。"""

    processor_id = "mismatched_identity.test"
    priority = 999
    output_schema_version = "test_mismatch.v1"

    def supports(self, context: FundProcessorDispatchKey) -> bool:
        return (
            context.fund_type == "active_fund"
            and context.report_type == "annual_report"
            and context.intermediate_kind == "parsed_annual_report.v1"
        )

    def extract(self, input_data: FundProcessorInput) -> FundProcessorResult:
        return FundProcessorResult(
            processor_id=self.processor_id,
            output_schema_version=self.output_schema_version,
            fund_code="999999",
            report_year=input_data.context.document_year,
            fund_type="active_fund",
            report_type="annual_report",
            input_intermediate_kind="parsed_annual_report.v1",
            field_families=(),
            gaps=(),
            anchors=(),
            source_provenance=input_data.source_provenance,
            candidate_boundary=None,
            contract_status="satisfied",
        )


class _NeverSupportProcessor:
    """测试用永不支持 active_fund 的 processor。"""

    processor_id = "never_support"
    priority = 0
    output_schema_version = "test.v1"

    def supports(self, context: FundProcessorDispatchKey) -> bool:
        return False

    def extract(self, input_data: FundProcessorInput) -> FundProcessorResult:
        raise AssertionError("never processor must not extract")


@pytest.mark.asyncio
async def test_active_fund_uses_processor_path_with_marker_values() -> None:
    """验证 all-six-family processor 投影只消费 owning family 字段。

    注入返回已知 marker 值的自定义 processor，验证 bundle 字段包含 marker
    而非 direct extractor 或 current_stage.v1 结果。
    """

    registry = FundProcessorRegistry()
    registry.register(_MarkerActiveFundProcessor)
    extractor = FundDataExtractor(
        repository=_FakeRepository(_annual_report()),
        nav_provider=_RecordingNavProvider(),
        processor_registry=registry,
    )

    bundle = await extractor.extract("110011", 2024)

    assert bundle.basic_identity.value == _MARKER_BASIC_IDENTITY
    assert bundle.product_profile.value == {"marker": "product_profile_from_processor"}
    assert bundle.benchmark.value == {"marker": "benchmark_from_processor"}
    assert bundle.risk_characteristic_text.value == {"marker": "risk_text_from_processor"}
    assert bundle.fee_schedule.value == {"marker": "fee_from_processor"}
    assert bundle.nav_benchmark_performance.value == {"marker": "perf_from_processor"}
    assert bundle.portfolio_managers.value == {"marker": "portfolio_managers_from_processor"}
    assert bundle.turnover_rate.value == {"marker": "turnover_from_processor"}
    assert bundle.manager_alignment.value == {"marker": "alignment_from_processor"}
    assert bundle.manager_strategy_text.value == {"marker": "strategy_from_processor"}
    assert bundle.holdings_snapshot.value == {"marker": "holdings_from_processor"}
    assert bundle.investor_return.value == {"marker": "investor_return_from_processor"}
    assert bundle.holder_structure.value == {"marker": "holder_from_processor"}
    assert bundle.share_change.value == {"marker": "share_change_from_processor"}
    assert not hasattr(bundle, "current_stage")
    assert bundle.basic_identity.value != {"marker": "current_stage_basic_identity_must_not_project"}
    assert bundle.share_change.value != {"marker": "current_stage_share_must_not_project"}
    assert bundle.holdings_snapshot.value != {"marker": "current_stage_holdings_must_not_project"}
    assert bundle.portfolio_managers.value != {"marker": "current_stage_portfolio_must_not_project"}
    assert bundle.tracking_error.extraction_mode == "missing"
    assert bundle.tracking_error.note == "非指数基金不适用跟踪误差"


@pytest.mark.asyncio
async def test_default_active_fund_still_uses_parsed_annual_report_processor_path() -> None:
    """验证默认路径仍解析 parsed_annual_report.v1 processor，不启用 FDD。"""

    registry = FundProcessorRegistry()
    registry.register(_MarkerActiveFundProcessor)
    extractor = FundDataExtractor(
        repository=_FakeRepository(_annual_report()),
        nav_provider=_RecordingNavProvider(),
        processor_registry=registry,
    )

    bundle = await extractor.extract("110011", 2024)

    assert bundle.basic_identity.value == _MARKER_BASIC_IDENTITY
    assert bundle.product_profile.value == {"marker": "product_profile_from_processor"}
    assert bundle.source_provenance is not None


@pytest.mark.asyncio
async def test_default_extract_does_not_resolve_fund_disclosure_processor() -> None:
    """验证 disclosure_intermediate=None 时不会解析 fund_disclosure_document.v1。"""

    registry = _RecordingRegistry()
    registry.register(_MarkerActiveFundProcessor)
    registry.register(_MarkerDisclosureProcessor)
    extractor = FundDataExtractor(
        repository=_FakeRepository(_annual_report()),
        nav_provider=_RecordingNavProvider(),
        processor_registry=registry,
    )

    bundle = await extractor.extract("110011", 2024)

    assert bundle.basic_identity.value == _MARKER_BASIC_IDENTITY
    assert [context.intermediate_kind for context in registry.resolved_contexts] == [
        "parsed_annual_report.v1"
    ]


@pytest.mark.asyncio
async def test_explicit_disclosure_intermediate_routes_to_registry() -> None:
    """验证显式 FDD 中间态通过 registry 投影 marker 字段。"""

    registry = _RecordingRegistry()
    registry.register(_MarkerActiveFundProcessor)
    registry.register(_MarkerDisclosureProcessor)
    extractor = FundDataExtractor(
        repository=_FakeRepository(_annual_report()),
        nav_provider=_RecordingNavProvider(),
        processor_registry=registry,
    )

    bundle = await extractor.extract(
        "110011",
        2024,
        disclosure_intermediate=_disclosure_intermediate(),
    )

    assert [context.intermediate_kind for context in registry.resolved_contexts] == [
        "fund_disclosure_document.v1"
    ]
    assert bundle.basic_identity.value is not None
    assert bundle.basic_identity.value["fund_name"] == "DISCLOSURE_MARKER_PROCESSOR_PROOF"
    assert bundle.product_profile.value == {"marker": "product_profile_from_disclosure_processor"}
    assert bundle.portfolio_managers.value == {"marker": "portfolio_from_disclosure_processor"}
    assert bundle.share_change.value == {"marker": "share_from_disclosure_processor"}
    assert bundle.holdings_snapshot.value == {"marker": "holdings_from_disclosure_processor"}
    assert not hasattr(bundle, "current_stage")
    assert bundle.basic_identity.value != {"marker": "current_stage_basic_identity_must_not_project"}
    assert bundle.share_change.value != {"marker": "current_stage_share_must_not_project"}
    assert bundle.holdings_snapshot.value != {"marker": "current_stage_holdings_must_not_project"}
    assert bundle.portfolio_managers.value != {"marker": "current_stage_portfolio_must_not_project"}


@pytest.mark.asyncio
async def test_explicit_disclosure_source_truth_return_attribution_projects_to_bundle() -> None:
    """验证 proof-positive FDD 收益归因 source truth 经 facade 投影。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当显式 FDD direct route 未投影到 bundle 或误用 candidate 时抛出。
    """

    extractor = FundDataExtractor(
        repository=_FakeRepository(_annual_report()),
        nav_provider=_RecordingNavProvider(),
        processor_registry=FundProcessorRegistry.create_default(),
    )

    bundle = await extractor.extract(
        "110011",
        2024,
        disclosure_intermediate=_source_truth_disclosure_intermediate(),
    )

    assert bundle.fee_schedule.value == {
        "management_fee": "1.50%",
        "custody_fee": "0.25%",
    }
    assert bundle.fee_schedule.extraction_mode == "direct"
    assert bundle.nav_benchmark_performance.value == {
        "nav_growth_rate": "8.00%",
        "benchmark_return_rate": "6.00%",
    }
    assert bundle.nav_benchmark_performance.extraction_mode == "direct"
    assert bundle.tracking_error.value is None
    assert bundle.tracking_error.extraction_mode == "missing"
    assert bundle.tracking_error.note == "非指数基金不适用跟踪误差"
    assert bundle.fee_schedule.anchors
    assert bundle.nav_benchmark_performance.anchors
    assert {
        anchor.source_kind
        for anchor in (
            *bundle.fee_schedule.anchors,
            *bundle.nav_benchmark_performance.anchors,
        )
    } == {"annual_report"}
    assert all(
        anchor.row_locator is not None and anchor.row_locator.startswith("field=")
        for anchor in (*bundle.fee_schedule.anchors, *bundle.nav_benchmark_performance.anchors)
    )


@pytest.mark.asyncio
async def test_explicit_disclosure_source_truth_manager_profile_projects_to_bundle() -> None:
    """验证 proof-positive FDD manager_profile source truth 经 facade 投影。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 manager_profile 五个 public bundle 字段未投影时抛出。
    """

    extractor = FundDataExtractor(
        repository=_FakeRepository(_annual_report()),
        nav_provider=_RecordingNavProvider(),
        processor_registry=FundProcessorRegistry.create_default(),
    )

    bundle = await extractor.extract(
        "110011",
        2024,
        disclosure_intermediate=_manager_profile_source_truth_disclosure_intermediate(),
    )

    assert bundle.portfolio_managers.extraction_mode == "direct"
    assert bundle.portfolio_managers.value is not None
    assert bundle.portfolio_managers.value["schema_version"] == (
        "portfolio_manager_tenure_list.v1"
    )
    assert bundle.portfolio_managers.value["fund_code"] == "110011"
    assert bundle.portfolio_managers.value["report_year"] == 2024
    assert bundle.portfolio_managers.value["portfolio_managers"] == [
        {
            "name": "张三",
            "role": "基金经理",
            "start_date": "2020-01-01",
            "source_anchor": {
                "section_id": "section-manager",
                "section_title": "基金经理情况",
                "page_number": None,
                "table_id": "table-roster",
                "row_locator": "portfolio_manager:张三",
            },
        }
    ]
    assert bundle.turnover_rate.value == {
        "turnover_rate": "123.45%",
        "turnover_basis": "双边成交金额除以平均股票市值",
    }
    assert bundle.manager_alignment.value == {
        "manager_holding": "本基金基金经理持有本开放式基金份额区间为100万份以上。",
        "employee_holding": "基金管理人所有从业人员持有本基金份额区间为50万份至100万份。",
        "judgment": None,
    }
    assert bundle.manager_strategy_text.value == {
        "strategy_summary": "本报告期坚持均衡配置。",
        "market_outlook": "后续将关注基本面变化。",
    }
    assert bundle.holdings_snapshot.value == {
        "top_holdings": [
            {"股票代码": "600000", "股票名称": "浦发银行", "公允价值": "1,234,567.89"}
        ],
        "top_holdings_status": "direct_top_ten",
        "top_holdings_source": "top_ten",
        "industry_distribution": [
            {"行业类别": "制造业", "公允价值": "2,000,000.00", "占基金资产净值比例": "12.34%"}
        ],
        "industry_distribution_status": "direct",
    }
    assert bundle.turnover_rate.extraction_mode == "direct"
    assert bundle.manager_alignment.extraction_mode == "direct"
    assert bundle.manager_strategy_text.extraction_mode == "direct"
    assert bundle.holdings_snapshot.extraction_mode == "direct"
    assert all(
        field.anchors
        for field in (
            bundle.portfolio_managers,
            bundle.turnover_rate,
            bundle.manager_alignment,
            bundle.manager_strategy_text,
            bundle.holdings_snapshot,
        )
    )
    assert bundle.investor_return.value is None
    assert bundle.holder_structure.value is None
    assert bundle.share_change.value is None
    assert bundle.bond_risk_evidence.value is None


@pytest.mark.asyncio
async def test_explicit_disclosure_source_truth_investor_experience_projects_to_bundle() -> None:
    """验证 proof-positive FDD investor_experience source truth 经 facade 投影。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 investor_experience 三个 bundle 字段未投影时抛出。
    """

    extractor = FundDataExtractor(
        repository=_FakeRepository(_annual_report()),
        nav_provider=_RecordingNavProvider(),
        processor_registry=FundProcessorRegistry.create_default(),
    )

    bundle = await extractor.extract(
        "110011",
        2024,
        disclosure_intermediate=_investor_experience_source_truth_disclosure_intermediate(),
    )

    assert bundle.investor_return.value == {
        "investor_return_rate": "7.25%",
        "disclosure_status": "direct",
        "fallback_status": "not_needed",
    }
    assert bundle.holder_structure.value == {
        "institutional_holder": "60.00%",
        "individual_holder": "40.00%",
    }
    assert bundle.share_change.value == {
        "beginning_share": "1,000.00",
        "ending_share": "1,250.00",
        "net_change": "250.00",
        "share_class_column": "110011",
        "share_class_selection_reason": "single_value_column",
    }
    assert bundle.investor_return.extraction_mode == "direct"
    assert bundle.holder_structure.extraction_mode == "direct"
    assert bundle.share_change.extraction_mode == "direct"
    assert bundle.investor_return.anchors
    assert bundle.holder_structure.anchors
    assert bundle.share_change.anchors
    assert {
        anchor.source_kind
        for anchor in (
            *bundle.investor_return.anchors,
            *bundle.holder_structure.anchors,
            *bundle.share_change.anchors,
        )
    } == {"annual_report"}


@pytest.mark.asyncio
async def test_explicit_disclosure_current_stage_source_truth_has_no_bundle_projection() -> None:
    """验证 proof-positive FDD current_stage source text 不产生 bundle 字段。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 facade 暴露 StructuredFundDataBundle.current_stage 时抛出。
    """

    extractor = FundDataExtractor(
        repository=_FakeRepository(_annual_report()),
        nav_provider=_RecordingNavProvider(),
        processor_registry=FundProcessorRegistry.create_default(),
    )

    bundle = await extractor.extract(
        "110011",
        2024,
        disclosure_intermediate=_current_stage_source_truth_disclosure_intermediate(),
    )

    assert not hasattr(bundle, "current_stage")
    assert bundle.basic_identity.value is not None
    assert bundle.basic_identity.value["fund_code"] == "110011"
    assert bundle.share_change.value == {
        "beginning_share": "1,000.00",
        "ending_share": "1,250.00",
        "net_change": "250.00",
        "share_class_column": "110011",
        "share_class_selection_reason": "single_value_column",
    }


@pytest.mark.asyncio
async def test_explicit_disclosure_core_risk_fallback_projects_risk_text_only() -> None:
    """验证既有 core_risk.v1 fallback 只投影 risk_characteristic_text。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 facade 新增 core_risk 字段或投影 deferred roles 时抛出。
    """

    registry = FundProcessorRegistry()
    registry.register(_CoreRiskFallbackDisclosureProcessor)
    extractor = FundDataExtractor(
        repository=_FakeRepository(_annual_report()),
        nav_provider=_RecordingNavProvider(),
        processor_registry=registry,
    )

    bundle = await extractor.extract(
        "110011",
        2024,
        disclosure_intermediate=_disclosure_intermediate(
            source_truth_admission=_source_truth_admission_proof()
        ),
    )

    assert not hasattr(bundle, "core_risk")
    assert bundle.risk_characteristic_text.value == {
        "schema_version": "risk_characteristic_text.v1",
        "fund_code": "110011",
        "report_year": 2024,
        "risk_characteristic_text": "本基金为较高风险较高收益品种。",
        "source_anchors": (
            {
                "section_id": "core-risk",
                "page_number": None,
                "table_id": "core-risk-table",
                "row_locator": "field=risk_characteristic_text.risk_characteristic_text",
            },
        ),
    }
    assert bundle.risk_characteristic_text.note == "fallback_from_core_risk.v1"
    assert bundle.risk_characteristic_text.extraction_mode == "direct"
    assert bundle.risk_characteristic_text.anchors
    assert bundle.turnover_rate.value is None
    assert bundle.holdings_snapshot.value is None
    assert bundle.manager_strategy_text.value is None


@pytest.mark.asyncio
async def test_explicit_disclosure_product_risk_text_wins_over_core_risk_fallback() -> None:
    """product_essence 已有 risk text 时不使用 core_risk fallback 覆盖。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 core_risk fallback 覆盖 owning family 字段时抛出。
    """

    registry = FundProcessorRegistry()
    registry.register(_CoreRiskProductWinsDisclosureProcessor)
    extractor = FundDataExtractor(
        repository=_FakeRepository(_annual_report()),
        nav_provider=_RecordingNavProvider(),
        processor_registry=registry,
    )

    bundle = await extractor.extract(
        "110011",
        2024,
        disclosure_intermediate=_disclosure_intermediate(
            source_truth_admission=_source_truth_admission_proof()
        ),
    )

    assert not hasattr(bundle, "core_risk")
    assert bundle.risk_characteristic_text.value is not None
    assert (
        bundle.risk_characteristic_text.value["risk_characteristic_text"]
        == "product_essence owns this risk text"
    )
    assert bundle.risk_characteristic_text.note is None
    assert bundle.risk_characteristic_text.anchors
    assert bundle.risk_characteristic_text.anchors[0].section_id == "product-risk"


@pytest.mark.asyncio
async def test_explicit_disclosure_candidate_only_manager_profile_stays_missing() -> None:
    """验证 proof-missing/candidate-only manager_profile 不投影 bundle 字段。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 candidate evidence 被 facade 当作字段值消费时抛出。
    """

    extractor = FundDataExtractor(
        repository=_FakeRepository(_annual_report()),
        nav_provider=_RecordingNavProvider(),
        processor_registry=FundProcessorRegistry.create_default(),
    )

    bundle = await extractor.extract(
        "110011",
        2024,
        disclosure_intermediate=_manager_profile_candidate_only_disclosure_intermediate(),
    )

    assert bundle.portfolio_managers.value is None
    assert bundle.turnover_rate.value is None
    assert bundle.manager_alignment.value is None
    assert bundle.manager_strategy_text.value is None
    assert bundle.holdings_snapshot.value is None
    assert bundle.portfolio_managers.anchors == ()
    assert bundle.turnover_rate.anchors == ()
    assert bundle.manager_alignment.anchors == ()
    assert bundle.manager_strategy_text.anchors == ()
    assert bundle.holdings_snapshot.anchors == ()
    assert bundle.portfolio_managers.extraction_mode == "missing"
    assert bundle.turnover_rate.extraction_mode == "missing"
    assert bundle.manager_alignment.extraction_mode == "missing"
    assert bundle.manager_strategy_text.extraction_mode == "missing"
    assert bundle.holdings_snapshot.extraction_mode == "missing"


@pytest.mark.asyncio
async def test_explicit_disclosure_candidate_only_investor_experience_stays_missing() -> None:
    """验证 proof-missing/candidate-only investor_experience 不投影 bundle 字段。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 candidate evidence 被 facade 当作 investor 字段值消费时抛出。
    """

    extractor = FundDataExtractor(
        repository=_FakeRepository(_annual_report()),
        nav_provider=_RecordingNavProvider(),
        processor_registry=FundProcessorRegistry.create_default(),
    )

    bundle = await extractor.extract(
        "110011",
        2024,
        disclosure_intermediate=_investor_experience_candidate_only_disclosure_intermediate(),
    )

    assert bundle.investor_return.value is None
    assert bundle.holder_structure.value is None
    assert bundle.share_change.value is None
    assert bundle.investor_return.anchors == ()
    assert bundle.holder_structure.anchors == ()
    assert bundle.share_change.anchors == ()
    assert bundle.investor_return.extraction_mode == "missing"
    assert bundle.holder_structure.extraction_mode == "missing"
    assert bundle.share_change.extraction_mode == "missing"
    assert bundle.portfolio_managers.note == (
        "field_not_in_family:manager_profile.v1:portfolio_managers"
    )


def test_explicit_disclosure_intermediate_uses_protocol_not_candidate_import() -> None:
    """验证 data_extractor 只导入协议，不导入 concrete candidate 模块。"""

    module_path = Path(__file__).parents[2] / "fund_agent" / "fund" / "data_extractor.py"
    tree = ast.parse(module_path.read_text(encoding="utf-8"))
    imported_modules = {
        node.module
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module is not None
    }
    imported_names_from_contracts = {
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom)
        and node.module == "fund_agent.fund.processors.contracts"
        for alias in node.names
    }

    assert "FundDisclosureDocumentIntermediate" in imported_names_from_contracts
    assert not any(
        module.startswith("fund_agent.fund.documents.candidates") for module in imported_modules
    )
    assert "docling" not in imported_modules


@pytest.mark.asyncio
async def test_explicit_disclosure_identity_mismatch_fails_before_nav() -> None:
    """验证 FDD fund/year 身份不匹配时在 NAV 调用前 fail-closed。"""

    nav_provider = _RecordingNavProvider()
    extractor = FundDataExtractor(
        repository=_FakeRepository(_annual_report()),
        nav_provider=nav_provider,
    )

    with pytest.raises(RuntimeError, match="FundDisclosureDocument identity mismatch"):
        await extractor.extract(
            "110011",
            2024,
            disclosure_intermediate=_disclosure_intermediate(fund_code="999999"),
        )

    assert nav_provider.calls == []


@pytest.mark.asyncio
async def test_explicit_disclosure_wrong_intermediate_kind_fails_before_nav() -> None:
    """验证非 fund_disclosure_document.v1 中间态在 NAV 调用前 fail-closed。"""

    nav_provider = _RecordingNavProvider()
    extractor = FundDataExtractor(
        repository=_FakeRepository(_annual_report()),
        nav_provider=nav_provider,
    )

    with pytest.raises(RuntimeError, match="intermediate_kind"):
        await extractor.extract(
            "110011",
            2024,
            disclosure_intermediate=_disclosure_intermediate(
                intermediate_kind="parsed_annual_report.v1"
            ),
        )

    assert nav_provider.calls == []


@pytest.mark.asyncio
async def test_explicit_disclosure_missing_provenance_fails_closed() -> None:
    """验证缺失 provenance 的显式 FDD 路径 fail-closed，不返回 bundle。"""

    extractor = FundDataExtractor(
        repository=_FakeRepository(_annual_report()),
        nav_provider=_RecordingNavProvider(),
    )

    with pytest.raises(RuntimeError, match="source_provenance_unsafe"):
        await extractor.extract(
            "110011",
            2024,
            disclosure_intermediate=_disclosure_intermediate(source_provenance=None),
        )


@pytest.mark.asyncio
async def test_explicit_disclosure_candidate_boundary_fails_closed() -> None:
    """验证 candidate_boundary 不会被提升为可用 bundle。"""

    extractor = FundDataExtractor(
        repository=_FakeRepository(_annual_report()),
        nav_provider=_RecordingNavProvider(),
    )

    with pytest.raises(RuntimeError, match="blocked"):
        await extractor.extract(
            "110011",
            2024,
            disclosure_intermediate=_disclosure_intermediate(
                candidate_boundary=CandidateBoundaryStatus(
                    candidate_only=True,
                    field_correctness_status="not_proven",
                    source_truth_status="not_proven",
                )
            ),
        )


@pytest.mark.asyncio
async def test_explicit_disclosure_schema_drift_fails_closed() -> None:
    """验证 schema_drift 来源失败显式 FDD 路径 fail-closed。"""

    await _assert_explicit_disclosure_failure_class_raises("schema_drift")


@pytest.mark.asyncio
async def test_explicit_disclosure_identity_mismatch_failure_class_fails_closed() -> None:
    """验证 identity_mismatch 来源失败显式 FDD 路径 fail-closed。"""

    await _assert_explicit_disclosure_failure_class_raises("identity_mismatch")


@pytest.mark.asyncio
async def test_explicit_disclosure_integrity_error_fails_closed() -> None:
    """验证 integrity_error 来源失败显式 FDD 路径 fail-closed。"""

    await _assert_explicit_disclosure_failure_class_raises("integrity_error")


@pytest.mark.asyncio
async def test_explicit_disclosure_unavailable_fails_closed_no_parsed_fallback() -> None:
    """验证 unavailable 不回退到 parsed annual production route。"""

    await _assert_explicit_disclosure_failure_class_raises("unavailable")


@pytest.mark.asyncio
async def test_explicit_disclosure_not_found_fails_closed_no_parsed_fallback() -> None:
    """验证 not_found 不回退到 parsed annual production route。"""

    await _assert_explicit_disclosure_failure_class_raises("not_found")


@pytest.mark.asyncio
async def test_explicit_disclosure_non_active_fund_raises_no_legacy_fallback() -> None:
    """验证非 active 显式 FDD 路径 fail-closed，不走 direct legacy。"""

    extractor = FundDataExtractor(
        repository=_FakeRepository(_index_annual_report()),
        nav_provider=_RecordingNavProvider(),
    )

    with pytest.raises(RuntimeError, match="supports only active_fund"):
        await extractor.extract(
            "000001",
            2024,
            disclosure_intermediate=_disclosure_intermediate(fund_code="000001"),
        )


@pytest.mark.asyncio
async def test_default_non_active_without_disclosure_preserves_legacy_path() -> None:
    """验证非 active 默认无 FDD 参数时仍保留 direct legacy path。"""

    extractor = FundDataExtractor(
        repository=_FakeRepository(_index_annual_report()),
        nav_provider=_RecordingNavProvider(),
    )

    bundle = await extractor.extract("000001", 2024)

    assert bundle.fund_code == "000001"
    assert bundle.basic_identity.value is not None
    assert bundle.basic_identity.value["classified_fund_type"] == "index_fund"


@pytest.mark.asyncio
async def test_explicit_disclosure_registry_resolution_failure_raises_no_fallback() -> None:
    """验证 registry 无 FDD processor 时抛 UnsupportedFundProcessorError，不 fallback。"""

    registry = FundProcessorRegistry()
    registry.register(_MarkerActiveFundProcessor)
    extractor = FundDataExtractor(
        repository=_FakeRepository(_annual_report()),
        nav_provider=_RecordingNavProvider(),
        processor_registry=registry,
    )

    with pytest.raises(UnsupportedFundProcessorError, match="fund_disclosure_document.v1"):
        await extractor.extract(
            "110011",
            2024,
            disclosure_intermediate=_disclosure_intermediate(),
        )


@pytest.mark.asyncio
async def test_explicit_disclosure_processor_result_identity_mismatch_fails_closed() -> None:
    """验证 FDD processor 返回错身份时 fail-closed。"""

    registry = FundProcessorRegistry()
    registry.register(_MismatchedDisclosureIdentityProcessor)
    extractor = FundDataExtractor(
        repository=_FakeRepository(_annual_report()),
        nav_provider=_RecordingNavProvider(),
        processor_registry=registry,
    )

    with pytest.raises(RuntimeError, match="Processor result identity mismatch"):
        await extractor.extract(
            "110011",
            2024,
            disclosure_intermediate=_disclosure_intermediate(),
        )


@pytest.mark.asyncio
async def test_explicit_disclosure_non_candidate_admitted_produces_missing_bundle() -> None:
    """验证非候选 FDD stub 通过 S4 missing 路径，但不提升字段值或 anchor。"""

    extractor = FundDataExtractor(
        repository=_FakeRepository(_annual_report()),
        nav_provider=_RecordingNavProvider(),
    )

    bundle = await extractor.extract(
        "110011",
        2024,
        disclosure_intermediate=_disclosure_intermediate(),
    )

    assert bundle.product_profile.value is None
    assert bundle.product_profile.anchors == ()
    assert bundle.product_profile.extraction_mode == "missing"
    assert bundle.product_profile.note == "field_not_in_family:product_essence.v1:product_profile"
    assert bundle.fee_schedule.value is None
    assert bundle.fee_schedule.anchors == ()
    assert bundle.manager_strategy_text.value is None
    assert bundle.manager_strategy_text.anchors == ()


@pytest.mark.asyncio
async def test_explicit_disclosure_missing_result_preserves_parsed_report_residual_fields() -> None:
    """验证 FDD missing 结果保留 parsed-report residual 字段语义。"""

    extractor = FundDataExtractor(
        repository=_FakeRepository(_annual_report()),
        nav_provider=_RecordingNavProvider(),
    )

    bundle = await extractor.extract(
        "110011",
        2024,
        disclosure_intermediate=_disclosure_intermediate(),
    )

    assert bundle.index_profile.value is None
    assert bundle.index_profile.anchors == ()
    assert bundle.bond_risk_evidence.value is None
    assert bundle.bond_risk_evidence.anchors == ()
    assert bundle.bond_risk_evidence.note == "not_applicable_non_bond_fund"
    assert bundle.portfolio_managers.value is None
    assert bundle.portfolio_managers.note == (
        "field_not_in_family:manager_profile.v1:portfolio_managers"
    )
    assert bundle.risk_characteristic_text.value is None
    assert bundle.risk_characteristic_text.note == (
        "field_not_in_family:product_essence.v1:risk_characteristic_text"
    )


@pytest.mark.asyncio
async def test_active_fund_unsupported_registry_fails_closed() -> None:
    """验证 registry 无 active_fund processor 时 fail-closed，不 fallback 到 direct 路径。"""

    registry = FundProcessorRegistry()
    registry.register(_NeverSupportProcessor)
    extractor = FundDataExtractor(
        repository=_FakeRepository(_annual_report()),
        nav_provider=_RecordingNavProvider(),
        processor_registry=registry,
    )

    with pytest.raises(UnsupportedFundProcessorError, match="unsupported_processor"):
        await extractor.extract("110011", 2024)


@pytest.mark.asyncio
async def test_active_fund_processor_mismatched_identity_fails_closed() -> None:
    """验证 processor 返回与 dispatch key 不一致的 identity 时 fail-closed。"""

    registry = FundProcessorRegistry()
    registry.register(_MismatchedIdentityProcessor)
    extractor = FundDataExtractor(
        repository=_FakeRepository(_annual_report()),
        nav_provider=_RecordingNavProvider(),
        processor_registry=registry,
    )

    with pytest.raises(RuntimeError, match="Processor result identity mismatch"):
        await extractor.extract("110011", 2024)


@pytest.mark.asyncio
async def test_data_extractor_rejects_report_identity_mismatch_before_nav() -> None:
    """验证 repository 返回不匹配年报时在 NAV provider 调用前 fail-closed。

    Repository 返回 fund_code="110011" 的年报，但请求为 "999999"。
    提取器应在 NAV provider 调用前检测身份不匹配并抛出 RuntimeError。
    """

    repository = _FakeRepository(_annual_report())
    nav_provider = _RecordingNavProvider()
    registry = FundProcessorRegistry()
    registry.register(_MarkerActiveFundProcessor)
    extractor = FundDataExtractor(
        repository=repository,
        nav_provider=nav_provider,
        processor_registry=registry,
    )

    with pytest.raises(RuntimeError, match="Report identity mismatch"):
        await extractor.extract("999999", 2024)

    assert nav_provider.calls == []


@pytest.mark.asyncio
async def test_index_fund_direct_path_smoke_test() -> None:
    """验证非 active 指数基金保留 direct legacy path 行为，不报错且返回 bundle。"""

    repository = _FakeRepository(_index_annual_report())
    extractor = FundDataExtractor(repository=repository, nav_provider=_RecordingNavProvider())

    bundle = await extractor.extract("000001", 2024)

    assert bundle.fund_code == "000001"
    assert bundle.report_year == 2024
    assert bundle.basic_identity.value is not None
    assert bundle.basic_identity.value["classified_fund_type"] == "index_fund"
    assert bundle.tracking_error.extraction_mode == "missing"
    assert bundle.source_provenance is not None


def _provenance() -> PublicSourceProvenance:
    """构造测试用安全默认公共 provenance。

    Args:
        无。

    Returns:
        公共来源 provenance fixture。

    Raises:
        无显式抛出。
    """

    return default_public_source_provenance()


def _disclosure_intermediate(**overrides: object) -> _StubDisclosureIntermediate:
    """构造测试用 FundDisclosureDocumentIntermediate stub。

    Args:
        **overrides: 覆盖协议字段。

    Returns:
        本地协议 stub。

    Raises:
        无显式抛出。
    """

    kwargs: dict[str, object] = {"source_provenance": _provenance()}
    kwargs.update(overrides)
    return _StubDisclosureIntermediate(**kwargs)  # type: ignore[arg-type]


def _source_truth_disclosure_intermediate() -> _StubDisclosureIntermediate:
    """构造带 proof-positive return_attribution.v1 内容的 FDD stub。

    Args:
        无。

    Returns:
        测试用 source-truth FDD content intermediate。

    Raises:
        无显式抛出。
    """

    table = _DisclosureTable(
        table_id="return-attribution-table",
        cells=(
            _DisclosureCell(
                cell_id="nav-growth",
                table_id="return-attribution-table",
                row_index=0,
                column_index=1,
                cell_text="8.00%",
                column_header_path=("基金份额净值增长率",),
            ),
            _DisclosureCell(
                cell_id="benchmark-return",
                table_id="return-attribution-table",
                row_index=0,
                column_index=2,
                cell_text="6.00%",
                column_header_path=("业绩比较基准收益率",),
            ),
            _DisclosureCell(
                cell_id="management-fee",
                table_id="return-attribution-table",
                row_index=1,
                column_index=1,
                cell_text="1.50%",
                row_label_path=("管理费率",),
            ),
            _DisclosureCell(
                cell_id="custody-fee",
                table_id="return-attribution-table",
                row_index=2,
                column_index=1,
                cell_text="0.25%",
                row_label_path=("托管费率",),
            ),
            _DisclosureCell(
                cell_id="tracking-error",
                table_id="return-attribution-table",
                row_index=3,
                column_index=1,
                cell_text="1.23%",
                row_label_path=("跟踪误差",),
            ),
        ),
    )
    return _disclosure_intermediate(
        table_blocks=(table,),
        source_truth_admission=_source_truth_admission_proof(),
    )


def _manager_profile_source_truth_disclosure_intermediate() -> _StubDisclosureIntermediate:
    """构造带 proof-positive manager_profile.v1 内容的 FDD stub。

    Args:
        无。

    Returns:
        测试用 manager_profile source-truth FDD content intermediate。

    Raises:
        无显式抛出。
    """

    return _manager_profile_disclosure_intermediate(
        source_truth_admission=_source_truth_admission_proof()
    )


def _manager_profile_candidate_only_disclosure_intermediate() -> _StubDisclosureIntermediate:
    """构造 proof-missing/candidate-only manager_profile.v1 内容的 FDD stub。

    Args:
        无。

    Returns:
        测试用 candidate-only FDD content intermediate。

    Raises:
        无显式抛出。
    """

    return _manager_profile_disclosure_intermediate(source_truth_admission=None)


def _investor_experience_source_truth_disclosure_intermediate() -> _StubDisclosureIntermediate:
    """构造带 proof-positive investor_experience.v1 内容的 FDD stub。

    Args:
        无。

    Returns:
        测试用 investor_experience source-truth FDD content intermediate。

    Raises:
        无显式抛出。
    """

    return _investor_experience_disclosure_intermediate(
        source_truth_admission=_source_truth_admission_proof()
    )


def _investor_experience_candidate_only_disclosure_intermediate() -> _StubDisclosureIntermediate:
    """构造 proof-missing/candidate-only investor_experience.v1 内容的 FDD stub。

    Args:
        无。

    Returns:
        测试用 candidate-only FDD content intermediate。

    Raises:
        无显式抛出。
    """

    return _investor_experience_disclosure_intermediate(source_truth_admission=None)


def _current_stage_source_truth_disclosure_intermediate() -> _StubDisclosureIntermediate:
    """构造带 proof-positive current_stage.v1 相关内容的 FDD stub。

    Args:
        无。

    Returns:
        测试用 current_stage source-truth FDD content intermediate。

    Raises:
        无显式抛出。
    """

    product_table = _DisclosureTable(
        table_id="table-current-product",
        section_id="section-product",
        heading_text="基金基本情况",
        table_caption_or_nearby_heading="基金基本情况",
        heading_path=("基金简介",),
        cells=(
            _DisclosureCell(
                cell_id="current-product-name",
                table_id="table-current-product",
                section_anchor="section-product",
                heading_path=("基金简介",),
                row_index=0,
                column_index=1,
                row_label_path=("基金名称",),
                column_header_path=("内容",),
                cell_text="测试当前阶段基金",
            ),
            _DisclosureCell(
                cell_id="current-product-code",
                table_id="table-current-product",
                section_anchor="section-product",
                heading_path=("基金简介",),
                row_index=1,
                column_index=1,
                row_label_path=("基金主代码",),
                column_header_path=("内容",),
                cell_text="110011",
            ),
        ),
    )
    share_change_table = _DisclosureTable(
        table_id="table-investor-share-change",
        section_id="section-share-change",
        heading_text="基金份额变动",
        table_caption_or_nearby_heading="基金份额变动",
        heading_path=("基金份额变动",),
        cells=(
            _investor_experience_share_change_cell(
                "期初基金份额总额", "1,000.00", row_index=0
            ),
            _investor_experience_share_change_cell(
                "期末基金份额总额", "1,250.00", row_index=1
            ),
            _investor_experience_share_change_cell("净变动", "250.00", row_index=2),
        ),
    )
    current_stage_paragraph = _DisclosureParagraph(
        block_id="paragraph-current-stage",
        section_id="section-current-stage",
        heading_path=("当前阶段",),
        text_raw="当前阶段：报告期基金运作保持稳定。",
        text_normalized="当前阶段：报告期基金运作保持稳定。",
    )
    return _disclosure_intermediate(
        paragraph_blocks=(current_stage_paragraph,),
        table_blocks=(product_table, share_change_table),
        source_truth_admission=_source_truth_admission_proof(),
    )


def _investor_experience_disclosure_intermediate(
    *,
    source_truth_admission: FundDisclosureSourceTruthAdmissionProof | None,
) -> _StubDisclosureIntermediate:
    """构造 investor_experience facade route 共用 FDD content fixture。

    Args:
        source_truth_admission: source-truth 正向证明；为空时保留 candidate-only 路径。

    Returns:
        测试用 FDD content intermediate。

    Raises:
        无显式抛出。
    """

    paragraphs = (
        _DisclosureParagraph(
            block_id="paragraph-investor-return",
            section_id="section-investor",
            heading_path=("投资者获得感",),
            text_raw="投资者收益率：7.25%",
            text_normalized="投资者收益率：7.25%",
        ),
        _DisclosureParagraph(
            block_id="paragraph-institutional-holder",
            section_id="section-holder",
            heading_path=("基金份额持有人结构",),
            text_raw="机构投资者持有比例：60.00%",
            text_normalized="机构投资者持有比例：60.00%",
        ),
        _DisclosureParagraph(
            block_id="paragraph-individual-holder",
            section_id="section-holder",
            heading_path=("基金份额持有人结构",),
            text_raw="个人投资者持有比例：40.00%",
            text_normalized="个人投资者持有比例：40.00%",
        ),
    )
    share_change_table = _DisclosureTable(
        table_id="table-investor-share-change",
        section_id="section-share-change",
        heading_text="基金份额变动",
        table_caption_or_nearby_heading="基金份额变动",
        heading_path=("基金份额变动",),
        cells=(
            _investor_experience_share_change_cell(
                "期初基金份额总额", "1,000.00", row_index=0
            ),
            _investor_experience_share_change_cell(
                "期末基金份额总额", "1,250.00", row_index=1
            ),
            _investor_experience_share_change_cell("净变动", "250.00", row_index=2),
        ),
    )
    return _disclosure_intermediate(
        paragraph_blocks=paragraphs,
        table_blocks=(share_change_table,),
        source_truth_admission=source_truth_admission,
    )


def _investor_experience_share_change_cell(
    label: str,
    value: str,
    *,
    row_index: int,
) -> _DisclosureCell:
    """构造 investor_experience share_change facade fixture。

    Args:
        label: 份额变动 row label。
        value: 披露值。
        row_index: 行号。

    Returns:
        FDD cell stub。

    Raises:
        无显式抛出。
    """

    return _DisclosureCell(
        cell_id=f"investor-share-change-{row_index}",
        table_id="table-investor-share-change",
        section_anchor="section-share-change",
        heading_path=("基金份额变动",),
        row_index=row_index,
        column_index=1,
        row_label_path=(label,),
        column_header_path=("110011",),
        cell_text=value,
    )


def _manager_profile_disclosure_intermediate(
    *,
    source_truth_admission: FundDisclosureSourceTruthAdmissionProof | None,
) -> _StubDisclosureIntermediate:
    """构造 manager_profile facade route 共用 FDD content fixture。

    Args:
        source_truth_admission: source-truth 正向证明；为空时保留 candidate-only 路径。

    Returns:
        测试用 FDD content intermediate。

    Raises:
        无显式抛出。
    """

    roster_table = _DisclosureTable(
        table_id="table-roster",
        section_id="section-manager",
        heading_text="基金经理情况",
        table_caption_or_nearby_heading="基金经理情况",
        heading_path=("基金管理人及基金经理情况",),
        cells=(
            _manager_profile_cell("姓名", "张三", row_index=0, column_index=0),
            _manager_profile_cell("职务", "基金经理", row_index=0, column_index=1),
            _manager_profile_cell("任职日期", "2020-01-01", row_index=0, column_index=2),
        ),
    )
    turnover_table = _DisclosureTable(
        table_id="table-turnover",
        section_id="section-turnover",
        heading_text="报告期内股票换手率",
        table_caption_or_nearby_heading="报告期内股票换手率",
        heading_path=("交易情况",),
        cells=(
            _manager_profile_cell(
                "报告期内股票换手率",
                "123.45%",
                row_index=0,
                column_index=1,
                table_id="table-turnover",
                label_axis="row",
            ),
            _manager_profile_cell(
                "换手率计算口径",
                "双边成交金额除以平均股票市值",
                row_index=1,
                column_index=1,
                table_id="table-turnover",
                label_axis="row",
            ),
        ),
    )
    top_holdings_table = _DisclosureTable(
        table_id="table-top-holdings",
        section_id="section-holdings",
        heading_text="前十名股票投资明细",
        table_caption_or_nearby_heading="前十名股票投资明细",
        heading_path=("投资组合", "前十名股票投资明细"),
        cells=(
            _manager_profile_holdings_cell(
                "股票代码", "600000", row_index=0, column_index=0, table_id="table-top-holdings"
            ),
            _manager_profile_holdings_cell(
                "股票名称", "浦发银行", row_index=0, column_index=1, table_id="table-top-holdings"
            ),
            _manager_profile_holdings_cell(
                "公允价值",
                "1,234,567.89",
                row_index=0,
                column_index=2,
                table_id="table-top-holdings",
            ),
        ),
    )
    industry_table = _DisclosureTable(
        table_id="table-industry",
        section_id="section-industry",
        heading_text="报告期末按行业分类的股票投资组合",
        table_caption_or_nearby_heading="报告期末按行业分类的股票投资组合",
        heading_path=("投资组合", "报告期末按行业分类的股票投资组合"),
        cells=(
            _manager_profile_holdings_cell(
                "行业类别", "制造业", row_index=0, column_index=0, table_id="table-industry"
            ),
            _manager_profile_holdings_cell(
                "公允价值",
                "2,000,000.00",
                row_index=0,
                column_index=1,
                table_id="table-industry",
            ),
            _manager_profile_holdings_cell(
                "占基金资产净值比例",
                "12.34%",
                row_index=0,
                column_index=2,
                table_id="table-industry",
            ),
        ),
    )
    paragraphs = (
        _DisclosureParagraph(
            block_id="paragraph-strategy",
            section_id="section-strategy",
            heading_path=("报告期内基金投资策略和运作分析",),
            text_raw="本报告期坚持均衡配置。",
            text_normalized="本报告期坚持均衡配置。",
        ),
        _DisclosureParagraph(
            block_id="paragraph-outlook",
            section_id="section-outlook",
            heading_path=("后市展望",),
            text_raw="后续将关注基本面变化。",
            text_normalized="后续将关注基本面变化。",
        ),
        _DisclosureParagraph(
            block_id="paragraph-manager-holding",
            section_id="section-alignment",
            heading_path=("基金经理持有本基金情况",),
            text_raw="本基金基金经理持有本开放式基金份额区间为100万份以上。",
            text_normalized="本基金基金经理持有本开放式基金份额区间为100万份以上。",
        ),
        _DisclosureParagraph(
            block_id="paragraph-employee-holding",
            section_id="section-alignment",
            heading_path=("基金管理人从业人员持有本基金情况",),
            text_raw="基金管理人所有从业人员持有本基金份额区间为50万份至100万份。",
            text_normalized="基金管理人所有从业人员持有本基金份额区间为50万份至100万份。",
        ),
    )
    return _disclosure_intermediate(
        paragraph_blocks=paragraphs,
        table_blocks=(roster_table, turnover_table, top_holdings_table, industry_table),
        source_truth_admission=source_truth_admission,
    )


def _manager_profile_cell(
    label: str,
    value: str,
    *,
    row_index: int,
    column_index: int,
    table_id: str = "table-roster",
    label_axis: Literal["row", "column"] = "column",
) -> _DisclosureCell:
    """构造 manager_profile table/cell facade fixture。

    Args:
        label: 行标签或列头文本。
        value: 单元格披露值。
        row_index: 行号。
        column_index: 列号。
        table_id: 所属表格 ID。
        label_axis: label 放入 row label 还是 column header。

    Returns:
        FDD cell stub。

    Raises:
        无显式抛出。
    """

    row_label_path = (label,) if label_axis == "row" else ("经理信息",)
    column_header_path = (label,) if label_axis == "column" else ("内容",)
    return _DisclosureCell(
        cell_id=f"{table_id}-cell-{row_index}-{column_index}",
        table_id=table_id,
        section_anchor="section-manager",
        heading_path=("基金经理情况",),
        row_index=row_index,
        column_index=column_index,
        row_label_path=row_label_path,
        column_header_path=column_header_path,
        cell_text=value,
    )


def _manager_profile_holdings_cell(
    header: str,
    value: str,
    *,
    row_index: int,
    column_index: int,
    table_id: str,
) -> _DisclosureCell:
    """构造 holdings_snapshot table/cell facade fixture。

    Args:
        header: 中文披露列头。
        value: 单元格披露值。
        row_index: 行号。
        column_index: 列号。
        table_id: 所属表格 ID。

    Returns:
        FDD cell stub。

    Raises:
        无显式抛出。
    """

    return _DisclosureCell(
        cell_id=f"{table_id}-cell-{row_index}-{column_index}",
        table_id=table_id,
        section_anchor="section-holdings",
        heading_path=("投资组合",),
        row_index=row_index,
        column_index=column_index,
        row_label_path=("持仓明细",),
        column_header_path=(header,),
        cell_text=value,
    )


def _source_truth_admission_proof() -> FundDisclosureSourceTruthAdmissionProof:
    """构造测试用合法 source-truth admission proof。

    Args:
        无。

    Returns:
        合法的 FDD source-truth 正向证明。

    Raises:
        ValueError: 当 proof 字段不满足契约时由 dataclass 抛出。
    """

    return FundDisclosureSourceTruthAdmissionProof(
        proof_kind="repository_loaded_annual_report_identity.v1",
        source_boundary="annual_report",
        fund_code="110011",
        report_year=2024,
        document_kind="annual_report",
        intermediate_kind="fund_disclosure_document.v1",
        source_kind="annual_report",
        repository_identity_verified=True,
        source_provenance_verified=True,
        locator_identity_verified=True,
        parser_integrity_verified=True,
        producer="FundDocumentRepository",
    )


async def _assert_explicit_disclosure_failure_class_raises(
    failure_class: AnnualReportSourceFailureCategory,
) -> None:
    """断言显式 FDD failure_class 不会 fallback 到 parsed annual 路径。

    Args:
        failure_class: 来源失败分类。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当显式 FDD 失败被吞掉或返回 bundle 时抛出。
    """

    registry = FundProcessorRegistry.create_default()
    extractor = FundDataExtractor(
        repository=_FakeRepository(_annual_report()),
        nav_provider=_RecordingNavProvider(),
        processor_registry=registry,
    )

    with pytest.raises(RuntimeError, match="fund_disclosure_document processor"):
        await extractor.extract(
            "110011",
            2024,
            disclosure_intermediate=_disclosure_intermediate(failure_class=failure_class),
        )


def _index_annual_report() -> ParsedAnnualReport:
    """构造指数基金年报 fixture（非 active 类型走 direct path）。"""

    section_one = "\n".join(
        (
            "§1 基金简介",
            "基金名称：测试指数基金",
            "基金代码：000001",
            "基金类别：股票指数型",
            "业绩比较基准：沪深300指数收益率",
        )
    )
    section_two = "\n".join(
        (
            "§2 基金简介",
            "投资目标：跟踪标的指数",
            "投资范围：主要投资指数成分股",
            "管理费率：0.50%",
            "托管费率：0.10%",
        )
    )
    raw_text = f"{section_one}\n{section_two}"
    section_one_start = 0
    section_two_start = len(section_one) + 1
    return ParsedAnnualReport(
        key=DocumentKey(fund_code="000001", year=2024),
        raw_text=raw_text,
        sections={
            "§1": ReportSection(
                section_id="§1",
                title="§1 基金简介",
                start_offset=section_one_start,
                end_offset=len(section_one),
                matched_rule="fixture",
                confidence=1.0,
            ),
            "§2": ReportSection(
                section_id="§2",
                title="§2 基金简介",
                start_offset=section_two_start,
                end_offset=len(raw_text),
                matched_rule="fixture",
                confidence=1.0,
            ),
        },
        tables=(),
        metadata=AnnualReportMetadata(),
    )


def _annual_report(
    *,
    source_metadata: AnnualReportSourceMetadata | None = None,
) -> ParsedAnnualReport:
    """构造可被当前 extractor 解析的最小年报。

    Args:
        source_metadata: 可选年报来源元数据。

    Returns:
        最小年报解析结果。

    Raises:
        无显式抛出。
    """

    section_one = "\n".join(
        (
            "§1 基金简介",
            "基金名称：测试成长基金",
            "基金代码：110011",
            "基金类别：混合型",
            "管理人：测试基金管理有限公司",
            "托管人：中国银行股份有限公司",
            "基金合同生效日：2020年1月1日",
        )
    )
    section_two = "\n".join(
        (
            "§2 基金简介",
            "投资目标：追求长期资本增值",
            "投资范围：主要投资股票和债券",
            "业绩比较基准：沪深300指数收益率",
            "管理费率：1.20%",
            "托管费率：0.20%",
        )
    )
    section_four = "\n".join(
        (
            "§4 管理人报告",
            "4.1.2 基金经理简介",
            "本节基金经理任期字段由表格承载。",
            "4.4 报告期内基金投资策略和运作分析",
            "长期均衡配置消费和制造行业。",
            "4.5 管理人对宏观经济、证券市场及行业走势的简要展望",
            "保持审慎。",
        )
    )
    section_eight = "\n".join(
        (
            "§8 投资组合报告",
            "换手率：80.00%",
            "期初份额：100",
            "期末份额：110",
            "净变动：10",
        )
    )
    section_nine = "\n".join(
        (
            "§9 基金份额持有人信息",
            "基金经理持有本基金：0份",
            "从业人员持有本基金：100份",
            "机构投资者持有比例：30%",
            "个人投资者持有比例：70%",
        )
    )
    raw_text = "\n".join(
        (
            section_one,
            section_two,
            section_four,
            section_eight,
            section_nine,
        )
    )
    section_one_start = 0
    section_two_start = len(section_one) + 1
    section_four_start = section_two_start + len(section_two) + 1
    section_eight_start = section_four_start + len(section_four) + 1
    section_nine_start = section_eight_start + len(section_eight) + 1
    return ParsedAnnualReport(
        key=DocumentKey(fund_code="110011", year=2024),
        raw_text=raw_text,
        sections={
            "§1": ReportSection(
                section_id="§1",
                title="§1 基金简介",
                start_offset=section_one_start,
                end_offset=len(section_one),
                matched_rule="fixture",
                confidence=1.0,
            ),
            "§2": ReportSection(
                section_id="§2",
                title="§2 基金简介",
                start_offset=section_two_start,
                end_offset=section_four_start,
                matched_rule="fixture",
                confidence=1.0,
            ),
            "§4": ReportSection(
                section_id="§4",
                title="§4 管理人报告",
                start_offset=section_four_start,
                end_offset=section_eight_start,
                matched_rule="fixture",
                confidence=1.0,
            ),
            "§8": ReportSection(
                section_id="§8",
                title="§8 投资组合报告",
                start_offset=section_eight_start,
                end_offset=section_nine_start,
                matched_rule="fixture",
                confidence=1.0,
            ),
            "§9": ReportSection(
                section_id="§9",
                title="§9 基金份额持有人信息",
                start_offset=section_nine_start,
                end_offset=len(raw_text),
                matched_rule="fixture",
                confidence=1.0,
            ),
        },
        tables=(
            ParsedTable(
                page_number=5,
                table_index=1,
                headers=("投资目标", "追求长期资本增值"),
                rows=(
                    ("投资范围", "主要投资股票和债券"),
                    ("风险收益特征", "本基金为混合型基金，风险收益特征高于债券型基金。"),
                    ("业绩比较基准", "沪深300指数收益率"),
                    ("管理费率", "1.20%"),
                    ("托管费率", "0.20%"),
                ),
            ),
            ParsedTable(
                page_number=22,
                table_index=0,
                headers=("姓名", "职务", "任职日期", "离任日期"),
                rows=(("张三", "基金经理", "2021-01-01", ""),),
            ),
        ),
        metadata=AnnualReportMetadata(source=source_metadata),
    )


def _bond_annual_report() -> ParsedAnnualReport:
    """构造债券基金年报 fixture。

    Args:
        无。

    Returns:
        可触发债券风险七组扫描的年报 fixture。

    Raises:
        无显式抛出。
    """

    section_one = "\n".join(
        [
            "基金名称：国泰利享中短债债券A",
            "基金代码：006597",
            "基金类别：债券型",
        ]
    )
    section_two = "\n".join(
        [
            "投资目标：在严格控制风险的前提下追求稳健收益",
            "投资范围：本基金主要投资于债券资产。",
            "业绩比较基准：中债综合财富指数收益率",
        ]
    )
    section_four = "\n".join(
        [
            "4.4 报告期内基金投资策略和运作分析",
            "本基金通过久期管理控制利率风险，主要投资中高等级信用债，控制信用风险。",
            "本基金严格控制流动性风险并力争控制回撤。",
        ]
    )
    raw_text = f"{section_one}\n{section_two}\n{section_four}"
    section_one_start = 0
    section_two_start = len(section_one) + 1
    section_four_start = section_two_start + len(section_two) + 1
    return ParsedAnnualReport(
        key=DocumentKey(fund_code="006597", year=2024),
        raw_text=raw_text,
        sections={
            "§1": ReportSection(
                section_id="§1",
                title="基金简介",
                start_offset=section_one_start,
                end_offset=len(section_one),
                matched_rule="fixture",
                confidence=1.0,
            ),
            "§2": ReportSection(
                section_id="§2",
                title="产品概况",
                start_offset=section_two_start,
                end_offset=section_two_start + len(section_two),
                matched_rule="fixture",
                confidence=1.0,
            ),
            "§4": ReportSection(
                section_id="§4",
                title="管理人报告",
                start_offset=section_four_start,
                end_offset=section_four_start + len(section_four),
                matched_rule="fixture",
                confidence=1.0,
            ),
        },
        tables=(),
        metadata=AnnualReportMetadata(),
    )


def _nav_series() -> FundNavSeries:
    """构造 2024 年度累计净值 series fixture。

    Args:
        无。

    Returns:
        可计算 -10% 最大回撤的 `FundNavSeries`。

    Raises:
        NavDataContractError: 当 fixture 不满足 typed contract 时抛出。
    """

    start = date(2024, 1, 1)
    values = [Decimal("1.00") + Decimal(index) / Decimal("1000") for index in range(30)]
    values[20] = Decimal("1.20")
    values[21] = Decimal("1.08")
    for index in range(22, 30):
        values[index] = Decimal("1.21") + Decimal(index) / Decimal("1000")
    records = tuple(
        FundNavRecord(
            date=start + timedelta(days=index),
            share_class="A",
            nav_value=value,
            nav_type="accumulated_nav",
            adjusted_basis="accumulated_nav",
            raw_change_rate=None,
            raw_payload={},
        )
        for index, value in enumerate(values)
    )
    return FundNavSeries(
        fund_code="006597",
        share_class="A",
        records=records,
        nav_type="accumulated_nav",
        adjusted_basis="accumulated_nav",
        dividend_adjustment_status="not_applicable",
        identity_status="verified",
        completeness_status="complete_enough",
        strong_drawdown_evidence_eligible=True,
        strong_drawdown_ineligibility_reason=None,
        source=NavSourceMetadata(
            source_name="csrc_eid",
            origin_source="csrc_eid",
            source_id="5755:2030-1010",
            source_url="https://eid.csrc.gov.cn/fund/5755",
            cached=False,
            retrieved_at=datetime(2026, 5, 29, tzinfo=timezone.utc),
            cache_updated_at=None,
            requested_fund_code="006597",
            returned_fund_code="006597",
            returned_fund_name="国泰利享中短债债券A",
            source_query_params=(("fund_code", "006597"), ("share_class", "A")),
        ),
        share_class_mapping=ShareClassMapping(
            requested_fund_code="006597",
            requested_share_class="A",
            resolved_fund_code="006597",
            resolved_share_class="A",
            mapping_status="verified",
            identity_status="verified",
            mapping_evidence=("fixture",),
        ),
        date_range_start=records[0].date,
        date_range_end=records[-1].date,
        record_count=len(records),
    )


def _fake_field() -> ExtractedField[dict[str, object]]:
    """构造 bundle 默认 provenance 测试用最小字段。

    Args:
        无。

    Returns:
        当前测试不读取内容的字段对象。

    Raises:
        无显式抛出。
    """

    return ExtractedField(value={}, anchors=(), extraction_mode="missing")
