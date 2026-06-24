# Plan Review Re-review: RR-09 A4 Row-material Precision Plan

Reviewed target:

`docs/reviews/evidence-confirm-productionization-rr-09-a4-row-material-precision-plan-20260624.md`

Fix artifact:

`docs/reviews/evidence-confirm-productionization-rr-09-a4-plan-fix-20260624.md`

Prior review:

`docs/reviews/plan-review-20260624-110223.md`

Scope:

Targeted re-review of PR-001 only.

## Finding Status

### PR-001-已修复-高-Bad Processor locator validation can still degrade into proof-bearing table references

- **Prior issue**: The original plan allowed recognized bad Processor locators to fall through to existing table downgrade behavior, which could create proof-bearing table references for malformed or contradictory locator data.
- **Fix evidence**:
  - The plan now distinguishes exact native `row-N`, recognized Processor protocol and arbitrary semantic locators.
  - Recognized Processor-protocol failures now explicitly return no reference with a blocking issue.
  - Arbitrary non-Processor semantic locators keep the existing A3 downgrade behavior.
  - The expected tests now require `status="fail"`, `references == ()` and blocking severity for mismatched `table_id`, missing `table_id`, missing `row`, invalid row, negative row and out-of-range row.
- **Residual risk**: Implementation must preserve this exact split. This is now testable and code-generation-ready.

Status: `已修复`

## Open Questions

None.

## Residual Risks

| Residual | Destination |
|---|---|
| A4 no-live implementation could still implement the protocol incorrectly. | Code review after implementation. |
| R3 `missing_section=3` is not solved by A4-S1. | Follow-up missing-section diagnostic/fix gate if live/PDF re-evidence still reports it. |
| B1 product CLI remains separate. | B1 runtime residual gate. |

## Conclusion

`pass-with-risks`

The targeted finding is fixed. Remaining risks are implementation/re-evidence risks and do not block controller acceptance of the A4 no-live implementation plan.
