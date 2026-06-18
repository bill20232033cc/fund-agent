"""基金分析命令行入口。

UI 层只负责解析用户输入和输出报告，不承载基金分析逻辑。
当前项目在 `pyproject.toml` 中暴露 `fund-analysis = fund_agent.ui.cli:app`，
因此 CLI 沿用 Typer 实现，而不是切换到 argparse。
"""

from __future__ import annotations

import asyncio
import json
from pathlib import Path
import sys
import threading
import time
from typing import Annotated, Callable, Mapping

import typer

from fund_agent.config.llm import LLMProviderConfigError
from fund_agent.config.paths import (
    DEFAULT_GOLDEN_ANSWER_JSON,
    DEFAULT_GOLDEN_PREFILL_OUTPUT,
    DEFAULT_GOLDEN_REVIEWED_MARKDOWN,
    DEFAULT_GOLDEN_TEMPLATE_PATH,
    DEFAULT_SELECTED_FUNDS_CSV,
)
from fund_agent.services import (
    ExtractionScoreRequest,
    ExtractionScoreService,
    ExtractionSnapshotRequest,
    ExtractionSnapshotService,
    FinalJudgment,
    FundChecklistResult,
    FundAnalysisDeveloperOverrides,
    FundAnalysisRequest,
    FundAnalysisService,
    FundArtifactInput,
    GoldenAnswerBuildRequest,
    GoldenAnswerService,
    GoldenPrefillRequest,
    GoldenPrefillService,
    GoldenReadinessPreflightRequest,
    GoldenReadinessPreflightService,
    MoneyHorizon,
    MultiYearAnnualAnalysisRequest,
    MultiYearAnnualAnalysisResult,
    LLMProviderConstructionError,
    QualityGateBlockedError,
    QualityGateNotRunBlockedError,
    QualityGateRequest,
    QualityGateService,
    ThermometerBatchResult,
    ThermometerReading,
    ThermometerRequest,
    ThermometerService,
    ValuationState,
    FundLLMAnalysisResult,
    FundLLMHostedRunResult,
)
from fund_agent.services.llm_run_artifacts import (
    LLMRunArtifactWriteResult,
    write_llm_incomplete_run_artifacts,
)

app = typer.Typer(help="基金行为教练 Agent — 买入前专业级基金体检报告")
DEFAULT_GOLDEN_TEMPLATE = DEFAULT_GOLDEN_TEMPLATE_PATH
DEFAULT_GOLDEN_ANSWER_OUTPUT = DEFAULT_GOLDEN_ANSWER_JSON
# 独立 quality-gate helper 的历史 P4 score fixture 路径，不是仓库级默认输出根。
DEFAULT_QUALITY_GATE_SCORE = Path(
    "reports/extraction-snapshots/p4-s3b-004393-controller-final-score/score.json"
)
DEFAULT_GOLDEN_READINESS_PREFLIGHT_RUN_ID = "golden-readiness-preflight-20260529"
DEFAULT_GOLDEN_READINESS_PREFLIGHT_OUTPUT_DIR = (
    DEFAULT_GOLDEN_ANSWER_JSON.parent.parent
    / "golden-readiness-preflight"
    / DEFAULT_GOLDEN_READINESS_PREFLIGHT_RUN_ID
)
_LLM_PROGRESS_PREFIX = "LLM progress:"
_LLM_PROGRESS_HEARTBEAT_INTERVAL_SECONDS = 30.0
_LLM_PROGRESS_THREAD_JOIN_SECONDS = 2.0
_LLM_PROGRESS_THREAD_POLL_SECONDS = 1.0
_LLM_PROGRESS_SAFE_VALUE_MAX_LENGTH = 80
_HOST_EVENT_RUN_STARTED = "run_started"
_HOST_EVENT_PHASE_STARTED = "phase_started"
_HOST_EVENT_PHASE_COMPLETED = "phase_completed"
_HOST_STATUS_SUCCEEDED = "succeeded"
_HOST_STATUS_FAILED = "failed"
_HOST_STATUS_CANCELLED = "cancelled"
_HOST_STATUS_DEADLINE_EXCEEDED = "deadline_exceeded"
_LLM_PROGRESS_FORBIDDEN_VALUE_PARTS = (
    "api_key",
    "authorization",
    "bearer",
    "cookie",
    "secret_key",
    "access_key",
    "system_prompt",
    "user_prompt",
    "prompt",
    "draft_markdown",
    "raw_response",
    "provider_response",
    "provider body",
    "raw audit",
    "model_name",
    "header",
)


def _llm_progress_auto_enabled() -> bool:
    """判断自动模式下是否启用 LLM progress。

    Args:
        无。

    Returns:
        `True` 表示当前 stderr 是 TTY，应启用交互式 progress。

    Raises:
        无显式抛出。
    """

    return sys.stderr.isatty()


def _resolve_llm_progress_enabled(llm_progress: bool | None) -> bool:
    """解析 LLM progress CLI 开关。

    Args:
        llm_progress: CLI 传入的三态开关；`None` 表示自动。

    Returns:
        `True` 表示启用 stderr progress。

    Raises:
        无显式抛出。
    """

    if llm_progress is True:
        return True
    if llm_progress is False:
        return False
    return _llm_progress_auto_enabled()


def _progress_scalar(value: object) -> str:
    """把 progress allowlist 值格式化为安全短标量。

    Args:
        value: Host event 中的 allowlist 字段值。

    Returns:
        可写入 stderr 的短字符串；缺失值返回 `none`。

    Raises:
        ValueError: 当值疑似包含 secret、prompt、raw response 或复杂 payload 时抛出。
    """

    if value is None:
        return "none"
    if isinstance(value, bool):
        text = "true" if value else "false"
    elif isinstance(value, int | float):
        text = str(value)
    else:
        text = str(value)
    lowered = text.lower()
    if any(part in lowered for part in _LLM_PROGRESS_FORBIDDEN_VALUE_PARTS):
        raise ValueError("progress value contains forbidden diagnostic fragment")
    text = " ".join(text.split())
    if len(text) > _LLM_PROGRESS_SAFE_VALUE_MAX_LENGTH:
        text = text[: _LLM_PROGRESS_SAFE_VALUE_MAX_LENGTH - 3].rstrip() + "..."
    return text or "none"


class _LLMProgressReporter:
    """CLI-owned 安全 LLM progress reporter。

    Reporter 只消费 Host 通用事件，维护当前 phase 状态，并把 allowlist
    字段写入 stderr。任何 reporter 内部异常都会关闭 progress，不影响 Host
    终态、stdout 或 CLI fail-closed 处理。
    """

    def __init__(
        self,
        *,
        enabled: bool,
        heartbeat_interval_seconds: float = _LLM_PROGRESS_HEARTBEAT_INTERVAL_SECONDS,
    ) -> None:
        """初始化 progress reporter。

        Args:
            enabled: 是否启用 progress 输出。
            heartbeat_interval_seconds: heartbeat 最小间隔秒数。

        Returns:
            无返回值。

        Raises:
            ValueError: heartbeat 间隔小于 30 秒时抛出。
        """

        if heartbeat_interval_seconds < _LLM_PROGRESS_HEARTBEAT_INTERVAL_SECONDS:
            raise ValueError("LLM progress heartbeat interval must be at least 30 seconds")
        self.enabled = enabled
        self._heartbeat_interval_seconds = heartbeat_interval_seconds
        self._stop_event = threading.Event()
        self._lock = threading.Lock()
        self._current_phase: str | None = None
        self._current_chapter_id: int | None = None
        self._current_attempt: int | None = None
        self._phase_started_monotonic: float | None = None
        self._last_heartbeat_monotonic: float | None = None
        self._terminal_emitted = False
        self._sink_failed = False
        self._thread: threading.Thread | None = None

    @property
    def event_sink(self) -> Callable[[object], None]:
        """返回传给 Service hosted LLM 用例的 no-raise event sink。

        Args:
            无。

        Returns:
            通用事件接收函数。

        Raises:
            无显式抛出；内部异常会被 sink wrapper 捕获。
        """

        return self.handle_event

    @property
    def sink_failed(self) -> bool:
        """返回 progress sink 是否已经失败。

        Args:
            无。

        Returns:
            `True` 表示 reporter 已关闭后续 progress 输出。

        Raises:
            无显式抛出。
        """

        with self._lock:
            return self._sink_failed

    def start(self) -> None:
        """启动 heartbeat 线程。

        Args:
            无。

        Returns:
            无返回值。

        Raises:
            无显式抛出；禁用 progress 时不启动线程。
        """

        if not self.enabled:
            return
        with self._lock:
            if self._thread is not None:
                return
            self._stop_event.clear()
            self._thread = threading.Thread(
                target=self._heartbeat_loop,
                name="fund-agent-llm-progress",
                daemon=True,
            )
            self._thread.start()

    def stop(self) -> None:
        """停止 heartbeat 线程并做有界 join。

        Args:
            无。

        Returns:
            无返回值。

        Raises:
            无显式抛出。
        """

        self._stop_event.set()
        thread = self._thread
        if thread is not None and thread.is_alive():
            thread.join(timeout=_LLM_PROGRESS_THREAD_JOIN_SECONDS)

    def handle_event(self, event: object) -> None:
        """处理通用事件并输出即时 progress。

        Args:
            event: Service/Host 已提交的安全事件。

        Returns:
            无返回值。

        Raises:
            无显式抛出；所有异常都会被捕获并关闭后续 progress。
        """

        if not self.enabled:
            return
        try:
            self._handle_event(event)
        except Exception:  # noqa: BLE001 - progress 失败不能影响 Host/CLI 主流程。
            self._mark_sink_failed()

    def emit_terminal(self, hosted_result: FundLLMHostedRunResult) -> None:
        """在 Host run 返回后输出 terminal progress 行。

        Args:
            hosted_result: Service 投影后的 Host run 终态结果。

        Returns:
            无返回值。

        Raises:
            无显式抛出；输出失败只关闭 progress。
        """

        if not self.enabled:
            return
        try:
            event_name = _terminal_progress_event_name(hosted_result)
            if event_name is None:
                return
            with self._lock:
                if self._sink_failed:
                    return
                self._terminal_emitted = True
                self._current_phase = None
                self._current_chapter_id = None
                self._current_attempt = None
                self._phase_started_monotonic = None
                self._stop_event.set()
            self.stop()
            self._safe_echo(
                (
                    f"{_LLM_PROGRESS_PREFIX} run_terminal "
                    f"run_id={_progress_scalar(hosted_result.host_run_id)} "
                    f"event={event_name} "
                    f"elapsed_ms={_progress_scalar(hosted_result.host_elapsed_ms)}"
                )
            )
        except Exception:  # noqa: BLE001 - terminal progress 失败不能覆盖原终态。
            self._mark_sink_failed()

    def _heartbeat_tick(self, now_monotonic: float | None = None) -> bool:
        """执行一次确定性 heartbeat 判定。

        Args:
            now_monotonic: 可选 monotonic 时间；测试可注入固定值。

        Returns:
            `True` 表示本次输出了 `still_running` 行。

        Raises:
            无显式抛出；输出失败只关闭 progress 并返回 `False`。
        """

        if not self.enabled:
            return False
        now = time.monotonic() if now_monotonic is None else now_monotonic
        try:
            with self._lock:
                if (
                    self._stop_event.is_set()
                    or self._terminal_emitted
                    or self._sink_failed
                    or self._current_phase is None
                    or self._phase_started_monotonic is None
                ):
                    return False
                if (
                    self._last_heartbeat_monotonic is not None
                    and now - self._last_heartbeat_monotonic
                    < self._heartbeat_interval_seconds
                ):
                    return False
                phase = self._current_phase
                chapter_id = self._current_chapter_id
                attempt = self._current_attempt
                elapsed_ms = max(0, int((now - self._phase_started_monotonic) * 1000))
                self._last_heartbeat_monotonic = now
            self._safe_echo(
                (
                    f"{_LLM_PROGRESS_PREFIX} still_running "
                    f"phase={_progress_scalar(phase)} "
                    f"chapter_id={_progress_scalar(chapter_id)} "
                    f"attempt={_progress_scalar(attempt)} "
                    f"elapsed_ms={_progress_scalar(elapsed_ms)}"
                )
            )
            return True
        except Exception:  # noqa: BLE001 - heartbeat 失败不能影响主流程。
            self._mark_sink_failed()
            return False

    def _handle_event(self, event: object) -> None:
        """处理单个通用事件的状态转移。

        Args:
            event: Service/Host 已提交事件。

        Returns:
            无返回值。

        Raises:
            ValueError: progress 值不满足安全输出契约时抛出。
        """

        event_type = _host_event_type_name(event)
        if event_type == _HOST_EVENT_RUN_STARTED:
            self._safe_echo(
                (
                    f"{_LLM_PROGRESS_PREFIX} run_started "
                    f"run_id={_progress_scalar(getattr(event, 'run_id', None))} "
                    f"timeout_seconds={_progress_scalar(_event_value(event, 'timeout_seconds'))}"
                )
            )
            return
        if event_type == _HOST_EVENT_PHASE_STARTED:
            self._handle_phase_started(event)
            return
        if event_type == _HOST_EVENT_PHASE_COMPLETED:
            self._handle_phase_completed(event)

    def _handle_phase_started(self, event: object) -> None:
        """记录 phase started 状态并输出 progress 行。

        Args:
            event: Service/Host phase started 事件。

        Returns:
            无返回值。

        Raises:
            ValueError: progress 值不满足安全输出契约时抛出。
        """

        phase = _event_value(event, "phase")
        chapter_id = _event_value(event, "chapter_id")
        attempt = _event_value(event, "attempt")
        with self._lock:
            if self._sink_failed or self._terminal_emitted:
                return
            self._current_phase = _progress_scalar(phase)
            self._current_chapter_id = _optional_int(chapter_id)
            self._current_attempt = _optional_int(attempt)
            self._phase_started_monotonic = time.monotonic()
            self._last_heartbeat_monotonic = None
        self._safe_echo(
            (
                f"{_LLM_PROGRESS_PREFIX} phase_started "
                f"phase={_progress_scalar(phase)} "
                f"chapter_id={_progress_scalar(chapter_id)} "
                f"attempt={_progress_scalar(attempt)}"
            )
        )

    def _handle_phase_completed(self, event: object) -> None:
        """记录 phase completed 状态并输出 progress 行。

        Args:
            event: Service/Host phase completed 事件。

        Returns:
            无返回值。

        Raises:
            ValueError: progress 值不满足安全输出契约时抛出。
        """

        phase = _event_value(event, "phase")
        chapter_id = _event_value(event, "chapter_id")
        attempt = _event_value(event, "attempt")
        elapsed_ms = _event_value(event, "elapsed_ms")
        with self._lock:
            if self._sink_failed or self._terminal_emitted:
                return
            if self._current_phase == _progress_scalar(phase):
                self._current_phase = None
                self._current_chapter_id = None
                self._current_attempt = None
                self._phase_started_monotonic = None
                self._last_heartbeat_monotonic = None
        self._safe_echo(
            (
                f"{_LLM_PROGRESS_PREFIX} phase_completed "
                f"phase={_progress_scalar(phase)} "
                f"chapter_id={_progress_scalar(chapter_id)} "
                f"attempt={_progress_scalar(attempt)} "
                f"elapsed_ms={_progress_scalar(elapsed_ms)}"
            )
        )

    def _heartbeat_loop(self) -> None:
        """后台 heartbeat 循环。

        Args:
            无。

        Returns:
            无返回值。

        Raises:
            无显式抛出；内部异常会关闭 progress。
        """

        while not self._stop_event.wait(_LLM_PROGRESS_THREAD_POLL_SECONDS):
            self._heartbeat_tick()

    def _safe_echo(self, line: str) -> None:
        """把 progress 行写入 stderr。

        Args:
            line: 已格式化的 progress 行。

        Returns:
            无返回值。

        Raises:
            Exception: `typer.echo` 底层写入异常原样抛出，由调用方捕获。
        """

        typer.echo(line, err=True)

    def _mark_sink_failed(self) -> None:
        """标记 progress sink 失败并关闭后续输出。

        Args:
            无。

        Returns:
            无返回值。

        Raises:
            无显式抛出。
        """

        with self._lock:
            self._sink_failed = True
            self._current_phase = None
            self._current_chapter_id = None
            self._current_attempt = None
            self._phase_started_monotonic = None
            self._last_heartbeat_monotonic = None
            self._stop_event.set()


def _optional_int(value: object) -> int | None:
    """把 Host progress 诊断值转换为可选整数。

    Args:
        value: Host event 诊断值。

    Returns:
        整数值；缺失时返回 `None`。

    Raises:
        ValueError: 当值无法安全转换为整数时抛出。
    """

    if value is None:
        return None
    if isinstance(value, bool):
        raise ValueError("progress int field cannot be bool")
    return int(value)


def _host_event_type_name(event: object) -> str:
    """读取通用事件类型名称。

    Args:
        event: 任意 duck-typed event 对象。

    Returns:
        event_type 的 value 或字符串形式；缺失时返回空字符串。

    Raises:
        无显式抛出。
    """

    event_type = getattr(event, "event_type", None)
    if event_type is None:
        return ""
    event_type_value = getattr(event_type, "value", None)
    if event_type_value is not None:
        return str(event_type_value)
    return str(event_type)


def _event_value(event: object, name: str) -> object:
    """从 duck-typed event 属性或 diagnostics 中读取 progress 字段。

    Args:
        event: 任意 duck-typed event 对象。
        name: 字段名。

    Returns:
        字段值；缺失时返回 `None`。

    Raises:
        无显式抛出。
    """

    direct_value = getattr(event, name, None)
    if direct_value is not None:
        return direct_value
    diagnostics = getattr(event, "diagnostics", None)
    if isinstance(diagnostics, Mapping):
        return diagnostics.get(name)
    return None


def _terminal_progress_event_name(hosted_result: FundLLMHostedRunResult) -> str | None:
    """把 Host 终态映射为 progress terminal event 名称。

    Args:
        hosted_result: Service 投影后的 Host run 结果。

    Returns:
        `run_completed` / `run_failed` / `run_cancelled`；非可展示终态返回 `None`。

    Raises:
        无显式抛出。
    """

    if hosted_result.host_status == _HOST_STATUS_SUCCEEDED:
        return "run_completed"
    if hosted_result.host_status == _HOST_STATUS_FAILED:
        return "run_failed"
    if hosted_result.host_status in {
        _HOST_STATUS_CANCELLED,
        _HOST_STATUS_DEADLINE_EXCEEDED,
    }:
        return "run_cancelled"
    return None


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
    use_llm: Annotated[
        bool,
        typer.Option("--use-llm", help="显式启用 Route C LLM 分章写作路径"),
    ] = False,
    llm_progress: Annotated[
        bool | None,
        typer.Option(
            "--llm-progress/--no-llm-progress",
            help="控制 --use-llm 安全 stderr progress；默认仅 TTY 启用",
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
        use_llm: 是否显式启用 Route C LLM 分章写作路径。
        llm_progress: 是否为 `--use-llm` 启用安全 stderr progress；`None` 表示自动。

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
        command_source="analyze",
    )
    try:
        if use_llm:
            progress_enabled = _resolve_llm_progress_enabled(llm_progress)
            reporter = _LLMProgressReporter(enabled=progress_enabled)
            hosted_result: FundLLMHostedRunResult | None = None
            try:
                reporter.start()
                hosted_result = FundAnalysisService().analyze_with_llm_hosted(
                    request,
                    event_sink=reporter.event_sink,
                )
            finally:
                reporter.stop()
            if hosted_result is None:
                raise RuntimeError("LLM Host run did not return a result")
            reporter.emit_terminal(hosted_result)
            if (
                hosted_result.host_status != _HOST_STATUS_SUCCEEDED
                or hosted_result.analysis_result is None
                or not hosted_result.host_operation_result_present
            ):
                if hosted_result.analysis_result is not None:
                    _write_incomplete_llm_artifacts_for_cli(
                        hosted_result.analysis_result,
                        host_run_id=hosted_result.host_run_id,
                    )
                    typer.echo(
                        _hosted_llm_incomplete_message(
                            hosted_result.analysis_result,
                            hosted_result,
                        ),
                        err=True,
                    )
                    raise typer.Exit(code=1)
                typer.echo(_host_run_failed_message(hosted_result), err=True)
                raise typer.Exit(code=1)
            result = hosted_result.analysis_result
        else:
            result = asyncio.run(FundAnalysisService().analyze(request))
    except LLMProviderConfigError as exc:
        typer.echo(f"LLM provider 配置错误：{exc}", err=True)
        raise typer.Exit(code=1) from exc
    except LLMProviderConstructionError as exc:
        typer.echo(f"LLM provider 构造失败：{exc}", err=True)
        raise typer.Exit(code=1) from exc
    except QualityGateNotRunBlockedError as exc:
        _echo_quality_gate_not_run_blocked(exc)
        raise typer.Exit(code=2) from exc
    except QualityGateBlockedError as exc:
        _echo_quality_gate_blocked(exc)
        raise typer.Exit(code=2) from exc
    except typer.Exit:
        raise
    except Exception as exc:
        typer.echo(f"分析失败：{exc}", err=True)
        raise typer.Exit(code=1) from exc
    if use_llm and result.final_assembly_result.report_markdown is None:
        _write_incomplete_llm_artifacts_for_cli(result, host_run_id=None)
        typer.echo(_llm_incomplete_message(result), err=True)
        raise typer.Exit(code=1)
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
        command_source="checklist",
    )
    try:
        result = asyncio.run(FundAnalysisService().checklist(request))
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


@app.command("analyze-annual-period")
def analyze_annual_period(
    fund_code: Annotated[str, typer.Argument(help="基金代码，如 110011")],
    target_year: Annotated[
        int,
        typer.Option(
            "--target-year",
            help="必需当前年报年份；例如 2025 表示当前报告年",
        ),
    ] = 2025,
    start_year: Annotated[
        int,
        typer.Option(
            "--start-year",
            help="最早 optional prior 年报年份；例如 2021 与 --target-year 2025 构成 2021-2025",
        ),
    ] = 2021,
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
                "估值状态：low/fair/high/unavailable；不传则沿用单年 analyze 自动估值行为"
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
        bool, typer.Option("--force-refresh", help="统一强制刷新所有请求年份")
    ] = False,
    quality_gate_policy: Annotated[
        str,
        typer.Option("--quality-gate-policy", help="质量 gate 策略 off/warn/block"),
    ] = "block",
) -> None:
    """对指定基金执行 2021-2025 等有界多年年报分析。

    Args:
        fund_code: 基金代码。
        target_year: 当前必需年报年份。
        start_year: 最早 optional prior 年报年份。
        investment_amount: 压力测试投入金额。
        max_tolerable_loss_rate: 最大可承受亏损比例。
        valuation_state: 估值状态。
        thermometer_cache_dir: 自动温度计缓存目录。
        user_money_horizon_years: 用户资金不用年限。
        force_refresh: 是否统一强制刷新。
        quality_gate_policy: quality gate 策略。

    Returns:
        无返回值，当前年份报告和多年证据摘要写入 stdout。

    Raises:
        typer.Exit: 分析失败时以非零状态退出。
    """

    try:
        request = MultiYearAnnualAnalysisRequest(
            fund_code=fund_code,
            target_year=target_year,
            start_year=start_year,
            investment_amount=investment_amount,
            max_tolerable_loss_rate=max_tolerable_loss_rate,
            valuation_state=_valuation_state(valuation_state),
            thermometer_cache_dir=thermometer_cache_dir,
            user_money_horizon_years=user_money_horizon_years,
            force_refresh=force_refresh,
            quality_gate_policy=_quality_gate_policy(quality_gate_policy),
        )
        result = asyncio.run(FundAnalysisService().analyze_multi_year_annual(request))
    except QualityGateNotRunBlockedError as exc:
        _echo_quality_gate_not_run_blocked(exc)
        raise typer.Exit(code=2) from exc
    except QualityGateBlockedError as exc:
        _echo_quality_gate_blocked(exc)
        raise typer.Exit(code=2) from exc
    except typer.BadParameter as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(code=2) from exc
    except Exception as exc:
        typer.echo(f"多年年报分析失败：{exc}", err=True)
        raise typer.Exit(code=1) from exc
    _echo_quality_gate_summary(result.current_year_result)
    _echo_multi_year_annual_summary(result)
    typer.echo("")
    typer.echo(result.annual_period_report.report_markdown, nl=False)


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
            ThermometerService().run(
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
            ExtractionSnapshotService().run(
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
        result = ExtractionScoreService().run(
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
            GoldenPrefillService().run(
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
        result = GoldenAnswerService().build(
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
        result = QualityGateService().run(
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


@app.command("golden-readiness-preflight")
def golden_readiness_preflight(
    run_id: Annotated[
        str,
        typer.Option("--run-id", help="preflight 运行 ID"),
    ] = DEFAULT_GOLDEN_READINESS_PREFLIGHT_RUN_ID,
    source_csv: Annotated[
        Path,
        typer.Option("--source-csv", help="精选基金池 CSV 路径"),
    ] = DEFAULT_SELECTED_FUNDS_CSV,
    golden_answer_path: Annotated[
        Path | None,
        typer.Option("--golden-answer-path", help="strict golden answer JSON 路径"),
    ] = DEFAULT_GOLDEN_ANSWER_OUTPUT,
    output_dir: Annotated[
        Path,
        typer.Option("--output-dir", help="preflight 输出目录"),
    ] = DEFAULT_GOLDEN_READINESS_PREFLIGHT_OUTPUT_DIR,
    preflight_input: Annotated[
        Path | None,
        typer.Option("--preflight-input", help="完整 preflight input JSON；production recommended"),
    ] = None,
    selected_pool_path: Annotated[
        Path | None,
        typer.Option("--selected-pool-path", help="selected pool JSON 路径"),
    ] = None,
    coverage_disposition_path: Annotated[
        Path | None,
        typer.Option("--coverage-disposition-path", help="coverage disposition manifest JSON 路径"),
    ] = None,
    fixture_promotion_state_path: Annotated[
        Path | None,
        typer.Option("--fixture-promotion-state-path", help="fixture promotion state JSON 路径"),
    ] = None,
    fund_artifact: Annotated[
        list[str] | None,
        typer.Option(
            "--fund-artifact",
            help="shortcut: fund_code::report_year::snapshot_path::score_path::quality_gate_path",
        ),
    ] = None,
) -> None:
    """生成只读 golden readiness preflight JSON / Markdown。

    Args:
        run_id: preflight 运行 ID。
        source_csv: 精选基金池 CSV 路径。
        golden_answer_path: strict golden answer JSON 路径。
        output_dir: 输出目录。
        preflight_input: 完整 preflight input JSON。
        selected_pool_path: selected pool JSON 路径。
        coverage_disposition_path: coverage disposition manifest JSON 路径。
        fixture_promotion_state_path: fixture promotion state JSON 路径。
        fund_artifact: shortcut artifact 输入。

    Returns:
        无返回值，产物路径写入 stdout。

    Raises:
        typer.Exit: 参数非法以 2 退出；IO/JSON/schema 失败以 1 退出。
    """

    try:
        parsed_fund_artifacts = tuple(
            _parse_preflight_fund_artifact(value) for value in (fund_artifact or [])
        )
        _validate_preflight_cli_conflicts(
            preflight_input=preflight_input,
            fund_artifacts=parsed_fund_artifacts,
            selected_pool_path=selected_pool_path,
            coverage_disposition_path=coverage_disposition_path,
            fixture_promotion_state_path=fixture_promotion_state_path,
        )
        result = GoldenReadinessPreflightService().run(
            GoldenReadinessPreflightRequest(
                source_csv=source_csv,
                output_dir=output_dir,
                run_id=run_id,
                fund_artifacts=parsed_fund_artifacts,
                golden_answer_path=golden_answer_path,
                fixture_promotion_state_path=fixture_promotion_state_path,
                coverage_disposition_path=coverage_disposition_path,
                preflight_input_path=preflight_input,
                selected_pool_path=selected_pool_path,
            )
        )
    except typer.BadParameter as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(code=2) from exc
    except ValueError as exc:
        typer.echo(f"golden readiness preflight 参数错误：{exc}", err=True)
        raise typer.Exit(code=2) from exc
    except Exception as exc:
        typer.echo(f"golden readiness preflight 生成失败：{exc}", err=True)
        raise typer.Exit(code=1) from exc
    typer.echo(f"preflight_json: {result.json_path}")
    typer.echo(f"preflight_md: {result.markdown_path}")
    typer.echo(f"overall_status: {result.overall_status}")


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


def _hosted_llm_incomplete_message(result, hosted_result: FundLLMHostedRunResult) -> str:  # type: ignore[no-untyped-def]
    """生成带 Host run 摘要的 LLM incomplete 安全错误消息。

    Args:
        result: Service 返回的 typed LLM 分析结果。
        hosted_result: Service 投影后的 Host 托管 run 终态结果。

    Returns:
        LLM incomplete 摘要和 Host run 安全摘要。

    Raises:
        无显式抛出。
    """

    return f"{_llm_incomplete_message(result)}; {_host_run_failed_message(hosted_result)}"


def _write_incomplete_llm_artifacts_for_cli(
    result: object,
    *,
    host_run_id: str | None,
) -> LLMRunArtifactWriteResult | None:
    """为 CLI typed incomplete LLM 结果写入本地诊断 artifact。

    Args:
        result: Host/Service 返回的 operation result；只有 typed LLM incomplete 结果会写入。
        host_run_id: Host run id；Host 成功但总装 incomplete 的兜底路径可为 `None`。

    Returns:
        写入结果；非 typed incomplete 或写入失败时返回 `None`。

    Raises:
        无显式抛出；写入失败只输出安全 warning 并保持原 fail-closed 流程。
    """

    if not isinstance(result, FundLLMAnalysisResult):
        return None
    if result.final_assembly_result.report_markdown is not None:
        return None
    try:
        artifact_result = write_llm_incomplete_run_artifacts(
            result,
            host_run_id=host_run_id,
        )
    except Exception as exc:  # noqa: BLE001 - artifact 失败不得覆盖原始 fail-closed 结果。
        typer.echo(
            f"LLM incomplete diagnostic artifact warning: write_failed type={type(exc).__name__}",
            err=True,
        )
        return None
    typer.echo(
        f"LLM incomplete diagnostic artifacts: {artifact_result.manifest_path}",
        err=True,
    )
    return artifact_result


def _host_run_failed_message(hosted_result: FundLLMHostedRunResult) -> str:
    """生成 Host run fail-closed 安全错误消息。

    Args:
        hosted_result: Service 投影后的 Host run 终态结果。

    Returns:
        仅包含 run state、安全分类和错误类型的 stderr 消息。

    Raises:
        无显式抛出。
    """

    timeout_classification = hosted_result.host_timeout_classification or "none"
    diagnostics = hosted_result.host_safe_diagnostics
    error_type = diagnostics.get("error_type", "none")
    cancel_reason = diagnostics.get("cancel_reason", "none")
    return (
        "LLM Host run 未完成："
        f"run_id={hosted_result.host_run_id}; "
        f"status={hosted_result.host_status}; "
        f"timeout_classification={timeout_classification}; "
        f"cancel_reason={cancel_reason}; "
        f"error_type={error_type}; "
        f"elapsed_ms={hosted_result.host_elapsed_ms}"
    )


def _llm_incomplete_message(result) -> str:  # type: ignore[no-untyped-def]
    """生成 LLM 分析未完成错误消息。

    Args:
        result: `FundLLMAnalysisResult` 或具备同名属性的测试替身。

    Returns:
        以 `LLM 分析未完成：` 开头的错误消息。

    Raises:
        无显式抛出。
    """

    final_assembly_result = result.final_assembly_result
    issues = getattr(final_assembly_result, "issues", ())
    issue_reasons = ", ".join(getattr(issue, "reason", str(issue)) for issue in issues)
    if not issue_reasons:
        issue_reasons = "no final assembly issue recorded"
    first_failed = _first_failed_chapter_summary(result.llm_orchestration_result)
    return (
        "LLM 分析未完成："
        f"orchestration_status={result.llm_orchestration_result.status}, "
        f"final_assembly_status={final_assembly_result.status}, "
        f"issues={issue_reasons}, "
        f"{first_failed}, "
        f"{_chapter_matrix_summary(result.llm_orchestration_result)}"
    )


def _first_failed_chapter_summary(orchestration_result) -> str:  # type: ignore[no-untyped-def]
    """提取首个未 accepted 章节的安全摘要。

    Args:
        orchestration_result: `ChapterOrchestrationResult` 或同名测试替身。

    Returns:
        `first_failed_*` 摘要；没有章节结果时返回 `first_failed_chapter=none`。

    Raises:
        无显式抛出。
    """

    chapter_results = getattr(orchestration_result, "chapter_results", ())
    for chapter_result in chapter_results:
        status = getattr(chapter_result, "status", None)
        if status == "accepted":
            continue
        chapter_id = getattr(chapter_result, "chapter_id", "unknown")
        stop_reason = getattr(chapter_result, "stop_reason", "unknown")
        failure_category = getattr(chapter_result, "failure_category", None)
        if failure_category is None:
            failure_category = "unknown"
        failure_subcategory = getattr(chapter_result, "failure_subcategory", None)
        if failure_subcategory is None:
            failure_subcategory = "unknown"
        runtime_summary = _first_failed_runtime_summary(chapter_result)
        return (
            f"first_failed_chapter_id={chapter_id}, "
            f"first_failed_status={status}, "
            f"first_failed_stop_reason={stop_reason}, "
            f"first_failed_category={failure_category}, "
            f"first_failed_subcategory={failure_subcategory}, "
            f"{runtime_summary}"
        )
    return "first_failed_chapter=none"


def _chapter_matrix_summary(orchestration_result) -> str:  # type: ignore[no-untyped-def]
    """提取全部章节的安全矩阵摘要。

    Args:
        orchestration_result: `ChapterOrchestrationResult` 或同名测试替身。

    Returns:
        仅含 chapter_id/status/stop_reason/failure_category/failure_subcategory 的摘要。

    Raises:
        无显式抛出。
    """

    rows: list[str] = []
    for chapter_result in getattr(orchestration_result, "chapter_results", ()):
        chapter_id = getattr(chapter_result, "chapter_id", "unknown")
        status = getattr(chapter_result, "status", "unknown")
        stop_reason = getattr(chapter_result, "stop_reason", "unknown")
        failure_category = getattr(chapter_result, "failure_category", None) or "unknown"
        failure_subcategory = getattr(chapter_result, "failure_subcategory", None) or "unknown"
        rows.append(
            f"{chapter_id}:{status}/{stop_reason}/{failure_category}/{failure_subcategory}"
        )
    if not rows:
        return "chapter_matrix=none"
    return f"chapter_matrix={';'.join(rows)}"


def _first_failed_runtime_summary(chapter_result) -> str:  # type: ignore[no-untyped-def]
    """提取首个失败章节 runtime 安全摘要。

    Args:
        chapter_result: `ChapterRunResult` 或同名测试替身。

    Returns:
        只含 allowlisted scalar 的 `first_failed_runtime_*` 摘要。

    Raises:
        无显式抛出。
    """

    diagnostics = _chapter_runtime_diagnostics(chapter_result)
    operation = _runtime_operation(diagnostics)
    observed_attempts = _runtime_provider_attempt_count(diagnostics)
    max_attempts = _runtime_provider_max_attempts(diagnostics)
    runtime_category = _runtime_provider_category(diagnostics)
    elapsed_ms_max = _runtime_elapsed_ms_max(diagnostics)
    prompt_chars = _runtime_prompt_chars(diagnostics)
    approx_prompt_tokens = _runtime_scalar_max(diagnostics, "approx_prompt_tokens")
    timeout_root_cause_hint = _runtime_first_scalar(diagnostics, "timeout_root_cause_hint")
    max_output_chars = _runtime_scalar_max(diagnostics, "max_output_chars")
    return (
        f"first_failed_runtime_operation={operation}, "
        f"first_failed_provider_attempts={observed_attempts}/{max_attempts}, "
        f"first_failed_provider_runtime_category={runtime_category}, "
        f"first_failed_elapsed_ms_max={elapsed_ms_max}, "
        f"first_failed_prompt_chars={prompt_chars}, "
        f"first_failed_approx_prompt_tokens={approx_prompt_tokens}, "
        f"first_failed_timeout_root_cause_hint={timeout_root_cause_hint}, "
        f"first_failed_max_output_chars={max_output_chars}"
    )


def _chapter_runtime_diagnostics(chapter_result) -> tuple[object, ...]:  # type: ignore[no-untyped-def]
    """收集章节级和 attempt 级 runtime diagnostic。

    Args:
        chapter_result: `ChapterRunResult` 或同名测试替身。

    Returns:
        runtime diagnostic tuple。

    Raises:
        无显式抛出。
    """

    diagnostics = list(getattr(chapter_result, "runtime_diagnostics", ()))
    for attempt in getattr(chapter_result, "attempts", ()):
        diagnostics.extend(getattr(attempt, "runtime_diagnostics", ()))
    return tuple(diagnostics)


def _runtime_operation(diagnostics: tuple[object, ...]) -> object:
    """读取首条 runtime operation。

    Args:
        diagnostics: runtime diagnostic tuple。

    Returns:
        operation 或 `unknown`。

    Raises:
        无显式抛出。
    """

    if not diagnostics:
        return "unknown"
    return getattr(diagnostics[0], "operation", None) or "unknown"


def _runtime_provider_attempt_count(diagnostics: tuple[object, ...]) -> int:
    """统计 observed provider attempts。

    Args:
        diagnostics: runtime diagnostic tuple。

    Returns:
        带 provider_attempt_index 的诊断数量。

    Raises:
        无显式抛出。
    """

    return sum(
        1
        for diagnostic in diagnostics
        if getattr(diagnostic, "provider_attempt_index", None) is not None
    )


def _runtime_provider_max_attempts(diagnostics: tuple[object, ...]) -> object:
    """读取 provider max attempts。

    Args:
        diagnostics: runtime diagnostic tuple。

    Returns:
        最大 attempts 或 `unknown`。

    Raises:
        无显式抛出。
    """

    values = tuple(
        getattr(diagnostic, "provider_max_attempts", None)
        for diagnostic in diagnostics
        if getattr(diagnostic, "provider_max_attempts", None) is not None
    )
    if not values:
        return "unknown"
    return max(values)


def _runtime_provider_category(diagnostics: tuple[object, ...]) -> object:
    """读取首个 provider runtime category。

    Args:
        diagnostics: runtime diagnostic tuple。

    Returns:
        runtime category 或 `unknown`。

    Raises:
        无显式抛出。
    """

    for diagnostic in diagnostics:
        category = getattr(diagnostic, "provider_runtime_category", None)
        if category is not None:
            return category
    return "unknown"


def _runtime_elapsed_ms_max(diagnostics: tuple[object, ...]) -> object:
    """读取 runtime diagnostic 最大 elapsed_ms。

    Args:
        diagnostics: runtime diagnostic tuple。

    Returns:
        最大 elapsed_ms 或 `unknown`。

    Raises:
        无显式抛出。
    """

    values = tuple(
        getattr(diagnostic, "elapsed_ms", None)
        for diagnostic in diagnostics
        if getattr(diagnostic, "elapsed_ms", None) is not None
    )
    if not values:
        return "unknown"
    return max(values)


def _runtime_prompt_chars(diagnostics: tuple[object, ...]) -> object:
    """读取 runtime diagnostic 的最大 prompt 字符总数。

    Args:
        diagnostics: runtime diagnostic tuple。

    Returns:
        system+user prompt chars 或 `unknown`。

    Raises:
        无显式抛出。
    """

    values: list[int] = []
    for diagnostic in diagnostics:
        system_prompt_chars = getattr(diagnostic, "system_prompt_chars", None)
        user_prompt_chars = getattr(diagnostic, "user_prompt_chars", None)
        if isinstance(system_prompt_chars, int) and isinstance(user_prompt_chars, int):
            values.append(system_prompt_chars + user_prompt_chars)
    if not values:
        return "unknown"
    return max(values)


def _runtime_scalar_max(diagnostics: tuple[object, ...], field_name: str) -> object:
    """读取 runtime diagnostic 某个整型标量最大值。

    Args:
        diagnostics: runtime diagnostic tuple。
        field_name: 字段名。

    Returns:
        最大整型值或 `unknown`。

    Raises:
        无显式抛出。
    """

    values = tuple(
        getattr(diagnostic, field_name, None)
        for diagnostic in diagnostics
        if isinstance(getattr(diagnostic, field_name, None), int)
    )
    if not values:
        return "unknown"
    return max(values)


def _runtime_first_scalar(diagnostics: tuple[object, ...], field_name: str) -> object:
    """读取 runtime diagnostic 首个非空标量。

    Args:
        diagnostics: runtime diagnostic tuple。
        field_name: 字段名。

    Returns:
        首个非空值或 `unknown`。

    Raises:
        无显式抛出。
    """

    for diagnostic in diagnostics:
        value = getattr(diagnostic, field_name, None)
        if value is not None:
            return value
    return "unknown"


def _parse_preflight_fund_artifact(value: str) -> FundArtifactInput:
    """解析 golden-readiness-preflight `--fund-artifact` shortcut。

    Args:
        value: `fund_code::report_year::snapshot_path::score_path::quality_gate_path` 字符串。

    Returns:
        fund artifact input。

    Raises:
        typer.BadParameter: 字段数、基金代码或年份非法时抛出。
    """

    parts = value.split("::")
    if len(parts) != 5:
        raise typer.BadParameter(
            "--fund-artifact 格式必须是 "
            "fund_code::report_year::snapshot_path::score_path::quality_gate_path"
        )
    fund_code, report_year_text, snapshot_path, score_path, quality_gate_path = parts
    if len(fund_code) != 6 or not fund_code.isdigit():
        raise typer.BadParameter("--fund-artifact fund_code 必须是 6 位数字")
    try:
        report_year = int(report_year_text)
    except ValueError as exc:
        raise typer.BadParameter("--fund-artifact report_year 必须是整数") from exc
    return FundArtifactInput(
        fund_code=fund_code,
        report_year=report_year,
        snapshot_path=Path(snapshot_path),
        score_path=Path(score_path),
        quality_gate_path=Path(quality_gate_path),
    )


def _validate_preflight_cli_conflicts(
    *,
    preflight_input: Path | None,
    fund_artifacts: tuple[FundArtifactInput, ...],
    selected_pool_path: Path | None,
    coverage_disposition_path: Path | None,
    fixture_promotion_state_path: Path | None,
) -> None:
    """校验 preflight CLI 互斥输入。

    Args:
        preflight_input: 完整 preflight input JSON。
        fund_artifacts: shortcut artifact 输入。
        selected_pool_path: selected pool JSON。
        coverage_disposition_path: coverage disposition manifest JSON。
        fixture_promotion_state_path: fixture promotion state JSON。

    Returns:
        无返回值。

    Raises:
        ValueError: `--preflight-input` 与逐项输入同时出现时抛出。
    """

    if preflight_input is None:
        return
    conflicts: list[str] = []
    if fund_artifacts:
        conflicts.append("--fund-artifact")
    if selected_pool_path is not None:
        conflicts.append("--selected-pool-path")
    if coverage_disposition_path is not None:
        conflicts.append("--coverage-disposition-path")
    if fixture_promotion_state_path is not None:
        conflicts.append("--fixture-promotion-state-path")
    if conflicts:
        raise ValueError(
            "--preflight-input 不能与逐项输入同时使用：" + ", ".join(sorted(conflicts))
        )


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


def _echo_checklist_result(result: FundChecklistResult) -> None:
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


def _echo_multi_year_annual_summary(result: MultiYearAnnualAnalysisResult) -> None:
    """输出多年年报证据摘要。

    Args:
        result: 多年年报分析结果。

    Returns:
        无返回值。

    Raises:
        无显式抛出。
    """

    bundle = result.annual_evidence_bundle
    typer.echo(f"fund_code: {bundle.fund_code}")
    typer.echo(f"target_year: {bundle.target_year}")
    typer.echo(f"canonical_years: {_format_cli_value(bundle.canonical_years)}")
    typer.echo(f"available_years: {_format_cli_value(bundle.available_years)}")
    typer.echo(f"gap_years: {_format_cli_value(bundle.gap_years)}")
    typer.echo(f"fail_closed_years: {_format_cli_value(bundle.fail_closed_years)}")
    typer.echo(f"cross_year_fact_count: {len(bundle.cross_year_facts)}")
    typer.echo(
        "fallback_year_count: "
        f"{_format_cli_value(bundle.fallback_summary.get('fallback_year_count'))}"
    )
    for year in bundle.canonical_years:
        provenance = bundle.source_provenance_by_year.get(year)
        if provenance is None:
            typer.echo(f"source[{year}]: unavailable")
            continue
        typer.echo(
            f"source[{year}]: selected_source={provenance.selected_source} "
            f"source_mode={provenance.source_mode} "
            f"fallback_enabled={_format_cli_value(provenance.fallback_enabled)} "
            f"fallback_used={_format_cli_value(provenance.fallback_used)}"
        )


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
