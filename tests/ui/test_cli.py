"""CLI 入口测试。"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from typer.testing import CliRunner

from fund_agent.ui import cli


@dataclass(frozen=True, slots=True)
class _FakeResult:
    """CLI 测试用 Service 返回值。"""

    report_markdown: str


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
        ],
    )

    assert result.exit_code == 0
    assert result.output == "# 0. 投资要点概览\n\n# 7. 是否值得持有——最终判断\n"
    assert _FakeService.last_request is not None
    assert _FakeService.last_request.fund_code == "110011"
    assert _FakeService.last_request.report_year == 2024
    assert _FakeService.last_request.equity_position == "80%"
    assert _FakeService.last_request.final_judgment == "worth_holding"
    assert _FakeService.last_request.force_refresh is True


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
        ],
    )

    assert result.exit_code == 0
    assert "score_json:" in result.output
    assert _FakeExtractionScoreService.last_request is not None
    assert _FakeExtractionScoreService.last_request.snapshot_path == Path("reports/extraction-snapshots/unit/snapshot.jsonl")
    assert _FakeExtractionScoreService.last_request.source_csv == Path("docs/code_20260519.csv")
    assert _FakeExtractionScoreService.last_request.output_dir == tmp_path
