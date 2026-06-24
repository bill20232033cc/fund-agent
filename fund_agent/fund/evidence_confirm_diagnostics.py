"""Evidence Confirm V2 安全诊断聚合，见基金分析模板第 0-7 章。

本模块属于 Agent 层 Fund 能力，只消费调用方已经得到的
`EvidenceConfirmResultV2` 内存对象，把 fact-level V2 结果压缩成安全诊断桶。
它不读取文档仓库、PDF/cache/source helper、parser artifact、Service、Host、
provider、CLI 或文件系统，也不改变 quality gate 语义。
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Final, Literal, TypeAlias

from fund_agent.fund.evidence_confirm import (
    EvidenceConfirmDimension,
    EvidenceConfirmDimensionStatus,
    EvidenceConfirmFactResultV2,
    EvidenceConfirmNextGateRecommendation,
    EvidenceConfirmResultV2,
)

EVIDENCE_CONFIRM_DIAGNOSTIC_SCHEMA_VERSION: Final[
    Literal["evidence_confirm_fact_diagnostic.v1"]
] = "evidence_confirm_fact_diagnostic.v1"

EvidenceConfirmDiagnosticRootCause: TypeAlias = Literal[
    "true_anchor_precision_gap",
    "projection_attachment_defect",
    "v2_false_positive",
    "undetermined",
]

_DIMENSION_ORDER: Final[dict[str, int]] = {
    "anchor_precision": 0,
    "source_support": 1,
    "missing_evidence": 2,
    "proof_boundary": 3,
    "value_match": 4,
}
_STATUS_ORDER: Final[dict[str, int]] = {"fail": 0, "warn": 1}


@dataclass(frozen=True, slots=True)
class EvidenceConfirmDiagnosticBucket:
    """Evidence Confirm 诊断聚合桶。

    Attributes:
        dimension: V2 维度。
        status: 该桶聚合的维度状态，只包含 fail / warn。
        source_field_id: 来源字段 ID。
        chapter_id: 模板章节编号。
        fact_count: 命中该桶的 fact 数。
        issue_count: 命中该桶的 issue 数。
        issue_ids: 去重后的安全 issue ids，不包含原文、路径或摘录。
        root_cause_classification: A1 诊断用保守 root-cause 初判。
        next_gate_recommendation: V2 提供的下一 gate 建议。
    """

    dimension: EvidenceConfirmDimension
    status: Literal["fail", "warn"]
    source_field_id: str
    chapter_id: int
    fact_count: int
    issue_count: int
    issue_ids: tuple[str, ...]
    root_cause_classification: EvidenceConfirmDiagnosticRootCause
    next_gate_recommendation: EvidenceConfirmNextGateRecommendation


@dataclass(frozen=True, slots=True)
class EvidenceConfirmDiagnosticSummary:
    """Evidence Confirm V2 安全诊断摘要。

    Attributes:
        schema_version: 诊断 schema 版本。
        fund_code: 基金代码。
        report_year: 年报年份。
        overall_status: V2 聚合状态。
        checked_fact_count: 已检查 fact 数。
        failed_fact_count: 失败 fact 数。
        warning_fact_count: 警告 fact 数。
        not_applicable_fact_count: 不适用 fact 数。
        issue_count: V2 issue 总数。
        diagnostic_buckets: 按维度/字段/章节聚合的安全诊断桶。
        dominant_root_cause_classifications: 诊断桶中出现的 root-cause 分类，按出现顺序去重。
    """

    schema_version: Literal["evidence_confirm_fact_diagnostic.v1"]
    fund_code: str
    report_year: int
    overall_status: str
    checked_fact_count: int
    failed_fact_count: int
    warning_fact_count: int
    not_applicable_fact_count: int
    issue_count: int
    diagnostic_buckets: tuple[EvidenceConfirmDiagnosticBucket, ...]
    dominant_root_cause_classifications: tuple[EvidenceConfirmDiagnosticRootCause, ...]

    def to_safe_dict(self) -> dict[str, object]:
        """返回只含安全标量和稳定 ID 的字典。

        Returns:
            可写入诊断 artifact 的 dict，不包含原文 excerpt、PDF/cache 路径、
            source helper 细节或 provider payload。

        Raises:
            无显式抛出。
        """

        return asdict(self)


def summarize_evidence_confirm_diagnostics(
    result: EvidenceConfirmResultV2,
) -> EvidenceConfirmDiagnosticSummary:
    """把 V2 Evidence Confirm 结果聚合为安全事实级诊断摘要。

    Args:
        result: 已运行完成的 V2 Evidence Confirm 结果。

    Returns:
        安全诊断摘要。

    Raises:
        无显式抛出。
    """

    buckets = _diagnostic_buckets(result.fact_results)
    return EvidenceConfirmDiagnosticSummary(
        schema_version=EVIDENCE_CONFIRM_DIAGNOSTIC_SCHEMA_VERSION,
        fund_code=result.fund_code,
        report_year=result.report_year,
        overall_status=result.overall_status,
        checked_fact_count=len(result.fact_results),
        failed_fact_count=_fact_status_count(result.fact_results, "fail"),
        warning_fact_count=_fact_status_count(result.fact_results, "warn"),
        not_applicable_fact_count=_fact_status_count(result.fact_results, "not_applicable"),
        issue_count=len(result.issues),
        diagnostic_buckets=buckets,
        dominant_root_cause_classifications=_dominant_root_causes(buckets),
    )


def _diagnostic_buckets(
    fact_results: tuple[EvidenceConfirmFactResultV2, ...],
) -> tuple[EvidenceConfirmDiagnosticBucket, ...]:
    """按维度、字段、章节和建议 gate 聚合失败/警告维度。

    Args:
        fact_results: V2 fact 结果。

    Returns:
        稳定排序的诊断桶。

    Raises:
        无显式抛出。
    """

    grouped: dict[
        tuple[
            EvidenceConfirmDimension,
            Literal["fail", "warn"],
            str,
            int,
            EvidenceConfirmDiagnosticRootCause,
            EvidenceConfirmNextGateRecommendation,
        ],
        dict[str, object],
    ] = {}
    for fact in fact_results:
        for dimension in fact.dimension_results:
            if dimension.status not in {"fail", "warn"}:
                continue
            status = _fail_or_warn_status(dimension.status)
            root_cause = _classify_root_cause(
                dimension.dimension,
                status,
                dimension.next_gate_recommendation,
            )
            key = (
                dimension.dimension,
                status,
                fact.source_field_id,
                _chapter_id_from_fact_id(fact.fact_id),
                root_cause,
                dimension.next_gate_recommendation,
            )
            bucket = grouped.setdefault(key, {"fact_count": 0, "issue_ids": []})
            bucket["fact_count"] = int(bucket["fact_count"]) + 1
            issue_ids = bucket["issue_ids"]
            if isinstance(issue_ids, list):
                issue_ids.extend(dimension.issue_ids)

    return tuple(
        EvidenceConfirmDiagnosticBucket(
            dimension=dimension,
            status=status,
            source_field_id=source_field_id,
            chapter_id=chapter_id,
            fact_count=int(payload["fact_count"]),
            issue_count=len(_unique_strings(tuple(payload["issue_ids"]))),
            issue_ids=_unique_strings(tuple(payload["issue_ids"])),
            root_cause_classification=root_cause,
            next_gate_recommendation=next_gate,
        )
        for (
            dimension,
            status,
            source_field_id,
            chapter_id,
            root_cause,
            next_gate,
        ), payload in sorted(grouped.items(), key=_bucket_sort_key)
    )


def _classify_root_cause(
    dimension: EvidenceConfirmDimension,
    status: Literal["fail", "warn"],
    next_gate_recommendation: EvidenceConfirmNextGateRecommendation,
) -> EvidenceConfirmDiagnosticRootCause:
    """对 V2 维度失败做保守 root-cause 初判。

    Args:
        dimension: V2 维度。
        status: 维度状态。
        next_gate_recommendation: V2 下一 gate 建议。

    Returns:
        A1 诊断计划使用的 root-cause 分类。

    Raises:
        无显式抛出。
    """

    if dimension == "anchor_precision" and status == "warn":
        return "true_anchor_precision_gap"
    if dimension in {"missing_evidence", "source_support", "proof_boundary"}:
        return "projection_attachment_defect"
    if next_gate_recommendation == "value_matching":
        return "undetermined"
    return "undetermined"


def _fact_status_count(
    fact_results: tuple[EvidenceConfirmFactResultV2, ...],
    status: str,
) -> int:
    """统计指定 fact 状态数量。

    Args:
        fact_results: V2 fact 结果。
        status: 目标状态。

    Returns:
        匹配数量。

    Raises:
        无显式抛出。
    """

    return sum(1 for fact in fact_results if fact.status == status)


def _dominant_root_causes(
    buckets: tuple[EvidenceConfirmDiagnosticBucket, ...],
) -> tuple[EvidenceConfirmDiagnosticRootCause, ...]:
    """按诊断桶顺序去重 root-cause 分类。

    Args:
        buckets: 诊断桶。

    Returns:
        去重后的 root-cause 分类。

    Raises:
        无显式抛出。
    """

    return tuple(dict.fromkeys(bucket.root_cause_classification for bucket in buckets))


def _chapter_id_from_fact_id(fact_id: str) -> int:
    """从标准 fact id 中读取章节编号，失败时返回 -1。

    Args:
        fact_id: `chapter-fact:<fund>:<year>:ch<id>:<source>` 形式的 fact id。

    Returns:
        章节编号；无法解析时返回 -1。

    Raises:
        无显式抛出。
    """

    for part in fact_id.split(":"):
        if part.startswith("ch") and part[2:].isdigit():
            return int(part[2:])
    return -1


def _unique_strings(values: tuple[object, ...]) -> tuple[str, ...]:
    """把值转成字符串并按首次出现顺序去重。

    Args:
        values: 输入值。

    Returns:
        去重字符串元组。

    Raises:
        无显式抛出。
    """

    return tuple(dict.fromkeys(str(value) for value in values if value is not None))


def _fail_or_warn_status(
    status: EvidenceConfirmDimensionStatus,
) -> Literal["fail", "warn"]:
    """把已过滤的维度状态收窄为 fail/warn。

    Args:
        status: V2 维度状态。

    Returns:
        `fail` 或 `warn`。

    Raises:
        ValueError: 调用方传入非 fail/warn 状态时抛出。
    """

    if status in {"fail", "warn"}:
        return status
    raise ValueError("diagnostic bucket status 必须是 fail / warn")


def _bucket_sort_key(
    item: tuple[
        tuple[
            EvidenceConfirmDimension,
            Literal["fail", "warn"],
            str,
            int,
            EvidenceConfirmDiagnosticRootCause,
            EvidenceConfirmNextGateRecommendation,
        ],
        dict[str, object],
    ],
) -> tuple[int, int, str, int, str, str]:
    """返回诊断桶稳定排序 key。

    Args:
        item: 分组项。

    Returns:
        排序 key。

    Raises:
        无显式抛出。
    """

    dimension, status, source_field_id, chapter_id, root_cause, next_gate = item[0]
    return (
        _STATUS_ORDER.get(status, 99),
        _DIMENSION_ORDER.get(dimension, 99),
        source_field_id,
        chapter_id,
        root_cause,
        next_gate,
    )
