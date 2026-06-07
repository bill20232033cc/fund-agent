"""Service-Agent bridge 测试，见模板第 1-6 章。"""

from __future__ import annotations

from datetime import UTC, datetime

from fund_agent.host import (
    HostCancellationToken,
    HostCancelReason,
    HostRunContext,
    HostRunEventType,
    HostRuntimeRunner,
)
from fund_agent.services.agent_bridge import run_agent_chapter_orchestration_bridge
from fund_agent.services.chapter_orchestrator import (
    ChapterOrchestrationPolicy,
    ChapterOrchestratorLLMClients,
    build_chapter_orchestration_input,
)
from tests.agent.test_runner import _FakeAuditor, _FakeWriter, _projection


def test_service_bridge_projects_accepted_agent_run_to_service_result() -> None:
    """验证 bridge 把 accepted Agent run 投影回 Service result。"""

    projection = _projection((1, 2))
    input_data = build_chapter_orchestration_input(
        fund_code="110011",
        report_year=2024,
        chapter_projection=projection,
        policy=ChapterOrchestrationPolicy(target_chapter_ids=(1, 2)),
    )

    result = run_agent_chapter_orchestration_bridge(
        input_data,
        projection=projection,
        llm_clients=ChapterOrchestratorLLMClients(
            writer=_FakeWriter(),
            auditor=_FakeAuditor(),
        ),
    )

    assert result.status == "accepted"
    assert result.generated_chapter_ids == (1, 2)
    assert result.skipped_chapter_ids == ()
    assert [conclusion.chapter_id for conclusion in result.accepted_conclusions] == [1, 2]


def test_service_bridge_preserves_partial_body_readiness() -> None:
    """验证 bridge 不把 partial body readiness 变成完整报告前置条件。"""

    projection = _projection((1, 2))
    input_data = build_chapter_orchestration_input(
        fund_code="110011",
        report_year=2024,
        chapter_projection=projection,
        policy=ChapterOrchestrationPolicy(target_chapter_ids=(1, 2)),
    )

    result = run_agent_chapter_orchestration_bridge(
        input_data,
        projection=projection,
        llm_clients=ChapterOrchestratorLLMClients(
            writer=_FakeWriter(actions={2: "不符合固定结构"}),
            auditor=_FakeAuditor(),
        ),
    )

    rows = {row.chapter_id: row for row in result.chapter_results}
    assert result.status == "partial"
    assert rows[1].status == "accepted"
    assert rows[2].status == "blocked"
    assert rows[2].stop_reason == "missing_required_structure"
    assert result.accepted_conclusions[0].chapter_id == 1


def test_service_bridge_translates_host_cancel_to_agent_interruption() -> None:
    """验证 Host cancel 在 bridge 层翻译为 Agent scheduler interruption。"""

    projection = _projection((1,))
    input_data = build_chapter_orchestration_input(
        fund_code="110011",
        report_year=2024,
        chapter_projection=projection,
        policy=ChapterOrchestrationPolicy(target_chapter_ids=(1,)),
    )
    token = HostCancellationToken()
    token.cancel(HostCancelReason.USER_CANCELLED)
    context = HostRunContext(
        run_id="host_run_test",
        started_at=datetime.now(UTC),
        deadline_at=None,
        timeout_seconds=None,
        cancellation_token=token,
    )

    result = run_agent_chapter_orchestration_bridge(
        input_data,
        projection=projection,
        llm_clients=ChapterOrchestratorLLMClients(
            writer=_FakeWriter(),
            auditor=_FakeAuditor(),
        ),
        host_context=context,
    )

    row = result.chapter_results[0]
    assert result.status == "blocked"
    assert row.status == "blocked"
    assert row.stop_reason == "llm_exception"
    assert row.attempts == ()
    assert "blocked_scheduler_interrupted" in result.blocked_reasons[0]


def test_service_bridge_records_repair_phase_events() -> None:
    """验证 Agent repair decision 会回放为 Host repair phase event。"""

    projection = _projection((1,))
    input_data = build_chapter_orchestration_input(
        fund_code="110011",
        report_year=2024,
        chapter_projection=projection,
        policy=ChapterOrchestrationPolicy(target_chapter_ids=(1,), max_repair_attempts=1),
    )

    def _operation(host_context: HostRunContext):
        return run_agent_chapter_orchestration_bridge(
            input_data,
            projection=projection,
            llm_clients=ChapterOrchestratorLLMClients(
                writer=_FakeWriter(),
                auditor=_FakeAuditor(
                    (
                        "BLOCKING|chapter|fixture semantic repair",
                        "PASS|chapter|no issues",
                    )
                ),
            ),
            host_context=host_context,
        )

    host_result = HostRuntimeRunner().run_sync(
        operation_name="agent_bridge_repair_event_test",
        operation=_operation,
        timeout_seconds=10,
    )

    phase_events = [
        event
        for event in host_result.events
        if event.event_type
        in {HostRunEventType.PHASE_STARTED, HostRunEventType.PHASE_COMPLETED}
    ]
    assert host_result.status == "succeeded"
    assert host_result.operation_result is not None
    assert host_result.operation_result.status == "accepted"
    assert [(event.event_type, event.diagnostics["phase"]) for event in phase_events] == [
        (HostRunEventType.PHASE_STARTED, "writer"),
        (HostRunEventType.PHASE_COMPLETED, "writer"),
        (HostRunEventType.PHASE_STARTED, "auditor"),
        (HostRunEventType.PHASE_COMPLETED, "auditor"),
        (HostRunEventType.PHASE_STARTED, "repair"),
        (HostRunEventType.PHASE_COMPLETED, "repair"),
        (HostRunEventType.PHASE_STARTED, "writer"),
        (HostRunEventType.PHASE_COMPLETED, "writer"),
        (HostRunEventType.PHASE_STARTED, "auditor"),
        (HostRunEventType.PHASE_COMPLETED, "auditor"),
    ]
    assert phase_events[4].diagnostics["chapter_id"] == 1
    assert phase_events[4].diagnostics["attempt"] == 0
