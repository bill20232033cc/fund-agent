"""单基金报告质量 gate 集成适配器。

本模块属于 Agent 层基金能力，负责把 `FundAnalysisService` 已经取得的
`StructuredFundDataBundle` 转换为 P4 snapshot/score/quality gate 产物。
它不重新抽取基金文档，也不把质量规则上移到 Service 或 UI。
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

from fund_agent.config.paths import DEFAULT_QUALITY_GATE_OUTPUT_ROOT
from fund_agent.fund.data_extractor import StructuredFundDataBundle
from fund_agent.fund.extraction_score import ExtractionScoreResult, write_extraction_score_records
from fund_agent.fund.extraction_snapshot import (
    SelectedFundRecord,
    build_snapshot_records,
    load_selected_funds,
    validate_selected_fund_pool,
)
from fund_agent.fund.evidence_confirm_production import EvidenceConfirmProductionSummary
from fund_agent.fund.quality_gate import (
    SEVERITY_BLOCK,
    SEVERITY_INFO,
    SEVERITY_WARN,
    QualityGateIssue,
    QualityGateResult,
    merge_quality_gate_issues,
    run_quality_gate,
)


@dataclass(frozen=True, slots=True)
class BundleQualityGateResult:
    """基于单只基金结构化数据包运行 quality gate 的结果。

    Attributes:
        run_id: 本次 quality gate 运行 ID。
        output_dir: 本次运行输出目录。
        snapshot_path: 由 bundle 生成的单基金 snapshot JSONL 路径。
        score_result: extraction score 结果；未运行时为空。
        quality_gate_result: quality gate 结果；未运行时为空。
        not_run_reason: 未运行原因；正常运行时为空。
    """

    run_id: str
    output_dir: Path
    snapshot_path: Path
    score_result: ExtractionScoreResult | None
    quality_gate_result: QualityGateResult | None
    not_run_reason: str | None


def run_quality_gate_for_bundle(
    *,
    bundle: StructuredFundDataBundle,
    source_csv: Path,
    output_dir: Path | None,
    run_id: str,
    golden_answer_path: Path | None,
    evidence_confirm_summary: EvidenceConfirmProductionSummary | None = None,
) -> BundleQualityGateResult:
    """对已抽取的单基金结构化数据运行质量 gate。

    Args:
        bundle: `FundAnalysisService` 已抽取的结构化基金数据包，见模板第 1 章产品本质。
        source_csv: 精选基金池 CSV，用于取得 App 类别和基金名称。
        output_dir: 显式输出目录；为空时使用 `reports/quality-gate-runs/<run_id>`。
        run_id: 本次运行 ID，必须由调用方显式传入。
        golden_answer_path: strict golden answer JSON 路径；为空时 correctness 标记为 unavailable。
        evidence_confirm_summary: 可选 Evidence Confirm 生产摘要；为空时保持既有行为，
            不向 quality gate 追加 ECQ issue。

    Returns:
        单基金 quality gate 集成结果。当前基金不在精选池或 CSV 不可用时，返回
        `not_run_reason`，不伪造 App 类别或继续评分。

    Raises:
        ValueError: run_id 为空时抛出。
        OSError: 输出目录或产物写入失败时抛出。
        json.JSONDecodeError: strict golden answer JSON 非法时由底层抛出。
    """

    if not run_id.strip():
        raise ValueError("quality_gate_run_id 不能为空")
    selected_fund, not_run_reason = _selected_fund_for_bundle(
        source_csv=source_csv,
        fund_code=bundle.fund_code,
    )
    resolved_output_dir = output_dir or DEFAULT_QUALITY_GATE_OUTPUT_ROOT / run_id
    snapshot_path = resolved_output_dir / "snapshot.jsonl"
    if selected_fund is None:
        return BundleQualityGateResult(
            run_id=run_id,
            output_dir=resolved_output_dir,
            snapshot_path=snapshot_path,
            score_result=None,
            quality_gate_result=None,
            not_run_reason=not_run_reason,
        )

    resolved_output_dir.mkdir(parents=True, exist_ok=True)
    records = build_snapshot_records(
        bundle=bundle,
        selected_fund=selected_fund,
        run_id=run_id,
        extraction_timestamp=_utc_now(),
        source_csv=str(source_csv),
    )
    snapshot_path.write_text(
        "\n".join(json.dumps(asdict(record), ensure_ascii=False) for record in records) + "\n",
        encoding="utf-8",
    )
    score_result = write_extraction_score_records(
        records=[asdict(record) for record in records],
        snapshot_path=snapshot_path,
        source_csv=source_csv,
        output_dir=resolved_output_dir,
        golden_answer_path=golden_answer_path,
    )
    gate_result = run_quality_gate(
        score_path=score_result.score_json_path,
        output_dir=resolved_output_dir,
    )
    if evidence_confirm_summary is not None:
        ecq_issues = _evidence_confirm_quality_gate_issues(
            evidence_confirm_summary,
            fund_code=bundle.fund_code,
            report_year=bundle.report_year,
        )
        gate_result = merge_quality_gate_issues(gate_result, ecq_issues)
    return BundleQualityGateResult(
        run_id=run_id,
        output_dir=resolved_output_dir,
        snapshot_path=snapshot_path,
        score_result=score_result,
        quality_gate_result=gate_result,
        not_run_reason=None,
    )


def check_quality_gate_fund_membership(
    *,
    source_csv: Path,
    fund_code: str,
) -> str | None:
    """检查当前基金是否可运行单基金 quality gate。

    该函数只做精选池 CSV 可用性和基金代码成员检查，不读取年报、不生成
    snapshot，也不执行评分。Service 可用它在昂贵抽取前进行 block 策略短路。

    Args:
        source_csv: 精选基金池 CSV 路径。
        fund_code: 当前基金代码。

    Returns:
        可运行时返回 `None`；不可运行时返回 not-run reason。

    Raises:
        无显式抛出；CSV 读取和校验异常会转换为 not-run reason。
    """

    _, not_run_reason = _selected_fund_for_bundle(
        source_csv=source_csv,
        fund_code=fund_code,
    )
    return not_run_reason


def _evidence_confirm_quality_gate_issues(
    summary: EvidenceConfirmProductionSummary | None,
    *,
    fund_code: str,
    report_year: int,
) -> tuple[QualityGateIssue, ...]:
    """把 Evidence Confirm 摘要投影为 ECQ quality gate issue。

    该函数只消费调用方传入的 compact summary，不读取 repository、PDF/cache、
    source adapter、parser、Docling、provider 或 LLM。见模板第 0-7 章 Evidence
    Confirm 证据复核路径。

    Args:
        summary: Evidence Confirm 生产摘要；显式传入 `None` 时生成 ECQ0/info。
        fund_code: 基金代码，用于 summary absent 时生成稳定 issue id。
        report_year: 年报年份，用于 summary absent 时生成稳定 issue id。

    Returns:
        ECQ issue 列表。

    Raises:
        无显式抛出。
    """

    if summary is None:
        return (
            _ecq_issue(
                rule_code="ECQ0",
                severity=SEVERITY_INFO,
                fund_code=fund_code,
                report_year=report_year,
                reason="not_requested",
                message="Evidence Confirm 未请求；quality gate 仅记录显式可见性信息。",
            ),
        )
    if summary.status == "not_run":
        return (
            _ecq_issue(
                rule_code="ECQ0",
                severity=SEVERITY_INFO,
                fund_code=summary.fund_code,
                report_year=summary.report_year,
                reason=summary.not_run_reason or "not_requested",
                message="Evidence Confirm 未运行。",
            ),
        )
    if summary.pathway_status == "fail":
        reason = summary.not_run_reason or "repository_failure:unknown"
        return (
            _ecq_issue(
                rule_code="ECQ1",
                severity=_ecq_policy_severity(summary),
                fund_code=summary.fund_code,
                report_year=summary.report_year,
                reason=reason,
                message="Evidence Confirm repository/source/reference 通路失败。",
            ),
        )
    issues: list[QualityGateIssue] = []
    if summary.deterministic_status == "fail":
        reason = f"deterministic_fail_{len(summary.blocking_issue_ids)}"
        issues.append(
            _ecq_issue(
                rule_code="ECQ2",
                severity=_ecq_policy_severity(summary),
                fund_code=summary.fund_code,
                report_year=summary.report_year,
                reason=reason,
                message=(
                    "Evidence Confirm V2 hard-gate fail；"
                    f"blocking_issue_count={len(summary.blocking_issue_ids)}。"
                ),
            ),
        )
    elif summary.deterministic_status == "warn":
        reason = f"deterministic_warn_{len(summary.warning_issue_ids)}"
        issues.append(
            _ecq_issue(
                rule_code="ECQ3",
                severity=SEVERITY_WARN,
                fund_code=summary.fund_code,
                report_year=summary.report_year,
                reason=reason,
                message=(
                    "Evidence Confirm V2 存在可复核 warning；"
                    f"warning_issue_count={len(summary.warning_issue_ids)}。"
                ),
            ),
        )
    if summary.semantic_status in {"fail", "warn"}:
        issues.append(_semantic_ecq_issue(summary))
    return tuple(issues)


def _semantic_ecq_issue(summary: EvidenceConfirmProductionSummary) -> QualityGateIssue:
    """把 injected semantic companion fail/warn 投影为 ECQ4。

    Args:
        summary: 已包含 semantic_status 的 Evidence Confirm 生产摘要。

    Returns:
        ECQ4 issue。

    Raises:
        ValueError: `policy="off"` 的 semantic fail/warn 摘要进入投影时抛出。
    """

    reason = f"semantic_{summary.semantic_status}"
    return _ecq_issue(
        rule_code="ECQ4",
        severity=_ecq_policy_severity(summary),
        fund_code=summary.fund_code,
        report_year=summary.report_year,
        reason=reason,
        message=f"Evidence Confirm semantic companion {summary.semantic_status}。",
    )


def _ecq_policy_severity(summary: EvidenceConfirmProductionSummary) -> str:
    """按 Evidence Confirm policy 决定 ECQ fail severity。

    Args:
        summary: Evidence Confirm 生产摘要。

    Returns:
        `block` 或 `warn`。

    Raises:
        ValueError: `policy="off"` 的 fail/warn 摘要进入 ECQ fail 映射时抛出。
    """

    if summary.policy == "block":
        return SEVERITY_BLOCK
    if summary.policy == "off":
        raise ValueError("policy='off' 的 Evidence Confirm fail/warn 摘要不能投影为 ECQ warn")
    return SEVERITY_WARN


def _ecq_issue(
    *,
    rule_code: str,
    severity: str,
    fund_code: str,
    report_year: int,
    reason: str,
    message: str,
) -> QualityGateIssue:
    """构造稳定 ECQ issue。

    Args:
        rule_code: ECQ 规则码。
        severity: issue 严重级别。
        fund_code: 基金代码。
        report_year: 年报年份。
        reason: 稳定原因码。
        message: 人类可读说明。

    Returns:
        QualityGateIssue。

    Raises:
        无显式抛出。
    """

    issue_id = f"evidence-confirm:{fund_code}:{report_year}:{rule_code}:{reason}"
    return QualityGateIssue(
        rule_code=rule_code,
        severity=severity,
        fund_code=fund_code,
        field_name=None,
        priority=None,
        message=message,
        reason=reason,
        issue_id=issue_id,
    )


def _selected_fund_for_bundle(
    *,
    source_csv: Path,
    fund_code: str,
) -> tuple[SelectedFundRecord | None, str | None]:
    """从精选基金池中查找当前基金记录。

    Args:
        source_csv: 精选基金池 CSV 路径。
        fund_code: 当前基金代码。

    Returns:
        `(selected_fund, not_run_reason)`；找不到或 CSV 不可用时返回未运行原因。

    Raises:
        无显式抛出；CSV 读取和校验异常会转换为 not-run reason。
    """

    try:
        funds = load_selected_funds(source_csv)
        validation = validate_selected_fund_pool(funds)
    except FileNotFoundError:
        return None, "quality gate source csv not found"
    except ValueError as exc:
        return None, f"quality gate source csv format error: {exc}"
    if validation.has_blocking_errors:
        return None, "quality gate source csv has blocking validation errors"
    for fund in funds:
        if fund.fund_code == fund_code:
            return fund, None
    return None, f"fund_code `{fund_code}` not found in quality gate source csv"


def _utc_now() -> str:
    """返回 UTC ISO-8601 时间戳。

    Args:
        无。

    Returns:
        ISO-8601 UTC 时间戳。

    Raises:
        无显式抛出。
    """

    return datetime.now(timezone.utc).isoformat()
