"""small golden set retained excerpt oracle 测试辅助函数。

本模块只读取 accepted retained excerpt JSON，并从短摘录 oracle 构造测试用
`ParsedAnnualReport`。它不读取 PDF、不调用 `FundDocumentRepository`、
不触发 source helper、fallback、provider 或网络路径。
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from fund_agent.fund.documents.models import DocumentKey, ParsedAnnualReport, ParsedTable, ReportSection

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
EXPECTED_FUND_TYPE_BY_CODE = {
    "004393": "active_fund",
    "004194": "enhanced_index",
    "006597": "bond_fund",
    "110020": "index_fund",
    "017641": "qdii_fund",
}
EXPECTED_FUND_CATEGORY_TEXT_BY_CODE = {
    "004393": "混合型",
    "004194": "指数增强型",
    "006597": "债券型",
    "110020": "指数型",
    "017641": "QDII",
}
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
RISK_CONTRACT_VERSION = "risk_characteristic_text.v1"
BOND_TOP_HOLDING_CONTRACT_VERSION = "bond_top_holding_row.v1"
TARGET_FUND_HOLDING_CONTRACT_VERSION = "target_fund_holding_row.v1"
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
HOLDINGS_RAW_KEY_ADAPTER = {
    "code": "股票代码",
    "name": "股票名称",
    "fair_value_cny": "公允价值",
    "net_asset_ratio": "占基金资产净值比例",
}


def load_json(path: Path) -> dict[str, Any]:
    """读取本地 JSON 文件。

    Args:
        path: 本地 JSON 文件路径。

    Returns:
        解析后的 JSON 字典。

    Raises:
        FileNotFoundError: 文件不存在。
        json.JSONDecodeError: 文件不是合法 JSON。
    """

    with path.open(encoding="utf-8") as input_file:
        return json.load(input_file)


def load_oracle() -> dict[str, Any]:
    """读取当前 gate 唯一 correctness oracle。

    Args:
        无。

    Returns:
        accepted retained excerpt fixture JSON。

    Raises:
        FileNotFoundError: oracle 文件不存在。
        json.JSONDecodeError: oracle 文件不是合法 JSON。
    """

    return load_json(ORACLE_PATH)


def oracle_rows_by_fund_code() -> dict[str, dict[str, Any]]:
    """按基金代码索引 accepted oracle 行。

    Args:
        无。

    Returns:
        以基金代码为 key 的 oracle 行字典。

    Raises:
        KeyError: oracle 缺少 rows 或 fund_code。
    """

    return {row["fund_code"]: row for row in load_oracle()["rows"]}


def iter_nested_keys(value: Any) -> set[str]:
    """递归收集 JSON-like 结构中的全部字典 key。

    Args:
        value: JSON-like 值。

    Returns:
        所有嵌套字典 key 的集合。

    Raises:
        无显式抛出。
    """

    keys: set[str] = set()
    if isinstance(value, dict):
        keys.update(str(key) for key in value)
        for child in value.values():
            keys.update(iter_nested_keys(child))
    elif isinstance(value, list):
        for child in value:
            keys.update(iter_nested_keys(child))
    return keys


def oracle_field(row: dict[str, Any], field_name: str) -> dict[str, Any]:
    """读取单个 accepted oracle field group。

    Args:
        row: accepted oracle 行。
        field_name: 字段组名称。

    Returns:
        字段组字典。

    Raises:
        KeyError: 行缺少 fields 或目标字段组。
    """

    return row["fields"][field_name]


def oracle_expected(row: dict[str, Any], field_name: str) -> Any:
    """读取单个字段组的 expected 值。

    Args:
        row: accepted oracle 行。
        field_name: 字段组名称。

    Returns:
        字段组 `expected` 值。

    Raises:
        KeyError: 字段组缺少 expected。
    """

    return oracle_field(row, field_name)["expected"]


def page_from_anchor(anchor: str) -> int:
    """从 oracle anchor 中提取 PDF 页码作为 ParsedTable 页码。

    Args:
        anchor: accepted oracle 中的 anchor 文本。

    Returns:
        页码；无法解析时返回 1。

    Raises:
        无显式抛出。
    """

    match = re.search(r"PDF p(?P<page>\d+)", anchor)
    if match is None:
        return 1
    return int(match.group("page"))


def risk_category_text(row: dict[str, Any]) -> str:
    """从 risk expected 派生基金类型识别可消费的类别文本。

    Args:
        row: accepted oracle 行。

    Returns:
        用于最小 ParsedAnnualReport 的基金类型文本。

    Raises:
        KeyError: risk 字段缺少 expected。
    """

    risk_value = str(oracle_expected(row, "risk"))
    fund_name = str(oracle_expected(row, "identity")["fund_name"])
    return f"{fund_name}；{risk_value}"


def risk_expected_text(row: dict[str, Any]) -> str:
    """读取 accepted oracle 中的风险收益特征文本。

    Args:
        row: accepted retained excerpt oracle 行。

    Returns:
        `risk_characteristic_text.v1` 契约应暴露的风险收益特征文本。

    Raises:
        KeyError: risk 字段缺少 expected。
    """

    return str(oracle_expected(row, "risk"))


def fund_category_text(row: dict[str, Any]) -> str:
    """按 accepted fund_code/type mapping 生成基金类别识别文本。

    Args:
        row: accepted retained excerpt oracle 行。

    Returns:
        当前 classifier 可稳定识别的基金类别文本。

    Raises:
        KeyError: fund_code 不在当前 accepted small golden set。
    """

    return EXPECTED_FUND_CATEGORY_TEXT_BY_CODE[str(row["fund_code"])]


def profile_table(row: dict[str, Any]) -> ParsedTable:
    """用 accepted oracle 构造当前 profile extractor 可消费的键值表。

    Args:
        row: accepted oracle 行。

    Returns:
        `ParsedTable`，字段值均来自 accepted retained excerpt oracle。

    Raises:
        KeyError: 必要字段组缺失。
    """

    identity = oracle_expected(row, "identity")
    fee = oracle_expected(row, "fee")
    scale = oracle_expected(row, "scale")
    return ParsedTable(
        page_number=page_from_anchor(oracle_field(row, "identity")["anchor"]),
        table_index=0,
        headers=("项目", "内容"),
        rows=(
            ("基金名称", str(identity["fund_name"])),
            ("基金主代码", str(identity["fund_code"])),
            ("基金类型", fund_category_text(row)),
            ("风险收益特征", risk_expected_text(row)),
            ("报告期末基金份额总额", str(scale.get("target_share_units") or scale.get("total_share_units") or "")),
            ("业绩比较基准", str(oracle_expected(row, "benchmark"))),
            ("管理费", str(fee["management_fee_rate"])),
            ("托管费", str(fee["custodian_fee_rate"])),
        ),
    )


def performance_table(row: dict[str, Any]) -> ParsedTable:
    """用 accepted oracle 构造当前 performance extractor 可消费的表现表。

    Args:
        row: accepted oracle 行。

    Returns:
        `ParsedTable`，包含年度净值增长率、基准收益率和可选跟踪误差。

    Raises:
        KeyError: return 字段缺少 expected。
    """

    return_expected = oracle_expected(row, "return")
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
        page_number=page_from_anchor(oracle_field(row, "return")["anchor"]),
        table_index=1,
        headers=headers,
        rows=rows,
    )


def manager_expected_entries(row: dict[str, Any]) -> list[dict[str, str]]:
    """读取 accepted oracle 中的基金经理任期列表。

    Args:
        row: accepted retained excerpt oracle 行。

    Returns:
        基金经理任期条目列表。

    Raises:
        KeyError: manager 字段缺少 expected。
    """

    return [{key: str(value) for key, value in entry.items()} for entry in oracle_expected(row, "manager")]


def manager_table(row: dict[str, Any]) -> ParsedTable:
    """用 accepted oracle 构造 manager roster contract 可消费的最小表格。

    Args:
        row: accepted retained excerpt oracle 行。

    Returns:
        `ParsedTable`，包含 `§4.1.2 基金经理简介` 的姓名、角色、任职日期和离任日期。

    Raises:
        KeyError: manager 字段缺少 expected 或 anchor。
    """

    rows = tuple(
        (
            entry["name"],
            entry["role"],
            entry["start_date"],
            entry.get("end_date", ""),
        )
        for entry in manager_expected_entries(row)
    )
    return ParsedTable(
        page_number=page_from_anchor(oracle_field(row, "manager")["anchor"]),
        table_index=3,
        headers=("姓名", "职务", "任职日期", "离任日期"),
        rows=rows,
    )


def holdings_expected_row(row: dict[str, Any], oracle_key: str) -> dict[str, str]:
    """读取 accepted oracle 中单个持仓行。

    Args:
        row: accepted retained excerpt oracle 行。
        oracle_key: 持仓 expected 下的行形态 key。

    Returns:
        canonical 持仓字段字典。

    Raises:
        KeyError: holdings 字段或目标行形态缺失。
    """

    expected_row = oracle_expected(row, "holdings")[oracle_key]
    return {key: str(value) for key, value in expected_row.items()}


def bond_top_holding_expected_row(row: dict[str, Any]) -> dict[str, str]:
    """读取 accepted oracle 中的首个债券持仓行。

    Args:
        row: accepted retained excerpt oracle 行。

    Returns:
        `bond_top_holding_row.v1` 契约的 canonical 债券持仓字段。

    Raises:
        KeyError: holdings 字段或 top_bond_table_row 缺失。
    """

    return holdings_expected_row(row, "top_bond_table_row")


def target_fund_holding_expected_row(row: dict[str, Any]) -> dict[str, str]:
    """读取 accepted oracle 中的目标基金持仓行。

    Args:
        row: accepted retained excerpt oracle 行。

    Returns:
        `target_fund_holding_row.v1` 契约的 canonical 目标基金持仓字段。

    Raises:
        KeyError: holdings 字段或 target_etf_holding 缺失。
    """

    return holdings_expected_row(row, "target_etf_holding")


def holdings_table(row: dict[str, Any]) -> ParsedTable:
    """用 accepted oracle 构造当前 holdings extractor 可消费的最小表格。

    Args:
        row: accepted retained excerpt oracle 行。

    Returns:
        `ParsedTable`，只包含当前 gate 接受的 equity-like holdings 第一行。

    Raises:
        KeyError: 基金代码不属于当前 gate 的 equity-like holdings 子集。
    """

    route = EQUITY_LIKE_HOLDINGS_ROWS[str(row["fund_code"])]
    expected_row = holdings_expected_row(row, str(route["oracle_key"]))
    if route["source"] == "top_ten":
        return ParsedTable(
            page_number=page_from_anchor(oracle_field(row, "holdings")["anchor"]),
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
        page_number=page_from_anchor(oracle_field(row, "holdings")["anchor"]),
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


def bond_top_holding_table(row: dict[str, Any]) -> ParsedTable:
    """用 accepted oracle 构造 bond top holding contract 可消费的最小表格。

    Args:
        row: accepted retained excerpt oracle 行。

    Returns:
        `ParsedTable`，包含 `§8.6 前五名债券投资明细` 的首个债券持仓行。

    Raises:
        KeyError: holdings 字段缺少 top_bond_table_row 或 anchor。
    """

    expected_row = bond_top_holding_expected_row(row)
    return ParsedTable(
        page_number=page_from_anchor(oracle_field(row, "holdings")["anchor"]),
        table_index=4,
        headers=("序号", "债券代码", "债券名称", "数量", "公允价值", "占基金资产净值比例"),
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


def target_fund_holding_table(row: dict[str, Any]) -> ParsedTable:
    """用 accepted oracle 构造 target-fund holding contract 可消费的最小表格。

    Args:
        row: accepted retained excerpt oracle 行。

    Returns:
        `ParsedTable`，包含 `§8.2 期末投资目标基金明细` 的目标基金持仓行。

    Raises:
        KeyError: holdings 字段缺少 target_etf_holding 或 anchor。
    """

    expected_row = target_fund_holding_expected_row(row)
    return ParsedTable(
        page_number=page_from_anchor(oracle_field(row, "holdings")["anchor"]),
        table_index=4,
        headers=("基金名称", "公允价值", "占基金资产净值比例"),
        rows=(
            (
                expected_row["name"],
                expected_row["fair_value_cny"],
                expected_row["net_asset_ratio"],
            ),
        ),
    )


def adapt_raw_holding_row(raw_row: dict[str, str]) -> dict[str, str]:
    """把当前 extractor 原始表头行映射为 oracle canonical keys。

    Args:
        raw_row: `holdings_snapshot.top_holdings` 中的原始表头字典。

    Returns:
        仅用于测试的 canonical 持仓字段字典。

    Raises:
        KeyError: 当前 extractor 原始表头缺少本 gate 必需字段。
    """

    return {
        canonical_key: raw_row[raw_key]
        for canonical_key, raw_key in HOLDINGS_RAW_KEY_ADAPTER.items()
    }


def build_report_from_oracle_row(
    row: dict[str, Any],
    *,
    include_manager: bool = False,
    include_holdings: bool = False,
    include_bond_holdings: bool = False,
    include_target_fund_holding: bool = False,
) -> ParsedAnnualReport:
    """从 accepted oracle 行构造最小 parsed annual report。

    Args:
        row: accepted retained excerpt oracle 行。
        include_manager: 是否附加 manager roster contract 的 `§4.1.2` 表。
        include_holdings: 是否附加当前 gate 接受的 equity-like holdings 表。
        include_bond_holdings: 是否附加 `bond_top_holding_row.v1` 的 `§8.6` 表。
        include_target_fund_holding: 是否附加 `target_fund_holding_row.v1` 的 `§8.2` 表。

    Returns:
        可供当前 extractor 直接消费的 `ParsedAnnualReport`。

    Raises:
        KeyError: 行缺少必要字段。
        ValueError: section marker 拼接异常时由字符串查找传播。
    """

    benchmark = str(oracle_expected(row, "benchmark"))
    raw_parts = [
        "§1 基金简介",
        "§2 基金产品说明",
        f"基金类型：{fund_category_text(row)}",
        f"风险收益特征：{risk_expected_text(row)}",
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
    if include_bond_holdings:
        raw_parts.extend(
            (
                "8.6 前五名债券投资明细",
                "本节债券持仓字段由同源 accepted oracle 表格承载。",
            )
        )
    if include_target_fund_holding:
        raw_parts.extend(
            (
                "8.2 期末投资目标基金明细",
                "本节目标基金持仓字段由同源 accepted oracle 表格承载。",
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
    tables = [profile_table(row), performance_table(row)]
    if include_manager:
        tables.append(manager_table(row))
    if include_holdings:
        tables.append(holdings_table(row))
    if include_bond_holdings:
        tables.append(bond_top_holding_table(row))
    if include_target_fund_holding:
        tables.append(target_fund_holding_table(row))
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


def synthetic_expected_fields_paths() -> list[Path]:
    """列出旧 synthetic fixture 的 expected_fields.json 路径。

    Args:
        无。

    Returns:
        五行 synthetic fixture 路径列表。

    Raises:
        无显式抛出。
    """

    return sorted(SYNTHETIC_FIXTURE_ROOT.glob(f"*_{EXPECTED_REPORT_YEAR}/expected_fields.json"))
