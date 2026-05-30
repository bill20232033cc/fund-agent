"""章节事实 typed projection，见基金分析模板第 0-7 章。

本模块属于 Agent 层 `fund_agent/fund` 基金能力，只把已经抽取完成的
`StructuredFundDataBundle` 投影为后续章节写作可消费的 typed facts。它不读取
年报 PDF、cache、下载 helper、外部来源适配器，也不调用 LLM、Service、Host 或 dayu。
`ChapterEvidenceSourceKind` 在 extractor 层 `EvidenceSourceKind` 的方向上扩展
`unknown`，用于投影层遇到来源闭集外锚点时 fail-closed 保留事实而不伪造来源。
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import TYPE_CHECKING, Final, Literal, TypeGuard, get_args

from fund_agent.fund.extractors.models import EvidenceAnchor, ExtractedField
from fund_agent.fund.fund_type import FundType
from fund_agent.fund.template.contracts import (
    ChapterContract,
    LensKey,
    get_chapter_contract,
    resolve_preferred_lens,
)
from fund_agent.fund.template.item_rules import (
    TemplateItemRuleDecision,
    evaluate_template_item_rules,
)

if TYPE_CHECKING:
    from fund_agent.fund.data.nav_data import NavDataResult
    from fund_agent.fund.data_extractor import StructuredFundDataBundle


ChapterFactSchemaVersion = Literal["chapter_fact_projection.v1"]
ChapterFactFundType = FundType | Literal["unknown"]

ChapterFactStatus = Literal[
    "available",
    "missing",
    "not_applicable",
    "unavailable",
    "unknown",
]

ChapterFactMissingReason = Literal[
    "classified_fund_type_missing",
    "classified_fund_type_invalid",
    "field_missing",
    "field_not_applicable",
    "field_unavailable",
    "evidence_missing",
    "accepted_chapter_conclusions_missing",
    "cross_period_comparison_missing",
    "unsupported_facet_inference",
]

ChapterFacetStatus = Literal["resolved", "empty", "unknown"]
ChapterFacetSource = Literal["preferred_lens", "item_rule_manifest", "empty", "unknown"]
ChapterEvidenceSourceKind = Literal["annual_report", "external_api", "derived", "unknown"]

CHAPTER_FACT_SCHEMA_VERSION: ChapterFactSchemaVersion = "chapter_fact_projection.v1"
DEFAULT_CHAPTER_FACT_IDS: Final[tuple[int, ...]] = tuple(range(8))
_SUPPORTED_FUND_TYPES: Final[frozenset[str]] = frozenset(get_args(FundType))
_SUPPORTED_ANCHOR_SOURCE_KINDS: Final[frozenset[str]] = frozenset(
    ("annual_report", "external_api", "derived")
)

_SOURCE_FIELD_IDS: Final[dict[str, str]] = {
    "basic_identity": "structured.basic_identity",
    "product_profile": "structured.product_profile",
    "benchmark": "structured.benchmark",
    "index_profile": "structured.index_profile",
    "fee_schedule": "structured.fee_schedule",
    "turnover_rate": "structured.turnover_rate",
    "nav_benchmark_performance": "structured.nav_benchmark_performance",
    "investor_return": "structured.investor_return",
    "tracking_error": "structured.tracking_error",
    "share_change": "structured.share_change",
    "manager_alignment": "structured.manager_alignment",
    "manager_strategy_text": "structured.manager_strategy_text",
    "holdings_snapshot": "structured.holdings_snapshot",
    "holder_structure": "structured.holder_structure",
    "bond_risk_evidence": "structured.bond_risk_evidence",
    "nav_data": "structured.nav_data",
}

_ACCEPTED_CHAPTER_CONCLUSIONS_SOURCE_FIELD_ID: Final[str] = (
    "synthetic.accepted_chapter_conclusions"
)
_CROSS_PERIOD_COMPARISON_SOURCE_FIELD_ID: Final[str] = "synthetic.cross_period_comparison"


@dataclass(frozen=True, slots=True)
class ChapterEvidenceAnchor:
    """章节证据锚点，供模板第 0-7 章 fact 引用。

    Attributes:
        anchor_id: 本次投影内稳定锚点 ID。
        source_kind: 证据来源类型；无法落入 extractor 闭集时为 `unknown`。
        document_year: 文档年份，非文档来源可为 `None`。
        section_id: 年报章节编号或派生来源标识。
        page_number: 年报页码；无法确定时为 `None`。
        table_id: 表格编号；非表格证据可为 `None`。
        row_locator: 行级或记录级定位。
        note: 附加说明。
    """

    anchor_id: str
    source_kind: ChapterEvidenceSourceKind
    document_year: int | None
    section_id: str | None
    page_number: int | None
    table_id: str | None
    row_locator: str | None
    note: str | None


@dataclass(frozen=True, slots=True)
class ChapterFactEntry:
    """章节事实条目，见模板第 0-7 章 CHAPTER_CONTRACT 输入。

    Attributes:
        fact_id: 本次投影内稳定事实 ID。
        chapter_id: 模板章节编号。
        field_path: 结构化字段路径。
        source_field_id: 稳定来源字段 ID。
        source_field_name: 来源字段名。
        status: 当前事实状态。
        value: 结构化事实值；缺失或不可用时可为 `None`。
        extraction_mode: extractor 抽取模式；非 `ExtractedField` 可为 `None`。
        evidence_anchor_ids: 本章内证据锚点 ID。
        missing_reason: 缺失、不可用、不适用或缺锚点原因。
        missing_detail: 面向审计的原因细节。
        required_by: 当前事实支撑的模板或 ITEM_RULE 约束。
    """

    fact_id: str
    chapter_id: int
    field_path: str
    source_field_id: str
    source_field_name: str
    status: ChapterFactStatus
    value: object | None
    extraction_mode: str | None
    evidence_anchor_ids: tuple[str, ...]
    missing_reason: ChapterFactMissingReason | None
    missing_detail: str | None
    required_by: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class ChapterFacetResolution:
    """章节 facet 解析结果，见模板第 0-7 章 preferred_lens。

    Attributes:
        chapter_id: 模板章节编号。
        fund_type: 标准基金类型或 `unknown`。
        facets: 已被结构化证据精确断言的 facet。
        status: facet 解析状态。
        reason: 解析说明。
        source: 解析来源。
        non_asserted_facets: 兼容但未断言的候选标签。
    """

    chapter_id: int
    fund_type: ChapterFactFundType
    facets: tuple[str, ...]
    status: ChapterFacetStatus
    reason: str
    source: ChapterFacetSource
    non_asserted_facets: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class ChapterLensResolution:
    """章节 preferred_lens 解析结果，见模板第 0-7 章。

    Attributes:
        chapter_id: 模板章节编号。
        fund_type: 标准基金类型或 `unknown`。
        lens_key: 命中的 lens key；基金类型未知时为 `unknown`。
        used_default: 是否使用 default fallback。
        statements: lens 说明文本。
        facets_any: lens 声明的候选 facet。
        priority: lens 优先级。
        missing_reason: 基金类型缺失或非法时的原因。
    """

    chapter_id: int
    fund_type: ChapterFactFundType
    lens_key: LensKey | Literal["unknown"]
    used_default: bool
    statements: tuple[str, ...]
    facets_any: tuple[str, ...]
    priority: str | None
    missing_reason: ChapterFactMissingReason | None


@dataclass(frozen=True, slots=True)
class ChapterItemRuleProjection:
    """章节 ITEM_RULE 投影，见模板第 1/2 章条件条目规则。

    Attributes:
        chapter_id: 模板章节编号。
        decisions: 当前章节的 ITEM_RULE 评估结果。
    """

    chapter_id: int
    decisions: tuple[TemplateItemRuleDecision, ...]


@dataclass(frozen=True, slots=True)
class ChapterFactInput:
    """单章 typed fact 输入，见模板第 0-7 章。

    Attributes:
        chapter_id: 模板章节编号。
        title: 章节标题。
        contract: 当前章节 CHAPTER_CONTRACT。
        fund_type: 标准基金类型或 `unknown`。
        classification_basis: 基金类型分类依据。
        facet_resolution: 当前章节 facet 解析结果。
        lens_resolution: 当前章节 preferred_lens 解析结果。
        item_rule_projection: 当前章节 ITEM_RULE 投影。
        facts: 当前章节事实条目。
        evidence_anchors: 当前章节证据锚点。
        missing_reasons: 当前章节去重后的缺失原因。
        source_field_ids: 当前章节去重后的来源字段 ID。
    """

    chapter_id: int
    title: str
    contract: ChapterContract
    fund_type: ChapterFactFundType
    classification_basis: tuple[str, ...]
    facet_resolution: ChapterFacetResolution
    lens_resolution: ChapterLensResolution
    item_rule_projection: ChapterItemRuleProjection
    facts: tuple[ChapterFactEntry, ...]
    evidence_anchors: tuple[ChapterEvidenceAnchor, ...]
    missing_reasons: tuple[ChapterFactMissingReason, ...]
    source_field_ids: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class ChapterFactProjection:
    """章节事实投影根对象，见模板第 0-7 章。

    Attributes:
        schema_version: 当前投影 schema 版本。
        fund_code: 基金代码。
        report_year: 年报年份。
        fund_type: 标准基金类型或 `unknown`。
        classification_basis: 基金类型分类依据。
        chapters: 章节事实输入列表。
        global_missing_reasons: 全局去重后的缺失原因。
    """

    schema_version: ChapterFactSchemaVersion
    fund_code: str
    report_year: int
    fund_type: ChapterFactFundType
    classification_basis: tuple[str, ...]
    chapters: tuple[ChapterFactInput, ...]
    global_missing_reasons: tuple[ChapterFactMissingReason, ...]


@dataclass(frozen=True, slots=True)
class _ChapterFieldSpec:
    """章节字段映射规格，见模板第 0-7 章。

    Attributes:
        chapter_id: 模板章节编号。
        field_name: `StructuredFundDataBundle` 字段名。
        source_field_id: 稳定来源字段 ID。
        required_by: 当前字段支撑的模板约束。
        item_rule_ids: 当前字段支撑的 ITEM_RULE 编号。
    """

    chapter_id: int
    field_name: str
    source_field_id: str
    required_by: tuple[str, ...]
    item_rule_ids: tuple[str, ...] = ()


_CHAPTER_FIELD_SPECS: Final[tuple[_ChapterFieldSpec, ...]] = (
    _ChapterFieldSpec(0, "basic_identity", _SOURCE_FIELD_IDS["basic_identity"], ("CHAPTER_CONTRACT.chapter_0",)),
    _ChapterFieldSpec(
        0,
        "nav_benchmark_performance",
        _SOURCE_FIELD_IDS["nav_benchmark_performance"],
        ("CHAPTER_CONTRACT.chapter_0",),
    ),
    _ChapterFieldSpec(0, "tracking_error", _SOURCE_FIELD_IDS["tracking_error"], ("CHAPTER_CONTRACT.chapter_0",)),
    _ChapterFieldSpec(0, "fee_schedule", _SOURCE_FIELD_IDS["fee_schedule"], ("CHAPTER_CONTRACT.chapter_0",)),
    _ChapterFieldSpec(
        0,
        "bond_risk_evidence",
        _SOURCE_FIELD_IDS["bond_risk_evidence"],
        ("CHAPTER_CONTRACT.chapter_0",),
    ),
    _ChapterFieldSpec(1, "basic_identity", _SOURCE_FIELD_IDS["basic_identity"], ("CHAPTER_CONTRACT.chapter_1",)),
    _ChapterFieldSpec(1, "product_profile", _SOURCE_FIELD_IDS["product_profile"], ("CHAPTER_CONTRACT.chapter_1",)),
    _ChapterFieldSpec(1, "benchmark", _SOURCE_FIELD_IDS["benchmark"], ("CHAPTER_CONTRACT.chapter_1",)),
    _ChapterFieldSpec(
        1,
        "index_profile",
        _SOURCE_FIELD_IDS["index_profile"],
        ("CHAPTER_CONTRACT.chapter_1",),
        ("chapter_1_index_constituents",),
    ),
    _ChapterFieldSpec(1, "fee_schedule", _SOURCE_FIELD_IDS["fee_schedule"], ("CHAPTER_CONTRACT.chapter_1",)),
    _ChapterFieldSpec(
        2,
        "nav_benchmark_performance",
        _SOURCE_FIELD_IDS["nav_benchmark_performance"],
        ("CHAPTER_CONTRACT.chapter_2",),
        ("chapter_2_alpha_yearly_breakdown",),
    ),
    _ChapterFieldSpec(2, "benchmark", _SOURCE_FIELD_IDS["benchmark"], ("CHAPTER_CONTRACT.chapter_2",)),
    _ChapterFieldSpec(
        2,
        "tracking_error",
        _SOURCE_FIELD_IDS["tracking_error"],
        ("CHAPTER_CONTRACT.chapter_2",),
        ("chapter_2_tracking_error_analysis",),
    ),
    _ChapterFieldSpec(2, "fee_schedule", _SOURCE_FIELD_IDS["fee_schedule"], ("CHAPTER_CONTRACT.chapter_2",)),
    _ChapterFieldSpec(2, "nav_data", _SOURCE_FIELD_IDS["nav_data"], ("CHAPTER_CONTRACT.chapter_2",)),
    _ChapterFieldSpec(3, "basic_identity", _SOURCE_FIELD_IDS["basic_identity"], ("CHAPTER_CONTRACT.chapter_3",)),
    _ChapterFieldSpec(
        3,
        "manager_strategy_text",
        _SOURCE_FIELD_IDS["manager_strategy_text"],
        ("CHAPTER_CONTRACT.chapter_3",),
    ),
    _ChapterFieldSpec(
        3,
        "holdings_snapshot",
        _SOURCE_FIELD_IDS["holdings_snapshot"],
        ("CHAPTER_CONTRACT.chapter_3",),
    ),
    _ChapterFieldSpec(3, "turnover_rate", _SOURCE_FIELD_IDS["turnover_rate"], ("CHAPTER_CONTRACT.chapter_3",)),
    _ChapterFieldSpec(
        3,
        "manager_alignment",
        _SOURCE_FIELD_IDS["manager_alignment"],
        ("CHAPTER_CONTRACT.chapter_3",),
    ),
    _ChapterFieldSpec(
        3,
        "holder_structure",
        _SOURCE_FIELD_IDS["holder_structure"],
        ("CHAPTER_CONTRACT.chapter_3",),
    ),
    _ChapterFieldSpec(
        4,
        "nav_benchmark_performance",
        _SOURCE_FIELD_IDS["nav_benchmark_performance"],
        ("CHAPTER_CONTRACT.chapter_4",),
    ),
    _ChapterFieldSpec(4, "investor_return", _SOURCE_FIELD_IDS["investor_return"], ("CHAPTER_CONTRACT.chapter_4",)),
    _ChapterFieldSpec(4, "share_change", _SOURCE_FIELD_IDS["share_change"], ("CHAPTER_CONTRACT.chapter_4",)),
    _ChapterFieldSpec(
        4,
        "holder_structure",
        _SOURCE_FIELD_IDS["holder_structure"],
        ("CHAPTER_CONTRACT.chapter_4",),
    ),
    _ChapterFieldSpec(4, "fee_schedule", _SOURCE_FIELD_IDS["fee_schedule"], ("CHAPTER_CONTRACT.chapter_4",)),
    _ChapterFieldSpec(5, "basic_identity", _SOURCE_FIELD_IDS["basic_identity"], ("CHAPTER_CONTRACT.chapter_5",)),
    _ChapterFieldSpec(5, "share_change", _SOURCE_FIELD_IDS["share_change"], ("CHAPTER_CONTRACT.chapter_5",)),
    _ChapterFieldSpec(
        5,
        "holdings_snapshot",
        _SOURCE_FIELD_IDS["holdings_snapshot"],
        ("CHAPTER_CONTRACT.chapter_5",),
    ),
    _ChapterFieldSpec(5, "turnover_rate", _SOURCE_FIELD_IDS["turnover_rate"], ("CHAPTER_CONTRACT.chapter_5",)),
    _ChapterFieldSpec(5, "fee_schedule", _SOURCE_FIELD_IDS["fee_schedule"], ("CHAPTER_CONTRACT.chapter_5",)),
    _ChapterFieldSpec(
        5,
        "manager_strategy_text",
        _SOURCE_FIELD_IDS["manager_strategy_text"],
        ("CHAPTER_CONTRACT.chapter_5",),
    ),
    _ChapterFieldSpec(6, "basic_identity", _SOURCE_FIELD_IDS["basic_identity"], ("CHAPTER_CONTRACT.chapter_6",)),
    _ChapterFieldSpec(6, "fee_schedule", _SOURCE_FIELD_IDS["fee_schedule"], ("CHAPTER_CONTRACT.chapter_6",)),
    _ChapterFieldSpec(6, "tracking_error", _SOURCE_FIELD_IDS["tracking_error"], ("CHAPTER_CONTRACT.chapter_6",)),
    _ChapterFieldSpec(6, "turnover_rate", _SOURCE_FIELD_IDS["turnover_rate"], ("CHAPTER_CONTRACT.chapter_6",)),
    _ChapterFieldSpec(
        6,
        "holdings_snapshot",
        _SOURCE_FIELD_IDS["holdings_snapshot"],
        ("CHAPTER_CONTRACT.chapter_6",),
    ),
    _ChapterFieldSpec(6, "share_change", _SOURCE_FIELD_IDS["share_change"], ("CHAPTER_CONTRACT.chapter_6",)),
    _ChapterFieldSpec(
        6,
        "bond_risk_evidence",
        _SOURCE_FIELD_IDS["bond_risk_evidence"],
        ("CHAPTER_CONTRACT.chapter_6",),
    ),
    _ChapterFieldSpec(6, "nav_data", _SOURCE_FIELD_IDS["nav_data"], ("CHAPTER_CONTRACT.chapter_6",)),
    _ChapterFieldSpec(7, "basic_identity", _SOURCE_FIELD_IDS["basic_identity"], ("CHAPTER_CONTRACT.chapter_7",)),
    _ChapterFieldSpec(
        7,
        "nav_benchmark_performance",
        _SOURCE_FIELD_IDS["nav_benchmark_performance"],
        ("CHAPTER_CONTRACT.chapter_7",),
    ),
    _ChapterFieldSpec(7, "tracking_error", _SOURCE_FIELD_IDS["tracking_error"], ("CHAPTER_CONTRACT.chapter_7",)),
    _ChapterFieldSpec(7, "fee_schedule", _SOURCE_FIELD_IDS["fee_schedule"], ("CHAPTER_CONTRACT.chapter_7",)),
    _ChapterFieldSpec(
        7,
        "manager_alignment",
        _SOURCE_FIELD_IDS["manager_alignment"],
        ("CHAPTER_CONTRACT.chapter_7",),
    ),
    _ChapterFieldSpec(
        7,
        "bond_risk_evidence",
        _SOURCE_FIELD_IDS["bond_risk_evidence"],
        ("CHAPTER_CONTRACT.chapter_7",),
    ),
)


@dataclass(frozen=True, slots=True)
class ChapterFactProvider:
    """章节事实 provider façade，见模板第 0-7 章。

    该类是 concrete façade，不是 Protocol，不承担 Service 编排、tool routing 或 runtime 生命周期。
    """

    def project(
        self,
        bundle: StructuredFundDataBundle,
        *,
        chapter_ids: tuple[int, ...] = DEFAULT_CHAPTER_FACT_IDS,
    ) -> ChapterFactProjection:
        """把结构化基金数据包投影为章节事实输入。

        Args:
            bundle: 已抽取完成的结构化基金数据包。
            chapter_ids: 需要投影的模板章节编号，必须非空、唯一且落在 0-7。

        Returns:
            章节事实投影。

        Raises:
            ValueError: 当章节编号为空、重复或越界时抛出。
        """

        return project_chapter_facts(bundle, chapter_ids=chapter_ids)


def project_chapter_facts(
    bundle: StructuredFundDataBundle,
    *,
    chapter_ids: tuple[int, ...] = DEFAULT_CHAPTER_FACT_IDS,
) -> ChapterFactProjection:
    """把 `StructuredFundDataBundle` 投影为模板第 0-7 章 typed facts。

    Args:
        bundle: 已抽取完成的结构化基金数据包。
        chapter_ids: 需要投影的模板章节编号，必须非空、唯一且落在 0-7。

    Returns:
        可供后续章节写作和审计消费的 `ChapterFactProjection`。

    Raises:
        ValueError: 当章节编号为空、重复或越界时抛出。
    """

    normalized_chapter_ids = _validate_chapter_ids(chapter_ids)
    fund_type, classification_basis, fund_type_missing_reason = _read_classified_fund_type(bundle)
    item_rule_decisions = _evaluate_item_rule_decisions(fund_type)
    chapters = tuple(
        _project_chapter(
            bundle,
            chapter_id=chapter_id,
            fund_type=fund_type,
            classification_basis=classification_basis,
            fund_type_missing_reason=fund_type_missing_reason,
            all_item_rule_decisions=item_rule_decisions,
        )
        for chapter_id in normalized_chapter_ids
    )
    global_missing_reasons = _unique_reasons(
        (*(() if fund_type_missing_reason is None else (fund_type_missing_reason,)),)
        + tuple(reason for chapter in chapters for reason in chapter.missing_reasons)
    )
    return ChapterFactProjection(
        schema_version=CHAPTER_FACT_SCHEMA_VERSION,
        fund_code=bundle.fund_code,
        report_year=bundle.report_year,
        fund_type=fund_type,
        classification_basis=classification_basis,
        chapters=chapters,
        global_missing_reasons=global_missing_reasons,
    )


def _validate_chapter_ids(chapter_ids: tuple[int, ...]) -> tuple[int, ...]:
    """校验模板第 0-7 章章节编号。

    Args:
        chapter_ids: 调用方请求的章节编号。

    Returns:
        原顺序返回的章节编号。

    Raises:
        ValueError: 当章节编号为空、重复或越界时抛出。
    """

    if not chapter_ids:
        raise ValueError("chapter_ids 不能为空")
    if len(set(chapter_ids)) != len(chapter_ids):
        raise ValueError("chapter_ids 不能重复")
    invalid_ids = tuple(chapter_id for chapter_id in chapter_ids if chapter_id not in DEFAULT_CHAPTER_FACT_IDS)
    if invalid_ids:
        raise ValueError(f"chapter_ids 包含未知模板章节：{invalid_ids}")
    return chapter_ids


def _read_classified_fund_type(
    bundle: StructuredFundDataBundle,
) -> tuple[ChapterFactFundType, tuple[str, ...], ChapterFactMissingReason | None]:
    """读取结构化基金类型，见模板第 1 章“基金类型与分类标签”。

    Args:
        bundle: 已抽取完成的结构化基金数据包。

    Returns:
        `(fund_type, classification_basis, missing_reason)` 三元组。

    Raises:
        无显式抛出。
    """

    identity_value = bundle.basic_identity.value
    if not isinstance(identity_value, dict):
        return "unknown", (), "classified_fund_type_missing"

    raw_fund_type = identity_value.get("classified_fund_type")
    classification_basis = _normalize_basis(identity_value.get("classification_basis"))
    if not isinstance(raw_fund_type, str) or not raw_fund_type.strip():
        return "unknown", classification_basis, "classified_fund_type_missing"
    if not _is_supported_fund_type(raw_fund_type):
        return "unknown", classification_basis, "classified_fund_type_invalid"
    return raw_fund_type, classification_basis, None


def _normalize_basis(value: object) -> tuple[str, ...]:
    """规范化基金类型分类依据，见模板第 1 章。

    Args:
        value: 结构化字段中的原始分类依据。

    Returns:
        字符串元组，忽略空值。

    Raises:
        无显式抛出。
    """

    if value is None:
        return ()
    if isinstance(value, str):
        return (value,) if value.strip() else ()
    if isinstance(value, (tuple, list)):
        return tuple(str(item) for item in value if str(item).strip())
    return (str(value),) if str(value).strip() else ()


def _is_supported_fund_type(value: str) -> TypeGuard[FundType]:
    """判断字符串是否为标准基金类型闭集成员。

    Args:
        value: 待判断的字符串。

    Returns:
        属于 `FundType` 闭集时返回 `True`。

    Raises:
        无显式抛出。
    """

    return value in _SUPPORTED_FUND_TYPES


def _chapter_field_specs(chapter_id: int) -> tuple[_ChapterFieldSpec, ...]:
    """读取模板章节对应的结构化字段映射。

    Args:
        chapter_id: 模板章节编号。

    Returns:
        当前章节的字段映射。

    Raises:
        ValueError: 当章节编号无效时抛出。
    """

    _validate_chapter_ids((chapter_id,))
    return tuple(spec for spec in _CHAPTER_FIELD_SPECS if spec.chapter_id == chapter_id)


def _project_chapter(
    bundle: StructuredFundDataBundle,
    *,
    chapter_id: int,
    fund_type: ChapterFactFundType,
    classification_basis: tuple[str, ...],
    fund_type_missing_reason: ChapterFactMissingReason | None,
    all_item_rule_decisions: tuple[TemplateItemRuleDecision, ...],
) -> ChapterFactInput:
    """投影单个模板章节的事实输入。

    Args:
        bundle: 已抽取完成的结构化基金数据包。
        chapter_id: 模板章节编号。
        fund_type: 标准基金类型或 `unknown`。
        classification_basis: 基金类型分类依据。
        fund_type_missing_reason: 基金类型缺失或非法原因。
        all_item_rule_decisions: 全局一次性 ITEM_RULE 评估结果。

    Returns:
        单章事实输入。

    Raises:
        ValueError: 当章节编号无效或 fact 锚点引用不完整时抛出。
    """

    contract = get_chapter_contract(chapter_id)
    lens_resolution = _resolve_chapter_lens(
        chapter_id,
        fund_type=fund_type,
        fund_type_missing_reason=fund_type_missing_reason,
    )
    facet_resolution = _resolve_chapter_facets(
        chapter_id,
        fund_type=fund_type,
        lens_resolution=lens_resolution,
    )
    item_rule_projection = _item_rule_decisions_for_chapter(
        chapter_id,
        all_item_rule_decisions,
    )
    specs = _chapter_field_specs(chapter_id)
    raw_anchors = tuple(anchor for spec in specs for anchor in _anchors_for_field(bundle, spec))
    evidence_anchors = _dedupe_chapter_anchors(
        bundle.fund_code,
        bundle.report_year,
        chapter_id,
        raw_anchors,
    )
    anchor_ids_by_key = {_anchor_key(anchor): anchor.anchor_id for anchor in evidence_anchors}
    facts = tuple(
        _project_field_fact(
            bundle,
            spec=spec,
            anchor_ids_by_key=anchor_ids_by_key,
        )
        for spec in specs
    ) + _synthetic_missing_facts(bundle, chapter_id)
    _ensure_fact_anchor_refs_exist(facts, evidence_anchors)
    missing_reasons = _unique_reasons(
        tuple(reason for fact in facts if (reason := fact.missing_reason) is not None)
        + (("unsupported_facet_inference",) if facet_resolution.non_asserted_facets else ())
        + (tuple() if lens_resolution.missing_reason is None else (lens_resolution.missing_reason,))
    )
    source_field_ids = _unique_strings(tuple(fact.source_field_id for fact in facts))
    return ChapterFactInput(
        chapter_id=chapter_id,
        title=contract.title,
        contract=contract,
        fund_type=fund_type,
        classification_basis=classification_basis,
        facet_resolution=facet_resolution,
        lens_resolution=lens_resolution,
        item_rule_projection=item_rule_projection,
        facts=facts,
        evidence_anchors=evidence_anchors,
        missing_reasons=missing_reasons,
        source_field_ids=source_field_ids,
    )


def _resolve_chapter_facets(
    chapter_id: int,
    *,
    fund_type: ChapterFactFundType,
    lens_resolution: ChapterLensResolution,
) -> ChapterFacetResolution:
    """解析章节 facet，见模板 preferred_lens 的 facets_any。

    Args:
        chapter_id: 模板章节编号。
        fund_type: 标准基金类型或 `unknown`。
        lens_resolution: 当前章节 preferred_lens 解析结果。

    Returns:
        当前章节 facet 解析结果。

    Raises:
        无显式抛出。
    """

    if fund_type == "unknown":
        return ChapterFacetResolution(
            chapter_id=chapter_id,
            fund_type=fund_type,
            facets=(),
            status="unknown",
            reason="基金类型缺失或非法，跳过 facet 解析",
            source="unknown",
            non_asserted_facets=(),
        )
    if not lens_resolution.facets_any:
        return ChapterFacetResolution(
            chapter_id=chapter_id,
            fund_type=fund_type,
            facets=(),
            status="empty",
            reason="当前 preferred_lens 未声明候选 facet",
            source="empty",
            non_asserted_facets=(),
        )
    return ChapterFacetResolution(
        chapter_id=chapter_id,
        fund_type=fund_type,
        facets=(),
        status="empty",
        reason="unsupported_facet_inference: 当前结构化字段不能精确断言 subtype",
        source="preferred_lens",
        non_asserted_facets=lens_resolution.facets_any,
    )


def _resolve_chapter_lens(
    chapter_id: int,
    *,
    fund_type: ChapterFactFundType,
    fund_type_missing_reason: ChapterFactMissingReason | None,
) -> ChapterLensResolution:
    """解析章节 preferred_lens，见模板第 0-7 章。

    Args:
        chapter_id: 模板章节编号。
        fund_type: 标准基金类型或 `unknown`。
        fund_type_missing_reason: 基金类型缺失或非法原因。

    Returns:
        当前章节 preferred_lens 解析结果。

    Raises:
        ValueError: 当有效基金类型无法解析 lens 时由模板 API 抛出。
    """

    if fund_type == "unknown":
        return ChapterLensResolution(
            chapter_id=chapter_id,
            fund_type=fund_type,
            lens_key="unknown",
            used_default=False,
            statements=(),
            facets_any=(),
            priority=None,
            missing_reason=fund_type_missing_reason,
        )

    # 经过 `_read_classified_fund_type` 和分支判断后，`fund_type` 已窄化为 `FundType`，
    # 因此可以传给 CHAPTER_CONTRACT / ITEM_RULE 的严格 FundType API。
    lens = resolve_preferred_lens(chapter_id, fund_type)
    return ChapterLensResolution(
        chapter_id=chapter_id,
        fund_type=fund_type,
        lens_key=lens.fund_type,
        used_default=lens.fund_type == "default",
        statements=lens.statements,
        facets_any=lens.facets_any,
        priority=lens.priority,
        missing_reason=None,
    )


def _evaluate_item_rule_decisions(
    fund_type: ChapterFactFundType,
) -> tuple[TemplateItemRuleDecision, ...]:
    """全局一次性评估 ITEM_RULE，见模板第 1/2 章。

    Args:
        fund_type: 标准基金类型或 `unknown`。

    Returns:
        ITEM_RULE 决策元组；基金类型未知时返回空元组。

    Raises:
        ValueError: 当有效基金类型无法通过 ITEM_RULE 校验时由模板 API 抛出。
    """

    if fund_type == "unknown":
        return ()
    return evaluate_template_item_rules(fund_type=fund_type, facets=())


def _item_rule_decisions_for_chapter(
    chapter_id: int,
    decisions: tuple[TemplateItemRuleDecision, ...],
) -> ChapterItemRuleProjection:
    """按章节过滤 ITEM_RULE 决策。

    Args:
        chapter_id: 模板章节编号。
        decisions: 全局 ITEM_RULE 决策。

    Returns:
        当前章节的 ITEM_RULE 投影。

    Raises:
        无显式抛出。
    """

    return ChapterItemRuleProjection(
        chapter_id=chapter_id,
        decisions=tuple(decision for decision in decisions if decision.chapter_id == chapter_id),
    )


def _anchors_for_field(
    bundle: StructuredFundDataBundle,
    spec: _ChapterFieldSpec,
) -> tuple[EvidenceAnchor, ...]:
    """收集字段普通证据锚点，见模板第 0-7 章证据输入。

    Args:
        bundle: 已抽取完成的结构化基金数据包。
        spec: 章节字段映射。

    Returns:
        可展开为 `ChapterEvidenceAnchor` 的普通证据锚点。

    Raises:
        无显式抛出。
    """

    if spec.field_name == "bond_risk_evidence":
        return ()
    value = getattr(bundle, spec.field_name)
    if isinstance(value, ExtractedField):
        return value.anchors
    if spec.field_name == "nav_data":
        return _nav_data_anchors(value)
    return ()


def _nav_data_anchors(nav_data: NavDataResult) -> tuple[EvidenceAnchor, ...]:
    """把 NAV 数据结果转换为外部 API 证据锚点，见模板第 2/6 章。

    Args:
        nav_data: 净值数据读取结果。

    Returns:
        NAV 可用时返回单个 `external_api` 锚点，否则返回空元组。

    Raises:
        无显式抛出。
    """

    if nav_data.unavailable or not nav_data.records:
        return ()
    note = f"source={nav_data.source}; cached={nav_data.cached}; records={len(nav_data.records)}"
    return (
        EvidenceAnchor(
            source_kind="external_api",
            document_year=None,
            section_id="external:nav_data",
            page_number=None,
            table_id=None,
            row_locator=f"nav_data:{nav_data.fund_code}",
            note=note,
        ),
    )


def _project_field_fact(
    bundle: StructuredFundDataBundle,
    *,
    spec: _ChapterFieldSpec,
    anchor_ids_by_key: dict[tuple[object, ...], str],
) -> ChapterFactEntry:
    """投影单个字段事实，见模板第 0-7 章。

    Args:
        bundle: 已抽取完成的结构化基金数据包。
        spec: 章节字段映射。
        anchor_ids_by_key: 章节内证据锚点 key 到 ID 的映射。

    Returns:
        单个章节事实条目。

    Raises:
        ValueError: 当字段类型不受支持时抛出。
    """

    value = getattr(bundle, spec.field_name)
    if isinstance(value, ExtractedField):
        if spec.field_name == "bond_risk_evidence":
            return _project_bond_risk_evidence_fact(bundle, spec=spec, field=value)
        return _project_extracted_field_fact(
            bundle,
            spec=spec,
            field=value,
            anchor_ids_by_key=anchor_ids_by_key,
        )
    if spec.field_name == "nav_data":
        return _project_nav_data_fact(bundle, spec=spec, nav_data=value, anchor_ids_by_key=anchor_ids_by_key)
    raise ValueError(f"不支持的章节事实字段类型：field_name={spec.field_name}")


def _project_extracted_field_fact(
    bundle: StructuredFundDataBundle,
    *,
    spec: _ChapterFieldSpec,
    field: ExtractedField[object],
    anchor_ids_by_key: dict[tuple[object, ...], str],
) -> ChapterFactEntry:
    """投影 `ExtractedField` 事实，见模板第 0-7 章。

    Args:
        bundle: 已抽取完成的结构化基金数据包。
        spec: 章节字段映射。
        field: 带证据的抽取字段。
        anchor_ids_by_key: 章节内证据锚点 key 到 ID 的映射。

    Returns:
        单个章节事实条目。

    Raises:
        无显式抛出。
    """

    if field.value is None or field.extraction_mode == "missing":
        status, missing_reason = _missing_status_for_field(spec.field_name, field.note)
        return _fact_entry(
            bundle,
            spec=spec,
            status=status,
            value=None,
            extraction_mode=field.extraction_mode,
            evidence_anchor_ids=(),
            missing_reason=missing_reason,
            missing_detail=field.note,
        )

    anchor_ids = tuple(anchor_ids_by_key[_anchor_key(_chapter_anchor_from_raw(anchor, ""))] for anchor in field.anchors)
    missing_reason: ChapterFactMissingReason | None = None
    missing_detail: str | None = None
    if not anchor_ids:
        missing_reason = "evidence_missing"
        missing_detail = f"{spec.field_name} 有结构化值但缺少证据锚点"
    return _fact_entry(
        bundle,
        spec=spec,
        status="available",
        value=field.value,
        extraction_mode=field.extraction_mode,
        evidence_anchor_ids=anchor_ids,
        missing_reason=missing_reason,
        missing_detail=missing_detail,
    )


def _project_bond_risk_evidence_fact(
    bundle: StructuredFundDataBundle,
    *,
    spec: _ChapterFieldSpec,
    field: ExtractedField[object],
) -> ChapterFactEntry:
    """投影债券风险证据事实，见模板第 6 章“核心风险”。

    Args:
        bundle: 已抽取完成的结构化基金数据包。
        spec: 章节字段映射。
        field: 债券风险证据字段。

    Returns:
        单个章节事实条目；组级 anchors 保留在 value 内部，不展开为章节锚点。

    Raises:
        无显式抛出。
    """

    if field.value is None or field.extraction_mode == "missing":
        status, missing_reason = _missing_status_for_field(spec.field_name, field.note)
        return _fact_entry(
            bundle,
            spec=spec,
            status=status,
            value=None,
            extraction_mode=field.extraction_mode,
            evidence_anchor_ids=(),
            missing_reason=missing_reason,
            missing_detail=field.note,
        )
    return _fact_entry(
        bundle,
        spec=spec,
        status="available",
        value=field.value,
        extraction_mode=field.extraction_mode,
        evidence_anchor_ids=(),
        missing_reason=None,
        missing_detail="bond_risk_evidence 组级锚点引用保留在 value.anchors 内，未展开为 ChapterEvidenceAnchor",
    )


def _project_nav_data_fact(
    bundle: StructuredFundDataBundle,
    *,
    spec: _ChapterFieldSpec,
    nav_data: NavDataResult,
    anchor_ids_by_key: dict[tuple[object, ...], str],
) -> ChapterFactEntry:
    """投影 NAV 数据事实，见模板第 2 章 R=A+B-C 和第 6 章核心风险。

    Args:
        bundle: 已抽取完成的结构化基金数据包。
        spec: 章节字段映射。
        nav_data: 净值数据读取结果。
        anchor_ids_by_key: 章节内证据锚点 key 到 ID 的映射。

    Returns:
        NAV 三态事实：available、missing 或 unavailable。

    Raises:
        无显式抛出。
    """

    if nav_data.unavailable:
        return _fact_entry(
            bundle,
            spec=spec,
            status="unavailable",
            value=None,
            extraction_mode=None,
            evidence_anchor_ids=(),
            missing_reason="field_unavailable",
            missing_detail=nav_data.unavailable_reason,
        )
    if not nav_data.records:
        return _fact_entry(
            bundle,
            spec=spec,
            status="missing",
            value=None,
            extraction_mode=None,
            evidence_anchor_ids=(),
            missing_reason="field_missing",
            missing_detail="nav_data records 为空且未标记 unavailable",
        )
    anchor_ids = tuple(
        anchor_ids_by_key[_anchor_key(_chapter_anchor_from_raw(anchor, ""))]
        for anchor in _nav_data_anchors(nav_data)
    )
    return _fact_entry(
        bundle,
        spec=spec,
        status="available",
        value=nav_data,
        extraction_mode=None,
        evidence_anchor_ids=anchor_ids,
        missing_reason=None,
        missing_detail=None,
    )


def _missing_status_for_field(
    field_name: str,
    note: str | None,
) -> tuple[ChapterFactStatus, ChapterFactMissingReason]:
    """根据字段 note 映射缺失语义，见模板第 0-7 章数据缺口。

    Args:
        field_name: 结构化字段名。
        note: extractor 附加说明。

    Returns:
        `(status, missing_reason)` 二元组。

    Raises:
        无显式抛出。
    """

    normalized_note = (note or "").lower()
    if (
        "not_applicable" in normalized_note
        or "not applicable" in normalized_note
        or "不适用" in normalized_note
        or (field_name == "bond_risk_evidence" and "non_bond" in normalized_note)
        or (field_name == "tracking_error" and "non_index" in normalized_note)
    ):
        return "not_applicable", "field_not_applicable"
    if "unavailable" in normalized_note or "不可用" in normalized_note:
        return "unavailable", "field_unavailable"
    return "missing", "field_missing"


def _fact_entry(
    bundle: StructuredFundDataBundle,
    *,
    spec: _ChapterFieldSpec,
    status: ChapterFactStatus,
    value: object | None,
    extraction_mode: str | None,
    evidence_anchor_ids: tuple[str, ...],
    missing_reason: ChapterFactMissingReason | None,
    missing_detail: str | None,
) -> ChapterFactEntry:
    """构造章节事实条目，见模板第 0-7 章。

    Args:
        bundle: 已抽取完成的结构化基金数据包。
        spec: 章节字段映射。
        status: 当前事实状态。
        value: 结构化事实值。
        extraction_mode: extractor 抽取模式。
        evidence_anchor_ids: 本章内证据锚点 ID。
        missing_reason: 缺失原因。
        missing_detail: 缺失细节。

    Returns:
        单个章节事实条目。

    Raises:
        无显式抛出。
    """

    return ChapterFactEntry(
        fact_id=_fact_id_for(bundle, spec.chapter_id, spec.source_field_id),
        chapter_id=spec.chapter_id,
        field_path=f"StructuredFundDataBundle.{spec.field_name}",
        source_field_id=spec.source_field_id,
        source_field_name=spec.field_name,
        status=status,
        value=value,
        extraction_mode=extraction_mode,
        evidence_anchor_ids=evidence_anchor_ids,
        missing_reason=missing_reason,
        missing_detail=missing_detail,
        required_by=spec.required_by + tuple(f"ITEM_RULE.{rule_id}" for rule_id in spec.item_rule_ids),
    )


def _synthetic_missing_facts(
    bundle: StructuredFundDataBundle,
    chapter_id: int,
) -> tuple[ChapterFactEntry, ...]:
    """生成章节级合成缺口事实，见模板第 0/5/7 章。

    Args:
        bundle: 已抽取完成的结构化基金数据包。
        chapter_id: 模板章节编号。

    Returns:
        当前章节需要的合成缺口事实。

    Raises:
        无显式抛出。
    """

    if chapter_id in (0, 7):
        return (
            _project_synthetic_missing_fact(
                bundle,
                chapter_id=chapter_id,
                source_field_id=_ACCEPTED_CHAPTER_CONCLUSIONS_SOURCE_FIELD_ID,
                source_field_name="accepted_chapter_conclusions",
                missing_reason="accepted_chapter_conclusions_missing",
                missing_detail="Gate 1 尚无章节 writer/auditor/orchestrator 的 accepted chapter conclusions",
            ),
        )
    if chapter_id == 5:
        return (
            _project_synthetic_missing_fact(
                bundle,
                chapter_id=chapter_id,
                source_field_id=_CROSS_PERIOD_COMPARISON_SOURCE_FIELD_ID,
                source_field_name="cross_period_comparison",
                missing_reason="cross_period_comparison_missing",
                missing_detail="当前输入是单期 StructuredFundDataBundle，不能伪造跨期比较",
            ),
        )
    return ()


def _project_synthetic_missing_fact(
    bundle: StructuredFundDataBundle,
    *,
    chapter_id: int,
    source_field_id: str,
    source_field_name: str,
    missing_reason: ChapterFactMissingReason,
    missing_detail: str,
) -> ChapterFactEntry:
    """构造合成缺口事实，见模板第 0/5/7 章。

    Args:
        bundle: 已抽取完成的结构化基金数据包。
        chapter_id: 模板章节编号。
        source_field_id: 合成来源字段 ID。
        source_field_name: 合成来源字段名。
        missing_reason: 缺口原因。
        missing_detail: 缺口细节。

    Returns:
        合成缺口事实。

    Raises:
        无显式抛出。
    """

    return ChapterFactEntry(
        fact_id=_fact_id_for(bundle, chapter_id, source_field_id),
        chapter_id=chapter_id,
        field_path=f"synthetic.{source_field_name}",
        source_field_id=source_field_id,
        source_field_name=source_field_name,
        status="missing",
        value=None,
        extraction_mode=None,
        evidence_anchor_ids=(),
        missing_reason=missing_reason,
        missing_detail=missing_detail,
        required_by=(f"CHAPTER_CONTRACT.chapter_{chapter_id}",),
    )


def _dedupe_chapter_anchors(
    fund_code: str,
    report_year: int,
    chapter_id: int,
    anchors: tuple[EvidenceAnchor, ...],
) -> tuple[ChapterEvidenceAnchor, ...]:
    """对章节证据锚点去重并生成稳定 ID。

    Args:
        fund_code: 基金代码。
        report_year: 年报年份。
        chapter_id: 模板章节编号。
        anchors: 原始普通证据锚点。

    Returns:
        去重后的章节证据锚点。

    Raises:
        无显式抛出。
    """

    projected: list[ChapterEvidenceAnchor] = []
    seen_keys: set[tuple[object, ...]] = set()
    seen_base_ids: dict[str, int] = {}
    for raw_anchor in anchors:
        anchor_without_id = _chapter_anchor_from_raw(raw_anchor, "")
        key = _anchor_key(anchor_without_id)
        if key in seen_keys:
            continue
        seen_keys.add(key)
        base_id = _anchor_id_for(fund_code, report_year, chapter_id, anchor_without_id)
        collision_count = seen_base_ids.get(base_id, 0) + 1
        seen_base_ids[base_id] = collision_count
        anchor_id = base_id if collision_count == 1 else f"{base_id}-{collision_count}"
        projected.append(_chapter_anchor_from_raw(raw_anchor, anchor_id))
    return tuple(projected)


def _chapter_anchor_from_raw(
    raw_anchor: EvidenceAnchor,
    anchor_id: str,
) -> ChapterEvidenceAnchor:
    """把 extractor 锚点转换为章节锚点。

    Args:
        raw_anchor: extractor 证据锚点。
        anchor_id: 已分配的章节锚点 ID。

    Returns:
        章节证据锚点。

    Raises:
        无显式抛出。
    """

    source_kind = raw_anchor.source_kind
    projected_source_kind: ChapterEvidenceSourceKind = (
        source_kind if source_kind in _SUPPORTED_ANCHOR_SOURCE_KINDS else "unknown"
    )
    return ChapterEvidenceAnchor(
        anchor_id=anchor_id,
        source_kind=projected_source_kind,
        document_year=raw_anchor.document_year,
        section_id=raw_anchor.section_id,
        page_number=raw_anchor.page_number,
        table_id=raw_anchor.table_id,
        row_locator=raw_anchor.row_locator,
        note=raw_anchor.note,
    )


def _anchor_id_for(
    fund_code: str,
    report_year: int,
    chapter_id: int,
    anchor: ChapterEvidenceAnchor,
) -> str:
    """生成稳定章节锚点 ID。

    Args:
        fund_code: 基金代码。
        report_year: 年报年份。
        chapter_id: 模板章节编号。
        anchor: 未分配 ID 的章节锚点。

    Returns:
        稳定锚点 ID。

    Raises:
        无显式抛出。
    """

    normalized = _anchor_normalized_payload(anchor)
    digest = hashlib.sha256(
        json.dumps(normalized, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()[:8]
    section = _stable_id_part(anchor.section_id)
    return (
        f"chapter-anchor:{fund_code}:{report_year}:ch{chapter_id}:"
        f"{anchor.source_kind}:{section}:{digest}"
    )


def _anchor_key(anchor: ChapterEvidenceAnchor) -> tuple[object, ...]:
    """生成章节锚点去重 key。

    Args:
        anchor: 章节证据锚点。

    Returns:
        可哈希的锚点定位 key。

    Raises:
        无显式抛出。
    """

    normalized = _anchor_normalized_payload(anchor)
    return tuple(normalized[key] for key in sorted(normalized))


def _anchor_normalized_payload(anchor: ChapterEvidenceAnchor) -> dict[str, object]:
    """生成锚点 ID 和去重所需的规范化 payload。

    Args:
        anchor: 章节证据锚点。

    Returns:
        规范化字典。

    Raises:
        无显式抛出。
    """

    return {
        "source_kind": anchor.source_kind,
        "document_year": anchor.document_year,
        "section_id": anchor.section_id,
        "page_number": anchor.page_number,
        "table_id": anchor.table_id,
        "row_locator": anchor.row_locator,
        "note": anchor.note,
    }


def _stable_id_part(value: str | None) -> str:
    """把锚点字段转为稳定 ID 片段。

    Args:
        value: 原始字段值。

    Returns:
        稳定字符串片段。

    Raises:
        无显式抛出。
    """

    if value is None or not value.strip():
        return "unknown"
    return value.replace(":", "_").replace("/", "_").replace(" ", "_")


def _ensure_fact_anchor_refs_exist(
    facts: tuple[ChapterFactEntry, ...],
    anchors: tuple[ChapterEvidenceAnchor, ...],
) -> None:
    """校验 fact 引用的证据锚点均存在于本章。

    Args:
        facts: 当前章节事实。
        anchors: 当前章节证据锚点。

    Returns:
        校验通过时返回 `None`。

    Raises:
        ValueError: 当任一 fact 引用不存在的锚点时抛出。
    """

    known_anchor_ids = {anchor.anchor_id for anchor in anchors}
    missing_refs = tuple(
        anchor_id
        for fact in facts
        for anchor_id in fact.evidence_anchor_ids
        if anchor_id not in known_anchor_ids
    )
    if missing_refs:
        raise ValueError(f"章节事实引用了不存在的 evidence anchor：{missing_refs}")


def _fact_id_for(
    bundle: StructuredFundDataBundle,
    chapter_id: int,
    source_field_id: str,
) -> str:
    """生成稳定章节事实 ID。

    Args:
        bundle: 已抽取完成的结构化基金数据包。
        chapter_id: 模板章节编号。
        source_field_id: 稳定来源字段 ID。

    Returns:
        稳定事实 ID。

    Raises:
        无显式抛出。
    """

    return f"chapter-fact:{bundle.fund_code}:{bundle.report_year}:ch{chapter_id}:{source_field_id}"


def _unique_reasons(
    reasons: tuple[ChapterFactMissingReason, ...],
) -> tuple[ChapterFactMissingReason, ...]:
    """按首次出现顺序去重缺失原因。

    Args:
        reasons: 原始缺失原因。

    Returns:
        去重后的缺失原因。

    Raises:
        无显式抛出。
    """

    return tuple(_unique_strings(reasons))  # type: ignore[return-value]


def _unique_strings(values: tuple[str, ...]) -> tuple[str, ...]:
    """按首次出现顺序去重字符串。

    Args:
        values: 原始字符串。

    Returns:
        去重后的字符串。

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
