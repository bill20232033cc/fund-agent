# Docling Full-document Coverage Evidence - 2026-06-16

Gate: `Docling Full-document Coverage Evidence Gate`
Role: evidence worker
Release/readiness: `NOT_READY`

## 1. Scope

This evidence gate evaluates whether accepted candidate Docling JSON outputs contain full-document coverage signals across S1/S4/S5/S6.

It does not run Docling conversion, live/network/EID/FDR/PDF/source acquisition, pdfplumber export, provider/LLM, analyze/checklist/golden/readiness/release/PR commands, and does not modify source, tests, runtime behavior, `FundDocumentRepository`, parser behavior, source policy, `EvidenceAnchor`, CHAPTER_CONTRACT, Service, Host, UI, renderer or quality gate.

This gate explicitly preserves:

- `candidate_only`
- `not_source_truth`
- `not_full_field_correctness`
- `not_baseline_promotion`
- `not_readiness_proof`

## 2. Evidence Inputs

| Input | Role |
| --- | --- |
| `docs/current-startup-packet.md` | Current active gate and guardrails |
| `docs/implementation-control.md` | Control truth |
| `docs/reviews/docling-multi-sample-runtime-containment-reevidence-controller-judgment-20260616.md` | Accepted runtime containment source |
| `reports/representation-json/004393_2025_docling_full.json` | S1 accepted Docling candidate JSON |
| `reports/docling-runtime-containment/20260616/outputs/006597_2024_docling_full.json` | S4 accepted isolated runtime output |
| `reports/docling-runtime-containment/20260616/outputs/017641_2024_docling_full.json` | S5 accepted isolated runtime output |
| `reports/docling-runtime-containment/20260616/outputs/110020_2024_docling_full.json` | S6 accepted isolated runtime output |
| `reports/docling-full-document-coverage/20260616/coverage-summary.json` | Coverage summary generated from the JSONs above |

## 3. Method

The evidence worker read the four local candidate JSON files and computed:

- page coverage by any extracted block;
- heading, paragraph and table page distribution;
- heading locator, paragraph locator, table shape and table-cell locator completeness;
- paragraph text and table-cell text completeness;
- expected annual-report section keyword coverage for 12 common annual-report section families;
- obvious gap flags: pages with no block and missing section keywords.

S1 uses the current full representation schema with `pages` and `provenance_locator` objects. S4/S5/S6 use the runtime-containment candidate schema, where table-cell locator is represented by `table_id + table.page_number + cell_index + row_start + column_start`. The evidence treats both forms as candidate locator evidence only.

## 4. Coverage Matrix

| Sample | Fund | Year | Pages | Pages with block | Headings | Paragraphs | Tables | Cells | Heading locator | Paragraph locator | Table shape | Cell locator | Missing section keywords |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| S1 | `004393` | 2025 | 65 | 65 / 100% | 213 | 457 | 95 | 3493 | 100% | 100% | 100% | 100% | none |
| S4 | `006597` | 2024 | 70 | 70 / 100% | 229 | 737 | 96 | 2759 | 100% | 100% | 100% | 100% | none |
| S5 | `017641` | 2024 | 110 | 110 / 100% | 208 | 856 | 121 | 7060 | 100% | 100% | 100% | 100% | none |
| S6 | `110020` | 2024 | 84 | 84 / 100% | 222 | 840 | 124 | 5940 | 100% | 100% | 100% | 100% | none |

## 5. Section Keyword Coverage

All four samples contained local candidate text matching these annual-report section families:

- important notice / directory;
- fund profile;
- main financial indicators and NAV performance;
- manager report;
- custodian report;
- audit report;
- financial statements and notes;
- portfolio report;
- holder information;
- open-ended fund share changes;
- major events;
- reference-file directory.

This is a coverage signal only. It does not prove semantic correctness, value correctness, or source truth.

## 6. Accepted Candidate Coverage Facts

| Claim | Evidence result |
| --- | --- |
| Every declared page has at least one extracted candidate block | PASS for S1/S4/S5/S6 |
| Every sample has paragraph text and paragraph locator coverage | PASS for S1/S4/S5/S6 |
| Every sample has table shape and table-cell locator coverage | PASS for S1/S4/S5/S6 |
| Every sample has 12 common annual-report section keyword families present | PASS for S1/S4/S5/S6 |
| Evidence proves full field correctness | REJECTED |
| Evidence proves source truth | REJECTED |
| Evidence promotes Docling to production baseline | REJECTED |
| Evidence proves readiness/release | REJECTED |

## 7. Residuals

| Residual | Status | Owner | Next handling |
| --- | --- | --- | --- |
| Field-level correctness beyond selected facts | open | baseline qualification owner | comparative correctness / fact-family expansion gate |
| EvidenceAnchor mapping from candidate locators | open | documents/schema owner | EvidenceAnchor mapping gate |
| Comparative quality against pdfplumber and EID HTML render | open | baseline qualification owner | route disposition gate |
| Production model artifact provenance and dependency policy | open | production integration owner | provenance/compliance gate |
| Cost/performance threshold and cache policy | open | baseline qualification owner | performance/cache/cost disposition gate |

## 8. Validation

Commands / checks used:

```text
git status --short
git status --branch --short
git diff --check
jq 'keys' reports/representation-json/004393_2025_docling_full.json
jq '{page0: .pages[0], section0: .sections[0], heading0: .headings[0], paragraph0: .paragraphs[0], table0: .tables[0], metrics, summary_metrics}' reports/representation-json/004393_2025_docling_full.json
jq '{keys: keys, heading0: .headings[0], paragraph0: .paragraphs[0], table0_keys: (.tables[0] | keys), table0: .tables[0] | del(.cells), cell0: .tables[0].cells[0], summary_metrics}' reports/docling-runtime-containment/20260616/outputs/006597_2024_docling_full.json
node_repl local JSON coverage computation over S1/S4/S5/S6
python -m json.tool reports/docling-full-document-coverage/20260616/coverage-summary.json
```

No live/source acquisition, Docling conversion, provider/LLM, readiness, release or PR command was run.

## 9. Verdict

```text
VERDICT: ACCEPT_FULL_DOCUMENT_COVERAGE_EVIDENCE_READY_FOR_EVIDENCEANCHOR_MAPPING_PLANNING_NOT_READY
```
