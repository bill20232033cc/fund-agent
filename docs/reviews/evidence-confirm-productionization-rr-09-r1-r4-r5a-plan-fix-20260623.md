# Evidence Confirm Productionization RR-09 R1-R4 / R5a Plan Fix

Verdict token:

`RR_09_R1_R4_R5A_PLAN_FIX_READY_FOR_REREVIEW_NOT_READY`

## Scope

Fix for plan review artifact:

`docs/reviews/plan-review-20260623-235818.md`

Target plan:

`docs/reviews/evidence-confirm-productionization-rr-09-r1-r4-r5a-residual-plan-20260623.md`

No code, tests, live/PDF/provider/LLM command, PR mutation, tag, release, or readiness claim was performed.

## Finding Addressed

`PR-001-未修复-高-R1-R4 单样本诊断门槛可能被误用为四样本关闭证据`

The original plan allowed "at least one representative sample" as a diagnostic goal without clearly preventing closure of all R1-R4 from one sample.

## Change Made

Section 4 now states:

- Evidence disposition is sample-specific.
- Single-sample diagnostic may prove the diagnostic method, classify that one sample, and decide the next diagnostic/fix step.
- Single-sample diagnostic must not close or reclassify unexamined R1-R4 samples.
- Closing or reclassifying all R1-R4 requires fact-level diagnostic coverage for all four RR-S2 failing samples, or an explicit table leaving unexamined samples open.
- Acceptance criteria are per sample unless the diagnostic covers all four samples.

## Residual Status

| Residual | Status after fix |
|---|---|
| R1-R4 | open; closure now requires per-sample diagnostic evidence |
| R5a | open; still routes to extraction/anchor hardening or product applicability decision |
| R5b | closed by Branch F; not reopened |
| Release/readiness | `NOT_READY` |

## Validation

Plan-only validation remains:

```bash
git diff --check -- docs/reviews/evidence-confirm-productionization-rr-09-r1-r4-r5a-residual-plan-20260623.md docs/reviews/evidence-confirm-productionization-rr-09-r1-r4-r5a-plan-fix-20260623.md docs/reviews/plan-review-20260623-235818.md
```

Completion token:

`RR_09_R1_R4_R5A_PLAN_FIX_READY_FOR_REREVIEW_NOT_READY`
