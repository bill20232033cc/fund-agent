# Bond Risk Evidence Extractor / Anchor Hardening Slice 5 Code Review

> Date: 2026-05-27
> Reviewer: MiMo (code review worker)
> Work unit: `bond risk evidence extractor / anchor hardening design gate`
> Gate: Slice 5 score applicability and P1 registration
> Decision: **PASS**

## Self-Check

- Role: code review worker only. No implementation, edit, commit, push, PR, approve, merge, mark-ready, or golden promotion.
- Files reviewed: `fund_agent/fund/extraction_score.py`, `tests/fund/test_extraction_score.py`.
- Read context: AGENTS.md, plan artifact, Slice 4 controller judgment, Slice 5 implementation artifact.
- Validation: `uv run pytest tests/fund/test_extraction_score.py -q` → 54 passed in 0.71s; `uv run ruff check` → All checks passed.

## Review Criteria Verification

### 1. P1 registration and complete bond evidence → 100% coverage/traceability, no issue

**PASS.**

- `FIELD_PRIORITY_BY_NAME["bond_risk_evidence"] = "P1"` at line 55.
- `test_field_priority_includes_bond_risk_evidence_as_p1` asserts P1 registration.
- `test_complete_bond_risk_evidence_record_scores_p1_pass_without_issue` verifies: `coverage_rate == 1.0`, `traceability_rate == 1.0`, `status == STATUS_PASS`, `fund_score.p1_status == STATUS_PASS`, `replacement_issue_ids == ()`, `derive_score_applicability_issues == ()`.

### 2. Missing/absent/malformed/missing-status/contract_status missing/anchorless → baseline_blocking

**PASS.**

`_bond_risk_unsatisfied_groups` returns all seven group ids for every fail-closed case:

- `record is None` → all seven.
- `anchor_present` falsy → all seven.
- `contract_status` not in `{satisfied, partial, missing}` → all seven.
- `contract_status == "missing"` → all seven.
- Structured groups malformed (`_string_tuple_field` returns None) → all seven.
- Unknown group ids → all seven.

Tests cover each case explicitly:

| Test | Scenario |
|---|---|
| `test_bond_fund_excludes_equity_holdings_with_replacement_issue` | No positive row → all seven missing |
| `test_anchor_missing_accepted_bond_risk_evidence_remains_all_seven_blocking` | `anchor_present=False` → all seven |
| `test_malformed_bond_risk_evidence_record_remains_all_seven_blocking` | `satisfied_groups` string instead of tuple → all seven |
| `test_missing_contract_status_bond_risk_evidence_remains_all_seven_blocking` | `contract_status=None` → all seven |

All emitted issues have `baseline_blocking=True`.

### 3. Weak/ambiguous groups remain unsatisfied; dynamic missing_evidence_groups is exact

**PASS.**

`_bond_risk_unsatisfied_groups` computes:
```python
explicit_unsatisfied = {*missing_groups, *weak_groups, *ambiguous_groups}
absent_from_satisfied = set(group_ids) - set(satisfied_groups)
unsatisfied = explicit_unsatisfied | absent_from_satisfied
```

For `partial` status, returns only groups in `unsatisfied` filtered by `group_ids` order. Tests verify exactness:

| Test | Unsatisfied groups | `missing_evidence_groups` |
|---|---|---|
| `test_weak_drawdown_...` | `drawdown_stress` (weak) | `("drawdown_stress",)` |
| `test_ambiguous_redemption_...` | `redemption_share_pressure` (ambiguous) | `("redemption_share_pressure",)` |
| `test_partial_bond_risk_...` | 3 mixed (missing + weak + ambiguous) | exact 3-tuple |

### 4. required_evidence_groups always full ordered seven groups

**PASS.**

`_bond_risk_evidence_missing_issue` always sets:
```python
group_ids = tuple(group.group_id for group in BOND_RISK_EVIDENCE_GROUPS)
```
and assigns `required_evidence_groups=group_ids`. This is a contract-level invariant independent of instance-level `missing_evidence_groups`.

Tests `test_weak_drawdown_...`, `test_ambiguous_redemption_...`, and `test_partial_bond_risk_...` all assert `issue.required_evidence_groups == _BOND_RISK_GROUP_IDS`.

### 5. Score consumes Slice 4 structured fields only, no note parsing

**PASS.**

`_bond_risk_unsatisfied_groups` reads only:
- `record.get("anchor_present")`
- `_optional_record_text(record, "bond_risk_contract_status")`
- `_string_tuple_field(record, "bond_risk_satisfied_groups")`
- `_string_tuple_field(record, "bond_risk_missing_groups")`
- `_string_tuple_field(record, "bond_risk_weak_groups")`
- `_string_tuple_field(record, "bond_risk_ambiguous_groups")`

No `note` access anywhere in score logic. `test_bond_risk_score_does_not_parse_note_for_satisfaction` explicitly confirms that a forged `note` containing `"contract_status=satisfied"` does not override the structured `contract_status="missing"`.

### 6. Non-bond and unknown/conflicting fund types remain unaffected/fail-closed

**PASS.**

- `_is_non_applicable_bond_risk_evidence_record_for_type` excludes `bond_risk_evidence` from P1 denominator for non-`bond_fund` types.
- `derive_score_applicability_issues` gates on `classified_fund_type != BOND_FUND_TYPE` → `continue`.
- No fund type inference from `bond_risk_evidence` content.
- `test_non_bond_fund_ignores_bond_risk_evidence_record` verifies: `bond_risk_evidence` not in field rows, no missing P1 fields, no issues.
- `test_unknown_or_conflicted_fund_type_keeps_holdings_fail_closed` (pre-existing) confirms fail-closed for unknown/conflicting types.

### 7. FQ0-FQ6, quality_gate, snapshot, data_extractor, golden fixtures, source/PDF/cache access untouched

**PASS.**

- Diff scope is limited to `extraction_score.py` and `test_extraction_score.py`.
- No changes to `extraction_snapshot.py`, `data_extractor.py`, `quality_gate.py`, golden fixtures, or any source/PDF/cache code.
- Existing `test_source_provenance_keys_do_not_change_score_outputs` continues to pass, confirming no regression in gate-sensitive outputs.
- Existing `test_run_extraction_score_writes_score_outputs` continues to pass, confirming score.json top-level key set and FQ output shape unchanged.

### 8. Tests cover all planned paths; no false pass from weakened denominator semantics

**PASS.**

54 tests pass. Slice 5 adds 11 new tests covering:

1. P1 registration
2. Complete positive → P1 pass, no issue
3. Weak drawdown → exact single group
4. Ambiguous redemption → exact single group
5. Partial mixed → exact 3 groups, required stays 7
6. Anchor-missing → all seven blocking
7. Malformed structured groups → all seven blocking
8. Missing contract_status → all seven blocking
9. Non-bond fund ignores bond_risk_evidence
10. Note prose cannot satisfy contract
11. Issue id determinism (pre-existing, still passes)

Denominator semantics are preserved: `required_evidence_groups` is always the full seven, `missing_evidence_groups` is dynamic, `baseline_blocking=True` on all emitted issues.

## Findings

No blocking findings.

## Residual Risks

1. **`_bond_risk_contract_satisfied` is defined but unused in this slice.** It delegates to `_bond_risk_unsatisfied_groups` and is a convenience wrapper. Low risk; may be useful in Slice 6 or quality gate integration. Not a blocking finding.

2. **Multiple same-fund same-year `bond_risk_evidence` rows return `None`.** `_bond_risk_evidence_record_for_fund` returns `None` when `len(matching_records) != 1`, which causes all seven groups to be missing. This is documented in the implementation artifact as conservative. Acceptable for v1; should be revisited only if snapshot intentionally supports repeated rows.

3. **`contract_status="partial"` with empty `unsatisfied` falls through to all seven missing.** This would require an internally contradictory snapshot (partial but all groups satisfied), which Slice 4 should not produce. Fail-closed behavior is correct. Not a blocking finding.

4. **`_string_tuple_field` rejects empty strings within tuples.** If a snapshot row contains `["drawdown_stress", ""]`, the entire field returns `None`, triggering all-seven fail-closed. This is strict but correct; empty group ids are not valid.

5. **Real `006597` / `2024` path not validated in this slice.** Unit fixtures are deterministic. Real-path validation is a Slice 6 responsibility per plan.

## Decision

**PASS.** No blocking findings. Implementation satisfies all eight review criteria. Proceed to controller judgment.
