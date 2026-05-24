"""`§8/§10` 持仓快照与份额变动 extractor 测试。"""

from __future__ import annotations

from fund_agent.fund.documents.models import DocumentKey, ParsedAnnualReport, ParsedTable, ReportSection
from fund_agent.fund.extractors.holdings_share_change import extract_holdings_share_change


def _build_report(
    tables: tuple[ParsedTable, ...],
    *,
    fund_code: str = "110011",
    raw_text: str | None = None,
    include_section_two: bool = False,
) -> ParsedAnnualReport:
    """构造带表格的最小年报对象。

    Args:
        tables: 表格元组。
        fund_code: 基金代码。
        raw_text: 自定义年报文本。
        include_section_two: 是否加入 §2 章节。

    Returns:
        构造后的年报对象。

    Raises:
        无显式抛出。
    """

    resolved_raw_text = raw_text or "§8 投资组合报告\n§10 基金份额变动\n"
    sections = {}
    if include_section_two:
        section_two_start = resolved_raw_text.index("§2 基金简介")
        section_eight_start = resolved_raw_text.index("§8 投资组合报告")
        sections["§2"] = ReportSection(
            section_id="§2",
            title="§2 基金简介",
            start_offset=section_two_start,
            end_offset=section_eight_start,
            matched_rule="fixture",
            confidence=1.0,
        )
    section_eight_start = resolved_raw_text.index("§8 投资组合报告")
    section_ten_start = resolved_raw_text.index("§10 基金份额变动")
    sections["§8"] = ReportSection(
        section_id="§8",
        title="§8 投资组合报告",
        start_offset=section_eight_start,
        end_offset=section_ten_start,
        matched_rule="fixture",
        confidence=1.0,
    )
    sections["§10"] = ReportSection(
        section_id="§10",
        title="§10 基金份额变动",
        start_offset=section_ten_start,
        end_offset=len(resolved_raw_text),
        matched_rule="fixture",
        confidence=1.0,
    )
    return ParsedAnnualReport(
        key=DocumentKey(fund_code=fund_code, year=2024),
        raw_text=resolved_raw_text,
        sections=sections,
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


def _all_stock_details_table(row_count: int = 12) -> ParsedTable:
    """构造所有股票投资明细表。

    Args:
        row_count: 生成行数。

    Returns:
        所有股票投资明细表。

    Raises:
        无显式抛出。
    """

    return ParsedTable(
        page_number=55,
        table_index=1,
        headers=("序号", "股票代码", "股票名称", "数量（股）", "公允价值（元）", "占基金资产净值比例（%）"),
        rows=tuple(
            (
                str(index),
                f"600{index:03d}",
                f"股票{index}",
                f"{index},000",
                f"{index},000.00",
                f"{index}.00",
            )
            for index in range(1, row_count + 1)
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


def _single_share_change_table_with_other_code_header() -> ParsedTable:
    """构造单值列但表头属于其他基金代码的份额变动表。

    Args:
        无。

    Returns:
        份额变动表格。

    Raises:
        无显式抛出。
    """

    return ParsedTable(
        page_number=69,
        table_index=0,
        headers=("项目", "110010 A类份额"),
        rows=(
            ("本报告期期初基金份额总额", "1,000,000.00"),
            ("本报告期期末基金份额总额", "900,000.00"),
            ("本期申购赎回净额", "-100,000.00"),
        ),
    )


def _section_two_share_class_table() -> ParsedTable:
    """构造 §2 分级基金简称/交易代码表。

    Args:
        无。

    Returns:
        §2 基金简介表。

    Raises:
        无显式抛出。
    """

    return ParsedTable(
        page_number=5,
        table_index=0,
        headers=("基金名称", "安信企业价值优选混合型证券投资基金", ""),
        rows=(
            ("基金简称", "安信企业价值优选混合", ""),
            ("基金主代码", "004393", ""),
            ("下属分级基金的基\n金简称", "安信企业价值优选混合A", "安信企业价值优选混合C"),
            ("下属分级基金的交\n易代码", "004393", "020964"),
        ),
    )


def _split_share_header_table() -> ParsedTable:
    """构造 parser 拆出的份额变动表头表。

    Args:
        无。

    Returns:
        份额变动表头表。

    Raises:
        无显式抛出。
    """

    return ParsedTable(
        page_number=63,
        table_index=3,
        headers=("项目", "安信企业价值优选混合A", "安信企业价值优选混合C"),
        rows=(("基金合同生效日", "27,803,840.65", "-"),),
    )


def _split_share_data_table() -> ParsedTable:
    """构造 parser 拆出的份额变动数据表。

    Args:
        无。

    Returns:
        份额变动数据表。

    Raises:
        无显式抛出。
    """

    return ParsedTable(
        page_number=64,
        table_index=0,
        headers=("（2022年8月8日）\n基金份额总额", "", ""),
        rows=(
            ("本报告期期初基金\n份额总额", "27,666,410.41", "-"),
            ("本报告期基金总申\n购份额", "166,998,199.71", "29,282,197.42"),
            ("减：本报告期基金总\n赎回份额", "45,098,870.12", "16,074,013.17"),
            ("本报告期基金拆分\n变动份额", "-", "-"),
            ("本报告期期末基金\n份额总额", "149,565,740.00", "13,208,184.25"),
        ),
    )


def _unrelated_adjacent_header_like_table() -> ParsedTable:
    """构造物理位置不相邻的 A/C 表头样表。

    Args:
        无。

    Returns:
        A/C 表头样表。

    Raises:
        无显式抛出。
    """

    return ParsedTable(
        page_number=40,
        table_index=0,
        headers=("项目", "安信企业价值优选混合A", "安信企业价值优选混合C"),
        rows=(("基金合同生效日", "27,803,840.65", "-"),),
    )


def _mismatched_split_share_data_table() -> ParsedTable:
    """构造值列数量与 A/C 表头数量不一致的拆表数据表。

    Args:
        无。

    Returns:
        值列数量不匹配的数据表。

    Raises:
        无显式抛出。
    """

    return ParsedTable(
        page_number=64,
        table_index=0,
        headers=("（2022年8月8日）\n基金份额总额", ""),
        rows=(
            ("本报告期期初基金\n份额总额", "27,666,410.41"),
            ("本报告期基金总申\n购份额", "166,998,199.71"),
            ("减：本报告期基金总\n赎回份额", "45,098,870.12"),
            ("本报告期期末基金\n份额总额", "149,565,740.00"),
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
    assert result.holdings_snapshot.value["top_holdings_status"] == "direct_top_ten"
    assert result.holdings_snapshot.value["top_holdings_source"] == "top_ten"
    assert result.holdings_snapshot.value["industry_distribution_status"] == "direct"
    assert result.holdings_snapshot.value["industry_distribution"][0]["行业"] == "制造业"
    assert {anchor.row_locator for anchor in result.holdings_snapshot.anchors} == {
        "top_ten",
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


def test_extract_holdings_share_change_uses_all_stock_details_as_top_holdings_source() -> None:
    """验证 §8 所有股票投资明细可作为股票持仓来源并截取前 10 行。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当所有股票明细未被识别时抛出。
    """

    report = _build_report((_all_stock_details_table(), _industry_distribution_table(), _share_change_table()))

    result = extract_holdings_share_change(report)

    assert result.holdings_snapshot.extraction_mode == "direct"
    assert result.holdings_snapshot.value is not None
    assert result.holdings_snapshot.value["top_holdings_status"] == "direct_all_stock_details"
    assert result.holdings_snapshot.value["top_holdings_source"] == "all_stock_investment_details"
    assert len(result.holdings_snapshot.value["top_holdings"]) == 10
    assert result.holdings_snapshot.value["top_holdings"][9]["股票名称"] == "股票10"
    assert {anchor.row_locator for anchor in result.holdings_snapshot.anchors} == {
        "all_stock_investment_details",
        "industry_distribution",
    }


def test_extract_holdings_share_change_keeps_industry_only_visible_but_stock_missing() -> None:
    """验证只有行业分布时不伪造股票持仓明细。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当行业分布被误计为股票明细时抛出。
    """

    report = _build_report((_industry_distribution_table(), _share_change_table()))

    result = extract_holdings_share_change(report)

    assert result.holdings_snapshot.extraction_mode == "direct"
    assert result.holdings_snapshot.value is not None
    assert result.holdings_snapshot.value["top_holdings"] is None
    assert result.holdings_snapshot.value["top_holdings_status"] == "missing"
    assert result.holdings_snapshot.value["top_holdings_source"] == "none"
    assert result.holdings_snapshot.value["industry_distribution_status"] == "direct"
    assert result.holdings_snapshot.note is not None


def test_extract_holdings_share_change_selects_a_class_from_adjacent_split_tables() -> None:
    """验证 §10 相邻拆表可在 §2 A/C 证据确认后选择 A 类。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 A 类拆表未抽取时抛出。
    """

    raw_text = "§2 基金简介\n安信企业价值优选混合A 004393 安信企业价值优选混合C 020964\n§8 投资组合报告\n§10 基金份额变动\n"
    report = _build_report(
        (
            _section_two_share_class_table(),
            _split_share_header_table(),
            _split_share_data_table(),
        ),
        fund_code="004393",
        raw_text=raw_text,
        include_section_two=True,
    )

    result = extract_holdings_share_change(report)

    assert result.share_change.extraction_mode == "direct"
    assert result.share_change.value == {
        "beginning_share": "27,666,410.41",
        "ending_share": "149,565,740.00",
        "net_change": "121,899,329.59",
        "share_class_column": "安信企业价值优选混合A",
        "share_class_selection_reason": "section_2_share_class_evidence",
    }
    assert result.share_change.anchors[0].page_number == 64


def test_extract_holdings_share_change_fails_closed_without_section_two_class_evidence() -> None:
    """验证缺少 §2 A/C 证据时拆表不默认选择 A 类。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当缺证据仍选择 A 类时抛出。
    """

    report = _build_report(
        (
            _split_share_header_table(),
            _split_share_data_table(),
        ),
        fund_code="004393",
    )

    result = extract_holdings_share_change(report)

    assert result.share_change.extraction_mode == "missing"
    assert result.share_change.value is None


def test_extract_holdings_share_change_fails_closed_for_unbounded_split_tables() -> None:
    """验证相邻列表中的非物理相邻 A/C 拆表不会被合并。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当非 §10/page-order bounded 拆表被合并时抛出。
    """

    raw_text = "§2 基金简介\n安信企业价值优选混合A 004393 安信企业价值优选混合C 020964\n§8 投资组合报告\n§10 基金份额变动\n"
    report = _build_report(
        (
            _section_two_share_class_table(),
            _unrelated_adjacent_header_like_table(),
            _split_share_data_table(),
        ),
        fund_code="004393",
        raw_text=raw_text,
        include_section_two=True,
    )

    result = extract_holdings_share_change(report)

    assert result.share_change.extraction_mode == "missing"
    assert result.share_change.value is None


def test_extract_holdings_share_change_fails_closed_for_split_column_count_mismatch() -> None:
    """验证拆表 A/C 表头数量与数据值列数量不一致时 fail closed。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当不确定列映射被合并时抛出。
    """

    raw_text = "§2 基金简介\n安信企业价值优选混合A 004393 安信企业价值优选混合C 020964\n§8 投资组合报告\n§10 基金份额变动\n"
    report = _build_report(
        (
            _section_two_share_class_table(),
            _split_share_header_table(),
            _mismatched_split_share_data_table(),
        ),
        fund_code="004393",
        raw_text=raw_text,
        include_section_two=True,
    )

    result = extract_holdings_share_change(report)

    assert result.share_change.extraction_mode == "missing"
    assert result.share_change.value is None


def test_extract_holdings_share_change_fails_closed_for_ambiguous_split_tables() -> None:
    """验证相邻多个拆表候选不会跨表头静默取值。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当非相邻拆表被误合并时抛出。
    """

    report = _build_report(
        (
            _split_share_header_table(),
            _industry_distribution_table(),
            _split_share_data_table(),
        ),
        fund_code="004393",
    )

    result = extract_holdings_share_change(report)

    assert result.share_change.extraction_mode == "missing"
    assert result.share_change.value is None


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


def test_extract_holdings_share_change_rejects_single_other_code_header() -> None:
    """验证单值列表头属于其他基金代码时不按当前基金抽取。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当非当前基金代码单值列被接受时抛出。
    """

    report = _build_report((_single_share_change_table_with_other_code_header(),))

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
