# Targeted Plan Re-review: RR-09 A3 Fix Plan

Reviewed target:

`docs/reviews/evidence-confirm-productionization-rr-09-a3-coarse-reference-bond-risk-fix-plan-20260624.md`

Prior review:

`docs/reviews/plan-review-20260624-095336.md`

Scope:

Only PR-001 from the prior review was re-reviewed. No new full-plan review was performed.

## Prior Finding Status

### PR-001-已修复-高-S2 narrowing lacks a precise token-source and ambiguity contract

- **Prior issue**: A3-S2 allowed optional fact value context but did not specify exact V2-token reuse, anchor-to-fact cardinality, or ambiguity handling.
- **Fix evidence**:
  - Plan now requires reuse of V2 deterministic primitives from `fund_agent.fund.evidence_confirm`: `_material_tokens`, `_normalize_text`, `_token_matches_excerpt`.
  - Plan now requires `anchor_id -> facts` to be built privately inside `build_annual_report_evidence_confirm_references()` from the already-passed `ChapterFactProjection`.
  - Plan now permits row narrowing only when exactly one available non-derived fact references the anchor and all V2 material tokens for that fact match exactly one table row.
  - Plan now requires degradation, not row precision, when there are zero facts, multiple facts, no material tokens, multiple matching rows, no matching rows, partial token matches, malformed tables, or unsupported section-only narrowing.
  - Planned tests now cover shared-anchor ambiguity and partial-token match.
- **Re-review decision**: `已修复`.

## Residual Risks

| Risk | Status |
|---|---|
| Real R1-R4 live/PDF rows may still be too coarse for strict V2 pass | Tracked to later authorized live/PDF re-evidence. |
| Private V2 helper imports may deserve future public helper extraction | Not blocking for A3; existing accepted diagnostic helper already uses the same pattern. |
| B1 runtime product CLI residual remains open | Separate authorization. |

## Conclusion

`pass-with-risks`

The prior blocking plan-review finding is fixed. The plan is ready for controller judgment; it still does not authorize implementation, live/PDF execution, product CLI execution or release/readiness.
