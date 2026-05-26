"""报告写作 dev-only 语义审计。

本模块属于 Agent 层 Fund 领域能力，只消费调用方显式传入的
`ReportEvidenceBundle`、已解析 records 或 `ChapterDraftSurrogate`。它不读取
基金原始披露文件、不触发来源编排、不调用生产抽取器或产品输出链路，也不接入
产品质量门。写作审计 failure category
刻意独立于 `report_evidence.GapFailureCategory`：前者描述报告措辞与证据支撑的
问题，后者描述事实投影阶段的数据缺口来源。
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Iterable, Mapping
from dataclasses import asdict, dataclass, is_dataclass
from typing import Literal

from fund_agent.fund.fund_type import FundType
from fund_agent.fund.report_evidence import (
    REPORT_EVIDENCE_SCHEMA_VERSION,
    ReportDataGap,
    ReportEvidenceAnchor,
    ReportEvidenceBundle,
    ReportFact,
    ReportPreferredLensProjection,
    ReportQualityContext,
)
from fund_agent.fund.template.chapter_contract_constraints import (
    ACTIVE_CHAPTER_3_TURNOVER_REQUIREMENT_ID,
    FailureCategory,
    TURNOVER_STYLE_GAP_REASON_CODES,
    TURNOVER_STYLE_REQUIRED_WORDING_FRAGMENTS,
    EvidenceRequirement,
    constraints_for_chapter,
    map_requirement_severity_to_issue_severity,
)

REPORT_WRITING_AUDIT_SCHEMA_VERSION = "report_writing_audit.v0"
AuditIssueSeverity = Literal["blocking", "material", "minor", "informational"]
DraftFundTypeSlot = FundType | Literal["default", "unknown"]
_STABILITY_CLAIM_TAGS = frozenset(
    (
        "stability_positive",
        "style_consistency_positive",
        "words_actions_consistent_positive",
    )
)
_STABILITY_PHRASES = (
    "风格稳定",
    "风格保持稳定",
    "风格一致",
    "风格延续",
    "言行一致",
    "投资框架稳定",
)
_NEGATED_STABILITY_PREFIXES = (
    "不判断",
    "不能判断",
    "无法判断",
    "不足以判断",
    "不能据此判断",
)
_QUESTIONING_STABILITY_SUFFIXES = ("是否", "能否")
_QUESTIONING_STABILITY_PREFIXES = ("下一步最小验证问题", "复核", "验证", "确认")
_INSUFFICIENT_WORDING = "证据不足"
_TRADING_ADVICE_PHRASES = (
    "建议买入",
    "可以买入",
    "立即买入",
    "建议卖出",
    "应该卖出",
    "清仓",
    "加仓",
    "减仓",
    "仓位比例",
)
_TURNOVER_STYLE_GAP_FIELD_PATHS = frozenset(
    ("turnover_rate", "manager.turnover_rate", "style_change_proxy")
)


@dataclass(frozen=True, slots=True)
class ChapterDraftSurrogate:
    """dev-only 章节草稿代理。

    Attributes:
        chapter_id: 模板章节编号，见模板第 0-7 章。
        fund_type_slot: 草稿显式基金类型 slot；`unknown` 会回退到 bundle/default。
        markdown: 调用方提供的章节 Markdown 或片段。
        claim_tags: 调用方显式声明的 claim 标签，优先于短语匹配。
        gap_refs: 草稿显式引用的数据缺口 id。
        anchor_refs: 草稿显式引用的证据锚点 id。
    """

    chapter_id: int
    fund_type_slot: DraftFundTypeSlot
    markdown: str
    claim_tags: tuple[str, ...] = ()
    gap_refs: tuple[str, ...] = ()
    anchor_refs: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class ReportWritingAuditIssue:
    """报告写作审计 issue。

    Attributes:
        issue_id: 稳定确定性 issue id。
        chapter_id: 章节编号；报告级问题为 `None`。
        fund_type_slot: 适用基金类型 slot。
        severity: issue 严重程度。
        failure_category: 写作审计失败分类。
        requirement_id: 关联证据要求 id；非 requirement 问题为 `None`。
        message: 面向开发者的中文问题说明。
        evidence_requirement_gaps: 未满足的证据要求 id。
        anchor_refs: 相关锚点引用。
        data_gap_refs: 相关数据缺口引用。
    """

    issue_id: str
    chapter_id: int | None
    fund_type_slot: str
    severity: AuditIssueSeverity
    failure_category: FailureCategory
    requirement_id: str | None
    message: str
    evidence_requirement_gaps: tuple[str, ...] = ()
    anchor_refs: tuple[str, ...] = ()
    data_gap_refs: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class ReportWritingAuditSummary:
    """报告写作审计汇总。

    Attributes:
        issue_count: issue 总数。
        blocking_count: blocking issue 数。
        material_count: material issue 数。
        minor_count: minor issue 数。
        informational_count: informational issue 数。
        failure_category_counts: 按失败分类排序后的计数。
        evidence_requirement_gap_count: 未满足证据要求计数。
    """

    issue_count: int
    blocking_count: int
    material_count: int
    minor_count: int
    informational_count: int
    failure_category_counts: tuple[tuple[str, int], ...]
    evidence_requirement_gap_count: int


@dataclass(frozen=True, slots=True)
class ReportWritingAuditResult:
    """报告写作审计结果。

    Attributes:
        schema_version: 审计结果 schema 版本。
        issues: 确定性排序后的 issue 列表。
        summary: issue 汇总。
        failed_closed: 当前 dev-only 审计是否因输入矛盾 fail closed。
    """

    schema_version: str
    issues: tuple[ReportWritingAuditIssue, ...]
    summary: ReportWritingAuditSummary
    failed_closed: bool


def audit_report_writing_bundle(
    bundle: ReportEvidenceBundle,
    *,
    chapter_drafts: tuple[ChapterDraftSurrogate, ...] = (),
) -> ReportWritingAuditResult:
    """审计单个报告证据包和可选章节草稿。

    Args:
        bundle: 调用方显式传入的报告证据包。
        chapter_drafts: 调用方显式传入的 dev-only 章节草稿代理。

    Returns:
        确定性的写作审计结果。

    Raises:
        无显式抛出；输入缺口以 issue 表达，不调用外部运行时。
    """

    fund_type_slot = _resolve_bundle_fund_type_slot(bundle)
    issues = []
    drafts_by_chapter = _group_drafts_by_chapter(chapter_drafts)
    active_chapter_3_slot, input_issues = _resolve_chapter_fund_type_slot(
        chapter_drafts=drafts_by_chapter.get(3, ()),
        bundle_fund_type_slot=fund_type_slot,
    )
    issues.extend(input_issues)

    issues.extend(_audit_forbidden_content(chapter_drafts, fund_type_slot))
    if not input_issues:
        issues.extend(
            _audit_active_chapter_3_turnover_requirement(
                bundle=bundle,
                fund_type_slot=active_chapter_3_slot,
                chapter_drafts=drafts_by_chapter.get(3, ()),
            )
        )

    result_issues = tuple(sorted(issues, key=lambda issue: issue.issue_id))
    return ReportWritingAuditResult(
        schema_version=REPORT_WRITING_AUDIT_SCHEMA_VERSION,
        issues=result_issues,
        summary=_summarize_issues(result_issues),
        failed_closed=any(issue.severity == "blocking" for issue in input_issues),
    )


def audit_report_writing_records(
    records: Iterable[Mapping[str, object]],
    *,
    chapter_drafts: tuple[ChapterDraftSurrogate, ...] = (),
) -> ReportWritingAuditResult:
    """审计调用方已解析的 JSONL-like records。

    Args:
        records: 调用方已解析的 mapping 记录；本 helper 只提取 bundle-like 字段，
            不读取文件，也不做完整 schema 校验。
        chapter_drafts: 调用方显式传入的 dev-only 章节草稿代理。

    Returns:
        写作审计结果；没有 bundle-like 记录时返回一个 blocking issue。

    Raises:
        无显式抛出；record 缺失或不支持时以 issue 表达。
    """

    bundle_record = _first_bundle_record(records)
    if bundle_record is None:
        issue = ReportWritingAuditIssue(
            issue_id="rwa:report:bundle_missing",
            chapter_id=None,
            fund_type_slot="default",
            severity="blocking",
            failure_category="required_evidence_missing",
            requirement_id=None,
            message="写作审计 records 未包含 bundle-like 记录，无法检查证据支撑。",
        )
        return ReportWritingAuditResult(
            schema_version=REPORT_WRITING_AUDIT_SCHEMA_VERSION,
            issues=(issue,),
            summary=_summarize_issues((issue,)),
            failed_closed=True,
        )
    bundle, input_issues = _bundle_from_record(bundle_record)
    if input_issues:
        result_issues = tuple(sorted(input_issues, key=lambda issue: issue.issue_id))
        return ReportWritingAuditResult(
            schema_version=REPORT_WRITING_AUDIT_SCHEMA_VERSION,
            issues=result_issues,
            summary=_summarize_issues(result_issues),
            failed_closed=True,
        )
    return audit_report_writing_bundle(
        bundle,
        chapter_drafts=chapter_drafts,
    )


def _audit_forbidden_content(
    chapter_drafts: tuple[ChapterDraftSurrogate, ...],
    bundle_fund_type_slot: FundType | Literal["default"],
) -> list[ReportWritingAuditIssue]:
    """检查 must_not_cover 与交易建议禁区。

    Args:
        chapter_drafts: 章节草稿代理。
        bundle_fund_type_slot: bundle 推导出的基金类型 slot。

    Returns:
        forbidden_content issue 列表。

    Raises:
        无显式抛出。
    """

    issues: list[ReportWritingAuditIssue] = []
    for draft in chapter_drafts:
        resolved_slot = _resolve_draft_fund_type_slot(draft, bundle_fund_type_slot)
        if _contains_trading_advice(draft.markdown):
            issues.append(
                _build_issue(
                    chapter_id=draft.chapter_id,
                    fund_type_slot=resolved_slot,
                    severity="blocking",
                    failure_category="forbidden_content",
                    requirement_id=None,
                    message="报告草稿包含买入、卖出或仓位比例等直接交易建议。",
                    anchor_refs=draft.anchor_refs,
                    data_gap_refs=draft.gap_refs,
                )
            )
        issues.extend(_must_not_cover_issues(draft, resolved_slot))
    return issues


def _audit_active_chapter_3_turnover_requirement(
    *,
    bundle: ReportEvidenceBundle,
    fund_type_slot: FundType | Literal["default"],
    chapter_drafts: tuple[ChapterDraftSurrogate, ...],
) -> list[ReportWritingAuditIssue]:
    """审计主动基金第 3 章换手率/风格一致性证据约束。

    Args:
        bundle: 报告证据包。
        fund_type_slot: bundle 推导出的基金类型 slot。
        chapter_drafts: 第 3 章草稿代理。

    Returns:
        active_fund 第 3 章相关 issue 列表。

    Raises:
        无显式抛出。
    """

    if fund_type_slot != "active_fund":
        return []

    requirement = _active_chapter_3_requirement()
    if requirement.deferred:
        return [
            _build_requirement_issue(
                requirement=requirement,
                severity=map_requirement_severity_to_issue_severity(requirement.severity),
                failure_category="deferred_extraction_requirement",
                message="主动基金第 3 章证据要求被标记为 deferred。",
                anchor_refs=(),
                data_gap_refs=(),
            )
        ]

    satisfying_fact = _find_satisfying_fact(
        bundle.facts,
        bundle.evidence_anchors,
        requirement,
    )
    if satisfying_fact is not None:
        return []

    compatible_gap = _find_compatible_gap(bundle.data_gaps, requirement)
    stability_claim = any(_has_active_chapter_3_stability_claim(draft) for draft in chapter_drafts)
    issues: list[ReportWritingAuditIssue] = []

    if compatible_gap is None:
        issues.append(
            _build_requirement_issue(
                requirement=requirement,
                severity=map_requirement_severity_to_issue_severity(requirement.severity),
                failure_category="required_evidence_missing",
                message="主动基金第 3 章缺少已复核换手率、风格变化代理事实或兼容 data_gap。",
                anchor_refs=(),
                data_gap_refs=(),
            )
        )
        if stability_claim:
            issues.append(
                _build_requirement_issue(
                    requirement=requirement,
                    severity="material",
                    failure_category="unsupported_stability_claim",
                    message="草稿在缺少换手率/风格变化证据时输出了风格稳定、风格一致或言行一致正向判断。",
                    anchor_refs=(),
                    data_gap_refs=(),
                )
            )
        return issues

    if not _drafts_preserve_required_wording(chapter_drafts, compatible_gap):
        issues.append(
            _build_requirement_issue(
                requirement=requirement,
                severity="material",
                failure_category="insufficient_evidence_wording_missing",
                message="草稿使用兼容 data_gap 时未保留证据不足措辞和下一步最小验证问题。",
                anchor_refs=(),
                data_gap_refs=(compatible_gap.gap_id,),
            )
        )
    if stability_claim:
        issues.append(
            _build_requirement_issue(
                requirement=requirement,
                severity="material",
                failure_category="unsupported_stability_claim",
                message="草稿在仅有 data_gap 降级证据时输出了风格稳定、风格一致或言行一致正向判断。",
                anchor_refs=(),
                data_gap_refs=(compatible_gap.gap_id,),
            )
        )
    return issues


def _must_not_cover_issues(
    draft: ChapterDraftSurrogate,
    fund_type_slot: FundType | Literal["default"],
) -> list[ReportWritingAuditIssue]:
    """根据章节 sidecar must_not_cover 检查草稿。

    Args:
        draft: 章节草稿代理。
        fund_type_slot: 已解析基金类型 slot。

    Returns:
        forbidden_content issue 列表。

    Raises:
        无显式抛出。
    """

    issues: list[ReportWritingAuditIssue] = []
    constraints = constraints_for_chapter(draft.chapter_id, fund_type_slot)
    for constraint in constraints:
        for index, forbidden in enumerate(constraint.must_not_cover):
            if _forbidden_rule_hits(forbidden, draft.markdown):
                issues.append(
                    _build_issue(
                        chapter_id=draft.chapter_id,
                        fund_type_slot=fund_type_slot,
                        severity="material",
                        failure_category="forbidden_content",
                        requirement_id=None,
                        message=f"草稿触发 CHAPTER_CONTRACT must_not_cover：{forbidden}",
                        anchor_refs=draft.anchor_refs,
                        data_gap_refs=draft.gap_refs,
                        issue_key=f"must_not_cover:{index}",
                    )
                )
    return issues


def _first_bundle_record(records: Iterable[Mapping[str, object]]) -> Mapping[str, object] | None:
    """提取首个 bundle-like record。

    Args:
        records: 调用方已解析 records。

    Returns:
        首个 bundle-like mapping；不存在时返回 `None`。

    Raises:
        无显式抛出。
    """

    for record in records:
        record_type = record.get("record_type")
        if record_type in (None, "bundle") and "bundle_id" in record:
            return record
    return None


def _bundle_from_record(
    record: Mapping[str, object],
) -> tuple[ReportEvidenceBundle, tuple[ReportWritingAuditIssue, ...]]:
    """从最小 mapping 构造审计所需的 `ReportEvidenceBundle`。

    Args:
        record: bundle-like mapping。

    Returns:
        仅包含写作审计所需字段的 `ReportEvidenceBundle`，以及输入校验 issue。

    Raises:
        无显式抛出；缺失字段使用 dev-only 保守默认值。
    """

    input_issues: list[ReportWritingAuditIssue] = []
    facts = tuple(_fact_from_mapping(item) for item in _mapping_sequence(record.get("facts")))
    evidence_anchors = tuple(
        _anchor_from_mapping(item)
        for item in _mapping_sequence(record.get("evidence_anchors"))
    )
    data_gap_results = tuple(
        _gap_from_mapping(item, index=index)
        for index, item in enumerate(_mapping_sequence(record.get("data_gaps")))
    )
    data_gaps = tuple(gap for gap, issue in data_gap_results if issue is None)
    input_issues.extend(issue for _gap, issue in data_gap_results if issue is not None)
    classified = record.get("classified_fund_type")
    fund_type_slot = record.get("fund_type_slot")
    report_year, report_year_issue = _coerce_report_year(record.get("report_year"))
    if report_year_issue is not None:
        input_issues.append(report_year_issue)
    bundle = ReportEvidenceBundle(
        bundle_id=str(record.get("bundle_id", "bundle:unknown")),
        schema_version=str(record.get("schema_version", REPORT_EVIDENCE_SCHEMA_VERSION)),
        corpus_id=str(record.get("corpus_id", "ad_hoc")),
        fund_code=str(record.get("fund_code", "unknown")),
        report_year=report_year,
        classified_fund_type=_coerce_classified_fund_type(classified),
        type_slot_membership_status="unknown",
        fund_type_slot=_coerce_fund_type_or_none(fund_type_slot),
        preferred_lens=ReportPreferredLensProjection(
            fund_type=_coerce_classified_fund_type(classified),
            chapters=(),
        ),
        quality_context=ReportQualityContext(),
        review_status="candidate",
        facts=facts,
        evidence_anchors=evidence_anchors,
        data_gaps=data_gaps,
    )
    return bundle, tuple(input_issues)


def _fact_from_mapping(record: Mapping[str, object]) -> ReportFact:
    """从 mapping 构造最小报告事实。

    Args:
        record: fact-like mapping。

    Returns:
        `ReportFact`。

    Raises:
        无显式抛出。
    """

    return ReportFact(
        fact_id=str(record.get("fact_id", "")),
        category=str(record.get("category", "other")),  # type: ignore[arg-type]
        field_path=str(record.get("field_path", "")),
        value=record.get("value"),
        unit=str(record.get("unit", "unknown")),  # type: ignore[arg-type]
        source_boundary=str(record.get("source_boundary", "manual_review")),  # type: ignore[arg-type]
        extraction_mode=str(record.get("extraction_mode", "manual_reviewed")),  # type: ignore[arg-type]
        review_status=str(record.get("review_status", "not_reviewed")),  # type: ignore[arg-type]
        source_anchor_ids=tuple(str(item) for item in record.get("source_anchor_ids", ()) or ()),
    )


def _gap_from_mapping(
    record: Mapping[str, object],
    *,
    index: int,
) -> tuple[ReportDataGap | None, ReportWritingAuditIssue | None]:
    """从 mapping 构造最小数据缺口。

    Args:
        record: gap-like mapping。

    Returns:
        `ReportDataGap` 与可选输入校验 issue。

    Raises:
        无显式抛出。
    """

    reason_code = record.get("reason_code")
    field_path = _optional_str(record.get("field_path"))
    required_report_wording = str(record.get("required_report_wording", ""))
    if not isinstance(reason_code, str) or not _gap_has_required_explicit_fields(
        reason_code=reason_code,
        field_path=field_path,
        required_report_wording=required_report_wording,
    ):
        return None, _build_issue(
            chapter_id=None,
            fund_type_slot="default",
            severity="blocking",
            failure_category="invalid_audit_input",
            requirement_id=None,
            message="records data_gap 缺少显式 reason_code、相关 field_path 或降级措辞，不能用于满足第 3 章证据要求。",
            issue_key=f"data_gap:{index}:invalid",
        )
    return ReportDataGap(
        gap_id=str(record.get("gap_id", "")),
        gap_kind=str(record.get("gap_kind", "not_reviewed")),  # type: ignore[arg-type]
        chapter_ids=tuple(str(item) for item in record.get("chapter_ids", ()) or ()),  # type: ignore[arg-type]
        failure_category=str(record.get("failure_category", reason_code)),  # type: ignore[arg-type]
        reason_code=reason_code,  # type: ignore[arg-type]
        fallback_allowed=bool(record.get("fallback_allowed", False)),
        fallback_used=bool(record.get("fallback_used", False)),
        required_report_wording=required_report_wording,
        field_path=field_path,
        related_fact_id=_optional_str(record.get("related_fact_id")),
        related_claim_id=_optional_str(record.get("related_claim_id")),
    ), None


def _anchor_from_mapping(record: Mapping[str, object]) -> ReportEvidenceAnchor:
    """从 mapping 构造最小证据锚点。

    Args:
        record: anchor-like mapping。

    Returns:
        `ReportEvidenceAnchor`。

    Raises:
        无显式抛出。
    """

    document_year, _issue = _coerce_report_year(record.get("document_year"))
    return ReportEvidenceAnchor(
        anchor_id=str(record.get("anchor_id", "")),
        source_kind=str(record.get("source_kind", "annual_report")),  # type: ignore[arg-type]
        source_strength=str(record.get("source_strength", "fund_disclosure")),  # type: ignore[arg-type]
        document_id=_optional_str(record.get("document_id")),
        document_year=document_year or None,
        section_id=_optional_str(record.get("section_id")),
        page_number=_optional_int_or_none(record.get("page_number")),
        table_id=_optional_str(record.get("table_id")),
        row_locator=_optional_str(record.get("row_locator")),
        review_artifact_ref=_optional_str(record.get("review_artifact_ref")),
        note=_optional_str(record.get("note")),
    )


def _find_satisfying_fact(
    facts: tuple[ReportFact, ...],
    evidence_anchors: tuple[ReportEvidenceAnchor, ...],
    requirement: EvidenceRequirement,
) -> ReportFact | None:
    """查找满足证据要求的已复核事实。

    Args:
        facts: 报告事实列表。
        evidence_anchors: 报告证据锚点列表。
        requirement: 证据要求。

    Returns:
        满足要求的事实；不存在时返回 `None`。

    Raises:
        无显式抛出。
    """

    accepted_fact_ids = set(requirement.accepted_fact_ids)
    existing_anchor_ids = {anchor.anchor_id for anchor in evidence_anchors}
    for fact in facts:
        if fact.fact_id not in accepted_fact_ids:
            continue
        if fact.review_status != "reviewed":
            continue
        if fact.extraction_mode not in ("direct", "derived", "manual_reviewed"):
            continue
        if fact.value is None:
            continue
        fact_anchor_ids = set(fact.source_anchor_ids)
        if not fact_anchor_ids:
            continue
        if not fact_anchor_ids.issubset(existing_anchor_ids):
            continue
        return fact
    return None


def _find_compatible_gap(
    data_gaps: tuple[ReportDataGap, ...],
    requirement: EvidenceRequirement,
) -> ReportDataGap | None:
    """查找满足降级语义的 data_gap。

    Args:
        data_gaps: 报告数据缺口列表。
        requirement: 证据要求。

    Returns:
        兼容 data_gap；不存在时返回 `None`。

    Raises:
        无显式抛出。
    """

    accepted_reason_codes = set(requirement.accepted_gap_reason_codes)
    for gap in data_gaps:
        if "chapter_3" not in gap.chapter_ids:
            continue
        if gap.reason_code not in accepted_reason_codes:
            continue
        if gap.field_path not in _TURNOVER_STYLE_GAP_FIELD_PATHS:
            continue
        return gap
    return None


def _gap_has_required_explicit_fields(
    *,
    reason_code: str,
    field_path: str | None,
    required_report_wording: str,
) -> bool:
    """判断 records data_gap 是否显式携带可兼容字段。

    Args:
        reason_code: caller-supplied data_gap 原因码。
        field_path: caller-supplied 字段路径。
        required_report_wording: caller-supplied 降级措辞。

    Returns:
        三个 compatibility-bearing 字段均显式匹配时返回 `True`。

    Raises:
        无显式抛出。
    """

    if reason_code not in TURNOVER_STYLE_GAP_REASON_CODES:
        return False
    if field_path not in _TURNOVER_STYLE_GAP_FIELD_PATHS:
        return False
    return bool(required_report_wording.strip())


def _drafts_preserve_required_wording(
    chapter_drafts: tuple[ChapterDraftSurrogate, ...],
    gap: ReportDataGap,
) -> bool:
    """判断草稿是否保留 data_gap 要求的证据不足措辞。

    Args:
        chapter_drafts: 第 3 章草稿代理。
        gap: 兼容 data_gap。

    Returns:
        草稿保留全部必要措辞时返回 `True`。

    Raises:
        无显式抛出。
    """

    fragments = _required_wording_fragments(gap)
    return any(all(fragment in draft.markdown for fragment in fragments) for draft in chapter_drafts)


def _required_wording_fragments(gap: ReportDataGap) -> tuple[str, ...]:
    """解析 data_gap 必须保留的措辞片段。

    Args:
        gap: 兼容 data_gap。

    Returns:
        必须保留的措辞片段。

    Raises:
        无显式抛出。
    """

    fragments = list(TURNOVER_STYLE_REQUIRED_WORDING_FRAGMENTS)
    if gap.required_report_wording and _INSUFFICIENT_WORDING in gap.required_report_wording:
        fragments.insert(0, _INSUFFICIENT_WORDING)
    return tuple(dict.fromkeys(fragments))


def _has_active_chapter_3_stability_claim(draft: ChapterDraftSurrogate) -> bool:
    """判断草稿是否包含主动基金第 3 章稳定性正向 claim。

    Args:
        draft: 章节草稿代理。

    Returns:
        显式 claim_tags 命中或中文短语命中时返回 `True`。

    Raises:
        无显式抛出。
    """

    if any(tag in _STABILITY_CLAIM_TAGS for tag in draft.claim_tags):
        return True
    return any(_phrase_is_positive_claim(draft.markdown, phrase) for phrase in _STABILITY_PHRASES)


def _phrase_is_positive_claim(markdown: str, phrase: str) -> bool:
    """判断稳定性短语是否为正向 claim。

    Args:
        markdown: 草稿文本。
        phrase: 待检测中文稳定性短语。

    Returns:
        短语出现且附近没有否定判断前缀时返回 `True`。

    Raises:
        无显式抛出。
    """

    index = markdown.find(phrase)
    while index >= 0:
        window_start = max(0, index - 20)
        prefix = markdown[window_start:index]
        if not any(negated in prefix for negated in _NEGATED_STABILITY_PREFIXES):
            sentence_start = _sentence_window_start(markdown, index)
            sentence_end = _sentence_window_end(markdown, index)
            sentence_prefix = markdown[sentence_start:index]
            sentence_suffix = markdown[index:sentence_end]
            if (
                any(questioning in sentence_suffix for questioning in _QUESTIONING_STABILITY_SUFFIXES)
                and any(
                    question_prefix in sentence_prefix
                    for question_prefix in _QUESTIONING_STABILITY_PREFIXES
                )
            ):
                index = markdown.find(phrase, index + len(phrase))
                continue
            return True
        index = markdown.find(phrase, index + len(phrase))
    return False


def _sentence_window_start(markdown: str, index: int) -> int:
    """查找稳定性短语所在句段的起点。

    Args:
        markdown: 草稿文本。
        index: 稳定性短语起始位置。

    Returns:
        句段起始位置；未找到分隔符时返回 `0`。

    Raises:
        无显式抛出。
    """

    separators = ("。", "！", "？", "\n", "；", ";")
    previous_positions = (markdown.rfind(separator, 0, index) for separator in separators)
    return max(previous_positions, default=-1) + 1


def _sentence_window_end(markdown: str, index: int) -> int:
    """查找稳定性短语所在句段的终点。

    Args:
        markdown: 草稿文本。
        index: 稳定性短语起始位置。

    Returns:
        句段终点位置；未找到分隔符时返回全文长度。

    Raises:
        无显式抛出。
    """

    separators = ("。", "！", "？", "\n", "；", ";")
    next_positions = tuple(
        position for separator in separators if (position := markdown.find(separator, index)) >= 0
    )
    return min(next_positions, default=len(markdown))


def _active_chapter_3_requirement() -> EvidenceRequirement:
    """读取主动基金第 3 章 material 证据要求。

    Args:
        无。

    Returns:
        active_fund 第 3 章换手率/风格一致性证据要求。

    Raises:
        ValueError: sidecar 缺少必要 requirement 时抛出。
    """

    for constraint in constraints_for_chapter(3, "active_fund"):
        for requirement in constraint.required_evidence:
            if requirement.requirement_id == ACTIVE_CHAPTER_3_TURNOVER_REQUIREMENT_ID:
                return requirement
    raise ValueError("sidecar 缺少主动基金第 3 章换手率/风格一致性证据要求")


def _build_requirement_issue(
    *,
    requirement: EvidenceRequirement,
    severity: AuditIssueSeverity,
    failure_category: FailureCategory,
    message: str,
    anchor_refs: tuple[str, ...],
    data_gap_refs: tuple[str, ...],
) -> ReportWritingAuditIssue:
    """构造 requirement 级 issue。

    Args:
        requirement: 证据要求。
        severity: issue 严重程度。
        failure_category: 失败分类。
        message: 中文问题说明。
        anchor_refs: 相关锚点引用。
        data_gap_refs: 相关 data_gap 引用。

    Returns:
        确定性 issue。

    Raises:
        无显式抛出。
    """

    return _build_issue(
        chapter_id=requirement.chapter_id,
        fund_type_slot=requirement.fund_type_slot,
        severity=severity,
        failure_category=failure_category,
        requirement_id=requirement.requirement_id,
        message=message,
        evidence_requirement_gaps=(requirement.requirement_id,),
        anchor_refs=anchor_refs,
        data_gap_refs=data_gap_refs,
    )


def _build_issue(
    *,
    chapter_id: int | None,
    fund_type_slot: str,
    severity: AuditIssueSeverity,
    failure_category: FailureCategory,
    requirement_id: str | None,
    message: str,
    evidence_requirement_gaps: tuple[str, ...] = (),
    anchor_refs: tuple[str, ...] = (),
    data_gap_refs: tuple[str, ...] = (),
    issue_key: str | None = None,
) -> ReportWritingAuditIssue:
    """构造写作审计 issue。

    Args:
        chapter_id: 章节编号；报告级为 `None`。
        fund_type_slot: 基金类型 slot。
        severity: issue 严重程度。
        failure_category: 失败分类。
        requirement_id: 关联 requirement id。
        message: 中文问题说明。
        evidence_requirement_gaps: 未满足的证据要求 id。
        anchor_refs: 相关锚点引用。
        data_gap_refs: 相关 data_gap 引用。
        issue_key: 可选附加定位键。

    Returns:
        确定性 issue。

    Raises:
        无显式抛出。
    """

    chapter_part = f"chapter_{chapter_id}" if chapter_id is not None else "report"
    requirement_part = requirement_id or issue_key or "none"
    issue_id = f"rwa:{chapter_part}:{fund_type_slot}:{failure_category}:{requirement_part}"
    return ReportWritingAuditIssue(
        issue_id=issue_id,
        chapter_id=chapter_id,
        fund_type_slot=fund_type_slot,
        severity=severity,
        failure_category=failure_category,
        requirement_id=requirement_id,
        message=message,
        evidence_requirement_gaps=evidence_requirement_gaps,
        anchor_refs=anchor_refs,
        data_gap_refs=data_gap_refs,
    )


def _summarize_issues(
    issues: tuple[ReportWritingAuditIssue, ...],
) -> ReportWritingAuditSummary:
    """汇总写作审计 issue。

    Args:
        issues: issue 列表。

    Returns:
        稳定排序的汇总结果。

    Raises:
        无显式抛出。
    """

    severity_counts = Counter(issue.severity for issue in issues)
    failure_counts = Counter(issue.failure_category for issue in issues)
    return ReportWritingAuditSummary(
        issue_count=len(issues),
        blocking_count=severity_counts["blocking"],
        material_count=severity_counts["material"],
        minor_count=severity_counts["minor"],
        informational_count=severity_counts["informational"],
        failure_category_counts=tuple(sorted(failure_counts.items())),
        evidence_requirement_gap_count=sum(
            len(issue.evidence_requirement_gaps) for issue in issues
        ),
    )


def _group_drafts_by_chapter(
    chapter_drafts: tuple[ChapterDraftSurrogate, ...],
) -> dict[int, tuple[ChapterDraftSurrogate, ...]]:
    """按章节编号聚合草稿。

    Args:
        chapter_drafts: 章节草稿代理。

    Returns:
        chapter_id 到草稿元组的映射。

    Raises:
        无显式抛出。
    """

    grouped: dict[int, list[ChapterDraftSurrogate]] = {}
    for draft in chapter_drafts:
        grouped.setdefault(draft.chapter_id, []).append(draft)
    return {chapter_id: tuple(drafts) for chapter_id, drafts in grouped.items()}


def _resolve_bundle_fund_type_slot(
    bundle: ReportEvidenceBundle,
) -> FundType | Literal["default"]:
    """解析 bundle 基金类型 slot。

    Args:
        bundle: 报告证据包。

    Returns:
        `fund_type_slot` 缺失时返回 `default`，不会从 classified type 猜测 slot。

    Raises:
        无显式抛出。
    """

    return bundle.fund_type_slot or "default"


def _resolve_draft_fund_type_slot(
    draft: ChapterDraftSurrogate,
    bundle_fund_type_slot: FundType | Literal["default"],
) -> FundType | Literal["default"]:
    """解析草稿基金类型 slot。

    Args:
        draft: 章节草稿代理。
        bundle_fund_type_slot: bundle 推导出的基金类型 slot。

    Returns:
        草稿显式基金类型优先；`unknown` 回退到 bundle/default。

    Raises:
        无显式抛出。
    """

    if draft.fund_type_slot in ("default", "unknown"):
        return bundle_fund_type_slot
    return draft.fund_type_slot


def _resolve_chapter_fund_type_slot(
    *,
    chapter_drafts: tuple[ChapterDraftSurrogate, ...],
    bundle_fund_type_slot: FundType | Literal["default"],
) -> tuple[FundType | Literal["default"], tuple[ReportWritingAuditIssue, ...]]:
    """解析单章审计应使用的基金类型 slot。

    Args:
        chapter_drafts: 当前章节草稿代理。
        bundle_fund_type_slot: bundle 推导出的基金类型 slot。

    Returns:
        草稿显式基金类型优先；否则使用 bundle/default；冲突时返回 blocking issue。

    Raises:
        无显式抛出。
    """

    explicit_slots = tuple(
        draft.fund_type_slot
        for draft in chapter_drafts
        if draft.fund_type_slot not in ("default", "unknown")
    )
    unique_slots = tuple(dict.fromkeys(explicit_slots))
    if len(unique_slots) > 1:
        issue = _build_issue(
            chapter_id=3,
            fund_type_slot="default",
            severity="blocking",
            failure_category="input_conflict",
            requirement_id=None,
            message="同一章节草稿包含多个显式 fund_type_slot，写作审计 fail-closed。",
            issue_key="fund_type_slot_conflict",
        )
        return "default", (issue,)
    if unique_slots:
        return unique_slots[0], ()
    return bundle_fund_type_slot, ()


def _contains_trading_advice(markdown: str) -> bool:
    """判断文本是否包含直接交易建议。

    Args:
        markdown: 草稿文本。

    Returns:
        命中买入、卖出、仓位比例等禁区短语时返回 `True`。

    Raises:
        无显式抛出。
    """

    return any(phrase in markdown for phrase in _TRADING_ADVICE_PHRASES)


def _forbidden_rule_hits(forbidden_rule: str, markdown: str) -> bool:
    """判断 must_not_cover 文本规则是否被草稿触发。

    Args:
        forbidden_rule: CHAPTER_CONTRACT must_not_cover 规则。
        markdown: 草稿文本。

    Returns:
        当前最小 deterministic 规则命中时返回 `True`。

    Raises:
        无显式抛出。
    """

    if "买入金额" in forbidden_rule and _contains_trading_advice(markdown):
        return True
    if "卖出时机" in forbidden_rule and _contains_trading_advice(markdown):
        return True
    if "仓位比例" in forbidden_rule and _contains_trading_advice(markdown):
        return True
    if "动机猜测" in forbidden_rule and ("动机" in markdown or "性格" in markdown):
        return True
    return False


def _mapping_sequence(value: object) -> tuple[Mapping[str, object], ...]:
    """把 record 子序列收敛为 mapping 元组。

    Args:
        value: 任意 JSON-like 值。

    Returns:
        mapping 元组；非 mapping 项会被忽略。

    Raises:
        无显式抛出。
    """

    if not isinstance(value, Iterable) or isinstance(value, (str, bytes, Mapping)):
        return ()
    return tuple(item for item in value if isinstance(item, Mapping))


def _coerce_classified_fund_type(value: object) -> FundType | Literal["unknown"]:
    """把 JSON-like 值转为 classified fund type。

    Args:
        value: 原始基金类型值。

    Returns:
        支持的基金类型；无法识别时返回 `unknown`。

    Raises:
        无显式抛出。
    """

    if value in (
        "index_fund",
        "active_fund",
        "bond_fund",
        "enhanced_index",
        "qdii_fund",
        "fof_fund",
    ):
        return value  # type: ignore[return-value]
    return "unknown"


def _coerce_fund_type_or_none(value: object) -> FundType | None:
    """把 JSON-like 值转为 fund_type_slot。

    Args:
        value: 原始基金类型 slot。

    Returns:
        支持的基金类型；无法识别时返回 `None`。

    Raises:
        无显式抛出。
    """

    classified = _coerce_classified_fund_type(value)
    if classified == "unknown":
        return None
    return classified


def _coerce_report_year(
    value: object,
) -> tuple[int, ReportWritingAuditIssue | None]:
    """把 records report_year 转为整数并保守处理异常。

    Args:
        value: caller-supplied report_year 值。

    Returns:
        年份整数和可选输入校验 issue。

    Raises:
        无显式抛出。
    """

    try:
        return int(value or 0), None
    except (TypeError, ValueError):
        issue = _build_issue(
            chapter_id=None,
            fund_type_slot="default",
            severity="blocking",
            failure_category="invalid_audit_input",
            requirement_id=None,
            message="records bundle report_year 不是整数，写作审计 fail-closed。",
            issue_key="report_year",
        )
        return 0, issue


def _optional_int_or_none(value: object) -> int | None:
    """把可选 JSON-like 值转为整数。

    Args:
        value: 原始值。

    Returns:
        可解析整数；不可解析或缺失时返回 `None`。

    Raises:
        无显式抛出。
    """

    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _optional_str(value: object) -> str | None:
    """把可选 JSON-like 值转为字符串。

    Args:
        value: 原始值。

    Returns:
        `None` 或字符串。

    Raises:
        无显式抛出。
    """

    if value is None:
        return None
    return str(value)


def issue_records(result: ReportWritingAuditResult) -> tuple[dict[str, object], ...]:
    """把审计 issue 转为 caller-supplied records 可复用的 dict。

    Args:
        result: 写作审计结果。

    Returns:
        issue dict 元组；调用方可自行写入 JSONL。

    Raises:
        无显式抛出。
    """

    return tuple(asdict(issue) for issue in result.issues)


def bundle_to_record(bundle: ReportEvidenceBundle) -> dict[str, object]:
    """把 dataclass bundle 转为 dev-only records helper 可消费的 mapping。

    Args:
        bundle: 报告证据包。

    Returns:
        bundle record mapping。

    Raises:
        TypeError: 输入不是 dataclass 时抛出。
    """

    if not is_dataclass(bundle):
        raise TypeError("bundle_to_record 只接受 ReportEvidenceBundle dataclass")
    record = asdict(bundle)
    record["record_type"] = "bundle"
    return record
