# FundDisclosureDocument Candidate Source Schema Plan

Date: 2026-06-14

Gate: `FundDisclosureDocument Candidate Source Schema Planning Gate`

Role: planning worker

Readiness state: `NOT_READY`

Verdict: `PLAN_READY_FOR_REVIEW_NOT_READY`

## 1. Scope

This plan defines the next no-code schema planning handoff for `eid_xbrl_html_render_candidate`.

The plan exists because the accepted design requires a candidate documents-layer route, but current code constraints are narrower than the future design:

- `EvidenceSourceKind` is currently `Literal["annual_report", "external_api", "derived"]`;
- `AnnualReportSourceName` is currently `Literal["eid", "eastmoney"]`;
- `AnnualReportSourceFailureCategory` is currently `Literal["not_found", "unavailable", "schema_drift", "identity_mismatch", "integrity_error"]`;
- `ANNUAL_REPORT_DOCUMENT_KIND` is currently fixed to `"annual_report"`;
- current production parsing remains `pdfplumber -> ParsedAnnualReport -> extractor -> EvidenceAnchor`;
- current `FundDocumentRepository` behavior is unchanged.

This gate is planning only. It does not implement schema/code/runtime behavior.

## 2. Evidence Reviewed

- `AGENTS.md`
- `docs/design.md`
- `docs/implementation-control.md`
- `docs/current-startup-packet.md`
- `docs/reviews/funddisclosuredocument-candidate-source-design-20260614.md`
- `docs/reviews/funddisclosuredocument-candidate-source-design-review-ds-20260614.md`
- `docs/reviews/funddisclosuredocument-candidate-source-design-review-mimo-20260614.md`
- `docs/reviews/funddisclosuredocument-candidate-source-design-controller-judgment-20260614.md`
- `fund_agent/fund/extractors/models.py`
- `fund_agent/fund/documents/models.py`
- `fund_agent/fund/documents/sources.py`

## 3. Current Code Constraints

| Constraint | Current fact | Planning implication |
|---|---|---|
| Evidence source kind | `EvidenceSourceKind = Literal["annual_report", "external_api", "derived"]` | `eid_xbrl_html_render_candidate` cannot be assumed to fit current `EvidenceAnchor.source_kind` without a schema decision. |
| Annual report source names | `AnnualReportSourceName = Literal["eid", "eastmoney"]` | Do not introduce a new production source name in this planning gate; HTML render is a candidate artifact route under future documents-layer ownership, not current production source policy. |
| Annual report failure categories | `not_found`, `unavailable`, `schema_drift`, `identity_mismatch`, `integrity_error` | Candidate failure classes must map to these canonical categories before implementation. |
| Document kind | `ANNUAL_REPORT_DOCUMENT_KIND = "annual_report"` | Candidate source planning should not broaden production document kind without a later schema/implementation gate. |
| Current document object | `ParsedAnnualReport`, `ParsedTable`, `ReportSection` | Future `FundDisclosureDocument` should be planned as a candidate representation layer, not a drop-in replacement for current parsed annual reports. |
| Current repository behavior | `FundDocumentRepository.load_annual_report()` | No behavior change; future endpoint/fetch/cache/parser access must remain internal to Fund documents. |

## 4. Schema Planning Objective

The next implementation-planning-ready schema decision must answer five questions:

1. How should `eid_xbrl_html_render_candidate` be represented without pretending it is current `EvidenceSourceKind` support?
2. What candidate document object is needed before any implementation: new `FundDisclosureDocument`, extension of current document models, or separate candidate artifact model?
3. How are candidate HTML render failure classes mapped into canonical source outcomes?
4. How can current `EvidenceAnchor` carry HTML render locator data with `page_number=null` without breaking renderer/audit assumptions?
5. Which validation tests would prove no behavior change before any later implementation gate?

## 5. Recommended Schema Strategy

Recommended planning strategy:

```text
Plan a new candidate document representation layer first.
Do not mutate current EvidenceAnchor or AnnualReportSourceName in this gate.
```

Rationale:

- Directly adding `eid_xbrl_html_render_candidate` to `EvidenceSourceKind` would affect renderer/audit/source-label behavior and should be treated as implementation scope.
- Treating HTML render as `annual_report` would hide the fact that the locator lacks PDF page coordinates and raw XML context.
- Treating HTML render as `external_api` would erase document-section/table locator semantics.
- A candidate representation layer lets a later implementation gate add tests around source kind projection, renderer labeling and fail-closed behavior before any production path consumes it.

## 6. Candidate Objects To Plan

Schema planning should specify these candidate objects before implementation:

### 6.1 Candidate render artifact identity

Minimum fields:

- `source_kind = "eid_xbrl_html_render_candidate"`;
- `fund_code`;
- `fund_id`;
- `instance_id`;
- `report_year`;
- `report_type_code`;
- `report_type_label`;
- `source_list`;
- `report_send_date`;
- `index_url`;
- `instance_view_url`;
- `render_url`;
- `redirect_location`;
- `content_type`;
- `content_length`;
- `content_hash`;
- `fetched_at`;
- `render_status`;
- `navigation_present`;

### 6.2 Candidate document representation

Minimum fields:

- artifact identity;
- ordered navigation nodes;
- section records;
- paragraph blocks;
- table blocks;
- locator stability classification;
- failure class;
- raw XML proof status fixed to `not_proven`;
- field correctness status fixed to `not_proven`;
- taxonomy compatibility status fixed to `not_proven`.

### 6.3 Candidate table block

Minimum fields:

- `section_anchor`;
- `heading_text`;
- `heading_path`;
- `table_index_under_section`;
- `table_caption_or_nearby_heading`;
- `header_rows`;
- `body_rows`;
- `row_count`;
- `column_count`;
- `merged_header_detected`;
- `locator_stability`;
- `extraction_note`.

### 6.4 Candidate cell locator

Minimum fields:

- `render_url`;
- `section_anchor`;
- `heading_path`;
- `table_index_under_section`;
- `row_index`;
- `row_label_path`;
- `column_header_path`;
- `cell_text`;
- `cell_hash`;

## 7. EvidenceAnchor Projection Options

Schema planning should compare three options and choose one in a later controller judgment.

| Option | Description | Pros | Risks |
|---|---|---|---|
| A. New `EvidenceSourceKind` value | Extend source kind to include `eid_xbrl_html_render_candidate` | Explicit and auditable | Touches renderer/source labels/tests; implementation scope; not planning-only |
| B. Intermediate candidate object only | Keep `EvidenceAnchor` unchanged until field projection validates a rendered cell | Avoids premature public anchor schema change | Requires later projection layer before extractor consumption |
| C. Use `annual_report` with HTML note | Store HTML locator in `note` while source kind remains `annual_report` | Minimal schema churn | Misleading because no PDF page coordinate and source artifact is not the production PDF |

Planning recommendation: Option B for the next implementation plan. Option A may be proposed only after renderer/audit/source-label impact is explicitly tested. Option C should be rejected unless a controller accepts it for an internal transitional test fixture only.

## 8. Failure Class Mapping Plan

Candidate failures must map to canonical outcomes before implementation:

| Candidate failure | Canonical category | Reason |
|---|---|---|
| `index_unavailable` | `unavailable` | Official EID index cannot be fetched or parsed due to temporary access/service issue |
| `list_row_missing` | `not_found` | EID list does not expose a matching concrete row |
| `identity_mismatch` | `identity_mismatch` | Fund/year/report identity conflicts |
| `redirect_unavailable` | `unavailable` or `schema_drift` | Temporary redirect failure is unavailable; stable response-contract change is schema drift |
| `render_unavailable` | `unavailable` | Final render page inaccessible or non-HTML due to service/access issue |
| `render_domain_mismatch` | `identity_mismatch` | Redirect leaves official EID domain and cannot be trusted as same source identity |
| `render_structure_missing` | `schema_drift` | Expected render contract such as title/navigation/sections is absent |
| `locator_unstable` | `schema_drift` | Render is accessible but cannot produce deterministic section/table/cell identity |
| `value_unvalidated` | no source failure; field projection blocked | Rendered value exists but is not accepted as field fact |
| `raw_xml_not_proven` | no source failure; raw XML route blocked | HTML route remains candidate; raw XML proof is separate |

Implementation planning must require tests for each mapping selected.

## 9. Validation Matrix For Later Implementation

No tests are required in this planning gate beyond linting the artifact. Later implementation planning should require:

| Validation | Purpose |
|---|---|
| model construction tests for candidate artifact identity | prove schema accepts required identity/hash/fetch metadata |
| failure mapping unit tests | prove candidate failures map to canonical source outcomes |
| locator serialization tests | prove section/table/cell locator fields round-trip |
| no repository behavior change tests | prove existing `FundDocumentRepository.load_annual_report()` behavior remains unchanged |
| renderer/audit non-consumption tests | prove Service/UI/Host/renderer/quality gate cannot consume candidate HTML render directly |
| source-label tests if Option A is selected | prove source labels and anchor rendering are explicit and non-misleading |

The validation matrix is limited to candidate representation internals. It must not plan extractor, renderer, audit, source-label or production-path consumption until a separate same-report representation evidence gate compares EID HTML render with the current pdfplumber representation on the same report subset.

## 10. Stop Conditions

Stop before implementation if any of these remains unresolved:

- no explicit decision on Option A/B/C for `EvidenceAnchor` projection;
- no canonical source outcome mapping for candidate failures;
- any plan requires Service/UI/Host/renderer/quality gate direct endpoint access;
- any plan claims raw XML, field correctness, taxonomy compatibility, source truth or readiness;
- ordinary non-REIT annual/interim residual is treated as covered;
- implementation worker would need to invent schema ownership, source kind or failure category.
- any plan tries to wire candidate HTML render into extractor, renderer, audit, source labels, CHAPTER_CONTRACT, quality gate or production repository behavior before same-report representation evidence compares EID HTML render with current pdfplumber.

## 11. Sequencing Constraint

The next implementation planning gate is allowed to plan only internal candidate representation schema mechanics:

- candidate dataclasses or typed dictionaries;
- serialization / deserialization;
- locator round-trip behavior;
- failure mapping to canonical outcomes;
- non-consumption guards proving no Service/UI/Host/renderer/quality gate access;
- no production `FundDocumentRepository.load_annual_report()` behavior change.

It must not plan extractor, renderer, audit, source-label or production-path consumption.

Before any consumer integration or field projection gate, the phaseflow must run:

```text
Same-report Comparison Evidence Gate: EID HTML render versus current pdfplumber
```

That evidence gate should compare the same report subset at the document-representation level: report identity, section hierarchy, table blocks, row/column locators, provenance locator quality, failure classes and gaps. It must not claim field correctness or readiness.

Docling remains later and optional:

```text
Annual-report Document Representation / Docling Benchmark Evidence Gate
```

Docling should be used only if EID HTML render plus current pdfplumber cannot cover required representation needs, or if a later controller decision reopens parser comparison. It is not a current parser replacement.

## 12. Next Gate Recommendation

Recommended next gate:

```text
FundDisclosureDocument Candidate Source Schema Plan Review Gate
```

Review focus:

- whether Option B is correctly recommended as the next implementation-planning strategy;
- whether Option C is rejected for production use;
- whether failure mapping preserves existing canonical source semantics;
- whether `EvidenceAnchor.source_kind` and renderer/audit impacts are not hidden;
- whether the plan prevents source fallback expansion and direct Service/UI/Host/renderer/quality-gate endpoint access.

If accepted, the next gate should be:

```text
FundDisclosureDocument Candidate Source No-live Implementation Planning Gate
```

That later gate should still be planning only unless a controller explicitly accepts implementation scope. Its allowed scope is candidate representation internals only; consumer integration must wait for the same-report comparison evidence gate.

## 13. Final Guardrails

Explicitly preserved:

- `not_raw_xml_download_proof`;
- `not_field_correctness_proof`;
- `not_taxonomy_compatibility_proof`;
- `not_source_truth`;
- `not_readiness_proof`;
- `no_repository_behavior_change`;
- `no_parser_replacement`;
- `no_llm_route_change`;
- `no_service_ui_host_renderer_quality_gate_endpoint_access`.

Final verdict:

```text
VERDICT: PLAN_READY_FOR_REVIEW_NOT_READY
```
