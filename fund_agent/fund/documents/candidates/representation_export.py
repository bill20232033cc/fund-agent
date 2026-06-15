"""候选年报表示导出 harness。

本模块只服务于 Fund documents 层内部的 candidate-only evidence gate。它定义
全量年报表示 JSON 的 manifest、输出 envelope、路径/hash 校验和 blocked-result
生成逻辑；不集成生产 ``FundDocumentRepository``，也不把 Docling、pdfplumber 或
EID HTML render 暴露给 Service/UI/Host/renderer/quality gate。
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Any, Literal

MANIFEST_SCHEMA_VERSION = "candidate_representation_export_manifest.v1"
ENVELOPE_SCHEMA_VERSION = "candidate_annual_report_representation.v1"
DEFAULT_OUTPUT_ROOT = Path("reports/representation-json")
PRODUCTION_CACHE_ROOT = Path("cache/pdf")

CandidateStatus = Literal["not_proven"]
ParserReplacementStatus = Literal["not_authorized"]


class CandidateRepresentationRoute(StrEnum):
    """候选表示路线。"""

    DOCLING_PDF = "docling_pdf_candidate"
    PDFPLUMBER_PDF = "pdfplumber_pdf_candidate"
    EID_HTML_RENDER = "eid_xbrl_html_render_candidate"


class CandidateExportMode(StrEnum):
    """候选导出执行模式。"""

    HANDLED = "handled"
    BLOCKED = "blocked"
    REFERENCE_EXISTING_JSON = "reference_existing_json"


@dataclass(frozen=True, slots=True)
class CandidateRepresentationExportEntry:
    """单个候选表示导出条目。

    Args:
        sample_id: 样本编号，如 ``S4``。
        fund_code: 基金代码。
        document_year: 年报年度。
        route: 候选路线。
        mode: 导出模式。
        input_artifact_path: 输入 artifact 路径；blocked 路线可以为空。
        accepted_input_sha256: 已接受输入 hash；没有接受 hash 时为 ``None``。
        provenance_judgment_path: 支撑该输入资格的 controller judgment。
        output_path: 输出 JSON 路径。
        report_type: 报告类型；当前只允许 ``annual_report``。

    Returns:
        dataclass 实例。

    Raises:
        无显式抛出。
    """

    sample_id: str
    fund_code: str
    document_year: int
    route: CandidateRepresentationRoute
    mode: CandidateExportMode
    input_artifact_path: Path | None
    accepted_input_sha256: str | None
    provenance_judgment_path: Path
    output_path: Path
    report_type: Literal["annual_report"] = "annual_report"


@dataclass(frozen=True, slots=True)
class CandidateRepresentationExportManifest:
    """候选表示导出 manifest。

    Args:
        entries: 导出条目。
        schema_version: manifest schema 版本。

    Returns:
        dataclass 实例。

    Raises:
        无显式抛出。
    """

    entries: tuple[CandidateRepresentationExportEntry, ...]
    schema_version: str = MANIFEST_SCHEMA_VERSION


RouteHandler = Callable[[CandidateRepresentationExportEntry], Mapping[str, Any]]


def load_manifest(path: Path) -> CandidateRepresentationExportManifest:
    """从 JSON 文件读取候选表示导出 manifest。

    Args:
        path: manifest JSON 路径。

    Returns:
        已解析并校验基础 schema 的 manifest。

    Raises:
        ValueError: JSON 顶层结构、schema 或条目字段非法时抛出。
    """

    payload = json.loads(path.read_text(encoding="utf-8"))
    return parse_manifest(payload)


def parse_manifest(payload: Mapping[str, Any]) -> CandidateRepresentationExportManifest:
    """解析候选表示导出 manifest payload。

    Args:
        payload: JSON-like manifest。

    Returns:
        ``CandidateRepresentationExportManifest``。

    Raises:
        ValueError: manifest schema 或条目字段非法时抛出。
    """

    if payload.get("schema_version") != MANIFEST_SCHEMA_VERSION:
        raise ValueError("unsupported manifest schema_version")
    raw_entries = payload.get("entries")
    if not isinstance(raw_entries, list) or not raw_entries:
        raise ValueError("manifest entries must be a non-empty list")
    entries = tuple(_parse_entry(item) for item in raw_entries)
    return CandidateRepresentationExportManifest(entries=entries)


def validate_manifest(
    manifest: CandidateRepresentationExportManifest,
    *,
    workspace_root: Path = Path("."),
    output_root: Path = DEFAULT_OUTPUT_ROOT,
) -> None:
    """校验 manifest 的路径、hash 与 candidate-only 边界。

    Args:
        manifest: 候选表示导出 manifest。
        workspace_root: 工作区根目录。
        output_root: 允许输出目录。

    Returns:
        无返回值。

    Raises:
        ValueError: 路径越界、hash 不匹配或生产 cache 写入时抛出。
    """

    if manifest.schema_version != MANIFEST_SCHEMA_VERSION:
        raise ValueError("unsupported manifest schema_version")
    for entry in manifest.entries:
        validate_entry(entry, workspace_root=workspace_root, output_root=output_root)


def validate_entry(
    entry: CandidateRepresentationExportEntry,
    *,
    workspace_root: Path = Path("."),
    output_root: Path = DEFAULT_OUTPUT_ROOT,
) -> None:
    """校验单个候选导出条目。

    Args:
        entry: 待校验条目。
        workspace_root: 工作区根目录。
        output_root: 允许输出目录。

    Returns:
        无返回值。

    Raises:
        ValueError: 条目违反路径、hash、报告类型或路线约束时抛出。
    """

    if entry.report_type != "annual_report":
        raise ValueError("candidate representation only supports annual_report")
    if not entry.fund_code.isdigit() or len(entry.fund_code) != 6:
        raise ValueError("fund_code must be a 6-digit string")
    if entry.document_year < 2000:
        raise ValueError("document_year is out of accepted range")
    _ensure_output_path(entry.output_path, output_root=output_root)
    if entry.input_artifact_path is None:
        if entry.mode != CandidateExportMode.BLOCKED:
            raise ValueError("input_artifact_path is required for non-blocked entries")
        return
    _ensure_not_production_cache(entry.input_artifact_path)
    if entry.mode == CandidateExportMode.REFERENCE_EXISTING_JSON:
        _ensure_reference_json_path(entry.input_artifact_path)
        if entry.output_path != entry.input_artifact_path:
            raise ValueError("reference_existing_json output_path must equal input_artifact_path")
        _ensure_existing_reference_json(
            workspace_root / entry.input_artifact_path,
            accepted_sha256=entry.accepted_input_sha256,
        )
        return
    if entry.route in (
        CandidateRepresentationRoute.DOCLING_PDF,
        CandidateRepresentationRoute.PDFPLUMBER_PDF,
    ) and entry.input_artifact_path.suffix.lower() != ".pdf":
        raise ValueError("PDF candidate routes require a .pdf input artifact")
    if entry.accepted_input_sha256 is not None:
        actual_hash = compute_sha256(workspace_root / entry.input_artifact_path)
        if actual_hash != entry.accepted_input_sha256:
            raise ValueError("input artifact sha256 mismatch")


def build_blocked_representation(
    entry: CandidateRepresentationExportEntry,
    *,
    failure_code: str,
    reason: str,
) -> dict[str, Any]:
    """构造候选路线不可用时的 blocked JSON envelope。

    Args:
        entry: 导出条目。
        failure_code: 稳定失败代码。
        reason: 可审计失败原因。

    Returns:
        候选表示 blocked JSON。

    Raises:
        ValueError: 失败代码或原因为空时抛出。
    """

    if not failure_code or not reason:
        raise ValueError("failure_code and reason are required")
    return build_representation_envelope(
        entry,
        summary_metrics=_empty_summary_metrics(),
        sections=(),
        headings=(),
        paragraphs=(),
        tables=(),
        text_blocks=(),
        route_failures=(
            {
                "failure_code": failure_code,
                "reason": reason,
                "source_kind": entry.route.value,
            },
        ),
    )


def build_representation_envelope(
    entry: CandidateRepresentationExportEntry,
    *,
    summary_metrics: Mapping[str, Any],
    sections: Sequence[Mapping[str, Any]],
    headings: Sequence[Mapping[str, Any]],
    paragraphs: Sequence[Mapping[str, Any]],
    tables: Sequence[Mapping[str, Any]],
    text_blocks: Sequence[Mapping[str, Any]],
    route_failures: Sequence[Mapping[str, Any]] = (),
) -> dict[str, Any]:
    """构造候选全量年报表示 JSON envelope。

    Args:
        entry: 导出条目。
        summary_metrics: 汇总指标。
        sections: section 表示。
        headings: heading 表示。
        paragraphs: paragraph 表示。
        tables: table 表示。
        text_blocks: text block 表示。
        route_failures: 路线失败记录。

    Returns:
        可序列化 JSON 字典。

    Raises:
        ValueError: summary_metrics 缺少必须字段时抛出。
    """

    _validate_summary_metrics(summary_metrics)
    return {
        "schema_version": ENVELOPE_SCHEMA_VERSION,
        "candidate_status": "not_proven",
        "field_correctness_status": "not_proven",
        "source_truth_status": "not_proven",
        "taxonomy_compatibility_status": "not_proven",
        "production_parser_replacement_status": "not_authorized",
        "source_kind": entry.route.value,
        "sample_id": entry.sample_id,
        "fund_code": entry.fund_code,
        "document_year": entry.document_year,
        "report_type": entry.report_type,
        "input_artifact": _input_artifact_payload(entry),
        "summary_metrics": dict(summary_metrics),
        "sections": list(sections),
        "headings": list(headings),
        "paragraphs": list(paragraphs),
        "tables": list(tables),
        "text_blocks": list(text_blocks),
        "failure_taxonomy": {
            "canonical_source_failures": (
                "not_found",
                "unavailable",
                "schema_drift",
                "identity_mismatch",
                "integrity_error",
            ),
            "route_failures": list(route_failures),
        },
        "blocked_claims": _blocked_claims(),
    }


def export_manifest(
    manifest: CandidateRepresentationExportManifest,
    *,
    route_handlers: Mapping[CandidateRepresentationRoute, RouteHandler] | None = None,
    workspace_root: Path = Path("."),
    output_root: Path = DEFAULT_OUTPUT_ROOT,
    allow_overwrite: bool = False,
) -> tuple[Path, ...]:
    """按 manifest 导出候选表示 JSON。

    Args:
        manifest: 候选导出 manifest。
        route_handlers: 路线 handler；测试和未来 evidence gate 可注入。
        workspace_root: 工作区根目录。
        output_root: 允许输出目录。
        allow_overwrite: 是否允许覆盖 write-producing entry 的既有输出。

    Returns:
        已写入的输出路径元组。

    Raises:
        ValueError: manifest 非法、缺少 handler 或 handler 输出越权时抛出。
    """

    validate_manifest(manifest, workspace_root=workspace_root, output_root=output_root)
    handlers = route_handlers or {}
    _ensure_write_entries_supported(manifest, handlers=handlers)
    _ensure_write_targets_available(
        manifest,
        workspace_root=workspace_root,
        allow_overwrite=allow_overwrite,
    )
    written: list[Path] = []
    for entry in manifest.entries:
        if entry.mode == CandidateExportMode.REFERENCE_EXISTING_JSON:
            continue
        payload = _payload_for_entry(entry, handlers)
        _validate_candidate_non_proof_payload(payload)
        output_path = workspace_root / entry.output_path
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        written.append(entry.output_path)
    return tuple(written)


def compute_sha256(path: Path) -> str:
    """计算文件 SHA-256。

    Args:
        path: 文件路径。

    Returns:
        十六进制 SHA-256。

    Raises:
        FileNotFoundError: 文件不存在时由 ``Path.open`` 抛出。
    """

    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main(argv: Sequence[str] | None = None) -> int:
    """候选 harness 命令入口。

    Args:
        argv: 命令行参数；为 ``None`` 时读取进程参数。

    Returns:
        进程退出码，成功为 ``0``。

    Raises:
        SystemExit: argparse 在参数非法时抛出。
    """

    parser = argparse.ArgumentParser(description="Validate candidate representation export manifest")
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--workspace-root", default=Path("."), type=Path)
    parser.add_argument("--output-root", default=DEFAULT_OUTPUT_ROOT, type=Path)
    parser.add_argument("--write-blocked", action="store_true")
    parser.add_argument("--run-built-in-handlers", action="store_true")
    parser.add_argument("--docling-artifacts-path", default=Path("cache/docling-artifacts"), type=Path)
    parser.add_argument("--docling-no-socket-block", action="store_true")
    parser.add_argument("--allow-overwrite", action="store_true")
    args = parser.parse_args(argv)

    if args.write_blocked and args.run_built_in_handlers:
        parser.error("--write-blocked and --run-built-in-handlers are mutually exclusive")

    manifest = load_manifest(args.manifest)
    if args.run_built_in_handlers:
        from fund_agent.fund.documents.candidates.representation_handlers import (
            CandidateHandlerConfig,
            built_in_route_handlers,
        )

        config = CandidateHandlerConfig(
            workspace_root=args.workspace_root,
            docling_artifacts_path=args.docling_artifacts_path,
            docling_socket_block=not args.docling_no_socket_block,
            allow_overwrite=args.allow_overwrite,
        )
        export_manifest(
            manifest,
            route_handlers=built_in_route_handlers(config),
            workspace_root=args.workspace_root,
            output_root=args.output_root,
            allow_overwrite=args.allow_overwrite,
        )
    elif args.write_blocked:
        export_manifest(
            manifest,
            workspace_root=args.workspace_root,
            output_root=args.output_root,
            allow_overwrite=args.allow_overwrite,
        )
    else:
        validate_manifest(
            manifest,
            workspace_root=args.workspace_root,
            output_root=args.output_root,
        )
    return 0


def _parse_entry(payload: Mapping[str, Any]) -> CandidateRepresentationExportEntry:
    """解析单个 manifest entry。

    Args:
        payload: entry JSON-like 字典。

    Returns:
        导出条目。

    Raises:
        ValueError: 必需字段缺失或枚举非法时抛出。
    """

    try:
        route = CandidateRepresentationRoute(str(payload["route"]))
        mode = CandidateExportMode(str(payload["mode"]))
        input_path = payload.get("input_artifact_path")
        accepted_hash = payload.get("accepted_input_sha256")
        return CandidateRepresentationExportEntry(
            sample_id=str(payload["sample_id"]),
            fund_code=str(payload["fund_code"]),
            document_year=int(payload["document_year"]),
            route=route,
            mode=mode,
            input_artifact_path=Path(str(input_path)) if input_path else None,
            accepted_input_sha256=str(accepted_hash) if accepted_hash else None,
            provenance_judgment_path=Path(str(payload["provenance_judgment_path"])),
            output_path=Path(str(payload["output_path"])),
            report_type=str(payload.get("report_type", "annual_report")),  # type: ignore[arg-type]
        )
    except KeyError as exc:
        raise ValueError(f"missing manifest field: {exc.args[0]}") from exc
    except ValueError as exc:
        raise ValueError(f"invalid manifest entry: {exc}") from exc


def _payload_for_entry(
    entry: CandidateRepresentationExportEntry,
    handlers: Mapping[CandidateRepresentationRoute, RouteHandler],
) -> Mapping[str, Any]:
    """根据 entry 和 handler 构造输出 payload。

    Args:
        entry: 导出条目。
        handlers: 路线 handler 映射。

    Returns:
        JSON-like payload。

    Raises:
        ValueError: 缺少 handler 或不支持模式时抛出。
    """

    if entry.mode == CandidateExportMode.BLOCKED:
        return build_blocked_representation(
            entry,
            failure_code=f"{entry.route.value}_not_available",
            reason="route artifact is not accepted for this sample",
        )
    if entry.mode == CandidateExportMode.HANDLED:
        handler = handlers.get(entry.route)
        if handler is None:
            raise ValueError(f"missing route handler for {entry.route.value}")
        return handler(entry)
    if entry.mode == CandidateExportMode.REFERENCE_EXISTING_JSON:
        raise ValueError("reference_existing_json validation is supported, rewrite is not")
    raise ValueError(f"unsupported export mode: {entry.mode}")


def _input_artifact_payload(entry: CandidateRepresentationExportEntry) -> dict[str, str | None]:
    """构造输入 artifact 元数据。

    Args:
        entry: 导出条目。

    Returns:
        输入 artifact 元数据字典。

    Raises:
        无显式抛出。
    """

    return {
        "path": str(entry.input_artifact_path) if entry.input_artifact_path else None,
        "accepted_sha256": entry.accepted_input_sha256,
        "provenance_judgment_path": str(entry.provenance_judgment_path),
    }


def _ensure_output_path(path: Path, *, output_root: Path) -> None:
    """校验输出路径只能位于允许目录。

    Args:
        path: 输出路径。
        output_root: 允许输出根目录。

    Returns:
        无返回值。

    Raises:
        ValueError: 输出路径越界或指向生产 cache 时抛出。
    """

    _ensure_safe_relative_path(path)
    if path.suffix.lower() != ".json":
        raise ValueError("candidate representation output must be a JSON file")
    if not path.is_relative_to(output_root):
        raise ValueError("candidate representation output must stay under reports/representation-json")
    _ensure_not_production_cache(path)


def _ensure_not_production_cache(path: Path) -> None:
    """拒绝生产-shaped PDF cache 路径。

    Args:
        path: 待检查路径。

    Returns:
        无返回值。

    Raises:
        ValueError: 路径位于 ``cache/pdf`` 时抛出。
    """

    _ensure_safe_relative_path(path)
    if path == PRODUCTION_CACHE_ROOT or path.is_relative_to(PRODUCTION_CACHE_ROOT):
        raise ValueError("candidate harness must not read or write production-shaped cache/pdf")


def _ensure_safe_relative_path(path: Path) -> None:
    """校验路径是无 traversal 的相对路径。

    Args:
        path: 待检查路径。

    Returns:
        无返回值。

    Raises:
        ValueError: 路径为绝对路径或包含 ``..`` 时抛出。
    """

    if path.is_absolute():
        raise ValueError("candidate artifact paths must be relative")
    if ".." in path.parts:
        raise ValueError("candidate artifact paths must not contain parent traversal")


def _ensure_reference_json_path(path: Path) -> None:
    """校验 reference-existing JSON 输入路径。

    Args:
        path: 既有 representation JSON 路径。

    Returns:
        无返回值。

    Raises:
        ValueError: 路径不是 JSON 或不在 representation 输出目录时抛出。
    """

    if path.suffix.lower() != ".json":
        raise ValueError("reference_existing_json input must be a JSON file")
    if not path.is_relative_to(DEFAULT_OUTPUT_ROOT):
        raise ValueError("reference_existing_json input must stay under reports/representation-json")


def _ensure_existing_reference_json(path: Path, *, accepted_sha256: str | None) -> None:
    """校验既有 reference JSON 存在且可解析。

    Args:
        path: 工作区内既有 representation JSON 路径。
        accepted_sha256: 可选的已接受 JSON hash。

    Returns:
        无返回值。

    Raises:
        ValueError: 文件不存在、不是文件、JSON 不可解析或 hash 不匹配时抛出。
    """

    if not path.is_file():
        raise ValueError("reference_existing_json input must exist")
    try:
        json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError("reference_existing_json input must be valid JSON") from exc
    if accepted_sha256 is not None and compute_sha256(path) != accepted_sha256:
        raise ValueError("reference_existing_json sha256 mismatch")


def _ensure_write_targets_available(
    manifest: CandidateRepresentationExportManifest,
    *,
    workspace_root: Path,
    allow_overwrite: bool,
) -> None:
    """在写入前一次性校验 write-producing 输出是否可写。

    Args:
        manifest: 候选导出 manifest。
        workspace_root: 工作区根目录。
        allow_overwrite: 是否允许覆盖已有输出。

    Returns:
        无返回值。

    Raises:
        ValueError: 默认 no-clobber 下存在 write-producing 输出时抛出。
    """

    if allow_overwrite:
        return
    existing_outputs: list[str] = []
    for entry in manifest.entries:
        if entry.mode == CandidateExportMode.REFERENCE_EXISTING_JSON:
            continue
        output_path = workspace_root / entry.output_path
        if output_path.exists():
            existing_outputs.append(str(entry.output_path))
    if existing_outputs:
        raise ValueError(f"candidate representation output already exists: {existing_outputs}")


def _ensure_write_entries_supported(
    manifest: CandidateRepresentationExportManifest,
    *,
    handlers: Mapping[CandidateRepresentationRoute, RouteHandler],
) -> None:
    """在写入前校验当前执行模式能处理所有 write-producing entries。

    Args:
        manifest: 候选导出 manifest。
        handlers: 当前可用 route handlers。

    Returns:
        无返回值。

    Raises:
        ValueError: handled entry 缺少 route handler 时抛出。
    """

    missing_handlers = [
        entry.route.value
        for entry in manifest.entries
        if entry.mode == CandidateExportMode.HANDLED and entry.route not in handlers
    ]
    if missing_handlers:
        raise ValueError(f"missing route handler for write-producing entries: {missing_handlers}")


def _validate_summary_metrics(summary_metrics: Mapping[str, Any]) -> None:
    """校验 summary metrics 至少包含路线比较所需闭集字段。

    Args:
        summary_metrics: 汇总指标。

    Returns:
        无返回值。

    Raises:
        ValueError: 必需字段缺失时抛出。
    """

    required_keys = {
        "page_count",
        "section_count",
        "heading_count",
        "paragraph_count",
        "table_count",
        "table_cell_count",
        "has_page_number",
        "has_bbox",
        "has_section_tree",
        "has_table_cell_locator",
        "has_content_hash",
        "has_url_or_source_locator",
    }
    missing = required_keys - set(summary_metrics)
    if missing:
        raise ValueError(f"summary_metrics missing required keys: {sorted(missing)}")


def _empty_summary_metrics() -> dict[str, int | bool]:
    """返回 blocked route 的空 summary metrics。

    Args:
        无。

    Returns:
        空指标字典。

    Raises:
        无显式抛出。
    """

    return {
        "page_count": 0,
        "section_count": 0,
        "heading_count": 0,
        "paragraph_count": 0,
        "table_count": 0,
        "table_cell_count": 0,
        "has_page_number": False,
        "has_bbox": False,
        "has_section_tree": False,
        "has_table_cell_locator": False,
        "has_content_hash": False,
        "has_url_or_source_locator": False,
    }


def _blocked_claims() -> tuple[str, ...]:
    """返回所有候选输出必须保留的 blocked claims。

    Args:
        无。

    Returns:
        blocked claim 元组。

    Raises:
        无显式抛出。
    """

    return (
        "not_raw_xml_download_proof",
        "not_field_correctness_proof",
        "not_taxonomy_compatibility_proof",
        "not_source_truth",
        "not_readiness_proof",
        "no_repository_behavior_change",
        "no_parser_replacement",
    )


def _validate_candidate_non_proof_payload(payload: Mapping[str, Any]) -> None:
    """校验输出 payload 没有越过 candidate-only 状态。

    Args:
        payload: 待写入 JSON payload。

    Returns:
        无返回值。

    Raises:
        ValueError: payload 声明 source truth、field correctness 或 parser replacement 时抛出。
    """

    if payload.get("candidate_status") != "not_proven":
        raise ValueError("candidate_status must remain not_proven")
    if payload.get("field_correctness_status") != "not_proven":
        raise ValueError("field_correctness_status must remain not_proven")
    if payload.get("source_truth_status") != "not_proven":
        raise ValueError("source_truth_status must remain not_proven")
    if payload.get("taxonomy_compatibility_status") != "not_proven":
        raise ValueError("taxonomy_compatibility_status must remain not_proven")
    if payload.get("production_parser_replacement_status") != "not_authorized":
        raise ValueError("production parser replacement must remain not_authorized")
    blocked_claims = set(payload.get("blocked_claims", ()))
    required_claims = set(_blocked_claims())
    if not required_claims <= blocked_claims:
        raise ValueError("candidate payload is missing blocked_claim guards")


if __name__ == "__main__":
    raise SystemExit(main())
