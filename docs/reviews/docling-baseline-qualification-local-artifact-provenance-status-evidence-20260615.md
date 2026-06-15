# Docling Baseline Qualification Local Artifact Provenance Status Evidence - 2026-06-15

Gate: `Docling Baseline Qualification Local Artifact Provenance Status Evidence Gate`
Role: evidence worker
Release/readiness: `NOT_READY`

## 1. Scope

This metadata-only evidence gate classifies visible local artifacts for the S1-S6 Docling baseline qualification sample matrix.

This gate does not read PDF bodies, parse PDFs, run `FundDocumentRepository`, run Docling conversion, run pdfplumber export, run EID/FDR/network/live commands, run provider/LLM/analyze/checklist/golden/readiness/release/PR commands, change source policy, or accept field correctness.

## 2. Commands Run

Allowed metadata-only commands:

```text
git branch --show-current
git status --short
stat -f '%N|%z|%Sm' <explicit cache/pdf paths>
stat -f '%N|%z|%Sm' <explicit parsed-report paths>
stat -f '%N|%z|%Sm' <explicit representation JSON paths>
jq '.summary_metrics // {...allowlisted summary fields...}' <explicit representation JSON paths>
jq '{rows: .rows | map({...allowlisted source metadata...})}' docs/reviews/mvp-small-golden-set-manual-evidence-intake-all5-20260609-source-payload.json
stat -f '%N|%z|%Sm' <explicit expected_fields.json paths>
```

No PDF body read or PDF hash command was run.

## 3. Preflight

| Item | Result |
|---|---|
| Branch | `feat/mvp-llm-incomplete-run-artifacts` |
| Status summary | `AGENTS.md` remains modified and rejected by prior rules-sync review; untracked residue remains; no source/test/runtime file was modified in this evidence gate. |

## 4. S1 Representation Evidence

Accepted same-report representation JSONs for S1:

| Path | Bytes | Modified |
|---|---:|---|
| `reports/representation-json/004393_2025_docling_full.json` | 4780505 | Jun 15 11:23:43 2026 |
| `reports/representation-json/004393_2025_pdfplumber_full.json` | 6335018 | Jun 15 11:23:43 2026 |
| `reports/representation-json/004393_2025_eid_html_render_full.json` | 1511506 | Jun 15 11:48:25 2026 |

Summary metrics:

| Route | Summary |
|---|---|
| Docling | `page_count=65`, `heading_count=213`, `table_count=95`, `cell_count=3493`, `has_page_number=true`, `has_content_hash=true`, status `FULL_LOCAL_DOCLING_ARTIFACT_REPRESENTATION_JSON_NOT_READY` |
| pdfplumber | `page_count=65`, `heading_count=8`, `table_count=92`, `cell_count=3640`, `has_page_number=true`, `has_content_hash=true`, status `LOCAL_PDFPLUMBER_FULL_EXPORT_FROM_EXISTING_PDF_AND_PARSED_CACHE_NOT_READY` |
| EID HTML render | `html_byte_size=822146`, `navigation_label_count=211`, `heading_candidate_count=261`, `table_count=802`, `table_cell_count=5526`, `has_page_number=false`, `has_content_hash=true` |

Disposition: S1 remains `accepted_tri_route_representation_seed_not_ready`. These JSONs are representation evidence only, not field correctness or source truth.

## 5. Local Cache Metadata

Visible PDF cache metadata:

| Sample | PDF path | Bytes | Modified | Filename provenance signal |
|---|---|---:|---|---|
| S1 `004393 / 2025` | `cache/pdf/004393_2025_annual_report_eid.pdf` | 832089 | Jun 13 16:28:13 2026 | EID-labeled |
| S2 `004393 / 2024` | `cache/pdf/004393_2024_annual_report_eid.pdf` | 841826 | Jun 13 16:28:18 2026 | EID-labeled |
| S3 `004194 / 2024` | `cache/pdf/004194_2024_annual_report_eid.pdf` | 852514 | May 22 15:02:30 2026 | EID-labeled |
| S4 `006597 / 2024` | `cache/pdf/006597_2024_annual_report_eid.pdf` | 792928 | May 29 05:51:59 2026 | EID-labeled filename only |
| S5 `017641 / 2024` | `cache/pdf/017641_2024_annual_report.pdf` | 2970819 | May 27 13:29:04 2026 | not EID-labeled |
| S6 `110020 / 2024` | `cache/pdf/110020_2024_annual_report.pdf` | 2639303 | May 27 12:58:14 2026 | not EID-labeled |

Visible parsed-report cache metadata:

| Sample | Parsed report path | Bytes | Modified |
|---|---|---:|---|
| S1 `004393 / 2025` | `cache/documents/parsed_reports/004393_2025_annual_report.json` | 263619 | Jun 13 16:28:17 2026 |
| S2 `004393 / 2024` | `cache/documents/parsed_reports/004393_2024_annual_report.json` | 288047 | Jun 13 16:28:23 2026 |
| S3 `004194 / 2024` | `cache/documents/parsed_reports/004194_2024_annual_report.json` | 368517 | May 22 15:02:36 2026 |
| S4 `006597 / 2024` | `cache/documents/parsed_reports/006597_2024_annual_report.json` | 232898 | May 29 05:52:03 2026 |
| S5 `017641 / 2024` | `cache/documents/parsed_reports/017641_2024_annual_report.json` | 396358 | May 27 13:29:13 2026 |
| S6 `110020 / 2024` | `cache/documents/parsed_reports/110020_2024_annual_report.json` | 356077 | May 27 12:58:21 2026 |

Parsed-report cache visibility is not source truth and is not accepted as baseline qualification input by this evidence alone.

## 6. Manual Source Metadata Cross-check

Allowlisted metadata from `docs/reviews/mvp-small-golden-set-manual-evidence-intake-all5-20260609-source-payload.json`:

| Sample | Source registry / URL class | Official document id | Hash status | Metadata implication |
|---|---|---|---|---|
| S2 `004393 / 2024` | EID URL `instance_show_pdf_id.do?instanceid=1248088` | `instanceid=1248088` | SHA-256 provided | Strong local EID candidate; no PDF body verification in this gate. |
| S3 `004194 / 2024` | EID URL `instance_show_pdf_id.do?instanceid=1248907` | `instanceid=1248907` | not provided | EID candidate with missing hash. |
| S4 `006597 / 2024` | CNINFO URL; source registry says EID locator provided but EID document id unknown | `cninfo:1222957988` | not provided | Filename conflicts with manual metadata; do not accept as EID-controlled without separate provenance proof. |
| S6 `110020 / 2024` | Fund-company CDN; source registry says EID locator provided but EID document id unknown | `efunds-bulletin-20250331-annual-report-110020` | not provided | Non-EID source metadata; needs EID-only acquisition or replacement. |
| S5 `017641 / 2024` | Fund-company URL; source registry says EID locator provided but EID document id unknown | `cifm:W020250331321243719367` | not provided | Non-EID source metadata; needs EID-only acquisition or replacement. |

## 7. Reference Candidate Metadata

Visible expected-fields fixtures:

| Path | Bytes | Modified |
|---|---:|---|
| `tests/fixtures/fund/small_golden_set/004393_2024/expected_fields.json` | 1951 | Jun 8 15:34:30 2026 |
| `tests/fixtures/fund/small_golden_set/004194_2024/expected_fields.json` | 1951 | Jun 8 15:34:30 2026 |
| `tests/fixtures/fund/small_golden_set/006597_2024/expected_fields.json` | 1951 | Jun 8 15:34:30 2026 |
| `tests/fixtures/fund/small_golden_set/017641_2024/expected_fields.json` | 2046 | Jun 8 15:34:30 2026 |
| `tests/fixtures/fund/small_golden_set/110020_2024/expected_fields.json` | 1951 | Jun 8 15:34:30 2026 |

Disposition: these are reference candidates only for this Docling baseline route. They do not automatically establish field correctness, row-level truth, retained excerpts or golden promotion.

## 8. Classification Matrix

| Sample | Artifact status | Provenance status | Acquisition decision | Reason |
|---|---|---|---|---|
| S1 `004393 / 2025` | accepted representation seed | accepted for representation evidence only | no acquisition for Gate 0A | Tri-route JSONs already accepted by prior controller judgments. |
| S2 `004393 / 2024` | visible local PDF/parsed candidate | EID metadata candidate with provided hash | `local_eid_candidate_ready_for_controller_acceptance` | EID URL/id and `_eid` cache naming align; no PDF body verification here. |
| S3 `004194 / 2024` | visible local PDF/parsed candidate | EID metadata candidate without hash | `local_eid_candidate_missing_hash_ready_for_controller_decision` | EID URL/id and `_eid` cache naming align; hash absent. |
| S4 `006597 / 2024` | visible local PDF/parsed candidate | provenance conflict | `needs_bounded_eid_only_acquisition_or_controller_provenance_decision` | `_eid` filename conflicts with accepted manual metadata pointing to CNINFO and unknown EID id. |
| S5 `017641 / 2024` | visible local PDF/parsed candidate | non-EID metadata | `needs_bounded_eid_only_acquisition_or_replacement` | local PDF and manual metadata are fund-company source, not EID-controlled. |
| S6 `110020 / 2024` | visible local PDF/parsed candidate | non-EID metadata | `needs_bounded_eid_only_acquisition_or_replacement` | local PDF and manual metadata are fund-company source, not EID-controlled. |

## 9. Blocked Claims

Still blocked:

- S2-S6 are accepted baseline qualification samples;
- S4 local `_eid` filename proves EID provenance;
- S5/S6 local PDFs can be used under EID single-source policy;
- any non-EID fallback is allowed;
- pdfplumber full representation JSON exists for S2-S6;
- Docling full representation JSON exists for S2-S6;
- EID HTML render is available for S2-S6;
- field correctness is proven;
- source truth is proven;
- raw XML / raw XBRL direct download is proven;
- taxonomy compatibility is proven;
- readiness/release/PR readiness.

## 10. Evidence Verdict

`VERDICT: LOCAL_ARTIFACT_STATUS_CLASSIFIED_WITH_PROVENANCE_GAPS_NOT_READY`

## 11. Recommended Next Gate

Recommended next gate:

`Docling Baseline Qualification Local Artifact Provenance Status Evidence Review Gate`

If accepted by review/controller:

1. Accept S2 as local EID candidate input for later pdfplumber export only if controller accepts metadata-only provenance.
2. Accept or request hash/provenance follow-up for S3.
3. Route S4-S6 to `Bounded EID-only Sample Acquisition Planning Gate` or profile-preserving replacement decision.
4. Do not proceed to pdfplumber export until active samples are accepted as EID-controlled or replaced.
