"""`§4/§8/§9` 管理人与持有人 extractor 测试。"""

from __future__ import annotations

from pathlib import Path

from fund_agent.fund.documents.models import DocumentKey, ParsedAnnualReport, ParsedTable, ReportSection
from fund_agent.fund.extractors.manager_ownership import extract_manager_ownership

_FIXTURE_DIR = Path(__file__).resolve().parents[2] / "fixtures" / "fund" / "extractors" / "manager_ownership"


def _load_fixture_text(filename: str) -> str:
    """读取 `§4/§8/§9` 测试夹具文本。

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
    """把最小 `§4/§8/§9` 文本夹具构造成 `ParsedAnnualReport`。

    Args:
        filename: 夹具文件名。
        fund_code: 基金代码。

    Returns:
        构造后的年报对象。

    Raises:
        ValueError: 夹具缺少 `§4/§8/§9` 时抛出。
    """

    raw_text = _load_fixture_text(filename)
    section_four_start = raw_text.index("§4 管理人报告")
    section_eight_start = raw_text.index("§8 投资组合报告")
    section_nine_start = raw_text.index("§9 基金份额持有人信息")
    return ParsedAnnualReport(
        key=DocumentKey(fund_code=fund_code, year=2024),
        raw_text=raw_text,
        sections={
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
        tables=(),
    )


def _build_report_from_text_and_tables(raw_text: str, tables: tuple[ParsedTable, ...]) -> ParsedAnnualReport:
    """把最小文本和表格构造成 `ParsedAnnualReport`。

    Args:
        raw_text: 年报正文。
        tables: 表格元组。

    Returns:
        构造后的年报对象。

    Raises:
        ValueError: 正文缺少必需章节时抛出。
    """

    section_four_start = raw_text.index("§4 管理人报告")
    section_eight_start = raw_text.index("§8 投资组合报告")
    section_nine_start = raw_text.index("§9 基金份额持有人信息")
    return ParsedAnnualReport(
        key=DocumentKey(fund_code="004393", year=2024),
        raw_text=raw_text,
        sections={
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
        tables=tables,
    )


def test_extract_manager_ownership_outputs_direct_fields_with_anchors() -> None:
    """验证完整披露时输出四类字段，并带证据锚点。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当字段或锚点缺失时抛出。
    """

    report = _build_report_from_fixture("manager_ownership_complete.txt", "110011")

    result = extract_manager_ownership(report)

    assert result.manager_strategy_text.extraction_mode == "direct"
    assert result.manager_strategy_text.value == {
        "strategy_summary": "本基金坚持自下而上选择具备长期竞争力的公司。",
        "style_positioning": "均衡偏价值，重视安全边际。",
        "market_outlook": "将继续关注企业盈利质量和估值匹配度。",
    }
    assert {anchor.section_id for anchor in result.manager_strategy_text.anchors} == {"§4"}
    assert result.turnover_rate.extraction_mode == "direct"
    assert result.turnover_rate.value == {
        "turnover_rate": "238.45%",
        "turnover_basis": "买卖股票成交总额除以期初期末平均股票资产。",
    }
    assert {anchor.row_locator for anchor in result.turnover_rate.anchors} == {"turnover_rate", "turnover_basis"}
    assert {anchor.section_id for anchor in result.turnover_rate.anchors} == {"§8"}
    assert all(anchor.source_kind == "annual_report" for anchor in result.turnover_rate.anchors)
    assert all(anchor.document_year == 2024 for anchor in result.turnover_rate.anchors)
    assert all(anchor.note is not None for anchor in result.turnover_rate.anchors)
    assert result.manager_alignment.extraction_mode == "direct"
    assert result.manager_alignment.value == {
        "manager_holding": "12.34万份",
        "employee_holding": "45.67万份",
        "judgment": None,
    }
    assert {anchor.section_id for anchor in result.manager_alignment.anchors} == {"§9"}
    assert result.holder_structure.extraction_mode == "direct"
    assert result.holder_structure.value == {
        "institutional_holder": "23.45%",
        "individual_holder": "76.55%",
    }
    assert {anchor.section_id for anchor in result.holder_structure.anchors} == {"§9"}


def test_extract_manager_ownership_outputs_strategy_text_from_numbered_headings() -> None:
    """验证 `§4` 编号标题后的策略与展望自然段可被抽取。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当标题块抽取失败时抛出。
    """

    raw_text = "\n".join(
        (
            "§4 管理人报告",
            "4.4.1 报告期内基金投资策略和运作分析",
            "本基金坚持从企业价值出发，配置经营质量较高的公司。",
            "报告期内组合保持主动选股思路。",
            "14.68%，结束了连续3年的下跌态势。",
            "4.5 管理人对宏观经济、证券市场及行业走势的简要展望",
            "未来将继续关注企业盈利质量与估值匹配度。",
            "§8 投资组合报告",
            "§9 基金份额持有人信息",
        )
    )
    report = _build_report_from_text_and_tables(raw_text, ())

    result = extract_manager_ownership(report)

    assert result.manager_strategy_text.extraction_mode == "direct"
    assert result.manager_strategy_text.value == {
        "strategy_summary": (
            "本基金坚持从企业价值出发，配置经营质量较高的公司。 报告期内组合保持主动选股思路。 "
            "14.68%，结束了连续3年的下跌态势。"
        ),
        "style_positioning": None,
        "market_outlook": "未来将继续关注企业盈利质量与估值匹配度。",
    }
    assert {anchor.row_locator for anchor in result.manager_strategy_text.anchors} == {
        "strategy_summary",
        "market_outlook",
    }


def test_extract_manager_ownership_outputs_alignment_and_holder_structure_from_tables() -> None:
    """验证 `§9` 持有人表格可抽取利益一致性和持有人结构原始披露。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当表格抽取或 anchor 不正确时抛出。
    """

    raw_text = "§4 管理人报告\n§8 投资组合报告\n§9 基金份额持有人信息\n"
    employee_table = ParsedTable(
        page_number=63,
        table_index=0,
        headers=("项目", "持有份额总数（份）", "占基金总份额比例"),
        rows=(("基金管理人所有从业人员持有本基金", "10,000.00", "0.01%"),),
    )
    manager_table = ParsedTable(
        page_number=63,
        table_index=1,
        headers=("项目", "持有基金份额总量的数量区间（万份）"),
        rows=(("本基金基金经理持有本开放式基金", "0~10"),),
    )
    holder_table = ParsedTable(
        page_number=63,
        table_index=2,
        headers=(
            "",
            "（户）",
            "",
            "持有份额",
            "占总份\n额比例\n（%）",
            "持有份额",
            "占总\n份额\n比例\n（%）",
        ),
        rows=(
            (
                "安信企业价值\n优选混合A",
                "1,583",
                "94,482.46",
                "129,320,194.75",
                "86.46",
                "20,245,545.25",
                "13.54",
            ),
        ),
    )
    holder_header_table = ParsedTable(
        page_number=62,
        table_index=1,
        headers=("份额级别", "持有人\n户数", "户均持有的\n基金份额", "持有人结构", ""),
        rows=(("", "", "", "机构投资者", "个人投资者"),),
    )
    report = _build_report_from_text_and_tables(
        raw_text,
        (employee_table, manager_table, holder_header_table, holder_table),
    )

    result = extract_manager_ownership(report)

    assert result.manager_alignment.extraction_mode == "direct"
    assert result.manager_alignment.value is not None
    assert "0~10" in result.manager_alignment.value["manager_holding"]
    assert "10,000.00" in result.manager_alignment.value["employee_holding"]
    assert {anchor.table_id for anchor in result.manager_alignment.anchors} == {
        "page-63-table-0",
        "page-63-table-1",
    }
    assert result.holder_structure.extraction_mode == "direct"
    assert result.holder_structure.value == {
        "institutional_holder": "86.46",
        "individual_holder": "13.54",
    }
    assert {anchor.table_id for anchor in result.holder_structure.anchors} == {"page-63-table-2"}


def test_extract_manager_ownership_reads_adjacent_ratio_without_share_column() -> None:
    """验证跨页续表只有比例相邻列时仍能抽取个人持有人比例。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当相邻比例列 fallback 失败时抛出。
    """

    raw_text = "§4 管理人报告\n§8 投资组合报告\n§9 基金份额持有人信息\n"
    holder_header_table = ParsedTable(
        page_number=62,
        table_index=1,
        headers=("份额级别", "持有人\n户数", "户均持有的\n基金份额", "持有人结构", ""),
        rows=(("", "", "", "机构投资者", "个人投资者"),),
    )
    holder_table = ParsedTable(
        page_number=63,
        table_index=2,
        headers=("", "持有份额", "比例", "比例"),
        rows=(("安信企业价值\n优选混合A", "129,320,194.75", "86.46", "13.54"),),
    )
    report = _build_report_from_text_and_tables(raw_text, (holder_header_table, holder_table))

    result = extract_manager_ownership(report)

    assert result.holder_structure.extraction_mode == "direct"
    assert result.holder_structure.value == {
        "institutional_holder": "86.46",
        "individual_holder": "13.54",
    }


def test_extract_manager_ownership_does_not_return_non_ratio_adjacent_cell() -> None:
    """验证跨页续表 fallback 不会把非比例文本静默当作个人比例。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当非比例候选列被误返回时抛出。
    """

    raw_text = "§4 管理人报告\n§8 投资组合报告\n§9 基金份额持有人信息\n"
    holder_header_table = ParsedTable(
        page_number=62,
        table_index=1,
        headers=("份额级别", "持有人\n户数", "户均持有的\n基金份额", "持有人结构", ""),
        rows=(("", "", "", "机构投资者", "个人投资者"),),
    )
    holder_table = ParsedTable(
        page_number=63,
        table_index=2,
        headers=("", "持有份额", "比例", "备注"),
        rows=(("安信企业价值\n优选混合A", "129,320,194.75", "86.46", "未披露"),),
    )
    report = _build_report_from_text_and_tables(raw_text, (holder_header_table, holder_table))

    result = extract_manager_ownership(report)

    assert result.holder_structure.extraction_mode == "direct"
    assert result.holder_structure.value == {
        "institutional_holder": "86.46",
        "individual_holder": None,
    }


def test_extract_manager_ownership_marks_missing_without_silent_blank() -> None:
    """验证未披露时四类字段显式返回 `missing`。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当缺失路径被静默处理时抛出。
    """

    report = _build_report_from_fixture("manager_ownership_missing.txt", "000171")

    result = extract_manager_ownership(report)

    assert result.manager_strategy_text.extraction_mode == "missing"
    assert result.manager_strategy_text.value is None
    assert result.manager_strategy_text.anchors == ()
    assert result.manager_strategy_text.note is not None
    assert result.turnover_rate.extraction_mode == "missing"
    assert result.turnover_rate.value is None
    assert result.turnover_rate.anchors == ()
    assert result.manager_alignment.extraction_mode == "missing"
    assert result.manager_alignment.value is None
    assert result.manager_alignment.anchors == ()
    assert result.holder_structure.extraction_mode == "missing"
    assert result.holder_structure.value is None
    assert result.holder_structure.anchors == ()


def test_extract_manager_ownership_keeps_partial_direct_values_without_judgment() -> None:
    """验证部分披露时保留原始值且不输出利益一致性判断。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当部分披露或判断边界不正确时抛出。
    """

    report = _build_report_from_fixture("manager_ownership_partial.txt", "510300")

    result = extract_manager_ownership(report)

    assert result.manager_strategy_text.extraction_mode == "direct"
    assert result.manager_strategy_text.value == {
        "strategy_summary": "本基金报告期内保持低估值行业配置。",
        "style_positioning": None,
        "market_outlook": None,
    }
    assert result.turnover_rate.extraction_mode == "direct"
    assert result.turnover_rate.value == {
        "turnover_rate": "88.00%",
        "turnover_basis": None,
    }
    assert result.manager_alignment.extraction_mode == "missing"
    assert result.holder_structure.extraction_mode == "direct"
    assert result.holder_structure.value == {
        "institutional_holder": "60.00%",
        "individual_holder": None,
    }
    assert result.holder_structure.anchors[0].row_locator == "institutional_holder"


def test_extract_manager_ownership_requires_numeric_turnover_anchor() -> None:
    """验证仅有换手率口径时不能把换手率标记为 `direct`。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当换手率数值缺失但仍被标记为直接披露时抛出。
    """

    report = _build_report_from_fixture("manager_ownership_turnover_basis_only.txt", "000123")

    result = extract_manager_ownership(report)

    assert result.turnover_rate.extraction_mode == "missing"
    assert result.turnover_rate.value == {
        "turnover_rate": None,
        "turnover_basis": "买卖股票成交总额除以期初期末平均股票资产。",
    }
    assert result.turnover_rate.anchors[0].row_locator == "turnover_basis"
    assert result.turnover_rate.note is not None
