"""Evidence Confirm 生产集成摘要，见基金分析模板第 0-7 章。

本模块属于 Agent 层基金能力，只把 repository-bounded Evidence Confirm 结果压缩为
Service / quality gate 可消费的安全摘要。摘要不携带原文 excerpt、PDF/cache 路径、
parser JSON、source adapter 对象或 provider 结果。
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Literal, TypeAlias

from fund_agent.fund.evidence_confirm import (
    EvidenceConfirmDimension,
    EvidenceConfirmDimensionResult,
    EvidenceConfirmFactResultV2,
    EvidenceConfirmReference,
)
from fund_agent.fund.evidence_confirm_semantic import EvidenceSemanticResult
from fund_agent.fund.evidence_confirm_sources import EvidenceConfirmRepositoryRunResult

EvidenceConfirmProductionPolicy: TypeAlias = Literal["off", "warn", "block"]
EvidenceConfirmProductionStatus: TypeAlias = Literal["pass", "warn", "fail", "not_run"]
EvidenceConfirmProductionPathwayStatus: TypeAlias = Literal["pass", "fail", "not_run"]
EvidenceConfirmProvenanceTier: TypeAlias = Literal["none", "section", "table", "row", "cell"]
EvidenceConfirmProvenanceStatus: TypeAlias = Literal["pass", "fail", "not_run"]
EvidenceConfirmProductionCheckStatus: TypeAlias = Literal[
    "pass",
    "warn",
    "fail",
    "not_applicable",
    "not_run",
]

SUMMARY_SCHEMA_VERSION: Literal["evidence_confirm_production_summary.v2"] = (
    "evidence_confirm_production_summary.v2"
)
STABLE_NOT_RUN_REASONS: frozenset[str] = frozenset(("not_requested", "policy_off", "invalid_request"))
_PROVENANCE_TIER_ORDER: dict[EvidenceConfirmProvenanceTier, int] = {
    "none": 0,
    "section": 1,
    "table": 2,
    "row": 3,
    "cell": 4,
}


@dataclass(frozen=True, slots=True)
class EvidenceConfirmProductionSummary:
    """Evidence Confirm 生产链路安全摘要。

    Attributes:
        schema_version: 摘要 schema 版本。
        policy: 调用方选择的生产策略。
        status: 聚合状态，按 `fail > warn > pass > not_run/not_applicable` 计算。
        fund_code: 基金代码。
        report_year: 年报年份。
        pathway_status: repository/source/reference materialization 通路状态。
        deterministic_status: strict V2 确定性复核状态。
        semantic_status: semantic companion 状态；缺省为 `not_run`，仅由 injected
            no-live semantic result 改写。
        checked_fact_count: 已复核 fact 数。
        failed_fact_count: 失败 fact 数。
        warning_fact_count: warning fact 数。
        not_applicable_fact_count: 不适用 fact 数。
        issue_count: compact issue 数，不包含原文。
        auditability_score: V2 聚合可审计性分数。
        blocking_issue_ids: 阻断 issue ids。
        warning_issue_ids: 生产可见的非阻断 issue ids，包含 reviewable 与 informational issue。
        not_run_reason: 未运行或失败摘要的稳定原因码。
        provenance_status: repository-bounded claim provenance 聚合状态。
        minimum_provenance_tier: 已检查适用 fact 的最低 provenance tier。
        provenance_missing_fact_count: provenance 缺失 fact 数。
        strict_precision_residual_count: provenance 通过但 strict value_match 失败的 fact 数。
        strict_precision_issue_ids: strict precision residual 对应 issue ids。
    """

    schema_version: Literal["evidence_confirm_production_summary.v2"]
    policy: EvidenceConfirmProductionPolicy
    status: EvidenceConfirmProductionStatus
    fund_code: str
    report_year: int
    pathway_status: EvidenceConfirmProductionPathwayStatus
    deterministic_status: EvidenceConfirmProductionCheckStatus
    semantic_status: EvidenceConfirmProductionCheckStatus
    checked_fact_count: int
    failed_fact_count: int
    warning_fact_count: int
    not_applicable_fact_count: int
    issue_count: int
    auditability_score: int | None
    blocking_issue_ids: tuple[str, ...]
    warning_issue_ids: tuple[str, ...]
    not_run_reason: str | None
    provenance_status: EvidenceConfirmProvenanceStatus = "not_run"
    minimum_provenance_tier: EvidenceConfirmProvenanceTier = "none"
    provenance_missing_fact_count: int = 0
    strict_precision_residual_count: int = 0
    strict_precision_issue_ids: tuple[str, ...] = ()


def summary_from_repository_result(
    result: EvidenceConfirmRepositoryRunResult,
    policy: EvidenceConfirmProductionPolicy,
    *,
    semantic_result: EvidenceSemanticResult | None = None,
) -> EvidenceConfirmProductionSummary:
    """从 repository-bounded Evidence Confirm 结果构造生产摘要。

    该函数不读取文档、不访问 repository，也不因 runner 失败结果抛出异常。失败
    repository 结果会转换为 `status="fail"` 和稳定 `repository_failure:<reason>`。
    可选 semantic result 只接受调用方已生成的 no-live typed 结果；本函数不构造
    provider client。

    Args:
        result: repository-bounded Evidence Confirm 运行结果。
        policy: 调用方选择的生产策略。
        semantic_result: 调用方注入的 no-live semantic companion 结果；缺省保持
            `semantic_status="not_run"`。

    Returns:
        安全生产摘要。

    Raises:
        ValueError: policy 不在 `off / warn / block` 内时抛出。
    """

    _validate_policy(policy)
    _validate_semantic_result_identity(result, semantic_result)
    deterministic_status = _deterministic_status(result)
    pathway_status = _pathway_status(result)
    semantic_status = _semantic_status(semantic_result)
    not_run_reason = _repository_failure_reason(result) if pathway_status == "fail" else None
    blocking_issue_ids = _blocking_issue_ids(result)
    warning_issue_ids = _warning_issue_ids(result)
    provenance_contract = _provenance_contract_from_result(result)
    status = _aggregate_summary_status(
        pathway_status=pathway_status,
        deterministic_status=deterministic_status,
        semantic_status=semantic_status,
    )
    return EvidenceConfirmProductionSummary(
        schema_version=SUMMARY_SCHEMA_VERSION,
        policy=policy,
        status=status,
        fund_code=result.fund_code,
        report_year=result.report_year,
        pathway_status=pathway_status,
        deterministic_status=deterministic_status,
        semantic_status=semantic_status,
        checked_fact_count=_checked_fact_count(result),
        failed_fact_count=_fact_status_count(result, "fail"),
        warning_fact_count=_fact_status_count(result, "warn"),
        not_applicable_fact_count=_fact_status_count(result, "not_applicable"),
        issue_count=_issue_count(result) + _semantic_issue_count(semantic_result),
        auditability_score=(
            result.evidence_confirm_result.auditability_score
            if result.evidence_confirm_result is not None
            else None
        ),
        blocking_issue_ids=blocking_issue_ids,
        warning_issue_ids=warning_issue_ids,
        not_run_reason=not_run_reason,
        provenance_status=provenance_contract.provenance_status,
        minimum_provenance_tier=provenance_contract.minimum_provenance_tier,
        provenance_missing_fact_count=provenance_contract.provenance_missing_fact_count,
        strict_precision_residual_count=provenance_contract.strict_precision_residual_count,
        strict_precision_issue_ids=provenance_contract.strict_precision_issue_ids,
    )


def not_run_evidence_confirm_summary(
    fund_code: str,
    report_year: int,
    policy: EvidenceConfirmProductionPolicy,
    reason: str,
) -> EvidenceConfirmProductionSummary:
    """构造 Evidence Confirm 未运行摘要。

    Args:
        fund_code: 基金代码。
        report_year: 年报年份。
        policy: 调用方选择的生产策略。
        reason: 稳定原因码；EC-P4 Slice 1 支持 `not_requested`、`policy_off`、
            `invalid_request`、`runner_exception:<class_name>` 与
            `repository_failure:<reason>`。

    Returns:
        未运行摘要。

    Raises:
        ValueError: policy 或 reason 非法时抛出。
    """

    _validate_policy(policy)
    _validate_reason(reason)
    return EvidenceConfirmProductionSummary(
        schema_version=SUMMARY_SCHEMA_VERSION,
        policy=policy,
        status="not_run",
        fund_code=fund_code,
        report_year=report_year,
        pathway_status="not_run",
        deterministic_status="not_run",
        semantic_status="not_run",
        checked_fact_count=0,
        failed_fact_count=0,
        warning_fact_count=0,
        not_applicable_fact_count=0,
        issue_count=0,
        auditability_score=None,
        blocking_issue_ids=(),
        warning_issue_ids=(),
        not_run_reason=reason,
        provenance_status="not_run",
        minimum_provenance_tier="none",
        provenance_missing_fact_count=0,
        strict_precision_residual_count=0,
        strict_precision_issue_ids=(),
    )


@dataclass(frozen=True, slots=True)
class _ProvenanceContract:
    """生产摘要中的 provenance v2 聚合结果。

    Attributes:
        provenance_status: claim provenance 聚合状态。
        minimum_provenance_tier: 已检查适用 fact 的最低 provenance tier。
        provenance_missing_fact_count: provenance 缺失 fact 数。
        strict_precision_residual_count: provenance 通过但 value_match 失败 fact 数。
        strict_precision_issue_ids: strict precision residual 对应 issue ids。
    """

    provenance_status: EvidenceConfirmProvenanceStatus
    minimum_provenance_tier: EvidenceConfirmProvenanceTier
    provenance_missing_fact_count: int
    strict_precision_residual_count: int
    strict_precision_issue_ids: tuple[str, ...]


def _aggregate_summary_status(
    *,
    pathway_status: EvidenceConfirmProductionPathwayStatus,
    deterministic_status: EvidenceConfirmProductionCheckStatus,
    semantic_status: EvidenceConfirmProductionCheckStatus,
) -> EvidenceConfirmProductionStatus:
    """按 EC-P4 优先级聚合摘要状态。

    Args:
        pathway_status: repository/source/reference materialization 通路状态。
        deterministic_status: strict V2 确定性复核状态。
        semantic_status: semantic companion 状态。

    Returns:
        聚合生产状态。

    Raises:
        无显式抛出。
    """

    if pathway_status == "fail":
        return "fail"
    statuses = (deterministic_status, semantic_status)
    if "fail" in statuses:
        return "fail"
    if "warn" in statuses:
        return "warn"
    if "pass" in statuses:
        return "pass"
    return "not_run"


def _deterministic_status(
    result: EvidenceConfirmRepositoryRunResult,
) -> EvidenceConfirmProductionCheckStatus:
    """从 runner 结果提取 strict V2 状态。

    Args:
        result: repository-bounded Evidence Confirm 运行结果。

    Returns:
        V2 状态；未运行时返回 `not_run`。

    Raises:
        无显式抛出。
    """

    if result.evidence_confirm_result is None:
        return "not_run"
    return result.evidence_confirm_result.overall_status


def _semantic_status(
    semantic_result: EvidenceSemanticResult | None,
) -> EvidenceConfirmProductionCheckStatus:
    """从 injected semantic result 提取生产摘要状态。

    Args:
        semantic_result: 调用方已生成的 no-live semantic 结果。

    Returns:
        semantic companion 状态；缺省为 `not_run`。

    Raises:
        无显式抛出。
    """

    if semantic_result is None:
        return "not_run"
    if semantic_result.overall_status == "not_applicable":
        return "not_applicable"
    return semantic_result.overall_status


def _semantic_issue_count(semantic_result: EvidenceSemanticResult | None) -> int:
    """统计 semantic companion 生产可见 issue 数。

    Args:
        semantic_result: 调用方已生成的 no-live semantic 结果。

    Returns:
        block/warn semantic claim 数。

    Raises:
        无显式抛出。
    """

    if semantic_result is None:
        return 0
    return sum(
        1
        for claim_result in semantic_result.claim_results
        if claim_result.severity in {"block", "warn"}
    )


def _reference_tier(reference: EvidenceConfirmReference) -> EvidenceConfirmProvenanceTier:
    """计算单条 proven reference 的 provenance tier。

    Args:
        reference: Evidence Confirm 显式引用摘录。

    Returns:
        provenance tier；当前实现不会返回 `cell`。

    Raises:
        无显式抛出。
    """

    if reference.source_truth_status != "proven" or reference.candidate_only:
        return "none"
    if reference.row_locator:
        return "row"
    if reference.table_id:
        return "table"
    if reference.section_id:
        return "section"
    return "none"


def _strongest_tier(
    tiers: Iterable[EvidenceConfirmProvenanceTier],
) -> EvidenceConfirmProvenanceTier:
    """返回 tier 集合中的最强 tier。

    Args:
        tiers: provenance tier 序列。

    Returns:
        最强 tier；空集合返回 `none`。

    Raises:
        无显式抛出。
    """

    strongest: EvidenceConfirmProvenanceTier = "none"
    for tier in tiers:
        if _PROVENANCE_TIER_ORDER[tier] > _PROVENANCE_TIER_ORDER[strongest]:
            strongest = tier
    return strongest


def _weakest_tier(
    tiers: Iterable[EvidenceConfirmProvenanceTier],
) -> EvidenceConfirmProvenanceTier:
    """返回 tier 集合中的最弱 tier。

    Args:
        tiers: provenance tier 序列。

    Returns:
        最弱 tier；空集合返回 `none`。

    Raises:
        无显式抛出。
    """

    weakest: EvidenceConfirmProvenanceTier | None = None
    for tier in tiers:
        if weakest is None or _PROVENANCE_TIER_ORDER[tier] < _PROVENANCE_TIER_ORDER[weakest]:
            weakest = tier
    return "none" if weakest is None else weakest


def _dimension_by_name(
    fact_result: EvidenceConfirmFactResultV2,
    name: EvidenceConfirmDimension,
) -> EvidenceConfirmDimensionResult | None:
    """按名称提取 V2 fact 维度结果。

    Args:
        fact_result: 单 fact V2 结果。
        name: 目标维度名。

    Returns:
        匹配维度结果；缺失时返回 ``None``。

    Raises:
        无显式抛出。
    """

    for dimension_result in fact_result.dimension_results:
        if dimension_result.dimension == name:
            return dimension_result
    return None


def _provenance_contract_from_result(
    result: EvidenceConfirmRepositoryRunResult,
) -> _ProvenanceContract:
    """从 repository runner 结果计算 summary v2 provenance contract。

    该函数只读取 runner 已返回的 reference metadata 与 V2 dimension 结果，不访问
    repository、PDF/cache、source helper、parser、provider、LLM 或报告正文。

    Args:
        result: repository-bounded Evidence Confirm 运行结果。

    Returns:
        provenance contract 聚合结果。

    Raises:
        无显式抛出。
    """

    if (
        result.pathway_status != "pass"
        or result.evidence_confirm_result is None
        or result.reference_build_result is None
    ):
        return _not_run_provenance_contract()

    anchor_tiers = _reference_tiers_by_anchor(result.reference_build_result.references)
    fact_tiers: list[EvidenceConfirmProvenanceTier] = []
    missing_count = 0
    strict_precision_count = 0
    strict_precision_issue_ids: list[str] = []

    for fact_result in result.evidence_confirm_result.fact_results:
        if fact_result.status == "not_applicable":
            continue

        source_support = _dimension_by_name(fact_result, "source_support")
        missing_evidence = _dimension_by_name(fact_result, "missing_evidence")
        value_match = _dimension_by_name(fact_result, "value_match")
        fact_tier = _fact_provenance_tier(fact_result, source_support, missing_evidence, anchor_tiers)
        fact_tiers.append(fact_tier)

        provenance_pass = (
            source_support is not None
            and source_support.status == "pass"
            and missing_evidence is not None
            and missing_evidence.status == "pass"
            and fact_tier != "none"
        )
        if not provenance_pass:
            missing_count += 1
            continue
        if value_match is not None and value_match.status == "fail":
            strict_precision_count += 1
            strict_precision_issue_ids.extend(value_match.issue_ids)

    if not fact_tiers:
        return _not_run_provenance_contract()

    return _ProvenanceContract(
        provenance_status="fail" if missing_count else "pass",
        minimum_provenance_tier=_weakest_tier(fact_tiers),
        provenance_missing_fact_count=missing_count,
        strict_precision_residual_count=strict_precision_count,
        strict_precision_issue_ids=tuple(dict.fromkeys(strict_precision_issue_ids)),
    )


def _not_run_provenance_contract() -> _ProvenanceContract:
    """构造 provenance not-run contract。

    Args:
        无。

    Returns:
        not-run provenance contract。

    Raises:
        无显式抛出。
    """

    return _ProvenanceContract(
        provenance_status="not_run",
        minimum_provenance_tier="none",
        provenance_missing_fact_count=0,
        strict_precision_residual_count=0,
        strict_precision_issue_ids=(),
    )


def _reference_tiers_by_anchor(
    references: tuple[EvidenceConfirmReference, ...],
) -> dict[str, EvidenceConfirmProvenanceTier]:
    """按 anchor 聚合最强 reference tier。

    Args:
        references: materializer 已返回的 reference 列表。

    Returns:
        anchor id 到最强 provenance tier 的映射。

    Raises:
        无显式抛出。
    """

    tiers_by_anchor: dict[str, list[EvidenceConfirmProvenanceTier]] = {}
    for reference in references:
        tiers_by_anchor.setdefault(reference.anchor_id, []).append(_reference_tier(reference))
    return {
        anchor_id: _strongest_tier(tiers)
        for anchor_id, tiers in tiers_by_anchor.items()
    }


def _fact_provenance_tier(
    fact_result: EvidenceConfirmFactResultV2,
    source_support: EvidenceConfirmDimensionResult | None,
    missing_evidence: EvidenceConfirmDimensionResult | None,
    anchor_tiers: dict[str, EvidenceConfirmProvenanceTier],
) -> EvidenceConfirmProvenanceTier:
    """计算单 fact 的最强 matched-reference provenance tier。

    Args:
        fact_result: 单 fact V2 结果。
        source_support: source_support 维度结果。
        missing_evidence: missing_evidence 维度结果。
        anchor_tiers: anchor id 到 reference tier 的映射。

    Returns:
        单 fact 最强 tier；无可证明 reference 时返回 `none`。

    Raises:
        无显式抛出。
    """

    matched_anchor_ids: list[str] = list(fact_result.matched_anchor_ids)
    if source_support is not None:
        matched_anchor_ids.extend(source_support.matched_anchor_ids)
    if missing_evidence is not None:
        matched_anchor_ids.extend(missing_evidence.matched_anchor_ids)
    return _strongest_tier(
        anchor_tiers.get(anchor_id, "none")
        for anchor_id in dict.fromkeys(matched_anchor_ids)
    )


def _validate_semantic_result_identity(
    result: EvidenceConfirmRepositoryRunResult,
    semantic_result: EvidenceSemanticResult | None,
) -> None:
    """校验 injected semantic result 与 deterministic 结果身份一致。

    Args:
        result: repository-bounded Evidence Confirm 运行结果。
        semantic_result: 调用方已生成的 no-live semantic 结果。

    Returns:
        无返回值。

    Raises:
        ValueError: semantic result 的基金代码或年份与 deterministic 结果不一致。
    """

    if semantic_result is None:
        return
    if semantic_result.fund_code != result.fund_code or semantic_result.report_year != result.report_year:
        raise ValueError("semantic result 与 Evidence Confirm repository result 身份不一致")


def _pathway_status(
    result: EvidenceConfirmRepositoryRunResult,
) -> EvidenceConfirmProductionPathwayStatus:
    """规范化 repository pathway 状态。

    Args:
        result: repository-bounded Evidence Confirm 运行结果。

    Returns:
        pathway 状态。

    Raises:
        无显式抛出。
    """

    if result.pathway_status == "pass":
        return "pass"
    return "fail"


def _checked_fact_count(result: EvidenceConfirmRepositoryRunResult) -> int:
    """统计 V2 已检查 fact 数。

    Args:
        result: repository-bounded Evidence Confirm 运行结果。

    Returns:
        fact 数。

    Raises:
        无显式抛出。
    """

    if result.evidence_confirm_result is None:
        return 0
    return len(result.evidence_confirm_result.fact_results)


def _fact_status_count(result: EvidenceConfirmRepositoryRunResult, status: str) -> int:
    """统计指定 V2 fact 状态数量。

    Args:
        result: repository-bounded Evidence Confirm 运行结果。
        status: 目标 fact 状态。

    Returns:
        匹配数量。

    Raises:
        无显式抛出。
    """

    if result.evidence_confirm_result is None:
        return 0
    return sum(1 for fact_result in result.evidence_confirm_result.fact_results if fact_result.status == status)


def _issue_count(result: EvidenceConfirmRepositoryRunResult) -> int:
    """统计 compact issue 数。

    Args:
        result: repository-bounded Evidence Confirm 运行结果。

    Returns:
        runner issue 与 V2 issue 的总数。

    Raises:
        无显式抛出。
    """

    v2_issue_count = (
        len(result.evidence_confirm_result.issues)
        if result.evidence_confirm_result is not None
        else 0
    )
    return len(result.issues) + v2_issue_count


def _blocking_issue_ids(result: EvidenceConfirmRepositoryRunResult) -> tuple[str, ...]:
    """收集阻断 issue ids。

    Args:
        result: repository-bounded Evidence Confirm 运行结果。

    Returns:
        去重后的阻断 issue ids。

    Raises:
        无显式抛出。
    """

    ids = [issue.issue_id for issue in result.issues if issue.severity == "blocking"]
    if result.evidence_confirm_result is not None:
        ids.extend(result.evidence_confirm_result.hard_gate.blocking_issue_ids)
    return tuple(dict.fromkeys(ids))


def _warning_issue_ids(result: EvidenceConfirmRepositoryRunResult) -> tuple[str, ...]:
    """收集生产可见的非阻断 issue ids。

    Args:
        result: repository-bounded Evidence Confirm 运行结果。

    Returns:
        去重后的 reviewable 与 informational issue ids。

    Raises:
        无显式抛出。
    """

    ids = [issue.issue_id for issue in result.issues if issue.severity == "informational"]
    ids.extend(f"pathway:{reason}" for reason in result.pathway_warning_reasons)
    if result.evidence_confirm_result is not None:
        ids.extend(result.evidence_confirm_result.hard_gate.reviewable_issue_ids)
        # V2 informational issue 仍是生产可见的非阻断信号，归入 warning_issue_ids。
        ids.extend(result.evidence_confirm_result.hard_gate.informational_issue_ids)
    return tuple(dict.fromkeys(ids))


def _repository_failure_reason(result: EvidenceConfirmRepositoryRunResult) -> str:
    """生成 repository failure 稳定原因码。

    Args:
        result: repository-bounded Evidence Confirm 运行结果。

    Returns:
        `repository_failure:<reason>`。

    Raises:
        无显式抛出。
    """

    reason = result.issues[0].reason if result.issues else "unknown"
    return f"repository_failure:{reason}"


def _validate_policy(policy: EvidenceConfirmProductionPolicy) -> None:
    """校验生产策略。

    Args:
        policy: 待校验策略。

    Returns:
        无返回值。

    Raises:
        ValueError: 策略非法时抛出。
    """

    if policy not in {"off", "warn", "block"}:
        raise ValueError(f"Evidence Confirm policy 不受支持：{policy}")


def _validate_reason(reason: str) -> None:
    """校验稳定原因码。

    Args:
        reason: 待校验原因码。

    Returns:
        无返回值。

    Raises:
        ValueError: 原因码非法时抛出。
    """

    if reason in STABLE_NOT_RUN_REASONS:
        return
    if reason.startswith("runner_exception:") and reason.removeprefix("runner_exception:"):
        return
    if reason.startswith("repository_failure:") and reason.removeprefix("repository_failure:"):
        return
    raise ValueError(f"Evidence Confirm reason 不受支持：{reason}")
