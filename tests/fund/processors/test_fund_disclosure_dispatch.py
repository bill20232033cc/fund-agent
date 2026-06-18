"""FundDisclosureDocument admission helper 测试。"""

from __future__ import annotations

import ast
from dataclasses import dataclass
from pathlib import Path
from typing import Literal, get_args

import pytest

from fund_agent.fund.extractors.models import EvidenceAnchor, EvidenceSourceKind
from fund_agent.fund.processors.contracts import (
    AnnualReportSourceFailureCategory,
    CandidateBoundaryStatus,
    FundDisclosureDocumentIntermediate,
    FundExtractionGapCode,
    FundProcessorDispatchKey,
)
from fund_agent.fund.processors.fund_disclosure_dispatch import (
    FAILURE_CLASS_ADMISSION_MAP,
    admit_disclosure_intermediate,
)
from fund_agent.fund.source_provenance import (
    PublicSourceProvenance,
    default_public_source_provenance,
)


@dataclass(frozen=True, slots=True)
class StubDisclosureIntermediate:
    """测试专用受控文档表示中间态，不导出到生产模型。"""

    document_kind: Literal["annual_report"] = "annual_report"
    fund_code: str = "004393"
    report_year: int = 2025
    intermediate_kind: Literal["fund_disclosure_document.v1"] = "fund_disclosure_document.v1"
    source_provenance: PublicSourceProvenance | None = None
    candidate_boundary: CandidateBoundaryStatus | None = None
    failure_class: AnnualReportSourceFailureCategory | None = None


def _dispatch_key() -> FundProcessorDispatchKey:
    """构造 FundDisclosureDocument admission 测试路由键。

    Args:
        无。

    Returns:
        主动基金年报 FundDisclosureDocument processor 路由键。

    Raises:
        无显式抛出。
    """

    return FundProcessorDispatchKey(
        fund_type="active_fund",
        report_type="annual_report",
        intermediate_kind="fund_disclosure_document.v1",
        source_kind="annual_report",
        document_year=2025,
        fund_code="004393",
    )


def _provenance() -> PublicSourceProvenance:
    """构造安全默认公共 provenance。

    Args:
        无。

    Returns:
        公共来源 provenance fixture。

    Raises:
        无显式抛出。
    """

    return default_public_source_provenance()


def test_fund_disclosure_intermediate_protocol_accepts_test_local_stub() -> None:
    """验证测试本地 stub 可实现协议且不进入生产模型。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 stub 不满足协议时抛出。
    """

    intermediate = StubDisclosureIntermediate(source_provenance=_provenance())

    assert isinstance(intermediate, FundDisclosureDocumentIntermediate)


def test_candidate_boundary_rejects_candidate_only_false() -> None:
    """验证候选边界不能声明非 candidate-only。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当非法候选边界未被拒绝时抛出。
    """

    with pytest.raises(ValueError, match="candidate_only"):
        CandidateBoundaryStatus(
            candidate_only=False,
            field_correctness_status="not_proven",
            source_truth_status="not_proven",
        )


def test_candidate_boundary_rejects_parser_replacement() -> None:
    """验证候选边界不能授权 parser replacement。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 parser replacement 授权未被拒绝时抛出。
    """

    with pytest.raises(ValueError, match="parser replacement"):
        CandidateBoundaryStatus(
            candidate_only=True,
            field_correctness_status="not_proven",
            source_truth_status="not_proven",
            parser_replacement_authorized=True,
        )


def test_candidate_boundary_rejects_readiness() -> None:
    """验证候选边界不能声明 readiness。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 readiness 声明未被拒绝时抛出。
    """

    with pytest.raises(ValueError, match="readiness"):
        CandidateBoundaryStatus(
            candidate_only=True,
            field_correctness_status="not_proven",
            source_truth_status="not_proven",
            readiness_status="ready",  # type: ignore[arg-type]
        )


@pytest.mark.parametrize(
    "failure_class",
    ("schema_drift", "identity_mismatch", "integrity_error"),
)
def test_fail_closed_failure_class_blocks_candidate_boundary(
    failure_class: AnnualReportSourceFailureCategory,
) -> None:
    """验证结构性失败分类映射到 candidate-only blocked。

    Args:
        failure_class: 年报来源失败分类。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当失败分类映射不符合 fail-closed 契约时抛出。
    """

    decision = admit_disclosure_intermediate(
        StubDisclosureIntermediate(
            source_provenance=_provenance(),
            failure_class=failure_class,
        ),
        _dispatch_key(),
    )

    assert not decision.admitted
    assert decision.gap_code == "candidate_boundary_blocked"
    assert decision.source_boundary == "candidate_only"
    assert decision.contract_status == "blocked"


@pytest.mark.parametrize("failure_class", ("not_found", "unavailable"))
def test_eligible_source_failure_class_is_unsupported_without_processor(
    failure_class: AnnualReportSourceFailureCategory,
) -> None:
    """验证 S3 无具体 processor 时 eligible 失败分类仍为 unsupported。

    Args:
        failure_class: 年报来源失败分类。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 unsupported 映射不正确时抛出。
    """

    decision = admit_disclosure_intermediate(
        StubDisclosureIntermediate(
            source_provenance=_provenance(),
            failure_class=failure_class,
        ),
        _dispatch_key(),
    )

    assert not decision.admitted
    assert decision.gap_code == "unsupported_intermediate"
    assert decision.source_boundary == "unsupported_intermediate"
    assert decision.contract_status == "unsupported"


def test_failure_class_precedes_missing_provenance_and_candidate_boundary() -> None:
    """验证 binding amendment 规定 failure_class 最高优先级。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当分支优先级不符合 controller judgment 时抛出。
    """

    decision = admit_disclosure_intermediate(
        StubDisclosureIntermediate(
            source_provenance=None,
            candidate_boundary=CandidateBoundaryStatus(
                candidate_only=True,
                field_correctness_status="not_proven",
                source_truth_status="not_proven",
            ),
            failure_class="schema_drift",
        ),
        _dispatch_key(),
    )

    assert not decision.admitted
    assert decision.gap_code == "candidate_boundary_blocked"
    assert decision.source_boundary == "candidate_only"
    assert decision.contract_status == "blocked"


def test_missing_provenance_precedes_candidate_boundary() -> None:
    """验证缺失 provenance 比 candidate boundary 更早阻断。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 provenance 缺失未 fail-closed 时抛出。
    """

    decision = admit_disclosure_intermediate(
        StubDisclosureIntermediate(
            source_provenance=None,
            candidate_boundary=CandidateBoundaryStatus(
                candidate_only=True,
                field_correctness_status="not_proven",
                source_truth_status="not_proven",
            ),
        ),
        _dispatch_key(),
    )

    assert not decision.admitted
    assert decision.gap_code == "source_provenance_unsafe"
    assert decision.source_boundary == "source_provenance_unsafe"
    assert decision.contract_status == "blocked"


def test_candidate_boundary_is_admitted_but_blocked_from_promotion() -> None:
    """验证候选中间态可进入 admission 判定但阻断生产提升。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 candidate-only/not_proven 边界被提升时抛出。
    """

    decision = admit_disclosure_intermediate(
        StubDisclosureIntermediate(
            source_provenance=_provenance(),
            candidate_boundary=CandidateBoundaryStatus(
                candidate_only=True,
                field_correctness_status="not_proven",
                source_truth_status="not_proven",
            ),
        ),
        _dispatch_key(),
    )

    assert decision.admitted
    assert decision.gap_code == "candidate_boundary_blocked"
    assert decision.source_boundary == "candidate_only"
    assert decision.contract_status == "blocked"


def test_valid_non_candidate_intermediate_is_satisfied() -> None:
    """验证无失败、非候选且 provenance 存在时 admission satisfied。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当正常中间态未被 admission 接受时抛出。
    """

    decision = admit_disclosure_intermediate(
        StubDisclosureIntermediate(source_provenance=_provenance()),
        _dispatch_key(),
    )

    assert decision.admitted
    assert decision.gap_code is None
    assert decision.source_boundary is None
    assert decision.contract_status == "satisfied"


def test_no_candidate_only_leaks_to_public_evidence_source_kind() -> None:
    """验证 candidate-only 不进入公共 EvidenceAnchor.source_kind。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当公共 source kind 被污染时抛出。
    """

    assert "candidate_only" not in get_args(EvidenceSourceKind)
    assert EvidenceAnchor.__dataclass_fields__["source_kind"].type == "EvidenceSourceKind"


def test_failure_class_map_covers_canonical_categories_and_existing_gap_codes() -> None:
    """验证失败分类映射完整且不引入新 gap code。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当映射缺项或 gap code 不存在时抛出。
    """

    assert set(FAILURE_CLASS_ADMISSION_MAP) == {
        "not_found",
        "unavailable",
        "schema_drift",
        "identity_mismatch",
        "integrity_error",
    }
    known_gap_codes = set(get_args(FundExtractionGapCode))
    used_gap_codes = {entry[0] for entry in FAILURE_CLASS_ADMISSION_MAP.values()}
    assert used_gap_codes <= known_gap_codes
    assert used_gap_codes == {"candidate_boundary_blocked", "unsupported_intermediate"}


def test_admission_helper_source_boundary_imports_stay_isolated() -> None:
    """验证 helper 不导入 Service/UI/Host/Agent/生产文档模型边界。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 helper 出现越界导入时抛出。
    """

    module_path = (
        Path(__file__).parents[3]
        / "fund_agent"
        / "fund"
        / "processors"
        / "fund_disclosure_dispatch.py"
    )
    tree = ast.parse(module_path.read_text(encoding="utf-8"))
    imported_modules = {
        node.module
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module is not None
    }

    forbidden_prefixes = (
        "fund_agent.services",
        "fund_agent.ui",
        "fund_agent.host",
        "fund_agent.agent",
        "fund_agent.fund.documents.models",
    )
    assert not any(module.startswith(forbidden_prefixes) for module in imported_modules)
