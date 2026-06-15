"""候选年报表示内部模型测试。"""

from __future__ import annotations

import pytest

from fund_agent.fund.documents.candidates.representation_models import (
    CandidateAnchorNote,
    CandidateRepresentationIdentity,
    CandidateRepresentationSourceKind,
    CandidateRepresentationStatus,
    CandidateSourceLocator,
)


def test_candidate_source_kind_values_are_closed() -> None:
    """验证候选来源类型闭集不包含 raw XBRL 或生产 parser。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 来源类型闭集发生非预期变化时抛出。
    """

    assert {item.value for item in CandidateRepresentationSourceKind} == {
        "docling_pdf_candidate",
        "pdfplumber_pdf_candidate",
        "eid_xbrl_html_render_candidate",
    }


def test_identity_rejects_non_annual_or_invalid_fund_code() -> None:
    """验证 identity 拒绝非年报和非法基金代码。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 非法 identity 未被拒绝时抛出。
    """

    with pytest.raises(ValueError, match="6-digit"):
        CandidateRepresentationIdentity(
            source_kind=CandidateRepresentationSourceKind.DOCLING_PDF,
            sample_id="S1",
            fund_code="4393",
            document_year=2025,
            report_type="annual_report",
            input_artifact_path="reports/representation-json/sample.json",
            accepted_input_sha256=None,
            provenance_judgment_path="docs/reviews/accepted.md",
        )
    with pytest.raises(ValueError, match="annual_report"):
        CandidateRepresentationIdentity(
            source_kind=CandidateRepresentationSourceKind.DOCLING_PDF,
            sample_id="S1",
            fund_code="004393",
            document_year=2025,
            report_type="quarterly_report",  # type: ignore[arg-type]
            input_artifact_path="reports/representation-json/sample.json",
            accepted_input_sha256=None,
            provenance_judgment_path="docs/reviews/accepted.md",
        )


def test_status_rejects_proof_or_parser_replacement_claims() -> None:
    """验证状态对象禁止字段正确性、source truth 和 parser replacement claim。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 越界状态未被拒绝时抛出。
    """

    with pytest.raises(ValueError, match="field_correctness"):
        CandidateRepresentationStatus(field_correctness_status="proven")  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="source_truth"):
        CandidateRepresentationStatus(source_truth_status="proven")  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="not_authorized"):
        CandidateRepresentationStatus(
            production_parser_replacement_status="authorized"  # type: ignore[arg-type]
        )


def test_candidate_anchor_note_rejects_truth_claims() -> None:
    """验证 candidate anchor note 仍保持 non-proof。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 越界 anchor note 未被拒绝时抛出。
    """

    locator = CandidateSourceLocator(
        source_kind=CandidateRepresentationSourceKind.DOCLING_PDF,
        source_ref="#/tables/0",
        page_number=5,
        bbox={"l": 1.0, "t": 2.0, "r": 3.0, "b": 4.0},
        table_index=0,
        row_index=1,
        column_index=2,
    )

    with pytest.raises(ValueError, match="field correctness"):
        CandidateAnchorNote(
            candidate_source_kind=CandidateRepresentationSourceKind.DOCLING_PDF,
            artifact_hash="abc",
            source_locator=locator,
            page_number_or_null=5,
            section_id_or_heading="sec",
            table_id="table",
            row_locator="row:1",
            row_label_path=(),
            column_header_path=("金额",),
            cell_hash="cell",
            locator_hash="locator",
            field_correctness_status="proven",  # type: ignore[arg-type]
        )
