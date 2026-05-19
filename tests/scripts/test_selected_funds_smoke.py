"""有知有行精选基金池 smoke CLI 测试。"""

from __future__ import annotations

from pathlib import Path

from scripts import selected_funds_smoke


def test_load_selected_funds_and_validate_duplicate_code() -> None:
    """验证真实精选基金池 CSV 可读取，并暴露重复基金代码。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 CSV 记录数量、类别或重复代码不符合当前事实时抛出。
    """

    funds = selected_funds_smoke.load_selected_funds(Path("docs/code_20260519.csv"))
    validation = selected_funds_smoke.validate_pool(funds)

    assert len(funds) == 56
    assert len({fund.code for fund in funds}) == 55
    assert validation.duplicate_codes == ("016492",)
    assert validation.missing_rows == ()
    assert validation.bad_code_rows == ()


def test_select_smoke_funds_samples_each_category_in_file_order() -> None:
    """验证默认分层抽样按类别从 CSV 文件顺序选取样本。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当抽样类别或基金代码不符合预期时抛出。
    """

    funds = selected_funds_smoke.load_selected_funds(Path("docs/code_20260519.csv"))
    selected = selected_funds_smoke.select_smoke_funds(
        funds,
        codes=None,
        sample_per_category=1,
        limit=None,
    )

    assert [fund.code for fund in selected] == ["000216", "007721", "007360", "001548", "006597", "001821"]


def test_select_smoke_funds_can_use_explicit_codes() -> None:
    """验证可用指定基金代码选择 smoke 样本。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当指定代码选择结果不符合预期时抛出。
    """

    funds = selected_funds_smoke.load_selected_funds(Path("docs/code_20260519.csv"))
    selected = selected_funds_smoke.select_smoke_funds(
        funds,
        codes=("004393", "001548"),
        sample_per_category=0,
        limit=None,
    )

    assert [fund.code for fund in selected] == ["004393", "001548"]
    assert [fund.name for fund in selected] == ["安信企业价值优选混合A", "天弘上证50ETF联接A"]


def test_build_analyze_command_uses_explicit_mvp_inputs() -> None:
    """验证 smoke 命令显式传入 MVP 分析必需参数。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当命令缺少关键显式参数时抛出。
    """

    fund = selected_funds_smoke.SelectedFund(
        line_number=2,
        name="安信企业价值优选混合A",
        code="004393",
        category="国内股票类",
    )

    command = selected_funds_smoke.build_analyze_command(
        fund,
        report_year=2024,
        fund_analysis_bin=".venv/bin/fund-analysis",
        force_refresh=True,
    )

    assert command[:3] == [".venv/bin/fund-analysis", "analyze", "004393"]
    assert "--report-year" in command
    assert "--equity-position" in command
    assert "--actual-style" in command
    assert "--manager-tenure-months" in command
    assert "--valuation-state" in command
    assert "--force-refresh" in command
