"""验证 small golden set Slice C Option 2 的离线 parser/fixture mechanics。

本测试只读取本地 review JSON 与 fixture JSON，不导入生产仓库、来源、
provider、fallback、LLM 或网络相关模块。
"""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = (
    REPO_ROOT / "docs" / "reviews" / "mvp-small-golden-set-manifest-20260608.json"
)
FIXTURE_ROOT = REPO_ROOT / "tests" / "fixtures" / "fund" / "small_golden_set"
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
EXACT_OR_NUMERIC_ASSERTIONS = {"exact", "normalized_text", "numeric_percent"}
EXPLICIT_DEGRADED_STATUSES = {"unavailable", "not_applicable", "deferred_policy"}
ALLOWED_IMPORT_ROOTS = {"__future__", "dataclasses", "json", "pathlib", "typing"}


@dataclass(frozen=True)
class ParsedFieldMechanics:
    """记录测试 helper 对单个 field group 的离线 mechanics 解析结果。

    参数：
        fund_code: 六位基金代码。
        field_name: 字段组名称。
        manifest_status: Slice A manifest 中声明的字段状态。
        fixture_status: Slice B fixture 中声明的字段状态。
        parser_status: Option 2 helper 输出的显式降级状态。
        reason: parser_status 的本地原因分类。

    返回：
        不适用。

    异常：
        不适用。
    """

    fund_code: str
    field_name: str
    manifest_status: str
    fixture_status: str
    parser_status: str
    reason: str


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


def _load_manifest_rows() -> dict[str, dict[str, Any]]:
    """按基金代码读取 Slice A manifest 行。

    参数：
        无。

    返回：
        以基金代码为 key 的 manifest 行字典。

    异常：
        FileNotFoundError: manifest 文件不存在。
        json.JSONDecodeError: manifest 不是合法 JSON。
        KeyError: manifest 缺少 rows 或 fund_code。
    """
    manifest = _load_json(MANIFEST_PATH)
    return {row["fund_code"]: row for row in manifest["rows"]}


def _load_expected_fields(fund_code: str) -> dict[str, Any]:
    """读取单只基金的 expected fields fixture。

    参数：
        fund_code: 六位基金代码。

    返回：
        解析后的 expected fields 字典。

    异常：
        FileNotFoundError: fixture 文件不存在。
        json.JSONDecodeError: fixture 不是合法 JSON。
    """
    return _load_json(FIXTURE_ROOT / f"{fund_code}_{EXPECTED_REPORT_YEAR}" / "expected_fields.json")


def _load_all_expected_fields() -> dict[str, dict[str, Any]]:
    """读取五行 small golden set expected fields。

    参数：
        无。

    返回：
        以基金代码为 key 的 expected fields 字典。

    异常：
        FileNotFoundError: 任一 fixture 文件不存在。
        json.JSONDecodeError: 任一 fixture 不是合法 JSON。
    """
    return {fund_code: _load_expected_fields(fund_code) for fund_code in EXPECTED_FUND_CODES}


def _parse_field_mechanics(
    fund_code: str,
    manifest_row: dict[str, Any],
    expected_fields: dict[str, Any],
) -> list[ParsedFieldMechanics]:
    """把 synthetic fixture 解析为显式离线 mechanics 状态。

    参数：
        fund_code: 六位基金代码。
        manifest_row: Slice A manifest 中对应行。
        expected_fields: Slice B expected fields fixture。

    返回：
        单行所有 field group 的 parser mechanics 输出。

    异常：
        KeyError: manifest 或 fixture 缺少必要字段。
    """
    parsed_fields: list[ParsedFieldMechanics] = []
    for field_name, field_group in expected_fields["field_groups"].items():
        manifest_status = manifest_row["field_expectations"][field_name]
        fixture_status = field_group["status"]
        parser_status, reason = _derive_parser_status(expected_fields, field_group)
        parsed_fields.append(
            ParsedFieldMechanics(
                fund_code=fund_code,
                field_name=field_name,
                manifest_status=manifest_status,
                fixture_status=fixture_status,
                parser_status=parser_status,
                reason=reason,
            )
        )
    return parsed_fields


def _derive_parser_status(
    expected_fields: dict[str, Any],
    field_group: dict[str, Any],
) -> tuple[str, str]:
    """根据 fixture 边界推导 Option 2 helper 的显式降级状态。

    参数：
        expected_fields: 单行 expected fields fixture。
        field_group: 单个字段组 fixture。

    返回：
        `(parser_status, reason)`，其中 parser_status 不表示 source truth 或 correctness。

    异常：
        KeyError: fixture 缺少必要边界字段。
    """
    fixture_status = field_group["status"]
    if fixture_status in {"unavailable", "not_applicable", "deferred_policy"}:
        return fixture_status, f"fixture_status_{fixture_status}"
    if expected_fields["source_identity"]["status"] != "matched":
        return "unavailable", "unsupported_unmatched_synthetic_fixture"
    if not expected_fields["exact_numeric_correctness_allowed"]:
        return "unavailable", "unsupported_exact_numeric_correctness_disabled"
    return "unavailable", "unsupported_option2_no_correctness_claim"


def _parse_all_field_mechanics() -> list[ParsedFieldMechanics]:
    """解析全部五行 fixture mechanics 输出。

    参数：
        无。

    返回：
        五行全部 field group 的 parser mechanics 输出。

    异常：
        FileNotFoundError: manifest 或 fixture 文件不存在。
        json.JSONDecodeError: manifest 或 fixture 不是合法 JSON。
        KeyError: manifest 或 fixture 缺少必要字段。
    """
    manifest_rows = _load_manifest_rows()
    fixture_rows = _load_all_expected_fields()
    parsed_fields: list[ParsedFieldMechanics] = []
    for fund_code, expected_fields in fixture_rows.items():
        parsed_fields.extend(
            _parse_field_mechanics(fund_code, manifest_rows[fund_code], expected_fields)
        )
    return parsed_fields


def test_parser_mechanics_reads_only_exact_five_local_fixture_rows() -> None:
    """验证 parser mechanics 只覆盖本地五行 fixture 目录与 2024 年份。

    参数：
        无。

    返回：
        无。

    异常：
        AssertionError: 行集合、目录集合或年份不符合 Option 2 边界。
    """
    manifest_rows = _load_manifest_rows()
    fixture_rows = _load_all_expected_fields()
    fixture_dirs = {path.name for path in FIXTURE_ROOT.iterdir() if path.is_dir()}

    assert set(manifest_rows) == EXPECTED_FUND_CODES
    assert set(fixture_rows) == EXPECTED_FUND_CODES
    assert fixture_dirs == {f"{fund_code}_{EXPECTED_REPORT_YEAR}" for fund_code in EXPECTED_FUND_CODES}
    for fund_code, expected_fields in fixture_rows.items():
        assert expected_fields["fund_code"] == fund_code
        assert expected_fields["report_year"] == EXPECTED_REPORT_YEAR


def test_parser_mechanics_preserves_fixture_fail_closed_metadata() -> None:
    """验证每行 fixture 保持 synthetic、unmatched、no-fallback、no-promotion 边界。

    参数：
        无。

    返回：
        无。

    异常：
        AssertionError: 任一行越界声明 source truth、fallback、promotion 或 correctness。
    """
    for expected_fields in _load_all_expected_fields().values():
        source_identity = expected_fields["source_identity"]

        assert expected_fields["promotion_allowed"] is False
        assert expected_fields["fallback_invocation"] == "prohibited"
        assert expected_fields["fixture_source_kind"] == "synthetic"
        assert source_identity["status"] == "unmatched_synthetic"
        assert source_identity["matched_source_document"] is False
        assert source_identity["fallback_used"] is False
        assert expected_fields["exact_numeric_correctness_allowed"] is False


def test_parser_mechanics_preserves_manifest_field_statuses() -> None:
    """验证 fixture 字段状态逐项继承 Slice A manifest。

    参数：
        无。

    返回：
        无。

    异常：
        AssertionError: 字段集合或字段状态与 Slice A manifest 不一致。
    """
    parsed_fields = _parse_all_field_mechanics()

    assert {field.field_name for field in parsed_fields} == EXPECTED_FIELD_GROUPS
    for field in parsed_fields:
        assert field.manifest_status == EXPECTED_STATUS_BY_FUND[field.fund_code][field.field_name]
        assert field.fixture_status == field.manifest_status

    qdii_fields = {
        field.field_name: field for field in parsed_fields if field.fund_code == "017641"
    }
    assert qdii_fields["holdings"].fixture_status == "unavailable"
    assert qdii_fields["risk"].fixture_status == "deferred_policy"


def test_parser_mechanics_never_uses_exact_or_numeric_assertion_kinds() -> None:
    """验证 synthetic/unmatched fixture 不承载 exact、normalized_text 或 numeric_percent。

    参数：
        无。

    返回：
        无。

    异常：
        AssertionError: 任一字段组出现 exact 或 numeric correctness 断言。
    """
    for expected_fields in _load_all_expected_fields().values():
        for field_group in expected_fields["field_groups"].values():
            assert field_group["assertion_kind"] not in EXACT_OR_NUMERIC_ASSERTIONS
            assert field_group["assertion_kind"] == "availability_status"


def test_parser_mechanics_degrades_unsupported_fields_explicitly() -> None:
    """验证 helper 输出显式降级状态，而不是把 unsupported 字段解析为成功。

    参数：
        无。

    返回：
        无。

    异常：
        AssertionError: helper 输出 silent success、空原因或非显式降级状态。
    """
    parsed_fields = _parse_all_field_mechanics()

    for field in parsed_fields:
        assert field.parser_status in EXPLICIT_DEGRADED_STATUSES
        assert field.parser_status not in {"expected", "success", "matched"}
        assert field.reason
        if field.fixture_status == "deferred_policy":
            assert field.parser_status == "deferred_policy"
            assert field.reason == "fixture_status_deferred_policy"
        elif field.fixture_status == "unavailable":
            assert field.parser_status == "unavailable"
            assert field.reason == "fixture_status_unavailable"
        else:
            assert field.parser_status == "unavailable"
            assert field.reason == "unsupported_unmatched_synthetic_fixture"


def test_parser_mechanics_test_file_uses_only_standard_library_imports() -> None:
    """验证本测试文件没有引入仓库、provider、source 或网络相关模块。

    参数：
        无。

    返回：
        无。

    异常：
        AssertionError: 测试文件出现非标准库或仓库模块导入。
    """
    test_source = Path(__file__).read_text(encoding="utf-8")
    imported_roots = set[str]()
    for line in test_source.splitlines():
        if line.startswith("import "):
            imported_roots.add(line.removeprefix("import ").split(".", maxsplit=1)[0])
        if line.startswith("from "):
            imported_roots.add(line.removeprefix("from ").split(maxsplit=1)[0].split(".")[0])

    assert imported_roots == ALLOWED_IMPORT_ROOTS
