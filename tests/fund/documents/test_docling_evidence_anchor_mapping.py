"""Docling 候选 EvidenceAnchor 映射测试。"""

from __future__ import annotations

from pathlib import Path

from fund_agent.fund.documents.candidates.evidence_anchor_mapping import (
    CandidateEvidenceAnchorMapping,
    map_candidate_document_anchor_candidates,
    map_candidate_locator_to_anchor_candidate,
)
from fund_agent.fund.documents.candidates.representation_export import (
    CandidateExportMode,
    CandidateRepresentationExportEntry,
    CandidateRepresentationRoute,
    build_representation_envelope,
)
from fund_agent.fund.documents.candidates.representation_projection import project_candidate_representation


def _entry(route: CandidateRepresentationRoute = CandidateRepresentationRoute.DOCLING_PDF) -> CandidateRepresentationExportEntry:
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
        provenance_judgment_path=Path("docs/reviews/docling-full-document-coverage-evidence-controller-judgment-20260616.md"),
        output_path=Path("reports/docling-candidate/004393_2025.json"),
    )


def _summary_metrics() -> dict[str, int | bool]:
    """返回完整 summary metrics。

    Args:
        无。

    Returns:
        summary metrics 字典。

    Raises:
        无显式抛出。
    """

    return {
        "page_count": 100,
        "section_count": 1,
        "heading_count": 1,
        "paragraph_count": 1,
        "table_count": 1,
        "table_cell_count": 1,
        "has_page_number": True,
        "has_bbox": True,
        "has_section_tree": True,
        "has_table_cell_locator": True,
        "has_content_hash": True,
        "has_url_or_source_locator": True,
    }


def _payload(
    *,
    sections: tuple[dict[str, object], ...] | None = None,
    text_blocks: tuple[dict[str, object], ...] | None = None,
    tables: tuple[dict[str, object], ...] | None = None,
    route: CandidateRepresentationRoute = CandidateRepresentationRoute.DOCLING_PDF,
) -> dict[str, object]:
    """构造 candidate representation payload。

    Args:
        sections: section payloads。
        text_blocks: text block payloads。
        tables: table payloads。
        route: 候选 route。

    Returns:
        candidate envelope。

    Raises:
        无显式抛出。
    """

    return build_representation_envelope(
        _entry(route),
        summary_metrics=_summary_metrics(),
        sections=sections if sections is not None else (_section(),),
        headings=(),
        paragraphs=(),
        text_blocks=text_blocks if text_blocks is not None else (_paragraph(),),
        tables=tables if tables is not None else (_table_with_cell(),),
    )


def _section(section_id: str = "sec_8", heading_text: str = "§8 投资组合报告", page_number: int = 60) -> dict[str, object]:
    """构造 section payload。

    Args:
        section_id: section id。
        heading_text: 标题文本。
        page_number: 页码。

    Returns:
        section 字典。

    Raises:
        无显式抛出。
    """

    return {
        "section_id": section_id,
        "source_ref": f"#/texts/{section_id}",
        "heading_text": heading_text,
        "page_number": page_number,
        "bbox": {"l": 1, "t": 2, "r": 3, "b": 4},
    }


def _paragraph(section_id: str = "sec_8", page_number: int = 61) -> dict[str, object]:
    """构造 paragraph payload。

    Args:
        section_id: section id。
        page_number: 页码。

    Returns:
        paragraph 字典。

    Raises:
        无显式抛出。
    """

    return {
        "block_id": "para_1",
        "block_type": "paragraph",
        "section_id": section_id,
        "heading_path": ["§8 投资组合报告"],
        "text": "报告期末股票投资组合文本。",
        "page_number": page_number,
        "bbox": {"l": 10, "t": 20, "r": 30, "b": 40},
    }


def _table_with_cell(
    *,
    table_id: str = "tbl_8_1",
    section_id: str = "sec_8",
    page_number: int = 62,
    cells: list[dict[str, object]] | None = None,
) -> dict[str, object]:
    """构造 table payload。

    Args:
        table_id: 表格 ID。
        section_id: section id。
        page_number: 页码。
        cells: cell payloads。

    Returns:
        table 字典。

    Raises:
        无显式抛出。
    """

    return {
        "table_id": table_id,
        "self_ref": table_id,
        "table_index": 0,
        "section_id": section_id,
        "heading_path": ["§8 投资组合报告"],
        "page_number": page_number,
        "bbox": {"l": 0, "t": 0, "r": 100, "b": 100},
        "row_count": 2,
        "column_count": 2,
        "cell_count": len(cells or [_cell()]),
        "cells": cells or [_cell()],
    }


def _cell(
    *,
    cell_index: int = 0,
    row_start: int | None = 1,
    column_start: int | None = 1,
    source_ref: str = "tbl_8_1",
    page_number: int = 62,
    bbox: dict[str, float | int] | None = None,
) -> dict[str, object]:
    """构造 cell payload。

    Args:
        cell_index: cell index。
        row_start: 起始行。
        column_start: 起始列。
        source_ref: source ref。
        page_number: 页码。
        bbox: bbox。

    Returns:
        cell 字典。

    Raises:
        无显式抛出。
    """

    payload: dict[str, object] = {
        "cell_index": cell_index,
        "row_end": 2,
        "column_end": 2,
        "row_span": 1,
        "column_span": 1,
        "row_header": False,
        "column_header": False,
        "row_label_path": ["股票A"],
        "column_header_path": ["占基金资产净值比例"],
        "text": "1.23%",
        "source_ref": source_ref,
        "bbox": bbox or {"l": 10, "t": 10, "r": 20, "b": 20},
        "cell_hash": f"cell_hash_{cell_index}",
        "locator_hash": f"locator_hash_{cell_index}",
    }
    if row_start is not None:
        payload["row_start"] = row_start
    if column_start is not None:
        payload["column_start"] = column_start
    payload["page_number"] = page_number
    return payload


def test_document_mapping_emits_candidate_wrappers_for_heading_paragraph_table_and_cell() -> None:
    """验证文档级映射输出 candidate wrapper 而非生产 EvidenceAnchor。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 映射结果不符合 candidate-only 边界时抛出。
    """

    document = project_candidate_representation(_payload())
    result = map_candidate_document_anchor_candidates(document, schema_family="S1_full")

    assert len(result.mapped) == 4
    assert result.blocked == ()
    assert all(isinstance(item, CandidateEvidenceAnchorMapping) for item in result.mapped)
    assert "EvidenceAnchor" not in {type(item).__name__ for item in result.mapped}
    assert {item.block_type for item in result.mapped} == {"heading", "paragraph", "table", "cell"}
    cell_mapping = next(item for item in result.mapped if item.block_type == "cell")
    assert cell_mapping.fields.source_kind == "annual_report"
    assert cell_mapping.fields.document_year == 2025
    assert cell_mapping.fields.section_id == "§8"
    assert cell_mapping.fields.table_id == "tbl_8_1"
    assert cell_mapping.fields.row_locator == (
        "cell:r1:c1:idx0;row_label=股票A;column_header=占基金资产净值比例"
    )
    assert cell_mapping.candidate_only is True
    assert cell_mapping.field_correctness_status == "not_proven"
    assert "candidate_only=true" in cell_mapping.fields.note


def test_s1_cell_can_resolve_parent_by_unique_bbox_containment_without_parent_argument() -> None:
    """验证 S1 cell 可通过唯一 bbox containment 定位父表。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: bbox 父表解析失败时抛出。
    """

    document = project_candidate_representation(_payload())
    cell = document.tables[0].cells[0]
    result = map_candidate_locator_to_anchor_candidate(document, cell, schema_family="S1_full")

    assert result.blocked == ()
    assert result.mapped[0].fields.table_id == "tbl_8_1"


def test_s1_cell_blocks_ambiguous_bbox_parent_resolution() -> None:
    """验证 S1 cell 在多表 bbox 同时包含时 fail-closed。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: ambiguous bbox 未阻断时抛出。
    """

    tables = (
        _table_with_cell(table_id="tbl_a", cells=[]),
        _table_with_cell(table_id="tbl_b", cells=[]),
    )
    payload = _payload(tables=tables)
    document = project_candidate_representation(payload)
    cell_document = project_candidate_representation(_payload())
    cell = cell_document.tables[0].cells[0]

    result = map_candidate_locator_to_anchor_candidate(document, cell, schema_family="S1_full")

    assert result.mapped == ()
    assert result.blocked[0].reason_code == "cannot_resolve_parent_table"


def test_s4_s5_s6_cell_blocks_missing_tuple_member() -> None:
    """验证 S4/S5/S6 缺 tuple 成员时阻断 cell 映射。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 缺失 tuple 字段未阻断时抛出。
    """

    table = _table_with_cell(cells=[_cell(row_start=None)])
    document = project_candidate_representation(_payload(tables=(table,)))

    result = map_candidate_document_anchor_candidates(document, schema_family="S4_S5_S6_lightweight")

    assert any(block.reason_code == "missing_cell_position" for block in result.blocked)
    assert not any(item.block_type == "cell" for item in result.mapped)


def test_s4_s5_s6_cell_happy_path_maps_with_exact_tuple() -> None:
    """验证 S4/S5/S6 完整 tuple 能映射 cell candidate。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 完整 tuple 未生成 cell candidate 时抛出。
    """

    document = project_candidate_representation(_payload())

    result = map_candidate_document_anchor_candidates(document, schema_family="S4_S5_S6_lightweight")

    cell_mapping = next(item for item in result.mapped if item.block_type == "cell")
    assert cell_mapping.fields.table_id == "tbl_8_1"
    assert cell_mapping.fields.page_number == 62
    assert cell_mapping.fields.row_locator == (
        "cell:r1:c1:idx0;row_label=股票A;column_header=占基金资产净值比例"
    )


def test_s4_s5_s6_cell_blocks_duplicate_tuple() -> None:
    """验证 S4/S5/S6 重复 tuple 时阻断 cell 映射。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 重复 tuple 未阻断时抛出。
    """

    table = _table_with_cell(
        cells=[
            _cell(cell_index=3, row_start=1, column_start=1),
            _cell(cell_index=3, row_start=1, column_start=1),
        ]
    )
    document = project_candidate_representation(_payload(tables=(table,)))

    result = map_candidate_document_anchor_candidates(document, schema_family="S4_S5_S6_lightweight")

    assert any(block.reason_code == "ambiguous_cell_tuple" for block in result.blocked)
    assert not any(item.block_type == "cell" for item in result.mapped)


def test_s4_s5_s6_maps_without_section_nodes_when_heading_path_is_one_to_one() -> None:
    """验证 S4/S5/S6 缺 section tree 但 heading path 一一映射时可映射。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 一一映射 heading path 未闭环时抛出。
    """

    payload = _payload(sections=())
    document = project_candidate_representation(payload)

    result = map_candidate_document_anchor_candidates(document, schema_family="S4_S5_S6_lightweight")

    assert any(item.block_type == "cell" and item.fields.section_id == "§8" for item in result.mapped)


def test_s4_s5_s6_blocks_without_section_nodes_when_heading_path_is_ambiguous() -> None:
    """验证 S4/S5/S6 缺 section tree 且 heading path 多匹配时阻断。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 多章节 heading path 未阻断时抛出。
    """

    table = {
        **_table_with_cell(),
        "heading_path": ["§8 投资组合报告", "§9 基金份额持有人信息"],
    }
    payload = _payload(sections=(), text_blocks=(), tables=(table,))
    document = project_candidate_representation(payload)

    result = map_candidate_document_anchor_candidates(document, schema_family="S4_S5_S6_lightweight")

    assert result.mapped == ()
    assert {block.reason_code for block in result.blocked} == {"unstable_section_context"}


def test_missing_section_context_blocks_mapping() -> None:
    """验证缺少章节上下文时不生成候选锚点。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 缺章节上下文仍生成锚点时抛出。
    """

    payload = _payload(
        sections=(),
        text_blocks=({**_paragraph(section_id="unknown"), "heading_path": []},),
        tables=(),
    )
    document = project_candidate_representation(payload)

    result = map_candidate_document_anchor_candidates(document, schema_family="S1_full")

    assert result.mapped == ()
    assert result.blocked[0].reason_code == "missing_section_context"


def test_unstable_section_context_blocks_mapping() -> None:
    """验证多章节 heading path 映射为 unstable_section_context。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 不稳定章节上下文未阻断时抛出。
    """

    payload = _payload(
        text_blocks=(
            {
                **_paragraph(),
                "heading_path": ["§8 投资组合报告", "§9 基金份额持有人信息"],
            },
        ),
        tables=(),
    )
    document = project_candidate_representation(payload)

    result = map_candidate_document_anchor_candidates(document, schema_family="S1_full")

    assert result.mapped[0].block_type == "heading"
    assert result.blocked[0].reason_code == "unstable_section_context"


def test_missing_page_blocks_mapping() -> None:
    """验证缺少页码时不生成候选锚点。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 缺页码仍生成锚点时抛出。
    """

    paragraph = _paragraph()
    paragraph.pop("page_number")
    payload = _payload(text_blocks=(paragraph,), tables=())
    document = project_candidate_representation(payload)

    result = map_candidate_document_anchor_candidates(document, schema_family="S1_full")

    assert any(block.reason_code == "missing_page_number" for block in result.blocked)


def test_non_docling_candidate_is_blocked() -> None:
    """验证非 Docling candidate 不进入本映射 helper。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 非 Docling route 未阻断时抛出。
    """

    document = project_candidate_representation(_payload(route=CandidateRepresentationRoute.PDFPLUMBER_PDF))

    result = map_candidate_document_anchor_candidates(document, schema_family="S1_full")

    assert result.mapped == ()
    assert result.blocked[0].reason_code == "unsupported_source_kind"
