# P19-S5 Plan Review Controller Acceptance — 2026-05-23

## Scope

- Phase: P19 thermometer independent development
- Gate: P19-S5 all-A PE source gate
- Design truth: `docs/design.md` v2.2
- Control truth: `docs/implementation-control.md`

## Inputs

- Plan: `docs/reviews/p19-s5-all-a-pe-source-gate-plan-20260523.md`
- Plan patch: `docs/reviews/p19-s5-all-a-pe-source-gate-plan-patch-20260523.md`
- MiMo plan review: `docs/reviews/p19-s5-plan-review-mimo-20260523.md`
- GLM plan review: `docs/reviews/p19-s5-plan-review-glm-20260523.md`
- Controller judgment: `docs/reviews/p19-s5-plan-review-controller-judgment-20260523.md`
- MiMo plan re-review: `docs/reviews/p19-s5-plan-rereview-mimo-20260523.md`
- GLM plan re-review: `docs/reviews/p19-s5-plan-rereview-glm-20260523.md`

## Controller Decision

Verdict: ACCEPTED PLAN

The original source-feasibility-first shape was correct, but controller judgment blocked the plan until it included `akshare.stock_a_ttm_lyr()` and design-compatible PE/PB semantics as hard acceptance criteria. The patched plan now makes `stock_a_ttm_lyr()` a mandatory PE candidate probe, requires source workers to re-run and freeze source-contract evidence, and makes equal-weight / median-oriented semantics, PE basis, PB basis, universe identity, common dates, and access constraints part of the source gate.

Based on `docs/design.md` §11 and first principles, this is the best current practice: do not implement an all-A thermometer until source identity and PE/PB semantics prove the design contract, but also do not ignore a plausible installed akshare PE candidate that reviewers already surfaced.

## Accepted Findings

### F1 — Missing `akshare.stock_a_ttm_lyr()`

- Status: fixed by plan patch.
- Reasoning: The source gate must validate every plausible design-allowed all-A PE candidate before declaring P19-S5 blocked.

### F2 — Acceptance needs design-compatible PE/PB semantics

- Status: fixed by plan patch.
- Reasoning: Existence of all-A PE/PB fields is insufficient if weighting method, statistic type, PE basis, PB basis, or universe identity conflicts with the v2.2 thermometer design.

## Next Gate

Proceed to P19-S5 source feasibility execution.

The source worker must:

- Re-run all mandatory probes in the patched plan.
- Produce a durable source feasibility artifact with the full probe matrix.
- Stop with one of `ACCEPT_IMPLEMENTATION_PLAN`, `BLOCKED_DEFERRED`, or `NEEDS_DESIGN_CHANGE`.
- Not modify production code, tests, docs truth files, or CLI behavior.

## Residual Risks

- `stock_a_ttm_lyr()` reviewer probe evidence is promising but not accepted as source truth until the source worker independently validates identity, fields, history, common dates, missing rules, access, and PE/PB semantics.
- If exact all-A PE/PB exists but semantics do not match the current design, the next gate is design change, not implementation.
