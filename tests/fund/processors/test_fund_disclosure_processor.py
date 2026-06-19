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
