"""Evidence Confirm 年报引用 materializer，见基金分析模板第 0-7 章。

本模块属于 Agent 层 ``fund_agent/fund`` 基金领域能力。它只消费调用方已经
传入的 ``ParsedAnnualReport``、``ChapterFactProjection`` 和章节锚点，不实例化
``FundDocumentRepository``，不读取 PDF/cache/source helper，不触发网络、provider、
Service、Host、renderer 或 quality gate 行为。
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Final, Literal

from fund_agent.fund.chapter_facts import (
    ChapterEvidenceAnchor,
    ChapterFactProjection,
)
from fund_agent.fund.documents.models import ParsedAnnualReport, ParsedTable
from fund_agent.fund.evidence_confirm import (
    EvidenceConfirmReference,
    EvidenceConfirmSourceTruthStatus,
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
    "build_annual_report_evidence_confirm_references",
]
