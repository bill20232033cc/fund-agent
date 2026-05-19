"""报告质量 gate 测试。"""

from __future__ import annotations

import json
from pathlib import Path

from fund_agent.fund.quality_gate import (
    GATE_STATUS_BLOCK,
    GATE_STATUS_PASS,
    GATE_STATUS_WARN,
    run_quality_gate,
)


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
    assert any(
        issue.severity == "warn" and issue.field_name == "holdings_snapshot"
        for issue in result.issues
    )
    assert any(issue.severity == "info" and issue.rule_code == "FQ0" for issue in result.issues)


def test_run_quality_gate_blocks_single_fund_p0_failure_even_when_field_aggregate_passes(
    tmp_path: Path,
) -> None:
    """验证单基金 P0 fail 会阻断，即使字段聚合评分为 pass。

    Args:
        tmp_path: pytest 临时目录 fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当单基金阻断 issue 缺失时抛出。
    """

    score_path = tmp_path / "score.json"
    score_path.write_text(
        json.dumps(
            {
                "field_scores": [
                    _field_score("basic_identity", "P0", "pass", 0.9, 0.9),
                ],
                "fund_scores": [
                    _fund_score("004393", "fail", "pass", p0_failed_fields=["basic_identity"]),
                    _fund_score("110011", "pass", "pass"),
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
    assert any(issue.rule_code == "FQ2F" and issue.fund_code == "004393" for issue in result.issues)
    assert payload["issues"][0]["fund_code"] == "004393"
    assert "004393" in markdown


def test_run_quality_gate_blocks_correctness_mismatch_as_fq1(tmp_path: Path) -> None:
    """验证 correctness 明确冲突会触发 FQ1 阻断。

    Args:
        tmp_path: pytest 临时目录 fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 FQ1 未触发时抛出。
    """

    score_path = tmp_path / "score.json"
    score_path.write_text(
        json.dumps(
            {
                "field_scores": [_field_score("classified_fund_type", "P0", "pass", 1.0, 1.0)],
                "fund_scores": [_fund_score("004393", "pass", "pass")],
                "correctness": {
                    "status": "available",
                    "record_results": [
                        {
                            "fund_code": "004393",
                            "field_name": "classified_fund_type",
                            "sub_field": "fund_type",
                            "status": "mismatch",
                            "expected_value": "active_fund",
                            "actual_value": "index_fund",
                            "normalized_expected": "active_fund",
                            "normalized_actual": "index_fund",
                            "reason": "保守 normalize 后不一致。",
                            "confidence": "high",
                            "source": "年报2024 §2 page-5",
                        }
                    ],
                },
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    result = run_quality_gate(score_path=score_path)
    payload = json.loads(result.gate_json_path.read_text(encoding="utf-8"))

    assert result.status == GATE_STATUS_BLOCK
    assert any(issue.rule_code == "FQ1" and issue.fund_code == "004393" for issue in result.issues)
    assert payload["issues"][0]["expected_value"] == "active_fund"


def test_run_quality_gate_keeps_fq0_info_without_golden_answer(tmp_path: Path) -> None:
    """验证无 golden answer 时仍保留 FQ0/info skeleton 且不阻断。

    Args:
        tmp_path: pytest 临时目录 fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 FQ0 skeleton 缺失或错误阻断时抛出。
    """

    score_path = tmp_path / "score.json"
    score_path.write_text(
        json.dumps(
            {
                "field_scores": [_field_score("classified_fund_type", "P0", "pass", 1.0, 1.0)],
                "correctness": {"status": "unavailable"},
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    result = run_quality_gate(score_path=score_path)

    assert result.status == GATE_STATUS_PASS
    assert any(issue.rule_code == "FQ0" and issue.severity == "info" for issue in result.issues)


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


def _fund_score(
    fund_code: str,
    p0_status: str,
    p1_status: str,
    *,
    p0_failed_fields: list[str] | None = None,
    p1_failed_fields: list[str] | None = None,
) -> dict[str, object]:
    """构造测试用单基金评分行。

    Args:
        fund_code: 基金代码。
        p0_status: P0 聚合状态。
        p1_status: P1 聚合状态。
        p0_failed_fields: P0 失败字段。
        p1_failed_fields: P1 失败字段。

    Returns:
        score.json 中的单基金评分对象。

    Raises:
        无显式抛出。
    """

    return {
        "fund_code": fund_code,
        "fund_name": f"测试基金{fund_code}",
        "app_category": "国内股票类",
        "records": 14,
        "p0_status": p0_status,
        "p1_status": p1_status,
        "status": p0_status if p0_status == "fail" else p1_status,
        "p0_failed_fields": p0_failed_fields or [],
        "p1_failed_fields": p1_failed_fields or [],
    }
