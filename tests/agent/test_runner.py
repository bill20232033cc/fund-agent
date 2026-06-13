"""Agent runner 测试，见模板第 1-6 章。"""

from __future__ import annotations

import ast
import inspect

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
        text = action if isinstance(action, str) else _valid_agent_markdown_from_request(request)
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
