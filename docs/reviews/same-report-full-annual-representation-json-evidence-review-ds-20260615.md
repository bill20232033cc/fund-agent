# Same-report Full Annual-report Representation JSON Evidence — DS Review

Date: 2026-06-15
Role: DS review worker
Gate: `Same-report Full Annual-report Representation JSON Evidence Gate`
Review artifact: `docs/reviews/same-report-full-annual-representation-json-evidence-review-ds-20260615.md`
Reviewed evidence: `docs/reviews/same-report-full-annual-representation-json-evidence-20260615.md`
Reviewed JSON artifacts:
- `reports/representation-json/004393_2025_docling_full.json`
- `reports/representation-json/004393_2025_pdfplumber_full.json`
- `reports/representation-json/004393_2025_eid_html_render_full.json`

## 1 Validation Method

- All three JSON files loaded and parsed with stdlib `json` — no parse errors.
- Source files listed in each JSON's metadata checked for disk existence.
- SHA-256 hashes in metadata independently recomputed against disk files.
- Summary metrics cross-checked between evidence note tables and actual JSON content.
- Section/heading/paragraph/table arrays inspected for structural plausibility.

## 2 Findings Table

| # | Severity | Finding | Evidence Location | Required Action |
|---|---|---|---|---|
| F1 | NONBLOCKING | Docling `section_count` metric is 13 in both the evidence note §4 metrics table and the JSON `summary_metrics.section_count`, but the actual `sections` array contains 25 top-level entries. The 13 likely corresponds to report chapters (§1–§13) while the 25 includes additional tree-structure grouping nodes (e.g. the document title as a section node before §1, and subsections promoted alongside their parents). The metric definition is ambiguous. | Evidence note §4 table; `004393_2025_docling_full.json` `summary_metrics.section_count=13` vs `len(sections)=25` | Either correct `section_count` to 25 to match the data array, or document the counting rule (e.g. "counts only chapter-level sections mapped to report §1–§13, excludes title page and non-chapter grouping nodes"). Does not block gate. |
| F2 | INFO | Docling source file `reports/docling-route-a/004393_2025_docling.json` SHA-256 independently verified: `00a88c71...` matches metadata `source_hashes` claim. Two other Route A source files present on disk but hash not independently rechecked (trusting the matched main file establishes the lineage). Metadata field `socket_blocked: true` confirms no network activity during the original conversion. Derivation-from-existing-artifact claim is supported. | Docling JSON `metadata.source_hashes` and `metadata.conversion_summary.socket_blocked` | None. |
| F3 | INFO | Pdfplumber source files `cache/pdf/004393_2025_annual_report_eid.pdf` and `cache/documents/parsed_reports/004393_2025_annual_report.json` both exist on disk and their SHA-256 hashes independently verified: `dc38aae8...` and `9670bbb0...` respectively, matching metadata claims. Source metadata confirms `selected_source=eid`, `source_mode=single_source_only`, `fallback_enabled=false`, `fallback_used=false`. No live/network source was involved. | Pdfplumber JSON `metadata.source_hashes` and `metadata.source_metadata` | None. |
| F4 | INFO | EID HTML render JSON is correctly blocked: `coverage_status=BLOCKED_NEEDS_LIVE_EID_HTML_DISCOVERY_NOT_READY`, all content arrays empty, all metrics zero, blocker message states no URL was fabricated. No live discovery was attempted. | EID HTML JSON `blocker`, `coverage_status`, all empty arrays | None. |
| F5 | INFO | All three JSONs carry explicit `metadata.source_truth_boundary` fields disclaiming field correctness, taxonomy, source truth, readiness, parser replacement or `FundDocumentRepository` behavior change. All `coverage_status` values end in `_NOT_READY`. Evidence note §§2, 9 explicitly restate these boundaries. Candidate-only scope is consistently preserved. | Each JSON `metadata.source_truth_boundary`; evidence note §2, §9 | None. |
| F6 | INFO | Evidence note §3 byte counts (Docling 4,780,505, pdfplumber 6,335,018, EID HTML 2,238) match actual disk file sizes. All per-route metrics in §§4–5 (page_count, heading_count, paragraph_count, table_count, cell_count, boolean flags) match the corresponding JSON `summary_metrics` values, with the F1 section_count exception noted above. | Evidence note §§3–6 vs JSON `summary_metrics` | None beyond F1. |
| F7 | INFO | All three JSONs include `failure_taxonomy` with `canonical_source_failures` listing `not_found / unavailable / schema_drift / identity_mismatch / integrity_error`, consistent with AGENTS.md EID single-source no-fallback policy. Docling and pdfplumber have empty `route_failures`; EID HTML has a single `not_found` route failure with the correct blocker reason. | Each JSON `failure_taxonomy` | None. |
| F8 | INFO | Evidence note §11 recommends three next gates. These are advisory, not binding. The review does not evaluate the merit of these recommendations (that is controller scope). | Evidence note §11 | None. |

## 3 Contract Boundary Verification

| Contract | Status | Evidence |
|---|---|---|
| No live/network/provider/LLM command run | PASS | All JSONs source from local disk paths or declare blocked; no live URLs present |
| No production parser replacement | PASS | All `source_truth_boundary` fields explicitly disclaim |
| No `FundDocumentRepository` behavior change | PASS | Disclaimed in all boundaries; pdfplumber JSON reads cache directly, not through repository |
| No source truth claim | PASS | Disclaimed in all boundaries |
| No field correctness claim | PASS | Disclaimed in all boundaries |
| No taxonomy claim | PASS | Disclaimed in all boundaries |
| No readiness/release claim | PASS | All coverage statuses end in `_NOT_READY` |
| No fabricated URL for EID HTML | PASS | Blocker message explicit; all content arrays empty |
| NOT_READY preserved | PASS | Consistent across all three JSONs and evidence note |
| Evidence note stays within authorized write set | PASS | Evidence note writes only the declared four artifacts; no control/design doc edits |

## 4 Adversarial Pass

- **What if docling source files were modified after the representation JSON was written?** Hash in metadata was verified against current disk file — match confirmed. Tampering window is bounded by the git commit that produced the source artifacts.
- **What if pdfplumber export accidentally called a live EID endpoint?** Source metadata shows `fallback_enabled=false, fallback_used=false`; the source file is a local PDF cache. The `source_url` field in metadata is EID provenance from the existing cache, not a live call made during this export.
- **What if the EID HTML blocker message is misleading and a URL was actually attempted?** JSON metrics are all zero, arrays empty, blocker field explicit. No evidence of any attempt.
- **What if NOT_READY is claimed but readiness is implicitly asserted?** All three JSONs have coverage status ending in `_NOT_READY`. All source_truth_boundary fields explicitly disclaim readiness. The evidence note verdict is `PARTIAL_JSON_COMPARISON_ONLY_NOT_READY`. No implicit readiness assertion detected.

## 5 Residual Risks

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Docling `section_count` definition ambiguity could cause downstream consumers to misinterpret coverage | Low | Low — the actual section data is present and correct; only the reported count metric is inconsistent | Fix F1 or document counting rule |
| Pdfplumber export format is evidence-only, not integrated with repository path — future consumers might assume it's the production schema | Low | Medium — could create expectation that pdfplumber full JSON is the canonical representation | Explicit in evidence note §5; the boundary disclaimers are clear |
| EID HTML render remains blocked — downstream planning gates may need this evidence | Medium | Low — the blocker is correctly documented; no false claim of availability | Controller should decide whether to authorize bounded live discovery before gates that need HTML comparability |

## 6 Verdict

**PASS_WITH_NONBLOCKING_FINDINGS**

All three JSON artifacts are present and valid. Docling derivation from existing Route A artifacts is hash-verified. Pdfplumber export is no-live from local cache. EID HTML correctly blocks without fabricated URL. Candidate-only, NOT_READY, no source truth, no field correctness, no taxonomy, and no parser replacement boundaries are consistently preserved. Metrics are internally consistent with the single exception of F1 (docling section_count definition). No blocker requires artifact fix before controller judgment.

## 7 Final Recommendation

Proceed to controller judgment. The one nonblocking finding (F1) can be dispositioned as a metric-definition clarification without artifact regeneration.
