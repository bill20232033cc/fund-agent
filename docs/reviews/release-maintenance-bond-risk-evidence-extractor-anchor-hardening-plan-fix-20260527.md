# Bond Risk Evidence Extractor / Anchor Hardening Plan Fix

> Date: 2026-05-27
> Role: planning fix worker
> Gate: plan fix after plan review
> Work unit: `bond risk evidence extractor / anchor hardening design gate`
> Edited plan: `docs/reviews/release-maintenance-bond-risk-evidence-extractor-anchor-hardening-plan-20260527.md`
> Source review: `docs/reviews/release-maintenance-bond-risk-evidence-extractor-anchor-hardening-plan-review-ds-20260527.md`
> Status: completed

## Scope Guard

- Self-check before work: pass.
- Role confirmed: planning fix worker only, not controller.
- No workflow command or skill was started.
- No implementation, tests, review, staging, commit, push, PR, merge, golden promotion, or baseline promotion was performed.
- Writes were limited to the approved plan artifact and this fix artifact.
- Plan goal and scope were not changed beyond the three controller-accepted findings.

## Finding Status

### DS 01: `bond_risk_evidence` Field Priority

Status: fixed in plan.

Plan changes:

- Registered `bond_risk_evidence` as `P1` in `FIELD_PRIORITY_BY_NAME`.
- Defined coverage semantics: `value_present` comes from `contract_status != "missing"`.
- Defined traceability semantics: `anchor_present` requires at least one stable group-level annual-report anchor.
- Added the expected complete `006597` / `2024` assertion: 100% P1 coverage and 100% P1 traceability for this field.
- Added Slice 4 tests and validation assertions for the P1 coverage/traceability behavior.

### DS 02: Non-Bond Extraction Boundary

Status: fixed in plan.

Plan changes:

- Changed extractor signature to receive `classified_fund_type` explicitly:
  `extract_bond_risk_evidence(report: ParsedAnnualReport, classified_fund_type: str | None)`.
- Added non-bond early-return boundary: non-`bond_fund` returns missing/not-applicable without scanning the seven bond evidence groups.
- Kept parameters explicit and reaffirmed that no hidden `extra_payload` state is allowed.
- Added Slice 2 and Slice 3 tests and stop conditions for unavailable explicit fund type.
- Preserved score-side non-bond ignore behavior as an additional safety boundary.

### DS 03: Required vs Missing Evidence Groups

Status: fixed in plan.

Plan changes:

- Stated the invariant that `required_evidence_groups` always equals all seven `BOND_RISK_EVIDENCE_GROUPS` ids.
- Stated that `missing_evidence_groups` is dynamic instance state and contains only unsatisfied groups.
- Added Slice 5 invariants, tests, and smoke assertions to prevent shrinking `required_evidence_groups` to the missing subset.

## Self-Check

Self-check: pass.

- All three controller-accepted findings were addressed.
- No new material choices were introduced.
- No plan goal or scope expansion was introduced.
- No files outside the allowed write set were modified.
