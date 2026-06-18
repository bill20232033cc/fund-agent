"""验证 small golden set Slice B 离线 fixture 的边界形状。

本测试只读取本地 `tests/fixtures/fund/small_golden_set` JSON 与文本 fixture，
不触发 FundDocumentRepository、PDF/cache、source helper、fallback、provider 或网络路径。
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


FIXTURE_ROOT = (
    Path(__file__).resolve().parents[1]
    / "fixtures"
    / "fund"
    / "small_golden_set"
)
EXPECTED_SCHEMA_VERSION = "fund-agent.small_golden_set_expected_fields.v1"
EXPECTED_REPORT_YEAR = 2024
EXPECTED_FUND_CODES = {"004393", "110020", "004194", "006597", "017641"}
EXPECTED_FIELD_GROUPS = {
    "identity",
    "source_document",
    "benchmark",
    "manager",
    "scale",
    "fee",
    "return",
    "holdings",
    "risk",
}
FIELD_STATUS_VALUES = {"expected", "unavailable", "not_applicable", "deferred_policy"}
ASSERTION_KIND_VALUES = {
    "exact",
    "normalized_text",
    "numeric_percent",
    "availability_status",
    "not_applicable",
    "deferred_policy",
}
EXACT_OR_NUMERIC_ASSERTIONS = {"exact", "normalized_text", "numeric_percent"}
FIXTURE_SOURCE_KIND_VALUES = {"real_minimal_excerpt", "synthetic", "unavailable"}
EXPECTED_STATUS_BY_FUND = {
    "004393": {
        "identity": "expected",
        "source_document": "expected",
        "benchmark": "expected",
        "manager": "expected",
        "scale": "expected",
        "fee": "expected",
        "return": "expected",
        "holdings": "expected",
        "risk": "expected",
    },
    "110020": {
        "identity": "expected",
        "source_document": "expected",
        "benchmark": "expected",
        "manager": "expected",
        "scale": "expected",
        "fee": "expected",
        "return": "expected",
        "holdings": "expected",
        "risk": "expected",
    },
    "004194": {
        "identity": "expected",
        "source_document": "expected",
        "benchmark": "expected",
        "manager": "expected",
        "scale": "expected",
        "fee": "expected",
        "return": "expected",
        "holdings": "expected",
        "risk": "expected",
    },
    "006597": {
        "identity": "expected",
        "source_document": "expected",
        "benchmark": "expected",
        "manager": "expected",
        "scale": "expected",
        "fee": "expected",
        "return": "expected",
        "holdings": "expected",
        "risk": "expected",
    },
    "017641": {
        "identity": "expected",
        "source_document": "expected",
        "benchmark": "expected",
        "manager": "expected",
        "scale": "expected",
        "fee": "expected",
        "return": "expected",
        "holdings": "unavailable",
        "risk": "deferred_policy",
    },
}


def _load_expected_fields(fund_code: str) -> dict[str, Any]:
    """读取单只基金的 expected fields fixture。

    参数：
        fund_code: 六位基金代码。

    返回：
        解析后的 expected fields 字典。

    异常：
        FileNotFoundError: fixture 文件不存在。
        json.JSONDecodeError: fixture 文件不是合法 JSON。
    """
    fixture_path = FIXTURE_ROOT / f"{fund_code}_{EXPECTED_REPORT_YEAR}" / "expected_fields.json"
    with fixture_path.open(encoding="utf-8") as fixture_file:
        return json.load(fixture_file)


def _load_excerpt(fund_code: str) -> str:
    """读取单只基金的最小 annual report excerpt fixture。

    参数：
        fund_code: 六位基金代码。

    返回：
        fixture 文本内容。

    异常：
        FileNotFoundError: fixture 文件不存在。
    """
    fixture_path = (
        FIXTURE_ROOT / f"{fund_code}_{EXPECTED_REPORT_YEAR}" / "annual_report_excerpt.txt"
    )
    return fixture_path.read_text(encoding="utf-8")


def test_fixture_directory_contains_exact_five_rows() -> None:
    """验证 fixture 目录严格对应 Slice A 五行集合。

    参数：
        无。

    返回：
        无。

    异常：
        AssertionError: fixture 目录集合或必要文件不符合 Slice B 计划。
    """
    fixture_dirs = {path.name for path in FIXTURE_ROOT.iterdir() if path.is_dir()}

    assert fixture_dirs == {f"{fund_code}_{EXPECTED_REPORT_YEAR}" for fund_code in EXPECTED_FUND_CODES}
    for fund_code in EXPECTED_FUND_CODES:
        assert (FIXTURE_ROOT / f"{fund_code}_{EXPECTED_REPORT_YEAR}" / "expected_fields.json").is_file()
        assert (
            FIXTURE_ROOT / f"{fund_code}_{EXPECTED_REPORT_YEAR}" / "annual_report_excerpt.txt"
        ).is_file()


def test_fixture_metadata_preserves_offline_promotion_and_fallback_boundaries() -> None:
    """验证 fixture 元数据保持 offline、promotion 和 fallback 边界。

    参数：
        无。

    返回：
        无。

    异常：
        AssertionError: fixture 允许 promotion、fallback 或 source identity 匹配。
    """
    for fund_code in EXPECTED_FUND_CODES:
        expected_fields = _load_expected_fields(fund_code)
        source_identity = expected_fields["source_identity"]

        assert expected_fields["schema_version"] == EXPECTED_SCHEMA_VERSION
        assert expected_fields["fund_code"] == fund_code
        assert expected_fields["report_year"] == EXPECTED_REPORT_YEAR
        assert expected_fields["promotion_allowed"] is False
        assert expected_fields["fallback_invocation"] == "prohibited"
        assert expected_fields["fixture_source_kind"] == "synthetic"
        assert expected_fields["exact_numeric_correctness_allowed"] is False
        assert source_identity["status"] == "unmatched_synthetic"
        assert source_identity["matched_source_document"] is False
        assert source_identity["fallback_used"] is False


def test_fixture_field_groups_have_required_status_and_anchor_shape() -> None:
    """验证每个 field group 记录 status、assertion_kind、source kind 和 anchor/缺口原因。

    参数：
        无。

    返回：
        无。

    异常：
        AssertionError: field group 形状、状态或 anchor/缺口原因不符合 Slice B 计划。
    """
    for fund_code in EXPECTED_FUND_CODES:
        expected_fields = _load_expected_fields(fund_code)
        field_groups = expected_fields["field_groups"]

        assert set(field_groups) == EXPECTED_FIELD_GROUPS
        for group_name, field_group in field_groups.items():
            assert field_group["status"] == EXPECTED_STATUS_BY_FUND[fund_code][group_name]
            assert field_group["status"] in FIELD_STATUS_VALUES
            assert field_group["assertion_kind"] in ASSERTION_KIND_VALUES
            assert field_group["fixture_source_kind"] in FIXTURE_SOURCE_KIND_VALUES
            assert field_group["fixture_source_kind"] == expected_fields["fixture_source_kind"]
            assert ("source_anchor" in field_group) ^ ("unavailable_reason" in field_group)


def test_synthetic_or_unavailable_fixture_cannot_drive_exact_or_numeric_assertions() -> None:
    """验证非 matched real fixture 禁止 exact、normalized_text 或 numeric_percent 断言。

    参数：
        无。

    返回：
        无。

    异常：
        AssertionError: synthetic/unavailable fixture 下出现 exact 或 numeric correctness 断言。
    """
    for fund_code in EXPECTED_FUND_CODES:
        expected_fields = _load_expected_fields(fund_code)
        for field_group in expected_fields["field_groups"].values():
            if expected_fields["fixture_source_kind"] != "real_minimal_excerpt":
                assert field_group["assertion_kind"] not in EXACT_OR_NUMERIC_ASSERTIONS
            assert field_group["assertion_kind"] == "availability_status"


def test_excerpts_are_minimal_synthetic_and_do_not_claim_real_source_identity() -> None:
    """验证 excerpt 是最小 synthetic 片段且未声明真实 source identity。

    参数：
        无。

    返回：
        无。

    异常：
        AssertionError: excerpt 缺少 synthetic 边界标记、过长或声明 matched identity。
    """
    for fund_code in EXPECTED_FUND_CODES:
        excerpt = _load_excerpt(fund_code)

        assert "SYNTHETIC SMALL GOLDEN SET EXCERPT" in excerpt
        assert f"fund_code: {fund_code}" in excerpt
        assert f"report_year: {EXPECTED_REPORT_YEAR}" in excerpt
        assert "fixture_source_kind: synthetic" in excerpt
        assert "source_identity: unmatched_synthetic" in excerpt
        assert "fallback_invocation: prohibited" in excerpt
        assert "promotion_allowed: false" in excerpt
        assert "matched" not in excerpt.lower().replace("unmatched_synthetic", "")
        assert len(excerpt.splitlines()) <= 20
