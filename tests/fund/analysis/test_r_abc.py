"""R=A+B-C 收益归因测试。"""

from __future__ import annotations

from decimal import Decimal

from fund_agent.fund.analysis import (
    RabcInput,
    calculate_r_abc,
    calculate_r_abc_from_bundle,
    calculate_r_abc_series,
)
from fund_agent.fund.data.nav_data import NavDataResult
from fund_agent.fund.data_extractor import StructuredFundDataBundle
from fund_agent.fund.extractors.models import (
    EvidenceAnchor,
    ExtractedField,
    IndexProfileValue,
    TrackingErrorValue,
)


def _anchor(section_id: str, row_locator: str) -> EvidenceAnchor:
    """构造测试用证据锚点。

    Args:
        section_id: 年报章节编号。
        row_locator: 行定位说明。

    Returns:
        测试证据锚点。

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
    mode: str = "direct",
) -> ExtractedField[dict[str, object]]:
    """构造测试用抽取字段。

    Args:
        value: 字段值。
        section_id: 年报章节编号。
        row_locator: 行定位说明。
        mode: 抽取模式。

    Returns:
        测试抽取字段。

    Raises:
        无显式抛出。
    """

    anchors = () if value is None else (_anchor(section_id, row_locator),)
    return ExtractedField(
        value=value,
        anchors=anchors,
        extraction_mode=mode,  # type: ignore[arg-type]
        note=None,
    )


def _bundle(
    *,
    nav_benchmark_value: dict[str, object] | None = None,
    fee_value: dict[str, object] | None = None,
    turnover_value: dict[str, object] | None = None,
) -> StructuredFundDataBundle:
    """构造最小 P1 结构化数据包。

    Args:
        nav_benchmark_value: 净值增长率与基准收益率。
        fee_value: 费率字段。
        turnover_value: 换手率字段。

    Returns:
        测试数据包。

    Raises:
        无显式抛出。
    """

    placeholder = _field({}, section_id="§1", row_locator="placeholder")
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
        report_year=2024,
        basic_identity=placeholder,
        product_profile=placeholder,
        benchmark=placeholder,
        index_profile=missing_index_profile,
        fee_schedule=_field(fee_value, section_id="§2", row_locator="fee_schedule")
        if fee_value is not None
        else _field(None, section_id="§2", row_locator="fee_schedule", mode="missing"),
        turnover_rate=_field(turnover_value, section_id="§8", row_locator="turnover_rate")
        if turnover_value is not None
        else _field(None, section_id="§8", row_locator="turnover_rate", mode="missing"),
        nav_benchmark_performance=_field(
            nav_benchmark_value,
            section_id="§3",
            row_locator="nav_benchmark_performance",
        )
        if nav_benchmark_value is not None
        else _field(None, section_id="§3", row_locator="nav_benchmark_performance", mode="missing"),
        investor_return=placeholder,
        tracking_error=missing_tracking_error,
        share_change=placeholder,
        manager_alignment=placeholder,
        manager_strategy_text=placeholder,
        holdings_snapshot=placeholder,
        holder_structure=placeholder,
        nav_data=NavDataResult(fund_code="110011", records=(), source="fixture", cached=False),
    )


def test_calculate_r_abc_matches_manual_formula() -> None:
    """验证 R=A+B-C 与手工计算一致，误差小于 0.01%。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当归因公式不闭合时抛出。
    """

    result = calculate_r_abc(
        RabcInput(
            period="1y",
            nav_growth_rate=Decimal("0.1234"),
            benchmark_return_rate=Decimal("0.1001"),
            equity_position=Decimal("0.80"),
            management_fee_rate=Decimal("0.012"),
            custody_fee_rate=Decimal("0.002"),
            turnover_rate=Decimal("1.2345"),
        )
    )

    assert result.status == "computed"
    assert result.total_return_r == Decimal("0.1234")
    assert result.beta_return_b == Decimal("0.080080")
    assert result.alpha_return_a == Decimal("0.043320")
    assert result.turnover_cost == Decimal("0.0037035")
    assert result.explicit_cost_c == Decimal("0.0177035")
    assert result.net_excess_return == Decimal("0.0256165")


def test_calculate_r_abc_series_supports_1y_3y_5y_periods() -> None:
    """验证归因模块支持 1/3/5 年多周期计算。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当多周期输出顺序或数量错误时抛出。
    """

    results = calculate_r_abc_series(
        (
            RabcInput(
                period="1y",
                nav_growth_rate=Decimal("0.10"),
                benchmark_return_rate=Decimal("0.08"),
                equity_position=Decimal("0.80"),
                management_fee_rate=Decimal("0.012"),
                custody_fee_rate=Decimal("0.002"),
                turnover_rate=Decimal("1.00"),
            ),
            RabcInput(
                period="3y",
                nav_growth_rate=Decimal("0.30"),
                benchmark_return_rate=Decimal("0.21"),
                equity_position=Decimal("0.75"),
                management_fee_rate=Decimal("0.036"),
                custody_fee_rate=Decimal("0.006"),
                turnover_rate=Decimal("2.10"),
            ),
            RabcInput(
                period="5y",
                nav_growth_rate=Decimal("0.50"),
                benchmark_return_rate=Decimal("0.35"),
                equity_position=Decimal("0.70"),
                management_fee_rate=Decimal("0.060"),
                custody_fee_rate=Decimal("0.010"),
                turnover_rate=Decimal("3.50"),
            ),
        )
    )

    assert tuple(result.period for result in results) == ("1y", "3y", "5y")
    assert all(result.status == "computed" for result in results)
    assert results[0].net_excess_return == Decimal("0.01900")


def test_calculate_r_abc_from_bundle_parses_p1_fields_and_keeps_anchors() -> None:
    """验证 P1 数据包适配能解析百分比字段并保留证据锚点。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当字段解析或证据传递错误时抛出。
    """

    result = calculate_r_abc_from_bundle(
        _bundle(
            nav_benchmark_value={
                "nav_growth_rate": "12.34%",
                "benchmark_return_rate": "10.01%",
            },
            fee_value={"management_fee": "1.20%/年", "custody_fee": "0.20%/年"},
            turnover_value={"turnover_rate": "123.45%"},
        ),
        equity_position="80%",
    )

    assert result.status == "computed"
    assert result.period == "2024"
    assert result.net_excess_return == Decimal("0.0256165")
    assert {anchor.section_id for anchor in result.anchors} == {"§2", "§3", "§8"}


def test_calculate_r_abc_from_bundle_requires_explicit_equity_position() -> None:
    """验证股票仓位缺失时不静默假设，直接返回 missing。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当缺失股票仓位仍继续计算时抛出。
    """

    result = calculate_r_abc_from_bundle(
        _bundle(
            nav_benchmark_value={
                "nav_growth_rate": "12.34%",
                "benchmark_return_rate": "10.01%",
            },
            fee_value={"management_fee": "1.20%", "custody_fee": "0.20%"},
            turnover_value={"turnover_rate": "123.45%"},
        )
    )

    assert result.status == "missing"
    assert result.net_excess_return is None
    assert result.note is not None
    assert "缺少显式股票仓位" in result.note


def test_calculate_r_abc_from_bundle_reports_missing_source_fields() -> None:
    """验证关键字段缺失时返回可审计的 missing 原因。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当缺失原因不完整时抛出。
    """

    result = calculate_r_abc_from_bundle(_bundle(), equity_position="80%")

    assert result.status == "missing"
    assert result.note is not None
    assert "缺少 §3 净值增长率/业绩比较基准收益率" in result.note
    assert "缺少 §2 管理费/托管费" in result.note
    assert "缺少 §8 换手率" in result.note


def test_calculate_r_abc_from_bundle_reports_partial_field_missing() -> None:
    """验证 direct 字段中的子值缺失时返回明确缺失原因。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当子字段缺失原因不明确时抛出。
    """

    result = calculate_r_abc_from_bundle(
        _bundle(
            nav_benchmark_value={
                "nav_growth_rate": "12.34%",
                "benchmark_return_rate": "10.01%",
            },
            fee_value={"management_fee": "1.20%", "custody_fee": None},
            turnover_value={"turnover_rate": "123.45%"},
        ),
        equity_position=80,
    )

    assert result.status == "missing"
    assert result.note is not None
    assert "缺少 §2 托管费" in result.note
