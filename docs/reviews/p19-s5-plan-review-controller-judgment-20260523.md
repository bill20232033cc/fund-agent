# P19-S5 Plan Review Controller Judgment - 2026-05-23

## Inputs

- Plan: `docs/reviews/p19-s5-all-a-pe-source-gate-plan-20260523.md`
- MiMo review: `docs/reviews/p19-s5-plan-review-mimo-20260523.md`
- GLM review: `docs/reviews/p19-s5-plan-review-glm-20260523.md`
- Design truth: `docs/design.md` v2.2 §11

## Judgment

Verdict: BLOCKED UNTIL PLAN PATCH

The source-feasibility-first shape is correct, but the current plan omits a critical installed akshare candidate: `stock_a_ttm_lyr()`. MiMo locally verified that it returns all-A PE history fields with thousands of rows and substantial common dates with `stock_a_all_pb()`. This directly changes the source gate from "PE history unresolved" to "PE candidate exists and needs source contract validation".

GLM's finding is also accepted: even when PE and PB histories exist, acceptance must require design-compatible equal-weight / median semantics. Exact all-A identity plus arbitrary market-weight PE/PB is not enough.

## Accepted Findings

### F1 - Missing `akshare.stock_a_ttm_lyr()`

Accepted as blocker.

Required plan patch:

- Add `akshare.stock_a_ttm_lyr()` to mandatory probes.
- Record local source module, URL/API, returned fields, rows, date range, missing rules, access/license hints, and common dates with `stock_a_all_pb()`.
- Treat `middlePETTM`, `middlePELYR`, `averagePETTM`, and `averagePELYR` as a source-contract decision, not an automatic implementation choice.
- Replace any absolute "all-A PE history unresolved" statement with "all-A PE candidate exists and requires contract validation" until feasibility completes.

### F2 - Acceptance needs design-compatible PE/PB semantics

Accepted.

Required plan patch:

- Add hard acceptance condition: PE and PB must match the current design's equal-weight / median-oriented thermometer semantics, or the gate outcome is `NEEDS_DESIGN_CHANGE`.
- Add probe fields for weighting method, statistic type, PE basis, and PB basis.
- If PE/PB exact all-A sources are mergeable but use materially different universes or weighting/statistic semantics, source gate must not return `ACCEPT_IMPLEMENTATION_PLAN`.

## Controller Decision

Do not run source feasibility from the current plan. Patch the plan first, then re-review the patched source gate plan.

## Next Gate

P19-S5 plan patch / re-review.
