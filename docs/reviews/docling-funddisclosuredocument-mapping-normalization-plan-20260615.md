# Docling FundDisclosureDocument Mapping And Normalization Plan

Date: 2026-06-15

Gate: `Docling FundDisclosureDocument Mapping And Normalization Planning Gate`

Role: planning worker

Readiness state: `NOT_READY`

Verdict: `PLAN_READY_FOR_REVIEW_NOT_READY`

## 1. Scope / Motivation

This artifact plans how the accepted Route A local Docling output can be used as no-live implementation-planning input for candidate `FundDisclosureDocument` and `EvidenceAnchor` mapping.

The motivation is narrow:

- Route A proved a local, socket-blocked Docling conversion can produce a full-content `DoclingDocument` JSON for `004393 / 2025`.
- Current production parsing remains `pdfplumber -> ParsedAnnualReport -> extractor -> EvidenceAnchor / CHAPTER_CONTRACT / audit / report`.
- Current `ParsedAnnualReport` is not a complete annual-report document representation.
- Future `FundDisclosureDocument` planning needs explicit mapping, normalization, source ownership, failure classes and no-consumption guardrails before any implementation-planning worker touches code.

This planning gate does not implement code, tests, runtime behavior, parser integration, repository behavior, source policy, Service/UI/Host/renderer/quality gate behavior, LLM route, readiness, release or PR state.

## 2. Evidence Reviewed

Required evidence read:

- `AGENTS.md`
- `docs/design.md`, Docling / `FundDisclosureDocument` / `EvidenceAnchor` / EID XBRL HTML render sections
- `docs/implementation-control.md`, `Current Truth Guardrails` and `Current Gate`
- `docs/current-startup-packet.md`, `Current Mainline` and `Resume Checklist`
- `docs/reviews/docling-route-a-local-artifact-conversion-quality-evidence-20260615.md`
- `reports/docling-route-a/004393_2025_docling_quality_summary.json`
- `reports/docling-route-a/artifact-manifest.json`
- `docs/reviews/funddisclosuredocument-candidate-source-schema-plan-20260614.md`
- `docs/reviews/funddisclosuredocument-candidate-source-schema-plan-controller-judgment-20260614.md`

Additional static structure check, read-only and no conversion:

- `reports/docling-route-a/004393_2025_docling.json`, limited to existing JSON keys and representative `texts` / `tables[].data.table_cells` shape.

No Docling conversion, PDF parser, EID/FDR/network, provider, LLM, analyze, checklist, golden, readiness, release, PR, stage, commit, push or PR command was run for this planning artifact.

## 3. Current Accepted Facts And Non-Proofs

Accepted facts:

- Current active gate is `Docling FundDisclosureDocument Mapping And Normalization Planning Gate`.
- Gate classification is `standard`.
- Route A local benchmark succeeded for `004393 / 2025` with `docling_version=2.93.0`, repo-local `cache/docling-artifacts`, `do_ocr=false`, `do_table_structure=true`, CPU, socket-blocked runtime and offline HuggingFace/Transformers flags.
- Conversion produced JSON and Markdown artifacts, 65 pages, 670 text items, 95 tables, 4 pictures, 33 groups, 213 Markdown headings and all `§1` through `§13` headings present.
- Docling JSON exposes document-level keys including `origin`, `pages`, `texts`, `tables`, `groups`, `body`, `pictures`, `furniture`, `form_items` and `key_value_items`.
- `texts` entries expose `label`, optional `level`, `text`, `orig`, `prov[].page_no`, `prov[].bbox` and `self_ref`.
- `tables` entries expose `self_ref`, `label`, `prov`, `captions`, `footnotes`, `parent`, `children` and `data`.
- `tables[].data` exposes `num_rows`, `num_cols`, `grid` and `table_cells`.
- `table_cells` expose `bbox`, `row_span`, `col_span`, `start_row_offset_idx`, `end_row_offset_idx`, `start_col_offset_idx`, `end_col_offset_idx`, `text`, `column_header`, `row_header`, `row_section` and `fillable`.
- Representative useful tables include stock detail table `table_index=74`, page 53, 38 rows, 6 cols; industry table `table_index=72`, page 52, 21 rows, 4 cols; manager holding table `table_index=86`, page 60, 7 rows, 3 cols.

Non-proofs:

- The local user-owned PDF benchmark is not source truth.
- Docling output is not field correctness proof.
- Docling output is not raw XML/XBRL proof.
- Docling output is not taxonomy compatibility proof.
- Docling output is not current production parser replacement.
- Docling output is not readiness, release or PR proof.
- The local model artifact manifest is provenance evidence for the benchmark only; it is not production model provenance acceptance.
- `换手率=0` keyword evidence is not a Docling failure in this context and is not a route to infer missing regulatory coverage.

## 4. Candidate Source Classification

Recommended candidate source kind:

```text
docling_pdf_candidate
```

Classification:

- `docling_pdf_candidate` is a candidate-only source classification for a Fund documents-layer representation derived from a PDF through Docling.
- It is not a current `EvidenceAnchor.source_kind` production fact.
- It is not a current production annual-report source policy.
- It must not be added to current production renderer/audit/source-label behavior in this gate.
- It must not be used by Service, UI, Host, renderer or quality gate directly.

Ownership:

- Candidate acquisition, parsing, normalization, cache metadata and failure classification must remain inside `fund_agent/fund/documents` and behind `FundDocumentRepository` boundaries if later implemented.
- Service/UI/Host/renderer/quality gate must continue to consume only accepted typed domain outputs, not PDF files, Docling artifacts, parser cache or parser helpers.

Relation to current source policy:

- Current production annual-report source policy remains EID single-source, no fallback.
- `docling_pdf_candidate` does not authorize Eastmoney, CNINFO, fund-company website, CDN or other fallback.
- It also does not alter accepted `eid_xbrl_html_render_candidate` planning. It is a parallel candidate document-representation input for later comparison or hybrid planning, not a replacement for current EID HTML render route evidence.

## 5. Candidate FundDisclosureDocument Mapping

### 5.1 Artifact Identity

Candidate `FundDisclosureDocument` identity should include:

- `source_kind`: `docling_pdf_candidate`
- `document_kind`: `annual_report_candidate`
- `fund_code`: required from trusted caller or repository identity, not inferred from Docling text alone
- `fund_name`: candidate value from title/text, with identity check status
- `report_year`: required from trusted caller or repository identity, cross-checked against cover text
- `report_type`: `annual_report`
- `input_pdf_filename`: from `origin.filename`
- `input_pdf_mimetype`: from `origin.mimetype`
- `input_pdf_binary_hash`: from `origin.binary_hash`, with explicit note that Docling's integer hash is not the same as accepted source/content SHA256 unless separately computed
- `docling_schema_name`
- `docling_version`
- `docling_artifact_manifest_ref`: path plus manifest hash if later accepted
- `conversion_config`: `do_ocr=false`, `do_table_structure=true`, CPU/offline/socket-blocked flags if carried from Route A metadata
- `docling_json_sha256`: Route A JSON hash
- `markdown_sha256`: Route A Markdown hash, diagnostic only
- `created_at` / `converted_at`
- `source_truth_status`: fixed `not_proven`
- `field_correctness_status`: fixed `not_proven`
- `taxonomy_compatibility_status`: fixed `not_proven`
- `production_parser_replacement_status`: fixed `not_authorized`

Identity failure classes:

- `candidate_identity_missing`: required fund/year/report identity unavailable from trusted repository input.
- `candidate_identity_mismatch`: trusted fund/year/report identity conflicts with title or cover metadata.
- `candidate_artifact_hash_missing`: Docling JSON or source PDF hash absent.
- `candidate_artifact_hash_mismatch`: expected hash differs from fixture/excerpt metadata.
- `candidate_schema_version_unsupported`: Docling JSON schema/version lacks required keys.

Canonical mapping for later planning:

- missing matching annual report under the current EID source remains `not_found`;
- inaccessible candidate artifact in a no-live fixture setup maps to `unavailable`;
- unsupported JSON schema, missing required table/text/provenance keys or unstable layout contract maps to `schema_drift`;
- fund/year/report identity conflict maps to `identity_mismatch`;
- hash mismatch or truncated/corrupt JSON maps to `integrity_error`.

### 5.2 Section Hierarchy

Input signals:

- `texts[].label == "section_header"`
- `texts[].level`
- `texts[].text`
- `texts[].prov[].page_no`
- `texts[].prov[].bbox`
- heading patterns such as `§8 投资组合报告`, `8.3 ...`, `7.4.7.1 ...`
- table-of-contents rows from early `document_index` tables, but only as navigation hints

Candidate section record:

- `section_id`: canonical annual-report id, for example `§8`, `8.3`, `7.4.7.1`
- `heading_text_raw`
- `heading_text_normalized`
- `heading_path`: ordered labels from top-level section to current heading
- `heading_level`: from Docling when reliable, otherwise derived from heading pattern
- `start_page_no`
- `end_page_no`: derived from next section start minus one, never inferred past document end without proof
- `start_ref`: Docling `self_ref`
- `start_bbox`
- `section_source`: `docling_heading`, `toc_hint`, or `derived_pattern`
- `section_confidence`: `strong`, `usable`, `weak`, `blocked`
- `normalization_notes`

Rules:

- Prefer body headings over table-of-contents entries.
- Use table-of-contents entries only to reconcile missing page spans, not as section content.
- Treat duplicate heading text as separate section records when section ids differ.
- Fail closed with `section_hierarchy_unstable` if a table or paragraph cannot be assigned to exactly one section path.

### 5.3 Page Spans

Candidate page-span mapping:

- `DocumentPageSpan(start_page_no, end_page_no, source_refs, confidence)`
- for headings, use heading `prov[].page_no`;
- for paragraphs and tables, use the union of their provenance page numbers;
- for cross-page stitched tables, preserve all contributing page numbers and original table refs.

Rules:

- PDF `page_no` is 1-based Docling page provenance and should be preserved as candidate PDF page number.
- `page_number` in current `EvidenceAnchor` projection may use Docling `page_no` only after the candidate field/cell projection is accepted.
- Page headers/footers should not expand section spans.
- Cover page and table-of-contents pages should be classified separately and excluded from body-section evidence unless explicitly referenced.

Failure classes:

- `page_provenance_missing`
- `page_span_overlap_unresolved`
- `section_page_span_unstable`
- `cross_page_table_span_unconfirmed`

### 5.4 Paragraph Blocks

Candidate paragraph block:

- `block_id`: stable from Docling `self_ref` plus content hash
- `block_type`: `paragraph`, `heading`, `note`, `list_item`, `caption`, `footnote`, `header_footer_candidate`
- `section_id`
- `heading_path`
- `page_no`
- `bbox`
- `text_raw`
- `text_normalized`
- `charspan`
- `content_hash`
- `normalization_applied`
- `excluded_reason`, nullable

Mapping rules:

- `texts[]` with `label == "text"` can map to paragraph blocks when assigned to a section.
- `section_header` maps to section metadata and may also remain as a heading block for traceability.
- `furniture` and repeated page artifacts should be candidates for header/footer exclusion.
- paragraph blocks are extractor input candidates only; they are not facts until self-owned extractor/projection validates them.

Failure classes:

- `paragraph_section_unassigned`
- `paragraph_text_empty_after_normalization`
- `paragraph_header_footer_ambiguous`
- `paragraph_order_unstable`

### 5.5 Table Blocks

Candidate table block:

- `table_id`: `docling:t{table_index}` or `docling:t{table_index}:stitched:{group_id}` for stitched tables
- `docling_self_ref`
- `section_id`
- `heading_path`
- `caption_refs`
- `caption_text_normalized`
- `page_numbers`
- `bbox_by_page`
- `num_rows`
- `num_cols`
- `raw_table_cells`
- `normalized_cells`
- `header_rows`
- `body_rows`
- `row_count`
- `column_count`
- `table_family`: candidate value such as `financial_metrics`, `financial_statement`, `portfolio_holding`, `manager_profile`, `holder_info`, or `unknown`
- `continuation_group_id`, nullable
- `locator_stability`: `strong`, `usable`, `weak`, `blocked`
- `failure_class`, nullable

Mapping rules:

- Use `tables[].data.table_cells`, not Markdown tables, as the primary structured input.
- Table-of-contents tables should be classified as `document_index` and excluded from field extraction.
- A table belongs to the nearest preceding body section whose page span contains the table provenance, unless a caption/heading ref gives stronger assignment.
- Tables with the same caption/header family across consecutive pages may be stitched only when continuation rules pass.
- Table `bbox` at table level and cell `bbox` must both be preserved.

Failure classes:

- `table_cells_missing`
- `table_provenance_missing`
- `table_section_unassigned`
- `table_header_unstable`
- `table_shape_inconsistent`
- `table_continuation_ambiguous`
- `table_toc_or_furniture_excluded`

### 5.6 Table Cell Locators

Candidate table cell locator:

- `table_id`
- `source_table_index`
- `source_table_self_ref`
- `page_no`
- `cell_bbox`
- `row_span`
- `col_span`
- `start_row_offset_idx`
- `end_row_offset_idx`
- `start_col_offset_idx`
- `end_col_offset_idx`
- `row_index_normalized`
- `column_index_normalized`
- `text_raw`
- `text_normalized`
- `column_header`
- `row_header`
- `row_section`
- `row_label_path`
- `column_header_path`
- `cell_hash`
- `locator_hash`
- `normalization_notes`

Locator rules:

- `row_label_path` is built from row-header cells, row-section cells and left-side label columns in the same logical row.
- `column_header_path` is built from all applicable header cells above the target cell after merged-cell expansion and duplicate-header collapse.
- For simple holdings tables, expected `column_header_path` examples include `["股票代码"]`, `["股票名称"]`, `["数量（股）"]`, `["公允价值（元）"]`, `["占基金资产净值比例（%）"]`.
- For financial statements, expected `column_header_path` examples include period headers such as `["本期末 2025年12月31日"]` and `["上年度末 2024年12月31日"]`.
- `cell_hash` should hash normalized text plus row/column locator context, not text alone.
- `locator_hash` should hash source kind, document identity, section id, table id, page, row label path, column header path and cell bbox bucket.

Failure classes:

- `cell_text_empty`
- `cell_bbox_missing`
- `cell_header_path_missing`
- `cell_row_label_path_missing`
- `cell_span_conflict`
- `cell_locator_unstable`

## 6. Candidate EvidenceAnchor Projection Strategy

Current `EvidenceAnchor` schema must not be changed in this gate.

Current fields:

- `source_kind`
- `document_year`
- `section_id`
- `page_number`
- `table_id`
- `row_locator`
- `note`

Projection recommendation:

- Keep `docling_pdf_candidate` inside the candidate representation layer for now.
- Do not add `docling_pdf_candidate` to current production `EvidenceAnchor.source_kind` in this gate.
- Later no-live implementation planning may include candidate-only projection fixtures that demonstrate how a validated table cell would become an `EvidenceAnchor`, but those fixtures must be explicitly non-production.

Candidate projection fields:

| Candidate locator field | Current `EvidenceAnchor` projection |
|---|---|
| `source_kind=docling_pdf_candidate` | candidate-only; not current production `EvidenceAnchor.source_kind` support |
| `report_year` | `document_year` |
| `section_id` | `section_id` |
| PDF `page_no` | `page_number` |
| `table_id` | `table_id` |
| `row_label_path` | `row_locator`, encoded as path text such as `项目/本基金基金经理持有本开放式基金/安信企业价值优选混合A` |
| `column_header_path` | preserve in `note` |
| `bbox` | preserve in `note` |
| `cell_text_normalized` | preserve in `note` only for traceability; not field correctness proof |
| `cell_hash` / `locator_hash` | preserve in `note` |
| `normalization_notes` | preserve in `note` |

Recommended `note` shape for later fixture planning:

```json
{
  "candidate_source_kind": "docling_pdf_candidate",
  "source_table_ref": "#/tables/74",
  "page_no": 53,
  "bbox": {"l": 116.4, "t": 167.99, "r": 150.42, "b": 176.29, "coord_origin": "TOPLEFT"},
  "row_offsets": [1, 2],
  "col_offsets": [1, 2],
  "row_label_path": ["1"],
  "column_header_path": ["股票代码"],
  "cell_text": "00939",
  "cell_hash": "...",
  "locator_hash": "...",
  "normalization": ["numeric_token_repair_if_needed", "chinese_space_repair_if_needed"],
  "source_truth_status": "not_proven",
  "field_correctness_status": "not_proven"
}
```

Projection stop rule:

- If `section_id`, `page_number`, `table_id`, `row_locator`, `column_header_path`, `bbox` or locator hash cannot be constructed deterministically, do not project an anchor. Emit a candidate failure and let extractor/projection fail closed.

## 7. Normalization Plan

Normalization must be deterministic, fixture-based and auditable. It must keep both raw and normalized values.

### 7.1 Chinese Space Repair

Problems observed:

- Chinese words are split by inserted spaces, for example `基 金 经 理`.
- Line wrapping splits phrases, for example `供 应业`.
- Keyword matching fails for phrases such as `本基金基金经理持有本开放式基金` when Docling emits `本基金基金经理持有 本开放式基金`.

Plan:

- Remove ASCII spaces between adjacent CJK characters by default.
- Preserve spaces between Latin tokens, ticker-like tokens and units where meaningful.
- Preserve spaces around dates only when needed to avoid merging unrelated tokens; normalize `2025 年 12 月 31 日` to `2025年12月31日` for locator matching.
- Store applied rules in `normalization_notes`.

Tests later:

- fixture cases for CJK-CJK space deletion;
- date normalization;
- mixed CJK/Latin/token preservation;
- whitespace-insensitive keyword lookup.

### 7.2 Numeric Token Repair

Problems observed:

- Number tokens are split, for example `33,984,439 .75` and `154,973,70 4.60`.
- Period headers can split year/month/day tokens.

Plan:

- Repair spaces inside numeric tokens only when both sides match numeric punctuation grammar.
- Normalize comma-grouped decimals to a canonical string while preserving original text.
- Do not coerce to `Decimal` in document normalization; numeric parsing belongs to later extractor validation.
- Mark ambiguous numeric repairs as `numeric_repair_ambiguous` and block field projection.

Tests later:

- `33,984,439 .75 -> 33,984,439.75`
- `154,973,70 4.60 -> 154,973,704.60`
- negative numbers and percentages;
- no repair across unrelated adjacent numbers.

### 7.3 Multi-Level Header Reconstruction

Plan:

- Identify header cells by `column_header=true`, top rows, row/col spans and repeated header labels.
- Expand merged header cells across their covered column range.
- Build `column_header_path` from top header row to leaf header cell.
- Collapse duplicate adjacent labels while preserving period/date labels.
- If header paths differ across stitched pages, mark table `table_header_unstable`.

Tests later:

- simple one-row holdings headers;
- period comparison headers;
- manager table with nested tenure columns;
- financial statement headers with current/prior periods.

### 7.4 Repeated Header Deduplication

Plan:

- Detect repeated header rows inside table body by comparing normalized row text to canonical header row signatures.
- Remove repeated header rows from `body_rows`, but preserve original row refs in `excluded_rows`.
- Never drop a row if any non-header cell contains business values not present in the header signature.

Tests later:

- repeated header in Markdown-derived quality examples;
- repeated page header after cross-page split;
- false-positive guard where a body row text resembles a header.

### 7.5 Cross-Page Table Stitching

Plan:

- Stitch only consecutive tables when all conditions pass:
  - adjacent or near-adjacent pages;
  - same section path or explicit continuation section;
  - same table family;
  - compatible column count after normalization;
  - compatible `column_header_path`;
  - no intervening body heading that starts a different table family;
  - continuation caption/header is identical or absent.
- Preserve every original `source_table_index`, `self_ref`, page number and bbox.
- Assign `table_id=docling:t{first_index}:stitched:{hash}`.

Tests later:

- accepted continuation fixture;
- reject incompatible column count;
- reject changed heading path;
- reject ambiguous financial statement continuation.

### 7.6 Merged Cell Handling

Plan:

- Use `row_span`, `col_span`, `start/end_row_offset_idx` and `start/end_col_offset_idx` to expand logical grid coverage.
- Forward-fill merged row labels only inside the merged span.
- Forward-fill merged column headers only inside the merged span.
- Record `merged_cell_source_ref` for every derived cell.
- Block projection when span coverage overlaps incompatibly.

Tests later:

- manager holding table row group;
- multi-share-class metrics table;
- financial statement row sections;
- overlapping span conflict.

### 7.7 Directory / Page Header / Footer Exclusion

Plan:

- Classify table-of-contents tables as `document_index` when early-page tables contain section ids, dotted leaders and page numbers.
- Exclude cover metadata, page headers, page footers and repeated report titles from body paragraph/table extraction.
- Keep excluded blocks in the candidate document with `excluded_reason`, because they may help navigation and provenance.
- Never use table-of-contents text as field facts.

Tests later:

- TOC table `table_index=0` and `table_index=1` excluded from field extraction;
- body heading retained;
- repeated report title excluded;
- note/caption not incorrectly excluded.

### 7.8 Row Label Path And Column Header Path Generation

Row label path:

- build from row-section cells, row-header cells and left label columns;
- normalize text;
- remove empty labels;
- preserve hierarchy order;
- include row ordinal only when label path is absent or non-unique;
- block projection if label path remains non-unique after ordinal fallback.

Column header path:

- build from expanded header cells above the target cell;
- normalize text;
- remove duplicate spanning labels;
- include units and period/date labels;
- block projection if leaf header is absent for data cells.

Locator uniqueness:

- candidate cell identity is unique only when `(document_identity, section_id, table_id, page_no, row_label_path, column_header_path, cell_hash)` is unique.
- if not unique, add source row/col offsets; if still not unique, block projection.

## 8. Implementation Slice Recommendations

These are recommendations for the later implementation-planning worker. They are not implementation authorization.

### Slice 0: Fixture Contract And No-Behavior Guard Plan

Plan only:

- choose a small checked-in fixture/excerpt format derived from existing Route A JSON snippets;
- define fixture metadata for document identity, tables, text blocks and expected normalized locators;
- define no-consumption guards that prove Service/UI/Host/renderer/quality gate do not call Docling, PDF, parser cache or candidate artifacts.

No PDF, no Docling conversion, no live source.

### Slice 1: Candidate Model Internals

Plan only:

- candidate identity objects;
- section records;
- page spans;
- paragraph blocks;
- table blocks;
- table cell locators;
- canonical failure mapping.

Models should live under Fund documents ownership if later implemented.

### Slice 2: Normalization Pipeline Internals

Plan only:

- CJK whitespace repair;
- numeric token repair;
- header reconstruction;
- merged-cell expansion;
- repeated-header removal;
- cross-page stitching;
- TOC/header/footer exclusion;
- row label path and column header path generation.

Every rule must be fixture-backed and preserve raw text.

### Slice 3: Candidate EvidenceAnchor Projection Fixture

Plan only:

- demonstrate projection from validated candidate cell locator to current `EvidenceAnchor` fields without modifying current schema;
- store `bbox`, `column_header_path`, `cell_text`, `cell_hash`, `locator_hash` and normalization notes in `note`;
- keep candidate source kind non-production.

### Slice 4: Repository Boundary Non-Behavior Planning

Plan only:

- verify existing `FundDocumentRepository.load_annual_report()` behavior remains unchanged;
- verify candidate objects are not consumed by production extractor, renderer, audit, Service, UI, Host or quality gate;
- verify no fallback/source expansion.

## 9. Validation Matrix For Later No-Live Implementation

The later implementation-planning worker should require fixture/excerpt validation only.

Forbidden in later no-live implementation planning:

- PDF/Docling conversion;
- PDF parser execution;
- EID/FDR/network;
- provider/LLM;
- analyze/checklist;
- golden;
- readiness/release/PR;
- source fallback expansion.

| Validation | Fixture input | Expected proof |
|---|---|---|
| Candidate identity fixture | excerpted `origin`, hashes and Route A metadata | identity fields round-trip; `source_truth_status=not_proven`; no production source policy change |
| Section hierarchy fixture | `texts` heading excerpts for `§1-§13` and nested headings | canonical section ids, heading paths and page spans are deterministic |
| Paragraph block fixture | `texts` body excerpts with page/bbox | paragraphs map to sections or fail closed with explicit failure |
| Table block fixture | representative table excerpts for holdings, industry, manager holding and financial statements | table id, section assignment, page provenance and raw cells preserved |
| Cell locator fixture | `table_cells` excerpts with bbox/header flags/offsets | row label path, column header path, cell hash and locator hash are stable |
| CJK space normalization fixture | split Chinese tokens | normalized text matches expected while raw text is retained |
| Numeric repair fixture | split numeric tokens | deterministic repair or explicit ambiguity block |
| Header reconstruction fixture | single-row and multi-row headers | column header paths reconstructed without duplicate headers |
| Repeated header fixture | body repeated header rows | header rows excluded without dropping business rows |
| Cross-page stitching fixture | consecutive table excerpts | accepted/rejected stitching decisions are deterministic |
| Merged cell fixture | row/col span excerpts | expanded grid keeps source refs and detects conflicts |
| TOC/header/footer exclusion fixture | document index and repeated furniture excerpts | excluded blocks are retained as navigation/provenance, not facts |
| Failure mapping fixture | candidate failures | maps to `not_found`, `unavailable`, `schema_drift`, `identity_mismatch`, `integrity_error` |
| Candidate EvidenceAnchor projection fixture | accepted cell locator | current `EvidenceAnchor` fields can carry page/table/row/note data without schema change |
| Repository behavior unchanged | existing fake repository or static boundary test | `load_annual_report()` behavior unchanged; no candidate route invoked by default |
| No direct parser access | static/fake import boundary checks | Service/UI/Host/renderer/quality gate do not import/call Docling, PDF cache, parser helper or candidate artifacts |

## 10. Stop Conditions

Stop before implementation planning is accepted if any condition holds:

- `docling_pdf_candidate` is treated as current production `EvidenceAnchor.source_kind`.
- The plan requires changing current `EvidenceAnchor` schema before a controller decision.
- The plan lets Service/UI/Host/renderer/quality gate call Docling, PDF, parser cache or candidate artifacts directly.
- Candidate output is described as source truth, field correctness proof, raw XML/XBRL proof, taxonomy proof, parser replacement, readiness or release proof.
- EID single-source/no-fallback policy is changed or bypassed.
- Eastmoney, CNINFO, fund-company website/CDN or other fallback is introduced.
- PDF/Docling conversion, PDF parser, EID/FDR/network, provider/LLM, analyze/checklist/golden/readiness/release/PR commands are required.
- Section hierarchy, table stitching, header reconstruction or locator uniqueness cannot fail closed.
- Candidate failure classes cannot map to canonical source outcomes.
- Implementation worker would still need to invent schema ownership, source kind, locator format, normalization rules or validation boundaries.

## 11. Residual Risks

- Route A is one local sample only, `004393 / 2025`; cross-fund, cross-year and report-type coverage remains unproven.
- Local HuggingFace cache provenance is not production model provenance acceptance.
- Docling JSON schema may drift across versions.
- PDF page provenance is useful for anchors, but not equivalent to source-truth validation.
- Cell text quality is materially useful but still needs extractor validation before becoming field facts.
- Multi-level headers, cross-page stitching and merged cells are likely the highest-risk normalization areas.
- Table-of-contents and repeated headers can create false positives if not excluded before locator generation.
- Same-report comparison across EID HTML render, current pdfplumber and Docling remains deferred.
- Production integration may require a later controller decision on whether `docling_pdf_candidate` becomes an accepted source kind, remains internal candidate metadata, or is only a benchmark representation.

## 12. Next Gate Recommendation

Recommended next gate:

```text
Docling FundDisclosureDocument Mapping And Normalization Plan Review Gate
```

Review focus:

- candidate-only `docling_pdf_candidate` classification;
- preservation of current `EvidenceAnchor` schema;
- completeness of table cell locator and normalization strategy;
- no direct Service/UI/Host/renderer/quality gate parser access;
- fixture/excerpt-only no-live validation matrix;
- preservation of EID single-source/no-fallback policy and `NOT_READY`.

If accepted, the following gate should be:

```text
FundDisclosureDocument Candidate Source No-live Implementation Planning Gate
```

Allowed scope for that later gate should remain planning only unless a controller explicitly authorizes implementation. Consumer integration, source-label behavior, extractor projection, renderer/audit consumption, readiness/release/PR and production parser replacement must remain separate gates.

## 13. Final Verdict

```text
VERDICT: PLAN_READY_FOR_REVIEW_NOT_READY
```
