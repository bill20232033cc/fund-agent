"""golden answer 预填底稿测试。"""

from __future__ import annotations

from decimal import Decimal

from fund_agent.fund.data.nav_data import NavDataResult
from fund_agent.fund.data_extractor import StructuredFundDataBundle
from fund_agent.fund.extractors import (
    EvidenceAnchor,
    ExtractedField,
    IndexProfileValue,
    TrackingErrorValue,
)
from fund_agent.fund.golden_prefill import run_golden_prefill


class _FakeGoldenExtractor:
    """golden prefill 测试用 fake extractor。"""

    async def extract(
        self,
        fund_code: str,
        report_year: int,
        *,
        force_refresh: bool = False,
    ) -> StructuredFundDataBundle:
        """返回固定结构化数据包。

        Args:
            fund_code: 基金代码。
            report_year: 年报年份。
            force_refresh: 是否强制刷新。

        Returns:
            fake 结构化数据包。

        Raises:
            无显式抛出。
        """

        anchor = EvidenceAnchor(
            source_kind="annual_report",
            document_year=report_year,
            section_id="§2",
            page_number=5,
            table_id="page-5-table-0",
            row_locator="fund_name",
            note="基金名称：测试基金",
        )
        missing_field = ExtractedField(value=None, anchors=(), extraction_mode="missing", note="fixture")
        index_profile: ExtractedField[IndexProfileValue] = ExtractedField(
            value=IndexProfileValue(
                benchmark_text="测试指数收益率",
                benchmark_identity_status="identified",
                benchmark_index_name="测试指数",
                benchmark_index_code="000001",
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
                    document_year=report_year,
                    section_id="§2",
                    page_number=5,
                    table_id="page-5-table-1",
                    row_locator="benchmark_index_name",
                    note="指数名称：测试指数",
                ),
            ),
            extraction_mode="direct",
        )
        tracking_error: ExtractedField[TrackingErrorValue] = ExtractedField(
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
                benchmark_index_name="测试指数",
                benchmark_index_code="000001",
                fund_series_source=None,
                index_series_source=None,
                observation_count=None,
                frequency="annual_report_period",
                annualization_factor=None,
                input_period_complete=True,
                provenance_note="年报直接披露。",
            ),
            anchors=(
                EvidenceAnchor(
                    source_kind="annual_report",
                    document_year=report_year,
                    section_id="§3",
                    page_number=6,
                    table_id=None,
                    row_locator="value_text",
                    note="报告期年化跟踪误差：1.23%",
                ),
            ),
            extraction_mode="direct",
        )
        return StructuredFundDataBundle(
            fund_code=fund_code,
            report_year=report_year,
            basic_identity=ExtractedField(
                value={
                    "fund_name": "测试基金",
                    "fund_code": fund_code,
                    "classified_fund_type": "active_fund",
                },
                anchors=(anchor,),
                extraction_mode="direct",
            ),
            product_profile=ExtractedField(
                value={
                    "investment_objective": "追求长期资本增值",
                    "style_positioning": "价值成长均衡",
                },
                anchors=(
                    EvidenceAnchor(
                        source_kind="annual_report",
                        document_year=report_year,
                        section_id="§2",
                        page_number=5,
                        table_id="page-5-table-1",
                        row_locator="style_positioning",
                        note="风格定位：价值成长均衡",
                    ),
                ),
                extraction_mode="direct",
            ),
            benchmark=ExtractedField(
                value={"benchmark_text": "测试基准"},
                anchors=(
                    EvidenceAnchor(
                        source_kind="annual_report",
                        document_year=report_year,
                        section_id="§2",
                        page_number=5,
                        table_id="page-5-table-1",
                        row_locator="benchmark",
                        note="业绩比较基准：测试基准",
                    ),
                ),
                extraction_mode="direct",
            ),
            fee_schedule=missing_field,
            index_profile=index_profile,
            turnover_rate=missing_field,
            nav_benchmark_performance=missing_field,
            investor_return=missing_field,
            tracking_error=tracking_error,
            share_change=missing_field,
            manager_alignment=missing_field,
            manager_strategy_text=missing_field,
            holdings_snapshot=missing_field,
            holder_structure=missing_field,
            nav_data=NavDataResult(fund_code=fund_code, records=[], source="fixture", cached=True),
        )


async def test_run_golden_prefill_writes_prefilled_markdown(tmp_path) -> None:
    """验证 golden prefill 会按模板写入预填 Markdown。

    Args:
        tmp_path: pytest 临时目录 fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当预填输出不符合预期时抛出。
    """

    template_path = tmp_path / "template.md"
    output_path = tmp_path / "prefill.md"
    template_path.write_text(
        "\n".join(
            (
                "# Correctness Golden Answer Template",
                "",
                "## 004393 测试基金（国内股票类）",
                "",
                "| field | sub_field | expected_value | confidence | source |",
                "|---|---|---|---|---|",
                "| basic_identity | fund_name | | | |",
                "| product_profile | style_positioning | | | |",
                "| classified_fund_type | fund_type | | | |",
                "| benchmark | benchmark_name | | | |",
                "| index_profile | benchmark_index_name | | | |",
                "| tracking_error | annualized | | | |",
                "| tracking_error | value_text | | | |",
                "| fee_schedule | — | — | — | 当前 slice 不处理 |",
            )
        ),
        encoding="utf-8",
    )

    result = await run_golden_prefill(
        template_path=template_path,
        output_path=output_path,
        report_year=2024,
        extractor=_FakeGoldenExtractor(),
    )

    output = output_path.read_text(encoding="utf-8")
    assert result.succeeded_fund_codes == ("004393",)
    assert "自动预填底稿" in output
    assert "| basic_identity | fund_name | 测试基金 | high | 年报2024 §2 page-5 page-5-table-0 fund_name |" in output
    assert "| product_profile | style_positioning | 价值成长均衡 | high | 年报2024 §2 page-5 page-5-table-1 style_positioning |" in output
    assert "| classified_fund_type | fund_type | active_fund | high | 年报2024 §2 page-5 page-5-table-0 fund_name |" in output
    assert "| benchmark | benchmark_name | 测试基准 | high | 年报2024 §2 page-5 page-5-table-1 benchmark |" in output
    assert "| index_profile | benchmark_index_name | 测试指数 | high | 年报2024 §2 page-5 page-5-table-1 benchmark_index_name |" in output
    assert "| tracking_error | annualized | True | high | 年报2024 §3 page-6 value_text |" in output
    assert "| tracking_error | value_text | 1.23% | high | 年报2024 §3 page-6 value_text |" in output
    assert "| fee_schedule | — | — | — | 当前 slice 不处理 |" in output
