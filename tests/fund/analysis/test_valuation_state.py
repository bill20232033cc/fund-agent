"""估值状态自动解析测试。"""

from __future__ import annotations

from decimal import Decimal

import pytest

from fund_agent.fund.analysis import (
    ValuationIndexTarget,
    build_explicit_valuation_resolution,
    build_thermometer_valuation_resolution,
    build_unavailable_valuation_resolution,
    resolve_valuation_index_target,
)
from fund_agent.fund.data.thermometer_types import ThermometerReading
from fund_agent.fund.extractors.models import EvidenceAnchor, ExtractedField, IndexProfileValue


def _anchor() -> EvidenceAnchor:
    """构造基准证据锚点。

    Args:
        无。

    Returns:
        年报基准证据锚点。

    Raises:
        无显式抛出。
    """

    return EvidenceAnchor(
        source_kind="annual_report",
        document_year=2024,
        section_id="§2",
        page_number=None,
        table_id=None,
        row_locator="benchmark",
        note="fixture benchmark",
    )


def _index_profile(
    *,
    benchmark_text: str | None = None,
    benchmark_index_name: str | None = None,
    benchmark_index_code: str | None = None,
    components: tuple[str, ...] = (),
) -> ExtractedField[IndexProfileValue]:
    """构造指数画像字段。

    Args:
        benchmark_text: 基准全文。
        benchmark_index_name: 单一指数名称。
        benchmark_index_code: 单一指数代码。
        components: 复合基准成分。

    Returns:
        指数画像抽取字段。

    Raises:
        无显式抛出。
    """

    return ExtractedField(
        value=IndexProfileValue(
            benchmark_text=benchmark_text,
            benchmark_identity_status="identified" if benchmark_text else "missing",
            benchmark_index_name=benchmark_index_name,
            benchmark_index_code=benchmark_index_code,
            benchmark_component_text=components,
            methodology_availability="missing",
            methodology_summary=None,
            methodology_source_title=None,
            constituents_availability="missing",
            constituents_summary=None,
            constituents_as_of_date=None,
            source_tier="benchmark_context",
            missing_reasons=(),
        ),
        anchors=(_anchor(),),
        extraction_mode="derived",
        note=None,
    )


def _benchmark(text: str | None) -> ExtractedField[dict[str, object]]:
    """构造业绩基准字段。

    Args:
        text: 基准文本。

    Returns:
        基准抽取字段。

    Raises:
        无显式抛出。
    """

    return ExtractedField(
        value={} if text is None else {"benchmark_text": text},
        anchors=() if text is None else (_anchor(),),
        extraction_mode="missing" if text is None else "direct",
        note=None,
    )


@pytest.mark.parametrize(
    ("fund_type", "text", "expected_code"),
    (
        ("index_fund", "沪深300指数收益率", "000300"),
        ("enhanced_index", "中证500指数收益率", "000905"),
        ("index_fund", "沪深300指数收益率*80% + 中证全债指数收益率*20%", "000300"),
    ),
)
def test_resolve_valuation_index_target_maps_supported_exact_identity(
    fund_type: str,
    text: str,
    expected_code: str,
) -> None:
    """验证支持基金类型和 exact identity 基准映射到指定指数。

    Args:
        fund_type: 基金类型。
        text: 基准文本。
        expected_code: 期望指数代码。

    Returns:
        无返回值。

    Raises:
        AssertionError: 映射不符合 P19-S3 scope 时抛出。
    """

    target = resolve_valuation_index_target(
        fund_type=fund_type,  # type: ignore[arg-type]
        index_profile=_index_profile(benchmark_text=text),
        benchmark=_benchmark(text),
    )

    assert target.status == "mapped"
    assert target.index_code == expected_code


@pytest.mark.parametrize("fund_type", ("active_fund", "bond_fund", "qdii_fund", "fof_fund"))
def test_resolve_valuation_index_target_rejects_unsupported_fund_types(fund_type: str) -> None:
    """验证非指数/指增基金不调用温度计。

    Args:
        fund_type: 基金类型。

    Returns:
        无返回值。

    Raises:
        AssertionError: 不支持基金类型被错误映射时抛出。
    """

    target = resolve_valuation_index_target(
        fund_type=fund_type,  # type: ignore[arg-type]
        index_profile=_index_profile(benchmark_text="沪深300指数收益率"),
        benchmark=_benchmark("沪深300指数收益率"),
    )

    assert target.status == "unsupported_fund_type"
    assert target.index_code is None


@pytest.mark.parametrize(
    "text",
    (
        "沪深300价值指数收益率",
        "沪深300成长指数收益率",
        "沪深300红利低波动指数收益率",
        "沪深300等权重指数收益率",
        "中证500质量成长指数收益率",
        "中证500低波动指数收益率",
        "中证500等权重指数收益率",
        "中证500医药卫生指数收益率",
    ),
)
def test_resolve_valuation_index_target_rejects_derived_indices(text: str) -> None:
    """验证派生、策略、行业指数不会被 substring alias 误映射。

    Args:
        text: 派生指数基准文本。

    Returns:
        无返回值。

    Raises:
        AssertionError: 派生指数被错误映射时抛出。
    """

    target = resolve_valuation_index_target(
        fund_type="index_fund",
        index_profile=_index_profile(benchmark_text=text),
        benchmark=_benchmark(text),
    )

    assert target.status == "unsupported_index"
    assert target.index_code is None


def test_resolve_valuation_index_target_marks_multiple_supported_indices_ambiguous() -> None:
    """验证多个支持权益指数混合时 fail-closed。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 多指数混合被错误选择单一温度计时抛出。
    """

    text = "沪深300指数收益率*50% + 中证500指数收益率*50%"
    target = resolve_valuation_index_target(
        fund_type="index_fund",
        index_profile=_index_profile(benchmark_text=text),
        benchmark=_benchmark(text),
    )

    assert target.status == "ambiguous_benchmark"
    assert target.index_code is None


def test_resolve_valuation_index_target_uses_supported_code_when_present() -> None:
    """验证指数画像已有支持代码时优先映射。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 支持代码未被优先使用时抛出。
    """

    target = resolve_valuation_index_target(
        fund_type="index_fund",
        index_profile=_index_profile(benchmark_index_code="000300"),
        benchmark=_benchmark(None),
    )

    assert target.status == "mapped"
    assert target.index_code == "000300"


@pytest.mark.parametrize(
    ("index_code", "text"),
    (
        ("000300", "沪深300价值指数收益率"),
        ("000905", "中证500质量成长指数收益率"),
    ),
)
def test_resolve_valuation_index_target_rejects_supported_code_text_conflicts(
    index_code: str,
    text: str,
) -> None:
    """验证支持指数代码不能绕过同源派生指数文本冲突。

    Args:
        index_code: benchmark_index_code 候选。
        text: 同源基准文本。

    Returns:
        无返回值。

    Raises:
        AssertionError: 派生指数文本被代码优先路径误映射时抛出。
    """

    target = resolve_valuation_index_target(
        fund_type="index_fund",
        index_profile=_index_profile(
            benchmark_text=text,
            benchmark_index_code=index_code,
            components=(text,),
        ),
        benchmark=_benchmark(text),
    )

    assert target.status == "unsupported_index"
    assert target.index_code is None


def test_build_resolution_constructors_preserve_structured_truth() -> None:
    """验证显式、不可用、温度计 resolution 字段完整。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: resolution 未保留必要结构化字段时抛出。
    """

    explicit = build_explicit_valuation_resolution("unavailable")
    assert explicit.source == "explicit_user_input"
    assert explicit.state == "unavailable"
    assert explicit.anchors[0].source_kind == "derived"

    unavailable = build_unavailable_valuation_resolution(
        ValuationIndexTarget(
            status="unsupported_index",
            index_code=None,
            index_name=None,
            reason="unsupported fixture",
            anchors=(_anchor(),),
        )
    )
    assert unavailable.source == "unavailable_mapping"
    assert unavailable.state == "unavailable"
    assert unavailable.unavailable_reason == "unsupported fixture"

    reading = ThermometerReading(
        index_code="000300",
        index_name="沪深300",
        temperature=Decimal("20.00"),
        pe_percentile=Decimal("10.00"),
        pb_percentile=Decimal("30.00"),
        valuation_state_candidate="low",
        data_date="2024-12-31",
        lookback_start="2014-12-31",
        lookback_end="2024-12-31",
        source="akshare_index_value_hist_funddb",
        cached=False,
        stale=False,
        unavailable=False,
        unavailable_reason=None,
        fetched_at="2025-01-01T00:00:00Z",
    )
    resolution = build_thermometer_valuation_resolution(reading)

    assert resolution.source == "self_owned_thermometer"
    assert resolution.state == "low"
    assert resolution.disclaimer_required
    assert resolution.anchors[0].source_kind == "external_api"
