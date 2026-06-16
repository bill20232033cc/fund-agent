# Fund Disclosure Processor Contract Design - 2026-06-16

Gate: `Fund Disclosure Processor Contract Design Gate`
Role: planning worker
Gate classification: `heavy`
Release/readiness: `NOT_READY`

## 1. Controller Request

Design a narrow fund-disclosure processor contract before continuing the 17-row Docling source-truth residual closure work.

The user clarified two binding constraints:

- This project targets fund quarterly reports, annual reports, prospectuses and similar fund disclosure materials, not company financial statements.
- The relevant storage separation is `source / processed / fund`, not Dayu's company-report framing.

This design therefore does not copy Dayu Fins financial-statement contracts. It only accepts the useful pattern that a domain package owns document storage, processing and processor dispatch behind a stable repository boundary.

## 2. Current Evidence Base

| Evidence | Accepted fact used by this design |
| --- | --- |
| `docs/design.md` section 6.1 | Production annual-report access must stay behind `FundDocumentRepository`; current production parser is `pdfplumber -> ParsedAnnualReport -> extractor -> EvidenceAnchor / CHAPTER_CONTRACT / audit / report generation`. |
| `docs/design.md` current Docling candidate section | `FundDisclosureDocument` is a Fund documents internal candidate representation; it may become extractor/projection input but cannot bypass custom extractors, chapter fact projection, EvidenceAnchor validation or fail-closed classification. |
| `fund_agent/fund/README.md` candidate harness section | `fund_agent/fund/documents/candidates/` is candidate-only evidence harness; it does not change `FundDocumentRepository`, production parser, public `EvidenceAnchor`, Service/UI/Host/renderer/quality gate, source truth or readiness. |
| `docs/reviews/docling-baseline-support-source-truth-evidence-controller-judgment-20260616.md` | Current source-truth evidence is partial: `55 / 72` selected rows matched repository parsed source body; `17 / 72` remain residual or blocked; all `4 / 4` reports loaded through `FundDocumentRepository` with EID single-source metadata. |
| `reports/docling-baseline-support-source-truth/20260616/source_truth_matrix.json` | Residual split is `15` ambiguous source-body matches, `1` source-body mismatch and `1` semantic assignment residual. |
| `docs/dayu-agent-codiwiki-and-development-stage-analysis-20260614.md` | Dayu Fins is a domain package, not a system layer; its processor dispatch and storage discipline are useful references, but company financial-statement contracts are not project truth here. |

## 3. Problem Statement

The 17 residuals are not all Docling parsing failures.

They expose a missing contract between three concerns:

1. Whether the official fund disclosure source identity is safe and same-source.
2. Whether a processor can provide stable section/table/cell locators for a selected disclosure body.
3. Whether a fund-domain field claim has the right semantic label and evidence anchor.

Without this contract, the next residual fix would tend to become a one-off proof script: enough to close a sample matrix, but not reusable for annual reports, quarterly reports, prospectuses or later baseline qualification.

## 4. Design Decision

Adopt a project-owned `Fund Disclosure Processor Contract` as an accepted future design for Fund documents internals.

The contract has three layers:

```text
source -> processed -> fund
```

This is a Fund-domain contract. It is not Dayu Fins runtime adoption, not company financial-statement extraction, and not a production Docling promotion.

### 4.1 Source Layer

The source layer owns official disclosure identity and acquisition provenance.

Current implementation fact:

- annual reports are loaded through `FundDocumentRepository`;
- current production source policy is EID single-source, no fallback;
- `not_found`, `unavailable`, `schema_drift`, `identity_mismatch`, `integrity_error` remain the canonical source failure categories.

Future contract fields:

| Field | Meaning |
| --- | --- |
| `fund_code` | 6-digit fund code from repository/source identity. |
| `document_kind` | Disclosure kind, initially `annual_report`; future candidates include `quarterly_report`, `semiannual_report`, `prospectus`, `fund_contract`, `announcement`. |
| `report_period` | Year or period covered by the disclosure. |
| `repository_source_name` | Repository/source identity, not parser identity and not `EvidenceAnchor.source_kind`. Current production annual reports remain `eid` source metadata. |
| `source_mode` | Single-source or future accepted source policy mode. Current annual reports remain `single_source_only`. |
| `source_artifact_identity` | Repository-owned safe identity such as report id, source URL, content hash, cache provenance and discovery contract version. |
| `source_failure_category` | Canonical failure category, when source acquisition or source identity fails. |

Non-goal:

- Do not expose PDF paths, cache internals or download helpers outside Fund documents.

### 4.2 Processed Layer

The processed layer owns parser output normalization. This is where Docling, pdfplumber, HTML render or other processors may produce route-neutral disclosure representation.

Existing candidate model fields already point in the right direction:

- `CandidateRepresentationDocument`;
- `CandidateRepresentationIdentity`;
- `CandidateSectionNode`;
- `CandidateTextBlock`;
- `CandidateTableBlock`;
- `CandidateTableCell`;
- `CandidateSourceLocator`;
- `CandidateAnchorNote`.

Future accepted contract name:

```text
FundDisclosureProcessedDocument
```

It may initially reuse or adapt the candidate representation model, but implementation must keep candidate/proof flags explicit until a later gate promotes any part to production.

Boundary rule:

- `repository_source_name` records official source identity such as `eid`.
- `processor_source_kind` or `processor_profile` records parser/representation route identity such as `docling_pdf_candidate`.
- `EvidenceAnchor.source_kind` remains the existing semantic evidence-source field. For annual-report anchor candidates it must remain `annual_report`; repository source and processor route may only be preserved in candidate metadata, note fields or proof-row metadata.

Required processed-layer locator fields for residual closure:

| Field | Required for | Reason |
| --- | --- | --- |
| `section_id` / `heading_path` | all rows | Prevent section-level false matches and support current EvidenceAnchor semantics. |
| `page_number` | PDF-derived annual report anchors | Preserve current annual-report anchor renderability. |
| `table_id` / `table_ordinal` | table fields | Disambiguate repeated values across tables. |
| `caption` / `label` / `table_family` | table fields | Distinguish portfolio, fee, holder and profile tables. |
| `row_label_path` | identity, fee, portfolio, holder fields | Disambiguate repeated numeric/text cells by row meaning. |
| `column_header_path` | share-class and period-sensitive fields | Distinguish A/C share classes, current-year columns and total columns. |
| `cell_hash` / `locator_hash` | source-truth comparison | Make locator equality deterministic across artifacts. |
| `bbox` / `source_ref` | raw-PDF/bbox proof candidate | Keep optional path for later proof without making it required now. |
| `locator_stability` | all locator claims | Allow fail-closed when merged cells, missing parent table context or unstable heading mapping makes the row unprovable. |

Processed-layer failure categories:

| Failure | Meaning | Source failure mapping |
| --- | --- | --- |
| `processor_unavailable` | Processor or local artifact unavailable | `unavailable` when it blocks a selected route. |
| `document_identity_mismatch` | Processed artifact identity does not match source identity | `identity_mismatch`. |
| `representation_schema_drift` | Parser output no longer conforms to accepted schema | `schema_drift`. |
| `locator_unstable` | Stable section/table/cell locator cannot be formed | `schema_drift` for source route, residual for candidate evidence. |
| `content_integrity_error` | Hash, byte identity or artifact integrity fails | `integrity_error`. |

### 4.3 Fund Layer

The fund layer owns fund-domain semantics.

It receives processed documents as extractor/projection input and decides whether a field candidate can become a fund fact candidate, an `EvidenceAnchor` candidate, or a fail-closed residual.

Future contract fields:

| Field | Meaning |
| --- | --- |
| `fact_id` | Review/evidence fact id such as `S6-F041`. |
| `field_name` | Fund-domain field such as `benchmark`, `fund_code`, `equity_investment_amount`. |
| `field_family` | Fund disclosure field family such as identity/profile/fee/portfolio/manager ownership/performance. |
| `expected_section_family` | Allowed annual-report section family or future disclosure section family. |
| `semantic_label_requirement` | Required row label, table family or source context for this field. |
| `share_class_context` | A/C/share-class or total context when relevant. |
| `normalized_value` | Candidate normalized value. |
| `evidence_anchor_candidate` | Candidate fields matching current `EvidenceAnchor` semantics; still not a production anchor until accepted by extractor/projection. |
| `proof_level` | `source_body_match`, `disambiguated_locator_match`, `raw_bbox_match_candidate`, `semantic_assignment_proven` or residual/blocker. |
| `residual_reason` | Canonical reason when proof is insufficient. |

Fund-layer hard rules:

- A value match alone is insufficient for semantic proof when multiple matches exist.
- `benchmark` requires benchmark-labeled source context; investment-objective text cannot close it.
- Fund identity fields must prefer labeled profile-table context such as `基金主代码` and `基金名称`, not repeated raw occurrences.
- Portfolio amount fields require table family/caption plus row label plus column header plus share-class/total context.
- If semantic labels and locators disagree, block at fund layer instead of upgrading source truth.

## 5. Processor Dispatch Design

Do not copy Dayu's company financial-report dispatch keys directly.

For fund disclosures, dispatch should use:

```text
document_kind + repository_source_name + media_type + processor_profile
```

Initial values:

| Key | Initial allowed values |
| --- | --- |
| `document_kind` | `annual_report` only for implementation slice 1. |
| `repository_source_name` | repository source identity from `FundDocumentRepository`; candidate parser identity stays separate. |
| `media_type` | `pdf`, `html_candidate`, `json_candidate`, `markdown_candidate`. |
| `processor_profile` | `production_pdfplumber_annual`, `docling_pdf_candidate`, `pdfplumber_pdf_candidate`, `eid_html_render_candidate`. |

Dispatch priority for current baseline work:

1. Current production annual-report parser remains `pdfplumber -> ParsedAnnualReport -> extractor`.
2. Docling PDF stays candidate-only and may feed processed-layer comparison/proof artifacts.
3. EID HTML render stays candidate/future until a separate source/schema gate accepts it.
4. Generic raw text or markdown outputs are diagnostics only, not source truth.

This preserves production behavior while allowing residual closure to reuse a stable route-neutral processor contract.

## 6. Mapping The 17 Residuals

| Residual family | Count | Contract gap | Required closure rule |
| --- | ---: | --- | --- |
| `ambiguous_source_body_match` | 15 | Source-body text match lacks enough processed/fund locator semantics. | Require section/table/row/column disambiguation and semantic label match before upgrading to source truth. |
| `source_body_mismatch` | 1 | Current selected source scope does not contain the normalized candidate value under the deterministic matching contract. | Triage across source identity, processed locator and fund semantic assignment; do not treat parser agreement as proof. |
| `semantic_assignment_residual` | 1 | Candidate value is attached to the wrong or insufficient semantic context. | Require fund-layer semantic label proof; keep residual if only adjacent or shared locator text exists. |

Specific residual handling:

| Residual | Required next handling |
| --- | --- |
| `fund_code`, `fund_name`, `manager`, `custodian` ambiguity | Match only when processed locator is inside expected profile table and row label path contains the expected label. |
| fee/share-class ambiguity | Match only when row label and column header identify fee type and share class. |
| portfolio amount ambiguity | Match only when table family/caption, row label and amount column agree. |
| `S5-F023 / investment_objective` mismatch | Classify root cause by source scope, processed section/table locator and fund semantic assignment. If same-source body does not contain the value, keep blocked. |
| `S6-F041 / benchmark` semantic residual | Do not close with the shared investment-objective cell. Close only if a benchmark-labeled source context is found. |

## 7. Implementation Slicing For Later Gates

This design gate does not authorize implementation. If accepted, the next implementation should be split narrowly.

### Slice 1: residual closure plan

Artifact-only planning gate.

Define:

- exact reviewed residual rows;
- expected locator/fund semantic rule per row;
- accepted source artifacts and repository reference constraints;
- expected output matrix fields;
- validation commands.

### Slice 2: candidate contract adapter

No-live implementation gate under `fund_agent/fund/documents/candidates/`.

Allowed work:

- add a candidate-internal adapter or data model for `source / processed / fund` proof rows;
- enrich residual matrix generation with locator disambiguation fields;
- preserve all candidate-only/proof-status flags.

Not allowed:

- production `FundDocumentRepository` behavior change;
- public `EvidenceAnchor` schema change;
- Service/UI/Host/renderer/quality gate integration;
- Docling baseline promotion.

### Slice 3: source-truth residual closure evidence

No-live evidence gate.

Expected output:

- a revised matrix with 17 rows dispositioned as `disambiguated_source_body_match`, `source_body_mismatch`, `semantic_assignment_residual` or another explicit residual;
- exact counts;
- root-cause notes for any still-blocked row;
- no baseline/readiness claim.

## 8. Acceptance Criteria For This Design

This design is acceptable only if it satisfies all conditions below.

| Criterion | Status |
| --- | --- |
| Preserves `FundDocumentRepository` as production annual-report access boundary | required |
| Defines `source / processed / fund` separation for fund disclosures | required |
| Keeps Docling candidate-only | required |
| Does not copy company financial-statement contracts | required |
| Gives every 17-row residual family a contract-level closure path | required |
| Does not claim source truth, full correctness, baseline, parser replacement or readiness | required |
| Leaves quarterly/prospectus support as future document-kind expansion, not current implementation scope | required |

## 9. Non-goals

This gate does not authorize:

- source code changes;
- test changes;
- README/design truth-source updates;
- `FundDocumentRepository` behavior changes;
- public `EvidenceAnchor` schema changes;
- direct PDF/cache/source-helper access;
- Docling conversion;
- live/network/EID/provider/LLM/analyze commands;
- official source policy changes;
- production parser replacement;
- Docling baseline qualification;
- release, PR or readiness actions.

## 10. Review Requirements

Review must challenge:

- whether the design is still too broad for the 17-row residual goal;
- whether quarterly/prospectus language could cause implementation scope creep;
- whether any contract field leaks parser or source internals outside Fund documents;
- whether the design gives implementation workers enough rules to avoid one-off scripts;
- whether `S6-F041 / benchmark` is protected from being closed by adjacent or shared locator text.

## 11. Next Entry Point If Accepted

```text
Docling Source-truth Residual Closure Planning Gate
```

Purpose:

- convert this processor contract into a handoff-ready no-live implementation/evidence plan;
- target the 17 residual rows only;
- preserve `NOT_READY`;
- keep baseline qualification blocked until source-truth residuals are closed or explicitly accepted as irreducible residuals.

## 12. Verdict

```text
VERDICT: FUND_DISCLOSURE_PROCESSOR_CONTRACT_DESIGN_READY_FOR_REVIEW_NOT_READY
```
