"""验证 retained excerpt oracle 驱动的 row-field extractor correctness。

本测试只读取 accepted retained excerpt JSON 作为 correctness oracle，不读取 PDF、
不调用 FundDocumentRepository，不触发 source helper、fallback、provider 或网络路径。
见模板第 1 章“产品本质”和第 2 章 R=A+B-C 的字段级抽取边界。
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import pytest

from fund_agent.fund.documents.models import DocumentKey, ParsedAnnualReport, ParsedTable, ReportSection
from fund_agent.fund.extractors.holdings_share_change import extract_holdings_share_change
from fund_agent.fund.extractors.manager_ownership import extract_manager_ownership
from fund_agent.fund.extractors.performance import extract_performance
from fund_agent.fund.extractors.profile import extract_profile


REPO_ROOT = Path(__file__).resolve().parents[2]
ORACLE_PATH = (
    REPO_ROOT
    / "docs"
    / "reviews"
    / "mvp-small-golden-set-retained-excerpt-fixture-pdf-only-20260609.json"
)
SYNTHETIC_FIXTURE_ROOT = REPO_ROOT / "tests" / "fixtures" / "fund" / "small_golden_set"
EXPECTED_SCHEMA_VERSION = "fund-agent.small_golden_set_retained_excerpt_fixture.v1"
EXPECTED_REPORT_YEAR = 2024
EXPECTED_ACCEPTED_FUND_CODES = {"004393", "004194", "006597", "110020", "017641"}
EXPECTED_FIELD_GROUPS = {
    "identity",
    "benchmark",
    "manager",
    "scale",
    "fee",
    "return",
    "holdings",
    "risk",
}
ORACLE_TOP_LEVEL_KEYS = {
    "schema_version",
    "gate",
    "classification",
    "date",
    "source_identity_checkpoint",
    "local_pdf_directory",
    "access_boundary",
    "retention_boundary",
    "rows",
    "next_gate",
    "non_goals_preserved",
}
ACCESS_BOUNDARY_FALSE_KEYS = {
    "network_access_performed",
    "fund_document_repository_live_acquisition_performed",
    "fallback_invocation_performed",
    "extractor_modified",
    "fixture_projection_performed",
    "exact_numeric_correctness_accepted",
    "golden_readiness_promotion_performed",
}
FORBIDDEN_RETAINED_KEYS = {
    "full_pdf",
    "full_pdf_text",
    "full_pdf_content",
    "full_page_text",
    "page_text",
    "raw_page_text",
    "raw_pdf_text",
}
MANAGER_CONTRACT_VERSION = "portfolio_manager_tenure_list.v1"
RISK_CONTRACT_VERSION = "risk_characteristic_text.v1"
EQUITY_LIKE_HOLDINGS_ROWS = {
    "004393": {
        "oracle_key": "top_stock_table_row",
        "source": "top_ten",
        "status": "direct_top_ten",
    },
    "004194": {
        "oracle_key": "top_index_stock_table_row",
        "source": "all_stock_investment_details",
        "status": "direct_all_stock_details",
    },
    "017641": {
        "oracle_key": "top_equity_table_row",
        "source": "all_stock_investment_details",
        "status": "direct_all_stock_details",
    },
}
UNSUPPORTED_HOLDINGS_ROWS = {
    "006597": "top_bond_table_row",
    "110020": "target_etf_holding",
}
HOLDINGS_RAW_KEY_ADAPTER = {
    "code": "股票代码",
    "name": "股票名称",
    "fair_value_cny": "公允价值",
    "net_asset_ratio": "占基金资产净值比例",
}


def _load_json(path: Path) -> dict[str, Any]:
    """读取本地 JSON 文件。

    参数：
        path: 本地 JSON 文件路径。

    返回：
        解析后的 JSON 字典。

    异常：
        FileNotFoundError: 文件不存在。
        json.JSONDecodeError: 文件不是合法 JSON。
    """

    with path.open(encoding="utf-8") as input_file:
        return json.load(input_file)


def _load_oracle() -> dict[str, Any]:
    """读取当前 gate 唯一 correctness oracle。

    参数：
        无。

    返回：
        accepted retained excerpt fixture JSON。

    异常：
        FileNotFoundError: oracle 文件不存在。
        json.JSONDecodeError: oracle 文件不是合法 JSON。
    """

    return _load_json(ORACLE_PATH)


def _oracle_rows_by_fund_code() -> dict[str, dict[str, Any]]:
    """按基金代码索引 accepted oracle 行。

    参数：
        无。

    返回：
        以基金代码为 key 的 oracle 行字典。

    异常：
        KeyError: oracle 缺少 rows 或 fund_code。
    """

    return {row["fund_code"]: row for row in _load_oracle()["rows"]}


def _iter_nested_keys(value: Any) -> set[str]:
    """递归收集 JSON-like 结构中的全部字典 key。

    参数：
        value: JSON-like 值。

    返回：
        所有嵌套字典 key 的集合。

    异常：
        无显式抛出。
    """

    keys: set[str] = set()
    if isinstance(value, dict):
        keys.update(str(key) for key in value)
        for child in value.values():
            keys.update(_iter_nested_keys(child))
    elif isinstance(value, list):
        for child in value:
            keys.update(_iter_nested_keys(child))
    return keys


def _field(row: dict[str, Any], field_name: str) -> dict[str, Any]:
    """读取单个 accepted oracle field group。

    参数：
        row: accepted oracle 行。
        field_name: 字段组名称。

    返回：
        字段组字典。

    异常：
        KeyError: 行缺少 fields 或目标字段组。
    """

    return row["fields"][field_name]


def _expected(row: dict[str, Any], field_name: str) -> Any:
    """读取单个字段组的 expected 值。

    参数：
        row: accepted oracle 行。
        field_name: 字段组名称。

    返回：
        字段组 `expected` 值。

    异常：
        KeyError: 字段组缺少 expected。
    """

    return _field(row, field_name)["expected"]


def _page_from_anchor(anchor: str) -> int:
    """从 oracle anchor 中提取 PDF 页码作为 ParsedTable 页码。

    参数：
        anchor: accepted oracle 中的 anchor 文本。

    返回：
        页码；无法解析时返回 1。

    异常：
        无显式抛出。
    """

    match = re.search(r"PDF p(?P<page>\d+)", anchor)
    if match is None:
        return 1
    return int(match.group("page"))


def _risk_category_text(row: dict[str, Any]) -> str:
    """从 risk expected 派生基金类型识别可消费的类别文本。

    参数：
        row: accepted oracle 行。

    返回：
        用于最小 ParsedAnnualReport 的基金类型文本。

    异常：
        KeyError: risk 字段缺少 expected。
    """

    risk_value = str(_expected(row, "risk"))
    fund_name = str(_expected(row, "identity")["fund_name"])
    return f"{fund_name}；{risk_value}"


def _profile_table(row: dict[str, Any]) -> ParsedTable:
    """用 accepted oracle 构造当前 profile extractor 可消费的键值表。

    参数：
        row: accepted oracle 行。

    返回：
        `ParsedTable`，字段值均来自 accepted retained excerpt oracle。

    异常：
        KeyError: 必要字段组缺失。
    """

    identity = _expected(row, "identity")
    fee = _expected(row, "fee")
    scale = _expected(row, "scale")
    return ParsedTable(
        page_number=_page_from_anchor(_field(row, "identity")["anchor"]),
        table_index=0,
        headers=("项目", "内容"),
        rows=(
            ("基金名称", str(identity["fund_name"])),
            ("基金主代码", str(identity["fund_code"])),
            ("基金类型", _risk_category_text(row)),
            ("风险收益特征", _risk_expected_text(row)),
            ("报告期末基金份额总额", str(scale.get("target_share_units") or scale.get("total_share_units") or "")),
            ("业绩比较基准", str(_expected(row, "benchmark"))),
            ("管理费", str(fee["management_fee_rate"])),
            ("托管费", str(fee["custodian_fee_rate"])),
        ),
    )


def _performance_table(row: dict[str, Any]) -> ParsedTable:
    """用 accepted oracle 构造当前 performance extractor 可消费的表现表。

    参数：
        row: accepted oracle 行。

    返回：
        `ParsedTable`，包含年度净值增长率、基准收益率和可选跟踪误差。

    异常：
        KeyError: return 字段缺少 expected。
    """

    return_expected = _expected(row, "return")
    headers = ("阶段", "份额净值增长率", "业绩比较基准收益率", "年化跟踪误差")
    rows = (
        (
            "过去一年",
            str(return_expected["target_share_one_year_nav_growth"]),
            str(return_expected["one_year_benchmark_return"]),
            str(return_expected.get("annual_tracking_error", "")),
        ),
    )
    return ParsedTable(
        page_number=_page_from_anchor(_field(row, "return")["anchor"]),
        table_index=1,
        headers=headers,
        rows=rows,
    )


def _manager_expected_entries(row: dict[str, Any]) -> list[dict[str, str]]:
    """读取 accepted oracle 中的基金经理任期列表。

    参数：
        row: accepted retained excerpt oracle 行。

    返回：
        基金经理任期条目列表。

    异常：
        KeyError: manager 字段缺少 expected。
    """

    return [{key: str(value) for key, value in entry.items()} for entry in _expected(row, "manager")]


def _risk_expected_text(row: dict[str, Any]) -> str:
    """读取 accepted oracle 中的风险收益特征文本。

    参数：
        row: accepted retained excerpt oracle 行。

    返回：
        `risk_characteristic_text.v1` 未来契约应暴露的风险收益特征文本。

    异常：
        KeyError: risk 字段缺少 expected。
    """

    return str(_expected(row, "risk"))


def _manager_table(row: dict[str, Any]) -> ParsedTable:
    """用 accepted oracle 构造未来 manager roster contract 可消费的最小表格。

    参数：
        row: accepted retained excerpt oracle 行。

    返回：
        `ParsedTable`，包含 `§4.1.2 基金经理简介` 的姓名、角色、任职日期和离任日期。

    异常：
        KeyError: manager 字段缺少 expected 或 anchor。
    """

    rows = tuple(
        (
            entry["name"],
            entry["role"],
            entry["start_date"],
            entry.get("end_date", ""),
        )
        for entry in _manager_expected_entries(row)
    )
    return ParsedTable(
        page_number=_page_from_anchor(_field(row, "manager")["anchor"]),
        table_index=3,
        headers=("姓名", "职务", "任职日期", "离任日期"),
        rows=rows,
    )


def _holdings_expected_row(row: dict[str, Any], oracle_key: str) -> dict[str, str]:
    """读取 accepted oracle 中单个持仓行。

    参数：
        row: accepted retained excerpt oracle 行。
        oracle_key: 持仓 expected 下的行形态 key。

    返回：
        canonical 持仓字段字典。

    异常：
        KeyError: holdings 字段或目标行形态缺失。
    """

    expected_row = _expected(row, "holdings")[oracle_key]
    return {key: str(value) for key, value in expected_row.items()}


def _holdings_table(row: dict[str, Any]) -> ParsedTable:
    """用 accepted oracle 构造当前 holdings extractor 可消费的最小表格。

    参数：
        row: accepted retained excerpt oracle 行。

    返回：
        `ParsedTable`，只包含当前 gate 接受的 equity-like holdings 第一行。

    异常：
        KeyError: 基金代码不属于当前 gate 的 equity-like holdings 子集。
    """

    route = EQUITY_LIKE_HOLDINGS_ROWS[str(row["fund_code"])]
    expected_row = _holdings_expected_row(row, str(route["oracle_key"]))
    if route["source"] == "top_ten":
        return ParsedTable(
            page_number=_page_from_anchor(_field(row, "holdings")["anchor"]),
            table_index=2,
            headers=("前十大重仓", "股票代码", "股票名称", "数量", "公允价值", "占基金资产净值比例"),
            rows=(
                (
                    "1",
                    expected_row["code"],
                    expected_row["name"],
                    "",
                    expected_row["fair_value_cny"],
                    expected_row["net_asset_ratio"],
                ),
            ),
        )
    return ParsedTable(
        page_number=_page_from_anchor(_field(row, "holdings")["anchor"]),
        table_index=2,
        headers=("股票代码", "股票名称", "数量", "公允价值", "占基金资产净值比例"),
        rows=(
            (
                expected_row["code"],
                expected_row["name"],
                "",
                expected_row["fair_value_cny"],
                expected_row["net_asset_ratio"],
            ),
        ),
    )


def _adapt_raw_holding_row(raw_row: dict[str, str]) -> dict[str, str]:
    """把当前 extractor 原始表头行映射为 oracle canonical keys。

    参数：
        raw_row: `holdings_snapshot.top_holdings` 中的原始表头字典。

    返回：
        仅用于本测试的 canonical 持仓字段字典。

    异常：
        KeyError: 当前 extractor 原始表头缺少本 gate 必需字段。
    """

    return {
        canonical_key: raw_row[raw_key]
        for canonical_key, raw_key in HOLDINGS_RAW_KEY_ADAPTER.items()
    }


def _build_report_from_oracle_row(
    row: dict[str, Any],
    *,
    include_manager: bool = False,
    include_holdings: bool = False,
) -> ParsedAnnualReport:
    """从 accepted oracle 行构造最小 parsed annual report。

    参数：
        row: accepted retained excerpt oracle 行。
        include_manager: 是否附加未来 manager roster contract 的 `§4.1.2` 表。
        include_holdings: 是否附加当前 gate 接受的 equity-like holdings 表。

    返回：
        可供当前 extractor 直接消费的 `ParsedAnnualReport`。

    异常：
        KeyError: 行缺少必要字段。
        ValueError: section marker 拼接异常时由字符串查找传播。
    """

    benchmark = str(_expected(row, "benchmark"))
    raw_parts = [
        "§1 基金简介",
        "§2 基金产品说明",
        f"基金类型：{_risk_category_text(row)}",
        f"风险收益特征：{_risk_expected_text(row)}",
        f"业绩比较基准：{benchmark}",
        "§3 主要财务指标、基金净值表现",
        "本节表现字段由同源 accepted oracle 表格承载。",
    ]
    if include_manager:
        raw_parts.extend(
            (
                "§4 管理人报告",
                "4.1.2 基金经理简介",
                "本节基金经理任期字段由同源 accepted oracle 表格承载。",
            )
        )
    raw_parts.extend(
        (
            "§8 投资组合报告",
            "本节持仓字段由同源 accepted oracle 表格承载。",
        )
    )
    raw_text = "\n".join(raw_parts)
    section_starts = {
        section_id: raw_text.index(section_id)
        for section_id in ("§1", "§2", "§3", "§8")
    }
    if include_manager:
        section_starts["§4"] = raw_text.index("§4")
    ordered_sections = sorted(section_starts, key=section_starts.__getitem__)
    section_ends = {
        section_id: (
            section_starts[ordered_sections[index + 1]]
            if index + 1 < len(ordered_sections)
            else len(raw_text)
        )
        for index, section_id in enumerate(ordered_sections)
    }
    tables = [_profile_table(row), _performance_table(row)]
    if include_manager:
        tables.append(_manager_table(row))
    if include_holdings:
        tables.append(_holdings_table(row))
    sections = {
        "§1": ReportSection(
            section_id="§1",
            title="§1 基金简介",
            start_offset=section_starts["§1"],
            end_offset=section_ends["§1"],
            matched_rule="accepted_retained_excerpt_oracle",
            confidence=1.0,
        ),
        "§2": ReportSection(
            section_id="§2",
            title="§2 基金产品说明",
            start_offset=section_starts["§2"],
            end_offset=section_ends["§2"],
            matched_rule="accepted_retained_excerpt_oracle",
            confidence=1.0,
        ),
        "§3": ReportSection(
            section_id="§3",
            title="§3 主要财务指标、基金净值表现",
            start_offset=section_starts["§3"],
            end_offset=section_ends["§3"],
            matched_rule="accepted_retained_excerpt_oracle",
            confidence=1.0,
        ),
        "§8": ReportSection(
            section_id="§8",
            title="§8 投资组合报告",
            start_offset=section_starts["§8"],
            end_offset=section_ends["§8"],
            matched_rule="accepted_retained_excerpt_oracle",
            confidence=1.0,
        ),
    }
    if include_manager:
        sections["§4"] = ReportSection(
            section_id="§4",
            title="§4 管理人报告",
            start_offset=section_starts["§4"],
            end_offset=section_ends["§4"],
            matched_rule="accepted_retained_excerpt_oracle",
            confidence=1.0,
        )
    return ParsedAnnualReport(
        key=DocumentKey(
            fund_code=str(row["fund_code"]),
            year=int(row["report_year"]),
            document_kind=str(row["document_kind"]),
        ),
        raw_text=raw_text,
        sections=sections,
        tables=tuple(tables),
    )


def _synthetic_expected_fields_paths() -> list[Path]:
    """列出旧 synthetic fixture 的 expected_fields.json 路径。

    参数：
        无。

    返回：
        五行 synthetic fixture 路径列表。

    异常：
        无显式抛出。
    """

    return sorted(SYNTHETIC_FIXTURE_ROOT.glob(f"*_{EXPECTED_REPORT_YEAR}/expected_fields.json"))


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


@pytest.mark.xfail(strict=True, reason="same-source holdings row exists, but current gate excludes this row shape")
@pytest.mark.parametrize("fund_code", sorted(UNSUPPORTED_HOLDINGS_ROWS))
def test_same_source_holdings_rows_outside_equity_like_subset_remain_blocked(
    fund_code: str,
) -> None:
    """记录 006597 bond holding 与 110020 target ETF holding 仍不进 passing correctness。

    参数：
        fund_code: 当前参数化基金代码。

    返回：
        无。

    异常：
        AssertionError: 当前持仓行形态仍未形成默认 passing correctness assertion。
    """

    row = _oracle_rows_by_fund_code()[fund_code]
    holdings_expected = _holdings_expected_row(row, UNSUPPORTED_HOLDINGS_ROWS[fund_code])

    assert holdings_expected
    assert _field(row, "holdings")["anchor"]
    assert _field(row, "holdings")["excerpt"]
    assert fund_code not in UNSUPPORTED_HOLDINGS_ROWS
