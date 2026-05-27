# QDII Replacement Fallback 040046 Evidence — Controller Judgment

> Date: 2026-05-27
> Controller: Codex
> Gate: `QDII replacement fallback 040046 evidence gate`
> Evidence artifact: `docs/reviews/release-maintenance-qdii-replacement-fallback-040046-evidence-20260527.md`
> Decision: **ACCEPTED LOCALLY**

## Startup Packet Replay

| Item | State |
|---|---|
| Current phase | `release maintenance` |
| Current gate before this judgment | `QDII replacement fallback 040046 evidence plan accepted locally` |
| Startup Packet next entry point | `QDII replacement fallback 040046 evidence gate; must use init-agents / tmux multi-agent flow` |
| Latest accepted checkpoint before this judgment | `f05101f docs: accept qdii fallback 040046 evidence plan` |

This gate followed the Startup Packet next entry point. No reconciliation artifact was required.

## Accepted Evidence Summary

The bounded evidence gate ran only `040046` / 2024 and did not run `096001`, `019172`, or later fallback candidates.

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
| `terminal_classification` | `quality_blocked_after_provenance` |
| `promotion_disposition` | `not_promoted` |
| P0 status | `pass`; no P0 failed fields |
| Blocking rule | `FQ4` missing-field-rate `35.7%` > threshold `35.0%` |
| P1 failed fields | `turnover_rate`, `holder_structure`, `holdings_snapshot`, `share_change` |
| `manager_strategy_text` | `pass`; 100% coverage / traceability |

`040046` is therefore source-provenance eligible but not replacement-ready, not baseline-ready, not golden-ready, not scoring-ready, and not promoted.

## Reviews

| Reviewer | Artifact | Verdict |
|---|---|---|
| AgentDS | `docs/reviews/release-maintenance-qdii-replacement-fallback-040046-evidence-review-ds-20260527.md` | `PASS` |
| AgentGLM | `docs/reviews/release-maintenance-qdii-replacement-fallback-040046-evidence-review-glm-20260527.md` | `PASS_WITH_FINDINGS` |

## Finding Judgment

| Finding | Controller judgment | Reason |
|---|---|---|
| DS F1: `errors.jsonl` is empty but evidence only lists it as generated | **accepted as low; no patch required** | Empty errors file is consistent with successful snapshot. It does not affect terminal classification or promotion state. |
| DS F2: summary shows 16 fields while score counts 14 due to applicability exclusions | **accepted as low residual** | The material quality outcome remains `block`; future evidence templates may surface applicability-excluded fields explicitly. |
| DS F3: raw `git diff --check` output omitted | **accepted as low; no patch required** | Evidence records the check passed and reviewers independently verified it. |
| GLM F1: terminal-state matrix lacks explicit FQ4 structural block row | **accepted as future plan-template residual** | `quality_blocked_after_provenance` is materially correct because provenance is eligible and quality status is `block`; future fallback plans should add an explicit FQ4 / non-P0 block row. |

No blocking or material finding remains. No evidence patch or re-review is required.

## Accepted Next Entry Point

`QDII replacement fallback candidate evidence plan gate for 019172`

Required next-gate constraints:

- Use `$init-agents` / tmux multi-agent flow.
- Start with Startup Packet replay and state this follows the accepted next entry point, not a gate switch.
- Produce a plan artifact before any `019172` evidence run.
- Select `019172` / 2024 as the next fallback candidate from the accepted enumeration fallback order unless a truth-source contradiction is found.
- Treat `019172` as `provenance_unknown`, `quality_unknown`, and `promotion_disposition=not_promoted` until evidence proves otherwise.
- Preserve accepted `096001` and `040046` states as source-provenance eligible but quality `block` and not promoted.
- Reuse the corrected evidence-plan shape, including generated-output provenance reading and an explicit FQ4 / non-P0 quality-block terminal row.
- Do not run any later fallback candidate in the plan gate.
- Preserve exclusions for `017641`, QDII-FOF, `013308`, and bond QDII candidates.
- Do not promote any candidate to durable baseline, golden answer corpus, accepted replacement, or scoring-ready state.

Do not change code, tests, renderer, FQ0-FQ6, Service/CLI defaults, `FundDocumentRepository` source strategy, source-helper fallback semantics, taxonomy, extractor, Host/Agent packages, Dayu runtime, golden files, baseline fixtures, durable corpus state, or GitHub state.

## Validation

- Evidence commands recorded in the accepted artifact completed as described.
- `git diff --check` passed after the evidence artifact update.
- Generated `reports/extraction-snapshots/qdii-replacement-fallback-040046-2024-20260527/` outputs stayed ignored/untracked.
- This accepted checkpoint changes docs/review/control artifacts only; no production code or tests changed.

## Residual Risks

| Residual | Owner / next gate | Required handling |
|---|---|---|
| `040046` FQ4 structural quality block | future QDII diagnosis or replacement decision gate | Do not promote; diagnose only in a separate authorized gate if needed. |
| `040046` P1 gaps: `turnover_rate`, `holder_structure`, `holdings_snapshot`, `share_change` | future QDII diagnosis or durable-baseline gate | Must be resolved or explicitly accepted before durable baseline consideration. |
| Terminal matrix lacks explicit FQ4 / non-P0 quality block row | next fallback evidence plan gate | Add explicit row to avoid ambiguity. |
| `019172` provenance/quality unknown | next fallback evidence plan gate | Plan before evidence; keep not promoted. |
| Eastmoney fallback source for `096001` and `040046` | future source/coverage decision gate | Source is eligible but quality reflects fallback-source extraction. |

