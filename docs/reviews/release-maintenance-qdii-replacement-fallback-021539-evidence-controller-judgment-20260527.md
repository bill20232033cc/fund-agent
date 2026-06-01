# QDII Replacement Fallback 021539 Evidence — Controller Judgment

> Date: 2026-05-27
> Controller: Codex
> Gate: `QDII replacement fallback 021539 evidence gate`
> Evidence artifact: `docs/reviews/release-maintenance-qdii-replacement-fallback-021539-evidence-20260527.md`
> Decision: **ACCEPTED LOCALLY**

## Startup Packet Replay

| Item | State |
|---|---|
| Current phase | `release maintenance` |
| Current gate before this judgment | `QDII replacement fallback 021539 evidence plan accepted locally` |
| Startup Packet next entry point | `QDII replacement fallback 021539 evidence gate; must use init-agents / tmux multi-agent flow` |
| Latest accepted checkpoint before this judgment | `b575a49 docs: accept qdii fallback 021539 evidence plan` |

This evidence gate followed the Startup Packet next entry point. No reconciliation artifact was required.

## Accepted Evidence Summary

The bounded evidence gate ran only `021539` / 2024 and did not run `020712`, active QDII, QDII-FOF, `013308`, bond QDII, `017641`, `096001`, `040046`, `019172`, or later fallback candidates.

Public provenance is eligible:

| Field | Accepted value |
|---|---|
| `resolved_source_name` | `eastmoney` |
| `fallback_used` | `true` |
| `primary_failure_category` | `unavailable` |
| `fallback_eligibility` | `eligible` |
| `source_provenance_status` | `complete` |
| `source_strategy` | `primary_then_fallback` |

Quality terminal state is:

| Field | Accepted value |
|---|---|
| `quality_gate_status` | `block` |
| `issue_count` | `7` |
| `terminal_classification` | `quality_blocked_after_provenance` |
| `promotion_disposition` | `not_promoted` |
| P0 status | `pass`; `manager_strategy_text` passed with 100% coverage / traceability |
| Blocking rule | FQ4 missing-field-rate `35.7%` > threshold `35.0%` |
| P1 failed fields | `turnover_rate`, `holder_structure`, `holdings_snapshot`, `share_change` |

`021539` is therefore source-provenance eligible but not replacement-ready, not baseline-ready, not golden-ready, not scoring-ready, and not promoted.

Because `021539` quality-blocked after eligible provenance, the accepted hard stop is now triggered: automatic QDII probing must stop. A new disposition gate is required before any further QDII probing, diagnosis, taxonomy / asset-class fitness decision, or coverage-blockage decision.

## Reviews

| Reviewer | Artifact | Verdict |
|---|---|---|
| AgentDS | `docs/reviews/release-maintenance-qdii-replacement-fallback-021539-evidence-review-ds-20260527.md` | `PASS` |
| AgentMiMo | `docs/reviews/release-maintenance-qdii-replacement-fallback-021539-evidence-review-mimo-20260527.md` | `PASS` |

AgentGLM was initially assigned as the second reviewer but was interrupted before producing a review artifact. The controller reassigned the second independent review to AgentMiMo using tmux handoff. AgentMiMo completed the review and wrote the accepted review artifact.

## Finding Judgment

| Finding | Controller judgment | Reason |
|---|---|---|
| DS findings | **none** | DS verified all 10 review criteria against generated public outputs. |
| MiMo findings | **none** | MiMo verified all 11 review criteria and recorded the four-candidate QDII quality-block pattern as a minor observation, not a finding. |
| Stray untracked `--help` file | **deferred to artifact disposition / user-authorized cleanup** | A 0-byte untracked `--help` file was produced by a controller handoff quoting mistake, not by the evidence worker and not as an accepted artifact. It is not staged or promoted. Deletion requires explicit cleanup authorization or a later artifact-disposition gate. |

No blocking or material finding remains. No evidence patch or re-review is required.

## Accepted Next Entry Point

`QDII replacement post-021539 disposition decision gate`

Required next-gate constraints:

- Use `$init-agents` / tmux multi-agent flow.
- Start with Startup Packet replay and state this follows the accepted next entry point, not a gate switch.
- Produce a reviewed disposition/decision artifact before any further QDII candidate evidence run.
- Summarize accepted QDII attempts: `096001`, `040046`, `019172`, and `021539`.
- Preserve all four as source-provenance eligible but quality `block`, terminal `quality_blocked_after_provenance`, and `promotion_disposition=not_promoted`.
- Treat automatic QDII probing as stopped by the accepted hard stop.
- Decide between QDII extraction/applicability diagnosis, taxonomy / asset-class fitness, or recording QDII coverage blocked and routing to another v1 blocker.
- Do not run `020712`, active QDII, QDII-FOF, `013308`, bond QDII, or any later candidate evidence in the disposition decision gate.
- Do not promote any QDII candidate to durable baseline, clean denominator, fixture, report-quality corpus, golden answer corpus, accepted replacement, source-safe state, or scoring-ready state.

Do not change code, tests, renderer, FQ0-FQ6, Service/CLI defaults, `FundDocumentRepository` source strategy, source-helper fallback semantics, taxonomy, extractor, Host/Agent packages, Dayu runtime, golden files, baseline fixtures, durable corpus state, or GitHub state.

## Validation

- Evidence commands recorded in the accepted artifact completed as described.
- `git diff --check` passed in the evidence artifact and in both accepted reviews.
- Generated `reports/extraction-snapshots/qdii-replacement-fallback-021539-2024-20260527/` outputs stayed ignored/untracked.
- This accepted checkpoint changes docs/review/control artifacts only; no production code or tests changed.

## Residual Risks

| Residual | Owner / next gate | Required handling |
|---|---|---|
| Four QDII replacement candidates quality-blocked after eligible provenance | `QDII replacement post-021539 disposition decision gate` | Stop automatic probing and decide diagnosis, taxonomy/asset-class fitness, or coverage-blocked disposition. |
| Repeated QDII P1 gaps | future QDII diagnosis or disposition gate | `turnover_rate`, `holder_structure`, `holdings_snapshot`, and `share_change` recur across candidates and should be treated as structural pattern evidence. |
| QDII index / feeder applicability suspicion | future QDII diagnosis gate | Investigate only in a separate reviewed gate if needed; do not change taxonomy or quality rules here. |
| Stray untracked `--help` file | artifact disposition / user-authorized cleanup | Do not stage or promote; clean only with explicit authorization or accepted disposition. |
| Golden/baseline remains blocked by QDII coverage | future baseline/golden gate | Do not enter golden answer corpus v1 until QDII disposition and other coverage blockers are resolved or explicitly excluded. |
