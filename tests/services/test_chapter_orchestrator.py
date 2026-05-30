"""Gate 3 Service 章节编排器测试，覆盖基金分析模板第 1-6 章。"""

from __future__ import annotations

import ast
from dataclasses import dataclass, replace
from pathlib import Path

import pytest

from fund_agent.fund.chapter_auditor import (
    ChapterAuditIssue,
    ChapterAuditLLMRequest,
    ChapterAuditLLMResponse,
    ChapterAuditRepairHint,
    ChapterAuditResult,
    ChapterLLMAuditResult,
    ChapterProgrammaticAuditResult,
)
from fund_agent.fund.chapter_facts import (
    project_chapter_facts,
)
from fund_agent.fund.chapter_writer import (
    ChapterLLMRequest,
    ChapterLLMResponse,
    ChapterWriteStopReason,
)
from fund_agent.services.chapter_orchestrator import (
    ChapterOrchestrationPolicy,
    ChapterOrchestrator,
    ChapterOrchestratorLLMClients,
    _decide_repair,
    _map_writer_stop_reason,
    _stop_reason_from_repair_decision,
    build_chapter_orchestration_input,
    orchestrate_chapters,
)
from tests.fund.test_chapter_facts import _bundle, _field


class _FakeChapterLLMClient:
    """测试用章节写作 fake client，只存在于 Service 测试。

    Attributes:
        texts: 按调用顺序返回的章节 Markdown。
        requests: 收到的 typed writer requests。
        raises: 是否抛出异常。
    """

    def __init__(self, texts: tuple[str, ...] = (), *, raises: bool = False) -> None:
        """初始化 fake writer。

        Args:
            texts: 固定返回文本序列；为空时按请求动态生成合法章节。
            raises: 是否在调用时抛出异常。

        Returns:
            无返回值。

        Raises:
            无显式抛出。
        """

        self.texts = list(texts)
        self.raises = raises
        self.requests: list[ChapterLLMRequest] = []

    def generate_chapter(self, request: ChapterLLMRequest) -> ChapterLLMResponse:
        """返回 fake 章节写作响应。

        Args:
            request: writer typed request。

        Returns:
            fake LLM 响应。

        Raises:
            RuntimeError: 当 `raises=True` 时抛出。
        """

        self.requests.append(request)
        if self.raises:
            raise RuntimeError("writer exploded")
        text = self.texts.pop(0) if self.texts else _valid_markdown_from_request(request)
        return ChapterLLMResponse(text=text, model_name="fake-writer", finish_reason="stop")


class _FakeAuditLLMClient:
    """测试用章节审计 fake client，只存在于 Service 测试。

    Attributes:
        raw_responses: 按调用顺序返回的 LLM audit 行协议。
        requests: 收到的 typed audit requests。
        raises: 是否抛出异常。
    """

    def __init__(self, raw_responses: tuple[str, ...] = (), *, raises: bool = False) -> None:
        """初始化 fake auditor。

        Args:
            raw_responses: 固定返回行协议序列；为空时默认 PASS。
            raises: 是否在调用时抛出异常。

        Returns:
            无返回值。

        Raises:
            无显式抛出。
        """

        self.raw_responses = list(raw_responses)
        self.raises = raises
        self.requests: list[ChapterAuditLLMRequest] = []

    def audit_chapter(self, request: ChapterAuditLLMRequest) -> ChapterAuditLLMResponse:
        """返回 fake 章节审计响应。

        Args:
            request: auditor typed request。

        Returns:
            fake LLM audit 响应。

        Raises:
            RuntimeError: 当 `raises=True` 时抛出。
        """

        self.requests.append(request)
        if self.raises:
            raise RuntimeError("auditor exploded")
        raw_text = self.raw_responses.pop(0) if self.raw_responses else "PASS|chapter|no issues"
        return ChapterAuditLLMResponse(raw_text=raw_text, model_name="fake-auditor", finish_reason="stop")


_DEFAULT_CLIENT = object()


class _RecordingFactProvider:
    """测试用 Gate 1 provider，记录投影请求。

    Attributes:
        calls: 收到的 `(fund_code, chapter_ids)` 调用。
    """

    def __init__(self) -> None:
        """初始化记录 provider。

        Args:
            无。

        Returns:
            无返回值。

        Raises:
            无显式抛出。
        """

        self.calls: list[tuple[str, tuple[int, ...]]] = []

    def project(self, bundle: object, *, chapter_ids: tuple[int, ...] = tuple(range(8))) -> object:
        """记录并委托 Gate 1 projection。

        Args:
            bundle: 测试结构化数据包。
            chapter_ids: 请求章节编号。

        Returns:
            Gate 1 projection。

        Raises:
            ValueError: 当 Gate 1 投影校验失败时抛出。
        """

        self.calls.append((bundle.fund_code, chapter_ids))
        return project_chapter_facts(bundle, chapter_ids=chapter_ids)


def test_accepts_bundle_input_and_projects_requested_chapters() -> None:
    """验证 bundle 输入会通过注入 provider 投影第 1-6 章。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 provider 注入或章节范围错误时抛出。
    """

    provider = _RecordingFactProvider()
    policy = ChapterOrchestrationPolicy(target_chapter_ids=(1,))
    input_data = build_chapter_orchestration_input(
        fund_code="110011",
        report_year=2024,
        structured_data=_bundle(),
        policy=policy,
    )

    result = orchestrate_chapters(input_data, llm_clients=_clients(), fact_provider=provider)

    assert provider.calls == [("110011", (1,))]
    assert result.status == "accepted"
    assert result.generated_chapter_ids == (1,)


def test_accepts_projection_input_without_calling_fact_provider() -> None:
    """验证 projection 输入不会二次调用 fact provider，见模板第 1 章。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 projection 路径误调用 provider 时抛出。
    """

    provider = _RecordingFactProvider()
    projection = project_chapter_facts(_bundle(), chapter_ids=(1,))
    input_data = build_chapter_orchestration_input(
        fund_code="110011",
        report_year=2024,
        chapter_projection=projection,
        policy=ChapterOrchestrationPolicy(target_chapter_ids=(1,)),
    )

    result = orchestrate_chapters(input_data, llm_clients=_clients(), fact_provider=provider)

    assert provider.calls == []
    assert result.status == "accepted"


def test_rejects_invalid_input_payload_shapes() -> None:
    """验证 bundle/projection 输入必须显式互斥。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当非法 payload 未抛出 `ValueError` 时抛出。
    """

    projection = project_chapter_facts(_bundle(), chapter_ids=(1,))
    with pytest.raises(ValueError):
        build_chapter_orchestration_input(
            fund_code="110011",
            report_year=2024,
            structured_data=_bundle(),
            chapter_projection=projection,
        )
    with pytest.raises(ValueError):
        build_chapter_orchestration_input(fund_code="110011", report_year=2024)


def test_rejects_fund_identity_mismatch() -> None:
    """验证 fund_code/report_year 必须与输入 payload 同源。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 identity mismatch 未抛出 `ValueError` 时抛出。
    """

    with pytest.raises(ValueError):
        build_chapter_orchestration_input(
            fund_code="000001",
            report_year=2024,
            structured_data=_bundle(),
        )
    with pytest.raises(ValueError):
        build_chapter_orchestration_input(
            fund_code="110011",
            report_year=2025,
            chapter_projection=project_chapter_facts(_bundle(), chapter_ids=(1,)),
        )


def test_policy_rejects_chapter_zero_seven_duplicates_and_invalid_numbers() -> None:
    """验证 Gate 3 policy 只接受模板第 1-6 章且章节唯一。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当非法章节编号未抛出 `ValueError` 时抛出。
    """

    for chapter_ids in ((), (0,), (7,), (1, 1), (-1,), (8,)):
        with pytest.raises(ValueError):
            ChapterOrchestrationPolicy(target_chapter_ids=chapter_ids)


def test_policy_rejects_negative_retry_and_non_positive_output_chars() -> None:
    """验证 retry budget 和输出上限 fail-closed。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当非法策略未抛出 `ValueError` 时抛出。
    """

    with pytest.raises(ValueError):
        ChapterOrchestrationPolicy(max_repair_attempts=-1)
    with pytest.raises(ValueError):
        ChapterOrchestrationPolicy(max_output_chars=0)


def test_happy_path_accepts_single_chapter_with_fake_writer_and_auditor() -> None:
    """验证第 1 章写作和审计 happy path accepted。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 happy path 未 accepted 时抛出。
    """

    writer = _FakeChapterLLMClient()
    auditor = _FakeAuditLLMClient()

    result = _orchestrate_one(writer=writer, auditor=auditor)

    assert result.status == "accepted"
    assert result.chapter_results[0].status == "accepted"
    assert result.accepted_conclusions[0].chapter_id == 1
    assert writer.requests[0].chapter_id == 1
    assert auditor.requests[0].chapter_id == 1


def test_writer_unavailable_blocks_and_does_not_call_auditor() -> None:
    """验证 writer client 缺失时阻断且不调用 auditor。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 auditor 被误调用时抛出。
    """

    auditor = _FakeAuditLLMClient()

    result = _orchestrate_one(writer=None, auditor=auditor)

    run = result.chapter_results[0]
    assert result.status == "blocked"
    assert run.status == "blocked"
    assert run.stop_reason == "llm_unavailable"
    assert run.attempts[0].audit_result is None
    assert auditor.requests == []


def test_auditor_unavailable_blocks_before_writer_when_llm_audit_enabled() -> None:
    """验证 auditor 缺失时全局 early stop，不调用 writer。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 writer 被误调用时抛出。
    """

    writer = _FakeChapterLLMClient()

    result = _orchestrate_one(writer=writer, auditor=None)

    assert result.status == "blocked"
    assert result.generated_chapter_ids == ()
    assert result.chapter_results[0].stop_reason == "llm_unavailable"
    assert result.chapter_results[0].attempts == ()
    assert writer.requests == []


def test_every_writer_stop_reason_maps_to_exact_run_reason() -> None:
    """验证每个 Gate 2 writer stop reason 都有一对一 Service 映射。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当映射缺失或歧义时抛出。
    """

    expected = {
        "fund_type_unknown": "fund_type_unknown",
        "missing_required_facts": "missing_required_facts",
        "evidence_anchor_missing": "missing_required_facts",
        "item_rule_deleted_required_content": "missing_required_facts",
        "chapter_requires_accepted_conclusions": "dependency_missing",
        "prompt_only": "writer_blocked",
        "llm_unavailable": "llm_unavailable",
        "llm_empty_response": "llm_empty_response",
        "llm_contract_violation": "llm_contract_violation",
    }
    assert set(expected) == set(ChapterWriteStopReason.__args__) - {"none"}
    for writer_stop_reason, run_stop_reason in expected.items():
        status, mapped_stop_reason = _map_writer_stop_reason(writer_stop_reason)
        assert status == "blocked"
        assert mapped_stop_reason == run_stop_reason


def test_writer_exception_becomes_llm_exception_and_does_not_leak() -> None:
    """验证 writer client 异常转为 Service fail-closed 状态。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当异常泄漏或状态错误时抛出。
    """

    result = _orchestrate_one(writer=_FakeChapterLLMClient(raises=True), auditor=_FakeAuditLLMClient())

    run = result.chapter_results[0]
    assert result.status == "blocked"
    assert run.status == "failed"
    assert run.stop_reason == "llm_exception"
    assert run.attempts == ()


def test_auditor_exception_becomes_llm_exception_and_records_writer_attempt() -> None:
    """验证 auditor client 异常转为 fail-closed 且保留 writer attempt。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 writer attempt 丢失或异常泄漏时抛出。
    """

    result = _orchestrate_one(writer=_FakeChapterLLMClient(), auditor=_FakeAuditLLMClient(raises=True))

    run = result.chapter_results[0]
    assert result.status == "blocked"
    assert run.stop_reason == "llm_exception"
    assert len(run.attempts) == 1
    assert run.attempts[0].audit_result is None


def test_unknown_fund_type_returns_global_blocked_without_writer_calls() -> None:
    """验证基金类型 unknown 时全局阻断且不调用 writer。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 unknown 类型进入 writer 时抛出。
    """

    writer = _FakeChapterLLMClient()
    projection = project_chapter_facts(
        replace(_bundle(), basic_identity=_field({"classification_basis": ("fixture",)}, "basic_identity")),
        chapter_ids=(1, 2),
    )
    input_data = build_chapter_orchestration_input(
        fund_code="110011",
        report_year=2024,
        chapter_projection=projection,
        policy=ChapterOrchestrationPolicy(target_chapter_ids=(1, 2)),
    )

    result = orchestrate_chapters(input_data, llm_clients=_clients(writer=writer))

    assert result.status == "blocked"
    assert [run.stop_reason for run in result.chapter_results] == [
        "fund_type_unknown",
        "fund_type_unknown",
    ]
    assert writer.requests == []


def test_repairable_audit_failure_retries_and_second_pass_accepts() -> None:
    """验证 patch/regenerate hint 在预算内映射为整章 regenerate。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 repair retry 未执行或未 accepted 时抛出。
    """

    bad = "### 结论要点\n缺少 required output。\n### 详细情况\n### 证据与出处\n"
    writer = _FakeChapterLLMClient((bad,))

    result = _orchestrate_one(writer=writer, auditor=_FakeAuditLLMClient())

    run = result.chapter_results[0]
    assert run.status == "accepted"
    assert len(run.attempts) == 2
    assert run.attempts[0].repair_decision is not None
    assert run.attempts[0].repair_decision.action == "regenerate"


def test_repair_budget_exhausted_returns_failed_stop_reason() -> None:
    """验证 repair budget 耗尽时返回 repair_budget_exhausted。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当预算耗尽未 fail-closed 时抛出。
    """

    bad = "### 结论要点\n缺少 required output。\n### 详细情况\n### 证据与出处\n"
    writer = _FakeChapterLLMClient((bad, bad))

    result = _orchestrate_one(writer=writer, auditor=_FakeAuditLLMClient())

    run = result.chapter_results[0]
    assert run.status == "failed"
    assert run.stop_reason == "repair_budget_exhausted"
    assert len(run.attempts) == 2
    repair_decision = run.attempts[-1].repair_decision
    assert repair_decision is not None
    assert repair_decision.stop_reason == "repair_budget_exhausted"


def test_repair_budget_exhausted_stop_reason_does_not_depend_on_reason_text() -> None:
    """验证 repair budget 耗尽 stop reason 不依赖中文 reason 文案。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 stop reason 仍依赖 reason 文案时抛出。
    """

    decision = _decide_repair(
        _audit_result_with_hint("regenerate"),
        remaining_budget=0,
        auditor_available=True,
        run_llm_audit=True,
    )
    renamed_decision = replace(decision, reason="可读文案允许调整。")

    assert decision.stop_reason == "repair_budget_exhausted"
    assert _stop_reason_from_repair_decision(renamed_decision) == "repair_budget_exhausted"


def test_max_repair_attempts_zero_does_not_retry_after_audit_failure() -> None:
    """验证 max_repair_attempts=0 时初始审计失败后不重试。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 retry budget 0 仍重试时抛出。
    """

    bad = "### 结论要点\n缺少 required output。\n### 详细情况\n### 证据与出处\n"
    writer = _FakeChapterLLMClient((bad,))

    result = _orchestrate_one(
        writer=writer,
        auditor=_FakeAuditLLMClient(),
        policy=ChapterOrchestrationPolicy(target_chapter_ids=(1,), max_repair_attempts=0),
    )

    run = result.chapter_results[0]
    assert run.stop_reason == "repair_budget_exhausted"
    assert len(run.attempts) == 1
    assert len(writer.requests) == 1


def test_auditor_llm_unavailable_issue_stops_without_writer_retry() -> None:
    """验证 auditor 返回 LLM_UNAVAILABLE issue 时不重试 writer。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 LLM unavailable 被误重试时抛出。
    """

    audit_result = _audit_result_with_hint("regenerate", llm_unavailable=True)

    decision = _decide_repair(
        audit_result,
        remaining_budget=1,
        auditor_available=False,
        run_llm_audit=True,
    )

    assert decision.action == "stop"
    assert decision.source_repair_hint == "regenerate"


def test_needs_more_facts_stops_without_retrying_source_access() -> None:
    """验证 needs_more_facts 停止本章且不 source probing。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 needs_more_facts 被误重试时抛出。
    """

    audit_result = _audit_result_with_hint("needs_more_facts")

    decision = _decide_repair(
        audit_result,
        remaining_budget=1,
        auditor_available=True,
        run_llm_audit=True,
    )

    assert decision.action == "needs_more_facts"
    assert decision.issue_ids


def test_fail_fast_true_skips_later_chapters_after_first_blocked() -> None:
    """验证 fail_fast=True 时前章阻断会跳过后续章节。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当后续章节未跳过时抛出。
    """

    result = _orchestrate(
        policy=ChapterOrchestrationPolicy(target_chapter_ids=(1, 2), fail_fast=True),
        writer=None,
        auditor=_FakeAuditLLMClient(),
    )

    assert result.status == "blocked"
    assert result.chapter_results[0].stop_reason == "llm_unavailable"
    assert result.chapter_results[1].status == "skipped"
    assert result.skipped_chapter_ids == (2,)


def test_fail_fast_false_continues_and_returns_partial() -> None:
    """验证 fail_fast=False 时后续章节继续执行并可返回 partial。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 partial 状态或继续执行错误时抛出。
    """

    bad = "### 结论要点\n缺少 required output。\n### 详细情况\n### 证据与出处\n"
    writer = _FakeChapterLLMClient((bad, bad))

    result = _orchestrate(
        policy=ChapterOrchestrationPolicy(target_chapter_ids=(1, 2), fail_fast=False),
        writer=writer,
        auditor=_FakeAuditLLMClient(),
    )

    assert result.status == "partial"
    assert result.chapter_results[0].stop_reason == "repair_budget_exhausted"
    assert result.chapter_results[1].status == "accepted"


def test_heading_conclusion_extraction_stops_before_next_heading() -> None:
    """验证 `### 结论要点` 抽取在下一个 `###` 或 `##` 截止。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当结论抽取越界时抛出。
    """

    result = _orchestrate_one(
        writer=_FakeChapterLLMClient((_valid_markdown_with_conclusion("第一行\n第二行"),)),
        auditor=_FakeAuditLLMClient(),
    )

    conclusion = result.accepted_conclusions[0]
    assert conclusion.conclusion_source == "heading"
    assert conclusion.conclusion_markdown == "第一行\n第二行"
    assert "详细情况" not in conclusion.conclusion_markdown


def test_h2_conclusion_extraction_stops_before_next_h2() -> None:
    """验证 `## 结论要点` 抽取在下一个 `##` 截止。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 H2 结论抽取越界时抛出。
    """

    markdown = _valid_markdown_with_conclusion("H2 结论", heading="## 结论要点", next_heading="## 详细情况")

    result = _orchestrate_one(writer=_FakeChapterLLMClient((markdown,)), auditor=_FakeAuditLLMClient())

    assert result.accepted_conclusions[0].conclusion_markdown == "H2 结论"


def test_fallback_conclusion_uses_first_three_non_empty_lines() -> None:
    """验证 accepted draft 无结论 heading 时 fallback 只取前三个非空行。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 fallback 抽取整章或超过三行时抛出。
    """

    policy = ChapterOrchestrationPolicy(
        target_chapter_ids=(1,),
        run_programmatic_audit=False,
        run_llm_audit=True,
    )
    markdown = "第一行\n\n第二行\n第三行\n第四行"

    result = _orchestrate_one(
        writer=_FakeChapterLLMClient((markdown,)),
        auditor=_FakeAuditLLMClient(),
        policy=policy,
    )

    conclusion = result.accepted_conclusions[0]
    assert conclusion.conclusion_source == "fallback_lines"
    assert conclusion.conclusion_markdown == "第一行\n第二行\n第三行"


def test_long_conclusion_is_capped_at_500_chars() -> None:
    """验证 accepted conclusion 有 500 字符硬上限。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当结论未截断或标记错误时抛出。
    """

    long_text = "结论" * 300

    result = _orchestrate_one(
        writer=_FakeChapterLLMClient((_valid_markdown_with_conclusion(long_text),)),
        auditor=_FakeAuditLLMClient(),
    )

    conclusion = result.accepted_conclusions[0]
    assert len(conclusion.conclusion_markdown) == 500
    assert conclusion.conclusion_truncated is True


def test_result_includes_accepted_conclusions_sorted_by_chapter_order() -> None:
    """验证 accepted conclusions 按章节顺序输出。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当结论顺序错误时抛出。
    """

    result = _orchestrate(policy=ChapterOrchestrationPolicy(target_chapter_ids=(2, 1)))

    assert result.status == "accepted"
    assert [conclusion.chapter_id for conclusion in result.accepted_conclusions] == [2, 1]


def test_result_excludes_chapter_zero_and_seven_generation_scope() -> None:
    """验证 Gate 3 不接受第 0/7 章生成，只保留第 1-6 章结论供后续 Gate 4。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当第 0/7 章进入生成范围时抛出。
    """

    result = _orchestrate(policy=ChapterOrchestrationPolicy(target_chapter_ids=(1, 6)))

    assert result.generated_chapter_ids == (1, 6)
    assert all(run.chapter_id not in (0, 7) for run in result.chapter_results)
    assert all(conclusion.chapter_id not in (0, 7) for conclusion in result.accepted_conclusions)


def test_chapter_orchestrator_facade_uses_injected_fact_provider() -> None:
    """验证 façade 与 standalone function 的 fact_provider 注入语义一致。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 façade 未使用注入 provider 时抛出。
    """

    provider = _RecordingFactProvider()
    input_data = build_chapter_orchestration_input(
        fund_code="110011",
        report_year=2024,
        structured_data=_bundle(),
        policy=ChapterOrchestrationPolicy(target_chapter_ids=(1,)),
    )

    result = ChapterOrchestrator(fact_provider=provider).orchestrate(
        input_data,
        llm_clients=_clients(),
    )

    assert result.status == "accepted"
    assert provider.calls == [("110011", (1,))]


def test_projection_must_cover_target_chapters_uniquely() -> None:
    """验证 projection 缺少目标章节时抛出调用方契约错误。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当缺章 projection 未抛出 `ValueError` 时抛出。
    """

    projection = project_chapter_facts(_bundle(), chapter_ids=(1,))
    input_data = build_chapter_orchestration_input(
        fund_code="110011",
        report_year=2024,
        chapter_projection=projection,
        policy=ChapterOrchestrationPolicy(target_chapter_ids=(1, 2)),
    )

    with pytest.raises(ValueError):
        orchestrate_chapters(input_data, llm_clients=_clients())


def test_chapter_orchestrator_imports_do_not_cross_forbidden_boundaries() -> None:
    """验证 Service orchestrator 不导入 source/PDF/provider/dayu 等越界模块。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当模块 import 越界时抛出。
    """

    imports = _imports_for(Path("fund_agent/services/chapter_orchestrator.py"))
    forbidden_fragments = (
        "documents",
        "repository",
        "cache",
        "pdf",
        "source",
        "downloader",
        "parser",
        "dayu",
        "openai",
        "httpx",
    )
    assert all(not any(fragment in module for fragment in forbidden_fragments) for module in imports)


def _clients(
    *,
    writer: _FakeChapterLLMClient | None = None,
    auditor: _FakeAuditLLMClient | None = None,
) -> ChapterOrchestratorLLMClients:
    """构造测试用 client bundle。

    Args:
        writer: 可选 fake writer；未提供时创建默认 fake。
        auditor: 可选 fake auditor；未提供时创建默认 fake。

    Returns:
        Service orchestrator client bundle。

    Raises:
        无显式抛出。
    """

    return ChapterOrchestratorLLMClients(
        writer=writer if writer is not None else _FakeChapterLLMClient(),
        auditor=auditor if auditor is not None else _FakeAuditLLMClient(),
    )


def _orchestrate_one(
    *,
    writer: _FakeChapterLLMClient | None,
    auditor: _FakeAuditLLMClient | None,
    policy: ChapterOrchestrationPolicy | None = None,
) -> object:
    """编排单个第 1 章测试用例。

    Args:
        writer: fake writer 或 `None`。
        auditor: fake auditor 或 `None`。
        policy: 可选编排策略。

    Returns:
        章节编排结果。

    Raises:
        ValueError: 当输入契约非法时抛出。
    """

    return _orchestrate(
        policy=policy or ChapterOrchestrationPolicy(target_chapter_ids=(1,)),
        writer=writer,
        auditor=auditor,
    )


def _orchestrate(
    *,
    policy: ChapterOrchestrationPolicy,
    writer: object = _DEFAULT_CLIENT,
    auditor: object = _DEFAULT_CLIENT,
) -> object:
    """按指定策略编排测试章节。

    Args:
        policy: 编排策略。
        writer: fake writer、`None` 或默认 sentinel。
        auditor: fake auditor、`None` 或默认 sentinel。

    Returns:
        章节编排结果。

    Raises:
        ValueError: 当输入契约非法时抛出。
    """

    writer_client = _FakeChapterLLMClient() if writer is _DEFAULT_CLIENT else writer
    auditor_client = _FakeAuditLLMClient() if auditor is _DEFAULT_CLIENT else auditor
    projection = project_chapter_facts(_bundle(), chapter_ids=policy.target_chapter_ids)
    input_data = build_chapter_orchestration_input(
        fund_code="110011",
        report_year=2024,
        chapter_projection=projection,
        policy=policy,
    )
    return orchestrate_chapters(
        input_data,
        llm_clients=ChapterOrchestratorLLMClients(writer=writer_client, auditor=auditor_client),
    )


def _orchestrate_with_writer_stop_reason(stop_reason: str) -> object:
    """构造触发指定 writer stop reason 的编排结果。

    Args:
        stop_reason: Gate 2 writer stop reason。

    Returns:
        章节编排结果。

    Raises:
        ValueError: 当 stop reason fixture 不支持时抛出。
    """

    if stop_reason in {"fund_type_unknown", "prompt_only", "chapter_requires_accepted_conclusions"}:
        status, run_stop_reason = _map_writer_stop_reason(stop_reason)
        return _MappedStopResult(status=status, stop_reason=run_stop_reason)
    if stop_reason == "llm_unavailable":
        return _orchestrate(
            policy=ChapterOrchestrationPolicy(target_chapter_ids=(1,)),
            writer=None,
            auditor=_FakeAuditLLMClient(),
        )
    text_by_reason = {
        "missing_required_facts": None,
        "evidence_anchor_missing": None,
        "item_rule_deleted_required_content": None,
        "chapter_requires_accepted_conclusions": None,
        "prompt_only": None,
        "llm_empty_response": "",
        "llm_contract_violation": "没有合法 marker 的正文",
    }
    if stop_reason not in text_by_reason:
        raise ValueError(f"unsupported fixture stop reason: {stop_reason}")
    if stop_reason in {
        "missing_required_facts",
        "evidence_anchor_missing",
        "item_rule_deleted_required_content",
    }:
        return _preflight_stop_result(stop_reason)
    return _orchestrate_one(
        writer=_FakeChapterLLMClient((text_by_reason[stop_reason],)),
        auditor=_FakeAuditLLMClient(),
    )


def _audit_result_with_hint(
    repair_hint: ChapterAuditRepairHint,
    *,
    llm_unavailable: bool = False,
) -> ChapterAuditResult:
    """构造 `_decide_repair()` 决策表测试用审计结果。

    Args:
        repair_hint: 聚合 repair hint。
        llm_unavailable: 是否构造 LLM_UNAVAILABLE issue。

    Returns:
        Gate 2 审计结果。

    Raises:
        无显式抛出。
    """

    rule_code = "LLM_UNAVAILABLE" if llm_unavailable else "C1"
    issue = ChapterAuditIssue(
        issue_id="audit:test",
        layer="llm",
        rule_code=rule_code,
        severity="blocking",
        message="fixture audit issue",
        location="chapter",
        repair_hint=repair_hint,
    )
    return ChapterAuditResult(
        status="blocked" if llm_unavailable else "fail",
        programmatic=ChapterProgrammaticAuditResult(status="pass", issues=(), checked_rules=()),
        llm=ChapterLLMAuditResult(
            status="blocked" if llm_unavailable else "fail",
            issues=(issue,),
            raw_response=None,
            model_name=None,
            finish_reason=None,
        ),
        accepted=False,
        repair_hint=repair_hint,
    )


def _preflight_stop_result(stop_reason: str) -> object:
    """构造触发 writer preflight stop reason 的结果。

    Args:
        stop_reason: Gate 2 writer preflight stop reason。

    Returns:
        章节编排结果。

    Raises:
        ValueError: 当 fixture 类型不支持时抛出。
    """

    if stop_reason == "missing_required_facts":
        bundle = replace(
            _bundle(),
            basic_identity=_field(None, "basic_identity", anchors=()),
            product_profile=_field(None, "product_profile", anchors=()),
            benchmark=_field(None, "benchmark", anchors=()),
            index_profile=_field(None, "index_profile", anchors=()),
            fee_schedule=_field(None, "fee_schedule", anchors=()),
        )
        projection = project_chapter_facts(bundle, chapter_ids=(1,))
    elif stop_reason == "evidence_anchor_missing":
        bundle = replace(
            _bundle(),
            basic_identity=_field(
                {"classified_fund_type": "active_fund", "classification_basis": ("fixture",)},
                "basic_identity",
                anchors=(),
            ),
        )
        projection = project_chapter_facts(bundle, chapter_ids=(1,))
    elif stop_reason == "item_rule_deleted_required_content":
        projection = project_chapter_facts(_bundle(fund_type="active_fund"), chapter_ids=(1,))
        chapter = projection.chapters[0]
        required_items = (*chapter.contract.required_output_items, "指数编制规则与成分股")
        projection = replace(
            projection,
            chapters=(replace(chapter, contract=replace(chapter.contract, required_output_items=required_items)),),
        )
    else:
        raise ValueError(f"unsupported preflight stop reason: {stop_reason}")
    input_data = build_chapter_orchestration_input(
        fund_code="110011",
        report_year=2024,
        chapter_projection=projection,
        policy=ChapterOrchestrationPolicy(target_chapter_ids=(1,)),
    )
    return orchestrate_chapters(input_data, llm_clients=_clients())


@dataclass(frozen=True, slots=True, kw_only=True)
class _MappedRun:
    """映射表测试用单章结果。"""

    status: str
    stop_reason: str


@dataclass(frozen=True, slots=True, kw_only=True)
class _MappedStopResult:
    """映射表测试用编排结果。"""

    status: str
    stop_reason: str

    @property
    def chapter_results(self) -> tuple[_MappedRun, ...]:
        """返回单章映射结果。

        Args:
            无。

        Returns:
            单章结果元组。

        Raises:
            无显式抛出。
        """

        return (_MappedRun(status=self.status, stop_reason=self.stop_reason),)


def _valid_markdown_from_request(request: ChapterLLMRequest) -> str:
    """按 writer request 构造合法章节 Markdown。

    Args:
        request: writer typed request。

    Returns:
        测试用章节 Markdown。

    Raises:
        无显式抛出。
    """

    anchor_id = request.required_anchor_ids[0]
    return _valid_markdown_from_parts(anchor_id, _required_items_from_request(request))


def _valid_markdown_from_projection(projection: object) -> str:
    """按 projection 构造引用第一 anchor 的章节 Markdown。

    Args:
        projection: Gate 1 projection。

    Returns:
        测试用章节 Markdown。

    Raises:
        AttributeError: 当 projection 不是 Gate 1 projection 时抛出。
    """

    chapter = projection.chapters[0]
    anchor_id = chapter.evidence_anchors[0].anchor_id
    return _valid_markdown_from_parts(anchor_id, chapter.contract.required_output_items)


def _valid_markdown_with_conclusion(
    conclusion: str,
    *,
    heading: str = "### 结论要点",
    next_heading: str = "### 详细情况",
) -> str:
    """构造带自定义结论段的合法章节 Markdown。

    Args:
        conclusion: 结论段内容。
        heading: 结论 heading。
        next_heading: 下一 heading。

    Returns:
        测试用章节 Markdown。

    Raises:
        无显式抛出。
    """

    projection = project_chapter_facts(_bundle(), chapter_ids=(1,))
    chapter = projection.chapters[0]
    anchor_id = chapter.evidence_anchors[0].anchor_id
    return (
        f"{heading}\n"
        f"{conclusion}\n"
        f"{next_heading}\n"
        f"{_required_lines(chapter.contract.required_output_items)}\n"
        "本章只使用已断言事实，并把候选 facet 写成未断言。\n"
        "### 证据与出处\n"
        f"<!-- anchor:{anchor_id} -->\n"
        "> 📎 证据：年报2024§§2表None行basic_identity（fixture）\n"
    )


def _valid_markdown_from_parts(anchor_id: str, required_items: tuple[str, ...]) -> str:
    """按 anchor 和 required item 构造合法章节 Markdown。

    Args:
        anchor_id: 证据锚点 ID。
        required_items: CHAPTER_CONTRACT required output items。

    Returns:
        测试用章节 Markdown。

    Raises:
        无显式抛出。
    """

    return (
        "### 结论要点\n"
        f"{_required_lines(required_items)}\n"
        "### 详细情况\n"
        "本章只使用已断言事实，并把候选 facet 写成未断言。\n"
        "### 证据与出处\n"
        f"<!-- anchor:{anchor_id} -->\n"
        "> 📎 证据：年报2024§§2表None行basic_identity（fixture）\n"
    )


def _required_items_from_request(request: ChapterLLMRequest) -> tuple[str, ...]:
    """从 writer prompt 文本中解析 required output items。

    Args:
        request: writer typed request。

    Returns:
        required output items。

    Raises:
        无显式抛出。
    """

    marker = "必须输出项："
    for line in request.user_prompt.splitlines():
        if line.startswith(marker):
            value = line.removeprefix(marker)
            parsed = ast.literal_eval(value)
            return tuple(parsed)
    return ()


def _required_lines(required_items: tuple[str, ...]) -> str:
    """构造 required output items 的测试正文行。

    Args:
        required_items: CHAPTER_CONTRACT required output items。

    Returns:
        Markdown 行文本。

    Raises:
        无显式抛出。
    """

    return "\n".join(f"- {item}: 已根据结构化事实说明。" for item in required_items)


def _imports_for(source_path: Path) -> set[str]:
    """读取 Python 文件导入模块集合。

    Args:
        source_path: Python 源码路径。

    Returns:
        import module 集合。

    Raises:
        SyntaxError: 当源码无法解析时抛出。
    """

    tree = ast.parse(source_path.read_text(encoding="utf-8"))
    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module)
    return imports
