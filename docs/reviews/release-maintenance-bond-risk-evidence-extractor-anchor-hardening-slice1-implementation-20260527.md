# Bond Risk Evidence Extractor / Anchor Hardening Slice 1 Implementation

> Date: 2026-05-27
> Role: implementation worker
> Gate: implementation Slice 1 for `bond risk evidence extractor / anchor hardening design gate`
> Scope: Slice 1 Model Contract only
> Accepted plan commit: `0a5bac9`

## Self-Check

### Before Start

- Self-check: pass
- Role confirmed: implementation worker only, not controller.
- Scope confirmed: Slice 1 Model Contract only.
- Prohibited actions avoided: no workflow command, no skill, no review, no stage, no commit, no push, no PR, no merge, no golden promotion.
- Allowed files confirmed:
  - `fund_agent/fund/extractors/models.py`
  - `tests/fund/extractors/test_bond_risk_evidence.py`
  - this implementation artifact path

### Before File Edits

- Self-check: pass
- Planned edits were limited to model contract types, pure validator helper, focused tests, and this artifact.
- No extraction, snapshot, score, data extractor, README, design, implementation-control, or gate/control files were edited.

### Before Completion

- Self-check: pass
- Changed files remain within the assigned slice.
- Validation commands required by handoff were run and passed.
- Stop status: complete for Slice 1 only.

## Changed Files

- `fund_agent/fund/extractors/models.py`
- `tests/fund/extractors/test_bond_risk_evidence.py`
- `docs/reviews/release-maintenance-bond-risk-evidence-extractor-anchor-hardening-slice1-implementation-20260527.md`

## Implemented Items

- Added `BondRiskEvidenceStatus`.
- Added `BondRiskEvidenceStrength`.
- Added `BondRiskEvidenceGroupId` with the seven required group ids:
  - `duration_rate_risk`
  - `credit_risk`
  - `leverage_liquidity`
  - `asset_allocation_holdings_mix`
  - `drawdown_stress`
  - `redemption_share_pressure`
  - `convertible_bond_equity_exposure`
- Added `BondRiskEvidenceAnchorRef`.
- Added `BondRiskEvidenceGroupRecord`.
- Added `BondRiskEvidenceValue`.
- Added `validate_bond_risk_evidence_value(value: BondRiskEvidenceValue) -> None`.
- Added Chinese docstrings referencing template第6章核心风险 for the new contract types and validator helpers.

## Enforced Invariants

- `schema_version` and `contract_id` must be `bond_risk_evidence.v1`.
- Exactly seven group records must be present.
- Group ids must exactly match the seven required ids and must not repeat.
- Accepted and weak records must reference at least one resolvable stable group-level anchor.
- Referenced anchors must exist in `BondRiskEvidenceValue.anchors`.
- Stable anchor ids must match `bond-risk:<fund_code>:<report_year>:<group_id>:<ordinal>`.
- `accepted` and `accepted_absence` records derive `satisfied_group_ids`.
- `missing`, `weak`, and `ambiguous` statuses derive their corresponding id tuples.
- Caller-provided derived id tuples are rejected when inconsistent with group statuses.
- `weak` drawdown-control records validate as weak and remain unsatisfied.
- Explicit absence convertible/equity records validate as accepted absence.

## Validation

- `uv run pytest tests/fund/extractors/test_bond_risk_evidence.py -q`
  - Result: passed, `6 passed in 0.52s`
- `uv run ruff check fund_agent/fund/extractors/models.py tests/fund/extractors/test_bond_risk_evidence.py`
  - Result: passed, `All checks passed!`

## Docs Decision

- No README, `docs/design.md`, or `docs/implementation-control.md` update in Slice 1.
- Reason: assigned slice is model contract only and handoff explicitly restricts edits to the listed code/test files plus this implementation artifact.

## Residual Risks / Uncovered Areas

- No extractor implementation in this slice.
- No `StructuredFundDataBundle` integration in this slice.
- No snapshot projection in this slice.
- No score applicability behavior change in this slice.
- No real `006597` annual-report evidence extraction or anchor normalization in this slice.

## Stop Status

- Slice 1 implementation is complete.
- Work stopped at the assigned model-contract boundary.
