"""验证 small golden set Slice A manifest 的离线 schema 边界。

本测试只读取本地 JSON review artifact，不触发 repository、PDF、provider、
fallback 或网络路径。
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


MANIFEST_PATH = (
    Path(__file__).resolve().parents[2]
    / "docs"
    / "reviews"
    / "mvp-small-golden-set-manifest-20260608.json"
)
EXPECTED_SCHEMA_VERSION = "fund-agent.small_golden_set_manifest.v1"
EXPECTED_REPORT_YEAR = 2024
EXPECTED_FUND_TYPES = {
    "004393": "active_fund",
    "110020": "index_fund",
    "004194": "enhanced_index",
    "006597": "bond_fund",
    "017641": "qdii_fund",
}
EXPECTED_SLOTS = {
    "004393": "active_equity_or_mixed",
    "110020": "broad_domestic_index",
    "004194": "enhanced_index",
    "006597": "bond",
    "017641": "qdii",
}
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
TOP_LEVEL_KEYS = {
    "schema_version",
    "promotion_allowed_default",
    "ordinary_pytest_network_allowed",
    "fallback_invocation_allowed",
    "rows",
}
ROW_KEYS = {
    "fund_code",
    "report_year",
    "slot",
    "expected_fund_type",
    "promotion_allowed",
    "source_document_identity",
    "field_expectations",
}
SOURCE_IDENTITY_KEYS = {
    "source_kind",
    "identity_status",
    "fallback_used",
    "fallback_invocation",
}
FIELD_STATUS_VALUES = {
    "expected",
    "unavailable",
    "not_applicable",
    "deferred_policy",
}
EXPECTED_FIELD_STATUS_BY_FUND = {
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
FORBIDDEN_CORRECTNESS_KEYS = {
    "accepted_correctness",
    "assertion_kind",
    "correctness_accepted",
    "correctness_assertion",
    "expected_value",
    "identity_evidence_anchor",
    "matched_correctness",
    "numeric_correctness",
    "source_document_id",
    "source_document_title",
}
FORBIDDEN_SOURCE_EXCERPT_KEYS = {
    "annual_report_excerpt",
    "excerpt",
    "raw_text",
    "source_excerpt",
    "source_text",
}


def _load_manifest() -> dict[str, Any]:
    """读取 Slice A manifest。

    参数：
        无。

    返回：
        解析后的 manifest 字典。

    异常：
        FileNotFoundError: manifest 文件不存在。
        json.JSONDecodeError: manifest 不是合法 JSON。
    """
    with MANIFEST_PATH.open(encoding="utf-8") as manifest_file:
        return json.load(manifest_file)


def _rows_by_fund_code(manifest: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """按基金代码索引 manifest 行。

    参数：
        manifest: 已解析的 manifest 字典。

    返回：
        以基金代码为 key 的行字典。

    异常：
        KeyError: manifest 缺少 rows 或行缺少 fund_code。
    """
    return {row["fund_code"]: row for row in manifest["rows"]}


def test_manifest_schema_version_and_global_boundaries() -> None:
    """验证 manifest schema 与全局离线边界。

    参数：
        无。

    返回：
        无。

    异常：
        AssertionError: manifest 全局 schema 或边界字段不符合 Slice A 约束。
    """
    manifest = _load_manifest()

    assert manifest["schema_version"] == EXPECTED_SCHEMA_VERSION
    assert manifest["promotion_allowed_default"] is False
    assert manifest["ordinary_pytest_network_allowed"] is False
    assert manifest["fallback_invocation_allowed"] is False


def test_manifest_uses_closed_key_sets_without_source_excerpts() -> None:
    """验证 Slice A manifest 使用封闭字段集合且不包含 source excerpt。

    参数：
        无。

    返回：
        无。

    异常：
        AssertionError: manifest 出现越界字段、source excerpt 或 raw text 字段。
    """
    manifest = _load_manifest()

    assert set(manifest) == TOP_LEVEL_KEYS
    for row in manifest["rows"]:
        assert set(row) == ROW_KEYS
        assert set(row["source_document_identity"]) == SOURCE_IDENTITY_KEYS
        _assert_no_forbidden_source_excerpt_keys(row)


def test_manifest_rows_exact_identity_and_promotion_boundary() -> None:
    """验证五行集合、年份、slot、基金类型和 promotion 边界。

    参数：
        无。

    返回：
        无。

    异常：
        AssertionError: manifest 行集合、年份、slot、基金类型或 promotion 边界错误。
    """
    manifest = _load_manifest()
    rows_by_fund_code = _rows_by_fund_code(manifest)

    assert set(rows_by_fund_code) == set(EXPECTED_FUND_TYPES)
    assert len(manifest["rows"]) == len(EXPECTED_FUND_TYPES)
    for fund_code, row in rows_by_fund_code.items():
        assert row["report_year"] == EXPECTED_REPORT_YEAR
        assert row["slot"] == EXPECTED_SLOTS[fund_code]
        assert row["expected_fund_type"] == EXPECTED_FUND_TYPES[fund_code]
        assert row["promotion_allowed"] is False


def test_manifest_source_identity_pending_and_fallback_prohibited() -> None:
    """验证 Slice A source identity 仍 pending 且禁止 fallback。

    参数：
        无。

    返回：
        无。

    异常：
        AssertionError: manifest 在 Slice A 声明 matched identity 或 fallback 可用。
    """
    manifest = _load_manifest()

    for row in manifest["rows"]:
        source_identity = row["source_document_identity"]
        assert source_identity["source_kind"] == "annual_report"
        assert source_identity["identity_status"] == "pending_offline_fixture"
        assert source_identity["fallback_used"] is False
        assert source_identity["fallback_invocation"] == "prohibited"


def test_field_expectations_complete_and_use_plan_status_values() -> None:
    """验证每行完整覆盖九个 field group 且状态来自计划枚举。

    参数：
        无。

    返回：
        无。

    异常：
        AssertionError: field group 不完整或状态不符合 accepted plan。
    """
    manifest = _load_manifest()
    rows_by_fund_code = _rows_by_fund_code(manifest)

    for fund_code, row in rows_by_fund_code.items():
        field_expectations = row["field_expectations"]
        assert set(field_expectations) == EXPECTED_FIELD_GROUPS
        assert set(field_expectations.values()) <= FIELD_STATUS_VALUES
        assert field_expectations == EXPECTED_FIELD_STATUS_BY_FUND[fund_code]


def test_pending_identity_cannot_accept_numeric_or_exact_correctness() -> None:
    """验证 pending source identity 不能声明精确或数值 correctness 已接受。

    参数：
        无。

    返回：
        无。

    异常：
        AssertionError: manifest 在 pending identity 下声明 exact/numeric correctness。
    """
    manifest = _load_manifest()

    for row in manifest["rows"]:
        assert row["source_document_identity"]["identity_status"] != "matched"
        _assert_no_forbidden_correctness_keys(row)


def _assert_no_forbidden_source_excerpt_keys(value: Any) -> None:
    """递归验证 manifest 未嵌入 Slice A 禁止的 source excerpt 字段。

    参数：
        value: 待检查的 JSON 值。

    返回：
        无。

    异常：
        AssertionError: 发现 source excerpt 或 raw text 字段。
    """
    if isinstance(value, dict):
        assert FORBIDDEN_SOURCE_EXCERPT_KEYS.isdisjoint(value)
        for nested_value in value.values():
            _assert_no_forbidden_source_excerpt_keys(nested_value)
    elif isinstance(value, list):
        for nested_value in value:
            _assert_no_forbidden_source_excerpt_keys(nested_value)


def _assert_no_forbidden_correctness_keys(value: Any) -> None:
    """递归验证 manifest 未写入 Slice A 禁止的 correctness 接受字段。

    参数：
        value: 待检查的 JSON 值。

    返回：
        无。

    异常：
        AssertionError: 发现禁止字段。
    """
    if isinstance(value, dict):
        assert FORBIDDEN_CORRECTNESS_KEYS.isdisjoint(value)
        for nested_value in value.values():
            _assert_no_forbidden_correctness_keys(nested_value)
    elif isinstance(value, list):
        for nested_value in value:
            _assert_no_forbidden_correctness_keys(nested_value)
