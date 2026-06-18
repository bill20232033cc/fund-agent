# Docling Candidate Runtime Containment And Same-report Benchmark Setup Planning Gate Plan - 2026-06-14

Status: DRAFT_FOR_REVIEW
Gate: `Docling Candidate Runtime Containment And Same-report Benchmark Setup Planning Gate`
Classification: `standard`
Readiness: `NOT_READY`

## 1. Goal

Produce a handoff-ready evidence plan for a future bounded benchmark that compares document representation quality on the ordinary non-REIT fund sample:

```text
fund_code=004393
fund_name=安信企业价值优选混合A
preferred report year=2025
fallback benchmark years=2024, 2023, 2022 only if 2025 identity or source route is blocked
```

The future benchmark must compare only document representation quality across:

1. `eid_xbrl_html_render_candidate`
2. current `pdfplumber_current` parser output through Fund documents / `FundDocumentRepository` ownership
3. `docling_candidate` output under explicit runtime containment

The immediate purpose of this planning gate is to prevent a repeat of the prior boundary incident where Docling conversion triggered RapidOCR model downloads before producing bounded evidence.

## 2. Motivation

The prior evidence artifact `docs/reviews/same-report-document-representation-quality-comparison-evidence-20260614.md` ended with:

```text
VERDICT: INSUFFICIENT_COMPARABLE_EVIDENCE_NOT_READY
```

Accepted blockers:

- `tier_a_ordinary_annual_not_available`: prior EID HTML annual samples were REIT annual reports.
- `docling_runtime_model_download_required`: `DocumentConverter().convert(...)` initiated RapidOCR model downloads from `modelscope.cn`.
- No route-strength verdict is allowed without a Tier A ordinary non-REIT annual same-report comparison.

The user has now selected `004393 / 安信企业价值优选混合A` as the future test fund. Existing control truth also records accepted bounded live EID single-source/no-fallback evidence for `004393 / 2021-2025`; this supports sample selection, not parser quality or readiness.

## 3. Non-goals

- Do not implement parser code.
- Do not add a Docling adapter.
- Do not install dependencies.
- Do not change `FundDocumentRepository`, source policy, parser behavior, extractor behavior, `EvidenceAnchor`, `CHAPTER_CONTRACT`, Service, Host, UI, renderer, quality gate, provider/LLM route, readiness, release, PR, or fallback policy.
- Do not read local `基金年报/` PDF bodies in this planning gate.
- Do not promote local PDFs to source truth.
- Do not compare PDF values to HTML values as field correctness proof.
- Do not claim raw XML direct download, raw XBRL instance availability, taxonomy compatibility, source truth, production parser replacement, or MVP/release readiness.
- Do not reintroduce Eastmoney, fund-company website, CNINFO, or any fallback source.

## 4. Direct Evidence Inputs

Required read set for the future evidence worker:

1. `AGENTS.md`
2. `docs/design.md`
3. `docs/current-startup-packet.md`
4. `docs/implementation-control.md`
5. `docs/reviews/same-report-document-representation-quality-comparison-evidence-20260614.md`
6. this plan after controller acceptance

Optional read set only if needed for exact command construction:

- `fund_agent/fund/documents/repository.py`
- `fund_agent/fund/documents/adapters/annual_report_pdf.py`
- `fund_agent/fund/documents/models.py`
- `fund_agent/fund/pdf/parser.py`
- Docling local API metadata through import/introspection only

Local data candidate inventory:

```text
基金年报/安信企业价值优选混合型证券投资基金2022年年度报告.pdf
基金年报/安信企业价值优选混合型证券投资基金2023年年度报告.pdf
基金年报/安信企业价值优选混合型证券投资基金2024年年度报告.pdf
基金年报/安信企业价值优选混合型证券投资基金2025年年度报告.pdf
```

These files are user-owned data artifact candidates. They are not current source truth and must not be body-read unless a later evidence gate records explicit user authorization and repository-compatible routing.

## 5. Current Planning Facts

| Fact | Status |
|---|---|
| Project `uv run python` can import Docling | observed in current workspace |
| Docling version | `2.93.0` observed through project environment |
| `PdfPipelineOptions` exposes `do_ocr` | observed through local import introspection |
| `PdfPipelineOptions.do_ocr` default | `True` observed through local import introspection |
| Prior Docling conversion triggered RapidOCR model downloads | accepted evidence fact in prior artifact |
| RapidOCR model files now exist in `.venv/lib/python3.11/site-packages/rapidocr/models` | observed residue from prior boundary incident; not promoted as accepted setup |
| Current production annual-report source policy | EID single-source only |
| `004393 / 2021-2025` annual-period source fact | accepted as bounded live EID single-source/no-fallback evidence, not parser quality proof |

## 6. Sample Matrix

The evidence gate must use this sample order:

| Priority | Sample | Purpose | Required identity proof |
|---|---|---|---|
| A1 | `004393 / 2025` annual report | preferred ordinary non-REIT same-report benchmark | same fund code, year, annual report type, EID/FDR source metadata, report title or send date |
| A2 | `004393 / 2024` annual report | fallback ordinary non-REIT benchmark if 2025 HTML render identity is unavailable | same proof as A1 |
| A3 | `004393 / 2023` annual report | fallback only if A1/A2 blocked | same proof as A1 |
| A4 | `004393 / 2022` annual report | fallback only if A1-A3 blocked | same proof as A1 |

Route-strength verdict requires at least one A-tier sample with:

```text
identity_match_status=identity_match_ordinary_non_reit_annual
```

If only local PDF file-name matching exists, classify as:

```text
identity_partly_matched_local_candidate_only
```

and do not issue a route-strength verdict.

## 7. Runtime Containment Strategy

The evidence gate must split Docling handling into containment checks before conversion.

Stage C0: Docling availability and configuration introspection

- import Docling through `uv run python`;
- record Docling version;
- inspect whether PDF pipeline options can set `do_ocr=False`;
- inspect whether table structure options are present;
- inspect all visible Docling `PdfPipelineOptions` and format options that may trigger model initialization, model artifact lookup, table-structure model use, layout model use, OCR, accelerator/device selection, remote artifact retrieval or network access;
- explicitly record whether any non-OCR pipeline stage appears to require model artifacts or network access;
- do not call `DocumentConverter().convert(...)`.

Stage C1: no-network/no-download containment plan

The evidence worker must define a local command wrapper that:

- sets `PdfPipelineOptions.do_ocr=False` for text-native annual reports;
- either disables table/layout model stages that would require unaccepted external artifacts, or proves through introspection that those stages are already local and do not perform network/model download;
- runs Docling conversion, if later allowed, in a subprocess that blocks Python socket connects during the conversion phase; official EID HTTP and FDR/PDF acquisition must happen before that conversion subprocess;
- sets offline/fail-closed environment variables where supported by the dependency stack, such as model-hub offline flags, but must not rely on undocumented environment variables as the sole containment mechanism;
- avoids OCR path by default;
- does not install or download dependencies;
- fails closed if Docling attempts network/model download;
- records whether existing model files are present but does not treat them as accepted evidence setup;
- classifies any conversion that succeeds only because of residual model files from the prior boundary incident as `DOCLING_MODEL_RESIDUAL_FROM_PRIOR_INCIDENT_NOT_PROMOTED`, not as proof that Docling is self-contained;
- writes no production cache or parser output.

Stage C2: bounded conversion only after C0/C1 pass

Only if C0 and C1 prove a no-network/no-download conversion setup, the future evidence gate may parse one identity-matched `004393` PDF path produced by Fund documents ownership.

If C0/C1 cannot prove containment, stop with:

```text
VERDICT: DOCLING_RUNTIME_CONTAINMENT_BLOCKED_NOT_READY
```

## 8. FundDocumentRepository Boundary

The future evidence worker must obtain the benchmark PDF through one of these routes, in order:

1. current `FundDocumentRepository` or `AnnualReportPdfAdapter` EID single-source path for `004393 / selected_year`;
2. existing repository cache entry whose metadata proves `selected_source=eid`, `source_mode=single_source_only`, `fallback_enabled=false`, `fallback_used=false`;
3. local `基金年报/` file only if a later evidence gate explicitly authorizes local user-owned PDF access and records why the route remains repository-compatible.

Forbidden:

- direct arbitrary PDF path parsing without repository-compatible ownership;
- direct body read of `基金年报/*.pdf` in planning;
- evidence worker invention of new production types, classes, modules, schemas, repository APIs, comparison schemas, or code artifacts;
- Service/UI/Host/renderer/quality-gate direct access to PDF, EID HTML, XBRL endpoints, parser cache or source helper;
- fallback source invocation.

## 9. EID HTML Render Route Setup

The future evidence gate must first determine whether an official EID XBRL HTML render exists for the selected `004393` annual report.

Allowed evidence path:

- bounded official EID HTTP GET/HEAD only to `eid.csrc.gov.cn` URLs discovered from accepted EID inputs or current official index/search endpoints;
- local parsing of JSON/HTML metadata, redirect location, title, navigation labels, section labels, table samples, content hash and locator candidates.

Stop if:

- official EID HTML render for `004393` selected year cannot be discovered without auth/captcha/manual browser state;
- public JSON/list/search cannot provide concrete instance id or HTML view path;
- redirects leave official EID domains;
- HTML body is blank/binary-only/image-only;
- evidence would require raw XML download, field correctness comparison or taxonomy proof.

## 10. Comparison Metrics

The future evidence artifact must compare representation quality, not value correctness.

Required metrics:

| Area | EID HTML render | pdfplumber current | Docling candidate |
|---|---|---|---|
| Identity | fund/year/type/idStr/render URL | EID PDF metadata/source URL/PDF hash | same repository-produced PDF path/hash |
| Section structure | navigation labels, anchors, heading paths | `ReportSection` ids/titles/offsets | element hierarchy, headings, page spans |
| Table structure | section-bound table ordinal, row/column labels | page/table index, headers, rows | table element path, row/column/cell model, bbox if available |
| Cell locator | render URL + section anchor + row/column path | page + table index + row/header | element path + page/bbox + row/column path |
| Narrative text | paragraph/title samples if present | raw text slices and section text | text blocks with labels/provenance |
| Failure class | official render missing/schema/identity/integrity class | parser section/table extraction gaps | runtime containment / conversion / structure gaps |
| Performance | fetch/parse elapsed if measured | parse elapsed | conversion elapsed only if contained |

## 11. Evidence Artifact

Recommended next evidence artifact:

```text
docs/reviews/docling-candidate-runtime-containment-same-report-benchmark-setup-evidence-20260614.md
```

Required sections:

1. Scope
2. Inputs Reviewed
3. Sample Selection And Identity Matrix
4. Docling Runtime Containment Checks
5. Official EID HTML Render Discovery For `004393`
6. FundDocumentRepository/PDF Ownership Proof
7. Route Availability Matrix
8. Section Structure Comparison
9. Table Structure Comparison
10. Locator Comparison
11. Narrative/Text Block Comparison
12. Performance And Runtime Side Effects
13. Blocked Proofs And Residuals
14. Next Gate Recommendation
15. Final Verdict

Allowed final verdicts:

```text
VERDICT: READY_FOR_CONTAINED_SAME_REPORT_COMPARISON_NOT_READY
VERDICT: HTML_RENDER_STRONGER_FOR_STRUCTURED_TABLES_NOT_READY
VERDICT: PDFPLUMBER_STRONGER_FOR_CURRENT_SCOPE_NOT_READY
VERDICT: DOCLING_STRONGER_FOR_DOCUMENT_REPRESENTATION_NOT_READY
VERDICT: HYBRID_ROUTE_REQUIRED_NOT_READY
VERDICT: DOCLING_RUNTIME_CONTAINMENT_BLOCKED_NOT_READY
VERDICT: IDENTITY_MATCHING_BLOCKED_NOT_READY
VERDICT: LOCAL_PDF_ONLY_NO_ROUTE_VERDICT_NOT_READY
VERDICT: INSUFFICIENT_COMPARABLE_EVIDENCE_NOT_READY
```

## 12. Allowed Evidence Commands

Allowed in evidence gate without live/parser conversion:

```text
git status --short
git status --branch --short
git diff --check
uv run python -c "<bounded Docling import/version/options introspection>"
find 基金年报 -maxdepth 1 -type f -name '*安信企业价值优选混合型证券投资基金*年度报告.pdf' -print
```

Allowed only after evidence gate restates exact commands and confirms containment:

```text
bounded official EID HTTP GET/HEAD to eid.csrc.gov.cn URLs only
repository-bounded EID single-source PDF metadata/path acquisition for 004393 selected year
current pdfplumber parser execution through Fund documents boundary
Docling conversion with do_ocr=False and conversion-phase socket blocking on one identity-matched repository-produced PDF path, only if C0/C1 prove no unaccepted model download path
```

Forbidden:

```text
dependency installation
Docling/OCR runtime model download
arbitrary network outside official EID URLs
direct local PDF body read outside repository-compatible ownership
new production types/classes/modules/schemas/repository APIs/comparison schema artifacts
production analyze/checklist/readiness/release/PR commands
provider/LLM commands
raw XML endpoint probing
taxonomy proof
field correctness comparison
source fallback invocation
FundDocumentRepository behavior change
Service/UI/Host/renderer/quality-gate consumer integration
```

## 13. Stop Conditions

Stop the evidence gate if any condition is true:

- Docling conversion requires OCR model download, model initialization network, dependency installation or uncontrolled runtime side effects.
- Docling cannot be configured with `do_ocr=False` or equivalent no-OCR bounded path for text-native PDFs.
- `004393` selected year cannot be matched across EID HTML render and FDR/PDF metadata.
- Only local filename-level PDF identity exists.
- Official EID HTML render requires auth/captcha/manual browser state.
- Redirects leave official EID domains.
- Any route requires Eastmoney, fund-company website, CNINFO or fallback.
- Evidence would need production repository/source/parser behavior changes.
- Evidence would need field correctness, raw XML or taxonomy claims.
- Workspace dirty state makes it impossible to write only the current evidence artifact.

## 14. Review Gates

Plan review:

- DS review
- MiMo review

Review focus:

- Whether the plan correctly uses `004393 / 安信企业价值优选混合A` as the primary ordinary non-REIT sample.
- Whether local `基金年报/` PDFs are kept as user-owned candidates and not source truth.
- Whether Docling runtime containment is required before any conversion.
- Whether `do_ocr=False` / no-network / no-download constraints are sufficient and reviewable.
- Whether all PDF access remains inside Fund documents / `FundDocumentRepository` ownership.
- Whether EID HTML render is still classified as `eid_xbrl_html_render_candidate`, not raw XBRL.
- Whether the plan avoids field correctness, taxonomy, source truth, parser replacement and readiness claims.

Controller judgment must classify findings as:

- `accepted`
- `accepted_with_rewrite`
- `rejected`
- `deferred`
- `unresolved_blocker`

Do not enter evidence gate until plan review passes and controller judgment accepts the plan.

## 15. Completion Report Format

The planning worker or controller must report:

```text
artifact path:
plan status:
primary benchmark sample:
non-goals preserved:
review required:
git diff --check:
next recommended gate:
residual risks:
```

## 16. Next Gate Recommendation

Next gate after plan review/controller acceptance:

```text
Docling Candidate Runtime Containment And Same-report Benchmark Setup Evidence Gate
```

The evidence gate may proceed only after controller acceptance. It must preserve `NOT_READY` and stop before any design/implementation gate.
