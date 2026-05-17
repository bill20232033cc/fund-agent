"""投资者获得感分析测试。"""

from __future__ import annotations

from decimal import Decimal

from fund_agent.fund.analysis import (
    analyze_investor_experience,
    calculate_behavior_gap,
    judge_fund_flow,
)
from fund_agent.fund.extractors.models import EvidenceAnchor, ExtractedField


def _anchor(section_id: str, row_locator: str) -> EvidenceAnchor:
    """构造测试证据锚点。

    Args:
        section_id: 年报章节编号。
        row_locator: 行定位说明。

    Returns:
        证据锚点。

    Raises:
        无显式抛出。
    """

    return EvidenceAnchor(
        source_kind="annual_report",
        document_year=2024,
        section_id=section_id,
        page_number=None,
        table_id=None,
        row_locator=row_locator,
        note=f"{row_locator}: fixture",
    )


def _field(
    value: dict[str, object] | None,
    *,
    section_id: str,
    row_locator: str,
) -> ExtractedField[dict[str, object]]:
    """构造测试抽取字段。

    Args:
        value: 字段值。
        section_id: 年报章节编号。
        row_locator: 行定位说明。

    Returns:
        抽取字段。

    Raises:
        无显式抛出。
    """

    return ExtractedField(
        value=value,
        anchors=() if value is None else (_anchor(section_id, row_locator),),
        extraction_mode="missing" if value is None else "direct",
        note=None,
    )


def _nav_performance(value: str | None = "12.34%") -> ExtractedField[dict[str, object]]:
    """构造产品收益字段。

    Args:
        value: 净值增长率。

    Returns:
        产品收益字段。

    Raises:
        无显式抛出。
    """

    return _field(
        None if value is None else {"nav_growth_rate": value, "benchmark_return_rate": "10.01%"},
        section_id="§3",
        row_locator="nav_benchmark_performance",
    )


def _investor_return(value: str | None = "8.88%") -> ExtractedField[dict[str, object]]:
    """构造投资者收益字段。

    Args:
        value: 投资者收益率。

    Returns:
        投资者收益字段。

    Raises:
        无显式抛出。
    """

    return _field(
        None
        if value is None
        else {
            "investor_return_rate": value,
            "disclosure_status": "direct",
            "fallback_status": "not_needed",
        },
        section_id="§3",
        row_locator="investor_return",
    )


def _share_change(
    beginning: str = "1,000,000.00",
    ending: str = "1,200,000.00",
    net_change: str = "200,000.00",
) -> ExtractedField[dict[str, object]]:
    """构造份额变动字段。

    Args:
        beginning: 期初份额。
        ending: 期末份额。
        net_change: 净变动。

    Returns:
        份额变动字段。

    Raises:
        无显式抛出。
    """

    return _field(
        {
            "beginning_share": beginning,
            "ending_share": ending,
            "net_change": net_change,
        },
        section_id="§10",
        row_locator="share_change",
    )


def test_calculate_behavior_gap_uses_investor_return_minus_product_return() -> None:
    """验证行为损益等于投资者收益减产品收益。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当行为损益公式错误时抛出。
    """

    result = calculate_behavior_gap(
        nav_benchmark_performance=_nav_performance("12.34%"),
        investor_return=_investor_return("8.88%"),
    )

    assert result.status == "computed"
    assert result.product_return == Decimal("0.1234")
    assert result.investor_return == Decimal("0.0888")
    assert result.behavior_gap == Decimal("-0.0346")
    assert {anchor.section_id for anchor in result.anchors} == {"§3"}


def test_calculate_behavior_gap_returns_missing_without_investor_return() -> None:
    """验证投资者收益率缺失时不静默估算。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当缺失投资者收益率仍继续计算时抛出。
    """

    result = calculate_behavior_gap(
        nav_benchmark_performance=_nav_performance("12.34%"),
        investor_return=_investor_return(None),
    )

    assert result.status == "missing"
    assert result.behavior_gap is None
    assert result.note is not None
    assert "缺少 §3 投资者实际收益率" in result.note


def test_judge_fund_flow_detects_chasing_performance() -> None:
    """验证产品收益为正且份额净流入时识别追涨信号。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当追涨信号判断错误时抛出。
    """

    result = judge_fund_flow(
        share_change=_share_change(net_change="200,000.00"),
        product_return=Decimal("0.1234"),
    )

    assert result.signal == "chasing_performance"
    assert result.net_change_ratio == Decimal("0.2")
    assert "追涨信号" in result.reason


def test_judge_fund_flow_detects_bottom_fishing() -> None:
    """验证产品收益不佳但份额净流入时识别抄底信号。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当抄底信号判断错误时抛出。
    """

    result = judge_fund_flow(
        share_change=_share_change(net_change="200,000.00"),
        product_return=Decimal("-0.05"),
    )

    assert result.signal == "bottom_fishing"
    assert "抄底信号" in result.reason


def test_analyze_investor_experience_marks_negative_when_gap_is_large() -> None:
    """验证行为损益明显为负时获得感为 negative。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当获得感状态错误时抛出。
    """

    result = analyze_investor_experience(
        nav_benchmark_performance=_nav_performance("12.34%"),
        investor_return=_investor_return("8.88%"),
        share_change=_share_change(net_change="200,000.00"),
    )

    assert result.status == "negative"
    assert result.behavior_gap.behavior_gap == Decimal("-0.0346")
    assert result.fund_flow.signal == "chasing_performance"


def test_judge_fund_flow_reports_missing_for_partial_share_change() -> None:
    """验证份额变动子字段缺失时返回 missing。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当份额变动缺失仍继续判断时抛出。
    """

    result = judge_fund_flow(
        share_change=_field(
            {"beginning_share": "1,000,000.00", "ending_share": "1,200,000.00", "net_change": None},
            section_id="§10",
            row_locator="share_change",
        ),
        product_return=Decimal("0.1234"),
    )

    assert result.signal == "missing"
    assert result.net_change is None
    assert "net_change" in result.reason
