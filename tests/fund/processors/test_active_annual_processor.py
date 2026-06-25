"""主动基金年报 processor 测试。"""

from __future__ import annotations

import ast
from pathlib import Path

from fund_agent.fund.documents.models import (
    AnnualReportMetadata,
    AnnualReportSourceMetadata,
    DocumentKey,
    ParsedAnnualReport,
    ParsedTable,
    ReportSection,
)
from fund_agent.fund.processors import (
    FIELD_FAMILY_MAPPINGS,
    ActiveFundAnnualProcessor,
    FundProcessorDispatchKey,
    FundProcessorInput,
)


def _dispatch_key() -> FundProcessorDispatchKey:
    """构造主动基金年报 processor 路由键。

    Args:
        无。

    Returns:
        S1 active annual dispatch key。

    Raises:
        无显式抛出。
    """

    return FundProcessorDispatchKey(
        fund_type="active_fund",
        report_type="annual_report",
        intermediate_kind="parsed_annual_report.v1",
        source_kind="annual_report",
        document_year=2024,
        fund_code="110011",
    )


def _unchecked_dispatch_key(
    *,
    fund_type: str = "active_fund",
    report_type: str = "annual_report",
    intermediate_kind: str = "parsed_annual_report.v1",
    processor_goal: str = "template_chapters_1_6_minimum_field_families",
) -> FundProcessorDispatchKey:
    """构造绕过 dataclass 校验的 dispatch key，用于测试防御性归因分支。

    Args:
        fund_type: 基金类型。
        report_type: 报告类型。
        intermediate_kind: 中间态类型。
        processor_goal: processor 目标。

    Returns:
        测试专用 dispatch key。

    Raises:
        无显式抛出。
    """

    key = object.__new__(FundProcessorDispatchKey)
    object.__setattr__(key, "fund_type", fund_type)
    object.__setattr__(key, "report_type", report_type)
    object.__setattr__(key, "intermediate_kind", intermediate_kind)
    object.__setattr__(key, "source_kind", "annual_report")
    object.__setattr__(key, "document_year", 2024)
    object.__setattr__(key, "fund_code", "110011")
    object.__setattr__(key, "processor_goal", processor_goal)
    return key


def _section_offsets(raw_text: str, titles: tuple[tuple[str, str], ...]) -> dict[str, ReportSection]:
    """按标题构造章节 offset。

    Args:
        raw_text: 年报文本。
        titles: `(section_id, title)` 元组。

    Returns:
        章节 ID 到 `ReportSection` 的映射。

    Raises:
        ValueError: 当标题不存在时抛出。
    """

    starts = [(section_id, title, raw_text.index(title)) for section_id, title in titles]
    sections: dict[str, ReportSection] = {}
    for index, (section_id, title, start) in enumerate(starts):
        end = starts[index + 1][2] if index + 1 < len(starts) else len(raw_text)
        sections[section_id] = ReportSection(
            section_id=section_id,
            title=title,
            start_offset=start,
            end_offset=end,
            matched_rule="fixture",
            confidence=1.0,
        )
    return sections


def _source_metadata() -> AnnualReportSourceMetadata:
    """构造来源元数据 fixture。

    Args:
        无。

    Returns:
        EID single-source 年报来源元数据。

    Raises:
        无显式抛出。
    """

    return AnnualReportSourceMetadata(
        source="eid",
        fund_code="110011",
        report_year=2024,
        selected_source="eid",
        source_mode="single_source_only",
        fallback_enabled=False,
        fallback_used=False,
        discovery_contract_version="fixture.v1",
    )


def _happy_report(
    *,
    include_tracking_error: bool = True,
    include_custody_fee: bool = True,
) -> ParsedAnnualReport:
    """构造覆盖六个字段族的 no-live synthetic ParsedAnnualReport。

    Args:
        include_tracking_error: 是否包含跟踪误差披露。
        include_custody_fee: 是否包含托管费率披露。

    Returns:
        只含内存文本和表格的年报 fixture。

    Raises:
        ValueError: 当章节标题 offset 构造失败时抛出。
    """

    tracking_error_line = "跟踪误差：2.10%" if include_tracking_error else "本节未披露跟踪误差。"
    custody_fee_lines = ("托管费率：0.20%",) if include_custody_fee else ()
    raw_text = "\n".join(
        (
            "§1 基金简介",
            "基金名称：易方达安心成长混合",
            "基金代码：110011",
            "基金类别：混合型",
            "基金规模：10.00亿元",
            "基金经理：张三",
            "§2 基金简介",
            "基金管理人：易方达基金管理有限公司",
            "基金托管人：工商银行",
            "基金合同生效日：2020-01-01",
            "投资目标：追求长期资本增值。",
            "投资范围：股票、债券及现金工具。",
            "投资策略：自下而上精选公司。",
            "风险收益特征：中高风险中高收益。",
            "业绩比较基准：沪深300指数收益率*80%+中债指数收益率*20%",
            "管理费率：1.20%",
            *custody_fee_lines,
            "§3 主要财务指标、基金净值表现及利润分配情况",
            "基金份额净值增长率：12.34%",
            "业绩比较基准收益率：10.01%",
            "投资者收益率：9.50%",
            tracking_error_line,
            "§4 管理人报告",
            "投资策略：坚持高质量成长股选择。",
            "后市展望：关注盈利质量和估值匹配。",
            "4.1.2 基金经理简介",
            "§8 投资组合报告",
            "报告期内股票换手率：238.45%",
            "换手率口径：买卖股票成交总额除以期初期末平均股票资产。",
            "§9 基金份额持有人信息",
            "基金经理持有本基金：12.34万份",
            "从业人员持有本基金：45.67万份",
            "机构投资者持有比例：23.45%",
            "个人投资者持有比例：76.55%",
            "§10 基金份额变动",
        )
    )
    tables = (
        ParsedTable(
            page_number=22,
            table_index=0,
            headers=("姓名", "职务", "任职日期", "离任日期"),
            rows=(("张三", "基金经理", "2021-01-01", ""),),
        ),
        ParsedTable(
            page_number=42,
            table_index=0,
            headers=("序号", "股票名称", "占基金资产净值比例", "前十大重仓"),
            rows=(("1", "贵州茅台", "8.00%", "前十大重仓"),),
        ),
        ParsedTable(
            page_number=43,
            table_index=1,
            headers=("行业", "占比"),
            rows=(("制造业", "55.00%"),),
        ),
        ParsedTable(
            page_number=58,
            table_index=0,
            headers=("项目", "份额"),
            rows=(
                ("期初基金份额总额", "1,000,000.00"),
                ("期末基金份额总额", "900,000.00"),
                ("本期申购赎回净额", "-100,000.00"),
            ),
        ),
    )
    return ParsedAnnualReport(
        key=DocumentKey(fund_code="110011", year=2024),
        raw_text=raw_text,
        sections=_section_offsets(
            raw_text,
            (
                ("§1", "§1 基金简介"),
                ("§2", "§2 基金简介"),
                ("§3", "§3 主要财务指标、基金净值表现及利润分配情况"),
                ("§4", "§4 管理人报告"),
                ("§8", "§8 投资组合报告"),
                ("§9", "§9 基金份额持有人信息"),
                ("§10", "§10 基金份额变动"),
            ),
        ),
        tables=tables,
        metadata=AnnualReportMetadata(source=_source_metadata()),
    )


def _report_without_custody_fee() -> ParsedAnnualReport:
    """构造仅缺少 fee_schedule.custody_fee child evidence 的 no-live 年报 fixture。

    Args:
        无。

    Returns:
        管理费率存在、托管费率显式缺失的年报 fixture。

    Raises:
        ValueError: 当章节标题 offset 构造失败时抛出。
    """

    return _happy_report(include_custody_fee=False)


def _report_without_core_risk_evidence() -> ParsedAnnualReport:
    """构造核心风险字段族完全缺失的 no-live 年报 fixture。

    Args:
        无。

    Returns:
        不含风险、持有人、换手率、持仓和跟踪误差证据的年报。

    Raises:
        ValueError: 当章节标题 offset 构造失败时抛出。
    """

    raw_text = "\n".join(
        (
            "§1 基金简介",
            "基金名称：易方达安心成长混合",
            "基金代码：110011",
            "基金类别：混合型",
            "基金规模：10.00亿元",
            "基金经理：张三",
            "§2 基金简介",
            "投资目标：追求长期资本增值。",
            "投资范围：股票、债券及现金工具。",
            "投资策略：自下而上精选公司。",
            "业绩比较基准：沪深300指数收益率*80%+中债指数收益率*20%",
            "管理费率：1.20%",
            "托管费率：0.20%",
            "§3 主要财务指标、基金净值表现及利润分配情况",
            "基金份额净值增长率：12.34%",
            "业绩比较基准收益率：10.01%",
            "投资者收益率：9.50%",
            "§4 管理人报告",
            "投资策略：坚持高质量成长股选择。",
            "后市展望：关注盈利质量和估值匹配。",
            "§8 投资组合报告",
            "§9 基金份额持有人信息",
            "§10 基金份额变动",
        )
    )
    return ParsedAnnualReport(
        key=DocumentKey(fund_code="110011", year=2024),
        raw_text=raw_text,
        sections=_section_offsets(
            raw_text,
            (
                ("§1", "§1 基金简介"),
                ("§2", "§2 基金简介"),
                ("§3", "§3 主要财务指标、基金净值表现及利润分配情况"),
                ("§4", "§4 管理人报告"),
                ("§8", "§8 投资组合报告"),
                ("§9", "§9 基金份额持有人信息"),
                ("§10", "§10 基金份额变动"),
            ),
        ),
        tables=(),
        metadata=AnnualReportMetadata(source=_source_metadata()),
    )


def _extract(report: ParsedAnnualReport) -> object:
    """运行 active annual processor。

    Args:
        report: 年报 fixture。

    Returns:
        Processor result。

    Raises:
        无显式抛出。
    """

    processor = ActiveFundAnnualProcessor()
    return processor.extract(FundProcessorInput(context=_dispatch_key(), intermediate=report))


def test_active_processor_outputs_six_non_missing_field_families() -> None:
    """验证 happy path 输出六个非缺失字段族。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当字段族数量、状态或 mapping 投影不符合预期时抛出。
    """

    result = _extract(_happy_report())

    field_family_ids = tuple(field_family.field_family_id for field_family in result.field_families)
    assert field_family_ids == (
        "product_essence.v1",
        "return_attribution.v1",
        "manager_profile.v1",
        "investor_experience.v1",
        "current_stage.v1",
        "core_risk.v1",
    )
    assert {field_family.status for field_family in result.field_families} == {"accepted"}
    assert result.contract_status == "satisfied"
    assert result.gaps == ()
    assert all(field_family.anchors for field_family in result.field_families)
    return_family = _family(result, "return_attribution.v1")
    assert return_family.value["nav_benchmark_performance"] == {
        "nav_growth_rate": "12.34%",
        "benchmark_return_rate": "10.01%",
    }
    assert return_family.value["fee_schedule"] == {
        "management_fee": "1.20%",
        "custody_fee": "0.20%",
    }
    manager_family = _family(result, "manager_profile.v1")
    assert manager_family.value["manager_strategy_text"] == {
        "strategy_summary": "坚持高质量成长股选择。",
        "market_outlook": "关注盈利质量和估值匹配。",
    }
    assert manager_family.value["manager_alignment"] == {
        "manager_holding": "12.34万份",
        "employee_holding": "45.67万份",
        "judgment": None,
    }
    assert "portfolio_managers" in manager_family.value
    assert "holdings_snapshot" in manager_family.value


def test_active_processor_emits_child_atomic_source_facts() -> None:
    """验证默认 parsed annual processor 从 S2A child outputs 发出 atomic facts。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 fact id、value 或 direct anchor source_field_path 不符合契约时抛出。
    """

    result = _extract(_happy_report())

    expected_fact_ids = {
        "fee_schedule.management_fee",
        "fee_schedule.custody_fee",
        "nav_benchmark_performance.nav_growth_rate",
        "nav_benchmark_performance.benchmark_return_rate",
        "manager_strategy_text.strategy_summary",
        "manager_strategy_text.market_outlook",
        "manager_alignment.manager_holding",
        "manager_alignment.employee_holding",
    }
    assert set(result.source_facts.facts) == expected_fact_ids
    for fact_id in expected_fact_ids:
        fact = result.source_facts.get_required(fact_id)
        assert fact.fact_id == fact.source_field_path == fact_id
        assert fact.status == "accepted"
        assert fact.value is not None
        assert fact.anchors
        assert all(
            anchor.row_locator is not None
            and f"source_field_path={fact_id};" in anchor.row_locator
            for anchor in fact.anchors
        )


def test_active_processor_emits_missing_child_fact_without_anchor() -> None:
    """验证显式 child gap 可成为 missing atomic fact，但不会伪造 anchor。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 missing fact 携带 anchor 或缺少 gap 时抛出。
    """

    result = _extract(_report_without_core_risk_evidence())

    missing_fact = result.source_facts.get_required("manager_alignment.manager_holding")
    assert missing_fact.status == "missing"
    assert missing_fact.value is None
    assert missing_fact.anchors == ()
    assert missing_fact.gaps
    assert "source_field_path=manager_alignment.manager_holding" in missing_fact.gaps[0]


def test_active_processor_preserves_partial_migrated_composite_child_gap() -> None:
    """验证迁移复合字段 sibling partial 不被兼容 dict 投影隐藏。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 missing child 未进入 value/gap/status 或 anchor 被伪造时抛出。
    """

    result = _extract(_report_without_custody_fee())

    management_fee = result.source_facts.get_required("fee_schedule.management_fee")
    custody_fee = result.source_facts.get_required("fee_schedule.custody_fee")
    assert management_fee.status == "accepted"
    assert management_fee.value == "1.20%"
    assert custody_fee.status == "missing"
    assert custody_fee.value is None
    assert custody_fee.anchors == ()

    return_family = _family(result, "return_attribution.v1")
    assert return_family.status == "partial"
    assert return_family.value["fee_schedule"] == {
        "management_fee": "1.20%",
        "custody_fee": None,
    }
    assert {
        gap.source_field_path
        for gap in return_family.gaps
        if gap.source_field_path == "fee_schedule.custody_fee"
    } == {"fee_schedule.custody_fee"}
    assert all(
        anchor.row_locator is not None
        and "source_field_path=fee_schedule.management_fee;" in anchor.row_locator
        for anchor in return_family.anchors
        if "source_field_path=fee_schedule." in (anchor.row_locator or "")
    )
    assert not any(
        anchor.row_locator is not None
        and "source_field_path=fee_schedule.custody_fee;" in anchor.row_locator
        for anchor in return_family.anchors
    )


def test_active_processor_does_not_infer_child_fact_from_composite_dict_shape() -> None:
    """验证缺少 S2A child evidence 时不从 legacy composite dict 反推 atomic fact。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当旧 dict shape 被错误用来创建 child fact 时抛出。
    """

    result = _extract(_report_without_core_risk_evidence())

    missing_fact = result.source_facts.get_required("manager_alignment.manager_holding")
    assert missing_fact.status == "missing"
    assert missing_fact.value is None
    assert missing_fact.anchors == ()
    assert missing_fact.gaps
    manager_family = _family(result, "manager_profile.v1")
    assert manager_family.value["manager_alignment"] is None


def test_active_processor_mapping_table_covers_emitted_value_fields() -> None:
    """验证字段族 value 只来自 documented mapping table。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当字段族输出绕过 mapping table 时抛出。
    """

    result = _extract(_happy_report())
    expected_fields_by_family = {
        mapping.field_family_id: {
            item.output_field_name
            for item in FIELD_FAMILY_MAPPINGS
            if item.field_family_id == mapping.field_family_id
        }
        for mapping in FIELD_FAMILY_MAPPINGS
    }

    for field_family in result.field_families:
        value_fields = set(field_family.value) - {"schema_version"}
        assert value_fields == expected_fields_by_family[field_family.field_family_id]


def test_active_processor_keeps_mapping_gaps_on_field_family_only() -> None:
    """验证字段族缺口留在本地而不进入 result-level gaps。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当本地 mapping gap 被提升到 result-level 时抛出。
    """

    result = _extract(_happy_report(include_tracking_error=False))

    return_family = _family(result, "return_attribution.v1")
    core_risk_family = _family(result, "core_risk.v1")
    assert return_family.status == "partial"
    assert core_risk_family.status == "partial"
    assert result.contract_status == "partial"
    assert result.gaps == ()
    assert {
        gap.source_field_path
        for gap in (*return_family.gaps, *core_risk_family.gaps)
    } == {"performance.tracking_error"}
    assert all(gap.field_family_id is not None for gap in return_family.gaps)
    assert all(gap.gap_code == "field_family_partial" for gap in return_family.gaps)


def test_active_processor_emits_field_family_missing_when_whole_family_missing() -> None:
    """验证字段族完全缺失时发出 field_family_missing gap。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当完全缺失字段族仍发出 partial gap 时抛出。
    """

    result = _extract(_report_without_core_risk_evidence())

    core_risk_family = _family(result, "core_risk.v1")
    assert core_risk_family.status == "missing"
    assert core_risk_family.anchors == ()
    assert core_risk_family.gaps
    assert {gap.gap_code for gap in core_risk_family.gaps} == {"field_family_missing"}
    assert {gap.field_family_id for gap in core_risk_family.gaps} == {"core_risk.v1"}
    assert result.gaps == ()


def test_active_processor_projects_public_provenance_and_public_anchors() -> None:
    """验证 provenance 来自 report metadata 且 anchor 不扩展 candidate source kind。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 provenance 或 anchor 来源越界时抛出。
    """

    result = _extract(_happy_report())

    assert result.source_provenance is not None
    assert result.source_provenance.selected_source == "eid"
    assert result.source_provenance.source_mode == "single_source_only"
    assert result.source_provenance.fallback_enabled is False
    assert {anchor.source_kind for anchor in result.anchors} <= {
        "annual_report",
        "external_api",
        "derived",
    }


def test_active_processor_makes_no_candidate_proof_or_readiness_claims() -> None:
    """验证 S1 不声明 candidate proof、parser replacement、readiness 或 release。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 result 出现 proof/readiness claim 时抛出。
    """

    result = _extract(_happy_report())
    payload_text = repr(result)

    assert result.candidate_boundary is None
    assert "candidate_only" not in payload_text
    assert "source_truth" not in payload_text
    assert "parser_replacement" not in payload_text
    assert "readiness" not in payload_text
    assert "release" not in payload_text


def test_active_processor_does_not_import_or_call_source_access_boundaries() -> None:
    """用 AST 守卫 processor 不触碰来源、PDF、Docling、provider 或 LLM 边界。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 processor 源码出现禁止边界引用时抛出。
    """

    module_path = (
        Path(__file__).resolve().parents[3]
        / "fund_agent"
        / "fund"
        / "processors"
        / "active_annual.py"
    )
    tree = ast.parse(module_path.read_text(encoding="utf-8"))
    forbidden_terms = (
        "FundDocumentRepository",
        "pdf",
        "cache",
        "sources",
        "source_helper",
        "docling",
        "candidate",
        "provider",
        "llm",
        "quality_gate",
    )
    imported_or_called_names = {
        node.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Name)
    }
    imported_modules = {
        node.module
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module is not None
    }

    combined = " ".join((*imported_or_called_names, *imported_modules)).lower()
    assert all(term.lower() not in combined for term in forbidden_terms)


def test_active_processor_fail_closed_on_wrong_intermediate_type() -> None:
    """验证错误中间态类型返回跨字段 fail-closed result。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当错误中间态被静默接受时抛出。
    """

    processor = ActiveFundAnnualProcessor()
    result = processor.extract(FundProcessorInput(context=_dispatch_key(), intermediate=object()))

    assert result.contract_status == "blocked"
    assert result.field_families == ()
    assert len(result.gaps) == 1
    assert result.gaps[0].gap_code == "input_type_mismatch"
    assert result.gaps[0].field_family_id is None
    assert result.gaps[0].source_boundary == "unsupported_intermediate"


def test_active_processor_unsupported_dispatch_gap_attribution() -> None:
    """验证 unsupported dispatch 按真实不匹配维度归因。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当所有 unsupported 场景都误归因为 intermediate 时抛出。
    """

    processor = ActiveFundAnnualProcessor()
    scenarios = (
        (
            _unchecked_dispatch_key(fund_type="index_fund"),
            "unsupported_fund_type",
            "unsupported_fund_type",
        ),
        (
            _unchecked_dispatch_key(report_type="semi_annual_report"),
            "unsupported_report_type",
            "unsupported_report_type",
        ),
        (
            _unchecked_dispatch_key(intermediate_kind="docling_pdf_candidate.v1"),
            "unsupported_intermediate_kind",
            "unsupported_intermediate",
        ),
        (
            _unchecked_dispatch_key(processor_goal="fixture_goal"),
            "unsupported_processor_goal",
            "unsupported_processor_goal",
        ),
    )

    for context, expected_gap_code, expected_boundary in scenarios:
        result = processor.extract(FundProcessorInput(context=context, intermediate=_happy_report()))

        assert result.contract_status == "unsupported"
        assert len(result.gaps) == 1
        assert result.gaps[0].field_family_id is None
        assert result.gaps[0].gap_code == expected_gap_code
        assert result.gaps[0].source_boundary == expected_boundary


def _family(result: object, field_family_id: str) -> object:
    """按 ID 读取字段族结果。

    Args:
        result: Processor result。
        field_family_id: 目标字段族 ID。

    Returns:
        命中的字段族结果。

    Raises:
        AssertionError: 当字段族不存在时抛出。
    """

    for field_family in result.field_families:
        if field_family.field_family_id == field_family_id:
            return field_family
    raise AssertionError(f"missing field family: {field_family_id}")
