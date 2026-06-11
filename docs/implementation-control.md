# 基金行为教练 Agent - 实施总控文档

> **版本**: v2.7-control-compressed
> **日期**: 2026-06-11
> **规则真源**: `AGENTS.md`
> **设计真源**: `docs/design.md`
> **控制真源**: `docs/implementation-control.md`
> **短启动入口**: `docs/current-startup-packet.md`
> **当前状态**: `MVP typed-template-to-agent report generation stabilization phase`。`Control-doc compression / artifact hygiene implementation gate` 已在本地 checkpoint `693638b` 接受，controller verdict 为 `ACCEPT_WITH_REVIEW_CHANNEL_RESIDUAL`。当前推荐主线入口是 `Source-like residue ownership gate for fund_agent/tools`。

---

## Startup Packet

短恢复入口见 `docs/current-startup-packet.md`。本文档前部只保留当前控制面；accepted artifact 长表和 historical ledger 已降级为 evidence-chain index：

- Accepted artifact index: `docs/reviews/mvp-control-doc-compression-accepted-artifact-index-20260611.md`
- Historical ledger index: `docs/reviews/mvp-control-doc-compression-historical-ledger-index-20260611.md`
- Untracked residue disposition: `docs/reviews/mvp-control-doc-compression-untracked-residue-disposition-20260611.md`

这些 index 不是设计真源，不覆盖 `AGENTS.md`、`docs/design.md`、`docs/current-startup-packet.md` 或本文档当前控制面。

## Current Truth Guardrails

- `AGENTS.md` 是最高优先级执行规则真源。
- `docs/design.md` 是设计真源；本 gate 不修改它。若发现设计/控制不一致，只记录 residual，转入单独 design-truth-sync gate。
- 当前 phase 是 `MVP typed-template-to-agent report generation stabilization phase`。
- 当前 template contract authored truth source 是 `docs/fund-analysis-template-draft.md` canonical `TEMPLATE_CONTRACT_MANIFEST_JSON`。
- 当前目标架构仍是 `UI -> Service -> Host -> Agent`。
- 当前默认生产主链路仍是确定性 `fund-analysis analyze/checklist`。
- 当前 `--use-llm` 路径是显式 opt-in、provider-backed、fail-closed；不提供 deterministic fallback。
- 当前 annual-report source policy 是 EID single-source operational no-live implementation。Fallback invocation、Eastmoney/fund-company/CNINFO source expansion、fixture projection、golden/readiness promotion、additional source acquisition、provider/default/runtime/budget/config change、chapter live acceptance、multi-year runtime、score-loop、release/merge/mark-ready 均未由本 gate 授权。
- 所有业务参数必须通过 typed request / contract / config 显式声明，禁止通过 `extra_payload` 传递显式参数。
- 生产年报访问必须通过 `FundDocumentRepository`；Service、UI、Host、renderer、quality gate 不得直接调用具体来源、PDF cache 或下载 helper。

## Current Gate

| Field | State |
|---|---|
| Active gate | `Source-like residue ownership gate for fund_agent/tools` |
| Classification | `standard` |
| Accepted input | Control-doc compression / artifact hygiene implementation accepted locally at `693638b`; controller judgment `docs/reviews/mvp-control-doc-compression-artifact-hygiene-controller-judgment-20260611.md` verdict `ACCEPT_WITH_REVIEW_CHANNEL_RESIDUAL` |
| Implementation objective | Plan ownership/disposition for visible source-like residue under `fund_agent/tools/` without import, staging, promotion, cleanup or deletion unless separately accepted |
| Implementation status | Not started |
| Next entry point | Planning worker for source-like residue ownership; read `docs/reviews/mvp-control-doc-compression-untracked-residue-disposition-20260611.md` first |

## Accepted Control-doc Compression Write Set

- `docs/implementation-control.md`
- `docs/current-startup-packet.md`
- `docs/reviews/mvp-control-doc-compression-accepted-artifact-index-20260611.md`
- `docs/reviews/mvp-control-doc-compression-historical-ledger-index-20260611.md`
- `docs/reviews/mvp-control-doc-compression-untracked-residue-disposition-20260611.md`
- `docs/reviews/mvp-control-doc-compression-artifact-hygiene-implementation-evidence-20260611.md`

## Non-goal Reminder

The accepted control-doc compression gate and the next source-like residue ownership planning entry do not authorize:

- source/test/runtime behavior changes
- `docs/design.md` or `.gitignore` edits
- reviewer/controller artifact creation or prefill by implementation worker
- delete, move, archive, clean, ignore, import, stage, promote, commit, push, PR or merge actions
- live EID/network/PDF/FDR/FundDocumentRepository/helper/fallback/provider/LLM/extractor/analyze/checklist/golden/readiness/score-loop/release commands
- treating arbitrary untracked workspace residue as proof, accepted fixture, product scope or release evidence

## Current Accepted Artifact Summary

The current control surface keeps only gate-family summaries. The evidence-chain reconstruction path is `docs/reviews/mvp-control-doc-compression-accepted-artifact-index-20260611.md`.

| Gate family | Accepted status | Current relevance | Residual owner / deferred gate |
|---|---|---|---|
| Control-doc compression / artifact hygiene | Planning accepted locally at `7365e2b`; implementation accepted locally at `693638b` | Current compressed control surface and index artifacts | Review-channel/worker-channel residuals accepted; no further action unless future handoff reliability gate is requested |
| EID single-source operational hardening | Accepted locally across failure-branch evidence, helper repair, controlled retry and metadata docs-sync | Current annual-report source policy | Fallback/source expansion and additional acquisition deferred |
| Small golden / extractor correctness | Accepted locally through current-consumable row-shape and extractor surfaces | Current extractor evidence baseline for named rows/contracts | Fixture projection, promotion and release/readiness deferred |
| Typed template truth-source replacement | Accepted locally; canonical JSON in template draft is authored truth source | Current template contract truth source | Public chapter id/runtime expansion unchanged |
| Agent engine / Host governance | Accepted locally for no-live Agent body runner and process-local Host lifecycle boundary | Current `--use-llm` architecture boundary | Full Agent tool-loop/runtime expansion deferred |
| Provider/runtime/LLM diagnostics | Accepted locally as fail-closed diagnostics and historical provider evidence | Informs provider residual routing | Live acceptance and runtime default changes deferred |
| Release/readiness historical evidence | Evidence-chain only | Does not set current release/PR/readiness state | Release owner after residue disposition acceptance |

## Open Residuals

| Residual | Status | Owner | Next handling |
|---|---|---|---|
| Review-channel residual from accepted control-doc compression gate | accepted residual | Controller / agent setup owner | Re-run init-agents cleanup before next tmux-pane handoff; do not treat old pane content as review output |
| Worker-channel capacity/transport residual from accepted control-doc compression gate | accepted residual | Controller / worker channel owner | Future handoffs should verify completion channel; accepted artifacts remain valid through independent review |
| Untracked residue remains in workspace | accepted residual | Controller / artifact owners | Use `docs/reviews/mvp-control-doc-compression-untracked-residue-disposition-20260611.md`; no cleanup in this gate |
| `fund_agent/tools/` source-like residue | active next mainline residual | Controller + implementation owner | Source-like residue ownership gate |
| Manual smoke reports and PDFs outside accepted evidence chain | accepted residual | User/controller/runtime evidence owner | Deferred runtime/data residue disposition gate |
| Release/readiness cleanliness unproven | accepted residual | Release owner | Deferred release-readiness gate after accepted disposition |
| Any design/control inconsistency discovered later | potential residual | Design owner/controller | Separate design-truth-sync gate; do not modify `docs/design.md` in this gate |

## Recent Active Gate Ledger

| Gate | Status | Evidence | Next |
|---|---|---|---|
| `Control-doc compression / artifact hygiene planning gate` | accepted locally | Plan `docs/reviews/mvp-control-doc-compression-artifact-hygiene-plan-20260611.md`; DS/MiMo plan reviews; controller judgment `ACCEPT_WITH_AMENDMENTS`; checkpoint `7365e2b` | Implementation accepted at `693638b` |
| `Control-doc compression / artifact hygiene implementation gate` | accepted locally | Implementation evidence, DS/MiMo reviews, controller judgment `ACCEPT_WITH_REVIEW_CHANNEL_RESIDUAL`; checkpoint `693638b` | Source-like residue ownership gate for `fund_agent/tools/` |

## Historical Evidence Index

Historical release-maintenance ledgers, superseded provider evidence, older PR/release notes and long accepted artifact lists are no longer active control surface. Use these evidence-chain entry points:

- `docs/reviews/mvp-control-doc-compression-accepted-artifact-index-20260611.md`
- `docs/reviews/mvp-control-doc-compression-historical-ledger-index-20260611.md`
- `docs/archive/implementation-control-release-maintenance-ledger-20260527.md`

Historical entries cannot override current phase, current gate, next entry point, `AGENTS.md`, `docs/design.md`, `docs/current-startup-packet.md` or the current sections of this document.

## Design / Control Alignment Rules

1. If README, `AGENTS.md`, `docs/design.md`, this control document and implementation conflict, resolve by current code facts plus reviewed control/design gates; do not keep dual口径.
2. Future design may be recorded only with explicit status labels: `当前已实现`, `已接受的未来设计`, or `候选/研究输入`.
3. This document remains the control truth for current phase, current gate, accepted artifact summaries, residual owners and next entry point.
4. Evidence-chain artifacts under `docs/reviews/` and `docs/archive/` are auditable support material, not architecture truth.

## Resume Checklist

1. Run `git status --branch --short` and `git status --short` only if status verification is needed.
2. Read `AGENTS.md`, `docs/current-startup-packet.md` and this file before choosing any next action.
3. For historical accepted evidence, use the accepted artifact index and historical ledger index.
4. Do not run live/provider/extractor/golden/readiness/release commands unless a separate reviewed gate explicitly authorizes them.
5. Do not import, stage, promote, clean or delete `fund_agent/tools/` until the source-like residue ownership gate is reviewed and accepted.
