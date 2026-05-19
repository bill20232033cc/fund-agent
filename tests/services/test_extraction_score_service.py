"""精选基金池抽取评分 Service 测试。"""

from __future__ import annotations

from pathlib import Path

import pytest

from fund_agent.fund.extraction_score import (
    CORRECTNESS_STATUS_UNAVAILABLE,
    CorrectnessSummary,
    ExtractionScoreResult,
    GoldenSetSelection,
    ScoreThresholds,
)
from fund_agent.services import ExtractionScoreRequest, ExtractionScoreService
from fund_agent.services import extraction_score_service


def test_extraction_score_service_delegates_explicit_params(monkeypatch, tmp_path: Path) -> None:  # type: ignore[no-untyped-def]
    """验证 Service 以显式参数委托 Capability 层评分能力。

    Args:
        monkeypatch: pytest monkeypatch fixture。
        tmp_path: pytest 临时目录 fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当参数转发或结果不符合契约时抛出。
    """

    calls = []

    def fake_run_extraction_score(**kwargs):  # type: ignore[no-untyped-def]
        """记录 Service 转发参数并返回固定结果。

        Args:
            kwargs: Service 转发给 Capability 的参数。

        Returns:
            fake 评分运行结果。

        Raises:
            无显式抛出。
        """

        calls.append(kwargs)
        return ExtractionScoreResult(
            snapshot_path=kwargs["snapshot_path"],
            source_csv=kwargs["source_csv"],
            output_dir=tmp_path,
            score_json_path=tmp_path / "score.json",
            score_markdown_path=tmp_path / "score.md",
            golden_set_path=tmp_path / "golden_set.json",
            field_scores=(),
            fund_scores=(),
            fund_quality=(),
            failed_funds=(),
            golden_set=GoldenSetSelection(
                source_csv=str(kwargs["source_csv"]),
                records=(),
                excluded_categories=("货币基金类",),
                exclusion_reason="fixture",
            ),
            thresholds=kwargs["thresholds"],
            correctness=CorrectnessSummary(
                status=CORRECTNESS_STATUS_UNAVAILABLE,
                golden_answer_path=str(kwargs["golden_answer_path"]),
                total_records=0,
                comparable_records=0,
                matched_records=0,
                mismatched_records=0,
                unavailable_records=0,
                skipped_records=0,
                accuracy_rate=None,
                reason="fixture",
                record_results=(),
            ),
        )

    monkeypatch.setattr(extraction_score_service, "run_extraction_score", fake_run_extraction_score)
    service = ExtractionScoreService()
    thresholds = ScoreThresholds(pass_coverage=0.95, pass_traceability=0.95)
    request = ExtractionScoreRequest(
        snapshot_path=tmp_path / "snapshot.jsonl",
        source_csv=Path("docs/code_20260519.csv"),
        output_dir=tmp_path,
        thresholds=thresholds,
        golden_answer_path=tmp_path / "golden-answer.json",
        errors_path=tmp_path / "errors.jsonl",
    )

    result = service.run(request)

    assert result.score_json_path == tmp_path / "score.json"
    assert len(calls) == 1
    assert calls[0] == {
        "snapshot_path": tmp_path / "snapshot.jsonl",
        "source_csv": Path("docs/code_20260519.csv"),
        "output_dir": tmp_path,
        "thresholds": thresholds,
        "golden_answer_path": tmp_path / "golden-answer.json",
        "errors_path": tmp_path / "errors.jsonl",
    }


def test_extraction_score_service_rejects_non_jsonl_snapshot(tmp_path: Path) -> None:
    """验证 Service 层拒绝非 JSONL snapshot 路径。

    Args:
        tmp_path: pytest 临时目录 fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当非法 snapshot 路径未被拒绝时抛出。
    """

    service = ExtractionScoreService()
    request = ExtractionScoreRequest(
        snapshot_path=tmp_path / "snapshot.json",
        source_csv=Path("docs/code_20260519.csv"),
        output_dir=None,
    )

    with pytest.raises(ValueError, match="jsonl"):
        service.run(request)


def test_extraction_score_service_rejects_non_jsonl_errors_path(tmp_path: Path) -> None:
    """验证 Service 层拒绝非 JSONL errors 路径。

    Args:
        tmp_path: pytest 临时目录 fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当非法 errors 路径未被拒绝时抛出。
    """

    service = ExtractionScoreService()
    request = ExtractionScoreRequest(
        snapshot_path=tmp_path / "snapshot.jsonl",
        source_csv=Path("docs/code_20260519.csv"),
        output_dir=None,
        errors_path=tmp_path / "errors.txt",
    )

    with pytest.raises(ValueError, match="errors_path"):
        service.run(request)
