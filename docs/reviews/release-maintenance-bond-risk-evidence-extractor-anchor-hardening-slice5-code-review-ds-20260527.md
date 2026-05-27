# Bond Risk Evidence Extractor / Anchor Hardening Slice 5 Code Review (DS)

> Date: 2026-05-27
> Work unit: `bond risk evidence extractor / anchor hardening design gate`
> Role: code review worker (DS)
> Gate: Slice 5 score applicability and P1 registration
> Decision: PASS

## Self-Check

- Role: code review worker only. No implementation, edit, commit, push, PR, approve, merge, mark ready, or golden promotion.
- Scope: `fund_agent/fund/extraction_score.py` and `tests/fund/test_extraction_score.py`.
- Read: AGENTS.md, plan (Slice 5), Slice 4 controller judgment, Slice 5 implementation artifact.
- Source of truth for contract: plan Slice 5 invariants and review criteria list.

## Validation Commands Re-Run

| Command | Result |
|---|---|
| `uv run pytest tests/fund/test_extraction_score.py -q` | 54 passed in 0.58s |
| `uv run ruff check fund_agent/fund/extraction_score.py tests/fund/test_extraction_score.py` | All checks passed! |

## Findings by Review Criterion

### Criterion 1: bond_risk_evidence is P1 and complete evidence gets 100% coverage/traceability without issue

**PASS.** `FIELD_PRIORITY_BY_NAME` registers `"bond_risk_evidence": "P1"` at line 55. `test_field_priority_includes_bond_risk_evidence_as_p1` asserts the registration. `test_complete_bond_risk_evidence_record_scores_p1_pass_without_issue` verifies: P1 priority, coverage_rate=1.0, traceability_rate=1.0, status=STATUS_PASS, no bond_risk_evidence_missing issue, and replacement_issue_ids=(). When `contract_status="satisfied"` + all seven groups satisfied + `anchor_present=True`, `_bond_risk_unsatisfied_groups` returns `()` → `missing_groups` is falsy → `derive_score_applicability_issues` emits no issue.

### Criterion 2: Missing/absent/malformed/missing-status/contract_status missing/anchorless evidence remains baseline_blocking

**PASS.** Five fail-closed paths verified:

| Condition | Mechanism | Test |
|---|---|---|
| Record absent (no bond_risk_evidence row) | `_bond_risk_evidence_record_for_fund` → None → all seven | `test_bond_fund_excludes_equity_holdings_with_replacement_issue` |
| anchor_present=False | `_bond_risk_unsatisfied_groups` line 1874 → all seven | `test_anchor_missing_accepted_bond_risk_evidence_remains_all_seven_blocking` |
| Malformed structured groups (string instead of list) | `_string_tuple_field` → None → `_bond_risk_structured_groups` → None → all seven | `test_malformed_bond_risk_evidence_record_remains_all_seven_blocking` |
| contract_status missing/None | Not in allowed set (line 1877-1882) → all seven | `test_missing_contract_status_bond_risk_evidence_remains_all_seven_blocking` |
| contract_status="missing" | Early return at line 1884 → all seven | Covered by all-seven path in test above |

All paths converge on `_bond_risk_evidence_missing_issue` which hardcodes `baseline_blocking=True` (line 1798).

### Criterion 3: Weak/ambiguous groups remain unsatisfied and dynamic missing_evidence_groups is exact

**PASS.** `_bond_risk_unsatisfied_groups` computes `unsatisfied = explicit_unsatisfied | absent_from_satisfied` (line 1896-1898), where `explicit_unsatisfied = {*missing, *weak, *ambiguous}`. Weak and ambiguous groups propagate into unsatisfied via the union. `test_weak_drawdown` verifies only `drawdown_stress` in missing. `test_ambiguous_redemption` verifies only `redemption_share_pressure` in missing. `test_partial_mixed` verifies three unsatisfied (leverage + drawdown + redemption) with all seven required.

### Criterion 4: required_evidence_groups always full ordered seven groups

**PASS.** `_bond_risk_evidence_missing_issue` always sets `required_evidence_groups = group_ids` where `group_ids` is derived from `BOND_RISK_EVIDENCE_GROUPS` (line 1775-1776). `missing_evidence_groups` is a separate parameter. `test_partial_bond_risk_evidence_keeps_required_groups_full_and_missing_dynamic` explicitly asserts `issue.required_evidence_groups == _BOND_RISK_GROUP_IDS` even when only three groups are missing.

### Criterion 5: Score consumes Slice 4 structured fields only, no note parsing

**PASS.** `_bond_risk_unsatisfied_groups` reads only: `bond_risk_contract_status`, `bond_risk_satisfied_groups`, `bond_risk_missing_groups`, `bond_risk_weak_groups`, `bond_risk_ambiguous_groups`. It never reads `note`. `test_bond_risk_score_does_not_parse_note_for_satisfaction` proves that `note="contract_status=satisfied"` is ignored when structured `contract_status="missing"`.

### Criterion 6: Non-bond and unknown/conflicting fund types remain unaffected/fail-closed

**PASS.** Three layers of protection:

1. `derive_score_applicability_issues` gates on `classified_fund_type == BOND_FUND_TYPE` (line 917) — non-bond never enters bond issue logic.
2. `_is_non_applicable_bond_risk_evidence_record_for_type` returns `True` for non-`bond_fund` — bond_risk_evidence records are filtered from scoring denominators for non-bond funds via `_scorable_records`.
3. Unknown/conflicting types (`classified_fund_type=None` or empty) cause `_is_non_applicable_bond_risk_evidence_record_for_type` to return `True` (since `None != "bond_fund"`), excluding the field from scoring.

No fund type inference from bond_risk_evidence occurs anywhere. `test_non_bond_fund_ignores_bond_risk_evidence_record` and `test_unknown_or_conflicted_fund_type_keeps_holdings_fail_closed` provide coverage.

### Criterion 7: FQ0-FQ6, quality_gate, snapshot, data_extractor, golden fixtures and source/PDF/cache access are untouched

**PASS.** extraction_score.py has no direct PDF/cache/source access. No FQ0-FQ6 threshold or severity constants were changed. `FIELD_PRIORITY_BY_NAME` was additively extended with `"bond_risk_evidence": "P1"`; existing entries are unchanged. Snapshot and data_extractor files are not in the changed file set. Quality gate is downstream of score and will be validated in Slice 6.

### Criterion 8: Tests cover all planned paths and do not create false pass by weakening denominator semantics

**PASS.** 54 tests pass (was 54 before Slice 5 changes per implementation artifact). The Slice 5 tests add 12 new bond-risk-specific test functions without weakening existing tests. All existing tests continue to pass. No existing assertions were modified or removed.

Test coverage of plan-required paths: complete record (no issue), weak group (partial issue), ambiguous group (partial issue), missing record (all-seven issue), malformed (all-seven), missing status (all-seven), anchorless (all-seven), non-bond (ignored), note-not-parsed, P1 registration, issue ID deterministic.

Denominator semantics: `required_evidence_groups` is always the contract-level invariant of seven groups. `missing_evidence_groups` is dynamic but never shrinks below actual unsatisfied count. `baseline_blocking` is hardcoded `True` in every emitted issue. No path allows a partial record to pass without issue.

## Residuals

1. **`value_present` not gated in `_bond_risk_unsatisfied_groups`**: The function does not check `value_present` before evaluating structured group fields. A Slice 4 record with `value_present=False`, `anchor_present=True`, and `contract_status="satisfied"` (internally inconsistent) would be treated as satisfied by Slice 5. Severity: low. Mitigation: Slice 4 contract ties `value_present` to `contract_status != "missing"`; this inconsistency requires upstream Slice 4 corruption and would be caught in Slice 4 validation.

2. **No per-group anchor validation in score**: Slice 5 validates `anchor_present` at field level only. A Slice 4 record could mark individual groups as "satisfied" without per-group anchors, and Slice 5 would accept it. Severity: low. Mitigation: per-group anchor validation is a Slice 4 extractor/snapshot contract concern. The implementation artifact documents this limitation. If per-group anchor granularity is needed, it requires additional structured fields in snapshot (one `anchor_present` boolean per group). Not blocking for this gate.

3. **Multiple same-fund same-year bond_risk_evidence rows fail-closed**: `_bond_risk_evidence_record_for_fund` returns `None` when `len(matching_records) != 1`. Duplicate rows → all-seven blocking. Severity: low. Mitigation: conservative; documented in implementation artifact. Snapshot should never produce duplicate rows for this field.

4. **Logic duplication between `derive_score_applicability_issues` and `_fund_field_applicability_decisions`**: Both functions independently compute bond risk evidence status via the same `_bond_risk_evidence_record_for_fund` + `_bond_risk_unsatisfied_groups` pattern. Severity: low. Not a correctness issue — both paths are independently tested. Future refactoring opportunity.

## Verdict

**PASS. No blocking findings.**

All eight review criteria are met. The implementation cleanly registers `bond_risk_evidence` as P1, consumes only Slice 4 structured snapshot fields, preserves fail-closed behavior for all malformed/missing/anchorless cases, correctly gates on exact `bond_fund`, and leaves non-bond/unknown/conflicting fund types unaffected. Tests cover the planned paths without denominator weakening. `ruf` and `pytest` pass cleanly.

Proceed to Slice 6 (real 006597 validation path) with residuals noted above.
