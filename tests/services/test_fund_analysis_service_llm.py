"""Gate 4 Slice 4B Service LLM 分析用例测试，覆盖模板第 0-7 章。"""

from __future__ import annotations

import ast
import asyncio
from pathlib import Path

import pytest

from fund_agent.fund.chapter_auditor import (
    ChapterAuditLLMRequest,
    ChapterAuditLLMResponse,
)
from fund_agent.fund.chapter_writer import (
    ChapterLLMRequest,
    ChapterLLMResponse,
)
from fund_agent.services import (
    ChapterOrchestrationPolicy,
    ChapterOrchestratorLLMClients,
    FundLLMAnalysisResult,
    QualityGateBlockedError,
    QualityGateNotRunBlockedError,
)
from fund_agent.host import HostRuntimeRunner
from fund_agent.host.runtime import HostRunEventType
from fund_agent.services.fund_analysis_service import FundAnalysisService
from tests.services.test_fund_analysis_service import (
    _FakeExtractor,
    _bundle,
    _developer_request,
    _low_quality_bundle,
    _source_csv,
)


class _FakeChapterLLMClient:
    """测试用章节写作 fake client，只存在于 Service LLM 测试。

    Attributes:
        requests: 收到的 writer typed requests。
        texts: 可选固定章节 Markdown 序列。
    """

    def __init__(self, texts: tuple[str, ...] = ()) -> None:
        """初始化 fake writer。

        Args:
            texts: 固定返回文本；为空时按请求动态生成合法章节。

        Returns:
            无返回值。

        Raises:
            无显式抛出。
        """

        self.requests: list[ChapterLLMRequest] = []
        self.texts = list(texts)

    def generate_chapter(self, request: ChapterLLMRequest) -> ChapterLLMResponse:
        """返回 fake 章节写作响应。

        Args:
            request: Gate 2 writer typed request。

        Returns:
            fake LLM 写作响应。

        Raises:
            无显式抛出。
        """

        self.requests.append(request)
        text = self.texts.pop(0) if self.texts else _valid_markdown_from_request(request)
        return ChapterLLMResponse(
            text=text,
            model_name="fake-writer",
            finish_reason="stop",
        )


class _FakeAuditLLMClient:
    """测试用章节审计 fake client，只存在于 Service LLM 测试。

    Attributes:
        requests: 收到的 auditor typed requests。
    """

    def __init__(self) -> None:
        """初始化 fake auditor。

        Args:
            无。

        Returns:
            无返回值。

        Raises:
            无显式抛出。
        """

        self.requests: list[ChapterAuditLLMRequest] = []

    def audit_chapter(self, request: ChapterAuditLLMRequest) -> ChapterAuditLLMResponse:
        """返回 PASS 行协议响应。

        Args:
            request: Gate 2 auditor typed request。

        Returns:
            fake LLM 审计响应。

        Raises:
            无显式抛出。
        """

        self.requests.append(request)
        return ChapterAuditLLMResponse(
            raw_text="PASS|chapter|no issues",
            model_name="fake-auditor",
            finish_reason="stop",
        )


@pytest.mark.asyncio
async def test_analyze_with_llm_returns_accepted_final_assembly_and_report_markdown() -> None:
    """验证 LLM Service 用例串起 core、Gate 3 和 Gate 4 accepted 报告。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 LLM 路径未总装 accepted 报告时抛出。
    """

    extractor = _FakeExtractor(_bundle())
    writer = _FakeChapterLLMClient()
    auditor = _FakeAuditLLMClient()
    service = FundAnalysisService(extractor=extractor)

    result = await service.analyze_with_llm(
        _developer_request(force_refresh=True),
        llm_clients=_clients(writer=writer, auditor=auditor),
        chapter_policy=ChapterOrchestrationPolicy(run_programmatic_audit=False),
    )

    assert isinstance(result, FundLLMAnalysisResult)
    assert extractor.calls == [("110011", 2024, True)]
    assert len(writer.requests) == 6
    assert len(auditor.requests) == 6
    assert result.llm_orchestration_result.status == "accepted"
    assert result.final_assembly_result.status == "accepted"
    assert result.final_assembly_result.assembled_chapter_ids == (0, 1, 2, 3, 4, 5, 6, 7)
    assert "## 第 0 章：投资要点概览" in result.report_markdown
    assert "## 第 7 章：是否值得持有--最终判断" in result.report_markdown
    assert result.quality_gate_result is None
    assert result.quality_gate_not_run_reason == "policy=off"


def test_host_runner_records_llm_service_phase_events() -> None:
    """验证 Host 托管 Service LLM 路径时记录章节 phase 和 final assembly。"""

    extractor = _FakeExtractor(_bundle())
    writer = _FakeChapterLLMClient()
    auditor = _FakeAuditLLMClient()
    service = FundAnalysisService(extractor=extractor)

    def operation(host_context):  # type: ignore[no-untyped-def]
        return asyncio.run(
            service.analyze_with_llm(
                _developer_request(force_refresh=True),
                llm_clients=_clients(writer=writer, auditor=auditor),
                chapter_policy=ChapterOrchestrationPolicy(
                    run_programmatic_audit=False,
                    target_chapter_ids=(1,),
                ),
                host_context=host_context,
            )
        )

    host_result = HostRuntimeRunner().run_sync(
        operation_name="fund_analysis_llm_report",
        operation=operation,
        timeout_seconds=30,
    )

    phase_events = [
        event
        for event in host_result.events
        if event.event_type
        in {HostRunEventType.PHASE_STARTED, HostRunEventType.PHASE_COMPLETED}
    ]
    assert host_result.status == "succeeded"
    assert [(event.event_type, event.diagnostics["phase"]) for event in phase_events] == [
        (HostRunEventType.PHASE_STARTED, "writer"),
        (HostRunEventType.PHASE_COMPLETED, "writer"),
        (HostRunEventType.PHASE_STARTED, "auditor"),
        (HostRunEventType.PHASE_COMPLETED, "auditor"),
        (HostRunEventType.PHASE_STARTED, "final_assembly"),
        (HostRunEventType.PHASE_COMPLETED, "final_assembly"),
    ]
    assert phase_events[0].diagnostics["chapter_id"] == 1


@pytest.mark.asyncio
async def test_deterministic_analyze_does_not_call_llm_orchestrator_path() -> None:
    """验证原 analyze 确定性路径不调用 LLM writer/auditor。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当确定性 analyze 误触发 LLM fake client 时抛出。
    """

    writer = _FakeChapterLLMClient()
    auditor = _FakeAuditLLMClient()
    service = FundAnalysisService(extractor=_FakeExtractor(_bundle()))

    result = await service.analyze(_developer_request())

    assert "# 0. 投资要点概览" in result.report_markdown
    assert writer.requests == []
    assert auditor.requests == []


@pytest.mark.asyncio
async def test_deterministic_checklist_does_not_call_llm_orchestrator_path() -> None:
    """验证原 checklist 确定性路径不调用 LLM writer/auditor。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 checklist 误触发 LLM fake client 时抛出。
    """

    writer = _FakeChapterLLMClient()
    auditor = _FakeAuditLLMClient()
    service = FundAnalysisService(extractor=_FakeExtractor(_bundle()))

    result = await service.checklist(_developer_request())

    assert len(result.checklist_result.items) == 7
    assert writer.requests == []
    assert auditor.requests == []


@pytest.mark.asyncio
async def test_missing_writer_or_auditor_blocks_without_deterministic_fallback() -> None:
    """验证缺 writer/auditor 时返回 typed blocked/incomplete，不回退确定性报告。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当缺 client 被 deterministic renderer 掩盖时抛出。
    """

    service = FundAnalysisService(extractor=_FakeExtractor(_bundle()))

    result = await service.analyze_with_llm(
        _developer_request(),
        llm_clients=ChapterOrchestratorLLMClients(
            writer=_FakeChapterLLMClient(),
            auditor=None,
        ),
    )

    assert result.llm_orchestration_result.status == "blocked"
    assert tuple(
        chapter_result.chapter_id
        for chapter_result in result.llm_orchestration_result.chapter_results
    ) == (1, 2, 3, 4, 5, 6)
    assert result.final_assembly_result.status == "incomplete"
    assert result.final_assembly_result.report_markdown is None
    with pytest.raises(ValueError, match="LLM 分析报告尚未完成"):
        _ = result.report_markdown


@pytest.mark.asyncio
async def test_analyze_with_llm_propagates_quality_gate_block_before_orchestration(
    tmp_path: Path,
) -> None:
    """验证 quality gate block 在进入 Gate 3 前按既有异常传播。

    Args:
        tmp_path: pytest 临时目录 fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 block 异常被吞掉或 LLM 被调用时抛出。
    """

    extractor = _FakeExtractor(_low_quality_bundle())
    writer = _FakeChapterLLMClient()
    auditor = _FakeAuditLLMClient()
    service = FundAnalysisService(extractor=extractor)

    with pytest.raises(QualityGateBlockedError) as exc_info:
        await service.analyze_with_llm(
            _developer_request(
                fund_code="004393",
                quality_gate_policy="block",
                quality_gate_source_csv=Path("docs/code_20260519.csv"),
                quality_gate_output_dir=tmp_path / "gate",
                quality_gate_run_id="fixture-run",
                quality_gate_golden_answer_path=None,
            ),
            llm_clients=_clients(writer=writer, auditor=auditor),
        )

    assert extractor.calls == [("004393", 2024, False)]
    assert exc_info.value.quality_gate_result.status == "block"
    assert writer.requests == []
    assert auditor.requests == []


@pytest.mark.asyncio
async def test_analyze_with_llm_propagates_quality_gate_not_run_before_extraction(
    tmp_path: Path,
) -> None:
    """验证 quality gate not-run 在 block 策略下沿用既有早停异常。

    Args:
        tmp_path: pytest 临时目录 fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 not-run 异常未早停或 LLM 被调用时抛出。
    """

    extractor = _FakeExtractor(_bundle())
    writer = _FakeChapterLLMClient()
    auditor = _FakeAuditLLMClient()
    service = FundAnalysisService(extractor=extractor)

    with pytest.raises(QualityGateNotRunBlockedError) as exc_info:
        await service.analyze_with_llm(
            _developer_request(
                fund_code="110011",
                quality_gate_policy="block",
                quality_gate_source_csv=_source_csv(tmp_path, "004393"),
                quality_gate_run_id="fixture-run",
                quality_gate_golden_answer_path=None,
            ),
            llm_clients=_clients(writer=writer, auditor=auditor),
        )

    assert exc_info.value.reason == "fund_code `110011` not found in quality gate source csv"
    assert extractor.calls == []
    assert writer.requests == []
    assert auditor.requests == []


def test_fund_analysis_service_imports_keep_llm_path_above_forbidden_boundaries() -> None:
    """验证 LLM Service 路径只依赖 Host contract，不直连底层来源或 dayu。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 Service 模块出现越界导入时抛出。
    """

    imports = _imports_for(Path("fund_agent/services/fund_analysis_service.py"))
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
    assert "fund_agent.fund.data_extractor" in imports
    assert "fund_agent.host" in imports


def _clients(
    *,
    writer: _FakeChapterLLMClient | None = None,
    auditor: _FakeAuditLLMClient | None = None,
) -> ChapterOrchestratorLLMClients:
    """构造测试用 LLM client bundle。

    Args:
        writer: fake writer；未提供时创建默认 fake。
        auditor: fake auditor；未提供时创建默认 fake。

    Returns:
        Gate 3 LLM clients。

    Raises:
        无显式抛出。
    """

    return ChapterOrchestratorLLMClients(
        writer=writer if writer is not None else _FakeChapterLLMClient(),
        auditor=auditor if auditor is not None else _FakeAuditLLMClient(),
    )


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
    return (
        "### 结论要点\n"
        f"{_required_lines(_required_items_from_request(request))}\n"
        "### 详细情况\n"
        "本章只使用已断言事实，并把候选 facet 写成未断言。\n"
        "### 证据与出处\n"
        f"<!-- anchor:{anchor_id} -->\n"
        "> 📎 证据：年报2024§§2表None行fixture（fixture）\n"
    )


def _required_items_from_request(request: ChapterLLMRequest) -> tuple[str, ...]:
    """从 writer prompt 文本中解析 required output items。

    Args:
        request: writer typed request。

    Returns:
        required output items。

    Raises:
        ValueError: 当 prompt 不含 required output items 时抛出。
    """

    marker = "必须输出项："
    for line in request.user_prompt.splitlines():
        if line.startswith(marker):
            return tuple(ast.literal_eval(line.removeprefix(marker)))
    raise ValueError("writer request 缺少必须输出项")


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
