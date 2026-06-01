# Bond Risk Evidence Extractor / Anchor Hardening Slice 4 Code Review (MiMo)

> Date: 2026-05-27
> Branch: `codex/local-reconciliation`
> Reviewer: MiMo (code review worker)
> Gate: revised Slice 4 snapshot projection review
> Scope: `fund_agent/fund/extraction_snapshot.py`, `tests/fund/test_extraction_snapshot.py`

## Verdict

**PASS**

No blocking findings. All seven review criteria satisfied.

## Validation

```
uv run pytest tests/fund/test_extraction_snapshot.py -q  → 12 passed in 0.71s
uv run ruff check fund_agent/fund/extraction_snapshot.py tests/fund/test_extraction_snapshot.py  → All checks passed!
```

## Findings (severity ordered)

### No blocking findings.

## Criterion-by-Criterion Assessment

### 1. Slice 4 stays snapshot-only; no edit to extraction_score.py or P1/score assertion

**PASS.** `extraction_snapshot.py` does not import, reference, or modify `FIELD_PRIORITY_BY_NAME`, `extraction_score.py`, or any score/gate logic. `FIELD_PRIORITY_BY_NAME` does not appear in the snapshot module. No P1 priority, score coverage, traceability denominator, score issue suppression, FQ behavior, or golden promotion assertions exist.

### 2. SnapshotRecord schema extension is additive; all records serialize predictably

**PASS.** Five new fields added to `SnapshotRecord` dataclass (lines 236-240), all with safe defaults:
- `bond_risk_contract_status: str | None = None`
- `bond_risk_satisfied_groups: tuple[str, ...] = ()`
- `bond_risk_missing_groups: tuple[str, ...] = ()`
- `bond_risk_weak_groups: tuple[str, ...] = ()`
- `bond_risk_ambiguous_groups: tuple[str, ...] = ()`

The `_snapshot_record` helper (lines 1081-1168) propagates these fields to all records. Existing records receive defaults (`None` / `()`), so JSONL serialization is predictable and backward-compatible.

### 3. bond_risk_evidence row uses structured BondRiskEvidenceValue fields, not note parsing

**PASS.** `_build_bond_risk_evidence_record` (lines 1012-1078) reads from `bundle.bond_risk_evidence.value` as `BondRiskEvidenceValue`. All group IDs (`satisfied_group_ids`, `missing_group_ids`, `weak_group_ids`, `ambiguous_group_ids`) and `contract_status` are taken from the structured value. The `note` field (line 1062) contains human-readable tokens (e.g., `contract_id=...`, `contract_status=...`) but is explicitly documented as supplementary — structured fields remain the machine-readable source of truth.

### 4. value_present and anchor_present semantics match amendment

**PASS.**
- `value_present`: `_bond_risk_value_present` (lines 1348-1361) returns `True` only when `value is not None and value.contract_status != "missing"`. This matches the amendment: "Set `value_present=True` only when the contract exists and is not `missing`."
- `anchor_present`: `_first_annual_report_anchor` (lines 1364-1380) returns the first anchor with `source_kind == "annual_report"`. `anchor_present` is `True` iff such an anchor exists. First-anchor compatibility fields (`section_id`, `page`, `table_id`, `row_id`) are derived from that anchor.

### 5. missing/weak/ambiguous/satisfied groups preserved exactly; comparable_values stays empty

**PASS.**
- `_string_tuple` (lines 1418-1431) preserves original order: `tuple(str(value) for value in values)`.
- `comparable_values={}` is hardcoded (line 1061), and `bond_risk_evidence` is absent from `COMPARABLE_SUB_FIELDS_BY_FIELD` (lines 49-84).

### 6. Existing snapshot behavior/source provenance/nav/classification remains compatible

**PASS.**
- `SNAPSHOT_FIELD_ORDER` (lines 30-48): new `("risk", "bond_risk_evidence")` inserted at index 14, after `("holdings", "holdings_snapshot")`. All 16 prior fields remain in original positions.
- `_snapshot_record` helper: bond risk fields are keyword-only with defaults, so existing call sites (e.g., `_build_extracted_field_record`, `_build_classification_record`, `_build_nav_record`) are unaffected.
- Source provenance fields copied from `bundle.source_provenance` identically to all rows.

### 7. Tests cover complete, partial, missing/non-bond, schema fields, field order, and non-comparable behavior

**PASS.** 12 tests pass. Bond-risk-specific coverage:

| Test | Scenario | Key assertions |
|------|----------|----------------|
| `test_build_snapshot_records_projects_complete_bond_risk_evidence_row` | All 7 groups accepted | `value_present=True`, `contract_status="satisfied"`, all 7 in `satisfied_groups`, note tokens present |
| `test_build_snapshot_records_projects_partial_bond_risk_evidence_groups` | Mixed weak/ambiguous/missing | `contract_status="partial"`, groups correctly partitioned across 4 fields |
| `test_build_snapshot_records_projects_missing_bond_risk_evidence_for_non_bond` | No bond risk evidence | `value_present=False`, `anchor_present=False`, all group tuples empty |
| `test_build_snapshot_records_treats_missing_bond_risk_contract_as_not_present` | All groups missing | `value_present=False`, `contract_status="missing"`, `anchor_present=True` (anchors still exist) |
| `test_build_snapshot_records_contains_required_schema_and_all_fields` | Schema + ordering | All 5 new fields present in payload, `bond_risk_evidence` absent from `COMPARABLE_SUB_FIELDS_BY_FIELD`, field order correct |

## Residual Risks

1. **Temporary UNMAPPED score state (by accepted amendment):** `bond_risk_evidence` is snapshot-visible but not registered in `FIELD_PRIORITY_BY_NAME`. This is acceptable as an intermediate local checkpoint because the existing all-seven bond blocker remains active until Slice 5.

2. **Slice 5 P1 registration is a hard dependency:** Slice 5 must register `bond_risk_evidence` in `FIELD_PRIORITY_BY_NAME` as `P1` and consume the structured snapshot fields for contract status and group IDs.

3. **Partial group test fixture inherits order from BOND_RISK_EVIDENCE_GROUP_IDS:** `test_build_snapshot_records_projects_partial_bond_risk_evidence_groups` asserts `satisfied_groups == tuple(BOND_RISK_EVIDENCE_GROUP_IDS[:4])`. This depends on the first 4 group IDs not being overridden. If the group ID order changes, the test will fail — this is acceptable but worth noting.
