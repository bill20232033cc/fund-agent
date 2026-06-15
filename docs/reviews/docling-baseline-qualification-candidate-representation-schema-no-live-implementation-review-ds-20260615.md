# Candidate Representation Schema No-live Implementation Review - DS - 2026-06-15

Verdict: `BLOCKED`

## Findings

| ID | Severity | Evidence | Finding | Required fix |
| --- | --- | --- | --- | --- |
| DS-IMPL-F1 | Blocking | Accepted plan requires Docling cell locator to preserve header flags. Initial `CandidateTableCell` had no `row_header` / `column_header` fields, projection did not read/store those flags, and projection tests did not assert them. | Route-specific Docling locator detail was lost. Header cells could not be distinguished from data cells in the route-neutral model, weakening later locator stability evidence and violating the accepted implementation plan. | Add explicit header flag preservation, map them from input cells, and add no-live assertions proving they survive projection. |

## Non-blocking Accepted Points

- Candidate-only guards are implemented for status and anchor notes.
- Reviewed implementation does not import or modify `FundDocumentRepository`, public `EvidenceAnchor`, Service, Host, UI, renderer, or quality gate paths.
- EID HTML blocked route remains document-level failure only in covered tests.
- Tests are synthetic/no-live and do not run Docling/pdfplumber conversion.

## Controller Disposition

`DS-IMPL-F1` is accepted and fixed before targeted re-review.
