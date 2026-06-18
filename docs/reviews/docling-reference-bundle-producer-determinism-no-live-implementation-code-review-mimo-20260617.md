# Docling Reference Bundle Producer Determinism No-live Implementation Code Review - MiMo - 2026-06-17

Gate: `Docling Reference Bundle Producer Determinism No-live Implementation Gate`
Role: code review worker only
Approved plan: `docs/reviews/docling-reference-bundle-producer-determinism-contract-plan-20260617.md`
Controller acceptance: `docs/reviews/docling-reference-bundle-producer-determinism-contract-plan-acceptance-controller-judgment-20260617.md`
Implementation evidence: `docs/reviews/docling-reference-bundle-producer-determinism-no-live-implementation-evidence-20260617.md`
Verdict: `CODE_REVIEW_PASS_NOT_READY`
Finding count: 0
Release/readiness: `NOT_READY`

## Review Scope

Changed files:

- `fund_agent/fund/documents/candidates/source_truth_residual_closure.py`
- `tests/fund/documents/test_docling_source_truth_residual_closure.py`
- `docs/reviews/docling-reference-bundle-producer-determinism-no-live-implementation-evidence-20260617.md`

## Validation Reproduction

```bash
uv run pytest tests/fund/documents/test_docling_source_truth_residual_closure.py -q
# Result: 89 passed in 0.77s

uv run ruff check fund_agent/fund/documents/candidates/source_truth_residual_closure.py tests/fund/documents/test_docling_source_truth_residual_closure.py
# Result: All checks passed!
```

All 89 tests pass. Ruff check clean.

## Slice 1 - Deterministic Diagnostic Models

### PRODUCER_CONTRACT_VERSION

- `source_truth_residual_closure.py:106`: `PRODUCER_CONTRACT_VERSION = "docling_reference_bundle_producer_contract.v1"` matches plan contract exactly.

### Text Normalization and Hash

- `source_truth_residual_closure.py:1925-1939`: `_diagnostic_normalized_text` converts `None` to `""`, applies `re.sub(r"\s+", " ", text).strip()` to collapse Unicode whitespace runs into single ASCII space with leading/trailing strip. Matches plan contract.
- `source_truth_residual_closure.py:1908-1922`: `_normalized_text_hash` computes `hashlib.sha256(normalized_text.encode("utf-8")).hexdigest()`. Matches plan contract.
- `source_truth_residual_closure.py:1942-1957`: `_raw_text_excerpt` truncates at `_RAW_TEXT_EXCERPT_CODEPOINT_LIMIT = 200` code points, appends `..." for max 203 code points. Uses Python string slicing on code points. Matches plan contract.

### Deterministic Sort Keys

- `source_truth_residual_closure.py:1720-1746`: `_cell_sort_key` returns `(sample_id, fund_code, document_year, page_number, table_id, row_index, column_index, normalized_text_hash)`. Matches plan determinism contract.
- `source_truth_residual_closure.py:1749-1774`: `_text_span_sort_key` returns `(sample_id, fund_code, document_year, page_number, section_id, context_label, normalized_text_hash)`. Matches plan determinism contract.

### Helper Boundary

- All new helpers (`_bundle_diagnostic_summary`, `_cell_diagnostic_payload`, `_text_span_diagnostic_payload`, `_sorted_cell_diagnostics`, `_sorted_text_span_diagnostics`, `_sorted_cells`, `_sorted_text_spans`, `_bundle_content_fingerprint`, `_normalized_text_hash`, `_diagnostic_normalized_text`, `_raw_text_excerpt`, `_sorted_counter`, `_producer_input_mode`, `_table_count`, `_section_count`, `_section_inference_reason_counts`, `_diagnostic_section_id`) are file-read free, repository-free, source-helper-free, and candidate-only. Verified by `test_pure_helper_boundary_does_not_read_or_call_repository`.

## Slice 2 - Bundle Diagnostic Summary

### Bundle-level Fields

`_bundle_diagnostic_summary` (line 1095) emits all 12 required bundle-level diagnostic fields:

| Plan field | Implementation | Present |
|---|---|---|
| `producer_contract_version` | Line 1150 | Yes |
| `producer_input_mode` | Line 1151 | Yes |
| `cell_count` | Line 1152 | Yes |
| `text_span_count` | Line 1153 | Yes |
| `table_count` | Line 1154 | Yes |
| `section_count` | Line 1155 | Yes |
| `table_family_counts` | Line 1156 | Yes |
| `section_inference_counts` | Line 1157 | Yes |
| `section_inference_reason_counts` | Line 1158 | Yes |
| `row_hierarchy_role_counts` | Line 1159 | Yes |
| `text_semantic_context_counts` | Line 1160 | Yes |
| `bundle_content_fingerprint` | Line 1161 | Yes |
| `diagnostic_payload_available` | Line 1164 | Yes |

### Fingerprint Computation

- `source_truth_residual_closure.py:1131-1148`: `fingerprint_payload` contains only hash-participating content: `producer_input_mode`, `cell_count`, `text_span_count`, `table_count`, `section_count`, `table_family_counts`, `section_inference_counts`, `section_inference_reason_counts`, `row_hierarchy_role_counts`, `text_semantic_context_counts`, `cell_normalized_text_hashes`, `text_span_normalized_text_hashes`. Companion metadata (`reference_bundle_schema_version`, `enrichment_status`, `reference_generation_status`, `producer_contract_version`, `diagnostic_payload_available`) is excluded from fingerprint. Matches plan.
- `source_truth_residual_closure.py:1886-1905`: `_bundle_content_fingerprint` uses `hashlib.sha256(json.dumps(fingerprint_payload, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8")).hexdigest()`. Matches plan SHA256 serialization.

### Fingerprint Stability Tests

- `test_bundle_content_fingerprint_is_stable_under_reference_order_variation`: Two bundles with different cell/span ordering produce identical fingerprints. Verified.
- `test_bundle_content_fingerprint_changes_when_hash_participating_content_changes`: Mutated cell value changes fingerprint; companion metadata change does not. Verified.

## Slice 3 - Row-level Diagnostic Payload

### Row-level Fields

- `source_truth_residual_closure.py:496`: `diagnostic_payload: Mapping[str, object] | None = None` field added to `ResidualClosureResultRow`.
- `source_truth_residual_closure.py:511`: `diagnostic_payload_available` derived from `self.diagnostic_payload is not None`.
- `source_truth_residual_closure.py:534-537`: Serialized as `diagnostic_payload_available` (bool) and `diagnostic_payload` (dict or null).

### Diagnostic Kinds

- `_selected_match_diagnostic_payload` (line 1168): For closed rows, emits `diagnostic_kind=selected_reference_match` with `normalized_candidate_hash` and `selected_reference_diagnostic`.
- `_source_absent_diagnostic_payload` (line 1192): For `source_body_mismatch`, emits `diagnostic_kind=candidate_search_no_source_match` with `candidate_search_diagnostics` bounded by `_ROW_DIAGNOSTIC_CANDIDATE_LIMIT = 20`.
- `_semantic_residual_diagnostic_payload` (line 1218): For `semantic_assignment_residual`, emits `diagnostic_kind=semantic_assignment_considered_matches` with `considered_match_diagnostics` containing `rejection_categories`.

### Cell/Span Diagnostic Fields

- Cell diagnostic payload (line 1540) includes: `reference_kind`, `sample_id`, `table_id`, `row_index`, `column_index`, `section_id`, `page_number`, `row_label_path`, `column_header_path`, `table_context`, `table_family`, `row_parent_label_path`, `row_hierarchy_path`, `row_hierarchy_role`, `share_class_context`, `share_class_context_source`, `period_context`, `period_context_source`, `normalized_text_hash`, `raw_text_excerpt`. Matches plan.
- Text-span diagnostic payload (line 1582) includes: `reference_kind`, `sample_id`, `section_id`, `page_number`, `context_label`, `heading_path`, `semantic_context_label`, `normalized_text_hash`, `raw_text_excerpt`. Matches plan.

### Diagnostic Sufficiency Tests

- `test_s5_f023_source_absent_row_emits_bounded_search_diagnostics`: `source_body_mismatch` exposes `candidate_search_diagnostics` with bounded text-span payload.
- `test_s6_f035_style_unknown_hierarchy_emits_row_diagnostic_without_closure`: `semantic_assignment_residual` exposes `required_row_hierarchy_role_absent` rejection category.
- `test_s6_f041_investment_objective_match_emits_benchmark_label_absent_diagnostic`: `S6-F041` exposes `required_text_semantic_context_absent` rejection category with `semantic_context_label` and `context_label` in reference diagnostic.
- `test_f015_semantic_residual_emits_share_and_period_rejection_diagnostics`: `F015` exposes `share_class_context_mismatch`, `period_context_mismatch`, `rejected_period_context` categories.

## Closure Semantics Verification

### S6-F041 Regression Guard

- `test_benchmark_guard_keeps_investment_objective_context_residual`: Investment-objective text does not close benchmark field. Closure disposition = `semantic_assignment_residual`. Verified.
- `test_s6_f041_investment_objective_match_emits_benchmark_label_absent_diagnostic`: Investment-objective text match emits `required_text_semantic_context_absent` rejection. Verified.
- `test_benchmark_closes_only_with_benchmark_semantic_label`: Only `benchmark` semantic context closes benchmark field. Verified.

### S6-F049/S6-F050 Regression Guard

- `test_identical_portfolio_values_remain_residual_without_proven_hierarchy`: Same-value equity/stock cells without proven hierarchy both remain `semantic_assignment_residual`. Verified.
- `test_equity_amount_closes_only_aggregate_row_not_stock_child_or_detail`: Equity closes only aggregate row, not child or detail. Verified.
- `test_stock_amount_closes_only_child_stock_row_under_equity_parent`: Stock closes only child row under equity parent. Verified.

### FIELD_RULES Not Relaxed

- `source_truth_residual_closure.py:613-729`: All FIELD_RULES preserved without relaxation. `_match_satisfies_rule` (line 966) not made more permissive. Verified.

### Missing Bundle Diagnostics

- `test_missing_bundle_diagnostics_do_not_infer_comparability`: When `reference_generation_status` is `blocked_reference_unavailable`, `diagnostic_payload_available=False` and `bundle_content_fingerprint=None`. Row-level `diagnostic_payload` is `None`. Closure disposition = `blocked_reference_unavailable`. Verified.

## Boundary Confirmation

- `candidate_only=true`: Preserved in `ResidualClosureResultRow` (line 493) and `SourceTruthResidualClosureMatrix` (line 553).
- `source_truth_status=not_proven`: Preserved as `Literal["not_proven"]` (line 494).
- `NOT_READY`: Evidence artifact states `NOT_READY`.
- No source truth acceptance implemented.
- No baseline promotion implemented.
- No parser replacement implemented.
- No release/readiness/PR/golden claim.
- No live/network/provider/LLM/analyze/checklist/golden/readiness/release command.
- No direct PDF/cache/source-helper access.
- No repository reload.
- No evidence wrapper or production CLI implemented (explicit non-goal per plan).

## Finding Count

0 findings.

## Self-check

Self-check: pass.

## Verdict

`CODE_REVIEW_PASS_NOT_READY`

The implementation faithfully follows the accepted plan slices 1-3. All deterministic diagnostic models, bundle-level summaries, and row-level diagnostic payloads are implemented exactly per contract. Closure semantics remain unchanged with S6-F041 and S6-F049/S6-F050 remaining fail-closed. Tests cover determinism, boundary, diagnostic sufficiency, and regression guards. No bugs, contract drift, missing tests, type-safety issues, or overbroad changes found.
