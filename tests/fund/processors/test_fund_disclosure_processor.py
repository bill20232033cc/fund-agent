"""FundDisclosureDocument processor 测试。"""

from __future__ import annotations

import ast
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import pytest

from fund_agent.fund.processors.contracts import (
    AnnualReportSourceFailureCategory,
    CandidateBoundaryStatus,
    FundCandidateEvidenceRecord,
    FundDisclosureDocumentContentIntermediate,
    FundDisclosureDocumentIntermediate,
    FundDisclosureSourceTruthAdmissionProof,
    FundExtractionGap,
    FundFieldFamilyResult,
    FundProcessorDispatchKey,
    FundProcessorInput,
    FundProcessorResult,
)
from fund_agent.fund.processors.fund_disclosure_processor import (
    FundDisclosureDocumentProcessor,
)
from fund_agent.fund.processors.registry import FundProcessorRegistry
from fund_agent.fund.source_provenance import (
    PublicSourceProvenance,
    default_public_source_provenance,
)


@dataclass(frozen=True, slots=True)
class _StubIntermediate:
    """测试专用受控文档表示中间态。"""

    document_kind: Literal["annual_report"] = "annual_report"
    fund_code: str = "004393"
    report_year: int = 2025
    intermediate_kind: Literal["fund_disclosure_document.v1"] = "fund_disclosure_document.v1"
    source_provenance: PublicSourceProvenance | None = None
    candidate_boundary: CandidateBoundaryStatus | None = None
    failure_class: AnnualReportSourceFailureCategory | None = None


@dataclass(frozen=True, slots=True)
class _SectionStub:
    """测试专用 section stub。"""

    section_id: str = "section-1"
    heading_text_raw: str = "基金简介"
    heading_text_normalized: str = "基金简介"
    heading_path: tuple[str, ...] = ("基金简介",)
    heading_level: int | None = 1
    locator_stability: str = "stable"


@dataclass(frozen=True, slots=True)
class _ParagraphStub:
    """测试专用 paragraph stub。"""

    block_id: str = "paragraph-1"
    section_id: str | None = "section-1"
    heading_path: tuple[str, ...] = ("基金简介",)
    text_raw: str = "本基金为主动权益基金。"
    text_normalized: str = "本基金为主动权益基金。"
    content_hash: str = "a" * 64
    locator_stability: str = "stable"


@dataclass(frozen=True, slots=True)
class _CellStub:
    """测试专用 table cell stub。"""

    cell_id: str = "cell-1"
    table_id: str = "table-1"
    section_anchor: str | None = "section-1"
    heading_path: tuple[str, ...] = ("基金简介",)
    row_index: int = 0
    column_index: int = 0
    row_label_path: tuple[str, ...] = ("基金名称",)
    column_header_path: tuple[str, ...] = ("项目",)
    cell_text: str = "测试基金"
    cell_text_normalized: str = "测试基金"
    locator_stability: str = "stable"


@dataclass(frozen=True, slots=True)
class _TableStub:
    """测试专用 table stub。"""

    table_id: str = "table-1"
    section_id: str | None = "section-1"
    heading_text: str | None = "基金基本情况"
    heading_path: tuple[str, ...] = ("基金简介",)
    table_caption_or_nearby_heading: str | None = "基金基本情况"
    cells: tuple[_CellStub, ...] = (_CellStub(),)
    locator_stability: str = "stable"


@dataclass(frozen=True, slots=True)
class _ContentIntermediateStub:
    """测试专用带正文结构的中间态。"""

    document_kind: Literal["annual_report"] = "annual_report"
    fund_code: str = "004393"
    report_year: int = 2025
    intermediate_kind: Literal["fund_disclosure_document.v1"] = "fund_disclosure_document.v1"
    source_provenance: PublicSourceProvenance | None = None
    candidate_boundary: CandidateBoundaryStatus | None = None
    failure_class: AnnualReportSourceFailureCategory | None = None
    source_truth_admission: FundDisclosureSourceTruthAdmissionProof | None = None
    sections: tuple[_SectionStub, ...] = (_SectionStub(),)
    paragraph_blocks: tuple[_ParagraphStub, ...] = (_ParagraphStub(),)
    table_blocks: tuple[_TableStub, ...] = (_TableStub(),)


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


def _source_truth_admission_proof(**overrides: object) -> FundDisclosureSourceTruthAdmissionProof:
    """构造 repository-loaded source-truth admission proof fixture。

    Args:
        **overrides: 可选字段覆盖。

    Returns:
        source-truth admission proof。

    Raises:
        ValueError: 字段非法时由契约模型抛出。
    """

    kwargs: dict[str, object] = {
        "proof_kind": "repository_loaded_annual_report_identity.v1",
        "source_boundary": "annual_report",
        "fund_code": "004393",
        "report_year": 2025,
        "document_kind": "annual_report",
        "intermediate_kind": "fund_disclosure_document.v1",
        "source_kind": "annual_report",
        "repository_identity_verified": True,
        "source_provenance_verified": True,
        "locator_identity_verified": True,
        "parser_integrity_verified": True,
        "producer": "FundDocumentRepository",
    }
    kwargs.update(overrides)
    return FundDisclosureSourceTruthAdmissionProof(**kwargs)  # type: ignore[arg-type]


def _dispatch_key(**overrides: object) -> FundProcessorDispatchKey:
    """构造 FundDisclosureDocument processor 路由键。

    Args:
        **overrides: 可选字段覆盖。

    Returns:
        Processor 路由键。

    Raises:
        无显式抛出。
    """

    kwargs: dict[str, object] = {
        "fund_type": "active_fund",
        "report_type": "annual_report",
        "intermediate_kind": "fund_disclosure_document.v1",
        "source_kind": "annual_report",
        "document_year": 2025,
        "fund_code": "004393",
    }
    kwargs.update(overrides)
    return FundProcessorDispatchKey(**kwargs)  # type: ignore[arg-type]


def _stub(**overrides: object) -> _StubIntermediate:
    """构造测试 stub。

    Args:
        **overrides: 可选字段覆盖。

    Returns:
        测试 stub。

    Raises:
        无显式抛出。
    """

    kw: dict[str, object] = {"source_provenance": _provenance()}
    kw.update(overrides)
    return _StubIntermediate(**kw)  # type: ignore[arg-type]


def _candidate_evidence(**overrides: object) -> FundCandidateEvidenceRecord:
    """构造 candidate evidence 记录。

    Args:
        **overrides: 可选字段覆盖。

    Returns:
        candidate-only 证据记录。

    Raises:
        ValueError: 字段非法时由契约模型抛出。
    """

    kwargs: dict[str, object] = {
        "field_family_id": "product_essence.v1",
        "source_boundary": "candidate_only",
        "source_field_path": "sections[0]",
        "section_id": "section-1",
        "table_id": None,
        "block_id": None,
        "cell_id": None,
        "heading_path": ("基金简介",),
        "row_locator": None,
        "excerpt": "候选摘录",
        "locator_stability": "stable",
    }
    kwargs.update(overrides)
    return FundCandidateEvidenceRecord(**kwargs)  # type: ignore[arg-type]


def _missing_gap() -> FundExtractionGap:
    """构造字段族缺失 gap。

    Args:
        无。

    Returns:
        字段族本地缺失 gap。

    Raises:
        无显式抛出。
    """

    return FundExtractionGap(
        gap_code="field_family_missing",
        message="missing",
        field_family_id="product_essence.v1",
        source_field_path=None,
        source_boundary="candidate_only",
        required=True,
    )


def _field_family(
    result: FundProcessorResult,
    field_family_id: str,
) -> FundFieldFamilyResult:
    """按字段族 ID 取结果。

    Args:
        result: processor 结果。
        field_family_id: 字段族 ID。

    Returns:
        匹配的字段族结果。

    Raises:
        AssertionError: 当字段族不存在时抛出。
    """

    for family in result.field_families:
        if family.field_family_id == field_family_id:
            return family
    raise AssertionError(f"field family not found: {field_family_id}")


def _gap_codes(family: FundFieldFamilyResult) -> set[str]:
    """返回字段族 gap code 集合。

    Args:
        family: 字段族结果。

    Returns:
        gap code 集合。

    Raises:
        无显式抛出。
    """

    return {gap.gap_code for gap in family.gaps}


# ── S6-A candidate evidence contract ───────────────────────────────────────


def test_admission_protocol_remains_content_free() -> None:
    """admission 协议不要求 section/table/paragraph 正文集合。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 admission 协议被正文结构污染时抛出。
    """

    intermediate = _stub(source_provenance=_provenance())

    assert isinstance(intermediate, FundDisclosureDocumentIntermediate)
    assert not isinstance(intermediate, FundDisclosureDocumentContentIntermediate)


def test_content_intermediate_protocol_accepts_content_stub() -> None:
    """content 协议只在 admission 字段之外增加正文集合。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 content 协议不能识别结构化正文 stub 时抛出。
    """

    intermediate = _ContentIntermediateStub(source_provenance=_provenance())

    assert isinstance(intermediate, FundDisclosureDocumentIntermediate)
    assert isinstance(intermediate, FundDisclosureDocumentContentIntermediate)


def test_source_truth_admission_requires_positive_proof() -> None:
    """非候选 content FDD 不能只靠 candidate_boundary=None 声明 source truth。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当缺 proof 仍产出 public value 或 anchor 时抛出。
    """

    processor = FundDisclosureDocumentProcessor()

    result = processor.extract(
        FundProcessorInput(
            context=_dispatch_key(),
            intermediate=_ContentIntermediateStub(
                source_provenance=_provenance(),
                candidate_boundary=None,
                source_truth_admission=None,
            ),
        )
    )

    product = _field_family(result, "product_essence.v1")

    assert result.contract_status == "missing"
    assert product.value == {}
    assert product.anchors == ()
    assert "source_truth_admission_missing" in _gap_codes(product)
    assert product.candidate_evidence


def test_source_truth_admission_marks_non_content_intermediate_missing() -> None:
    """非 content FDD 中间态也必须暴露 source-truth admission 缺 proof 诊断。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当非 content FDD 缺 proof 被静默放行时抛出。
    """

    processor = FundDisclosureDocumentProcessor()

    result = processor.extract(
        FundProcessorInput(
            context=_dispatch_key(),
            intermediate=_StubIntermediate(
                source_provenance=_provenance(),
                candidate_boundary=None,
                failure_class=None,
            ),
        )
    )

    product = _field_family(result, "product_essence.v1")

    assert result.contract_status == "missing"
    assert product.status == "missing"
    assert product.value == {}
    assert product.anchors == ()
    assert "source_truth_admission_missing" in _gap_codes(product)


def test_source_truth_admission_rejects_identity_mismatch() -> None:
    """source-truth proof 身份必须与 dispatch/intermediate 同源一致。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 identity mismatch proof 被接受时抛出。
    """

    processor = FundDisclosureDocumentProcessor()

    result = processor.extract(
        FundProcessorInput(
            context=_dispatch_key(),
            intermediate=_ContentIntermediateStub(
                source_provenance=_provenance(),
                source_truth_admission=_source_truth_admission_proof(fund_code="110011"),
            ),
        )
    )

    product = _field_family(result, "product_essence.v1")

    assert result.contract_status == "missing"
    assert product.value == {}
    assert product.anchors == ()
    assert "source_truth_admission_invalid" in _gap_codes(product)


def test_source_truth_admission_accepts_repository_loaded_identity_proof() -> None:
    """repository-loaded identity proof 可通过 Slice A admission guard。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当匹配 proof 仍被 source-truth guard 拦截时抛出。
    """

    processor = FundDisclosureDocumentProcessor()

    result = processor.extract(
        FundProcessorInput(
            context=_dispatch_key(),
            intermediate=_ContentIntermediateStub(
                source_provenance=_provenance(),
                source_truth_admission=_source_truth_admission_proof(),
            ),
        )
    )

    product = _field_family(result, "product_essence.v1")

    assert result.contract_status == "missing"
    assert product.value == {}
    assert product.anchors == ()
    assert "source_truth_admission_missing" not in _gap_codes(product)
    assert "source_truth_admission_invalid" not in _gap_codes(product)
    assert product.candidate_evidence


@pytest.mark.parametrize(
    ("field_name", "bad_value", "message"),
    (
        ("source_boundary", "annual_report", "source_boundary"),
        ("candidate_only", False, "candidate_only"),
        ("field_correctness_status", "proven", "field correctness"),
        ("source_truth_status", "proven", "source truth"),
        ("parser_replacement_authorized", True, "parser replacement"),
        ("readiness_status", "ready", "readiness"),
        ("source_field_path", "", "source_field_path"),
        ("excerpt", "", "excerpt"),
    ),
)
def test_candidate_evidence_record_rejects_unsafe_boundary_fields(
    field_name: str,
    bad_value: object,
    message: str,
) -> None:
    """candidate evidence 拒绝 proof/source-truth/readiness 逃逸。

    Args:
        field_name: 被覆盖字段名。
        bad_value: 非法字段值。
        message: 预期错误消息片段。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当非法 candidate evidence 被接受时抛出。
    """

    with pytest.raises(ValueError, match=message):
        _candidate_evidence(**{field_name: bad_value})


def test_candidate_evidence_record_requires_locator_identity() -> None:
    """candidate evidence 至少需要一个 locator identity。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当无定位证据被接受时抛出。
    """

    with pytest.raises(ValueError, match="locator identity"):
        _candidate_evidence(section_id=None, table_id=None, block_id=None, cell_id=None)


def test_missing_field_family_can_carry_candidate_evidence_without_value_leak() -> None:
    """missing 字段族可携带 candidate_evidence，但不得写入 value。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 candidate evidence 泄漏到 public value 时抛出。
    """

    record = _candidate_evidence()

    family = FundFieldFamilyResult(
        field_family_id="product_essence.v1",
        chapter_ids=(1,),
        value={},
        status="missing",
        extraction_mode="missing",
        anchors=(),
        gaps=(_missing_gap(),),
        source_provenance=_provenance(),
        candidate_evidence=(record,),
    )

    assert family.status == "missing"
    assert family.value == {}
    assert family.anchors == ()
    assert family.candidate_evidence == (record,)


def test_candidate_evidence_does_not_satisfy_partial_anchor_requirement() -> None:
    """candidate evidence 不能替代 partial 字段族的 public EvidenceAnchor。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 partial 无 public anchor 仍被接受时抛出。
    """

    with pytest.raises(ValueError, match="EvidenceAnchor"):
        FundFieldFamilyResult(
            field_family_id="product_essence.v1",
            chapter_ids=(1,),
            value={},
            status="partial",
            extraction_mode="direct",
            anchors=(),
            gaps=(),
            source_provenance=_provenance(),
            candidate_evidence=(_candidate_evidence(),),
        )


# ── S6-B product essence candidate selector ────────────────────────────────


def test_product_essence_selector_adds_candidate_evidence_only() -> None:
    """product_essence selector 只填 candidate_evidence，不填 public value/anchor。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当候选证据泄漏到 public 字段时抛出。
    """

    processor = FundDisclosureDocumentProcessor()

    result = processor.extract(
        FundProcessorInput(
            context=_dispatch_key(),
            intermediate=_ContentIntermediateStub(source_provenance=_provenance()),
        )
    )

    product = _field_family(result, "product_essence.v1")
    paths = {record.source_field_path for record in product.candidate_evidence}

    assert result.contract_status == "missing"
    assert product.status == "missing"
    assert product.extraction_mode == "missing"
    assert product.value == {}
    assert product.anchors == ()
    assert product.gaps[0].gap_code == "candidate_only_not_source_truth"
    assert "sections[0]" in paths
    assert "table_blocks[0]" in paths
    assert "table_blocks[0].cells[0]" in paths
    for record in product.candidate_evidence:
        assert record.candidate_only
        assert record.source_boundary == "candidate_only"
        assert record.field_correctness_status == "not_proven"
        assert record.source_truth_status == "not_proven"
        assert not record.parser_replacement_authorized
        assert record.readiness_status == "not_ready"
        assert record.source_field_path not in product.value


def test_product_essence_selector_leaves_other_families_without_candidate_evidence() -> None:
    """S6-B 不为其它五个字段族生成 candidate evidence。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 selector 越界到其它字段族时抛出。
    """

    processor = FundDisclosureDocumentProcessor()

    result = processor.extract(
        FundProcessorInput(
            context=_dispatch_key(),
            intermediate=_ContentIntermediateStub(source_provenance=_provenance()),
        )
    )

    for family in result.field_families:
        if family.field_family_id == "product_essence.v1":
            continue
        assert family.status == "missing"
        assert family.value == {}
        assert family.anchors == ()
        assert family.candidate_evidence == ()
        assert family.gaps[0].gap_code == "field_family_missing"


def test_product_essence_selector_no_match_keeps_field_family_missing() -> None:
    """非匹配正文不产生 candidate evidence，保留 field_family_missing。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当无关正文被误命中时抛出。
    """

    processor = FundDisclosureDocumentProcessor()
    section = _SectionStub(
        heading_text_raw="其他章节",
        heading_text_normalized="其他章节",
        heading_path=("其他章节",),
    )
    paragraph = _ParagraphStub(
        heading_path=("其他章节",),
        text_raw="无关内容",
        text_normalized="无关内容",
    )
    cell = _CellStub(
        heading_path=("其他章节",),
        row_label_path=("其他",),
        column_header_path=("其他",),
        cell_text="无关",
        cell_text_normalized="无关",
    )
    table = _TableStub(
        heading_text="其他表格",
        table_caption_or_nearby_heading="其他表格",
        heading_path=("其他章节",),
        cells=(cell,),
    )

    result = processor.extract(
        FundProcessorInput(
            context=_dispatch_key(),
            intermediate=_ContentIntermediateStub(
                source_provenance=_provenance(),
                sections=(section,),
                paragraph_blocks=(paragraph,),
                table_blocks=(table,),
            ),
        )
    )

    product = _field_family(result, "product_essence.v1")

    assert product.candidate_evidence == ()
    assert product.status == "missing"
    assert product.value == {}
    assert product.anchors == ()
    assert product.gaps[0].gap_code == "field_family_missing"


def test_product_essence_selector_preserves_candidate_boundary_blocked_status() -> None:
    """candidate_boundary 输入即使有 candidate evidence，整体仍 blocked。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 candidate evidence 提升 consumption status 时抛出。
    """

    processor = FundDisclosureDocumentProcessor()
    boundary = CandidateBoundaryStatus(
        candidate_only=True,
        field_correctness_status="not_proven",
        source_truth_status="not_proven",
    )

    result = processor.extract(
        FundProcessorInput(
            context=_dispatch_key(),
            intermediate=_ContentIntermediateStub(
                source_provenance=_provenance(),
                candidate_boundary=boundary,
            ),
        )
    )

    product = _field_family(result, "product_essence.v1")

    assert result.contract_status == "blocked"
    assert result.candidate_boundary is boundary
    assert product.candidate_evidence
    assert product.value == {}
    assert product.anchors == ()


# ── S6-C return attribution candidate selector ─────────────────────────────


def test_return_attribution_selector_adds_candidate_evidence_only() -> None:
    """return_attribution selector 只填 candidate_evidence，不填 public value/anchor。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当候选证据泄漏到 public 字段时抛出。
    """

    processor = FundDisclosureDocumentProcessor()
    section = _SectionStub(
        heading_text_raw="基金净值表现",
        heading_text_normalized="基金净值表现",
        heading_path=("基金净值表现",),
    )
    paragraph = _ParagraphStub(
        block_id="paragraph-fee",
        section_id="section-fee",
        heading_path=("费用",),
        text_raw="基金管理费按前一日基金资产净值的一定年费率计提。",
        text_normalized="基金管理费按前一日基金资产净值的一定年费率计提。",
    )
    cell = _CellStub(
        cell_id="cell-tracking",
        table_id="table-tracking",
        section_anchor="section-tracking",
        heading_path=("跟踪误差",),
        row_label_path=("年化跟踪误差",),
        column_header_path=("项目",),
        cell_text="年化跟踪误差",
        cell_text_normalized="年化跟踪误差",
    )
    table = _TableStub(
        table_id="table-tracking",
        section_id="section-tracking",
        heading_text="跟踪误差说明",
        table_caption_or_nearby_heading="跟踪误差说明",
        heading_path=("跟踪误差",),
        cells=(cell,),
    )

    result = processor.extract(
        FundProcessorInput(
            context=_dispatch_key(),
            intermediate=_ContentIntermediateStub(
                source_provenance=_provenance(),
                sections=(section,),
                paragraph_blocks=(paragraph,),
                table_blocks=(table,),
            ),
        )
    )

    family = _field_family(result, "return_attribution.v1")
    paths = {record.source_field_path for record in family.candidate_evidence}

    assert family.status == "missing"
    assert family.extraction_mode == "missing"
    assert family.value == {}
    assert family.anchors == ()
    assert family.gaps[0].gap_code == "candidate_only_not_source_truth"
    assert "sections[0]" in paths
    assert "paragraph_blocks[0]" in paths
    assert "table_blocks[0]" in paths
    assert "table_blocks[0].cells[0]" in paths


def test_return_attribution_selector_preserves_candidate_boundary_fields() -> None:
    """return_attribution candidate records 固定保持 not_proven/not_ready。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当候选边界字段被提升时抛出。
    """

    processor = FundDisclosureDocumentProcessor()
    section = _SectionStub(
        heading_text_raw="业绩比较基准收益率",
        heading_text_normalized="业绩比较基准收益率",
        heading_path=("业绩比较基准收益率",),
    )

    result = processor.extract(
        FundProcessorInput(
            context=_dispatch_key(),
            intermediate=_ContentIntermediateStub(
                source_provenance=_provenance(),
                sections=(section,),
                paragraph_blocks=(),
                table_blocks=(),
            ),
        )
    )

    family = _field_family(result, "return_attribution.v1")

    assert family.candidate_evidence
    for record in family.candidate_evidence:
        assert record.field_family_id == "return_attribution.v1"
        assert record.candidate_only
        assert record.source_boundary == "candidate_only"
        assert record.field_correctness_status == "not_proven"
        assert record.source_truth_status == "not_proven"
        assert not record.parser_replacement_authorized
        assert record.readiness_status == "not_ready"
        assert record.source_field_path not in family.value


def test_return_attribution_selector_keeps_other_unimplemented_families_without_candidate_evidence() -> None:
    """S6-C 不为其它未实现字段族生成 candidate evidence。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 selector 越界到其它字段族时抛出。
    """

    processor = FundDisclosureDocumentProcessor()
    section = _SectionStub(
        heading_text_raw="基金份额净值增长率",
        heading_text_normalized="基金份额净值增长率",
        heading_path=("基金份额净值增长率",),
    )

    result = processor.extract(
        FundProcessorInput(
            context=_dispatch_key(),
            intermediate=_ContentIntermediateStub(
                source_provenance=_provenance(),
                sections=(section,),
                paragraph_blocks=(),
                table_blocks=(),
            ),
        )
    )

    product = _field_family(result, "product_essence.v1")
    assert product.candidate_evidence == ()
    assert product.gaps[0].gap_code == "field_family_missing"

    for family_id in (
        "manager_profile.v1",
        "investor_experience.v1",
        "current_stage.v1",
        "core_risk.v1",
    ):
        family = _field_family(result, family_id)
        assert family.status == "missing"
        assert family.value == {}
        assert family.anchors == ()
        assert family.candidate_evidence == ()
        assert family.gaps[0].gap_code == "field_family_missing"


def test_return_attribution_selector_no_match_keeps_field_family_missing() -> None:
    """非匹配正文不产生 return_attribution candidate evidence。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当无关正文被误命中时抛出。
    """

    processor = FundDisclosureDocumentProcessor()
    section = _SectionStub(
        heading_text_raw="其他章节",
        heading_text_normalized="其他章节",
        heading_path=("其他章节",),
    )
    paragraph = _ParagraphStub(
        heading_path=("其他章节",),
        text_raw="无关内容",
        text_normalized="无关内容",
    )
    cell = _CellStub(
        heading_path=("其他章节",),
        row_label_path=("其他",),
        column_header_path=("其他",),
        cell_text="无关",
        cell_text_normalized="无关",
    )
    table = _TableStub(
        heading_text="其他表格",
        table_caption_or_nearby_heading="其他表格",
        heading_path=("其他章节",),
        cells=(cell,),
    )

    result = processor.extract(
        FundProcessorInput(
            context=_dispatch_key(),
            intermediate=_ContentIntermediateStub(
                source_provenance=_provenance(),
                sections=(section,),
                paragraph_blocks=(paragraph,),
                table_blocks=(table,),
            ),
        )
    )

    family = _field_family(result, "return_attribution.v1")

    assert family.candidate_evidence == ()
    assert family.status == "missing"
    assert family.value == {}
    assert family.anchors == ()
    assert family.gaps[0].gap_code == "field_family_missing"


def test_return_attribution_selector_preserves_candidate_boundary_blocked_status() -> None:
    """candidate_boundary 输入即使有 return candidate evidence，整体仍 blocked。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 candidate evidence 提升 consumption status 时抛出。
    """

    processor = FundDisclosureDocumentProcessor()
    boundary = CandidateBoundaryStatus(
        candidate_only=True,
        field_correctness_status="not_proven",
        source_truth_status="not_proven",
    )
    section = _SectionStub(
        heading_text_raw="基准收益率",
        heading_text_normalized="基准收益率",
        heading_path=("基准收益率",),
    )

    result = processor.extract(
        FundProcessorInput(
            context=_dispatch_key(),
            intermediate=_ContentIntermediateStub(
                source_provenance=_provenance(),
                candidate_boundary=boundary,
                sections=(section,),
                paragraph_blocks=(),
                table_blocks=(),
            ),
        )
    )

    family = _field_family(result, "return_attribution.v1")

    assert result.contract_status == "blocked"
    assert result.candidate_boundary is boundary
    assert family.candidate_evidence
    assert family.value == {}
    assert family.anchors == ()


def test_return_attribution_selector_orders_dedupes_limits_and_truncates() -> None:
    """return_attribution selector 保持 role/source 顺序、去重和 12 条限量。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 source path、顺序、去重或限量不符合 S6-C 时抛出。
    """

    processor = FundDisclosureDocumentProcessor()
    long_nav_text = "基金份额净值增长率" + "明细" * 100
    sections = (
        _SectionStub(
            section_id="section-nav-0",
            heading_text_raw=long_nav_text,
            heading_text_normalized=long_nav_text,
            heading_path=(long_nav_text,),
        ),
        _SectionStub(
            section_id="section-nav-fee",
            heading_text_raw="基金份额净值增长率与基金管理费",
            heading_text_normalized="基金份额净值增长率与基金管理费",
            heading_path=("基金份额净值增长率与基金管理费",),
        ),
    )
    paragraphs = tuple(
        _ParagraphStub(
            block_id=f"paragraph-nav-{index}",
            section_id=f"section-nav-{index + 2}",
            heading_path=("基金净值表现",),
            text_raw=f"第{index}段披露基金净值表现。",
            text_normalized=f"第{index}段披露基金净值表现。",
        )
        for index in range(3)
    )
    cells = (
        _CellStub(
            cell_id="cell-original-0",
            row_index=2,
            column_index=0,
            row_label_path=("净值增长率",),
            cell_text="净值增长率",
            cell_text_normalized="净值增长率",
        ),
        _CellStub(
            cell_id="cell-original-1",
            row_index=0,
            column_index=0,
            row_label_path=("业绩比较基准收益率",),
            cell_text="业绩比较基准收益率",
            cell_text_normalized="业绩比较基准收益率",
        ),
        _CellStub(
            cell_id="cell-original-2",
            row_index=1,
            column_index=0,
            row_label_path=("基准收益率",),
            cell_text="基准收益率",
            cell_text_normalized="基准收益率",
        ),
    )
    nav_table = _TableStub(
        table_id="table-nav",
        section_id="section-table-nav",
        heading_text="基金净值表现",
        table_caption_or_nearby_heading="基金净值表现",
        heading_path=("基金净值表现",),
        cells=cells,
    )
    fee_paragraphs = tuple(
        _ParagraphStub(
            block_id=f"paragraph-fee-{index}",
            section_id=f"section-fee-{index}",
            heading_path=("基金费用",),
            text_raw=f"第{index}段披露基金管理费。",
            text_normalized=f"第{index}段披露基金管理费。",
        )
        for index in range(6)
    )

    result = processor.extract(
        FundProcessorInput(
            context=_dispatch_key(),
            intermediate=_ContentIntermediateStub(
                source_provenance=_provenance(),
                sections=sections,
                paragraph_blocks=paragraphs + fee_paragraphs,
                table_blocks=(nav_table,),
            ),
        )
    )

    records = _field_family(result, "return_attribution.v1").candidate_evidence
    paths = [record.source_field_path for record in records]

    assert len(records) == 12
    assert paths == [
        "sections[0]",
        "sections[1]",
        "paragraph_blocks[0]",
        "paragraph_blocks[1]",
        "paragraph_blocks[2]",
        "table_blocks[0]",
        "table_blocks[0].cells[1]",
        "table_blocks[0].cells[2]",
        "table_blocks[0].cells[0]",
        "paragraph_blocks[3]",
        "paragraph_blocks[4]",
        "paragraph_blocks[5]",
    ]
    assert len(set(paths)) == len(paths)
    assert records[0].row_locator == "role=nav_benchmark_performance; locator=section_id=section-nav-0"
    assert records[1].row_locator == "role=nav_benchmark_performance; locator=section_id=section-nav-fee"
    assert all(len(record.excerpt) <= 160 for record in records)
    assert all(record.field_family_id == "return_attribution.v1" for record in records)


# ── S6-D manager profile candidate selector ────────────────────────────────


def test_manager_profile_selector_adds_candidate_evidence_only() -> None:
    """manager_profile selector 只填 candidate_evidence，不填 public value/anchor。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当候选证据泄漏到 public 字段时抛出。
    """

    processor = FundDisclosureDocumentProcessor()
    section = _SectionStub(
        section_id="section-manager",
        heading_text_raw="基金管理人及基金经理情况",
        heading_text_normalized="基金管理人及基金经理情况",
        heading_path=("基金管理人及基金经理情况",),
    )
    strategy = _ParagraphStub(
        block_id="paragraph-strategy",
        section_id="section-strategy",
        heading_path=("投资策略和运作分析",),
        text_raw="报告期内基金投资策略和运作分析。",
        text_normalized="报告期内基金投资策略和运作分析。",
    )
    alignment = _ParagraphStub(
        block_id="paragraph-alignment",
        section_id="section-alignment",
        heading_path=("基金管理人持有情况",),
        text_raw="基金管理人从业人员持有本基金。",
        text_normalized="基金管理人从业人员持有本基金。",
    )
    turnover_table = _TableStub(
        table_id="table-turnover",
        section_id="section-turnover",
        heading_text="报告期内股票换手率",
        table_caption_or_nearby_heading="报告期内股票换手率",
        heading_path=("交易情况",),
        cells=(),
    )
    holdings_table = _TableStub(
        table_id="table-holdings",
        section_id="section-holdings",
        heading_text="前十名股票投资明细",
        table_caption_or_nearby_heading="前十名股票投资明细",
        heading_path=("投资组合",),
        cells=(),
    )

    result = processor.extract(
        FundProcessorInput(
            context=_dispatch_key(),
            intermediate=_ContentIntermediateStub(
                source_provenance=_provenance(),
                sections=(section,),
                paragraph_blocks=(strategy, alignment),
                table_blocks=(turnover_table, holdings_table),
            ),
        )
    )

    family = _field_family(result, "manager_profile.v1")
    roles = {record.row_locator.split(";")[0] for record in family.candidate_evidence}

    assert family.status == "missing"
    assert family.extraction_mode == "missing"
    assert family.value == {}
    assert family.anchors == ()
    assert family.gaps[0].gap_code == "candidate_only_not_source_truth"
    assert roles == {
        "role=portfolio_managers",
        "role=manager_strategy_text",
        "role=turnover_rate",
        "role=manager_alignment",
        "role=holdings_snapshot",
    }


def test_manager_profile_selector_preserves_candidate_boundary_fields() -> None:
    """manager_profile candidate records 固定保持 candidate-only/not_proven/not_ready。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当候选边界字段被提升时抛出。
    """

    processor = FundDisclosureDocumentProcessor()
    section = _SectionStub(
        section_id="section-manager",
        heading_text_raw="基金经理简介",
        heading_text_normalized="基金经理简介",
        heading_path=("基金经理简介",),
    )

    result = processor.extract(
        FundProcessorInput(
            context=_dispatch_key(),
            intermediate=_ContentIntermediateStub(
                source_provenance=_provenance(),
                sections=(section,),
                paragraph_blocks=(),
                table_blocks=(),
            ),
        )
    )

    family = _field_family(result, "manager_profile.v1")

    assert family.candidate_evidence
    for record in family.candidate_evidence:
        assert record.field_family_id == "manager_profile.v1"
        assert record.candidate_only
        assert record.source_boundary == "candidate_only"
        assert record.field_correctness_status == "not_proven"
        assert record.source_truth_status == "not_proven"
        assert not record.parser_replacement_authorized
        assert record.readiness_status == "not_ready"
        assert record.source_field_path not in family.value


def test_manager_profile_selector_keeps_other_remaining_families_without_candidate_evidence() -> None:
    """S6-D 不为未授权字段族生成 candidate evidence。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 selector 越界到其它字段族时抛出。
    """

    processor = FundDisclosureDocumentProcessor()
    section = _SectionStub(
        section_id="section-manager",
        heading_text_raw="基金经理情况",
        heading_text_normalized="基金经理情况",
        heading_path=("基金经理情况",),
    )

    result = processor.extract(
        FundProcessorInput(
            context=_dispatch_key(),
            intermediate=_ContentIntermediateStub(
                source_provenance=_provenance(),
                sections=(section,),
                paragraph_blocks=(),
                table_blocks=(),
            ),
        )
    )

    for family_id in ("product_essence.v1", "return_attribution.v1"):
        family = _field_family(result, family_id)
        assert family.candidate_evidence == ()
        assert family.gaps[0].gap_code == "field_family_missing"

    for family_id in ("investor_experience.v1", "current_stage.v1", "core_risk.v1"):
        family = _field_family(result, family_id)
        assert family.status == "missing"
        assert family.value == {}
        assert family.anchors == ()
        assert family.candidate_evidence == ()
        assert family.gaps[0].gap_code == "field_family_missing"


def test_manager_profile_selector_no_match_keeps_field_family_missing() -> None:
    """非匹配正文不产生 manager_profile candidate evidence。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当无关正文被误命中时抛出。
    """

    processor = FundDisclosureDocumentProcessor()
    section = _SectionStub(
        heading_text_raw="其他章节",
        heading_text_normalized="其他章节",
        heading_path=("其他章节",),
    )
    paragraph = _ParagraphStub(
        heading_path=("其他章节",),
        text_raw="无关内容",
        text_normalized="无关内容",
    )
    cell = _CellStub(
        heading_path=("其他章节",),
        row_label_path=("其他",),
        column_header_path=("其他",),
        cell_text="无关",
        cell_text_normalized="无关",
    )
    table = _TableStub(
        heading_text="其他表格",
        table_caption_or_nearby_heading="其他表格",
        heading_path=("其他章节",),
        cells=(cell,),
    )

    result = processor.extract(
        FundProcessorInput(
            context=_dispatch_key(),
            intermediate=_ContentIntermediateStub(
                source_provenance=_provenance(),
                sections=(section,),
                paragraph_blocks=(paragraph,),
                table_blocks=(table,),
            ),
        )
    )

    family = _field_family(result, "manager_profile.v1")

    assert family.candidate_evidence == ()
    assert family.status == "missing"
    assert family.value == {}
    assert family.anchors == ()
    assert family.gaps[0].gap_code == "field_family_missing"


def test_manager_profile_selector_preserves_candidate_boundary_blocked_status() -> None:
    """candidate_boundary 输入即使有 manager candidate evidence，整体仍 blocked。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 candidate evidence 提升 consumption status 时抛出。
    """

    processor = FundDisclosureDocumentProcessor()
    boundary = CandidateBoundaryStatus(
        candidate_only=True,
        field_correctness_status="not_proven",
        source_truth_status="not_proven",
    )
    section = _SectionStub(
        section_id="section-manager",
        heading_text_raw="主要人员情况",
        heading_text_normalized="主要人员情况",
        heading_path=("主要人员情况",),
    )

    result = processor.extract(
        FundProcessorInput(
            context=_dispatch_key(),
            intermediate=_ContentIntermediateStub(
                source_provenance=_provenance(),
                candidate_boundary=boundary,
                sections=(section,),
                paragraph_blocks=(),
                table_blocks=(),
            ),
        )
    )

    family = _field_family(result, "manager_profile.v1")

    assert result.contract_status == "blocked"
    assert result.candidate_boundary is boundary
    assert family.candidate_evidence
    assert family.value == {}
    assert family.anchors == ()


def test_manager_profile_selector_orders_dedupes_limits_and_truncates() -> None:
    """manager_profile selector 保持 role/source 顺序、去重和 16 条限量。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 source path、顺序、去重或限量不符合 S6-D 时抛出。
    """

    processor = FundDisclosureDocumentProcessor()
    long_heading = "基金经理简介" + "明细" * 100
    section = _SectionStub(
        section_id="section-manager",
        heading_text_raw=long_heading,
        heading_text_normalized=long_heading,
        heading_path=(long_heading,),
    )
    portfolio_paragraphs = tuple(
        _ParagraphStub(
            block_id=f"paragraph-manager-{index}",
            section_id=f"section-manager-{index}",
            heading_path=("基金经理情况",),
            text_raw=text,
            text_normalized=text,
        )
        for index, text in enumerate(("姓名", "职务"))
    )
    strategy_paragraphs = tuple(
        _ParagraphStub(
            block_id=f"paragraph-strategy-{index}",
            section_id=f"section-strategy-{index}",
            heading_path=("投资策略和运作分析",),
            text_raw=f"第{index}段披露投资策略和运作分析。",
            text_normalized=f"第{index}段披露投资策略和运作分析。",
        )
        for index in range(3)
    )
    turnover_paragraphs = tuple(
        _ParagraphStub(
            block_id=f"paragraph-turnover-{index}",
            section_id=f"section-turnover-{index}",
            heading_path=("换手率",),
            text_raw=f"第{index}段披露换手率。",
            text_normalized=f"第{index}段披露换手率。",
        )
        for index in range(3)
    )
    alignment_paragraphs = tuple(
        _ParagraphStub(
            block_id=f"paragraph-alignment-{index}",
            section_id=f"section-alignment-{index}",
            heading_path=("持有情况",),
            text_raw=f"第{index}段披露基金经理持有情况。",
            text_normalized=f"第{index}段披露基金经理持有情况。",
        )
        for index in range(4)
    )
    cells = (
        _CellStub(
            cell_id="cell-original-0",
            row_index=2,
            column_index=0,
            column_header_path=("任职日期",),
            cell_text="2020-01-01",
            cell_text_normalized="2020-01-01",
        ),
        _CellStub(
            cell_id="cell-original-1",
            row_index=0,
            column_index=0,
            column_header_path=("姓名",),
            cell_text="张三",
            cell_text_normalized="张三",
        ),
        _CellStub(
            cell_id="cell-original-2",
            row_index=1,
            column_index=0,
            column_header_path=("职务",),
            cell_text="基金经理",
            cell_text_normalized="基金经理",
        ),
    )
    table = _TableStub(
        table_id="table-manager",
        section_id="section-manager-table",
        heading_text="基金经理情况",
        table_caption_or_nearby_heading="基金经理情况",
        heading_path=("基金经理情况",),
        cells=cells,
    )

    result = processor.extract(
        FundProcessorInput(
            context=_dispatch_key(),
            intermediate=_ContentIntermediateStub(
                source_provenance=_provenance(),
                sections=(section,),
                paragraph_blocks=(
                    *portfolio_paragraphs,
                    *strategy_paragraphs,
                    *turnover_paragraphs,
                    *alignment_paragraphs,
                ),
                table_blocks=(table,),
            ),
        )
    )

    records = _field_family(result, "manager_profile.v1").candidate_evidence
    paths = [record.source_field_path for record in records]

    assert len(records) == 16
    assert paths == [
        "sections[0]",
        "paragraph_blocks[0]",
        "paragraph_blocks[1]",
        "table_blocks[0]",
        "table_blocks[0].cells[1]",
        "table_blocks[0].cells[2]",
        "table_blocks[0].cells[0]",
        "paragraph_blocks[2]",
        "paragraph_blocks[3]",
        "paragraph_blocks[4]",
        "paragraph_blocks[5]",
        "paragraph_blocks[6]",
        "paragraph_blocks[7]",
        "paragraph_blocks[8]",
        "paragraph_blocks[9]",
        "paragraph_blocks[10]",
    ]
    assert "paragraph_blocks[11]" not in paths
    assert len(set(paths)) == len(paths)
    assert records[0].row_locator == "role=portfolio_managers; locator=section_id=section-manager"
    assert records[13].row_locator == "role=manager_alignment; locator=block_id=paragraph-alignment-0"
    assert all(len(record.excerpt) <= 160 for record in records)
    assert all(record.field_family_id == "manager_profile.v1" for record in records)


def test_manager_profile_selector_requires_context_for_generic_roster_and_holding_tokens() -> None:
    """generic roster/holding token 缺少 context 时不得产生 manager_profile evidence。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 generic token 绕过 guard 时抛出。
    """

    processor = FundDisclosureDocumentProcessor()
    section = _SectionStub(
        heading_text_raw="姓名",
        heading_text_normalized="姓名",
        heading_path=("姓名",),
    )
    paragraph = _ParagraphStub(
        heading_path=("人员信息",),
        text_raw="职务",
        text_normalized="职务",
    )
    cells = (
        _CellStub(
            cell_id="cell-roster",
            row_index=0,
            column_index=0,
            row_label_path=("人员",),
            column_header_path=("任职日期",),
            cell_text="2020-01-01",
            cell_text_normalized="2020-01-01",
        ),
        _CellStub(
            cell_id="cell-holding",
            row_index=1,
            column_index=0,
            row_label_path=("持有本基金",),
            column_header_path=("份额",),
            cell_text="持有本基金",
            cell_text_normalized="持有本基金",
        ),
    )
    table = _TableStub(
        heading_text="人员清单",
        table_caption_or_nearby_heading="人员清单",
        heading_path=("人员清单",),
        cells=cells,
    )

    result = processor.extract(
        FundProcessorInput(
            context=_dispatch_key(),
            intermediate=_ContentIntermediateStub(
                source_provenance=_provenance(),
                sections=(section,),
                paragraph_blocks=(paragraph,),
                table_blocks=(table,),
            ),
        )
    )

    family = _field_family(result, "manager_profile.v1")

    assert family.candidate_evidence == ()
    assert family.gaps[0].gap_code == "field_family_missing"


def test_manager_profile_selector_allows_generic_tokens_with_context() -> None:
    """generic token 带 controller 指定 context 时可产生 candidate evidence。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当正向 guard context 被过度阻断时抛出。
    """

    processor = FundDisclosureDocumentProcessor()
    roster_cells = (
        _CellStub(
            cell_id="cell-name",
            row_index=0,
            column_index=0,
            column_header_path=("姓名",),
            cell_text="张三",
            cell_text_normalized="张三",
        ),
        _CellStub(
            cell_id="cell-role",
            row_index=0,
            column_index=1,
            column_header_path=("职务",),
            cell_text="基金经理",
            cell_text_normalized="基金经理",
        ),
        _CellStub(
            cell_id="cell-date",
            row_index=0,
            column_index=2,
            column_header_path=("任职日期",),
            cell_text="2020-01-01",
            cell_text_normalized="2020-01-01",
        ),
    )
    roster_table = _TableStub(
        table_id="table-roster",
        section_id="section-manager",
        heading_text="基金经理情况",
        table_caption_or_nearby_heading="基金经理情况",
        heading_path=("基金管理人及基金经理情况",),
        cells=roster_cells,
    )
    holding_cell = _CellStub(
        cell_id="cell-holding",
        table_id="table-holding",
        row_index=0,
        column_index=0,
        row_label_path=("基金管理人从业人员",),
        column_header_path=("持有本基金",),
        cell_text="持有本基金",
        cell_text_normalized="持有本基金",
    )
    holding_table = _TableStub(
        table_id="table-holding",
        section_id="section-holding",
        heading_text="基金管理人持有情况",
        table_caption_or_nearby_heading="基金管理人持有情况",
        heading_path=("基金管理人持有情况",),
        cells=(holding_cell,),
    )

    result = processor.extract(
        FundProcessorInput(
            context=_dispatch_key(),
            intermediate=_ContentIntermediateStub(
                source_provenance=_provenance(),
                sections=(),
                paragraph_blocks=(),
                table_blocks=(roster_table, holding_table),
            ),
        )
    )

    family = _field_family(result, "manager_profile.v1")
    paths_by_role = {
        record.source_field_path: record.row_locator.split(";")[0]
        for record in family.candidate_evidence
    }

    assert paths_by_role["table_blocks[0].cells[0]"] == "role=portfolio_managers"
    assert paths_by_role["table_blocks[0].cells[1]"] == "role=portfolio_managers"
    assert paths_by_role["table_blocks[0].cells[2]"] == "role=portfolio_managers"
    assert paths_by_role["table_blocks[1].cells[0]"] == "role=manager_alignment"
    assert family.status == "missing"
    assert family.extraction_mode == "missing"
    assert family.value == {}
    assert family.anchors == ()


# ── S6-E investor experience candidate selector ────────────────────────────


def test_investor_experience_selector_adds_candidate_evidence_only() -> None:
    """investor_experience selector 只填 candidate_evidence，不填 public value/anchor。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当候选证据泄漏到 public 字段时抛出。
    """

    processor = FundDisclosureDocumentProcessor()
    investor_section = _SectionStub(
        section_id="section-investor-return",
        heading_text_raw="投资者实际收益",
        heading_text_normalized="投资者实际收益",
        heading_path=("投资者实际收益",),
    )
    holder_section = _SectionStub(
        section_id="section-holder",
        heading_text_raw="基金份额持有人结构",
        heading_text_normalized="基金份额持有人结构",
        heading_path=("基金份额持有人结构",),
    )
    share_paragraph = _ParagraphStub(
        block_id="paragraph-share-change",
        section_id="section-share",
        heading_path=("基金份额变动",),
        text_raw="基金份额变动情况。",
        text_normalized="基金份额变动情况。",
    )
    subscription_cell = _CellStub(
        cell_id="cell-subscription",
        table_id="table-subscription",
        section_anchor="section-subscription",
        heading_path=("申购赎回",),
        row_label_path=("基金总申购份额",),
        column_header_path=("项目",),
        cell_text="总申购份额",
        cell_text_normalized="总申购份额",
    )
    subscription_table = _TableStub(
        table_id="table-subscription",
        section_id="section-subscription",
        heading_text="申购赎回",
        table_caption_or_nearby_heading="申购赎回",
        heading_path=("申购赎回",),
        cells=(subscription_cell,),
    )
    distribution_table = _TableStub(
        table_id="table-distribution",
        section_id="section-distribution",
        heading_text="基金收益分配",
        table_caption_or_nearby_heading="基金收益分配",
        heading_path=("基金收益分配",),
        cells=(),
    )

    result = processor.extract(
        FundProcessorInput(
            context=_dispatch_key(),
            intermediate=_ContentIntermediateStub(
                source_provenance=_provenance(),
                sections=(investor_section, holder_section),
                paragraph_blocks=(share_paragraph,),
                table_blocks=(subscription_table, distribution_table),
            ),
        )
    )

    family = _field_family(result, "investor_experience.v1")
    roles = {record.row_locator.split(";")[0] for record in family.candidate_evidence}

    assert family.status == "missing"
    assert family.extraction_mode == "missing"
    assert family.value == {}
    assert family.anchors == ()
    assert family.gaps[0].gap_code == "candidate_only_not_source_truth"
    assert roles == {
        "role=investor_return",
        "role=holder_structure",
        "role=share_change",
        "role=subscription_redemption",
        "role=income_distribution",
    }


def test_investor_experience_selector_preserves_candidate_boundary_fields() -> None:
    """investor_experience candidate records 固定保持 candidate-only/not_proven/not_ready。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当候选边界字段被提升时抛出。
    """

    processor = FundDisclosureDocumentProcessor()
    section = _SectionStub(
        section_id="section-investor-return",
        heading_text_raw="投资者获得感",
        heading_text_normalized="投资者获得感",
        heading_path=("投资者获得感",),
    )

    result = processor.extract(
        FundProcessorInput(
            context=_dispatch_key(),
            intermediate=_ContentIntermediateStub(
                source_provenance=_provenance(),
                sections=(section,),
                paragraph_blocks=(),
                table_blocks=(),
            ),
        )
    )

    family = _field_family(result, "investor_experience.v1")

    assert family.candidate_evidence
    for record in family.candidate_evidence:
        assert record.field_family_id == "investor_experience.v1"
        assert record.candidate_only
        assert record.source_boundary == "candidate_only"
        assert record.field_correctness_status == "not_proven"
        assert record.source_truth_status == "not_proven"
        assert not record.parser_replacement_authorized
        assert record.readiness_status == "not_ready"
        assert record.source_field_path not in family.value


def test_investor_experience_selector_keeps_other_families_without_candidate_evidence() -> None:
    """S6-E 不为其它字段族生成 candidate evidence。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 selector 越界到其它字段族时抛出。
    """

    processor = FundDisclosureDocumentProcessor()
    section = _SectionStub(
        section_id="section-investor-return",
        heading_text_raw="盈利投资者占比",
        heading_text_normalized="盈利投资者占比",
        heading_path=("盈利投资者占比",),
    )

    result = processor.extract(
        FundProcessorInput(
            context=_dispatch_key(),
            intermediate=_ContentIntermediateStub(
                source_provenance=_provenance(),
                sections=(section,),
                paragraph_blocks=(),
                table_blocks=(),
            ),
        )
    )

    investor = _field_family(result, "investor_experience.v1")
    assert investor.candidate_evidence

    for family_id in (
        "product_essence.v1",
        "return_attribution.v1",
        "manager_profile.v1",
        "current_stage.v1",
        "core_risk.v1",
    ):
        family = _field_family(result, family_id)
        assert family.status == "missing"
        assert family.value == {}
        assert family.anchors == ()
        assert family.candidate_evidence == ()
        assert family.gaps[0].gap_code == "field_family_missing"


def test_investor_experience_selector_no_match_keeps_field_family_missing() -> None:
    """非匹配正文不产生 investor_experience candidate evidence。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当无关正文被误命中时抛出。
    """

    processor = FundDisclosureDocumentProcessor()
    section = _SectionStub(
        heading_text_raw="其他章节",
        heading_text_normalized="其他章节",
        heading_path=("其他章节",),
    )
    paragraph = _ParagraphStub(
        heading_path=("其他章节",),
        text_raw="无关内容",
        text_normalized="无关内容",
    )
    cell = _CellStub(
        heading_path=("其他章节",),
        row_label_path=("其他",),
        column_header_path=("其他",),
        cell_text="无关",
        cell_text_normalized="无关",
    )
    table = _TableStub(
        heading_text="其他表格",
        table_caption_or_nearby_heading="其他表格",
        heading_path=("其他章节",),
        cells=(cell,),
    )

    result = processor.extract(
        FundProcessorInput(
            context=_dispatch_key(),
            intermediate=_ContentIntermediateStub(
                source_provenance=_provenance(),
                sections=(section,),
                paragraph_blocks=(paragraph,),
                table_blocks=(table,),
            ),
        )
    )

    family = _field_family(result, "investor_experience.v1")

    assert family.candidate_evidence == ()
    assert family.status == "missing"
    assert family.value == {}
    assert family.anchors == ()
    assert family.gaps[0].gap_code == "field_family_missing"


def test_investor_experience_selector_preserves_candidate_boundary_blocked_status() -> None:
    """candidate_boundary 输入即使有 investor evidence，整体仍 blocked。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 candidate evidence 提升 consumption status 时抛出。
    """

    processor = FundDisclosureDocumentProcessor()
    boundary = CandidateBoundaryStatus(
        candidate_only=True,
        field_correctness_status="not_proven",
        source_truth_status="not_proven",
    )
    section = _SectionStub(
        section_id="section-investor-return",
        heading_text_raw="投资者回报",
        heading_text_normalized="投资者回报",
        heading_path=("投资者回报",),
    )

    result = processor.extract(
        FundProcessorInput(
            context=_dispatch_key(),
            intermediate=_ContentIntermediateStub(
                source_provenance=_provenance(),
                candidate_boundary=boundary,
                sections=(section,),
                paragraph_blocks=(),
                table_blocks=(),
            ),
        )
    )

    family = _field_family(result, "investor_experience.v1")

    assert result.contract_status == "blocked"
    assert result.candidate_boundary is boundary
    assert family.candidate_evidence
    assert family.value == {}
    assert family.anchors == ()


def test_investor_experience_selector_orders_dedupes_limits_and_truncates() -> None:
    """investor_experience selector 保持 role/source 顺序、去重和 16 条限量。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 source path、顺序、去重或限量不符合 S6-E 时抛出。
    """

    processor = FundDisclosureDocumentProcessor()
    long_heading = "投资者实际收益" + "明细" * 100
    sections = (
        _SectionStub(
            section_id="section-investor",
            heading_text_raw=f"{long_heading}与基金份额持有人结构",
            heading_text_normalized=f"{long_heading}与基金份额持有人结构",
            heading_path=(f"{long_heading}与基金份额持有人结构",),
        ),
        _SectionStub(
            section_id="section-holder",
            heading_text_raw="基金份额持有人情况",
            heading_text_normalized="基金份额持有人情况",
            heading_path=("基金份额持有人情况",),
        ),
        _SectionStub(
            section_id="section-share",
            heading_text_raw="基金份额变动",
            heading_text_normalized="基金份额变动",
            heading_path=("基金份额变动",),
        ),
        _SectionStub(
            section_id="section-subscription",
            heading_text_raw="申购赎回",
            heading_text_normalized="申购赎回",
            heading_path=("申购赎回",),
        ),
    )
    paragraphs = (
        _ParagraphStub(
            block_id="paragraph-investor",
            section_id="section-investor",
            heading_path=("投资者回报",),
            text_raw="投资者回报披露。",
            text_normalized="投资者回报披露。",
        ),
        _ParagraphStub(
            block_id="paragraph-holder",
            section_id="section-holder",
            heading_path=("持有人结构",),
            text_raw="基金份额持有人信息披露。",
            text_normalized="基金份额持有人信息披露。",
        ),
        _ParagraphStub(
            block_id="paragraph-share",
            section_id="section-share",
            heading_path=("份额变动",),
            text_raw="份额变动披露。",
            text_normalized="份额变动披露。",
        ),
        _ParagraphStub(
            block_id="paragraph-subscription",
            section_id="section-subscription",
            heading_path=("申购赎回",),
            text_raw="本期申购披露。",
            text_normalized="本期申购披露。",
        ),
        _ParagraphStub(
            block_id="paragraph-distribution",
            section_id="section-distribution",
            heading_path=("收益分配",),
            text_raw="基金收益分配披露。",
            text_normalized="基金收益分配披露。",
        ),
    )
    holder_cells = (
        _CellStub(
            cell_id="holder-cell-original-0",
            row_index=2,
            column_index=0,
            row_label_path=("持有人户数",),
            cell_text="持有人户数",
            cell_text_normalized="持有人户数",
        ),
        _CellStub(
            cell_id="holder-cell-original-1",
            row_index=0,
            column_index=0,
            row_label_path=("机构投资者持有",),
            cell_text="机构投资者持有",
            cell_text_normalized="机构投资者持有",
        ),
        _CellStub(
            cell_id="holder-cell-original-2",
            row_index=1,
            column_index=0,
            row_label_path=("个人投资者持有",),
            cell_text="个人投资者持有",
            cell_text_normalized="个人投资者持有",
        ),
    )
    share_cells = (
        _CellStub(
            cell_id="share-cell-original-0",
            table_id="table-share",
            row_index=2,
            column_index=0,
            row_label_path=("期末基金份额总额",),
            cell_text="期末基金份额总额",
            cell_text_normalized="期末基金份额总额",
        ),
        _CellStub(
            cell_id="share-cell-original-1",
            table_id="table-share",
            row_index=0,
            column_index=0,
            row_label_path=("报告期期初基金份额总额",),
            cell_text="报告期期初基金份额总额",
            cell_text_normalized="报告期期初基金份额总额",
        ),
        _CellStub(
            cell_id="share-cell-original-2",
            table_id="table-share",
            row_index=1,
            column_index=0,
            row_label_path=("报告期期末基金份额总额",),
            cell_text="报告期期末基金份额总额",
            cell_text_normalized="报告期期末基金份额总额",
        ),
    )
    subscription_cells = (
        _CellStub(
            cell_id="subscription-cell-original-0",
            table_id="table-subscription",
            row_index=1,
            column_index=0,
            heading_path=("申购赎回",),
            row_label_path=("总申购份额",),
            cell_text="总申购份额",
            cell_text_normalized="总申购份额",
        ),
        _CellStub(
            cell_id="subscription-cell-original-1",
            table_id="table-subscription",
            row_index=0,
            column_index=0,
            heading_path=("申购赎回",),
            row_label_path=("总赎回份额",),
            cell_text="总赎回份额",
            cell_text_normalized="总赎回份额",
        ),
    )
    holder_table = _TableStub(
        table_id="table-holder",
        section_id="section-holder-table",
        heading_text="基金份额持有人结构",
        table_caption_or_nearby_heading="基金份额持有人结构",
        heading_path=("基金份额持有人结构",),
        cells=holder_cells,
    )
    share_table = _TableStub(
        table_id="table-share",
        section_id="section-share-table",
        heading_text="基金份额总额变动",
        table_caption_or_nearby_heading="基金份额总额变动",
        heading_path=("基金份额总额变动",),
        cells=share_cells,
    )
    subscription_table = _TableStub(
        table_id="table-subscription",
        section_id="section-subscription-table",
        heading_text="申购赎回",
        table_caption_or_nearby_heading="申购赎回",
        heading_path=("申购赎回",),
        cells=subscription_cells,
    )

    result = processor.extract(
        FundProcessorInput(
            context=_dispatch_key(),
            intermediate=_ContentIntermediateStub(
                source_provenance=_provenance(),
                sections=sections,
                paragraph_blocks=paragraphs,
                table_blocks=(holder_table, share_table, subscription_table),
            ),
        )
    )

    records = _field_family(result, "investor_experience.v1").candidate_evidence
    paths = [record.source_field_path for record in records]

    assert len(records) == 16
    assert paths == [
        "sections[0]",
        "paragraph_blocks[0]",
        "sections[1]",
        "paragraph_blocks[1]",
        "table_blocks[0]",
        "table_blocks[0].cells[1]",
        "table_blocks[0].cells[2]",
        "table_blocks[0].cells[0]",
        "sections[2]",
        "paragraph_blocks[2]",
        "table_blocks[1]",
        "table_blocks[1].cells[1]",
        "table_blocks[1].cells[2]",
        "table_blocks[1].cells[0]",
        "sections[3]",
        "paragraph_blocks[3]",
    ]
    assert "paragraph_blocks[4]" not in paths
    assert len(set(paths)) == len(paths)
    assert records[0].row_locator == "role=investor_return; locator=section_id=section-investor"
    assert records[2].row_locator == "role=holder_structure; locator=section_id=section-holder"
    assert records[8].row_locator == "role=share_change; locator=section_id=section-share"
    assert records[14].row_locator == (
        "role=subscription_redemption; locator=section_id=section-subscription"
    )
    assert all(len(record.excerpt) <= 160 for record in records)
    assert all(record.field_family_id == "investor_experience.v1" for record in records)


def test_investor_experience_selector_requires_context_for_generic_tokens() -> None:
    """generic investor-experience token 缺少 context 时不得产生 evidence。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 generic token 绕过 guard 时抛出。
    """

    processor = FundDisclosureDocumentProcessor()
    sections = (
        _SectionStub(
            section_id="section-return",
            heading_text_raw="实际收益",
            heading_text_normalized="实际收益",
            heading_path=("实际收益",),
        ),
        _SectionStub(
            section_id="section-holder",
            heading_text_raw="机构投资者",
            heading_text_normalized="机构投资者",
            heading_path=("机构投资者",),
        ),
        _SectionStub(
            section_id="section-share",
            heading_text_raw="期初份额",
            heading_text_normalized="期初份额",
            heading_path=("期初份额",),
        ),
        _SectionStub(
            section_id="section-subscription",
            heading_text_raw="申购",
            heading_text_normalized="申购",
            heading_path=("申购",),
        ),
        _SectionStub(
            section_id="section-distribution",
            heading_text_raw="分红",
            heading_text_normalized="分红",
            heading_path=("分红",),
        ),
    )

    result = processor.extract(
        FundProcessorInput(
            context=_dispatch_key(),
            intermediate=_ContentIntermediateStub(
                source_provenance=_provenance(),
                sections=sections,
                paragraph_blocks=(),
                table_blocks=(),
            ),
        )
    )

    family = _field_family(result, "investor_experience.v1")

    assert family.candidate_evidence == ()
    assert family.gaps[0].gap_code == "field_family_missing"


def test_investor_experience_selector_allows_generic_tokens_with_context() -> None:
    """generic investor-experience token 带 context 时可产生 candidate evidence。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当正向 guard context 被过度阻断时抛出。
    """

    processor = FundDisclosureDocumentProcessor()
    sections = (
        _SectionStub(
            section_id="section-return",
            heading_text_raw="投资者的实际收益披露",
            heading_text_normalized="投资者的实际收益披露",
            heading_path=("投资者的实际收益披露",),
        ),
        _SectionStub(
            section_id="section-holder",
            heading_text_raw="基金份额持有人中的机构投资者占比",
            heading_text_normalized="基金份额持有人中的机构投资者占比",
            heading_path=("基金份额持有人中的机构投资者占比",),
        ),
        _SectionStub(
            section_id="section-share",
            heading_text_raw="基金份额期初份额披露",
            heading_text_normalized="基金份额期初份额披露",
            heading_path=("基金份额期初份额披露",),
        ),
        _SectionStub(
            section_id="section-subscription",
            heading_text_raw="基金总申购中的净申购为正",
            heading_text_normalized="基金总申购中的净申购为正",
            heading_path=("基金总申购中的净申购为正",),
        ),
        _SectionStub(
            section_id="section-distribution",
            heading_text_raw="分配方案含分红",
            heading_text_normalized="分配方案含分红",
            heading_path=("分配方案含分红",),
        ),
    )

    result = processor.extract(
        FundProcessorInput(
            context=_dispatch_key(),
            intermediate=_ContentIntermediateStub(
                source_provenance=_provenance(),
                sections=sections,
                paragraph_blocks=(),
                table_blocks=(),
            ),
        )
    )

    family = _field_family(result, "investor_experience.v1")
    roles = [record.row_locator.split(";")[0] for record in family.candidate_evidence]

    assert roles == [
        "role=investor_return",
        "role=holder_structure",
        "role=share_change",
        "role=subscription_redemption",
        "role=income_distribution",
    ]


def test_investor_experience_selector_does_not_capture_return_or_manager_owned_tokens() -> None:
    """S6-C/S6-D-owned token 不得生成 investor_experience evidence。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 S6-E 捕获其它 selector 已拥有 token 时抛出。
    """

    processor = FundDisclosureDocumentProcessor()
    sections = tuple(
        _SectionStub(
            section_id=f"section-owned-{index}",
            heading_text_raw=text,
            heading_text_normalized=text,
            heading_path=(text,),
        )
        for index, text in enumerate(
            (
                "净值增长率",
                "业绩比较基准",
                "跟踪误差",
                "管理费",
                "换手率",
                "基金经理",
                "前十名股票投资明细",
            )
        )
    )

    result = processor.extract(
        FundProcessorInput(
            context=_dispatch_key(),
            intermediate=_ContentIntermediateStub(
                source_provenance=_provenance(),
                sections=sections,
                paragraph_blocks=(),
                table_blocks=(),
            ),
        )
    )

    family = _field_family(result, "investor_experience.v1")

    assert family.candidate_evidence == ()
    assert family.gaps[0].gap_code == "field_family_missing"


def test_investor_experience_selector_blocks_subscription_redemption_self_guard() -> None:
    """申购/赎回 generic token 不得靠同一 cell 的份额文本自守卫。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 subscription_redemption 自守卫通过时抛出。
    """

    processor = FundDisclosureDocumentProcessor()
    paragraph = _ParagraphStub(
        block_id="paragraph-fee",
        section_id="section-fee",
        heading_path=("费率说明",),
        text_raw="申购份额的计算方式为净申购金额除以基金份额净值。",
        text_normalized="申购份额的计算方式为净申购金额除以基金份额净值。",
    )
    cells = (
        _CellStub(
            cell_id="cell-subscription-share",
            row_index=0,
            column_index=0,
            row_label_path=("计算方式",),
            column_header_path=("费率",),
            cell_text="申购份额",
            cell_text_normalized="申购份额",
        ),
        _CellStub(
            cell_id="cell-subscription-method",
            row_index=1,
            column_index=0,
            row_label_path=("计算方式",),
            column_header_path=("费率",),
            cell_text="申购份额的计算方式",
            cell_text_normalized="申购份额的计算方式",
        ),
    )
    table = _TableStub(
        heading_text="费率表",
        table_caption_or_nearby_heading="费率表",
        heading_path=("费率说明",),
        cells=cells,
    )

    result = processor.extract(
        FundProcessorInput(
            context=_dispatch_key(),
            intermediate=_ContentIntermediateStub(
                source_provenance=_provenance(),
                sections=(),
                paragraph_blocks=(paragraph,),
                table_blocks=(table,),
            ),
        )
    )

    family = _field_family(result, "investor_experience.v1")

    assert family.candidate_evidence == ()
    assert family.gaps[0].gap_code == "field_family_missing"


def test_investor_experience_selector_allows_subscription_redemption_context_guard() -> None:
    """申购/赎回 generic token 可由 source-level actual-flow context 通过。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 controller 允许的 guard context 被误拒时抛出。
    """

    processor = FundDisclosureDocumentProcessor()
    cell = _CellStub(
        cell_id="cell-net-subscription",
        row_index=0,
        column_index=0,
        row_label_path=("净申购",),
        column_header_path=("项目",),
        cell_text="净申购",
        cell_text_normalized="净申购",
    )
    table = _TableStub(
        table_id="table-share-flow",
        section_id="section-share-flow",
        heading_text="基金份额总额变动",
        table_caption_or_nearby_heading="基金份额总额变动",
        heading_path=("基金份额总额变动",),
        cells=(cell,),
    )

    result = processor.extract(
        FundProcessorInput(
            context=_dispatch_key(),
            intermediate=_ContentIntermediateStub(
                source_provenance=_provenance(),
                sections=(),
                paragraph_blocks=(),
                table_blocks=(table,),
            ),
        )
    )

    family = _field_family(result, "investor_experience.v1")
    paths_by_role = {
        record.source_field_path: record.row_locator.split(";")[0]
        for record in family.candidate_evidence
    }

    assert paths_by_role["table_blocks[0].cells[0]"] == "role=subscription_redemption"


# ── S6-F core risk candidate selector ───────────────────────────────────────


def _core_risk_result(
    *,
    sections: tuple[_SectionStub, ...] = (),
    paragraphs: tuple[_ParagraphStub, ...] = (),
    tables: tuple[_TableStub, ...] = (),
    candidate_boundary: CandidateBoundaryStatus | None = None,
) -> FundProcessorResult:
    """运行 core_risk selector 测试用 processor。

    Args:
        sections: section fixture。
        paragraphs: paragraph fixture。
        tables: table fixture。
        candidate_boundary: 可选候选边界。

    Returns:
        processor 输出结果。

    Raises:
        AssertionError: processor contract 断言失败时由调用方抛出。
    """

    processor = FundDisclosureDocumentProcessor()
    return processor.extract(
        FundProcessorInput(
            context=_dispatch_key(),
            intermediate=_ContentIntermediateStub(
                source_provenance=_provenance(),
                candidate_boundary=candidate_boundary,
                sections=sections,
                paragraph_blocks=paragraphs,
                table_blocks=tables,
            ),
        )
    )


def _family_signature(family: FundFieldFamilyResult) -> tuple[object, ...]:
    """返回用于比较字段族 public/candidate 语义的稳定摘要。

    Args:
        family: 字段族结果。

    Returns:
        包含 record count、path 顺序、gap、public value/anchors 的摘要。

    Raises:
        无显式抛出。
    """

    return (
        len(family.candidate_evidence),
        tuple(record.source_field_path for record in family.candidate_evidence),
        tuple(gap.gap_code for gap in family.gaps),
        family.value,
        family.anchors,
    )


def test_core_risk_selector_adds_candidate_evidence_only() -> None:
    """core_risk selector 只填 candidate_evidence，不填 public value/anchor。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 role、gap 或 public boundary 不符合 S6-F 时抛出。
    """

    result = _core_risk_result(
        sections=(
            _SectionStub(
                section_id="section-risk",
                heading_text_raw="风险收益特征",
                heading_text_normalized="风险收益特征",
                heading_path=("风险收益特征",),
            ),
            _SectionStub(
                section_id="section-scale",
                heading_text_raw="基金资产净值低于五千万元",
                heading_text_normalized="基金资产净值低于五千万元",
                heading_path=("基金资产净值低于五千万元",),
            ),
            _SectionStub(
                section_id="section-tracking",
                heading_text_raw="跟踪误差",
                heading_text_normalized="跟踪误差",
                heading_path=("跟踪误差",),
            ),
            _SectionStub(
                section_id="section-turnover",
                heading_text_raw="换手率",
                heading_text_normalized="换手率",
                heading_path=("换手率",),
            ),
            _SectionStub(
                section_id="section-concentration",
                heading_text_raw="持仓集中度",
                heading_text_normalized="持仓集中度",
                heading_path=("持仓集中度",),
            ),
        )
    )

    family = _field_family(result, "core_risk.v1")
    roles = {record.row_locator.split(";")[0] for record in family.candidate_evidence}

    assert result.contract_status == "missing"
    assert roles == {
        "role=risk_characteristic",
        "role=liquidation_or_scale_risk",
        "role=tracking_error_or_deviation_risk",
        "role=turnover_or_style_drift_risk",
        "role=concentration_risk",
    }
    assert family.status == "missing"
    assert family.extraction_mode == "missing"
    assert family.value == {}
    assert family.anchors == ()
    assert family.gaps[0].gap_code == "candidate_only_not_source_truth"


def test_core_risk_selector_preserves_candidate_boundary_fields() -> None:
    """core_risk candidate records 固定保持 candidate-only/not_proven/not_ready。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 candidate evidence 泄漏到 public value 时抛出。
    """

    paragraph = _ParagraphStub(
        block_id="paragraph-risk-number",
        heading_path=("核心风险",),
        text_raw="连续二十个工作日基金资产净值低于5000万元，候选摘录含数值。",
        text_normalized="连续二十个工作日基金资产净值低于5000万元，候选摘录含数值。",
    )

    family = _field_family(_core_risk_result(paragraphs=(paragraph,)), "core_risk.v1")

    assert family.candidate_evidence
    assert family.value == {}
    assert family.anchors == ()
    for record in family.candidate_evidence:
        assert record.field_family_id == "core_risk.v1"
        assert record.candidate_only
        assert record.source_boundary == "candidate_only"
        assert record.field_correctness_status == "not_proven"
        assert record.source_truth_status == "not_proven"
        assert not record.parser_replacement_authorized
        assert record.readiness_status == "not_ready"
        assert record.source_field_path not in family.value
        assert record.excerpt not in family.value


def test_core_risk_selector_keeps_current_stage_without_candidate_evidence() -> None:
    """S6-F 不为 current_stage.v1 生成 candidate evidence。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 current_stage 越界获得 evidence 时抛出。
    """

    result = _core_risk_result(
        sections=(
            _SectionStub(
                section_id="section-risk",
                heading_text_raw="风险收益特征",
                heading_text_normalized="风险收益特征",
                heading_path=("风险收益特征",),
            ),
        )
    )

    current_stage = _field_family(result, "current_stage.v1")
    core_risk = _field_family(result, "core_risk.v1")

    assert core_risk.candidate_evidence
    assert current_stage.candidate_evidence == ()
    assert current_stage.value == {}
    assert current_stage.anchors == ()
    assert current_stage.gaps[0].gap_code == "field_family_missing"


def test_core_risk_selector_no_match_keeps_field_family_missing() -> None:
    """非匹配正文不产生 core_risk candidate evidence。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当无关正文被误命中时抛出。
    """

    result = _core_risk_result(
        sections=(
            _SectionStub(
                section_id="section-neutral",
                heading_text_raw="其他章节",
                heading_text_normalized="其他章节",
                heading_path=("其他章节",),
            ),
        ),
        paragraphs=(
            _ParagraphStub(
                block_id="paragraph-neutral",
                heading_path=("其他章节",),
                text_raw="无关内容",
                text_normalized="无关内容",
            ),
        ),
        tables=(
            _TableStub(
                heading_text="其他表格",
                table_caption_or_nearby_heading="其他表格",
                heading_path=("其他章节",),
                cells=(
                    _CellStub(
                        row_label_path=("其他",),
                        column_header_path=("其他",),
                        cell_text="无关",
                        cell_text_normalized="无关",
                    ),
                ),
            ),
        ),
    )

    family = _field_family(result, "core_risk.v1")

    assert family.candidate_evidence == ()
    assert family.gaps[0].gap_code == "field_family_missing"


def test_core_risk_selector_preserves_candidate_boundary_blocked_status() -> None:
    """candidate_boundary 输入即使有 core_risk evidence，整体仍 blocked。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 candidate evidence 提升 consumption status 时抛出。
    """

    boundary = CandidateBoundaryStatus(
        candidate_only=True,
        field_correctness_status="not_proven",
        source_truth_status="not_proven",
    )

    result = _core_risk_result(
        candidate_boundary=boundary,
        sections=(
            _SectionStub(
                section_id="section-risk",
                heading_text_raw="风险收益特征",
                heading_text_normalized="风险收益特征",
                heading_path=("风险收益特征",),
            ),
        ),
    )
    family = _field_family(result, "core_risk.v1")

    assert result.contract_status == "blocked"
    assert result.candidate_boundary is boundary
    assert family.candidate_evidence
    assert family.value == {}
    assert family.anchors == ()


def test_core_risk_selector_orders_dedupes_limits_and_truncates() -> None:
    """core_risk selector 保持 role/source 顺序、去重、16 条限量和摘录截断。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 source path、顺序、去重或限量不符合 S6-F 时抛出。
    """

    long_text = "风险收益特征" + "很长" * 100
    sections = (
        _SectionStub("section-risk", long_text, long_text, (long_text,)),
        _SectionStub("section-scale", "基金合同自动终止", "基金合同自动终止", ("基金合同自动终止",)),
        _SectionStub("section-tracking", "跟踪误差", "跟踪误差", ("跟踪误差",)),
        _SectionStub("section-turnover", "换手率", "换手率", ("换手率",)),
        _SectionStub("section-concentration", "持仓集中度", "持仓集中度", ("持仓集中度",)),
    )
    paragraphs = (
        _ParagraphStub("paragraph-risk", heading_path=("风险收益特征",), text_raw="风险收益特征"),
        _ParagraphStub(
            "paragraph-scale",
            heading_path=("清算",),
            text_raw="连续二十个工作日基金资产净值低于5000万元",
            text_normalized="连续二十个工作日基金资产净值低于5000万元",
        ),
        _ParagraphStub("paragraph-tracking", heading_path=("跟踪误差",), text_raw="跟踪误差"),
        _ParagraphStub("paragraph-turnover", heading_path=("换手率",), text_raw="换手率"),
        _ParagraphStub("paragraph-concentration", heading_path=("持仓集中度",), text_raw="持仓集中度"),
    )
    tables = (
        _TableStub(
            table_id="table-risk",
            heading_text="风险收益特征",
            table_caption_or_nearby_heading="风险收益特征",
            heading_path=("风险收益特征",),
            cells=(
                _CellStub("risk-cell-original-0", row_index=2, cell_text="风险收益特征"),
                _CellStub("risk-cell-original-1", row_index=0, cell_text="风险收益特征"),
            ),
        ),
        _TableStub(
            table_id="table-scale",
            heading_text="基金财产清算",
            table_caption_or_nearby_heading="基金财产清算",
            heading_path=("基金财产清算",),
            cells=(
                _CellStub(
                    "scale-cell",
                    table_id="table-scale",
                    cell_text="基金份额持有人数量不满200人",
                    cell_text_normalized="基金份额持有人数量不满200人",
                ),
            ),
        ),
        _TableStub(
            table_id="table-tracking",
            heading_text="跟踪误差",
            table_caption_or_nearby_heading="跟踪误差",
            heading_path=("跟踪误差",),
            cells=(
                _CellStub(
                    "tracking-cell",
                    table_id="table-tracking",
                    cell_text="日均跟踪偏离度",
                    cell_text_normalized="日均跟踪偏离度",
                ),
            ),
        ),
        _TableStub(
            table_id="table-turnover",
            heading_text="换手率",
            table_caption_or_nearby_heading="换手率",
            heading_path=("换手率",),
            cells=(
                _CellStub(
                    "turnover-cell",
                    table_id="table-turnover",
                    cell_text="投资风格发生重大变化",
                    cell_text_normalized="投资风格发生重大变化",
                ),
            ),
        ),
        _TableStub(
            table_id="table-concentration",
            heading_text="前十名股票投资明细",
            table_caption_or_nearby_heading="前十名股票投资明细",
            heading_path=("前十名股票投资明细",),
            cells=(
                _CellStub(
                    "concentration-cell",
                    table_id="table-concentration",
                    cell_text="报告期末基金资产组合情况",
                    cell_text_normalized="报告期末基金资产组合情况",
                ),
            ),
        ),
    )

    records = _field_family(
        _core_risk_result(sections=sections, paragraphs=paragraphs, tables=tables),
        "core_risk.v1",
    ).candidate_evidence
    paths = [record.source_field_path for record in records]

    assert len(records) == 16
    assert paths == [
        "sections[0]",
        "paragraph_blocks[0]",
        "table_blocks[0]",
        "table_blocks[0].cells[1]",
        "table_blocks[0].cells[0]",
        "sections[1]",
        "paragraph_blocks[1]",
        "table_blocks[1]",
        "table_blocks[1].cells[0]",
        "sections[2]",
        "paragraph_blocks[2]",
        "table_blocks[2]",
        "table_blocks[2].cells[0]",
        "sections[3]",
        "paragraph_blocks[3]",
        "table_blocks[3]",
    ]
    assert "sections[4]" not in paths
    assert len(set(paths)) == len(paths)
    assert records[0].row_locator == "role=risk_characteristic; locator=section_id=section-risk"
    assert records[5].row_locator == "role=liquidation_or_scale_risk; locator=section_id=section-scale"
    assert records[9].row_locator == "role=tracking_error_or_deviation_risk; locator=section_id=section-tracking"
    assert records[13].row_locator == "role=turnover_or_style_drift_risk; locator=section_id=section-turnover"
    assert all(len(record.excerpt) <= 160 for record in records)


def test_core_risk_selector_requires_context_for_generic_tokens() -> None:
    """core_risk broad generic token 缺少 source-level context 时不得产生 evidence。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 broad token 绕过 guard 时抛出。
    """

    sections = tuple(
        _SectionStub(
            section_id=f"section-generic-{index}",
            heading_text_raw=text,
            heading_text_normalized=text,
            heading_path=(text,),
        )
        for index, text in enumerate(
            (
                "风险",
                "收益",
                "规模",
                "清盘",
                "持有人",
                "基金资产净值",
                "跟踪",
                "偏离",
                "换手",
                "风格",
                "漂移",
                "策略变化",
                "持仓",
                "集中",
                "行业集中",
                "前十名",
            )
        )
    )

    family = _field_family(_core_risk_result(sections=sections), "core_risk.v1")

    assert family.candidate_evidence == ()
    assert family.gaps[0].gap_code == "field_family_missing"


def test_core_risk_selector_allows_generic_tokens_with_source_context() -> None:
    """core_risk generic token 带同源 guard context 时可产生 candidate evidence。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当正向 guard context 被过度阻断时抛出。
    """

    paragraphs = (
        _ParagraphStub(
            block_id="paragraph-risk",
            text_raw="基金简介提示风险。",
            text_normalized="基金简介提示风险。",
        ),
        _ParagraphStub(
            block_id="paragraph-scale",
            text_raw="基金份额持有人数量接近二百人，存在规模关注。",
            text_normalized="基金份额持有人数量接近二百人，存在规模关注。",
        ),
        _ParagraphStub(
            block_id="paragraph-tracking",
            text_raw="业绩比较基准附近出现偏离。",
            text_normalized="业绩比较基准附近出现偏离。",
        ),
        _ParagraphStub(
            block_id="paragraph-turnover",
            text_raw="投资策略发生重大变化，风格需要关注。",
            text_normalized="投资策略发生重大变化，风格需要关注。",
        ),
        _ParagraphStub(
            block_id="paragraph-concentration",
            text_raw="股票投资组合中前十名占比体现持仓特征。",
            text_normalized="股票投资组合中前十名占比体现持仓特征。",
        ),
    )

    family = _field_family(_core_risk_result(paragraphs=paragraphs), "core_risk.v1")
    roles = [record.row_locator.split(";")[0] for record in family.candidate_evidence]

    assert roles == [
        "role=risk_characteristic",
        "role=liquidation_or_scale_risk",
        "role=tracking_error_or_deviation_risk",
        "role=turnover_or_style_drift_risk",
        "role=concentration_risk",
    ]


def test_core_risk_selector_blocks_cell_self_guard_for_broad_tokens() -> None:
    """core_risk cell generic token 不得靠同一 cell 文本自守卫。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 same-cell guard 或跨 source guard 误通过时抛出。
    """

    blocked_table = _TableStub(
        table_id="table-blocked-risk",
        heading_text="普通明细",
        table_caption_or_nearby_heading="普通明细",
        heading_path=("普通明细",),
        cells=(
                _CellStub(
                    cell_id="cell-self-guard",
                    table_id="table-blocked-risk",
                    heading_path=("普通明细",),
                    row_label_path=("项目",),
                    column_header_path=("说明",),
                    cell_text="基金产品资料概要提示风险",
                    cell_text_normalized="基金产品资料概要提示风险",
                ),
                _CellStub(
                    cell_id="cell-sibling-guard",
                    table_id="table-blocked-risk",
                    heading_path=("普通明细",),
                    row_index=1,
                    row_label_path=("基金简介",),
                    column_header_path=("说明",),
                cell_text="普通文本",
                cell_text_normalized="普通文本",
            ),
        ),
    )
    allowed_table = _TableStub(
        table_id="table-allowed-risk",
        heading_text="基金简介",
        table_caption_or_nearby_heading="基金简介",
        heading_path=("基金简介",),
        cells=(
            _CellStub(
                cell_id="cell-allowed-risk",
                table_id="table-allowed-risk",
                row_label_path=("项目",),
                column_header_path=("说明",),
                cell_text="风险",
                cell_text_normalized="风险",
            ),
        ),
    )

    blocked_family = _field_family(_core_risk_result(tables=(blocked_table,)), "core_risk.v1")
    allowed_family = _field_family(_core_risk_result(tables=(allowed_table,)), "core_risk.v1")
    allowed_paths = {record.source_field_path for record in allowed_family.candidate_evidence}

    assert blocked_family.candidate_evidence == ()
    assert "table_blocks[0].cells[0]" in allowed_paths


def test_core_risk_selector_does_not_capture_reasoning_or_output_tokens() -> None:
    """S6-F 不把 Chapter 6 推理/输出词当成 locator token。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 forbidden token 单独产生 record 时抛出。
    """

    forbidden_sections = tuple(
        _SectionStub(
            section_id=f"section-forbidden-{index}",
            heading_text_raw=text,
            heading_text_normalized=text,
            heading_path=(text,),
        )
        for index, text in enumerate(
            ("压力测试", "最大回撤", "否决", "一票否决", "最致命", "需要替换", "值得持有", "风险等级")
        )
    )
    mixed_paragraph = _ParagraphStub(
        block_id="paragraph-mixed",
        text_raw="压力测试提示风险收益特征需阅读披露。",
        text_normalized="压力测试提示风险收益特征需阅读披露。",
    )

    pure_family = _field_family(_core_risk_result(sections=forbidden_sections), "core_risk.v1")
    mixed_family = _field_family(_core_risk_result(paragraphs=(mixed_paragraph,)), "core_risk.v1")

    assert pure_family.candidate_evidence == ()
    assert len(mixed_family.candidate_evidence) == 1
    assert mixed_family.candidate_evidence[0].row_locator.split(";")[0] == "role=risk_characteristic"
    assert mixed_family.candidate_evidence[0].source_field_path == "paragraph_blocks[0]"


def test_core_risk_selector_does_not_capture_investor_experience_owned_tokens() -> None:
    """S6-E-owned share-flow/distribution token 不得生成 core_risk evidence。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 S6-F 捕获 S6-E owned token 时抛出。
    """

    sections = tuple(
        _SectionStub(
            section_id=f"section-investor-owned-{index}",
            heading_text_raw=text,
            heading_text_normalized=text,
            heading_path=(text,),
        )
        for index, text in enumerate(
            ("基金份额变动", "申购", "赎回", "净申购", "净赎回", "收益分配", "分红", "红利")
        )
    )

    family = _field_family(_core_risk_result(sections=sections), "core_risk.v1")

    assert family.candidate_evidence == ()
    assert family.gaps[0].gap_code == "field_family_missing"


def test_core_risk_selector_preserves_overlap_family_semantics() -> None:
    """加入 S6-F 内容时 S6-B/S6-C/S6-D/S6-E 既有语义保持不变。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当既有字段族 count/order/gap/value/anchors 被改变时抛出。
    """

    baseline_sections = (
        _SectionStub(
            section_id="section-product",
            heading_text_raw="基金简介",
            heading_text_normalized="基金简介",
            heading_path=("基金简介",),
        ),
        _SectionStub(
            section_id="section-return",
            heading_text_raw="基金份额净值增长率",
            heading_text_normalized="基金份额净值增长率",
            heading_path=("基金份额净值增长率",),
        ),
        _SectionStub(
            section_id="section-manager",
            heading_text_raw="基金经理简介",
            heading_text_normalized="基金经理简介",
            heading_path=("基金经理简介",),
        ),
        _SectionStub(
            section_id="section-investor",
            heading_text_raw="投资者实际收益",
            heading_text_normalized="投资者实际收益",
            heading_path=("投资者实际收益",),
        ),
    )
    added_sections = (
        *baseline_sections,
        _SectionStub(
            section_id="section-core-risk",
            heading_text_raw="基金合同自动终止",
            heading_text_normalized="基金合同自动终止",
            heading_path=("基金合同自动终止",),
        ),
    )

    baseline = _core_risk_result(sections=baseline_sections)
    with_core_risk = _core_risk_result(sections=added_sections)

    for family_id in (
        "product_essence.v1",
        "return_attribution.v1",
        "manager_profile.v1",
        "investor_experience.v1",
    ):
        assert _family_signature(_field_family(with_core_risk, family_id)) == _family_signature(
            _field_family(baseline, family_id)
        )
    assert _field_family(with_core_risk, "core_risk.v1").candidate_evidence


# ── S6-G current stage candidate selector ───────────────────────────────────


def _current_stage_result(
    *,
    sections: tuple[_SectionStub, ...] = (),
    paragraphs: tuple[_ParagraphStub, ...] = (),
    tables: tuple[_TableStub, ...] = (),
    candidate_boundary: CandidateBoundaryStatus | None = None,
) -> FundProcessorResult:
    """运行 current_stage selector 测试用 processor。

    Args:
        sections: section fixture。
        paragraphs: paragraph fixture。
        tables: table fixture。
        candidate_boundary: 可选候选边界。

    Returns:
        processor 输出结果。

    Raises:
        AssertionError: processor contract 断言失败时由调用方抛出。
    """

    processor = FundDisclosureDocumentProcessor()
    return processor.extract(
        FundProcessorInput(
            context=_dispatch_key(),
            intermediate=_ContentIntermediateStub(
                source_provenance=_provenance(),
                candidate_boundary=candidate_boundary,
                sections=sections,
                paragraph_blocks=paragraphs,
                table_blocks=tables,
            ),
        )
    )


def test_current_stage_selector_adds_candidate_evidence_only() -> None:
    """current_stage selector 只填 candidate_evidence，不填 public value/anchor。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 role、gap 或 public boundary 不符合 S6-G 时抛出。
    """

    result = _current_stage_result(
        sections=(
            _SectionStub(
                section_id="section-stage",
                heading_text_raw="当前阶段",
                heading_text_normalized="当前阶段",
                heading_path=("当前阶段",),
            ),
            _SectionStub(
                section_id="section-manager-change",
                heading_text_raw="基金经理变更",
                heading_text_normalized="基金经理变更",
                heading_path=("基金经理变更",),
            ),
            _SectionStub(
                section_id="section-share-scale",
                heading_text_raw="规模变化",
                heading_text_normalized="规模变化",
                heading_path=("规模变化",),
            ),
            _SectionStub(
                section_id="section-strategy-change",
                heading_text_raw="投资策略调整",
                heading_text_normalized="投资策略调整",
                heading_path=("投资策略调整",),
            ),
        )
    )

    family = _field_family(result, "current_stage.v1")
    roles = {record.row_locator.split(";")[0] for record in family.candidate_evidence}

    assert result.contract_status == "missing"
    assert roles == {
        "role=stage_status",
        "role=manager_change",
        "role=share_scale_change",
        "role=holding_strategy_change",
    }
    assert family.status == "missing"
    assert family.extraction_mode == "missing"
    assert family.value == {}
    assert family.anchors == ()
    assert family.gaps[0].gap_code == "candidate_only_not_source_truth"


def test_current_stage_selector_classifies_strategy_operation_heading_as_holding_change() -> None:
    """S6-G exact 投资策略运作分析 heading/text 归属 holding_strategy_change。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 overlap token 被 stage_status 抢占时抛出。
    """

    overlap_text = "报告期内基金投资策略和运作分析"
    section = _SectionStub(
        section_id="section-strategy-operation",
        heading_text_raw=overlap_text,
        heading_text_normalized=overlap_text,
        heading_path=(overlap_text,),
    )
    paragraph = _ParagraphStub(
        block_id="paragraph-strategy-operation",
        heading_path=(overlap_text,),
        text_raw=overlap_text,
        text_normalized=overlap_text,
    )

    family = _field_family(
        _current_stage_result(sections=(section,), paragraphs=(paragraph,)),
        "current_stage.v1",
    )
    row_locators = [record.row_locator for record in family.candidate_evidence]

    assert row_locators == [
        "role=holding_strategy_change; locator=section_id=section-strategy-operation",
        "role=holding_strategy_change; locator=block_id=paragraph-strategy-operation",
    ]
    assert all(not row_locator.startswith("role=stage_status;") for row_locator in row_locators)


def test_current_stage_selector_preserves_candidate_boundary_fields() -> None:
    """current_stage candidate records 固定保持 candidate-only/not_proven/not_ready。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 candidate evidence 泄漏到 public value 时抛出。
    """

    paragraph = _ParagraphStub(
        block_id="paragraph-stage-number",
        heading_path=("当前阶段与关键变化",),
        text_raw="基金当前阶段处于稳定期，候选摘录含 2025 年规模变化数字。",
        text_normalized="基金当前阶段处于稳定期，候选摘录含 2025 年规模变化数字。",
    )

    family = _field_family(_current_stage_result(paragraphs=(paragraph,)), "current_stage.v1")

    assert family.candidate_evidence
    assert family.value == {}
    assert family.anchors == ()
    for record in family.candidate_evidence:
        assert record.field_family_id == "current_stage.v1"
        assert record.candidate_only
        assert record.source_boundary == "candidate_only"
        assert record.field_correctness_status == "not_proven"
        assert record.source_truth_status == "not_proven"
        assert not record.parser_replacement_authorized
        assert record.readiness_status == "not_ready"
        assert record.source_field_path not in family.value
        assert record.excerpt not in family.value


def test_current_stage_selector_no_match_keeps_field_family_missing() -> None:
    """非匹配正文不产生 current_stage candidate evidence。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当无关正文被误命中时抛出。
    """

    family = _field_family(
        _current_stage_result(
            sections=(
                _SectionStub(
                    section_id="section-neutral",
                    heading_text_raw="其他章节",
                    heading_text_normalized="其他章节",
                    heading_path=("其他章节",),
                ),
            ),
            paragraphs=(
                _ParagraphStub(
                    block_id="paragraph-neutral",
                    heading_path=("其他章节",),
                    text_raw="无关内容",
                    text_normalized="无关内容",
                ),
            ),
            tables=(
                _TableStub(
                    heading_text="其他表格",
                    table_caption_or_nearby_heading="其他表格",
                    heading_path=("其他章节",),
                    cells=(
                        _CellStub(
                            row_label_path=("其他",),
                            column_header_path=("其他",),
                            cell_text="无关",
                            cell_text_normalized="无关",
                        ),
                    ),
                ),
            ),
        ),
        "current_stage.v1",
    )

    assert family.candidate_evidence == ()
    assert family.status == "missing"
    assert family.value == {}
    assert family.anchors == ()
    assert family.gaps[0].gap_code == "field_family_missing"


def test_current_stage_selector_preserves_candidate_boundary_blocked_status() -> None:
    """candidate_boundary 输入即使有 current_stage evidence，整体仍 blocked。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 candidate evidence 提升 consumption status 时抛出。
    """

    boundary = CandidateBoundaryStatus(
        candidate_only=True,
        field_correctness_status="not_proven",
        source_truth_status="not_proven",
    )

    result = _current_stage_result(
        candidate_boundary=boundary,
        sections=(
            _SectionStub(
                section_id="section-stage",
                heading_text_raw="当前阶段",
                heading_text_normalized="当前阶段",
                heading_path=("当前阶段",),
            ),
        ),
    )
    family = _field_family(result, "current_stage.v1")

    assert result.contract_status == "blocked"
    assert result.candidate_boundary is boundary
    assert family.candidate_evidence
    assert family.value == {}
    assert family.anchors == ()


def test_current_stage_selector_orders_dedupes_limits_and_truncates() -> None:
    """current_stage selector 保持 role/source 顺序、去重、16 条限量和摘录截断。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 source path、顺序、去重或限量不符合 S6-G 时抛出。
    """

    long_text = "当前阶段" + "很长" * 100
    sections = (
        _SectionStub("section-stage", long_text, long_text, (long_text, "基金经理变更")),
        _SectionStub("section-manager", "基金经理变更", "基金经理变更", ("基金经理变更",)),
        _SectionStub("section-share", "基金份额变动", "基金份额变动", ("基金份额变动",)),
        _SectionStub("section-strategy", "投资策略调整", "投资策略调整", ("投资策略调整",)),
    )
    paragraphs = (
        _ParagraphStub("paragraph-stage", heading_path=("当前阶段",), text_raw="当前阶段"),
        _ParagraphStub("paragraph-manager", heading_path=("基金经理变更",), text_raw="基金经理变更"),
        _ParagraphStub("paragraph-share", heading_path=("基金份额变动",), text_raw="基金份额变动"),
        _ParagraphStub("paragraph-strategy", heading_path=("投资策略调整",), text_raw="投资策略调整"),
    )
    tables = (
        _TableStub(
            table_id="table-stage",
            heading_text="当前阶段",
            table_caption_or_nearby_heading="当前阶段",
            heading_path=("当前阶段",),
            cells=(
                _CellStub(
                    "stage-cell-original-0",
                    table_id="table-stage",
                    row_index=2,
                    cell_text="当前阶段",
                    cell_text_normalized="当前阶段",
                ),
                _CellStub(
                    "stage-cell-original-1",
                    table_id="table-stage",
                    row_index=0,
                    cell_text="当前阶段",
                    cell_text_normalized="当前阶段",
                ),
            ),
        ),
        _TableStub(
            table_id="table-manager",
            heading_text="基金经理变更",
            table_caption_or_nearby_heading="基金经理变更",
            heading_path=("基金经理变更",),
            cells=(
                _CellStub(
                    "manager-cell",
                    table_id="table-manager",
                    cell_text="新任基金经理",
                    cell_text_normalized="新任基金经理",
                ),
            ),
        ),
        _TableStub(
            table_id="table-share",
            heading_text="基金份额总额变动",
            table_caption_or_nearby_heading="基金份额总额变动",
            heading_path=("基金份额总额变动",),
            cells=(
                _CellStub(
                    "share-cell",
                    table_id="table-share",
                    cell_text="大额申购",
                    cell_text_normalized="大额申购",
                ),
            ),
        ),
        _TableStub(
            table_id="table-strategy",
            heading_text="投资策略调整",
            table_caption_or_nearby_heading="投资策略调整",
            heading_path=("投资策略调整",),
            cells=(
                _CellStub(
                    "strategy-cell",
                    table_id="table-strategy",
                    cell_text="持仓结构变化",
                    cell_text_normalized="持仓结构变化",
                ),
            ),
        ),
    )

    records = _field_family(
        _current_stage_result(sections=sections, paragraphs=paragraphs, tables=tables),
        "current_stage.v1",
    ).candidate_evidence
    paths = [record.source_field_path for record in records]

    assert len(records) == 16
    assert paths == [
        "sections[0]",
        "paragraph_blocks[0]",
        "table_blocks[0]",
        "table_blocks[0].cells[1]",
        "table_blocks[0].cells[0]",
        "sections[1]",
        "paragraph_blocks[1]",
        "table_blocks[1]",
        "table_blocks[1].cells[0]",
        "sections[2]",
        "paragraph_blocks[2]",
        "table_blocks[2]",
        "table_blocks[2].cells[0]",
        "sections[3]",
        "paragraph_blocks[3]",
        "table_blocks[3]",
    ]
    assert "table_blocks[3].cells[0]" not in paths
    assert paths.count("sections[0]") == 1
    assert len(set(paths)) == len(paths)
    assert records[0].row_locator == "role=stage_status; locator=section_id=section-stage"
    assert records[5].row_locator == "role=manager_change; locator=section_id=section-manager"
    assert records[9].row_locator == "role=share_scale_change; locator=section_id=section-share"
    assert records[13].row_locator == "role=holding_strategy_change; locator=section_id=section-strategy"
    assert all(len(record.excerpt) <= 160 for record in records)
    assert all(record.field_family_id == "current_stage.v1" for record in records)


def test_current_stage_selector_requires_context_for_generic_tokens() -> None:
    """current_stage generic token 缺少 source-level context 时不得产生 evidence。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 broad token 绕过 guard 时抛出。
    """

    sections = tuple(
        _SectionStub(
            section_id=f"section-generic-{index}",
            heading_text_raw=text,
            heading_text_normalized=text,
            heading_path=(text,),
        )
        for index, text in enumerate(
            (
                "阶段",
                "状态",
                "运作",
                "变更",
                "变动",
                "任职",
                "离任",
                "聘任",
                "份额",
                "规模",
                "申购",
                "赎回",
                "策略",
                "持仓",
                "配置",
                "仓位",
                "行业",
                "重仓",
                "变化",
                "调整",
            )
        )
    )

    family = _field_family(_current_stage_result(sections=sections), "current_stage.v1")

    assert family.candidate_evidence == ()
    assert family.gaps[0].gap_code == "field_family_missing"


def test_current_stage_selector_allows_generic_tokens_with_source_context() -> None:
    """current_stage generic token 带同源 guard context 时可产生 candidate evidence。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当正向 guard context 被过度阻断时抛出。
    """

    tables = (
        _TableStub(
            table_id="table-stage-context",
            heading_text="关键变化",
            table_caption_or_nearby_heading="关键变化",
            heading_path=("关键变化",),
            cells=(
                _CellStub(
                    "cell-stage-generic",
                    table_id="table-stage-context",
                    cell_text="阶段",
                    cell_text_normalized="阶段",
                ),
            ),
        ),
        _TableStub(
            table_id="table-manager-context",
            heading_text="基金经理情况",
            table_caption_or_nearby_heading="基金经理情况",
            heading_path=("基金经理情况",),
            cells=(
                _CellStub(
                    "cell-manager-generic",
                    table_id="table-manager-context",
                    cell_text="变更",
                    cell_text_normalized="变更",
                ),
            ),
        ),
        _TableStub(
            table_id="table-share-context",
            heading_text="基金份额总额变动",
            table_caption_or_nearby_heading="基金份额总额变动",
            heading_path=("基金份额总额变动",),
            cells=(
                _CellStub(
                    "cell-share-generic",
                    table_id="table-share-context",
                    cell_text="规模",
                    cell_text_normalized="规模",
                ),
            ),
        ),
        _TableStub(
            table_id="table-strategy-context",
            heading_text="投资组合",
            table_caption_or_nearby_heading="投资组合",
            heading_path=("投资组合",),
            cells=(
                _CellStub(
                    "cell-strategy-generic",
                    table_id="table-strategy-context",
                    cell_text="调整",
                    cell_text_normalized="调整",
                ),
            ),
        ),
    )

    family = _field_family(_current_stage_result(tables=tables), "current_stage.v1")
    roles = [record.row_locator.split(";")[0] for record in family.candidate_evidence]

    assert "role=stage_status" in roles
    assert "role=manager_change" in roles
    assert "role=share_scale_change" in roles
    assert "role=holding_strategy_change" in roles


def test_current_stage_selector_blocks_cell_self_guard_for_broad_tokens() -> None:
    """current_stage cell generic token 不得靠同一 cell 文本自守卫或 sibling 授权。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 same-cell guard 或跨 source guard 误通过时抛出。
    """

    blocked_table = _TableStub(
        table_id="table-blocked-current-stage",
        heading_text="普通明细",
        table_caption_or_nearby_heading="普通明细",
        heading_path=("普通明细",),
        cells=(
            _CellStub(
                cell_id="cell-self-guard",
                table_id="table-blocked-current-stage",
                heading_path=("普通明细",),
                row_label_path=("项目",),
                column_header_path=("说明",),
                cell_text="投资策略出现调整",
                cell_text_normalized="投资策略出现调整",
            ),
            _CellStub(
                cell_id="cell-sibling-guard",
                table_id="table-blocked-current-stage",
                heading_path=("普通明细",),
                row_index=1,
                row_label_path=("项目",),
                column_header_path=("说明",),
                cell_text="当前阶段",
                cell_text_normalized="当前阶段",
            ),
        ),
    )
    allowed_table = _TableStub(
        table_id="table-allowed-current-stage",
        heading_text="投资组合",
        table_caption_or_nearby_heading="投资组合",
        heading_path=("投资组合",),
        cells=(
            _CellStub(
                cell_id="cell-allowed-current-stage",
                table_id="table-allowed-current-stage",
                row_label_path=("项目",),
                column_header_path=("说明",),
                cell_text="调整",
                cell_text_normalized="调整",
            ),
        ),
    )

    blocked_paths = {
        record.source_field_path
        for record in _field_family(
            _current_stage_result(tables=(blocked_table,)), "current_stage.v1"
        ).candidate_evidence
    }
    allowed_paths = {
        record.source_field_path
        for record in _field_family(
            _current_stage_result(tables=(allowed_table,)), "current_stage.v1"
        ).candidate_evidence
    }

    assert "table_blocks[0].cells[0]" not in blocked_paths
    assert "table_blocks[0].cells[1]" in blocked_paths
    assert "table_blocks[0].cells[0]" in allowed_paths


def test_current_stage_selector_blocks_chapter5_reasoning_output_tokens() -> None:
    """S6-G 不把 Chapter 5 推理/输出词当成 locator token。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 forbidden token 单独产生 record 时抛出。
    """

    forbidden_sections = tuple(
        _SectionStub(
            section_id=f"section-forbidden-ch5-{index}",
            heading_text_raw=text,
            heading_text_normalized=text,
            heading_path=(text,),
        )
        for index, text in enumerate(
            (
                "为什么偏偏是现在",
                "下一步最小验证问题",
                "接下来最该跟踪",
                "变化是否改变前文判断",
                "未改变",
                "需要重新评估",
                "推翻前文判断",
                "值得持有",
                "需要关注",
                "建议替换",
                "买入",
                "卖出",
            )
        )
    )
    mixed_paragraph = _ParagraphStub(
        block_id="paragraph-mixed-ch5",
        text_raw="为什么偏偏是现在需要关注；当前阶段披露为稳定期。",
        text_normalized="为什么偏偏是现在需要关注；当前阶段披露为稳定期。",
    )

    pure_family = _field_family(_current_stage_result(sections=forbidden_sections), "current_stage.v1")
    mixed_family = _field_family(
        _current_stage_result(paragraphs=(mixed_paragraph,)), "current_stage.v1"
    )

    assert pure_family.candidate_evidence == ()
    assert len(mixed_family.candidate_evidence) == 1
    assert mixed_family.candidate_evidence[0].row_locator.split(";")[0] == "role=stage_status"
    assert mixed_family.candidate_evidence[0].source_field_path == "paragraph_blocks[0]"


def test_current_stage_selector_blocks_chapter6_risk_tokens() -> None:
    """S6-G 不捕获 Chapter 6 / S6-F risk-owned token。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当风险词单独生成 current_stage record 时抛出。
    """

    sections = tuple(
        _SectionStub(
            section_id=f"section-risk-owned-{index}",
            heading_text_raw=text,
            heading_text_normalized=text,
            heading_path=(text,),
        )
        for index, text in enumerate(
            ("风险", "核心风险", "清盘风险", "压力测试", "最大回撤", "否决", "一票否决", "风险等级", "需要替换", "值得持有")
        )
    )

    family = _field_family(_current_stage_result(sections=sections), "current_stage.v1")

    assert family.candidate_evidence == ()
    assert family.gaps[0].gap_code == "field_family_missing"


def test_current_stage_selector_blocks_market_and_valuation_external_tokens() -> None:
    """S6-G 不捕获市场预测或估值外部真源 token。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当外部预测词生成 current_stage record 时抛出。
    """

    sections = tuple(
        _SectionStub(
            section_id=f"section-market-owned-{index}",
            heading_text_raw=text,
            heading_text_normalized=text,
            heading_path=(text,),
        )
        for index, text in enumerate(
            ("市场走势", "未来收益", "宏观预测", "估值温度计", "温度计", "估值百分位", "估值分位", "低估", "高估", "便宜", "昂贵")
        )
    )

    family = _field_family(_current_stage_result(sections=sections), "current_stage.v1")

    assert family.candidate_evidence == ()
    assert family.gaps[0].gap_code == "field_family_missing"


def test_current_stage_selector_blocks_product_identity_only_overlap() -> None:
    """产品身份类 token 不单独生成 current_stage evidence。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 S6-B-owned token 越界生成 current_stage record 时抛出。
    """

    sections = tuple(
        _SectionStub(
            section_id=f"section-product-owned-{index}",
            heading_text_raw=text,
            heading_text_normalized=text,
            heading_path=(text,),
        )
        for index, text in enumerate(("基金简介", "基金基本情况", "产品概况", "基金名称", "基金代码", "风险收益特征", "业绩比较基准"))
    )

    result = _current_stage_result(sections=sections)

    assert _field_family(result, "current_stage.v1").candidate_evidence == ()
    assert _field_family(result, "product_essence.v1").candidate_evidence


def test_current_stage_selector_blocks_manager_biography_only_overlap() -> None:
    """基金经理履历类 token 不单独生成 current_stage evidence。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 S6-D-owned token 越界或合法变更词被阻断时抛出。
    """

    biography_sections = tuple(
        _SectionStub(
            section_id=f"section-manager-bio-{index}",
            heading_text_raw=text,
            heading_text_normalized=text,
            heading_path=(text,),
        )
        for index, text in enumerate(("基金经理简介", "姓名", "职务", "职责", "岗位"))
    )
    legal_section = _SectionStub(
        section_id="section-manager-change",
        heading_text_raw="基金经理变更",
        heading_text_normalized="基金经理变更",
        heading_path=("基金经理变更",),
    )

    biography_result = _current_stage_result(sections=biography_sections)
    legal_result = _current_stage_result(sections=(legal_section,))
    legal_roles = {
        record.row_locator.split(";")[0]
        for record in _field_family(legal_result, "current_stage.v1").candidate_evidence
    }

    assert _field_family(biography_result, "current_stage.v1").candidate_evidence == ()
    assert _field_family(biography_result, "manager_profile.v1").candidate_evidence
    assert legal_roles == {"role=manager_change"}


def test_current_stage_selector_blocks_investor_experience_only_overlap() -> None:
    """投资者获得感类 token 不单独生成 current_stage evidence。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 S6-E-owned token 越界或合法份额变化词被阻断时抛出。
    """

    investor_sections = tuple(
        _SectionStub(
            section_id=f"section-investor-owned-{index}",
            heading_text_raw=text,
            heading_text_normalized=text,
            heading_path=(text,),
        )
        for index, text in enumerate(
            ("持有人户数", "户均持有份额", "机构投资者持有", "个人投资者持有", "收益分配", "分红", "红利", "投资者实际收益", "投资者获得感")
        )
    )
    legal_section = _SectionStub(
        section_id="section-share-scale",
        heading_text_raw="基金份额变动",
        heading_text_normalized="基金份额变动",
        heading_path=("基金份额变动",),
    )

    investor_result = _current_stage_result(sections=investor_sections)
    legal_result = _current_stage_result(sections=(legal_section,))
    legal_roles = {
        record.row_locator.split(";")[0]
        for record in _field_family(legal_result, "current_stage.v1").candidate_evidence
    }

    assert _field_family(investor_result, "current_stage.v1").candidate_evidence == ()
    assert _field_family(investor_result, "investor_experience.v1").candidate_evidence
    assert legal_roles == {"role=share_scale_change"}


def test_current_stage_selector_blocks_return_fee_only_overlap() -> None:
    """收益/费用类 token 不单独生成 current_stage evidence。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 S6-C-owned token 越界生成 current_stage record 时抛出。
    """

    sections = tuple(
        _SectionStub(
            section_id=f"section-return-fee-owned-{index}",
            heading_text_raw=text,
            heading_text_normalized=text,
            heading_path=(text,),
        )
        for index, text in enumerate(
            ("净值增长率", "业绩比较基准收益率", "管理费", "托管费", "销售服务费", "跟踪误差", "跟踪偏离度")
        )
    )

    result = _current_stage_result(sections=sections)

    assert _field_family(result, "current_stage.v1").candidate_evidence == ()
    assert _field_family(result, "return_attribution.v1").candidate_evidence


def test_current_stage_selector_preserves_overlap_family_semantics() -> None:
    """加入 S6-G 内容时 S6-B/S6-C/S6-D/S6-E/S6-F 既有语义保持不变。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当既有字段族 count/order/gap/value/anchors 被改变时抛出。
    """

    baseline_sections = (
        _SectionStub(
            section_id="section-product",
            heading_text_raw="基金简介",
            heading_text_normalized="基金简介",
            heading_path=("基金简介",),
        ),
        _SectionStub(
            section_id="section-return",
            heading_text_raw="基金份额净值增长率",
            heading_text_normalized="基金份额净值增长率",
            heading_path=("基金份额净值增长率",),
        ),
        _SectionStub(
            section_id="section-manager",
            heading_text_raw="基金经理简介",
            heading_text_normalized="基金经理简介",
            heading_path=("基金经理简介",),
        ),
        _SectionStub(
            section_id="section-investor-share",
            heading_text_raw="基金份额变动",
            heading_text_normalized="基金份额变动",
            heading_path=("基金份额变动",),
        ),
        _SectionStub(
            section_id="section-core-risk",
            heading_text_raw="风险收益特征",
            heading_text_normalized="风险收益特征",
            heading_path=("风险收益特征",),
        ),
    )
    added_sections = (
        *baseline_sections,
        _SectionStub(
            section_id="section-current-stage",
            heading_text_raw="当前阶段",
            heading_text_normalized="当前阶段",
            heading_path=("当前阶段",),
        ),
    )

    baseline = _current_stage_result(sections=baseline_sections)
    with_current_stage = _current_stage_result(sections=added_sections)

    for family_id in (
        "product_essence.v1",
        "return_attribution.v1",
        "manager_profile.v1",
        "investor_experience.v1",
        "core_risk.v1",
    ):
        assert _family_signature(_field_family(with_current_stage, family_id)) == _family_signature(
            _field_family(baseline, family_id)
        )

    investor_baseline = _field_family(baseline, "investor_experience.v1")
    investor_with_stage = _field_family(with_current_stage, "investor_experience.v1")
    assert investor_baseline.candidate_evidence[0].row_locator.startswith("role=share_change")
    assert _family_signature(investor_with_stage) == _family_signature(investor_baseline)
    assert {
        record.source_field_path
        for record in _field_family(baseline, "current_stage.v1").candidate_evidence
    } == {"sections[3]"}
    assert {
        record.source_field_path
        for record in _field_family(with_current_stage, "current_stage.v1").candidate_evidence
    } == {"sections[3]", "sections[5]"}


# ── Registration ────────────────────────────────────────────────────────────


def test_processor_registered_in_default_registry() -> None:
    """默认 registry 包含 FundDisclosureDocumentProcessor 并可解析 fund_disclosure_document.v1。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 registry 未注册或解析错误时抛出。
    """

    registry = FundProcessorRegistry.create_default()

    processor = registry.resolve(
        FundProcessorDispatchKey(
            fund_type="active_fund",
            report_type="annual_report",
            intermediate_kind="fund_disclosure_document.v1",
            source_kind="annual_report",
            document_year=2025,
            fund_code="004393",
        )
    )

    assert isinstance(processor, FundDisclosureDocumentProcessor)
    assert processor.processor_id == "fund_disclosure_document.fund_disclosure_document.v1"


# ── supports() ──────────────────────────────────────────────────────────────


def test_supports_fund_disclosure_document_v1() -> None:
    """supports() 对 active_fund + annual_report + fund_disclosure_document.v1 返回 True。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 supports 拒绝合法 dispatch key 时抛出。
    """

    processor = FundDisclosureDocumentProcessor()

    assert processor.supports(_dispatch_key())


def test_supports_rejects_parsed_annual_report_v1() -> None:
    """supports() 对 parsed_annual_report.v1 返回 False，不抢占 ActiveFundAnnualProcessor。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 supports 接受 parsed_annual_report.v1 时抛出。
    """

    processor = FundDisclosureDocumentProcessor()

    assert not processor.supports(_dispatch_key(intermediate_kind="parsed_annual_report.v1"))


def test_supports_rejects_non_active_fund_type() -> None:
    """supports() 对非 active fund 类型返回 False。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 supports 接受非 active 类型时抛出。
    """

    processor = FundDisclosureDocumentProcessor()

    assert not processor.supports(_dispatch_key(fund_type="index_fund"))


def test_processor_priority_below_active_annual() -> None:
    """FundDisclosureDocumentProcessor priority(50) 低于 ActiveFundAnnualProcessor(100)。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 priority 排序不正确时抛出。
    """

    disclosure = FundDisclosureDocumentProcessor()
    from fund_agent.fund.processors.active_annual import ActiveFundAnnualProcessor

    active = ActiveFundAnnualProcessor()

    assert disclosure.priority < active.priority


# ── extract() guards ────────────────────────────────────────────────────────


def test_extract_rejects_wrong_intermediate_type() -> None:
    """extract 对非 FundDisclosureDocumentIntermediate 输入返回 blocked。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当类型不匹配未被拒绝时抛出。
    """

    processor = FundDisclosureDocumentProcessor()
    from fund_agent.fund.processors.contracts import FundProcessorInput

    result = processor.extract(
        FundProcessorInput(
            context=_dispatch_key(),
            intermediate="not_a_valid_intermediate",
        )
    )

    assert result.contract_status == "blocked"
    assert any(g.gap_code == "input_type_mismatch" for g in result.gaps)


# ── Identity validation ─────────────────────────────────────────────────────


def test_extract_rejects_intermediate_kind_mismatch() -> None:
    """intermediate_kind 不匹配 → gap_code=input_type_mismatch, source_boundary=unsupported_intermediate。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 gap 映射不符合 plan 时抛出。
    """

    processor = FundDisclosureDocumentProcessor()
    from fund_agent.fund.processors.contracts import FundProcessorInput

    result = processor.extract(
        FundProcessorInput(
            context=_dispatch_key(),
            intermediate=_stub(intermediate_kind="parsed_annual_report.v1"),  # type: ignore[arg-type]
        )
    )

    assert result.contract_status == "blocked"
    gap = result.gaps[0]
    assert gap.gap_code == "input_type_mismatch"
    assert gap.source_boundary == "unsupported_intermediate"


def test_extract_rejects_document_kind_mismatch() -> None:
    """document_kind 不匹配 → gap_code=unsupported_report_type, source_boundary=unsupported_report_type。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 gap 映射不符合 plan 时抛出。
    """

    processor = FundDisclosureDocumentProcessor()
    from fund_agent.fund.processors.contracts import FundProcessorInput

    result = processor.extract(
        FundProcessorInput(
            context=_dispatch_key(),
            intermediate=_stub(document_kind="interim_report"),  # type: ignore[arg-type]
        )
    )

    assert result.contract_status == "blocked"
    gap = result.gaps[0]
    assert gap.gap_code == "unsupported_report_type"
    assert gap.source_boundary == "unsupported_report_type"


def test_extract_rejects_fund_code_mismatch() -> None:
    """fund_code 不匹配 → gap_code=unsupported_intermediate, source_boundary=unsupported_intermediate。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 gap 映射不符合 plan 时抛出。
    """

    processor = FundDisclosureDocumentProcessor()
    from fund_agent.fund.processors.contracts import FundProcessorInput

    result = processor.extract(
        FundProcessorInput(
            context=_dispatch_key(),
            intermediate=_stub(fund_code="999999"),
        )
    )

    assert result.contract_status == "blocked"
    gap = result.gaps[0]
    assert gap.gap_code == "unsupported_intermediate"
    assert gap.source_boundary == "unsupported_intermediate"


def test_extract_rejects_report_year_mismatch() -> None:
    """report_year 不匹配 → gap_code=unsupported_intermediate, source_boundary=unsupported_intermediate。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 gap 映射不符合 plan 时抛出。
    """

    processor = FundDisclosureDocumentProcessor()
    from fund_agent.fund.processors.contracts import FundProcessorInput

    result = processor.extract(
        FundProcessorInput(
            context=_dispatch_key(),
            intermediate=_stub(report_year=2020),
        )
    )

    assert result.contract_status == "blocked"
    gap = result.gaps[0]
    assert gap.gap_code == "unsupported_intermediate"
    assert gap.source_boundary == "unsupported_intermediate"


# ── Admission helper consumption ────────────────────────────────────────────


@pytest.mark.parametrize("failure_class", ("schema_drift", "identity_mismatch", "integrity_error"))
def test_extract_blocks_on_fail_closed_failure_class(
    failure_class: AnnualReportSourceFailureCategory,
) -> None:
    """结构性失败分类 → admission helper 返回 not admitted → processor 返回 blocked。

    Args:
        failure_class: 年报来源失败分类。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当失败分类未被正确处理时抛出。
    """

    processor = FundDisclosureDocumentProcessor()
    from fund_agent.fund.processors.contracts import FundProcessorInput

    result = processor.extract(
        FundProcessorInput(
            context=_dispatch_key(),
            intermediate=_stub(
                source_provenance=_provenance(),
                failure_class=failure_class,
            ),
        )
    )

    assert result.contract_status == "blocked"
    assert result.gaps
    gap = result.gaps[0]
    assert gap.gap_code == "candidate_boundary_blocked"
    assert gap.source_boundary == "candidate_only"


@pytest.mark.parametrize("failure_class", ("not_found", "unavailable"))
def test_extract_blocks_on_eligible_failure_class(
    failure_class: AnnualReportSourceFailureCategory,
) -> None:
    """eligible 失败分类 → admission helper→ unsupported。

    Args:
        failure_class: 年报来源失败分类。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 failure 映射不正确时抛出。
    """

    processor = FundDisclosureDocumentProcessor()
    from fund_agent.fund.processors.contracts import FundProcessorInput

    result = processor.extract(
        FundProcessorInput(
            context=_dispatch_key(),
            intermediate=_stub(
                source_provenance=_provenance(),
                failure_class=failure_class,
            ),
        )
    )

    assert result.contract_status == "unsupported"
    gap = result.gaps[0]
    assert gap.gap_code == "unsupported_intermediate"


def test_extract_blocks_on_missing_source_provenance() -> None:
    """缺失 provenance → admission helper 返回 source_provenance_unsafe → processor blocked。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当缺失 provenance 未 fail-closed 时抛出。
    """

    processor = FundDisclosureDocumentProcessor()
    from fund_agent.fund.processors.contracts import FundProcessorInput

    result = processor.extract(
        FundProcessorInput(
            context=_dispatch_key(),
            intermediate=_stub(source_provenance=None),
        )
    )

    assert result.contract_status == "blocked"
    gap = result.gaps[0]
    assert gap.gap_code == "source_provenance_unsafe"


def test_extract_admits_candidate_boundary_but_returns_blocked() -> None:
    """候选中间态 admitted 但 contract_status=blocked，六个字段族全 missing。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当候选边界被错误提升时抛出。
    """

    processor = FundDisclosureDocumentProcessor()
    from fund_agent.fund.processors.contracts import FundProcessorInput

    result = processor.extract(
        FundProcessorInput(
            context=_dispatch_key(),
            intermediate=_stub(
                source_provenance=_provenance(),
                candidate_boundary=CandidateBoundaryStatus(
                    candidate_only=True,
                    field_correctness_status="not_proven",
                    source_truth_status="not_proven",
                ),
            ),
        )
    )

    assert result.contract_status == "blocked"
    assert result.candidate_boundary is not None
    assert result.candidate_boundary.candidate_only
    assert len(result.field_families) == 6
    for family in result.field_families:
        assert family.status == "missing"
        assert family.value == {}
        assert family.gaps[0].gap_code == "field_family_missing"


# ── Satisfied path ──────────────────────────────────────────────────────────


def test_extract_satisfied_returns_fully_gapped_result() -> None:
    """admission satisfied → contract_status=missing，6 个字段族全 status=missing。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 satisfied 路径输出不符合预期时抛出。
    """

    processor = FundDisclosureDocumentProcessor()
    from fund_agent.fund.processors.contracts import FundProcessorInput

    result = processor.extract(
        FundProcessorInput(
            context=_dispatch_key(),
            intermediate=_stub(source_provenance=_provenance()),
        )
    )

    assert result.contract_status == "missing"
    assert len(result.field_families) == 6
    family_ids = {f.field_family_id for f in result.field_families}
    assert family_ids == {
        "product_essence.v1",
        "return_attribution.v1",
        "manager_profile.v1",
        "investor_experience.v1",
        "current_stage.v1",
        "core_risk.v1",
    }
    for family in result.field_families:
        assert family.status == "missing"
        assert family.value == {}
        assert family.extraction_mode == "missing"
        assert family.anchors == ()
        assert _gap_codes(family) == {
            "field_family_missing",
            "source_truth_admission_missing",
        }
    assert result.gaps == ()


def test_extract_satisfied_result_preserves_source_provenance() -> None:
    """satisfied 路径保留 intermediate 的 source_provenance。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 provenance 丢失时抛出。
    """

    processor = FundDisclosureDocumentProcessor()
    from fund_agent.fund.processors.contracts import FundProcessorInput

    prov = _provenance()
    result = processor.extract(
        FundProcessorInput(
            context=_dispatch_key(),
            intermediate=_stub(source_provenance=prov),
        )
    )

    assert result.source_provenance is prov


def test_extract_satisfied_result_candidate_boundary_none() -> None:
    """非候选 satisfied 路径 candidate_boundary 为 None。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 candidate_boundary 非预期时抛出。
    """

    processor = FundDisclosureDocumentProcessor()
    from fund_agent.fund.processors.contracts import FundProcessorInput

    result = processor.extract(
        FundProcessorInput(
            context=_dispatch_key(),
            intermediate=_stub(source_provenance=_provenance()),
        )
    )

    assert result.candidate_boundary is None


def test_extract_candidate_boundary_result_preserves_candidate_boundary() -> None:
    """候选路径保留 intermediate.candidate_boundary。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 candidate_boundary 丢失时抛出。
    """

    processor = FundDisclosureDocumentProcessor()
    from fund_agent.fund.processors.contracts import FundProcessorInput

    cb = CandidateBoundaryStatus(
        candidate_only=True,
        field_correctness_status="not_proven",
        source_truth_status="not_proven",
    )
    result = processor.extract(
        FundProcessorInput(
            context=_dispatch_key(),
            intermediate=_stub(source_provenance=_provenance(), candidate_boundary=cb),
        )
    )

    assert result.candidate_boundary is cb


# ── KeyError handling ───────────────────────────────────────────────────────


def test_extract_keyerror_on_invalid_failure_class_is_caught() -> None:
    """admission helper KeyError → processor 捕获并返回 blocked result。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 KeyError 未被转换时抛出。
    """

    processor = FundDisclosureDocumentProcessor()
    from fund_agent.fund.processors.contracts import FundProcessorInput

    # 构造 failure_class 为非标准值以触发 FAILURE_CLASS_ADMISSION_MAP KeyError
    class _BadIntermediate:
        document_kind = "annual_report"
        fund_code = "004393"
        report_year = 2025
        intermediate_kind = "fund_disclosure_document.v1"
        source_provenance = _provenance()
        candidate_boundary = None
        failure_class = "not_a_real_failure_class"

    result = processor.extract(
        FundProcessorInput(
            context=_dispatch_key(),
            intermediate=_BadIntermediate(),  # type: ignore[arg-type]
        )
    )

    assert result.contract_status == "unsupported"
    gap = result.gaps[0]
    assert gap.gap_code == "unsupported_intermediate"
    assert "not_a_real_failure_class" in gap.message


# ── Unsupported context ─────────────────────────────────────────────────────


def test_extract_unsupported_context_returns_blocked() -> None:
    """dispatch key 不匹配 supports → blocked result。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 unsupported 未被正确处理时抛出。
    """

    processor = FundDisclosureDocumentProcessor()
    from fund_agent.fund.processors.contracts import FundProcessorInput

    result = processor.extract(
        FundProcessorInput(
            context=_dispatch_key(fund_type="index_fund"),
            intermediate=_stub(source_provenance=_provenance()),
        )
    )

    assert result.contract_status == "unsupported"
    assert any(g.gap_code == "unsupported_fund_type" for g in result.gaps)


# ── Result integrity ────────────────────────────────────────────────────────


def test_extract_result_gaps_are_cross_family_only() -> None:
    """result-level gaps 不含 field_family_id（S1 invariant）。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 result gaps 带有 field_family_id 时抛出。
    """

    processor = FundDisclosureDocumentProcessor()
    from fund_agent.fund.processors.contracts import FundProcessorInput

    result = processor.extract(
        FundProcessorInput(
            context=_dispatch_key(),
            intermediate=_stub(source_provenance=_provenance()),
        )
    )

    for gap in result.gaps:
        assert gap.field_family_id is None


# ── Boundary isolation ──────────────────────────────────────────────────────


def test_processor_does_not_import_forbidden_boundaries() -> None:
    """processor 模块不导入 Service/UI/Host/Agent/documents.models/candidates。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当出现越界导入时抛出。
    """

    module_path = (
        Path(__file__).parents[3]
        / "fund_agent"
        / "fund"
        / "processors"
        / "fund_disclosure_processor.py"
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
        "fund_agent.fund.documents.candidates",
    )
    assert not any(module.startswith(forbidden_prefixes) for module in imported_modules)
