"""报告质量 gate 测试。"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

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
                    _field_score("tracking_error", "P1", "fail", 0.0, 0.0),
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
        issue.severity == "warn" and issue.field_name == "tracking_error"
        for issue in result.issues
    )
    assert any(issue.severity == "info" and issue.rule_code == "FQ0" for issue in result.issues)


def test_run_quality_gate_warns_turnover_only_p1_failure_without_fq4(
    tmp_path: Path,
) -> None:
    """验证换手率单项 P1 失败只产生 warning，不触发 FQ4。

    Args:
        tmp_path: pytest 临时目录 fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当换手率 P1 缺口被误判为 block 或 FQ4 时抛出。
    """

    score_path = tmp_path / "score.json"
    score_path.write_text(
        json.dumps(
            {
                "field_scores": [
                    _field_score("basic_identity", "P0", "pass", 1.0, 1.0),
                    _field_score("turnover_rate", "P1", "fail", 0.0, 0.0),
                ],
                "fund_scores": [
                    _fund_score(
                        "004393",
                        "pass",
                        "fail",
                        p1_failed_fields=["turnover_rate"],
                    ),
                ],
                "fund_quality": [
                    _fund_quality(
                        missing_field_rate=0.01,
                        reason="仅 turnover_rate 缺失",
                    ),
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
        issue.rule_code == "FQ2"
        and issue.severity == "warn"
        and issue.field_name == "turnover_rate"
        for issue in result.issues
    )
    assert any(
        issue.rule_code == "FQ2F"
        and issue.severity == "warn"
        and issue.priority == "P1"
        for issue in result.issues
    )
    assert not any(issue.severity == "block" for issue in result.issues)
    assert not any(issue.rule_code == "FQ4" for issue in result.issues)


def test_run_quality_gate_projects_score_applicability_issue_as_fq2f_warn(
    tmp_path: Path,
) -> None:
    """验证债券风险替代 issue 投影为 warn-level FQ2F。

    Args:
        tmp_path: pytest 临时目录 fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当投影规则不符合契约时抛出。
    """

    score_path = tmp_path / "score.json"
    issue = _score_applicability_issue()
    score_path.write_text(
        json.dumps(
            {
                "field_scores": [_field_score("classified_fund_type", "P0", "pass", 1.0, 1.0)],
                "fund_scores": [_fund_score("006597", "pass", "pass")],
                "fund_quality": [
                    _fund_quality(
                        fund_code="006597",
                        app_category="国内债券类",
                        classified_fund_type="bond_fund",
                        preferred_lens_key="bond_fund",
                    )
                ],
                "score_applicability_issues": [issue],
                "correctness": {"status": "unavailable"},
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    result = run_quality_gate(score_path=score_path)
    payload = json.loads(result.gate_json_path.read_text(encoding="utf-8"))
    projected = next(
        issue for issue in result.issues if issue.reason == "bond_risk_evidence_missing"
    )

    assert result.status == GATE_STATUS_WARN
    assert projected.rule_code == "FQ2F"
    assert projected.severity == "warn"
    assert projected.fund_code == "006597"
    assert projected.field_name == "holdings_snapshot"
    assert projected.priority == "P1"
    assert "bond_risk_evidence.v1" in projected.message
    assert any(
        item["rule_code"] == "FQ2F" and item["reason"] == "bond_risk_evidence_missing"
        for item in payload["issues"]
    )


def test_run_quality_gate_rejects_malformed_score_applicability_issue(
    tmp_path: Path,
) -> None:
    """验证 malformed score_applicability_issues fail fast。

    Args:
        tmp_path: pytest 临时目录 fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当非法 issue 未被拒绝时抛出。
    """

    score_path = tmp_path / "score.json"
    malformed_issue = _score_applicability_issue()
    malformed_issue["issue_id"] = "bad-id"
    score_path.write_text(
        json.dumps(
            {
                "field_scores": [_field_score("classified_fund_type", "P0", "pass", 1.0, 1.0)],
                "score_applicability_issues": [malformed_issue],
                "correctness": {"status": "unavailable"},
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="issue_id"):
        run_quality_gate(score_path=score_path)


def test_run_quality_gate_rejects_score_applicability_issue_wrong_report_year_id(
    tmp_path: Path,
) -> None:
    """验证 issue_id 中 report_year 片段错误时 fail fast。

    Args:
        tmp_path: pytest 临时目录 fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当错误年份片段未被拒绝时抛出。
    """

    score_path = tmp_path / "score.json"
    malformed_issue = _score_applicability_issue()
    malformed_issue["issue_id"] = (
        "score-applicability:006597:2023:holdings_snapshot:"
        "bond_risk_evidence_missing:bond_risk_evidence.v1"
    )
    score_path.write_text(
        json.dumps(
            {
                "field_scores": [_field_score("classified_fund_type", "P0", "pass", 1.0, 1.0)],
                "score_applicability_issues": [malformed_issue],
                "correctness": {"status": "unavailable"},
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="issue_id"):
        run_quality_gate(score_path=score_path)


def test_run_quality_gate_treats_missing_score_applicability_issues_as_empty(
    tmp_path: Path,
) -> None:
    """验证旧 score.json 缺少 score_applicability_issues 时保持兼容。

    Args:
        tmp_path: pytest 临时目录 fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当旧 payload 不兼容时抛出。
    """

    score_path = tmp_path / "score.json"
    score_path.write_text(
        json.dumps(
            {
                "field_scores": [_field_score("classified_fund_type", "P0", "pass", 1.0, 1.0)],
                "fund_quality": [_fund_quality(missing_field_rate=0.0)],
                "correctness": {"status": "unavailable"},
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    result = run_quality_gate(score_path=score_path)

    assert result.status == GATE_STATUS_PASS
    assert not any(issue.reason == "bond_risk_evidence_missing" for issue in result.issues)


def test_run_quality_gate_has_no_bond_risk_fq2f_when_score_issue_absent(
    tmp_path: Path,
) -> None:
    """验证七组债券风险证据满足后，quality gate 不凭其它字段生成 bond blocker。

    Args:
        tmp_path: pytest 临时目录 fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 score 未给 issue 仍生成 bond_risk_evidence_missing 时抛出。
    """

    score_path = tmp_path / "score.json"
    score_path.write_text(
        json.dumps(
            {
                "field_scores": [_field_score("classified_fund_type", "P0", "pass", 1.0, 1.0)],
                "fund_scores": [_fund_score("006597", "pass", "pass")],
                "fund_quality": [
                    _fund_quality(
                        fund_code="006597",
                        app_category="国内债券类",
                        classified_fund_type="bond_fund",
                        preferred_lens_key="bond_fund",
                        missing_field_rate=0.0,
                    )
                ],
                "score_applicability_issues": [],
                "correctness": {"status": "unavailable"},
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    result = run_quality_gate(score_path=score_path)

    assert result.status == GATE_STATUS_PASS
    assert not any(
        issue.rule_code == "FQ2F" and issue.reason == "bond_risk_evidence_missing"
        for issue in result.issues
    )


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


def test_run_quality_gate_blocks_composite_index_profile_scalar_mismatch(
    tmp_path: Path,
) -> None:
    """验证复合指数画像 scalar mismatch 通过 FQ1 阻断。

    Args:
        tmp_path: pytest 临时目录 fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 index_profile correctness mismatch 未阻断时抛出。
    """

    score_path = tmp_path / "score.json"
    score_path.write_text(
        json.dumps(
            {
                "field_scores": [_field_score("index_profile", "P1", "pass", 1.0, 1.0)],
                "fund_scores": [_fund_score("004194", "pass", "pass")],
                "correctness": {
                    "status": "available",
                    "record_results": [
                        {
                            "fund_code": "004194",
                            "field_name": "index_profile",
                            "sub_field": "source_tier",
                            "status": "mismatch",
                            "expected_value": "benchmark_context",
                            "actual_value": "missing",
                            "normalized_expected": "benchmark_context",
                            "normalized_actual": "missing",
                            "reason": "保守 normalize 后不一致。",
                            "confidence": "high",
                            "source": "年报2024 §2 page-5 page-5-table-1 benchmark",
                        }
                    ],
                },
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    result = run_quality_gate(score_path=score_path)
    issue = next(issue for issue in result.issues if issue.rule_code == "FQ1")

    assert result.status == GATE_STATUS_BLOCK
    assert issue.fund_code == "004194"
    assert issue.field_name == "index_profile"
    assert "index_profile.source_tier" in issue.message
    assert issue.expected_value == "benchmark_context"
    assert issue.actual_value == "missing"


def test_run_quality_gate_reports_correctness_fund_not_covered_as_fq0_info(
    tmp_path: Path,
) -> None:
    """验证精选池成员缺 golden 覆盖时是 FQ0/info 而非 block。

    Args:
        tmp_path: pytest 临时目录 fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 FQ0 metadata 不符合 P9-S2 契约时抛出。
    """

    score_path = tmp_path / "score.json"
    score_path.write_text(
        json.dumps(
            {
                "field_scores": [_field_score("classified_fund_type", "P0", "pass", 1.0, 1.0)],
                "fund_scores": [_fund_score("000216", "pass", "pass")],
                "correctness": {
                    "status": "available",
                    "golden_answer_path": "reports/golden-answers/golden-answer.json",
                    "coverage_scope": "fund_not_covered",
                    "coverage_reason": "fund_not_covered",
                    "coverage_required": False,
                    "covered_fund_codes": [],
                    "missing_fund_codes": ["000216"],
                    "total_records": 6,
                    "comparable_records": 0,
                    "unavailable_records": 0,
                    "record_results": [],
                },
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    result = run_quality_gate(score_path=score_path)
    payload = json.loads(result.gate_json_path.read_text(encoding="utf-8"))
    issue = next(issue for issue in result.issues if issue.rule_code == "FQ0")

    assert result.status == GATE_STATUS_PASS
    assert issue.severity == "info"
    assert issue.fund_code == "000216"
    assert issue.reason == "fund_not_covered"
    assert issue.coverage_scope == "fund_not_covered"
    assert issue.golden_answer_path == "reports/golden-answers/golden-answer.json"
    assert issue.comparable_records == 0
    assert issue.total_records == 6
    assert payload["issues"][0]["reason"] == "fund_not_covered"


def test_run_quality_gate_reports_no_comparable_fields_as_fq0_info(tmp_path: Path) -> None:
    """验证当前基金有 golden 记录但无可比字段时输出 no_comparable_fields。

    Args:
        tmp_path: pytest 临时目录 fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 no_comparable_fields 未被输出为 FQ0/info 时抛出。
    """

    score_path = tmp_path / "score.json"
    score_path.write_text(
        json.dumps(
            {
                "field_scores": [_field_score("fee_schedule", "P0", "pass", 1.0, 1.0)],
                "fund_scores": [_fund_score("004393", "pass", "pass")],
                "correctness": {
                    "status": "available",
                    "golden_answer_path": "reports/golden-answers/golden-answer.json",
                    "coverage_scope": "no_comparable_fields",
                    "coverage_reason": "no_comparable_fields",
                    "coverage_required": False,
                    "covered_fund_codes": [],
                    "missing_fund_codes": ["004393"],
                    "total_records": 1,
                    "comparable_records": 0,
                    "unavailable_records": 1,
                    "record_results": [
                        {
                            "fund_code": "004393",
                            "field_name": "fee_schedule",
                            "sub_field": "management_fee",
                            "status": "unavailable",
                            "expected_value": "1.20%",
                            "actual_value": None,
                            "normalized_expected": "1.20%",
                            "normalized_actual": None,
                            "reason": "snapshot 未显式暴露该 golden 子字段；不进入 correctness 分母。",
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
    issue = next(issue for issue in result.issues if issue.rule_code == "FQ0")

    assert result.status == GATE_STATUS_PASS
    assert issue.fund_code == "004393"
    assert issue.reason == "no_comparable_fields"
    assert issue.coverage_scope == "no_comparable_fields"
    assert issue.comparable_records == 0
    assert issue.unavailable_records == 1


def test_run_quality_gate_reports_correctness_year_not_covered_as_fq0_info(
    tmp_path: Path,
) -> None:
    """验证当前年份缺 golden 覆盖时是 FQ0/info 而非 FQ1/block。

    Args:
        tmp_path: pytest 临时目录 fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 year_not_covered 被误阻断时抛出。
    """

    score_path = tmp_path / "score.json"
    score_path.write_text(
        json.dumps(
            {
                "field_scores": [_field_score("classified_fund_type", "P0", "pass", 1.0, 1.0)],
                "fund_scores": [_fund_score("004393", "pass", "pass")],
                "correctness": {
                    "status": "available",
                    "golden_answer_path": "reports/golden-answers/golden-answer.json",
                    "coverage_scope": "year_not_covered",
                    "coverage_reason": "year_not_covered",
                    "coverage_required": False,
                    "covered_fund_codes": [],
                    "missing_fund_codes": ["004393"],
                    "total_records": 2,
                    "comparable_records": 0,
                    "mismatched_records": 0,
                    "unavailable_records": 2,
                    "record_results": [
                        {
                            "fund_code": "004393",
                            "report_year": 2024,
                            "field_name": "classified_fund_type",
                            "sub_field": "fund_type",
                            "status": "unavailable",
                            "expected_value": "active_fund",
                            "actual_value": None,
                            "normalized_expected": "active_fund",
                            "normalized_actual": None,
                            "reason": "snapshot 未显式暴露该 golden 子字段；不进入 correctness 分母。",
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
    issue = next(issue for issue in result.issues if issue.rule_code == "FQ0")

    assert result.status == GATE_STATUS_PASS
    assert issue.severity == "info"
    assert issue.fund_code == "004393"
    assert issue.reason == "year_not_covered"
    assert issue.coverage_scope == "year_not_covered"
    assert issue.comparable_records == 0
    assert not any(issue.rule_code == "FQ1" for issue in result.issues)


def test_run_quality_gate_blocks_app_category_conflict_and_lens_mismatch(tmp_path: Path) -> None:
    """验证 App 类别冲突触发 FQ1，模板契约 mismatch 触发 FQ5。

    Args:
        tmp_path: pytest 临时目录 fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 FQ1/FQ5 未触发时抛出。
    """

    score_path = tmp_path / "score.json"
    score_path.write_text(
        json.dumps(
            {
                "field_scores": [_field_score("classified_fund_type", "P0", "pass", 1.0, 1.0)],
                "fund_quality": [
                    _fund_quality(
                        app_category="国内债券类",
                        classified_fund_type="active_fund",
                        app_category_status="conflict",
                        preferred_lens_status="mismatch",
                        preferred_lens_key="active_fund",
                        missing_field_rate=0.0,
                    )
                ],
                "correctness": {"status": "unavailable"},
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    result = run_quality_gate(score_path=score_path)
    payload = json.loads(result.gate_json_path.read_text(encoding="utf-8"))
    rule_codes = {issue.rule_code for issue in result.issues}

    assert result.status == GATE_STATUS_BLOCK
    assert {"FQ1", "FQ5"} <= rule_codes
    fq1_payload = next(issue for issue in payload["issues"] if issue["rule_code"] == "FQ1")
    fq5_payload = next(issue for issue in payload["issues"] if issue["rule_code"] == "FQ5")
    assert fq1_payload["app_category"] == "国内债券类"
    assert fq1_payload["classified_fund_type"] == "active_fund"
    assert fq5_payload["preferred_lens_key"] == "active_fund"
    assert payload["rule_results"][0]["status"] == "mismatch"


def test_run_quality_gate_records_resolved_fq5_without_issue(tmp_path: Path) -> None:
    """验证 resolved FQ5 只进入 rule_results，不产生 issue。

    Args:
        tmp_path: pytest 临时目录 fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: resolved FQ5 被错误记为 issue 时抛出。
    """

    score_path = tmp_path / "score.json"
    score_path.write_text(
        json.dumps(
            {
                "field_scores": [_field_score("classified_fund_type", "P0", "pass", 1.0, 1.0)],
                "fund_quality": [_fund_quality(preferred_lens_status="resolved")],
                "correctness": {"status": "unavailable"},
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    result = run_quality_gate(score_path=score_path)
    payload = json.loads(result.gate_json_path.read_text(encoding="utf-8"))
    markdown = result.gate_markdown_path.read_text(encoding="utf-8")

    assert result.status == GATE_STATUS_PASS
    assert not any(issue.rule_code == "FQ5" for issue in result.issues)
    assert payload["rule_results"][0]["rule_code"] == "FQ5"
    assert payload["rule_results"][0]["status"] == "resolved"
    assert "## Rule Results" in markdown


def test_run_quality_gate_records_not_applicable_fq5_without_issue(tmp_path: Path) -> None:
    """验证 not_applicable FQ5 只解释状态，不触发阻断。

    Args:
        tmp_path: pytest 临时目录 fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: not_applicable FQ5 被错误记为 issue 时抛出。
    """

    score_path = tmp_path / "score.json"
    score_path.write_text(
        json.dumps(
            {
                "field_scores": [_field_score("classified_fund_type", "P0", "pass", 1.0, 1.0)],
                "fund_quality": [
                    _fund_quality(
                        classified_fund_type="",
                        preferred_lens_status="not_applicable",
                        preferred_lens_key="",
                    )
                ],
                "correctness": {"status": "unavailable"},
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    result = run_quality_gate(score_path=score_path)
    payload = json.loads(result.gate_json_path.read_text(encoding="utf-8"))

    assert result.status == GATE_STATUS_PASS
    assert not any(issue.rule_code == "FQ5" for issue in result.issues)
    assert payload["rule_results"][0]["status"] == "not_applicable"


def test_run_quality_gate_keeps_legacy_match_status_compatible(tmp_path: Path) -> None:
    """验证旧 score.json 的 match 状态被规范化为 resolved。

    Args:
        tmp_path: pytest 临时目录 fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: legacy match 未保持兼容时抛出。
    """

    score_path = tmp_path / "score.json"
    score_path.write_text(
        json.dumps(
            {
                "field_scores": [_field_score("classified_fund_type", "P0", "pass", 1.0, 1.0)],
                "fund_quality": [
                    _fund_quality(
                        preferred_lens_status="match",
                        preferred_lens_key="active_equity_fund",
                    )
                ],
                "correctness": {"status": "unavailable"},
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    result = run_quality_gate(score_path=score_path)
    payload = json.loads(result.gate_json_path.read_text(encoding="utf-8"))

    assert result.status == GATE_STATUS_PASS
    assert payload["rule_results"][0]["status"] == "resolved"


def test_run_quality_gate_rejects_unknown_fq5_status(tmp_path: Path) -> None:
    """验证未知 FQ5 状态 fail closed。

    Args:
        tmp_path: pytest 临时目录 fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 未知状态未抛出 `ValueError` 时抛出。
    """

    score_path = tmp_path / "score.json"
    score_path.write_text(
        json.dumps(
            {
                "field_scores": [_field_score("classified_fund_type", "P0", "pass", 1.0, 1.0)],
                "fund_quality": [_fund_quality(preferred_lens_status="unknown")],
                "correctness": {"status": "unavailable"},
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    try:
        run_quality_gate(score_path=score_path)
    except ValueError as exc:
        assert "preferred_lens_status" in str(exc)
    else:
        raise AssertionError("expected ValueError for unknown preferred_lens_status")


def test_run_quality_gate_preserves_fund_type_conflict_reason_in_fq5(tmp_path: Path) -> None:
    """验证 score 派生的多基金类型冲突会进入 FQ5/block 并保留原因。

    Args:
        tmp_path: pytest 临时目录 fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 冲突原因未进入 FQ5 issue 时抛出。
    """

    score_path = tmp_path / "score.json"
    score_path.write_text(
        json.dumps(
            {
                "field_scores": [_field_score("classified_fund_type", "P0", "pass", 1.0, 1.0)],
                "fund_quality": [
                    _fund_quality(
                        classified_fund_type="",
                        preferred_lens_status="mismatch",
                        preferred_lens_key="",
                        reason="classified_fund_type 存在冲突值：active_fund, bond_fund",
                    )
                ],
                "correctness": {"status": "unavailable"},
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    result = run_quality_gate(score_path=score_path)
    fq5_issue = next(issue for issue in result.issues if issue.rule_code == "FQ5")

    assert result.status == GATE_STATUS_BLOCK
    assert "active_fund, bond_fund" in fq5_issue.message


def test_run_quality_gate_warns_and_blocks_fq4_missing_rate_thresholds(tmp_path: Path) -> None:
    """验证 FQ4 按缺失率阈值触发 warn/block。

    Args:
        tmp_path: pytest 临时目录 fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 FQ4 阈值不符合契约时抛出。
    """

    score_path = tmp_path / "score.json"
    score_path.write_text(
        json.dumps(
            {
                "field_scores": [_field_score("classified_fund_type", "P0", "pass", 1.0, 1.0)],
                "fund_quality": [
                    _fund_quality(fund_code="000001", missing_field_rate=0.20),
                    _fund_quality(fund_code="000002", missing_field_rate=0.35),
                ],
                "correctness": {"status": "unavailable"},
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    result = run_quality_gate(score_path=score_path)
    fq4_by_fund = {issue.fund_code: issue for issue in result.issues if issue.rule_code == "FQ4"}

    assert result.status == GATE_STATUS_BLOCK
    assert fq4_by_fund["000001"].severity == "warn"
    assert fq4_by_fund["000001"].observed_rate == 0.20
    assert fq4_by_fund["000001"].threshold == 0.20
    assert fq4_by_fund["000002"].severity == "block"
    assert fq4_by_fund["000002"].observed_rate == 0.35
    assert fq4_by_fund["000002"].threshold == 0.35


def test_run_quality_gate_preserves_fq4_thresholds_with_score_applicability_issue(
    tmp_path: Path,
) -> None:
    """验证 score applicability 投影不改变 FQ4 阈值。

    Args:
        tmp_path: pytest 临时目录 fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 FQ4 阈值被替代 issue 改写时抛出。
    """

    score_path = tmp_path / "score.json"
    score_path.write_text(
        json.dumps(
            {
                "field_scores": [_field_score("classified_fund_type", "P0", "pass", 1.0, 1.0)],
                "fund_quality": [
                    _fund_quality(
                        fund_code="006597",
                        app_category="国内债券类",
                        classified_fund_type="bond_fund",
                        preferred_lens_key="bond_fund",
                        missing_field_rate=0.35,
                    )
                ],
                "score_applicability_issues": [_score_applicability_issue()],
                "correctness": {"status": "unavailable"},
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    result = run_quality_gate(score_path=score_path)
    fq4_issue = next(issue for issue in result.issues if issue.rule_code == "FQ4")

    assert result.status == GATE_STATUS_BLOCK
    assert fq4_issue.severity == "block"
    assert fq4_issue.threshold == 0.35
    assert any(issue.reason == "bond_risk_evidence_missing" for issue in result.issues)


def test_run_quality_gate_synthetic_006597_like_bond_exclusion_does_not_mis_pass(
    tmp_path: Path,
) -> None:
    """验证 006597-like 债券样本不会因 holdings 分母排除而误 pass。

    Args:
        tmp_path: pytest 临时目录 fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当替代风险 issue 缺失导致误 pass 时抛出。
    """

    score_path = tmp_path / "score.json"
    score_path.write_text(
        json.dumps(
            {
                "field_scores": [_field_score("classified_fund_type", "P0", "pass", 1.0, 1.0)],
                "fund_scores": [_fund_score("006597", "pass", "pass")],
                "fund_quality": [
                    _fund_quality(
                        fund_code="006597",
                        app_category="国内债券类",
                        classified_fund_type="bond_fund",
                        preferred_lens_key="bond_fund",
                        missing_field_rate=0.0,
                    )
                ],
                "field_applicability_decisions": [
                    {
                        "fund_code": "006597",
                        "report_year": "2024",
                        "field_name": "holdings_snapshot",
                        "classified_fund_type": "bond_fund",
                        "applicability_status": "not_applicable_replaced",
                        "reason_code": "not_applicable_to_bond_fund_equity_holdings",
                        "replacement_field_name": "bond_risk_evidence",
                        "contract_id": "bond_risk_evidence.v1",
                        "denominator_effect": "excluded_with_replacement_issue",
                        "raw_total_field_count": 2,
                        "raw_missing_field_count": 1,
                        "raw_missing_field_rate": 0.5,
                        "applicable_total_field_count": 1,
                        "applicable_missing_field_count": 0,
                        "applicable_missing_field_rate": 0.0,
                        "excluded_non_applicable_fields": ["holdings_snapshot"],
                        "replacement_issue_ids": [
                            "score-applicability:006597:2024:holdings_snapshot:bond_risk_evidence_missing:bond_risk_evidence.v1"
                        ],
                    }
                ],
                "score_applicability_issues": [_score_applicability_issue()],
                "correctness": {"status": "unavailable"},
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    result = run_quality_gate(score_path=score_path)

    assert result.status == GATE_STATUS_WARN
    assert any(
        issue.rule_code == "FQ2F"
        and issue.reason == "bond_risk_evidence_missing"
        and issue.fund_code == "006597"
        for issue in result.issues
    )
    assert not any(issue.rule_code == "FQ4" for issue in result.issues)


def test_run_quality_gate_rejects_unknown_unavailable_coverage_scope(tmp_path: Path) -> None:
    """验证 unavailable correctness 携带未知 coverage_scope 时 fail closed。

    Args:
        tmp_path: pytest 临时目录 fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 未知 coverage_scope 未抛出 ValueError 时抛出。
    """

    score_path = tmp_path / "score.json"
    score_path.write_text(
        json.dumps(
            {
                "field_scores": [_field_score("classified_fund_type", "P0", "pass", 1.0, 1.0)],
                "correctness": {
                    "status": "unavailable",
                    "coverage_scope": "bogus_scope",
                    "coverage_reason": "not_configured",
                },
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    try:
        run_quality_gate(score_path=score_path)
    except ValueError as exc:
        assert "coverage_scope" in str(exc)
    else:
        raise AssertionError("expected ValueError for unknown unavailable coverage_scope")


def test_run_quality_gate_rejects_unknown_unavailable_coverage_reason(tmp_path: Path) -> None:
    """验证 unavailable correctness 携带未知 coverage_reason 时 fail closed。

    Args:
        tmp_path: pytest 临时目录 fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 未知 coverage_reason 未抛出 ValueError 时抛出。
    """

    score_path = tmp_path / "score.json"
    score_path.write_text(
        json.dumps(
            {
                "field_scores": [_field_score("classified_fund_type", "P0", "pass", 1.0, 1.0)],
                "correctness": {
                    "status": "unavailable",
                    "coverage_scope": "not_configured",
                    "coverage_reason": "bogus_reason",
                },
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    try:
        run_quality_gate(score_path=score_path)
    except ValueError as exc:
        assert "coverage_reason" in str(exc)
    else:
        raise AssertionError("expected ValueError for unknown unavailable coverage_reason")


def test_run_quality_gate_keeps_old_score_without_fund_quality_compatible(tmp_path: Path) -> None:
    """验证旧 score.json 缺少 fund_quality 时 gate 不 fatal。

    Args:
        tmp_path: pytest 临时目录 fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当兼容路径异常或缺少 info issue 时抛出。
    """

    score_path = tmp_path / "score.json"
    score_path.write_text(
        json.dumps(
            {
                "field_scores": [_field_score("classified_fund_type", "P0", "pass", 1.0, 1.0)],
                "correctness": {
                    "status": "unavailable",
                    "coverage_scope": "not_configured",
                    "coverage_reason": "not_configured",
                    "missing_fund_codes": ["004393"],
                    "total_records": 0,
                    "comparable_records": 0,
                    "unavailable_records": 0,
                },
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    result = run_quality_gate(score_path=score_path)

    assert result.status == GATE_STATUS_PASS
    assert any("fund_quality" in issue.message for issue in result.issues)


def test_run_quality_gate_rejects_bool_field_score_numeric_rates(tmp_path: Path) -> None:
    """验证 field_scores 数值字段拒绝 bool。

    Args:
        tmp_path: pytest 临时目录 fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 bool 数值字段未被拒绝时抛出。
    """

    score_path = tmp_path / "score.json"
    score_path.write_text(
        json.dumps(
            {
                "field_scores": [
                    _field_score("classified_fund_type", "P0", "pass", True, 1.0),
                ],
                "correctness": {"status": "unavailable"},
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="field_scores\\[0\\]\\.coverage_rate 必须是数值"):
        run_quality_gate(score_path=score_path)


def test_run_quality_gate_rejects_bool_fund_quality_numeric_rates(tmp_path: Path) -> None:
    """验证 fund_quality 数值字段拒绝 bool。

    Args:
        tmp_path: pytest 临时目录 fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 bool 数值字段未被拒绝时抛出。
    """

    score_path = tmp_path / "score.json"
    score_path.write_text(
        json.dumps(
            {
                "field_scores": [_field_score("classified_fund_type", "P0", "pass", 1.0, 1.0)],
                "fund_quality": [
                    _fund_quality(missing_field_rate=True),
                ],
                "correctness": {"status": "unavailable"},
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="fund_quality\\[0\\]\\.missing_field_rate 必须是数值"):
        run_quality_gate(score_path=score_path)


def test_run_quality_gate_blocks_failed_funds_as_fq6(tmp_path: Path) -> None:
    """验证 failed_funds 会触发 FQ6 阻断。

    Args:
        tmp_path: pytest 临时目录 fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当失败基金未触发阻断时抛出。
    """

    score_path = tmp_path / "score.json"
    score_path.write_text(
        json.dumps(
            {
                "field_scores": [_field_score("classified_fund_type", "P0", "pass", 1.0, 1.0)],
                "failed_funds": [
                    {
                        "fund_code": "000001",
                        "fund_name": "失败基金",
                        "app_category": "国内股票类",
                        "report_year": 2024,
                        "error_type": "RuntimeError",
                        "error_message": "fixture failure",
                    }
                ],
                "correctness": {"status": "unavailable"},
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    result = run_quality_gate(score_path=score_path)
    payload = json.loads(result.gate_json_path.read_text(encoding="utf-8"))
    fq6_issue = next(issue for issue in result.issues if issue.rule_code == "FQ6")

    assert result.status == GATE_STATUS_BLOCK
    assert fq6_issue.fund_code == "000001"
    assert fq6_issue.error_type == "RuntimeError"
    assert any(issue["rule_code"] == "FQ6" for issue in payload["issues"])


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
    issue = next(issue for issue in result.issues if issue.rule_code == "FQ0")
    assert issue.severity == "info"
    assert issue.reason == "not_configured"
    assert issue.coverage_scope == "not_configured"


def test_run_quality_gate_reports_not_configured_with_fund_metadata(tmp_path: Path) -> None:
    """验证新 score 的 not_configured FQ0/info 带 fund-scoped metadata。

    Args:
        tmp_path: pytest 临时目录 fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 metadata 未进入 FQ0 issue 时抛出。
    """

    score_path = tmp_path / "score.json"
    score_path.write_text(
        json.dumps(
            {
                "field_scores": [_field_score("classified_fund_type", "P0", "pass", 1.0, 1.0)],
                "correctness": {
                    "status": "unavailable",
                    "coverage_scope": "not_configured",
                    "coverage_reason": "not_configured",
                    "missing_fund_codes": ["004393"],
                    "total_records": 0,
                    "comparable_records": 0,
                    "unavailable_records": 0,
                },
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    result = run_quality_gate(score_path=score_path)
    issue = next(issue for issue in result.issues if issue.rule_code == "FQ0")

    assert result.status == GATE_STATUS_PASS
    assert issue.fund_code == "004393"
    assert issue.reason == "not_configured"
    assert issue.coverage_scope == "not_configured"
    assert issue.comparable_records == 0


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


def _fund_quality(
    *,
    fund_code: str = "004393",
    app_category: str = "国内股票类",
    classified_fund_type: str = "active_fund",
    app_category_status: str = "match",
    preferred_lens_status: str = "resolved",
    preferred_lens_key: str = "active_fund",
    missing_field_rate: float = 0.0,
    reason: str = "测试原因",
) -> dict[str, object]:
    """构造测试用基金质量派生行。

    Args:
        fund_code: 基金代码。
        app_category: App 类别。
        classified_fund_type: 系统基金类型。
        app_category_status: App 类别状态。
        preferred_lens_status: preferred_lens 状态。
        preferred_lens_key: preferred_lens key。
        missing_field_rate: 缺失字段比例。
        reason: 基金质量原因。

    Returns:
        score.json 中的 fund_quality 对象。

    Raises:
        无显式抛出。
    """

    return {
        "fund_code": fund_code,
        "fund_name": f"测试基金{fund_code}",
        "app_category": app_category,
        "classified_fund_type": classified_fund_type,
        "app_category_status": app_category_status,
        "preferred_lens_status": preferred_lens_status,
        "preferred_lens_key": preferred_lens_key,
        "missing_field_count": int(missing_field_rate * 100),
        "total_field_count": 100,
        "missing_field_rate": missing_field_rate,
        "missing_p0_fields": [],
        "missing_p1_fields": [],
        "reason": reason,
    }


def _score_applicability_issue() -> dict[str, object]:
    """构造测试用 score applicability issue。

    Args:
        无。

    Returns:
        score.json 中的 score_applicability_issues 对象。

    Raises:
        无显式抛出。
    """

    return {
        "issue_id": (
            "score-applicability:006597:2024:holdings_snapshot:"
            "bond_risk_evidence_missing:bond_risk_evidence.v1"
        ),
        "issue_code": "bond_risk_evidence_missing",
        "severity": "warn",
        "fund_code": "006597",
        "report_year": "2024",
        "field_name": "holdings_snapshot",
        "classified_fund_type": "bond_fund",
        "replacement_field_name": "bond_risk_evidence",
        "contract_id": "bond_risk_evidence.v1",
        "priority": "P1",
        "message": (
            "基金 `006597` 为债券基金，权益持仓型 holdings_snapshot 不进入股票持仓分母；"
            "但 `bond_risk_evidence.v1` 尚无已复核债券风险证据。"
        ),
        "baseline_blocking": True,
        "rule_code_hint": "FQ2F",
        "denominator_excluded_fields": ["holdings_snapshot"],
        "required_evidence_groups": [
            "duration_rate_risk",
            "credit_risk",
            "leverage_liquidity",
            "asset_allocation_holdings_mix",
            "drawdown_stress",
            "redemption_share_pressure",
            "convertible_bond_equity_exposure",
        ],
        "missing_evidence_groups": [
            "duration_rate_risk",
            "credit_risk",
            "leverage_liquidity",
            "asset_allocation_holdings_mix",
            "drawdown_stress",
            "redemption_share_pressure",
            "convertible_bond_equity_exposure",
        ],
    }
