"""Evidence Confirm 语义蕴含复核，见基金分析模板第 0-7 章。

本模块属于 Agent 层 ``fund_agent/fund`` 基金领域能力，只消费调用方显式传入的
V2 Evidence Confirm 结果、同源引用摘录和语义 claim。它不读取年报仓库、PDF/cache/
source helper、Service、Host、provider、网络、文件系统、renderer、quality gate 或
dayu runtime。当前实现是 no-live semantic companion：调用方注入的 client 只能判断
已通过确定性前置门控的 bounded claim/excerpt。
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final, Literal, Protocol, TypeAlias, get_args

from fund_agent.fund.evidence_confirm import (
    EvidenceConfirmFactResultV2,
    EvidenceConfirmReference,
    EvidenceConfirmResultV2,
)

EVIDENCE_CONFIRM_SEMANTIC_SCHEMA_VERSION: Final[str] = "evidence_confirm_semantic.v1"

EvidenceSemanticStatus: TypeAlias = Literal[
    "entailed",
    "contradicted",
    "insufficient",
    "not_applicable",
]
EvidenceSemanticSeverity: TypeAlias = Literal["block", "warn", "info"]
EvidenceSemanticOverallStatus: TypeAlias = Literal["pass", "warn", "fail", "not_applicable"]
EvidenceSemanticReasonCode: TypeAlias = Literal[
    "entailed_by_excerpt",
    "contradicted_by_excerpt",
    "insufficient_excerpt_support",
    "not_applicable",
    "deterministic_gate_failed",
    "missing_claim",
    "missing_bounded_excerpt",
    "malformed_client_result",
    "client_exception",
]

_SEMANTIC_STATUSES: Final[frozenset[str]] = frozenset(get_args(EvidenceSemanticStatus))
_SEMANTIC_REASON_CODES: Final[frozenset[str]] = frozenset(get_args(EvidenceSemanticReasonCode))
_CLIENT_REASON_CODES_BY_STATUS: Final[dict[str, frozenset[str]]] = {
    "entailed": frozenset(("entailed_by_excerpt",)),
    "contradicted": frozenset(("contradicted_by_excerpt",)),
    "insufficient": frozenset(("insufficient_excerpt_support",)),
    "not_applicable": frozenset(("not_applicable",)),
}
_DETERMINISTIC_PREREQUISITE_DIMENSIONS: Final[tuple[str, ...]] = (
    "source_support",
    "missing_evidence",
    "proof_boundary",
)


@dataclass(frozen=True, slots=True)
class EvidenceSemanticClaim:
    """Evidence Confirm 语义 claim。

    Attributes:
        claim_id: 调用方提供的稳定 claim id。
        fact_id: 关联的章节事实 id。
        source_field_id: 关联的来源字段 id。
        claim_text: 待复核的自然语言断言。
        anchor_ids: claim 显式引用的 anchor ids。
    """

    claim_id: str
    fact_id: str
    source_field_id: str
    claim_text: str
    anchor_ids: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class EvidenceEntailmentRequest:
    """语义蕴含 client 请求。

    Attributes:
        claim: 待复核语义 claim。
        excerpt_texts: 与 claim anchor 绑定的 bounded excerpt 文本。
    """

    claim: EvidenceSemanticClaim
    excerpt_texts: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class EvidenceEntailmentJudgment:
    """语义蕴含 client 判断结果。

    Attributes:
        status: 语义支持状态。
        reason_code: 稳定原因码。
        message: 可选说明。
    """

    status: EvidenceSemanticStatus
    reason_code: EvidenceSemanticReasonCode
    message: str | None = None


class EvidenceEntailmentClient(Protocol):
    """Evidence Confirm 语义蕴含 client 协议。"""

    def judge(self, request: EvidenceEntailmentRequest) -> EvidenceEntailmentJudgment:
        """判断 claim 是否被 bounded excerpts 语义蕴含。

        Args:
            request: 语义蕴含请求。

        Returns:
            语义蕴含判断。

        Raises:
            Exception: 实现方可抛出异常，调用方会 fail-closed。
        """


@dataclass(frozen=True, slots=True)
class EvidenceSemanticClaimResult:
    """单个 semantic claim 复核结果。

    Attributes:
        claim_id: 关联 claim id。
        fact_id: 关联 fact id。
        source_field_id: 关联来源字段 id。
        status: 语义支持状态。
        severity: gate 严重程度。
        reason_code: 稳定原因码。
        matched_anchor_ids: 参与语义复核的 anchor ids。
        message: 可选说明。
    """

    claim_id: str
    fact_id: str
    source_field_id: str
    status: EvidenceSemanticStatus
    severity: EvidenceSemanticSeverity
    reason_code: EvidenceSemanticReasonCode
    matched_anchor_ids: tuple[str, ...]
    message: str | None


@dataclass(frozen=True, slots=True)
class EvidenceSemanticResult:
    """Evidence Confirm 语义蕴含聚合结果。

    Attributes:
        schema_version: 结果 schema 版本。
        fund_code: 基金代码。
        report_year: 年报年份。
        claim_results: 单 claim 结果。
        overall_status: 聚合 gate 状态。
    """

    schema_version: str
    fund_code: str
    report_year: int
    claim_results: tuple[EvidenceSemanticClaimResult, ...]
    overall_status: EvidenceSemanticOverallStatus


def confirm_semantic_entailment(
    *,
    evidence_result: EvidenceConfirmResultV2,
    references: tuple[EvidenceConfirmReference, ...],
    claims: tuple[EvidenceSemanticClaim, ...],
    client: EvidenceEntailmentClient,
) -> EvidenceSemanticResult:
    """复核 semantic claims 是否被同源 bounded excerpts 蕴含。

    Args:
        evidence_result: 已完成的 V2 Evidence Confirm 结果。
        references: 调用方显式传入的 reference excerpts。
        claims: 待复核语义 claim 列表。
        client: 调用方注入的语义蕴含 client。

    Returns:
        语义蕴含聚合结果。

    Raises:
        无显式抛出；client 异常会被转换为 fail-closed claim result。
    """

    facts_by_identity = _fact_results_by_identity(evidence_result)
    reference_texts_by_anchor = _reference_texts_by_anchor(references)
    claim_results = tuple(
        _confirm_single_claim(
            claim=claim,
            fact_result=facts_by_identity.get((claim.fact_id, claim.source_field_id)),
            reference_texts_by_anchor=reference_texts_by_anchor,
            client=client,
        )
        for claim in sorted(claims, key=lambda item: (item.source_field_id, item.fact_id, item.claim_id))
    )
    return EvidenceSemanticResult(
        schema_version=EVIDENCE_CONFIRM_SEMANTIC_SCHEMA_VERSION,
        fund_code=evidence_result.fund_code,
        report_year=evidence_result.report_year,
        claim_results=claim_results,
        overall_status=_overall_status(claim_results),
    )


def _confirm_single_claim(
    *,
    claim: EvidenceSemanticClaim,
    fact_result: EvidenceConfirmFactResultV2 | None,
    reference_texts_by_anchor: dict[str, tuple[str, ...]],
    client: EvidenceEntailmentClient,
) -> EvidenceSemanticClaimResult:
    """复核单个 semantic claim。

    Args:
        claim: 待复核 claim。
        fact_result: 对应 V2 fact 结果。
        reference_texts_by_anchor: proven reference excerpt 文本索引。
        client: 语义蕴含 client。

    Returns:
        单 claim 复核结果。

    Raises:
        无显式抛出。
    """

    if fact_result is None or _deterministic_gate_blocks(fact_result):
        return _claim_result(
            claim,
            status="insufficient",
            severity="block",
            reason_code="deterministic_gate_failed",
            matched_anchor_ids=(),
            message="deterministic Evidence Confirm gate 未通过。",
        )

    if not claim.claim_text.strip():
        return _claim_result(
            claim,
            status="not_applicable",
            severity="info",
            reason_code="missing_claim",
            matched_anchor_ids=(),
            message="claim_text 为空。",
        )

    matched_anchor_ids, excerpt_texts = _bounded_excerpts_for_claim(
        claim,
        fact_result,
        reference_texts_by_anchor,
    )
    if not excerpt_texts:
        return _claim_result(
            claim,
            status="insufficient",
            severity="block",
            reason_code="missing_bounded_excerpt",
            matched_anchor_ids=(),
            message="claim 没有同 anchor 的 bounded excerpt。",
        )

    request = EvidenceEntailmentRequest(claim=claim, excerpt_texts=excerpt_texts)
    try:
        judgment = client.judge(request)
    except Exception:  # noqa: BLE001 - semantic gate must fail closed without leaking details.
        return _claim_result(
            claim,
            status="insufficient",
            severity="block",
            reason_code="client_exception",
            matched_anchor_ids=matched_anchor_ids,
            message="semantic entailment client 抛出异常。",
        )

    if not _judgment_is_valid(judgment):
        return _claim_result(
            claim,
            status="insufficient",
            severity="block",
            reason_code="malformed_client_result",
            matched_anchor_ids=matched_anchor_ids,
            message="semantic entailment client 返回非法结果。",
        )

    severity = _severity_for_judgment(judgment, fact_result)
    return _claim_result(
        claim,
        status=judgment.status,
        severity=severity,
        reason_code=judgment.reason_code,
        matched_anchor_ids=matched_anchor_ids,
        message=judgment.message,
    )


def _fact_results_by_identity(
    evidence_result: EvidenceConfirmResultV2,
) -> dict[tuple[str, str], EvidenceConfirmFactResultV2]:
    """按 fact/source identity 索引 V2 fact 结果。

    Args:
        evidence_result: V2 Evidence Confirm 结果。

    Returns:
        `(fact_id, source_field_id)` 到 fact result 的映射。

    Raises:
        无显式抛出。
    """

    return {
        (fact_result.fact_id, fact_result.source_field_id): fact_result
        for fact_result in evidence_result.fact_results
    }


def _reference_texts_by_anchor(
    references: tuple[EvidenceConfirmReference, ...],
) -> dict[str, tuple[str, ...]]:
    """按 anchor id 索引 proven reference excerpt 文本。

    Args:
        references: 显式 reference excerpts。

    Returns:
        anchor id 到 excerpt 文本元组的映射。

    Raises:
        无显式抛出。
    """

    grouped: dict[str, list[str]] = {}
    for reference in references:
        if reference.candidate_only or reference.source_truth_status != "proven":
            continue
        text = reference.excerpt_text.strip()
        if not text:
            continue
        grouped.setdefault(reference.anchor_id, []).append(text)
    return {anchor_id: tuple(texts) for anchor_id, texts in grouped.items()}


def _deterministic_gate_blocks(fact_result: EvidenceConfirmFactResultV2) -> bool:
    """判断 V2 deterministic gate 是否阻断语义复核。

    Args:
        fact_result: V2 fact 结果。

    Returns:
        需要阻断语义 client 调用时返回 ``True``。

    Raises:
        无显式抛出。
    """

    if fact_result.hard_gate.status == "fail":
        return True
    for dimension in _DETERMINISTIC_PREREQUISITE_DIMENSIONS:
        if _dimension_status(fact_result, dimension) != "pass":
            return True
    return _dimension_status(fact_result, "value_match") == "fail"


def _dimension_status(fact_result: EvidenceConfirmFactResultV2, dimension: str) -> str | None:
    """读取指定 V2 dimension 状态。

    Args:
        fact_result: V2 fact 结果。
        dimension: 维度名称。

    Returns:
        维度状态；不存在时返回 ``None``。

    Raises:
        无显式抛出。
    """

    for result in fact_result.dimension_results:
        if result.dimension == dimension:
            return result.status
    return None


def _bounded_excerpts_for_claim(
    claim: EvidenceSemanticClaim,
    fact_result: EvidenceConfirmFactResultV2,
    reference_texts_by_anchor: dict[str, tuple[str, ...]],
) -> tuple[tuple[str, ...], tuple[str, ...]]:
    """读取 claim 与 deterministic matched anchors 交集内的 excerpt。

    Args:
        claim: 待复核 claim。
        fact_result: V2 fact 结果。
        reference_texts_by_anchor: proven reference excerpt 文本索引。

    Returns:
        matched anchor ids 与 excerpt 文本。

    Raises:
        无显式抛出。
    """

    deterministic_anchor_ids = set(fact_result.matched_anchor_ids)
    matched_anchor_ids: list[str] = []
    excerpt_texts: list[str] = []
    for anchor_id in claim.anchor_ids:
        if anchor_id not in deterministic_anchor_ids:
            continue
        texts = reference_texts_by_anchor.get(anchor_id, ())
        if not texts:
            continue
        matched_anchor_ids.append(anchor_id)
        excerpt_texts.extend(texts)
    return tuple(dict.fromkeys(matched_anchor_ids)), tuple(dict.fromkeys(excerpt_texts))


def _judgment_is_valid(judgment: object) -> bool:
    """校验 semantic client 判断结果是否落入闭集且语义兼容。

    Args:
        judgment: client 返回对象。

    Returns:
        判断结果满足闭集和 status/reason 兼容契约时返回 ``True``。

    Raises:
        无显式抛出。
    """

    if not (
        isinstance(judgment, EvidenceEntailmentJudgment)
        and judgment.status in _SEMANTIC_STATUSES
        and judgment.reason_code in _SEMANTIC_REASON_CODES
    ):
        return False
    return judgment.reason_code in _CLIENT_REASON_CODES_BY_STATUS[judgment.status]


def _severity_for_judgment(
    judgment: EvidenceEntailmentJudgment,
    fact_result: EvidenceConfirmFactResultV2,
) -> EvidenceSemanticSeverity:
    """把 semantic judgment 映射为 gate severity。

    Args:
        judgment: 语义蕴含判断。
        fact_result: V2 fact 结果。

    Returns:
        gate severity。

    Raises:
        无显式抛出。
    """

    if judgment.status == "contradicted":
        return "block"
    if judgment.status == "insufficient":
        return "warn"
    if judgment.status == "not_applicable":
        return "info"
    if fact_result.hard_gate.status == "warn":
        return "warn"
    return "info"


def _claim_result(
    claim: EvidenceSemanticClaim,
    *,
    status: EvidenceSemanticStatus,
    severity: EvidenceSemanticSeverity,
    reason_code: EvidenceSemanticReasonCode,
    matched_anchor_ids: tuple[str, ...],
    message: str | None,
) -> EvidenceSemanticClaimResult:
    """构造单 claim 结果。

    Args:
        claim: 待复核 claim。
        status: 语义支持状态。
        severity: gate 严重程度。
        reason_code: 稳定原因码。
        matched_anchor_ids: 匹配 anchor ids。
        message: 可选说明。

    Returns:
        单 claim 结果。

    Raises:
        无显式抛出。
    """

    return EvidenceSemanticClaimResult(
        claim_id=claim.claim_id,
        fact_id=claim.fact_id,
        source_field_id=claim.source_field_id,
        status=status,
        severity=severity,
        reason_code=reason_code,
        matched_anchor_ids=matched_anchor_ids,
        message=message,
    )


def _overall_status(
    claim_results: tuple[EvidenceSemanticClaimResult, ...],
) -> EvidenceSemanticOverallStatus:
    """聚合 semantic claim gate 状态。

    Args:
        claim_results: 单 claim 结果。

    Returns:
        聚合 gate 状态。

    Raises:
        无显式抛出。
    """

    if any(item.status == "contradicted" or item.severity == "block" for item in claim_results):
        return "fail"
    if any(item.status == "insufficient" or item.severity == "warn" for item in claim_results):
        return "warn"
    if any(item.status == "entailed" for item in claim_results):
        return "pass"
    return "not_applicable"


__all__ = [
    "EVIDENCE_CONFIRM_SEMANTIC_SCHEMA_VERSION",
    "EvidenceEntailmentClient",
    "EvidenceEntailmentJudgment",
    "EvidenceEntailmentRequest",
    "EvidenceSemanticClaim",
    "EvidenceSemanticClaimResult",
    "EvidenceSemanticOverallStatus",
    "EvidenceSemanticReasonCode",
    "EvidenceSemanticResult",
    "EvidenceSemanticSeverity",
    "EvidenceSemanticStatus",
    "confirm_semantic_entailment",
]
