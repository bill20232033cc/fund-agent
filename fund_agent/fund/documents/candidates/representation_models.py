"""候选年报表示的 route-neutral 内部模型。

本模块只定义 Fund documents 层内部 candidate-only schema。它不改变
``FundDocumentRepository``、生产 parser、公共 ``EvidenceAnchor`` schema 或
Service/UI/Host/renderer/quality gate 的消费边界。
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Literal

CandidateProofStatus = Literal["not_proven"]
CandidateParserReplacementStatus = Literal["not_authorized"]
CandidateReportType = Literal["annual_report"]
CandidateLocatorStability = Literal["strong", "usable", "weak", "blocked"]
CandidateIssueSeverity = Literal["info", "reviewable", "blocking"]


class CandidateRepresentationSourceKind(StrEnum):
    """候选年报表示来源类型。"""

    DOCLING_PDF = "docling_pdf_candidate"
    PDFPLUMBER_PDF = "pdfplumber_pdf_candidate"
    EID_HTML_RENDER = "eid_xbrl_html_render_candidate"


@dataclass(frozen=True, slots=True)
class CandidateRepresentationIdentity:
    """候选表示身份信息。

    Attributes:
        source_kind: 候选来源类型。
        sample_id: 样本编号；旧 reference JSON 可为空。
        fund_code: 6 位基金代码。
        document_year: 年报年度。
        report_type: 报告类型，当前只允许年报。
        input_artifact_path: 输入 artifact 路径；blocked route 可为空。
        accepted_input_sha256: 已接受输入 hash；可为空。
        provenance_judgment_path: 支撑输入资格的 judgment 路径。
    """

    source_kind: CandidateRepresentationSourceKind
    sample_id: str | None
    fund_code: str
    document_year: int
    report_type: CandidateReportType
    input_artifact_path: str | None
    accepted_input_sha256: str | None
    provenance_judgment_path: str

    def __post_init__(self) -> None:
        """校验候选身份字段。

        Args:
            无。

        Returns:
            无返回值。

        Raises:
            ValueError: 基金代码或报告类型非法时抛出。
        """

        if not self.fund_code.isdigit() or len(self.fund_code) != 6:
            raise ValueError("fund_code must be a 6-digit string")
        if self.report_type != "annual_report":
            raise ValueError("candidate representation only supports annual_report")


@dataclass(frozen=True, slots=True)
class CandidateRepresentationStatus:
    """候选表示 non-proof 状态。

    Attributes:
        candidate_status: 候选状态。
        field_correctness_status: 字段正确性状态。
        source_truth_status: 来源真值状态。
        taxonomy_compatibility_status: taxonomy 兼容性状态。
        production_parser_replacement_status: 生产 parser replacement 授权状态。
    """

    candidate_status: CandidateProofStatus = "not_proven"
    field_correctness_status: CandidateProofStatus = "not_proven"
    source_truth_status: CandidateProofStatus = "not_proven"
    taxonomy_compatibility_status: CandidateProofStatus = "not_proven"
    production_parser_replacement_status: CandidateParserReplacementStatus = "not_authorized"

    def __post_init__(self) -> None:
        """校验所有状态保持 non-proof。

        Args:
            无。

        Returns:
            无返回值。

        Raises:
            ValueError: 任一状态越过 candidate-only 边界时抛出。
        """

        if self.candidate_status != "not_proven":
            raise ValueError("candidate_status must remain not_proven")
        if self.field_correctness_status != "not_proven":
            raise ValueError("field_correctness_status must remain not_proven")
        if self.source_truth_status != "not_proven":
            raise ValueError("source_truth_status must remain not_proven")
        if self.taxonomy_compatibility_status != "not_proven":
            raise ValueError("taxonomy_compatibility_status must remain not_proven")
        if self.production_parser_replacement_status != "not_authorized":
            raise ValueError("production parser replacement must remain not_authorized")


@dataclass(frozen=True, slots=True)
class CandidateSourceLocator:
    """route-specific 候选 source locator。

    Attributes:
        source_kind: 候选来源类型。
        source_ref: 来源内部引用。
        page_number: 页码；HTML render 可为空。
        bbox: bbox 信息；pdfplumber/EID HTML 可为空。
        url: EID HTML render URL；PDF route 通常为空。
        dom_id: HTML DOM id 或 anchor；非 HTML route 为空。
        table_index: 表格序号。
        row_index: 行序号。
        column_index: 列序号。
        char_start: 文本起始偏移。
        char_end: 文本结束偏移。
    """

    source_kind: CandidateRepresentationSourceKind
    source_ref: str | None
    page_number: int | None
    bbox: dict[str, float | str] | None
    url: str | None = None
    dom_id: str | None = None
    table_index: int | None = None
    row_index: int | None = None
    column_index: int | None = None
    char_start: int | None = None
    char_end: int | None = None


@dataclass(frozen=True, slots=True)
class CandidateSectionNode:
    """候选章节节点。"""

    section_id: str
    source_ref: str | None
    heading_text: str
    heading_path: tuple[str, ...]
    heading_level: int | None
    page_start: int | None
    page_end: int | None
    source_locator: CandidateSourceLocator
    content_hash: str | None
    confidence: CandidateLocatorStability = "usable"
    excluded_reason: str | None = None


@dataclass(frozen=True, slots=True)
class CandidateTextBlock:
    """候选文本块。"""

    block_id: str
    block_type: str
    section_id: str | None
    heading_path: tuple[str, ...]
    text: str
    normalized_text: str
    source_locator: CandidateSourceLocator
    content_hash: str | None
    excluded_reason: str | None = None


@dataclass(frozen=True, slots=True)
class CandidateTableCell:
    """候选表格单元格。"""

    cell_index: int
    row_start: int | None
    row_end: int | None
    column_start: int | None
    column_end: int | None
    row_span: int | None
    column_span: int | None
    row_header: bool
    column_header: bool
    row_label_path: tuple[str, ...]
    column_header_path: tuple[str, ...]
    text: str
    normalized_text: str
    source_locator: CandidateSourceLocator
    cell_hash: str
    locator_hash: str
    stability: CandidateLocatorStability


@dataclass(frozen=True, slots=True)
class CandidateTableBlock:
    """候选表格块。"""

    table_id: str
    source_ref: str | None
    route_table_index: int
    section_id: str | None
    heading_path: tuple[str, ...]
    page_numbers: tuple[int, ...]
    source_locator: CandidateSourceLocator
    bbox_by_page: tuple[dict[str, object], ...]
    caption: str | None
    label: str | None
    row_count: int
    column_count: int
    cell_count: int
    table_family: str
    locator_stability: CandidateLocatorStability
    excluded_reason: str | None
    failure_code: str | None
    cells: tuple[CandidateTableCell, ...]


@dataclass(frozen=True, slots=True)
class CandidateProjectionIssue:
    """候选表示投影 issue。"""

    issue_id: str
    severity: CandidateIssueSeverity
    source_kind: CandidateRepresentationSourceKind
    location: str
    message: str
    failure_code: str | None = None


@dataclass(frozen=True, slots=True)
class CandidateRepresentationDocument:
    """候选年报表示文档。"""

    schema_version: str
    identity: CandidateRepresentationIdentity
    status: CandidateRepresentationStatus
    summary_metrics: dict[str, object]
    sections: tuple[CandidateSectionNode, ...]
    text_blocks: tuple[CandidateTextBlock, ...]
    tables: tuple[CandidateTableBlock, ...]
    route_failures: tuple[CandidateProjectionIssue, ...]
    projection_issues: tuple[CandidateProjectionIssue, ...]
    blocked_claims: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class CandidateAnchorNote:
    """候选 EvidenceAnchor note。

    该对象是 candidate-internal note，不修改公共 ``EvidenceAnchor`` schema。
    """

    candidate_source_kind: CandidateRepresentationSourceKind
    artifact_hash: str | None
    source_locator: CandidateSourceLocator
    page_number_or_null: int | None
    section_id_or_heading: str | None
    table_id: str | None
    row_locator: str | None
    row_label_path: tuple[str, ...]
    column_header_path: tuple[str, ...]
    cell_hash: str | None
    locator_hash: str
    field_correctness_status: CandidateProofStatus = "not_proven"
    source_truth_status: CandidateProofStatus = "not_proven"

    def __post_init__(self) -> None:
        """校验候选 anchor note 不声明事实证明。

        Args:
            无。

        Returns:
            无返回值。

        Raises:
            ValueError: note 越过 candidate-only 边界时抛出。
        """

        if self.field_correctness_status != "not_proven":
            raise ValueError("candidate anchor note must not prove field correctness")
        if self.source_truth_status != "not_proven":
            raise ValueError("candidate anchor note must not prove source truth")
