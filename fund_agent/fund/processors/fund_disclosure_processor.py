"""FundDisclosureDocument 中间态 processor（S4 skeleton）。

本 processor 只做：注册、身份校验、S3 admission 判定消费、fail-closed extract。
字段族提取在 FundDisclosureDocument schema gate 完成前全部返回 missing。
不读取 FundDocumentRepository、PDF/cache/source helper、Docling、network、
provider、LLM、Service/UI/Host、renderer 或 quality gate。
"""

from __future__ import annotations

from typing import Final

from fund_agent.fund.processors.contracts import (
    FundDisclosureDocumentIntermediate,
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

        field_families = tuple(
            _missing_field_family(family_id, source_provenance) for family_id in _FAMILY_ORDER
        )
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
