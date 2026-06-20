"""FundDisclosureDocument processor 测试。"""

from __future__ import annotations

import ast
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path
from typing import Literal

import pytest

from fund_agent.fund.extractors.models import TrackingErrorValue
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
    _manager_profile_cell_original_index,
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


def _source_truth_content_intermediate(
    *,
    cells: tuple[_CellStub, ...] = (),
    paragraphs: tuple[_ParagraphStub, ...] = (),
    sections: tuple[_SectionStub, ...] = (),
    source_truth_admission: FundDisclosureSourceTruthAdmissionProof | None = None,
    with_source_truth_proof: bool = True,
) -> _ContentIntermediateStub:
    """构造 proof-positive source-truth FDD content fixture。

    Args:
        cells: table cells。
        paragraphs: paragraph blocks。
        sections: sections。
        source_truth_admission: 可选 source-truth proof；缺省构造合法 proof。
        with_source_truth_proof: 是否带 source-truth proof。

    Returns:
        FDD content intermediate stub。

    Raises:
        无显式抛出。
    """

    table = _TableStub(cells=cells) if cells else _TableStub(cells=())
    proof = source_truth_admission
    if with_source_truth_proof and proof is None:
        proof = _source_truth_admission_proof()
    return _ContentIntermediateStub(
        source_provenance=_provenance(),
        source_truth_admission=proof,
        sections=sections,
        paragraph_blocks=paragraphs,
        table_blocks=(table,),
    )


def _product_essence_source_truth_result(
    intermediate: _ContentIntermediateStub,
) -> FundProcessorResult:
    """运行 product_essence source-truth processor fixture。

    Args:
        intermediate: FDD content intermediate。

    Returns:
        processor 输出结果。

    Raises:
        无显式抛出。
    """

    processor = FundDisclosureDocumentProcessor()
    return processor.extract(FundProcessorInput(context=_dispatch_key(), intermediate=intermediate))


def _return_attribution_source_truth_result(
    intermediate: _ContentIntermediateStub,
) -> FundProcessorResult:
    """运行 return_attribution source-truth route 测试用 processor。

    Args:
        intermediate: FDD content intermediate。

    Returns:
        processor 输出结果。

    Raises:
        无显式抛出。
    """

    processor = FundDisclosureDocumentProcessor()
    return processor.extract(FundProcessorInput(context=_dispatch_key(), intermediate=intermediate))


def _manager_profile_source_truth_result(
    intermediate: _ContentIntermediateStub,
) -> FundProcessorResult:
    """运行 manager_profile source-truth route 测试用 processor。

    Args:
        intermediate: FDD content intermediate。

    Returns:
        processor 输出结果。

    Raises:
        无显式抛出。
    """

    processor = FundDisclosureDocumentProcessor()
    return processor.extract(FundProcessorInput(context=_dispatch_key(), intermediate=intermediate))


def _investor_experience_source_truth_result(
    intermediate: _ContentIntermediateStub,
) -> FundProcessorResult:
    """运行 investor_experience source-truth route 测试用 processor。

    Args:
        intermediate: FDD content intermediate。

    Returns:
        processor 输出结果。

    Raises:
        无显式抛出。
    """

    processor = FundDisclosureDocumentProcessor()
    return processor.extract(FundProcessorInput(context=_dispatch_key(), intermediate=intermediate))


def _current_stage_source_truth_result(
    intermediate: _ContentIntermediateStub,
) -> FundProcessorResult:
    """运行 current_stage source-truth route 测试用 processor。

    Args:
        intermediate: FDD content intermediate。

    Returns:
        processor 输出结果。

    Raises:
        无显式抛出。
    """

    processor = FundDisclosureDocumentProcessor()
    return processor.extract(FundProcessorInput(context=_dispatch_key(), intermediate=intermediate))


def _investor_paragraph(
    text: str,
    *,
    block_id: str = "paragraph-investor",
    heading_path: tuple[str, ...] = ("投资者获得感",),
) -> _ParagraphStub:
    """构造 investor_experience paragraph source-truth fixture。

    Args:
        text: paragraph 文本。
        block_id: block id。
        heading_path: heading path。

    Returns:
        paragraph stub。

    Raises:
        无显式抛出。
    """

    return _ParagraphStub(
        block_id=block_id,
        section_id="section-investor",
        heading_path=heading_path,
        text_raw=text,
        text_normalized=text,
    )


def _investor_cell(
    label: str,
    value: str,
    *,
    row_index: int,
    column_index: int = 1,
    table_id: str = "table-investor",
    cell_id: str | None = None,
    column_header_path: tuple[str, ...] = ("内容",),
    heading_path: tuple[str, ...] = ("投资者获得感",),
) -> _CellStub:
    """构造 investor_experience table/cell source-truth fixture。

    Args:
        label: row label。
        value: cell value。
        row_index: 行号。
        column_index: 列号。
        table_id: 所属表格 ID。
        cell_id: 可选 cell id。
        column_header_path: column header path。
        heading_path: heading path。

    Returns:
        cell stub。

    Raises:
        无显式抛出。
    """

    return _CellStub(
        cell_id=cell_id or f"{table_id}-cell-{row_index}-{column_index}",
        table_id=table_id,
        section_anchor="section-investor",
        heading_path=heading_path,
        row_index=row_index,
        column_index=column_index,
        row_label_path=(label,),
        column_header_path=column_header_path,
        cell_text=value,
        cell_text_normalized=value,
    )


def _product_cell(
    output_label: str,
    value: str,
    *,
    row_index: int,
    column_index: int = 1,
    cell_id: str | None = None,
) -> _CellStub:
    """构造 Slice B table/cell source-truth fixture。

    Args:
        output_label: row_label_path label。
        value: cell value。
        row_index: 行号。
        column_index: 列号。
        cell_id: 可选 cell id。

    Returns:
        table cell stub。

    Raises:
        无显式抛出。
    """

    resolved_cell_id = cell_id or f"cell-{row_index}-{column_index}"
    return _CellStub(
        cell_id=resolved_cell_id,
        row_index=row_index,
        column_index=column_index,
        row_label_path=(output_label,),
        column_header_path=("内容",),
        cell_text=value,
        cell_text_normalized=value,
    )


def _return_attribution_cell(
    label: str,
    value: str,
    *,
    row_index: int,
    column_index: int = 1,
    cell_id: str | None = None,
    label_axis: Literal["row", "column"] = "row",
) -> _CellStub:
    """构造 Slice 2 return_attribution table/cell source-truth fixture。

    Args:
        label: row label 或 column header label。
        value: cell value。
        row_index: 行号。
        column_index: 列号。
        cell_id: 可选 cell id。
        label_axis: label 放入 row label 还是 column header。

    Returns:
        table cell stub。

    Raises:
        无显式抛出。
    """

    resolved_cell_id = cell_id or f"return-cell-{row_index}-{column_index}"
    row_label_path = (label,) if label_axis == "row" else ("报告期",)
    column_header_path = (label,) if label_axis == "column" else ("内容",)
    return _CellStub(
        cell_id=resolved_cell_id,
        row_index=row_index,
        column_index=column_index,
        row_label_path=row_label_path,
        column_header_path=column_header_path,
        cell_text=value,
        cell_text_normalized=value,
        heading_path=("收益归因",),
    )


def _manager_profile_cell(
    label: str,
    value: str,
    *,
    row_index: int,
    column_index: int = 1,
    cell_id: str | None = None,
    table_id: str = "table-manager",
    label_axis: Literal["row", "column"] = "column",
    locator_stability: str = "stable",
) -> _CellStub:
    """构造 Slice 3 manager_profile table/cell source-truth fixture。

    Args:
        label: row label 或 column header label。
        value: cell value。
        row_index: 行号。
        column_index: 列号。
        cell_id: 可选 cell id。
        table_id: 所属 table id。
        label_axis: label 放入 row label 还是 column header。
        locator_stability: locator 稳定性。

    Returns:
        table cell stub。

    Raises:
        无显式抛出。
    """

    resolved_cell_id = cell_id or f"manager-cell-{row_index}-{column_index}"
    row_label_path = (label,) if label_axis == "row" else ("经理信息",)
    column_header_path = (label,) if label_axis == "column" else ("内容",)
    return _CellStub(
        cell_id=resolved_cell_id,
        table_id=table_id,
        row_index=row_index,
        column_index=column_index,
        row_label_path=row_label_path,
        column_header_path=column_header_path,
        cell_text=value,
        cell_text_normalized=value,
        heading_path=("基金经理情况",),
        locator_stability=locator_stability,
    )


def _manager_profile_holdings_cell(
    header: str,
    value: str,
    *,
    row_index: int,
    column_index: int,
    table_id: str,
) -> _CellStub:
    """构造 Slice 3 holdings_snapshot table/cell source-truth fixture。

    Args:
        header: 中文披露列头。
        value: cell 披露文本。
        row_index: 行号。
        column_index: 列号。
        table_id: 所属 table id。

    Returns:
        holdings_snapshot table cell stub。

    Raises:
        无显式抛出。
    """

    return _CellStub(
        cell_id=f"{table_id}-cell-{row_index}-{column_index}",
        table_id=table_id,
        row_index=row_index,
        column_index=column_index,
        row_label_path=("持仓明细",),
        column_header_path=(header,),
        cell_text=value,
        cell_text_normalized=value,
        heading_path=("投资组合",),
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
    assert product.candidate_evidence == ()


# ── Slice B product essence source-truth extraction ────────────────────────


def test_product_essence_source_truth_extracts_exact_value_shape() -> None:
    """proof-positive FDD content 可抽取 exact product_essence.v1 value shape。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 public value、anchor 或候选边界不符合 Slice B 时抛出。
    """

    paragraph = _ParagraphStub(
        block_id="paragraph-investment-objective",
        heading_path=("投资目标",),
        text_raw="力争实现基金资产长期稳健增值。",
        text_normalized="力争实现基金资产长期稳健增值。",
    )
    result = _product_essence_source_truth_result(
        _source_truth_content_intermediate(
            cells=(
                _product_cell("基金名称", "测试主动基金", row_index=0),
                _product_cell("基金主代码", "004393", row_index=1),
                _product_cell("基金管理人", "测试基金管理有限公司", row_index=2),
                _product_cell("基金托管人", "测试托管银行", row_index=3),
                _product_cell("业绩比较基准", "沪深300指数收益率*80%+中债综合指数收益率*20%", row_index=4),
                _product_cell("风险收益特征", "本基金属于主动权益基金，风险收益水平较高。", row_index=5),
            ),
            paragraphs=(paragraph,),
        )
    )

    product = _field_family(result, "product_essence.v1")
    value = product.value

    assert result.contract_status == "partial"
    assert product.status == "accepted"
    assert product.extraction_mode == "direct"
    assert product.candidate_evidence == ()
    assert set(value) == {
        "basic_identity",
        "product_profile",
        "benchmark",
        "risk_characteristic_text",
    }
    assert value["basic_identity"] == {
        "fund_name": "测试主动基金",
        "fund_code": "004393",
        "fund_category": None,
        "fund_scale": None,
        "fund_manager": None,
        "management_company": "测试基金管理有限公司",
        "custodian": "测试托管银行",
        "inception_date": None,
        "classified_fund_type": "active_fund",
        "classification_basis": ("dispatch_key.fund_type=active_fund",),
    }
    assert value["product_profile"] == {
        "investment_objective": "力争实现基金资产长期稳健增值。",
        "style_positioning": None,
        "investment_scope": None,
        "investment_strategy": None,
    }
    assert value["benchmark"] == {
        "benchmark_text": "沪深300指数收益率*80%+中债综合指数收益率*20%"
    }
    assert value["risk_characteristic_text"] == {
        "schema_version": "risk_characteristic_text.v1",
        "fund_code": "004393",
        "report_year": 2025,
        "risk_characteristic_text": "本基金属于主动权益基金，风险收益水平较高。",
        "source_anchors": [
            {
                "section_id": "section-1",
                "page_number": None,
                "table_id": "table-1",
                "row_locator": (
                    "field=risk_characteristic_text.risk_characteristic_text; "
                    "table_id=table-1; row=5; column=1; cell_id=cell-5-1"
                ),
            }
        ],
    }
    assert product.anchors
    assert all(anchor.source_kind == "annual_report" for anchor in product.anchors)
    current_stage = _field_family(result, "current_stage.v1")
    assert current_stage.status == "partial"
    assert set(current_stage.value) == {"schema_version", "basic_identity"}
    assert current_stage.candidate_evidence == ()
    for family in result.field_families:
        if family.field_family_id in {"product_essence.v1", "current_stage.v1"}:
            continue
        assert family.status == "missing"
        assert family.value == {}
        assert family.anchors == ()


def test_product_essence_source_truth_requires_proof_even_when_candidate_boundary_none() -> None:
    """即使 candidate_boundary=None，缺 proof 的可抽取内容也必须 fail-closed。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当缺 proof 仍输出 public value 或 anchors 时抛出。
    """

    result = _product_essence_source_truth_result(
        _source_truth_content_intermediate(
            cells=(
                _product_cell("基金名称", "测试主动基金", row_index=0),
                _product_cell("基金主代码", "004393", row_index=1),
            ),
            with_source_truth_proof=False,
        )
    )

    product = _field_family(result, "product_essence.v1")

    assert product.value == {}
    assert product.anchors == ()
    assert "source_truth_admission_missing" in _gap_codes(product)


def test_product_essence_source_truth_rejects_missing_source_provenance() -> None:
    """source_provenance 缺失时在 base admission 顶层 blocked。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当缺 source provenance 未被 base admission 阻断时抛出。
    """

    result = _product_essence_source_truth_result(
        _ContentIntermediateStub(
            source_provenance=None,
            source_truth_admission=_source_truth_admission_proof(),
            table_blocks=(
                _TableStub(
                    cells=(
                        _product_cell("基金名称", "测试主动基金", row_index=0),
                        _product_cell("基金主代码", "004393", row_index=1),
                    )
                ),
            ),
        )
    )

    assert result.contract_status == "blocked"
    assert result.field_families == ()
    assert result.anchors == ()
    assert result.gaps[0].gap_code == "source_provenance_unsafe"
    assert result.gaps[0].source_boundary == "source_provenance_unsafe"


@pytest.mark.parametrize(
    ("failure_class", "expected_gap_code", "expected_source_boundary", "expected_status"),
    (
        ("not_found", "unsupported_intermediate", "unsupported_intermediate", "unsupported"),
        ("unavailable", "unsupported_intermediate", "unsupported_intermediate", "unsupported"),
        ("schema_drift", "candidate_boundary_blocked", "candidate_only", "blocked"),
        ("identity_mismatch", "candidate_boundary_blocked", "candidate_only", "blocked"),
        ("integrity_error", "candidate_boundary_blocked", "candidate_only", "blocked"),
    ),
)
def test_product_essence_source_truth_rejects_failure_class_at_base_admission(
    failure_class: AnnualReportSourceFailureCategory,
    expected_gap_code: str,
    expected_source_boundary: str,
    expected_status: str,
) -> None:
    """failure_class 存在时按 base admission map fail-closed。

    Args:
        failure_class: 年报来源失败分类。
        expected_gap_code: admission map 预期 gap code。
        expected_source_boundary: admission map 预期来源边界。
        expected_status: admission map 预期 contract status。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 failure_class 未按 admission map 阻断时抛出。
    """

    result = _product_essence_source_truth_result(
        _ContentIntermediateStub(
            source_provenance=_provenance(),
            failure_class=failure_class,
            source_truth_admission=_source_truth_admission_proof(),
            table_blocks=(
                _TableStub(
                    cells=(
                        _product_cell("基金名称", "测试主动基金", row_index=0),
                        _product_cell("基金主代码", "004393", row_index=1),
                    )
                ),
            ),
        )
    )

    assert result.contract_status == expected_status
    assert result.field_families == ()
    assert result.anchors == ()
    assert result.gaps[0].gap_code == expected_gap_code
    assert result.gaps[0].source_boundary == expected_source_boundary


def test_product_essence_source_truth_ambiguous_duplicate_omits_conflicting_path() -> None:
    """同一路径多个不同稳定值必须省略冲突路径并记录 ambiguous gap。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当冲突 basic_identity 被错误输出时抛出。
    """

    result = _product_essence_source_truth_result(
        _source_truth_content_intermediate(
            cells=(
                _product_cell("基金名称", "测试主动基金A", row_index=0, cell_id="cell-name-a"),
                _product_cell("基金名称", "测试主动基金B", row_index=1, cell_id="cell-name-b"),
                _product_cell("基金主代码", "004393", row_index=2),
            )
        )
    )

    product = _field_family(result, "product_essence.v1")

    assert "basic_identity" not in product.value
    assert product.anchors == ()
    assert "ambiguous_table_or_locator" in _gap_codes(product)


def test_product_essence_source_truth_matches_column_header_only_cell() -> None:
    """row_label_path 不命中时允许 column_header_path 命中 product_essence 字段。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 column_header_path-only cell 未被抽取时抛出。
    """

    cell = _CellStub(
        cell_id="cell-benchmark-column-only",
        row_index=0,
        column_index=2,
        row_label_path=("无关行",),
        column_header_path=("业绩比较基准",),
        cell_text="沪深300指数收益率*80%+中债综合指数收益率*20%",
        cell_text_normalized="沪深300指数收益率*80%+中债综合指数收益率*20%",
    )
    result = _product_essence_source_truth_result(
        _source_truth_content_intermediate(cells=(cell,))
    )

    product = _field_family(result, "product_essence.v1")

    assert product.value["benchmark"] == {
        "benchmark_text": "沪深300指数收益率*80%+中债综合指数收益率*20%"
    }
    assert any(
        anchor.row_locator == (
            "field=benchmark.benchmark_text; table_id=table-1; "
            "row=0; column=2; cell_id=cell-benchmark-column-only"
        )
        for anchor in product.anchors
    )


@pytest.mark.parametrize("generic_text", ("项目", "指标", "名称", "内容", "说明"))
def test_product_essence_source_truth_rejects_generic_cell_text(generic_text: str) -> None:
    """泛化表头文本不能作为 product_essence 字段值输出。

    Args:
        generic_text: 待验证的泛化 cell 文本。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当泛化 cell 文本被写入 public path 时抛出。
    """

    result = _product_essence_source_truth_result(
        _source_truth_content_intermediate(
            cells=(
                _product_cell(
                    "基金名称",
                    generic_text,
                    row_index=0,
                    cell_id=f"cell-generic-{generic_text}",
                ),
                _product_cell("基金主代码", "004393", row_index=1),
            )
        )
    )

    product = _field_family(result, "product_essence.v1")

    assert "basic_identity" not in product.value
    assert all(
        "field=basic_identity.fund_name" not in anchor.row_locator
        for anchor in product.anchors
    )


def test_product_essence_source_truth_skips_unstable_table_or_cell_locator() -> None:
    """table 或 cell locator 不稳定时必须跳过对应候选。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当不稳定 table/cell locator 被抽取时抛出。
    """

    unstable_table = _TableStub(
        table_id="unstable-table",
        locator_stability="unstable",
        cells=(_product_cell("基金名称", "不应输出的基金名称", row_index=0),),
    )
    unstable_cell_table = _TableStub(
        table_id="stable-table",
        cells=(
            _CellStub(
                cell_id="unstable-cell",
                table_id="stable-table",
                row_index=1,
                column_index=1,
                row_label_path=("基金主代码",),
                column_header_path=("内容",),
                cell_text="004393",
                cell_text_normalized="004393",
                locator_stability="unstable",
            ),
        ),
    )
    result = _product_essence_source_truth_result(
        _ContentIntermediateStub(
            source_provenance=_provenance(),
            source_truth_admission=_source_truth_admission_proof(),
            paragraph_blocks=(),
            table_blocks=(unstable_table, unstable_cell_table),
        )
    )

    product = _field_family(result, "product_essence.v1")

    assert product.status == "missing"
    assert product.value == {}
    assert product.anchors == ()
    assert "ambiguous_table_or_locator" not in _gap_codes(product)


def test_product_essence_source_truth_dedupes_identical_values_with_first_locator() -> None:
    """同一路径相同规范化值去重，并使用第一个稳定 locator。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当相同值被误判为歧义或未使用首个 locator 时抛出。
    """

    result = _product_essence_source_truth_result(
        _source_truth_content_intermediate(
            cells=(
                _product_cell("基金名称", "测试主动基金", row_index=0, cell_id="cell-name-first"),
                _product_cell("基金名称", "测试主动基金", row_index=1, cell_id="cell-name-second"),
                _product_cell("基金主代码", "004393", row_index=2, cell_id="cell-code"),
            )
        )
    )

    product = _field_family(result, "product_essence.v1")
    name_locators = [
        anchor.row_locator
        for anchor in product.anchors
        if "field=basic_identity.fund_name" in anchor.row_locator
    ]

    assert product.value["basic_identity"]["fund_name"] == "测试主动基金"
    assert "ambiguous_table_or_locator" not in _gap_codes(product)
    assert name_locators == [
        (
            "field=basic_identity.fund_name; table_id=table-1; "
            "row=0; column=1; cell_id=cell-name-first"
        )
    ]


def test_product_essence_source_truth_paragraph_fallback_for_descriptive_fields() -> None:
    """描述性字段没有 table 值时允许 paragraph fallback。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 paragraph fallback 未形成 public value 或 anchor 时抛出。
    """

    paragraph = _ParagraphStub(
        block_id="paragraph-investment-scope",
        heading_path=("基金简介",),
        text_raw="投资范围：主要投资于具有良好流动性的权益类资产。",
        text_normalized="投资范围：主要投资于具有良好流动性的权益类资产。",
    )
    result = _product_essence_source_truth_result(
        _source_truth_content_intermediate(
            cells=(
                _product_cell("基金名称", "测试主动基金", row_index=0),
                _product_cell("基金主代码", "004393", row_index=1),
            ),
            paragraphs=(paragraph,),
        )
    )

    product = _field_family(result, "product_essence.v1")
    profile = product.value["product_profile"]

    assert profile["investment_scope"] == "主要投资于具有良好流动性的权益类资产。"
    assert any(
        anchor.row_locator == (
            "field=product_profile.investment_scope; block_id=paragraph-investment-scope"
        )
        for anchor in product.anchors
    )


def test_product_essence_source_truth_paragraph_heading_path_fallback() -> None:
    """paragraph heading_path 命中时可抽取描述性字段全文。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 heading_path fallback 未抽取描述性字段时抛出。
    """

    paragraph = _ParagraphStub(
        block_id="paragraph-investment-strategy",
        heading_path=("基金产品资料概要", "投资策略"),
        text_raw="本基金采用自下而上的个股选择策略。",
        text_normalized="本基金采用自下而上的个股选择策略。",
    )
    result = _product_essence_source_truth_result(
        _source_truth_content_intermediate(paragraphs=(paragraph,))
    )

    product = _field_family(result, "product_essence.v1")
    profile = product.value["product_profile"]

    assert profile["investment_strategy"] == "本基金采用自下而上的个股选择策略。"
    assert any(
        anchor.row_locator == (
            "field=product_profile.investment_strategy; block_id=paragraph-investment-strategy"
        )
        for anchor in product.anchors
    )


def test_product_essence_source_truth_missing_keeps_family_missing() -> None:
    """proof-positive content 无允许 label 时 product_essence 仍 missing。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当无 label 内容被误抽取时抛出。
    """

    result = _product_essence_source_truth_result(
        _source_truth_content_intermediate(
            cells=(_product_cell("其他字段", "无关内容", row_index=0),),
            paragraphs=(
                _ParagraphStub(
                    heading_path=("其他章节",),
                    text_raw="无关内容",
                    text_normalized="无关内容",
                ),
            ),
        )
    )

    product = _field_family(result, "product_essence.v1")

    assert product.status == "missing"
    assert product.value == {}
    assert product.anchors == ()
    assert product.candidate_evidence == ()
    assert product.gaps[0].gap_code == "field_family_missing"


def test_product_essence_source_truth_partial_when_required_groups_missing() -> None:
    """只有 fund name/code 时输出 basic_identity，字段族状态为 partial。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 required group 缺失未反映为 partial gap 时抛出。
    """

    result = _product_essence_source_truth_result(
        _source_truth_content_intermediate(
            cells=(
                _product_cell("基金名称", "测试主动基金", row_index=0),
                _product_cell("基金主代码", "004393", row_index=1),
            )
        )
    )

    product = _field_family(result, "product_essence.v1")

    assert product.status == "partial"
    assert product.extraction_mode == "direct"
    assert set(product.value) == {"basic_identity"}
    assert product.value["basic_identity"]["fund_name"] == "测试主动基金"
    assert product.value["basic_identity"]["fund_code"] == "004393"
    assert "field_family_partial" in _gap_codes(product)


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


def test_return_attribution_source_truth_route_suppresses_candidate_evidence() -> None:
    """proof-positive route 进入 direct skeleton，并压制候选证据。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 direct skeleton 混入 candidate evidence 或 public value 时抛出。
    """

    section = _SectionStub(
        section_id="section-nav",
        heading_text_raw="基金份额净值增长率",
        heading_text_normalized="基金份额净值增长率",
        heading_path=("基金份额净值增长率",),
    )

    result = _return_attribution_source_truth_result(
        _source_truth_content_intermediate(sections=(section,))
    )
    family = _field_family(result, "return_attribution.v1")

    assert result.contract_status == "missing"
    assert family.status == "missing"
    assert family.extraction_mode == "missing"
    assert family.value == {}
    assert family.anchors == ()
    assert family.candidate_evidence == ()
    assert _gap_codes(family) == {"field_family_missing"}


def test_return_attribution_source_truth_requires_proof_even_when_candidate_boundary_none() -> None:
    """缺 proof 时即使 candidate_boundary=None，也保留候选证据和 admission gap。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当缺 proof 被 direct route 接受或候选证据丢失时抛出。
    """

    section = _SectionStub(
        section_id="section-nav",
        heading_text_raw="业绩比较基准收益率",
        heading_text_normalized="业绩比较基准收益率",
        heading_path=("业绩比较基准收益率",),
    )

    result = _return_attribution_source_truth_result(
        _source_truth_content_intermediate(sections=(section,), with_source_truth_proof=False)
    )
    family = _field_family(result, "return_attribution.v1")

    assert result.contract_status == "missing"
    assert family.status == "missing"
    assert family.value == {}
    assert family.anchors == ()
    assert family.candidate_evidence
    assert _gap_codes(family) == {
        "candidate_only_not_source_truth",
        "source_truth_admission_missing",
    }


def test_return_attribution_source_truth_rejects_base_admission_invalid_paths() -> None:
    """failure_class 或 source_provenance 非法时不产生 return direct output。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 base admission invalid path 仍返回字段族时抛出。
    """

    section = _SectionStub(
        section_id="section-nav",
        heading_text_raw="基金份额净值增长率",
        heading_text_normalized="基金份额净值增长率",
        heading_path=("基金份额净值增长率",),
    )
    invalid_inputs = (
        _ContentIntermediateStub(
            source_provenance=None,
            source_truth_admission=_source_truth_admission_proof(),
            sections=(section,),
            paragraph_blocks=(),
            table_blocks=(),
        ),
        _ContentIntermediateStub(
            source_provenance=_provenance(),
            failure_class="schema_drift",
            source_truth_admission=_source_truth_admission_proof(),
            sections=(section,),
            paragraph_blocks=(),
            table_blocks=(),
        ),
    )

    for intermediate in invalid_inputs:
        result = _return_attribution_source_truth_result(intermediate)

        assert result.contract_status == "blocked"
        assert result.field_families == ()
        assert result.anchors == ()


def test_return_attribution_source_truth_candidate_boundary_remains_blocked() -> None:
    """candidate_boundary blocked path 不因 proof 存在被提升为 source truth。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 candidate boundary 被 direct route 绕过时抛出。
    """

    boundary = CandidateBoundaryStatus(
        candidate_only=True,
        field_correctness_status="not_proven",
        source_truth_status="not_proven",
    )
    section = _SectionStub(
        section_id="section-nav",
        heading_text_raw="基准收益率",
        heading_text_normalized="基准收益率",
        heading_path=("基准收益率",),
    )

    result = _return_attribution_source_truth_result(
        _ContentIntermediateStub(
            source_provenance=_provenance(),
            candidate_boundary=boundary,
            source_truth_admission=_source_truth_admission_proof(),
            sections=(section,),
            paragraph_blocks=(),
            table_blocks=(),
        )
    )
    family = _field_family(result, "return_attribution.v1")

    assert result.contract_status == "blocked"
    assert result.candidate_boundary is boundary
    assert family.status == "missing"
    assert family.value == {}
    assert family.anchors == ()
    assert family.candidate_evidence
    assert _gap_codes(family) == {"candidate_only_not_source_truth"}


def test_return_attribution_source_truth_extracts_exact_value_shape() -> None:
    """proof-positive FDD content 可抽取 exact return_attribution.v1 value shape。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 public value、anchor 或 direct route 不符合 Slice 2 时抛出。
    """

    cells = (
        _return_attribution_cell(
            "基金份额净值增长率",
            "12.34%",
            row_index=0,
            column_index=1,
            label_axis="column",
        ),
        _return_attribution_cell(
            "业绩比较基准收益率",
            "10.11%",
            row_index=0,
            column_index=2,
            label_axis="column",
        ),
        _return_attribution_cell("管理费率", "1.20%", row_index=1),
        _return_attribution_cell("托管费率", "0.20%", row_index=2),
        _return_attribution_cell(
            "年化跟踪误差",
            "0.45%",
            row_index=3,
            column_index=1,
            label_axis="column",
        ),
    )

    result = _return_attribution_source_truth_result(
        _source_truth_content_intermediate(cells=cells)
    )
    family = _field_family(result, "return_attribution.v1")
    value = family.value
    tracking_error = value["tracking_error"]

    assert result.contract_status == "partial"
    assert family.status == "accepted"
    assert family.extraction_mode == "direct"
    assert family.candidate_evidence == ()
    assert set(value) == {
        "schema_version",
        "nav_benchmark_performance",
        "fee_schedule",
        "tracking_error",
    }
    assert value["schema_version"] == "return_attribution.v1"
    assert value["nav_benchmark_performance"] == {
        "nav_growth_rate": "12.34%",
        "benchmark_return_rate": "10.11%",
    }
    assert value["fee_schedule"] == {
        "management_fee": "1.20%",
        "custody_fee": "0.20%",
    }
    assert isinstance(tracking_error, TrackingErrorValue)
    assert tracking_error.value == Decimal("0.0045")
    assert tracking_error.value_text == "0.45%"
    assert tracking_error.unit == "ratio"
    assert tracking_error.period_label == "报告期"
    assert tracking_error.period_start is None
    assert tracking_error.period_end is None
    assert tracking_error.annualized
    assert tracking_error.source_type == "direct_disclosure"
    assert tracking_error.calculation_method == "disclosed"
    assert tracking_error.benchmark_identity_status == "missing"
    assert tracking_error.benchmark_index_name is None
    assert tracking_error.benchmark_index_code is None
    assert tracking_error.fund_series_source is None
    assert tracking_error.index_series_source is None
    assert tracking_error.observation_count is None
    assert tracking_error.frequency == "annual_report_period"
    assert tracking_error.annualization_factor is None
    assert tracking_error.input_period_complete
    assert "直接披露" in tracking_error.provenance_note
    assert family.gaps == ()
    assert len(family.anchors) == 5
    assert {anchor.source_kind for anchor in family.anchors} == {"annual_report"}


def test_return_attribution_source_truth_partial_when_required_groups_missing() -> None:
    """只形成部分 top-level subvalue 时，return_attribution.v1 返回 partial。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当部分值被误判为 accepted 或 missing 时抛出。
    """

    cells = (
        _return_attribution_cell(
            "基金份额净值增长率",
            "8.00%",
            row_index=0,
            column_index=1,
            label_axis="column",
        ),
        _return_attribution_cell(
            "业绩比较基准收益率",
            "6.00%",
            row_index=0,
            column_index=2,
            label_axis="column",
        ),
    )

    result = _return_attribution_source_truth_result(
        _source_truth_content_intermediate(cells=cells)
    )
    family = _field_family(result, "return_attribution.v1")

    assert family.status == "partial"
    assert family.extraction_mode == "direct"
    assert set(family.value) == {"schema_version", "nav_benchmark_performance"}
    assert _gap_codes(family) == {"field_family_partial"}
    assert {gap.source_field_path for gap in family.gaps} == {"fee_schedule", "tracking_error"}


def test_return_attribution_source_truth_missing_when_no_allowed_labels() -> None:
    """proof-positive 但无允许 label 时，public 结果保持 missing。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当无关内容被提升为 public value 时抛出。
    """

    cells = (_return_attribution_cell("无关指标", "99.99%", row_index=0),)

    result = _return_attribution_source_truth_result(
        _source_truth_content_intermediate(cells=cells)
    )
    family = _field_family(result, "return_attribution.v1")

    assert family.status == "missing"
    assert family.extraction_mode == "missing"
    assert family.value == {}
    assert family.anchors == ()
    assert family.candidate_evidence == ()
    assert _gap_codes(family) == {"field_family_missing"}


def test_return_attribution_source_truth_fee_schedule_one_side_is_partial() -> None:
    """仅管理费或托管费存在时，fee_schedule 可作为 partial subvalue 输出。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当单侧费率被丢弃或扩展到未授权 subkey 时抛出。
    """

    cells = (_return_attribution_cell("管理费率", "1.50%", row_index=0),)

    result = _return_attribution_source_truth_result(
        _source_truth_content_intermediate(cells=cells)
    )
    family = _field_family(result, "return_attribution.v1")

    assert family.status == "partial"
    assert family.value["fee_schedule"] == {
        "management_fee": "1.50%",
        "custody_fee": None,
    }
    assert set(family.value["fee_schedule"]) == {"management_fee", "custody_fee"}
    assert "field_family_partial" in _gap_codes(family)


@pytest.mark.parametrize(
    "cells",
    (
        (
            _return_attribution_cell(
                "基金份额净值增长率",
                "8.00%",
                row_index=0,
                column_index=1,
                label_axis="column",
            ),
        ),
        (
            _return_attribution_cell(
                "基金份额净值增长率",
                "8.00%",
                row_index=0,
                column_index=1,
                label_axis="column",
            ),
            _return_attribution_cell(
                "业绩比较基准收益率",
                "6.00%",
                row_index=1,
                column_index=2,
                label_axis="column",
            ),
        ),
    ),
)
def test_return_attribution_source_truth_nav_requires_both_sides_same_row(
    cells: tuple[_CellStub, ...],
) -> None:
    """NAV/benchmark 缺任一侧或不同 row 时，表现 subvalue fail closed。

    Args:
        cells: NAV/benchmark 测试单元格。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当非同一行配对被采信时抛出。
    """

    result = _return_attribution_source_truth_result(
        _source_truth_content_intermediate(cells=cells)
    )
    family = _field_family(result, "return_attribution.v1")

    assert family.status == "missing"
    assert "nav_benchmark_performance" not in family.value
    assert family.anchors == ()


def test_return_attribution_source_truth_nav_ambiguous_pairs_fail_closed() -> None:
    """多组 NAV/benchmark 同行配对时，表现 subvalue 必须 fail closed。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当多行配对被任意采信时抛出。
    """

    cells = (
        _return_attribution_cell(
            "基金份额净值增长率",
            "8.00%",
            row_index=0,
            column_index=1,
            label_axis="column",
        ),
        _return_attribution_cell(
            "业绩比较基准收益率",
            "6.00%",
            row_index=0,
            column_index=2,
            label_axis="column",
        ),
        _return_attribution_cell(
            "基金份额净值增长率",
            "9.00%",
            row_index=1,
            column_index=1,
            label_axis="column",
        ),
        _return_attribution_cell(
            "业绩比较基准收益率",
            "7.00%",
            row_index=1,
            column_index=2,
            label_axis="column",
        ),
    )

    result = _return_attribution_source_truth_result(
        _source_truth_content_intermediate(cells=cells)
    )
    family = _field_family(result, "return_attribution.v1")

    assert family.status == "missing"
    assert family.value == {}
    assert family.anchors == ()
    assert _gap_codes(family) == {"ambiguous_table_or_locator", "field_family_missing"}
    assert {gap.source_field_path for gap in family.gaps if gap.gap_code == "ambiguous_table_or_locator"} == {
        "nav_benchmark_performance"
    }


def test_return_attribution_source_truth_tracking_error_actual_disclosure_value() -> None:
    """实际披露的跟踪误差构造完整 TrackingErrorValue。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 tracking_error 不是完整 direct disclosure 结构时抛出。
    """

    paragraph = _ParagraphStub(
        block_id="paragraph-tracking",
        section_id="section-tracking",
        heading_path=("基金净值表现",),
        text_raw="本报告期基金年化跟踪误差为0.88%。",
        text_normalized="本报告期基金年化跟踪误差为0.88%。",
    )

    result = _return_attribution_source_truth_result(
        _source_truth_content_intermediate(paragraphs=(paragraph,))
    )
    family = _field_family(result, "return_attribution.v1")
    tracking_error = family.value["tracking_error"]

    assert family.status == "partial"
    assert isinstance(tracking_error, TrackingErrorValue)
    assert tracking_error.value == Decimal("0.0088")
    assert tracking_error.value_text == "0.88%"
    assert tracking_error.period_label == "本报告期"
    assert tracking_error.annualized
    assert tracking_error.frequency == "annual_report_period"
    assert tracking_error.input_period_complete
    assert tracking_error.fund_series_source is None
    assert tracking_error.index_series_source is None


def test_return_attribution_source_truth_rejects_tracking_error_target_context() -> None:
    """目标、控制或上限语境的跟踪误差不得进入 public value。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当目标/控制语境被当作实际披露时抛出。
    """

    paragraph = _ParagraphStub(
        block_id="paragraph-tracking-target",
        section_id="section-tracking",
        heading_path=("投资目标",),
        text_raw="本基金力争将跟踪误差控制在不超过4.00%，偏离度绝对值目标较低。",
        text_normalized="本基金力争将跟踪误差控制在不超过4.00%，偏离度绝对值目标较低。",
    )

    result = _return_attribution_source_truth_result(
        _source_truth_content_intermediate(paragraphs=(paragraph,))
    )
    family = _field_family(result, "return_attribution.v1")

    assert family.status == "missing"
    assert family.value == {}
    assert family.anchors == ()
    assert "field_family_missing" in _gap_codes(family)


def test_return_attribution_source_truth_rejects_table_cell_tracking_error_target_context() -> None:
    """table cell 中目标/控制语境的跟踪误差不得进入 public value。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 table cell 目标/控制语境被当作实际披露时抛出。
    """

    cells = (
        _return_attribution_cell(
            "跟踪误差控制目标",
            "不超过4.00%",
            row_index=0,
            column_index=1,
        ),
    )

    result = _return_attribution_source_truth_result(
        _source_truth_content_intermediate(cells=cells)
    )
    family = _field_family(result, "return_attribution.v1")

    assert family.status == "missing"
    assert family.value == {}
    assert family.anchors == ()
    assert "field_family_missing" in _gap_codes(family)


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


# ── manager_profile source-truth Slice 1 skeleton ─────────────────────────


def test_manager_profile_source_truth_route_suppresses_candidate_evidence() -> None:
    """proof-positive direct-route missing 必须抑制 manager_profile candidate evidence。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 direct-route missing 回退到 S6-D candidate evidence 时抛出。
    """

    section = _SectionStub(
        section_id="section-manager",
        heading_text_raw="基金管理人及基金经理情况",
        heading_text_normalized="基金管理人及基金经理情况",
        heading_path=("基金管理人及基金经理情况",),
    )
    result = _manager_profile_source_truth_result(
        _ContentIntermediateStub(
            source_provenance=_provenance(),
            source_truth_admission=_source_truth_admission_proof(),
            sections=(section,),
            paragraph_blocks=(),
            table_blocks=(),
        )
    )

    family = _field_family(result, "manager_profile.v1")
    current_stage = _field_family(result, "current_stage.v1")
    core_risk = _field_family(result, "core_risk.v1")

    assert result.contract_status == "missing"
    assert family.status == "missing"
    assert family.extraction_mode == "missing"
    assert family.value == {}
    assert family.anchors == ()
    assert family.candidate_evidence == ()
    assert _gap_codes(family) == {"field_family_missing"}
    assert current_stage.status == "missing"
    assert current_stage.value == {}
    assert current_stage.anchors == ()
    assert core_risk.status == "missing"
    assert core_risk.value == {}
    assert core_risk.anchors == ()


def test_manager_profile_source_truth_requires_proof_even_when_candidate_boundary_none() -> None:
    """candidate_boundary=None 缺 proof 时保留 candidate-only 路径和 admission missing gap。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当缺 proof 被误认为 source truth 或丢失 candidate evidence 时抛出。
    """

    section = _SectionStub(
        section_id="section-manager",
        heading_text_raw="基金经理简介",
        heading_text_normalized="基金经理简介",
        heading_path=("基金经理简介",),
    )

    result = _manager_profile_source_truth_result(
        _ContentIntermediateStub(
            source_provenance=_provenance(),
            candidate_boundary=None,
            source_truth_admission=None,
            sections=(section,),
            paragraph_blocks=(),
            table_blocks=(),
        )
    )

    family = _field_family(result, "manager_profile.v1")

    assert result.contract_status == "missing"
    assert family.status == "missing"
    assert family.value == {}
    assert family.anchors == ()
    assert family.candidate_evidence
    assert _gap_codes(family) == {
        "candidate_only_not_source_truth",
        "source_truth_admission_missing",
    }


def test_manager_profile_source_truth_rejects_base_admission_invalid_paths() -> None:
    """base admission 非法路径必须先阻断，不进入 manager_profile direct skeleton。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 base admission failure 仍返回字段族时抛出。
    """

    missing_provenance = _manager_profile_source_truth_result(
        _ContentIntermediateStub(
            source_provenance=None,
            source_truth_admission=_source_truth_admission_proof(),
            sections=(
                _SectionStub(
                    heading_text_raw="基金经理简介",
                    heading_text_normalized="基金经理简介",
                    heading_path=("基金经理简介",),
                ),
            ),
            paragraph_blocks=(),
            table_blocks=(),
        )
    )
    schema_drift = _manager_profile_source_truth_result(
        _ContentIntermediateStub(
            source_provenance=_provenance(),
            failure_class="schema_drift",
            source_truth_admission=_source_truth_admission_proof(),
            sections=(
                _SectionStub(
                    heading_text_raw="基金经理简介",
                    heading_text_normalized="基金经理简介",
                    heading_path=("基金经理简介",),
                ),
            ),
            paragraph_blocks=(),
            table_blocks=(),
        )
    )

    assert missing_provenance.contract_status == "blocked"
    assert missing_provenance.field_families == ()
    assert missing_provenance.gaps[0].gap_code == "source_provenance_unsafe"
    assert schema_drift.contract_status == "blocked"
    assert schema_drift.field_families == ()
    assert schema_drift.gaps[0].gap_code == "candidate_boundary_blocked"


def test_manager_profile_source_truth_candidate_boundary_remains_blocked() -> None:
    """candidate_boundary 输入仍 blocked，且 manager_profile 不进入 source-truth direct route。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 candidate boundary 被 direct route 绕过时抛出。
    """

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

    result = _manager_profile_source_truth_result(
        _ContentIntermediateStub(
            source_provenance=_provenance(),
            candidate_boundary=boundary,
            source_truth_admission=_source_truth_admission_proof(),
            sections=(section,),
            paragraph_blocks=(),
            table_blocks=(),
        )
    )

    family = _field_family(result, "manager_profile.v1")

    assert result.contract_status == "blocked"
    assert result.candidate_boundary is boundary
    assert family.status == "missing"
    assert family.extraction_mode == "missing"
    assert family.value == {}
    assert family.anchors == ()
    assert family.candidate_evidence
    assert _gap_codes(family) == {"candidate_only_not_source_truth"}


# ── manager_profile source-truth Slice 3 values ────────────────────────────


def test_manager_profile_source_truth_extracts_roster_strategy_turnover_shape() -> None:
    """proof-positive FDD 可抽取 roster、strategy/outlook 和 turnover exact shape。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 Slice 3 public value、anchor 或越界 family 不符合计划时抛出。
    """

    roster_table = _TableStub(
        table_id="table-roster",
        section_id="section-manager",
        heading_text="基金经理情况",
        table_caption_or_nearby_heading="基金经理情况",
        heading_path=("基金管理人及基金经理情况",),
        cells=(
            _manager_profile_cell("姓名", "张三", row_index=0, column_index=0),
            _manager_profile_cell("职务", "基金经理", row_index=0, column_index=1),
            _manager_profile_cell("任职日期", "2020-01-01", row_index=0, column_index=2),
        ),
    )
    turnover_table = _TableStub(
        table_id="table-turnover",
        section_id="section-turnover",
        heading_text="报告期内股票换手率",
        table_caption_or_nearby_heading="报告期内股票换手率",
        heading_path=("交易情况",),
        cells=(
            _manager_profile_cell(
                "报告期内股票换手率",
                "123.45%",
                row_index=0,
                column_index=1,
                table_id="table-turnover",
                label_axis="row",
            ),
            _manager_profile_cell(
                "换手率计算口径",
                "双边成交金额除以平均股票市值",
                row_index=1,
                column_index=1,
                table_id="table-turnover",
                label_axis="row",
            ),
        ),
    )
    strategy = _ParagraphStub(
        block_id="paragraph-strategy",
        section_id="section-strategy",
        heading_path=("报告期内基金投资策略和运作分析",),
        text_raw="本报告期坚持均衡配置。",
        text_normalized="本报告期坚持均衡配置。",
    )
    outlook = _ParagraphStub(
        block_id="paragraph-outlook",
        section_id="section-outlook",
        heading_path=("后市展望",),
        text_raw="后续将关注基本面变化。",
        text_normalized="后续将关注基本面变化。",
    )

    result = _manager_profile_source_truth_result(
        _ContentIntermediateStub(
            source_provenance=_provenance(),
            source_truth_admission=_source_truth_admission_proof(),
            sections=(),
            paragraph_blocks=(strategy, outlook),
            table_blocks=(roster_table, turnover_table),
        )
    )

    family = _field_family(result, "manager_profile.v1")
    value = family.value
    roster = value["portfolio_managers"]
    manager = roster["portfolio_managers"][0]

    assert result.contract_status == "partial"
    assert family.status == "partial"
    assert family.extraction_mode == "direct"
    assert family.candidate_evidence == ()
    assert set(value) == {
        "schema_version",
        "portfolio_managers",
        "manager_strategy_text",
        "turnover_rate",
    }
    assert value["schema_version"] == "manager_profile.v1"
    assert roster["schema_version"] == "portfolio_manager_tenure_list.v1"
    assert roster["fund_code"] == "004393"
    assert roster["report_year"] == 2025
    assert manager["name"] == "张三"
    assert manager["role"] == "基金经理"
    assert manager["start_date"] == "2020-01-01"
    assert manager["source_anchor"]["row_locator"] == "portfolio_manager:张三"
    assert value["manager_strategy_text"] == {
        "strategy_summary": "本报告期坚持均衡配置。",
        "market_outlook": "后续将关注基本面变化。",
    }
    assert value["turnover_rate"] == {
        "turnover_rate": "123.45%",
        "turnover_basis": "双边成交金额除以平均股票市值",
    }
    assert {gap.source_field_path for gap in family.gaps} == {
        "manager_alignment",
        "holdings_snapshot",
    }
    assert len(family.anchors) == 3
    assert all(anchor.source_kind == "annual_report" for anchor in family.anchors)
    current_stage = _field_family(result, "current_stage.v1")
    assert current_stage.status == "partial"
    assert set(current_stage.value) == {"schema_version", "portfolio_managers"}
    assert current_stage.anchors
    assert current_stage.candidate_evidence == ()
    assert _field_family(result, "core_risk.v1").value == {}
    assert _field_family(result, "core_risk.v1").anchors == ()


def test_manager_profile_source_truth_partial_when_required_groups_missing() -> None:
    """只形成一个 Slice 3 subvalue 时返回 partial，缺失 top-level 用 gaps 表示。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当缺失 top-level key 被 None 占位或状态错误时抛出。
    """

    strategy = _ParagraphStub(
        block_id="paragraph-strategy",
        section_id="section-strategy",
        heading_path=("投资策略和运作分析",),
        text_raw="本报告期采用自下而上的选股策略。",
        text_normalized="本报告期采用自下而上的选股策略。",
    )
    basis_only = _ParagraphStub(
        block_id="paragraph-turnover-basis",
        section_id="section-turnover",
        heading_path=("换手率计算口径",),
        text_raw="换手率计算口径为双边成交金额。",
        text_normalized="换手率计算口径为双边成交金额。",
    )

    result = _manager_profile_source_truth_result(
        _ContentIntermediateStub(
            source_provenance=_provenance(),
            source_truth_admission=_source_truth_admission_proof(),
            sections=(),
            paragraph_blocks=(strategy, basis_only),
            table_blocks=(),
        )
    )

    family = _field_family(result, "manager_profile.v1")

    assert family.status == "partial"
    assert family.extraction_mode == "direct"
    assert set(family.value) == {"schema_version", "manager_strategy_text"}
    assert family.value["manager_strategy_text"] == {
        "strategy_summary": "本报告期采用自下而上的选股策略。",
        "market_outlook": None,
    }
    assert "turnover_rate" not in family.value
    assert "portfolio_managers" not in family.value
    assert "turnover_rate" not in family.value
    assert {gap.source_field_path for gap in family.gaps} == {
        "portfolio_managers",
        "turnover_rate",
        "manager_alignment",
        "holdings_snapshot",
    }


def test_manager_profile_source_truth_missing_when_no_allowed_labels() -> None:
    """proof-positive content 没有 Slice 3 allowed label 时保持 direct-route missing。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当无关内容被误抽取或回退到 candidate evidence 时抛出。
    """

    result = _manager_profile_source_truth_result(
        _ContentIntermediateStub(
            source_provenance=_provenance(),
            source_truth_admission=_source_truth_admission_proof(),
            sections=(
                _SectionStub(
                    heading_text_raw="其他章节",
                    heading_text_normalized="其他章节",
                    heading_path=("其他章节",),
                ),
            ),
            paragraph_blocks=(
                _ParagraphStub(
                    heading_path=("其他章节",),
                    text_raw="无关内容。",
                    text_normalized="无关内容。",
                ),
            ),
            table_blocks=(),
        )
    )

    family = _field_family(result, "manager_profile.v1")

    assert result.contract_status == "missing"
    assert family.status == "missing"
    assert family.extraction_mode == "missing"
    assert family.value == {}
    assert family.anchors == ()
    assert family.candidate_evidence == ()
    assert _gap_codes(family) == {"field_family_missing"}


def test_manager_profile_source_truth_ambiguous_duplicate_omits_conflicting_value() -> None:
    """同一路径冲突稳定值必须省略对应 turnover_rate 并追加 ambiguity gap。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当冲突 turnover 值进入 public value 时抛出。
    """

    turnover_table = _TableStub(
        table_id="table-turnover",
        section_id="section-turnover",
        heading_text="报告期内股票换手率",
        table_caption_or_nearby_heading="报告期内股票换手率",
        heading_path=("交易情况",),
        cells=(
            _manager_profile_cell(
                "报告期内股票换手率",
                "100.00%",
                row_index=0,
                table_id="table-turnover",
                label_axis="row",
            ),
            _manager_profile_cell(
                "报告期内股票换手率",
                "120.00%",
                row_index=1,
                table_id="table-turnover",
                label_axis="row",
            ),
        ),
    )
    strategy = _ParagraphStub(
        block_id="paragraph-strategy",
        section_id="section-strategy",
        heading_path=("投资策略",),
        text_raw="本报告期维持既定投资策略。",
        text_normalized="本报告期维持既定投资策略。",
    )

    result = _manager_profile_source_truth_result(
        _ContentIntermediateStub(
            source_provenance=_provenance(),
            source_truth_admission=_source_truth_admission_proof(),
            sections=(),
            paragraph_blocks=(strategy,),
            table_blocks=(turnover_table,),
        )
    )

    family = _field_family(result, "manager_profile.v1")

    assert family.status == "partial"
    assert "manager_strategy_text" in family.value
    assert "turnover_rate" not in family.value
    assert "ambiguous_table_or_locator" in _gap_codes(family)
    assert any(
        gap.source_field_path == "turnover_rate.turnover_rate"
        for gap in family.gaps
        if gap.gap_code == "ambiguous_table_or_locator"
    )
    assert all("field=turnover_rate.turnover_rate" not in anchor.row_locator for anchor in family.anchors)


def test_manager_profile_source_truth_skips_unstable_locator() -> None:
    """unstable table、paragraph 或 cell locator 不得进入 manager_profile source-truth value。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 unstable locator 被抽取为 public value 时抛出。
    """

    unstable_roster_table = _TableStub(
        table_id="table-roster",
        section_id="section-manager",
        heading_text="基金经理情况",
        table_caption_or_nearby_heading="基金经理情况",
        heading_path=("基金经理情况",),
        locator_stability="unstable",
        cells=(
            _manager_profile_cell("姓名", "张三", row_index=0, column_index=0),
            _manager_profile_cell("职务", "基金经理", row_index=0, column_index=1),
        ),
    )
    unstable_turnover_table = _TableStub(
        table_id="table-turnover",
        section_id="section-turnover",
        heading_text="报告期内股票换手率",
        table_caption_or_nearby_heading="报告期内股票换手率",
        heading_path=("交易情况",),
        cells=(
            _manager_profile_cell(
                "报告期内股票换手率",
                "80.00%",
                row_index=0,
                table_id="table-turnover",
                label_axis="row",
                locator_stability="unstable",
            ),
        ),
    )
    unstable_strategy = _ParagraphStub(
        block_id="paragraph-strategy",
        section_id="section-strategy",
        heading_path=("投资策略和运作分析",),
        text_raw="不稳定 locator 的策略文本。",
        text_normalized="不稳定 locator 的策略文本。",
        locator_stability="unstable",
    )

    result = _manager_profile_source_truth_result(
        _ContentIntermediateStub(
            source_provenance=_provenance(),
            source_truth_admission=_source_truth_admission_proof(),
            sections=(),
            paragraph_blocks=(unstable_strategy,),
            table_blocks=(unstable_roster_table, unstable_turnover_table),
        )
    )

    family = _field_family(result, "manager_profile.v1")

    assert family.status == "missing"
    assert family.extraction_mode == "missing"
    assert family.value == {}
    assert family.anchors == ()
    assert family.candidate_evidence == ()
    assert "ambiguous_table_or_locator" not in _gap_codes(family)


def test_manager_profile_source_truth_roster_broad_heading_does_not_authorize_non_manager_row() -> None:
    """broad manager heading 下非基金经理角色行不得发出 portfolio_managers。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 heading_path 自授权非经理行时抛出。
    """

    roster_table = _TableStub(
        table_id="table-roster",
        section_id="section-manager",
        heading_text="主要人员情况",
        table_caption_or_nearby_heading="基金经理情况",
        heading_path=("基金管理人及基金经理情况",),
        cells=(
            _manager_profile_cell("姓名", "李四", row_index=0, column_index=0),
            _manager_profile_cell("职务", "研究员", row_index=0, column_index=1),
        ),
    )

    result = _manager_profile_source_truth_result(
        _ContentIntermediateStub(
            source_provenance=_provenance(),
            source_truth_admission=_source_truth_admission_proof(),
            sections=(),
            paragraph_blocks=(),
            table_blocks=(roster_table,),
        )
    )

    family = _field_family(result, "manager_profile.v1")

    assert family.status == "missing"
    assert family.value == {}
    assert family.anchors == ()
    assert family.candidate_evidence == ()


def test_manager_profile_source_truth_strategy_requires_heading_path_membership() -> None:
    """非 strategy heading 下正文包含策略 token 时不得发出 manager_strategy_text。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当正文 token 绕过 heading gate 时抛出。
    """

    paragraph = _ParagraphStub(
        block_id="paragraph-other",
        section_id="section-other",
        heading_path=("其他重要事项",),
        text_raw="本段提到投资策略和运作分析，但不位于策略章节。",
        text_normalized="本段提到投资策略和运作分析，但不位于策略章节。",
    )

    result = _manager_profile_source_truth_result(
        _ContentIntermediateStub(
            source_provenance=_provenance(),
            source_truth_admission=_source_truth_admission_proof(),
            sections=(),
            paragraph_blocks=(paragraph,),
            table_blocks=(),
        )
    )

    family = _field_family(result, "manager_profile.v1")

    assert family.status == "missing"
    assert "manager_strategy_text" not in family.value
    assert family.anchors == ()
    assert family.candidate_evidence == ()


def test_manager_profile_source_truth_ambiguous_roster_name_omits_conflicting_entry() -> None:
    """同名经理披露 role/date 冲突时省略该 entry 并追加 portfolio ambiguity。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当冲突同名经理进入 public value 时抛出。
    """

    first_table = _TableStub(
        table_id="table-roster-first",
        section_id="section-manager",
        heading_text="基金经理情况",
        table_caption_or_nearby_heading="基金经理情况",
        heading_path=("基金经理情况",),
        cells=(
            _manager_profile_cell(
                "姓名", "张三", row_index=0, column_index=0, table_id="table-roster-first"
            ),
            _manager_profile_cell(
                "职务", "基金经理", row_index=0, column_index=1, table_id="table-roster-first"
            ),
            _manager_profile_cell(
                "任职日期", "2020-01-01", row_index=0, column_index=2, table_id="table-roster-first"
            ),
        ),
    )
    second_table = _TableStub(
        table_id="table-roster-second",
        section_id="section-manager",
        heading_text="基金经理情况",
        table_caption_or_nearby_heading="基金经理情况",
        heading_path=("基金经理情况",),
        cells=(
            _manager_profile_cell(
                "姓名", "张三", row_index=0, column_index=0, table_id="table-roster-second"
            ),
            _manager_profile_cell(
                "职务", "基金经理", row_index=0, column_index=1, table_id="table-roster-second"
            ),
            _manager_profile_cell(
                "任职日期", "2021-01-01", row_index=0, column_index=2, table_id="table-roster-second"
            ),
        ),
    )

    result = _manager_profile_source_truth_result(
        _ContentIntermediateStub(
            source_provenance=_provenance(),
            source_truth_admission=_source_truth_admission_proof(),
            sections=(),
            paragraph_blocks=(),
            table_blocks=(first_table, second_table),
        )
    )

    family = _field_family(result, "manager_profile.v1")

    assert "portfolio_managers" not in family.value
    assert "ambiguous_table_or_locator" in _gap_codes(family)
    assert any(
        gap.source_field_path == "portfolio_managers"
        for gap in family.gaps
        if gap.gap_code == "ambiguous_table_or_locator"
    )


def test_manager_profile_source_truth_identical_roster_duplicate_keeps_first_locator() -> None:
    """同名经理披露值完全相同时只保留首个 locator 且不产生 ambiguity。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当同值重复经理被误判冲突或重复输出时抛出。
    """

    first_table = _TableStub(
        table_id="table-roster-first",
        section_id="section-manager",
        heading_text="基金经理情况",
        table_caption_or_nearby_heading="基金经理情况",
        heading_path=("基金经理情况",),
        cells=(
            _manager_profile_cell(
                "姓名", "张三", row_index=0, column_index=0, table_id="table-roster-first"
            ),
            _manager_profile_cell(
                "职务", "基金经理", row_index=0, column_index=1, table_id="table-roster-first"
            ),
            _manager_profile_cell(
                "任职日期", "2020-01-01", row_index=0, column_index=2, table_id="table-roster-first"
            ),
        ),
    )
    second_table = _TableStub(
        table_id="table-roster-second",
        section_id="section-manager",
        heading_text="基金经理情况",
        table_caption_or_nearby_heading="基金经理情况",
        heading_path=("基金经理情况",),
        cells=(
            _manager_profile_cell(
                "姓名", "张三", row_index=0, column_index=0, table_id="table-roster-second"
            ),
            _manager_profile_cell(
                "职务", "基金经理", row_index=0, column_index=1, table_id="table-roster-second"
            ),
            _manager_profile_cell(
                "任职日期", "2020-01-01", row_index=0, column_index=2, table_id="table-roster-second"
            ),
        ),
    )

    result = _manager_profile_source_truth_result(
        _ContentIntermediateStub(
            source_provenance=_provenance(),
            source_truth_admission=_source_truth_admission_proof(),
            sections=(),
            paragraph_blocks=(),
            table_blocks=(first_table, second_table),
        )
    )

    family = _field_family(result, "manager_profile.v1")
    roster = family.value["portfolio_managers"]
    managers = roster["portfolio_managers"]

    assert len(managers) == 1
    assert managers[0]["name"] == "张三"
    assert managers[0]["source_anchor"]["table_id"] == "table-roster-first"
    assert len(family.anchors) == 1
    assert family.anchors[0].table_id == "table-roster-first"
    assert "ambiguous_table_or_locator" not in _gap_codes(family)


def test_manager_profile_source_truth_extracts_alignment_without_judgment() -> None:
    """proof-positive FDD 只抽取经理/从业人员持有披露，不生成利益一致性判断。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 judgment 非 None 或候选证据泄漏时抛出。
    """

    manager_paragraph = _ParagraphStub(
        block_id="paragraph-manager-holding",
        section_id="section-alignment",
        heading_path=("基金经理持有本基金情况",),
        text_raw="本基金基金经理持有本开放式基金份额区间为100万份以上。",
        text_normalized="本基金基金经理持有本开放式基金份额区间为100万份以上。",
    )
    employee_paragraph = _ParagraphStub(
        block_id="paragraph-employee-holding",
        section_id="section-alignment",
        heading_path=("基金管理人从业人员持有本基金情况",),
        text_raw="基金管理人所有从业人员持有本基金份额区间为50万份至100万份。",
        text_normalized="基金管理人所有从业人员持有本基金份额区间为50万份至100万份。",
    )

    result = _manager_profile_source_truth_result(
        _ContentIntermediateStub(
            source_provenance=_provenance(),
            source_truth_admission=_source_truth_admission_proof(),
            sections=(),
            paragraph_blocks=(manager_paragraph, employee_paragraph),
            table_blocks=(),
        )
    )

    family = _field_family(result, "manager_profile.v1")
    alignment = family.value["manager_alignment"]

    assert family.status == "partial"
    assert family.extraction_mode == "direct"
    assert family.candidate_evidence == ()
    assert alignment == {
        "manager_holding": "本基金基金经理持有本开放式基金份额区间为100万份以上。",
        "employee_holding": "基金管理人所有从业人员持有本基金份额区间为50万份至100万份。",
        "judgment": None,
    }
    assert "利益一致" not in str(alignment)
    assert {gap.source_field_path for gap in family.gaps} == {
        "portfolio_managers",
        "manager_strategy_text",
        "turnover_rate",
        "holdings_snapshot",
    }


def test_manager_profile_source_truth_extracts_holdings_snapshot_without_risk_or_stage_fields() -> None:
    """proof-positive FDD 只抽取持仓快照原始行，不向阶段或风险字段族写值。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当持仓快照扩展出风险/阶段字段或跨族泄漏时抛出。
    """

    top_table = _TableStub(
        table_id="table-top-holdings",
        section_id="section-holdings",
        heading_text="前十名股票投资明细",
        table_caption_or_nearby_heading="前十名股票投资明细",
        heading_path=("投资组合", "前十名股票投资明细"),
        cells=(
            _manager_profile_holdings_cell("股票代码", "600000", row_index=0, column_index=0, table_id="table-top-holdings"),
            _manager_profile_holdings_cell("股票名称", "浦发银行", row_index=0, column_index=1, table_id="table-top-holdings"),
            _manager_profile_holdings_cell("公允价值", "1,234,567.89", row_index=0, column_index=2, table_id="table-top-holdings"),
        ),
    )
    industry_table = _TableStub(
        table_id="table-industry",
        section_id="section-industry",
        heading_text="报告期末按行业分类的股票投资组合",
        table_caption_or_nearby_heading="报告期末按行业分类的股票投资组合",
        heading_path=("投资组合", "报告期末按行业分类的股票投资组合"),
        cells=(
            _manager_profile_holdings_cell("行业类别", "制造业", row_index=0, column_index=0, table_id="table-industry"),
            _manager_profile_holdings_cell("公允价值", "2,000,000.00", row_index=0, column_index=1, table_id="table-industry"),
            _manager_profile_holdings_cell("占基金资产净值比例", "12.34%", row_index=0, column_index=2, table_id="table-industry"),
        ),
    )

    result = _manager_profile_source_truth_result(
        _ContentIntermediateStub(
            source_provenance=_provenance(),
            source_truth_admission=_source_truth_admission_proof(),
            sections=(),
            paragraph_blocks=(),
            table_blocks=(top_table, industry_table),
        )
    )

    family = _field_family(result, "manager_profile.v1")
    holdings = family.value["holdings_snapshot"]

    assert family.status == "partial"
    assert set(holdings) == {
        "top_holdings",
        "top_holdings_status",
        "top_holdings_source",
        "industry_distribution",
        "industry_distribution_status",
    }
    assert holdings["top_holdings_status"] == "direct_top_ten"
    assert holdings["top_holdings_source"] == "top_ten"
    assert holdings["industry_distribution_status"] == "direct"
    assert holdings["top_holdings"] == [
        {"股票代码": "600000", "股票名称": "浦发银行", "公允价值": "1,234,567.89"}
    ]
    assert holdings["industry_distribution"] == [
        {"行业类别": "制造业", "公允价值": "2,000,000.00", "占基金资产净值比例": "12.34%"}
    ]
    assert "concentration" not in holdings
    assert "style_drift" not in holdings
    assert "core_risk" not in holdings
    assert "current_stage" not in holdings
    current_stage = _field_family(result, "current_stage.v1")
    assert current_stage.status == "partial"
    assert set(current_stage.value) == {"schema_version", "holdings_snapshot"}
    assert current_stage.anchors
    assert current_stage.candidate_evidence == ()
    assert _field_family(result, "core_risk.v1").value == {}
    assert _field_family(result, "core_risk.v1").anchors == ()


def test_manager_profile_source_truth_rejects_generic_holding_without_guard_context() -> None:
    """generic 持有本基金 source 缺少经理/从业人员同源 guard 时不得抽取。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 generic holding token 自授权进入 public value 时抛出。
    """

    table = _TableStub(
        table_id="table-generic-holding",
        section_id="section-other",
        heading_text="其他持有情况",
        table_caption_or_nearby_heading="其他持有情况",
        heading_path=("其他持有情况",),
        cells=(
            _CellStub(
                cell_id="cell-generic-holding",
                table_id="table-generic-holding",
                row_index=0,
                column_index=0,
                row_label_path=("持有本基金",),
                column_header_path=("内容",),
                cell_text="持有本基金",
                cell_text_normalized="持有本基金",
            ),
        ),
    )

    result = _manager_profile_source_truth_result(
        _ContentIntermediateStub(
            source_provenance=_provenance(),
            source_truth_admission=_source_truth_admission_proof(),
            sections=(),
            paragraph_blocks=(),
            table_blocks=(table,),
        )
    )

    family = _field_family(result, "manager_profile.v1")

    assert family.status == "missing"
    assert family.value == {}
    assert family.anchors == ()
    assert family.candidate_evidence == ()
    assert _gap_codes(family) == {"field_family_missing"}


def test_manager_profile_source_truth_same_value_multi_locator_keeps_first_anchor() -> None:
    """同一 alignment 值跨多个稳定 locator 重复时保留首个 anchor。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当同值重复产生 ambiguity 或锚点不稳定时抛出。
    """

    first = _ParagraphStub(
        block_id="paragraph-holding-first",
        section_id="section-first",
        heading_path=("基金经理持有本基金情况",),
        text_raw="基金经理持有本基金份额区间为100万份以上。",
        text_normalized="基金经理持有本基金份额区间为100万份以上。",
    )
    second = _ParagraphStub(
        block_id="paragraph-holding-second",
        section_id="section-second",
        heading_path=("基金经理持有本基金情况",),
        text_raw="基金经理持有本基金份额区间为100万份以上。",
        text_normalized="基金经理持有本基金份额区间为100万份以上。",
    )

    result = _manager_profile_source_truth_result(
        _ContentIntermediateStub(
            source_provenance=_provenance(),
            source_truth_admission=_source_truth_admission_proof(),
            sections=(),
            paragraph_blocks=(first, second),
            table_blocks=(),
        )
    )

    family = _field_family(result, "manager_profile.v1")

    assert family.value["manager_alignment"]["manager_holding"] == "基金经理持有本基金份额区间为100万份以上。"
    assert len(family.anchors) == 1
    assert family.anchors[0].row_locator == (
        "field=manager_alignment.manager_holding; block_id=paragraph-holding-first"
    )
    assert "ambiguous_table_or_locator" not in _gap_codes(family)


def test_manager_profile_source_truth_conflicting_holdings_row_is_ambiguous() -> None:
    """同一持仓行 identity 出现冲突值时省略该行并追加 ambiguity gap。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当冲突持仓行进入 public value 时抛出。
    """

    table = _TableStub(
        table_id="table-conflicting-holdings",
        section_id="section-holdings",
        heading_text="前十名股票投资明细",
        table_caption_or_nearby_heading="前十名股票投资明细",
        heading_path=("投资组合", "前十名股票投资明细"),
        cells=(
            _manager_profile_holdings_cell("股票代码", "600000", row_index=0, column_index=0, table_id="table-conflicting-holdings"),
            _manager_profile_holdings_cell("股票名称", "浦发银行", row_index=0, column_index=1, table_id="table-conflicting-holdings"),
            _manager_profile_holdings_cell("公允价值", "1,000.00", row_index=0, column_index=2, table_id="table-conflicting-holdings"),
            _manager_profile_holdings_cell("股票代码", "600000", row_index=1, column_index=0, table_id="table-conflicting-holdings"),
            _manager_profile_holdings_cell("股票名称", "浦发银行", row_index=1, column_index=1, table_id="table-conflicting-holdings"),
            _manager_profile_holdings_cell("公允价值", "2,000.00", row_index=1, column_index=2, table_id="table-conflicting-holdings"),
        ),
    )

    result = _manager_profile_source_truth_result(
        _ContentIntermediateStub(
            source_provenance=_provenance(),
            source_truth_admission=_source_truth_admission_proof(),
            sections=(),
            paragraph_blocks=(),
            table_blocks=(table,),
        )
    )

    family = _field_family(result, "manager_profile.v1")

    assert "holdings_snapshot" not in family.value
    assert family.anchors == ()
    assert "ambiguous_table_or_locator" in _gap_codes(family)
    assert any(
        gap.source_field_path == "holdings_snapshot.top_holdings"
        for gap in family.gaps
        if gap.gap_code == "ambiguous_table_or_locator"
    )


def test_manager_profile_source_truth_accepted_when_all_allowed_groups_present() -> None:
    """五个 manager_profile top-level subvalues 全部存在时 accepted 且无缺口。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当五项完整仍 partial、缺 gap 或跨族泄漏时抛出。
    """

    roster_table = _TableStub(
        table_id="table-roster",
        section_id="section-manager",
        heading_text="基金经理情况",
        table_caption_or_nearby_heading="基金经理情况",
        heading_path=("基金经理情况",),
        cells=(
            _manager_profile_cell("姓名", "张三", row_index=0, column_index=0),
            _manager_profile_cell("职务", "基金经理", row_index=0, column_index=1),
            _manager_profile_cell("任职日期", "2020-01-01", row_index=0, column_index=2),
        ),
    )
    turnover_table = _TableStub(
        table_id="table-turnover",
        section_id="section-turnover",
        heading_text="报告期内股票换手率",
        table_caption_or_nearby_heading="报告期内股票换手率",
        heading_path=("交易情况",),
        cells=(
            _manager_profile_cell(
                "报告期内股票换手率",
                "123.45%",
                row_index=0,
                table_id="table-turnover",
                label_axis="row",
            ),
        ),
    )
    top_table = _TableStub(
        table_id="table-top-holdings",
        section_id="section-holdings",
        heading_text="前十名股票投资明细",
        table_caption_or_nearby_heading="前十名股票投资明细",
        heading_path=("投资组合", "前十名股票投资明细"),
        cells=(
            _manager_profile_holdings_cell("股票代码", "600000", row_index=0, column_index=0, table_id="table-top-holdings"),
            _manager_profile_holdings_cell("股票名称", "浦发银行", row_index=0, column_index=1, table_id="table-top-holdings"),
            _manager_profile_holdings_cell("公允价值", "1,234.56", row_index=0, column_index=2, table_id="table-top-holdings"),
        ),
    )
    strategy = _ParagraphStub(
        block_id="paragraph-strategy",
        section_id="section-strategy",
        heading_path=("报告期内基金投资策略和运作分析",),
        text_raw="本报告期坚持均衡配置。",
        text_normalized="本报告期坚持均衡配置。",
    )
    alignment = _ParagraphStub(
        block_id="paragraph-alignment",
        section_id="section-alignment",
        heading_path=("基金经理持有本基金情况",),
        text_raw="基金经理持有本基金份额区间为100万份以上。",
        text_normalized="基金经理持有本基金份额区间为100万份以上。",
    )

    result = _manager_profile_source_truth_result(
        _ContentIntermediateStub(
            source_provenance=_provenance(),
            source_truth_admission=_source_truth_admission_proof(),
            sections=(),
            paragraph_blocks=(strategy, alignment),
            table_blocks=(roster_table, turnover_table, top_table),
        )
    )

    family = _field_family(result, "manager_profile.v1")

    assert result.contract_status == "partial"
    assert family.status == "accepted"
    assert family.extraction_mode == "direct"
    assert family.gaps == ()
    assert family.candidate_evidence == ()
    assert set(family.value) == {
        "schema_version",
        "portfolio_managers",
        "manager_strategy_text",
        "turnover_rate",
        "manager_alignment",
        "holdings_snapshot",
    }
    assert family.value["schema_version"] == "manager_profile.v1"
    current_stage = _field_family(result, "current_stage.v1")
    assert current_stage.status == "partial"
    assert set(current_stage.value) == {
        "schema_version",
        "holdings_snapshot",
        "portfolio_managers",
    }
    assert current_stage.candidate_evidence == ()
    assert _field_family(result, "core_risk.v1").value == {}


def test_manager_profile_source_truth_full_value_with_internal_ambiguity_is_partial() -> None:
    """五个 top-level 都存在但内部有歧义时不得返回 accepted。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当带 ambiguity gap 的完整 top-level 被误标 accepted 时抛出。
    """

    roster_table = _TableStub(
        table_id="table-roster",
        section_id="section-manager",
        heading_text="基金经理情况",
        table_caption_or_nearby_heading="基金经理情况",
        heading_path=("基金经理情况",),
        cells=(
            _manager_profile_cell("姓名", "张三", row_index=0, column_index=0),
            _manager_profile_cell("职务", "基金经理", row_index=0, column_index=1),
            _manager_profile_cell("任职日期", "2020-01-01", row_index=0, column_index=2),
        ),
    )
    turnover_table = _TableStub(
        table_id="table-turnover",
        section_id="section-turnover",
        heading_text="报告期内股票换手率",
        table_caption_or_nearby_heading="报告期内股票换手率",
        heading_path=("交易情况",),
        cells=(
            _manager_profile_cell(
                "报告期内股票换手率",
                "123.45%",
                row_index=0,
                table_id="table-turnover",
                label_axis="row",
            ),
        ),
    )
    holdings_table = _TableStub(
        table_id="table-ambiguous-plus-valid-holdings",
        section_id="section-holdings",
        heading_text="前十名股票投资明细",
        table_caption_or_nearby_heading="前十名股票投资明细",
        heading_path=("投资组合", "前十名股票投资明细"),
        cells=(
            _manager_profile_holdings_cell("股票代码", "600000", row_index=0, column_index=0, table_id="table-ambiguous-plus-valid-holdings"),
            _manager_profile_holdings_cell("股票名称", "浦发银行", row_index=0, column_index=1, table_id="table-ambiguous-plus-valid-holdings"),
            _manager_profile_holdings_cell("公允价值", "1,000.00", row_index=0, column_index=2, table_id="table-ambiguous-plus-valid-holdings"),
            _manager_profile_holdings_cell("股票代码", "600000", row_index=1, column_index=0, table_id="table-ambiguous-plus-valid-holdings"),
            _manager_profile_holdings_cell("股票名称", "浦发银行", row_index=1, column_index=1, table_id="table-ambiguous-plus-valid-holdings"),
            _manager_profile_holdings_cell("公允价值", "2,000.00", row_index=1, column_index=2, table_id="table-ambiguous-plus-valid-holdings"),
            _manager_profile_holdings_cell("股票代码", "000001", row_index=2, column_index=0, table_id="table-ambiguous-plus-valid-holdings"),
            _manager_profile_holdings_cell("股票名称", "平安银行", row_index=2, column_index=1, table_id="table-ambiguous-plus-valid-holdings"),
            _manager_profile_holdings_cell("公允价值", "3,000.00", row_index=2, column_index=2, table_id="table-ambiguous-plus-valid-holdings"),
        ),
    )
    strategy = _ParagraphStub(
        block_id="paragraph-strategy",
        section_id="section-strategy",
        heading_path=("报告期内基金投资策略和运作分析",),
        text_raw="本报告期坚持均衡配置。",
        text_normalized="本报告期坚持均衡配置。",
    )
    alignment = _ParagraphStub(
        block_id="paragraph-alignment",
        section_id="section-alignment",
        heading_path=("基金经理持有本基金情况",),
        text_raw="基金经理持有本基金份额区间为100万份以上。",
        text_normalized="基金经理持有本基金份额区间为100万份以上。",
    )

    result = _manager_profile_source_truth_result(
        _ContentIntermediateStub(
            source_provenance=_provenance(),
            source_truth_admission=_source_truth_admission_proof(),
            sections=(),
            paragraph_blocks=(strategy, alignment),
            table_blocks=(roster_table, turnover_table, holdings_table),
        )
    )

    family = _field_family(result, "manager_profile.v1")

    assert set(family.value) == {
        "schema_version",
        "portfolio_managers",
        "manager_strategy_text",
        "turnover_rate",
        "manager_alignment",
        "holdings_snapshot",
    }
    assert family.status == "partial"
    assert family.extraction_mode == "direct"
    assert family.candidate_evidence == ()
    assert "ambiguous_table_or_locator" in _gap_codes(family)
    assert any(
        gap.source_field_path == "holdings_snapshot.top_holdings"
        for gap in family.gaps
        if gap.gap_code == "ambiguous_table_or_locator"
    )


def test_manager_profile_source_truth_extracts_table_backed_alignment() -> None:
    """table-backed alignment 路径可按 label/value split 抽取持有披露。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 table/cell guard 或 label/value 分离失效时抛出。
    """

    table = _TableStub(
        table_id="table-alignment",
        section_id="section-alignment",
        heading_text="基金管理人持有情况",
        table_caption_or_nearby_heading="基金管理人持有情况",
        heading_path=("基金管理人持有情况",),
        cells=(
            _CellStub(
                cell_id="cell-manager-label",
                table_id="table-alignment",
                row_index=0,
                column_index=0,
                row_label_path=("基金经理持有本基金",),
                column_header_path=("项目",),
                cell_text="基金经理持有本基金",
                cell_text_normalized="基金经理持有本基金",
            ),
            _CellStub(
                cell_id="cell-manager-value",
                table_id="table-alignment",
                row_index=0,
                column_index=1,
                row_label_path=("基金经理持有本基金",),
                column_header_path=("内容",),
                cell_text="100万份以上",
                cell_text_normalized="100万份以上",
            ),
            _CellStub(
                cell_id="cell-employee-label",
                table_id="table-alignment",
                row_index=1,
                column_index=0,
                row_label_path=("基金管理人所有从业人员持有本基金",),
                column_header_path=("项目",),
                cell_text="基金管理人所有从业人员持有本基金",
                cell_text_normalized="基金管理人所有从业人员持有本基金",
            ),
            _CellStub(
                cell_id="cell-employee-value",
                table_id="table-alignment",
                row_index=1,
                column_index=1,
                row_label_path=("基金管理人所有从业人员持有本基金",),
                column_header_path=("内容",),
                cell_text="50万份至100万份",
                cell_text_normalized="50万份至100万份",
            ),
        ),
    )

    result = _manager_profile_source_truth_result(
        _ContentIntermediateStub(
            source_provenance=_provenance(),
            source_truth_admission=_source_truth_admission_proof(),
            sections=(),
            paragraph_blocks=(),
            table_blocks=(table,),
        )
    )

    family = _field_family(result, "manager_profile.v1")

    assert family.value["manager_alignment"] == {
        "manager_holding": "100万份以上",
        "employee_holding": "50万份至100万份",
        "judgment": None,
    }
    assert family.anchors[0].table_id == "table-alignment"
    assert family.anchors[0].row_locator.startswith("field=manager_alignment.manager_holding")
    assert family.candidate_evidence == ()


def test_manager_profile_cell_original_index_raises_for_foreign_cell() -> None:
    """target cell 不属于 table.cells 时不得静默返回 cells[0]。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 helper 未抛出 ValueError 时由 pytest 抛出。
    """

    table_cell = _CellStub(cell_id="cell-owned", table_id="table-owned")
    foreign_cell = _CellStub(cell_id="cell-foreign", table_id="table-owned")
    table = _TableStub(table_id="table-owned", cells=(table_cell,))

    with pytest.raises(ValueError, match="target_cell not found"):
        _manager_profile_cell_original_index(table, foreign_cell)


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


def test_investor_experience_source_truth_route_suppresses_candidate_evidence() -> None:
    """proof-positive direct route 缺 public value 时也清空 investor candidate evidence。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 direct-route missing 仍泄漏 candidate evidence 时抛出。
    """

    result = _investor_experience_source_truth_result(
        _source_truth_content_intermediate(
            sections=(
                _SectionStub(
                    section_id="section-distribution",
                    heading_text_raw="基金收益分配",
                    heading_text_normalized="基金收益分配",
                    heading_path=("基金收益分配",),
                ),
            ),
        )
    )

    family = _field_family(result, "investor_experience.v1")

    assert family.status == "missing"
    assert family.value == {}
    assert family.anchors == ()
    assert family.candidate_evidence == ()
    assert _gap_codes(family) == {"field_family_missing"}


def test_investor_experience_source_truth_requires_proof_even_when_candidate_boundary_none() -> None:
    """proof 缺失时保持 candidate-only missing 并追加 source_truth_admission_missing。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 proof-missing 路径被提升为 public direct 时抛出。
    """

    processor = FundDisclosureDocumentProcessor()
    result = processor.extract(
        FundProcessorInput(
            context=_dispatch_key(),
            intermediate=_ContentIntermediateStub(
                source_provenance=_provenance(),
                sections=(
                    _SectionStub(
                        section_id="section-investor",
                        heading_text_raw="投资者实际收益",
                        heading_text_normalized="投资者实际收益",
                        heading_path=("投资者实际收益",),
                    ),
                ),
                paragraph_blocks=(),
                table_blocks=(),
            ),
        )
    )

    family = _field_family(result, "investor_experience.v1")

    assert family.status == "missing"
    assert family.value == {}
    assert family.anchors == ()
    assert family.candidate_evidence
    assert _gap_codes(family) == {
        "candidate_only_not_source_truth",
        "source_truth_admission_missing",
    }


def test_investor_experience_source_truth_rejects_base_admission_invalid_paths() -> None:
    """缺 provenance 或 failure_class 非空时不得产出 investor public value。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 invalid base admission 被直接抽取时抛出。
    """

    for intermediate in (
        _ContentIntermediateStub(
            source_provenance=None,
            source_truth_admission=_source_truth_admission_proof(),
            paragraph_blocks=(
                _investor_paragraph("投资者收益率：6.66%", block_id="paragraph-return"),
            ),
            table_blocks=(),
        ),
        _ContentIntermediateStub(
            source_provenance=_provenance(),
            failure_class="schema_drift",
            source_truth_admission=_source_truth_admission_proof(),
            paragraph_blocks=(
                _investor_paragraph("投资者收益率：6.66%", block_id="paragraph-return"),
            ),
            table_blocks=(),
        ),
    ):
        result = _investor_experience_source_truth_result(intermediate)
        if result.field_families:
            family = _field_family(result, "investor_experience.v1")
            assert family.value == {}
            assert family.anchors == ()
            assert family.extraction_mode == "missing"
        else:
            assert result.contract_status == "blocked"
            assert result.anchors == ()


def test_investor_experience_source_truth_candidate_boundary_remains_blocked() -> None:
    """candidate_boundary 输入不得进入 investor source-truth direct extraction。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 candidate boundary 被提升为 public source truth 时抛出。
    """

    result = _investor_experience_source_truth_result(
        _ContentIntermediateStub(
            source_provenance=_provenance(),
            candidate_boundary=CandidateBoundaryStatus(
                candidate_only=True,
                field_correctness_status="not_proven",
                source_truth_status="not_proven",
            ),
            source_truth_admission=_source_truth_admission_proof(),
            paragraph_blocks=(
                _investor_paragraph("投资者收益率：6.66%", block_id="paragraph-return"),
            ),
            table_blocks=(),
        )
    )

    family = _field_family(result, "investor_experience.v1")

    assert result.contract_status == "blocked"
    assert family.value == {}
    assert family.anchors == ()


def test_investor_experience_source_truth_extracts_exact_value_shape() -> None:
    """proof-positive investor_experience 只发出三个既有 public/bundle key。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 public shape 扩张或字段缺失时抛出。
    """

    cells = (
        _investor_cell("期初基金份额总额", "1,000.00", row_index=0, column_header_path=("004393",)),
        _investor_cell("期末基金份额总额", "1,250.00", row_index=1, column_header_path=("004393",)),
        _investor_cell("净变动", "250.00", row_index=2, column_header_path=("004393",)),
    )
    result = _investor_experience_source_truth_result(
        _source_truth_content_intermediate(
            cells=cells,
            paragraphs=(
                _investor_paragraph("投资者收益率：7.25%", block_id="paragraph-return"),
                _investor_paragraph("机构投资者持有比例：60.00%", block_id="paragraph-inst"),
                _investor_paragraph("个人投资者持有比例：40.00%", block_id="paragraph-ind"),
            ),
        )
    )

    family = _field_family(result, "investor_experience.v1")

    assert family.status == "accepted"
    assert family.extraction_mode == "direct"
    assert set(family.value) == {
        "schema_version",
        "investor_return",
        "holder_structure",
        "share_change",
    }
    assert family.value["investor_return"] == {
        "investor_return_rate": "7.25%",
        "disclosure_status": "direct",
        "fallback_status": "not_needed",
    }
    assert family.value["holder_structure"] == {
        "institutional_holder": "60.00%",
        "individual_holder": "40.00%",
    }
    assert family.value["share_change"] == {
        "beginning_share": "1,000.00",
        "ending_share": "1,250.00",
        "net_change": "250.00",
        "share_class_column": "004393",
        "share_class_selection_reason": "single_value_column",
    }
    assert family.candidate_evidence == ()
    assert family.anchors
    assert {anchor.source_kind for anchor in family.anchors} == {"annual_report"}


def test_investor_experience_source_truth_estimated_investor_return_only() -> None:
    """仅估算投资者收益率时发出 estimated public shape。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 estimated disclosure status 错误时抛出。
    """

    result = _investor_experience_source_truth_result(
        _source_truth_content_intermediate(
            paragraphs=(
                _investor_paragraph(
                    "估算投资者收益率：5.50%",
                    block_id="paragraph-estimated-return",
                ),
            ),
        )
    )

    family = _field_family(result, "investor_experience.v1")

    assert family.status == "partial"
    assert family.value["investor_return"] == {
        "investor_return_rate": "5.50%",
        "disclosure_status": "estimated",
        "fallback_status": "estimated_disclosure_in_section",
    }


def test_investor_experience_source_truth_estimated_investor_return_conflict_omits_value() -> None:
    """估算投资者收益率冲突时 omit investor_return 并记录 ambiguity。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 estimated 冲突仍进入 public value 时抛出。
    """

    result = _investor_experience_source_truth_result(
        _source_truth_content_intermediate(
            paragraphs=(
                _investor_paragraph("估算投资者收益率：5.50%", block_id="paragraph-est-1"),
                _investor_paragraph("估算投资者收益率：6.50%", block_id="paragraph-est-2"),
            ),
        )
    )

    family = _field_family(result, "investor_experience.v1")

    assert family.value == {}
    assert any(
        gap.gap_code == "ambiguous_table_or_locator"
        and gap.source_field_path == "investor_return"
        for gap in family.gaps
    )


def test_investor_experience_source_truth_investor_return_paragraph_requires_label_value_pattern() -> None:
    """投资者收益率 paragraph 必须同段有 label 和有效百分比且非 unavailable。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 label-only 或 unavailable 文本被采信时抛出。
    """

    result = _investor_experience_source_truth_result(
        _source_truth_content_intermediate(
            paragraphs=(
                _investor_paragraph("投资者收益率", block_id="paragraph-label-only"),
                _investor_paragraph("投资者收益率：未披露 8.00%", block_id="paragraph-unavailable"),
                _investor_paragraph("本段仅出现 8.00% 但无标签", block_id="paragraph-value-only"),
            ),
        )
    )

    family = _field_family(result, "investor_experience.v1")

    assert family.value == {}
    assert _gap_codes(family) == {"field_family_missing"}


def test_investor_experience_source_truth_holder_structure_filters_placeholder_values() -> None:
    """holder_structure placeholder side 不得作为 public value。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 placeholder 被写入 holder_structure 时抛出。
    """

    result = _investor_experience_source_truth_result(
        _source_truth_content_intermediate(
            paragraphs=(
                _investor_paragraph("机构投资者持有比例：未披露", block_id="paragraph-inst"),
                _investor_paragraph("个人投资者持有比例：40.00%", block_id="paragraph-ind"),
            ),
        )
    )

    family = _field_family(result, "investor_experience.v1")

    assert family.value["holder_structure"] == {
        "institutional_holder": None,
        "individual_holder": "40.00%",
    }


def test_investor_experience_source_truth_partial_when_required_groups_missing() -> None:
    """只命中部分 top-level 时返回 partial 并记录 field_family_partial。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 partial 完整度状态错误时抛出。
    """

    result = _investor_experience_source_truth_result(
        _source_truth_content_intermediate(
            paragraphs=(
                _investor_paragraph("投资者收益率：7.25%", block_id="paragraph-return"),
            ),
        )
    )

    family = _field_family(result, "investor_experience.v1")

    assert family.status == "partial"
    assert set(family.value) == {"schema_version", "investor_return"}
    assert "field_family_partial" in _gap_codes(family)


def test_investor_experience_source_truth_missing_when_no_allowed_public_labels() -> None:
    """仅申购赎回或收益分配 locator 内容不得产生 public subvalue。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 candidate-only role 被写入 public value 时抛出。
    """

    result = _investor_experience_source_truth_result(
        _source_truth_content_intermediate(
            sections=(
                _SectionStub(
                    section_id="section-subscription",
                    heading_text_raw="申购赎回",
                    heading_text_normalized="申购赎回",
                    heading_path=("基金份额变动", "申购赎回"),
                ),
                _SectionStub(
                    section_id="section-distribution",
                    heading_text_raw="收益分配",
                    heading_text_normalized="收益分配",
                    heading_path=("收益分配",),
                ),
            ),
        )
    )

    family = _field_family(result, "investor_experience.v1")

    assert family.value == {}
    assert family.candidate_evidence == ()
    assert _gap_codes(family) == {"field_family_missing"}


def test_investor_experience_source_truth_ambiguous_duplicate_omits_conflicting_value() -> None:
    """同一 output path 多个冲突值时 omit 对应 public subvalue。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当冲突值被任意采信时抛出。
    """

    result = _investor_experience_source_truth_result(
        _source_truth_content_intermediate(
            paragraphs=(
                _investor_paragraph("投资者收益率：7.25%", block_id="paragraph-return-1"),
                _investor_paragraph("投资者收益率：8.25%", block_id="paragraph-return-2"),
                _investor_paragraph("机构投资者持有比例：60.00%", block_id="paragraph-inst"),
            ),
        )
    )

    family = _field_family(result, "investor_experience.v1")

    assert "investor_return" not in family.value
    assert "holder_structure" in family.value
    assert family.status == "partial"
    assert any(gap.source_field_path == "investor_return" for gap in family.gaps)


def test_investor_experience_source_truth_share_change_excludes_label_column() -> None:
    """share_change table 排除 label column 后只取数值列。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 label column 被误选为 value column 时抛出。
    """

    cells = (
        _investor_cell("项目", "期初基金份额总额", row_index=0, column_index=0),
        _investor_cell("项目", "期末基金份额总额", row_index=1, column_index=0),
        _investor_cell("期初基金份额总额", "1,000.00", row_index=0, column_index=1),
        _investor_cell("期末基金份额总额", "1,250.00", row_index=1, column_index=1),
    )
    result = _investor_experience_source_truth_result(
        _source_truth_content_intermediate(cells=cells)
    )

    family = _field_family(result, "investor_experience.v1")

    assert family.value["share_change"]["beginning_share"] == "1,000.00"
    assert family.value["share_change"]["ending_share"] == "1,250.00"
    assert family.value["share_change"]["share_class_selection_reason"] == "single_value_column"


def test_investor_experience_source_truth_share_change_selects_single_value_column() -> None:
    """share_change 只有一个 value column 时不要求 fund code header。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 single-value-column 路径未被独立选择时抛出。
    """

    cells = (
        _investor_cell("项目", "期初基金份额总额", row_index=0, column_index=0),
        _investor_cell("项目", "期末基金份额总额", row_index=1, column_index=0),
        _investor_cell(
            "期初基金份额总额",
            "1,000.00",
            row_index=0,
            column_index=1,
            column_header_path=("报告期份额",),
        ),
        _investor_cell(
            "期末基金份额总额",
            "1,250.00",
            row_index=1,
            column_index=1,
            column_header_path=("报告期份额",),
        ),
    )
    result = _investor_experience_source_truth_result(
        _source_truth_content_intermediate(cells=cells)
    )

    share_change = _field_family(result, "investor_experience.v1").value["share_change"]

    assert share_change == {
        "beginning_share": "1,000.00",
        "ending_share": "1,250.00",
        "net_change": "250.00",
        "share_class_column": "报告期份额",
        "share_class_selection_reason": "single_value_column",
    }


def test_investor_experience_source_truth_share_change_selects_exact_fund_code_column() -> None:
    """多 value column 时只允许 exact fund_code header match。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 substring/fuzzy fund code 被误选时抛出。
    """

    cells = (
        _investor_cell(
            "期初基金份额总额",
            "1,000.00",
            row_index=0,
            column_index=1,
            column_header_path=("004393",),
        ),
        _investor_cell(
            "期末基金份额总额",
            "1,250.00",
            row_index=1,
            column_index=1,
            column_header_path=("004393",),
        ),
        _investor_cell(
            "期初基金份额总额",
            "9,000.00",
            row_index=0,
            column_index=2,
            column_header_path=("004393A",),
        ),
        _investor_cell(
            "期末基金份额总额",
            "9,250.00",
            row_index=1,
            column_index=2,
            column_header_path=("004393A",),
        ),
    )
    result = _investor_experience_source_truth_result(
        _source_truth_content_intermediate(cells=cells)
    )

    share_change = _field_family(result, "investor_experience.v1").value["share_change"]

    assert share_change["beginning_share"] == "1,000.00"
    assert share_change["ending_share"] == "1,250.00"
    assert share_change["share_class_column"] == "004393"
    assert share_change["share_class_selection_reason"] == "fund_code_header_match"


def test_investor_experience_source_truth_share_change_rejects_ambiguous_share_class_columns() -> None:
    """多 value column 无 exact fund_code 时 omit share_change。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 share class ambiguity 被静默选择时抛出。
    """

    cells = (
        _investor_cell(
            "期初基金份额总额",
            "1,000.00",
            row_index=0,
            column_index=1,
            column_header_path=("A类",),
        ),
        _investor_cell(
            "期末基金份额总额",
            "1,250.00",
            row_index=1,
            column_index=1,
            column_header_path=("A类",),
        ),
        _investor_cell(
            "期初基金份额总额",
            "2,000.00",
            row_index=0,
            column_index=2,
            column_header_path=("C类",),
        ),
        _investor_cell(
            "期末基金份额总额",
            "2,250.00",
            row_index=1,
            column_index=2,
            column_header_path=("C类",),
        ),
    )
    result = _investor_experience_source_truth_result(
        _source_truth_content_intermediate(cells=cells)
    )

    family = _field_family(result, "investor_experience.v1")

    assert family.value == {}
    assert _gap_codes(family) == {"ambiguous_table_or_locator", "field_family_missing"}
    assert any(
        gap.gap_code == "ambiguous_table_or_locator" and gap.source_field_path == "share_change"
        for gap in family.gaps
    )


def test_investor_experience_source_truth_share_change_calculates_net_change() -> None:
    """缺净变动行时用 Decimal 计算 ending - beginning。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当净变动计算格式偏离既有语义时抛出。
    """

    cells = (
        _investor_cell("期初基金份额总额", "1,000.00", row_index=0, column_header_path=("004393",)),
        _investor_cell("期末基金份额总额", "1,234.50", row_index=1, column_header_path=("004393",)),
    )
    result = _investor_experience_source_truth_result(
        _source_truth_content_intermediate(cells=cells)
    )

    share_change = _field_family(result, "investor_experience.v1").value["share_change"]

    assert share_change["net_change"] == "234.50"


def test_investor_experience_source_truth_does_not_populate_stage_or_risk() -> None:
    """investor direct route 不得把候选 evidence 提升为 stage/risk public value。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当相邻 family 被 direct route 干扰时抛出。
    """

    result = _investor_experience_source_truth_result(
        _source_truth_content_intermediate(
            paragraphs=(
                _investor_paragraph("投资者收益率：7.25%", block_id="paragraph-return"),
                _ParagraphStub(
                    block_id="paragraph-stage",
                    section_id="section-stage",
                    heading_path=("投资策略和运作分析",),
                    text_raw="本报告期组合仓位保持稳定，配置结构有所调整。",
                    text_normalized="本报告期组合仓位保持稳定，配置结构有所调整。",
                ),
                _ParagraphStub(
                    block_id="paragraph-risk",
                    section_id="section-risk",
                    heading_path=("风险收益特征",),
                    text_raw="本基金属于较高风险较高收益的基金品种。",
                    text_normalized="本基金属于较高风险较高收益的基金品种。",
                ),
            ),
        )
    )

    investor = _field_family(result, "investor_experience.v1")
    current_stage = _field_family(result, "current_stage.v1")
    core_risk = _field_family(result, "core_risk.v1")

    assert investor.candidate_evidence == ()
    assert investor.value["investor_return"]["investor_return_rate"] == "7.25%"
    assert current_stage.value == {}
    assert core_risk.value == {}
    assert current_stage.candidate_evidence == ()
    assert core_risk.candidate_evidence


# ── current_stage source-truth values ──────────────────────────────────────


def test_current_stage_source_truth_extracts_allowed_fact_inputs_only() -> None:
    """proof-positive current_stage 只发出四个既有 public key。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 current_stage 扩张 schema、缺少 anchor 或混入 candidate 时抛出。
    """

    product_table = _TableStub(
        table_id="table-product",
        section_id="section-product",
        heading_text="基金基本情况",
        table_caption_or_nearby_heading="基金基本情况",
        heading_path=("基金简介",),
        cells=(
            _product_cell("基金名称", "测试主动基金", row_index=0, cell_id="product-name"),
            _product_cell("基金主代码", "004393", row_index=1, cell_id="product-code"),
        ),
    )
    share_table = _TableStub(
        table_id="table-share",
        section_id="section-share",
        heading_text="基金份额变动",
        table_caption_or_nearby_heading="基金份额变动",
        heading_path=("基金份额变动",),
        cells=(
            _investor_cell(
                "期初基金份额总额",
                "1,000.00",
                row_index=0,
                table_id="table-share",
                column_header_path=("004393",),
            ),
            _investor_cell(
                "期末基金份额总额",
                "1,250.00",
                row_index=1,
                table_id="table-share",
                column_header_path=("004393",),
            ),
            _investor_cell(
                "净变动",
                "250.00",
                row_index=2,
                table_id="table-share",
                column_header_path=("004393",),
            ),
        ),
    )
    roster_table = _TableStub(
        table_id="table-roster",
        section_id="section-manager",
        heading_text="基金经理情况",
        table_caption_or_nearby_heading="基金经理情况",
        heading_path=("基金管理人及基金经理情况",),
        cells=(
            _manager_profile_cell("姓名", "张三", row_index=0, column_index=0),
            _manager_profile_cell("职务", "基金经理", row_index=0, column_index=1),
            _manager_profile_cell("任职日期", "2020-01-01", row_index=0, column_index=2),
        ),
    )
    holdings_table = _TableStub(
        table_id="table-top-holdings",
        section_id="section-holdings",
        heading_text="前十名股票投资明细",
        table_caption_or_nearby_heading="前十名股票投资明细",
        heading_path=("投资组合", "前十名股票投资明细"),
        cells=(
            _manager_profile_holdings_cell(
                "股票代码", "600000", row_index=0, column_index=0, table_id="table-top-holdings"
            ),
            _manager_profile_holdings_cell(
                "股票名称", "浦发银行", row_index=0, column_index=1, table_id="table-top-holdings"
            ),
            _manager_profile_holdings_cell(
                "公允价值",
                "1,234,567.89",
                row_index=0,
                column_index=2,
                table_id="table-top-holdings",
            ),
        ),
    )

    result = _current_stage_source_truth_result(
        _ContentIntermediateStub(
            source_provenance=_provenance(),
            source_truth_admission=_source_truth_admission_proof(),
            sections=(),
            paragraph_blocks=(),
            table_blocks=(product_table, share_table, roster_table, holdings_table),
        )
    )

    family = _field_family(result, "current_stage.v1")
    value = family.value

    assert family.status == "accepted"
    assert family.extraction_mode == "direct"
    assert family.candidate_evidence == ()
    assert set(value) == {
        "schema_version",
        "basic_identity",
        "share_change",
        "holdings_snapshot",
        "portfolio_managers",
    }
    assert value["schema_version"] == "current_stage.v1"
    assert value["basic_identity"]["fund_name"] == "测试主动基金"
    assert value["basic_identity"]["fund_code"] == "004393"
    assert value["share_change"] == {
        "beginning_share": "1,000.00",
        "ending_share": "1,250.00",
        "net_change": "250.00",
        "share_class_column": "004393",
        "share_class_selection_reason": "single_value_column",
    }
    assert value["holdings_snapshot"]["top_holdings"] == [
        {"股票代码": "600000", "股票名称": "浦发银行", "公允价值": "1,234,567.89"}
    ]
    assert value["portfolio_managers"]["portfolio_managers"][0]["name"] == "张三"
    assert family.anchors
    assert {anchor.source_kind for anchor in family.anchors} == {"annual_report"}
    forbidden_keys = {
        "current_stage_summary",
        "stage_status",
        "manager_change",
        "share_scale_change",
        "holding_strategy_change",
        "stage_judgment",
        "market_timing",
        "valuation_state",
    }
    assert forbidden_keys.isdisjoint(value)


def test_current_stage_source_truth_direct_missing_suppresses_candidate_evidence() -> None:
    """proof-positive current_stage direct missing 不回退 candidate evidence。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 direct missing 混入 candidate evidence 时抛出。
    """

    result = _current_stage_source_truth_result(
        _ContentIntermediateStub(
            source_provenance=_provenance(),
            source_truth_admission=_source_truth_admission_proof(),
            sections=(
                _SectionStub(
                    section_id="section-stage",
                    heading_text_raw="当前阶段",
                    heading_text_normalized="当前阶段",
                    heading_path=("当前阶段",),
                ),
            ),
            paragraph_blocks=(),
            table_blocks=(),
        )
    )

    family = _field_family(result, "current_stage.v1")

    assert family.status == "missing"
    assert family.extraction_mode == "missing"
    assert family.value == {}
    assert family.anchors == ()
    assert family.candidate_evidence == ()
    assert _gap_codes(family) == {"field_family_missing"}


def test_current_stage_source_truth_requires_positive_proof() -> None:
    """缺 source-truth proof 时 current_stage public 结果保持 missing。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当缺 proof 仍输出 current_stage public value 时抛出。
    """

    result = _current_stage_source_truth_result(
        _ContentIntermediateStub(
            source_provenance=_provenance(),
            source_truth_admission=None,
            sections=(
                _SectionStub(
                    section_id="section-stage",
                    heading_text_raw="当前阶段",
                    heading_text_normalized="当前阶段",
                    heading_path=("当前阶段",),
                ),
            ),
            paragraph_blocks=(),
            table_blocks=(),
        )
    )

    family = _field_family(result, "current_stage.v1")

    assert family.status == "missing"
    assert family.value == {}
    assert family.anchors == ()
    assert family.candidate_evidence
    assert "source_truth_admission_missing" in _gap_codes(family)


def test_current_stage_source_truth_rejects_invalid_proof() -> None:
    """proof 身份不一致时 current_stage 不进入 direct source truth。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 invalid proof 被接受时抛出。
    """

    result = _current_stage_source_truth_result(
        _ContentIntermediateStub(
            source_provenance=_provenance(),
            source_truth_admission=_source_truth_admission_proof(fund_code="110011"),
            sections=(
                _SectionStub(
                    section_id="section-stage",
                    heading_text_raw="基金运作情况",
                    heading_text_normalized="基金运作情况",
                    heading_path=("基金运作情况",),
                ),
            ),
            paragraph_blocks=(),
            table_blocks=(),
        )
    )

    family = _field_family(result, "current_stage.v1")

    assert family.status == "missing"
    assert family.value == {}
    assert family.anchors == ()
    assert "source_truth_admission_invalid" in _gap_codes(family)


def test_current_stage_source_truth_candidate_boundary_remains_blocked() -> None:
    """candidate boundary 不因 current_stage source-truth proof 存在被绕过。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 candidate boundary 被 direct route 绕过时抛出。
    """

    boundary = CandidateBoundaryStatus(
        candidate_only=True,
        field_correctness_status="not_proven",
        source_truth_status="not_proven",
    )
    result = _current_stage_source_truth_result(
        _ContentIntermediateStub(
            source_provenance=_provenance(),
            candidate_boundary=boundary,
            source_truth_admission=_source_truth_admission_proof(),
            sections=(
                _SectionStub(
                    section_id="section-stage",
                    heading_text_raw="当前阶段",
                    heading_text_normalized="当前阶段",
                    heading_path=("当前阶段",),
                ),
            ),
            paragraph_blocks=(),
            table_blocks=(),
        )
    )

    family = _field_family(result, "current_stage.v1")

    assert result.contract_status == "blocked"
    assert result.candidate_boundary is boundary
    assert family.status == "missing"
    assert family.value == {}
    assert family.anchors == ()
    assert family.candidate_evidence
    assert _gap_codes(family) == {"candidate_only_not_source_truth"}


def test_current_stage_source_truth_does_not_implement_core_risk() -> None:
    """current_stage direct extraction 不改变 core_risk candidate-only 边界。

    Args:
        无。

    Returns:
        无返回值。

    Raises:
        AssertionError: 当 core_risk 被 source-truth 提升时抛出。
    """

    result = _current_stage_source_truth_result(
        _ContentIntermediateStub(
            source_provenance=_provenance(),
            source_truth_admission=_source_truth_admission_proof(),
            sections=(
                _SectionStub(
                    section_id="section-risk",
                    heading_text_raw="风险收益特征",
                    heading_text_normalized="风险收益特征",
                    heading_path=("风险收益特征",),
                ),
            ),
            table_blocks=(
                _TableStub(
                    table_id="table-product",
                    heading_text="基金基本情况",
                    table_caption_or_nearby_heading="基金基本情况",
                    heading_path=("基金简介",),
                    cells=(
                        _product_cell("基金名称", "测试主动基金", row_index=0),
                        _product_cell("基金主代码", "004393", row_index=1),
                    ),
                ),
            ),
        )
    )

    current_stage = _field_family(result, "current_stage.v1")
    core_risk = _field_family(result, "core_risk.v1")

    assert current_stage.status == "partial"
    assert set(current_stage.value) == {"schema_version", "basic_identity"}
    assert current_stage.candidate_evidence == ()
    assert core_risk.status == "missing"
    assert core_risk.value == {}
    assert core_risk.anchors == ()
    assert core_risk.candidate_evidence


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
