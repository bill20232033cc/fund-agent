# Control-doc Compression Accepted Artifact Index

日期：2026-06-11

状态：accepted evidence-chain index；accepted locally at `693638b`.

Scope: this index groups accepted artifacts that are relevant to the active `MVP typed-template-to-agent report generation stabilization phase`. It is not a design truth source and does not override `AGENTS.md`, `docs/design.md`, `docs/current-startup-packet.md`, or `docs/implementation-control.md`.

## Index Rules

- Group by gate family, not by full chronological ledger.
- Preserve accepted status, authoritative artifact paths/checkpoints, current relevance and residual owner/deferred gate.
- Historical artifacts listed here remain evidence chain only.
- Untracked residue is not accepted proof unless a controller judgment has accepted that exact artifact in a reviewed gate.

## Gate Family Index

| Gate family | Accepted status | Authoritative artifact paths / checkpoints | Current relevance | Residual owner / deferred gate |
|---|---|---|---|---|
| Control-doc compression / artifact hygiene | Planning gate accepted locally; implementation accepted locally at `693638b` | Plan `docs/reviews/mvp-control-doc-compression-artifact-hygiene-plan-20260611.md`; plan controller judgment `docs/reviews/mvp-control-doc-compression-artifact-hygiene-plan-controller-judgment-20260611.md`; planning checkpoint `7365e2b`; implementation evidence `docs/reviews/mvp-control-doc-compression-artifact-hygiene-implementation-evidence-20260611.md`; DS review `docs/reviews/mvp-control-doc-compression-artifact-hygiene-code-review-ds-20260611.md`; MiMo review `docs/reviews/mvp-control-doc-compression-artifact-hygiene-code-review-mimo-20260611.md`; implementation controller judgment `docs/reviews/mvp-control-doc-compression-artifact-hygiene-controller-judgment-20260611.md`; implementation checkpoint `693638b` | Current compressed control surface and evidence-chain indexes | Review-channel/worker-channel residuals accepted; next mainline is source-like residue ownership gate for `fund_agent/tools/` |
| EID single-source operational hardening | Accepted locally across failure-branch evidence, helper repair, controlled live retry and metadata docs-sync | Controlled live EID failure-branch plan `7ebd06d`; evidence `ebcd3bf`; helper repair plan `38d7f9e`; helper repair implementation `022b409`; helper retry evidence `f0a1459`; metadata docs-sync planning `daf5de7`; metadata docs-sync implementation `36a7979` | Current annual-report source policy remains EID single-source operational implementation; helper repair evidence is accepted | Fallback invocation/source expansion/additional acquisition remain deferred to separate reviewed gates |
| Small golden set / extractor correctness | Accepted locally through current-consumable row-shape and extractor surfaces | Planning `4ebaf0b`; implementation plan `d05c1c9`; Slice A `a94c705`; Slice B `ceb418b`; Slice C reconciliation `2371ad1`; source identity option `0cc0c14`; parser mechanics option `cb2cf77`; matched source identity prep `65532ab`; manual evidence `2706f91` and `7cc0479`; row/extractor family checkpoints through target-fund extractor implementation `7a10dbf`; downstream integration implementation `c3b9061` | Current extractor correctness evidence for accepted rows/contracts; supports current no-live extractor surfaces | Fixture projection, promotion, release/readiness and additional source acquisition deferred |
| Typed template truth-source replacement | Accepted locally | Typed template implementation planning `581ab4d`; Slices 0-8 `4619f12`, `f66043f`, `66d9580`, `848b756`, `52b055f`, `ae0b9fa`, `1ec22e0`, `23b8f5f`, `984d3be`; aggregate deepreview `d08eab9`; truth-source replacement plan `266e18f`; Slices 1-5 `3c2b237`, `0263bc2`, `202b396`, `e613876`, `42243b9`; aggregate review `115b075`; template truth validation plan `ecbd20f`; validation gate `c907258` | `docs/fund-analysis-template-draft.md` canonical `TEMPLATE_CONTRACT_MANIFEST_JSON` is current authored Fund template contract truth source | Deterministic defaults, provider defaults, public chapter ids `0-7`, golden/readiness and score-loop unchanged unless separately gated |
| Agent engine / Host governance | Accepted locally for current no-live body-chapter mechanics and process-local Host lifecycle boundary | Agent design refresh `b862381`; Slice A `8d50b40`; Slice B `1c3c031`; Slice C `bc45778`; Slice D `9f6d360`; Slice E plan `cf20620`; Slice E implementation `49df574`; aggregate deepreview `7224eb8`; Draft PR #22 closeout `2b1c804`; internalized Host governance accepted in prior control ledger | Current Agent owns contracts, ToolTrace, Fund adapters, repair policy, body runner and readiness for body chapters; Host owns process-local lifecycle/deadline/cancel/terminal state | Full Agent tool-loop, durable Host session/resume/memory/outbox and live/runtime integration remain future gates |
| Provider/runtime/LLM diagnostics and calibration | Accepted locally as fail-closed diagnostics, evidence classification and no-live calibration slices | Provider factory `26203d3`; CLI provider wiring `ab0590a`; incomplete retention `4f7903f`; LLM progress `d656816`; provider budget plan `0fd8b7c`; diagnostic repair `218a4f6`; endpoint/path family `a96a724`, `764ca00`, `dd0a074`; chapter acceptance no-live closeout `13a8c19`; provider residual evidence `3f72786`; future live provider calibration blocked evidence `79fd068`; post-config live smoke disposition artifacts in `docs/reviews/` | Supports current fail-closed `--use-llm` behavior and residual routing; does not prove accepted live report generation | Live acceptance, endpoint ownership changes, provider defaults/runtime budget changes, score-loop and readiness remain deferred |
| Downstream integration and row-shape follow-up | Accepted locally | Downstream integration planning `56b9e42`; implementation `c3b9061`; row-shape decision artifacts in `docs/reviews/`; same-source failing-test/fix checkpoints for manager, risk text, bond top holding and target-fund holding | Current extractor surfaces and integration plan are accepted inputs to control truth | Further row families or fixture projection require separate gates |
| Release-maintenance and retrospective evidence | Historical accepted evidence | Release-maintenance artifacts under `docs/reviews/release-maintenance-*`; retrospective review checkpoints `f590cae`, `525f9e4`, `671e967`, `3af9e63`; archive `docs/archive/implementation-control-release-maintenance-ledger-20260527.md` | Evidence-chain only; useful for provenance and prior release-maintenance context | Does not set current release/readiness/PR state |

## Current-useful Checkpoint Summary

| Checkpoint / artifact | Role |
|---|---|
| `7365e2b` | Accepted planning checkpoint for current control-doc compression / artifact hygiene implementation gate |
| `693638b` | Accepted implementation checkpoint for control-doc compression / artifact hygiene gate |
| `c907258` | Accepted template truth validation checkpoint |
| `115b075` | Accepted typed template truth-source replacement aggregate checkpoint |
| `7224eb8` | Accepted Agent Engine Slice E aggregate deepreview checkpoint |
| `2b1c804` | Accepted Draft PR #22 review/fix/re-review closeout checkpoint |
| `7a10dbf` | Accepted target fund holding extractor fix implementation checkpoint |
| `c3b9061` | Accepted downstream integration implementation checkpoint |
| `36a7979` | Accepted EID metadata design wording docs-sync implementation checkpoint |

## Non-overrides

This artifact does not authorize source/test/runtime changes, live commands, fallback, source expansion, provider/LLM changes, extractor/analyze/checklist/golden/readiness/score-loop/release actions, PR state changes, cleanup or promotion of untracked residue.
