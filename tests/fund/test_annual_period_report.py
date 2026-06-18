"""多年年报期间报告 renderer 测试。"""

from __future__ import annotations

from dataclasses import dataclass

import pytest

from fund_agent.fund.annual_evidence import (
    ANNUAL_EVIDENCE_ANCHOR_SCHEMA_VERSION,
    ANNUAL_EVIDENCE_BUNDLE_SCHEMA_VERSION,
    ANNUAL_EVIDENCE_CROSS_YEAR_FACT_SCHEMA_VERSION,
    AnnualEvidenceAnchor,
    AnnualEvidenceBundle,
    AnnualEvidenceGap,
    CrossYearDerivedFact,
)
from fund_agent.fund.source_provenance import default_public_source_provenance
from fund_agent.fund.template.annual_period_renderer import (
    AnnualPeriodReportRenderInput,
    QUALITY_GATE_STATUS_NOT_AVAILABLE,
    render_annual_period_report,
    validate_annual_period_report_wording,
)


@dataclass(frozen=True, slots=True)
class _CurrentYearBundle:
    """renderer 测试用当前年份 bundle 替身。"""

    fund_code: str
    report_year: int


def test_annual_period_report_renders_full_years_and_cross_year_facts() -> None:
    """验证完整五年 bundle 渲染覆盖表和跨年事实。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 渲染结果不符合契约时抛出。
    """

    result = render_annual_period_report(
        AnnualPeriodReportRenderInput(
            annual_evidence_bundle=_bundle_with_fact(canonical_years=(2025, 2024, 2023, 2022, 2021)),
            current_year_report_markdown=_current_year_report(),
            quality_gate_status="warn",
        )
    )

    assert result.report_markdown.startswith("# 多年年报分析（2021-2025）")
    assert "| 2025 | available | selected_source=none; source_mode=legacy_or_unknown" in (
        result.report_markdown
    )
    assert "fact_id=fact-fee" in result.report_markdown
    assert "source_years=2025,2024" in result.report_markdown
    assert "anchor-2025(year=2025, field=annual_evidence.fee_schedule" in result.report_markdown
    assert "quality_gate_status=warn" in result.report_markdown
    assert "<!-- current_year_report:start -->" in result.report_markdown
    assert "# 0. 投资要点概览" in result.current_year_report_markdown
    assert result.cross_year_fact_count == 1


def test_annual_period_report_renders_gap_and_fail_closed_without_overclaim() -> None:
    """验证缺口和 fail-closed 年份显式降级且不输出强结论。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 降级输出不符合契约时抛出。
    """

    result = render_annual_period_report(
        AnnualPeriodReportRenderInput(
            annual_evidence_bundle=_bundle_with_fact(
                gap_years=(2023,),
                fail_closed_years=(2022,),
                data_gaps=(
                    AnnualEvidenceGap(
                        gap_id="gap-2023",
                        year=2023,
                        status="gap",
                        source_failure_category="not_found",
                        message="fixture gap",
                    ),
                ),
            ),
            current_year_report_markdown=_current_year_report(),
            quality_gate_status="pass",
        )
    )

    assert "gap_years: 2023" in result.report_markdown
    assert "fail_closed_years: 2022" in result.report_markdown
    assert "gap_note:" in result.report_markdown
    assert "fail_closed_note:" in result.report_markdown
    assert "当前结论仍以目标年份报告和质量门控为准" in result.report_markdown
    assert "建议买入" not in result.period_summary_markdown
    assert "收益预测" not in result.period_summary_markdown


def test_annual_period_report_renders_all_prior_years_gap_as_insufficient() -> None:
    """验证所有 prior 年份缺口时输出最小跨年证据不足路径。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 缺证据路径不符合契约时抛出。
    """

    result = render_annual_period_report(
        AnnualPeriodReportRenderInput(
            annual_evidence_bundle=_bundle_without_fact(
                canonical_years=(2025, 2024, 2023, 2022, 2021),
                available_years=(2025,),
                gap_years=(2024, 2023, 2022, 2021),
            ),
            current_year_report_markdown=_current_year_report(),
        )
    )

    assert "跨年事实：insufficient_evidence" in result.report_markdown
    assert "impact_status=insufficient_evidence" in result.report_markdown
    assert f"quality_gate_status={QUALITY_GATE_STATUS_NOT_AVAILABLE}" in result.report_markdown
    assert "不据此声明通过或 readiness" in result.report_markdown


def test_annual_period_report_redacts_raw_pdf_or_cache_paths() -> None:
    """验证跨年事实值中的 raw PDF/cache 路径不被渲染。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 路径未脱敏时抛出。
    """

    result = render_annual_period_report(
        AnnualPeriodReportRenderInput(
            annual_evidence_bundle=_bundle_with_fact(
                values_by_year={2025: {"raw_path": "/tmp/cache/report.pdf"}, 2024: "1.30%"}
            ),
            current_year_report_markdown=_current_year_report(),
            quality_gate_status="warn",
        )
    )

    assert "/tmp/cache/report.pdf" not in result.report_markdown
    assert "redacted_path" in result.report_markdown


@pytest.mark.parametrize("forbidden_text", ("建议买入", "收益预测", "必然带来收益"))
def test_annual_period_report_wording_guard_rejects_forbidden_impact_text(
    forbidden_text: str,
) -> None:
    """验证影响章节 wording guard 拒绝禁用措辞。

    Args:
        forbidden_text: 人工构造的禁用措辞。

    Returns:
        无返回值。

    Raises:
        AssertionError: 禁用措辞未触发错误时抛出。
    """

    with pytest.raises(ValueError, match="禁用措辞"):
        validate_annual_period_report_wording(
            "# 多年年报分析（2021-2025）\n\n"
            "## 对当前判断的影响\n\n"
            f"- {forbidden_text}\n\n"
            "## 缺口与降级\n"
        )


def test_annual_period_report_fails_closed_on_empty_current_year_report() -> None:
    """验证当前年份报告为空时 fail closed。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 空报告未触发错误时抛出。
    """

    with pytest.raises(ValueError, match="不能为空"):
        render_annual_period_report(
            AnnualPeriodReportRenderInput(
                annual_evidence_bundle=_bundle_without_fact(),
                current_year_report_markdown="",
            )
        )


def _current_year_report() -> str:
    """返回测试用当前年份报告。

    Args:
        无。

    Returns:
        当前年份报告 Markdown。

    Raises:
        无显式抛出。
    """

    return "# 0. 投资要点概览\n\n# 7. 是否值得持有——最终判断\n"


def _bundle_with_fact(
    *,
    canonical_years: tuple[int, ...] = (2025, 2024),
    gap_years: tuple[int, ...] = (),
    fail_closed_years: tuple[int, ...] = (),
    data_gaps: tuple[AnnualEvidenceGap, ...] = (),
    values_by_year: dict[int, object] | None = None,
) -> AnnualEvidenceBundle:
    """构造含跨年事实的测试 bundle。

    Args:
        canonical_years: 规范年份。
        gap_years: 缺口年份。
        fail_closed_years: fail-closed 年份。
        data_gaps: 数据缺口。
        values_by_year: 跨年事实值。

    Returns:
        多年年报证据 bundle。

    Raises:
        无显式抛出。
    """

    fact = CrossYearDerivedFact(
        schema_version=ANNUAL_EVIDENCE_CROSS_YEAR_FACT_SCHEMA_VERSION,
        fact_id="fact-fee",
        fact_type="fee_schedule_trend",
        source_field_id="annual_evidence.cross_year.fee_schedule_trend",
        status="available",
        values_by_year=values_by_year
        or {2025: {"management_fee": "1.20%"}, 2024: {"management_fee": "1.30%"}},
        source_years=(2025, 2024),
        source_year_anchor_ids=("anchor-2025", "anchor-2024"),
        dependency_requirements=("ch5.requirement.fee_schedule_trend",),
        caveats=(),
    )
    return AnnualEvidenceBundle(
        schema_version=ANNUAL_EVIDENCE_BUNDLE_SCHEMA_VERSION,
        fund_code="110011",
        target_year=2025,
        canonical_years=canonical_years,
        current_year_bundle=_CurrentYearBundle(fund_code="110011", report_year=2025),  # type: ignore[arg-type]
        year_records=(),
        available_years=tuple(
            year for year in canonical_years if year not in gap_years + fail_closed_years
        ),
        gap_years=gap_years,
        fail_closed_years=fail_closed_years,
        source_provenance_by_year={
            year: default_public_source_provenance() for year in canonical_years
        },
        source_documents_by_year={},
        anchors_by_year={
            2025: (_anchor("anchor-2025", 2025),),
            2024: (_anchor("anchor-2024", 2024),),
        },
        data_gaps=data_gaps,
        requirement_availability={
            "ch5.requirement.fee_schedule_trend": {"status": "available"}
        },
        cross_year_facts=(fact,),
        degradation_summary={"cross_year_claims_allowed": True},
        fallback_summary={"fallback_year_count": 0},
    )


def _bundle_without_fact(
    *,
    canonical_years: tuple[int, ...] = (2025, 2024),
    available_years: tuple[int, ...] = (2025,),
    gap_years: tuple[int, ...] = (2024,),
    fail_closed_years: tuple[int, ...] = (),
) -> AnnualEvidenceBundle:
    """构造无跨年事实的测试 bundle。

    Args:
        canonical_years: 规范年份。
        available_years: 可用年份。
        gap_years: 缺口年份。
        fail_closed_years: fail-closed 年份。

    Returns:
        多年年报证据 bundle。

    Raises:
        无显式抛出。
    """

    return AnnualEvidenceBundle(
        schema_version=ANNUAL_EVIDENCE_BUNDLE_SCHEMA_VERSION,
        fund_code="110011",
        target_year=2025,
        canonical_years=canonical_years,
        current_year_bundle=_CurrentYearBundle(fund_code="110011", report_year=2025),  # type: ignore[arg-type]
        year_records=(),
        available_years=available_years,
        gap_years=gap_years,
        fail_closed_years=fail_closed_years,
        source_provenance_by_year={
            year: default_public_source_provenance() for year in canonical_years
        },
        source_documents_by_year={},
        anchors_by_year={},
        data_gaps=(),
        requirement_availability={},
        cross_year_facts=(),
        degradation_summary={"cross_year_claims_allowed": False},
        fallback_summary={"fallback_year_count": 0},
    )


def _anchor(anchor_id: str, year: int) -> AnnualEvidenceAnchor:
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
