"""候选年报表示 envelope 到内部模型的投影。

本模块只消费已经存在的 candidate representation JSON-like payload，不读取
PDF、不调用 Docling/pdfplumber、不访问 ``FundDocumentRepository``，也不改变
公共 ``EvidenceAnchor`` schema。
"""

from __future__ import annotations

import hashlib
from collections.abc import Mapping
from typing import Any

from fund_agent.fund.documents.candidates.representation_export import ENVELOPE_SCHEMA_VERSION
from fund_agent.fund.documents.candidates.representation_models import (
    CandidateAnchorNote,
    CandidateProjectionIssue,
    CandidateRepresentationDocument,
    CandidateRepresentationIdentity,
    CandidateRepresentationSourceKind,
    CandidateRepresentationStatus,
    CandidateSectionNode,
    CandidateSourceLocator,
    CandidateTableBlock,
    CandidateTableCell,
    CandidateTextBlock,
)

REQUIRED_BLOCKED_CLAIMS = frozenset(
    {
        "not_raw_xml_download_proof",
        "not_field_correctness_proof",
        "not_taxonomy_compatibility_proof",
        "not_source_truth",
        "not_readiness_proof",
        "no_repository_behavior_change",
        "no_parser_replacement",
    }
)


def project_candidate_representation(payload: Mapping[str, Any]) -> CandidateRepresentationDocument:
    """把候选表示 envelope 投影为 route-neutral 内部模型。

    Args:
        payload: candidate representation JSON-like payload。

    Returns:
        候选年报表示文档。

    Raises:
        ValueError: schema、source kind 或 non-proof 状态非法时抛出。
    """

    if payload.get("schema_version") != ENVELOPE_SCHEMA_VERSION:
        raise ValueError("unsupported candidate representation schema_version")
    source_kind = CandidateRepresentationSourceKind(str(payload["source_kind"]))
    blocked_claims = tuple(str(item) for item in payload.get("blocked_claims", ()))
    missing_blocked_claims = REQUIRED_BLOCKED_CLAIMS - set(blocked_claims)
    if missing_blocked_claims:
        raise ValueError(f"candidate payload is missing blocked claims: {sorted(missing_blocked_claims)}")
    status = CandidateRepresentationStatus(
        candidate_status=str(payload.get("candidate_status", "")),  # type: ignore[arg-type]
        field_correctness_status=str(payload.get("field_correctness_status", "")),  # type: ignore[arg-type]
        source_truth_status=str(payload.get("source_truth_status", "")),  # type: ignore[arg-type]
        taxonomy_compatibility_status=str(payload.get("taxonomy_compatibility_status", "")),  # type: ignore[arg-type]
        production_parser_replacement_status=str(  # type: ignore[arg-type]
            payload.get("production_parser_replacement_status", "")
        ),
    )
    identity = _project_identity(payload, source_kind)
    return CandidateRepresentationDocument(
        schema_version=str(payload["schema_version"]),
        identity=identity,
        status=status,
        summary_metrics=dict(_as_mapping(payload.get("summary_metrics"), "summary_metrics")),
        sections=_project_sections(payload, source_kind),
        text_blocks=_project_text_blocks(payload, source_kind),
        tables=_project_tables(payload, source_kind),
        route_failures=_project_route_failures(payload, source_kind),
        projection_issues=_projection_issues(payload, source_kind),
        blocked_claims=blocked_claims,
    )


def build_candidate_anchor_note(
    *,
    document: CandidateRepresentationDocument,
    table: CandidateTableBlock,
    cell: CandidateTableCell,
) -> CandidateAnchorNote:
    """从候选 table/cell 构造内部 anchor note。

    Args:
        document: 候选表示文档。
        table: 候选表格块。
        cell: 候选单元格。

    Returns:
        candidate-only anchor note。

    Raises:
        ValueError: locator hash 缺失时抛出。
    """

    if not cell.locator_hash:
        raise ValueError("candidate anchor note requires locator_hash")
    return CandidateAnchorNote(
        candidate_source_kind=document.identity.source_kind,
        artifact_hash=document.identity.accepted_input_sha256,
        source_locator=cell.source_locator,
        page_number_or_null=cell.source_locator.page_number,
        section_id_or_heading=table.section_id,
        table_id=table.table_id,
        row_locator=_row_locator(cell),
        row_label_path=cell.row_label_path,
        column_header_path=cell.column_header_path,
        cell_hash=cell.cell_hash,
        locator_hash=cell.locator_hash,
    )


def _project_identity(
    payload: Mapping[str, Any],
    source_kind: CandidateRepresentationSourceKind,
) -> CandidateRepresentationIdentity:
    """投影候选 identity。

    Args:
        payload: candidate envelope。
        source_kind: 已解析来源类型。

    Returns:
        候选 identity。

    Raises:
        ValueError: identity 字段非法时抛出。
    """

    input_artifact = _as_mapping(payload.get("input_artifact"), "input_artifact")
    return CandidateRepresentationIdentity(
        source_kind=source_kind,
        sample_id=str(payload["sample_id"]) if payload.get("sample_id") is not None else None,
        fund_code=str(payload["fund_code"]),
        document_year=int(payload["document_year"]),
        report_type=str(payload.get("report_type", "annual_report")),  # type: ignore[arg-type]
        input_artifact_path=(
            str(input_artifact["path"]) if input_artifact.get("path") is not None else None
        ),
        accepted_input_sha256=(
            str(input_artifact["accepted_sha256"])
            if input_artifact.get("accepted_sha256") is not None
            else None
        ),
        provenance_judgment_path=str(input_artifact.get("provenance_judgment_path", "")),
    )


def _project_sections(
    payload: Mapping[str, Any],
    source_kind: CandidateRepresentationSourceKind,
) -> tuple[CandidateSectionNode, ...]:
    """投影候选 section 列表。

    Args:
        payload: candidate envelope。
        source_kind: 来源类型。

    Returns:
        section tuple。

    Raises:
        无显式抛出。
    """

    sections: list[CandidateSectionNode] = []
    for index, raw_section in enumerate(_as_sequence(payload.get("sections"))):
        section = _as_mapping(raw_section, f"sections/{index}")
        heading_text = str(section.get("heading_text") or section.get("title") or "")
        page_number = _int_or_none(section.get("page_number") or section.get("page_start"))
        locator = CandidateSourceLocator(
            source_kind=source_kind,
            source_ref=str(section.get("source_ref") or section.get("heading_id") or section.get("section_id")),
            page_number=page_number,
            bbox=_bbox_or_none(section.get("bbox")),
            char_start=_int_or_none(section.get("start_offset")),
            char_end=_int_or_none(section.get("end_offset")),
        )
        sections.append(
            CandidateSectionNode(
                section_id=str(section.get("section_id") or f"section_{index}"),
                source_ref=locator.source_ref,
                heading_text=heading_text,
                heading_path=(heading_text,) if heading_text else (),
                heading_level=_int_or_none(section.get("heading_level")),
                page_start=page_number,
                page_end=_int_or_none(section.get("page_end")) or page_number,
                source_locator=locator,
                content_hash=str(section["content_hash"]) if section.get("content_hash") else None,
                excluded_reason=str(section["excluded_reason"]) if section.get("excluded_reason") else None,
            )
        )
    return tuple(sections)


def _project_text_blocks(
    payload: Mapping[str, Any],
    source_kind: CandidateRepresentationSourceKind,
) -> tuple[CandidateTextBlock, ...]:
    """投影候选 text blocks。

    Args:
        payload: candidate envelope。
        source_kind: 来源类型。

    Returns:
        text block tuple。

    Raises:
        无显式抛出。
    """

    raw_blocks = _as_sequence(payload.get("text_blocks")) or _as_sequence(payload.get("paragraphs"))
    blocks: list[CandidateTextBlock] = []
    for index, raw_block in enumerate(raw_blocks):
        block = _as_mapping(raw_block, f"text_blocks/{index}")
        text = str(block.get("text", ""))
        locator = CandidateSourceLocator(
            source_kind=source_kind,
            source_ref=str(block.get("block_id") or block.get("source_ref") or f"text_block_{index}"),
            page_number=_int_or_none(block.get("page_number")),
            bbox=_bbox_or_none(block.get("bbox")),
        )
        blocks.append(
            CandidateTextBlock(
                block_id=str(block.get("block_id") or f"text_block_{index}"),
                block_type=str(block.get("block_type") or block.get("label") or "paragraph"),
                section_id=str(block["section_id"]) if block.get("section_id") else None,
                heading_path=_string_tuple(block.get("heading_path")),
                text=text,
                normalized_text=str(block.get("normalized_text") or text),
                source_locator=locator,
                content_hash=str(block["content_hash"]) if block.get("content_hash") else None,
                excluded_reason=str(block["excluded_reason"]) if block.get("excluded_reason") else None,
            )
        )
    return tuple(blocks)


def _project_tables(
    payload: Mapping[str, Any],
    source_kind: CandidateRepresentationSourceKind,
) -> tuple[CandidateTableBlock, ...]:
    """投影候选 tables。

    Args:
        payload: candidate envelope。
        source_kind: 来源类型。

    Returns:
        table tuple。

    Raises:
        无显式抛出。
    """

    tables: list[CandidateTableBlock] = []
    for index, raw_table in enumerate(_as_sequence(payload.get("tables"))):
        table = _as_mapping(raw_table, f"tables/{index}")
        table_index = int(table.get("table_index", index) or index)
        page_number = _int_or_none(table.get("page_number"))
        locator = CandidateSourceLocator(
            source_kind=source_kind,
            source_ref=str(table.get("self_ref") or table.get("source_ref") or table.get("table_id")),
            page_number=page_number,
            bbox=_bbox_or_none(table.get("bbox")),
            table_index=table_index,
        )
        cells = _project_cells(table, source_kind, table_index=table_index)
        cell_count = int(table.get("cell_count", len(cells)) or 0)
        tables.append(
            CandidateTableBlock(
                table_id=str(table.get("table_id") or f"table_{index}"),
                source_ref=locator.source_ref,
                route_table_index=table_index,
                section_id=str(table["section_id"]) if table.get("section_id") else None,
                heading_path=_string_tuple(table.get("heading_path")),
                page_numbers=(page_number,) if page_number is not None else (),
                source_locator=locator,
                bbox_by_page=_bbox_by_page(table, page_number),
                caption=str(table["caption"]) if table.get("caption") else None,
                label=str(table["label"]) if table.get("label") else None,
                row_count=int(table.get("row_count", 0) or 0),
                column_count=int(table.get("column_count", 0) or 0),
                cell_count=cell_count,
                table_family=str(table.get("table_family") or "unknown"),
                locator_stability="usable" if cell_count > 0 else "blocked",
                excluded_reason=str(table["excluded_reason"]) if table.get("excluded_reason") else None,
                failure_code=str(table["failure_code"]) if table.get("failure_code") else None,
                cells=cells,
            )
        )
    return tuple(tables)


def _project_cells(
    table: Mapping[str, Any],
    source_kind: CandidateRepresentationSourceKind,
    *,
    table_index: int,
) -> tuple[CandidateTableCell, ...]:
    """投影候选 table cells。

    Args:
        table: table mapping。
        source_kind: 来源类型。
        table_index: 表格序号。

    Returns:
        cell tuple。

    Raises:
        无显式抛出。
    """

    cells: list[CandidateTableCell] = []
    raw_cells = _as_sequence(table.get("cells"))
    if not raw_cells:
        raw_cells = _cells_from_pdfplumber_rows(table)
    for index, raw_cell in enumerate(raw_cells):
        cell = _as_mapping(raw_cell, f"tables/{table_index}/cells/{index}")
        text = str(cell.get("text", ""))
        row_start = _int_or_none(_first_present(cell, "row_start", "row_index"))
        column_start = _int_or_none(_first_present(cell, "column_start", "column_index"))
        locator = CandidateSourceLocator(
            source_kind=source_kind,
            source_ref=str(table.get("self_ref") or table.get("table_id")),
            page_number=_int_or_none(table.get("page_number")),
            bbox=_bbox_or_none(cell.get("bbox")),
            table_index=table_index,
            row_index=row_start,
            column_index=column_start,
        )
        locator_hash = str(cell.get("locator_hash") or _hash_values(source_kind.value, table_index, index, text))
        cells.append(
            CandidateTableCell(
                cell_index=int(cell.get("cell_index", index) or index),
                row_start=row_start,
                row_end=_int_or_none(cell.get("row_end")),
                column_start=column_start,
                column_end=_int_or_none(cell.get("column_end")),
                row_span=_int_or_none(cell.get("row_span")),
                column_span=_int_or_none(cell.get("column_span")),
                row_header=bool(cell.get("row_header", False)),
                column_header=bool(cell.get("column_header", False)),
                row_label_path=_string_tuple(cell.get("row_label_path")),
                column_header_path=_string_tuple(cell.get("column_header_path")),
                text=text,
                normalized_text=str(cell.get("normalized_text") or text),
                source_locator=locator,
                cell_hash=str(cell.get("cell_hash") or cell.get("content_hash") or _hash_values(text)),
                locator_hash=locator_hash,
                stability="usable" if locator_hash else "blocked",
            )
        )
    return tuple(cells)


def _cells_from_pdfplumber_rows(table: Mapping[str, Any]) -> tuple[Mapping[str, Any], ...]:
    """把 pdfplumber rows/header 结构投影成候选 cell mapping。

    Args:
        table: pdfplumber 候选 table mapping。

    Returns:
        cell mapping tuple；无 rows 时为空。

    Raises:
        无显式抛出。
    """

    rows = _as_sequence(table.get("rows"))
    if not rows:
        return ()
    headers = tuple(str(header) for header in _as_sequence(table.get("headers")))
    cells: list[Mapping[str, Any]] = []
    for row_index, raw_row in enumerate(rows):
        row = _as_sequence(raw_row)
        for column_index, raw_value in enumerate(row):
            cells.append(
                {
                    "cell_index": len(cells),
                    "row_start": row_index,
                    "row_end": row_index + 1,
                    "column_start": column_index,
                    "column_end": column_index + 1,
                    "row_span": 1,
                    "column_span": 1,
                    "text": str(raw_value),
                    "column_header_path": (
                        (headers[column_index],)
                        if column_index < len(headers) and headers[column_index]
                        else ()
                    ),
                    "row_label_path": (str(row[0]),) if row and column_index != 0 else (),
                }
            )
    return tuple(cells)


def _project_route_failures(
    payload: Mapping[str, Any],
    source_kind: CandidateRepresentationSourceKind,
) -> tuple[CandidateProjectionIssue, ...]:
    """投影 route failure taxonomy。

    Args:
        payload: candidate envelope。
        source_kind: 来源类型。

    Returns:
        issue tuple。

    Raises:
        无显式抛出。
    """

    taxonomy = _as_mapping(payload.get("failure_taxonomy"), "failure_taxonomy")
    issues: list[CandidateProjectionIssue] = []
    for index, raw_failure in enumerate(_as_sequence(taxonomy.get("route_failures"))):
        failure = _as_mapping(raw_failure, f"route_failures/{index}")
        code = str(failure.get("failure_code") or "candidate_route_failure")
        issues.append(
            CandidateProjectionIssue(
                issue_id=f"route_failure:{index}:{code}",
                severity="blocking",
                source_kind=source_kind,
                location=f"/failure_taxonomy/route_failures/{index}",
                message=str(failure.get("reason") or code),
                failure_code=code,
            )
        )
    return tuple(issues)


def _projection_issues(
    payload: Mapping[str, Any],
    source_kind: CandidateRepresentationSourceKind,
) -> tuple[CandidateProjectionIssue, ...]:
    """生成投影级非阻断 issue。

    Args:
        payload: candidate envelope。
        source_kind: 来源类型。

    Returns:
        issue tuple。

    Raises:
        无显式抛出。
    """

    issues: list[CandidateProjectionIssue] = []
    if source_kind == CandidateRepresentationSourceKind.PDFPLUMBER_PDF:
        issues.append(
            CandidateProjectionIssue(
                issue_id="pdfplumber:bbox_not_available",
                severity="info",
                source_kind=source_kind,
                location="/tables",
                message="pdfplumber candidate projection may not expose bbox",
            )
        )
    if source_kind == CandidateRepresentationSourceKind.EID_HTML_RENDER and not payload.get("tables"):
        issues.append(
            CandidateProjectionIssue(
                issue_id="eid_html:blocked_or_no_tables",
                severity="info",
                source_kind=source_kind,
                location="/tables",
                message="EID HTML render route has no accepted table payload in this gate",
            )
        )
    return tuple(issues)


def _row_locator(cell: CandidateTableCell) -> str | None:
    """构造候选行 locator 文本。

    Args:
        cell: 候选单元格。

    Returns:
        行 locator；缺少行信息时返回 ``None``。

    Raises:
        无显式抛出。
    """

    if cell.row_label_path:
        return " > ".join(cell.row_label_path)
    if cell.row_start is not None:
        return f"row:{cell.row_start}"
    return None


def _bbox_by_page(table: Mapping[str, Any], page_number: int | None) -> tuple[dict[str, object], ...]:
    """构造表格 bbox_by_page。

    Args:
        table: table mapping。
        page_number: 页码。

    Returns:
        bbox_by_page tuple。

    Raises:
        无显式抛出。
    """

    bbox = _bbox_or_none(table.get("bbox"))
    if bbox is None or page_number is None:
        return ()
    return ({"page_no": page_number, "bbox": bbox},)


def _as_mapping(value: Any, field_name: str) -> Mapping[str, Any]:
    """校验值为 mapping。

    Args:
        value: 输入值。
        field_name: 字段名。

    Returns:
        mapping。

    Raises:
        ValueError: 值不是 mapping 时抛出。
    """

    if isinstance(value, Mapping):
        return value
    raise ValueError(f"{field_name} must be a mapping")


def _as_sequence(value: Any) -> tuple[Any, ...]:
    """把 list/tuple 转成 tuple。

    Args:
        value: 输入值。

    Returns:
        tuple；非序列时为空 tuple。

    Raises:
        无显式抛出。
    """

    if isinstance(value, (list, tuple)):
        return tuple(value)
    return ()


def _string_tuple(value: Any) -> tuple[str, ...]:
    """把输入值转换为字符串 tuple。

    Args:
        value: 输入值。

    Returns:
        字符串 tuple。

    Raises:
        无显式抛出。
    """

    if isinstance(value, (list, tuple)):
        return tuple(str(item) for item in value)
    if isinstance(value, str) and value:
        return (value,)
    return ()


def _bbox_or_none(value: Any) -> dict[str, float | str] | None:
    """校验 bbox mapping。

    Args:
        value: bbox 值。

    Returns:
        bbox dict 或 ``None``。

    Raises:
        无显式抛出。
    """

    if not isinstance(value, Mapping):
        return None
    return {
        str(key): raw_value
        for key, raw_value in value.items()
        if isinstance(raw_value, (float, int, str))
    }


def _int_or_none(value: Any) -> int | None:
    """把值转换为 int 或 None。

    Args:
        value: 输入值。

    Returns:
        int 或 ``None``。

    Raises:
        无显式抛出。
    """

    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    return None


def _first_present(mapping: Mapping[str, Any], *keys: str) -> Any:
    """返回 mapping 中第一个存在且非 None 的值。

    Args:
        mapping: 输入 mapping。
        *keys: 候选 key。

    Returns:
        第一个存在且非 ``None`` 的值；都不存在时返回 ``None``。

    Raises:
        无显式抛出。
    """

    for key in keys:
        if key in mapping and mapping[key] is not None:
            return mapping[key]
    return None


def _hash_values(*values: object) -> str:
    """计算稳定 hash。

    Args:
        *values: 参与 hash 的值。

    Returns:
        SHA-256 十六进制字符串。

    Raises:
        无显式抛出。
    """

    digest = hashlib.sha256()
    for value in values:
        digest.update(str(value).encode("utf-8"))
        digest.update(b"\0")
    return digest.hexdigest()
