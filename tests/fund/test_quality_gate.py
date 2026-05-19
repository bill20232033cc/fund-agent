"""报告质量 gate 测试。"""

from __future__ import annotations

import json
from pathlib import Path

from fund_agent.fund.quality_gate import GATE_STATUS_BLOCK, GATE_STATUS_WARN, run_quality_gate


def test_run_quality_gate_blocks_failed_p0_fields(tmp_path: Path) -> None:
    """验证 P0 字段 fail 会阻断报告质量 gate。

    Args:
        tmp_path: pytest 临时目录 fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 P0 fail 未触发阻断时抛出。
    """

    score_path = tmp_path / "score.json"
    score_path.write_text(
        json.dumps(
            {
                "field_scores": [
                    _field_score("fee_schedule", "P0", "fail", 0.0, 0.0),
                    _field_score("holder_structure", "P1", "pass", 1.0, 1.0),
                ],
                "correctness": {"status": "not_implemented"},
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    result = run_quality_gate(score_path=score_path)
    payload = json.loads(result.gate_json_path.read_text(encoding="utf-8"))
    markdown = result.gate_markdown_path.read_text(encoding="utf-8")

    assert result.status == GATE_STATUS_BLOCK
    assert payload["status"] == GATE_STATUS_BLOCK
    assert {issue.rule_code for issue in result.issues} >= {"FQ0", "FQ2", "FQ3"}
    assert "fee_schedule" in markdown


def test_run_quality_gate_warns_failed_p1_without_blocking(tmp_path: Path) -> None:
    """验证只有 P1 字段 fail 时 gate 为 warn。

    Args:
        tmp_path: pytest 临时目录 fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 P1 fail 被错误阻断时抛出。
    """

    score_path = tmp_path / "score.json"
    score_path.write_text(
        json.dumps(
            {
                "field_scores": [
                    _field_score("basic_identity", "P0", "pass", 1.0, 1.0),
                    _field_score("holdings_snapshot", "P1", "fail", 0.0, 0.0),
                ],
                "correctness": {"status": "not_implemented"},
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    result = run_quality_gate(score_path=score_path)

    assert result.status == GATE_STATUS_WARN
    assert any(issue.severity == "warn" and issue.field_name == "holdings_snapshot" for issue in result.issues)
    assert any(issue.severity == "info" and issue.rule_code == "FQ0" for issue in result.issues)


def _field_score(
    field_name: str,
    priority: str,
    status: str,
    coverage_rate: float,
    traceability_rate: float,
) -> dict[str, object]:
    """构造测试用字段评分行。

    Args:
        field_name: 字段名。
        priority: 优先级。
        status: 字段评分状态。
        coverage_rate: coverage 比率。
        traceability_rate: traceability 比率。

    Returns:
        score.json 中的字段评分对象。

    Raises:
        无显式抛出。
    """

    return {
        "field_group": "fixture",
        "field_name": field_name,
        "priority": priority,
        "records": 1,
        "covered_records": 1 if coverage_rate else 0,
        "traceable_records": 1 if traceability_rate else 0,
        "coverage_rate": coverage_rate,
        "traceability_rate": traceability_rate,
        "status": status,
    }
