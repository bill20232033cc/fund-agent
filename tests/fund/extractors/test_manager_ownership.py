"""`§4/§8/§9` 管理人与持有人 extractor 测试。"""

from __future__ import annotations

from pathlib import Path

from fund_agent.fund.documents.models import DocumentKey, ParsedAnnualReport, ReportSection
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
