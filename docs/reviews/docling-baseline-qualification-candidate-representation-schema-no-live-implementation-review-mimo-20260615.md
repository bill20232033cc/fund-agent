# Candidate Representation Schema No-live Implementation Review - MiMo - 2026-06-15

Verdict: `BLOCKED`

## Findings

| ID | Severity | Evidence | Finding | Required fix |
| --- | --- | --- | --- | --- |
| MIMO-IMPL-F1 | High | `fund_agent/fund/documents/candidates/representation_projection.py` initial `_project_cells()` implementation; projection tests did not assert zero-valued row/column locators. | Row/column locator projection dropped valid zero offsets because `0` was treated as falsy when falling back from `row_start` to `row_index` and `column_start` to `column_index`. | Use first-present semantics that preserves `0`; add regression assertions for Docling `row_start=0`, `column_start=0` and pdfplumber synthesized zero-based locators. |
| MIMO-IMPL-F2 | Medium | `tests/fund/documents/test_candidate_representation_projection.py` initial assertions. | Tests did not catch the zero-offset locator regression. | Extend Docling and pdfplumber projection tests with explicit zero-index locator assertions. |

## Accepted Facts

- Three internal route kinds are present and closed: `docling_pdf_candidate`, `pdfplumber_pdf_candidate`, `eid_xbrl_html_render_candidate`.
- Candidate-only status guards reject proof/parser-replacement claims in model/projection paths.
- EID HTML blocked projection remains document-level failure without tables.
- README does not overclaim baseline/readiness.

## Controller Disposition

Both findings are accepted and fixed before targeted re-review.
