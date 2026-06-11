# 基金行为教练 Agent - 实施总控文档

> **版本**: v2.7-control-compressed
> **日期**: 2026-06-11
> **规则真源**: `AGENTS.md`
> **设计真源**: `docs/design.md`
> **控制真源**: `docs/implementation-control.md`
> **短启动入口**: `docs/current-startup-packet.md`
> **当前状态**: `MVP typed-template-to-agent report generation stabilization phase`。`Control-doc compression / artifact hygiene implementation gate` 已在本地 checkpoint `693638b` 接受，controller verdict 为 `ACCEPT_WITH_REVIEW_CHANNEL_RESIDUAL`。`Source-like residue ownership implementation gate for fund_agent/tools` 已在本地 checkpoint `11040bd` 接受，controller verdict 为 `ACCEPT`。`EID source provenance truth alignment gate` 已在本地 checkpoint `2cee618` 接受，controller verdict 为 `ACCEPT_WITH_RESIDUALS`。`LLM execution request validation ordering gate` 已在本地 checkpoint `336081e` 接受，controller verdict 为 `ACCEPT_WITH_RESIDUALS`。`UI-Service-Host boundary reconciliation gate` 已在本地 checkpoint `8ff20ed` 接受，controller verdict 为 `ACCEPT_WITH_RESIDUALS`。`Runtime artifact disposition / ignore-rule gate` 已在本地 checkpoint `6bef193` 接受，controller verdict 为 `ACCEPT_WITH_RESIDUALS`。`Release-readiness cleanliness planning gate` 已在本地 checkpoint `1bbcd19` 接受，controller verdict 为 `ACCEPT_WITH_AMENDMENTS`。`Release-readiness cleanliness evidence gate` 已在本地 checkpoint `d0d9672` 接受，controller verdict 为 `ACCEPT_WITH_RESIDUALS_NOT_READY`。`Release-readiness blocker disposition planning gate` 已在本地 checkpoint `e41981a` 接受，controller verdict 为 `ACCEPT_WITH_RESIDUALS`。`Review-artifact provenance disposition evidence gate` 已在本地 checkpoint `9e0e540` 接受，controller verdict 为 `ACCEPT_WITH_RESIDUALS_NOT_READY`。`Review-artifact residual acceptance planning gate` 已在本地 checkpoint `f87edb5` 接受，controller verdict 为 `ACCEPT_WITH_NONBLOCKING_RESIDUALS`。`EID source provenance implementation closeout gate` 已在本地 checkpoint `12f506f` 接受，controller verdict 为 `ACCEPT`。`Multi-year annual analysis productization planning gate` 已在本地 checkpoint `26ed466` 接受，controller verdict 为 `ACCEPT_WITH_NONBLOCKING_RESIDUALS`。`Multi-year annual analysis productization implementation gate` 已在本地 checkpoint `61ab780` 接受，controller verdict 为 `ACCEPT_WITH_RESIDUALS`。`Controlled live 2021-2025 annual-period evidence planning gate` 已在本地 checkpoint `4f8908b` 接受，controller verdict 为 `ACCEPT_WITH_NONBLOCKING_RESIDUALS`。`Controlled live 2021-2025 annual-period evidence execution gate` 已在本地 checkpoint `271a052` 接受，controller verdict 为 `ACCEPT_WITH_RESIDUALS`。`Multi-year annual narrative writer/reporting planning gate` 已在本地 checkpoint `8682859` 接受，controller verdict 为 `ACCEPT_WITH_REVIEW_CHANNEL_RESIDUAL`；当前推荐主线入口是 `multi-year annual narrative writer/reporting implementation gate`。

---

## Startup Packet

短恢复入口见 `docs/current-startup-packet.md`。本文档前部只保留当前控制面；accepted artifact 长表和 historical ledger 已降级为 evidence-chain index：

- Accepted artifact index: `docs/reviews/mvp-control-doc-compression-accepted-artifact-index-20260611.md`
- Historical ledger index: `docs/reviews/mvp-control-doc-compression-historical-ledger-index-20260611.md`
- Untracked residue disposition: `docs/reviews/mvp-control-doc-compression-untracked-residue-disposition-20260611.md`
- Long-run phaseflow startup: `docs/reviews/mvp-long-run-phaseflow-startup-20260611-115345.md`

这些 index 不是设计真源，不覆盖 `AGENTS.md`、`docs/design.md`、`docs/current-startup-packet.md` 或本文档当前控制面。

## Current Truth Guardrails

- `AGENTS.md` 是最高优先级执行规则真源。
- `docs/design.md` 是设计真源；multi-year annual analysis productization implementation 和 controlled live 2021-2025 annual-period evidence 已完成 truth-doc sync。
- 当前 phase 是 `MVP typed-template-to-agent report generation stabilization phase`。
- 当前 template contract authored truth source 是 `docs/fund-analysis-template-draft.md` canonical `TEMPLATE_CONTRACT_MANIFEST_JSON`。
- 当前目标架构仍是 `UI -> Service -> Host -> Agent`。
- 当前默认生产主链路仍是确定性 `fund-analysis analyze/checklist`。
- 当前 `fund-analysis analyze-annual-period` 是确定性 multi-year annual product path：target year 走现有单年 `analyze()`，optional prior years 由 Fund 层通过 `FundDocumentRepository` 加载为 `AnnualEvidenceBundle`，CLI 输出 target-year Markdown 加 evidence summary。Controlled live evidence 已对 `004393 / 2021-2025` 单样本接受：五年均 available、EID single-source、fallback disabled/unused。Annual-period narrative writer/reporting implementation plan 已在 `8682859` 接受，但 formal annual-period report body 尚未实现为当前代码事实。
- 当前 `--use-llm` 路径是显式 opt-in、provider-backed、fail-closed；不提供 deterministic fallback。
- 当前 annual-report source policy 是 EID single-source operational no-live implementation。Fallback invocation、Eastmoney/fund-company/CNINFO source expansion、fixture projection、golden/readiness promotion、additional source acquisition、provider/default/runtime/budget/config change、chapter live acceptance、full cross-year narrative writer/reporting、score-loop、release/merge/mark-ready 均未由本 gate 授权。
- 所有业务参数必须通过 typed request / contract / config 显式声明，禁止通过 `extra_payload` 传递显式参数。
- 生产年报访问必须通过 `FundDocumentRepository`；Service、UI、Host、renderer、quality gate 不得直接调用具体来源、PDF cache 或下载 helper。

## Current Gate

| Field | State |
|---|---|
| Active gate | `multi-year annual narrative writer/reporting implementation gate` |
| Classification | `heavy` because accepted implementation changes user-facing `analyze-annual-period` report output |
| Accepted input | Multi-year annual analysis productization implementation evidence `docs/reviews/mvp-multi-year-annual-analysis-productization-implementation-evidence-20260611.md`; controller judgment `docs/reviews/mvp-multi-year-annual-analysis-productization-implementation-controller-judgment-20260611-175745.md`; checkpoint `61ab780`; controlled live execution evidence `docs/reviews/mvp-controlled-live-2021-2025-annual-period-evidence-execution-evidence-20260611.md`; execution controller judgment `docs/reviews/mvp-controlled-live-2021-2025-annual-period-evidence-execution-controller-judgment-20260611-231045.md`; checkpoint `271a052`; annual narrative/reporting plan `docs/reviews/mvp-multi-year-annual-narrative-writer-reporting-plan-20260611.md`; DS/MiMo reviews; DS targeted re-review; plan controller judgment `docs/reviews/mvp-multi-year-annual-narrative-writer-reporting-plan-controller-judgment-20260611-233310.md`; checkpoint `8682859` |
| Implementation objective | Implement accepted deterministic annual-period narrative/reporting plan: explicit annual-period report field, CLI annual-period report body after metadata header, Fund-owned renderer from typed in-memory annual evidence |
| Implementation status | Planning accepted; implementation not started in control truth. Current code still outputs target-year Markdown plus annual evidence summary |
| Next entry point | Implementation worker for accepted annual narrative/reporting plan; no live/provider/LLM/source-policy/release work is authorized |

## Long-run Phaseflow Queue

Controller startup artifact: `docs/reviews/mvp-long-run-phaseflow-startup-20260611-115345.md`.

Recommended mainline order:

1. `Source-like residue ownership gate for fund_agent/tools`
2. `EID source provenance truth alignment gate`
3. `LLM execution request validation ordering gate`
4. `UI-Service-Host boundary reconciliation gate`
5. `Runtime artifact disposition / ignore-rule planning gate`
6. `Release-readiness cleanliness gate`

Deferred entries requiring separate reviewed authorization:

- controlled live EID evidence gate
- live provider / LLM acceptance gate
- extractor/golden/readiness promotion gates
- fallback/source expansion design gate
- full Agent tool-loop/runtime expansion gate
- durable Host session/resume/memory/outbox gate

## Accepted Control-doc Compression Write Set

- `docs/implementation-control.md`
- `docs/current-startup-packet.md`
- `docs/reviews/mvp-control-doc-compression-accepted-artifact-index-20260611.md`
- `docs/reviews/mvp-control-doc-compression-historical-ledger-index-20260611.md`
- `docs/reviews/mvp-control-doc-compression-untracked-residue-disposition-20260611.md`
- `docs/reviews/mvp-control-doc-compression-artifact-hygiene-implementation-evidence-20260611.md`

## Non-goal Reminder

The accepted multi-year annual analysis productization implementation still does not authorize:

- `.gitignore` edits
- `docs/design.md`, README or control-truth changes outside controller status sync
- source/test/runtime behavior outside accepted annual narrative writer/reporting implementation plan and subsequent reviewed gates
- reviewer/controller artifact creation outside the accepted implementation/review write set
- delete, move, archive, clean, ignore, import, stage, promote, commit, push, PR, merge, mark-ready or release-state actions
- additional live EID/network/PDF/FDR/FundDocumentRepository/helper/fallback/provider/LLM/extractor/analyze/checklist/golden/readiness/score-loop/release commands beyond accepted evidence checkpoint `271a052`
- provider default changes, runtime budget changes, live provider acceptance, retry/fallback semantics, external PR state, or release-readiness status changes
- Host durable session/resume/memory/reply outbox, Agent full tool-loop/runtime expansion, UI direct Host/Agent calls, or Service direct source/cache/PDF calls
- treating arbitrary untracked workspace residue as proof, accepted fixture, product scope, release evidence or readiness pass

## Current Accepted Artifact Summary

The current control surface keeps only gate-family summaries. The evidence-chain reconstruction path is `docs/reviews/mvp-control-doc-compression-accepted-artifact-index-20260611.md`.

| Gate family | Accepted status | Current relevance | Residual owner / deferred gate |
|---|---|---|---|
| Control-doc compression / artifact hygiene | Planning accepted locally at `7365e2b`; implementation accepted locally at `693638b` | Current compressed control surface and index artifacts | Review-channel/worker-channel residuals accepted; no further action unless future handoff reliability gate is requested |
| EID single-source operational hardening | Accepted locally across failure-branch evidence, helper repair, controlled retry, metadata docs-sync, Source Provenance v2 truth alignment at `2cee618` and wording closeout at `12f506f` | Current annual-report source policy and public provenance projection | Fallback/source expansion and additional acquisition deferred |
| Small golden / extractor correctness | Accepted locally through current-consumable row-shape and extractor surfaces | Current extractor evidence baseline for named rows/contracts | Fixture projection, promotion and release/readiness deferred |
| Typed template truth-source replacement | Accepted locally; canonical JSON in template draft is authored truth source | Current template contract truth source | Public chapter id/runtime expansion unchanged |
| Agent engine / Host governance | Accepted locally for no-live Agent body runner and process-local Host lifecycle boundary | Current `--use-llm` architecture boundary | Full Agent tool-loop/runtime expansion deferred |
| Provider/runtime/LLM diagnostics | Accepted locally as fail-closed diagnostics, historical provider evidence and LLM request validation ordering at `336081e` | Informs provider residual routing; current builder validates request/contract before provider construction | Live acceptance, runtime default changes and LLM path request-parity consistency deferred |
| Multi-year annual analysis productization | Accepted locally at `61ab780`; live evidence accepted at `271a052` for `004393 / 2021-2025`; narrative/reporting plan accepted at `8682859` | Current deterministic `analyze-annual-period` product path, Fund `AnnualEvidenceBundle`, Chapter 5 cross-year fact projection, docs/tests and bounded single-sample live EID evidence; implementation gate now targets formal annual-period report body | Source identity extension, additional samples and coverage measurement residuals deferred |
| Release/readiness historical evidence | Evidence-chain only | Does not set current release/PR/readiness state | Release owner after residue disposition acceptance |

## Open Residuals

| Residual | Status | Owner | Next handling |
|---|---|---|---|
| Review-channel residual from accepted control-doc compression gate | accepted residual | Controller / agent setup owner | Re-run init-agents cleanup before next tmux-pane handoff; do not treat old pane content as review output |
| Worker-channel capacity/transport residual from accepted control-doc compression gate | accepted residual | Controller / worker channel owner | Future handoffs should verify completion channel; accepted artifacts remain valid through independent review |
| Untracked residue remains in workspace | accepted residual | Controller / artifact owners | Use `docs/reviews/mvp-control-doc-compression-untracked-residue-disposition-20260611.md`; no cleanup in this gate |
| `fund_agent/tools/` source-like residue | accepted; removed from working tree | Controller + implementation owner | Closed for exact residue; no further action unless it reappears |
| Manual smoke reports and PDFs outside accepted evidence chain | accepted residual | User/controller/runtime evidence owner | Deferred runtime/data residue disposition gate |
| Release/readiness cleanliness unproven | accepted residual | Release owner | Deferred release-readiness gate after accepted disposition |
| EID public provenance mismatch | accepted; closed for current implementation | Fund/source provenance owner | Closed by `2cee618`; public v2 projection now exposes `selected_source`, `source_mode`, `fallback_enabled` |
| Source provenance design/README wording drift (`mode` vs `source_mode`) | accepted; closed at `12f506f` | Design owner/controller | Historical review artifacts may still contain old wording as evidence chain only |
| LLM execution request validation ordering | accepted; closed for current implementation | Service/LLM execution owner | Closed by `336081e`; LLM path parity with deterministic `_validate_request()` deferred |
| UI-Service-Host boundary reconciliation | accepted; closed for current implementation | Service/Host boundary owner | Closed by `8ff20ed`; future Host durable and Agent full runtime expansion remain separate |
| Runtime artifact disposition / ignore-rule planning | accepted; closed for non-destructive disposition | Controller / artifact owners | Closed by `6bef193`; untracked residue remains release/readiness blocker with owners/next gates |
| Release-readiness cleanliness planning | accepted locally at `1bbcd19` | Release owner / controller | Evidence gate may proceed under accepted local non-destructive matrix |
| Release-readiness cleanliness evidence | accepted locally at `d0d9672`; result `NOT_READY` | Release owner / controller | Blocks readiness claim; route to blocker disposition planning |
| Release-readiness blocker disposition planning | accepted locally at `e41981a` | Release owner / controller | Routes first follow-up to review-artifact provenance disposition evidence |
| Review-artifact provenance disposition evidence | accepted locally at `9e0e540`; result `NOT_READY` | Controller / artifact owners | Exact paths classified, but no current/historical chain acceptance; route to residual acceptance planning |
| Review-artifact residual acceptance planning | accepted locally at `f87edb5`; planning only | Controller / artifact owners | Evidence gate deferred by user-directed sequencing; no residual/readiness accepted |
| Review-artifact residual acceptance evidence | deferred residual | Controller / artifact owners | Future reviewed evidence gate if user/controller returns to release-readiness residue closure |
| EID source provenance implementation closeout | accepted locally at `12f506f` | Fund/source provenance owner + controller | Closed; Source Provenance v2 wording synced in design/README |
| Multi-year annual analysis productization implementation | accepted locally at `61ab780`; `ACCEPT_WITH_RESIDUALS` | Product/Service/Fund owner + controller | Closed for product path; deferred full cross-year narrative writer/reporting, source identity extension, additional samples and coverage measurement |
| Controlled live 2021-2025 annual-period evidence | execution accepted locally at `271a052`; `ACCEPT_WITH_RESIDUALS` | Controller / evidence owner | Closed for single sample `004393`; additional live samples/readiness remain separate |
| Multi-year annual narrative writer/reporting | planning accepted locally at `8682859`; implementation not started | Product/reporting owner | Current mainline implementation gate under accepted plan |
| Deepreview-derived long-run gates | queued residual | Controller / future gate owners | Use `docs/reviews/mvp-long-run-phaseflow-startup-20260611-115345.md`; follow queue order |
| Any design/control inconsistency discovered later | potential residual | Design owner/controller | Separate design-truth-sync gate; do not modify `docs/design.md` in this gate |

## Recent Active Gate Ledger

| Gate | Status | Evidence | Next |
|---|---|---|---|
| `Control-doc compression / artifact hygiene planning gate` | accepted locally | Plan `docs/reviews/mvp-control-doc-compression-artifact-hygiene-plan-20260611.md`; DS/MiMo plan reviews; controller judgment `ACCEPT_WITH_AMENDMENTS`; checkpoint `7365e2b` | Implementation accepted at `693638b` |
| `Control-doc compression / artifact hygiene implementation gate` | accepted locally | Implementation evidence, DS/MiMo reviews, controller judgment `ACCEPT_WITH_REVIEW_CHANNEL_RESIDUAL`; checkpoint `693638b` | Source-like residue ownership gate for `fund_agent/tools/` |
| `Long-run phaseflow startup` | opened | Controller startup artifact `docs/reviews/mvp-long-run-phaseflow-startup-20260611-115345.md`; review input `docs/reviews/repo-review-20260611-114133.md` | Planning worker for `Source-like residue ownership gate for fund_agent/tools` |
| `Source-like residue ownership planning gate for fund_agent/tools` | accepted | Plan, MiMo review, DS review and controller judgment `docs/reviews/mvp-source-like-residue-ownership-plan-controller-judgment-20260611-122048.md`; verdict `ACCEPT_WITH_EXPLICIT_DELETE_AUTH_REQUIRED` | User-authorized bounded implementation gate |
| `Source-like residue ownership implementation gate for fund_agent/tools` | accepted locally | Implementation evidence, MiMo review, DS review and controller judgment `docs/reviews/mvp-source-like-residue-ownership-implementation-controller-judgment-20260611-125554.md`; verdict `ACCEPT`; checkpoint `11040bd` | EID source provenance truth alignment gate |
| `EID source provenance truth alignment planning gate` | accepted | Plan, MiMo review, DS review and controller judgment `docs/reviews/mvp-eid-source-provenance-truth-alignment-plan-controller-judgment-20260611-130744.md`; verdict `ACCEPT_WITH_AMENDMENTS` | Implementation accepted at `2cee618` |
| `EID source provenance truth alignment implementation gate` | accepted locally | Implementation evidence, MiMo review, DS review and controller judgment `docs/reviews/mvp-eid-source-provenance-truth-alignment-implementation-controller-judgment-20260611-132708.md`; verdict `ACCEPT_WITH_RESIDUALS`; checkpoint `2cee618` | LLM execution request validation ordering gate |
| `LLM execution request validation ordering planning gate` | accepted | Plan, MiMo review, DS review and controller judgment `docs/reviews/mvp-llm-execution-request-validation-ordering-plan-controller-judgment-20260611-133729.md`; verdict `ACCEPT_WITH_AMENDMENTS`; checkpoint `e9f944d` | Implementation accepted at `336081e` |
| `LLM execution request validation ordering implementation gate` | accepted locally | Implementation evidence, MiMo review, DS review and controller judgment `docs/reviews/mvp-llm-execution-request-validation-ordering-implementation-controller-judgment-20260611-134702.md`; verdict `ACCEPT_WITH_RESIDUALS`; checkpoint `336081e` | UI-Service-Host boundary reconciliation gate |
| `UI-Service-Host boundary reconciliation planning gate` | accepted locally | Plan, MiMo review, DS review and controller judgment `docs/reviews/mvp-ui-service-host-boundary-reconciliation-plan-controller-judgment-20260611-140916.md`; verdict `ACCEPT_WITH_AMENDMENTS`; checkpoint `d6fe6db` | Implementation worker for accepted write set |
| `UI-Service-Host boundary reconciliation implementation gate` | accepted locally | Implementation evidence, MiMo review, DS review and controller judgment `docs/reviews/mvp-ui-service-host-boundary-reconciliation-implementation-controller-judgment-20260611-144133.md`; verdict `ACCEPT_WITH_RESIDUALS`; checkpoint `8ff20ed` | Runtime artifact disposition / ignore-rule planning gate |
| `Runtime artifact disposition / ignore-rule planning gate` | accepted locally | Plan, MiMo review, DS review and controller judgment `docs/reviews/mvp-runtime-artifact-disposition-ignore-rule-plan-controller-judgment-20260611-145413.md`; verdict `ACCEPT_WITH_AMENDMENTS`; checkpoint `b4ab635` | Implementation/disposition worker under accepted plan boundaries |
| `Runtime artifact disposition / ignore-rule implementation/disposition gate` | accepted locally | Implementation evidence, MiMo review, DS review and controller judgment `docs/reviews/mvp-runtime-artifact-disposition-ignore-rule-implementation-controller-judgment-20260611-150616.md`; verdict `ACCEPT_WITH_RESIDUALS`; checkpoint `6bef193` | Release-readiness cleanliness gate |
| `Release-readiness cleanliness planning gate` | accepted locally | Plan, MiMo review, DS review and controller judgment `docs/reviews/mvp-release-readiness-cleanliness-plan-controller-judgment-20260611-152127.md`; verdict `ACCEPT_WITH_AMENDMENTS`; checkpoint `1bbcd19` | Release-readiness cleanliness evidence gate |
| `Release-readiness cleanliness evidence gate` | accepted locally; not ready | Evidence, MiMo review, DS review and controller judgment `docs/reviews/mvp-release-readiness-cleanliness-evidence-controller-judgment-20260611-153309.md`; verdict `ACCEPT_WITH_RESIDUALS_NOT_READY`; checkpoint `d0d9672` | Release-readiness blocker disposition planning gate |
| `Release-readiness blocker disposition planning gate` | accepted locally | Plan, MiMo review, DS review and controller judgment `docs/reviews/mvp-release-readiness-blocker-disposition-plan-controller-judgment-20260611-155001.md`; verdict `ACCEPT_WITH_RESIDUALS`; checkpoint `e41981a` | Review-artifact provenance disposition evidence gate |
| `Review-artifact provenance disposition evidence gate` | accepted locally; not ready | Evidence, MiMo review, DS review and controller judgment `docs/reviews/mvp-review-artifact-provenance-disposition-evidence-controller-judgment-20260611-160126.md`; verdict `ACCEPT_WITH_RESIDUALS_NOT_READY`; checkpoint `9e0e540` | Review-artifact residual acceptance planning gate |
| `Review-artifact residual acceptance planning gate` | accepted locally; planning only | Plan, MiMo review, DS review and controller judgment `docs/reviews/mvp-review-artifact-residual-acceptance-plan-controller-judgment-20260611-162326.md`; verdict `ACCEPT_WITH_NONBLOCKING_RESIDUALS`; checkpoint `f87edb5` | User-directed EID source provenance implementation closeout gate |
| `EID source provenance implementation closeout gate` | accepted locally | Evidence, MiMo review, DS review and controller judgment `docs/reviews/mvp-eid-source-provenance-closeout-controller-judgment-20260611-163234.md`; verdict `ACCEPT`; checkpoint `12f506f` | Multi-year annual analysis productization planning gate |
| `Multi-year annual analysis productization planning gate` | accepted locally | Plan, MiMo review, DS review and controller judgment `docs/reviews/mvp-multi-year-annual-analysis-productization-plan-controller-judgment-20260611-165124.md`; verdict `ACCEPT_WITH_NONBLOCKING_RESIDUALS`; checkpoint `26ed466` | Multi-year annual analysis productization implementation gate |
| `Multi-year annual analysis productization implementation gate` | accepted locally | Implementation evidence, MiMo review, DS review and controller judgment `docs/reviews/mvp-multi-year-annual-analysis-productization-implementation-controller-judgment-20260611-175745.md`; verdict `ACCEPT_WITH_RESIDUALS`; checkpoint `61ab780` | Controlled live 2021-2025 annual-period evidence planning gate |
| `Controlled live 2021-2025 annual-period evidence planning gate` | accepted locally | Plan, DS/MiMo reviews, targeted re-reviews and controller judgment `docs/reviews/mvp-controlled-live-2021-2025-annual-period-evidence-plan-controller-judgment-20260611-225543.md`; verdict `ACCEPT_WITH_NONBLOCKING_RESIDUALS`; checkpoint `4f8908b` | Separately opened controlled live 2021-2025 annual-period evidence execution gate |
| `Controlled live 2021-2025 annual-period evidence execution gate` | accepted locally | Evidence, DS/MiMo reviews and controller judgment `docs/reviews/mvp-controlled-live-2021-2025-annual-period-evidence-execution-controller-judgment-20260611-231045.md`; verdict `ACCEPT_WITH_RESIDUALS`; checkpoint `271a052` | Multi-year annual narrative writer/reporting planning gate |
| `Multi-year annual narrative writer/reporting planning gate` | accepted locally | Plan, DS review, MiMo review, DS targeted re-review and controller judgment `docs/reviews/mvp-multi-year-annual-narrative-writer-reporting-plan-controller-judgment-20260611-233310.md`; verdict `ACCEPT_WITH_REVIEW_CHANNEL_RESIDUAL`; checkpoint `8682859` | Multi-year annual narrative writer/reporting implementation gate |

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
5. Current mainline is multi-year annual narrative writer/reporting implementation after accepted planning checkpoint `8682859`. Do not claim readiness, push, PR, run additional live/provider/EID/PDF/FDR/analyze/checklist/golden/release commands, read report/PDF contents, or clean residue unless a reviewed follow-up gate explicitly authorizes it.
