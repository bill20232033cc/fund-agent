"""Fund Processor/Extractor 契约模型。

本模块定义 Fund 层 Processor/Extractor 的最小公共契约，见模板第 1-6 章。
它只描述受控中间态、字段族、证据锚点和 fail-closed 缺口语义，不读取
`FundDocumentRepository`、PDF/cache/source helper、Docling、provider、LLM 或上层
Service/UI/Host。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import ClassVar, Literal, Protocol, runtime_checkable

from fund_agent.fund.documents.models import (
    AnnualReportReferenceMetadata,
    AnnualReportSourceFailureCategory,
    ParsedAnnualReport,
)
from fund_agent.fund.extractors.models import EvidenceAnchor
from fund_agent.fund.fund_type import FundType
from fund_agent.fund.source_provenance import PublicSourceProvenance
from fund_agent.fund.source_facts import AtomicSourceFactStore, empty_atomic_source_fact_store

FundReportType = Literal["annual_report"]
FundIntermediateKind = Literal[
    "parsed_annual_report.v1",
    "fund_disclosure_document.v1",
    "docling_pdf_candidate.v1",
    "pdfplumber_pdf_candidate.v1",
    "eid_xbrl_html_render_candidate.v1",
]
FundProcessorGoal = Literal["template_chapters_1_6_minimum_field_families"]
FundFieldFamilyId = Literal[
    "product_essence.v1",
    "return_attribution.v1",
    "manager_profile.v1",
    "investor_experience.v1",
    "current_stage.v1",
    "core_risk.v1",
]
FundFieldFamilyStatus = Literal["accepted", "partial", "missing", "not_applicable", "blocked"]
FundProcessorContractStatus = Literal["satisfied", "partial", "missing", "unsupported", "blocked"]
FundProcessorExtractionMode = Literal["direct", "derived", "estimated", "missing", "not_applicable"]
FundExtractionGapCode = Literal[
    "field_family_missing",
    "field_family_partial",
    "evidence_anchor_missing",
    "unsupported_processor",
    "unsupported_intermediate",
    "unsupported_intermediate_kind",
    "unsupported_report_type",
    "unsupported_fund_type",
    "unsupported_processor_goal",
    "input_type_mismatch",
    "source_provenance_unsafe",
    "candidate_boundary_blocked",
    "candidate_only_not_source_truth",
    "source_truth_admission_missing",
    "source_truth_admission_invalid",
    "derived_metric_unavailable",
    "ambiguous_table_or_locator",
    "fund_type_missing_or_ambiguous",
]
FundExtractionSourceBoundary = Literal[
    "annual_report",
    "derived_nav",
    "candidate_only",
    "unsupported_intermediate",
    "unsupported_report_type",
    "unsupported_fund_type",
    "unsupported_processor_goal",
    "ambiguous_locator",
    "source_provenance_unsafe",
    "source_truth_unverified",
]

_SUPPORTED_REPORT_TYPES = frozenset(("annual_report",))
_SUPPORTED_INTERMEDIATE_KINDS = frozenset(
    (
        "parsed_annual_report.v1",
        "fund_disclosure_document.v1",
        "docling_pdf_candidate.v1",
        "pdfplumber_pdf_candidate.v1",
        "eid_xbrl_html_render_candidate.v1",
    )
)
_SUPPORTED_PROCESSOR_GOALS = frozenset(("template_chapters_1_6_minimum_field_families",))


@dataclass(frozen=True, slots=True)
class FundProcessorDispatchKey:
    """Processor 路由键。

    Args:
        无。

    Attributes:
        fund_type: 已识别的基金类型；解析前必须先分类。
        report_type: 报告类型；S1 只支持年报。
        intermediate_kind: 受控中间态类型；S1 只实现 `ParsedAnnualReport`。
        source_kind: 公共来源类型；生产锚点当前只允许 `annual_report`、`external_api`
            或 `derived`。
        document_year: 年报年份，必须为正整数。
        fund_code: 6 位基金代码。
        processor_goal: 当前 processor 目标。

    Raises:
        ValueError: 当基金代码、年份、报告类型、中间态或目标非法时抛出。
    """

    fund_type: FundType
    report_type: FundReportType
    intermediate_kind: FundIntermediateKind
    source_kind: str
    document_year: int
    fund_code: str
    processor_goal: FundProcessorGoal = "template_chapters_1_6_minimum_field_families"

    def __post_init__(self) -> None:
        """校验 dispatch key 的显式字段。

        Args:
            无。

        Returns:
            无返回值。

        Raises:
            ValueError: 当字段值不在当前契约支持范围内时抛出。
        """

        if not (self.fund_code.isdigit() and len(self.fund_code) == 6):
            raise ValueError("fund_code 必须是 6 位数字")
        if self.document_year <= 0:
            raise ValueError("document_year 必须为正整数")
        if self.report_type not in _SUPPORTED_REPORT_TYPES:
            raise ValueError(f"report_type 不受支持：{self.report_type}")
        if self.intermediate_kind not in _SUPPORTED_INTERMEDIATE_KINDS:
            raise ValueError(f"intermediate_kind 不受支持：{self.intermediate_kind}")
        if self.processor_goal not in _SUPPORTED_PROCESSOR_GOALS:
            raise ValueError(f"processor_goal 不受支持：{self.processor_goal}")


@dataclass(frozen=True, slots=True)
class CandidateBoundaryStatus:
    """候选中间态边界状态。

    Args:
        无。

    Attributes:
        candidate_only: 是否仍为 candidate-only。
        field_correctness_status: 字段正确性状态；候选路径必须保持 `not_proven`。
        source_truth_status: 来源真源状态；候选路径必须保持 `not_proven`。
        parser_replacement_authorized: 是否授权替换生产 parser；S1 必须为 `False`。
        readiness_status: readiness 状态；S1 不声明 readiness。

    Raises:
        ValueError: 当候选边界被错误提升为 proof/readiness 时抛出。
    """

    candidate_only: bool
    field_correctness_status: Literal["not_proven"]
    source_truth_status: Literal["not_proven"]
    parser_replacement_authorized: bool = False
    readiness_status: Literal["not_ready"] = "not_ready"

    def __post_init__(self) -> None:
        """校验候选边界不能声明 proof、parser replacement 或 readiness。

        Args:
            无。

        Returns:
            无返回值。

        Raises:
            ValueError: 当候选边界字段违反 S1 NOT_READY 约束时抛出。
        """

        if not self.candidate_only:
            raise ValueError("候选边界必须保持 candidate_only=True")
        if self.parser_replacement_authorized:
            raise ValueError("候选边界不得授权 parser replacement")
        if self.readiness_status != "not_ready":
            raise ValueError("候选边界不得声明 readiness")


@dataclass(frozen=True, slots=True)
class FundDisclosureSourceTruthAdmissionProof:
    """FundDisclosureDocument source-truth admission 正向证明。

    Args:
        无。

    Attributes:
        proof_kind: 固定证明类型；只表示 repository 已加载年报身份。
        source_boundary: 固定为年报边界。
        fund_code: 6 位基金代码。
        report_year: 年报年份。
        document_kind: 固定为年报。
        intermediate_kind: 固定为 FundDisclosureDocument 中间态。
        source_kind: 固定为年报来源。
        repository_identity_verified: repository 身份校验必须为真。
        source_provenance_verified: 来源 provenance 校验必须为真。
        locator_identity_verified: locator 身份校验必须为真。
        parser_integrity_verified: parser 完整性校验必须为真。
        producer: 固定为 `FundDocumentRepository`。

    Raises:
        ValueError: 当任一字段不满足 Slice A 正向证明契约时抛出。
    """

    proof_kind: Literal["repository_loaded_annual_report_identity.v1"]
    source_boundary: Literal["annual_report"]
    fund_code: str
    report_year: int
    document_kind: Literal["annual_report"]
    intermediate_kind: Literal["fund_disclosure_document.v1"]
    source_kind: Literal["annual_report"]
    repository_identity_verified: Literal[True]
    source_provenance_verified: Literal[True]
    locator_identity_verified: Literal[True]
    parser_integrity_verified: Literal[True]
    producer: Literal["FundDocumentRepository"]

    def __post_init__(self) -> None:
        """校验 source-truth admission proof 的显式正向证明字段。

        Args:
            无。

        Returns:
            无返回值。

        Raises:
            ValueError: 当 proof 字段越界、身份非法或布尔证明不全为真时抛出。
        """

        if self.proof_kind != "repository_loaded_annual_report_identity.v1":
            raise ValueError("source-truth admission proof_kind 非法")
        if self.source_boundary != "annual_report":
            raise ValueError("source-truth admission source_boundary 非法")
        if not (self.fund_code.isdigit() and len(self.fund_code) == 6):
            raise ValueError("source-truth admission fund_code 必须是 6 位数字")
        if self.report_year <= 0:
            raise ValueError("source-truth admission report_year 必须为正整数")
        if self.document_kind != "annual_report":
            raise ValueError("source-truth admission document_kind 非法")
        if self.intermediate_kind != "fund_disclosure_document.v1":
            raise ValueError("source-truth admission intermediate_kind 非法")
        if self.source_kind != "annual_report":
            raise ValueError("source-truth admission source_kind 非法")
        if self.producer != "FundDocumentRepository":
            raise ValueError("source-truth admission producer 非法")
        if not (
            self.repository_identity_verified is True
            and self.source_provenance_verified is True
            and self.locator_identity_verified is True
            and self.parser_integrity_verified is True
        ):
            raise ValueError("source-truth admission proof booleans 必须全为 True")


@runtime_checkable
class FundDisclosureDocumentIntermediate(Protocol):
    """受控文档表示中间态协议。

    任何进入 Processor 边界的 `FundDisclosureDocument`-like 对象都必须实现该协议。
    本协议只描述报告身份、受控中间态类型、公共来源 provenance 与失败分类；不描述
    完整文档内容，也不暴露 Docling、PDF/cache/source helper 或 parser 原始产物。
    """

    @property
    def document_kind(self) -> FundReportType:
        """返回报告类型。

        Args:
            无。

        Returns:
            当前只允许 `annual_report`。

        Raises:
            无显式抛出。
        """

    @property
    def fund_code(self) -> str:
        """返回基金代码。

        Args:
            无。

        Returns:
            6 位基金代码字符串。

        Raises:
            无显式抛出。
        """

    @property
    def report_year(self) -> int:
        """返回年报年份。

        Args:
            无。

        Returns:
            年报年份。

        Raises:
            无显式抛出。
        """

    @property
    def intermediate_kind(self) -> FundIntermediateKind:
        """返回受控中间态类型。

        Args:
            无。

        Returns:
            当前中间态类型。

        Raises:
            无显式抛出。
        """

    @property
    def source_provenance(self) -> PublicSourceProvenance | None:
        """返回公共来源 provenance。

        Args:
            无。

        Returns:
            可安全公开的来源 provenance；缺失时 admission helper 必须 fail-closed。

        Raises:
            无显式抛出。
        """

    @property
    def candidate_boundary(self) -> CandidateBoundaryStatus | None:
        """返回候选边界状态。

        Args:
            无。

        Returns:
            候选中间态的 fail-closed 边界；非候选中间态为 `None`。

        Raises:
            无显式抛出。
        """

    @property
    def failure_class(self) -> AnnualReportSourceFailureCategory | None:
        """返回来源失败分类。

        Args:
            无。

        Returns:
            五类标准年报来源失败分类；没有失败时为 `None`。

        Raises:
            无显式抛出。
        """


class FundDisclosureSectionLike(Protocol):
    """FundDisclosureDocument section 的最小结构协议。"""

    section_id: str
    heading_text_raw: str
    heading_text_normalized: str
    heading_path: tuple[str, ...]
    heading_level: int | None
    locator_stability: str


class FundDisclosureParagraphBlockLike(Protocol):
    """FundDisclosureDocument paragraph block 的最小结构协议。"""

    block_id: str
    section_id: str | None
    heading_path: tuple[str, ...]
    text_raw: str
    text_normalized: str
    content_hash: str
    locator_stability: str


class FundDisclosureCellLike(Protocol):
    """FundDisclosureDocument table cell locator 的最小结构协议。"""

    cell_id: str
    table_id: str
    section_anchor: str | None
    heading_path: tuple[str, ...]
    row_index: int
    column_index: int
    row_label_path: tuple[str, ...]
    column_header_path: tuple[str, ...]
    cell_text: str
    cell_text_normalized: str
    locator_stability: str


class FundDisclosureTableBlockLike(Protocol):
    """FundDisclosureDocument table block 的最小结构协议。"""

    table_id: str
    section_id: str | None
    heading_text: str | None
    heading_path: tuple[str, ...]
    table_caption_or_nearby_heading: str | None
    cells: tuple[FundDisclosureCellLike, ...]
    locator_stability: str


@runtime_checkable
class FundDisclosureDocumentContentIntermediate(FundDisclosureDocumentIntermediate, Protocol):
    """带正文结构的 FundDisclosureDocument 中间态协议。

    本协议只用于 admission 之后的 candidate evidence harness。基础 admission 仍只依赖
    ``FundDisclosureDocumentIntermediate``，避免把身份/失败分类判定与正文结构耦合。
    """

    sections: tuple[FundDisclosureSectionLike, ...]
    paragraph_blocks: tuple[FundDisclosureParagraphBlockLike, ...]
    table_blocks: tuple[FundDisclosureTableBlockLike, ...]
    source_truth_admission: FundDisclosureSourceTruthAdmissionProof | None


@dataclass(frozen=True, slots=True)
class FundProcessorInput:
    """Processor 输入契约。

    Args:
        无。

    Attributes:
        context: Processor 路由键。
        intermediate: 受控中间态；S1 只接受 `ParsedAnnualReport`。
        reference_metadata: 可选同源引用元数据。
        candidate_boundary: 可选候选边界状态；S1 生产路径不使用。
        source_provenance: 可选公共来源 provenance；缺省时 processor 从 report metadata
            投影。

    Raises:
        无显式抛出。
    """

    context: FundProcessorDispatchKey
    intermediate: ParsedAnnualReport | object
    reference_metadata: AnnualReportReferenceMetadata | None = None
    candidate_boundary: CandidateBoundaryStatus | None = None
    source_provenance: PublicSourceProvenance | None = None


@dataclass(frozen=True, slots=True)
class FundExtractionGap:
    """字段抽取缺口。

    Args:
        无。

    Attributes:
        gap_code: 稳定缺口码。
        message: 人可读缺口说明。
        field_family_id: 字段族内缺口所属字段族；跨字段缺口为 `None`。
        source_field_path: 缺失或阻断的 extractor 输出路径。
        source_boundary: 缺口所属来源边界。
        required: 该字段是否为当前 mapping table 的必需项。

    Raises:
        无显式抛出。
    """

    gap_code: FundExtractionGapCode
    message: str
    field_family_id: FundFieldFamilyId | None
    source_field_path: str | None
    source_boundary: FundExtractionSourceBoundary
    required: bool = True


@dataclass(frozen=True, slots=True)
class FundCandidateEvidenceRecord:
    """candidate-only 字段族证据记录。

    Args:
        无。

    Attributes:
        field_family_id: 候选证据所属字段族。
        source_boundary: 固定为 ``candidate_only``。
        source_field_path: 候选结构内字段路径。
        section_id: section locator。
        table_id: table locator。
        block_id: paragraph/block locator。
        cell_id: cell locator。
        heading_path: 候选 heading path。
        row_locator: 行级定位说明。
        excerpt: 候选摘录，不是 source truth。
        locator_stability: locator 稳定性标签。
        candidate_only: 固定为 ``True``。
        field_correctness_status: 固定为 ``not_proven``。
        source_truth_status: 固定为 ``not_proven``。
        parser_replacement_authorized: 固定为 ``False``。
        readiness_status: 固定为 ``not_ready``。

    Raises:
        ValueError: 当候选边界、定位或证明状态非法时抛出。
    """

    field_family_id: FundFieldFamilyId
    source_boundary: Literal["candidate_only"]
    source_field_path: str
    section_id: str | None
    table_id: str | None
    block_id: str | None
    cell_id: str | None
    heading_path: tuple[str, ...]
    row_locator: str | None
    excerpt: str
    locator_stability: str
    candidate_only: Literal[True] = True
    field_correctness_status: Literal["not_proven"] = "not_proven"
    source_truth_status: Literal["not_proven"] = "not_proven"
    parser_replacement_authorized: Literal[False] = False
    readiness_status: Literal["not_ready"] = "not_ready"

    def __post_init__(self) -> None:
        """校验 candidate evidence 不能声明 proof、source truth 或 readiness。

        Args:
            无。

        Returns:
            无返回值。

        Raises:
            ValueError: 当字段违反 candidate-only 契约时抛出。
        """

        if self.source_boundary != "candidate_only":
            raise ValueError("candidate evidence source_boundary 必须是 candidate_only")
        if not self.source_field_path:
            raise ValueError("candidate evidence source_field_path 不能为空")
        if not self.excerpt:
            raise ValueError("candidate evidence excerpt 不能为空")
        if not self.locator_stability:
            raise ValueError("candidate evidence locator_stability 不能为空")
        if not any((self.section_id, self.table_id, self.block_id, self.cell_id)):
            raise ValueError("candidate evidence 必须至少包含一个 locator identity")
        if not self.candidate_only:
            raise ValueError("candidate evidence 必须保持 candidate_only=True")
        if self.field_correctness_status != "not_proven":
            raise ValueError("candidate evidence 不得声明 field correctness")
        if self.source_truth_status != "not_proven":
            raise ValueError("candidate evidence 不得声明 source truth")
        if self.parser_replacement_authorized:
            raise ValueError("candidate evidence 不得授权 parser replacement")
        if self.readiness_status != "not_ready":
            raise ValueError("candidate evidence 不得声明 readiness")


@dataclass(frozen=True, slots=True)
class FundFieldFamilyResult:
    """单个模板字段族输出。

    Args:
        无。

    Attributes:
        field_family_id: 字段族 ID，对应模板第 1-6 章最小字段族。
        chapter_ids: 公开模板章节 ID。
        value: 字段族值；只能来自 documented mapping table。
        status: 字段族状态。
        extraction_mode: 字段族抽取模式。
        anchors: 当前字段族公共证据锚点。
        gaps: 当前字段族本地缺口；不进入 result-level gaps。
        source_provenance: 公共来源 provenance。
        candidate_evidence: candidate-only 内部证据记录；不满足 public anchor 要求。

    Raises:
        ValueError: 非缺失字段族没有 anchor 或缺失字段族没有 gap 时抛出。
    """

    field_family_id: FundFieldFamilyId
    chapter_ids: tuple[int, ...]
    value: dict[str, object]
    status: FundFieldFamilyStatus
    extraction_mode: FundProcessorExtractionMode
    anchors: tuple[EvidenceAnchor, ...]
    gaps: tuple[FundExtractionGap, ...]
    source_provenance: PublicSourceProvenance | None
    candidate_evidence: tuple[FundCandidateEvidenceRecord, ...] = ()

    def __post_init__(self) -> None:
        """校验字段族 anchor/gap 的 fail-closed 形状。

        Args:
            无。

        Returns:
            无返回值。

        Raises:
            ValueError: 当非缺失字段族缺少锚点或缺失字段族缺少缺口时抛出。
        """

        if self.status in {"accepted", "partial"} and not self.anchors:
            raise ValueError(f"{self.field_family_id} 非缺失字段族必须包含 EvidenceAnchor")
        if self.status == "missing" and not self.gaps:
            raise ValueError(f"{self.field_family_id} missing 字段族必须包含本地 gap")


@dataclass(frozen=True, slots=True)
class FundProcessorResult:
    """Processor 输出契约。

    Args:
        无。

    Attributes:
        processor_id: processor 稳定 ID。
        output_schema_version: 输出 schema 版本。
        fund_code: 6 位基金代码。
        report_year: 年报年份。
        fund_type: 基金类型。
        report_type: 报告类型。
        input_intermediate_kind: 输入中间态类型。
        field_families: 模板字段族输出。
        gaps: 跨字段族缺口；字段族本地缺口必须留在对应字段族。
        anchors: 去重后的公共证据锚点。
        source_provenance: 公共来源 provenance。
        candidate_boundary: 候选边界状态；S1 生产路径为 `None`。
        contract_status: 整体契约状态。
        source_facts: Processor 输出的 atomic source facts 真源面。

    Raises:
        ValueError: 当 result-level gaps 错收字段族本地缺口时抛出。
    """

    processor_id: str
    output_schema_version: str
    fund_code: str
    report_year: int
    fund_type: FundType
    report_type: FundReportType
    input_intermediate_kind: FundIntermediateKind
    field_families: tuple[FundFieldFamilyResult, ...]
    gaps: tuple[FundExtractionGap, ...]
    anchors: tuple[EvidenceAnchor, ...]
    source_provenance: PublicSourceProvenance | None
    candidate_boundary: CandidateBoundaryStatus | None
    contract_status: FundProcessorContractStatus
    source_facts: AtomicSourceFactStore = field(default_factory=empty_atomic_source_fact_store)

    def __post_init__(self) -> None:
        """校验 result-level gaps 只承载跨字段族缺口。

        Args:
            无。

        Returns:
            无返回值。

        Raises:
            ValueError: 当 result-level gap 带字段族 ID 时抛出。
        """

        if any(gap.field_family_id is not None for gap in self.gaps):
            raise ValueError("FundProcessorResult.gaps 只允许跨字段族缺口")


class FundProcessorProtocol(Protocol):
    """Fund Processor 协议。

    Processor 只能基于 dispatch metadata 判断支持性，且 `extract()` 只能消费已传入的
    受控中间态。实现不得读取 repository、PDF/cache/source helper、Docling、network、
    provider、LLM、Service/UI/Host、renderer 或 quality gate。
    """

    processor_id: ClassVar[str]
    priority: ClassVar[int]
    output_schema_version: ClassVar[str]

    def supports(self, context: FundProcessorDispatchKey) -> bool:
        """判断当前 processor 是否支持 dispatch key。

        Args:
            context: Processor 路由键。

        Returns:
            支持时返回 `True`。

        Raises:
            无显式抛出。
        """

    def extract(self, input_data: FundProcessorInput) -> FundProcessorResult:
        """执行字段族抽取。

        Args:
            input_data: Processor 输入契约。

        Returns:
            Processor 输出结果。

        Raises:
            实现可在契约字段非法时抛出 `ValueError`。
        """
