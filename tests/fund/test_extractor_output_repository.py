"""Extractor output repository 测试。

本测试只验证 `StructuredFundDataBundle` 到结构化 JSON 的显式仓库化输出，
不读取 FundDocumentRepository、PDF/cache、parser 原始产物、网络、provider 或 LLM。
"""

from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path

import pytest

from fund_agent.fund.extractor_output_repository import (
    EXTRACTOR_OUTPUT_FILENAME,
    EXTRACTOR_OUTPUT_SCHEMA_VERSION,
    ExtractorOutputRepository,
)
from fund_agent.fund.extractors.models import ExtractedField
from tests.services.test_fund_analysis_service import _bundle


def test_repository_saves_bundle_under_fund_report_type_year_path(tmp_path: Path) -> None:
    """验证仓库按 fund_code / report_type / year 组织输出路径。

    Args:
        tmp_path: pytest 临时目录。

    Returns:
        无返回值。

    Raises:
        AssertionError: 路径、schema 或 identity 不符合契约时抛出。
    """

    repository = ExtractorOutputRepository(root_dir=tmp_path)

    record = repository.save(bundle=_bundle())
    payload = json.loads(record.path.read_text(encoding="utf-8"))

    assert record.path == tmp_path / "110011" / "annual_report" / "2024" / EXTRACTOR_OUTPUT_FILENAME
    assert record.path.is_file()
    assert payload["schema_version"] == EXTRACTOR_OUTPUT_SCHEMA_VERSION
    assert payload["fund_code"] == "110011"
    assert payload["report_type"] == "annual_report"
    assert payload["report_year"] == 2024
    assert payload["bundle"]["fund_code"] == "110011"
    assert payload["bundle"]["report_year"] == 2024


def test_repository_roundtrip_preserves_extracted_field_missing_semantics(
    tmp_path: Path,
) -> None:
    """验证缺失字段语义不会在落盘后被折叠成空值。

    Args:
        tmp_path: pytest 临时目录。

    Returns:
        无返回值。

    Raises:
        AssertionError: `ExtractedField` 的 value/mode/note/anchors 丢失时抛出。
    """

    repository = ExtractorOutputRepository(root_dir=tmp_path)

    repository.save(bundle=_bundle())
    record = repository.load(fund_code="110011", report_type="annual_report", report_year=2024)
    index_profile = record.bundle_payload["index_profile"]

    assert isinstance(index_profile, dict)
    assert index_profile["value"] is None
    assert index_profile["anchors"] == []
    assert index_profile["extraction_mode"] == "missing"
    assert index_profile["note"] == "fixture"


def test_repository_roundtrip_preserves_anchors_nav_data_and_source_provenance(
    tmp_path: Path,
) -> None:
    """验证锚点、NAV 和公共来源 provenance 会保留在 bundle payload 中。

    Args:
        tmp_path: pytest 临时目录。

    Returns:
        无返回值。

    Raises:
        AssertionError: 关键 payload 字段缺失或被错误转换时抛出。
    """

    repository = ExtractorOutputRepository(root_dir=tmp_path)

    repository.save(bundle=_bundle())
    record = repository.load(fund_code="110011", report_type="annual_report", report_year=2024)
    basic_identity = record.bundle_payload["basic_identity"]
    nav_data = record.bundle_payload["nav_data"]
    source_provenance = record.bundle_payload["source_provenance"]

    assert isinstance(basic_identity, dict)
    assert basic_identity["anchors"][0]["source_kind"] == "annual_report"
    assert basic_identity["anchors"][0]["document_year"] == 2024
    assert basic_identity["anchors"][0]["section_id"] == "§1"
    assert isinstance(nav_data, dict)
    assert nav_data["fund_code"] == "110011"
    assert nav_data["records"] == [{"date": "2024-12-31", "nav": 1.2}]
    assert nav_data["cached"] is True
    assert isinstance(source_provenance, dict)
    assert source_provenance["source_provenance_schema_version"] == "repository_source_provenance.v2"
    assert source_provenance["fallback_eligibility"] == "not_applicable"


def test_repository_save_and_load_payload_use_same_sequence_shape(tmp_path: Path) -> None:
    """验证 save 返回 payload 与 load 返回 payload 使用一致 JSON array/list 形态。

    Args:
        tmp_path: pytest 临时目录。

    Returns:
        无返回值。

    Raises:
        AssertionError: save/load payload sequence 形态不一致时抛出。
    """

    repository = ExtractorOutputRepository(root_dir=tmp_path)

    saved_record = repository.save(bundle=_bundle())
    loaded_record = repository.load(fund_code="110011", report_type="annual_report", report_year=2024)
    saved_basic_identity = saved_record.bundle_payload["basic_identity"]
    loaded_basic_identity = loaded_record.bundle_payload["basic_identity"]

    assert isinstance(saved_basic_identity, dict)
    assert isinstance(loaded_basic_identity, dict)
    assert isinstance(saved_basic_identity["anchors"], list)
    assert saved_basic_identity["anchors"] == loaded_basic_identity["anchors"]
    assert saved_record.bundle_payload == loaded_record.bundle_payload


def test_repository_rejects_path_json_identity_mismatch(tmp_path: Path) -> None:
    """验证 load 时会拒绝路径身份与 JSON 身份不一致的文件。

    Args:
        tmp_path: pytest 临时目录。

    Returns:
        无返回值。

    Raises:
        AssertionError: 身份不一致未 fail-closed 时抛出。
    """

    repository = ExtractorOutputRepository(root_dir=tmp_path)
    record = repository.save(bundle=_bundle())
    payload = json.loads(record.path.read_text(encoding="utf-8"))
    payload["fund_code"] = "999999"
    record.path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    with pytest.raises(ValueError, match="identity mismatch"):
        repository.load(fund_code="110011", report_type="annual_report", report_year=2024)


@pytest.mark.parametrize(
    ("bundle_key", "bad_value"),
    (
        ("fund_code", "999999"),
        ("report_year", 2025),
    ),
)
def test_repository_rejects_bundle_identity_mismatch(
    tmp_path: Path,
    bundle_key: str,
    bad_value: object,
) -> None:
    """验证 bundle 内部身份与顶层身份不一致时 fail-closed。

    Args:
        tmp_path: pytest 临时目录。
        bundle_key: 要篡改的 bundle 身份字段。
        bad_value: 篡改后的值。

    Returns:
        无返回值。

    Raises:
        AssertionError: bundle 内部身份不一致未被拒绝时抛出。
    """

    repository = ExtractorOutputRepository(root_dir=tmp_path)
    record = repository.save(bundle=_bundle())
    payload = json.loads(record.path.read_text(encoding="utf-8"))
    payload["bundle"][bundle_key] = bad_value
    record.path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    with pytest.raises(ValueError, match="bundle identity mismatch"):
        repository.load(fund_code="110011", report_type="annual_report", report_year=2024)


def test_repository_rejects_unsupported_report_type(tmp_path: Path) -> None:
    """验证 v1 不接受非 annual_report 报告类型。

    Args:
        tmp_path: pytest 临时目录。

    Returns:
        无返回值。

    Raises:
        AssertionError: 非 annual report 未被拒绝时抛出。
    """

    repository = ExtractorOutputRepository(root_dir=tmp_path)

    with pytest.raises(ValueError, match="annual_report"):
        repository.path_for(fund_code="110011", report_type="semiannual_report", report_year=2024)
    with pytest.raises(ValueError, match="annual_report"):
        repository.save(bundle=_bundle(), report_type="quarterly_report")


def test_repository_rejects_malformed_fund_code_and_year(tmp_path: Path) -> None:
    """验证非法基金代码和年份会 fail-closed。

    Args:
        tmp_path: pytest 临时目录。

    Returns:
        无返回值。

    Raises:
        AssertionError: 非法 identity 未被拒绝时抛出。
    """

    repository = ExtractorOutputRepository(root_dir=tmp_path)

    with pytest.raises(ValueError, match="fund_code"):
        repository.path_for(fund_code="11011", report_type="annual_report", report_year=2024)
    with pytest.raises(ValueError, match="report_year"):
        repository.path_for(fund_code="110011", report_type="annual_report", report_year=0)


def test_repository_rejects_unknown_non_jsonable_bundle_value(tmp_path: Path) -> None:
    """验证未知对象不会被宽松字符串化写入 JSON。

    Args:
        tmp_path: pytest 临时目录。

    Returns:
        无返回值。

    Raises:
        AssertionError: 未知对象被错误写成 JSON 时抛出。
    """

    repository = ExtractorOutputRepository(root_dir=tmp_path)
    bundle = replace(
        _bundle(),
        basic_identity=ExtractedField(
            value={"fund_name": object()},
            anchors=(),
            extraction_mode="direct",
            note=None,
        ),
    )

    with pytest.raises(TypeError, match="bundle.basic_identity.value.fund_name"):
        repository.save(bundle=bundle)
