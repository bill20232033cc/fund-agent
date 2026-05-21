"""CLI 入口测试。"""

from __future__ import annotations

import json
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path

from typer.testing import CliRunner

from fund_agent.fund.data.thermometer import MacroTemperature, MarketTemperature, ThermometerSnapshot
from fund_agent.fund.quality_gate import QualityGateResult
from fund_agent.services import QualityGateBlockedError, QualityGateNotRunBlockedError
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

    async def analyze(self, request):  # type: ignore[no-untyped-def]
        """记录请求并返回固定 Markdown。

        Args:
            request: CLI 构造的 Service 请求。

        Returns:
            fake Service 返回值。

        Raises:
            无显式抛出。
        """

        type(self).last_request = request
        return _FakeResult(report_markdown="# 0. 投资要点概览\n\n# 7. 是否值得持有——最终判断\n")


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


def _fake_quality_gate_result(*, status: str) -> QualityGateResult:
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
        issues=(object(), object()),
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
        return type(self).snapshot or _available_thermometer_snapshot()


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


def _available_thermometer_snapshot() -> ThermometerSnapshot:
    """构造可用温度计快照。

    Args:
        无。

    Returns:
        可用温度计快照。

    Raises:
        无显式抛出。
    """

    return ThermometerSnapshot(
        as_of_text="2026-05-20",
        as_of_date="2026-05-20",
        market=MarketTemperature(
            value=Decimal("32.5"),
            valuation_band="偏低",
            trend_text="低估",
        ),
        indexes=(),
        macro=MacroTemperature(
            bond_temperature=Decimal("55.5"),
            ten_year_treasury_yield=Decimal("2.1"),
        ),
        source="youzhiyouxing",
        cached=False,
        stale=False,
        unavailable=False,
        unavailable_reason=None,
        fetched_at="2026-05-20T00:00:00+00:00",
    )


def _unavailable_thermometer_snapshot() -> ThermometerSnapshot:
    """构造不可用温度计快照。

    Args:
        无。

    Returns:
        不可用温度计快照。

    Raises:
        无显式抛出。
    """

    return ThermometerSnapshot(
        as_of_text=None,
        as_of_date=None,
        market=None,
        indexes=(),
        macro=None,
        source="youzhiyouxing",
        cached=False,
        stale=False,
        unavailable=True,
        unavailable_reason="network down",
        fetched_at=None,
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
    assert _FakeService.last_request is not None
    assert _FakeService.last_request.fund_code == "110011"
    assert _FakeService.last_request.report_year == 2024
    assert _FakeService.last_request.mode == "developer_override"
    assert _FakeService.last_request.developer_overrides is not None
    assert _FakeService.last_request.developer_overrides.equity_position == "80%"
    assert _FakeService.last_request.developer_overrides.final_judgment_override == "worth_holding"
    assert _FakeService.last_request.force_refresh is True
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


def test_checklist_cli_is_not_misleading_placeholder() -> None:
    """验证 checklist 命令不会输出误导性成功文本。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 placeholder 命令伪装成功时抛出。
    """

    runner = CliRunner()

    result = runner.invoke(cli.app, ["checklist", "110011"])

    assert result.exit_code == 2
    assert "尚未接入 Service" in result.output


def test_thermometer_cli_prints_plain_summary(monkeypatch, tmp_path) -> None:  # type: ignore[no-untyped-def]
    """验证 thermometer 命令输出 plain text 摘要并转发显式参数。

    Args:
        monkeypatch: pytest monkeypatch fixture。
        tmp_path: pytest 临时目录 fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 CLI 输出或参数转发不符合契约时抛出。
    """

    _FakeThermometerService.last_request = None
    _FakeThermometerService.snapshot = _available_thermometer_snapshot()
    monkeypatch.setattr(cli, "ThermometerService", _FakeThermometerService)
    runner = CliRunner()

    result = runner.invoke(
        cli.app,
        ["thermometer", "--cache-dir", str(tmp_path), "--force-refresh"],
    )

    assert result.exit_code == 0
    assert "source: youzhiyouxing" in result.output
    assert "unavailable: false" in result.output
    assert "market_temperature: 32.5" in result.output
    assert _FakeThermometerService.last_request is not None
    assert _FakeThermometerService.last_request.cache_dir == tmp_path
    assert _FakeThermometerService.last_request.force_refresh is True


def test_thermometer_cli_prints_json_for_unavailable_snapshot(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """验证 thermometer JSON 输出覆盖 unavailable 数据态且退出 0。

    Args:
        monkeypatch: pytest monkeypatch fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 JSON 输出或退出码不符合契约时抛出。
    """

    _FakeThermometerService.last_request = None
    _FakeThermometerService.snapshot = _unavailable_thermometer_snapshot()
    monkeypatch.setattr(cli, "ThermometerService", _FakeThermometerService)
    runner = CliRunner()

    result = runner.invoke(cli.app, ["thermometer", "--json"])

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["unavailable"] is True
    assert payload["unavailable_reason"] == "network down"
    assert payload["market_temperature"] is None


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
