"""P4-S2 精选基金池字段级评分测试。"""

from __future__ import annotations

import json
from pathlib import Path

from fund_agent.fund.extraction_score import (
    CORRECTNESS_MATCH,
    CORRECTNESS_MISMATCH,
    CORRECTNESS_STATUS_AVAILABLE,
    CORRECTNESS_STATUS_UNAVAILABLE,
    CORRECTNESS_UNAVAILABLE,
    EXCLUDED_GOLDEN_CATEGORIES,
    FIELD_PRIORITY_BY_NAME,
    MANDATORY_GOLDEN_CODE,
    MONEY_MARKET_CATEGORY,
    STATUS_FAIL,
    STATUS_PASS,
    STATUS_WATCH,
    run_extraction_score,
    compare_snapshot_correctness,
    score_fund_records,
    score_snapshot_records,
    select_minimal_golden_set,
)
from fund_agent.fund.extraction_snapshot import load_selected_funds


def test_score_snapshot_records_computes_coverage_traceability_status_and_priority() -> None:
    """验证字段级评分覆盖 coverage、traceability、status 和 priority 映射。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当评分结果不符合 P4-S2 契约时抛出。
    """

    records = [
        _snapshot_record("profile", "basic_identity", value_present=True, anchor_present=True),
        _snapshot_record("profile", "basic_identity", value_present=True, anchor_present=False),
        _snapshot_record("profile", "product_profile", value_present=True, anchor_present=True),
        _snapshot_record("profile", "product_profile", value_present=False, anchor_present=True),
        _snapshot_record("manager", "turnover_rate", value_present=True, anchor_present=False),
        _snapshot_record("manager", "turnover_rate", value_present=False, anchor_present=False),
        _snapshot_record("nav", "nav_data", value_present=True, anchor_present=False),
        _snapshot_record("nav", "nav_data", value_present=False, anchor_present=False),
    ]

    rows = score_snapshot_records(records)
    rows_by_name = {row.field_name: row for row in rows}

    assert rows_by_name["basic_identity"].priority == "P0"
    assert rows_by_name["basic_identity"].records == 2
    assert rows_by_name["basic_identity"].coverage_rate == 1.0
    assert rows_by_name["basic_identity"].traceability_rate == 0.5
    assert rows_by_name["basic_identity"].status == STATUS_FAIL
    assert rows_by_name["product_profile"].priority == "P1"
    assert rows_by_name["product_profile"].coverage_rate == 0.5
    assert rows_by_name["product_profile"].traceability_rate == 1.0
    assert rows_by_name["product_profile"].status == STATUS_FAIL
    assert rows_by_name["turnover_rate"].priority == "P1"
    assert rows_by_name["nav_data"].priority == "P2"
    assert set(FIELD_PRIORITY_BY_NAME) >= {row.field_name for row in rows}


def test_score_snapshot_records_status_thresholds_are_deterministic() -> None:
    """验证 pass / watch / fail 阈值是确定性的。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当阈值状态不符合预期时抛出。
    """

    records = []
    records.extend(
        _snapshot_record("profile", "basic_identity", value_present=True, anchor_present=True)
        for _ in range(10)
    )
    records.extend(
        _snapshot_record("profile", "benchmark", value_present=index < 8, anchor_present=index < 8)
        for index in range(10)
    )
    records.extend(
        _snapshot_record(
            "profile", "fee_schedule", value_present=index < 6, anchor_present=index < 6
        )
        for index in range(10)
    )

    rows_by_name = {row.field_name: row for row in score_snapshot_records(records)}

    assert rows_by_name["basic_identity"].status == STATUS_PASS
    assert rows_by_name["benchmark"].status == STATUS_WATCH
    assert rows_by_name["fee_schedule"].status == STATUS_FAIL


def test_score_fund_records_exposes_single_fund_p0_failure_when_aggregate_can_pass() -> None:
    """验证单基金 P0 失败不会被字段级聚合均值掩盖。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当单基金 P0 状态未被识别时抛出。
    """

    records = [
        _snapshot_record(
            "profile",
            "basic_identity",
            fund_code=f"{index:06d}",
            value_present=index != 0,
            anchor_present=index != 0,
        )
        for index in range(10)
    ]

    field_row = score_snapshot_records(records)[0]
    fund_rows = score_fund_records(records)
    rows_by_code = {row.fund_code: row for row in fund_rows}

    assert field_row.status == STATUS_PASS
    assert rows_by_code["000000"].p0_status == STATUS_FAIL
    assert rows_by_code["000000"].p0_failed_fields == ("basic_identity",)
    assert rows_by_code["000001"].p0_status == STATUS_PASS


def test_run_extraction_score_writes_score_outputs(tmp_path: Path) -> None:
    """验证评分 API 从 snapshot.jsonl 写出 score.json、score.md 和 golden_set.json。

    Args:
        tmp_path: pytest 临时目录 fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当输出产物缺失或内容不符合契约时抛出。
    """

    snapshot_path = tmp_path / "snapshot.jsonl"
    snapshot_path.write_text(
        "\n".join(
            json.dumps(record, ensure_ascii=False)
            for record in [
                _snapshot_record(
                    "profile", "basic_identity", value_present=True, anchor_present=True
                ),
                _snapshot_record("profile", "benchmark", value_present=False, anchor_present=False),
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    output_dir = tmp_path / "score-output"

    result = run_extraction_score(
        snapshot_path=snapshot_path,
        source_csv=Path("docs/code_20260519.csv"),
        output_dir=output_dir,
    )

    score_payload = json.loads(result.score_json_path.read_text(encoding="utf-8"))
    markdown = result.score_markdown_path.read_text(encoding="utf-8")
    golden_payload = json.loads(result.golden_set_path.read_text(encoding="utf-8"))

    assert result.score_json_path.exists()
    assert result.score_markdown_path.exists()
    assert result.golden_set_path.exists()
    assert score_payload["fund_count"] == 1
    assert score_payload["fund_scores"][0]["fund_code"] == "004393"
    assert score_payload["correctness"]["status"] == CORRECTNESS_STATUS_UNAVAILABLE
    assert score_payload["p0_status"] == STATUS_FAIL
    assert "## Correctness" in markdown
    assert "## Fund Scores" in markdown
    assert "## Field Scores" in markdown
    assert MANDATORY_GOLDEN_CODE in {record["fund_code"] for record in golden_payload["records"]}


def test_compare_snapshot_correctness_perfect_match_and_skipped_denominator(tmp_path: Path) -> None:
    """验证 correctness 可比字段 perfect match 且 skipped 不进入分母。

    Args:
        tmp_path: pytest 临时目录 fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 correctness 分母或匹配状态不符合契约时抛出。
    """

    golden_path = _golden_answer_json(
        tmp_path,
        expected_fund_type="active_fund",
        skipped_fields=["fee_schedule"],
    )
    records = [
        _snapshot_record(
            "profile",
            "classified_fund_type",
            value_present=True,
            anchor_present=True,
            classified_fund_type="active_fund",
        )
    ]

    summary = compare_snapshot_correctness(records=records, golden_answer_path=golden_path)

    assert summary.status == CORRECTNESS_STATUS_AVAILABLE
    assert summary.total_records == 2
    assert summary.comparable_records == 1
    assert summary.matched_records == 1
    assert summary.mismatched_records == 0
    assert summary.unavailable_records == 1
    assert summary.skipped_records == 1
    assert summary.accuracy_rate == 1.0
    statuses = {(row.field_name, row.sub_field): row.status for row in summary.record_results}
    assert statuses[("classified_fund_type", "fund_type")] == CORRECTNESS_MATCH
    assert statuses[("basic_identity", "fund_name")] == CORRECTNESS_UNAVAILABLE


def test_run_extraction_score_writes_correctness_mismatch(tmp_path: Path) -> None:
    """验证 run_extraction_score 会把 strict golden answer mismatch 写入 score.json。

    Args:
        tmp_path: pytest 临时目录 fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 score.json 缺少 correctness mismatch 时抛出。
    """

    snapshot_path = tmp_path / "snapshot.jsonl"
    snapshot_path.write_text(
        json.dumps(
            _snapshot_record(
                "profile",
                "classified_fund_type",
                value_present=True,
                anchor_present=True,
                classified_fund_type="index_fund",
            ),
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )
    golden_path = _golden_answer_json(tmp_path, expected_fund_type="active_fund")

    result = run_extraction_score(
        snapshot_path=snapshot_path,
        source_csv=Path("docs/code_20260519.csv"),
        output_dir=tmp_path / "score-output",
        golden_answer_path=golden_path,
    )

    score_payload = json.loads(result.score_json_path.read_text(encoding="utf-8"))
    mismatch_rows = [
        row
        for row in score_payload["correctness"]["record_results"]
        if row["status"] == CORRECTNESS_MISMATCH
    ]
    assert score_payload["correctness"]["status"] == CORRECTNESS_STATUS_AVAILABLE
    assert score_payload["correctness"]["comparable_records"] == 1
    assert score_payload["correctness"]["mismatched_records"] == 1
    assert mismatch_rows[0]["expected_value"] == "active_fund"
    assert mismatch_rows[0]["actual_value"] == "index_fund"


def test_select_minimal_golden_set_uses_only_csv_codes_and_excludes_money_market() -> None:
    """验证最小 golden set 只从真实 CSV 选码，包含必需类别并排除货币基金。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 golden set 不符合 P4-S2 选择规则时抛出。
    """

    source_csv = Path("docs/code_20260519.csv")
    selection = select_minimal_golden_set(source_csv)
    selected_codes = {record.fund_code for record in selection.records}
    selected_categories = {record.app_category for record in selection.records}
    csv_codes = _csv_codes(source_csv)

    assert MANDATORY_GOLDEN_CODE in selected_codes
    assert selected_codes <= csv_codes
    assert MONEY_MARKET_CATEGORY not in selected_categories
    assert EXCLUDED_GOLDEN_CATEGORIES == (MONEY_MARKET_CATEGORY,)
    assert selection.excluded_categories == (MONEY_MARKET_CATEGORY,)
    assert {"黄金类", "海外股票类", "海外债券/稳健类", "国内债券类"} <= selected_categories
    assert sum(1 for record in selection.records if record.app_category == "国内股票类") >= 2


def _snapshot_record(
    field_group: str,
    field_name: str,
    *,
    fund_code: str = "004393",
    value_present: bool,
    anchor_present: bool,
    classified_fund_type: str = "active_fund",
) -> dict[str, object]:
    """构造测试用 snapshot 记录。

    Args:
        field_group: 字段组。
        field_name: 字段名。
        fund_code: 基金代码。
        value_present: 是否存在字段值。
        anchor_present: 是否存在证据锚点。
        classified_fund_type: 系统识别基金类型。

    Returns:
        符合评分最小输入契约的字典。

    Raises:
        无显式抛出。
    """

    return {
        "fund_code": fund_code,
        "fund_name": f"测试基金{fund_code}",
        "app_category": "国内股票类",
        "classified_fund_type": classified_fund_type,
        "field_group": field_group,
        "field_name": field_name,
        "value_present": value_present,
        "anchor_present": anchor_present,
    }


def _golden_answer_json(
    tmp_path: Path,
    *,
    expected_fund_type: str,
    skipped_fields: list[str] | None = None,
) -> Path:
    """写入测试用 strict golden answer JSON。

    Args:
        tmp_path: pytest 临时目录 fixture。
        expected_fund_type: golden answer 中的基金类型真值。
        skipped_fields: 明确跳过字段。

    Returns:
        strict JSON 路径。

    Raises:
        OSError: 写入失败时抛出。
    """

    path = tmp_path / "golden-answer.json"
    records = [
        {
            "fund_code": "004393",
            "field_name": "classified_fund_type",
            "sub_field": "fund_type",
            "expected_value": expected_fund_type,
            "confidence": "high",
            "source": "年报2024 §2 page-5",
        },
        {
            "fund_code": "004393",
            "field_name": "basic_identity",
            "sub_field": "fund_name",
            "expected_value": "测试基金",
            "confidence": "high",
            "source": "年报2024 §2 page-5",
        },
    ]
    path.write_text(
        json.dumps(
            {
                "schema_version": "fund-agent.golden-answer.v1",
                "source_markdown": "fixture.md",
                "fund_count": 1,
                "record_count": len(records),
                "funds": [
                    {
                        "fund_code": "004393",
                        "title": "测试基金（国内股票类）",
                        "records": records,
                        "skipped_fields": skipped_fields or [],
                    }
                ],
                "records": records,
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    return path


def _csv_codes(source_csv: Path) -> set[str]:
    """读取 CSV 中所有基金代码。

    Args:
        source_csv: 精选基金池 CSV 路径。

    Returns:
        CSV 中的基金代码集合。

    Raises:
        OSError: 文件读取失败时抛出。
    """

    return {fund.fund_code for fund in load_selected_funds(source_csv)}
