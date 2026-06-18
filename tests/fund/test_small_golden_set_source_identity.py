"""验证 small golden set Slice C Option 1 的 source identity fail-closed 边界。

本测试只读取本地 small golden set fixture JSON，不触发 FundDocumentRepository、
PDF/cache、source helper、fallback、provider、LLM 或网络路径。
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
EXPECTED_REPORT_YEAR = 2024
EXPECTED_FUND_CODES = {"004393", "110020", "004194", "006597", "017641"}
EXPECTED_SCHEMA_VERSION = "fund-agent.small_golden_set_expected_fields.v1"
MATCHED_REQUIRED_IDENTITY_FIELDS = {
    "source_document_title",
    "source_document_id",
    "resolved_fund_code",
    "resolved_share_class",
    "source_kind",
    "report_year",
    "identity_evidence_anchor",
    "identity_evidence_origin",
}
MATCHED_ALLOWED_ORIGINS = {
    "pre_existing_offline_metadata",
    "retained_real_minimal_excerpt_anchor",
}
EXACT_OR_NUMERIC_ASSERTIONS = {"exact", "normalized_text", "numeric_percent"}


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


def _all_expected_fields() -> dict[str, dict[str, Any]]:
    """读取五行 small golden set expected fields。

    参数：
        无。

    返回：
        以基金代码为 key 的 expected fields 字典。

    异常：
        FileNotFoundError: 任一 fixture 文件不存在。
        json.JSONDecodeError: 任一 fixture 文件不是合法 JSON。
    """
    return {fund_code: _load_expected_fields(fund_code) for fund_code in EXPECTED_FUND_CODES}


def _assert_matched_identity_shape(fund_code: str, expected_fields: dict[str, Any]) -> None:
    """验证 matched 行具备完整 source document / fund / year / provenance 字段。

    参数：
        fund_code: 六位基金代码。
        expected_fields: 单行 expected fields fixture。

    返回：
        无。

    异常：
        AssertionError: matched 行缺少必要身份字段或边界字段。
    """
    source_identity = expected_fields["source_identity"]

    assert source_identity["status"] == "matched"
    assert source_identity["matched_source_document"] is True
    assert expected_fields["fixture_source_kind"] == "real_minimal_excerpt"
    assert expected_fields["exact_numeric_correctness_allowed"] is True
    assert expected_fields["promotion_allowed"] is False
    assert expected_fields["fallback_invocation"] == "prohibited"
    assert source_identity["fallback_used"] is False
    assert MATCHED_REQUIRED_IDENTITY_FIELDS <= set(source_identity)
    assert source_identity["resolved_fund_code"] == fund_code
    assert source_identity["report_year"] == EXPECTED_REPORT_YEAR
    assert source_identity["source_kind"] == "annual_report"
    assert source_identity["identity_evidence_origin"] in MATCHED_ALLOWED_ORIGINS
    for field_name in MATCHED_REQUIRED_IDENTITY_FIELDS:
        assert source_identity[field_name] not in ("", None)


def _assert_unmatched_synthetic_shape(fund_code: str, expected_fields: dict[str, Any]) -> None:
    """验证 unmatched synthetic 行不能声明 source correctness。

    参数：
        fund_code: 六位基金代码。
        expected_fields: 单行 expected fields fixture。

    返回：
        无。

    异常：
        AssertionError: unmatched synthetic 行越界声明 matched identity 或 correctness。
    """
    source_identity = expected_fields["source_identity"]

    assert expected_fields["fund_code"] == fund_code
    assert expected_fields["report_year"] == EXPECTED_REPORT_YEAR
    assert expected_fields["fixture_source_kind"] == "synthetic"
    assert expected_fields["exact_numeric_correctness_allowed"] is False
    assert expected_fields["promotion_allowed"] is False
    assert expected_fields["fallback_invocation"] == "prohibited"
    assert source_identity["status"] == "unmatched_synthetic"
    assert source_identity["matched_source_document"] is False
    assert source_identity["fallback_used"] is False
    assert "reason" in source_identity
    assert MATCHED_REQUIRED_IDENTITY_FIELDS.isdisjoint(source_identity)


def test_source_identity_guard_keeps_exact_five_rows() -> None:
    """验证 source identity guard 只覆盖 Slice A/B 接受的五行集合。

    参数：
        无。

    返回：
        无。

    异常：
        AssertionError: fixture 行集合、年份或 schema 版本不符合当前 mini-slice。
    """
    rows = _all_expected_fields()

    assert set(rows) == EXPECTED_FUND_CODES
    for fund_code, expected_fields in rows.items():
        assert expected_fields["schema_version"] == EXPECTED_SCHEMA_VERSION
        assert expected_fields["fund_code"] == fund_code
        assert expected_fields["report_year"] == EXPECTED_REPORT_YEAR


def test_matched_rows_require_complete_source_document_identity() -> None:
    """验证任何 matched 行都必须有完整 source document / year / fund / provenance 字段。

    参数：
        无。

    返回：
        无。

    异常：
        AssertionError: matched 行缺少必要字段，或 unmatched 行未保持 fail-closed。
    """
    for fund_code, expected_fields in _all_expected_fields().items():
        source_identity = expected_fields["source_identity"]
        if source_identity["status"] == "matched":
            _assert_matched_identity_shape(fund_code, expected_fields)
        else:
            _assert_unmatched_synthetic_shape(fund_code, expected_fields)


def test_unmatched_synthetic_rows_remain_non_correctness_fixtures() -> None:
    """验证当前 unmatched synthetic 行不能承载 exact / numeric correctness。

    参数：
        无。

    返回：
        无。

    异常：
        AssertionError: synthetic fixture 出现 exact、normalized_text 或 numeric_percent 断言。
    """
    for expected_fields in _all_expected_fields().values():
        if expected_fields["source_identity"]["status"] == "unmatched_synthetic":
            assert expected_fields["fixture_source_kind"] == "synthetic"
            assert expected_fields["exact_numeric_correctness_allowed"] is False
            for field_group in expected_fields["field_groups"].values():
                assert field_group["fixture_source_kind"] == "synthetic"
                assert field_group["assertion_kind"] not in EXACT_OR_NUMERIC_ASSERTIONS
                assert field_group["assertion_kind"] == "availability_status"


def test_no_row_claims_fallback_or_promotion_through_source_identity() -> None:
    """验证 source identity guard 不允许 fallback、promotion 或 readiness 语义漂移。

    参数：
        无。

    返回：
        无。

    异常：
        AssertionError: 任一行声明 fallback、promotion 或缺少 source identity 边界字段。
    """
    for expected_fields in _all_expected_fields().values():
        source_identity = expected_fields["source_identity"]

        assert expected_fields["promotion_allowed"] is False
        assert expected_fields["fallback_invocation"] == "prohibited"
        assert source_identity["fallback_used"] is False
        assert "promotion_allowed" not in source_identity
        assert "quality_gate_promotion" not in source_identity
