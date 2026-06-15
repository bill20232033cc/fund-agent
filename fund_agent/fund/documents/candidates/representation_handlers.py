"""候选年报表示内置 route handlers。

本模块只服务于 Fund documents candidate evidence gate。它把 Docling、
pdfplumber 与 EID HTML render 的候选表示构造成统一 envelope，不接入生产
``FundDocumentRepository``，不改变来源策略，也不向 Service/UI/Host/renderer/
quality gate 暴露候选实现。
"""

from __future__ import annotations

import hashlib
import os
import socket
from collections.abc import Callable, Mapping
from contextlib import contextmanager, nullcontext
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from fund_agent.fund.documents.candidates.representation_export import (
    CandidateRepresentationExportEntry,
    CandidateRepresentationRoute,
    RouteHandler,
    build_blocked_representation,
    build_representation_envelope,
)
from fund_agent.fund.pdf.parser import extract_tables, extract_text, locate_sections


@dataclass(frozen=True, slots=True)
class CandidateHandlerConfig:
    """候选 handler 配置。

    Args:
        workspace_root: 工作区根目录。
        docling_artifacts_path: 本地 Docling artifact 目录。
        docling_do_ocr: 是否启用 Docling OCR；当前默认关闭。
        docling_do_table_structure: 是否启用 Docling 表结构恢复。
        docling_socket_block: 是否在 Docling 转换期间阻断 socket。
        allow_overwrite: 是否允许输出覆盖；实际写入由 harness 处理。

    Returns:
        dataclass 实例。

    Raises:
        无显式抛出。
    """

    workspace_root: Path = Path(".")
    docling_artifacts_path: Path = Path("cache/docling-artifacts")
    docling_do_ocr: bool = False
    docling_do_table_structure: bool = True
    docling_socket_block: bool = True
    allow_overwrite: bool = False


ConverterFactory = Callable[[CandidateHandlerConfig], Any]
TextExtractor = Callable[[Path], str]
TableExtractor = Callable[[Path], list[dict[str, object]]]
SectionLocator = Callable[[str], dict[str, tuple[int, int]]]


def built_in_route_handlers(config: CandidateHandlerConfig) -> dict[CandidateRepresentationRoute, RouteHandler]:
    """构造内置候选 route handler 映射。

    Args:
        config: 候选 handler 配置。

    Returns:
        route 到 handler 的映射。

    Raises:
        无显式抛出。
    """

    return {
        CandidateRepresentationRoute.DOCLING_PDF: (
            lambda entry: build_docling_candidate_representation(entry, config=config)
        ),
        CandidateRepresentationRoute.PDFPLUMBER_PDF: (
            lambda entry: build_pdfplumber_candidate_representation(entry, config=config)
        ),
        CandidateRepresentationRoute.EID_HTML_RENDER: (
            lambda entry: build_eid_html_candidate_representation(entry, config=config)
        ),
    }


def build_pdfplumber_candidate_representation(
    entry: CandidateRepresentationExportEntry,
    *,
    config: CandidateHandlerConfig,
    text_extractor: TextExtractor = extract_text,
    table_extractor: TableExtractor = extract_tables,
    section_locator: SectionLocator = locate_sections,
) -> dict[str, Any]:
    """构造 pdfplumber 候选年报表示。

    Args:
        entry: 候选导出条目。
        config: 候选 handler 配置。
        text_extractor: 可注入全文提取函数，测试使用 fake。
        table_extractor: 可注入表格提取函数，测试使用 fake。
        section_locator: 可注入章节定位函数，测试使用 fake。

    Returns:
        候选表示 envelope。

    Raises:
        ValueError: 缺少 PDF 输入路径时抛出。
    """

    if entry.input_artifact_path is None:
        raise ValueError("pdfplumber candidate requires input_artifact_path")
    pdf_path = config.workspace_root / entry.input_artifact_path
    raw_text = text_extractor(pdf_path)
    raw_tables = table_extractor(pdf_path)
    raw_sections = section_locator(raw_text)
    sections = _pdfplumber_sections(raw_text, raw_sections)
    tables = _pdfplumber_tables(raw_tables)
    paragraphs = _paragraphs_from_text(raw_text)
    text_blocks = _text_blocks_from_sections(raw_text, raw_sections)
    return build_representation_envelope(
        entry,
        summary_metrics=_summary_metrics(
            page_count=_max_page_number(raw_tables),
            sections=sections,
            headings=sections,
            paragraphs=paragraphs,
            tables=tables,
            table_cell_count=sum(int(table["cell_count"]) for table in tables),
            has_page_number=True,
            has_bbox=False,
            has_section_tree=True,
            has_table_cell_locator=True,
            has_content_hash=True,
            has_url_or_source_locator=True,
        ),
        sections=sections,
        headings=_headings_from_sections(sections),
        paragraphs=paragraphs,
        tables=tables,
        text_blocks=text_blocks,
    )


def build_docling_candidate_representation(
    entry: CandidateRepresentationExportEntry,
    *,
    config: CandidateHandlerConfig,
    converter_factory: ConverterFactory | None = None,
) -> dict[str, Any]:
    """构造 Docling 候选年报表示。

    Args:
        entry: 候选导出条目。
        config: 候选 handler 配置。
        converter_factory: 可注入 converter factory，测试使用 fake。

    Returns:
        候选表示 envelope，或 blocked envelope。

    Raises:
        ValueError: 缺少 PDF 输入路径时抛出。
    """

    if entry.input_artifact_path is None:
        raise ValueError("docling candidate requires input_artifact_path")
    if not (config.workspace_root / config.docling_artifacts_path).exists():
        return build_blocked_representation(
            entry,
            failure_code="docling_local_artifacts_missing",
            reason="local Docling artifacts path is unavailable",
        )
    pdf_path = config.workspace_root / entry.input_artifact_path
    try:
        with _docling_environment(config):
            converter = (
                converter_factory(config)
                if converter_factory is not None
                else _default_docling_converter(config)
            )
            conversion_result = converter.convert(pdf_path)
    except OSError as exc:
        return build_blocked_representation(
            entry,
            failure_code="docling_network_attempt_blocked",
            reason=f"Docling conversion attempted blocked network access: {exc}",
        )
    except (ImportError, RuntimeError, AttributeError, ValueError) as exc:
        return build_blocked_representation(
            entry,
            failure_code="docling_model_artifact_unavailable",
            reason=f"Docling conversion unavailable in local artifact mode: {exc}",
        )
    document_payload = _docling_result_to_mapping(conversion_result)
    sections = _docling_sections(document_payload)
    headings = _docling_headings(document_payload, sections)
    paragraphs = _docling_paragraphs(document_payload)
    tables = _docling_tables(document_payload)
    text_blocks = _docling_text_blocks(document_payload, paragraphs)
    return build_representation_envelope(
        entry,
        summary_metrics=_summary_metrics(
            page_count=_docling_page_count(document_payload),
            sections=sections,
            headings=headings,
            paragraphs=paragraphs,
            tables=tables,
            table_cell_count=sum(int(table["cell_count"]) for table in tables),
            has_page_number=True,
            has_bbox=_docling_has_bbox(document_payload),
            has_section_tree=bool(sections),
            has_table_cell_locator=bool(tables),
            has_content_hash=True,
            has_url_or_source_locator=True,
        ),
        sections=sections,
        headings=headings,
        paragraphs=paragraphs,
        tables=tables,
        text_blocks=text_blocks,
    )


def build_eid_html_candidate_representation(
    entry: CandidateRepresentationExportEntry,
    *,
    config: CandidateHandlerConfig,
) -> dict[str, Any]:
    """构造 EID HTML render 候选 blocked 表示。

    Args:
        entry: 候选导出条目。
        config: 候选 handler 配置；当前不使用。

    Returns:
        blocked 候选表示 envelope。

    Raises:
        无显式抛出。
    """

    _ = config
    return build_blocked_representation(
        entry,
        failure_code="eid_html_render_url_not_accepted_for_sample",
        reason="EID HTML render artifact is not accepted for this sample in the current gate",
    )


def _summary_metrics(
    *,
    page_count: int,
    sections: list[dict[str, Any]],
    headings: list[dict[str, Any]],
    paragraphs: list[dict[str, Any]],
    tables: list[dict[str, Any]],
    table_cell_count: int,
    has_page_number: bool,
    has_bbox: bool,
    has_section_tree: bool,
    has_table_cell_locator: bool,
    has_content_hash: bool,
    has_url_or_source_locator: bool,
) -> dict[str, int | bool]:
    """构造候选路线比较用 summary metrics。

    Args:
        page_count: 页数。
        sections: section 列表。
        headings: heading 列表。
        paragraphs: paragraph 列表。
        tables: table 列表。
        table_cell_count: 表格 cell 数。
        has_page_number: 是否有页码。
        has_bbox: 是否有 bbox。
        has_section_tree: 是否有 section tree。
        has_table_cell_locator: 是否有 table cell locator。
        has_content_hash: 是否有内容 hash。
        has_url_or_source_locator: 是否有 URL 或 source locator。

    Returns:
        summary metrics 字典。

    Raises:
        无显式抛出。
    """

    return {
        "page_count": page_count,
        "section_count": len(sections),
        "heading_count": len(headings),
        "paragraph_count": len(paragraphs),
        "table_count": len(tables),
        "table_cell_count": table_cell_count,
        "has_page_number": has_page_number,
        "has_bbox": has_bbox,
        "has_section_tree": has_section_tree,
        "has_table_cell_locator": has_table_cell_locator,
        "has_content_hash": has_content_hash,
        "has_url_or_source_locator": has_url_or_source_locator,
    }


def _pdfplumber_sections(text: str, raw_sections: Mapping[str, tuple[int, int]]) -> list[dict[str, Any]]:
    """把 pdfplumber 章节偏移映射为候选 section。

    Args:
        text: 年报全文。
        raw_sections: section id 到字符偏移的映射。

    Returns:
        section 字典列表。

    Raises:
        无显式抛出。
    """

    sections: list[dict[str, Any]] = []
    for section_id, (start, end) in sorted(raw_sections.items(), key=lambda item: item[1][0]):
        excerpt = text[start:end].strip()
        title = excerpt.splitlines()[0].strip() if excerpt else section_id
        sections.append({
            "section_id": section_id,
            "heading_text": title,
            "start_offset": start,
            "end_offset": end,
            "content_hash": _hash_text(excerpt),
        })
    return sections


def _headings_from_sections(sections: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """从 section 列表派生 heading 列表。

    Args:
        sections: section 字典列表。

    Returns:
        heading 字典列表。

    Raises:
        无显式抛出。
    """

    return [
        {
            "heading_id": section["section_id"],
            "heading_text": section["heading_text"],
            "section_id": section["section_id"],
        }
        for section in sections
    ]


def _paragraphs_from_text(text: str) -> list[dict[str, Any]]:
    """从全文构造轻量 paragraph blocks。

    Args:
        text: 年报全文。

    Returns:
        paragraph 字典列表。

    Raises:
        无显式抛出。
    """

    blocks: list[dict[str, Any]] = []
    cursor = 0
    for index, paragraph in enumerate(part.strip() for part in text.split("\n\n") if part.strip()):
        start = text.find(paragraph, cursor)
        cursor = start + len(paragraph) if start >= 0 else cursor
        blocks.append({
            "paragraph_index": index,
            "text": paragraph,
            "content_hash": _hash_text(paragraph),
        })
    return blocks


def _text_blocks_from_sections(
    text: str,
    raw_sections: Mapping[str, tuple[int, int]],
) -> list[dict[str, Any]]:
    """从 section 偏移构造 text block。

    Args:
        text: 年报全文。
        raw_sections: section id 到字符偏移的映射。

    Returns:
        text block 字典列表。

    Raises:
        无显式抛出。
    """

    blocks: list[dict[str, Any]] = []
    for section_id, (start, end) in sorted(raw_sections.items(), key=lambda item: item[1][0]):
        content = text[start:end].strip()
        blocks.append({
            "block_id": section_id,
            "section_id": section_id,
            "text": content,
            "content_hash": _hash_text(content),
        })
    return blocks


def _pdfplumber_tables(raw_tables: list[dict[str, object]]) -> list[dict[str, Any]]:
    """把 pdfplumber 表格映射为候选 table。

    Args:
        raw_tables: ``extract_tables`` 返回的表格列表。

    Returns:
        table 字典列表。

    Raises:
        无显式抛出。
    """

    tables: list[dict[str, Any]] = []
    for table_index, table in enumerate(raw_tables):
        headers = [str(header) for header in table.get("headers", [])]
        rows = table.get("rows", [])
        row_count = len(rows) if isinstance(rows, list) else 0
        column_count = len(headers)
        tables.append({
            "table_id": f"pdfplumber_table_{table_index}",
            "page_number": table.get("page_number"),
            "table_index": table_index,
            "headers": headers,
            "row_count": row_count,
            "column_count": column_count,
            "cell_count": row_count * column_count,
            "locator_strategy": "page_number+table_index+row_index+column_index",
            "rows": rows if isinstance(rows, list) else [],
        })
    return tables


def _max_page_number(raw_tables: list[dict[str, object]]) -> int:
    """从表格元数据估算最大页码。

    Args:
        raw_tables: ``extract_tables`` 返回的表格列表。

    Returns:
        最大页码；没有页码时返回 0。

    Raises:
        无显式抛出。
    """

    page_numbers = [
        int(table["page_number"])
        for table in raw_tables
        if isinstance(table.get("page_number"), int)
    ]
    return max(page_numbers, default=0)


def _docling_result_to_mapping(result: Any) -> Mapping[str, Any]:
    """把 Docling conversion result 转成 mapping。

    Args:
        result: Docling conversion result 或 fake result。

    Returns:
        JSON-like mapping。

    Raises:
        ValueError: 无法转成 mapping 时抛出。
    """

    candidate = getattr(result, "document", result)
    if hasattr(candidate, "export_to_dict"):
        candidate = candidate.export_to_dict()
    if isinstance(candidate, Mapping):
        return candidate
    raise ValueError("Docling result cannot be exported to mapping")


def _docling_sections(payload: Mapping[str, Any]) -> list[dict[str, Any]]:
    """从 Docling payload 提取 section 候选。

    Args:
        payload: Docling exported dict。

    Returns:
        section 字典列表。

    Raises:
        无显式抛出。
    """

    raw_sections = payload.get("sections", ())
    sections: list[dict[str, Any]] = []
    if isinstance(raw_sections, list):
        for index, section in enumerate(raw_sections):
            if not isinstance(section, Mapping):
                continue
            text = str(section.get("heading_text") or section.get("title") or section.get("text") or "")
            sections.append({
                "section_id": str(section.get("section_id") or f"docling_section_{index}"),
                "heading_text": text,
                "content_hash": _hash_text(text),
            })
    return sections


def _docling_headings(payload: Mapping[str, Any], sections: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """从 Docling payload 提取 heading 候选。

    Args:
        payload: Docling exported dict。
        sections: 已提取 section 列表。

    Returns:
        heading 字典列表。

    Raises:
        无显式抛出。
    """

    raw_headings = payload.get("headings", ())
    if isinstance(raw_headings, list) and raw_headings:
        headings: list[dict[str, Any]] = []
        for index, heading in enumerate(raw_headings):
            if isinstance(heading, Mapping):
                text = str(heading.get("text") or heading.get("heading_text") or "")
            else:
                text = str(heading)
            headings.append({
                "heading_id": f"docling_heading_{index}",
                "heading_text": text,
                "content_hash": _hash_text(text),
            })
        return headings
    return _headings_from_sections(sections)


def _docling_paragraphs(payload: Mapping[str, Any]) -> list[dict[str, Any]]:
    """从 Docling payload 提取 paragraph 候选。

    Args:
        payload: Docling exported dict。

    Returns:
        paragraph 字典列表。

    Raises:
        无显式抛出。
    """

    raw_paragraphs = payload.get("paragraphs") or payload.get("texts") or ()
    paragraphs: list[dict[str, Any]] = []
    if isinstance(raw_paragraphs, list):
        for index, paragraph in enumerate(raw_paragraphs):
            text = str(paragraph.get("text", "")) if isinstance(paragraph, Mapping) else str(paragraph)
            paragraphs.append({
                "paragraph_index": index,
                "text": text,
                "content_hash": _hash_text(text),
            })
    return paragraphs


def _docling_tables(payload: Mapping[str, Any]) -> list[dict[str, Any]]:
    """从 Docling payload 提取 table 候选。

    Args:
        payload: Docling exported dict。

    Returns:
        table 字典列表。

    Raises:
        无显式抛出。
    """

    raw_tables = payload.get("tables", ())
    tables: list[dict[str, Any]] = []
    if not isinstance(raw_tables, list):
        return tables
    for index, table in enumerate(raw_tables):
        if not isinstance(table, Mapping):
            continue
        cells = table.get("cells", ())
        if not isinstance(cells, list):
            cells = table.get("table_cells", ())
        cell_count = len(cells) if isinstance(cells, list) else 0
        tables.append({
            "table_id": str(table.get("table_id") or f"docling_table_{index}"),
            "page_number": table.get("page_number"),
            "table_index": index,
            "caption": table.get("caption"),
            "row_count": int(table.get("row_count", 0) or 0),
            "column_count": int(table.get("column_count", 0) or 0),
            "cell_count": cell_count,
            "locator_strategy": "table_id+cell_index+row_index+column_index",
            "cells": cells if isinstance(cells, list) else [],
        })
    return tables


def _docling_text_blocks(
    payload: Mapping[str, Any],
    paragraphs: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """从 Docling payload 提取 text block 候选。

    Args:
        payload: Docling exported dict。
        paragraphs: 已提取 paragraph 列表。

    Returns:
        text block 字典列表。

    Raises:
        无显式抛出。
    """

    raw_blocks = payload.get("text_blocks", ())
    if isinstance(raw_blocks, list) and raw_blocks:
        return [dict(block) for block in raw_blocks if isinstance(block, Mapping)]
    return [
        {
            "block_id": f"docling_paragraph_{paragraph['paragraph_index']}",
            "text": paragraph["text"],
            "content_hash": paragraph["content_hash"],
        }
        for paragraph in paragraphs
    ]


def _docling_page_count(payload: Mapping[str, Any]) -> int:
    """从 Docling payload 读取页数。

    Args:
        payload: Docling exported dict。

    Returns:
        页数；无法识别时返回 0。

    Raises:
        无显式抛出。
    """

    pages = payload.get("pages")
    if isinstance(pages, list):
        return len(pages)
    if isinstance(pages, Mapping):
        return len(pages)
    page_count = payload.get("page_count")
    return int(page_count) if isinstance(page_count, int) else 0


def _docling_has_bbox(payload: Mapping[str, Any]) -> bool:
    """判断 Docling payload 是否包含 bbox。

    Args:
        payload: Docling exported dict。

    Returns:
        存在 bbox 时返回 ``True``。

    Raises:
        无显式抛出。
    """

    return "bbox" in str(payload)


def _hash_text(text: str) -> str:
    """计算文本 SHA-256。

    Args:
        text: 输入文本。

    Returns:
        SHA-256 十六进制字符串。

    Raises:
        无显式抛出。
    """

    return hashlib.sha256(text.encode("utf-8")).hexdigest()


@contextmanager
def _docling_environment(config: CandidateHandlerConfig) -> Any:
    """建立 Docling 本地 artifact / socket-block 运行环境。

    Args:
        config: 候选 handler 配置。

    Yields:
        无。

    Raises:
        OSError: socket-block 捕获到网络访问时抛出。
    """

    previous_hf_offline = os.environ.get("HF_HUB_OFFLINE")
    previous_transformers_offline = os.environ.get("TRANSFORMERS_OFFLINE")
    os.environ["HF_HUB_OFFLINE"] = "1"
    os.environ["TRANSFORMERS_OFFLINE"] = "1"
    socket_context = _block_socket() if config.docling_socket_block else nullcontext()
    try:
        with socket_context:
            yield
    finally:
        _restore_env("HF_HUB_OFFLINE", previous_hf_offline)
        _restore_env("TRANSFORMERS_OFFLINE", previous_transformers_offline)


@contextmanager
def _block_socket() -> Any:
    """临时阻断 socket 创建。

    Args:
        无。

    Yields:
        无。

    Raises:
        OSError: 任何 socket 创建都会抛出。
    """

    original_socket = socket.socket

    def _raise_blocked_socket(*_args: Any, **_kwargs: Any) -> socket.socket:
        """阻断 socket 创建。

        Args:
            *_args: 原始 socket 参数。
            **_kwargs: 原始 socket 参数。

        Returns:
            不返回。

        Raises:
            OSError: 始终抛出。
        """

        raise OSError("socket access blocked for candidate Docling conversion")

    socket.socket = _raise_blocked_socket  # type: ignore[assignment]
    try:
        yield
    finally:
        socket.socket = original_socket


def _restore_env(name: str, value: str | None) -> None:
    """恢复环境变量。

    Args:
        name: 环境变量名。
        value: 原始值；``None`` 表示原先不存在。

    Returns:
        无返回值。

    Raises:
        无显式抛出。
    """

    if value is None:
        os.environ.pop(name, None)
    else:
        os.environ[name] = value


def _default_docling_converter(config: CandidateHandlerConfig) -> Any:
    """构造默认 Docling converter。

    Args:
        config: 候选 handler 配置。

    Returns:
        Docling ``DocumentConverter`` 实例。

    Raises:
        ImportError: Docling 未安装时抛出。
        RuntimeError: 当前版本无法接受本地 artifact 配置时抛出。
    """

    from docling.datamodel.base_models import InputFormat
    from docling.datamodel.pipeline_options import PdfPipelineOptions
    from docling.document_converter import DocumentConverter, PdfFormatOption

    artifacts_path = config.workspace_root / config.docling_artifacts_path
    pipeline_options = PdfPipelineOptions(
        artifacts_path=artifacts_path,
        do_ocr=config.docling_do_ocr,
        do_table_structure=config.docling_do_table_structure,
    )
    return DocumentConverter(
        allowed_formats=[InputFormat.PDF],
        format_options={
            InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options),
        },
    )
