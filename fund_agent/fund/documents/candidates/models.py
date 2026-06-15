"""Docling 候选 FundDisclosureDocument 内部模型。

这些模型只用于 no-live candidate fixture 与 locator 验证，不改变当前
``ParsedAnnualReport``、``EvidenceAnchor`` 或生产年报来源策略。
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Literal, TypedDict

CandidateSourceKind = Literal["docling_pdf_candidate"]
CandidateDocumentKind = Literal["annual_report_candidate"]
CandidateTruthStatus = Literal["not_proven"]
CandidateParserReplacementStatus = Literal["not_authorized"]
CandidateReportType = Literal["annual_report"]

NormalizationRuleName = Literal[
    "cjk_space_repair",
    "date_space_repair",
    "numeric_punctuation_repair",
    "numeric_whitespace_grouping_repair_or_block",
    "header_path_reconstruction",
    "repeated_header_exclusion",
    "cross_page_table_stitching",
    "merged_cell_expansion",
    "toc_header_footer_exclusion",
    "row_label_path_generation",
    "column_header_path_generation",
]

NORMALIZATION_RULE_NAMES: tuple[NormalizationRuleName, ...] = (
    "cjk_space_repair",
    "date_space_repair",
    "numeric_punctuation_repair",
    "numeric_whitespace_grouping_repair_or_block",
    "header_path_reconstruction",
    "repeated_header_exclusion",
    "cross_page_table_stitching",
    "merged_cell_expansion",
    "toc_header_footer_exclusion",
    "row_label_path_generation",
    "column_header_path_generation",
)

DOCUMENT_TEXT_NORMALIZATION_RULE_NAMES: tuple[NormalizationRuleName, ...] = (
    "cjk_space_repair",
    "date_space_repair",
    "numeric_punctuation_repair",
    "numeric_whitespace_grouping_repair_or_block",
)

TABLE_LOCATOR_NORMALIZATION_RULE_NAMES: tuple[NormalizationRuleName, ...] = (
    "header_path_reconstruction",
    "repeated_header_exclusion",
    "cross_page_table_stitching",
    "merged_cell_expansion",
    "toc_header_footer_exclusion",
    "row_label_path_generation",
    "column_header_path_generation",
)


class CandidateFailureCode(StrEnum):
    """候选文档内部失败代码。"""

    CANDIDATE_NOT_FOUND = "candidate_not_found"
    CANDIDATE_UNAVAILABLE = "candidate_unavailable"
    CANDIDATE_IDENTITY_MISSING = "candidate_identity_missing"
    CANDIDATE_IDENTITY_MISMATCH = "candidate_identity_mismatch"
    CANDIDATE_ARTIFACT_HASH_MISSING = "candidate_artifact_hash_missing"
    CANDIDATE_ARTIFACT_HASH_MISMATCH = "candidate_artifact_hash_mismatch"
    CANDIDATE_SCHEMA_VERSION_UNSUPPORTED = "candidate_schema_version_unsupported"
    PAGE_PROVENANCE_MISSING = "page_provenance_missing"
    SECTION_HIERARCHY_UNSTABLE = "section_hierarchy_unstable"
    TABLE_CELLS_MISSING = "table_cells_missing"
    TABLE_PROVENANCE_MISSING = "table_provenance_missing"
    TABLE_SECTION_UNASSIGNED = "table_section_unassigned"
    TABLE_HEADER_UNSTABLE = "table_header_unstable"
    TABLE_SHAPE_INCONSISTENT = "table_shape_inconsistent"
    TABLE_CONTINUATION_AMBIGUOUS = "table_continuation_ambiguous"
    CELL_TEXT_EMPTY = "cell_text_empty"
    CELL_BBOX_MISSING = "cell_bbox_missing"
    CELL_HEADER_PATH_MISSING = "cell_header_path_missing"
    CELL_ROW_LABEL_PATH_MISSING = "cell_row_label_path_missing"
    CELL_SPAN_CONFLICT = "cell_span_conflict"
    CELL_LOCATOR_UNSTABLE = "cell_locator_unstable"
    NUMERIC_REPAIR_AMBIGUOUS = "numeric_repair_ambiguous"
    EXCERPT_HASH_MISMATCH = "excerpt_hash_mismatch"
    EXCERPT_TRUNCATED = "excerpt_truncated"


CandidateSectionSource = Literal["docling_heading", "toc_hint", "derived_pattern"]
CandidateConfidence = Literal["strong", "usable", "weak", "blocked"]
CandidateBlockType = Literal[
    "paragraph",
    "heading",
    "note",
    "list_item",
    "caption",
    "footnote",
    "header_footer_candidate",
]
CandidateTableFamily = Literal[
    "financial_metrics",
    "financial_statement",
    "portfolio_holding",
    "industry_holding",
    "manager_profile",
    "holder_info",
    "document_index",
    "unknown",
]
LocatorStability = Literal["strong", "usable", "weak", "blocked"]
CandidateBlockReason = Literal[
    "toc",
    "page_header",
    "page_footer",
    "cover_metadata",
    "repeated_report_title",
    "repeated_table_header",
    "ambiguous",
]


CandidateBBox = TypedDict(
    "CandidateBBox",
    {
        "l": float,
        "t": float,
        "r": float,
        "b": float,
        "coord_origin": str,
    },
)
"""Docling bbox 的 JSON 兼容形状。"""


class CandidatePageBBox(TypedDict):
    """带页码的 bbox 形状。"""

    page_no: int
    bbox: CandidateBBox


class CandidateEvidenceAnchorNote(TypedDict):
    """候选锚点投影 note，fixture-only。

    该结构放在 candidate internals 中，不改变当前 ``EvidenceAnchor`` schema。
    """

    candidate_source_kind: Literal["docling_pdf_candidate"]
    source_table_ref: str
    page_no: int
    bbox: dict[str, float | str]
    row_offsets: tuple[int, int]
    col_offsets: tuple[int, int]
    row_label_path: tuple[str, ...]
    column_header_path: tuple[str, ...]
    cell_text: str
    cell_hash: str
    locator_hash: str
    normalization: tuple[NormalizationRuleName, ...]
    source_truth_status: Literal["not_proven"]
    field_correctness_status: Literal["not_proven"]


@dataclass(frozen=True, slots=True)
class NormalizedText:
    """文本级归一化结果。

    Attributes:
        raw_text: 原始文本。
        normalized_text: 归一化后的文本。
        rules_applied: 实际改变文本或触发 block 的闭合规则名。
        failure_code: 歧义或阻断时的候选失败代码；无失败时为 ``None``。
    """

    raw_text: str
    normalized_text: str
    rules_applied: tuple[NormalizationRuleName, ...]
    failure_code: CandidateFailureCode | None = None

    @property
    def blocked(self) -> bool:
        """返回该文本归一化是否应阻断候选投影。

        Args:
            无。

        Returns:
            存在失败代码时返回 ``True``。

        Raises:
            无显式抛出。
        """

        return self.failure_code is not None


@dataclass(frozen=True, slots=True)
class CandidateArtifactIdentity:
    """候选文档身份信息。"""

    source_kind: CandidateSourceKind
    document_kind: CandidateDocumentKind
    fund_code: str
    fund_name: str | None
    report_year: int
    report_type: CandidateReportType
    input_pdf_filename: str | None
    input_pdf_mimetype: str | None
    input_pdf_binary_hash: str | None
    docling_schema_name: str | None
    docling_version: str | None
    docling_json_sha256: str
    markdown_sha256: str | None
    source_truth_status: CandidateTruthStatus = "not_proven"
    field_correctness_status: CandidateTruthStatus = "not_proven"
    taxonomy_compatibility_status: CandidateTruthStatus = "not_proven"
    production_parser_replacement_status: CandidateParserReplacementStatus = "not_authorized"

    def __post_init__(self) -> None:
        """校验候选身份状态只能保持 non-proof 值。

        Args:
            无。

        Returns:
            无返回值。

        Raises:
            ValueError: 状态字段被设置为非 candidate-only 值时抛出。
        """

        if self.source_kind != "docling_pdf_candidate":
            raise ValueError("候选 source_kind 必须为 docling_pdf_candidate")
        if self.document_kind != "annual_report_candidate":
            raise ValueError("候选 document_kind 必须为 annual_report_candidate")
        if self.report_type != "annual_report":
            raise ValueError("候选 report_type 必须为 annual_report")
        if (
            self.source_truth_status != "not_proven"
            or self.field_correctness_status != "not_proven"
            or self.taxonomy_compatibility_status != "not_proven"
        ):
            raise ValueError("候选文档不得声明 source truth、field correctness 或 taxonomy proof")
        if self.production_parser_replacement_status != "not_authorized":
            raise ValueError("候选文档不得声明生产 parser replacement 授权")


@dataclass(frozen=True, slots=True)
class CandidatePageSpan:
    """候选文档页码跨度。"""

    start_page_no: int
    end_page_no: int
    source_refs: tuple[str, ...]
    confidence: CandidateConfidence


@dataclass(frozen=True, slots=True)
class CandidateSection:
    """候选章节记录。"""

    section_id: str
    heading_text_raw: str
    heading_text_normalized: str
    heading_path: tuple[str, ...]
    heading_level: int | None
    page_span: CandidatePageSpan
    start_ref: str
    start_bbox: CandidateBBox | None
    section_source: CandidateSectionSource
    confidence: CandidateConfidence
    normalization_notes: tuple[NormalizationRuleName, ...]


@dataclass(frozen=True, slots=True)
class CandidateParagraphBlock:
    """候选段落块。"""

    block_id: str
    block_type: CandidateBlockType
    section_id: str | None
    heading_path: tuple[str, ...]
    page_no: int | None
    bbox: CandidateBBox | None
    text_raw: str
    text_normalized: str
    content_hash: str
    normalization_applied: tuple[NormalizationRuleName, ...]
    excluded_reason: CandidateBlockReason | None


@dataclass(frozen=True, slots=True)
class CandidateRawTableCell:
    """Docling table cell 的最小内部表示。"""

    bbox: CandidateBBox | None
    row_span: int
    col_span: int
    start_row_offset_idx: int
    end_row_offset_idx: int
    start_col_offset_idx: int
    end_col_offset_idx: int
    text: str
    column_header: bool
    row_header: bool
    row_section: bool
    fillable: bool


@dataclass(frozen=True, slots=True)
class CandidateTableCellLocator:
    """候选表格单元格 locator。"""

    table_id: str
    source_table_index: int
    source_table_self_ref: str
    page_no: int
    cell_bbox: CandidateBBox
    row_span: int
    col_span: int
    start_row_offset_idx: int
    end_row_offset_idx: int
    start_col_offset_idx: int
    end_col_offset_idx: int
    row_index_normalized: int
    column_index_normalized: int
    text_raw: str
    text_normalized: str
    column_header: bool
    row_header: bool
    row_section: bool
    row_label_path: tuple[str, ...]
    column_header_path: tuple[str, ...]
    cell_hash: str
    locator_hash: str
    normalization_notes: tuple[NormalizationRuleName, ...]


@dataclass(frozen=True, slots=True)
class CandidateTableBlock:
    """候选表格块。"""

    table_id: str
    source_table_index: int
    docling_self_ref: str
    section_id: str | None
    heading_path: tuple[str, ...]
    page_numbers: tuple[int, ...]
    bbox_by_page: tuple[CandidatePageBBox, ...]
    num_rows: int
    num_cols: int
    normalized_cells: tuple[CandidateTableCellLocator, ...]
    header_rows: tuple[int, ...]
    body_rows: tuple[int, ...]
    table_family: CandidateTableFamily
    continuation_group_id: str | None
    locator_stability: LocatorStability
    failure_code: CandidateFailureCode | None
    excluded_reason: CandidateBlockReason | None = None


@dataclass(frozen=True, slots=True)
class CandidateTableGroup:
    """跨页 stitched 表格返回契约。"""

    group_id: str
    source_table_ids: tuple[str, ...]
    page_numbers: tuple[int, ...]
    table_family: CandidateTableFamily
    stitched_table: CandidateTableBlock | None
    failure_code: CandidateFailureCode | None
    normalization_notes: tuple[NormalizationRuleName, ...]
