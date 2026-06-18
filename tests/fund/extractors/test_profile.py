"""基础画像 extractor 测试。"""

from __future__ import annotations

from pathlib import Path

import pytest

import fund_agent.fund.extractors.profile as profile_module
from fund_agent.fund.documents.models import DocumentKey, ParsedAnnualReport, ParsedTable, ReportSection
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


def _build_table_profile_report(fund_code: str, profile_table: ParsedTable, product_table: ParsedTable) -> ParsedAnnualReport:
    """构造真实年报 `§2` 表格式基础画像测试对象。

    Args:
        fund_code: 基金代码。
        profile_table: 基金身份键值表。
        product_table: 产品本质键值表。

    Returns:
        带 `§2` 表格的年报对象。

    Raises:
        ValueError: 章节标题缺失时抛出。
    """

    raw_text = "\n".join(
        (
            "§1 基金简介",
            "§2 基金简介",
            "本章字段主要位于表格。",
        )
    )
    section_two_start = raw_text.index("§2")
    return ParsedAnnualReport(
        key=DocumentKey(fund_code=fund_code, year=2024),
        raw_text=raw_text,
        sections={
            "§1": ReportSection(
                section_id="§1",
                title="§1 基金简介",
                start_offset=0,
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
        tables=(profile_table, product_table),
    )


def _build_report_with_extra_section(
    fund_code: str,
    profile_table: ParsedTable,
    product_table: ParsedTable,
    extra_section_id: str,
    extra_section_title: str,
    extra_section_text: str,
    extra_tables: tuple[ParsedTable, ...] = (),
) -> ParsedAnnualReport:
    """构造带 parser 可见额外章节的基础画像测试对象。

    Args:
        fund_code: 基金代码。
        profile_table: 基金身份键值表。
        product_table: 产品本质键值表。
        extra_section_id: 额外章节编号。
        extra_section_title: 额外章节标题。
        extra_section_text: 额外章节正文。
        extra_tables: 额外 parser 表格。

    Returns:
        带 `§2` 与额外章节的年报对象。

    Raises:
        ValueError: 章节标题缺失时抛出。
    """

    raw_text = "\n".join(
        (
            "§1 基金简介",
            "§2 基金简介",
            "本章字段主要位于表格。",
            extra_section_title,
            extra_section_text,
        )
    )
    section_two_start = raw_text.index("§2")
    extra_section_start = raw_text.index(extra_section_title)
    return ParsedAnnualReport(
        key=DocumentKey(fund_code=fund_code, year=2024),
        raw_text=raw_text,
        sections={
            "§1": ReportSection(
                section_id="§1",
                title="§1 基金简介",
                start_offset=0,
                end_offset=section_two_start,
                matched_rule="fixture",
                confidence=1.0,
            ),
            "§2": ReportSection(
                section_id="§2",
                title="§2 基金简介",
                start_offset=section_two_start,
                end_offset=extra_section_start,
                matched_rule="fixture",
                confidence=1.0,
            ),
            extra_section_id: ReportSection(
                section_id=extra_section_id,
                title=extra_section_title,
                start_offset=extra_section_start,
                end_offset=len(raw_text),
                matched_rule="fixture",
                confidence=1.0,
            ),
        },
        tables=(profile_table, product_table, *extra_tables),
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

    def _fake_build_risk_characteristic_text(_report: ParsedAnnualReport) -> ExtractedField[dict[str, object]]:
        call_order.append("risk")
        return _dummy_field()

    def _fake_build_benchmark(_report: ParsedAnnualReport) -> ExtractedField[dict[str, object]]:
        call_order.append("benchmark")
        return _dummy_field()

    def _fake_build_index_profile(
        _classification: FundTypeClassification,
        _benchmark: ExtractedField[dict[str, object]],
    ) -> ExtractedField[object]:
        call_order.append("index_profile")
        return ExtractedField(value=None, anchors=(), extraction_mode="missing", note="fixture")

    def _fake_build_fee_schedule(_report: ParsedAnnualReport) -> ExtractedField[dict[str, object]]:
        call_order.append("fee")
        return _dummy_field()

    monkeypatch.setattr(profile_module, "classify_fund_type", _fake_classify)
    monkeypatch.setattr(profile_module, "_build_basic_identity", _fake_build_basic_identity)
    monkeypatch.setattr(profile_module, "_build_product_profile", _fake_build_product_profile)
    monkeypatch.setattr(profile_module, "_build_risk_characteristic_text", _fake_build_risk_characteristic_text)
    monkeypatch.setattr(profile_module, "_build_benchmark", _fake_build_benchmark)
    monkeypatch.setattr(profile_module, "_build_index_profile", _fake_build_index_profile)
    monkeypatch.setattr(profile_module, "_build_fee_schedule", _fake_build_fee_schedule)

    result = extract_profile(report)

    assert isinstance(result, ProfileExtractionResult)
    assert call_order == ["classify", "benchmark", "basic", "product", "risk", "index_profile", "fee"]


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


def test_extract_profile_builds_pure_index_profile_from_benchmark_context() -> None:
    """验证纯指数基金生成 Tier 1 指数画像但不声称编制方法或成分股。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当指数画像层级或证据边界不符合预期时抛出。
    """

    report = _build_report_from_fixture("index_fund_profile.txt", "510300")

    result = extract_profile(report)

    assert result.basic_identity.value is not None
    assert result.basic_identity.value["classified_fund_type"] == "index_fund"
    assert result.index_profile.extraction_mode == "direct"
    assert result.index_profile.value is not None
    assert result.index_profile.value.benchmark_text == "沪深300指数收益率"
    assert result.index_profile.value.benchmark_identity_status == "identified"
    assert result.index_profile.value.benchmark_index_name == "沪深300指数"
    assert result.index_profile.value.methodology_availability == "benchmark_only"
    assert result.index_profile.value.constituents_availability == "benchmark_only"
    assert result.index_profile.anchors == result.benchmark.anchors


def test_extract_profile_builds_composite_index_profile_for_enhanced_index() -> None:
    """验证指数增强复合基准保留 composite 状态。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当复合基准被静默压成单一指数时抛出。
    """

    report = _build_report_from_fixture("index_enhanced_profile.txt", "161725")

    result = extract_profile(report)

    assert result.basic_identity.value is not None
    assert result.basic_identity.value["classified_fund_type"] == "enhanced_index"
    assert result.index_profile.value is not None
    assert result.index_profile.value.benchmark_identity_status == "composite"
    assert result.index_profile.value.benchmark_index_name is None
    assert result.index_profile.value.benchmark_component_text


@pytest.mark.parametrize(
    ("fund_code", "raw_benchmark_text", "expected_benchmark_text"),
    (
        (
            "017644",
            "中证1000指数收益率×95%+同期银行活期存款利\n率(税后)×5%",
            "中证1000指数收益率×95%+同期银行活期存款利率(税后)×5%",
        ),
        (
            "019918",
            "中证2000指数收益率*95%+中国人民银行人民币活期存款利率（税后）\n*5%",
            "中证2000指数收益率*95%+中国人民银行人民币活期存款利率（税后）*5%",
        ),
        (
            "004194",
            "中证1000指数收益率×95%+同期银行活期存款利率（税后）×5%",
            "中证1000指数收益率×95%+同期银行活期存款利率（税后）×5%",
        ),
        (
            "005313",
            "中证1000指数收益率*95%＋一年期人民币定期存款利率（税后）*5%",
            "中证1000指数收益率*95%＋一年期人民币定期存款利率（税后）*5%",
        ),
        (
            "019923",
            "中证2000指数收益率×95%＋人民币活期存款税后利率×5%",
            "中证2000指数收益率×95%＋人民币活期存款税后利率×5%",
        ),
    ),
)
def test_extract_profile_normalizes_benchmark_text_newlines_only_for_benchmark_path(
    fund_code: str,
    raw_benchmark_text: str,
    expected_benchmark_text: str,
) -> None:
    """验证基准文本路径会清理 PDF 表格视觉换行并保留指数画像语义。

    Args:
        fund_code: 基金代码。
        raw_benchmark_text: 表格中原始业绩比较基准。
        expected_benchmark_text: 期望输出的业绩比较基准。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当基准文本、锚点或复合基准语义漂移时抛出。
    """

    report = _build_table_profile_report(
        fund_code,
        ParsedTable(
            page_number=5,
            table_index=0,
            headers=("基金名称", "示例中证指数增强型证券投资基金"),
            rows=(("基金简称", "示例中证指数增强A"), ("基金主代码", fund_code)),
        ),
        ParsedTable(
            page_number=5,
            table_index=1,
            headers=("投资目标", "在控制跟踪误差的基础上追求超越标的指数的增强收益。"),
            rows=(
                ("投资范围", "本基金主要投资于标的指数成份股及备选成份股。"),
                ("投资策略", "采用指数增强策略，力争获得超越标的指数的收益。"),
                ("业绩比较基准", raw_benchmark_text),
            ),
        ),
    )

    result = extract_profile(report)

    assert result.benchmark.value == {"benchmark_text": expected_benchmark_text}
    benchmark_anchor = result.benchmark.anchors[0]
    assert benchmark_anchor.note == f"业绩比较基准：{expected_benchmark_text}"
    assert benchmark_anchor.section_id == "§2"
    assert benchmark_anchor.page_number == 5
    assert benchmark_anchor.table_id == "page-5-table-1"
    assert benchmark_anchor.row_locator == "benchmark"
    assert result.index_profile.value is not None
    assert result.index_profile.value.benchmark_text == expected_benchmark_text
    assert result.index_profile.value.benchmark_identity_status == "composite"
    assert result.index_profile.value.benchmark_index_name is None
    assert result.index_profile.value.benchmark_component_text == profile_module._benchmark_components(
        expected_benchmark_text
    )
    assert result.index_profile.value.methodology_availability == "benchmark_only"
    assert result.index_profile.value.constituents_availability == "benchmark_only"
    assert result.index_profile.value.source_tier == "benchmark_context"


def test_extract_profile_splits_composite_benchmark_with_chinese_and_multiply_separators() -> None:
    """验证复合基准拆分覆盖 `和` 与 `×` 分隔符。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当复合基准被误判为单一指数时抛出。
    """

    report = _build_table_profile_report(
        "510311",
        ParsedTable(
            page_number=5,
            table_index=0,
            headers=("基金名称", "示例沪深300指数证券投资基金"),
            rows=(("基金简称", "示例沪深300指数A"), ("基金主代码", "510311")),
        ),
        ParsedTable(
            page_number=5,
            table_index=1,
            headers=("投资目标", "紧密跟踪标的指数表现。"),
            rows=(
                ("投资范围", "投资于沪深300指数及中证500指数成份股。"),
                ("投资策略", "采用完全复制法跟踪标的指数。"),
                ("业绩比较基准", "沪深300指数收益率×80%和中证500指数收益率×20%"),
            ),
        ),
    )

    result = extract_profile(report)

    assert result.basic_identity.value is not None
    assert result.basic_identity.value["classified_fund_type"] == "index_fund"
    assert result.index_profile.value is not None
    assert result.index_profile.value.benchmark_identity_status == "composite"
    assert result.index_profile.value.benchmark_index_name is None
    assert result.index_profile.value.benchmark_component_text == (
        "沪深300指数收益率",
        "80%",
        "中证500指数收益率",
        "20%",
    )


def test_extract_profile_marks_non_index_profile_missing() -> None:
    """验证非指数基金显式返回不适用的指数画像字段。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当非指数基金仍生成指数画像时抛出。
    """

    report = _build_report_from_fixture("active_fund_profile.txt", "110011")

    result = extract_profile(report)

    assert result.index_profile.extraction_mode == "missing"
    assert result.index_profile.value is None
    assert result.index_profile.anchors == ()
    assert result.index_profile.note == "非指数基金不适用指数画像"


def test_extract_profile_reads_real_section_two_key_value_tables() -> None:
    """验证基础画像能读取真实年报 `§2` 键值表的表头与数据行。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当表格字段未被正确提取时抛出。
    """

    report = _build_table_profile_report(
        "510300",
        ParsedTable(
            page_number=5,
            table_index=0,
            headers=("基金名称", "华泰柏瑞沪深300交易型开放式指数证券投资基金"),
            rows=(
                ("基金简称", "华泰柏瑞沪深300ETF"),
                ("基金主代码", "510300"),
                ("报告期末基金份额总额", "8,900,000,000.00份"),
                ("基金管理人", "华泰柏瑞基金管理有限公司"),
            ),
        ),
        ParsedTable(
            page_number=5,
            table_index=1,
            headers=("投资目标", "紧密跟踪标的指数表现。"),
            rows=(
                ("投资范围", "投资于沪深300指数成份股。"),
                ("投资策略", "采用完全复制法。"),
                ("风险收益特征", "被动指数型产品，跟踪沪深300指数。"),
                ("业绩比较基准", "沪深300指数"),
                ("管理费率", "0.50%"),
                ("托管费率", "0.10%"),
            ),
        ),
    )

    result = extract_profile(report)

    assert result.basic_identity.value is not None
    assert result.basic_identity.value["fund_name"] == "华泰柏瑞沪深300交易型开放式指数证券投资基金"
    assert result.basic_identity.value["fund_code"] == "510300"
    assert result.basic_identity.value["management_company"] == "华泰柏瑞基金管理有限公司"
    assert result.basic_identity.value["custodian"] is None
    assert result.basic_identity.value["inception_date"] is None
    assert result.basic_identity.value["classified_fund_type"] == "index_fund"
    assert result.product_profile.value == {
        "investment_objective": "紧密跟踪标的指数表现。",
        "style_positioning": "被动指数型产品，跟踪沪深300指数。",
        "investment_scope": "投资于沪深300指数成份股。",
        "investment_strategy": "采用完全复制法。",
    }
    assert result.risk_characteristic_text.value == {
        "schema_version": "risk_characteristic_text.v1",
        "fund_code": "510300",
        "report_year": 2024,
        "risk_characteristic_text": "被动指数型产品，跟踪沪深300指数。",
        "source_anchors": [
            {
                "section_id": "§2",
                "page_number": 5,
                "table_id": "page-5-table-1",
                "row_locator": "risk_characteristic_text",
            }
        ],
    }
    assert result.benchmark.value == {"benchmark_text": "沪深300指数"}
    assert result.fee_schedule.value == {
        "management_fee": "0.50%",
        "custody_fee": "0.10%",
    }
    anchor_table_ids = {anchor.table_id for anchor in result.basic_identity.anchors}
    assert "page-5-table-0" in anchor_table_ids
    assert result.product_profile.anchors[0].table_id == "page-5-table-1"
    assert result.risk_characteristic_text.extraction_mode == "direct"
    assert result.risk_characteristic_text.anchors[0].table_id == "page-5-table-1"


def test_extract_profile_marks_risk_characteristic_text_missing_without_explicit_label() -> None:
    """验证未披露显式风险收益特征时不从基金类型或产品定位间接推断。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当风险收益特征未 fail-closed 为 missing 时抛出。
    """

    report = _build_report_from_fixture("active_fund_profile.txt", "110011")

    result = extract_profile(report)

    assert result.risk_characteristic_text.extraction_mode == "missing"
    assert result.risk_characteristic_text.value is None
    assert result.risk_characteristic_text.anchors == ()


def test_extract_profile_outputs_basic_identity_company_custodian_inception_with_anchors() -> None:
    """验证基础身份从 `§2` 表格输出管理人、托管人和合同生效日及锚点。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当新增基础身份字段或证据锚点缺失时抛出。
    """

    report = _build_table_profile_report(
        "004393",
        ParsedTable(
            page_number=5,
            table_index=0,
            headers=("基金名称", "安信企业价值优选混合型证券投资基金"),
            rows=(
                ("基金简称", "安信企业价值优选混合A"),
                ("基金主代码", "004393"),
                ("基金管理人", "安信基金管理有限责任公司"),
                ("基金托管人", "中国银行股份有限公司"),
                ("基金合同生效日", "2022 年 8 月 8 日"),
            ),
        ),
        ParsedTable(
            page_number=5,
            table_index=1,
            headers=("投资目标", "在严格控制风险的前提下，追求基金资产的长期稳健增值。"),
            rows=(
                ("投资范围", "投资于股票、债券等。"),
                ("业绩比较基准", "沪深300指数收益率×60%+中债综合指数收益率×40%"),
            ),
        ),
    )

    result = extract_profile(report)

    assert result.basic_identity.value is not None
    assert result.basic_identity.value["management_company"] == "安信基金管理有限责任公司"
    assert result.basic_identity.value["custodian"] == "中国银行股份有限公司"
    assert result.basic_identity.value["inception_date"] == "2022 年 8 月 8 日"
    anchors = {anchor.row_locator: anchor for anchor in result.basic_identity.anchors}
    assert anchors["management_company"].section_id == "§2"
    assert anchors["management_company"].table_id == "page-5-table-0"
    assert anchors["management_company"].note == "基金管理人：安信基金管理有限责任公司"
    assert anchors["custodian"].table_id == "page-5-table-0"
    assert anchors["inception_date"].table_id == "page-5-table-0"


def test_extract_profile_fee_schedule_fallback_reads_74102_text_when_section_seven_absent() -> None:
    """验证 `§2` 缺费率时按 parser 可见 `7.4.10.2` 文本 fallback。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 fallback 依赖 `§7` 或未输出标量费率时抛出。
    """

    report = _build_report_with_extra_section(
        "004393",
        ParsedTable(
            page_number=5,
            table_index=0,
            headers=("基金名称", "安信企业价值优选混合型证券投资基金"),
            rows=(("基金简称", "安信企业价值优选混合A"), ("基金主代码", "004393")),
        ),
        ParsedTable(
            page_number=5,
            table_index=1,
            headers=("投资目标", "追求基金资产长期稳健增值。"),
            rows=(("业绩比较基准", "沪深300指数收益率×60%+中债综合指数收益率×40%"),),
        ),
        "§5",
        "§5 财务报表附注",
        "\n".join(
            (
                "7.4.10.2 基金费用计提方法、计提标准和支付方式",
                "7.4.10.2.1 基金管理费",
                "本基金的管理费按前一日基金资产净值的 1.20% 年费率计提。",
                "7.4.10.2.2 基金托管费",
                "本基金的托管费按前一日基金资产净值的 0.20% 年费率计提。",
                "7.4.10.3 其他费用",
            )
        ),
    )

    result = extract_profile(report)

    assert result.fee_schedule.value == {
        "management_fee": "1.20%",
        "custody_fee": "0.20%",
    }
    anchors = {anchor.row_locator: anchor for anchor in result.fee_schedule.anchors}
    assert anchors["management_fee"].section_id == "§5"
    assert anchors["management_fee"].table_id is None
    assert anchors["management_fee"].note == "7.4.10.2.1 基金管理费：1.20%"
    assert anchors["custody_fee"].section_id == "§5"
    assert anchors["custody_fee"].note == "7.4.10.2.2 基金托管费：0.20%"


def test_extract_profile_fee_schedule_fallback_reads_74102_table_semantics() -> None:
    """验证 fallback 可从表格语义读取 `7.4.10.2` 管理费和托管费。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当表格语义 fallback 未提取费率时抛出。
    """

    fee_table = ParsedTable(
        page_number=42,
        table_index=3,
        headers=("项目", "计提标准"),
        rows=(
            ("7.4.10.2.1 基金管理费", "按前一日基金资产净值的 1.20% 年费率计提"),
            ("7.4.10.2.2 基金托管费", "按前一日基金资产净值的 0.20% 年费率计提"),
        ),
    )
    report = _build_report_with_extra_section(
        "004393",
        ParsedTable(
            page_number=5,
            table_index=0,
            headers=("基金名称", "安信企业价值优选混合型证券投资基金"),
            rows=(("基金简称", "安信企业价值优选混合A"), ("基金主代码", "004393")),
        ),
        ParsedTable(
            page_number=5,
            table_index=1,
            headers=("投资目标", "追求基金资产长期稳健增值。"),
            rows=(("业绩比较基准", "沪深300指数收益率×60%+中债综合指数收益率×40%"),),
        ),
        "§5",
        "§5 财务报表附注",
        "7.4.10.2 基金费用计提方法、计提标准和支付方式",
        (fee_table,),
    )

    result = extract_profile(report)

    assert result.fee_schedule.value == {
        "management_fee": "1.20%",
        "custody_fee": "0.20%",
    }
    anchors = {anchor.row_locator: anchor for anchor in result.fee_schedule.anchors}
    assert anchors["management_fee"].table_id == "page-42-table-3"
    assert anchors["management_fee"].page_number == 42
    assert anchors["management_fee"].section_id == "§7.4.10.2.1"
    assert anchors["custody_fee"].table_id == "page-42-table-3"
    assert anchors["custody_fee"].section_id == "§7.4.10.2.2"


def test_extract_profile_fee_schedule_table_fallback_ignores_unbounded_fee_labels() -> None:
    """验证表格 fallback 不会被无目标子章节上下文的宽泛费率标签抢先命中。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当无关费率表覆盖目标 `7.4.10.2.x` 费率时抛出。
    """

    unrelated_fee_table = ParsedTable(
        page_number=20,
        table_index=0,
        headers=("项目", "说明"),
        rows=(
            ("其他基金管理费率说明", "同类产品管理费可能达到 3.00%"),
            ("其他产品托管费水平", "同类产品托管费可能达到 4.00%"),
        ),
    )
    target_fee_table = ParsedTable(
        page_number=42,
        table_index=3,
        headers=("项目", "计提标准"),
        rows=(
            ("7.4.10.2.1 基金管理费", "按前一日基金资产净值的 1.20% 年费率计提"),
            ("7.4.10.2.2 基金托管费", "按前一日基金资产净值的 0.20% 年费率计提"),
        ),
    )
    report = _build_report_with_extra_section(
        "004393",
        ParsedTable(
            page_number=5,
            table_index=0,
            headers=("基金名称", "安信企业价值优选混合型证券投资基金"),
            rows=(("基金简称", "安信企业价值优选混合A"), ("基金主代码", "004393")),
        ),
        ParsedTable(
            page_number=5,
            table_index=1,
            headers=("投资目标", "追求基金资产长期稳健增值。"),
            rows=(("业绩比较基准", "沪深300指数收益率×60%+中债综合指数收益率×40%"),),
        ),
        "§5",
        "§5 财务报表附注",
        "7.4.10.2 基金费用计提方法、计提标准和支付方式",
        (unrelated_fee_table, target_fee_table),
    )

    result = extract_profile(report)

    assert result.fee_schedule.value == {
        "management_fee": "1.20%",
        "custody_fee": "0.20%",
    }
    anchors = {anchor.row_locator: anchor for anchor in result.fee_schedule.anchors}
    assert anchors["management_fee"].table_id == "page-42-table-3"
    assert anchors["custody_fee"].table_id == "page-42-table-3"
    assert anchors["management_fee"].section_id == "§7.4.10.2.1"
    assert anchors["custody_fee"].section_id == "§7.4.10.2.2"


def test_extract_profile_fee_schedule_table_fallback_stays_inside_target_subsection() -> None:
    """验证表格 fallback 不会跨子章节把相同标签碰撞成错误费率。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当托管费从管理费子章节误抽取时抛出。
    """

    fee_table = ParsedTable(
        page_number=42,
        table_index=3,
        headers=("项目", "计提标准"),
        rows=(
            ("7.4.10.2.1 基金管理费", "管理费 1.20%，托管费另见下节。"),
            ("提示", "本行仍在管理费子章节，托管费历史水平 9.99% 不应命中。"),
            ("7.4.10.2.2 基金托管费", "托管费按前一日基金资产净值的 0.20% 年费率计提"),
        ),
    )
    report = _build_report_with_extra_section(
        "004393",
        ParsedTable(
            page_number=5,
            table_index=0,
            headers=("基金名称", "安信企业价值优选混合型证券投资基金"),
            rows=(("基金简称", "安信企业价值优选混合A"), ("基金主代码", "004393")),
        ),
        ParsedTable(
            page_number=5,
            table_index=1,
            headers=("投资目标", "追求基金资产长期稳健增值。"),
            rows=(("业绩比较基准", "沪深300指数收益率×60%+中债综合指数收益率×40%"),),
        ),
        "§5",
        "§5 财务报表附注",
        "7.4.10.2 基金费用计提方法、计提标准和支付方式",
        (fee_table,),
    )

    result = extract_profile(report)

    assert result.fee_schedule.value == {
        "management_fee": "1.20%",
        "custody_fee": "0.20%",
    }
    custody_anchor = {
        anchor.row_locator: anchor for anchor in result.fee_schedule.anchors
    }["custody_fee"]
    assert custody_anchor.note == (
        "7.4.10.2.2 基金托管费："
        "7.4.10.2.2 基金托管费 托管费按前一日基金资产净值的 0.20% 年费率计提"
    )


def test_extract_profile_fee_schedule_table_fallback_uses_target_subsection_anchor() -> None:
    """验证表格 fallback 使用目标子章节语义锚点而不是猜测 parser section。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当表格锚点使用无关章节猜测而非目标子章节时抛出。
    """

    fee_table = ParsedTable(
        page_number=42,
        table_index=3,
        headers=("项目", "计提标准"),
        rows=(
            ("7.4.10.2.1 基金管理费", "按前一日基金资产净值的 1.20% 年费率计提"),
            ("7.4.10.2.2 基金托管费", "按前一日基金资产净值的 0.20% 年费率计提"),
        ),
    )
    report = _build_report_with_extra_section(
        "004393",
        ParsedTable(
            page_number=5,
            table_index=0,
            headers=("基金名称", "安信企业价值优选混合型证券投资基金"),
            rows=(("基金简称", "安信企业价值优选混合A"), ("基金主代码", "004393")),
        ),
        ParsedTable(
            page_number=5,
            table_index=1,
            headers=("投资目标", "追求基金资产长期稳健增值。"),
            rows=(("业绩比较基准", "沪深300指数收益率×60%+中债综合指数收益率×40%"),),
        ),
        "§5",
        "§5 财务报表附注",
        "\n".join(
            (
                "7.4.10.2 基金费用计提方法、计提标准和支付方式",
                "7.4.10.2.1 基金管理费",
                "详见下表。",
                "7.4.10.2.2 基金托管费",
                "详见下表。",
            )
        ),
        (fee_table,),
    )

    result = extract_profile(report)

    anchors = {anchor.row_locator: anchor for anchor in result.fee_schedule.anchors}
    assert anchors["management_fee"].section_id == "§7.4.10.2.1"
    assert anchors["management_fee"].table_id == "page-42-table-3"
    assert anchors["custody_fee"].section_id == "§7.4.10.2.2"


def test_extract_profile_fee_schedule_keeps_section_two_values_without_fallback_drift() -> None:
    """验证 `§2` 已披露费率时不被 fallback 文本覆盖。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 direct 费率被 fallback 破坏时抛出。
    """

    report = _build_report_with_extra_section(
        "510300",
        ParsedTable(
            page_number=5,
            table_index=0,
            headers=("基金名称", "华泰柏瑞沪深300交易型开放式指数证券投资基金"),
            rows=(("基金简称", "华泰柏瑞沪深300ETF"), ("基金主代码", "510300")),
        ),
        ParsedTable(
            page_number=5,
            table_index=1,
            headers=("投资目标", "紧密跟踪标的指数表现。"),
            rows=(
                ("业绩比较基准", "沪深300指数"),
                ("管理费率", "0.50%"),
                ("托管费率", "0.10%"),
            ),
        ),
        "§5",
        "§5 财务报表附注",
        "\n".join(
            (
                "7.4.10.2.1 基金管理费",
                "错误候选 1.20%",
                "7.4.10.2.2 基金托管费",
                "错误候选 0.20%",
            )
        ),
    )

    result = extract_profile(report)

    assert result.fee_schedule.value == {
        "management_fee": "0.50%",
        "custody_fee": "0.10%",
    }
    assert {anchor.section_id for anchor in result.fee_schedule.anchors} == {"§2"}


def test_extract_profile_fee_schedule_combines_direct_and_fallback_when_partial() -> None:
    """验证 direct 与 fallback 可按缺失侧合并。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当局部 direct 或 fallback 锚点丢失时抛出。
    """

    report = _build_report_with_extra_section(
        "004393",
        ParsedTable(
            page_number=5,
            table_index=0,
            headers=("基金名称", "安信企业价值优选混合型证券投资基金"),
            rows=(("基金简称", "安信企业价值优选混合A"), ("基金主代码", "004393")),
        ),
        ParsedTable(
            page_number=5,
            table_index=1,
            headers=("投资目标", "追求基金资产长期稳健增值。"),
            rows=(
                ("业绩比较基准", "沪深300指数收益率×60%+中债综合指数收益率×40%"),
                ("管理费率", "1.00%"),
            ),
        ),
        "§5",
        "§5 财务报表附注",
        "\n".join(
            (
                "7.4.10.2.2 基金托管费",
                "本基金的托管费按前一日基金资产净值的 0.20% 年费率计提。",
            )
        ),
    )

    result = extract_profile(report)

    assert result.fee_schedule.value == {
        "management_fee": "1.00%",
        "custody_fee": "0.20%",
    }
    anchors = {anchor.row_locator: anchor for anchor in result.fee_schedule.anchors}
    assert anchors["management_fee"].section_id == "§2"
    assert anchors["management_fee"].table_id == "page-5-table-1"
    assert anchors["custody_fee"].section_id == "§5"
    assert anchors["custody_fee"].table_id is None


def test_extract_profile_fee_schedule_remains_missing_without_section_two_or_fallback_fee() -> None:
    """验证没有 direct 与 fallback 费率时 `fee_schedule` 仍为 missing。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当无费率披露被误抽取时抛出。
    """

    report = _build_report_with_extra_section(
        "004393",
        ParsedTable(
            page_number=5,
            table_index=0,
            headers=("基金名称", "安信企业价值优选混合型证券投资基金"),
            rows=(("基金简称", "安信企业价值优选混合A"), ("基金主代码", "004393")),
        ),
        ParsedTable(
            page_number=5,
            table_index=1,
            headers=("投资目标", "追求基金资产长期稳健增值。"),
            rows=(("业绩比较基准", "沪深300指数收益率×60%+中债综合指数收益率×40%"),),
        ),
        "§5",
        "§5 财务报表附注",
        "7.4.10.2 基金费用计提方法、计提标准和支付方式\n本节未列示管理费或托管费率。",
    )

    result = extract_profile(report)

    assert result.fee_schedule.value is None
    assert result.fee_schedule.anchors == ()
    assert result.fee_schedule.extraction_mode == "missing"
    assert result.fee_schedule.note == "§2 与 7.4.10.2 均未披露管理费/托管费"


def test_extract_profile_prefers_bond_name_before_mixed_index_benchmark() -> None:
    """验证债券基金不会因基准含股票指数而误判为指数基金。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当债券基金分类错误时抛出。
    """

    report = _build_table_profile_report(
        "000171",
        ParsedTable(
            page_number=5,
            table_index=0,
            headers=("基金名称", "易方达裕丰回报债券型证券投资基金"),
            rows=(("基金简称", "易方达裕丰回报债券A"), ("基金主代码", "000171")),
        ),
        ParsedTable(
            page_number=5,
            table_index=1,
            headers=("投资目标", "本基金主要投资于债券资产。"),
            rows=(
                ("投资范围", "本基金主要投资于债券资产，可少量投资股票。"),
                ("业绩比较基准", "中债新综合财富指数收益率*90%+沪深300指数收益率*10%"),
            ),
        ),
    )

    result = extract_profile(report)

    assert result.basic_identity.value is not None
    assert result.basic_identity.value["classified_fund_type"] == "bond_fund"


def test_extract_profile_classifies_004393_like_mixed_fund_as_active_not_index() -> None:
    """验证 004393 风格混合基金不会因比较基准指数名称误判为指数基金。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当比较基准中的指数名称触发指数基金误判时抛出。
    """

    report = _build_table_profile_report(
        "004393",
        ParsedTable(
            page_number=5,
            table_index=0,
            headers=("基金名称", "安信企业价值优选混合型证券投资基金"),
            rows=(("基金简称", "安信企业价值优选混合A"), ("基金主代码", "004393")),
        ),
        ParsedTable(
            page_number=5,
            table_index=1,
            headers=("投资目标", "在严格控制风险的前提下，追求基金资产的长期稳健增值。"),
            rows=(
                (
                    "业绩比较基准",
                    "沪深300指数收益率×60%+恒生指数收益率（经汇率调整后）×20%+中债综合（全价）指数收益率×20%",
                ),
            ),
        ),
    )

    result = extract_profile(report)

    assert result.basic_identity.value is not None
    assert result.basic_identity.value["classified_fund_type"] == "active_fund"
    assert result.basic_identity.value["classified_fund_type"] != "index_fund"


def test_extract_profile_does_not_treat_tracking_market_dynamics_as_index() -> None:
    """验证“紧密跟踪市场动态”不会被当作指数基金策略证据。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当泛化跟踪表述触发指数基金误判时抛出。
    """

    report = _build_table_profile_report(
        "019999",
        ParsedTable(
            page_number=5,
            table_index=0,
            headers=("基金名称", "示例灵活配置混合型证券投资基金"),
            rows=(("基金简称", "示例灵活配置混合A"), ("基金主代码", "019999")),
        ),
        ParsedTable(
            page_number=5,
            table_index=1,
            headers=("投资目标", "紧密跟踪市场动态，灵活调整投资组合。"),
            rows=(
                (
                    "业绩比较基准",
                    "沪深300指数收益率×60%+中债综合指数收益率×40%",
                ),
            ),
        ),
    )

    result = extract_profile(report)

    assert result.basic_identity.value is not None
    assert result.basic_identity.value["classified_fund_type"] == "active_fund"
    assert result.basic_identity.value["classified_fund_type"] != "index_fund"


def test_extract_profile_does_not_treat_generic_enhance_word_as_enhanced_index() -> None:
    """验证泛化“增强收益”表述不会把普通指数基金误判为指数增强。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当普通指数基金因泛化增强词被误判时抛出。
    """

    report = _build_table_profile_report(
        "510310",
        ParsedTable(
            page_number=5,
            table_index=0,
            headers=("基金名称", "示例沪深300指数证券投资基金"),
            rows=(("基金简称", "示例沪深300指数A"), ("基金主代码", "510310")),
        ),
        ParsedTable(
            page_number=5,
            table_index=1,
            headers=("投资目标", "紧密跟踪标的指数表现，并力争增强投资者长期持有体验。"),
            rows=(
                ("投资范围", "投资于沪深300指数成份股。"),
                ("投资策略", "采用完全复制法跟踪标的指数。"),
                ("业绩比较基准", "沪深300指数收益率"),
            ),
        ),
    )

    result = extract_profile(report)

    assert result.basic_identity.value is not None
    assert result.basic_identity.value["classified_fund_type"] == "index_fund"
    assert result.basic_identity.value["classified_fund_type"] != "enhanced_index"


def test_extract_profile_does_not_use_benchmark_for_qdii_or_fof_classification() -> None:
    """验证 QDII/FOF 顶层分类不由业绩比较基准单独触发。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当基准文本中的境外或 FOF 词触发顶层分类时抛出。
    """

    report = _build_table_profile_report(
        "019998",
        ParsedTable(
            page_number=5,
            table_index=0,
            headers=("基金名称", "示例灵活配置混合型证券投资基金"),
            rows=(("基金简称", "示例灵活配置混合A"), ("基金主代码", "019998")),
        ),
        ParsedTable(
            page_number=5,
            table_index=1,
            headers=("投资目标", "在严格控制风险的前提下追求长期稳健增值。"),
            rows=(
                ("投资范围", "本基金主要投资于境内股票、存托凭证和现金管理工具。"),
                ("投资策略", "采用主动管理策略。"),
                ("业绩比较基准", "境外权益指数收益率×20%+FOF基金指数收益率×10%+沪深300指数收益率×70%"),
            ),
        ),
    )

    result = extract_profile(report)

    assert result.basic_identity.value is not None
    assert result.basic_identity.value["classified_fund_type"] == "active_fund"
    assert result.basic_identity.value["classified_fund_type"] not in {"qdii_fund", "fof_fund"}


def test_extract_profile_uses_table_short_name_for_qdii_classification() -> None:
    """验证基金简称中的 QDII 标识可参与基金类型判断。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 QDII 基金分类错误时抛出。
    """

    report = _build_table_profile_report(
        "110011",
        ParsedTable(
            page_number=5,
            table_index=0,
            headers=("基金名称", "易方达优质精选混合型证券投资基金"),
            rows=(("基金简称", "易方达优质精选混合（QDII）"), ("基金主代码", "110011")),
        ),
        ParsedTable(
            page_number=5,
            table_index=1,
            headers=("投资目标", "精选优质企业。"),
            rows=(("业绩比较基准", "沪深300指数收益率×50%+中证香港300指数收益率×30%"),),
        ),
    )

    result = extract_profile(report)

    assert result.basic_identity.value is not None
    assert result.basic_identity.value["fund_name"] == "易方达优质精选混合型证券投资基金"
    assert result.basic_identity.value["classified_fund_type"] == "qdii_fund"


def test_extract_profile_preserves_qdii_enhanced_index_evidence() -> None:
    """验证 QDII 顶层分类会保留增强指数并发证据。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 QDII 增强指数证据被分类早返回吞掉时抛出。
    """

    report = _build_table_profile_report(
        "161128",
        ParsedTable(
            page_number=5,
            table_index=0,
            headers=("基金名称", "易方达标普500指数增强型证券投资基金（QDII）"),
            rows=(("基金简称", "易方达标普500增强QDII"), ("基金主代码", "161128")),
        ),
        ParsedTable(
            page_number=5,
            table_index=1,
            headers=("投资目标", "在控制跟踪误差的基础上追求超越标的指数的增强收益。"),
            rows=(
                ("投资范围", "本基金主要投资于标普500指数成份股及备选成份股。"),
                ("投资策略", "采用指数增强策略，力争获得超越标的指数的收益。"),
                ("业绩比较基准", "标普500指数收益率"),
            ),
        ),
    )

    result = extract_profile(report)

    assert result.basic_identity.value is not None
    assert result.basic_identity.value["classified_fund_type"] == "qdii_fund"
    basis_text = "\n".join(result.basic_identity.value["classification_basis"])
    assert "同时命中指数基金身份或策略证据" in basis_text
    assert "同时命中增强关键词" in basis_text


def test_extract_profile_preserves_fof_index_evidence() -> None:
    """验证 FOF 顶层分类会保留指数并发证据。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 FOF 指数证据被分类早返回吞掉时抛出。
    """

    report = _build_table_profile_report(
        "020001",
        ParsedTable(
            page_number=5,
            table_index=0,
            headers=("基金名称", "示例目标日期指数基金中基金（FOF）"),
            rows=(("基金简称", "示例目标日期指数FOF"), ("基金主代码", "020001")),
        ),
        ParsedTable(
            page_number=5,
            table_index=1,
            headers=("投资目标", "紧密跟踪目标日期基金指数表现。"),
            rows=(
                ("投资范围", "本基金主要投资于公开募集证券投资基金。"),
                ("投资策略", "采用抽样复制方法跟踪目标日期基金指数。"),
                ("业绩比较基准", "目标日期基金指数收益率"),
            ),
        ),
    )

    result = extract_profile(report)

    assert result.basic_identity.value is not None
    assert result.basic_identity.value["classified_fund_type"] == "fof_fund"
    basis_text = "\n".join(result.basic_identity.value["classification_basis"])
    assert "同时命中指数基金身份或策略证据" in basis_text
