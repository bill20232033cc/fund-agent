"""Docling candidate 表格 locator helper。

本模块只基于 no-live excerpt 构建 candidate locator，不集成生产 extractor 或 renderer。
"""

from __future__ import annotations

import hashlib
import json
from collections import defaultdict
from typing import Any

from .models import (
    NORMALIZATION_RULE_NAMES,
    TABLE_LOCATOR_NORMALIZATION_RULE_NAMES,
    CandidateBlockReason,
    CandidateFailureCode,
    CandidatePageBBox,
    CandidateRawTableCell,
    CandidateTableBlock,
    CandidateTableCellLocator,
    CandidateTableFamily,
    CandidateTableGroup,
    NormalizationRuleName,
)
from .normalization import normalize_text


def build_table_block_from_excerpt(
    table_excerpt: dict[str, Any],
    *,
    section_id: str | None,
    heading_path: tuple[str, ...],
    table_family: CandidateTableFamily = "unknown",
) -> CandidateTableBlock:
    """从 excerpt table JSON 构建候选表格块。

    Args:
        table_excerpt: fixture 中的单个表格 excerpt。
        section_id: 候选章节编号。
        heading_path: 候选章节路径。
        table_family: 候选表格族。

    Returns:
        候选表格块。

    Raises:
        ValueError: table_cells 为空或缺少必要 provenance 时抛出。
    """

    raw_cells = _parse_raw_cells(table_excerpt.get("table_cells"))
    if not raw_cells:
        raise ValueError(CandidateFailureCode.TABLE_CELLS_MISSING.value)
    page_no = _extract_page_no(table_excerpt)
    source_table_index = int(table_excerpt["source_table_index"])
    table_id = f"docling:t{source_table_index}"
    grid = _expand_grid(raw_cells)
    header_rows = _header_rows(raw_cells)
    repeated_rows = _repeated_header_rows(raw_cells, header_rows)
    excluded_reason: CandidateBlockReason | None = (
        "toc" if table_excerpt.get("label") == "document_index" else None
    )
    normalized_cells = tuple(
        _build_cell_locator(
            raw_cell=cell,
            raw_cells=raw_cells,
            grid=grid,
            table_id=table_id,
            source_table_index=source_table_index,
            source_table_self_ref=str(table_excerpt.get("self_ref", "")),
            page_no=page_no,
        )
        for cell in raw_cells
        if cell.bbox is not None
    )
    body_rows = tuple(
        row
        for row in sorted({cell.start_row_offset_idx for cell in raw_cells})
        if row not in header_rows and row not in repeated_rows
    )
    return CandidateTableBlock(
        table_id=table_id,
        source_table_index=source_table_index,
        docling_self_ref=str(table_excerpt.get("self_ref", "")),
        section_id=section_id,
        heading_path=heading_path,
        page_numbers=(page_no,),
        bbox_by_page=_bbox_by_page(table_excerpt),
        num_rows=int(table_excerpt["num_rows"]),
        num_cols=int(table_excerpt["num_cols"]),
        normalized_cells=normalized_cells,
        header_rows=header_rows,
        body_rows=body_rows,
        table_family="document_index" if excluded_reason == "toc" else table_family,
        continuation_group_id=None,
        locator_stability="blocked" if excluded_reason == "toc" else "usable",
        failure_code=None,
        excluded_reason=excluded_reason,
    )


def build_candidate_anchor_note(locator: CandidateTableCellLocator) -> dict[str, object]:
    """构造 candidate-only EvidenceAnchor note。

    Args:
        locator: 已稳定的候选单元格 locator。

    Returns:
        可序列化到当前 ``EvidenceAnchor.note`` 的 candidate note 字典。

    Raises:
        ValueError: locator 缺少关键路径或 hash 时抛出。
    """

    if not locator.row_label_path or not locator.column_header_path:
        raise ValueError(CandidateFailureCode.CELL_LOCATOR_UNSTABLE.value)
    if not locator.cell_hash or not locator.locator_hash:
        raise ValueError(CandidateFailureCode.CELL_LOCATOR_UNSTABLE.value)
    return {
        "candidate_source_kind": "docling_pdf_candidate",
        "source_table_ref": locator.source_table_self_ref,
        "page_no": locator.page_no,
        "bbox": dict(locator.cell_bbox),
        "row_offsets": (locator.start_row_offset_idx, locator.end_row_offset_idx),
        "col_offsets": (locator.start_col_offset_idx, locator.end_col_offset_idx),
        "row_label_path": locator.row_label_path,
        "column_header_path": locator.column_header_path,
        "cell_text": locator.text_normalized,
        "cell_hash": locator.cell_hash,
        "locator_hash": locator.locator_hash,
        "normalization": locator.normalization_notes,
        "source_truth_status": "not_proven",
        "field_correctness_status": "not_proven",
    }


def stitch_candidate_tables(tables: tuple[CandidateTableBlock, ...]) -> CandidateTableGroup:
    """把候选表格按严格条件尝试 stitched group。

    Args:
        tables: 待 stitching 的候选表格块，至少两个。

    Returns:
        stitched group；失败时 ``stitched_table`` 为 ``None`` 并带 failure_code。

    Raises:
        ValueError: 少于两个表格时抛出。
    """

    if len(tables) < 2:
        raise ValueError("cross-page stitching 至少需要两个表格")
    first = tables[0]
    group_id = _stable_hash([table.table_id for table in tables])[:12]
    if len({table.section_id for table in tables}) != 1:
        return _failed_group(group_id, tables, CandidateFailureCode.TABLE_CONTINUATION_AMBIGUOUS)
    if len({table.table_family for table in tables}) != 1:
        return _failed_group(group_id, tables, CandidateFailureCode.TABLE_CONTINUATION_AMBIGUOUS)
    if len({table.num_cols for table in tables}) != 1:
        return _failed_group(group_id, tables, CandidateFailureCode.TABLE_SHAPE_INCONSISTENT)
    if not _header_signatures_compatible(tables):
        return _failed_group(group_id, tables, CandidateFailureCode.TABLE_HEADER_UNSTABLE)
    page_numbers = tuple(page for table in tables for page in table.page_numbers)
    if sorted(page_numbers) != list(page_numbers) or max(page_numbers) - min(page_numbers) > len(tables):
        return _failed_group(group_id, tables, CandidateFailureCode.TABLE_CONTINUATION_AMBIGUOUS)
    stitched_id = f"docling:t{first.source_table_index}:stitched:{group_id}"
    stitched_cells = tuple(cell for table in tables for cell in table.normalized_cells)
    stitched_table = CandidateTableBlock(
        table_id=stitched_id,
        source_table_index=first.source_table_index,
        docling_self_ref=first.docling_self_ref,
        section_id=first.section_id,
        heading_path=first.heading_path,
        page_numbers=page_numbers,
        bbox_by_page=tuple(bbox for table in tables for bbox in table.bbox_by_page),
        num_rows=sum(table.num_rows for table in tables),
        num_cols=first.num_cols,
        normalized_cells=stitched_cells,
        header_rows=first.header_rows,
        body_rows=tuple(row for table in tables for row in table.body_rows),
        table_family=first.table_family,
        continuation_group_id=group_id,
        locator_stability="usable",
        failure_code=None,
    )
    return CandidateTableGroup(
        group_id=group_id,
        source_table_ids=tuple(table.table_id for table in tables),
        page_numbers=page_numbers,
        table_family=first.table_family,
        stitched_table=stitched_table,
        failure_code=None,
        normalization_notes=("cross_page_table_stitching",),
    )


def implemented_locator_normalization_rules() -> tuple[NormalizationRuleName, ...]:
    """返回表格 locator helper 实现的规则名。

    Args:
        无。

    Returns:
        表格/locator 规则名闭集。

    Raises:
        无显式抛出。
    """

    return TABLE_LOCATOR_NORMALIZATION_RULE_NAMES


def implemented_normalization_rules() -> tuple[NormalizationRuleName, ...]:
    """返回本 gate 实现的完整归一化规则名闭集。

    Args:
        无。

    Returns:
        完整闭合规则名。

    Raises:
        无显式抛出。
    """

    return NORMALIZATION_RULE_NAMES


def _parse_raw_cells(raw_payload: Any) -> tuple[CandidateRawTableCell, ...]:
    """解析 fixture 中的 table_cells。

    Args:
        raw_payload: 原始 JSON 值。

    Returns:
        内部 raw cell 元组。

    Raises:
        ValueError: table_cells 不是非空列表时抛出。
    """

    if not isinstance(raw_payload, list) or not raw_payload:
        raise ValueError(CandidateFailureCode.TABLE_CELLS_MISSING.value)
    cells: list[CandidateRawTableCell] = []
    for payload in raw_payload:
        if not isinstance(payload, dict):
            raise ValueError(CandidateFailureCode.CANDIDATE_SCHEMA_VERSION_UNSUPPORTED.value)
        cells.append(
            CandidateRawTableCell(
                bbox=payload.get("bbox"),
                row_span=int(payload.get("row_span", 1)),
                col_span=int(payload.get("col_span", 1)),
                start_row_offset_idx=int(payload["start_row_offset_idx"]),
                end_row_offset_idx=int(payload["end_row_offset_idx"]),
                start_col_offset_idx=int(payload["start_col_offset_idx"]),
                end_col_offset_idx=int(payload["end_col_offset_idx"]),
                text=str(payload.get("text", "")),
                column_header=bool(payload.get("column_header", False)),
                row_header=bool(payload.get("row_header", False)),
                row_section=bool(payload.get("row_section", False)),
                fillable=bool(payload.get("fillable", False)),
            )
        )
    return tuple(cells)


def _extract_page_no(table_excerpt: dict[str, Any]) -> int:
    """从 table excerpt 中读取页码。

    Args:
        table_excerpt: 单个表格 excerpt。

    Returns:
        1-based 页码。

    Raises:
        ValueError: 缺少 provenance 页码时抛出。
    """

    prov = table_excerpt.get("prov")
    if not isinstance(prov, list) or not prov:
        raise ValueError(CandidateFailureCode.TABLE_PROVENANCE_MISSING.value)
    page_no = prov[0].get("page_no")
    if page_no is None:
        raise ValueError(CandidateFailureCode.PAGE_PROVENANCE_MISSING.value)
    return int(page_no)


def _bbox_by_page(table_excerpt: dict[str, Any]) -> tuple[CandidatePageBBox, ...]:
    """提取表格级 bbox provenance。

    Args:
        table_excerpt: 单个表格 excerpt。

    Returns:
        带页码的 bbox 元组。

    Raises:
        无显式抛出。
    """

    boxes = []
    for item in table_excerpt.get("prov", []):
        if "page_no" in item and "bbox" in item:
            boxes.append({"page_no": int(item["page_no"]), "bbox": item["bbox"]})
    return tuple(boxes)


def _expand_grid(
    raw_cells: tuple[CandidateRawTableCell, ...],
) -> dict[tuple[int, int], CandidateRawTableCell]:
    """按 row/col span 展开逻辑表格网格。

    Args:
        raw_cells: 原始 cell 元组。

    Returns:
        坐标到 source cell 的映射。

    Raises:
        ValueError: span 覆盖冲突时抛出。
    """

    grid: dict[tuple[int, int], CandidateRawTableCell] = {}
    for cell in raw_cells:
        for row in range(cell.start_row_offset_idx, cell.end_row_offset_idx):
            for col in range(cell.start_col_offset_idx, cell.end_col_offset_idx):
                key = (row, col)
                if key in grid:
                    raise ValueError(CandidateFailureCode.CELL_SPAN_CONFLICT.value)
                grid[key] = cell
    return grid


def _header_rows(raw_cells: tuple[CandidateRawTableCell, ...]) -> tuple[int, ...]:
    """识别 header rows。

    Args:
        raw_cells: 原始 cell 元组。

    Returns:
        header row index 元组。

    Raises:
        无显式抛出。
    """

    return tuple(
        sorted({cell.start_row_offset_idx for cell in raw_cells if cell.column_header})
    )


def _repeated_header_rows(
    raw_cells: tuple[CandidateRawTableCell, ...],
    header_rows: tuple[int, ...],
) -> tuple[int, ...]:
    """识别 body 中重复出现的 header rows。

    Args:
        raw_cells: 原始 cell 元组。
        header_rows: 已识别 header rows。

    Returns:
        重复 header row index 元组。

    Raises:
        无显式抛出。
    """

    if not header_rows:
        return ()
    row_texts = _row_texts(raw_cells)
    canonical = tuple(row_texts[row] for row in header_rows if row in row_texts)
    repeated: list[int] = []
    for row, values in row_texts.items():
        if row in header_rows:
            continue
        if values in canonical:
            repeated.append(row)
    return tuple(repeated)


def _build_cell_locator(
    *,
    raw_cell: CandidateRawTableCell,
    raw_cells: tuple[CandidateRawTableCell, ...],
    grid: dict[tuple[int, int], CandidateRawTableCell],
    table_id: str,
    source_table_index: int,
    source_table_self_ref: str,
    page_no: int,
) -> CandidateTableCellLocator:
    """构建单个 cell locator。

    Args:
        raw_cell: 当前 source cell。
        raw_cells: 表格内所有 source cells。
        grid: 已展开的逻辑网格。
        table_id: 候选表格 ID。
        source_table_index: Docling table index。
        source_table_self_ref: Docling self_ref。
        page_no: PDF 页码。

    Returns:
        候选单元格 locator。

    Raises:
        ValueError: bbox 缺失时抛出。
    """

    if raw_cell.bbox is None:
        raise ValueError(CandidateFailureCode.CELL_BBOX_MISSING.value)
    normalized = normalize_text(raw_cell.text)
    row_label_path = _row_label_path(raw_cell, grid)
    column_header_path = _column_header_path(raw_cell, raw_cells, grid)
    rules = list(normalized.rules_applied)
    if row_label_path:
        rules.append("row_label_path_generation")
        rules.extend(_row_path_normalization_rules(raw_cell, grid))
    if column_header_path:
        rules.append("column_header_path_generation")
    if raw_cell.row_span > 1 or raw_cell.col_span > 1 or _row_path_uses_merged_cell(raw_cell, grid):
        rules.append("merged_cell_expansion")
    cell_hash = _stable_hash(
        [
            normalized.normalized_text,
            row_label_path,
            column_header_path,
            raw_cell.start_row_offset_idx,
            raw_cell.start_col_offset_idx,
        ]
    )
    locator_hash = _stable_hash(
        [
            "docling_pdf_candidate",
            table_id,
            page_no,
            row_label_path,
            column_header_path,
            _bbox_bucket(raw_cell.bbox),
        ]
    )
    return CandidateTableCellLocator(
        table_id=table_id,
        source_table_index=source_table_index,
        source_table_self_ref=source_table_self_ref,
        page_no=page_no,
        cell_bbox=raw_cell.bbox,
        row_span=raw_cell.row_span,
        col_span=raw_cell.col_span,
        start_row_offset_idx=raw_cell.start_row_offset_idx,
        end_row_offset_idx=raw_cell.end_row_offset_idx,
        start_col_offset_idx=raw_cell.start_col_offset_idx,
        end_col_offset_idx=raw_cell.end_col_offset_idx,
        row_index_normalized=raw_cell.start_row_offset_idx,
        column_index_normalized=raw_cell.start_col_offset_idx,
        text_raw=raw_cell.text,
        text_normalized=normalized.normalized_text,
        column_header=raw_cell.column_header,
        row_header=raw_cell.row_header,
        row_section=raw_cell.row_section,
        row_label_path=row_label_path,
        column_header_path=column_header_path,
        cell_hash=cell_hash,
        locator_hash=locator_hash,
        normalization_notes=tuple(dict.fromkeys(rules)),
    )


def _row_label_path(
    raw_cell: CandidateRawTableCell,
    grid: dict[tuple[int, int], CandidateRawTableCell],
) -> tuple[str, ...]:
    """生成 row label path。

    Args:
        raw_cell: 当前 source cell。
        grid: 已展开的逻辑网格。

    Returns:
        row label path。

    Raises:
        无显式抛出。
    """

    if raw_cell.column_header:
        return ()
    labels: list[str] = []
    row = raw_cell.start_row_offset_idx
    for col in range(0, raw_cell.start_col_offset_idx):
        label_cell = grid.get((row, col))
        if label_cell is None or label_cell.column_header:
            continue
        normalized = normalize_text(label_cell.text)
        if normalized.normalized_text and normalized.normalized_text not in labels:
            labels.append(normalized.normalized_text)
    return tuple(labels)


def _row_path_uses_merged_cell(
    raw_cell: CandidateRawTableCell,
    grid: dict[tuple[int, int], CandidateRawTableCell],
) -> bool:
    """判断 row path 是否依赖 merged cell expansion。

    Args:
        raw_cell: 当前 source cell。
        grid: 已展开的逻辑网格。

    Returns:
        左侧 label path 使用跨行/跨列 cell 时返回 ``True``。

    Raises:
        无显式抛出。
    """

    row = raw_cell.start_row_offset_idx
    for col in range(0, raw_cell.start_col_offset_idx):
        label_cell = grid.get((row, col))
        if label_cell is not None and (label_cell.row_span > 1 or label_cell.col_span > 1):
            return True
    return False


def _row_path_normalization_rules(
    raw_cell: CandidateRawTableCell,
    grid: dict[tuple[int, int], CandidateRawTableCell],
) -> tuple[NormalizationRuleName, ...]:
    """收集 row path 来源 cell 的文本归一化规则。

    Args:
        raw_cell: 当前 source cell。
        grid: 已展开的逻辑网格。

    Returns:
        row path 来源 cell 的文本规则名。

    Raises:
        无显式抛出。
    """

    rules: list[NormalizationRuleName] = []
    row = raw_cell.start_row_offset_idx
    for col in range(0, raw_cell.start_col_offset_idx):
        label_cell = grid.get((row, col))
        if label_cell is None or label_cell.column_header:
            continue
        rules.extend(normalize_text(label_cell.text).rules_applied)
    return tuple(dict.fromkeys(rules))


def _column_header_path(
    raw_cell: CandidateRawTableCell,
    raw_cells: tuple[CandidateRawTableCell, ...],
    grid: dict[tuple[int, int], CandidateRawTableCell],
) -> tuple[str, ...]:
    """生成 column header path。

    Args:
        raw_cell: 当前 source cell。
        raw_cells: 表格内所有 source cells。
        grid: 已展开的逻辑网格。

    Returns:
        column header path。

    Raises:
        无显式抛出。
    """

    if raw_cell.column_header:
        return ()
    headers: list[str] = []
    col = raw_cell.start_col_offset_idx
    header_rows = _header_rows(raw_cells)
    for row in header_rows:
        header_cell = grid.get((row, col))
        if header_cell is None or not header_cell.column_header:
            continue
        normalized = normalize_text(header_cell.text)
        if normalized.normalized_text and normalized.normalized_text not in headers:
            headers.append(normalized.normalized_text)
    return tuple(headers)


def _row_texts(
    raw_cells: tuple[CandidateRawTableCell, ...],
) -> dict[int, tuple[str, ...]]:
    """按行聚合 normalized cell text。

    Args:
        raw_cells: 原始 cell 元组。

    Returns:
        row index 到 normalized text tuple 的映射。

    Raises:
        无显式抛出。
    """

    rows: dict[int, list[tuple[int, str]]] = defaultdict(list)
    for cell in raw_cells:
        rows[cell.start_row_offset_idx].append(
            (cell.start_col_offset_idx, normalize_text(cell.text).normalized_text)
        )
    return {
        row: tuple(value for _, value in sorted(values))
        for row, values in rows.items()
    }


def _header_signatures_compatible(tables: tuple[CandidateTableBlock, ...]) -> bool:
    """判断多个表格 header path 是否兼容。

    Args:
        tables: 候选表格块。

    Returns:
        header signature 兼容时返回 ``True``。

    Raises:
        无显式抛出。
    """

    signatures = []
    for table in tables:
        headers = sorted(
            {
                cell.text_normalized
                for cell in table.normalized_cells
                if cell.column_header
            }
        )
        signatures.append(tuple(headers))
    first = signatures[0]
    return all(signature == first for signature in signatures[1:])


def _failed_group(
    group_id: str,
    tables: tuple[CandidateTableBlock, ...],
    failure_code: CandidateFailureCode,
) -> CandidateTableGroup:
    """构造 stitching 失败结果。

    Args:
        group_id: stitching group ID。
        tables: 输入表格。
        failure_code: 失败代码。

    Returns:
        失败的 table group。

    Raises:
        无显式抛出。
    """

    return CandidateTableGroup(
        group_id=group_id,
        source_table_ids=tuple(table.table_id for table in tables),
        page_numbers=tuple(page for table in tables for page in table.page_numbers),
        table_family=tables[0].table_family,
        stitched_table=None,
        failure_code=failure_code,
        normalization_notes=(),
    )


def _bbox_bucket(bbox: dict[str, float | str]) -> tuple[float | str, ...]:
    """把 bbox 转成 hash 稳定 bucket。

    Args:
        bbox: bbox 字典。

    Returns:
        hash 用 tuple。

    Raises:
        无显式抛出。
    """

    return (
        round(float(bbox["l"]), 2),
        round(float(bbox["t"]), 2),
        round(float(bbox["r"]), 2),
        round(float(bbox["b"]), 2),
        str(bbox["coord_origin"]),
    )


def _stable_hash(parts: object) -> str:
    """计算 JSON 稳定 SHA256。

    Args:
        parts: 任意 JSON 兼容对象。

    Returns:
        SHA256 十六进制字符串。

    Raises:
        TypeError: 输入不能 JSON 序列化时由 ``json.dumps`` 抛出。
    """

    payload = json.dumps(parts, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()
