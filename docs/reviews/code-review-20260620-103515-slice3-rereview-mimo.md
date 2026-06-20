# Targeted Re-review: Slice 3 Fix Gate — AgentMiMo

## Metadata

- Work unit: `FundDisclosureDocument manager_profile.v1 Source-truth Direct Extraction`
- Gate: `Slice 3 Fix Re-review Gate`
- Role: AgentMiMo, review-only
- Date: 2026-06-20 10:35:15
- Prior reviews:
  - DS: `docs/reviews/code-review-20260620-101854.md`
  - MiMo: `docs/reviews/code-review-20260620-102521.md`
- Fix evidence: `docs/reviews/funddisclosuredocument-manager-profile-source-truth-extraction-slice3-fix-evidence-20260620.md`
- Implementation evidence: `docs/reviews/funddisclosuredocument-manager-profile-source-truth-extraction-slice3-implementation-evidence-20260620.md`

## Verdict

**TARGETED_REREVIEW_PASS**

## Accepted Finding Status

### Finding 1 (DS medium): `_manager_profile_status` must not return `accepted` when any ambiguity gap exists

**Status: 已修复**

Code evidence (`fund_agent/fund/processors/fund_disclosure_processor.py:2508`):

```python
if all(top_level in value for top_level in _MANAGER_PROFILE_REQUIRED_TOP_LEVEL) and not ambiguous_paths:
    return "accepted"
```

The `_manager_profile_status` function now requires **both** conditions to return `accepted`:
1. All five top-level values present (`portfolio_managers`, `manager_strategy_text`, `turnover_rate`, `manager_alignment`, `holdings_snapshot`)
2. `ambiguous_paths` is empty

When all five values exist but `ambiguous_paths` is non-empty, the function falls through to `return "partial"`.

Test evidence (`test_manager_profile_source_truth_full_value_with_internal_ambiguity_is_partial`, line 3720):
- Constructs all five top-level values with a conflicting holdings row causing ambiguity
- Asserts `family.status == "partial"` (not `accepted`)
- Asserts `family.extraction_mode == "direct"`
- Asserts `family.candidate_evidence == ()`
- Asserts `"ambiguous_table_or_locator" in _gap_codes(family)`
- Asserts the specific gap targets `holdings_snapshot.top_holdings`

**Expected final behavior confirmed**: all five top-level values present + internal `ambiguous_paths` → status `partial`, direct mode, ambiguity gap preserved, `candidate_evidence` empty.

### Finding 2 (DS low): `_manager_profile_cell_original_index` must not silently return index 0 when target cell is not in `table.cells`

**Status: 已修复**

Code evidence (`fund_agent/fund/processors/fund_disclosure_processor.py:2175-2195`):

```python
def _manager_profile_cell_original_index(
    table: FundDisclosureTableBlockLike,
    target_cell: FundDisclosureCellLike,
) -> int:
    for cell_index, cell in enumerate(table.cells):
        if cell is target_cell:
            return cell_index
    raise ValueError("target_cell not found in table.cells")
```

The function now raises `ValueError` with an explicit message when the target cell is not found, instead of silently returning `0`.

Test evidence (`test_manager_profile_cell_original_index_raises_for_foreign_cell`, line 3910):
- Creates a table with one cell and a foreign cell not in the table
- Asserts `pytest.raises(ValueError, match="target_cell not found")`
- Confirms the defensive failure is raised

**Expected final behavior confirmed**: defensive `ValueError` raised when target cell is not in `table.cells`, with regression test coverage.

### Finding 3 (DS residual): table-backed `manager_alignment` positive path should be covered if feasible

**Status: 已修复**

Test evidence (`test_manager_profile_source_truth_extracts_table_backed_alignment`, line 3825):
- Constructs a table with label/value split cells for manager and employee holdings
- Tests `manager_holding` extraction from `基金经理持有本基金` label with `100万份以上` value
- Tests `employee_holding` extraction from `基金管理人所有从业人员持有本基金` label with `50万份至100万份` value
- Asserts public shape: `{"manager_holding": "100万份以上", "employee_holding": "50万份至100万份", "judgment": None}`
- Asserts anchor generation with `table_id == "table-alignment"` and row_locator containing `field=manager_alignment.manager_holding`
- Asserts `candidate_evidence == ()`

The test covers:
1. Label/value split extraction from table cells
2. Guard context behavior (label cells provide context for value cells)
3. Public value shape correctness
4. Direct-route candidate evidence suppression
5. Anchor generation

**Expected final behavior confirmed**: table-backed `manager_alignment` positive path is covered with label/value split, guard behavior, and public shape verification.

## Validation Evidence Rerun

### pytest

```text
uv run pytest tests/fund/processors/test_fund_disclosure_processor.py
157 passed in 0.87s
```

### ruff

```text
uv run ruff check fund_agent/fund/processors/fund_disclosure_processor.py tests/fund/processors/test_fund_disclosure_processor.py
All checks passed!
```

### git diff --check

```text
<no output, no whitespace errors>
```

## Scope Boundary Verification

- No unrelated families reviewed as new work
- No live/PDF/FDR/Docling/provider/LLM evidence required
- No parser replacement, EvidenceSourceKind expansion, facade Slice 4, docs sync, readiness, PR, or release required
- Candidate-only/not_proven/NOT_READY semantics preserved
- No code modified, no staging, no commit, no push

## Residual Risks

All residual risks remain as documented in the implementation and fix evidence artifacts:

1. Facade projection for manager-profile FDD source-truth values → Slice 4
2. `docs/design.md` and `fund_agent/fund/README.md` sync → Slice 4
3. Real-report manager-profile field correctness → future evidence gate
4. Broader holdings shapes → future holdings refinement gate
5. Manager alignment judgment → later CHAPTER_CONTRACT / analysis gate

## Stop Confirmation

- Review-only role: no code modified
- No staging, commit, or push
- No next gate action taken
- Artifact written at: `docs/reviews/code-review-20260620-103515-slice3-rereview-mimo.md`
