# RR-09 A2 Plan Fix

Verdict: `RR_09_A2_PLAN_FIX_READY_FOR_REREVIEW_NOT_READY`

## Scope

Fix for plan review finding PR-001 from:

- Review artifact: `docs/reviews/plan-review-20260624-055333.md`
- Plan artifact: `docs/reviews/evidence-confirm-productionization-rr-09-a2-value-match-diagnostic-plan-20260624.md`

No source code, tests, live/PDF command, provider/LLM command, quality-gate semantic change, checklist support, report-body rendering, tag, release, or readiness claim was performed.

## Accepted Finding

| Finding | Status | Summary |
|---|---|---|
| PR-001 | accepted | A2 diagnostic helper must be same-source with deterministic V2 token/matcher primitives; a parallel approximate matcher would make diagnostic evidence unreliable. |

## Fix

Updated the A2 plan to add a mandatory V2 same-source constraint:

- Diagnostic token and match metadata must be derived from the same primitives used by deterministic V2 `value_match`.
- The helper must not implement a parallel approximate matcher.
- Acceptable implementation is either package-private diagnostic functions in `evidence_confirm.py`, or extraction of exact package-private primitives into an internal helper module consumed by both V2 and diagnostics.
- If a separate `evidence_confirm_value_diagnostics.py` module is used, it must call those primitives rather than duplicating flatten / normalize / numeric matching logic.

Updated Slice A2-S1 validation requirements:

- Tests must prove diagnostic match/miss metadata is consistent with `confirm_projection_evidence_v2()`.
- Tests must cover text substring match, numeric decimal equivalence, percent-unit mismatch, ignored keys, dataclass flatten, dict key order, nested list values and empty values under current V2 behavior.
- A2-S2 evidence must state that token/match metadata is derived from V2 same-source primitives, not a parallel matcher.

## Residuals

| Residual | Destination |
|---|---|
| A2-S1 implementation still needs code review after implementation. | Future A2-S1 implementation gate. |
| A2-S2 live/PDF diagnostic still requires separate explicit authorization. | Future A2-S2 authorization/evidence gate. |
| Release/readiness remains unproven. | Release boundary / later readiness gate. |

## Completion Token

`RR_09_A2_PLAN_FIX_READY_FOR_REREVIEW_NOT_READY`
