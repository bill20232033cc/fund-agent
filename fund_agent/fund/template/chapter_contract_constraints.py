"""CHAPTER_CONTRACT 可执行写作约束 sidecar。

本模块属于 Agent 层 Fund 领域能力，负责在不修改既有
`ChapterContract` 的前提下，为模板第 0-7 章补充 dev-only 写作审计所需的
证据约束。既有 `fund_agent.fund.template.contracts` 仍是章节编号、
must_answer、must_not_cover 与 preferred_lens 的唯一真源；本模块只在加载时
包裹该 manifest，并对 active_fund 第 3 章言行一致性、增强指数第 2 章
R=A+B-C、债券第 6 章核心风险等约束提供可执行配置。
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final, Literal

from fund_agent.fund.fund_type import FundType
from fund_agent.fund.template.contracts import (
    LensKey,
    load_template_contract_manifest,
)

RequirementSeverity = Literal["blocking", "material", "informational", "config_only"]
RequirementStatus = Literal[
    "satisfied",
    "missing",
    "satisfied_by_data_gap",
    "not_applicable",
]
FailureCategory = Literal[
    "unsupported_stability_claim",
    "required_evidence_missing",
    "forbidden_content",
    "allowed_na_reason_missing",
    "insufficient_evidence_wording_missing",
    "final_judgment_unsupported",
    "deferred_extraction_requirement",
    "invalid_audit_input",
    "input_conflict",
]

CONSTRAINT_SCHEMA_VERSION: Final[str] = "chapter_contract_constraints.v0"
ACTIVE_CHAPTER_3_TURNOVER_REQUIREMENT_ID: Final[str] = (
    "chapter_3.active_fund.turnover_style_consistency_evidence"
)
ENHANCED_INDEX_CHAPTER_2_REQUIREMENT_ID: Final[str] = (
    "chapter_2.enhanced_index.tracking_error_evidence"
)
BOND_CHAPTER_6_REQUIREMENT_ID: Final[str] = "chapter_6.bond_fund.risk_lens_evidence"
TURNOVER_STYLE_GAP_REASON_CODES: Final[tuple[str, ...]] = (
    "turnover_or_style_change_not_reviewed",
    "not_reviewed_in_current_slice",
    "source_unavailable",
)
TURNOVER_STYLE_REQUIRED_WORDING_FRAGMENTS: Final[tuple[str, ...]] = (
    "不能据此判断风格稳定、风格一致或言行一致",
    "下一步最小验证问题：",
)
_DEFAULT_ALLOWED_NA_REASONS: Final[tuple[str, ...]] = (
    "not_applicable_to_fund_type",
    "not_reviewed_in_current_slice",
)
_EXPECTED_CHAPTER_IDS: Final[tuple[int, ...]] = tuple(range(8))


@dataclass(frozen=True, slots=True)
class EvidenceRequirement:
    """单条报告写作证据要求。

    Attributes:
        requirement_id: 约束稳定标识。
        chapter_id: 模板章节编号，必须为第 0-7 章之一。
        fund_type_slot: 适用基金类型 slot，或 `default`。
        fact_categories: 可接受事实类别。
        accepted_fact_ids: 可直接满足约束的事实 id。
        accepted_gap_reason_codes: 可降级满足约束的数据缺口原因码。
        required_wording_fragments: 使用数据缺口时报告必须保留的措辞片段。
        severity: 约束严重程度；`config_only` 在写作审计 issue 中映射为 informational。
        deferred: 是否为已配置但当前 slice 不执行的抽取依赖要求。
    """

    requirement_id: str
    chapter_id: int
    fund_type_slot: LensKey
    fact_categories: tuple[str, ...]
    accepted_fact_ids: tuple[str, ...]
    accepted_gap_reason_codes: tuple[str, ...]
    required_wording_fragments: tuple[str, ...]
    severity: RequirementSeverity
    deferred: bool = False


@dataclass(frozen=True, slots=True)
class ChapterExecutableConstraint:
    """单章 CHAPTER_CONTRACT 的可执行 sidecar 约束。

    Attributes:
        chapter_id: 模板章节编号，必须与既有 `ChapterContract` 对齐。
        fund_type_slot: 适用基金类型 slot，或 `default`。
        must_answer: 从既有 `ChapterContract.must_answer` 复制的只读上下文。
        must_not_cover: 从既有 `ChapterContract.must_not_cover` 复制的禁写规则。
        required_evidence: 本 sidecar 增补的证据要求。
        allowed_na_reason: 本章允许的 N/A 或 data_gap 原因；N/A 不等于证据满足。
        failure_behavior: 当前约束默认失败行为。
    """

    chapter_id: int
    fund_type_slot: LensKey
    must_answer: tuple[str, ...]
    must_not_cover: tuple[str, ...]
    required_evidence: tuple[EvidenceRequirement, ...]
    allowed_na_reason: tuple[str, ...]
    failure_behavior: RequirementSeverity


@dataclass(frozen=True, slots=True)
class ChapterContractConstraintManifest:
    """CHAPTER_CONTRACT 可执行 sidecar 清单。

    Attributes:
        schema_version: sidecar schema 版本。
        source_manifest_template_id: 被包裹的模板 manifest id。
        constraints: 模板第 0-7 章的默认约束和基金类型 overlay。
    """

    schema_version: str
    source_manifest_template_id: str
    constraints: tuple[ChapterExecutableConstraint, ...]


def load_chapter_contract_constraint_manifest() -> ChapterContractConstraintManifest:
    """加载 CHAPTER_CONTRACT 可执行约束清单。

    Returns:
        包含第 0-7 章默认约束与首个实现 slice overlay 的 sidecar manifest。

    Raises:
        ValueError: sidecar 与既有模板 manifest 章节不一致、字段为空或 overlay 非法时抛出。
    """

    source_manifest = load_template_contract_manifest()
    source_by_id = {chapter.chapter_id: chapter for chapter in source_manifest.chapters}
    constraints: list[ChapterExecutableConstraint] = []

    for chapter in source_manifest.chapters:
        constraints.append(
            ChapterExecutableConstraint(
                chapter_id=chapter.chapter_id,
                fund_type_slot="default",
                must_answer=chapter.must_answer,
                must_not_cover=chapter.must_not_cover,
                required_evidence=(),
                allowed_na_reason=_DEFAULT_ALLOWED_NA_REASONS,
                failure_behavior="informational",
            )
        )

    chapter_2 = source_by_id[2]
    constraints.append(
        ChapterExecutableConstraint(
            chapter_id=2,
            fund_type_slot="enhanced_index",
            must_answer=chapter_2.must_answer,
            must_not_cover=chapter_2.must_not_cover,
            required_evidence=(
                EvidenceRequirement(
                    requirement_id=ENHANCED_INDEX_CHAPTER_2_REQUIREMENT_ID,
                    chapter_id=2,
                    fund_type_slot="enhanced_index",
                    fact_categories=("performance",),
                    accepted_fact_ids=("fact:performance.tracking_error",),
                    accepted_gap_reason_codes=("not_reviewed_in_current_slice",),
                    required_wording_fragments=(),
                    severity="config_only",
                    deferred=True,
                ),
            ),
            allowed_na_reason=("not_reviewed_in_current_slice", "source_unavailable"),
            failure_behavior="config_only",
        )
    )

    chapter_3 = source_by_id[3]
    constraints.append(
        ChapterExecutableConstraint(
            chapter_id=3,
            fund_type_slot="active_fund",
            must_answer=chapter_3.must_answer,
            must_not_cover=chapter_3.must_not_cover,
            required_evidence=(
                EvidenceRequirement(
                    requirement_id=ACTIVE_CHAPTER_3_TURNOVER_REQUIREMENT_ID,
                    chapter_id=3,
                    fund_type_slot="active_fund",
                    fact_categories=("manager", "holdings"),
                    accepted_fact_ids=(
                        "fact:manager.turnover_rate",
                        "fact:manager.style_change_proxy",
                        "fact:holdings.style_change_proxy",
                    ),
                    accepted_gap_reason_codes=TURNOVER_STYLE_GAP_REASON_CODES,
                    required_wording_fragments=TURNOVER_STYLE_REQUIRED_WORDING_FRAGMENTS,
                    severity="material",
                    deferred=False,
                ),
            ),
            allowed_na_reason=TURNOVER_STYLE_GAP_REASON_CODES,
            failure_behavior="material",
        )
    )

    chapter_6 = source_by_id[6]
    constraints.append(
        ChapterExecutableConstraint(
            chapter_id=6,
            fund_type_slot="bond_fund",
            must_answer=chapter_6.must_answer,
            must_not_cover=chapter_6.must_not_cover,
            required_evidence=(
                EvidenceRequirement(
                    requirement_id=BOND_CHAPTER_6_REQUIREMENT_ID,
                    chapter_id=6,
                    fund_type_slot="bond_fund",
                    fact_categories=("risk",),
                    accepted_fact_ids=(
                        "fact:risk.duration",
                        "fact:risk.credit_exposure",
                        "fact:risk.leverage",
                        "fact:risk.liquidity",
                        "fact:risk.max_drawdown",
                    ),
                    accepted_gap_reason_codes=("not_reviewed_in_current_slice",),
                    required_wording_fragments=(),
                    severity="config_only",
                    deferred=True,
                ),
            ),
            allowed_na_reason=("not_reviewed_in_current_slice", "source_unavailable"),
            failure_behavior="config_only",
        )
    )

    manifest = ChapterContractConstraintManifest(
        schema_version=CONSTRAINT_SCHEMA_VERSION,
        source_manifest_template_id=source_manifest.template_id,
        constraints=tuple(constraints),
    )
    validate_chapter_contract_constraint_manifest(manifest)
    return manifest


def validate_chapter_contract_constraint_manifest(
    manifest: ChapterContractConstraintManifest,
) -> None:
    """校验 CHAPTER_CONTRACT sidecar 是否仍包裹既有模板真源。

    Args:
        manifest: 待校验的 sidecar manifest。

    Returns:
        校验通过时返回 `None`。

    Raises:
        ValueError: schema、章节覆盖、default wrapper 或 evidence requirement 不合法时抛出。
    """

    source_manifest = load_template_contract_manifest()
    source_by_id = {chapter.chapter_id: chapter for chapter in source_manifest.chapters}
    if manifest.source_manifest_template_id != source_manifest.template_id:
        raise ValueError("sidecar source_manifest_template_id 与模板 manifest 不一致")
    if manifest.schema_version != CONSTRAINT_SCHEMA_VERSION:
        raise ValueError("sidecar schema_version 不受支持")

    constraint_chapter_ids = {constraint.chapter_id for constraint in manifest.constraints}
    if constraint_chapter_ids != set(_EXPECTED_CHAPTER_IDS):
        raise ValueError("sidecar 必须且只能覆盖模板第 0-7 章")

    default_constraints = {
        constraint.chapter_id: constraint
        for constraint in manifest.constraints
        if constraint.fund_type_slot == "default"
    }
    if tuple(sorted(default_constraints)) != _EXPECTED_CHAPTER_IDS:
        raise ValueError("sidecar 每章必须有且仅有一个 default wrapper")

    for chapter_id, constraint in default_constraints.items():
        source_chapter = source_by_id[chapter_id]
        if constraint.must_answer != source_chapter.must_answer:
            raise ValueError(f"章节 {chapter_id} default must_answer 未包裹模板真源")
        if constraint.must_not_cover != source_chapter.must_not_cover:
            raise ValueError(f"章节 {chapter_id} default must_not_cover 未包裹模板真源")

    for constraint in manifest.constraints:
        _validate_constraint(constraint, source_by_id)


def constraints_for_chapter(
    chapter_id: int,
    fund_type_slot: FundType | Literal["default"] = "default",
) -> tuple[ChapterExecutableConstraint, ...]:
    """按章节与基金类型读取 sidecar 约束。

    Args:
        chapter_id: 模板章节编号，必须为第 0-7 章之一。
        fund_type_slot: 基金类型 slot；未命中时仍返回 default 约束。

    Returns:
        先 default 后基金类型 overlay 的约束元组。

    Raises:
        ValueError: 章节编号或基金类型 slot 不受支持时抛出。
    """

    _validate_chapter_id(chapter_id)
    _validate_fund_type_slot(fund_type_slot)
    manifest = load_chapter_contract_constraint_manifest()
    matches = tuple(
        constraint
        for constraint in manifest.constraints
        if constraint.chapter_id == chapter_id
        and constraint.fund_type_slot in ("default", fund_type_slot)
    )
    if not matches:
        raise ValueError(f"未找到章节 {chapter_id} 的 sidecar 约束")
    return tuple(sorted(matches, key=lambda item: item.fund_type_slot != "default"))


def map_requirement_severity_to_issue_severity(
    severity: RequirementSeverity,
) -> Literal["blocking", "material", "minor", "informational"]:
    """把 sidecar 约束严重程度映射为写作审计 issue 严重程度。

    Args:
        severity: sidecar 约束严重程度。

    Returns:
        写作审计 issue 的稳定严重程度；`config_only` 映射为 `informational`。

    Raises:
        ValueError: 遇到未知严重程度时抛出。
    """

    if severity in ("blocking", "material", "informational"):
        return severity
    if severity == "config_only":
        return "informational"
    raise ValueError(f"不支持的约束严重程度：{severity}")


def _validate_constraint(
    constraint: ChapterExecutableConstraint,
    source_by_id: dict[int, object],
) -> None:
    """校验单条 sidecar 约束。

    Args:
        constraint: 待校验约束。
        source_by_id: 既有模板章节索引。

    Returns:
        校验通过时返回 `None`。

    Raises:
        ValueError: 约束字段为空、fund_type_slot 非法或 requirement 不合法时抛出。
    """

    _validate_chapter_id(constraint.chapter_id)
    _validate_fund_type_slot(constraint.fund_type_slot)
    source_chapter = source_by_id[constraint.chapter_id]
    if constraint.must_answer != source_chapter.must_answer:  # type: ignore[attr-defined]
        raise ValueError(f"章节 {constraint.chapter_id} must_answer 未包裹模板真源")
    if not set(source_chapter.must_not_cover).issubset(constraint.must_not_cover):  # type: ignore[attr-defined]
        raise ValueError(f"章节 {constraint.chapter_id} must_not_cover 缺少模板真源规则")
    _validate_text_tuple(constraint.must_answer, "must_answer", constraint.chapter_id)
    _validate_text_tuple(constraint.must_not_cover, "must_not_cover", constraint.chapter_id)
    _validate_text_tuple(constraint.allowed_na_reason, "allowed_na_reason", constraint.chapter_id)
    _validate_severity(constraint.failure_behavior)
    for requirement in constraint.required_evidence:
        _validate_requirement(requirement, constraint)


def _validate_requirement(
    requirement: EvidenceRequirement,
    constraint: ChapterExecutableConstraint,
) -> None:
    """校验单条证据要求。

    Args:
        requirement: 待校验证据要求。
        constraint: requirement 所属章节约束。

    Returns:
        校验通过时返回 `None`。

    Raises:
        ValueError: requirement 与所属章节不一致或字段非法时抛出。
    """

    if not requirement.requirement_id.strip():
        raise ValueError("requirement_id 不能为空")
    if requirement.chapter_id != constraint.chapter_id:
        raise ValueError("requirement chapter_id 必须与所属 constraint 一致")
    if requirement.fund_type_slot != constraint.fund_type_slot:
        raise ValueError("requirement fund_type_slot 必须与所属 constraint 一致")
    if not requirement.fact_categories:
        raise ValueError(f"{requirement.requirement_id} fact_categories 不能为空")
    if not requirement.accepted_fact_ids and not requirement.accepted_gap_reason_codes:
        raise ValueError(f"{requirement.requirement_id} 必须声明事实或 data_gap 降级路径")
    _validate_text_tuple(requirement.fact_categories, "fact_categories", requirement.chapter_id)
    _validate_text_tuple(
        requirement.accepted_fact_ids,
        "accepted_fact_ids",
        requirement.chapter_id,
        allow_empty=True,
    )
    _validate_text_tuple(
        requirement.accepted_gap_reason_codes,
        "accepted_gap_reason_codes",
        requirement.chapter_id,
        allow_empty=True,
    )
    _validate_text_tuple(
        requirement.required_wording_fragments,
        "required_wording_fragments",
        requirement.chapter_id,
        allow_empty=True,
    )
    _validate_severity(requirement.severity)


def _validate_chapter_id(chapter_id: int) -> None:
    """校验章节编号。

    Args:
        chapter_id: 待校验章节编号。

    Returns:
        校验通过时返回 `None`。

    Raises:
        ValueError: 章节编号不是第 0-7 章时抛出。
    """

    if chapter_id not in _EXPECTED_CHAPTER_IDS:
        raise ValueError(f"不支持的章节 id：{chapter_id}")


def _validate_fund_type_slot(fund_type_slot: LensKey) -> None:
    """校验基金类型 slot。

    Args:
        fund_type_slot: 待校验基金类型 slot。

    Returns:
        校验通过时返回 `None`。

    Raises:
        ValueError: fund_type_slot 不受支持时抛出。
    """

    if fund_type_slot not in (
        "default",
        "index_fund",
        "active_fund",
        "bond_fund",
        "enhanced_index",
        "qdii_fund",
        "fof_fund",
    ):
        raise ValueError(f"不支持的基金类型 slot：{fund_type_slot}")


def _validate_severity(severity: RequirementSeverity) -> None:
    """校验约束严重程度。

    Args:
        severity: 待校验严重程度。

    Returns:
        校验通过时返回 `None`。

    Raises:
        ValueError: 严重程度不在稳定 Literal 域内时抛出。
    """

    if severity not in ("blocking", "material", "informational", "config_only"):
        raise ValueError(f"不支持的约束严重程度：{severity}")


def _validate_text_tuple(
    values: tuple[str, ...],
    field_name: str,
    chapter_id: int,
    *,
    allow_empty: bool = False,
) -> None:
    """校验文本元组。

    Args:
        values: 待校验文本元组。
        field_name: 字段名，用于错误信息。
        chapter_id: 当前章节编号。
        allow_empty: 是否允许空元组。

    Returns:
        校验通过时返回 `None`。

    Raises:
        ValueError: 元组为空或包含空白文本时抛出。
    """

    if not values and not allow_empty:
        raise ValueError(f"章节 {chapter_id} {field_name} 不能为空")
    if any(not value.strip() for value in values):
        raise ValueError(f"章节 {chapter_id} {field_name} 存在空值")
