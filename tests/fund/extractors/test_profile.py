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
    assert result.basic_identity.value["classified_fund_type"] == "index_fund"
    assert result.product_profile.value == {
        "investment_objective": "紧密跟踪标的指数表现。",
        "style_positioning": "被动指数型产品，跟踪沪深300指数。",
        "investment_scope": "投资于沪深300指数成份股。",
        "investment_strategy": "采用完全复制法。",
    }
    assert result.benchmark.value == {"benchmark_text": "沪深300指数"}
    assert result.fee_schedule.value == {
        "management_fee": "0.50%",
        "custody_fee": "0.10%",
    }
    anchor_table_ids = {anchor.table_id for anchor in result.basic_identity.anchors}
    assert "page-5-table-0" in anchor_table_ids
    assert result.product_profile.anchors[0].table_id == "page-5-table-1"


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
