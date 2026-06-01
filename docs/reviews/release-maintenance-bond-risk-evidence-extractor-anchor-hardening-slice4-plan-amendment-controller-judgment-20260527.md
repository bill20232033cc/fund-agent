# Bond Risk Evidence Extractor / Anchor Hardening Slice 4 Plan Amendment Controller Judgment

> Date: 2026-05-27
> Work unit: `bond risk evidence extractor / anchor hardening design gate`
> Controller role: Gateflow controller
> Gate: Slice 4 stop-condition resolution
> Decision: amendment accepted; resume Slice 4 with revised scope

## Self-Check

- Current role: controller only; the blocked implementation, amendment, and amendment reviews were delegated.
- Branch: `codex/local-reconciliation`.
- Scope: resolving a plan/file-ownership mismatch only. No code implementation, score edit, quality gate edit, golden promotion, PR, push, merge, approve, or mark-ready work.
- Source of truth: original accepted plan, blocked Slice 4 implementation artifact, plan amendment artifact, MiMo review, and DS review.
- Stop conditions: the original Slice 4 stop condition was correctly triggered and is now resolved by an accepted amendment. No user-input blocker remains.

## Root Fact

`FIELD_PRIORITY_BY_NAME` is defined in `fund_agent/fund/extraction_score.py`, not in `fund_agent/fund/extraction_snapshot.py`.

The original Slice 4 allowed files only included snapshot files, while original Slice 5 already included score files. Therefore adding P1 registration in Slice 4 would either cross allowed scope or merge snapshot projection and score semantics into one slice.

## Accepted Amendment

Slice 4 remains snapshot-only:

- Allowed files stay limited to `fund_agent/fund/extraction_snapshot.py` and `tests/fund/test_extraction_snapshot.py`.
- Slice 4 implements `bond_risk_evidence` snapshot projection, additive machine-readable fields, first-anchor projection, and non-comparable correctness behavior.
- Slice 4 must not edit `FIELD_PRIORITY_BY_NAME`, `extraction_score.py`, score applicability, quality gate, or golden fixtures.
- Temporary post-Slice-4 state may expose an `UNMAPPED` `bond_risk_evidence` row. This is acceptable only as an intermediate local checkpoint because the existing all-seven bond blocker remains active.

Slice 5 inherits a non-optional score requirement:

- Register `bond_risk_evidence` in `FIELD_PRIORITY_BY_NAME` as `P1`.
- Consume Slice 4 structured snapshot fields for contract status and group ids.
- Do not parse free-form `note` to decide score applicability.

## Review Disposition

MiMo review: PASS.

- Accepted P1 deferral as architecturally justified.
- Accepted temporary `UNMAPPED` state as bounded local intermediate state.
- Accepted additive `SnapshotRecord` schema extension as feasible.
- Advisory residuals: make note formatting scope explicit and keep P1 assertions out of Slice 4.

DS review: PASS.

- Verified score currently does not consume `bond_risk_evidence`; current blocker remains unchanged until Slice 5.
- Accepted schema extension as additive and preferable to prose parsing.
- Flagged Slice 5 P1 registration as hard dependency.

Controller disposition:

- No fix required for amendment.
- No user decision required; the correct path is unambiguous and stays within existing gate scope.
- Implementation control must not close this gate until Slice 5 completes P1 registration and score applicability behavior.

## Revised Slice 4 Handoff Conditions

Slice 4 implementation must:

- Add `("risk", "bond_risk_evidence")` to `SNAPSHOT_FIELD_ORDER`.
- Add additive `SnapshotRecord` fields:
  - `bond_risk_contract_status`
  - `bond_risk_satisfied_groups`
  - `bond_risk_missing_groups`
  - `bond_risk_weak_groups`
  - `bond_risk_ambiguous_groups`
- Keep `bond_risk_evidence` out of `COMPARABLE_SUB_FIELDS_BY_FIELD`.
- Set `value_present=True` only when the contract exists and is not `missing`.
- Set `anchor_present=True` only when a field-level annual-report anchor exists.
- Preserve first-anchor compatibility fields for human traceability.
- Expose the group data through structured fields so Slice 5 can avoid prose parsing.
- Document the temporary `UNMAPPED` score state as residual.

Slice 4 implementation must not:

- Edit `fund_agent/fund/extraction_score.py`.
- Assert P1 priority, score coverage, traceability denominator, score issue suppression, FQ behavior, or golden promotion.
- Use `note` as the only machine-readable bond-risk contract.

## Decision

The amendment is accepted. Proceed with revised Slice 4 implementation. The blocked implementation artifact remains part of the audit trail and should be included in the next accepted checkpoint.
