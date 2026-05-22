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
