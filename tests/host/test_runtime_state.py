"""Host runtime state 单元测试。"""

from __future__ import annotations

import pytest

from fund_agent.host import (
    HostCancellationToken,
    HostCancelReason,
    HostRuntimeError,
    HostRunStatus,
    build_safe_diagnostics,
    is_terminal_status,
)


def test_terminal_statuses_are_closed_set() -> None:
    """验证 Host 终态集合稳定。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当终态集合不符合契约时抛出。
    """

    assert not is_terminal_status(HostRunStatus.CREATED)
    assert not is_terminal_status(HostRunStatus.RUNNING)
    assert is_terminal_status(HostRunStatus.SUCCEEDED)
    assert is_terminal_status(HostRunStatus.FAILED)
    assert is_terminal_status(HostRunStatus.CANCELLED)
    assert is_terminal_status(HostRunStatus.DEADLINE_EXCEEDED)


def test_cancellation_token_preserves_first_reason() -> None:
    """验证取消令牌幂等并保留首次原因。"""

    token = HostCancellationToken()

    token.cancel(HostCancelReason.USER_CANCELLED)
    token.cancel(HostCancelReason.RUN_DEADLINE_EXCEEDED)

    assert token.is_cancelled()
    assert token.reason == HostCancelReason.USER_CANCELLED


def test_cancellation_token_raise_if_cancelled() -> None:
    """验证取消令牌可在协作边界 fail-closed。"""

    token = HostCancellationToken()
    token.cancel(HostCancelReason.RUN_DEADLINE_EXCEEDED)

    with pytest.raises(HostRuntimeError, match="run_deadline_exceeded"):
        token.raise_if_cancelled()


def test_safe_diagnostics_rejects_forbidden_keys() -> None:
    """验证安全诊断拒绝 secret / prompt / raw response 类字段。"""

    with pytest.raises(HostRuntimeError, match="prompt"):
        build_safe_diagnostics({"full_prompt": "secret"})

    with pytest.raises(HostRuntimeError, match="Authorization"):
        build_safe_diagnostics({"Authorization": "Bearer token"})


def test_safe_diagnostics_rejects_forbidden_string_values() -> None:
    """验证安全诊断拒绝敏感字符串值。"""

    forbidden_values = (
        "Bearer sk-test-secret",
        "system_prompt raw_response",
        "chapter_draft draft_markdown",
        "provider_response payload",
    )

    for value in forbidden_values:
        with pytest.raises(HostRuntimeError, match="敏感字符串值"):
            build_safe_diagnostics({"message": value})


def test_safe_diagnostics_truncates_long_string() -> None:
    """验证安全诊断截断长字符串，避免 unbounded exception 泄漏。"""

    diagnostics = build_safe_diagnostics({"error_type": "x" * 500})

    assert isinstance(diagnostics["error_type"], str)
    assert len(diagnostics["error_type"]) <= 240
    assert diagnostics["error_type"].endswith("...")


def test_safe_diagnostics_rejects_complex_payload() -> None:
    """验证安全诊断拒绝复杂 payload。"""

    with pytest.raises(HostRuntimeError, match="dict"):
        build_safe_diagnostics({"payload": {"nested": "value"}})
