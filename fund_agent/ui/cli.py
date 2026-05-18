"""基金分析命令行入口。

UI 层只负责解析用户输入和输出报告，不承载基金分析逻辑。
当前项目在 `pyproject.toml` 中暴露 `fund-analysis = fund_agent.ui.cli:app`，
因此 CLI 沿用 Typer 实现，而不是切换到 argparse。
"""

from __future__ import annotations

import asyncio
from typing import Annotated

import typer

from fund_agent.fund.template import TemplateFinalJudgment
from fund_agent.services import FundAnalysisRequest, FundAnalysisService, MoneyHorizon, ValuationState

app = typer.Typer(help="基金行为教练 Agent — 买入前专业级基金体检报告")


@app.command()
def analyze(
    fund_code: Annotated[str, typer.Argument(help="基金代码，如 110011")],
    report_year: Annotated[int, typer.Option("--report-year", help="年报年份")] = 2024,
    equity_position: Annotated[str | None, typer.Option("--equity-position", help="显式股票仓位，如 80%")] = None,
    actual_style: Annotated[str | None, typer.Option("--actual-style", help="显式实际持仓风格")] = None,
    actual_equity_position: Annotated[
        str | None,
        typer.Option("--actual-equity-position", help="显式实际股票仓位，如 80%"),
    ] = None,
    manager_tenure_months: Annotated[
        int | None,
        typer.Option("--manager-tenure-months", help="基金经理管理本基金月数"),
    ] = None,
    peer_fee_median: Annotated[str | None, typer.Option("--peer-fee-median", help="同类总费率中位数，如 1.2%")] = None,
    tracking_error: Annotated[str | None, typer.Option("--tracking-error", help="指数基金跟踪误差，如 1.5%")] = None,
    investment_amount: Annotated[
        str,
        typer.Option("--investment-amount", help="压力测试投入金额，CLI 显式默认 10000 元"),
    ] = "10000",
    max_tolerable_loss_rate: Annotated[
        str | None,
        typer.Option("--max-tolerable-loss-rate", help="最大可承受亏损比例，如 40%"),
    ] = None,
    valuation_state: Annotated[
        str,
        typer.Option("--valuation-state", help="估值状态：low/fair/high/unavailable"),
    ] = "unavailable",
    money_horizon: Annotated[
        str | None,
        typer.Option("--money-horizon", help="资金期限分类：long_enough/uncertain/too_short"),
    ] = None,
    user_money_horizon_years: Annotated[str | None, typer.Option("--user-money-horizon-years", help="用户资金不用年限")] = None,
    current_stage: Annotated[str | None, typer.Option("--current-stage", help="当前阶段与关键变化说明")] = None,
    final_judgment: Annotated[
        str,
        typer.Option("--final-judgment", help="最终判断：worth_holding/needs_attention/suggest_replace"),
    ] = "needs_attention",
    force_refresh: Annotated[bool, typer.Option("--force-refresh", help="强制刷新底层数据")] = False,
) -> None:
    """对指定基金执行完整分析，输出 8 章 Markdown 体检报告。

    Args:
        fund_code: 基金代码。
        report_year: 年报年份。
        equity_position: R=A+B-C 显式股票仓位。
        actual_style: 言行一致性显式实际风格。
        actual_equity_position: 言行一致性显式实际股票仓位。
        manager_tenure_months: 基金经理管理本基金月数。
        peer_fee_median: 同类总费率中位数。
        tracking_error: 指数基金跟踪误差。
        investment_amount: 压力测试投入金额。
        max_tolerable_loss_rate: 最大可承受亏损比例。
        valuation_state: 估值状态。
        money_horizon: 用户资金期限分类。
        user_money_horizon_years: 用户资金不用年限。
        current_stage: 当前阶段与关键变化说明。
        final_judgment: 最终持有判断。
        force_refresh: 是否强制刷新底层数据。

    Returns:
        无返回值，报告写入 stdout。

    Raises:
        typer.Exit: 分析失败时以非零状态退出。
    """

    request = FundAnalysisRequest(
        fund_code=fund_code,
        report_year=report_year,
        equity_position=equity_position,
        actual_style=actual_style,
        actual_equity_position=actual_equity_position,
        manager_tenure_months=manager_tenure_months,
        peer_fee_median=peer_fee_median,
        tracking_error=tracking_error,
        investment_amount=investment_amount,
        max_tolerable_loss_rate=max_tolerable_loss_rate,
        valuation_state=_valuation_state(valuation_state),
        money_horizon=_money_horizon(money_horizon),
        user_money_horizon_years=user_money_horizon_years,
        current_stage=current_stage,
        final_judgment=_final_judgment(final_judgment),
        force_refresh=force_refresh,
    )
    try:
        result = asyncio.run(FundAnalysisService().analyze(request))
    except Exception as exc:
        typer.echo(f"分析失败：{exc}", err=True)
        raise typer.Exit(code=1) from exc
    typer.echo(result.report_markdown, nl=False)


@app.command()
def checklist(
    fund_code: Annotated[str, typer.Argument(help="基金代码")],
) -> None:
    """提示检查清单独立命令尚未接入，避免输出误导性成功信息。

    Args:
        fund_code: 基金代码。

    Returns:
        无返回值。

    Raises:
        typer.Exit: 始终以非零状态退出，提示用户使用 `analyze`。
    """

    typer.echo(f"检查清单独立命令尚未接入 Service：{fund_code}。请先使用 analyze 生成完整报告。", err=True)
    raise typer.Exit(code=2)


def _valuation_state(value: str) -> ValuationState:
    """校验估值状态选项。

    Args:
        value: CLI 输入的估值状态。

    Returns:
        合法估值状态。

    Raises:
        typer.BadParameter: 当取值不在允许集合内时抛出。
    """

    allowed = {"low", "fair", "high", "unavailable"}
    if value not in allowed:
        raise typer.BadParameter(f"valuation_state 必须是 {', '.join(sorted(allowed))}")
    return value  # type: ignore[return-value]


def _money_horizon(value: str | None) -> MoneyHorizon | None:
    """校验资金期限分类。

    Args:
        value: CLI 输入的资金期限分类。

    Returns:
        合法资金期限分类或 `None`。

    Raises:
        typer.BadParameter: 当取值不在允许集合内时抛出。
    """

    if value is None:
        return None
    allowed = {"long_enough", "uncertain", "too_short"}
    if value not in allowed:
        raise typer.BadParameter(f"money_horizon 必须是 {', '.join(sorted(allowed))}")
    return value  # type: ignore[return-value]


def _final_judgment(value: str) -> TemplateFinalJudgment:
    """校验最终判断选项。

    Args:
        value: CLI 输入的最终判断。

    Returns:
        合法最终判断。

    Raises:
        typer.BadParameter: 当取值不在允许集合内时抛出。
    """

    allowed = {"worth_holding", "needs_attention", "suggest_replace"}
    if value not in allowed:
        raise typer.BadParameter(f"final_judgment 必须是 {', '.join(sorted(allowed))}")
    return value  # type: ignore[return-value]


if __name__ == "__main__":
    app()
