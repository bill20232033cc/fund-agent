"""report-quality dev-only 维护脚本测试。"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from fund_agent.fund.report_evidence import REPORT_EVIDENCE_SCHEMA_VERSION
from scripts import report_quality_eval


def test_eval_writes_summary_for_jsonl_and_bundle_inputs(tmp_path: Path) -> None:
    """验证脚本可消费显式 JSONL 与 bundle JSON 并写出汇总。

    Args:
        tmp_path: pytest 临时目录。

    Returns:
        无返回值。

    Raises:
        AssertionError: 输出 summary 不符合预期时抛出。
    """

    jsonl_path = tmp_path / "quality.jsonl"
    bundle_path = tmp_path / "bundle.json"
    output_path = tmp_path / "scratch" / "summary.json"
    bundle = _valid_bundle_dict(review_status="fact_prefill_reviewed")
    score_issue = _external_score_issue()
    _write_jsonl_records(jsonl_path, ({"record_type": "bundle", **bundle}, score_issue))
    bundle_path.write_text(json.dumps(_valid_bundle_dict(), ensure_ascii=False), encoding="utf-8")

    exit_code = report_quality_eval.main(
        [
            "--jsonl",
            str(jsonl_path),
            "--bundle",
            str(bundle_path),
            "--output",
            str(output_path),
            "--run-id",
            "score-run:dev-tool",
        ]
    )

    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert exit_code == 0
    assert payload["input_count"] == 2
    assert payload["summary"]["total_records"] == 3
    assert payload["summary"]["blocking_count"] == 0
    assert payload["summary"]["failed_closed"] is False
    assert [item["run_id"] for item in payload["inputs"]] == [
        "score-run:dev-tool",
        "score-run:dev-tool",
    ]


def test_eval_reports_validator_issues_without_nonzero_exit(tmp_path: Path) -> None:
    """验证 validator issue 通过 summary 表达，脚本本身仍成功写出结果。

    Args:
        tmp_path: pytest 临时目录。

    Returns:
        无返回值。

    Raises:
        AssertionError: blocking issue 未写入 summary 时抛出。
    """

    bundle_path = tmp_path / "bad-bundle.json"
    output_path = tmp_path / "summary.json"
    bundle = _valid_bundle_dict()
    del bundle["fund_code"]
    bundle_path.write_text(json.dumps(bundle, ensure_ascii=False), encoding="utf-8")

    exit_code = report_quality_eval.main(
        ["--bundle", str(bundle_path), "--output", str(output_path)]
    )

    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert exit_code == 0
    assert payload["summary"]["blocking_count"] >= 1
    assert payload["summary"]["failed_closed"] is True
    assert ["RQV_FIELD_MISSING", 1] in payload["summary"]["error_code_counts"]


def test_eval_requires_explicit_input_path(tmp_path: Path) -> None:
    """验证脚本必须显式传入 JSONL 或 bundle 输入路径。

    Args:
        tmp_path: pytest 临时目录。

    Returns:
        无返回值。

    Raises:
        AssertionError: 未触发 argparse 失败时抛出。
    """

    with pytest.raises(SystemExit) as exc_info:
        report_quality_eval.main(["--output", str(tmp_path / "summary.json")])

    assert exc_info.value.code == 2


def test_eval_rejects_non_object_bundle_json(tmp_path: Path) -> None:
    """验证 bundle JSON 顶层必须是 object。

    Args:
        tmp_path: pytest 临时目录。

    Returns:
        无返回值。

    Raises:
        AssertionError: 非 object bundle 未被拒绝时抛出。
    """

    bundle_path = tmp_path / "bundle.json"
    bundle_path.write_text("[]", encoding="utf-8")

    with pytest.raises(TypeError, match="bundle JSON must be an object"):
        report_quality_eval.main(
            [
                "--bundle",
                str(bundle_path),
                "--output",
                str(tmp_path / "summary.json"),
            ]
        )


def _valid_bundle_dict(review_status: str = "scoring_ready") -> dict[str, object]:
    """构造最小合法 fake bundle serialization。

    Args:
        review_status: bundle review_status。

    Returns:
        fake bundle dict。
    """

    return {
        "bundle_id": "bundle:004393:2024",
        "schema_version": REPORT_EVIDENCE_SCHEMA_VERSION,
        "corpus_id": "corpus:dev-tool:test",
        "fund_code": "004393",
        "report_year": 2024,
        "classified_fund_type": "active_fund",
        "type_slot_membership_status": "matches_slot",
        "fund_type_slot": "active_fund",
        "preferred_lens": {
            "fund_type": "active_fund",
            "chapters": [
                {
                    "chapter_id": f"chapter_{index}",
                    "lens_key": "active_fund",
                    "used_default": False,
                    "primary_focus": "超额收益稳定性",
                    "watch_variable_label": "换手率",
                    "risk_focus_label": "风格漂移",
                    "source_statements": [],
                }
                for index in range(8)
            ],
        },
        "quality_context": {
            "fq_gate_status": "pass",
            "fq_issue_refs": [],
            "programmatic_audit_status": "pass",
            "report_quality_score_refs": [],
            "known_residual_refs": [],
            "judgment_constraint": "cautious_only",
        },
        "review_status": review_status,
        "source_documents": [
            {
                "document_id": "doc:004393:2024:annual_report",
                "document_type": "annual_report",
                "identity_status": "verified_annual_report",
                "source_boundary": "repository_derived",
                "source_failure_category": "none",
                "fallback_allowed": False,
                "fallback_used": False,
                "review_artifact_refs": [],
            }
        ],
        "facts": [
            {
                "fact_id": "fact:basic_identity",
                "category": "identity",
                "field_path": "basic_identity",
                "value": {"fund_name": "测试基金"},
                "unit": "object",
                "source_boundary": "repository_derived",
                "extraction_mode": "direct",
                "review_status": "reviewed",
                "period": None,
                "source_anchor_ids": ["anchor:004393:2024:annual_report:sec2:abc12345"],
                "source_document_ids": ["doc:004393:2024:annual_report"],
                "failure_category": None,
                "data_gap_refs": [],
                "score_issue_ids": [],
            }
        ],
        "derived_calculations": [],
        "evidence_anchors": [
            {
                "anchor_id": "anchor:004393:2024:annual_report:sec2:abc12345",
                "source_kind": "annual_report",
                "source_strength": "fund_disclosure",
                "document_id": "doc:004393:2024:annual_report",
                "document_year": 2024,
                "section_id": "sec2",
                "page_number": 12,
                "table_id": None,
                "row_locator": "row:1",
                "review_artifact_ref": None,
                "note": "基金基本信息",
            }
        ],
        "data_gaps": [],
        "score_issue_links": [],
        "validation_messages": [],
    }


def _external_score_issue() -> dict[str, object]:
    """构造 JSONL 独立 score_issue record。

    Args:
        无。

    Returns:
        独立 score_issue record。
    """

    return {
        "record_type": "score_issue",
        "issue_id": "issue:chapter2:pass",
        "score_run_id": "score-run:dev-tool",
        "chapter_id": "chapter_2",
        "dimension": "fact_coverage",
        "status": "pass",
        "next_gate_recommendation": "review_acceptance",
        "severity": None,
        "field_path": None,
        "evidence_anchor_refs": ["anchor:004393:2024:annual_report:sec2:abc12345"],
        "data_gap_refs": [],
    }


def _write_jsonl_records(path: Path, records: tuple[dict[str, object], ...]) -> None:
    """写入测试 JSONL records。

    Args:
        path: JSONL 输出路径。
        records: 待写入 records。

    Returns:
        无返回值。
    """

    path.write_text(
        "\n".join(json.dumps(record, ensure_ascii=False) for record in records),
        encoding="utf-8",
    )
