"""P4-S2 精选基金池字段级评分测试。"""

from __future__ import annotations

import json
from pathlib import Path

from fund_agent.fund.extraction_score import (
    EXCLUDED_GOLDEN_CATEGORIES,
    FIELD_PRIORITY_BY_NAME,
    MANDATORY_GOLDEN_CODE,
    MONEY_MARKET_CATEGORY,
    STATUS_FAIL,
    STATUS_PASS,
    STATUS_WATCH,
    run_extraction_score,
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
        _snapshot_record("profile", "fee_schedule", value_present=index < 6, anchor_present=index < 6)
        for index in range(10)
    )

    rows_by_name = {row.field_name: row for row in score_snapshot_records(records)}

    assert rows_by_name["basic_identity"].status == STATUS_PASS
    assert rows_by_name["benchmark"].status == STATUS_WATCH
    assert rows_by_name["fee_schedule"].status == STATUS_FAIL


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
                _snapshot_record("profile", "basic_identity", value_present=True, anchor_present=True),
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
    assert score_payload["correctness"]["status"] == "not_implemented"
    assert score_payload["p0_status"] == STATUS_FAIL
    assert "## Field Scores" in markdown
    assert MANDATORY_GOLDEN_CODE in {record["fund_code"] for record in golden_payload["records"]}


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
    value_present: bool,
    anchor_present: bool,
) -> dict[str, object]:
    """构造测试用 snapshot 记录。

    Args:
        field_group: 字段组。
        field_name: 字段名。
        value_present: 是否存在字段值。
        anchor_present: 是否存在证据锚点。

    Returns:
        符合评分最小输入契约的字典。

    Raises:
        无显式抛出。
    """

    return {
        "field_group": field_group,
        "field_name": field_name,
        "value_present": value_present,
        "anchor_present": anchor_present,
    }


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
