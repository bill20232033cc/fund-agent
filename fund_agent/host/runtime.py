"""本项目内化的最小 Host runtime governance。

本模块只承载通用运行生命周期、取消、deadline、终态和安全诊断契约。
它不理解基金业务，不导入 Service / Fund，也不依赖外部 Dayu runtime。
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from enum import StrEnum
from typing import Callable, Mapping, TypeVar


_RUN_ID_PREFIX = "host_run_"
_MAX_DIAGNOSTIC_STRING_LENGTH = 240
_FORBIDDEN_DIAGNOSTIC_KEY_PARTS = (
    "api_key",
    "authorization",
    "auth_header",
    "prompt",
    "draft",
    "provider_response",
    "audit_response",
    "raw_response",
    "stdout",
    "stderr",
)

TResult = TypeVar("TResult")
HostRunEventSink = Callable[["HostRunEvent"], None]


class HostRuntimeError(RuntimeError):
    """Host runtime 治理错误。"""


class HostRunStatus(StrEnum):
    """Host run 生命周期状态。"""

    CREATED = "created"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"
    DEADLINE_EXCEEDED = "deadline_exceeded"


class HostCancelReason(StrEnum):
    """Host run 取消原因。"""

    USER_CANCELLED = "user_cancelled"
    RUN_DEADLINE_EXCEEDED = "run_deadline_exceeded"


class HostTimeoutClassification(StrEnum):
    """Host 层 timeout 分类。"""

    RUN_DEADLINE_EXCEEDED = "run_deadline_exceeded"
    PHASE_TIMEOUT = "phase_timeout"
    PROVIDER_RUNTIME_TIMEOUT = "provider_runtime_timeout"


class HostRunEventType(StrEnum):
    """Host run 安全事件类型。"""

    RUN_STARTED = "run_started"
    PHASE_STARTED = "phase_started"
    PHASE_COMPLETED = "phase_completed"
    DIAGNOSTIC_RECORDED = "diagnostic_recorded"
    RUN_COMPLETED = "run_completed"
    RUN_FAILED = "run_failed"
    RUN_CANCELLED = "run_cancelled"


def is_terminal_status(status: HostRunStatus) -> bool:
    """判断 Host run 状态是否为终态。

    Args:
        status: 待判断的 Host run 状态。

    Returns:
        `True` 表示该状态为终态。

    Raises:
        无。
    """

    return status in {
        HostRunStatus.SUCCEEDED,
        HostRunStatus.FAILED,
        HostRunStatus.CANCELLED,
        HostRunStatus.DEADLINE_EXCEEDED,
    }


def _generate_run_id() -> str:
    """生成进程内唯一 Host run ID。"""

    return f"{_RUN_ID_PREFIX}{uuid.uuid4().hex[:16]}"


def _now_utc() -> datetime:
    """返回 timezone-aware UTC 当前时间。"""

    return datetime.now(UTC)


def _elapsed_ms(started_monotonic: float) -> int:
    """根据 monotonic 起点计算毫秒耗时。"""

    return max(0, int((time.monotonic() - started_monotonic) * 1000))


def _normalize_diagnostic_value(value: object) -> object:
    """规范化安全诊断值。

    Args:
        value: 原始诊断值。

    Returns:
        允许进入诊断 payload 的安全标量值。

    Raises:
        HostRuntimeError: 当值类型可能承载非安全复杂 payload 时抛出。
    """

    if value is None or isinstance(value, bool | int | float):
        return value
    if isinstance(value, StrEnum):
        return value.value
    if isinstance(value, str):
        if len(value) <= _MAX_DIAGNOSTIC_STRING_LENGTH:
            return value
        return value[: _MAX_DIAGNOSTIC_STRING_LENGTH - 3].rstrip() + "..."
    raise HostRuntimeError(f"不支持的 Host 安全诊断值类型: {type(value).__name__}")


def build_safe_diagnostics(values: Mapping[str, object]) -> dict[str, object]:
    """构造 Host 安全诊断 payload。

    Args:
        values: 候选诊断键值。键名不得包含 secret / prompt / raw response 等
            禁止片段；值只能是安全标量。

    Returns:
        可用于事件、stderr 摘要或 evidence artifact 的安全诊断字典。

    Raises:
        HostRuntimeError: 当键名或值不符合安全契约时抛出。
    """

    safe: dict[str, object] = {}
    for key, value in values.items():
        normalized_key = str(key)
        lowered = normalized_key.lower()
        if any(part in lowered for part in _FORBIDDEN_DIAGNOSTIC_KEY_PARTS):
            raise HostRuntimeError(f"Host 安全诊断禁止字段: {normalized_key}")
        safe[normalized_key] = _normalize_diagnostic_value(value)
    return safe


@dataclass(slots=True)
class HostCancellationToken:
    """Host run 协作式取消令牌。"""

    _reason: HostCancelReason | None = None

    @property
    def reason(self) -> HostCancelReason | None:
        """返回首次取消原因。"""

        return self._reason

    def cancel(self, reason: HostCancelReason) -> None:
        """触发取消，保留首次取消原因。

        Args:
            reason: 取消原因。

        Returns:
            无返回值。

        Raises:
            无。
        """

        if self._reason is None:
            self._reason = reason

    def is_cancelled(self) -> bool:
        """检查令牌是否已取消。"""

        return self._reason is not None

    def raise_if_cancelled(self) -> None:
        """若已取消则抛出 `HostRuntimeError`。

        Args:
            无。

        Returns:
            无返回值。

        Raises:
            HostRuntimeError: 当令牌已取消时抛出。
        """

        if self._reason is not None:
            raise HostRuntimeError(f"Host run 已取消: {self._reason.value}")


@dataclass(frozen=True, slots=True)
class HostRunContext:
    """Host 传给被托管 operation 的生命周期上下文。"""

    run_id: str
    started_at: datetime
    deadline_at: datetime | None
    timeout_seconds: int | None
    cancellation_token: HostCancellationToken
    _event_recorder: Callable[[HostRunEventType, Mapping[str, object]], None] | None = field(
        default=None,
        repr=False,
        compare=False,
    )

    def deadline_exceeded(self, *, now: datetime | None = None) -> bool:
        """判断当前 run 是否已超过 deadline。

        Args:
            now: 可选当前时间；缺省时使用 UTC 当前时间。

        Returns:
            `True` 表示已超过 deadline。

        Raises:
            无。
        """

        if self.deadline_at is None:
            return False
        current = now or _now_utc()
        return current >= self.deadline_at

    def cancel_if_deadline_exceeded(self, *, now: datetime | None = None) -> bool:
        """若超过 deadline 则触发取消。

        Args:
            now: 可选当前时间；缺省时使用 UTC 当前时间。

        Returns:
            `True` 表示本次检查发现 deadline 已超过。

        Raises:
            无。
        """

        if not self.deadline_exceeded(now=now):
            return False
        self.cancellation_token.cancel(HostCancelReason.RUN_DEADLINE_EXCEEDED)
        return True

    def raise_if_cancelled_or_deadline_exceeded(self) -> None:
        """在 phase 边界检查 deadline 和取消令牌。

        Args:
            无。

        Returns:
            无返回值。

        Raises:
            HostRuntimeError: 当 run 已取消或超过 deadline 时抛出。
        """

        self.cancel_if_deadline_exceeded()
        self.cancellation_token.raise_if_cancelled()

    def record_phase_started(
        self,
        *,
        phase: str,
        chapter_id: int | None = None,
        attempt: int | None = None,
        provider_attempt: int | None = None,
    ) -> None:
        """记录安全 phase_started 事件。

        Args:
            phase: phase 名称，例如 writer / auditor / repair / final_assembly。
            chapter_id: 可选模板章节编号。
            attempt: 可选章节 attempt 序号。
            provider_attempt: 可选 provider attempt 序号。

        Returns:
            无返回值。

        Raises:
            HostRuntimeError: 当诊断字段不符合安全契约时抛出。
        """

        self.record_diagnostic(
            event_type=HostRunEventType.PHASE_STARTED,
            phase=phase,
            chapter_id=chapter_id,
            attempt=attempt,
            provider_attempt=provider_attempt,
        )

    def record_phase_completed(
        self,
        *,
        phase: str,
        chapter_id: int | None = None,
        attempt: int | None = None,
        provider_attempt: int | None = None,
        elapsed_ms: int | None = None,
    ) -> None:
        """记录安全 phase_completed 事件。

        Args:
            phase: phase 名称，例如 writer / auditor / repair / final_assembly。
            chapter_id: 可选模板章节编号。
            attempt: 可选章节 attempt 序号。
            provider_attempt: 可选 provider attempt 序号。
            elapsed_ms: 可选 phase 耗时毫秒。

        Returns:
            无返回值。

        Raises:
            HostRuntimeError: 当诊断字段不符合安全契约时抛出。
        """

        self.record_diagnostic(
            event_type=HostRunEventType.PHASE_COMPLETED,
            phase=phase,
            chapter_id=chapter_id,
            attempt=attempt,
            provider_attempt=provider_attempt,
            elapsed_ms=elapsed_ms,
        )

    def record_diagnostic(
        self,
        *,
        event_type: HostRunEventType = HostRunEventType.DIAGNOSTIC_RECORDED,
        **diagnostics: object,
    ) -> None:
        """记录安全 Host run 诊断事件。

        Args:
            event_type: 要记录的事件类型。
            diagnostics: 仅允许安全标量，不得包含 prompt / draft / raw response / secret。

        Returns:
            无返回值。

        Raises:
            HostRuntimeError: 当诊断字段不符合安全契约时抛出。
        """

        if self._event_recorder is None:
            return
        self._event_recorder(event_type, diagnostics)


@dataclass(frozen=True, slots=True)
class HostRunEvent:
    """Host run 安全事件。"""

    event_type: HostRunEventType
    run_id: str
    created_at: datetime
    diagnostics: Mapping[str, object] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class HostRunResult:
    """Host 托管 operation 的结果。"""

    run_id: str
    status: HostRunStatus
    started_at: datetime
    deadline_at: datetime | None
    completed_at: datetime
    elapsed_ms: int
    operation_result: object | None
    timeout_classification: HostTimeoutClassification | None
    safe_diagnostics: Mapping[str, object]
    events: tuple[HostRunEvent, ...]

    @property
    def is_terminal(self) -> bool:
        """返回当前结果是否为终态结果。"""

        return is_terminal_status(self.status)


class HostRuntimeRunner:
    """进程内 Host runtime runner。

    Runner 只接受同步 operation callable，不管理 asyncio event loop。当前 CLI
    若需要调用 async Service API，必须在 CLI-owned closure 中桥接。
    """

    def run_sync(
        self,
        *,
        operation_name: str,
        operation: Callable[[HostRunContext], TResult],
        timeout_seconds: int | None = None,
        session_id: str | None = None,
        event_sink: HostRunEventSink | None = None,
    ) -> HostRunResult:
        """托管一次同步 operation。

        Args:
            operation_name: 操作名称，仅用于安全诊断，不承载业务语义。
            operation: 被托管的同步 callable。
            timeout_seconds: 可选 run deadline 秒数，必须为正整数。
            session_id: 可选 Host session ID，仅进入安全诊断。
            event_sink: 可选通用事件接收器；Host 提交事件后同步调用。

        Returns:
            HostRunResult。

        Raises:
            ValueError: timeout 非法时抛出。
        """

        if timeout_seconds is not None and timeout_seconds <= 0:
            raise ValueError("timeout_seconds 必须为正整数或 None")

        run_id = _generate_run_id()
        started_at = _now_utc()
        started_monotonic = time.monotonic()
        deadline_at = (
            started_at + timedelta(seconds=timeout_seconds)
            if timeout_seconds is not None
            else None
        )
        events: list[HostRunEvent] = []
        event_sink_errors: list[BaseException] = []
        _commit_event(
            events,
            HostRunEventType.RUN_STARTED,
            run_id=run_id,
            event_sink=event_sink,
            event_sink_errors=event_sink_errors,
            operation_name=operation_name,
            session_id=session_id,
            timeout_seconds=timeout_seconds,
        )
        token = HostCancellationToken()

        def record_event(event_type: HostRunEventType, diagnostics: Mapping[str, object]) -> None:
            """把 operation 内部事件追加到当前 run 事件流。"""

            _commit_event(
                events,
                event_type,
                run_id=run_id,
                event_sink=event_sink,
                event_sink_errors=event_sink_errors,
                **diagnostics,
            )

        context = HostRunContext(
            run_id=run_id,
            started_at=started_at,
            deadline_at=deadline_at,
            timeout_seconds=timeout_seconds,
            cancellation_token=token,
            _event_recorder=record_event,
        )
        try:
            context.cancel_if_deadline_exceeded()
            if token.is_cancelled():
                return self._cancelled_result(
                    context=context,
                    started_monotonic=started_monotonic,
                    events=events,
                    operation_name=operation_name,
                    operation_result=None,
                    event_sink=event_sink,
                    event_sink_errors=event_sink_errors,
                )

            operation_result = operation(context)
            context.cancel_if_deadline_exceeded()
            if token.is_cancelled():
                return self._cancelled_result(
                    context=context,
                    started_monotonic=started_monotonic,
                    events=events,
                    operation_name=operation_name,
                    operation_result=operation_result,
                    event_sink=event_sink,
                    event_sink_errors=event_sink_errors,
                )

            completed_at = _now_utc()
            _commit_event(
                events,
                HostRunEventType.RUN_COMPLETED,
                run_id=run_id,
                event_sink=event_sink,
                event_sink_errors=event_sink_errors,
            )
            return HostRunResult(
                run_id=run_id,
                status=HostRunStatus.SUCCEEDED,
                started_at=started_at,
                deadline_at=deadline_at,
                completed_at=completed_at,
                elapsed_ms=_elapsed_ms(started_monotonic),
                operation_result=operation_result,
                timeout_classification=None,
                safe_diagnostics=build_safe_diagnostics(
                    {
                        "operation_name": operation_name,
                        "status": HostRunStatus.SUCCEEDED,
                        "session_id": session_id,
                    }
                ),
                events=tuple(events),
            )
        except Exception as exc:  # noqa: BLE001
            if event_sink_errors and event_sink_errors[-1] is exc:
                raise
            context.cancel_if_deadline_exceeded()
            if token.is_cancelled():
                return self._cancelled_result(
                    context=context,
                    started_monotonic=started_monotonic,
                    events=events,
                    operation_name=operation_name,
                    operation_result=None,
                    event_sink=event_sink,
                    event_sink_errors=event_sink_errors,
                )
            completed_at = _now_utc()
            diagnostics = build_safe_diagnostics(
                {
                    "operation_name": operation_name,
                    "status": HostRunStatus.FAILED,
                    "error_type": type(exc).__name__,
                    "session_id": session_id,
                }
            )
            _commit_event(
                events,
                HostRunEventType.DIAGNOSTIC_RECORDED,
                run_id=run_id,
                event_sink=event_sink,
                event_sink_errors=event_sink_errors,
                **diagnostics,
            )
            _commit_event(
                events,
                HostRunEventType.RUN_FAILED,
                run_id=run_id,
                event_sink=event_sink,
                event_sink_errors=event_sink_errors,
            )
            return HostRunResult(
                run_id=run_id,
                status=HostRunStatus.FAILED,
                started_at=started_at,
                deadline_at=deadline_at,
                completed_at=completed_at,
                elapsed_ms=_elapsed_ms(started_monotonic),
                operation_result=None,
                timeout_classification=None,
                safe_diagnostics=diagnostics,
                events=tuple(events),
            )

    def _cancelled_result(
        self,
        *,
        context: HostRunContext,
        started_monotonic: float,
        events: list[HostRunEvent],
        operation_name: str,
        operation_result: object | None,
        event_sink: HostRunEventSink | None = None,
        event_sink_errors: list[BaseException] | None = None,
    ) -> HostRunResult:
        """构造取消 / deadline exceeded 终态结果。"""

        reason = context.cancellation_token.reason or HostCancelReason.USER_CANCELLED
        status = (
            HostRunStatus.DEADLINE_EXCEEDED
            if reason == HostCancelReason.RUN_DEADLINE_EXCEEDED
            else HostRunStatus.CANCELLED
        )
        timeout_classification = (
            HostTimeoutClassification.RUN_DEADLINE_EXCEEDED
            if reason == HostCancelReason.RUN_DEADLINE_EXCEEDED
            else None
        )
        diagnostics = build_safe_diagnostics(
            {
                "operation_name": operation_name,
                "status": status,
                "cancel_reason": reason,
                "timeout_classification": timeout_classification,
            }
        )
        _commit_event(
            events,
            HostRunEventType.DIAGNOSTIC_RECORDED,
            run_id=context.run_id,
            event_sink=event_sink,
            event_sink_errors=event_sink_errors,
            **diagnostics,
        )
        _commit_event(
            events,
            HostRunEventType.RUN_CANCELLED,
            run_id=context.run_id,
            event_sink=event_sink,
            event_sink_errors=event_sink_errors,
        )
        return HostRunResult(
            run_id=context.run_id,
            status=status,
            started_at=context.started_at,
            deadline_at=context.deadline_at,
            completed_at=_now_utc(),
            elapsed_ms=_elapsed_ms(started_monotonic),
            operation_result=operation_result,
            timeout_classification=timeout_classification,
            safe_diagnostics=diagnostics,
            events=tuple(events),
        )


def _event(
    event_type: HostRunEventType,
    *,
    run_id: str,
    **diagnostics: object,
) -> HostRunEvent:
    """构造安全 Host run 事件。"""

    return HostRunEvent(
        event_type=event_type,
        run_id=run_id,
        created_at=_now_utc(),
        diagnostics=build_safe_diagnostics(diagnostics),
    )


def _commit_event(
    events: list[HostRunEvent],
    event_type: HostRunEventType,
    *,
    run_id: str,
    event_sink: HostRunEventSink | None,
    event_sink_errors: list[BaseException] | None = None,
    **diagnostics: object,
) -> HostRunEvent:
    """提交 Host 事件并同步投递给通用 sink。

    Args:
        events: 当前 run 的内存事件列表。
        event_type: 事件类型。
        run_id: Host run ID。
        event_sink: 可选通用事件接收器。
        event_sink_errors: 可选 sink 异常记录，用于避免 broad operation catch 误吞。
        diagnostics: 安全诊断字段。

    Returns:
        已追加到事件列表的同一个事件对象。

    Raises:
        HostRuntimeError: 当诊断字段不符合安全契约时抛出。
        Exception: `event_sink` 抛出的异常原样传播，Host 不吞掉或翻译。
    """

    event = _event(event_type, run_id=run_id, **diagnostics)
    events.append(event)
    if event_sink is not None:
        try:
            event_sink(event)
        except Exception as exc:  # noqa: BLE001 - 只记录后原样抛出，Host 不翻译。
            if event_sink_errors is not None:
                event_sink_errors.append(exc)
            raise
    return event
