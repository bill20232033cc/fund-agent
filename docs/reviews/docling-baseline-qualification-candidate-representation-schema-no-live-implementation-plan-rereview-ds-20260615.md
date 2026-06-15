# Candidate Representation Schema No-live Implementation Plan Rereview - DS

Date: 2026-06-15

Gate: Candidate Representation Schema No-live Implementation Plan Review Gate

Targeted finding: DS-NL-PLAN-F1 only

Verdict: PASS

## Re-reviewed Finding

DS-NL-PLAN-F1 previously blocked the plan because it listed proposed model names without field-level contracts, nullability/default rules, route-specific locator payload structures, projection issue shape, `CandidateAnchorNote` shape, or tests that would prevent lossy route collapse.

## Closure Assessment

Closed.

Evidence in the current plan:

- §5.1 now defines field-level contracts for all proposed models: `CandidateRepresentationIdentity`, `CandidateRepresentationStatus`, `CandidateSourceLocator`, `CandidateSectionNode`, `CandidateTextBlock`, `CandidateTableBlock`, `CandidateTableCell`, `CandidateRepresentationDocument`, `CandidateProjectionIssue`, and `CandidateAnchorNote`.
- Those tables include field names, types, required status, null/default rules, and projection source or route semantics where applicable.
- `CandidateSourceLocator` now carries route-discriminating fields for source ref, page, bbox, URL, DOM id, table/row/column indexes, and pdfplumber character offsets.
- §6.1 now defines route-specific locator rules for Docling, pdfplumber, and EID HTML render, including Docling bbox/page/cell offsets, pdfplumber `bbox=None`, and EID blocked/document-level failure plus `page_number=None`.
- `CandidateProjectionIssue` now has an explicit shape: `issue_id`, `severity`, `source_kind`, `location`, `message`, and `failure_code`.
- `CandidateAnchorNote` now has an explicit internal shape and keeps `field_correctness_status` / `source_truth_status` at `not_proven`.
- §8 now requires tests that preserve Docling bbox/page/offset/span/header flags, pdfplumber row/column/header data with `bbox=None`, EID blocked document-level failure with no sections/tables/cells, and failure if route-specific locator payloads collapse into one lossy shape.

## Remaining Residuals

- This rereview only closes DS-NL-PLAN-F1. It does not perform a full new plan review.
- The plan remains no-live and candidate-only; implementation still must not touch public `EvidenceAnchor`, `FundDocumentRepository`, production parser, Service/UI/Host/renderer/quality gate, readiness, release, or PR paths.

## Final Recommendation

PASS. DS-NL-PLAN-F1 is closed. The plan may proceed to controller disposition for the no-live implementation planning gate.
