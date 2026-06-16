"""Docling source-truth residual 的 candidate-only 闭合 helper。

本模块只处理 Fund documents candidate internals，见模板第 1 章产品身份、
第 2 章 R=A+B-C 成本/组合事实、第 3 章基金经理画像和第 8 章证据审计
所需的字段证明前置校验。它不读取文件、不调用 Docling、不访问
``FundDocumentRepository``、不调用 source helper，也不构造生产
``EvidenceAnchor``。
"""

from __future__ import annotations

import re
from collections import Counter
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Literal

from fund_agent.fund.documents.candidates.normalization import normalize_text
from fund_agent.fund.documents.candidates.representation_models import (
    CandidateRepresentationDocument,
)

ClosureDisposition = Literal[
    "disambiguated_source_body_match",
    "semantic_equivalent_duplicate_residual",
    "source_body_mismatch",
    "semantic_assignment_residual",
    "blocked_locator_unavailable",
    "blocked_reference_unavailable",
    "blocked_rule_missing",
    "blocked_candidate_metadata_violation",
]
SourceLayerStatus = Literal[
    "same_source_reference_loaded",
    "same_source_text_absent",
    "blocked_reference_unavailable",
    "metadata_violation",
]
ProcessedLayerStatus = Literal[
    "locator_context_available",
    "locator_context_insufficient",
    "locator_context_conflict",
    "candidate_metadata_violation",
]
FundLayerStatus = Literal[
    "semantic_rule_satisfied",
    "semantic_rule_unresolved",
    "semantic_rule_rejected",
    "semantic_rule_missing",
]
ReferenceOrigin = Literal[
    "fund_document_repository_parsed_table",
    "fund_document_repository_section_text",
]
ReferenceGenerationStatus = Literal["available", "blocked_reference_unavailable"]

_SCHEMA_VERSION = "docling_source_truth_residual_closure.v1"
_ANNUAL_REPORT_EVIDENCE_SOURCE_KIND = "annual_report"


@dataclass(frozen=True, slots=True)
class ResidualClosureRule:
    """字段级 residual 闭合规则。

    Attributes:
        field_name: 字段名。
        expected_section_id: 期望年报章节。
        required_row_label_any: 任一必须出现的行标签。
        rejected_row_label_any: 任一出现即拒绝的行标签。
        required_table_family_any: 任一必须出现的表格上下文标签。
        required_column_header_any: 任一必须出现的列表头标签。
        share_class_context: 份额类别上下文。
        allow_semantic_equivalent_duplicate: 是否允许同语义重复保持 residual。
        semantic_guard: 额外语义 guard 标签。
    """

    field_name: str
    expected_section_id: str
    required_row_label_any: tuple[str, ...] = ()
    rejected_row_label_any: tuple[str, ...] = ()
    required_table_family_any: tuple[str, ...] = ()
    required_column_header_any: tuple[str, ...] = ()
    share_class_context: str | None = None
    allow_semantic_equivalent_duplicate: bool = False
    semantic_guard: str | None = None


@dataclass(frozen=True, slots=True)
class RepositoryReferenceCell:
    """由仓库解析结果派生的表格单元格引用。

    Attributes:
        fund_code: 基金代码。
        document_year: 年报年份。
        repository_source_name: 仓库来源名，例如 ``eid``。
        source_mode: 来源策略模式。
        fallback_used: 是否使用 fallback。
        section_id: 年报章节。
        page_number: 页码。
        table_id: 表格 ID。
        row_index: 行号。
        column_index: 列号。
        row_label_path: 行标签路径。
        column_header_path: 列表头路径。
        raw_text: 原始单元格文本。
        normalized_text: 归一化单元格文本。
        table_context: 表格上下文。
        reference_origin: 引用来源。
    """

    fund_code: str
    document_year: int
    repository_source_name: str
    source_mode: str
    fallback_used: bool
    section_id: str
    page_number: int
    table_id: str
    row_index: int
    column_index: int
    row_label_path: tuple[str, ...]
    column_header_path: tuple[str, ...]
    raw_text: str
    normalized_text: str
    table_context: tuple[str, ...]
    reference_origin: ReferenceOrigin = "fund_document_repository_parsed_table"

    def to_dict(self) -> dict[str, object]:
        """序列化为 JSON 兼容字典。

        Args:
            无。

        Returns:
            JSON 兼容字典。

        Raises:
            无显式抛出。
        """

        return {
            "fund_code": self.fund_code,
            "document_year": self.document_year,
            "repository_source_name": self.repository_source_name,
            "source_mode": self.source_mode,
            "fallback_used": self.fallback_used,
            "section_id": self.section_id,
            "page_number": self.page_number,
            "table_id": self.table_id,
            "row_index": self.row_index,
            "column_index": self.column_index,
            "row_label_path": list(self.row_label_path),
            "column_header_path": list(self.column_header_path),
            "raw_text": self.raw_text,
            "normalized_text": self.normalized_text,
            "table_context": list(self.table_context),
            "reference_origin": self.reference_origin,
        }


@dataclass(frozen=True, slots=True)
class RepositoryReferenceTextSpan:
    """由仓库解析结果派生的章节文本引用。

    Attributes:
        fund_code: 基金代码。
        document_year: 年报年份。
        repository_source_name: 仓库来源名。
        source_mode: 来源策略模式。
        fallback_used: 是否使用 fallback。
        section_id: 年报章节。
        page_number: 页码。
        raw_text: 原始文本。
        normalized_text: 归一化文本。
        context_label: 文本上下文标签。
        reference_origin: 引用来源。
    """

    fund_code: str
    document_year: int
    repository_source_name: str
    source_mode: str
    fallback_used: bool
    section_id: str
    page_number: int
    raw_text: str
    normalized_text: str
    context_label: str
    reference_origin: ReferenceOrigin = "fund_document_repository_section_text"

    def to_dict(self) -> dict[str, object]:
        """序列化为 JSON 兼容字典。

        Args:
            无。

        Returns:
            JSON 兼容字典。

        Raises:
            无显式抛出。
        """

        return {
            "fund_code": self.fund_code,
            "document_year": self.document_year,
            "repository_source_name": self.repository_source_name,
            "source_mode": self.source_mode,
            "fallback_used": self.fallback_used,
            "section_id": self.section_id,
            "page_number": self.page_number,
            "raw_text": self.raw_text,
            "normalized_text": self.normalized_text,
            "context_label": self.context_label,
            "reference_origin": self.reference_origin,
        }


@dataclass(frozen=True, slots=True)
class RepositoryReferenceBundle:
    """单样本仓库引用集合。

    Attributes:
        sample_id: 样本 ID。
        fund_code: 基金代码。
        document_year: 年报年份。
        metadata_ok: 仓库来源 metadata 是否通过。
        metadata_reason: metadata 失败原因。
        cells: 表格单元格引用。
        text_spans: 章节文本引用。
        reference_generation_status: 引用生成状态。
    """

    sample_id: str
    fund_code: str
    document_year: int
    metadata_ok: bool
    metadata_reason: str | None
    cells: tuple[RepositoryReferenceCell, ...] = ()
    text_spans: tuple[RepositoryReferenceTextSpan, ...] = ()
    reference_generation_status: ReferenceGenerationStatus = "available"

    def to_dict(self) -> dict[str, object]:
        """序列化为 JSON 兼容字典。

        Args:
            无。

        Returns:
            JSON 兼容字典。

        Raises:
            无显式抛出。
        """

        return {
            "sample_id": self.sample_id,
            "fund_code": self.fund_code,
            "document_year": self.document_year,
            "metadata_ok": self.metadata_ok,
            "metadata_reason": self.metadata_reason,
            "cells": [cell.to_dict() for cell in self.cells],
            "text_spans": [span.to_dict() for span in self.text_spans],
            "reference_generation_status": self.reference_generation_status,
        }


@dataclass(frozen=True, slots=True)
class ResidualClosureInputRow:
    """待闭合 residual 输入行。"""

    sample_id: str
    fact_id: str
    fund_code: str
    document_year: int
    field_name: str
    candidate_anchor: Mapping[str, object]
    normalized_candidate: str
    current_disposition: str
    residual_reason: str | None


@dataclass(frozen=True, slots=True)
class ResidualClosureResultRow:
    """单行 residual 闭合结果。"""

    sample_id: str
    fact_id: str
    fund_code: str
    document_year: int
    field_name: str
    current_disposition: str
    closure_disposition: ClosureDisposition
    closure_reason: str
    source_layer_status: SourceLayerStatus
    processed_layer_status: ProcessedLayerStatus
    fund_layer_status: FundLayerStatus
    matched_row_label_path: tuple[str, ...] = ()
    matched_column_header_path: tuple[str, ...] = ()
    matched_table_context: tuple[str, ...] = ()
    matched_repository_source_name: str | None = None
    matched_source_mode: str | None = None
    matched_reference_origin: ReferenceOrigin | None = None
    candidate_processor_source_kind: str | None = None
    candidate_only: bool = True
    source_truth_status: Literal["not_proven"] = "not_proven"
    evidence_anchor_source_kind: Literal["annual_report"] = _ANNUAL_REPORT_EVIDENCE_SOURCE_KIND

    def to_dict(self) -> dict[str, object]:
        """序列化为 JSON 兼容字典。

        Args:
            无。

        Returns:
            JSON 兼容字典。

        Raises:
            无显式抛出。
        """

        return {
            "sample_id": self.sample_id,
            "fact_id": self.fact_id,
            "fund_code": self.fund_code,
            "document_year": self.document_year,
            "field_name": self.field_name,
            "current_disposition": self.current_disposition,
            "closure_disposition": self.closure_disposition,
            "closure_reason": self.closure_reason,
            "source_layer_status": self.source_layer_status,
            "processed_layer_status": self.processed_layer_status,
            "fund_layer_status": self.fund_layer_status,
            "matched_row_label_path": list(self.matched_row_label_path),
            "matched_column_header_path": list(self.matched_column_header_path),
            "matched_table_context": list(self.matched_table_context),
            "matched_repository_source_name": self.matched_repository_source_name,
            "matched_source_mode": self.matched_source_mode,
            "matched_reference_origin": self.matched_reference_origin,
            "candidate_processor_source_kind": self.candidate_processor_source_kind,
            "candidate_only": self.candidate_only,
            "source_truth_status": self.source_truth_status,
            "evidence_anchor_source_kind": self.evidence_anchor_source_kind,
        }


@dataclass(frozen=True, slots=True)
class SourceTruthResidualClosureMatrix:
    """source-truth residual 闭合矩阵。"""

    rows: tuple[ResidualClosureResultRow, ...]
    input_artifacts: tuple[dict[str, object], ...] = ()
    schema_version: str = _SCHEMA_VERSION
    not_baseline_promotion: bool = True
    not_parser_replacement: bool = True
    not_release_readiness: bool = True
    not_full_field_correctness: bool = True
    not_raw_pdf_bbox_truth: bool = True
    candidate_only: bool = True

    def to_dict(self) -> dict[str, object]:
        """序列化为 JSON 兼容字典。

        Args:
            无。

        Returns:
            JSON 兼容字典。

        Raises:
            无显式抛出。
        """

        dispositions = Counter(row.closure_disposition for row in self.rows)
        by_sample: dict[str, Counter[str]] = {}
        for row in self.rows:
            by_sample.setdefault(row.sample_id, Counter())[row.closure_disposition] += 1
        return {
            "schema_version": self.schema_version,
            "input_artifacts": list(self.input_artifacts),
            "summary": {
                "rows_total": len(self.rows),
                "dispositions": dict(sorted(dispositions.items())),
                "closed_count": dispositions.get("disambiguated_source_body_match", 0),
                "residual_or_blocked_count": len(self.rows)
                - dispositions.get("disambiguated_source_body_match", 0),
            },
            "by_sample": {
                sample_id: dict(sorted(counter.items()))
                for sample_id, counter in sorted(by_sample.items())
            },
            "rows": [row.to_dict() for row in self.rows],
            "not_baseline_promotion": self.not_baseline_promotion,
            "not_parser_replacement": self.not_parser_replacement,
            "not_release_readiness": self.not_release_readiness,
            "not_full_field_correctness": self.not_full_field_correctness,
            "not_raw_pdf_bbox_truth": self.not_raw_pdf_bbox_truth,
            "candidate_only": self.candidate_only,
        }


@dataclass(frozen=True, slots=True)
class _ReferenceMatch:
    """内部引用命中结果。"""

    cell: RepositoryReferenceCell | None = None
    text_span: RepositoryReferenceTextSpan | None = None


@dataclass(frozen=True, slots=True)
class _SemanticEvaluation:
    """内部语义规则评估结果。"""

    status: FundLayerStatus
    matched: tuple[_ReferenceMatch, ...]
    reason: str


FIELD_RULES: dict[str, ResidualClosureRule] = {
    "fund_name": ResidualClosureRule(
        field_name="fund_name",
        expected_section_id="§2",
        required_row_label_any=("基金名称",),
        rejected_row_label_any=("基金简称", "基金主代码", "基金管理人"),
    ),
    "fund_code": ResidualClosureRule(
        field_name="fund_code",
        expected_section_id="§2",
        required_row_label_any=("基金主代码",),
        rejected_row_label_any=("交易代码", "下属分级基金的交易代码"),
    ),
    "manager": ResidualClosureRule(
        field_name="manager",
        expected_section_id="§2",
        required_row_label_any=("基金管理人", "基金管理人名称"),
    ),
    "custodian": ResidualClosureRule(
        field_name="custodian",
        expected_section_id="§2",
        required_row_label_any=("基金托管人", "基金托管人名称"),
    ),
    "fixed_income_investment_amount": ResidualClosureRule(
        field_name="fixed_income_investment_amount",
        expected_section_id="§8",
        required_row_label_any=("固定收益投资",),
        rejected_row_label_any=("第二层次", "合计"),
        required_table_family_any=("投资组合", "资产组合", "基金资产组合"),
    ),
    "equity_investment_amount": ResidualClosureRule(
        field_name="equity_investment_amount",
        expected_section_id="§8",
        required_row_label_any=("权益投资",),
        rejected_row_label_any=("其中：股票", "其中:股票", "普通股", "美国"),
        required_table_family_any=("投资组合", "资产组合", "基金资产组合"),
    ),
    "stock_investment_amount": ResidualClosureRule(
        field_name="stock_investment_amount",
        expected_section_id="§8",
        required_row_label_any=("其中：股票", "其中:股票", "股票"),
        rejected_row_label_any=("权益投资",),
        required_table_family_any=("投资组合", "资产组合", "基金资产组合"),
    ),
    "manager_holding_range_A": ResidualClosureRule(
        field_name="manager_holding_range_A",
        expected_section_id="§10",
        required_row_label_any=("本基金基金经理持有本开放式基金", "基金经理持有"),
        rejected_row_label_any=("合计",),
        required_table_family_any=("基金经理持有", "管理人持有"),
        share_class_context="A",
    ),
    "sales_service_fee_C_current_year": ResidualClosureRule(
        field_name="sales_service_fee_C_current_year",
        expected_section_id="§7",
        required_row_label_any=("销售服务费",),
        required_table_family_any=("销售服务费",),
        required_column_header_any=("本期", "本报告期", "当前"),
        share_class_context="C",
        allow_semantic_equivalent_duplicate=True,
    ),
    "investment_objective": ResidualClosureRule(
        field_name="investment_objective",
        expected_section_id="§2",
        required_row_label_any=("投资目标",),
        semantic_guard="投资目标",
    ),
    "benchmark": ResidualClosureRule(
        field_name="benchmark",
        expected_section_id="§2",
        required_row_label_any=("业绩比较基准",),
        rejected_row_label_any=("投资目标",),
        semantic_guard="业绩比较基准",
    ),
}


def close_source_truth_residuals(
    *,
    source_truth_matrix: Mapping[str, object],
    candidate_documents: Mapping[str, CandidateRepresentationDocument] | None = None,
    repository_reference_rows: Mapping[str, object],
) -> SourceTruthResidualClosureMatrix:
    """按 source / processed / fund 合同分类 source-truth residual。

    Args:
        source_truth_matrix: 上游 source-truth matrix。
        candidate_documents: 已投影的候选文档；保留给后续 document-level
            candidate guard，当前 helper 行为仍只做 candidate metadata guard。
        repository_reference_rows: 已构造的仓库引用 bundle 映射。

    Returns:
        residual 闭合矩阵。

    Raises:
        ValueError: 输入 matrix 行结构非法时抛出。
    """

    # 保留 accepted plan API；当前 no-live slice 不读取候选文档正文。
    _ = candidate_documents
    bundles = _coerce_reference_bundles(repository_reference_rows)
    input_artifacts = tuple(
        dict(item)
        for item in _sequence(source_truth_matrix.get("input_artifacts"))
        if isinstance(item, Mapping)
    )
    result_rows = tuple(
        _close_row(_coerce_input_row(row), bundles)
        for row in _residual_rows(source_truth_matrix)
    )
    return SourceTruthResidualClosureMatrix(
        rows=result_rows,
        input_artifacts=input_artifacts,
    )


def _close_row(
    row: ResidualClosureInputRow,
    bundles: Mapping[str, RepositoryReferenceBundle],
) -> ResidualClosureResultRow:
    """闭合单个 residual 行。

    Args:
        row: residual 输入行。
        bundles: 仓库引用 bundle 映射。

    Returns:
        单行闭合结果。

    Raises:
        无显式抛出。
    """

    rule = FIELD_RULES.get(row.field_name)
    processed_status = _processed_status(row, rule)
    if processed_status == "candidate_metadata_violation":
        return _result(
            row,
            "blocked_candidate_metadata_violation",
            "candidate anchor does not preserve candidate-only annual-report boundary",
            "blocked_reference_unavailable",
            processed_status,
            "semantic_rule_unresolved",
        )
    if rule is None:
        return _result(
            row,
            "blocked_rule_missing",
            "no fund-layer residual closure rule for field",
            "blocked_reference_unavailable",
            processed_status,
            "semantic_rule_missing",
        )
    bundle = _bundle_for_row(row, bundles)
    if bundle is None or bundle.reference_generation_status != "available":
        return _result(
            row,
            "blocked_reference_unavailable",
            "no repository-mediated no-live reference bundle is available",
            "blocked_reference_unavailable",
            processed_status,
            "semantic_rule_unresolved",
        )
    if not bundle.metadata_ok:
        return _result(
            row,
            "blocked_reference_unavailable",
            bundle.metadata_reason or "repository metadata is unsafe",
            "metadata_violation",
            processed_status,
            "semantic_rule_unresolved",
        )
    source_matches = _source_matches(row, bundle)
    if not source_matches:
        return _result(
            row,
            "source_body_mismatch",
            "same-source repository reference contains no normalized candidate text",
            "same_source_text_absent",
            processed_status,
            "semantic_rule_unresolved",
        )
    if processed_status != "locator_context_available":
        return _result(
            row,
            "blocked_locator_unavailable",
            "candidate locator context is insufficient or conflicts with the fund rule",
            "same_source_reference_loaded",
            processed_status,
            "semantic_rule_unresolved",
        )
    semantic = _evaluate_semantics(rule, source_matches)
    if semantic.status != "semantic_rule_satisfied":
        return _result(
            row,
            "semantic_assignment_residual",
            semantic.reason,
            "same_source_reference_loaded",
            processed_status,
            semantic.status,
        )
    if rule.allow_semantic_equivalent_duplicate and len(semantic.matched) > 1:
        first_match = semantic.matched[0]
        return _result(
            row,
            "semantic_equivalent_duplicate_residual",
            "multiple semantically equivalent source rows remain unresolved",
            "same_source_reference_loaded",
            processed_status,
            "semantic_rule_unresolved",
            first_match,
        )
    return _result(
        row,
        "disambiguated_source_body_match",
        "source, processed locator and fund semantic rule agree",
        "same_source_reference_loaded",
        processed_status,
        "semantic_rule_satisfied",
        semantic.matched[0],
    )


def _processed_status(
    row: ResidualClosureInputRow,
    rule: ResidualClosureRule | None,
) -> ProcessedLayerStatus:
    """判断 candidate processed locator 状态。

    Args:
        row: residual 输入行。
        rule: 字段规则。

    Returns:
        processed 层状态。

    Raises:
        无显式抛出。
    """

    anchor = row.candidate_anchor
    if anchor.get("candidate_only") is not True:
        return "candidate_metadata_violation"
    if anchor.get("field_correctness_status") not in (None, "not_proven"):
        return "candidate_metadata_violation"
    if anchor.get("source_truth_status") not in (None, "not_proven"):
        return "candidate_metadata_violation"
    if anchor.get("evidence_anchor_source_kind") not in (None, _ANNUAL_REPORT_EVIDENCE_SOURCE_KIND):
        return "candidate_metadata_violation"
    if anchor.get("source_kind") not in (None, _ANNUAL_REPORT_EVIDENCE_SOURCE_KIND):
        return "candidate_metadata_violation"
    if str(anchor.get("section_id", "")) == "":
        return "locator_context_insufficient"
    if rule is not None and anchor.get("section_id") != rule.expected_section_id:
        return "locator_context_conflict"
    if _requires_table_locator(row.field_name) and (
        not anchor.get("table_id") or not anchor.get("row_locator")
    ):
        return "locator_context_insufficient"
    return "locator_context_available"


def _evaluate_semantics(
    rule: ResidualClosureRule,
    source_matches: tuple[_ReferenceMatch, ...],
) -> _SemanticEvaluation:
    """执行 fund 层语义规则。

    Args:
        rule: 字段规则。
        source_matches: 同源文本命中。

    Returns:
        语义评估结果。

    Raises:
        无显式抛出。
    """

    accepted: list[_ReferenceMatch] = []
    rejected = False
    for match in source_matches:
        if _match_satisfies_rule(match, rule):
            accepted.append(match)
        else:
            rejected = True
    if accepted:
        return _SemanticEvaluation(
            status="semantic_rule_satisfied",
            matched=tuple(accepted),
            reason="fund semantic rule satisfied",
        )
    return _SemanticEvaluation(
        status="semantic_rule_rejected" if rejected else "semantic_rule_unresolved",
        matched=(),
        reason="same-source value is present but fund semantic context is not proven",
    )


def _match_satisfies_rule(match: _ReferenceMatch, rule: ResidualClosureRule) -> bool:
    """判断引用命中是否满足字段规则。

    Args:
        match: 引用命中。
        rule: 字段规则。

    Returns:
        满足时返回 ``True``。

    Raises:
        无显式抛出。
    """

    row_labels = _row_labels(match)
    column_headers = _column_headers(match)
    table_context = _table_context(match)
    section_id = _section_id(match)
    if section_id != rule.expected_section_id:
        return False
    if rule.rejected_row_label_any and _contains_any(row_labels, rule.rejected_row_label_any):
        return False
    if rule.required_row_label_any and not _contains_any(row_labels, rule.required_row_label_any):
        return False
    if rule.required_column_header_any and not _contains_any(
        column_headers,
        rule.required_column_header_any,
    ):
        return False
    if rule.share_class_context and not _has_share_class_context(
        column_headers,
        rule.share_class_context,
    ):
        return False
    if rule.required_table_family_any and not _contains_any(
        table_context,
        rule.required_table_family_any,
    ):
        return False
    if rule.semantic_guard and not _contains_any(
        row_labels + table_context,
        (rule.semantic_guard,),
    ):
        return False
    return True


def _source_matches(
    row: ResidualClosureInputRow,
    bundle: RepositoryReferenceBundle,
) -> tuple[_ReferenceMatch, ...]:
    """查找同源引用文本命中。

    Args:
        row: residual 输入行。
        bundle: 仓库引用 bundle。

    Returns:
        命中结果。

    Raises:
        无显式抛出。
    """

    candidate = _normalize_for_match(row.normalized_candidate)
    matches: list[_ReferenceMatch] = []
    for cell in bundle.cells:
        if _reference_matches(candidate, cell.normalized_text, cell.raw_text):
            matches.append(_ReferenceMatch(cell=cell))
    for span in bundle.text_spans:
        if _reference_matches(candidate, span.normalized_text, span.raw_text):
            matches.append(_ReferenceMatch(text_span=span))
    return tuple(matches)


def _reference_matches(candidate: str, normalized_text: str, raw_text: str) -> bool:
    """判断 reference 是否包含候选值。

    Args:
        candidate: 已归一化候选值。
        normalized_text: reference 归一化文本。
        raw_text: reference 原始文本。

    Returns:
        命中时返回 ``True``。

    Raises:
        无显式抛出。
    """

    if not candidate:
        return False
    return candidate in _normalize_for_match(normalized_text) or candidate in _normalize_for_match(raw_text)


def _coerce_input_row(payload: Mapping[str, object]) -> ResidualClosureInputRow:
    """转换 residual matrix 行。

    Args:
        payload: JSON-like 行。

    Returns:
        residual 输入行。

    Raises:
        ValueError: 字段非法时抛出。
    """

    anchor = payload.get("candidate_anchor")
    if not isinstance(anchor, Mapping):
        raise ValueError("residual row requires candidate_anchor mapping")
    return ResidualClosureInputRow(
        sample_id=str(payload["sample_id"]),
        fact_id=str(payload["fact_id"]),
        fund_code=str(payload["fund_code"]),
        document_year=int(payload["document_year"]),
        field_name=str(payload["field_name"]),
        candidate_anchor=anchor,
        normalized_candidate=str(
            payload.get("normalized_candidate") or payload.get("candidate_value") or ""
        ),
        current_disposition=str(payload["row_disposition"]),
        residual_reason=(
            str(payload["residual_reason"])
            if payload.get("residual_reason") is not None
            else None
        ),
    )


def _coerce_reference_bundles(
    payload: Mapping[str, object],
) -> dict[str, RepositoryReferenceBundle]:
    """转换引用 bundle 映射。

    Args:
        payload: bundle 映射。

    Returns:
        以 sample id 和 fund/year 双 key 索引的 bundle。

    Raises:
        ValueError: bundle 字段非法时抛出。
    """

    bundles: dict[str, RepositoryReferenceBundle] = {}
    for key, value in payload.items():
        bundle = value if isinstance(value, RepositoryReferenceBundle) else _coerce_bundle(value)
        bundles[str(key)] = bundle
        bundles[bundle.sample_id] = bundle
        bundles[f"{bundle.fund_code}:{bundle.document_year}"] = bundle
    return bundles


def _coerce_bundle(value: object) -> RepositoryReferenceBundle:
    """转换单个引用 bundle。

    Args:
        value: JSON-like bundle。

    Returns:
        引用 bundle。

    Raises:
        ValueError: bundle 非 mapping 时抛出。
    """

    if not isinstance(value, Mapping):
        raise ValueError("repository reference bundle must be a mapping")
    return RepositoryReferenceBundle(
        sample_id=str(value["sample_id"]),
        fund_code=str(value["fund_code"]),
        document_year=int(value["document_year"]),
        metadata_ok=bool(value.get("metadata_ok", False)),
        metadata_reason=(
            str(value["metadata_reason"]) if value.get("metadata_reason") is not None else None
        ),
        cells=tuple(_coerce_cell(item) for item in _sequence(value.get("cells"))),
        text_spans=tuple(
            _coerce_text_span(item) for item in _sequence(value.get("text_spans"))
        ),
        reference_generation_status=str(  # type: ignore[arg-type]
            value.get("reference_generation_status", "available")
        ),
    )


def _coerce_cell(value: object) -> RepositoryReferenceCell:
    """转换单元格引用。

    Args:
        value: JSON-like cell。

    Returns:
        单元格引用。

    Raises:
        ValueError: cell 非 mapping 时抛出。
    """

    if isinstance(value, RepositoryReferenceCell):
        return value
    if not isinstance(value, Mapping):
        raise ValueError("repository reference cell must be a mapping")
    return RepositoryReferenceCell(
        fund_code=str(value["fund_code"]),
        document_year=int(value["document_year"]),
        repository_source_name=str(value["repository_source_name"]),
        source_mode=str(value["source_mode"]),
        fallback_used=bool(value.get("fallback_used", False)),
        section_id=str(value["section_id"]),
        page_number=int(value["page_number"]),
        table_id=str(value["table_id"]),
        row_index=int(value["row_index"]),
        column_index=int(value["column_index"]),
        row_label_path=_string_tuple(value.get("row_label_path")),
        column_header_path=_string_tuple(value.get("column_header_path")),
        raw_text=str(value.get("raw_text", "")),
        normalized_text=str(value.get("normalized_text", value.get("raw_text", ""))),
        table_context=_string_tuple(value.get("table_context")),
        reference_origin=str(  # type: ignore[arg-type]
            value.get("reference_origin", "fund_document_repository_parsed_table")
        ),
    )


def _coerce_text_span(value: object) -> RepositoryReferenceTextSpan:
    """转换文本引用。

    Args:
        value: JSON-like text span。

    Returns:
        文本引用。

    Raises:
        ValueError: text span 非 mapping 时抛出。
    """

    if isinstance(value, RepositoryReferenceTextSpan):
        return value
    if not isinstance(value, Mapping):
        raise ValueError("repository reference text span must be a mapping")
    return RepositoryReferenceTextSpan(
        fund_code=str(value["fund_code"]),
        document_year=int(value["document_year"]),
        repository_source_name=str(value["repository_source_name"]),
        source_mode=str(value["source_mode"]),
        fallback_used=bool(value.get("fallback_used", False)),
        section_id=str(value["section_id"]),
        page_number=int(value["page_number"]),
        raw_text=str(value.get("raw_text", "")),
        normalized_text=str(value.get("normalized_text", value.get("raw_text", ""))),
        context_label=str(value.get("context_label", "")),
        reference_origin=str(  # type: ignore[arg-type]
            value.get("reference_origin", "fund_document_repository_section_text")
        ),
    )


def _residual_rows(source_truth_matrix: Mapping[str, object]) -> tuple[Mapping[str, object], ...]:
    """提取 residual rows。

    Args:
        source_truth_matrix: 上游 source-truth matrix。

    Returns:
        residual row tuple。

    Raises:
        ValueError: rows 字段非法时抛出。
    """

    rows = _sequence(source_truth_matrix.get("rows"))
    residuals: list[Mapping[str, object]] = []
    for row in rows:
        if not isinstance(row, Mapping):
            raise ValueError("source_truth_matrix rows must be mappings")
        if row.get("row_disposition") != "source_body_match":
            residuals.append(row)
    return tuple(residuals)


def _result(
    row: ResidualClosureInputRow,
    disposition: ClosureDisposition,
    reason: str,
    source_status: SourceLayerStatus,
    processed_status: ProcessedLayerStatus,
    fund_status: FundLayerStatus,
    match: _ReferenceMatch | None = None,
) -> ResidualClosureResultRow:
    """构造单行输出。

    Args:
        row: 输入行。
        disposition: 闭合 disposition。
        reason: 原因。
        source_status: source 层状态。
        processed_status: processed 层状态。
        fund_status: fund 层状态。
        match: 可选命中引用。

    Returns:
        输出行。

    Raises:
        无显式抛出。
    """

    return ResidualClosureResultRow(
        sample_id=row.sample_id,
        fact_id=row.fact_id,
        fund_code=row.fund_code,
        document_year=row.document_year,
        field_name=row.field_name,
        current_disposition=row.current_disposition,
        closure_disposition=disposition,
        closure_reason=reason,
        source_layer_status=source_status,
        processed_layer_status=processed_status,
        fund_layer_status=fund_status,
        matched_row_label_path=_row_labels(match) if match is not None else (),
        matched_column_header_path=_column_headers(match) if match is not None else (),
        matched_table_context=_table_context(match) if match is not None else (),
        matched_repository_source_name=(
            _repository_source_name(match) if match is not None else None
        ),
        matched_source_mode=_source_mode(match) if match is not None else None,
        matched_reference_origin=_reference_origin(match) if match is not None else None,
        candidate_processor_source_kind=_candidate_processor_source_kind(row),
    )


def _bundle_for_row(
    row: ResidualClosureInputRow,
    bundles: Mapping[str, RepositoryReferenceBundle],
) -> RepositoryReferenceBundle | None:
    """查找输入行对应 bundle。

    Args:
        row: 输入行。
        bundles: bundle 映射。

    Returns:
        命中 bundle；不存在时返回 ``None``。

    Raises:
        无显式抛出。
    """

    return bundles.get(row.sample_id) or bundles.get(f"{row.fund_code}:{row.document_year}")


def _requires_table_locator(field_name: str) -> bool:
    """判断字段是否要求 table/cell locator。

    Args:
        field_name: 字段名。

    Returns:
        需要时返回 ``True``。

    Raises:
        无显式抛出。
    """

    return field_name not in {"investment_objective", "benchmark"}


def _candidate_processor_source_kind(row: ResidualClosureInputRow) -> str | None:
    """返回 candidate processor route 身份。

    Args:
        row: 输入行。

    Returns:
        candidate processor route；缺失时返回 ``None``。

    Raises:
        无显式抛出。
    """

    value = row.candidate_anchor.get("candidate_source_kind") or row.candidate_anchor.get(
        "processor_source_kind"
    )
    return str(value) if value is not None else None


def _repository_source_name(match: _ReferenceMatch) -> str | None:
    """返回仓库来源名。

    Args:
        match: 命中引用。

    Returns:
        仓库来源名。

    Raises:
        无显式抛出。
    """

    if match.cell is not None:
        return match.cell.repository_source_name
    if match.text_span is not None:
        return match.text_span.repository_source_name
    return None


def _source_mode(match: _ReferenceMatch) -> str | None:
    """返回仓库来源模式。

    Args:
        match: 命中引用。

    Returns:
        来源模式。

    Raises:
        无显式抛出。
    """

    if match.cell is not None:
        return match.cell.source_mode
    if match.text_span is not None:
        return match.text_span.source_mode
    return None


def _reference_origin(match: _ReferenceMatch) -> ReferenceOrigin | None:
    """返回仓库引用来源。

    Args:
        match: 命中引用。

    Returns:
        引用来源。

    Raises:
        无显式抛出。
    """

    if match.cell is not None:
        return match.cell.reference_origin
    if match.text_span is not None:
        return match.text_span.reference_origin
    return None


def _row_labels(match: _ReferenceMatch | None) -> tuple[str, ...]:
    """返回命中引用的行标签。

    Args:
        match: 命中引用。

    Returns:
        行标签 tuple。

    Raises:
        无显式抛出。
    """

    if match is None:
        return ()
    if match.cell is not None:
        return match.cell.row_label_path
    if match.text_span is not None:
        return (match.text_span.context_label,)
    return ()


def _column_headers(match: _ReferenceMatch | None) -> tuple[str, ...]:
    """返回命中引用的列表头。

    Args:
        match: 命中引用。

    Returns:
        列表头 tuple。

    Raises:
        无显式抛出。
    """

    if match is None or match.cell is None:
        return ()
    return match.cell.column_header_path


def _table_context(match: _ReferenceMatch | None) -> tuple[str, ...]:
    """返回命中引用的表格上下文。

    Args:
        match: 命中引用。

    Returns:
        表格上下文 tuple。

    Raises:
        无显式抛出。
    """

    if match is None:
        return ()
    if match.cell is not None:
        return match.cell.table_context
    if match.text_span is not None:
        return (match.text_span.context_label,)
    return ()


def _section_id(match: _ReferenceMatch) -> str:
    """返回命中引用的章节 ID。

    Args:
        match: 命中引用。

    Returns:
        章节 ID。

    Raises:
        无显式抛出。
    """

    if match.cell is not None:
        return match.cell.section_id
    if match.text_span is not None:
        return match.text_span.section_id
    return ""


def _contains_any(values: tuple[str, ...], needles: tuple[str, ...]) -> bool:
    """判断 values 是否包含任一 needle。

    Args:
        values: 候选文本。
        needles: 目标片段。

    Returns:
        包含时返回 ``True``。

    Raises:
        无显式抛出。
    """

    haystack = _normalize_for_label(" ".join(values))
    return any(_normalize_for_label(needle) in haystack for needle in needles)


def _has_share_class_context(values: tuple[str, ...], share_class: str) -> bool:
    """判断列表头是否含有指定份额类别上下文。

    Args:
        values: 列表头路径。
        share_class: 份额类别，例如 ``A`` 或 ``C``。

    Returns:
        存在明确份额类别时返回 ``True``。

    Raises:
        无显式抛出。
    """

    normalized_share = _normalize_for_label(share_class)
    accepted_exact = {
        normalized_share,
        f"{normalized_share}类",
        f"{normalized_share}份额",
    }
    for value in values:
        normalized_value = _normalize_for_label(value)
        if normalized_value in accepted_exact:
            return True
        if _ends_with_fund_share_class_label(normalized_value, normalized_share):
            return True
        if f"{normalized_share}类" in normalized_value:
            return True
    return False


def _ends_with_fund_share_class_label(value: str, share_class: str) -> bool:
    """判断文本是否以基金份额类别标签收尾。

    Args:
        value: 已归一化文本。
        share_class: 已归一化份额类别，例如 ``a`` 或 ``c``。

    Returns:
        以中文基金份额标签收尾时返回 ``True``。

    Raises:
        无显式抛出。
    """

    if value == share_class:
        return True
    if not value.endswith(share_class) or len(value) <= len(share_class):
        return False
    prefix = value[: -len(share_class)]
    previous = prefix[-1]
    return "\u4e00" <= previous <= "\u9fff"


def _normalize_for_match(text: str) -> str:
    """归一化 source-truth 文本匹配。

    Args:
        text: 原始文本。

    Returns:
        归一化文本。

    Raises:
        无显式抛出。
    """

    normalized = normalize_text(text).normalized_text.lower()
    chars: list[str] = []
    for index, char in enumerate(normalized):
        previous_char = normalized[index - 1] if index > 0 else ""
        next_char = normalized[index + 1] if index + 1 < len(normalized) else ""
        if char in ".．。":
            if previous_char.isdigit() and next_char.isdigit():
                chars.append(".")
            continue
        if re.match(r"[\s,，()（）]", char):
            continue
        chars.append(char)
    return "".join(chars)


def _normalize_for_label(text: str) -> str:
    """归一化语义标签匹配。

    Args:
        text: 原始标签。

    Returns:
        归一化标签。

    Raises:
        无显式抛出。
    """

    normalized = normalize_text(text).normalized_text.lower()
    return re.sub(r"\s+", "", normalized)


def _string_tuple(value: object) -> tuple[str, ...]:
    """把 JSON-like 值转为字符串 tuple。

    Args:
        value: 原始值。

    Returns:
        字符串 tuple。

    Raises:
        无显式抛出。
    """

    return tuple(str(item) for item in _sequence(value))


def _sequence(value: object) -> tuple[object, ...]:
    """把 JSON-like sequence 转为 tuple。

    Args:
        value: 原始值。

    Returns:
        tuple。

    Raises:
        无显式抛出。
    """

    if value is None:
        return ()
    if isinstance(value, tuple):
        return value
    if isinstance(value, list):
        return tuple(value)
    return ()
