"""Evidence Confirm 年报引用 materializer no-live 测试。"""

from __future__ import annotations

import subprocess
import sys
from dataclasses import replace
from pathlib import Path

import pytest

from fund_agent.fund.chapter_facts import ChapterEvidenceAnchor, project_chapter_facts
from fund_agent.fund.documents.models import (
    AnnualReportMetadata,
    AnnualReportSourceMetadata,
    DocumentKey,
    ParsedAnnualReport,
    ParsedTable,
    ReportSection,
)
from fund_agent.fund.evidence_confirm import confirm_projection_evidence_v2
from fund_agent.fund.evidence_confirm_sources import (
    DEFAULT_MAX_SECTION_EXCERPT_CHARS,
    SUPPORTED_ROW_LOCATOR_RE,
    SUPPORTED_TABLE_ID_RE,
    EvidenceConfirmReferenceBuildRequest,
    build_annual_report_evidence_confirm_references,
)
from tests.fund.test_chapter_facts import _bundle


def test_table_row_reference_builds_for_compatible_locator() -> None:
    """验证兼容 table_id 与 row-0 可生成 annual_report excerpt。"""

    projection, _, _ = _projection_with_anchor(
        table_id="page-3-table-0",
        row_locator="row-0",
        page_number=3,
    )
    report = _parsed_report(
        tables=(
            ParsedTable(
                page_number=3,
                table_index=0,
                headers=("项目", "数值"),
                rows=(("换手率", "120%"),),
            ),
        ),
    )

    result = build_annual_report_evidence_confirm_references(_request(projection, report))

    assert result.status == "pass"
    assert result.issues == ()
    assert len(result.references) == 1
    reference = result.references[0]
    assert reference.reference_kind == "annual_report_excerpt"
    assert reference.source_kind == "annual_report"
    assert reference.source_truth_status == "proven"
    assert reference.document_year == 2024
    assert reference.section_id == "§8"
    assert reference.page_number == 3
    assert reference.table_id == "page-3-table-0"
    assert reference.row_locator == "row-0"
    assert "项目: 换手率" in reference.excerpt_text
    assert "数值: 120%" in reference.excerpt_text


def test_section_only_reference_uses_get_section_text_and_max_bound() -> None:
    """验证无 table/row locator 时只使用 section text 且执行字符上限。"""

    projection, _, _ = _projection_with_anchor(page_number=99)
    report = _parsed_report(section_body="换手率为 120%。这一段很长。")

    result = build_annual_report_evidence_confirm_references(
        EvidenceConfirmReferenceBuildRequest(
            fund_code="110011",
            report_year=2024,
            projection=projection,
            parsed_report=report,
            source_truth_status="proven",
            max_section_excerpt_chars=5,
        )
    )

    assert result.status == "pass"
    assert result.references[0].excerpt_text == "换手率为 "
    assert result.references[0].page_number == 99
    assert result.references[0].table_id is None
    assert result.references[0].row_locator is None


def test_negative_max_section_excerpt_chars_fails_closed_explicitly() -> None:
    """验证负数 section excerpt 上限不能绕过边界。"""

    projection, _, _ = _projection_with_anchor()
    report = _parsed_report(section_body="换手率为 120%。这一段不应完整进入 excerpt。")

    result = build_annual_report_evidence_confirm_references(
        EvidenceConfirmReferenceBuildRequest(
            fund_code="110011",
            report_year=2024,
            projection=projection,
            parsed_report=report,
            source_truth_status="proven",
            max_section_excerpt_chars=-1,
        )
    )

    assert result.status == "fail"
    assert result.references == ()
    assert {issue.reason for issue in result.issues} == {"invalid_max_section_excerpt_chars"}
    assert all(issue.severity == "blocking" for issue in result.issues)


def test_zero_max_section_excerpt_chars_fails_closed_as_empty_excerpt() -> None:
    """验证零 section excerpt 上限保留 empty_section_excerpt fail-closed 行为。"""

    projection, _, _ = _projection_with_anchor()
    report = _parsed_report(section_body="换手率为 120%。")

    result = build_annual_report_evidence_confirm_references(
        EvidenceConfirmReferenceBuildRequest(
            fund_code="110011",
            report_year=2024,
            projection=projection,
            parsed_report=report,
            source_truth_status="proven",
            max_section_excerpt_chars=0,
        )
    )

    assert result.status == "fail"
    assert result.references == ()
    assert {issue.reason for issue in result.issues} == {"empty_section_excerpt"}
    assert all(issue.severity == "blocking" for issue in result.issues)


@pytest.mark.parametrize(
    ("report_case", "anchor_kwargs", "expected_reason"),
    (
        ("empty_sections", {}, "missing_section"),
        ("empty_tables", {"table_id": "page-3-table-0", "row_locator": "row-0"}, "table_locator_not_found"),
        ("default", {"table_id": "table-0", "row_locator": "row-0"}, "unsupported_table_id_format"),
        (
            "one_row_table",
            {"table_id": "page-3-table-0", "row_locator": "row:0"},
            "unsupported_row_locator_format",
        ),
        (
            "one_row_table",
            {"table_id": "page-3-table-0", "row_locator": "row-1"},
            "row_locator_out_of_range",
        ),
        ("blank_section", {}, "empty_section_excerpt"),
    ),
)
def test_locator_and_section_failures_are_explicit(
    report_case: str,
    anchor_kwargs: dict[str, object],
    expected_reason: str,
) -> None:
    """验证空 section/table 与不支持 locator 都 fail-closed 且不 fallback。"""

    projection, _, _ = _projection_with_anchor(page_number=3, **anchor_kwargs)
    report = _report_for_case(report_case)

    result = build_annual_report_evidence_confirm_references(_request(projection, report))

    assert result.status == "fail"
    assert result.references == ()
    assert {issue.reason for issue in result.issues} == {expected_reason}
    assert all(issue.severity == "blocking" for issue in result.issues)


def test_header_row_width_mismatch_renders_deterministic_excerpt() -> None:
    """验证表头与行宽不一致时稳定输出且不抛异常。"""

    projection, _, _ = _projection_with_anchor(
        table_id="page-3-table-0",
        row_locator="row-0",
        page_number=3,
    )
    report = _parsed_report(
        tables=(ParsedTable(page_number=3, table_index=0, headers=("项目",), rows=(("换手率", "120%"),)),)
    )

    result = build_annual_report_evidence_confirm_references(_request(projection, report))

    assert result.status == "pass"
    assert result.references[0].excerpt_text.endswith("项目: 换手率 | column_1: 120%")


def test_wrong_year_fails_closed() -> None:
    """验证 anchor document_year 与 request 年份矛盾时失败。"""

    projection, _, _ = _projection_with_anchor(document_year=2023)

    result = build_annual_report_evidence_confirm_references(_request(projection, _parsed_report()))

    assert result.status == "fail"
    assert result.references == ()
    assert {issue.reason for issue in result.issues} == {"wrong_document_year"}


def test_non_annual_report_anchors_are_not_materialized() -> None:
    """验证 external_api、derived、unknown anchors 只产生 not-applicable issue。"""

    base_projection, chapter, _ = _projection_with_anchor()
    anchor = chapter.evidence_anchors[0]
    anchors = (
        replace(anchor, anchor_id="external", source_kind="external_api", section_id=None),
        replace(anchor, anchor_id="derived", source_kind="derived", section_id=None),
        replace(anchor, anchor_id="unknown", source_kind="unknown", section_id=None),
    )
    projection = replace(base_projection, chapters=(replace(chapter, evidence_anchors=anchors),))

    result = build_annual_report_evidence_confirm_references(_request(projection, _parsed_report()))

    assert result.status == "not_applicable"
    assert result.references == ()
    assert {issue.reason for issue in result.issues} == {"anchor_not_applicable"}
    assert {issue.anchor_id for issue in result.issues} == {"external", "derived", "unknown"}
    assert all(issue.severity == "informational" for issue in result.issues)


@pytest.mark.parametrize(
    ("request_status", "metadata_case", "expected_reason"),
    (
        ("not_proven", "proven", "source_truth_not_proven"),
        ("proven", "missing", "source_truth_metadata_missing"),
        ("proven", "fallback_used", "source_truth_metadata_negative"),
        ("proven", "eastmoney", "source_truth_metadata_negative"),
    ),
)
def test_candidate_not_proven_missing_or_negative_metadata_cannot_produce_proof_positive(
    request_status: str,
    metadata_case: str,
    expected_reason: str,
) -> None:
    """验证未证明请求和缺失/负向 metadata 不能生成 proven reference。"""

    projection, _, _ = _projection_with_anchor()
    metadata = _metadata_for_case(metadata_case)
    report = _parsed_report(metadata=metadata)

    result = build_annual_report_evidence_confirm_references(
        EvidenceConfirmReferenceBuildRequest(
            fund_code="110011",
            report_year=2024,
            projection=projection,
            parsed_report=report,
            source_truth_status=request_status,  # type: ignore[arg-type]
        )
    )

    assert result.status == "fail"
    assert result.references == ()
    assert {issue.reason for issue in result.issues} == {expected_reason}


def test_default_request_is_not_proven_and_section_bound_is_1200() -> None:
    """验证 request 默认不证明 source truth 且 section bound 为 1200。"""

    projection, _, _ = _projection_with_anchor()
    request = EvidenceConfirmReferenceBuildRequest(
        fund_code="110011",
        report_year=2024,
        projection=projection,
        parsed_report=_parsed_report(),
    )

    assert request.source_truth_status == "not_proven"
    assert request.max_section_excerpt_chars == DEFAULT_MAX_SECTION_EXCERPT_CHARS
    assert SUPPORTED_TABLE_ID_RE.pattern == r"^page-(?P<page_number>[1-9][0-9]*)-table-(?P<table_index>0|[1-9][0-9]*)$"
    assert SUPPORTED_ROW_LOCATOR_RE.pattern == r"^row-(?P<row_index>0|[1-9][0-9]*)$"


def test_produced_references_pipe_into_v2_pass_and_value_mismatch_fail() -> None:
    """验证 materialized references 可进入 V2，同源值通过，值不匹配失败。"""

    projection, chapter, fact = _projection_with_anchor(
        table_id="page-3-table-0",
        row_locator="row-0",
        page_number=3,
    )
    report = _parsed_report(
        tables=(ParsedTable(page_number=3, table_index=0, headers=("项目", "数值"), rows=(("换手率", "120%"),)),)
    )
    build_result = build_annual_report_evidence_confirm_references(_request(projection, report))

    passing = confirm_projection_evidence_v2(projection, build_result.references)
    mismatch_projection = replace(
        projection,
        chapters=(
            replace(
                chapter,
                facts=(replace(fact, value={"turnover_rate": "999%"}),),
            ),
        ),
    )
    failing = confirm_projection_evidence_v2(mismatch_projection, build_result.references)

    assert build_result.status == "pass"
    assert passing.overall_status == "pass"
    assert failing.overall_status == "fail"
    value_dim = next(d for d in failing.fact_results[0].dimension_results if d.dimension == "value_match")
    assert value_dim.status == "fail"


def test_import_isolation_does_not_import_repository() -> None:
    """验证模块导入不实例化 repository、不触发 PDF/cache/network 入口。"""

    completed = subprocess.run(
        [
            sys.executable,
            "-c",
                (
                    "from fund_agent.fund.documents.repository import FundDocumentRepository; "
                    "fail_init = lambda self, *args, **kwargs: (_ for _ in ()).throw(RuntimeError('repository instantiated')); "
                    "FundDocumentRepository.__init__ = fail_init; "
                    "import fund_agent.fund.evidence_confirm_sources; "
                    "print('import-ok')"
            ),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    source = Path("fund_agent/fund/evidence_confirm_sources.py").read_text(encoding="utf-8")

    assert completed.stdout.strip() == "import-ok"
    assert "FundDocumentRepository(" not in source
    assert "load_annual_report" not in source
    assert "fetch_pdf" not in source


def _projection_with_anchor(
    *,
    source_kind: str = "annual_report",
    document_year: int | None = 2024,
    section_id: str | None = "§8",
    page_number: int | None = None,
    table_id: str | None = None,
    row_locator: str | None = None,
) -> tuple[object, object, ChapterEvidenceAnchor]:
    """构造只含一个可用 fact 与一个 anchor 的 projection。

    Args:
        source_kind: anchor 来源类型。
        document_year: anchor 文档年份。
        section_id: anchor section id。
        page_number: anchor 页码。
        table_id: anchor table locator。
        row_locator: anchor row locator。

    Returns:
        projection、chapter、fact 三元组。

    Raises:
        AssertionError: fixture 中缺少目标 fact 时抛出。
    """

    base_projection = project_chapter_facts(_bundle(), chapter_ids=(3,))
    chapter = base_projection.chapters[0]
    fact = next(item for item in chapter.facts if item.source_field_id == "structured.turnover_rate")
    anchor_id = fact.evidence_anchor_ids[0]
    anchor = ChapterEvidenceAnchor(
        anchor_id=anchor_id,
        source_kind=source_kind,  # type: ignore[arg-type]
        document_year=document_year,
        section_id=section_id,
        page_number=page_number,
        table_id=table_id,
        row_locator=row_locator,
        note=None,
    )
    fact = replace(fact, value={"turnover_rate": "120%"}, evidence_anchor_ids=(anchor_id,))
    chapter = replace(chapter, facts=(fact,), evidence_anchors=(anchor,))
    projection = replace(base_projection, chapters=(chapter,))
    return projection, chapter, fact


def _request(
    projection: object,
    report: ParsedAnnualReport,
) -> EvidenceConfirmReferenceBuildRequest:
    """构造 proven materializer 请求。

    Args:
        projection: 章节事实投影。
        report: fake ParsedAnnualReport。

    Returns:
        materializer 请求。

    Raises:
        无显式抛出。
    """

    return EvidenceConfirmReferenceBuildRequest(
        fund_code="110011",
        report_year=2024,
        projection=projection,  # type: ignore[arg-type]
        parsed_report=report,
        source_truth_status="proven",
    )


def _report_for_case(report_case: str) -> ParsedAnnualReport:
    """按 case 构造 fake ParsedAnnualReport。

    Args:
        report_case: 测试 case 名称。

    Returns:
        fake ParsedAnnualReport。

    Raises:
        AssertionError: 未知 case 时抛出。
    """

    if report_case == "empty_sections":
        return _parsed_report(sections={})
    if report_case == "empty_tables":
        return _parsed_report(tables=())
    if report_case == "one_row_table":
        return _parsed_report(
            tables=(
                ParsedTable(
                    page_number=3,
                    table_index=0,
                    headers=("项目",),
                    rows=(("换手率",),),
                ),
            )
        )
    if report_case == "blank_section":
        return _parsed_report(section_body="   \n\t   ")
    if report_case == "default":
        return _parsed_report()
    raise AssertionError(f"unknown report_case: {report_case}")


def _parsed_report(
    *,
    section_body: str = "换手率为 120%。",
    sections: dict[str, ReportSection] | None = None,
    tables: tuple[ParsedTable, ...] = (),
    metadata: AnnualReportMetadata | None = None,
) -> ParsedAnnualReport:
    """构造 fake ParsedAnnualReport。

    Args:
        section_body: section 正文。
        sections: 可选章节索引覆盖。
        tables: fake 表格。
        metadata: fake 来源 metadata。

    Returns:
        fake ParsedAnnualReport。

    Raises:
        无显式抛出。
    """

    prefix = "目录\n"
    raw_text = f"{prefix}{section_body}"
    effective_sections = (
        {
            "§8": ReportSection(
                section_id="§8",
                title="§8 投资组合报告",
                start_offset=len(prefix),
                end_offset=len(raw_text),
                matched_rule="fixture",
                confidence=1.0,
            )
        }
        if sections is None
        else sections
    )
    return ParsedAnnualReport(
        key=DocumentKey(fund_code="110011", year=2024),
        raw_text=raw_text,
        sections=effective_sections,
        tables=tables,
        metadata=metadata or _proven_metadata(),
    )


def _metadata_for_case(metadata_case: str) -> AnnualReportMetadata:
    """按 case 构造 fake 来源 metadata。

    Args:
        metadata_case: 测试 case 名称。

    Returns:
        fake 来源 metadata。

    Raises:
        AssertionError: 未知 case 时抛出。
    """

    if metadata_case == "proven":
        return _proven_metadata()
    if metadata_case == "missing":
        return AnnualReportMetadata()
    if metadata_case == "fallback_used":
        return _negative_metadata(fallback_used=True)
    if metadata_case == "eastmoney":
        return _negative_metadata(source="eastmoney", selected_source="eastmoney")
    raise AssertionError(f"unknown metadata_case: {metadata_case}")


def _proven_metadata() -> AnnualReportMetadata:
    """构造满足当前 EID single-source admission 的 fake metadata。"""

    return AnnualReportMetadata(
        source=AnnualReportSourceMetadata(
            source="eid",
            fund_code="110011",
            report_year=2024,
            fallback_used=False,
            primary_failure_category=None,
            selected_source="eid",
            source_mode="single_source_only",
            fallback_enabled=False,
        )
    )


def _negative_metadata(
    *,
    source: str = "eid",
    selected_source: str = "eid",
    fallback_used: bool = False,
) -> AnnualReportMetadata:
    """构造不满足 proof admission 的 fake metadata。

    Args:
        source: 来源名称。
        selected_source: 选中来源。
        fallback_used: 是否使用 fallback。

    Returns:
        负向 metadata。

    Raises:
        无显式抛出。
    """

    return AnnualReportMetadata(
        source=AnnualReportSourceMetadata(
            source=source,  # type: ignore[arg-type]
            fund_code="110011",
            report_year=2024,
            fallback_used=fallback_used,
            primary_failure_category=None,
            selected_source=selected_source,  # type: ignore[arg-type]
            source_mode="single_source_only",
            fallback_enabled=False,
        )
    )
