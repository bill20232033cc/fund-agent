"""多年年报证据作用域与聚合能力，见模板第 5 章“当前阶段”。

本模块属于 Agent 层 Fund 领域能力，只通过 `FundDocumentRepository` 加载年报，
并把已加载年报投影为有界、可审计的年度证据摘要。Service 可以声明作用域，
但不能直接读取 repository、PDF cache 或来源 helper。
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Literal, Mapping, Protocol, Sequence, TypeAlias, get_args

from fund_agent.fund.data_extractor import StructuredFundDataBundle
from fund_agent.fund.documents import FundDocumentRepository
from fund_agent.fund.documents.models import (
    AnnualReportSourceFailureCategory,
    AnnualReportSourceMetadata,
    ParsedAnnualReport,
)
from fund_agent.fund.documents.sources import (
    AnnualReportSourceAggregateError,
    AnnualReportSourceFallbackBlockedError,
    AnnualReportSourceIntegrityError,
    AnnualReportSourceMismatchError,
    AnnualReportSourceNotFoundError,
    AnnualReportSourceSchemaError,
    AnnualReportSourceUnavailableError,
)
from fund_agent.fund.extractors import (
    EvidenceAnchor,
    ExtractedField,
    extract_holdings_share_change,
    extract_manager_ownership,
    extract_profile,
)
from fund_agent.fund.source_provenance import PublicSourceProvenance, project_public_source_provenance

ANNUAL_EVIDENCE_BUNDLE_SCHEMA_VERSION = "annual_evidence_bundle.v1"
ANNUAL_EVIDENCE_ANCHOR_SCHEMA_VERSION = "annual_evidence_anchor.v1"
ANNUAL_EVIDENCE_CROSS_YEAR_FACT_SCHEMA_VERSION = "annual_evidence_cross_year_fact.v1"
CURRENT_YEAR_REQUIRED_PRIOR_YEARS_OPTIONAL = "current_year_required_prior_years_optional"
MAX_ANNUAL_EVIDENCE_YEARS = 5

AnnualEvidenceAvailabilityStatus: TypeAlias = Literal[
    "available",
    "gap",
    "failed_closed",
    "blocked",
]
AnnualEvidenceDocumentIdentityStatus: TypeAlias = Literal[
    "verified_annual_report",
    "identity_mismatch",
    "source_failed",
    "unknown",
]
AnnualEvidenceDegradationPolicy: TypeAlias = Literal[
    "current_year_required_prior_years_optional"
]
CrossYearFactType: TypeAlias = Literal[
    "fee_schedule_trend",
    "turnover_rate_trend",
    "share_change_trend",
    "holdings_snapshot_trend",
    "manager_continuity",
]

_DEGRADABLE_FAILURE_CATEGORIES: frozenset[str] = frozenset(("not_found", "unavailable"))
_FAIL_CLOSED_FAILURE_CATEGORIES: frozenset[str] = frozenset(
    ("schema_drift", "identity_mismatch", "integrity_error")
)
_SUPPORTED_CROSS_YEAR_FACTS: tuple[CrossYearFactType, ...] = get_args(CrossYearFactType)
_CROSS_YEAR_SOURCE_FIELDS: Mapping[CrossYearFactType, str] = {
    "fee_schedule_trend": "fee_schedule",
    "turnover_rate_trend": "turnover_rate",
    "share_change_trend": "share_change",
    "holdings_snapshot_trend": "holdings_snapshot",
    "manager_continuity": "portfolio_managers",
}


class _AnnualReportRepository(Protocol):
    """年报仓库协议。"""

    async def load_annual_report(
        self,
        fund_code: str,
        year: int,
        *,
        force_refresh: bool = False,
    ) -> ParsedAnnualReport:
        """加载指定基金和年份的年报。

        Args:
            fund_code: 基金代码。
            year: 年报年份。
            force_refresh: 是否强制刷新。

        Returns:
            已解析年报。

        Raises:
            Exception: 允许具体仓库传播来源异常。
        """


@dataclass(frozen=True, slots=True)
class AnnualEvidenceScopeRequest:
    """Fund 层多年年报证据作用域请求。

    Attributes:
        fund_code: 基金代码。
        target_year: 当前必需年报年份。
        required_years: 必需年报年份；MVP 只允许包含 `target_year`。
        optional_years: 可降级的 prior 年份。
        max_years: 年报证据硬上限。
        force_refresh: 是否统一强制刷新。
        degradation_policy: 降级策略。
    """

    fund_code: str
    target_year: int
    required_years: tuple[int, ...]
    optional_years: tuple[int, ...]
    max_years: int = MAX_ANNUAL_EVIDENCE_YEARS
    force_refresh: bool = False
    degradation_policy: AnnualEvidenceDegradationPolicy = (
        CURRENT_YEAR_REQUIRED_PRIOR_YEARS_OPTIONAL
    )

    def __post_init__(self) -> None:
        """校验多年年报证据作用域。

        Args:
            无。

        Returns:
            无返回值。

        Raises:
            ValueError: 当基金代码、年份集合、上限或降级策略非法时抛出。
        """

        normalized_fund_code = self.fund_code.strip()
        if len(normalized_fund_code) != 6 or not normalized_fund_code.isdigit():
            raise ValueError("fund_code 必须是 6 位数字")
        if self.target_year <= 0:
            raise ValueError("target_year 必须为正整数")
        if self.max_years < 1 or self.max_years > MAX_ANNUAL_EVIDENCE_YEARS:
            raise ValueError("max_years 必须在 1..5 范围内")
        if self.degradation_policy != CURRENT_YEAR_REQUIRED_PRIOR_YEARS_OPTIONAL:
            raise ValueError("degradation_policy 不受支持")
        if self.required_years != (self.target_year,):
            raise ValueError("MVP required_years 必须且只能包含 target_year")
        if self.target_year in self.optional_years:
            raise ValueError("optional_years 不能包含 target_year")
        if len(set(self.optional_years)) != len(self.optional_years):
            raise ValueError("optional_years 不能重复")
        if any(year >= self.target_year for year in self.optional_years):
            raise ValueError("optional_years 必须早于 target_year")
        expected_optional_years = tuple(
            range(self.target_year - 1, self.target_year - len(self.optional_years) - 1, -1)
        )
        if self.optional_years != expected_optional_years:
            raise ValueError("optional_years 必须是 target_year 的连续前序年份")
        if len(self.required_years) + len(self.optional_years) > self.max_years:
            raise ValueError("requested years 不能超过 max_years")

    @property
    def canonical_years(self) -> tuple[int, ...]:
        """返回规范年份顺序。

        Args:
            无。

        Returns:
            target year 在前、prior years 降序排列的年份元组。

        Raises:
            无显式抛出。
        """

        return (self.target_year, *self.optional_years)


@dataclass(frozen=True, slots=True)
class AnnualEvidenceAnchor:
    """年度证据锚点。

    Attributes:
        schema_version: 锚点 schema 版本。
        anchor_id: 本 bundle 内稳定锚点 ID。
        source_year: 来源年报年份。
        source_field_id: 来源字段 ID。
        source_kind: 原 extractor 锚点来源类型。
        section_id: 年报章节。
        page_number: 页码。
        table_id: 表格 ID。
        row_locator: 行定位。
        note: 说明。
    """

    schema_version: str
    anchor_id: str
    source_year: int
    source_field_id: str
    source_kind: str
    section_id: str | None
    page_number: int | None
    table_id: str | None
    row_locator: str | None
    note: str | None


@dataclass(frozen=True, slots=True)
class AnnualEvidenceGap:
    """年度证据缺口。

    Attributes:
        gap_id: 稳定缺口 ID。
        year: 年份。
        status: 年度状态。
        source_failure_category: 来源失败类别。
        message: 安全错误说明。
    """

    gap_id: str
    year: int
    status: AnnualEvidenceAvailabilityStatus
    source_failure_category: AnnualReportSourceFailureCategory | None
    message: str


@dataclass(frozen=True, slots=True)
class AnnualYearEvidenceRecord:
    """单年年报证据摘要。

    Attributes:
        year: 年份。
        required: 是否为必需年份。
        status: 年度可用性状态。
        document_identity_status: 文档身份状态。
        source_failure_category: 来源失败类别。
        source_provenance: 公共来源 provenance。
        source_fund_id: 来源基金 ID。
        fields: 年度字段摘要。
        anchors: 年度锚点。
        gaps: 年度缺口。
    """

    year: int
    required: bool
    status: AnnualEvidenceAvailabilityStatus
    document_identity_status: AnnualEvidenceDocumentIdentityStatus
    source_failure_category: AnnualReportSourceFailureCategory | None
    source_provenance: PublicSourceProvenance | None
    source_fund_id: str | None
    fields: Mapping[str, ExtractedField[object]]
    anchors: tuple[AnnualEvidenceAnchor, ...]
    gaps: tuple[AnnualEvidenceGap, ...]


@dataclass(frozen=True, slots=True)
class CrossYearDerivedFact:
    """跨年派生事实，见模板第 5 章。

    Attributes:
        schema_version: schema 版本。
        fact_id: 稳定事实 ID。
        fact_type: 跨年事实类型。
        source_field_id: 来源字段 ID。
        status: 事实状态。
        values_by_year: 逐年结构化值。
        source_years: 支撑年份。
        source_year_anchor_ids: 支撑年份锚点 ID。
        dependency_requirements: 依赖 requirement。
        caveats: 降级或 fallback caveat。
    """

    schema_version: str
    fact_id: str
    fact_type: CrossYearFactType
    source_field_id: str
    status: Literal["available", "degraded"]
    values_by_year: Mapping[int, object]
    source_years: tuple[int, ...]
    source_year_anchor_ids: tuple[str, ...]
    dependency_requirements: tuple[str, ...]
    caveats: tuple[str, ...]

    def to_fact_value(self) -> dict[str, object]:
        """转成 `ChapterFactEntry.value` 可安全承载的结构。

        Args:
            无。

        Returns:
            JSON 兼容的事实值。

        Raises:
            无显式抛出。
        """

        return {
            "schema_version": self.schema_version,
            "fact_type": self.fact_type,
            "values_by_year": {str(year): value for year, value in self.values_by_year.items()},
            "source_years": self.source_years,
            "source_year_anchor_ids": self.source_year_anchor_ids,
            "dependency_requirements": self.dependency_requirements,
            "caveats": self.caveats,
        }


@dataclass(frozen=True, slots=True)
class AnnualEvidenceBundle:
    """多年年报证据 bundle。

    Attributes:
        schema_version: bundle schema 版本。
        fund_code: 基金代码。
        target_year: 当前必需年份。
        canonical_years: 规范年份顺序。
        current_year_bundle: 当前年份结构化数据包。
        year_records: 年度证据记录。
        available_years: 可用年份。
        gap_years: 可降级缺口年份。
        fail_closed_years: fail-closed 年份。
        source_provenance_by_year: 公共来源 provenance。
        source_documents_by_year: 安全文档身份记录。
        anchors_by_year: 年度锚点。
        data_gaps: 年度缺口。
        requirement_availability: requirement 级可用性摘要。
        cross_year_facts: 跨年事实。
        degradation_summary: 降级摘要。
        fallback_summary: fallback 摘要。
    """

    schema_version: str
    fund_code: str
    target_year: int
    canonical_years: tuple[int, ...]
    current_year_bundle: StructuredFundDataBundle
    year_records: tuple[AnnualYearEvidenceRecord, ...]
    available_years: tuple[int, ...]
    gap_years: tuple[int, ...]
    fail_closed_years: tuple[int, ...]
    source_provenance_by_year: Mapping[int, PublicSourceProvenance | None]
    source_documents_by_year: Mapping[int, Mapping[str, object]]
    anchors_by_year: Mapping[int, tuple[AnnualEvidenceAnchor, ...]]
    data_gaps: tuple[AnnualEvidenceGap, ...]
    requirement_availability: Mapping[str, Mapping[str, object]]
    cross_year_facts: tuple[CrossYearDerivedFact, ...]
    degradation_summary: Mapping[str, object]
    fallback_summary: Mapping[str, object]

    def anchor_by_id(self, anchor_id: str) -> AnnualEvidenceAnchor | None:
        """按 anchor ID 查找年度证据锚点。

        Args:
            anchor_id: 锚点 ID。

        Returns:
            命中时返回年度锚点，否则返回 `None`。

        Raises:
            无显式抛出。
        """

        for anchors in self.anchors_by_year.values():
            for anchor in anchors:
                if anchor.anchor_id == anchor_id:
                    return anchor
        return None


class AnnualEvidenceLoader:
    """Fund 层多年年报证据 loader。"""

    def __init__(self, repository: _AnnualReportRepository | None = None) -> None:
        """初始化 loader。

        Args:
            repository: 年报仓库；未提供时使用默认 `FundDocumentRepository`。

        Returns:
            无返回值。

        Raises:
            无显式抛出。
        """

        self._repository = repository or FundDocumentRepository()

    async def load(
        self,
        scope: AnnualEvidenceScopeRequest,
        *,
        current_year_bundle: StructuredFundDataBundle,
    ) -> AnnualEvidenceBundle:
        """加载 prior 年度证据并构造多年证据 bundle。

        Args:
            scope: Fund 层年度证据作用域。
            current_year_bundle: 当前年份结构化数据包。

        Returns:
            多年年报证据 bundle。

        Raises:
            ValueError: 当前年份结构化数据与 scope 不一致时抛出。
            Exception: 必需年份失败时传播来源异常。
        """

        if current_year_bundle.fund_code != scope.fund_code:
            raise ValueError("current_year_bundle fund_code 与 scope 不一致")
        if current_year_bundle.report_year != scope.target_year:
            raise ValueError("current_year_bundle report_year 必须等于 target_year")

        records: list[AnnualYearEvidenceRecord] = [
            _record_from_current_year_bundle(current_year_bundle)
        ]
        for year in scope.optional_years:
            records.append(await self._load_optional_year(scope, year))
        return _build_bundle(scope, current_year_bundle, tuple(records))

    async def _load_optional_year(
        self,
        scope: AnnualEvidenceScopeRequest,
        year: int,
    ) -> AnnualYearEvidenceRecord:
        """加载单个 optional prior 年份。

        Args:
            scope: Fund 层年度证据作用域。
            year: optional prior 年份。

        Returns:
            单年证据记录。

        Raises:
            无显式抛出；optional 年份失败会转为 year-level record。
        """

        try:
            report = await self._repository.load_annual_report(
                scope.fund_code,
                year,
                force_refresh=scope.force_refresh,
            )
        except Exception as exc:  # noqa: BLE001 - 年报来源异常需归类为年度缺口。
            category = _classify_source_failure(exc)
            status: AnnualEvidenceAvailabilityStatus = (
                "gap" if category in _DEGRADABLE_FAILURE_CATEGORIES else "failed_closed"
            )
            identity_status: AnnualEvidenceDocumentIdentityStatus = (
                "identity_mismatch" if category == "identity_mismatch" else "source_failed"
            )
            gap = _gap_for_failure(year, status, category, str(exc))
            return AnnualYearEvidenceRecord(
                year=year,
                required=False,
                status=status,
                document_identity_status=identity_status,
                source_failure_category=category,
                source_provenance=None,
                source_fund_id=None,
                fields={},
                anchors=(),
                gaps=(gap,),
            )
        return _record_from_prior_report(scope.fund_code, report)


def _record_from_current_year_bundle(
    bundle: StructuredFundDataBundle,
) -> AnnualYearEvidenceRecord:
    """从当前年份结构化数据包构造年度记录。

    Args:
        bundle: 当前年份结构化数据包。

    Returns:
        年度证据记录。

    Raises:
        无显式抛出。
    """

    fields = _fields_from_bundle(bundle)
    anchors = _anchors_for_fields(bundle.report_year, fields)
    return AnnualYearEvidenceRecord(
        year=bundle.report_year,
        required=True,
        status="available",
        document_identity_status="verified_annual_report",
        source_failure_category=None,
        source_provenance=bundle.source_provenance,
        source_fund_id=None,
        fields=fields,
        anchors=anchors,
        gaps=(),
    )


def _record_from_prior_report(
    requested_fund_code: str,
    report: ParsedAnnualReport,
) -> AnnualYearEvidenceRecord:
    """从 prior 年报构造年度记录。

    Args:
        requested_fund_code: 请求基金代码。
        report: 已加载年报。

    Returns:
        年度证据记录。

    Raises:
        无显式抛出；身份不匹配会转为 fail-closed 年度记录。
    """

    if report.key.fund_code != requested_fund_code:
        gap = _gap_for_failure(
            report.key.year,
            "failed_closed",
            "identity_mismatch",
            "prior-year report fund_code does not match requested fund_code",
        )
        return AnnualYearEvidenceRecord(
            year=report.key.year,
            required=False,
            status="failed_closed",
            document_identity_status="identity_mismatch",
            source_failure_category="identity_mismatch",
            source_provenance=project_public_source_provenance(report.metadata.source),
            source_fund_id=_source_fund_id(report.metadata.source),
            fields={},
            anchors=(),
            gaps=(gap,),
        )

    fields = _fields_from_prior_report(report)
    anchors = _anchors_for_fields(report.key.year, fields)
    return AnnualYearEvidenceRecord(
        year=report.key.year,
        required=False,
        status="available",
        document_identity_status="verified_annual_report",
        source_failure_category=None,
        source_provenance=project_public_source_provenance(report.metadata.source),
        source_fund_id=_source_fund_id(report.metadata.source),
        fields=fields,
        anchors=anchors,
        gaps=(),
    )


def _fields_from_bundle(bundle: StructuredFundDataBundle) -> Mapping[str, ExtractedField[object]]:
    """提取当前年份可参与跨年比较的字段。

    Args:
        bundle: 当前年份结构化数据包。

    Returns:
        字段名到抽取字段的映射。

    Raises:
        无显式抛出。
    """

    return {
        "fee_schedule": bundle.fee_schedule,
        "turnover_rate": bundle.turnover_rate,
        "share_change": bundle.share_change,
        "holdings_snapshot": bundle.holdings_snapshot,
        "portfolio_managers": bundle.portfolio_managers,
    }


def _fields_from_prior_report(report: ParsedAnnualReport) -> Mapping[str, ExtractedField[object]]:
    """从 prior 年报抽取跨年比较所需窄字段。

    Args:
        report: 已加载 prior 年报。

    Returns:
        字段名到抽取字段的映射。

    Raises:
        无显式抛出；extractor 内部异常自然传播为实现缺陷。
    """

    profile_result = extract_profile(report)
    manager_result = extract_manager_ownership(report)
    holdings_result = extract_holdings_share_change(report)
    return {
        "fee_schedule": profile_result.fee_schedule,
        "turnover_rate": manager_result.turnover_rate,
        "share_change": holdings_result.share_change,
        "holdings_snapshot": holdings_result.holdings_snapshot,
        "portfolio_managers": manager_result.portfolio_managers,
    }


def _anchors_for_fields(
    year: int,
    fields: Mapping[str, ExtractedField[object]],
) -> tuple[AnnualEvidenceAnchor, ...]:
    """把 extractor 锚点投影为年度锚点。

    Args:
        year: 年报年份。
        fields: 字段映射。

    Returns:
        年度锚点元组。

    Raises:
        无显式抛出。
    """

    anchors: list[AnnualEvidenceAnchor] = []
    for field_name, field in fields.items():
        for index, anchor in enumerate(field.anchors):
            anchors.append(_annual_anchor(year, field_name, index, anchor))
    return tuple(anchors)


def _annual_anchor(
    year: int,
    field_name: str,
    index: int,
    anchor: EvidenceAnchor,
) -> AnnualEvidenceAnchor:
    """构造年度锚点。

    Args:
        year: 年报年份。
        field_name: 字段名。
        index: 字段内锚点序号。
        anchor: extractor 锚点。

    Returns:
        年度锚点。

    Raises:
        无显式抛出。
    """

    source_field_id = f"annual_evidence.{field_name}"
    anchor_id = _stable_id(
        "annual-anchor",
        year,
        field_name,
        index,
        anchor.source_kind,
        anchor.section_id,
        anchor.table_id,
        anchor.row_locator,
    )
    return AnnualEvidenceAnchor(
        schema_version=ANNUAL_EVIDENCE_ANCHOR_SCHEMA_VERSION,
        anchor_id=anchor_id,
        source_year=year,
        source_field_id=source_field_id,
        source_kind=str(anchor.source_kind),
        section_id=anchor.section_id,
        page_number=anchor.page_number,
        table_id=anchor.table_id,
        row_locator=anchor.row_locator,
        note=anchor.note,
    )


def _build_bundle(
    scope: AnnualEvidenceScopeRequest,
    current_year_bundle: StructuredFundDataBundle,
    records: tuple[AnnualYearEvidenceRecord, ...],
) -> AnnualEvidenceBundle:
    """构造多年证据 bundle。

    Args:
        scope: Fund 层年度证据作用域。
        current_year_bundle: 当前年份结构化数据包。
        records: 年度记录。

    Returns:
        多年年报证据 bundle。

    Raises:
        无显式抛出。
    """

    available_years = tuple(record.year for record in records if record.status == "available")
    gap_years = tuple(record.year for record in records if record.status == "gap")
    fail_closed_years = tuple(record.year for record in records if record.status == "failed_closed")
    anchors_by_year = {record.year: record.anchors for record in records}
    data_gaps = tuple(gap for record in records for gap in record.gaps)
    source_provenance_by_year = {
        record.year: record.source_provenance for record in records
    }
    source_documents_by_year = {
        record.year: {
            "document_kind": "annual_report",
            "year": record.year,
            "document_identity_status": record.document_identity_status,
            "source_failure_category": record.source_failure_category,
        }
        for record in records
    }
    cross_year_facts = _derive_cross_year_facts(records)
    requirement_availability = _derive_requirement_availability(records, cross_year_facts)
    return AnnualEvidenceBundle(
        schema_version=ANNUAL_EVIDENCE_BUNDLE_SCHEMA_VERSION,
        fund_code=scope.fund_code,
        target_year=scope.target_year,
        canonical_years=scope.canonical_years,
        current_year_bundle=current_year_bundle,
        year_records=records,
        available_years=available_years,
        gap_years=gap_years,
        fail_closed_years=fail_closed_years,
        source_provenance_by_year=source_provenance_by_year,
        source_documents_by_year=source_documents_by_year,
        anchors_by_year=anchors_by_year,
        data_gaps=data_gaps,
        requirement_availability=requirement_availability,
        cross_year_facts=cross_year_facts,
        degradation_summary={
            "gap_years": gap_years,
            "fail_closed_years": fail_closed_years,
            "cross_year_claims_allowed": bool(cross_year_facts),
        },
        fallback_summary=_derive_fallback_summary(records),
    )


def _derive_cross_year_facts(
    records: Sequence[AnnualYearEvidenceRecord],
) -> tuple[CrossYearDerivedFact, ...]:
    """派生低风险跨年事实。

    Args:
        records: 年度记录。

    Returns:
        跨年事实元组。

    Raises:
        无显式抛出。
    """

    facts: list[CrossYearDerivedFact] = []
    for fact_type in _SUPPORTED_CROSS_YEAR_FACTS:
        field_name = _CROSS_YEAR_SOURCE_FIELDS[fact_type]
        available_records = tuple(
            record for record in records if _field_has_value_and_anchor(record, field_name)
        )
        if len(available_records) < 2:
            continue
        values_by_year = {
            record.year: record.fields[field_name].value for record in available_records
        }
        source_anchor_ids = tuple(
            _first_anchor_id(record, field_name) for record in available_records
        )
        facts.append(
            CrossYearDerivedFact(
                schema_version=ANNUAL_EVIDENCE_CROSS_YEAR_FACT_SCHEMA_VERSION,
                fact_id=_stable_id("cross-year-fact", fact_type, tuple(values_by_year)),
                fact_type=fact_type,
                source_field_id=f"annual_evidence.cross_year.{fact_type}",
                status="available",
                values_by_year=values_by_year,
                source_years=tuple(record.year for record in available_records),
                source_year_anchor_ids=source_anchor_ids,
                dependency_requirements=(f"ch5.requirement.{fact_type}",),
                caveats=_caveats_for_records(records),
            )
        )
    return tuple(facts)


def _derive_requirement_availability(
    records: Sequence[AnnualYearEvidenceRecord],
    facts: Sequence[CrossYearDerivedFact],
) -> Mapping[str, Mapping[str, object]]:
    """派生 requirement 级可用性。

    Args:
        records: 年度记录。
        facts: 跨年事实。

    Returns:
        requirement id 到状态摘要的映射。

    Raises:
        无显式抛出。
    """

    fact_requirements = {
        requirement: fact
        for fact in facts
        for requirement in fact.dependency_requirements
    }
    return {
        f"ch5.requirement.{fact_type}": {
            "status": "available" if f"ch5.requirement.{fact_type}" in fact_requirements else "unavailable",
            "available_years": tuple(record.year for record in records if record.status == "available"),
            "gap_years": tuple(record.year for record in records if record.status == "gap"),
            "fail_closed_years": tuple(record.year for record in records if record.status == "failed_closed"),
        }
        for fact_type in _SUPPORTED_CROSS_YEAR_FACTS
    }


def _derive_fallback_summary(
    records: Sequence[AnnualYearEvidenceRecord],
) -> Mapping[str, object]:
    """派生 bundle 级 fallback 摘要。

    Args:
        records: 年度记录。

    Returns:
        fallback 摘要。

    Raises:
        无显式抛出。
    """

    fallback_years = tuple(
        record.year
        for record in records
        if record.source_provenance is not None
        and record.source_provenance.fallback_used
    )
    categories = tuple(
        record.source_failure_category
        for record in records
        if record.source_failure_category is not None
    )
    return {
        "fallback_years": fallback_years,
        "fallback_year_count": len(fallback_years),
        "source_failure_categories": categories,
    }


def _field_has_value_and_anchor(record: AnnualYearEvidenceRecord, field_name: str) -> bool:
    """判断年度字段是否可用于跨年事实。

    Args:
        record: 年度记录。
        field_name: 字段名。

    Returns:
        字段有值且有年度锚点时返回 `True`。

    Raises:
        无显式抛出。
    """

    field = record.fields.get(field_name)
    if field is None or field.value is None or not field.anchors:
        return False
    return record.status == "available"


def _first_anchor_id(record: AnnualYearEvidenceRecord, field_name: str) -> str:
    """读取字段第一个年度锚点 ID。

    Args:
        record: 年度记录。
        field_name: 字段名。

    Returns:
        年度锚点 ID。

    Raises:
        ValueError: 找不到锚点时抛出。
    """

    source_field_id = f"annual_evidence.{field_name}"
    for anchor in record.anchors:
        if anchor.source_field_id == source_field_id:
            return anchor.anchor_id
    raise ValueError(f"字段缺少年度锚点: {record.year} {field_name}")


def _caveats_for_records(records: Sequence[AnnualYearEvidenceRecord]) -> tuple[str, ...]:
    """派生跨年事实 caveat。

    Args:
        records: 年度记录。

    Returns:
        caveat 元组。

    Raises:
        无显式抛出。
    """

    caveats: list[str] = []
    gap_years = tuple(record.year for record in records if record.status == "gap")
    fail_closed_years = tuple(record.year for record in records if record.status == "failed_closed")
    if gap_years:
        caveats.append(f"missing_or_unavailable_years={gap_years}")
    if fail_closed_years:
        caveats.append(f"fail_closed_years={fail_closed_years}")
    return tuple(caveats)


def _gap_for_failure(
    year: int,
    status: AnnualEvidenceAvailabilityStatus,
    category: AnnualReportSourceFailureCategory | None,
    message: str,
) -> AnnualEvidenceGap:
    """构造年度缺口。

    Args:
        year: 年份。
        status: 年度状态。
        category: 来源失败类别。
        message: 错误说明。

    Returns:
        年度缺口。

    Raises:
        无显式抛出。
    """

    return AnnualEvidenceGap(
        gap_id=_stable_id("annual-gap", year, status, category, message),
        year=year,
        status=status,
        source_failure_category=category,
        message=message,
    )


def _classify_source_failure(
    exc: Exception,
) -> AnnualReportSourceFailureCategory | None:
    """把来源异常归类为闭集失败类别。

    Args:
        exc: 来源异常。

    Returns:
        来源失败类别；未知异常返回 `unavailable`。

    Raises:
        无显式抛出。
    """

    if isinstance(exc, AnnualReportSourceNotFoundError | FileNotFoundError):
        return "not_found"
    if isinstance(exc, AnnualReportSourceUnavailableError):
        return "unavailable"
    if isinstance(exc, AnnualReportSourceMismatchError):
        return "identity_mismatch"
    if isinstance(exc, AnnualReportSourceSchemaError):
        return "schema_drift"
    if isinstance(exc, AnnualReportSourceIntegrityError):
        return "integrity_error"
    if isinstance(exc, AnnualReportSourceFallbackBlockedError):
        return exc.blocking_failure.category
    if isinstance(exc, AnnualReportSourceAggregateError):
        return _category_from_aggregate_error(exc)
    return "unavailable"


def _category_from_aggregate_error(
    exc: AnnualReportSourceAggregateError,
) -> AnnualReportSourceFailureCategory | None:
    """从聚合来源异常中提取年度失败类别。

    Args:
        exc: 聚合来源异常。

    Returns:
        失败类别。

    Raises:
        无显式抛出。
    """

    categories = tuple(failure.category for failure in exc.failures)
    if any(category in _FAIL_CLOSED_FAILURE_CATEGORIES for category in categories):
        for category in categories:
            if category in _FAIL_CLOSED_FAILURE_CATEGORIES:
                return category
    if "unavailable" in categories:
        return "unavailable"
    if "not_found" in categories:
        return "not_found"
    return None


def _source_fund_id(metadata: AnnualReportSourceMetadata | None) -> str | None:
    """读取来源基金 ID。

    Args:
        metadata: 年报来源 metadata。

    Returns:
        来源基金 ID。

    Raises:
        无显式抛出。
    """

    if metadata is None:
        return None
    return metadata.fund_id


def _stable_id(*parts: object) -> str:
    """构造短稳定 ID。

    Args:
        parts: 参与 hash 的结构化片段。

    Returns:
        稳定 ID。

    Raises:
        无显式抛出。
    """

    payload = json.dumps(parts, ensure_ascii=False, sort_keys=True, default=str)
    return hashlib.sha1(payload.encode("utf-8")).hexdigest()[:16]
