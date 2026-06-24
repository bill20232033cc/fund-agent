# RR-09 A5 Plan Fix

Gate: `RR-09 A5 Projection Locator Adoption / R3 Missing-section Residual Planning Gate`

Reviewed target: `docs/reviews/evidence-confirm-productionization-rr-09-a5-projection-locator-adoption-plan-20260624.md`

Plan review artifact: `docs/reviews/plan-review-20260624-112914.md`

## Accepted Finding

### PR-001

Status: `已修复`

The original A5 plan made the fail-closed empty-anchor behavior too broad. Because `_field_from_family()` is shared by all `FundProcessorResult` projections, applying empty-anchor behavior to every family with no `field=` locator could strip valid anchors from non-FDD processor paths such as `active_annual.py`, which wraps legacy extractor outputs into processor family results.

## Fix Applied

The plan now narrows field-specific filtering to field-locator-capable processor families:

- If a family contains recognized semicolon `field=` Processor locators, top-level fields select only compatible exact or dot-prefix anchors.
- If a family contains recognized `field=` locators but none match the requested field, the field gets empty anchors and remains fail-closed.
- If a family contains no recognized semicolon `field=` Processor locators, `_field_from_family()` must preserve the existing `family_result.anchors` behavior.

The plan also now requires tests proving:

- mixed FDD `return_attribution.v1` and `manager_profile.v1` anchors are filtered by field path;
- no-`field=` processor family fixtures keep existing anchors.

## Validation

Static artifact validation:

```text
git diff --check -- docs/reviews/evidence-confirm-productionization-rr-09-a5-projection-locator-adoption-plan-20260624.md docs/reviews/plan-review-20260624-112914.md docs/reviews/evidence-confirm-productionization-rr-09-a5-plan-fix-20260624.md
```

Result: passed.

## Residual Risks

| Risk | Disposition |
| --- | --- |
| Runtime R1-R4 may use no-`field=` legacy processor/extractor locators and still not activate A4 row materialization. | Covered by A5-S0 diagnostic and later live/PDF authorization precheck. |
| R3 `missing_section=3` remains open. | Preserved as separate A5-S2/separate diagnostic residual. |

## Verdict

`RR_09_A5_PLAN_FIX_READY_FOR_REREVIEW_NOT_READY`
