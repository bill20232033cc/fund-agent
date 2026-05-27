# Bond Risk Evidence Extractor / Anchor Hardening Slice 5 Fix

> Date: 2026-05-27
> Role: fix worker
> Gate: Slice 5 accepted-finding fix after code review

## Scope

- Changed `fund_agent/fund/extraction_score.py`
- Changed `tests/fund/test_extraction_score.py`
- Added this fix artifact

No commit, push, PR, approval, merge, ready marking, or golden promotion was performed.

## Fixed Finding

Accepted finding: a malformed or inconsistent `bond_risk_evidence` snapshot row with `value_present=false`, `anchor_present=true`, `bond_risk_contract_status=satisfied`, and all seven satisfied groups could be treated as satisfying `bond_risk_evidence.v1`.

Fix: `_bond_risk_unsatisfied_groups` now treats `value_present=false` as an all-seven fail-closed condition before trusting structured contract status or group fields. This keeps missing field value evidence from turning into a pass through inconsistent structured metadata.

Regression coverage: added a focused test where `value_present=false`, `anchor_present=true`, `contract_status=satisfied`, and all seven groups are listed as satisfied. The score still emits `bond_risk_evidence_missing`, keeps all seven groups in `missing_evidence_groups`, and sets `baseline_blocking=true`.

## Validation

- `uv run pytest tests/fund/test_extraction_score.py -q` -> `55 passed in 0.83s`
- `uv run ruff check fund_agent/fund/extraction_score.py tests/fund/test_extraction_score.py` -> `All checks passed!`

## Residuals

- Per-group anchor validation remains deferred; field-level `anchor_present` is still the current gate contract.
- Duplicate `bond_risk_evidence` rows still fail closed; behavior left unchanged.
- Logic duplication between issue derivation and applicability decision derivation remains unchanged.
