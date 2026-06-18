# Docling Dedicated Extractor Row-column Label Derivation Implementation Evidence - 2026-06-17

Gate: `Docling Dedicated Extractor Row-column Label Derivation Implementation Gate`
Accepted plan commit: `07886d1`
Status: `IMPLEMENTATION_COMPLETE_NOT_READY`
Release/readiness: `NOT_READY`

## Changed Files

- `fund_agent/fund/documents/candidates/template_field_extraction.py`
- `tests/fund/documents/test_docling_template_field_extraction.py`
- `docs/reviews/code-review-20260617-221818.md`
- `docs/reviews/docling-dedicated-extractor-row-column-label-derivation-code-rereview-20260617.md`

## Implementation Summary

Implemented extractor-local row/column label derivation:

- added private `_TableContext`;
- derives column labels from exactly one deterministic header-like row;
- treats duplicate target headers as ambiguous and fail-closed;
- derives row labels from the first non-empty non-numeric, non-header row cell;
- keeps stored `row_label_path` / `column_header_path` as first-priority evidence;
- does not mutate candidate representation objects;
- does not modify `representation_projection.py`;
- does not modify `FundDataExtractor`;
- does not expose production `EvidenceAnchor`.

Updated table-semantic matchers:

- `_match_performance_field`;
- `_match_portfolio_managers`;
- `_match_holding_row`;
- `_find_cell_by_headers_or_labels`;
- `_row_contains_any`.

## Test Coverage Added

Added focused synthetic coverage for:

- empty-path performance table with deterministic header row;
- empty-path portfolio manager table with deterministic header row;
- empty-path holdings table with deterministic header row and row-leading asset type;
- no deterministic header row remains missing;
- duplicated performance header remains missing;
- structural `column_header=True` without semantic header labels remains missing.

## Code Review Disposition

Code review artifact:

- `docs/reviews/code-review-20260617-221818.md`

Accepted finding:

- `001` column_header flag can turn non-header row 0 into a derived header.

Fix:

- `_is_header_like_row` no longer treats `cell.column_header` as independent evidence.
- Regression test added for structural header flag without semantic labels.

Re-review artifact:

- `docs/reviews/docling-dedicated-extractor-row-column-label-derivation-code-rereview-20260617.md`

Status:

- `001` 已修复.

## Validation

Command:

```text
uv run pytest tests/fund/documents/test_docling_template_field_extraction.py tests/fund/documents/test_docling_evidence_anchor_mapping.py -q
```

Result:

```text
56 passed in 0.41s
```

Command:

```text
uv run ruff check fund_agent/fund/documents/candidates/template_field_extraction.py tests/fund/documents/test_docling_template_field_extraction.py
```

Result:

```text
All checks passed!
```

## Docs Decision

No README update.

Reason:

- The slice changes only candidate-only extractor internals and focused tests.
- No public CLI, README example, package boundary, production behavior, or testing convention changed.

## Residual Risks

- Real-envelope uplift is measured separately in the re-evidence artifact.
- Candidate field hits remain candidate-only and do not prove field correctness.
- No source-truth acceptance, parser replacement, baseline promotion, or production integration is authorized.

VERDICT: `IMPLEMENTATION_COMPLETE_ROW_COLUMN_LABEL_DERIVATION_NOT_READY`
