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
    FundExtractionGap,
    FundFieldFamilyResult,
    FundProcessorDispatchKey,
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
        assert len(family.gaps) == 1
        assert family.gaps[0].gap_code == "field_family_missing"
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
