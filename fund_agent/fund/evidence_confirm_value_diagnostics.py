"""Evidence Confirm V2 value-match 安全诊断，见基金分析模板第 0-7 章。

本模块属于 Agent 层 ``fund_agent/fund`` 基金领域能力，只消费调用方显式
传入的章节事实投影、同源引用摘录和 V2 复核结果。它不读取年报仓库、PDF/cache、
source helper、Service、Host、provider、CLI、renderer 或文件系统。
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, is_dataclass
from decimal import Decimal
from typing import Final, Literal, TypeAlias

from fund_agent.fund.chapter_facts import ChapterFactEntry, ChapterFactProjection
from fund_agent.fund.evidence_confirm import (
    EvidenceConfirmFactResultV2,
    EvidenceConfirmReference,
    EvidenceConfirmResultV2,
    _anchors_by_id,
    _fact_is_derived,
    _fact_is_not_applicable,
    _IGNORED_VALUE_KEYS,
    _normalize_text,
    _proof_references_for_fact,
    _references_by_anchor,
    _resolved_fact_material_tokens,
    _UNRESOLVED_FACT_MATERIAL,
    _token_matches_excerpt,
)

VALUE_MATCH_DIAGNOSTIC_SCHEMA_VERSION: Final[
    Literal["evidence_confirm_value_diagnostic.v1"]
] = "evidence_confirm_value_diagnostic.v1"
MATCH_SOURCE: Final[Literal["deterministic_v2_same_source_primitives"]] = (
    "deterministic_v2_same_source_primitives"
)

ValueDiagnosticClassification: TypeAlias = Literal[
    "value_shape_overbroad",
    "matcher_normalization_gap",
    "coarse_reference_insufficient",
    "anchor_attachment_mismatch",
    "extractor_value_or_anchor_defect",
    "bond_risk_group_anchor_projection_gap",
    "undetermined_requires_live_excerpt_review",
    "not_applicable",
]
ValueTokenCategory: TypeAlias = Literal[
    "numeric_percent",
    "numeric_plain",
    "boolean",
    "short_text",
    "long_text",
    "empty",
]
ReferenceGranularity: TypeAlias = Literal[
    "section_level",
    "table_level",
    "row_level",
    "derived_or_reviewed_note",
]


@dataclass(frozen=True, slots=True)
class EvidenceConfirmValueDiagnosticRecord:
    """单个 fact 的 value-match 安全诊断记录。

    Attributes:
        fact_id: 章节事实 ID。
        source_field_id: 来源字段 ID。
        chapter_id: 模板章节编号。
        fact_status: V2 fact 状态。
        failing_dimensions: 当前 fact 的失败维度。
        warning_dimensions: 当前 fact 的警告维度。
        anchor_count: fact 声明的 anchor 数。
        reference_count: fact anchor 对应的全部 reference 数。
        proof_reference_count: 满足 V2 proof predicate 的 reference 数。
        token_count: V2 material token 数。
        matched_token_category_counts: 已匹配 token 的安全类别计数。
        unmatched_token_category_counts: 未匹配 token 的安全类别计数。
        unmatched_value_paths: 未匹配 token 对应的结构化路径，不含原始值。
        reference_granularity_counts: proof reference 粒度计数。
        locator_downgraded: 是否存在 anchor row locator 被降级成非行级 reference。
        classification: 诊断分类。
        token_match_source: token/match 来源，固定声明复用 V2 primitives。
    """

    fact_id: str
    source_field_id: str
    chapter_id: int
    fact_status: str
    failing_dimensions: tuple[str, ...]
    warning_dimensions: tuple[str, ...]
    anchor_count: int
    reference_count: int
    proof_reference_count: int
    token_count: int
    matched_token_category_counts: dict[str, int]
    unmatched_token_category_counts: dict[str, int]
    unmatched_value_paths: tuple[str, ...]
    reference_granularity_counts: dict[str, int]
    locator_downgraded: bool
    classification: ValueDiagnosticClassification
    token_match_source: Literal["deterministic_v2_same_source_primitives"] = MATCH_SOURCE


@dataclass(frozen=True, slots=True)
class EvidenceConfirmValueDiagnosticSummary:
    """Evidence Confirm value-match 安全诊断摘要。

    Attributes:
        schema_version: 诊断 schema 版本。
        fund_code: 基金代码。
        report_year: 年报年份。
        token_match_source: token/match 来源。
        record_count: 诊断记录数量。
        records: 逐 fact 安全诊断记录。
        classification_counts: 诊断分类计数。
    """

    schema_version: Literal["evidence_confirm_value_diagnostic.v1"]
    fund_code: str
    report_year: int
    token_match_source: Literal["deterministic_v2_same_source_primitives"]
    record_count: int
    records: tuple[EvidenceConfirmValueDiagnosticRecord, ...]
    classification_counts: dict[str, int]

    def to_safe_dict(self) -> dict[str, object]:
        """返回只含安全标量、稳定 ID 和结构路径的字典。

        Returns:
            JSON 兼容字典，不包含原始 excerpt、PDF/cache 路径、URL、provider
            payload 或原始 token value。

        Raises:
            无显式抛出。
        """

        return asdict(self)


def summarize_value_match_diagnostics(
    *,
    projection: ChapterFactProjection,
    references: tuple[EvidenceConfirmReference, ...],
    result: EvidenceConfirmResultV2,
) -> EvidenceConfirmValueDiagnosticSummary:
    """生成 Evidence Confirm V2 value-match 安全诊断。

    Args:
        projection: 已投影的章节事实。
        references: 同源引用摘录。
        result: V2 Evidence Confirm 结果。

    Returns:
        安全诊断摘要。

    Raises:
        无显式抛出。
    """

    references_by_anchor = _references_by_anchor(references)
    fact_results_by_id = {fact.fact_id: fact for fact in result.fact_results}
    records: list[EvidenceConfirmValueDiagnosticRecord] = []
    for chapter in sorted(projection.chapters, key=lambda item: item.chapter_id):
        anchors_by_id = _anchors_by_id(chapter.evidence_anchors)
        for fact in sorted(chapter.facts, key=lambda item: (item.source_field_id, item.fact_id)):
            fact_result = fact_results_by_id.get(fact.fact_id)
            if fact_result is None:
                continue
            record = _record_for_fact(
                fact=fact,
                fact_result=fact_result,
                references_by_anchor=references_by_anchor,
                anchors_by_id=anchors_by_id,
                report_year=projection.report_year,
                projection=projection,
            )
            if record is not None:
                records.append(record)

    sorted_records = tuple(sorted(records, key=lambda item: (item.chapter_id, item.source_field_id, item.fact_id)))
    return EvidenceConfirmValueDiagnosticSummary(
        schema_version=VALUE_MATCH_DIAGNOSTIC_SCHEMA_VERSION,
        fund_code=projection.fund_code,
        report_year=projection.report_year,
        token_match_source=MATCH_SOURCE,
        record_count=len(sorted_records),
        records=sorted_records,
        classification_counts=_classification_counts(sorted_records),
    )


def _record_for_fact(
    *,
    fact: ChapterFactEntry,
    fact_result: EvidenceConfirmFactResultV2,
    references_by_anchor: dict[str, tuple[EvidenceConfirmReference, ...]],
    anchors_by_id: dict[str, object],
    report_year: int,
    projection: ChapterFactProjection,
) -> EvidenceConfirmValueDiagnosticRecord | None:
    """构造单个 fact 的安全诊断记录。

    Args:
        fact: 章节事实。
        fact_result: V2 fact 结果。
        references_by_anchor: anchor id 到 references 的映射。
        anchors_by_id: 当前章节 anchor id 映射。
        report_year: 年报年份。

    Returns:
        需要诊断时返回记录，否则返回 ``None``。

    Raises:
        无显式抛出。
    """

    value_status = _dimension_status(fact_result, "value_match")
    missing_status = _dimension_status(fact_result, "missing_evidence")
    if (
        value_status not in {"fail", "pass"}
        and not _has_proof_failure(fact_result)
        and not _is_bond_risk_missing_failure(fact, missing_status)
    ):
        return None

    proof_references = _proof_references_for_fact(
        fact,
        references_by_anchor,
        anchors_by_id,  # type: ignore[arg-type]
        report_year,
    )
    all_references = tuple(
        reference for anchor_id in fact.evidence_anchor_ids for reference in references_by_anchor.get(anchor_id, ())
    )
    tokens = _resolved_fact_material_tokens(projection, fact)
    if tokens is _UNRESOLVED_FACT_MATERIAL:
        tokens = ()
    matched_tokens, unmatched_tokens = _matched_and_unmatched_tokens(tokens, proof_references)
    failing_dimensions = tuple(
        dimension.dimension for dimension in fact_result.dimension_results if dimension.status == "fail"
    )
    warning_dimensions = tuple(
        dimension.dimension for dimension in fact_result.dimension_results if dimension.status == "warn"
    )
    locator_downgraded = _locator_downgraded(fact, proof_references, anchors_by_id)
    classification = _classify_record(
        fact=fact,
        fact_result=fact_result,
        all_references=all_references,
        proof_references=proof_references,
        tokens=tokens,
        unmatched_tokens=unmatched_tokens,
        value_status=value_status,
        missing_status=missing_status,
        locator_downgraded=locator_downgraded,
    )
    return EvidenceConfirmValueDiagnosticRecord(
        fact_id=fact.fact_id,
        source_field_id=fact.source_field_id,
        chapter_id=fact.chapter_id,
        fact_status=fact_result.status,
        failing_dimensions=failing_dimensions,
        warning_dimensions=warning_dimensions,
        anchor_count=len(fact.evidence_anchor_ids),
        reference_count=len(all_references),
        proof_reference_count=len(proof_references),
        token_count=len(tokens),
        matched_token_category_counts=_category_counts(matched_tokens),
        unmatched_token_category_counts=_category_counts(unmatched_tokens),
        unmatched_value_paths=_unmatched_value_paths(fact.value, unmatched_tokens),
        reference_granularity_counts=_reference_granularity_counts(proof_references),
        locator_downgraded=locator_downgraded,
        classification=classification,
    )


def _dimension_status(fact_result: EvidenceConfirmFactResultV2, dimension_name: str) -> str:
    """读取指定 V2 dimension 状态。

    Args:
        fact_result: V2 fact 结果。
        dimension_name: 维度名称。

    Returns:
        维度状态；不存在时返回 ``not_applicable``。

    Raises:
        无显式抛出。
    """

    for dimension in fact_result.dimension_results:
        if dimension.dimension == dimension_name:
            return dimension.status
    return "not_applicable"


def _has_proof_failure(fact_result: EvidenceConfirmFactResultV2) -> bool:
    """判断 fact 是否存在 proof/reference 相关失败。

    Args:
        fact_result: V2 fact 结果。

    Returns:
        source_support、missing_evidence 或 proof_boundary 失败时返回 ``True``。

    Raises:
        无显式抛出。
    """

    return any(
        dimension.dimension in {"source_support", "missing_evidence", "proof_boundary"}
        and dimension.status == "fail"
        for dimension in fact_result.dimension_results
    )


def _matched_and_unmatched_tokens(
    tokens: tuple[str, ...],
    proof_references: tuple[EvidenceConfirmReference, ...],
) -> tuple[tuple[str, ...], tuple[str, ...]]:
    """用 V2 token matcher 区分已匹配和未匹配 token。

    Args:
        tokens: V2 material tokens。
        proof_references: V2 proof references。

    Returns:
        已匹配 token 与未匹配 token。

    Raises:
        无显式抛出。
    """

    matched: list[str] = []
    unmatched: list[str] = []
    normalized_excerpts = tuple(_normalize_text(reference.excerpt_text) for reference in proof_references)
    for token in tokens:
        if any(_token_matches_excerpt(token, excerpt) for excerpt in normalized_excerpts):
            matched.append(token)
        else:
            unmatched.append(token)
    return tuple(matched), tuple(unmatched)


def _category_counts(tokens: tuple[str, ...]) -> dict[str, int]:
    """统计 token 安全类别。

    Args:
        tokens: V2 material tokens。

    Returns:
        类别到数量的稳定 dict。

    Raises:
        无显式抛出。
    """

    counts: dict[str, int] = {}
    for token in tokens:
        category = _token_category(token)
        counts[category] = counts.get(category, 0) + 1
    return dict(sorted(counts.items()))


def _token_category(token: str) -> ValueTokenCategory:
    """把 V2 token 映射为安全类别。

    Args:
        token: V2 material token。

    Returns:
        安全 token 类别。

    Raises:
        无显式抛出。
    """

    if not token:
        return "empty"
    if token in {"true", "false"}:
        return "boolean"
    if token.endswith("%") and _decimal_or_none(token.rstrip("%")) is not None:
        return "numeric_percent"
    if _decimal_or_none(token) is not None:
        return "numeric_plain"
    if len(token) <= 16:
        return "short_text"
    return "long_text"


def _decimal_or_none(value: str) -> Decimal | None:
    """解析 Decimal，失败返回 ``None``。

    Args:
        value: 待解析文本。

    Returns:
        Decimal 或 ``None``。

    Raises:
        无显式抛出。
    """

    try:
        return Decimal(value)
    except Exception:  # noqa: BLE001 - diagnostic category only.
        return None


def _unmatched_value_paths(value: object | None, unmatched_tokens: tuple[str, ...]) -> tuple[str, ...]:
    """读取未匹配 token 对应的安全结构路径。

    Args:
        value: fact value。
        unmatched_tokens: 未匹配 V2 material tokens。

    Returns:
        稳定结构路径，不含原始值。

    Raises:
        无显式抛出。
    """

    unmatched = set(unmatched_tokens)
    paths: list[str] = []
    for path, token in _value_token_paths(value, "value"):
        if token in unmatched:
            paths.append(path)
    return tuple(dict.fromkeys(paths))


def _value_token_paths(value: object | None, path: str) -> tuple[tuple[str, str], ...]:
    """以 V2-compatible 方式生成结构路径和归一化 token。

    Args:
        value: 待遍历值。
        path: 当前结构路径。

    Returns:
        ``(path, normalized_token)`` 元组。

    Raises:
        无显式抛出。
    """

    if value is None:
        return ()
    if isinstance(value, bool):
        return ((path, _normalize_text(str(value))),)
    if isinstance(value, (str, int, float, Decimal)):
        token = _normalize_text(str(value))
        return ((path, token),) if token else ()
    if is_dataclass(value) and not isinstance(value, type):
        return _value_token_paths(asdict(value), path)
    if isinstance(value, dict):
        collected: list[tuple[str, str]] = []
        for key in sorted(value):
            if str(key) in _IGNORED_VALUE_KEYS:
                continue
            collected.extend(_value_token_paths(value[key], f"{path}.{key}"))
        return tuple(collected)
    if isinstance(value, (tuple, list)):
        collected = []
        for item in value:
            collected.extend(_value_token_paths(item, f"{path}[]"))
        return tuple(collected)
    return ()


def _reference_granularity_counts(
    proof_references: tuple[EvidenceConfirmReference, ...],
) -> dict[str, int]:
    """统计 proof reference 粒度。

    Args:
        proof_references: V2 proof references。

    Returns:
        粒度到数量的稳定 dict。

    Raises:
        无显式抛出。
    """

    counts: dict[str, int] = {}
    for reference in proof_references:
        granularity = _reference_granularity(reference)
        counts[granularity] = counts.get(granularity, 0) + 1
    return dict(sorted(counts.items()))


def _reference_granularity(reference: EvidenceConfirmReference) -> ReferenceGranularity:
    """读取 reference 粒度。

    Args:
        reference: Evidence Confirm reference。

    Returns:
        粒度分类。

    Raises:
        无显式抛出。
    """

    if reference.reference_kind in {"reviewed_note", "derived_calculation"}:
        return "derived_or_reviewed_note"
    if reference.row_locator:
        return "row_level"
    if reference.table_id:
        return "table_level"
    return "section_level"


def _locator_downgraded(
    fact: ChapterFactEntry,
    proof_references: tuple[EvidenceConfirmReference, ...],
    anchors_by_id: dict[str, object],
) -> bool:
    """判断 fact 是否存在 row locator 降级。

    Args:
        fact: 章节事实。
        proof_references: V2 proof references。
        anchors_by_id: 章节 anchor 映射。

    Returns:
        存在降级时返回 ``True``。

    Raises:
        无显式抛出。
    """

    references_by_id = {reference.anchor_id: reference for reference in proof_references}
    for anchor_id in fact.evidence_anchor_ids:
        anchor = anchors_by_id.get(anchor_id)
        reference = references_by_id.get(anchor_id)
        if anchor is None or reference is None:
            continue
        if getattr(anchor, "row_locator", None) and reference.row_locator is None:
            return True
    return False


def _classify_record(
    *,
    fact: ChapterFactEntry,
    fact_result: EvidenceConfirmFactResultV2,
    all_references: tuple[EvidenceConfirmReference, ...],
    proof_references: tuple[EvidenceConfirmReference, ...],
    tokens: tuple[str, ...],
    unmatched_tokens: tuple[str, ...],
    value_status: str,
    missing_status: str,
    locator_downgraded: bool,
) -> ValueDiagnosticClassification:
    """分类单个诊断记录。

    Args:
        fact: 章节事实。
        fact_result: V2 fact 结果。
        all_references: fact anchor 对应全部 references。
        proof_references: V2 proof references。
        tokens: V2 material tokens。
        unmatched_tokens: 未匹配 token。
        value_status: value_match 维度状态。
        missing_status: missing_evidence 维度状态。
        locator_downgraded: 是否存在 locator 降级。

    Returns:
        诊断分类。

    Raises:
        无显式抛出。
    """

    if _is_bond_risk_missing_failure(fact, missing_status):
        return "bond_risk_group_anchor_projection_gap"
    if value_status == "pass":
        return "not_applicable"
    if _fact_is_not_applicable(fact) or _fact_is_derived(fact) or fact_result.status == "not_applicable":
        return "not_applicable"
    if all_references and not proof_references:
        return "anchor_attachment_mismatch"
    if not proof_references:
        return "undetermined_requires_live_excerpt_review"
    if _looks_overbroad(tokens, unmatched_tokens):
        return "value_shape_overbroad"
    if locator_downgraded or _only_coarse_references(proof_references):
        return "coarse_reference_insufficient"
    if _text_tokens_dominate(unmatched_tokens):
        return "matcher_normalization_gap"
    return "extractor_value_or_anchor_defect"


def _is_bond_risk_missing_failure(fact: ChapterFactEntry, missing_status: str) -> bool:
    """判断是否为 bond-risk 组级 anchor projection gap。

    Args:
        fact: 章节事实。
        missing_status: missing_evidence 维度状态。

    Returns:
        命中 bond-risk projection gap 时返回 ``True``。

    Raises:
        无显式抛出。
    """

    return (
        missing_status == "fail"
        and fact.source_field_id == "structured.bond_risk_evidence"
        and not fact.evidence_anchor_ids
        and bool(getattr(fact.value, "anchors", ()))
    )


def _looks_overbroad(tokens: tuple[str, ...], unmatched_tokens: tuple[str, ...]) -> bool:
    """判断 value shape 是否可能过宽。

    Args:
        tokens: 全部 V2 material tokens。
        unmatched_tokens: 未匹配 tokens。

    Returns:
        token 形状过宽时返回 ``True``。

    Raises:
        无显式抛出。
    """

    return len(tokens) >= 8 and len(unmatched_tokens) >= max(6, len(tokens) // 2)


def _only_coarse_references(
    proof_references: tuple[EvidenceConfirmReference, ...],
) -> bool:
    """判断 proof references 是否全为粗粒度。

    Args:
        proof_references: V2 proof references。

    Returns:
        全为 section/table 粗粒度时返回 ``True``。

    Raises:
        无显式抛出。
    """

    return bool(proof_references) and all(reference.row_locator is None for reference in proof_references)


def _text_tokens_dominate(tokens: tuple[str, ...]) -> bool:
    """判断未匹配 token 是否以文本为主。

    Args:
        tokens: 未匹配 tokens。

    Returns:
        文本 token 占多数时返回 ``True``。

    Raises:
        无显式抛出。
    """

    if not tokens:
        return False
    text_count = sum(1 for token in tokens if _token_category(token) in {"short_text", "long_text"})
    return text_count >= len(tokens) / 2


def _classification_counts(
    records: tuple[EvidenceConfirmValueDiagnosticRecord, ...],
) -> dict[str, int]:
    """统计诊断分类。

    Args:
        records: 诊断记录。

    Returns:
        分类计数。

    Raises:
        无显式抛出。
    """

    counts: dict[str, int] = {}
    for record in records:
        counts[record.classification] = counts.get(record.classification, 0) + 1
    return dict(sorted(counts.items()))


__all__ = (
    "EvidenceConfirmValueDiagnosticRecord",
    "EvidenceConfirmValueDiagnosticSummary",
    "VALUE_MATCH_DIAGNOSTIC_SCHEMA_VERSION",
    "summarize_value_match_diagnostics",
)
