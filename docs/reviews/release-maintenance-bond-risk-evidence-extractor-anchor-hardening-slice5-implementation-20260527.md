# Bond Risk Evidence Extractor / Anchor Hardening Slice 5 Implementation

> Date: 2026-05-27
> Work unit: `bond risk evidence extractor / anchor hardening design gate`
> Role: implementation worker
> Gate: Slice 5 score applicability and P1 registration
> Status: implemented, pending independent review/controller judgment

## Scope

Allowed files changed:

- `fund_agent/fund/extraction_score.py`
- `tests/fund/test_extraction_score.py`
- `docs/reviews/release-maintenance-bond-risk-evidence-extractor-anchor-hardening-slice5-implementation-20260527.md`

No commit, push, PR, approval, merge, ready marking, golden promotion, README update, design/control doc update, extractor/model/snapshot/quality-gate change, PDF/cache/source change, or FQ0-FQ6 threshold/severity change was performed.

## Implementation Summary

- Registered `bond_risk_evidence` in `FIELD_PRIORITY_BY_NAME` as `P1`.
- Updated `derive_score_applicability_issues` so exact `bond_fund` holdings replacement now looks for the same-fund same-year `bond_risk_evidence` snapshot row after holdings replacement applies.
- Added structured score helpers that consume only Slice 4 machine-readable snapshot fields:
  - `bond_risk_contract_status`
  - `bond_risk_satisfied_groups`
  - `bond_risk_missing_groups`
  - `bond_risk_weak_groups`
  - `bond_risk_ambiguous_groups`
- Kept `note` as non-authoritative; score satisfaction does not parse prose.
- Complete `contract_status="satisfied"` records with all seven required groups satisfied and `anchor_present=True` emit no `bond_risk_evidence_missing`.
- Missing, absent, malformed, missing-status, `contract_status="missing"`, anchorless, weak, ambiguous, or incomplete records emit `bond_risk_evidence_missing` with `baseline_blocking=True`.
- `required_evidence_groups` remains the full ordered seven-group contract from `BOND_RISK_EVIDENCE_GROUPS`.
- `missing_evidence_groups` is dynamic for partial records and all seven for whole-record fail-closed cases.
- Non-bond funds ignore `bond_risk_evidence` for score denominators and issues.
- Unknown/conflicting fund types remain fail-closed for `holdings_snapshot`; they are not inferred from `bond_risk_evidence`.

## Tests Added/Updated

- P1 registration for `bond_risk_evidence`.
- Exact bond fund with no positive row preserves the all-seven blocker.
- Complete positive bond-risk row scores P1 pass with 100% coverage/traceability and no bond issue.
- Weak `drawdown_stress` lists only `drawdown_stress`.
- Ambiguous `redemption_share_pressure` lists only `redemption_share_pressure`.
- Partial mixed groups keep required groups at all seven and dynamic missing groups exact.
- Anchor-missing accepted-looking record remains all-seven blocking.
- Malformed structured groups remain all-seven blocking.
- Missing `contract_status` remains all-seven blocking.
- Non-bond fund ignores `bond_risk_evidence`.
- Note prose cannot satisfy the contract.

## Validation Results

- `uv run pytest tests/fund/test_extraction_score.py -q`
  - Result: `54 passed in 0.78s`
- `uv run ruff check fund_agent/fund/extraction_score.py tests/fund/test_extraction_score.py`
  - Result: `All checks passed!`

## Residual Risks

- This slice validates score behavior with deterministic unit fixtures only. Real `006597` / `2024` extraction-score and quality-gate behavior remains a Slice 6 validation responsibility.
- `anchor_present=False` is treated as a whole-record anchor failure and returns all seven missing groups. The current Slice 4 snapshot row exposes field-level anchor presence, not per-group anchor absence, so score cannot prove an exact anchorless subgroup without additional structured fields.
- Multiple same-fund same-year `bond_risk_evidence` rows fail closed as absent/malformed by returning all seven missing groups. This is conservative and should be revisited only if snapshot intentionally supports repeated rows for this field.
