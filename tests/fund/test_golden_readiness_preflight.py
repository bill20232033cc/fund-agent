"""Golden readiness preflight 聚合测试。"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from fund_agent.fund.golden_readiness_preflight import (
    FundArtifactInput,
    load_default_current_disposition_manifest,
    run_golden_readiness_preflight,
)


def test_preflight_blocks_missing_required_artifact(tmp_path: Path) -> None:
    """缺失 required artifact 时不得 ready，并输出 missing_input_artifact。

    Args:
        tmp_path: pytest 临时目录 fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当缺失 artifact 未 fail-closed 时抛出。
    """

    source_csv = _write_text(tmp_path / "source.csv", "fund_code\n000001\n")
    golden = _write_golden(tmp_path / "golden.json", ("000001",))

    result = run_golden_readiness_preflight(
        source_csv=source_csv,
        output_dir=tmp_path / "out",
        run_id="unit",
        fund_artifacts=(
            FundArtifactInput(
                fund_code="000001",
                report_year=2024,
                snapshot_path=tmp_path / "missing.jsonl",
                score_path=None,
                quality_gate_path=None,
            ),
        ),
        golden_answer_path=golden,
        fixture_promotion_state_path=None,
        coverage_disposition_path=None,
    )

    row = result.rows[0]
    assert row.readiness == "not_evaluated"
    assert "missing_input_artifact" in _row_blocker_codes(row)
    assert result.overall_status == "block"


def test_preflight_marks_006597_bond_blocker_resolved_not_blocker(tmp_path: Path) -> None:
    """006597 最新 bond blocker 必须作为 resolved item，不得列 blocker。

    Args:
        tmp_path: pytest 临时目录 fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 006597 bond blocker 回归时抛出。
    """

    source_csv = _write_text(tmp_path / "source.csv", "fund_code\n006597\n")
    golden = _write_golden(tmp_path / "golden.json", ("006597",))
    snapshot = _write_snapshot(tmp_path / "snapshot.jsonl", fund_code="006597")
    score = _write_score(tmp_path / "score.json", fund_code="006597")
    quality = _write_quality(tmp_path / "quality.json", fund_code="006597", status="warn")

    result = run_golden_readiness_preflight(
        source_csv=source_csv,
        output_dir=tmp_path / "out",
        run_id="unit",
        fund_artifacts=(
            FundArtifactInput(
                fund_code="006597",
                report_year=2024,
                snapshot_path=snapshot,
                score_path=score,
                quality_gate_path=quality,
                raw_disposition="bond_risk_evidence_resolved_not_promoted",
                preflight_disposition="include_for_later_review",
            ),
        ),
        golden_answer_path=golden,
        fixture_promotion_state_path=None,
        coverage_disposition_path=None,
    )

    row = result.rows[0]
    assert any(
        item.code == "blocker_resolved"
        and item.original_blocker_code == "bond_risk_evidence_missing"
        and item.fund_code == "006597"
        for item in row.resolved_items
    )
    assert "bond_risk_evidence_missing" not in _row_blocker_codes(row)
    payload = json.loads(result.json_path.read_text(encoding="utf-8"))
    assert "bond_risk_evidence_missing" not in {
        blocker["code"] for blocker in payload["rows"][0]["blockers"]
    }


def test_preflight_blocks_baseline_blocking_score_issue(tmp_path: Path) -> None:
    """baseline_blocking score issue 必须 block。

    Args:
        tmp_path: pytest 临时目录 fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 baseline_blocking 未阻断时抛出。
    """

    result = _run_single_artifact(
        tmp_path,
        fund_code="000001",
        score_extra={
            "score_applicability_issues": [
                {"reason_code": "unit", "baseline_blocking": True}
            ]
        },
    )

    row = result.rows[0]
    assert row.readiness == "blocked"
    assert "score_applicability_baseline_blocking" in _row_blocker_codes(row)


def test_preflight_blocks_quality_block_but_warn_only_warning(tmp_path: Path) -> None:
    """quality block 阻断；quality warn 只进入 warning。

    Args:
        tmp_path: pytest 临时目录 fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 quality gate 状态聚合错误时抛出。
    """

    blocked = _run_single_artifact(tmp_path / "blocked", fund_code="000001", quality_status="block")
    warned = _run_single_artifact(tmp_path / "warned", fund_code="000002", quality_status="warn")

    assert "quality_gate_block" in _row_blocker_codes(blocked.rows[0])
    assert "quality_gate_warn" in {warning.code for warning in warned.rows[0].warnings}
    assert "quality_gate_block" not in _row_blocker_codes(warned.rows[0])


def test_preflight_blocks_source_provenance_unknown_or_ineligible(tmp_path: Path) -> None:
    """fallback provenance unknown 或 ineligible 必须 fail-closed。

    Args:
        tmp_path: pytest 临时目录 fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 source provenance 未 fail-closed 时抛出。
    """

    unknown = _run_single_artifact(
        tmp_path / "unknown",
        fund_code="000001",
        snapshot_extra={
            "fallback_used": True,
            "primary_failure_category": None,
            "fallback_eligibility": "unknown",
            "source_provenance_status": "incomplete",
        },
    )
    ineligible = _run_single_artifact(
        tmp_path / "ineligible",
        fund_code="000002",
        snapshot_extra={
            "fallback_used": True,
            "primary_failure_category": "schema_drift",
            "fallback_eligibility": "ineligible",
            "source_provenance_status": "incomplete",
        },
    )

    assert "source_provenance_unknown" in _row_blocker_codes(unknown.rows[0])
    assert "source_provenance_ineligible" in _row_blocker_codes(ineligible.rows[0])


def test_preflight_records_eligible_fallback_as_non_ready_evidence(tmp_path: Path) -> None:
    """eligible fallback 只记录 warning，不证明 ready。

    Args:
        tmp_path: pytest 临时目录 fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 eligible fallback 被当作 ready 证明时抛出。
    """

    result = _run_single_artifact(
        tmp_path,
        fund_code="000001",
        snapshot_extra={
            "fallback_used": True,
            "primary_failure_category": "unavailable",
            "fallback_eligibility": "eligible",
            "source_provenance_status": "complete",
        },
    )

    row = result.rows[0]
    assert "source_provenance_eligible_fallback" in {warning.code for warning in row.warnings}
    assert row.readiness != "ready"


def test_preflight_blocks_qdii_hard_stop(tmp_path: Path) -> None:
    """四个 QDII rows 必须输出 qdii coverage blocker 和 hard stop。

    Args:
        tmp_path: pytest 临时目录 fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 QDII hard stop 未阻断时抛出。
    """

    source_csv = _write_text(tmp_path / "source.csv", "fund_code\n096001\n")
    golden = _write_golden(tmp_path / "golden.json", ("096001", "040046", "019172", "021539"))

    result = run_golden_readiness_preflight(
        source_csv=source_csv,
        output_dir=tmp_path / "out",
        run_id="unit",
        fund_artifacts=(),
        golden_answer_path=golden,
        fixture_promotion_state_path=None,
        coverage_disposition_path=None,
    )

    qdii_rows = [row for row in result.rows if row.fund_code in {"096001", "040046", "019172", "021539"}]
    assert len(qdii_rows) == 4
    assert all("qdii_coverage_blocked" in _row_blocker_codes(row) for row in qdii_rows)
    assert "qdii_replacement_hard_stop" in {blocker.code for blocker in result.global_blockers}
    assert result.overall_status == "block"


def test_preflight_blocks_fof_taxonomy_pending_and_rejects_qdii_fof_as_pure_fof(
    tmp_path: Path,
) -> None:
    """FOF slot 必须保留 taxonomy/data gap，不能用 QDII-FOF 充当 pure FOF。

    Args:
        tmp_path: pytest 临时目录 fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 FOF slot 未阻断时抛出。
    """

    source_csv = _write_text(tmp_path / "source.csv", "fund_code\n007721\n")
    golden = _write_golden(tmp_path / "golden.json", ("007721",))

    result = run_golden_readiness_preflight(
        source_csv=source_csv,
        output_dir=tmp_path / "out",
        run_id="unit",
        fund_artifacts=(),
        golden_answer_path=golden,
        fixture_promotion_state_path=None,
        coverage_disposition_path=None,
    )

    fof_row = next(row for row in result.rows if row.fund_code == "FOF_SLOT")
    assert {"fof_taxonomy_pending", "fof_data_gap"} <= _row_blocker_codes(fof_row)
    assert fof_row.readiness == "blocked"


def test_preflight_preserves_110020_raw_disposition_and_blocks_not_promoted(
    tmp_path: Path,
) -> None:
    """110020 必须保留原始 disposition，并因未 promotion / 证据不足阻断。

    Args:
        tmp_path: pytest 临时目录 fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 110020 disposition 丢失或误放行时抛出。
    """

    source_csv = _write_text(tmp_path / "source.csv", "fund_code\n110020\n")
    golden = _write_golden(tmp_path / "golden.json", ("110020",))
    snapshot = _write_snapshot(tmp_path / "snapshot.jsonl", fund_code="110020")
    score = _write_score(tmp_path / "score.json", fund_code="110020")
    quality = _write_quality(tmp_path / "quality.json", fund_code="110020", status="warn")

    result = run_golden_readiness_preflight(
        source_csv=source_csv,
        output_dir=tmp_path / "out",
        run_id="unit",
        fund_artifacts=(
            FundArtifactInput(
                fund_code="110020",
                report_year=2024,
                snapshot_path=snapshot,
                score_path=score,
                quality_gate_path=quality,
                raw_disposition="reviewed_coverage_candidate_input_accepted",
                preflight_disposition="reviewed_coverage_candidate",
            ),
        ),
        golden_answer_path=golden,
        fixture_promotion_state_path=None,
        coverage_disposition_path=None,
    )

    row = result.rows[0]
    assert row.raw_disposition == "reviewed_coverage_candidate_input_accepted"
    assert row.preflight_disposition == "reviewed_coverage_candidate"
    assert {"reviewed_candidate_not_promoted", "index_evidence_insufficient"} <= _row_blocker_codes(
        row
    )


def test_preflight_blocks_strict_golden_absence_and_fund_miss(tmp_path: Path) -> None:
    """strict golden 缺失或 fund-level 未覆盖必须阻断。

    Args:
        tmp_path: pytest 临时目录 fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 strict golden 缺口未阻断时抛出。
    """

    absent = _run_single_artifact(tmp_path / "absent", fund_code="000001", golden_path=None)
    miss_golden = _write_golden(tmp_path / "golden.json", ("000002",))
    miss = _run_single_artifact(tmp_path / "miss", fund_code="000001", golden_path=miss_golden)

    assert "strict_golden_not_configured" in _all_blocker_codes(absent)
    assert "strict_golden_fund_not_covered" in _row_blocker_codes(miss.rows[0])


def test_preflight_reserves_strict_golden_year_and_partial_coverage_codes(tmp_path: Path) -> None:
    """v1 不触发 strict_golden_year_not_covered / partial coverage reserved codes。

    Args:
        tmp_path: pytest 临时目录 fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 reserved codes 被触发时抛出。
    """

    result = _run_single_artifact(tmp_path, fund_code="000001")

    assert "strict_golden_year_not_covered" not in _all_blocker_codes(result)
    assert "strict_golden_partial_coverage" not in _all_blocker_codes(result)


def test_preflight_blocks_fixture_promotion_absence(tmp_path: Path) -> None:
    """未提供 fixture promotion manifest 必须输出 fixture_promotion_absent。

    Args:
        tmp_path: pytest 临时目录 fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 fixture promotion 缺失未阻断时抛出。
    """

    result = _run_single_artifact(tmp_path, fund_code="000001")

    assert "fixture_promotion_absent" in _all_blocker_codes(result)


def test_preflight_outputs_static_disposition_manifest_metadata(tmp_path: Path) -> None:
    """输出 JSON 必须包含静态 manifest metadata。

    Args:
        tmp_path: pytest 临时目录 fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 manifest metadata 缺失时抛出。
    """

    result = _run_single_artifact(tmp_path, fund_code="000001")
    payload = json.loads(result.json_path.read_text(encoding="utf-8"))
    manifest = payload["static_disposition_manifest"]

    assert manifest["schema_version"] == "fund-agent.coverage-disposition.static-current.v1"
    assert manifest["accepted_as_of"] == "2026-05-29"
    assert manifest["source_artifacts"]
    assert manifest["entries"]


def test_preflight_input_schema_rejects_unknown_fields(tmp_path: Path) -> None:
    """preflight input JSON 未知字段必须被拒绝。

    Args:
        tmp_path: pytest 临时目录 fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当未知字段未抛错时抛出。
    """

    input_path = tmp_path / "input.json"
    input_path.write_text(
        json.dumps(
            {
                "schema_version": "fund-agent.golden-readiness-preflight.input.v1",
                "run_id": "unit",
                "source_csv": str(tmp_path / "source.csv"),
                "golden_answer_path": None,
                "fixture_promotion_state_path": None,
                "coverage_disposition_path": None,
                "output_dir": str(tmp_path / "out"),
                "fund_artifacts": [],
                "extra_payload": {},
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="未知字段"):
        run_golden_readiness_preflight(
            source_csv=Path("ignored.csv"),
            output_dir=tmp_path / "ignored",
            run_id="ignored",
            fund_artifacts=(),
            golden_answer_path=None,
            fixture_promotion_state_path=None,
            coverage_disposition_path=None,
            preflight_input_path=input_path,
        )


def test_preflight_json_schema_and_markdown_paths_written(tmp_path: Path) -> None:
    """preflight 必须写出 JSON 和 Markdown。

    Args:
        tmp_path: pytest 临时目录 fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当输出文件缺失或 schema 错误时抛出。
    """

    result = _run_single_artifact(tmp_path, fund_code="000001")
    payload = json.loads(result.json_path.read_text(encoding="utf-8"))

    assert result.json_path.exists()
    assert result.markdown_path.exists()
    assert payload["schema_version"] == "fund-agent.golden-readiness-preflight.v1"
    assert "Overall Verdict" in result.markdown_path.read_text(encoding="utf-8")


def _run_single_artifact(
    tmp_path: Path,
    *,
    fund_code: str,
    snapshot_extra: dict[str, object] | None = None,
    score_extra: dict[str, object] | None = None,
    quality_status: str = "pass",
    golden_path: Path | None | bool = True,
):
    """构造单基金 preflight 测试运行。

    Args:
        tmp_path: 临时目录。
        fund_code: 基金代码。
        snapshot_extra: snapshot 额外字段。
        score_extra: score 额外字段。
        quality_status: quality gate 状态。
        golden_path: golden 路径；True 表示自动生成覆盖当前基金，None 表示不配置。

    Returns:
        preflight result。

    Raises:
        AssertionError: 由调用方断言触发。
    """

    tmp_path.mkdir(parents=True, exist_ok=True)
    source_csv = _write_text(tmp_path / "source.csv", f"fund_code\n{fund_code}\n")
    if golden_path is True:
        actual_golden_path = _write_golden(tmp_path / "golden.json", (fund_code,))
    else:
        actual_golden_path = golden_path
    snapshot = _write_snapshot(
        tmp_path / "snapshot.jsonl", fund_code=fund_code, extra=snapshot_extra or {}
    )
    score = _write_score(tmp_path / "score.json", fund_code=fund_code, extra=score_extra or {})
    quality = _write_quality(tmp_path / "quality.json", fund_code=fund_code, status=quality_status)
    return run_golden_readiness_preflight(
        source_csv=source_csv,
        output_dir=tmp_path / "out",
        run_id="unit",
        fund_artifacts=(
            FundArtifactInput(
                fund_code=fund_code,
                report_year=2024,
                snapshot_path=snapshot,
                score_path=score,
                quality_gate_path=quality,
                raw_disposition="evaluated_carry_forward_candidate",
                preflight_disposition="include_for_later_review",
            ),
        ),
        golden_answer_path=actual_golden_path,
        fixture_promotion_state_path=None,
        coverage_disposition_path=None,
    )


def _write_snapshot(
    path: Path, *, fund_code: str, extra: dict[str, object] | None = None
) -> Path:
    """写入最小 snapshot JSONL。

    Args:
        path: 输出路径。
        fund_code: 基金代码。
        extra: 额外字段。

    Returns:
        输出路径。

    Raises:
        OSError: 写入失败时抛出。
    """

    path.parent.mkdir(parents=True, exist_ok=True)
    row = {
        "fund_code": fund_code,
        "report_year": 2024,
        "fund_name": f"基金{fund_code}",
        "app_category": "国内股票类",
        "classified_fund_type": "active_fund",
        "fallback_used": False,
        "fallback_eligibility": "not_applicable",
        "source_provenance_status": "not_applicable",
    }
    row.update(extra or {})
    path.write_text(json.dumps(row, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def _write_score(
    path: Path, *, fund_code: str, extra: dict[str, object] | None = None
) -> Path:
    """写入最小 score JSON。

    Args:
        path: 输出路径。
        fund_code: 基金代码。
        extra: 额外字段。

    Returns:
        输出路径。

    Raises:
        OSError: 写入失败时抛出。
    """

    payload: dict[str, object] = {
        "fund_scores": [{"fund_code": fund_code, "fund_name": f"基金{fund_code}"}],
        "fund_quality": [
            {
                "fund_code": fund_code,
                "fund_name": f"基金{fund_code}",
                "app_category": "国内股票类",
                "classified_fund_type": "active_fund",
            }
        ],
        "score_applicability_issues": [],
        "correctness": {"status": "available", "coverage_scope": "covered"},
    }
    payload.update(extra or {})
    return _write_json(path, payload)


def _write_quality(path: Path, *, fund_code: str, status: str) -> Path:
    """写入最小 quality gate JSON。

    Args:
        path: 输出路径。
        fund_code: 基金代码。
        status: gate status。

    Returns:
        输出路径。

    Raises:
        OSError: 写入失败时抛出。
    """

    return _write_json(path, {"status": status, "issues": [], "rule_results": [], "fund_code": fund_code})


def _write_golden(path: Path, fund_codes: tuple[str, ...]) -> Path:
    """写入最小 strict golden answer v1 JSON。

    Args:
        path: 输出路径。
        fund_codes: 覆盖基金代码。

    Returns:
        输出路径。

    Raises:
        OSError: 写入失败时抛出。
    """

    return _write_json(
        path,
        {
            "schema_version": "fund-agent.golden-answer.v1",
            "funds": [
                {
                    "fund_code": fund_code,
                    "records": [{"fund_code": fund_code, "field_name": "basic_identity"}],
                }
                for fund_code in fund_codes
            ],
        },
    )


def _write_json(path: Path, payload: dict[str, object]) -> Path:
    """写入 JSON 文件。

    Args:
        path: 输出路径。
        payload: JSON payload。

    Returns:
        输出路径。

    Raises:
        OSError: 写入失败时抛出。
    """

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    return path


def _write_text(path: Path, text: str) -> Path:
    """写入文本文件。

    Args:
        path: 输出路径。
        text: 文本。

    Returns:
        输出路径。

    Raises:
        OSError: 写入失败时抛出。
    """

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def _row_blocker_codes(row) -> set[str]:  # type: ignore[no-untyped-def]
    """读取 row blocker code 集合。

    Args:
        row: readiness row。

    Returns:
        blocker code 集合。

    Raises:
        无显式抛出。
    """

    return {blocker.code for blocker in row.blockers}


def _all_blocker_codes(result) -> set[str]:  # type: ignore[no-untyped-def]
    """读取全局和 row blocker code 集合。

    Args:
        result: preflight result。

    Returns:
        blocker code 集合。

    Raises:
        无显式抛出。
    """

    codes = {blocker.code for blocker in result.global_blockers}
    for row in result.rows:
        codes.update(_row_blocker_codes(row))
    return codes


def test_default_manifest_preserves_110020_raw_disposition() -> None:
    """默认 manifest 必须保留 110020 controller 原始 disposition。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 110020 原始 disposition 改写时抛出。
    """

    manifest = load_default_current_disposition_manifest()
    entry = next(entry for entry in manifest.entries if entry.fund_code == "110020")

    assert entry.raw_disposition == "reviewed_coverage_candidate_input_accepted"
    assert entry.preflight_disposition == "reviewed_coverage_candidate"
