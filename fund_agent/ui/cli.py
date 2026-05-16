import typer

app = typer.Typer(help="基金行为教练 Agent — 买入前专业级基金体检报告")


@app.command()
def analyze(
    fund_code: str = typer.Argument(help="基金代码，如 110011"),
    amount: float | None = typer.Option(None, help="拟投资金额（元）"),
) -> None:
    """对指定基金执行完整分析，输出 8 章体检报告。"""
    typer.echo(f"开始分析基金 {fund_code}...")
    # TODO: 调用 FundAnalysisService


@app.command()
def checklist(
    fund_code: str = typer.Argument(help="基金代码"),
) -> None:
    """对指定基金执行买入前 7 问题检查清单。"""
    typer.echo(f"执行检查清单: {fund_code}...")
    # TODO: 调用 ChecklistService


if __name__ == "__main__":
    app()
