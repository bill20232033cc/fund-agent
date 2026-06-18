# FundDisclosureDocument Candidate Source No-live Implementation Plan

Date: 2026-06-18

Gate: `FundDisclosureDocument Candidate Source No-live Implementation Planning Gate`

Role: planning worker only

Readiness state: `NOT_READY`

Verdict: `PLAN_FIXED_READY_FOR_REVIEW_NOT_READY`

## 1. Scope

This plan defines the exact code-generation-ready implementation contract for `FundDisclosureDocument`
candidate schema. It bridges the accepted candidate source schema plan
(`docs/reviews/funddisclosuredocument-candidate-source-schema-plan-20260614.md`) to a future
implementation gate.

This plan does NOT authorize:

- code implementation, editing, or deletion;
- production parser replacement;
- `FundDocumentRepository.load_annual_report()` behavior change;
- `EvidenceAnchor` schema change or `EvidenceSourceKind` expansion;
- CHAPTER_CONTRACT change;
- extractor/renderer/audit/source-label or production consumer integration;
- Service / UI / Host / renderer / quality gate direct access to candidate internals or EID HTML render;
- raw XML/XBRL route;
- field correctness, taxonomy compatibility, source truth, readiness or release claims;
- `FundDataExtractor.extract()` facade integration for `fund_disclosure_document.v1`;
- actual field-family extraction from `FundDisclosureDocument`;
- source policy, fallback, Eastmoney/CNINFO, provider defaults, repair budget, annual-period LLM route,
  EvidenceSourceKind, or production repository behavior change.

## 2. Evidence Reviewed

- `AGENTS.md`
- `docs/design.md` v2.21 (Fund documents / Processor-Extractor / Docling reorientation sections)
- `docs/implementation-control.md` (current gate and queue)
- `docs/current-startup-packet.md`
- `docs/reviews/funddisclosuredocument-candidate-source-schema-plan-20260614.md`
- `docs/reviews/funddisclosuredocument-candidate-source-schema-plan-controller-judgment-20260614.md`
- `docs/reviews/s4-concrete-funddisclosuredocument-processor-final-closeout-controller-judgment-20260618.md`
- Current code surfaces:
  - `fund_agent/fund/documents/models.py` — `AnnualReportSourceFailureCategory`, `EvidenceAnchor`-adjacent types
  - `fund_agent/fund/extractors/models.py` — `EvidenceAnchor`, `EvidenceSourceKind`
  - `fund_agent/fund/processors/contracts.py` — `FundDisclosureDocumentIntermediate` Protocol,
    `CandidateBoundaryStatus`, `FundIntermediateKind`, `FundProcessorDispatchKey`, gap model
  - `fund_agent/fund/processors/fund_disclosure_processor.py` — S4 skeleton processor
  - `fund_agent/fund/processors/fund_disclosure_dispatch.py` — `admit_disclosure_intermediate()`
  - `fund_agent/fund/documents/candidates/models.py` — existing Docling candidate models (reference only)
  - `fund_agent/fund/documents/candidates/failures.py` — existing Docling failure mapping (reference only)
  - `tests/fund/documents/test_docling_*.py` — existing candidate tests (reference only)
  - `tests/fund/processors/test_fund_disclosure_processor.py` — S4 processor tests (reference only)

## 3. Current Code Facts and Truth Constraints

### 3.1 Closed Literals That Must NOT Be Mutated

| Type | Current literal | Constraint |
|------|----------------|------------|
| `EvidenceSourceKind` | `"annual_report"`, `"external_api"`, `"derived"` | Must remain closed; `eid_xbrl_html_render_candidate` must NOT be added |
| `AnnualReportSourceName` | `"eid"`, `"eastmoney"` | Must remain closed; no new production source name |
| `AnnualReportSourceFailureCategory` | `"not_found"`, `"unavailable"`, `"schema_drift"`, `"identity_mismatch"`, `"integrity_error"` | Must remain closed; candidate failures must map INTO these five |
| `ANNUAL_REPORT_DOCUMENT_KIND` | `"annual_report"` | Must remain unchanged |
| `EvidenceAnchor` dataclass | 7 fields including `source_kind: EvidenceSourceKind` | Schema must remain unchanged |
| `FundIntermediateKind` | already includes `"fund_disclosure_document.v1"` | Already accepted; no expansion needed. `"eid_xbrl_html_render_candidate.v1"` is a candidate source artifact kind, NOT a processor dispatch key and NOT an `intermediate_kind` value |

### 3.2 Existing Infrastructure Already Accepted

- `FundDisclosureDocumentIntermediate` Protocol (in `contracts.py`) — defines minimum contract for any
  `FundDisclosureDocument`-like object: `document_kind`, `fund_code`, `report_year`, `intermediate_kind`,
  `source_provenance`, `candidate_boundary`, `failure_class`.
- `CandidateBoundaryStatus` — frozen dataclass enforcing `candidate_only=True`, `field_correctness_status="not_proven"`,
  `source_truth_status="not_proven"`, `parser_replacement_authorized=False`, `readiness_status="not_ready"`.
- `FundProcessorDispatchKey` — already accepts `intermediate_kind="fund_disclosure_document.v1"`.
- S4 `FundDisclosureDocumentProcessor` — skeleton processor that validates identity, calls
  `admit_disclosure_intermediate()`, and returns all six field families as `missing`.
- `FundProcessorRegistry.create_default()` — already resolves `active_fund + annual_report + fund_disclosure_document.v1`.
- `FundDataExtractor.extract()` — does NOT consume `fund_disclosure_document.v1`; stays unchanged.
- `admit_disclosure_intermediate()` (in `fund_disclosure_dispatch.py`) — consumes
  `FundDisclosureDocumentIntermediate`, maps `failure_class` to canonical gap codes.

### 3.3 Existing Candidate Internals (Reference Only)

The Docling candidate models in `fund_agent/fund/documents/candidates/models.py` provide reference
patterns (frozen dataclasses, `CandidateSourceKind`, `LocatorStability`, `CandidateFailureCode`,
`CandidateTableCellLocator`), but are bound to `docling_pdf_candidate` source kind. The new
`FundDisclosureDocument` schema must be independent, owned under Fund documents internals, and
source-artifact-kind-agnostic (supporting `eid_xbrl_html_render_candidate.v1` and potentially other candidate
source artifact kinds — distinct from `intermediate_kind` which is always `"fund_disclosure_document.v1"`).

### 3.4 Constraints From Accepted Schema Plan Controller Judgment

From `docs/reviews/funddisclosuredocument-candidate-source-schema-plan-controller-judgment-20260614.md`:

| Constraint | Source |
|------------|--------|
| Option B (intermediate candidate object without mutating `EvidenceAnchor`) is the accepted strategy | Judgment §4 |
| Candidate failure classes must map to canonical five categories | Judgment §4 |
| Next implementation planning may cover only candidate representation internals | Judgment §4 |
| `redirect_unavailable` and `render_unavailable` need testable split rules | Judgment §5 |
| Same-report comparison has not run; do not plan consumer integration | Judgment §5 |
| Ordinary non-REIT annual/interim coverage remains unproven | Judgment §5 |
| Field correctness, unit/date, raw XML/taxonomy, source truth remain unproven | Judgment §5 |

### 3.5 Constraints From S4 Final Closeout

From `docs/reviews/s4-concrete-funddisclosuredocument-processor-final-closeout-controller-judgment-20260618.md`:

| Constraint |
|------------|
| `FundDisclosureDocument` production schema NOT yet implemented |
| `FundDataExtractor.extract()` does NOT consume `fund_disclosure_document.v1` |
| Actual field-family extraction deferred to S6+ |
| S5 facade integration deferred to after schema planning/implementation |
| No public `EvidenceSourceKind` / `EvidenceAnchor.source_kind` expansion |
| No Service/UI/Host/renderer/quality-gate direct parser consumption |

## 4. Why Schema Implementation Planning is the Correct Next Gate

The gate sequence constraint is:

```
S4 skeleton processor (DONE)
  → Schema no-live implementation planning (THIS GATE)
    → Schema no-live implementation gate (FUTURE)
      → S5 facade integration gate (FUTURE)
        → S6+ field-family extraction gate (FUTURE)
```

Rationale:

1. **S4 skeleton exists but has nothing to admit.** `FundDisclosureDocumentProcessor` calls
   `admit_disclosure_intermediate(intermediate, context)` but no concrete `FundDisclosureDocument`
   dataclass exists that satisfies `FundDisclosureDocumentIntermediate`. The processor is a validated
   empty shell.

2. **Schema must exist before facade integration.** S5 will wire `FundDataExtractor.extract()` to
   consume `fund_disclosure_document.v1` through the processor registry. Without a concrete schema,
   there is nothing to wire.

3. **Schema must exist before field extraction.** S6+ will implement actual field-family extraction
   from `FundDisclosureDocument` sections/tables/blocks. Without a schema defining those structures,
   extraction has no input contract.

4. **Schema implementation is internal-only.** It creates no production behavior change, touches no
   repository/source/parser/facade, and can be validated entirely through no-live construction,
   serialization, failure mapping, and non-consumption tests.

5. **Same-report comparison is deferred but not blocking.** The controller judgment identifies
   same-report comparison as a deferred evidence gate, not a prerequisite for internal schema
   implementation. Schema implementation validates structural correctness, not field correctness.

## 5. Exact Future Implementation Write Set

### 5.1 Allowed Files (implementation gate only; NOT this planning gate)

| File | Purpose |
|------|---------|
| `fund_agent/fund/documents/candidates/fund_disclosure_document.py` | **New.** `FundDisclosureDocument` dataclass, `FundDisclosureDocumentIdentity`, `FundDisclosureDocumentSection`, `FundDisclosureDocumentTableBlock`, `FundDisclosureDocumentCellLocator`, `FundDisclosureDocumentFailure`, serialization helpers |
| `fund_agent/fund/documents/candidates/fund_disclosure_failure_mapping.py` | **New.** EID HTML render candidate failure codes → canonical `AnnualReportSourceFailureCategory` mapping. Imports `AnnualReportSourceFailureCategory` from `fund_agent.fund.documents.models` and follows the existing mapping pattern in `fund_agent.fund.documents.candidates.failures` |
| `tests/fund/documents/test_fund_disclosure_document.py` | **New.** Schema construction, serialization round-trip, failure mapping, locator stability, non-consumption guard tests |
| `tests/fund/documents/test_fund_disclosure_failure_mapping.py` | **New.** Failure mapping unit tests including `redirect_unavailable` / `render_unavailable` split |

### 5.2 Explicitly Forbidden Files (must NOT be touched)

| File | Reason |
|------|--------|
| `fund_agent/fund/extractors/models.py` | `EvidenceSourceKind` must remain closed |
| `fund_agent/fund/documents/models.py` | `AnnualReportSourceFailureCategory` must remain closed |
| `fund_agent/fund/documents/repository.py` | No repository behavior change |
| `fund_agent/fund/documents/sources.py` | No source policy change |
| `fund_agent/fund/processors/contracts.py` | `FundDisclosureDocumentIntermediate` Protocol already accepted; no change needed |
| `fund_agent/fund/processors/fund_disclosure_processor.py` | S4 skeleton already accepted; no change needed |
| `fund_agent/fund/processors/fund_disclosure_dispatch.py` | Admission helper already accepted; no change needed |
| `fund_agent/fund/data_extractor.py` | `FundDataExtractor.extract()` must not consume `fund_disclosure_document.v1` |
| `fund_agent/fund/template/renderer.py` | No renderer change |
| `fund_agent/services/*` | No Service layer change |
| `fund_agent/ui/*` | No UI layer change |
| `fund_agent/host/*` | No Host layer change |
| `fund_agent/agent/*` | No Agent layer change |
| `fund_agent/fund/audit/*` | No audit change |
| `fund_agent/fund/analysis/*` | No analysis change |
| `docs/design.md` | No design truth change |
| `docs/implementation-control.md` | No control truth change (except gate status update after implementation) |
| `README.md`, `fund_agent/README.md`, `fund_agent/fund/README.md` | No README change in this gate; deferred to implementation gate |

## 6. Candidate Object Schema

### 6.1 Module Ownership

All new types live under `fund_agent/fund/documents/candidates/`. This is the established location
for candidate document representation internals, already housing Docling candidate models. The new
`FundDisclosureDocument` schema is a sibling, not a replacement.

The `FundDisclosureDocument` dataclass must satisfy `FundDisclosureDocumentIntermediate` Protocol
(already defined in `fund_agent/fund/processors/contracts.py`). This means it must expose:
`document_kind`, `fund_code`, `report_year`, `intermediate_kind`, `source_provenance`,
`candidate_boundary`, `failure_class`.

**Critical: `FundDisclosureDocument.intermediate_kind` is fixed to `"fund_disclosure_document.v1"`.**
This is the processor dispatch key that S4 `FundDisclosureDocumentProcessor` validates via
`context.intermediate_kind == intermediate.intermediate_kind`. EID HTML render provenance is a
separate concern tracked on `FundDisclosureDocumentIdentity.source_artifact_kind` (see §6.2),
not on `intermediate_kind`. Using any other value for `intermediate_kind` would cause the processor
to reject the intermediate with an `input_type_mismatch` gap code instead of reaching the
candidate-boundary / fully-gapped missing behavior.

### 6.2 Identity: `FundDisclosureDocumentIdentity`

Frozen dataclass capturing artifact-level identity and fetch/render metadata.

```text
FundDisclosureDocumentIdentity (frozen dataclass):
  # Source identity — records where the candidate artifact came from.
  # source_artifact_kind tracks the render provenance (e.g. "eid_xbrl_html_render_candidate.v1").
  # This is NOT an intermediate_kind / processor dispatch key — it describes the artifact source.
  source_artifact_kind: Literal["eid_xbrl_html_render_candidate.v1"]  # or future candidate artifact kinds
  source_kind: Literal["eid_xbrl_html_render_candidate"]  # short form without version
  fund_code: str                                       # 6-digit
  fund_id: str | None                                  # EID platform fund ID
  instance_id: str | None                              # EID公告实例ID (upload_info_id)
  report_year: int                                     # positive integer
  report_type_code: str | None                         # EID report type code
  report_type_label: str | None                        # EID report type description
  report_send_date: str | None                         # EID report send date
  source_list: tuple[str, ...] | None                  # candidate source list (e.g. EID index URL origins)

  # Fetch/render metadata
  index_url: str | None                                # EID公告列表URL
  instance_view_url: str | None                        # EID公告详情URL
  render_url: str | None                               # final HTML render URL
  redirect_location: str | None                        # observed redirect target
  content_type: str | None                             # HTTP Content-Type of render
  content_length: int | None                           # HTTP Content-Length of render
  content_hash: str | None                             # SHA-256 of render body
  fetched_at: str | None                               # ISO-8601 fetch timestamp
  render_status: str | None                            # "ok", "redirect_followed", "timeout", etc.
  navigation_present: bool                             # whether render page has navigation structure

  # Candidate boundary (fixed values enforced by __post_init__)
  candidate_only: Literal[True] = True
  field_correctness_status: Literal["not_proven"] = "not_proven"
  source_truth_status: Literal["not_proven"] = "not_proven"
  parser_replacement_authorized: Literal[False] = False
  readiness_status: Literal["not_ready"] = "not_ready"
```

`__post_init__` must enforce:
- `source_artifact_kind` is a recognized candidate source artifact kind
- `source_kind` matches `source_artifact_kind` without the `.v1` suffix
- `fund_code` is 6-digit
- `report_year` > 0
- All five boundary fields have their exact non-proof values
- `content_hash`: `None` valid; 64-char hex valid; empty string, non-hex, wrong length invalid (see §10.1 for explicit test requirements)

### 6.3 Navigation: `FundDisclosureDocumentNavigationNode`

Frozen dataclass for ordered navigation structure extracted from render page.

```text
FundDisclosureDocumentNavigationNode (frozen dataclass):
  node_id: str                                         # stable navigation node ID
  title_text: str                                      # raw title text
  title_normalized: str                                # CJK/whitespace normalized
  level: int                                           # heading level (1-based)
  parent_node_id: str | None
  child_node_ids: tuple[str, ...]
  section_id: str | None                               # resolved section anchor
  locator_stability: LocatorStability                  # "strong" / "usable" / "weak" / "blocked"
  order_index: int                                     # 0-based document order
```

### 6.4 Sections: `FundDisclosureDocumentSection`

Frozen dataclass for document sections identified from navigation + content.

```text
FundDisclosureDocumentSection (frozen dataclass):
  section_id: str                                      # stable section anchor
  heading_text_raw: str
  heading_text_normalized: str
  heading_path: tuple[str, ...]                        # breadcrumb path
  heading_level: int | None
  start_page_or_offset: int | None                     # render-specific locator
  end_page_or_offset: int | None
  child_section_ids: tuple[str, ...]
  locator_stability: LocatorStability
  normalization_notes: tuple[str, ...]                 # normalization steps applied
```

### 6.5 Paragraph Blocks: `FundDisclosureDocumentParagraphBlock`

```text
FundDisclosureDocumentParagraphBlock (frozen dataclass):
  block_id: str
  block_type: Literal["paragraph", "heading", "note", "list_item", "caption", "footnote"]
  section_id: str | None
  heading_path: tuple[str, ...]
  text_raw: str
  text_normalized: str
  content_hash: str                                    # SHA-256 of normalized text
  locator_stability: LocatorStability
  normalization_applied: tuple[str, ...]
```

### 6.6 Table Blocks: `FundDisclosureDocumentTableBlock`

```text
FundDisclosureDocumentTableBlock (frozen dataclass):
  table_id: str                                        # stable table identifier
  section_id: str | None                               # parent section anchor
  heading_text: str | None                             # nearest heading or caption
  heading_path: tuple[str, ...]
  table_index_under_section: int | None                # ordinal within parent section
  table_caption_or_nearby_heading: str | None
  header_rows: tuple[int, ...]                         # 0-based row indices of header
  body_rows: tuple[int, ...]                           # 0-based row indices of body
  row_count: int
  column_count: int
  merged_header_detected: bool
  cells: tuple[FundDisclosureDocumentCellLocator, ...]
  locator_stability: LocatorStability
  extraction_note: str | None
```

### 6.7 Cell Locators: `FundDisclosureDocumentCellLocator`

```text
FundDisclosureDocumentCellLocator (frozen dataclass):
  cell_id: str                                         # stable cell identifier
  table_id: str                                        # parent table
  render_url: str | None                               # source render URL for back-tracing
  section_anchor: str | None                           # parent section
  heading_path: tuple[str, ...]
  table_index_under_section: int | None
  row_index: int                                       # 0-based normalized row
  column_index: int                                    # 0-based normalized column
  row_label_path: tuple[str, ...]                      # row header breadcrumb
  column_header_path: tuple[str, ...]                  # column header breadcrumb
  cell_text: str                                       # raw cell text
  cell_text_normalized: str                            # normalized text
  cell_hash: str                                       # SHA-256 of normalized text
  is_header_cell: bool
  locator_stability: LocatorStability
  normalization_applied: tuple[str, ...]
```

### 6.8 Locator Stability Classification

**Import from existing module.** `LocatorStability` is already defined in
`fund_agent.fund.documents.candidates.models` as:

```python
LocatorStability = Literal["strong", "usable", "weak", "blocked"]
```

The implementation must import and reuse this existing type — **redefining `LocatorStability` is forbidden.**

| Value | Meaning |
|-------|---------|
| `strong` | Section/table/cell identity is deterministic from the same render URL |
| `usable` | Identity is reasonably stable but may vary across re-fetches of the same report |
| `weak` | Identity depends on fragile render features (e.g., generated IDs, timestamp-dependent ordering) |
| `blocked` | Cannot produce a stable locator; must not be used for field projection |

### 6.9 Serialization / Deserialization

Each dataclass must support:

- `to_dict() -> dict[str, object]` — JSON-compatible serialization
- `from_dict(data: dict[str, object]) -> Self` — classmethod deserialization with validation
- JSON round-trip: `from_dict(obj.to_dict()) == obj`

Serialization must:
- Use `dataclasses.asdict()` or explicit projection
- Serialize `tuple` as JSON array
- Serialize `Literal` as string
- Handle `None` fields
- NOT serialize any field that contains raw PDF, raw HTML, or provider credentials

### 6.10 Candidate Boundary Fields

The top-level `FundDisclosureDocument` must carry a single `candidate_boundary` field:

```python
from fund_agent.fund.processors.contracts import CandidateBoundaryStatus

@dataclass(frozen=True, slots=True)
class FundDisclosureDocument:
    ...
    candidate_boundary: CandidateBoundaryStatus = CandidateBoundaryStatus(
        candidate_only=True,
        field_correctness_status="not_proven",
        source_truth_status="not_proven",
        parser_replacement_authorized=False,
        readiness_status="not_ready",
    )
```

**Do not duplicate the five separate boundary fields** (`candidate_only`, `field_correctness_status`,
etc.) on `FundDisclosureDocument`. Use the existing `CandidateBoundaryStatus` frozen dataclass from
`fund_agent.fund.processors.contracts`, which already enforces the not_proven/not_ready semantics in
its own `__post_init__`.

`FundDisclosureDocumentIdentity` may keep its inline five boundary fields (they serve a separate
identity-level concern), but those fields must be validated against `CandidateBoundaryStatus`
semantics — specifically, identity boundary fields must not contradict the canonical boundary.
Tests must prove exact `not_proven`/`not_ready` semantics (see §10.1).

### 6.11 Failure Class

`FundDisclosureDocument` must carry:

```text
failure_class: AnnualReportSourceFailureCategory | None
```

This is the canonical failure mapping result. It must be `None` when the render was successfully
fetched and parsed. When non-None, it must be one of the five canonical categories.

The internal failure codes (see §7) are candidate-internal only. The `failure_class` field on
`FundDisclosureDocument` is the MAPPED canonical category, not the internal code.

## 7. Failure Mapping Rules

### 7.1 Internal Failure Codes (Candidate-only)

**Source-failure codes** (map to `AnnualReportSourceFailureCategory`):

```text
FundDisclosureCandidateSourceFailureCode = Literal[
    "index_unavailable",
    "list_row_missing",
    "identity_mismatch",
    "redirect_unavailable",
    "render_unavailable",
    "render_domain_mismatch",
    "render_structure_missing",
    "locator_unstable",
]
```

**Projection-blocker statuses** (do NOT map to `AnnualReportSourceFailureCategory` in this gate):

```text
FundDisclosureProjectionBlocker = Literal[
    "value_unvalidated",
    "raw_xml_not_proven",
]
```

`value_unvalidated` and `raw_xml_not_proven` are candidate boundary statuses indicating that
field projection is blocked, not that the source artifact is unavailable/broken/drifted. They
must NOT be mapped to `AnnualReportSourceFailureCategory` unless a future gate provides a direct
reason to do so. The current gate treats them as projection-blocker statuses only — they appear
on `FundDisclosureDocument` as boundary fields, not as `failure_class` values.

**Unified code for convenience** (combines both):

```text
FundDisclosureCandidateFailureCode = FundDisclosureCandidateSourceFailureCode | FundDisclosureProjectionBlocker
```

All codes are candidate-internal. They must NOT be exposed to `EvidenceAnchor.source_kind`,
`AnnualReportSourceFailureCategory`, or any production type.

### 7.2 Canonical Mapping Table

Only `FundDisclosureCandidateSourceFailureCode` values map to canonical categories.
`FundDisclosureProjectionBlocker` values (`value_unvalidated`, `raw_xml_not_proven`) are
projection-blocker statuses that do NOT appear as `failure_class` values (see §7.1).

| Candidate failure | Canonical category | Rule |
|-------------------|-------------------|------|
| `index_unavailable` | `unavailable` | EID index cannot be fetched/parsed due to temporary access/service issue |
| `list_row_missing` | `not_found` | EID list does not expose a matching concrete row |
| `identity_mismatch` | `identity_mismatch` | Fund/year/report identity conflicts |
| `redirect_unavailable` | `identity_mismatch`, `unavailable`, or `not_found` | **See total ordered decision table in §7.3** |
| `render_unavailable` | `schema_drift`, `unavailable`, or `not_found` | **See total ordered decision table in §7.3** |
| `render_domain_mismatch` | `identity_mismatch` | Redirect leaves official EID domain |
| `render_structure_missing` | `schema_drift` | Expected render contract (title/navigation/sections) absent |
| `locator_unstable` | `schema_drift` | Render accessible but cannot produce deterministic locators |

Projection-blocker statuses (do NOT map in this gate):

| Status | Meaning |
|--------|---------|
| `value_unvalidated` | Rendered value exists but fails validation; candidate boundary status that blocks field projection. Does NOT map to `AnnualReportSourceFailureCategory` unless a future gate provides a direct reason |
| `raw_xml_not_proven` | HTML route remains candidate; raw XML proof is separate. Candidate boundary status that blocks field projection. Does NOT map to `AnnualReportSourceFailureCategory` unless a future gate provides a direct reason |

### 7.3 `redirect_unavailable` / `render_unavailable` Split Rules

This is the binding residual from the schema plan controller judgment (§5).

The split rules use a typed context object (not loose keyword arguments — see §7.4).

#### 7.3.1 `redirect_unavailable` Total Ordered Decision Table

Evaluated top-to-bottom; the first matching row determines the canonical category.

| Priority | Fact pattern | Canonical category | Rationale |
|----------|-------------|-------------------|-----------|
| 1 | `redirect_domain` differs from known official EID domain | `identity_mismatch` | Non-official redirect target is identity failure regardless of HTTP status. Covers mixed facts: non-EID redirect + 5xx → `identity_mismatch`; non-EID redirect + 4xx → `identity_mismatch` |
| 2 | `http_status` is 5xx, connection timeout, DNS failure, or TLS error | `unavailable` | Temporary infrastructure failure on redirect target; retry with backoff may resolve |
| 3 | `http_status` is 4xx (404, 410) | `not_found` | Redirect target resource gone; not temporary |
| 4 | Insufficient facts (`http_status` is `None` or cannot determine sub-condition) | `unavailable` | Conservative default: treat as temporary |

#### 7.3.2 `render_unavailable` Total Ordered Decision Table

Evaluated top-to-bottom; the first matching row determines the canonical category.

| Priority | Fact pattern | Canonical category | Rationale |
|----------|-------------|-------------------|-----------|
| 1 | HTTP 200 and `body_empty` is `True` | `schema_drift` | Stable response contract changed (empty body); not temporary |
| 2 | HTTP 200 and `body_is_html` is `False` (non-empty but non-HTML body) | `schema_drift` | Stable response contract changed (non-HTML body); not temporary |
| 3 | HTTP 200 and `body_is_html` is `True` and `structure_absence_observed_consistently` is `True` | `schema_drift` | HTML body returned but expected structure (navigation/sections) consistently absent across retries |
| 4 | `http_status` is 5xx, connection timeout, DNS failure, or TLS error | `unavailable` | Temporary infrastructure failure on render URL |
| 5 | `http_status` is 4xx (404, 410) on known render URL | `not_found` | Known render URL returns 4xx; resource gone, not temporary |
| 6 | Insufficient facts (`http_status` is `None`, `body_empty` is `False`, `body_is_html` is `True`, no consistent structure absence observed) | `unavailable` | Conservative default: treat as temporary |

#### 7.3.3 Mixed-Fact Coverage

The total ordered tables above cover all required mixed-fact combinations:

| Mixed fact | Table | Priority row | Result |
|------------|-------|-------------|--------|
| Non-EID redirect + HTTP 5xx | `redirect_unavailable` | 1 (domain mismatch first) | `identity_mismatch` |
| Non-EID redirect + HTTP 4xx | `redirect_unavailable` | 1 (domain mismatch first) | `identity_mismatch` |
| Known render URL 404 | `render_unavailable` | 5 | `not_found` |
| HTTP 200 empty body | `render_unavailable` | 1 | `schema_drift` |
| HTTP 200 non-HTML body | `render_unavailable` | 2 | `schema_drift` |
| HTML body with consistent structure absence | `render_unavailable` | 3 | `schema_drift` |
| Insufficient facts (both tables) | `redirect_unavailable` / `render_unavailable` | Last row in each | `unavailable` |

### 7.4 Mapping Context Object and Function Contract

**Typed context object** (replaces loose keyword-only arguments):

```text
FundDisclosureFailureContext (frozen dataclass):
  http_status: int | None = None
  error_type: str | None = None
  redirect_target_url: str | None = None
  redirect_domain: str | None = None
  official_domain_status: str | None = None
  render_url_known: bool = False
  body_empty: bool = False
  body_is_html: bool = True
  navigation_present: bool | None = None
  sections_present: bool | None = None
  retry_count: int = 0
  structure_absence_observed_consistently: bool = False
```

Fields not relevant to a particular failure path may be left at their defaults. The mapping
function only reads the fields needed for the specific `failure_code`.

**Mapping function:**

```text
map_fund_disclosure_failure_to_source_category(
    failure_code: FundDisclosureCandidateSourceFailureCode,
    context: FundDisclosureFailureContext | None = None,
) -> AnnualReportSourceFailureCategory
```

This function must:
- Map every `FundDisclosureCandidateSourceFailureCode` to exactly one canonical category.
- For `redirect_unavailable` and `render_unavailable`, use `context` fields to apply split rules per §7.3.
- For codes that don't need context (e.g., `index_unavailable` → `unavailable`), accept `context=None`.
- Raise `ValueError` (not `KeyError`) for projection blockers (`value_unvalidated`, `raw_xml_not_proven`) and unknown codes (fail-closed).
- Tests must instantiate `FundDisclosureFailureContext` for every priority row in the §7.3 total
  ordered decision tables plus all mixed-fact combinations in §7.3.3.

## 8. Preserving EvidenceAnchor.source_kind Without Expansion

The plan enforces:

1. **No new `EvidenceSourceKind` value.** `eid_xbrl_html_render_candidate.v1` is a candidate-internal
   `source_artifact_kind` string in `FundDisclosureDocumentIdentity`, NOT an `EvidenceSourceKind` literal value.
   The short form `eid_xbrl_html_render_candidate` (without `.v1`) is stored in
   `FundDisclosureDocumentIdentity.source_kind` for display/lookup convenience.

2. **Candidate locator → EvidenceAnchor projection strategy is deferred.** This gate does not
   choose `EvidenceAnchor.source_kind`, `page_number`, `note` encoding, renderer label, audit
   behavior, source-label behavior, consumer integration, or field projection strategy. All
   projection decisions are routed to a future gate after same-report EID HTML render versus
   current pdfplumber representation evidence. This schema implementation gate defines candidate
   internals only.

3. **`EvidenceAnchor` schema is unchanged.** The 7 existing fields remain as-is. No new fields.

4. **`EvidenceSourceKind` literal is unchanged.** The 3 existing values remain as-is.

5. **Test guard:** A non-consumption test must prove that `FundDisclosureDocument` does not import
   or reference `EvidenceAnchor` or `EvidenceSourceKind` from `fund_agent/fund/extractors/models.py`.
   Candidate internals may reference `AnnualReportSourceFailureCategory` from
   `fund_agent/fund/documents/models.py` (for failure mapping only), but must not import
   `EvidenceAnchor` or `EvidenceSourceKind`.

## 9. Non-Consumption Guards

### 9.1 AST-Based Guarded-Tree Test (Primary)

The implementation must provide an AST-based guarded-tree test mirroring the exact pattern in
`tests/fund/documents/test_docling_no_consumption_guards.py`. This test must:

- Scan Python files via `ast.parse()` and `ast.walk()`, checking `ast.Import` and `ast.ImportFrom` nodes.
- Scan at least these paths:
  - `fund_agent/services/`
  - `fund_agent/ui/`
  - `fund_agent/host/`
  - `fund_agent/agent/`
  - `fund_agent/fund/template/`
  - `fund_agent/fund/audit/`
  - `fund_agent/fund/extractors/`
  - `fund_agent/fund/report_quality_validation.py`
- Forbidden import prefixes must include at minimum:
  - `fund_agent.fund.documents.candidates.fund_disclosure_document`
  - `fund_agent.fund.documents.candidates.fund_disclosure_failure_mapping`
- Public `__init__` surface import checks may remain as additional (secondary) validation, not primary.

The test function naming must follow the existing convention:
`test_service_ui_host_renderer_audit_quality_and_extractors_do_not_import_fund_disclosure_candidates()`.

### 9.2 Additional Boundary Enforcement

The implementation must also prove through no-live tests that:

| Guard | Test approach |
|-------|--------------|
| `FundDisclosureDocument` does not import `EvidenceAnchor` or `EvidenceSourceKind` | AST import analysis on candidate module itself |
| `FundDocumentRepository.load_annual_report()` behavior unchanged | Call existing test suite |
| `FundDataExtractor.extract()` does not import or consume `FundDisclosureDocument` | AST import check + existing test suite |
| Current `EvidenceSourceKind` literal values unchanged | Assert exact tuple |
| Current `AnnualReportSourceFailureCategory` literal values unchanged | Assert exact tuple |

### 9.3 How FundDisclosureDocument Stays Internal

The `FundDisclosureDocument` dataclass:

- Lives only in `fund_agent/fund/documents/candidates/` (Fund documents internal).
- Is consumed only by `FundDisclosureDocumentProcessor` (already behind `FundProcessorRegistry`).
- Is not re-exported from `fund_agent/fund/__init__.py` or any public package `__init__.py`.
- Is not imported by Service, UI, Host, Agent, renderer, or quality gate modules.
- Satisfies `FundDisclosureDocumentIntermediate` Protocol, which is the ONLY contract visible
  outside `fund_agent/fund/documents/candidates/`.

The `FundDisclosureDocumentIntermediate` Protocol in `contracts.py` already defines the minimum
surface area: `document_kind`, `fund_code`, `report_year`, `intermediate_kind`, `source_provenance`,
`candidate_boundary`, `failure_class`. No code outside the processor boundary may access
`FundDisclosureDocument` sections, tables, blocks, or cell locators directly.

## 10. Required No-live Tests and Exact Commands

### 10.1 Test File: `tests/fund/documents/test_fund_disclosure_document.py`

| Test class / function | What it proves |
|----------------------|----------------|
| `TestFundDisclosureDocumentIdentityConstruction` | Identity accepts valid fields, rejects invalid fund_code/year, enforces boundary field constraints |
| `TestFundDisclosureDocumentIdentityContentHash` | `content_hash`: `None` valid; 64-char hex valid; empty string invalid; non-hex chars invalid; wrong length (e.g. 63 or 65 chars) invalid |
| `TestFundDisclosureDocumentIdentitySerialization` | `to_dict()` / `from_dict()` round-trip preserves all fields |
| `TestFundDisclosureDocumentSectionConstruction` | Section construction and validation |
| `TestFundDisclosureDocumentTableBlockConstruction` | Table block construction, header/body row indexing, cell count consistency |
| `TestFundDisclosureDocumentCellLocatorConstruction` | Cell locator construction, row/column index, hash stability |
| `TestFundDisclosureDocumentConstruction` | Full document assembly, `FundDisclosureDocumentIntermediate` Protocol compliance; `intermediate_kind="fund_disclosure_document.v1"` is fixed |
| `TestFundDisclosureDocumentSerializationRoundTrip` | Full document `to_dict()` → `from_dict()` → equality |
| `TestFundDisclosureDocumentBoundaryFields` | `candidate_boundary: CandidateBoundaryStatus` rejects non-proof values; exact `not_proven`/`not_ready` semantics enforced |
| `TestFundDisclosureDocumentLocatorStabilityReuse` | `LocatorStability` is imported from `fund_agent.fund.documents.candidates.models`, not redefined |
| `TestFundDisclosureDocumentNavigationRoundTrip` | Navigation nodes serialize/deserialize correctly |
| `TestFundDisclosureDocumentCandidateOnlyGuards` | `candidate_only` cannot be `False`, `readiness_status` cannot be changed |
| `TestFundDisclosureDocumentDoesNotImportEvidenceAnchor` | AST import analysis proving no dependency on extractor `EvidenceAnchor` or `EvidenceSourceKind` |
| `TestFundDisclosureDocumentIsNotReExported` | Proves `FundDisclosureDocument` is not in public `__init__.py` exports |
| `TestFundDisclosureDocumentSatisfiesIntermediateProtocol` | `isinstance(doc, FundDisclosureDocumentIntermediate)` is `True` |
| `TestFundDisclosureDocumentReachesProcessor` | Construct a concrete doc with `intermediate_kind="fund_disclosure_document.v1"`, pass through `FundDisclosureDocumentProcessor`: processor must reach candidate-boundary / fully-gapped missing behavior, NOT `input_type_mismatch` |
| `TestFundDisclosureDocumentNoConsumptionASTGuards` | AST-based scan of services/ui/host/agent/template/audit/extractors/quality for forbidden candidate imports (mirrors `test_docling_no_consumption_guards.py` pattern) |

### 10.2 Test File: `tests/fund/documents/test_fund_disclosure_failure_mapping.py`

| Test class / function | What it proves |
|----------------------|----------------|
| `TestFailureMappingComplete` | All `FundDisclosureCandidateSourceFailureCode` values map to canonical categories via `map_fund_disclosure_failure_to_source_category()`; function accepts only `FundDisclosureCandidateSourceFailureCode`, not `FundDisclosureCandidateFailureCode` |
| `TestFailureMappingRedirectUnavailableDecisionTable` | `redirect_unavailable` with `FundDisclosureFailureContext` evaluated per total ordered decision table in §7.3.1: priority 1 (non-EID domain → `identity_mismatch` regardless of HTTP status), priority 2 (5xx/timeout/DNS/TLS → `unavailable`), priority 3 (4xx → `not_found`), priority 4 (insufficient facts → `unavailable`) |
| `TestFailureMappingRenderUnavailableDecisionTable` | `render_unavailable` with `FundDisclosureFailureContext` evaluated per total ordered decision table in §7.3.2: priority 1 (HTTP 200 empty body → `schema_drift`), priority 2 (HTTP 200 non-HTML body → `schema_drift`), priority 3 (HTTP 200 HTML with consistent structure absence → `schema_drift`), priority 4 (5xx → `unavailable`), priority 5 (known URL 4xx → `not_found`), priority 6 (insufficient facts → `unavailable`) |
| `TestFailureMappingIndexUnavailable` | `index_unavailable` → `unavailable` (context=None accepted) |
| `TestFailureMappingListRowMissing` | `list_row_missing` → `not_found` |
| `TestFailureMappingIdentityMismatch` | `identity_mismatch` → `identity_mismatch` |
| `TestFailureMappingRenderDomainMismatch` | `render_domain_mismatch` → `identity_mismatch` |
| `TestFailureMappingRenderStructureMissing` | `render_structure_missing` → `schema_drift` |
| `TestFailureMappingLocatorUnstable` | `locator_unstable` → `schema_drift` |
| `TestFailureMappingMixedFacts` | Every mixed-fact combination in §7.3.3 evaluated correctly: non-EID redirect + 5xx → `identity_mismatch`; non-EID redirect + 4xx → `identity_mismatch`; known render URL 404 → `not_found`; HTTP 200 empty body → `schema_drift`; HTTP 200 non-HTML body → `schema_drift`; HTML body with consistent structure absence → `schema_drift`; insufficient facts both tables → `unavailable` |
| `TestProjectionBlockerRaisesValueError` | `value_unvalidated` and `raw_xml_not_proven` raise `ValueError` when passed to `map_fund_disclosure_failure_to_source_category()` (projection blockers are not source failures; function accepts only `FundDisclosureCandidateSourceFailureCode`) |
| `TestFailureMappingUnknownCode` | Unknown string raises `ValueError` (fail-closed) |
| `TestFailureMappingImportFollowsPattern` | `fund_disclosure_failure_mapping.py` imports `AnnualReportSourceFailureCategory` from `fund_agent.fund.documents.models`, following the pattern in `fund_agent.fund.documents.candidates.failures` |
| `TestFailureMappingDoesNotImportEvidenceSourceKind` | No dependency on extractor `EvidenceSourceKind` |

### 10.3 Existing Test Suites That Must Still Pass

These existing tests must pass unchanged after schema implementation:

```bash
# S4 processor tests
python -m pytest tests/fund/processors/test_fund_disclosure_processor.py -v

# Existing candidate document tests (must not break)
python -m pytest tests/fund/documents/test_docling_candidate_models.py -v
python -m pytest tests/fund/documents/test_docling_failure_mapping.py -v
python -m pytest tests/fund/documents/test_docling_locators.py -v
python -m pytest tests/fund/documents/test_docling_no_consumption_guards.py -v

# Repository tests (must not break)
python -m pytest tests/fund/documents/test_repository.py -v

# Registry tests (must not break)
python -m pytest tests/fund/processors/test_registry.py -v

# Active annual processor tests (must not break)
python -m pytest tests/fund/processors/test_active_annual_processor.py -v
```

### 10.4 Full Validation Commands (Future Implementation Gate)

```bash
# 1. New schema tests
python -m pytest tests/fund/documents/test_fund_disclosure_document.py -v

# 2. New failure mapping tests
python -m pytest tests/fund/documents/test_fund_disclosure_failure_mapping.py -v

# 3. All candidate document tests
python -m pytest tests/fund/documents/ -v

# 4. All processor tests
python -m pytest tests/fund/processors/ -v

# 5. Lint
ruff check fund_agent/fund/documents/candidates/fund_disclosure_document.py
ruff check fund_agent/fund/documents/candidates/fund_disclosure_failure_mapping.py
ruff check tests/fund/documents/test_fund_disclosure_document.py
ruff check tests/fund/documents/test_fund_disclosure_failure_mapping.py

# 6. Format
ruff format --check -- fund_agent/fund/documents/candidates/fund_disclosure_document.py
ruff format --check -- fund_agent/fund/documents/candidates/fund_disclosure_failure_mapping.py

# 7. Diff validation
git diff --check -- fund_agent/fund/documents/candidates/
git diff --check -- tests/fund/documents/

# 8. Verify no forbidden files touched
git diff --name-only -- fund_agent/fund/extractors/models.py  # must be empty
git diff --name-only -- fund_agent/fund/documents/models.py   # must be empty
git diff --name-only -- fund_agent/fund/documents/repository.py  # must be empty
git diff --name-only -- fund_agent/fund/processors/contracts.py  # must be empty
git diff --name-only -- fund_agent/fund/processors/fund_disclosure_processor.py  # must be empty
git diff --name-only -- fund_agent/services/  # must be empty
git diff --name-only -- fund_agent/ui/  # must be empty

# 9. EvidenceAnchor / EvidenceSourceKind immutability
python -c "
from fund_agent.fund.extractors.models import EvidenceSourceKind
# EvidenceSourceKind is a Literal type; verify its values
import typing
args = typing.get_args(EvidenceSourceKind)
assert args == ('annual_report', 'external_api', 'derived'), f'Unexpected: {args}'
print('EvidenceSourceKind unchanged:', args)
"

# 10. AnnualReportSourceFailureCategory immutability
python -c "
from fund_agent.fund.documents.models import AnnualReportSourceFailureCategory
import typing
args = typing.get_args(AnnualReportSourceFailureCategory)
expected = ('not_found', 'unavailable', 'schema_drift', 'identity_mismatch', 'integrity_error')
assert args == expected, f'Unexpected: {args}'
print('AnnualReportSourceFailureCategory unchanged:', args)
"
```

## 11. Residual Risks

| # | Residual | Owner | Destination | Severity |
|---|----------|-------|-------------|----------|
| 1 | Same-report comparison evidence (EID HTML render vs current pdfplumber) has not run | Fund documents / evidence owner | Same-report Comparison Evidence Gate | Blocks any consumer integration or field projection |
| 2 | Ordinary non-REIT annual/interim HTML render coverage unproven | Fund documents / source research owner | Sample expansion evidence gate | Blocks generalization claims; does not block internal schema |
| 3 | Field correctness, unit/date semantics, raw XML/taxonomy proof, source truth unproven | Fund documents / evidence owner | Separate evidence gates only | Blocks S6+ field extraction correctness claims |
| 4 | S5 facade integration not yet planned | Fund extractor owner | S5 Facade Integration Gate (after schema implementation) | Blocks `FundDataExtractor.extract()` consumption of `fund_disclosure_document.v1` |
| 5 | S6+ field-family extraction not yet planned | Fund extractor owner | S6+ Field-family Extraction Gate (after S5) | Blocks actual field extraction from `FundDisclosureDocument` |
| 6 | PR #23 remains draft/open | Maintainer / controller | PR disposition gate or user decision | Does not block this planning gate; blocks merge |
| 7 | Full-repo / PR-scoped `ruff format --check` baseline drift | Formatting / repository hygiene owner | Separate formatting-baseline gate | Does not block schema implementation |
| 8 | Candidate `source_artifact_kind` may need expansion for future candidate sources beyond `eid_xbrl_html_render_candidate.v1` | Fund documents owner | Future candidate source design gate | `FundDisclosureDocumentIdentity.source_artifact_kind` uses a closed literal that may need expansion |

## 12. Stop Conditions for Future Implementation Worker

The implementation worker must STOP and report `BLOCKED_NOT_READY` if any of these conditions is true:

1. Any forbidden file listed in §5.2 is modified.
2. `EvidenceSourceKind` literal values are changed.
3. `AnnualReportSourceFailureCategory` literal values are changed.
4. `EvidenceAnchor` schema is modified.
5. `FundDocumentRepository.load_annual_report()` behavior changes.
6. `FundDataExtractor.extract()` imports or consumes `FundDisclosureDocument`.
7. Any Service, UI, Host, Agent, renderer, or quality gate module imports `FundDisclosureDocument`.
8. `FundDisclosureDocument` is re-exported from any public `__init__.py`.
9. `FundDisclosureDocument` does not satisfy `FundDisclosureDocumentIntermediate` Protocol.
10. Any boundary field (`candidate_only`, `field_correctness_status`, `source_truth_status`,
    `parser_replacement_authorized`, `readiness_status`) accepts a non-proof value.
11. Any `FundDisclosureCandidateSourceFailureCode` value is not mapped to a canonical
    `AnnualReportSourceFailureCategory` via `map_fund_disclosure_failure_to_source_category()`.
12. `FundDisclosureProjectionBlocker` values (`value_unvalidated`, `raw_xml_not_proven`) are
    passed to the failure mapping function without raising `ValueError`.
13. `redirect_unavailable` / `render_unavailable` split rules are not implemented as total
    ordered decision tables using `FundDisclosureFailureContext`, covering all priority rows
    in §7.3.1 and §7.3.2 including the mixed-fact combinations in §7.3.3.
14. `LocatorStability` is redefined instead of imported from
    `fund_agent.fund.documents.candidates.models`.
15. `FundDisclosureDocument` duplicates five separate boundary fields instead of using
    `candidate_boundary: CandidateBoundaryStatus` imported from `fund_agent.fund.processors.contracts`.
16. `FundDisclosureDocument.intermediate_kind` is any value other than `"fund_disclosure_document.v1"`.
17. Any test in `tests/fund/documents/test_docling_*.py` or `tests/fund/processors/` that
    previously passed now fails.
18. `ruff check` or `ruff format --check` fails on any new file.
19. `FundDisclosureDocument` imports `EvidenceAnchor` or `EvidenceSourceKind` from
    `fund_agent/fund/extractors/models.py`.
20. Code claims source truth, field correctness, taxonomy compatibility, parser replacement,
    readiness, or release.
21. Code wires candidate HTML render into extractor, renderer, audit, source labels,
    CHAPTER_CONTRACT, quality gate, or production repository behavior.

## 13. README / Docs Sync Triggers

During the future implementation gate (NOT this planning gate):

- If `fund_agent/fund/documents/candidates/` is modified → update `fund_agent/fund/README.md`
  to reflect the new `FundDisclosureDocument` candidate schema as Fund documents internal only,
  not production surface.
- Do NOT update project root `README.md` (no user-visible change).
- Do NOT update `fund_agent/README.md` (no boundary change).
- Do NOT update `docs/design.md` (no design truth change; candidate internals are already
  described as future design).

## 14. Final Guardrails

Explicitly preserved by this plan:

- `not_raw_xml_download_proof`
- `not_field_correctness_proof`
- `not_taxonomy_compatibility_proof`
- `not_source_truth`
- `not_readiness_proof`
- `no_repository_behavior_change`
- `no_parser_replacement`
- `no_evidence_source_kind_expansion`
- `no_annual_report_source_name_expansion`
- `no_failure_category_expansion`
- `no_evidence_anchor_schema_change`
- `no_extractor_facade_change`
- `no_service_ui_host_renderer_quality_gate_access`
- `no_llm_route_change`
- `no_source_policy_change`
- `no_intermediate_kind_mutation` — `FundDisclosureDocument.intermediate_kind` is fixed to `"fund_disclosure_document.v1"`
- `no_locator_stability_redefinition` — `LocatorStability` is imported from `fund_agent.fund.documents.candidates.models`
- `no_candidate_boundary_duplication` — `candidate_boundary` uses `CandidateBoundaryStatus` from `contracts.py`
- `no_projection_blocker_mapping` — `value_unvalidated`, `raw_xml_not_proven` are projection-blocker statuses, not source failure categories
- `no_loose_failure_context` — failure mapping uses typed `FundDisclosureFailureContext`, not keyword arguments
- `no_missing_ast_guard` — non-consumption test uses AST-based guarded-tree pattern from `test_docling_no_consumption_guards.py`

Final verdict:

```text
VERDICT: PLAN_FIXED_READY_FOR_REVIEW_NOT_READY
```
