"""Agent tool adapters 测试，见模板第 1-6 章。"""

from __future__ import annotations

import ast
import inspect

from fund_agent.agent import tools as tools_module
from fund_agent.agent.tools import (
    AUDIT_CHAPTER_LLM_TOOL_NAME,
    AUDIT_CHAPTER_PROGRAMMATIC_TOOL_NAME,
    PROJECT_CHAPTER_FACTS_TOOL_NAME,
    SUPPORTED_TOOL_NAMES,
    WRITE_CHAPTER_TOOL_NAME,
    audit_chapter_llm_tool,
    audit_chapter_programmatic_tool,
    project_chapter_facts_tool,
    write_chapter_tool,
)
from fund_agent.fund.chapter_auditor import ChapterAuditInput
from fund_agent.fund.chapter_facts import project_chapter_facts
from fund_agent.fund.chapter_writer import (
    ChapterDraft,
    ChapterLLMRequest,
    ChapterLLMResponse,
    build_chapter_prompt,
    build_chapter_writer_input,
)
from tests.fund.test_chapter_auditor import _FakeAuditLLMClient
from tests.fund.test_chapter_facts import _bundle
from tests.fund.test_chapter_writer import (
    _FakeChapterLLMClient,
    _valid_chapter_markdown_for_prompt,
)


def test_supported_tool_names_exclude_run_level_evidence_availability() -> None:
    """验证 availability 派生不是 ToolRegistry 工具。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当工具集合暴露 run-level availability 时抛出。
    """

    assert SUPPORTED_TOOL_NAMES == (
        PROJECT_CHAPTER_FACTS_TOOL_NAME,
        WRITE_CHAPTER_TOOL_NAME,
        AUDIT_CHAPTER_PROGRAMMATIC_TOOL_NAME,
        AUDIT_CHAPTER_LLM_TOOL_NAME,
    )
    assert "fund.derive_evidence_availability" not in SUPPORTED_TOOL_NAMES


def test_project_chapter_facts_tool_records_run_level_safe_trace() -> None:
    """验证投影工具记录 run-level 安全 trace。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 trace 章节归属或安全字段错误时抛出。
    """

    execution = project_chapter_facts_tool(_bundle(), chapter_ids=(1, 2), attempt_index=0)

    assert execution.exception is None
    assert execution.output is not None
    safe = execution.trace.to_safe_dict()
    assert safe["tool_name"] == PROJECT_CHAPTER_FACTS_TOOL_NAME
    assert safe["chapter_id"] is None
    assert safe["status"] == "succeeded"
    assert safe["terminal_state"] == "accepted"
    assert safe["request_metadata"] == {
        "fund_code": "110011",
        "report_year": 2024,
        "chapter_count": 2,
    }
    assert safe["result_metadata"]["projected_chapter_count"] == 2


def test_write_chapter_tool_records_prompt_cost_without_payload() -> None:
    """验证 writer 工具只记录 prompt 成本标量。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 trace 泄漏 prompt/draft/raw response 时抛出。
    """

    input_data = _writer_input(1)
    prompt = build_chapter_prompt(input_data)
    anchor_id = input_data.chapter.evidence_anchors[0].anchor_id
    text = _valid_chapter_markdown_for_prompt(input_data, prompt, anchor_id)

    execution = write_chapter_tool(
        input_data,
        llm_client=_FakeChapterLLMClient(text),
        attempt_index=0,
        request_id="req-writer-safe",
    )

    assert execution.exception is None
    assert execution.output is not None
    assert execution.output.status == "drafted"
    safe = execution.trace.to_safe_dict()
    assert safe["tool_name"] == WRITE_CHAPTER_TOOL_NAME
    assert safe["chapter_id"] == 1
    assert safe["status"] == "succeeded"
    assert safe["terminal_state"] == "accepted"
    assert safe["response_chars"] == len(text)
    assert safe["request_id"] == "req-writer-safe"
    result_metadata = safe["result_metadata"]
    assert result_metadata["prompt_chars"] > 0
    assert result_metadata["approx_prompt_tokens"] > 0
    _assert_trace_excludes_unsafe_payloads(safe)


def test_write_chapter_tool_blocks_prompt_contract_without_draft_payload() -> None:
    """验证 writer 契约失败记录 issue id 而不保存草稿。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 blocked trace 泄漏草稿时抛出。
    """

    input_data = _writer_input(1)
    execution = write_chapter_tool(
        input_data,
        llm_client=_FakeChapterLLMClient("不符合固定结构"),
        attempt_index=1,
    )

    assert execution.exception is None
    assert execution.output is not None
    assert execution.output.status == "blocked"
    safe = execution.trace.to_safe_dict()
    assert safe["status"] == "blocked"
    assert safe["terminal_state"] == "blocked_prompt_contract"
    assert safe["issue_ids"]
    _assert_trace_excludes_unsafe_payloads(safe)


def test_programmatic_audit_tool_records_rule_counts_without_draft() -> None:
    """验证程序审计工具只记录规则数量和 issue id。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当程序审计 trace 泄漏草稿时抛出。
    """

    audit_input = _audit_input()

    execution = audit_chapter_programmatic_tool(audit_input, attempt_index=0)

    assert execution.exception is None
    assert execution.output is not None
    safe = execution.trace.to_safe_dict()
    assert safe["tool_name"] == AUDIT_CHAPTER_PROGRAMMATIC_TOOL_NAME
    assert safe["status"] == "succeeded"
    assert safe["terminal_state"] == "accepted"
    assert safe["result_metadata"]["checked_rule_count"] > 0
    _assert_trace_excludes_unsafe_payloads(safe)


def test_llm_audit_tool_records_raw_response_length_only() -> None:
    """验证 LLM 审计工具只记录 raw response 长度。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 LLM 审计 trace 泄漏 raw response 时抛出。
    """

    audit_input = _audit_input()
    raw_text = "PASS|chapter|no issues"

    execution = audit_chapter_llm_tool(
        audit_input,
        llm_client=_FakeAuditLLMClient(raw_text),
        attempt_index=0,
        request_id="req-audit-safe",
    )

    assert execution.exception is None
    assert execution.output is not None
    safe = execution.trace.to_safe_dict()
    assert safe["tool_name"] == AUDIT_CHAPTER_LLM_TOOL_NAME
    assert safe["status"] == "succeeded"
    assert safe["terminal_state"] == "accepted"
    assert safe["response_chars"] == len(raw_text)
    assert safe["request_id"] == "req-audit-safe"
    _assert_trace_excludes_unsafe_payloads(safe)


def test_tool_adapter_exception_trace_uses_safe_error_type_only() -> None:
    """验证异常 trace 只记录异常类型，不记录异常消息或 payload。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当异常 trace 泄漏不安全内容时抛出。
    """

    input_data = _writer_input(1)

    class _ExplodingWriter:
        """抛异常的 writer fake。"""

        def generate_chapter(self, request: ChapterLLMRequest) -> ChapterLLMResponse:
            """抛出带敏感字符串的异常。

            Args:
                request: writer request。

            Returns:
                不返回。

            Raises:
                RuntimeError: 始终抛出。
            """

            raise RuntimeError("api_key=secret raw_provider_response=payload")

    execution = write_chapter_tool(
        input_data,
        llm_client=_ExplodingWriter(),
        attempt_index=0,
    )

    assert execution.output is None
    assert execution.exception is not None
    safe = execution.trace.to_safe_dict()
    assert safe["status"] == "failed"
    assert safe["terminal_state"] == "blocked_internal_code_bug"
    assert safe["result_metadata"] == {"error_type": "RuntimeError"}
    _assert_trace_excludes_unsafe_payloads(safe)


def test_agent_tools_do_not_import_host_or_service() -> None:
    """验证 Agent tools 不导入 Host 或 Service。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 Agent tools 依赖 Host/Service 时抛出。
    """

    source = inspect.getsource(tools_module)
    tree = ast.parse(source)
    imported_modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_modules.update(alias.name for alias in node.names)
        if isinstance(node, ast.ImportFrom) and node.module is not None:
            imported_modules.add(node.module)

    assert not any(module.startswith("fund_agent.host") for module in imported_modules)
    assert not any(module.startswith("fund_agent.services") for module in imported_modules)


def _writer_input(chapter_id: int) -> object:
    """构造测试 writer input。

    Args:
        chapter_id: 模板章节编号。

    Returns:
        writer typed 输入。

    Raises:
        ValueError: 当投影或 writer input 构造失败时抛出。
    """

    projection = project_chapter_facts(_bundle(), chapter_ids=(chapter_id,))
    return build_chapter_writer_input(projection, chapter_id=chapter_id)


def _audit_input() -> ChapterAuditInput:
    """构造测试 auditor input。

    Args:
        无。

    Returns:
        auditor typed 输入。

    Raises:
        ValueError: 当投影或 writer input 构造失败时抛出。
    """

    writer_input = _writer_input(1)
    anchor_id = writer_input.chapter.evidence_anchors[0].anchor_id
    prompt = build_chapter_prompt(writer_input)
    markdown = _valid_chapter_markdown_for_prompt(writer_input, prompt, anchor_id)
    draft = ChapterDraft(
        chapter_id=writer_input.chapter.chapter_id,
        title=writer_input.chapter.title,
        markdown=markdown,
        used_fact_ids=tuple(fact.fact_id for fact in writer_input.chapter.facts),
        used_anchor_ids=(anchor_id,),
        declared_missing_reasons=(),
        deleted_item_rule_ids=(),
        model_name="fake-writer",
        finish_reason="stop",
    )
    return ChapterAuditInput(writer_input=writer_input, draft=draft)


def _assert_trace_excludes_unsafe_payloads(safe_trace: dict[str, object]) -> None:
    """断言安全 trace 不包含不安全 payload 字段或内容。

    Args:
        safe_trace: `ToolTrace.to_safe_dict()` 输出。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当输出包含不安全字段或内容时抛出。
    """

    rendered = repr(safe_trace).lower()
    forbidden_fragments = (
        "system_prompt':",
        "user_prompt':",
        "draft_markdown",
        "raw_provider_response",
        "raw_audit_response",
        "api_key",
        "authorization",
        "bearer",
        "model_name",
        "base_url",
        "headers",
        "不符合固定结构",
        "pass|chapter|no issues",
    )
    for fragment in forbidden_fragments:
        assert fragment not in rendered
