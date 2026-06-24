# Evidence Confirm Productionization RR-09 A4 Plan Fix

Verdict token:

`RR_09_A4_PLAN_FIX_READY_FOR_REREVIEW_NOT_READY`

## Scope

Target plan:

`docs/reviews/evidence-confirm-productionization-rr-09-a4-row-material-precision-plan-20260624.md`

Prior review:

`docs/reviews/plan-review-20260624-110223.md`

Finding fixed:

`PR-001-未修复-高-Bad Processor locator validation can still degrade into proof-bearing table references`

This fix updates only the plan artifact. It does not implement code, run live/PDF commands, run product CLI commands, change V2/ECQ/quality-gate semantics, push, mutate PR state, tag, release or claim readiness.

## Fix Summary

The plan now separates unsupported arbitrary semantic locators from recognized Processor-protocol locators:

- Exact native `row-N` keeps the current path.
- Arbitrary non-Processor semantic locators keep A3 token-based narrowing and informational table/section downgrade behavior.
- Recognized Processor-protocol locators are identified by semicolon-delimited keys from `field`, `table_id`, `row`, `column` or `cell_id`.
- Recognized Processor-protocol failures now produce no proof reference and a blocking issue instead of degrading to table excerpt.

The plan now requires blocking/no-reference behavior for:

- mismatched embedded `table_id`;
- missing embedded `table_id`;
- missing `row`;
- non-integer row;
- negative row;
- out-of-range row.

The test plan now requires these failure cases to assert:

- `status="fail"`;
- `references == ()`;
- blocking issue severity;
- no table excerpt fallback.

## Verification

Static verification after edit:

```bash
git diff --check
```

Result:

- Pending in this turn's final validation.

## Residuals

| Residual | Status |
|---|---|
| A4 plan targeted re-review | Required next. |
| A4 no-live implementation | Not authorized by this artifact; requires controller acceptance after plan re-review. |
| R1-R4 live/PDF re-evidence | Separate exact authorization after implementation/review. |
| B1 `017641 / 2024` runtime product CLI re-evidence | Separate exact authorization. |
| Release/readiness | `NOT_READY`. |

Completion token:

`RR_09_A4_PLAN_FIX_READY_FOR_REREVIEW_NOT_READY`
