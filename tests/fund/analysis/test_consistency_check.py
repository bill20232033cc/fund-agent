"""言行一致性检验测试。"""

from __future__ import annotations

from fund_agent.fund.analysis import check_consistency
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


def _field(value: dict[str, object] | None, section_id: str, row_locator: str) -> ExtractedField[dict[str, object]]:
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


def _product_profile(
    *,
    style_positioning: str = "均衡偏价值，重视安全边际。",
) -> ExtractedField[dict[str, object]]:
    """构造 §2 产品画像字段。

    Args:
        style_positioning: 风格定位。

    Returns:
        产品画像字段。

    Raises:
        无显式抛出。
    """

    return _field(
        {
            "investment_objective": "追求长期稳健增值。",
            "style_positioning": style_positioning,
            "investment_strategy": "均衡配置。",
        },
        "§2",
        "product_profile",
    )


def _manager_strategy(
    *,
    strategy_summary: str = "坚持长期持有，均衡配置，关注消费和医药行业。",
) -> ExtractedField[dict[str, object]]:
    """构造 §4 策略文本字段。

    Args:
        strategy_summary: 策略摘要。

    Returns:
        管理人策略文本字段。

    Raises:
        无显式抛出。
    """

    return _field(
        {
            "strategy_summary": strategy_summary,
            "market_outlook": "继续关注消费和医药。",
        },
        "§4",
        "manager_strategy_text",
    )


def _holdings_snapshot(industry_rows: list[dict[str, str]] | None) -> ExtractedField[dict[str, object]]:
    """构造 §8 持仓快照字段。

    Args:
        industry_rows: 行业分布行。

    Returns:
        持仓快照字段。

    Raises:
        无显式抛出。
    """

    return _field(
        {
            "top_holdings": [{"股票名称": "测试股票", "占基金资产净值比例": "8.00%"}],
            "industry_distribution": industry_rows,
            "industry_distribution_status": "direct" if industry_rows is not None else "missing",
        },
        "§8",
        "holdings_snapshot",
    )


def _turnover_rate(value: str | None) -> ExtractedField[dict[str, object]]:
    """构造 §8 换手率字段。

    Args:
        value: 换手率文本。

    Returns:
        换手率字段。

    Raises:
        无显式抛出。
    """

    return _field(
        None if value is None else {"turnover_rate": value, "turnover_basis": "fixture"},
        "§8",
        "turnover_rate",
    )


def _dimension_statuses(result_dimensions: tuple[object, ...]) -> dict[str, str]:
    """把维度结果转换为状态字典。

    Args:
        result_dimensions: 维度结果元组。

    Returns:
        维度名到状态的映射。

    Raises:
        无显式抛出。
    """

    return {
        getattr(dimension, "dimension"): getattr(dimension, "status")
        for dimension in result_dimensions
    }


def test_check_consistency_outputs_four_green_dimensions_when_evidence_matches() -> None:
    """验证 4 维度证据匹配时输出整体一致。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当一致性判断错误时抛出。
    """

    result = check_consistency(
        product_profile=_product_profile(),
        manager_strategy_text=_manager_strategy(),
        holdings_snapshot=_holdings_snapshot([{"行业": "消费", "占比": "45.00%"}]),
        turnover_rate=_turnover_rate("80%"),
        actual_style="价值风格",
        actual_equity_position="60%",
    )

    assert result.overall_status == "aligned"
    assert result.overall_signal == "green"
    assert _dimension_statuses(result.dimensions) == {
        "investment_style": "aligned",
        "industry_preference": "aligned",
        "position_management": "aligned",
        "turnover_level": "aligned",
    }


def test_check_consistency_reports_red_for_style_and_industry_mismatch() -> None:
    """验证风格和行业证据不匹配时输出不一致。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当不一致信号未触发时抛出。
    """

    result = check_consistency(
        product_profile=_product_profile(style_positioning="价值风格。"),
        manager_strategy_text=_manager_strategy(strategy_summary="坚持长期持有，关注消费行业。"),
        holdings_snapshot=_holdings_snapshot([{"行业": "科技", "占比": "60.00%"}]),
        turnover_rate=_turnover_rate("80%"),
        actual_style="成长风格",
        actual_equity_position="60%",
    )

    statuses = _dimension_statuses(result.dimensions)
    assert result.overall_status == "misaligned"
    assert result.overall_signal == "red"
    assert statuses["investment_style"] == "misaligned"
    assert statuses["industry_preference"] == "misaligned"


def test_check_consistency_requires_explicit_actual_style_and_position() -> None:
    """验证实际风格和股票仓位缺失时不使用默认假设。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当缺失实际证据仍输出判断时抛出。
    """

    result = check_consistency(
        product_profile=_product_profile(),
        manager_strategy_text=_manager_strategy(),
        holdings_snapshot=_holdings_snapshot([{"行业": "消费", "占比": "45.00%"}]),
        turnover_rate=_turnover_rate("80%"),
    )

    statuses = _dimension_statuses(result.dimensions)
    assert statuses["investment_style"] == "insufficient_data"
    assert statuses["position_management"] == "insufficient_data"
    assert result.overall_status == "insufficient_data"


def test_check_consistency_detects_high_turnover_against_long_term_claim() -> None:
    """验证长期持有宣称与高换手率冲突时输出红灯。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当换手冲突未触发时抛出。
    """

    result = check_consistency(
        product_profile=_product_profile(),
        manager_strategy_text=_manager_strategy(strategy_summary="坚持长期持有，均衡配置。"),
        holdings_snapshot=_holdings_snapshot([{"行业": "消费", "占比": "45.00%"}]),
        turnover_rate=_turnover_rate("260%"),
        actual_style="价值风格",
        actual_equity_position="60%",
    )

    turnover_dimension = next(
        dimension for dimension in result.dimensions if dimension.dimension == "turnover_level"
    )
    assert turnover_dimension.status == "misaligned"
    assert turnover_dimension.signal == "red"


def test_check_consistency_reports_insufficient_when_industry_distribution_missing() -> None:
    """验证行业分布缺失时行业维度返回证据不足。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当行业分布缺失仍强行判断时抛出。
    """

    result = check_consistency(
        product_profile=_product_profile(),
        manager_strategy_text=_manager_strategy(strategy_summary="关注消费行业，长期持有。"),
        holdings_snapshot=_holdings_snapshot(None),
        turnover_rate=_turnover_rate("80%"),
        actual_style="价值风格",
        actual_equity_position="60%",
    )

    industry_dimension = next(
        dimension for dimension in result.dimensions if dimension.dimension == "industry_preference"
    )
    assert industry_dimension.status == "insufficient_data"
    assert "缺少 §4 行业偏好宣称或 §8 行业分布" in industry_dimension.reason
