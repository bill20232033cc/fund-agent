"""报告证据包 typed model 与结构化抽取投影。

本模块属于 Agent 层 Fund 领域能力，负责把已经生成的
`StructuredFundDataBundle` 投影为报告质量基线可消费的事实、证据锚点、
数据缺口、preferred_lens 和 review status。它只消费内存中的结构化数据包，
不读取基金文档、不触发来源编排，也不改变模板第 0-7 章渲染行为。
"""

from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from collections import defaultdict
from collections.abc import Mapping
from dataclasses import asdict, dataclass, field, is_dataclass, replace
from decimal import Decimal
from typing import Final, Literal, get_args

from fund_agent.fund.data_extractor import StructuredFundDataBundle
from fund_agent.fund.extractors import EvidenceAnchor, ExtractedField
from fund_agent.fund.fund_type import FundType
from fund_agent.fund.template.contracts import LensKey
from fund_agent.fund.template.lens_application import build_lens_application_plan

REPORT_EVIDENCE_SCHEMA_VERSION: Final[str] = "report_evidence_bundle.v0"

ClassifiedFundType = FundType | Literal["unknown"]
FundTypeSlot = FundType
TypeSlotMembershipStatus = Literal[
    "matches_slot",
    "type_gap",
    "taxonomy_pending",
    "unknown",
    "not_applicable",
]
DocumentType = Literal["annual_report", "prospectus", "fund_contract", "periodic_report"]
DocumentIdentityStatus = Literal[
    "verified_annual_report",
    "unverified",
    "mismatch",
    "source_failed",
    "verified_as_annual_report_but_type_gap",
]
SourceBoundary = Literal[
    "repository_derived",
    "derived_calculation",
    "external_official",
    "manual_review",
    "unknown",
    "probe_only",
]
SourceFailureCategory = Literal[
    "none",
    "not_found",
    "unavailable",
    "schema_drift",
    "identity_mismatch",
    "integrity_error",
    "unknown_upstream_failure_category",
]
ReportAnchorSourceKind = Literal["annual_report", "external_api", "derived", "reviewed_note"]
SourceStrength = Literal[
    "fund_disclosure",
    "official_reference",
    "manager_statement",
    "third_party_reference",
    "derived",
    "manual_review",
]
FactCategory = Literal[
    "identity",
    "fund_type",
    "benchmark",
    "performance",
    "fee",
    "manager",
    "holdings",
    "holders",
    "risk",
    "valuation",
    "thermometer",
    "nav",
    "other",
]
ReportExtractionMode = Literal[
    "direct",
    "derived",
    "estimated",
    "missing",
    "manual_reviewed",
    "not_applicable",
]
FactUnit = Literal[
    "percent",
    "ratio",
    "cny",
    "date",
    "text",
    "count",
    "object",
    "not_applicable",
    "unknown",
]
GapKind = Literal[
    "missing_fact",
    "not_disclosed",
    "not_reviewed",
    "source_failure",
    "identity_conflict",
    "type_slot_gap",
    "unsupported_claim",
    "not_applicable",
    "manual_review_required",
]
GapFailureCategory = Literal[
    "not_found",
    "unavailable",
    "schema_drift",
    "identity_mismatch",
    "integrity_error",
    "not_disclosed",
    "ambiguous",
    "not_applicable",
    "unsupported_source",
    "manual_review_required",
    "not_reviewed_in_current_slice",
    "classified_fund_type_missing",
    "classified_fund_type_invalid",
    "unknown_upstream_failure_category",
]
DataGapReasonCode = Literal[
    "missing_from_extractor",
    "not_reviewed_in_current_slice",
    "not_disclosed",
    "manual_review_required",
    "classified_fund_type_missing",
    "classified_fund_type_invalid",
    "classified_as_different_fund_type",
    "unknown_upstream_failure_category",
    "unsupported_stability_claim",
    "not_applicable_to_fund_type",
    "source_failed",
]
ChapterRef = Literal[
    "chapter_0",
    "chapter_1",
    "chapter_2",
    "chapter_3",
    "chapter_4",
    "chapter_5",
    "chapter_6",
    "chapter_7",
    "report_level",
]
ReviewStatus = Literal[
    "candidate",
    "repository_verified",
    "fact_prefill_generated",
    "fact_prefill_reviewed",
    "scoring_ready",
    "accepted_baseline",
    "rejected",
    "deferred",
    "expired",
]
FactReviewStatus = Literal["not_reviewed", "partially_reviewed", "reviewed"]
SchemaRevisionStatus = Literal["current", "expired"]
FQGateStatus = Literal["pass", "warn", "block", "not_run"]
ProgrammaticAuditStatus = Literal["pass", "warn", "block", "not_run"]
JudgmentConstraint = Literal[
    "strong_allowed",
    "cautious_only",
    "must_downgrade_or_block",
    "not_evaluated",
]
ScoreDimension = Literal[
    "fact_coverage",
    "extraction_correctness",
    "evidence_traceability",
    "chapter_contract_completeness",
    "final_judgment_consistency",
    "investment_advice_boundary",
    "readability_actionability",
    "chapter_summary",
]
ScoreRecordStatus = Literal["pass", "issue", "blocked", "N/A", "skipped"]
ScoreIssueSeverity = Literal["blocking", "material", "minor"]
NextGateRecommendation = Literal[
    "source_reliability",
    "data_extraction",
    "evidence_anchor",
    "chapter_contract",
    "final_judgment_contract",
    "wording_audit",
    "writing_iteration",
    "manual_review",
    "fund_type_taxonomy",
    "stop_before_durable_baseline",
    "review_acceptance",
]
CalculationFormulaName = Literal[
    "r_abc",
    "cost_estimate",
    "thermometer_state",
    "pressure_test",
    "final_judgment_support",
    "other",
]
CalculationStatus = Literal[
    "computed",
    "blocked_by_missing_fact",
    "blocked_by_conflict",
    "not_applicable",
    "manual_review_required",
]

_SUPPORTED_FUND_TYPES: Final[tuple[FundType, ...]] = get_args(FundType)
_SUPPORTED_CLASSIFIED_FUND_TYPES: Final[tuple[str, ...]] = (*_SUPPORTED_FUND_TYPES, "unknown")
_FAIL_CLOSED_SOURCE_FAILURES: Final[frozenset[str]] = frozenset(
    ("schema_drift", "identity_mismatch", "integrity_error")
)
_FALLBACK_ALLOWED_SOURCE_FAILURES: Final[frozenset[str]] = frozenset(
    ("not_found", "unavailable")
)
_VALID_CHAPTER_REFS: Final[frozenset[str]] = frozenset(get_args(ChapterRef))
_SCORING_READY_CHAPTER_REFS: Final[tuple[ChapterRef, ...]] = (
    "chapter_0",
    "chapter_1",
    "chapter_2",
    "chapter_3",
    "chapter_4",
    "chapter_5",
    "chapter_6",
    "chapter_7",
)
_DEFAULT_MISSING_WORDING: Final[str] = "数据不足，需复核该字段后再作判断"
_TRACEABILITY_WORDING: Final[str] = "该字段缺少可追溯证据锚点，需人工复核后再用于判断"
_SECTION_SANITIZE_PATTERN: Final[re.Pattern[str]] = re.compile(r"[^A-Za-z0-9_.-]+")
_WHITESPACE_PATTERN: Final[re.Pattern[str]] = re.compile(r"\s+")


@dataclass(frozen=True, slots=True)
class _FieldSpec:
    """当前结构化字段到报告事实的投影配置。

    Args:
        无。

    Attributes:
        bundle_attribute: `StructuredFundDataBundle` 上的字段名。
        category: 报告事实分类。
        field_path: 报告事实字段路径。
        unit: 报告事实单位。
    """

    bundle_attribute: str
    category: FactCategory
    field_path: str
    unit: FactUnit


_FIELD_SPECS: Final[tuple[_FieldSpec, ...]] = (
    _FieldSpec("basic_identity", "identity", "basic_identity", "object"),
    _FieldSpec("product_profile", "identity", "product_profile", "object"),
    _FieldSpec("benchmark", "benchmark", "benchmark", "object"),
    _FieldSpec("index_profile", "benchmark", "index_profile", "object"),
    _FieldSpec("fee_schedule", "fee", "fee_schedule", "object"),
    _FieldSpec("turnover_rate", "manager", "turnover_rate", "percent"),
    _FieldSpec("nav_benchmark_performance", "performance", "nav_benchmark_performance", "object"),
    _FieldSpec("investor_return", "performance", "investor_return", "object"),
    _FieldSpec("tracking_error", "performance", "tracking_error", "ratio"),
    _FieldSpec("share_change", "holders", "share_change", "object"),
    _FieldSpec("manager_alignment", "manager", "manager_alignment", "object"),
    _FieldSpec("manager_strategy_text", "manager", "manager_strategy_text", "object"),
    _FieldSpec("holdings_snapshot", "holdings", "holdings_snapshot", "object"),
    _FieldSpec("holder_structure", "holders", "holder_structure", "object"),
)


@dataclass(frozen=True, slots=True)
class ReportSourceDocument:
    """报告证据包中的来源文档边界记录。

    Attributes:
        document_id: 文档稳定标识。
        document_type: 文档类型，本 slice 固定为年报。
        identity_status: 文档身份校验状态。
        source_boundary: 来源边界。
        source_failure_category: 来源失败分类。
        fallback_allowed: 当前失败分类是否允许 fallback。
        fallback_used: 是否已经使用 fallback。
        review_artifact_refs: 人工审阅 Markdown artifact 引用。
    """

    document_id: str
    document_type: DocumentType
    identity_status: DocumentIdentityStatus
    source_boundary: SourceBoundary
    source_failure_category: SourceFailureCategory
    fallback_allowed: bool
    fallback_used: bool
    review_artifact_refs: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class ReportEvidenceAnchor:
    """报告事实可引用的证据锚点。

    Attributes:
        anchor_id: bundle-local 稳定锚点标识。
        source_kind: 报告锚点来源类型。
        source_strength: 来源强度。
        document_id: 年报锚点所属文档标识。
        document_year: 年报年份。
        section_id: 年报章节编号。
        page_number: 页码。
        table_id: 表格标识。
        row_locator: 行级定位。
        review_artifact_ref: 人工审阅 artifact 引用。
        note: 短来源说明。
    """

    anchor_id: str
    source_kind: ReportAnchorSourceKind
    source_strength: SourceStrength
    document_id: str | None = None
    document_year: int | None = None
    section_id: str | None = None
    page_number: int | None = None
    table_id: str | None = None
    row_locator: str | None = None
    review_artifact_ref: str | None = None
    note: str | None = None


@dataclass(frozen=True, slots=True)
class ReportDataGap:
    """报告证据包中的数据缺口或用词约束。

    Attributes:
        gap_id: bundle-local 稳定缺口标识。
        gap_kind: 缺口类型。
        field_path: 字段级缺口路径。
        related_fact_id: 关联事实标识。
        related_claim_id: 关联声明标识。
        chapter_ids: 受影响章节，见模板第 0-7 章。
        failure_category: 缺口失败分类。
        reason_code: 受控原因码。
        fallback_allowed: 是否允许 fallback。
        fallback_used: 是否已经使用 fallback。
        required_report_wording: 报告必须遵守的用词约束。
        blocks_claim_ids: 被阻断的声明标识。
        blocks_scoring_dimensions: 被阻断的评分维度。
        score_issue_ids: 关联评分问题标识。
    """

    gap_id: str
    gap_kind: GapKind
    chapter_ids: tuple[ChapterRef, ...]
    failure_category: GapFailureCategory
    reason_code: DataGapReasonCode
    fallback_allowed: bool
    fallback_used: bool
    required_report_wording: str
    field_path: str | None = None
    related_fact_id: str | None = None
    related_claim_id: str | None = None
    blocks_claim_ids: tuple[str, ...] = ()
    blocks_scoring_dimensions: tuple[ScoreDimension, ...] = ()
    score_issue_ids: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class ReportFact:
    """报告可用事实记录。

    Attributes:
        fact_id: bundle-local 稳定事实标识。
        category: 事实分类。
        field_path: 当前结构化字段路径。
        value: JSON-like 抽取值或 `None`。
        unit: 事实单位。
        source_boundary: 来源边界。
        extraction_mode: 抽取模式。
        review_status: 字段审阅状态。
        period: 期间说明。
        source_anchor_ids: 全部来源锚点标识。
        source_document_ids: 来源文档标识。
        failure_category: 缺失或不安全值的失败分类。
        data_gap_refs: 同 bundle 数据缺口引用。
        score_issue_ids: 关联评分问题标识。
    """

    fact_id: str
    category: FactCategory
    field_path: str
    value: object | None
    unit: FactUnit
    source_boundary: SourceBoundary
    extraction_mode: ReportExtractionMode
    review_status: FactReviewStatus
    period: str | None = None
    source_anchor_ids: tuple[str, ...] = ()
    source_document_ids: tuple[str, ...] = ()
    failure_category: GapFailureCategory | None = None
    data_gap_refs: tuple[str, ...] = ()
    score_issue_ids: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class DerivedCalculation:
    """派生计算记录形状，首个 slice 不自动填充。

    Attributes:
        calculation_id: 稳定计算标识。
        formula_name: 计算公式名，见模板第 2 章 R=A+B-C。
        calculation_status: 计算状态。
        input_fact_ids: 输入事实标识。
        input_anchor_ids: 输入锚点标识。
        output_value: 输出值。
        assumptions: 计算假设。
        degradation_text: 降级说明。
        data_gap_refs: 同 bundle 数据缺口引用。
        score_issue_ids: 关联评分问题标识。
    """

    calculation_id: str
    formula_name: CalculationFormulaName
    calculation_status: CalculationStatus
    input_fact_ids: tuple[str, ...] = ()
    input_anchor_ids: tuple[str, ...] = ()
    output_value: object | None = None
    assumptions: tuple[str, ...] = ()
    degradation_text: str | None = None
    data_gap_refs: tuple[str, ...] = ()
    score_issue_ids: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class ReportScoreIssueLink:
    """报告证据包与评分 issue 的显式链接。

    Attributes:
        issue_id: 评分 issue 稳定标识。
        score_run_id: 评分运行标识。
        chapter_id: 章节标识或 report-level。
        dimension: 评分维度。
        status: 评分记录状态。
        next_gate_recommendation: 下一 gate 建议。
        severity: issue 严重程度。
        field_path: 字段路径。
        claim_id: 声明标识。
        contract_item_id: CHAPTER_CONTRACT / ITEM_RULE 条目标识。
        problem: 本地化问题。
        expected: 预期行为。
        observed_ref: 审阅证据引用。
        evidence_anchor_refs: 锚点或审阅 Markdown 引用。
        data_gap_refs: 同 bundle 数据缺口引用。
        na_reason: `N/A` 原因。
        reviewer_note: 审阅说明。
    """

    issue_id: str
    score_run_id: str
    chapter_id: ChapterRef
    dimension: ScoreDimension
    status: ScoreRecordStatus
    next_gate_recommendation: NextGateRecommendation
    severity: ScoreIssueSeverity | None = None
    field_path: str | None = None
    claim_id: str | None = None
    contract_item_id: str | None = None
    problem: str | None = None
    expected: str | None = None
    observed_ref: str | None = None
    evidence_anchor_refs: tuple[str, ...] = ()
    data_gap_refs: tuple[str, ...] = ()
    na_reason: str | None = None
    reviewer_note: str | None = None


@dataclass(frozen=True, slots=True)
class ReportQualityContext:
    """报告质量上下文。

    Attributes:
        fq_gate_status: FQ0-FQ6 最终状态。
        fq_issue_refs: FQ issue 引用。
        programmatic_audit_status: 程序审计状态。
        report_quality_score_refs: 评分 issue 或 run 引用。
        known_residual_refs: 已知 residual 引用。
        judgment_constraint: 最终判断约束。
    """

    fq_gate_status: FQGateStatus = "not_run"
    fq_issue_refs: tuple[str, ...] = ()
    programmatic_audit_status: ProgrammaticAuditStatus = "not_run"
    report_quality_score_refs: tuple[str, ...] = ()
    known_residual_refs: tuple[str, ...] = ()
    judgment_constraint: JudgmentConstraint = "not_evaluated"


@dataclass(frozen=True, slots=True)
class ReportPreferredLensChapter:
    """单章 preferred_lens 可序列化投影。

    Attributes:
        chapter_id: 章节标识，限定为模板第 0-7 章。
        lens_key: 实际使用的 lens key。
        used_default: 是否使用 default lens。
        primary_focus: 主要关注点。
        watch_variable_label: 观察变量标签。
        risk_focus_label: 风险关注标签。
        source_statements: CHAPTER_CONTRACT 原始 statements。
    """

    chapter_id: ChapterRef
    lens_key: LensKey
    used_default: bool
    primary_focus: str
    watch_variable_label: str | None = None
    risk_focus_label: str | None = None
    source_statements: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class ReportPreferredLensProjection:
    """preferred_lens 的 bundle 级可序列化投影。

    Attributes:
        fund_type: 已分类基金类型；未知时不投影章节。
        chapters: 模板第 0-7 章 lens 投影。
    """

    fund_type: ClassifiedFundType
    chapters: tuple[ReportPreferredLensChapter, ...] = ()


@dataclass(frozen=True, slots=True)
class ReportDataGapOverride:
    """人工审阅或已接受计划提供的显式数据缺口。

    Attributes:
        field_path: 关联字段路径。
        gap_kind: 缺口类型。
        failure_category: 缺口失败分类。
        reason_code: 原因码。
        chapter_ids: 受影响章节，见模板第 0-7 章。
        required_report_wording: 报告必须遵守的用词约束。
        related_claim_id: 关联声明标识。
        blocks_claim_ids: 被阻断的声明标识。
        blocks_scoring_dimensions: 被阻断的评分维度。
        score_issue_ids: 预链接评分 issue 标识。
    """

    field_path: str
    gap_kind: GapKind
    failure_category: GapFailureCategory
    reason_code: DataGapReasonCode
    chapter_ids: tuple[ChapterRef, ...]
    required_report_wording: str
    related_claim_id: str | None = None
    blocks_claim_ids: tuple[str, ...] = ()
    blocks_scoring_dimensions: tuple[ScoreDimension, ...] = ()
    score_issue_ids: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class ReportEvidenceProjectionContext:
    """报告证据包投影上下文。

    该上下文只承载显式审阅和投影元数据，不重复 `fund_code` / `report_year`，
    也不携带任意扩展业务参数。

    Attributes:
        run_id: 投影运行标识。
        corpus_id: 语料标识，`ad_hoc` 或 `corpus:{name}:{version}`。
        source_boundary: 来源边界。
        source_failure_category: 来源失败分类。
        fund_type_slot: 基线类型 slot。
        document_identity_status: 文档身份状态。
        fallback_used: 是否已经使用 fallback。
        review_artifact_refs: 审阅 artifact 引用。
        fact_review_status: 字段审阅状态。
        schema_revision_status: schema 修订状态。
        quality_context: 质量上下文。
        data_gap_overrides: 显式数据缺口。
        score_issue_links: 显式评分 issue 链接。
        attempted_review_status: 调用方尝试指定的状态；本 slice 禁止基线状态。
    """

    run_id: str
    corpus_id: str
    source_boundary: SourceBoundary
    source_failure_category: SourceFailureCategory
    fund_type_slot: FundType | None = None
    document_identity_status: DocumentIdentityStatus = "verified_annual_report"
    fallback_used: bool = False
    review_artifact_refs: tuple[str, ...] = ()
    fact_review_status: FactReviewStatus = "not_reviewed"
    schema_revision_status: SchemaRevisionStatus = "current"
    quality_context: ReportQualityContext = field(default_factory=ReportQualityContext)
    data_gap_overrides: tuple[ReportDataGapOverride, ...] = ()
    score_issue_links: tuple[ReportScoreIssueLink, ...] = ()
    attempted_review_status: ReviewStatus | None = None


@dataclass(frozen=True, slots=True)
class ReportEvidenceBundle:
    """报告证据包。

    Attributes:
        bundle_id: bundle 稳定标识。
        schema_version: schema 版本。
        corpus_id: 语料标识。
        fund_code: 基金代码。
        report_year: 年报年份。
        classified_fund_type: 已分类基金类型。
        type_slot_membership_status: 分类与基线 slot 的关系。
        preferred_lens: preferred_lens 投影。
        quality_context: 质量上下文。
        review_status: 派生审阅状态。
        fund_type_slot: 基线类型 slot。
        source_documents: 来源文档记录。
        facts: 报告事实。
        derived_calculations: 派生计算记录；首个 slice 默认空。
        evidence_anchors: 证据锚点。
        data_gaps: 数据缺口。
        score_issue_links: 评分 issue 链接。
        validation_messages: 非致命或致命校验消息。
    """

    bundle_id: str
    schema_version: str
    corpus_id: str
    fund_code: str
    report_year: int
    classified_fund_type: ClassifiedFundType
    type_slot_membership_status: TypeSlotMembershipStatus
    preferred_lens: ReportPreferredLensProjection
    quality_context: ReportQualityContext
    review_status: ReviewStatus
    fund_type_slot: FundType | None = None
    source_documents: tuple[ReportSourceDocument, ...] = ()
    facts: tuple[ReportFact, ...] = ()
    derived_calculations: tuple[DerivedCalculation, ...] = ()
    evidence_anchors: tuple[ReportEvidenceAnchor, ...] = ()
    data_gaps: tuple[ReportDataGap, ...] = ()
    score_issue_links: tuple[ReportScoreIssueLink, ...] = ()
    validation_messages: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class _AnchorProjection:
    """内部锚点投影暂存结构。

    Attributes:
        key: 归一化锚点去重 key。
        prefix: 锚点 id 前缀。
        locator_json: 归一化 locator JSON。
        anchor: 尚未带 id 的锚点字段。
    """

    key: tuple[str, int | None, str | None, str]
    prefix: str
    locator_json: str
    anchor: ReportEvidenceAnchor


def project_report_evidence_bundle(
    bundle: StructuredFundDataBundle,
    context: ReportEvidenceProjectionContext,
) -> ReportEvidenceBundle:
    """从结构化抽取包投影报告证据包。

    Args:
        bundle: 已由上游抽取链路生成的结构化基金数据包。
        context: 显式投影上下文。

    Returns:
        报告证据包；业务矛盾会进入 `review_status="rejected"` 和
        `validation_messages`，而不是静默清洗。

    Raises:
        ValueError: 上下文本身不合法、或调用方试图在本 slice 强制
            `accepted_baseline` 时抛出。
    """

    _validate_projection_context(context)

    document_id = _build_document_id(bundle.fund_code, bundle.report_year)
    source_document = _build_source_document(
        fund_code=bundle.fund_code,
        report_year=bundle.report_year,
        context=context,
    )
    validation_messages: list[str] = []
    data_gaps: list[ReportDataGap] = []
    hard_rejected = False

    classified_fund_type, classification_gap = _read_classified_fund_type(
        bundle=bundle,
        context=context,
    )
    if classification_gap is not None:
        data_gaps.append(classification_gap)
    type_slot_status = _derive_type_slot_membership_status(
        classified_fund_type=classified_fund_type,
        fund_type_slot=context.fund_type_slot,
    )
    type_slot_gap = _build_type_slot_gap_if_needed(
        bundle=bundle,
        context=context,
        classified_fund_type=classified_fund_type,
        type_slot_status=type_slot_status,
    )
    if type_slot_gap is not None:
        data_gaps.append(type_slot_gap)

    preferred_lens, lens_messages, lens_rejected = _project_preferred_lens(classified_fund_type)
    validation_messages.extend(lens_messages)
    hard_rejected = hard_rejected or lens_rejected

    anchor_inputs: list[tuple[_FieldSpec, EvidenceAnchor]] = []
    for spec in _FIELD_SPECS:
        extracted_field = _get_extracted_field(bundle, spec.bundle_attribute)
        anchor_inputs.extend((spec, anchor) for anchor in extracted_field.anchors)
    anchor_inputs.extend(("classified_fund_type", anchor) for anchor in bundle.basic_identity.anchors)  # type: ignore[arg-type]
    anchor_id_by_key, evidence_anchors, anchor_messages = _project_evidence_anchors(
        anchor_inputs=tuple(anchor_inputs),
        fund_code=bundle.fund_code,
        report_year=bundle.report_year,
        document_id=document_id,
    )
    validation_messages.extend(anchor_messages)

    facts: list[ReportFact] = []
    for spec in _FIELD_SPECS:
        extracted_field = _get_extracted_field(bundle, spec.bundle_attribute)
        fact, field_gaps, field_messages, field_rejected = _project_extracted_field_fact(
            bundle=bundle,
            context=context,
            spec=spec,
            extracted_field=extracted_field,
            document_id=document_id,
            anchor_id_by_key=anchor_id_by_key,
        )
        facts.append(fact)
        data_gaps.extend(field_gaps)
        validation_messages.extend(field_messages)
        hard_rejected = hard_rejected or field_rejected

    classified_fact, classified_fact_gaps = _project_classified_fund_type_fact(
        bundle=bundle,
        context=context,
        classified_fund_type=classified_fund_type,
        document_id=document_id,
        anchor_id_by_key=anchor_id_by_key,
    )
    facts.append(classified_fact)
    data_gaps.extend(classified_fact_gaps)

    override_gaps = _project_data_gap_overrides(bundle=bundle, context=context)
    data_gaps.extend(override_gaps)
    data_gaps = _deduplicate_gaps(tuple(data_gaps))
    facts = _attach_gap_refs_to_facts(tuple(facts), tuple(data_gaps))
    data_gaps = _attach_score_issue_refs_to_gaps(tuple(data_gaps), context.score_issue_links)
    facts = _attach_score_issue_refs_to_facts(tuple(facts), context.score_issue_links)

    score_messages, score_rejected = _validate_score_issue_links(
        score_issue_links=context.score_issue_links,
        data_gaps=tuple(data_gaps),
        evidence_anchors=evidence_anchors,
    )
    validation_messages.extend(score_messages)
    hard_rejected = hard_rejected or score_rejected

    quality_context = _merge_quality_context(
        context.quality_context,
        tuple(issue.issue_id for issue in context.score_issue_links),
    )
    review_status = derive_report_evidence_review_status(
        context=context,
        classified_fund_type=classified_fund_type,
        type_slot_membership_status=type_slot_status,
        preferred_lens=preferred_lens,
        facts=tuple(facts),
        data_gaps=tuple(data_gaps),
        score_issue_links=context.score_issue_links,
        validation_messages=tuple(validation_messages),
        hard_rejected=hard_rejected,
    )

    return ReportEvidenceBundle(
        bundle_id=_build_bundle_id(bundle.fund_code, bundle.report_year, context.run_id),
        schema_version=REPORT_EVIDENCE_SCHEMA_VERSION,
        corpus_id=context.corpus_id,
        fund_code=bundle.fund_code,
        report_year=bundle.report_year,
        classified_fund_type=classified_fund_type,
        fund_type_slot=context.fund_type_slot,
        type_slot_membership_status=type_slot_status,
        preferred_lens=preferred_lens,
        source_documents=(source_document,),
        facts=tuple(facts),
        derived_calculations=(),
        evidence_anchors=evidence_anchors,
        data_gaps=tuple(data_gaps),
        quality_context=quality_context,
        score_issue_links=context.score_issue_links,
        review_status=review_status,
        validation_messages=tuple(validation_messages),
    )


def derive_report_evidence_review_status(
    *,
    context: ReportEvidenceProjectionContext,
    classified_fund_type: ClassifiedFundType,
    type_slot_membership_status: TypeSlotMembershipStatus,
    preferred_lens: ReportPreferredLensProjection,
    facts: tuple[ReportFact, ...],
    data_gaps: tuple[ReportDataGap, ...],
    score_issue_links: tuple[ReportScoreIssueLink, ...],
    validation_messages: tuple[str, ...],
    hard_rejected: bool = False,
) -> ReviewStatus:
    """派生报告证据包 review status。

    Args:
        context: 投影上下文。
        classified_fund_type: 已分类基金类型。
        type_slot_membership_status: 类型 slot 关系。
        preferred_lens: preferred_lens 投影。
        facts: 报告事实。
        data_gaps: 数据缺口。
        score_issue_links: 评分 issue 链接。
        validation_messages: 校验消息。
        hard_rejected: 是否存在硬拒绝条件。

    Returns:
        派生 review status；本 slice 不会返回 `accepted_baseline`。

    Raises:
        无显式抛出。
    """

    del validation_messages
    if _has_rejected_condition(context=context, hard_rejected=hard_rejected):
        return "rejected"
    if context.schema_revision_status == "expired":
        return "expired"
    if _has_deferred_condition(
        context=context,
        classified_fund_type=classified_fund_type,
        type_slot_membership_status=type_slot_membership_status,
        data_gaps=data_gaps,
    ):
        return "deferred"
    if _is_scoring_ready(
        context=context,
        classified_fund_type=classified_fund_type,
        type_slot_membership_status=type_slot_membership_status,
        preferred_lens=preferred_lens,
        data_gaps=data_gaps,
        score_issue_links=score_issue_links,
    ):
        return "scoring_ready"
    if facts and context.fact_review_status == "reviewed":
        return "fact_prefill_reviewed"
    if facts:
        return "fact_prefill_generated"
    if context.document_identity_status == "verified_annual_report":
        return "repository_verified"
    return "candidate"


def build_gap_id(
    fund_code: str,
    report_year: int,
    gap_kind: GapKind,
    field_or_claim_path: str,
    reason_code: DataGapReasonCode,
) -> str:
    """构建确定性数据缺口标识。

    Args:
        fund_code: 基金代码。
        report_year: 年报年份。
        gap_kind: 缺口类型。
        field_or_claim_path: 字段或声明路径。
        reason_code: 原因码。

    Returns:
        确定性 gap id。

    Raises:
        无显式抛出。
    """

    return f"gap:{fund_code}:{report_year}:{gap_kind}:{field_or_claim_path}:{reason_code}"


def build_score_issue_id(
    score_run_id: str,
    fund_code: str,
    report_year: int,
    chapter_id: ChapterRef,
    dimension: ScoreDimension,
    *,
    field_path: str | None = None,
    claim_id: str | None = None,
    contract_item_id: str | None = None,
) -> str:
    """构建确定性评分 issue 标识。

    Args:
        score_run_id: 评分运行标识。
        fund_code: 基金代码。
        report_year: 年报年份。
        chapter_id: 章节标识。
        dimension: 评分维度。
        field_path: 字段路径。
        claim_id: 声明标识。
        contract_item_id: CHAPTER_CONTRACT / ITEM_RULE 条目标识。

    Returns:
        确定性 issue id。

    Raises:
        ValueError: 三类定位字段均为空时抛出。
    """

    target = field_path or claim_id or contract_item_id
    if target is None:
        raise ValueError("score issue id 需要 field_path、claim_id 或 contract_item_id")
    target_hash = hashlib.sha256(_normalize_text(target).encode("utf-8")).hexdigest()[:8]
    return f"issue:{score_run_id}:{fund_code}:{report_year}:{chapter_id}:{dimension}:{target_hash}"


def _validate_projection_context(context: ReportEvidenceProjectionContext) -> None:
    """校验投影上下文。

    Args:
        context: 投影上下文。

    Returns:
        无返回值。

    Raises:
        ValueError: 上下文字段组合不合法时抛出。
    """

    if not context.run_id.strip():
        raise ValueError("run_id 不能为空")
    if not context.corpus_id.strip():
        raise ValueError("corpus_id 不能为空")
    if not _is_valid_corpus_id(context.corpus_id):
        raise ValueError(f"corpus_id 形态不合法：{context.corpus_id}")
    if context.fund_type_slot is not None and context.fund_type_slot not in _SUPPORTED_FUND_TYPES:
        raise ValueError(f"fund_type_slot 不受支持：{context.fund_type_slot}")
    if context.fallback_used and context.source_failure_category == "none":
        raise ValueError("fallback_used=True 时 source_failure_category 不能为 none")
    if context.fallback_used and context.source_failure_category in _FAIL_CLOSED_SOURCE_FAILURES:
        raise ValueError("fail-closed 来源失败分类不允许 fallback_used=True")
    if context.source_boundary == "external_official":
        raise ValueError("external_official 不能作为年报事实唯一来源边界")
    if context.attempted_review_status == "accepted_baseline":
        raise ValueError("当前 slice 不允许强制 accepted_baseline")
    for override in context.data_gap_overrides:
        _validate_chapter_refs(override.chapter_ids)


def _is_valid_corpus_id(corpus_id: str) -> bool:
    """判断语料标识是否符合当前 slice 契约。

    Args:
        corpus_id: 语料标识。

    Returns:
        合法返回 `True`，否则返回 `False`。

    Raises:
        无显式抛出。
    """

    if corpus_id == "ad_hoc":
        return True
    parts = corpus_id.split(":")
    return len(parts) == 3 and parts[0] == "corpus" and all(part.strip() for part in parts[1:])


def _build_document_id(fund_code: str, report_year: int) -> str:
    """构建来源文档标识。

    Args:
        fund_code: 基金代码。
        report_year: 年报年份。

    Returns:
        年报文档标识。

    Raises:
        无显式抛出。
    """

    return f"doc:{fund_code}:{report_year}:annual_report"


def _build_bundle_id(fund_code: str, report_year: int, run_id: str) -> str:
    """构建报告证据包标识。

    Args:
        fund_code: 基金代码。
        report_year: 年报年份。
        run_id: 投影运行标识。

    Returns:
        报告证据包标识。

    Raises:
        无显式抛出。
    """

    return f"reb:{fund_code}:{report_year}:{REPORT_EVIDENCE_SCHEMA_VERSION}:{run_id}"


def _build_source_document(
    *,
    fund_code: str,
    report_year: int,
    context: ReportEvidenceProjectionContext,
) -> ReportSourceDocument:
    """构建来源文档记录。

    Args:
        fund_code: 基金代码。
        report_year: 年报年份。
        context: 投影上下文。

    Returns:
        来源文档记录。

    Raises:
        无显式抛出。
    """

    return ReportSourceDocument(
        document_id=_build_document_id(fund_code, report_year),
        document_type="annual_report",
        identity_status=context.document_identity_status,
        source_boundary=context.source_boundary,
        source_failure_category=context.source_failure_category,
        fallback_allowed=context.source_failure_category in _FALLBACK_ALLOWED_SOURCE_FAILURES,
        fallback_used=context.fallback_used,
        review_artifact_refs=context.review_artifact_refs,
    )


def _read_classified_fund_type(
    *,
    bundle: StructuredFundDataBundle,
    context: ReportEvidenceProjectionContext,
) -> tuple[ClassifiedFundType, ReportDataGap | None]:
    """从基础身份字段读取标准基金类型。

    Args:
        bundle: 结构化基金数据包。
        context: 投影上下文。

    Returns:
        `(分类结果, 可选数据缺口)`。

    Raises:
        无显式抛出。
    """

    value = bundle.basic_identity.value
    if not isinstance(value, Mapping) or "classified_fund_type" not in value:
        return "unknown", _build_simple_gap(
            bundle=bundle,
            context=context,
            gap_kind="missing_fact",
            field_path="classified_fund_type",
            failure_category="classified_fund_type_missing",
            reason_code="classified_fund_type_missing",
            wording="缺少基金类型分类，必须先确认基金类型再应用 preferred_lens",
            chapter_ids=("report_level",),
        )
    classified_fund_type = value["classified_fund_type"]
    if classified_fund_type not in _SUPPORTED_FUND_TYPES:
        return "unknown", _build_simple_gap(
            bundle=bundle,
            context=context,
            gap_kind="type_slot_gap",
            field_path="classified_fund_type",
            failure_category="classified_fund_type_invalid",
            reason_code="classified_fund_type_invalid",
            wording="基金类型分类不在受控域内，必须复核后再进入评分",
            chapter_ids=("report_level",),
        )
    return classified_fund_type, None  # type: ignore[return-value]


def _derive_type_slot_membership_status(
    *,
    classified_fund_type: ClassifiedFundType,
    fund_type_slot: FundType | None,
) -> TypeSlotMembershipStatus:
    """派生基金类型与基线 slot 的关系。

    Args:
        classified_fund_type: 已分类基金类型。
        fund_type_slot: 基线类型 slot。

    Returns:
        类型 slot 关系状态。

    Raises:
        无显式抛出。
    """

    if fund_type_slot is None:
        return "not_applicable"
    if classified_fund_type == "unknown":
        return "unknown"
    if classified_fund_type == fund_type_slot:
        return "matches_slot"
    if fund_type_slot == "fof_fund" and classified_fund_type == "qdii_fund":
        return "taxonomy_pending"
    return "type_gap"


def _build_type_slot_gap_if_needed(
    *,
    bundle: StructuredFundDataBundle,
    context: ReportEvidenceProjectionContext,
    classified_fund_type: ClassifiedFundType,
    type_slot_status: TypeSlotMembershipStatus,
) -> ReportDataGap | None:
    """在类型 slot 不匹配时构建数据缺口。

    Args:
        bundle: 结构化基金数据包。
        context: 投影上下文。
        classified_fund_type: 已分类基金类型。
        type_slot_status: 类型 slot 关系状态。

    Returns:
        需要时返回类型缺口，否则返回 `None`。

    Raises:
        无显式抛出。
    """

    if context.fund_type_slot is None or type_slot_status == "matches_slot":
        return None
    reason: DataGapReasonCode = (
        "classified_fund_type_missing"
        if classified_fund_type == "unknown"
        else "classified_as_different_fund_type"
    )
    return _build_simple_gap(
        bundle=bundle,
        context=context,
        gap_kind="type_slot_gap",
        field_path="classified_fund_type",
        failure_category=(
            "classified_fund_type_missing"
            if classified_fund_type == "unknown"
            else "ambiguous"
        ),
        reason_code=reason,
        wording="基金类型与当前基线 slot 不一致，不能作为该 slot 的 scoring-ready 样本",
        chapter_ids=("report_level",),
    )


def _project_preferred_lens(
    classified_fund_type: ClassifiedFundType,
) -> tuple[ReportPreferredLensProjection, tuple[str, ...], bool]:
    """投影 preferred_lens 应用计划。

    Args:
        classified_fund_type: 已分类基金类型。

    Returns:
        `(lens 投影, 校验消息, 是否硬拒绝)`。

    Raises:
        无显式抛出。
    """

    if classified_fund_type == "unknown":
        return ReportPreferredLensProjection(fund_type="unknown", chapters=()), (), False
    try:
        plan = build_lens_application_plan(classified_fund_type)
    except ValueError as exc:
        return (
            ReportPreferredLensProjection(fund_type=classified_fund_type, chapters=()),
            (f"preferred_lens resolution failed: {exc}",),
            True,
        )
    chapters: list[ReportPreferredLensChapter] = []
    messages: list[str] = []
    hard_rejected = False
    for chapter in plan.chapters:
        if chapter.chapter_id not in range(8):
            messages.append(f"preferred_lens chapter_id out of range: {chapter.chapter_id}")
            hard_rejected = True
            continue
        chapters.append(
            ReportPreferredLensChapter(
                chapter_id=f"chapter_{chapter.chapter_id}",  # type: ignore[arg-type]
                lens_key=chapter.lens_key,
                used_default=chapter.used_default,
                primary_focus=chapter.primary_focus,
                watch_variable_label=chapter.watch_variable_label,
                risk_focus_label=chapter.risk_focus_label,
                source_statements=chapter.source_statements,
            )
        )
    return (
        ReportPreferredLensProjection(fund_type=classified_fund_type, chapters=tuple(chapters)),
        tuple(messages),
        hard_rejected,
    )


def _get_extracted_field(bundle: StructuredFundDataBundle, attribute: str) -> ExtractedField[object]:
    """读取结构化数据包中的抽取字段。

    Args:
        bundle: 结构化基金数据包。
        attribute: 字段名。

    Returns:
        抽取字段。

    Raises:
        AttributeError: 当结构化包缺少计划字段时抛出。
    """

    return getattr(bundle, attribute)


def _project_evidence_anchors(
    *,
    anchor_inputs: tuple[tuple[_FieldSpec | str, EvidenceAnchor], ...],
    fund_code: str,
    report_year: int,
    document_id: str,
) -> tuple[dict[tuple[str, int | None, str | None, str], str], tuple[ReportEvidenceAnchor, ...], tuple[str, ...]]:
    """投影并去重证据锚点。

    Args:
        anchor_inputs: 字段与 extractor 锚点列表。
        fund_code: 基金代码。
        report_year: 年报年份。
        document_id: 年报文档标识。

    Returns:
        `(归一化 key 到 anchor_id, 锚点列表, 校验消息)`。

    Raises:
        无显式抛出。
    """

    del report_year
    projections_by_key: dict[tuple[str, int | None, str | None, str], _AnchorProjection] = {}
    ordered_keys: list[tuple[str, int | None, str | None, str]] = []
    for _, anchor in anchor_inputs:
        projection = _normalize_anchor_projection(
            fund_code=fund_code,
            document_id=document_id,
            anchor=anchor,
        )
        if projection.key in projections_by_key:
            continue
        projections_by_key[projection.key] = projection
        ordered_keys.append(projection.key)

    id_by_key: dict[tuple[str, int | None, str | None, str], str] = {}
    messages: list[str] = []
    grouped: dict[str, list[_AnchorProjection]] = defaultdict(list)
    for projection in projections_by_key.values():
        locator_hash = _short_locator_hash(projection.locator_json)
        grouped[f"{projection.prefix}:{locator_hash}"].append(projection)
    for base_id, projections in grouped.items():
        ordered = sorted(projections, key=lambda item: item.locator_json)
        for index, projection in enumerate(ordered, start=1):
            anchor_id = base_id if index == 1 else f"{base_id}-{index}"
            if index > 1:
                messages.append(f"anchor hash collision suffix applied: {anchor_id}")
            id_by_key[projection.key] = anchor_id

    evidence_anchors = tuple(
        replace(projections_by_key[key].anchor, anchor_id=id_by_key[key]) for key in ordered_keys
    )
    return id_by_key, evidence_anchors, tuple(messages)


def _normalize_anchor_projection(
    *,
    fund_code: str,
    document_id: str,
    anchor: EvidenceAnchor,
) -> _AnchorProjection:
    """归一化单个 extractor 锚点。

    Args:
        fund_code: 基金代码。
        document_id: 年报文档标识。
        anchor: extractor 锚点。

    Returns:
        内部锚点投影。

    Raises:
        无显式抛出。
    """

    source_kind, source_strength = _map_anchor_source(anchor.source_kind)
    section_or_source = _sanitize_anchor_section(anchor.section_id or anchor.source_kind)
    prefix = f"anchor:{fund_code}:{anchor.document_year}:{source_kind}:{section_or_source}"
    locator_json = _normalized_locator_json(
        page_number=anchor.page_number,
        table_id=anchor.table_id,
        row_locator=anchor.row_locator,
        note=anchor.note,
        review_artifact_ref=None,
    )
    key = (source_kind, anchor.document_year, anchor.section_id, locator_json)
    return _AnchorProjection(
        key=key,
        prefix=prefix,
        locator_json=locator_json,
        anchor=ReportEvidenceAnchor(
            anchor_id="",
            source_kind=source_kind,
            source_strength=source_strength,
            document_id=document_id if source_kind == "annual_report" else None,
            document_year=anchor.document_year,
            section_id=anchor.section_id,
            page_number=anchor.page_number,
            table_id=anchor.table_id,
            row_locator=anchor.row_locator,
            note=anchor.note,
        ),
    )


def _map_anchor_source(source_kind: str) -> tuple[ReportAnchorSourceKind, SourceStrength]:
    """映射 extractor 锚点来源到报告锚点域。

    Args:
        source_kind: extractor 来源类型。

    Returns:
        `(报告来源类型, 来源强度)`。

    Raises:
        无显式抛出。
    """

    if source_kind == "annual_report":
        return "annual_report", "fund_disclosure"
    if source_kind == "external_api":
        return "external_api", "third_party_reference"
    return "derived", "derived"


def _project_extracted_field_fact(
    *,
    bundle: StructuredFundDataBundle,
    context: ReportEvidenceProjectionContext,
    spec: _FieldSpec,
    extracted_field: ExtractedField[object],
    document_id: str,
    anchor_id_by_key: Mapping[tuple[str, int | None, str | None, str], str],
) -> tuple[ReportFact, tuple[ReportDataGap, ...], tuple[str, ...], bool]:
    """把单个 `ExtractedField` 投影为报告事实。

    Args:
        bundle: 结构化基金数据包。
        context: 投影上下文。
        spec: 字段投影配置。
        extracted_field: 抽取字段。
        document_id: 年报文档标识。
        anchor_id_by_key: 锚点 key 到 id 的映射。

    Returns:
        `(事实, 数据缺口, 校验消息, 是否硬拒绝)`。

    Raises:
        无显式抛出。
    """

    extraction_mode = _coerce_extraction_mode(extracted_field.extraction_mode)
    anchor_ids = _anchor_ids_for_field(extracted_field.anchors, anchor_id_by_key)
    fact_id = _build_fact_id(spec.category, spec.field_path)
    gaps: list[ReportDataGap] = []
    messages: list[str] = []
    hard_rejected = False
    failure_category: GapFailureCategory | None = None
    unit = spec.unit
    value = _to_report_value(extracted_field.value)

    if extraction_mode == "missing" and extracted_field.value is None:
        gap = _build_simple_gap(
            bundle=bundle,
            context=context,
            gap_kind="missing_fact",
            field_path=spec.field_path,
            failure_category="manual_review_required",
            reason_code="missing_from_extractor",
            wording=extracted_field.note or _DEFAULT_MISSING_WORDING,
            related_fact_id=fact_id,
            chapter_ids=("report_level",),
        )
        gaps.append(gap)
        failure_category = gap.failure_category
    elif extraction_mode == "missing" and extracted_field.value is not None:
        message = f"{spec.field_path} extraction_mode=missing but value is not None"
        messages.append(message)
        hard_rejected = True
        gap = _build_simple_gap(
            bundle=bundle,
            context=context,
            gap_kind="manual_review_required",
            field_path=spec.field_path,
            failure_category="ambiguous",
            reason_code="manual_review_required",
            wording=message,
            related_fact_id=fact_id,
            chapter_ids=("report_level",),
        )
        gaps.append(gap)
        failure_category = gap.failure_category
    elif extraction_mode in {"direct", "derived", "estimated"} and extracted_field.value is None:
        gap = _build_simple_gap(
            bundle=bundle,
            context=context,
            gap_kind="manual_review_required",
            field_path=spec.field_path,
            failure_category="ambiguous",
            reason_code="manual_review_required",
            wording=_DEFAULT_MISSING_WORDING,
            related_fact_id=fact_id,
            chapter_ids=("report_level",),
        )
        gaps.append(gap)
        failure_category = gap.failure_category
    elif extraction_mode in {"direct", "derived", "estimated"} and not anchor_ids:
        gap = _build_simple_gap(
            bundle=bundle,
            context=context,
            gap_kind="manual_review_required",
            field_path=spec.field_path,
            failure_category="manual_review_required",
            reason_code="manual_review_required",
            wording=_TRACEABILITY_WORDING,
            related_fact_id=fact_id,
            chapter_ids=("report_level",),
            blocks_scoring_dimensions=("evidence_traceability",),
        )
        gaps.append(gap)
        failure_category = gap.failure_category
    elif extraction_mode == "not_applicable":
        unit = "not_applicable"
        if extracted_field.value is not None:
            messages.append(f"{spec.field_path} not_applicable fact must not carry value")
            hard_rejected = True

    source_document_ids = (document_id,) if anchor_ids or spec.field_path == "basic_identity" else ()
    fact = ReportFact(
        fact_id=fact_id,
        category=spec.category,
        field_path=spec.field_path,
        value=value,
        unit=unit,
        source_anchor_ids=anchor_ids,
        source_document_ids=source_document_ids,
        source_boundary=context.source_boundary,
        extraction_mode=extraction_mode,
        review_status=context.fact_review_status,
        failure_category=failure_category,
    )
    return fact, tuple(gaps), tuple(messages), hard_rejected


def _project_classified_fund_type_fact(
    *,
    bundle: StructuredFundDataBundle,
    context: ReportEvidenceProjectionContext,
    classified_fund_type: ClassifiedFundType,
    document_id: str,
    anchor_id_by_key: Mapping[tuple[str, int | None, str | None, str], str],
) -> tuple[ReportFact, tuple[ReportDataGap, ...]]:
    """投影虚拟 `classified_fund_type` 事实。

    Args:
        bundle: 结构化基金数据包。
        context: 投影上下文。
        classified_fund_type: 已分类基金类型。
        document_id: 年报文档标识。
        anchor_id_by_key: 锚点 key 到 id 的映射。

    Returns:
        `(虚拟事实, 数据缺口)`。

    Raises:
        无显式抛出。
    """

    anchor_ids = _anchor_ids_for_field(bundle.basic_identity.anchors, anchor_id_by_key)
    gaps: tuple[ReportDataGap, ...] = ()
    failure_category: GapFailureCategory | None = None
    if classified_fund_type == "unknown":
        gap = _build_simple_gap(
            bundle=bundle,
            context=context,
            gap_kind="missing_fact",
            field_path="classified_fund_type",
            failure_category="classified_fund_type_missing",
            reason_code="classified_fund_type_missing",
            wording="缺少可用基金类型，不能应用基金类型优先分析规则",
            related_fact_id="fact:fund_type.classified_fund_type",
            chapter_ids=("report_level",),
        )
        gaps = (gap,)
        failure_category = gap.failure_category
    return (
        ReportFact(
            fact_id="fact:fund_type.classified_fund_type",
            category="fund_type",
            field_path="classified_fund_type",
            value=classified_fund_type if classified_fund_type != "unknown" else None,
            unit="text",
            source_anchor_ids=anchor_ids,
            source_document_ids=(document_id,) if anchor_ids else (),
            source_boundary=context.source_boundary,
            extraction_mode="direct" if classified_fund_type != "unknown" else "missing",
            review_status=context.fact_review_status,
            failure_category=failure_category,
        ),
        gaps,
    )


def _coerce_extraction_mode(mode: str) -> ReportExtractionMode:
    """把抽取模式收敛到报告事实模式域。

    Args:
        mode: 原始抽取模式。

    Returns:
        报告抽取模式；未知模式进入 `manual_reviewed` 前必须由上游显式支持，
        当前保守标记为 `missing`。

    Raises:
        无显式抛出。
    """

    if mode in get_args(ReportExtractionMode):
        return mode  # type: ignore[return-value]
    return "missing"


def _anchor_ids_for_field(
    anchors: tuple[EvidenceAnchor, ...],
    anchor_id_by_key: Mapping[tuple[str, int | None, str | None, str], str],
) -> tuple[str, ...]:
    """读取字段全部锚点 id。

    Args:
        anchors: extractor 锚点。
        anchor_id_by_key: 归一化 key 到 id 的映射。

    Returns:
        保序去重后的锚点 id。

    Raises:
        无显式抛出。
    """

    ids: list[str] = []
    for anchor in anchors:
        locator_json = _normalized_locator_json(
            page_number=anchor.page_number,
            table_id=anchor.table_id,
            row_locator=anchor.row_locator,
            note=anchor.note,
            review_artifact_ref=None,
        )
        source_kind, _ = _map_anchor_source(anchor.source_kind)
        key = (source_kind, anchor.document_year, anchor.section_id, locator_json)
        anchor_id = anchor_id_by_key.get(key)
        if anchor_id is not None and anchor_id not in ids:
            ids.append(anchor_id)
    return tuple(ids)


def _build_fact_id(category: FactCategory, field_path: str) -> str:
    """构建事实标识。

    Args:
        category: 事实分类。
        field_path: 字段路径。

    Returns:
        事实标识。

    Raises:
        无显式抛出。
    """

    return f"fact:{category}.{field_path}"


def _build_simple_gap(
    *,
    bundle: StructuredFundDataBundle,
    context: ReportEvidenceProjectionContext,
    gap_kind: GapKind,
    field_path: str,
    failure_category: GapFailureCategory,
    reason_code: DataGapReasonCode,
    wording: str,
    chapter_ids: tuple[ChapterRef, ...],
    related_fact_id: str | None = None,
    related_claim_id: str | None = None,
    blocks_claim_ids: tuple[str, ...] = (),
    blocks_scoring_dimensions: tuple[ScoreDimension, ...] = (),
    score_issue_ids: tuple[str, ...] = (),
) -> ReportDataGap:
    """构建字段级数据缺口。

    Args:
        bundle: 结构化基金数据包。
        context: 投影上下文。
        gap_kind: 缺口类型。
        field_path: 字段路径。
        failure_category: 失败分类。
        reason_code: 原因码。
        wording: 报告用词约束。
        chapter_ids: 章节引用。
        related_fact_id: 关联事实 id。
        related_claim_id: 关联声明 id。
        blocks_claim_ids: 被阻断声明。
        blocks_scoring_dimensions: 被阻断评分维度。
        score_issue_ids: 关联评分 issue。

    Returns:
        数据缺口记录。

    Raises:
        ValueError: 章节引用非法时抛出。
    """

    _validate_chapter_refs(chapter_ids)
    return ReportDataGap(
        gap_id=build_gap_id(
            bundle.fund_code,
            bundle.report_year,
            gap_kind,
            field_path,
            reason_code,
        ),
        gap_kind=gap_kind,
        field_path=field_path,
        related_fact_id=related_fact_id,
        related_claim_id=related_claim_id,
        chapter_ids=chapter_ids,
        failure_category=failure_category,
        reason_code=reason_code,
        fallback_allowed=context.source_failure_category in _FALLBACK_ALLOWED_SOURCE_FAILURES,
        fallback_used=context.fallback_used,
        required_report_wording=wording,
        blocks_claim_ids=blocks_claim_ids,
        blocks_scoring_dimensions=blocks_scoring_dimensions,
        score_issue_ids=score_issue_ids,
    )


def _project_data_gap_overrides(
    *,
    bundle: StructuredFundDataBundle,
    context: ReportEvidenceProjectionContext,
) -> tuple[ReportDataGap, ...]:
    """投影显式数据缺口 override。

    Args:
        bundle: 结构化基金数据包。
        context: 投影上下文。

    Returns:
        数据缺口 tuple。

    Raises:
        ValueError: override 章节非法时抛出。
    """

    gaps: list[ReportDataGap] = []
    for override in context.data_gap_overrides:
        field_path = _normalize_override_field_path(override.field_path)
        _validate_chapter_refs(override.chapter_ids)
        gaps.append(
            ReportDataGap(
                gap_id=build_gap_id(
                    bundle.fund_code,
                    bundle.report_year,
                    override.gap_kind,
                    field_path,
                    override.reason_code,
                ),
                gap_kind=override.gap_kind,
                field_path=field_path,
                related_fact_id=_fact_id_for_override_field_path(field_path),
                related_claim_id=override.related_claim_id,
                chapter_ids=override.chapter_ids,
                failure_category=override.failure_category,
                reason_code=override.reason_code,
                fallback_allowed=context.source_failure_category in _FALLBACK_ALLOWED_SOURCE_FAILURES,
                fallback_used=context.fallback_used,
                required_report_wording=override.required_report_wording,
                blocks_claim_ids=override.blocks_claim_ids,
                blocks_scoring_dimensions=override.blocks_scoring_dimensions,
                score_issue_ids=override.score_issue_ids,
            )
        )
    return tuple(gaps)


def _normalize_override_field_path(field_path: str) -> str:
    """规范化 override 字段路径。

    Args:
        field_path: 原始字段路径。

    Returns:
        规范化字段路径。

    Raises:
        无显式抛出。
    """

    if field_path == "turnover_rate":
        return "manager.turnover_rate"
    return field_path


def _fact_id_for_override_field_path(field_path: str) -> str | None:
    """根据 override 字段路径推导关联 fact id。

    Args:
        field_path: override 字段路径。

    Returns:
        可推导时返回 fact id，否则返回 `None`。

    Raises:
        无显式抛出。
    """

    if field_path == "manager.turnover_rate":
        return "fact:manager.turnover_rate"
    if "." not in field_path:
        for spec in _FIELD_SPECS:
            if spec.field_path == field_path:
                return _build_fact_id(spec.category, spec.field_path)
    return None


def _deduplicate_gaps(gaps: tuple[ReportDataGap, ...]) -> list[ReportDataGap]:
    """按 gap id 去重数据缺口，并合并同一缺口的反向引用。

    Args:
        gaps: 数据缺口。

    Returns:
        保序去重后的数据缺口列表；同一 `gap_id` 重复出现时，保留首条
        缺口的业务描述，并补齐首条缺失而后续缺口携带的关联标识。

    Raises:
        无显式抛出。
    """

    index_by_gap_id: dict[str, int] = {}
    result: list[ReportDataGap] = []
    for gap in gaps:
        existing_index = index_by_gap_id.get(gap.gap_id)
        if existing_index is not None:
            result[existing_index] = _merge_duplicate_gap_references(result[existing_index], gap)
            continue
        index_by_gap_id[gap.gap_id] = len(result)
        result.append(gap)
    return result


def _merge_duplicate_gap_references(
    existing_gap: ReportDataGap,
    incoming_gap: ReportDataGap,
) -> ReportDataGap:
    """合并同一数据缺口重复投影时携带的反向引用。

    Args:
        existing_gap: 保序去重中已经保留的数据缺口。
        incoming_gap: 后续遇到的同 `gap_id` 数据缺口。

    Returns:
        合并关联标识后的数据缺口。

    Raises:
        无显式抛出。
    """

    related_fact_id = existing_gap.related_fact_id or incoming_gap.related_fact_id
    related_claim_id = existing_gap.related_claim_id or incoming_gap.related_claim_id
    if (
        related_fact_id != existing_gap.related_fact_id
        or related_claim_id != existing_gap.related_claim_id
    ):
        return replace(
            existing_gap,
            related_fact_id=related_fact_id,
            related_claim_id=related_claim_id,
        )
    return existing_gap


def _attach_gap_refs_to_facts(
    facts: tuple[ReportFact, ...],
    data_gaps: tuple[ReportDataGap, ...],
) -> list[ReportFact]:
    """把同字段数据缺口引用回填到事实。

    Args:
        facts: 报告事实。
        data_gaps: 数据缺口。

    Returns:
        回填后的事实列表。

    Raises:
        无显式抛出。
    """

    result: list[ReportFact] = []
    for fact in facts:
        gap_ids = [
            gap.gap_id
            for gap in data_gaps
            if _gap_matches_fact(gap=gap, fact=fact)
        ]
        result.append(replace(fact, data_gap_refs=_dedupe((*fact.data_gap_refs, *gap_ids))))
    return result


def _gap_matches_fact(*, gap: ReportDataGap, fact: ReportFact) -> bool:
    """判断数据缺口是否关联某个事实。

    Args:
        gap: 数据缺口。
        fact: 报告事实。

    Returns:
        关联返回 `True`，否则返回 `False`。

    Raises:
        无显式抛出。
    """

    if gap.related_fact_id == fact.fact_id:
        return True
    if gap.field_path == fact.field_path:
        return True
    return bool(gap.field_path and gap.field_path.endswith(f".{fact.field_path}"))


def _attach_score_issue_refs_to_facts(
    facts: tuple[ReportFact, ...],
    score_issue_links: tuple[ReportScoreIssueLink, ...],
) -> list[ReportFact]:
    """把评分 issue 引用回填到事实。

    Args:
        facts: 报告事实。
        score_issue_links: 评分 issue 链接。

    Returns:
        回填后的事实列表。

    Raises:
        无显式抛出。
    """

    result: list[ReportFact] = []
    for fact in facts:
        issue_ids = [
            issue.issue_id
            for issue in score_issue_links
            if issue.field_path == fact.field_path or issue.field_path == _qualified_fact_field_path(fact)
        ]
        result.append(replace(fact, score_issue_ids=_dedupe((*fact.score_issue_ids, *issue_ids))))
    return result


def _attach_score_issue_refs_to_gaps(
    data_gaps: tuple[ReportDataGap, ...],
    score_issue_links: tuple[ReportScoreIssueLink, ...],
) -> list[ReportDataGap]:
    """把评分 issue 引用回填到数据缺口。

    Args:
        data_gaps: 数据缺口。
        score_issue_links: 评分 issue 链接。

    Returns:
        回填后的数据缺口列表。

    Raises:
        无显式抛出。
    """

    result: list[ReportDataGap] = []
    for gap in data_gaps:
        issue_ids = [issue.issue_id for issue in score_issue_links if gap.gap_id in issue.data_gap_refs]
        result.append(replace(gap, score_issue_ids=_dedupe((*gap.score_issue_ids, *issue_ids))))
    return result


def _qualified_fact_field_path(fact: ReportFact) -> str:
    """返回事实的 category-qualified 字段路径。

    Args:
        fact: 报告事实。

    Returns:
        带分类前缀的字段路径。

    Raises:
        无显式抛出。
    """

    return f"{fact.category}.{fact.field_path}"


def _validate_score_issue_links(
    *,
    score_issue_links: tuple[ReportScoreIssueLink, ...],
    data_gaps: tuple[ReportDataGap, ...],
    evidence_anchors: tuple[ReportEvidenceAnchor, ...],
) -> tuple[tuple[str, ...], bool]:
    """校验评分 issue 链接。

    Args:
        score_issue_links: 评分 issue 链接。
        data_gaps: 数据缺口。
        evidence_anchors: 证据锚点。

    Returns:
        `(校验消息, 是否硬拒绝)`。

    Raises:
        无显式抛出。
    """

    messages: list[str] = []
    gap_ids = {gap.gap_id for gap in data_gaps}
    anchor_ids = {anchor.anchor_id for anchor in evidence_anchors}
    blocking_gap_ids = {gap.gap_id for gap in data_gaps if _is_blocking_gap(gap)}
    for issue in score_issue_links:
        if issue.data_gap_refs:
            missing_gap_refs = tuple(ref for ref in issue.data_gap_refs if ref not in gap_ids)
            if missing_gap_refs:
                messages.append(f"score issue {issue.issue_id} references missing gaps: {missing_gap_refs}")
        missing_anchor_refs = tuple(
            ref for ref in issue.evidence_anchor_refs if ref.startswith("anchor:") and ref not in anchor_ids
        )
        if missing_anchor_refs:
            messages.append(f"score issue {issue.issue_id} references missing anchors: {missing_anchor_refs}")
        if issue.status in {"issue", "blocked"} and issue.severity is None:
            messages.append(f"score issue {issue.issue_id} requires severity")
        if issue.status == "pass" and any(ref in blocking_gap_ids for ref in issue.data_gap_refs):
            messages.append(f"score issue {issue.issue_id} pass status conflicts with blocking gap")
        if issue.status == "N/A" and not (issue.na_reason or issue.reviewer_note):
            messages.append(f"score issue {issue.issue_id} N/A requires na_reason or reviewer_note")
        if issue.dimension == "chapter_summary" and issue.status != "skipped":
            messages.append(f"score issue {issue.issue_id} chapter_summary requires skipped status")
        if issue.status == "skipped" and issue.dimension != "chapter_summary":
            messages.append(f"score issue {issue.issue_id} skipped is only valid for chapter_summary")
    return tuple(messages), bool(messages)


def _merge_quality_context(
    quality_context: ReportQualityContext,
    issue_ids: tuple[str, ...],
) -> ReportQualityContext:
    """合并质量上下文中的评分引用。

    Args:
        quality_context: 原始质量上下文。
        issue_ids: 当前 bundle 中的 issue id。

    Returns:
        合并后的质量上下文。

    Raises:
        无显式抛出。
    """

    return replace(
        quality_context,
        report_quality_score_refs=_dedupe((*quality_context.report_quality_score_refs, *issue_ids)),
    )


def _has_rejected_condition(
    *,
    context: ReportEvidenceProjectionContext,
    hard_rejected: bool,
) -> bool:
    """判断是否存在 rejected 条件。

    Args:
        context: 投影上下文。
        hard_rejected: 是否已有硬拒绝校验结果。

    Returns:
        需要 rejected 返回 `True`。

    Raises:
        无显式抛出。
    """

    return (
        hard_rejected
        or context.document_identity_status == "mismatch"
        or context.source_failure_category in _FAIL_CLOSED_SOURCE_FAILURES
    )


def _has_deferred_condition(
    *,
    context: ReportEvidenceProjectionContext,
    classified_fund_type: ClassifiedFundType,
    type_slot_membership_status: TypeSlotMembershipStatus,
    data_gaps: tuple[ReportDataGap, ...],
) -> bool:
    """判断是否存在 deferred 条件。

    Args:
        context: 投影上下文。
        classified_fund_type: 已分类基金类型。
        type_slot_membership_status: 类型 slot 状态。
        data_gaps: 数据缺口。

    Returns:
        需要 deferred 返回 `True`。

    Raises:
        无显式抛出。
    """

    if context.source_failure_category == "unknown_upstream_failure_category":
        return True
    if classified_fund_type == "unknown":
        return True
    if context.fund_type_slot is not None and type_slot_membership_status in {
        "type_gap",
        "taxonomy_pending",
        "unknown",
    }:
        return True
    if context.source_boundary in {"unknown", "probe_only"}:
        return True
    if any(_is_blocking_gap(gap) for gap in data_gaps):
        return True
    if context.fact_review_status == "partially_reviewed":
        return True
    return (
        context.quality_context.fq_gate_status == "block"
        or context.quality_context.programmatic_audit_status == "block"
    )


def _is_scoring_ready(
    *,
    context: ReportEvidenceProjectionContext,
    classified_fund_type: ClassifiedFundType,
    type_slot_membership_status: TypeSlotMembershipStatus,
    preferred_lens: ReportPreferredLensProjection,
    data_gaps: tuple[ReportDataGap, ...],
    score_issue_links: tuple[ReportScoreIssueLink, ...],
) -> bool:
    """判断是否满足 scoring_ready。

    Args:
        context: 投影上下文。
        classified_fund_type: 已分类基金类型。
        type_slot_membership_status: 类型 slot 状态。
        preferred_lens: preferred_lens 投影。
        data_gaps: 数据缺口。
        score_issue_links: 评分 issue 链接。

    Returns:
        满足 scoring_ready 返回 `True`。

    Raises:
        无显式抛出。
    """

    lens_chapters = tuple(chapter.chapter_id for chapter in preferred_lens.chapters)
    return (
        context.corpus_id != "ad_hoc"
        and context.document_identity_status == "verified_annual_report"
        and context.source_boundary not in {"unknown", "probe_only"}
        and context.source_failure_category == "none"
        and classified_fund_type != "unknown"
        and type_slot_membership_status == "matches_slot"
        and context.fact_review_status == "reviewed"
        and lens_chapters == _SCORING_READY_CHAPTER_REFS
        and not any(_is_blocking_gap(gap) for gap in data_gaps)
        and not any(issue.severity == "blocking" for issue in score_issue_links)
    )


def _is_blocking_gap(gap: ReportDataGap) -> bool:
    """判断数据缺口是否阻断评分。

    Args:
        gap: 数据缺口。

    Returns:
        阻断返回 `True`。

    Raises:
        无显式抛出。
    """

    return gap.gap_kind != "not_applicable" and gap.failure_category != "not_applicable"


def _validate_chapter_refs(chapter_ids: tuple[ChapterRef, ...]) -> None:
    """校验章节引用。

    Args:
        chapter_ids: 章节引用。

    Returns:
        无返回值。

    Raises:
        ValueError: 章节引用为空或非法时抛出。
    """

    if not chapter_ids:
        raise ValueError("chapter_ids 不能为空")
    invalid = tuple(chapter_id for chapter_id in chapter_ids if chapter_id not in _VALID_CHAPTER_REFS)
    if invalid:
        raise ValueError(f"chapter_ids 包含非法值：{invalid}")


def _to_report_value(value: object) -> object | None:
    """把抽取值转换为报告证据包可稳定比较的值。

    Args:
        value: 原始抽取值。

    Returns:
        JSON-like 值或 `None`。

    Raises:
        无显式抛出。
    """

    if value is None:
        return None
    if isinstance(value, Decimal):
        return str(value)
    if is_dataclass(value) and not isinstance(value, type):
        return _to_report_value(asdict(value))
    if isinstance(value, Mapping):
        return {str(key): _to_report_value(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return tuple(_to_report_value(item) for item in value)
    if isinstance(value, list):
        return [_to_report_value(item) for item in value]
    return value


def _normalized_locator_json(
    *,
    page_number: int | None,
    table_id: str | None,
    row_locator: str | None,
    note: str | None,
    review_artifact_ref: str | None,
) -> str:
    """构建归一化 locator JSON。

    Args:
        page_number: 页码。
        table_id: 表格标识。
        row_locator: 行级定位。
        note: 说明。
        review_artifact_ref: 审阅 artifact 引用。

    Returns:
        排序后的稳定 JSON 字符串。

    Raises:
        无显式抛出。
    """

    locator = {
        "page_number": page_number if isinstance(page_number, int) else "",
        "table_id": _normalize_text(table_id),
        "row_locator": _normalize_text(row_locator),
        "note": _normalize_text(note),
        "review_artifact_ref": _normalize_text(review_artifact_ref),
    }
    return json.dumps(locator, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _short_locator_hash(locator_json: str) -> str:
    """计算 locator 短哈希。

    Args:
        locator_json: 归一化 locator JSON。

    Returns:
        `sha256` 前 8 位十六进制小写字符串。

    Raises:
        无显式抛出。
    """

    return hashlib.sha256(locator_json.encode("utf-8")).hexdigest()[:8]


def _sanitize_anchor_section(section_or_source: str | None) -> str:
    """清洗锚点 id 中的章节或来源片段。

    Args:
        section_or_source: 原始章节或来源。

    Returns:
        可用于 id 的片段。

    Raises:
        无显式抛出。
    """

    value = unicodedata.normalize("NFC", section_or_source or "").strip()
    if value.startswith("§"):
        value = f"sec{value[1:]}"
    value = "".join(character.lower() if "A" <= character <= "Z" else character for character in value)
    value = _WHITESPACE_PATTERN.sub("_", value)
    value = _SECTION_SANITIZE_PATTERN.sub("_", value)
    value = re.sub(r"_+", "_", value).strip("_")
    return value or "unknown"


def _normalize_text(value: object | None) -> str:
    """归一化文本值。

    Args:
        value: 原始值。

    Returns:
        NFC、去首尾空白、内部 ASCII 空白折叠后的字符串。

    Raises:
        无显式抛出。
    """

    if value is None:
        return ""
    normalized = unicodedata.normalize("NFC", str(value).strip())
    return _WHITESPACE_PATTERN.sub(" ", normalized)


def _dedupe(values: tuple[str, ...]) -> tuple[str, ...]:
    """保序去重字符串 tuple。

    Args:
        values: 原始字符串。

    Returns:
        去重后的 tuple。

    Raises:
        无显式抛出。
    """

    result: list[str] = []
    for value in values:
        if value not in result:
            result.append(value)
    return tuple(result)
