# Candidate Representation Schema No-live Implementation Plan Review - DS

Date: 2026-06-15

Gate: Candidate Representation Schema No-live Implementation Plan Review Gate

Verdict: BLOCKED

## Scope

Reviewed target:

- `docs/reviews/docling-baseline-qualification-candidate-representation-schema-no-live-implementation-plan-20260615.md`

Accepted design input:

- `docs/reviews/docling-baseline-qualification-candidate-representation-schema-design-plan-controller-judgment-20260615.md`

Context checked:

- `fund_agent/fund/documents/candidates/models.py`
- `fund_agent/fund/documents/candidates/locators.py`
- `fund_agent/fund/documents/candidates/representation_export.py`
- prior accepted schema design plan field lists for route-neutral section/table/cell candidates

No plan/source/code artifact was modified by this review.

## Findings

| ID | Severity | Path / section | Reason | Fix | Blocking |
|---|---|---|---|---|---|
| DS-NL-PLAN-F1 | High | Plan §5 Route-neutral Models, §6 Projection Functions, §8 Tests | The plan is not yet code-generation-ready for the schema slice. It lists dataclass names (`CandidateRepresentationIdentity`, `CandidateRepresentationStatus`, `CandidateSourceLocator`, `CandidateSectionNode`, `CandidateTextBlock`, `CandidateTableCell`, `CandidateTableBlock`, `CandidateRepresentationDocument`, `CandidateAnchorNote`, `CandidateProjectionIssue`) but does not define their field-level contracts, optional/nullability rules, enum/literal values, route-specific locator payload shape, or projection issue shape. §6 says to keep route-specific locator payloads, but does not define the payload structure for Docling vs pdfplumber vs EID HTML. §8 tests cover behavior categories, but do not force preservation of the accepted design fields such as section `source_ref/page_span/source_locator`, table `source_ref/route_table_index/page_numbers/bbox_by_page/locator_stability`, or cell `row_start/column_start/page_number/source_locator/cell_hash/locator_hash`. Current code still has Docling-first candidate models, while `representation_export.py` already has a three-route envelope; without field-level contracts, the implementation worker must invent schema details and may produce a lossy or route-biased model. | Amend the plan before implementation. Add a field matrix for every new model with type, required/optional status, default/null handling, route-specific semantics, and projection source path from existing envelope JSON. Explicitly bind the model fields to the accepted design plan's common envelope, section, table, cell and candidate-anchor-note fields. Add required tests that assert Docling bbox/page/cell offsets, pdfplumber `bbox=None` plus row/column/header data, and EID blocked route as document-level failure with no source-truth upgrade. | Yes |

## Accepted Non-blocking Points

- The proposed write set is correctly limited to candidate internals, tests and Fund README documentation.
- The do-not-modify list correctly excludes public `documents.__init__`, `FundDocumentRepository`, source/cache/adapters, public `EvidenceAnchor`, Service, Host, UI, quality gate and control docs.
- The plan preserves candidate-only, `NOT_READY`, no source truth, no field correctness, no taxonomy proof and no parser replacement status.
- The plan keeps EID HTML blocked payload as document-level failure only and does not treat it as available source truth.
- The validation commands are no-live and do not authorize full Docling/pdfplumber conversion or production integration.

## Required Fix

Before entering no-live implementation, revise the plan to include:

- exact fields for `CandidateRepresentationIdentity`;
- exact fields for `CandidateRepresentationStatus`;
- exact fields and discriminators for `CandidateSourceLocator`;
- exact fields for `CandidateSectionNode`, `CandidateTextBlock`, `CandidateTableBlock` and `CandidateTableCell`;
- exact fields for `CandidateRepresentationDocument`;
- exact fields for `CandidateProjectionIssue`;
- exact `CandidateAnchorNote` structure and its non-proof guard fields;
- route-specific locator payload rules for `docling_pdf_candidate`, `pdfplumber_pdf_candidate` and `eid_xbrl_html_render_candidate`;
- tests that fail if accepted route-specific locator differences are collapsed.

## Final Recommendation

BLOCKED. Do not enter `Candidate Representation Schema No-live Implementation Gate` until DS-NL-PLAN-F1 is fixed. The current plan has correct boundaries, but it is not sufficiently code-generation-ready for a schema implementation gate.
