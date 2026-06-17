"""Docling source-truth residual 的 candidate-only 闭合 helper。

本模块只处理 Fund documents candidate internals，见模板第 1 章产品身份、
第 2 章 R=A+B-C 成本/组合事实、第 3 章基金经理画像和第 8 章证据审计
所需的字段证明前置校验。它不读取文件、不调用 Docling、不访问
``FundDocumentRepository``、不调用 source helper，也不构造生产
``EvidenceAnchor``。
"""

from __future__ import annotations

import hashlib
import json
import re
from collections import Counter
from collections.abc import Mapping
from dataclasses import dataclass, replace
from typing import Literal, TypeVar

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
ProducerInputMode = Literal["raw_legacy_v1", "pre_enriched_v2"]
_LiteralT = TypeVar("_LiteralT", bound=str)
TableFamily = Literal[
    "unknown",
    "expense_fee_table",
    "manager_holding_table",
    "portfolio_asset_composition_table",
    "fair_value_hierarchy_table",
    "financial_statement_table",
    "holding_detail_table",
    "fund_profile_table",
    "benchmark_context_table",
    "other",
]
RowHierarchyRole = Literal["unknown", "standalone", "aggregate", "child"]
ShareClassContext = Literal["unknown", "not_applicable", "A", "C"]
ShareClassContextSource = Literal[
    "unknown",
    "not_applicable",
    "column_header",
    "header_band",
    "row_label",
    "table_context",
]
PeriodContext = Literal[
    "unknown",
    "not_applicable",
    "current_period",
    "prior_period",
    "period_end",
]
PeriodContextSource = Literal[
    "unknown",
    "not_applicable",
    "column_header",
    "header_band",
    "table_context",
]
TextSemanticContext = Literal[
    "unknown",
    "benchmark",
    "investment_objective",
    "fund_profile",
    "other",
]
ReferenceEnrichmentStatus = Literal["not_enriched", "partially_enriched", "enriched"]

_SCHEMA_VERSION = "docling_source_truth_residual_closure.v1"
PRODUCER_CONTRACT_VERSION = "docling_reference_bundle_producer_contract.v1"
_ANNUAL_REPORT_EVIDENCE_SOURCE_KIND = "annual_report"
_REFERENCE_BUNDLE_SCHEMA_VERSION = "repository_reference_bundle.v2"
_LEGACY_REFERENCE_BUNDLE_SCHEMA_VERSION = "repository_reference_bundle.v1"
_RAW_TEXT_EXCERPT_CODEPOINT_LIMIT = 200
_ROW_DIAGNOSTIC_CANDIDATE_LIMIT = 20
_TABLE_FAMILY_VALUES: tuple[TableFamily, ...] = (
    "unknown",
    "expense_fee_table",
    "manager_holding_table",
    "portfolio_asset_composition_table",
    "fair_value_hierarchy_table",
    "financial_statement_table",
    "holding_detail_table",
    "fund_profile_table",
    "benchmark_context_table",
    "other",
)
_ROW_HIERARCHY_ROLE_VALUES: tuple[RowHierarchyRole, ...] = (
    "unknown",
    "standalone",
    "aggregate",
    "child",
)
_SHARE_CLASS_CONTEXT_VALUES: tuple[ShareClassContext, ...] = (
    "unknown",
    "not_applicable",
    "A",
    "C",
)
_SHARE_CLASS_CONTEXT_SOURCE_VALUES: tuple[ShareClassContextSource, ...] = (
    "unknown",
    "not_applicable",
    "column_header",
    "header_band",
    "row_label",
    "table_context",
)
_PERIOD_CONTEXT_VALUES: tuple[PeriodContext, ...] = (
    "unknown",
    "not_applicable",
    "current_period",
    "prior_period",
    "period_end",
)
_PERIOD_CONTEXT_SOURCE_VALUES: tuple[PeriodContextSource, ...] = (
    "unknown",
    "not_applicable",
    "column_header",
    "header_band",
    "table_context",
)
_TEXT_SEMANTIC_CONTEXT_VALUES: tuple[TextSemanticContext, ...] = (
    "unknown",
    "benchmark",
    "investment_objective",
    "fund_profile",
    "other",
)
_REFERENCE_ENRICHMENT_STATUS_VALUES: tuple[ReferenceEnrichmentStatus, ...] = (
    "not_enriched",
    "partially_enriched",
    "enriched",
)
_REFERENCE_GENERATION_STATUS_VALUES: tuple[ReferenceGenerationStatus, ...] = (
    "available",
    "blocked_reference_unavailable",
)


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
        allowed_table_families: 允许的表族。
        rejected_table_families: 拒绝的表族。
        required_parent_row_label_any: 任一必须出现的父行标签。
        rejected_parent_row_label_any: 任一出现即拒绝的父行标签。
        required_row_hierarchy_role: 必须匹配的行层级角色。
        rejected_row_hierarchy_roles: 拒绝的行层级角色。
        required_period_context: 必须匹配的期间上下文。
        rejected_period_contexts: 拒绝的期间上下文。
        allowed_share_class_context_sources: 允许的份额类别证明来源。
        required_text_semantic_context: 必须匹配的文本语义上下文。
    """

    field_name: str
    expected_section_id: str
    required_row_label_any: tuple[str, ...] = ()
    rejected_row_label_any: tuple[str, ...] = ()
    required_table_family_any: tuple[str, ...] = ()
    required_column_header_any: tuple[str, ...] = ()
    share_class_context: ShareClassContext | None = None
    allow_semantic_equivalent_duplicate: bool = False
    semantic_guard: str | None = None
    allowed_table_families: tuple[TableFamily, ...] = ()
    rejected_table_families: tuple[TableFamily, ...] = ()
    required_parent_row_label_any: tuple[str, ...] = ()
    rejected_parent_row_label_any: tuple[str, ...] = ()
    required_row_hierarchy_role: RowHierarchyRole | None = None
    rejected_row_hierarchy_roles: tuple[RowHierarchyRole, ...] = ()
    required_period_context: PeriodContext | None = None
    rejected_period_contexts: tuple[PeriodContext, ...] = ()
    allowed_share_class_context_sources: tuple[ShareClassContextSource, ...] = ()
    required_text_semantic_context: TextSemanticContext | None = None


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
        table_title_path: 表格标题路径。
        heading_path: 表格所在章节标题路径。
        column_header_band_path: 多层表头 band 路径。
        table_family: 表族分类。
        row_parent_label_path: 已证明父行标签路径。
        row_hierarchy_path: 已证明父行加当前行路径。
        row_hierarchy_role: 行层级角色。
        bounded_neighbor_row_labels: 有界邻近行诊断标签。
        share_class_context: 规范份额类别上下文。
        share_class_context_source: 份额类别证明来源。
        period_context: 规范期间上下文。
        period_context_source: 期间证明来源。
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
    table_title_path: tuple[str, ...] = ()
    heading_path: tuple[str, ...] = ()
    column_header_band_path: tuple[str, ...] = ()
    table_family: TableFamily = "unknown"
    row_parent_label_path: tuple[str, ...] = ()
    row_hierarchy_path: tuple[str, ...] = ()
    row_hierarchy_role: RowHierarchyRole = "unknown"
    bounded_neighbor_row_labels: tuple[str, ...] = ()
    share_class_context: ShareClassContext = "unknown"
    share_class_context_source: ShareClassContextSource = "unknown"
    period_context: PeriodContext = "unknown"
    period_context_source: PeriodContextSource = "unknown"

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
            "table_title_path": list(self.table_title_path),
            "heading_path": list(self.heading_path),
            "column_header_band_path": list(self.column_header_band_path),
            "table_family": self.table_family,
            "row_parent_label_path": list(self.row_parent_label_path),
            "row_hierarchy_path": list(self.row_hierarchy_path),
            "row_hierarchy_role": self.row_hierarchy_role,
            "bounded_neighbor_row_labels": list(self.bounded_neighbor_row_labels),
            "share_class_context": self.share_class_context,
            "share_class_context_source": self.share_class_context_source,
            "period_context": self.period_context,
            "period_context_source": self.period_context_source,
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
        heading_path: 文本所在标题路径。
        semantic_context_label: 规范文本语义上下文。
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
    heading_path: tuple[str, ...] = ()
    semantic_context_label: TextSemanticContext = "unknown"

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
            "heading_path": list(self.heading_path),
            "semantic_context_label": self.semantic_context_label,
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
        reference_bundle_schema_version: 引用 bundle schema 版本。
        enrichment_status: 富化状态。
        enrichment_notes: 非证明性富化备注。
    """

    sample_id: str
    fund_code: str
    document_year: int
    metadata_ok: bool
    metadata_reason: str | None
    cells: tuple[RepositoryReferenceCell, ...] = ()
    text_spans: tuple[RepositoryReferenceTextSpan, ...] = ()
    reference_generation_status: ReferenceGenerationStatus = "available"
    reference_bundle_schema_version: str = _REFERENCE_BUNDLE_SCHEMA_VERSION
    enrichment_status: ReferenceEnrichmentStatus = "not_enriched"
    enrichment_notes: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, object]:
        """序列化为 JSON 兼容字典。

        Args:
            无。

        Returns:
            JSON 兼容字典。

        Raises:
            无显式抛出。
        """

        diagnostics = _bundle_diagnostic_summary(self)
        return {
            "sample_id": self.sample_id,
            "fund_code": self.fund_code,
            "document_year": self.document_year,
            "metadata_ok": self.metadata_ok,
            "metadata_reason": self.metadata_reason,
            "cells": [cell.to_dict() for cell in self.cells],
            "text_spans": [span.to_dict() for span in self.text_spans],
            "reference_generation_status": self.reference_generation_status,
            "reference_bundle_schema_version": self.reference_bundle_schema_version,
            "enrichment_status": self.enrichment_status,
            "enrichment_notes": list(self.enrichment_notes),
            **diagnostics,
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
    diagnostic_payload: Mapping[str, object] | None = None

    def to_dict(self) -> dict[str, object]:
        """序列化为 JSON 兼容字典。

        Args:
            无。

        Returns:
            JSON 兼容字典。

        Raises:
            无显式抛出。
        """

        diagnostic_payload_available = self.diagnostic_payload is not None
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
            "diagnostic_payload_available": diagnostic_payload_available,
            "diagnostic_payload": dict(self.diagnostic_payload)
            if self.diagnostic_payload is not None
            else None,
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
        allowed_table_families=("portfolio_asset_composition_table",),
        rejected_table_families=(
            "fair_value_hierarchy_table",
            "financial_statement_table",
            "holding_detail_table",
            "unknown",
            "other",
        ),
    ),
    "equity_investment_amount": ResidualClosureRule(
        field_name="equity_investment_amount",
        expected_section_id="§8",
        required_row_label_any=("权益投资",),
        rejected_row_label_any=("其中：股票", "其中:股票", "普通股", "美国"),
        required_table_family_any=("投资组合", "资产组合", "基金资产组合"),
        allowed_table_families=("portfolio_asset_composition_table",),
        rejected_table_families=(
            "fair_value_hierarchy_table",
            "financial_statement_table",
            "holding_detail_table",
            "unknown",
            "other",
        ),
        rejected_row_hierarchy_roles=("child", "unknown"),
    ),
    "stock_investment_amount": ResidualClosureRule(
        field_name="stock_investment_amount",
        expected_section_id="§8",
        required_row_label_any=("其中：股票", "其中:股票", "股票"),
        required_table_family_any=("投资组合", "资产组合", "基金资产组合"),
        allowed_table_families=("portfolio_asset_composition_table",),
        rejected_table_families=(
            "fair_value_hierarchy_table",
            "financial_statement_table",
            "holding_detail_table",
            "unknown",
            "other",
        ),
        required_parent_row_label_any=("权益投资",),
        required_row_hierarchy_role="child",
    ),
    "manager_holding_range_A": ResidualClosureRule(
        field_name="manager_holding_range_A",
        expected_section_id="§10",
        required_row_label_any=("本基金基金经理持有本开放式基金", "基金经理持有"),
        rejected_row_label_any=("合计", "员工", "高级管理人员", "从业人员", "持有人户数"),
        required_table_family_any=("基金经理持有", "管理人持有"),
        share_class_context="A",
        allowed_table_families=("manager_holding_table",),
        rejected_table_families=("unknown", "other"),
        allowed_share_class_context_sources=(
            "column_header",
            "header_band",
            "row_label",
            "table_context",
        ),
    ),
    "sales_service_fee_C_current_year": ResidualClosureRule(
        field_name="sales_service_fee_C_current_year",
        expected_section_id="§7",
        required_row_label_any=("销售服务费",),
        required_table_family_any=("销售服务费",),
        share_class_context="C",
        allow_semantic_equivalent_duplicate=True,
        allowed_table_families=("expense_fee_table",),
        rejected_table_families=("unknown", "other"),
        required_period_context="current_period",
        rejected_period_contexts=("prior_period", "unknown"),
        allowed_share_class_context_sources=(
            "column_header",
            "header_band",
            "row_label",
            "table_context",
        ),
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
        rejected_row_label_any=("投资目标",),
        required_text_semantic_context="benchmark",
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
    bundles = {
        key: _enrich_reference_bundle_contexts(bundle)
        for key, bundle in bundles.items()
    }
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
            diagnostic_payload=_source_absent_diagnostic_payload(row, bundle),
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
            diagnostic_payload=_semantic_residual_diagnostic_payload(
                row,
                rule,
                source_matches,
            ),
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
            _selected_match_diagnostic_payload(row, first_match),
        )
    return _result(
        row,
        "disambiguated_source_body_match",
        "source, processed locator and fund semantic rule agree",
        "same_source_reference_loaded",
        processed_status,
        "semantic_rule_satisfied",
        semantic.matched[0],
        _selected_match_diagnostic_payload(row, semantic.matched[0]),
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
    cell = match.cell
    span = match.text_span
    if section_id != rule.expected_section_id:
        return False
    if rule.rejected_table_families and (
        cell is None or cell.table_family in rule.rejected_table_families
    ):
        return False
    if rule.allowed_table_families and (
        cell is None or cell.table_family not in rule.allowed_table_families
    ):
        return False
    if rule.required_text_semantic_context:
        if span is not None:
            if span.semantic_context_label != rule.required_text_semantic_context:
                return False
        elif not _cell_has_required_text_semantic_context(
            cell,
            rule.required_text_semantic_context,
        ):
            return False
    if rule.rejected_row_label_any and _contains_any(row_labels, rule.rejected_row_label_any):
        return False
    if rule.required_row_label_any and not _contains_any(row_labels, rule.required_row_label_any):
        return False
    parent_labels = _parent_row_labels(cell)
    if rule.rejected_parent_row_label_any and _contains_any(
        parent_labels,
        rule.rejected_parent_row_label_any,
    ):
        return False
    if rule.required_parent_row_label_any and not _contains_any(
        parent_labels,
        rule.required_parent_row_label_any,
    ):
        return False
    if rule.rejected_row_hierarchy_roles and (
        cell is None or cell.row_hierarchy_role in rule.rejected_row_hierarchy_roles
    ):
        return False
    if rule.required_row_hierarchy_role is not None and (
        cell is None or cell.row_hierarchy_role != rule.required_row_hierarchy_role
    ):
        return False
    if rule.required_column_header_any and not _contains_any(
        column_headers,
        rule.required_column_header_any,
    ):
        return False
    if rule.share_class_context and not _has_canonical_share_class_context(
        cell,
        rule.share_class_context,
        rule.allowed_share_class_context_sources,
    ):
        return False
    if rule.required_period_context is not None and (
        cell is None or cell.period_context != rule.required_period_context
    ):
        return False
    if rule.rejected_period_contexts and (
        cell is None or cell.period_context in rule.rejected_period_contexts
    ):
        return False
    has_new_table_family_predicate = bool(
        rule.allowed_table_families or rule.rejected_table_families
    )
    if (
        not has_new_table_family_predicate
        and rule.required_table_family_any
        and not _contains_any(
            table_context,
            rule.required_table_family_any,
        )
    ):
        return False
    if rule.semantic_guard and not _contains_any(
        _semantic_context_values(match),
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


def _bundle_diagnostic_summary(bundle: RepositoryReferenceBundle) -> dict[str, object]:
    """生成 reference bundle producer candidate-only 诊断摘要。

    Args:
        bundle: 仓库引用 bundle。

    Returns:
        只用于 drift/comparability 调试的 JSON 兼容诊断字段。

    Raises:
        无显式抛出。
    """

    diagnostic_payload_available = bundle.reference_generation_status == "available"
    producer_input_mode = _producer_input_mode(bundle)
    cell_diagnostics = _sorted_cell_diagnostics(bundle)
    text_span_diagnostics = _sorted_text_span_diagnostics(bundle)
    table_count = _table_count(bundle)
    section_count = _section_count(bundle)
    table_family_counts = _sorted_counter(
        Counter(cell.table_family for cell in bundle.cells)
    )
    section_inference_counts = _sorted_counter(
        Counter(
            _diagnostic_section_id(section_id)
            for section_id in tuple(cell.section_id for cell in bundle.cells)
            + tuple(span.section_id for span in bundle.text_spans)
        )
    )
    section_inference_reason_counts = _section_inference_reason_counts(bundle)
    row_hierarchy_role_counts = _sorted_counter(
        Counter(cell.row_hierarchy_role for cell in bundle.cells)
    )
    text_semantic_context_counts = _sorted_counter(
        Counter(span.semantic_context_label for span in bundle.text_spans)
    )
    fingerprint_payload = {
        "producer_input_mode": producer_input_mode,
        "cell_count": len(bundle.cells),
        "text_span_count": len(bundle.text_spans),
        "table_count": table_count,
        "section_count": section_count,
        "table_family_counts": table_family_counts,
        "section_inference_counts": section_inference_counts,
        "section_inference_reason_counts": section_inference_reason_counts,
        "row_hierarchy_role_counts": row_hierarchy_role_counts,
        "text_semantic_context_counts": text_semantic_context_counts,
        "cell_normalized_text_hashes": [
            diagnostic["normalized_text_hash"] for diagnostic in cell_diagnostics
        ],
        "text_span_normalized_text_hashes": [
            diagnostic["normalized_text_hash"] for diagnostic in text_span_diagnostics
        ],
    }
    return {
        "producer_contract_version": PRODUCER_CONTRACT_VERSION,
        "producer_input_mode": producer_input_mode,
        "cell_count": len(bundle.cells),
        "text_span_count": len(bundle.text_spans),
        "table_count": table_count,
        "section_count": section_count,
        "table_family_counts": table_family_counts,
        "section_inference_counts": section_inference_counts,
        "section_inference_reason_counts": section_inference_reason_counts,
        "row_hierarchy_role_counts": row_hierarchy_role_counts,
        "text_semantic_context_counts": text_semantic_context_counts,
        "bundle_content_fingerprint": _bundle_content_fingerprint(fingerprint_payload)
        if diagnostic_payload_available
        else None,
        "diagnostic_payload_available": diagnostic_payload_available,
    }


def _selected_match_diagnostic_payload(
    row: ResidualClosureInputRow,
    match: _ReferenceMatch,
) -> dict[str, object]:
    """生成闭合行选中 match 的诊断 payload。

    Args:
        row: residual 输入行。
        match: 已选中引用命中。

    Returns:
        JSON 兼容诊断 payload。

    Raises:
        无显式抛出。
    """

    return {
        "diagnostic_kind": "selected_reference_match",
        "normalized_candidate_hash": _normalized_text_hash(row.normalized_candidate),
        "selected_reference_diagnostic": _match_diagnostic(row.sample_id, match),
    }


def _source_absent_diagnostic_payload(
    row: ResidualClosureInputRow,
    bundle: RepositoryReferenceBundle,
) -> dict[str, object]:
    """生成 source body absent 行的有界搜索诊断。

    Args:
        row: residual 输入行。
        bundle: 已加载的仓库引用 bundle。

    Returns:
        JSON 兼容诊断 payload。

    Raises:
        无显式抛出。
    """

    return {
        "diagnostic_kind": "candidate_search_no_source_match",
        "normalized_candidate_hash": _normalized_text_hash(row.normalized_candidate),
        "searched_cell_count": len(bundle.cells),
        "searched_text_span_count": len(bundle.text_spans),
        "candidate_search_diagnostics": _bounded_reference_diagnostics(row.sample_id, bundle),
    }


def _semantic_residual_diagnostic_payload(
    row: ResidualClosureInputRow,
    rule: ResidualClosureRule,
    source_matches: tuple[_ReferenceMatch, ...],
) -> dict[str, object]:
    """生成 fund semantic residual 行的候选拒绝诊断。

    Args:
        row: residual 输入行。
        rule: 字段闭合规则。
        source_matches: 已确认同源文本命中的候选引用。

    Returns:
        JSON 兼容诊断 payload。

    Raises:
        无显式抛出。
    """

    sorted_matches = sorted(
        source_matches,
        key=lambda match: _match_sort_key(row.sample_id, match),
    )
    considered = []
    for match in sorted_matches[:_ROW_DIAGNOSTIC_CANDIDATE_LIMIT]:
        considered.append(
            {
                "reference_diagnostic": _match_diagnostic(row.sample_id, match),
                "rejection_categories": _semantic_rejection_categories(match, rule),
            }
        )
    return {
        "diagnostic_kind": "semantic_assignment_considered_matches",
        "normalized_candidate_hash": _normalized_text_hash(row.normalized_candidate),
        "considered_match_count": len(source_matches),
        "considered_match_diagnostics": considered,
    }


def _bounded_reference_diagnostics(
    sample_id: str,
    bundle: RepositoryReferenceBundle,
) -> dict[str, object]:
    """生成 bundle 内有界候选引用诊断。

    Args:
        sample_id: 样本 ID。
        bundle: 已加载的仓库引用 bundle。

    Returns:
        JSON 兼容候选引用诊断。

    Raises:
        无显式抛出。
    """

    cell_matches = (
        _ReferenceMatch(cell=cell) for cell in _sorted_cells(bundle)
    )
    span_matches = (
        _ReferenceMatch(text_span=span) for span in _sorted_text_spans(bundle)
    )
    return {
        "cells": [
            _match_diagnostic(sample_id, match)
            for match in tuple(cell_matches)[:_ROW_DIAGNOSTIC_CANDIDATE_LIMIT]
        ],
        "text_spans": [
            _match_diagnostic(sample_id, match)
            for match in tuple(span_matches)[:_ROW_DIAGNOSTIC_CANDIDATE_LIMIT]
        ],
        "diagnostic_limit": _ROW_DIAGNOSTIC_CANDIDATE_LIMIT,
    }


def _semantic_rejection_categories(
    match: _ReferenceMatch,
    rule: ResidualClosureRule,
) -> tuple[dict[str, object], ...]:
    """返回 match 不满足 fund 规则的诊断分类。

    Args:
        match: 引用命中。
        rule: 字段闭合规则。

    Returns:
        拒绝分类 tuple；满足规则时为空 tuple。

    Raises:
        无显式抛出。
    """

    categories: list[dict[str, object]] = []
    row_labels = _row_labels(match)
    column_headers = _column_headers(match)
    table_context = _table_context(match)
    section_id = _section_id(match)
    cell = match.cell
    span = match.text_span
    if section_id != rule.expected_section_id:
        categories.append(
            {
                "category": "section_id_mismatch",
                "expected_section_id": rule.expected_section_id,
                "actual_section_id": section_id,
            }
        )
    if rule.rejected_table_families and (
        cell is None or cell.table_family in rule.rejected_table_families
    ):
        categories.append(
            {
                "category": "rejected_table_family",
                "rejected_table_families": list(rule.rejected_table_families),
                "actual_table_family": cell.table_family if cell is not None else None,
            }
        )
    if rule.allowed_table_families and (
        cell is None or cell.table_family not in rule.allowed_table_families
    ):
        categories.append(
            {
                "category": "table_family_not_allowed",
                "allowed_table_families": list(rule.allowed_table_families),
                "actual_table_family": cell.table_family if cell is not None else None,
            }
        )
    if rule.required_text_semantic_context and not _match_has_required_text_context(
        match,
        rule.required_text_semantic_context,
    ):
        categories.append(
            {
                "category": "required_text_semantic_context_absent",
                "required_text_semantic_context": rule.required_text_semantic_context,
                "actual_text_semantic_context": span.semantic_context_label
                if span is not None
                else None,
            }
        )
    if rule.rejected_row_label_any and _contains_any(row_labels, rule.rejected_row_label_any):
        categories.append(
            {
                "category": "rejected_row_label",
                "rejected_row_label_any": list(rule.rejected_row_label_any),
                "actual_row_label_path": list(row_labels),
            }
        )
    if rule.required_row_label_any and not _contains_any(row_labels, rule.required_row_label_any):
        categories.append(
            {
                "category": "required_row_label_absent",
                "required_row_label_any": list(rule.required_row_label_any),
                "actual_row_label_path": list(row_labels),
            }
        )
    parent_labels = _parent_row_labels(cell)
    if rule.rejected_parent_row_label_any and _contains_any(
        parent_labels,
        rule.rejected_parent_row_label_any,
    ):
        categories.append(
            {
                "category": "rejected_parent_row_label",
                "rejected_parent_row_label_any": list(rule.rejected_parent_row_label_any),
                "actual_parent_row_label_path": list(parent_labels),
            }
        )
    if rule.required_parent_row_label_any and not _contains_any(
        parent_labels,
        rule.required_parent_row_label_any,
    ):
        categories.append(
            {
                "category": "required_parent_row_label_absent",
                "required_parent_row_label_any": list(rule.required_parent_row_label_any),
                "actual_parent_row_label_path": list(parent_labels),
            }
        )
    if rule.rejected_row_hierarchy_roles and (
        cell is None or cell.row_hierarchy_role in rule.rejected_row_hierarchy_roles
    ):
        categories.append(
            {
                "category": "rejected_row_hierarchy_role",
                "rejected_row_hierarchy_roles": list(rule.rejected_row_hierarchy_roles),
                "actual_row_hierarchy_role": cell.row_hierarchy_role
                if cell is not None
                else None,
            }
        )
    if rule.required_row_hierarchy_role is not None and (
        cell is None or cell.row_hierarchy_role != rule.required_row_hierarchy_role
    ):
        categories.append(
            {
                "category": "required_row_hierarchy_role_absent",
                "required_row_hierarchy_role": rule.required_row_hierarchy_role,
                "actual_row_hierarchy_role": cell.row_hierarchy_role
                if cell is not None
                else None,
            }
        )
    if rule.required_column_header_any and not _contains_any(
        column_headers,
        rule.required_column_header_any,
    ):
        categories.append(
            {
                "category": "required_column_header_absent",
                "required_column_header_any": list(rule.required_column_header_any),
                "actual_column_header_path": list(column_headers),
            }
        )
    if rule.share_class_context and not _has_canonical_share_class_context(
        cell,
        rule.share_class_context,
        rule.allowed_share_class_context_sources,
    ):
        categories.append(
            {
                "category": "share_class_context_mismatch",
                "required_share_class_context": rule.share_class_context,
                "actual_share_class_context": cell.share_class_context
                if cell is not None
                else None,
                "actual_share_class_context_source": cell.share_class_context_source
                if cell is not None
                else None,
            }
        )
    if rule.required_period_context is not None and (
        cell is None or cell.period_context != rule.required_period_context
    ):
        categories.append(
            {
                "category": "period_context_mismatch",
                "required_period_context": rule.required_period_context,
                "actual_period_context": cell.period_context if cell is not None else None,
            }
        )
    if rule.rejected_period_contexts and (
        cell is None or cell.period_context in rule.rejected_period_contexts
    ):
        categories.append(
            {
                "category": "rejected_period_context",
                "rejected_period_contexts": list(rule.rejected_period_contexts),
                "actual_period_context": cell.period_context if cell is not None else None,
            }
        )
    has_new_table_family_predicate = bool(
        rule.allowed_table_families or rule.rejected_table_families
    )
    if (
        not has_new_table_family_predicate
        and rule.required_table_family_any
        and not _contains_any(table_context, rule.required_table_family_any)
    ):
        categories.append(
            {
                "category": "required_table_family_text_absent",
                "required_table_family_any": list(rule.required_table_family_any),
                "actual_table_context": list(table_context),
            }
        )
    if rule.semantic_guard and not _contains_any(
        _semantic_context_values(match),
        (rule.semantic_guard,),
    ):
        categories.append(
            {
                "category": "semantic_guard_absent",
                "semantic_guard": rule.semantic_guard,
            }
        )
    return tuple(categories)


def _match_has_required_text_context(
    match: _ReferenceMatch,
    required_context: TextSemanticContext,
) -> bool:
    """判断 match 是否满足文本语义上下文要求。

    Args:
        match: 引用命中。
        required_context: 必须的文本语义上下文。

    Returns:
        满足时返回 ``True``。

    Raises:
        无显式抛出。
    """

    if match.text_span is not None:
        return match.text_span.semantic_context_label == required_context
    return _cell_has_required_text_semantic_context(match.cell, required_context)


def _match_diagnostic(sample_id: str, match: _ReferenceMatch) -> dict[str, object]:
    """生成单个引用 match 的有界诊断。

    Args:
        sample_id: 样本 ID。
        match: 引用命中。

    Returns:
        JSON 兼容引用诊断。

    Raises:
        无显式抛出。
    """

    if match.cell is not None:
        return _cell_diagnostic_payload(sample_id, match.cell)
    if match.text_span is not None:
        return _text_span_diagnostic_payload(sample_id, match.text_span)
    return {"sample_id": sample_id, "reference_kind": "unknown"}


def _cell_diagnostic_payload(
    sample_id: str,
    cell: RepositoryReferenceCell,
) -> dict[str, object]:
    """生成单元格引用诊断 payload。

    Args:
        sample_id: 样本 ID。
        cell: 单元格引用。

    Returns:
        JSON 兼容单元格诊断。

    Raises:
        无显式抛出。
    """

    normalized_text = _diagnostic_normalized_text(cell.normalized_text)
    return {
        "reference_kind": "cell",
        "sample_id": sample_id,
        "table_id": cell.table_id,
        "row_index": cell.row_index,
        "column_index": cell.column_index,
        "section_id": cell.section_id,
        "page_number": cell.page_number,
        "row_label_path": list(cell.row_label_path),
        "column_header_path": list(cell.column_header_path),
        "table_context": list(cell.table_context),
        "table_family": cell.table_family,
        "row_parent_label_path": list(cell.row_parent_label_path),
        "row_hierarchy_path": list(cell.row_hierarchy_path),
        "row_hierarchy_role": cell.row_hierarchy_role,
        "share_class_context": cell.share_class_context,
        "share_class_context_source": cell.share_class_context_source,
        "period_context": cell.period_context,
        "period_context_source": cell.period_context_source,
        "normalized_text_hash": _normalized_text_hash(normalized_text),
        "raw_text_excerpt": _raw_text_excerpt(normalized_text),
    }


def _text_span_diagnostic_payload(
    sample_id: str,
    span: RepositoryReferenceTextSpan,
) -> dict[str, object]:
    """生成文本 span 引用诊断 payload。

    Args:
        sample_id: 样本 ID。
        span: 文本引用。

    Returns:
        JSON 兼容文本 span 诊断。

    Raises:
        无显式抛出。
    """

    normalized_text = _diagnostic_normalized_text(span.normalized_text)
    return {
        "reference_kind": "text_span",
        "sample_id": sample_id,
        "section_id": span.section_id,
        "page_number": span.page_number,
        "context_label": span.context_label,
        "heading_path": list(span.heading_path),
        "semantic_context_label": span.semantic_context_label,
        "normalized_text_hash": _normalized_text_hash(normalized_text),
        "raw_text_excerpt": _raw_text_excerpt(normalized_text),
    }


def _sorted_cell_diagnostics(
    bundle: RepositoryReferenceBundle,
) -> tuple[dict[str, object], ...]:
    """按生产者契约顺序返回 cell 诊断。

    Args:
        bundle: 仓库引用 bundle。

    Returns:
        已排序 cell 诊断 tuple。

    Raises:
        无显式抛出。
    """

    return tuple(
        _cell_diagnostic_payload(bundle.sample_id, cell)
        for cell in _sorted_cells(bundle)
    )


def _sorted_text_span_diagnostics(
    bundle: RepositoryReferenceBundle,
) -> tuple[dict[str, object], ...]:
    """按生产者契约顺序返回 text span 诊断。

    Args:
        bundle: 仓库引用 bundle。

    Returns:
        已排序 text span 诊断 tuple。

    Raises:
        无显式抛出。
    """

    return tuple(
        _text_span_diagnostic_payload(bundle.sample_id, span)
        for span in _sorted_text_spans(bundle)
    )


def _sorted_cells(
    bundle: RepositoryReferenceBundle,
) -> tuple[RepositoryReferenceCell, ...]:
    """按生产者契约排序 cell。

    Args:
        bundle: 仓库引用 bundle。

    Returns:
        已排序 cell tuple。

    Raises:
        无显式抛出。
    """

    return tuple(sorted(bundle.cells, key=lambda cell: _cell_sort_key(bundle.sample_id, cell)))


def _sorted_text_spans(
    bundle: RepositoryReferenceBundle,
) -> tuple[RepositoryReferenceTextSpan, ...]:
    """按生产者契约排序 text span。

    Args:
        bundle: 仓库引用 bundle。

    Returns:
        已排序 text span tuple。

    Raises:
        无显式抛出。
    """

    return tuple(
        sorted(
            bundle.text_spans,
            key=lambda span: _text_span_sort_key(bundle.sample_id, span),
        )
    )


def _match_sort_key(
    sample_id: str,
    match: _ReferenceMatch,
) -> tuple[object, ...]:
    """返回 match 诊断排序 key。

    Args:
        sample_id: 样本 ID。
        match: 引用命中。

    Returns:
        可排序 key。

    Raises:
        无显式抛出。
    """

    if match.cell is not None:
        return ("cell", *_cell_sort_key(sample_id, match.cell))
    if match.text_span is not None:
        return ("text_span", *_text_span_sort_key(sample_id, match.text_span))
    return ("unknown", sample_id)


def _cell_sort_key(
    sample_id: str,
    cell: RepositoryReferenceCell,
) -> tuple[object, ...]:
    """返回 deterministic cell sort key。

    Args:
        sample_id: 样本 ID。
        cell: 单元格引用。

    Returns:
        生产者契约排序 key。

    Raises:
        无显式抛出。
    """

    return (
        sample_id,
        cell.fund_code,
        cell.document_year,
        cell.page_number,
        cell.table_id,
        cell.row_index,
        cell.column_index,
        _normalized_text_hash(cell.normalized_text),
    )


def _text_span_sort_key(
    sample_id: str,
    span: RepositoryReferenceTextSpan,
) -> tuple[object, ...]:
    """返回 deterministic text span sort key。

    Args:
        sample_id: 样本 ID。
        span: 文本引用。

    Returns:
        生产者契约排序 key。

    Raises:
        无显式抛出。
    """

    return (
        sample_id,
        span.fund_code,
        span.document_year,
        span.page_number,
        span.section_id,
        span.context_label,
        _normalized_text_hash(span.normalized_text),
    )


def _producer_input_mode(bundle: RepositoryReferenceBundle) -> ProducerInputMode:
    """返回 producer input mode。

    Args:
        bundle: 仓库引用 bundle。

    Returns:
        raw v1 或 pre-enriched v2。

    Raises:
        无显式抛出。
    """

    if bundle.reference_bundle_schema_version == _LEGACY_REFERENCE_BUNDLE_SCHEMA_VERSION:
        return "raw_legacy_v1"
    return "pre_enriched_v2"


def _table_count(bundle: RepositoryReferenceBundle) -> int:
    """返回 bundle 内唯一 table identity 数量。

    Args:
        bundle: 仓库引用 bundle。

    Returns:
        table 数量。

    Raises:
        无显式抛出。
    """

    return len(
        {
            (
                cell.fund_code,
                cell.document_year,
                cell.repository_source_name,
                cell.section_id,
                cell.table_id,
            )
            for cell in bundle.cells
        }
    )


def _section_count(bundle: RepositoryReferenceBundle) -> int:
    """返回 bundle 内唯一 section id 数量。

    Args:
        bundle: 仓库引用 bundle。

    Returns:
        section 数量。

    Raises:
        无显式抛出。
    """

    return len(
        {
            _diagnostic_section_id(section_id)
            for section_id in tuple(cell.section_id for cell in bundle.cells)
            + tuple(span.section_id for span in bundle.text_spans)
        }
    )


def _section_inference_reason_counts(
    bundle: RepositoryReferenceBundle,
) -> dict[str, int]:
    """返回 section 诊断原因计数。

    Args:
        bundle: 仓库引用 bundle。

    Returns:
        section reason 计数字典。

    Raises:
        无显式抛出。
    """

    reasons = Counter(
        "explicit_section_id"
        if _diagnostic_section_id(section_id) != "unknown"
        else "missing_section_id"
        for section_id in tuple(cell.section_id for cell in bundle.cells)
        + tuple(span.section_id for span in bundle.text_spans)
    )
    return _sorted_counter(reasons)


def _diagnostic_section_id(section_id: object) -> str:
    """返回诊断用 section id。

    Args:
        section_id: 原始 section id。

    Returns:
        空值时返回 ``unknown``。

    Raises:
        无显式抛出。
    """

    normalized = _diagnostic_normalized_text(section_id)
    return normalized if normalized else "unknown"


def _bundle_content_fingerprint(fingerprint_payload: Mapping[str, object]) -> str:
    """按生产者契约计算 bundle content fingerprint。

    Args:
        fingerprint_payload: 只包含 hash-participating content 的 payload。

    Returns:
        SHA256 hex digest。

    Raises:
        无显式抛出。
    """

    serialized = json.dumps(
        fingerprint_payload,
        sort_keys=True,
        ensure_ascii=False,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(serialized).hexdigest()


def _normalized_text_hash(value: object) -> str:
    """按生产者契约计算 normalized_text_hash。

    Args:
        value: 原始文本。

    Returns:
        SHA256 hex digest。

    Raises:
        无显式抛出。
    """

    normalized_text = _diagnostic_normalized_text(value)
    return hashlib.sha256(normalized_text.encode("utf-8")).hexdigest()


def _diagnostic_normalized_text(value: object) -> str:
    """按生产者契约归一化诊断文本。

    Args:
        value: 原始文本；``None`` 视为 ``""``。

    Returns:
        Unicode whitespace 折叠后的文本。

    Raises:
        无显式抛出。
    """

    text = "" if value is None else str(value)
    return re.sub(r"\s+", " ", text).strip()


def _raw_text_excerpt(normalized_text: str) -> str:
    """返回有界 raw text excerpt。

    Args:
        normalized_text: 已按诊断契约归一化的文本。

    Returns:
        最多 203 code points 的 excerpt。

    Raises:
        无显式抛出。
    """

    if len(normalized_text) <= _RAW_TEXT_EXCERPT_CODEPOINT_LIMIT:
        return normalized_text
    return f"{normalized_text[:_RAW_TEXT_EXCERPT_CODEPOINT_LIMIT]}..."


def _sorted_counter(counter: Counter[str]) -> dict[str, int]:
    """把 Counter 转成 key 排序的普通字典。

    Args:
        counter: 字符串计数器。

    Returns:
        key 排序字典。

    Raises:
        无显式抛出。
    """

    return {key: counter[key] for key in sorted(counter)}


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
        reference_generation_status=_coerce_literal(
            value.get("reference_generation_status"),
            _REFERENCE_GENERATION_STATUS_VALUES,
            "available",
        ),
        reference_bundle_schema_version=str(
            value.get("reference_bundle_schema_version", _LEGACY_REFERENCE_BUNDLE_SCHEMA_VERSION)
        ),
        enrichment_status=_coerce_literal(
            value.get("enrichment_status"),
            _REFERENCE_ENRICHMENT_STATUS_VALUES,
            "not_enriched",
        ),
        enrichment_notes=_string_tuple(value.get("enrichment_notes")),
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
    row_label_path = _string_tuple(value.get("row_label_path"))
    row_hierarchy_role = _coerce_literal(
        value.get("row_hierarchy_role"),
        _ROW_HIERARCHY_ROLE_VALUES,
        "unknown",
    )
    row_hierarchy_path = _string_tuple(value.get("row_hierarchy_path"))
    if row_hierarchy_role == "standalone" and not row_hierarchy_path:
        row_hierarchy_path = row_label_path
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
        row_label_path=row_label_path,
        column_header_path=_string_tuple(value.get("column_header_path")),
        raw_text=str(value.get("raw_text", "")),
        normalized_text=str(value.get("normalized_text", value.get("raw_text", ""))),
        table_context=_string_tuple(value.get("table_context")),
        reference_origin=str(  # type: ignore[arg-type]
            value.get("reference_origin", "fund_document_repository_parsed_table")
        ),
        table_title_path=_string_tuple(value.get("table_title_path")),
        heading_path=_string_tuple(value.get("heading_path")),
        column_header_band_path=_string_tuple(value.get("column_header_band_path")),
        table_family=_coerce_literal(
            value.get("table_family"),
            _TABLE_FAMILY_VALUES,
            "unknown",
        ),
        row_parent_label_path=_string_tuple(value.get("row_parent_label_path")),
        row_hierarchy_path=row_hierarchy_path,
        row_hierarchy_role=row_hierarchy_role,
        bounded_neighbor_row_labels=_string_tuple(value.get("bounded_neighbor_row_labels")),
        share_class_context=_coerce_literal(
            value.get("share_class_context"),
            _SHARE_CLASS_CONTEXT_VALUES,
            "unknown",
        ),
        share_class_context_source=_coerce_literal(
            value.get("share_class_context_source"),
            _SHARE_CLASS_CONTEXT_SOURCE_VALUES,
            "unknown",
        ),
        period_context=_coerce_literal(
            value.get("period_context"),
            _PERIOD_CONTEXT_VALUES,
            "unknown",
        ),
        period_context_source=_coerce_literal(
            value.get("period_context_source"),
            _PERIOD_CONTEXT_SOURCE_VALUES,
            "unknown",
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
        heading_path=_string_tuple(value.get("heading_path")),
        semantic_context_label=_coerce_literal(
            value.get("semantic_context_label"),
            _TEXT_SEMANTIC_CONTEXT_VALUES,
            "unknown",
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
    diagnostic_payload: Mapping[str, object] | None = None,
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
        diagnostic_payload: 可选 candidate-only 诊断 payload。

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
        diagnostic_payload=diagnostic_payload,
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


def _parent_row_labels(cell: RepositoryReferenceCell | None) -> tuple[str, ...]:
    """返回已证明的父行标签。

    Args:
        cell: 单元格引用。

    Returns:
        父行标签 tuple。

    Raises:
        无显式抛出。
    """

    if cell is None:
        return ()
    if cell.row_parent_label_path:
        return cell.row_parent_label_path
    if len(cell.row_hierarchy_path) > 1:
        return cell.row_hierarchy_path[:-1]
    return ()


def _semantic_context_values(match: _ReferenceMatch) -> tuple[str, ...]:
    """返回用于语义 guard 的已加载上下文。

    Args:
        match: 引用命中。

    Returns:
        语义上下文 tuple。

    Raises:
        无显式抛出。
    """

    if match.cell is not None:
        cell = match.cell
        return (
            cell.row_label_path
            + cell.table_context
            + cell.table_title_path
            + cell.heading_path
        )
    if match.text_span is not None:
        span = match.text_span
        return (span.context_label,) + span.heading_path
    return ()


def _cell_has_required_text_semantic_context(
    cell: RepositoryReferenceCell | None,
    required_context: TextSemanticContext,
) -> bool:
    """判断表格单元格是否具备等价文本语义上下文。

    Args:
        cell: 单元格引用。
        required_context: 必须满足的文本语义上下文。

    Returns:
        满足时返回 ``True``。

    Raises:
        无显式抛出。
    """

    if cell is None:
        return False
    if required_context == "benchmark":
        if _contains_any(_semantic_context_values(_ReferenceMatch(cell=cell)), ("投资目标",)):
            return False
        return _contains_any(
            cell.row_label_path + cell.table_context + cell.heading_path + cell.table_title_path,
            ("业绩比较基准",),
        )
    return False


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


def _has_canonical_share_class_context(
    cell: RepositoryReferenceCell | None,
    share_class: ShareClassContext,
    allowed_sources: tuple[ShareClassContextSource, ...],
) -> bool:
    """判断单元格是否具备规范份额类别上下文。

    Args:
        cell: 单元格引用。
        share_class: 规则要求的份额类别。
        allowed_sources: 允许的证明来源；空 tuple 表示任一已证明来源。

    Returns:
        满足时返回 ``True``。

    Raises:
        无显式抛出。
    """

    if cell is None or share_class in ("unknown", "not_applicable"):
        return False
    if cell.share_class_context != share_class:
        return False
    if cell.share_class_context_source in ("unknown", "not_applicable"):
        return False
    return not allowed_sources or cell.share_class_context_source in allowed_sources


def _derive_share_class_context(
    cell: RepositoryReferenceCell,
) -> tuple[ShareClassContext, ShareClassContextSource]:
    """从已加载的表头/行/表上下文派生规范份额类别。

    Args:
        cell: 单元格引用。

    Returns:
        ``(share_class_context, share_class_context_source)``。

    Raises:
        无显式抛出。
    """

    sources: tuple[tuple[ShareClassContextSource, tuple[str, ...]], ...] = (
        ("column_header", cell.column_header_path),
        ("header_band", cell.column_header_band_path),
        ("row_label", cell.row_label_path),
        ("table_context", cell.table_context),
    )
    selected: ShareClassContext = "unknown"
    selected_source: ShareClassContextSource = "unknown"
    for source, values in sources:
        matched = _share_classes_in_values(values)
        if len(matched) > 1:
            return "unknown", "unknown"
        if len(matched) == 0:
            continue
        current = matched[0]
        if selected == "unknown":
            selected = current
            selected_source = source
            continue
        if selected != current:
            return "unknown", "unknown"
    return selected, selected_source


def _share_classes_in_values(values: tuple[str, ...]) -> tuple[ShareClassContext, ...]:
    """返回文本集合中明确出现的份额类别。

    Args:
        values: 待检查文本。

    Returns:
        去重后的份额类别。

    Raises:
        无显式抛出。
    """

    matched: list[ShareClassContext] = []
    for share_class in ("A", "C"):
        if _has_share_class_context(values, share_class):
            matched.append(share_class)
    return tuple(matched)


def _derive_period_context(
    cell: RepositoryReferenceCell,
) -> tuple[PeriodContext, PeriodContextSource]:
    """从已加载的表头/header band/表上下文派生规范期间。

    Args:
        cell: 单元格引用。

    Returns:
        ``(period_context, period_context_source)``。

    Raises:
        无显式抛出。
    """

    sources: tuple[tuple[PeriodContextSource, tuple[str, ...]], ...] = (
        ("column_header", cell.column_header_path),
        ("header_band", cell.column_header_band_path),
        ("table_context", cell.table_context),
    )
    selected: PeriodContext = "unknown"
    selected_source: PeriodContextSource = "unknown"
    for source, values in sources:
        matched = _period_contexts_in_values(values)
        if len(matched) > 1:
            return "unknown", "unknown"
        if len(matched) == 0:
            continue
        current = matched[0]
        if selected == "unknown":
            selected = current
            selected_source = source
            continue
        if selected != current:
            return "unknown", "unknown"
    return selected, selected_source


def _period_contexts_in_values(values: tuple[str, ...]) -> tuple[PeriodContext, ...]:
    """返回文本集合中明确出现的期间上下文。

    Args:
        values: 待检查文本。

    Returns:
        去重后的期间上下文。

    Raises:
        无显式抛出。
    """

    contexts: list[PeriodContext] = []
    for value in values:
        context = _period_context_from_text(value)
        if context != "unknown" and context not in contexts:
            contexts.append(context)
    return tuple(contexts)


def _period_context_from_text(value: str) -> PeriodContext:
    """从单段文本识别规范期间。

    Args:
        value: 原始文本。

    Returns:
        期间上下文。

    Raises:
        无显式抛出。
    """

    normalized = _normalize_for_label(value)
    if any(term in normalized for term in ("报告期末", "期末余额", "期末公允价值", "期末")):
        return "period_end"
    if any(
        term in normalized
        for term in ("上年度可比期间", "上年同期", "上年度", "上期")
    ):
        return "prior_period"
    if any(
        term in normalized
        for term in ("本期发生额", "本报告期", "报告期", "本期", "本年", "当前")
    ):
        return "current_period"
    return "unknown"


def _classify_bundle_tables(bundle: RepositoryReferenceBundle) -> RepositoryReferenceBundle:
    """按 table identity 对 bundle 内单元格做候选表族分类。

    Args:
        bundle: 引用 bundle。

    Returns:
        已广播表族分类的引用 bundle。

    Raises:
        无显式抛出。
    """

    if not bundle.cells:
        return bundle
    grouped: dict[tuple[str, int, str, str, str], list[RepositoryReferenceCell]] = {}
    for cell in bundle.cells:
        key = (
            cell.fund_code,
            cell.document_year,
            cell.repository_source_name,
            cell.section_id,
            cell.table_id,
        )
        grouped.setdefault(key, []).append(cell)
    family_by_key = {
        key: _classify_table_family(tuple(cells)) for key, cells in grouped.items()
    }
    cells = tuple(
        replace(
            cell,
            table_family=family_by_key[
                (
                    cell.fund_code,
                    cell.document_year,
                    cell.repository_source_name,
                    cell.section_id,
                    cell.table_id,
                )
            ],
        )
        for cell in bundle.cells
    )
    return replace(bundle, cells=cells)


def _enrich_reference_bundle_contexts(
    bundle: RepositoryReferenceBundle,
) -> RepositoryReferenceBundle:
    """为 legacy/raw bundle 派生候选上下文。

    Args:
        bundle: 引用 bundle。

    Returns:
        legacy/raw bundle 返回带派生 context 的引用 bundle；v2 bundle 原样返回。

    Raises:
        无显式抛出。
    """

    if bundle.reference_bundle_schema_version != _LEGACY_REFERENCE_BUNDLE_SCHEMA_VERSION:
        return bundle
    classified = _classify_bundle_tables(bundle)
    hierarchy_enriched = _enrich_row_hierarchy_contexts(classified)
    cells: list[RepositoryReferenceCell] = []
    for cell in hierarchy_enriched.cells:
        share_context, share_source = _derive_share_class_context(cell)
        period_context, period_source = _derive_period_context(cell)
        cells.append(
            replace(
                cell,
                share_class_context=share_context,
                share_class_context_source=share_source,
                period_context=period_context,
                period_context_source=period_source,
            )
        )
    context_enriched = replace(hierarchy_enriched, cells=tuple(cells))
    return _enrich_text_span_semantic_contexts(context_enriched)


def _enrich_row_hierarchy_contexts(
    bundle: RepositoryReferenceBundle,
) -> RepositoryReferenceBundle:
    """为 legacy/raw §8 组合表派生候选行层级。

    Args:
        bundle: 已完成表族分类的引用 bundle。

    Returns:
        带已证明 aggregate/child 行层级的引用 bundle。

    Raises:
        无显式抛出。
    """

    if not bundle.cells:
        return bundle
    grouped: dict[tuple[str, int, str, str, str], list[RepositoryReferenceCell]] = {}
    for cell in bundle.cells:
        key = (
            cell.fund_code,
            cell.document_year,
            cell.repository_source_name,
            cell.section_id,
            cell.table_id,
        )
        grouped.setdefault(key, []).append(cell)
    hierarchy_by_cell: dict[
        tuple[str, int, str, str, str, int, int],
        tuple[tuple[str, ...], tuple[str, ...], RowHierarchyRole],
    ] = {}
    for key, cells in grouped.items():
        table_hierarchy = _derive_table_row_hierarchy(tuple(cells))
        for row_column, hierarchy in table_hierarchy.items():
            hierarchy_by_cell[(*key, *row_column)] = hierarchy
    if not hierarchy_by_cell:
        return bundle
    enriched_cells: list[RepositoryReferenceCell] = []
    for cell in bundle.cells:
        key = (
            cell.fund_code,
            cell.document_year,
            cell.repository_source_name,
            cell.section_id,
            cell.table_id,
            cell.row_index,
            cell.column_index,
        )
        hierarchy = hierarchy_by_cell.get(key)
        if hierarchy is None:
            enriched_cells.append(cell)
            continue
        parent_path, hierarchy_path, role = hierarchy
        enriched_cells.append(
            replace(
                cell,
                row_parent_label_path=parent_path,
                row_hierarchy_path=hierarchy_path,
                row_hierarchy_role=role,
            )
        )
    return replace(bundle, cells=tuple(enriched_cells))


def _derive_table_row_hierarchy(
    cells: tuple[RepositoryReferenceCell, ...],
) -> dict[tuple[int, int], tuple[tuple[str, ...], tuple[str, ...], RowHierarchyRole]]:
    """从单表内显式行标签派生组合表父子层级。

    Args:
        cells: 同一 table identity 下的单元格。

    Returns:
        以 ``(row_index, column_index)`` 为 key 的层级证明映射。

    Raises:
        无显式抛出。
    """

    if not cells:
        return {}
    if any(cell.section_id != "§8" for cell in cells):
        return {}
    if any(cell.table_family != "portfolio_asset_composition_table" for cell in cells):
        return {}

    row_labels: dict[int, str] = {}
    cell_identities: set[tuple[int, int]] = set()
    for cell in cells:
        if not _is_comparable_row_index(cell.row_index):
            return {}
        cell_identity = (cell.row_index, cell.column_index)
        if cell_identity in cell_identities:
            return {}
        cell_identities.add(cell_identity)
        label = _row_primary_label(cell)
        if not label:
            return {}
        existing = row_labels.get(cell.row_index)
        if existing is not None and existing != label:
            return {}
        row_labels[cell.row_index] = label

    sorted_rows = tuple(sorted(row_labels.items()))
    parent_by_row: dict[int, str] = {}
    current_parent: tuple[int, str] | None = None
    for row_index, label in sorted_rows:
        if _is_equity_parent_label(label):
            current_parent = (row_index, label)
            continue
        if _is_stock_child_label(label):
            if current_parent is not None:
                parent_index, parent_label = current_parent
                if parent_index < row_index:
                    parent_by_row[row_index] = parent_label
            continue
        if _is_detail_or_geography_row(label):
            current_parent = None
            continue
        if _is_explicit_top_level_asset_row(label):
            current_parent = None

    children_by_parent: dict[str, list[int]] = {}
    for child_index, parent_label in parent_by_row.items():
        children_by_parent.setdefault(parent_label, []).append(child_index)
    if not children_by_parent:
        return {}

    hierarchy: dict[tuple[int, int], tuple[tuple[str, ...], tuple[str, ...], RowHierarchyRole]] = {}
    proven_parent_labels = set(children_by_parent)
    for cell in cells:
        label = row_labels[cell.row_index]
        if _is_equity_parent_label(label) and label in proven_parent_labels:
            hierarchy[(cell.row_index, cell.column_index)] = ((), (label,), "aggregate")
            continue
        parent_label = parent_by_row.get(cell.row_index)
        if parent_label is not None and _is_stock_child_label(label):
            hierarchy[(cell.row_index, cell.column_index)] = (
                (parent_label,),
                (parent_label, label),
                "child",
            )
    return hierarchy


def _row_primary_label(cell: RepositoryReferenceCell) -> str:
    """返回单元格最贴近数值的行标签。

    Args:
        cell: 单元格引用。

    Returns:
        ``row_label_path`` 最后一个非空 strip 后元素；不存在时返回空字符串。

    Raises:
        无显式抛出。
    """

    for label in reversed(cell.row_label_path):
        stripped = label.strip()
        if stripped:
            return stripped
    return ""


def _is_equity_parent_label(label: str) -> bool:
    """判断行标签是否为组合表权益投资父行。

    Args:
        label: primary row label。

    Returns:
        是权益投资父行时返回 ``True``。

    Raises:
        无显式抛出。
    """

    return "权益投资" in _normalize_for_label(label)


def _is_stock_child_label(label: str) -> bool:
    """判断行标签是否为本 gate 允许正向闭合的股票 child 行。

    Args:
        label: primary row label。

    Returns:
        标签同时包含 ``其中`` 和 ``股票`` 时返回 ``True``。

    Raises:
        无显式抛出。
    """

    normalized = _normalize_for_label(label)
    return "其中" in normalized and "股票" in normalized


def _is_explicit_top_level_asset_row(label: str) -> bool:
    """判断行标签是否为明确的组合表顶层资产行。

    Args:
        label: primary row label。

    Returns:
        是顶层资产行时返回 ``True``。

    Raises:
        无显式抛出。
    """

    normalized = _normalize_for_label(label)
    return any(
        _normalize_for_label(candidate) in normalized
        for candidate in (
            "权益投资",
            "基金投资",
            "固定收益投资",
            "贵金属投资",
            "金融衍生品投资",
            "买入返售金融资产",
        )
    )


def _is_detail_or_geography_row(label: str) -> bool:
    """判断行标签是否为明细、国家/地区等非组合层级行。

    Args:
        label: primary row label。

    Returns:
        是明细或地理分类行时返回 ``True``。

    Raises:
        无显式抛出。
    """

    normalized = _normalize_for_label(label)
    return any(
        _normalize_for_label(candidate) in normalized
        for candidate in (
            "国家",
            "地区",
            "美国",
            "行业",
            "明细",
            "前十名",
            "券种",
            "第二层次",
            "第三层次",
        )
    )


def _is_comparable_row_index(value: object) -> bool:
    """判断 row_index 是否可用于表内顺序比较。

    Args:
        value: row_index 值。

    Returns:
        整数且非 bool 时返回 ``True``；整数 gaps 仍可比较。

    Raises:
        无显式抛出。
    """

    return isinstance(value, int) and not isinstance(value, bool)


def _enrich_text_span_semantic_contexts(
    bundle: RepositoryReferenceBundle,
) -> RepositoryReferenceBundle:
    """为 legacy/raw 文本 span 派生规范语义上下文。

    Args:
        bundle: 引用 bundle。

    Returns:
        带文本语义上下文的引用 bundle。

    Raises:
        无显式抛出。
    """

    if not bundle.text_spans:
        return bundle
    return replace(
        bundle,
        text_spans=tuple(
            replace(span, semantic_context_label=_derive_text_semantic_context(span))
            for span in bundle.text_spans
        ),
    )


def _derive_text_semantic_context(
    span: RepositoryReferenceTextSpan,
) -> TextSemanticContext:
    """从已加载文本局部标签派生规范语义上下文。

    Args:
        span: 文本引用。

    Returns:
        ``benchmark``、``investment_objective`` 或 ``unknown``。

    Raises:
        无显式抛出。
    """

    if span.section_id != "§2":
        return "unknown"

    context_values = (span.context_label,) if span.context_label else ()
    context_benchmark = _has_local_benchmark_label(context_values)
    context_objective = _has_local_investment_objective_label(context_values)
    heading_benchmark = _has_local_benchmark_label(span.heading_path)
    heading_objective = _has_local_investment_objective_label(span.heading_path)
    raw_benchmark = _raw_text_has_local_label(span.raw_text, _BENCHMARK_CONTEXT_LABELS)
    raw_objective = _raw_text_has_local_label(span.raw_text, _INVESTMENT_OBJECTIVE_LABELS)

    if context_benchmark and context_objective:
        return "unknown"
    if context_objective:
        return "investment_objective"
    if context_benchmark:
        if heading_objective or raw_objective:
            return "unknown"
        return "benchmark"

    if heading_benchmark and heading_objective:
        return "unknown"
    if heading_objective:
        return "investment_objective"
    if heading_benchmark:
        if raw_objective:
            return "unknown"
        return "benchmark"

    if raw_benchmark and raw_objective:
        return "unknown"
    if raw_objective:
        return "investment_objective"
    if raw_benchmark:
        return "benchmark"
    return "unknown"


_BENCHMARK_CONTEXT_LABELS = ("业绩比较基准", "比较基准", "业绩基准")
_INVESTMENT_OBJECTIVE_LABELS = ("投资目标", "投资目的")


def _has_local_benchmark_label(values: tuple[str, ...]) -> bool:
    """判断文本集合是否含 benchmark 局部标签。

    Args:
        values: 标签集合。

    Returns:
        含 benchmark 标签时返回 ``True``。

    Raises:
        无显式抛出。
    """

    return _contains_any(values, _BENCHMARK_CONTEXT_LABELS)


def _has_local_investment_objective_label(values: tuple[str, ...]) -> bool:
    """判断文本集合是否含投资目标局部标签。

    Args:
        values: 标签集合。

    Returns:
        含投资目标标签时返回 ``True``。

    Raises:
        无显式抛出。
    """

    return _contains_any(values, _INVESTMENT_OBJECTIVE_LABELS)


def _raw_text_has_local_label(text: str, labels: tuple[str, ...]) -> bool:
    """判断 raw text 是否以局部标签前缀开头。

    Args:
        text: 原始文本。
        labels: 可接受标签。

    Returns:
        以 ``label + delimiter/end`` 开头时返回 ``True``。

    Raises:
        无显式抛出。
    """

    normalized_text = normalize_text(text).normalized_text.lower().lstrip()
    if not normalized_text:
        return False
    for label in labels:
        normalized_label = normalize_text(label).normalized_text.lower()
        if not normalized_text.startswith(normalized_label):
            continue
        suffix = normalized_text[len(normalized_label) :]
        if not suffix:
            return True
        if suffix[0] in (":", "：", "|", "｜") or suffix[0].isspace():
            return True
    return False


def _classify_table_family(cells: tuple[RepositoryReferenceCell, ...]) -> TableFamily:
    """按已加载表格上下文确定候选表族。

    Args:
        cells: 同一 table identity 下的单元格。

    Returns:
        表族标签。

    Raises:
        无显式抛出。
    """

    if not cells:
        return "unknown"
    section_ids = tuple(sorted({cell.section_id for cell in cells}))
    priority_signals = (
        _signal_text(section_ids),
        _signal_text(tuple(item for cell in cells for item in cell.table_title_path)),
        _signal_text(tuple(item for cell in cells for item in cell.heading_path)),
        _signal_text(tuple(item for cell in cells for item in cell.table_context)),
        _signal_text(
            tuple(
                item
                for cell in cells
                for item in cell.row_label_path + cell.row_hierarchy_path
            )
        ),
        _signal_text(
            tuple(
                item
                for cell in cells
                for item in cell.column_header_path + cell.column_header_band_path
            )
        ),
    )
    for signal in priority_signals:
        families = _families_for_signal(section_ids, signal)
        selected = _resolve_table_family_conflict(families, signal)
        if selected != "unknown":
            return selected
    return "unknown"


def _signal_text(values: tuple[str, ...]) -> str:
    """把多个标签归一化成单段分类信号。

    Args:
        values: 原始标签。

    Returns:
        归一化信号。

    Raises:
        无显式抛出。
    """

    return _normalize_for_label(" ".join(values))


def _families_for_signal(
    section_ids: tuple[str, ...],
    signal: str,
) -> tuple[TableFamily, ...]:
    """返回单个优先级信号支持的表族。

    Args:
        section_ids: 表格章节集合。
        signal: 归一化信号文本。

    Returns:
        表族 tuple。

    Raises:
        无显式抛出。
    """

    if not signal:
        return ()
    families: list[TableFamily] = []
    if _signal_has_any(signal, ("公允价值层次", "第一层次", "第二层次", "第三层次")):
        families.append("fair_value_hierarchy_table")
    if "§7" in section_ids and _signal_has_any(
        signal,
        ("销售服务费", "管理人报酬", "托管费", "费用"),
    ):
        families.append("expense_fee_table")
    if "§10" in section_ids and _signal_has_any(
        signal,
        ("基金经理持有", "管理人持有", "本基金基金经理持有本开放式基金"),
    ):
        families.append("manager_holding_table")
    if "§8" in section_ids and _signal_has_any(
        signal,
        ("基金资产组合", "期末基金资产组合", "报告期末基金资产组合", "固定收益投资", "权益投资", "其中:股票", "其中：股票"),
    ):
        families.append("portfolio_asset_composition_table")
    if _signal_has_any(signal, ("资产负债表", "利润表", "所有者权益", "现金流量表")):
        families.append("financial_statement_table")
    if _signal_has_any(
        signal,
        ("前十名", "明细", "行业分类", "地区", "国家", "券种", "股票投资明细"),
    ):
        families.append("holding_detail_table")
    if "§2" in section_ids and _signal_has_any(signal, ("基金概况", "基金简介", "基本信息")):
        families.append("fund_profile_table")
    if _signal_has_any(signal, ("业绩比较基准",)):
        families.append("benchmark_context_table")
    return tuple(families)


def _resolve_table_family_conflict(
    families: tuple[TableFamily, ...],
    signal: str,
) -> TableFamily:
    """解析同优先级表族冲突。

    Args:
        families: 候选表族。
        signal: 归一化信号。

    Returns:
        表族标签。

    Raises:
        无显式抛出。
    """

    unique = tuple(dict.fromkeys(families))
    if not unique:
        return "unknown"
    if "fair_value_hierarchy_table" in unique:
        return "fair_value_hierarchy_table"
    if len(unique) == 1:
        return unique[0]
    if "portfolio_asset_composition_table" in unique and _signal_has_any(
        signal,
        ("报告期末基金资产组合", "期末基金资产组合", "基金资产组合"),
    ):
        return "portfolio_asset_composition_table"
    return "unknown"


def _signal_has_any(signal: str, needles: tuple[str, ...]) -> bool:
    """判断归一化信号是否包含任一片段。

    Args:
        signal: 已归一化信号。
        needles: 原始片段。

    Returns:
        包含时返回 ``True``。

    Raises:
        无显式抛出。
    """

    return any(_normalize_for_label(needle) in signal for needle in needles)


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


def _coerce_literal(
    value: object,
    allowed_values: tuple[_LiteralT, ...],
    default: _LiteralT,
) -> _LiteralT:
    """把 JSON-like 值转换为受限 literal。

    Args:
        value: 原始值。
        allowed_values: 允许值集合。
        default: 缺失或非法时的默认值。

    Returns:
        受限 literal 值。

    Raises:
        无显式抛出。
    """

    if value is None:
        return default
    candidate = str(value)
    for allowed in allowed_values:
        if candidate == allowed:
            return allowed
    return default


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
