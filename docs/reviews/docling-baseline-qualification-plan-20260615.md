# Docling Baseline Qualification Plan - 2026-06-15

Status: `PLAN_FIXED_NOT_READY`
Gate: `Docling Baseline Qualification Planning Gate`
Role: planning worker only
Release/readiness: `NOT_READY`

## Worker Self-check

- Current gate / role: planning worker for Docling baseline qualification; not controller, not implementation, not evidence executor.
- Source of truth: `AGENTS.md`, current startup/control docs, relevant `docs/design.md` lines, accepted Docling / same-report JSON / EID HTML render judgments, and high-level metrics from `reports/representation-json/`.
- Scope boundary: write this single plan artifact only; no source, test, runtime, control-doc, design-doc, readiness, release, PR, stage or commit action.
- Stop conditions: any plan path that treats Docling as current production baseline, source truth, field correctness proof, taxonomy proof, raw XML proof, readiness proof, or non-EID fallback must stop.
- Validation: `git diff --check`.

## 1. Scope And Motivation

This plan defines the evidence sequence required to decide whether Docling can qualify as a production baseline candidate for annual-report document representation.

The motivation is the accepted design gap: current production parsing is `pdfplumber -> raw_text / tables -> locate_sections -> ParsedAnnualReport -> self-owned extractors -> EvidenceAnchor / CHAPTER_CONTRACT / audit / report generation`. That chain supports accepted extractor surfaces, but it is not a complete, reusable annual-report document representation. Docling has shown useful full-document representation on `004393 / 2025`, but current evidence is still candidate-only and single-sample.

This plan does not assume Docling is the baseline. It defines gates that must fail closed before any later controller may consider Docling beyond auxiliary candidate status.

## 2. Baseline Candidate Versus Production Baseline

| Term | Meaning | What it allows | What it does not allow |
|---|---|---|---|
| `baseline candidate` | A candidate document representation route with enough containment, reproducibility, multi-sample coverage, locator, EvidenceAnchor mapping, field-correctness comparison and performance evidence to justify a future implementation planning gate. | Future reviewed planning for repository-internal integration or hybrid routing. | Production parser replacement, public source-kind change, extractor consumer integration, source-truth claim, readiness claim. |
| `production baseline` | The accepted default production representation route inside `FundDocumentRepository` / Fund documents, after separate design, implementation, review and acceptance gates. | Future production behavior only after controller acceptance and code implementation. | Cannot be declared by this plan, by single-sample Docling evidence, or by representation JSON existence. |

Docling can only move from `candidate` to `baseline candidate` after all gates in this plan pass. It can only become `production baseline` after later implementation and controller judgment gates that are outside this plan.

## 3. Non-goals And Forbidden Claims

Non-goals:

- No source, test, runtime, README, design or control-doc modification in this planning gate.
- No Docling conversion, PDF parser execution, EID/FDR/network, provider/LLM, analyze/checklist, golden, readiness, release or PR execution in this planning gate.
- No production parser replacement plan in this artifact.
- No `FundDocumentRepository.load_annual_report()` behavior change in this artifact.
- No `EvidenceAnchor` schema or `EvidenceSourceKind` expansion in this artifact.
- No Service/UI/Host/renderer/quality-gate direct access to Docling, PDFs, parser cache or parser helpers.
- No Eastmoney, CNINFO, fund-company website or any non-EID fallback.

Forbidden claims:

- Docling is current production baseline.
- Docling output is field correctness proof.
- Docling Markdown, JSON, HTML, OCR text, raw text or table cells are source truth.
- EID HTML render is raw XML / raw XBRL instance proof.
- Taxonomy compatibility is proven.
- Release, PR or readiness is achieved.

## 4. Current Accepted Evidence Facts

| Evidence fact | Current accepted status | Boundary |
|---|---|---|
| Route A local Docling benchmark for `004393 / 2025` succeeded with socket-blocked local artifacts, `do_ocr=false`, `do_table_structure=true`, 65 pages, 213 headings, 95 tables, 3493 cells in full JSON. | Candidate representation evidence accepted. | One local sample only; not source truth, field correctness, production parser, model provenance acceptance or readiness. |
| Docling JSON, not Markdown tables, is the accepted primary structured input for candidate mapping. | Accepted mapping/normalization plan fact. | Markdown whitespace and numeric splitting require deterministic normalization and fail-closed parsing boundaries. |
| Candidate internals exist under `fund_agent/fund/documents/candidates/`, with no public export, unchanged `EvidenceAnchor`, unchanged `EvidenceSourceKind`, unchanged repository production behavior and no-consumption guards. | Accepted no-live implementation fact. | Internal candidate tools only; no consumer integration or production behavior change. |
| Same-report full representation JSON exists for Docling and pdfplumber for `004393 / 2025`; EID HTML render JSON was later accepted after bounded discovery. | Accepted same-report representation evidence. | JSON existence is representation evidence, not tri-route quality verdict or field correctness. |
| EID HTML render same-report candidate for `004393 / 2025` has official request provenance, `source_kind=eid_xbrl_html_render_candidate`, 822146 HTML bytes, 211 navigation labels, 261 heading candidates, 802 tables, 5526 table cells and no PDF page anchors. | Accepted candidate evidence. | HTML render is not raw XML, source truth, taxonomy proof or production source. |
| Current EID single-source policy remains production source policy. | Accepted current implementation/design fact. | `not_found` / `unavailable` terminal; `schema_drift` / `identity_mismatch` / `integrity_error` fail closed; no non-EID fallback. |

Current artifact availability is intentionally uneven:

| Scope | Accepted current state | Required handling before evidence execution |
|---|---|---|
| S1 `004393 / 2025` | Docling full JSON, pdfplumber full JSON and EID HTML render full JSON are accepted representation evidence. | May seed later gates, still not field truth. |
| S2-S6 local EID-controlled annual-report PDFs | Not proven by this plan. Some historical 2024 small-golden EID/FDR acquisition evidence may exist, but this plan does not accept those bodies as Docling qualification inputs until a bounded acquisition-status gate classifies them. | Must pass EID-only acquisition status planning and, where missing, bounded EID-only sample acquisition execution before Gate A. |
| S2-S6 pdfplumber full representation JSON | Not currently accepted. | Must be exported and accepted as prerequisite representation artifacts before Gate B uses pdfplumber parity/comparison thresholds. |
| S2-S6 EID HTML render JSON | Not currently accepted. | Optional per sample; absence must be classified before Gate D. Gate D must degrade to two-route comparison where no separately accepted EID HTML render exists. |
| S2-S6 reviewed/golden field references | Not currently accepted. | True field correctness cannot be measured until same-report manual reviewed reference facts or golden references are acquired and accepted. Route agreement cannot fill this role. |

## 5. Required Sample Matrix

The qualification set must be multi-sample before Docling can become a baseline candidate. The minimum matrix is six fund/year profiles:

| Sample | Fund / year | Profile role | Why required | Minimum representation targets |
|---|---|---|---|---|
| S1 | `004393 / 2025` 安信企业价值优选混合A | Active fund, accepted same-report tri-route seed | Existing Docling/pdfplumber/EID HTML JSONs; baseline regression seed. | Full section hierarchy, portfolio tables, manager table, financial statements, manager holding, page/bbox anchors. |
| S2 | `004393 / 2024` 安信企业价值优选混合A | Same fund prior year | Tests year stability and prevents overfitting to one 2025 report layout. | Same field families as S1; same-year identity must not cross-apply. |
| S3 | `004194 / 2024` 招商中证1000指数增强A | Enhanced index | Tests index/enhanced-index profile, benchmark/methodology/constituents and tracking-related tables. | Benchmark identity, methodology availability, constituents availability, tracking-error locator candidates. |
| S4 | `006597 / 2024` 国泰利享中短债债券A | Bond fund | Tests bond holding, NAV/drawdown-adjacent evidence, bond risk text and multi-share-class identity. | Bond holding rows, duration/credit/leverage/liquidity text candidates, A-share class locators. |
| S5 | `017641 / 2024` 摩根标普500指数(QDII)人民币A | QDII | Tests overseas exposure, currency / market risk and disclosure gaps. | Overseas holding/benchmark/risk paragraphs, explicit unavailable/deferred-policy handling. |
| S6 | `110020 / 2024` 易方达沪深300ETF联接A | Index / ETF-linked reviewed candidate | Tests index methodology, target/underlying fund holding and constituents evidence insufficiency. | Target fund holding rows, methodology and constituents locator candidates, explicit insufficiency classification. |

Expansion rule: if any fund/year has missing local EID-controlled annual report artifact, the gate may add a replacement only through a controller-approved EID-only sample acquisition gate. Replacement must preserve profile coverage and must not use non-EID fallback.

## 6. Evidence Gate Sequence

### Gate 0. Prerequisite Artifact And Reference Establishment

Goal: make the hidden prerequisites explicit before any Docling runtime or coverage evidence execution. Gate 0 is a dependency family, not proof that Docling qualifies.

Required sub-gates:

| Sub-gate | Goal | Output needed before later gates |
|---|---|---|
| 0A acquisition status planning | Classify S1-S6 as `accepted_local_artifact`, `needs_bounded_eid_acquisition`, `replace_required`, or `out_of_scope`. | Sample status matrix with source-policy boundary and owner. |
| 0B bounded EID-only sample acquisition execution, if needed | Acquire missing annual-report PDFs only through EID single-source/FDR-authorized route, with no fallback. | Accepted local EID-controlled PDF artifacts and source metadata for every active sample. |
| 0C pdfplumber full representation export | Produce same-report pdfplumber full representation JSON for every active sample from accepted local artifacts. | Accepted pdfplumber representation JSONs and summary metrics. |
| 0D field-reference establishment | Establish same-report manual reviewed reference facts or golden references for each field family that Gate D will score. | Accepted reference-fact manifest by sample and field family. |
| 0E EID HTML render availability classification | Classify EID HTML render candidate availability per active sample. | `accepted_eid_html_render_json`, `not_authorized`, `not_found`, or `deferred` status; no fabricated URLs. |

Allowed commands:

- Status/metadata commands approved by the controller for each sub-gate.
- `python -m json.tool <artifact>.json > /dev/null`
- `jq '.summary_metrics' <representation.json>`
- `git diff --check`

Forbidden commands:

- Any non-EID source acquisition.
- Any Docling conversion during acquisition-status planning.
- Any field-reference shortcut based only on Docling/pdfplumber/EID HTML route agreement.
- Provider/LLM, analyze/checklist, golden promotion, readiness, release, PR, stage, commit or push.

Pass thresholds:

- 100% active samples have accepted local EID-controlled PDF artifacts or are replaced by a controller-approved profile-preserving EID-only sample.
- 100% active samples have accepted pdfplumber full representation JSON before Gate B.
- Gate D true field correctness scope is limited to sample/field-family pairs with accepted same-report reviewed/golden reference facts.
- Samples without EID HTML render JSON are explicitly marked as two-route comparison only.

Stop conditions:

- S2-S6 artifacts are assumed available without status classification.
- Any worker uses route agreement as truth reference.
- Any non-EID fallback is introduced.
- Any sample acquisition or reference establishment tries to claim readiness.

### Gate A. Runtime Containment / Reproducibility Evidence

Goal: prove Docling execution can be repeated for the sample matrix with local artifact containment, deterministic configuration and no hidden network/model download.

Inputs:

- Accepted local artifact manifest from Route A.
- Candidate sample matrix.
- Gate 0 accepted EID-controlled local annual-report PDFs and source metadata for all active samples.
- Gate 0 sample status matrix and replacement decisions, if any.
- Candidate conversion runner or script defined by a later implementation plan.

Allowed commands:

- `git branch --show-current`
- `git status --short`
- `python -m json.tool <candidate-manifest.json> > /dev/null`
- `uv run python <approved_docling_conversion_runner> --sample-manifest <matrix> --artifacts-path cache/docling-artifacts --offline --socket-block --no-ocr --table-structure`
- `uv run pytest <approved no-live runtime containment tests> -q`
- `git diff --check`

Forbidden commands:

- Unbounded network, EID/FDR/PDF download, sample acquisition or pdfplumber baseline export inside Gate A.
- Provider/LLM, analyze/checklist, golden, readiness, release, PR, push, stage or commit.
- Any command that lets Docling download models at runtime.
- Any non-EID source acquisition.

Artifacts:

- `reports/docling-baseline-qualification/runtime-containment/<run-id>/manifest.json`
- `reports/docling-baseline-qualification/runtime-containment/<run-id>/per-sample-summary.json`
- Evidence artifact under `docs/reviews/`.

Validation commands:

- `python -m json.tool` for every JSON artifact.
- Hash check against artifact manifest.
- Socket-block log check.
- `git diff --check`.

Pass thresholds:

- 100% samples run with `HF_HUB_OFFLINE=1`, `TRANSFORMERS_OFFLINE=1`, explicit `artifacts_path`, socket-blocked process and recorded Docling/package versions.
- 0 runtime model downloads.
- 0 non-EID source reads.
- 0 missing output hashes.
- Conversion failure rate must be 0 for `DOCLING_ELIGIBLE_AS_BASELINE_CANDIDATE_NOT_READY` or `DOCLING_ELIGIBLE_AS_HYBRID_PRIMARY_NOT_READY`.
- Exactly 1 isolated, profile-specific, fully classified fail-closed conversion failure can only map to `DOCLING_REMAINS_AUXILIARY_CANDIDATE_NOT_READY` at Gate F.
- Any unclassified conversion failure or 2+ conversion failures map to `DOCLING_REJECTED_AS_BASELINE_CANDIDATE_NOT_READY` unless the controller explicitly narrows the sample matrix and reopens Gate 0.

Stop conditions:

- Any hidden network/model download attempt.
- Any source path outside EID/FDR-approved local artifact boundaries.
- Any worker tries to treat local benchmark PDF as source truth.
- Any sample identity mismatch.

### Gate B. Full-document Coverage Evidence

Goal: prove Docling covers complete annual-report structure across the sample matrix, not only isolated tables.

Inputs:

- Gate A per-sample Docling JSON outputs.
- Gate 0 accepted pdfplumber full representation exports for the same samples.
- Gate 0 EID HTML render availability classification and accepted EID HTML render representation JSON where authorized and available.

Allowed commands:

- `python -m json.tool <representation.json> > /dev/null`
- `jq '.summary_metrics' <representation.json>`
- `uv run python <approved_representation_metrics_script> --inputs <manifest>`
- `git diff --check`

Forbidden commands:

- Field extraction promotion.
- CHAPTER_CONTRACT consumption.
- Service/UI/Host/renderer/quality-gate integration.
- Any readiness/release/PR command.

Artifacts:

- Per-sample route metrics JSON.
- Coverage matrix comparing Docling, pdfplumber and EID HTML render where available.
- Evidence artifact under `docs/reviews/`.

Validation commands:

- JSON schema validation for metrics artifacts.
- Metric consistency check: top-level counts equal body array lengths for sections/headings/tables/cells/pages.
- `git diff --check`.

Pass thresholds:

- PDF page coverage must be complete for every PDF-backed sample. Page count differences versus pdfplumber are not blind failures if classified as route representation differences, but any unexplained missing source page is a blocker.
- Major annual-report chapter heading coverage: `§1` through last disclosed annual-report section present or explicitly fail-closed with locator evidence; target 100%, pass floor 95% across samples.
- Table coverage versus pdfplumber is a screening metric, not standalone proof. Default watch band is `0.80x` to `1.30x`; any outside-band sample and any inside-band sample with large semantic differences must be classified by a closed `data_table`, `layout_table`, `continuation_fragment`, `merged_header`, `non_table_block` taxonomy before pass.
- Cell locator coverage: >= 95% table cells have page number and row/column offsets.
- Content hash presence: 100% per block/table/cell where represented.

Stop conditions:

- Section count semantics remain ambiguous after evidence; chapter-level versus all-node counts must be separated.
- Any sample misses a major report chapter without fail-closed classification.
- Any body arrays cannot be traced to source page/table/cell provenance.

### Gate C. EvidenceAnchor Mapping Evidence

Goal: prove Docling locators can map to current `EvidenceAnchor` without changing public schema and without treating candidate metadata as facts.

Inputs:

- Gate B full-document JSONs.
- Existing candidate internals for normalization, table groups and candidate note projection.
- Current `EvidenceAnchor` fields: `source_kind`, `document_year`, `section_id`, `page_number`, `table_id`, `row_locator`, `note`.

Allowed commands:

- `uv run pytest tests/fund/documents/test_docling_candidate_models.py tests/fund/documents/test_docling_normalization.py tests/fund/documents/test_docling_locators.py tests/fund/documents/test_docling_failure_mapping.py tests/fund/documents/test_docling_no_consumption_guards.py -q`
- `uv run python <approved_anchor_mapping_metrics_script> --inputs <manifest>`
- `python -m json.tool <anchor-mapping.json> > /dev/null`
- `git diff --check`

Forbidden commands:

- `EvidenceAnchor` schema change.
- `EvidenceSourceKind` public expansion.
- Extractor/renderer/audit/Service/UI/Host/quality-gate consumer integration.
- Field correctness claim.

Artifacts:

- Per-sample `candidate_anchor_mapping.json`.
- Locator collision report.
- Evidence artifact under `docs/reviews/`.

Validation commands:

- Candidate note JSON parse check.
- Anchor uniqueness check by `(document_year, section_id, page_number, table_id, row_locator, note.locator_hash)`.
- No-consumption guard tests.
- `git diff --check`.

Pass thresholds:

- 100% table cells used by field candidates have non-empty candidate anchor notes.
- >= 99% locator uniqueness across sample matrix; any collision must be deterministic and fail-closed.
- 100% mapped anchors preserve raw text and normalized text separately.
- 100% ambiguous whitespace-only numeric grouping cases either deterministically repair under closed rule names or fail closed.
- 0 public schema/source-kind changes.

Stop conditions:

- Mapping requires public `EvidenceAnchor` schema change to be useful.
- Locator notes cannot preserve bbox/page/row/column/source hash without lossy string parsing.
- Candidate locators are consumed outside Fund documents boundary.

### Gate D. Field Correctness Comparative Evidence

Goal: compare Docling-derived candidate field extraction against current pdfplumber baseline and EID HTML render candidate without promoting any route to source truth. Gate D has two layers:

- D1 identity and structural comparison: verifies same-report identity, locator presence, field-family coverage and route disagreements. This can run for all active samples after Gates 0-C.
- D2 true field correctness: compares values only against accepted same-report manual reviewed facts or golden references. D2 can run only for sample/field-family pairs produced by Gate 0D.

Route agreement is never truth. It can only prioritize manual review or classify disagreement.

Inputs:

- Gate C anchor mappings.
- Gate 0D accepted same-report reviewed/golden reference manifest, with explicit coverage by sample and field family.
- Closed field families: identity, source document, benchmark, manager, scale, fee, return, holdings, risk, bond top holdings, target fund holdings, QDII risk/exposure, manager holding.
- Gate 0C same-report pdfplumber representations for all active samples.
- Gate 0E EID HTML render candidate representations where accepted; samples without EID HTML render stay two-route only.

Allowed commands:

- `uv run python <approved_field_comparison_script> --sample-manifest <matrix> --routes docling,pdfplumber,eid_html_render --field-families <closed-list>`
- `uv run python <approved_reference_coverage_script> --reference-manifest <accepted_reference_facts.json>`
- `python -m json.tool <field-comparison.json> > /dev/null`
- `uv run pytest <approved fixture-only comparison tests> -q`
- `git diff --check`

Forbidden commands:

- Golden promotion.
- New manual reference creation inside Gate D; reference facts must already be accepted by Gate 0D.
- Readiness/release/PR.
- Direct analyze/checklist.
- Live provider/LLM.
- Any report-writing or CHAPTER_CONTRACT consumption from candidate fields.

Artifacts:

- `field_comparison_matrix.json`
- `reference_coverage_matrix.json`
- Per-sample mismatch and unavailable report.
- Manual-review queue for mismatches.
- Evidence artifact under `docs/reviews/`.

Validation commands:

- JSON schema validation.
- Same-fund/year filter check; cross-fund unavailable records must not count against same-fund correctness.
- Reference coverage validation: every D2 scored field must point to an accepted same-report reviewed/golden reference id.
- Mismatch classification check.
- `git diff --check`.

Pass thresholds:

- D1 identity fields: 100% exact match or fail-closed; any fund code/year/report type/source-document mismatch rejects baseline candidacy.
- D1 structural comparison: route disagreements are classified as `docling_only`, `pdfplumber_only`, `eid_html_only`, `multi_route_agreement`, `all_routes_missing`, or `manual_review_required`; none of these labels proves field correctness.
- D2 high-priority field correctness versus accepted reviewed/golden facts: >= 98% exact/normalized match, 0 critical mismatch, counted only over fields with accepted reference ids.
- D2 medium-priority field correctness: >= 95% exact/normalized match, mismatches classified by route and field family, counted only over fields with accepted reference ids.
- Reference coverage: baseline-candidate verdict requires D2 coverage for all high-priority field families for S1-S4 and identity/source-document references for S5-S6. If S5/S6 profile-specific field references are deferred, verdict cannot exceed hybrid or auxiliary unless controller accepts the reduced field-correctness scope.
- EvidenceAnchor presence for comparable accepted fields: 100%.
- EID HTML render comparison must remain candidate-only and record `page_number=null` where no PDF page anchor exists.

Stop conditions:

- Any critical identity mismatch.
- Any route projects a value without same-report locator.
- Any mismatch is hidden as unavailable.
- Any worker treats Docling as source truth because it agrees with pdfplumber or EID HTML.
- Any D2 field is scored without an accepted reference id.

### Gate E. Performance / Cache / Cost Evidence

Goal: prove Docling can run within acceptable local runtime, cache footprint and repeatability envelopes before baseline-candidate disposition.

Inputs:

- Gate A conversion logs.
- Gate B/C/D artifact sizes and metrics.
- Cache manifest for Docling models, PDF inputs, parsed outputs and representation JSONs.

Allowed commands:

- `du -sh cache/docling-artifacts reports/docling-baseline-qualification reports/representation-json`
- `uv run python <approved_performance_summary_script> --run-roots <paths>`
- `python -m json.tool <performance-summary.json> > /dev/null`
- `git diff --check`

Forbidden commands:

- Network/model downloads.
- Provider/LLM.
- Production cache migration.
- Runtime default changes.
- Readiness/release/PR.

Artifacts:

- `performance_cache_cost_summary.json`
- Per-sample cold/warm timing table.
- Cache invalidation and artifact retention recommendation.
- Evidence artifact under `docs/reviews/`.

Validation commands:

- Timing artifact schema validation.
- Hash repeatability check for repeated runs on at least S1 and one non-S1 sample.
- Cache root inventory check.
- `git diff --check`.

Pass thresholds:

- Performance thresholds are tentative until Gate A logs establish the current hardware/runtime baseline. Initial watch target is cold conversion p95 <= 120 seconds per annual report on the recorded CPU profile; Gate E evidence must either confirm this target or propose a controller-reviewed calibrated threshold from Gate A logs before disposition.
- Warm representation load p95 <= 5 seconds.
- Repeated run hash stability for normalized representation: 100% for repeated S1 and one additional sample.
- Candidate output size <= 15x input PDF size or controller-accepted justification.
- Cache manifest includes model version, artifact hashes, Docling version, conversion flags and schema version for 100% samples.

Stop conditions:

- Non-deterministic output without explained timestamp/hash exclusion.
- Cache cannot distinguish model version, Docling version or conversion flags.
- Runtime requires network or provider.

### Gate F. Baseline Disposition Controller Judgment

Goal: decide Docling disposition after Gate 0 and Gates A-E without implementing production behavior.

Inputs:

- Accepted Gate 0 prerequisite artifacts and reference coverage status.
- Accepted evidence artifacts from Gates A-E.
- Independent reviews for each material evidence artifact.
- Residual risk map.

Allowed commands:

- `git branch --show-current`
- `git status --short`
- `git diff --check`
- Read-only artifact validation commands already accepted by A-E.

Forbidden commands:

- Production implementation.
- Stage/commit/push/PR unless separately authorized by controller flow.
- Readiness/release.
- Any source policy, repository behavior or public schema change.

Artifacts:

- Controller judgment artifact under `docs/reviews/`.
- Verdict chosen from Section 10 only.
- Residual tracking table with owner and next gate.

Validation commands:

- `git diff --check`.
- Optional: `python -m json.tool` over machine-readable evidence indexes.

Pass thresholds:

- Gate 0 prerequisites accepted or explicitly scoped down with controller-owned residuals.
- All A-E gates accepted with no blocking findings.
- Every residual has owner and next gate.
- Verdict preserves `NOT_READY`.
- No blocked claim is converted into accepted fact.

Stop conditions:

- Any Gate 0 prerequisite remains unclassified for an active sample.
- Any A-E gate has unresolved blocker.
- Any evidence artifact lacks review or controller acceptance.
- Any proposed verdict implies production baseline or readiness.

## 7. Comparison Design

Comparison must separate representation quality from field correctness.

| Route | Current role | Strength to test | Weakness / boundary |
|---|---|---|---|
| Current pdfplumber baseline | Current production parser basis through repository internals; representation export is local no-live evidence, not a public schema. | Existing production path, page numbers, current extractor compatibility. | Weak section/document representation; not a full semantic document object. |
| Docling | PDF-derived candidate document representation. | Full section/table/cell/page/bbox representation, table structure, candidate EvidenceAnchor mapping. | Requires normalization, table continuation stitching, model/cache provenance and multi-sample proof. |
| EID XBRL HTML render candidate | EID official HTML render candidate source. | Official request provenance, navigation/HTML locators, same-report rendered facts. | No PDF page numbers, many layout tables, not raw XML/source truth/taxonomy proof. |

Comparison axes:

- document identity: fund code, fund name, report year, report type, source policy metadata;
- full-document coverage: pages, sections, heading tree, paragraphs, tables, cells;
- table quality: data table versus layout table classification, multi-level headers, cross-page continuation, merged cells, row/column locators;
- locator stability: page/bbox for PDF routes, URL/hash/navigation locators for EID HTML, collision rate, repeat-run stability;
- EvidenceAnchor projection: current schema compatibility, note payload parseability, raw/normalized text preservation;
- field correctness: only against accepted reviewed/golden facts and same-report manual evidence, not route agreement alone;
- performance/cache: runtime, artifact size, repeatability, cache invalidation keys.

Decision rule:

- Route agreement can prioritize manual review, but cannot prove field correctness.
- EID HTML render can strengthen source provenance, but cannot provide PDF page anchors.
- Docling can strengthen page/bbox/table representation, but cannot be source truth.
- Hybrid disposition is valid only if each route has an explicit role and no consumer bypasses self-owned extractors / EvidenceAnchor / fail-closed classification.

EID HTML render availability semantics:

- S1 currently has accepted EID HTML render JSON.
- S2-S6 have no accepted EID HTML render JSON in this plan.
- Gate 0E must classify each non-S1 sample before Gate D. If no EID HTML render is accepted, the sample remains eligible for Docling/pdfplumber two-route representation comparison, but not for tri-route claims.
- Missing EID HTML render for S2-S6 blocks source-provenance-heavy hybrid claims for those samples unless the controller explicitly accepts a reduced comparison scope.

Hybrid route combination semantics are deferred to a later hybrid routing design gate unless Gate F selects `DOCLING_ELIGIBLE_AS_HYBRID_PRIMARY_NOT_READY`. If that verdict is selected, the minimum allowed semantics are:

- Docling is the PDF-derived page/bbox/table representation primary.
- pdfplumber remains the current production baseline reference until a later implementation gate changes repository behavior.
- EID HTML render, when available, is an official rendered-source locator supplement, not fallback and not source truth.
- Conflict resolution is fail-closed: route disagreement opens manual review or extractor validation; no logical OR of route values can produce a field fact.
- All routing remains inside Fund documents / `FundDocumentRepository`; consumers still receive only extractor/projection/EvidenceAnchor-approved facts.

## 8. Failure Taxonomy

Docling qualification failures must be classified into closed categories:

| Category | Meaning | Baseline impact |
|---|---|---|
| `runtime_network_escape` | Conversion attempts network/model download under offline/socket-block mode. | Reject baseline candidacy. |
| `model_artifact_unproven` | Local model cache exists but provenance/version/hash acceptance missing. | Blocks production baseline; may allow candidate-only evidence. |
| `conversion_failure` | Docling cannot produce JSON for a sample. | Reject baseline candidate if unclassified or recurring; auxiliary only if isolated and fail-closed. |
| `identity_mismatch` | Output conflicts with fund code/year/report type/source identity. | Reject baseline candidacy. |
| `section_coverage_gap` | Major annual-report section missing or unmapped. | Blocks candidate unless explicitly not applicable and reviewed. |
| `table_structure_loss` | Critical table rows/headers/cells lost or unrecoverably split. | Blocks baseline for affected profile; may route hybrid/auxiliary. |
| `normalization_ambiguity` | Text/numeric repair cannot be deterministic. | Must fail closed; repeated ambiguity blocks field projection. |
| `locator_collision` | Multiple cells/blocks map to same locator without disambiguation. | Blocks EvidenceAnchor mapping gate. |
| `anchor_schema_pressure` | Useful mapping requires public `EvidenceAnchor` schema change. | Blocks this route; requires separate schema gate. |
| `field_mismatch_critical` | High-priority accepted field mismatches reviewed truth. | Reject baseline candidacy. |
| `field_unavailable_silent` | Missing fields are hidden or treated as success. | Reject baseline candidacy. |
| `performance_regression` | Runtime/cache exceeds accepted thresholds. | Blocks baseline; may remain auxiliary. |
| `boundary_violation` | Service/UI/Host/renderer/quality gate consumes candidate directly. | Reject gate result until fixed. |
| `source_policy_violation` | Non-EID fallback or source expansion appears. | Reject gate result. |
| `readiness_overclaim` | Evidence claims production/readiness beyond scope. | Reject artifact until corrected. |

## 9. Acceptance Threshold Summary

Docling cannot pass baseline-candidate disposition unless all of the following are true:

- Runtime containment: 100% offline/socket-blocked, 0 hidden downloads, explicit artifact hashes.
- Prerequisites: Gate 0 accepted sample artifacts, pdfplumber full exports and reference-fact coverage for the scored field families.
- Sample matrix: all six required fund/year profiles represented or replaced through controller-approved EID-only profile-preserving replacement.
- Coverage: >= 95% major-section coverage across samples; 100% source-page coverage for PDF-backed samples, with any route page-count difference classified.
- Locator quality: >= 99% locator uniqueness; 100% field-candidate anchors preserve raw and normalized text.
- Field correctness: 100% identity match; D2 true field correctness only over accepted reference facts; >= 98% high-priority field match, 0 critical mismatch.
- Performance/cache: Gate E calibrated cold p95 threshold accepted from Gate A logs, warm p95 <= 5 seconds, repeat normalized hash stability for repeated samples.
- Boundary: 0 public schema/source-kind/repository behavior changes, 0 direct consumer access, 0 non-EID fallback.
- Evidence discipline: every evidence artifact reviewed and accepted, every residual owned, release/readiness remains `NOT_READY`.

## 10. Verdict Criteria

### `VERDICT: DOCLING_ELIGIBLE_AS_BASELINE_CANDIDATE_NOT_READY`

Use only if:

- Gate 0 prerequisites are accepted for all active samples.
- Gates A-E all pass thresholds.
- Docling outperforms or matches pdfplumber on full-document coverage, table locators and EvidenceAnchor mapping across the six-sample matrix.
- D2 field correctness thresholds pass without critical mismatch over accepted high-priority reference facts, with no route-agreement-as-truth shortcut.
- Performance/cache thresholds are calibrated from Gate A logs and pass.
- Remaining residuals are implementation/provenance hardening, not correctness or boundary blockers.

Meaning: Docling may enter a future production-baseline implementation planning gate. It is still not production baseline and not ready.

### `VERDICT: DOCLING_ELIGIBLE_AS_HYBRID_PRIMARY_NOT_READY`

Use only if:

- Gate 0 prerequisites are accepted for all active samples, or any missing EID HTML render route is explicitly classified as reduced tri-route scope.
- Docling passes runtime, coverage, anchor and performance gates.
- Docling is strongest for PDF page/bbox/table representation, but EID HTML render is required for official rendered-source locators or specific table families.
- Field correctness passes only where accepted reference facts exist; route roles are combined only by explicit priority and fail-closed rules from Section 7.
- Hybrid routing can remain wholly inside Fund documents / `FundDocumentRepository` boundaries.

Meaning: Docling may be the primary PDF-derived representation in a future hybrid design, but not sole baseline and not ready.

### `VERDICT: DOCLING_REMAINS_AUXILIARY_CANDIDATE_NOT_READY`

Use if:

- Docling is useful for some table/locator/document representation work, but misses one or more baseline thresholds.
- Exactly 1 isolated, profile-specific, fully classified fail-closed Gate A conversion failure occurs.
- S2-S6 reference facts or EID HTML render availability remain insufficient for baseline/hybrid verdict, but Docling representation still provides bounded diagnostic value.
- Failures are bounded and do not require rejection.
- Current pdfplumber and/or EID HTML render remain necessary primary routes.

Meaning: Docling can support diagnostics, fixtures or auxiliary extraction pilots, but cannot enter production-baseline planning.

### `VERDICT: DOCLING_REJECTED_AS_BASELINE_CANDIDATE_NOT_READY`

Use if any of these occur:

- Runtime containment/network escape failure.
- Unclassified conversion failure or 2+ conversion failures.
- Identity mismatch.
- Critical field mismatch.
- Repeated major-section/table loss.
- Unresolved locator collision or anchor schema pressure.
- Boundary/source-policy violation.
- Performance/cache infeasible without unapproved runtime changes.
- Evidence overclaims source truth/readiness/production baseline.

Meaning: Docling must not be treated as baseline candidate. It may only re-enter through a new controller-approved research/evidence gate.

## 11. Recommended First Next Gate After Plan Acceptance

Recommended next gate:

```text
Docling Baseline Qualification Acquisition Status Planning Gate
```

Purpose:

- define exact EID-only sample acquisition status for S1-S6;
- classify which samples already have acceptable local artifacts and which need separately authorized EID-only acquisition;
- classify missing pdfplumber full representation exports and reference-fact coverage as blockers before Gate A/B/D;
- preserve no-live/no-conversion boundaries until the controller explicitly authorizes evidence execution.

This next gate should be planning-only. It should not run Docling conversion or live/network commands unless a later controller explicitly opens a bounded evidence execution gate.

Required dependency chain after this plan:

1. `Docling Baseline Qualification Acquisition Status Planning Gate`: classify S1 existing artifacts, S2-S6 local EID-controlled PDF status, required replacements, pdfplumber export status, EID HTML render availability and reference-fact coverage.
2. `Bounded EID-only Sample Acquisition Execution Gate`, only if status planning finds missing local artifacts and the controller/user authorizes bounded live/EID work.
3. `Pdfplumber Full Representation Export Planning/Execution Gate`, if S2-S6 pdfplumber JSONs are missing; this must stay repository-internal and no-readiness.
4. `Same-report Manual Reviewed Reference Facts / Golden Reference Acquisition Gate`, before Gate D D2 scoring for non-S1 field families.
5. `Docling/pdfplumber Runner Planning Gate`, if approved conversion/export runners are not already accepted.
6. Gate A runtime containment evidence.
7. Gate B full-document coverage evidence.
8. Gate C EvidenceAnchor mapping evidence.
9. Gate D identity/structural comparison plus true field correctness over accepted references only.
10. Gate E performance/cache/cost evidence with calibrated thresholds.
11. Gate F baseline disposition controller judgment.

## 12. Residuals And Deferred Gates

| Residual | Owner | Deferred gate |
|---|---|---|
| Docling model artifact provenance is benchmark-only. | Controller / model artifact owner | Docling Model Artifact Provenance Acceptance Gate. |
| S2-S6 EID-controlled local PDF artifact status is unclassified in this plan. | Controller / acquisition owner | Acquisition Status Planning Gate and bounded EID-only acquisition execution if needed. |
| S2-S6 pdfplumber full representation exports are not currently accepted. | Fund documents / parser owner | Pdfplumber Full Representation Export Planning/Execution Gate. |
| S2-S6 reviewed/golden field references are not currently accepted. | Fund extractor/projection owner | Same-report Manual Reviewed Reference Facts / Golden Reference Acquisition Gate. |
| Candidate `EvidenceAnchor` metadata is currently packed in note fields. | Fund documents / EvidenceAnchor owner | Candidate Source-kind / EvidenceAnchor Schema Decision Gate, only if public schema pressure remains after mapping evidence. |
| EID HTML render is candidate only and has no page numbers. | Fund documents / EID HTML owner | Hybrid Locator Semantics Planning Gate. |
| Field correctness remains unproven for Docling across samples. | Fund extractor/projection owner | Docling Field Correctness Comparative Evidence Gate. |
| Production repository integration is not planned here. | Fund documents owner | Production Repository Integration Planning Gate after baseline disposition. |
| CHAPTER_CONTRACT / renderer / quality-gate consumption is not authorized. | Fund/Service owners | Extractor Projection And Consumer Integration Gate after field correctness acceptance. |
| Release/readiness remains `NOT_READY`. | Release owner / controller | Separate release-readiness gates only after implementation, review and accepted evidence. |

## 13. Completion Report Format For Future Workers

Future evidence or implementation workers must report:

```text
Artifact path:
Gate:
Role:
Changed files:
Validation:
Verdict:
Residuals:
Forbidden commands not run:
Self-check: pass | blocked - <reason>
```

They must stop if assigned scope is insufficient, if a blocked claim would be required to proceed, or if any command would cross live/network/provider/readiness/release/PR boundaries without explicit controller/user authorization.
