"""Agent runner 测试，见模板第 1-6 章。"""

from __future__ import annotations

import ast
import inspect
from dataclasses import replace

import pytest

import fund_agent.agent.runner as runner_module
from fund_agent.agent import (
    AgentLLMClients,
    AgentRepairPolicy,
    AgentRunPolicy,
    AgentSchedulerInterruption,
    run_agent_body_chapters,
)
from fund_agent.fund.chapter_auditor import ChapterAuditLLMRequest, ChapterAuditLLMResponse
from fund_agent.fund.chapter_facts import project_chapter_facts
from fund_agent.fund.evidence_availability import EvidenceAvailability
from fund_agent.fund.extractors.models import ExtractedField
from fund_agent.fund.chapter_writer import (
    ChapterLLMRequest,
    ChapterLLMResponse,
    build_chapter_writer_input,
    write_chapter,
)
from fund_agent.fund.template.typed_contracts import load_typed_template_contract_manifest
from tests.fund.test_chapter_facts import _bundle
from tests.services.test_chapter_orchestrator import _valid_markdown_from_request


class _FakeWriter:
    """测试用 writer client。"""

    def __init__(self, actions: dict[int, object] | None = None) -> None:
        """初始化 fake writer。

        Args:
            actions: 章节编号到 markdown 或异常的映射。

        Returns:
            无返回值。

        Raises:
            无。
        """

        self.actions = actions or {}
        self.requests: list[ChapterLLMRequest] = []

    def generate_chapter(self, request: ChapterLLMRequest) -> ChapterLLMResponse:
        """返回合法章节、预设文本或抛出异常。"""

        self.requests.append(request)
        action = self.actions.get(request.chapter_id)
        if isinstance(action, Exception):
            raise action
        if callable(action):
            text = action(request)
        elif isinstance(action, str):
            text = action
        else:
            text = _valid_agent_markdown_from_request(request)
        return ChapterLLMResponse(text=text, model_name="fake-writer", finish_reason="stop")


class _FakeAuditor:
    """测试用 auditor client。"""

    def __init__(self, responses: tuple[str, ...] = ()) -> None:
        """初始化 fake auditor。

        Args:
            responses: 按调用顺序返回的行协议。

        Returns:
            无返回值。

        Raises:
            无。
        """

        self.responses = list(responses)
        self.requests: list[ChapterAuditLLMRequest] = []

    def audit_chapter(self, request: ChapterAuditLLMRequest) -> ChapterAuditLLMResponse:
        """返回测试行协议。"""

        self.requests.append(request)
        raw_text = self.responses.pop(0) if self.responses else "PASS|chapter|no issues"
        return ChapterAuditLLMResponse(raw_text=raw_text, model_name="fake-auditor", finish_reason="stop")


class LLMProviderTimeoutError(Exception):
    """测试用 provider timeout 异常，按类名映射。"""


def test_runner_accepts_all_body_chapters_and_builds_readiness() -> None:
    """验证全部正文 accepted 时 readiness 可交给 final assembly。"""

    writer = _FakeWriter()
    auditor = _FakeAuditor()

    run = run_agent_body_chapters(
        _projection((1, 2, 3, 4, 5, 6)),
        llm_clients=AgentLLMClients(writer=writer, auditor=auditor),
    )

    assert run.status == "accepted"
    assert run.final_assembly_readiness is not None
    assert run.final_assembly_readiness.ready is True
    assert run.final_assembly_readiness.accepted_source_chapter_ids == (1, 2, 3, 4, 5, 6)
    assert [request.chapter_id for request in writer.requests] == [1, 2, 3, 4, 5, 6]
    assert all(task.accepted_conclusion is not None for task in run.tasks)


def test_writer_block_does_not_skip_later_body_chapters() -> None:
    """验证单章 writer 阻断不跳过后续正文章节。"""

    writer = _FakeWriter(actions={3: "不符合固定结构"})

    run = run_agent_body_chapters(
        _projection((1, 2, 3, 4, 5, 6)),
        llm_clients=AgentLLMClients(writer=writer, auditor=_FakeAuditor()),
    )

    rows = {task.chapter_id: task for task in run.tasks}
    assert run.status == "partial"
    assert [request.chapter_id for request in writer.requests] == [1, 2, 3, 4, 5, 6]
    assert rows[3].status == "blocked"
    assert rows[3].terminal_state == "blocked_prompt_contract"
    assert rows[3].failure_category == "prompt_contract"
    assert rows[4].status == "accepted"
    assert run.final_assembly_readiness is not None
    assert run.final_assembly_readiness.ready is False


def test_provider_timeout_is_provider_runtime_and_does_not_content_retry() -> None:
    """验证 provider timeout 不消耗 Agent 内容修复预算。"""

    writer = _FakeWriter(actions={1: LLMProviderTimeoutError("timeout")})

    run = run_agent_body_chapters(
        _projection((1,)),
        llm_clients=AgentLLMClients(writer=writer, auditor=_FakeAuditor()),
        policy=AgentRunPolicy(target_chapter_ids=(1,)),
    )

    task = run.tasks[0]
    assert run.status == "blocked"
    assert task.status == "failed"
    assert task.terminal_state == "blocked_provider_runtime"
    assert task.failure_category == "llm_timeout"
    assert len(writer.requests) == 1
    assert task.attempts == ()


def test_unknown_exception_is_code_bug_not_provider_runtime() -> None:
    """验证未知异常保留 code_bug 分类且不泄漏异常消息。"""

    writer = _FakeWriter(actions={1: RuntimeError("Authorization Bearer sk-secret prompt raw")})

    run = run_agent_body_chapters(
        _projection((1,)),
        llm_clients=AgentLLMClients(writer=writer, auditor=_FakeAuditor()),
        policy=AgentRunPolicy(target_chapter_ids=(1,)),
    )

    task = run.tasks[0]
    assert task.status == "failed"
    assert task.terminal_state == "blocked_internal_code_bug"
    assert task.failure_category == "code_bug"
    rendered = repr(task.blocked_reasons)
    assert "Authorization" not in rendered
    assert "sk-secret" not in rendered
    assert "prompt raw" not in rendered


def test_chapter_3_value_error_is_internal_code_bug_without_provider_runtime() -> None:
    """验证第 3 章 pre-provider ValueError 保持内部 code_bug。"""

    writer = _FakeWriter(actions={3: ValueError("Authorization Bearer sk-secret prompt raw")})

    run = run_agent_body_chapters(
        _projection((3,)),
        llm_clients=AgentLLMClients(writer=writer, auditor=_FakeAuditor()),
        policy=AgentRunPolicy(
            target_chapter_ids=(3,),
            max_output_chars=12000,
            typed_template_path="typed_template_contract",
        ),
    )

    task = run.tasks[0]
    assert [request.chapter_id for request in writer.requests] == [3]
    assert run.status in {"blocked", "failed"}
    assert task.status == "failed"
    assert task.terminal_state == "blocked_internal_code_bug"
    assert task.failure_category == "code_bug"
    assert task.stop_reason == "llm_exception"
    assert task.attempts == ()
    rendered = repr(task.blocked_reasons)
    assert "Authorization" not in rendered
    assert "Bearer" not in rendered
    assert "sk-secret" not in rendered
    assert "prompt raw" not in rendered


def test_chapter_3_writer_input_value_error_is_internal_code_bug_before_writer_tool(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """验证第 3 章 writer input 构造异常被归类为内部 code_bug。"""

    def _raise_typed_required_output_items(
        chapter_id: int,
        *,
        policy: object,
    ) -> tuple[object, ...]:
        """在第 3 章 writer request 构造前注入 ValueError。"""

        if chapter_id == 3:
            raise ValueError("Authorization Bearer sk-secret prompt raw")
        return ()

    monkeypatch.setattr(
        runner_module,
        "_typed_required_output_items",
        _raise_typed_required_output_items,
    )
    writer = _FakeWriter()

    run = run_agent_body_chapters(
        _projection((3,)),
        llm_clients=AgentLLMClients(writer=writer, auditor=_FakeAuditor()),
        policy=AgentRunPolicy(
            target_chapter_ids=(3,),
            max_output_chars=12000,
            typed_template_path="typed_template_contract",
        ),
    )

    task = run.tasks[0]
    assert writer.requests == []
    assert run.status in {"blocked", "failed"}
    assert task.chapter_id == 3
    assert task.status == "failed"
    assert task.terminal_state == "blocked_internal_code_bug"
    assert task.stop_reason == "llm_exception"
    assert task.failure_category == "code_bug"
    assert task.attempts == ()
    rendered = repr(task.blocked_reasons)
    assert "Authorization" not in rendered
    assert "Bearer" not in rendered
    assert "sk-secret" not in rendered
    assert "prompt raw" not in rendered


def test_chapter_3_missing_typed_availability_blocks_before_provider(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """验证第 3 章 covered typed availability 缺项转为 fact_gap 且不调 provider。"""

    def _empty_availability(_: object) -> EvidenceAvailability:
        """返回同 identity 但缺 required_output requirement 的 availability。"""

        return EvidenceAvailability(
            schema_version="evidence_availability.v1",
            source_schema_version="chapter_fact_projection.v1",
            fund_code="110011",
            report_year=2024,
            requirements=(),
        )

    monkeypatch.setattr(runner_module, "derive_evidence_availability", _empty_availability)
    writer = _FakeWriter()

    run = run_agent_body_chapters(
        _projection((3,)),
        llm_clients=AgentLLMClients(writer=writer, auditor=_FakeAuditor()),
        policy=AgentRunPolicy(
            target_chapter_ids=(3,),
            max_output_chars=12000,
            typed_template_path="typed_template_contract",
        ),
    )

    task = run.tasks[0]
    assert writer.requests == []
    assert run.status == "blocked"
    assert task.chapter_id == 3
    assert task.status == "blocked"
    assert task.terminal_state == "blocked_fact_gap"
    assert task.stop_reason == "missing_required_facts"
    assert task.failure_category == "fact_gap"
    assert len(task.attempts) == 1
    writer_result = task.attempts[0].writer_result
    assert writer_result is not None
    assert writer_result.status == "blocked"
    assert writer_result.prompt.required_output_evidence_plan
    assert any(
        plan.item_id == "ch3.required_output.item_03" and plan.action == "block"
        for plan in writer_result.prompt.required_output_evidence_plan
    )


def test_chapter_3_missing_basic_manager_info_renders_evidence_gap_and_accepts() -> None:
    """验证第 3 章基金经理基本信息缺证时用证据缺口安全降级。"""

    projection = _projection_with_missing_portfolio_managers()
    writer = _FakeWriter(actions={3: _chapter_3_markdown_with_item01_gap})

    run = run_agent_body_chapters(
        projection,
        llm_clients=AgentLLMClients(writer=writer, auditor=_FakeAuditor()),
        policy=AgentRunPolicy(
            target_chapter_ids=(3,),
            max_output_chars=12000,
            typed_template_path="typed_template_contract",
        ),
    )

    task = run.tasks[0]
    assert [request.chapter_id for request in writer.requests] == [3]
    assert run.status == "accepted"
    assert task.chapter_id == 3
    assert task.status == "accepted"
    assert task.accepted_draft is not None
    assert task.accepted_conclusion is not None
    assert run.final_assembly_readiness is not None
    assert run.final_assembly_readiness.ready is True
    assert run.final_assembly_readiness.accepted_source_chapter_ids == (3,)
    assert len(task.attempts) == 1
    writer_result = task.attempts[0].writer_result
    assert writer_result is not None
    assert writer_result.status == "drafted"
    item_01 = next(
        plan
        for plan in writer_result.prompt.required_output_evidence_plan
        if plan.item_id == "ch3.required_output.item_01"
    )
    assert item_01.availability_status == "missing"
    assert item_01.action == "render_evidence_gap"
    assert item_01.requirement_fact_ids


def test_chapter_3_missing_basic_manager_info_without_gap_phrase_blocks_after_writer() -> None:
    """验证第 3 章基金经理基本信息缺证但未写缺口时在 writer 输出校验后阻断。"""

    projection = _projection_with_missing_portfolio_managers()
    writer = _FakeWriter(actions={3: _chapter_3_markdown_without_item01_gap})

    run = run_agent_body_chapters(
        projection,
        llm_clients=AgentLLMClients(writer=writer, auditor=_FakeAuditor()),
        policy=AgentRunPolicy(
            target_chapter_ids=(3,),
            max_output_chars=12000,
            typed_template_path="typed_template_contract",
        ),
    )

    task = run.tasks[0]
    assert [request.chapter_id for request in writer.requests] == [3]
    assert run.status == "blocked"
    assert task.chapter_id == 3
    assert task.status == "blocked"
    assert task.terminal_state == "blocked_prompt_contract"
    assert task.stop_reason == "missing_required_output_marker"
    assert task.failure_category == "prompt_contract"
    assert task.failure_subcategory == "missing_required_marker"
    assert len(task.attempts) == 1
    writer_result = task.attempts[0].writer_result
    assert writer_result is not None
    assert writer_result.status == "blocked"
    rendered = repr(task.blocked_reasons)
    assert "writer:required_output_gap_missing:ch3.required_output.item_01" in rendered
    assert "required_output_block:ch3.required_output.item_01" not in rendered


def test_chapter_2_missing_evidence_gap_renders_and_builds_readiness() -> None:
    """验证 Agent runner 接受第 2 章非 available 证据缺口输出。"""

    projection = _projection_with_missing_chapter_2_evidence()
    writer = _FakeWriter(actions={2: _chapter_2_markdown_with_gap})

    run = run_agent_body_chapters(
        projection,
        llm_clients=AgentLLMClients(writer=writer, auditor=_FakeAuditor()),
        policy=AgentRunPolicy(
            target_chapter_ids=(2,),
            max_output_chars=12000,
            typed_template_path="typed_template_contract",
        ),
    )

    task = run.tasks[0]
    writer_result = task.attempts[0].writer_result
    assert run.status == "accepted"
    assert task.chapter_id == 2
    assert task.status == "accepted"
    assert task.accepted_draft is not None
    assert run.final_assembly_readiness is not None
    assert run.final_assembly_readiness.ready is True
    assert len(writer.requests) == 1
    assert writer_result is not None
    plan_by_id = {plan.item_id: plan for plan in writer_result.prompt.required_output_evidence_plan}
    assert plan_by_id["ch2.required_output.item_01"].action == "render_evidence_gap"
    assert plan_by_id["ch2.required_output.item_01"].availability_status == "missing"
    assert plan_by_id["ch2.required_output.item_07"].action == "render_minimum_verification_question"


def test_chapter_2_missing_evidence_without_gap_phrase_blocks_before_readiness() -> None:
    """验证 Agent runner 对第 2 章 unsafe 缺口输出仍 fail-closed。"""

    projection = _projection_with_missing_chapter_2_evidence()
    writer = _FakeWriter(actions={2: _chapter_2_markdown_without_gap_phrase})

    run = run_agent_body_chapters(
        projection,
        llm_clients=AgentLLMClients(writer=writer, auditor=_FakeAuditor()),
        policy=AgentRunPolicy(
            target_chapter_ids=(2,),
            max_output_chars=12000,
            typed_template_path="typed_template_contract",
        ),
    )

    task = run.tasks[0]
    assert run.status == "blocked"
    assert task.chapter_id == 2
    assert task.status == "blocked"
    assert task.terminal_state == "blocked_prompt_contract"
    assert task.stop_reason == "missing_required_output_marker"
    assert task.failure_category == "prompt_contract"
    assert task.failure_subcategory == "missing_required_marker"
    assert run.final_assembly_readiness is not None
    assert run.final_assembly_readiness.ready is False
    rendered = repr(task.blocked_reasons)
    assert "writer:required_output_gap_missing:ch2.required_output.item_01" in rendered
    assert "required_output_block:ch2.required_output.item_01" not in rendered


def test_chapter_3_missing_evidence_availability_envelope_remains_value_error(
) -> None:
    """验证第 3 章 typed availability 完全未提供时仍 fail-closed 为 ValueError。"""

    writer = _FakeWriter()
    manifest = load_typed_template_contract_manifest()
    chapter3 = next(chapter for chapter in manifest.chapters if chapter.chapter_id == 3)
    input_data = build_chapter_writer_input(
        _projection((3,)),
        chapter_id=3,
        max_output_chars=12000,
        typed_required_output_items=chapter3.required_output_items,
        evidence_availability=None,
    )

    with pytest.raises(ValueError, match="EvidenceAvailability"):
        write_chapter(input_data, llm_client=writer)
    assert writer.requests == []


def test_needs_more_facts_stops_without_source_probe_or_regenerate() -> None:
    """验证 needs_more_facts 终止且不重写、不 source probe。"""

    writer = _FakeWriter(actions={5: None})

    def _append_style_assertion(request: ChapterLLMRequest) -> ChapterLLMResponse:
        text = _valid_markdown_from_request(request) + "\n过去一年变化不大，风格稳定。"
        return ChapterLLMResponse(text=text, model_name="fake-writer", finish_reason="stop")

    writer.generate_chapter = _append_style_assertion  # type: ignore[method-assign]

    run = run_agent_body_chapters(
        _projection((5,)),
        llm_clients=AgentLLMClients(writer=writer, auditor=_FakeAuditor()),
        policy=AgentRunPolicy(target_chapter_ids=(5,)),
    )

    task = run.tasks[0]
    assert task.status == "blocked"
    assert task.terminal_state == "blocked_needs_more_facts"
    assert task.failure_category == "fact_gap"
    assert len(task.attempts) == 1


def test_repair_budget_exhausted_records_each_regenerate_attempt() -> None:
    """验证修复预算耗尽前每次 regenerate 都进入 attempt ledger。"""

    writer = _FakeWriter()
    auditor = _FakeAuditor(
        (
            "BLOCKING|chapter|fixture semantic repair",
            "BLOCKING|chapter|fixture semantic repair",
        )
    )

    run = run_agent_body_chapters(
        _projection((1,)),
        llm_clients=AgentLLMClients(writer=writer, auditor=auditor),
        policy=AgentRunPolicy(
            target_chapter_ids=(1,),
            repair_policy=AgentRepairPolicy(max_content_repair_attempts=1),
        ),
    )

    task = run.tasks[0]
    assert task.status == "failed"
    assert task.terminal_state == "blocked_repair_budget_exhausted"
    assert len(writer.requests) == 2
    assert [attempt.attempt_index for attempt in task.attempts] == [0, 1]


def test_chapter5_audit_parse_repair_attempt_carries_forbidden_phrase_guidance() -> None:
    """验证第 5 章 audit parse repair attempt 携带 forbidden phrase 改写清单。"""

    writer = _FakeWriter()
    auditor = _FakeAuditor(("这不是合法行协议", "PASS|chapter|no issues"))

    run = run_agent_body_chapters(
        _projection((5,)),
        llm_clients=AgentLLMClients(writer=writer, auditor=auditor),
        policy=AgentRunPolicy(
            target_chapter_ids=(5,),
            repair_policy=AgentRepairPolicy(max_content_repair_attempts=1),
        ),
    )

    assert run.status == "accepted"
    assert [request.chapter_id for request in writer.requests] == [5, 5]
    assert writer.requests[0].repair_context is None
    repair_context = writer.requests[1].repair_context
    assert repair_context is not None
    assert "llm:parse_failure" in repair_context.previous_issue_ids
    assert "第5章 forbidden phrase repair 必须改写规则" in writer.requests[1].user_prompt
    assert "值得持有 / 需要关注 / 建议替换" in writer.requests[1].user_prompt


def test_chapter_6_invalid_anchor_marker_retries_once_and_accepts() -> None:
    """验证第 6 章 invalid anchor marker 可消耗既有预算重写并接受。"""

    def _first_invalid_then_valid(request: ChapterLLMRequest) -> str:
        if request.repair_context is None:
            return _invalid_anchor_markdown_from_request(request)
        return _valid_agent_markdown_from_request(request)

    writer = _FakeWriter(actions={6: _first_invalid_then_valid})

    run = run_agent_body_chapters(
        _projection((6,)),
        llm_clients=AgentLLMClients(writer=writer, auditor=_FakeAuditor()),
        policy=AgentRunPolicy(
            target_chapter_ids=(6,),
            repair_policy=AgentRepairPolicy(max_content_repair_attempts=1),
        ),
    )

    task = run.tasks[0]
    assert run.status == "accepted"
    assert task.status == "accepted"
    assert [request.chapter_id for request in writer.requests] == [6, 6]
    assert [attempt.attempt_index for attempt in task.attempts] == [0, 1]
    repair_context = writer.requests[1].repair_context
    assert repair_context is not None
    assert repair_context.attempt_index == 1
    assert any(
        issue_id.startswith("writer:invalid_anchor_marker")
        for issue_id in repair_context.previous_issue_ids
    )
    assert any(
        "<!-- anchor:<anchor_id> -->" in correction
        for correction in repair_context.required_corrections
    )


def test_chapter_6_invalid_anchor_marker_twice_fails_closed_after_one_retry() -> None:
    """验证第 6 章 invalid anchor marker 第二次仍失败时无隐藏第三次重试。"""

    writer = _FakeWriter(actions={6: _invalid_anchor_markdown_from_request})

    run = run_agent_body_chapters(
        _projection((6,)),
        llm_clients=AgentLLMClients(writer=writer, auditor=_FakeAuditor()),
        policy=AgentRunPolicy(
            target_chapter_ids=(6,),
            repair_policy=AgentRepairPolicy(max_content_repair_attempts=1),
        ),
    )

    task = run.tasks[0]
    assert run.status == "blocked"
    assert task.status == "blocked"
    assert task.terminal_state == "blocked_prompt_contract"
    assert task.stop_reason == "llm_contract_violation"
    assert task.failure_category == "prompt_contract"
    assert [request.chapter_id for request in writer.requests] == [6, 6]
    assert [attempt.attempt_index for attempt in task.attempts] == [0, 1]
    assert writer.requests[0].repair_context is None
    assert writer.requests[1].repair_context is not None


def test_chapter_6_invalid_anchor_marker_budget_zero_does_not_retry() -> None:
    """回归守卫：第 6 章预算为 0 时 invalid anchor marker 不重试。"""

    writer = _FakeWriter(actions={6: _invalid_anchor_markdown_from_request})

    run = run_agent_body_chapters(
        _projection((6,)),
        llm_clients=AgentLLMClients(writer=writer, auditor=_FakeAuditor()),
        policy=AgentRunPolicy(
            target_chapter_ids=(6,),
            repair_policy=AgentRepairPolicy(max_content_repair_attempts=0),
        ),
    )

    task = run.tasks[0]
    assert run.status == "blocked"
    assert task.status == "blocked"
    assert task.stop_reason == "llm_contract_violation"
    assert len(writer.requests) == 1
    assert writer.requests[0].repair_context is None
    assert [attempt.attempt_index for attempt in task.attempts] == [0]


def test_non_chapter_6_invalid_anchor_marker_does_not_retry() -> None:
    """回归守卫：非第 6 章 invalid anchor marker 保持一次 writer 后 fail-closed。"""

    writer = _FakeWriter(actions={5: _invalid_anchor_markdown_from_request})

    run = run_agent_body_chapters(
        _projection((5,)),
        llm_clients=AgentLLMClients(writer=writer, auditor=_FakeAuditor()),
        policy=AgentRunPolicy(
            target_chapter_ids=(5,),
            repair_policy=AgentRepairPolicy(max_content_repair_attempts=1),
        ),
    )

    task = run.tasks[0]
    assert run.status == "blocked"
    assert task.status == "blocked"
    assert task.stop_reason == "llm_contract_violation"
    assert len(writer.requests) == 1
    assert writer.requests[0].repair_context is None
    assert [attempt.attempt_index for attempt in task.attempts] == [0]


def test_cancel_before_first_chapter_fails_closed_without_generation() -> None:
    """验证首章前取消不生成正文。"""

    writer = _FakeWriter()

    def _checker(
        phase: str,
        chapter_id: int | None,
        attempt_index: int | None,
    ) -> AgentSchedulerInterruption:
        return AgentSchedulerInterruption(
            status="cancelled",
            reason="cancelled by host",
            phase=phase,
            chapter_id=chapter_id,
            attempt_index=attempt_index,
        )

    run = run_agent_body_chapters(
        _projection((1, 2)),
        llm_clients=AgentLLMClients(writer=writer, auditor=_FakeAuditor()),
        policy=AgentRunPolicy(target_chapter_ids=(1, 2)),
        interruption_checker=_checker,
    )

    assert run.status == "blocked"
    assert run.scheduler_interruption is not None
    assert run.scheduler_interruption.status == "cancelled"
    assert writer.requests == []
    assert all(task.terminal_state == "blocked_scheduler_interrupted" for task in run.tasks)
    assert all(task.stop_reason == "scheduler_cancelled" for task in run.tasks)
    assert all(task.failure_category == "scheduler_cancelled" for task in run.tasks)


def test_deadline_between_writer_and_auditor_fails_closed_without_budget_use() -> None:
    """验证 writer/auditor 间 deadline 中断不进入 auditor 或 repair。"""

    writer = _FakeWriter()
    auditor = _FakeAuditor()

    def _checker(
        phase: str,
        chapter_id: int | None,
        attempt_index: int | None,
    ) -> AgentSchedulerInterruption:
        if phase == "between_writer_and_auditor":
            return AgentSchedulerInterruption(
                status="deadline_exceeded",
                reason="deadline",
                phase=phase,
                chapter_id=chapter_id,
                attempt_index=attempt_index,
            )
        return AgentSchedulerInterruption(
            status="none",
            reason=None,
            phase=phase,
            chapter_id=chapter_id,
            attempt_index=attempt_index,
        )

    run = run_agent_body_chapters(
        _projection((1,)),
        llm_clients=AgentLLMClients(writer=writer, auditor=auditor),
        policy=AgentRunPolicy(target_chapter_ids=(1,)),
        interruption_checker=_checker,
    )

    task = run.tasks[0]
    assert task.terminal_state == "blocked_scheduler_interrupted"
    assert task.stop_reason == "scheduler_deadline_exceeded"
    assert task.failure_category == "scheduler_deadline_exceeded"
    assert len(writer.requests) == 1
    assert auditor.requests == []
    assert len(task.attempts) == 1
    assert len(task.attempts[0].tool_traces) == 1


def test_deadline_after_programmatic_audit_fails_closed_before_llm_auditor() -> None:
    """验证程序审计后 deadline 中断不继续调用 LLM auditor。"""

    writer = _FakeWriter()
    auditor = _FakeAuditor()

    def _checker(
        phase: str,
        chapter_id: int | None,
        attempt_index: int | None,
    ) -> AgentSchedulerInterruption:
        if phase == "between_programmatic_and_llm_auditor":
            return AgentSchedulerInterruption(
                status="deadline_exceeded",
                reason="deadline",
                phase=phase,
                chapter_id=chapter_id,
                attempt_index=attempt_index,
            )
        return AgentSchedulerInterruption(
            status="none",
            reason=None,
            phase=phase,
            chapter_id=chapter_id,
            attempt_index=attempt_index,
        )

    run = run_agent_body_chapters(
        _projection((1,)),
        llm_clients=AgentLLMClients(writer=writer, auditor=auditor),
        policy=AgentRunPolicy(target_chapter_ids=(1,)),
        interruption_checker=_checker,
    )

    task = run.tasks[0]
    assert task.terminal_state == "blocked_scheduler_interrupted"
    assert task.stop_reason == "scheduler_deadline_exceeded"
    assert task.failure_category == "scheduler_deadline_exceeded"
    assert len(writer.requests) == 1
    assert auditor.requests == []
    assert len(task.attempts) == 1
    assert [trace.request.tool_name for trace in task.attempts[0].tool_traces] == [
        "fund.write_chapter",
        "fund.audit_chapter_programmatic",
    ]


def test_legacy_contract_does_not_derive_typed_evidence_availability(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """验证 legacy path 不读取 typed availability sidecar。"""

    def _unexpected_availability(_: object) -> object:
        raise AssertionError("legacy path must not derive typed evidence availability")

    monkeypatch.setattr(
        runner_module,
        "derive_evidence_availability",
        _unexpected_availability,
    )

    run = run_agent_body_chapters(
        _projection((1,)),
        llm_clients=AgentLLMClients(writer=_FakeWriter(), auditor=_FakeAuditor()),
        policy=AgentRunPolicy(target_chapter_ids=(1,), typed_template_path="legacy_contract"),
    )

    assert run.status == "accepted"
    assert run.evidence_availability.requirements == ()


def test_agent_runner_does_not_import_host_or_service() -> None:
    """验证 Agent runner 不导入 Host 或 Service。"""

    source = inspect.getsource(runner_module)
    tree = ast.parse(source)
    imported_modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_modules.update(alias.name for alias in node.names)
        if isinstance(node, ast.ImportFrom) and node.module is not None:
            imported_modules.add(node.module)

    assert not any(module.startswith("fund_agent.host") for module in imported_modules)
    assert not any(module.startswith("fund_agent.services") for module in imported_modules)


def _projection(chapter_ids: tuple[int, ...]) -> object:
    """构造测试 projection。"""

    return project_chapter_facts(_bundle(), chapter_ids=chapter_ids)


def _projection_with_missing_portfolio_managers() -> object:
    """构造第 3 章基金经理基本信息缺少已复核证据的 projection。"""

    missing_portfolio_managers = ExtractedField(
        value=None,
        anchors=(),
        extraction_mode="missing",
        note="no-live missing portfolio managers",
    )
    return project_chapter_facts(
        replace(_bundle(), portfolio_managers=missing_portfolio_managers),
        chapter_ids=(3,),
    )


def _projection_with_missing_chapter_2_evidence() -> object:
    """构造第 2 章收益与成本证据缺少已复核证据的 projection。"""

    missing_nav = ExtractedField(
        value=None,
        anchors=(),
        extraction_mode="missing",
        note="no-live missing nav benchmark performance",
    )
    missing_fee = ExtractedField(
        value=None,
        anchors=(),
        extraction_mode="missing",
        note="no-live missing fee schedule",
    )
    return project_chapter_facts(
        replace(
            _bundle(),
            nav_benchmark_performance=missing_nav,
            fee_schedule=missing_fee,
        ),
        chapter_ids=(2,),
    )


def _required_items_from_request(request: ChapterLLMRequest) -> tuple[str, ...]:
    """从 writer prompt 中提取 required output stable ids。"""

    marker = "必须输出项："
    for line in request.user_prompt.splitlines():
        if line.startswith(marker):
            parsed = ast.literal_eval(line.removeprefix(marker))
            return tuple(_required_item_from_prompt_payload(item) for item in parsed)
    raise ValueError("writer request 缺少 required output items")


def _required_item_from_prompt_payload(item: str) -> str:
    """从 typed prompt payload 中提取 required output stable id。"""

    first_line = item.splitlines()[0] if item else ""
    if first_line.startswith("<!-- required_output:") and first_line.endswith(" -->"):
        return first_line.removeprefix("<!-- required_output:").removesuffix(" -->")
    return item


def _chapter_2_markdown_with_gap(request: ChapterLLMRequest) -> str:
    """构造第 2 章 approved gap/minimum-verification Markdown。"""

    marker_text = "\n".join(
        f"<!-- required_output:{item} -->\n"
        "- 证据不足，不能完成具体 R=A+B-C 数字闭环。"
        "下一步最小验证问题：复核同源年报中的基金收益、基准收益和费用口径。"
        for item in _required_items_from_request(request)
    )
    markdown = _valid_agent_markdown_from_request(request)
    start = markdown.find("<!-- required_output:")
    end = markdown.find("### 详细情况")
    if start < 0 or end < 0:
        raise AssertionError("第 2 章测试 Markdown 缺少 required output 区段")
    return markdown[:start] + marker_text + "\n" + markdown[end:]


def _chapter_2_markdown_without_gap_phrase(request: ChapterLLMRequest) -> str:
    """构造第 2 章缺少 approved gap wording 的 Markdown。"""

    marker_text = "\n".join(
        f"<!-- required_output:{item} -->\n- {item}: 已根据结构化事实说明。"
        for item in _required_items_from_request(request)
    )
    markdown = _valid_agent_markdown_from_request(request)
    start = markdown.find("<!-- required_output:")
    end = markdown.find("### 详细情况")
    if start < 0 or end < 0:
        raise AssertionError("第 2 章测试 Markdown 缺少 required output 区段")
    return markdown[:start] + marker_text + "\n" + markdown[end:]


def _chapter_3_markdown_with_item01_gap(request: ChapterLLMRequest) -> str:
    """构造 item 01 使用 approved gap wording 的第 3 章 Markdown。"""

    markdown = _valid_agent_markdown_from_request(request)
    return markdown.replace(
        "<!-- required_output:ch3.required_output.item_01 -->",
        "<!-- required_output:ch3.required_output.item_01 -->\n"
        "- 基金经理基本信息证据不足，不能据此判断基金经理基本信息。",
        1,
    )


def _chapter_3_markdown_without_item01_gap(request: ChapterLLMRequest) -> str:
    """构造 item 01 保留 marker 但缺少 approved gap wording 的第 3 章 Markdown。"""

    marker = "<!-- required_output:ch3.required_output.item_01 -->"
    markdown = _valid_agent_markdown_from_request(request)
    start = markdown.find(marker)
    if start < 0:
        raise AssertionError("第 3 章测试 Markdown 缺少 item 01 marker")
    segment_start = start + len(marker)
    next_start = markdown.find("<!-- required_output:", segment_start)
    if next_start < 0:
        raise AssertionError("第 3 章测试 Markdown 缺少 item 01 后续 marker")
    return (
        markdown[:segment_start]
        + "\n- 基金经理基本信息：已根据结构化事实说明。\n"
        + markdown[next_start:]
    )


def _valid_agent_markdown_from_request(request: ChapterLLMRequest) -> str:
    """构造适配当前 Agent runner 测试的合法章节 Markdown。"""

    markdown = _valid_markdown_from_request(request)
    if request.chapter_id == 3:
        return (
            markdown.replace(
            "本章只使用已断言事实，并把候选 facet 写成未断言。",
            "本章仅记录已披露事实；证据不足时不输出一致性结论。",
        )
            .replace(
                "- 言行一致性判断: 已根据结构化事实说明。",
                "- 证据不足，不输出一致性结论。下一步最小验证问题：补齐已复核行为证据。",
            )
            .replace(
                "- 风格稳定性判断: 已根据结构化事实说明。",
                "- 数据不足，不能据此判断风格。下一步最小验证问题：补齐跨期持仓证据。",
            )
        )
    return markdown


def _invalid_anchor_markdown_from_request(request: ChapterLLMRequest) -> str:
    """构造非法 anchor marker 章节 Markdown。"""

    return _valid_agent_markdown_from_request(request).replace("<!-- anchor:", "<!-- ANCHOR:", 1)
