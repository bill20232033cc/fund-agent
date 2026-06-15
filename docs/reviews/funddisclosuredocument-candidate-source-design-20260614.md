# FundDisclosureDocument Candidate Source Design

Date: 2026-06-14

Gate: `FundDisclosureDocument Candidate Source Design Gate`

Role: design worker

Readiness state: `NOT_READY`

Verdict: `DESIGN_READY_FOR_REVIEW_NOT_READY`

## 1. Scope

This artifact designs a candidate documents-layer source model for CSRC EID XBRL HTML render artifacts.

The accepted candidate source classification is:

```text
source_kind = eid_xbrl_html_render_candidate
```

This design is limited to how accepted HTML render evidence may enter a future `FundDisclosureDocument` / `EvidenceAnchor` pipeline. It does not implement code, change runtime behavior, replace the production parser, change `FundDocumentRepository`, alter CHAPTER_CONTRACT, or make readiness/release claims.

## 2. Evidence Reviewed

- `AGENTS.md`
- `docs/design.md`
- `docs/implementation-control.md`
- `docs/current-startup-packet.md`
- `docs/reviews/csrc-eid-xbrl-html-render-route-realignment-controller-judgment-20260614.md`
- `docs/reviews/csrc-eid-xbrl-html-structured-render-artifact-evaluation-plan-controller-judgment-20260614.md`
- `docs/reviews/csrc-eid-xbrl-html-structured-render-artifact-evaluation-evidence-20260614.md`
- `docs/reviews/csrc-eid-xbrl-html-structured-render-artifact-evaluation-evidence-controller-judgment-20260614.md`
- `docs/reviews/csrc-eid-xbrl-html-evidence-closeout-control-sync-controller-judgment-20260614.md`

## 3. Accepted Design Inputs

| Input | Accepted use |
|---|---|
| EID index JSON lists | Announcement discovery and report identity candidate metadata only |
| `instance_html_view.do?instanceid=<idStr>` redirect | Render artifact identity and fetch provenance only |
| `/xbrl/REPORT/HTML/...html` final page | Candidate structured render artifact only |
| `instance_navigation` labels | Candidate section hierarchy and locator input |
| HTML headings / anchors | Candidate section identity and table grouping input |
| HTML table cells | Candidate table-block extraction input, not field correctness proof |
| Content hash / byte size / URL | Artifact identity, cache identity and change detection input |

Accepted evidence shows official HTML render artifacts are publicly reachable and partly stable for section/table/provenance projection. It does not prove raw XML access, raw XBRL facts, `schemaRef` / `contextRef` / `unitRef` lineage, taxonomy compatibility, rendered value correctness, or readiness.

## 4. Boundary Decision

The candidate source must live inside the Fund documents layer.

Allowed future ownership:

```text
fund_agent/fund/documents
  -> FundDocumentRepository internal source adapter
  -> candidate render artifact fetch/cache/fail-closed classification
  -> candidate FundDisclosureDocument projection
  -> extractor / chapter fact projection / EvidenceAnchor validation
```

Forbidden ownership:

```text
Service / UI / Host / renderer / quality gate
  -> direct EID XBRL endpoint calls
  -> direct HTML render parsing
  -> direct cache/file access
  -> direct use of render cells as report facts
```

This keeps AGENTS.md boundaries intact: all fund document access remains mediated by `FundDocumentRepository`, and all facts still require extractor / projection / `EvidenceAnchor` validation before CHAPTER_CONTRACT, audit, report generation or LLM consumption.

## 5. Candidate FundDisclosureDocument Shape

The future candidate object should represent a disclosure artifact, not a final fact store.

Minimum candidate fields:

| Field | Purpose |
|---|---|
| `source_kind` | Always `eid_xbrl_html_render_candidate` |
| `fund_code` | From EID list row / render identity |
| `fund_id` | From EID `fundidStr` when present |
| `instance_id` | EID `idStr` |
| `report_year` | EID list row `reportYear` |
| `report_type_code` | Code inferred from render path such as `FB030010` / `FB010010` / `FC100050` / `FA050010` |
| `report_type_label` | EID visible type such as `第一季度报告` / `年度报告` / `基金经理变更公告` |
| `report_send_date` | EID list row send date |
| `index_url` | `indexXbrlData.json` URL used for discovery |
| `instance_view_url` | `instance_html_view.do?instanceid=<idStr>` URL |
| `render_url` | Final `/xbrl/REPORT/HTML/...html` URL |
| `redirect_status` | Status and redirect location for instance view |
| `render_status` | Final HTML status / content-type / byte size |
| `content_hash` | Hash of final HTML render artifact |
| `fetched_at` | Fetch timestamp for future cache invalidation |
| `navigation` | Ordered navigation labels and anchor ids |
| `sections` | Candidate section hierarchy and visible titles |
| `blocks` | Ordered paragraph/table blocks with section ownership |
| `failure_class` | Fail-closed reason when discovery/fetch/parse/locator fails |

The object should not expose a field named `raw_xbrl`, `raw_xml`, `xbrl_instance`, or any equivalent that implies raw instance proof.

## 6. Section And Table Locator Contract

Candidate section locator:

| Locator field | Source |
|---|---|
| `render_url` | Final official HTML URL |
| `section_anchor` | DOM id / navigation target when present |
| `heading_text` | Visible section heading |
| `heading_path` | Ordered navigation / parent heading path |
| `section_index` | Stable ordinal under the render page |
| `report_type_code` | Render path / EID report type metadata |

Candidate table locator:

| Locator field | Source |
|---|---|
| `section_anchor` | Owning section id |
| `heading_text` | Owning heading |
| `table_index_under_section` | Table ordinal under section |
| `table_caption_or_nearby_heading` | Caption or nearest visible heading |
| `row_index` | Rendered table row ordinal |
| `row_label_path` | Row label / nested row labels when present |
| `column_header_path` | Header hierarchy reconstructed from rendered cells |
| `cell_text` | Rendered cell text |
| `cell_hash` | Optional hash of normalized cell text plus locator |

Locator stability should be classified before any field projection:

| Class | Meaning |
|---|---|
| `stable` | Anchor, heading, table ordinal, row label and column header path are all available and deterministic in repeated local parsing |
| `partly_stable` | Enough structure exists for a pilot, but repeated headings, nested tables, merged headers or report-family variance require normalization |
| `unstable` | DOM/table structure can be parsed but does not provide reliable section/table/cell identity |
| `not_extractable` | HTML is blank, binary-only, image-only, auth-gated, or lacks table/section structure |

## 7. EvidenceAnchor Candidate Mapping

Existing `EvidenceAnchor` fields can carry the candidate without schema change in the design phase:

| EvidenceAnchor field | Candidate mapping |
|---|---|
| `source_kind` | `eid_xbrl_html_render_candidate` |
| `document_year` | EID `reportYear` |
| `section_id` | `report_type_code + ":" + section_anchor_or_normalized_heading` |
| `page_number` | `null`; HTML render has no accepted PDF page coordinate |
| `table_id` | `heading_text + "#" + table_index_under_section` or stable DOM table identifier if later proven |
| `row_locator` | `row_index + row_label_path + column_header_path` |
| `note` | `idStr`, `render_url`, redirect location, content hash, report type label, source list and locator stability class |

This mapping is weaker than raw XML `contextRef` / `unitRef` / `schemaRef` proof. It may be sufficient for a structured-table candidate if locator stability and field projection are later accepted, but PDF remains necessary for narrative text and page-number anchors until a separate document representation gate proves otherwise.

## 8. Failure Taxonomy

Future implementation planning must require fail-closed source failures:

| Failure class | Meaning | Allowed consequence |
|---|---|---|
| `index_unavailable` | EID index JSON unavailable or non-JSON | Candidate source unavailable; do not fallback silently |
| `list_row_missing` | No matching row for fund/report identity | Candidate source gap |
| `identity_mismatch` | Row or render identity conflicts with requested fund/year/report type | Fail closed |
| `redirect_unavailable` | Instance view does not redirect to official render URL | Fail closed |
| `render_unavailable` | Final HTML is not accessible as expected text/html | Candidate source unavailable |
| `render_domain_mismatch` | Redirect leaves official EID domain | Fail closed |
| `render_structure_missing` | Missing `<title>XBRL</title>` / `instance_navigation` / visible sections | Candidate source gap |
| `locator_unstable` | Section/table/cell locator cannot be deterministically formed | Field projection blocked |
| `value_unvalidated` | Rendered cell exists but field correctness is not validated | No fact promotion |
| `raw_xml_not_proven` | Raw XML endpoint still unavailable/unproven | Raw XBRL route remains blocked |

`not_found` and `unavailable` remain terminal EID single-source outcomes under current policy. Eastmoney, fund-company, CNINFO or other fallback sources must not re-enter through this design.

## 9. Comparison With pdfplumber And Docling

This design makes the methods comparable only at the document-representation layer, not at the final fact-truth layer.

| Method | Strongest current role | Weakness |
|---|---|---|
| EID XBRL HTML render | Official rendered structured disclosure candidate for tables, headings, and report metadata where available | Not raw XML, no page number, no raw fact context/unit/schema proof, ordinary non-REIT annual sample still residual |
| Current pdfplumber path | Current production PDF parser path and existing extractor input | Field/extractor driven; not a complete annual-report document representation; table/section coverage gaps remain |
| Docling | Future benchmark candidate for layout/table/section recovery from PDF | Not current production parser; must remain inside Fund documents layer; cannot become fact truth without extractor / EvidenceAnchor validation |

The immediate next comparison should not be "which parser is better" in the abstract. It should compare whether the same report subset can produce stable `FundDisclosureDocument` sections/tables/locators from:

- EID HTML render;
- current pdfplumber output;
- optional Docling benchmark only if the first two cannot cover required representation needs.

## 10. Next Gate Recommendation

Recommended next gate:

```text
FundDisclosureDocument Candidate Source Design Review Gate
```

Review focus:

- whether `eid_xbrl_html_render_candidate` is kept distinct from raw XML/XBRL instance truth;
- whether repository boundaries are preserved;
- whether Service/UI/Host/renderer/quality gate direct endpoint access is forbidden;
- whether current `EvidenceAnchor` fields can carry the candidate without schema change;
- whether failure taxonomy is specific enough for implementation planning;
- whether comparison with pdfplumber/Docling is framed at document-representation level rather than readiness or fact correctness level.

Binding inputs for the next schema planning gate:

- Existing code may not currently accept `eid_xbrl_html_render_candidate` as a concrete `EvidenceAnchor.source_kind`. Schema planning must verify current model constraints and choose an explicit migration or projection strategy; it must not assume the current code can already carry this source kind.
- Candidate failure classes must be mapped back to canonical source outcome semantics such as `not_found`, `unavailable`, `schema_drift`, `identity_mismatch` and `integrity_error` before implementation planning. Implementation workers must not invent source ownership or outcome semantics.
- Ordinary non-REIT annual/interim HTML render coverage remains an open residual. Schema planning must not generalize from the current REIT annual/interim sample to all ordinary fund annual reports.

If accepted, the next planning gate should be:

```text
FundDisclosureDocument Candidate Source Schema Planning Gate
```

Deferred gates:

- ordinary non-REIT annual/interim EID HTML sample expansion;
- same-report comparison evidence gate: EID HTML render versus current pdfplumber;
- optional Docling benchmark gate;
- raw XML endpoint research;
- field correctness validation;
- production implementation;
- readiness/release/PR gates.

## 11. Final Guardrails

Explicitly not accepted:

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
VERDICT: DESIGN_READY_FOR_REVIEW_NOT_READY
```
