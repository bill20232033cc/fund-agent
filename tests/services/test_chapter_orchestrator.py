"""Gate 3 Service 章节编排器测试，覆盖基金分析模板第 1-6 章。"""

from __future__ import annotations

import ast
from dataclasses import dataclass, replace
from pathlib import Path

import pytest

import fund_agent.services.chapter_orchestrator as chapter_orchestrator_module
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
    ChapterDraft,
    ChapterLLMRequest,
    ChapterLLMResponse,
    ChapterWriteIssue,
    ChapterWriteResult,
    ChapterWriteStopReason,
    build_chapter_prompt,
    build_chapter_writer_input,
)
from fund_agent.services.chapter_orchestrator import (
    ChapterAttemptRecord,
    ChapterLLMRuntimeDiagnostic,
    ChapterOrchestrationResult,
    ChapterOrchestrationPolicy,
    ChapterOrchestrator,
    ChapterOrchestratorLLMClients,
    ChapterRunResult,
    _audit_prompt_contract_diagnostic,
    _chapter_failure_category_from_audit_result,
    _decide_repair,
    _map_writer_stop_reason,
    _writer_prompt_contract_diagnostic,
    _required_corrections_from_issues,
    _stop_reason_from_repair_decision,
    build_chapter_orchestration_input,
    orchestrate_chapters,
    serialize_chapter_prompt_contract_diagnostics,
    serialize_chapter_runtime_diagnostics,
)
from fund_agent.fund.extractors.models import ExtractedField
from fund_agent.services.llm_provider import (
    LLMProviderMalformedResponseError,
    LLMProviderNetworkError,
    LLMProviderRateLimitError,
    LLMProviderTimeoutError,
)
from fund_agent.fund.template.typed_contracts import load_typed_template_contract_manifest
from tests.fund.test_chapter_facts import _bundle, _field


class _FakeChapterLLMClient:
    """测试用章节写作 fake client，只存在于 Service 测试。

    Attributes:
        texts: 按调用顺序返回的章节 Markdown。
        requests: 收到的 typed writer requests。
        raises: 是否抛出异常。
    """

    def __init__(
        self,
        texts: tuple[str, ...] = (),
        *,
        raises: bool = False,
        exception: Exception | None = None,
    ) -> None:
        """初始化 fake writer。

        Args:
            texts: 固定返回文本序列；为空时按请求动态生成合法章节。
            raises: 是否在调用时抛出异常。
            exception: 显式抛出的异常。

        Returns:
            无返回值。

        Raises:
            无显式抛出。
        """

        self.texts = list(texts)
        self.raises = raises
        self.exception = exception
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
        if self.texts:
            text = self.texts.pop(0)
        elif self.exception is not None:
            raise self.exception
        else:
            text = _valid_markdown_from_request(request)
        return ChapterLLMResponse(text=text, model_name="fake-writer", finish_reason="stop")


class _FakeAuditLLMClient:
    """测试用章节审计 fake client，只存在于 Service 测试。

    Attributes:
        raw_responses: 按调用顺序返回的 LLM audit 行协议。
        requests: 收到的 typed audit requests。
        raises: 是否抛出异常。
    """

    def __init__(
        self,
        raw_responses: tuple[str, ...] = (),
        *,
        raises: bool = False,
        exception: Exception | None = None,
    ) -> None:
        """初始化 fake auditor。

        Args:
            raw_responses: 固定返回行协议序列；为空时默认 PASS。
            raises: 是否在调用时抛出异常。
            exception: 显式抛出的异常。

        Returns:
            无返回值。

        Raises:
            无显式抛出。
        """

        self.raw_responses = list(raw_responses)
        self.raises = raises
        self.exception = exception
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
        if self.raw_responses:
            raw_text = self.raw_responses.pop(0)
        elif self.exception is not None:
            raise self.exception
        else:
            raw_text = "PASS|chapter|no issues"
        return ChapterAuditLLMResponse(raw_text=raw_text, model_name="fake-auditor", finish_reason="stop")


class _ChapterPlanWriterClient:
    """测试用章节写作 fake client，按章节执行预设动作。

    Attributes:
        actions: 章节编号到动作的映射。
        requests: 收到的 typed writer requests。
    """

    def __init__(self, actions: dict[int, object]) -> None:
        """初始化按章节分派的 fake writer。

        Args:
            actions: 章节编号到异常或 markdown 文本的映射；缺失章节返回合法章节。

        Returns:
            无返回值。

        Raises:
            无显式抛出。
        """

        self.actions = actions
        self.requests: list[ChapterLLMRequest] = []

    def generate_chapter(self, request: ChapterLLMRequest) -> ChapterLLMResponse:
        """按章节动作返回响应或抛出异常。

        Args:
            request: writer typed request。

        Returns:
            fake LLM 响应。

        Raises:
            Exception: 当章节动作配置为异常时抛出。
        """

        self.requests.append(request)
        action = self.actions.get(request.chapter_id)
        if isinstance(action, Exception):
            raise action
        if callable(action):
            text = action(request)
        elif isinstance(action, str):
            text = action
        else:
            text = _valid_markdown_from_request(request)
        return ChapterLLMResponse(text=text, model_name="fake-writer", finish_reason="stop")


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
        "missing_required_structure": "missing_required_structure",
        "missing_required_output_marker": "missing_required_output_marker",
        "unknown_anchor": "unknown_anchor",
        "response_too_long": "response_too_long",
        "response_incomplete": "response_incomplete",
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


@pytest.mark.parametrize(
    ("exception", "stop_reason"),
    (
        (LLMProviderTimeoutError("LLM provider request timed out"), "llm_timeout"),
        (LLMProviderRateLimitError("LLM provider rate limited: status_code=429"), "llm_rate_limited"),
        (LLMProviderMalformedResponseError("LLM provider returned invalid JSON"), "llm_malformed_response"),
        (LLMProviderNetworkError("LLM provider network error"), "llm_network_error"),
    ),
)
def test_provider_runtime_exceptions_map_to_precise_stop_reason(
    exception: Exception,
    stop_reason: str,
) -> None:
    """验证 provider runtime 异常映射为精确 fail-closed 分类。

    Args:
        exception: fake provider 异常。
        stop_reason: 预期 Service stop reason。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当异常被折叠到泛化分类时抛出。
    """

    result = _orchestrate_one(
        writer=_FakeChapterLLMClient(exception=exception),
        auditor=_FakeAuditLLMClient(),
    )

    run = result.chapter_results[0]
    assert run.status == "failed"
    assert run.stop_reason == stop_reason
    assert "Authorization" not in run.issues[0]
    assert "Bearer" not in run.issues[0]


def test_provider_timeout_diagnostic_is_enriched_and_does_not_regenerate() -> None:
    """验证 timeout 诊断补齐章节身份且不触发额外 regenerate。"""

    provider_diagnostics = (
        ChapterLLMRuntimeDiagnostic(
            operation="writer",
            chapter_id=None,
            fund_code=None,
            report_year=None,
            repair_attempt_index=None,
            provider_attempt_index=1,
            provider_max_attempts=2,
            provider_runtime_category="timeout",
            chapter_failure_category=None,
            elapsed_ms=10,
            status_code=None,
            request_id=None,
            model_name=None,
            finish_reason=None,
            response_chars=None,
            error_type="TimeoutException",
            message="LLM provider request timed out",
        ),
        ChapterLLMRuntimeDiagnostic(
            operation="writer",
            chapter_id=None,
            fund_code=None,
            report_year=None,
            repair_attempt_index=None,
            provider_attempt_index=2,
            provider_max_attempts=2,
            provider_runtime_category="timeout",
            chapter_failure_category=None,
            elapsed_ms=11,
            status_code=None,
            request_id=None,
            model_name=None,
            finish_reason=None,
            response_chars=None,
            error_type="TimeoutException",
            message="LLM provider request timed out",
        ),
    )
    exception = LLMProviderTimeoutError(
        "LLM provider request timed out",
        diagnostics=provider_diagnostics,
    )
    writer = _FakeChapterLLMClient(exception=exception)

    result = _orchestrate_one(
        writer=writer,
        auditor=_FakeAuditLLMClient(),
        policy=ChapterOrchestrationPolicy(target_chapter_ids=(1,), max_repair_attempts=3),
    )

    run = result.chapter_results[0]
    assert run.status == "failed"
    assert run.stop_reason == "llm_timeout"
    assert run.failure_category == "llm_timeout"
    assert len(writer.requests) == 1
    assert run.runtime_diagnostics
    assert len(run.runtime_diagnostics) == 2
    first = run.runtime_diagnostics[0]
    assert first.chapter_id == 1
    assert first.fund_code == "110011"
    assert first.report_year == 2024
    assert first.repair_attempt_index == 0
    assert first.provider_attempt_index == 1
    assert first.provider_max_attempts == 2
    assert first.provider_runtime_category == "timeout"
    assert first.chapter_failure_category == "llm_timeout"


def test_writer_prompt_contract_blocked_records_diagnostic_category() -> None:
    """验证 writer contract blocked 分类为 prompt_contract。"""

    result = _orchestrate_with_writer_stop_reason("missing_required_output_marker")

    run = result.chapter_results[0]
    diagnostic = run.attempts[0].runtime_diagnostics[0]
    assert run.stop_reason == "missing_required_output_marker"
    assert run.failure_category == "prompt_contract"
    assert run.failure_subcategory == "missing_required_marker"
    prompt_diagnostic = run.prompt_contract_diagnostics[0]
    assert prompt_diagnostic.primary_subcategory == "missing_required_marker"
    assert prompt_diagnostic.required_output_missing_count == 1
    assert prompt_diagnostic.accepted_draft_present is False
    assert diagnostic.chapter_failure_category == "prompt_contract"
    assert diagnostic.provider_runtime_category is None


@pytest.mark.parametrize(
    ("stop_reason", "subcategory", "counter_name"),
    (
        ("missing_required_structure", "missing_structure", "required_structure_missing_count"),
        ("missing_required_output_marker", "missing_required_marker", "required_output_missing_count"),
        ("unknown_anchor", "unknown_anchor", "unknown_anchor_count"),
        ("llm_contract_violation", "invalid_marker", "invalid_marker_count"),
        ("response_too_long", "response_length_incomplete", "response_length_incomplete_count"),
    ),
)
def test_writer_prompt_contract_subcategory_mapping(
    stop_reason: str,
    subcategory: str,
    counter_name: str,
) -> None:
    """验证 writer blocked 按 plan taxonomy 派生子类。"""

    result = _orchestrate_with_writer_stop_reason(stop_reason)

    run = result.chapter_results[0]
    prompt_diagnostic = run.prompt_contract_diagnostics[0]
    assert run.failure_category == "prompt_contract"
    assert run.failure_subcategory == subcategory
    assert prompt_diagnostic.primary_subcategory == subcategory
    assert getattr(prompt_diagnostic, counter_name) > 0


def test_writer_diagnostic_prefix_counts_strip_raw_suffixes() -> None:
    """验证 issue_id_prefix_counts 不保留 raw anchor/missing/phrase suffix。"""

    result = _orchestrate_with_writer_stop_reason("unknown_anchor")

    run = result.chapter_results[0]
    prompt_diagnostic = run.prompt_contract_diagnostics[0]
    assert prompt_diagnostic.issue_id_prefix_counts == {"writer:unknown_anchor": 1}
    assert "unknown-anchor" not in str(prompt_diagnostic.issue_id_prefix_counts)


def test_writer_forbidden_phrase_subcategory_remains_blocked() -> None:
    """验证 writer 禁用措辞只诊断为 forbidden_phrase，不放行。"""

    projection = project_chapter_facts(_bundle(), chapter_ids=(1,))
    markdown = _valid_markdown_from_projection(projection) + "\n建议买入。"

    result = _orchestrate_one(
        writer=_FakeChapterLLMClient((markdown,)),
        auditor=_FakeAuditLLMClient(),
    )

    run = result.chapter_results[0]
    diagnostic = run.prompt_contract_diagnostics[0]
    assert run.status == "blocked"
    assert run.failure_subcategory == "forbidden_phrase"
    assert diagnostic.forbidden_phrase_count == 1
    assert diagnostic.issue_id_prefix_counts == {"writer:forbidden_phrase": 1}
    assert "建议买入" not in str(diagnostic.issue_id_prefix_counts)


@pytest.mark.parametrize(
    ("marker", "expected_prefix"),
    (
        ("<!-- missing:unknown_reason -->", "writer:unknown_missing_reason"),
        ("<!-- missing :field_missing -->", "writer:invalid_missing_marker"),
    ),
)
def test_writer_missing_marker_issues_count_as_invalid_marker_without_raw_suffix(
    marker: str,
    expected_prefix: str,
) -> None:
    """验证 missing marker 问题归 invalid_marker 且不存 raw suffix。"""

    projection = project_chapter_facts(_bundle(), chapter_ids=(1,))
    markdown = _valid_markdown_from_projection(projection) + f"\n{marker}"

    result = _orchestrate_one(
        writer=_FakeChapterLLMClient((markdown,)),
        auditor=_FakeAuditLLMClient(),
    )

    run = result.chapter_results[0]
    assert run.status == "blocked"
    assert run.failure_category == "prompt_contract"
    assert run.failure_subcategory == "invalid_marker"
    diagnostic = run.prompt_contract_diagnostics[0]
    assert diagnostic.primary_subcategory == "invalid_marker"
    assert diagnostic.invalid_marker_count == 1
    assert diagnostic.issue_id_prefix_counts == {expected_prefix: 1}
    assert "unknown_reason" not in str(diagnostic.issue_id_prefix_counts)
    assert "field_missing" not in str(diagnostic.issue_id_prefix_counts)


def test_accepted_chapter_has_no_prompt_contract_subcategory() -> None:
    """验证 accepted 章节不携带 prompt-contract 子类。"""

    result = _orchestrate_one(writer=_FakeChapterLLMClient(), auditor=_FakeAuditLLMClient())

    run = result.chapter_results[0]
    assert run.status == "accepted"
    assert run.failure_category is None
    assert run.failure_subcategory is None
    assert run.prompt_contract_diagnostics == ()


def test_programmatic_candidate_facet_assertion_is_counted_not_accepted() -> None:
    """验证候选 facet 断言只计数，仍阻断。"""

    projection = project_chapter_facts(_bundle(), chapter_ids=(1,))
    facet = projection.chapters[0].facet_resolution.non_asserted_facets[0]
    markdown = _valid_markdown_from_projection(projection) + f"\n本基金属于{facet}。"

    result = _orchestrate_one(
        writer=_FakeChapterLLMClient((markdown, markdown)),
        auditor=_FakeAuditLLMClient(),
        policy=ChapterOrchestrationPolicy(target_chapter_ids=(1,), max_repair_attempts=1),
    )

    run = result.chapter_results[0]
    diagnostic = run.prompt_contract_diagnostics[0]
    assert run.status == "failed"
    assert run.failure_category == "prompt_contract"
    assert run.failure_subcategory == "candidate_facet_assertion"
    assert diagnostic.primary_subcategory == "candidate_facet_assertion"
    assert diagnostic.candidate_facet_assertion_count > 0
    assert facet not in str(diagnostic.issue_id_prefix_counts)


def test_programmatic_forbidden_phrase_is_counted_not_accepted() -> None:
    """验证 programmatic audit 禁用措辞只计数，仍阻断。"""

    audit_result = ChapterAuditResult(
        status="fail",
        programmatic=ChapterProgrammaticAuditResult(
            status="fail",
            checked_rules=("C1",),
            issues=(
                _audit_issue(
                    "programmatic:C1:phrase:abcdef",
                    "C1",
                    "章节包含禁用措辞：仓位比例",
                    "phrase",
                ),
            ),
        ),
        llm=ChapterLLMAuditResult(status="pass", issues=(), raw_response=None, model_name=None, finish_reason=None),
        accepted=False,
        repair_hint="regenerate",
    )

    diagnostic = _audit_prompt_contract_diagnostic(audit_result, chapter_id=1, attempt_index=0)

    assert diagnostic is not None
    assert diagnostic.primary_subcategory == "forbidden_phrase"
    assert diagnostic.forbidden_phrase_count == 1
    assert diagnostic.issue_id_prefix_counts == {"programmatic:C1": 1}


def test_programmatic_l1_numerical_closure_is_counted_not_code_bug_other() -> None:
    """验证 programmatic:L1 映射到专用子类且仍阻断，见模板第 2章 R=A+B-C。"""

    audit_result = ChapterAuditResult(
        status="fail",
        programmatic=ChapterProgrammaticAuditResult(
            status="fail",
            checked_rules=("L1",),
            issues=(
                _audit_issue(
                    "programmatic:L1:line:2:abcdef",
                    "L1",
                    "R=A+B-C / A=R-B / A-C 数字闭环断言缺少邻近 anchor marker。",
                    "line:2",
                ),
            ),
        ),
        llm=ChapterLLMAuditResult(status="pass", issues=(), raw_response=None, model_name=None, finish_reason=None),
        accepted=False,
        repair_hint="patch",
    )

    diagnostic = _audit_prompt_contract_diagnostic(audit_result, chapter_id=2, attempt_index=0)

    assert diagnostic is not None
    assert diagnostic.primary_subcategory == "l1_numerical_closure"
    assert diagnostic.l1_numerical_closure_count == 1
    assert diagnostic.issue_id_prefix_counts == {"programmatic:L1": 1}
    assert "line:2" not in str(diagnostic.issue_id_prefix_counts)


def test_provider_timeout_has_no_prompt_contract_subcategory() -> None:
    """验证 provider timeout 不产生 prompt-contract subcategory。"""

    result = _orchestrate_one(
        writer=_FakeChapterLLMClient(exception=LLMProviderTimeoutError("timeout")),
        auditor=_FakeAuditLLMClient(),
    )

    run = result.chapter_results[0]
    assert run.failure_category == "llm_timeout"
    assert run.failure_subcategory is None
    assert run.prompt_contract_diagnostics == ()


def test_unmapped_writer_contract_issue_is_code_bug_other() -> None:
    """验证无可分类计数的 writer contract issue 归 code_bug_other。"""

    projection = project_chapter_facts(_bundle(), chapter_ids=(1,))
    writer_input = build_chapter_writer_input(projection, chapter_id=1)
    prompt = build_chapter_prompt(writer_input)
    writer_result = ChapterWriteResult(
        status="blocked",
        stop_reason="llm_contract_violation",
        prompt=prompt,
        draft=None,
        issues=(
            ChapterWriteIssue(
                issue_id="writer:llm_contract_violation",
                severity="blocking",
                reason="llm_contract_violation",
                message="generic contract violation",
            ),
        ),
    )

    diagnostic = _writer_prompt_contract_diagnostic(writer_result, chapter_id=1, attempt_index=0)

    assert diagnostic is not None
    assert diagnostic.primary_subcategory == "code_bug_other"


def test_candidate_facet_precedence_beats_forbidden_phrase_only_by_plan_order() -> None:
    """验证 audit 子类按 plan precedence 选择主类。"""

    audit_result = ChapterAuditResult(
        status="fail",
        programmatic=ChapterProgrammaticAuditResult(
            status="fail",
            checked_rules=("C1", "C2"),
            issues=(
                _audit_issue("facet", "C2", "候选 facet 被写成已断言事实：foo", "facet"),
                _audit_issue("forbidden", "C1", "章节包含禁用措辞：建议买入", "phrase"),
            ),
        ),
        llm=ChapterLLMAuditResult(status="pass", issues=(), raw_response=None, model_name=None, finish_reason=None),
        accepted=False,
        repair_hint="regenerate",
    )

    diagnostic = _audit_prompt_contract_diagnostic(audit_result, chapter_id=1, attempt_index=0)

    assert diagnostic is not None
    assert diagnostic.primary_subcategory == "candidate_facet_assertion"
    assert diagnostic.candidate_facet_assertion_count == 1
    assert diagnostic.forbidden_phrase_count == 1


def test_candidate_facet_and_forbidden_phrase_precedence_beats_l1() -> None:
    """验证 L1 子类位于 forbidden_phrase 之后且不掩盖 candidate facet。"""

    audit_result = ChapterAuditResult(
        status="fail",
        programmatic=ChapterProgrammaticAuditResult(
            status="fail",
            checked_rules=("C1", "C2", "L1"),
            issues=(
                _audit_issue("facet", "C2", "候选 facet 被写成已断言事实：foo", "facet"),
                _audit_issue("forbidden", "C1", "章节包含禁用措辞：建议买入", "phrase"),
                _audit_issue(
                    "programmatic:L1:line:4:abcdef",
                    "L1",
                    "R=A+B-C / A=R-B / A-C 数字闭环断言缺少邻近 anchor marker。",
                    "line:4",
                ),
            ),
        ),
        llm=ChapterLLMAuditResult(status="pass", issues=(), raw_response=None, model_name=None, finish_reason=None),
        accepted=False,
        repair_hint="regenerate",
    )

    diagnostic = _audit_prompt_contract_diagnostic(audit_result, chapter_id=2, attempt_index=0)

    assert diagnostic is not None
    assert diagnostic.primary_subcategory == "candidate_facet_assertion"
    assert diagnostic.candidate_facet_assertion_count == 1
    assert diagnostic.forbidden_phrase_count == 1
    assert diagnostic.l1_numerical_closure_count == 1


def test_sanitized_prompt_contract_serialization_excludes_raw_payloads() -> None:
    """验证脱敏诊断序列化不包含 prompt、draft 或 raw response。"""

    result = _orchestrate_with_writer_stop_reason("unknown_anchor")

    payload = serialize_chapter_prompt_contract_diagnostics(result)
    text = str(payload)

    assert payload["first_failed"]["subcategory"] == "unknown_anchor"  # type: ignore[index]
    assert "chapter_phase_matrix" in payload
    for forbidden in (
        "system_prompt",
        "user_prompt",
        "draft_markdown",
        "raw_response",
        "provider_response",
        "accepted_draft.markdown",
        "### 结论要点",
        "Authorization",
        "Bearer",
        "sk-",
    ):
        assert forbidden not in text


def test_runtime_diagnostic_serialization_exposes_only_safe_scalars() -> None:
    """验证 runtime 诊断序列化只输出白名单标量，见模板第 1-6 章。"""

    provider_diagnostics = (
        ChapterLLMRuntimeDiagnostic(
            operation="writer",
            chapter_id=None,
            fund_code=None,
            report_year=None,
            repair_attempt_index=None,
            provider_attempt_index=1,
            provider_max_attempts=2,
            provider_runtime_category="timeout",
            chapter_failure_category=None,
            elapsed_ms=123,
            status_code=None,
            request_id="req-safe-1",
            model_name="secret-deployment-model",
            finish_reason=None,
            response_chars=None,
            error_type="TimeoutException",
            system_prompt_chars=100,
            user_prompt_chars=300,
            approx_prompt_tokens=100,
            allowed_fact_count=None,
            allowed_anchor_count=2,
            max_output_chars=12000,
            timeout_seconds=120,
            timeout_max_attempts=2,
            timeout_backoff_seconds=1,
            timeout_budget_kind="writer_initial",
            message=(
                "writer issue USER_PROMPT_CANARY DRAFT_MARKDOWN_CANARY "
                "RAW_RESPONSE_CANARY raw audit provider body Authorization Bearer sk-secret"
            ),
        ),
        ChapterLLMRuntimeDiagnostic(
            operation="writer",
            chapter_id=None,
            fund_code=None,
            report_year=None,
            repair_attempt_index=None,
            provider_attempt_index=2,
            provider_max_attempts=2,
            provider_runtime_category="timeout",
            chapter_failure_category=None,
            elapsed_ms=456,
            status_code=None,
            request_id="req-safe-2",
            model_name="secret-deployment-model",
            finish_reason=None,
            response_chars=None,
            error_type="TimeoutException",
            system_prompt_chars=100,
            user_prompt_chars=300,
            approx_prompt_tokens=100,
            allowed_fact_count=None,
            allowed_anchor_count=2,
            max_output_chars=12000,
            timeout_seconds=120,
            timeout_max_attempts=2,
            timeout_backoff_seconds=1,
            timeout_budget_kind="writer_initial",
            message=(
                "auditor programmatic RAW_AUDIT_RESPONSE_CANARY "
                "SYSTEM_PROMPT_CANARY PROVIDER_RESPONSE_CANARY header key"
            ),
        ),
    )
    result = _orchestrate_one(
        writer=_FakeChapterLLMClient(
            exception=LLMProviderTimeoutError(
                "timeout with provider body",
                diagnostics=provider_diagnostics,
            )
        ),
        auditor=_FakeAuditLLMClient(),
        policy=ChapterOrchestrationPolicy(target_chapter_ids=(1, 2)),
    )

    payload = serialize_chapter_runtime_diagnostics(result)
    text = str(payload)
    first_failed = payload["first_failed"]  # type: ignore[index]
    first_row = payload["chapter_runtime_matrix"][0]  # type: ignore[index]
    diagnostics = first_row["runtime_diagnostics"]  # type: ignore[index]

    assert payload["schema_version"] == "chapter_runtime_diagnostic_payload.v1"
    assert first_failed["runtime_operation"] == "writer"  # type: ignore[index]
    assert first_failed["repair_attempt_index"] == 0  # type: ignore[index]
    assert first_failed["provider_attempt_count"] == 2  # type: ignore[index]
    assert first_failed["provider_max_attempts"] == 2  # type: ignore[index]
    assert first_failed["provider_runtime_categories"] == ("timeout",)  # type: ignore[index]
    assert first_failed["timeout_seconds"] == 120  # type: ignore[index]
    assert first_failed["timeout_max_attempts"] == 2  # type: ignore[index]
    assert first_failed["timeout_backoff_seconds"] == 1  # type: ignore[index]
    assert first_failed["timeout_budget_kind"] == "writer_initial"  # type: ignore[index]
    assert first_failed["timeout_root_cause_hint"] == "small_prompt_provider_timeout"  # type: ignore[index]
    assert first_failed["system_prompt_chars"] == 100  # type: ignore[index]
    assert first_failed["user_prompt_chars"] == 300  # type: ignore[index]
    assert first_failed["approx_prompt_tokens"] == 100  # type: ignore[index]
    assert first_failed["allowed_fact_count"] is None  # type: ignore[index]
    assert first_failed["allowed_anchor_count"] == 2  # type: ignore[index]
    assert first_failed["max_output_chars"] == 12000  # type: ignore[index]
    assert diagnostics[0]["operation"] == "writer"  # type: ignore[index]
    assert diagnostics[0]["provider_attempt_index"] == 1  # type: ignore[index]
    assert diagnostics[0]["elapsed_ms"] == 123  # type: ignore[index]
    assert diagnostics[0]["system_prompt_chars"] == 100  # type: ignore[index]
    assert diagnostics[0]["user_prompt_chars"] == 300  # type: ignore[index]
    assert diagnostics[0]["approx_prompt_tokens"] == 100  # type: ignore[index]
    assert diagnostics[0]["allowed_anchor_count"] == 2  # type: ignore[index]
    assert diagnostics[0]["max_output_chars"] == 12000  # type: ignore[index]
    assert diagnostics[0]["timeout_seconds"] == 120  # type: ignore[index]
    assert diagnostics[0]["timeout_root_cause_hint"] == "small_prompt_provider_timeout"  # type: ignore[index]
    assert diagnostics[0]["prompt_cost_diagnostic"] is None  # type: ignore[index]
    assert diagnostics[1]["provider_attempt_index"] == 2  # type: ignore[index]
    assert diagnostics[1]["elapsed_ms"] == 456  # type: ignore[index]
    for forbidden in (
        "model_name",
        "secret-deployment-model",
        "message",
        "writer issue",
        "auditor",
        "programmatic",
        "raw audit",
        "RAW_AUDIT_RESPONSE_CANARY",
        "SYSTEM_PROMPT_CANARY",
        "USER_PROMPT_CANARY",
        "DRAFT_MARKDOWN_CANARY",
        "RAW_RESPONSE_CANARY",
        "PROVIDER_RESPONSE_CANARY",
        "provider body",
        "Authorization",
        "Bearer",
        "sk-secret",
        "header",
        "key",
    ):
        assert forbidden not in text


def test_repair_timeout_terminal_diagnostic_is_not_shadowed_by_prior_audit_row() -> None:
    """验证 repair 后 terminal timeout 不会被先前 auditor 诊断遮蔽。"""

    projection = project_chapter_facts(_bundle(), chapter_ids=(2,))
    markdown = _valid_markdown_from_projection(projection) + "\nA=R-B，因此 Alpha 为 2.10%。"
    timeout_diagnostic = ChapterLLMRuntimeDiagnostic(
        operation="auditor",
        chapter_id=None,
        fund_code=None,
        report_year=None,
        repair_attempt_index=None,
        provider_attempt_index=1,
        provider_max_attempts=2,
        provider_runtime_category="timeout",
        chapter_failure_category=None,
        elapsed_ms=120000,
        status_code=2000,
        request_id="req-opaque-safe",
        model_name="secret-model",
        finish_reason=None,
        response_chars=None,
        error_type="ReadTimeout",
        system_prompt_chars=10,
        user_prompt_chars=3000,
        approx_prompt_tokens=752,
        allowed_fact_count=3,
        allowed_anchor_count=2,
        max_output_chars=12000,
        timeout_seconds=60,
        timeout_max_attempts=2,
        timeout_backoff_seconds=1,
        timeout_budget_kind="auditor",
    )

    result = _orchestrate(
        writer=_FakeChapterLLMClient(
            texts=(markdown, _valid_markdown_from_projection(projection)),
        ),
        auditor=_FakeAuditLLMClient(
            ("BLOCKING|R=A+B-C 数字闭环|A=R-B 缺少邻近 anchor marker。",),
            exception=LLMProviderTimeoutError(
                "timeout on repair auditor provider body Authorization Bearer sk-secret",
                diagnostics=(timeout_diagnostic,),
            ),
        ),
        policy=ChapterOrchestrationPolicy(target_chapter_ids=(2,), max_repair_attempts=1),
    )

    run = result.chapter_results[0]
    payload = serialize_chapter_runtime_diagnostics(result)
    first_failed = payload["first_failed"]  # type: ignore[index]
    row = payload["chapter_runtime_matrix"][0]  # type: ignore[index]
    diagnostics = row["runtime_diagnostics"]  # type: ignore[index]

    assert run.stop_reason == "llm_timeout"
    assert run.failure_category == "llm_timeout"
    assert len(run.attempts) == 2
    assert run.attempts[0].runtime_diagnostics[0].chapter_failure_category == "prompt_contract"
    assert run.attempts[1].runtime_diagnostics[0].provider_runtime_category == "timeout"
    assert first_failed["diagnostic_consistency_status"] == "consistent"  # type: ignore[index]
    assert first_failed["terminal_runtime_diagnostic_present"] is True  # type: ignore[index]
    assert first_failed["terminal_runtime_operation"] == "auditor"  # type: ignore[index]
    assert first_failed["terminal_repair_attempt_index"] == 1  # type: ignore[index]
    assert first_failed["terminal_issue_class"] == "ReadTimeout"  # type: ignore[index]
    assert first_failed["runtime_operation"] == "auditor"  # type: ignore[index]
    assert first_failed["repair_attempt_index"] == 1  # type: ignore[index]
    assert first_failed["provider_attempt_count"] == 1  # type: ignore[index]
    assert first_failed["timeout_budget_kind"] == "auditor"  # type: ignore[index]
    assert first_failed["timeout_seconds"] == 60  # type: ignore[index]
    assert first_failed["approx_prompt_tokens"] == 752  # type: ignore[index]
    assert row["diagnostic_consistency_status"] == "consistent"  # type: ignore[index]
    assert diagnostics[0]["chapter_failure_category"] == "prompt_contract"  # type: ignore[index]
    assert diagnostics[1]["chapter_failure_category"] == "llm_timeout"  # type: ignore[index]
    assert diagnostics[1]["status_code"] is None  # type: ignore[index]
    assert "secret-model" not in str(payload)
    assert "provider body" not in str(payload)


def test_writer_repair_timeout_terminal_diagnostic_uses_chapter_level_row() -> None:
    """验证 writer repair timeout 没有 attempt record 时仍保留章节级 terminal row。"""

    projection = project_chapter_facts(_bundle(), chapter_ids=(2,))
    markdown = _valid_markdown_from_projection(projection) + "\nA=R-B，因此 Alpha 为 2.10%。"
    timeout_diagnostic = ChapterLLMRuntimeDiagnostic(
        operation="writer",
        chapter_id=None,
        fund_code=None,
        report_year=None,
        repair_attempt_index=None,
        provider_attempt_index=1,
        provider_max_attempts=2,
        provider_runtime_category="timeout",
        chapter_failure_category=None,
        elapsed_ms=120000,
        status_code=None,
        request_id="req-opaque-safe",
        model_name=None,
        finish_reason=None,
        response_chars=None,
        error_type="ReadTimeout",
        system_prompt_chars=10,
        user_prompt_chars=3000,
        approx_prompt_tokens=752,
        allowed_fact_count=3,
        allowed_anchor_count=2,
        max_output_chars=12000,
        timeout_seconds=60,
        timeout_max_attempts=2,
        timeout_backoff_seconds=1,
        timeout_budget_kind="writer_repair",
    )

    result = _orchestrate(
        writer=_FakeChapterLLMClient(
            texts=(markdown,),
            exception=LLMProviderTimeoutError(
                "timeout on repair provider body Authorization Bearer sk-secret",
                diagnostics=(timeout_diagnostic,),
            ),
        ),
        auditor=_FakeAuditLLMClient(),
        policy=ChapterOrchestrationPolicy(target_chapter_ids=(2,), max_repair_attempts=1),
    )

    run = result.chapter_results[0]
    payload = serialize_chapter_runtime_diagnostics(result)
    first_failed = payload["first_failed"]  # type: ignore[index]
    row = payload["chapter_runtime_matrix"][0]  # type: ignore[index]
    diagnostics = row["runtime_diagnostics"]  # type: ignore[index]

    assert run.stop_reason == "llm_timeout"
    assert run.failure_category == "llm_timeout"
    assert run.runtime_diagnostics[0].provider_runtime_category == "timeout"
    assert first_failed["diagnostic_consistency_status"] == "consistent"  # type: ignore[index]
    assert first_failed["terminal_runtime_diagnostic_present"] is True  # type: ignore[index]
    assert first_failed["terminal_runtime_operation"] == "writer"  # type: ignore[index]
    assert first_failed["terminal_repair_attempt_index"] == 1  # type: ignore[index]
    assert first_failed["terminal_issue_class"] == "ReadTimeout"  # type: ignore[index]
    assert first_failed["runtime_operation"] == "writer"  # type: ignore[index]
    assert first_failed["repair_attempt_index"] == 1  # type: ignore[index]
    assert first_failed["provider_attempt_count"] == 1  # type: ignore[index]
    assert first_failed["timeout_budget_kind"] == "writer_repair"  # type: ignore[index]
    assert first_failed["timeout_seconds"] == 60  # type: ignore[index]
    assert first_failed["approx_prompt_tokens"] == 752  # type: ignore[index]
    assert row["diagnostic_consistency_status"] == "consistent"  # type: ignore[index]
    assert diagnostics[0]["chapter_failure_category"] == "llm_timeout"  # type: ignore[index]
    assert diagnostics[0]["status_code"] is None  # type: ignore[index]
    assert diagnostics[1]["chapter_failure_category"] == "prompt_contract"  # type: ignore[index]
    assert "secret-model" not in str(payload)
    assert "provider body" not in str(payload)


def test_timeout_terminal_without_matching_runtime_row_marks_missing() -> None:
    """验证 llm_timeout 没有 timeout row 时只标缺失，不伪造 timeout 标量。"""

    projection = project_chapter_facts(_bundle(), chapter_ids=(2,))
    writer_input = build_chapter_writer_input(projection, chapter_id=2)
    draft = _valid_markdown_from_projection(projection) + "\nA=R-B，因此 Alpha 为 2.10%。"
    audit_result = _audit_result_for_l1()
    run = ChapterRunResult(
        chapter_id=2,
        title="第 2 章",
        status="failed",
        stop_reason="llm_timeout",
        accepted_draft=None,
        accepted_conclusion=None,
        attempts=(
            ChapterAttemptRecord(
                attempt_index=0,
                writer_result=ChapterWriteResult(
                    status="drafted",
                    stop_reason="none",
                    draft=ChapterDraft(
                        chapter_id=2,
                        title="第 2 章",
                        markdown=draft,
                        used_fact_ids=(),
                        used_anchor_ids=(),
                        declared_missing_reasons=(),
                        deleted_item_rule_ids=(),
                        model_name="fake-writer",
                        finish_reason="stop",
                    ),
                    issues=(),
                    prompt=build_chapter_prompt(writer_input),
                    response_chars=len(draft),
                    max_output_chars=12000,
                    finish_reason="stop",
                ),
                audit_result=audit_result,
                repair_decision=None,
                runtime_diagnostics=(
                    ChapterLLMRuntimeDiagnostic(
                        operation="auditor",
                        chapter_id=2,
                        fund_code="110011",
                        report_year=2024,
                        repair_attempt_index=0,
                        provider_attempt_index=None,
                        provider_max_attempts=None,
                        provider_runtime_category=None,
                        chapter_failure_category="prompt_contract",
                        elapsed_ms=None,
                        status_code=None,
                        request_id=None,
                        model_name=None,
                        finish_reason="stop",
                        response_chars=22,
                        error_type=None,
                    ),
                ),
            ),
        ),
        issues=("LLM client exception category=llm_timeout: LLMProviderTimeoutError",),
        failure_category="llm_timeout",
    )
    result = _orchestration_from_runs((run,))

    payload = serialize_chapter_runtime_diagnostics(result)
    first_failed = payload["first_failed"]  # type: ignore[index]
    row = payload["chapter_runtime_matrix"][0]  # type: ignore[index]

    assert first_failed["diagnostic_consistency_status"] == "missing_terminal_runtime_diagnostic"  # type: ignore[index]
    assert first_failed["terminal_runtime_diagnostic_present"] is False  # type: ignore[index]
    assert first_failed["terminal_issue_class"] == "LLMProviderTimeoutError"  # type: ignore[index]
    assert first_failed["runtime_operation"] is None  # type: ignore[index]
    assert first_failed["provider_attempt_count"] == 0  # type: ignore[index]
    assert first_failed["provider_runtime_categories"] == ()  # type: ignore[index]
    assert first_failed["timeout_seconds"] is None  # type: ignore[index]
    assert first_failed["timeout_budget_kind"] is None  # type: ignore[index]
    assert row["diagnostic_consistency_status"] == "missing_terminal_runtime_diagnostic"  # type: ignore[index]
    assert row["runtime_diagnostics"][0]["chapter_failure_category"] == "prompt_contract"  # type: ignore[index]
    assert row["runtime_diagnostics"][0]["finish_reason"] == "stop"  # type: ignore[index]


def test_runtime_diagnostic_serialization_includes_attempt_level_diagnostics() -> None:
    """验证 serializer 覆盖 attempt.runtime_diagnostics。"""

    result = _orchestrate_with_writer_stop_reason("missing_required_output_marker")

    payload = serialize_chapter_runtime_diagnostics(result)
    first_failed = payload["first_failed"]  # type: ignore[index]
    first_row = payload["chapter_runtime_matrix"][0]  # type: ignore[index]
    diagnostics = first_row["runtime_diagnostics"]  # type: ignore[index]

    assert first_failed["runtime_operation"] == "writer"  # type: ignore[index]
    assert first_failed["repair_attempt_index"] == 0  # type: ignore[index]
    assert first_failed["provider_attempt_count"] == 0  # type: ignore[index]
    assert first_failed["provider_max_attempts"] is None  # type: ignore[index]
    assert first_failed["provider_runtime_categories"] == ()  # type: ignore[index]
    assert diagnostics[0]["operation"] == "writer"  # type: ignore[index]
    assert diagnostics[0]["chapter_failure_category"] == "prompt_contract"  # type: ignore[index]
    assert "message" not in str(payload)


def test_runtime_root_cause_hint_never_marks_auditor_as_large_prompt_cost() -> None:
    """验证 auditor timeout 不会产出 large_writer_prompt_cost。"""

    diagnostic = ChapterLLMRuntimeDiagnostic(
        operation="auditor",
        chapter_id=3,
        fund_code="000001",
        report_year=2024,
        repair_attempt_index=0,
        provider_attempt_index=1,
        provider_max_attempts=1,
        provider_runtime_category="timeout",
        chapter_failure_category="llm_timeout",
        elapsed_ms=120000,
        status_code=None,
        request_id=None,
        model_name=None,
        finish_reason=None,
        response_chars=None,
        error_type="ReadTimeout",
        system_prompt_chars=10,
        user_prompt_chars=40000,
        approx_prompt_tokens=10003,
        allowed_fact_count=3,
        allowed_anchor_count=3,
        max_output_chars=None,
        timeout_seconds=120,
        timeout_max_attempts=1,
        timeout_backoff_seconds=0,
        timeout_budget_kind="auditor",
    )
    result = _orchestrate_one(
        writer=_FakeChapterLLMClient(exception=LLMProviderTimeoutError("timeout", diagnostics=(diagnostic,))),
        auditor=_FakeAuditLLMClient(),
        policy=ChapterOrchestrationPolicy(target_chapter_ids=(3,)),
    )

    payload = serialize_chapter_runtime_diagnostics(result)
    first_failed = payload["first_failed"]  # type: ignore[index]
    row = payload["chapter_runtime_matrix"][0]  # type: ignore[index]
    diagnostics = row["runtime_diagnostics"]  # type: ignore[index]

    assert first_failed["timeout_root_cause_hint"] == "provider_runtime_timeout_uncalibrated"  # type: ignore[index]
    assert diagnostics[0]["timeout_root_cause_hint"] == "provider_runtime_timeout_uncalibrated"  # type: ignore[index]
    assert "large_writer_prompt_cost" not in str(payload)


def test_l1_prompt_contract_serialization_exposes_safe_subcategory_only() -> None:
    """验证 L1 诊断序列化只暴露安全 prefix 和计数，见模板第 2章 R=A+B-C。"""

    projection = project_chapter_facts(_bundle(), chapter_ids=(2,))
    markdown = _valid_markdown_from_projection(projection) + "\nA=R-B，因此 Alpha 为 2.10%。"

    result = _orchestrate(
        writer=_FakeChapterLLMClient((markdown, markdown)),
        auditor=_FakeAuditLLMClient(),
        policy=ChapterOrchestrationPolicy(target_chapter_ids=(2,), max_repair_attempts=1),
    )
    payload = serialize_chapter_prompt_contract_diagnostics(result)
    text = str(payload)

    assert payload["first_failed"]["category"] == "prompt_contract"  # type: ignore[index]
    assert payload["first_failed"]["subcategory"] == "l1_numerical_closure"  # type: ignore[index]
    phases = payload["chapter_phase_matrix"][0]["phases"]  # type: ignore[index]
    assert phases[0]["primary_subcategory"] == "l1_numerical_closure"  # type: ignore[index]
    assert phases[0]["l1_numerical_closure_count"] == 1  # type: ignore[index]
    assert "programmatic:L1" in text
    assert "line:" not in text
    assert "Alpha 为 2.10%" not in text
    assert "A=R-B" not in text
    assert "draft_markdown" not in text
    assert "user_prompt" not in text


def test_audit_parse_failure_records_audit_parse_diagnostic() -> None:
    """验证 LLM audit 行协议解析失败分类为 audit_parse。"""

    result = _orchestrate_one(
        writer=_FakeChapterLLMClient(),
        auditor=_FakeAuditLLMClient(("这不是合法行协议", "这也不是合法行协议")),
    )

    run = result.chapter_results[0]
    assert run.status == "blocked"
    assert run.failure_category == "audit_parse"
    assert len(run.attempts) == 2
    diagnostic = run.attempts[-1].runtime_diagnostics[0]
    assert diagnostic.chapter_failure_category == "audit_parse"
    assert diagnostic.repair_attempt_index == 1


def test_parseable_llm_audit_failure_after_programmatic_pass_is_audit_rule_too_strict() -> None:
    """验证 programmatic pass 后的可解析 LLM fail 分类为 audit_rule_too_strict。"""

    result = _orchestrate_one(
        writer=_FakeChapterLLMClient(),
        auditor=_FakeAuditLLMClient(("BLOCKING|证据与出处|证据表达过宽，请缩小到已有 anchor。",)),
        policy=ChapterOrchestrationPolicy(target_chapter_ids=(1,), max_repair_attempts=0),
    )

    run = result.chapter_results[0]
    assert run.status == "failed"
    assert run.stop_reason == "repair_budget_exhausted"
    assert run.failure_category == "audit_rule_too_strict"
    diagnostic = run.attempts[0].runtime_diagnostics[0]
    assert diagnostic.chapter_failure_category == "audit_rule_too_strict"


def test_l1_repair_context_guides_anchored_correction_and_accepts_after_repair() -> None:
    """验证 L1 专用修复项经 typed repair context 传递并支持二轮修复通过。"""

    projection = project_chapter_facts(_bundle(), chapter_ids=(2,))
    base_markdown = _valid_markdown_from_projection(projection)
    anchor_id = projection.chapters[0].evidence_anchors[0].anchor_id
    first_markdown = f"{base_markdown}\nA=R-B，因此 Alpha 为 2.10%。"
    repaired_markdown = f"{base_markdown}\n<!-- anchor:{anchor_id} -->\nA=R-B，因此 Alpha 为 2.10%。"
    writer = _FakeChapterLLMClient((first_markdown, repaired_markdown))

    result = _orchestrate(
        writer=writer,
        auditor=_FakeAuditLLMClient(),
        policy=ChapterOrchestrationPolicy(target_chapter_ids=(2,), max_repair_attempts=1),
    )

    run = result.chapter_results[0]
    assert run.status == "accepted"
    assert len(writer.requests) == 2
    repair_context = writer.requests[1].repair_context
    assert repair_context is not None
    assert any(issue_id.startswith("programmatic:L1") for issue_id in repair_context.previous_issue_ids)
    assert any("第2章 R=A+B-C 数字闭环" in item for item in repair_context.required_corrections)
    assert any("### 结论要点 与 ### 证据与出处" in item for item in repair_context.required_corrections)
    assert any("不得在这些段落无锚点复述 R/A/B/C/A-C 具体百分比" in item for item in repair_context.required_corrections)
    assert "第2章 L1 repair 必须改写规则" in writer.requests[1].user_prompt
    assert "先删除上一轮无邻近 anchor 的具体数字闭环断言" in writer.requests[1].user_prompt
    assert "只有确认 allowed `<!-- anchor:<anchor_id> -->` 支撑该具体数值时" in writer.requests[1].user_prompt
    assert "同一句或上下2行" in writer.requests[1].user_prompt
    assert "不确定时写数据不足或下一步最小验证问题，且不写具体百分比" in writer.requests[1].user_prompt
    assert "输出前逐行自查 R/A/B/C/A-C/Alpha/Beta/Cost/%" in writer.requests[1].user_prompt
    assert "extra_payload" not in writer.requests[1].user_prompt


def test_chapter_6_invalid_anchor_marker_retries_and_accepts() -> None:
    """验证 Service 编排第 6 章 invalid anchor marker 可预算内重写通过。"""

    def _first_invalid_then_valid(request: ChapterLLMRequest) -> str:
        if request.repair_context is None:
            return _invalid_anchor_markdown_from_request(request)
        return _valid_markdown_from_request(request)

    writer = _ChapterPlanWriterClient({6: _first_invalid_then_valid})

    result = _orchestrate(
        policy=ChapterOrchestrationPolicy(target_chapter_ids=(6,), max_repair_attempts=1),
        writer=writer,
        auditor=_FakeAuditLLMClient(),
    )

    run = result.chapter_results[0]
    assert result.status == "accepted"
    assert run.status == "accepted"
    assert [request.chapter_id for request in writer.requests] == [6, 6]
    assert writer.requests[0].repair_context is None
    assert writer.requests[1].repair_context is not None
    assert writer.requests[1].repair_context.attempt_index == 1
    assert len(run.attempts) == 2


def test_chapter_6_invalid_anchor_marker_budget_zero_does_not_retry() -> None:
    """回归守卫：Service 编排第 6 章预算为 0 时 invalid marker 不重试。"""

    writer = _ChapterPlanWriterClient({6: _invalid_anchor_markdown_from_request})

    result = _orchestrate(
        policy=ChapterOrchestrationPolicy(target_chapter_ids=(6,), max_repair_attempts=0),
        writer=writer,
        auditor=_FakeAuditLLMClient(),
    )

    run = result.chapter_results[0]
    assert result.status == "blocked"
    assert run.status == "blocked"
    assert run.stop_reason == "llm_contract_violation"
    assert len(writer.requests) == 1
    assert writer.requests[0].repair_context is None
    assert len(run.attempts) == 1


def test_l1_failure_after_repair_budget_exhausted_keeps_l1_subcategory() -> None:
    """验证 repair 后仍无锚点数字闭环时 fail-closed 且保留 L1 子类。"""

    projection = project_chapter_facts(_bundle(), chapter_ids=(2,))
    markdown = _valid_markdown_from_projection(projection) + "\nA=R-B，因此 Alpha 为 2.10%。"

    result = _orchestrate(
        writer=_FakeChapterLLMClient((markdown, markdown)),
        auditor=_FakeAuditLLMClient(),
        policy=ChapterOrchestrationPolicy(target_chapter_ids=(2,), max_repair_attempts=1),
    )

    run = result.chapter_results[0]
    assert run.status == "failed"
    assert run.stop_reason == "repair_budget_exhausted"
    assert run.failure_category == "prompt_contract"
    assert run.failure_subcategory == "l1_numerical_closure"
    assert run.prompt_contract_diagnostics[0].primary_subcategory == "l1_numerical_closure"


def test_needs_more_facts_records_fact_gap_diagnostic() -> None:
    """验证 needs_more_facts 审计结果分类为 fact_gap。"""

    projection = project_chapter_facts(_bundle(), chapter_ids=(5,))
    markdown = _valid_markdown_from_projection(projection)

    result = _orchestrate_one(
        writer=_FakeChapterLLMClient((f"{markdown}\n风格稳定。",)),
        auditor=_FakeAuditLLMClient(),
        policy=ChapterOrchestrationPolicy(target_chapter_ids=(5,)),
    )

    run = result.chapter_results[0]
    assert run.status == "blocked"
    assert run.stop_reason == "needs_more_facts"
    assert run.failure_category == "fact_gap"
    diagnostic = run.attempts[0].runtime_diagnostics[0]
    assert diagnostic.chapter_failure_category == "fact_gap"


def test_unexpected_exception_records_code_bug_diagnostic_without_secret() -> None:
    """验证未知异常分类为 code_bug 且诊断脱敏。"""

    exception = RuntimeError("Authorization Bearer sk-secret prompt full text")

    result = _orchestrate_one(
        writer=_FakeChapterLLMClient(exception=exception),
        auditor=_FakeAuditLLMClient(),
    )

    run = result.chapter_results[0]
    assert run.status == "failed"
    assert run.stop_reason == "llm_exception"
    assert run.failure_category == "code_bug"
    diagnostic = run.runtime_diagnostics[0]
    assert diagnostic.chapter_failure_category == "code_bug"
    assert diagnostic.error_type == "RuntimeError"
    assert "Authorization" not in (diagnostic.message or "")
    assert "Bearer" not in (diagnostic.message or "")
    assert "sk-" not in (diagnostic.message or "")


def test_chapter_3_pre_provider_value_error_serializes_safe_runtime_cap() -> None:
    """验证第 3 章 pre-provider code_bug 序列化保留安全输出上限。"""

    exception = ValueError("Authorization Bearer sk-secret prompt raw")

    result = _orchestrate_one(
        writer=_FakeChapterLLMClient(exception=exception),
        auditor=_FakeAuditLLMClient(),
        policy=ChapterOrchestrationPolicy(
            target_chapter_ids=(3,),
            max_output_chars=12000,
            typed_template_path="typed_template_contract",
        ),
    )

    payload = serialize_chapter_runtime_diagnostics(result)
    first_failed = payload["first_failed"]  # type: ignore[index]
    row = payload["chapter_runtime_matrix"][0]  # type: ignore[index]
    diagnostics = row["runtime_diagnostics"]  # type: ignore[index]

    assert first_failed["chapter_id"] == 3  # type: ignore[index]
    assert first_failed["stop_reason"] == "llm_exception"  # type: ignore[index]
    assert first_failed["category"] == "code_bug"  # type: ignore[index]
    assert first_failed["provider_attempt_count"] == 0  # type: ignore[index]
    assert first_failed["provider_runtime_categories"] == ()  # type: ignore[index]
    assert first_failed["max_output_chars"] == 12000  # type: ignore[index]
    assert first_failed["terminal_runtime_diagnostic_present"] is True  # type: ignore[index]
    assert first_failed["diagnostic_consistency_status"] == "consistent"  # type: ignore[index]
    assert diagnostics[0]["error_type"] == "ValueError"  # type: ignore[index]
    assert diagnostics[0]["max_output_chars"] == 12000  # type: ignore[index]
    assert diagnostics[0]["provider_runtime_category"] is None  # type: ignore[index]
    diagnostic_message = diagnostics[0].get("message")  # type: ignore[union-attr]
    assert "Authorization" not in (diagnostic_message or "")
    assert "Bearer" not in (diagnostic_message or "")
    assert "sk-secret" not in (diagnostic_message or "")
    assert "prompt raw" not in (diagnostic_message or "")
    text = str(payload)
    assert "Authorization" not in text
    assert "Bearer" not in text
    assert "sk-secret" not in text
    assert "prompt raw" not in text


def test_chapter_3_writer_input_value_error_serializes_safe_runtime_cap_before_writer_tool(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """验证第 3 章 writer input 构造异常投影为安全运行时诊断。"""

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
        "fund_agent.agent.runner._typed_required_output_items",
        _raise_typed_required_output_items,
    )
    writer = _FakeChapterLLMClient()

    result = _orchestrate(
        writer=writer,
        auditor=_FakeAuditLLMClient(),
        policy=ChapterOrchestrationPolicy(
            target_chapter_ids=(3,),
            max_output_chars=12000,
            typed_template_path="typed_template_contract",
        ),
    )

    run = result.chapter_results[0]
    payload = serialize_chapter_runtime_diagnostics(result)
    first_failed = payload["first_failed"]  # type: ignore[index]
    row = payload["chapter_runtime_matrix"][0]  # type: ignore[index]
    diagnostics = row["runtime_diagnostics"]  # type: ignore[index]

    assert writer.requests == []
    assert result.status == "blocked"
    assert run.chapter_id == 3
    assert run.status == "failed"
    assert run.stop_reason == "llm_exception"
    assert run.failure_category == "code_bug"
    assert first_failed["chapter_id"] == 3  # type: ignore[index]
    assert first_failed["stop_reason"] == "llm_exception"  # type: ignore[index]
    assert first_failed["category"] == "code_bug"  # type: ignore[index]
    assert first_failed["provider_attempt_count"] == 0  # type: ignore[index]
    assert first_failed["provider_runtime_categories"] == ()  # type: ignore[index]
    assert first_failed["max_output_chars"] == 12000  # type: ignore[index]
    assert first_failed["terminal_runtime_diagnostic_present"] is True  # type: ignore[index]
    assert first_failed["diagnostic_consistency_status"] == "consistent"  # type: ignore[index]
    assert diagnostics[0]["error_type"] == "ValueError"  # type: ignore[index]
    assert diagnostics[0]["max_output_chars"] == 12000  # type: ignore[index]
    assert diagnostics[0]["provider_runtime_category"] is None  # type: ignore[index]
    text = str(payload)
    assert "Authorization" not in text
    assert "Bearer" not in text
    assert "sk-secret" not in text
    assert "prompt raw" not in text


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

    writer = _FakeChapterLLMClient()

    result = _orchestrate_one(
        writer=writer,
        auditor=_FakeAuditLLMClient(("REVIEWABLE|证据与出处|证据支撑不足，请补充 allowed anchor。",)),
    )

    run = result.chapter_results[0]
    assert run.status == "accepted"
    assert len(run.attempts) == 2
    assert run.attempts[0].repair_decision is not None
    assert run.attempts[0].repair_decision.action == "regenerate"
    assert writer.requests[0].repair_context is None
    assert writer.requests[1].repair_context is not None
    assert writer.requests[1].repair_context.attempt_index == 1


def test_regenerate_request_contains_previous_failure_context() -> None:
    """验证 regenerate writer request 携带上一轮失败上下文。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当第二轮 request 缺少 repair context 时抛出。
    """

    writer = _FakeChapterLLMClient()

    result = _orchestrate_one(
        writer=writer,
        auditor=_FakeAuditLLMClient(("REVIEWABLE|required output|缺少 required output marker，请补齐。",)),
    )

    assert result.chapter_results[0].status == "accepted"
    repair_context = writer.requests[1].repair_context
    assert repair_context is not None
    assert repair_context.previous_issue_ids
    assert any("required output" in message for message in repair_context.previous_messages)
    assert any("required output" in correction for correction in repair_context.required_corrections)


def test_required_corrections_are_deterministic_for_known_issue_patterns() -> None:
    """验证 known audit issue 生成确定性 correction。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当映射不稳定时抛出。
    """

    issues = (
        _audit_issue("p1", "P1", "缺少结构段落：结论要点", "结论要点"),
        _audit_issue("c2-output", "C2", "缺少 required output item marker：费用", "费用"),
        _audit_issue("c2-facet", "C2", "候选 facet 被写成已断言事实：主动权益", "主动权益"),
        _audit_issue(
            "programmatic:L1:line:5:abcdef",
            "L1",
            "R=A+B-C / A=R-B / A-C 数字闭环断言缺少邻近 anchor marker。",
            "line:5",
        ),
        _audit_issue("e1", "E1", "草稿引用未授权锚点：unknown", "used_anchor_ids"),
        _audit_issue("llm:parse_failure", "C1", "parse failure", "raw_response"),
        replace(
            _audit_issue(
                "programmatic:C2:chapter_2_alpha_yearly_breakdown:abcdef",
                "C2",
                "ITEM_RULE 要求删除的段落仍出现在草稿中：超额收益分年度拆解",
                "chapter_2_alpha_yearly_breakdown",
            ),
            item_rule_ids=("chapter_2_alpha_yearly_breakdown",),
        ),
    )

    corrections = _required_corrections_from_issues(issues)

    assert "补齐 ### 结论要点 / ### 详细情况 / ### 证据与出处 固定结构段落。" in corrections
    assert any("required output item" in correction for correction in corrections)
    assert any("候选 facet" in correction for correction in corrections)
    assert any("第2章 R=A+B-C 数字闭环" in correction for correction in corrections)
    assert any("### 结论要点 与 ### 证据与出处" in correction for correction in corrections)
    assert any("不得编造 Alpha、Beta、Cost 或 R 数值" in correction for correction in corrections)
    assert any("allowed anchor marker" in correction for correction in corrections)
    assert any("PASS|chapter|no issues" in correction for correction in corrections)
    assert any("BLOCKING、REVIEWABLE 或 INFO" in correction for correction in corrections)
    assert any("禁止 SEVERITY 占位词" in correction for correction in corrections)
    assert any("解释性前缀、Markdown、JSON" in correction for correction in corrections)
    assert any("删除 ITEM_RULE 要求删除的 optional/conditional 段落标题和专属段落" in correction for correction in corrections)
    assert any("不得删除 required output marker" in correction for correction in corrections)


def test_required_corrections_sanitize_unknown_issue_message() -> None:
    """验证未知 issue fallback 会脱敏并限长。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当敏感文本进入 correction 时抛出。
    """

    issue = _audit_issue(
        "unknown",
        "C1",
        "raw\nAuthorization: Bearer sk-secret prompt full provider response " + "x" * 400,
        "chapter",
    )

    corrections = _required_corrections_from_issues((issue,))

    correction = corrections[0]
    assert "\n" not in correction
    assert "Authorization" not in correction
    assert "Bearer" not in correction
    assert "sk-" not in correction
    assert "prompt" not in correction
    assert len(correction) <= 183


def test_repair_budget_exhausted_returns_failed_stop_reason() -> None:
    """验证 repair budget 耗尽时返回 repair_budget_exhausted。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当预算耗尽未 fail-closed 时抛出。
    """

    writer = _FakeChapterLLMClient()

    result = _orchestrate_one(
        writer=writer,
        auditor=_FakeAuditLLMClient(
            (
                "REVIEWABLE|证据与出处|证据支撑不足，请补充 allowed anchor。",
                "REVIEWABLE|证据与出处|证据支撑不足，请补充 allowed anchor。",
            )
        ),
    )

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

    writer = _FakeChapterLLMClient()

    result = _orchestrate_one(
        writer=writer,
        auditor=_FakeAuditLLMClient(("REVIEWABLE|证据与出处|证据支撑不足，请补充 allowed anchor。",)),
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


def test_llm_unavailable_audit_is_not_audit_rule_too_strict() -> None:
    """验证 LLM_UNAVAILABLE 不会被归类为 auditor 规则过严。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当不可用问题误归类为 audit_rule_too_strict 时抛出。
    """

    audit_result = _audit_result_with_hint("regenerate", llm_unavailable=True)
    assert audit_result.programmatic.status == "pass"
    assert audit_result.llm.status == "blocked"
    assert _chapter_failure_category_from_audit_result(audit_result) == "prompt_contract"


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


def test_fail_fast_true_is_legacy_noop_and_later_chapter_executes() -> None:
    """验证 fail_fast=True 不再让前章失败跳过后续正文章节。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当后续章节被 dependency_missing 跳过时抛出。
    """

    writer = _ChapterPlanWriterClient({1: LLMProviderTimeoutError("timeout")})
    result = _orchestrate(
        policy=ChapterOrchestrationPolicy(target_chapter_ids=(1, 2), fail_fast=True),
        writer=writer,
        auditor=_FakeAuditLLMClient(),
    )

    assert result.status == "partial"
    assert [request.chapter_id for request in writer.requests] == [1, 2]
    assert result.chapter_results[0].status == "failed"
    assert result.chapter_results[0].stop_reason == "llm_timeout"
    assert result.chapter_results[1].status == "accepted"
    assert result.chapter_results[1].stop_reason == "none"
    assert result.generated_chapter_ids == (1, 2)
    assert result.skipped_chapter_ids == ()


def test_chapter_1_timeout_does_not_skip_chapters_2_to_6() -> None:
    """验证第 1 章 timeout 后第 2-6 章仍独立进入 writer。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当后续章节未执行或被 dependency_missing 代替时抛出。
    """

    writer = _ChapterPlanWriterClient({1: LLMProviderTimeoutError("timeout")})

    result = _orchestrate(
        policy=ChapterOrchestrationPolicy(target_chapter_ids=(1, 2, 3, 4, 5, 6)),
        writer=writer,
        auditor=_FakeAuditLLMClient(),
    )

    assert result.status == "partial"
    assert _unique_request_chapter_ids(writer.requests) == [1, 2, 3, 4, 5, 6]
    assert result.chapter_results[0].status == "failed"
    assert result.chapter_results[0].stop_reason == "llm_timeout"
    assert all(run.status != "skipped" for run in result.chapter_results[1:])
    assert all(run.stop_reason != "dependency_missing" for run in result.chapter_results[1:])
    assert result.generated_chapter_ids == (1, 2, 3, 4, 5, 6)
    assert result.skipped_chapter_ids == ()


def test_mixed_body_chapter_matrix_preserves_each_chapter_outcome() -> None:
    """验证混合 accepted/blocked/failed 矩阵不会被首个失败覆盖。"""

    projection = project_chapter_facts(_bundle(), chapter_ids=(1, 2, 3, 4, 5, 6))
    chapter3_markdown = _valid_markdown_for_chapter(projection, 3).replace(
        "<!-- required_output:",
        "<!-- removed_required_output:",
        1,
    )
    chapter5_markdown = f"{_valid_markdown_for_chapter(projection, 5)}\n风格稳定。"
    writer = _ChapterPlanWriterClient(
        {
            1: LLMProviderTimeoutError("timeout"),
            3: chapter3_markdown,
            5: chapter5_markdown,
        }
    )
    input_data = build_chapter_orchestration_input(
        fund_code="110011",
        report_year=2024,
        chapter_projection=projection,
        policy=ChapterOrchestrationPolicy(target_chapter_ids=(1, 2, 3, 4, 5, 6), max_repair_attempts=0),
    )

    result = orchestrate_chapters(
        input_data,
        llm_clients=ChapterOrchestratorLLMClients(
            writer=writer,
            auditor=_FakeAuditLLMClient(("PASS|chapter|no issues", "这不是合法行协议", "PASS|chapter|no issues")),
        ),
    )

    rows = {run.chapter_id: run for run in result.chapter_results}
    assert result.status == "partial"
    assert [request.chapter_id for request in writer.requests] == [1, 2, 3, 4, 5, 6]
    assert rows[1].status == "failed"
    assert rows[1].stop_reason == "llm_timeout"
    assert rows[1].failure_category == "llm_timeout"
    assert rows[2].status == "accepted"
    assert rows[2].stop_reason == "none"
    assert rows[3].status == "blocked"
    assert rows[3].failure_category == "prompt_contract"
    assert rows[3].failure_subcategory == "missing_required_marker"
    assert rows[4].status == "blocked"
    assert rows[4].failure_category == "audit_parse"
    assert rows[5].status == "blocked"
    assert rows[5].stop_reason == "needs_more_facts"
    assert rows[5].failure_category == "fact_gap"
    assert rows[6].status == "accepted"
    assert result.skipped_chapter_ids == ()


def test_all_blocked_body_chapters_all_execute_and_status_blocked() -> None:
    """验证所有正文章节阻断时也执行全部请求章节，总状态为 blocked。"""

    writer = _ChapterPlanWriterClient({chapter_id: LLMProviderTimeoutError("timeout") for chapter_id in range(1, 7)})

    result = _orchestrate(
        policy=ChapterOrchestrationPolicy(target_chapter_ids=(1, 2, 3, 4, 5, 6)),
        writer=writer,
        auditor=_FakeAuditLLMClient(),
    )

    assert result.status == "blocked"
    assert [request.chapter_id for request in writer.requests] == [1, 2, 3, 4, 5, 6]
    assert all(run.status == "failed" for run in result.chapter_results)
    assert all(run.stop_reason == "llm_timeout" for run in result.chapter_results)
    assert result.generated_chapter_ids == (1, 2, 3, 4, 5, 6)
    assert result.skipped_chapter_ids == ()


def test_dependency_missing_only_for_true_writer_dependency_not_prior_failure() -> None:
    """验证 dependency_missing 只来自 writer 明确依赖停止原因。"""

    status, stop_reason = _map_writer_stop_reason("chapter_requires_accepted_conclusions")
    writer = _ChapterPlanWriterClient({1: LLMProviderTimeoutError("timeout")})

    result = _orchestrate(
        policy=ChapterOrchestrationPolicy(target_chapter_ids=(1, 2), fail_fast=True),
        writer=writer,
        auditor=_FakeAuditLLMClient(),
    )

    assert status == "blocked"
    assert stop_reason == "dependency_missing"
    assert [run.stop_reason for run in result.chapter_results] == ["llm_timeout", "none"]
    assert all(run.stop_reason != "dependency_missing" for run in result.chapter_results)
    assert result.chapter_results[1].status == "accepted"
    assert result.skipped_chapter_ids == ()
    assert result.generated_chapter_ids == (1, 2)


def test_typed_contract_path_preserves_independent_body_execution(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """验证 typed contract path 接入后仍独立执行正文章节。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 typed path 未传入 availability/audit_focus 或前章失败跳过后章时抛出。
    """

    availability_calls: list[tuple[str, int]] = []
    typed_manifest = load_typed_template_contract_manifest()
    typed_by_id = {chapter.chapter_id: chapter for chapter in typed_manifest.chapters}
    original_derive_availability = chapter_orchestrator_module.derive_evidence_availability

    def _record_derive_availability(projection):  # type: ignore[no-untyped-def]
        """记录 Service façade 是否显式派生 EvidenceAvailability。"""

        availability_calls.append((projection.fund_code, projection.report_year))
        availability = original_derive_availability(projection)
        assert availability.require("ch2.required_output.item_01").chapter_id == 2
        assert availability.require("ch3.required_output.item_03").status == "unreviewed"
        return availability

    monkeypatch.setattr(
        chapter_orchestrator_module,
        "derive_evidence_availability",
        _record_derive_availability,
    )
    writer = _ChapterPlanWriterClient({1: LLMProviderTimeoutError("timeout")})
    auditor = _FakeAuditLLMClient()
    result = _orchestrate(
        policy=ChapterOrchestrationPolicy(
            target_chapter_ids=(1, 2, 3),
            max_repair_attempts=0,
            prompt_payload_mode="compact",
            typed_template_path="typed_template_contract",
        ),
        writer=writer,
        auditor=auditor,
    )

    rows = {run.chapter_id: run for run in result.chapter_results}
    assert result.status == "partial"
    assert [request.chapter_id for request in writer.requests] == [1, 2, 3]
    assert rows[1].status == "failed"
    assert rows[1].stop_reason == "llm_timeout"
    assert rows[2].status == "accepted"
    assert rows[3].status == "accepted"
    assert rows[2].attempts[0].writer_result.prompt.required_output_evidence_plan
    assert rows[3].attempts[0].writer_result.prompt.required_output_evidence_plan
    assert rows[2].attempts[0].writer_result.prompt.required_output_items == tuple(
        item.item_id for item in typed_by_id[2].required_output_items
    )
    assert rows[3].attempts[0].writer_result.prompt.required_output_items == tuple(
        item.item_id for item in typed_by_id[3].required_output_items
    )
    ch3_plan_by_id = {
        plan.item_id: plan
        for plan in rows[3].attempts[0].writer_result.prompt.required_output_evidence_plan
    }
    assert ch3_plan_by_id["ch3.required_output.item_03"].text == (
        typed_by_id[3].required_output_items[2].text
    )
    assert ch3_plan_by_id["ch3.required_output.item_03"].action == "render_evidence_gap"
    assert ch3_plan_by_id["ch3.required_output.item_03"].availability_status == "unreviewed"
    assert availability_calls == [("110011", 2024)]
    assert auditor.requests[0].chapter_id == 2
    assert auditor.requests[0].audit_focus == typed_by_id[2].audit_focus
    assert auditor.requests[1].chapter_id == 3
    assert auditor.requests[1].audit_focus == typed_by_id[3].audit_focus
    assert result.skipped_chapter_ids == ()
    assert all(run.stop_reason != "dependency_missing" for run in result.chapter_results[1:])


def test_typed_contract_path_repair_keeps_typed_required_output_items() -> None:
    """验证 typed path repair 轮次也把 required output items 传给 writer。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 repair writer input 丢失 typed required output 行为时抛出。
    """

    writer = _FakeChapterLLMClient()
    auditor = _FakeAuditLLMClient(
        (
            "BLOCKING|chapter|fixture semantic repair",
            "PASS|chapter|no issues",
        )
    )

    result = _orchestrate(
        policy=ChapterOrchestrationPolicy(
            target_chapter_ids=(2,),
            max_repair_attempts=1,
            prompt_payload_mode="compact",
            typed_template_path="typed_template_contract",
        ),
        writer=writer,
        auditor=auditor,
    )

    run = result.chapter_results[0]
    assert result.status == "accepted"
    assert run.status == "accepted"
    assert run.stop_reason == "none"
    assert [request.chapter_id for request in writer.requests] == [2, 2]
    assert len(run.attempts) == 2
    assert all(
        attempt.writer_result.prompt.required_output_evidence_plan
        for attempt in run.attempts
    )
    assert all(
        attempt.writer_result.prompt.required_output_items[0].startswith(
            "ch2.required_output."
        )
        for attempt in run.attempts
    )


def test_chapter_2_typed_missing_evidence_gap_path_accepts_without_repair() -> None:
    """验证第 2 章 typed 非 available 证据可渲染缺口并保持一次 writer 调用。"""

    projection = project_chapter_facts(
        replace(
            _bundle(),
            nav_benchmark_performance=ExtractedField(
                value=None,
                anchors=(),
                extraction_mode="missing",
                note="fixture missing",
            ),
            fee_schedule=ExtractedField(
                value=None,
                anchors=(),
                extraction_mode="missing",
                note="fixture missing",
            ),
        ),
        chapter_ids=(2,),
    )
    policy = ChapterOrchestrationPolicy(
        target_chapter_ids=(2,),
        max_repair_attempts=1,
        typed_template_path="typed_template_contract",
    )
    input_data = build_chapter_orchestration_input(
        fund_code="110011",
        report_year=2024,
        chapter_projection=projection,
        policy=policy,
    )
    writer = _ChapterPlanWriterClient({2: _chapter_2_gap_markdown_from_request})

    result = orchestrate_chapters(
        input_data,
        llm_clients=ChapterOrchestratorLLMClients(writer=writer, auditor=_FakeAuditLLMClient()),
    )

    run = result.chapter_results[0]
    plan_by_id = {
        plan.item_id: plan
        for plan in run.attempts[0].writer_result.prompt.required_output_evidence_plan
    }
    assert result.status == "accepted"
    assert run.status == "accepted"
    assert run.stop_reason == "none"
    assert len(writer.requests) == 1
    assert policy.max_repair_attempts == 1
    assert plan_by_id["ch2.required_output.item_01"].action == "render_evidence_gap"
    assert plan_by_id["ch2.required_output.item_01"].availability_status == "missing"
    assert plan_by_id["ch2.required_output.item_07"].action == "render_minimum_verification_question"
    assert plan_by_id["ch2.required_output.item_07"].availability_status == "missing"


def test_chapter_2_typed_available_facts_still_fail_l1_after_one_repair() -> None:
    """验证第 2 章 available facts 被忽略时仍按 L1 fail-closed 且只 repair 一次。"""

    writer = _ChapterPlanWriterClient({2: _chapter_2_unanchored_closure_from_request})

    result = _orchestrate(
        writer=writer,
        auditor=_FakeAuditLLMClient(),
        policy=ChapterOrchestrationPolicy(
            target_chapter_ids=(2,),
            max_repair_attempts=1,
            typed_template_path="typed_template_contract",
        ),
    )

    run = result.chapter_results[0]
    assert run.status == "failed"
    assert run.stop_reason == "repair_budget_exhausted"
    assert run.failure_category == "prompt_contract"
    assert run.failure_subcategory == "l1_numerical_closure"
    assert len(writer.requests) == 2
    assert len(run.attempts) == 2
    assert all(
        plan.action == "render"
        for plan in run.attempts[0].writer_result.prompt.required_output_evidence_plan
    )


def test_typed_contract_path_ch1_accepts_typed_required_output_markers() -> None:
    """验证 typed 第 1 章不会因使用 stable required-output marker 被程序审计误阻断。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 Ch1 typed marker 被 legacy marker 规则误阻断时抛出。
    """

    result = _orchestrate(
        policy=ChapterOrchestrationPolicy(
            target_chapter_ids=(1,),
            prompt_payload_mode="compact",
            typed_template_path="typed_template_contract",
        ),
        writer=_FakeChapterLLMClient(),
        auditor=_FakeAuditLLMClient(),
    )

    run = result.chapter_results[0]
    assert result.status == "accepted"
    assert run.status == "accepted"
    assert run.attempts[0].writer_result.prompt.required_output_items[0].startswith(
        "ch1.required_output."
    )
    assert not any(
        "required output item marker" in issue.message
        for issue in run.attempts[0].audit_result.programmatic.issues
    )


def test_first_failed_diagnostic_keeps_full_chapter_matrix() -> None:
    """验证 first_failed 不隐藏完整章节矩阵。"""

    writer = _ChapterPlanWriterClient({1: LLMProviderTimeoutError("timeout")})
    result = _orchestrate(
        policy=ChapterOrchestrationPolicy(target_chapter_ids=(1, 2)),
        writer=writer,
        auditor=_FakeAuditLLMClient(),
    )

    runtime_payload = serialize_chapter_runtime_diagnostics(result)
    prompt_payload = serialize_chapter_prompt_contract_diagnostics(result)

    assert runtime_payload["first_failed"]["chapter_id"] == 1  # type: ignore[index]
    assert len(runtime_payload["chapter_runtime_matrix"]) == 2  # type: ignore[arg-type]
    assert runtime_payload["chapter_runtime_matrix"][1]["status"] == "accepted"  # type: ignore[index]
    assert len(prompt_payload["chapter_phase_matrix"]) == 2  # type: ignore[arg-type]
    assert prompt_payload["chapter_phase_matrix"][1]["status"] == "accepted"  # type: ignore[index]


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
    """验证 parser 要求固定 H3 结论段落，H2 不再作为 accepted 结构。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 H2 结论抽取越界时抛出。
    """

    markdown = _valid_markdown_with_conclusion("H2 结论", heading="## 结论要点", next_heading="## 详细情况")

    result = _orchestrate_one(writer=_FakeChapterLLMClient((markdown,)), auditor=_FakeAuditLLMClient())

    run = result.chapter_results[0]
    assert run.status == "blocked"
    assert run.stop_reason == "missing_required_structure"


def test_fixed_heading_conclusion_takes_precedence_over_preamble_lines() -> None:
    """验证固定结论 heading 优先于前置散行，见模板第 1-6 章。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当结论抽取没有遵守固定结构时抛出。
    """

    policy = ChapterOrchestrationPolicy(
        target_chapter_ids=(1,),
        run_programmatic_audit=False,
        run_llm_audit=True,
    )
    markdown = (
        "第一行\n\n第二行\n第三行\n第四行\n"
        "### 结论要点\n"
        f"{_required_lines(project_chapter_facts(_bundle(), chapter_ids=(1,)).chapters[0].contract.required_output_items)}\n"
        "### 详细情况\n"
        "### 证据与出处\n"
    )

    result = _orchestrate_one(
        writer=_FakeChapterLLMClient((markdown,)),
        auditor=_FakeAuditLLMClient(),
        policy=policy,
    )

    conclusion = result.accepted_conclusions[0]
    assert conclusion.conclusion_source == "heading"
    assert "<!-- required_output:" in conclusion.conclusion_markdown
    assert "第一行" not in conclusion.conclusion_markdown


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


def _orchestration_from_runs(
    chapter_results: tuple[ChapterRunResult, ...],
) -> ChapterOrchestrationResult:
    """从手工章节结果构造编排结果。

    Args:
        chapter_results: 手工构造的章节结果。

    Returns:
        测试用章节编排结果。

    Raises:
        无显式抛出。
    """

    projection = project_chapter_facts(
        _bundle(),
        chapter_ids=tuple(result.chapter_id for result in chapter_results),
    )
    return ChapterOrchestrationResult(
        status="blocked",
        fund_code="110011",
        report_year=2024,
        projection=projection,
        chapter_results=chapter_results,
        accepted_conclusions=(),
        blocked_reasons=tuple(issue for result in chapter_results for issue in result.issues),
        generated_chapter_ids=tuple(result.chapter_id for result in chapter_results),
        skipped_chapter_ids=(),
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
    if stop_reason == "response_incomplete":
        return _MappedStopResult(status="blocked", stop_reason="response_incomplete")
    text_by_reason = {
        "missing_required_facts": None,
        "evidence_anchor_missing": None,
        "item_rule_deleted_required_content": None,
        "chapter_requires_accepted_conclusions": None,
        "prompt_only": None,
        "llm_empty_response": "",
        "llm_contract_violation": "### 结论要点\n<!-- ANCHOR:bad -->\n### 详细情况\n### 证据与出处\n",
        "missing_required_structure": _valid_markdown_from_projection(
            project_chapter_facts(_bundle(), chapter_ids=(1,))
        ).replace("### 详细情况\n", ""),
        "missing_required_output_marker": _valid_markdown_from_projection(
            project_chapter_facts(_bundle(), chapter_ids=(1,))
        ).replace("<!-- required_output:", "<!-- removed_required_output:", 1),
        "unknown_anchor": _valid_markdown_from_parts(
            "unknown-anchor",
            project_chapter_facts(_bundle(), chapter_ids=(1,)).chapters[0].contract.required_output_items,
        ).replace("> 📎 证据：年报2024§§2表None行basic_identity（fixture）\n", ""),
        "response_too_long": _valid_markdown_from_projection(project_chapter_facts(_bundle(), chapter_ids=(1,))),
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
        policy=(
            ChapterOrchestrationPolicy(target_chapter_ids=(1,), max_output_chars=10)
            if stop_reason == "response_too_long"
            else None
        ),
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


def _audit_result_for_l1() -> ChapterAuditResult:
    """构造第 2 章 L1 programmatic audit failure。

    Args:
        无。

    Returns:
        L1 审计失败结果。

    Raises:
        无显式抛出。
    """

    issue = ChapterAuditIssue(
        issue_id="programmatic:L1:line:2:abcdef",
        layer="programmatic",
        rule_code="L1",
        severity="blocking",
        message="R=A+B-C 数字闭环缺少邻近 anchor marker。",
        location="line:2",
        repair_hint="patch",
    )
    return ChapterAuditResult(
        status="fail",
        programmatic=ChapterProgrammaticAuditResult(
            status="fail",
            issues=(issue,),
            checked_rules=("L1",),
        ),
        llm=ChapterLLMAuditResult(
            status="pass",
            issues=(),
            raw_response=None,
            model_name=None,
            finish_reason="stop",
        ),
        accepted=False,
        repair_hint="patch",
    )


def _audit_issue(
    issue_id: str,
    rule_code: str,
    message: str,
    location: str,
) -> ChapterAuditIssue:
    """构造 repair correction 测试用 audit issue。

    Args:
        issue_id: issue id。
        rule_code: 审计规则码。
        message: issue message。
        location: issue location。

    Returns:
        测试用 audit issue。

    Raises:
        无显式抛出。
    """

    return ChapterAuditIssue(
        issue_id=issue_id,
        layer="programmatic",
        rule_code=rule_code,
        severity="blocking",
        message=message,
        location=location,
        repair_hint="patch",
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


def _invalid_anchor_markdown_from_request(request: ChapterLLMRequest) -> str:
    """按 writer request 构造非法 anchor marker 章节 Markdown。"""

    return _valid_markdown_from_request(request).replace("<!-- anchor:", "<!-- ANCHOR:", 1)


def _chapter_2_gap_markdown_from_request(request: ChapterLLMRequest) -> str:
    """构造第 2 章非 available required output 的安全缺口/最小验证 Markdown。"""

    anchor_id = request.required_anchor_ids[0]
    required_lines = "\n".join(
        f"<!-- required_output:{item} -->\n"
        "- 证据不足，不能完成具体 R=A+B-C 数字闭环。"
        "下一步最小验证问题：复核同源年报中的基金收益、基准收益和费用口径。"
        for item in _required_items_from_request(request)
    )
    return (
        "### 结论要点\n"
        f"{required_lines}\n"
        "### 详细情况\n"
        "本章只记录当前同源已复核证据不足的项目，不输出具体百分比闭环。\n"
        "### 证据与出处\n"
        f"<!-- anchor:{anchor_id} -->\n"
        "> 📎 证据：年报2024§§2表None行fixture（fixture）\n"
    )


def _chapter_2_unanchored_closure_from_request(request: ChapterLLMRequest) -> str:
    """构造第 2 章 typed marker 完整但含无锚点数字闭环的 Markdown。"""

    return _valid_markdown_from_request(request) + "\nA=R-B，因此 Alpha 为 2.10%。"


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


def _valid_markdown_for_chapter(projection: object, chapter_id: int) -> str:
    """按 projection 中指定章节构造合法章节 Markdown。

    Args:
        projection: Gate 1 projection。
        chapter_id: 模板章节编号。

    Returns:
        测试用章节 Markdown。

    Raises:
        AssertionError: 当 projection 不含目标章节时抛出。
    """

    for chapter in projection.chapters:
        if chapter.chapter_id == chapter_id:
            anchor_id = chapter.evidence_anchors[0].anchor_id
            return _valid_markdown_from_parts(anchor_id, chapter.contract.required_output_items)
    raise AssertionError(f"missing chapter fixture: {chapter_id}")


def _unique_request_chapter_ids(requests: list[ChapterLLMRequest]) -> list[int]:
    """按首次出现顺序返回 writer request 章节编号。

    Args:
        requests: writer fake 收到的请求。

    Returns:
        去重后的章节编号列表。

    Raises:
        无显式抛出。
    """

    chapter_ids: list[int] = []
    seen: set[int] = set()
    for request in requests:
        if request.chapter_id in seen:
            continue
        chapter_ids.append(request.chapter_id)
        seen.add(request.chapter_id)
    return chapter_ids


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
            return tuple(_required_item_from_prompt_payload(item) for item in parsed)
    return ()


def _required_item_from_prompt_payload(item: str) -> str:
    """从 prompt required output payload 中提取 exact marker item。

    Args:
        item: legacy required output 原文，或 typed payload 多行字符串。

    Returns:
        legacy 原文或 typed stable item id。

    Raises:
        无显式抛出。
    """

    first_line = item.splitlines()[0] if item else ""
    if first_line.startswith("<!-- required_output:") and first_line.endswith(" -->"):
        return first_line.removeprefix("<!-- required_output:").removesuffix(" -->")
    return item



def _required_lines(required_items: tuple[str, ...]) -> str:
    """构造 required output items 的测试正文行。

    Args:
        required_items: CHAPTER_CONTRACT required output items。

    Returns:
        Markdown 行文本。

    Raises:
        无显式抛出。
    """

    return "\n".join(f"<!-- required_output:{item} -->\n- {item}: {_required_line_text(item)}" for item in required_items)


def _required_line_text(item: str) -> str:
    """构造单个 required output 的测试文本。

    Args:
        item: required output item 原文或 typed item id。

    Returns:
        可通过 writer / auditor 程序检查的测试文本。

    Raises:
        无显式抛出。
    """

    if item.startswith("ch2.required_output.") or item.startswith("ch3.required_output."):
        return "证据不足，下一步最小验证问题是复核同源年报披露。"
    return "已根据结构化事实说明。"


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
