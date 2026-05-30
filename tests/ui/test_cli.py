"""CLI 入口测试。"""

from __future__ import annotations

import json
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path

import pytest
from typer.main import get_command
from typer.testing import CliRunner

from fund_agent.fund.data.thermometer_cache import ThermometerHistoryCache
from fund_agent.fund.data.thermometer_types import PePbHistory, PePbPoint
from fund_agent.fund.quality_gate import QualityGateIssue, QualityGateResult
from fund_agent.services import (
    QualityGateBlockedError,
    QualityGateNotRunBlockedError,
    ThermometerBatchResult,
    ThermometerReading,
)
from fund_agent.ui import cli


@dataclass(frozen=True, slots=True)
class _FakeResult:
    """CLI 测试用 Service 返回值。"""

    report_markdown: str
    quality_gate_result: object | None = None
    quality_gate_not_run_reason: str | None = None


class _FakeService:
    """CLI 测试用成功 Service。"""

    last_request = None
    analyze_called = False
    analyze_with_llm_called = False

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

    async def analyze_with_llm(self, request, *, llm_clients):  # type: ignore[no-untyped-def]
        """记录 LLM 分析调用，测试 fail-closed 时不得触发。

        Args:
            request: CLI 构造的 Service 请求。
            llm_clients: 显式注入的 LLM 客户端。

        Returns:
            fake Service 返回值。

        Raises:
            无显式抛出。
        """

        type(self).analyze_with_llm_called = True
        type(self).last_request = request
        return _FakeResult(report_markdown="# LLM report\n")


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
    _FakeService.analyze_called = False
    _FakeService.analyze_with_llm_called = False
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
    assert _FakeService.analyze_with_llm_called is False
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


def test_analyze_cli_use_llm_fails_closed_before_service(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """验证 `analyze --use-llm` 在 provider 未实现时失败关闭。

    Args:
        monkeypatch: pytest monkeypatch fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 CLI 调用 Service 或输出 deterministic 报告时抛出。
    """

    _FakeService.last_request = None
    _FakeService.analyze_called = False
    _FakeService.analyze_with_llm_called = False
    monkeypatch.setattr(cli, "FundAnalysisService", _FakeService)
    runner = CliRunner()

    result = runner.invoke(cli.app, ["analyze", "110011", "--use-llm"])

    assert result.exit_code == 1
    assert result.stdout == ""
    assert "LLM provider 未配置/未实现" in result.stderr
    assert "# 0. 投资要点概览" not in result.output
    assert _FakeService.last_request is None
    assert _FakeService.analyze_called is False
    assert _FakeService.analyze_with_llm_called is False


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
    monkeypatch.setattr(cli, "FundAnalysisService", _FakeService)
    runner = CliRunner()

    result = runner.invoke(cli.app, ["analyze", "110011"])

    assert result.exit_code == 0
    assert _FakeService.last_request is not None
    assert _FakeService.last_request.mode == "product"
    assert _FakeService.last_request.developer_overrides is None
    assert _FakeService.last_request.valuation_state is None


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
    assert "--use-llm" in result.output

    analyze_command = get_command(cli.app).commands["analyze"]
    option_names = {
        option_name
        for parameter in analyze_command.params
        for option_name in getattr(parameter, "opts", ())
    }
    assert "--thermometer-cache-dir" in option_names
    assert "--use-llm" in option_names


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
    assert "--use-llm" in result.output
    assert _FakeChecklistService.last_request is None
    assert _FakeChecklistService.checklist_called is False

    checklist_command = get_command(cli.app).commands["checklist"]
    option_names = {
        option_name
        for parameter in checklist_command.params
        for option_name in getattr(parameter, "opts", ())
    }
    assert "--use-llm" not in option_names


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
