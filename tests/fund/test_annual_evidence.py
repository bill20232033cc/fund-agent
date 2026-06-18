"""多年年报证据 bundle 与 Chapter 5 投影测试。"""

from __future__ import annotations

from decimal import Decimal

import pytest

from fund_agent.fund.annual_evidence import (
    ANNUAL_EVIDENCE_ANCHOR_SCHEMA_VERSION,
    ANNUAL_EVIDENCE_BUNDLE_SCHEMA_VERSION,
    ANNUAL_EVIDENCE_CROSS_YEAR_FACT_SCHEMA_VERSION,
    AnnualEvidenceAnchor,
    AnnualEvidenceBundle,
    AnnualEvidenceLoader,
    AnnualEvidenceScopeRequest,
    CrossYearDerivedFact,
)
from fund_agent.fund.chapter_facts import ChapterFactProvider
from fund_agent.fund.data.nav_data import NavDataResult
from fund_agent.fund.data_extractor import StructuredFundDataBundle
from fund_agent.fund.documents.sources import (
    AnnualReportSourceIntegrityError,
    AnnualReportSourceNotFoundError,
    AnnualReportSourceSchemaError,
    AnnualReportSourceUnavailableError,
)
from fund_agent.fund.extractors import EvidenceAnchor, ExtractedField, IndexProfileValue, TrackingErrorValue
from fund_agent.fund.source_provenance import default_public_source_provenance


def test_annual_evidence_scope_validates_canonical_years() -> None:
    """验证多年年报 scope 固定为 target year 加连续 prior years。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        无显式抛出。
    """

    scope = AnnualEvidenceScopeRequest(
        fund_code="110011",
        target_year=2025,
        required_years=(2025,),
        optional_years=(2024, 2023, 2022, 2021),
        max_years=5,
    )

    assert scope.canonical_years == (2025, 2024, 2023, 2022, 2021)


@pytest.mark.parametrize(
    ("optional_years", "message"),
    [
        ((2023, 2024), "optional_years 必须是 target_year 的连续前序年份"),
        ((2025,), "optional_years 不能包含 target_year"),
        ((2024, 2024), "optional_years 不能重复"),
    ],
)
def test_annual_evidence_scope_rejects_invalid_prior_years(
    optional_years: tuple[int, ...],
    message: str,
) -> None:
    """验证 prior year 校验 fail-fast。

    Args:
        optional_years: 测试输入年份。
        message: 预期错误片段。

    Returns:
        无返回值。

    Raises:
        无显式抛出。
    """

    with pytest.raises(ValueError, match=message):
        AnnualEvidenceScopeRequest(
            fund_code="110011",
            target_year=2025,
            required_years=(2025,),
            optional_years=optional_years,
            max_years=5,
        )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    (
        "failure",
        "expected_gap_years",
        "expected_fail_closed_years",
        "expected_category",
    ),
    [
        (
            AnnualReportSourceNotFoundError("not found"),
            (2024,),
            (),
            "not_found",
        ),
        (
            AnnualReportSourceUnavailableError("temporarily unavailable"),
            (2024,),
            (),
            "unavailable",
        ),
        (
            AnnualReportSourceIntegrityError("bad pdf"),
            (),
            (2024,),
            "integrity_error",
        ),
        (
            AnnualReportSourceSchemaError("schema drift"),
            (),
            (2024,),
            "schema_drift",
        ),
    ],
)
async def test_loader_classifies_optional_source_failures(
    failure: Exception,
    expected_gap_years: tuple[int, ...],
    expected_fail_closed_years: tuple[int, ...],
    expected_category: str,
) -> None:
    """验证 optional prior 年份失败不会杀死当前年份证据。

    Args:
        failure: fake repository 抛出的来源异常。
        expected_gap_years: 预期可降级缺口年份。
        expected_fail_closed_years: 预期 fail-closed 年份。
        expected_category: 预期来源失败类别。

    Returns:
        无返回值。

    Raises:
        无显式抛出。
    """

    loader = AnnualEvidenceLoader(
        repository=_FailingRepository(
            {
                2024: failure,
            }
        )
    )
    scope = AnnualEvidenceScopeRequest(
        fund_code="110011",
        target_year=2025,
        required_years=(2025,),
        optional_years=(2024,),
        max_years=5,
    )

    bundle = await loader.load(scope, current_year_bundle=_bundle(2025))

    assert bundle.available_years == (2025,)
    assert bundle.gap_years == expected_gap_years
    assert bundle.fail_closed_years == expected_fail_closed_years
    assert bundle.data_gaps[0].source_failure_category == expected_category


def test_project_annual_evidence_adds_chapter5_cross_year_fact() -> None:
    """验证多年 evidence 只以 additive 方式扩展第 5 章。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        无显式抛出。
    """

    bundle = _annual_bundle_with_cross_year_fact()

    projection = ChapterFactProvider().project_annual_evidence(bundle)
    chapter5 = next(chapter for chapter in projection.chapters if chapter.chapter_id == 5)

    assert "cross_period_comparison_missing" not in chapter5.missing_reasons
    assert "annual_evidence.cross_year.fee_schedule_trend" in chapter5.source_field_ids
    fact = next(
        item
        for item in chapter5.facts
        if item.source_field_id == "annual_evidence.cross_year.fee_schedule_trend"
    )
    assert fact.value["source_years"] == (2025, 2024)
    assert fact.evidence_anchor_ids == ("anchor-2025", "anchor-2024")


class _FailingRepository:
    """按年份抛出异常的 fake repository。"""

    def __init__(self, failures: dict[int, Exception]) -> None:
        """初始化 fake repository。

        Args:
            failures: 年份到异常的映射。

        Returns:
            无返回值。

        Raises:
            无显式抛出。
        """

        self.failures = failures
        self.calls: list[tuple[str, int, bool]] = []

    async def load_annual_report(
        self,
        fund_code: str,
        year: int,
        *,
        force_refresh: bool = False,
    ):
        """记录调用并抛出对应异常。

        Args:
            fund_code: 基金代码。
            year: 年份。
            force_refresh: 是否强制刷新。

        Returns:
            不返回。

        Raises:
            Exception: 按年份抛出测试异常。
        """

        self.calls.append((fund_code, year, force_refresh))
        raise self.failures[year]


def _annual_bundle_with_cross_year_fact() -> AnnualEvidenceBundle:
    """构造含跨年事实的 bundle。

    Args:
        无。

    Returns:
        多年年报证据 bundle。

    Raises:
        无显式抛出。
    """

    current_bundle = _bundle(2025)
    anchors_by_year = {
        2025: (_annual_anchor("anchor-2025", 2025),),
        2024: (_annual_anchor("anchor-2024", 2024),),
    }
    fact = CrossYearDerivedFact(
        schema_version=ANNUAL_EVIDENCE_CROSS_YEAR_FACT_SCHEMA_VERSION,
        fact_id="fact-fee",
        fact_type="fee_schedule_trend",
        source_field_id="annual_evidence.cross_year.fee_schedule_trend",
        status="available",
        values_by_year={2025: {"management_fee": "1.20%"}, 2024: {"management_fee": "1.30%"}},
        source_years=(2025, 2024),
        source_year_anchor_ids=("anchor-2025", "anchor-2024"),
        dependency_requirements=("ch5.requirement.fee_schedule_trend",),
        caveats=(),
    )
    return AnnualEvidenceBundle(
        schema_version=ANNUAL_EVIDENCE_BUNDLE_SCHEMA_VERSION,
        fund_code="110011",
        target_year=2025,
        canonical_years=(2025, 2024),
        current_year_bundle=current_bundle,
        year_records=(),
        available_years=(2025, 2024),
        gap_years=(),
        fail_closed_years=(),
        source_provenance_by_year={2025: default_public_source_provenance(), 2024: None},
        source_documents_by_year={},
        anchors_by_year=anchors_by_year,
        data_gaps=(),
        requirement_availability={
            "ch5.requirement.fee_schedule_trend": {"status": "available"}
        },
        cross_year_facts=(fact,),
        degradation_summary={"cross_year_claims_allowed": True},
        fallback_summary={"fallback_year_count": 0},
    )


def _annual_anchor(anchor_id: str, year: int) -> AnnualEvidenceAnchor:
    """构造年度锚点。

    Args:
        anchor_id: 锚点 ID。
        year: 年份。

    Returns:
        年度锚点。

    Raises:
        无显式抛出。
    """

    return AnnualEvidenceAnchor(
        schema_version=ANNUAL_EVIDENCE_ANCHOR_SCHEMA_VERSION,
        anchor_id=anchor_id,
        source_year=year,
        source_field_id="annual_evidence.fee_schedule",
        source_kind="annual_report",
        section_id="§7",
        page_number=None,
        table_id="fee",
        row_locator="management_fee",
        note=None,
    )


def _anchor(year: int, row_locator: str) -> EvidenceAnchor:
    """构造 extractor 锚点。

    Args:
        year: 年份。
        row_locator: 行定位。

    Returns:
        extractor 锚点。

    Raises:
        无显式抛出。
    """

    return EvidenceAnchor(
        source_kind="annual_report",
        document_year=year,
        section_id="§7",
        page_number=None,
        table_id=None,
        row_locator=row_locator,
        note=None,
    )


def _field(year: int, value: dict[str, object], row_locator: str) -> ExtractedField[dict[str, object]]:
    """构造结构化字段。

    Args:
        year: 年份。
        value: 字段值。
        row_locator: 行定位。

    Returns:
        抽取字段。

    Raises:
        无显式抛出。
    """

    return ExtractedField(
        value=value,
        anchors=(_anchor(year, row_locator),),
        extraction_mode="direct",
        note=None,
    )


def _bundle(year: int) -> StructuredFundDataBundle:
    """构造测试结构化数据包。

    Args:
        year: 报告年份。

    Returns:
        结构化数据包。

    Raises:
        无显式抛出。
    """

    missing_index_profile: ExtractedField[IndexProfileValue] = ExtractedField(
        value=None,
        anchors=(),
        extraction_mode="missing",
        note="fixture",
    )
    missing_tracking_error: ExtractedField[TrackingErrorValue] = ExtractedField(
        value=None,
        anchors=(),
        extraction_mode="missing",
        note="fixture",
    )
    return StructuredFundDataBundle(
        fund_code="110011",
        report_year=year,
        basic_identity=_field(
            year,
            {
                "fund_name": "测试基金",
                "fund_code": "110011",
                "classified_fund_type": "active_fund",
            },
            "basic_identity",
        ),
        product_profile=_field(year, {"investment_objective": "长期增值"}, "product_profile"),
        benchmark=_field(year, {"benchmark": "沪深300"}, "benchmark"),
        index_profile=missing_index_profile,
        fee_schedule=_field(year, {"management_fee": "1.20%"}, "fee_schedule"),
        turnover_rate=_field(year, {"turnover_rate": "80%"}, "turnover_rate"),
        nav_benchmark_performance=_field(year, {"nav_growth_rate": "1%"}, "performance"),
        investor_return=_field(year, {"investor_return_rate": "1%"}, "investor_return"),
        tracking_error=missing_tracking_error,
        share_change=_field(year, {"ending_share": "100"}, "share_change"),
        manager_alignment=_field(year, {"manager_holding": "0"}, "manager_alignment"),
        manager_strategy_text=_field(year, {"strategy_summary": "均衡配置"}, "strategy"),
        holdings_snapshot=_field(year, {"top_holdings": [{"name": "A"}]}, "holdings"),
        holder_structure=_field(year, {"individual_holder_ratio": "80%"}, "holders"),
        nav_data=NavDataResult(
            fund_code="110011",
            records=[{"date": f"{year}-12-31", "nav": Decimal("1.00")}],
            source="fixture",
            cached=True,
        ),
    )
