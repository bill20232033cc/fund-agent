"""Docling candidate 内部模型测试。"""

from __future__ import annotations

import json
from pathlib import Path
from typing import get_args

import pytest

from fund_agent.fund.documents.candidates.models import (
    NORMALIZATION_RULE_NAMES,
    CandidateArtifactIdentity,
    NormalizationRuleName,
)
from fund_agent.fund.documents import __all__ as documents_public_exports
from fund_agent.fund.extractors.models import EvidenceSourceKind

FIXTURE_PATH = Path("tests/fixtures/fund/docling_route_a/004393_2025/excerpt.json")
REQUIRED_TABLE_CASES = {
    "toc-table-0",
    "manager-table-14",
    "industry-table-72",
    "stock-holding-table-74",
    "manager-holding-table-86",
    "financial-continuation-61",
    "financial-continuation-62",
}


def _load_fixture() -> dict[str, object]:
    """读取 no-live excerpt fixture。

    Args:
        无。

    Returns:
        fixture JSON 字典。

    Raises:
        AssertionError: fixture 不是 JSON object 时抛出。
    """

    payload = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    assert isinstance(payload, dict)
    return payload


def test_fixture_metadata_preserves_non_proof_statuses() -> None:
    """验证 fixture metadata 保留 non-proof 边界。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: metadata 不符合 accepted plan 时抛出。
    """

    metadata = _load_fixture()["metadata"]
    assert isinstance(metadata, dict)
    assert metadata["fixture_schema_version"] == "docling_route_a_excerpt.v1"
    assert metadata["route_a_json_sha256"] == (
        "b7a664c31a11db332815884b5632451ed6e64c8d246254ed23f55f409364c933"
    )
    assert metadata["full_json_committed"] is False
    assert metadata["source_truth_status"] == "not_proven"
    assert metadata["field_correctness_status"] == "not_proven"
    assert metadata["taxonomy_compatibility_status"] == "not_proven"
    assert metadata["production_parser_replacement_status"] == "not_authorized"


def test_required_table_cases_have_non_empty_cells_and_provenance() -> None:
    """验证必需表格 case 都有非空 table_cells 和 provenance。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: table case 缺失、cells 为空或 provenance 缺失时抛出。
    """

    table_excerpts = _load_fixture()["table_excerpts"]
    assert isinstance(table_excerpts, list)
    by_case = {item["case_id"]: item for item in table_excerpts if isinstance(item, dict)}
    assert REQUIRED_TABLE_CASES <= set(by_case)
    for case_id in REQUIRED_TABLE_CASES:
        item = by_case[case_id]
        assert item["table_cells"], case_id
        assert item["prov"], case_id
        assert all("bbox" in cell for cell in item["table_cells"])


def test_candidate_identity_is_candidate_only() -> None:
    """验证 candidate identity 只能表达 candidate-only 状态。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: candidate identity 不符合边界时抛出。
    """

    metadata = _load_fixture()["metadata"]
    origin = _load_fixture()["origin_excerpt"]
    assert isinstance(metadata, dict)
    assert isinstance(origin, dict)
    identity = CandidateArtifactIdentity(
        source_kind="docling_pdf_candidate",
        document_kind="annual_report_candidate",
        fund_code=str(metadata["fund_code"]),
        fund_name=str(metadata["fund_name"]),
        report_year=int(metadata["report_year"]),
        report_type="annual_report",
        input_pdf_filename=str(origin["filename"]),
        input_pdf_mimetype=str(origin["mimetype"]),
        input_pdf_binary_hash=str(origin["binary_hash"]),
        docling_schema_name=None,
        docling_version="2.93.0",
        docling_json_sha256=str(metadata["route_a_json_sha256"]),
        markdown_sha256=str(metadata["route_a_markdown_sha256"]),
    )
    assert identity.source_truth_status == "not_proven"
    assert identity.field_correctness_status == "not_proven"
    assert identity.production_parser_replacement_status == "not_authorized"


def test_candidate_identity_rejects_truth_claims() -> None:
    """验证 candidate identity 拒绝 source truth 状态提升。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 未拒绝 truth claim 时抛出。
    """

    with pytest.raises(ValueError, match="source truth"):
        CandidateArtifactIdentity(
            source_kind="docling_pdf_candidate",
            document_kind="annual_report_candidate",
            fund_code="004393",
            fund_name="安信企业价值优选混合A",
            report_year=2025,
            report_type="annual_report",
            input_pdf_filename=None,
            input_pdf_mimetype=None,
            input_pdf_binary_hash=None,
            docling_schema_name=None,
            docling_version=None,
            docling_json_sha256="hash",
            markdown_sha256=None,
            source_truth_status="proven",  # type: ignore[arg-type]
        )


def test_normalization_rule_type_matches_closed_vocabulary_exactly() -> None:
    """验证 NormalizationRuleName Literal 与闭合词表完全一致。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: Literal 和闭合词表不一致时抛出。
    """

    assert get_args(NormalizationRuleName) == NORMALIZATION_RULE_NAMES


def test_candidate_internals_are_not_public_documents_exports() -> None:
    """验证 candidate internals 未进入 documents 公共入口。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: candidate internals 被公共导出时抛出。
    """

    assert "CandidateArtifactIdentity" not in documents_public_exports
    assert "docling_pdf_candidate" not in get_args(EvidenceSourceKind)

