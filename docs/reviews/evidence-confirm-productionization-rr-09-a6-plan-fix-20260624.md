# Evidence Confirm Productionization RR-09 A6 Plan Fix

Verdict token:

`RR_09_A6_PLAN_FIX_READY_FOR_REREVIEW_NOT_READY`

## Scope

Fix accepted plan-review finding PR-001 from:

`docs/reviews/plan-review-20260624-125616.md`

Reviewed plan:

`docs/reviews/evidence-confirm-productionization-rr-09-a6-projection-runtime-locator-adoption-plan-20260624.md`

This is a planning-only fix. No production code, tests, live/PDF command, product CLI command, provider/LLM call, checklist/report-body rendering, V2/ECQ/quality-gate semantic change, push, tag, release or readiness promotion was performed.

## Finding Status

| Finding | Status | Resolution |
|---|---|---|
| PR-001 subfield scoped anchors can be fabricated from field-level anchors | fixed in plan | A6-S1 now emits only top-level `source_field_path=<field>` for parsed annual anchors. Subfield-scoped semantic locators are reserved for direct anchor-to-subfield provenance. |

## Plan Changes

The plan now states:

- Default parsed annual projection exposes top-level field-scoped semantic locators only.
- Parsed annual projection must not infer `source_field_path=<field>.<subfield>` from composite dict value shape.
- `source_field_path=<field>.<subfield>` is allowed only when the caller already has direct subfield provenance, such as an explicit source-truth/FDD anchor or a no-live materializer fixture modeling direct provenance.
- A6-S1 tests must prove parsed annual projection does not generate inferred subfield locators.
- A6-S2 tests must include a negative parsed-annual-style composite fixture that avoids fabricated subfield row proof.

## Validation

```bash
rg -n "subfield|source_field_path|fabricat|A6-S1|A6-S2" \
  docs/reviews/evidence-confirm-productionization-rr-09-a6-projection-runtime-locator-adoption-plan-20260624.md \
  docs/reviews/plan-review-20260624-125616.md
git diff --check
```

Results:

- Plan text now contains explicit top-level-only parsed annual constraints.
- Plan text retains direct subfield materializer support only where direct provenance is supplied.
- `git diff --check` passed.

## Residual Risks

| Risk | Destination |
|---|---|
| Top-level parsed annual field scoping may not fully close all composite value-match failures | A6 implementation evidence and later live/PDF authorization |
| Extractor-specific direct subfield provenance may still be required for full R1-R4 closure | Later A7 extractor-specific locator precision gate |
| R3 `missing_section=3` remains independent | Existing R3 missing-section residual |

## Next Gate

`RR-09 A6 Targeted Plan Re-review Gate`

Completion token:

`RR_09_A6_PLAN_FIX_READY_FOR_REREVIEW_NOT_READY`
