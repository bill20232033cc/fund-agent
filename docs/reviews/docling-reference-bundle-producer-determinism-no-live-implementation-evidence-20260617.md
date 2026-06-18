# Docling Reference Bundle Producer Determinism No-live Implementation Evidence - 2026-06-17

Gate: `Docling Reference Bundle Producer Determinism No-live Implementation Gate`
Role: implementation worker only
Approved plan: `docs/reviews/docling-reference-bundle-producer-determinism-contract-plan-20260617.md`
Accepted plan commit: `2c028ec`
Release/readiness: `NOT_READY`

## Allowed Write Set

- `fund_agent/fund/documents/candidates/source_truth_residual_closure.py`
- `tests/fund/documents/test_docling_source_truth_residual_closure.py`
- `docs/reviews/docling-reference-bundle-producer-determinism-no-live-implementation-evidence-20260617.md`

## Changed Files

- `fund_agent/fund/documents/candidates/source_truth_residual_closure.py`
- `tests/fund/documents/test_docling_source_truth_residual_closure.py`
- `docs/reviews/docling-reference-bundle-producer-determinism-no-live-implementation-evidence-20260617.md`

## Implemented Plan Items

1. Slice 1 - deterministic diagnostic models:
   - Added `PRODUCER_CONTRACT_VERSION = "docling_reference_bundle_producer_contract.v1"`.
   - Added deterministic diagnostic normalization, `normalized_text_hash`, bounded `raw_text_excerpt`, and producer sort-key helpers.
   - Kept helpers file-read free, repository-free, source-helper-free, and candidate-only.

2. Slice 2 - bundle diagnostic summary:
   - Added bundle-level `cell_count`, `text_span_count`, `table_count`, `section_count`, `table_family_counts`, `section_inference_counts`, `section_inference_reason_counts`, `row_hierarchy_role_counts`, `text_semantic_context_counts`.
   - Added `producer_input_mode` with `raw_legacy_v1` / `pre_enriched_v2`.
   - Added `bundle_content_fingerprint` using only the accepted normalized payload and the required SHA256 JSON serialization.
   - Companion metadata is emitted but not included in the fingerprint payload.

3. Slice 3 - row-level diagnostic payload:
   - Added `diagnostic_payload_available` and optional `diagnostic_payload` to `ResidualClosureResultRow.to_dict()`.
   - Closed rows and semantic-equivalent duplicate rows include selected matched reference diagnostics.
   - `source_body_mismatch` rows include bounded candidate-search diagnostics from the already loaded bundle.
   - `semantic_assignment_residual` rows include bounded considered-match diagnostics and rejection categories.

## Diagnostic Fields Added

Bundle-level diagnostics:

- `producer_contract_version`
- `producer_input_mode`
- `cell_count`
- `text_span_count`
- `table_count`
- `section_count`
- `table_family_counts`
- `section_inference_counts`
- `section_inference_reason_counts`
- `row_hierarchy_role_counts`
- `text_semantic_context_counts`
- `bundle_content_fingerprint`
- `diagnostic_payload_available`

Row-level diagnostics:

- `diagnostic_payload_available`
- `diagnostic_payload.diagnostic_kind`
- `diagnostic_payload.normalized_candidate_hash`
- `diagnostic_payload.selected_reference_diagnostic`
- `diagnostic_payload.candidate_search_diagnostics`
- `diagnostic_payload.considered_match_diagnostics`
- `diagnostic_payload.considered_match_diagnostics[].rejection_categories`

Reference diagnostic payloads include bounded cell/text-span fields, `normalized_text_hash`, and `raw_text_excerpt`.

## Closure Semantics

Closure semantics changed: no.

- Existing FIELD_RULES were not relaxed.
- `_match_satisfies_rule()` was not made more permissive.
- `S6-F041` remains residual on investment-objective text without benchmark semantic context.
- `S6-F049` / `S6-F050` remain blocked from closing by value equality alone when hierarchy is not proven.
- Missing bundle diagnostics set `diagnostic_payload_available=false` and do not infer comparability.

## Tests And Validation

Command:

```text
uv run pytest tests/fund/documents/test_docling_source_truth_residual_closure.py -q
```

Result: PASS, `89 passed in 0.98s`.

Command:

```text
uv run ruff check fund_agent/fund/documents/candidates/source_truth_residual_closure.py tests/fund/documents/test_docling_source_truth_residual_closure.py
```

Result: PASS, `All checks passed!`.

Command:

```text
git diff --check -- fund_agent/fund/documents/candidates/source_truth_residual_closure.py tests/fund/documents/test_docling_source_truth_residual_closure.py docs/reviews/docling-reference-bundle-producer-determinism-no-live-implementation-evidence-20260617.md
```

Result: PASS.

## Residual Risks / Open Questions

- Bundle `section_inference_counts` and `section_inference_reason_counts` are deterministic diagnostics over already loaded section ids; they do not prove section correctness.
- Row diagnostic payloads are bounded and diagnostic-only; they are not source truth, field correctness proof, or baseline qualification.
- No evidence wrapper, production CLI, live re-evidence, golden promotion, or repository reload was implemented in this slice.

## Boundary Confirmation

- Preserved `candidate_only=true`, `source_truth_status=not_proven`, and `NOT_READY`.
- No source truth acceptance.
- No baseline promotion.
- No parser replacement.
- No full field correctness claim.
- No golden/readiness/release/PR claim.
- No live/network/provider/LLM/analyze/checklist/golden/readiness/release command.
- No direct PDF/cache/source-helper access.
- No repository reload.
- No commit, push, PR, release, or closeout action.

## Self-check

Self-check: pass.
