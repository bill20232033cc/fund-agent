# Same-report EID HTML Render vs Pdfplumber vs Docling Document Representation Evidence — DS Review

Date: 2026-06-15

Gate: `Same-report EID HTML Render vs Pdfplumber vs Docling Document Representation Evidence Gate`

Reviewer role: DS review worker

Reviewed artifact: `docs/reviews/same-report-eid-html-vs-pdfplumber-vs-docling-document-representation-evidence-20260615.md`

## Verdict

**PASS_WITH_NONBLOCKING_FINDINGS**

## Review Scope

This review validates the evidence artifact against the five prescribed review focuses. No code edits, no control/design doc edits, no stage/commit/push/PR. This review does not enter the next gate.

## Focus 1: NOT_READY And Candidate-only Status Preservation

| Check | Result |
|---|---|
| Artifact status is `EVIDENCE_COMPLETE_NOT_READY` | PASS |
| Final verdict is `HYBRID_OR_NEXT_EVIDENCE_REQUIRED_NOT_READY` | PASS |
| Readiness state is `NOT_READY` | PASS |
| All three routes classified with `candidate` qualifier where applicable | PASS |
| EID HTML: `partly_stable_route_family_candidate_but_no_004393_same_report_proof` | PASS |
| Docling: `strongest_same_report_full_document_candidate_but_candidate_only` | PASS |
| Pdfplumber: correctly classified as operational path, not promoted to full representation | PASS |
| Section 6 guard labels: `not_readiness_proof`, `no_repository_behavior_change`, `no_parser_replacement` | PASS |

No drift from `NOT_READY` or candidate-only status was observed. The artifact consistently classifies each route with appropriate candidate/operational qualifiers and never promotes any route to production, source truth, or readiness.

## Focus 2: HTML Render Not Treated As Raw XML / Source Truth / Field Correctness / Taxonomy Proof

| Check | Result |
|---|---|
| Section 1 explicit non-claims include raw XML, field correctness, taxonomy, source truth | PASS |
| Section 3 EID HTML row non-proof guard: `not_raw_xml_download_proof`, `not_field_correctness_proof`, `not_taxonomy_compatibility_proof`, `not_source_truth` | PASS |
| Section 4.1: "HTML render is not raw XML/XBRL instance proof" | PASS |
| Section 4.1: "HTML render lacks PDF page/bbox provenance" | PASS |
| Section 6: all five blocked proofs correctly labeled and scoped | PASS |
| `not_raw_xml_download_proof`: "HTML render remains rendered HTML" | PASS |
| `not_field_correctness_proof`: correctly scoped to worker scope | PASS |
| `not_taxonomy_compatibility_proof`: correctly scoped, no schemaRef/DTS/namespace proof | PASS |
| `not_source_truth`: all three inputs correctly classified as candidate representation inputs | PASS |

No claim in the artifact treats HTML render as raw XML download, XBRL instance proof, field correctness proof, or taxonomy compatibility proof. The evidence artifact maintains the same guard discipline established by prior HTML render evidence and controller judgments.

## Focus 3: No Production Parser Replacement / Repository Behavior Change / Service/UI/Host/Renderer/Quality Direct Access

| Check | Result |
|---|---|
| Section 1 explicit non-claims: no parser replacement, no repository behavior change, no Service/UI/Host/renderer/quality gate direct access | PASS |
| Preflight table: worker self-check confirms no source/test/runtime/control docs changed | PASS |
| Section 6: `no_repository_behavior_change` guard confirmed by test assertion | PASS |
| Section 6: `no_parser_replacement`: "production parser remains current pdfplumber path" | PASS |
| Section 3 pdfplumber row: retains current operational path classification without replacement authorization | PASS |
| Docling classification: `strong_candidate_for_full_document_representation_not_production_parser` | PASS |
| EID HTML classification: `keep_as_structured_disclosure_locator_candidate_where_available` | PASS |
| Section 7 recommendation: explicitly requires repository encapsulation, candidate-only status | PASS |

The artifact correctly maintains all production boundaries. No route is promoted to production parser status. No repository behavior change is authorized. No consumer integration is authorized. Candidate internals remain under candidate package.

## Focus 4: Same-report Observed Evidence Distinguished From Route-family Evidence And Residuals

| Check | Result |
|---|---|
| Section 2 input table explicitly classifies each input as route-family vs same-report vs repo fact | PASS |
| EID HTML render: classified as route-family evidence, same-report `004393 / 2025` artifact explicitly absent | PASS |
| Docling Route A: classified as same-report observed evidence for `004393 / 2025` | PASS |
| Candidate internals: classified as same-report excerpt-backed | PASS |
| Section 3 comparability matrix: EID HTML `Coverage signal` and `Section hierarchy signal` both note route-family only, not same-report proven | PASS |
| Missing input entries: both missing same-report artifacts transparently flagged as residuals | PASS |
| Prior same-report comparison (`INSUFFICIENT_COMPARABLE_EVIDENCE_NOT_READY`) correctly cited as accepted evidence / residual | PASS |

The artifact clearly distinguishes between:
- Route-family evidence (EID HTML: 12 samples exist, but not for `004393 / 2025`)
- Same-report observed evidence (Docling: 65 pages, 670 text items, 95 tables for `004393 / 2025`)
- Operational repo facts (pdfplumber: works but no full same-report representation artifact present)

This distinction is critical for the hybrid recommendation: it prevents the artifact from overclaiming route-family evidence as same-report proof.

## Focus 5: Hybrid/next Evidence Recommendation Supported By Evidence

| Check | Result |
|---|---|
| Section 5 decision sufficiency: single-route options all `NO_NOT_READY` with clear reasons | PASS |
| Section 5: hybrid option `YES_FOR_PLANNING_NOT_READY` — planning only, not production | PASS |
| Section 7 primary recommendation: Hybrid FundDisclosureDocument Candidate Source Planning Gate | PASS |
| Three hybrid roles are evidence-backed: | |
| - Pdfplumber baseline: operational fact confirmed by design/repo evidence | PASS |
| - Docling candidate full-document: strongest same-report representation signal in allowed evidence | PASS |
| - EID HTML candidate locator: structured disclosure locator signal where same-report availability is proven | PASS |
| Recommendation explicitly preserves EID single-source/no-fallback, candidate-only, repository encapsulation, `NOT_READY` | PASS |
| Deferred entries (11 items) cover all open residuals without skipping any gate | PASS |
| Section 8 self-check confirms no controller action taken, scope boundary preserved | PASS |

The hybrid recommendation is well-supported by the evidence asymmetry documented in the artifact:
- Docling has the strongest same-report `004393 / 2025` full-document signal
- EID HTML has structured disclosure locator signal but lacks same-report `004393 / 2025` proof
- Pdfplumber remains the operational baseline but lacks full-document representation proof

The recommendation correctly defers production decisions and routes to a planning gate rather than an implementation gate.

The recommendation also aligns with the phaseflow queue in `docs/implementation-control.md`, where item 11 (`FundDisclosureDocument Candidate Source No-live Implementation Planning Gate`) is explicitly deferred "until same-report evidence determines whether EID HTML render alone, Docling, pdfplumber or a hybrid representation should be planned." The current evidence artifact provides that determination (hybrid), so the recommendation naturally follows the existing queue.

## Focus 6: Blockers Requiring Fix Before Controller Judgment

No blockers found. The evidence artifact:
- Correctly reports its own evidence gaps as open residuals
- Makes no unauthorized scope expansions
- Preserves all NOT_READY and candidate-only boundaries
- Cross-references to accepted evidence are accurate
- Self-check validation (`git diff --check`) passes

## Findings Table

| Severity | Finding | Evidence Location | Required Action |
|---|---|---|---|
| info | The hybrid recommendation ("Hybrid FundDisclosureDocument Candidate Source Planning Gate") could explicitly reference phaseflow queue item 11 to reduce ambiguity about whether this is a new gate or a refinement of the existing deferred gate. | Section 7, primary recommendation | Controller may optionally add a cross-reference to phaseflow item 11 in the judgment; non-blocking. |
| info | Section 3 pdfplumber reliability classification uses a long descriptive string (`accepted_operational_path_for_current_extraction_but_not_full_FundDisclosureDocument_representation`) rather than a compact classification label like the other two routes. This is a stylistic consistency observation, not a factual error. | Section 3, pdfplumber row, reliability column | No action required; controller may note for consistency in future artifacts. |
| info | The missing same-report EID HTML render artifact for `004393 / 2025` is correctly flagged as a residual, but the artifact does not discuss whether the HTML render URL for this specific fund would be constructible from the known URL pattern (which prior HTML evidence proved for REIT samples via public announcement JSON). This is a minor completeness observation; the residual classification remains correct regardless. | Section 2, missing input row; Section 6 residual table | No action required; can be explored in a future discovery gate. |

## Cross-reference Verification

Key claims verified against cited sources:

| Claim in evidence | Source checked | Match |
|---|---|---|
| Docling Route A: 65 pages, 670 text items, 95 tables, 213 headings, all §1-§13 | `docling-route-a-local-artifact-conversion-quality-evidence-20260615.md` | Confirmed |
| Candidate internals: models, normalization, locators, failure mapping, no-consumption guards implemented | `docling-funddisclosuredocument-mapping-normalization-no-live-implementation-controller-judgment-20260615.md` | Confirmed; verdict `ACCEPT_IMPLEMENTATION_WITH_NONBLOCKING_RESIDUALS_NOT_READY` |
| Prior same-report comparison: `INSUFFICIENT_COMPARABLE_EVIDENCE_NOT_READY` | `same-report-document-representation-quality-comparison-evidence-20260614.md` | Confirmed |
| HTML render: 12 samples available, partly stable, not raw XML | `csrc-eid-xbrl-html-structured-render-artifact-evaluation-evidence-20260614.md` and controller judgment | Confirmed |
| Current gate: same-report evidence only, no production integration | `docs/implementation-control.md` lines 42-52 | Confirmed |
| Repository non-behavior: `FundDocumentRepository.load_annual_report` has no candidate route | `test_repository.py` (cited, not re-run) | Confirmed by prior controller judgment |
| Controller judgment deferred same-report comparison as next gate | `docling-funddisclosuredocument-mapping-normalization-no-live-implementation-controller-judgment-20260615.md` Section 8 | Confirmed |

No cross-reference contradictions were found.

## Boundary Validation

| Boundary | Status |
|---|---|
| `FundDocumentRepository` behavior unchanged | PASS — test assertion cited, no change authorized |
| EID single-source/no-fallback preserved | PASS — hybrid recommendation explicitly preserves this |
| `EvidenceAnchor` schema unchanged | PASS — candidate note placed under internals only |
| `EvidenceSourceKind` unchanged | PASS — `docling_pdf_candidate` is internal metadata only |
| No production parser replacement | PASS — pdfplumber remains production baseline |
| No Service/UI/Host/renderer/quality direct access | PASS — all routes remain candidate or repository-internal |
| No source truth / field correctness / taxonomy proof claims | PASS — all blocked proofs correctly retained |
| Release/readiness NOT_READY preserved | PASS — consistently maintained |

## Residual Risks

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Hybrid planning gate may need same-report HTML render discovery before it can finalize the three-role design | Medium | Low — planning can proceed with role definitions even if specific URL isn't verified | Evidence artifact already defers this as a separate discovery gate |
| The asymmetry in evidence quality (Docling has strongest same-report signal) could bias the hybrid design toward Docling-centric representation | Low | Medium — but the evidence artifact explicitly retains pdfplumber as baseline and HTML render as locator source | Controller should ensure the planning gate maintains the three-role balance |
| Docling model artifact provenance remains unaccepted for production | Low | Low for planning gate — only matters at production integration | Already deferred as separate gate |

## Final Recommendation

Accept the evidence artifact as `EVIDENCE_COMPLETE_NOT_READY` with verdict `HYBRID_OR_NEXT_EVIDENCE_REQUIRED_NOT_READY`. Route to controller for judgment.

The three info-level findings are non-blocking and do not require artifact revision before controller judgment. The evidence artifact correctly:
- Preserves `NOT_READY` and candidate-only status
- Never treats HTML render as raw XML, source truth, field correctness, or taxonomy proof
- Never authorizes production parser replacement, repository behavior change, or consumer integration
- Clearly distinguishes same-report observed evidence from route-family evidence
- Makes a hybrid recommendation that is well-supported by the documented evidence asymmetry

No code edits, no control/design doc edits, no stage/commit/push/PR. Not entering next gate.
