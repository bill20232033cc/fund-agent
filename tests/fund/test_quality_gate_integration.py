"""单基金 quality gate 集成 adapter 测试。"""

from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path

from fund_agent.fund.quality_gate_integration import (
    check_quality_gate_fund_membership,
    run_quality_gate_for_bundle,
)
from tests.services.test_fund_analysis_service import _bundle


def test_run_quality_gate_for_bundle_writes_score_and_gate_without_reextracting(
    tmp_path: Path,
) -> None:
    """验证 adapter 基于已抽取 bundle 生成 score/gate 产物。

    Args:
        tmp_path: pytest 临时目录 fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 adapter 未写出预期产物时抛出。
    """

    source_csv = _source_csv(tmp_path, "110011")
    output_dir = tmp_path / "gate-run"

    result = run_quality_gate_for_bundle(
        bundle=_bundle(),
        source_csv=source_csv,
        output_dir=output_dir,
        run_id="fixture-run",
        golden_answer_path=None,
    )

    score_payload = json.loads(result.score_result.score_json_path.read_text(encoding="utf-8"))

    assert result.not_run_reason is None
    assert result.snapshot_path.exists()
    assert result.score_result is not None
    assert result.quality_gate_result is not None
    assert result.quality_gate_result.gate_json_path.exists()
    assert score_payload["fund_scores"][0]["fund_code"] == "110011"
    assert score_payload["golden_set"]["records"] == []
    assert score_payload["correctness"]["coverage_scope"] == "not_configured"


def test_run_quality_gate_for_bundle_selected_member_without_golden_is_fq0_info(
    tmp_path: Path,
) -> None:
    """验证精选池成员缺 golden 覆盖时 gate 已运行且只记录 FQ0/info。

    Args:
        tmp_path: pytest 临时目录 fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当缺 golden 被误判为 not-run 或 block 时抛出。
    """

    source_csv = _source_csv(tmp_path, "110011")
    golden_path = _golden_answer_json(tmp_path, fund_code="004393")

    result = run_quality_gate_for_bundle(
        bundle=_bundle(),
        source_csv=source_csv,
        output_dir=tmp_path / "gate-run",
        run_id="fixture-run",
        golden_answer_path=golden_path,
    )

    score_payload = json.loads(result.score_result.score_json_path.read_text(encoding="utf-8"))
    fq0_issue = next(
        issue for issue in result.quality_gate_result.issues if issue.rule_code == "FQ0"
    )

    assert result.not_run_reason is None
    assert result.quality_gate_result.status == "pass"
    assert score_payload["correctness"]["coverage_scope"] == "fund_not_covered"
    assert fq0_issue.fund_code == "110011"
    assert fq0_issue.reason == "fund_not_covered"
    assert fq0_issue.coverage_scope == "fund_not_covered"


def test_run_quality_gate_for_bundle_uses_bundle_report_year_for_correctness(
    tmp_path: Path,
) -> None:
    """验证 2025 bundle 不会被 2024 golden answer 误判为 FQ1 mismatch。

    Args:
        tmp_path: pytest 临时目录 fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 report_year 未从 bundle 传播到 correctness 时抛出。
    """

    source_csv = _source_csv(tmp_path, "110011")
    golden_path = _golden_answer_json(tmp_path, fund_code="110011")

    result = run_quality_gate_for_bundle(
        bundle=replace(_bundle(), report_year=2025),
        source_csv=source_csv,
        output_dir=tmp_path / "gate-run",
        run_id="fixture-run",
        golden_answer_path=golden_path,
    )

    score_payload = json.loads(result.score_result.score_json_path.read_text(encoding="utf-8"))
    fq0_issue = next(
        issue for issue in result.quality_gate_result.issues if issue.rule_code == "FQ0"
    )

    assert result.not_run_reason is None
    assert result.quality_gate_result.status == "pass"
    assert score_payload["correctness"]["coverage_scope"] == "year_not_covered"
    assert score_payload["correctness"]["comparable_records"] == 0
    assert score_payload["correctness"]["mismatched_records"] == 0
    assert fq0_issue.reason == "year_not_covered"
    assert fq0_issue.coverage_scope == "year_not_covered"
    assert not any(issue.rule_code == "FQ1" for issue in result.quality_gate_result.issues)


def test_run_quality_gate_for_bundle_not_run_when_fund_absent(tmp_path: Path) -> None:
    """验证基金不在精选池时不伪造 App 类别且不写运行产物。

    Args:
        tmp_path: pytest 临时目录 fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 adapter 错误继续运行时抛出。
    """

    source_csv = _source_csv(tmp_path, "004393")
    output_dir = tmp_path / "gate-run"

    result = run_quality_gate_for_bundle(
        bundle=_bundle(),
        source_csv=source_csv,
        output_dir=output_dir,
        run_id="fixture-run",
        golden_answer_path=None,
    )

    assert result.quality_gate_result is None
    assert result.score_result is None
    assert result.not_run_reason == "fund_code `110011` not found in quality gate source csv"
    assert not output_dir.exists()


def test_check_quality_gate_fund_membership_reports_missing_csv(tmp_path: Path) -> None:
    """验证抽取前成员检查能区分精选池 CSV 缺失。

    Args:
        tmp_path: pytest 临时目录 fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当缺失 CSV 被误报为通用格式错误时抛出。
    """

    not_run_reason = check_quality_gate_fund_membership(
        source_csv=tmp_path / "missing.csv",
        fund_code="110011",
    )

    assert not_run_reason == "quality gate source csv not found"


def _source_csv(tmp_path: Path, fund_code: str) -> Path:
    """写入测试用精选基金池 CSV。

    Args:
        tmp_path: pytest 临时目录 fixture。
        fund_code: CSV 中的基金代码。

    Returns:
        CSV 路径。

    Raises:
        OSError: 写入失败时抛出。
    """

    source_csv = tmp_path / "selected.csv"
    source_csv.write_text(
        f"基金名称,基金代码,类别\n测试基金,{fund_code},国内股票类\n",
        encoding="utf-8",
    )
    return source_csv


def _bundle_with_code(fund_code: str):
    """构造指定基金代码的结构化数据包。

    Args:
        fund_code: 基金代码。

    Returns:
        结构化数据包。

    Raises:
        无显式抛出。
    """

    return replace(_bundle(), fund_code=fund_code)


def _golden_answer_json(tmp_path: Path, *, fund_code: str) -> Path:
    """写入测试用 strict golden answer JSON。

    Args:
        tmp_path: pytest 临时目录 fixture。
        fund_code: golden answer 覆盖的基金代码。

    Returns:
        strict JSON 路径。

    Raises:
        OSError: 写入失败时抛出。
    """

    records = [
        {
            "fund_code": fund_code,
            "report_year": 2024,
            "field_name": "classified_fund_type",
            "sub_field": "fund_type",
            "expected_value": "active_fund",
            "confidence": "high",
            "source": "年报2024 §2 page-5",
        }
    ]
    path = tmp_path / "golden-answer.json"
    path.write_text(
        json.dumps(
            {
                "schema_version": "fund-agent.golden-answer.v1",
                "source_markdown": "fixture.md",
                "fund_count": 1,
                "record_count": len(records),
                "funds": [
                    {
                        "fund_code": fund_code,
                        "report_year": 2024,
                        "title": "测试基金（国内股票类）",
                        "records": records,
                        "skipped_fields": [],
                    }
                ],
                "records": records,
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    return path
