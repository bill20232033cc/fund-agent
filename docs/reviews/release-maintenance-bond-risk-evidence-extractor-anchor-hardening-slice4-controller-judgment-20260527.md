# Bond Risk Evidence Extractor / Anchor Hardening Slice 4 Controller Judgment

> Date: 2026-05-27
> Work unit: `bond risk evidence extractor / anchor hardening design gate`
> Controller role: Gateflow controller
> Gate: revised Slice 4 snapshot projection
> Decision: accepted for local Slice 4 checkpoint

## Self-Check

- Current role: controller only; implementation and review were delegated.
- Branch: `codex/local-reconciliation`.
- Scope: snapshot projection only. No score edit, P1 priority registration, quality gate edit, golden promotion, Service/UI parameter change, PR, push, merge, approve, or mark-ready work.
- Source of truth: accepted Slice 4 plan amendment, amendment controller judgment, Slice 4 implementation v2 artifact, MiMo review, and DS review.
- Stop conditions: none remain. The original allowed-file stop condition was resolved by amendment; implementation stayed inside revised scope.

## Accepted Implementation

Slice 4 now projects `bond_risk_evidence` into extraction snapshot rows while leaving score semantics unchanged until Slice 5.

Accepted behavior:

- `SNAPSHOT_FIELD_ORDER` includes `("risk", "bond_risk_evidence")` immediately after `("holdings", "holdings_snapshot")`.
- `SnapshotRecord` is additively extended with:
  - `bond_risk_contract_status`
  - `bond_risk_satisfied_groups`
  - `bond_risk_missing_groups`
  - `bond_risk_weak_groups`
  - `bond_risk_ambiguous_groups`
- The bond-risk row reads `BondRiskEvidenceValue` structured fields directly and does not parse `note`.
- `value_present=True` only when a structured value exists and `contract_status != "missing"`.
- `anchor_present=True` only when the field-level anchors include an annual-report anchor.
- First-anchor compatibility fields remain populated from that annual-report anchor.
- `comparable_values` remains `{}` and `bond_risk_evidence` is not added to `COMPARABLE_SUB_FIELDS_BY_FIELD`.
- Human-readable `note` tokens are supplementary only; structured fields are the machine-readable contract for Slice 5.

## Review Finding Disposition

MiMo review: PASS, no blocking findings.

DS review: PASS, no blocking findings.

Accepted residuals:

- Temporary `UNMAPPED` score state is expected until Slice 5 registers `bond_risk_evidence` in `FIELD_PRIORITY_BY_NAME`.
- No dedicated test for non-annual-report-only anchors. Low risk; field-level no-anchor path is covered and Slice 6 real-report validation must confirm annual-report anchors.
- Note delimiter escaping is not material because score must consume structured fields, not note prose.
- Test helper simplification of `extraction_mode` is acceptable; contract status is tested through structured fields.
- Single-file coverage was not separately measured; global required coverage command remains part of final validation.

Rejected as not required in this slice:

- Editing `fund_agent/fund/extraction_score.py`.
- Asserting P1 priority, P1 coverage denominator, traceability denominator, score issue suppression, FQ behavior, or golden promotion.
- Parser/schema work beyond additive snapshot fields.

## Validation Evidence

Controller reran:

- `uv run pytest tests/fund/test_extraction_snapshot.py -q`
  - Result: `12 passed in 0.55s`
- `uv run ruff check fund_agent/fund/extraction_snapshot.py tests/fund/test_extraction_snapshot.py`
  - Result: `All checks passed!`
- `git diff --check`
  - Result: passed

Worker and reviewers also reported the Slice 4 checks passing.

## Boundary Judgment

Hard constraints remain intact:

- No FQ0-FQ6 weakening.
- No bypass of `FundDocumentRepository`; snapshot consumes already extracted bundles.
- Missing/weak/ambiguous evidence remains observable and not satisfied.
- No qualitative evidence is promoted to quantitative evidence.
- No golden corpus promotion.
- No QDII, FOF, 110020, release readiness, Host/Agent/dayu, PR, push, merge, approve, or mark-ready work.
- No explicit parameters hidden in `extra_payload`.
- UI -> Service -> Host -> Agent boundary is unchanged.

## Mandatory Slice 5 Carry-Forward

Slice 5 must:

- Register `bond_risk_evidence` in `FIELD_PRIORITY_BY_NAME` as `P1`.
- Consume the structured snapshot fields added in Slice 4.
- Keep current blocker behavior when the row is missing, malformed, partial, weak, ambiguous, or anchorless.
- Avoid parsing free-form `note` for score applicability.

## Decision

Slice 4 is accepted for local checkpoint. Proceed to Slice 5 score applicability and P1 registration.
