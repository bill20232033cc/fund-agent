# Docling Baseline Qualification Full Representation Export Plan - 2026-06-15

Status: `READY_FOR_PLAN_REVIEW_NOT_READY`
Gate: `Full Representation Export Planning Gate`
Role: planning worker
Release/readiness: `NOT_READY`

## 1. Goal

Plan the next reproducible route for full annual-report representation export after accepted staged EID artifact capture for S4/S5/S6.

The product question is whether Docling can become a baseline candidate by producing complete, comparable annual-report representation JSON across a bounded sample set, while current pdfplumber and EID HTML render remain comparable candidate routes where their inputs are available.

This planning gate does not run Docling, pdfplumber, EID HTML discovery, `FundDocumentRepository`, provider/LLM, analyzer/checklist, golden, readiness, release, PR, push or merge commands.

## 2. Source Of Truth

- `AGENTS.md`
- `docs/design.md`
- `docs/implementation-control.md`
- `docs/current-startup-packet.md`
- `docs/reviews/docling-baseline-qualification-plan-controller-judgment-20260615.md`
- `docs/reviews/docling-baseline-qualification-acquisition-status-plan-controller-judgment-20260615.md`
- `docs/reviews/docling-baseline-qualification-local-artifact-provenance-status-evidence-controller-judgment-20260615.md`
- `docs/reviews/docling-baseline-qualification-bounded-eid-only-acquisition-metadata-evidence-controller-judgment-20260615.md`
- `docs/reviews/docling-baseline-qualification-bounded-eid-only-artifact-capture-evidence-controller-judgment-20260615.md`
- `docs/reviews/same-report-full-annual-representation-json-evidence-controller-judgment-20260615.md`
- `docs/reviews/bounded-same-report-eid-html-render-discovery-controller-judgment-20260615.md`

Accepted current facts:

- S1 `004393 / 2025` has accepted full representation JSON artifacts for Docling, pdfplumber and EID HTML render under `reports/representation-json/`.
- S4 `006597 / 2024`, S5 `017641 / 2024` and S6 `110020 / 2024` have accepted staged EID PDF artifacts under `cache/eid-artifact-capture/docling-baseline-qualification-20260615/pdf/`.
- The accepted staged PDFs prove EID metadata-linked bytes and PDF integrity only. They do not prove field correctness, source truth, Docling quality, pdfplumber quality, EID HTML availability, taxonomy compatibility or readiness.
- S2 `004393 / 2024` remains a local EID candidate with stronger metadata alignment than S3, but no current gate has accepted it as a full baseline-qualification artifact.
- S3 `004194 / 2024` remains a local EID candidate with a hash/provenance residual.
- Existing production parser remains `pdfplumber -> ParsedAnnualReport -> self-developed extractor`; Docling and EID HTML render are candidate representation inputs only.
- EID single-source/no fallback remains binding. Eastmoney, fund-company website, CNINFO and other non-EID fallbacks are not allowed in this route.

## 3. Non-goals

- No code implementation in this planning gate.
- No Docling conversion.
- No pdfplumber export.
- No EID HTML render discovery or HTTP request.
- No PDF body parsing or PDF value comparison.
- No `FundDocumentRepository` execution.
- No production parser replacement.
- No `FundDocumentRepository` behavior change.
- No Service/UI/Host/renderer/quality-gate direct access to PDF, Docling, pdfplumber, EID HTML or parser cache.
- No source policy change and no non-EID fallback.
- No raw XML / raw XBRL instance claim.
- No field correctness, source truth, taxonomy compatibility, baseline qualification, readiness or release claim.
- No stage, push, PR or merge.

## 4. Planning Decision

Do not proceed directly to an ad hoc export evidence gate.

Reason:

- The repository currently has accepted full representation JSON artifacts for S1, but no tracked, reusable export harness or command contract that can regenerate the same artifact family for S4/S5/S6.
- Letting an evidence worker write one-off export scripts would make the next evidence hard to review, hard to reproduce and likely to bypass the Fund documents boundary.
- The next implementation should first create a candidate-only diagnostic export harness inside the Fund documents candidate boundary, with tests proving candidate-only status, explicit input manifests and no public consumer integration.

Controller implication:

- This plan routes to a no-live implementation gate before full export evidence.
- That implementation gate must be narrow and must not run full Docling conversion during normal tests.

## 5. Sample Matrix

| Sample | Fund/year | Current accepted artifact status | First-wave export disposition |
|---|---|---|---|
| S1 | `004393 / 2025` | Accepted Docling, pdfplumber and EID HTML full JSON already exist. | `reference_existing_json_only`; validate JSON shape and metrics, no re-export by default. |
| S2 | `004393 / 2024` | Local EID candidate with metadata alignment; not accepted as baseline artifact. | `defer_or_optional_after_provenance_decision`; do not block S4-S6 first wave. |
| S3 | `004194 / 2024` | Local EID candidate with hash/provenance residual. | `defer_until_hash_or_provenance_resolution`; do not use for baseline qualification yet. |
| S4 | `006597 / 2024` | Accepted staged EID PDF with SHA-256 `85c08ef235b06f5dd8867040193b547c7a91da3829c86eabf2817bbf1934e982`. | `required_first_wave_pdf_routes`; use staged path only. |
| S5 | `017641 / 2024` | Accepted staged EID PDF with SHA-256 `33e1898cfd80408f16c52bddd9f823a0577b000055ec9e69870ee1d212933f2c`. | `required_first_wave_pdf_routes`; use staged path only. |
| S6 | `110020 / 2024` | Accepted staged EID PDF with SHA-256 `307210ba3e55cf611334cebc3c0103824cf7c3352598522f257e741220dd6790`. | `required_first_wave_pdf_routes`; use staged path only. |

First-wave evidence target:

- S1 remains the accepted reference sample.
- S4/S5/S6 become the required first-wave expansion for Docling and pdfplumber full representation export.
- EID HTML render route for S4/S5/S6 is classified separately because it cannot consume staged PDF paths. It requires accepted EID HTML render URL discovery, or it must produce explicit blocked JSON artifacts.
- S2/S3 are deferred unless a later controller decision accepts local-cache provenance or opens a bounded EID evidence gate for them.

This first wave is not the final six-sample baseline qualification proof.

## 6. Required Implementation Gate

Next gate after plan acceptance:

`Candidate Representation Export Harness No-live Implementation Gate`

Allowed write set:

```text
fund_agent/fund/documents/candidates/representation_export.py
tests/fund/documents/test_candidate_representation_export.py
docs/reviews/docling-baseline-qualification-full-representation-export-implementation-evidence-20260615.md
```

Conditional write set, only if imports require it:

```text
fund_agent/fund/documents/candidates/__init__.py
tests/README.md
fund_agent/fund/README.md
```

Forbidden write set:

```text
fund_agent/fund/documents/repository.py
fund_agent/fund/documents/sources.py
fund_agent/fund/documents/cache.py
fund_agent/services/
fund_agent/host/
fund_agent/ui/
fund_agent/fund/quality_gate.py
fund_agent/fund/extractors/
docs/design.md
docs/implementation-control.md
docs/current-startup-packet.md
cache/pdf/
reports/representation-json/
```

Implementation contract:

- Define a candidate-only export manifest model that records sample id, fund code, report year, route kind, input artifact path, accepted input hash, provenance judgment path and output path.
- Define route kinds for:
  - `docling_pdf_candidate`
  - `pdfplumber_pdf_candidate`
  - `eid_xbrl_html_render_candidate`
- Define a common representation JSON envelope:
  - `schema_version`
  - `candidate_status`
  - `source_kind`
  - `sample_id`
  - `fund_code`
  - `document_year`
  - `report_type`
  - `input_artifact`
  - `summary_metrics`
  - `sections`
  - `headings`
  - `paragraphs`
  - `tables`
  - `text_blocks`
  - `failure_taxonomy`
  - `blocked_claims`
- Provide pure validation helpers for manifest/path/hash/envelope checks.
- Provide blocked-result builders for route-unavailable cases, especially EID HTML render unavailable for S4/S5/S6.
- Do not expose candidate internals from `fund_agent/fund/documents/__init__.py`.
- Do not make Docling, pdfplumber or EID HTML render a production dependency of Service/UI/Host/renderer/quality gate.
- Do not call network, provider/LLM, analyzer/checklist, golden, readiness or release commands.

Unit tests:

- Use synthetic manifests and fake route outputs.
- Assert candidate-only statuses remain `not_proven` / `not_authorized`.
- Assert non-EID source kinds are rejected.
- Assert output paths cannot target production cache.
- Assert `eid_xbrl_html_render_candidate` can produce blocked JSON without raw XML, field correctness, taxonomy or source-truth claims.
- Assert candidate internals remain non-public exports.

Validation commands for implementation gate:

```text
uv run pytest tests/fund/documents/test_candidate_representation_export.py tests/fund/documents/test_docling_candidate_models.py tests/fund/documents/test_docling_no_consumption_guards.py -q
uv run ruff check fund_agent/fund/documents/candidates/representation_export.py tests/fund/documents/test_candidate_representation_export.py
git diff --check
```

## 7. Full Representation Export Evidence Gate

Next gate after implementation acceptance:

`Full Representation Export Evidence Gate`

Allowed evidence inputs:

```text
reports/representation-json/004393_2025_docling_full.json
reports/representation-json/004393_2025_pdfplumber_full.json
reports/representation-json/004393_2025_eid_html_render_full.json
cache/eid-artifact-capture/docling-baseline-qualification-20260615/pdf/006597_2024_annual_report_eid.pdf
cache/eid-artifact-capture/docling-baseline-qualification-20260615/pdf/017641_2024_annual_report_eid.pdf
cache/eid-artifact-capture/docling-baseline-qualification-20260615/pdf/110020_2024_annual_report_eid.pdf
```

Allowed tracked evidence artifact:

```text
docs/reviews/docling-baseline-qualification-full-representation-export-evidence-20260615.md
```

Allowed generated report artifacts, if the implementation gate accepts the harness:

```text
reports/representation-json/006597_2024_docling_full.json
reports/representation-json/006597_2024_pdfplumber_full.json
reports/representation-json/006597_2024_eid_html_render_blocked.json
reports/representation-json/017641_2024_docling_full.json
reports/representation-json/017641_2024_pdfplumber_full.json
reports/representation-json/017641_2024_eid_html_render_blocked.json
reports/representation-json/110020_2024_docling_full.json
reports/representation-json/110020_2024_pdfplumber_full.json
reports/representation-json/110020_2024_eid_html_render_blocked.json
```

Evidence gate required records:

- exact command lines;
- input artifact path and SHA-256;
- output path and JSON SHA-256;
- route kind;
- page count;
- section count with definition;
- heading count;
- paragraph/text block count;
- table count;
- table cell count;
- has page number;
- has bbox;
- has section tree;
- has table cell locator;
- has content hash;
- has source URL or source locator;
- runtime duration if available;
- memory or CPU caveat if observable without extra tooling;
- per-route failure taxonomy;
- blocked claims and residuals.

Acceptance vocabulary:

- `FULL_EXPORT_JSON_ACCEPTED_CANDIDATE_NOT_READY`
- `PARTIAL_EXPORT_WITH_BLOCKED_ROUTES_NOT_READY`
- `EXPORT_HARNESS_BLOCKED_NOT_READY`
- `EXPORT_OUTPUT_REJECTED_NOT_READY`

The evidence gate may compare representation completeness metrics. It must not compare table values to PDF manually or claim field correctness.

## 8. EID HTML Route Handling

EID HTML render does not consume staged PDFs. Therefore S4/S5/S6 EID HTML output in the first full-export evidence gate must be one of:

- accepted full JSON only if a prior or same explicitly authorized bounded EID HTML render discovery gate provides official render URLs and local HTML-derived artifacts; or
- blocked JSON with `route_failure=eid_html_render_url_not_accepted_for_sample`.

The first-wave export evidence should prefer blocked JSON for S4/S5/S6 unless the controller opens a separate bounded EID HTML discovery gate.

Do not infer EID HTML URL availability from PDF `uploadInfoId`, local PDF filename or route agreement.

## 9. Stop Conditions

Stop before implementation if:

- implementation would need to modify `FundDocumentRepository`, production source policy, Service, UI, Host, renderer, quality gate or extractor behavior;
- implementation requires making Docling a production parser replacement;
- implementation needs live/network access;
- implementation cannot keep candidate internals out of public `fund_agent.fund.documents` exports;
- implementation would write to `cache/pdf`;
- implementation would use Eastmoney, fund-company website, CNINFO or other non-EID fallback.

Stop before evidence execution if:

- the export harness is not accepted by review/controller judgment;
- evidence worker would need ad hoc script design not covered by the accepted harness;
- Docling attempts to download models or use network;
- full export requires OCR or layout-model changes not covered by accepted containment;
- pdfplumber export cannot consume explicit staged paths without production cache mutation;
- EID HTML discovery is needed for S4/S5/S6 but not explicitly authorized;
- output JSON omits required non-proof fields or blocked-claim guards.

## 10. Review Checklist

Reviewers must check:

- Does the plan avoid treating Docling output as source truth?
- Does it avoid treating HTML render as raw XML / raw XBRL?
- Does it preserve EID single-source/no fallback?
- Does it avoid non-EID local PDFs for S4/S5/S6?
- Does it keep S3 hash/provenance residual from being silently accepted?
- Does it avoid writing to or relying on production-shaped `cache/pdf` for S4/S5/S6?
- Does it route to a reproducible harness before evidence export?
- Does the proposed harness stay inside Fund documents candidate internals?
- Does it avoid Service/UI/Host/renderer/quality-gate access to parser or source artifacts?
- Does it keep release/readiness as `NOT_READY`?

## 11. Next Gate Recommendation

Immediate next gate:

`Full Representation Export Plan Review Gate`

If accepted:

`Candidate Representation Export Harness No-live Implementation Gate`

After implementation acceptance:

`Full Representation Export Evidence Gate`

Deferred entries:

- `S2/S3 Local Cache Provenance Resolution Gate`
- `S4/S5/S6 EID HTML Render Discovery Gate`
- `EID Staged PDF Cache Promotion Planning Gate`
- `Field Correctness Validation Gate`
- `FundDisclosureDocument Production Schema / Repository Integration Planning Gate`
- `Docling Baseline Qualification Controller Closeout Gate`
- readiness/release/PR gates

## 12. Final Verdict

`VERDICT: READY_FOR_PLAN_REVIEW_NOT_READY`
