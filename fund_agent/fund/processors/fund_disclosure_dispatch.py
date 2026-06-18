"""FundDisclosureDocument 中间态 admission helper。

本模块只做 Processor/Extractor 边界前的纯契约判定，见模板第 1-6 章字段族入口。
它不读取 `FundDocumentRepository`、PDF/cache/source helper、Docling、network、
provider、LLM、Service/UI/Host、renderer 或 quality gate，也不实现 fallback、
具体 processor 或生产 facade 接入。
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

from fund_agent.fund.processors.contracts import (
    AnnualReportSourceFailureCategory,
    FundDisclosureDocumentIntermediate,
    FundExtractionGapCode,
    FundExtractionSourceBoundary,
    FundProcessorContractStatus,
    FundProcessorDispatchKey,
)

FAILURE_CLASS_ADMISSION_MAP: Final[
    dict[
        AnnualReportSourceFailureCategory,
        tuple[
            FundExtractionGapCode,
            FundExtractionSourceBoundary,
            FundProcessorContractStatus,
        ],
    ]
] = {
    "not_found": (
        "unsupported_intermediate",
        "unsupported_intermediate",
        "unsupported",
    ),
    "unavailable": (
        "unsupported_intermediate",
        "unsupported_intermediate",
        "unsupported",
    ),
    "schema_drift": (
        "candidate_boundary_blocked",
        "candidate_only",
        "blocked",
    ),
    "identity_mismatch": (
        "candidate_boundary_blocked",
        "candidate_only",
        "blocked",
    ),
    "integrity_error": (
        "candidate_boundary_blocked",
        "candidate_only",
        "blocked",
    ),
}


@dataclass(frozen=True, slots=True)
class DisclosureAdmissionDecision:
    """FundDisclosureDocument 中间态 admission 判定结果。

    Args:
        无。

    Attributes:
        admitted: 当前中间态是否通过 admission helper 的最低边界检查。
        gap_code: 阻断或 unsupported 时对应的 processor gap code。
        source_boundary: 阻断或 unsupported 时对应的来源边界。
        contract_status: admission 层面的 processor 契约状态。

    Raises:
        无显式抛出。
    """

    admitted: bool
    gap_code: FundExtractionGapCode | None
    source_boundary: FundExtractionSourceBoundary | None
    contract_status: FundProcessorContractStatus


def admit_disclosure_intermediate(
    intermediate: FundDisclosureDocumentIntermediate,
    dispatch_key: FundProcessorDispatchKey,
) -> DisclosureAdmissionDecision:
    """判定受控文档表示是否可进入后续 processor 投影。

    Args:
        intermediate: `FundDisclosureDocument`-like 受控中间态。
        dispatch_key: Processor 路由键；S3 只保留显式参数边界，不执行 registry 解析。

    Returns:
        admission 判定结果。

    Raises:
        KeyError: 当 `failure_class` 不是标准五类来源失败分类时抛出。
    """

    _ = dispatch_key
    if intermediate.failure_class is not None:
        gap_code, source_boundary, contract_status = FAILURE_CLASS_ADMISSION_MAP[
            intermediate.failure_class
        ]
        return DisclosureAdmissionDecision(
            admitted=False,
            gap_code=gap_code,
            source_boundary=source_boundary,
            contract_status=contract_status,
        )
    if intermediate.source_provenance is None:
        return DisclosureAdmissionDecision(
            admitted=False,
            gap_code="source_provenance_unsafe",
            source_boundary="source_provenance_unsafe",
            contract_status="blocked",
        )
    if intermediate.candidate_boundary is not None:
        return DisclosureAdmissionDecision(
            admitted=True,
            gap_code="candidate_boundary_blocked",
            source_boundary="candidate_only",
            contract_status="blocked",
        )
    return DisclosureAdmissionDecision(
        admitted=True,
        gap_code=None,
        source_boundary=None,
        contract_status="satisfied",
    )
