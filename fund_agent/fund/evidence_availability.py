"""章节证据可用性派生视图，见基金分析模板第 2/3 章。

本模块属于 Agent 层 `fund_agent/fund` 基金领域能力，只从同源
`ChapterFactProjection` / `ChapterFactInput`、facts、anchors、missing reasons
和 additive typed CHAPTER_CONTRACT requirement id 派生 `EvidenceAvailability`。
它不读取年报仓库、PDF/cache/source helper、Service、Host、provider、retained report、
文件系统、环境变量或 dayu runtime；该视图也不替代 `ChapterFactProjection`。
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Final, Literal, TypeAlias, get_args

from fund_agent.fund.chapter_facts import (
    ChapterFactEntry,
    ChapterFactInput,
    ChapterFactMissingReason,
    ChapterFactProjection,
)
from fund_agent.fund.template.typed_contracts import (
    TypedTemplateContractManifest,
    load_typed_template_contract_manifest,
)

EVIDENCE_AVAILABILITY_SCHEMA_VERSION: Final[str] = "evidence_availability.v1"

AvailabilityStatus: TypeAlias = Literal[
    "available",
    "missing",
    "unavailable",
    "not_applicable",
    "unreviewed",
]

EvidenceRequirementId: TypeAlias = Literal[
    "ch1.requirement.portfolio_managers_reviewed",
    "ch1.requirement.risk_characteristic_text_reviewed",
    "ch2.must_answer.item_01",
    "ch2.must_answer.item_02",
    "ch2.must_answer.item_03",
    "ch2.must_answer.item_04",
    "ch2.must_answer.item_05",
    "ch2.must_answer.item_06",
    "ch2.required_output.item_01",
    "ch2.required_output.item_02",
    "ch2.required_output.item_03",
    "ch2.required_output.item_04",
    "ch2.required_output.item_05",
    "ch2.required_output.item_06",
    "ch2.required_output.item_07",
    "ch3.requirement.manager_strategy_text_reviewed",
    "ch3.requirement.turnover_rate_reviewed",
    "ch3.requirement.holdings_snapshot_reviewed",
    "ch3.requirement.cross_period_style_evidence_reviewed",
    "ch3.requirement.manager_alignment_reviewed",
    "ch3.requirement.actual_behavior_reviewed",
    "ch3.required_output.item_01",
    "ch3.required_output.item_02",
    "ch3.required_output.item_03",
    "ch3.required_output.item_04",
    "ch3.required_output.item_05",
    "ch3.required_output.item_06",
    "ch6.requirement.risk_characteristic_text_reviewed",
]

RequirementSourceKind: TypeAlias = Literal["fact", "synthetic_gap", "derived"]

_KNOWN_REQUIREMENT_IDS: Final[frozenset[str]] = frozenset(get_args(EvidenceRequirementId))
_STATUS_ORDER: Final[tuple[AvailabilityStatus, ...]] = (
    "unreviewed",
    "unavailable",
    "missing",
    "not_applicable",
    "available",
)


@dataclass(frozen=True, slots=True)
class EvidenceGapReference:
    """安全数据缺口引用。

    Attributes:
        gap_id: 本次派生内稳定 gap id，不包含原始报告文本。
        requirement_id: 关联的证据 requirement id。
        chapter_id: 公开章节编号；Ch2 内部子契约仍归属第 2 章。
        status: 当前 requirement 的缺口状态。
        missing_reason: 同源 fact 的缺失原因；派生缺口可为 `None`。
        missing_detail: 同源 fact 的安全缺失说明；不包含 PDF 原文。
        related_fact_id: 关联 fact id；派生缺口可为 `None`。
        source_field_id: 关联来源字段 id；派生缺口可为 `None`。
    """

    gap_id: str
    requirement_id: EvidenceRequirementId
    chapter_id: int
    status: AvailabilityStatus
    missing_reason: ChapterFactMissingReason | None
    missing_detail: str | None
    related_fact_id: str | None
    source_field_id: str | None


@dataclass(frozen=True, slots=True)
class RequirementAvailability:
    """单个证据 requirement 的可用性。

    Attributes:
        requirement_id: stable requirement id。
        chapter_id: 公开章节编号；不得为 Ch2 内部子契约创建公开章节。
        status: distinct availability 状态。
        source_kind: availability 来源类型。
        source_field_ids: 同源 facts 的来源字段 id。
        fact_ids: 同源 facts 的 fact id。
        evidence_anchor_ids: 同源 facts 引用的 anchor id。
        gap_references: 安全数据缺口引用。
        internal_subcontract_id: 第 2 章内部子契约编号；非 Ch2 为 `None`。
        detail: 面向审计的安全说明。
    """

    requirement_id: EvidenceRequirementId
    chapter_id: int
    status: AvailabilityStatus
    source_kind: RequirementSourceKind
    source_field_ids: tuple[str, ...]
    fact_ids: tuple[str, ...]
    evidence_anchor_ids: tuple[str, ...]
    gap_references: tuple[EvidenceGapReference, ...]
    internal_subcontract_id: str | None = None
    detail: str | None = None


@dataclass(frozen=True, slots=True)
class EvidenceAvailability:
    """章节证据可用性根对象。

    Attributes:
        schema_version: availability schema 版本。
        source_schema_version: 输入 `ChapterFactProjection` schema 版本。
        fund_code: 基金代码。
        report_year: 年报年份。
        requirements: requirement 级 availability 列表。
    """

    schema_version: str
    source_schema_version: str
    fund_code: str
    report_year: int
    requirements: tuple[RequirementAvailability, ...]

    def require(self, requirement_id: EvidenceRequirementId) -> RequirementAvailability:
        """按 requirement id 读取 availability。

        Args:
            requirement_id: 需要读取的 stable requirement id。

        Returns:
            匹配的 `RequirementAvailability`。

        Raises:
            ValueError: requirement id 不在当前 availability 中时抛出。
        """

        for requirement in self.requirements:
            if requirement.requirement_id == requirement_id:
                return requirement
        raise ValueError(f"未知 EvidenceAvailability requirement_id：{requirement_id}")


@dataclass(frozen=True, slots=True)
class _RequirementSpec:
    """requirement 到同源 fact 字段的派生规格。"""

    requirement_id: EvidenceRequirementId
    chapter_id: int
    source_field_ids: tuple[str, ...]
    internal_subcontract_id: str | None = None
    source_kind: RequirementSourceKind = "fact"
    detail: str | None = None


_CH2_REQUIREMENT_SPECS: Final[tuple[_RequirementSpec, ...]] = (
    _RequirementSpec("ch2.must_answer.item_01", 2, ("structured.nav_benchmark_performance",), "performance"),
    _RequirementSpec("ch2.must_answer.item_02", 2, ("structured.nav_benchmark_performance",), "performance"),
    _RequirementSpec("ch2.must_answer.item_03", 2, ("structured.nav_benchmark_performance",), "attribution"),
    _RequirementSpec("ch2.must_answer.item_04", 2, ("structured.nav_benchmark_performance",), "attribution"),
    _RequirementSpec("ch2.must_answer.item_05", 2, ("structured.fee_schedule",), "cost"),
    _RequirementSpec("ch2.must_answer.item_06", 2, ("structured.fee_schedule",), "cost"),
    _RequirementSpec("ch2.required_output.item_01", 2, ("structured.nav_benchmark_performance",), "performance"),
    _RequirementSpec("ch2.required_output.item_02", 2, ("structured.nav_benchmark_performance",), "performance"),
    _RequirementSpec("ch2.required_output.item_03", 2, ("structured.nav_benchmark_performance",), "attribution"),
    _RequirementSpec("ch2.required_output.item_04", 2, ("structured.nav_benchmark_performance",), "attribution"),
    _RequirementSpec("ch2.required_output.item_05", 2, ("structured.fee_schedule",), "cost"),
    _RequirementSpec("ch2.required_output.item_06", 2, ("structured.fee_schedule",), "cost"),
    _RequirementSpec("ch2.required_output.item_07", 2, ("structured.nav_benchmark_performance", "structured.fee_schedule"), "cost"),
)

_CH1_REQUIREMENT_SPECS: Final[tuple[_RequirementSpec, ...]] = (
    _RequirementSpec(
        "ch1.requirement.portfolio_managers_reviewed",
        1,
        ("structured.portfolio_managers",),
        detail="模板第 1 章基金经理任期列表证据。",
    ),
    _RequirementSpec(
        "ch1.requirement.risk_characteristic_text_reviewed",
        1,
        ("structured.risk_characteristic_text",),
        detail="模板第 1 章风险收益特征文本证据。",
    ),
)

_CH3_REQUIREMENT_SPECS: Final[tuple[_RequirementSpec, ...]] = (
    _RequirementSpec(
        "ch3.requirement.manager_strategy_text_reviewed",
        3,
        ("structured.manager_strategy_text",),
        detail="模板第 3 章 §4 策略文本证据。",
    ),
    _RequirementSpec(
        "ch3.requirement.turnover_rate_reviewed",
        3,
        ("structured.turnover_rate",),
        detail="模板第 3 章 §8 换手率证据。",
    ),
    _RequirementSpec(
        "ch3.requirement.holdings_snapshot_reviewed",
        3,
        ("structured.holdings_snapshot",),
        detail="模板第 3 章 §8 持仓快照证据。",
    ),
    _RequirementSpec(
        "ch3.requirement.cross_period_style_evidence_reviewed",
        3,
        ("synthetic.cross_period_comparison",),
        source_kind="synthetic_gap",
        detail="当前单年 ChapterFactProjection 不加载 prior-year 文档，跨期风格证据视为未复核。",
    ),
    _RequirementSpec(
        "ch3.requirement.manager_alignment_reviewed",
        3,
        ("structured.manager_alignment",),
        detail="模板第 3 章 §9 基金经理持有披露证据。",
    ),
    _RequirementSpec(
        "ch3.required_output.item_01",
        3,
        ("structured.basic_identity", "structured.portfolio_managers"),
        detail="基金经理基本信息 required output 证据。",
    ),
    _RequirementSpec(
        "ch3.required_output.item_02",
        3,
        ("structured.manager_strategy_text",),
        detail="宣称的投资策略 required output 证据。",
    ),
    _RequirementSpec(
        "ch3.required_output.item_06",
        3,
        ("structured.manager_alignment",),
        detail="利益一致性 required output 证据。",
    ),
)

_CH6_REQUIREMENT_SPECS: Final[tuple[_RequirementSpec, ...]] = (
    _RequirementSpec(
        "ch6.requirement.risk_characteristic_text_reviewed",
        6,
        ("structured.risk_characteristic_text",),
        detail="模板第 6 章风险收益特征文本证据。",
    ),
)

_CH3_ACTUAL_BEHAVIOR_REQUIREMENT_ID: Final[EvidenceRequirementId] = "ch3.requirement.actual_behavior_reviewed"
_CH3_ACTUAL_BEHAVIOR_OUTPUT_IDS: Final[tuple[EvidenceRequirementId, ...]] = (
    "ch3.required_output.item_03",
    "ch3.required_output.item_04",
    "ch3.required_output.item_05",
)
_CH3_ACTUAL_BEHAVIOR_DEPENDENCIES: Final[tuple[EvidenceRequirementId, ...]] = (
    "ch3.requirement.turnover_rate_reviewed",
    "ch3.requirement.holdings_snapshot_reviewed",
    "ch3.requirement.cross_period_style_evidence_reviewed",
)


def derive_evidence_availability(
    projection: ChapterFactProjection,
    typed_manifest: TypedTemplateContractManifest | None = None,
) -> EvidenceAvailability:
    """从同源章节事实派生证据可用性。

    Args:
        projection: `ChapterFactProjection` 输入，不会被替换或修改。
        typed_manifest: 可选 typed contract manifest；为空时读取 additive typed sidecar。

    Returns:
        `EvidenceAvailability` 派生视图。

    Raises:
        ValueError: typed contract 中存在未知 requirement id，或输入章节重复时抛出。
    """

    manifest = typed_manifest if typed_manifest is not None else load_typed_template_contract_manifest()
    _validate_typed_requirement_ids(manifest)
    _validate_projection_chapters(projection)
    base_requirements = tuple(
        _derive_from_spec(projection, spec)
        for spec in (
            *_CH1_REQUIREMENT_SPECS,
            *_CH2_REQUIREMENT_SPECS,
            *_CH3_REQUIREMENT_SPECS,
            *_CH6_REQUIREMENT_SPECS,
        )
    )
    aggregate_requirements = _derive_ch3_actual_behavior_requirements(base_requirements)
    requirements = _assert_unique_requirements((*base_requirements, *aggregate_requirements))
    return EvidenceAvailability(
        schema_version=EVIDENCE_AVAILABILITY_SCHEMA_VERSION,
        source_schema_version=projection.schema_version,
        fund_code=projection.fund_code,
        report_year=projection.report_year,
        requirements=requirements,
    )


def derive_chapter_evidence_availability(
    chapter: ChapterFactInput,
    typed_manifest: TypedTemplateContractManifest | None = None,
) -> tuple[RequirementAvailability, ...]:
    """从单章 `ChapterFactInput` 派生该章证据可用性。

    Args:
        chapter: 单章事实输入。
        typed_manifest: 可选 typed contract manifest；为空时读取 additive typed sidecar。

    Returns:
        当前公开章节的 requirement availability 元组。

    Raises:
        ValueError: typed contract 中存在未知 requirement id，或章节编号不受支持时抛出。
    """

    projection = ChapterFactProjection(
        schema_version="chapter_fact_projection.v1",
        fund_code=_fund_code_from_chapter(chapter),
        report_year=_report_year_from_chapter(chapter),
        fund_type=chapter.fund_type,
        classification_basis=chapter.classification_basis,
        chapters=(chapter,),
        global_missing_reasons=chapter.missing_reasons,
    )
    availability = derive_evidence_availability(projection, typed_manifest)
    return tuple(requirement for requirement in availability.requirements if requirement.chapter_id == chapter.chapter_id)


def _validate_projection_chapters(projection: ChapterFactProjection) -> None:
    """校验 projection 章节编号不重复。

    Args:
        projection: 待校验的章节事实投影。

    Returns:
        校验通过时返回 `None`。

    Raises:
        ValueError: 章节编号重复时抛出。
    """

    chapter_ids = tuple(chapter.chapter_id for chapter in projection.chapters)
    if len(set(chapter_ids)) != len(chapter_ids):
        raise ValueError("ChapterFactProjection 章节编号存在重复")


def _validate_typed_requirement_ids(manifest: TypedTemplateContractManifest) -> None:
    """校验 typed contract 引用的 requirement ids 均可派生。

    Args:
        manifest: typed contract manifest。

    Returns:
        校验通过时返回 `None`。

    Raises:
        ValueError: must_not_cover predicate 或 Ch2 internal subcontract 中存在未知 requirement id。
    """

    referenced_ids: list[str] = []
    for chapter in manifest.chapters:
        for clause in chapter.must_not_cover:
            if clause.applies_when is not None:
                referenced_ids.extend(clause.applies_when.requirement_ids)
        for subcontract in chapter.internal_subcontracts:
            referenced_ids.extend(subcontract.requirement_ids)
    unknown_ids = tuple(requirement_id for requirement_id in referenced_ids if requirement_id not in _KNOWN_REQUIREMENT_IDS)
    if unknown_ids:
        raise ValueError(f"typed contract 存在未知 EvidenceRequirementId：{unknown_ids}")


def _derive_from_spec(
    projection: ChapterFactProjection,
    spec: _RequirementSpec,
) -> RequirementAvailability:
    """按派生规格生成单个 requirement availability。

    Args:
        projection: 章节事实投影。
        spec: requirement 派生规格。

    Returns:
        单个 requirement availability。

    Raises:
        无显式抛出。
    """

    facts = _facts_for_spec(projection, spec)
    status = _status_for_facts(spec, facts)
    fact_ids = tuple(fact.fact_id for fact in facts)
    anchor_ids = _unique_strings(tuple(anchor_id for fact in facts for anchor_id in fact.evidence_anchor_ids))
    gap_references = _gap_references_for_facts(spec, facts, status)
    return RequirementAvailability(
        requirement_id=spec.requirement_id,
        chapter_id=spec.chapter_id,
        status=status,
        source_kind=spec.source_kind,
        source_field_ids=spec.source_field_ids,
        fact_ids=fact_ids,
        evidence_anchor_ids=anchor_ids,
        gap_references=gap_references,
        internal_subcontract_id=spec.internal_subcontract_id,
        detail=spec.detail,
    )


def _facts_for_spec(
    projection: ChapterFactProjection,
    spec: _RequirementSpec,
) -> tuple[ChapterFactEntry, ...]:
    """读取同源 facts。

    Args:
        projection: 章节事实投影。
        spec: requirement 派生规格。

    Returns:
        匹配 source_field_id 的 facts；cross-period 可跨章节读取 synthetic gap。

    Raises:
        无显式抛出。
    """

    matched: list[ChapterFactEntry] = []
    for chapter in projection.chapters:
        for fact in chapter.facts:
            if fact.source_field_id in spec.source_field_ids and (
                fact.chapter_id == spec.chapter_id or fact.source_field_id.startswith("synthetic.")
            ):
                matched.append(fact)
    return tuple(matched)


def _status_for_facts(
    spec: _RequirementSpec,
    facts: tuple[ChapterFactEntry, ...],
) -> AvailabilityStatus:
    """从 facts 派生 requirement 状态。

    Args:
        spec: requirement 派生规格。
        facts: 同源 facts。

    Returns:
        distinct availability 状态。

    Raises:
        无显式抛出。
    """

    if spec.requirement_id == "ch3.requirement.cross_period_style_evidence_reviewed":
        return "unreviewed"
    if not facts:
        return "unreviewed"
    fact_statuses = tuple(_status_for_fact(fact) for fact in facts)
    return _combine_statuses(fact_statuses)


def _status_for_fact(fact: ChapterFactEntry) -> AvailabilityStatus:
    """从单个 fact 派生 availability 状态。

    Args:
        fact: 章节事实。

    Returns:
        availability 状态。

    Raises:
        无显式抛出。
    """

    if fact.status == "available" and fact.evidence_anchor_ids and fact.missing_reason is None:
        return "available"
    if fact.status == "available":
        return "unreviewed"
    if fact.status in ("missing", "unavailable", "not_applicable"):
        return fact.status
    return "unreviewed"


def _derive_ch3_actual_behavior_requirements(
    base_requirements: tuple[RequirementAvailability, ...],
) -> tuple[RequirementAvailability, ...]:
    """派生第 3 章实际行为聚合 requirement。

    Args:
        base_requirements: 已派生的基础 requirements。

    Returns:
        `actual_behavior_reviewed` 和相关 required output requirements。

    Raises:
        ValueError: 基础 requirement 缺失时抛出。
    """

    dependencies = tuple(_requirement_by_id(base_requirements, requirement_id) for requirement_id in _CH3_ACTUAL_BEHAVIOR_DEPENDENCIES)
    status = _combine_statuses(tuple(requirement.status for requirement in dependencies))
    fact_ids = _unique_strings(tuple(fact_id for requirement in dependencies for fact_id in requirement.fact_ids))
    anchor_ids = _unique_strings(tuple(anchor_id for requirement in dependencies for anchor_id in requirement.evidence_anchor_ids))
    source_field_ids = _unique_strings(
        tuple(source_field_id for requirement in dependencies for source_field_id in requirement.source_field_ids)
    )
    gap_references = tuple(gap for requirement in dependencies for gap in requirement.gap_references)
    aggregate = RequirementAvailability(
        requirement_id=_CH3_ACTUAL_BEHAVIOR_REQUIREMENT_ID,
        chapter_id=3,
        status=status,
        source_kind="derived",
        source_field_ids=source_field_ids,
        fact_ids=fact_ids,
        evidence_anchor_ids=anchor_ids,
        gap_references=gap_references,
        detail="模板第 3 章实际投资行为由换手率、持仓快照和跨期风格证据共同支撑。",
    )
    outputs = tuple(
        RequirementAvailability(
            requirement_id=requirement_id,
            chapter_id=3,
            status=status,
            source_kind="derived",
            source_field_ids=source_field_ids,
            fact_ids=fact_ids,
            evidence_anchor_ids=anchor_ids,
            gap_references=gap_references,
            detail="第 3 章 actual behavior required output 复用同源实际行为 availability。",
        )
        for requirement_id in _CH3_ACTUAL_BEHAVIOR_OUTPUT_IDS
    )
    return (aggregate, *outputs)


def _requirement_by_id(
    requirements: tuple[RequirementAvailability, ...],
    requirement_id: EvidenceRequirementId,
) -> RequirementAvailability:
    """按 id 读取 requirement availability。

    Args:
        requirements: requirement availability 序列。
        requirement_id: stable requirement id。

    Returns:
        匹配的 requirement availability。

    Raises:
        ValueError: 未找到 requirement 时抛出。
    """

    for requirement in requirements:
        if requirement.requirement_id == requirement_id:
            return requirement
    raise ValueError(f"缺少基础 EvidenceRequirementId：{requirement_id}")


def _combine_statuses(statuses: tuple[AvailabilityStatus, ...]) -> AvailabilityStatus:
    """组合多个状态为最保守 requirement 状态。

    Args:
        statuses: 待组合状态。

    Returns:
        按 unreviewed > unavailable > missing > not_applicable > available 优先级组合后的状态。

    Raises:
        ValueError: 状态序列为空时抛出。
    """

    if not statuses:
        raise ValueError("availability statuses 不能为空")
    for status in _STATUS_ORDER:
        if status in statuses:
            return status
    return "unreviewed"


def _gap_references_for_facts(
    spec: _RequirementSpec,
    facts: tuple[ChapterFactEntry, ...],
    status: AvailabilityStatus,
) -> tuple[EvidenceGapReference, ...]:
    """生成安全 gap references。

    Args:
        spec: requirement 派生规格。
        facts: 同源 facts。
        status: requirement 状态。

    Returns:
        gap reference 元组；available 不生成缺口。

    Raises:
        无显式抛出。
    """

    if status == "available":
        return ()
    if not facts:
        return (
            _gap_reference(
                spec,
                status=status,
                missing_reason=None,
                missing_detail="projection 中没有同源 fact；不加载文档补齐。",
                related_fact_id=None,
                source_field_id=None,
            ),
        )
    return tuple(
        _gap_reference(
            spec,
            status=_status_for_fact(fact) if spec.requirement_id != "ch3.requirement.cross_period_style_evidence_reviewed" else status,
            missing_reason=fact.missing_reason,
            missing_detail=fact.missing_detail,
            related_fact_id=fact.fact_id,
            source_field_id=fact.source_field_id,
        )
        for fact in facts
        if _status_for_fact(fact) != "available" or spec.requirement_id == "ch3.requirement.cross_period_style_evidence_reviewed"
    )


def _gap_reference(
    spec: _RequirementSpec,
    *,
    status: AvailabilityStatus,
    missing_reason: ChapterFactMissingReason | None,
    missing_detail: str | None,
    related_fact_id: str | None,
    source_field_id: str | None,
) -> EvidenceGapReference:
    """构造安全 gap reference。

    Args:
        spec: requirement 派生规格。
        status: 缺口状态。
        missing_reason: 缺失原因。
        missing_detail: 安全缺失说明。
        related_fact_id: 关联 fact id。
        source_field_id: 关联来源字段 id。

    Returns:
        `EvidenceGapReference`。

    Raises:
        无显式抛出。
    """

    raw = f"{spec.requirement_id}|{status}|{missing_reason}|{related_fact_id}|{source_field_id}"
    digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()[:10]
    return EvidenceGapReference(
        gap_id=f"evidence-gap:{spec.requirement_id}:{digest}",
        requirement_id=spec.requirement_id,
        chapter_id=spec.chapter_id,
        status=status,
        missing_reason=missing_reason,
        missing_detail=missing_detail,
        related_fact_id=related_fact_id,
        source_field_id=source_field_id,
    )


def _assert_unique_requirements(
    requirements: tuple[RequirementAvailability, ...],
) -> tuple[RequirementAvailability, ...]:
    """校验 requirement id 唯一。

    Args:
        requirements: 待校验的 requirement availability。

    Returns:
        原序列。

    Raises:
        ValueError: requirement id 重复时抛出。
    """

    requirement_ids = tuple(requirement.requirement_id for requirement in requirements)
    if len(set(requirement_ids)) != len(requirement_ids):
        raise ValueError("EvidenceAvailability requirement_id 存在重复")
    return requirements


def _fund_code_from_chapter(chapter: ChapterFactInput) -> str:
    """从章节 fact id 中恢复基金代码。

    Args:
        chapter: 单章事实输入。

    Returns:
        基金代码；无 fact 时返回 `unknown`。

    Raises:
        无显式抛出。
    """

    if not chapter.facts:
        return "unknown"
    parts = chapter.facts[0].fact_id.split(":")
    return parts[1] if len(parts) > 1 else "unknown"


def _report_year_from_chapter(chapter: ChapterFactInput) -> int:
    """从章节 fact id 中恢复报告年份。

    Args:
        chapter: 单章事实输入。

    Returns:
        报告年份；无合法 fact id 时返回 `0`。

    Raises:
        无显式抛出。
    """

    if not chapter.facts:
        return 0
    parts = chapter.facts[0].fact_id.split(":")
    if len(parts) <= 2:
        return 0
    try:
        return int(parts[2])
    except ValueError:
        return 0


def _unique_strings(values: tuple[str, ...]) -> tuple[str, ...]:
    """按首次出现顺序去重字符串。

    Args:
        values: 原始字符串。

    Returns:
        去重后的字符串元组。

    Raises:
        无显式抛出。
    """

    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        result.append(value)
    return tuple(result)


__all__ = [
    "EVIDENCE_AVAILABILITY_SCHEMA_VERSION",
    "AvailabilityStatus",
    "EvidenceAvailability",
    "EvidenceGapReference",
    "EvidenceRequirementId",
    "RequirementAvailability",
    "derive_chapter_evidence_availability",
    "derive_evidence_availability",
]
