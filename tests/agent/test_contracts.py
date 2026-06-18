"""Agent contracts 测试，见模板第 1-6 章。"""

from __future__ import annotations

import ast
import inspect
from dataclasses import FrozenInstanceError

import pytest

import fund_agent.agent.contracts as contracts_module
from fund_agent.agent import (
    AgentRepairPolicy,
    AgentSchedulerInterruption,
    ChapterAttempt,
    ChapterTask,
    FinalAssemblyReadiness,
    ToolCallRequest,
    ToolCallResult,
    ToolTrace,
)


def test_tool_trace_safe_dict_excludes_unsafe_payloads() -> None:
    """验证 ToolTrace 只输出安全标量。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 trace 输出含不安全字段时抛出。
    """

    request = ToolCallRequest(
        tool_name="fund.write_chapter",
        chapter_id=2,
        attempt_index=0,
        safe_metadata={"prompt_chars": 120, "approx_prompt_tokens": 30},
    )
    result = ToolCallResult(
        status="blocked",
        terminal_state="blocked_prompt_contract",
        issue_ids=("missing_required_output_marker",),
        safe_metadata={"response_chars": 88},
    )

    trace = ToolTrace(
        request=request,
        result=result,
        elapsed_ms=15,
        response_chars=88,
        request_id="req-safe",
    )

    safe = trace.to_safe_dict()

    assert safe == {
        "tool_name": "fund.write_chapter",
        "chapter_id": 2,
        "attempt_index": 0,
        "status": "blocked",
        "terminal_state": "blocked_prompt_contract",
        "issue_ids": ("missing_required_output_marker",),
        "elapsed_ms": 15,
        "response_chars": 88,
        "request_id": "req-safe",
        "request_metadata": {"prompt_chars": 120, "approx_prompt_tokens": 30},
        "result_metadata": {"response_chars": 88},
    }
    unsafe_keys = {
        "prompt",
        "draft",
        "raw_provider_response",
        "api_key",
        "authorization",
        "model_name",
        "base_url",
    }
    assert unsafe_keys.isdisjoint(safe)


@pytest.mark.parametrize(
    "metadata",
    [
        {"prompt": "full prompt"},
        {"draft_markdown": "## draft"},
        {"raw_provider_response": "{}"},
        {"api_key": "sk-secret"},
        {"Authorization": "Bearer sk-secret"},
        {"model_name": "provider-model"},
        {"base_url": "https://provider.example"},
    ],
)
def test_tool_trace_rejects_unsafe_metadata_keys(metadata: dict[str, str]) -> None:
    """验证 ToolTrace metadata 拒绝不安全字段。

    Args:
        metadata: 待注入的 metadata。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当不安全字段未被拒绝时抛出。
    """

    with pytest.raises(ValueError, match="不安全字段"):
        ToolCallRequest(
            tool_name="fund.write_chapter",
            chapter_id=1,
            attempt_index=0,
            safe_metadata=metadata,
        )


def test_repair_policy_forbids_hidden_retry() -> None:
    """验证 Agent repair policy 禁止 hidden retry。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 hidden retry 可开启时抛出。
    """

    assert AgentRepairPolicy(max_content_repair_attempts=1).hidden_retry_allowed is False
    with pytest.raises(ValueError, match="hidden retry"):
        AgentRepairPolicy(max_content_repair_attempts=1, hidden_retry_allowed=True)


def test_scheduler_interruption_contract_validates_status_and_reason() -> None:
    """验证 scheduler interruption 是 Agent-owned normalized contract。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当中断状态校验失效时抛出。
    """

    interruption = AgentSchedulerInterruption(
        status="deadline_exceeded",
        reason="host deadline exceeded",
        phase="after_tool_call",
        chapter_id=2,
        attempt_index=0,
    )

    assert interruption.status == "deadline_exceeded"
    with pytest.raises(ValueError, match="必须提供 reason"):
        AgentSchedulerInterruption(status="cancelled", reason=None, phase="before_chapter")
    with pytest.raises(ValueError, match="不允许 reason"):
        AgentSchedulerInterruption(status="none", reason="unexpected", phase="before_chapter")


def test_chapter_task_and_attempt_are_immutable_and_body_scoped() -> None:
    """验证 task/attempt 为不可变 body chapter 契约。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当可变性或章节范围失效时抛出。
    """

    attempt = ChapterAttempt(
        attempt_index=0,
        tool_traces=(),
        terminal_state="blocked_prompt_contract",
    )
    task = ChapterTask(
        chapter_id=3,
        title="基金经理画像",
        status="blocked",
        terminal_state="blocked_prompt_contract",
        attempts=(attempt,),
        blocked_reasons=("3:blocked_prompt_contract:prompt_contract",),
        failure_category="prompt_contract",
    )

    assert task.attempts == (attempt,)
    with pytest.raises(FrozenInstanceError):
        task.title = "changed"  # type: ignore[misc]
    with pytest.raises(ValueError, match="第 1-6 章"):
        ChapterTask(
            chapter_id=7,
            title="最终判断",
            status="prepared",
            terminal_state="accepted",
        )


def test_final_assembly_readiness_rejects_duplicate_or_conflicting_sources() -> None:
    """验证 final readiness 不允许重复来源或 accepted/blocked 冲突。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当重复来源未 fail-closed 时抛出。
    """

    readiness = FinalAssemblyReadiness(
        ready=False,
        accepted_source_chapter_ids=(1, 2),
        blocked_chapter_ids=(3,),
        blocking_reasons=("3:blocked",),
    )

    assert readiness.accepted_source_chapter_ids == (1, 2)
    with pytest.raises(ValueError, match="不允许重复"):
        FinalAssemblyReadiness(
            ready=True,
            accepted_source_chapter_ids=(1, 1),
            blocked_chapter_ids=(),
        )
    with pytest.raises(ValueError, match="冲突"):
        FinalAssemblyReadiness(
            ready=False,
            accepted_source_chapter_ids=(1,),
            blocked_chapter_ids=(1,),
        )


def test_agent_contracts_do_not_import_host_or_service() -> None:
    """验证 Agent contracts 不导入 Host 或 Service。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 Agent contracts 依赖 Host/Service 时抛出。
    """

    source = inspect.getsource(contracts_module)
    tree = ast.parse(source)
    imported_modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_modules.update(alias.name for alias in node.names)
        if isinstance(node, ast.ImportFrom) and node.module is not None:
            imported_modules.add(node.module)

    assert "fund_agent.host" not in imported_modules
    assert not any(module.startswith("fund_agent.services") for module in imported_modules)
