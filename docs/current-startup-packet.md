# Current Startup Packet

Purpose: short resume entry for the `MVP typed-template-to-agent report generation stabilization phase`. This file is a control packet, not a historical ledger and not a design truth source.

## 1. Read Order

1. `AGENTS.md`
2. `docs/design.md`
3. `docs/implementation-control.md`
4. `docs/fund-analysis-template-draft.md`
5. Evidence-chain indexes only when needed:
   - `docs/reviews/mvp-control-doc-compression-accepted-artifact-index-20260611.md`
   - `docs/reviews/mvp-control-doc-compression-historical-ledger-index-20260611.md`
   - `docs/reviews/mvp-control-doc-compression-untracked-residue-disposition-20260611.md`

`docs/reviews/` and `docs/archive/` are evidence chain only. They do not override `AGENTS.md`, `docs/design.md`, this startup packet, or `docs/implementation-control.md`.

## 2. Current Mainline

| Field | State |
|---|---|
| Current phase | `MVP typed-template-to-agent report generation stabilization phase` |
| Current active gate | Waiting for separately opened `controlled live 2021-2025 annual-period evidence execution gate` |
| Gate classification | Future controlled-live execution is `heavy` unless controller narrows it before opening |
| Current accepted checkpoint | Controlled live 2021-2025 annual-period evidence planning accepted locally at `4f8908b` by controller judgment `docs/reviews/mvp-controlled-live-2021-2025-annual-period-evidence-plan-controller-judgment-20260611-225543.md`; release/readiness result remains `NOT_READY` |
| Implementation status | EID Source Provenance v2 wording is accepted. Multi-year annual analysis productization is implemented as deterministic no-live product capability: Service request/result, Fund annual evidence bundle, Chapter 5 projection and CLI `analyze-annual-period` |
| Next entry point | Separately opened controlled live 2021-2025 annual-period evidence execution gate. Do not run live commands until that controlled-live gate is explicitly opened |
| Control truth | `docs/implementation-control.md` |
| Design truth | `docs/design.md` |
| Template truth | `docs/fund-analysis-template-draft.md` canonical `TEMPLATE_CONTRACT_MANIFEST_JSON` |
| Accepted artifact index | `docs/reviews/mvp-control-doc-compression-accepted-artifact-index-20260611.md` |
| Historical ledger index | `docs/reviews/mvp-control-doc-compression-historical-ledger-index-20260611.md` |
| Residue disposition index | `docs/reviews/mvp-control-doc-compression-untracked-residue-disposition-20260611.md` |
| Long-run phaseflow startup | `docs/reviews/mvp-long-run-phaseflow-startup-20260611-115345.md` |

## 3. Current Control Truth

- Current production default remains deterministic `fund-analysis analyze/checklist`: structured extraction, deterministic analysis, template rendering, programmatic audit and FQ0-FQ6 quality gate.
- Current `--use-llm` path remains explicit opt-in and fail-closed: `CLI -> Service prepares FundLLMExecutionRequest / ExecutionContract -> Host runner -> Service -> Agent body runner -> fund_agent/fund -> provider HTTP call`.
- Current `fund-analysis analyze-annual-period` path is deterministic no-live product capability: CLI calls Service `analyze_multi_year_annual()`, Service runs target-year `analyze()` and requests Fund-owned `AnnualEvidenceScopeRequest`, and Fund builds `AnnualEvidenceBundle` by loading optional prior years through `FundDocumentRepository`.
- Current Agent implementation owns no-live body-chapter execution mechanics: contracts, ToolTrace, Fund tool adapters, repair policy, body runner and final assembly readiness.
- Host remains lifecycle-only and business-opaque. Service owns use-case orchestration, ExecutionContract semantics, provider construction/runtime ceilings and final product fail-closed mapping. Fund owns domain rules, CHAPTER_CONTRACT / preferred_lens / ITEM_RULE semantics, extraction and audit.
- EID single-source annual-report access is current operational source policy. Eastmoney, fund-company/CDN, CNINFO, fallback invocation, fixture projection, golden/readiness promotion, additional source acquisition, score-loop, release/merge/mark-ready and PR external state are not authorized by this gate.

## 4. Current Gate Scope

The implementation checkpoint `61ab780` has accepted the no-live formal 2021-2025 annual-report analysis capability from `docs/reviews/mvp-multi-year-annual-analysis-productization-plan-20260611.md`, replacing manual five single-year runs plus manual merge with an explicit typed product path. The follow-up controlled-live planning checkpoint `4f8908b` accepted the command matrix, stop conditions and evidence artifact schema for a future 2021-2025 annual-period live evidence execution gate.

Accepted implementation scope:

- Service typed request/result and product orchestration for multi-year annual analysis
- Fund-owned annual evidence scope/loading/bundle/cross-year facts
- additive Chapter 5 cross-year fact projection
- CLI product surface `fund-analysis analyze-annual-period`
- targeted deterministic tests and README updates triggered by actual source changes
- implementation evidence / review / controller judgment artifacts under `docs/reviews/`
- this startup packet, `docs/design.md` and `docs/implementation-control.md` for truth-doc sync

Still explicitly out of scope unless a future reviewed gate authorizes it:

- `.gitignore`
- reports, PDF/document corpus
- source/test/runtime behavior outside the accepted multi-year productization plan
- reviewer or controller artifacts outside the accepted implementation/review write set
- delete, move, archive, clean, ignore, import, stage, promote, commit, push, PR or merge actions
- live EID/network/PDF/FDR/FundDocumentRepository/helper/fallback/provider/LLM/extractor/analyze/checklist/golden/readiness/score-loop/release commands; the accepted planning matrix does not itself authorize execution

## 5. Current Accepted Artifact Summary

The active startup surface keeps only current-useful accepted facts. Full evidence-chain grouping is in `docs/reviews/mvp-control-doc-compression-accepted-artifact-index-20260611.md`.

| Gate family | Current relevance |
|---|---|
| Control-doc compression / artifact hygiene | Planning gate accepted locally at `7365e2b`; implementation accepted locally at `693638b`; controller judgment `ACCEPT_WITH_REVIEW_CHANNEL_RESIDUAL` |
| EID single-source operational hardening | Current annual-report source policy, helper repair evidence and public Source Provenance v2 truth alignment/wording are accepted; fallback/source expansion remains deferred |
| Small golden / extractor correctness | Current-consumable row-field extractor surfaces are accepted; fixture projection and promotion remain deferred |
| Typed template truth-source replacement | `docs/fund-analysis-template-draft.md` canonical JSON is accepted authored template contract truth source |
| Agent engine / Host governance | Current no-live Agent body runner and process-local Host lifecycle boundary are accepted; full tool-loop/runtime expansion remains future |
| Provider/runtime/LLM diagnostics | Fail-closed provider path, diagnostics and LLM request validation ordering are accepted; live acceptance and runtime default changes remain unproven or deferred |
| Release/readiness historical evidence | Evidence chain only; does not set current release/PR/readiness state |

## 6. Open Residuals

| Residual | Owner | Next gate | Current blocker? |
|---|---|---|---|
| Review-channel residual from current gate | Controller / agent setup owner | Re-run init-agents cleanup before next tmux-pane handoff | Does not block accepted checkpoint; affects future handoff reliability |
| Untracked workspace residue | Controller / artifact owners | Artifact-specific disposition gates listed in residue disposition index | Does not block accepted control-doc compression; blocks release/readiness until accepted disposition |
| `fund_agent/tools/` source-like residue | Controller + implementation owner | Closed; evidence in `docs/reviews/mvp-source-like-residue-ownership-implementation-evidence-20260611.md` | Accepted; no longer blocks release/readiness for this exact residue |
| Manual smoke reports and PDFs outside accepted evidence chain | User/controller/runtime evidence owner | Runtime/data artifact disposition gates | Blocks release/readiness if unclassified |
| Deepreview-derived long-run gates | Controller / future gate owners | Phaseflow queue in `docs/reviews/mvp-long-run-phaseflow-startup-20260611-115345.md` plus user-directed productization queue | Follow queue order unless superseded by current control truth; productization implementation is accepted at `61ab780` |
| EID public provenance mismatch | Fund/source provenance owner | Closed by `2cee618`; closeout wording sync accepted at `12f506f` | Accepted for current implementation |
| Source provenance design/README wording drift (`mode` vs `source_mode`) | Design/controller owner | Closed by `12f506f`; historical review artifacts may still contain old wording as evidence chain only | Accepted; no current blocker |
| LLM execution request validation ordering | Service/LLM execution owner | Closed by `336081e`; LLM path parity with deterministic `_validate_request()` remains separate | Accepted for current implementation |
| UI-Service-Host boundary reconciliation | Service/Host boundary owner | Closed by `8ff20ed`; residual future Host/Agent expansion remains separate | Accepted for current implementation |
| Runtime artifact disposition / ignore-rule planning | Controller / artifact owners | Closed by `6bef193`; residue remains visible with owners/next gates | Accepted for current non-destructive disposition |
| Release-readiness cleanliness planning | Release owner / controller | Plan accepted at `1bbcd19`; evidence gate not started | Accepted planning checkpoint |
| Release-readiness cleanliness evidence | Release owner / controller | Evidence accepted at `d0d9672`; result `NOT_READY` | Accepted evidence checkpoint; blocks readiness claim |
| Release-readiness blocker disposition planning | Release owner / controller | Plan accepted at `e41981a`; routes first evidence gate to review-artifact provenance | Accepted planning checkpoint |
| Review-artifact provenance disposition evidence | Controller / artifact owners | Evidence accepted at `9e0e540`; no path accepted as current/historical chain; result remains `NOT_READY` | Accepted evidence checkpoint |
| Review-artifact residual acceptance planning | Controller / artifact owners | Plan accepted at `f87edb5`; evidence gate deferred by user-directed sequencing | Accepted planning checkpoint; release/readiness remains `NOT_READY` |
| Review-artifact residual acceptance evidence | Controller / artifact owners | Deferred residual acceptance evidence gate | Deferred; not current mainline |
| EID source provenance implementation closeout | Fund/source provenance owner + controller | Closed by `12f506f`; Source Provenance v2 wording synced in design/README | Accepted closeout checkpoint |
| Multi-year annual analysis productization | Product/Service/Fund owner + controller | Implementation accepted at `61ab780`; DS review accepted after follow-up, MiMo review accepted | Accepted with residuals; live annual-period evidence and narrative writer/reporting are deferred |
| Controlled live 2021-2025 annual-period evidence | Controller / future evidence owner | Execution gate using accepted plan `docs/reviews/mvp-controlled-live-2021-2025-annual-period-evidence-plan-20260611.md` | Planning accepted at `4f8908b`; execution still requires separate controlled-live opening |
| Any discovered design/control inconsistency | Controller/design owner | Separate design-truth-sync gate | Must be recorded as residual; `docs/design.md` remains untouched in this gate |
| Live EID/provider/extractor/golden/readiness/release work | Corresponding gate owner | Separate reviewed gate with explicit authorization | Not authorized here |

## 7. Resume Checklist

1. Run only allowed status/metadata checks if resuming from this checkpoint.
2. Read `docs/implementation-control.md` for current control truth.
3. Use the accepted artifact and historical ledger indexes for evidence-chain reconstruction.
4. Do not use arbitrary untracked residue as proof.
5. Next mainline is the separately opened controlled live 2021-2025 annual-period evidence execution gate after accepted planning checkpoint `4f8908b`. Do not claim readiness, push, PR, run live/provider/EID/PDF/FDR/analyze/checklist/golden/release commands, read report/PDF contents, or clean residue until that controlled-live execution gate is explicitly opened.
