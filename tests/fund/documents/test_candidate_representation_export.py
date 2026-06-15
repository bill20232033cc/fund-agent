"""候选年报表示导出 harness 测试。"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from fund_agent.fund.documents import __all__ as documents_public_exports
from fund_agent.fund.documents.candidates.representation_export import (
    CandidateRepresentationExportEntry,
    CandidateRepresentationExportManifest,
    CandidateRepresentationRoute,
    CandidateExportMode,
    build_representation_envelope,
    compute_sha256,
    export_manifest,
    parse_manifest,
    validate_entry,
)


def _write_file(path: Path, content: bytes) -> str:
    """写入测试文件并返回 SHA-256。

    Args:
        path: 输出路径。
        content: 文件内容。

    Returns:
        文件 SHA-256。

    Raises:
        无显式抛出。
    """

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)
    return compute_sha256(path)


def _entry(tmp_path: Path, *, mode: CandidateExportMode) -> CandidateRepresentationExportEntry:
    """构造测试用导出条目。

    Args:
        tmp_path: pytest 临时目录。
        mode: 导出模式。

    Returns:
        候选导出条目。

    Raises:
        无显式抛出。
    """

    input_path = Path("cache/eid-artifact-capture/sample/pdf/006597_2024.pdf")
    accepted_hash = _write_file(tmp_path / input_path, b"%PDF- test")
    return CandidateRepresentationExportEntry(
        sample_id="S4",
        fund_code="006597",
        document_year=2024,
        route=CandidateRepresentationRoute.DOCLING_PDF,
        mode=mode,
        input_artifact_path=input_path,
        accepted_input_sha256=accepted_hash,
        provenance_judgment_path=Path("docs/reviews/accepted.md"),
        output_path=Path("reports/representation-json/006597_2024_docling_full.json"),
    )


def _summary_metrics() -> dict[str, int | bool]:
    """返回测试用完整 summary metrics。

    Args:
        无。

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
        "table_cell_count": 1,
        "has_page_number": True,
        "has_bbox": True,
        "has_section_tree": True,
        "has_table_cell_locator": True,
        "has_content_hash": True,
        "has_url_or_source_locator": True,
    }


def test_parse_manifest_and_validate_hash(tmp_path: Path) -> None:
    """验证 manifest 解析和输入 hash 校验。

    Args:
        tmp_path: pytest 临时目录。

    Returns:
        无返回值。

    Raises:
        AssertionError: manifest 解析或校验不符合预期时抛出。
    """

    entry = _entry(tmp_path, mode=CandidateExportMode.BLOCKED)
    payload = {
        "schema_version": "candidate_representation_export_manifest.v1",
        "entries": [
            {
                "sample_id": entry.sample_id,
                "fund_code": entry.fund_code,
                "document_year": entry.document_year,
                "route": entry.route.value,
                "mode": entry.mode.value,
                "input_artifact_path": str(entry.input_artifact_path),
                "accepted_input_sha256": entry.accepted_input_sha256,
                "provenance_judgment_path": str(entry.provenance_judgment_path),
                "output_path": str(entry.output_path),
            }
        ],
    }

    manifest = parse_manifest(payload)

    assert manifest.entries == (entry,)
    validate_entry(manifest.entries[0], workspace_root=tmp_path)


def test_validate_entry_rejects_production_cache_path(tmp_path: Path) -> None:
    """验证 harness 拒绝生产-shaped cache/pdf 输入路径。

    Args:
        tmp_path: pytest 临时目录。

    Returns:
        无返回值。

    Raises:
        AssertionError: 未拒绝生产 cache 路径时抛出。
    """

    entry = CandidateRepresentationExportEntry(
        sample_id="S4",
        fund_code="006597",
        document_year=2024,
        route=CandidateRepresentationRoute.PDFPLUMBER_PDF,
        mode=CandidateExportMode.BLOCKED,
        input_artifact_path=Path("cache/pdf/006597_2024_annual_report_eid.pdf"),
        accepted_input_sha256=None,
        provenance_judgment_path=Path("docs/reviews/accepted.md"),
        output_path=Path("reports/representation-json/006597_2024_pdfplumber_full.json"),
    )

    with pytest.raises(ValueError, match="cache/pdf"):
        validate_entry(entry, workspace_root=tmp_path)


def test_validate_entry_accepts_reference_existing_json(tmp_path: Path) -> None:
    """验证 S1 既有 representation JSON 可作为只校验 reference。

    Args:
        tmp_path: pytest 临时目录。

    Returns:
        无返回值。

    Raises:
        AssertionError: reference JSON 被错误拒绝时抛出。
    """

    input_path = Path("reports/representation-json/004393_2025_docling_full.json")
    entry = CandidateRepresentationExportEntry(
        sample_id="S1",
        fund_code="004393",
        document_year=2025,
        route=CandidateRepresentationRoute.DOCLING_PDF,
        mode=CandidateExportMode.REFERENCE_EXISTING_JSON,
        input_artifact_path=input_path,
        accepted_input_sha256=None,
        provenance_judgment_path=Path("docs/reviews/accepted.md"),
        output_path=input_path,
    )

    _write_file(tmp_path / input_path, b"{\"schema_version\":\"test\"}\n")
    validate_entry(entry, workspace_root=tmp_path)


def test_validate_entry_rejects_output_path_traversal(tmp_path: Path) -> None:
    """验证输出路径不能用 parent traversal 逃逸允许目录。

    Args:
        tmp_path: pytest 临时目录。

    Returns:
        无返回值。

    Raises:
        AssertionError: 未拒绝 traversal 输出路径时抛出。
    """

    entry = _entry(tmp_path, mode=CandidateExportMode.BLOCKED)
    escaped = CandidateRepresentationExportEntry(
        sample_id=entry.sample_id,
        fund_code=entry.fund_code,
        document_year=entry.document_year,
        route=entry.route,
        mode=entry.mode,
        input_artifact_path=entry.input_artifact_path,
        accepted_input_sha256=entry.accepted_input_sha256,
        provenance_judgment_path=entry.provenance_judgment_path,
        output_path=Path("reports/representation-json/../../cache/pdf/out.json"),
    )

    with pytest.raises(ValueError, match="parent traversal"):
        validate_entry(escaped, workspace_root=tmp_path)


def test_validate_entry_rejects_input_path_traversal_to_cache_pdf(tmp_path: Path) -> None:
    """验证输入路径不能用 parent traversal 绕过 cache/pdf 拒绝。

    Args:
        tmp_path: pytest 临时目录。

    Returns:
        无返回值。

    Raises:
        AssertionError: 未拒绝 traversal 输入路径时抛出。
    """

    entry = CandidateRepresentationExportEntry(
        sample_id="S4",
        fund_code="006597",
        document_year=2024,
        route=CandidateRepresentationRoute.PDFPLUMBER_PDF,
        mode=CandidateExportMode.BLOCKED,
        input_artifact_path=Path("cache/eid-artifact-capture/../../pdf/foo.pdf"),
        accepted_input_sha256=None,
        provenance_judgment_path=Path("docs/reviews/accepted.md"),
        output_path=Path("reports/representation-json/006597_2024_pdfplumber_full.json"),
    )

    with pytest.raises(ValueError, match="parent traversal"):
        validate_entry(entry, workspace_root=tmp_path)


def test_export_manifest_writes_blocked_candidate_json(tmp_path: Path) -> None:
    """验证 blocked 模式写出 non-proof JSON。

    Args:
        tmp_path: pytest 临时目录。

    Returns:
        无返回值。

    Raises:
        AssertionError: 输出 JSON 不符合 candidate-only 约束时抛出。
    """

    entry = CandidateRepresentationExportEntry(
        sample_id="S5",
        fund_code="017641",
        document_year=2024,
        route=CandidateRepresentationRoute.EID_HTML_RENDER,
        mode=CandidateExportMode.BLOCKED,
        input_artifact_path=None,
        accepted_input_sha256=None,
        provenance_judgment_path=Path("docs/reviews/accepted.md"),
        output_path=Path("reports/representation-json/017641_2024_eid_html_render_blocked.json"),
    )
    manifest = CandidateRepresentationExportManifest(entries=(entry,))

    written = export_manifest(manifest, workspace_root=tmp_path)

    assert written == (entry.output_path,)
    payload = json.loads((tmp_path / entry.output_path).read_text(encoding="utf-8"))
    assert payload["candidate_status"] == "not_proven"
    assert payload["source_truth_status"] == "not_proven"
    assert payload["production_parser_replacement_status"] == "not_authorized"
    assert "not_field_correctness_proof" in payload["blocked_claims"]
    assert payload["failure_taxonomy"]["route_failures"][0]["failure_code"] == (
        "eid_xbrl_html_render_candidate_not_available"
    )


def test_export_manifest_accepts_fake_handler_but_rejects_truth_claim(tmp_path: Path) -> None:
    """验证 fake handler 可写候选 JSON，但 truth claim 会被拒绝。

    Args:
        tmp_path: pytest 临时目录。

    Returns:
        无返回值。

    Raises:
        AssertionError: handler 输出校验不符合预期时抛出。
    """

    entry = _entry(tmp_path, mode=CandidateExportMode.HANDLED)
    manifest = CandidateRepresentationExportManifest(entries=(entry,))

    def _handler(route_entry: CandidateRepresentationExportEntry) -> dict[str, object]:
        """构造带非法 truth claim 的 fake handler 输出。

        Args:
            route_entry: 导出条目。

        Returns:
            非法 JSON payload。

        Raises:
            无显式抛出。
        """

        payload = build_representation_envelope(
            route_entry,
            summary_metrics=_summary_metrics(),
            sections=(),
            headings=(),
            paragraphs=(),
            tables=(),
            text_blocks=(),
        )
        payload["source_truth_status"] = "proven"
        return payload

    with pytest.raises(ValueError, match="source_truth_status"):
        export_manifest(
            manifest,
            route_handlers={CandidateRepresentationRoute.DOCLING_PDF: _handler},
            workspace_root=tmp_path,
        )


def test_candidate_internals_are_not_public_document_exports() -> None:
    """验证 representation export internals 未进入 documents 公共入口。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: candidate internals 被公共导出时抛出。
    """

    assert "CandidateRepresentationExportEntry" not in documents_public_exports
    assert "CandidateRepresentationRoute" not in documents_public_exports
