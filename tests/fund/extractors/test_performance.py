"""`§3` 表现 extractor 测试。"""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path

from fund_agent.fund.documents.models import DocumentKey, ParsedAnnualReport, ParsedTable, ReportSection
from fund_agent.fund.extractors.performance import extract_performance

_FIXTURE_DIR = Path(__file__).resolve().parents[2] / "fixtures" / "fund" / "extractors" / "performance"


def _load_fixture_text(filename: str) -> str:
    """读取 `§3` 表现测试夹具文本。

    Args:
        filename: 夹具文件名。

    Returns:
        夹具全文文本。

    Raises:
        FileNotFoundError: 夹具不存在时抛出。
        OSError: 夹具读取失败时抛出。
    """

    return (_FIXTURE_DIR / filename).read_text(encoding="utf-8")


def _build_report_from_fixture(filename: str, fund_code: str) -> ParsedAnnualReport:
    """把最小 `§3` 文本夹具构造成 `ParsedAnnualReport`。

    Args:
        filename: 夹具文件名。
        fund_code: 基金代码。

    Returns:
        构造后的年报对象。

    Raises:
        ValueError: 夹具缺少 `§3` 时抛出。
    """

    raw_text = _load_fixture_text(filename)
    section_start = raw_text.index("§3 主要财务指标、基金净值表现及利润分配情况")
    return ParsedAnnualReport(
        key=DocumentKey(fund_code=fund_code, year=2024),
        raw_text=raw_text,
        sections={
            "§3": ReportSection(
                section_id="§3",
                title="§3 主要财务指标、基金净值表现及利润分配情况",
                start_offset=section_start,
                end_offset=len(raw_text),
                matched_rule="fixture",
                confidence=1.0,
            ),
        },
        tables=(),
    )


def _build_report_with_tables(tables: tuple[ParsedTable, ...], fund_code: str) -> ParsedAnnualReport:
    """构造带 `§3` 表格的最小年报对象。

    Args:
        tables: 表格元组。
        fund_code: 基金代码。

    Returns:
        构造后的年报对象。

    Raises:
        无显式抛出。
    """

    raw_text = "§3 主要财务指标、基金净值表现及利润分配情况\n"
    return ParsedAnnualReport(
        key=DocumentKey(fund_code=fund_code, year=2024),
        raw_text=raw_text,
        sections={
            "§3": ReportSection(
                section_id="§3",
                title="§3 主要财务指标、基金净值表现及利润分配情况",
                start_offset=0,
                end_offset=len(raw_text),
                matched_rule="fixture",
                confidence=1.0,
            ),
        },
        tables=tables,
    )


def _build_report_with_text_and_tables(
    section_text: str,
    tables: tuple[ParsedTable, ...],
    fund_code: str,
) -> ParsedAnnualReport:
    """构造同时包含 `§3` 正文和表格的年报对象。

    Args:
        section_text: `§3` 正文。
        tables: 表格元组。
        fund_code: 基金代码。

    Returns:
        构造后的年报对象。

    Raises:
        无显式抛出。
    """

    raw_text = f"§3 主要财务指标、基金净值表现及利润分配情况\n{section_text}"
    return ParsedAnnualReport(
        key=DocumentKey(fund_code=fund_code, year=2024),
        raw_text=raw_text,
        sections={
            "§3": ReportSection(
                section_id="§3",
                title="§3 主要财务指标、基金净值表现及利润分配情况",
                start_offset=0,
                end_offset=len(raw_text),
                matched_rule="fixture",
                confidence=1.0,
            ),
        },
        tables=tables,
    )


def test_extract_performance_outputs_nav_and_benchmark_with_anchors() -> None:
    """验证 `§3` 能直接提取净值增长率与基准收益率，并带 anchor。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当字段或 anchor 缺失时抛出。
    """

    report = _build_report_from_fixture("performance_with_investor_return.txt", "110011")

    result = extract_performance(report)

    assert result.nav_benchmark_performance.extraction_mode == "direct"
    assert result.nav_benchmark_performance.value == {
        "nav_growth_rate": "12.34%",
        "benchmark_return_rate": "10.01%",
    }
    assert {anchor.source_kind for anchor in result.nav_benchmark_performance.anchors} == {"annual_report"}
    assert {anchor.section_id for anchor in result.nav_benchmark_performance.anchors} == {"§3"}
    assert {anchor.document_year for anchor in result.nav_benchmark_performance.anchors} == {2024}
    assert all(anchor.note is not None for anchor in result.nav_benchmark_performance.anchors)
    anchor_labels = {anchor.row_locator for anchor in result.nav_benchmark_performance.anchors}
    assert {"nav_growth_rate", "benchmark_return_rate"} <= anchor_labels


def test_extract_performance_outputs_direct_tracking_error_when_disclosed() -> None:
    """验证年报直接披露实际跟踪误差时返回结构化字段。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当跟踪误差未被结构化抽取时抛出。
    """

    report = _build_report_from_fixture("performance_with_tracking_error.txt", "510300")

    result = extract_performance(report)

    assert result.tracking_error.extraction_mode == "direct"
    assert result.tracking_error.value is not None
    assert result.tracking_error.value.value == Decimal("0.0123")
    assert result.tracking_error.value.value_text == "1.23%"
    assert result.tracking_error.value.period_label == "报告期"
    assert result.tracking_error.value.annualized is True
    assert result.tracking_error.value.source_type == "direct_disclosure"
    assert result.tracking_error.anchors[0].source_kind == "annual_report"
    assert result.tracking_error.anchors[0].section_id == "§3"
    assert result.tracking_error.anchors[0].row_locator == "tracking_error"


def test_extract_performance_does_not_treat_tracking_error_target_as_observed() -> None:
    """验证跟踪误差目标或限制文本不会被当作实际值。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当目标值被误抽取为实际跟踪误差时抛出。
    """

    report = _build_report_from_fixture("performance_with_tracking_error_target_only.txt", "510300")

    result = extract_performance(report)

    assert result.tracking_error.extraction_mode == "missing"
    assert result.tracking_error.value is None
    assert result.tracking_error.anchors == ()


def test_extract_performance_fails_closed_on_ambiguous_tracking_error_text() -> None:
    """验证实际值和目标值混杂时返回 ambiguous missing。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当模糊文本未 fail closed 时抛出。
    """

    report = _build_report_from_fixture("performance_with_tracking_error_ambiguous.txt", "510300")

    result = extract_performance(report)

    assert result.tracking_error.extraction_mode == "missing"
    assert result.tracking_error.value is None
    assert result.tracking_error.note == "tracking_error_ambiguous"


def test_extract_performance_does_not_use_standard_deviation_as_tracking_error() -> None:
    """验证净值或基准标准差不会被误认为跟踪误差。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当标准差被误抽取为跟踪误差时抛出。
    """

    report = _build_report_from_fixture("performance_with_standard_deviation_only.txt", "510300")

    result = extract_performance(report)

    assert result.tracking_error.extraction_mode == "missing"
    assert result.tracking_error.value is None


def test_extract_performance_outputs_tracking_error_from_annual_table() -> None:
    """验证年报表现表中直接披露跟踪误差时可抽取。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当表格跟踪误差抽取失败时抛出。
    """

    table = ParsedTable(
        page_number=9,
        table_index=1,
        headers=("阶段", "份额净值增长率①", "业绩比较基准收益率③", "年化跟踪误差"),
        rows=(("过去一年", "17.32%", "14.45%", "1.11%"),),
    )
    report = _build_report_with_tables((table,), "510300")

    result = extract_performance(report)

    assert result.tracking_error.extraction_mode == "direct"
    assert result.tracking_error.value is not None
    assert result.tracking_error.value.value == Decimal("0.0111")
    assert result.tracking_error.value.period_label == "过去一年"
    assert result.tracking_error.anchors[0].table_id == "page-9-table-1"


def test_extract_performance_keeps_table_match_when_text_discloses_same_tracking_error() -> None:
    """验证正文和表格披露同一跟踪误差时保留表格锚点。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当一致双披露被误判为 ambiguous 时抛出。
    """

    table = ParsedTable(
        page_number=9,
        table_index=1,
        headers=("阶段", "年化跟踪误差"),
        rows=(("过去一年", "0.53%"),),
    )
    report = _build_report_with_text_and_tables(
        "报告期年化跟踪误差为 0.53%。",
        (table,),
        "510300",
    )

    result = extract_performance(report)

    assert result.tracking_error.extraction_mode == "direct"
    assert result.tracking_error.value is not None
    assert result.tracking_error.value.value == Decimal("0.0053")
    assert result.tracking_error.anchors[0].table_id == "page-9-table-1"


def test_extract_performance_marks_table_text_conflicting_tracking_error_as_ambiguous() -> None:
    """验证正文和表格跟踪误差不一致时返回 ambiguous。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当冲突披露未 fail closed 时抛出。
    """

    table = ParsedTable(
        page_number=9,
        table_index=1,
        headers=("阶段", "年化跟踪误差"),
        rows=(("过去一年", "0.53%"),),
    )
    report = _build_report_with_text_and_tables(
        "报告期年化跟踪误差为 0.71%。",
        (table,),
        "510300",
    )

    result = extract_performance(report)

    assert result.tracking_error.extraction_mode == "missing"
    assert result.tracking_error.value is None
    assert result.tracking_error.note == "tracking_error_ambiguous"


def test_extract_performance_outputs_nav_and_benchmark_from_annual_table() -> None:
    """验证 `§3` 年度净值表现表可抽取净值增长率和基准收益率。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当表格抽取或 anchor 不正确时抛出。
    """

    table = ParsedTable(
        page_number=8,
        table_index=0,
        headers=("阶段", "份额净值\n增长率①", "份额净值增\n长率标准差②", "业绩比较\n基准收益\n率③"),
        rows=(
            ("过去三个月", "3.01%", "1.20%", "2.00%"),
            ("过去一年", "17.32%", "1.44%", "14.45%"),
        ),
    )
    report = _build_report_with_tables((table,), "004393")

    result = extract_performance(report)

    assert result.nav_benchmark_performance.extraction_mode == "direct"
    assert result.nav_benchmark_performance.value == {
        "nav_growth_rate": "17.32%",
        "benchmark_return_rate": "14.45%",
    }
    assert {anchor.page_number for anchor in result.nav_benchmark_performance.anchors} == {8}
    assert {anchor.table_id for anchor in result.nav_benchmark_performance.anchors} == {
        "page-8-table-0"
    }
    assert all(
        anchor.note is not None and "过去一年" in anchor.note
        for anchor in result.nav_benchmark_performance.anchors
    )


def test_extract_performance_ignores_standard_deviation_columns_when_order_changes() -> None:
    """验证净值表现表列序变化时不会把标准差列误当收益率。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当表头语义匹配误中标准差列时抛出。
    """

    table = ParsedTable(
        page_number=8,
        table_index=0,
        headers=("阶段", "份额净值增\n长率标准差②", "份额净值\n增长率①", "业绩比较基准收益率标准差④", "业绩比较\n基准收益\n率③"),
        rows=(("过去一年", "1.44%", "17.32%", "1.22%", "14.45%"),),
    )
    report = _build_report_with_tables((table,), "004393")

    result = extract_performance(report)

    assert result.nav_benchmark_performance.extraction_mode == "direct"
    assert result.nav_benchmark_performance.value == {
        "nav_growth_rate": "17.32%",
        "benchmark_return_rate": "14.45%",
    }


def test_extract_performance_outputs_direct_investor_return_when_disclosed() -> None:
    """验证投资者收益率直接披露时返回 `direct`。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当直接披露路径不正确时抛出。
    """

    report = _build_report_from_fixture("performance_with_investor_return.txt", "110011")

    result = extract_performance(report)

    assert result.investor_return.extraction_mode == "direct"
    assert result.investor_return.value == {
        "investor_return_rate": "8.88%",
        "disclosure_status": "direct",
        "fallback_status": "not_needed",
    }
    assert result.investor_return.anchors[0].source_kind == "annual_report"
    assert result.investor_return.anchors[0].section_id == "§3"
    assert result.investor_return.anchors[0].document_year == 2024
    assert result.investor_return.anchors[0].note is not None
    assert result.investor_return.anchors[0].row_locator == "investor_return_rate"


def test_extract_performance_outputs_estimated_investor_return_when_marked_in_section() -> None:
    """验证投资者收益率以估算口径披露时返回 `estimated`。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当估算披露路径不正确时抛出。
    """

    report = _build_report_from_fixture("performance_with_estimated_investor_return.txt", "000171")

    result = extract_performance(report)

    assert result.investor_return.extraction_mode == "estimated"
    assert result.investor_return.value == {
        "investor_return_rate": "6.66%",
        "disclosure_status": "estimated",
        "fallback_status": "estimated_disclosure_in_section",
    }
    assert result.investor_return.anchors[0].source_kind == "annual_report"
    assert result.investor_return.anchors[0].section_id == "§3"
    assert result.investor_return.anchors[0].document_year == 2024
    assert result.investor_return.anchors[0].note is not None
    assert result.investor_return.anchors[0].row_locator == "estimated_investor_return_rate"
    assert result.investor_return.note is not None


def test_extract_performance_marks_missing_investor_return_without_silent_blank() -> None:
    """验证投资者收益率未披露时显式返回 `missing`。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当未披露路径被静默处理时抛出。
    """

    report = _build_report_from_fixture("performance_without_investor_return.txt", "000171")

    result = extract_performance(report)

    assert result.nav_benchmark_performance.extraction_mode == "direct"
    assert result.investor_return.extraction_mode == "missing"
    assert result.investor_return.value == {
        "investor_return_rate": None,
        "disclosure_status": "missing",
        "fallback_status": "pending_later_slice",
    }
    assert result.investor_return.anchors == ()
    assert result.investor_return.note is not None


def test_extract_performance_marks_partial_nav_benchmark_as_missing() -> None:
    """验证 `nav_benchmark_performance` 部分命中时显式保留缺失状态。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当部分命中被伪装成完整 direct 时抛出。
    """

    report = _build_report_from_fixture("performance_with_partial_nav_only.txt", "510300")

    result = extract_performance(report)

    assert result.nav_benchmark_performance.extraction_mode == "missing"
    assert result.nav_benchmark_performance.value == {
        "nav_growth_rate": "9.99%",
        "benchmark_return_rate": None,
    }
    assert len(result.nav_benchmark_performance.anchors) == 1
    assert result.nav_benchmark_performance.anchors[0].row_locator == "nav_growth_rate"
    assert result.nav_benchmark_performance.note is not None
