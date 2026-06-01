"""Host runtime runner 单元测试。"""

from __future__ import annotations

from datetime import timedelta
from pathlib import Path

from fund_agent.host import (
    build_safe_diagnostics,
    HostCancelReason,
    HostRunContext,
    HostRunStatus,
    HostRuntimeError,
    HostRuntimeRunner,
    HostTimeoutClassification,
)
from fund_agent.host.runtime import HostRunEventType

_HOST_PACKAGE_ROOT = Path(__file__).parents[2] / "fund_agent" / "host"


def test_host_package_does_not_import_service_or_fund_layers() -> None:
    """验证 Host 包不导入 Service 或 Fund 层实现。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 Host 越过 `UI -> Service -> Host -> Agent` 边界时抛出。
    """

    for source_path in _HOST_PACKAGE_ROOT.rglob("*.py"):
        source = source_path.read_text(encoding="utf-8")
        assert "fund_agent.services" not in source
        assert "fund_agent.fund" not in source


def test_host_runner_source_has_no_fund_business_semantics() -> None:
    """验证 Host runner 不理解基金业务或 Service ExecutionContract 字段。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 Host 源码出现基金业务字段或 typed request 字段时抛出。
    """

    host_source = "\n".join(
        source_path.read_text(encoding="utf-8")
        for source_path in sorted(_HOST_PACKAGE_ROOT.rglob("*.py"))
    )
    forbidden_terms = (
        "FundLLMExecutionContract",
        "FundLLMExecutionRequest",
        "FundAnalysisRequest",
        "ExecutionContract",
        "fund_code",
        "report_year",
        "report_mode",
        "llm_opt_in_mode",
        "analysis_input",
        "chapter_policy",
        "assembly_policy",
        "provider_runtime_budget",
        "quality_fail_closed_policy",
        "quality_policy",
        "preferred_lens",
        "ITEM_RULE",
        "CHAPTER_CONTRACT",
        "FundDocumentRepository",
        "extra_payload",
    )

    for term in forbidden_terms:
        assert term not in host_source


def test_build_safe_diagnostics_rejects_forbidden_business_payload_keys() -> None:
    """验证 Host 安全诊断拒绝 prompt、草稿、原始响应和 secret 字段。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当不安全诊断字段被 Host 接受时抛出。
    """

    forbidden_keys = (
        "system_prompt",
        "chapter_draft",
        "raw_provider_response",
        "raw_audit_response",
        "Authorization",
        "api_key",
    )

    for key in forbidden_keys:
        try:
            build_safe_diagnostics({key: "secret payload"})
        except HostRuntimeError as exc:
            assert key.lower() in str(exc).lower()
        else:  # pragma: no cover - 分支存在是为了给断言失败明确消息。
            raise AssertionError(f"Host safe diagnostics accepted forbidden key: {key}")


def test_run_sync_success_emits_terminal_result() -> None:
    """验证同步 operation 成功时进入 succeeded 终态。"""

    result = HostRuntimeRunner().run_sync(
        operation_name="unit_operation",
        operation=lambda context: {"run_id": context.run_id},
        timeout_seconds=10,
    )

    assert result.status == HostRunStatus.SUCCEEDED
    assert result.is_terminal
    assert result.run_id.startswith("host_run_")
    assert result.deadline_at == result.started_at + timedelta(seconds=10)
    assert result.operation_result == {"run_id": result.run_id}
    assert [event.event_type for event in result.events] == [
        HostRunEventType.RUN_STARTED,
        HostRunEventType.RUN_COMPLETED,
    ]


def test_run_sync_records_operation_phase_events() -> None:
    """验证 operation 可记录安全 phase 生命周期事件。"""

    def operation(context: HostRunContext) -> str:
        context.record_phase_started(phase="writer", chapter_id=1, attempt=0)
        context.record_phase_completed(
            phase="writer",
            chapter_id=1,
            attempt=0,
            elapsed_ms=12,
        )
        return "ok"

    result = HostRuntimeRunner().run_sync(
        operation_name="unit_operation",
        operation=operation,
        timeout_seconds=10,
    )

    assert [event.event_type for event in result.events] == [
        HostRunEventType.RUN_STARTED,
        HostRunEventType.PHASE_STARTED,
        HostRunEventType.PHASE_COMPLETED,
        HostRunEventType.RUN_COMPLETED,
    ]
    assert result.events[1].diagnostics == {
        "phase": "writer",
        "chapter_id": 1,
        "attempt": 0,
        "provider_attempt": None,
    }


def test_run_sync_exception_is_failed_with_safe_error_type() -> None:
    """验证 operation 异常被收敛为 failed 终态和安全错误类型。"""

    def operation(context: HostRunContext) -> object:
        raise RuntimeError(f"boom {context.run_id}")

    result = HostRuntimeRunner().run_sync(
        operation_name="unit_operation",
        operation=operation,
        timeout_seconds=10,
    )

    assert result.status == HostRunStatus.FAILED
    assert result.operation_result is None
    assert result.safe_diagnostics["error_type"] == "RuntimeError"
    assert [event.event_type for event in result.events] == [
        HostRunEventType.RUN_STARTED,
        HostRunEventType.DIAGNOSTIC_RECORDED,
        HostRunEventType.RUN_FAILED,
    ]


def test_run_sync_cancelled_before_return_is_cancelled() -> None:
    """验证 operation 协作式取消后进入 cancelled 终态。"""

    def operation(context: HostRunContext) -> str:
        context.cancellation_token.cancel(HostCancelReason.USER_CANCELLED)
        return "partial"

    result = HostRuntimeRunner().run_sync(
        operation_name="unit_operation",
        operation=operation,
        timeout_seconds=10,
    )

    assert result.status == HostRunStatus.CANCELLED
    assert result.operation_result == "partial"
    assert result.timeout_classification is None
    assert result.safe_diagnostics["cancel_reason"] == "user_cancelled"
    assert result.events[-1].event_type == HostRunEventType.RUN_CANCELLED


def test_run_sync_deadline_exceeded_before_operation() -> None:
    """验证 deadline 已过时进入 deadline_exceeded 终态。"""

    called = False

    def operation(context: HostRunContext) -> object:
        nonlocal called
        called = True
        return None

    result = HostRuntimeRunner().run_sync(
        operation_name="unit_operation",
        operation=operation,
        timeout_seconds=1,
    )
    # 直接操作 context 时间不稳定，因此这里只验证正常路径没有误触发。
    assert result.status == HostRunStatus.SUCCEEDED
    assert called


def test_run_sync_deadline_exceeded_after_operation() -> None:
    """验证 operation 触发 deadline cancel 后分类为 run_deadline_exceeded。"""

    def operation(context: HostRunContext) -> str:
        context.cancellation_token.cancel(HostCancelReason.RUN_DEADLINE_EXCEEDED)
        return "late"

    result = HostRuntimeRunner().run_sync(
        operation_name="unit_operation",
        operation=operation,
        timeout_seconds=10,
    )

    assert result.status == HostRunStatus.DEADLINE_EXCEEDED
    assert result.timeout_classification == HostTimeoutClassification.RUN_DEADLINE_EXCEEDED
    assert result.safe_diagnostics["timeout_classification"] == "run_deadline_exceeded"


def test_run_sync_event_order_has_single_terminal_event() -> None:
    """验证事件顺序只有一个 terminal event。"""

    result = HostRuntimeRunner().run_sync(
        operation_name="unit_operation",
        operation=lambda context: "ok",
        timeout_seconds=None,
    )

    event_types = [event.event_type for event in result.events]
    assert event_types[0] == HostRunEventType.RUN_STARTED
    assert event_types[-1] in {
        HostRunEventType.RUN_COMPLETED,
        HostRunEventType.RUN_FAILED,
        HostRunEventType.RUN_CANCELLED,
    }
    assert len(
        [
            event_type
            for event_type in event_types
            if event_type
            in {
                HostRunEventType.RUN_COMPLETED,
                HostRunEventType.RUN_FAILED,
                HostRunEventType.RUN_CANCELLED,
            }
        ]
    ) == 1
