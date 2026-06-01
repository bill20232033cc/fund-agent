# Bond Risk Evidence Extractor / Anchor Hardening Slice 4 Code Review (DS)

> Date: 2026-05-28
> Branch: `codex/local-reconciliation`
> Gate: revised Slice 4 snapshot projection code review
> Role: code review worker (DS)
> Verdict: PASS

## Self-Check

- No implementation, commit, push, PR, approve, merge, mark-ready, or golden promotion work performed.
- Reviewed diff confirms only `fund_agent/fund/extraction_snapshot.py` and `tests/fund/test_extraction_snapshot.py` were changed.
- `fund_agent/fund/extraction_score.py` — zero diff, criterion 1 satisfied.

## Validation

```
uv run pytest tests/fund/test_extraction_snapshot.py -q → 12 passed
uv run ruff check fund_agent/fund/extraction_snapshot.py tests/fund/test_extraction_snapshot.py → All checks passed!
```

## Findings (severity ordered)

### No blocking findings.

### 1. Criterion 1: Slice 4 stays snapshot-only, no score edit

**PASS.** `git diff HEAD -- fund_agent/fund/extraction_score.py` returns empty. `FIELD_PRIORITY_BY_NAME` is untouched. No P1 registration, score coverage assertion, traceability denominator, FQ behavior, or golden promotion logic present in the diff.

### 2. Criterion 2: SnapshotRecord schema extension is additive, serialization predictable

**PASS.** Five new fields added to `SnapshotRecord` with explicit defaults:

- `bond_risk_contract_status: str | None = None`
- `bond_risk_satisfied_groups: tuple[str, ...] = ()`
- `bond_risk_missing_groups: tuple[str, ...] = ()`
- `bond_risk_weak_groups: tuple[str, ...] = ()`
- `bond_risk_ambiguous_groups: tuple[str, ...] = ()`

All five fields appear on every record (verified by `test_build_snapshot_records_contains_required_schema_and_all_fields` lines 173–196, which asserts field set via `asdict` includes all `_BOND_RISK_SNAPSHOT_FIELDS`). JSONL serialization via `asdict(record)` produces stable, predictable output. Defaults ensure backward compatibility: existing non-bond records carry `None`/`()` without disruption.

### 3. Criterion 3: bond_risk_evidence uses structured BondRiskEvidenceValue fields, not note parsing

**PASS.** In `_build_bond_risk_evidence_record` (line 1046):

```python
structured_value = value if isinstance(value, BondRiskEvidenceValue) else None
```

The `isinstance` guard prevents non-BondRiskEvidenceValue values from reaching structured field projection. The five bond-risk fields are populated directly from `structured_value.contract_status`, `.satisfied_group_ids`, etc. — no regex, split, or free-form parsing of the note string. The note tokens (line 1398–1410) are documented as human-readable only: "结构化字段仍是机器判定真源" (structured fields remain the machine-judgment truth source).

The field-level anchors used for first-anchor projection come from `extracted_field.anchors` (EvidenceAnchor objects with `source_kind`), not from `value.anchors` (BondRiskEvidenceAnchorRef objects without `source_kind`). This is architecturally correct: the snapshot anchor column projects field-level traceability, while group-level anchor refs live in the structured group fields for Slice 5 consumption.

### 4. Criterion 4: value_present and anchor_present semantics match amendment

**PASS.**

`_bond_risk_value_present` (line 1348):
```python
return value is not None and value.contract_status != _EXTRACTION_MODE_MISSING
```
Returns `True` only when a structured contract exists AND the contract is not `missing`. This exactly matches the amendment: "value_present=True only when the contract exists and is not missing."

Test `test_build_snapshot_records_treats_missing_bond_risk_contract_as_not_present` verifies: all-seven-groups-missing `BondRiskEvidenceValue` → `value_present=False`, `anchor_present=True`, `contract_status="missing"`, all seven groups in `bond_risk_missing_groups`. The non-null value object is correctly distinguished from value presence.

`_first_annual_report_anchor` (line 1364) filters `extracted_field.anchors` by `source_kind == "annual_report"`, returning the first match. This correctly implements "anchor_present=True only when a field-level annual-report anchor exists."

### 5. Criterion 5: missing/weak/ambiguous/satisfied groups preserved exactly; comparable_values stays empty

**PASS.** The four group-tracking fields are populated via `_string_tuple()` from their corresponding `BondRiskEvidenceValue` fields, preserving group ID strings and original order.

Test `test_build_snapshot_records_projects_partial_bond_risk_evidence_groups` verifies exact group membership after partial overrides:
- `drawdown_stress` → weak → `bond_risk_weak_groups == ("drawdown_stress",)`
- `redemption_share_pressure` → ambiguous → `bond_risk_ambiguous_groups == ("redemption_share_pressure",)`
- `convertible_bond_equity_exposure` → missing → `bond_risk_missing_groups == ("convertible_bond_equity_exposure",)`
- First 4 groups → satisfied → `bond_risk_satisfied_groups == tuple(BOND_RISK_EVIDENCE_GROUP_IDS[:4])`

`comparable_values` is hardcoded to `{}` in `_build_bond_risk_evidence_record` (line 1061). Test verifies `comparable_values == {}` in complete, partial, missing, and non-bond scenarios. `COMPARABLE_SUB_FIELDS_BY_FIELD` does not contain `bond_risk_evidence`, confirmed by assertion on line 239.

### 6. Criterion 6: Existing snapshot behavior, source provenance, nav, classification remains compatible

**PASS.** All 12 existing tests pass without modification (the new tests were added, not replacing old ones). `_build_extracted_field_record`, `_build_classification_record`, `_build_nav_record` are unchanged. Source provenance fields continue to be copied identically to all rows per `test_build_snapshot_records_copies_identical_bundle_source_provenance_to_all_rows`. NAV degradation note format preserved per `test_build_snapshot_records_preserves_unavailable_nav_reason`. Index quality and composite index comparable_values behavior unchanged per existing tests.

### 7. Criterion 7: Test coverage

**PASS.** Coverage matrix:

| Scenario | Test |
|---|---|
| Complete bond risk evidence row | `test_build_snapshot_records_projects_complete_bond_risk_evidence_row` |
| Partial with specific group statuses | `test_build_snapshot_records_projects_partial_bond_risk_evidence_groups` |
| Missing/non-bond (null value) | `test_build_snapshot_records_projects_missing_bond_risk_evidence_for_non_bond` |
| contract_status="missing" with non-null value | `test_build_snapshot_records_treats_missing_bond_risk_contract_as_not_present` |
| Schema field presence on all records | `test_build_snapshot_records_contains_required_schema_and_all_fields` |
| Field order insertion | `test_build_snapshot_records_contains_required_schema_and_all_fields` (line 240–243) |
| Non-comparable behavior | `test_build_snapshot_records_contains_required_schema_and_all_fields` (lines 238–239) |
| Existing behavior regression | All 12 tests pass, including provenance, nav, index quality, composite index, known-failure tests |

## Residuals

1. **No explicit test for anchor_present=False when field-level EvidenceAnchor exists but has non-annual-report source_kind.** The `_first_annual_report_anchor` negative path (e.g., only Eastmoney fallback anchors in `extracted_field.anchors`) lacks a dedicated test. Low risk: the logic is a simple linear scan; the no-anchor-at-all case is tested in the missing/non-bond test. If a fund's bond risk evidence comes solely from a non-annual-report source, anchor_present would correctly be False but the row would still carry structured group data — this is correct behavior but untested.

2. **Note format uses semicolon/comma delimiters without escaping.** The note string `contract_id=...; contract_status=...; satisfied_groups=g1,g2,g3;` would be ambiguous if any group ID itself contained a semicolon or comma. No current group IDs contain these characters, and the amendment explicitly designates structured fields as the machine-readable truth source. Acceptable.

3. **`_bond_risk_field` test helper ties extraction_mode to contract_status.** In production, extraction_mode reflects the extraction process, not the contract outcome. The test helper's simplification (`"direct" if contract_status == "satisfied" else "estimated"`) means the partial test's extraction_mode is "estimated" rather than whatever the real extractor produces. Test-only concern; production correctness unaffected.

4. **No coverage report for single-file ≥80% target.** AGENTS.md recommends ≥80% coverage for new/modified modules. The 12 tests exercise all new code paths and all existing ones, but no formal coverage measurement was run for this file specifically. The project CI coverage gate will provide the final number; if below threshold, the delta is in `write_snapshot_summary` and `run_extraction_snapshot` (existing code touched only by the field order insertion, not by new bond-risk logic).

## Deferred to Slice 5 (as expected per amendment)

- `FIELD_PRIORITY_BY_NAME` P1 registration for `bond_risk_evidence`
- Score applicability and traceability denominator updates
- Quality gate, golden fixture, or FQ behavior changes
- Consumption of structured snapshot fields for score logic

## Verdict

PASS. No blocking findings. The implementation faithfully executes the accepted Slice 4 amendment: snapshot-only, schema-additive, structured-field-driven, score-respecting. Tests cover the required scenarios. All tests pass, linting clean.
