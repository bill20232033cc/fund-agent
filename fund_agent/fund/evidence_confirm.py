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

EVIDENCE_CONFIRM_SCHEMA_VERSION: Final[str] = "evidence_confirm.v1"

EvidenceConfirmRuleCode: TypeAlias = Literal["E1", "E2", "E3"]
EvidenceConfirmStatus: TypeAlias = Literal["pass", "warn", "fail", "not_applicable"]
EvidenceConfirmSeverity: TypeAlias = Literal["blocking", "reviewable", "informational"]
EvidenceConfirmReferenceKind: TypeAlias = Literal[
    "annual_report_excerpt",
    "reviewed_note",
    "derived_calculation",
]
EvidenceConfirmSourceTruthStatus: TypeAlias = Literal["proven", "not_proven"]

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


def _confirm_fact(
    fact: ChapterFactEntry,
    references_by_anchor: dict[str, tuple[EvidenceConfirmReference, ...]],
    anchors_by_id: dict[str, ChapterEvidenceAnchor],
    report_year: int,
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
        return _fact_result(fact, "not_applicable", (), (), None), ()

    if not fact.evidence_anchor_ids:
        issue = _issue("E3", "blocking", fact, None, "可用 fact 缺少 evidence anchor。")
        return _fact_result(fact, "fail", (), (issue.issue_id,), 0), (issue,)

    known_anchors = _known_anchors_for_fact(fact, anchors_by_id)
    if not known_anchors:
        issue = _issue("E3", "blocking", fact, None, "fact anchor 不存在于当前章节 evidence anchors。")
        return _fact_result(fact, "fail", (), (issue.issue_id,), 0), (issue,)

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

    tokens = _material_tokens(fact.value)
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
) -> EvidenceConfirmIssue | None:
    """检查 reference anchor 精度。

    Args:
        fact: 章节事实。
        reference: 引用摘录。

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
