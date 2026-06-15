# Review: Same-report EID HTML Render vs Pdfplumber vs Docling Document Representation Evidence

Reviewer: MiMo
Date: 2026-06-15
Gate: `Same-report EID HTML Render vs Pdfplumber vs Docling Document Representation Evidence Gate`
Reviewed artifact: `docs/reviews/same-report-eid-html-vs-pdfplumber-vs-docling-document-representation-evidence-20260615.md`

## Verdict

**PASS_WITH_NONBLOCKING_FINDINGS**

## Review Focus Results

### 1. NOT_READY and candidate-only status preservation

PASS. The artifact consistently preserves `NOT_READY` throughout:

- Status field: `EVIDENCE_COMPLETE_NOT_READY` (line 9)
- Final verdict: `HYBRID_OR_NEXT_EVIDENCE_REQUIRED_NOT_READY` (line 11)
- Readiness state: `NOT_READY` (line 13)
- Section 5 route decision table: all four options are `NO_NOT_READY` or `YES_FOR_PLANNING_NOT_READY`
- Section 6 guard labels: `not_readiness_proof`, `no_repository_behavior_change`, `no_parser_replacement` all present
- Section 7 recommendation explicitly requires "must preserve EID single-source/no-fallback semantics, candidate-only status, repository encapsulation and `NOT_READY`"
- Worker self-check (line 41) correctly identifies role as evidence worker, not controller

All three routes maintain candidate-only classification:
- EID HTML: `partly_stable_route_family_candidate_but_no_004393_same_report_proof`
- pdfplumber: `accepted_operational_path_for_current_extraction_but_not_full_FundDisclosureDocument_representation`
- Docling: `strongest_same_report_full_document_candidate_but_candidate_only`

No readiness, release, source-truth, field-correctness or parser-replacement claim found.

### 2. HTML render not treated as raw XML/source truth/field correctness/taxonomy proof

PASS. The artifact explicitly and repeatedly guards against this conflation:

- Section 1 non-proof guard list includes `not_raw_xml_download_proof`, `not_field_correctness_proof`, `not_taxonomy_compatibility_proof`, `not_source_truth`, `not_readiness_proof` (lines 145-148)
- Section 3 comparability matrix, EID HTML row: "Raw XML, field correctness, taxonomy, ordinary non-REIT annual coverage and full narrative coverage are unproven" (line 73)
- Section 4.1: "HTML render is not raw XML/XBRL instance proof" (line 89)
- Section 6 required guard labels enumerate all seven anti-conflation guards (lines 142-148)
- Section 2 evidence inputs table explicitly marks accepted HTML evidence as "Not raw XML, not field correctness, not taxonomy proof" (line 51)

No instance found where HTML render is treated as raw XML download, source truth, field correctness or taxonomy proof.

### 3. No production parser replacement / repository behavior change / direct access

PASS. The artifact does not:

- Change `FundDocumentRepository` — Section 1 explicit guard (line 30); Section 2 test_repository input confirms no candidate route (line 65)
- Change production parser — Section 6 `no_parser_replacement` guard (line 148)
- Authorize Service/UI/Host/renderer/quality-gate direct access — Section 1 guard (line 30)
- Change source policy, fallback behavior or EID single-source semantics — Section 1 guard (line 30)

### 4. Same-report observed evidence vs route-family evidence distinction

PASS. The artifact makes this distinction explicit and traceable:

- Section 1: "this artifact distinguishes same-report observed evidence from route-family or repo facts" (line 23)
- EID HTML: "Same-report `004393 / 2025` HTML render not present in allowed evidence" → route-family classification with 12-sample accepted evidence (line 73)
- pdfplumber: "No allowed same-report full-document pdfplumber document representation artifact for `004393 / 2025`" → operational path fact, not same-report representation proof (line 74)
- Docling Route A: "Same-report observed: `004393 / 2025`, 65 pages, 670 text items..." → true same-report evidence (line 75)
- Section 2 inputs table: "Missing accepted `004393 / 2025` EID HTML render artifact" and "Missing accepted `004393 / 2025` full pdfplumber document representation artifact" both classified as `residual` (lines 66-67)
- Section 3 comparability matrix uses `Source kind` column to distinguish: `eid_xbrl_html_render_candidate`, `current_production_pdf_parser_internal`, `docling_pdf_candidate`, `docling_pdf_candidate_internal_helpers`

The distinction is clear and consistently applied throughout the comparability matrix and route-by-route findings.

### 5. Hybrid/next evidence recommendation supported by evidence

PASS. The recommendation is well-supported:

- Section 5 route decision table shows all single-source options are `NO_NOT_READY` with specific reasons:
  - EID HTML only: same-report `004393/2025` absent, ordinary non-REIT coverage unproven, narrative/PDF replacement unproven
  - Docling only: source truth, model provenance, production route and field correctness unproven
  - pdfplumber only: field/extractor-oriented, not proven as full `FundDisclosureDocument` representation
- Hybrid option is `YES_FOR_PLANNING_NOT_READY` with supporting rationale
- Section 4 route-by-route findings provide specific strength/weakness evidence for each route that collectively supports hybrid planning:
  - pdfplumber = production baseline with page-number provenance
  - Docling = strongest same-report full-document candidate with section hierarchy and table-cell provenance
  - EID HTML = structured disclosure locator candidate where available
- Section 7 recommendation is bounded and specific: three explicit roles, preservation constraints, and decision between narrow pilot vs broader schema slice

The recommendation does not overclaim: it is `YES_FOR_PLANNING_NOT_READY`, not `YES_FOR_IMPLEMENTATION`.

### 6. Blockers requiring evidence artifact fix before controller judgment

No blocking findings identified. See nonblocking findings below.

## Findings Table

| # | Severity | Finding | Evidence location | Required action |
|---|---|---|---|---|
| F1 | Nonblocking / Low | Section 6 residuals table does not explicitly list the two key availability gaps identified in Section 2: "Same-report EID HTML render for `004393 / 2025`" and "Pdfplumber full-document representation baseline for `004393 / 2025`". These are correctly recorded as `residual` in Section 2 inputs table (lines 66-67) and referenced in Section 5 decision rationale, but Section 6 residuals table (lines 152-163) omits them as discrete row items, relying on the reader to connect Section 2 residuals to Section 5 decision outcomes. | Section 2 lines 66-67 vs Section 6 lines 152-163 | No fix required for controller judgment; these gaps are adequately captured in Section 2 and Section 5. Consider adding explicit rows to Section 6 residuals table for completeness in future re-issuance if controller requests. |
| F2 | Nonblocking / Info | The `HYBRID_OR_NEXT_EVIDENCE_REQUIRED_NOT_READY` verdict label is novel in this evidence chain. Prior evidence used `INSUFFICIENT_COMPARABLE_EVIDENCE_NOT_READY`. The new verdict semantics are clear from context but could benefit from a one-line definition or pointer to Section 5 for controller reference. | Line 11, Section 5 | No fix required; verdict is self-explanatory from Section 5 table. |

## Residual Risks

1. **Same-report `004393 / 2025` EID HTML render remains undiscovered** — blocks route-strength comparison at same-report level for this specific fund/year. Not a blocker for hybrid planning gate, but limits the evidence basis for EID HTML route classification.

2. **Same-report `004393 / 2025` full pdfplumber representation not materialized** — current production parser operates but no full-document quality artifact was allowed. Hybrid planning gate should decide whether to materialize a baseline artifact.

3. **Ordinary non-REIT annual HTML render coverage unproven** — accepted HTML sample window was REIT annual. Hybrid planning gate should address whether additional non-REIT coverage evidence is needed before committing to EID HTML as a disclosure locator source.

4. **Docling model artifact provenance remains benchmark-only** — local HuggingFace cache copies are not production-accepted provenance. A future provenance acceptance gate is correctly deferred.

5. **Route-by-route evidence asymmetry** — Docling has same-report observed evidence while EID HTML and pdfplumber rely on route-family/operational-path evidence. The hybrid recommendation correctly accounts for this asymmetry by not requiring equal evidence strength for planning.

## Final Recommendation

**Accept this evidence artifact for controller judgment.** The artifact is well-structured, correctly scoped, preserves all required guards and boundaries, and supports the hybrid planning recommendation with adequate evidence. The two nonblocking findings do not require artifact revision before controller judgment.

The evidence supports proceeding to a `Hybrid FundDisclosureDocument Candidate Source Planning Gate` as recommended in Section 7, with the understanding that same-report EID HTML render and pdfplumber baseline materialization remain deferred residuals that the planning gate must explicitly disposition.
