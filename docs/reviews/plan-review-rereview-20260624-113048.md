# Plan Re-review - RR-09 A5 Projection Locator Adoption Plan

Reviewed target: `docs/reviews/evidence-confirm-productionization-rr-09-a5-projection-locator-adoption-plan-20260624.md`

Prior review: `docs/reviews/plan-review-20260624-112914.md`

Fix artifact: `docs/reviews/evidence-confirm-productionization-rr-09-a5-plan-fix-20260624.md`

Scope: Re-review accepted finding PR-001 and check whether the A5 plan is now implementation-ready for no-live work.

Conclusion: `pass-with-risks`

## Accepted Finding Status

| Finding | Status | Evidence |
| --- | --- | --- |
| PR-001: 无 `field=` locator 时空 anchors 的规则会破坏非 FDD processor family projection | 已修复 | Plan now limits filtering to field-locator-capable families and requires preserving `family_result.anchors` when no recognized semicolon `field=` locator exists. |

## Assumptions Re-tested

- `_field_from_family()` remains shared, so the plan must protect non-FDD/no-`field=` family outputs.
- Field-specific filtering is now gated by recognized semicolon `field=` locators.
- A no-`field=` processor family fixture is now a required regression.
- R3 `missing_section=3` remains outside row locator adoption and is not downgraded.

## Re-review Notes

The fixed plan removes the blocking overreach. It now states:

- field-specific filtering applies only when the family anchor set contains recognized semicolon `field=` Processor locators;
- if no recognized `field=` locator exists, the existing `family_result.anchors` behavior is preserved;
- field-locator-capable families still fail closed when no compatible field path exists;
- tests must cover both mixed FDD field-locator families and no-`field=` processor family fixtures.

This makes the no-live implementation boundary code-generation-ready without introducing a public per-field anchor schema.

## Residual Risks

| Risk | Classification |
| --- | --- |
| R1-R4 runtime may still not activate A4 row materialization if the active path is legacy/no-`field=` locators or table/section preflight failure. | Covered by A5-S0 diagnostics and later live/PDF authorization; not blocking no-live plan. |
| R3 `missing_section=3` remains unresolved. | Tracked as A5-S2/separate missing-section diagnostic residual; not blocking locator adoption plan. |
| Exact implementation may choose a parser that treats malformed semicolon strings as field-locator-capable. | Implementation review must verify malformed/absent `field=` locators do not trigger unrelated anchor stripping. |

## Validation

Static artifact check:

```text
git diff --check -- docs/reviews/evidence-confirm-productionization-rr-09-a5-projection-locator-adoption-plan-20260624.md docs/reviews/plan-review-20260624-112914.md docs/reviews/evidence-confirm-productionization-rr-09-a5-plan-fix-20260624.md
```

Result: passed.

## Final Conclusion

`pass-with-risks`

The A5 plan is ready for controller judgment as a no-live implementation plan. It remains `NOT_READY` for release/readiness and requires a later explicit authorization before any live/PDF or product CLI evidence.
