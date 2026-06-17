"""测试 Docling candidate template field extractor。"""

from __future__ import annotations

import pytest

from fund_agent.fund.documents.candidates.representation_models import (
    CandidateRepresentationDocument,
    CandidateRepresentationIdentity,
    CandidateRepresentationSourceKind,
    CandidateRepresentationStatus,
    CandidateSectionNode,
    CandidateSourceLocator,
    CandidateTableBlock,
    CandidateTableCell,
    CandidateTextBlock,
)
from fund_agent.fund.documents.candidates.template_field_extraction import (
    CandidateTemplateFieldAnchor,
    DEFAULT_DOCLING_TEMPLATE_FIELD_PATHS,
    extract_docling_template_fields,
)


def _identity(
    source_kind: CandidateRepresentationSourceKind = CandidateRepresentationSourceKind.DOCLING_PDF,
) -> CandidateRepresentationIdentity:
    """构造候选表示 identity。

    Args:
        source_kind: 候选来源类型。

    Returns:
        候选表示 identity。

    Raises:
        无显式抛出。
    """

    return CandidateRepresentationIdentity(
        source_kind=source_kind,
        sample_id="SYN",
        fund_code="004393",
        document_year=2025,
        report_type="annual_report",
        input_artifact_path="reports/synthetic-docling.json",
        accepted_input_sha256="abc123",
        provenance_judgment_path="docs/reviews/synthetic.md",
    )


def _locator(
    source_ref: str,
    *,
    page_number: int | None = 1,
    row_index: int | None = None,
    column_index: int | None = None,
) -> CandidateSourceLocator:
    """构造候选 locator。

    Args:
        source_ref: 来源引用。
        page_number: 页码。
        row_index: 行号。
        column_index: 列号。

    Returns:
        候选 locator。

    Raises:
        无显式抛出。
    """

    return CandidateSourceLocator(
        source_kind=CandidateRepresentationSourceKind.DOCLING_PDF,
        source_ref=source_ref,
        page_number=page_number,
        bbox=None,
        row_index=row_index,
        column_index=column_index,
    )


def _cell(
    index: int,
    row: int,
    column: int,
    text: str,
    *,
    row_label_path: tuple[str, ...] = (),
    column_header_path: tuple[str, ...] = (),
) -> CandidateTableCell:
    """构造候选表格单元格。

    Args:
        index: 单元格序号。
        row: 行号。
        column: 列号。
        text: 单元格文本。
        row_label_path: 行标签路径。
        column_header_path: 列头路径。

    Returns:
        候选单元格。

    Raises:
        无显式抛出。
    """

    return CandidateTableCell(
        cell_index=index,
        row_start=row,
        row_end=row,
        column_start=column,
        column_end=column,
        row_span=1,
        column_span=1,
        row_header=column == 0,
        column_header=row == 0,
        row_label_path=row_label_path,
        column_header_path=column_header_path,
        text=text,
        normalized_text=text,
        source_locator=_locator(f"cell-{index}", page_number=2 + row, row_index=row, column_index=column),
        cell_hash=f"cell-hash-{index}",
        locator_hash=f"locator-hash-{index}",
        stability="strong",
    )


def _table(
    table_id: str,
    section_id: str | None,
    cells: tuple[CandidateTableCell, ...],
    *,
    page_number: int = 2,
) -> CandidateTableBlock:
    """构造候选表格。

    Args:
        table_id: 表格 ID。
        section_id: 章节 ID。
        cells: 单元格。
        page_number: 表格页码。

    Returns:
        候选表格。

    Raises:
        无显式抛出。
    """

    return CandidateTableBlock(
        table_id=table_id,
        source_ref=table_id,
        route_table_index=1,
        section_id=section_id,
        heading_path=(section_id,) if section_id else (),
        page_numbers=(page_number,),
        source_locator=_locator(table_id, page_number=page_number),
        bbox_by_page=(),
        caption=None,
        label=None,
        row_count=max((cell.row_start or 0 for cell in cells), default=0) + 1,
        column_count=max((cell.column_start or 0 for cell in cells), default=0) + 1,
        cell_count=len(cells),
        table_family="synthetic",
        locator_stability="strong",
        excluded_reason=None,
        failure_code=None,
        cells=cells,
    )


def _text_block(
    block_id: str,
    section_id: str | None,
    text: str,
    *,
    page_number: int = 3,
) -> CandidateTextBlock:
    """构造候选文本块。

    Args:
        block_id: 文本块 ID。
        section_id: 章节 ID。
        text: 文本内容。
        page_number: 文本块页码。

    Returns:
        候选文本块。

    Raises:
        无显式抛出。
    """

    return CandidateTextBlock(
        block_id=block_id,
        block_type="paragraph",
        section_id=section_id,
        heading_path=(section_id,) if section_id else (),
        text=text,
        normalized_text=text,
        source_locator=_locator(block_id, page_number=page_number),
        content_hash=f"hash-{block_id}",
        excluded_reason=None,
    )


def _section_node(section_id: str, heading_text: str, page_number: int) -> CandidateSectionNode:
    """构造候选章节节点。

    Args:
        section_id: 候选章节节点 ID。
        heading_text: 标题文本。
        page_number: 页码。

    Returns:
        候选章节节点。

    Raises:
        无显式抛出。
    """

    return CandidateSectionNode(
        section_id=section_id,
        source_ref=section_id,
        heading_text=heading_text,
        heading_path=(heading_text,),
        heading_level=1,
        page_start=page_number,
        page_end=page_number,
        source_locator=_locator(section_id, page_number=page_number),
        content_hash=f"hash-{section_id}",
        confidence="usable",
        excluded_reason=None,
    )


def _document(
    *,
    status: CandidateRepresentationStatus | None = None,
    source_kind: CandidateRepresentationSourceKind = CandidateRepresentationSourceKind.DOCLING_PDF,
) -> CandidateRepresentationDocument:
    """构造覆盖初始目标字段的候选文档。

    Args:
        status: candidate non-proof 状态。
        source_kind: 候选来源类型。

    Returns:
        候选文档。

    Raises:
        无显式抛出。
    """

    profile_cells = (
        _cell(1, 1, 0, "基金名称"),
        _cell(2, 1, 1, "安信企业价值优选混合型证券投资基金"),
        _cell(3, 2, 0, "基金主代码"),
        _cell(4, 2, 1, "004393"),
        _cell(5, 3, 0, "基金管理人"),
        _cell(6, 3, 1, "安信基金管理有限责任公司"),
        _cell(7, 4, 0, "基金托管人"),
        _cell(8, 4, 1, "招商银行股份有限公司"),
        _cell(9, 5, 0, "投资目标"),
        _cell(10, 5, 1, "追求长期稳健增值"),
        _cell(11, 6, 0, "投资范围"),
        _cell(12, 6, 1, "投资于股票、债券和货币市场工具"),
        _cell(13, 7, 0, "业绩比较基准"),
        _cell(14, 7, 1, "沪深300指数收益率*60%+中债指数收益率*40%"),
        _cell(15, 8, 0, "风险收益特征"),
        _cell(16, 8, 1, "本基金为混合型基金，风险收益高于债券基金"),
    )
    fee_cells = (
        _cell(17, 1, 0, "基金管理费"),
        _cell(18, 1, 1, "1.20%"),
        _cell(19, 2, 0, "基金托管费"),
        _cell(20, 2, 1, "0.20%"),
    )
    performance_cells = (
        _cell(21, 1, 0, "过去一年", row_label_path=("过去一年",)),
        _cell(
            22,
            1,
            1,
            "12.34%",
            row_label_path=("过去一年",),
            column_header_path=("净值增长率",),
        ),
        _cell(
            23,
            1,
            2,
            "10.00%",
            row_label_path=("过去一年",),
            column_header_path=("业绩比较基准收益率",),
        ),
    )
    manager_cells = (
        _cell(24, 0, 0, "姓名", column_header_path=("姓名",)),
        _cell(25, 0, 1, "任职日期", column_header_path=("任职日期",)),
        _cell(26, 1, 0, "张三", column_header_path=("姓名",)),
        _cell(27, 1, 1, "2020-01-01", column_header_path=("任职日期",)),
    )
    manager_alignment_cells = (
        _cell(28, 1, 0, "本基金基金经理持有本开放式基金"),
        _cell(29, 1, 1, "10~50万份"),
    )
    holdings_cells = (
        _cell(30, 1, 0, "股票", row_label_path=("股票",)),
        _cell(31, 1, 1, "贵州茅台", column_header_path=("股票名称",), row_label_path=("股票",)),
        _cell(32, 1, 2, "100000.00", column_header_path=("公允价值",), row_label_path=("股票",)),
        _cell(
            33,
            1,
            3,
            "5.00%",
            column_header_path=("占基金资产净值比例",),
            row_label_path=("股票",),
        ),
        _cell(34, 2, 0, "债券", row_label_path=("债券",)),
        _cell(35, 2, 1, "国债2401", column_header_path=("债券名称",), row_label_path=("债券",)),
        _cell(36, 2, 2, "200000.00", column_header_path=("公允价值",), row_label_path=("债券",)),
        _cell(
            37,
            2,
            3,
            "4.00%",
            column_header_path=("占基金资产净值比例",),
            row_label_path=("债券",),
        ),
        _cell(38, 3, 0, "目标基金", row_label_path=("目标基金",)),
        _cell(39, 3, 1, "沪深300ETF", column_header_path=("基金名称",), row_label_path=("目标基金",)),
        _cell(40, 3, 2, "300000.00", column_header_path=("公允价值",), row_label_path=("目标基金",)),
        _cell(
            41,
            3,
            3,
            "3.00%",
            column_header_path=("占基金资产净值比例",),
            row_label_path=("目标基金",),
        ),
    )
    return CandidateRepresentationDocument(
        schema_version="candidate_annual_report_representation.v1",
        identity=_identity(source_kind),
        status=status or CandidateRepresentationStatus(),
        summary_metrics={},
        sections=(),
        text_blocks=(
            _text_block("tracking-actual", "§3", "本报告期实际跟踪误差为 1.23%"),
            _text_block("tracking-target", "§3", "力争将跟踪误差控制在 4.00%以内"),
        ),
        tables=(
            _table("profile", "§2", profile_cells),
            _table("fee", "§7", fee_cells),
            _table("performance", "§3", performance_cells),
            _table("manager", "§4", manager_cells),
            _table("manager_alignment", "§10", manager_alignment_cells),
            _table("holdings", "§8", holdings_cells),
        ),
        route_failures=(),
        projection_issues=(),
        blocked_claims=(),
    )


def _field(result_field_map: dict[str, object], field_path: str):
    """按字段路径读取结果字段。

    Args:
        result_field_map: 字段路径到字段对象的映射。
        field_path: 字段路径。

    Returns:
        字段对象。

    Raises:
        KeyError: 字段不存在时抛出。
    """

    return result_field_map[field_path]


def test_docling_template_field_extractor_emits_one_candidate_field_per_default_path() -> None:
    """验证默认目标字段全部有且仅有一个 candidate-only 输出。"""

    result = extract_docling_template_fields(_document())

    assert result.schema_version == "docling_template_field_candidates.v1"
    assert result.candidate_only is True
    assert result.source_truth_status == "not_proven"
    assert len(result.fields) == len(DEFAULT_DOCLING_TEMPLATE_FIELD_PATHS)
    assert {field.field_path for field in result.fields} == set(DEFAULT_DOCLING_TEMPLATE_FIELD_PATHS)
    assert all(field.candidate_only is True for field in result.fields)
    assert all(field.source_truth_status == "not_proven" for field in result.fields)


def test_docling_template_field_extractor_maps_profile_fee_and_performance_fields() -> None:
    """验证 profile、fee 与 performance 字段按候选表格映射。"""

    result = extract_docling_template_fields(_document())
    fields = {field.field_path: field for field in result.fields}

    assert _field(fields, "basic_identity.fund_name").value == "安信企业价值优选混合型证券投资基金"
    assert _field(fields, "basic_identity.fund_code").value == "004393"
    assert _field(fields, "basic_identity.management_company").value == "安信基金管理有限责任公司"
    assert _field(fields, "basic_identity.custodian").value == "招商银行股份有限公司"
    assert _field(fields, "product_profile.investment_objective").value == "追求长期稳健增值"
    assert _field(fields, "product_profile.investment_scope").value == "投资于股票、债券和货币市场工具"
    assert _field(fields, "benchmark.benchmark_text").value == "沪深300指数收益率*60%+中债指数收益率*40%"
    assert _field(fields, "risk_characteristic_text.risk_characteristic_text").value.startswith("本基金为混合型基金")
    assert _field(fields, "fee_schedule.management_fee").value == "1.20%"
    assert _field(fields, "fee_schedule.custody_fee").value == "0.20%"
    assert _field(fields, "nav_benchmark_performance.nav_growth_rate").value == "12.34%"
    assert _field(fields, "nav_benchmark_performance.benchmark_return_rate").value == "10.00%"


def test_docling_template_field_extractor_maps_tracking_manager_and_holding_fields() -> None:
    """验证 tracking error、manager 与 holdings 候选字段。"""

    result = extract_docling_template_fields(_document())
    fields = {field.field_path: field for field in result.fields}

    assert _field(fields, "tracking_error.value_text").value == "1.23%"
    portfolio_managers = _field(fields, "portfolio_managers").value
    assert portfolio_managers == {
        "schema_version": "portfolio_manager_tenure_list.v1",
        "managers": [{"name": "张三", "start_date": "2020-01-01"}],
    }
    assert _field(fields, "manager_alignment.manager_holding_range").value == "10~50万份"
    assert _field(fields, "holdings_snapshot.top_holdings").value == {
        "rows": ({"name": "贵州茅台", "fair_value_cny": "100000.00", "net_asset_ratio": "5.00%"},)
    }
    assert _field(fields, "holdings_snapshot.bond_top_holdings").value == {
        "rows": ({"name": "国债2401", "fair_value_cny": "200000.00", "net_asset_ratio": "4.00%"},)
    }
    assert _field(fields, "holdings_snapshot.target_fund_holdings").value == {
        "rows": ({"name": "沪深300ETF", "fair_value_cny": "300000.00", "net_asset_ratio": "3.00%"},)
    }


def test_docling_template_field_extractor_emits_explicit_missing_for_deferred_paths() -> None:
    """验证未实现路径显式 missing，不静默遗漏。"""

    result = extract_docling_template_fields(_document())
    fields = {field.field_path: field for field in result.fields}

    for field_path in ("manager_strategy_text", "holder_structure", "share_change", "bond_risk_evidence"):
        field = _field(fields, field_path)
        assert field.extraction_mode == "missing"
        assert field.value is None
        assert field.anchors == ()
        assert field.note
        assert field_path in result.missing_field_paths


def test_docling_template_field_extractor_rejects_non_docling_source() -> None:
    """验证非 Docling candidate source 不能进入本 extractor。"""

    with pytest.raises(ValueError, match="docling_pdf_candidate"):
        extract_docling_template_fields(
            _document(source_kind=CandidateRepresentationSourceKind.PDFPLUMBER_PDF)
        )


def test_docling_template_field_extractor_rejects_status_claims() -> None:
    """验证输入状态不能越过 candidate-only proof 边界。"""

    with pytest.raises(ValueError, match="source_truth_status"):
        extract_docling_template_fields(
            _document(
                status=CandidateRepresentationStatus(
                    candidate_status="not_proven",
                    field_correctness_status="not_proven",
                    source_truth_status="accepted",  # type: ignore[arg-type]
                    taxonomy_compatibility_status="not_proven",
                    production_parser_replacement_status="not_authorized",
                )
            )
        )


def test_docling_template_field_extractor_rejects_tracking_error_target_text() -> None:
    """验证跟踪误差目标/限制文本不会被误采信。"""

    document = CandidateRepresentationDocument(
        schema_version="candidate_annual_report_representation.v1",
        identity=_identity(),
        status=CandidateRepresentationStatus(),
        summary_metrics={},
        sections=(),
        text_blocks=(_text_block("tracking-target", "§3", "力争将跟踪误差控制在 4.00%以内"),),
        tables=(),
        route_failures=(),
        projection_issues=(),
        blocked_claims=(),
    )

    result = extract_docling_template_fields(document, target_field_paths=("tracking_error.value_text",))
    field = result.fields[0]
    assert field.extraction_mode == "missing"
    assert field.value is None
    assert field.anchors == ()


def test_docling_template_field_extractor_rejects_invalid_target_field_paths() -> None:
    """验证目标字段路径集合 fail-closed。"""

    document = _document()

    with pytest.raises(ValueError, match="cannot be empty"):
        extract_docling_template_fields(document, target_field_paths=())
    with pytest.raises(ValueError, match="duplicates"):
        extract_docling_template_fields(
            document,
            target_field_paths=("basic_identity.fund_name", "basic_identity.fund_name"),
        )
    with pytest.raises(ValueError, match="unsupported"):
        extract_docling_template_fields(document, target_field_paths=("unknown.field",))


def test_docling_template_field_extractor_uses_text_label_fallback() -> None:
    """验证无表格时可通过同章节文本标签抽取字段。"""

    document = CandidateRepresentationDocument(
        schema_version="candidate_annual_report_representation.v1",
        identity=_identity(),
        status=CandidateRepresentationStatus(),
        summary_metrics={},
        sections=(),
        text_blocks=(_text_block("fund-code-text", "§2", "基金代码：004393"),),
        tables=(),
        route_failures=(),
        projection_issues=(),
        blocked_claims=(),
    )

    result = extract_docling_template_fields(document, target_field_paths=("basic_identity.fund_code",))
    field = result.fields[0]
    assert field.extraction_mode == "direct"
    assert field.value == "004393"
    assert field.anchors[0].note.startswith("candidate_only:")


def test_docling_template_field_extractor_uses_page_section_context_for_unlinked_table() -> None:
    """验证无显式 section_id 的表格可按稳定章节页码 span 抽取。"""

    cells = (
        _cell(100, 1, 0, "基金名称"),
        _cell(101, 1, 1, "安信企业价值优选混合型证券投资基金"),
    )
    document = CandidateRepresentationDocument(
        schema_version="candidate_annual_report_representation.v1",
        identity=_identity(),
        status=CandidateRepresentationStatus(),
        summary_metrics={},
        sections=(
            _section_node("sec_2", "§2 基金简介", 2),
            _section_node("sec_3", "§3 主要财务指标、基金净值表现及利润分配情况", 10),
        ),
        text_blocks=(),
        tables=(_table("unlinked-profile", None, cells, page_number=3),),
        route_failures=(),
        projection_issues=(),
        blocked_claims=(),
    )

    result = extract_docling_template_fields(document, target_field_paths=("basic_identity.fund_name",))
    field = result.fields[0]

    assert field.extraction_mode == "direct"
    assert field.value == "安信企业价值优选混合型证券投资基金"
    assert field.anchors[0].section_id == "§2"


def test_docling_template_field_extractor_uses_page_section_context_for_unlinked_text() -> None:
    """验证无显式 section_id 的文本块可按稳定章节页码 span 抽取。"""

    document = CandidateRepresentationDocument(
        schema_version="candidate_annual_report_representation.v1",
        identity=_identity(),
        status=CandidateRepresentationStatus(),
        summary_metrics={},
        sections=(
            _section_node("sec_2", "§2 基金简介", 2),
            _section_node("sec_3", "§3 主要财务指标、基金净值表现及利润分配情况", 10),
        ),
        text_blocks=(_text_block("fund-code-text", None, "基金代码：004393", page_number=3),),
        tables=(),
        route_failures=(),
        projection_issues=(),
        blocked_claims=(),
    )

    result = extract_docling_template_fields(document, target_field_paths=("basic_identity.fund_code",))
    field = result.fields[0]

    assert field.extraction_mode == "direct"
    assert field.value == "004393"
    assert field.anchors[0].section_id == "§2"


def test_docling_template_field_extractor_keeps_duplicate_section_context_missing() -> None:
    """验证同页重复顶层章节时 fail-closed，不因标签存在而抽取。"""

    cells = (
        _cell(110, 1, 0, "基金名称"),
        _cell(111, 1, 1, "安信企业价值优选混合型证券投资基金"),
    )
    document = CandidateRepresentationDocument(
        schema_version="candidate_annual_report_representation.v1",
        identity=_identity(),
        status=CandidateRepresentationStatus(),
        summary_metrics={},
        sections=(
            _section_node("sec_2_a", "§2 基金简介", 2),
            _section_node("sec_2_b", "§2 基金简介", 2),
        ),
        text_blocks=(),
        tables=(_table("ambiguous-profile", None, cells, page_number=2),),
        route_failures=(),
        projection_issues=(),
        blocked_claims=(),
    )

    result = extract_docling_template_fields(document, target_field_paths=("basic_identity.fund_name",))
    field = result.fields[0]

    assert field.extraction_mode == "missing"
    assert field.value is None
    assert field.anchors == ()


def test_docling_template_field_extractor_derives_performance_labels_from_header_row() -> None:
    """验证空 label path 的业绩表可从确定性表头与行首标签派生字段。"""

    cells = (
        _cell(120, 0, 0, "阶段"),
        _cell(121, 0, 1, "净值增长率"),
        _cell(122, 0, 2, "业绩比较基准收益率"),
        _cell(123, 1, 0, "过去一年"),
        _cell(124, 1, 1, "12.34%"),
        _cell(125, 1, 2, "10.00%"),
    )
    document = CandidateRepresentationDocument(
        schema_version="candidate_annual_report_representation.v1",
        identity=_identity(),
        status=CandidateRepresentationStatus(),
        summary_metrics={},
        sections=(),
        text_blocks=(),
        tables=(_table("derived-performance", "§3", cells),),
        route_failures=(),
        projection_issues=(),
        blocked_claims=(),
    )

    result = extract_docling_template_fields(
        document,
        target_field_paths=(
            "nav_benchmark_performance.nav_growth_rate",
            "nav_benchmark_performance.benchmark_return_rate",
        ),
    )
    fields = {field.field_path: field for field in result.fields}

    assert _field(fields, "nav_benchmark_performance.nav_growth_rate").value == "12.34%"
    assert _field(fields, "nav_benchmark_performance.benchmark_return_rate").value == "10.00%"
    assert all(field.extraction_mode == "direct" for field in result.fields)


def test_docling_template_field_extractor_derives_manager_labels_from_header_row() -> None:
    """验证空 label path 的基金经理表可从确定性表头派生姓名和任职日期。"""

    cells = (
        _cell(130, 0, 0, "姓名"),
        _cell(131, 0, 1, "任职日期"),
        _cell(132, 1, 0, "李四"),
        _cell(133, 1, 1, "2021-05-01"),
    )
    document = CandidateRepresentationDocument(
        schema_version="candidate_annual_report_representation.v1",
        identity=_identity(),
        status=CandidateRepresentationStatus(),
        summary_metrics={},
        sections=(),
        text_blocks=(),
        tables=(_table("derived-manager", "§4", cells),),
        route_failures=(),
        projection_issues=(),
        blocked_claims=(),
    )

    result = extract_docling_template_fields(document, target_field_paths=("portfolio_managers",))
    field = result.fields[0]

    assert field.extraction_mode == "direct"
    assert field.value == {
        "schema_version": "portfolio_manager_tenure_list.v1",
        "managers": [{"name": "李四", "start_date": "2021-05-01"}],
    }


def test_docling_template_field_extractor_derives_holding_labels_from_header_row() -> None:
    """验证空 label path 的持仓表可从确定性表头和行首资产类型派生字段。"""

    cells = (
        _cell(140, 0, 0, "资产类型"),
        _cell(141, 0, 1, "股票名称"),
        _cell(142, 0, 2, "公允价值"),
        _cell(143, 0, 3, "占基金资产净值比例"),
        _cell(144, 1, 0, "股票"),
        _cell(145, 1, 1, "宁德时代"),
        _cell(146, 1, 2, "123456.00"),
        _cell(147, 1, 3, "6.66%"),
    )
    document = CandidateRepresentationDocument(
        schema_version="candidate_annual_report_representation.v1",
        identity=_identity(),
        status=CandidateRepresentationStatus(),
        summary_metrics={},
        sections=(),
        text_blocks=(),
        tables=(_table("derived-holding", "§8", cells),),
        route_failures=(),
        projection_issues=(),
        blocked_claims=(),
    )

    result = extract_docling_template_fields(document, target_field_paths=("holdings_snapshot.top_holdings",))
    field = result.fields[0]

    assert field.extraction_mode == "direct"
    assert field.value == {
        "rows": ({"name": "宁德时代", "fair_value_cny": "123456.00", "net_asset_ratio": "6.66%"},)
    }
    assert field.anchors[0].note.startswith("candidate_only:")


def test_docling_template_field_extractor_keeps_missing_without_deterministic_header() -> None:
    """验证无确定性表头时不按位置猜测业绩字段。"""

    cells = (
        _cell(150, 1, 0, "过去一年"),
        _cell(151, 1, 1, "12.34%"),
    )
    document = CandidateRepresentationDocument(
        schema_version="candidate_annual_report_representation.v1",
        identity=_identity(),
        status=CandidateRepresentationStatus(),
        summary_metrics={},
        sections=(),
        text_blocks=(),
        tables=(_table("no-header-performance", "§3", cells),),
        route_failures=(),
        projection_issues=(),
        blocked_claims=(),
    )

    result = extract_docling_template_fields(
        document,
        target_field_paths=("nav_benchmark_performance.nav_growth_rate",),
    )
    field = result.fields[0]

    assert field.extraction_mode == "missing"
    assert field.value is None
    assert field.anchors == ()


def test_docling_template_field_extractor_ignores_structural_column_header_without_labels() -> None:
    """验证结构性 column_header 标记不能单独触发表头派生。"""

    cells = (
        _cell(152, 0, 0, "过去一年"),
        _cell(153, 0, 1, "12.34%"),
    )
    document = CandidateRepresentationDocument(
        schema_version="candidate_annual_report_representation.v1",
        identity=_identity(),
        status=CandidateRepresentationStatus(),
        summary_metrics={},
        sections=(),
        text_blocks=(),
        tables=(_table("structural-header-only-performance", "§3", cells),),
        route_failures=(),
        projection_issues=(),
        blocked_claims=(),
    )

    result = extract_docling_template_fields(
        document,
        target_field_paths=("nav_benchmark_performance.nav_growth_rate",),
    )
    field = result.fields[0]

    assert field.extraction_mode == "missing"
    assert field.value is None
    assert field.anchors == ()


def test_docling_template_field_extractor_keeps_missing_for_ambiguous_performance_header() -> None:
    """验证重复目标表头时不取第一个匹配列。"""

    cells = (
        _cell(160, 0, 0, "阶段"),
        _cell(161, 0, 1, "净值增长率"),
        _cell(162, 0, 2, "净值增长率"),
        _cell(163, 1, 0, "过去一年"),
        _cell(164, 1, 1, "12.34%"),
        _cell(165, 1, 2, "13.57%"),
    )
    document = CandidateRepresentationDocument(
        schema_version="candidate_annual_report_representation.v1",
        identity=_identity(),
        status=CandidateRepresentationStatus(),
        summary_metrics={},
        sections=(),
        text_blocks=(),
        tables=(_table("ambiguous-performance", "§3", cells),),
        route_failures=(),
        projection_issues=(),
        blocked_claims=(),
    )

    result = extract_docling_template_fields(
        document,
        target_field_paths=("nav_benchmark_performance.nav_growth_rate",),
    )
    field = result.fields[0]

    assert field.extraction_mode == "missing"
    assert field.value is None
    assert field.anchors == ()


def test_candidate_template_field_anchor_rejects_non_candidate_note() -> None:
    """验证候选锚点 note 必须显式标记 candidate-only。"""

    with pytest.raises(ValueError, match="candidate_only"):
        CandidateTemplateFieldAnchor(
            source_kind="annual_report",
            document_year=2025,
            section_id="§2",
            page_number=1,
            table_id=None,
            row_locator="row",
            note="production-looking-note",
        )
