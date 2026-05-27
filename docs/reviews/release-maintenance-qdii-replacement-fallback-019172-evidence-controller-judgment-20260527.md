# QDII Replacement Fallback 019172 Evidence — Controller Judgment

> Date: 2026-05-27
> Controller: Codex
> Gate: `QDII replacement fallback 019172 evidence gate`
> Evidence artifact: `docs/reviews/release-maintenance-qdii-replacement-fallback-019172-evidence-20260527.md`
> Decision: **ACCEPTED LOCALLY**

## Startup Packet Replay

| Item | State |
|---|---|
| Current phase | `release maintenance` |
| Current gate before this judgment | `QDII replacement fallback 019172 evidence plan accepted locally` |
| Startup Packet next entry point | `QDII replacement fallback 019172 evidence gate; must use init-agents / tmux multi-agent flow` |
| Latest accepted checkpoint before this judgment | `dafc72f docs: accept qdii fallback 019172 evidence plan` |

This evidence gate followed the Startup Packet next entry point. No reconciliation artifact was required.

## Accepted Evidence Summary

The bounded evidence gate ran only `019172` / 2024 and did not run `096001`, `040046`, `017641`, or later fallback candidates.

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
| `issue_count` | `9` |
| `terminal_classification` | `quality_blocked_after_provenance` |
| `promotion_disposition` | `not_promoted` |
| Primary blocker | P0 `manager_strategy_text` coverage / traceability `0.0% / 0.0%` |
| Additional blocker | FQ4 missing-field-rate `35.7%` > threshold `35.0%` |
| P1 failed fields | `turnover_rate`, `holdings_snapshot`, `share_change` |

`019172` is therefore source-provenance eligible but not replacement-ready, not baseline-ready, not golden-ready, not scoring-ready, and not promoted.

## Reviews

| Reviewer | Artifact | Verdict |
|---|---|---|
| AgentDS | `docs/reviews/release-maintenance-qdii-replacement-fallback-019172-evidence-review-ds-20260527.md` | `PASS_WITH_FINDINGS` |
| AgentGLM | `docs/reviews/release-maintenance-qdii-replacement-fallback-019172-evidence-review-glm-20260527.md` | `PASS` |

## Finding Judgment

| Finding | Controller judgment | Reason |
|---|---|---|
| DS L1 / GLM L1: generated `summary.md` exposes 16 snapshot fields while score uses 14 applicable fields | **accepted as low residual; no patch required** | Reviewers verified the quality decision uses the applicable score denominator. This repeats the accepted 040046 pattern and does not affect terminal classification. |
| DS L2: `false_positive_suspicion` cites `index_profile` behavior that likely reflects current QDII-before-index classification priority | **accepted as low calibration residual** | The suspicion is not used to bypass quality block or authorize policy/code changes. The P0 `manager_strategy_text` blocker and FQ4 block remain sufficient for `quality_blocked_after_provenance`. Future evidence artifacts should calibrate false-positive suspicion against known applicability rules. |

No blocking or material finding remains. No evidence patch or re-review is required.

## Accepted Next Entry Point

`QDII replacement post-019172 disposition decision gate`

Required next-gate constraints:

- Use `$init-agents` / tmux multi-agent flow.
- Start with Startup Packet replay and state this follows the accepted next entry point, not a gate switch.
- Produce a reviewed disposition/decision artifact before any later QDII candidate evidence run.
- Preserve `096001`, `040046`, and `019172` as source-provenance eligible but quality `block` and `not_promoted`.
- Decide whether to continue to the next equity-QDII fallback candidate from the accepted enumeration order, open a taxonomy/asset-class fitness gate, or stop QDII replacement and report coverage blockage.
- Do not run `021539`, `020712`, active QDII, QDII-FOF, `013308`, or bond QDII evidence until a new plan gate explicitly authorizes exactly one row.
- Do not promote any QDII candidate to durable baseline, clean denominator, fixture, report-quality corpus, golden answer corpus, accepted replacement, or scoring-ready state.

Do not change code, tests, renderer, FQ0-FQ6, Service/CLI defaults, `FundDocumentRepository` source strategy, source-helper fallback semantics, taxonomy, extractor, Host/Agent packages, Dayu runtime, golden files, baseline fixtures, durable corpus state, or GitHub state.

## Validation

- Evidence commands recorded in the accepted artifact completed as described.
- `git diff --check` passed in the evidence artifact and in both independent reviews.
- Generated `reports/extraction-snapshots/qdii-replacement-fallback-019172-2024-20260527/` outputs stayed ignored/untracked.
- This accepted checkpoint changes docs/review/control artifacts only; no production code or tests changed.

## Residual Risks

| Residual | Owner / next gate | Required handling |
|---|---|---|
| Three QDII replacement candidates quality-blocked after eligible provenance | `QDII replacement post-019172 disposition decision gate` | Decide whether more fallback evidence is justified or whether QDII coverage remains blocked. |
| `019172` P0 `manager_strategy_text` block | future QDII diagnosis or disposition gate | Do not promote; diagnose only in a separate reviewed gate if needed. |
| `019172` FQ4 structural block and P1 gaps | future QDII diagnosis or disposition gate | Do not promote; preserve blocker evidence. |
| False-positive suspicion calibration | future evidence-template ergonomics gate | Future artifacts should distinguish known applicability behavior from true false-positive suspicion. |
| QDII-FOF / `013308` / bond QDII exclusions | future taxonomy or asset-class fitness gate | Do not use these rows without explicit reviewed controller authorization. |
