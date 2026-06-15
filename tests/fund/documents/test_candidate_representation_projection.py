"""候选年报表示投影测试。"""

from __future__ import annotations

from pathlib import Path

import pytest

from fund_agent.fund.documents.candidates.representation_export import (
    CandidateExportMode,
    CandidateRepresentationExportEntry,
    CandidateRepresentationRoute,
    build_blocked_representation,
    build_representation_envelope,
)
from fund_agent.fund.documents.candidates.representation_models import (
    CandidateRepresentationSourceKind,
)
from fund_agent.fund.documents.candidates.representation_projection import (
    build_candidate_anchor_note,
    project_candidate_representation,
)


def _entry(route: CandidateRepresentationRoute) -> CandidateRepresentationExportEntry:
    """构造 synthetic candidate entry。

    Args:
        route: 候选 route。

    Returns:
        候选导出 entry。

    Raises:
        无显式抛出。
    """

    return CandidateRepresentationExportEntry(
        sample_id="S1",
        fund_code="004393",
        document_year=2025,
        route=route,
        mode=CandidateExportMode.HANDLED,
        input_artifact_path=Path("cache/eid-artifact-capture/sample/pdf/004393_2025.pdf"),
        accepted_input_sha256="abc123",
        provenance_judgment_path=Path("docs/reviews/accepted.md"),
        output_path=Path("reports/representation-json/004393_2025_candidate.json"),
    )


def _summary_metrics(*, table_cell_count: int, has_bbox: bool) -> dict[str, int | bool]:
    """返回完整 summary metrics。

    Args:
        table_cell_count: 表格 cell 数。
        has_bbox: 是否具备 bbox。

    Returns:
        summary metrics 字典。

    Raises:
        无显式抛出。
    """

    return {
        "page_count": 1,
        "section_count": 1,
        "heading_count": 1,
        "paragraph_count": 1,
        "table_count": 1,
        "table_cell_count": table_cell_count,
        "has_page_number": True,
        "has_bbox": has_bbox,
        "has_section_tree": True,
        "has_table_cell_locator": True,
        "has_content_hash": True,
        "has_url_or_source_locator": True,
    }


def test_project_docling_candidate_preserves_page_bbox_and_anchor_note() -> None:
    """验证 Docling candidate 投影保留页码、bbox 和候选 anchor note。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: route-specific locator 被弱化时抛出。
    """

    payload = build_representation_envelope(
        _entry(CandidateRepresentationRoute.DOCLING_PDF),
        summary_metrics=_summary_metrics(table_cell_count=1, has_bbox=True),
        sections=(
            {
                "section_id": "sec_1",
                "source_ref": "#/texts/0",
                "heading_text": "§2 基金简介",
                "page_number": 5,
                "bbox": {"l": 1, "t": 2, "r": 3, "b": 4},
                "content_hash": "section_hash",
            },
        ),
        headings=(),
        paragraphs=(),
        text_blocks=(
            {
                "block_id": "text_1",
                "block_type": "paragraph",
                "section_id": "sec_1",
                "heading_path": ["§2 基金简介"],
                "text": "基金简介文本",
                "page_number": 5,
                "bbox": {"l": 2, "t": 3, "r": 4, "b": 5},
                "content_hash": "text_hash",
            },
        ),
        tables=(
            {
                "table_id": "tbl_1",
                "self_ref": "#/tables/0",
                "table_index": 0,
                "section_id": "sec_1",
                "heading_path": ["§2 基金简介"],
                "page_number": 5,
                "bbox": {"l": 10, "t": 20, "r": 30, "b": 40},
                "row_count": 1,
                "column_count": 1,
                "cell_count": 1,
                "cells": [
                    {
                        "cell_index": 0,
                        "row_start": 0,
                        "row_end": 1,
                        "column_start": 0,
                        "column_end": 1,
                        "row_span": 1,
                        "column_span": 1,
                        "row_header": True,
                        "column_header": True,
                        "row_label_path": ["基金名称"],
                        "column_header_path": ["项目"],
                        "text": "安信企业价值优选混合A",
                        "bbox": {"l": 11, "t": 21, "r": 29, "b": 39},
                        "cell_hash": "cell_hash",
                        "locator_hash": "locator_hash",
                    }
                ],
            },
        ),
    )

    document = project_candidate_representation(payload)
    table = document.tables[0]
    cell = table.cells[0]
    note = build_candidate_anchor_note(document=document, table=table, cell=cell)

    assert document.identity.source_kind == CandidateRepresentationSourceKind.DOCLING_PDF
    assert document.status.source_truth_status == "not_proven"
    assert document.sections[0].source_locator.bbox == {"l": 1, "t": 2, "r": 3, "b": 4}
    assert cell.row_start == 0
    assert cell.column_start == 0
    assert cell.row_header is True
    assert cell.column_header is True
    assert cell.source_locator.page_number == 5
    assert cell.source_locator.bbox == {"l": 11, "t": 21, "r": 29, "b": 39}
    assert note.field_correctness_status == "not_proven"
    assert note.locator_hash == "locator_hash"


def test_project_pdfplumber_candidate_synthesizes_cells_from_rows_without_bbox() -> None:
    """验证 pdfplumber rows/header 结构会合成 cell locator 且不伪造 bbox。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: rows 未被正确投影时抛出。
    """

    payload = build_representation_envelope(
        _entry(CandidateRepresentationRoute.PDFPLUMBER_PDF),
        summary_metrics=_summary_metrics(table_cell_count=4, has_bbox=False),
        sections=(
            {
                "section_id": "sec_1",
                "heading_text": "§1 产品概况",
                "page_number": 2,
            },
        ),
        headings=(),
        paragraphs=(),
        text_blocks=(),
        tables=(
            {
                "table_id": "tbl_pdf_1",
                "table_index": 0,
                "page_number": 2,
                "headers": ["项目", "数值"],
                "rows": [["净值增长率", "1.23%"], ["业绩比较基准", "0.98%"]],
                "row_count": 2,
                "column_count": 2,
            },
        ),
    )

    document = project_candidate_representation(payload)
    table = document.tables[0]

    assert document.identity.source_kind == CandidateRepresentationSourceKind.PDFPLUMBER_PDF
    assert len(table.cells) == 4
    assert table.cells[1].text == "1.23%"
    assert table.cells[1].row_start == 0
    assert table.cells[1].column_start == 1
    assert table.cells[1].row_header is False
    assert table.cells[1].column_header is False
    assert table.cells[1].column_header_path == ("数值",)
    assert table.cells[1].row_label_path == ("净值增长率",)
    assert table.cells[1].source_locator.bbox is None
    assert table.cells[1].source_locator.page_number == 2


def test_project_eid_html_blocked_keeps_route_failure_without_tables() -> None:
    """验证 EID HTML blocked candidate 只保留 route failure。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: blocked route 被错误提升为表格表示时抛出。
    """

    entry = _entry(CandidateRepresentationRoute.EID_HTML_RENDER)
    blocked_entry = CandidateRepresentationExportEntry(
        sample_id=entry.sample_id,
        fund_code=entry.fund_code,
        document_year=entry.document_year,
        route=entry.route,
        mode=CandidateExportMode.BLOCKED,
        input_artifact_path=None,
        accepted_input_sha256=None,
        provenance_judgment_path=entry.provenance_judgment_path,
        output_path=entry.output_path,
    )
    payload = build_blocked_representation(
        blocked_entry,
        failure_code="eid_html_render_url_not_accepted_for_sample",
        reason="no accepted EID HTML render artifact for this sample",
    )

    document = project_candidate_representation(payload)

    assert document.identity.source_kind == CandidateRepresentationSourceKind.EID_HTML_RENDER
    assert document.tables == ()
    assert document.route_failures[0].failure_code == "eid_html_render_url_not_accepted_for_sample"
    assert document.projection_issues[0].issue_id == "eid_html:blocked_or_no_tables"


def test_projection_rejects_truth_and_parser_replacement_claims() -> None:
    """验证 projection 拒绝 truth、field correctness 和 parser replacement 越界状态。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 越界状态未被拒绝时抛出。
    """

    payload = build_representation_envelope(
        _entry(CandidateRepresentationRoute.DOCLING_PDF),
        summary_metrics=_summary_metrics(table_cell_count=0, has_bbox=False),
        sections=(),
        headings=(),
        paragraphs=(),
        tables=(),
        text_blocks=(),
    )
    payload["source_truth_status"] = "proven"

    with pytest.raises(ValueError, match="source_truth"):
        project_candidate_representation(payload)

    payload["source_truth_status"] = "not_proven"
    payload["production_parser_replacement_status"] = "authorized"
    with pytest.raises(ValueError, match="not_authorized"):
        project_candidate_representation(payload)


def test_projection_rejects_missing_blocked_claim_guards() -> None:
    """验证 projection 拒绝缺少 candidate-only blocked claims 的 payload。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 缺少 guard 未被拒绝时抛出。
    """

    payload = build_representation_envelope(
        _entry(CandidateRepresentationRoute.DOCLING_PDF),
        summary_metrics=_summary_metrics(table_cell_count=0, has_bbox=False),
        sections=(),
        headings=(),
        paragraphs=(),
        tables=(),
        text_blocks=(),
    )
    payload["blocked_claims"] = ["not_source_truth"]

    with pytest.raises(ValueError, match="blocked claims"):
        project_candidate_representation(payload)
