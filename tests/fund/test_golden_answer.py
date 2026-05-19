"""golden answer Markdown 转 JSON 测试。"""

from __future__ import annotations

import json

import pytest

from fund_agent.fund.golden_answer import (
    GoldenAnswerValidationError,
    build_golden_answer_json,
    load_golden_answer_json,
    parse_golden_answer_markdown,
)


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
    assert payload["records"] == [
        {
            "fund_code": "004393",
            "field_name": "basic_identity",
            "sub_field": "fund_name",
            "expected_value": "测试基金",
            "confidence": "high",
            "source": "年报2024 §2 page-5",
        }
    ]


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
    assert funds[0].records[0].field_name == "classified_fund_type"
    assert funds[0].records[0].expected_value == "active_fund"
