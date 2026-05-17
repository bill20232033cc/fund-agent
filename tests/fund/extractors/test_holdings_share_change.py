"""`§8/§10` 持仓快照与份额变动 extractor 测试。"""

from __future__ import annotations

from fund_agent.fund.documents.models import DocumentKey, ParsedAnnualReport, ParsedTable, ReportSection
from fund_agent.fund.extractors.holdings_share_change import extract_holdings_share_change


def _build_report(tables: tuple[ParsedTable, ...]) -> ParsedAnnualReport:
    """构造带表格的最小年报对象。

    Args:
        tables: 表格元组。

    Returns:
        构造后的年报对象。

    Raises:
        无显式抛出。
    """

    raw_text = "§8 投资组合报告\n§10 基金份额变动\n"
    section_ten_start = raw_text.index("§10 基金份额变动")
    return ParsedAnnualReport(
        key=DocumentKey(fund_code="110011", year=2024),
        raw_text=raw_text,
        sections={
            "§8": ReportSection(
                section_id="§8",
                title="§8 投资组合报告",
                start_offset=0,
                end_offset=section_ten_start,
                matched_rule="fixture",
                confidence=1.0,
            ),
            "§10": ReportSection(
                section_id="§10",
                title="§10 基金份额变动",
                start_offset=section_ten_start,
                end_offset=len(raw_text),
                matched_rule="fixture",
                confidence=1.0,
            ),
        },
        tables=tables,
    )


def _top_holdings_table() -> ParsedTable:
    """构造前十大重仓表。

    Args:
        无。

    Returns:
        前十大重仓表格。

    Raises:
        无显式抛出。
    """

    return ParsedTable(
        page_number=42,
        table_index=0,
        headers=("序号", "股票名称", "占基金资产净值比例", "前十大重仓"),
        rows=(
            ("1", "贵州茅台", "8.00%", "前十大重仓"),
            ("2", "宁德时代", "6.50%", "前十大重仓"),
        ),
    )


def _industry_distribution_table() -> ParsedTable:
    """构造行业分布表。

    Args:
        无。

    Returns:
        行业分布表格。

    Raises:
        无显式抛出。
    """

    return ParsedTable(
        page_number=43,
        table_index=1,
        headers=("行业", "占比"),
        rows=(
            ("制造业", "55.00%"),
            ("金融业", "12.00%"),
        ),
    )


def _share_change_table() -> ParsedTable:
    """构造份额变动表。

    Args:
        无。

    Returns:
        份额变动表格。

    Raises:
        无显式抛出。
    """

    return ParsedTable(
        page_number=58,
        table_index=0,
        headers=("项目", "份额"),
        rows=(
            ("期初基金份额总额", "1,000,000.00"),
            ("期末基金份额总额", "900,000.00"),
            ("本期申购赎回净额", "-100,000.00"),
        ),
    )


def test_extract_holdings_share_change_outputs_tables_with_table_anchors() -> None:
    """验证持仓快照和份额变动能输出表格型 anchor。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当字段或表格型 anchor 缺失时抛出。
    """

    report = _build_report((_top_holdings_table(), _industry_distribution_table(), _share_change_table()))

    result = extract_holdings_share_change(report)

    assert result.holdings_snapshot.extraction_mode == "direct"
    assert result.holdings_snapshot.value is not None
    assert result.holdings_snapshot.value["top_holdings"][0]["股票名称"] == "贵州茅台"
    assert result.holdings_snapshot.value["industry_distribution_status"] == "direct"
    assert result.holdings_snapshot.value["industry_distribution"][0]["行业"] == "制造业"
    assert {anchor.row_locator for anchor in result.holdings_snapshot.anchors} == {
        "top_holdings",
        "industry_distribution",
    }
    assert {anchor.page_number for anchor in result.holdings_snapshot.anchors} == {42, 43}
    assert all(anchor.table_id is not None for anchor in result.holdings_snapshot.anchors)
    assert result.share_change.extraction_mode == "direct"
    assert result.share_change.value == {
        "beginning_share": "1,000,000.00",
        "ending_share": "900,000.00",
        "net_change": "-100,000.00",
    }
    assert result.share_change.anchors[0].section_id == "§10"
    assert result.share_change.anchors[0].page_number == 58
    assert result.share_change.anchors[0].table_id == "page-58-table-0"
    assert result.share_change.anchors[0].row_locator == "share_change"


def test_extract_holdings_share_change_marks_industry_distribution_missing() -> None:
    """验证行业分布未披露时不会阻断前十大重仓输出。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当行业分布缺失状态不正确时抛出。
    """

    report = _build_report((_top_holdings_table(), _share_change_table()))

    result = extract_holdings_share_change(report)

    assert result.holdings_snapshot.extraction_mode == "direct"
    assert result.holdings_snapshot.value is not None
    assert result.holdings_snapshot.value["industry_distribution"] is None
    assert result.holdings_snapshot.value["industry_distribution_status"] == "missing"
    assert result.holdings_snapshot.note is not None


def test_extract_holdings_share_change_marks_missing_without_tables() -> None:
    """验证缺少可识别表格时显式返回 `missing`。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当缺失路径被静默处理时抛出。
    """

    report = _build_report(())

    result = extract_holdings_share_change(report)

    assert result.holdings_snapshot.extraction_mode == "missing"
    assert result.holdings_snapshot.value is None
    assert result.holdings_snapshot.anchors == ()
    assert result.share_change.extraction_mode == "missing"
    assert result.share_change.value is None
    assert result.share_change.anchors == ()
