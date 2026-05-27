# Bond Risk Evidence Extractor / Anchor Hardening Slice 5 Re-Review (DS)

> Date: 2026-05-28
> Role: re-review worker (DS)
> Gate: Slice 5 re-review after accepted-finding fix
> Decision: **PASS**

## Self-Check

- Role: re-review worker only. No implementation, edit, commit, push, PR, approve, merge, mark ready, or golden promotion.
- Scope: `fund_agent/fund/extraction_score.py`, `tests/fund/test_extraction_score.py`.
- Read: AGENTS.md, Slice 5 code review (DS), Slice 5 code review (MiMo), Slice 5 fix artifact.
- Source of truth: the five specific re-review questions in the handoff.

## Validation Commands

| Command | Result |
|---|---|
| `uv run pytest tests/fund/test_extraction_score.py -q` | 55 passed in 0.77s |
| `uv run ruff check fund_agent/fund/extraction_score.py tests/fund/test_extraction_score.py` | All checks passed! |

## Re-Review Questions

### Q1: Is the accepted value_present=false finding fully fixed?

**YES.** `_bond_risk_unsatisfied_groups` at line 1874-1875 now checks `value_present` before any structured field evaluation:

```python
if not _truthy_bool(record.get("value_present")):
    return group_ids
```

This guard is positioned immediately after the `record is None` check and before `anchor_present`, `contract_status`, structured group parsing, and the satisfied-vs-unsatisfied logic. A snapshot row with `value_present=false`, `anchor_present=true`, `contract_status="satisfied"`, and all seven groups listed as satisfied will now hit line 1874 and return all seven group ids as unsatisfied — fail-closed.

### Q2: Does score now fail closed before trusting structured satisfied groups when value_present is false?

**YES.** The execution order in `_bond_risk_unsatisfied_groups` is:

1. Line 1872-1873: `record is None` → all seven (unchanged)
2. Line 1874-1875: `value_present` falsy → all seven **(new fix)**
3. Line 1876-1877: `anchor_present` falsy → all seven (unchanged)
4. Line 1879-1885: `contract_status` missing/unknown → all seven (unchanged)
5. Line 1886-1887: `contract_status == "missing"` → all seven (unchanged)
6. Line 1889-1891: structured groups malformed → all seven (unchanged)
7. Line 1901-1902: satisfied with no unsatisfied → `()` (unchanged)

The `value_present` check fires before structured groups are ever parsed (line 1889) and before the satisfied shortcut (line 1901-1902). No path exists where `value_present=false` can reach the satisfied return.

### Q3: Do the new tests prove baseline_blocking=true and all seven missing groups for this inconsistent row?

**YES.** `test_value_missing_accepted_bond_risk_evidence_remains_all_seven_blocking` (test file line 745-770) constructs the exact inconsistent scenario:

- `value_present=False`
- `anchor_present=True`
- `contract_status="satisfied"`
- `satisfied_groups=_BOND_RISK_GROUP_IDS` (all seven)

And asserts:
- `issue.issue_code == "bond_risk_evidence_missing"`
- `issue.required_evidence_groups == _BOND_RISK_GROUP_IDS` (all seven contract-level)
- `issue.missing_evidence_groups == _BOND_RISK_GROUP_IDS` (all seven missing)
- `issue.baseline_blocking is True`

The test passes and the assertion coverage is exhaustive for the scenario.

### Q4: Did the fix preserve all prior Slice 5 behavior and hard constraints?

**YES.** 55 tests pass (54 pre-fix + 1 new). Verification of unchanged hard constraints:

| Constraint | Mechanism | Verified |
|---|---|---|
| anchor_present guard | Still at line 1876-1877 | `test_anchor_missing_...` passes |
| contract_status guards | Lines 1879-1887 unchanged | `test_missing_contract_status_...` passes |
| malformed guard | Lines 1889-1891 unchanged | `test_malformed_bond_risk_...` passes |
| required_evidence_groups always seven | Line 1775, 1801 unchanged | 4 tests assert `_BOND_RISK_GROUP_IDS` |
| baseline_blocking=True | Line 1798 unchanged | All issue-emitting tests assert True |
| P1 registration | `FIELD_PRIORITY_BY_NAME` unchanged | `test_field_priority_...` passes |
| Non-bond unaffected | Gate on `BOND_FUND_TYPE` unchanged | `test_non_bond_fund_ignores_...` passes |
| No note parsing | No `note` access in score logic | `test_bond_risk_score_does_not_parse_note_...` passes |
| No source/PDF/cache access | Diff scope unchanged | Provenance tests pass |
| Complete evidence → no issue | Satisfied path unchanged | `test_complete_bond_risk_...` passes |

No existing assertion was modified or removed. No existing test behavior changed.

### Q5: Any new blocking findings?

**No.** Review of the fix and surrounding code found zero new blocking findings.

## Residuals (carried forward from original DS review)

1. **No per-group anchor validation**: Slice 5 validates `anchor_present` at field level only. A Slice 4 record could mark individual groups as satisfied without per-group anchors. Severity: low. Mitigation: per-group anchor validation is a Slice 4 extractor/snapshot contract concern.

2. **Multiple same-fund same-year rows fail-closed**: `_bond_risk_evidence_record_for_fund` returns `None` when `len(matching_records) != 1`. Duplicate rows → all-seven blocking. Severity: low. Mitigation: conservative; snapshot should never produce duplicates.

3. **Logic duplication**: `derive_score_applicability_issues` and `_fund_field_applicability_decisions` independently compute bond risk evidence status. Severity: low. No correctness impact. Future refactoring opportunity.

## Verdict

**PASS. No blocking findings.**

The accepted `value_present=false` finding is fully fixed with a minimal, correctly positioned guard at line 1874-1875. The fix preserves all prior Slice 5 behavior, hard constraints, and test coverage. 55 tests pass, ruff clean. Proceed to controller judgment.
