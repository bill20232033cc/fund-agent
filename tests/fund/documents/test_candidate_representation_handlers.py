"""候选年报表示 route handlers 测试。"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from fund_agent.fund.documents import __all__ as documents_public_exports
from fund_agent.fund.documents.candidates.representation_export import (
    CandidateRepresentationExportEntry,
    CandidateRepresentationRoute,
    CandidateExportMode,
    compute_sha256,
)
from fund_agent.fund.documents.candidates.representation_handlers import (
    CandidateHandlerConfig,
    _default_docling_converter,
    build_docling_candidate_representation,
    build_eid_html_candidate_representation,
    build_pdfplumber_candidate_representation,
    built_in_route_handlers,
)


def _write_pdf(path: Path) -> str:
    """写入测试 PDF 字节并返回 SHA-256。

    Args:
        path: 输出路径。

    Returns:
        文件 SHA-256。

    Raises:
        无显式抛出。
    """

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"%PDF- fake candidate")
    return compute_sha256(path)


def _entry(tmp_path: Path, route: CandidateRepresentationRoute) -> CandidateRepresentationExportEntry:
    """构造测试用 handled entry。

    Args:
        tmp_path: pytest 临时目录。
        route: 候选路线。

    Returns:
        候选导出条目。

    Raises:
        无显式抛出。
    """

    input_path = Path("cache/eid-artifact-capture/sample/pdf/006597_2024.pdf")
    accepted_hash = _write_pdf(tmp_path / input_path)
    return CandidateRepresentationExportEntry(
        sample_id="S4",
        fund_code="006597",
        document_year=2024,
        route=route,
        mode=CandidateExportMode.HANDLED,
        input_artifact_path=input_path,
        accepted_input_sha256=accepted_hash,
        provenance_judgment_path=Path("docs/reviews/accepted.md"),
        output_path=Path(f"reports/representation-json/006597_2024_{route.value}.json"),
    )


def test_built_in_route_handlers_register_all_candidate_routes(tmp_path: Path) -> None:
    """验证内置 handler 覆盖三个候选 route。

    Args:
        tmp_path: pytest 临时目录。

    Returns:
        无返回值。

    Raises:
        AssertionError: route handler 缺失时抛出。
    """

    handlers = built_in_route_handlers(CandidateHandlerConfig(workspace_root=tmp_path))

    assert set(handlers) == {
        CandidateRepresentationRoute.DOCLING_PDF,
        CandidateRepresentationRoute.PDFPLUMBER_PDF,
        CandidateRepresentationRoute.EID_HTML_RENDER,
    }


def test_pdfplumber_handler_uses_injected_extractors_without_real_pdf_read(tmp_path: Path) -> None:
    """验证 pdfplumber handler 可通过 fake extractor 构造候选表示。

    Args:
        tmp_path: pytest 临时目录。

    Returns:
        无返回值。

    Raises:
        AssertionError: 输出不符合候选 envelope 时抛出。
    """

    entry = _entry(tmp_path, CandidateRepresentationRoute.PDFPLUMBER_PDF)
    calls: list[Path | str] = []

    def _fake_text(path: Path) -> str:
        """返回 fake 年报全文。

        Args:
            path: PDF 路径。

        Returns:
            fake 文本。

        Raises:
            无显式抛出。
        """

        calls.append(path)
        return "§1 产品概况\n第一段\n\n§2 收益归因\n第二段"

    def _fake_tables(path: Path) -> list[dict[str, object]]:
        """返回 fake 表格。

        Args:
            path: PDF 路径。

        Returns:
            fake 表格列表。

        Raises:
            无显式抛出。
        """

        calls.append(path)
        return [{"page_number": 2, "headers": ["项目", "数值"], "rows": [["A", "1"], ["B", "2"]]}]

    def _fake_sections(text: str) -> dict[str, tuple[int, int]]:
        """返回 fake 章节偏移。

        Args:
            text: fake 文本。

        Returns:
            section 偏移映射。

        Raises:
            无显式抛出。
        """

        calls.append(text)
        return {"§1": (0, 12), "§2": (14, len(text))}

    payload = build_pdfplumber_candidate_representation(
        entry,
        config=CandidateHandlerConfig(workspace_root=tmp_path),
        text_extractor=_fake_text,
        table_extractor=_fake_tables,
        section_locator=_fake_sections,
    )

    assert payload["source_kind"] == "pdfplumber_pdf_candidate"
    assert payload["candidate_status"] == "not_proven"
    assert payload["summary_metrics"]["section_count"] == 2
    assert payload["summary_metrics"]["table_count"] == 1
    assert payload["summary_metrics"]["table_cell_count"] == 4
    assert payload["tables"][0]["locator_strategy"] == "page_number+table_index+row_index+column_index"
    assert calls[0] == tmp_path / entry.input_artifact_path


def test_docling_handler_returns_blocked_when_local_artifacts_missing(tmp_path: Path) -> None:
    """验证缺少本地 Docling artifact 时返回 blocked JSON。

    Args:
        tmp_path: pytest 临时目录。

    Returns:
        无返回值。

    Raises:
        AssertionError: 未返回稳定 blocked failure 时抛出。
    """

    entry = _entry(tmp_path, CandidateRepresentationRoute.DOCLING_PDF)

    payload = build_docling_candidate_representation(
        entry,
        config=CandidateHandlerConfig(workspace_root=tmp_path),
    )

    assert payload["source_kind"] == "docling_pdf_candidate"
    assert payload["failure_taxonomy"]["route_failures"][0]["failure_code"] == "docling_local_artifacts_missing"
    assert "not_source_truth" in payload["blocked_claims"]


def test_docling_handler_uses_fake_converter_and_keeps_candidate_status(tmp_path: Path) -> None:
    """验证 Docling handler 可用 fake converter 生成候选表示。

    Args:
        tmp_path: pytest 临时目录。

    Returns:
        无返回值。

    Raises:
        AssertionError: 输出不符合候选 envelope 时抛出。
    """

    entry = _entry(tmp_path, CandidateRepresentationRoute.DOCLING_PDF)
    (tmp_path / "cache/docling-artifacts").mkdir(parents=True)

    class _FakeConverter:
        """测试用 fake Docling converter。"""

        def convert(self, _path: Path) -> dict[str, Any]:
            """返回 fake Docling exported dict。

            Args:
                _path: PDF 路径。

            Returns:
                fake exported dict。

            Raises:
                无显式抛出。
            """

            return {
                "pages": [{"page_no": 1}, {"page_no": 2}],
                "sections": [{"section_id": "sec1", "heading_text": "一、产品概况"}],
                "headings": [{"text": "一、产品概况"}],
                "paragraphs": [{"text": "基金概况文本", "bbox": [0, 0, 1, 1]}],
                "tables": [
                    {
                        "table_id": "tbl1",
                        "page_number": 2,
                        "row_count": 1,
                        "column_count": 2,
                        "cells": [
                            {"row_index": 0, "column_index": 0, "text": "项目", "bbox": [0, 0, 1, 1]},
                            {"row_index": 0, "column_index": 1, "text": "数值", "bbox": [0, 0, 1, 1]},
                        ],
                    }
                ],
            }

    payload = build_docling_candidate_representation(
        entry,
        config=CandidateHandlerConfig(workspace_root=tmp_path),
        converter_factory=lambda _config: _FakeConverter(),
    )

    assert payload["source_kind"] == "docling_pdf_candidate"
    assert payload["candidate_status"] == "not_proven"
    assert payload["summary_metrics"]["page_count"] == 2
    assert payload["summary_metrics"]["table_cell_count"] == 2
    assert payload["summary_metrics"]["has_bbox"] is True
    assert payload["tables"][0]["locator_strategy"] == "table_id+cell_index+row_index+column_index"


def test_docling_handler_maps_exported_text_labels_and_nested_table_cells(tmp_path: Path) -> None:
    """验证 Docling exported dict 的真实 text/table 结构被映射。

    Args:
        tmp_path: pytest 临时目录。

    Returns:
        无返回值。

    Raises:
        AssertionError: section/header 或 nested table cells 未被映射时抛出。
    """

    entry = _entry(tmp_path, CandidateRepresentationRoute.DOCLING_PDF)
    (tmp_path / "cache/docling-artifacts").mkdir(parents=True)

    class _ExportDictConverter:
        """测试用贴近 Docling export_to_dict 的 fake converter。"""

        def convert(self, _path: Path) -> dict[str, Any]:
            """返回 fake Docling export_to_dict shape。

            Args:
                _path: PDF 路径。

            Returns:
                fake exported dict。

            Raises:
                无显式抛出。
            """

            return {
                "pages": {"1": {"page_no": 1}},
                "texts": [
                    {
                        "self_ref": "#/texts/0",
                        "label": "section_header",
                        "text": "§2 基金简介",
                        "prov": [{"page_no": 5, "bbox": {"l": 1, "t": 2, "r": 3, "b": 4}}],
                    }
                ],
                "tables": [
                    {
                        "self_ref": "#/tables/0",
                        "label": "table",
                        "prov": [{"page_no": 5, "bbox": {"l": 0, "t": 0, "r": 10, "b": 10}}],
                        "data": {
                            "table_cells": [
                                {
                                    "start_row_offset_idx": 0,
                                    "end_row_offset_idx": 1,
                                    "start_col_offset_idx": 0,
                                    "end_col_offset_idx": 1,
                                    "row_span": 1,
                                    "col_span": 1,
                                    "text": "基金名称",
                                    "bbox": {"l": 1, "t": 1, "r": 2, "b": 2},
                                    "row_header": True,
                                },
                                {
                                    "start_row_offset_idx": 0,
                                    "end_row_offset_idx": 1,
                                    "start_col_offset_idx": 1,
                                    "end_col_offset_idx": 2,
                                    "row_span": 1,
                                    "col_span": 1,
                                    "text": "测试基金",
                                    "bbox": {"l": 2, "t": 1, "r": 3, "b": 2},
                                },
                            ]
                        },
                    }
                ],
            }

    payload = build_docling_candidate_representation(
        entry,
        config=CandidateHandlerConfig(workspace_root=tmp_path),
        converter_factory=lambda _config: _ExportDictConverter(),
    )

    assert payload["summary_metrics"]["section_count"] == 1
    assert payload["summary_metrics"]["heading_count"] == 1
    assert payload["summary_metrics"]["table_cell_count"] == 2
    assert payload["sections"][0]["heading_text"] == "§2 基金简介"
    assert payload["tables"][0]["page_number"] == 5
    assert payload["tables"][0]["row_count"] == 1
    assert payload["tables"][0]["column_count"] == 2
    assert payload["tables"][0]["cells"][0]["row_header"] is True


def test_docling_handler_maps_socket_error_to_blocked(tmp_path: Path) -> None:
    """验证 Docling socket 访问错误映射为 blocked failure。

    Args:
        tmp_path: pytest 临时目录。

    Returns:
        无返回值。

    Raises:
        AssertionError: socket 错误未映射为稳定 failure code 时抛出。
    """

    entry = _entry(tmp_path, CandidateRepresentationRoute.DOCLING_PDF)
    (tmp_path / "cache/docling-artifacts").mkdir(parents=True)

    class _NetworkConverter:
        """测试用会触发网络错误的 fake converter。"""

        def convert(self, _path: Path) -> dict[str, Any]:
            """模拟 socket 阻断。

            Args:
                _path: PDF 路径。

            Returns:
                不返回。

            Raises:
                OSError: 模拟 socket 阻断。
            """

            raise OSError("socket access blocked for candidate Docling conversion")

    payload = build_docling_candidate_representation(
        entry,
        config=CandidateHandlerConfig(workspace_root=tmp_path),
        converter_factory=lambda _config: _NetworkConverter(),
    )

    assert payload["failure_taxonomy"]["route_failures"][0]["failure_code"] == "docling_network_attempt_blocked"


def test_default_docling_converter_binds_configured_local_artifacts_path(tmp_path: Path) -> None:
    """验证默认 Docling converter 绑定本地 artifacts path。

    该测试只构造 converter 并检查 pipeline options，不运行真实 PDF 转换。

    Args:
        tmp_path: pytest 临时目录。

    Returns:
        无返回值。

    Raises:
        AssertionError: 默认 converter 未消费配置时抛出。
    """

    base_models = pytest.importorskip("docling.datamodel.base_models")
    InputFormat = base_models.InputFormat

    from fund_agent.config import paths

    artifacts_path = paths.DEFAULT_DOCLING_ARTIFACT_ROOT
    (tmp_path / artifacts_path).mkdir(parents=True)

    converter = _default_docling_converter(
        CandidateHandlerConfig(
            workspace_root=tmp_path,
            docling_artifacts_path=artifacts_path,
            docling_do_ocr=False,
            docling_do_table_structure=True,
        )
    )
    pdf_options = converter.format_to_options[InputFormat.PDF].pipeline_options

    assert pdf_options.artifacts_path == tmp_path / artifacts_path
    assert pdf_options.do_ocr is False
    assert pdf_options.do_table_structure is True


def test_eid_html_handler_remains_blocked_candidate(tmp_path: Path) -> None:
    """验证 EID HTML handler 当前只输出 blocked candidate。

    Args:
        tmp_path: pytest 临时目录。

    Returns:
        无返回值。

    Raises:
        AssertionError: EID HTML 被错误提升为可用表示时抛出。
    """

    entry = CandidateRepresentationExportEntry(
        sample_id="S4",
        fund_code="006597",
        document_year=2024,
        route=CandidateRepresentationRoute.EID_HTML_RENDER,
        mode=CandidateExportMode.BLOCKED,
        input_artifact_path=None,
        accepted_input_sha256=None,
        provenance_judgment_path=Path("docs/reviews/accepted.md"),
        output_path=Path("reports/representation-json/006597_2024_eid_html_render_blocked.json"),
    )

    payload = build_eid_html_candidate_representation(
        entry,
        config=CandidateHandlerConfig(workspace_root=tmp_path),
    )

    assert payload["source_kind"] == "eid_xbrl_html_render_candidate"
    assert payload["failure_taxonomy"]["route_failures"][0]["failure_code"] == (
        "eid_html_render_url_not_accepted_for_sample"
    )
    assert payload["source_truth_status"] == "not_proven"


def test_candidate_handlers_are_not_public_document_exports() -> None:
    """验证 route handler internals 未进入 documents 公共入口。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: candidate handler 被公共导出时抛出。
    """

    assert "CandidateHandlerConfig" not in documents_public_exports
    assert "build_docling_candidate_representation" not in documents_public_exports
