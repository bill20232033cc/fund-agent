"""Golden readiness preflight 只读聚合能力。

本模块属于 Agent 层 Fund 包，负责把 snapshot、score、quality gate、
strict golden answer v1、fixture promotion state 与 accepted coverage disposition
聚合成 baseline/golden v1 promotion 前的只读 readiness 判定。它不读取 PDF/cache，
不调用下载或来源 helper，不修改 FQ0-FQ6、golden fixture 或 promotion state。

基金分析报告仍以模板第 0-7 章为业务分析结构；本模块只处理 promotion readiness
边界，避免把质量 gate 的 warning、eligible fallback 或 reviewed candidate 误判为 ready。
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Literal, Mapping, Sequence, cast

ReadinessStatus = Literal["ready", "blocked", "deferred_with_owner", "not_evaluated"]
PreflightOverallStatus = Literal["pass", "block"]
BlockerSeverity = Literal["block", "warn", "info"]
PromotionState = Literal["not_promoted", "promoted_fixture", "unknown"]
PreflightDisposition = Literal[
    "reviewed_coverage_candidate",
    "include_for_later_review",
    "replace",
    "needs_taxonomy_gate",
    "needs_evidence_gate",
    "blocked",
    "deferred",
    "unknown",
]

INPUT_SCHEMA_VERSION = "fund-agent.golden-readiness-preflight.input.v1"
OUTPUT_SCHEMA_VERSION = "fund-agent.golden-readiness-preflight.v1"
STATIC_DISPOSITION_SCHEMA_VERSION = "fund-agent.coverage-disposition.static-current.v1"
STATIC_DISPOSITION_ACCEPTED_AS_OF = "2026-05-29"
ELIGIBLE_FALLBACK_FAILURE_CATEGORIES = frozenset({"not_found", "unavailable"})
INELIGIBLE_FALLBACK_FAILURE_CATEGORIES = frozenset(
    {"schema_drift", "identity_mismatch", "integrity_error"}
)
RESERVED_STRICT_GOLDEN_CODES = frozenset(
    {"strict_golden_year_not_covered", "strict_golden_partial_coverage"}
)
DEFAULT_REPORT_YEAR = 2024


@dataclass(frozen=True, slots=True)
class ReadinessBlocker:
    """Readiness 阻断项。

    Attributes:
        code: blocker taxonomy 代码。
        severity: 阻断等级。
        scope: 影响范围。
        fund_code: 关联基金代码或 slot id。
        message: 人类可读说明。
        owner: 后续 owner。
        next_gate: 下一步 gate。
        evidence_artifacts: 证据 artifact 路径。
    """

    code: str
    severity: BlockerSeverity
    scope: str
    fund_code: str | None
    message: str
    owner: str
    next_gate: str
    evidence_artifacts: tuple[Path, ...] = ()


@dataclass(frozen=True, slots=True)
class ReadinessWarning:
    """Readiness 非阻断 warning。

    Attributes:
        code: warning taxonomy 代码。
        severity: warning 等级。
        scope: 影响范围。
        fund_code: 关联基金代码或 slot id。
        message: 人类可读说明。
        owner: 后续 owner。
        next_gate: 下一步 gate。
        evidence_artifacts: 证据 artifact 路径。
    """

    code: str
    severity: BlockerSeverity
    scope: str
    fund_code: str | None
    message: str
    owner: str
    next_gate: str
    evidence_artifacts: tuple[Path, ...] = ()


@dataclass(frozen=True, slots=True)
class ResolvedReadinessItem:
    """已解除 readiness 项。

    Attributes:
        code: resolved taxonomy 代码。
        original_blocker_code: 原 blocker 代码。
        fund_code: 关联基金代码。
        message: 人类可读说明。
        evidence_artifacts: 证据 artifact 路径。
    """

    code: str
    original_blocker_code: str
    fund_code: str
    message: str
    evidence_artifacts: tuple[Path, ...] = ()


@dataclass(frozen=True, slots=True)
class FundArtifactInput:
    """单基金或 slot 的 preflight 输入。

    Attributes:
        fund_code: 基金代码或静态 slot id。
        report_year: 年报年份。
        snapshot_path: extraction snapshot JSONL 路径。
        score_path: extraction score JSON 路径。
        quality_gate_path: quality gate JSON 路径。
        score_golden_set_path: score 产出的 golden_set JSON 路径。
        promotion_state: fixture promotion 状态。
        raw_disposition: controller judgment 原始 disposition。
        preflight_disposition: preflight 归一化 disposition。
        coverage_owner: coverage owner。
        next_gate: 下一步 gate。
        evidence_artifacts: accepted evidence artifacts。
    """

    fund_code: str
    report_year: int
    snapshot_path: Path | None
    score_path: Path | None
    quality_gate_path: Path | None
    score_golden_set_path: Path | None = None
    promotion_state: PromotionState = "not_promoted"
    raw_disposition: str | None = None
    preflight_disposition: PreflightDisposition = "unknown"
    coverage_owner: str = "future baseline/golden preflight owner"
    next_gate: str = "fixture promotion / strict golden coverage gate"
    evidence_artifacts: tuple[Path, ...] = ()


@dataclass(frozen=True, slots=True)
class CoverageDispositionEntry:
    """当前 accepted coverage disposition manifest 条目。

    Attributes:
        fund_code: 基金代码或 slot id。
        report_year: 年报年份。
        raw_disposition: controller judgment 原始 disposition。
        preflight_disposition: preflight 归一化 disposition。
        promotion_state: 当前 promotion 状态。
        coverage_owner: coverage owner。
        next_gate: 下一步 gate。
        blocks_v1: 是否阻断 baseline/golden v1 promotion。
        evidence_artifacts: accepted evidence artifacts。
        snapshot_path: 默认 snapshot artifact。
        score_path: 默认 score artifact。
        quality_gate_path: 默认 quality gate artifact。
        score_golden_set_path: 默认 golden_set artifact。
        artifact_required: 是否要求三类运行 artifact 存在。
        slot_kind: slot 类型。
        lifecycle_note: 静态 manifest 生命周期说明。
    """

    fund_code: str
    report_year: int
    raw_disposition: str
    preflight_disposition: PreflightDisposition
    promotion_state: PromotionState
    coverage_owner: str
    next_gate: str
    blocks_v1: bool
    evidence_artifacts: tuple[Path, ...]
    snapshot_path: Path | None = None
    score_path: Path | None = None
    quality_gate_path: Path | None = None
    score_golden_set_path: Path | None = None
    artifact_required: bool = True
    slot_kind: str = "fund"
    lifecycle_note: str = "static current accepted disposition; replace with tracked manifest on change"


@dataclass(frozen=True, slots=True)
class CoverageDispositionManifest:
    """当前 accepted coverage disposition manifest。

    Attributes:
        schema_version: manifest schema 版本。
        accepted_as_of: accepted 状态日期。
        source_artifacts: manifest 来源 controller artifacts。
        entries: disposition 条目。
        lifecycle_semantics: 静态 manifest 退出条件。
    """

    schema_version: str
    accepted_as_of: str
    source_artifacts: tuple[Path, ...]
    entries: tuple[CoverageDispositionEntry, ...]
    lifecycle_semantics: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class GoldenReadinessInput:
    """Golden readiness preflight 显式输入。

    Attributes:
        source_csv: 精选基金池 CSV 路径。
        output_dir: 输出目录。
        run_id: 运行 ID。
        fund_artifacts: 单基金或 slot artifact 输入。
        golden_answer_path: strict golden answer JSON 路径。
        fixture_promotion_state_path: fixture promotion state JSON 路径。
        coverage_disposition_path: coverage disposition manifest JSON 路径。
        preflight_input_path: 完整 preflight input JSON 路径。
        selected_pool_path: selected pool JSON 路径。
    """

    source_csv: Path
    output_dir: Path
    run_id: str
    fund_artifacts: tuple[FundArtifactInput, ...]
    golden_answer_path: Path | None
    fixture_promotion_state_path: Path | None
    coverage_disposition_path: Path | None
    preflight_input_path: Path | None = None
    selected_pool_path: Path | None = None


@dataclass(frozen=True, slots=True)
class FundReadinessRow:
    """单基金或 slot readiness 输出行。

    Attributes:
        fund_code: 基金代码或 slot id。
        report_year: 年报年份。
        fund_name: 基金名称。
        app_category: 应用类别。
        classified_fund_type: 分类基金类型。
        readiness: readiness 状态。
        promotion_state: promotion 状态。
        source_provenance_status: source provenance 状态。
        fallback_eligibility: fallback eligibility。
        quality_gate_status: quality gate 状态。
        strict_golden_coverage: strict golden fund-level coverage。
        fixture_promotion_state: fixture promotion state。
        raw_disposition: 原始 disposition。
        preflight_disposition: preflight disposition。
        blockers: blocker 列表。
        warnings: warning 列表。
        resolved_items: resolved item 列表。
        owner: owner。
        next_gate: 下一步 gate。
        evidence_artifacts: 证据 artifact 路径。
    """

    fund_code: str
    report_year: int
    fund_name: str | None
    app_category: str | None
    classified_fund_type: str | None
    readiness: ReadinessStatus
    promotion_state: PromotionState
    source_provenance_status: str
    fallback_eligibility: str
    quality_gate_status: str
    strict_golden_coverage: str
    fixture_promotion_state: str
    raw_disposition: str | None
    preflight_disposition: PreflightDisposition
    blockers: tuple[ReadinessBlocker, ...]
    warnings: tuple[ReadinessWarning, ...]
    resolved_items: tuple[ResolvedReadinessItem, ...]
    owner: str
    next_gate: str
    evidence_artifacts: tuple[Path, ...]


@dataclass(frozen=True, slots=True)
class GoldenReadinessPreflightResult:
    """Golden readiness preflight 输出。

    Attributes:
        schema_version: 输出 schema 版本。
        run_id: 运行 ID。
        generated_at: ISO-8601 生成时间。
        source_csv: 精选基金池 CSV 路径。
        golden_answer_path: strict golden answer JSON 路径。
        static_disposition_manifest: 当前静态 disposition manifest。
        overall_status: 全局状态。
        ready_count: ready 行数。
        blocked_count: blocked 行数。
        deferred_count: deferred 行数。
        not_evaluated_count: not_evaluated 行数。
        rows: per-fund/per-slot readiness 行。
        global_blockers: 全局 blocker。
        resolved_items: 全局 resolved item。
        blocking_questions: 需要 controller 回答的问题。
        json_path: JSON 输出路径。
        markdown_path: Markdown 输出路径。
    """

    schema_version: str
    run_id: str
    generated_at: str
    source_csv: Path
    golden_answer_path: Path | None
    static_disposition_manifest: CoverageDispositionManifest
    overall_status: PreflightOverallStatus
    ready_count: int
    blocked_count: int
    deferred_count: int
    not_evaluated_count: int
    rows: tuple[FundReadinessRow, ...]
    global_blockers: tuple[ReadinessBlocker, ...]
    resolved_items: tuple[ResolvedReadinessItem, ...]
    blocking_questions: tuple[str, ...]
    json_path: Path
    markdown_path: Path


@dataclass(frozen=True, slots=True)
class _SourceProvenanceSummary:
    """source provenance 派生结果。

    Attributes:
        status: provenance 状态。
        fallback_eligibility: fallback eligibility。
        blockers: provenance blocker。
        warnings: provenance warning。
    """

    status: str
    fallback_eligibility: str
    blockers: tuple[ReadinessBlocker, ...] = ()
    warnings: tuple[ReadinessWarning, ...] = ()


@dataclass(frozen=True, slots=True)
class _PromotionStateSummary:
    """fixture promotion 派生结果。

    Attributes:
        state: fixture promotion 输出状态。
        promotion_state: promotion enum。
        blockers: promotion blocker。
    """

    state: str
    promotion_state: PromotionState
    blockers: tuple[ReadinessBlocker, ...] = ()


def load_default_current_disposition_manifest() -> CoverageDispositionManifest:
    """加载代码内当前 accepted disposition manifest。

    Returns:
        当前静态 accepted coverage disposition manifest。

    Raises:
        无显式抛出。
    """

    source_artifacts = (
        _review_artifact(
            "release-maintenance-source-provenance-post-implementation-bounded-evidence-rerun-"
            "controller-judgment-20260527.md"
        ),
        _review_artifact(
            "release-maintenance-110020-reviewed-coverage-candidate-evidence-controller-judgment-"
            "20260527.md"
        ),
        _review_artifact(
            "release-maintenance-consolidation-post-021539-disposition-controller-judgment-"
            "20260527.md"
        ),
        _review_artifact(
            "release-maintenance-drawdown-stress-nav-derived-metric-controller-judgment-"
            "20260529.md"
        ),
    )
    return CoverageDispositionManifest(
        schema_version=STATIC_DISPOSITION_SCHEMA_VERSION,
        accepted_as_of=STATIC_DISPOSITION_ACCEPTED_AS_OF,
        source_artifacts=source_artifacts,
        lifecycle_semantics=(
            "任一 controller judgment 改变 coverage disposition、owner、revisit condition、"
            "blocks_v1 或 promotion disposition 时，停止扩展代码内 manifest。",
            "新 fund 加入候选池、已有 fund 移除、fixture promotion state 变更，必须开独立"
            " machine-readable disposition manifest gate。",
            "需要同时维护 3 个以上条目或跨多 gate 复用 disposition 数据时，产出 tracked JSON"
            " manifest 后再由 preflight 消费。",
        ),
        entries=(
            _entry(
                "004393",
                "evaluated_carry_forward_candidate",
                "include_for_later_review",
                "future baseline preflight owner",
                "fixture promotion / strict golden coverage gate",
                Path("reports/extraction-snapshots/small-baseline-corpus-v1-004393-2024"),
                evidence_artifacts=(source_artifacts[0],),
            ),
            _entry(
                "004194",
                "evaluated_carry_forward_candidate",
                "include_for_later_review",
                "future baseline preflight owner",
                "fixture promotion / strict golden coverage gate",
                Path("reports/extraction-snapshots/small-baseline-corpus-v1-004194-2024"),
                evidence_artifacts=(source_artifacts[0],),
            ),
            _entry(
                "017641",
                "source_provenance_complete_quality_block_not_promoted",
                "include_for_later_review",
                "future baseline preflight owner",
                "quality block disposition / fixture promotion gate",
                Path("reports/extraction-snapshots/source-provenance-rerun-017641-2024-20260527"),
                evidence_artifacts=(source_artifacts[0],),
            ),
            _entry(
                "006597",
                "bond_risk_evidence_resolved_not_promoted",
                "include_for_later_review",
                "future baseline/golden preflight owner",
                "fixture promotion / strict golden coverage gate",
                Path("reports/extraction-snapshots/bond-risk-drawdown-nav-006597-2024-20260529"),
                score_path=Path(
                    "reports/scoring-runs/bond-risk-drawdown-nav-006597-2024-20260529/score.json"
                ),
                quality_gate_path=Path(
                    "reports/quality-gate-runs/"
                    "bond-risk-drawdown-nav-006597-2024-20260529/quality_gate.json"
                ),
                evidence_artifacts=(source_artifacts[3],),
            ),
            _entry(
                "110020",
                "reviewed_coverage_candidate_input_accepted",
                "reviewed_coverage_candidate",
                "future index evidence sufficiency gate",
                "index reviewed fact freeze / methodology / constituents evidence gate",
                Path("reports/extraction-snapshots/110020-reviewed-coverage-candidate-2024-20260527"),
                evidence_artifacts=(source_artifacts[1],),
            ),
            _entry(
                "096001",
                "quality_blocked_after_provenance_hard_stop",
                "blocked",
                "future QDII diagnosis or taxonomy / asset-class fitness gate",
                "QDII diagnosis or explicit QDII deferred-from-v1 disposition gate",
                Path("reports/extraction-snapshots/qdii-replacement-candidate-096001-2024-20260527"),
                evidence_artifacts=(source_artifacts[2],),
            ),
            _entry(
                "040046",
                "quality_blocked_after_provenance_hard_stop",
                "blocked",
                "future QDII diagnosis or taxonomy / asset-class fitness gate",
                "QDII diagnosis or explicit QDII deferred-from-v1 disposition gate",
                Path("reports/extraction-snapshots/qdii-replacement-fallback-040046-2024-20260527"),
                evidence_artifacts=(source_artifacts[2],),
            ),
            _entry(
                "019172",
                "quality_blocked_after_provenance_hard_stop",
                "blocked",
                "future QDII diagnosis or taxonomy / asset-class fitness gate",
                "QDII diagnosis or explicit QDII deferred-from-v1 disposition gate",
                Path("reports/extraction-snapshots/qdii-replacement-fallback-019172-2024-20260527"),
                evidence_artifacts=(source_artifacts[2],),
            ),
            _entry(
                "021539",
                "quality_blocked_after_provenance_hard_stop",
                "blocked",
                "future QDII diagnosis or taxonomy / asset-class fitness gate",
                "QDII diagnosis or explicit QDII deferred-from-v1 disposition gate",
                Path("reports/extraction-snapshots/qdii-replacement-fallback-021539-2024-20260527"),
                evidence_artifacts=(source_artifacts[2],),
            ),
            CoverageDispositionEntry(
                fund_code="FOF_SLOT",
                report_year=DEFAULT_REPORT_YEAR,
                raw_disposition="data_gap_taxonomy_pending",
                preflight_disposition="needs_taxonomy_gate",
                promotion_state="not_promoted",
                coverage_owner="future FOF taxonomy / pure FOF candidate gate",
                next_gate="pure FOF repository-verified candidate gate",
                blocks_v1=True,
                evidence_artifacts=(source_artifacts[2],),
                artifact_required=False,
                slot_kind="fof_slot",
            ),
        ),
    )


def run_golden_readiness_preflight(
    *,
    source_csv: Path,
    output_dir: Path,
    run_id: str,
    fund_artifacts: Sequence[FundArtifactInput],
    golden_answer_path: Path | None,
    fixture_promotion_state_path: Path | None,
    coverage_disposition_path: Path | None,
    preflight_input_path: Path | None = None,
    selected_pool_path: Path | None = None,
) -> GoldenReadinessPreflightResult:
    """执行 golden readiness preflight。

    Args:
        source_csv: 精选基金池 CSV 路径。
        output_dir: 输出目录。
        run_id: 运行 ID。
        fund_artifacts: 单基金或 slot artifact 输入。
        golden_answer_path: strict golden answer JSON 路径。
        fixture_promotion_state_path: fixture promotion state JSON 路径。
        coverage_disposition_path: coverage disposition manifest JSON 路径。
        preflight_input_path: 完整 preflight input JSON 路径。
        selected_pool_path: selected pool JSON 路径。

    Returns:
        preflight 结果，并已写出 JSON / Markdown。

    Raises:
        ValueError: 输入 JSON schema 或 artifact JSON/JSONL 非法时抛出。
        OSError: 输出目录创建或文件写入失败时抛出。
    """

    request = GoldenReadinessInput(
        source_csv=source_csv,
        output_dir=output_dir,
        run_id=run_id,
        fund_artifacts=tuple(fund_artifacts),
        golden_answer_path=golden_answer_path,
        fixture_promotion_state_path=fixture_promotion_state_path,
        coverage_disposition_path=coverage_disposition_path,
        preflight_input_path=preflight_input_path,
        selected_pool_path=selected_pool_path,
    )
    if preflight_input_path is not None:
        request = _load_preflight_input(preflight_input_path)

    static_manifest = load_default_current_disposition_manifest()
    manifest = _load_coverage_disposition_manifest(
        request.coverage_disposition_path, default_manifest=static_manifest
    )
    artifacts = _complete_fund_artifacts(request.fund_artifacts, manifest)
    global_blockers = _derive_global_blockers(
        source_csv=request.source_csv,
        golden_answer_path=request.golden_answer_path,
        fixture_promotion_state_path=request.fixture_promotion_state_path,
    )
    golden_covered_funds = _load_strict_golden_covered_funds(request.golden_answer_path)
    fixture_states = _load_fixture_promotion_states(request.fixture_promotion_state_path)
    rows = tuple(
        _build_readiness_row(
            artifact,
            manifest=manifest,
            golden_answer_path=request.golden_answer_path,
            golden_covered_funds=golden_covered_funds,
            fixture_promotion_state_path=request.fixture_promotion_state_path,
            fixture_states=fixture_states,
        )
        for artifact in artifacts
    )
    global_blockers = tuple(global_blockers) + _derive_manifest_global_blockers(rows, manifest)
    all_resolved_items = tuple(item for row in rows for item in row.resolved_items)
    overall_status: PreflightOverallStatus = (
        "block"
        if global_blockers
        or any(row.readiness in {"blocked", "not_evaluated"} for row in rows)
        or any(_row_blocks_v1(row, manifest) for row in rows)
        else "pass"
    )
    result = GoldenReadinessPreflightResult(
        schema_version=OUTPUT_SCHEMA_VERSION,
        run_id=request.run_id,
        generated_at=datetime.now(UTC).isoformat(),
        source_csv=request.source_csv,
        golden_answer_path=request.golden_answer_path,
        static_disposition_manifest=static_manifest,
        overall_status=overall_status,
        ready_count=sum(1 for row in rows if row.readiness == "ready"),
        blocked_count=sum(1 for row in rows if row.readiness == "blocked"),
        deferred_count=sum(1 for row in rows if row.readiness == "deferred_with_owner"),
        not_evaluated_count=sum(1 for row in rows if row.readiness == "not_evaluated"),
        rows=rows,
        global_blockers=global_blockers,
        resolved_items=all_resolved_items,
        blocking_questions=_derive_blocking_questions(rows, global_blockers),
        json_path=request.output_dir / "golden_readiness_preflight.json",
        markdown_path=request.output_dir / "golden_readiness_preflight.md",
    )
    _write_outputs(result)
    return result


def _review_artifact(filename: str) -> Path:
    """构造 docs/reviews 下的 accepted artifact 路径。

    Args:
        filename: `docs/reviews` 下的文件名。

    Returns:
        artifact 路径。

    Raises:
        无显式抛出。
    """

    return Path("docs") / "reviews" / filename


def _entry(
    fund_code: str,
    raw_disposition: str,
    preflight_disposition: PreflightDisposition,
    coverage_owner: str,
    next_gate: str,
    artifact_dir: Path,
    *,
    score_path: Path | None = None,
    quality_gate_path: Path | None = None,
    evidence_artifacts: tuple[Path, ...] = (),
) -> CoverageDispositionEntry:
    """构造静态 manifest 中常规基金条目。

    Args:
        fund_code: 基金代码。
        raw_disposition: 原始 disposition。
        preflight_disposition: preflight disposition。
        coverage_owner: coverage owner。
        next_gate: 下一步 gate。
        artifact_dir: 默认 artifact 目录。
        score_path: 覆盖默认 score 路径。
        quality_gate_path: 覆盖默认 quality gate 路径。
        evidence_artifacts: 证据 artifact。

    Returns:
        coverage disposition entry。

    Raises:
        无显式抛出。
    """

    return CoverageDispositionEntry(
        fund_code=fund_code,
        report_year=DEFAULT_REPORT_YEAR,
        raw_disposition=raw_disposition,
        preflight_disposition=preflight_disposition,
        promotion_state="not_promoted",
        coverage_owner=coverage_owner,
        next_gate=next_gate,
        blocks_v1=True,
        evidence_artifacts=evidence_artifacts,
        snapshot_path=artifact_dir / "snapshot.jsonl",
        score_path=score_path or artifact_dir / "score.json",
        quality_gate_path=quality_gate_path or artifact_dir / "quality_gate.json",
        score_golden_set_path=artifact_dir / "golden_set.json",
    )


def _load_preflight_input(path: Path) -> GoldenReadinessInput:
    """读取 production recommended preflight input JSON。

    Args:
        path: preflight input JSON 路径。

    Returns:
        解析后的显式输入对象。

    Raises:
        ValueError: schema_version、未知字段或字段类型非法时抛出。
    """

    payload = _load_json_object(path)
    allowed_keys = {
        "schema_version",
        "run_id",
        "source_csv",
        "selected_pool_path",
        "golden_answer_path",
        "fixture_promotion_state_path",
        "coverage_disposition_path",
        "output_dir",
        "fund_artifacts",
    }
    _reject_unknown_keys(payload, allowed_keys, "preflight input")
    if payload.get("schema_version") != INPUT_SCHEMA_VERSION:
        raise ValueError(f"preflight_input schema_version 必须是 {INPUT_SCHEMA_VERSION}")
    fund_artifacts = payload.get("fund_artifacts")
    if not isinstance(fund_artifacts, list):
        raise ValueError("preflight_input fund_artifacts 必须是数组")
    return GoldenReadinessInput(
        source_csv=_path_from_json(payload, "source_csv", required=True) or Path(),
        output_dir=_path_from_json(payload, "output_dir", required=True) or Path(),
        run_id=_str_from_json(payload, "run_id", required=True) or "",
        fund_artifacts=tuple(_fund_artifact_from_json(item) for item in fund_artifacts),
        golden_answer_path=_path_from_json(payload, "golden_answer_path", required=False),
        fixture_promotion_state_path=_path_from_json(
            payload, "fixture_promotion_state_path", required=False
        ),
        coverage_disposition_path=_path_from_json(
            payload, "coverage_disposition_path", required=False
        ),
        preflight_input_path=path,
        selected_pool_path=_path_from_json(payload, "selected_pool_path", required=False),
    )


def _fund_artifact_from_json(payload: object) -> FundArtifactInput:
    """解析单项 fund artifact JSON。

    Args:
        payload: 单项 artifact JSON object。

    Returns:
        fund artifact input。

    Raises:
        ValueError: 字段缺失、未知字段或类型非法时抛出。
    """

    if not isinstance(payload, dict):
        raise ValueError("fund_artifacts 每项必须是 object")
    item = cast(dict[str, object], payload)
    allowed_keys = {
        "fund_code",
        "report_year",
        "snapshot_path",
        "score_path",
        "quality_gate_path",
        "score_golden_set_path",
        "promotion_state",
        "raw_disposition",
        "preflight_disposition",
        "coverage_owner",
        "next_gate",
        "evidence_artifacts",
    }
    _reject_unknown_keys(item, allowed_keys, "fund artifact")
    for required_key in ("fund_code", "report_year", "snapshot_path", "score_path", "quality_gate_path"):
        if required_key not in item:
            raise ValueError(f"fund artifact 缺少字段：{required_key}")
    evidence_artifacts = item.get("evidence_artifacts", [])
    if not isinstance(evidence_artifacts, list) or not all(
        isinstance(value, str) for value in evidence_artifacts
    ):
        raise ValueError("fund artifact evidence_artifacts 必须是字符串数组")
    promotion_state = item.get("promotion_state", "not_promoted")
    if promotion_state not in {"not_promoted", "promoted_fixture", "unknown"}:
        raise ValueError("fund artifact promotion_state 非法")
    preflight_disposition = item.get("preflight_disposition", "unknown")
    if preflight_disposition not in _allowed_preflight_dispositions():
        raise ValueError("fund artifact preflight_disposition 非法")
    report_year = item.get("report_year")
    if not isinstance(report_year, int):
        raise ValueError("fund artifact report_year 必须是整数")
    return FundArtifactInput(
        fund_code=_str_from_json(item, "fund_code", required=True) or "",
        report_year=report_year,
        snapshot_path=_path_from_json(item, "snapshot_path", required=False),
        score_path=_path_from_json(item, "score_path", required=False),
        quality_gate_path=_path_from_json(item, "quality_gate_path", required=False),
        score_golden_set_path=_path_from_json(item, "score_golden_set_path", required=False),
        promotion_state=cast(PromotionState, promotion_state),
        raw_disposition=cast(str | None, item.get("raw_disposition")),
        preflight_disposition=cast(PreflightDisposition, preflight_disposition),
        coverage_owner=_str_from_json(item, "coverage_owner", required=False)
        or "future baseline/golden preflight owner",
        next_gate=_str_from_json(item, "next_gate", required=False)
        or "fixture promotion / strict golden coverage gate",
        evidence_artifacts=tuple(Path(value) for value in evidence_artifacts),
    )


def _reject_unknown_keys(payload: Mapping[str, object], allowed_keys: set[str], label: str) -> None:
    """拒绝未知字段，防止形成隐式 extra payload。

    Args:
        payload: JSON object。
        allowed_keys: 允许字段集合。
        label: 错误消息标签。

    Returns:
        无返回值。

    Raises:
        ValueError: 发现未知字段时抛出。
    """

    unknown_keys = set(payload) - allowed_keys
    if unknown_keys:
        raise ValueError(f"{label} 含未知字段：{', '.join(sorted(unknown_keys))}")


def _path_from_json(payload: Mapping[str, object], key: str, *, required: bool) -> Path | None:
    """从 JSON object 读取路径字段。

    Args:
        payload: JSON object。
        key: 字段名。
        required: 是否必填。

    Returns:
        Path 或 None。

    Raises:
        ValueError: 必填缺失或类型非法时抛出。
    """

    if key not in payload or payload[key] is None:
        if required:
            raise ValueError(f"缺少路径字段：{key}")
        return None
    value = payload[key]
    if not isinstance(value, str):
        raise ValueError(f"{key} 必须是字符串或 null")
    return Path(value)


def _str_from_json(payload: Mapping[str, object], key: str, *, required: bool) -> str | None:
    """从 JSON object 读取字符串字段。

    Args:
        payload: JSON object。
        key: 字段名。
        required: 是否必填。

    Returns:
        字符串或 None。

    Raises:
        ValueError: 必填缺失或类型非法时抛出。
    """

    if key not in payload or payload[key] is None:
        if required:
            raise ValueError(f"缺少字符串字段：{key}")
        return None
    value = payload[key]
    if not isinstance(value, str):
        raise ValueError(f"{key} 必须是字符串")
    return value


def _allowed_preflight_dispositions() -> set[str]:
    """返回允许的 preflight disposition。

    Returns:
        允许值集合。

    Raises:
        无显式抛出。
    """

    return {
        "reviewed_coverage_candidate",
        "include_for_later_review",
        "replace",
        "needs_taxonomy_gate",
        "needs_evidence_gate",
        "blocked",
        "deferred",
        "unknown",
    }


def _load_coverage_disposition_manifest(
    path: Path | None, *, default_manifest: CoverageDispositionManifest
) -> CoverageDispositionManifest:
    """读取 coverage disposition manifest。

    当前 gate 没有 tracked manifest 时使用代码内静态 accepted-current-state manifest。

    Args:
        path: manifest JSON 路径。
        default_manifest: 静态默认 manifest。

    Returns:
        coverage disposition manifest。

    Raises:
        ValueError: 传入 manifest 非法时抛出。
    """

    if path is None:
        return default_manifest
    payload = _load_json_object(path)
    allowed_keys = {
        "schema_version",
        "accepted_as_of",
        "source_artifacts",
        "entries",
        "lifecycle_semantics",
    }
    _reject_unknown_keys(payload, allowed_keys, "coverage disposition manifest")
    if payload.get("schema_version") != STATIC_DISPOSITION_SCHEMA_VERSION:
        raise ValueError(
            f"coverage_disposition schema_version 必须是 {STATIC_DISPOSITION_SCHEMA_VERSION}"
        )
    source_artifacts = _path_tuple_from_json(payload, "source_artifacts")
    entries = payload.get("entries")
    if not isinstance(entries, list):
        raise ValueError("coverage_disposition entries 必须是数组")
    lifecycle_semantics = payload.get("lifecycle_semantics", ())
    if not isinstance(lifecycle_semantics, list) or not all(
        isinstance(item, str) for item in lifecycle_semantics
    ):
        raise ValueError("coverage_disposition lifecycle_semantics 必须是字符串数组")
    return CoverageDispositionManifest(
        schema_version=STATIC_DISPOSITION_SCHEMA_VERSION,
        accepted_as_of=_str_from_json(payload, "accepted_as_of", required=True) or "",
        source_artifacts=source_artifacts,
        entries=tuple(_coverage_entry_from_json(item) for item in entries),
        lifecycle_semantics=tuple(lifecycle_semantics),
    )


def _coverage_entry_from_json(payload: object) -> CoverageDispositionEntry:
    """解析 coverage disposition manifest entry。

    Args:
        payload: 单项 entry JSON object。

    Returns:
        coverage disposition entry。

    Raises:
        ValueError: 字段缺失或非法时抛出。
    """

    if not isinstance(payload, dict):
        raise ValueError("coverage disposition entries 每项必须是 object")
    item = cast(dict[str, object], payload)
    allowed_keys = {
        "fund_code",
        "report_year",
        "raw_disposition",
        "preflight_disposition",
        "promotion_state",
        "coverage_owner",
        "next_gate",
        "blocks_v1",
        "evidence_artifacts",
        "snapshot_path",
        "score_path",
        "quality_gate_path",
        "score_golden_set_path",
        "artifact_required",
        "slot_kind",
        "lifecycle_note",
    }
    _reject_unknown_keys(item, allowed_keys, "coverage disposition entry")
    report_year = item.get("report_year")
    blocks_v1 = item.get("blocks_v1")
    artifact_required = item.get("artifact_required", True)
    if not isinstance(report_year, int):
        raise ValueError("coverage disposition entry report_year 必须是整数")
    if not isinstance(blocks_v1, bool):
        raise ValueError("coverage disposition entry blocks_v1 必须是 bool")
    if not isinstance(artifact_required, bool):
        raise ValueError("coverage disposition entry artifact_required 必须是 bool")
    promotion_state = item.get("promotion_state", "not_promoted")
    preflight_disposition = item.get("preflight_disposition", "unknown")
    if promotion_state not in {"not_promoted", "promoted_fixture", "unknown"}:
        raise ValueError("coverage disposition entry promotion_state 非法")
    if preflight_disposition not in _allowed_preflight_dispositions():
        raise ValueError("coverage disposition entry preflight_disposition 非法")
    return CoverageDispositionEntry(
        fund_code=_str_from_json(item, "fund_code", required=True) or "",
        report_year=report_year,
        raw_disposition=_str_from_json(item, "raw_disposition", required=True) or "",
        preflight_disposition=cast(PreflightDisposition, preflight_disposition),
        promotion_state=cast(PromotionState, promotion_state),
        coverage_owner=_str_from_json(item, "coverage_owner", required=True) or "",
        next_gate=_str_from_json(item, "next_gate", required=True) or "",
        blocks_v1=blocks_v1,
        evidence_artifacts=_path_tuple_from_json(item, "evidence_artifacts"),
        snapshot_path=_path_from_json(item, "snapshot_path", required=False),
        score_path=_path_from_json(item, "score_path", required=False),
        quality_gate_path=_path_from_json(item, "quality_gate_path", required=False),
        score_golden_set_path=_path_from_json(item, "score_golden_set_path", required=False),
        artifact_required=artifact_required,
        slot_kind=_str_from_json(item, "slot_kind", required=False) or "fund",
        lifecycle_note=_str_from_json(item, "lifecycle_note", required=False)
        or "tracked disposition manifest entry",
    )


def _path_tuple_from_json(payload: Mapping[str, object], key: str) -> tuple[Path, ...]:
    """从 JSON object 读取路径数组。

    Args:
        payload: JSON object。
        key: 字段名。

    Returns:
        路径元组。

    Raises:
        ValueError: 字段不是字符串数组时抛出。
    """

    value = payload.get(key, [])
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise ValueError(f"{key} 必须是字符串数组")
    return tuple(Path(item) for item in value)


def _complete_fund_artifacts(
    fund_artifacts: tuple[FundArtifactInput, ...], manifest: CoverageDispositionManifest
) -> tuple[FundArtifactInput, ...]:
    """用 manifest 补全输入 artifact。

    Args:
        fund_artifacts: 用户显式输入 artifact。
        manifest: coverage disposition manifest。

    Returns:
        补全后的 artifact 元组。

    Raises:
        无显式抛出。
    """

    entries_by_key = {
        (entry.fund_code, entry.report_year): entry for entry in manifest.entries
    }
    if not fund_artifacts:
        return tuple(_artifact_from_entry(entry) for entry in manifest.entries)
    completed: list[FundArtifactInput] = []
    for artifact in fund_artifacts:
        entry = entries_by_key.get((artifact.fund_code, artifact.report_year))
        if entry is None:
            completed.append(artifact)
            continue
        completed.append(
            FundArtifactInput(
                fund_code=artifact.fund_code,
                report_year=artifact.report_year,
                snapshot_path=artifact.snapshot_path or entry.snapshot_path,
                score_path=artifact.score_path or entry.score_path,
                quality_gate_path=artifact.quality_gate_path or entry.quality_gate_path,
                score_golden_set_path=artifact.score_golden_set_path or entry.score_golden_set_path,
                promotion_state=artifact.promotion_state,
                raw_disposition=artifact.raw_disposition or entry.raw_disposition,
                preflight_disposition=(
                    entry.preflight_disposition
                    if artifact.preflight_disposition == "unknown"
                    else artifact.preflight_disposition
                ),
                coverage_owner=artifact.coverage_owner or entry.coverage_owner,
                next_gate=artifact.next_gate or entry.next_gate,
                evidence_artifacts=artifact.evidence_artifacts or entry.evidence_artifacts,
            )
        )
    return tuple(completed)


def _artifact_from_entry(entry: CoverageDispositionEntry) -> FundArtifactInput:
    """从 manifest entry 构造默认 fund artifact。

    Args:
        entry: coverage disposition entry。

    Returns:
        fund artifact input。

    Raises:
        无显式抛出。
    """

    return FundArtifactInput(
        fund_code=entry.fund_code,
        report_year=entry.report_year,
        snapshot_path=entry.snapshot_path,
        score_path=entry.score_path,
        quality_gate_path=entry.quality_gate_path,
        score_golden_set_path=entry.score_golden_set_path,
        promotion_state=entry.promotion_state,
        raw_disposition=entry.raw_disposition,
        preflight_disposition=entry.preflight_disposition,
        coverage_owner=entry.coverage_owner,
        next_gate=entry.next_gate,
        evidence_artifacts=entry.evidence_artifacts,
    )


def _derive_global_blockers(
    *,
    source_csv: Path,
    golden_answer_path: Path | None,
    fixture_promotion_state_path: Path | None,
) -> tuple[ReadinessBlocker, ...]:
    """派生全局 artifact blocker。

    Args:
        source_csv: 精选基金池 CSV 路径。
        golden_answer_path: strict golden answer JSON 路径。
        fixture_promotion_state_path: fixture promotion state JSON 路径。

    Returns:
        全局 blocker 元组。

    Raises:
        无显式抛出。
    """

    blockers: list[ReadinessBlocker] = []
    if not source_csv.exists():
        blockers.append(
            _blocker(
                "missing_input_artifact",
                "global",
                None,
                f"source_csv 缺失：{source_csv}",
                "preflight input owner",
                "provide repository selected pool source CSV",
            )
        )
    if golden_answer_path is None or not golden_answer_path.exists():
        blockers.append(
            _blocker(
                "strict_golden_not_configured",
                "global",
                None,
                "strict golden answer JSON 缺失或未配置。",
                "future strict golden coverage gate",
                "provide accepted strict golden answer v1 JSON",
            )
        )
    if fixture_promotion_state_path is None:
        blockers.append(
            _blocker(
                "fixture_promotion_absent",
                "global",
                None,
                "未提供 accepted fixture promotion state manifest。",
                "future fixture promotion gate",
                "produce accepted fixture promotion state manifest",
            )
        )
    elif not fixture_promotion_state_path.exists():
        blockers.append(
            _blocker(
                "fixture_promotion_absent",
                "global",
                None,
                f"fixture promotion state manifest 缺失：{fixture_promotion_state_path}",
                "future fixture promotion gate",
                "produce accepted fixture promotion state manifest",
            )
        )
    return tuple(blockers)


def _load_strict_golden_covered_funds(path: Path | None) -> set[str] | None:
    """读取 strict golden answer v1 已覆盖基金代码。

    Args:
        path: strict golden answer JSON 路径。

    Returns:
        已覆盖基金代码集合；未配置或缺失时返回 None。

    Raises:
        ValueError: JSON 非 object 或 `funds` 结构非法时抛出。
    """

    if path is None or not path.exists():
        return None
    payload = _load_json_object(path)
    funds = payload.get("funds")
    if not isinstance(funds, list):
        raise ValueError("strict golden answer funds 必须是数组")
    covered_funds: set[str] = set()
    for fund in funds:
        if not isinstance(fund, dict):
            raise ValueError("strict golden answer funds 每项必须是 object")
        fund_code = fund.get("fund_code")
        if not isinstance(fund_code, str):
            raise ValueError("strict golden answer funds[].fund_code 必须是字符串")
        records = fund.get("records", [])
        if not isinstance(records, list):
            raise ValueError("strict golden answer funds[].records 必须是数组")
        covered_funds.add(fund_code)
    return covered_funds


def _load_fixture_promotion_states(path: Path | None) -> dict[str, PromotionState] | None:
    """读取 fixture promotion state manifest。

    Args:
        path: fixture promotion state JSON 路径。

    Returns:
        fund_code 到 promotion state 的映射；未提供时返回 None。

    Raises:
        ValueError: JSON 结构非法时抛出。
    """

    if path is None or not path.exists():
        return None
    payload = _load_json_object(path)
    entries = payload.get("entries")
    if isinstance(entries, list):
        states: dict[str, PromotionState] = {}
        for entry in entries:
            if not isinstance(entry, dict):
                raise ValueError("fixture promotion entries 每项必须是 object")
            fund_code = entry.get("fund_code")
            promotion_state = entry.get("promotion_state")
            if not isinstance(fund_code, str) or promotion_state not in {
                "not_promoted",
                "promoted_fixture",
                "unknown",
            }:
                raise ValueError("fixture promotion entry fund_code/promotion_state 非法")
            states[fund_code] = cast(PromotionState, promotion_state)
        return states
    if all(
        isinstance(key, str) and value in {"not_promoted", "promoted_fixture", "unknown"}
        for key, value in payload.items()
    ):
        return {key: cast(PromotionState, value) for key, value in payload.items()}
    raise ValueError("fixture promotion state manifest 必须包含 entries 或 fund_code->state 映射")


def _build_readiness_row(
    artifact: FundArtifactInput,
    *,
    manifest: CoverageDispositionManifest,
    golden_answer_path: Path | None,
    golden_covered_funds: set[str] | None,
    fixture_promotion_state_path: Path | None,
    fixture_states: dict[str, PromotionState] | None,
) -> FundReadinessRow:
    """构造单基金或 slot readiness 行。

    Args:
        artifact: 单基金或 slot artifact 输入。
        manifest: coverage disposition manifest。
        golden_answer_path: strict golden answer JSON 路径。
        golden_covered_funds: strict golden v1 已覆盖基金集合。
        fixture_promotion_state_path: fixture promotion state JSON 路径。
        fixture_states: fixture promotion 状态映射。

    Returns:
        readiness row。

    Raises:
        ValueError: artifact JSON/JSONL 文件存在但内容非法时抛出。
    """

    entry = _find_manifest_entry(manifest, artifact.fund_code, artifact.report_year)
    artifact_required = True if entry is None else entry.artifact_required
    blockers: list[ReadinessBlocker] = []
    warnings: list[ReadinessWarning] = []
    resolved_items: list[ResolvedReadinessItem] = []
    snapshot_rows: tuple[Mapping[str, object], ...] = ()
    score_payload: dict[str, object] | None = None
    quality_payload: dict[str, object] | None = None

    if artifact_required:
        blockers.extend(_missing_artifact_blockers(artifact))
    if artifact.snapshot_path is not None and artifact.snapshot_path.exists():
        snapshot_rows = _load_snapshot_rows(artifact.snapshot_path)
    if artifact.score_path is not None and artifact.score_path.exists():
        score_payload = _load_json_object(artifact.score_path)
    if artifact.quality_gate_path is not None and artifact.quality_gate_path.exists():
        quality_payload = _load_json_object(artifact.quality_gate_path)

    identity = _derive_identity(artifact, snapshot_rows, score_payload)
    source_summary = _derive_source_provenance_state(
        snapshot_rows,
        fund_code=artifact.fund_code,
        owner=artifact.coverage_owner,
        next_gate=artifact.next_gate,
        evidence_artifacts=artifact.evidence_artifacts,
    )
    blockers.extend(source_summary.blockers)
    warnings.extend(source_summary.warnings)
    if score_payload is not None:
        blockers.extend(_derive_score_blockers(score_payload, artifact))
        blockers.extend(_derive_score_correctness_blockers(score_payload, artifact, golden_answer_path))
    if quality_payload is not None:
        quality_blockers, quality_warnings = _derive_quality_blockers(quality_payload, artifact)
        blockers.extend(quality_blockers)
        warnings.extend(quality_warnings)
    strict_golden_coverage, strict_blockers = _derive_strict_golden_coverage(
        artifact=artifact,
        golden_covered_funds=golden_covered_funds,
        golden_answer_path=golden_answer_path,
    )
    blockers.extend(strict_blockers)
    fixture_summary = _derive_fixture_promotion_state(
        artifact=artifact,
        fixture_promotion_state_path=fixture_promotion_state_path,
        fixture_states=fixture_states,
    )
    blockers.extend(fixture_summary.blockers)
    disposition_blockers = _derive_coverage_disposition_blockers(artifact, entry)
    blockers.extend(disposition_blockers)
    if artifact.fund_code == "006597":
        resolved_items.extend(
            _derive_006597_bond_resolved_items(score_payload, quality_payload, artifact)
        )

    readiness = _aggregate_readiness(
        blockers=tuple(blockers),
        artifact_required=artifact_required,
        preflight_disposition=artifact.preflight_disposition,
    )
    return FundReadinessRow(
        fund_code=artifact.fund_code,
        report_year=artifact.report_year,
        fund_name=identity["fund_name"],
        app_category=identity["app_category"],
        classified_fund_type=identity["classified_fund_type"],
        readiness=readiness,
        promotion_state=fixture_summary.promotion_state,
        source_provenance_status=source_summary.status,
        fallback_eligibility=source_summary.fallback_eligibility,
        quality_gate_status=_quality_gate_status(quality_payload),
        strict_golden_coverage=strict_golden_coverage,
        fixture_promotion_state=fixture_summary.state,
        raw_disposition=artifact.raw_disposition,
        preflight_disposition=artifact.preflight_disposition,
        blockers=tuple(blockers),
        warnings=tuple(warnings),
        resolved_items=tuple(resolved_items),
        owner=artifact.coverage_owner,
        next_gate=artifact.next_gate,
        evidence_artifacts=artifact.evidence_artifacts,
    )


def _find_manifest_entry(
    manifest: CoverageDispositionManifest, fund_code: str, report_year: int
) -> CoverageDispositionEntry | None:
    """查找 manifest entry。

    Args:
        manifest: coverage disposition manifest。
        fund_code: 基金代码或 slot id。
        report_year: 年报年份。

    Returns:
        匹配 entry 或 None。

    Raises:
        无显式抛出。
    """

    for entry in manifest.entries:
        if entry.fund_code == fund_code and entry.report_year == report_year:
            return entry
    return None


def _missing_artifact_blockers(artifact: FundArtifactInput) -> tuple[ReadinessBlocker, ...]:
    """派生缺失输入 artifact blocker。

    Args:
        artifact: 单基金 artifact 输入。

    Returns:
        缺失 artifact blocker。

    Raises:
        无显式抛出。
    """

    required_paths = {
        "snapshot_path": artifact.snapshot_path,
        "score_path": artifact.score_path,
        "quality_gate_path": artifact.quality_gate_path,
    }
    blockers = []
    for field_name, path in required_paths.items():
        if path is None or not path.exists():
            blockers.append(
                _blocker(
                    "missing_input_artifact",
                    "fund",
                    artifact.fund_code,
                    f"{artifact.fund_code} {field_name} 缺失或不可读：{path}",
                    artifact.coverage_owner,
                    artifact.next_gate,
                    artifact.evidence_artifacts,
                )
            )
    return tuple(blockers)


def _derive_identity(
    artifact: FundArtifactInput,
    snapshot_rows: tuple[Mapping[str, object], ...],
    score_payload: dict[str, object] | None,
) -> dict[str, str | None]:
    """从 snapshot/score 派生基金身份字段。

    Args:
        artifact: 单基金 artifact 输入。
        snapshot_rows: snapshot JSONL 行。
        score_payload: score JSON payload。

    Returns:
        fund_name、app_category、classified_fund_type 字段。

    Raises:
        无显式抛出。
    """

    for row in snapshot_rows:
        if row.get("fund_code") == artifact.fund_code or artifact.fund_code == "FOF_SLOT":
            return {
                "fund_name": _optional_str(row.get("fund_name")),
                "app_category": _optional_str(row.get("app_category")),
                "classified_fund_type": _optional_str(row.get("classified_fund_type")),
            }
    if score_payload is not None:
        for key in ("fund_quality", "fund_scores"):
            records = score_payload.get(key)
            if isinstance(records, list):
                for record in records:
                    if isinstance(record, dict) and record.get("fund_code") == artifact.fund_code:
                        return {
                            "fund_name": _optional_str(record.get("fund_name")),
                            "app_category": _optional_str(record.get("app_category")),
                            "classified_fund_type": _optional_str(
                                record.get("classified_fund_type")
                            ),
                        }
    if artifact.fund_code == "FOF_SLOT":
        return {
            "fund_name": "Pure FOF coverage slot",
            "app_category": "FOF",
            "classified_fund_type": "fof_fund",
        }
    return {"fund_name": None, "app_category": None, "classified_fund_type": None}


def _optional_str(value: object) -> str | None:
    """把 object 安全转换为可选字符串。

    Args:
        value: 待转换值。

    Returns:
        字符串或 None。

    Raises:
        无显式抛出。
    """

    return value if isinstance(value, str) else None


def _derive_source_provenance_state(
    snapshot_rows: tuple[Mapping[str, object], ...],
    *,
    fund_code: str,
    owner: str,
    next_gate: str,
    evidence_artifacts: tuple[Path, ...],
) -> _SourceProvenanceSummary:
    """派生 source provenance readiness 状态。

    Args:
        snapshot_rows: snapshot JSONL 行。
        fund_code: 基金代码或 slot id。
        owner: owner。
        next_gate: 下一步 gate。
        evidence_artifacts: 证据 artifact。

    Returns:
        source provenance summary。

    Raises:
        无显式抛出。
    """

    if not snapshot_rows:
        return _SourceProvenanceSummary("not_evaluated", "not_evaluated")
    fallback_rows = [row for row in snapshot_rows if row.get("fallback_used") is True]
    if not fallback_rows:
        return _SourceProvenanceSummary("not_applicable", "not_applicable")
    categories = {row.get("primary_failure_category") for row in fallback_rows}
    eligibilities = {row.get("fallback_eligibility") for row in fallback_rows}
    status = _optional_str(fallback_rows[0].get("source_provenance_status")) or "unknown"
    fallback_eligibility = _optional_str(fallback_rows[0].get("fallback_eligibility")) or "unknown"
    if None in categories or "unknown" in eligibilities or None in eligibilities:
        return _SourceProvenanceSummary(
            status,
            fallback_eligibility,
            blockers=(
                _blocker(
                    "source_provenance_unknown",
                    "fund",
                    fund_code,
                    f"{fund_code} 使用 fallback 但 provenance category/eligibility 不完整。",
                    owner,
                    next_gate,
                    evidence_artifacts,
                ),
            ),
        )
    if any(category in INELIGIBLE_FALLBACK_FAILURE_CATEGORIES for category in categories) or any(
        eligibility != "eligible" for eligibility in eligibilities
    ):
        return _SourceProvenanceSummary(
            status,
            fallback_eligibility,
            blockers=(
                _blocker(
                    "source_provenance_ineligible",
                    "fund",
                    fund_code,
                    f"{fund_code} fallback provenance 不符合 fail-closed 规则。",
                    owner,
                    next_gate,
                    evidence_artifacts,
                ),
            ),
        )
    if all(category in ELIGIBLE_FALLBACK_FAILURE_CATEGORIES for category in categories):
        return _SourceProvenanceSummary(
            status,
            fallback_eligibility,
            warnings=(
                _warning(
                    "source_provenance_eligible_fallback",
                    "fund",
                    fund_code,
                    f"{fund_code} fallback eligible；仅解除 source blocker，不证明 ready。",
                    owner,
                    next_gate,
                    evidence_artifacts,
                ),
            ),
        )
    return _SourceProvenanceSummary(
        status,
        fallback_eligibility,
        blockers=(
            _blocker(
                "source_provenance_unknown",
                "fund",
                fund_code,
                f"{fund_code} fallback provenance category 无法归入 accepted taxonomy。",
                owner,
                next_gate,
                evidence_artifacts,
            ),
        ),
    )


def _derive_score_blockers(
    score_payload: Mapping[str, object], artifact: FundArtifactInput
) -> tuple[ReadinessBlocker, ...]:
    """派生 score blocker。

    Args:
        score_payload: score JSON payload。
        artifact: 单基金 artifact 输入。

    Returns:
        score blocker 元组。

    Raises:
        无显式抛出。
    """

    issues = score_payload.get("score_applicability_issues", [])
    if not isinstance(issues, list):
        return (
            _blocker(
                "score_applicability_baseline_blocking",
                "fund",
                artifact.fund_code,
                "score_applicability_issues 非数组，无法证明 baseline readiness。",
                artifact.coverage_owner,
                artifact.next_gate,
                artifact.evidence_artifacts,
            ),
        )
    blockers: list[ReadinessBlocker] = []
    for issue in issues:
        if isinstance(issue, dict) and issue.get("baseline_blocking") is True:
            blockers.append(
                _blocker(
                    "score_applicability_baseline_blocking",
                    "fund",
                    artifact.fund_code,
                    f"{artifact.fund_code} 存在 baseline_blocking score issue。",
                    artifact.coverage_owner,
                    artifact.next_gate,
                    artifact.evidence_artifacts,
                )
            )
    return tuple(blockers)


def _derive_score_correctness_blockers(
    score_payload: Mapping[str, object],
    artifact: FundArtifactInput,
    golden_answer_path: Path | None,
) -> tuple[ReadinessBlocker, ...]:
    """派生 score correctness 配置 blocker。

    Args:
        score_payload: score JSON payload。
        artifact: 单基金 artifact 输入。
        golden_answer_path: strict golden answer JSON 路径。

    Returns:
        correctness blocker 元组。

    Raises:
        无显式抛出。
    """

    correctness = score_payload.get("correctness")
    if golden_answer_path is None:
        return (
            _blocker(
                "strict_golden_not_configured",
                "fund",
                artifact.fund_code,
                f"{artifact.fund_code} score correctness 未配置 strict golden answer。",
                artifact.coverage_owner,
                artifact.next_gate,
                artifact.evidence_artifacts,
            ),
        )
    if not isinstance(correctness, dict):
        return ()
    coverage_scope = correctness.get("coverage_scope")
    status = correctness.get("status")
    if status == "unavailable" and coverage_scope == "not_configured":
        return (
            _blocker(
                "strict_golden_not_configured",
                "fund",
                artifact.fund_code,
                f"{artifact.fund_code} score correctness 为 not_configured。",
                artifact.coverage_owner,
                artifact.next_gate,
                artifact.evidence_artifacts,
            ),
        )
    return ()


def _derive_quality_blockers(
    quality_payload: Mapping[str, object], artifact: FundArtifactInput
) -> tuple[tuple[ReadinessBlocker, ...], tuple[ReadinessWarning, ...]]:
    """派生 quality gate blocker/warning。

    Args:
        quality_payload: quality gate JSON payload。
        artifact: 单基金 artifact 输入。

    Returns:
        blocker 与 warning 元组。

    Raises:
        无显式抛出。
    """

    status = quality_payload.get("status")
    if status == "block":
        return (
            (
                _blocker(
                    "quality_gate_block",
                    "fund",
                    artifact.fund_code,
                    f"{artifact.fund_code} quality gate status=block。",
                    artifact.coverage_owner,
                    artifact.next_gate,
                    artifact.evidence_artifacts,
                ),
            ),
            (),
        )
    if status == "warn":
        return (
            (),
            (
                _warning(
                    "quality_gate_warn",
                    "fund",
                    artifact.fund_code,
                    f"{artifact.fund_code} quality gate status=warn；不能证明 ready。",
                    artifact.coverage_owner,
                    artifact.next_gate,
                    artifact.evidence_artifacts,
                ),
            ),
        )
    return (), ()


def _derive_strict_golden_coverage(
    *,
    artifact: FundArtifactInput,
    golden_covered_funds: set[str] | None,
    golden_answer_path: Path | None,
) -> tuple[str, tuple[ReadinessBlocker, ...]]:
    """派生 strict golden v1 fund-level 覆盖状态。

    Args:
        artifact: 单基金 artifact 输入。
        golden_covered_funds: strict golden v1 已覆盖基金集合。
        golden_answer_path: strict golden answer JSON 路径。

    Returns:
        覆盖状态与 blocker 元组。

    Raises:
        无显式抛出。
    """

    if not artifact.fund_code.isdigit():
        return "not_applicable", ()
    if golden_answer_path is None or golden_covered_funds is None:
        return (
            "not_configured",
            (
                _blocker(
                    "strict_golden_not_configured",
                    "fund",
                    artifact.fund_code,
                    f"{artifact.fund_code} strict golden answer 未配置。",
                    artifact.coverage_owner,
                    artifact.next_gate,
                    artifact.evidence_artifacts,
                ),
            ),
        )
    if artifact.fund_code not in golden_covered_funds:
        return (
            "fund_not_covered",
            (
                _blocker(
                    "strict_golden_fund_not_covered",
                    "fund",
                    artifact.fund_code,
                    f"{artifact.fund_code} 不在 strict golden answer v1 fund-level coverage 中。",
                    artifact.coverage_owner,
                    artifact.next_gate,
                    artifact.evidence_artifacts,
                ),
            ),
        )
    return "covered", ()


def _derive_fixture_promotion_state(
    *,
    artifact: FundArtifactInput,
    fixture_promotion_state_path: Path | None,
    fixture_states: dict[str, PromotionState] | None,
) -> _PromotionStateSummary:
    """派生 fixture promotion 状态。

    Args:
        artifact: 单基金 artifact 输入。
        fixture_promotion_state_path: fixture promotion state JSON 路径。
        fixture_states: fixture promotion 状态映射。

    Returns:
        promotion state summary。

    Raises:
        无显式抛出。
    """

    if not artifact.fund_code.isdigit():
        return _PromotionStateSummary("not_applicable", artifact.promotion_state)
    if fixture_promotion_state_path is None or fixture_states is None:
        return _PromotionStateSummary(
            "absent",
            "not_promoted",
            blockers=(
                _blocker(
                    "fixture_promotion_absent",
                    "fund",
                    artifact.fund_code,
                    f"{artifact.fund_code} 未发现 accepted fixture promotion state。",
                    artifact.coverage_owner,
                    artifact.next_gate,
                    artifact.evidence_artifacts,
                ),
            ),
        )
    promotion_state = fixture_states.get(artifact.fund_code)
    if promotion_state is None or promotion_state == "unknown":
        return _PromotionStateSummary(
            "unknown",
            "unknown",
            blockers=(
                _blocker(
                    "fixture_promotion_unknown",
                    "fund",
                    artifact.fund_code,
                    f"{artifact.fund_code} fixture promotion state 缺失或 unknown。",
                    artifact.coverage_owner,
                    artifact.next_gate,
                    artifact.evidence_artifacts,
                ),
            ),
        )
    if promotion_state != "promoted_fixture":
        return _PromotionStateSummary(
            promotion_state,
            promotion_state,
            blockers=(
                _blocker(
                    "fixture_promotion_absent",
                    "fund",
                    artifact.fund_code,
                    f"{artifact.fund_code} 尚未 accepted fixture promotion。",
                    artifact.coverage_owner,
                    artifact.next_gate,
                    artifact.evidence_artifacts,
                ),
            ),
        )
    return _PromotionStateSummary("promoted_fixture", "promoted_fixture")


def _derive_coverage_disposition_blockers(
    artifact: FundArtifactInput, entry: CoverageDispositionEntry | None
) -> tuple[ReadinessBlocker, ...]:
    """派生 coverage disposition blocker。

    Args:
        artifact: 单基金 artifact 输入。
        entry: coverage disposition entry。

    Returns:
        disposition blocker 元组。

    Raises:
        无显式抛出。
    """

    disposition = artifact.preflight_disposition
    if entry is None and disposition == "unknown":
        return (
            _blocker(
                "missing_input_artifact",
                "fund",
                artifact.fund_code,
                f"{artifact.fund_code} 缺少机器可归因 coverage disposition。",
                artifact.coverage_owner,
                artifact.next_gate,
                artifact.evidence_artifacts,
            ),
        )
    if disposition == "blocked" and artifact.fund_code in {"096001", "040046", "019172", "021539"}:
        return (
            _blocker(
                "qdii_coverage_blocked",
                "slot",
                artifact.fund_code,
                "QDII replacement hard stop accepted; candidate quality block after eligible provenance.",
                artifact.coverage_owner,
                artifact.next_gate,
                artifact.evidence_artifacts,
            ),
        )
    if disposition == "needs_taxonomy_gate":
        return (
            _blocker(
                "fof_taxonomy_pending",
                "slot",
                artifact.fund_code,
                "Pure FOF taxonomy pending；QDII-FOF 不可计为 pure FOF。",
                artifact.coverage_owner,
                artifact.next_gate,
                artifact.evidence_artifacts,
            ),
            _blocker(
                "fof_data_gap",
                "slot",
                artifact.fund_code,
                "缺少 repository-verified pure FOF candidate。",
                artifact.coverage_owner,
                artifact.next_gate,
                artifact.evidence_artifacts,
            ),
        )
    if disposition == "reviewed_coverage_candidate":
        return (
            _blocker(
                "reviewed_candidate_not_promoted",
                "fund",
                artifact.fund_code,
                f"{artifact.fund_code} 仅 accepted 为 reviewed coverage candidate input，尚未 promotion。",
                artifact.coverage_owner,
                artifact.next_gate,
                artifact.evidence_artifacts,
            ),
            _blocker(
                "index_evidence_insufficient",
                "fund",
                artifact.fund_code,
                f"{artifact.fund_code} methodology/constituents/reviewed fact freeze 证据仍不足。",
                artifact.coverage_owner,
                artifact.next_gate,
                artifact.evidence_artifacts,
            ),
        )
    return ()


def _derive_006597_bond_resolved_items(
    score_payload: Mapping[str, object] | None,
    quality_payload: Mapping[str, object] | None,
    artifact: FundArtifactInput,
) -> tuple[ResolvedReadinessItem, ...]:
    """派生 006597 bond blocker resolved item。

    Args:
        score_payload: score JSON payload。
        quality_payload: quality gate JSON payload。
        artifact: 006597 artifact 输入。

    Returns:
        resolved item；若仍发现 bond blocker 则为空。

    Raises:
        无显式抛出。
    """

    if score_payload is None or quality_payload is None:
        return ()
    if _payload_mentions_code(score_payload.get("score_applicability_issues"), "bond_risk_evidence_missing"):
        return ()
    if _payload_mentions_code(quality_payload.get("issues"), "bond_risk_evidence_missing"):
        return ()
    return (
        ResolvedReadinessItem(
            code="blocker_resolved",
            original_blocker_code="bond_risk_evidence_missing",
            fund_code="006597",
            message=(
                "006597 bond_risk_evidence_missing resolved by accepted NAV-derived "
                "drawdown metric gate."
            ),
            evidence_artifacts=artifact.evidence_artifacts,
        ),
    )


def _payload_mentions_code(payload: object, code: str) -> bool:
    """检查 payload 是否包含指定代码文本。

    Args:
        payload: 任意 JSON 子树。
        code: 待查找代码。

    Returns:
        是否命中。

    Raises:
        无显式抛出。
    """

    if isinstance(payload, str):
        return code in payload
    if isinstance(payload, dict):
        return any(_payload_mentions_code(value, code) for value in payload.values())
    if isinstance(payload, list):
        return any(_payload_mentions_code(value, code) for value in payload)
    return False


def _quality_gate_status(quality_payload: Mapping[str, object] | None) -> str:
    """读取 quality gate status。

    Args:
        quality_payload: quality gate JSON payload。

    Returns:
        status 字符串。

    Raises:
        无显式抛出。
    """

    if quality_payload is None:
        return "not_evaluated"
    status = quality_payload.get("status")
    return status if isinstance(status, str) else "unknown"


def _aggregate_readiness(
    *,
    blockers: tuple[ReadinessBlocker, ...],
    artifact_required: bool,
    preflight_disposition: PreflightDisposition,
) -> ReadinessStatus:
    """聚合 readiness 状态。

    Args:
        blockers: blocker 元组。
        artifact_required: 是否要求运行 artifact。
        preflight_disposition: preflight disposition。

    Returns:
        readiness 状态。

    Raises:
        无显式抛出。
    """

    if any(blocker.code == "missing_input_artifact" for blocker in blockers) and artifact_required:
        return "not_evaluated"
    if blockers:
        if any(blocker.code in {"fof_taxonomy_pending", "fof_data_gap"} for blocker in blockers):
            return "blocked"
        if preflight_disposition in {
            "reviewed_coverage_candidate",
            "include_for_later_review",
            "needs_taxonomy_gate",
            "deferred",
        } and not any(
            blocker.code
            in {
                "quality_gate_block",
                "source_provenance_unknown",
                "source_provenance_ineligible",
                "score_applicability_baseline_blocking",
                "qdii_coverage_blocked",
            }
            for blocker in blockers
        ):
            return "deferred_with_owner"
        return "blocked"
    return "ready"


def _derive_manifest_global_blockers(
    rows: tuple[FundReadinessRow, ...], manifest: CoverageDispositionManifest
) -> tuple[ReadinessBlocker, ...]:
    """派生 manifest 级全局 blocker。

    Args:
        rows: readiness 行。
        manifest: coverage disposition manifest。

    Returns:
        全局 blocker 元组。

    Raises:
        无显式抛出。
    """

    blockers: list[ReadinessBlocker] = []
    qdii_rows = [row for row in rows if row.fund_code in {"096001", "040046", "019172", "021539"}]
    if qdii_rows:
        blockers.append(
            _blocker(
                "qdii_replacement_hard_stop",
                "global",
                None,
                "QDII replacement hard stop accepted；禁止继续 automatic QDII probing。",
                "future QDII diagnosis or taxonomy / asset-class fitness gate",
                "QDII diagnosis or explicit QDII deferred-from-v1 disposition gate",
                _manifest_source_artifacts(manifest),
            )
        )
    return tuple(blockers)


def _row_blocks_v1(row: FundReadinessRow, manifest: CoverageDispositionManifest) -> bool:
    """判断 row 是否因 accepted disposition 阻断 v1。

    Args:
        row: readiness 行。
        manifest: coverage disposition manifest。

    Returns:
        是否阻断 v1。

    Raises:
        无显式抛出。
    """

    entry = _find_manifest_entry(manifest, row.fund_code, row.report_year)
    return bool(entry and entry.blocks_v1 and row.readiness != "ready")


def _derive_blocking_questions(
    rows: tuple[FundReadinessRow, ...], global_blockers: tuple[ReadinessBlocker, ...]
) -> tuple[str, ...]:
    """派生 blocking questions。

    Args:
        rows: readiness 行。
        global_blockers: 全局 blocker。

    Returns:
        blocking questions。

    Raises:
        无显式抛出。
    """

    questions: list[str] = []
    if any(blocker.code == "fixture_promotion_absent" for blocker in global_blockers) or any(
        blocker.code == "fixture_promotion_absent" for row in rows for blocker in row.blockers
    ):
        questions.append("是否产出 accepted fixture promotion state manifest，并由独立 gate 接受？")
    if any(row.fund_code == "FOF_SLOT" for row in rows):
        questions.append("pure FOF coverage 是否已有 repository-verified candidate 和 taxonomy gate？")
    if any(row.fund_code == "110020" for row in rows):
        questions.append("110020 是否完成 methodology/constituents/reviewed fact freeze gate？")
    return tuple(questions)


def _manifest_source_artifacts(manifest: CoverageDispositionManifest) -> tuple[Path, ...]:
    """读取 manifest 来源 artifact。

    Args:
        manifest: coverage disposition manifest。

    Returns:
        来源 artifact 路径。

    Raises:
        无显式抛出。
    """

    return manifest.source_artifacts


def _blocker(
    code: str,
    scope: str,
    fund_code: str | None,
    message: str,
    owner: str,
    next_gate: str,
    evidence_artifacts: tuple[Path, ...] = (),
) -> ReadinessBlocker:
    """构造 block severity blocker。

    Args:
        code: blocker code。
        scope: 影响范围。
        fund_code: 基金代码或 slot id。
        message: 说明。
        owner: owner。
        next_gate: 下一步 gate。
        evidence_artifacts: 证据 artifact。

    Returns:
        readiness blocker。

    Raises:
        无显式抛出。
    """

    return ReadinessBlocker(
        code=code,
        severity="block",
        scope=scope,
        fund_code=fund_code,
        message=message,
        owner=owner,
        next_gate=next_gate,
        evidence_artifacts=evidence_artifacts,
    )


def _warning(
    code: str,
    scope: str,
    fund_code: str | None,
    message: str,
    owner: str,
    next_gate: str,
    evidence_artifacts: tuple[Path, ...] = (),
) -> ReadinessWarning:
    """构造 warn severity warning。

    Args:
        code: warning code。
        scope: 影响范围。
        fund_code: 基金代码或 slot id。
        message: 说明。
        owner: owner。
        next_gate: 下一步 gate。
        evidence_artifacts: 证据 artifact。

    Returns:
        readiness warning。

    Raises:
        无显式抛出。
    """

    return ReadinessWarning(
        code=code,
        severity="warn",
        scope=scope,
        fund_code=fund_code,
        message=message,
        owner=owner,
        next_gate=next_gate,
        evidence_artifacts=evidence_artifacts,
    )


def _load_json_object(path: Path) -> dict[str, object]:
    """读取 JSON object。

    Args:
        path: JSON 路径。

    Returns:
        JSON object。

    Raises:
        ValueError: JSON 顶层不是 object 时抛出。
        OSError: 文件读取失败时传播。
        json.JSONDecodeError: JSON 解析失败时传播。
    """

    with path.open("r", encoding="utf-8") as file_obj:
        payload = json.load(file_obj)
    if not isinstance(payload, dict):
        raise ValueError(f"JSON 顶层必须是 object：{path}")
    return cast(dict[str, object], payload)


def _load_snapshot_rows(path: Path) -> tuple[Mapping[str, object], ...]:
    """读取 snapshot JSONL 行。

    Args:
        path: snapshot JSONL 路径。

    Returns:
        JSON object 行元组。

    Raises:
        ValueError: 任一非空行不是 JSON object 时抛出。
        OSError: 文件读取失败时传播。
        json.JSONDecodeError: JSONL 解析失败时传播。
    """

    rows: list[Mapping[str, object]] = []
    with path.open("r", encoding="utf-8") as file_obj:
        for line_number, line in enumerate(file_obj, start=1):
            if not line.strip():
                continue
            payload = json.loads(line)
            if not isinstance(payload, dict):
                raise ValueError(f"snapshot JSONL 第 {line_number} 行必须是 object：{path}")
            rows.append(cast(Mapping[str, object], payload))
    return tuple(rows)


def _write_outputs(result: GoldenReadinessPreflightResult) -> None:
    """写出 JSON 和 Markdown。

    Args:
        result: preflight result。

    Returns:
        无返回值。

    Raises:
        OSError: 目录创建或文件写入失败时抛出。
    """

    result.json_path.parent.mkdir(parents=True, exist_ok=True)
    result.json_path.write_text(
        json.dumps(_json_payload(result), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    result.markdown_path.write_text(_markdown_payload(result), encoding="utf-8")


def _json_payload(result: GoldenReadinessPreflightResult) -> dict[str, object]:
    """构造机器可读 JSON payload。

    Args:
        result: preflight result。

    Returns:
        JSON-serializable dict。

    Raises:
        无显式抛出。
    """

    return {
        "schema_version": result.schema_version,
        "run_id": result.run_id,
        "generated_at": result.generated_at,
        "source_csv": str(result.source_csv),
        "golden_answer_path": (
            str(result.golden_answer_path) if result.golden_answer_path is not None else None
        ),
        "static_disposition_manifest": _manifest_payload(result.static_disposition_manifest),
        "overall_status": result.overall_status,
        "ready_count": result.ready_count,
        "blocked_count": result.blocked_count,
        "deferred_count": result.deferred_count,
        "not_evaluated_count": result.not_evaluated_count,
        "rows": [_row_payload(row) for row in result.rows],
        "global_blockers": [_blocker_payload(blocker) for blocker in result.global_blockers],
        "resolved_items": [_resolved_payload(item) for item in result.resolved_items],
        "blocking_questions": list(result.blocking_questions),
    }


def _manifest_payload(manifest: CoverageDispositionManifest) -> dict[str, object]:
    """构造 manifest JSON payload。

    Args:
        manifest: coverage disposition manifest。

    Returns:
        JSON-serializable dict。

    Raises:
        无显式抛出。
    """

    return {
        "schema_version": manifest.schema_version,
        "accepted_as_of": manifest.accepted_as_of,
        "source_artifacts": [str(path) for path in manifest.source_artifacts],
        "lifecycle_semantics": list(manifest.lifecycle_semantics),
        "entries": [
            {
                "fund_code": entry.fund_code,
                "report_year": entry.report_year,
                "raw_disposition": entry.raw_disposition,
                "preflight_disposition": entry.preflight_disposition,
                "promotion_state": entry.promotion_state,
                "coverage_owner": entry.coverage_owner,
                "next_gate": entry.next_gate,
                "blocks_v1": entry.blocks_v1,
                "evidence_artifacts": [str(path) for path in entry.evidence_artifacts],
                "snapshot_path": str(entry.snapshot_path) if entry.snapshot_path else None,
                "score_path": str(entry.score_path) if entry.score_path else None,
                "quality_gate_path": str(entry.quality_gate_path)
                if entry.quality_gate_path
                else None,
                "score_golden_set_path": str(entry.score_golden_set_path)
                if entry.score_golden_set_path
                else None,
                "artifact_required": entry.artifact_required,
                "slot_kind": entry.slot_kind,
                "lifecycle_note": entry.lifecycle_note,
            }
            for entry in manifest.entries
        ],
    }


def _row_payload(row: FundReadinessRow) -> dict[str, object]:
    """构造 row JSON payload。

    Args:
        row: readiness row。

    Returns:
        JSON-serializable dict。

    Raises:
        无显式抛出。
    """

    return {
        "fund_code": row.fund_code,
        "report_year": row.report_year,
        "fund_name": row.fund_name,
        "app_category": row.app_category,
        "classified_fund_type": row.classified_fund_type,
        "readiness": row.readiness,
        "promotion_state": row.promotion_state,
        "source_provenance_status": row.source_provenance_status,
        "fallback_eligibility": row.fallback_eligibility,
        "quality_gate_status": row.quality_gate_status,
        "strict_golden_coverage": row.strict_golden_coverage,
        "fixture_promotion_state": row.fixture_promotion_state,
        "raw_disposition": row.raw_disposition,
        "preflight_disposition": row.preflight_disposition,
        "blockers": [_blocker_payload(blocker) for blocker in row.blockers],
        "warnings": [_warning_payload(warning) for warning in row.warnings],
        "resolved_items": [_resolved_payload(item) for item in row.resolved_items],
        "owner": row.owner,
        "next_gate": row.next_gate,
        "evidence_artifacts": [str(path) for path in row.evidence_artifacts],
    }


def _blocker_payload(blocker: ReadinessBlocker) -> dict[str, object]:
    """构造 blocker JSON payload。

    Args:
        blocker: readiness blocker。

    Returns:
        JSON-serializable dict。

    Raises:
        无显式抛出。
    """

    return {
        "code": blocker.code,
        "severity": blocker.severity,
        "scope": blocker.scope,
        "fund_code": blocker.fund_code,
        "message": blocker.message,
        "owner": blocker.owner,
        "next_gate": blocker.next_gate,
        "evidence_artifacts": [str(path) for path in blocker.evidence_artifacts],
    }


def _warning_payload(warning: ReadinessWarning) -> dict[str, object]:
    """构造 warning JSON payload。

    Args:
        warning: readiness warning。

    Returns:
        JSON-serializable dict。

    Raises:
        无显式抛出。
    """

    return {
        "code": warning.code,
        "severity": warning.severity,
        "scope": warning.scope,
        "fund_code": warning.fund_code,
        "message": warning.message,
        "owner": warning.owner,
        "next_gate": warning.next_gate,
        "evidence_artifacts": [str(path) for path in warning.evidence_artifacts],
    }


def _resolved_payload(item: ResolvedReadinessItem) -> dict[str, object]:
    """构造 resolved item JSON payload。

    Args:
        item: resolved item。

    Returns:
        JSON-serializable dict。

    Raises:
        无显式抛出。
    """

    return {
        "code": item.code,
        "original_blocker_code": item.original_blocker_code,
        "fund_code": item.fund_code,
        "message": item.message,
        "evidence_artifacts": [str(path) for path in item.evidence_artifacts],
    }


def _markdown_payload(result: GoldenReadinessPreflightResult) -> str:
    """构造人类可读 Markdown payload。

    Args:
        result: preflight result。

    Returns:
        Markdown 字符串。

    Raises:
        无显式抛出。
    """

    verdict = result.overall_status.upper()
    lines = [
        "# Golden Readiness Preflight",
        "",
        "## 真源摘要",
        "",
        f"- run_id: `{result.run_id}`",
        f"- source_csv: `{result.source_csv}`",
        f"- golden_answer_path: `{result.golden_answer_path}`",
        "- strict golden answer v1 仅执行 fund-level coverage；year/partial coverage codes 保留不触发。",
        "- 本 preflight 只读，不执行 fixture promotion、golden promotion、release 或 QDII probing。",
        "",
        "## Overall Verdict",
        "",
        f"**{verdict}**",
        "",
        "## 已解除",
        "",
    ]
    if result.resolved_items:
        for item in result.resolved_items:
            lines.append(
                f"- `{item.code}` / original_blocker_code=`{item.original_blocker_code}` / "
                f"fund_code=`{item.fund_code}`: {item.message}"
            )
    else:
        lines.append("- 无")
    lines.extend(
        [
            "",
            "## Per-Fund / Slot Readiness",
            "",
            "| fund_code | year | readiness | quality | strict_golden | fixture | disposition |",
            "|---|---:|---|---|---|---|---|",
        ]
    )
    for row in result.rows:
        lines.append(
            f"| {row.fund_code} | {row.report_year} | {row.readiness} | "
            f"{row.quality_gate_status} | {row.strict_golden_coverage} | "
            f"{row.fixture_promotion_state} | {row.preflight_disposition} |"
        )
    lines.extend(["", "## Blockers By Severity", ""])
    all_blockers = list(result.global_blockers)
    all_blockers.extend(blocker for row in result.rows for blocker in row.blockers)
    if all_blockers:
        lines.extend(
            [
                "| severity | code | scope | fund_code | owner | next_gate | message |",
                "|---|---|---|---|---|---|---|",
            ]
        )
        for blocker in all_blockers:
            lines.append(
                f"| {blocker.severity} | {blocker.code} | {blocker.scope} | "
                f"{blocker.fund_code or ''} | {blocker.owner} | {blocker.next_gate} | "
                f"{blocker.message} |"
            )
    else:
        lines.append("- 无")
    lines.extend(
        [
            "",
            "## Owner / Next Gate",
            "",
            "| fund_code | owner | next_gate |",
            "|---|---|---|",
        ]
    )
    for row in result.rows:
        lines.append(f"| {row.fund_code} | {row.owner} | {row.next_gate} |")
    lines.extend(["", "## Missing Input / Blocking Questions", ""])
    if result.blocking_questions:
        for question in result.blocking_questions:
            lines.append(f"- {question}")
    else:
        lines.append("- 无")
    lines.extend(
        [
            "",
            "## Non-goals And Guardrails",
            "",
            "- 不修改 score policy、quality gate severity、FQ0-FQ6 或 final judgment。",
            "- 不修改 golden answer JSON、golden fixtures 或 fixture promotion state。",
            "- 不直接访问 PDF/cache/source helper；年报访问边界保持在 FundDocumentRepository。",
            "- 不引入 Host/Agent/dayu、不执行 push/PR/merge/release/golden promotion。",
            "",
        ]
    )
    return "\n".join(lines)


def _load_json_object_or_none(path: Path | None) -> dict[str, object] | None:
    """读取可选 JSON object。

    Args:
        path: 可选 JSON 路径。

    Returns:
        JSON object 或 None。

    Raises:
        ValueError: JSON 顶层不是 object 时抛出。
    """

    if path is None or not path.exists():
        return None
    return _load_json_object(path)


_ = _load_json_object_or_none
