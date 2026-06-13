"""golden answer Markdown 转 JSON 测试。"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from fund_agent.fund.golden_answer import (
    GoldenAnswerValidationError,
    build_golden_answer_json,
    load_golden_answer_json,
    parse_golden_answer_markdown,
)

_P16_S2_INDEX_PROFILE_GOLDEN_ROWS = {
    "004194": {
        "benchmark_text": "中证1000指数收益率×95%+同期银行活期存款利率（税后）×5%",
        "benchmark_identity_status": "composite",
        "methodology_availability": "benchmark_only",
        "constituents_availability": "benchmark_only",
        "source_tier": "benchmark_context",
    },
    "005313": {
        "benchmark_text": "中证1000指数收益率*95%＋一年期人民币定期存款利率（税后）*5%",
        "benchmark_identity_status": "composite",
        "methodology_availability": "benchmark_only",
        "constituents_availability": "benchmark_only",
        "source_tier": "benchmark_context",
    },
    "017644": {
        "benchmark_text": "中证1000指数收益率×95%+同期银行活期存款利率(税后)×5%",
        "benchmark_identity_status": "composite",
        "methodology_availability": "benchmark_only",
        "constituents_availability": "benchmark_only",
        "source_tier": "benchmark_context",
    },
    "019918": {
        "benchmark_text": "中证2000指数收益率*95%+中国人民银行人民币活期存款利率（税后）*5%",
        "benchmark_identity_status": "composite",
        "methodology_availability": "benchmark_only",
        "constituents_availability": "benchmark_only",
        "source_tier": "benchmark_context",
    },
    "019923": {
        "benchmark_text": "中证2000指数收益率×95%＋人民币活期存款税后利率×5%",
        "benchmark_identity_status": "composite",
        "methodology_availability": "benchmark_only",
        "constituents_availability": "benchmark_only",
        "source_tier": "benchmark_context",
    },
}


def test_parse_golden_answer_markdown_outputs_strict_records() -> None:
    """验证人工审核 Markdown 会被解析为 strict golden answer 记录。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当字段解析或跳过项处理不符合预期时抛出。
    """

    markdown = "\n".join(
        (
            "# Correctness Golden Answer Template",
            "",
            "## 004393 测试基金（国内股票类）",
            "",
            "| field | sub_field | expected_value | confidence | source |",
            "|---|---|---|---|---|",
            "| basic_identity | fund_name | 测试基金 | high | 年报2024 §2 page-5 |",
            "| benchmark | benchmark_name | 沪深300\\|中债综合 | medium | 年报2024 §2 page-5 |",
            "| fee_schedule | — | — | — | 当前 slice 不处理 |",
        )
    )

    funds = parse_golden_answer_markdown(markdown)

    assert len(funds) == 1
    assert funds[0].fund_code == "004393"
    assert funds[0].skipped_fields == ("fee_schedule",)
    assert [record.sub_field for record in funds[0].records] == ["fund_name", "benchmark_name"]
    assert funds[0].records[1].expected_value == "沪深300|中债综合"


def test_parse_golden_answer_markdown_rejects_incomplete_rows() -> None:
    """验证未完成人工审核的行会给出可定位错误。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当校验错误缺少上下文时抛出。
    """

    markdown = "\n".join(
        (
            "## 004393 测试基金（国内股票类）",
            "",
            "| field | sub_field | expected_value | confidence | source |",
            "|---|---|---|---|---|",
            "| basic_identity | fund_name | | high | 年报2024 §2 page-5 |",
            "| benchmark | benchmark_name | 测试基准 | manual_required | manual_required |",
        )
    )

    with pytest.raises(GoldenAnswerValidationError) as exc_info:
        parse_golden_answer_markdown(markdown)

    error_text = str(exc_info.value)
    assert "004393 basic_identity.fund_name" in error_text
    assert "expected_value 不能为空" in error_text
    assert "confidence 必须是 high / medium / low" in error_text
    assert "source 必须填写可复核来源" in error_text


def test_build_golden_answer_json_writes_machine_readable_payload(tmp_path) -> None:
    """验证 golden answer JSON 输出包含 schema、funds 和扁平 records。

    Args:
        tmp_path: pytest 临时目录 fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 JSON payload 不符合契约时抛出。
    """

    input_path = tmp_path / "reviewed.md"
    output_path = tmp_path / "golden-answer.json"
    input_path.write_text(
        "\n".join(
            (
                "## 004393 测试基金（国内股票类）",
                "",
                "| field | sub_field | expected_value | confidence | source |",
                "|---|---|---|---|---|",
                "| basic_identity | fund_name | 测试基金 | high | 年报2024 §2 page-5 |",
                "| fee_schedule | — | — | — | 当前 slice 不处理 |",
            )
        ),
        encoding="utf-8",
    )

    result = build_golden_answer_json(input_path=input_path, output_path=output_path)

    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert result.fund_count == 1
    assert result.record_count == 1
    assert result.skipped_count == 1
    assert payload["schema_version"] == "fund-agent.golden-answer.v1"
    assert payload["funds"][0]["report_year"] == 2024
    assert payload["records"] == [
        {
            "fund_code": "004393",
            "report_year": 2024,
            "field_name": "basic_identity",
            "sub_field": "fund_name",
            "expected_value": "测试基金",
            "confidence": "high",
            "source": "年报2024 §2 page-5",
        }
    ]


def test_build_golden_answer_json_writes_explicit_metadata_report_year(
    tmp_path: Path,
) -> None:
    """验证 build 端到端输出 metadata 指定的 report_year。

    Args:
        tmp_path: pytest 临时目录 fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 fund 或 record 年份未写入 JSON 时抛出。
    """

    input_path = tmp_path / "reviewed-2025.md"
    output_path = tmp_path / "golden-answer-2025.json"
    input_path.write_text(
        "\n".join(
            (
                "## 004393 测试基金（国内股票类）",
                "",
                "```golden-answer-metadata",
                "report_year: 2025",
                "```",
                "",
                "| field | sub_field | expected_value | confidence | source |",
                "|---|---|---|---|---|",
                "| classified_fund_type | fund_type | active_fund | high | 年报2025 §2 page-5 |",
            )
        ),
        encoding="utf-8",
    )

    result = build_golden_answer_json(input_path=input_path, output_path=output_path)

    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert result.record_count == 1
    assert payload["funds"][0]["report_year"] == 2025
    assert payload["funds"][0]["records"][0]["report_year"] == 2025
    assert payload["records"][0]["report_year"] == 2025


def test_parse_golden_answer_markdown_accepts_explicit_report_year_metadata() -> None:
    """验证基金级 metadata 会写入 fund 和 record 的 report_year。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 metadata 年份未生效时抛出。
    """

    markdown = "\n".join(
        (
            "## 004393 测试基金（国内股票类）",
            "",
            "```golden-answer-metadata",
            "report_year: 2025",
            "```",
            "",
            "| field | sub_field | expected_value | confidence | source |",
            "|---|---|---|---|---|",
            "| classified_fund_type | fund_type | active_fund | high | 年报2025 §2 page-5 |",
        )
    )

    funds = parse_golden_answer_markdown(markdown)

    assert funds[0].report_year == 2025
    assert funds[0].records[0].report_year == 2025
    assert funds[0].records[0].source == "年报2025 §2 page-5"


def test_parse_golden_answer_markdown_allows_same_fund_across_years() -> None:
    """验证同一基金跨年份可复用同一字段 identity 的非年份部分。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当跨年份同基金被误拒时抛出。
    """

    markdown = "\n".join(
        (
            "## 004393 测试基金（国内股票类）",
            "",
            "| field | sub_field | expected_value | confidence | source |",
            "|---|---|---|---|---|",
            "| classified_fund_type | fund_type | active_fund | high | 年报2024 §2 page-5 |",
            "",
            "## 004393 测试基金（国内股票类）",
            "",
            "```golden-answer-metadata",
            "report_year: 2025",
            "```",
            "",
            "| field | sub_field | expected_value | confidence | source |",
            "|---|---|---|---|---|",
            "| classified_fund_type | fund_type | enhanced_index | high | 年报2025 §2 page-5 |",
        )
    )

    funds = parse_golden_answer_markdown(markdown)

    assert [(fund.fund_code, fund.report_year) for fund in funds] == [
        ("004393", 2024),
        ("004393", 2025),
    ]
    assert [fund.records[0].expected_value for fund in funds] == [
        "active_fund",
        "enhanced_index",
    ]


def test_parse_golden_answer_markdown_rejects_duplicate_fund_year_blocks() -> None:
    """验证同一基金同一年份不能拆成多个 Markdown 区块。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当重复基金年份区块未被拒绝时抛出。
    """

    markdown = "\n".join(
        (
            "## 004393 测试基金（国内股票类）",
            "",
            "```golden-answer-metadata",
            "report_year: 2025",
            "```",
            "",
            "| field | sub_field | expected_value | confidence | source |",
            "|---|---|---|---|---|",
            "| basic_identity | fund_name | 测试基金 | high | 年报2025 §2 page-5 |",
            "",
            "## 004393 测试基金（国内股票类）",
            "",
            "```golden-answer-metadata",
            "report_year: 2025",
            "```",
            "",
            "| field | sub_field | expected_value | confidence | source |",
            "|---|---|---|---|---|",
            "| classified_fund_type | fund_type | active_fund | high | 年报2025 §2 page-5 |",
        )
    )

    with pytest.raises(GoldenAnswerValidationError) as exc_info:
        parse_golden_answer_markdown(markdown)

    assert "fund 004393 2025: 重复 golden answer 基金区块" in str(exc_info.value)


@pytest.mark.parametrize(
    ("metadata_block", "expected_error"),
    (
        ("foo: 2025", "未知 metadata key foo"),
        ("report_year: 2025\nreport_year: 2026", "metadata key report_year 重复"),
        ("report_year: abc", "report_year 必须是整数"),
        ("", "golden-answer-metadata 必须包含 report_year"),
    ),
)
def test_parse_golden_answer_markdown_rejects_invalid_metadata(
    metadata_block: str,
    expected_error: str,
) -> None:
    """验证非法 metadata 会 fail-fast 并保留错误上下文。

    Args:
        metadata_block: metadata 代码块正文。
        expected_error: 预期错误片段。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当非法 metadata 未被拒绝时抛出。
    """

    markdown = "\n".join(
        (
            "## 004393 测试基金（国内股票类）",
            "",
            "```golden-answer-metadata",
            metadata_block,
            "```",
            "",
            "| field | sub_field | expected_value | confidence | source |",
            "|---|---|---|---|---|",
            "| classified_fund_type | fund_type | active_fund | high | 年报2025 §2 page-5 |",
        )
    )

    with pytest.raises(GoldenAnswerValidationError) as exc_info:
        parse_golden_answer_markdown(markdown)

    assert expected_error in str(exc_info.value)


def test_parse_golden_answer_markdown_rejects_late_or_unclosed_metadata() -> None:
    """验证 metadata 不能出现在表格之后，且必须闭合代码块。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 metadata 位置或闭合校验缺失时抛出。
    """

    late_markdown = "\n".join(
        (
            "## 004393 测试基金（国内股票类）",
            "",
            "| field | sub_field | expected_value | confidence | source |",
            "|---|---|---|---|---|",
            "| classified_fund_type | fund_type | active_fund | high | 年报2025 §2 page-5 |",
            "```golden-answer-metadata",
            "report_year: 2025",
            "```",
        )
    )
    unclosed_markdown = "\n".join(
        (
            "## 004393 测试基金（国内股票类）",
            "",
            "```golden-answer-metadata",
            "report_year: 2025",
        )
    )

    with pytest.raises(GoldenAnswerValidationError) as late_exc_info:
        parse_golden_answer_markdown(late_markdown)
    with pytest.raises(GoldenAnswerValidationError) as unclosed_exc_info:
        parse_golden_answer_markdown(unclosed_markdown)

    assert "golden-answer-metadata 必须出现在第一张表格之前" in str(late_exc_info.value)
    assert "golden-answer-metadata 代码块未关闭" in str(unclosed_exc_info.value)


def test_load_golden_answer_json_reuses_strict_schema(tmp_path) -> None:
    """验证 strict golden answer JSON 可被复用为 correctness 输入。

    Args:
        tmp_path: pytest 临时目录 fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 strict JSON loader 未恢复记录时抛出。
    """

    input_path = tmp_path / "reviewed.md"
    output_path = tmp_path / "golden-answer.json"
    input_path.write_text(
        "\n".join(
            (
                "## 004393 测试基金（国内股票类）",
                "",
                "| field | sub_field | expected_value | confidence | source |",
                "|---|---|---|---|---|",
                "| classified_fund_type | fund_type | active_fund | high | 年报2024 §2 page-5 |",
            )
        ),
        encoding="utf-8",
    )
    build_golden_answer_json(input_path=input_path, output_path=output_path)

    funds = load_golden_answer_json(output_path)

    assert len(funds) == 1
    assert funds[0].report_year == 2024
    assert funds[0].records[0].report_year == 2024
    assert funds[0].records[0].field_name == "classified_fund_type"
    assert funds[0].records[0].expected_value == "active_fund"


def test_load_golden_answer_json_defaults_legacy_report_year_to_2024(tmp_path: Path) -> None:
    """验证 legacy JSON 缺少 report_year 时按当前 2024 golden 语义加载。

    Args:
        tmp_path: pytest 临时目录 fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 legacy report_year 兼容规则失效时抛出。
    """

    path = tmp_path / "legacy-golden-answer.json"
    path.write_text(
        json.dumps(
            {
                "schema_version": "fund-agent.golden-answer.v1",
                "source_markdown": "fixture.md",
                "fund_count": 1,
                "record_count": 1,
                "funds": [
                    {
                        "fund_code": "004393",
                        "title": "测试基金（国内股票类）",
                        "records": [
                            {
                                "fund_code": "004393",
                                "field_name": "classified_fund_type",
                                "sub_field": "fund_type",
                                "expected_value": "active_fund",
                                "confidence": "high",
                                "source": "年报2024 §2 page-5",
                            }
                        ],
                        "skipped_fields": [],
                    }
                ],
                "records": [],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    funds = load_golden_answer_json(path)

    assert funds[0].report_year == 2024
    assert funds[0].records[0].report_year == 2024


def test_load_golden_answer_json_rejects_duplicate_same_year_identity(
    tmp_path: Path,
) -> None:
    """验证同基金同年份同字段子键重复会被拒绝。

    Args:
        tmp_path: pytest 临时目录 fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当重复 identity 未被拒绝时抛出。
    """

    duplicate_record = {
        "fund_code": "004393",
        "report_year": 2024,
        "field_name": "classified_fund_type",
        "sub_field": "fund_type",
        "expected_value": "active_fund",
        "confidence": "high",
        "source": "年报2024 §2 page-5",
    }
    path = tmp_path / "duplicate-golden-answer.json"
    path.write_text(
        json.dumps(
            _golden_answer_payload(
                funds=[
                    _golden_answer_fund_payload(
                        fund_code="004393",
                        report_year=2024,
                        records=[duplicate_record, dict(duplicate_record)],
                    )
                ]
            ),
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    with pytest.raises(GoldenAnswerValidationError) as exc_info:
        load_golden_answer_json(path)

    assert "重复 golden answer 行 004393 2024 classified_fund_type.fund_type" in str(
        exc_info.value
    )


def test_load_golden_answer_json_allows_same_fund_code_different_report_year(
    tmp_path: Path,
) -> None:
    """验证同一 fund_code 可在不同 report_year 下独立出现。

    Args:
        tmp_path: pytest 临时目录 fixture。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当跨年份同基金 golden 被误拒时抛出。
    """

    path = tmp_path / "multi-year-golden-answer.json"
    path.write_text(
        json.dumps(
            _golden_answer_payload(
                funds=[
                    _golden_answer_fund_payload(
                        fund_code="004393",
                        report_year=2024,
                        expected_value="active_fund",
                    ),
                    _golden_answer_fund_payload(
                        fund_code="004393",
                        report_year=2025,
                        expected_value="enhanced_index",
                    ),
                ]
            ),
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    funds = load_golden_answer_json(path)

    assert [(fund.fund_code, fund.report_year) for fund in funds] == [
        ("004393", 2024),
        ("004393", 2025),
    ]
    assert [fund.records[0].expected_value for fund in funds] == [
        "active_fund",
        "enhanced_index",
    ]


def test_reviewed_golden_answer_contains_only_planned_p16_s2_index_profile_rows() -> None:
    """验证 P16-S2 增强指数 golden rows 只覆盖计划内 scalar 子字段。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 strict rows 缺失、越界或 composite 语义被补值时抛出。
    """

    funds = {
        fund.fund_code: fund
        for fund in load_golden_answer_json(Path("reports/golden-answers/golden-answer.json"))
    }
    for fund_code, expected_rows in _P16_S2_INDEX_PROFILE_GOLDEN_ROWS.items():
        actual_rows = {
            record.sub_field: record
            for record in funds[fund_code].records
            if record.field_name == "index_profile"
        }
        assert set(actual_rows) == set(expected_rows)
        for sub_field, expected_value in expected_rows.items():
            assert actual_rows[sub_field].expected_value == expected_value
            assert actual_rows[sub_field].confidence == "high"
            assert "\n" not in actual_rows[sub_field].expected_value
        assert "benchmark_index_name" not in actual_rows
        assert "benchmark_index_code" not in actual_rows
        assert "benchmark_component_text" not in actual_rows
        assert not any(
            record.field_name == "tracking_error" for record in funds[fund_code].records
        )


def test_reviewed_golden_answer_preserves_001548_index_profile_rows() -> None:
    """验证 P16-S2 未改写既有 001548 指数画像 golden rows。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 001548 既有 row 被删除或改写时抛出。
    """

    funds = {
        fund.fund_code: fund
        for fund in load_golden_answer_json(Path("reports/golden-answers/golden-answer.json"))
    }
    rows = {
        record.sub_field: record.expected_value
        for record in funds["001548"].records
        if record.field_name == "index_profile"
    }

    assert rows == {
        "benchmark_text": "上证50指数收益率×95%＋银行活期存款利率（税后） ×5%",
        "benchmark_identity_status": "identified",
        "benchmark_index_name": "上证50指数",
        "source_tier": "benchmark_context",
    }


def _golden_answer_payload(*, funds: list[dict[str, object]]) -> dict[str, object]:
    """构造测试用 golden answer 顶层 payload。

    Args:
        funds: 基金级 payload 列表。

    Returns:
        strict golden answer JSON payload。

    Raises:
        无显式抛出。
    """

    records: list[object] = []
    for fund in funds:
        fund_records = fund.get("records")
        if isinstance(fund_records, list):
            records.extend(fund_records)
    return {
        "schema_version": "fund-agent.golden-answer.v1",
        "source_markdown": "fixture.md",
        "fund_count": len(funds),
        "record_count": len(records),
        "funds": funds,
        "records": records,
    }


def _golden_answer_fund_payload(
    *,
    fund_code: str,
    report_year: int,
    expected_value: str = "active_fund",
    records: list[dict[str, object]] | None = None,
) -> dict[str, object]:
    """构造测试用单基金 golden answer payload。

    Args:
        fund_code: 基金代码。
        report_year: 年报年份。
        expected_value: 默认基金类型期望值。
        records: 显式记录列表；为空时生成一条 classified_fund_type。

    Returns:
        单基金 payload。

    Raises:
        无显式抛出。
    """

    resolved_records = records or [
        {
            "fund_code": fund_code,
            "report_year": report_year,
            "field_name": "classified_fund_type",
            "sub_field": "fund_type",
            "expected_value": expected_value,
            "confidence": "high",
            "source": f"年报{report_year} §2 page-5",
        }
    ]
    return {
        "fund_code": fund_code,
        "report_year": report_year,
        "title": "测试基金（国内股票类）",
        "records": resolved_records,
        "skipped_fields": [],
    }
