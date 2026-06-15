# Docling Baseline Qualification Full Representation Export Evidence - 2026-06-15

Gate: `Full Representation Export Evidence Gate`
Role: evidence worker
Release/readiness: `NOT_READY`

## 1. Scope

This evidence gate ran the accepted candidate representation export harness with built-in handlers for the first-wave sample matrix.

This gate did not run live/network/EID/FDR/provider/LLM/analyze/readiness/release/PR commands. It did not change `FundDocumentRepository`, source policy, production parser behavior, Service, UI, Host, renderer, quality gate, extractor consumers, `EvidenceAnchor` or `CHAPTER_CONTRACT`.

## 2. Accepted Inputs

S1 read-only reference JSONs:

- `reports/representation-json/004393_2025_docling_full.json`
- `reports/representation-json/004393_2025_pdfplumber_full.json`
- `reports/representation-json/004393_2025_eid_html_render_full.json`

S4/S5/S6 accepted staged EID PDFs:

| Sample | Fund | PDF path | Accepted SHA-256 |
|---|---|---|---|
| S4 | `006597/2024` | `cache/eid-artifact-capture/docling-baseline-qualification-20260615/pdf/006597_2024_annual_report_eid.pdf` | `85c08ef235b06f5dd8867040193b547c7a91da3829c86eabf2817bbf1934e982` |
| S5 | `017641/2024` | `cache/eid-artifact-capture/docling-baseline-qualification-20260615/pdf/017641_2024_annual_report_eid.pdf` | `33e1898cfd80408f16c52bddd9f823a0577b000055ec9e69870ee1d212933f2c` |
| S6 | `110020/2024` | `cache/eid-artifact-capture/docling-baseline-qualification-20260615/pdf/110020_2024_annual_report_eid.pdf` | `307210ba3e55cf611334cebc3c0103824cf7c3352598522f257e741220dd6790` |

Local Docling artifacts:

- `cache/docling-artifacts/docling-project--docling-layout-heron/...`
- `cache/docling-artifacts/docling-project--docling-models/...`

Manifest:

- `reports/representation-json/full-representation-export-manifest-20260615.json`
- SHA-256: `bab5fcb81126ca501c553e94eafebcd64da2b537930833aaf81c118b648b6349`
- Entries: `12`

## 3. Commands

Initial export command:

```text
uv run python -m fund_agent.fund.documents.candidates.representation_export --manifest reports/representation-json/full-representation-export-manifest-20260615.json --run-built-in-handlers --docling-artifacts-path cache/docling-artifacts
```

Result: exited `0`.

Adapter fix validation:

```text
uv run pytest tests/fund/documents/test_candidate_representation_handlers.py tests/fund/documents/test_candidate_representation_export.py tests/fund/documents/test_docling_no_consumption_guards.py -q
```

Result:

```text
26 passed in 2.27s
```

```text
uv run ruff check fund_agent/fund/documents/candidates/representation_handlers.py fund_agent/fund/documents/candidates/representation_export.py tests/fund/documents/test_candidate_representation_handlers.py tests/fund/documents/test_candidate_representation_export.py
```

Result:

```text
All checks passed!
```

```text
git diff --check
```

Result: passed.

Overwrite rerun command after accepted-in-gate adapter fix:

```text
uv run python -m fund_agent.fund.documents.candidates.representation_export --manifest reports/representation-json/full-representation-export-manifest-20260615.json --run-built-in-handlers --docling-artifacts-path cache/docling-artifacts --allow-overwrite
```

Result: exited `0`.

Reason for overwrite:

- The first S4/S5/S6 Docling outputs were generated in this same evidence gate.
- They exposed a candidate adapter mapping defect: `heading_count=0`, `section_count=0`, `table_cell_count=0`.
- The defect was fixed narrowly in candidate adapter code and covered by no-live tests.
- S1 `reference_existing_json` files were read-only and not rewritten.
- No production cache path was overwritten.

## 4. Output Matrix

| Sample | Route | Output path | SHA-256 | Size bytes | Key metrics / status |
|---|---|---|---|---:|---|
| S1 `004393/2025` | Docling reference | `reports/representation-json/004393_2025_docling_full.json` | `069282b22d7926e93743cc12a8538e43eaf262aa165376d872552a76efac0e49` | 4780505 | `page_count=65`, `section_count=13`, `heading_count=213`, `table_count=95`, `cell_count=3493` |
| S1 `004393/2025` | pdfplumber reference | `reports/representation-json/004393_2025_pdfplumber_full.json` | `ef1787934e0a8b46bd9b3c8e03a9b760d6c987fd51952739c1f77ac7f24b6ab4` | 6335018 | `page_count=65`, `section_count=8`, `heading_count=8`, `table_count=92`, `cell_count=3640` |
| S1 `004393/2025` | EID HTML reference | `reports/representation-json/004393_2025_eid_html_render_full.json` | `63b5575b8591f572fa31cb6f359f70ad855460baa0adff383882bf27a0e2e22b` | 1511506 | `heading_candidate_count=261`, `table_count=802`, `table_cell_count=5526`, `has_page_number=false` |
| S4 `006597/2024` | Docling | `reports/representation-json/006597_2024_docling_full.json` | `ee193cc74542fb2792f2baf1984cf288cf9b55bd321ccee43aff7a6e69258307` | 2465451 | `page_count=70`, `section_count=229`, `heading_count=229`, `table_count=96`, `table_cell_count=2759` |
| S4 `006597/2024` | pdfplumber | `reports/representation-json/006597_2024_pdfplumber_full.json` | `003678ba8c2a50520011ebbe5fa7c9d991c912677353547376cf69f9f1b49370` | 386864 | `page_count=69`, `section_count=8`, `heading_count=8`, `table_count=85`, `table_cell_count=2561` |
| S4 `006597/2024` | EID HTML blocked | `reports/representation-json/006597_2024_eid_html_render_blocked.json` | `7cc3ac785dde2ca155456507d36fe4ae7bd2ff532135944b5087ff38b2b207b4` | 1817 | `eid_xbrl_html_render_candidate_not_available` |
| S5 `017641/2024` | Docling | `reports/representation-json/017641_2024_docling_full.json` | `7fe3c36eb3cb10108482bbe877bcdbbac7706471137046394d8322ccf77e56d7` | 5077159 | `page_count=110`, `section_count=208`, `heading_count=208`, `table_count=121`, `table_cell_count=7060` |
| S5 `017641/2024` | pdfplumber | `reports/representation-json/017641_2024_pdfplumber_full.json` | `80d6cdfff2003259c2891db20bc86476b6249cf3fc10bc976ba46a75228f3265` | 607345 | `page_count=109`, `section_count=6`, `heading_count=6`, `table_count=114`, `table_cell_count=6805` |
| S5 `017641/2024` | EID HTML blocked | `reports/representation-json/017641_2024_eid_html_render_blocked.json` | `391d0026f9a562fd728c3da88bfa488831dcf3123fb2bbe51ac29fdc838ed119` | 1817 | `eid_xbrl_html_render_candidate_not_available` |
| S6 `110020/2024` | Docling | `reports/representation-json/110020_2024_docling_full.json` | `ce2cbeb348101a21df563be4a60dd57d54ac73a3a14a7454845e7d36d56f86fb` | 4414725 | `page_count=84`, `section_count=222`, `heading_count=222`, `table_count=124`, `table_cell_count=5940` |
| S6 `110020/2024` | pdfplumber | `reports/representation-json/110020_2024_pdfplumber_full.json` | `8c0d0d94e78da5c44a36dc23650eb4cfca78c475ec2e5db19232c21bd0f3a0cd` | 555369 | `page_count=84`, `section_count=8`, `heading_count=8`, `table_count=118`, `table_cell_count=5633` |
| S6 `110020/2024` | EID HTML blocked | `reports/representation-json/110020_2024_eid_html_render_blocked.json` | `717871cb0dfe26549538edfe7be9e1e70718b8a5ac20453b72f4f5073aa64ac0` | 1817 | `eid_xbrl_html_render_candidate_not_available` |

## 5. Evidence Findings

Accepted evidence facts:

- Docling local artifact route can produce full candidate JSON for S4/S5/S6 with page, heading/section, table and cell locators.
- pdfplumber route can produce full candidate JSON for S4/S5/S6 with page, section and table/cell counts.
- EID HTML render remains blocked for S4/S5/S6 because no accepted render artifact URL/path exists for these samples in this gate.
- S1 reference JSONs remain read-only reference evidence and were not overwritten.

Comparative observations:

- Docling produced far richer heading/section candidates than pdfplumber for S4/S5/S6: `229/208/222` vs `8/6/8`.
- Docling produced table cell counts in the same order of magnitude as pdfplumber: S4 `2759 vs 2561`, S5 `7060 vs 6805`, S6 `5940 vs 5633`.
- Docling preserved bbox for headings/tables/cells; current pdfplumber candidate handler does not expose bbox.
- pdfplumber retains a smaller, section-catalog-oriented section set; Docling exposes many layout-level headings, including table-of-contents and subheading candidates.
- These are structural coverage facts only. They are not field correctness facts.

## 6. Blocked Claims

This evidence is explicitly:

- not source truth;
- not field correctness proof;
- not taxonomy compatibility proof;
- not parser replacement proof;
- not readiness proof;
- not release proof;
- not raw XML/XBRL proof;
- not an EID HTML render availability proof for S4/S5/S6.

## 7. Residuals

| Residual | Status | Next handling |
|---|---|---|
| Docling heading candidates are abundant and may include TOC/furniture headings. | Accepted residual | Candidate schema/design gate must define heading filtering and section tree semantics. |
| Docling/pdfplumber value correctness has not been compared against expected fields. | Deferred | Field-family correctness pilot gate. |
| EID HTML render for S4/S5/S6 remains blocked. | Deferred | Separate bounded EID HTML render discovery/evidence gate if needed. |
| S2/S3 provenance/hash issues remain unresolved. | Deferred | Separate provenance/disposition gate. |
| Release/readiness remains `NOT_READY`. | Accepted residual | Do not claim readiness/release/PR. |

## 8. Final Verdict

`VERDICT: FULL_REPRESENTATION_EXPORT_EVIDENCE_READY_FOR_REVIEW_NOT_READY`
