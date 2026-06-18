# Docling Reference Bundle Producer Determinism Contract Plan - 2026-06-17

Gate: `Docling Reference Bundle Producer Determinism Contract Planning Gate`
Role: planning worker only
Status: `HANDOFF_READY_NOT_READY`
Planned next gate type: no-live implementation planning / implementation gate
Release/readiness: `NOT_READY`

## Goal

Define the next gate after the accepted comparability diagnostic:

`docs/reviews/docling-reference-bundle-comparability-diagnostic-controller-judgment-20260617.md`

The next gate must stop residual-closure testing from chasing closure counts before the reference-bundle producer is stable. It must specify a deterministic producer contract and evidence shape so future residual-closure re-evidence compares like with like.

This is not a source-truth, baseline, parser, release, or readiness gate. It is a testing-strategy correction gate for candidate-only Docling residual closure.

## Current Accepted Facts

- Accepted diagnostic verdict: `ACCEPT_COMPARABILITY_DIAGNOSTIC_WRAPPER_DRIFT_IDENTIFIED_NOT_READY`.
- Diagnostic matrix: `reports/docling-reference-bundle-comparability-diagnostic/20260617/comparability_matrix.json`.
- Prior accepted residual-closure checkpoint: `13 closed / 4 residual`.
- Current blocked re-evidence checkpoint: `10 closed / 7 residual`.
- Delta: `-3` closed rows.
- Regression rows: `F015`, `S5-F023`, `S6-F035`.
- Target seven: prior `3 / 7` closed; current `2 / 7` closed.
- All four samples show repository load count drift and section inference drift.
- Text span count drift appears in `S1`, `S4`, and `S6`; `S5` has stable text span count but content/context drift.
- The committed JSON artifacts prove wrapper/reference-bundle construction drift before helper semantics.
- The committed JSON artifacts do not expose enough raw cell/text-span payload to identify the exact producer line.
- `candidate_only=true`, `source_truth_status=not_proven`, and `NOT_READY` remain binding.

## Non-goals

- No residual-closure re-evidence retry in this gate.
- No attempt to recover `13 / 4` closure count.
- No Docling baseline promotion.
- No source truth acceptance.
- No parser replacement.
- No full field correctness claim.
- No release, PR, golden, or readiness claim.
- No live/network/provider/LLM/analyze/checklist/golden/readiness/release command.
- No direct PDF/cache/source-helper access.
- No repository object reload unless a separate later gate explicitly authorizes `FundDocumentRepository.load_annual_report(..., force_refresh=False)` with socket guard.
- No control-doc, design-doc, README, source policy, fallback, provider, or production parser behavior change.

## Core Decision

The next executable work should be a narrow no-live implementation gate for deterministic reference-bundle producer instrumentation under:

`fund_agent/fund/documents/candidates/source_truth_residual_closure.py`

The implementation must not make the helper more permissive to increase closure count. It must make the producer input and diagnostic output stable enough that future closure-count changes are interpretable.

The producer contract must answer:

1. What raw reference payload was supplied to the helper?
2. Was it v1 raw legacy input or v2 pre-enriched bundle input?
3. Which deterministic enrichment steps ran?
4. What counts and hashes prove the same sample produced comparable input across runs?
5. Which raw cell/text span candidates existed when a row became `source_body_mismatch` or `semantic_assignment_residual`?
6. Which fields are diagnostic-only and cannot be used as positive source-truth proof?

## Required Producer Contract

### Bundle-level contract

Every `RepositoryReferenceBundle.to_dict()` output used for residual-closure evidence should expose deterministic diagnostics:

- `reference_bundle_schema_version`
- `enrichment_status`
- `reference_generation_status`
- `producer_contract_version`
- `producer_input_mode`: one of `raw_legacy_v1`, `pre_enriched_v2`
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

These fields are diagnostic metadata only. They do not prove source truth, field correctness, baseline qualification, readiness, or parser replacement.

`bundle_content_fingerprint` hash-participating content is limited to this normalized payload:

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
- sorted per-cell `normalized_text_hash` values
- sorted per-text-span `normalized_text_hash` values

Companion metadata must be emitted but must not participate in `bundle_content_fingerprint`:

- `reference_bundle_schema_version`
- `enrichment_status`
- `reference_generation_status`
- `producer_contract_version`
- `diagnostic_payload_available`

The binding producer contract version is:

```python
PRODUCER_CONTRACT_VERSION = "docling_reference_bundle_producer_contract.v1"
```

### Cell-level diagnostic contract

For evidence rows that are evaluated by table-cell matching, the diagnostic output must preserve enough candidate match payload to debug drift without reading PDFs:

- `sample_id`
- `table_id`
- `row_index`
- `column_index`
- `section_id`
- `page_number`
- `row_label_path`
- `column_header_path`
- `table_context`
- `table_family`
- `row_parent_label_path`
- `row_hierarchy_path`
- `row_hierarchy_role`
- `share_class_context`
- `share_class_context_source`
- `period_context`
- `period_context_source`
- `normalized_text_hash`
- `raw_text_excerpt`

`raw_text_excerpt` must be bounded to the first 200 Unicode code points of the normalized text. If the normalized text is longer than 200 code points, the excerpt must be truncated to 200 code points and suffixed with `...`, for a maximum emitted length of 203 code points. It is non-authoritative, exists only to debug candidate-wrapper drift, and must not be treated as source truth.

### Text-span diagnostic contract

For evidence rows evaluated by section text, the diagnostic output must preserve:

- `sample_id`
- `section_id`
- `page_number`
- `context_label`
- `heading_path`
- `semantic_context_label`
- `normalized_text_hash`
- `raw_text_excerpt`

`raw_text_excerpt` uses the same 200-code-point bound and `...` truncation convention as the cell-level diagnostic contract.

For `benchmark` and `investment_objective`, the future evidence must be able to distinguish:

- text absent from the bundle;
- text present but labeled as `investment_objective`;
- text present and explicitly labeled as `benchmark`;
- ambiguous label, therefore residual.

`S6-F041` remains residual unless benchmark-labeled context is explicitly proven.

## Required Algorithmic Constraints

The implementation must preserve these fail-closed semantics:

- If bundle diagnostics are missing, mark `diagnostic_payload_available=false`; do not infer comparability.
- If two tables or spans have unstable order, sort by deterministic keys before hashing or reporting.
- Deterministic sort key for cells: `(sample_id, fund_code, document_year, page_number, table_id, row_index, column_index, normalized_text_hash)`.
- Deterministic sort key for text spans: `(sample_id, fund_code, document_year, page_number, section_id, context_label, normalized_text_hash)`.
- `bundle_content_fingerprint` must be computed with `hashlib.sha256(json.dumps(fingerprint_payload, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8")).hexdigest()`, where `fingerprint_payload` contains only the hash-participating content listed in this plan.
- `normalized_text_hash` must be computed with `hashlib.sha256(normalized_text.encode("utf-8")).hexdigest()`.
- `normalized_text` must be produced by converting null input to `""`, replacing all Unicode whitespace runs with a single ASCII space, and stripping leading/trailing whitespace.
- v1 raw legacy bundle input may be enriched in memory, but the output must state `producer_input_mode=raw_legacy_v1`.
- Existing v2 fields must not be overwritten by inference unless the input mode and enrichment notes make that explicit.
- `bounded_neighbor_row_labels` remains diagnostic-only / negative-disambiguation only.
- `allowed_table_families` / `rejected_table_families` continue to take precedence over legacy `required_table_family_any`.
- Missing or conflicting table-family classification remains `unknown`.
- Missing row hierarchy remains `unknown` or `standalone` according to existing deterministic defaults; it must not close aggregate/child residuals.
- `S6-F049` / `S6-F050` cannot close by value equality alone.

## Proposed Implementation Slices

### Slice 1 - Deterministic Diagnostic Models

Target file:

- `fund_agent/fund/documents/candidates/source_truth_residual_closure.py`

Implementation:

- Add immutable candidate-only diagnostic dataclasses if needed, or extend existing `to_dict()` output with deterministic diagnostics.
- Add the binding module-level producer contract version constant: `PRODUCER_CONTRACT_VERSION = "docling_reference_bundle_producer_contract.v1"`.
- Add stable hash helpers for normalized cell/text-span diagnostic payloads.
- Keep all new helpers file-read free, repository-free, source-helper-free, and candidate-only.

Validation:

- Unit tests prove fingerprints are stable under input tuple order variations after deterministic sorting.
- Unit tests prove raw-text excerpts are bounded.
- Unit tests prove missing diagnostics do not imply comparability.

### Slice 2 - Bundle Diagnostic Summary

Target file:

- `fund_agent/fund/documents/candidates/source_truth_residual_closure.py`

Implementation:

- Add bundle-level count summaries for cells, text spans, tables, sections, table families, row hierarchy roles, and text semantic contexts.
- Ensure summaries are generated after enrichment and explicitly record whether input was legacy v1 or v2.
- Preserve existing closure behavior; no rule should become more permissive.

Validation:

- Unit tests build two semantically identical bundles with different object ordering and assert identical diagnostic summaries and fingerprints.
- Unit tests mutate one section/table/text-span field and assert the fingerprint changes.

### Slice 3 - Row-level Diagnostic Payload for Drift Analysis

Target file:

- `fund_agent/fund/documents/candidates/source_truth_residual_closure.py`

Implementation:

- Add optional diagnostic payload to `ResidualClosureResultRow.to_dict()` for candidate matches considered by source/fund-layer evaluation.
- For closed rows, include selected matched diagnostic payload.
- For `source_body_mismatch`, include bounded candidate-search diagnostics if available without repository reload.
- For `semantic_assignment_residual`, include bounded considered-match diagnostics with rule-rejection categories.
- Do not include full raw annual-report body or unbounded table/text payload.

Validation:

- Unit tests for `F015`, `S5-F023`, `S6-F035`, and `S6-F041` style rows prove diagnostics distinguish:
  - source text absent;
  - source text present but semantic label rejected;
  - row hierarchy unknown;
  - benchmark label absent.

## Future Evidence-Artifact Contract Requirements

This section is not an implementation slice.

Controller check found no committed standalone evidence wrapper under:

- `scripts`
- `fund_agent/fund/documents`
- `tests/fund/documents`

Therefore the current implementation handoff must not attempt to update a wrapper script, create a production CLI, or add a new evidence command. No new production CLI is authorized in this plan.

Future evidence-artifact requirements:

- Future residual-closure evidence must write producer diagnostics into the matrix JSON before reporting closure deltas.
- Evidence reports must compare `bundle_content_fingerprint` before interpreting closure counts.
- If fingerprints/count summaries differ, the evidence verdict must be blocked as non-comparable rather than treated as helper regression or improvement.
- Future matrix JSON must contain `producer_contract_version`, bundle diagnostics, row diagnostics, `candidate_only=true`, and `source_truth_status=not_proven`.

Future evidence review validation:

- Review the future evidence artifact directly; do not infer diagnostics from closure-count movement.
- Verify `producer_contract_version` equals `docling_reference_bundle_producer_contract.v1`.
- Verify every sample has bundle diagnostics and every row has row diagnostics when `diagnostic_payload_available=true`.
- Verify missing diagnostics block comparability rather than supporting a helper regression/improvement claim.

## Test Strategy

The next gate should reduce, not expand, test scope.

Target source file:

- `fund_agent/fund/documents/candidates/source_truth_residual_closure.py`

Target test file:

- `tests/fund/documents/test_docling_source_truth_residual_closure.py`

Future implementation validation commands:

```bash
uv run pytest tests/fund/documents/test_docling_source_truth_residual_closure.py -q
uv run ruff check fund_agent/fund/documents/candidates/source_truth_residual_closure.py tests/fund/documents/test_docling_source_truth_residual_closure.py
git diff --check -- fund_agent/fund/documents/candidates/source_truth_residual_closure.py tests/fund/documents/test_docling_source_truth_residual_closure.py
```

Required tests:

1. Determinism tests:
   - same logical bundle, different input order -> same fingerprint;
   - changed section inference/table family/text span -> different fingerprint.
   - SHA256 fingerprint output is a 64-character lowercase hex digest from the specified JSON serialization.
2. Boundary tests:
   - no file reads, no repository calls, no source-helper calls from new helpers;
   - `candidate_only`, `source_truth_status=not_proven`, `NOT_READY` flags preserved in output.
   - `raw_text_excerpt` emits at most 203 code points when truncation suffix is present.
3. Diagnostic sufficiency tests:
   - `source_body_mismatch` exposes enough bounded diagnostics to identify text absence vs missing payload;
   - `semantic_assignment_residual` exposes enough bounded diagnostics to identify semantic-rule rejection category.
4. Regression guard tests:
   - `S6-F041` does not close on investment-objective text;
   - `S6-F049` / `S6-F050` do not close by value equality without hierarchy;
   - ambiguous table family remains residual.

Not required:

- More sample expansion.
- More live evidence.
- Full parser benchmark.
- Golden/readiness tests.
- Source truth promotion.

## Future Evidence Gate After Implementation

After implementation and code review, the next evidence gate should be:

`Docling Reference Bundle Producer Determinism No-live Evidence Gate`

Allowed evidence write set:

- `reports/docling-reference-bundle-producer-determinism/20260617/producer_determinism_matrix.json`
- `docs/reviews/docling-reference-bundle-producer-determinism-evidence-20260617.md`

Expected evidence:

- same input bundle serialized twice yields same fingerprint;
- controlled field perturbation yields changed fingerprint;
- prior/current residual-closure matrices are not reinterpreted until producer diagnostics exist;
- current `10 / 7` remains valid blocked evidence, not successful re-evidence.

Expected verdict tokens:

- `PRODUCER_DETERMINISM_EVIDENCE_ACCEPTED_NOT_READY`
- `PRODUCER_DETERMINISM_EVIDENCE_BLOCKED_NOT_READY`
- `PRODUCER_DIAGNOSTIC_PAYLOAD_INSUFFICIENT_NOT_READY`

## Stop Conditions

Stop and return to controller if:

- implementation requires repository reload, direct PDF/cache/source-helper access, or live/network.
- exact producer-line root cause is requested before the diagnostic payload exists.
- implementation would change residual closure semantics instead of adding deterministic diagnostics.
- implementation would make rules more permissive to recover closure count.
- any test or evidence tries to claim source truth, parser replacement, Docling baseline, full correctness, golden readiness, release readiness, or PR readiness.

## Review Gates

1. Plan review:
   - verify this plan addresses wrapper/reference-bundle construction drift rather than helper closure count;
   - verify it is code-generation-ready;
   - verify no source truth/readiness/parser claims.
2. Implementation review:
   - verify new diagnostics are deterministic and bounded;
   - verify closure semantics are unchanged except diagnostic payload;
   - verify no direct file/repository/source-helper access was added.
3. Determinism evidence review:
   - verify fingerprints/count summaries support comparability;
   - verify future residual-closure evidence can fail closed on non-comparable producer input.

## Completion Report Format

Future implementation worker must report:

- files changed;
- producer contract version;
- whether closure semantics changed;
- diagnostic payload fields added;
- tests run and pass/fail;
- boundary confirmation:
  - `candidate_only=true`;
  - `source_truth_status=not_proven`;
  - `NOT_READY`;
  - no source truth acceptance;
  - no baseline promotion;
  - no parser replacement;
  - no release/readiness/PR/golden claim.

## Final Verdict

`HANDOFF_READY_NOT_READY`

This plan routes the next work to deterministic producer instrumentation and comparable evidence. It explicitly blocks further residual-closure re-evidence until producer comparability is proven.
