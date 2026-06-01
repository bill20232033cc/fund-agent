# Bond Risk Evidence Extractor / Anchor Hardening Slice 4 Implementation v2

> Date: 2026-05-27
> Branch: `codex/local-reconciliation`
> Gate: revised Slice 4 snapshot projection after accepted plan amendment
> Role: implementation worker
> Status: implementation complete; review required

## Scope

Implemented only the accepted Slice 4 snapshot projection amendment. No full gateflow, self-review, commit, push, PR, approval, merge, mark-ready, golden promotion, score edit, quality-gate edit, fixture edit, README edit, design/control edit, PDF/cache/source change, or external workflow action was performed.

## Files Changed

- `fund_agent/fund/extraction_snapshot.py`
- `tests/fund/test_extraction_snapshot.py`
- `docs/reviews/release-maintenance-bond-risk-evidence-extractor-anchor-hardening-slice4-implementation-v2-20260527.md`

## Implementation Summary

- Added `("risk", "bond_risk_evidence")` to `SNAPSHOT_FIELD_ORDER` immediately after `("holdings", "holdings_snapshot")`.
- Extended `SnapshotRecord` additively with machine-readable bond risk fields:
  - `bond_risk_contract_status`
  - `bond_risk_satisfied_groups`
  - `bond_risk_missing_groups`
  - `bond_risk_weak_groups`
  - `bond_risk_ambiguous_groups`
- Built the `bond_risk_evidence` row from `bundle.bond_risk_evidence.value` as a `BondRiskEvidenceValue`, using structured contract fields instead of parsing `note`.
- Set `value_present=True` only when the structured contract exists and `contract_status != "missing"`.
- Set `anchor_present=True` only when the field-level anchors include at least one `source_kind="annual_report"` anchor, and preserved first-anchor compatibility fields from that annual-report anchor.
- Kept `bond_risk_evidence` out of `COMPARABLE_SUB_FIELDS_BY_FIELD`, so `comparable_values` remains `{}` and the row stays out of the golden correctness comparable-value denominator in this slice.
- Added stable human-readable note tokens when a structured value exists:
  - `contract_id=...`
  - `contract_status=...`
  - `satisfied_groups=...`
  - `missing_groups=...`
  - `weak_groups=...`
  - `ambiguous_groups=...`

## Tests Added / Updated

- Covered complete `bond_risk_evidence` row projection, including risk group/name, value presence, annual-report anchor projection, first-anchor compatibility fields, structured contract/group fields, note tokens, and empty comparable values.
- Covered partial evidence with explicit missing, weak, and ambiguous groups projected through structured fields.
- Covered non-bond/default missing row with no value, no anchor, no structured group data, and empty comparable values.
- Covered structured `contract_status="missing"` with a non-null value so `value_present` remains false.
- Covered schema field presence on all records.
- Covered field order insertion after `holdings_snapshot`.
- Covered `bond_risk_evidence` absence from `COMPARABLE_SUB_FIELDS_BY_FIELD`.

## Validation

```bash
uv run pytest tests/fund/test_extraction_snapshot.py -q
```

Result: `12 passed in 0.39s`

```bash
uv run ruff check fund_agent/fund/extraction_snapshot.py tests/fund/test_extraction_snapshot.py
```

Result: `All checks passed!`

## Residual Risks

- Temporary `UNMAPPED` score state remains by accepted amendment: `bond_risk_evidence` is snapshot-visible but not yet registered in `FIELD_PRIORITY_BY_NAME`.
- Existing bond-risk applicability blocker remains active until Slice 5 consumes the structured snapshot fields and updates score semantics.
- The additive JSONL schema extension adds five nullable/tuple fields to every snapshot row; this was judged feasible within Slice 4 because it is additive and avoids prose parsing in Slice 5.

## Explicit Deferral

`FIELD_PRIORITY_BY_NAME` P1 registration for `bond_risk_evidence` is deferred to Slice 5 by the accepted plan amendment. Slice 4 intentionally does not edit `fund_agent/fund/extraction_score.py` and does not assert P1 priority, score coverage, score traceability, score applicability issue suppression, or golden promotion behavior.
