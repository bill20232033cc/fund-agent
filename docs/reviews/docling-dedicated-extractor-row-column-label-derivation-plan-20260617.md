# Docling Dedicated Extractor Row-column Label Derivation Plan - 2026-06-17

Gate: `Docling Dedicated Extractor Row-column Label Derivation Planning Gate`
Role: planning worker
Status: `PLAN_READY_FOR_REVIEW_NOT_READY`
Release/readiness: `NOT_READY`

## Goal

Implement a candidate-only row/column label derivation slice inside the dedicated Docling template-field extractor.

The immediate purpose is to improve table-semantic template field coverage after section-context remediation, especially fields still blocked by empty `row_label_path` and `column_header_path`.

Success signal:

- existing candidate-only boundary tests still pass;
- synthetic tests prove that empty stored row/column paths can be deterministically derived from header rows and row-leading cells;
- same four current-schema Docling candidate envelopes are re-evidenced against the section-context baseline;
- results remain `candidate_only=true`, `source_truth_status="not_proven"`, and release/readiness remains `NOT_READY`.

## Non-goals / Boundaries

This gate does not authorize:

- source-truth acceptance;
- field correctness claims;
- parser replacement;
- `FundDataExtractor` integration;
- production `EvidenceAnchor` exposure;
- mutation of `CandidateRepresentationDocument`, `CandidateTableBlock`, or `CandidateTableCell`;
- changes to `representation_projection.py`;
- live Docling, PDF, cache, source-helper, network, provider, LLM, golden, release, PR, or readiness commands.

The derived labels are local extractor working context only. They are not a candidate representation schema upgrade.

## Design / Control Alignment

Direct accepted inputs:

- `docs/reviews/docling-dedicated-extractor-real-envelope-mismatch-diagnostic-controller-judgment-20260617.md`
- `docs/reviews/docling-dedicated-extractor-section-context-remediation-controller-judgment-20260617.md`
- `docs/reviews/docling-dedicated-extractor-section-context-remediation-reevidence-20260617.md`

Accepted facts:

- Four runnable current-schema Docling envelopes have tables and text blocks.
- All four had zero non-empty `row_label_path` values and zero non-empty `column_header_path` values.
- Section-context remediation increased direct field coverage from `0 / 92` to `48 / 92`.
- Remaining row/column label dependent fields are still limited.
- All outputs must remain candidate-only and `NOT_READY`.

## First-principles Judgment

The dedicated extractor currently has enough table geometry to derive local matching context:

- rows can be grouped by `CandidateTableCell.row_start`;
- columns can be keyed by `CandidateTableCell.column_start`;
- real Docling envelopes preserve table text even when projected semantic label paths are empty.

The shortest safe route is not to change parser/projection semantics. It is to derive a local table context for the extractor and use it only for matching. This is narrower, reversible, and keeps source-truth proof out of scope.

This is not over-designed because it avoids a public schema change and avoids a generalized table understanding layer. It adds only private helpers needed by the current field matchers.

## Affected Files

Allowed implementation files:

- `fund_agent/fund/documents/candidates/template_field_extraction.py`
- `tests/fund/documents/test_docling_template_field_extraction.py`

Allowed evidence artifacts:

- `docs/reviews/docling-dedicated-extractor-row-column-label-derivation-implementation-evidence-20260617.md`
- `docs/reviews/code-review-*.md`
- `docs/reviews/docling-dedicated-extractor-row-column-label-derivation-code-rereview-20260617.md` if a fix is needed
- `docs/reviews/docling-dedicated-extractor-row-column-label-derivation-reevidence-20260617.md`
- `reports/docling-dedicated-extractor-row-column-label-derivation-reevidence/20260617/template_field_coverage_after_row_column_labels.json`

## Contract / Schema / State Changes

No public contract, schema, or production state-machine changes.

Private implementation contract:

- build table context from existing cell text and geometry;
- never mutate candidate representation objects;
- prefer stored `row_label_path` and `column_header_path` when present;
- derive labels only when a table has deterministic header/row context;
- fail closed when label derivation is absent or ambiguous;
- anchor the original matched cell, not the derived label source cell.

## Implementation Decisions

1. Add private table-context helpers in `template_field_extraction.py`.
   - Represent per-table derived context as private dataclasses or private tuples.
   - Derive column labels from header-like rows whose non-empty cells contain at least two known table-header terms.
   - Map each header cell to its `column_start`.
   - Derive row labels from the first non-empty cell in a row when it is not a numeric value and not a header-only cell.

2. Keep matching fail-closed.
   - Do not infer a label from arbitrary position alone.
   - Do not infer a column label when no header-like row is present.
   - Do not infer a target column label when duplicate or conflicting derived headers make the target column ambiguous.
   - Do not override stored paths.
   - Do not extract from a value cell unless the target column or row context is supported by stored or derived labels.

3. Update only table-semantic matchers.
   - `_match_performance_field` must use derived column labels and derived row labels.
   - `_match_portfolio_managers` must allow derived `姓名` / `任职日期` column labels.
   - `_match_holding_row` must allow derived holding name/value/ratio column labels and row context labels.
   - Existing key/value text and table matching should remain functionally unchanged.

4. Keep diagnostics and proof status unchanged.
   - Do not add readiness claims.
   - Do not interpret coverage uplift as correctness proof.

## Slice

### Slice 1: Local row/column label derivation

Objective:

- make table-semantic matchers work when candidate cells have empty stored label paths but deterministic table text/geometry exists.

Allowed changes:

- add private helper constants/dataclasses/functions in `template_field_extraction.py`;
- update `_match_performance_field`, `_match_portfolio_managers`, `_match_holding_row`, `_find_cell_by_headers_or_labels`, and `_row_contains_any` as needed;
- add focused tests in `tests/fund/documents/test_docling_template_field_extraction.py`.

Expected outcome:

- synthetic empty-path performance table extracts `nav_benchmark_performance.nav_growth_rate` and `nav_benchmark_performance.benchmark_return_rate`;
- synthetic empty-path manager table extracts `portfolio_managers`;
- synthetic empty-path holdings table extracts at least stock top holdings and preserves candidate anchors;
- a table without a deterministic header row remains missing.
- a table with duplicated target performance headers keeps the affected performance field missing instead of taking the first matching column.

Stop condition:

- stop after implementation, tests, code review/fix loop, re-evidence artifact, and accepted local commit;
- do not proceed to source-truth, correctness, baseline promotion, production integration, aggregate deepreview, PR, or release gates without explicit controller decision.

## Tests / Validation

Required local validation:

```text
uv run pytest tests/fund/documents/test_docling_template_field_extraction.py tests/fund/documents/test_docling_evidence_anchor_mapping.py -q
```

Expected:

- all existing tests pass;
- new row/column derivation tests pass.

Required lint:

```text
uv run ruff check fund_agent/fund/documents/candidates/template_field_extraction.py tests/fund/documents/test_docling_template_field_extraction.py
```

Expected:

- `All checks passed!`

Required re-evidence:

- run the same accepted no-live current-schema envelope set used by section-context remediation;
- write `reports/docling-dedicated-extractor-row-column-label-derivation-reevidence/20260617/template_field_coverage_after_row_column_labels.json`;
- compare against `48 / 92` direct slots and `52` candidate anchors.

## Docs Decision

No README update in this planning gate.

If implementation only changes candidate-only internals and tests, README updates are not required. Any later public contract, CLI, production path, or package-level behavior change must trigger docs per `AGENTS.md`.

## Risks / Open Questions

Residual risks:

- Derived labels can improve candidate coverage but cannot prove correctness.
- Some real Docling tables may not expose a clean header row; no-uplift remains a valid outcome.
- Header synonyms may remain incomplete and require a later narrow gate.
- Table family remains `unknown`; this gate does not solve table-family classification.
- Deferred fields remain explicitly missing.

Open questions:

- None blocking for this slice.

## Completion Report Format

Implementation closeout must report:

- changed files;
- new helper behavior;
- tests and lint results;
- real-envelope re-evidence metrics against `48 / 92`;
- remaining residuals and next gate recommendation;
- explicit `NOT_READY` / candidate-only boundary.

VERDICT: `PLAN_READY_FOR_REVIEW_ROW_COLUMN_LABEL_DERIVATION_NOT_READY`
