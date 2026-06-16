"""Docling 候选表示到 EvidenceAnchor 语义字段的内部映射。

本模块只处理 Fund documents candidate internals。它不导入或返回生产
``EvidenceAnchor``，不读取 PDF，不调用 Docling，不访问 ``FundDocumentRepository``，
也不改变 Service/Host/UI/renderer/quality gate 的消费边界。年报章节归属采用
显式 ``§`` 章节 token 和闭合年报标题族判断；无法一一映射时 fail-closed。
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from typing import Literal, TypeAlias

from fund_agent.fund.documents.candidates.representation_models import (
    CandidateRepresentationDocument,
    CandidateRepresentationSourceKind,
    CandidateSectionNode,
    CandidateSourceLocator,
    CandidateTableBlock,
    CandidateTableCell,
    CandidateTextBlock,
)

CandidateAnchorBlockType = Literal["heading", "paragraph", "table", "cell"]
CandidateAnchorSchemaFamily = Literal["S1_full", "S4_S5_S6_lightweight"]
CandidateAnchorSource = Literal["docling"]
CandidateAnnualSourceKind = Literal["annual_report"]
CandidateAnchorBlock: TypeAlias = CandidateSectionNode | CandidateTextBlock | CandidateTableBlock | CandidateTableCell

_ANNUAL_SECTION_PATTERN = re.compile(r"§\s*(\d+(?:\.\d+)*)")
_NUMERIC_HEADING_PATTERN = re.compile(r"^(\d{1,2})(?:\.\d+)*\s+(.+)$")
_ARABIC_CHAPTER_PATTERN = re.compile(r"^第\s*(\d{1,2})\s*章\s*(.+)$")
_UNSUPPORTED_HEADING_NUMBER_PATTERNS = (
    re.compile(r"^\d{1,2}(?:\.\d+)*、"),
    re.compile(r"^[一二三四五六七八九十]+、"),
    re.compile(r"^\([一二三四五六七八九十]+\)"),
    re.compile(r"^第\s*[一二三四五六七八九十]+\s*[章节]"),
)
_SUPPORTED_SECTION_PREFIXES = frozenset(f"§{index}" for index in range(1, 11))
_SECTION_KEYWORD_FAMILIES: dict[str, tuple[str, ...]] = {
    "§1": ("重要提示", "目录"),
    "§2": ("基金简介", "基金概况", "基金产品概况", "基金基本情况"),
    "§3": ("主要财务指标", "基金净值表现", "过去三年"),
    "§4": ("管理人报告", "基金管理人", "报告期内基金投资策略"),
    "§5": ("托管人报告",),
    "§6": ("审计报告",),
    "§7": ("年度财务报表", "财务报表"),
    "§8": ("投资组合报告", "期末基金资产组合", "股票投资组合", "报告期末按行业分类的股票投资组合", "报告期末基金资产组合情况"),
    "§9": ("基金份额持有人信息", "持有人信息", "期末基金份额持有人户数及持有人结构"),
    "§10": ("开放式基金份额变动", "基金份额变动"),
}


@dataclass(frozen=True, slots=True)
class CandidateEvidenceAnchorFields:
    """候选锚点的 EvidenceAnchor 语义字段。

    Attributes:
        source_kind: 当前年报语义来源，只允许 ``annual_report``。
        document_year: 年报年度。
        section_id: 年报章节编号。
        page_number: 页码。
        table_id: 表格标识；非表格锚点为 ``None``。
        row_locator: 行/单元格定位；非行级锚点为 ``None``。
        note: 候选 note，保留 candidate-only 元数据。
    """

    source_kind: CandidateAnnualSourceKind
    document_year: int
    section_id: str
    page_number: int
    table_id: str | None
    row_locator: str | None
    note: str

    def __post_init__(self) -> None:
        """校验候选字段没有越过生产锚点边界。

        Args:
            无。

        Returns:
            无返回值。

        Raises:
            ValueError: 字段不满足候选年报锚点最小要求时抛出。
        """

        if self.source_kind != "annual_report":
            raise ValueError("candidate anchor fields only mirror annual_report semantics")
        if not self.section_id:
            raise ValueError("candidate anchor fields require section_id")
        if self.page_number < 1:
            raise ValueError("candidate anchor fields require positive page_number")


@dataclass(frozen=True, slots=True)
class CandidateEvidenceAnchorMapping:
    """候选 EvidenceAnchor 映射结果。

    Attributes:
        fields: EvidenceAnchor 语义字段；不是生产 ``EvidenceAnchor`` 对象。
        candidate_source: 候选来源，当前只允许 ``docling``。
        schema_family: 输入 candidate schema family。
        sample_id: 样本编号。
        candidate_only: 必须为 ``True``。
        field_correctness_status: 字段正确性状态，必须保持 ``not_proven``。
        source_truth_status: 来源真值状态，必须保持 ``not_proven``。
        block_type: 映射块类型。
        locator_summary: 原始 locator 摘要。
    """

    fields: CandidateEvidenceAnchorFields
    candidate_source: CandidateAnchorSource
    schema_family: CandidateAnchorSchemaFamily
    sample_id: str | None
    candidate_only: bool
    field_correctness_status: Literal["not_proven"]
    source_truth_status: Literal["not_proven"]
    block_type: CandidateAnchorBlockType
    locator_summary: dict[str, object | None]

    def __post_init__(self) -> None:
        """校验 wrapper 强制表达 candidate-only。

        Args:
            无。

        Returns:
            无返回值。

        Raises:
            ValueError: metadata 越过候选边界时抛出。
        """

        if self.candidate_source != "docling":
            raise ValueError("candidate_source must be docling")
        if self.candidate_only is not True:
            raise ValueError("candidate mapping must remain candidate_only")
        if self.field_correctness_status != "not_proven":
            raise ValueError("candidate mapping must not prove field correctness")
        if self.source_truth_status != "not_proven":
            raise ValueError("candidate mapping must not prove source truth")


@dataclass(frozen=True, slots=True)
class CandidateEvidenceAnchorMappingBlocked:
    """候选锚点映射阻断记录。"""

    reason_code: str
    block_type: CandidateAnchorBlockType
    message: str
    schema_family: CandidateAnchorSchemaFamily
    sample_id: str | None
    candidate_source: CandidateAnchorSource = "docling"
    candidate_only: bool = True
    field_correctness_status: Literal["not_proven"] = "not_proven"
    source_truth_status: Literal["not_proven"] = "not_proven"
    locator_summary: dict[str, object | None] | None = None


@dataclass(frozen=True, slots=True)
class CandidateEvidenceAnchorMappingResult:
    """候选锚点映射批处理结果。"""

    mapped: tuple[CandidateEvidenceAnchorMapping, ...]
    blocked: tuple[CandidateEvidenceAnchorMappingBlocked, ...]


def map_candidate_document_anchor_candidates(
    document: CandidateRepresentationDocument,
    *,
    schema_family: CandidateAnchorSchemaFamily,
) -> CandidateEvidenceAnchorMappingResult:
    """映射整个候选文档中可稳定定位的 Docling candidate 锚点。

    Args:
        document: 已投影的 candidate representation 文档。
        schema_family: 输入 schema family。

    Returns:
        候选锚点映射结果，包含 mapped 与 blocked。

    Raises:
        无显式抛出；非 Docling 输入会返回阻断记录。
    """

    mapped: list[CandidateEvidenceAnchorMapping] = []
    blocked: list[CandidateEvidenceAnchorMappingBlocked] = []
    section_index = _build_section_index(document)
    for section in document.sections:
        _append_mapping_result(
            mapped,
            blocked,
            _map_candidate_locator_to_anchor_candidate(
                document,
                section,
                schema_family=schema_family,
                section_index=section_index,
            ),
        )
    for text_block in document.text_blocks:
        _append_mapping_result(
            mapped,
            blocked,
            _map_candidate_locator_to_anchor_candidate(
                document,
                text_block,
                schema_family=schema_family,
                section_index=section_index,
            ),
        )
    for table in document.tables:
        _append_mapping_result(
            mapped,
            blocked,
            _map_candidate_locator_to_anchor_candidate(
                document,
                table,
                schema_family=schema_family,
                section_index=section_index,
            ),
        )
        for cell in table.cells:
            _append_mapping_result(
                mapped,
                blocked,
                _map_candidate_locator_to_anchor_candidate(
                    document,
                    cell,
                    schema_family=schema_family,
                    parent_table=table,
                    section_index=section_index,
                ),
            )
    return CandidateEvidenceAnchorMappingResult(mapped=tuple(mapped), blocked=tuple(blocked))


def map_candidate_locator_to_anchor_candidate(
    document: CandidateRepresentationDocument,
    block: CandidateAnchorBlock,
    *,
    schema_family: CandidateAnchorSchemaFamily,
    parent_table: CandidateTableBlock | None = None,
) -> CandidateEvidenceAnchorMappingResult:
    """把单个 candidate locator 映射为候选锚点字段。

    Args:
        document: 候选表示文档。
        block: heading/paragraph/table/cell 候选块。
        schema_family: 输入 schema family。
        parent_table: 已知父表；document 批处理时由结构化嵌套提供。

    Returns:
        单块映射结果。

    Raises:
        无显式抛出；不满足条件时返回 blocked。
    """

    return _map_candidate_locator_to_anchor_candidate(
        document,
        block,
        schema_family=schema_family,
        parent_table=parent_table,
        section_index=_build_section_index(document),
    )


def _map_candidate_locator_to_anchor_candidate(
    document: CandidateRepresentationDocument,
    block: CandidateAnchorBlock,
    *,
    schema_family: CandidateAnchorSchemaFamily,
    section_index: _SectionIndex,
    parent_table: CandidateTableBlock | None = None,
) -> CandidateEvidenceAnchorMappingResult:
    """把单个 candidate locator 映射为候选锚点字段。

    Args:
        document: 候选表示文档。
        block: heading/paragraph/table/cell 候选块。
        schema_family: 输入 schema family。
        section_index: 文档级稳定章节索引。
        parent_table: 已知父表；document 批处理时由结构化嵌套提供。

    Returns:
        单块映射结果。

    Raises:
        无显式抛出；不满足条件时返回 blocked。
    """

    block_type = _block_type(block)
    if document.identity.source_kind != CandidateRepresentationSourceKind.DOCLING_PDF:
        return _blocked_result(
            "unsupported_source_kind",
            block_type,
            "only docling_pdf_candidate can be mapped by this candidate helper",
            document,
            schema_family,
            block,
        )
    if isinstance(block, CandidateTableCell):
        return _map_cell(
            document,
            block,
            schema_family=schema_family,
            parent_table=parent_table,
            section_index=section_index,
        )
    section = _resolve_section_id(document, block, section_index=section_index)
    if section.reason_code is not None:
        return _blocked_result(section.reason_code, block_type, section.message, document, schema_family, block)
    page_number = _page_number(block, parent_table=None)
    if page_number is None:
        return _blocked_result("missing_page_number", block_type, "candidate block lacks stable page number", document, schema_family, block)
    if isinstance(block, CandidateSectionNode):
        return _mapped_result(document, block, schema_family, section.section_id, page_number, table_id=None, row_locator=None)
    if isinstance(block, CandidateTextBlock):
        return _mapped_result(document, block, schema_family, section.section_id, page_number, table_id=None, row_locator=None)
    return _mapped_result(document, block, schema_family, section.section_id, page_number, table_id=block.table_id, row_locator=None)


@dataclass(frozen=True, slots=True)
class _SectionResolution:
    """内部章节解析结果。"""

    section_id: str
    reason_code: str | None
    message: str


@dataclass(frozen=True, slots=True)
class _SectionCandidateExtraction:
    """内部章节候选提取结果。"""

    candidates: tuple[str, ...]
    unsupported_heading_number: bool


@dataclass(frozen=True, slots=True)
class _SectionIndexEntry:
    """内部章节索引条目。"""

    section_id: str
    page: int
    is_toc: bool
    is_child_heading: bool
    node_id: str


@dataclass(frozen=True, slots=True)
class _SectionSpan:
    """内部稳定章节页码半开区间。"""

    section_id: str
    start_page: int
    end_page: int | None


@dataclass(frozen=True, slots=True)
class _SectionIndex:
    """文档级稳定章节索引。"""

    sections_by_node_id: tuple[tuple[str, str], ...]
    spans: tuple[_SectionSpan, ...]
    duplicate_sections: frozenset[str]
    non_monotonic_sections: frozenset[str]

    def section_for_node_id(self, node_id: str | None) -> str | None:
        """按 candidate section id 查找稳定年报章节。

        Args:
            node_id: candidate section id。

        Returns:
            年报章节编号；不存在时返回 ``None``。

        Raises:
            无显式抛出。
        """

        if node_id is None:
            return None
        for candidate_node_id, section_id in self.sections_by_node_id:
            if candidate_node_id == node_id:
                return section_id
        return None

    def safety_reason_for_section(self, section_id: str) -> str | None:
        """返回章节索引安全阻断原因。

        Args:
            section_id: 年报章节编号。

        Returns:
            阻断原因；章节安全时返回 ``None``。

        Raises:
            无显式抛出。
        """

        if section_id in self.duplicate_sections:
            return "duplicate_section_heading"
        if section_id in self.non_monotonic_sections:
            return "section_order_not_monotonic"
        return None

    def section_for_pages(self, pages: tuple[int, ...]) -> _SectionResolution:
        """按页码半开区间解析稳定章节。

        Args:
            pages: 待解析的正页码集合。

        Returns:
            内部章节解析结果。

        Raises:
            无显式抛出。
        """

        if not pages:
            return _SectionResolution("", "missing_section_context", "candidate block has no stable section page context")
        resolved: set[str] = set()
        reasons: set[str] = set()
        for page in pages:
            span = self._span_for_page(page)
            if span is None:
                return _SectionResolution("", "missing_section_context", "candidate block page is outside stable section spans")
            reason = self.safety_reason_for_section(span.section_id)
            if reason is not None:
                reasons.add(reason)
            resolved.add(span.section_id)
        if len(resolved) > 1:
            return _SectionResolution(
                "",
                "section_span_crosses_multiple_sections",
                "candidate table page range crosses multiple stable section spans",
            )
        if reasons:
            reason_code = sorted(reasons)[0]
            return _SectionResolution("", reason_code, f"candidate section span blocked by {reason_code}")
        return _SectionResolution(next(iter(resolved)), None, "")

    def _span_for_page(self, page: int) -> _SectionSpan | None:
        """查找页码所属半开章节区间。

        Args:
            page: 正页码。

        Returns:
            命中的章节 span；未命中时返回 ``None``。

        Raises:
            无显式抛出。
        """

        for span in self.spans:
            if page < span.start_page:
                continue
            if span.end_page is not None and page >= span.end_page:
                continue
            return span
        return None


def _append_mapping_result(
    mapped: list[CandidateEvidenceAnchorMapping],
    blocked: list[CandidateEvidenceAnchorMappingBlocked],
    result: CandidateEvidenceAnchorMappingResult,
) -> None:
    """追加单块映射结果。

    Args:
        mapped: mapped 累积列表。
        blocked: blocked 累积列表。
        result: 单块结果。

    Returns:
        无返回值。

    Raises:
        无显式抛出。
    """

    mapped.extend(result.mapped)
    blocked.extend(result.blocked)


def _map_cell(
    document: CandidateRepresentationDocument,
    cell: CandidateTableCell,
    *,
    schema_family: CandidateAnchorSchemaFamily,
    parent_table: CandidateTableBlock | None,
    section_index: _SectionIndex,
) -> CandidateEvidenceAnchorMappingResult:
    """映射候选单元格。

    Args:
        document: 候选表示文档。
        cell: 候选单元格。
        schema_family: 输入 schema family。
        parent_table: 显式父表。
        section_index: 文档级稳定章节索引。

    Returns:
        单元格映射结果。

    Raises:
        无显式抛出。
    """

    table = parent_table or _resolve_parent_table(document, cell)
    if table is None:
        return _blocked_result(
            "cannot_resolve_parent_table",
            "cell",
            "cell parent table cannot be resolved by structural link, shared id or unique bbox containment",
            document,
            schema_family,
            cell,
        )
    section = _resolve_section_id(document, table, section_index=section_index)
    if section.reason_code is not None:
        return _blocked_result(section.reason_code, "cell", section.message, document, schema_family, cell)
    table_validation = _validate_cell_parent_table(table, cell, schema_family)
    if table_validation is not None:
        return _blocked_result(table_validation, "cell", f"cell locator blocked: {table_validation}", document, schema_family, cell)
    page_number = _page_number(cell, parent_table=table)
    if page_number is None:
        return _blocked_result("missing_page_number", "cell", "cell and parent table lack stable page number", document, schema_family, cell)
    row_locator = _cell_row_locator(cell, schema_family)
    if row_locator is None:
        return _blocked_result("missing_cell_position", "cell", "cell lacks deterministic row/column position", document, schema_family, cell)
    return _mapped_result(
        document,
        cell,
        schema_family,
        section.section_id,
        page_number,
        table_id=table.table_id,
        row_locator=row_locator,
    )


def _validate_cell_parent_table(
    table: CandidateTableBlock,
    cell: CandidateTableCell,
    schema_family: CandidateAnchorSchemaFamily,
) -> str | None:
    """校验父表上下文满足 schema family 的定位要求。

    Args:
        table: 候选父表。
        cell: 候选单元格。
        schema_family: 输入 schema family。

    Returns:
        阻断 reason code；通过时返回 ``None``。

    Raises:
        无显式抛出。
    """

    if not table.table_id:
        return "missing_table_id"
    if schema_family == "S4_S5_S6_lightweight":
        if table.source_locator.page_number is None and not table.page_numbers:
            return "missing_page_number"
        if cell.cell_index is None or cell.row_start is None or cell.column_start is None:
            return "missing_cell_position"
        if _duplicate_cell_tuple_exists(table, cell):
            return "ambiguous_cell_tuple"
    if schema_family == "S1_full" and len(table.page_numbers) > 1 and cell.source_locator.page_number is None:
        return "missing_page_number"
    return None


def _duplicate_cell_tuple_exists(table: CandidateTableBlock, cell: CandidateTableCell) -> bool:
    """判断轻量 schema 的 cell tuple 是否重复。

    Args:
        table: 候选父表。
        cell: 目标单元格。

    Returns:
        同表内存在重复 tuple 时返回 ``True``。

    Raises:
        无显式抛出。
    """

    target = (cell.cell_index, cell.row_start, cell.column_start)
    return sum(1 for candidate in table.cells if (candidate.cell_index, candidate.row_start, candidate.column_start) == target) > 1


def _resolve_parent_table(
    document: CandidateRepresentationDocument,
    cell: CandidateTableCell,
) -> CandidateTableBlock | None:
    """按共享 id 或 bbox containment 解析候选父表。

    Args:
        document: 候选表示文档。
        cell: 候选单元格。

    Returns:
        唯一父表；无法唯一解析时返回 ``None``。

    Raises:
        无显式抛出。
    """

    by_ref = tuple(
        table
        for table in document.tables
        if cell.source_locator.source_ref
        and cell.source_locator.source_ref in {table.table_id, table.source_ref, table.source_locator.source_ref}
    )
    if len(by_ref) == 1:
        return by_ref[0]
    by_bbox = tuple(table for table in document.tables if _table_contains_cell_bbox(table, cell))
    if len(by_bbox) == 1:
        return by_bbox[0]
    return None


def _table_contains_cell_bbox(table: CandidateTableBlock, cell: CandidateTableCell) -> bool:
    """判断表格 bbox 是否唯一包含 cell bbox。

    Args:
        table: 候选表格。
        cell: 候选单元格。

    Returns:
        表格任一同页 bbox 包含 cell bbox 时返回 ``True``。

    Raises:
        无显式抛出。
    """

    cell_bbox = cell.source_locator.bbox
    if cell_bbox is None:
        return False
    cell_page = cell.source_locator.page_number
    if cell_page is None:
        return False
    for page_bbox in table.bbox_by_page:
        if page_bbox.get("page_no") != cell_page:
            continue
        raw_table_bbox = page_bbox.get("bbox")
        if isinstance(raw_table_bbox, dict) and _bbox_contains(raw_table_bbox, cell_bbox):
            return True
    table_bbox = table.source_locator.bbox
    return table.source_locator.page_number == cell_page and table_bbox is not None and _bbox_contains(table_bbox, cell_bbox)


def _bbox_contains(table_bbox: dict[str, object], cell_bbox: dict[str, object]) -> bool:
    """判断一个 bbox 是否包含另一个 bbox。

    Args:
        table_bbox: 表格 bbox。
        cell_bbox: 单元格 bbox。

    Returns:
        包含时返回 ``True``。

    Raises:
        无显式抛出。
    """

    left = _float_or_none(table_bbox.get("l"))
    top = _float_or_none(table_bbox.get("t"))
    right = _float_or_none(table_bbox.get("r"))
    bottom = _float_or_none(table_bbox.get("b"))
    cell_left = _float_or_none(cell_bbox.get("l"))
    cell_top = _float_or_none(cell_bbox.get("t"))
    cell_right = _float_or_none(cell_bbox.get("r"))
    cell_bottom = _float_or_none(cell_bbox.get("b"))
    if None in {left, top, right, bottom, cell_left, cell_top, cell_right, cell_bottom}:
        return False
    return left <= cell_left and top <= cell_top and right >= cell_right and bottom >= cell_bottom


def _resolve_section_id(
    document: CandidateRepresentationDocument,
    block: CandidateAnchorBlock,
    *,
    section_index: _SectionIndex,
) -> _SectionResolution:
    """解析候选块所属的稳定年报章节。

    Args:
        document: 候选表示文档。
        block: 候选块。
        section_index: 文档级稳定章节索引。

    Returns:
        内部章节解析结果。

    Raises:
        无显式抛出。
    """

    extraction = _section_candidates_from_block(block)
    candidates = set(extraction.candidates)
    if extraction.unsupported_heading_number and not candidates:
        return _SectionResolution("", "unsupported_heading_number", "candidate heading number is unsupported")
    if not candidates:
        section = _section_candidate_from_document_section(document, block, section_index)
        if section.reason_code is not None or section.section_id:
            return section
    if not candidates:
        page_resolution = section_index.section_for_pages(_positive_pages_for_block(block))
        if page_resolution.reason_code is not None or page_resolution.section_id:
            return page_resolution
    if not candidates:
        return _SectionResolution("", "missing_section_context", "candidate block has no section context")
    if len(candidates) > 1:
        return _SectionResolution("", "unstable_section_context", "candidate block maps to multiple annual-report sections")
    section_id = next(iter(candidates))
    if section_id not in _SUPPORTED_SECTION_PREFIXES:
        return _SectionResolution("", "unsupported_heading_number", "candidate section is outside supported annual-report section families")
    safety_reason = section_index.safety_reason_for_section(section_id)
    if safety_reason is not None:
        return _SectionResolution("", safety_reason, f"candidate section context blocked by {safety_reason}")
    return _SectionResolution(section_id, None, "")


def _section_candidates_from_block(block: CandidateAnchorBlock) -> _SectionCandidateExtraction:
    """从块自身 section/heading 字段提取年报章节候选。

    Args:
        block: 候选块。

    Returns:
        年报章节候选提取结果。

    Raises:
        无显式抛出。
    """

    values: list[str] = []
    if isinstance(block, CandidateSectionNode):
        values.extend([block.section_id, block.heading_text, *block.heading_path])
    elif isinstance(block, (CandidateTextBlock, CandidateTableBlock)):
        if block.section_id:
            values.append(block.section_id)
        values.extend(block.heading_path)
        if isinstance(block, CandidateTableBlock):
            values.extend(value for value in (block.caption, block.label) if value)
    return _section_candidates_from_texts(values)


def _section_candidate_from_document_section(
    document: CandidateRepresentationDocument,
    block: CandidateAnchorBlock,
    section_index: _SectionIndex,
) -> _SectionResolution:
    """通过 document section 节点补充章节候选。

    Args:
        document: 候选表示文档。
        block: 候选块。
        section_index: 文档级稳定章节索引。

    Returns:
        内部章节解析结果。

    Raises:
        无显式抛出。
    """

    section_id = getattr(block, "section_id", None)
    if not section_id:
        return _SectionResolution("", None, "")
    indexed_section_id = section_index.section_for_node_id(section_id)
    if indexed_section_id is not None:
        safety_reason = section_index.safety_reason_for_section(indexed_section_id)
        if safety_reason is not None:
            return _SectionResolution("", safety_reason, f"document section context blocked by {safety_reason}")
        return _SectionResolution(indexed_section_id, None, "")
    matched = tuple(section for section in document.sections if section.section_id == section_id)
    if len(matched) != 1:
        return _SectionResolution("", None, "")
    section = matched[0]
    extraction = _section_candidates_from_texts([section.section_id, section.heading_text, *section.heading_path])
    if extraction.unsupported_heading_number and not extraction.candidates:
        return _SectionResolution("", "unsupported_heading_number", "candidate heading number is unsupported")
    if len(extraction.candidates) == 1:
        section_id = extraction.candidates[0]
        safety_reason = section_index.safety_reason_for_section(section_id)
        if safety_reason is not None:
            return _SectionResolution("", safety_reason, f"document section context blocked by {safety_reason}")
        return _SectionResolution(section_id, None, "")
    if len(extraction.candidates) > 1:
        return _SectionResolution("", "unstable_section_context", "document section maps to multiple annual-report sections")
    return _SectionResolution("", None, "")


def _section_candidates_from_texts(values: list[str]) -> _SectionCandidateExtraction:
    """从文本集合提取闭合年报章节族。

    Args:
        values: 待解析文本。

    Returns:
        年报章节候选提取结果。

    Raises:
        无显式抛出。
    """

    candidates: set[str] = set()
    unsupported_heading_number = False
    for value in values:
        normalized = _normalize_heading_text(value)
        if not normalized:
            continue
        section_match = _ANNUAL_SECTION_PATTERN.search(normalized)
        if section_match:
            section_id = _section_id_from_top_level(section_match.group(1).split(".")[0])
            if section_id is None:
                unsupported_heading_number = True
            else:
                candidates.add(section_id)
            continue
        numeric_candidate = _section_candidate_from_numeric_heading(normalized)
        if numeric_candidate.unsupported_heading_number:
            unsupported_heading_number = True
            continue
        candidates.update(numeric_candidate.candidates)
        if numeric_candidate.candidates:
            continue
        for section_id, keywords in _SECTION_KEYWORD_FAMILIES.items():
            if any(keyword in normalized for keyword in keywords):
                candidates.add(section_id)
    return _SectionCandidateExtraction(tuple(sorted(candidates)), unsupported_heading_number)


def _build_section_index(document: CandidateRepresentationDocument) -> _SectionIndex:
    """为候选文档构建一次性稳定章节索引。

    Args:
        document: 候选表示文档。

    Returns:
        稳定章节索引。

    Raises:
        无显式抛出。
    """

    entries = tuple(_section_index_entries(document.sections))
    body_entries = tuple(entry for entry in entries if not entry.is_toc)
    grouped = _group_entries_by_section(body_entries)
    duplicate_sections = _duplicate_sections(grouped)
    selected_pages = {
        section_id: min(entry.page for entry in section_entries)
        for section_id, section_entries in grouped.items()
    }
    non_monotonic_sections = _non_monotonic_sections(selected_pages)
    boundary_pages = _unindexed_section_boundary_pages(document.sections)
    spans = _section_spans(selected_pages, boundary_pages)
    sections_by_node_id = tuple(
        (entry.node_id, entry.section_id)
        for entry in body_entries
        if entry.section_id in selected_pages
    )
    return _SectionIndex(
        sections_by_node_id=sections_by_node_id,
        spans=spans,
        duplicate_sections=frozenset(duplicate_sections),
        non_monotonic_sections=frozenset(non_monotonic_sections),
    )


def _section_index_entries(sections: tuple[CandidateSectionNode, ...]) -> tuple[_SectionIndexEntry, ...]:
    """从 section nodes 提取可参与索引的正页码章节条目。

    Args:
        sections: 候选 section nodes。

    Returns:
        索引条目 tuple。

    Raises:
        无显式抛出。
    """

    entries: list[_SectionIndexEntry] = []
    for section in sections:
        page = section.source_locator.page_number
        if page is None or page <= 0:
            continue
        extraction = _section_candidates_from_texts([section.section_id, section.heading_text, *section.heading_path])
        if len(extraction.candidates) != 1:
            continue
        entries.append(
            _SectionIndexEntry(
                section_id=extraction.candidates[0],
                page=page,
                is_toc=_is_toc_section(section),
                is_child_heading=_is_child_section_heading(section),
                node_id=section.section_id,
            )
        )
    return tuple(entries)


def _group_entries_by_section(
    entries: tuple[_SectionIndexEntry, ...],
) -> dict[str, tuple[_SectionIndexEntry, ...]]:
    """按年报章节归组索引条目。

    Args:
        entries: 索引条目。

    Returns:
        章节到条目的映射。

    Raises:
        无显式抛出。
    """

    grouped: dict[str, list[_SectionIndexEntry]] = {}
    for entry in entries:
        grouped.setdefault(entry.section_id, []).append(entry)
    return {section_id: tuple(section_entries) for section_id, section_entries in grouped.items()}


def _duplicate_sections(grouped: dict[str, tuple[_SectionIndexEntry, ...]]) -> set[str]:
    """识别不安全的重复正文章节。

    Args:
        grouped: 章节归组条目。

    Returns:
        重复不安全章节集合。

    Raises:
        无显式抛出。
    """

    duplicate_sections: set[str] = set()
    for section_id, entries in grouped.items():
        top_level_node_ids = {entry.node_id for entry in entries if not entry.is_child_heading}
        if len(top_level_node_ids) > 1:
            duplicate_sections.add(section_id)
    return duplicate_sections


def _non_monotonic_sections(selected_pages: dict[str, int]) -> set[str]:
    """识别跨顶层章节起始页倒序的章节。

    Args:
        selected_pages: 年报章节到正文起始页的映射。

    Returns:
        非单调章节集合。

    Raises:
        无显式抛出。
    """

    non_monotonic: set[str] = set()
    ordered = sorted(selected_pages.items(), key=lambda item: _section_number(item[0]))
    for left_index, (left_section, left_page) in enumerate(ordered):
        for right_section, right_page in ordered[left_index + 1 :]:
            if right_page < left_page:
                non_monotonic.update({left_section, right_section})
    return non_monotonic


def _unindexed_section_boundary_pages(sections: tuple[CandidateSectionNode, ...]) -> frozenset[int]:
    """提取未进入稳定章节索引的正文 section node 边界页。

    Args:
        sections: 候选 section nodes。

    Returns:
        可作为稳定 span 上界的正页码集合。

    Raises:
        无显式抛出。
    """

    boundary_pages: set[int] = set()
    for section in sections:
        page = section.source_locator.page_number
        if page is None or page <= 0:
            continue
        if _is_toc_section(section) or _is_child_section_heading(section):
            continue
        extraction = _section_candidates_from_texts([section.section_id, section.heading_text, *section.heading_path])
        if len(extraction.candidates) != 1:
            boundary_pages.add(page)
    return frozenset(boundary_pages)


def _section_spans(selected_pages: dict[str, int], boundary_pages: frozenset[int]) -> tuple[_SectionSpan, ...]:
    """根据选定正文起始页构建半开章节区间。

    Args:
        selected_pages: 年报章节到正文起始页的映射。
        boundary_pages: 不属于稳定章节起点但可截断 span 的正文边界页。

    Returns:
        半开章节区间 tuple。

    Raises:
        无显式抛出。
    """

    ordered = sorted(selected_pages.items(), key=lambda item: item[1])
    spans: list[_SectionSpan] = []
    for index, (section_id, start_page) in enumerate(ordered):
        next_stable_start = ordered[index + 1][1] if index + 1 < len(ordered) else None
        next_boundary = min((page for page in boundary_pages if page > start_page), default=None)
        next_start = _minimum_positive_page(next_stable_start, next_boundary)
        spans.append(_SectionSpan(section_id=section_id, start_page=start_page, end_page=next_start))
    return tuple(spans)


def _minimum_positive_page(left: int | None, right: int | None) -> int | None:
    """返回两个可选正页码中较小者。

    Args:
        left: 第一个候选页码。
        right: 第二个候选页码。

    Returns:
        较小正页码；两者都不存在时返回 ``None``。

    Raises:
        无显式抛出。
    """

    if left is None:
        return right
    if right is None:
        return left
    return min(left, right)


def _positive_pages_for_block(block: CandidateAnchorBlock) -> tuple[int, ...]:
    """提取块可用于章节 span 解析的正页码。

    Args:
        block: 候选块。

    Returns:
        去重正页码 tuple。

    Raises:
        无显式抛出。
    """

    pages: set[int] = set()
    page_number = block.source_locator.page_number
    if page_number is not None and page_number > 0:
        pages.add(page_number)
    if isinstance(block, CandidateTableBlock):
        pages.update(page for page in block.page_numbers if page > 0)
    return tuple(sorted(pages))


def _section_candidate_from_numeric_heading(normalized: str) -> _SectionCandidateExtraction:
    """从阿拉伯数字标题提取闭合章节候选。

    Args:
        normalized: 已 NFKC 和空白规整的标题文本。

    Returns:
        章节候选提取结果。

    Raises:
        无显式抛出。
    """

    for unsupported_pattern in _UNSUPPORTED_HEADING_NUMBER_PATTERNS:
        if unsupported_pattern.search(normalized):
            return _SectionCandidateExtraction((), True)
    match = _NUMERIC_HEADING_PATTERN.match(normalized) or _ARABIC_CHAPTER_PATTERN.match(normalized)
    if match is None:
        return _SectionCandidateExtraction((), False)
    section_id = _section_id_from_top_level(match.group(1))
    if section_id is None:
        return _SectionCandidateExtraction((), True)
    title = match.group(2)
    if _text_matches_section_family(section_id, title):
        return _SectionCandidateExtraction((section_id,), False)
    return _SectionCandidateExtraction((), True)


def _normalize_heading_text(value: str) -> str:
    """规整标题文本用于确定性匹配。

    Args:
        value: 原始标题文本。

    Returns:
        NFKC 和空白规整后的文本。

    Raises:
        无显式抛出。
    """

    return re.sub(r"\s+", " ", unicodedata.normalize("NFKC", value)).strip()


def _section_id_from_top_level(raw_number: str) -> str | None:
    """把顶层数字转换为支持的年报章节编号。

    Args:
        raw_number: 顶层数字字符串。

    Returns:
        ``§N``；不支持时返回 ``None``。

    Raises:
        无显式抛出。
    """

    try:
        number = int(raw_number)
    except ValueError:
        return None
    section_id = f"§{number}"
    if section_id not in _SUPPORTED_SECTION_PREFIXES:
        return None
    return section_id


def _text_matches_section_family(section_id: str, text: str) -> bool:
    """判断标题正文是否命中闭合章节标题族。

    Args:
        section_id: 年报章节编号。
        text: 标题正文。

    Returns:
        命中时返回 ``True``。

    Raises:
        无显式抛出。
    """

    normalized = _normalize_heading_text(text)
    return any(keyword in normalized for keyword in _SECTION_KEYWORD_FAMILIES.get(section_id, ()))


def _is_toc_section(section: CandidateSectionNode) -> bool:
    """判断 section node 是否为确定性目录节点。

    Args:
        section: 候选 section node。

    Returns:
        是 TOC/目录节点时返回 ``True``。

    Raises:
        无显式抛出。
    """

    values = (section.section_id, section.heading_text, *section.heading_path)
    normalized_values = tuple(_normalize_heading_text(value).lower() for value in values)
    return any("目录" in value or "toc" in value for value in normalized_values)


def _is_child_section_heading(section: CandidateSectionNode) -> bool:
    """判断 section node 是否为同一顶层章节的子标题。

    Args:
        section: 候选 section node。

    Returns:
        是子标题时返回 ``True``。

    Raises:
        无显式抛出。
    """

    values = (section.heading_text, *section.heading_path)
    for value in values:
        normalized = _normalize_heading_text(value)
        section_match = _ANNUAL_SECTION_PATTERN.search(normalized)
        if section_match and "." in section_match.group(1):
            return True
        if _NUMERIC_HEADING_PATTERN.match(normalized) and "." in normalized.split(" ", 1)[0]:
            return True
    return False


def _section_number(section_id: str) -> int:
    """返回年报章节数字。

    Args:
        section_id: ``§N`` 章节编号。

    Returns:
        章节数字；无法解析时返回高位数字。

    Raises:
        无显式抛出。
    """

    try:
        return int(section_id.removeprefix("§"))
    except ValueError:
        return 10_000


def _mapped_result(
    document: CandidateRepresentationDocument,
    block: CandidateAnchorBlock,
    schema_family: CandidateAnchorSchemaFamily,
    section_id: str,
    page_number: int,
    *,
    table_id: str | None,
    row_locator: str | None,
) -> CandidateEvidenceAnchorMappingResult:
    """构造单个 mapped 结果。

    Args:
        document: 候选表示文档。
        block: 候选块。
        schema_family: 输入 schema family。
        section_id: 稳定章节编号。
        page_number: 稳定页码。
        table_id: 表格 ID。
        row_locator: 行 locator。

    Returns:
        单 mapped 结果。

    Raises:
        无显式抛出。
    """

    block_type = _block_type(block)
    locator_summary = _locator_summary(block)
    fields = CandidateEvidenceAnchorFields(
        source_kind="annual_report",
        document_year=document.identity.document_year,
        section_id=section_id,
        page_number=page_number,
        table_id=table_id,
        row_locator=row_locator,
        note=_note(document, block_type, schema_family, locator_summary),
    )
    mapping = CandidateEvidenceAnchorMapping(
        fields=fields,
        candidate_source="docling",
        schema_family=schema_family,
        sample_id=document.identity.sample_id,
        candidate_only=True,
        field_correctness_status="not_proven",
        source_truth_status="not_proven",
        block_type=block_type,
        locator_summary=locator_summary,
    )
    return CandidateEvidenceAnchorMappingResult(mapped=(mapping,), blocked=())


def _blocked_result(
    reason_code: str,
    block_type: CandidateAnchorBlockType,
    message: str,
    document: CandidateRepresentationDocument,
    schema_family: CandidateAnchorSchemaFamily,
    block: CandidateAnchorBlock,
) -> CandidateEvidenceAnchorMappingResult:
    """构造单个 blocked 结果。

    Args:
        reason_code: 阻断代码。
        block_type: 候选块类型。
        message: 阻断说明。
        document: 候选表示文档。
        schema_family: 输入 schema family。
        block: 候选块。

    Returns:
        单 blocked 结果。

    Raises:
        无显式抛出。
    """

    blocked = CandidateEvidenceAnchorMappingBlocked(
        reason_code=reason_code,
        block_type=block_type,
        message=message,
        schema_family=schema_family,
        sample_id=document.identity.sample_id,
        locator_summary=_locator_summary(block),
    )
    return CandidateEvidenceAnchorMappingResult(mapped=(), blocked=(blocked,))


def _block_type(block: CandidateAnchorBlock) -> CandidateAnchorBlockType:
    """返回候选块类型。

    Args:
        block: 候选块。

    Returns:
        候选块类型。

    Raises:
        无显式抛出。
    """

    if isinstance(block, CandidateSectionNode):
        return "heading"
    if isinstance(block, CandidateTextBlock):
        return "paragraph"
    if isinstance(block, CandidateTableBlock):
        return "table"
    return "cell"


def _page_number(block: CandidateAnchorBlock, *, parent_table: CandidateTableBlock | None) -> int | None:
    """解析稳定页码。

    Args:
        block: 候选块。
        parent_table: 候选父表。

    Returns:
        稳定页码；无法唯一确定时为 ``None``。

    Raises:
        无显式抛出。
    """

    if isinstance(block, CandidateSectionNode):
        return block.source_locator.page_number
    if isinstance(block, CandidateTextBlock):
        return block.source_locator.page_number
    if isinstance(block, CandidateTableBlock):
        if block.source_locator.page_number is not None:
            return block.source_locator.page_number
        if len(block.page_numbers) == 1:
            return block.page_numbers[0]
        return None
    if block.source_locator.page_number is not None:
        return block.source_locator.page_number
    if parent_table is not None:
        return _page_number(parent_table, parent_table=None)
    return None


def _cell_row_locator(cell: CandidateTableCell, schema_family: CandidateAnchorSchemaFamily) -> str | None:
    """构造候选单元格 row locator。

    Args:
        cell: 候选单元格。
        schema_family: 输入 schema family。

    Returns:
        row locator；定位字段不足时返回 ``None``。

    Raises:
        无显式抛出。
    """

    if cell.row_start is None or cell.column_start is None:
        return None
    parts = [f"cell:r{cell.row_start}", f"c{cell.column_start}"]
    if cell.cell_index is not None:
        parts.append(f"idx{cell.cell_index}")
    elif schema_family == "S4_S5_S6_lightweight":
        return None
    if cell.row_label_path:
        parts.append(f"row_label={' > '.join(cell.row_label_path)}")
    if cell.column_header_path:
        parts.append(f"column_header={' > '.join(cell.column_header_path)}")
    return ":".join(parts[:3]) + (";" + ";".join(parts[3:]) if len(parts) > 3 else "")


def _locator_summary(block: CandidateAnchorBlock) -> dict[str, object | None]:
    """生成可审计的 locator 摘要。

    Args:
        block: 候选块。

    Returns:
        locator 摘要。

    Raises:
        无显式抛出。
    """

    locator = _source_locator(block)
    summary: dict[str, object | None] = {
        "source_ref": locator.source_ref,
        "page_number": locator.page_number,
        "table_index": locator.table_index,
        "row_index": locator.row_index,
        "column_index": locator.column_index,
        "has_bbox": locator.bbox is not None,
    }
    if isinstance(block, CandidateTableBlock):
        summary.update({"table_id": block.table_id, "section_id": block.section_id})
    if isinstance(block, CandidateTableCell):
        summary.update({"cell_index": block.cell_index, "locator_hash": block.locator_hash})
    if isinstance(block, CandidateTextBlock):
        summary.update({"block_id": block.block_id, "section_id": block.section_id})
    if isinstance(block, CandidateSectionNode):
        summary.update({"section_id": block.section_id, "heading_text": block.heading_text})
    return summary


def _source_locator(block: CandidateAnchorBlock) -> CandidateSourceLocator:
    """返回候选块的 source locator。

    Args:
        block: 候选块。

    Returns:
        source locator。

    Raises:
        无显式抛出。
    """

    return block.source_locator


def _note(
    document: CandidateRepresentationDocument,
    block_type: CandidateAnchorBlockType,
    schema_family: CandidateAnchorSchemaFamily,
    locator_summary: dict[str, object | None],
) -> str:
    """构造 candidate-only note。

    Args:
        document: 候选表示文档。
        block_type: 候选块类型。
        schema_family: 输入 schema family。
        locator_summary: locator 摘要。

    Returns:
        note 字符串。

    Raises:
        无显式抛出。
    """

    return (
        "candidate_source=docling; "
        f"schema_family={schema_family}; "
        f"sample_id={document.identity.sample_id}; "
        "candidate_only=true; "
        "field_correctness_status=not_proven; "
        f"block_type={block_type}; "
        f"locator={locator_summary}"
    )


def _float_or_none(value: object) -> float | None:
    """转换 float 值。

    Args:
        value: 输入值。

    Returns:
        float 或 ``None``。

    Raises:
        无显式抛出。
    """

    if isinstance(value, bool):
        return None
    if isinstance(value, (float, int)):
        return float(value)
    return None
