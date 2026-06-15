# Same-report Document Representation Quality Comparison Plan

Date: 2026-06-14

Verdict: `PLAN_READY_FOR_REVIEW_NOT_READY`

## 1. Scope

Gate: `Same-report Document Representation Quality Comparison Planning Gate`

Role: planning worker.

Goal: produce a handoff-ready evidence plan to compare document representation quality across three candidate routes on identity-matched same-report samples:

1. `eid_xbrl_html_render_candidate`
2. current pdfplumber-based Fund documents parser output
3. Docling candidate output

The comparison target is document representation quality, not raw XBRL truth, field correctness, taxonomy compatibility, source truth, LLM report quality or release readiness.

## 2. Motivation

The current route has accepted that EID XBRL HTML render artifacts are publicly reachable and partly stable as candidate structured render artifacts. It has also accepted that current pdfplumber extraction and future Docling benchmarking are document-layer concerns inside Fund documents / `FundDocumentRepository` boundaries.

The next implementation planning decision is premature without same-report evidence. A candidate source schema should not proceed toward implementation until the controller can compare whether EID HTML render, current pdfplumber and Docling candidate outputs produce materially different section/table/locator quality on the same report identity.

## 3. Source-of-truth Inputs

Read in this order:

1. `AGENTS.md`
2. `docs/design.md`
3. `docs/implementation-control.md`
4. `docs/current-startup-packet.md`
5. `docs/reviews/workspace-artifact-disposition-before-same-report-comparison-20260614.md`
6. `docs/reviews/same-report-document-representation-quality-comparison-control-sync-20260614.md`
7. `docs/reviews/csrc-eid-xbrl-html-structured-render-artifact-evaluation-evidence-20260614.md`
8. `docs/reviews/csrc-eid-xbrl-html-structured-render-artifact-evaluation-evidence-controller-judgment-20260614.md`
9. `docs/reviews/funddisclosuredocument-candidate-source-schema-plan-controller-judgment-20260614.md`
10. `docs/reviews/annual-report-document-representation-docling-benchmark-plan-controller-judgment-20260614.md`

Evidence-chain artifacts are inputs only. They do not override `AGENTS.md`, `docs/design.md`, `docs/implementation-control.md` or `docs/current-startup-packet.md`.

## 4. Non-goals

- Do not implement code.
- Do not run parsers.
- Do not download PDFs.
- Do not run live/provider/LLM/analyze/checklist/golden/readiness/release/PR/push/merge commands.
- Do not install Docling or add dependencies.
- Do not add a Docling adapter.
- Do not modify `FundDocumentRepository`.
- Do not modify source policy, fallback policy, extractor, renderer, audit, source-label, CHAPTER_CONTRACT, EvidenceAnchor schema, Service, Host, UI or quality gate.
- Do not promote EID HTML render to source truth.
- Do not call EID HTML render raw XML or raw XBRL.
- Do not claim raw XML download, field correctness, taxonomy compatibility, source truth, production parser replacement, LLM readiness, MVP readiness or release readiness.
- Do not stage, commit, push or create PR.
- Do not use arbitrary untracked residue as proof.

## 5. Required Planning Question

The evidence gate must answer:

```text
For the same fund/report identity, which route produces the most stable and auditable document representation for sections, tables, text blocks and locator candidates?
```

It must not answer:

```text
Which route proves the disclosed fact is correct?
Which route should replace production parsing?
Is the system ready?
```

## 6. Route Definitions

| Route | Input identity | Output to compare | Hard caveat |
|---|---|---|---|
| `eid_xbrl_html_render_candidate` | Official EID JSON row plus `instance_html_view` redirect and final `/xbrl/REPORT/HTML/...html` URL | Rendered section/navigation labels, table structure, row/column locator candidates, text block samples, content hash | Not raw XML, not field correctness proof, no PDF page number |
| `pdfplumber_current` | Same report accessed only through `FundDocumentRepository` / Fund documents parser boundary | Current parsed sections, tables/raw text, parser failure class, existing EvidenceAnchor candidates if emitted | Current extractor coverage is not full-document coverage |
| `docling_candidate` | Same PDF report, only through a bounded benchmark path inside Fund documents boundary | Docling document elements, sections/headings, table blocks, cell coordinates if available, provenance candidates | Candidate only; no dependency install or production adapter in evidence gate |

## 7. Identity Matching Policy

No comparison is valid unless identity match is proven before parsing.

Required identity fields:

| Field | Required? | Notes |
|---|---:|---|
| `fund_code` | yes | Must match across EID JSON/render metadata and PDF route. |
| `fund_name` | yes if available | Normalized name or title comparison; mismatch is fail-closed. |
| `report_year` | yes | Must match target disclosure period, not just send date. |
| `report_type` | yes | Annual, interim, quarterly, temporary announcement or contract announcement. |
| `report_title` | yes if available | Used to detect mismatched report family. |
| `report_send_date` | preferred | Used as supporting identity, not sole identity. |
| EID `idStr` | yes for EID route | Must map to final render URL. |
| PDF repository identity | yes for PDF routes | Must be repository-resolved, not arbitrary direct filesystem access. |
| report-level discriminator | yes | At least one route-comparable discriminator is required: official report title, EID render URL/id, repository source URL/detail id, send/upload date, correction/announcement sequence, or content hash. |

Identity classification:

| Status | Meaning | Action |
|---|---|---|
| `identity_match` | Same fund, year, type and at least one report-level discriminator are consistent across routes. | Eligible for quality comparison. |
| `identity_partly_matched` | Fund/year/type match, but report-level discriminator is incomplete or one route lacks comparable title/date/source/hash metadata. | Eligible only for exploratory notes; cannot decide quality winner. |
| `identity_mismatch` | Any core identity conflict. | Stop for that sample. |
| `identity_not_proven` | Missing EID row, PDF identity or Docling input identity. | Stop for that sample. |

Aggregate identity rule:

- A route-strength verdict requires at least one Tier A `identity_match` sample.
- Mixed exact/partial samples must report per-sample identity status and cannot use partial samples to decide a route winner.
- If all candidate samples are only `identity_partly_matched`, the final verdict must be `PARTIAL_IDENTITY_ONLY_NO_WINNER_NOT_READY`.

## 8. Sample Matrix Design

Minimum evidence gate sample set:

| Tier | Required sample | Purpose | Stop rule |
|---|---|---|---|
| A | 1 ordinary non-REIT annual fund report with EID HTML render and repository-resolved PDF | Primary MVP-like annual report comparison | If no ordinary annual report can be identity-matched, classify as `sample_unavailable` and do not substitute a different type as proof. |
| B | 1 quarterly or interim fund report with EID HTML render and repository-resolved PDF, if repository supports it | Tests periodic disclosure route beyond annual report | If repository does not support this report type, classify as `repository_scope_gap`; do not change repository behavior. |
| C | 1 already accepted EID HTML render sample from prior evidence, even if PDF route is not available | Tests whether previously accepted HTML route remains usable as HTML-only baseline | Not eligible for three-route comparison unless PDF/Docling identity also matches. |

Fallback sample expansion:

- If Tier A cannot be discovered without live access, the evidence gate may use bounded official EID JSON/HTML GET only if explicitly authorized by that evidence gate.
- If local untracked PDFs are considered for Tier A, the gate must first record user authorization for sample use and still route access through a repository-compatible boundary. Direct PDF body reads are not allowed by this planning artifact.
- Docling may only consume a repository-approved document handle or path produced by the Fund documents boundary for the identity-matched report. It may not parse arbitrary local PDF paths, and untracked PDFs remain unavailable unless an evidence gate records explicit user authorization and repository-compatible routing.
- REIT annual reports may be used only as a separate REIT-labeled sample, not as substitute proof for ordinary fund annual reports.

## 9. Comparison Dimensions

Each route/sample row must fill the same matrix:

| Dimension | Measurement | Expected evidence |
|---|---|---|
| Identity | `identity_match_status` and source metadata | fund code, year, type, title, EID idStr, repository identity |
| Artifact reproducibility | content hash / parser version / dependency availability | EID HTML SHA-256, PDF identity hash if available, Docling version if available |
| Section structure | section count, heading path samples, hierarchy depth | 5-10 representative headings, stability class |
| Table structure | table count, table captions/nearby headings, header paths, merged-cell handling | 3-5 target tables per sample if present |
| Cell locator | row label path, row index, column header path, cell text/hash | locator examples for numeric and text cells |
| Text block coverage | paragraph/block count and representative narrative blocks | narrative extraction samples; do not infer full CHAPTER_CONTRACT coverage |
| Provenance | render URL / PDF page-bbox / Docling element path | candidate EvidenceAnchor mapping, not final source truth |
| Failure taxonomy | canonical failure class | `not_found`, `unavailable`, `schema_drift`, `identity_mismatch`, `integrity_error`, plus route-specific diagnostic note |
| Performance metadata | elapsed time and artifact size if collected | diagnostic only; no readiness claim |

Stability classes:

```text
stable
partly_stable
unstable
not_extractable
not_comparable
```

## 10. Target Tables And Blocks

The evidence gate should prefer target blocks that matter to future extractor projection, without validating field correctness:

1. Basic fund identity / report metadata table.
2. Main financial indicators table.
3. Net value / benchmark performance table.
4. Asset allocation / portfolio composition table.
5. Fee / cost table if present.
6. Manager / holder / share change table if present.
7. One narrative risk or investment strategy paragraph block.

For each target, record whether the route can produce:

```text
section_heading
table_heading_or_nearby_heading
table_ordinal_under_section
row_label_path
column_header_path
rendered_text_observed
locator_stability
candidate_anchor_note
not_field_correctness
```

Do not compare extracted values to PDF or call values correct unless a later field-correctness gate authorizes that proof.

## 11. Candidate EvidenceAnchor Mapping

The evidence gate must produce candidate mappings only:

| Route | Candidate anchor mapping |
|---|---|
| EID HTML render | `source_kind=eid_xbrl_html_render_candidate`; `page_number=null`; `note` includes idStr, render URL, redirect location, content hash, report type, source list, section heading, table ordinal, row/column locator and stability class. |
| pdfplumber current | Existing annual-report style anchor if available; include page number/bbox if produced by current parser. |
| Docling candidate | Candidate only; include document element id/path, page span/bbox if available, table/cell path and Docling version; do not write to current `EvidenceAnchor` schema. |

All candidate anchors must be marked as below fact truth until extractor / projection / anchor validation accepts them.

## 12. Evidence Gate Output Artifact

Recommended next artifact:

```text
docs/reviews/same-report-document-representation-quality-comparison-evidence-20260614.md
```

Required sections:

1. Scope
2. Inputs Reviewed
3. Identity Matching Matrix
4. Route Availability Matrix
5. Sample Matrix
6. Section Structure Comparison
7. Table Structure Comparison
8. Cell Locator Comparison
9. Narrative/Text Block Comparison
10. Candidate EvidenceAnchor Mapping
11. Failure Taxonomy
12. Comparative Findings
13. Blocked Proofs And Residuals
14. Next Gate Recommendation
15. Final Verdict

Allowed final verdicts:

```text
VERDICT: HTML_RENDER_STRONGER_FOR_STRUCTURED_TABLES_NOT_READY
VERDICT: PDFPLUMBER_STRONGER_FOR_CURRENT_SCOPE_NOT_READY
VERDICT: DOCLING_STRONGER_FOR_DOCUMENT_REPRESENTATION_NOT_READY
VERDICT: HYBRID_ROUTE_REQUIRED_NOT_READY
VERDICT: IDENTITY_MATCHING_BLOCKED_NOT_READY
VERDICT: PARTIAL_IDENTITY_ONLY_NO_WINNER_NOT_READY
VERDICT: DOCLING_UNAVAILABLE_NOT_READY
VERDICT: INSUFFICIENT_COMPARABLE_EVIDENCE_NOT_READY
```

## 13. Allowed Evidence Gate Commands

This planning gate runs no parsers. The later explicitly authorized evidence gate may define a narrow command list for bounded parser comparison, but must restate exact commands and stop rules before execution. The planning recommendation is:

Allowed without live/network:

```text
git status --short
git status --branch --short
git diff --check
python -c "<bounded importlib/docling availability check only>"
uv run python -m pytest <targeted no-live tests only if an implementation already exists>
```

Allowed only if explicitly authorized inside the evidence gate:

```text
bounded official EID HTTP GET/HEAD for accepted or newly discovered official EID JSON/render URLs
repository-bounded local PDF access through FundDocumentRepository-compatible APIs
bounded Docling local parse on identity-matched sample PDFs if Docling is already installed, no dependency install is needed, and the PDF handle/path is produced by Fund documents / `FundDocumentRepository` ownership for the matched report
current pdfplumber parser execution through Fund documents boundary
```

Forbidden:

```text
curl / DNS / socket / arbitrary network outside accepted official EID URLs
production analyze/checklist/readiness/release/PR commands
provider/LLM commands
direct PDF filesystem body reads outside repository boundary
dependency installation
source/test/runtime behavior changes
```

## 14. Review Focus

Plan review must challenge:

- Whether the plan accidentally treats EID HTML render as raw XML.
- Whether identity matching is strong enough before comparison.
- Whether Docling is allowed only as candidate parser output, not production replacement.
- Whether pdfplumber access stays inside Fund documents / repository boundary.
- Whether local untracked PDFs are being smuggled in as accepted data fixtures.
- Whether field correctness, taxonomy compatibility or readiness is overclaimed.
- Whether the evidence artifact can be written without implementation workers inventing schema, source ownership or route priority.

## 15. Stop Conditions

Stop before evidence execution if any of these is true:

- No same-report identity can be proven.
- The evidence worker would need to change code before comparison.
- The evidence worker would need to install Docling.
- The evidence worker would need to bypass `FundDocumentRepository` / Fund documents boundaries.
- The evidence worker would need to read PDF bodies directly from untracked local files without explicit user authorization and repository-compatible routing.
- EID HTML access requires auth/captcha/manual browser state.
- EID redirects leave official EID domains.
- Comparison requires field correctness, raw XML, taxonomy or readiness claims.

## 16. Next Gate Recommendation

Immediate next gate:

```text
Same-report Document Representation Quality Comparison Plan Review Gate
```

If plan review passes:

```text
Same-report Document Representation Quality Comparison Evidence Gate
```

Only after evidence is accepted may the controller choose one of:

1. `FundDisclosureDocument Candidate Source No-live Implementation Planning Gate`
2. `Docling Candidate Adapter Design Gate`
3. `Hybrid FundDisclosureDocument Representation Design Gate`
4. `Pause HTML/Docling route and return to current pdfplumber/extractor stabilization`

## 17. Final Guardrails

- Preserve `NOT_READY`.
- Preserve EID single-source production source policy.
- Do not reintroduce Eastmoney, fund-company website, CNINFO or other fallback.
- Do not make readiness/release/PR claims.
- Do not change code, tests, runtime behavior, docs outside review artifacts, source policy or parser ownership.
- Do not treat this plan as evidence that any route is superior.

VERDICT: PLAN_READY_FOR_REVIEW_NOT_READY
