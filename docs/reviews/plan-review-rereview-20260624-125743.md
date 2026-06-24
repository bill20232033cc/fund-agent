# Plan Review Re-review 20260624-125743

Reviewed target:

`docs/reviews/evidence-confirm-productionization-rr-09-a6-projection-runtime-locator-adoption-plan-20260624.md`

Prior review:

`docs/reviews/plan-review-20260624-125616.md`

Scope:

Targeted re-review of PR-001 only. No implementation code was reviewed.

## Finding Status

### PR-001-已修复-高-subfield scoped anchors can be fabricated from field-level anchors

- **Prior problem**: The original plan allowed parsed annual projection to walk composite dict values and clone every field anchor into every subfield path, which could fabricate anchor-to-subfield proof.
- **Plan fix observed**:
  - Goal now says parsed annual exposes top-level field-scoped locators while reserving subfield locators for direct anchor-to-subfield provenance.
  - Success signals now use top-level parsed annual fields (`fee_schedule`, `nav_benchmark_performance`, `manager_alignment`, `manager_strategy_text`) and explicitly prohibit inferring subfield scope from value shape.
  - A6-S1 no longer contains `_public_value_paths(...)` and now requires `_field_scoped_anchors(...)` to clone anchors with `source_field_path=mapping.output_field_name` only.
  - Tests now require a negative assertion that parsed annual projection does not generate `source_field_path=fee_schedule.management_fee` from composite dict values.
  - A6-S2 distinguishes top-level parsed annual scope from direct subfield scope and requires a negative composite fixture.
- **Direct evidence**:
  - Plan lines contain `Parsed annual processors may emit only top-level source_field_path values unless they have direct source evidence linking an anchor to a subfield`.
  - Plan lines contain `It must not emit source_field_path=<field>.<subfield> for parsed annual fields`.
  - Plan lines contain `Composite value shape fabricates subfield proof` risk control.
- **Status**: 已修复

## Open Questions

None blocking for planning handoff.

## Residual Risks

| Risk | Destination |
|---|---|
| A6 top-level field scoping may be necessary but insufficient to close all R1-R4 value-match failures | A6 implementation evidence plus later live/PDF re-evidence authorization |
| Full closure may require extractor-specific direct subfield provenance | Later A7 extractor-specific locator precision planning |

## Conclusion

`pass-with-risks`

PR-001 is fixed. The plan is now safe to hand to a no-live implementation worker, with the explicit residual that A6 may only remove cross-field anchor ambiguity and may not fully close composite subfield row precision.
