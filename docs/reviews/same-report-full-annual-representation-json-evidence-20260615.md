# Same-report Full Annual-report Representation JSON Evidence - 2026-06-15

Status: `EVIDENCE_COMPLETE_NOT_READY`  
Gate: `Same-report Full Annual-report Representation JSON Evidence Gate`  
Role: evidence worker  
Fund/report: `004393 / 2025`  
Release/readiness: `NOT_READY`

## 1 Scope

Produce same-report full annual-report representation JSON evidence for three candidate routes: Docling Route A, pdfplumber local baseline, and EID HTML render. This gate writes only the three representation JSON artifacts and this evidence note.

No live/network/provider/LLM/analyze/checklist/golden/readiness/release/PR/stage/commit command was run. No production parser replacement, `FundDocumentRepository` behavior change, source policy change, field correctness claim, source-truth claim, taxonomy claim, readiness claim or repository integration is made.

Worker self-check: pass. Current role is evidence worker, not controller; writes are limited to the authorized artifact set; no PR/push/stage/commit or next review gate was entered.

## 2 Source Truth Boundaries

- `docs/design.md` keeps pdfplumber as current production parser baseline: `pdfplumber -> raw_text / tables -> locate_sections -> ParsedAnnualReport -> extractor -> EvidenceAnchor`.
- Docling is candidate full-document representation evidence only. Its JSON/Markdown is not a fund fact source truth and cannot bypass extractor, `EvidenceAnchor`, or fail-closed validation.
- EID HTML render is candidate structured disclosure locator evidence only where same-report availability is proven. It is not raw XML/XBRL instance proof, field correctness proof or taxonomy proof.
- Existing `004393 / 2025` EID source metadata inside parsed cache is used only as local provenance for the pdfplumber representation artifact.

## 3 Artifact Inventory

| Artifact | Status | Bytes | Notes |
|---|---:|---:|---|
| `reports/representation-json/004393_2025_docling_full.json` | `FULL_LOCAL_DOCLING_ARTIFACT_REPRESENTATION_JSON_NOT_READY` | 4780505 | Derived from existing Docling Route A JSON and summaries; Docling conversion was not rerun. |
| `reports/representation-json/004393_2025_pdfplumber_full.json` | `LOCAL_PDFPLUMBER_FULL_EXPORT_FROM_EXISTING_PDF_AND_PARSED_CACHE_NOT_READY` | 6335018 | Derived no-live from existing local PDF cache and repository parsed cache. |
| `reports/representation-json/004393_2025_eid_html_render_full.json` | `BLOCKED_NEEDS_LIVE_EID_HTML_DISCOVERY_NOT_READY` | 2238 | Blocked because no accepted same-report local HTML render artifact exists and live discovery is not authorized. |

## 4 Docling Full JSON Result

Docling full JSON is available. Summary metrics:

| Metric | Value |
|---|---:|
| page_count | 65 |
| section_count | 13 |
| heading_count | 213 |
| paragraph_count | 457 |
| table_count | 95 |
| cell_count | 3493 |
| has_page_number | True |
| has_bbox | True |
| has_section_tree | True |
| has_table_cell_locator | True |

Result: strongest local full-document representation artifact among the three routes in this gate. It remains candidate representation evidence only.

## 5 Pdfplumber Full JSON Result

Pdfplumber JSON was generated from existing local cache surfaces only:

- `cache/pdf/004393_2025_annual_report_eid.pdf`
- `cache/documents/parsed_reports/004393_2025_annual_report.json`

Summary metrics:

| Metric | Value |
|---|---:|
| page_count | 65 |
| section_count | 8 |
| heading_count | 8 |
| paragraph_count | 65 |
| table_count | 92 |
| cell_count | 3640 |
| has_page_number | True |
| has_bbox | True |
| has_section_tree | True |
| has_table_cell_locator | True |

Result: usable no-live baseline export for comparison, but it is still a generated evidence artifact, not a production `FundDisclosureDocument` schema or parser replacement.

## 6 EID HTML Render Full JSON Result

EID HTML render JSON is blocked: `No accepted same-report 004393 / 2025 EID HTML render artifact is available in the allowed local input set; live/network discovery is not authorized, so no URL is fabricated.`

No HTML URL is fabricated. No live/network discovery was run.

## 7 Coverage Matrix

| Route | Full JSON | Pages | Sections/headings | Paragraph/text blocks | Tables/cells | Provenance locators | Failure taxonomy | Coverage status |
|---|---|---:|---:|---:|---:|---|---|---|
| Docling | yes | 65 | 13/213 | 457 | 95/3493 | page/bbox/self_ref | yes | `FULL_LOCAL_DOCLING_ARTIFACT_REPRESENTATION_JSON_NOT_READY` |
| pdfplumber | yes | 65 | 8/8 | 65 pages + 5540 word blocks | 92/3640 | local PDF path/page/bbox + parsed-cache offsets | yes | `LOCAL_PDFPLUMBER_FULL_EXPORT_FROM_EXISTING_PDF_AND_PARSED_CACHE_NOT_READY` |
| EID HTML render | no | 0 | 0/0 | 0 | 0/0 | absent; no fabricated URL | yes | `BLOCKED_NEEDS_LIVE_EID_HTML_DISCOVERY_NOT_READY` |

## 8 Representation Quality Matrix

| Dimension | Docling | pdfplumber local baseline | EID HTML render |
|---|---|---|---|
| Same-report availability | available from Route A local artifact | available from local PDF/cache | blocked locally |
| Page coverage | 65 pages | 65 pages | not available |
| Section signal | 213 headings, generated section tree | repository parsed cache has 8 located sections | not available |
| Paragraph/text blocks | Docling text blocks with page/bbox | page text + word blocks with bbox | not available |
| Tables | 95 tables with table_cells | pdfplumber detected tables/cells plus repository parsed-cache tables | not available |
| Cell locator | row/col offsets and bbox | row/col locator and bbox where pdfplumber exposes it | not available |
| Source locator | Docling self_ref/page/bbox/source artifact | local PDF path/page/bbox and EID parsed-cache metadata | blocked; no URL fabricated |
| Quality limitation | candidate benchmark only; may wrap/split text | current production parser shape is extractor-oriented, not accepted full-document schema | requires bounded live discovery/evidence gate |

## 9 Blocked / Missing Proofs

- Same-report `004393 / 2025` EID HTML render artifact remains missing under no-live constraints.
- Raw XML direct download, field correctness, raw fact provenance and taxonomy compatibility remain unproven.
- Neither Docling nor pdfplumber JSON is accepted as `FundDisclosureDocument` production schema.
- No source truth, readiness, release, PR, provider/LLM or parser replacement claim is made.

## 10 Route Comparison

Docling gives the richest same-report representation surface in this evidence set: page/bbox locators, headings, text blocks, table cells and content hashes. Pdfplumber gives the current baseline-compatible local export and keeps repository parsed-cache sections/source metadata visible, but its accepted production parser is still field-extractor-oriented rather than a full semantic document object. EID HTML render remains promising as a structured disclosure locator route, but exact same-report local evidence is absent in this handoff.

## 11 Next Gate Recommendation

Recommended next handling:

1. `Pdfplumber Full Representation Export Planning Gate`: decide whether this generated local export shape is sufficient as a repeatable baseline or needs a bounded repository-internal export contract.
2. `Bounded Same-report EID HTML Render Discovery Gate`: authorize exact `004393 / 2025` HTML render discovery only if controller needs same-report HTML comparability.
3. Keep `Hybrid FundDisclosureDocument Candidate Source Planning Gate` as planning-only until candidate source roles, failure taxonomy and projection boundaries are accepted.

## 12 Final Verdict

`VERDICT: PARTIAL_JSON_COMPARISON_ONLY_NOT_READY`
