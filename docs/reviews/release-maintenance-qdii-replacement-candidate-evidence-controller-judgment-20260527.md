# QDII Replacement Candidate Evidence — Controller Judgment

> Date: 2026-05-27
> Controller: Codex
> Gate: `QDII replacement candidate evidence gate`
> Evidence artifact: `docs/reviews/release-maintenance-qdii-replacement-candidate-evidence-20260527.md`
> Decision: **ACCEPTED LOCALLY**

## Startup Packet Replay

| Item | State |
|---|---|
| Current phase | `release maintenance` |
| Current gate before this judgment | `QDII replacement candidate evidence plan accepted locally` |
| Startup Packet next entry point | `QDII replacement candidate evidence gate; must use init-agents / tmux multi-agent flow` |
| Latest accepted checkpoint before this judgment | `fe2ea65 docs: accept qdii replacement evidence plan` |

This gate followed the Startup Packet next entry point. No reconciliation artifact was required.

## Accepted Evidence Summary

The bounded evidence gate ran only `096001` / 2024 and did not run fallback candidates.

Public provenance is eligible:

| Field | Accepted value |
|---|---|
| `resolved_source_name` | `eastmoney` |
| `fallback_used` | `true` |
| `primary_failure_category` | `unavailable` |
| `fallback_eligibility` | `eligible` |
| `source_provenance_status` | `complete` |
| `source_strategy` | `primary_then_fallback` |

The evidence then ran `extraction-score` and `quality-gate` through public CLI paths. Quality terminal state is:

| Field | Accepted value |
|---|---|
| `quality_gate_status` | `block` |
| `terminal_classification` | `quality_blocked_after_provenance` |
| `promotion_disposition` | `not_promoted` |
| Primary P0 blocker | `nav_benchmark_performance` |
| FQ4 missing-field-rate | `42.9%` |
| `manager_strategy_text` | `pass`; not the blocker |

`096001` is therefore source-provenance eligible but not replacement-ready, not baseline-ready, not golden-ready, not scoring-ready, and not promoted.

## Reviews

| Stage | Reviewer | Artifact | Verdict |
|---|---|---|---|
| Initial evidence review | AgentDS | `docs/reviews/release-maintenance-qdii-replacement-candidate-evidence-review-ds-20260527.md` | `BLOCKED` |
| Initial evidence review | AgentGLM | `docs/reviews/release-maintenance-qdii-replacement-candidate-evidence-review-glm-20260527.md` | `BLOCKED` |
| Re-review after fix | AgentDS | `docs/reviews/release-maintenance-qdii-replacement-candidate-evidence-rereview-ds-20260527.md` | `PASS` |
| Re-review after fix | AgentGLM | `docs/reviews/release-maintenance-qdii-replacement-candidate-evidence-rereview-glm-20260527.md` | `PASS` |

## Finding Judgment

| Finding | Controller judgment | Reason |
|---|---|---|
| DS/GLM initial blocking finding: worker stopped after snapshot by reading only CLI stdout, while public generated files contained complete provenance | **accepted and fixed** | The corrected evidence artifact reads public `summary.md` / `snapshot.jsonl`, records eligible provenance, and continues through score and quality gate. |
| DS high finding: non-matrix terminal classification `provenance_incomplete_not_run_quality` | **accepted and fixed** | Corrected terminal classification is `quality_blocked_after_provenance`, which exists in the accepted plan matrix. |
| GLM minor finding: `fallback_eligibility` was recorded as `not_eligible` | **accepted and fixed** | Corrected public provenance records `fallback_eligibility=eligible`. |
| DS/GLM residual: Eastmoney fallback path | **accepted as residual** | Provenance is eligible under accepted source semantics, but quality evidence reflects fallback-source extraction. |
| DS/GLM residual: `nav_benchmark_performance` P0 block and FQ4 missing-field-rate block | **accepted as blocker for promotion** | This prevents replacement/baseline/golden promotion and drives the next fallback plan gate. |

No blocking finding remains after re-review. No further re-review is required for this gate.

## Accepted Next Entry Point

`QDII replacement fallback candidate evidence plan gate for 040046`

Required next-gate constraints:

- Use `$init-agents` / tmux multi-agent flow.
- Start with Startup Packet replay and state this follows the accepted next entry point, not a gate switch.
- Produce a plan artifact before any fallback evidence run.
- Select `040046` / 2024 as the next fallback candidate from the accepted enumeration fallback order unless a truth-source contradiction is found.
- Treat `040046` as `provenance_unknown`, `quality_unknown`, and `promotion_disposition=not_promoted` until evidence proves otherwise.
- Reuse the accepted evidence-plan shape: public CLI preflight, public snapshot/score/quality-gate commands, generated-output provenance reading, provenance-before-quality ordering, fail-closed stop categories, explicit terminal classification, and `promotion_disposition=not_promoted`.
- Do not run `019172` or any later fallback candidate in the next plan gate.
- Preserve exclusions for `017641`, QDII-FOF, `013308`, and bond QDII candidates.
- Do not promote any candidate to durable baseline, golden answer corpus, accepted replacement, or scoring-ready state.

Do not change code, tests, renderer, FQ0-FQ6, Service/CLI defaults, `FundDocumentRepository` source strategy, source-helper fallback semantics, taxonomy, extractor, Host/Agent packages, Dayu runtime, golden files, baseline fixtures, durable corpus state, or GitHub state.

## Validation

- Evidence commands recorded in the accepted artifact completed as described.
- `git diff --check` passed after the evidence artifact update.
- Generated `reports/extraction-snapshots/qdii-replacement-candidate-096001-2024-20260527/` outputs stayed ignored/untracked.
- This accepted checkpoint changes docs/review/control artifacts only; no production code or tests changed.

## Residual Risks

| Residual | Owner / next gate | Required handling |
|---|---|---|
| `096001` P0 `nav_benchmark_performance` block | future QDII diagnosis or replacement decision gate | Do not promote `096001`; diagnose disclosure-vs-extractor only in a separate authorized gate if needed. |
| `096001` FQ4 missing-field-rate block | future QDII diagnosis or replacement decision gate | Do not treat source-eligible as report-quality-ready. |
| `096001` P1 gaps: `turnover_rate`, `holder_structure`, `holdings_snapshot`, `share_change` | future QDII diagnosis or durable-baseline gate | Must be resolved or explicitly accepted before durable baseline consideration. |
| Eastmoney fallback source | next fallback/evidence gates | Record that source is eligible fallback, but quality reflects fallback-source extraction. |
| `040046` provenance/quality unknown | next fallback evidence plan gate | Plan before any evidence run; keep not promoted. |

