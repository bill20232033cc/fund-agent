"""Docling 候选表示到分析模板字段的候选抽取。

本模块只消费已经投影完成的 ``CandidateRepresentationDocument``，不调用
Docling、不读取 PDF、不访问 ``FundDocumentRepository``，也不返回生产
``EvidenceAnchor``。输出保持 candidate-only，用于后续证据和集成 gate。
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Final, Literal

from fund_agent.fund.documents.candidates.evidence_anchor_mapping import (
    CandidateAnchorSchemaFamily,
    map_candidate_locator_to_anchor_candidate,
)
from fund_agent.fund.documents.candidates.representation_models import (
    CandidateRepresentationDocument,
    CandidateRepresentationSourceKind,
    CandidateTableBlock,
    CandidateTableCell,
    CandidateTextBlock,
)

DOCLING_TEMPLATE_FIELD_SCHEMA_VERSION: Final[str] = "docling_template_field_candidates.v1"
CandidateTemplateExtractionMode = Literal["direct", "missing"]
CandidateTemplateSourceTruthStatus = Literal["not_proven"]
CandidateTemplateSourceKind = Literal["annual_report"]
_SectionContextCache = dict[int, str | None]

DEFAULT_DOCLING_TEMPLATE_FIELD_PATHS: Final[tuple[str, ...]] = (
    "basic_identity.fund_name",
    "basic_identity.fund_code",
    "basic_identity.management_company",
    "basic_identity.custodian",
    "product_profile.investment_objective",
    "product_profile.investment_scope",
    "benchmark.benchmark_text",
    "risk_characteristic_text.risk_characteristic_text",
    "fee_schedule.management_fee",
    "fee_schedule.custody_fee",
    "nav_benchmark_performance.nav_growth_rate",
    "nav_benchmark_performance.benchmark_return_rate",
    "tracking_error.value_text",
    "portfolio_managers",
    "turnover_rate",
    "manager_alignment.manager_holding_range",
    "holdings_snapshot.top_holdings",
    "holdings_snapshot.bond_top_holdings",
    "holdings_snapshot.target_fund_holdings",
    "manager_strategy_text",
    "holder_structure",
    "share_change",
    "bond_risk_evidence",
)

_PROFILE_LABELS: Final[dict[str, tuple[str, ...]]] = {
    "basic_identity.fund_name": ("基金名称", "基金简称"),
    "basic_identity.fund_code": ("基金主代码", "基金代码"),
    "basic_identity.management_company": ("基金管理人",),
    "basic_identity.custodian": ("基金托管人",),
    "product_profile.investment_objective": ("投资目标",),
    "product_profile.investment_scope": ("投资范围",),
    "benchmark.benchmark_text": ("业绩比较基准",),
    "risk_characteristic_text.risk_characteristic_text": ("风险收益特征", "基金风险收益特征"),
}
_FEE_LABELS: Final[dict[str, tuple[str, ...]]] = {
    "fee_schedule.management_fee": ("管理费", "基金管理费", "管理费率"),
    "fee_schedule.custody_fee": ("托管费", "基金托管费", "托管费率"),
}
_PERFORMANCE_LABELS: Final[dict[str, tuple[str, ...]]] = {
    "nav_benchmark_performance.nav_growth_rate": ("净值增长率", "基金份额净值增长率"),
    "nav_benchmark_performance.benchmark_return_rate": ("业绩比较基准收益率", "基准收益率"),
}
_DEFERRED_FIELD_NOTES: Final[dict[str, str]] = {
    "manager_strategy_text": "docling_template_field_deferred_manager_strategy_text",
    "holder_structure": "docling_template_field_deferred_holder_structure",
    "share_change": "docling_template_field_deferred_share_change",
    "bond_risk_evidence": "docling_template_field_deferred_bond_risk_evidence",
}
_TRACKING_ERROR_REJECT_KEYWORDS: Final[tuple[str, ...]] = (
    "控制在",
    "不超过",
    "力争",
    "争取",
    "目标",
    "限制",
    "最小化",
)
_TRACKING_ERROR_ACCEPT_KEYWORDS: Final[tuple[str, ...]] = ("实际", "报告期", "本报告期", "过去一年")
_PERCENT_PATTERN: Final[re.Pattern[str]] = re.compile(r"[-+]?\d+(?:,\d{3})*(?:\.\d+)?\s*%")


@dataclass(frozen=True, slots=True)
class CandidateTemplateFieldAnchor:
    """模板字段候选锚点。

    该结构只镜像年报语义定位，不是生产 ``EvidenceAnchor``。

    Attributes:
        source_kind: 语义来源类型，当前只允许年报。
        document_year: 年报年份。
        section_id: 年报章节。
        page_number: 页码；缺失时为 ``None``。
        table_id: 表格 ID；非表格命中为 ``None``。
        row_locator: 行或单元格定位；文本命中可为 block ID。
        note: candidate-only 说明。
    """

    source_kind: CandidateTemplateSourceKind
    document_year: int
    section_id: str | None
    page_number: int | None
    table_id: str | None
    row_locator: str | None
    note: str

    def __post_init__(self) -> None:
        """校验候选锚点不能伪装为生产锚点。

        Args:
            无。

        Returns:
            无返回值。

        Raises:
            ValueError: note 未显式标记 candidate-only 时抛出。
        """

        if not self.note.startswith("candidate_only:"):
            raise ValueError("CandidateTemplateFieldAnchor note must start with candidate_only:")


@dataclass(frozen=True, slots=True)
class CandidateTemplateField:
    """单个模板目标字段的候选抽取结果。

    Attributes:
        field_group: 字段组。
        field_path: dot-notation 字段路径。
        value: 候选值；缺失时为 ``None``。
        extraction_mode: ``direct`` 或 ``missing``。
        anchors: 候选锚点。
        note: 缺失、阻断或命中说明。
        candidate_only: 必须保持 ``True``。
        source_truth_status: 必须保持 ``not_proven``。
    """

    field_group: str
    field_path: str
    value: object | None
    extraction_mode: CandidateTemplateExtractionMode
    anchors: tuple[CandidateTemplateFieldAnchor, ...]
    note: str | None
    candidate_only: bool
    source_truth_status: CandidateTemplateSourceTruthStatus

    def __post_init__(self) -> None:
        """校验候选字段不越过 proof 边界。

        Args:
            无。

        Returns:
            无返回值。

        Raises:
            ValueError: candidate-only、不证明 source truth 或锚点约束被破坏时抛出。
        """

        if self.candidate_only is not True:
            raise ValueError("CandidateTemplateField must remain candidate_only")
        if self.source_truth_status != "not_proven":
            raise ValueError("CandidateTemplateField must keep source_truth_status=not_proven")
        if self.extraction_mode == "direct" and not self.anchors:
            raise ValueError("direct CandidateTemplateField requires at least one anchor")
        if self.extraction_mode == "missing" and self.value is not None:
            raise ValueError("missing CandidateTemplateField value must be None")


@dataclass(frozen=True, slots=True)
class DoclingTemplateFieldExtractionResult:
    """Docling 模板字段候选抽取结果。

    Attributes:
        schema_version: 当前固定为 ``docling_template_field_candidates.v1``。
        fund_code: 基金代码。
        document_year: 年报年份。
        candidate_only: 必须保持 ``True``。
        source_truth_status: 必须保持 ``not_proven``。
        fields: 目标字段候选结果。
        missing_field_paths: 缺失字段路径。
        blocked_field_paths: 因边界或歧义被阻断的字段路径。
        diagnostics: 诊断信息；不能替代证据。
    """

    schema_version: str
    fund_code: str
    document_year: int
    candidate_only: bool
    source_truth_status: CandidateTemplateSourceTruthStatus
    fields: tuple[CandidateTemplateField, ...]
    missing_field_paths: tuple[str, ...]
    blocked_field_paths: tuple[str, ...]
    diagnostics: dict[str, object]

    def __post_init__(self) -> None:
        """校验整体结果保持 candidate-only。

        Args:
            无。

        Returns:
            无返回值。

        Raises:
            ValueError: schema 或 proof 边界非法时抛出。
        """

        if self.schema_version != DOCLING_TEMPLATE_FIELD_SCHEMA_VERSION:
            raise ValueError("unsupported docling template field schema_version")
        if self.candidate_only is not True:
            raise ValueError("Docling template field result must remain candidate_only")
        if self.source_truth_status != "not_proven":
            raise ValueError("Docling template field result must keep source_truth_status=not_proven")


@dataclass(frozen=True, slots=True)
class _FieldMatch:
    """内部字段命中结果。"""

    field_path: str
    value: object
    anchors: tuple[CandidateTemplateFieldAnchor, ...]
    note: str


def extract_docling_template_fields(
    document: CandidateRepresentationDocument,
    *,
    target_field_paths: tuple[str, ...] = DEFAULT_DOCLING_TEMPLATE_FIELD_PATHS,
) -> DoclingTemplateFieldExtractionResult:
    """从 Docling 候选文档抽取分析模板字段候选。

    Args:
        document: 已投影的 Docling candidate representation。
        target_field_paths: 目标字段路径；默认使用当前计划接受的字段集合。

    Returns:
        candidate-only 模板字段候选抽取结果。

    Raises:
        ValueError: 输入不是 Docling candidate、状态越界或目标字段重复时抛出。
    """

    _validate_document(document)
    _validate_target_field_paths(target_field_paths)

    section_context_cache: _SectionContextCache = {}
    fields = tuple(
        _extract_single_field(document, field_path, section_context_cache)
        for field_path in target_field_paths
    )
    missing_field_paths = tuple(field.field_path for field in fields if field.extraction_mode == "missing")
    blocked_field_paths = tuple(
        field.field_path
        for field in fields
        if field.note is not None and field.note.startswith("blocked:")
    )
    diagnostics = {
        "target_field_count": len(target_field_paths),
        "direct_field_count": sum(1 for field in fields if field.extraction_mode == "direct"),
        "missing_field_count": len(missing_field_paths),
        "blocked_field_count": len(blocked_field_paths),
    }
    return DoclingTemplateFieldExtractionResult(
        schema_version=DOCLING_TEMPLATE_FIELD_SCHEMA_VERSION,
        fund_code=document.identity.fund_code,
        document_year=document.identity.document_year,
        candidate_only=True,
        source_truth_status="not_proven",
        fields=fields,
        missing_field_paths=missing_field_paths,
        blocked_field_paths=blocked_field_paths,
        diagnostics=diagnostics,
    )


def _validate_document(document: CandidateRepresentationDocument) -> None:
    """校验 Docling candidate 输入边界。

    Args:
        document: 候选文档。

    Returns:
        校验通过返回 ``None``。

    Raises:
        ValueError: 来源类型或 non-proof 状态非法时抛出。
    """

    if document.identity.source_kind != CandidateRepresentationSourceKind.DOCLING_PDF:
        raise ValueError("docling template field extraction requires docling_pdf_candidate")
    if document.status.candidate_status != "not_proven":
        raise ValueError("candidate_status must remain not_proven")
    if document.status.field_correctness_status != "not_proven":
        raise ValueError("field_correctness_status must remain not_proven")
    if document.status.source_truth_status != "not_proven":
        raise ValueError("source_truth_status must remain not_proven")
    if document.status.production_parser_replacement_status != "not_authorized":
        raise ValueError("production parser replacement must remain not_authorized")


def _validate_target_field_paths(target_field_paths: tuple[str, ...]) -> None:
    """校验目标字段路径集合。

    Args:
        target_field_paths: 目标字段路径。

    Returns:
        校验通过返回 ``None``。

    Raises:
        ValueError: 路径为空、重复或不在默认集合中时抛出。
    """

    if not target_field_paths:
        raise ValueError("target_field_paths cannot be empty")
    if len(set(target_field_paths)) != len(target_field_paths):
        raise ValueError("target_field_paths cannot contain duplicates")
    unsupported = sorted(set(target_field_paths) - set(DEFAULT_DOCLING_TEMPLATE_FIELD_PATHS))
    if unsupported:
        raise ValueError(f"unsupported docling template field paths: {unsupported}")


def _extract_single_field(
    document: CandidateRepresentationDocument,
    field_path: str,
    section_context_cache: _SectionContextCache,
) -> CandidateTemplateField:
    """抽取单个模板字段候选。

    Args:
        document: 候选文档。
        field_path: 目标字段路径。
        section_context_cache: 本次抽取的章节解析缓存。

    Returns:
        单字段候选结果。

    Raises:
        ValueError: 字段路径不在默认集合时抛出。
    """

    match = _match_field(document, field_path, section_context_cache)
    if match is None:
        return _missing_field(field_path, _missing_note_for(field_path))
    return CandidateTemplateField(
        field_group=_field_group(field_path),
        field_path=field_path,
        value=match.value,
        extraction_mode="direct",
        anchors=match.anchors,
        note=match.note,
        candidate_only=True,
        source_truth_status="not_proven",
    )


def _match_field(
    document: CandidateRepresentationDocument,
    field_path: str,
    section_context_cache: _SectionContextCache,
) -> _FieldMatch | None:
    """按字段路径分派匹配规则。

    Args:
        document: 候选文档。
        field_path: 目标字段路径。
        section_context_cache: 本次抽取的章节解析缓存。

    Returns:
        命中结果；未命中时返回 ``None``。

    Raises:
        无显式抛出。
    """

    if field_path in _PROFILE_LABELS:
        return _match_key_value_field(
            document,
            field_path,
            _PROFILE_LABELS[field_path],
            ("§2",),
            section_context_cache,
        )
    if field_path in _FEE_LABELS:
        return _match_key_value_field(
            document,
            field_path,
            _FEE_LABELS[field_path],
            ("§7",),
            section_context_cache,
        )
    if field_path in _PERFORMANCE_LABELS:
        return _match_performance_field(
            document,
            field_path,
            _PERFORMANCE_LABELS[field_path],
            section_context_cache,
        )
    if field_path == "tracking_error.value_text":
        return _match_tracking_error(document, section_context_cache)
    if field_path == "portfolio_managers":
        return _match_portfolio_managers(document, section_context_cache)
    if field_path == "turnover_rate":
        return _match_key_value_field(
            document,
            field_path,
            ("换手率", "股票交易金额占基金资产净值比例"),
            ("§8",),
            section_context_cache,
        )
    if field_path == "manager_alignment.manager_holding_range":
        return _match_key_value_field(
            document,
            field_path,
            ("基金经理持有", "本基金基金经理持有"),
            ("§10",),
            section_context_cache,
        )
    if field_path.startswith("holdings_snapshot."):
        return _match_holding_row(document, field_path, section_context_cache)
    return None


def _match_key_value_field(
    document: CandidateRepresentationDocument,
    field_path: str,
    labels: tuple[str, ...],
    section_ids: tuple[str, ...],
    section_context_cache: _SectionContextCache,
) -> _FieldMatch | None:
    """从候选表格或文本块匹配键值字段。

    Args:
        document: 候选文档。
        field_path: 目标字段路径。
        labels: 可接受标签。
        section_ids: 允许章节。
        section_context_cache: 本次抽取的章节解析缓存。

    Returns:
        命中结果；未命中时返回 ``None``。

    Raises:
        无显式抛出。
    """

    table_match = _match_key_value_table_field(
        document,
        field_path,
        labels,
        section_ids,
        section_context_cache,
    )
    if table_match is not None:
        return table_match
    return _match_text_label_field(document, field_path, labels, section_ids, section_context_cache)


def _match_key_value_table_field(
    document: CandidateRepresentationDocument,
    field_path: str,
    labels: tuple[str, ...],
    section_ids: tuple[str, ...],
    section_context_cache: _SectionContextCache,
) -> _FieldMatch | None:
    """从候选表格匹配键值字段。

    Args:
        document: 候选文档。
        field_path: 目标字段路径。
        labels: 可接受标签。
        section_ids: 允许章节。
        section_context_cache: 本次抽取的章节解析缓存。

    Returns:
        命中结果；未命中时返回 ``None``。

    Raises:
        无显式抛出。
    """

    for table in document.tables:
        effective_section_id = _effective_section_id(document, table, section_context_cache)
        if not _section_allowed(effective_section_id, section_ids):
            continue
        rows = _group_cells_by_row(table)
        for row_cells in rows:
            label_cell = _find_label_cell(row_cells, labels)
            if label_cell is None:
                continue
            value_cell = _find_value_cell(row_cells, label_cell)
            if value_cell is None:
                continue
            value = _normalize_text(value_cell.text)
            if not value:
                continue
            return _field_match(
                document,
                field_path,
                value,
                _anchor_for_cell(
                    document,
                    table,
                    value_cell,
                    note=f"label={_normalize_text(label_cell.text)}",
                    section_id=effective_section_id,
                ),
                "candidate_table_key_value_match",
            )
    return None


def _match_text_label_field(
    document: CandidateRepresentationDocument,
    field_path: str,
    labels: tuple[str, ...],
    section_ids: tuple[str, ...],
    section_context_cache: _SectionContextCache,
) -> _FieldMatch | None:
    """从候选文本块匹配标签字段。

    Args:
        document: 候选文档。
        field_path: 目标字段路径。
        labels: 可接受标签。
        section_ids: 允许章节。
        section_context_cache: 本次抽取的章节解析缓存。

    Returns:
        命中结果；未命中时返回 ``None``。

    Raises:
        无显式抛出。
    """

    for block in document.text_blocks:
        effective_section_id = _effective_section_id(document, block, section_context_cache)
        if not _section_allowed(effective_section_id, section_ids):
            continue
        text = _normalize_text(block.normalized_text or block.text)
        for label in labels:
            value = _value_after_label(text, label)
            if value:
                return _field_match(
                    document,
                    field_path,
                    value,
                    _anchor_for_text_block(document, block, note=f"label={label}", section_id=effective_section_id),
                    "candidate_text_label_match",
                )
    return None


def _match_performance_field(
    document: CandidateRepresentationDocument,
    field_path: str,
    labels: tuple[str, ...],
    section_context_cache: _SectionContextCache,
) -> _FieldMatch | None:
    """从 `§3` 候选业绩表匹配净值/基准收益字段。

    Args:
        document: 候选文档。
        field_path: 目标字段路径。
        labels: 目标列头标签。
        section_context_cache: 本次抽取的章节解析缓存。

    Returns:
        命中结果；未命中时返回 ``None``。

    Raises:
        无显式抛出。
    """

    for table in document.tables:
        effective_section_id = _effective_section_id(document, table, section_context_cache)
        if not _section_allowed(effective_section_id, ("§3",)):
            continue
        for cell in table.cells:
            if not _contains_any(cell.column_header_path, labels):
                continue
            if not _contains_any(cell.row_label_path, ("过去一年", "过去一年内", "报告期")):
                continue
            value = _normalize_text(cell.text)
            if value:
                return _field_match(
                    document,
                    field_path,
                    value,
                    _anchor_for_cell(
                        document,
                        table,
                        cell,
                        note="performance_table_match",
                        section_id=effective_section_id,
                    ),
                    "candidate_performance_table_match",
                )
    return None


def _match_tracking_error(
    document: CandidateRepresentationDocument,
    section_context_cache: _SectionContextCache,
) -> _FieldMatch | None:
    """匹配实际披露的跟踪误差字段，见模板第 2 章 R=A+B-C。

    Args:
        document: 候选文档。
        section_context_cache: 本次抽取的章节解析缓存。

    Returns:
        命中结果；目标/限制/叙述性文本返回 ``None``。

    Raises:
        无显式抛出。
    """

    for block in document.text_blocks:
        effective_section_id = _effective_section_id(document, block, section_context_cache)
        if not _section_allowed(effective_section_id, ("§3", "§4")):
            continue
        text = _normalize_text(block.normalized_text or block.text)
        if "跟踪误差" not in text:
            continue
        if _contains_keyword(text, _TRACKING_ERROR_REJECT_KEYWORDS):
            continue
        if not _contains_keyword(text, _TRACKING_ERROR_ACCEPT_KEYWORDS):
            continue
        value_match = _PERCENT_PATTERN.search(text)
        if value_match is None:
            continue
        return _field_match(
            document,
            "tracking_error.value_text",
            value_match.group(0),
            _anchor_for_text_block(document, block, note="actual_tracking_error_text", section_id=effective_section_id),
            "candidate_actual_tracking_error_match",
        )
    return None


def _match_portfolio_managers(
    document: CandidateRepresentationDocument,
    section_context_cache: _SectionContextCache,
) -> _FieldMatch | None:
    """匹配基金经理列表字段，见模板第 3 章基金经理画像。

    Args:
        document: 候选文档。
        section_context_cache: 本次抽取的章节解析缓存。

    Returns:
        命中结果；未命中时返回 ``None``。

    Raises:
        无显式抛出。
    """

    managers: list[dict[str, str]] = []
    anchors: list[CandidateTemplateFieldAnchor] = []
    for table in document.tables:
        effective_section_id = _effective_section_id(document, table, section_context_cache)
        if not _section_allowed(effective_section_id, ("§4",)):
            continue
        rows = _group_cells_by_row(table)
        for row_cells in rows:
            name_cell = _find_cell_by_headers_or_labels(row_cells, ("姓名", "基金经理"))
            start_cell = _find_cell_by_headers_or_labels(row_cells, ("任职日期", "开始日期"))
            if name_cell is None:
                continue
            name = _normalize_text(name_cell.text)
            if not name or name in {"姓名", "基金经理"}:
                continue
            manager: dict[str, str] = {"name": name}
            if start_cell is not None and _normalize_text(start_cell.text):
                manager["start_date"] = _normalize_text(start_cell.text)
            managers.append(manager)
            anchors.append(
                _anchor_for_cell(
                    document,
                    table,
                    name_cell,
                    note="portfolio_manager_row",
                    section_id=effective_section_id,
                )
            )
    if not managers:
        return None
    return _field_match(
        document,
        "portfolio_managers",
        {"schema_version": "portfolio_manager_tenure_list.v1", "managers": managers},
        tuple(anchors),
        "candidate_portfolio_manager_table_match",
    )


def _match_holding_row(
    document: CandidateRepresentationDocument,
    field_path: str,
    section_context_cache: _SectionContextCache,
) -> _FieldMatch | None:
    """匹配持仓快照首行候选字段。

    Args:
        document: 候选文档。
        field_path: 持仓字段路径。
        section_context_cache: 本次抽取的章节解析缓存。

    Returns:
        命中结果；缺少上下文时返回 ``None``。

    Raises:
        无显式抛出。
    """

    required_labels = _holding_required_labels(field_path)
    for table in document.tables:
        effective_section_id = _effective_section_id(document, table, section_context_cache)
        if not _section_allowed(effective_section_id, ("§8",)):
            continue
        rows = _group_cells_by_row(table)
        for row_cells in rows:
            if required_labels and not _row_contains_any(row_cells, required_labels):
                continue
            name_cell = _find_cell_by_headers_or_labels(row_cells, ("股票名称", "债券名称", "基金名称", "名称"))
            value_cell = _find_cell_by_headers_or_labels(row_cells, ("公允价值", "金额"))
            ratio_cell = _find_cell_by_headers_or_labels(row_cells, ("占基金资产净值比例", "占净值比例"))
            if name_cell is None:
                continue
            value = {
                "name": _normalize_text(name_cell.text),
                "fair_value_cny": _normalize_text(value_cell.text) if value_cell is not None else None,
                "net_asset_ratio": _normalize_text(ratio_cell.text) if ratio_cell is not None else None,
            }
            if not value["name"]:
                continue
            return _field_match(
                document,
                field_path,
                {"rows": (value,)},
                _anchor_for_cell(
                    document,
                    table,
                    name_cell,
                    note="holding_row_match",
                    section_id=effective_section_id,
                ),
                "candidate_holding_table_match",
            )
    return None


def _holding_required_labels(field_path: str) -> tuple[str, ...]:
    """返回持仓字段的必要行/表上下文标签。

    Args:
        field_path: 持仓字段路径。

    Returns:
        必要标签。

    Raises:
        无显式抛出。
    """

    if field_path == "holdings_snapshot.top_holdings":
        return ("股票", "权益")
    if field_path == "holdings_snapshot.bond_top_holdings":
        return ("债券", "固定收益")
    if field_path == "holdings_snapshot.target_fund_holdings":
        return ("基金投资", "目标基金", "ETF")
    return ()


def _field_match(
    document: CandidateRepresentationDocument,
    field_path: str,
    value: object,
    anchors: CandidateTemplateFieldAnchor | tuple[CandidateTemplateFieldAnchor, ...],
    note: str,
) -> _FieldMatch:
    """构造内部命中对象。

    Args:
        document: 候选文档。
        field_path: 字段路径。
        value: 候选值。
        anchors: 候选锚点。
        note: 命中说明。

    Returns:
        命中对象。

    Raises:
        无显式抛出。
    """

    anchor_tuple = anchors if isinstance(anchors, tuple) else (anchors,)
    return _FieldMatch(field_path=field_path, value=value, anchors=anchor_tuple, note=note)


def _missing_field(field_path: str, note: str) -> CandidateTemplateField:
    """构造显式缺失字段。

    Args:
        field_path: 字段路径。
        note: 缺失原因。

    Returns:
        candidate-only 缺失字段。

    Raises:
        无显式抛出。
    """

    return CandidateTemplateField(
        field_group=_field_group(field_path),
        field_path=field_path,
        value=None,
        extraction_mode="missing",
        anchors=(),
        note=note,
        candidate_only=True,
        source_truth_status="not_proven",
    )


def _missing_note_for(field_path: str) -> str:
    """返回稳定缺失原因码。

    Args:
        field_path: 字段路径。

    Returns:
        缺失原因码。

    Raises:
        无显式抛出。
    """

    if field_path in _DEFERRED_FIELD_NOTES:
        return _DEFERRED_FIELD_NOTES[field_path]
    return f"docling_template_field_missing:{field_path}"


def _field_group(field_path: str) -> str:
    """从字段路径派生字段组。

    Args:
        field_path: 字段路径。

    Returns:
        字段组。

    Raises:
        无显式抛出。
    """

    root = field_path.split(".", 1)[0]
    if root in {"basic_identity", "product_profile", "benchmark", "risk_characteristic_text", "fee_schedule"}:
        return "profile"
    if root in {"nav_benchmark_performance", "tracking_error"}:
        return "performance"
    if root in {"portfolio_managers", "turnover_rate", "manager_alignment", "manager_strategy_text"}:
        return "manager"
    if root == "holdings_snapshot":
        return "holdings"
    if root in {"holder_structure", "share_change"}:
        return root
    if root == "bond_risk_evidence":
        return "risk"
    return root


def _group_cells_by_row(table: CandidateTableBlock) -> tuple[tuple[CandidateTableCell, ...], ...]:
    """按行号分组候选单元格。

    Args:
        table: 候选表格。

    Returns:
        按行排序的单元格组。

    Raises:
        无显式抛出。
    """

    grouped: dict[int, list[CandidateTableCell]] = {}
    for cell in table.cells:
        row_index = cell.row_start if cell.row_start is not None else cell.cell_index
        grouped.setdefault(row_index, []).append(cell)
    rows: list[tuple[CandidateTableCell, ...]] = []
    for row_index in sorted(grouped):
        rows.append(tuple(sorted(grouped[row_index], key=_cell_column_key)))
    return tuple(rows)


def _cell_column_key(cell: CandidateTableCell) -> tuple[int, int]:
    """返回单元格排序键。

    Args:
        cell: 候选单元格。

    Returns:
        `(column_start, cell_index)`。

    Raises:
        无显式抛出。
    """

    return (cell.column_start if cell.column_start is not None else cell.cell_index, cell.cell_index)


def _find_label_cell(
    row_cells: tuple[CandidateTableCell, ...],
    labels: tuple[str, ...],
) -> CandidateTableCell | None:
    """在一行中查找标签单元格。

    Args:
        row_cells: 同一行单元格。
        labels: 标签集合。

    Returns:
        标签单元格；未命中返回 ``None``。

    Raises:
        无显式抛出。
    """

    for cell in row_cells:
        text = _normalize_text(cell.text)
        if _contains_keyword(text, labels) or _contains_any(cell.row_label_path, labels):
            return cell
    return None


def _find_value_cell(
    row_cells: tuple[CandidateTableCell, ...],
    label_cell: CandidateTableCell,
) -> CandidateTableCell | None:
    """查找标签行中的值单元格。

    Args:
        row_cells: 同一行单元格。
        label_cell: 标签单元格。

    Returns:
        值单元格；未命中返回 ``None``。

    Raises:
        无显式抛出。
    """

    for cell in row_cells:
        if cell is label_cell:
            continue
        value = _normalize_text(cell.text)
        if value:
            return cell
    return None


def _find_cell_by_headers_or_labels(
    row_cells: tuple[CandidateTableCell, ...],
    labels: tuple[str, ...],
) -> CandidateTableCell | None:
    """按表头、行标签或文本查找单元格。

    Args:
        row_cells: 同一行单元格。
        labels: 标签集合。

    Returns:
        命中的单元格；未命中返回 ``None``。

    Raises:
        无显式抛出。
    """

    for cell in row_cells:
        if _contains_any(cell.column_header_path, labels):
            return cell
        if _contains_any(cell.row_label_path, labels):
            return cell
        if _contains_keyword(_normalize_text(cell.text), labels):
            return cell
    return None


def _row_contains_any(
    row_cells: tuple[CandidateTableCell, ...],
    labels: tuple[str, ...],
) -> bool:
    """判断一行是否包含任一上下文标签。

    Args:
        row_cells: 同一行单元格。
        labels: 标签集合。

    Returns:
        命中时返回 ``True``。

    Raises:
        无显式抛出。
    """

    for cell in row_cells:
        if _contains_keyword(_normalize_text(cell.text), labels):
            return True
        if _contains_any(cell.row_label_path, labels) or _contains_any(cell.column_header_path, labels):
            return True
    return False


def _anchor_for_cell(
    document: CandidateRepresentationDocument,
    table: CandidateTableBlock,
    cell: CandidateTableCell,
    *,
    note: str,
    section_id: str | None = None,
) -> CandidateTemplateFieldAnchor:
    """从候选表格单元格构造候选模板锚点。

    Args:
        document: 候选文档。
        table: 候选表格。
        cell: 候选单元格。
        note: 锚点说明。
        section_id: 已解析的有效章节；为空时使用表格原始章节。

    Returns:
        候选模板字段锚点。

    Raises:
        无显式抛出。
    """

    row = cell.row_start if cell.row_start is not None else cell.cell_index
    column = cell.column_start if cell.column_start is not None else cell.cell_index
    return CandidateTemplateFieldAnchor(
        source_kind="annual_report",
        document_year=document.identity.document_year,
        section_id=section_id or table.section_id,
        page_number=cell.source_locator.page_number,
        table_id=table.table_id,
        row_locator=f"cell:r{row}:c{column}:idx{cell.cell_index}",
        note=f"candidate_only:{note}; locator_hash={cell.locator_hash}",
    )


def _anchor_for_text_block(
    document: CandidateRepresentationDocument,
    block: CandidateTextBlock,
    *,
    note: str,
    section_id: str | None = None,
) -> CandidateTemplateFieldAnchor:
    """从候选文本块构造候选模板锚点。

    Args:
        document: 候选文档。
        block: 候选文本块。
        note: 锚点说明。
        section_id: 已解析的有效章节；为空时使用文本块原始章节。

    Returns:
        候选模板字段锚点。

    Raises:
        无显式抛出。
    """

    return CandidateTemplateFieldAnchor(
        source_kind="annual_report",
        document_year=document.identity.document_year,
        section_id=section_id or block.section_id,
        page_number=block.source_locator.page_number,
        table_id=None,
        row_locator=block.block_id,
        note=f"candidate_only:{note}; source_ref={block.source_locator.source_ref}",
    )


def _value_after_label(text: str, label: str) -> str | None:
    """从标签文本中截取值。

    Args:
        text: 规范化文本。
        label: 标签。

    Returns:
        标签后的值；不存在时返回 ``None``。

    Raises:
        无显式抛出。
    """

    pattern = re.compile(rf"{re.escape(label)}\s*[：:]\s*(.+)")
    match = pattern.search(text)
    if match is None:
        return None
    value = _normalize_text(match.group(1))
    return value or None


def _section_allowed(section_id: str | None, allowed: tuple[str, ...]) -> bool:
    """判断章节是否在允许集合中。

    Args:
        section_id: 章节 ID。
        allowed: 允许章节。

    Returns:
        允许时返回 ``True``。

    Raises:
        无显式抛出。
    """

    return section_id in allowed


def _effective_section_id(
    document: CandidateRepresentationDocument,
    block: CandidateTableBlock | CandidateTextBlock,
    section_context_cache: _SectionContextCache,
) -> str | None:
    """解析候选块的有效年报章节。

    Args:
        document: 候选文档。
        block: 候选表格或文本块。
        section_context_cache: 本次抽取的章节解析缓存。

    Returns:
        稳定 ``§N`` 章节；无法安全解析时返回 ``None``。

    Raises:
        无显式抛出。
    """

    cache_key = id(block)
    if cache_key in section_context_cache:
        return section_context_cache[cache_key]
    if block.section_id and block.section_id.startswith("§"):
        section_context_cache[cache_key] = block.section_id
        return block.section_id
    result = map_candidate_locator_to_anchor_candidate(
        document,
        block,
        schema_family=_schema_family_for_document(document),
    )
    if len(result.mapped) != 1:
        section_context_cache[cache_key] = None
        return None
    section_id = result.mapped[0].fields.section_id
    section_context_cache[cache_key] = section_id
    return section_id


def _schema_family_for_document(document: CandidateRepresentationDocument) -> CandidateAnchorSchemaFamily:
    """返回 section 解析使用的候选 schema family。

    Args:
        document: 候选文档。

    Returns:
        候选 schema family。

    Raises:
        无显式抛出。
    """

    if document.identity.sample_id == "S1":
        return "S1_full"
    return "S4_S5_S6_lightweight"


def _contains_any(values: tuple[str, ...], labels: tuple[str, ...]) -> bool:
    """判断路径值中是否包含任一标签。

    Args:
        values: 路径值。
        labels: 标签集合。

    Returns:
        命中时返回 ``True``。

    Raises:
        无显式抛出。
    """

    return any(_contains_keyword(_normalize_text(value), labels) for value in values)


def _contains_keyword(text: str, labels: tuple[str, ...]) -> bool:
    """判断文本是否包含任一标签。

    Args:
        text: 文本。
        labels: 标签集合。

    Returns:
        命中时返回 ``True``。

    Raises:
        无显式抛出。
    """

    return any(label in text for label in labels)


def _normalize_text(value: str) -> str:
    """规范化候选文本。

    Args:
        value: 原始文本。

    Returns:
        去除首尾空白并压缩空白后的文本。

    Raises:
        无显式抛出。
    """

    return re.sub(r"\s+", " ", value).strip()
