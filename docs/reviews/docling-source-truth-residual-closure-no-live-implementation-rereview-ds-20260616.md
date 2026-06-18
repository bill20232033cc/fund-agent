# Docling Source-truth Residual Closure No-live Implementation Re-review (AgentDS) - 2026-06-16

Gate: `Docling Source-truth Residual Closure No-live Implementation Gate`
Role: re-review worker only
Reviewer: AgentDS
Prior reviews: MiMo (PASS_WITH_FINDINGS), DS (PASS_WITH_FINDINGS)
Fix evidence: `docs/reviews/docling-source-truth-residual-closure-no-live-implementation-fix-evidence-20260616.md`

## 1. Fix Verification

### 1.1 MiMo F3 — unused imports `field` and `Any` removed

**VERIFIED.** `source_truth_residual_closure.py` line 15 imports `dataclass` only (no `field`), line 16 imports `Literal` only (no `Any`). No other unused imports found.

### 1.2 MiMo F2 — `manager_holding_range_A` test added

**VERIFIED.** `test_manager_holding_range_a_requires_fund_share_class_label` (line 430) exercises the A share-class fund-manager holding range rule with `share_class_context="A"`. It confirms that a `beta` column header (arbitrary Latin word) is rejected while `混合A` (fund share class label) is accepted. Passes.

### 1.3 DS F1 — numeric decimal normalization tightened

**VERIFIED.** `_normalize_for_match` (lines 1321–1346) now preserves `.` when it appears between two digits (decimal separator), while still stripping other punctuation and whitespace. `149698325.51` normalizes to `149698325.51`, and `1496.9832551` normalizes to `1496.9832551` — they are no longer collapsed to the same string. Thousand-separator commas are still removed.

Tests:
- `test_decimal_separator_placement_is_preserved_during_value_match` — asserts `149,698,325.51` → `149698325.51` and the two dot-placement variants are NOT equal.
- `test_decimal_placement_difference_does_not_close_source_body_match` — end-to-end test: equity value `149698325.51` against a reference cell with `1496.9832551` produces `source_body_mismatch`.

Both pass.

### 1.4 DS F2 — short share-class matching tightened

**VERIFIED.** `_ends_with_fund_share_class_label` (lines 1298–1318) now requires the character immediately before the share-class suffix to be a CJK character (`一`–`鿿`). Arbitrary Latin words ending in `a`/`c` (e.g., `beta`, `alpha`, `clinic`) are rejected because the preceding character is ASCII.

Accepted labels: `A`, `A类`, `混合A`, `债券A`, `C`, `C类` — all verified by `test_share_class_context_accepts_fund_share_labels` (6 parametrized cases). Rejected labels: `beta`, `alpha`, `clinic` — verified by `test_share_class_context_rejects_arbitrary_latin_suffix_words` (3 parametrized cases). All pass.

### 1.5 DS F3 — `locator_context_conflict` test added

**VERIFIED.** `test_locator_context_conflict_blocks_locator_layer` (line 526) uses `fund_code` (requires `§2`) with `section_id="§8"`. Asserts `blocked_locator_unavailable` disposition and `locator_context_conflict` processed status. Passes.

### 1.6 DS F4 — `blocked_rule_missing` test added

**VERIFIED.** `test_unknown_field_name_returns_blocked_rule_missing` (line 536) uses field name `unknown_field` not present in `FIELD_RULES`. Asserts `blocked_rule_missing` disposition and `semantic_rule_missing` fund status. Passes.

### 1.7 DS F5 — invalid `source_kind`/`evidence_anchor_source_kind` guard tested

**VERIFIED.** `test_evidence_anchor_source_kind_guard_rejects_non_annual_report` (line 609) parametrizes both `source_kind: "docling_pdf_candidate"` and `evidence_anchor_source_kind: "docling_pdf_candidate"`. Both produce `blocked_candidate_metadata_violation`. Passes.

### 1.8 MiMo F1 — `candidate_documents` parameter retained intentionally

**ACKNOWLEDGED.** The parameter is documented and retained per accepted plan API for future document-level candidate guards. Current behavior is row-level only. This is a design decision, not a defect.

## 2. Re-review Focus Areas

### 2.1 Numeric decimal normalization — no false positives

Confirmed. The delimiter-aware normalization in `_normalize_for_match` preserves dots between digits and strips everything else. Values differing only by decimal placement no longer normalize to the same string.

### 2.2 Short A/C share-class matching — Latin words rejected, fund labels accepted

Confirmed. The CJK-prefix guard in `_ends_with_fund_share_class_label` correctly distinguishes Chinese fund share-class labels (`混合A`, `债券A`) from arbitrary Latin words (`beta`, `alpha`, `clinic`).

### 2.3 No production surface changes

**VERIFIED.** Only new files under `fund_agent/fund/documents/candidates/` and `tests/fund/documents/`. No tracked files modified. No imports of `FundDocumentRepository`, `EvidenceAnchor`, `load_annual_report`, source helpers, file I/O, or network libraries. Helper is pure-candidate-only.

### 2.4 NOT_READY preserved

**VERIFIED.** Fix evidence states `NOT_READY` and explicitly denies baseline qualification, parser replacement, source-truth proof, full field correctness, release readiness, and PR readiness. All six non-proof guard flags remain `True`. ResidualClosureResultRow carries `source_truth_status = "not_proven"` and `candidate_only = True`.

## 3. Validation

```
uv run pytest tests/fund/documents/test_docling_source_truth_residual_closure.py
→ 29 passed in 0.55s

git diff --check
→ clean (no output)
```

## 4. Test Inventory (post-fix)

| # | Test | Origin |
|---|------|--------|
| 1 | test_identity_code_disambiguates_main_code_from_trading_code | original |
| 2 | test_identity_name_closes_only_on_labeled_profile_row | original |
| 3 | test_manager_and_custodian_close_on_labeled_profile_rows | original |
| 4 | test_portfolio_parent_child_split_uses_row_label_not_value_only | original |
| 5 | test_fixed_income_rejects_fair_value_hierarchy_and_accepts_portfolio_row | original |
| 6 | test_benchmark_guard_keeps_investment_objective_context_residual | original |
| 7 | test_investment_objective_without_same_source_body_stays_mismatch | original |
| 8 | test_unresolved_expense_duplicate_remains_semantic_equivalent_residual | original |
| 9 | test_manager_holding_range_a_requires_fund_share_class_label | fix (MiMo F2) |
| 10–15 | test_share_class_context_accepts_fund_share_labels (6 cases) | fix (DS F2) |
| 16–18 | test_share_class_context_rejects_arbitrary_latin_suffix_words (3 cases) | fix (DS F2) |
| 19 | test_decimal_separator_placement_is_preserved_during_value_match | fix (DS F1) |
| 20 | test_decimal_placement_difference_does_not_close_source_body_match | fix (DS F1) |
| 21 | test_locator_context_conflict_blocks_locator_layer | fix (DS F3) |
| 22 | test_unknown_field_name_returns_blocked_rule_missing | fix (DS F4) |
| 23 | test_boundary_fields_keep_repository_processor_and_anchor_kind_separate | original |
| 24 | test_output_guard_flags_are_preserved | original |
| 25 | test_candidate_boundary_guard_rejects_truth_claims | original |
| 26–27 | test_evidence_anchor_source_kind_guard_rejects_non_annual_report (2 cases) | fix (DS F5) |
| 28 | test_pure_helper_boundary_does_not_read_or_call_repository | original |
| 29 | test_missing_reference_bundle_blocks_reference_layer | original |

All 29 tests pass.

## 5. Conclusion

```text
PASS
```

All eight findings from the two prior reviews (MiMo F1–F3, DS F1–F5) are resolved: F1 (unused imports) removed, F2 (missing test) added, F3 (decimal collapse) patched with delimiter-aware normalization, F4 (Latin word over-match) patched with CJK-prefix guard, F5–F7 (test coverage gaps) filled with dedicated tests, F8 (intentional API reservation) acknowledged.

No new findings. No production surface changes. No forbidden imports. No readiness/baseline/parser-replacement claims. NOT_READY preserved. All 29 tests pass. git diff clean.
