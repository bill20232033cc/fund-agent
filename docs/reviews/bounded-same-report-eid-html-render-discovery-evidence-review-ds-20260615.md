# Bounded Same-report EID HTML Render Discovery Evidence — DS Review

Date: 2026-06-15

Gate: `Bounded Same-report EID HTML Render Discovery Gate`

Role: DS review worker

Verdict: `PASS`

## 1. Scope

- Review target: `docs/reviews/bounded-same-report-eid-html-render-discovery-evidence-20260615.md`
- JSON artifact: `reports/representation-json/004393_2025_eid_html_render_full.json`
- Controller judgment (context): `docs/reviews/same-report-full-annual-representation-json-evidence-controller-judgment-20260615.md`
- Project rules: `AGENTS.md`
- Included: evidence claims, JSON structure/provenance/completeness, guardrail integrity, EID single-source policy compliance, AgentCodex block record
- Excluded: field correctness assessment, taxonomy assessment, source truth assessment, production readiness, parser replacement, repository behavior, design/control doc edits, live/network verification

## 2. Evidence Summary

The evidence artifact records a bounded live discovery: CSRC EID XBRL search → one matched row for `004393 / 2025 / FB010010` (uploadInfoId=22053366) → instance HTML view redirect → final HTML render (822146 bytes, SHA-256 `8e03dfee…`) served from `eid.csrc.gov.cn`. The full render was parsed into a structured JSON with navigation labels (211), heading candidates (261), paragraph blocks (750), tables (802), target table candidates (14), and blocked claims (9). The evidence explicitly records that AgentCodex network approval UI blocked, and the controller executed the bounded curl requests directly.

## 3. Review Focus Verification

### 3.1 Same-report EID HTML render availability for 004393 / 2025, and only that

**PASS.** The evidence chain is bounded to one fund/year/report-type:

- Search request filters: `fundCode=004393`, `reportYear=2025`, `reportTypeCode=FB010010` (年度报告)
- Search result: `iTotalRecords=1`, single matched row with `uploadInfoId=22053366`, fund name `安信企业价值优选混合`
- Instance view: `instance_html_view.do?instanceid=22053366` → 302 → final render URL stays within `eid.csrc.gov.cn`
- JSON `source_kind`: `eid_xbrl_html_render_candidate` — scoped to candidate, not source truth
- JSON `source_classification`: `same_report_html_render_found_candidate_not_ready`
- No other fund, year, or report type was claimed

### 3.2 Avoids treating HTML render as raw XML/XBRL instance truth

**PASS.** Both evidence doc §6 and JSON `blocked_claims` explicitly list `not_raw_xml_download_proof`. The `source_kind` is `eid_xbrl_html_render_candidate`, distinguishing generated HTML render from raw XBRL instance. The JSON contains parsed HTML structure (tags, text, tables), not XBRL taxonomy elements (schemaRef, contextRef, unitRef, fact items).

### 3.3 Avoids field correctness, taxonomy compatibility, source truth, readiness, production parser replacement, or repository behavior claims

**PASS.** Each is explicitly blocked:

| Claim | Evidence doc guardrail (§6) | JSON blocked_claims |
|---|---|---|
| Field correctness | `not_field_correctness_proof` | present |
| Taxonomy compatibility | `not_taxonomy_compatibility_proof` | present |
| Source truth | `not_source_truth` | present |
| Readiness | `not_readiness_proof` / `NOT_READY` | present |
| Repository behavior change | `no_repository_behavior_change` | present |
| Parser replacement | `no_production_parser_replacement` | present |

The evidence doc §5 maps `FundDisclosureDocument` and `EvidenceAnchor` as **candidates** only, with `source_owner_boundary: "future FundDocumentRepository internal candidate only"`. No production contract is asserted.

### 3.4 Preserves EID single-source and no non-EID fallback

**PASS.** All three requests (search metadata, same-report search, instance HTML view) target `eid.csrc.gov.cn`. No Eastmoney, CNINFO, fund-company website, or other source appears in any request URL, response, or mapping. JSON `blocked_claims` includes `no_non_eid_fallback`. This matches `AGENTS.md` policy: EID single-source, `not_found`/`unavailable` is terminal failure, no fallback.

### 3.5 JSON includes enough request provenance, render URL/hash, navigation/section/table/locator candidates, and blocked claims

**PASS.** JSON structure verification (`python -m json.tool` passed):

| Required element | Present | Detail |
|---|---|---|
| Request provenance | Yes | `official_request_provenance` with search URL, method, full aoData, result summary, instance_html_view URL, redirect location, final status/content-type/length, complete response headers (302 + 200) |
| Render URL | Yes | `html_render_identity.render_url` + each `locator_candidate.render_url` |
| Content hash | Yes | `html_render_identity.content_sha256`: `8e03dfee69eb8a17c653eb0ae5fcefd12d331820f0543bee83d7136c3cc3fb94` |
| Navigation labels | Yes | 211 items |
| Heading candidates | Yes | 261 items, each with `tag`, `id`, `class`, `text` |
| Paragraph blocks | Yes | 750 items, each with `tag`, `id`, `class`, `text` |
| Tables | Yes | 802 items, each with `table_index`, `attrs`, `row_count`, `cell_count`, `text_sample`, `rows` |
| Target table candidates | Yes | 14 items, each with `table_index`, `hit_terms`, `row_count`, `cell_count`, `locator_candidate` (render_url, table_index_under_document, row_locator_rule, column_header_path_rule), `sample_rows` |
| Blocked claims | Yes | 9 items: not_raw_xml_download_proof, not_field_correctness_proof, not_taxonomy_compatibility_proof, not_source_truth, not_readiness_proof, no_repository_behavior_change, no_non_eid_fallback, no_production_parser_replacement, no_page_number_anchor |
| Candidate mappings | Yes | `funddisclosuredocument_candidate_mapping` (document_id, source_kind, owner boundary, render_url, content_hash, sections/blocks description) + `evidence_anchor_candidate_mapping` (source_kind, page_number=null, section/table/row/column locator rules, note_rule) |

`summary_metrics` is internally consistent with the data arrays: navigation_label_count=211, heading_candidate_count=261, paragraph_block_count=750, table_count=802, target_table_candidate_count=14. `has_url_or_source_locator=true`, `has_content_hash=true`, `has_page_number=false`, `has_section_tree=true`, `has_table_cell_locator=true`.

### 3.6 Honestly records AgentCodex network approval UI blocked and controller collected live facts

**PASS.** Evidence doc header states: "evidence worker fallback executed by controller after AgentCodex approval UI blocked on bounded curl requests." The controller judgment (§1) confirms: "EID HTML same-report full JSON is blocked because no local accepted 004393 / 2025 HTML render artifact exists and live/network discovery was not authorized." The evidence artifact exists only because the controller authorized this bounded gate with explicit live/network authorization (§5: "Requires bounded same-report EID HTML render discovery gate with explicit live/network authorization"). The provenance chain is honest and complete.

### 3.7 Any blocker requiring artifact rewrite before controller acceptance

**None found.** JSON is valid. Evidence doc and JSON are internally consistent in all verified fields (URLs, hash, counts, identities). Guardrails are explicit and comprehensive. Residuals are properly acknowledged (§7). No material defect, omission, or misrepresentation was found.

## 4. Findings

未发现实质性问题。

## 5. Open Questions

无。

## 6. Residual Risk

| Risk | Status |
|---|---|
| HTML table count (802) includes layout/TOC tables alongside data tables; target_table_candidates (14) is keyword-filtered but not schema-validated | Accepted residual in evidence doc §7; deferred to candidate schema/planning gate |
| No PDF page numbers; locators use table_index + row_index only | Accepted residual; PDF or Docling needed for page-number anchors |
| Field correctness, taxonomy, source truth remain unverified | Explicitly blocked claims; not this gate's scope |
| `html_section_id_or_anchor` is null in all locator candidates; render provides no stable DOM section IDs | Inherent characteristic of CSRC HTML render format; heading text is the available anchor |

## 7. Controller Disposition

No blocking findings. Recommended controller actions:

- Accept this DS review as evidence that the bounded discovery evidence artifact is honest, properly scoped, and internally consistent
- Carry the four accepted residuals into the next gate(s)
- The evidence is sufficient for controller to close `Bounded Same-report EID HTML Render Discovery Gate` and advance to the next deferred gate(s)

## 8. Validation

```text
python -m json.tool reports/representation-json/004393_2025_eid_html_render_full.json > /dev/null  # PASS
git diff --check                                                                                    # PASS (no output)
```
