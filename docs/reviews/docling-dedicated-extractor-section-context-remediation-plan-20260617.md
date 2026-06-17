# Docling Dedicated Extractor Section-context Remediation Plan - 2026-06-17

Gate: `Docling Dedicated Extractor Section-context Remediation Planning Gate`
Role: planning worker
Prior diagnostic commit: `ffce4a9`
Status: `PLAN_READY_FOR_REVIEW_NOT_READY`
Release/readiness: `NOT_READY`

## Goal

Implement the smallest candidate-only remediation that lets the Docling dedicated template-field extractor use deterministic section context for real candidate envelopes whose `CandidateTextBlock.section_id` and `CandidateTableBlock.section_id` are `None`.

## Motivation

The accepted diagnostic found:

- 4 runnable current-schema Docling candidate envelopes;
- 92 target field slots;
- 0 direct extractor hits before remediation;
- 74 field slots primarily blocked because section headings exist but text blocks/tables are not linked to normalized sections;
- all projected table/text block `section_id` values are `None`;
- row/column label paths remain absent and are out of scope for this slice.

The extractor currently calls `_section_allowed(block.section_id, allowed)` directly. On real envelopes, this rejects all text blocks and tables before label matching.

## First-principles Judgment

The extractor should not invent a separate section parser. The repository already has accepted candidate-only section span logic in `fund_agent/fund/documents/candidates/evidence_anchor_mapping.py`, with fail-closed handling for:

- missing section context;
- duplicate section heading;
- unsupported heading number;
- non-monotonic section order;
- cross-section multi-page spans;
- ambiguous heading paths.

Therefore the narrow remediation is to let the template extractor resolve a block's effective section through that accepted candidate mapping path, while preserving candidate-only and `not_proven` status.

## Non-goals

This gate will not:

- modify `representation_projection.py`;
- modify `FundDataExtractor`;
- modify production `EvidenceAnchor` schema;
- derive row/column label paths;
- classify `table_family`;
- change source acquisition or repository behavior;
- generate fresh Docling conversions;
- run live/network/provider/LLM/golden/readiness/release/PR commands;
- compare values with source truth;
- promote baseline, parser replacement, or production integration.

## Allowed Write Set

- `fund_agent/fund/documents/candidates/template_field_extraction.py`
- `tests/fund/documents/test_docling_template_field_extraction.py`
- `docs/reviews/docling-dedicated-extractor-section-context-remediation-implementation-evidence-20260617.md`
- code review / re-review artifacts under `docs/reviews/`
- `reports/docling-dedicated-extractor-section-context-remediation-reevidence/20260617/template_field_coverage_after_section_context.json`
- `docs/reviews/docling-dedicated-extractor-section-context-remediation-reevidence-20260617.md`
- controller judgment artifact for this gate

## Implementation Decisions

### 1. Reuse accepted candidate anchor mapping

In `template_field_extraction.py`, import:

- `CandidateAnchorSchemaFamily`
- `map_candidate_locator_to_anchor_candidate`

Add private helpers:

- `_schema_family_for_document(document) -> CandidateAnchorSchemaFamily`
- `_effective_section_id(document, block, parent_table=None) -> str | None`
- `_section_allowed_for_block(document, block, allowed, parent_table=None) -> bool`

Expected behavior:

- If `block.section_id` is already one of the allowed normalized section IDs, use it directly.
- Otherwise call `map_candidate_locator_to_anchor_candidate(...)`.
- If mapping returns exactly one mapped candidate, use `mapped[0].fields.section_id`.
- If mapping returns blocked or multiple mapped candidates, treat section as unavailable and keep extraction missing.
- Do not surface mapped result as production anchor; use it only as candidate-only section context.

### 2. Schema-family choice

Use current accepted local schema-family convention:

- `S1_full` for sample `S1`;
- `S4_S5_S6_lightweight` for samples `S4`, `S5`, `S6`;
- default to `S4_S5_S6_lightweight` for other samples.

This choice is diagnostic/candidate-only and must not become a public production contract.

### 3. Apply section resolver only to section filters

Replace section checks in these matcher paths:

- `_match_key_value_table_field`
- `_match_text_label_field`
- `_match_performance_field`
- `_match_tracking_error`
- `_match_portfolio_managers`
- `_match_holding_row`

Do not change matching labels, values, row grouping, row/column label derivation, or deferred fields.

### 4. Anchors should report effective section

When a direct field is matched because of resolved section context, emitted `CandidateTemplateFieldAnchor.section_id` should use the effective section ID, not raw `None`.

Add optional `section_id` override to:

- `_anchor_for_cell(...)`
- `_anchor_for_text_block(...)`

The note must remain prefixed with `candidate_only:`.

## Tests

Add focused tests in `tests/fund/documents/test_docling_template_field_extraction.py`:

1. Table with `section_id=None`, page inside a stable `§2` span, and label/value row should extract `basic_identity.fund_name`.
2. Text block with `section_id=None`, page inside a stable `§2` span, and `基金代码：004393` should extract `basic_identity.fund_code`.
3. Duplicate same-page `§2` headings should fail closed and keep the field missing.
4. Existing synthetic tests with explicit section IDs must still pass.

Expected validation:

```text
uv run pytest tests/fund/documents/test_docling_template_field_extraction.py tests/fund/documents/test_docling_evidence_anchor_mapping.py -q
uv run ruff check fund_agent/fund/documents/candidates/template_field_extraction.py tests/fund/documents/test_docling_template_field_extraction.py
git diff --check -- <allowed write set>
```

## Re-evidence

After implementation, rerun the same four runnable candidate envelopes from prior evidence and write:

`reports/docling-dedicated-extractor-section-context-remediation-reevidence/20260617/template_field_coverage_after_section_context.json`

Acceptance signal:

- direct coverage should be greater than 0 if section-context was the blocking cause for key/value/text fields;
- row/column dependent fields may remain missing;
- deferred fields remain missing;
- all outputs remain candidate-only and `NOT_READY`.

If direct coverage remains 0, the implementation must be accepted only as a negative remediation result and route back to diagnostics.

## Residual Risks

Assigned to later row/column label derivation gate:

- performance table fields;
- manager table fields;
- holdings snapshot fields.

Assigned to later table-family gate:

- false-positive control for table-specific extraction.

Assigned to later comparative correctness gate:

- value correctness and source truth.

Assigned to later integration gate:

- production projection and quality gate semantics.

## Completion Report Format

Implementation evidence verdict must be one of:

- `SECTION_CONTEXT_REMEDIATION_IMPLEMENTED_NOT_READY`
- `SECTION_CONTEXT_REMEDIATION_BLOCKED_NOT_READY`

Re-evidence verdict must be one of:

- `SECTION_CONTEXT_REMEDIATION_COVERAGE_UPLIFT_NOT_READY`
- `SECTION_CONTEXT_REMEDIATION_NO_UPLIFT_NOT_READY`

VERDICT: `PLAN_READY_FOR_REVIEW_NOT_READY`
