# 基金行为教练 Agent —— 实施总控文档

> **版本**: v2.1
> **日期**: 2026-05-27
> **设计真源**: `docs/design.md` (v2.2)
> **规则真源**: `AGENTS.md`
> **历史快照**: `docs/archive/implementation-control-history-20260525.md`
> **release-maintenance 长账本**: `docs/archive/implementation-control-release-maintenance-ledger-20260527.md`
> **当前状态**: release maintenance；bond risk evidence extractor / anchor hardening Slice 6 blocked with reason；下一入口为 drawdown_stress evidence contract / NAV-derived risk metric design gate 或已授权的 extractor-hardening amendment

---

## Startup Packet

### Current Truth Guardrails

本节是每个总控 / 子 Agent 恢复任务时必须先读取并复述的当前执行口径。

- 当前真源只包括 `AGENTS.md`、`docs/design.md` 当前设计章节、本文档 Startup Packet 和当前 gate。
- `docs/reviews/` 与 `docs/archive/` 只作为证据链；旧六层、Application、Runtime/Engine 表述只作为历史证据，不得作为当前架构依据。
- 当前架构按 Dayu 四层 `UI -> Service -> Host -> Agent` 设计；当前确定性生产主链路仍是 UI -> Service -> `fund_agent/fund` Agent 层基金能力的过渡实现。
- 未开独立 Host/Agent gate 前，不得创建占位 `fund_agent/host` 或 `fund_agent/agent` 包；确需 Host 时必须使用 `dayu.host`，确需 Agent 执行内核 / tool loop / runner / ToolRegistry / ToolTrace 时必须使用 `dayu.engine`。
- 后续 plan/review 必须显式检查四层边界、Dayu Host/Agent 依赖纪律、显式参数 / 禁止 `extra_payload`、`dayu-agent` pyproject 工程基线和当前 gate 非目标。
- 当前 phase 采用 `AGENTS.md` 的 Gate 轻重分类规则；每个 gate 进入前必须记录 `fast_path` / `standard` / `heavy` 分类、分类依据、验证矩阵和升级条件。默认 `standard`，分类不确定时选择更重一级；不得用轻量流程改变 public contract、schema、quality gate 语义、final judgment、Host/Agent/dayu、外部来源策略或 release/PR 外部状态。

| Field | State |
|---|---|
| Branch | `codex/local-reconciliation` |
| Current phase | `release maintenance` |
| Current gate | `bond risk evidence extractor / anchor hardening Slice 6 blocked with reason` |
| Current gate classification | `standard` |
| Next entry point | `drawdown_stress evidence contract / NAV-derived risk metric design gate, or authorized extractor-hardening amendment for credit_risk + redemption_share_pressure` |
| Next gate classification | `standard` |
| Latest accepted gate checkpoint | `bond risk evidence extractor / anchor hardening Slice 5 local accepted commit; Slice 6 validation is blocked-with-reason, not accepted as unblocked` |
| Design truth | `docs/design.md` (v2.2) |
| Control truth | `docs/implementation-control.md` |
| Historical control snapshots | `docs/archive/implementation-control-history-20260525.md`; `docs/archive/implementation-control-release-maintenance-ledger-20260527.md` |
| External repo state | PR 18 merged at `2026-05-25T14:44:05Z`; PR 19 merged at `2026-05-25T15:43:35Z`; `origin/main` points to `44ea955` |

## Current Gate

### Current Accepted Artifacts

| Purpose | Artifact |
|---|---|
| Truth preflight | `docs/reviews/release-maintenance-bond-positive-risk-truth-preflight-20260527.md` |
| Evidence plan | `docs/reviews/release-maintenance-bond-positive-risk-evidence-plan-20260527.md` |
| Plan review: DS | `docs/reviews/release-maintenance-bond-positive-risk-evidence-plan-review-ds-20260527.md` |
| Plan review: MiMo | `docs/reviews/release-maintenance-bond-positive-risk-evidence-plan-review-mimo-20260527.md` |
| Plan re-review: MiMo | `docs/reviews/release-maintenance-bond-positive-risk-evidence-plan-rereview-mimo-20260527.md` |
| Plan controller judgment | `docs/reviews/release-maintenance-bond-positive-risk-evidence-plan-controller-judgment-20260527.md` |
| Evidence artifact | `docs/reviews/release-maintenance-bond-positive-risk-evidence-20260527.md` |
| Evidence review: DS | `docs/reviews/release-maintenance-bond-positive-risk-evidence-review-ds-20260527.md` |
| Evidence review: MiMo | `docs/reviews/release-maintenance-bond-positive-risk-evidence-review-mimo-20260527.md` |
| Controller judgment | `docs/reviews/release-maintenance-bond-positive-risk-evidence-controller-judgment-20260527.md` |

### Current Decision Summary

- Truth preflight found and closed a docs-only mismatch: `docs/implementation-control.md` referenced `AGENTS.md` Gate classification rules before `AGENTS.md` defined `fast_path` / `standard` / `heavy`; `AGENTS.md` now defines the rules.
- Automatic QDII replacement probing is stopped. Do not run additional QDII candidates until a separate QDII diagnosis, taxonomy / asset-class fitness, or explicit coverage-blocked gate is accepted.
- `096001`, `040046`, `019172`, and `021539` are all preserved as source-provenance eligible, quality `block`, terminal `quality_blocked_after_provenance`, and `not_promoted`.
- QDII coverage is blocked for baseline/golden v1; no QDII row is replacement-ready, baseline-ready, scoring-ready, golden-ready, or source-safe for promotion.
- Coverage disposition matrix remains: active `004393` and enhanced-index `004194` are carry-forward evaluated candidates; index `110020` is terminal `reviewed_coverage_candidate_input_accepted` but `not_promoted`; bond `006597` remains blocked by `bond_risk_evidence_missing.baseline_blocking=true`; FOF remains `data_gap` / `taxonomy_pending`.
- `006597` / 2024 annual report contains same-fund/year candidate bond-risk evidence for all seven `bond_risk_evidence.v1` groups, but current public CLI/score cannot express positive `bond_risk_evidence` records or durable group-level anchors. Final state is `extractor/evidence anchor issue requiring future gate`, not data gap and not blocker解除.
- Future bond risk extractor/anchor work must preserve evidence-strength distinctions: `drawdown_stress` currently has qualitative drawdown-control intent rather than a quantitative metric, and `leverage_liquidity` needs precise table/row anchors before consumption.
- Golden answer corpus v1 remains blocked until coverage, source, quality, fund-type, and fixture-promotion blockers are resolved or explicitly deferred.

## Next Entry Point

`drawdown_stress evidence contract / NAV-derived risk metric design gate`, or an explicitly authorized `bond risk evidence extractor / anchor hardening amendment` for `credit_risk` and `redemption_share_pressure`.

This next gate must start with Startup Packet replay and `$init-agents` / tmux multi-agent flow. Slice 1-5 already define and emit positive `bond_risk_evidence.v1`; Slice 6 real validation remains blocked because `006597` / 2024 still has `drawdown_stress` as weak qualitative evidence and score keeps `bond_risk_evidence_missing.baseline_blocking=true`.

Allowed scope:

- Plan/review before any implementation.
- If continuing extractor hardening, limit scope to `credit_risk` rating distribution table detection and `redemption_share_pressure` §2 share-class mapping / §10 share-change table selection.
- If pursuing full blocker解除, define a separate contract for NAV-derived max drawdown / volatility evidence, including source anchors and score applicability semantics.
- Keep qualitative drawdown-control text weak unless a reviewed contract explicitly changes the rule.
- Preserve evidence-strength distinctions and do not treat weak or ambiguous groups as accepted.
- Preserve existing FQ0-FQ6 semantics, renderer output, Service/CLI behavior, source strategy, and `FundDocumentRepository` boundaries.
- Do not enter QDII probing, FOF taxonomy work, golden corpus preflight, release readiness, Host/Agent/dayu work, baseline/golden promotion, or GitHub mutation.
- Produce two independent reviews and controller judgment before acceptance.

## Current Non-Goals

- Do not change current v0 renderer or current 8-chapter output.
- Do not change FQ0-FQ6 quality gate behavior.
- Do not claim LLM audit / Evidence Confirm / repair loop is implemented.
- Do not create Host/Agent packages or introduce `dayu.host` / `dayu.engine` before an explicit gate.
- Do not introduce calculated index series, external index adapters beyond accepted thermometer data-source protocols, methodology extraction, constituents extraction, QDII subtype redesign, unsupported coverage targets, or quality-gate weakening.
- Do not promote local scoring, writing, or data-source run outputs into tracked fixtures without a later reviewed gate.
- Do not enter `golden answer corpus v1` until coverage, source, quality, fund-type, and fixture-promotion blockers are resolved.
- Do not push, create PR, mark ready, merge, close PRs, edit unrelated PRs, delete branches, or perform additional GitHub mutations without explicit user authorization.

## Open Residuals

| Residual | Owner / next gate | Required handling |
|---|---|---|
| QDII coverage blocked after hard stop | future QDII diagnosis or taxonomy / asset-class fitness gate | Automatic QDII probing is stopped; preserve `096001`, `040046`, `019172`, `021539` as provenance-eligible, quality `block`, `not_promoted`. No new QDII evidence before a separate accepted gate. |
| Golden answer corpus v1 blocked | future golden preflight after coverage disposition | Do not promote any sample until coverage, source, quality, fund-type, and fixture-promotion blockers are resolved. |
| `110020` reviewed coverage candidate | future golden/baseline preflight | Accepted only as reviewed coverage candidate input; remains `not_promoted`; methodology / constituents evidence remains insufficient. |
| `017641` QDII data gap | disposition / taxonomy follow-up | Original QDII row is provenance-complete but quality `block` due to `manager_strategy_text`; accepted disposition is `replace`, not promotion. |
| FOF coverage / taxonomy | future fund-type taxonomy gate | Find pure `fof_fund` repository-verified candidate, or open taxonomy gate before counting QDII-FOF attempts as FOF coverage. |
| `006597` bond risk evidence blocker | `drawdown_stress evidence contract / NAV-derived risk metric design gate` or authorized extractor-hardening amendment | Slice 6 real validation emitted positive `bond_risk_evidence.v1` but score still has `bond_risk_evidence_missing.baseline_blocking=true`; `credit_risk` and `redemption_share_pressure` are extractor misses, while `drawdown_stress` has only qualitative control-drawdown text and remains weak under current contract. Do not claim blocker解除 without quantitative drawdown/volatility evidence or a reviewed contract change. |
| Source metadata strict bool parsing | future source provenance hardening gate | Plan/review strict bool parser for `AnnualReportSourceMetadata.from_dict()`; current known issue: string `"false"` coerces truthy. |
| Stray untracked `--help` file | artifact disposition / user-authorized cleanup | Do not stage or promote; delete only with explicit authorization or accepted disposition. |
| Untracked review/evidence artifacts | artifact disposition gate if needed | Decide whether to accept, archive, or leave untracked; do not silently stage unrelated artifacts. |

## Recent Active Gate Ledger

| Gate | Status | Artifact | Validation / judgment | Next action |
|---|---|---|---|---|
| `source provenance post-implementation bounded evidence rerun` | accepted locally | `docs/reviews/release-maintenance-source-provenance-post-implementation-bounded-evidence-rerun-controller-judgment-20260527.md` | `110020` and `017641` exposed complete eligible fallback provenance; no promotion | post-provenance coverage recovery decision |
| `docs-only truth reconciliation` | accepted locally | `docs/reviews/release-maintenance-docs-truth-reconciliation-20260527.md` | Repo review F1/F2 closed in `docs/design.md`; F3 deferred; ruff / pytest / diff check passed | coverage recovery decision |
| `post-provenance coverage recovery decision plan` | accepted locally | `docs/reviews/release-maintenance-post-provenance-coverage-recovery-decision-plan-controller-judgment-20260527.md` | Roadmap gates 1-4 skipped as accepted; golden corpus v1 blocked | `110020` candidate decision |
| `110020 reviewed coverage candidate evidence` | accepted locally | `docs/reviews/release-maintenance-110020-reviewed-coverage-candidate-evidence-controller-judgment-20260527.md` | Public evidence accepted terminal `reviewed_coverage_candidate_input_accepted`; no promotion | `017641` triage |
| `017641 manager_strategy_text public evidence triage` | accepted locally | `docs/reviews/release-maintenance-017641-manager-strategy-text-public-evidence-triage-controller-judgment-20260527.md` | Terminal `disclosure_data_gap_not_baseline_ready`; no promotion | baseline disposition |
| `baseline coverage disposition decision plan` | accepted locally | `docs/reviews/release-maintenance-baseline-coverage-disposition-decision-plan-controller-judgment-20260527.md` | Accepted disposition matrix requirements; no code/evidence/product-flow changes | replacement / exclusion selection |
| `replacement/exclusion candidate selection` | accepted locally | `docs/reviews/release-maintenance-replacement-exclusion-candidate-selection-controller-judgment-20260527.md` | Accepted `017641=replace`, `FOF=needs_taxonomy_gate`, `006597=needs_evidence_gate`; no promotion | QDII replacement plan |
| `QDII replacement evidence sequence` | accepted locally | `docs/reviews/release-maintenance-qdii-replacement-candidate-evidence-controller-judgment-20260527.md`; `docs/reviews/release-maintenance-qdii-replacement-fallback-040046-evidence-controller-judgment-20260527.md`; `docs/reviews/release-maintenance-qdii-replacement-fallback-019172-evidence-controller-judgment-20260527.md`; `docs/reviews/release-maintenance-qdii-replacement-fallback-021539-evidence-controller-judgment-20260527.md` | `096001`, `040046`, `019172`, `021539` all provenance-eligible but quality `block`; `021539` triggers hard stop | QDII post-021539 disposition decision |
| `release-maintenance consolidation / QDII post-021539 disposition` | accepted locally | `docs/reviews/release-maintenance-consolidation-post-021539-disposition-controller-judgment-20260527.md` | Control-doc compression accepted; QDII automatic probing stopped; QDII coverage blocked; golden corpus v1 remains blocked; DS/MiMo reviews `PASS_WITH_FINDINGS`; no code/product changes | bond positive-risk evidence |
| `bond positive-risk evidence` | accepted locally | `docs/reviews/release-maintenance-bond-positive-risk-evidence-controller-judgment-20260527.md` | Truth preflight fixed Gate classification rules in `AGENTS.md`; 006597 evidence run found candidate annual-report evidence for all seven bond-risk groups, but current CLI/score cannot express positive records; DS/MiMo reviews `PASS_WITH_FINDINGS`; no code/product changes | bond risk evidence extractor / anchor hardening design |
| `bond risk evidence extractor / anchor hardening` | blocked with reason | `docs/reviews/release-maintenance-bond-risk-evidence-extractor-anchor-hardening-slice6-controller-judgment-20260528.md` | Slice 1-5 accepted locally and emit structured `bond_risk_evidence.v1`; Slice 6 real validation still has `bond_risk_evidence_missing.baseline_blocking=true` for `credit_risk`, `drawdown_stress`, `redemption_share_pressure`; DS/GLM agree only two groups are extractor misses and drawdown remains weak | drawdown evidence contract / NAV-derived risk metric design gate, or authorized extractor-hardening amendment |

## Historical Evidence Index

Detailed control history is preserved in archive files:

- `docs/archive/implementation-control-history-20260525.md`
- `docs/archive/implementation-control-release-maintenance-ledger-20260527.md`

Use archive files only for evidence reconstruction. They are not current gate truth and must not override this Startup Packet or `docs/design.md` current design sections.

Archived material includes:

- P0-P19 phase definitions, detailed gate logs, PR/commit records, validation counts, and residual histories.
- Superseded six-layer / Application / Runtime/Engine wording.
- Long-form release-maintenance PR 16 / PR 17 / 004393 quality gate / P19 thermometer records.
- Detailed release-maintenance accepted artifacts, Current Decisions, Open Residuals, and Active Gate Ledger through QDII replacement fallback 021539 evidence.

## Design / Control Alignment Rules

1. `AGENTS.md` is the highest-priority execution rule source.
2. `docs/design.md` remains the design truth for architecture, boundaries, current product behavior, Dayu non-dependency, `FundDocumentRepository` source boundaries, report-quality design, and thermometer design.
3. `docs/implementation-control.md` remains the control truth for current phase, current gate, accepted artifacts, residual owners, and next entry point.
4. Historical archive entries are evidence only. If archive content contradicts Startup Packet or `docs/design.md`, treat the archive content as superseded unless a new controller judgment says otherwise.
5. Future control-doc updates should prefer a new `docs/reviews/` artifact plus a short control-doc reference over appending long logs.

## Resume Checklist

When resuming:

1. Read `AGENTS.md`.
2. Read `docs/design.md` current relevant sections.
3. Read this Startup Packet.
4. Confirm `Current phase`, `Current gate`, and `Next entry point`.
5. Confirm the next action is controller work or specialist work.
6. Classify the next gate as `fast_path`, `standard`, or `heavy` per `AGENTS.md`.
7. If specialist work is required, delegate through the current gate handoff; do not write the specialist plan directly unless explicitly authorized.
8. Preserve deterministic MVP boundaries and do not introduce Host/Agent/runtime work outside an explicit gate.
