# Evidence Confirm Productionization RR-09 A3 Plan Fix

Verdict token:

`RR_09_A3_PLAN_FIX_READY_FOR_REREVIEW_NOT_READY`

## Scope

Target plan:

`docs/reviews/evidence-confirm-productionization-rr-09-a3-coarse-reference-bond-risk-fix-plan-20260624.md`

Prior review:

`docs/reviews/plan-review-20260624-095336.md`

Finding fixed:

`PR-001-未修复-高-S2 narrowing lacks a precise token-source and ambiguity contract`

This fix updates only the plan artifact. It does not implement code, run live/PDF commands, run product CLI commands, change V2/ECQ/quality-gate semantics, or claim release/readiness.

## Fix Summary

The plan now makes A3-S2 implementation-ready by binding the row narrowing contract to the same deterministic primitives already used by V2 and the accepted A2 diagnostic helper:

- Reuse `_material_tokens`, `_normalize_text` and `_token_matches_excerpt` from `fund_agent.fund.evidence_confirm`.
- Build `anchor_id -> facts` privately inside `build_annual_report_evidence_confirm_references()` from the already-passed `ChapterFactProjection`.
- Permit row-level narrowing only when exactly one available non-derived fact references the anchor and all V2 material tokens for that fact match exactly one table row.
- Preserve A1-C table/section downgrade when there are zero or multiple facts, no material token, multiple matching rows, no matching row, partial-token matches, malformed tables, or unsupported section-only narrowing.
- Add planned no-live tests for shared-anchor ambiguity and partial-token match.

## Verification

Static verification after edit:

```bash
git diff --check
```

Result:

- Passed.

Targeted re-review:

`docs/reviews/plan-review-rereview-20260624-095424.md`

Result:

- `pass-with-risks`
- PR-001 status: `已修复`

## Residuals

| Residual | Status |
|---|---|
| A3 no-live implementation | Not authorized by this artifact; requires controller acceptance of plan. |
| R1-R4 live/PDF re-evidence | Requires separate exact authorization after implementation/review. |
| B1 `017641 / 2024` runtime product CLI re-evidence | Still separate authorization. |
| Release/readiness | `NOT_READY`. |

Completion token:

`RR_09_A3_PLAN_FIX_READY_FOR_REREVIEW_NOT_READY`
