# Targeted Re-review: Slice 3 Fix Gate

## Metadata

- Work unit: `FundDisclosureDocument manager_profile.v1 Source-truth Direct Extraction`
- Gate: `Slice 3 Fix Re-review Gate`
- Role: AgentDS, review-only
- Prior DS review: `code-review-20260620-101854.md`
- Prior MiMo review: `code-review-20260620-102521.md`
- Fix evidence: `funddisclosuredocument-manager-profile-source-truth-extraction-slice3-fix-evidence-20260620.md`
- Re-review artifact: `code-review-20260620-103515-slice3-rereview-ds.md`
- Review mode: targeted re-review — only verify 3 accepted findings; no new discovery

## Validation Commands (rerun)

```text
uv run pytest tests/fund/processors/test_fund_disclosure_processor.py
→ 157 passed in 0.87s

uv run ruff check fund_agent/fund/processors/fund_disclosure_processor.py tests/fund/processors/test_fund_disclosure_processor.py
→ All checks passed!

git diff --check
→ <no output>
```

## Accepted Finding Verification

### Finding 1 (DS MEDIUM): `_manager_profile_status` returns `accepted` when ambiguity gaps exist

**Expected from fix**: signature accepts `ambiguous_paths`, `accepted` only when `not ambiguous_paths`, call site passes it.

**Actual code evidence**:

- `_manager_profile_status` signature (line 2494): `def _manager_profile_status(value: dict[str, object], ambiguous_paths: set[str]) -> str:`
- Accepted gate (line 2508): `if all(top_level in value for top_level in _MANAGER_PROFILE_REQUIRED_TOP_LEVEL) and not ambiguous_paths:`
- Call site (line 1094): `status = _manager_profile_status(value, ambiguous_paths)`

**Test evidence** (`test_manager_profile_source_truth_full_value_with_internal_ambiguity_is_partial`, line 3720):

- Constructs all 5 top-level values: roster (table), strategy (paragraph), turnover (table), alignment (paragraph), holdings (table)
- Holdings table has conflicting rows: same stock code 600000 with different 公允价值 (1,000.00 vs 2,000.00) → internal ambiguity
- Has non-conflicting row 000001 → `holdings_snapshot` top-level key is present in value
- Asserts `set(family.value)` includes all 6 keys (schema_version + 5 top-level)
- Asserts `family.status == "partial"` (not `"accepted"`)
- Asserts `family.extraction_mode == "direct"`
- Asserts `family.candidate_evidence == ()`
- Asserts `"ambiguous_table_or_locator" in _gap_codes(family)`
- Asserts ambiguity gap `source_field_path == "holdings_snapshot.top_holdings"`

**Status: 已修复**

### Finding 2 (DS LOW): `_manager_profile_cell_original_index` silently returns `0` for foreign cell

**Expected from fix**: raise `ValueError` instead of returning a misleading valid index.

**Actual code evidence**:

- Function (line 2175-2195): `for` loop over `table.cells` with `is` identity check; on miss: `raise ValueError("target_cell not found in table.cells")`
- No `return 0` fallback present

**Test evidence** (`test_manager_profile_cell_original_index_raises_for_foreign_cell`, line 3910):

- Creates `table_cell` owned by table, `foreign_cell` with same `table_id` but not in `table.cells`
- Uses `pytest.raises(ValueError, match="target_cell not found")`
- Confirms defensive failure, not silent `cells[0]` return

**Status: 已修复**

### Finding 3 (DS RESIDUAL): table-backed `manager_alignment` positive path coverage

**Expected from fix**: add test covering table/cell-backed alignment with label/value split, guard context, and direct-route candidate suppression.

**Test evidence** (`test_manager_profile_source_truth_extracts_table_backed_alignment`, line 3825):

- Creates a 2-row table with label/value columns: manager holding ("100万份以上") and employee holding ("50万份至100万份")
- Uses label column (column_index=0, "基金经理持有本基金" / "基金管理人所有从业人员持有本基金") and value column (column_index=1)
- Asserts `family.value["manager_alignment"] == {"manager_holding": "100万份以上", "employee_holding": "50万份至100万份", "judgment": None}`
- Asserts anchor uses `table_id="table-alignment"`
- Asserts `family.candidate_evidence == ()` — direct route, no candidate leak
- Confirms label/value split, guard behavior (strong token "基金经理持有本基金" in same row), public value shape, judgment=None

**Status: 已修复**

## Scope Boundary Confirmation

- No new files modified beyond the two accepted files (`fund_disclosure_processor.py`, `test_fund_disclosure_processor.py`)
- No Slice 4 facade regression, docs sync, or other-family extraction
- No `EvidenceSourceKind`, `EvidenceAnchor`, public contract, source provenance schema, or gap taxonomy expansion
- No parser replacement or candidate evidence consumed as source truth
- No `investor_experience.v1`, `current_stage.v1`, `core_risk.v1` extraction attempted
- Three new tests added (fixing 3 accepted findings); 157 total tests pass
- `candidate_evidence=()` preserved on direct-route results

## Finding Status Summary

| Finding | Status |
|---|---|
| DS MEDIUM: `_manager_profile_status` ambiguity gap → `accepted` | 已修复 |
| DS LOW: `_manager_profile_cell_original_index` silent `0` return | 已修复 |
| DS RESIDUAL: table-backed manager_alignment positive path coverage | 已修复 |

## Verdict

**TARGETED_REREVIEW_PASS**

All three accepted findings are fixed with direct code and test evidence. No regressions. Scope boundary intact.
