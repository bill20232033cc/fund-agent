"""CLI 入口测试。"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from decimal import Decimal
from pathlib import Path

import pytest
from typer.main import get_command
from typer.testing import CliRunner

from fund_agent.fund.data.thermometer_cache import ThermometerHistoryCache
from fund_agent.fund.data.thermometer_types import PePbHistory, PePbPoint
from fund_agent.fund.quality_gate import QualityGateIssue, QualityGateResult
from fund_agent.services import (
    FundLLMHostedRunResult,
    QualityGateBlockedError,
    QualityGateNotRunBlockedError,
    ThermometerBatchResult,
    ThermometerReading,
)
from fund_agent.services.fund_analysis_service import EvidenceConfirmBlockedError
from fund_agent.ui import cli


@dataclass(frozen=True, slots=True)
class _FakeEventType:
    """CLI 测试用带 value 的事件类型。"""

    value: str


@dataclass(frozen=True, slots=True)
class _FakeHostEvent:
    """CLI 测试用 duck-typed Host event。"""

    event_type: object
    run_id: str
    phase: str | None = None
    chapter_id: int | None = None
    attempt: int | None = None
    elapsed_ms: int | None = None
    diagnostics: dict[str, object] | None = None


def _emit_fake_progress_events(event_sink) -> None:  # type: ignore[no-untyped-def]
    """在 fake hosted Service 中发送安全 progress events。

    Args:
        event_sink: UI 传入的 progress sink。

    Returns:
        无返回值。

    Raises:
        无显式抛出。
    """

    if event_sink is None:
        return
    event_sink(
        _FakeHostEvent(
            event_type=_FakeEventType("run_started"),
            run_id="host_run_fake",
            diagnostics={"timeout_seconds": 372},
        )
    )
    event_sink(_FakeHostEvent(event_type="phase_started", run_id="host_run_fake", phase="analysis_core"))
    event_sink(
        _FakeHostEvent(
            event_type="phase_completed",
            run_id="host_run_fake",
            phase="analysis_core",
            elapsed_ms=1,
        )
    )
    event_sink(
        _FakeHostEvent(
            event_type="phase_started",
            run_id="host_run_fake",
            phase="writer",
            chapter_id=1,
            attempt=0,
        )
    )
    event_sink(
        _FakeHostEvent(
            event_type="phase_completed",
            run_id="host_run_fake",
            phase="writer",
            chapter_id=1,
            attempt=0,
            elapsed_ms=2,
        )
    )
    event_sink(_FakeHostEvent(event_type="phase_started", run_id="host_run_fake", phase="final_assembly"))
    event_sink(
        _FakeHostEvent(
            event_type="phase_completed",
            run_id="host_run_fake",
            phase="final_assembly",
            elapsed_ms=3,
        )
    )


def _emit_fake_run_started(event_sink) -> None:  # type: ignore[no-untyped-def]
    """发送 fake run_started 事件。

    Args:
        event_sink: UI 传入的 progress sink。

    Returns:
        无返回值。

    Raises:
        无显式抛出。
    """

    if event_sink is None:
        return
    event_sink(
        _FakeHostEvent(
            event_type=_FakeEventType("run_started"),
            run_id="host_run_fake",
            diagnostics={"timeout_seconds": 372},
        )
    )


def _hosted_result(
    analysis_result: object | None,
    *,
    status: str = "succeeded",
    run_id: str = "host_run_fake",
    elapsed_ms: int | None = 0,
    timeout_classification: str | None = None,
    diagnostics: dict[str, object] | None = None,
    operation_result_present: bool | None = None,
) -> FundLLMHostedRunResult:
    """构造 Service-owned hosted run result。

    Args:
        analysis_result: fake LLM 分析结果。
        status: Host 终态字符串。
        run_id: Host run id。
        elapsed_ms: Host run 耗时。
        timeout_classification: timeout 分类。
        diagnostics: 安全诊断。
        operation_result_present: 是否存在 operation result；缺省按 result 是否为空推断。

    Returns:
        fake hosted run result。

    Raises:
        无显式抛出。
    """

    return FundLLMHostedRunResult(
        analysis_result=analysis_result,  # type: ignore[arg-type]
        host_status=status,
        host_run_id=run_id,
        host_elapsed_ms=elapsed_ms,
        host_timeout_classification=timeout_classification,
        host_safe_diagnostics=diagnostics or {},
        host_event_count=8,
        host_completed_at_iso="2026-06-11T00:00:00+00:00",
        host_operation_result_present=(
            analysis_result is not None
            if operation_result_present is None
            else operation_result_present
        ),
    )


@dataclass(frozen=True, slots=True)
class _FakeResult:
    """CLI 测试用 Service 返回值。"""

    report_markdown: str
    quality_gate_result: object | None = None
    quality_gate_not_run_reason: str | None = None
    evidence_confirm_summary: object | None = None


@dataclass(frozen=True, slots=True)
class _FakeEvidenceConfirmSummary:
    """CLI 测试用 Evidence Confirm 安全摘要。"""

    policy: str
    status: str
    checked_fact_count: int = 8
    failed_fact_count: int = 0
    auditability_score: int | None = 92
    not_run_reason: str | None = None
    source_excerpt: str | None = None
    pdf_path: str | None = None
    parser_payload: object | None = None
    provider_payload: object | None = None


@dataclass(frozen=True, slots=True)
class _FakeAnnualEvidenceBundle:
    """CLI 多年年报测试用 bundle。"""

    fund_code: str = "110011"
    target_year: int = 2025
    canonical_years: tuple[int, ...] = (2025, 2024, 2023, 2022, 2021)
    available_years: tuple[int, ...] = (2025,)
    gap_years: tuple[int, ...] = (2024, 2023, 2022, 2021)
    fail_closed_years: tuple[int, ...] = ()
    cross_year_facts: tuple[object, ...] = ()
    fallback_summary: dict[str, object] = field(
        default_factory=lambda: {"fallback_year_count": 0}
    )
    source_provenance_by_year: dict[int, object] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class _FakeAnnualPeriodReport:
    """CLI 多年年报测试用 annual-period report。"""

    report_markdown: str


@dataclass(frozen=True, slots=True)
class _FakeMultiYearResult:
    """CLI 多年年报测试用 Service 返回值。"""

    current_year_result: _FakeResult
    annual_evidence_bundle: _FakeAnnualEvidenceBundle
    annual_period_report: _FakeAnnualPeriodReport

    @property
    def report_markdown(self) -> str:
        """返回 fake 当前年份报告。

        Args:
            无。

        Returns:
            fake Markdown。

        Raises:
            无显式抛出。
        """

        return self.current_year_result.report_markdown


@dataclass(frozen=True, slots=True)
class _FakeLLMFinalAssemblyResult:
    """CLI LLM 测试用 final assembly 结果。"""

    status: str
    report_markdown: str | None
    issues: tuple[object, ...] = ()


@dataclass(frozen=True, slots=True)
class _FakeRuntimeDiagnostic:
    """CLI LLM 测试用 runtime diagnostic。"""

    operation: str
    provider_attempt_index: int | None = None
    provider_max_attempts: int | None = None
    provider_runtime_category: str | None = None
    elapsed_ms: int | None = None
    system_prompt_chars: int | None = None
    user_prompt_chars: int | None = None
    approx_prompt_tokens: int | None = None
    allowed_fact_count: int | None = None
    allowed_anchor_count: int | None = None
    max_output_chars: int | None = None
    timeout_root_cause_hint: str | None = None
    message: str | None = None


@dataclass(frozen=True, slots=True)
class _FakeChapterRunResult:
    """CLI LLM 测试用章节结果。"""

    chapter_id: int
    status: str
    stop_reason: str
    failure_category: str | None = None
    failure_subcategory: str | None = None
    attempts: tuple[object, ...] = ()
    runtime_diagnostics: tuple[object, ...] = ()


@dataclass(frozen=True, slots=True)
class _FakeLLMOrchestrationResult:
    """CLI LLM 测试用 orchestration 结果。"""

    status: str
    blocked_reasons: tuple[str, ...] = ()
    chapter_results: tuple[_FakeChapterRunResult, ...] = ()


@dataclass(frozen=True, slots=True)
class _FakeLLMResult:
    """CLI LLM 测试用 Service 返回值。"""

    final_assembly_result: _FakeLLMFinalAssemblyResult
    llm_orchestration_result: _FakeLLMOrchestrationResult
    quality_gate_result: object | None = None
    quality_gate_not_run_reason: str | None = None

    @property
    def report_markdown(self) -> str:
        """返回 fake LLM 报告。

        Args:
            无。

        Returns:
            fake LLM Markdown。

        Raises:
            ValueError: 当 fake final assembly 未产出报告时抛出。
        """

        if self.final_assembly_result.report_markdown is None:
            raise ValueError("fake LLM report incomplete")
        return self.final_assembly_result.report_markdown


class _FakeService:
    """CLI 测试用成功 Service。"""

    last_request = None
    last_hosted_request = None
    last_multi_year_request = None
    last_event_sink = None
    analyze_called = False
    analyze_multi_year_annual_called = False
    analyze_with_llm_hosted_called = False

    async def analyze(self, request):  # type: ignore[no-untyped-def]
        """记录请求并返回固定 Markdown。

        Args:
            request: CLI 构造的 Service 请求。

        Returns:
            fake Service 返回值。

        Raises:
            无显式抛出。
        """

        type(self).analyze_called = True
        type(self).last_request = request
        return _FakeResult(report_markdown="# 0. 投资要点概览\n\n# 7. 是否值得持有——最终判断\n")

    async def analyze_multi_year_annual(self, request):  # type: ignore[no-untyped-def]
        """记录多年年报请求并返回固定 Markdown。

        Args:
            request: CLI 构造的多年年报 Service 请求。

        Returns:
            fake 多年年报 Service 返回值。

        Raises:
            无显式抛出。
        """

        type(self).analyze_multi_year_annual_called = True
        type(self).last_multi_year_request = request
        return _FakeMultiYearResult(
            current_year_result=_FakeResult(report_markdown="# current year report\n"),
            annual_evidence_bundle=_FakeAnnualEvidenceBundle(),
            annual_period_report=_FakeAnnualPeriodReport(
                report_markdown="# annual period report\n"
            ),
        )

    def analyze_with_llm_hosted(  # type: ignore[no-untyped-def]
        self,
        hosted_request,
        *,
        event_sink=None,
    ):
        """记录 LLM 分析调用，测试 fail-closed 时不得触发。

        Args:
            hosted_request: CLI 构造的 Service 请求。
            event_sink: UI progress sink。

        Returns:
            fake Service 返回值。

        Raises:
            无显式抛出。
        """

        type(self).analyze_with_llm_hosted_called = True
        type(self).last_hosted_request = hosted_request
        type(self).last_event_sink = event_sink
        _emit_fake_progress_events(event_sink)
        return _hosted_result(
            _FakeLLMResult(
                final_assembly_result=_FakeLLMFinalAssemblyResult(
                    status="accepted",
                    report_markdown="# LLM report\n",
                ),
                llm_orchestration_result=_FakeLLMOrchestrationResult(status="accepted"),
            )
        )


@dataclass(frozen=True, slots=True)
class _FakeChecklistItem:
    """CLI checklist 测试用单项结果。"""

    code: str
    signal: str
    status: str
    question: str
    reason: str
    anchors: tuple[object, ...] = ()


@dataclass(frozen=True, slots=True)
class _FakeChecklistResult:
    """CLI checklist 测试用检查清单结果。"""

    items: tuple[_FakeChecklistItem, ...]
    overall_signal: str
    overall_status: str
    next_minimum_verification: str


@dataclass(frozen=True, slots=True)
class _FakeValuationResolution:
    """CLI checklist 测试用估值解析结果。"""

    state: str
    source: str
    index_code: str | None = None
    temperature: Decimal | None = None


@dataclass(frozen=True, slots=True)
class _FakeFinalJudgmentDecision:
    """CLI checklist 测试用最终判断结果。"""

    selected_judgment: str
    derived_judgment: str
    source: str


@dataclass(frozen=True, slots=True)
class _FakeStructuredData:
    """CLI checklist 测试用结构化数据摘要。"""

    fund_code: str
    report_year: int


@dataclass(frozen=True, slots=True)
class _FakeChecklistServiceResult:
    """CLI checklist 测试用 Service 结果。"""

    structured_data: _FakeStructuredData
    checklist_result: _FakeChecklistResult
    valuation_state_resolution: _FakeValuationResolution
    final_judgment_decision: _FakeFinalJudgmentDecision
    quality_gate_result: object | None = None
    quality_gate_not_run_reason: str | None = None


class _FakeChecklistService:
    """CLI 测试用独立 checklist Service。"""

    last_request = None
    checklist_called = False

    async def checklist(self, request):  # type: ignore[no-untyped-def]
        """记录请求并返回固定检查清单。

        Args:
            request: CLI 构造的 Service 请求。

        Returns:
            fake checklist Service 返回值。

        Raises:
            无显式抛出。
        """

        type(self).checklist_called = True
        type(self).last_request = request
        item = _FakeChecklistItem(
            code="valuation",
            signal="green",
            status="pass",
            question="当前估值处于什么位置？",
            reason="当前估值偏低。",
            anchors=(object(),),
        )
        return _FakeChecklistServiceResult(
            structured_data=_FakeStructuredData(fund_code=request.fund_code, report_year=request.report_year),
            checklist_result=_FakeChecklistResult(
                items=(item,),
                overall_signal="green",
                overall_status="pass",
                next_minimum_verification="进入程序审计。",
            ),
            valuation_state_resolution=_FakeValuationResolution(
                state="low",
                source="explicit_user_input",
                index_code="000300",
                temperature=Decimal("12.3"),
            ),
            final_judgment_decision=_FakeFinalJudgmentDecision(
                selected_judgment="worth_holding",
                derived_judgment="worth_holding",
                source="derived",
            ),
        )


class _FakeWarnService:
    """CLI 测试用带 quality gate warning 的 Service。"""

    async def analyze(self, request):  # type: ignore[no-untyped-def]
        """返回携带 gate 结果的 fake 报告。

        Args:
            request: CLI 构造的 Service 请求。

        Returns:
            fake Service 返回值。

        Raises:
            无显式抛出。
        """

        return _FakeResult(
            report_markdown="# 0. 投资要点概览\n",
            quality_gate_result=_fake_quality_gate_result(status="warn"),
        )


class _FakeEvidenceConfirmWarnService:
    """CLI 测试用带 Evidence Confirm 摘要的 Service。"""

    last_request = None

    async def analyze(self, request):  # type: ignore[no-untyped-def]
        """记录请求并返回 Evidence Confirm safe summary。

        Args:
            request: CLI 构造的 Service 请求。

        Returns:
            fake Service 返回值。

        Raises:
            无显式抛出。
        """

        type(self).last_request = request
        return _FakeResult(
            report_markdown="# report body\n",
            evidence_confirm_summary=_FakeEvidenceConfirmSummary(
                policy="warn",
                status="warn",
                checked_fact_count=8,
                failed_fact_count=1,
                auditability_score=None,
            ),
        )


class _FakeProductEvidenceConfirmWarnService:
    """CLI 测试用默认 product Evidence Confirm 摘要 Service。"""

    last_request = None

    async def analyze(self, request):  # type: ignore[no-untyped-def]
        """记录 product 请求并返回只应暴露 safe fields 的摘要。

        Args:
            request: CLI 构造的 Service 请求。

        Returns:
            fake Service 返回值。

        Raises:
            无显式抛出。
        """

        type(self).last_request = request
        summary = _FakeEvidenceConfirmSummary(
            policy="warn",
            status="warn",
            checked_fact_count=8,
            failed_fact_count=1,
            auditability_score=87,
            source_excerpt="secret excerpt should stay hidden",
            pdf_path="/tmp/source.pdf",
            parser_payload={"raw": "parser json"},
            provider_payload={"raw": "provider body"},
        )
        return _FakeResult(
            report_markdown="# report body\n",
            evidence_confirm_summary=summary,
        )


class _FakeAnnualPeriodEvidenceConfirmService:
    """CLI 多年年报测试用带 current-year Evidence Confirm 摘要的 Service。"""

    async def analyze_multi_year_annual(self, request):  # type: ignore[no-untyped-def]
        """返回带 current-year Evidence Confirm safe summary 的多年年报结果。

        Args:
            request: CLI 构造的多年年报 Service 请求。

        Returns:
            fake 多年年报 Service 返回值。

        Raises:
            无显式抛出。
        """

        return _FakeMultiYearResult(
            current_year_result=_FakeResult(
                report_markdown="# current year report\n",
                evidence_confirm_summary=_FakeEvidenceConfirmSummary(
                    policy="warn",
                    status="warn",
                    checked_fact_count=8,
                    failed_fact_count=1,
                    auditability_score=87,
                    source_excerpt="annual secret excerpt",
                    pdf_path="/tmp/annual-source.pdf",
                    parser_payload={"raw": "annual parser"},
                    provider_payload={"raw": "annual provider"},
                ),
            ),
            annual_evidence_bundle=_FakeAnnualEvidenceBundle(),
            annual_period_report=_FakeAnnualPeriodReport(
                report_markdown="# annual period report\n"
            ),
        )


class _FakeInfoService:
    """CLI 测试用带 quality gate informational issue 的 Service。"""

    async def analyze(self, request):  # type: ignore[no-untyped-def]
        """返回携带 FQ0/info coverage issue 的 fake 报告。

        Args:
            request: CLI 构造的 Service 请求。

        Returns:
            fake Service 返回值。

        Raises:
            无显式抛出。
        """

        return _FakeResult(
            report_markdown="# 0. 投资要点概览\n",
            quality_gate_result=_fake_quality_gate_result(
                status="pass",
                issues=(
                    QualityGateIssue(
                        rule_code="FQ0",
                        severity="info",
                        fund_code="000216",
                        field_name=None,
                        priority=None,
                        message="strict golden answer 尚未覆盖",
                        reason="fund_not_covered",
                        coverage_scope="fund_not_covered",
                    ),
                ),
            ),
        )


class _FakeBlockedAnalysisService:
    """CLI 测试用 quality gate 阻断 Service。"""

    async def analyze(self, request):  # type: ignore[no-untyped-def]
        """抛出结构化 quality gate 阻断异常。

        Args:
            request: CLI 构造的 Service 请求。

        Returns:
            无返回值。

        Raises:
            QualityGateBlockedError: 始终抛出。
        """

        raise QualityGateBlockedError(_fake_quality_gate_result(status="block"))


class _FakeNotRunBlockedAnalysisService:
    """CLI 测试用 quality gate 未运行阻断 Service。"""

    async def analyze(self, request):  # type: ignore[no-untyped-def]
        """抛出 quality gate 未运行阻断异常。

        Args:
            request: CLI 构造的 Service 请求。

        Returns:
            无返回值。

        Raises:
            QualityGateNotRunBlockedError: 始终抛出。
        """

        raise QualityGateNotRunBlockedError("fund_code `110011` not found")


class _FakeEvidenceConfirmBlockedAnalysisService:
    """CLI 测试用 Evidence Confirm 阻断 Service。"""

    last_request = None

    async def analyze(self, request):  # type: ignore[no-untyped-def]
        """抛出 Evidence Confirm 阻断异常。

        Args:
            request: CLI 构造的 Service 请求。

        Returns:
            无返回值。

        Raises:
            EvidenceConfirmBlockedError: 始终抛出。
        """

        type(self).last_request = request
        raise EvidenceConfirmBlockedError(
            _FakeEvidenceConfirmSummary(
                policy="block",
                status="fail",
                checked_fact_count=8,
                failed_fact_count=2,
                auditability_score=41,
                not_run_reason="deterministic_fail",
            )
        )


class _FakeLLMBlockedAnalysisService:
    """CLI LLM 测试用 quality gate 阻断 Service。"""

    async def analyze(self, request):  # type: ignore[no-untyped-def]
        """默认确定性 analyze 不应被 LLM path 调用。

        Args:
            request: CLI 构造的 Service 请求。

        Returns:
            无返回值。

        Raises:
            AssertionError: 始终抛出。
        """

        raise AssertionError("deterministic analyze must not be called")

    def analyze_with_llm_hosted(  # type: ignore[no-untyped-def]
        self,
        hosted_request,
        *,
        event_sink=None,
    ):
        """抛出结构化 quality gate 阻断异常。

        Args:
            hosted_request: CLI 构造的 Service 请求。
            event_sink: UI progress sink。

        Returns:
            无返回值。

        Raises:
            QualityGateBlockedError: 始终抛出。
        """

        _emit_fake_run_started(event_sink)
        raise QualityGateBlockedError(_fake_quality_gate_result(status="block"))


class _FakeLLMNotRunBlockedAnalysisService:
    """CLI LLM 测试用 quality gate 未运行阻断 Service。"""

    async def analyze(self, request):  # type: ignore[no-untyped-def]
        """默认确定性 analyze 不应被 LLM path 调用。

        Args:
            request: CLI 构造的 Service 请求。

        Returns:
            无返回值。

        Raises:
            AssertionError: 始终抛出。
        """

        raise AssertionError("deterministic analyze must not be called")

    def analyze_with_llm_hosted(  # type: ignore[no-untyped-def]
        self,
        hosted_request,
        *,
        event_sink=None,
    ):
        """抛出 quality gate 未运行阻断异常。

        Args:
            hosted_request: CLI 构造的 Service 请求。
            event_sink: UI progress sink。

        Returns:
            无返回值。

        Raises:
            QualityGateNotRunBlockedError: 始终抛出。
        """

        _emit_fake_run_started(event_sink)
        raise QualityGateNotRunBlockedError("fund_code `110011` not found")


class _IncompleteLLMService(_FakeService):
    """返回 incomplete LLM 结果的 fake Service。"""

    def analyze_with_llm_hosted(  # type: ignore[no-untyped-def]
        self,
        hosted_request,
        *,
        event_sink=None,
    ):
        """记录调用并返回 incomplete final assembly。

        Args:
            hosted_request: CLI 构造的 Service 请求。
            event_sink: UI progress sink。

        Returns:
            incomplete fake LLM result。

        Raises:
            无显式抛出。
        """

        type(self).analyze_with_llm_hosted_called = True
        type(self).last_hosted_request = hosted_request
        type(self).last_event_sink = event_sink
        _emit_fake_progress_events(event_sink)
        return _hosted_result(
            _FakeLLMResult(
                final_assembly_result=_FakeLLMFinalAssemblyResult(
                    status="blocked",
                    report_markdown=None,
                    issues=("chapter_missing",),
                ),
                llm_orchestration_result=_FakeLLMOrchestrationResult(status="partial"),
            ),
            status="failed",
            diagnostics={"error_type": "_LLMIncompleteHostRunError"},
        )


class _L1IncompleteLLMService(_FakeService):
    """返回 L1 programmatic audit 分类 incomplete LLM 结果的 fake Service。"""

    def analyze_with_llm_hosted(  # type: ignore[no-untyped-def]
        self,
        hosted_request,
        *,
        event_sink=None,
    ):
        """记录调用并返回 L1 数字闭环阻断结果。

        Args:
            hosted_request: CLI 构造的 Service 请求。
            event_sink: UI progress sink。

        Returns:
            incomplete fake LLM result。

        Raises:
            无显式抛出。
        """

        type(self).analyze_with_llm_hosted_called = True
        type(self).last_hosted_request = hosted_request
        type(self).last_event_sink = event_sink
        _emit_fake_progress_events(event_sink)
        return _hosted_result(
            _FakeLLMResult(
                final_assembly_result=_FakeLLMFinalAssemblyResult(
                    status="blocked",
                    report_markdown=None,
                    issues=("chapter_missing",),
                ),
                llm_orchestration_result=_FakeLLMOrchestrationResult(
                    status="partial",
                    chapter_results=(
                        _FakeChapterRunResult(
                            chapter_id=2,
                            status="failed",
                            stop_reason="repair_budget_exhausted",
                            failure_category="prompt_contract",
                            failure_subcategory="l1_numerical_closure",
                        ),
                    ),
                ),
            ),
            status="failed",
            diagnostics={"error_type": "_LLMIncompleteHostRunError"},
        )


class _TimeoutLLMService(_FakeService):
    """返回 timeout 分类 incomplete LLM 结果的 fake Service。"""

    def analyze_with_llm_hosted(  # type: ignore[no-untyped-def]
        self,
        hosted_request,
        *,
        event_sink=None,
    ):
        """记录调用并返回 llm_timeout 阻断结果。

        Args:
            hosted_request: CLI 构造的 Service 请求。
            event_sink: UI progress sink。

        Returns:
            incomplete fake LLM result。

        Raises:
            无显式抛出。
        """

        type(self).analyze_with_llm_hosted_called = True
        type(self).last_hosted_request = hosted_request
        type(self).last_event_sink = event_sink
        _emit_fake_progress_events(event_sink)
        return _hosted_result(
            _FakeLLMResult(
                final_assembly_result=_FakeLLMFinalAssemblyResult(
                    status="blocked",
                    report_markdown=None,
                    issues=("llm_timeout",),
                ),
                llm_orchestration_result=_FakeLLMOrchestrationResult(
                    status="blocked",
                    blocked_reasons=("llm_timeout",),
                    chapter_results=(
                        _FakeChapterRunResult(
                            chapter_id=2,
                            status="failed",
                            stop_reason="llm_timeout",
                            failure_category="llm_timeout",
                            failure_subcategory=None,
                            runtime_diagnostics=(
                                _FakeRuntimeDiagnostic(
                                    operation="writer",
                                    provider_attempt_index=1,
                                    provider_max_attempts=2,
                                    provider_runtime_category="timeout",
                                    elapsed_ms=120000,
                                    system_prompt_chars=40,
                                    user_prompt_chars=360,
                                    approx_prompt_tokens=100,
                                    allowed_fact_count=None,
                                    allowed_anchor_count=3,
                                    max_output_chars=12000,
                                    timeout_root_cause_hint="small_prompt_provider_timeout",
                                    message=(
                                        "message writer auditor programmatic raw audit "
                                        "system_prompt user_prompt draft_markdown "
                                        "provider_response provider body Authorization "
                                        "Bearer sk-secret header key"
                                    ),
                                ),
                                _FakeRuntimeDiagnostic(
                                    operation="writer",
                                    provider_attempt_index=2,
                                    provider_max_attempts=2,
                                    provider_runtime_category="timeout",
                                    elapsed_ms=121000,
                                    system_prompt_chars=40,
                                    user_prompt_chars=360,
                                    approx_prompt_tokens=100,
                                    allowed_fact_count=None,
                                    allowed_anchor_count=3,
                                    max_output_chars=12000,
                                    timeout_root_cause_hint="small_prompt_provider_timeout",
                                    message="second message should not render",
                                ),
                            ),
                        ),
                    ),
                ),
            ),
            status="failed",
            timeout_classification="provider_runtime_timeout",
            diagnostics={"error_type": "_LLMIncompleteHostRunError"},
        )


class _MatrixIncompleteLLMService(_FakeService):
    """返回多章节 mixed matrix 的 incomplete LLM 结果。"""

    def analyze_with_llm_hosted(  # type: ignore[no-untyped-def]
        self,
        hosted_request,
        *,
        event_sink=None,
    ):
        """记录调用并返回含 accepted/failed 行的 all-chapter matrix。

        Args:
            hosted_request: CLI 构造的 Service 请求。
            event_sink: UI progress sink。

        Returns:
            incomplete fake LLM result。

        Raises:
            无显式抛出。
        """

        type(self).analyze_with_llm_hosted_called = True
        type(self).last_hosted_request = hosted_request
        type(self).last_event_sink = event_sink
        _emit_fake_progress_events(event_sink)
        return _hosted_result(
            _FakeLLMResult(
                final_assembly_result=_FakeLLMFinalAssemblyResult(
                    status="incomplete",
                    report_markdown=None,
                    issues=("chapter_missing",),
                ),
                llm_orchestration_result=_FakeLLMOrchestrationResult(
                    status="partial",
                    chapter_results=(
                        _FakeChapterRunResult(
                            chapter_id=1,
                            status="failed",
                            stop_reason="llm_timeout",
                            failure_category="llm_timeout",
                        ),
                        _FakeChapterRunResult(
                            chapter_id=2,
                            status="accepted",
                            stop_reason="none",
                        ),
                        _FakeChapterRunResult(
                            chapter_id=3,
                            status="blocked",
                            stop_reason="missing_required_output_marker",
                            failure_category="prompt_contract",
                            failure_subcategory="missing_required_marker",
                            runtime_diagnostics=(
                                _FakeRuntimeDiagnostic(
                                    operation="writer",
                                    provider_attempt_index=1,
                                    provider_max_attempts=1,
                                    provider_runtime_category="malformed",
                                    elapsed_ms=9,
                                    system_prompt_chars=10,
                                    user_prompt_chars=20,
                                    approx_prompt_tokens=8,
                                    message=(
                                        "message Authorization Bearer sk-secret api_key "
                                        "system_prompt user_prompt draft_markdown raw_response "
                                        "raw audit provider_response provider body model_name header key"
                                    ),
                                ),
                            ),
                        ),
                    ),
                ),
            ),
            status="failed",
            diagnostics={"error_type": "_LLMIncompleteHostRunError"},
        )


class _FailingService:
    """CLI 测试用失败 Service。"""

    async def analyze(self, request):  # type: ignore[no-untyped-def]
        """抛出固定异常。

        Args:
            request: CLI 构造的 Service 请求。

        Returns:
            无返回值。

        Raises:
            RuntimeError: 始终抛出。
        """

        raise RuntimeError("fixture failure")


class _FailingLLMService(_FakeService):
    """CLI 测试用 Host 托管 LLM 失败 Service。"""

    def analyze_with_llm_hosted(  # type: ignore[no-untyped-def]
        self,
        hosted_request,
        *,
        event_sink=None,
    ):
        """抛出固定 LLM 异常，验证 Host fail-closed 输出不被二次包装。"""

        _emit_fake_run_started(event_sink)
        return _hosted_result(
            None,
            status="failed",
            diagnostics={"error_type": "RuntimeError"},
            operation_result_present=False,
        )


class _LLMConfigErrorService(_FakeService):
    """CLI 测试用 LLM 配置错误 Service。"""

    def analyze_with_llm_hosted(  # type: ignore[no-untyped-def]
        self,
        hosted_request,
        *,
        event_sink=None,
    ):
        """模拟 Service hosted 用例在 Host run 前发现 LLM 配置缺失。"""

        raise cli.LLMProviderConfigError("missing FUND_AGENT_LLM_PROVIDER")


class _LLMConstructionErrorService(_FakeService):
    """CLI 测试用 LLM provider 构造错误 Service。"""

    def analyze_with_llm_hosted(  # type: ignore[no-untyped-def]
        self,
        hosted_request,
        *,
        event_sink=None,
    ):
        """模拟 Service hosted 用例在 Host run 前构造 provider 失败。"""

        raise cli.LLMProviderConstructionError("fixture construction failure")


def _fake_quality_gate_result(
    *,
    status: str,
    issues: tuple[object, ...] = (object(), object()),
) -> QualityGateResult:
    """构造 CLI 分析路径使用的 fake quality gate 结果。

    Args:
        status: gate 状态。

    Returns:
        fake quality gate 结果。

    Raises:
        无显式抛出。
    """

    return QualityGateResult(
        score_path=Path("score.json"),
        output_dir=Path("quality-output"),
        gate_json_path=Path("quality-output/quality_gate.json"),
        gate_markdown_path=Path("quality-output/quality_gate.md"),
        status=status,
        issues=issues,
    )


@dataclass(frozen=True, slots=True)
class _FakeSnapshotResult:
    """CLI 测试用快照运行结果。"""

    snapshot_path: Path
    summary_path: Path
    errors_path: Path


class _FakeExtractionSnapshotService:
    """CLI 测试用快照 Service。"""

    last_request = None

    async def run(self, request):  # type: ignore[no-untyped-def]
        """记录请求并返回固定路径。

        Args:
            request: CLI 构造的快照请求。

        Returns:
            fake 快照结果。

        Raises:
            无显式抛出。
        """

        type(self).last_request = request
        return _FakeSnapshotResult(
            snapshot_path=Path("snapshot.jsonl"),
            summary_path=Path("summary.md"),
            errors_path=Path("errors.jsonl"),
        )


@dataclass(frozen=True, slots=True)
class _FakeExtractorOutputIdentity:
    """CLI 测试用 extractor output 身份。"""

    fund_code: str
    report_type: str
    report_year: int


@dataclass(frozen=True, slots=True)
class _FakeExtractorOutputRecord:
    """CLI 测试用 extractor output 保存结果。"""

    schema_version: str
    identity: _FakeExtractorOutputIdentity
    path: Path


class _FakeExtractorOutputService:
    """CLI 测试用 extractor output Service。"""

    last_request = None

    async def save(self, request):  # type: ignore[no-untyped-def]
        """记录请求并返回固定保存结果。

        Args:
            request: CLI 构造的保存请求。

        Returns:
            fake 保存结果。

        Raises:
            无显式抛出。
        """

        type(self).last_request = request
        return _FakeExtractorOutputRecord(
            schema_version="fund-agent.extractor_output.v1",
            identity=_FakeExtractorOutputIdentity(
                fund_code=request.fund_code,
                report_type=request.report_type,
                report_year=request.report_year,
            ),
            path=Path("reports/extractor-outputs/004393/annual_report/2024/structured_fund_data.json"),
        )


@dataclass(frozen=True, slots=True)
class _FakeScoreResult:
    """CLI 测试用评分运行结果。"""

    score_json_path: Path
    score_markdown_path: Path
    golden_set_path: Path


class _FakeExtractionScoreService:
    """CLI 测试用评分 Service。"""

    last_request = None

    def run(self, request):  # type: ignore[no-untyped-def]
        """记录请求并返回固定路径。

        Args:
            request: CLI 构造的评分请求。

        Returns:
            fake 评分结果。

        Raises:
            无显式抛出。
        """

        type(self).last_request = request
        return _FakeScoreResult(
            score_json_path=Path("score.json"),
            score_markdown_path=Path("score.md"),
            golden_set_path=Path("golden_set.json"),
        )


@dataclass(frozen=True, slots=True)
class _FakeGoldenPrefillResult:
    """CLI 测试用 golden prefill 结果。"""

    output_path: Path
    fund_codes: tuple[str, ...]
    succeeded_fund_codes: tuple[str, ...]
    failed_fund_codes: tuple[str, ...]


class _FakeGoldenPrefillService:
    """CLI 测试用 golden prefill Service。"""

    last_request = None

    async def run(self, request):  # type: ignore[no-untyped-def]
        """记录请求并返回固定路径。

        Args:
            request: CLI 构造的预填请求。

        Returns:
            fake 预填结果。

        Raises:
            无显式抛出。
        """

        type(self).last_request = request
        return _FakeGoldenPrefillResult(
            output_path=Path("prefill.md"),
            fund_codes=("004393",),
            succeeded_fund_codes=("004393",),
            failed_fund_codes=(),
        )


@dataclass(frozen=True, slots=True)
class _FakeGoldenAnswerBuildResult:
    """CLI 测试用 golden answer build 结果。"""

    output_path: Path
    fund_count: int
    record_count: int
    skipped_count: int


class _FakeGoldenAnswerService:
    """CLI 测试用 golden answer Service。"""

    last_request = None

    def build(self, request):  # type: ignore[no-untyped-def]
        """记录请求并返回固定统计。

        Args:
            request: CLI 构造的 golden answer build 请求。

        Returns:
            fake 构建结果。

        Raises:
            无显式抛出。
        """

        type(self).last_request = request
        return _FakeGoldenAnswerBuildResult(
            output_path=Path("golden-answer.json"),
            fund_count=1,
            record_count=2,
            skipped_count=1,
        )


@dataclass(frozen=True, slots=True)
class _FakeQualityGateResult:
    """CLI 测试用 quality gate 结果。"""

    gate_json_path: Path
    gate_markdown_path: Path
    status: str
    issues: tuple[object, ...]


class _FakeQualityGateService:
    """CLI 测试用 quality gate Service。"""

    last_request = None

    def run(self, request):  # type: ignore[no-untyped-def]
        """记录请求并返回固定 gate 结果。

        Args:
            request: CLI 构造的 quality gate 请求。

        Returns:
            fake gate 结果。

        Raises:
            无显式抛出。
        """

        type(self).last_request = request
        return _FakeQualityGateResult(
            gate_json_path=Path("quality_gate.json"),
            gate_markdown_path=Path("quality_gate.md"),
            status="block",
            issues=(object(), object()),
        )


@dataclass(frozen=True, slots=True)
class _FakeGoldenReadinessPreflightResult:
    """CLI 测试用 golden readiness preflight 结果。"""

    json_path: Path
    markdown_path: Path
    overall_status: str


class _FakeGoldenReadinessPreflightService:
    """CLI 测试用 golden readiness preflight Service。"""

    last_request = None

    def run(self, request):  # type: ignore[no-untyped-def]
        """记录请求并返回固定 preflight 路径。

        Args:
            request: CLI 构造的 preflight 请求。

        Returns:
            fake preflight 结果。

        Raises:
            无显式抛出。
        """

        type(self).last_request = request
        return _FakeGoldenReadinessPreflightResult(
            json_path=Path("golden_readiness_preflight.json"),
            markdown_path=Path("golden_readiness_preflight.md"),
            overall_status="block",
        )


class _FakeThermometerService:
    """CLI 测试用温度计 Service。"""

    last_request = None
    snapshot = None

    async def run(self, request):  # type: ignore[no-untyped-def]
        """记录请求并返回固定温度计快照。

        Args:
            request: CLI 构造的温度计请求。

        Returns:
            fake 温度计快照。

        Raises:
            无显式抛出。
        """

        type(self).last_request = request
        return type(self).snapshot or _available_all_a_thermometer_reading()


class _FailingThermometerService:
    """CLI 测试用失败温度计 Service。"""

    async def run(self, request):  # type: ignore[no-untyped-def]
        """抛出固定异常。

        Args:
            request: CLI 构造的温度计请求。

        Returns:
            无返回值。

        Raises:
            RuntimeError: 始终抛出。
        """

        raise RuntimeError("thermometer fixture failure")


def _forbid_llm_artifact_writer(*args, **kwargs):  # type: ignore[no-untyped-def]
    """不应触发 LLM artifact 写入的测试路径哨兵。

    Args:
        args: 未使用。
        kwargs: 未使用。

    Returns:
        无返回值。

    Raises:
        AssertionError: 始终抛出。
    """

    raise AssertionError("LLM artifact writer must not be called")


def _available_thermometer_reading() -> ThermometerReading:
    """构造可用自建温度计读数。

    Args:
        无。

    Returns:
        自建温度计读数。

    Raises:
        无显式抛出。
    """

    return ThermometerReading(
        index_code="000300",
        index_name="沪深300",
        temperature=Decimal("42.50"),
        pe_percentile=Decimal("40.00"),
        pb_percentile=Decimal("45.00"),
        valuation_state_candidate="fair",
        data_date="2026-05-22",
        lookback_start="2005-04-08",
        lookback_end="2026-05-22",
        source="akshare_legulegu_index_pe_pb",
        cached=False,
        stale=False,
        unavailable=False,
        unavailable_reason=None,
        fetched_at="2026-05-23T00:00:00+00:00",
    )


def _available_all_a_thermometer_reading() -> ThermometerReading:
    """构造可用全 A 市场温度计读数。

    Args:
        无。

    Returns:
        全 A 市场温度计读数。

    Raises:
        无显式抛出。
    """

    return ThermometerReading(
        index_code="wind_all_a",
        index_name="万得全 A / 全 A 市场",
        temperature=Decimal("35.25"),
        pe_percentile=Decimal("30.00"),
        pb_percentile=Decimal("40.50"),
        valuation_state_candidate="fair",
        data_date="2026-05-22",
        lookback_start="2005-01-04",
        lookback_end="2026-05-22",
        source="akshare_legulegu_all_a_pe_pb",
        cached=False,
        stale=False,
        unavailable=False,
        unavailable_reason=None,
        fetched_at="2026-05-23T00:00:00+00:00",
    )


def _unavailable_all_a_thermometer_reading() -> ThermometerReading:
    """构造不可用全 A 市场温度计读数。

    Args:
        无。

    Returns:
        不可用全 A 市场温度计读数。

    Raises:
        无显式抛出。
    """

    return ThermometerReading(
        index_code="wind_all_a",
        index_name="万得全 A / 全 A 市场",
        temperature=None,
        pe_percentile=None,
        pb_percentile=None,
        valuation_state_candidate="unavailable",
        data_date=None,
        lookback_start=None,
        lookback_end=None,
        source="self_owned_thermometer",
        cached=False,
        stale=False,
        unavailable=True,
        unavailable_reason="network down",
        fetched_at=None,
    )


def _available_thermometer_batch_result() -> ThermometerBatchResult:
    """构造批量自建温度计结果。

    Args:
        无。

    Returns:
        批量温度计结果。

    Raises:
        无显式抛出。
    """

    return ThermometerBatchResult(
        requested_index_codes=("000300", "000905"),
        generated_at="2026-05-23T00:00:00+00:00",
        readings=(
            _available_thermometer_reading(),
            ThermometerReading(
                index_code="000905",
                index_name="中证500",
                temperature=Decimal("52.50"),
                pe_percentile=Decimal("50.00"),
                pb_percentile=Decimal("55.00"),
                valuation_state_candidate="fair",
                data_date="2026-05-22",
                lookback_start="2007-01-15",
                lookback_end="2026-05-22",
                source="akshare_legulegu_index_pe_pb",
                cached=False,
                stale=False,
                unavailable=False,
                unavailable_reason=None,
                fetched_at="2026-05-23T00:00:00+00:00",
            ),
        ),
    )


def _available_all_a_mixed_batch_result() -> ThermometerBatchResult:
    """构造全 A 与指数混合批量自建温度计结果。

    Args:
        无。

    Returns:
        混合批量温度计结果。

    Raises:
        无显式抛出。
    """

    return ThermometerBatchResult(
        requested_index_codes=("wind_all_a", "000300"),
        generated_at="2026-05-23T00:00:00+00:00",
        readings=(
            _available_all_a_thermometer_reading(),
            _available_thermometer_reading(),
        ),
    )


def _partial_unavailable_thermometer_batch_result() -> ThermometerBatchResult:
    """构造部分不可用的批量自建温度计结果。

    Args:
        无。

    Returns:
        部分不可用批量温度计结果。

    Raises:
        无显式抛出。
    """

    return ThermometerBatchResult(
        requested_index_codes=("000300", "999999"),
        generated_at="2026-05-23T00:00:00+00:00",
        readings=(
            _available_thermometer_reading(),
            ThermometerReading(
                index_code="999999",
                index_name="999999",
                temperature=None,
                pe_percentile=None,
                pb_percentile=None,
                valuation_state_candidate="unavailable",
                data_date=None,
                lookback_start=None,
                lookback_end=None,
                source="self_owned_thermometer",
                cached=False,
                stale=False,
                unavailable=True,
                unavailable_reason="自建温度计数据不可用：暂不支持指数：999999",
                fetched_at=None,
            ),
        ),
        unavailable=False,
        partial_unavailable=True,
        unavailable_count=1,
    )


def _cli_index_history(index_code: str, index_name: str) -> PePbHistory:
    """构造 CLI 真实 Service cache 测试使用的 PE/PB 历史。

    Args:
        index_code: 指数代码。
        index_name: 指数名称。

    Returns:
        满足温度计计算最小样本要求的历史序列。

    Raises:
        无显式抛出。
    """

    return PePbHistory(
        index_code=index_code,
        index_name=index_name,
        source="fixture",
        points=tuple(
            PePbPoint(
                date=f"2026-05-{day:02d}",
                pe=Decimal(day),
                pb=Decimal(day) / Decimal("10"),
            )
            for day in range(1, 31)
        ),
    )


def test_analyze_cli_calls_service_and_prints_report(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """验证 analyze 命令调用 Service 并输出 Markdown。

    Args:
        monkeypatch: pytest monkeypatch fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 CLI 未调用 Service 或未输出报告时抛出。
    """

    _FakeService.last_request = None
    _FakeService.last_hosted_request = None
    _FakeService.analyze_called = False
    _FakeService.analyze_with_llm_hosted_called = False
    monkeypatch.setattr(cli, "FundAnalysisService", _FakeService)
    runner = CliRunner()

    result = runner.invoke(
        cli.app,
        [
            "analyze",
            "110011",
            "--report-year",
            "2024",
            "--dev-override",
            "--equity-position",
            "80%",
            "--actual-style",
            "均衡",
            "--actual-equity-position",
            "70%",
            "--manager-tenure-months",
            "24",
            "--peer-fee-median",
            "1.00%",
            "--investment-amount",
            "10000",
            "--max-tolerable-loss-rate",
            "50%",
            "--valuation-state",
            "low",
            "--thermometer-cache-dir",
            "cache/thermometer-fixture",
            "--user-money-horizon-years",
            "4",
            "--current-stage",
            "fixture stage",
            "--final-judgment",
            "worth_holding",
            "--force-refresh",
            "--quality-gate-policy",
            "warn",
            "--quality-gate-source-csv",
            "docs/code_20260519.csv",
            "--quality-gate-output-dir",
            "quality-output",
            "--quality-gate-run-id",
            "fixture-run",
            "--quality-gate-golden-answer-path",
            "reports/golden-answers/golden-answer.json",
        ],
    )

    assert result.exit_code == 0
    assert result.output == "# 0. 投资要点概览\n\n# 7. 是否值得持有——最终判断\n"
    assert _FakeService.analyze_called is True
    assert _FakeService.analyze_with_llm_hosted_called is False
    assert _FakeService.last_request is not None
    assert _FakeService.last_request.fund_code == "110011"
    assert _FakeService.last_request.report_year == 2024
    assert _FakeService.last_request.mode == "developer_override"
    assert _FakeService.last_request.developer_overrides is not None
    assert _FakeService.last_request.developer_overrides.equity_position == "80%"
    assert _FakeService.last_request.developer_overrides.final_judgment_override == "worth_holding"
    assert _FakeService.last_request.valuation_state == "low"
    assert _FakeService.last_request.thermometer_cache_dir == Path("cache/thermometer-fixture")
    assert _FakeService.last_request.force_refresh is True
    assert _FakeService.last_request.command_source == "analyze"
    assert _FakeService.last_request.developer_overrides.quality_gate_policy == "warn"
    assert _FakeService.last_request.developer_overrides.quality_gate_source_csv == Path(
        "docs/code_20260519.csv"
    )
    assert _FakeService.last_request.developer_overrides.quality_gate_output_dir == Path(
        "quality-output"
    )
    assert _FakeService.last_request.developer_overrides.quality_gate_run_id == "fixture-run"
    assert _FakeService.last_request.developer_overrides.quality_gate_golden_answer_path == Path(
        "reports/golden-answers/golden-answer.json"
    )
    assert _FakeService.last_request.developer_overrides.evidence_confirm_policy == "off"


def test_analyze_cli_dev_override_without_policy_keeps_evidence_confirm_off(
    monkeypatch,
) -> None:  # type: ignore[no-untyped-def]
    """验证 plain `--dev-override` 不继承 product Evidence Confirm warn。

    Args:
        monkeypatch: pytest monkeypatch fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当开发覆盖默认 Evidence Confirm 策略不是 off 时抛出。
    """

    _FakeService.last_request = None
    _FakeService.analyze_called = False
    monkeypatch.setattr(cli, "FundAnalysisService", _FakeService)
    runner = CliRunner()

    result = runner.invoke(cli.app, ["analyze", "110011", "--dev-override"])

    assert result.exit_code == 0
    assert _FakeService.analyze_called is True
    assert _FakeService.last_request is not None
    assert _FakeService.last_request.mode == "developer_override"
    assert _FakeService.last_request.developer_overrides is not None
    assert _FakeService.last_request.developer_overrides.evidence_confirm_policy == "off"


def test_analyze_annual_period_cli_calls_multi_year_service(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """验证多年年报 CLI 投影显式 Service 请求。

    Args:
        monkeypatch: pytest monkeypatch fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: CLI 未按契约调用 Service 时抛出。
    """

    _FakeService.analyze_called = False
    _FakeService.analyze_multi_year_annual_called = False
    _FakeService.last_multi_year_request = None
    monkeypatch.setattr(cli, "FundAnalysisService", _FakeService)

    result = CliRunner().invoke(
        cli.app,
        [
            "analyze-annual-period",
            "110011",
            "--target-year",
            "2025",
            "--start-year",
            "2021",
            "--valuation-state",
            "unavailable",
            "--quality-gate-policy",
            "off",
        ],
    )

    assert result.exit_code == 0
    assert "canonical_years: 2025,2024,2023,2022,2021" in result.output
    assert "# annual period report" in result.output
    assert "# current year report" not in result.output
    assert _FakeService.analyze_called is False
    assert _FakeService.analyze_multi_year_annual_called is True
    assert _FakeService.last_multi_year_request is not None
    assert _FakeService.last_multi_year_request.fund_code == "110011"
    assert _FakeService.last_multi_year_request.target_year == 2025
    assert _FakeService.last_multi_year_request.start_year == 2021
    assert _FakeService.last_multi_year_request.valuation_state == "unavailable"
    assert _FakeService.last_multi_year_request.quality_gate_policy == "off"


def test_analyze_annual_period_cli_prints_current_year_evidence_confirm_summary(
    monkeypatch,
) -> None:  # type: ignore[no-untyped-def]
    """验证 annual-period CLI 输出 current-year Evidence Confirm 安全摘要。

    Args:
        monkeypatch: pytest monkeypatch fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: annual-period CLI 未输出 safe summary 或泄漏原始证据时抛出。
    """

    monkeypatch.setattr(cli, "FundAnalysisService", _FakeAnnualPeriodEvidenceConfirmService)

    result = CliRunner().invoke(
        cli.app,
        [
            "analyze-annual-period",
            "110011",
            "--target-year",
            "2025",
            "--start-year",
            "2021",
            "--valuation-state",
            "unavailable",
            "--quality-gate-policy",
            "off",
        ],
    )

    assert result.exit_code == 0
    assert "evidence_confirm_status: warn" in result.output
    assert "evidence_confirm_policy: warn" in result.output
    assert "evidence_confirm_checked_facts: 8" in result.output
    assert "evidence_confirm_failed_facts: 1" in result.output
    assert "evidence_confirm_auditability_score: 87" in result.output
    assert "canonical_years: 2025,2024,2023,2022,2021" in result.output
    assert "# annual period report" in result.output
    assert "# current year report" not in result.output
    assert "annual secret excerpt" not in result.output
    assert "/tmp/annual-source.pdf" not in result.output
    assert "annual parser" not in result.output
    assert "annual provider" not in result.output


def test_analyze_cli_use_llm_missing_config_fails_before_service(
    monkeypatch,
) -> None:  # type: ignore[no-untyped-def]
    """验证 `analyze --use-llm` 缺失配置时失败且不调用 Service。

    Args:
        monkeypatch: pytest monkeypatch fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 CLI 调用 Service 或输出 deterministic 报告时抛出。
    """

    monkeypatch.setattr(cli, "FundAnalysisService", _LLMConfigErrorService)
    monkeypatch.setattr(
        cli,
        "write_llm_incomplete_run_artifacts",
        _forbid_llm_artifact_writer,
    )
    for env_name in (
        "FUND_AGENT_LLM_PROVIDER",
        "FUND_AGENT_LLM_BASE_URL",
        "FUND_AGENT_LLM_API_KEY",
        "FUND_AGENT_LLM_MODEL",
    ):
        monkeypatch.delenv(env_name, raising=False)
    runner = CliRunner()

    result = runner.invoke(cli.app, ["analyze", "110011", "--use-llm"])

    assert result.exit_code == 1
    assert result.stdout == ""
    assert "LLM provider 配置错误：missing FUND_AGENT_LLM_PROVIDER" in result.stderr
    assert "# 0. 投资要点概览" not in result.output


def test_analyze_cli_use_llm_configured_calls_llm_service_and_prints_report(
    monkeypatch,
) -> None:  # type: ignore[no-untyped-def]
    """验证配置完整时 CLI 调用 LLM Service 且输出 LLM 报告。

    Args:
        monkeypatch: pytest monkeypatch fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 CLI 调用 deterministic analyze 或未传递 typed policy 时抛出。
    """

    _FakeService.last_request = None
    _FakeService.last_hosted_request = None
    _FakeService.last_event_sink = None
    _FakeService.analyze_called = False
    _FakeService.analyze_with_llm_hosted_called = False
    monkeypatch.setattr(cli, "FundAnalysisService", _FakeService)
    runner = CliRunner()

    result = runner.invoke(cli.app, ["analyze", "110011", "--use-llm"])

    assert result.exit_code == 0
    assert result.stdout == "# LLM report\n"
    assert _FakeService.analyze_called is False
    assert _FakeService.analyze_with_llm_hosted_called is True
    assert _FakeService.last_request is None
    assert _FakeService.last_hosted_request is not None
    assert _FakeService.last_hosted_request.fund_code == "110011"
    assert _FakeService.last_hosted_request.report_year == 2024
    assert _FakeService.last_event_sink is not None


def test_analyze_cli_use_llm_default_non_tty_does_not_print_progress(
    monkeypatch,
) -> None:  # type: ignore[no-untyped-def]
    """验证非 TTY auto 模式默认不输出 LLM progress。"""

    monkeypatch.setattr(cli, "_llm_progress_auto_enabled", lambda: False)
    monkeypatch.setattr(cli, "FundAnalysisService", _FakeService)
    runner = CliRunner()

    result = runner.invoke(cli.app, ["analyze", "110011", "--use-llm"])

    assert result.exit_code == 0
    assert result.stdout == "# LLM report\n"
    assert "LLM progress:" not in result.stderr


def test_analyze_cli_use_llm_forced_progress_prints_safe_stderr(
    monkeypatch,
) -> None:  # type: ignore[no-untyped-def]
    """验证 forced progress 只向 stderr 输出安全进度行。"""

    monkeypatch.setattr(cli, "_llm_progress_auto_enabled", lambda: False)
    monkeypatch.setattr(cli, "FundAnalysisService", _FakeService)
    runner = CliRunner()

    result = runner.invoke(
        cli.app,
        ["analyze", "110011", "--use-llm", "--llm-progress"],
    )

    assert result.exit_code == 0
    assert result.stdout == "# LLM report\n"
    progress_lines = [
        line for line in result.stderr.splitlines() if line.startswith("LLM progress:")
    ]
    assert sum(" run_started " in line for line in progress_lines) == 1
    assert any(" phase_started phase=analysis_core " in line for line in progress_lines)
    assert any(" phase_completed phase=analysis_core " in line for line in progress_lines)
    assert any(" phase_started phase=writer " in line for line in progress_lines)
    assert any(" phase_completed phase=writer " in line for line in progress_lines)
    assert sum(" run_terminal " in line for line in progress_lines) == 1
    assert progress_lines[-1].endswith("event=run_completed elapsed_ms=0")
    assert "LLM progress:" not in result.stdout
    for forbidden in (
        "Authorization",
        "Bearer",
        "sk-",
        "api_key",
        "cookie",
        "secret_key",
        "access_key",
        "system_prompt",
        "user_prompt",
        "prompt",
        "draft_markdown",
        "raw_response",
        "provider_response",
        "provider body",
        "raw audit",
        "model_name",
        "header",
    ):
        assert forbidden not in "\n".join(progress_lines)


def test_analyze_cli_use_llm_auto_tty_prints_progress(
    monkeypatch,
) -> None:  # type: ignore[no-untyped-def]
    """验证 auto 模式在 helper 返回 TTY 时启用 progress。"""

    monkeypatch.setattr(cli, "_llm_progress_auto_enabled", lambda: True)
    monkeypatch.setattr(cli, "FundAnalysisService", _FakeService)
    runner = CliRunner()

    result = runner.invoke(cli.app, ["analyze", "110011", "--use-llm"])

    assert result.exit_code == 0
    assert result.stdout == "# LLM report\n"
    assert "LLM progress: run_started" in result.stderr


def test_analyze_cli_use_llm_no_progress_overrides_tty_auto(
    monkeypatch,
) -> None:  # type: ignore[no-untyped-def]
    """验证 `--no-llm-progress` 会覆盖 TTY auto。"""

    monkeypatch.setattr(cli, "_llm_progress_auto_enabled", lambda: True)
    monkeypatch.setattr(cli, "FundAnalysisService", _FakeService)
    runner = CliRunner()

    result = runner.invoke(
        cli.app,
        ["analyze", "110011", "--use-llm", "--no-llm-progress"],
    )

    assert result.exit_code == 0
    assert result.stdout == "# LLM report\n"
    assert "LLM progress:" not in result.stderr


def test_llm_progress_reporter_heartbeat_tick_lifecycle(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """验证 reporter heartbeat 的 deterministic tick 生命周期。

    Args:
        monkeypatch: pytest monkeypatch fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 heartbeat 判定或 throttle 失效时抛出。
    """

    lines: list[str] = []
    monkeypatch.setattr(cli.typer, "echo", lambda line, err=True, nl=True: lines.append(line))
    reporter = cli._LLMProgressReporter(enabled=True)
    event = _FakeHostEvent(
        event_type=_FakeEventType("phase_started"),
        run_id="host_run_test",
        diagnostics={
            "phase": "writer",
            "chapter_id": 1,
            "attempt": 0,
            "provider_attempt": None,
        },
    )

    reporter.handle_event(event)
    assert reporter._heartbeat_tick(now_monotonic=100.0) is True
    assert reporter._heartbeat_tick(now_monotonic=110.0) is False
    assert reporter._heartbeat_tick(now_monotonic=130.0) is True
    assert lines[-1].startswith("LLM progress: still_running phase=writer")
    reporter.stop()
    assert reporter._heartbeat_tick(now_monotonic=200.0) is False


def test_llm_progress_reporter_heartbeat_suppressed_after_sink_failure(
    monkeypatch,
) -> None:  # type: ignore[no-untyped-def]
    """验证 sink 失败后 heartbeat 被关闭。

    Args:
        monkeypatch: pytest monkeypatch fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 sink 失败后仍输出 heartbeat 时抛出。
    """

    def raise_echo(*args, **kwargs):  # type: ignore[no-untyped-def]
        """模拟 stderr 写入失败。

        Args:
            args: 未使用。
            kwargs: 未使用。

        Returns:
            无返回值。

        Raises:
            RuntimeError: 始终抛出。
        """

        raise RuntimeError("stderr closed")

    monkeypatch.setattr(cli.typer, "echo", raise_echo)
    reporter = cli._LLMProgressReporter(enabled=True)
    event = _FakeHostEvent(
        event_type=_FakeEventType("phase_started"),
        run_id="host_run_test",
        diagnostics={
            "phase": "writer",
            "chapter_id": 1,
            "attempt": 0,
            "provider_attempt": None,
        },
    )

    reporter.handle_event(event)

    assert reporter.sink_failed is True
    assert reporter._heartbeat_tick(now_monotonic=100.0) is False


def test_llm_progress_reporter_suppresses_heartbeat_after_terminal(
    monkeypatch,
) -> None:  # type: ignore[no-untyped-def]
    """验证 run_terminal 后不再输出 still_running。

    Args:
        monkeypatch: pytest monkeypatch fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 terminal 后仍输出 heartbeat 时抛出。
    """

    lines: list[str] = []
    monkeypatch.setattr(cli.typer, "echo", lambda line, err=True, nl=True: lines.append(line))
    reporter = cli._LLMProgressReporter(enabled=True)
    event = _FakeHostEvent(
        event_type=_FakeEventType("phase_started"),
        run_id="host_run_test",
        diagnostics={
            "phase": "writer",
            "chapter_id": 1,
            "attempt": 0,
            "provider_attempt": None,
        },
    )
    hosted_result = _hosted_result(
        object(),
        run_id="host_run_test",
        status="succeeded",
        elapsed_ms=42,
    )

    reporter.handle_event(event)
    reporter.emit_terminal(hosted_result)

    assert lines[-1] == "LLM progress: run_terminal run_id=host_run_test event=run_completed elapsed_ms=42"
    assert reporter._heartbeat_tick(now_monotonic=100.0) is False


def test_llm_progress_reporter_sink_exception_does_not_escape(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """验证 CLI sink wrapper 捕获 reporter 异常。

    Args:
        monkeypatch: pytest monkeypatch fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 reporter 异常逃逸或未标记 sink_failed 时抛出。
    """

    def raise_echo(*args, **kwargs):  # type: ignore[no-untyped-def]
        """模拟 stderr 写入失败。

        Args:
            args: 未使用。
            kwargs: 未使用。

        Returns:
            无返回值。

        Raises:
            RuntimeError: 始终抛出。
        """

        raise RuntimeError("stderr closed")

    monkeypatch.setattr(cli.typer, "echo", raise_echo)
    reporter = cli._LLMProgressReporter(enabled=True)
    event = _FakeHostEvent(
        event_type=_FakeEventType("run_started"),
        run_id="host_run_test",
        diagnostics={"timeout_seconds": 1},
    )

    reporter.event_sink(event)

    assert reporter.sink_failed is True


def test_analyze_cli_progress_sink_failure_does_not_affect_success(
    monkeypatch,
) -> None:  # type: ignore[no-untyped-def]
    """验证 progress sink 失败不影响 Host 终态、stdout 或 exit code。

    Args:
        monkeypatch: pytest monkeypatch fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 progress 失败改变 CLI 成功路径时抛出。
    """

    original_echo = cli.typer.echo

    def fail_progress_echo(message=None, *args, **kwargs):  # type: ignore[no-untyped-def]
        """只让 progress 行写入失败，普通 CLI 输出仍使用原 echo。

        Args:
            message: Typer echo 消息。
            args: 透传给原 echo 的位置参数。
            kwargs: 透传给原 echo 的关键字参数。

        Returns:
            原 echo 的返回值。

        Raises:
            RuntimeError: progress 行始终抛出，模拟 stderr 写入失败。
            Exception: 原 echo 可能传播的异常。
        """

        if isinstance(message, str) and message.startswith("LLM progress:"):
            raise RuntimeError("stderr closed")
        return original_echo(message, *args, **kwargs)

    monkeypatch.setattr(cli.typer, "echo", fail_progress_echo)
    monkeypatch.setattr(cli, "_llm_progress_auto_enabled", lambda: False)
    monkeypatch.setattr(cli, "FundAnalysisService", _FakeService)
    runner = CliRunner()

    result = runner.invoke(
        cli.app,
        ["analyze", "110011", "--use-llm", "--llm-progress"],
    )

    assert result.exit_code == 0
    assert result.stdout == "# LLM report\n"
    assert "LLM progress:" not in result.stderr


def test_analyze_cli_use_llm_construction_error_fails_before_service(
    monkeypatch,
) -> None:  # type: ignore[no-untyped-def]
    """验证 provider 构造失败时失败且不调用 Service。

    Args:
        monkeypatch: pytest monkeypatch fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当构造失败后仍调用 Service 或 stdout 非空时抛出。
    """

    monkeypatch.setattr(cli, "FundAnalysisService", _LLMConstructionErrorService)
    runner = CliRunner()

    result = runner.invoke(cli.app, ["analyze", "110011", "--use-llm"])

    assert result.exit_code == 1
    assert result.stdout == ""
    assert "LLM provider 构造失败：fixture construction failure" in result.stderr


def test_analyze_cli_use_llm_incomplete_result_exits_without_fallback(
    monkeypatch,
) -> None:  # type: ignore[no-untyped-def]
    """验证 LLM 总装未完成时退出 1 且不输出 deterministic 报告。

    Args:
        monkeypatch: pytest monkeypatch fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 CLI 回退 deterministic 报告或 stdout 非空时抛出。
    """

    _IncompleteLLMService.last_request = None
    _IncompleteLLMService.analyze_called = False
    _IncompleteLLMService.analyze_with_llm_hosted_called = False
    monkeypatch.setattr(cli, "FundAnalysisService", _IncompleteLLMService)
    runner = CliRunner()

    result = runner.invoke(cli.app, ["analyze", "110011", "--use-llm"])

    assert result.exit_code == 1
    assert result.stdout == ""
    assert "LLM 分析未完成：" in result.stderr
    assert "LLM Host run 未完成：" in result.stderr
    assert "status=failed" in result.stderr
    assert "error_type=_LLMIncompleteHostRunError" in result.stderr
    assert "orchestration_status=partial" in result.stderr
    assert "# 0. 投资要点概览" not in result.output
    assert _IncompleteLLMService.analyze_called is False
    assert _IncompleteLLMService.analyze_with_llm_hosted_called is True


def test_use_llm_incomplete_typed_readiness_empty_stdout_exit_one(
    monkeypatch,
) -> None:  # type: ignore[no-untyped-def]
    """验证 typed readiness incomplete 时 stdout 为空、退出 1 且无确定性回退。

    Args:
        monkeypatch: pytest monkeypatch fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 incomplete 被输出或回退 deterministic 报告时抛出。
    """

    _IncompleteLLMService.last_request = None
    _IncompleteLLMService.analyze_called = False
    _IncompleteLLMService.analyze_with_llm_hosted_called = False
    monkeypatch.setattr(cli, "FundAnalysisService", _IncompleteLLMService)
    runner = CliRunner()

    result = runner.invoke(cli.app, ["analyze", "110011", "--use-llm"])

    assert result.exit_code == 1
    assert result.stdout == ""
    assert "LLM 分析未完成：" in result.stderr
    assert "# 0. 投资要点概览" not in result.output
    assert _IncompleteLLMService.analyze_called is False
    assert _IncompleteLLMService.analyze_with_llm_hosted_called is True


def test_analyze_cli_use_llm_forced_progress_incomplete_keeps_fail_closed(
    monkeypatch,
) -> None:  # type: ignore[no-untyped-def]
    """验证 forced progress 不改变 incomplete fail-closed 语义。"""

    monkeypatch.setattr(cli, "_llm_progress_auto_enabled", lambda: False)
    monkeypatch.setattr(cli, "FundAnalysisService", _IncompleteLLMService)
    runner = CliRunner()

    result = runner.invoke(
        cli.app,
        ["analyze", "110011", "--use-llm", "--llm-progress"],
    )

    assert result.exit_code == 1
    assert result.stdout == ""
    assert "LLM progress: run_started" in result.stderr
    assert "LLM progress: run_terminal" in result.stderr
    assert "event=run_failed" in result.stderr
    assert "LLM 分析未完成：" in result.stderr
    assert "LLM Host run 未完成：" in result.stderr
    assert "# 0. 投资要点概览" not in result.output


def test_analyze_cli_use_llm_typed_incomplete_writes_artifact_path(
    monkeypatch,
    tmp_path: Path,
) -> None:  # type: ignore[no-untyped-def]
    """验证 typed incomplete LLM 结果会写 artifact 并保持 fail-closed 输出。

    Args:
        monkeypatch: pytest monkeypatch fixture。
        tmp_path: pytest 临时目录 fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 CLI 未调用 artifact writer 或改变 fail-closed 行为时抛出。
    """

    calls: list[tuple[object, str | None]] = []

    def fake_write(result, *, host_run_id):  # type: ignore[no-untyped-def]
        """记录 artifact writer 调用并返回安全 manifest 路径。

        Args:
            result: CLI 传入的 typed incomplete 结果。
            host_run_id: Host run id。

        Returns:
            fake artifact 写入结果。

        Raises:
            无显式抛出。
        """

        calls.append((result, host_run_id))
        return cli.LLMRunArtifactWriteResult(
            artifact_dir=tmp_path / "run",
            manifest_path=tmp_path / "run/manifest.json",
            summary_path=tmp_path / "run/summary.json",
            redaction_applied=False,
            written_files=(tmp_path / "run/manifest.json",),
        )

    monkeypatch.setattr(cli, "FundLLMAnalysisResult", _FakeLLMResult)
    monkeypatch.setattr(cli, "write_llm_incomplete_run_artifacts", fake_write)
    monkeypatch.setattr(cli, "FundAnalysisService", _IncompleteLLMService)
    runner = CliRunner()

    result = runner.invoke(cli.app, ["analyze", "110011", "--use-llm"])

    assert result.exit_code == 1
    assert result.stdout == ""
    assert "LLM incomplete diagnostic artifacts:" in result.stderr
    assert "manifest.json" in result.stderr
    assert "LLM 分析未完成：" in result.stderr
    assert "LLM Host run 未完成：" in result.stderr
    assert len(calls) == 1
    assert calls[0][1].startswith("host_run_")
    assert "# 0. 投资要点概览" not in result.output


def test_analyze_cli_incomplete_artifact_write_failure_preserves_fail_closed(
    monkeypatch,
) -> None:  # type: ignore[no-untyped-def]
    """验证 artifact 写入失败只输出安全 warning，原 incomplete 仍 fail-closed。

    Args:
        monkeypatch: pytest monkeypatch fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当写入失败污染 stdout 或隐藏 incomplete 摘要时抛出。
    """

    def raise_write_failure(result, *, host_run_id):  # type: ignore[no-untyped-def]
        """模拟 artifact 写入失败。

        Args:
            result: CLI 传入的 typed incomplete 结果。
            host_run_id: Host run id。

        Returns:
            无返回值。

        Raises:
            OSError: 始终抛出。
        """

        raise OSError("secret path /tmp/sk-secret")

    monkeypatch.setattr(cli, "FundLLMAnalysisResult", _FakeLLMResult)
    monkeypatch.setattr(cli, "write_llm_incomplete_run_artifacts", raise_write_failure)
    monkeypatch.setattr(cli, "FundAnalysisService", _IncompleteLLMService)
    runner = CliRunner()

    result = runner.invoke(cli.app, ["analyze", "110011", "--use-llm"])

    assert result.exit_code == 1
    assert result.stdout == ""
    assert "LLM incomplete diagnostic artifact warning: write_failed type=OSError" in result.stderr
    assert "secret path" not in result.stderr
    assert "sk-secret" not in result.stderr
    assert "LLM 分析未完成：" in result.stderr
    assert "LLM Host run 未完成：" in result.stderr
    assert "# 0. 投资要点概览" not in result.output


def test_analyze_cli_use_llm_incomplete_prints_safe_all_chapter_matrix(
    monkeypatch,
) -> None:  # type: ignore[no-untyped-def]
    """验证 incomplete stderr 同时包含 first_failed 和安全全章节矩阵。"""

    _MatrixIncompleteLLMService.last_request = None
    _MatrixIncompleteLLMService.analyze_called = False
    _MatrixIncompleteLLMService.analyze_with_llm_hosted_called = False
    monkeypatch.setattr(cli, "FundAnalysisService", _MatrixIncompleteLLMService)
    runner = CliRunner()

    result = runner.invoke(cli.app, ["analyze", "110011", "--use-llm"])

    assert result.exit_code == 1
    assert result.stdout == ""
    assert "LLM Host run 未完成：" in result.stderr
    assert "first_failed_chapter_id=1" in result.stderr
    assert "first_failed_status=failed" in result.stderr
    assert "first_failed_stop_reason=llm_timeout" in result.stderr
    assert "chapter_matrix=" in result.stderr
    assert "1:failed/llm_timeout/llm_timeout/unknown" in result.stderr
    assert "2:accepted/none/unknown/unknown" in result.stderr
    assert "3:blocked/missing_required_output_marker/prompt_contract/missing_required_marker" in result.stderr
    assert "2:skipped/dependency_missing" not in result.stderr
    assert "3:skipped/dependency_missing" not in result.stderr
    for forbidden in (
        "message",
        "Authorization",
        "Bearer",
        "sk-",
        "api_key",
        "system_prompt",
        "user_prompt",
        "draft_markdown",
        "raw_response",
        "raw audit",
        "provider_response",
        "provider body",
        "model_name",
        "header",
        "key",
    ):
        assert forbidden not in result.stderr
    assert "# 0. 投资要点概览" not in result.output
    assert _MatrixIncompleteLLMService.analyze_called is False
    assert _MatrixIncompleteLLMService.analyze_with_llm_hosted_called is True


def test_analyze_cli_use_llm_l1_subcategory_matches_service_summary(
    monkeypatch,
) -> None:  # type: ignore[no-untyped-def]
    """验证 CLI 直接透出 Service L1 子类且不回退 deterministic。

    Args:
        monkeypatch: pytest monkeypatch fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 CLI 丢失 L1 子类或输出报告时抛出。
    """

    _L1IncompleteLLMService.last_request = None
    _L1IncompleteLLMService.analyze_called = False
    _L1IncompleteLLMService.analyze_with_llm_hosted_called = False
    monkeypatch.setattr(cli, "FundAnalysisService", _L1IncompleteLLMService)
    runner = CliRunner()

    result = runner.invoke(cli.app, ["analyze", "110011", "--use-llm"])

    assert result.exit_code == 1
    assert result.stdout == ""
    assert "LLM Host run 未完成：" in result.stderr
    assert "first_failed_chapter_id=2" in result.stderr
    assert "first_failed_status=failed" in result.stderr
    assert "first_failed_stop_reason=repair_budget_exhausted" in result.stderr
    assert "first_failed_category=prompt_contract" in result.stderr
    assert "first_failed_subcategory=l1_numerical_closure" in result.stderr
    assert "chapter_matrix=2:failed/repair_budget_exhausted/prompt_contract/l1_numerical_closure" in result.stderr
    assert "first_failed_subcategory=unknown" not in result.stderr
    assert "first_failed_category=audit_rule_too_strict" not in result.stderr
    assert "# 0. 投资要点概览" not in result.output
    assert _L1IncompleteLLMService.analyze_called is False
    assert _L1IncompleteLLMService.analyze_with_llm_hosted_called is True


def test_analyze_cli_use_llm_timeout_fail_closed_without_fallback(
    monkeypatch,
) -> None:  # type: ignore[no-untyped-def]
    """验证 `--use-llm` timeout 分类 fail-closed 且不回退 deterministic。

    Args:
        monkeypatch: pytest monkeypatch fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 timeout 被吞掉或输出 deterministic 报告时抛出。
    """

    _TimeoutLLMService.last_request = None
    _TimeoutLLMService.analyze_called = False
    _TimeoutLLMService.analyze_with_llm_hosted_called = False
    monkeypatch.setattr(cli, "FundAnalysisService", _TimeoutLLMService)
    runner = CliRunner()

    result = runner.invoke(cli.app, ["analyze", "110011", "--use-llm"])

    assert result.exit_code == 1
    assert result.stdout == ""
    assert "LLM 分析未完成：" in result.stderr
    assert "LLM Host run 未完成：" in result.stderr
    assert "llm_timeout" in result.stderr
    assert "first_failed_chapter_id=2" in result.stderr
    assert "first_failed_status=failed" in result.stderr
    assert "first_failed_stop_reason=llm_timeout" in result.stderr
    assert "first_failed_category=llm_timeout" in result.stderr
    assert "first_failed_subcategory=unknown" in result.stderr
    assert "first_failed_runtime_operation=writer" in result.stderr
    assert "first_failed_provider_attempts=2/2" in result.stderr
    assert "first_failed_provider_runtime_category=timeout" in result.stderr
    assert "first_failed_elapsed_ms_max=121000" in result.stderr
    assert "first_failed_prompt_chars=400" in result.stderr
    assert "first_failed_approx_prompt_tokens=100" in result.stderr
    assert "first_failed_timeout_root_cause_hint=small_prompt_provider_timeout" in result.stderr
    assert "first_failed_max_output_chars=12000" in result.stderr
    assert "chapter_matrix=2:failed/llm_timeout/llm_timeout/unknown" in result.stderr
    assert "message" not in result.stderr
    assert "writer" in result.stderr
    assert "Authorization" not in result.stderr
    assert "Bearer" not in result.stderr
    assert "sk-" not in result.stderr
    assert "api_key" not in result.stderr
    assert "header" not in result.stderr
    assert "key" not in result.stderr
    assert "auditor" not in result.stderr
    assert "programmatic" not in result.stderr
    assert "raw audit" not in result.stderr
    assert "system_prompt" not in result.stderr
    assert "user_prompt" not in result.stderr
    assert "draft_markdown" not in result.stderr
    assert "raw_response" not in result.stderr
    assert "provider_response" not in result.stderr
    assert "provider body" not in result.stderr
    assert "model_name" not in result.stderr
    assert "# 0. 投资要点概览" not in result.output
    assert _TimeoutLLMService.analyze_called is False
    assert _TimeoutLLMService.analyze_with_llm_hosted_called is True


def test_analyze_cli_use_llm_forced_progress_timeout_is_safe(
    monkeypatch,
) -> None:  # type: ignore[no-untyped-def]
    """验证 timeout incomplete 下 progress 仍只输出安全 allowlist 字段。"""

    monkeypatch.setattr(cli, "_llm_progress_auto_enabled", lambda: False)
    monkeypatch.setattr(cli, "FundAnalysisService", _TimeoutLLMService)
    runner = CliRunner()

    result = runner.invoke(
        cli.app,
        ["analyze", "110011", "--use-llm", "--llm-progress"],
    )

    assert result.exit_code == 1
    assert result.stdout == ""
    assert "LLM progress: phase_started phase=writer" in result.stderr
    assert "LLM progress: run_terminal" in result.stderr
    assert "first_failed_provider_runtime_category=timeout" in result.stderr
    progress_stderr = "\n".join(
        line for line in result.stderr.splitlines() if line.startswith("LLM progress:")
    )
    for forbidden in (
        "Authorization",
        "Bearer",
        "sk-",
        "api_key",
        "cookie",
        "secret_key",
        "access_key",
        "system_prompt",
        "user_prompt",
        "prompt",
        "draft_markdown",
        "raw_response",
        "provider_response",
        "provider body",
        "raw audit",
        "model_name",
        "header",
    ):
        assert forbidden not in progress_stderr
    assert "# 0. 投资要点概览" not in result.output


def test_analyze_cli_use_llm_host_failure_is_not_double_wrapped(
    monkeypatch,
) -> None:  # type: ignore[no-untyped-def]
    """验证 Host run 失败摘要不会再被通用分析失败分支包一层。"""

    monkeypatch.setattr(cli, "FundAnalysisService", _FailingLLMService)
    runner = CliRunner()

    result = runner.invoke(cli.app, ["analyze", "110011", "--use-llm"])

    assert result.exit_code == 1
    assert result.stdout == ""
    assert "LLM Host run 未完成：" in result.stderr
    assert "status=failed" in result.stderr
    assert "error_type=RuntimeError" in result.stderr
    assert "分析失败：" not in result.stderr
    assert "llm fixture failure" not in result.stderr


def test_analyze_cli_use_llm_host_terminal_failure_does_not_fake_success(
    monkeypatch,
) -> None:  # type: ignore[no-untyped-def]
    """验证 Host failed 终态不会被 CLI 当作成功报告输出。

    Args:
        monkeypatch: pytest monkeypatch fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 Host failed 被吞掉或伪造成成功时抛出。
    """

    _FailingLLMService.analyze_called = False
    _FailingLLMService.analyze_with_llm_hosted_called = False
    monkeypatch.setattr(cli, "FundAnalysisService", _FailingLLMService)
    runner = CliRunner()

    result = runner.invoke(cli.app, ["analyze", "110011", "--use-llm"])

    assert result.exit_code == 1
    assert result.stdout == ""
    assert "LLM Host run 未完成：" in result.stderr
    assert "status=failed" in result.stderr
    assert "error_type=RuntimeError" in result.stderr
    assert "status=succeeded" not in result.stderr
    assert "# LLM report" not in result.output
    assert "# 0. 投资要点概览" not in result.output


def test_cli_use_llm_boundary_delegates_to_service_hosted_use_case() -> None:
    """验证 CLI `--use-llm` 边界只委托 Service hosted 用例。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 CLI 仍保留 Host invocation 或 request builder 责任时抛出。
    """

    cli_source = Path(cli.__file__).read_text(encoding="utf-8")
    forbidden_terms = (
        "Host" + "RuntimeRunner",
        "Host" + "RunResult",
        "Host" + "RunStatus",
        "Host" + "RunEvent",
        "build_fund_llm_" + "execution_request",
        "extra_payload",
    )

    assert "FundAnalysisService().analyze_with_llm_hosted(" in cli_source
    for term in forbidden_terms:
        assert term not in cli_source


def test_cli_module_imports_service_but_not_agent_internals() -> None:
    """验证 UI 只依赖 Service，不直接导入 Agent 内部模块。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 CLI 直接导入 Agent 内部模块时抛出。
    """

    cli_source = Path(cli.__file__).read_text(encoding="utf-8")
    forbidden_agent_import = "fund_agent." + "fund."
    forbidden_application_import = "fund_agent." + "application"

    assert "fund_agent.services" in cli_source
    assert forbidden_agent_import not in cli_source
    assert forbidden_application_import not in cli_source


def test_cli_module_has_no_evidence_confirm_runner_imports() -> None:
    """验证 CLI 未导入 Evidence Confirm runner 或 Fund 文档内部实现。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 CLI import 越过 UI/Service 边界时抛出。
    """

    cli_source = Path(cli.__file__).read_text(encoding="utf-8")
    import_lines = "\n".join(
        line
        for line in cli_source.splitlines()
        if line.startswith("import ") or line.startswith("from ")
    )
    forbidden_import_terms = (
        "FundDocumentRepository",
        "download_annual_report",
        "annual_report_source",
        "evidence_confirm_sources",
        "evidence_confirm_production",
        "run_repository_bounded_evidence_confirm",
        "Docling",
        "docling",
        "pdfplumber",
    )

    for term in forbidden_import_terms:
        assert term not in import_lines


def test_cli_module_llm_boundary_has_no_forbidden_runtime_imports() -> None:
    """验证 CLI `--use-llm` 入口未引入 provider SDK、dayu 或间接业务参数。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 CLI 越过当前 Slice 4C 边界时抛出。
    """

    cli_source = Path(cli.__file__).read_text(encoding="utf-8")
    forbidden_terms = (
        "dayu",
        "extra_payload",
        "openai",
        "anthropic",
        "httpx",
        "provider_sdk",
        "pdf_cache",
        "download_annual_report",
        "annual_report_source",
    )

    for term in forbidden_terms:
        assert term not in cli_source


def test_analyze_cli_prints_quality_gate_summary_to_stderr(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """验证 analyze 成功时 quality gate 摘要写入 stderr。

    Args:
        monkeypatch: pytest monkeypatch fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 stdout 被 gate 摘要污染或 stderr 缺少摘要时抛出。
    """

    monkeypatch.setattr(cli, "FundAnalysisService", _FakeWarnService)
    runner = CliRunner()

    result = runner.invoke(
        cli.app,
        ["analyze", "110011", "--dev-override", "--quality-gate-policy", "warn"],
    )

    assert result.exit_code == 0
    assert result.output.endswith("# 0. 投资要点概览\n")
    assert "quality_gate_status: warn" in result.output
    assert "quality_gate_json: quality-output/quality_gate.json" in result.output


def test_analyze_cli_prints_quality_gate_info_for_missing_golden_coverage(
    monkeypatch,
) -> None:  # type: ignore[no-untyped-def]
    """验证 fund-scoped FQ0/info 会输出 concise quality_gate_info 行。

    Args:
        monkeypatch: pytest monkeypatch fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 info 行缺失或 exit code 被改变时抛出。
    """

    monkeypatch.setattr(cli, "FundAnalysisService", _FakeInfoService)
    runner = CliRunner()

    result = runner.invoke(cli.app, ["analyze", "000216"])

    assert result.exit_code == 0
    assert result.output.endswith("# 0. 投资要点概览\n")
    assert "quality_gate_status: pass" in result.output
    assert (
        "quality_gate_info: strict golden answer not covered for fund_code 000216 "
        "reason=fund_not_covered"
    ) in result.output


def test_analyze_cli_default_product_prints_evidence_confirm_warn_summary(
    monkeypatch,
) -> None:  # type: ignore[no-untyped-def]
    """验证默认 product analyze 输出 Evidence Confirm warn 安全摘要。

    Args:
        monkeypatch: pytest monkeypatch fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 默认 product 摘要缺失或泄漏非安全字段时抛出。
    """

    _FakeProductEvidenceConfirmWarnService.last_request = None
    monkeypatch.setattr(cli, "FundAnalysisService", _FakeProductEvidenceConfirmWarnService)
    runner = CliRunner()

    result = runner.invoke(cli.app, ["analyze", "110011"])

    assert result.exit_code == 0
    assert result.output.endswith("# report body\n")
    assert "evidence_confirm_status: warn" in result.output
    assert "evidence_confirm_policy: warn" in result.output
    assert "evidence_confirm_checked_facts: 8" in result.output
    assert "evidence_confirm_failed_facts: 1" in result.output
    assert "evidence_confirm_auditability_score: 87" in result.output
    assert "secret excerpt" not in result.output
    assert "source.pdf" not in result.output
    assert "parser json" not in result.output
    assert "provider body" not in result.output
    assert _FakeProductEvidenceConfirmWarnService.last_request is not None
    assert _FakeProductEvidenceConfirmWarnService.last_request.mode == "product"
    assert _FakeProductEvidenceConfirmWarnService.last_request.developer_overrides is None


def test_analyze_cli_dev_override_evidence_confirm_warn_passes_policy_and_prints_summary(
    monkeypatch,
) -> None:  # type: ignore[no-untyped-def]
    """验证 analyze 开发覆盖 Evidence Confirm warn 策略透传并输出 safe summary。

    Args:
        monkeypatch: pytest monkeypatch fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 策略未透传或摘要输出不符合契约时抛出。
    """

    _FakeEvidenceConfirmWarnService.last_request = None
    monkeypatch.setattr(cli, "FundAnalysisService", _FakeEvidenceConfirmWarnService)
    runner = CliRunner()

    result = runner.invoke(
        cli.app,
        ["analyze", "110011", "--dev-override", "--evidence-confirm-policy", "warn"],
    )

    assert result.exit_code == 0
    assert result.output.endswith("# report body\n")
    assert "evidence_confirm_status: warn" in result.output
    assert "evidence_confirm_policy: warn" in result.output
    assert "evidence_confirm_checked_facts: 8" in result.output
    assert "evidence_confirm_failed_facts: 1" in result.output
    assert "evidence_confirm_auditability_score: none" in result.output
    assert "excerpt" not in result.output.lower()
    assert "pdf" not in result.output.lower()
    assert _FakeEvidenceConfirmWarnService.last_request is not None
    assert _FakeEvidenceConfirmWarnService.last_request.mode == "developer_override"
    assert (
        _FakeEvidenceConfirmWarnService.last_request.developer_overrides.evidence_confirm_policy
        == "warn"
    )


def test_analyze_cli_default_product_request(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """验证 analyze 默认构造 product mode 最小请求。

    Args:
        monkeypatch: pytest monkeypatch fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 CLI 默认请求携带开发覆盖时抛出。
    """

    _FakeService.last_request = None
    _FakeService.analyze_called = False
    _FakeService.analyze_with_llm_hosted_called = False
    monkeypatch.setattr(cli, "FundAnalysisService", _FakeService)
    monkeypatch.setattr(
        cli,
        "write_llm_incomplete_run_artifacts",
        _forbid_llm_artifact_writer,
    )
    runner = CliRunner()

    result = runner.invoke(cli.app, ["analyze", "110011"])

    assert result.exit_code == 0
    assert _FakeService.analyze_called is True
    assert _FakeService.analyze_with_llm_hosted_called is False
    assert _FakeService.last_request is not None
    assert _FakeService.last_request.mode == "product"
    assert _FakeService.last_request.developer_overrides is None
    assert _FakeService.last_request.valuation_state is None


def test_default_analyze_unchanged_with_typed_contract_modules_present(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """验证默认 analyze 不读取 LLM config 或 typed LLM provider config。

    Args:
        monkeypatch: pytest monkeypatch fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当默认 analyze 触发 LLM builder、provider config、Host 或 artifact 写入时抛出。
    """

    _FakeService.last_request = None
    _FakeService.analyze_called = False
    _FakeService.analyze_with_llm_hosted_called = False
    monkeypatch.setattr(cli, "FundAnalysisService", _FakeService)
    monkeypatch.setattr(
        cli,
        "write_llm_incomplete_run_artifacts",
        _forbid_llm_artifact_writer,
    )
    runner = CliRunner()

    result = runner.invoke(cli.app, ["analyze", "110011", "--report-year", "2024"])

    assert result.exit_code == 0
    assert result.stdout == "# 0. 投资要点概览\n\n# 7. 是否值得持有——最终判断\n"
    assert _FakeService.analyze_called is True
    assert _FakeService.analyze_with_llm_hosted_called is False
    assert _FakeService.last_request.command_source == "analyze"


def test_analyze_cli_rejects_dev_options_without_dev_override(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """验证开发参数未配 `--dev-override` 会统一失败。

    Args:
        monkeypatch: pytest monkeypatch fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当开发参数静默生效时抛出。
    """

    _FakeService.last_request = None
    monkeypatch.setattr(cli, "FundAnalysisService", _FakeService)
    runner = CliRunner()

    result = runner.invoke(cli.app, ["analyze", "110011", "--equity-position", "80%"])

    assert result.exit_code != 0
    assert "--dev-override" in result.output
    assert "--equity-position" in result.output
    assert _FakeService.last_request is None


def test_analyze_cli_rejects_quality_gate_policy_without_dev_override(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """验证 quality gate warn/off 只允许开发覆盖模式。

    Args:
        monkeypatch: pytest monkeypatch fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 product mode 可关闭 gate 时抛出。
    """

    _FakeService.last_request = None
    monkeypatch.setattr(cli, "FundAnalysisService", _FakeService)
    runner = CliRunner()

    result = runner.invoke(cli.app, ["analyze", "110011", "--quality-gate-policy", "off"])

    assert result.exit_code != 0
    assert "--dev-override" in result.output
    assert "--quality-gate-policy" in result.output
    assert _FakeService.last_request is None


def test_analyze_cli_rejects_evidence_confirm_policy_without_dev_override(
    monkeypatch,
) -> None:  # type: ignore[no-untyped-def]
    """验证 Evidence Confirm warn/block 只允许开发覆盖模式。

    Args:
        monkeypatch: pytest monkeypatch fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 product mode 可启用 Evidence Confirm 时抛出。
    """

    _FakeService.last_request = None
    monkeypatch.setattr(cli, "FundAnalysisService", _FakeService)
    runner = CliRunner()

    result = runner.invoke(
        cli.app,
        ["analyze", "110011", "--evidence-confirm-policy", "warn"],
    )

    assert result.exit_code != 0
    assert "--dev-override" in result.output
    assert "--evidence-confirm-policy" in result.output
    assert _FakeService.last_request is None


def test_analyze_cli_structured_quality_gate_block(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """验证 analyze 被 quality gate 阻断时输出结构化 stderr 且 stdout 为空。

    Args:
        monkeypatch: pytest monkeypatch fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当阻断输出不符合契约时抛出。
    """

    monkeypatch.setattr(cli, "FundAnalysisService", _FakeBlockedAnalysisService)
    runner = CliRunner()

    result = runner.invoke(cli.app, ["analyze", "110011"])

    assert result.exit_code == 2
    assert "# 0. 投资要点概览" not in result.output
    assert "质量 gate 阻断报告输出" in result.output
    assert "quality_gate_status: block" in result.output
    assert "quality_gate_issues: 2" in result.output
    assert "quality_gate_json: quality-output/quality_gate.json" in result.output


def test_analyze_cli_evidence_confirm_block_exits_2_without_report_body(
    monkeypatch,
) -> None:  # type: ignore[no-untyped-def]
    """验证 Evidence Confirm block 阻断时退出 2 且不输出报告正文。

    Args:
        monkeypatch: pytest monkeypatch fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 阻断输出或退出码不符合契约时抛出。
    """

    _FakeEvidenceConfirmBlockedAnalysisService.last_request = None
    monkeypatch.setattr(cli, "FundAnalysisService", _FakeEvidenceConfirmBlockedAnalysisService)
    runner = CliRunner()

    result = runner.invoke(
        cli.app,
        ["analyze", "110011", "--dev-override", "--evidence-confirm-policy", "block"],
    )

    assert result.exit_code == 2
    assert "# report body" not in result.output
    assert "Evidence Confirm 阻断报告输出" in result.output
    assert "evidence_confirm_status: fail" in result.output
    assert "evidence_confirm_policy: block" in result.output
    assert "evidence_confirm_checked_facts: 8" in result.output
    assert "evidence_confirm_failed_facts: 2" in result.output
    assert "evidence_confirm_auditability_score: 41" in result.output
    assert _FakeEvidenceConfirmBlockedAnalysisService.last_request is not None
    assert (
        _FakeEvidenceConfirmBlockedAnalysisService.last_request.developer_overrides.evidence_confirm_policy
        == "block"
    )


def test_analyze_cli_use_llm_structured_quality_gate_block(
    monkeypatch,
) -> None:  # type: ignore[no-untyped-def]
    """验证 LLM path 的 quality gate 阻断仍返回退出码 2。

    Args:
        monkeypatch: pytest monkeypatch fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 LLM path 未保持 quality gate 阻断语义时抛出。
    """

    monkeypatch.setattr(cli, "FundAnalysisService", _FakeLLMBlockedAnalysisService)
    runner = CliRunner()

    result = runner.invoke(cli.app, ["analyze", "110011", "--use-llm"])

    assert result.exit_code == 2
    assert result.stdout == ""
    assert "质量 gate 阻断报告输出" in result.stderr
    assert "quality_gate_status: block" in result.stderr
    assert "quality_gate_issues: 2" in result.stderr
    assert "LLM Host run 未完成" not in result.stderr
    assert "status=succeeded" not in result.stderr


def test_analyze_cli_use_llm_progress_quality_gate_block_preserves_error(
    monkeypatch,
) -> None:  # type: ignore[no-untyped-def]
    """验证 progress 启用时 LLM quality gate block 仍走既有错误路径。

    Args:
        monkeypatch: pytest monkeypatch fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 progress 破坏 quality gate block 退出语义时抛出。
    """

    monkeypatch.setattr(cli, "_llm_progress_auto_enabled", lambda: False)
    monkeypatch.setattr(cli, "FundAnalysisService", _FakeLLMBlockedAnalysisService)
    runner = CliRunner()

    result = runner.invoke(
        cli.app,
        ["analyze", "110011", "--use-llm", "--llm-progress"],
    )

    assert result.exit_code == 2
    assert result.stdout == ""
    assert "质量 gate 阻断报告输出" in result.stderr
    assert "quality_gate_status: block" in result.stderr
    assert "quality_gate_issues: 2" in result.stderr
    assert "LLM progress: run_started" in result.stderr
    assert "LLM progress: run_terminal" not in result.stderr
    assert "UnboundLocalError" not in result.stderr
    assert "host_result" not in result.stderr
    assert "分析失败：" not in result.stderr
    assert "LLM Host run 未完成" not in result.stderr


def test_analyze_cli_structured_quality_gate_not_run_block(
    monkeypatch,
) -> None:  # type: ignore[no-untyped-def]
    """验证 block 策略下 quality gate 未运行时返回结构化退出码。

    Args:
        monkeypatch: pytest monkeypatch fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 not-run 阻断输出不符合契约时抛出。
    """

    monkeypatch.setattr(cli, "FundAnalysisService", _FakeNotRunBlockedAnalysisService)
    runner = CliRunner()

    result = runner.invoke(cli.app, ["analyze", "110011"])

    assert result.exit_code == 2
    assert "# 0. 投资要点概览" not in result.output
    assert "质量 gate 阻断报告输出" in result.output
    assert "quality_gate_status: not_run" in result.output
    assert "quality_gate_not_run_reason: fund_code `110011` not found" in result.output


def test_analyze_cli_use_llm_structured_quality_gate_not_run_block(
    monkeypatch,
) -> None:  # type: ignore[no-untyped-def]
    """验证 LLM path 的 quality gate 未运行阻断仍返回退出码 2。

    Args:
        monkeypatch: pytest monkeypatch fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 LLM path 未保持 not-run 阻断语义时抛出。
    """

    monkeypatch.setattr(cli, "FundAnalysisService", _FakeLLMNotRunBlockedAnalysisService)
    runner = CliRunner()

    result = runner.invoke(cli.app, ["analyze", "110011", "--use-llm"])

    assert result.exit_code == 2
    assert result.stdout == ""
    assert "质量 gate 阻断报告输出" in result.stderr
    assert "quality_gate_status: not_run" in result.stderr
    assert "quality_gate_not_run_reason: fund_code `110011` not found" in result.stderr
    assert "LLM Host run 未完成" not in result.stderr
    assert "status=succeeded" not in result.stderr


def test_analyze_cli_use_llm_progress_quality_gate_not_run_preserves_error(
    monkeypatch,
) -> None:  # type: ignore[no-untyped-def]
    """验证 progress 启用时 LLM quality gate not-run 仍走既有错误路径。

    Args:
        monkeypatch: pytest monkeypatch fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 progress 破坏 quality gate not-run 退出语义时抛出。
    """

    monkeypatch.setattr(cli, "_llm_progress_auto_enabled", lambda: False)
    monkeypatch.setattr(cli, "FundAnalysisService", _FakeLLMNotRunBlockedAnalysisService)
    runner = CliRunner()

    result = runner.invoke(
        cli.app,
        ["analyze", "110011", "--use-llm", "--llm-progress"],
    )

    assert result.exit_code == 2
    assert result.stdout == ""
    assert "质量 gate 阻断报告输出" in result.stderr
    assert "quality_gate_status: not_run" in result.stderr
    assert "quality_gate_not_run_reason: fund_code `110011` not found" in result.stderr
    assert "LLM progress: run_started" in result.stderr
    assert "LLM progress: run_terminal" not in result.stderr
    assert "UnboundLocalError" not in result.stderr
    assert "host_result" not in result.stderr
    assert "分析失败：" not in result.stderr
    assert "LLM Host run 未完成" not in result.stderr


def test_analyze_cli_exits_nonzero_with_clear_message(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """验证 analyze 失败时非零退出并输出清晰错误。

    Args:
        monkeypatch: pytest monkeypatch fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 CLI 失败路径不符合契约时抛出。
    """

    monkeypatch.setattr(cli, "FundAnalysisService", _FailingService)
    runner = CliRunner()

    result = runner.invoke(cli.app, ["analyze", "110011"])

    assert result.exit_code == 1
    assert "分析失败：fixture failure" in result.output


def test_analyze_cli_explicit_unavailable_is_forwarded(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """验证显式 unavailable 作为手动灰灯转发给 Service。

    Args:
        monkeypatch: pytest monkeypatch fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: unavailable 未显式转发时抛出。
    """

    _FakeService.last_request = None
    monkeypatch.setattr(cli, "FundAnalysisService", _FakeService)
    runner = CliRunner()

    result = runner.invoke(cli.app, ["analyze", "110011", "--valuation-state", "unavailable"])

    assert result.exit_code == 0
    assert _FakeService.last_request is not None
    assert _FakeService.last_request.valuation_state == "unavailable"


def test_analyze_cli_help_documents_auto_valuation_and_opt_out() -> None:
    """验证 analyze help 说明缺省自动估值和 unavailable opt-out。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: help 文案缺少 P19-S3 契约时抛出。
    """

    runner = CliRunner()

    result = runner.invoke(cli.app, ["analyze", "--help"], env={"COLUMNS": "120"})

    assert result.exit_code == 0
    assert "缺省时允许自动温度计估值" in result.output
    assert "unavailable" in result.output
    assert "则手动灰灯且不调用温度计" in result.output

    analyze_command = get_command(cli.app).commands["analyze"]
    option_names = {
        option_name
        for parameter in analyze_command.params
        for option_name in getattr(parameter, "opts", ())
    }
    assert "--thermometer-cache-dir" in option_names
    assert "--use-llm" in option_names
    assert "--evidence-confirm-policy" in option_names
    assert "--no-evidence-confirm" not in option_names
    assert "--evidence-confirm" not in option_names

    evidence_confirm_help = next(
        parameter.help
        for parameter in analyze_command.params
        if "--evidence-confirm-policy" in getattr(parameter, "opts", ())
    )
    assert evidence_confirm_help == (
        "开发覆盖：Evidence Confirm 策略 off/warn/block；仅在 --dev-override 下生效"
    )
    assert "Evidence Confirm 策略 off/warn/block；opt-in" not in result.output


def test_thermometer_cli_help_documents_all_a_and_self_owned_history() -> None:
    """验证 thermometer help 说明全 A 代码和自有历史数据刷新语义。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: help 文案缺少 P19-S5 契约时抛出。
    """

    runner = CliRunner()

    result = runner.invoke(cli.app, ["thermometer", "--help"], env={"COLUMNS": "120"})

    assert result.exit_code == 0
    assert "wind_all_a" in result.output
    assert "000300" in result.output
    assert "000905" in result.output
    assert "自有温度计历史数据" in result.output


def test_analyze_cli_invalid_valuation_exits_2(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """验证非法估值状态返回参数错误。

    Args:
        monkeypatch: pytest monkeypatch fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 非法估值状态未被拒绝时抛出。
    """

    _FakeService.last_request = None
    monkeypatch.setattr(cli, "FundAnalysisService", _FakeService)
    runner = CliRunner()

    result = runner.invoke(cli.app, ["analyze", "110011", "--valuation-state", "cold"])

    assert result.exit_code == 2
    assert "valuation_state 必须是" in result.output
    assert _FakeService.last_request is None


def test_checklist_cli_calls_service_and_prints_summary(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """验证 checklist 命令接入 Service 并输出真实摘要。

    Args:
        monkeypatch: pytest monkeypatch fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: CLI 未调用 Service 或摘要缺少核心字段时抛出。
    """

    _FakeChecklistService.last_request = None
    _FakeChecklistService.checklist_called = False
    monkeypatch.setattr(cli, "FundAnalysisService", _FakeChecklistService)
    monkeypatch.setattr(
        cli,
        "write_llm_incomplete_run_artifacts",
        _forbid_llm_artifact_writer,
    )
    runner = CliRunner()

    result = runner.invoke(
        cli.app,
        [
            "checklist",
            "110011",
            "--valuation-state",
            "low",
            "--user-money-horizon-years",
            "4",
        ],
    )

    assert result.exit_code == 0
    assert _FakeChecklistService.checklist_called is True
    assert _FakeChecklistService.last_request is not None
    assert _FakeChecklistService.last_request.fund_code == "110011"
    assert _FakeChecklistService.last_request.valuation_state == "low"
    assert _FakeChecklistService.last_request.user_money_horizon_years == "4"
    assert _FakeChecklistService.last_request.command_source == "checklist"
    assert "overall_signal: green" in result.output
    assert "valuation_state: low" in result.output
    assert "final_judgment: worth_holding" in result.output
    assert "- valuation: green/pass" in result.output


def test_checklist_cli_rejects_use_llm_option(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """验证 checklist 不接受 `--use-llm`，且不会调用 Service。

    Args:
        monkeypatch: pytest monkeypatch fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 checklist 接受 LLM 选项或调用 Service 时抛出。
    """

    _FakeChecklistService.last_request = None
    _FakeChecklistService.checklist_called = False
    monkeypatch.setattr(cli, "FundAnalysisService", _FakeChecklistService)
    runner = CliRunner()

    result = runner.invoke(cli.app, ["checklist", "110011", "--use-llm"])

    assert result.exit_code != 0
    assert _FakeChecklistService.last_request is None
    assert _FakeChecklistService.checklist_called is False

    checklist_command = get_command(cli.app).commands["checklist"]
    option_names = {
        option_name
        for parameter in checklist_command.params
        for option_name in getattr(parameter, "opts", ())
    }
    assert "--use-llm" not in option_names
    assert "--evidence-confirm-policy" not in option_names


def test_checklist_cli_help_does_not_expose_evidence_confirm_policy() -> None:
    """验证 checklist help 不暴露 Evidence Confirm CLI 参数。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: checklist help 暴露 analyze-only flag 时抛出。
    """

    runner = CliRunner()

    result = runner.invoke(cli.app, ["checklist", "--help"], env={"COLUMNS": "120"})

    assert result.exit_code == 0
    assert "--evidence-confirm-policy" not in result.output
    assert "--no-evidence-confirm" not in result.output
    assert "--evidence-confirm" not in result.output


def test_thermometer_cli_prints_plain_summary(monkeypatch, tmp_path) -> None:  # type: ignore[no-untyped-def]
    """验证 thermometer 命令默认输出全 A plain text 摘要并转发显式参数。

    Args:
        monkeypatch: pytest monkeypatch fixture。
        tmp_path: pytest 临时目录 fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当全 A 输出或参数转发不符合契约时抛出。
    """

    _FakeThermometerService.last_request = None
    _FakeThermometerService.snapshot = _available_all_a_thermometer_reading()
    monkeypatch.setattr(cli, "ThermometerService", _FakeThermometerService)
    runner = CliRunner()

    result = runner.invoke(
        cli.app,
        ["thermometer", "--cache-dir", str(tmp_path), "--force-refresh"],
    )

    assert result.exit_code == 0
    assert "index_code: wind_all_a" in result.output
    assert "index_name: 万得全 A / 全 A 市场" in result.output
    assert "source: akshare_legulegu_all_a_pe_pb" in result.output
    assert "unavailable: false" in result.output
    assert "temperature: 35.25" in result.output
    assert "pe_percentile: 30.00" in result.output
    assert "pb_percentile: 40.50" in result.output
    assert "valuation_state_candidate: fair" in result.output
    assert "disclaimer: 本温度计基于有知有行公开方法论独立计算，非有知有行官方数据。" in result.output
    assert _FakeThermometerService.last_request is not None
    assert _FakeThermometerService.last_request.cache_dir == tmp_path
    assert _FakeThermometerService.last_request.force_refresh is True
    assert _FakeThermometerService.last_request.index_code is None
    assert _FakeThermometerService.last_request.index_codes is None


def test_thermometer_cli_no_arg_json_delegates_default_to_service(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """验证 thermometer 无参数 JSON 输出全 A 读数且默认路由归 Service 所有。

    Args:
        monkeypatch: pytest monkeypatch fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 JSON 输出或默认请求不符合契约时抛出。
    """

    _FakeThermometerService.last_request = None
    _FakeThermometerService.snapshot = _available_all_a_thermometer_reading()
    monkeypatch.setattr(cli, "ThermometerService", _FakeThermometerService)
    runner = CliRunner()

    result = runner.invoke(cli.app, ["thermometer", "--json"])

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["index_code"] == "wind_all_a"
    assert payload["index_name"] == "万得全 A / 全 A 市场"
    assert payload["temperature"] == "35.25"
    assert payload["pe_percentile"] == "30.00"
    assert payload["pb_percentile"] == "40.50"
    assert payload["valuation_state_candidate"] == "fair"
    assert "非有知有行官方数据" in payload["disclaimer"]
    assert _FakeThermometerService.last_request is not None
    assert _FakeThermometerService.last_request.index_code is None
    assert _FakeThermometerService.last_request.index_codes is None


def test_thermometer_cli_prints_json_for_unavailable_all_a_reading(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """验证 thermometer JSON 输出覆盖全 A unavailable 数据态且退出 0。

    Args:
        monkeypatch: pytest monkeypatch fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 JSON 输出或退出码不符合契约时抛出。
    """

    _FakeThermometerService.last_request = None
    _FakeThermometerService.snapshot = _unavailable_all_a_thermometer_reading()
    monkeypatch.setattr(cli, "ThermometerService", _FakeThermometerService)
    runner = CliRunner()

    result = runner.invoke(cli.app, ["thermometer", "--json"])

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["index_code"] == "wind_all_a"
    assert payload["unavailable"] is True
    assert payload["unavailable_reason"] == "network down"
    assert payload["temperature"] is None
    assert payload["pe_percentile"] is None
    assert payload["pb_percentile"] is None


def test_thermometer_cli_prints_all_a_reading_json(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """验证 thermometer --index wind_all_a JSON 输出全 A 市场读数。

    Args:
        monkeypatch: pytest monkeypatch fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 JSON 输出或参数转发不符合契约时抛出。
    """

    _FakeThermometerService.last_request = None
    _FakeThermometerService.snapshot = _available_all_a_thermometer_reading()
    monkeypatch.setattr(cli, "ThermometerService", _FakeThermometerService)
    runner = CliRunner()

    result = runner.invoke(cli.app, ["thermometer", "--index", "wind_all_a", "--json"])

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["index_code"] == "wind_all_a"
    assert payload["index_name"] == "万得全 A / 全 A 市场"
    assert payload["source"] == "akshare_legulegu_all_a_pe_pb"
    assert _FakeThermometerService.last_request is not None
    assert _FakeThermometerService.last_request.index_code == "wind_all_a"
    assert _FakeThermometerService.last_request.index_codes is None


def test_thermometer_cli_prints_index_reading_json(monkeypatch, tmp_path) -> None:  # type: ignore[no-untyped-def]
    """验证 thermometer --index JSON 输出自建温度计读数并转发参数。

    Args:
        monkeypatch: pytest monkeypatch fixture。
        tmp_path: pytest 临时目录 fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 JSON 输出或参数转发不符合契约时抛出。
    """

    _FakeThermometerService.last_request = None
    _FakeThermometerService.snapshot = _available_thermometer_reading()
    monkeypatch.setattr(cli, "ThermometerService", _FakeThermometerService)
    runner = CliRunner()

    result = runner.invoke(
        cli.app,
        ["thermometer", "--index", "000300", "--cache-dir", str(tmp_path), "--json"],
    )

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["index_code"] == "000300"
    assert payload["index_name"] == "沪深300"
    assert payload["temperature"] == "42.50"
    assert payload["valuation_state_candidate"] == "fair"
    assert "非有知有行官方数据" in payload["disclaimer"]
    assert _FakeThermometerService.last_request is not None
    assert _FakeThermometerService.last_request.index_code == "000300"
    assert _FakeThermometerService.last_request.cache_dir == tmp_path


def test_thermometer_cli_prints_index_reading_plain(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """验证 thermometer --index plain 输出自建温度计读数。

    Args:
        monkeypatch: pytest monkeypatch fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 plain 输出不符合契约时抛出。
    """

    _FakeThermometerService.last_request = None
    _FakeThermometerService.snapshot = _available_thermometer_reading()
    monkeypatch.setattr(cli, "ThermometerService", _FakeThermometerService)
    runner = CliRunner()

    result = runner.invoke(cli.app, ["thermometer", "--index", "000300"])

    assert result.exit_code == 0
    assert "index_code: 000300" in result.output
    assert "temperature: 42.50" in result.output
    assert "valuation_state_candidate: fair" in result.output


def test_thermometer_cli_prints_batch_reading_json(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """验证 thermometer --index 批量 JSON 输出和参数转发。

    Args:
        monkeypatch: pytest monkeypatch fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当批量 JSON 输出不符合契约时抛出。
    """

    _FakeThermometerService.last_request = None
    _FakeThermometerService.snapshot = _available_thermometer_batch_result()
    monkeypatch.setattr(cli, "ThermometerService", _FakeThermometerService)
    runner = CliRunner()

    result = runner.invoke(cli.app, ["thermometer", "--index", "000300,000905", "--json"])

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["source"] == "self_owned_index_thermometer_batch"
    assert payload["requested_index_codes"] == ["000300", "000905"]
    assert payload["result_count"] == 2
    assert payload["partial_unavailable"] is False
    assert payload["readings"][0]["index_code"] == "000300"
    assert payload["readings"][1]["index_code"] == "000905"
    assert _FakeThermometerService.last_request is not None
    assert _FakeThermometerService.last_request.index_code is None
    assert _FakeThermometerService.last_request.index_codes == ("000300", "000905")


def test_thermometer_cli_prints_all_a_mixed_batch_reading_json(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """验证 thermometer --index 支持全 A 与指数混合批量 JSON 输出。

    Args:
        monkeypatch: pytest monkeypatch fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当混合批量 JSON 输出不符合契约时抛出。
    """

    _FakeThermometerService.last_request = None
    _FakeThermometerService.snapshot = _available_all_a_mixed_batch_result()
    monkeypatch.setattr(cli, "ThermometerService", _FakeThermometerService)
    runner = CliRunner()

    result = runner.invoke(cli.app, ["thermometer", "--index", "wind_all_a,000300", "--json"])

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["requested_index_codes"] == ["wind_all_a", "000300"]
    assert payload["result_count"] == 2
    assert payload["readings"][0]["index_code"] == "wind_all_a"
    assert payload["readings"][0]["index_name"] == "万得全 A / 全 A 市场"
    assert payload["readings"][1]["index_code"] == "000300"
    assert _FakeThermometerService.last_request is not None
    assert _FakeThermometerService.last_request.index_code is None
    assert _FakeThermometerService.last_request.index_codes == ("wind_all_a", "000300")


def test_thermometer_cli_prints_batch_reading_plain(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """验证 thermometer --index 批量 plain 输出。

    Args:
        monkeypatch: pytest monkeypatch fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当批量 plain 输出不符合契约时抛出。
    """

    _FakeThermometerService.last_request = None
    _FakeThermometerService.snapshot = _available_thermometer_batch_result()
    monkeypatch.setattr(cli, "ThermometerService", _FakeThermometerService)
    runner = CliRunner()

    result = runner.invoke(cli.app, ["thermometer", "--index", "000300,000905"])

    assert result.exit_code == 0
    assert "source: self_owned_index_thermometer_batch" in result.output
    assert "requested_index_codes: 000300,000905" in result.output
    assert "[000300]" in result.output
    assert "[000905]" in result.output
    assert "index_name: 中证500" in result.output


def test_thermometer_cli_partial_unavailable_batch_json_exits_zero(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """验证 well-formed unsupported code 在 CLI JSON 中是 partial unavailable 且退出 0。

    Args:
        monkeypatch: pytest monkeypatch fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 unsupported code 被当成进程失败时抛出。
    """

    _FakeThermometerService.last_request = None
    _FakeThermometerService.snapshot = _partial_unavailable_thermometer_batch_result()
    monkeypatch.setattr(cli, "ThermometerService", _FakeThermometerService)
    runner = CliRunner()

    result = runner.invoke(cli.app, ["thermometer", "--index", "000300,999999", "--json"])

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["requested_index_codes"] == ["000300", "999999"]
    assert payload["partial_unavailable"] is True
    assert payload["unavailable_count"] == 1
    assert payload["readings"][1]["index_code"] == "999999"
    assert payload["readings"][1]["unavailable"] is True
    assert _FakeThermometerService.last_request.index_codes == ("000300", "999999")


def test_thermometer_cli_unsupported_batch_item_returns_unavailable_json(
    tmp_path: Path,
) -> None:
    """验证 CLI 真实 Service 对 unsupported 指数返回单项 unavailable。

    Args:
        tmp_path: pytest 临时目录 fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 CLI 未返回单项 unavailable 读数时抛出。
    """

    cache = ThermometerHistoryCache(root_dir=tmp_path)
    cache.save(_cli_index_history(index_code="000300", index_name="沪深300"))
    runner = CliRunner()

    result = runner.invoke(
        cli.app,
        [
            "thermometer",
            "--index",
            "000300,999999",
            "--cache-dir",
            str(tmp_path),
            "--json",
        ],
    )

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["requested_index_codes"] == ["000300", "999999"]
    assert payload["partial_unavailable"] is True
    assert payload["unavailable_count"] == 1
    assert payload["readings"][0]["index_code"] == "000300"
    assert payload["readings"][0]["unavailable"] is False
    assert payload["readings"][0]["cached"] is True
    assert payload["readings"][1]["index_code"] == "999999"
    assert payload["readings"][1]["unavailable"] is True
    assert payload["readings"][1]["cached"] is False
    assert payload["readings"][1]["temperature"] is None
    assert "暂不支持温度计代码：999999" in str(payload["readings"][1]["unavailable_reason"])


@pytest.mark.parametrize(
    "index_option",
    [
        "000300,abc",
        "wind_all_a,abc",
        "000300,",
        ",000905",
        "   ",
        "000300,   ",
    ],
)
def test_thermometer_cli_malformed_index_input_exits_two(
    index_option: str,
) -> None:  # type: ignore[no-untyped-def]
    """验证 malformed `--index` 请求退出 2。

    Args:
        index_option: 待验证的 CLI `--index` 原始值。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 malformed 输入未退出 2 时抛出。
    """

    runner = CliRunner()

    result = runner.invoke(cli.app, ["thermometer", "--index", index_option])

    assert result.exit_code == 2
    assert "温度计请求参数错误" in result.output


def test_thermometer_cli_exits_nonzero_on_service_error(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """验证 thermometer Service 异常时 CLI 非零退出。

    Args:
        monkeypatch: pytest monkeypatch fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当失败路径不符合契约时抛出。
    """

    monkeypatch.setattr(cli, "ThermometerService", _FailingThermometerService)
    runner = CliRunner()

    result = runner.invoke(cli.app, ["thermometer"])

    assert result.exit_code == 1
    assert "温度计查询失败：thermometer fixture failure" in result.output


def test_extraction_snapshot_cli_is_thin_capability_entry(monkeypatch, tmp_path) -> None:  # type: ignore[no-untyped-def]
    """验证 extraction-snapshot 命令只把显式参数转发给 Service。

    Args:
        monkeypatch: pytest monkeypatch fixture。
        tmp_path: pytest 临时目录 fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 CLI 参数转发或输出路径不符合契约时抛出。
    """

    _FakeExtractionSnapshotService.last_request = None
    monkeypatch.setattr(cli, "ExtractionSnapshotService", _FakeExtractionSnapshotService)
    runner = CliRunner()

    result = runner.invoke(
        cli.app,
        [
            "extraction-snapshot",
            "--run-id",
            "unit-run",
            "--fund-code",
            "004393",
            "--report-year",
            "2024",
            "--source-csv",
            "docs/code_20260519.csv",
            "--output-dir",
            str(tmp_path),
            "--sample-per-category",
            "2",
            "--limit",
            "3",
            "--force-refresh",
        ],
    )

    assert result.exit_code == 0
    assert "snapshot:" in result.output
    assert _FakeExtractionSnapshotService.last_request is not None
    assert _FakeExtractionSnapshotService.last_request.fund_code == "004393"
    assert _FakeExtractionSnapshotService.last_request.report_year == 2024
    assert _FakeExtractionSnapshotService.last_request.source_csv == Path("docs/code_20260519.csv")
    assert _FakeExtractionSnapshotService.last_request.run_id == "unit-run"
    assert _FakeExtractionSnapshotService.last_request.output_dir == tmp_path
    assert _FakeExtractionSnapshotService.last_request.force_refresh is True
    assert _FakeExtractionSnapshotService.last_request.sample_per_category == 2
    assert _FakeExtractionSnapshotService.last_request.limit == 3


def test_extractor_output_save_cli_is_thin_service_entry(monkeypatch, tmp_path) -> None:  # type: ignore[no-untyped-def]
    """验证 extractor-output-save 命令只把显式参数转发给 Service。

    Args:
        monkeypatch: pytest monkeypatch fixture。
        tmp_path: pytest 临时目录 fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 CLI 参数转发或输出路径不符合契约时抛出。
    """

    _FakeExtractorOutputService.last_request = None
    monkeypatch.setattr(cli, "ExtractorOutputService", _FakeExtractorOutputService)
    runner = CliRunner()

    result = runner.invoke(
        cli.app,
        [
            "extractor-output-save",
            "004393",
            "--report-year",
            "2024",
            "--report-type",
            "annual_report",
            "--output-root",
            str(tmp_path),
            "--force-refresh",
        ],
    )

    assert result.exit_code == 0
    assert "extractor_output_json:" in result.output
    assert "schema_version: fund-agent.extractor_output.v1" in result.output
    assert "fund_code: 004393" in result.output
    assert "report_type: annual_report" in result.output
    assert "report_year: 2024" in result.output
    assert _FakeExtractorOutputService.last_request is not None
    assert _FakeExtractorOutputService.last_request.fund_code == "004393"
    assert _FakeExtractorOutputService.last_request.report_year == 2024
    assert _FakeExtractorOutputService.last_request.report_type == "annual_report"
    assert _FakeExtractorOutputService.last_request.output_root == tmp_path
    assert _FakeExtractorOutputService.last_request.force_refresh is True


def test_extraction_score_cli_is_thin_service_entry(monkeypatch, tmp_path) -> None:  # type: ignore[no-untyped-def]
    """验证 extraction-score 命令只把显式参数转发给 Service。

    Args:
        monkeypatch: pytest monkeypatch fixture。
        tmp_path: pytest 临时目录 fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 CLI 参数转发或输出路径不符合契约时抛出。
    """

    _FakeExtractionScoreService.last_request = None
    monkeypatch.setattr(cli, "ExtractionScoreService", _FakeExtractionScoreService)
    runner = CliRunner()

    result = runner.invoke(
        cli.app,
        [
            "extraction-score",
            "--snapshot-path",
            "reports/extraction-snapshots/unit/snapshot.jsonl",
            "--source-csv",
            "docs/code_20260519.csv",
            "--output-dir",
            str(tmp_path),
            "--golden-answer-path",
            "reports/golden-answers/golden-answer.json",
            "--errors-path",
            "reports/extraction-snapshots/unit/errors.jsonl",
        ],
    )

    assert result.exit_code == 0
    assert "score_json:" in result.output
    assert _FakeExtractionScoreService.last_request is not None
    assert _FakeExtractionScoreService.last_request.snapshot_path == Path(
        "reports/extraction-snapshots/unit/snapshot.jsonl"
    )
    assert _FakeExtractionScoreService.last_request.source_csv == Path("docs/code_20260519.csv")
    assert _FakeExtractionScoreService.last_request.output_dir == tmp_path
    assert _FakeExtractionScoreService.last_request.golden_answer_path == Path(
        "reports/golden-answers/golden-answer.json"
    )
    assert _FakeExtractionScoreService.last_request.errors_path == Path(
        "reports/extraction-snapshots/unit/errors.jsonl"
    )


def test_golden_prefill_cli_is_thin_service_entry(monkeypatch, tmp_path) -> None:  # type: ignore[no-untyped-def]
    """验证 golden-prefill 命令只把显式参数转发给 Service。

    Args:
        monkeypatch: pytest monkeypatch fixture。
        tmp_path: pytest 临时目录 fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 CLI 参数转发或输出路径不符合契约时抛出。
    """

    _FakeGoldenPrefillService.last_request = None
    monkeypatch.setattr(cli, "GoldenPrefillService", _FakeGoldenPrefillService)
    runner = CliRunner()
    output_path = tmp_path / "prefill.md"

    result = runner.invoke(
        cli.app,
        [
            "golden-prefill",
            "--template-path",
            "docs/golden-answer-template.md",
            "--output-path",
            str(output_path),
            "--report-year",
            "2024",
            "--force-refresh",
        ],
    )

    assert result.exit_code == 0
    assert "prefill:" in result.output
    assert _FakeGoldenPrefillService.last_request is not None
    assert _FakeGoldenPrefillService.last_request.template_path == Path(
        "docs/golden-answer-template.md"
    )
    assert _FakeGoldenPrefillService.last_request.output_path == output_path
    assert _FakeGoldenPrefillService.last_request.report_year == 2024
    assert _FakeGoldenPrefillService.last_request.force_refresh is True


def test_golden_build_cli_is_thin_service_entry(monkeypatch, tmp_path) -> None:  # type: ignore[no-untyped-def]
    """验证 golden-build 命令只把显式参数转发给 Service。

    Args:
        monkeypatch: pytest monkeypatch fixture。
        tmp_path: pytest 临时目录 fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 CLI 参数转发或输出摘要不符合契约时抛出。
    """

    _FakeGoldenAnswerService.last_request = None
    monkeypatch.setattr(cli, "GoldenAnswerService", _FakeGoldenAnswerService)
    runner = CliRunner()
    input_path = tmp_path / "reviewed.md"
    output_path = tmp_path / "golden-answer.json"

    result = runner.invoke(
        cli.app,
        [
            "golden-build",
            "--input-path",
            str(input_path),
            "--output-path",
            str(output_path),
        ],
    )

    assert result.exit_code == 0
    assert "golden_answer:" in result.output
    assert "records: 2" in result.output
    assert _FakeGoldenAnswerService.last_request is not None
    assert _FakeGoldenAnswerService.last_request.input_path == input_path
    assert _FakeGoldenAnswerService.last_request.output_path == output_path


def test_golden_build_cli_defaults_to_reviewed_markdown(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """验证 golden-build 默认读取人工审核后的 Markdown。

    Args:
        monkeypatch: pytest monkeypatch fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当默认输入路径不是 reviewed Markdown 时抛出。
    """

    _FakeGoldenAnswerService.last_request = None
    monkeypatch.setattr(cli, "GoldenAnswerService", _FakeGoldenAnswerService)
    runner = CliRunner()

    result = runner.invoke(cli.app, ["golden-build"])

    assert result.exit_code == 0
    assert _FakeGoldenAnswerService.last_request is not None
    assert _FakeGoldenAnswerService.last_request.input_path == Path(
        "reports/golden-answers/golden-answer-prefill-reviewed.md"
    )
    assert _FakeGoldenAnswerService.last_request.output_path == Path(
        "reports/golden-answers/golden-answer.json"
    )


def test_quality_gate_cli_is_thin_service_entry(monkeypatch, tmp_path) -> None:  # type: ignore[no-untyped-def]
    """验证 quality-gate 命令只把显式参数转发给 Service。

    Args:
        monkeypatch: pytest monkeypatch fixture。
        tmp_path: pytest 临时目录 fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 CLI 参数转发或输出摘要不符合契约时抛出。
    """

    _FakeQualityGateService.last_request = None
    monkeypatch.setattr(cli, "QualityGateService", _FakeQualityGateService)
    runner = CliRunner()
    score_path = tmp_path / "score.json"
    output_dir = tmp_path / "gate"

    result = runner.invoke(
        cli.app,
        [
            "quality-gate",
            "--score-path",
            str(score_path),
            "--output-dir",
            str(output_dir),
        ],
    )

    assert result.exit_code == 0
    assert "quality_gate_json:" in result.output
    assert "status: block" in result.output
    assert _FakeQualityGateService.last_request is not None
    assert _FakeQualityGateService.last_request.score_path == score_path
    assert _FakeQualityGateService.last_request.output_dir == output_dir


def test_golden_readiness_preflight_cli_outputs_paths_and_status(
    monkeypatch,
    tmp_path,
) -> None:  # type: ignore[no-untyped-def]
    """验证 golden-readiness-preflight CLI 转发显式参数并输出产物路径。

    Args:
        monkeypatch: pytest monkeypatch fixture。
        tmp_path: pytest 临时目录 fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 CLI 输出或请求转发不符合契约时抛出。
    """

    _FakeGoldenReadinessPreflightService.last_request = None
    monkeypatch.setattr(
        cli, "GoldenReadinessPreflightService", _FakeGoldenReadinessPreflightService
    )
    runner = CliRunner()
    output_dir = tmp_path / "preflight"

    result = runner.invoke(
        cli.app,
        [
            "golden-readiness-preflight",
            "--run-id",
            "unit",
            "--source-csv",
            "docs/code_20260519.csv",
            "--golden-answer-path",
            "reports/golden-answers/golden-answer.json",
            "--output-dir",
            str(output_dir),
            "--fund-artifact",
            "006597::2024::snapshot.jsonl::score.json::quality_gate.json",
        ],
    )

    assert result.exit_code == 0
    assert "preflight_json: golden_readiness_preflight.json" in result.output
    assert "overall_status: block" in result.output
    request = _FakeGoldenReadinessPreflightService.last_request
    assert request is not None
    assert request.output_dir == output_dir
    assert len(request.fund_artifacts) == 1
    artifact = request.fund_artifacts[0]
    assert artifact.fund_code == "006597"
    assert artifact.report_year == 2024
    assert artifact.snapshot_path == Path("snapshot.jsonl")
    assert artifact.score_path == Path("score.json")
    assert artifact.quality_gate_path == Path("quality_gate.json")


def test_golden_readiness_preflight_cli_rejects_preflight_input_conflicts(
    monkeypatch,
) -> None:  # type: ignore[no-untyped-def]
    """验证 `--preflight-input` 与逐项输入互斥。

    Args:
        monkeypatch: pytest monkeypatch fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当互斥参数未返回 exit 2 时抛出。
    """

    monkeypatch.setattr(
        cli, "GoldenReadinessPreflightService", _FakeGoldenReadinessPreflightService
    )
    runner = CliRunner()

    result = runner.invoke(
        cli.app,
        [
            "golden-readiness-preflight",
            "--preflight-input",
            "input.json",
            "--fund-artifact",
            "006597::2024::snapshot.jsonl::score.json::quality_gate.json",
        ],
    )

    assert result.exit_code == 2
    assert "--preflight-input 不能与逐项输入同时使用" in result.output


def test_golden_readiness_preflight_cli_rejects_bad_fund_artifact_fields() -> None:
    """验证 `--fund-artifact` 字段数必须精确为 5。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当错误字段数未返回 exit 2 时抛出。
    """

    runner = CliRunner()

    result = runner.invoke(
        cli.app,
        [
            "golden-readiness-preflight",
            "--fund-artifact",
            "006597::2024::snapshot.jsonl::score.json",
        ],
    )

    assert result.exit_code == 2
    assert "--fund-artifact 格式必须是" in result.output


def test_golden_readiness_preflight_cli_rejects_bad_fund_code() -> None:
    """验证 `--fund-artifact` fund_code 必须为 6 位数字。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当错误 fund_code 未返回 exit 2 时抛出。
    """

    runner = CliRunner()

    result = runner.invoke(
        cli.app,
        [
            "golden-readiness-preflight",
            "--fund-artifact",
            "6597::2024::snapshot.jsonl::score.json::quality_gate.json",
        ],
    )

    assert result.exit_code == 2
    assert "fund_code 必须是 6 位数字" in result.output
