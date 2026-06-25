"""证据复核与锚点可审计性评分，见基金分析模板第 0-7 章。

本模块属于 Agent 层 ``fund_agent/fund`` 基金领域能力，只消费调用方显式传入的
章节事实投影和同源引用摘录。它不读取年报仓库、PDF/cache/source helper、Service、
Host、provider、网络、文件系统或 dayu runtime。当前实现是 no-live phase 1：
只验证 fact value 与同一个 anchor id 的显式 reference excerpt 是否可复核。
"""

from __future__ import annotations

import hashlib
import re
import unicodedata
from dataclasses import asdict, dataclass, is_dataclass
from decimal import Decimal, InvalidOperation
from typing import Final, Literal, TypeAlias

from fund_agent.fund.chapter_facts import (
    ChapterEvidenceAnchor,
    ChapterFactEntry,
    ChapterFactInput,
    ChapterFactProjection,
)
from fund_agent.fund.source_facts import AtomicSourceFact, CompositeAnalysisView

EVIDENCE_CONFIRM_SCHEMA_VERSION: Final[str] = "evidence_confirm.v1"
EVIDENCE_CONFIRM_V2_SCHEMA_VERSION: Final[str] = "evidence_confirm.v2"

EvidenceConfirmRuleCode: TypeAlias = Literal["E1", "E2", "E3"]
EvidenceConfirmStatus: TypeAlias = Literal["pass", "warn", "fail", "not_applicable"]
EvidenceConfirmSeverity: TypeAlias = Literal["blocking", "reviewable", "informational"]
EvidenceConfirmReferenceKind: TypeAlias = Literal[
    "annual_report_excerpt",
    "reviewed_note",
    "derived_calculation",
]
EvidenceConfirmSourceTruthStatus: TypeAlias = Literal["proven", "not_proven"]

EvidenceConfirmGateStatus: TypeAlias = Literal["pass", "warn", "fail", "not_applicable"]
EvidenceConfirmDimension: TypeAlias = Literal[
    "anchor_precision", "source_support", "missing_evidence", "proof_boundary", "value_match"
]
EvidenceConfirmDimensionStatus: TypeAlias = Literal["pass", "warn", "fail", "not_applicable"]
EvidenceConfirmGateSeverity: TypeAlias = Literal["blocking", "reviewable", "informational"]
EvidenceConfirmNextGateRecommendation: TypeAlias = Literal[
    "evidence_anchor", "source_truth_proof", "value_matching", "manual_review", "not_applicable"
]

_V2_DIMENSION_ORDER: Final[tuple[EvidenceConfirmDimension, ...]] = (
    "anchor_precision",
    "source_support",
    "missing_evidence",
    "proof_boundary",
    "value_match",
)

_PROOF_SOURCE_KINDS: Final[frozenset[str]] = frozenset(("annual_report", "reviewed_note", "derived"))
_REFERENCE_SOURCE_KIND_PAIRS: Final[dict[str, str]] = {
    "annual_report_excerpt": "annual_report",
    "reviewed_note": "reviewed_note",
    "derived_calculation": "derived",
}
_IGNORED_VALUE_KEYS: Final[frozenset[str]] = frozenset(
    (
        "schema_version",
        "fund_code",
        "report_year",
        "source_anchor",
        "source_anchors",
    )
)
_WHITESPACE_RE: Final[re.Pattern[str]] = re.compile(r"\s+")
_PUNCTUATION_RE: Final[re.Pattern[str]] = re.compile(r"[，,。；;：:、（）()\[\]{}]")
_NUMERIC_TOKEN_RE: Final[re.Pattern[str]] = re.compile(r"^[+-]?\d+(?:\.\d+)?%?$")
_NUMERIC_CANDIDATE_RE: Final[re.Pattern[str]] = re.compile(r"(?<![\d.])[+-]?\d+(?:\.\d+)?%?(?![\d.])")


class _UnresolvedFactMaterial:
    """bridge material value 无法解析的内部哨兵。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        无显式抛出。
    """


_UNRESOLVED_FACT_MATERIAL: Final[_UnresolvedFactMaterial] = _UnresolvedFactMaterial()


@dataclass(frozen=True, slots=True)
class EvidenceConfirmReference:
    """Evidence Confirm 显式引用摘录。

    Attributes:
        anchor_id: 关联的章节 anchor id。
        reference_kind: 引用摘录类型。
        source_kind: 来源类型，phase 1 使用本模块闭集校验。
        document_year: 年报年份；非文档来源可为 ``None``。
        section_id: 年报章节编号或 reviewed note 定位。
        page_number: 页码。
        table_id: 表格标识。
        row_locator: 行级定位。
        excerpt_text: 与 anchor id 同源的摘录文本。
        source_truth_status: 该引用是否已被调用方声明为 proven。
        candidate_only: 是否仍是 candidate-only 证据。
    """

    anchor_id: str
    reference_kind: EvidenceConfirmReferenceKind
    source_kind: str
    document_year: int | None
    section_id: str | None
    page_number: int | None
    table_id: str | None
    row_locator: str | None
    excerpt_text: str
    source_truth_status: EvidenceConfirmSourceTruthStatus = "proven"
    candidate_only: bool = False


@dataclass(frozen=True, slots=True)
class EvidenceConfirmIssue:
    """Evidence Confirm issue。

    Attributes:
        issue_id: 稳定 issue id。
        rule_code: E1/E2/E3 规则码。
        severity: 严重程度。
        fact_id: 关联事实 id。
        source_field_id: 关联来源字段 id。
        anchor_id: 关联 anchor id；缺失时为 ``None``。
        message: 中文问题说明。
    """

    issue_id: str
    rule_code: EvidenceConfirmRuleCode
    severity: EvidenceConfirmSeverity
    fact_id: str
    source_field_id: str
    anchor_id: str | None
    message: str


@dataclass(frozen=True, slots=True)
class EvidenceConfirmFactResult:
    """单个 fact 的证据复核结果。

    Attributes:
        fact_id: 关联事实 id。
        source_field_id: 关联来源字段 id。
        status: 单 fact 复核状态。
        matched_anchor_ids: 通过同源摘录匹配的 anchor ids。
        issue_ids: 关联 issue ids。
        auditability_score: 可审计性分数；not_applicable 时为 ``None``。
    """

    fact_id: str
    source_field_id: str
    status: EvidenceConfirmStatus
    matched_anchor_ids: tuple[str, ...]
    issue_ids: tuple[str, ...]
    auditability_score: int | None


@dataclass(frozen=True, slots=True)
class EvidenceConfirmResult:
    """Evidence Confirm 聚合结果。

    Attributes:
        schema_version: 结果 schema 版本。
        fund_code: 基金代码。
        report_year: 年报年份。
        fact_results: 单 fact 结果。
        issues: 所有 issue。
        checked_rules: 已执行规则。
        overall_status: 聚合状态。
        auditability_score: 聚合平均分；无可计分 fact 时为 ``None``。
    """

    schema_version: str
    fund_code: str
    report_year: int
    fact_results: tuple[EvidenceConfirmFactResult, ...]
    issues: tuple[EvidenceConfirmIssue, ...]
    checked_rules: tuple[EvidenceConfirmRuleCode, ...]
    overall_status: EvidenceConfirmStatus
    auditability_score: int | None


@dataclass(frozen=True, slots=True)
class EvidenceConfirmDimensionResult:
    """V2 单维度评分结果。

    Attributes:
        dimension: 维度名称。
        status: 维度状态。
        score: 维度分数；not_applicable 时为 ``None``。
        issue_ids: 关联 issue ids。
        matched_anchor_ids: 匹配 anchor ids。
        next_gate_recommendation: 下一 gate 建议。
        message: 可选说明。
    """

    dimension: EvidenceConfirmDimension
    status: EvidenceConfirmDimensionStatus
    score: int | None
    issue_ids: tuple[str, ...]
    matched_anchor_ids: tuple[str, ...]
    next_gate_recommendation: EvidenceConfirmNextGateRecommendation
    message: str | None = None


@dataclass(frozen=True, slots=True)
class EvidenceConfirmHardGate:
    """V2 硬门控结果。

    Attributes:
        status: 门控状态。
        blocking_issue_ids: 阻塞 issue ids。
        reviewable_issue_ids: 可复核 issue ids。
        informational_issue_ids: 信息性 issue ids。
        passed_dimension_count: 通过维度数。
        failed_dimension_count: 失败维度数。
        warn_dimension_count: 警告维度数。
        not_applicable_dimension_count: 不适用维度数。
    """

    status: EvidenceConfirmGateStatus
    blocking_issue_ids: tuple[str, ...]
    reviewable_issue_ids: tuple[str, ...]
    informational_issue_ids: tuple[str, ...]
    passed_dimension_count: int
    failed_dimension_count: int
    warn_dimension_count: int
    not_applicable_dimension_count: int


@dataclass(frozen=True, slots=True)
class EvidenceConfirmFactResultV2:
    """V2 单 fact 证据复核结果。

    Attributes:
        fact_id: 关联事实 id。
        source_field_id: 关联来源字段 id。
        status: fact 硬门控状态。
        hard_gate: fact 硬门控详情。
        dimension_results: 五维度结果，按确定性顺序。
        matched_anchor_ids: 匹配 anchor ids。
        issue_ids: 关联 issue ids。
        auditability_score: 可审计性分数；not_applicable 时为 ``None``。
    """

    fact_id: str
    source_field_id: str
    status: EvidenceConfirmGateStatus
    hard_gate: EvidenceConfirmHardGate
    dimension_results: tuple[EvidenceConfirmDimensionResult, ...]
    matched_anchor_ids: tuple[str, ...]
    issue_ids: tuple[str, ...]
    auditability_score: int | None


@dataclass(frozen=True, slots=True)
class EvidenceConfirmResultV2:
    """V2 Evidence Confirm 聚合结果。

    Attributes:
        schema_version: 结果 schema 版本。
        fund_code: 基金代码。
        report_year: 年报年份。
        fact_results: 单 fact V2 结果。
        issues: 所有 issue。
        checked_rules: 已执行规则。
        hard_gate: 聚合硬门控。
        overall_status: 聚合状态，等于 hard_gate.status。
        auditability_score: 聚合可审计性分数。
    """

    schema_version: str
    fund_code: str
    report_year: int
    fact_results: tuple[EvidenceConfirmFactResultV2, ...]
    issues: tuple[EvidenceConfirmIssue, ...]
    checked_rules: tuple[EvidenceConfirmRuleCode, ...]
    hard_gate: EvidenceConfirmHardGate
    overall_status: EvidenceConfirmGateStatus
    auditability_score: int | None


def confirm_chapter_evidence(
    chapter: ChapterFactInput,
    references: tuple[EvidenceConfirmReference, ...],
) -> EvidenceConfirmResult:
    """复核单章 fact 与 anchor reference 的同源关系。

    Args:
        chapter: 单章事实输入。
        references: 调用方显式传入的同源引用摘录。

    Returns:
        单章 Evidence Confirm 结果。

    Raises:
        无显式抛出。
    """

    references_by_anchor = _references_by_anchor(references)
    anchors_by_id = _anchors_by_id(chapter.evidence_anchors)
    report_year = _report_year_from_facts(chapter.facts) or _report_year_from_references(references)
    issues: list[EvidenceConfirmIssue] = []
    fact_results: list[EvidenceConfirmFactResult] = []
    for fact in sorted(chapter.facts, key=lambda item: (item.source_field_id, item.fact_id)):
        fact_result, fact_issues = _confirm_fact(fact, references_by_anchor, anchors_by_id, report_year)
        issues.extend(fact_issues)
        fact_results.append(fact_result)
    sorted_issues = tuple(sorted(issues, key=lambda issue: issue.issue_id))
    sorted_fact_results = tuple(sorted(fact_results, key=lambda item: (item.source_field_id, item.fact_id)))
    return EvidenceConfirmResult(
        schema_version=EVIDENCE_CONFIRM_SCHEMA_VERSION,
        fund_code=_fund_code_from_facts(chapter.facts),
        report_year=report_year,
        fact_results=sorted_fact_results,
        issues=sorted_issues,
        checked_rules=("E1", "E2", "E3"),
        overall_status=_overall_status(sorted_issues, sorted_fact_results),
        auditability_score=_aggregate_score(sorted_fact_results),
    )


def confirm_projection_evidence(
    projection: ChapterFactProjection,
    references: tuple[EvidenceConfirmReference, ...],
) -> EvidenceConfirmResult:
    """复核章节事实投影中的全部章节。

    Args:
        projection: 章节事实投影。
        references: 调用方显式传入的同源引用摘录。

    Returns:
        聚合 Evidence Confirm 结果。

    Raises:
        无显式抛出。
    """

    references_by_anchor = _references_by_anchor(references)
    issues: list[EvidenceConfirmIssue] = []
    fact_results: list[EvidenceConfirmFactResult] = []
    for chapter in sorted(projection.chapters, key=lambda item: item.chapter_id):
        anchors_by_id = _anchors_by_id(chapter.evidence_anchors)
        for fact in sorted(chapter.facts, key=lambda item: (item.source_field_id, item.fact_id)):
            fact_result, fact_issues = _confirm_fact(
                fact,
                references_by_anchor,
                anchors_by_id,
                projection.report_year,
                projection,
            )
            issues.extend(fact_issues)
            fact_results.append(fact_result)
    sorted_issues = tuple(sorted(issues, key=lambda issue: issue.issue_id))
    sorted_fact_results = tuple(
        sorted(fact_results, key=lambda item: (item.source_field_id, item.fact_id))
    )
    return EvidenceConfirmResult(
        schema_version=EVIDENCE_CONFIRM_SCHEMA_VERSION,
        fund_code=projection.fund_code,
        report_year=projection.report_year,
        fact_results=sorted_fact_results,
        issues=sorted_issues,
        checked_rules=("E1", "E2", "E3"),
        overall_status=_overall_status(sorted_issues, sorted_fact_results),
        auditability_score=_aggregate_score(sorted_fact_results),
    )


def confirm_chapter_evidence_v2(
    chapter: ChapterFactInput,
    references: tuple[EvidenceConfirmReference, ...],
) -> EvidenceConfirmResultV2:
    """V2 复核单章 fact 与 anchor reference 的同源关系。

    产生五维度评分和硬门控结果。不读取外部状态。

    Args:
        chapter: 单章事实输入。
        references: 调用方显式传入的同源引用摘录。

    Returns:
        V2 单章 Evidence Confirm 结果。

    Raises:
        无显式抛出。
    """

    references_by_anchor = _references_by_anchor(references)
    anchors_by_id = _anchors_by_id(chapter.evidence_anchors)
    report_year = _report_year_from_facts(chapter.facts) or _report_year_from_references(references)
    issues: list[EvidenceConfirmIssue] = []
    fact_results: list[EvidenceConfirmFactResultV2] = []
    for fact in sorted(chapter.facts, key=lambda item: (item.source_field_id, item.fact_id)):
        fact_result, fact_issues = _confirm_fact_v2(fact, references_by_anchor, anchors_by_id, report_year)
        issues.extend(fact_issues)
        fact_results.append(fact_result)
    sorted_issues = tuple(sorted(issues, key=lambda issue: issue.issue_id))
    sorted_fact_results = tuple(sorted(fact_results, key=lambda item: (item.source_field_id, item.fact_id)))
    aggregate_hard_gate = _aggregate_hard_gate(sorted_fact_results)
    return EvidenceConfirmResultV2(
        schema_version=EVIDENCE_CONFIRM_V2_SCHEMA_VERSION,
        fund_code=_fund_code_from_facts(chapter.facts),
        report_year=report_year,
        fact_results=sorted_fact_results,
        issues=sorted_issues,
        checked_rules=("E1", "E2", "E3"),
        hard_gate=aggregate_hard_gate,
        overall_status=aggregate_hard_gate.status,
        auditability_score=_aggregate_score_v2(sorted_fact_results, aggregate_hard_gate),
    )


def confirm_projection_evidence_v2(
    projection: ChapterFactProjection,
    references: tuple[EvidenceConfirmReference, ...],
) -> EvidenceConfirmResultV2:
    """V2 复核章节事实投影中的全部章节。

    聚合所有章节 fact 结果，按 chapter_id/source_field_id/fact_id 稳定排序。

    Args:
        projection: 章节事实投影。
        references: 调用方显式传入的同源引用摘录。

    Returns:
        V2 聚合 Evidence Confirm 结果。

    Raises:
        无显式抛出。
    """

    references_by_anchor = _references_by_anchor(references)
    issues: list[EvidenceConfirmIssue] = []
    fact_results: list[tuple[int, EvidenceConfirmFactResultV2]] = []
    for chapter in sorted(projection.chapters, key=lambda item: item.chapter_id):
        anchors_by_id = _anchors_by_id(chapter.evidence_anchors)
        for fact in sorted(chapter.facts, key=lambda item: (item.source_field_id, item.fact_id)):
            fact_result, fact_issues = _confirm_fact_v2(
                fact,
                references_by_anchor,
                anchors_by_id,
                projection.report_year,
                projection,
            )
            issues.extend(fact_issues)
            fact_results.append((chapter.chapter_id, fact_result))
    sorted_issues = tuple(sorted(issues, key=lambda issue: issue.issue_id))
    sorted_fact_results = tuple(
        item[1]
        for item in sorted(
            fact_results,
            key=lambda item: (item[0], item[1].source_field_id, item[1].fact_id),
        )
    )
    aggregate_hard_gate = _aggregate_hard_gate(sorted_fact_results)
    return EvidenceConfirmResultV2(
        schema_version=EVIDENCE_CONFIRM_V2_SCHEMA_VERSION,
        fund_code=projection.fund_code,
        report_year=projection.report_year,
        fact_results=sorted_fact_results,
        issues=sorted_issues,
        checked_rules=("E1", "E2", "E3"),
        hard_gate=aggregate_hard_gate,
        overall_status=aggregate_hard_gate.status,
        auditability_score=_aggregate_score_v2(sorted_fact_results, aggregate_hard_gate),
    )


def _confirm_fact_v2(
    fact: ChapterFactEntry,
    references_by_anchor: dict[str, tuple[EvidenceConfirmReference, ...]],
    anchors_by_id: dict[str, ChapterEvidenceAnchor],
    report_year: int,
    projection: ChapterFactProjection | None = None,
) -> tuple[EvidenceConfirmFactResultV2, tuple[EvidenceConfirmIssue, ...]]:
    """V2 复核单个 fact，产生五维度结果。

    Args:
        fact: 章节事实。
        references_by_anchor: anchor id 到引用摘录的映射。
        anchors_by_id: anchor id 到章节证据锚点的映射。
        report_year: 当前报告年份。

    Returns:
        V2 单 fact result 与 issue 列表。

    Raises:
        无显式抛出。
    """

    if _fact_is_not_applicable(fact):
        return _fact_result_v2_not_applicable(fact), ()

    if fact.missing_reason == "evidence_missing":
        issue = _issue("E3", "blocking", fact, None, "缺锚点 fact 不能被证据复核确认。")
        return _fact_result_v2_e3_blocking(fact, (issue,)), (issue,)

    if fact.status != "available":
        return _fact_result_v2_not_applicable(fact), ()

    if _fact_is_derived(fact):
        derived_issues = _derived_dependency_provenance_issues(fact, projection)
        if derived_issues:
            return _fact_result_v2_e3_blocking(fact, derived_issues), derived_issues
        return _fact_result_v2_not_applicable(fact), ()

    if not fact.evidence_anchor_ids:
        issue = _issue("E3", "blocking", fact, None, "可用 fact 缺少 evidence anchor。")
        return _fact_result_v2_e3_blocking(fact, (issue,)), (issue,)

    dangling_anchor_ids = _dangling_anchor_ids_for_fact(fact, anchors_by_id)
    known_anchors = _known_anchors_for_fact(fact, anchors_by_id)
    if not known_anchors:
        issues = _dangling_anchor_issues_for_fact(fact, dangling_anchor_ids)
        return _fact_result_v2_e3_blocking(fact, issues), issues

    if not any(anchor.source_kind in _PROOF_SOURCE_KINDS for anchor in known_anchors):
        return _fact_result_v2_not_applicable(fact), ()

    # 收集 fact 自身 anchor 的全部 references（含 non-proof）
    all_fact_references: list[EvidenceConfirmReference] = []
    for anchor_id in fact.evidence_anchor_ids:
        for reference in references_by_anchor.get(anchor_id, ()):
            all_fact_references.append(reference)

    proof_references = _proof_references_for_fact(fact, references_by_anchor, anchors_by_id, report_year)

    issues: list[EvidenceConfirmIssue] = []
    dimension_results: list[EvidenceConfirmDimensionResult] = []

    # 维度 1: anchor_precision
    dim_anchor, dim_anchor_issues = _dimension_anchor_precision(fact, proof_references, anchors_by_id)
    issues.extend(dim_anchor_issues)
    dimension_results.append(dim_anchor)

    # 维度 2: source_support
    dim_source, dim_source_issues = _dimension_source_support(fact, proof_references)
    issues.extend(dim_source_issues)
    dimension_results.append(dim_source)

    # 维度 3: missing_evidence
    dim_missing, dim_missing_issues = _dimension_missing_evidence(
        fact, proof_references, dangling_anchor_ids
    )
    issues.extend(dim_missing_issues)
    dimension_results.append(dim_missing)

    # 维度 4: proof_boundary
    dim_proof, dim_proof_issues = _dimension_proof_boundary(
        fact, all_fact_references, anchors_by_id, report_year
    )
    issues.extend(dim_proof_issues)
    dimension_results.append(dim_proof)

    # 维度 5: value_match
    material_value = _resolved_fact_material_value(projection, fact)
    dim_value, dim_value_issues = _dimension_value_match(fact, proof_references, material_value)
    issues.extend(dim_value_issues)
    dimension_results.append(dim_value)

    hard_gate = _fact_hard_gate(dimension_results, issues)
    matched_anchor_ids = _all_matched_anchor_ids(dimension_results)
    fact_score = _fact_score_v2(dimension_results, hard_gate)

    return EvidenceConfirmFactResultV2(
        fact_id=fact.fact_id,
        source_field_id=fact.source_field_id,
        status=hard_gate.status,
        hard_gate=hard_gate,
        dimension_results=tuple(dimension_results),
        matched_anchor_ids=matched_anchor_ids,
        issue_ids=_issue_ids(issues),
        auditability_score=fact_score,
    ), tuple(issues)


def _fact_result_v2_not_applicable(fact: ChapterFactEntry) -> EvidenceConfirmFactResultV2:
    """构造 not_applicable V2 fact result。

    Args:
        fact: 章节事实。

    Returns:
        所有维度 not_applicable 的 V2 fact result。

    Raises:
        无显式抛出。
    """

    dimension_results = tuple(
        EvidenceConfirmDimensionResult(
            dimension=dim,
            status="not_applicable",
            score=None,
            issue_ids=(),
            matched_anchor_ids=(),
            next_gate_recommendation="not_applicable",
        )
        for dim in _V2_DIMENSION_ORDER
    )
    hard_gate = EvidenceConfirmHardGate(
        status="not_applicable",
        blocking_issue_ids=(),
        reviewable_issue_ids=(),
        informational_issue_ids=(),
        passed_dimension_count=0,
        failed_dimension_count=0,
        warn_dimension_count=0,
        not_applicable_dimension_count=5,
    )
    return EvidenceConfirmFactResultV2(
        fact_id=fact.fact_id,
        source_field_id=fact.source_field_id,
        status="not_applicable",
        hard_gate=hard_gate,
        dimension_results=dimension_results,
        matched_anchor_ids=(),
        issue_ids=(),
        auditability_score=None,
    )


def _fact_result_v2_e3_blocking(
    fact: ChapterFactEntry,
    blocking_issues: tuple[EvidenceConfirmIssue, ...],
) -> EvidenceConfirmFactResultV2:
    """构造 E3 阻塞失败的 V2 fact result。

    Args:
        fact: 章节事实。
        blocking_issues: 阻塞 issue 列表。

    Returns:
        missing_evidence fail、其余 not_applicable 的 V2 fact result。

    Raises:
        无显式抛出。
    """

    blocking_issue_ids = tuple(issue.issue_id for issue in blocking_issues)
    dimension_results: list[EvidenceConfirmDimensionResult] = []
    for dim in _V2_DIMENSION_ORDER:
        if dim == "missing_evidence":
            dimension_results.append(
                EvidenceConfirmDimensionResult(
                    dimension=dim,
                    status="fail",
                    score=0,
                    issue_ids=blocking_issue_ids,
                    matched_anchor_ids=(),
                    next_gate_recommendation="evidence_anchor",
                )
            )
        else:
            dimension_results.append(
                EvidenceConfirmDimensionResult(
                    dimension=dim,
                    status="not_applicable",
                    score=None,
                    issue_ids=(),
                    matched_anchor_ids=(),
                    next_gate_recommendation="not_applicable",
                )
            )
    hard_gate = EvidenceConfirmHardGate(
        status="fail",
        blocking_issue_ids=blocking_issue_ids,
        reviewable_issue_ids=(),
        informational_issue_ids=(),
        passed_dimension_count=0,
        failed_dimension_count=1,
        warn_dimension_count=0,
        not_applicable_dimension_count=4,
    )
    return EvidenceConfirmFactResultV2(
        fact_id=fact.fact_id,
        source_field_id=fact.source_field_id,
        status="fail",
        hard_gate=hard_gate,
        dimension_results=tuple(dimension_results),
        matched_anchor_ids=(),
        issue_ids=blocking_issue_ids,
        auditability_score=0,
    )


def _dimension_anchor_precision(
    fact: ChapterFactEntry,
    proof_references: tuple[EvidenceConfirmReference, ...],
    anchors_by_id: dict[str, ChapterEvidenceAnchor] | None = None,
) -> tuple[EvidenceConfirmDimensionResult, tuple[EvidenceConfirmIssue, ...]]:
    """计算 anchor_precision 维度。

    Args:
        fact: 章节事实。
        proof_references: proven references。
        anchors_by_id: anchor id 到章节证据锚点的映射；用于识别 reference 定位降级。

    Returns:
        维度结果与 issue 列表。

    Raises:
        无显式抛出。
    """

    if not proof_references:
        return (
            EvidenceConfirmDimensionResult(
                dimension="anchor_precision",
                status="not_applicable",
                score=None,
                issue_ids=(),
                matched_anchor_ids=(),
                next_gate_recommendation="not_applicable",
            ),
            (),
        )

    issues: list[EvidenceConfirmIssue] = []
    for reference in proof_references:
        precision_issue = _precision_issue(fact, reference, anchors_by_id)
        if precision_issue is not None:
            issues.append(precision_issue)

    if issues:
        return (
            EvidenceConfirmDimensionResult(
                dimension="anchor_precision",
                status="warn",
                score=70,
                issue_ids=tuple(issue.issue_id for issue in issues),
                matched_anchor_ids=(),
                next_gate_recommendation="evidence_anchor",
            ),
            tuple(issues),
        )

    return (
        EvidenceConfirmDimensionResult(
            dimension="anchor_precision",
            status="pass",
            score=100,
            issue_ids=(),
            matched_anchor_ids=tuple(dict.fromkeys(r.anchor_id for r in proof_references)),
            next_gate_recommendation="evidence_anchor",
        ),
        (),
    )


def _dimension_source_support(
    fact: ChapterFactEntry,
    proof_references: tuple[EvidenceConfirmReference, ...],
) -> tuple[EvidenceConfirmDimensionResult, tuple[EvidenceConfirmIssue, ...]]:
    """计算 source_support 维度。

    Args:
        fact: 章节事实。
        proof_references: proven references。

    Returns:
        维度结果与 issue 列表。

    Raises:
        无显式抛出。
    """

    if _fact_is_not_applicable(fact) or _fact_is_derived(fact):
        return (
            EvidenceConfirmDimensionResult(
                dimension="source_support",
                status="not_applicable",
                score=None,
                issue_ids=(),
                matched_anchor_ids=(),
                next_gate_recommendation="not_applicable",
            ),
            (),
        )

    if proof_references:
        return (
            EvidenceConfirmDimensionResult(
                dimension="source_support",
                status="pass",
                score=100,
                issue_ids=(),
                matched_anchor_ids=tuple(dict.fromkeys(r.anchor_id for r in proof_references)),
                next_gate_recommendation="source_truth_proof",
            ),
            (),
        )

    issue = _issue(
        "E3",
        "blocking",
        fact,
        None,
        "source_support 缺少与 fact 自有 anchor 关联的 proven reference excerpt。",
    )
    return (
        EvidenceConfirmDimensionResult(
            dimension="source_support",
            status="fail",
            score=0,
            issue_ids=(issue.issue_id,),
            matched_anchor_ids=(),
            next_gate_recommendation="source_truth_proof",
        ),
        (issue,),
    )


def _dimension_missing_evidence(
    fact: ChapterFactEntry,
    proof_references: tuple[EvidenceConfirmReference, ...],
    dangling_anchor_ids: tuple[str, ...],
) -> tuple[EvidenceConfirmDimensionResult, tuple[EvidenceConfirmIssue, ...]]:
    """计算 missing_evidence 维度。

    Args:
        fact: 章节事实。
        proof_references: proven references。
        dangling_anchor_ids: fact 声明但当前章节不存在的 anchor ids。

    Returns:
        维度结果与 issue 列表。

    Raises:
        无显式抛出。
    """

    if _fact_is_not_applicable(fact) or _fact_is_derived(fact):
        return (
            EvidenceConfirmDimensionResult(
                dimension="missing_evidence",
                status="not_applicable",
                score=None,
                issue_ids=(),
                matched_anchor_ids=(),
                next_gate_recommendation="not_applicable",
            ),
            (),
        )

    if dangling_anchor_ids:
        issues = tuple(
            _issue(
                "E3",
                "blocking",
                fact,
                anchor_id,
                "missing_evidence fact anchor 不存在于当前章节 evidence anchors。",
            )
            for anchor_id in dangling_anchor_ids
        )
        return (
            EvidenceConfirmDimensionResult(
                dimension="missing_evidence",
                status="fail",
                score=0,
                issue_ids=tuple(issue.issue_id for issue in issues),
                matched_anchor_ids=(),
                next_gate_recommendation="evidence_anchor",
            ),
            issues,
        )

    if proof_references:
        return (
            EvidenceConfirmDimensionResult(
                dimension="missing_evidence",
                status="pass",
                score=100,
                issue_ids=(),
                matched_anchor_ids=tuple(dict.fromkeys(r.anchor_id for r in proof_references)),
                next_gate_recommendation="evidence_anchor",
            ),
            (),
        )

    issue = _issue(
        "E3",
        "blocking",
        fact,
        None,
        "missing_evidence 缺少满足 E3 证据要求的 proven reference excerpt。",
    )
    return (
        EvidenceConfirmDimensionResult(
            dimension="missing_evidence",
            status="fail",
            score=0,
            issue_ids=(issue.issue_id,),
            matched_anchor_ids=(),
            next_gate_recommendation="evidence_anchor",
        ),
        (issue,),
    )


def _dimension_proof_boundary(
    fact: ChapterFactEntry,
    all_fact_references: list[EvidenceConfirmReference],
    anchors_by_id: dict[str, ChapterEvidenceAnchor],
    report_year: int,
) -> tuple[EvidenceConfirmDimensionResult, tuple[EvidenceConfirmIssue, ...]]:
    """计算 proof_boundary 维度。

    混合引用规则：即使存在 valid proven references，若有 invalid same-anchor
    引用，proof_boundary 仍 fail。

    Args:
        fact: 章节事实。
        all_fact_references: fact 自身 anchor 的全部 references。
        anchors_by_id: anchor id 到章节证据锚点的映射。
        report_year: 当前报告年份。

    Returns:
        维度结果与 issue 列表。

    Raises:
        无显式抛出。
    """

    if _fact_is_not_applicable(fact) or _fact_is_derived(fact):
        return (
            EvidenceConfirmDimensionResult(
                dimension="proof_boundary",
                status="not_applicable",
                score=None,
                issue_ids=(),
                matched_anchor_ids=(),
                next_gate_recommendation="not_applicable",
            ),
            (),
        )

    if not all_fact_references:
        return (
            EvidenceConfirmDimensionResult(
                dimension="proof_boundary",
                status="not_applicable",
                score=None,
                issue_ids=(),
                matched_anchor_ids=(),
                next_gate_recommendation="not_applicable",
            ),
            (),
        )

    issues: list[EvidenceConfirmIssue] = []
    for reference in all_fact_references:
        anchor = anchors_by_id.get(reference.anchor_id)
        if anchor is None:
            issue = _issue(
                "E3",
                "blocking",
                fact,
                reference.anchor_id,
                "reference anchor 不存在于当前章节 evidence anchors。",
            )
            issues.append(issue)
            continue
        if not _reference_is_proof(reference, anchor, report_year):
            reason = _proof_failure_reason(reference, anchor, report_year)
            issue = _issue("E3", "blocking", fact, reference.anchor_id, reason)
            issues.append(issue)

    if issues:
        return (
            EvidenceConfirmDimensionResult(
                dimension="proof_boundary",
                status="fail",
                score=0,
                issue_ids=tuple(issue.issue_id for issue in issues),
                matched_anchor_ids=(),
                next_gate_recommendation="source_truth_proof",
            ),
            tuple(issues),
        )

    return (
        EvidenceConfirmDimensionResult(
            dimension="proof_boundary",
            status="pass",
            score=100,
            issue_ids=(),
            matched_anchor_ids=tuple(dict.fromkeys(r.anchor_id for r in all_fact_references)),
            next_gate_recommendation="source_truth_proof",
        ),
        (),
    )


def _proof_failure_reason(
    reference: EvidenceConfirmReference,
    anchor: ChapterEvidenceAnchor,
    report_year: int,
) -> str:
    """返回 proof 失败的具体原因。

    Args:
        reference: 引用摘录。
        anchor: 章节证据锚点。
        report_year: 报告年份。

    Returns:
        中文失败原因。

    Raises:
        无显式抛出。
    """

    if reference.candidate_only:
        return "candidate-only reference 不能满足 proof predicate。"
    if reference.source_truth_status != "proven":
        return "not_proven reference 不能满足 proof predicate。"
    if reference.source_kind not in _PROOF_SOURCE_KINDS:
        return f"未知 source_kind '{reference.source_kind}' 不能满足 proof predicate。"
    if _REFERENCE_SOURCE_KIND_PAIRS.get(reference.reference_kind) != reference.source_kind:
        return f"reference_kind '{reference.reference_kind}' 与 source_kind '{reference.source_kind}' 不匹配。"
    if anchor.source_kind != reference.source_kind:
        return f"reference source_kind '{reference.source_kind}' 与 anchor source_kind '{anchor.source_kind}' 不匹配。"
    if report_year and reference.document_year is not None and reference.document_year != report_year:
        return f"reference document_year {reference.document_year} 与 report_year {report_year} 不匹配。"
    if (
        anchor.document_year is not None
        and reference.document_year is not None
        and anchor.document_year != reference.document_year
    ):
        return f"reference document_year {reference.document_year} 与 anchor document_year {anchor.document_year} 不匹配。"
    if anchor.section_id and reference.section_id and anchor.section_id != reference.section_id:
        return f"reference section_id '{reference.section_id}' 与 anchor section_id '{anchor.section_id}' 不匹配。"
    if (
        anchor.page_number is not None
        and reference.page_number is not None
        and anchor.page_number != reference.page_number
    ):
        return f"reference page_number {reference.page_number} 与 anchor page_number {anchor.page_number} 不匹配。"
    if anchor.table_id and reference.table_id and anchor.table_id != reference.table_id:
        return f"reference table_id '{reference.table_id}' 与 anchor table_id '{anchor.table_id}' 不匹配。"
    if anchor.row_locator and reference.row_locator and anchor.row_locator != reference.row_locator:
        return f"reference row_locator '{reference.row_locator}' 与 anchor row_locator '{anchor.row_locator}' 不匹配。"
    return "reference 不满足 proof predicate。"


def _dimension_value_match(
    fact: ChapterFactEntry,
    proof_references: tuple[EvidenceConfirmReference, ...],
    material_value: object | None | _UnresolvedFactMaterial = _UNRESOLVED_FACT_MATERIAL,
) -> tuple[EvidenceConfirmDimensionResult, tuple[EvidenceConfirmIssue, ...]]:
    """计算 value_match 维度。

    Args:
        fact: 章节事实。
        proof_references: proven references。

    Returns:
        维度结果与 issue 列表。

    Raises:
        无显式抛出。
    """

    if _fact_is_not_applicable(fact) or _fact_is_derived(fact):
        return (
            EvidenceConfirmDimensionResult(
                dimension="value_match",
                status="not_applicable",
                score=None,
                issue_ids=(),
                matched_anchor_ids=(),
                next_gate_recommendation="not_applicable",
            ),
            (),
        )

    if not proof_references:
        return (
            EvidenceConfirmDimensionResult(
                dimension="value_match",
                status="not_applicable",
                score=None,
                issue_ids=(),
                matched_anchor_ids=(),
                next_gate_recommendation="not_applicable",
            ),
            (),
        )

    if material_value is _UNRESOLVED_FACT_MATERIAL:
        issue = _issue("E3", "blocking", fact, None, "bridge fact 无法解析 material value。")
        return (
            EvidenceConfirmDimensionResult(
                dimension="value_match",
                status="fail",
                score=0,
                issue_ids=(issue.issue_id,),
                matched_anchor_ids=(),
                next_gate_recommendation="manual_review",
            ),
            (issue,),
        )

    tokens = _material_tokens(material_value)
    if not tokens:
        if _fact_is_required(fact):
            issue = _issue("E3", "blocking", fact, None, "required fact 无可复核 material value token。")
            return (
                EvidenceConfirmDimensionResult(
                    dimension="value_match",
                    status="fail",
                    score=0,
                    issue_ids=(issue.issue_id,),
                    matched_anchor_ids=(),
                    next_gate_recommendation="manual_review",
                ),
                (issue,),
            )
        return (
            EvidenceConfirmDimensionResult(
                dimension="value_match",
                status="not_applicable",
                score=None,
                issue_ids=(),
                matched_anchor_ids=(),
                next_gate_recommendation="not_applicable",
            ),
            (),
        )

    matched_anchor_ids = _matched_anchor_ids(tokens, proof_references)
    if matched_anchor_ids:
        return (
            EvidenceConfirmDimensionResult(
                dimension="value_match",
                status="pass",
                score=100,
                issue_ids=(),
                matched_anchor_ids=matched_anchor_ids,
                next_gate_recommendation="value_matching",
            ),
            (),
        )

    issue = _issue(
        "E2",
        "blocking",
        fact,
        None,
        "fact value 未出现在同一 anchor 的 reference excerpt 中。",
    )
    return (
        EvidenceConfirmDimensionResult(
            dimension="value_match",
            status="fail",
            score=40,
            issue_ids=(issue.issue_id,),
            matched_anchor_ids=(),
            next_gate_recommendation="value_matching",
        ),
        (issue,),
    )


def _fact_hard_gate(
    dimension_results: list[EvidenceConfirmDimensionResult],
    issues: list[EvidenceConfirmIssue],
) -> EvidenceConfirmHardGate:
    """计算 fact 级硬门控。

    Args:
        dimension_results: 维度结果。
        issues: issue 列表。

    Returns:
        fact 级硬门控。

    Raises:
        无显式抛出。
    """

    blocking_issue_ids = tuple(issue.issue_id for issue in issues if issue.severity == "blocking")
    reviewable_issue_ids = tuple(issue.issue_id for issue in issues if issue.severity == "reviewable")
    informational_issue_ids = tuple(issue.issue_id for issue in issues if issue.severity == "informational")

    passed = sum(1 for d in dimension_results if d.status == "pass")
    failed = sum(1 for d in dimension_results if d.status == "fail")
    warned = sum(1 for d in dimension_results if d.status == "warn")
    not_applicable = sum(1 for d in dimension_results if d.status == "not_applicable")

    if failed > 0 and blocking_issue_ids:
        status: EvidenceConfirmGateStatus = "fail"
    elif warned > 0 and not blocking_issue_ids:
        status = "warn"
    elif not_applicable == len(dimension_results):
        status = "not_applicable"
    else:
        status = "pass"

    return EvidenceConfirmHardGate(
        status=status,
        blocking_issue_ids=blocking_issue_ids,
        reviewable_issue_ids=reviewable_issue_ids,
        informational_issue_ids=informational_issue_ids,
        passed_dimension_count=passed,
        failed_dimension_count=failed,
        warn_dimension_count=warned,
        not_applicable_dimension_count=not_applicable,
    )


def _aggregate_hard_gate(
    fact_results: tuple[EvidenceConfirmFactResultV2, ...],
) -> EvidenceConfirmHardGate:
    """计算聚合硬门控。

    Args:
        fact_results: fact V2 结果列表。

    Returns:
        聚合硬门控。

    Raises:
        无显式抛出。
    """

    if not fact_results:
        return EvidenceConfirmHardGate(
            status="not_applicable",
            blocking_issue_ids=(),
            reviewable_issue_ids=(),
            informational_issue_ids=(),
            passed_dimension_count=0,
            failed_dimension_count=0,
            warn_dimension_count=0,
            not_applicable_dimension_count=0,
        )

    all_blocking: list[str] = []
    all_reviewable: list[str] = []
    all_informational: list[str] = []
    for result in fact_results:
        all_blocking.extend(result.hard_gate.blocking_issue_ids)
        all_reviewable.extend(result.hard_gate.reviewable_issue_ids)
        all_informational.extend(result.hard_gate.informational_issue_ids)

    has_fail = any(r.status == "fail" for r in fact_results)
    has_warn = any(r.status == "warn" for r in fact_results)
    has_pass = any(r.status == "pass" for r in fact_results)
    all_not_applicable = all(r.status == "not_applicable" for r in fact_results)

    if has_fail:
        status: EvidenceConfirmGateStatus = "fail"
    elif has_warn:
        status = "warn"
    elif has_pass:
        status = "pass"
    elif all_not_applicable:
        status = "not_applicable"
    else:
        status = "not_applicable"

    return EvidenceConfirmHardGate(
        status=status,
        blocking_issue_ids=tuple(dict.fromkeys(all_blocking)),
        reviewable_issue_ids=tuple(dict.fromkeys(all_reviewable)),
        informational_issue_ids=tuple(dict.fromkeys(all_informational)),
        passed_dimension_count=sum(r.hard_gate.passed_dimension_count for r in fact_results),
        failed_dimension_count=sum(r.hard_gate.failed_dimension_count for r in fact_results),
        warn_dimension_count=sum(r.hard_gate.warn_dimension_count for r in fact_results),
        not_applicable_dimension_count=sum(r.hard_gate.not_applicable_dimension_count for r in fact_results),
    )


def _all_matched_anchor_ids(
    dimension_results: list[EvidenceConfirmDimensionResult],
) -> tuple[str, ...]:
    """从所有维度结果收集 matched_anchor_ids。

    Args:
        dimension_results: 维度结果列表。

    Returns:
        去重 matched anchor ids。

    Raises:
        无显式抛出。
    """

    all_ids: list[str] = []
    for dim in dimension_results:
        all_ids.extend(dim.matched_anchor_ids)
    return tuple(dict.fromkeys(all_ids))


def _fact_score_v2(
    dimension_results: list[EvidenceConfirmDimensionResult],
    hard_gate: EvidenceConfirmHardGate,
) -> int | None:
    """计算 V2 fact 可审计性分数，含阻塞失败上限。

    Args:
        dimension_results: 维度结果。
        hard_gate: fact 硬门控。

    Returns:
        fact 分数；全 not_applicable 时为 ``None``。

    Raises:
        无显式抛出。
    """

    scores = [d.score for d in dimension_results if d.score is not None]
    if not scores:
        return None

    raw_average = round(sum(scores) / len(scores))

    if hard_gate.status == "fail":
        blocking_fail_scores = [
            d.score
            for d in dimension_results
            if d.status == "fail" and d.score is not None and any(
                issue_id in hard_gate.blocking_issue_ids for issue_id in d.issue_ids
            )
        ]
        if blocking_fail_scores:
            return min(blocking_fail_scores)

    return raw_average


def _aggregate_score_v2(
    fact_results: tuple[EvidenceConfirmFactResultV2, ...],
    aggregate_hard_gate: EvidenceConfirmHardGate,
) -> int | None:
    """计算 V2 聚合可审计性分数，含聚合阻塞失败上限。

    Args:
        fact_results: fact V2 结果列表。
        aggregate_hard_gate: 聚合硬门控。

    Returns:
        聚合分数；无 fact 有 numeric score 时为 ``None``。

    Raises:
        无显式抛出。
    """

    scores = tuple(r.auditability_score for r in fact_results if r.auditability_score is not None)
    if not scores:
        return None

    raw_average = round(sum(scores) / len(scores))

    if aggregate_hard_gate.status == "fail":
        failing_scores = [
            r.auditability_score
            for r in fact_results
            if r.status == "fail" and r.auditability_score is not None
        ]
        if failing_scores:
            return min(failing_scores)

    return raw_average


def _confirm_fact(
    fact: ChapterFactEntry,
    references_by_anchor: dict[str, tuple[EvidenceConfirmReference, ...]],
    anchors_by_id: dict[str, ChapterEvidenceAnchor],
    report_year: int,
    projection: ChapterFactProjection | None = None,
) -> tuple[EvidenceConfirmFactResult, tuple[EvidenceConfirmIssue, ...]]:
    """复核单个 fact。

    Args:
        fact: 章节事实。
        references_by_anchor: anchor id 到引用摘录的映射。
        anchors_by_id: anchor id 到章节证据锚点的映射。
        report_year: 当前报告年份。

    Returns:
        单 fact result 与 issue 列表。

    Raises:
        无显式抛出。
    """

    if _fact_is_not_applicable(fact):
        return _fact_result(fact, "not_applicable", (), (), None), ()

    issues: list[EvidenceConfirmIssue] = []
    if fact.missing_reason == "evidence_missing":
        issue = _issue("E3", "blocking", fact, None, "缺锚点 fact 不能被证据复核确认。")
        return _fact_result(fact, "fail", (), (issue.issue_id,), 0), (issue,)

    if fact.status != "available":
        return _fact_result(fact, "not_applicable", (), (), None), ()

    if _fact_is_derived(fact):
        derived_issues = _derived_dependency_provenance_issues(fact, projection)
        if derived_issues:
            return _fact_result(
                fact,
                "fail",
                (),
                tuple(issue.issue_id for issue in derived_issues),
                0,
            ), derived_issues
        return _fact_result(fact, "not_applicable", (), (), None), ()

    if not fact.evidence_anchor_ids:
        issue = _issue("E3", "blocking", fact, None, "可用 fact 缺少 evidence anchor。")
        return _fact_result(fact, "fail", (), (issue.issue_id,), 0), (issue,)

    dangling_anchor_ids = _dangling_anchor_ids_for_fact(fact, anchors_by_id)
    known_anchors = _known_anchors_for_fact(fact, anchors_by_id)
    if not known_anchors:
        dangling_issues = _dangling_anchor_issues_for_fact(fact, dangling_anchor_ids)
        return _fact_result(
            fact,
            "fail",
            (),
            tuple(issue.issue_id for issue in dangling_issues),
            0,
        ), dangling_issues
    if dangling_anchor_ids:
        dangling_issues = _dangling_anchor_issues_for_fact(fact, dangling_anchor_ids)
        return _fact_result(
            fact,
            "fail",
            (),
            tuple(issue.issue_id for issue in dangling_issues),
            0,
        ), dangling_issues

    if not any(anchor.source_kind in _PROOF_SOURCE_KINDS for anchor in known_anchors):
        return _fact_result(fact, "not_applicable", (), (), None), ()

    proof_references = _proof_references_for_fact(fact, references_by_anchor, anchors_by_id, report_year)
    if not proof_references:
        issue = _issue("E3", "blocking", fact, None, "fact 没有可确认的 proven reference excerpt。")
        return _fact_result(fact, "fail", (), (issue.issue_id,), 0), (issue,)

    for reference in proof_references:
        precision_issue = _precision_issue(fact, reference)
        if precision_issue is not None:
            issues.append(precision_issue)

    material_value = _resolved_fact_material_value(projection, fact)
    if material_value is _UNRESOLVED_FACT_MATERIAL:
        issue = _issue("E3", "blocking", fact, None, "bridge fact 无法解析 material value。")
        issues.append(issue)
        return _fact_result(fact, "fail", (), _issue_ids(issues), 0), tuple(issues)

    tokens = _material_tokens(material_value)
    if not tokens:
        if _fact_is_required(fact):
            issue = _issue("E3", "blocking", fact, None, "required fact 无可复核 material value token。")
            issues.append(issue)
            return _fact_result(fact, "fail", (), _issue_ids(issues), 0), tuple(issues)
        return _fact_result(fact, "not_applicable", (), _issue_ids(issues), None), tuple(issues)

    matched_anchor_ids = _matched_anchor_ids(tokens, proof_references)
    if not matched_anchor_ids:
        issues.append(
            _issue(
                "E2",
                "blocking",
                fact,
                None,
                "fact value 未出现在同一 anchor 的 reference excerpt 中。",
            )
        )
        return _fact_result(fact, "fail", (), _issue_ids(issues), 40), tuple(issues)

    status: EvidenceConfirmStatus = "warn" if issues else "pass"
    score = 70 if issues else 100
    return _fact_result(fact, status, matched_anchor_ids, _issue_ids(issues), score), tuple(issues)


def _references_by_anchor(
    references: tuple[EvidenceConfirmReference, ...],
) -> dict[str, tuple[EvidenceConfirmReference, ...]]:
    """按 anchor id 分组引用摘录。

    Args:
        references: 引用摘录。

    Returns:
        anchor id 到引用摘录元组的映射。

    Raises:
        无显式抛出。
    """

    grouped: dict[str, list[EvidenceConfirmReference]] = {}
    for reference in references:
        grouped.setdefault(reference.anchor_id, []).append(reference)
    return {key: tuple(value) for key, value in grouped.items()}


def _anchors_by_id(
    anchors: tuple[ChapterEvidenceAnchor, ...],
) -> dict[str, ChapterEvidenceAnchor]:
    """按 anchor id 索引章节证据锚点。

    Args:
        anchors: 章节证据锚点。

    Returns:
        anchor id 到章节证据锚点的映射。

    Raises:
        无显式抛出。
    """

    return {anchor.anchor_id: anchor for anchor in anchors}


def _proof_references_for_fact(
    fact: ChapterFactEntry,
    references_by_anchor: dict[str, tuple[EvidenceConfirmReference, ...]],
    anchors_by_id: dict[str, ChapterEvidenceAnchor],
    report_year: int,
) -> tuple[EvidenceConfirmReference, ...]:
    """读取 fact 自身 anchor id 对应的 proven references。

    Args:
        fact: 章节事实。
        references_by_anchor: anchor id 到引用摘录的映射。
        anchors_by_id: anchor id 到章节证据锚点的映射。
        report_year: 当前报告年份。

    Returns:
        proven reference 列表。

    Raises:
        无显式抛出。
    """

    references: list[EvidenceConfirmReference] = []
    for anchor_id in fact.evidence_anchor_ids:
        anchor = anchors_by_id.get(anchor_id)
        if anchor is None:
            continue
        for reference in references_by_anchor.get(anchor_id, ()):
            if _reference_is_proof(reference, anchor, report_year):
                references.append(reference)
    return tuple(references)


def _known_anchors_for_fact(
    fact: ChapterFactEntry,
    anchors_by_id: dict[str, ChapterEvidenceAnchor],
) -> tuple[ChapterEvidenceAnchor, ...]:
    """读取 fact 当前章节内存在的 anchors。

    Args:
        fact: 章节事实。
        anchors_by_id: anchor id 到章节证据锚点的映射。

    Returns:
        当前章节内存在的 anchors。

    Raises:
        无显式抛出。
    """

    return tuple(
        anchor
        for anchor_id in fact.evidence_anchor_ids
        if (anchor := anchors_by_id.get(anchor_id)) is not None
    )


def _dangling_anchor_ids_for_fact(
    fact: ChapterFactEntry,
    anchors_by_id: dict[str, ChapterEvidenceAnchor],
) -> tuple[str, ...]:
    """读取 fact 声明但当前章节不存在的 anchor ids。

    Args:
        fact: 章节事实。
        anchors_by_id: anchor id 到章节证据锚点的映射。

    Returns:
        当前章节内不存在的 anchor ids。

    Raises:
        无显式抛出。
    """

    return tuple(anchor_id for anchor_id in fact.evidence_anchor_ids if anchor_id not in anchors_by_id)


def _dangling_anchor_issues_for_fact(
    fact: ChapterFactEntry,
    dangling_anchor_ids: tuple[str, ...],
) -> tuple[EvidenceConfirmIssue, ...]:
    """构造 fact 悬挂 anchor 的 E3 blocking issues。

    Args:
        fact: 章节事实。
        dangling_anchor_ids: fact 声明但当前章节不存在的 anchor ids。

    Returns:
        每个悬挂 anchor 对应一个 E3 blocking issue。

    Raises:
        无显式抛出。
    """

    return tuple(
        _issue(
            "E3",
            "blocking",
            fact,
            anchor_id,
            "missing_evidence fact anchor 不存在于当前章节 evidence anchors。",
        )
        for anchor_id in dangling_anchor_ids
    )


def _reference_is_proof(
    reference: EvidenceConfirmReference,
    anchor: ChapterEvidenceAnchor,
    report_year: int,
) -> bool:
    """判断引用摘录是否满足 phase 1 proof predicate。

    Args:
        reference: 引用摘录。
        anchor: 当前章节中同 id 的证据锚点。
        report_year: 当前报告年份。

    Returns:
        满足闭集 proof predicate 时返回 ``True``。

    Raises:
        无显式抛出。
    """

    return (
        not reference.candidate_only
        and reference.source_truth_status == "proven"
        and reference.source_kind in _PROOF_SOURCE_KINDS
        and _REFERENCE_SOURCE_KIND_PAIRS.get(reference.reference_kind) == reference.source_kind
        and _reference_matches_anchor(reference, anchor, report_year)
    )


def _reference_matches_anchor(
    reference: EvidenceConfirmReference,
    anchor: ChapterEvidenceAnchor,
    report_year: int,
) -> bool:
    """判断 reference 是否与当前章节 anchor 的来源身份相容。

    Args:
        reference: 引用摘录。
        anchor: 当前章节中同 id 的证据锚点。
        report_year: 当前报告年份。

    Returns:
        来源类型、年份和显式 locator 不矛盾时返回 ``True``。

    Raises:
        无显式抛出。
    """

    if anchor.source_kind != reference.source_kind:
        return False
    if report_year and reference.document_year is not None and reference.document_year != report_year:
        return False
    if (
        anchor.document_year is not None
        and reference.document_year is not None
        and anchor.document_year != reference.document_year
    ):
        return False
    if anchor.section_id and reference.section_id and anchor.section_id != reference.section_id:
        return False
    if (
        anchor.page_number is not None
        and reference.page_number is not None
        and anchor.page_number != reference.page_number
    ):
        return False
    if anchor.table_id and reference.table_id and anchor.table_id != reference.table_id:
        return False
    if anchor.row_locator and reference.row_locator and anchor.row_locator != reference.row_locator:
        return False
    return True


def _precision_issue(
    fact: ChapterFactEntry,
    reference: EvidenceConfirmReference,
    anchors_by_id: dict[str, ChapterEvidenceAnchor] | None = None,
) -> EvidenceConfirmIssue | None:
    """检查 reference anchor 精度。

    Args:
        fact: 章节事实。
        reference: 引用摘录。
        anchors_by_id: anchor id 到章节证据锚点的映射；为空时仅检查 reference 自身定位。

    Returns:
        精度 issue；无问题时返回 ``None``。

    Raises:
        无显式抛出。
    """

    if reference.reference_kind == "derived_calculation":
        return None
    if not reference.excerpt_text.strip():
        return _issue("E1", "reviewable", fact, reference.anchor_id, "reference excerpt 为空。")
    if reference.reference_kind == "reviewed_note":
        if reference.section_id or reference.row_locator:
            return None
        return _issue("E1", "reviewable", fact, reference.anchor_id, "reviewed note 缺少可复核定位。")
    anchor = anchors_by_id.get(reference.anchor_id) if anchors_by_id is not None else None
    if anchor is not None and anchor.row_locator and reference.row_locator is None:
        return _issue(
            "E1",
            "reviewable",
            fact,
            reference.anchor_id,
            "annual_report anchor 声明 row_locator，但 reference 已降级为非行级定位。",
        )
    if not reference.section_id:
        return _issue("E1", "reviewable", fact, reference.anchor_id, "annual_report excerpt 缺少 section_id。")
    if reference.page_number is None and not reference.table_id and not reference.row_locator:
        return _issue("E1", "reviewable", fact, reference.anchor_id, "annual_report excerpt 缺少页码、表格或行级定位。")
    return None


def _matched_anchor_ids(
    tokens: tuple[str, ...],
    references: tuple[EvidenceConfirmReference, ...],
) -> tuple[str, ...]:
    """返回与 material token 匹配的 anchor ids。

    Args:
        tokens: 已归一化 material tokens。
        references: proven references。

    Returns:
        匹配的 anchor ids。

    Raises:
        无显式抛出。
    """

    matched: list[str] = []
    for reference in references:
        normalized_excerpt = _normalize_text(reference.excerpt_text)
        if any(_token_matches_excerpt(token, normalized_excerpt) for token in tokens):
            matched.append(reference.anchor_id)
    return tuple(dict.fromkeys(matched))


def _token_matches_excerpt(token: str, normalized_excerpt: str) -> bool:
    """判断 material token 是否在摘录中可复核命中。

    Args:
        token: 已归一化 material token。
        normalized_excerpt: 已归一化 reference excerpt。

    Returns:
        token 可在摘录中保守命中时返回 ``True``。

    Raises:
        无显式抛出。
    """

    if _NUMERIC_TOKEN_RE.fullmatch(token):
        return _numeric_token_matches_excerpt(token, normalized_excerpt)
    return token in normalized_excerpt


def _numeric_token_matches_excerpt(token: str, normalized_excerpt: str) -> bool:
    """按数值边界和小数等价匹配 numeric token。

    Args:
        token: 已归一化 numeric token。
        normalized_excerpt: 已归一化 reference excerpt。

    Returns:
        数值候选在边界和单位上相容时返回 ``True``。

    Raises:
        无显式抛出。
    """

    token_has_percent = token.endswith("%")
    token_decimal = _decimal_from_numeric_token(token)
    if token_decimal is None:
        return False
    for match in _NUMERIC_CANDIDATE_RE.finditer(normalized_excerpt):
        candidate = match.group(0)
        if candidate.endswith("%") != token_has_percent:
            continue
        candidate_decimal = _decimal_from_numeric_token(candidate)
        if candidate_decimal is not None and candidate_decimal == token_decimal:
            return True
    return False


def _decimal_from_numeric_token(token: str) -> Decimal | None:
    """从 numeric token 读取 Decimal。

    Args:
        token: 已归一化 numeric token。

    Returns:
        Decimal 值；无法解析时返回 ``None``。

    Raises:
        无显式抛出。
    """

    try:
        return Decimal(token.rstrip("%"))
    except InvalidOperation:
        return None


def _material_tokens(value: object | None) -> tuple[str, ...]:
    """从 fact value 提取可复核 material token。

    Args:
        value: 结构化 fact value。

    Returns:
        归一化 token 元组。

    Raises:
        无显式抛出。
    """

    tokens = tuple(_normalize_text(str(item)) for item in _flatten_material_values(value))
    return tuple(token for token in dict.fromkeys(tokens) if token)


def _resolved_fact_material_value(
    projection: ChapterFactProjection | None,
    fact: ChapterFactEntry,
) -> object | None | _UnresolvedFactMaterial:
    """通过 S4 bridge id 解析 Evidence Confirm material value。

    Args:
        projection: 章节事实投影；为空时保持 legacy `fact.value` 语义。
        fact: 当前章节事实。

    Returns:
        bridge 存在时返回 atomic 单值或 derived view 值；bridge 缺失时返回
        `_UNRESOLVED_FACT_MATERIAL`；legacy fact 返回 `fact.value`。

    Raises:
        无显式抛出。
    """

    if projection is None:
        return fact.value
    if fact.source_fact_ids and fact.derived_view_id is not None:
        return _UNRESOLVED_FACT_MATERIAL
    if fact.source_fact_ids:
        if len(fact.source_fact_ids) != 1:
            return _UNRESOLVED_FACT_MATERIAL
        source_fact = projection.source_facts.get_optional(fact.source_fact_ids[0])
        if source_fact is None:
            return _UNRESOLVED_FACT_MATERIAL
        return source_fact.value
    if fact.derived_view_id is not None:
        derived_view = _derived_view_for_fact(projection, fact)
        if derived_view is None:
            return _UNRESOLVED_FACT_MATERIAL
        return derived_view.value
    return fact.value


def _resolved_fact_material_tokens(
    projection: ChapterFactProjection | None,
    fact: ChapterFactEntry,
) -> tuple[str, ...] | _UnresolvedFactMaterial:
    """解析 fact 的 Evidence Confirm material tokens。

    Args:
        projection: 章节事实投影；为空时保持 legacy `fact.value` 语义。
        fact: 当前章节事实。

    Returns:
        material tokens；bridge 缺失时返回 `_UNRESOLVED_FACT_MATERIAL`。

    Raises:
        无显式抛出。
    """

    material_value = _resolved_fact_material_value(projection, fact)
    if material_value is _UNRESOLVED_FACT_MATERIAL:
        return _UNRESOLVED_FACT_MATERIAL
    return _material_tokens(material_value)


def _derived_dependency_provenance_issues(
    fact: ChapterFactEntry,
    projection: ChapterFactProjection | None,
) -> tuple[EvidenceConfirmIssue, ...]:
    """校验 derived view 的 child atomic facts 是否具备 section-or-better provenance。

    Args:
        fact: 当前章节事实。
        projection: 章节事实投影。

    Returns:
        provenance 缺失对应的 E3 blocking issues；非 bridge derived fact 返回空。

    Raises:
        无显式抛出。
    """

    if projection is None or fact.derived_view_id is None:
        return ()
    derived_view = _derived_view_for_fact(projection, fact)
    if derived_view is None:
        return (_issue("E3", "blocking", fact, None, "derived_view_id 未在 projection.derived_views 中解析。"),)

    issues: list[EvidenceConfirmIssue] = []
    for dependency_fact_id in derived_view.dependency_fact_ids:
        source_fact = projection.source_facts.get_optional(dependency_fact_id)
        if source_fact is None:
            issues.append(
                _issue(
                    "E3",
                    "blocking",
                    fact,
                    None,
                    f"derived view 依赖的 atomic fact 缺失: {dependency_fact_id}。",
                )
            )
            continue
        if not _source_fact_has_section_or_better_provenance(source_fact):
            issues.append(
                _issue(
                    "E3",
                    "blocking",
                    fact,
                    None,
                    f"derived view 依赖的 atomic fact 缺少 section-or-better provenance: {dependency_fact_id}。",
                )
            )
    return tuple(issues)


def _derived_view_for_fact(
    projection: ChapterFactProjection,
    fact: ChapterFactEntry,
) -> CompositeAnalysisView | None:
    """按 `derived_view_id` 唯一读取 projection derived view。

    Args:
        projection: 章节事实投影。
        fact: 当前章节事实。

    Returns:
        exactly one 匹配的 derived view；无匹配或重复匹配时返回 ``None``。

    Raises:
        无显式抛出。
    """

    matched_views = tuple(
        view for view in projection.derived_views if view.view_id == fact.derived_view_id
    )
    if len(matched_views) != 1:
        return None
    return matched_views[0]


def _source_fact_has_section_or_better_provenance(source_fact: AtomicSourceFact) -> bool:
    """判断 atomic child fact 是否具备 section-or-better provenance。

    Args:
        source_fact: atomic source fact。

    Returns:
        存在可复核来源锚点时返回 ``True``。annual_report 锚点必须至少有
        section_id；derived 锚点只要求存在，external_api 不用于当前 annual
        report proof。

    Raises:
        无显式抛出。
    """

    for anchor in source_fact.anchors:
        if anchor.source_kind == "annual_report" and anchor.section_id:
            return True
        if anchor.source_kind == "derived":
            return True
    return False


def _flatten_material_values(value: object | None) -> tuple[object, ...]:
    """递归展开结构化值中的 material scalar。

    Args:
        value: 任意结构化值。

    Returns:
        material scalar 元组。

    Raises:
        无显式抛出。
    """

    if value is None:
        return ()
    if isinstance(value, bool):
        return (value,)
    if isinstance(value, (str, int, float, Decimal)):
        return (value,)
    if is_dataclass(value) and not isinstance(value, type):
        return _flatten_material_values(asdict(value))
    if isinstance(value, dict):
        flattened: list[object] = []
        for key in sorted(value):
            if str(key) in _IGNORED_VALUE_KEYS:
                continue
            flattened.extend(_flatten_material_values(value[key]))
        return tuple(flattened)
    if isinstance(value, (tuple, list)):
        flattened = []
        for item in value:
            flattened.extend(_flatten_material_values(item))
        return tuple(flattened)
    return ()


def _normalize_text(value: str) -> str:
    """归一化文本以支持保守同源匹配。

    Args:
        value: 原始文本。

    Returns:
        归一化文本。

    Raises:
        无显式抛出。
    """

    text = unicodedata.normalize("NFKC", value).casefold()
    text = text.replace("％", "%")
    text = _PUNCTUATION_RE.sub("", text)
    text = _WHITESPACE_RE.sub("", text)
    return text.strip()


def _fact_is_not_applicable(fact: ChapterFactEntry) -> bool:
    """判断 fact 是否不适用。

    Args:
        fact: 章节事实。

    Returns:
        不适用时返回 ``True``。

    Raises:
        无显式抛出。
    """

    return fact.status == "not_applicable" or fact.missing_reason == "field_not_applicable"


def _fact_is_derived(fact: ChapterFactEntry) -> bool:
    """判断 fact 是否为 derived/synthetic 来源。

    Args:
        fact: 章节事实。

    Returns:
        derived/synthetic fact 返回 ``True``。

    Raises:
        无显式抛出。
    """

    return fact.source_field_id.startswith("synthetic.") or fact.extraction_mode == "derived"


def _fact_is_required(fact: ChapterFactEntry) -> bool:
    """判断 fact 是否支撑模板 requirement。

    Args:
        fact: 章节事实。

    Returns:
        有 required_by 时返回 ``True``。

    Raises:
        无显式抛出。
    """

    return bool(fact.required_by)


def _fact_result(
    fact: ChapterFactEntry,
    status: EvidenceConfirmStatus,
    matched_anchor_ids: tuple[str, ...],
    issue_ids: tuple[str, ...],
    score: int | None,
) -> EvidenceConfirmFactResult:
    """构造单 fact result。

    Args:
        fact: 章节事实。
        status: 复核状态。
        matched_anchor_ids: 匹配 anchor ids。
        issue_ids: issue ids。
        score: 可审计性分数。

    Returns:
        单 fact result。

    Raises:
        无显式抛出。
    """

    return EvidenceConfirmFactResult(
        fact_id=fact.fact_id,
        source_field_id=fact.source_field_id,
        status=status,
        matched_anchor_ids=matched_anchor_ids,
        issue_ids=issue_ids,
        auditability_score=score,
    )


def _issue(
    rule_code: EvidenceConfirmRuleCode,
    severity: EvidenceConfirmSeverity,
    fact: ChapterFactEntry,
    anchor_id: str | None,
    message: str,
) -> EvidenceConfirmIssue:
    """构造稳定 issue。

    Args:
        rule_code: E1/E2/E3 规则码。
        severity: 严重程度。
        fact: 章节事实。
        anchor_id: 关联 anchor id。
        message: 问题说明。

    Returns:
        Evidence Confirm issue。

    Raises:
        无显式抛出。
    """

    digest = hashlib.sha1(
        "|".join((rule_code, fact.fact_id, fact.source_field_id, anchor_id or "none", message)).encode(
            "utf-8"
        )
    ).hexdigest()[:12]
    return EvidenceConfirmIssue(
        issue_id=f"evidence-confirm:{rule_code.lower()}:{digest}",
        rule_code=rule_code,
        severity=severity,
        fact_id=fact.fact_id,
        source_field_id=fact.source_field_id,
        anchor_id=anchor_id,
        message=message,
    )


def _issue_ids(issues: list[EvidenceConfirmIssue]) -> tuple[str, ...]:
    """提取 issue ids。

    Args:
        issues: issue 列表。

    Returns:
        issue id 元组。

    Raises:
        无显式抛出。
    """

    return tuple(issue.issue_id for issue in issues)


def _overall_status(
    issues: tuple[EvidenceConfirmIssue, ...],
    fact_results: tuple[EvidenceConfirmFactResult, ...],
) -> EvidenceConfirmStatus:
    """计算聚合状态。

    Args:
        issues: issue 列表。
        fact_results: fact result 列表。

    Returns:
        聚合状态。

    Raises:
        无显式抛出。
    """

    if any(issue.severity == "blocking" for issue in issues):
        return "fail"
    if any(issue.severity == "reviewable" for issue in issues):
        return "warn"
    if not any(result.auditability_score is not None for result in fact_results):
        return "not_applicable"
    return "pass"


def _aggregate_score(fact_results: tuple[EvidenceConfirmFactResult, ...]) -> int | None:
    """计算聚合分数。

    Args:
        fact_results: fact result 列表。

    Returns:
        平均分；无可计分 fact 时返回 ``None``。

    Raises:
        无显式抛出。
    """

    scores = tuple(result.auditability_score for result in fact_results if result.auditability_score is not None)
    if not scores:
        return None
    return round(sum(scores) / len(scores))


def _fund_code_from_facts(facts: tuple[ChapterFactEntry, ...]) -> str:
    """从 fact id 中保守读取基金代码。

    Args:
        facts: 章节事实。

    Returns:
        基金代码；无法读取时为 ``unknown``。

    Raises:
        无显式抛出。
    """

    for fact in facts:
        parts = fact.fact_id.split(":")
        if len(parts) >= 3:
            return parts[1]
    return "unknown"


def _report_year_from_facts(facts: tuple[ChapterFactEntry, ...]) -> int:
    """从 fact id 中保守读取报告年份。

    Args:
        facts: 章节事实。

    Returns:
        报告年份；无法读取时为 ``0``。

    Raises:
        无显式抛出。
    """

    for fact in facts:
        parts = fact.fact_id.split(":")
        if len(parts) >= 4 and parts[2].isdigit():
            return int(parts[2])
    return 0


def _report_year_from_references(references: tuple[EvidenceConfirmReference, ...]) -> int:
    """从 references 中读取报告年份。

    Args:
        references: 引用摘录。

    Returns:
        首个非空年份；缺失时返回 ``0``。

    Raises:
        无显式抛出。
    """

    for reference in references:
        if reference.document_year is not None:
            return reference.document_year
    return 0
