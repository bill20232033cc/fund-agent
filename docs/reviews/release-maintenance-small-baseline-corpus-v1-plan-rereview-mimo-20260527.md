# Targeted Re-Review: Small Baseline Corpus v1 Plan

> Date: 2026-05-27
> Reviewer: AgentMiMo
> Review target: `docs/reviews/release-maintenance-small-baseline-corpus-v1-plan-20260527.md` (revised)
> Prior review: `docs/reviews/release-maintenance-small-baseline-corpus-v1-plan-review-mimo-20260527.md`
> Verdict: **PASS**

---

## Finding Resolution

### M1 (MATERIAL): Plan-only gate should mandate `git diff --check`

**Status: RESOLVED**

Evidence of resolution:

1. Verifier Matrix line 125: new row `| Diff whitespace closeout | git diff --check | Required before closeout even for plan-only gates. |`
2. Validation section line 166: "Closeout still requires `git diff --check`; the result must be reported by the worker before handing the plan back."

The finding is fully addressed. The `git diff --check` requirement is now explicit in both the verifier matrix and the validation section, and the responsibility is assigned to the implementation worker before handoff.

---

### M2 (MINOR): `selected_funds_smoke.py` dry-run scope clarification

**Status: RESOLVED**

Evidence of resolution:

Verifier Matrix line 109: "Dry-run by default; validates script argument parsing and command construction only. Unless a later implementation proves otherwise, it provides no annual-report availability confidence and has no network/cache expectation."

The finding is fully addressed. The dry-run is now explicitly scoped to argument parsing and command construction only, with an explicit statement that it provides no availability confidence and has no network/cache expectation.

---

## Scope Check

The revised plan introduces the following changes beyond M1/M2 resolution:

1. **Row count reconciliation** (line 18): Explicitly distinguishes "seven unique fund codes" from "eight candidate rows" because `004393` appears twice (2024 and 2025). This is a factual precision improvement.

2. **Golden coverage separation** (lines 35, 74): New selection rule 6 and decision summary step 4 separate `golden_covered` from `golden_missing` / `year_not_covered` observations. This correctly accounts for the fact that `004393`/2024 may have golden coverage while `004194`/2024 and `006597`/2024 should produce `year_not_covered` / `FQ0/info`.

3. **`--dev-override` semantics guard** (lines 64, 107-108): Added explicit warnings that `--dev-override` for `004393`/2025 must not be interpreted as consuming final-judgment semantics; record only exit, quality gate summary, availability, and report-year scope.

4. **Stop condition addition** (line 136): New stop condition — `004194`/2024 or `006597`/2024 golden-missing `FQ0/info` must not be misclassified as extraction failure.

5. **Next gate threshold refinement** (lines 145, 149): Golden corpus v1 gate now requires "at least five representative candidates across at least half the target fund-type slots" with separated golden-covered vs golden-missing rows. The fallback gate now covers "at or below three clean candidates" and "fewer than half the target fund-type slots."

All changes are within the plan-only scope. No source, tests, renderer, FQ0-FQ6, Service/CLI, Host/Agent/dayu, extractor, source fallback, fixtures, commit, push, or PR changes are introduced. The golden coverage refinements are analytical improvements to the plan's evaluation logic, not implementation scope creep.

---

## Summary

| Finding | Status | Notes |
|---------|--------|-------|
| M1 | RESOLVED | `git diff --check` in verifier matrix and validation section |
| M2 | RESOLVED | Dry-run scope explicitly limited to argument parsing |

---

## Verdict

**PASS**

Both prior findings are resolved. The plan revisions improve factual precision (row count reconciliation), analytical rigor (golden coverage separation), and boundary safety (`--dev-override` semantics guard, stop condition for golden-missing misclassification). All changes remain within the plan-only scope. No new findings.
