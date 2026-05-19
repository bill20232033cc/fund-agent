"""`§8/§10` 持仓快照与份额变动 extractor 测试。"""

from __future__ import annotations

from fund_agent.fund.documents.models import DocumentKey, ParsedAnnualReport, ParsedTable, ReportSection
from fund_agent.fund.extractors.holdings_share_change import extract_holdings_share_change


def _build_report(tables: tuple[ParsedTable, ...], *, fund_code: str = "110011") -> ParsedAnnualReport:
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
        key=DocumentKey(fund_code=fund_code, year=2024),
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


def _share_change_table_with_subscription_and_redemption_rows() -> ParsedTable:
    """构造申购/赎回拆分披露的份额变动表。

    Args:
        无。

    Returns:
        份额变动表格。

    Raises:
        无显式抛出。
    """

    return ParsedTable(
        page_number=64,
        table_index=0,
        headers=("项目", "A类份额", "C类份额"),
        rows=(
            ("本报告期期初基金份额总额", "1,000,000.00", "-"),
            ("本报告期基金总申购份额", "200,000.00", "50,000.00"),
            ("减：本报告期基金总赎回份额", "300,000.00", "25,000.00"),
            ("本报告期期末基金份额总额", "900,000.00", "25,000.00"),
        ),
    )


def _share_change_table_with_code_headers() -> ParsedTable:
    """构造包含基金代码表头的多份额变动表。

    Args:
        无。

    Returns:
        份额变动表格。

    Raises:
        无显式抛出。
    """

    return ParsedTable(
        page_number=65,
        table_index=0,
        headers=("项目", "110010 A类份额", "110011 C类份额"),
        rows=(
            ("本报告期期初基金份额总额", "1,000,000.00", "10,000.00"),
            ("本报告期期末基金份额总额", "900,000.00", "25,000.00"),
            ("本期申购赎回净额", "-100,000.00", "15,000.00"),
        ),
    )


def _ambiguous_share_change_table() -> ParsedTable:
    """构造无法可靠选择份额列的多份额变动表。

    Args:
        无。

    Returns:
        份额变动表格。

    Raises:
        无显式抛出。
    """

    return ParsedTable(
        page_number=66,
        table_index=0,
        headers=("项目", "B类份额", "C类份额"),
        rows=(
            ("本报告期期初基金份额总额", "1,000,000.00", "10,000.00"),
            ("本报告期期末基金份额总额", "900,000.00", "25,000.00"),
            ("本期申购赎回净额", "-100,000.00", "15,000.00"),
        ),
    )


def _share_change_table_with_total_and_classes() -> ParsedTable:
    """构造总份额列与 A/C 份额列并存的份额变动表。

    Args:
        无。

    Returns:
        份额变动表格。

    Raises:
        无显式抛出。
    """

    return ParsedTable(
        page_number=67,
        table_index=0,
        headers=("项目", "基金份额总额", "A类份额", "C类份额"),
        rows=(
            ("本报告期期初基金份额总额", "1,010,000.00", "1,000,000.00", "10,000.00"),
            ("本报告期期末基金份额总额", "925,000.00", "900,000.00", "25,000.00"),
            ("本期申购赎回净额", "-85,000.00", "-100,000.00", "15,000.00"),
        ),
    )


def _share_change_table_with_a_and_d_classes() -> ParsedTable:
    """构造 A/D 份额列并存的份额变动表。

    Args:
        无。

    Returns:
        份额变动表格。

    Raises:
        无显式抛出。
    """

    return ParsedTable(
        page_number=68,
        table_index=0,
        headers=("项目", "A类份额", "D类份额"),
        rows=(
            ("本报告期期初基金份额总额", "1,000,000.00", "10,000.00"),
            ("本报告期期末基金份额总额", "900,000.00", "25,000.00"),
            ("本期申购赎回净额", "-100,000.00", "15,000.00"),
        ),
    )


def _share_change_table_with_other_code_and_a_class() -> ParsedTable:
    """构造包含非当前基金代码列和 A 类列的歧义表。

    Args:
        无。

    Returns:
        份额变动表格。

    Raises:
        无显式抛出。
    """

    return ParsedTable(
        page_number=68,
        table_index=0,
        headers=("项目", "110010 A类份额", "A类份额"),
        rows=(
            ("本报告期期初基金份额总额", "1,000,000.00", "10,000.00"),
            ("本报告期期末基金份额总额", "900,000.00", "25,000.00"),
            ("本期申购赎回净额", "-100,000.00", "15,000.00"),
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
        "share_class_column": "份额",
        "share_class_selection_reason": "single_value_column",
    }
    assert result.share_change.anchors[0].section_id == "§10"
    assert result.share_change.anchors[0].page_number == 58
    assert result.share_change.anchors[0].table_id == "page-58-table-0"
    assert result.share_change.anchors[0].row_locator == "share_change"


def test_extract_holdings_share_change_outputs_share_change_from_subscription_redemption_table() -> None:
    """验证申购/赎回拆分的 `§10` 表格可抽取份额变动。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当申购/赎回表识别或净变动计算失败时抛出。
    """

    report = _build_report((_share_change_table_with_subscription_and_redemption_rows(),))

    result = extract_holdings_share_change(report)

    assert result.share_change.extraction_mode == "missing"
    assert result.share_change.value is None
    assert "多个份额列" in (result.share_change.note or "")


def test_extract_holdings_share_change_selects_exact_fund_code_column() -> None:
    """验证份额变动优先选择表头精确包含当前基金代码的列。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当基金代码列未被优先选择时抛出。
    """

    report = _build_report((_share_change_table_with_code_headers(),))

    result = extract_holdings_share_change(report)

    assert result.share_change.extraction_mode == "direct"
    assert result.share_change.value == {
        "beginning_share": "10,000.00",
        "ending_share": "25,000.00",
        "net_change": "15,000.00",
        "share_class_column": "110011 C类份额",
        "share_class_selection_reason": "fund_code_header_match",
    }


def test_extract_holdings_share_change_marks_ambiguous_multi_class_table_missing() -> None:
    """验证无法可靠选择份额列时不再默认取第一列。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当歧义多列表未 fail closed 时抛出。
    """

    report = _build_report((_ambiguous_share_change_table(),))

    result = extract_holdings_share_change(report)

    assert result.share_change.extraction_mode == "missing"
    assert result.share_change.value is None
    assert "多个份额列" in (result.share_change.note or "")


def test_extract_holdings_share_change_marks_total_and_classes_table_missing() -> None:
    """验证总份额列与 A/C 列并存且无代码表头时 fail closed。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当总份额列被误选时抛出。
    """

    report = _build_report((_share_change_table_with_total_and_classes(),))

    result = extract_holdings_share_change(report)

    assert result.share_change.extraction_mode == "missing"
    assert result.share_change.value is None


def test_extract_holdings_share_change_does_not_default_to_a_class_for_non_a_fund() -> None:
    """验证非 A 类基金在 A/D 多份额表中不会默认选择 A 类。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当非 A 类基金误选 A 类份额时抛出。
    """

    report = _build_report((_share_change_table_with_a_and_d_classes(),), fund_code="019264")

    result = extract_holdings_share_change(report)

    assert result.share_change.extraction_mode == "missing"
    assert result.share_change.value is None


def test_extract_holdings_share_change_does_not_fallback_when_other_code_header_exists() -> None:
    """验证存在其他基金代码表头时不使用 A 类 fallback。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 code-specific 冲突列被忽略时抛出。
    """

    report = _build_report((_share_change_table_with_other_code_and_a_class(),))

    result = extract_holdings_share_change(report)

    assert result.share_change.extraction_mode == "missing"
    assert result.share_change.value is None


def test_extract_holdings_share_change_ignores_profit_change_table() -> None:
    """验证利润分配变动表不会被误识别为基金份额变动。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当非份额表被误命中时抛出。
    """

    profit_table = ParsedTable(
        page_number=35,
        table_index=1,
        headers=("项目", "已实现部分", "未实现部分", "未分配利润合计"),
        rows=(
            ("本期期初", "-", "-", "-"),
            (
                "本期基金份额交易产生的变动数",
                "17,018,032.90",
                "-4,617,878.47",
                "12,400,154.43",
            ),
            ("其中：基金申购款", "38,799,313.90", "-8,896,172.47", "29,903,141.43"),
            ("基金赎回款", "-21,781,281.00", "4,278,294.00", "-17,502,987.00"),
            ("本期末", "14,035,524.09", "-3,106,403.66", "10,929,120.43"),
        ),
    )
    report = _build_report((profit_table,))

    result = extract_holdings_share_change(report)

    assert result.share_change.extraction_mode == "missing"
    assert result.share_change.value is None
    assert result.share_change.anchors == ()


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
