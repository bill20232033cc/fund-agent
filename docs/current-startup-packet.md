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
| Current active gate | `Runtime/live report residue disposition metadata evidence gate` |
| Gate classification | `standard`; evidence only, non-live, metadata-only, no report-content proof, no PR/release external state |
| Current accepted checkpoint | Runtime/live report residue disposition planning accepted locally at `c681bee` by controller judgment `docs/reviews/mvp-runtime-live-report-residue-disposition-plan-controller-judgment-20260612-062606.md`; release/readiness result remains `NOT_READY` |
| Implementation status | EID Source Provenance v2 wording is accepted. Multi-year annual analysis productization is implemented as deterministic product capability: Service request/result, Fund annual evidence bundle, Chapter 5 projection, CLI `analyze-annual-period` and Fund-owned deterministic annual-period report renderer. Controlled live evidence for `004393 / 2021-2025` is accepted as a single-sample EID single-source/no-fallback evidence fact. Annual-period narrative writer/reporting is implemented and accepted. Review/audit residue evidence is accepted as metadata-only classification, but no path is accepted as source truth, release evidence or readiness proof |
| Next entry point | Evidence worker for `Runtime/live report residue disposition metadata evidence gate`. Controlled live annual-period narrative evidence is a separate explicitly authorized gate |
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
- Current `fund-analysis analyze-annual-period` path is deterministic product capability: CLI calls Service `analyze_multi_year_annual()`, Service runs target-year `analyze()` and requests Fund-owned `AnnualEvidenceScopeRequest`, Fund builds `AnnualEvidenceBundle` by loading optional prior years through `FundDocumentRepository`, and Fund-owned renderer produces a formal annual-period Markdown report from in-memory typed inputs. CLI stdout emits the metadata header first, then `result.annual_period_report.report_markdown`; `MultiYearAnnualAnalysisResult.report_markdown` remains the current-year report. Controlled live evidence is accepted for the single sample `004393 / 2021-2025`: all five years were available, `cross_year_fact_count=3`, `fallback_year_count=0`, and all five years emitted EID single-source/no-fallback provenance.
- Current Agent implementation owns no-live body-chapter execution mechanics: contracts, ToolTrace, Fund tool adapters, repair policy, body runner and final assembly readiness.
- Host remains lifecycle-only and business-opaque. Service owns use-case orchestration, ExecutionContract semantics, provider construction/runtime ceilings and final product fail-closed mapping. Fund owns domain rules, CHAPTER_CONTRACT / preferred_lens / ITEM_RULE semantics, extraction and audit.
- EID single-source annual-report access is current operational source policy. Eastmoney, fund-company/CDN, CNINFO, fallback invocation, fixture projection, golden/readiness promotion, additional source acquisition, score-loop, release/merge/mark-ready and PR external state are not authorized by this gate.

## 4. Current Gate Scope

The implementation checkpoint `61ab780` accepted the no-live formal 2021-2025 annual-report analysis capability from `docs/reviews/mvp-multi-year-annual-analysis-productization-plan-20260611.md`, replacing manual five single-year runs plus manual merge with an explicit typed product path. The controlled-live execution checkpoint `271a052` accepted `004393 / 2021-2025` as a bounded live EID single-source/no-fallback evidence fact for the current product path. The planning checkpoint `8682859` accepted `docs/reviews/mvp-multi-year-annual-narrative-writer-reporting-plan-20260611.md` as the implementation plan for formal deterministic annual-period narrative/reporting. The implementation checkpoint `b3254b3` accepted the formal deterministic annual-period report body and explicit `annual_period_report` result field. The planning checkpoint `1edf06b` accepted the non-live release-readiness residual/artifact disposition plan. The evidence checkpoint `387d16a` accepted review/audit residue metadata classification and keeps release/readiness `NOT_READY`. The planning checkpoint `c681bee` accepted runtime/live report residue metadata-only evidence planning.

Accepted implementation scope:

- Service typed request/result and product orchestration for multi-year annual analysis
- Fund-owned annual evidence scope/loading/bundle/cross-year facts
- additive Chapter 5 cross-year fact projection
- CLI product surface `fund-analysis analyze-annual-period`
- Fund-owned deterministic `annual_period_report.v1` renderer
- explicit `MultiYearAnnualAnalysisResult.annual_period_report`
- CLI metadata header followed by formal annual-period report body
- targeted deterministic tests and README updates triggered by actual source changes
- implementation evidence / review / controller judgment artifacts under `docs/reviews/`
- this startup packet, `docs/design.md` and `docs/implementation-control.md` for truth-doc sync
- release-readiness residual/artifact disposition plan, DS/MiMo reviews and controller judgment under `docs/reviews/`

Still explicitly out of scope unless a future reviewed gate authorizes it:

- `.gitignore`
- reports, PDF/document corpus
- source/test/runtime behavior outside future reviewed gates
- reviewer or controller artifacts outside the accepted implementation/review write set
- delete, move, archive, clean, ignore, import, stage, promote, commit, push, PR or merge actions
- additional live EID/network/PDF/FDR/FundDocumentRepository/helper/fallback/provider/LLM/extractor/analyze/checklist/golden/readiness/score-loop/release commands beyond the accepted `004393 / 2021-2025` evidence run

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
| Release-readiness residual/artifact disposition planning | Controller / artifact owners | Plan accepted at `1edf06b`; DS/MiMo reviews complete; controller judgment `ACCEPT_WITH_NONBLOCKING_AMENDMENTS` | Accepted planning checkpoint; release/readiness remains `NOT_READY` |
| Review-artifact residual acceptance evidence | Controller / artifact owners | Evidence accepted at `387d16a`; 36 paths classified as non-proof residue; no path accepted as source truth/release evidence/readiness proof | Accepted evidence checkpoint; release/readiness remains `NOT_READY` |
| Runtime/live report residue disposition planning | Runtime evidence owner / controller | Planning accepted at `c681bee`; controller judgment `docs/reviews/mvp-runtime-live-report-residue-disposition-plan-controller-judgment-20260612-062606.md` | Accepted planning checkpoint; release/readiness remains `NOT_READY` |
| Runtime/live report residue disposition metadata evidence | Runtime evidence owner / controller | Evidence gate under accepted plan `docs/reviews/mvp-runtime-live-report-residue-disposition-plan-20260612.md` | Current mainline |
| EID source provenance implementation closeout | Fund/source provenance owner + controller | Closed by `12f506f`; Source Provenance v2 wording synced in design/README | Accepted closeout checkpoint |
| Multi-year annual analysis productization | Product/Service/Fund owner + controller | Implementation accepted at `61ab780`; DS review accepted after follow-up, MiMo review accepted | Accepted with residuals; formal narrative/reporting implementation accepted separately at `b3254b3` |
| Controlled live 2021-2025 annual-period evidence | Controller / evidence owner | Execution accepted at `271a052`; evidence in `docs/reviews/mvp-controlled-live-2021-2025-annual-period-evidence-execution-evidence-20260611.md` | Accepted for single sample `004393`; additional samples/readiness remain deferred |
| Multi-year annual narrative writer/reporting | Product/reporting owner | Implementation accepted at `b3254b3`; controller judgment `docs/reviews/mvp-multi-year-annual-narrative-writer-reporting-implementation-controller-judgment-20260612-002524.md` | Accepted; additional live samples/readiness/source identity/coverage remain deferred |
| Any discovered design/control inconsistency | Controller/design owner | Separate design-truth-sync gate | Must be recorded as residual; `docs/design.md` remains untouched in this gate |
| Live EID/provider/extractor/golden/readiness/release work | Corresponding gate owner | Separate reviewed gate with explicit authorization | Not authorized here |

## 7. Resume Checklist

1. Run only allowed status/metadata checks if resuming from this checkpoint.
2. Read `docs/implementation-control.md` for current control truth.
3. Use the accepted artifact and historical ledger indexes for evidence-chain reconstruction.
4. Do not use arbitrary untracked residue as proof.
5. Next mainline is `Runtime/live report residue disposition metadata evidence gate` after accepted planning checkpoint `c681bee`. Do not claim readiness, push, PR, run additional live/provider/EID/PDF/FDR/analyze/checklist/golden/release commands, read report/PDF contents, or clean residue unless a reviewed follow-up gate explicitly authorizes it.
