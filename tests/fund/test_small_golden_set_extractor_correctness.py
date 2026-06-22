"""验证 retained excerpt oracle 驱动的 row-field extractor correctness。

本测试只读取 accepted retained excerpt JSON 作为 correctness oracle，不读取 PDF、
不调用 FundDocumentRepository，不触发 source helper、fallback、provider 或网络路径。
见模板第 1 章“产品本质”和第 2 章 R=A+B-C 的字段级抽取边界。
"""

from __future__ import annotations

import pytest

from fund_agent.fund.extractors.holdings_share_change import extract_holdings_share_change
from fund_agent.fund.extractors.manager_ownership import extract_manager_ownership
from fund_agent.fund.extractors.performance import extract_performance
from fund_agent.fund.extractors.profile import extract_profile
from tests.fund.small_golden_oracle_helpers import (
    ACCESS_BOUNDARY_FALSE_KEYS,
    BOND_TOP_HOLDING_CONTRACT_VERSION,
    EQUITY_LIKE_HOLDINGS_ROWS,
    EXPECTED_ACCEPTED_FUND_CODES,
    EXPECTED_FIELD_GROUPS,
    EXPECTED_REPORT_YEAR,
    EXPECTED_SCHEMA_VERSION,
    FORBIDDEN_RETAINED_KEYS,
    ORACLE_PATH,
    ORACLE_TOP_LEVEL_KEYS,
    RISK_CONTRACT_VERSION,
    SYNTHETIC_FIXTURE_ROOT,
    TARGET_FUND_HOLDING_CONTRACT_VERSION,
    adapt_raw_holding_row as _adapt_raw_holding_row,
    bond_top_holding_expected_row as _bond_top_holding_expected_row,
    build_report_from_oracle_row as _build_report_from_oracle_row,
    iter_nested_keys as _iter_nested_keys,
    load_json as _load_json,
    load_oracle as _load_oracle,
    manager_expected_entries as _manager_expected_entries,
    oracle_expected as _expected,
    oracle_field as _field,
    oracle_rows_by_fund_code as _oracle_rows_by_fund_code,
    page_from_anchor as _page_from_anchor,
    risk_expected_text as _risk_expected_text,
    synthetic_expected_fields_paths as _synthetic_expected_fields_paths,
    target_fund_holding_expected_row as _target_fund_holding_expected_row,
    holdings_expected_row as _holdings_expected_row,
)

MANAGER_CONTRACT_VERSION = "portfolio_manager_tenure_list.v1"


def test_oracle_boundary_is_retained_excerpt_only_for_accepted_rows() -> None:
    """验证 accepted oracle 的行集合、字段完整性和 retention 边界。

    参数：
        无。

    返回：
        无。

    异常：
        AssertionError: oracle 形状或边界越过当前 gate。
    """

    oracle = _load_oracle()
    rows_by_fund_code = _oracle_rows_by_fund_code()

    assert set(oracle) == ORACLE_TOP_LEVEL_KEYS
    assert oracle["schema_version"] == EXPECTED_SCHEMA_VERSION
    assert set(rows_by_fund_code) == EXPECTED_ACCEPTED_FUND_CODES
    assert len(oracle["rows"]) == len(EXPECTED_ACCEPTED_FUND_CODES)
    for row in rows_by_fund_code.values():
        assert row["report_year"] == EXPECTED_REPORT_YEAR
        assert row["document_kind"] == "annual_report"
        assert set(row["fields"]) == EXPECTED_FIELD_GROUPS
        for field_group in row["fields"].values():
            assert field_group["expected"] not in ("", None, [], {})
            assert field_group["anchor"]
            assert field_group["excerpt"]
            assert len(str(field_group["excerpt"])) < 300

    access_boundary = oracle["access_boundary"]
    retention_boundary = oracle["retention_boundary"]
    for key in ACCESS_BOUNDARY_FALSE_KEYS:
        assert access_boundary[key] is False
    assert retention_boundary["full_pdf_retained"] is False
    assert retention_boundary["full_page_text_retained"] is False
    assert FORBIDDEN_RETAINED_KEYS.isdisjoint(_iter_nested_keys(oracle))


def test_synthetic_unmatched_expected_fields_are_excluded_from_correctness_source() -> None:
    """验证旧 synthetic/unmatched fixture 不能作为 correctness oracle。

    参数：
        无。

    返回：
        无。

    异常：
        AssertionError: synthetic fixture 被错误赋予 source identity 或 correctness 资格。
    """

    assert ORACLE_PATH.name != "expected_fields.json"
    assert SYNTHETIC_FIXTURE_ROOT not in ORACLE_PATH.parents
    expected_fields_paths = _synthetic_expected_fields_paths()

    assert len(expected_fields_paths) == len(EXPECTED_ACCEPTED_FUND_CODES)
    for path in expected_fields_paths:
        expected_fields = _load_json(path)
        source_identity = expected_fields["source_identity"]

        assert expected_fields["fixture_source_kind"] == "synthetic"
        assert expected_fields["exact_numeric_correctness_allowed"] is False
        assert expected_fields["promotion_allowed"] is False
        assert expected_fields["fallback_invocation"] == "prohibited"
        assert source_identity["status"] == "unmatched_synthetic"
        assert source_identity["matched_source_document"] is False


@pytest.mark.parametrize("fund_code", sorted(EXPECTED_ACCEPTED_FUND_CODES))
def test_profile_extractor_matches_same_source_identity_benchmark_and_fee(
    fund_code: str,
) -> None:
    """验证 profile extractor 对同源身份、scale、benchmark 和费率字段的 exact correctness。

    参数：
        fund_code: 当前参数化基金代码。

    返回：
        无。

    异常：
        AssertionError: 当前 extractor 未匹配 accepted oracle 中可直接消费的字段。
    """

    row = _oracle_rows_by_fund_code()[fund_code]
    report = _build_report_from_oracle_row(row)
    profile = extract_profile(report)
    identity_expected = _expected(row, "identity")
    scale_expected = _expected(row, "scale")
    fee_expected = _expected(row, "fee")
    expected_units = scale_expected.get("target_share_units") or scale_expected.get("total_share_units")

    assert profile.basic_identity.value is not None
    assert profile.benchmark.value is not None
    assert profile.fee_schedule.value is not None
    assert profile.basic_identity.value["fund_code"] == identity_expected["fund_code"]
    assert profile.basic_identity.value["fund_name"] == identity_expected["fund_name"]
    assert profile.basic_identity.value["fund_scale"] == expected_units
    assert profile.benchmark.value["benchmark_text"] == _expected(row, "benchmark")
    assert profile.fee_schedule.value["management_fee"] == fee_expected["management_fee_rate"]
    assert profile.fee_schedule.value["custody_fee"] == fee_expected["custodian_fee_rate"]
    assert profile.basic_identity.anchors
    assert profile.benchmark.anchors
    assert profile.fee_schedule.anchors


@pytest.mark.parametrize("fund_code", sorted(EXPECTED_ACCEPTED_FUND_CODES))
def test_performance_extractor_matches_same_source_one_year_returns(
    fund_code: str,
) -> None:
    """验证 performance extractor 对同源年度收益率字段的 numeric correctness。

    参数：
        fund_code: 当前参数化基金代码。

    返回：
        无。

    异常：
        AssertionError: 当前 extractor 未匹配 accepted oracle 中的年度收益字段。
    """

    row = _oracle_rows_by_fund_code()[fund_code]
    report = _build_report_from_oracle_row(row)
    performance = extract_performance(report)
    return_expected = _expected(row, "return")

    assert performance.nav_benchmark_performance.value is not None
    assert performance.nav_benchmark_performance.extraction_mode == "direct"
    assert (
        performance.nav_benchmark_performance.value["nav_growth_rate"]
        == return_expected["target_share_one_year_nav_growth"]
    )
    assert (
        performance.nav_benchmark_performance.value["benchmark_return_rate"]
        == return_expected["one_year_benchmark_return"]
    )
    assert performance.nav_benchmark_performance.anchors


def test_performance_extractor_matches_same_source_tracking_error_when_present() -> None:
    """验证当前 extractor 可消费 110020 同源跟踪误差字段。

    参数：
        无。

    返回：
        无。

    异常：
        AssertionError: 当前 extractor 未匹配 accepted oracle 中的跟踪误差字段。
    """

    row = _oracle_rows_by_fund_code()["110020"]
    report = _build_report_from_oracle_row(row)
    performance = extract_performance(report)
    return_expected = _expected(row, "return")

    assert performance.tracking_error.value is not None
    assert performance.tracking_error.extraction_mode == "direct"
    assert performance.tracking_error.value.value_text == return_expected["annual_tracking_error"]
    assert performance.tracking_error.anchors


@pytest.mark.parametrize("fund_code", sorted(EXPECTED_ACCEPTED_FUND_CODES))
def test_manager_extractor_exposes_same_source_portfolio_manager_tenure_list(
    fund_code: str,
) -> None:
    """验证未来 manager roster 契约必须匹配同源 retained oracle。

    参数：
        fund_code: 当前参数化基金代码。

    返回：
        无。

    异常：
        AssertionError: 未来 manager roster 输出未匹配 accepted oracle。
        AttributeError: 当前 extractor 尚未暴露 `portfolio_managers` 输出面。
    """

    row = _oracle_rows_by_fund_code()[fund_code]
    report = _build_report_from_oracle_row(row, include_manager=True)
    manager_result = extract_manager_ownership(report)
    expected_entries = _manager_expected_entries(row)

    portfolio_managers = manager_result.portfolio_managers

    assert portfolio_managers.extraction_mode == "direct"
    assert portfolio_managers.value is not None
    assert portfolio_managers.value["schema_version"] == MANAGER_CONTRACT_VERSION
    assert portfolio_managers.value["fund_code"] == fund_code
    assert portfolio_managers.value["report_year"] == EXPECTED_REPORT_YEAR
    actual_entries = portfolio_managers.value["portfolio_managers"]
    assert len(actual_entries) == len(expected_entries)
    for actual_entry, expected_entry in zip(actual_entries, expected_entries, strict=True):
        assert actual_entry["name"] == expected_entry["name"]
        assert actual_entry["role"] == expected_entry["role"]
        assert actual_entry["start_date"] == expected_entry["start_date"]
        if "end_date" in expected_entry:
            assert actual_entry["end_date"] == expected_entry["end_date"]
        assert actual_entry["source_anchor"]["section_id"] == "§4"
        assert "4.1.2" in actual_entry["source_anchor"]["section_title"]
        assert expected_entry["name"] in actual_entry["source_anchor"]["row_locator"]
    assert portfolio_managers.anchors


@pytest.mark.parametrize("fund_code", sorted(EQUITY_LIKE_HOLDINGS_ROWS))
def test_holdings_extractor_matches_same_source_equity_like_top_row(
    fund_code: str,
) -> None:
    """验证 holdings extractor 对同源 equity-like 第一持仓行的 correctness。

    参数：
        fund_code: 当前参数化基金代码。

    返回：
        无。

    异常：
        AssertionError: 当前 extractor 未匹配 accepted oracle 中的持仓第一行。
    """

    row = _oracle_rows_by_fund_code()[fund_code]
    route = EQUITY_LIKE_HOLDINGS_ROWS[fund_code]
    report = _build_report_from_oracle_row(row, include_holdings=True)
    holdings = extract_holdings_share_change(report).holdings_snapshot
    holdings_expected = _holdings_expected_row(row, str(route["oracle_key"]))

    assert holdings.extraction_mode == "direct"
    assert holdings.value is not None
    assert holdings.value["top_holdings_status"] == route["status"]
    assert holdings.value["top_holdings_source"] == route["source"]
    top_holdings = holdings.value["top_holdings"]
    assert isinstance(top_holdings, list)
    assert top_holdings
    assert _adapt_raw_holding_row(top_holdings[0]) == holdings_expected
    assert holdings.anchors


def test_profile_extractor_exposes_same_source_risk_characteristic_text() -> None:
    """验证 profile extractor 对同源风险收益特征字段的 correctness。

    参数：
        无。

    返回：
        无。

    异常：
        AssertionError: 当前风险收益特征输出未匹配 accepted oracle。
    """

    rows_by_fund_code = _oracle_rows_by_fund_code()
    profiles = {
        fund_code: extract_profile(_build_report_from_oracle_row(rows_by_fund_code[fund_code]))
        for fund_code in sorted(EXPECTED_ACCEPTED_FUND_CODES)
    }
    for fund_code, profile in profiles.items():
        expected_text = _risk_expected_text(rows_by_fund_code[fund_code])
        risk_characteristic = profile.risk_characteristic_text

        assert risk_characteristic.extraction_mode == "direct"
        assert risk_characteristic.value is not None
        assert risk_characteristic.value["schema_version"] == RISK_CONTRACT_VERSION
        assert risk_characteristic.value["fund_code"] == fund_code
        assert risk_characteristic.value["report_year"] == EXPECTED_REPORT_YEAR
        assert risk_characteristic.value["risk_characteristic_text"] == expected_text
        assert risk_characteristic.value["source_anchors"]
        assert risk_characteristic.anchors


def test_holdings_extractor_exposes_same_source_bond_top_holding_row() -> None:
    """验证 holdings extractor 对同源债券第一持仓行的 correctness。

    参数：
        无。

    返回：
        无。

    异常：
        AssertionError: 当前债券持仓输出未匹配 accepted oracle。
    """

    fund_code = "006597"
    row = _oracle_rows_by_fund_code()[fund_code]
    report = _build_report_from_oracle_row(row, include_bond_holdings=True)
    holdings = extract_holdings_share_change(report).holdings_snapshot
    expected_row = _bond_top_holding_expected_row(row)

    assert holdings.extraction_mode == "direct"
    assert holdings.value is not None
    assert holdings.value["schema_version"] == BOND_TOP_HOLDING_CONTRACT_VERSION
    assert holdings.value["fund_code"] == fund_code
    assert holdings.value["report_year"] == EXPECTED_REPORT_YEAR
    bond_top_holdings = holdings.value["bond_top_holdings"]
    assert isinstance(bond_top_holdings, list)
    assert bond_top_holdings
    actual_row = bond_top_holdings[0]
    assert actual_row["code"] == expected_row["code"]
    assert actual_row["name"] == expected_row["name"]
    assert actual_row["fair_value_cny"] == expected_row["fair_value_cny"]
    assert actual_row["net_asset_ratio"] == expected_row["net_asset_ratio"]
    source_anchor = actual_row["source_anchor"]
    assert source_anchor["section_id"] == "§8"
    assert "前五名债券投资明细" in source_anchor["section_title"]
    assert source_anchor["page_number"] == _page_from_anchor(_field(row, "holdings")["anchor"])
    assert expected_row["code"] in source_anchor["row_locator"]
    assert expected_row["name"] in source_anchor["row_locator"]
    assert holdings.anchors


def test_holdings_extractor_exposes_same_source_target_fund_holding_row() -> None:
    """验证 holdings extractor 对同源目标基金持仓行的 correctness。

    参数：
        无。

    返回：
        无。

    异常：
        AssertionError: 未来目标基金持仓输出未匹配 accepted oracle。
    """

    fund_code = "110020"
    row = _oracle_rows_by_fund_code()[fund_code]
    report = _build_report_from_oracle_row(row, include_target_fund_holding=True)
    holdings = extract_holdings_share_change(report).holdings_snapshot
    expected_row = _target_fund_holding_expected_row(row)

    assert holdings.extraction_mode == "direct"
    assert holdings.value is not None
    assert holdings.value["schema_version"] == TARGET_FUND_HOLDING_CONTRACT_VERSION
    assert holdings.value["fund_code"] == fund_code
    assert holdings.value["report_year"] == EXPECTED_REPORT_YEAR
    target_fund_holdings = holdings.value["target_fund_holdings"]
    assert isinstance(target_fund_holdings, list)
    assert target_fund_holdings
    actual_row = target_fund_holdings[0]
    assert actual_row["name"] == expected_row["name"]
    assert actual_row["fair_value_cny"] == expected_row["fair_value_cny"]
    assert actual_row["net_asset_ratio"] == expected_row["net_asset_ratio"]
    assert "code" not in actual_row
    source_anchor = actual_row["source_anchor"]
    assert source_anchor["section_id"] == "§8"
    assert "期末投资目标基金明细" in source_anchor["section_title"]
    assert source_anchor["page_number"] == _page_from_anchor(_field(row, "holdings")["anchor"])
    assert expected_row["name"] in source_anchor["row_locator"]
    assert holdings.anchors
