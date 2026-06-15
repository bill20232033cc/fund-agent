# Docling FundDisclosureDocument Mapping And Normalization No-live Implementation Plan

Date: 2026-06-15

Gate: `Docling FundDisclosureDocument Mapping And Normalization No-live Implementation Planning Gate`

Role: planning worker only

Readiness state: `NOT_READY`

Verdict: `PLAN_READY_FOR_REVIEW_NOT_READY`

## 1. Scope / Motivation / Non-goals

### 1.1 Scope

This artifact turns the accepted mapping/normalization plan into a handoff-ready, code-generation-ready no-live implementation plan.

The later implementation worker may implement only candidate internals under Fund documents ownership, no-live excerpt fixtures, fixture-backed normalization and locator helpers, canonical failure mapping, repository non-behavior-change tests and no-consumption guard tests.

### 1.2 Motivation

- Route A proved one local, socket-blocked Docling conversion for `004393 / 2025` can produce a full-content `DoclingDocument` JSON with useful headings, tables, page provenance, bbox and row/column offsets.
- The accepted plan and controller judgment require a candidate-only `FundDisclosureDocument` representation before any consumer integration.
- Current production `ParsedAnnualReport -> extractor -> EvidenceAnchor` is not a complete annual-report document representation.
- Implementation must not require the next worker to invent schema ownership, fixture shape, normalization rule names, failure mapping, test scope or boundary rules.

### 1.3 Non-goals

This plan does not authorize:

- source/test/runtime implementation in this planning turn;
- production parser replacement;
- `FundDocumentRepository.load_annual_report()` behavior change;
- current `EvidenceAnchor` schema change or `EvidenceSourceKind` expansion;
- extractor, renderer, audit, source-label, Service, Host, UI or quality-gate consumer integration;
- direct Service/UI/Host/renderer/quality-gate access to Docling, PDF files, parser cache, parser helpers or candidate artifacts;
- PDF/Docling conversion, PDF parser execution, EID/FDR/network, provider/LLM, analyze/checklist, golden, readiness/release/PR commands;
- source truth, field correctness, raw XML/XBRL, taxonomy compatibility, parser replacement or readiness claims;
- EID source policy change or Eastmoney/CNINFO/fund-company website fallback.

## 2. Evidence Reviewed

- `AGENTS.md`
- `docs/implementation-control.md`, `Current Truth Guardrails`, `Current Gate`, `Next entry point`
- `docs/current-startup-packet.md`, `Current Mainline`, `Resume Checklist`
- `docs/reviews/docling-funddisclosuredocument-mapping-normalization-plan-20260615.md`
- `docs/reviews/docling-funddisclosuredocument-mapping-normalization-plan-controller-judgment-20260615.md`
- `docs/reviews/docling-funddisclosuredocument-mapping-normalization-plan-review-ds-20260615.md`
- `docs/reviews/docling-funddisclosuredocument-mapping-normalization-plan-review-mimo-20260615.md`
- `docs/reviews/docling-route-a-local-artifact-conversion-quality-evidence-20260615.md`
- `reports/docling-route-a/004393_2025_docling_quality_summary.json`
- Static ownership check: `fund_agent/fund/documents/models.py`, `fund_agent/fund/documents/repository.py`, `fund_agent/fund/extractors/models.py`, `fund_agent/fund/documents/__init__.py`, `tests/fund/documents/test_repository.py`

Commands run by this planning worker were read-only/status/static reads only. No PDF/Docling conversion, PDF parser, EID/FDR/network, provider/LLM, analyze/checklist, golden, readiness/release, stage, commit, push or PR command was run.

## 3. Accepted Facts And Non-proofs

### 3.1 Accepted facts

- Current active gate is `Docling FundDisclosureDocument Mapping And Normalization No-live Implementation Planning Gate`.
- This gate is planning-only and must preserve `NOT_READY`.
- `docling_pdf_candidate` is accepted only as a candidate Fund documents-layer representation derived from PDF through Docling.
- `docling_pdf_candidate` is not a current production `EvidenceAnchor.source_kind`.
- Current `EvidenceSourceKind` is `Literal["annual_report", "external_api", "derived"]`; it must not be expanded in this implementation gate.
- `FundDocumentRepository` remains the production document access boundary.
- Current production annual-report source policy remains EID single-source with no fallback.
- Route A local benchmark facts for `004393 / 2025`: 65 pages, 670 text items, 95 tables, 213 Markdown headings, all `§1` through `§13` present, JSON/Markdown outputs produced, `do_ocr=false`, `do_table_structure=true`, CPU, socket-blocked runtime, offline HuggingFace/Transformers flags.
- Docling JSON `tables[].data.table_cells`, not Markdown tables, is the accepted structured input for candidate mapping.
- Representative Route A tables for excerpt fixtures: table `0` / page 3 document index, table `14` / page 11 fund manager, table `72` / page 52 industry, table `74` / page 53 stock holding detail, table `86` / page 60 manager holding, table `61`/`62` / pages 46-47 comparative financial-statement-style tables.
- Route A quality issues requiring normalization: CJK spaces, date spaces, numeric punctuation split, whitespace-only numeric grouping ambiguity, duplicated/split headers, repeated headers, cross-page table split, merged cells, TOC/header/footer exclusion and brittle exact keyword matching.

### 3.2 Non-proofs

- The local user-owned PDF benchmark is not source truth.
- Docling output is not field correctness proof.
- Docling output is not raw XML/XBRL proof.
- Docling output is not taxonomy compatibility proof.
- Docling output is not parser replacement proof.
- Local HuggingFace cache provenance is benchmark-only, not production model provenance acceptance.
- Same-report comparison across EID HTML render, current pdfplumber and Docling remains deferred and is required before consumer integration or route-strength claims.
- Candidate `EvidenceAnchor` projection fixtures are non-production and do not authorize extractor/value projection.
- `换手率=0` keyword evidence is not a Docling failure and must not be used to infer regulatory/source coverage.

## 4. Allowed Write Set Proposal

The later no-live implementation worker should restrict writes to the following proposal. Anything outside this set requires controller decision before implementation.

| Category | Proposed paths | Allowed content |
|---|---|---|
| Fund documents candidate internals | `fund_agent/fund/documents/candidates/__init__.py`, `fund_agent/fund/documents/candidates/models.py`, `fund_agent/fund/documents/candidates/normalization.py`, `fund_agent/fund/documents/candidates/locators.py`, `fund_agent/fund/documents/candidates/failures.py` | Candidate-only dataclasses, TypedDicts, enums, pure functions and failure mapping. Do not export from `fund_agent/fund/documents/__init__.py` unless controller later authorizes public contract. |
| Fixture/excerpt data | `tests/fixtures/fund/docling_route_a/004393_2025/excerpt.json`, optional small per-case files under the same directory | Minimal excerpt copied from existing Route A JSON summary/source snippets. Do not commit full `004393_2025_docling.json`, full Markdown, PDF, cache artifacts or model artifacts. |
| Fixture/excerpt tests | `tests/fund/documents/test_docling_candidate_models.py`, `tests/fund/documents/test_docling_normalization.py`, `tests/fund/documents/test_docling_locators.py`, `tests/fund/documents/test_docling_failure_mapping.py`, `tests/fund/documents/test_docling_no_consumption_guards.py`, narrow additions to `tests/fund/documents/test_repository.py` | No-live tests only, using JSON excerpts/fakes. No conversion, parser, network, provider, LLM, analyze/checklist/golden/readiness. |
| Necessary docs decision | `fund_agent/fund/README.md` or `tests/README.md`, only if implementation changes local ownership/test docs | Candidate-only status, excerpt fixture provenance, no-consumption boundaries and no-live commands. Do not update design/control docs as source truth from implementation worker. |

Forbidden writes:

- production Service/UI/Host/renderer/quality-gate behavior;
- `fund_agent/fund/extractors/models.py` public `EvidenceAnchor` schema or `EvidenceSourceKind`;
- `FundDocumentRepository.load_annual_report()` production behavior;
- source policy/fallback code;
- full Route A JSON/Markdown/PDF/model/cache artifacts;
- readiness/release/PR artifacts.

## 5. Proposed Module / File Ownership

### 5.1 Ownership rules

- Candidate representation belongs to `fund_agent/fund/documents/candidates`.
- Existing `fund_agent/fund/documents/models.py` remains the public production annual-report model surface.
- Existing `fund_agent/fund/extractors/models.py` remains the public `EvidenceAnchor` schema surface and must not import candidate internals.
- Candidate-to-`EvidenceAnchor` projection is fixture-only and should live as a helper/test fixture under candidate ownership, not extractor ownership.
- Normalization is document-level only: it stabilizes locator text, headers, row/column paths and hashes; it does not parse `Decimal`, choose business fields or prove field correctness.

### 5.2 Proposed files

| Concern | Proposed owner | Notes |
|---|---|---|
| Candidate model | `fund_agent/fund/documents/candidates/models.py` | Internal dataclasses/enums/TypedDicts. No public `documents.__all__` export. |
| Normalization rules | `fund_agent/fund/documents/candidates/normalization.py` | Pure functions returning raw/normalized text plus closed rule names and block status. |
| Locator/projection helper | `fund_agent/fund/documents/candidates/locators.py` | Table grid expansion, row/column path generation, locator hash, candidate-only `EvidenceAnchor` note shape. |
| Failure mapping | `fund_agent/fund/documents/candidates/failures.py` | Candidate failures to canonical `AnnualReportSourceFailureCategory` outcomes. |
| Fixture metadata/excerpts | `tests/fixtures/fund/docling_route_a/004393_2025/excerpt.json` | Minimal excerpts only; include hash metadata tying the excerpt to Route A JSON without embedding full JSON. |
| Tests | `tests/fund/documents/test_docling_*.py` | Focused, no-live, fixture/fake-only. |
| Repository non-behavior tests | additions to `tests/fund/documents/test_repository.py` | Prove default load path remains `ParsedAnnualReport`; candidate route is not invoked by default. |
| No-consumption guards | `tests/fund/documents/test_docling_no_consumption_guards.py` | AST/static import checks over Service/UI/Host/renderer/quality gate. |

## 6. Candidate Dataclass / TypedDict / Enum Design

All names below are candidate internals. They must not modify current `EvidenceAnchor`, `EvidenceSourceKind`, renderer source labels, audit contracts or quality-gate schemas.

### 6.1 Enums and Literals

```python
CandidateSourceKind = Literal["docling_pdf_candidate"]
CandidateDocumentKind = Literal["annual_report_candidate"]
CandidateTruthStatus = Literal["not_proven"]
CandidateParserReplacementStatus = Literal["not_authorized"]

class CandidateFailureCode(StrEnum):
    CANDIDATE_IDENTITY_MISSING = "candidate_identity_missing"
    CANDIDATE_IDENTITY_MISMATCH = "candidate_identity_mismatch"
    CANDIDATE_ARTIFACT_HASH_MISSING = "candidate_artifact_hash_missing"
    CANDIDATE_ARTIFACT_HASH_MISMATCH = "candidate_artifact_hash_mismatch"
    CANDIDATE_SCHEMA_VERSION_UNSUPPORTED = "candidate_schema_version_unsupported"
    PAGE_PROVENANCE_MISSING = "page_provenance_missing"
    SECTION_HIERARCHY_UNSTABLE = "section_hierarchy_unstable"
    TABLE_CELLS_MISSING = "table_cells_missing"
    TABLE_PROVENANCE_MISSING = "table_provenance_missing"
    TABLE_SECTION_UNASSIGNED = "table_section_unassigned"
    TABLE_HEADER_UNSTABLE = "table_header_unstable"
    TABLE_SHAPE_INCONSISTENT = "table_shape_inconsistent"
    TABLE_CONTINUATION_AMBIGUOUS = "table_continuation_ambiguous"
    CELL_BBOX_MISSING = "cell_bbox_missing"
    CELL_HEADER_PATH_MISSING = "cell_header_path_missing"
    CELL_ROW_LABEL_PATH_MISSING = "cell_row_label_path_missing"
    CELL_SPAN_CONFLICT = "cell_span_conflict"
    CELL_LOCATOR_UNSTABLE = "cell_locator_unstable"
    NUMERIC_REPAIR_AMBIGUOUS = "numeric_repair_ambiguous"
    EXCERPT_HASH_MISMATCH = "excerpt_hash_mismatch"
    EXCERPT_TRUNCATED = "excerpt_truncated"
```

Other small closed enums:

- `CandidateSectionSource`: `docling_heading`, `toc_hint`, `derived_pattern`
- `CandidateConfidence`: `strong`, `usable`, `weak`, `blocked`
- `CandidateBlockType`: `paragraph`, `heading`, `note`, `list_item`, `caption`, `footnote`, `header_footer_candidate`
- `CandidateTableFamily`: `financial_metrics`, `financial_statement`, `portfolio_holding`, `industry_holding`, `manager_profile`, `holder_info`, `document_index`, `unknown`
- `LocatorStability`: `strong`, `usable`, `weak`, `blocked`
- `CandidateBlockReason`: `toc`, `page_header`, `page_footer`, `cover_metadata`, `repeated_report_title`, `repeated_table_header`, `ambiguous`

### 6.2 Core dataclasses

```python
@dataclass(frozen=True, slots=True)
class CandidateArtifactIdentity:
    source_kind: CandidateSourceKind
    document_kind: CandidateDocumentKind
    fund_code: str
    fund_name: str | None
    report_year: int
    report_type: Literal["annual_report"]
    input_pdf_filename: str | None
    input_pdf_mimetype: str | None
    input_pdf_binary_hash: str | None
    docling_schema_name: str | None
    docling_version: str | None
    docling_json_sha256: str
    markdown_sha256: str | None
    source_truth_status: CandidateTruthStatus
    field_correctness_status: CandidateTruthStatus
    taxonomy_compatibility_status: CandidateTruthStatus
    production_parser_replacement_status: CandidateParserReplacementStatus

@dataclass(frozen=True, slots=True)
class CandidatePageSpan:
    start_page_no: int
    end_page_no: int
    source_refs: tuple[str, ...]
    confidence: CandidateConfidence

@dataclass(frozen=True, slots=True)
class CandidateSection:
    section_id: str
    heading_text_raw: str
    heading_text_normalized: str
    heading_path: tuple[str, ...]
    heading_level: int | None
    page_span: CandidatePageSpan
    start_ref: str
    start_bbox: "CandidateBBox | None"
    section_source: CandidateSectionSource
    confidence: CandidateConfidence
    normalization_notes: tuple["NormalizationRuleName", ...]

@dataclass(frozen=True, slots=True)
class CandidateParagraphBlock:
    block_id: str
    block_type: CandidateBlockType
    section_id: str | None
    heading_path: tuple[str, ...]
    page_no: int | None
    bbox: "CandidateBBox | None"
    text_raw: str
    text_normalized: str
    content_hash: str
    normalization_applied: tuple["NormalizationRuleName", ...]
    excluded_reason: CandidateBlockReason | None

@dataclass(frozen=True, slots=True)
class CandidateTableBlock:
    table_id: str
    source_table_index: int
    docling_self_ref: str
    section_id: str | None
    heading_path: tuple[str, ...]
    page_numbers: tuple[int, ...]
    bbox_by_page: tuple["CandidatePageBBox", ...]
    num_rows: int
    num_cols: int
    normalized_cells: tuple["CandidateTableCellLocator", ...]
    header_rows: tuple[int, ...]
    body_rows: tuple[int, ...]
    table_family: CandidateTableFamily
    continuation_group_id: str | None
    locator_stability: LocatorStability
    failure_code: CandidateFailureCode | None
```

### 6.3 Cell locator and projection note

```python
@dataclass(frozen=True, slots=True)
class CandidateTableCellLocator:
    table_id: str
    source_table_index: int
    source_table_self_ref: str
    page_no: int
    cell_bbox: "CandidateBBox"
    row_span: int
    col_span: int
    start_row_offset_idx: int
    end_row_offset_idx: int
    start_col_offset_idx: int
    end_col_offset_idx: int
    row_index_normalized: int
    column_index_normalized: int
    text_raw: str
    text_normalized: str
    column_header: bool
    row_header: bool
    row_section: bool
    row_label_path: tuple[str, ...]
    column_header_path: tuple[str, ...]
    cell_hash: str
    locator_hash: str
    normalization_notes: tuple["NormalizationRuleName", ...]
```

`CandidateEvidenceAnchorNote` should be a `TypedDict` or JSON-compatible dataclass used only by fixture tests:

```python
class CandidateEvidenceAnchorNote(TypedDict):
    candidate_source_kind: Literal["docling_pdf_candidate"]
    source_table_ref: str
    page_no: int
    bbox: dict[str, float | str]
    row_offsets: tuple[int, int]
    col_offsets: tuple[int, int]
    row_label_path: tuple[str, ...]
    column_header_path: tuple[str, ...]
    cell_text: str
    cell_hash: str
    locator_hash: str
    normalization: tuple["NormalizationRuleName", ...]
    source_truth_status: Literal["not_proven"]
    field_correctness_status: Literal["not_proven"]
```

Projection fixture constraints:

- Project `document_year`, `section_id`, `page_number`, `table_id`, `row_locator`, `note` only in tests.
- Do not add `docling_pdf_candidate` to `EvidenceSourceKind`.
- Do not claim `cell_text` as field value.
- If `section_id`, page number, table id, row path, column path, bbox or locator hash is unstable, emit candidate failure and do not project fixture anchor.

## 7. Closed Normalization Rule Vocabulary

The implementation must use exactly this closed rule-name vocabulary for `normalization_notes`. Do not use ad hoc strings such as `numeric_token_repair_if_needed`.

| Rule name | Layer | Applies to | Output semantics |
|---|---|---|---|
| `cjk_space_repair` | document | Spaces between adjacent CJK characters in paragraphs/cells/headings | Remove only CJK-CJK ASCII whitespace; preserve raw text. |
| `date_space_repair` | document | Chinese date tokens such as `2025 年 12 月 31 日`, `2022年8 月8日` | Normalize date spacing for locator stability, e.g. `2025年12月31日`. No date semantics beyond string normalization. |
| `numeric_punctuation_repair` | document | Numeric punctuation splits such as `33,984,439 .75`, `154,973,70 4.60` | Repair only when punctuation grammar is deterministic. No Decimal parsing. |
| `numeric_whitespace_grouping_repair_or_block` | document | Whitespace-only grouped numerics such as `100 000`, `1 234 567` | Repair only under deterministic grouping rules; otherwise block projection with `numeric_repair_ambiguous`. |
| `header_path_reconstruction` | document/table | `column_header=true`, top rows, merged headers, period labels | Build `column_header_path` from expanded headers. |
| `repeated_header_exclusion` | document/table | Repeated table headers in body rows | Remove from body rows, retain excluded refs and reason. |
| `cross_page_table_stitching` | document/table | Consecutive table blocks that pass continuation rules | Stitch into candidate table group while preserving original table refs/pages/bboxes. |
| `merged_cell_expansion` | document/table | Cells with `row_span`, `col_span`, offset ranges | Expand logical coverage and preserve `merged_cell_source_ref`. |
| `toc_header_footer_exclusion` | document/block | TOC tables, cover metadata, page header/footer, repeated report titles | Exclude from facts; retain as navigation/provenance blocks. |
| `row_label_path_generation` | document/table | Row-section/header cells and left label columns | Generate stable row path; block if non-unique after ordinal fallback. |
| `column_header_path_generation` | document/table | Header cells above data cells | Generate stable column path; block if leaf header absent for data cells. |

Rule notes:

- A rule may be recorded as applied only when it changed text, excluded a block, stitched a table, expanded a span or generated a path.
- Failure/block reasons are not normalization rule names. Use `CandidateFailureCode` for failures.
- Raw text and source refs must always be retained alongside normalized output.

## 8. Document Normalization vs Extractor / Value Parsing Boundary

Document normalization may:

- repair whitespace and punctuation for locator stability;
- reconstruct section/header/row/column paths;
- deduplicate repeated headers;
- stitch cross-page table candidates;
- expand merged cells;
- exclude TOC/header/footer/furniture from fact candidates;
- compute stable hashes from normalized text plus locator context;
- emit candidate failures when locator stability cannot be proven.

Document normalization must not:

- parse `Decimal`, percent, date periods or business values into typed facts;
- choose which business field a value satisfies;
- infer field correctness;
- reconcile with NAV/API/provider values;
- apply CHAPTER_CONTRACT, ITEM_RULE or audit logic;
- produce production `EvidenceAnchor` instances consumed by extractors/renderers/audits;
- change source policy or fallback semantics.

Extractor/value parsing belongs to later extractor/projection gates. It must be separately authorized after same-report comparison and consumer integration planning.

## 9. Whitespace-only Numeric Grouping Rule

The implementation must make `numeric_whitespace_grouping_repair_or_block` deterministic.

### 9.1 Deterministic repair conditions

Repair a whitespace-only grouped numeric token only when all conditions hold:

1. The token is within one cell/paragraph text span, not across table cells.
2. The token consists of an optional sign, a first digit group of 1-3 digits, one or more ASCII whitespace separators, subsequent digit groups of exactly 3 digits, and an optional decimal suffix.
3. The token has no CJK/Latin letters, tilde range marker, slash, colon, date unit, currency unit embedded inside the matched span.
4. The token is not part of a date-like or code-like pattern.
5. Removing whitespace yields a valid numeric string under document-level string grammar.

Accepted repair examples:

| Raw | Normalized | Rule |
|---|---|---|
| `100 000` | `100000` | `numeric_whitespace_grouping_repair_or_block` |
| `1 234 567` | `1234567` | `numeric_whitespace_grouping_repair_or_block` |
| `12 345.67` | `12345.67` | `numeric_whitespace_grouping_repair_or_block` |
| `-1 234 567.89` | `-1234567.89` | `numeric_whitespace_grouping_repair_or_block` |

### 9.2 Fail-closed / no-repair conditions

Block candidate field projection with `numeric_repair_ambiguous` when:

- any subsequent group is not exactly 3 digits, e.g. `1 23 456`;
- the first group has more than 3 digits and is not a date handled by `date_space_repair`;
- the token can plausibly be a range or share interval, e.g. `50 100` when no separator/range marker proves grouping;
- the token is adjacent to CJK/Latin business text in a way that changes token boundary;
- the token crosses cells/rows/paragraph blocks;
- normalization would merge two independent values.

No-repair examples:

| Raw | Expected outcome |
|---|---|
| `1 23 456` | block as `numeric_repair_ambiguous` |
| `50 100` | block unless fixture proves it is a grouped amount by table context; default is block |
| `2025 12 31` | do not numeric-repair; date rule may handle only explicit Chinese date-unit forms |
| `A 100 000` | repair only the bounded numeric token if token boundaries are explicit; otherwise block |
| `100 000 50` | block because final group length is not 3 |

Fixture cases must include both accepted and rejected examples. All accepted repairs remain strings; no Decimal parsing is allowed.

## 10. Fixture / Excerpt Design

### 10.1 Fixture path and metadata

Use one minimal checked-in JSON excerpt:

```text
tests/fixtures/fund/docling_route_a/004393_2025/excerpt.json
```

The fixture must include:

- `fixture_schema_version`: `docling_route_a_excerpt.v1`
- `fixture_source_kind`: `docling_pdf_candidate_excerpt`
- `fund_code`: `004393`
- `fund_name`: `安信企业价值优选混合A`
- `report_year`: `2025`
- `report_type`: `annual_report`
- `route_a_json_sha256`: `b7a664c31a11db332815884b5632451ed6e64c8d246254ed23f55f409364c933`
- `route_a_markdown_sha256`: `e9644cceebc82a9d9a4a3a1af692e5c7a8fa99edc0ceec0a824e4f246dc87596`
- `excerpt_hash_sha256`: computed over the checked-in excerpt file
- `source_artifact_path`: diagnostic string `reports/docling-route-a/004393_2025_docling.json`, not consumed by tests
- `full_json_committed`: `false`
- `source_truth_status`: `not_proven`
- `field_correctness_status`: `not_proven`
- `taxonomy_compatibility_status`: `not_proven`
- `production_parser_replacement_status`: `not_authorized`
- `notes`: explicit statement that the fixture is a minimal excerpt and not source truth.

### 10.2 Fixture content shape

Keep only minimal snippets needed for deterministic tests:

```json
{
  "metadata": {},
  "origin_excerpt": {
    "filename": "安信企业价值优选混合型证券投资基金2025年年度报告.pdf",
    "mimetype": "application/pdf",
    "binary_hash": "<docling-origin-binary-hash-if-present>"
  },
  "text_excerpts": [
    {
      "case_id": "section-heading-s8",
      "self_ref": "#/texts/...",
      "label": "section_header",
      "level": 1,
      "text": "§8 投资组合报告",
      "prov": [{"page_no": 50, "bbox": {"l": 0, "t": 0, "r": 0, "b": 0, "coord_origin": "TOPLEFT"}}]
    }
  ],
  "table_excerpts": [
    {
      "case_id": "toc-table-0",
      "source_table_index": 0,
      "label": "document_index",
      "page_no": 3,
      "num_rows": 37,
      "num_cols": 3,
      "table_cells": []
    },
    {
      "case_id": "stock-holding-table-74",
      "source_table_index": 74,
      "label": "table",
      "page_no": 53,
      "num_rows": 38,
      "num_cols": 6,
      "table_cells": []
    },
    {
      "case_id": "manager-holding-table-86",
      "source_table_index": 86,
      "label": "table",
      "page_no": 60,
      "num_rows": 7,
      "num_cols": 3,
      "table_cells": []
    }
  ],
  "normalization_cases": [],
  "failure_cases": []
}
```

`table_cells` should contain only the header rows and 2-4 representative body rows per table, preserving Docling fields:

- `bbox`
- `row_span`
- `col_span`
- `start_row_offset_idx`
- `end_row_offset_idx`
- `start_col_offset_idx`
- `end_col_offset_idx`
- `text`
- `column_header`
- `row_header`
- `row_section`
- `fillable`

### 10.3 Required excerpt cases

| Case | Source | Purpose |
|---|---|---|
| `toc-table-0` | Route A table `0`, page 3 | `toc_header_footer_exclusion`, document index exclusion. |
| `manager-table-14` | Route A table `14`, page 11 | CJK/date space repair and multi-level header path. |
| `industry-table-72` | Route A table `72`, page 52 | CJK split repair, industry row labels, numeric value locator. |
| `stock-holding-table-74` | Route A table `74`, page 53 | simple header path, row label path, cell/locator hash. |
| `manager-holding-table-86` | Route A table `86`, page 60 | manager holding keyword whitespace normalization and row label hierarchy. |
| `financial-continuation-61-62` | Route A tables `61`/`62`, pages 46-47 | cross-page stitching accept/reject decisions, compatible/incompatible header paths. |
| `numeric-punctuation` | synthetic excerpt text based on Route A observations | `33,984,439 .75`, `154,973,70 4.60`. |
| `numeric-whitespace-grouping` | fixture-only cases | `100 000`, `1 234 567`, `1 23 456`, `50 100`. |

The implementation worker must not copy the full Route A JSON. If a case needs additional cells, add only the minimal cells and update `excerpt_hash_sha256`.

## 11. Implementation Slices

Each slice is intentionally small. Later implementation should keep commits/review artifacts separable if the controller requests that workflow.

### Slice 0: Fixture Contract And Red Tests

Files:

- `tests/fixtures/fund/docling_route_a/004393_2025/excerpt.json`
- `tests/fund/documents/test_docling_candidate_models.py`
- `tests/fund/documents/test_docling_normalization.py`
- `tests/fund/documents/test_docling_locators.py`
- `tests/fund/documents/test_docling_failure_mapping.py`

Contracts:

- Excerpt fixture loads from checked-in JSON only.
- Fixture metadata contains full Route A hashes and explicit non-proof statuses.
- Full JSON/Markdown/PDF/cache/model artifacts are not required.

Expected assertions:

- fixture has schema version `docling_route_a_excerpt.v1`;
- `route_a_json_sha256` equals accepted Route A JSON hash;
- `full_json_committed is false`;
- required cases exist;
- fixture tests fail before candidate implementation if helpers are absent.

Failure paths:

- missing route hash -> `candidate_artifact_hash_missing`;
- excerpt hash mismatch -> `excerpt_hash_mismatch`;
- missing required table/text fields -> `candidate_schema_version_unsupported` or `schema_drift` canonical mapping.

### Slice 1: Candidate Model Internals

Files:

- `fund_agent/fund/documents/candidates/__init__.py`
- `fund_agent/fund/documents/candidates/models.py`
- `tests/fund/documents/test_docling_candidate_models.py`

Contracts:

- Implement dataclasses/enums/TypedDicts from section 6.
- Keep `source_truth_status`, `field_correctness_status`, `taxonomy_compatibility_status` fixed to `not_proven`.
- Keep `production_parser_replacement_status` fixed to `not_authorized`.
- Do not export candidate models from `fund_agent/fund/documents/__init__.py`.
- Do not modify `fund_agent/fund/extractors/models.py`.

Expected assertions:

- candidate identity round-trips from fixture metadata;
- `source_kind == "docling_pdf_candidate"` only inside candidate model;
- current `EvidenceSourceKind` literal remains `annual_report/external_api/derived`;
- candidate statuses cannot be initialized as truth/proven/authorized values.

Failure paths:

- identity missing or mismatch emits candidate identity failure;
- hash missing/mismatch emits artifact failure;
- unsupported schema emits schema failure.

### Slice 2: Text Normalization Core

Files:

- `fund_agent/fund/documents/candidates/normalization.py`
- `tests/fund/documents/test_docling_normalization.py`

Contracts:

- Implement `cjk_space_repair`, `date_space_repair`, `numeric_punctuation_repair`, `numeric_whitespace_grouping_repair_or_block`.
- Return a value object such as `NormalizedText(raw_text, normalized_text, rules_applied, failure_code)`.
- Preserve raw text.
- Do not parse Decimal or infer field correctness.

Expected assertions:

- `基 金 经 理` normalizes to `基金经理`;
- `供 应业` normalizes to `供应业`;
- `2025 年 12 月 31 日` normalizes to `2025年12月31日`;
- `2022年8 月8日` normalizes to `2022年8月8日`;
- `33,984,439 .75` normalizes to `33,984,439.75`;
- `154,973,70 4.60` normalizes to `154,973,704.60`;
- `100 000` normalizes to `100000`;
- `1 234 567` normalizes to `1234567`;
- `1 23 456`, `50 100`, cross-cell numeric spans block with `numeric_repair_ambiguous`.

Failure paths:

- ambiguous numeric grouping returns failure and blocks projection;
- mixed Latin/ticker/unit spaces are preserved unless a bounded numeric token is deterministic.

### Slice 3: Table Structure Normalization And Locators

Files:

- `fund_agent/fund/documents/candidates/locators.py`
- `tests/fund/documents/test_docling_locators.py`

Contracts:

- Implement `header_path_reconstruction`, `repeated_header_exclusion`, `merged_cell_expansion`, `toc_header_footer_exclusion`, `row_label_path_generation`, `column_header_path_generation`.
- Implement `cell_hash` and `locator_hash` as deterministic hashes over normalized text plus locator context, not text alone.
- Use `table_cells`, not Markdown, as structured input.

Expected assertions:

- stock holding table `74` reconstructs column paths such as `股票代码`, `股票名称`, `数量（股）`, `公允价值（元）`, `占基金资产净值比例（%）`;
- manager holding table `86` normalizes `本基金基金经理持有 本开放式基金` to a stable row label path;
- TOC table `0` is excluded as `document_index` and retained with exclusion reason;
- repeated header rows are excluded without dropping business rows;
- merged spans preserve source refs and reject overlap conflicts;
- duplicate locator context falls back to offsets and blocks if still non-unique.

Failure paths:

- missing `table_cells` -> `table_cells_missing`;
- missing bbox -> `cell_bbox_missing`;
- absent leaf header -> `cell_header_path_missing`;
- non-unique row path after ordinal fallback -> `cell_row_label_path_missing` or `cell_locator_unstable`;
- conflicting spans -> `cell_span_conflict`.

### Slice 4: Cross-page Table Stitching

Files:

- `fund_agent/fund/documents/candidates/locators.py`
- `tests/fund/documents/test_docling_locators.py`

Contracts:

- Implement `cross_page_table_stitching` as an opt-in pure helper over excerpted table blocks.
- Stitch only adjacent/near-adjacent pages with same section path, same table family, compatible column count, compatible `column_header_path`, no intervening different body heading, and identical/absent continuation caption/header.
- Preserve all original `source_table_index`, `self_ref`, page numbers and bboxes.

Expected assertions:

- compatible fixture pair stitches to `docling:t{first_index}:stitched:{hash}`;
- incompatible column count rejects;
- changed heading path rejects;
- ambiguous financial statement continuation rejects.

Failure paths:

- ambiguous continuation -> `table_continuation_ambiguous`;
- header mismatch -> `table_header_unstable`;
- shape mismatch -> `table_shape_inconsistent`.

### Slice 5: Candidate EvidenceAnchor Projection Fixture

Files:

- `fund_agent/fund/documents/candidates/locators.py`
- `tests/fund/documents/test_docling_locators.py`

Contracts:

- Provide fixture-only projection helper such as `build_candidate_anchor_note(locator) -> CandidateEvidenceAnchorNote`.
- Do not instantiate production `EvidenceAnchor` in runtime code.
- Test may instantiate current `EvidenceAnchor` only to prove current fields can carry candidate note without schema change.
- Keep `docling_pdf_candidate` inside `note["candidate_source_kind"]`, not `source_kind`.

Expected assertions:

- projection note contains `bbox`, row/col offsets, row label path, column header path, `cell_hash`, `locator_hash`, normalization names and `not_proven` statuses;
- production `EvidenceAnchor.source_kind` remains `annual_report` in the demonstration if a current anchor is instantiated;
- no public schema field is added.

Failure paths:

- missing page/table/row/column/bbox/hash blocks projection;
- ambiguous numeric repair blocks projection.

### Slice 6: Canonical Failure Mapping

Files:

- `fund_agent/fund/documents/candidates/failures.py`
- `tests/fund/documents/test_docling_failure_mapping.py`

Contracts:

- Map candidate failures to current canonical `AnnualReportSourceFailureCategory`: `not_found`, `unavailable`, `schema_drift`, `identity_mismatch`, `integrity_error`.
- Keep terminal failure semantics. Do not introduce fallback.

Required mapping:

| Candidate condition | Canonical outcome |
|---|---|
| No matching annual report under current EID source | `not_found` |
| Fixture/artifact inaccessible in no-live setup | `unavailable` |
| Unsupported Docling schema/version | `schema_drift` |
| Missing required JSON keys: `texts`, `tables`, `tables[].data.table_cells`, provenance, bbox | `schema_drift` |
| Section hierarchy/table shape/header/locator contract unstable | `schema_drift` |
| Trusted fund/year/report identity missing or conflicting | `identity_mismatch` |
| Docling JSON hash/source PDF hash missing, mismatched, truncated or corrupt | `integrity_error` |

Expected assertions:

- every `CandidateFailureCode` maps to one canonical outcome or is explicitly non-source local exclusion;
- `not_found` and `unavailable` remain terminal, no fallback route is suggested;
- mapping table has no Eastmoney/CNINFO/fund-company fallback branch.

Failure paths:

- unmapped candidate failure fails tests;
- unknown canonical outcome fails tests.

### Slice 7: Repository Non-behavior And No-consumption Guards

Files:

- `tests/fund/documents/test_repository.py`
- `tests/fund/documents/test_docling_no_consumption_guards.py`

Contracts:

- `FundDocumentRepository.load_annual_report()` production behavior remains unchanged.
- Candidate modules are not imported/called by Service/UI/Host/renderer/quality gate.
- Current production parser/cache boundary remains inside Fund documents.

Expected assertions:

- fake loader path in `FundDocumentRepository.load_annual_report()` still returns `ParsedAnnualReport` and does not expose path or candidate document;
- default repository has no candidate route invoked by default;
- `fund_agent/services`, `fund_agent/ui`, `fund_agent/host`, `fund_agent/fund/template`, `fund_agent/fund/audit`, `fund_agent/fund/report_quality_validation.py` do not import `fund_agent.fund.documents.candidates`, `docling`, PDF cache helpers, parser adapters or Docling/PDF parser helpers directly;
- `fund_agent/fund/documents/__init__.py` does not export candidate internals;
- `EvidenceSourceKind` still excludes `docling_pdf_candidate`.

Failure paths:

- any direct import/call in forbidden consumers fails no-consumption guard;
- any production repository return type/source policy behavior change fails repository tests.

### Slice 8: README/Test Documentation Decision

Files:

- `fund_agent/fund/README.md` and/or `tests/README.md`, only if implementation worker changes candidate internals/tests.

Contracts:

- Document candidate-only status.
- Document no-live fixture provenance and full-JSON non-commit rule.
- Document no-consumption boundary.
- Preserve `NOT_READY`.

Expected assertions:

- docs do not describe Docling as production parser, source truth, field correctness proof or readiness proof.

## 12. Validation Commands For Later Implementation

Planning worker did not run these commands. Later implementation worker may run only no-live targeted commands such as:

```bash
uv run pytest tests/fund/documents/test_docling_candidate_models.py -q
uv run pytest tests/fund/documents/test_docling_normalization.py -q
uv run pytest tests/fund/documents/test_docling_locators.py -q
uv run pytest tests/fund/documents/test_docling_failure_mapping.py -q
uv run pytest tests/fund/documents/test_docling_no_consumption_guards.py -q
uv run pytest tests/fund/documents/test_repository.py -q
uv run ruff check fund_agent/fund/documents tests/fund/documents
```

Forbidden validation:

- PDF/Docling conversion;
- PDF parser execution;
- EID/FDR/network;
- provider/LLM;
- `fund-analysis analyze`;
- `fund-analysis checklist`;
- golden/readiness/release/PR commands;
- fallback/source expansion tests that touch live sources.

## 13. Stop Conditions

Stop and return `PLAN_NEEDS_CONTROLLER_DECISION_NOT_READY` or `BLOCKED_NOT_READY` if any condition appears:

- implementation would need to change current `EvidenceAnchor` public schema or `EvidenceSourceKind`;
- `docling_pdf_candidate` is proposed as production `source_kind`;
- Service/UI/Host/renderer/quality gate would import/call Docling, PDF files, parser cache, parser helpers or candidate artifacts directly;
- `FundDocumentRepository.load_annual_report()` production behavior would change;
- EID single-source/no-fallback policy would change or a fallback source is introduced;
- implementation requires full Route A JSON/Markdown/PDF/model/cache artifacts to be committed;
- implementation requires PDF/Docling conversion, parser, EID/FDR/network, provider/LLM, analyze/checklist/golden/readiness/release/PR commands;
- document normalization must parse Decimal, prove field correctness or choose business fields;
- same-report comparison or consumer integration is needed to pass a test;
- candidate output is described as source truth, field correctness, raw XML/XBRL, taxonomy compatibility, parser replacement, readiness or release proof;
- normalization vocabulary needs a new rule name outside section 7.

## 14. Residual Risks

- Route A remains one local sample only: `004393 / 2025`.
- Local model cache provenance is unresolved for production use.
- Docling JSON schema may drift across versions.
- Same-report EID HTML render versus current pdfplumber versus Docling comparison remains deferred.
- Candidate locator quality does not prove extractor field correctness.
- Numeric whitespace grouping may still require extractor-level context in future; this gate defaults ambiguous cases to fail-closed.
- Cross-page stitching, merged-cell expansion and header reconstruction are high-risk and must remain fixture-backed.
- Production integration requires later controller decisions on candidate source kind, public schema, consumer routing and parser strategy.

## 15. Next Gate Recommendation

Recommended next gate:

```text
Docling FundDisclosureDocument Mapping And Normalization No-live Implementation Plan Review Gate
```

Review focus:

- candidate-only ownership under Fund documents;
- no current `EvidenceAnchor` schema change;
- closed normalization vocabulary completeness;
- whitespace-only numeric grouping repair/block semantics;
- fixture excerpt minimality and hash/provenance metadata;
- deterministic failure mapping;
- no-consumption guard coverage;
- repository non-behavior coverage;
- preservation of EID single-source/no-fallback policy and `NOT_READY`.

If accepted, the controller may separately authorize:

```text
Docling FundDisclosureDocument Mapping And Normalization No-live Implementation Gate
```

That later gate should remain no-live and candidate-only unless the controller explicitly expands scope.

## 16. Completion Report Format For Later Implementation Worker

Later implementation worker should report:

```text
Path(s) changed:
- ...

Implemented slices:
- Slice N: ...

Validation run:
- command: ...
- result: ...

Forbidden commands not run:
- PDF/Docling conversion: not run
- PDF parser/EID/FDR/network/provider/LLM/analyze/checklist/golden/readiness/release/PR: not run

Boundary verdict:
- EvidenceAnchor schema unchanged: yes/no
- FundDocumentRepository.load_annual_report behavior unchanged: yes/no
- Service/UI/Host/renderer/quality gate no-consumption guards: pass/fail
- EID single-source/no-fallback preserved: yes/no
- NOT_READY preserved: yes/no

Residuals:
- ...

Final verdict:
- IMPLEMENTATION_READY_FOR_REVIEW_NOT_READY
- IMPLEMENTATION_NEEDS_CONTROLLER_DECISION_NOT_READY
- BLOCKED_NOT_READY
```

## 17. Final Verdict

```text
VERDICT: PLAN_READY_FOR_REVIEW_NOT_READY
```

Stop here. Do not enter implementation.
