"""年报 ParsedAnnualReport Processor。

本模块实现 `ParsedAnnualReport` 字段族 processor：只消费已经加载好的
`ParsedAnnualReport`，按基金类型分 processor 包装现有窄 extractor，输出模板第 1-6
章最小字段族。它不读取 `FundDocumentRepository`、PDF/cache/source helper、Docling、
candidate projection、network、provider、LLM、Service/UI/Host、renderer 或 quality gate。

字段级 mapping table：

| extractor output path | field_family_id | field name | chapter | mode | required | gap |
|---|---|---|---|---|---|---|
| profile.basic_identity | product_essence.v1 | basic_identity | 1 | direct | yes | field_family_partial |
| profile.product_profile | product_essence.v1 | product_profile | 1 | direct | yes | field_family_partial |
| profile.risk_characteristic_text | product_essence.v1 | risk_characteristic_text | 1 | direct | yes | field_family_partial |
| profile.benchmark | product_essence.v1 | benchmark | 1 | direct | yes | field_family_partial |
| performance.nav_benchmark_performance | return_attribution.v1 | nav_benchmark_performance | 2 | direct | yes | field_family_partial |
| performance.tracking_error | return_attribution.v1 | tracking_error | 2 | direct | yes | field_family_partial |
| profile.fee_schedule | return_attribution.v1 | fee_schedule | 2 | direct | yes | field_family_partial |
| manager_ownership.portfolio_managers | manager_profile.v1 | portfolio_managers | 3 | direct | yes | field_family_partial |
| manager_ownership.manager_strategy_text | manager_profile.v1 | manager_strategy_text | 3 | direct | yes | field_family_partial |
| manager_ownership.turnover_rate | manager_profile.v1 | turnover_rate | 3 | direct | yes | field_family_partial |
| manager_ownership.manager_alignment | manager_profile.v1 | manager_alignment | 3 | direct | yes | field_family_partial |
| holdings_share_change.holdings_snapshot | manager_profile.v1 | holdings_snapshot | 3 | direct | yes | field_family_partial |
| performance.investor_return | investor_experience.v1 | investor_return | 4 | direct/estimated | yes | field_family_partial |
| manager_ownership.holder_structure | investor_experience.v1 | holder_structure | 4 | direct | yes | field_family_partial |
| holdings_share_change.share_change | investor_experience.v1 | share_change | 4 | direct | yes | field_family_partial |
| profile.basic_identity | current_stage.v1 | basic_identity | 5 | direct | yes | field_family_partial |
| holdings_share_change.share_change | current_stage.v1 | share_change | 5 | direct | yes | field_family_partial |
| holdings_share_change.holdings_snapshot | current_stage.v1 | holdings_snapshot | 5 | direct | yes | field_family_partial |
| manager_ownership.portfolio_managers | current_stage.v1 | portfolio_managers | 5 | direct | yes | field_family_partial |
| profile.risk_characteristic_text | core_risk.v1 | risk_characteristic_text | 6 | direct | yes | field_family_partial |
| manager_ownership.holder_structure | core_risk.v1 | holder_structure | 6 | direct | yes | field_family_partial |
| manager_ownership.turnover_rate | core_risk.v1 | turnover_rate | 6 | direct | yes | field_family_partial |
| holdings_share_change.holdings_snapshot | core_risk.v1 | holdings_snapshot | 6 | direct | yes | field_family_partial |
| performance.tracking_error | core_risk.v1 | tracking_error | 6 | direct | yes | field_family_partial |
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Final, Iterable

from fund_agent.fund.documents.models import ParsedAnnualReport
from fund_agent.fund.extractors.holdings_share_change import extract_holdings_share_change
from fund_agent.fund.extractors.manager_ownership import extract_manager_ownership
from fund_agent.fund.extractors.models import EvidenceAnchor, ExtractedField
from fund_agent.fund.extractors.performance import extract_performance
from fund_agent.fund.extractors.profile import extract_profile
from fund_agent.fund.fund_type import FundType
from fund_agent.fund.processors.contracts import (
    FundExtractionGapCode,
    FundExtractionSourceBoundary,
    FundExtractionGap,
    FundFieldFamilyId,
    FundFieldFamilyResult,
    FundFieldFamilyStatus,
    FundProcessorContractStatus,
    FundProcessorDispatchKey,
    FundProcessorExtractionMode,
    FundProcessorInput,
    FundProcessorResult,
)
from fund_agent.fund.source_facts import AtomicSourceFact, AtomicSourceFactStore
from fund_agent.fund.source_provenance import (
    PublicSourceProvenance,
    project_public_source_provenance,
)

_OUTPUT_SCHEMA_VERSION: Final[str] = "fund_processor_result.v1"


@dataclass(frozen=True, slots=True)
class FieldFamilyMapping:
    """字段族 mapping table 单行。

    Args:
        无。

    Attributes:
        source_path: 现有窄 extractor 输出路径。
        field_family_id: 目标字段族。
        output_field_name: 字段族值内字段名。
        chapter_ids: 公开模板章节 ID。
        required: 是否为当前字段族必需项。

    Raises:
        无显式抛出。
    """

    source_path: str
    field_family_id: FundFieldFamilyId
    output_field_name: str
    chapter_ids: tuple[int, ...]
    required: bool = True


FIELD_FAMILY_MAPPINGS: Final[tuple[FieldFamilyMapping, ...]] = (
    FieldFamilyMapping("profile.basic_identity", "product_essence.v1", "basic_identity", (1,)),
    FieldFamilyMapping("profile.product_profile", "product_essence.v1", "product_profile", (1,)),
    FieldFamilyMapping(
        "profile.risk_characteristic_text",
        "product_essence.v1",
        "risk_characteristic_text",
        (1,),
    ),
    FieldFamilyMapping("profile.benchmark", "product_essence.v1", "benchmark", (1,)),
    FieldFamilyMapping(
        "performance.nav_benchmark_performance",
        "return_attribution.v1",
        "nav_benchmark_performance",
        (2,),
    ),
    FieldFamilyMapping("performance.tracking_error", "return_attribution.v1", "tracking_error", (2,)),
    FieldFamilyMapping("profile.fee_schedule", "return_attribution.v1", "fee_schedule", (2,)),
    FieldFamilyMapping(
        "manager_ownership.portfolio_managers",
        "manager_profile.v1",
        "portfolio_managers",
        (3,),
    ),
    FieldFamilyMapping(
        "manager_ownership.manager_strategy_text",
        "manager_profile.v1",
        "manager_strategy_text",
        (3,),
    ),
    FieldFamilyMapping("manager_ownership.turnover_rate", "manager_profile.v1", "turnover_rate", (3,)),
    FieldFamilyMapping(
        "manager_ownership.manager_alignment",
        "manager_profile.v1",
        "manager_alignment",
        (3,),
    ),
    FieldFamilyMapping(
        "holdings_share_change.holdings_snapshot",
        "manager_profile.v1",
        "holdings_snapshot",
        (3,),
    ),
    FieldFamilyMapping(
        "performance.investor_return",
        "investor_experience.v1",
        "investor_return",
        (4,),
    ),
    FieldFamilyMapping(
        "manager_ownership.holder_structure",
        "investor_experience.v1",
        "holder_structure",
        (4,),
    ),
    FieldFamilyMapping(
        "holdings_share_change.share_change",
        "investor_experience.v1",
        "share_change",
        (4,),
    ),
    FieldFamilyMapping("profile.basic_identity", "current_stage.v1", "basic_identity", (5,)),
    FieldFamilyMapping("holdings_share_change.share_change", "current_stage.v1", "share_change", (5,)),
    FieldFamilyMapping(
        "holdings_share_change.holdings_snapshot",
        "current_stage.v1",
        "holdings_snapshot",
        (5,),
    ),
    FieldFamilyMapping(
        "manager_ownership.portfolio_managers",
        "current_stage.v1",
        "portfolio_managers",
        (5,),
    ),
    FieldFamilyMapping(
        "profile.risk_characteristic_text",
        "core_risk.v1",
        "risk_characteristic_text",
        (6,),
    ),
    FieldFamilyMapping(
        "manager_ownership.holder_structure",
        "core_risk.v1",
        "holder_structure",
        (6,),
    ),
    FieldFamilyMapping("manager_ownership.turnover_rate", "core_risk.v1", "turnover_rate", (6,)),
    FieldFamilyMapping(
        "holdings_share_change.holdings_snapshot",
        "core_risk.v1",
        "holdings_snapshot",
        (6,),
    ),
    FieldFamilyMapping("performance.tracking_error", "core_risk.v1", "tracking_error", (6,)),
)
_FAMILY_ORDER: Final[tuple[FundFieldFamilyId, ...]] = (
    "product_essence.v1",
    "return_attribution.v1",
    "manager_profile.v1",
    "investor_experience.v1",
    "current_stage.v1",
    "core_risk.v1",
)
_MIGRATED_COMPOSITE_CHILDREN: Final[dict[str, tuple[str, ...]]] = {
    "fee_schedule": ("management_fee", "custody_fee"),
    "nav_benchmark_performance": ("nav_growth_rate", "benchmark_return_rate"),
    "manager_strategy_text": ("strategy_summary", "market_outlook"),
    "manager_alignment": ("manager_holding", "employee_holding"),
}
_CHILD_SOURCE_FACT_MAPPINGS: Final[dict[str, tuple[str, FundFieldFamilyId]]] = {
    "profile.fee_schedule_management_fee": (
        "fee_schedule.management_fee",
        "return_attribution.v1",
    ),
    "profile.fee_schedule_custody_fee": (
        "fee_schedule.custody_fee",
        "return_attribution.v1",
    ),
    "performance.nav_benchmark_performance_nav_growth_rate": (
        "nav_benchmark_performance.nav_growth_rate",
        "return_attribution.v1",
    ),
    "performance.nav_benchmark_performance_benchmark_return_rate": (
        "nav_benchmark_performance.benchmark_return_rate",
        "return_attribution.v1",
    ),
    "manager_ownership.manager_strategy_text_strategy_summary": (
        "manager_strategy_text.strategy_summary",
        "manager_profile.v1",
    ),
    "manager_ownership.manager_strategy_text_market_outlook": (
        "manager_strategy_text.market_outlook",
        "manager_profile.v1",
    ),
    "manager_ownership.manager_alignment_manager_holding": (
        "manager_alignment.manager_holding",
        "manager_profile.v1",
    ),
    "manager_ownership.manager_alignment_employee_holding": (
        "manager_alignment.employee_holding",
        "manager_profile.v1",
    ),
}


class _ParsedAnnualReportFundProcessor:
    """已分类基金年报 parsed intermediate processor 基类，见模板第 1-6 章字段族。

    子类只通过 `processor_id` 和 `supported_fund_type` 区分基金类型；字段族 mapping
    与 fail-closed 语义共享，避免为每类基金复制 extractor 编排。
    """

    processor_id: str = ""
    priority: int = 90
    output_schema_version: str = _OUTPUT_SCHEMA_VERSION
    supported_fund_type: FundType = "active_fund"

    def supports(self, context: FundProcessorDispatchKey) -> bool:
        """判断是否支持当前 dispatch key。

        Args:
            context: Processor 路由键。

        Returns:
            仅在子类声明基金类型的年报 `ParsedAnnualReport` 场景返回 `True`。

        Raises:
            无显式抛出。
        """

        return (
            context.fund_type == self.supported_fund_type
            and context.report_type == "annual_report"
            and context.intermediate_kind == "parsed_annual_report.v1"
            and context.processor_goal == "template_chapters_1_6_minimum_field_families"
        )

    def extract(self, input_data: FundProcessorInput) -> FundProcessorResult:
        """抽取已分类基金年报六个字段族。

        Args:
            input_data: Processor 输入契约。

        Returns:
            六个字段族的 processor 结果；字段族缺口保留在本地。

        Raises:
            无显式抛出；不支持或输入类型错误会返回 fail-closed result。
        """

        if not self.supports(input_data.context):
            gap_code, source_boundary = _unsupported_block_details(
                input_data.context,
                supported_fund_type=self.supported_fund_type,
            )
            return _blocked_result(
                self.processor_id,
                input_data.context,
                gap_code=gap_code,
                message=f"{self.__class__.__name__} 不支持当前 dispatch key",
                source_boundary=source_boundary,
            )
        if not isinstance(input_data.intermediate, ParsedAnnualReport):
            return _blocked_result(
                self.processor_id,
                input_data.context,
                gap_code="input_type_mismatch",
                message="parsed annual processor 只接受 ParsedAnnualReport",
                source_boundary="unsupported_intermediate",
            )

        report = input_data.intermediate
        source_provenance = input_data.source_provenance or project_public_source_provenance(
            report.metadata.source
        )
        extracted_fields = _collect_existing_extractor_fields(report)
        source_facts = _build_source_fact_store(extracted_fields, source_provenance)
        field_families = tuple(
            _build_field_family_result(family_id, extracted_fields, source_provenance, source_facts)
            for family_id in _FAMILY_ORDER
        )
        anchors = _dedupe_anchors(
            anchor for family in field_families for anchor in family.anchors
        )
        return FundProcessorResult(
            processor_id=self.processor_id,
            output_schema_version=self.output_schema_version,
            fund_code=report.key.fund_code,
            report_year=report.key.year,
            fund_type=input_data.context.fund_type,
            report_type=input_data.context.report_type,
            input_intermediate_kind=input_data.context.intermediate_kind,
            field_families=field_families,
            gaps=(),
            anchors=anchors,
            source_provenance=source_provenance,
            source_facts=source_facts,
            candidate_boundary=None,
            contract_status=_derive_contract_status(field_families),
        )


class ActiveFundAnnualProcessor(_ParsedAnnualReportFundProcessor):
    """主动基金年报 processor，见模板第 1-6 章字段族。

    该 processor 支持 `active_fund + annual_report + parsed_annual_report.v1`，
    并把当前窄 extractor 输出投影为字段族结果；它不会声明 source truth、parser
    replacement、candidate proof、readiness 或 release 状态。
    """

    processor_id: Final[str] = "active_fund_annual.parsed_annual_report.v1"
    priority: Final[int] = 100
    supported_fund_type: Final[FundType] = "active_fund"


class IndexFundAnnualProcessor(_ParsedAnnualReportFundProcessor):
    """指数基金年报 processor，见模板第 1-6 章字段族。"""

    processor_id: Final[str] = "index_fund_annual.parsed_annual_report.v1"
    supported_fund_type: Final[FundType] = "index_fund"


class EnhancedIndexFundAnnualProcessor(_ParsedAnnualReportFundProcessor):
    """指数增强基金年报 processor，见模板第 1-6 章字段族。"""

    processor_id: Final[str] = "enhanced_index_annual.parsed_annual_report.v1"
    supported_fund_type: Final[FundType] = "enhanced_index"


class BondFundAnnualProcessor(_ParsedAnnualReportFundProcessor):
    """债券基金年报 processor，见模板第 1-6 章字段族。"""

    processor_id: Final[str] = "bond_fund_annual.parsed_annual_report.v1"
    supported_fund_type: Final[FundType] = "bond_fund"


class QdiiFundAnnualProcessor(_ParsedAnnualReportFundProcessor):
    """QDII 基金年报 processor，见模板第 1-6 章字段族。"""

    processor_id: Final[str] = "qdii_fund_annual.parsed_annual_report.v1"
    supported_fund_type: Final[FundType] = "qdii_fund"


class FofFundAnnualProcessor(_ParsedAnnualReportFundProcessor):
    """FOF 基金年报 processor，见模板第 1-6 章字段族。"""

    processor_id: Final[str] = "fof_fund_annual.parsed_annual_report.v1"
    supported_fund_type: Final[FundType] = "fof_fund"


def _collect_existing_extractor_fields(
    report: ParsedAnnualReport,
) -> dict[str, ExtractedField[object]]:
    """调用现有窄 extractor 并按 documented source_path 收集字段。

    Args:
        report: 已加载的年报中间态。

    Returns:
        extractor 输出路径到 `ExtractedField` 的映射。

    Raises:
        无显式抛出；窄 extractor 内部实现异常会自然暴露为实现缺陷。
    """

    profile = extract_profile(report)
    performance = extract_performance(report)
    manager_ownership = extract_manager_ownership(report)
    holdings_share_change = extract_holdings_share_change(report)
    return {
        "profile.basic_identity": profile.basic_identity,
        "profile.product_profile": profile.product_profile,
        "profile.risk_characteristic_text": profile.risk_characteristic_text,
        "profile.benchmark": profile.benchmark,
        "profile.fee_schedule": profile.fee_schedule,
        "profile.fee_schedule_management_fee": profile.fee_schedule_management_fee,
        "profile.fee_schedule_custody_fee": profile.fee_schedule_custody_fee,
        "performance.nav_benchmark_performance": performance.nav_benchmark_performance,
        "performance.nav_benchmark_performance_nav_growth_rate": (
            performance.nav_benchmark_performance_nav_growth_rate
        ),
        "performance.nav_benchmark_performance_benchmark_return_rate": (
            performance.nav_benchmark_performance_benchmark_return_rate
        ),
        "performance.investor_return": performance.investor_return,
        "performance.tracking_error": performance.tracking_error,
        "manager_ownership.manager_strategy_text": manager_ownership.manager_strategy_text,
        "manager_ownership.manager_strategy_text_strategy_summary": (
            manager_ownership.manager_strategy_text_strategy_summary
        ),
        "manager_ownership.manager_strategy_text_market_outlook": (
            manager_ownership.manager_strategy_text_market_outlook
        ),
        "manager_ownership.portfolio_managers": manager_ownership.portfolio_managers,
        "manager_ownership.turnover_rate": manager_ownership.turnover_rate,
        "manager_ownership.manager_alignment": manager_ownership.manager_alignment,
        "manager_ownership.manager_alignment_manager_holding": (
            manager_ownership.manager_alignment_manager_holding
        ),
        "manager_ownership.manager_alignment_employee_holding": (
            manager_ownership.manager_alignment_employee_holding
        ),
        "manager_ownership.holder_structure": manager_ownership.holder_structure,
        "holdings_share_change.holdings_snapshot": holdings_share_change.holdings_snapshot,
        "holdings_share_change.share_change": holdings_share_change.share_change,
    }


def _build_source_fact_store(
    extracted_fields: dict[str, ExtractedField[object]],
    source_provenance: PublicSourceProvenance,
) -> AtomicSourceFactStore:
    """从 S2A 子字段输出构造 parsed annual atomic source fact store。

    Args:
        extracted_fields: extractor 输出路径到字段的映射。
        source_provenance: 公共来源 provenance。

    Returns:
        仅包含直接 child evidence 或显式 child gap 的 atomic source facts。

    Raises:
        无显式抛出。
    """

    facts = []
    for source_path, (fact_id, family_id) in _CHILD_SOURCE_FACT_MAPPINGS.items():
        field = extracted_fields.get(source_path)
        fact = _source_fact_from_child_field(
            fact_id=fact_id,
            family_id=family_id,
            field=field,
            source_provenance=source_provenance,
        )
        if fact is not None:
            facts.append(fact)
    return AtomicSourceFactStore(tuple(facts))


def _source_fact_from_child_field(
    *,
    fact_id: str,
    family_id: FundFieldFamilyId,
    field: ExtractedField[object] | None,
    source_provenance: PublicSourceProvenance,
) -> AtomicSourceFact | None:
    """将单个 S2A child 字段转换为 atomic fact。

    Args:
        fact_id: canonical source field path。
        family_id: 所属字段族。
        field: S2A child-level extractor 输出。
        source_provenance: 公共来源 provenance。

    Returns:
        直接命中或显式缺口的 atomic fact；否则返回 `None`。

    Raises:
        无显式抛出。
    """

    if _child_field_has_direct_fact(field, fact_id):
        return AtomicSourceFact(
            fact_id=fact_id,
            family_id=family_id,
            value=field.value,
            status="accepted",
            extraction_mode=field.extraction_mode,
            anchors=field.anchors,
            provenance=source_provenance,
            gaps=(),
            source_field_path=fact_id,
        )
    if _child_field_has_explicit_gap(field, fact_id):
        return AtomicSourceFact(
            fact_id=fact_id,
            family_id=family_id,
            value=None,
            status="missing",
            extraction_mode="missing",
            anchors=(),
            provenance=source_provenance,
            gaps=(field.note or f"source_field_path={fact_id}; gap=missing",),
            source_field_path=fact_id,
        )
    return None


def _child_field_has_direct_fact(field: ExtractedField[object] | None, fact_id: str) -> bool:
    """判断 child 字段是否携带 canonical direct evidence。

    Args:
        field: S2A child-level extractor 输出。
        fact_id: canonical source field path。

    Returns:
        字段有值、非 missing 且每个 anchor 均指向当前 fact id 时返回 `True`。

    Raises:
        无显式抛出。
    """

    return (
        field is not None
        and field.value is not None
        and field.extraction_mode != "missing"
        and bool(field.anchors)
        and all(_anchor_has_source_field_path(anchor, fact_id) for anchor in field.anchors)
    )


def _child_field_has_explicit_gap(field: ExtractedField[object] | None, fact_id: str) -> bool:
    """判断 child 字段是否显式报告当前 canonical path 的缺口。

    Args:
        field: S2A child-level extractor 输出。
        fact_id: canonical source field path。

    Returns:
        `missing` 字段 note 显式携带 `source_field_path=<fact_id>` 时返回 `True`。

    Raises:
        无显式抛出。
    """

    return (
        field is not None
        and field.value is None
        and not field.anchors
        and field.extraction_mode == "missing"
        and _text_has_source_field_path(field.note, fact_id)
    )


def _build_field_family_result(
    field_family_id: FundFieldFamilyId,
    extracted_fields: dict[str, ExtractedField[object]],
    source_provenance: PublicSourceProvenance,
    source_facts: AtomicSourceFactStore,
) -> FundFieldFamilyResult:
    """按 mapping table 构造单个字段族结果。

    Args:
        field_family_id: 目标字段族 ID。
        extracted_fields: extractor 输出路径到字段的映射。
        source_provenance: 公共来源 provenance。
        source_facts: parsed annual atomic source fact store。

    Returns:
        字段族结果。

    Raises:
        ValueError: 当 mapping table 缺少目标字段族定义时抛出。
    """

    mappings = tuple(
        mapping for mapping in FIELD_FAMILY_MAPPINGS if mapping.field_family_id == field_family_id
    )
    if not mappings:
        raise ValueError(f"未定义字段族 mapping：{field_family_id}")

    value: dict[str, object] = {"schema_version": field_family_id}
    anchors: list[EvidenceAnchor] = []
    missing_fields: list[tuple[FieldFamilyMapping, ExtractedField[object] | None]] = []
    missing_composite_children: list[tuple[FieldFamilyMapping, str, AtomicSourceFact]] = []
    for mapping in mappings:
        field = extracted_fields.get(mapping.source_path)
        composite_value = _composite_value_from_source_facts(mapping.output_field_name, source_facts)
        if composite_value:
            value[mapping.output_field_name] = composite_value
            anchors.extend(_composite_anchors_from_source_facts(mapping.output_field_name, source_facts))
            missing_composite_children.extend(
                _missing_composite_children(mapping, source_facts)
            )
            continue
        if _field_has_public_value(field):
            value[mapping.output_field_name] = field.value
            anchors.extend(_field_scoped_anchors(mapping, field))
            continue
        value[mapping.output_field_name] = None
        missing_fields.append((mapping, field))

    partial_gaps = [
        _field_gap(mapping, field, "field_family_partial") for mapping, field in missing_fields
    ]
    partial_gaps.extend(
        _composite_child_gap(mapping, fact_id, fact, "field_family_partial")
        for mapping, fact_id, fact in missing_composite_children
    )
    status = _derive_family_status(mappings, partial_gaps)
    gap_code: FundExtractionGapCode = (
        "field_family_missing" if status == "missing" else "field_family_partial"
    )
    gaps = (
        *(_field_gap(mapping, field, gap_code) for mapping, field in missing_fields),
        *(
            _composite_child_gap(mapping, fact_id, fact, gap_code)
            for mapping, fact_id, fact in missing_composite_children
        ),
    )
    extraction_mode = _derive_family_extraction_mode(mappings, extracted_fields, status)
    return FundFieldFamilyResult(
        field_family_id=field_family_id,
        chapter_ids=_chapter_ids_for_mappings(mappings),
        value=value,
        status=status,
        extraction_mode=extraction_mode,
        anchors=_dedupe_anchors(anchors),
        gaps=gaps,
        source_provenance=source_provenance,
    )


def _field_scoped_anchors(
    mapping: FieldFamilyMapping,
    field: ExtractedField[object],
) -> tuple[EvidenceAnchor, ...]:
    """为 parsed annual 字段添加顶层字段范围定位。

    Args:
        mapping: 当前字段族 mapping 行。
        field: 窄 extractor 输出字段。

    Returns:
        带 ``source_field_path`` 顶层字段范围的 anchors。

    Raises:
        无显式抛出。
    """

    return tuple(
        _with_source_field_path(anchor, mapping.output_field_name) for anchor in field.anchors
    )


def _composite_value_from_source_facts(
    output_field_name: str,
    source_facts: AtomicSourceFactStore,
) -> dict[str, object] | None:
    """从 atomic child facts 派生迁移复合字段兼容 value。

    Args:
        output_field_name: 顶层兼容字段名。
        source_facts: parsed annual atomic source fact store。

    Returns:
        至少一个子事实 accepted 时返回包含全部 required child key 的旧 dict shape；
        accepted child 写入事实值，显式 missing 或缺失 child 写入 `None`。

    Raises:
        无显式抛出。
    """

    child_names = _MIGRATED_COMPOSITE_CHILDREN.get(output_field_name)
    if child_names is None:
        return None
    child_facts = {
        child_name: source_facts.get_optional(f"{output_field_name}.{child_name}")
        for child_name in child_names
    }
    if not any(fact is not None and fact.status == "accepted" for fact in child_facts.values()):
        return None
    value = {
        child_name: fact.value if fact is not None and fact.status == "accepted" else None
        for child_name, fact in child_facts.items()
    }
    if output_field_name == "manager_alignment":
        value["judgment"] = None
    return value


def _missing_composite_children(
    mapping: FieldFamilyMapping,
    source_facts: AtomicSourceFactStore,
) -> tuple[tuple[FieldFamilyMapping, str, AtomicSourceFact], ...]:
    """列出迁移复合字段中显式 missing 的 child facts。

    Args:
        mapping: 当前字段族 mapping 行。
        source_facts: parsed annual atomic source fact store。

    Returns:
        每个显式 missing child 对应的 mapping、fact id 和 fact。

    Raises:
        无显式抛出。
    """

    return tuple(
        (mapping, fact_id, fact)
        for child_name in _MIGRATED_COMPOSITE_CHILDREN.get(mapping.output_field_name, ())
        if (fact_id := f"{mapping.output_field_name}.{child_name}")
        and (fact := source_facts.get_optional(fact_id)) is not None
        and fact.status == "missing"
    )


def _composite_anchors_from_source_facts(
    output_field_name: str,
    source_facts: AtomicSourceFactStore,
) -> tuple[EvidenceAnchor, ...]:
    """从 accepted atomic facts 聚合迁移复合字段兼容 anchors。

    Args:
        output_field_name: 顶层兼容字段名。
        source_facts: parsed annual atomic source fact store。

    Returns:
        子事实 direct anchors 去重结果。

    Raises:
        无显式抛出。
    """

    child_names = _MIGRATED_COMPOSITE_CHILDREN.get(output_field_name, ())
    return _dedupe_anchors(
        anchor
        for child_name in child_names
        if (fact := source_facts.get_optional(f"{output_field_name}.{child_name}")) is not None
        and fact.status == "accepted"
        for anchor in fact.anchors
    )


def _with_source_field_path(anchor: EvidenceAnchor, source_field_path: str) -> EvidenceAnchor:
    """克隆 anchor 并附加非 Processor 字段范围定位。

    Args:
        anchor: 原始公共证据锚点。
        source_field_path: 顶层 public field 名称。

    Returns:
        附加 ``source_field_path`` 的锚点。

    Raises:
        无显式抛出。
    """

    return replace(
        anchor,
        row_locator=(
            f"source_field_path={source_field_path}; "
            f"locator={_sanitize_legacy_locator(anchor.row_locator)}"
        ),
    )


def _sanitize_legacy_locator(row_locator: str | None) -> str:
    """清理 legacy locator，避免污染分号 key=value 协议。

    Args:
        row_locator: 原始行级或语义定位。

    Returns:
        不含分号和等号的稳定 locator 文本。

    Raises:
        无显式抛出。
    """

    if not row_locator:
        return "missing"
    sanitized = " ".join(row_locator.replace(";", " ").replace("=", " ").split())
    return sanitized or "missing"


def _anchor_has_source_field_path(anchor: EvidenceAnchor, fact_id: str) -> bool:
    """判断 anchor row locator 是否携带 canonical source_field_path。

    Args:
        anchor: 待检查锚点。
        fact_id: canonical source field path。

    Returns:
        row locator 中 `source_field_path` 等于 fact id 时返回 `True`。

    Raises:
        无显式抛出。
    """

    return _text_has_source_field_path(anchor.row_locator, fact_id)


def _text_has_source_field_path(text: str | None, fact_id: str) -> bool:
    """解析分号分隔 locator/note 中的 `source_field_path`。

    Args:
        text: row locator 或 note 文本。
        fact_id: canonical source field path。

    Returns:
        存在完全匹配的 `source_field_path=<fact_id>` segment 时返回 `True`。

    Raises:
        无显式抛出。
    """

    if text is None:
        return False
    for segment in text.split(";"):
        key, separator, value = segment.strip().partition("=")
        if separator == "=" and key == "source_field_path" and value.strip() == fact_id:
            return True
    return False


def _field_has_public_value(field: ExtractedField[object] | None) -> bool:
    """判断 extractor 字段是否可进入字段族 value。

    Args:
        field: extractor 输出字段。

    Returns:
        字段有值、非 missing 且带公共锚点时返回 `True`。

    Raises:
        无显式抛出。
    """

    return (
        field is not None
        and field.value is not None
        and field.extraction_mode != "missing"
        and bool(field.anchors)
    )


def _field_gap(
    mapping: FieldFamilyMapping,
    field: ExtractedField[object] | None,
    gap_code: FundExtractionGapCode,
) -> FundExtractionGap:
    """为单个缺失 mapping 构造字段族本地 gap。

    Args:
        mapping: mapping table 单行。
        field: extractor 输出字段；可能缺失。
        gap_code: 字段族局部缺口码。

    Returns:
        字段族本地缺口。

    Raises:
        无显式抛出。
    """

    note = field.note if field is not None and field.note else "mapping 字段未形成可采信值"
    return FundExtractionGap(
        gap_code=gap_code,
        message=f"{mapping.source_path} 缺失或不可采信：{note}",
        field_family_id=mapping.field_family_id,
        source_field_path=mapping.source_path,
        source_boundary="annual_report",
        required=mapping.required,
    )


def _composite_child_gap(
    mapping: FieldFamilyMapping,
    fact_id: str,
    fact: AtomicSourceFact,
    gap_code: FundExtractionGapCode,
) -> FundExtractionGap:
    """为迁移复合字段的显式 missing child 构造字段族 gap。

    Args:
        mapping: 当前字段族 mapping 行。
        fact_id: missing child fact id。
        fact: missing atomic source fact。
        gap_code: 字段族局部缺口码。

    Returns:
        指向 child fact id 的字段族本地缺口。

    Raises:
        无显式抛出。
    """

    note = "; ".join(fact.gaps) if fact.gaps else "child source fact 显式缺失"
    return FundExtractionGap(
        gap_code=gap_code,
        message=f"{fact_id} 缺失或不可采信：{note}",
        field_family_id=mapping.field_family_id,
        source_field_path=fact_id,
        source_boundary="annual_report",
        required=mapping.required,
    )


def _derive_family_status(
    mappings: tuple[FieldFamilyMapping, ...],
    gaps: list[FundExtractionGap],
) -> FundFieldFamilyStatus:
    """从 required mapping 缺口派生字段族状态。

    Args:
        mappings: 当前字段族 mapping 行。
        gaps: 当前字段族缺口。

    Returns:
        `accepted`、`partial` 或 `missing`。

    Raises:
        无显式抛出。
    """

    required_count = sum(1 for mapping in mappings if mapping.required)
    required_gap_count = sum(1 for gap in gaps if gap.required)
    if required_gap_count == 0:
        return "accepted"
    if required_gap_count == required_count:
        return "missing"
    return "partial"


def _derive_family_extraction_mode(
    mappings: tuple[FieldFamilyMapping, ...],
    extracted_fields: dict[str, ExtractedField[object]],
    status: FundFieldFamilyStatus,
) -> FundProcessorExtractionMode:
    """从字段抽取模式派生字段族模式。

    Args:
        mappings: 当前字段族 mapping 行。
        extracted_fields: extractor 输出路径到字段的映射。
        status: 字段族状态。

    Returns:
        字段族抽取模式。

    Raises:
        无显式抛出。
    """

    if status == "missing":
        return "missing"
    modes = tuple(
        field.extraction_mode
        for mapping in mappings
        if (field := extracted_fields.get(mapping.source_path)) is not None
        and _field_has_public_value(field)
    )
    if "estimated" in modes:
        return "estimated"
    if "derived" in modes:
        return "derived"
    return "direct"


def _chapter_ids_for_mappings(mappings: tuple[FieldFamilyMapping, ...]) -> tuple[int, ...]:
    """从 mapping table 派生字段族公开章节 ID。

    Args:
        mappings: 当前字段族 mapping 行。

    Returns:
        去重且稳定排序的章节 ID。

    Raises:
        无显式抛出。
    """

    return tuple(sorted({chapter_id for mapping in mappings for chapter_id in mapping.chapter_ids}))


def _derive_contract_status(
    field_families: tuple[FundFieldFamilyResult, ...],
) -> FundProcessorContractStatus:
    """从六个字段族状态派生整体契约状态。

    Args:
        field_families: 字段族结果。

    Returns:
        整体契约状态。

    Raises:
        无显式抛出。
    """

    statuses = {field_family.status for field_family in field_families}
    if statuses == {"accepted"}:
        return "satisfied"
    if "accepted" in statuses or "partial" in statuses:
        return "partial"
    return "missing"


def _dedupe_anchors(anchors: Iterable[EvidenceAnchor]) -> tuple[EvidenceAnchor, ...]:
    """按 dataclass 值去重公共 EvidenceAnchor。

    Args:
        anchors: 可迭代的锚点对象。

    Returns:
        去重且保持首次出现顺序的锚点元组。

    Raises:
        无显式抛出。
    """

    deduped: list[EvidenceAnchor] = []
    seen: set[EvidenceAnchor] = set()
    for anchor in anchors:
        if anchor in seen:
            continue
        seen.add(anchor)
        deduped.append(anchor)
    return tuple(deduped)


def _unsupported_block_details(
    context: FundProcessorDispatchKey,
    *,
    supported_fund_type: FundType,
) -> tuple[FundExtractionGapCode, FundExtractionSourceBoundary]:
    """按 dispatch key 不匹配维度选择 fail-closed gap 归因。

    Args:
        context: Processor 路由键。
        supported_fund_type: 当前 processor 支持的标准基金类型。

    Returns:
        跨字段缺口码与 source boundary。

    Raises:
        无显式抛出。
    """

    if context.fund_type != supported_fund_type:
        return "unsupported_fund_type", "unsupported_fund_type"
    if context.report_type != "annual_report":
        return "unsupported_report_type", "unsupported_report_type"
    if context.intermediate_kind != "parsed_annual_report.v1":
        return "unsupported_intermediate_kind", "unsupported_intermediate"
    if context.processor_goal != "template_chapters_1_6_minimum_field_families":
        return "unsupported_processor_goal", "unsupported_processor_goal"
    return "unsupported_processor", "unsupported_intermediate"


def _blocked_result(
    processor_id: str,
    context: FundProcessorDispatchKey,
    *,
    gap_code: FundExtractionGapCode,
    message: str,
    source_boundary: FundExtractionSourceBoundary,
) -> FundProcessorResult:
    """构造跨字段 fail-closed processor 结果。

    Args:
        processor_id: 当前 processor ID。
        context: Processor 路由键。
        gap_code: 跨字段缺口码。
        message: 缺口说明。
        source_boundary: 跨字段缺口来源边界。

    Returns:
        `unsupported` 或 `blocked` 状态结果。

    Raises:
        无显式抛出。
    """

    return FundProcessorResult(
        processor_id=processor_id,
        output_schema_version=_OUTPUT_SCHEMA_VERSION,
        fund_code=context.fund_code,
        report_year=context.document_year,
        fund_type=context.fund_type,
        report_type=context.report_type,
        input_intermediate_kind=context.intermediate_kind,
        field_families=(),
        gaps=(
            FundExtractionGap(
                gap_code=gap_code,
                message=message,
                field_family_id=None,
                source_field_path=None,
                source_boundary=source_boundary,
                required=True,
            ),
        ),
        anchors=(),
        source_provenance=None,
        candidate_boundary=None,
        contract_status="unsupported" if gap_code.startswith("unsupported_") else "blocked",
    )
