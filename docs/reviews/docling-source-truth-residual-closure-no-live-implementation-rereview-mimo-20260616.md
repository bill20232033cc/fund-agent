# Docling Source-truth Residual Closure No-live Implementation Re-review - 2026-06-16

Gate: `Docling Source-truth Residual Closure No-live Implementation Gate`
Role: re-review worker only
Reviewer: AgentMiMo

## Inputs Reviewed

Prior reviews:
- `docs/reviews/docling-source-truth-residual-closure-no-live-implementation-code-review-mimo-20260616.md`
- `docs/reviews/docling-source-truth-residual-closure-no-live-implementation-code-review-ds-20260616.md`

Fix evidence:
- `docs/reviews/docling-source-truth-residual-closure-no-live-implementation-fix-evidence-20260616.md`

Changed files:
- `fund_agent/fund/documents/candidates/source_truth_residual_closure.py`
- `tests/fund/documents/test_docling_source_truth_residual_closure.py`
- `docs/reviews/docling-source-truth-residual-closure-no-live-implementation-evidence-20260616.md`
- `docs/reviews/docling-source-truth-residual-closure-no-live-implementation-fix-evidence-20260616.md`

## Validation

```text
uv run pytest tests/fund/documents/test_docling_source_truth_residual_closure.py
→ 29 passed in 0.66s

git diff --check
→ (no output, clean)
```

## Fix Verification

### 1. MiMo F3: unused imports removed — PASS

Lines 10–16 of `source_truth_residual_closure.py` import `re`, `Counter`, `Mapping`, `dataclass`, `Literal`. No `field` or `Any` import remains.

### 2. MiMo F2: `manager_holding_range_A` test added — PASS

`test_manager_holding_range_a_requires_fund_share_class_label` (line 430) constructs a row with `field_name="manager_holding_range_A"`, `section_id="§10"`, and two bundle cells: one with `column_header_path=("beta",)` (should reject) and one with `column_header_path=("混合A",)` (should accept). Asserts `closure_disposition == "disambiguated_source_body_match"` and `matched_column_header_path == ["混合A"]`.

### 3. DS F1: decimal normalization no longer creates false positives — PASS

`_normalize_for_match` (lines 1321–1346) now preserves decimal points between digits:

```python
if char in ".．。":
    if previous_char.isdigit() and next_char.isdigit():
        chars.append(".")
    continue
```

Thousand separators (commas between digit groups) are still removed. Test `test_decimal_separator_placement_is_preserved_during_value_match` verifies `"149,698,325.51"` normalizes to `"149698325.51"` and that `"149698325.51" != "1496.9832551"` after normalization. Test `test_decimal_placement_difference_does_not_close_source_body_match` verifies end-to-end that differing decimal placement yields `source_body_mismatch`.

### 4. DS F2: short A/C share-class matching tightened — PASS

`_ends_with_fund_share_class_label` (lines 1298–1318) now requires the character preceding the share-class suffix to be a Chinese character:

```python
previous = prefix[-1]
return "一" <= previous <= "鿿"
```

This rejects arbitrary Latin words ending in `a` or `c` (e.g. `beta`, `alpha`, `clinic`). Fund share-class labels with Chinese prefixes (`混合A`, `债券A`) and bare class labels (`A`, `A类`, `C`, `C类`) remain accepted. Parametrized tests verify both acceptance (6 cases) and rejection (3 cases: `beta`, `alpha`, `clinic`).

### 5. DS F3: `locator_context_conflict` test added — PASS

`test_locator_context_conflict_blocks_locator_layer` (line 526) constructs a row with `field_name="fund_code"` (requires `§2`) but `section_id="§8"`. Asserts `closure_disposition == "blocked_locator_unavailable"` and `processed_layer_status == "locator_context_conflict"`.

### 6. DS F4: `blocked_rule_missing` test added — PASS

`test_unknown_field_name_returns_blocked_rule_missing` (line 536) constructs a row with `field_name="unknown_field"` and empty bundle. Asserts `closure_disposition == "blocked_rule_missing"` and `fund_layer_status == "semantic_rule_missing"`.

### 7. DS F5: invalid `source_kind`/`evidence_anchor_source_kind` guard tested — PASS

`test_evidence_anchor_source_kind_guard_rejects_non_annual_report` (line 609) is parametrized with two cases: `anchor_extra={"source_kind": "docling_pdf_candidate"}` and `anchor_extra={"evidence_anchor_source_kind": "docling_pdf_candidate"}`. Both assert `closure_disposition == "blocked_candidate_metadata_violation"` and `processed_layer_status == "candidate_metadata_violation"`.

## Re-check: No production boundary changes — PASS

- Files are new (untracked), not modifications to existing tracked files. `git log` shows no prior commits for either file.
- `source_truth_residual_closure.py` is under `fund_agent/fund/documents/candidates/`, not re-exported from `fund_agent.fund.documents`.
- No imports of `FundDocumentRepository`, `EvidenceAnchor`, `Docling`, `open`, `Path`, or source helpers.
- No file I/O, network, EID, provider, LLM, or `analyze` calls.
- `candidate_documents` parameter is accepted but unused (retained per accepted plan API); current behavior is row-level candidate metadata guard only.

## Re-check: NOT_READY, no baseline, no parser replacement, no release readiness — PASS

- `SourceTruthResidualClosureMatrix` carries all six non-proof guard flags: `not_baseline_promotion=True`, `not_parser_replacement=True`, `not_release_readiness=True`, `not_full_field_correctness=True`, `not_raw_pdf_bbox_truth=True`, `candidate_only=True`.
- Evidence documents explicitly state `NOT_READY` and claim no baseline qualification, no parser replacement, no release readiness, no PR readiness, and no full field correctness.
- No evidence matrix JSON is generated; deferred to later evidence gate.

## Test Count Delta

| Stage | Tests |
| --- | --- |
| Prior review (MiMo) | 13 |
| Prior review (DS) | 13 |
| After fix | 29 |

New tests: `manager_holding_range_A` (1), share-class acceptance parametric (6), share-class rejection parametric (3), decimal normalization (2), `locator_context_conflict` (1), `blocked_rule_missing` (1), `evidence_anchor_source_kind` guard parametric (2). Total +16.

## Conclusion

```text
PASS
```

All five prior findings (MiMo F2, F3; DS F1–F5) are verified resolved. 29 tests pass. Decimal normalization preserves decimal placement without false-positive collapse. Short A/C share-class matching rejects arbitrary Latin suffix words while retaining Chinese fund label acceptance. No production boundary, readiness, baseline, or parser-replacement changes detected. `NOT_READY` preserved.
