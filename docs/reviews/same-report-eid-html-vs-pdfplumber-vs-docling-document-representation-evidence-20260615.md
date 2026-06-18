# Same-report EID HTML Render vs Pdfplumber vs Docling Document Representation Evidence

Date: 2026-06-15

Gate: `Same-report EID HTML Render vs Pdfplumber vs Docling Document Representation Evidence Gate`

Role: evidence worker

Status: `EVIDENCE_COMPLETE_NOT_READY`

Final verdict: `HYBRID_OR_NEXT_EVIDENCE_REQUIRED_NOT_READY`

Readiness state: `NOT_READY`

## 1. Scope And Source-of-truth Boundaries

This artifact compares accepted evidence for document representation quality across:

- EID XBRL HTML render candidate evidence;
- current pdfplumber/PDF production surfaces;
- Docling Route A local benchmark output and accepted candidate internals.

The comparison target is `004393 / 2025` where accepted local Docling artifacts exist. EID HTML render evidence is accepted as a route-family candidate, but no accepted same-report EID HTML render artifact for `004393 / 2025` was present in the allowed input set. Current pdfplumber remains the accepted operational production parser path, but no allowed same-report full-document pdfplumber representation artifact for `004393 / 2025` was present beyond current repo/behavior evidence and prior same-report REIT evidence. Therefore this artifact distinguishes same-report observed evidence from route-family or repo facts.

This artifact does not:

- run network, live EID, FDR, PDF body extraction, Docling conversion, provider/LLM, analyze/checklist, golden, readiness, release, PR, push, stage or commit commands;
- read PDF bodies beyond already materialized accepted artifacts;
- modify source, tests, runtime behavior, design docs or control docs;
- change `FundDocumentRepository`, EID single-source policy, fallback behavior, parser selection, `EvidenceAnchor`, `CHAPTER_CONTRACT`, Service, Host, UI, renderer or quality gate behavior;
- claim source truth, field correctness, raw XML/XBRL direct download, taxonomy compatibility, parser replacement, readiness, release readiness, MVP readiness or PR readiness.

Preflight:

| Check | Result |
|---|---|
| Branch | `feat/mvp-llm-incomplete-run-artifacts` |
| Worktree | Existing dirty/untracked workspace observed before this artifact; this worker only writes this artifact. |
| Validation allowed | `git diff --check` after writing only. |

Worker self-check at start: pass. Current role is evidence worker, not controller; assigned gate is evidence only; allowed write set is exactly this artifact; no commit/push/PR or next-gate action is authorized.

## 2. Evidence Inputs

| Input | Classification | Evidence used | Non-proof guard |
|---|---|---|---|
| `AGENTS.md` | repo rule fact | `FundDocumentRepository` is the only annual-report access boundary; pdfplumber is repository-internal; EID single-source/no fallback is current policy. | Does not authorize new source/parser behavior. |
| `docs/design.md` relevant Docling/PDF/EID sections | truth-doc fact | Current production parser is `pdfplumber -> raw_text / tables -> locate_sections -> ParsedAnnualReport -> extractor`; `FundDisclosureDocument` is future candidate; Docling and HTML are candidate inputs only. | Candidate artifacts are not fact truth and cannot bypass extractor/EvidenceAnchor/fail-closed boundaries. |
| `docs/implementation-control.md` current status/gate | truth-doc fact | Current active gate is this same-report evidence gate; scope is evidence only; release/readiness remains `NOT_READY`. | No production integration, parser replacement, source policy change or readiness claim. |
| `docs/current-startup-packet.md` current mainline | truth-doc fact | Mainline confirms current gate follows accepted Docling candidate-internals judgment and requires comparison across HTML render, pdfplumber/PDF and Docling outputs. | Does not override AGENTS/design/control truth. |
| `docs/reviews/csrc-eid-xbrl-html-structured-render-artifact-evaluation-evidence-20260614.md` | accepted evidence | Official EID HTML render pages were reachable for 12 samples; pages contained navigation, headings, table cells, paragraph-like text, byte sizes and content hashes; table locator candidates were partly stable. | Not raw XML, not field correctness, not taxonomy proof, not ordinary non-REIT annual coverage, not source truth, not readiness. |
| `docs/reviews/csrc-eid-xbrl-html-structured-render-artifact-evaluation-evidence-controller-judgment-20260614.md` | accepted evidence | Controller accepted HTML render as partly stable candidate input and rejected parser replacement/readiness claims. | Full narrative/page-number coverage not proven. |
| `docs/reviews/same-report-document-representation-quality-comparison-evidence-20260614.md` | accepted evidence / residual | Prior same-report comparison found EID HTML and pdfplumber partially comparable on REIT annual samples; Docling was blocked by uncontained model download. | Verdict was `INSUFFICIENT_COMPARABLE_EVIDENCE_NOT_READY`; no ordinary non-REIT tri-route winner. |
| `docs/reviews/docling-route-a-local-artifact-conversion-quality-evidence-20260615.md` | accepted evidence | Route A local benchmark for `004393 / 2025` produced 65 pages, 670 text items, 95 tables, 213 headings, all `§1` to `§13` sections, JSON page/bbox/row-col provenance and useful table structures. | Input PDF is user-owned local benchmark artifact, not source truth; model provenance remains benchmark-only. |
| `docs/reviews/docling-funddisclosuredocument-mapping-normalization-no-live-implementation-evidence-20260615.md` | accepted evidence | Candidate internals implemented models, normalization, table locator/stitch/projection helpers, canonical failure mapping and no-consumption guards. | Candidate-only; no production repository behavior change; no field correctness/source truth/parser replacement. |
| `docs/reviews/docling-funddisclosuredocument-mapping-normalization-no-live-implementation-controller-judgment-20260615.md` | accepted evidence | Controller accepted candidate internals with nonblocking residuals and routed this evidence gate next. | Same-report comparison remained deferred; release/readiness remains `NOT_READY`. |
| `reports/docling-route-a/artifact-manifest.json` | candidate artifact | Local artifact manifest records Docling model artifact file counts, byte sizes and hashes for benchmark setup. | Model artifact provenance acceptance is still deferred before production use. |
| `reports/docling-route-a/004393_2025_docling_summary.json` | candidate artifact | `socket_blocked=true`, `do_ocr=false`, `do_table_structure=true`; output has 65 pages, 670 text items, 95 tables, 33 groups, 152718 Markdown chars and JSON/Markdown hashes. | Local benchmark output only; not production source. |
| `reports/docling-route-a/004393_2025_docling_quality_summary.json` | candidate artifact | All `§1` to `§13` sections present; `heading_count=213`; keyword hits include fund basics, financial metrics, manager, strategy, financial statements, portfolio and holder sections. | Section/text presence is representation evidence, not field correctness. |
| `reports/docling-route-a/004393_2025_docling.json` | candidate artifact | `DoclingDocument` JSON contains `texts`, `tables`, `groups`, `pages`; table examples include page provenance, bbox and row/column offsets. | Values are not promoted to facts. |
| `reports/docling-route-a/004393_2025_docling.md` | candidate artifact | Markdown exposes full report heading hierarchy and readable table/text blocks for `004393 / 2025`. | Markdown is not the preferred structured consumption layer and not fact truth. |
| `tests/fixtures/fund/docling_route_a/004393_2025/excerpt.json` | candidate artifact | Minimal excerpt retains Route A hashes, `source_truth_status=not_proven`, `field_correctness_status=not_proven`, `taxonomy_compatibility_status=not_proven`, `production_parser_replacement_status=not_authorized`; table/text provenance retained. | Excerpt hash is descriptive placeholder; fixture is candidate-only. |
| `fund_agent/fund/documents/candidates/*.py` | repo fact / candidate internals | Candidate identity, table locator, anchor note and failure mapping helpers exist under internal candidate package. | Not exported as production document surface. |
| `tests/fund/documents/test_docling_*.py` | repo fact / accepted behavior evidence | Tests bind candidate-only statuses, locator paths/hashes, table stitching accept/reject behavior, no-consumption guards and canonical failure mapping. | No pytest rerun in this worker; relying on accepted implementation judgment. |
| `tests/fund/documents/test_repository.py` | repo fact / accepted behavior evidence | Test asserts `FundDocumentRepository.load_annual_report` has no candidate route, no `load_candidate_document`, no `load_fund_disclosure_document`, and no `docling_pdf_candidate` reference. | Confirms no repository behavior change only. |
| Missing accepted `004393 / 2025` EID HTML render artifact | residual | No same-report HTML render file/metadata was present in allowed inputs. | Blocks EID HTML-only winner for this exact same-report comparison. |
| Missing accepted `004393 / 2025` full pdfplumber document representation artifact | residual | Current parser path is accepted operationally, but allowed inputs do not provide a full same-report pdfplumber document representation quality artifact for `004393 / 2025`. | Blocks pdfplumber-only representation winner. |

## 3. Same-report Comparability Matrix For `004393 / 2025`

| Representation source | Source kind | Coverage signal | Section hierarchy signal | Table structure signal | Locator/provenance signal | Failure class signal | Current reliability classification | Non-proof guard |
|---|---|---|---|---|---|---|---|---|
| EID XBRL HTML render | `eid_xbrl_html_render_candidate` | Route-family evidence: 12 official HTML render samples available and parseable. Same-report `004393 / 2025` HTML render not present in allowed evidence. | Stronger than raw PDF text where available: `instance_navigation`, section headings and anchors were extractable in accepted HTML evidence. Not proven for `004393 / 2025`. | Strong for rendered XBRL table candidates where available; prior samples include row/column locator candidates and HTML table boundaries. | Render URL, section anchor, heading, table ordinal, row label path, column header path, content hash candidates. Page number/bbox absent. | Raw XML, field correctness, taxonomy, ordinary non-REIT annual coverage and full narrative coverage are unproven. Failure mapping still needs future design/implementation for this source. | `partly_stable_route_family_candidate_but_no_004393_same_report_proof` | `not_raw_xml_download_proof`; `not_field_correctness_proof`; `not_taxonomy_compatibility_proof`; `not_source_truth`; `not_readiness_proof`; no parser replacement. |
| Current pdfplumber/PDF path | `current_production_pdf_parser_internal` | Operational path accepted by design/repo: PDF to raw text/tables/sections/extractors. Prior REIT same-report evidence showed pdfplumber can expose raw text and many table objects. No allowed full `004393 / 2025` representation artifact was present. | Current design says `ParsedAnnualReport` is field/extractor input, not full semantic document. Prior same-report REIT evidence showed section indexing can collapse to a coarse section. | Existing path extracts table objects with page/table ordinals, but table hierarchy/merged header semantics are weaker than Docling candidate JSON and HTML render table locators in the accepted evidence. | Strong on PDF page-number provenance and operational parser viability. Weaker on stable section/table semantic locator without extractor-specific rules. | Existing source failure taxonomy is canonical EID single-source: `not_found`/`unavailable` terminal, `schema_drift`/`identity_mismatch`/`integrity_error` fail-closed. | `accepted_operational_path_for_current_extraction_but_not_full_FundDisclosureDocument_representation` | `no_repository_behavior_change`; `no_parser_replacement`; no source truth or field correctness expansion beyond accepted extractor surfaces. |
| Docling Route A full output | `docling_pdf_candidate` | Same-report observed: `004393 / 2025`, 65 pages, 670 text items, 95 tables, 213 headings, all `§1` to `§13` sections present. | Strongest same-report full-document section hierarchy signal in allowed inputs; Markdown and quality summary expose major sections and deep headings. | Strongest same-report table representation signal in allowed inputs; JSON table cells include row/col offsets, spans, header flags, page and bbox. Multi-level headers can duplicate/split; cross-page tables require stitching. | Strong page/bbox/cell-level provenance; candidate internals produce row label path, column header path, cell hash, locator hash and candidate anchor note inside current `EvidenceAnchor.note`. | Candidate failure codes map to canonical source categories only; table missing/provenance/header/stitch issues map to fail-closed categories. | `strongest_same_report_full_document_candidate_but_candidate_only` | `not_source_truth`; `not_field_correctness_proof`; `not_taxonomy_compatibility_proof`; `not_readiness_proof`; `no_repository_behavior_change`; `no_parser_replacement`; model provenance benchmark-only. |
| Docling candidate internals | `docling_pdf_candidate_internal_helpers` | Same-report excerpt-backed no-live helpers cover representative table families from `004393 / 2025`. | Section/paragraph models exist but are not deeply exercised; table/locator path is the stronger accepted behavior. | Locator tests reconstruct portfolio row/header paths, manager holding merged labels, exclude TOC tables, and test compatible/incompatible stitching. | Candidate anchor note retains `docling_pdf_candidate` only inside note while public `EvidenceAnchor.source_kind` stays `annual_report`. | Every candidate failure code maps to canonical categories and introduces no fallback/source expansion. | `accepted_candidate_internal_behavior_not_public_api` | Candidate internals not exported from `fund_agent.fund.documents`; no consumer import; no production route. |

## 4. Route-by-route Findings

### 4.1 EID HTML Render

Accepted evidence supports the HTML render route as a candidate structured disclosure locator source where official render pages are available. Its strongest signal is structured disclosure location: official redirect URL, content hash, navigation anchor, section label, table ordinal, row/column locator and rendered table text.

The evidence is not sufficient to choose EID HTML only:

- accepted HTML samples did not include `004393 / 2025`;
- ordinary non-REIT annual coverage was not proven in the accepted sample window;
- full CHAPTER_CONTRACT narrative coverage was not proven;
- HTML render is not raw XML/XBRL instance proof;
- HTML render lacks PDF page/bbox provenance and current `EvidenceAnchor` page-number semantics without a future schema/projection decision.

Current classification: `keep_as_structured_disclosure_locator_candidate_where_available`.

### 4.2 Pdfplumber / Current PDF Surfaces

Current pdfplumber remains the accepted operational production path because it is already encapsulated inside `FundDocumentRepository` and feeds `ParsedAnnualReport`, self-authored extractors and current `EvidenceAnchor` outputs.

The evidence is not sufficient to choose pdfplumber only for future `FundDisclosureDocument` representation:

- design truth says `ParsedAnnualReport` is oriented to accepted fields and anchors, not a complete semantic document;
- prior same-report evidence showed pdfplumber can provide page/table objects but may have weaker section-navigation identity;
- no allowed same-report full-document representation artifact for `004393 / 2025` was present in this worker input set;
- choosing pdfplumber only would leave the annual-report document representation design gap open.

Current classification: `retain_as_production_operational_path_and_baseline`.

### 4.3 Docling Route A / Candidate Internals

Docling has the strongest same-report full-document representation signal for `004393 / 2025` in the allowed evidence:

- all major annual-report sections `§1` through `§13` are present;
- `heading_count=213`;
- output contains 95 tables and 670 text items over 65 pages;
- JSON preserves page/bbox provenance and table cell row/column offsets;
- candidate internals can form row label paths, column header paths, cell hashes, locator hashes and candidate notes;
- no-consumption tests preserve production boundaries.

The evidence is not sufficient to choose Docling only:

- Route A input is a user-owned local benchmark PDF, not accepted EID source truth;
- values are not field correctness proof;
- model artifact provenance is not production accepted;
- candidate section/paragraph mapping is modeled but not deeply exercised;
- no production repository route is authorized;
- no consumer integration is authorized.

Current classification: `strong_candidate_for_full_document_representation_not_production_parser`.

## 5. Route Decision Sufficiency

| Decision option | Evidence sufficiency | Reason |
|---|---|---|
| Choose EID HTML only | `NO_NOT_READY` | Structured disclosure locator signal is strong where available, but same-report `004393 / 2025`, ordinary non-REIT annual coverage, full narrative/PDF replacement, raw XML, field correctness and taxonomy proof are absent. |
| Choose Docling only | `NO_NOT_READY` | Strongest same-report full-document signal for `004393 / 2025`, but source truth, model provenance, production repository route and field correctness are not proven. |
| Choose pdfplumber only | `NO_NOT_READY` | Current operational path remains accepted, but it is field/extractor-oriented and not proven as full `FundDisclosureDocument` representation. |
| Choose hybrid/next evidence | `YES_FOR_PLANNING_NOT_READY` | Evidence supports a hybrid candidate-source planning gate: pdfplumber remains production baseline, Docling supplies candidate full-document PDF representation, and EID HTML render supplies candidate structured disclosure locators where same-report availability is proven. |

## 6. Blocked Proofs And Residuals

Required guard labels:

- `not_raw_xml_download_proof`: no concrete raw XML/XBRL instance endpoint was proven in this worker scope; HTML render remains rendered HTML.
- `not_field_correctness_proof`: no route value was validated against authoritative field definitions or independent source in this worker scope.
- `not_taxonomy_compatibility_proof`: no `schemaRef`, DTS, namespace, context/unit or cross-year taxonomy compatibility proof exists here.
- `not_source_truth`: HTML render, Docling JSON/Markdown and local benchmark PDF outputs are candidate representation inputs only until accepted extractor/projection/EvidenceAnchor/fail-closed gates promote specific facts.
- `not_readiness_proof`: release/readiness remains `NOT_READY`.
- `no_repository_behavior_change`: `FundDocumentRepository.load_annual_report()` has no candidate route and no candidate public method in accepted tests.
- `no_parser_replacement`: production parser remains current pdfplumber path; Docling and HTML render remain candidate inputs.

Residuals:

| Residual | Status | Next handling |
|---|---|---|
| Same-report EID HTML render for `004393 / 2025` | `OPEN` | Need a future bounded no-live/live-authorized discovery/evidence gate if route-strength comparison requires this exact HTML artifact. |
| Ordinary non-REIT annual HTML render coverage | `OPEN` | Same as above; current accepted HTML annual sample window was REIT annual. |
| Raw XML direct download | `OPEN_BLOCKED` | Separate raw-instance endpoint evidence gate only if a public endpoint is discovered. |
| Field correctness | `OPEN` | Future extractor/projection validation gate using accepted source identity and independent checks. |
| Taxonomy compatibility | `OPEN_BLOCKED` | Future taxonomy evidence gate; not derived from rendered HTML. |
| Docling model artifact provenance | `OPEN` | Future model artifact provenance acceptance gate before production use. |
| Docling section/paragraph mapping depth | `OPEN` | Future section/paragraph mapping evidence or implementation gate. |
| Docling table continuation/header normalization | `OPEN` | Candidate source planning and table-family pilot should define accept/reject rules. |
| Pdfplumber full-document representation baseline for `004393 / 2025` | `OPEN` | Future no-live baseline artifact could materialize current parser section/table/text representation without changing production behavior. |
| Candidate source-kind / EvidenceAnchor schema decision | `OPEN` | Future schema/projection decision gate if candidate notes need a public source-kind or stable note contract. |

## 7. Primary Recommendation And Deferred Entries

Primary recommendation:

Proceed to a `Hybrid FundDisclosureDocument Candidate Source Planning Gate` that explicitly designs a candidate document representation strategy with three bounded roles:

1. current pdfplumber/PDF path remains the production operational baseline and page-number anchor source;
2. Docling remains a candidate full-document PDF representation source for section hierarchy, page/bbox provenance and table-cell locator candidates;
3. EID HTML render remains a candidate structured disclosure locator source only where same-report official render availability is proven.

The planning gate must preserve EID single-source/no-fallback semantics, candidate-only status, repository encapsulation and `NOT_READY`, and must decide whether the next implementation slice is a narrow same-report extraction projection pilot or a broader candidate source schema/projection slice.

Deferred entries:

- same-report `004393 / 2025` EID HTML render discovery/evidence gate;
- ordinary non-REIT annual/interim HTML render coverage gate;
- Docling model artifact provenance acceptance gate;
- Docling fixture-integrity hardening gate;
- pdfplumber same-report baseline materialization gate;
- candidate `EvidenceAnchor` note/source-kind schema decision gate;
- extractor projection over candidate document representation planning gate;
- raw XML endpoint proof gate only if a public endpoint is discovered;
- field correctness validation gate;
- taxonomy compatibility gate;
- readiness/release/PR gates.

## 8. Completion Self-check

Self-check: pass.

- Current gate/role: evidence worker for same-report representation evidence; no controller action taken.
- Source of truth: read AGENTS, relevant design sections, current control/status, current startup mainline, accepted input artifacts and allowed candidate artifacts/tests/source.
- Scope boundary: wrote only this artifact; no source/tests/runtime/control docs changed.
- Stop conditions: no blocker requiring live/network/PDF/Docling conversion was encountered; evidence gaps are recorded as residuals.
- Evidence and validation: artifact complete; required validation is `git diff --check`.
- Next action: stop after validation; do not stage, commit, push, PR or enter review gate.
