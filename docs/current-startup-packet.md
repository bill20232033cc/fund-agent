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
| Current active gate | `Control-doc compression / artifact hygiene implementation gate` |
| Gate classification | `standard` |
| Current accepted checkpoint | Planning gate accepted locally at `7365e2b` with controller verdict `ACCEPT_WITH_AMENDMENTS` |
| Implementation status | This implementation gate is docs-only/no-live and pending review/controller acceptance after the implementation evidence artifact is written |
| Next entry point | Review `docs/reviews/mvp-control-doc-compression-artifact-hygiene-implementation-evidence-20260611.md`, then controller judgment for whether the implementation is accepted. No reviewer/controller artifact may be created or edited by implementation worker |
| Control truth | `docs/implementation-control.md` |
| Design truth | `docs/design.md` |
| Template truth | `docs/fund-analysis-template-draft.md` canonical `TEMPLATE_CONTRACT_MANIFEST_JSON` |
| Accepted artifact index | `docs/reviews/mvp-control-doc-compression-accepted-artifact-index-20260611.md` |
| Historical ledger index | `docs/reviews/mvp-control-doc-compression-historical-ledger-index-20260611.md` |
| Residue disposition index | `docs/reviews/mvp-control-doc-compression-untracked-residue-disposition-20260611.md` |

## 3. Current Control Truth

- Current production default remains deterministic `fund-analysis analyze/checklist`: structured extraction, deterministic analysis, template rendering, programmatic audit and FQ0-FQ6 quality gate.
- Current `--use-llm` path remains explicit opt-in and fail-closed: `CLI -> Service prepares FundLLMExecutionRequest / ExecutionContract -> Host runner -> Service -> Agent body runner -> fund_agent/fund -> provider HTTP call`.
- Current Agent implementation owns no-live body-chapter execution mechanics: contracts, ToolTrace, Fund tool adapters, repair policy, body runner and final assembly readiness.
- Host remains lifecycle-only and business-opaque. Service owns use-case orchestration, ExecutionContract semantics, provider construction/runtime ceilings and final product fail-closed mapping. Fund owns domain rules, CHAPTER_CONTRACT / preferred_lens / ITEM_RULE semantics, extraction and audit.
- EID single-source annual-report access is current operational source policy. Eastmoney, fund-company/CDN, CNINFO, fallback invocation, fixture projection, golden/readiness promotion, additional source acquisition, score-loop, release/merge/mark-ready and PR external state are not authorized by this gate.

## 4. Current Gate Scope

Allowed writes for this implementation gate:

- `docs/implementation-control.md`
- `docs/current-startup-packet.md`
- `docs/reviews/mvp-control-doc-compression-accepted-artifact-index-20260611.md`
- `docs/reviews/mvp-control-doc-compression-historical-ledger-index-20260611.md`
- `docs/reviews/mvp-control-doc-compression-untracked-residue-disposition-20260611.md`
- `docs/reviews/mvp-control-doc-compression-artifact-hygiene-implementation-evidence-20260611.md`

Explicitly out of scope:

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
| Control-doc compression / artifact hygiene | Planning gate accepted locally at `7365e2b`; current implementation gate is docs-only/no-live and pending review/controller acceptance |
| EID single-source operational hardening | Current annual-report source policy and helper repair evidence are accepted; fallback/source expansion remains deferred |
| Small golden / extractor correctness | Current-consumable row-field extractor surfaces are accepted; fixture projection and promotion remain deferred |
| Typed template truth-source replacement | `docs/fund-analysis-template-draft.md` canonical JSON is accepted authored template contract truth source |
| Agent engine / Host governance | Current no-live Agent body runner and process-local Host lifecycle boundary are accepted; full tool-loop/runtime expansion remains future |
| Provider/runtime/LLM diagnostics | Fail-closed provider path and diagnostics are accepted; live acceptance and runtime default changes remain unproven or deferred |
| Release/readiness historical evidence | Evidence chain only; does not set current release/PR/readiness state |

## 6. Open Residuals

| Residual | Owner | Next gate | Current blocker? |
|---|---|---|---|
| Implementation gate review/controller acceptance | Reviewer/controller | Control-doc compression implementation review and judgment | Blocks acceptance of this implementation gate |
| Untracked workspace residue | Controller / artifact owners | Artifact-specific disposition gates listed in residue disposition index | Does not block this docs-only implementation; blocks release/readiness until accepted disposition |
| `fund_agent/tools/` source-like residue | Controller + implementation owner | Source-like residue ownership gate | Blocks release/readiness; not imported/staged/promoted here |
| Manual smoke reports and PDFs outside accepted evidence chain | User/controller/runtime evidence owner | Runtime/data artifact disposition gates | Blocks release/readiness if unclassified |
| Any discovered design/control inconsistency | Controller/design owner | Separate design-truth-sync gate | Must be recorded as residual; `docs/design.md` remains untouched in this gate |
| Live EID/provider/extractor/golden/readiness/release work | Corresponding gate owner | Separate reviewed gate with explicit authorization | Not authorized here |

## 7. Resume Checklist

1. Run only allowed status/metadata checks if resuming this gate.
2. Read `docs/implementation-control.md` for current control truth.
3. Use the accepted artifact and historical ledger indexes for evidence-chain reconstruction.
4. Do not use arbitrary untracked residue as proof.
5. Do not modify or create reviewer/controller artifacts from the implementation-worker role.
