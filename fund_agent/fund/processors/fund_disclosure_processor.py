"""FundDisclosureDocument 中间态 processor（S4 skeleton）。

本 processor 只做：注册、身份校验、S3 admission 判定消费、fail-closed extract。
字段族提取在 FundDisclosureDocument schema gate 完成前全部返回 missing。
不读取 FundDocumentRepository、PDF/cache/source helper、Docling、network、
provider、LLM、Service/UI/Host、renderer 或 quality gate。
"""

from __future__ import annotations

from typing import Final

from fund_agent.fund.processors.contracts import (
    FundCandidateEvidenceRecord,
    FundDisclosureDocumentContentIntermediate,
    FundDisclosureDocumentIntermediate,
    FundDisclosureTableBlockLike,
    FundExtractionGap,
    FundExtractionGapCode,
    FundExtractionSourceBoundary,
    FundFieldFamilyId,
    FundFieldFamilyResult,
    FundProcessorContractStatus,
    FundProcessorDispatchKey,
    FundProcessorInput,
    FundProcessorResult,
)
from fund_agent.fund.processors.fund_disclosure_dispatch import (
    admit_disclosure_intermediate,
)
from fund_agent.fund.source_provenance import PublicSourceProvenance

_OUTPUT_SCHEMA_VERSION: Final[str] = "fund_processor_result.v1"

_FAMILY_ORDER: Final[tuple[FundFieldFamilyId, ...]] = (
    "product_essence.v1",
    "return_attribution.v1",
    "manager_profile.v1",
    "investor_experience.v1",
    "current_stage.v1",
    "core_risk.v1",
)

_CHAPTER_IDS: Final[dict[FundFieldFamilyId, tuple[int, ...]]] = {
    "product_essence.v1": (1,),
    "return_attribution.v1": (2,),
    "manager_profile.v1": (3,),
    "investor_experience.v1": (4,),
    "current_stage.v1": (5,),
    "core_risk.v1": (6,),
}

_PRODUCT_ESSENCE_CANDIDATE_LIMIT: Final[int] = 12
_CANDIDATE_EXCERPT_LIMIT: Final[int] = 160
_PRODUCT_ESSENCE_MATCH_GROUPS: Final[tuple[tuple[str, tuple[str, ...]], ...]] = (
    (
        "product_identity",
        ("基金简介", "基金基本情况", "产品概况", "基金产品资料概要", "基金名称", "基金代码"),
    ),
    ("investment_scope", ("投资目标", "投资范围", "投资策略")),
    ("benchmark", ("业绩比较基准", "比较基准")),
    ("risk_characteristic", ("风险收益特征", "风险特征")),
)


class FundDisclosureDocumentProcessor:
    """FundDisclosureDocument 中间态 processor（S4 skeleton）。

    本 processor 只支持 active_fund + annual_report + fund_disclosure_document.v1，
    在 FundDisclosureDocument schema gate 完成前所有字段族返回 missing。
    不声明 source truth、parser replacement、candidate proof、readiness 或 release。
    """

    processor_id: Final[str] = "fund_disclosure_document.fund_disclosure_document.v1"
    priority: Final[int] = 50
    output_schema_version: Final[str] = _OUTPUT_SCHEMA_VERSION

    def supports(self, context: FundProcessorDispatchKey) -> bool:
        """判断是否支持当前 dispatch key。

        Args:
            context: Processor 路由键。

        Returns:
            仅在主动基金年报 FundDisclosureDocument 中间态返回 True。

        Raises:
            无显式抛出。
        """

        return (
            context.fund_type == "active_fund"
            and context.report_type == "annual_report"
            and context.intermediate_kind == "fund_disclosure_document.v1"
            and context.processor_goal == "template_chapters_1_6_minimum_field_families"
        )

    def extract(self, input_data: FundProcessorInput) -> FundProcessorResult:
        """执行 admission 判定与 identity 校验；字段抽取 deferred 到 schema gate。

        Args:
            input_data: Processor 输入契约。

        Returns:
            Processor 输出结果；当前所有字段族为 missing。

        Raises:
            无显式抛出；所有异常路径转为 fail-closed result。
        """

        context = input_data.context

        if not self.supports(context):
            gap_code, source_boundary = _unsupported_block_details(context)
            return _blocked_result(
                self.processor_id,
                context,
                gap_code=gap_code,
                message="FundDisclosureDocumentProcessor 不支持当前 dispatch key",
                source_boundary=source_boundary,
            )

        intermediate = input_data.intermediate
        if not isinstance(intermediate, FundDisclosureDocumentIntermediate):
            return _blocked_result(
                self.processor_id,
                context,
                gap_code="input_type_mismatch",
                message="FundDisclosureDocumentProcessor 只接受 FundDisclosureDocumentIntermediate",
                source_boundary="unsupported_intermediate",
            )

        identity_blocked = _check_identity(context, intermediate)
        if identity_blocked is not None:
            return identity_blocked

        try:
            admission = admit_disclosure_intermediate(intermediate, context)
        except KeyError:
            return _blocked_result(
                self.processor_id,
                context,
                gap_code="unsupported_intermediate",
                message=(
                    f"admission helper 无法识别 failure_class：{intermediate.failure_class}；"
                    "标准五类来源失败分类之外的非法值"
                ),
                source_boundary="unsupported_intermediate",
            )

        source_provenance = intermediate.source_provenance
        candidate_boundary = intermediate.candidate_boundary

        if not admission.admitted:
            return FundProcessorResult(
                processor_id=self.processor_id,
                output_schema_version=self.output_schema_version,
                fund_code=context.fund_code,
                report_year=context.document_year,
                fund_type=context.fund_type,
                report_type=context.report_type,
                input_intermediate_kind=context.intermediate_kind,
                field_families=(),
                gaps=(
                    FundExtractionGap(
                        gap_code=admission.gap_code,  # type: ignore[arg-type]
                        message=f"admission 拒绝：gap_code={admission.gap_code}",
                        field_family_id=None,
                        source_field_path=None,
                        source_boundary=admission.source_boundary,  # type: ignore[arg-type]
                        required=True,
                    ),
                ),
                anchors=(),
                source_provenance=source_provenance,
                candidate_boundary=candidate_boundary,
                contract_status=admission.contract_status,
            )

        field_families = _field_families_for_intermediate(intermediate, source_provenance)
        contract_status: FundProcessorContractStatus = (
            "blocked" if admission.contract_status == "blocked" else "missing"
        )
        return FundProcessorResult(
            processor_id=self.processor_id,
            output_schema_version=self.output_schema_version,
            fund_code=context.fund_code,
            report_year=context.document_year,
            fund_type=context.fund_type,
            report_type=context.report_type,
            input_intermediate_kind=context.intermediate_kind,
            field_families=field_families,
            gaps=(),
            anchors=(),
            source_provenance=source_provenance,
            candidate_boundary=candidate_boundary,
            contract_status=contract_status,
        )


def _check_identity(
    context: FundProcessorDispatchKey,
    intermediate: FundDisclosureDocumentIntermediate,
) -> FundProcessorResult | None:
    """校验 dispatch key 与 intermediate 身份一致性。

    Args:
        context: Processor 路由键。
        intermediate: 受控文档表示中间态。

    Returns:
        身份不一致时返回 blocked result（contract_status 固定为 "blocked"）；
        一致时返回 None。

    Raises:
        无显式抛出。
    """

    if intermediate.intermediate_kind != context.intermediate_kind:
        return _blocked_result(
            processor_id="fund_disclosure_document.fund_disclosure_document.v1",
            context=context,
            gap_code="input_type_mismatch",
            message=(
                f"intermediate_kind 不匹配："
                f"intermediate={intermediate.intermediate_kind} "
                f"dispatch={context.intermediate_kind}"
            ),
            source_boundary="unsupported_intermediate",
            contract_status="blocked",
        )
    if intermediate.document_kind != context.report_type:
        return _blocked_result(
            processor_id="fund_disclosure_document.fund_disclosure_document.v1",
            context=context,
            gap_code="unsupported_report_type",
            message=(
                f"document_kind 不匹配："
                f"intermediate={intermediate.document_kind} "
                f"dispatch={context.report_type}"
            ),
            source_boundary="unsupported_report_type",
            contract_status="blocked",
        )
    if intermediate.fund_code != context.fund_code:
        return _blocked_result(
            processor_id="fund_disclosure_document.fund_disclosure_document.v1",
            context=context,
            gap_code="unsupported_intermediate",
            message=(
                f"fund_code 不匹配："
                f"intermediate={intermediate.fund_code} "
                f"dispatch={context.fund_code}"
            ),
            source_boundary="unsupported_intermediate",
            contract_status="blocked",
        )
    if intermediate.report_year != context.document_year:
        return _blocked_result(
            processor_id="fund_disclosure_document.fund_disclosure_document.v1",
            context=context,
            gap_code="unsupported_intermediate",
            message=(
                f"report_year 不匹配："
                f"intermediate={intermediate.report_year} "
                f"dispatch={context.document_year}"
            ),
            source_boundary="unsupported_intermediate",
            contract_status="blocked",
        )
    return None


def _field_families_for_intermediate(
    intermediate: FundDisclosureDocumentIntermediate,
    source_provenance: PublicSourceProvenance | None,
) -> tuple[FundFieldFamilyResult, ...]:
    """构造 FundDisclosureDocument processor 字段族结果。

    Args:
        intermediate: 已通过身份校验和 admission 的中间态。
        source_provenance: 公共来源 provenance。

    Returns:
        六个字段族结果；S6-B 仅为 ``product_essence.v1`` 附加 candidate evidence。

    Raises:
        无显式抛出。
    """

    product_essence_evidence = _select_product_essence_candidate_evidence(intermediate)
    return tuple(
        _candidate_missing_field_family(family_id, source_provenance, product_essence_evidence)
        if family_id == "product_essence.v1" and product_essence_evidence
        else _missing_field_family(family_id, source_provenance)
        for family_id in _FAMILY_ORDER
    )


def _select_product_essence_candidate_evidence(
    intermediate: FundDisclosureDocumentIntermediate,
) -> tuple[FundCandidateEvidenceRecord, ...]:
    """选择产品本质字段族的 candidate-only locator evidence。

    Args:
        intermediate: FundDisclosureDocument-like 中间态。

    Returns:
        按 S6-B mapping table 排序和限量后的候选证据记录。

    Raises:
        无显式抛出。
    """

    if not isinstance(intermediate, FundDisclosureDocumentContentIntermediate):
        return ()

    records: list[FundCandidateEvidenceRecord] = []
    seen_paths: set[str] = set()
    for role, tokens in _PRODUCT_ESSENCE_MATCH_GROUPS:
        _extend_product_essence_section_records(records, seen_paths, intermediate, role, tokens)
        _extend_product_essence_paragraph_records(records, seen_paths, intermediate, role, tokens)
        _extend_product_essence_table_records(records, seen_paths, intermediate, role, tokens)
        if len(records) >= _PRODUCT_ESSENCE_CANDIDATE_LIMIT:
            break
    return tuple(records[:_PRODUCT_ESSENCE_CANDIDATE_LIMIT])


def _extend_product_essence_section_records(
    records: list[FundCandidateEvidenceRecord],
    seen_paths: set[str],
    intermediate: FundDisclosureDocumentContentIntermediate,
    role: str,
    tokens: tuple[str, ...],
) -> None:
    """追加 section locator candidate evidence。

    Args:
        records: 待追加的记录列表。
        seen_paths: 已使用的 source path。
        intermediate: 带正文结构的中间态。
        role: 命中的 evidence role。
        tokens: 当前 role 的匹配 token。

    Returns:
        无返回值。

    Raises:
        无显式抛出。
    """

    for index, section in enumerate(intermediate.sections):
        path = f"sections[{index}]"
        texts = (
            section.heading_text_normalized,
            section.heading_text_raw,
            *_tuple_text(section.heading_path),
        )
        if path in seen_paths or not _matches_any_token(texts, tokens):
            continue
        seen_paths.add(path)
        records.append(
            FundCandidateEvidenceRecord(
                field_family_id="product_essence.v1",
                source_boundary="candidate_only",
                source_field_path=path,
                section_id=section.section_id,
                table_id=None,
                block_id=None,
                cell_id=None,
                heading_path=section.heading_path,
                row_locator=f"role={role}; locator=section_id={section.section_id}",
                excerpt=_truncate(_first_non_empty(texts)),
                locator_stability=section.locator_stability,
            )
        )


def _extend_product_essence_paragraph_records(
    records: list[FundCandidateEvidenceRecord],
    seen_paths: set[str],
    intermediate: FundDisclosureDocumentContentIntermediate,
    role: str,
    tokens: tuple[str, ...],
) -> None:
    """追加 paragraph block candidate evidence。

    Args:
        records: 待追加的记录列表。
        seen_paths: 已使用的 source path。
        intermediate: 带正文结构的中间态。
        role: 命中的 evidence role。
        tokens: 当前 role 的匹配 token。

    Returns:
        无返回值。

    Raises:
        无显式抛出。
    """

    for index, paragraph in enumerate(intermediate.paragraph_blocks):
        path = f"paragraph_blocks[{index}]"
        texts = (
            paragraph.text_normalized,
            paragraph.text_raw,
            *_tuple_text(paragraph.heading_path),
        )
        if path in seen_paths or not _matches_any_token(texts, tokens):
            continue
        seen_paths.add(path)
        records.append(
            FundCandidateEvidenceRecord(
                field_family_id="product_essence.v1",
                source_boundary="candidate_only",
                source_field_path=path,
                section_id=paragraph.section_id,
                table_id=None,
                block_id=paragraph.block_id,
                cell_id=None,
                heading_path=paragraph.heading_path,
                row_locator=f"role={role}; locator=block_id={paragraph.block_id}",
                excerpt=_truncate(_first_non_empty((paragraph.text_normalized, paragraph.text_raw))),
                locator_stability=paragraph.locator_stability,
            )
        )


def _extend_product_essence_table_records(
    records: list[FundCandidateEvidenceRecord],
    seen_paths: set[str],
    intermediate: FundDisclosureDocumentContentIntermediate,
    role: str,
    tokens: tuple[str, ...],
) -> None:
    """追加 table 和 cell candidate evidence。

    Args:
        records: 待追加的记录列表。
        seen_paths: 已使用的 source path。
        intermediate: 带正文结构的中间态。
        role: 命中的 evidence role。
        tokens: 当前 role 的匹配 token。

    Returns:
        无返回值。

    Raises:
        无显式抛出。
    """

    for table_index, table in enumerate(intermediate.table_blocks):
        path = f"table_blocks[{table_index}]"
        texts = (
            table.heading_text,
            table.table_caption_or_nearby_heading,
            *_tuple_text(table.heading_path),
        )
        if path not in seen_paths and _matches_any_token(texts, tokens):
            seen_paths.add(path)
            records.append(
                FundCandidateEvidenceRecord(
                    field_family_id="product_essence.v1",
                    source_boundary="candidate_only",
                    source_field_path=path,
                    section_id=table.section_id,
                    table_id=table.table_id,
                    block_id=None,
                    cell_id=None,
                    heading_path=table.heading_path,
                    row_locator=f"role={role}; locator=table_id={table.table_id}",
                    excerpt=_truncate(_first_non_empty(texts)),
                    locator_stability=table.locator_stability,
                )
            )
        _extend_product_essence_cell_records(records, seen_paths, table_index, table, role, tokens)


def _extend_product_essence_cell_records(
    records: list[FundCandidateEvidenceRecord],
    seen_paths: set[str],
    table_index: int,
    table: FundDisclosureTableBlockLike,
    role: str,
    tokens: tuple[str, ...],
) -> None:
    """追加 table cell candidate evidence。

    Args:
        records: 待追加的记录列表。
        seen_paths: 已使用的 source path。
        table_index: table tuple 中的原始索引。
        table: table block 结构协议对象。
        role: 命中的 evidence role。
        tokens: 当前 role 的匹配 token。

    Returns:
        无返回值。

    Raises:
        无显式抛出。
    """

    indexed_cells = sorted(
        enumerate(table.cells), key=lambda item: (item[1].row_index, item[1].column_index)
    )
    for cell_index, cell in indexed_cells:
        path = f"table_blocks[{table_index}].cells[{cell_index}]"
        texts = (
            cell.cell_text_normalized,
            cell.cell_text,
            *_tuple_text(cell.row_label_path),
            *_tuple_text(cell.column_header_path),
            *_tuple_text(cell.heading_path),
        )
        if path in seen_paths or not _matches_any_token(texts, tokens):
            continue
        seen_paths.add(path)
        row_locator = (
            f"role={role}; locator=table_id={cell.table_id}; "
            f"row={cell.row_index}; column={cell.column_index}"
        )
        records.append(
            FundCandidateEvidenceRecord(
                field_family_id="product_essence.v1",
                source_boundary="candidate_only",
                source_field_path=path,
                section_id=cell.section_anchor,
                table_id=cell.table_id,
                block_id=None,
                cell_id=cell.cell_id,
                heading_path=cell.heading_path,
                row_locator=row_locator,
                excerpt=_truncate(_first_non_empty((cell.cell_text_normalized, cell.cell_text))),
                locator_stability=cell.locator_stability,
            )
        )


def _candidate_missing_field_family(
    family_id: FundFieldFamilyId,
    source_provenance: PublicSourceProvenance | None,
    candidate_evidence: tuple[FundCandidateEvidenceRecord, ...],
) -> FundFieldFamilyResult:
    """构造带 candidate evidence 的 public-missing 字段族。

    Args:
        family_id: 字段族 ID。
        source_provenance: 公共来源 provenance。
        candidate_evidence: candidate-only 证据记录。

    Returns:
        public status 仍为 missing 的字段族结果。

    Raises:
        无显式抛出。
    """

    return FundFieldFamilyResult(
        field_family_id=family_id,
        chapter_ids=_CHAPTER_IDS[family_id],
        value={},
        status="missing",
        extraction_mode="missing",
        anchors=(),
        gaps=(
            FundExtractionGap(
                gap_code="candidate_only_not_source_truth",
                message=(
                    f"{family_id} 仅存在 candidate-only locator evidence；"
                    "未证明 source truth 或字段正确性"
                ),
                field_family_id=family_id,
                source_field_path=None,
                source_boundary="candidate_only",
                required=True,
            ),
        ),
        source_provenance=source_provenance,
        candidate_evidence=candidate_evidence,
    )


def _missing_field_family(
    family_id: FundFieldFamilyId,
    source_provenance: PublicSourceProvenance | None,
) -> FundFieldFamilyResult:
    """构造全缺字段族结果。

    Args:
        family_id: 字段族 ID。
        source_provenance: 公共来源 provenance。

    Returns:
        status="missing" 的字段族结果。

    Raises:
        无显式抛出。
    """

    return FundFieldFamilyResult(
        field_family_id=family_id,
        chapter_ids=_CHAPTER_IDS[family_id],
        value={},
        status="missing",
        extraction_mode="missing",
        anchors=(),
        gaps=(
            FundExtractionGap(
                gap_code="field_family_missing",
                message=(
                    f"{family_id} 字段抽取未实现："
                    "FundDisclosureDocument schema gate 完成前全部返回 missing"
                ),
                field_family_id=family_id,
                source_field_path=None,
                source_boundary="unsupported_intermediate",
                required=True,
            ),
        ),
        source_provenance=source_provenance,
    )


def _matches_any_token(texts: tuple[str | None, ...], tokens: tuple[str, ...]) -> bool:
    """判断文本集合是否命中任一 token。

    Args:
        texts: 候选文本集合。
        tokens: 匹配 token。

    Returns:
        任一文本包含任一 token 时返回 True。

    Raises:
        无显式抛出。
    """

    normalized_tokens = tuple(_normalize_match_text(token) for token in tokens)
    return any(
        token and token in _normalize_match_text(text)
        for text in texts
        for token in normalized_tokens
    )


def _normalize_match_text(text: str | None) -> str:
    """规范化用于 token matching 的文本。

    Args:
        text: 原始文本或 None。

    Returns:
        去除常见空白后的文本。

    Raises:
        无显式抛出。
    """

    if text is None:
        return ""
    return "".join(str(text).split()).replace("\u3000", "")


def _first_non_empty(texts: tuple[str | None, ...]) -> str:
    """返回第一个非空文本。

    Args:
        texts: 候选文本集合。

    Returns:
        第一个非空文本；全部为空时返回固定占位。

    Raises:
        无显式抛出。
    """

    for text in texts:
        if text:
            return text
    return "candidate evidence"


def _truncate(text: str) -> str:
    """截断 candidate excerpt。

    Args:
        text: 原始摘录。

    Returns:
        最长 160 字符的摘录。

    Raises:
        无显式抛出。
    """

    return text[:_CANDIDATE_EXCERPT_LIMIT]


def _tuple_text(values: tuple[str, ...]) -> tuple[str, ...]:
    """返回字符串 tuple，供类型检查和展开使用。

    Args:
        values: 字符串 tuple。

    Returns:
        原值。

    Raises:
        无显式抛出。
    """

    return values


def _unsupported_block_details(
    context: FundProcessorDispatchKey,
) -> tuple[FundExtractionGapCode, FundExtractionSourceBoundary]:
    """按 dispatch key 不匹配维度选择 fail-closed gap 归因。

    Args:
        context: Processor 路由键。

    Returns:
        跨字段缺口码与 source boundary。

    Raises:
        无显式抛出。
    """

    if context.fund_type != "active_fund":
        return "unsupported_fund_type", "unsupported_fund_type"
    if context.report_type != "annual_report":
        return "unsupported_report_type", "unsupported_report_type"
    if context.intermediate_kind != "fund_disclosure_document.v1":
        return "unsupported_intermediate_kind", "unsupported_intermediate"
    if context.processor_goal != "template_chapters_1_6_minimum_field_families":
        return "unsupported_processor_goal", "unsupported_processor_goal"
    return "unsupported_processor", "unsupported_intermediate"


def _blocked_result(
    processor_id: str,
    context: FundProcessorDispatchKey,
    *,
    gap_code: FundExtractionGapCode,
    message: str,
    source_boundary: FundExtractionSourceBoundary,
    contract_status: FundProcessorContractStatus | None = None,
) -> FundProcessorResult:
    """构造跨字段 fail-closed processor 结果。

    Args:
        processor_id: 当前 processor ID。
        context: Processor 路由键。
        gap_code: 跨字段缺口码。
        message: 缺口说明。
        source_boundary: 跨字段缺口来源边界。
        contract_status: 显式契约状态；缺省时从 gap_code 前缀自动推导。

    Returns:
        unsupported 或 blocked 状态结果。

    Raises:
        无显式抛出。
    """

    if contract_status is None:
        contract_status = "unsupported" if gap_code.startswith("unsupported_") else "blocked"
    return FundProcessorResult(
        processor_id=processor_id,
        output_schema_version=_OUTPUT_SCHEMA_VERSION,
        fund_code=context.fund_code,
        report_year=context.document_year,
        fund_type=context.fund_type,
        report_type=context.report_type,
        input_intermediate_kind=context.intermediate_kind,
        field_families=(),
        gaps=(
            FundExtractionGap(
                gap_code=gap_code,
                message=message,
                field_family_id=None,
                source_field_path=None,
                source_boundary=source_boundary,
                required=True,
            ),
        ),
        anchors=(),
        source_provenance=None,
        candidate_boundary=None,
        contract_status=contract_status,
    )
