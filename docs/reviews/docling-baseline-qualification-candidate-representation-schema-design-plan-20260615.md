# Docling Baseline Qualification Candidate Representation Schema Design Plan - 2026-06-15

Status: `READY_FOR_PLAN_REVIEW_NOT_READY`
Gate: `Candidate Representation Schema / Design Planning Gate`
Role: planning worker
Release/readiness: `NOT_READY`

## 1. Goal

Plan a candidate schema/design gate for annual-report document representation after accepted full representation structural evidence.

The goal is to define a code-generation-ready design for a Fund documents internal candidate representation that can compare and normalize:

- `docling_pdf_candidate`;
- `pdfplumber_pdf_candidate`;
- `eid_xbrl_html_render_candidate`.

This design must support future field-family correctness pilots and eventual `FundDisclosureDocument` planning, without changing production parser behavior in this gate.

## 2. Truth Sources

- `AGENTS.md`
- `docs/design.md`
- `docs/implementation-control.md`
- `docs/current-startup-packet.md`
- `docs/reviews/docling-baseline-qualification-full-representation-export-controller-judgment-20260615.md`
- `docs/reviews/docling-baseline-qualification-full-representation-export-evidence-20260615.md`
- `docs/reviews/docling-baseline-qualification-built-in-representation-handler-implementation-controller-judgment-20260615.md`
- `fund_agent/fund/documents/candidates/models.py`
- `fund_agent/fund/documents/candidates/locators.py`
- `fund_agent/fund/documents/candidates/representation_export.py`
- `fund_agent/fund/documents/candidates/representation_handlers.py`
- `fund_agent/fund/extractors/models.py`

Accepted facts:

- Full candidate representation JSONs exist for S1/S4/S5/S6.
- Docling can produce page, heading/section, table and cell locator candidate JSONs for S4/S5/S6.
- pdfplumber can produce page, section and table/cell count candidate JSONs for S4/S5/S6.
- EID HTML render remains blocked for S4/S5/S6 in this evidence chain.
- Current production parser remains `pdfplumber -> ParsedAnnualReport -> extractor`.
- Release/readiness remains `NOT_READY`.

## 3. Non-goals

- No production parser replacement.
- No `FundDocumentRepository` behavior change.
- No source policy change.
- No Eastmoney, fund-company website, CNINFO or non-EID fallback.
- No live/network/EID/FDR/provider/LLM/analyze/readiness/release/PR commands.
- No direct Service/UI/Host/renderer/quality-gate access to candidate representations.
- No field correctness claim.
- No source truth, taxonomy compatibility, raw XML/XBRL, parser replacement, baseline qualification or readiness claim.
- No modification to public `EvidenceAnchor` schema in this planning gate.
- No code implementation in this planning gate.

## 4. Design Problem

Existing candidate internals are Docling-first:

- `CandidateSourceKind = Literal["docling_pdf_candidate"]`;
- `CandidateEvidenceAnchorNote.candidate_source_kind = "docling_pdf_candidate"`;
- table locator helpers assume Docling-shaped table excerpts.

Full representation evidence now needs a broader candidate model:

- Docling has abundant heading/section candidates and bbox-rich table cells.
- pdfplumber has a smaller section-catalog-oriented section set and table cells without bbox.
- EID HTML render can supply URL/DOM/table locators when accepted, but page number is typically unavailable.

The next design must not collapse these differences into one lossy shape. It should define a common candidate envelope plus route-specific locator payloads.

## 5. Proposed Schema Direction

### 5.1 Candidate source kinds

Internal candidate source kind should become a closed enum:

```text
docling_pdf_candidate
pdfplumber_pdf_candidate
eid_xbrl_html_render_candidate
```

This is candidate-internal only. It must not be added to public `EvidenceSourceKind` in this gate.

### 5.2 Common envelope

Define or formalize a common candidate representation envelope:

```text
schema_version
candidate_status
field_correctness_status
source_truth_status
taxonomy_compatibility_status
production_parser_replacement_status
source_kind
sample_id
fund_code
document_year
report_type
input_artifact
summary_metrics
sections
headings
paragraphs
tables
text_blocks
failure_taxonomy
blocked_claims
```

Binding guard values:

```text
candidate_status = not_proven
field_correctness_status = not_proven
source_truth_status = not_proven
taxonomy_compatibility_status = not_proven
production_parser_replacement_status = not_authorized
```

### 5.3 Common section model

Define a route-neutral section candidate shape:

```text
section_id
source_ref
heading_text
heading_path
heading_level
page_span
source_locator
bbox
content_hash
confidence
excluded_reason
normalization_notes
```

Route-specific expectations:

- Docling: section candidates may be abundant and must distinguish body section headings from TOC/furniture/repeated titles.
- pdfplumber: section candidates should map existing section catalog ids and character offsets.
- EID HTML: section candidates should use render URL, DOM id/anchor or heading text path; `page_number=null`.

### 5.4 Common table model

Define a table candidate shape:

```text
table_id
source_ref
route_table_index
section_id
heading_path
page_numbers
source_locator
bbox_by_page
caption
label
row_count
column_count
cell_count
table_family
locator_stability
excluded_reason
failure_code
cells
```

### 5.5 Common cell locator model

Define a cell locator candidate shape:

```text
cell_index
row_start
row_end
column_start
column_end
row_span
column_span
row_label_path
column_header_path
text
normalized_text
bbox
page_number
source_locator
cell_hash
locator_hash
normalization_notes
stability
```

Route-specific expectations:

- Docling cell locator should preserve bbox, row/column offsets, spans and header flags from `tables[*].data.table_cells`.
- pdfplumber cell locator can preserve row/column indexes and headers, but bbox may be `null`.
- EID HTML cell locator can preserve render URL, DOM/table ordinal, row index, row label path, column header path and cell text/hash; page number should remain `null`.

### 5.6 Candidate-to-EvidenceAnchor note

Do not change public `EvidenceAnchor` in this gate.

Plan an internal candidate note that can later be serialized into `EvidenceAnchor.note` only after a separate mapping acceptance gate:

```text
candidate_source_kind
artifact_hash
route_locator
page_number_or_null
section_id_or_heading
table_id
row_locator
column_header_path
row_label_path
cell_hash
locator_hash
field_correctness_status=not_proven
source_truth_status=not_proven
```

This note is weaker than a production `EvidenceAnchor` until field-family correctness and mapping validation pass.

## 6. Baseline Qualification Criteria

Docling can only be considered a baseline candidate after these criteria are accepted:

1. Structural coverage:
   - full JSON export succeeds for S1/S4/S5/S6;
   - page, heading/section, paragraph, table and cell locator dimensions are populated;
   - failures are explicit and fail-closed.
2. Locator stability:
   - headings can be filtered into body section candidates;
   - table cells have stable row/column locators;
   - TOC/furniture/repeated headers are marked or excluded.
3. Field-family pilot:
   - selected fields can be mapped to candidate locators without comparing against production parser shortcuts;
   - at minimum one table-heavy field family and one narrative/section field family should be evaluated.
4. Anchor projection:
   - candidate locator note can map to current `EvidenceAnchor` fields without changing public schema or losing provenance.
5. Boundary compliance:
   - Fund documents internal only;
   - no Service/UI/Host/renderer/quality-gate direct access;
   - no source truth/readiness claim.

## 7. Proposed Implementation Planning Slices

This planning gate should recommend, but not execute, these future slices:

### Slice A: Candidate schema unification plan

Output:

- plan accepted schema names and dataclass/TypedDict targets;
- decide whether to extend existing `models.py` or add route-neutral `representation_models.py`;
- define route-specific payload typing.

### Slice B: Candidate schema no-live implementation

Possible files:

- `fund_agent/fund/documents/candidates/representation_models.py`
- `fund_agent/fund/documents/candidates/representation_projection.py`
- `tests/fund/documents/test_candidate_representation_models.py`
- `tests/fund/documents/test_candidate_representation_projection.py`

Constraints:

- no production exports;
- no full conversion in tests;
- consume committed `reports/representation-json/*` only if tests use small excerpts or generated mini payloads.

### Slice C: Locator stability evidence

Use existing full representation JSONs to measure:

- body heading filtering;
- TOC/furniture exclusion;
- table family classification candidates;
- row/column locator path completeness;
- bbox/page/source locator presence.

### Slice D: Field-family correctness pilot planning

Choose narrow field families:

- table-heavy: fund profile table, fee table, holdings table or manager table;
- narrative: investment strategy / manager discussion section.

This slice should still be planning or evidence-only unless explicitly accepted for implementation.

## 8. Required Reviews

Plan reviewers must check:

- no production parser replacement;
- no public `EvidenceAnchor` schema change;
- no direct Service/UI/Host/renderer/quality gate access;
- no source truth/field correctness/readiness claim;
- candidate source kinds remain internal;
- EID HTML remains candidate render artifact, not raw XBRL;
- baseline criteria do not silently promote Docling.

## 9. Validation Commands For Future Implementation

Potential future implementation gate should run:

```text
uv run pytest tests/fund/documents/test_candidate_representation_models.py tests/fund/documents/test_candidate_representation_projection.py tests/fund/documents/test_docling_no_consumption_guards.py -q
uv run ruff check fund_agent/fund/documents/candidates/representation_models.py fund_agent/fund/documents/candidates/representation_projection.py tests/fund/documents/test_candidate_representation_models.py tests/fund/documents/test_candidate_representation_projection.py
git diff --check
```

No future implementation gate should run live/network/EID/FDR/provider/LLM/analyze/readiness/release/PR commands unless a separate gate explicitly authorizes them.

## 10. Stop Conditions

Stop before implementation if:

- schema requires public `EvidenceAnchor` changes;
- implementation would route Service/UI/Host/renderer/quality gate to candidate representations directly;
- implementation would replace production parser;
- design cannot preserve route-specific locator differences;
- Docling baseline would be claimed without field-family correctness evidence;
- EID HTML route needs live discovery or raw XML proof.

## 11. Next Gate Recommendation

Immediate next gate:

`Candidate Representation Schema / Design Plan Review Gate`

If accepted:

`Candidate Representation Schema No-live Implementation Planning Gate`

Then:

`Candidate Representation Locator Stability Evidence Gate`

Deferred:

- field-family correctness pilot;
- production `FundDisclosureDocument` integration;
- public `EvidenceAnchor` mapping acceptance;
- EID HTML render S4/S5/S6 discovery;
- readiness/release/PR gates.

## 12. Final Verdict

`VERDICT: READY_FOR_PLAN_REVIEW_NOT_READY`
