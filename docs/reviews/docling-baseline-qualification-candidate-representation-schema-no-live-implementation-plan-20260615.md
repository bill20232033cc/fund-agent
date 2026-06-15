# Docling Baseline Qualification Candidate Representation Schema No-live Implementation Plan - 2026-06-15

Status: `READY_FOR_PLAN_REVIEW_NOT_READY`
Gate: `Candidate Representation Schema No-live Implementation Planning Gate`
Role: planning worker
Release/readiness: `NOT_READY`

## 1. Goal

Plan a narrow no-live implementation for route-neutral candidate representation schema internals.

The implementation should make the existing full representation JSONs easier to validate, project and compare without changing production parser behavior or public contracts.

## 2. Source Of Truth

- `AGENTS.md`
- `docs/design.md`
- `docs/reviews/docling-baseline-qualification-candidate-representation-schema-design-plan-controller-judgment-20260615.md`
- `docs/reviews/docling-baseline-qualification-full-representation-export-controller-judgment-20260615.md`
- `fund_agent/fund/documents/candidates/models.py`
- `fund_agent/fund/documents/candidates/representation_export.py`
- `fund_agent/fund/documents/candidates/representation_handlers.py`

Accepted constraints:

- candidate-only;
- `NOT_READY`;
- no source truth;
- no field correctness proof;
- no parser replacement;
- no public `EvidenceAnchor` schema change;
- no `FundDocumentRepository` behavior change;
- no Service/UI/Host/renderer/quality-gate integration.

## 3. Non-goals

- No production integration.
- No production parser replacement.
- No source policy change.
- No live/network/EID/FDR/provider/LLM/analyze/readiness/release/PR commands.
- No direct consumption of candidate JSON by Service/UI/Host/renderer/quality gate.
- No field-family correctness pilot.
- No public `EvidenceSourceKind` expansion.
- No public `EvidenceAnchor` dataclass field change.
- No full annual-report conversion in tests.

## 4. Proposed Write Set

Implementation files:

```text
fund_agent/fund/documents/candidates/representation_models.py
fund_agent/fund/documents/candidates/representation_projection.py
```

Tests:

```text
tests/fund/documents/test_candidate_representation_models.py
tests/fund/documents/test_candidate_representation_projection.py
tests/fund/documents/test_docling_no_consumption_guards.py
```

Documentation:

```text
fund_agent/fund/README.md
```

Do not modify:

```text
fund_agent/fund/documents/__init__.py
fund_agent/fund/documents/repository.py
fund_agent/fund/documents/sources.py
fund_agent/fund/documents/cache.py
fund_agent/fund/documents/adapters/annual_report_pdf.py
fund_agent/fund/extractors/models.py
fund_agent/services/
fund_agent/host/
fund_agent/ui/
fund_agent/fund/quality_gate.py
docs/design.md
docs/implementation-control.md
docs/current-startup-packet.md
```

## 5. Route-neutral Models

Add candidate-internal source enum:

```python
class CandidateRepresentationSourceKind(StrEnum):
    DOCLING_PDF = "docling_pdf_candidate"
    PDFPLUMBER_PDF = "pdfplumber_pdf_candidate"
    EID_HTML_RENDER = "eid_xbrl_html_render_candidate"
```

Add frozen/slotted dataclasses:

```python
CandidateRepresentationIdentity
CandidateRepresentationStatus
CandidateSourceLocator
CandidateSectionNode
CandidateTextBlock
CandidateTableCell
CandidateTableBlock
CandidateRepresentationDocument
CandidateAnchorNote
CandidateProjectionIssue
```

### 5.1 Field-level contracts

`CandidateRepresentationIdentity`

| Field | Type | Required | Null/default | Projection source |
|---|---|---|---|---|
| `source_kind` | `CandidateRepresentationSourceKind` | yes | no null | `payload["source_kind"]` |
| `sample_id` | `str | None` | yes | nullable for legacy S1 refs | `payload.get("sample_id")` |
| `fund_code` | `str` | yes | no null; 6 digits | `payload["fund_code"]` |
| `document_year` | `int` | yes | no null | `payload["document_year"]` |
| `report_type` | `Literal["annual_report"]` | yes | no null | `payload["report_type"]` |
| `input_artifact_path` | `str | None` | yes | nullable for blocked routes | `payload["input_artifact"]["path"]` |
| `accepted_input_sha256` | `str | None` | yes | nullable | `payload["input_artifact"]["accepted_sha256"]` |
| `provenance_judgment_path` | `str` | yes | no null | `payload["input_artifact"]["provenance_judgment_path"]` |

`CandidateRepresentationStatus`

| Field | Type | Required | Allowed value |
|---|---|---|---|
| `candidate_status` | `Literal["not_proven"]` | yes | `not_proven` |
| `field_correctness_status` | `Literal["not_proven"]` | yes | `not_proven` |
| `source_truth_status` | `Literal["not_proven"]` | yes | `not_proven` |
| `taxonomy_compatibility_status` | `Literal["not_proven"]` | yes | `not_proven` |
| `production_parser_replacement_status` | `Literal["not_authorized"]` | yes | `not_authorized` |

`CandidateSourceLocator`

| Field | Type | Required | Null/default | Route semantics |
|---|---|---|---|---|
| `source_kind` | `CandidateRepresentationSourceKind` | yes | no null | discriminator |
| `source_ref` | `str | None` | yes | nullable | Docling `self_ref`; pdfplumber synthetic table/block id; EID HTML DOM id/anchor if accepted |
| `page_number` | `int | None` | yes | nullable | Docling/pdfplumber page; EID HTML `None` |
| `bbox` | `dict[str, float | str] | None` | yes | nullable | Docling bbox; pdfplumber usually `None`; EID HTML `None` |
| `url` | `str | None` | yes | nullable | EID HTML render URL; otherwise `None` |
| `dom_id` | `str | None` | yes | nullable | EID HTML DOM id/anchor; otherwise `None` |
| `table_index` | `int | None` | yes | nullable | route table ordinal |
| `row_index` | `int | None` | yes | nullable | route row ordinal |
| `column_index` | `int | None` | yes | nullable | route column ordinal |
| `char_start` | `int | None` | yes | nullable | pdfplumber text offset if present |
| `char_end` | `int | None` | yes | nullable | pdfplumber text offset if present |

`CandidateSectionNode`

| Field | Type | Required | Null/default | Projection source |
|---|---|---|---|---|
| `section_id` | `str` | yes | no null | `section["section_id"]` or stable derived id |
| `source_ref` | `str | None` | yes | nullable | section source ref / heading id |
| `heading_text` | `str` | yes | empty allowed only with projection issue | section/heading text |
| `heading_path` | `tuple[str, ...]` | yes | default `(heading_text,)` | section path when available |
| `heading_level` | `int | None` | yes | nullable | route-specific inferred level |
| `page_start` | `int | None` | yes | nullable | page span start |
| `page_end` | `int | None` | yes | nullable | page span end |
| `source_locator` | `CandidateSourceLocator` | yes | no null | route-specific locator |
| `content_hash` | `str | None` | yes | nullable | `section["content_hash"]` |
| `confidence` | `Literal["strong","usable","weak","blocked"]` | yes | default `usable` | route confidence |
| `excluded_reason` | `str | None` | yes | nullable | TOC/furniture/repeated title |

`CandidateTextBlock`

| Field | Type | Required | Null/default | Projection source |
|---|---|---|---|---|
| `block_id` | `str` | yes | no null | block id or derived stable id |
| `block_type` | `str` | yes | no null | paragraph/heading/note/list/caption/footnote/header-footer |
| `section_id` | `str | None` | yes | nullable | assigned section |
| `heading_path` | `tuple[str, ...]` | yes | default `()` | route heading path |
| `text` | `str` | yes | empty allowed with issue | block text |
| `normalized_text` | `str` | yes | default same as `text` | normalized block text |
| `source_locator` | `CandidateSourceLocator` | yes | no null | route-specific locator |
| `content_hash` | `str | None` | yes | nullable | content hash |
| `excluded_reason` | `str | None` | yes | nullable | TOC/furniture/repeated title |

`CandidateTableBlock`

| Field | Type | Required | Null/default | Projection source |
|---|---|---|---|---|
| `table_id` | `str` | yes | no null | `table["table_id"]` |
| `source_ref` | `str | None` | yes | nullable | Docling `self_ref`; pdfplumber table id; EID DOM/table id |
| `route_table_index` | `int` | yes | no null | `table["table_index"]` |
| `section_id` | `str | None` | yes | nullable | assigned section |
| `heading_path` | `tuple[str, ...]` | yes | default `()` | table heading path |
| `page_numbers` | `tuple[int, ...]` | yes | empty allowed for EID HTML | table page numbers |
| `source_locator` | `CandidateSourceLocator` | yes | no null | table locator |
| `bbox_by_page` | `tuple[dict[str, object], ...]` | yes | empty allowed | Docling bbox list; pdfplumber/EID may be empty |
| `caption` | `str | None` | yes | nullable | caption |
| `label` | `str | None` | yes | nullable | route label |
| `row_count` | `int` | yes | default 0 | table rows |
| `column_count` | `int` | yes | default 0 | table columns |
| `cell_count` | `int` | yes | default 0 | table cells |
| `table_family` | `str` | yes | default `unknown` | future classifier |
| `locator_stability` | `Literal["strong","usable","weak","blocked"]` | yes | default `usable` when cells exist else `blocked` | locator quality |
| `excluded_reason` | `str | None` | yes | nullable | TOC/furniture/repeated header |
| `failure_code` | `str | None` | yes | nullable | projection/table failure |
| `cells` | `tuple[CandidateTableCell, ...]` | yes | default `()` | projected cells |

`CandidateTableCell`

| Field | Type | Required | Null/default | Projection source |
|---|---|---|---|---|
| `cell_index` | `int` | yes | no null | cell ordinal |
| `row_start` | `int | None` | yes | nullable | Docling row offset / pdfplumber row index / EID row index |
| `row_end` | `int | None` | yes | nullable | Docling row offset end |
| `column_start` | `int | None` | yes | nullable | Docling col offset / pdfplumber column index / EID column index |
| `column_end` | `int | None` | yes | nullable | Docling col offset end |
| `row_span` | `int | None` | yes | nullable | route span |
| `column_span` | `int | None` | yes | nullable | route span |
| `row_label_path` | `tuple[str, ...]` | yes | default `()` | row labels if available |
| `column_header_path` | `tuple[str, ...]` | yes | default `()` | column labels if available |
| `text` | `str` | yes | empty allowed with issue | cell text |
| `normalized_text` | `str` | yes | default same as `text` | normalized cell text |
| `source_locator` | `CandidateSourceLocator` | yes | no null | cell locator |
| `cell_hash` | `str` | yes | derived if absent | hash of normalized text + locator |
| `locator_hash` | `str` | yes | derived if absent | stable locator hash |
| `stability` | `Literal["strong","usable","weak","blocked"]` | yes | default by locator completeness | locator quality |

`CandidateRepresentationDocument`

| Field | Type | Required | Null/default | Projection source |
|---|---|---|---|---|
| `schema_version` | `str` | yes | no null | payload schema version |
| `identity` | `CandidateRepresentationIdentity` | yes | no null | identity fields |
| `status` | `CandidateRepresentationStatus` | yes | no null | status fields |
| `summary_metrics` | `dict[str, object]` | yes | no null | payload summary metrics |
| `sections` | `tuple[CandidateSectionNode, ...]` | yes | default `()` | payload sections/headings |
| `text_blocks` | `tuple[CandidateTextBlock, ...]` | yes | default `()` | payload text_blocks/paragraphs |
| `tables` | `tuple[CandidateTableBlock, ...]` | yes | default `()` | payload tables |
| `route_failures` | `tuple[CandidateProjectionIssue, ...]` | yes | default `()` | failure taxonomy route failures |
| `projection_issues` | `tuple[CandidateProjectionIssue, ...]` | yes | default `()` | projection validation issues |
| `blocked_claims` | `tuple[str, ...]` | yes | no null | payload blocked claims |

`CandidateProjectionIssue`

| Field | Type | Required | Null/default |
|---|---|---|---|
| `issue_id` | `str` | yes | stable id |
| `severity` | `Literal["info","reviewable","blocking"]` | yes | no null |
| `source_kind` | `CandidateRepresentationSourceKind` | yes | no null |
| `location` | `str` | yes | JSON pointer or route locator |
| `message` | `str` | yes | no null |
| `failure_code` | `str | None` | yes | nullable |

`CandidateAnchorNote`

| Field | Type | Required | Null/default |
|---|---|---|---|
| `candidate_source_kind` | `CandidateRepresentationSourceKind` | yes | no null |
| `artifact_hash` | `str | None` | yes | nullable |
| `source_locator` | `dict[str, object]` | yes | no null |
| `page_number_or_null` | `int | None` | yes | nullable |
| `section_id_or_heading` | `str | None` | yes | nullable |
| `table_id` | `str | None` | yes | nullable |
| `row_locator` | `str | None` | yes | nullable |
| `row_label_path` | `tuple[str, ...]` | yes | default `()` |
| `column_header_path` | `tuple[str, ...]` | yes | default `()` |
| `cell_hash` | `str | None` | yes | nullable |
| `locator_hash` | `str` | yes | no null |
| `field_correctness_status` | `Literal["not_proven"]` | yes | `not_proven` |
| `source_truth_status` | `Literal["not_proven"]` | yes | `not_proven` |

All status fields must remain non-proof:

```text
candidate_status=not_proven
field_correctness_status=not_proven
source_truth_status=not_proven
taxonomy_compatibility_status=not_proven
production_parser_replacement_status=not_authorized
```

## 6. Projection Functions

Implement projection helpers that consume existing candidate envelope JSON payloads and return typed candidate internals:

```python
def project_candidate_representation(payload: Mapping[str, Any]) -> CandidateRepresentationDocument:
    ...


def build_candidate_anchor_note(
    *,
    document: CandidateRepresentationDocument,
    table: CandidateTableBlock,
    cell: CandidateTableCell,
) -> CandidateAnchorNote:
    ...
```

Projection requirements:

- validate `schema_version`;
- validate closed source kind;
- validate non-proof status fields;
- keep route-specific locator payloads;
- map Docling page/bbox/cell offsets if present;
- map pdfplumber row/column/header data with bbox allowed as `None`;
- map EID HTML blocked payload as document-level failure only;
- reject source truth/readiness claims;
- preserve failure taxonomy;
- not call parsers or read PDFs.

### 6.1 Route-specific locator payload rules

Docling payload rules:

- section locator uses `heading_id`/`section_id`, `page_number`, `bbox`, and content hash;
- table locator uses `self_ref`, `table_index`, `page_number`, `bbox`;
- cell locator uses `cell_index`, row/column offsets, spans, header flags, bbox and hashes;
- missing bbox is allowed only with `projection_issue.severity="reviewable"` unless the row is blocked/excluded.

pdfplumber payload rules:

- section locator uses section catalog id and optional character offsets;
- table locator uses page number + table index;
- cell locator uses table index + row/column index/header text;
- `bbox=None` is expected and must not be treated as a projection failure;
- page number is expected for tables.

EID HTML render payload rules:

- blocked payload remains document-level failure and should project zero sections/tables/cells;
- accepted future HTML payload uses render URL + DOM/anchor/table ordinal, not page number;
- `page_number=None` is expected and must not be treated as a projection failure;
- no raw XML/contextRef/unitRef/taxonomy claim may be inferred.

## 7. Candidate Anchor Note

`CandidateAnchorNote` is internal only. It may contain:

```text
candidate_source_kind
artifact_hash
source_locator
page_number_or_null
section_id_or_heading
table_id
row_locator
row_label_path
column_header_path
cell_hash
locator_hash
field_correctness_status
source_truth_status
```

It must not mutate public `EvidenceAnchor` or add public source kinds.

## 8. Tests

Required tests:

- route enum accepts exactly three candidate source kinds;
- non-proof status guard rejects `source_truth_status=proven`;
- projection accepts minimal Docling-like envelope with bbox/cells;
- projection accepts minimal pdfplumber-like envelope with `bbox=None`;
- projection accepts EID HTML blocked envelope and exposes route failure;
- projection rejects unknown source kind;
- projection rejects production parser replacement claim;
- anchor note includes candidate status fields and locator hash;
- Docling projection preserves bbox, page number, row/column offsets, spans and header flags;
- pdfplumber projection preserves row/column/header data while keeping `bbox=None`;
- EID blocked projection yields document-level route failure and no sections/tables/cells;
- tests fail if route-specific locator payloads are collapsed into a single lossy shape;
- no public `fund_agent.fund.documents` export;
- no Service/UI/Host/renderer/quality gate imports candidate internals.

Tests must use small synthetic payloads or tiny excerpts. They must not read the committed full JSONs by default and must not run Docling/pdfplumber conversion.

## 9. Validation Commands

Implementation gate should run:

```text
uv run pytest tests/fund/documents/test_candidate_representation_models.py tests/fund/documents/test_candidate_representation_projection.py tests/fund/documents/test_docling_no_consumption_guards.py -q
uv run ruff check fund_agent/fund/documents/candidates/representation_models.py fund_agent/fund/documents/candidates/representation_projection.py tests/fund/documents/test_candidate_representation_models.py tests/fund/documents/test_candidate_representation_projection.py
git diff --check
```

Optional only if implementation touches existing handler/export tests:

```text
uv run pytest tests/fund/documents/test_candidate_representation_handlers.py tests/fund/documents/test_candidate_representation_export.py -q
```

## 10. Review Checklist

Reviewers must check:

- no production parser/repository/source behavior change;
- no public `EvidenceAnchor` schema change;
- no public `documents.__init__` export;
- candidate source kinds remain internal;
- route-specific locator differences are not erased;
- blocked EID HTML route does not become source truth;
- tests remain no-live and no-conversion;
- README update does not claim readiness or parser replacement.

## 11. Stop Conditions

Stop before implementation if:

- implementation would require modifying public `EvidenceAnchor`;
- implementation would require modifying `FundDocumentRepository`;
- implementation would route candidate JSON to Service/UI/Host/renderer/quality gate;
- implementation would need live/network or full conversion;
- implementation would make Docling a production baseline without field-family correctness evidence.

## 12. Next Gate Recommendation

Immediate next gate:

`Candidate Representation Schema No-live Implementation Plan Review Gate`

If accepted:

`Candidate Representation Schema No-live Implementation Gate`

Then:

`Candidate Representation Locator Stability Evidence Gate`

Deferred:

- field-family correctness pilot;
- production `FundDisclosureDocument` integration;
- public `EvidenceAnchor` mapping acceptance;
- release/readiness/PR.

## 13. Final Verdict

`VERDICT: READY_FOR_PLAN_REVIEW_NOT_READY`
