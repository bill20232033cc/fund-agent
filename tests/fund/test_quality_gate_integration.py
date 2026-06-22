"""单基金 quality gate 集成 adapter 测试。"""

from __future__ import annotations

import ast
import json
from dataclasses import replace
from pathlib import Path

import pytest

from fund_agent.fund.evidence_confirm_production import (
    EvidenceConfirmProductionSummary,
    not_run_evidence_confirm_summary,
)
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


def test_quality_gate_integration_without_summary_is_unchanged(tmp_path: Path) -> None:
    """验证未传 Evidence Confirm 摘要时保持既有 FQ-only 行为。

    Args:
        tmp_path: pytest 临时目录 fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当默认路径出现 ECQ issue 时抛出。
    """

    result = run_quality_gate_for_bundle(
        bundle=_bundle(),
        source_csv=_source_csv(tmp_path, "110011"),
        output_dir=tmp_path / "gate-run",
        run_id="fixture-run",
        golden_answer_path=None,
    )

    payload = json.loads(result.quality_gate_result.gate_json_path.read_text(encoding="utf-8"))

    assert not any(issue.rule_code.startswith("ECQ") for issue in result.quality_gate_result.issues)
    assert not any(issue["rule_code"].startswith("ECQ") for issue in payload["issues"])


def test_quality_gate_integration_explicit_summary_none_produces_no_ecq_issues(
    tmp_path: Path,
) -> None:
    """验证显式传入 summary=None 时不会生成 ECQ issue。

    Args:
        tmp_path: pytest 临时目录 fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 summary absent 路径出现 ECQ issue 时抛出。
    """

    result = run_quality_gate_for_bundle(
        bundle=_bundle(),
        source_csv=_source_csv(tmp_path, "110011"),
        output_dir=tmp_path / "gate-run",
        run_id="fixture-run",
        golden_answer_path=None,
        evidence_confirm_summary=None,
    )

    payload = json.loads(result.quality_gate_result.gate_json_path.read_text(encoding="utf-8"))

    assert not any(issue.rule_code.startswith("ECQ") for issue in result.quality_gate_result.issues)
    assert not any(issue["rule_code"].startswith("ECQ") for issue in payload["issues"])


def test_quality_gate_integration_maps_evidence_confirm_fail_to_ecq2_block(
    tmp_path: Path,
) -> None:
    """验证 deterministic fail + block policy 投影为稳定 ECQ2/block issue。

    Args:
        tmp_path: pytest 临时目录 fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 ECQ2 投影不符合契约时抛出。
    """

    result = run_quality_gate_for_bundle(
        bundle=_bundle(),
        source_csv=_source_csv(tmp_path, "110011"),
        output_dir=tmp_path / "gate-run",
        run_id="fixture-run",
        golden_answer_path=None,
        evidence_confirm_summary=_summary(status="fail", deterministic_status="fail"),
    )

    payload = json.loads(result.quality_gate_result.gate_json_path.read_text(encoding="utf-8"))
    ecq2 = next(issue for issue in result.quality_gate_result.issues if issue.rule_code == "ECQ2")

    assert ecq2.severity == "block"
    assert ecq2.reason == "deterministic_fail_1"
    assert ecq2.issue_id == "evidence-confirm:110011:2024:ECQ2:deterministic_fail_1"
    assert any(issue["issue_id"] == ecq2.issue_id for issue in payload["issues"])
    assert "ECQ2" in result.quality_gate_result.gate_markdown_path.read_text(encoding="utf-8")


def test_quality_gate_integration_maps_evidence_confirm_fail_warn_policy_to_ecq2_warn(
    tmp_path: Path,
) -> None:
    """验证 deterministic fail + warn policy 投影为 ECQ2/warn。

    Args:
        tmp_path: pytest 临时目录 fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 warn policy fail 路径被误投影时抛出。
    """

    result = run_quality_gate_for_bundle(
        bundle=_bundle(),
        source_csv=_source_csv(tmp_path, "110011"),
        output_dir=tmp_path / "gate-run",
        run_id="fixture-run",
        golden_answer_path=None,
        evidence_confirm_summary=_summary(
            policy="warn",
            status="fail",
            deterministic_status="fail",
        ),
    )

    ecq2 = next(issue for issue in result.quality_gate_result.issues if issue.rule_code == "ECQ2")

    assert result.quality_gate_result.status == "warn"
    assert ecq2.severity == "warn"
    assert ecq2.reason == "deterministic_fail_1"


def test_quality_gate_integration_ecq2_block_changes_gate_status_to_block(
    tmp_path: Path,
) -> None:
    """验证合并 ECQ2/block 后按既有聚合语义把 gate 升为 block。

    Args:
        tmp_path: pytest 临时目录 fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 ECQ2/block 未影响聚合状态时抛出。
    """

    result = run_quality_gate_for_bundle(
        bundle=_bundle(),
        source_csv=_source_csv(tmp_path, "110011"),
        output_dir=tmp_path / "gate-run",
        run_id="fixture-run",
        golden_answer_path=None,
        evidence_confirm_summary=_summary(status="fail", deterministic_status="fail"),
    )

    payload = json.loads(result.quality_gate_result.gate_json_path.read_text(encoding="utf-8"))

    assert result.quality_gate_result.status == "block"
    assert payload["status"] == "block"


def test_quality_gate_integration_maps_evidence_confirm_warn_to_ecq3_warn(
    tmp_path: Path,
) -> None:
    """验证 deterministic warn 投影为 ECQ3/warn。

    Args:
        tmp_path: pytest 临时目录 fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 warning 摘要未生成 ECQ3/warn 时抛出。
    """

    result = run_quality_gate_for_bundle(
        bundle=_bundle(),
        source_csv=_source_csv(tmp_path, "110011"),
        output_dir=tmp_path / "gate-run",
        run_id="fixture-run",
        golden_answer_path=None,
        evidence_confirm_summary=_summary(status="warn", deterministic_status="warn"),
    )

    ecq3 = next(issue for issue in result.quality_gate_result.issues if issue.rule_code == "ECQ3")

    assert result.quality_gate_result.status == "warn"
    assert ecq3.severity == "warn"
    assert ecq3.reason == "deterministic_warn_1"


def test_quality_gate_integration_maps_semantic_fail_to_ecq4_block(
    tmp_path: Path,
) -> None:
    """验证 injected semantic fail + block policy 投影为 ECQ4/block。

    Args:
        tmp_path: pytest 临时目录 fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 semantic fail 未生成 ECQ4/block 时抛出。
    """

    result = run_quality_gate_for_bundle(
        bundle=_bundle(),
        source_csv=_source_csv(tmp_path, "110011"),
        output_dir=tmp_path / "gate-run",
        run_id="fixture-run",
        golden_answer_path=None,
        evidence_confirm_summary=_summary(
            status="fail",
            deterministic_status="pass",
            semantic_status="fail",
        ),
    )

    ecq4 = next(issue for issue in result.quality_gate_result.issues if issue.rule_code == "ECQ4")

    assert result.quality_gate_result.status == "block"
    assert ecq4.severity == "block"
    assert ecq4.reason == "semantic_fail"
    assert ecq4.issue_id == "evidence-confirm:110011:2024:ECQ4:semantic_fail"


def test_quality_gate_integration_maps_semantic_fail_warn_policy_to_ecq4_warn(
    tmp_path: Path,
) -> None:
    """验证 injected semantic fail + warn policy 投影为 ECQ4/warn。

    Args:
        tmp_path: pytest 临时目录 fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 warn policy semantic fail 被误投影时抛出。
    """

    result = run_quality_gate_for_bundle(
        bundle=_bundle(),
        source_csv=_source_csv(tmp_path, "110011"),
        output_dir=tmp_path / "gate-run",
        run_id="fixture-run",
        golden_answer_path=None,
        evidence_confirm_summary=_summary(
            policy="warn",
            status="fail",
            deterministic_status="pass",
            semantic_status="fail",
        ),
    )

    ecq4 = next(issue for issue in result.quality_gate_result.issues if issue.rule_code == "ECQ4")

    assert result.quality_gate_result.status == "warn"
    assert ecq4.severity == "warn"
    assert ecq4.reason == "semantic_fail"


def test_quality_gate_integration_deterministic_fail_blocks_even_when_semantic_passes(
    tmp_path: Path,
) -> None:
    """验证 deterministic V2 fail 不会被 semantic pass 覆盖。

    Args:
        tmp_path: pytest 临时目录 fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 semantic pass 掩盖 deterministic fail 时抛出。
    """

    result = run_quality_gate_for_bundle(
        bundle=_bundle(),
        source_csv=_source_csv(tmp_path, "110011"),
        output_dir=tmp_path / "gate-run",
        run_id="fixture-run",
        golden_answer_path=None,
        evidence_confirm_summary=_summary(
            status="fail",
            deterministic_status="fail",
            semantic_status="pass",
        ),
    )

    ecq2 = next(issue for issue in result.quality_gate_result.issues if issue.rule_code == "ECQ2")

    assert result.quality_gate_result.status == "block"
    assert ecq2.severity == "block"
    assert not any(issue.rule_code == "ECQ4" for issue in result.quality_gate_result.issues)


def test_quality_gate_integration_maps_pathway_fail_to_ecq1_block(
    tmp_path: Path,
) -> None:
    """验证 pathway fail + block policy 投影为 ECQ1/block。

    Args:
        tmp_path: pytest 临时目录 fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 pathway fail 未生成 ECQ1/block 时抛出。
    """

    result = run_quality_gate_for_bundle(
        bundle=_bundle(),
        source_csv=_source_csv(tmp_path, "110011"),
        output_dir=tmp_path / "gate-run",
        run_id="fixture-run",
        golden_answer_path=None,
        evidence_confirm_summary=_summary(
            status="fail",
            deterministic_status="not_run",
            pathway_status="fail",
            not_run_reason="repository_failure:source_unavailable",
        ),
    )

    ecq1 = next(issue for issue in result.quality_gate_result.issues if issue.rule_code == "ECQ1")

    assert result.quality_gate_result.status == "block"
    assert ecq1.severity == "block"
    assert ecq1.reason == "repository_failure:source_unavailable"
    assert ecq1.issue_id == "evidence-confirm:110011:2024:ECQ1:repository_failure:source_unavailable"


def test_quality_gate_integration_rejects_off_policy_fail_summary(tmp_path: Path) -> None:
    """验证 policy=off 的 fail 摘要不会被静默降级成 ECQ warn。

    Args:
        tmp_path: pytest 临时目录 fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 off policy fail 摘要未抛错时抛出。
    """

    with pytest.raises(ValueError, match="policy='off'"):
        run_quality_gate_for_bundle(
            bundle=_bundle(),
            source_csv=_source_csv(tmp_path, "110011"),
            output_dir=tmp_path / "gate-run",
            run_id="fixture-run",
            golden_answer_path=None,
            evidence_confirm_summary=_summary(
                policy="off",
                status="fail",
                deterministic_status="fail",
            ),
        )


def test_quality_gate_integration_maps_not_run_to_ecq0_info(tmp_path: Path) -> None:
    """验证显式 not-run summary 投影为 ECQ0/info。

    Args:
        tmp_path: pytest 临时目录 fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 not-run 摘要未生成 ECQ0/info 时抛出。
    """

    result = run_quality_gate_for_bundle(
        bundle=_bundle(),
        source_csv=_source_csv(tmp_path, "110011"),
        output_dir=tmp_path / "gate-run",
        run_id="fixture-run",
        golden_answer_path=None,
        evidence_confirm_summary=not_run_evidence_confirm_summary(
            fund_code="110011",
            report_year=2024,
            policy="off",
            reason="policy_off",
        ),
    )

    ecq0 = next(issue for issue in result.quality_gate_result.issues if issue.rule_code == "ECQ0")

    assert result.quality_gate_result.status == "pass"
    assert ecq0.severity == "info"
    assert ecq0.reason == "policy_off"
    assert ecq0.issue_id == "evidence-confirm:110011:2024:ECQ0:policy_off"


def test_score_json_schema_remains_evidence_confirm_unaware(tmp_path: Path) -> None:
    """验证 ECQ 只进入 quality_gate.json，不修改 score.json schema。

    Args:
        tmp_path: pytest 临时目录 fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 score.json 出现 Evidence Confirm 字段时抛出。
    """

    result = run_quality_gate_for_bundle(
        bundle=_bundle(),
        source_csv=_source_csv(tmp_path, "110011"),
        output_dir=tmp_path / "gate-run",
        run_id="fixture-run",
        golden_answer_path=None,
        evidence_confirm_summary=_summary(status="warn", deterministic_status="warn"),
    )

    score_payload = json.loads(result.score_result.score_json_path.read_text(encoding="utf-8"))
    gate_payload = json.loads(result.quality_gate_result.gate_json_path.read_text(encoding="utf-8"))

    assert "evidence_confirm" not in score_payload
    assert not any("evidence_confirm" in key for key in score_payload)
    assert any(issue["rule_code"] == "ECQ3" for issue in gate_payload["issues"])


def test_quality_gate_integration_boundary_no_repository_or_source_imports() -> None:
    """验证 quality_gate_integration 不导入 repository/source/parser/provider 边界模块。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当模块出现禁用导入时抛出。
    """

    module_path = Path("fund_agent/fund/quality_gate_integration.py")
    tree = ast.parse(module_path.read_text(encoding="utf-8"))
    imports: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module is not None:
            imports.append(node.module)

    forbidden = ("repository", "source_adapter", "parser", "docling", "provider")

    assert not any(any(token in module for token in forbidden) for module in imports)


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


def _summary(
    *,
    policy: str = "block",
    status: str,
    deterministic_status: str,
    semantic_status: str = "not_run",
    pathway_status: str = "pass",
    not_run_reason: str | None = None,
) -> EvidenceConfirmProductionSummary:
    """构造测试用 Evidence Confirm 生产摘要。

    Args:
        policy: Evidence Confirm 生产策略。
        status: 摘要聚合状态。
        deterministic_status: deterministic V2 状态。
        semantic_status: semantic companion 状态。
        pathway_status: repository/source/reference materialization 通路状态。
        not_run_reason: 未运行或失败原因。

    Returns:
        Evidence Confirm 生产摘要。

    Raises:
        无显式抛出。
    """

    return EvidenceConfirmProductionSummary(
        schema_version="evidence_confirm_production_summary.v1",
        policy=policy,
        status=status,
        fund_code="110011",
        report_year=2024,
        pathway_status=pathway_status,
        deterministic_status=deterministic_status,
        semantic_status=semantic_status,
        checked_fact_count=1,
        failed_fact_count=1 if deterministic_status == "fail" else 0,
        warning_fact_count=1 if deterministic_status == "warn" else 0,
        not_applicable_fact_count=0,
        issue_count=1,
        auditability_score=40,
        blocking_issue_ids=("evidence-confirm:e3:blocking",)
        if deterministic_status == "fail"
        else (),
        warning_issue_ids=("evidence-confirm:e1:reviewable",)
        if deterministic_status == "warn"
        else (),
        not_run_reason=not_run_reason,
    )
