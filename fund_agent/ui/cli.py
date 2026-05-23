"""基金分析命令行入口。

UI 层只负责解析用户输入和输出报告，不承载基金分析逻辑。
当前项目在 `pyproject.toml` 中暴露 `fund-analysis = fund_agent.ui.cli:app`，
因此 CLI 沿用 Typer 实现，而不是切换到 argparse。
"""

from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Annotated

import typer

from fund_agent.config.paths import (
    DEFAULT_GOLDEN_ANSWER_JSON,
    DEFAULT_GOLDEN_PREFILL_OUTPUT,
    DEFAULT_GOLDEN_REVIEWED_MARKDOWN,
    DEFAULT_GOLDEN_TEMPLATE_PATH,
    DEFAULT_SELECTED_FUNDS_CSV,
)
from fund_agent.application import (
    ExtractionScoreRequest,
    ExtractionScoreUseCase,
    ExtractionSnapshotRequest,
    ExtractionSnapshotUseCase,
    FinalJudgment,
    FundAnalysisDeveloperOverrides,
    FundAnalysisRequest,
    FundAnalysisUseCase,
    GoldenAnswerBuildRequest,
    GoldenAnswerUseCase,
    GoldenPrefillRequest,
    GoldenPrefillUseCase,
    MoneyHorizon,
    QualityGateBlockedError,
    QualityGateNotRunBlockedError,
    QualityGateRequest,
    QualityGateUseCase,
    ThermometerBatchResult,
    ThermometerReading,
    ThermometerRequest,
    ThermometerUseCase,
    ValuationState,
)

app = typer.Typer(help="基金行为教练 Agent — 买入前专业级基金体检报告")
DEFAULT_GOLDEN_TEMPLATE = DEFAULT_GOLDEN_TEMPLATE_PATH
DEFAULT_GOLDEN_ANSWER_OUTPUT = DEFAULT_GOLDEN_ANSWER_JSON
# 独立 quality-gate helper 的历史 P4 score fixture 路径，不是仓库级默认输出根。
DEFAULT_QUALITY_GATE_SCORE = Path(
    "reports/extraction-snapshots/p4-s3b-004393-controller-final-score/score.json"
)


@app.command()
def analyze(
    fund_code: Annotated[str, typer.Argument(help="基金代码，如 110011")],
    report_year: Annotated[int, typer.Option("--report-year", help="年报年份")] = 2024,
    dev_override: Annotated[
        bool,
        typer.Option("--dev-override", help="启用开发覆盖/夹具参数"),
    ] = False,
    equity_position: Annotated[
        str | None, typer.Option("--equity-position", help="开发覆盖：显式股票仓位，如 80%")
    ] = None,
    actual_style: Annotated[
        str | None, typer.Option("--actual-style", help="开发覆盖：显式实际持仓风格")
    ] = None,
    actual_equity_position: Annotated[
        str | None,
        typer.Option("--actual-equity-position", help="开发覆盖：显式实际股票仓位，如 80%"),
    ] = None,
    manager_tenure_months: Annotated[
        int | None,
        typer.Option("--manager-tenure-months", help="开发覆盖：基金经理管理本基金月数"),
    ] = None,
    peer_fee_median: Annotated[
        str | None, typer.Option("--peer-fee-median", help="开发覆盖：同类总费率中位数，如 1.2%")
    ] = None,
    tracking_error: Annotated[
        str | None, typer.Option("--tracking-error", help="开发覆盖：指数基金跟踪误差，如 1.5%")
    ] = None,
    investment_amount: Annotated[
        str,
        typer.Option("--investment-amount", help="压力测试投入金额，CLI 显式默认 10000 元"),
    ] = "10000",
    max_tolerable_loss_rate: Annotated[
        str | None,
        typer.Option("--max-tolerable-loss-rate", help="最大可承受亏损比例，如 40%"),
    ] = None,
    valuation_state: Annotated[
        str | None,
        typer.Option(
            "--valuation-state",
            help=(
                "估值状态：low/fair/high/unavailable；不传则尝试自建温度计自动估值；"
                "传 unavailable 则手动灰灯且不调用温度计"
            ),
        ),
    ] = None,
    thermometer_cache_dir: Annotated[
        Path | None,
        typer.Option("--thermometer-cache-dir", help="analyze 自动估值使用的自建温度计缓存目录"),
    ] = None,
    money_horizon: Annotated[
        str | None,
        typer.Option(
            "--money-horizon", help="开发覆盖：资金期限分类 long_enough/uncertain/too_short"
        ),
    ] = None,
    user_money_horizon_years: Annotated[
        str | None, typer.Option("--user-money-horizon-years", help="用户资金不用年限")
    ] = None,
    current_stage: Annotated[
        str | None, typer.Option("--current-stage", help="开发覆盖：当前阶段与关键变化说明")
    ] = None,
    final_judgment_override: Annotated[
        str | None,
        typer.Option(
            "--final-judgment-override",
            "--final-judgment",
            help="开发覆盖：最终判断 worth_holding/needs_attention/suggest_replace",
        ),
    ] = None,
    force_refresh: Annotated[
        bool, typer.Option("--force-refresh", help="强制刷新底层数据")
    ] = False,
    quality_gate_policy: Annotated[
        str,
        typer.Option("--quality-gate-policy", help="开发覆盖：质量 gate 策略 off/warn/block"),
    ] = "block",
    quality_gate_source_csv: Annotated[
        Path | None,
        typer.Option("--quality-gate-source-csv", help="开发覆盖：质量 gate 精选基金池 CSV 路径"),
    ] = None,
    quality_gate_output_dir: Annotated[
        Path | None,
        typer.Option("--quality-gate-output-dir", help="开发覆盖：质量 gate 输出目录"),
    ] = None,
    quality_gate_run_id: Annotated[
        str | None,
        typer.Option("--quality-gate-run-id", help="开发覆盖：质量 gate 运行 ID"),
    ] = None,
    quality_gate_golden_answer_path: Annotated[
        Path | None,
        typer.Option(
            "--quality-gate-golden-answer-path", help="开发覆盖：strict golden answer JSON 路径"
        ),
    ] = None,
) -> None:
    """对指定基金执行完整分析，输出 8 章 Markdown 体检报告。

    Args:
        fund_code: 基金代码。
        report_year: 年报年份。
        dev_override: 是否启用开发覆盖参数。
        equity_position: R=A+B-C 显式股票仓位。
        actual_style: 言行一致性显式实际风格。
        actual_equity_position: 言行一致性显式实际股票仓位。
        manager_tenure_months: 基金经理管理本基金月数。
        peer_fee_median: 同类总费率中位数。
        tracking_error: 指数基金跟踪误差。
        investment_amount: 压力测试投入金额。
        max_tolerable_loss_rate: 最大可承受亏损比例。
        valuation_state: 估值状态；缺省时允许自动温度计估值。
        thermometer_cache_dir: 自动温度计缓存目录。
        money_horizon: 用户资金期限分类。
        user_money_horizon_years: 用户资金不用年限。
        current_stage: 当前阶段与关键变化说明。
        final_judgment_override: 开发覆盖最终持有判断。
        force_refresh: 是否强制刷新底层数据。
        quality_gate_policy: 质量 gate 策略。
        quality_gate_source_csv: 质量 gate 精选基金池 CSV 路径。
        quality_gate_output_dir: 质量 gate 输出目录。
        quality_gate_run_id: 质量 gate 运行 ID。
        quality_gate_golden_answer_path: strict golden answer JSON 路径。

    Returns:
        无返回值，报告写入 stdout。

    Raises:
        typer.Exit: 分析失败时以非零状态退出。
    """

    try:
        developer_overrides = _build_developer_overrides(
            dev_override=dev_override,
            equity_position=equity_position,
            actual_style=actual_style,
            actual_equity_position=actual_equity_position,
            manager_tenure_months=manager_tenure_months,
            peer_fee_median=peer_fee_median,
            tracking_error=tracking_error,
            money_horizon=money_horizon,
            current_stage=current_stage,
            final_judgment_override=final_judgment_override,
            quality_gate_policy=quality_gate_policy,
            quality_gate_source_csv=quality_gate_source_csv,
            quality_gate_output_dir=quality_gate_output_dir,
            quality_gate_run_id=quality_gate_run_id,
            quality_gate_golden_answer_path=quality_gate_golden_answer_path,
        )
    except typer.BadParameter as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(code=2) from exc
    request = FundAnalysisRequest(
        fund_code=fund_code,
        report_year=report_year,
        investment_amount=investment_amount,
        max_tolerable_loss_rate=max_tolerable_loss_rate,
        valuation_state=_valuation_state(valuation_state),
        thermometer_cache_dir=thermometer_cache_dir,
        user_money_horizon_years=user_money_horizon_years,
        force_refresh=force_refresh,
        mode="developer_override" if dev_override else "product",
        developer_overrides=developer_overrides,
    )
    try:
        result = asyncio.run(FundAnalysisUseCase().analyze(request))
    except QualityGateNotRunBlockedError as exc:
        _echo_quality_gate_not_run_blocked(exc)
        raise typer.Exit(code=2) from exc
    except QualityGateBlockedError as exc:
        _echo_quality_gate_blocked(exc)
        raise typer.Exit(code=2) from exc
    except Exception as exc:
        typer.echo(f"分析失败：{exc}", err=True)
        raise typer.Exit(code=1) from exc
    _echo_quality_gate_summary(result)
    typer.echo(result.report_markdown, nl=False)


@app.command()
def checklist(
    fund_code: Annotated[str, typer.Argument(help="基金代码")],
    report_year: Annotated[int, typer.Option("--report-year", help="年报年份")] = 2024,
    investment_amount: Annotated[
        str,
        typer.Option("--investment-amount", help="压力测试投入金额，CLI 显式默认 10000 元"),
    ] = "10000",
    max_tolerable_loss_rate: Annotated[
        str | None,
        typer.Option("--max-tolerable-loss-rate", help="最大可承受亏损比例，如 40%"),
    ] = None,
    valuation_state: Annotated[
        str | None,
        typer.Option(
            "--valuation-state",
            help=(
                "估值状态：low/fair/high/unavailable；不传则尝试自建温度计自动估值；"
                "传 unavailable 则手动灰灯且不调用温度计"
            ),
        ),
    ] = None,
    thermometer_cache_dir: Annotated[
        Path | None,
        typer.Option("--thermometer-cache-dir", help="自动估值使用的自建温度计缓存目录"),
    ] = None,
    user_money_horizon_years: Annotated[
        str | None, typer.Option("--user-money-horizon-years", help="用户资金不用年限")
    ] = None,
    force_refresh: Annotated[
        bool, typer.Option("--force-refresh", help="强制刷新底层数据")
    ] = False,
) -> None:
    """对指定基金执行独立买入前检查清单。

    Args:
        fund_code: 基金代码。
        report_year: 年报年份。
        investment_amount: 压力测试投入金额。
        max_tolerable_loss_rate: 最大可承受亏损比例。
        valuation_state: 估值状态；缺省时允许自动温度计估值。
        thermometer_cache_dir: 自动温度计缓存目录。
        user_money_horizon_years: 用户资金不用年限。
        force_refresh: 是否强制刷新底层数据。

    Returns:
        无返回值，检查清单摘要写入 stdout。

    Raises:
        typer.Exit: 检查清单生成失败时以非零状态退出。
    """

    request = FundAnalysisRequest(
        fund_code=fund_code,
        report_year=report_year,
        investment_amount=investment_amount,
        max_tolerable_loss_rate=max_tolerable_loss_rate,
        valuation_state=_valuation_state(valuation_state),
        thermometer_cache_dir=thermometer_cache_dir,
        user_money_horizon_years=user_money_horizon_years,
        force_refresh=force_refresh,
    )
    try:
        result = asyncio.run(FundAnalysisUseCase().checklist(request))
    except QualityGateNotRunBlockedError as exc:
        _echo_quality_gate_not_run_blocked(exc)
        raise typer.Exit(code=2) from exc
    except QualityGateBlockedError as exc:
        _echo_quality_gate_blocked(exc)
        raise typer.Exit(code=2) from exc
    except Exception as exc:
        typer.echo(f"检查清单生成失败：{exc}", err=True)
        raise typer.Exit(code=1) from exc
    _echo_quality_gate_summary(result)
    _echo_checklist_result(result)


@app.command("thermometer")
def thermometer(
    index_code: Annotated[
        str | None,
        typer.Option(
            "--index",
            help="自建温度计代码；支持 wind_all_a、000300、000905 或逗号分隔批量",
        ),
    ] = None,
    cache_dir: Annotated[
        Path | None,
        typer.Option("--cache-dir", help="温度计缓存目录；不传则使用默认 cache/thermometer"),
    ] = None,
    force_refresh: Annotated[
        bool, typer.Option("--force-refresh", help="强制刷新自有温度计历史数据")
    ] = False,
    output_json: Annotated[bool, typer.Option("--json", help="以 JSON 输出温度计快照摘要")] = False,
) -> None:
    """查询自建市场或指数温度计读数。

    Args:
        index_code: 自建温度计代码；为空时由 Service 默认路由到全 A 市场；逗号分隔时批量查询。
        cache_dir: 温度计缓存目录。
        force_refresh: 是否强制刷新。
        output_json: 是否输出 JSON。

    Returns:
        无返回值，温度计摘要写入 stdout。

    Raises:
        typer.Exit: Service 校验或运行失败时以非零状态退出。
    """

    try:
        parsed_index_code, parsed_index_codes = _parse_index_option(index_code)
        snapshot = asyncio.run(
            ThermometerUseCase().run(
                ThermometerRequest(
                    cache_dir=cache_dir,
                    force_refresh=force_refresh,
                    index_code=parsed_index_code,
                    index_codes=parsed_index_codes,
                )
            )
        )
    except ValueError as exc:
        typer.echo(f"温度计请求参数错误：{exc}", err=True)
        raise typer.Exit(code=2) from exc
    except Exception as exc:
        typer.echo(f"温度计查询失败：{exc}", err=True)
        raise typer.Exit(code=1) from exc
    payload = _thermometer_snapshot_payload(snapshot)
    if output_json:
        typer.echo(json.dumps(payload, ensure_ascii=False, indent=2))
        return
    _echo_thermometer_snapshot(payload)


@app.command("extraction-snapshot")
def extraction_snapshot(
    run_id: Annotated[
        str, typer.Option("--run-id", help="本次快照运行 ID，如 p4-s1-20260519-004393")
    ],
    report_year: Annotated[int, typer.Option("--report-year", help="年报年份")] = 2024,
    fund_code: Annotated[
        str | None, typer.Option("--fund-code", help="指定单只基金代码；不传则按类别抽样")
    ] = None,
    source_csv: Annotated[
        Path,
        typer.Option("--source-csv", help="精选基金池 CSV 路径"),
    ] = DEFAULT_SELECTED_FUNDS_CSV,
    output_dir: Annotated[Path | None, typer.Option("--output-dir", help="显式输出目录")] = None,
    sample_per_category: Annotated[
        int, typer.Option("--sample-per-category", help="未指定基金代码时每类抽样数量")
    ] = 1,
    limit: Annotated[int | None, typer.Option("--limit", help="最多抽取基金数量")] = None,
    force_refresh: Annotated[
        bool, typer.Option("--force-refresh", help="强制刷新底层数据")
    ] = False,
) -> None:
    """生成精选基金池字段级抽取快照。

    Args:
        run_id: 本次运行 ID。
        report_year: 年报年份。
        fund_code: 指定单只基金代码；为空时按类别抽样。
        source_csv: 精选基金池 CSV 路径。
        output_dir: 显式输出目录。
        sample_per_category: 未指定基金代码时每个类别抽样数量。
        limit: 最大抽取数量。
        force_refresh: 是否强制刷新底层数据。

    Returns:
        无返回值，产物写入输出目录并在 stdout 打印路径。

    Raises:
        typer.Exit: 快照生成失败时以非零状态退出。
    """

    try:
        result = asyncio.run(
            ExtractionSnapshotUseCase().run(
                ExtractionSnapshotRequest(
                    fund_code=fund_code,
                    report_year=report_year,
                    source_csv=source_csv,
                    run_id=run_id,
                    output_dir=output_dir,
                    force_refresh=force_refresh,
                    sample_per_category=sample_per_category,
                    limit=limit,
                )
            )
        )
    except Exception as exc:
        typer.echo(f"快照生成失败：{exc}", err=True)
        raise typer.Exit(code=1) from exc
    typer.echo(f"snapshot: {result.snapshot_path}")
    typer.echo(f"summary: {result.summary_path}")
    typer.echo(f"errors: {result.errors_path}")


@app.command("extraction-score")
def extraction_score(
    snapshot_path: Annotated[
        Path, typer.Option("--snapshot-path", help="P4-S1 snapshot.jsonl 路径")
    ],
    source_csv: Annotated[
        Path,
        typer.Option("--source-csv", help="精选基金池 CSV 路径"),
    ] = DEFAULT_SELECTED_FUNDS_CSV,
    output_dir: Annotated[Path | None, typer.Option("--output-dir", help="显式输出目录")] = None,
    golden_answer_path: Annotated[
        Path | None,
        typer.Option(
            "--golden-answer-path",
            help="strict golden answer JSON 路径；提供后执行 correctness 比对",
        ),
    ] = None,
    errors_path: Annotated[
        Path | None,
        typer.Option(
            "--errors-path",
            help="extraction-snapshot 产出的 errors.jsonl 路径；提供后纳入失败基金 accounting",
        ),
    ] = None,
) -> None:
    """对 P4-S1 snapshot 生成字段级 coverage / traceability 评分。

    Args:
        snapshot_path: P4-S1 输出的 JSONL 快照路径。
        source_csv: 精选基金池 CSV 路径。
        output_dir: 显式输出目录。
        golden_answer_path: strict golden answer JSON 路径；为空时只输出 FQ0 skeleton。
        errors_path: P4-S1 输出的错误 JSONL 路径；为空时不纳入失败基金 accounting。

    Returns:
        无返回值，产物写入输出目录并在 stdout 打印路径。

    Raises:
        typer.Exit: 评分失败时以非零状态退出。
    """

    try:
        result = ExtractionScoreUseCase().run(
            ExtractionScoreRequest(
                snapshot_path=snapshot_path,
                source_csv=source_csv,
                output_dir=output_dir,
                golden_answer_path=golden_answer_path,
                errors_path=errors_path,
            )
        )
    except Exception as exc:
        typer.echo(f"评分生成失败：{exc}", err=True)
        raise typer.Exit(code=1) from exc
    typer.echo(f"score_json: {result.score_json_path}")
    typer.echo(f"score_md: {result.score_markdown_path}")
    typer.echo(f"golden_set: {result.golden_set_path}")


@app.command("golden-prefill")
def golden_prefill(
    template_path: Annotated[
        Path,
        typer.Option("--template-path", help="golden answer Markdown 模板路径"),
    ] = DEFAULT_GOLDEN_TEMPLATE,
    output_path: Annotated[
        Path,
        typer.Option("--output-path", help="预填底稿输出路径"),
    ] = DEFAULT_GOLDEN_PREFILL_OUTPUT,
    report_year: Annotated[int, typer.Option("--report-year", help="年报年份")] = 2024,
    force_refresh: Annotated[
        bool, typer.Option("--force-refresh", help="强制刷新底层数据")
    ] = False,
) -> None:
    """生成 correctness golden answer 自动预填底稿。

    Args:
        template_path: golden answer Markdown 模板路径。
        output_path: 预填底稿输出路径。
        report_year: 年报年份。
        force_refresh: 是否强制刷新底层数据。

    Returns:
        无返回值，产物写入输出路径并在 stdout 打印摘要。

    Raises:
        typer.Exit: 预填失败时以非零状态退出。
    """

    try:
        result = asyncio.run(
            GoldenPrefillUseCase().run(
                GoldenPrefillRequest(
                    template_path=template_path,
                    output_path=output_path,
                    report_year=report_year,
                    force_refresh=force_refresh,
                )
            )
        )
    except Exception as exc:
        typer.echo(f"golden answer 预填失败：{exc}", err=True)
        raise typer.Exit(code=1) from exc
    typer.echo(f"prefill: {result.output_path}")
    typer.echo(f"funds: {len(result.succeeded_fund_codes)}/{len(result.fund_codes)} succeeded")
    if result.failed_fund_codes:
        typer.echo(f"failed: {', '.join(result.failed_fund_codes)}")


@app.command("golden-build")
def golden_build(
    input_path: Annotated[
        Path,
        typer.Option("--input-path", help="人工审核后的 golden answer Markdown 路径"),
    ] = DEFAULT_GOLDEN_REVIEWED_MARKDOWN,
    output_path: Annotated[
        Path,
        typer.Option("--output-path", help="strict golden answer JSON 输出路径"),
    ] = DEFAULT_GOLDEN_ANSWER_OUTPUT,
) -> None:
    """把人工审核后的 golden answer Markdown 转换为 strict JSON。

    Args:
        input_path: 人工审核后的 Markdown 路径。
        output_path: strict golden answer JSON 输出路径。

    Returns:
        无返回值，产物写入输出路径并在 stdout 打印摘要。

    Raises:
        typer.Exit: 转换或校验失败时以非零状态退出。
    """

    try:
        result = GoldenAnswerUseCase().build(
            GoldenAnswerBuildRequest(
                input_path=input_path,
                output_path=output_path,
            )
        )
    except Exception as exc:
        typer.echo(f"golden answer 构建失败：{exc}", err=True)
        raise typer.Exit(code=1) from exc
    typer.echo(f"golden_answer: {result.output_path}")
    typer.echo(f"funds: {result.fund_count}")
    typer.echo(f"records: {result.record_count}")
    typer.echo(f"skipped: {result.skipped_count}")


@app.command("quality-gate")
def quality_gate(
    score_path: Annotated[
        Path, typer.Option("--score-path", help="extraction-score 产出的 score.json 路径")
    ] = DEFAULT_QUALITY_GATE_SCORE,
    output_dir: Annotated[
        Path | None, typer.Option("--output-dir", help="质量 gate 输出目录")
    ] = None,
) -> None:
    """基于 extraction-score 结果生成报告质量 gate。

    Args:
        score_path: `score.json` 路径。
        output_dir: 输出目录。

    Returns:
        无返回值，产物写入输出目录并在 stdout 打印摘要。

    Raises:
        typer.Exit: gate 生成失败时以非零状态退出。
    """

    try:
        result = QualityGateUseCase().run(
            QualityGateRequest(
                score_path=score_path,
                output_dir=output_dir,
            )
        )
    except Exception as exc:
        typer.echo(f"质量 gate 生成失败：{exc}", err=True)
        raise typer.Exit(code=1) from exc
    typer.echo(f"quality_gate_json: {result.gate_json_path}")
    typer.echo(f"quality_gate_md: {result.gate_markdown_path}")
    typer.echo(f"status: {result.status}")
    typer.echo(f"issues: {len(result.issues)}")


def _valuation_state(value: str | None) -> ValuationState | None:
    """校验估值状态选项。

    Args:
        value: CLI 输入的估值状态；`None` 表示允许自动温度计估值。

    Returns:
        合法估值状态或 `None`。

    Raises:
        typer.BadParameter: 当取值不在允许集合内时抛出。
    """

    if value is None:
        return None
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


def _final_judgment(value: str) -> FinalJudgment:
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


def _quality_gate_policy(value: str):
    """校验 quality gate 策略。

    Args:
        value: CLI 输入的策略。

    Returns:
        合法 quality gate 策略。

    Raises:
        typer.BadParameter: 当取值不在允许集合内时抛出。
    """

    allowed = {"off", "warn", "block"}
    if value not in allowed:
        raise typer.BadParameter(f"quality_gate_policy 必须是 {', '.join(sorted(allowed))}")
    return value


def _has_developer_override_options(
    *,
    equity_position: str | None,
    actual_style: str | None,
    actual_equity_position: str | None,
    manager_tenure_months: int | None,
    peer_fee_median: str | None,
    tracking_error: str | None,
    money_horizon: str | None,
    current_stage: str | None,
    final_judgment_override: str | None,
    quality_gate_policy: str,
    quality_gate_source_csv: Path | None,
    quality_gate_output_dir: Path | None,
    quality_gate_run_id: str | None,
    quality_gate_golden_answer_path: Path | None,
) -> tuple[str, ...]:
    """识别 CLI 中出现的开发覆盖参数。

    Args:
        equity_position: 显式股票仓位。
        actual_style: 显式实际持仓风格。
        actual_equity_position: 显式实际股票仓位。
        manager_tenure_months: 基金经理管理本基金月数。
        peer_fee_median: 同类总费率中位数。
        tracking_error: 指数基金跟踪误差。
        money_horizon: 资金期限分类。
        current_stage: 当前阶段与关键变化。
        final_judgment_override: 开发覆盖最终判断。
        quality_gate_policy: quality gate 策略。
        quality_gate_source_csv: quality gate 精选基金池 CSV 路径。
        quality_gate_output_dir: quality gate 输出目录。
        quality_gate_run_id: quality gate 运行 ID。
        quality_gate_golden_answer_path: strict golden answer JSON 路径。

    Returns:
        已传入的开发覆盖参数名。

    Raises:
        无显式抛出。
    """

    provided: list[str] = []
    if equity_position is not None:
        provided.append("--equity-position")
    if actual_style is not None:
        provided.append("--actual-style")
    if actual_equity_position is not None:
        provided.append("--actual-equity-position")
    if manager_tenure_months is not None:
        provided.append("--manager-tenure-months")
    if peer_fee_median is not None:
        provided.append("--peer-fee-median")
    if tracking_error is not None:
        provided.append("--tracking-error")
    if money_horizon is not None:
        provided.append("--money-horizon")
    if current_stage is not None:
        provided.append("--current-stage")
    if final_judgment_override is not None:
        provided.append("--final-judgment-override")
    if quality_gate_policy != "block":
        provided.append("--quality-gate-policy")
    if quality_gate_source_csv is not None:
        provided.append("--quality-gate-source-csv")
    if quality_gate_output_dir is not None:
        provided.append("--quality-gate-output-dir")
    if quality_gate_run_id is not None:
        provided.append("--quality-gate-run-id")
    if quality_gate_golden_answer_path is not None:
        provided.append("--quality-gate-golden-answer-path")
    return tuple(provided)


def _build_developer_overrides(
    *,
    dev_override: bool,
    equity_position: str | None,
    actual_style: str | None,
    actual_equity_position: str | None,
    manager_tenure_months: int | None,
    peer_fee_median: str | None,
    tracking_error: str | None,
    money_horizon: str | None,
    current_stage: str | None,
    final_judgment_override: str | None,
    quality_gate_policy: str,
    quality_gate_source_csv: Path | None,
    quality_gate_output_dir: Path | None,
    quality_gate_run_id: str | None,
    quality_gate_golden_answer_path: Path | None,
) -> FundAnalysisDeveloperOverrides | None:
    """构造 nested developer override 契约。

    Args:
        dev_override: 是否启用开发覆盖模式。
        equity_position: 显式股票仓位。
        actual_style: 显式实际持仓风格。
        actual_equity_position: 显式实际股票仓位。
        manager_tenure_months: 基金经理管理本基金月数。
        peer_fee_median: 同类总费率中位数。
        tracking_error: 指数基金跟踪误差。
        money_horizon: 资金期限分类。
        current_stage: 当前阶段与关键变化。
        final_judgment_override: 开发覆盖最终判断。
        quality_gate_policy: quality gate 策略。
        quality_gate_source_csv: quality gate 精选基金池 CSV 路径。
        quality_gate_output_dir: quality gate 输出目录。
        quality_gate_run_id: quality gate 运行 ID。
        quality_gate_golden_answer_path: strict golden answer JSON 路径。

    Returns:
        开发覆盖对象；product mode 返回 `None`。

    Raises:
        typer.BadParameter: 未启用 `--dev-override` 但传入开发参数时抛出。
    """

    provided_options = _has_developer_override_options(
        equity_position=equity_position,
        actual_style=actual_style,
        actual_equity_position=actual_equity_position,
        manager_tenure_months=manager_tenure_months,
        peer_fee_median=peer_fee_median,
        tracking_error=tracking_error,
        money_horizon=money_horizon,
        current_stage=current_stage,
        final_judgment_override=final_judgment_override,
        quality_gate_policy=quality_gate_policy,
        quality_gate_source_csv=quality_gate_source_csv,
        quality_gate_output_dir=quality_gate_output_dir,
        quality_gate_run_id=quality_gate_run_id,
        quality_gate_golden_answer_path=quality_gate_golden_answer_path,
    )
    if provided_options and not dev_override:
        raise typer.BadParameter(
            f"开发覆盖参数必须同时传 --dev-override：{', '.join(provided_options)}"
        )
    if not dev_override:
        return None
    return FundAnalysisDeveloperOverrides(
        equity_position=equity_position,
        actual_style=actual_style,
        actual_equity_position=actual_equity_position,
        manager_tenure_months=manager_tenure_months,
        peer_fee_median=peer_fee_median,
        tracking_error=tracking_error,
        money_horizon=_money_horizon(money_horizon),
        current_stage=current_stage,
        final_judgment_override=(
            _final_judgment(final_judgment_override)
            if final_judgment_override is not None
            else None
        ),
        quality_gate_policy=_quality_gate_policy(quality_gate_policy),
        quality_gate_source_csv=quality_gate_source_csv,
        quality_gate_output_dir=quality_gate_output_dir,
        quality_gate_run_id=quality_gate_run_id,
        quality_gate_golden_answer_path=quality_gate_golden_answer_path,
    )


def _thermometer_snapshot_payload(snapshot) -> dict[str, object]:  # type: ignore[no-untyped-def]
    """把温度计快照转换为 CLI 输出 payload。

    Args:
        snapshot: 温度计快照。

    Returns:
        可 JSON 序列化的摘要 payload。

    Raises:
        无显式抛出。
    """

    if isinstance(snapshot, ThermometerReading):
        return _thermometer_reading_payload(snapshot)
    if isinstance(snapshot, ThermometerBatchResult):
        return _thermometer_batch_payload(snapshot)

    market = snapshot.market
    macro = snapshot.macro
    return {
        "source": snapshot.source,
        "cached": snapshot.cached,
        "stale": snapshot.stale,
        "unavailable": snapshot.unavailable,
        "unavailable_reason": snapshot.unavailable_reason,
        "as_of_text": snapshot.as_of_text,
        "as_of_date": snapshot.as_of_date,
        "fetched_at": snapshot.fetched_at,
        "market_temperature": str(market.value) if market and market.value is not None else None,
        "market_valuation_band": market.valuation_band if market else None,
        "market_trend_text": market.trend_text if market else None,
        "index_count": len(snapshot.indexes),
        "bond_temperature": (
            str(macro.bond_temperature) if macro and macro.bond_temperature is not None else None
        ),
        "ten_year_treasury_yield": (
            str(macro.ten_year_treasury_yield)
            if macro and macro.ten_year_treasury_yield is not None
            else None
        ),
    }


def _thermometer_batch_payload(batch: ThermometerBatchResult) -> dict[str, object]:
    """把批量自建温度计读数转换为 CLI 输出 payload。

    Args:
        batch: 批量温度计结果。

    Returns:
        可 JSON 序列化的批量摘要 payload。

    Raises:
        无显式抛出。
    """

    return {
        "source": batch.source,
        "requested_index_codes": list(batch.requested_index_codes),
        "result_count": len(batch.readings),
        "unavailable": batch.unavailable,
        "partial_unavailable": batch.partial_unavailable,
        "unavailable_count": batch.unavailable_count,
        "generated_at": batch.generated_at,
        "disclaimer": batch.disclaimer,
        "readings": [_thermometer_reading_payload(reading) for reading in batch.readings],
    }


def _thermometer_reading_payload(reading: ThermometerReading) -> dict[str, object]:
    """把自建温度计读数转换为 CLI 输出 payload。

    Args:
        reading: 自建温度计读数。

    Returns:
        可 JSON 序列化的摘要 payload。

    Raises:
        无显式抛出。
    """

    return {
        "source": reading.source,
        "cached": reading.cached,
        "stale": reading.stale,
        "unavailable": reading.unavailable,
        "unavailable_reason": reading.unavailable_reason,
        "index_code": reading.index_code,
        "index_name": reading.index_name,
        "temperature": str(reading.temperature) if reading.temperature is not None else None,
        "pe_percentile": (
            str(reading.pe_percentile) if reading.pe_percentile is not None else None
        ),
        "pb_percentile": (
            str(reading.pb_percentile) if reading.pb_percentile is not None else None
        ),
        "valuation_state_candidate": reading.valuation_state_candidate,
        "data_date": reading.data_date,
        "lookback_start": reading.lookback_start,
        "lookback_end": reading.lookback_end,
        "fetched_at": reading.fetched_at,
        "disclaimer": reading.disclaimer,
    }


def _echo_thermometer_snapshot(payload: dict[str, object]) -> None:
    """输出温度计快照摘要。

    Args:
        payload: `_thermometer_snapshot_payload()` 生成的摘要。

    Returns:
        无返回值。

    Raises:
        无显式抛出。
    """

    readings = payload.get("readings")
    for key, value in payload.items():
        if key == "readings":
            continue
        typer.echo(f"{key}: {_format_cli_value(value)}")
    if isinstance(readings, list):
        for reading in readings:
            if not isinstance(reading, dict):
                continue
            typer.echo("")
            typer.echo(f"[{_format_cli_value(reading.get('index_code'))}]")
            for key, value in reading.items():
                if key in {"source", "index_code", "disclaimer"}:
                    continue
                typer.echo(f"{key}: {_format_cli_value(value)}")


def _parse_index_option(index_code: str | None) -> tuple[str | None, tuple[str, ...] | None]:
    """解析 CLI `--index` 选项为显式 Service 请求字段。

    Args:
        index_code: CLI 原始指数选项。

    Returns:
        单指数代码或批量指数代码；未传入时两者都为空。

    Raises:
        无显式抛出；指数形态校验由 Service 统一处理。
    """

    if index_code is None:
        return None, None
    if "," not in index_code:
        return index_code, None
    return None, tuple(index_code.split(","))


def _format_cli_value(value: object) -> str:
    """格式化 CLI 摘要值。

    Args:
        value: 待格式化值。

    Returns:
        CLI 友好的字符串。

    Raises:
        无显式抛出。
    """

    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, list | tuple):
        return ",".join(str(item) for item in value)
    if value is None:
        return ""
    return str(value)


def _echo_checklist_result(result) -> None:  # type: ignore[no-untyped-def]
    """输出独立检查清单摘要。

    Args:
        result: `FundChecklistResult`。

    Returns:
        无返回值。

    Raises:
        无显式抛出。
    """

    checklist_result = result.checklist_result
    decision = result.final_judgment_decision
    valuation_resolution = result.valuation_state_resolution
    typer.echo(f"fund_code: {result.structured_data.fund_code}")
    typer.echo(f"report_year: {result.structured_data.report_year}")
    typer.echo(f"overall_signal: {checklist_result.overall_signal}")
    typer.echo(f"overall_status: {checklist_result.overall_status}")
    typer.echo(f"valuation_state: {valuation_resolution.state}")
    typer.echo(f"valuation_source: {valuation_resolution.source}")
    if valuation_resolution.index_code:
        typer.echo(f"valuation_index_code: {valuation_resolution.index_code}")
    if valuation_resolution.temperature is not None:
        typer.echo(f"valuation_temperature: {valuation_resolution.temperature}")
    typer.echo(f"final_judgment: {decision.selected_judgment}")
    typer.echo(f"derived_final_judgment: {decision.derived_judgment}")
    typer.echo(f"final_judgment_source: {decision.source}")
    typer.echo(f"next_minimum_verification: {checklist_result.next_minimum_verification}")
    typer.echo("")
    for item in checklist_result.items:
        typer.echo(f"- {item.code}: {item.signal}/{item.status} | {item.question}")
        typer.echo(f"  reason: {item.reason}")
        if item.anchors:
            typer.echo(f"  evidence_count: {len(item.anchors)}")


def _echo_quality_gate_blocked(error: QualityGateBlockedError) -> None:
    """输出结构化 quality gate 阻断信息。

    Args:
        error: Service 抛出的结构化阻断异常。

    Returns:
        无返回值。

    Raises:
        无显式抛出。
    """

    result = error.quality_gate_result
    typer.echo("质量 gate 阻断报告输出", err=True)
    typer.echo(f"quality_gate_status: {result.status}", err=True)
    typer.echo(f"quality_gate_issues: {len(result.issues)}", err=True)
    typer.echo(f"quality_gate_json: {result.gate_json_path}", err=True)
    typer.echo(f"quality_gate_md: {result.gate_markdown_path}", err=True)


def _echo_quality_gate_not_run_blocked(error: QualityGateNotRunBlockedError) -> None:
    """输出 quality gate 未运行导致的 block 策略阻断信息。

    Args:
        error: Service 抛出的未运行阻断异常。

    Returns:
        无返回值。

    Raises:
        无显式抛出。
    """

    typer.echo("质量 gate 阻断报告输出", err=True)
    typer.echo("quality_gate_status: not_run", err=True)
    typer.echo(f"quality_gate_not_run_reason: {error.reason}", err=True)


def _echo_quality_gate_summary(result) -> None:  # type: ignore[no-untyped-def]
    """把 quality gate 摘要写入 stderr。

    Args:
        result: `FundAnalysisResult`。

    Returns:
        无返回值。

    Raises:
        无显式抛出。
    """

    if result.quality_gate_result is not None:
        gate = result.quality_gate_result
        typer.echo(f"quality_gate_status: {gate.status}", err=True)
        typer.echo(f"quality_gate_issues: {len(gate.issues)}", err=True)
        for info_line in _quality_gate_info_lines(gate):
            typer.echo(f"quality_gate_info: {info_line}", err=True)
        typer.echo(f"quality_gate_json: {gate.gate_json_path}", err=True)
        typer.echo(f"quality_gate_md: {gate.gate_markdown_path}", err=True)
        return
    if result.quality_gate_not_run_reason:
        typer.echo(f"quality gate not run: {result.quality_gate_not_run_reason}", err=True)


def _quality_gate_info_lines(gate) -> tuple[str, ...]:  # type: ignore[no-untyped-def]
    """生成 fund-scoped correctness coverage informational stderr 行。

    Args:
        gate: quality gate 结果对象。

    Returns:
        需要写入 stderr 的简短 info 行。

    Raises:
        无显式抛出。
    """

    lines: list[str] = []
    coverage_reasons = {
        "not_configured",
        "fund_not_covered",
        "no_comparable_fields",
        "field_not_comparable",
    }
    for issue in gate.issues:
        if getattr(issue, "rule_code", None) != "FQ0":
            continue
        if getattr(issue, "severity", None) != "info":
            continue
        reason = getattr(issue, "reason", None)
        fund_code = getattr(issue, "fund_code", None)
        if reason not in coverage_reasons or not fund_code:
            continue
        lines.append(f"strict golden answer not covered for fund_code {fund_code} reason={reason}")
    return tuple(lines)


if __name__ == "__main__":
    app()
