"""Evidence Confirm 年报引用 materializer，见基金分析模板第 0-7 章。

本模块属于 Agent 层 ``fund_agent/fund`` 基金领域能力。它只消费调用方已经
传入的 ``ParsedAnnualReport``、``ChapterFactProjection`` 和章节锚点，不实例化
``FundDocumentRepository``，不读取 PDF/cache/source helper，不触发网络、provider、
Service、Host、renderer 或 quality gate 行为。
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from inspect import iscoroutinefunction
from typing import Callable, Final, Literal

from fund_agent.fund.chapter_facts import (
    ChapterEvidenceAnchor,
    ChapterFactProjection,
)
from fund_agent.fund.documents.models import ParsedAnnualReport, ParsedTable
from fund_agent.fund.evidence_confirm import (
    EvidenceConfirmResultV2,
    EvidenceConfirmReference,
    EvidenceConfirmSourceTruthStatus,
    confirm_projection_evidence_v2,
)

DEFAULT_MAX_SECTION_EXCERPT_CHARS: Final[int] = 1200
SUPPORTED_TABLE_ID_RE: Final[re.Pattern[str]] = re.compile(
    r"^page-(?P<page_number>[1-9][0-9]*)-table-(?P<table_index>0|[1-9][0-9]*)$"
)
SUPPORTED_ROW_LOCATOR_RE: Final[re.Pattern[str]] = re.compile(
    r"^row-(?P<row_index>0|[1-9][0-9]*)$"
)

EvidenceConfirmReferenceBuildStatus = Literal["pass", "fail", "not_applicable"]
EvidenceConfirmReferenceBuildIssueSeverity = Literal["blocking", "informational"]
EvidenceConfirmRepositoryRunStatus = Literal["pass", "fail"]
EvidenceConfirmRepositoryPathwayStatus = Literal["pass", "fail"]
EvidenceConfirmRepositoryFailureCategory = Literal[
    "not_found",
    "unavailable",
    "schema_drift",
    "identity_mismatch",
    "integrity_error",
    "ambiguous_repository_failure",
]
EvidenceConfirmRepositoryRunIssueSeverity = Literal["blocking", "informational"]

_SOURCE_FAILURE_CATEGORIES: Final[frozenset[str]] = frozenset(
    ("not_found", "unavailable", "schema_drift", "identity_mismatch", "integrity_error")
)


@dataclass(frozen=True, slots=True)
class EvidenceConfirmReferenceBuildRequest:
    """Evidence Confirm 年报引用构建请求。

    Attributes:
        fund_code: 基金代码。
        report_year: 年报年份。
        projection: 已投影的章节事实，见模板第 0-7 章。
        parsed_report: 已加载并解析的年报对象。
        source_truth_status: 调用方请求的 source truth 状态，默认不证明。
        max_section_excerpt_chars: section excerpt 最大字符数。
    """

    fund_code: str
    report_year: int
    projection: ChapterFactProjection
    parsed_report: ParsedAnnualReport
    source_truth_status: EvidenceConfirmSourceTruthStatus = "not_proven"
    max_section_excerpt_chars: int = DEFAULT_MAX_SECTION_EXCERPT_CHARS


@dataclass(frozen=True, slots=True)
class EvidenceConfirmReferenceBuildIssue:
    """Evidence Confirm 年报引用构建 issue。

    Attributes:
        issue_id: 稳定 issue id。
        severity: 严重程度。
        anchor_id: 关联 anchor id。
        reason: 稳定原因码。
        message: 中文问题说明。
    """

    issue_id: str
    severity: EvidenceConfirmReferenceBuildIssueSeverity
    anchor_id: str
    reason: str
    message: str


@dataclass(frozen=True, slots=True)
class EvidenceConfirmReferenceBuildResult:
    """Evidence Confirm 年报引用构建结果。

    Attributes:
        references: 已构建的显式年报引用摘录。
        issues: 构建过程中的 fail-closed 或 not-applicable issue。
        status: 聚合状态；存在 blocking issue 时为 fail。
    """

    references: tuple[EvidenceConfirmReference, ...]
    issues: tuple[EvidenceConfirmReferenceBuildIssue, ...]
    status: EvidenceConfirmReferenceBuildStatus


@dataclass(frozen=True, slots=True)
class EvidenceConfirmRepositoryRunRequest:
    """Repository-bounded Evidence Confirm 执行请求。

    Args:
        无。

    Attributes:
        fund_code: 基金代码。
        report_year: 年报年份。
        projection: 显式传入的章节事实投影；为空时必须提供 projection_factory。
        projection_factory: repository load 成功后按 ParsedAnnualReport 构造投影的受控 hook。
        repository: 可注入的文档仓库；为空时由 runner 内部创建默认仓库。
        force_refresh: 是否强制刷新底层年报来源。
        max_section_excerpt_chars: section excerpt 最大字符数。
        run_v2_confirm: 是否将 materialized references 继续送入 V2。
    """

    fund_code: str
    report_year: int
    projection: ChapterFactProjection | None = None
    projection_factory: Callable[[ParsedAnnualReport], ChapterFactProjection] | None = None
    repository: object | None = None
    force_refresh: bool = False
    max_section_excerpt_chars: int = DEFAULT_MAX_SECTION_EXCERPT_CHARS
    run_v2_confirm: bool = True


@dataclass(frozen=True, slots=True)
class EvidenceConfirmRepositorySourceProvenance:
    """Repository runner 的安全来源 provenance 摘要。

    Args:
        无。

    Attributes:
        source: 来源名称。
        selected_source: 当前策略选中的来源。
        source_mode: 当前来源策略模式。
        fallback_enabled: 当前来源策略是否启用 fallback。
        fallback_used: 当前加载结果是否使用 fallback。
        primary_failure_category: 主来源失败类别。
        metadata_admitted: 是否满足当前 EID single-source/no-fallback admission。
    """

    source: str | None
    selected_source: str | None
    source_mode: str | None
    fallback_enabled: bool | None
    fallback_used: bool | None
    primary_failure_category: str | None
    metadata_admitted: bool


@dataclass(frozen=True, slots=True)
class EvidenceConfirmRepositoryRunIssue:
    """Repository runner issue。

    Args:
        无。

    Attributes:
        issue_id: 稳定 issue id。
        severity: 严重程度。
        reason: 稳定原因码。
        message: 中文问题说明。
        failure_category: 来源失败分类。
    """

    issue_id: str
    severity: EvidenceConfirmRepositoryRunIssueSeverity
    reason: str
    message: str
    failure_category: EvidenceConfirmRepositoryFailureCategory | None = None


@dataclass(frozen=True, slots=True)
class EvidenceConfirmRepositoryRunResult:
    """Repository-bounded Evidence Confirm 执行结果。

    Args:
        无。

    Attributes:
        status: 聚合执行状态。
        pathway_status: repository/source/PDF 通路状态，不等同于 strict V2 pass。
        pathway_warning_reasons: 通路可接受但 strict V2 非 pass 的稳定 warning 原因。
        fund_code: 基金代码。
        report_year: 年报年份。
        source_provenance: 安全来源 provenance 摘要。
        reference_build_result: 年报引用 materializer 结果。
        evidence_confirm_result: V2 复核结果。
        issues: runner 层 issue。
    """

    status: EvidenceConfirmRepositoryRunStatus
    pathway_status: EvidenceConfirmRepositoryPathwayStatus
    pathway_warning_reasons: tuple[str, ...]
    fund_code: str
    report_year: int
    source_provenance: EvidenceConfirmRepositorySourceProvenance | None
    reference_build_result: EvidenceConfirmReferenceBuildResult | None
    evidence_confirm_result: EvidenceConfirmResultV2 | None
    issues: tuple[EvidenceConfirmRepositoryRunIssue, ...]


def build_annual_report_evidence_confirm_references(
    request: EvidenceConfirmReferenceBuildRequest,
) -> EvidenceConfirmReferenceBuildResult:
    """从当前 ``ParsedAnnualReport`` 字段构建 Evidence Confirm 年报引用。

    该函数只 materialize ``source_kind="annual_report"`` 的章节锚点。表格定位仅支持
    ``page-{page_number}-table-{table_index}``，行定位仅支持零基 ``row-N``。不支持或
    无法唯一定位时 fail-closed，不按标题、单元格值、页码文本或 parser artifact 推断。

    Args:
        request: 年报引用构建请求。

    Returns:
        引用构建结果。

    Raises:
        无显式抛出。
    """

    issues: list[EvidenceConfirmReferenceBuildIssue] = []
    references: list[EvidenceConfirmReference] = []
    for anchor in _projection_annual_anchors(request.projection):
        reference, anchor_issues = _build_reference_for_anchor(request, anchor)
        issues.extend(anchor_issues)
        if reference is not None:
            references.append(reference)

    sorted_references = tuple(sorted(references, key=lambda item: item.anchor_id))
    sorted_issues = tuple(sorted(issues, key=lambda item: item.issue_id))
    return EvidenceConfirmReferenceBuildResult(
        references=sorted_references,
        issues=sorted_issues,
        status=_result_status(sorted_references, sorted_issues),
    )


async def run_repository_bounded_evidence_confirm(
    request: EvidenceConfirmRepositoryRunRequest,
) -> EvidenceConfirmRepositoryRunResult:
    """通过 `FundDocumentRepository.load_annual_report()` 驱动 Evidence Confirm。

    本函数是 EC-P2 repository-bounded runner。它只调用仓库公开年报加载入口，
    不读取 PDF/cache/source helper，不调用 Service、Host、renderer、quality gate、
    provider 或 LLM。见模板第 0-7 章 Evidence Confirm 路径。

    Args:
        request: Repository-bounded 执行请求。

    Returns:
        执行结果；任何来源或 materializer 问题均 fail-closed。

    Raises:
        无显式抛出；仓库异常被分类并写入 issue。
    """

    fund_code = request.fund_code.strip()
    if not fund_code:
        return _repository_failure_result(
            request,
            reason="invalid_fund_code",
            message="fund_code 不能为空。",
        )
    if request.report_year <= 0:
        return _repository_failure_result(
            request,
            reason="invalid_report_year",
            message="report_year 必须为正整数。",
        )
    if request.projection is None and request.projection_factory is None:
        return _repository_failure_result(
            request,
            reason="missing_projection",
            message="projection 与 projection_factory 不能同时为空。",
        )

    try:
        repository = request.repository if request.repository is not None else _default_repository()
    except Exception as exc:  # noqa: BLE001 - EC-P2 must return safe fail-closed result.
        return _repository_failure_result(
            request,
            reason="repository_initialization_failed",
            message=f"FundDocumentRepository 初始化失败: {exc.__class__.__name__}",
            failure_category="ambiguous_repository_failure",
        )
    load_annual_report = getattr(repository, "load_annual_report", None)
    if not iscoroutinefunction(load_annual_report):
        return _repository_failure_result(
            request,
            reason="invalid_repository",
            message="repository 必须暴露 async load_annual_report()。",
        )

    try:
        parsed_report = await load_annual_report(
            fund_code,
            request.report_year,
            force_refresh=request.force_refresh,
        )
    except Exception as exc:  # noqa: BLE001 - EC-P2 must classify repository boundary failures.
        category = _classify_repository_failure(exc)
        return _repository_failure_result(
            request,
            reason="repository_load_failed",
            message=f"repository.load_annual_report 失败: {exc.__class__.__name__}",
            failure_category=category,
        )

    source_provenance = _repository_source_provenance(parsed_report, fund_code, request.report_year)
    if not source_provenance.metadata_admitted:
        return EvidenceConfirmRepositoryRunResult(
            status="fail",
            pathway_status="fail",
            pathway_warning_reasons=(),
            fund_code=fund_code,
            report_year=request.report_year,
            source_provenance=source_provenance,
            reference_build_result=None,
            evidence_confirm_result=None,
            issues=(
                _repository_issue(
                    "source_truth_metadata_negative",
                    "ParsedAnnualReport 来源 metadata 未满足当前 EID single-source/no-fallback admission。",
                ),
            ),
        )

    projection = request.projection
    if projection is None and request.projection_factory is not None:
        try:
            projection = request.projection_factory(parsed_report)
        except Exception as exc:  # noqa: BLE001 - EC-P2 must fail closed and keep CLI output safe.
            return EvidenceConfirmRepositoryRunResult(
                status="fail",
                pathway_status="fail",
                pathway_warning_reasons=(),
                fund_code=fund_code,
                report_year=request.report_year,
                source_provenance=source_provenance,
                reference_build_result=None,
                evidence_confirm_result=None,
                issues=(
                    _repository_issue(
                        "projection_factory_failed",
                        f"projection_factory 失败: {exc.__class__.__name__}",
                    ),
                ),
            )

    build_result = build_annual_report_evidence_confirm_references(
        EvidenceConfirmReferenceBuildRequest(
            fund_code=fund_code,
            report_year=request.report_year,
            projection=projection,
            parsed_report=parsed_report,
            source_truth_status="proven",
            max_section_excerpt_chars=request.max_section_excerpt_chars,
        )
    )
    evidence_result = (
        confirm_projection_evidence_v2(projection, build_result.references)
        if request.run_v2_confirm
        else None
    )
    issues = _issues_from_reference_build(build_result)
    status = _repository_result_status(build_result, evidence_result, issues)
    pathway_status, pathway_warning_reasons = _repository_pathway_status(
        source_provenance,
        build_result,
        evidence_result,
        run_v2_confirm=request.run_v2_confirm,
    )
    return EvidenceConfirmRepositoryRunResult(
        status=status,
        pathway_status=pathway_status,
        pathway_warning_reasons=pathway_warning_reasons,
        fund_code=fund_code,
        report_year=request.report_year,
        source_provenance=source_provenance,
        reference_build_result=build_result,
        evidence_confirm_result=evidence_result,
        issues=issues,
    )


def _repository_failure_result(
    request: EvidenceConfirmRepositoryRunRequest,
    *,
    reason: str,
    message: str,
    failure_category: EvidenceConfirmRepositoryFailureCategory | None = None,
) -> EvidenceConfirmRepositoryRunResult:
    """构造 repository runner fail-closed 结果。

    Args:
        request: Repository-bounded 执行请求。
        reason: 稳定原因码。
        message: 中文问题说明。
        failure_category: 来源失败分类。

    Returns:
        fail-closed 执行结果。

    Raises:
        无显式抛出。
    """

    return EvidenceConfirmRepositoryRunResult(
        status="fail",
        pathway_status="fail",
        pathway_warning_reasons=(),
        fund_code=request.fund_code.strip(),
        report_year=request.report_year,
        source_provenance=None,
        reference_build_result=None,
        evidence_confirm_result=None,
        issues=(
            _repository_issue(
                reason,
                message,
                failure_category=failure_category,
            ),
        ),
    )


def _repository_issue(
    reason: str,
    message: str,
    *,
    severity: EvidenceConfirmRepositoryRunIssueSeverity = "blocking",
    failure_category: EvidenceConfirmRepositoryFailureCategory | None = None,
) -> EvidenceConfirmRepositoryRunIssue:
    """构造稳定 repository runner issue。

    Args:
        reason: 稳定原因码。
        message: 中文问题说明。
        severity: 严重程度。
        failure_category: 来源失败分类。

    Returns:
        runner issue。

    Raises:
        无显式抛出。
    """

    return EvidenceConfirmRepositoryRunIssue(
        issue_id=f"evidence-confirm-repository:{reason}",
        severity=severity,
        reason=reason,
        message=message,
        failure_category=failure_category,
    )


def _default_repository() -> object:
    """按需创建默认 FundDocumentRepository。

    Args:
        无。

    Returns:
        默认文档仓库实例。

    Raises:
        底层 repository 初始化异常原样抛出给调用方。
    """

    from fund_agent.fund.documents.repository import FundDocumentRepository

    return FundDocumentRepository()


def _classify_repository_failure(exc: Exception) -> EvidenceConfirmRepositoryFailureCategory:
    """把 repository 边界异常归类为稳定来源失败类别。

    Args:
        exc: repository.load_annual_report 抛出的异常。

    Returns:
        来源失败类别；不能证明具体来源类别时返回 ambiguous。

    Raises:
        无显式抛出。
    """

    explicit_category = _failure_category_from_value(getattr(exc, "category", None))
    if explicit_category is not None:
        return explicit_category

    blocking_failure = getattr(exc, "blocking_failure", None)
    blocking_category = _failure_category_from_value(getattr(blocking_failure, "category", None))
    if blocking_category is not None:
        return blocking_category

    aggregate_category = _single_failure_category(getattr(exc, "failures", None))
    if aggregate_category is not None:
        return aggregate_category

    class_name = exc.__class__.__name__
    if class_name == "AnnualReportSourceNotFoundError":
        return "not_found"
    if class_name == "AnnualReportSourceUnavailableError":
        return "unavailable"
    if class_name == "AnnualReportSourceSchemaError":
        return "schema_drift"
    if class_name == "AnnualReportSourceMismatchError":
        return "identity_mismatch"
    if class_name == "AnnualReportSourceIntegrityError":
        return "integrity_error"
    return "ambiguous_repository_failure"


def _single_failure_category(
    failures: object,
) -> EvidenceConfirmRepositoryFailureCategory | None:
    """从聚合 failures 中提取唯一稳定类别。

    Args:
        failures: 可能的 failures iterable。

    Returns:
        唯一来源失败类别；没有或不唯一时返回 ``None``。

    Raises:
        无显式抛出。
    """

    if not isinstance(failures, tuple):
        return None
    categories = frozenset(
        category
        for failure in failures
        if (category := _failure_category_from_value(getattr(failure, "category", None))) is not None
    )
    if len(categories) == 1:
        return next(iter(categories))
    return None


def _failure_category_from_value(
    value: object,
) -> EvidenceConfirmRepositoryFailureCategory | None:
    """规范化来源失败类别值。

    Args:
        value: 原始类别值。

    Returns:
        已知来源失败类别；未知时返回 ``None``。

    Raises:
        无显式抛出。
    """

    normalized = str(value).strip() if value is not None else ""
    if normalized in _SOURCE_FAILURE_CATEGORIES:
        return normalized  # type: ignore[return-value]
    return None


def _repository_source_provenance(
    parsed_report: ParsedAnnualReport,
    fund_code: str,
    report_year: int,
) -> EvidenceConfirmRepositorySourceProvenance:
    """从 ParsedAnnualReport 构造安全 provenance 摘要。

    Args:
        parsed_report: repository 返回的解析年报。
        fund_code: 请求基金代码。
        report_year: 请求年报年份。

    Returns:
        不包含 PDF 路径、URL 或原文的来源 provenance。

    Raises:
        无显式抛出。
    """

    source = parsed_report.metadata.source
    return EvidenceConfirmRepositorySourceProvenance(
        source=getattr(source, "source", None),
        selected_source=getattr(source, "selected_source", None),
        source_mode=getattr(source, "source_mode", None),
        fallback_enabled=getattr(source, "fallback_enabled", None),
        fallback_used=getattr(source, "fallback_used", None),
        primary_failure_category=getattr(source, "primary_failure_category", None),
        metadata_admitted=_repository_metadata_admitted(parsed_report, fund_code, report_year),
    )


def _repository_metadata_admitted(
    parsed_report: ParsedAnnualReport,
    fund_code: str,
    report_year: int,
) -> bool:
    """判断 repository 返回报告是否满足当前 proof-positive admission。

    Args:
        parsed_report: repository 返回的解析年报。
        fund_code: 请求基金代码。
        report_year: 请求年报年份。

    Returns:
        满足 EID single-source/no-fallback 且身份匹配时返回 ``True``。

    Raises:
        无显式抛出。
    """

    if parsed_report.key.fund_code != fund_code or parsed_report.key.year != report_year:
        return False
    source = parsed_report.metadata.source
    if source is None:
        return False
    return (
        getattr(source, "source", None) == "eid"
        and getattr(source, "selected_source", None) == "eid"
        and getattr(source, "source_mode", None) == "single_source_only"
        and getattr(source, "fallback_enabled", None) is False
        and getattr(source, "fallback_used", None) is False
        and getattr(source, "primary_failure_category", None) is None
        and getattr(source, "fund_code", None) == fund_code
        and getattr(source, "report_year", None) == report_year
    )


def _issues_from_reference_build(
    build_result: EvidenceConfirmReferenceBuildResult,
) -> tuple[EvidenceConfirmRepositoryRunIssue, ...]:
    """把 reference build issue 投影到 runner issue。

    Args:
        build_result: materializer 结果。

    Returns:
        runner issue 列表。

    Raises:
        无显式抛出。
    """

    return tuple(
        EvidenceConfirmRepositoryRunIssue(
            issue_id=f"evidence-confirm-repository:reference-build:{issue.anchor_id}:{issue.reason}",
            severity=issue.severity,
            reason=issue.reason,
            message=issue.message,
            failure_category=None,
        )
        for issue in build_result.issues
    )


def _repository_result_status(
    build_result: EvidenceConfirmReferenceBuildResult,
    evidence_result: EvidenceConfirmResultV2 | None,
    issues: tuple[EvidenceConfirmRepositoryRunIssue, ...],
) -> EvidenceConfirmRepositoryRunStatus:
    """计算 repository runner 聚合状态。

    Args:
        build_result: materializer 结果。
        evidence_result: V2 复核结果。
        issues: runner issue。

    Returns:
        pass 或 fail。

    Raises:
        无显式抛出。
    """

    if build_result.status != "pass":
        return "fail"
    if any(issue.severity == "blocking" for issue in issues):
        return "fail"
    if evidence_result is not None and evidence_result.overall_status != "pass":
        return "fail"
    return "pass"


def _repository_pathway_status(
    source_provenance: EvidenceConfirmRepositorySourceProvenance | None,
    build_result: EvidenceConfirmReferenceBuildResult | None,
    evidence_result: EvidenceConfirmResultV2 | None,
    *,
    run_v2_confirm: bool,
) -> tuple[EvidenceConfirmRepositoryPathwayStatus, tuple[str, ...]]:
    """计算 EC-P2 repository/source/PDF 通路状态。

    该状态只用于区分 source/PDF pathway 是否打通，不代表 strict V2 pass、
    字段正确性、语义 entailment、golden、readiness 或 release。当前唯一可接受的
    strict V2 非 pass 情况是 section-only smoke 引发的 E1 anchor_precision warning。

    Args:
        source_provenance: 安全来源 provenance。
        build_result: reference materializer 结果。
        evidence_result: V2 复核结果。
        run_v2_confirm: 当前请求是否要求运行 V2。

    Returns:
        pathway 状态与可接受 warning 原因。

    Raises:
        无显式抛出。
    """

    if source_provenance is None or not source_provenance.metadata_admitted:
        return "fail", ()
    if build_result is None or build_result.status != "pass" or not build_result.references:
        return "fail", ()
    if not run_v2_confirm:
        return "pass", ()
    if evidence_result is None:
        return "fail", ()
    if evidence_result.overall_status == "pass":
        return "pass", ()
    if evidence_result.overall_status != "warn":
        return "fail", ()
    if _v2_warn_is_only_anchor_precision(evidence_result):
        return "pass", ("v2_anchor_precision_warn_section_only_smoke",)
    return "fail", ()


def _v2_warn_is_only_anchor_precision(evidence_result: EvidenceConfirmResultV2) -> bool:
    """判断 V2 warn 是否只来自 E1 anchor_precision。

    Args:
        evidence_result: V2 复核结果。

    Returns:
        只有 E1 anchor_precision reviewable warning 时返回 ``True``。

    Raises:
        无显式抛出。
    """

    if evidence_result.hard_gate.blocking_issue_ids:
        return False
    if not evidence_result.issues:
        return False
    if any(issue.rule_code != "E1" or issue.severity != "reviewable" for issue in evidence_result.issues):
        return False

    warned_dimensions: list[str] = []
    failed_dimensions: list[str] = []
    for fact_result in evidence_result.fact_results:
        for dimension_result in fact_result.dimension_results:
            if dimension_result.status == "warn":
                warned_dimensions.append(dimension_result.dimension)
            if dimension_result.status == "fail":
                failed_dimensions.append(dimension_result.dimension)

    return bool(warned_dimensions) and not failed_dimensions and set(warned_dimensions) == {"anchor_precision"}


def _projection_annual_anchors(projection: ChapterFactProjection) -> tuple[ChapterEvidenceAnchor, ...]:
    """按章节与 anchor id 稳定读取 projection 内全部证据锚点。

    Args:
        projection: 章节事实投影。

    Returns:
        稳定排序后的章节证据锚点。

    Raises:
        无显式抛出。
    """

    anchors: list[tuple[int, ChapterEvidenceAnchor]] = []
    for chapter in projection.chapters:
        for anchor in chapter.evidence_anchors:
            anchors.append((chapter.chapter_id, anchor))
    return tuple(anchor for _, anchor in sorted(anchors, key=lambda item: (item[0], item[1].anchor_id)))


def _build_reference_for_anchor(
    request: EvidenceConfirmReferenceBuildRequest,
    anchor: ChapterEvidenceAnchor,
) -> tuple[EvidenceConfirmReference | None, tuple[EvidenceConfirmReferenceBuildIssue, ...]]:
    """构建单个 anchor 的年报引用。

    Args:
        request: 年报引用构建请求。
        anchor: 当前章节证据锚点。

    Returns:
        可选引用与 issue 列表。

    Raises:
        无显式抛出。
    """

    anchor_issues: list[EvidenceConfirmReferenceBuildIssue] = []
    if anchor.source_kind != "annual_report":
        return None, (
            _issue(
                anchor,
                "informational",
                "anchor_not_applicable",
                f"source_kind '{anchor.source_kind}' 不适用于 annual_report reference materializer。",
            ),
        )

    preflight_issue = _anchor_preflight_issue(request, anchor)
    if preflight_issue is not None:
        return None, (preflight_issue,)

    excerpt_result = _anchor_excerpt(request, anchor)
    anchor_issues.extend(excerpt_result.issues)
    if excerpt_result.excerpt_text is None:
        return None, tuple(anchor_issues)

    admission_issue = _source_truth_admission_issue(request, anchor)
    if admission_issue is not None:
        anchor_issues.append(admission_issue)
        return None, tuple(anchor_issues)

    return (
        EvidenceConfirmReference(
            anchor_id=anchor.anchor_id,
            reference_kind="annual_report_excerpt",
            source_kind="annual_report",
            document_year=request.report_year,
            section_id=anchor.section_id,
            page_number=excerpt_result.page_number,
            table_id=excerpt_result.table_id,
            row_locator=excerpt_result.row_locator,
            excerpt_text=excerpt_result.excerpt_text,
            source_truth_status="proven",
            candidate_only=False,
        ),
        tuple(anchor_issues),
    )


@dataclass(frozen=True, slots=True)
class _AnchorExcerptResult:
    """单个 anchor 的 excerpt 构建中间结果。

    Attributes:
        excerpt_text: 已归一且可复核的摘录文本。
        page_number: 引用页码。
        table_id: 引用表格 locator。
        row_locator: 引用行 locator。
        issues: 构建 issue。
    """

    excerpt_text: str | None
    page_number: int | None
    table_id: str | None
    row_locator: str | None
    issues: tuple[EvidenceConfirmReferenceBuildIssue, ...]


def _anchor_preflight_issue(
    request: EvidenceConfirmReferenceBuildRequest,
    anchor: ChapterEvidenceAnchor,
) -> EvidenceConfirmReferenceBuildIssue | None:
    """执行年报锚点身份前置校验。

    Args:
        request: 年报引用构建请求。
        anchor: 当前章节证据锚点。

    Returns:
        失败 issue；通过时返回 ``None``。

    Raises:
        无显式抛出。
    """

    if anchor.document_year is not None and anchor.document_year != request.report_year:
        return _issue(
            anchor,
            "blocking",
            "wrong_document_year",
            f"anchor document_year {anchor.document_year} 与 request.report_year {request.report_year} 不匹配。",
        )
    if not anchor.section_id or anchor.section_id not in request.parsed_report.sections:
        return _issue(
            anchor,
            "blocking",
            "missing_section",
            "annual_report anchor 缺少当前 ParsedAnnualReport 中存在的 section_id。",
        )
    if request.parsed_report.key.fund_code != request.fund_code:
        return _issue(
            anchor,
            "blocking",
            "parsed_report_fund_mismatch",
            f"parsed_report fund_code {request.parsed_report.key.fund_code} 与 request.fund_code {request.fund_code} 不匹配。",
        )
    if request.parsed_report.key.year != request.report_year:
        return _issue(
            anchor,
            "blocking",
            "parsed_report_year_mismatch",
            f"parsed_report year {request.parsed_report.key.year} 与 request.report_year {request.report_year} 不匹配。",
        )
    return None


def _anchor_excerpt(
    request: EvidenceConfirmReferenceBuildRequest,
    anchor: ChapterEvidenceAnchor,
) -> _AnchorExcerptResult:
    """构建 anchor 的 section/table/row excerpt。

    Args:
        request: 年报引用构建请求。
        anchor: 当前章节证据锚点。

    Returns:
        excerpt 中间结果。

    Raises:
        无显式抛出。
    """

    if anchor.row_locator and not anchor.table_id:
        return _empty_excerpt_issue(
            anchor,
            "row_locator_without_table_id",
            "row_locator 缺少兼容 table_id，不能进行行级定位。",
        )
    if anchor.table_id:
        return _table_excerpt(request, anchor)
    return _section_excerpt(request, anchor)


def _table_excerpt(
    request: EvidenceConfirmReferenceBuildRequest,
    anchor: ChapterEvidenceAnchor,
) -> _AnchorExcerptResult:
    """构建 table 或 table-row excerpt。

    Args:
        request: 年报引用构建请求。
        anchor: 当前章节证据锚点。

    Returns:
        table excerpt 中间结果。

    Raises:
        无显式抛出。
    """

    table_match = SUPPORTED_TABLE_ID_RE.fullmatch(anchor.table_id or "")
    if table_match is None:
        return _empty_excerpt_issue(
            anchor,
            "unsupported_table_id_format",
            "table_id 只支持 page-{page_number}-table-{table_index} 格式。",
        )
    page_number = int(table_match.group("page_number"))
    table_index = int(table_match.group("table_index"))
    if anchor.page_number is not None and anchor.page_number != page_number:
        return _empty_excerpt_issue(
            anchor,
            "page_number_mismatch",
            f"anchor page_number {anchor.page_number} 与 table_id page_number {page_number} 不匹配。",
        )

    tables = tuple(
        table
        for table in request.parsed_report.tables
        if table.page_number == page_number and table.table_index == table_index
    )
    if not tables:
        return _empty_excerpt_issue(
            anchor,
            "table_locator_not_found",
            "当前 ParsedAnnualReport 未找到兼容 table_id 对应的唯一表格。",
        )
    if len(tables) > 1:
        return _empty_excerpt_issue(
            anchor,
            "duplicate_table_locator",
            "当前 ParsedAnnualReport 中存在重复 page/table_index 表格，拒绝推断。",
        )

    table = tables[0]
    if anchor.row_locator:
        return _table_row_excerpt(anchor, table)
    excerpt = _normalize_whitespace(_format_table_excerpt(table))
    if not excerpt:
        return _empty_excerpt_issue(anchor, "empty_table_excerpt", "table excerpt 为空。")
    return _AnchorExcerptResult(
        excerpt_text=excerpt,
        page_number=page_number,
        table_id=anchor.table_id,
        row_locator=None,
        issues=(),
    )


def _table_row_excerpt(
    anchor: ChapterEvidenceAnchor,
    table: ParsedTable,
) -> _AnchorExcerptResult:
    """构建零基 row-N table-row excerpt。

    Args:
        anchor: 当前章节证据锚点。
        table: 已唯一命中的表格。

    Returns:
        table-row excerpt 中间结果。

    Raises:
        无显式抛出。
    """

    row_match = SUPPORTED_ROW_LOCATOR_RE.fullmatch(anchor.row_locator or "")
    if row_match is None:
        return _empty_excerpt_issue(
            anchor,
            "unsupported_row_locator_format",
            "row_locator 只支持零基 row-{zero_based_index} 格式。",
        )
    row_index = int(row_match.group("row_index"))
    if row_index >= len(table.rows):
        return _empty_excerpt_issue(
            anchor,
            "row_locator_out_of_range",
            f"row_locator {anchor.row_locator} 超出 ParsedTable.rows 范围。",
        )
    excerpt = _normalize_whitespace(_format_table_row_excerpt(table, row_index))
    if not excerpt:
        return _empty_excerpt_issue(anchor, "empty_table_row_excerpt", "table row excerpt 为空。")
    return _AnchorExcerptResult(
        excerpt_text=excerpt,
        page_number=table.page_number,
        table_id=anchor.table_id,
        row_locator=anchor.row_locator,
        issues=(),
    )


def _section_excerpt(
    request: EvidenceConfirmReferenceBuildRequest,
    anchor: ChapterEvidenceAnchor,
) -> _AnchorExcerptResult:
    """构建 section excerpt，不按 page_number 切 raw_text。

    Args:
        request: 年报引用构建请求。
        anchor: 当前章节证据锚点。

    Returns:
        section excerpt 中间结果。

    Raises:
        无显式抛出。
    """

    if request.max_section_excerpt_chars < 0:
        return _empty_excerpt_issue(
            anchor,
            "invalid_max_section_excerpt_chars",
            "max_section_excerpt_chars 不能为负数。",
        )
    section_text = request.parsed_report.get_section_text(anchor.section_id or "")
    excerpt = _normalize_whitespace(section_text or "")
    excerpt = excerpt[: request.max_section_excerpt_chars]
    if not excerpt:
        return _empty_excerpt_issue(anchor, "empty_section_excerpt", "section excerpt 为空。")
    return _AnchorExcerptResult(
        excerpt_text=excerpt,
        page_number=anchor.page_number,
        table_id=None,
        row_locator=None,
        issues=(),
    )


def _source_truth_admission_issue(
    request: EvidenceConfirmReferenceBuildRequest,
    anchor: ChapterEvidenceAnchor,
) -> EvidenceConfirmReferenceBuildIssue | None:
    """校验 proven reference 的显式 source-truth admission。

    Args:
        request: 年报引用构建请求。
        anchor: 当前章节证据锚点。

    Returns:
        失败 issue；通过时返回 ``None``。

    Raises:
        无显式抛出。
    """

    if request.source_truth_status != "proven":
        return _issue(
            anchor,
            "blocking",
            "source_truth_not_proven",
            "request.source_truth_status 不是 proven，不能 materialize proof-positive reference。",
        )
    source = request.parsed_report.metadata.source
    if source is None:
        return _issue(
            anchor,
            "blocking",
            "source_truth_metadata_missing",
            "ParsedAnnualReport 缺少来源 metadata，不能 materialize proof-positive reference。",
        )
    if not _metadata_admission_satisfied(request, source):
        return _issue(
            anchor,
            "blocking",
            "source_truth_metadata_negative",
            "ParsedAnnualReport 来源 metadata 未满足当前 EID single-source admission。",
        )
    return None


def _metadata_admission_satisfied(
    request: EvidenceConfirmReferenceBuildRequest,
    source: object,
) -> bool:
    """判断当前年报来源 metadata 是否满足 EC-P1A proof admission。

    Args:
        request: 年报引用构建请求。
        source: ``AnnualReportSourceMetadata`` 实例；以 object 接收避免扩大公开契约。

    Returns:
        满足当前 EID single-source metadata admission 时返回 ``True``。

    Raises:
        无显式抛出。
    """

    return (
        getattr(source, "source", None) == "eid"
        and getattr(source, "selected_source", None) == "eid"
        and getattr(source, "source_mode", None) == "single_source_only"
        and getattr(source, "fallback_enabled", None) is False
        and getattr(source, "fallback_used", None) is False
        and getattr(source, "primary_failure_category", None) is None
        and getattr(source, "fund_code", None) == request.fund_code
        and getattr(source, "report_year", None) == request.report_year
    )


def _format_table_row_excerpt(table: ParsedTable, row_index: int) -> str:
    """把裸 tuple row 格式化为稳定 table-row excerpt。

    Args:
        table: 已唯一命中的表格。
        row_index: 零基行号。

    Returns:
        稳定 table-row excerpt。

    Raises:
        无显式抛出。
    """

    row = table.rows[row_index]
    width = max(len(table.headers), len(row))
    cells: list[str] = []
    for index in range(width):
        header = _header_at(table.headers, index)
        value = row[index] if index < len(row) else ""
        cells.append(f"{header}: {value}")
    return f"page {table.page_number} table {table.table_index} {row_index}: " + " | ".join(cells)


def _format_table_excerpt(table: ParsedTable) -> str:
    """把当前表格格式化为稳定 table excerpt。

    Args:
        table: 已唯一命中的表格。

    Returns:
        稳定 table excerpt。

    Raises:
        无显式抛出。
    """

    rows = tuple(_format_table_row_excerpt(table, index) for index in range(len(table.rows)))
    return "\n".join(rows)


def _header_at(headers: tuple[str, ...], index: int) -> str:
    """读取表头；缺失或空白时使用稳定列名。

    Args:
        headers: 表头元组。
        index: 列号。

    Returns:
        表头或稳定 fallback 列名。

    Raises:
        无显式抛出。
    """

    if index < len(headers):
        header = headers[index].strip()
        if header:
            return header
    return f"column_{index}"


def _empty_excerpt_issue(
    anchor: ChapterEvidenceAnchor,
    reason: str,
    message: str,
) -> _AnchorExcerptResult:
    """构造只有 blocking issue 的空 excerpt 结果。

    Args:
        anchor: 当前章节证据锚点。
        reason: 稳定原因码。
        message: 中文问题说明。

    Returns:
        空 excerpt 中间结果。

    Raises:
        无显式抛出。
    """

    return _AnchorExcerptResult(
        excerpt_text=None,
        page_number=None,
        table_id=None,
        row_locator=None,
        issues=(_issue(anchor, "blocking", reason, message),),
    )


def _normalize_whitespace(value: str) -> str:
    """归一化空白字符。

    Args:
        value: 原始文本。

    Returns:
        去首尾且压缩空白后的文本。

    Raises:
        无显式抛出。
    """

    return re.sub(r"\s+", " ", value).strip()


def _issue(
    anchor: ChapterEvidenceAnchor,
    severity: EvidenceConfirmReferenceBuildIssueSeverity,
    reason: str,
    message: str,
) -> EvidenceConfirmReferenceBuildIssue:
    """构造稳定 reference build issue。

    Args:
        anchor: 当前章节证据锚点。
        severity: 严重程度。
        reason: 稳定原因码。
        message: 中文问题说明。

    Returns:
        构建 issue。

    Raises:
        无显式抛出。
    """

    return EvidenceConfirmReferenceBuildIssue(
        issue_id=f"evidence-confirm-reference-build:{anchor.anchor_id}:{reason}",
        severity=severity,
        anchor_id=anchor.anchor_id,
        reason=reason,
        message=message,
    )


def _result_status(
    references: tuple[EvidenceConfirmReference, ...],
    issues: tuple[EvidenceConfirmReferenceBuildIssue, ...],
) -> EvidenceConfirmReferenceBuildStatus:
    """计算 materializer 聚合状态。

    Args:
        references: 已构建引用。
        issues: 构建 issue。

    Returns:
        聚合状态。

    Raises:
        无显式抛出。
    """

    if any(issue.severity == "blocking" for issue in issues):
        return "fail"
    if references:
        return "pass"
    return "not_applicable"


__all__ = [
    "DEFAULT_MAX_SECTION_EXCERPT_CHARS",
    "SUPPORTED_ROW_LOCATOR_RE",
    "SUPPORTED_TABLE_ID_RE",
    "EvidenceConfirmReferenceBuildIssue",
    "EvidenceConfirmReferenceBuildRequest",
    "EvidenceConfirmReferenceBuildResult",
    "EvidenceConfirmRepositoryPathwayStatus",
    "EvidenceConfirmRepositoryRunIssue",
    "EvidenceConfirmRepositoryRunRequest",
    "EvidenceConfirmRepositoryRunResult",
    "EvidenceConfirmRepositorySourceProvenance",
    "build_annual_report_evidence_confirm_references",
    "run_repository_bounded_evidence_confirm",
]
