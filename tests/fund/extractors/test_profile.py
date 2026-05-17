"""基础画像 extractor 测试。"""

from __future__ import annotations

from pathlib import Path

import pytest

import fund_agent.fund.extractors.profile as profile_module
from fund_agent.fund.documents.models import DocumentKey, ParsedAnnualReport, ReportSection
from fund_agent.fund.extractors.models import ExtractedField, ProfileExtractionResult
from fund_agent.fund.extractors.profile import extract_profile
from fund_agent.fund.fund_type import FundTypeClassification

_FIXTURE_DIR = Path(__file__).resolve().parents[2] / "fixtures" / "fund" / "extractors" / "profile"


def _load_fixture_text(filename: str) -> str:
    """读取基础画像测试夹具文本。

    Args:
        filename: 夹具文件名。

    Returns:
        夹具全文文本。

    Raises:
        FileNotFoundError: 夹具不存在时抛出。
        OSError: 夹具读取失败时抛出。
    """

    return (_FIXTURE_DIR / filename).read_text(encoding="utf-8")


def _build_report_from_fixture(filename: str, fund_code: str) -> ParsedAnnualReport:
    """把最小文本夹具构造成 `ParsedAnnualReport`。

    Args:
        filename: 夹具文件名。
        fund_code: 基金代码。

    Returns:
        构造后的年报对象。

    Raises:
        ValueError: 夹具缺少 `§1/§2` 时抛出。
    """

    raw_text = _load_fixture_text(filename)
    section_one_start = raw_text.index("§1 基金简介")
    section_two_start = raw_text.index("§2 基金简介")
    return ParsedAnnualReport(
        key=DocumentKey(fund_code=fund_code, year=2024),
        raw_text=raw_text,
        sections={
            "§1": ReportSection(
                section_id="§1",
                title="§1 基金简介",
                start_offset=section_one_start,
                end_offset=section_two_start,
                matched_rule="fixture",
                confidence=1.0,
            ),
            "§2": ReportSection(
                section_id="§2",
                title="§2 基金简介",
                start_offset=section_two_start,
                end_offset=len(raw_text),
                matched_rule="fixture",
                confidence=1.0,
            ),
        },
        tables=(),
    )


def _dummy_field() -> ExtractedField[dict[str, object]]:
    """构造顺序测试使用的占位字段。

    Args:
        无。

    Returns:
        最小可用的抽取字段。

    Raises:
        无显式抛出。
    """

    return ExtractedField(value={}, anchors=(), extraction_mode="direct", note=None)


def test_extract_profile_classifies_before_general_field_builders(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """验证基金类型识别先于通用字段构造执行。

    Args:
        monkeypatch: pytest 提供的运行时打补丁工具。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当分类未先于通用字段构造执行时抛出。
    """

    report = _build_report_from_fixture("active_fund_profile.txt", "110011")
    call_order: list[str] = []

    def _fake_classify(_report: ParsedAnnualReport) -> FundTypeClassification:
        call_order.append("classify")
        return FundTypeClassification("active_fund", ("测试分类依据",))

    def _fake_build_basic_identity(
        _report: ParsedAnnualReport,
        _classification: FundTypeClassification,
    ) -> ExtractedField[dict[str, object]]:
        call_order.append("basic")
        return _dummy_field()

    def _fake_build_product_profile(_report: ParsedAnnualReport) -> ExtractedField[dict[str, object]]:
        call_order.append("product")
        return _dummy_field()

    def _fake_build_benchmark(_report: ParsedAnnualReport) -> ExtractedField[dict[str, object]]:
        call_order.append("benchmark")
        return _dummy_field()

    def _fake_build_fee_schedule(_report: ParsedAnnualReport) -> ExtractedField[dict[str, object]]:
        call_order.append("fee")
        return _dummy_field()

    monkeypatch.setattr(profile_module, "classify_fund_type", _fake_classify)
    monkeypatch.setattr(profile_module, "_build_basic_identity", _fake_build_basic_identity)
    monkeypatch.setattr(profile_module, "_build_product_profile", _fake_build_product_profile)
    monkeypatch.setattr(profile_module, "_build_benchmark", _fake_build_benchmark)
    monkeypatch.setattr(profile_module, "_build_fee_schedule", _fake_build_fee_schedule)

    result = extract_profile(report)

    assert isinstance(result, ProfileExtractionResult)
    assert call_order == ["classify", "basic", "product", "benchmark", "fee"]


def test_extract_profile_outputs_classification_basis_and_anchors_for_active_fund() -> None:
    """验证主动权益基金画像会输出分类依据与关键字段锚点。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当分类依据或关键字段锚点缺失时抛出。
    """

    report = _build_report_from_fixture("active_fund_profile.txt", "110011")

    result = extract_profile(report)

    assert result.basic_identity.value is not None
    assert result.basic_identity.value["classified_fund_type"] == "active_fund"
    assert result.basic_identity.value["classification_basis"]
    basic_anchor_labels = {anchor.row_locator for anchor in result.basic_identity.anchors}
    assert {"fund_scale", "fund_manager"} <= basic_anchor_labels
    assert result.benchmark.value == {
        "benchmark_text": "沪深300指数收益率×80%＋中债综合指数收益率×20%"
    }
    assert result.benchmark.anchors[0].section_id == "§2"
    fee_anchor_labels = {anchor.row_locator for anchor in result.fee_schedule.anchors}
    assert {"management_fee", "custody_fee"} <= fee_anchor_labels


@pytest.mark.parametrize(
    ("fixture_name", "fund_code", "expected_type"),
    (
        ("index_enhanced_profile.txt", "161725", "enhanced_index"),
        ("bond_fund_profile.txt", "000123", "bond_fund"),
    ),
)
def test_extract_profile_classifies_multiple_fund_types_without_code_special_case(
    fixture_name: str,
    fund_code: str,
    expected_type: str,
) -> None:
    """验证不同基金类型可由 `§1/§2` 规则识别，不依赖基金代码特判。

    Args:
        fixture_name: 夹具文件名。
        fund_code: 测试基金代码。
        expected_type: 期望基金类型标签。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当分类结果不符合预期时抛出。
    """

    report = _build_report_from_fixture(fixture_name, fund_code)

    result = extract_profile(report)

    assert result.basic_identity.value is not None
    assert result.basic_identity.value["classified_fund_type"] == expected_type
    assert result.basic_identity.value["classification_basis"]
