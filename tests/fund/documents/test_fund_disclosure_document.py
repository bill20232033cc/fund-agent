"""FundDisclosureDocument candidate-only schema 测试。"""

from __future__ import annotations

import ast
from pathlib import Path
from typing import get_args

import pytest

from fund_agent.fund.documents.candidates.fund_disclosure_document import (
    FundDisclosureDocument,
    FundDisclosureDocumentCellLocator,
    FundDisclosureDocumentFailure,
    FundDisclosureDocumentIdentity,
    FundDisclosureDocumentNavigationNode,
    FundDisclosureDocumentParagraphBlock,
    FundDisclosureDocumentSection,
    FundDisclosureDocumentTableBlock,
)
from fund_agent.fund.documents.candidates.models import LocatorStability
from fund_agent.fund.documents.models import AnnualReportSourceFailureCategory
from fund_agent.fund.extractors.models import EvidenceSourceKind
from fund_agent.fund.processors.contracts import (
    CandidateBoundaryStatus,
    FundDisclosureDocumentIntermediate,
    FundProcessorDispatchKey,
    FundProcessorInput,
)
from fund_agent.fund.processors.fund_disclosure_processor import (
    FundDisclosureDocumentProcessor,
)
from fund_agent.fund.source_provenance import default_public_source_provenance

_HASH_A = "a" * 64
_HASH_B = "b" * 64
_HASH_C = "c" * 64


def _identity(**overrides: object) -> FundDisclosureDocumentIdentity:
    """构造合法 identity fixture。

    Args:
        **overrides: 字段覆盖。

    Returns:
        候选文档身份对象。

    Raises:
        ValueError: 覆盖字段非法时由构造函数抛出。
    """

    values: dict[str, object] = {
        "source_artifact_kind": "eid_xbrl_html_render_candidate.v1",
        "source_kind": "eid_xbrl_html_render_candidate",
        "fund_code": "004393",
        "fund_id": "10004393",
        "instance_id": "upload-2025",
        "report_year": 2025,
        "report_type_code": "annual",
        "report_type_label": "年度报告",
        "report_send_date": "2026-03-31",
        "source_list": ("https://eid.csrc.gov.cn/fund/notice",),
        "index_url": "https://eid.csrc.gov.cn/fund/notice",
        "instance_view_url": "https://eid.csrc.gov.cn/fund/detail/upload-2025",
        "render_url": "https://eid.csrc.gov.cn/fund/render/upload-2025",
        "redirect_location": None,
        "content_type": "text/html",
        "content_length": 1024,
        "content_hash": _HASH_A,
        "fetched_at": "2026-06-18T00:00:00Z",
        "render_status": "ok",
        "navigation_present": True,
    }
    values.update(overrides)
    return FundDisclosureDocumentIdentity(**values)  # type: ignore[arg-type]


def _navigation() -> FundDisclosureDocumentNavigationNode:
    """构造 navigation fixture。

    Args:
        无。

    Returns:
        navigation node。

    Raises:
        无显式抛出。
    """

    return FundDisclosureDocumentNavigationNode(
        node_id="nav-1",
        title_text="一、基金简介",
        title_normalized="一、基金简介",
        level=1,
        parent_node_id=None,
        child_node_ids=(),
        section_id="sec-1",
        locator_stability="strong",
        order_index=0,
    )


def _section(**overrides: object) -> FundDisclosureDocumentSection:
    """构造 section fixture。

    Args:
        **overrides: 字段覆盖。

    Returns:
        section。

    Raises:
        ValueError: 覆盖字段非法时由构造函数抛出。
    """

    values: dict[str, object] = {
        "section_id": "sec-1",
        "heading_text_raw": "一、基金简介",
        "heading_text_normalized": "一、基金简介",
        "heading_path": ("一、基金简介",),
        "heading_level": 1,
        "start_page_or_offset": 0,
        "end_page_or_offset": 10,
        "child_section_ids": (),
        "locator_stability": "strong",
        "normalization_notes": ("cjk_space_repair",),
    }
    values.update(overrides)
    return FundDisclosureDocumentSection(**values)  # type: ignore[arg-type]


def _paragraph() -> FundDisclosureDocumentParagraphBlock:
    """构造 paragraph block fixture。

    Args:
        无。

    Returns:
        paragraph block。

    Raises:
        无显式抛出。
    """

    return FundDisclosureDocumentParagraphBlock(
        block_id="p-1",
        block_type="paragraph",
        section_id="sec-1",
        heading_path=("一、基金简介",),
        text_raw="基金简介正文",
        text_normalized="基金简介正文",
        content_hash=_HASH_B,
        locator_stability="usable",
        normalization_applied=("cjk_space_repair",),
    )


def _cell(**overrides: object) -> FundDisclosureDocumentCellLocator:
    """构造 cell locator fixture。

    Args:
        **overrides: 字段覆盖。

    Returns:
        cell locator。

    Raises:
        ValueError: 覆盖字段非法时由构造函数抛出。
    """

    values: dict[str, object] = {
        "cell_id": "cell-1",
        "table_id": "table-1",
        "render_url": "https://eid.csrc.gov.cn/fund/render/upload-2025",
        "section_anchor": "sec-1",
        "heading_path": ("一、基金简介",),
        "table_index_under_section": 0,
        "row_index": 0,
        "column_index": 0,
        "row_label_path": ("资产净值",),
        "column_header_path": ("本期末",),
        "cell_text": "100.00",
        "cell_text_normalized": "100.00",
        "cell_hash": _HASH_C,
        "is_header_cell": False,
        "locator_stability": "strong",
        "normalization_applied": ("numeric_punctuation_repair",),
    }
    values.update(overrides)
    return FundDisclosureDocumentCellLocator(**values)  # type: ignore[arg-type]


def _table(**overrides: object) -> FundDisclosureDocumentTableBlock:
    """构造 table block fixture。

    Args:
        **overrides: 字段覆盖。

    Returns:
        table block。

    Raises:
        ValueError: 覆盖字段非法时由构造函数抛出。
    """

    values: dict[str, object] = {
        "table_id": "table-1",
        "section_id": "sec-1",
        "heading_text": "主要财务指标",
        "heading_path": ("一、基金简介", "主要财务指标"),
        "table_index_under_section": 0,
        "table_caption_or_nearby_heading": "主要财务指标",
        "header_rows": (0,),
        "body_rows": (1,),
        "row_count": 2,
        "column_count": 2,
        "merged_header_detected": False,
        "cells": (_cell(),),
        "locator_stability": "strong",
        "extraction_note": None,
    }
    values.update(overrides)
    return FundDisclosureDocumentTableBlock(**values)  # type: ignore[arg-type]


def _document(**overrides: object) -> FundDisclosureDocument:
    """构造完整 FundDisclosureDocument fixture。

    Args:
        **overrides: 字段覆盖。

    Returns:
        候选文档对象。

    Raises:
        ValueError: 覆盖字段非法时由构造函数抛出。
    """

    values: dict[str, object] = {
        "identity": _identity(),
        "navigation_nodes": (_navigation(),),
        "sections": (_section(),),
        "paragraph_blocks": (_paragraph(),),
        "table_blocks": (_table(),),
        "failures": (),
        "source_provenance": default_public_source_provenance(),
        "failure_class": None,
    }
    values.update(overrides)
    return FundDisclosureDocument(**values)  # type: ignore[arg-type]


class TestFundDisclosureDocumentIdentityConstruction:
    """验证 identity 构造与边界。"""

    def test_identity_accepts_valid_fields(self) -> None:
        """合法 identity 保留 candidate-only 边界字段。

        Args:
            无。

        Returns:
            无返回值。

        Raises:
            AssertionError: 字段不符合预期时抛出。
        """

        identity = _identity()

        assert identity.fund_code == "004393"
        assert identity.source_artifact_kind == "eid_xbrl_html_render_candidate.v1"
        assert identity.source_kind == "eid_xbrl_html_render_candidate"
        assert identity.candidate_only is True
        assert identity.field_correctness_status == "not_proven"
        assert identity.source_truth_status == "not_proven"
        assert identity.parser_replacement_authorized is False
        assert identity.readiness_status == "not_ready"

    @pytest.mark.parametrize("fund_code", ("4393", "abcdef", "0000000"))
    def test_identity_rejects_invalid_fund_code(self, fund_code: str) -> None:
        """非法基金代码被拒绝。

        Args:
            fund_code: 非 6 位数字基金代码。

        Returns:
            无返回值。

        Raises:
            AssertionError: 未抛出 ValueError 时抛出。
        """

        with pytest.raises(ValueError):
            _identity(fund_code=fund_code)

    def test_identity_rejects_invalid_report_year(self) -> None:
        """非正数年份被拒绝。

        Args:
            无。

        Returns:
            无返回值。

        Raises:
            AssertionError: 未抛出 ValueError 时抛出。
        """

        with pytest.raises(ValueError):
            _identity(report_year=0)

    def test_identity_rejects_boundary_escalation(self) -> None:
        """identity 不允许提升 source_truth/readiness。

        Args:
            无。

        Returns:
            无返回值。

        Raises:
            AssertionError: 未抛出 ValueError 时抛出。
        """

        with pytest.raises(ValueError):
            _identity(readiness_status="ready")


class TestFundDisclosureDocumentIdentityContentHash:
    """验证 identity content_hash 规则。"""

    def test_content_hash_none_and_64_hex_are_valid(self) -> None:
        """None 与 64 位 hex hash 有效。

        Args:
            无。

        Returns:
            无返回值。

        Raises:
            AssertionError: 合法 hash 被拒绝时抛出。
        """

        assert _identity(content_hash=None).content_hash is None
        assert _identity(content_hash="0123456789abcdef" * 4).content_hash is not None

    @pytest.mark.parametrize("content_hash", ("", "g" * 64, "a" * 63, "a" * 65))
    def test_invalid_content_hash_is_rejected(self, content_hash: str) -> None:
        """空、非 hex、长度错误 hash 被拒绝。

        Args:
            content_hash: 非法 hash。

        Returns:
            无返回值。

        Raises:
            AssertionError: 未抛出 ValueError 时抛出。
        """

        with pytest.raises(ValueError):
            _identity(content_hash=content_hash)


class TestFundDisclosureDocumentIdentitySerialization:
    """验证 identity serialization。"""

    def test_identity_round_trip_preserves_all_fields(self) -> None:
        """identity to_dict/from_dict 往返相等。

        Args:
            无。

        Returns:
            无返回值。

        Raises:
            AssertionError: round-trip 不相等时抛出。
        """

        identity = _identity()

        assert FundDisclosureDocumentIdentity.from_dict(identity.to_dict()) == identity


class TestFundDisclosureDocumentSectionConstruction:
    """验证 section 构造。"""

    def test_section_construction_and_validation(self) -> None:
        """section 合法字段可构造，非法范围被拒绝。

        Args:
            无。

        Returns:
            无返回值。

        Raises:
            AssertionError: 行为不符合预期时抛出。
        """

        section = _section()
        assert section.locator_stability == "strong"
        with pytest.raises(ValueError):
            _section(start_page_or_offset=10, end_page_or_offset=1)


class TestFundDisclosureDocumentTableBlockConstruction:
    """验证 table block 构造。"""

    def test_table_block_shape_and_cell_consistency(self) -> None:
        """table shape 与 cell locator 一致性被校验。

        Args:
            无。

        Returns:
            无返回值。

        Raises:
            AssertionError: 行为不符合预期时抛出。
        """

        table = _table()
        assert table.row_count == 2
        assert table.column_count == 2
        with pytest.raises(ValueError):
            _table(cells=(_cell(row_index=3),))
        with pytest.raises(ValueError):
            _table(cells=(_cell(table_id="other"),))


class TestFundDisclosureDocumentCellLocatorConstruction:
    """验证 cell locator 构造。"""

    def test_cell_locator_indices_and_hash(self) -> None:
        """cell row/column index 与 hash 被校验。

        Args:
            无。

        Returns:
            无返回值。

        Raises:
            AssertionError: 行为不符合预期时抛出。
        """

        cell = _cell()
        assert cell.row_index == 0
        assert cell.column_index == 0
        with pytest.raises(ValueError):
            _cell(row_index=-1)
        with pytest.raises(ValueError):
            _cell(cell_hash="bad")


class TestFundDisclosureDocumentConstruction:
    """验证顶层文档构造。"""

    def test_full_document_assembly_and_fixed_intermediate_kind(self) -> None:
        """完整文档固定 intermediate_kind 并满足基础字段。

        Args:
            无。

        Returns:
            无返回值。

        Raises:
            AssertionError: 字段不符合预期时抛出。
        """

        document = _document()

        assert document.document_kind == "annual_report"
        assert document.fund_code == "004393"
        assert document.report_year == 2025
        assert document.intermediate_kind == "fund_disclosure_document.v1"

    def test_unknown_section_reference_is_rejected(self) -> None:
        """未知 section 引用被拒绝。

        Args:
            无。

        Returns:
            无返回值。

        Raises:
            AssertionError: 未抛出 ValueError 时抛出。
        """

        with pytest.raises(ValueError):
            _document(
                navigation_nodes=(
                    _navigation().__class__(**{**_navigation().to_dict(), "section_id": "missing"}),
                )
            )


class TestFundDisclosureDocumentSerializationRoundTrip:
    """验证完整文档 serialization。"""

    def test_full_document_round_trip_preserves_equality(self) -> None:
        """完整文档 to_dict/from_dict 往返相等。

        Args:
            无。

        Returns:
            无返回值。

        Raises:
            AssertionError: round-trip 不相等时抛出。
        """

        document = _document(
            failures=(
                FundDisclosureDocumentFailure(
                    failure_code="value_unvalidated",
                    failure_message="candidate value not validated",
                    source_stage="projection",
                    canonical_failure_class=None,
                ),
            )
        )

        assert FundDisclosureDocument.from_dict(document.to_dict()) == document


class TestFundDisclosureDocumentBoundaryFields:
    """验证顶层 candidate_boundary。"""

    def test_candidate_boundary_enforces_not_proven_not_ready(self) -> None:
        """CandidateBoundaryStatus 保持 not_proven/not_ready。

        Args:
            无。

        Returns:
            无返回值。

        Raises:
            AssertionError: 边界语义错误时抛出。
        """

        document = _document()

        assert document.candidate_boundary.candidate_only is True
        assert document.candidate_boundary.field_correctness_status == "not_proven"
        assert document.candidate_boundary.source_truth_status == "not_proven"
        assert document.candidate_boundary.readiness_status == "not_ready"
        with pytest.raises(ValueError):
            CandidateBoundaryStatus(
                candidate_only=False,
                field_correctness_status="not_proven",
                source_truth_status="not_proven",
            )


class TestFundDisclosureDocumentLocatorStabilityReuse:
    """验证 LocatorStability 复用既有 literal。"""

    def test_locator_stability_literal_values_match_existing_type(self) -> None:
        """LocatorStability 仍来自 existing candidate models。

        Args:
            无。

        Returns:
            无返回值。

        Raises:
            AssertionError: literal 值被改动时抛出。
        """

        assert get_args(LocatorStability) == ("strong", "usable", "weak", "blocked")


class TestFundDisclosureDocumentNavigationRoundTrip:
    """验证 navigation serialization。"""

    def test_navigation_node_round_trip(self) -> None:
        """navigation node to_dict/from_dict 往返相等。

        Args:
            无。

        Returns:
            无返回值。

        Raises:
            AssertionError: round-trip 不相等时抛出。
        """

        node = _navigation()

        assert FundDisclosureDocumentNavigationNode.from_dict(node.to_dict()) == node


class TestFundDisclosureDocumentCandidateOnlyGuards:
    """验证 candidate-only guard。"""

    def test_candidate_only_and_readiness_cannot_be_changed(self) -> None:
        """candidate_only/readiness 非安全值被拒绝。

        Args:
            无。

        Returns:
            无返回值。

        Raises:
            AssertionError: 未抛出 ValueError 时抛出。
        """

        with pytest.raises(ValueError):
            _identity(candidate_only=False)
        with pytest.raises(ValueError):
            _identity(readiness_status="ready")


class TestFundDisclosureDocumentDoesNotImportEvidenceAnchor:
    """验证 candidate module 不依赖 extractor EvidenceAnchor。"""

    def test_candidate_module_does_not_import_evidence_anchor_or_source_kind(self) -> None:
        """AST 证明 schema module 未 import EvidenceAnchor/EvidenceSourceKind。

        Args:
            无。

        Returns:
            无返回值。

        Raises:
            AssertionError: 发现 forbidden import 时抛出。
        """

        tree = ast.parse(
            Path("fund_agent/fund/documents/candidates/fund_disclosure_document.py").read_text(
                encoding="utf-8"
            )
        )
        imported_symbols = {
            alias.name
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom)
            for alias in node.names
        }

        assert "EvidenceAnchor" not in imported_symbols
        assert "EvidenceSourceKind" not in imported_symbols


class TestFundDisclosureDocumentIsNotReExported:
    """验证 public init 不导出 candidate internals。"""

    def test_public_init_files_do_not_export_fund_disclosure_document(self) -> None:
        """fund/documents public init 不暴露 FundDisclosureDocument。

        Args:
            无。

        Returns:
            无返回值。

        Raises:
            AssertionError: public surface 泄漏 candidate internals 时抛出。
        """

        for init_path in (
            Path("fund_agent/fund/__init__.py"),
            Path("fund_agent/fund/documents/__init__.py"),
        ):
            content = init_path.read_text(encoding="utf-8")
            assert "FundDisclosureDocument" not in content
            assert "fund_disclosure_document" not in content


class TestFundDisclosureDocumentSatisfiesIntermediateProtocol:
    """验证 Protocol 合规。"""

    def test_document_is_runtime_intermediate_protocol_instance(self) -> None:
        """FundDisclosureDocument 满足 FundDisclosureDocumentIntermediate Protocol。

        Args:
            无。

        Returns:
            无返回值。

        Raises:
            AssertionError: Protocol runtime check 失败时抛出。
        """

        assert isinstance(_document(), FundDisclosureDocumentIntermediate)


class TestFundDisclosureDocumentReachesProcessor:
    """验证 processor reachability。"""

    def test_document_reaches_fully_gapped_missing_behavior(self) -> None:
        """具体 schema 通过 processor identity check，进入 fully-gapped missing 路径。

        Args:
            无。

        Returns:
            无返回值。

        Raises:
            AssertionError: 出现 input_type_mismatch 或未返回六个字段族时抛出。
        """

        processor = FundDisclosureDocumentProcessor()
        result = processor.extract(
            FundProcessorInput(
                context=FundProcessorDispatchKey(
                    fund_type="active_fund",
                    report_type="annual_report",
                    intermediate_kind="fund_disclosure_document.v1",
                    source_kind="annual_report",
                    document_year=2025,
                    fund_code="004393",
                ),
                intermediate=_document(),
            )
        )

        assert result.contract_status == "blocked"
        assert result.gaps == ()
        assert len(result.field_families) == 6
        assert {family.status for family in result.field_families} == {"missing"}


class TestFundDisclosureDocumentNoConsumptionASTGuards:
    """验证 consumer tree 不 import FundDisclosureDocument candidate internals。"""

    def test_service_ui_host_renderer_audit_quality_and_extractors_do_not_import_fund_disclosure_candidates(
        self,
    ) -> None:
        """AST 扫描 consumer tree，禁止直接 import 新 candidate internals。

        Args:
            无。

        Returns:
            无返回值。

        Raises:
            AssertionError: 发现 forbidden import 时抛出。
        """

        forbidden_import_prefixes = (
            "fund_agent.fund.documents.candidates.fund_disclosure_document",
            "fund_agent.fund.documents.candidates.fund_disclosure_failure_mapping",
        )
        guarded_paths = (
            Path("fund_agent/services"),
            Path("fund_agent/ui"),
            Path("fund_agent/host"),
            Path("fund_agent/agent"),
            Path("fund_agent/fund/template"),
            Path("fund_agent/fund/audit"),
            Path("fund_agent/fund/extractors"),
            Path("fund_agent/fund/report_quality_validation.py"),
        )
        violations: list[str] = []
        for path in _iter_python_files(guarded_paths):
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                module = _imported_module_name(node)
                if module is not None and module.startswith(forbidden_import_prefixes):
                    violations.append(f"{path}:{module}")

        assert violations == []

    def test_closed_literals_unchanged(self) -> None:
        """验证 EvidenceSourceKind 与 AnnualReportSourceFailureCategory 未扩展。

        Args:
            无。

        Returns:
            无返回值。

        Raises:
            AssertionError: closed literal 被扩展时抛出。
        """

        assert get_args(EvidenceSourceKind) == ("annual_report", "external_api", "derived")
        assert get_args(AnnualReportSourceFailureCategory) == (
            "not_found",
            "unavailable",
            "schema_drift",
            "identity_mismatch",
            "integrity_error",
        )


def _iter_python_files(paths: tuple[Path, ...]) -> tuple[Path, ...]:
    """展开待检查 Python 文件。

    Args:
        paths: 文件或目录路径。

    Returns:
        Python 文件路径元组。

    Raises:
        无显式抛出。
    """

    files: list[Path] = []
    for path in paths:
        if path.is_file():
            files.append(path)
        else:
            files.extend(sorted(path.rglob("*.py")))
    return tuple(files)


def _imported_module_name(node: ast.AST) -> str | None:
    """提取 import 节点的模块名。

    Args:
        node: AST 节点。

    Returns:
        import 模块名；非 import 节点返回 ``None``。

    Raises:
        无显式抛出。
    """

    if isinstance(node, ast.Import):
        return node.names[0].name
    if isinstance(node, ast.ImportFrom):
        return node.module
    return None
