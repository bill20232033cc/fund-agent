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
| Current active gate | `Runtime artifact disposition / ignore-rule planning gate` |
| Gate classification | `standard` |
| Current accepted checkpoint | Runtime artifact disposition / ignore-rule plan accepted locally at `b4ab635` by controller judgment `docs/reviews/mvp-runtime-artifact-disposition-ignore-rule-plan-controller-judgment-20260611-145413.md` |
| Implementation status | Plan accepted; implementation/disposition not started. Untracked residue remains unaccepted as proof, release evidence or source truth |
| Next entry point | Runtime artifact disposition / ignore-rule implementation/disposition gate under accepted plan; do not clean, delete, move, archive, ignore, stage, promote, edit `.gitignore` or treat runtime artifacts as evidence without accepted implementation scope and required authorization |
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
- Current Agent implementation owns no-live body-chapter execution mechanics: contracts, ToolTrace, Fund tool adapters, repair policy, body runner and final assembly readiness.
- Host remains lifecycle-only and business-opaque. Service owns use-case orchestration, ExecutionContract semantics, provider construction/runtime ceilings and final product fail-closed mapping. Fund owns domain rules, CHAPTER_CONTRACT / preferred_lens / ITEM_RULE semantics, extraction and audit.
- EID single-source annual-report access is current operational source policy. Eastmoney, fund-company/CDN, CNINFO, fallback invocation, fixture projection, golden/readiness promotion, additional source acquisition, score-loop, release/merge/mark-ready and PR external state are not authorized by this gate.

## 4. Current Gate Scope

The current entry is implementation/disposition planning follow-through for `Runtime artifact disposition / ignore-rule gate` under accepted plan checkpoint `b4ab635`. No cleanup, ignore-rule edit, archive, delete, promotion or release-readiness status change has been performed yet.

Allowed controller writes before implementation acceptance:

- implementation/evidence / review / controller judgment artifacts under `docs/reviews/`
- this startup packet and `docs/implementation-control.md` only for controller status sync

Still explicitly out of scope unless a future reviewed gate authorizes it:

- `docs/design.md`
- `.gitignore`
- source, tests, runtime behavior, reports, PDF/document corpus
- reviewer or controller artifacts
- delete, move, archive, clean, ignore, import, stage, promote, commit, push, PR or merge actions
- live EID/network/PDF/FDR/FundDocumentRepository/helper/fallback/provider/LLM/extractor/analyze/checklist/golden/readiness/score-loop/release commands

## 5. Current Accepted Artifact Summary

The active startup surface keeps only current-useful accepted facts. Full evidence-chain grouping is in `docs/reviews/mvp-control-doc-compression-accepted-artifact-index-20260611.md`.

| Gate family | Current relevance |
|---|---|
| Control-doc compression / artifact hygiene | Planning gate accepted locally at `7365e2b`; implementation accepted locally at `693638b`; controller judgment `ACCEPT_WITH_REVIEW_CHANNEL_RESIDUAL` |
| EID single-source operational hardening | Current annual-report source policy, helper repair evidence and public Source Provenance v2 truth alignment are accepted; fallback/source expansion remains deferred |
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
| Deepreview-derived long-run gates | Controller / future gate owners | Phaseflow queue in `docs/reviews/mvp-long-run-phaseflow-startup-20260611-115345.md` | Follow queue order; current active gate is runtime artifact disposition / ignore-rule planning |
| EID public provenance mismatch | Fund/source provenance owner | Closed by `2cee618`; residual design/README wording sync remains separate | Accepted for current implementation |
| Source provenance design/README wording drift (`mode` vs `source_mode`) | Design/controller owner | Separate design-truth-sync or documentation consistency gate | Does not block accepted EID implementation |
| LLM execution request validation ordering | Service/LLM execution owner | Closed by `336081e`; LLM path parity with deterministic `_validate_request()` remains separate | Accepted for current implementation |
| UI-Service-Host boundary reconciliation | Service/Host boundary owner | Closed by `8ff20ed`; residual future Host/Agent expansion remains separate | Accepted for current implementation |
| Runtime artifact disposition / ignore-rule planning | Controller / artifact owners | Plan accepted at `b4ab635`; implementation/disposition not started | Active mainline gate |
| Any discovered design/control inconsistency | Controller/design owner | Separate design-truth-sync gate | Must be recorded as residual; `docs/design.md` remains untouched in this gate |
| Live EID/provider/extractor/golden/readiness/release work | Corresponding gate owner | Separate reviewed gate with explicit authorization | Not authorized here |

## 7. Resume Checklist

1. Run only allowed status/metadata checks if resuming from this checkpoint.
2. Read `docs/implementation-control.md` for current control truth.
3. Use the accepted artifact and historical ledger indexes for evidence-chain reconstruction.
4. Do not use arbitrary untracked residue as proof.
5. Next mainline is runtime artifact disposition / ignore-rule implementation/disposition under accepted plan `b4ab635`. Do not clean, delete, move, archive, ignore, stage, promote, edit `.gitignore` or treat runtime artifacts as accepted release evidence without accepted implementation scope and required authorization.
