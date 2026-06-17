# Docling Dedicated Extractor Real-envelope Mismatch Diagnostic Controller Judgment - 2026-06-17

Gate: `Docling Dedicated Extractor Real-envelope Mismatch Diagnostic Evidence Gate`
Role: controller
Accepted plan commit: `dbd77fd`
Status: `DIAGNOSTIC_ACCEPTED_NOT_READY`
Verdict: `ACCEPT_DIAGNOSTIC_ROUTE_TO_SECTION_CONTEXT_REMEDIATION_PLANNING_NOT_READY`
Release/readiness: `NOT_READY`

## Inputs

- Diagnostic plan: `docs/reviews/docling-dedicated-extractor-real-envelope-mismatch-diagnostic-plan-20260617.md`
- Diagnostic evidence: `docs/reviews/docling-dedicated-extractor-real-envelope-mismatch-diagnostic-evidence-20260617.md`
- Diagnostic matrix: `reports/docling-dedicated-extractor-real-envelope-mismatch-diagnostic/20260617/real_envelope_shape_matrix.json`
- Prior field coverage matrix: `reports/docling-dedicated-extractor-candidate-field-no-live-evidence/20260617/template_field_coverage_matrix.json`

## Decision

Accept the diagnostic.

The primary cause of zero candidate-field coverage is classified as:

`section_candidates_exist_but_blocks_unlinked`

The next gate must be section-context remediation planning. Do not proceed to field contract stabilization, row/column label derivation, comparative correctness, production integration, or baseline promotion yet.

## Accepted Facts

- Four runnable current-schema Docling candidate envelopes were inspected.
- All four have section headings.
- All four have tables and text blocks.
- All four have `CandidateTableBlock.section_id=None` for every table.
- All four have `CandidateTextBlock.section_id=None` for every text block.
- All four have `table_family="unknown"` for every table.
- All four have zero non-empty `row_label_path` values.
- All four have zero non-empty `column_header_path` values.
- Many target labels are present in candidate text/table content, so zero extractor coverage is not source absence evidence.
- 74 of 92 field slots are classified as `section_candidates_exist_but_blocks_unlinked`.
- 16 of 92 field slots are classified as `deferred_by_plan`.
- 2 of 92 field slots are classified as `section_id_absent_or_not_projected`.

## Boundary

This judgment does not authorize:

- source-truth acceptance;
- field-correctness claims;
- parser replacement;
- baseline promotion;
- production integration;
- direct PDF/cache/source-helper access;
- live/network/provider/LLM/golden/readiness/release/PR commands.

## Residual Owner

Next gate:

`Docling Dedicated Extractor Section-context Remediation Planning Gate`

Required plan properties:

- candidate-only;
- no production parser replacement;
- no source-truth claim;
- deterministic section-span logic;
- fail-closed behavior for duplicate, unsupported, or ambiguous section headings;
- measurable expected coverage uplift on the same four runnable samples;
- no row/column label derivation in the first slice unless explicitly justified by section-linkage evidence.

## Stop Condition

The baseline path remains blocked until section-context remediation is planned, implemented, reviewed, and re-evidenced.

VERDICT: `ACCEPT_DIAGNOSTIC_ROUTE_TO_SECTION_CONTEXT_REMEDIATION_PLANNING_NOT_READY`
