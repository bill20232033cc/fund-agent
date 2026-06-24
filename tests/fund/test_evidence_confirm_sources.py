"""Evidence Confirm 年报引用 materializer no-live 测试。"""

from __future__ import annotations

import subprocess
import sys
from dataclasses import replace
from types import SimpleNamespace

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
    EvidenceConfirmRepositoryRunRequest,
    build_annual_report_evidence_confirm_references,
    run_repository_bounded_evidence_confirm,
)
from scripts.evidence_confirm_ec_p2_live_sample import (
    PROJECTION_KIND,
    LiveProjectionUnavailableError,
    build_live_section_smoke_projection,
    run_authorized_sample,
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


def test_semantic_row_locator_with_table_narrows_to_single_matching_row_reference() -> None:
    """验证单 fact 全 token 唯一命中时语义 row_locator 收窄为行级 excerpt。"""

    projection, _, _ = _projection_with_anchor(
        table_id="page-3-table-0",
        row_locator="row:turnover_rate",
        page_number=3,
    )
    report = _parsed_report(
        tables=(
            ParsedTable(
                page_number=3,
                table_index=0,
                headers=("项目", "数值"),
                rows=(("换手率", "120%"), ("规模", "10 亿")),
            ),
        ),
    )

    result = build_annual_report_evidence_confirm_references(_request(projection, report))

    assert result.status == "pass"
    assert result.issues == ()
    assert len(result.references) == 1
    assert result.references[0].table_id == "page-3-table-0"
    assert result.references[0].row_locator == "row:turnover_rate"
    assert "项目: 换手率" in result.references[0].excerpt_text
    assert "项目: 规模" not in result.references[0].excerpt_text

    v2_result = confirm_projection_evidence_v2(projection, result.references)
    assert v2_result.overall_status == "pass"


def test_source_field_path_top_level_composite_scope_keeps_table_reference() -> None:
    """验证顶层复合字段 scope 不推断子字段行级 proof。

    parsed annual 默认路径只承诺顶层 ``source_field_path``，不能从 value 形状反推
    management_fee/custody_fee 的子字段来源。
    """

    projection, _, _ = _fee_schedule_projection_with_source_scope(
        row_locators=("source_field_path=fee_schedule; locator=fee_schedule",),
        evidence_anchor_ids=("fee-anchor",),
    )
    report = _parsed_report(
        tables=(
            ParsedTable(
                page_number=3,
                table_index=0,
                headers=("项目", "数值"),
                rows=(("管理费率", "1.50%"), ("托管费率", "0.25%")),
            ),
        ),
    )

    result = build_annual_report_evidence_confirm_references(_request(projection, report))

    assert result.status == "pass"
    assert len(result.references) == 1
    assert result.references[0].row_locator is None
    assert "项目: 管理费率" in result.references[0].excerpt_text
    assert "项目: 托管费率" in result.references[0].excerpt_text
    assert {issue.reason for issue in result.issues} == {
        "semantic_row_locator_degraded_to_table_excerpt"
    }


def test_source_field_path_subfield_scope_narrows_to_matching_rows() -> None:
    """验证显式子字段 source scope 可分别收窄到唯一行。"""

    management_locator = (
        "source_field_path=fee_schedule.management_fee; locator=management_fee"
    )
    custody_locator = "source_field_path=fee_schedule.custody_fee; locator=custody_fee"
    projection, _, _ = _fee_schedule_projection_with_source_scope(
        row_locators=(management_locator, custody_locator),
        evidence_anchor_ids=("fee-management-anchor", "fee-custody-anchor"),
    )
    report = _parsed_report(
        tables=(
            ParsedTable(
                page_number=3,
                table_index=0,
                headers=("项目", "数值"),
                rows=(("管理费率", "1.50%"), ("托管费率", "0.25%")),
            ),
        ),
    )

    result = build_annual_report_evidence_confirm_references(_request(projection, report))

    assert result.status == "pass"
    assert result.issues == ()
    references_by_locator = {
        reference.row_locator: reference for reference in result.references
    }
    assert set(references_by_locator) == {management_locator, custody_locator}
    assert "项目: 管理费率" in references_by_locator[management_locator].excerpt_text
    assert "项目: 托管费率" not in references_by_locator[management_locator].excerpt_text
    assert "项目: 托管费率" in references_by_locator[custody_locator].excerpt_text
    assert "项目: 管理费率" not in references_by_locator[custody_locator].excerpt_text

    v2_result = confirm_projection_evidence_v2(projection, result.references)
    assert v2_result.overall_status == "pass"


def test_source_field_path_subfield_duplicate_token_keeps_table_reference() -> None:
    """验证子字段 token 命中多行时仍降级为 table excerpt。"""

    projection, _, _ = _fee_schedule_projection_with_source_scope(
        row_locators=(
            "source_field_path=fee_schedule.management_fee; locator=management_fee",
        ),
        evidence_anchor_ids=("fee-management-anchor",),
    )
    report = _parsed_report(
        tables=(
            ParsedTable(
                page_number=3,
                table_index=0,
                headers=("项目", "数值"),
                rows=(("管理费率", "1.50%"), ("另一管理费率", "1.50%")),
            ),
        ),
    )

    result = build_annual_report_evidence_confirm_references(_request(projection, report))

    assert result.status == "pass"
    assert len(result.references) == 1
    assert result.references[0].row_locator is None
    assert result.references[0].excerpt_text.count("1.50%") == 2
    assert {issue.reason for issue in result.issues} == {
        "semantic_row_locator_degraded_to_table_excerpt"
    }


def test_processor_row_locator_with_table_builds_row_reference() -> None:
    """验证 Processor row locator 可直接生成行级 excerpt。"""

    row_locator = (
        "field=fee_schedule.management_fee; table_id=page-3-table-0; "
        "row=1; column=2; cell_id=c-1"
    )
    projection, _, _ = _projection_with_anchor(
        table_id="page-3-table-0",
        row_locator=row_locator,
        page_number=3,
    )
    report = _parsed_report(
        tables=(
            ParsedTable(
                page_number=3,
                table_index=0,
                headers=("项目", "数值"),
                rows=(("规模", "10 亿"), ("换手率", "120%")),
            ),
        ),
    )

    result = build_annual_report_evidence_confirm_references(_request(projection, report))

    assert result.status == "pass"
    assert result.issues == ()
    assert len(result.references) == 1
    assert result.references[0].table_id == "page-3-table-0"
    assert result.references[0].row_locator == row_locator
    assert "项目: 换手率" in result.references[0].excerpt_text
    assert "项目: 规模" not in result.references[0].excerpt_text

    v2_result = confirm_projection_evidence_v2(projection, result.references)
    assert v2_result.overall_status == "pass"


def test_processor_row_locator_shared_anchor_uses_explicit_row_reference() -> None:
    """验证多 fact 共用显式 Processor row locator 时可用该行级定位。"""

    row_locator = "field=fixture.bundle; table_id=page-3-table-0; row=0; column=1; cell_id=c-0"
    projection, chapter, fact = _projection_with_anchor(
        table_id="page-3-table-0",
        row_locator=row_locator,
        page_number=3,
    )
    other_fact = replace(
        fact,
        fact_id=f"{fact.fact_id}:scale",
        field_path="fixture.scale",
        source_field_id="structured.fixture_scale",
        source_field_name="fixture_scale",
        value={"scale": "10 亿"},
    )
    projection = replace(projection, chapters=(replace(chapter, facts=(fact, other_fact)),))
    report = _parsed_report(
        tables=(
            ParsedTable(
                page_number=3,
                table_index=0,
                headers=("项目", "数值", "备注"),
                rows=(("换手率", "120%", "规模 10 亿"), ("规模", "10 亿", "无")),
            ),
        ),
    )

    result = build_annual_report_evidence_confirm_references(_request(projection, report))

    assert result.status == "pass"
    assert result.issues == ()
    assert len(result.references) == 1
    assert result.references[0].row_locator == row_locator
    assert "项目: 换手率" in result.references[0].excerpt_text
    assert "项目: 规模" not in result.references[0].excerpt_text

    v2_result = confirm_projection_evidence_v2(projection, result.references)
    assert v2_result.overall_status == "pass"


@pytest.mark.parametrize(
    ("row_locator", "expected_reason"),
    (
        (
            "field=fee_schedule.management_fee; table_id=page-9-table-0; row=0; column=2",
            "processor_row_locator_table_mismatch",
        ),
        (
            "field=fee_schedule.management_fee; row=0; column=2",
            "processor_row_locator_missing_table_id",
        ),
        (
            "field=fee_schedule.management_fee; table_id=page-3-table-0; column=2",
            "processor_row_locator_missing_row",
        ),
        (
            "field=fee_schedule.management_fee; table_id=page-3-table-0; row=abc; column=2",
            "processor_row_locator_invalid_row",
        ),
        (
            "field=fee_schedule.management_fee; table_id=page-3-table-0; row=-1; column=2",
            "processor_row_locator_invalid_row",
        ),
        (
            "field=fee_schedule.management_fee; table_id=page-3-table-0; row=9; column=2",
            "processor_row_locator_out_of_range",
        ),
    ),
)
def test_processor_row_locator_failures_do_not_degrade_to_table_reference(
    row_locator: str,
    expected_reason: str,
) -> None:
    """验证已识别 Processor locator 错误 fail-closed 且不降级为 table proof。"""

    projection, _, _ = _projection_with_anchor(
        table_id="page-3-table-0",
        row_locator=row_locator,
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

    assert result.status == "fail"
    assert result.references == ()
    assert {issue.reason for issue in result.issues} == {expected_reason}
    assert all(issue.severity == "blocking" for issue in result.issues)


def test_semantic_row_locator_shared_anchor_ambiguity_keeps_table_reference() -> None:
    """验证多个 fact 共用语义 row anchor 时保持 table 级降级。"""

    projection, chapter, fact = _projection_with_anchor(
        table_id="page-3-table-0",
        row_locator="row:turnover_rate",
        page_number=3,
    )
    other_fact = replace(
        fact,
        fact_id=f"{fact.fact_id}:scale",
        field_path="fixture.scale",
        source_field_id="structured.fixture_scale",
        source_field_name="fixture_scale",
        value={"scale": "10 亿"},
    )
    projection = replace(projection, chapters=(replace(chapter, facts=(fact, other_fact)),))
    report = _parsed_report(
        tables=(
            ParsedTable(
                page_number=3,
                table_index=0,
                headers=("项目", "数值"),
                rows=(("换手率", "120%"), ("规模", "10 亿")),
            ),
        ),
    )

    result = build_annual_report_evidence_confirm_references(_request(projection, report))

    assert result.status == "pass"
    assert len(result.references) == 1
    assert result.references[0].table_id == "page-3-table-0"
    assert result.references[0].row_locator is None
    assert "项目: 换手率" in result.references[0].excerpt_text
    assert "项目: 规模" in result.references[0].excerpt_text
    assert {issue.reason for issue in result.issues} == {"semantic_row_locator_degraded_to_table_excerpt"}
    assert all(issue.severity == "informational" for issue in result.issues)


def test_semantic_row_locator_partial_token_match_keeps_table_reference() -> None:
    """验证 material token 不能完整命中单行时保持 table 级降级。"""

    projection, chapter, fact = _projection_with_anchor(
        table_id="page-3-table-0",
        row_locator="row:turnover_rate",
        page_number=3,
    )
    projection = replace(
        projection,
        chapters=(replace(chapter, facts=(replace(fact, value={"turnover_rate": "120%", "missing": "999%"}),)),),
    )
    report = _parsed_report(
        tables=(
            ParsedTable(
                page_number=3,
                table_index=0,
                headers=("项目", "数值"),
                rows=(("换手率", "120%"), ("规模", "10 亿")),
            ),
        ),
    )

    result = build_annual_report_evidence_confirm_references(_request(projection, report))

    assert result.status == "pass"
    assert result.references[0].row_locator is None
    assert "项目: 换手率" in result.references[0].excerpt_text
    assert "项目: 规模" in result.references[0].excerpt_text
    assert {issue.reason for issue in result.issues} == {"semantic_row_locator_degraded_to_table_excerpt"}


def test_row_locator_without_table_degrades_to_section_reference() -> None:
    """验证无 table_id 的语义 row_locator 降级为 section excerpt。"""

    projection, _, _ = _projection_with_anchor(row_locator="field=turnover_rate", page_number=7)
    report = _parsed_report(section_body="本章节披露换手率为 120%。")

    result = build_annual_report_evidence_confirm_references(_request(projection, report))

    assert result.status == "pass"
    assert len(result.references) == 1
    assert result.references[0].page_number == 7
    assert result.references[0].table_id is None
    assert result.references[0].row_locator is None
    assert result.references[0].excerpt_text == "本章节披露换手率为 120%。"
    assert {issue.reason for issue in result.issues} == {"semantic_row_locator_degraded_to_section_excerpt"}
    assert all(issue.severity == "informational" for issue in result.issues)


def test_degraded_row_locator_keeps_v2_anchor_precision_warning() -> None:
    """验证无法唯一收窄的 row_locator 降级后保留 E1 精度 warning。"""

    projection, chapter, fact = _projection_with_anchor(
        table_id="page-3-table-0",
        row_locator="row:0:换手率",
        page_number=3,
    )
    other_fact = replace(
        fact,
        fact_id=f"{fact.fact_id}:scale",
        field_path="fixture.scale",
        source_field_id="structured.fixture_scale",
        source_field_name="fixture_scale",
        value={"scale": "10 亿"},
    )
    projection = replace(projection, chapters=(replace(chapter, facts=(fact, other_fact)),))
    report = _parsed_report(
        tables=(
            ParsedTable(
                page_number=3,
                table_index=0,
                headers=("项目", "数值"),
                rows=(("换手率", "120%"), ("规模", "10 亿")),
            ),
        ),
    )
    build_result = build_annual_report_evidence_confirm_references(_request(projection, report))

    result = confirm_projection_evidence_v2(projection, build_result.references)

    assert build_result.status == "pass"
    assert result.overall_status == "warn"
    fact_result = result.fact_results[0]
    dimensions = {dimension.dimension: dimension for dimension in fact_result.dimension_results}
    assert dimensions["anchor_precision"].status == "warn"
    assert dimensions["source_support"].status == "pass"
    assert dimensions["missing_evidence"].status == "pass"
    assert dimensions["value_match"].status == "pass"
    assert {issue.rule_code for issue in result.issues} == {"E1"}


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


@pytest.mark.asyncio
async def test_repository_runner_uses_only_load_annual_report_and_passes_v2() -> None:
    """验证 repository runner 只调用 load_annual_report 并输出 proof-positive V2 pass。"""

    projection, _, _ = _projection_with_anchor(
        table_id="page-3-table-0",
        row_locator="row-0",
        page_number=3,
    )
    report = _parsed_report(
        tables=(ParsedTable(page_number=3, table_index=0, headers=("项目", "数值"), rows=(("换手率", "120%"),)),)
    )
    repository = _PoisonRepository(report)

    result = await run_repository_bounded_evidence_confirm(
        EvidenceConfirmRepositoryRunRequest(
            fund_code="110011",
            report_year=2024,
            projection=projection,  # type: ignore[arg-type]
            repository=repository,
            force_refresh=True,
        )
    )

    assert repository.calls == (("110011", 2024, True),)
    assert result.status == "pass"
    assert result.pathway_status == "pass"
    assert result.pathway_warning_reasons == ()
    assert result.source_provenance is not None
    assert result.source_provenance.metadata_admitted is True
    assert result.reference_build_result is not None
    assert result.reference_build_result.status == "pass"
    assert result.evidence_confirm_result is not None
    assert result.evidence_confirm_result.overall_status == "pass"
    assert result.issues == ()


@pytest.mark.asyncio
async def test_repository_runner_can_build_projection_after_repository_load() -> None:
    """验证 projection_factory 在 runner 内 repository load 成功后执行。"""

    projection, _, _ = _projection_with_anchor(
        table_id="page-3-table-0",
        row_locator="row-0",
        page_number=3,
    )
    report = _parsed_report(
        tables=(ParsedTable(page_number=3, table_index=0, headers=("项目", "数值"), rows=(("换手率", "120%"),)),)
    )
    repository = _PoisonRepository(report)
    calls: list[DocumentKey] = []

    def projection_factory(parsed_report: ParsedAnnualReport) -> object:
        """记录 runner 传入的 parsed report 并返回 projection。"""

        calls.append(parsed_report.key)
        return projection

    result = await run_repository_bounded_evidence_confirm(
        EvidenceConfirmRepositoryRunRequest(
            fund_code="110011",
            report_year=2024,
            projection_factory=projection_factory,  # type: ignore[arg-type]
            repository=repository,
            force_refresh=True,
        )
    )

    assert repository.calls == (("110011", 2024, True),)
    assert calls == [DocumentKey(fund_code="110011", year=2024)]
    assert result.status == "pass"
    assert result.pathway_status == "pass"


@pytest.mark.asyncio
async def test_repository_runner_section_smoke_warn_is_pathway_pass() -> None:
    """验证 section-only smoke 的 E1 warning 可作为 EC-P2 pathway pass。"""

    report = _parsed_report(section_body="目标 section token 120%")
    repository = _PoisonRepository(report)

    result = await run_repository_bounded_evidence_confirm(
        EvidenceConfirmRepositoryRunRequest(
            fund_code="110011",
            report_year=2024,
            projection_factory=build_live_section_smoke_projection,
            repository=repository,
        )
    )

    assert result.status == "fail"
    assert result.pathway_status == "pass"
    assert result.pathway_warning_reasons == ("v2_anchor_precision_warn_section_only_smoke",)
    assert result.reference_build_result is not None
    assert result.reference_build_result.status == "pass"
    assert result.evidence_confirm_result is not None
    assert result.evidence_confirm_result.overall_status == "warn"
    assert {issue.rule_code for issue in result.evidence_confirm_result.issues} == {"E1"}
    warned_dimensions = {
        dimension.dimension
        for fact_result in result.evidence_confirm_result.fact_results
        for dimension in fact_result.dimension_results
        if dimension.status == "warn"
    }
    assert warned_dimensions == {"anchor_precision"}


@pytest.mark.asyncio
async def test_repository_runner_degraded_semantic_row_locator_warn_is_pathway_pass() -> None:
    """验证语义 row_locator 不能唯一收窄时，EC-P2 pathway 仍可通过。"""

    projection, chapter, fact = _projection_with_anchor(
        table_id="page-3-table-0",
        row_locator="row:0:换手率",
        page_number=3,
    )
    other_fact = replace(
        fact,
        fact_id=f"{fact.fact_id}:scale",
        field_path="fixture.scale",
        source_field_id="structured.fixture_scale",
        source_field_name="fixture_scale",
        value={"scale": "10 亿"},
    )
    projection = replace(projection, chapters=(replace(chapter, facts=(fact, other_fact)),))
    report = _parsed_report(
        tables=(
            ParsedTable(
                page_number=3,
                table_index=0,
                headers=("项目", "数值"),
                rows=(("换手率", "120%"), ("规模", "10 亿")),
            ),
        ),
    )
    repository = _PoisonRepository(report)

    result = await run_repository_bounded_evidence_confirm(
        EvidenceConfirmRepositoryRunRequest(
            fund_code="110011",
            report_year=2024,
            projection=projection,  # type: ignore[arg-type]
            repository=repository,
        )
    )

    assert result.status == "fail"
    assert result.pathway_status == "pass"
    assert result.reference_build_result is not None
    assert result.reference_build_result.status == "pass"
    assert {issue.reason for issue in result.reference_build_result.issues} == {
        "semantic_row_locator_degraded_to_table_excerpt"
    }
    assert result.evidence_confirm_result is not None
    assert result.evidence_confirm_result.overall_status == "warn"
    warned_dimensions = {
        dimension.dimension
        for fact_result in result.evidence_confirm_result.fact_results
        for dimension in fact_result.dimension_results
        if dimension.status == "warn"
    }
    failed_dimensions = {
        dimension.dimension
        for fact_result in result.evidence_confirm_result.fact_results
        for dimension in fact_result.dimension_results
        if dimension.status == "fail"
    }
    assert warned_dimensions == {"anchor_precision"}
    assert failed_dimensions == set()


@pytest.mark.asyncio
async def test_repository_runner_rejects_invalid_repository_shape() -> None:
    """验证非 async load_annual_report 仓库不能进入来源或 PDF 路径。"""

    class InvalidRepository:
        """缺少 async 边界的 fake repository。"""

        def load_annual_report(self, fund_code: str, report_year: int, *, force_refresh: bool = False) -> None:
            """同步方法应被拒绝。"""

    projection, _, _ = _projection_with_anchor()

    result = await run_repository_bounded_evidence_confirm(
        EvidenceConfirmRepositoryRunRequest(
            fund_code="110011",
            report_year=2024,
            projection=projection,  # type: ignore[arg-type]
            repository=InvalidRepository(),
        )
    )

    assert result.status == "fail"
    assert result.pathway_status == "fail"
    assert result.reference_build_result is None
    assert {issue.reason for issue in result.issues} == {"invalid_repository"}


@pytest.mark.asyncio
async def test_repository_runner_rejects_negative_source_provenance_before_v2() -> None:
    """验证负向来源 metadata 不能进入 proof-positive reference 或 V2。"""

    projection, _, _ = _projection_with_anchor()
    repository = _PoisonRepository(_parsed_report(metadata=_negative_metadata(fallback_used=True)))

    result = await run_repository_bounded_evidence_confirm(
        EvidenceConfirmRepositoryRunRequest(
            fund_code="110011",
            report_year=2024,
            projection=projection,  # type: ignore[arg-type]
            repository=repository,
        )
    )

    assert result.status == "fail"
    assert result.pathway_status == "fail"
    assert result.source_provenance is not None
    assert result.source_provenance.metadata_admitted is False
    assert result.reference_build_result is None
    assert result.evidence_confirm_result is None
    assert {issue.reason for issue in result.issues} == {"source_truth_metadata_negative"}


@pytest.mark.asyncio
async def test_repository_runner_propagates_materializer_failure() -> None:
    """验证 materializer fail-closed issue 会提升为 runner fail。"""

    projection, _, _ = _projection_with_anchor(section_id="§missing")
    repository = _PoisonRepository(_parsed_report())

    result = await run_repository_bounded_evidence_confirm(
        EvidenceConfirmRepositoryRunRequest(
            fund_code="110011",
            report_year=2024,
            projection=projection,  # type: ignore[arg-type]
            repository=repository,
        )
    )

    assert result.status == "fail"
    assert result.pathway_status == "fail"
    assert result.reference_build_result is not None
    assert result.reference_build_result.status == "fail"
    assert {issue.reason for issue in result.issues} == {"missing_section"}


@pytest.mark.asyncio
async def test_repository_runner_fails_when_v2_value_mismatches() -> None:
    """验证 reference materialized 成功但 V2 值不匹配时 runner 失败。"""

    projection, chapter, fact = _projection_with_anchor(
        table_id="page-3-table-0",
        row_locator="row-0",
        page_number=3,
    )
    mismatch_projection = replace(
        projection,
        chapters=(replace(chapter, facts=(replace(fact, value={"turnover_rate": "999%"}),)),),
    )
    repository = _PoisonRepository(
        _parsed_report(
            tables=(ParsedTable(page_number=3, table_index=0, headers=("项目", "数值"), rows=(("换手率", "120%"),)),)
        )
    )

    result = await run_repository_bounded_evidence_confirm(
        EvidenceConfirmRepositoryRunRequest(
            fund_code="110011",
            report_year=2024,
            projection=mismatch_projection,  # type: ignore[arg-type]
            repository=repository,
        )
    )

    assert result.status == "fail"
    assert result.pathway_status == "fail"
    assert result.reference_build_result is not None
    assert result.reference_build_result.status == "pass"
    assert result.evidence_confirm_result is not None
    assert result.evidence_confirm_result.overall_status == "fail"


class _FailingRepository:
    """抛出指定异常的 fake repository。"""

    def __init__(self, exception: Exception) -> None:
        """记录待抛异常。"""

        self._exception = exception

    async def load_annual_report(
        self,
        fund_code: str,
        report_year: int,
        *,
        force_refresh: bool = False,
    ) -> ParsedAnnualReport:
        """模拟 repository.load_annual_report 失败。"""

        raise self._exception


class _CategorizedRepositoryError(Exception):
    """带 category 属性的 fake repository 异常。"""

    def __init__(self, category: str) -> None:
        """记录来源失败类别。"""

        self.category = category
        super().__init__(category)


class _AggregateRepositoryError(Exception):
    """带 failures 属性的 fake repository 聚合异常。"""

    def __init__(self, failures: tuple[object, ...]) -> None:
        """记录逐来源失败。"""

        self.failures = failures
        super().__init__("aggregate")


def _exception_named(class_name: str) -> Exception:
    """构造指定类名的 fake 异常。

    Args:
        class_name: 需要模拟的异常类名。

    Returns:
        fake 异常实例。

    Raises:
        无显式抛出。
    """

    exception_cls = type(class_name, (Exception,), {})
    return exception_cls(class_name)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("exception", "expected_category"),
    (
        (_exception_named("AnnualReportSourceNotFoundError"), "not_found"),
        (_exception_named("AnnualReportSourceUnavailableError"), "unavailable"),
        (_exception_named("AnnualReportSourceSchemaError"), "schema_drift"),
        (_exception_named("AnnualReportSourceMismatchError"), "identity_mismatch"),
        (_exception_named("AnnualReportSourceIntegrityError"), "integrity_error"),
        (FileNotFoundError("missing"), "not_found"),
        (_CategorizedRepositoryError("not_found"), "not_found"),
        (_AggregateRepositoryError((SimpleNamespace(category="unavailable"),)), "unavailable"),
        (RuntimeError("boom"), "ambiguous_repository_failure"),
    ),
)
async def test_repository_runner_classifies_repository_failures(
    exception: Exception,
    expected_category: str,
) -> None:
    """验证 repository 边界异常被归类为稳定失败类别。"""

    projection, _, _ = _projection_with_anchor()
    result = await run_repository_bounded_evidence_confirm(
        EvidenceConfirmRepositoryRunRequest(
            fund_code="110011",
            report_year=2024,
            projection=projection,  # type: ignore[arg-type]
            repository=_FailingRepository(exception),
        )
    )

    assert result.status == "fail"
    assert result.pathway_status == "fail"
    assert {issue.reason for issue in result.issues} == {"repository_load_failed"}
    assert {issue.failure_category for issue in result.issues} == {expected_category}


@pytest.mark.asyncio
async def test_live_sample_returns_safe_payload_when_repository_fails() -> None:
    """验证 sample path 的 repository 失败不 traceback，返回安全分类 payload。"""

    payload = await run_authorized_sample(
        force_refresh=True,
        repository=_FailingRepository(_exception_named("AnnualReportSourceUnavailableError")),
    )

    assert payload["sample"] == "004393/2025"
    assert payload["status"] == "fail"
    assert payload["pathway_status"] == "fail"
    assert payload["pathway_warning_reasons"] == ()
    assert payload["projection_kind"] == PROJECTION_KIND
    assert payload["field_correctness_proven"] is False
    assert payload["issue_reasons"] == ("repository_load_failed",)
    assert payload["failure_categories"] == ("unavailable",)


def test_live_section_smoke_projection_uses_first_non_empty_section() -> None:
    """验证 sample helper 从 fake parsed report 稳定构造 section smoke projection。"""

    report = _multi_section_report()

    projection = build_live_section_smoke_projection(report)

    assert projection.fund_code == "110011"
    assert projection.report_year == 2024
    assert projection.classification_basis == (PROJECTION_KIND,)
    chapter = projection.chapters[0]
    assert chapter.fund_type == "unknown"
    assert chapter.evidence_anchors[0].section_id == "§2"
    assert chapter.evidence_anchors[0].source_kind == "annual_report"
    assert chapter.facts[0].source_field_id == "ec_p2.live_section_smoke"
    assert chapter.facts[0].value == {"section_smoke_token": "目标 section token 120%"}


def test_live_section_smoke_projection_fails_when_all_sections_empty() -> None:
    """验证 sample helper 在无非空 section 时显式失败。"""

    report = _parsed_report(section_body="   ")

    with pytest.raises(LiveProjectionUnavailableError, match="live_projection_section_unavailable"):
        build_live_section_smoke_projection(report)


def test_import_isolation_does_not_import_repository() -> None:
    """验证模块导入不实例化 repository、不触发 PDF/cache/network 入口。"""

    completed = subprocess.run(
        [
            sys.executable,
            "-c",
                (
                    "from fund_agent.fund.documents.repository import FundDocumentRepository; "
                    "called = {'load': False}; "
                    "fail_init = lambda self, *args, **kwargs: (_ for _ in ()).throw(RuntimeError('repository instantiated')); "
                    "FundDocumentRepository.__init__ = fail_init; "
                    "FundDocumentRepository.load_annual_report = lambda *args, **kwargs: called.update(load=True); "
                    "import fund_agent.fund.evidence_confirm_sources; "
                    "print('import-ok', called['load'])"
            ),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert completed.stdout.strip() == "import-ok False"


class _PoisonRepository:
    """只允许 load_annual_report 的 fake repository。"""

    def __init__(self, report: ParsedAnnualReport) -> None:
        """记录返回报告。"""

        self._report = report
        self.calls: tuple[tuple[str, int, bool], ...] = ()

    async def load_annual_report(
        self,
        fund_code: str,
        report_year: int,
        *,
        force_refresh: bool = False,
    ) -> ParsedAnnualReport:
        """记录调用并返回 fake ParsedAnnualReport。"""

        self.calls = (*self.calls, (fund_code, report_year, force_refresh))
        return self._report

    def fetch_pdf(self, *args: object, **kwargs: object) -> None:
        """禁止 runner 触碰 PDF helper。"""

        raise AssertionError("fetch_pdf must not be called")

    def fetch_pdf_path(self, *args: object, **kwargs: object) -> None:
        """禁止 runner 触碰 PDF path helper。"""

        raise AssertionError("fetch_pdf_path must not be called")

    def parse_pdf(self, *args: object, **kwargs: object) -> None:
        """禁止 runner 触碰 parser helper。"""

        raise AssertionError("parse_pdf must not be called")


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


def _fee_schedule_projection_with_source_scope(
    *,
    row_locators: tuple[str, ...],
    evidence_anchor_ids: tuple[str, ...],
) -> tuple[object, object, object]:
    """构造 fee_schedule source_field_path scope projection。

    Args:
        row_locators: 待绑定到 anchors 的语义 locator。
        evidence_anchor_ids: 与 locator 一一对应的 anchor id。

    Returns:
        projection、chapter、fact 三元组。

    Raises:
        AssertionError: 当 locator 与 anchor id 数量不一致时抛出。
    """

    assert len(row_locators) == len(evidence_anchor_ids)
    base_projection = project_chapter_facts(_bundle(), chapter_ids=(2,))
    chapter = base_projection.chapters[0]
    template_fact = next(
        item for item in chapter.facts if item.source_field_id == "structured.fee_schedule"
    )
    anchors = tuple(
        ChapterEvidenceAnchor(
            anchor_id=anchor_id,
            source_kind="annual_report",
            document_year=2024,
            section_id="§8",
            page_number=3,
            table_id="page-3-table-0",
            row_locator=row_locator,
            note=None,
        )
        for anchor_id, row_locator in zip(evidence_anchor_ids, row_locators, strict=True)
    )
    fact = replace(
        template_fact,
        field_path="structured.fee_schedule",
        source_field_id="structured.fee_schedule",
        source_field_name="fee_schedule",
        value={"management_fee": "1.50%", "custody_fee": "0.25%"},
        evidence_anchor_ids=evidence_anchor_ids,
        missing_reason=None,
        missing_detail=None,
        status="available",
    )
    chapter = replace(chapter, facts=(fact,), evidence_anchors=anchors)
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


def _multi_section_report() -> ParsedAnnualReport:
    """构造含空 section 和非空 section 的 fake ParsedAnnualReport。

    Args:
        无。

    Returns:
        fake ParsedAnnualReport。

    Raises:
        无显式抛出。
    """

    raw_text = "目录\n   \n目标 section token 120%\n"
    first_start = len("目录\n")
    first_end = first_start + len("   \n")
    second_end = len(raw_text)
    return ParsedAnnualReport(
        key=DocumentKey(fund_code="110011", year=2024),
        raw_text=raw_text,
        sections={
            "§1": ReportSection(
                section_id="§1",
                title="§1 空章节",
                start_offset=first_start,
                end_offset=first_end,
                matched_rule="fixture",
                confidence=1.0,
            ),
            "§2": ReportSection(
                section_id="§2",
                title="§2 目标章节",
                start_offset=first_end,
                end_offset=second_end,
                matched_rule="fixture",
                confidence=1.0,
            ),
        },
        tables=(),
        metadata=_proven_metadata(),
    )


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
