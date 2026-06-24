# Evidence Confirm Productionization Program Plan

## Verdict

`PLAN_READY_FOR_REVIEW_NOT_READY`

## Scope

- Work unit: `Evidence Confirm Productionization Program`
- Branch: `evidence-confirm-productionization`
- Gate classification: `heavy`
- Role: planning worker only
- Artifact: `docs/reviews/evidence-confirm-productionization-program-plan-20260622.md`
- Current control entry: `Await User Decision After Evidence Confirm Scoring V2 Closeout`
- Current PR evidence: PR-39 remains draft/open at remote head `dc586516e9f122670dc97a8c62474c9303fb6621`, merge state `CLEAN`, CI `test` SUCCESS.

This plan does not implement source code, run live/network/PDF/provider/LLM commands, mutate PR-39, mark ready, merge, push, commit, change release/readiness, or edit production files.

## Goal, Motivation, Success Signals

Goal: turn current no-live Evidence Confirm V2 from a Fund-layer helper into a reviewed production program that can eventually:

1. Build same-source annual-report excerpt references through `FundDocumentRepository` only.
2. Run deterministic Evidence Confirm over report/chapter facts with hard-gate semantics.
3. Add bounded semantic entailment for qualitative claims without letting LLM/provider output override deterministic source/proof failures.
4. Integrate results into Service, UI, renderer, and quality gate through explicit contracts.
5. Produce release/readiness evidence without claiming readiness before the evidence chain proves it.

Motivation: current V2 proves auditability scoring mechanics, but the closeout explicitly leaves full live source/PDF Evidence Confirm, semantic entailment, report-level adoption, renderer/quality-gate consumption, and release/readiness as residuals. A single implementation jump would mix source access, semantic judgment, public contracts, user-visible behavior, and release claims. These risks need ordered gates.

Success signals:

- Live reference construction is repository-bounded: no Service/UI/Host/renderer/quality gate direct PDF/cache/source/helper/parser calls.
- Existing no-live V1/V2 public behavior remains unchanged until an explicit production gate changes it.
- Candidate-only, `not_proven`, dangling-anchor, missing-reference, source-kind mismatch, wrong-year, and value mismatch paths remain fail-closed.
- Semantic entailment has a typed deterministic boundary, fake-client tests, and provider-live evidence only in an explicitly authorized later gate.
- Quality gate can consume Evidence Confirm summaries without reading documents and without hiding source failures.
- UI reports status and artifact paths only; it does not run evidence logic or inspect parser artifacts.
- Readiness/release remains `NOT_READY` until matrix, live evidence, provider evidence, docs, CI, and residual disposition are all accepted.

## Non-goals

- No source fallback behavior change.
- No `EvidenceSourceKind` or public `EvidenceAnchor` expansion unless a later gate proves it is necessary.
- No Docling/pdfplumber/EID HTML render direct consumption by Service, UI, Host, renderer, quality gate, LLM prompt, or templates.
- No parser replacement, full field correctness, golden promotion, or readiness claim in source/PDF or semantic gates.
- No default-on LLM/provider behavior before explicit provider and release gates.
- No PR-39 external-state mutation in this program plan.
- No Host durable session/resume/memory/outbox or Agent full tool-loop expansion.

## First-principles Judgment

Evidence Confirm answers a narrower question than extraction correctness: for a rendered or projected fact, can the cited anchor be rechecked against same-source material, and does the cited material support the fact value or assertion? That decomposes into four independent proof layers:

- Source access proof: can the same report be loaded through the accepted repository path?
- Locator proof: can an anchor locate a bounded excerpt in the same parsed annual report?
- Value/proof-boundary proof: does V2 confirm source support, missing evidence, proof boundary, and value match?
- Semantic support proof: for qualitative assertions, does a bounded semantic checker say the excerpt entails the assertion?

The first implementation gate should not start with live execution or Service defaults. It should first add a Fund-layer no-live reference materialization contract with fake `ParsedAnnualReport` input and tests. That gives later live, Service, quality-gate, and UI gates a stable primitive without weakening current no-live semantics.

## Direct Code Evidence

- Current Evidence Confirm module states it only consumes caller-provided `ChapterFactProjection` / references and does not read repository, PDF/cache/source helper, Service, Host, provider, network, filesystem, or dayu runtime: `fund_agent/fund/evidence_confirm.py:1`.
- Current proof source kinds are a closed set: `annual_report`, `reviewed_note`, `derived`; reference-kind/source-kind pairs are closed and deterministic: `fund_agent/fund/evidence_confirm.py:56`.
- `EvidenceConfirmReference.source_truth_status` currently defaults to `"proven"`, while V2 proof predicate rejects `candidate_only` and any non-`proven` reference: `fund_agent/fund/evidence_confirm.py:78`, `fund_agent/fund/evidence_confirm.py:1004`, `fund_agent/fund/evidence_confirm.py:1606`.
- V2 result has schema `evidence_confirm.v2`, fact-level results, issues, checked rules, hard gate, overall status, and auditability score: `fund_agent/fund/evidence_confirm.py:250`.
- V1/V2 public entrypoints require explicit references from the caller: `fund_agent/fund/evidence_confirm.py:277`, `fund_agent/fund/evidence_confirm.py:364`, `fund_agent/fund/evidence_confirm.py:408`.
- `FundDocumentRepository.load_annual_report()` is the current annual-report loading boundary and returns parsed report without exposing local PDF path upward: `fund_agent/fund/documents/repository.py:295`, `fund_agent/fund/documents/repository.py:318`.
- Repository cache reuse is already guarded by current EID single-source metadata: `fund_agent/fund/documents/repository.py:268`.
- `ParsedAnnualReport` exposes `raw_text`, `sections`, `tables`, and `metadata`; `get_section_text()` only slices `raw_text` by `ReportSection.start_offset/end_offset`: `fund_agent/fund/documents/models.py:738`, `fund_agent/fund/documents/models.py:820`.
- `ReportSection` exposes `section_id`, `title`, `start_offset`, `end_offset`, `matched_rule`, and `confidence`; it has no page or paragraph structure: `fund_agent/fund/documents/models.py:609`.
- `ParsedTable` exposes only `page_number`, `table_index`, `headers`, and bare tuple `rows`; it has no `table_id` and no row-level metadata: `fund_agent/fund/documents/models.py:676`.
- `ChapterEvidenceAnchor` has optional `table_id` and `row_locator` strings, but no format contract in the dataclass itself: `fund_agent/fund/chapter_facts.py:98`.
- Several current extractors build table anchor IDs with the local helper convention `page-{page_number}-table-{table_index}`; this is implementation evidence for a compatibility parser, not a `ParsedTable` field: `fund_agent/fund/extractors/profile.py:585`, `fund_agent/fund/extractors/holdings_share_change.py:406`, `fund_agent/fund/extractors/performance.py:990`.
- Quality gate currently only consumes `score.json` and explicitly does not read PDF/cache/fund documents or execute LLM audit: `fund_agent/fund/quality_gate.py:1`.
- The single-fund quality-gate adapter consumes already extracted `StructuredFundDataBundle`; it does not re-extract documents or move quality rules to Service/UI: `fund_agent/fund/quality_gate_integration.py:1`, `fund_agent/fund/quality_gate_integration.py:48`.
- Service already has `FundAnalysisDeveloperOverrides`, and product mode rejects developer overrides; this is the EC-P6 opt-in placement that preserves product defaults: `fund_agent/services/fund_analysis_service.py:190`, `fund_agent/services/fund_analysis_service.py:227`, `fund_agent/services/fund_analysis_service.py:1427`.
- Service `_run_analysis_core()` extracts once, then runs quality gate over the bundle before P2 analysis and final judgment: `fund_agent/services/fund_analysis_service.py:1089`, `fund_agent/services/fund_analysis_service.py:1111`, `fund_agent/services/fund_analysis_service.py:1116`.
- PR-39 final closeout preserves boundaries: no live source/PDF integration, no Service/UI/Host/renderer/quality-gate consumption, no parser replacement, no source-kind/anchor expansion, no provider/LLM command, and release/readiness remains unproven: `docs/reviews/evidence-confirm-scoring-v2-final-closeout-20260622.md:76`.

## Architecture Boundary Alignment

UI -> Service -> Host -> Agent remains the governing boundary.

- UI: parses explicit user flags, prints status/artifact paths, and exits with documented codes. It must not inspect PDF/cache/parser output, call `FundDocumentRepository`, call Evidence Confirm internals directly, or construct provider clients.
- Service: owns use-case policy and explicit request fields. It can request Evidence Confirm through Fund-layer public facades, pass policy to quality-gate integration, and project safe results to UI/renderer. It must not read PDF/cache/source helpers or Docling/pdfplumber/EID candidate artifacts.
- Host: remains business-opaque. For future provider-backed semantic entailment, Host may govern lifecycle only if the Service-owned provider route explicitly uses it. It must not own fund evidence semantics.
- Agent/Fund: owns document repository usage, reference materialization, deterministic Evidence Confirm, semantic checker protocol, quality gate issue projection, renderer-safe summaries, and fail-closed evidence semantics.

## Program Gate Order

1. `EC-P1A ParsedAnnualReport Locator-contract No-live Materializer Gate`
2. `EC-P2 Repository-bounded Live Source/PDF Evidence Gate`
3. `EC-P3 Deterministic Evidence Confirm Production Facade Gate`
4. `EC-P4 Semantic Entailment Contract and Fake-provider Gate`
5. `EC-P5 Controlled Semantic Provider Evidence Gate`
6. `EC-P6 Service Integration Opt-in Gate`
7. `EC-P7 Renderer and UI Surfacing Gate`
8. `EC-P8 Quality Gate Consumption Gate`
9. `EC-P9 Production Default Decision Gate`
10. `EC-P10 Release/readiness Evidence Matrix Gate`
11. `EC-P11 PR/release External-state Gate`

Each implementation gate must go through plan review, implementation, code review, fix/re-review, aggregate deepreview, accepted local commit, draft PR pass, and final closeout unless the controller narrows it.

## Work Units

### EC-P1A ParsedAnnualReport Locator-contract No-live Materializer Gate

Objective: add a no-live Fund-layer primitive that converts current `ParsedAnnualReport` fields plus `ChapterFactProjection` anchors into explicit `EvidenceConfirmReference` objects without inventing unavailable locator structure. This is the first implementation work unit and is detailed below.

Expected outcome:

- A new Fund-layer module provides deterministic reference materialization from current `ParsedAnnualReport` fields only: `sections`, `raw_text`, `get_section_text(section_id)`, `tables`, `ParsedTable.page_number`, `ParsedTable.table_index`, `ParsedTable.headers`, and `ParsedTable.rows`.
- No repository call is required in EC-P1 tests; fake parsed reports are used.
- The primitive never exposes PDF path, cache path, source URL, raw Docling/pdfplumber/EID HTML JSON, or source helper details.
- The primitive produces only existing reference/source kinds: `annual_report_excerpt` and `annual_report` for materialized annual-report references. It does not expand `EvidenceSourceKind`, public `EvidenceAnchor`, or existing V1/V2 schemas.
- It returns explicit fail-closed gaps for unsupported, ambiguous, or unlocatable anchors instead of inventing references or falling back across locator types.

Allowed files/modules:

- New `fund_agent/fund/evidence_confirm_sources.py` for materializer contract and implementation.
- `fund_agent/fund/evidence_confirm.py` only for imports/types if strictly necessary; no V1/V2 behavior change.
- `tests/fund/test_evidence_confirm_sources.py`.
- `fund_agent/fund/README.md` only if public Fund package documentation needs current-state sync.
- `tests/README.md` for the new no-live test surface.
- Review/evidence artifacts under `docs/reviews/`.

Exact allowed changes:

- Add typed request, result, and issue dataclasses:
  - `EvidenceConfirmReferenceBuildRequest(fund_code, report_year, projection, parsed_report, source_truth_status="not_proven", max_section_excerpt_chars=1200)`
  - `EvidenceConfirmReferenceBuildResult(references, issues, status)`
  - `EvidenceConfirmReferenceBuildIssue(issue_id, severity, anchor_id, reason, message)`
- Add `build_annual_report_evidence_confirm_references(request)`.
- Add module-level constants:
  - `SUPPORTED_TABLE_ID_RE = r"^page-(?P<page_number>[1-9][0-9]*)-table-(?P<table_index>0|[1-9][0-9]*)$"`
  - `SUPPORTED_ROW_LOCATOR_RE = r"^row-(?P<row_index>0|[1-9][0-9]*)$"`
  - `DEFAULT_MAX_SECTION_EXCERPT_CHARS = 1200`
- Anchor admission:
  - match only anchors whose `source_kind == "annual_report"`;
  - require `anchor.document_year in {None, request.report_year}` and fail issue on contradictory year;
  - require `anchor.section_id` to exist in `request.parsed_report.sections` for every annual-report reference;
  - skip `external_api`, `derived`, and `unknown` anchors with explicit not-applicable issue.
- Table locator contract:
  - `ParsedTable` has no `table_id`; EC-P1A therefore accepts only the compatibility `ChapterEvidenceAnchor.table_id` format `page-{page_number}-table-{table_index}`;
  - any other non-empty `anchor.table_id` fails closed with `unsupported_table_id_format`;
  - compatible `table_id` parses to `page_number` and `table_index`, then must match exactly one `ParsedTable` with those fields;
  - if `anchor.page_number` is present, it must equal the parsed table id page; page mismatch fails closed;
  - duplicate table candidates, missing table candidates, or table candidates that do not match page/index fail closed;
  - no arbitrary table title, section-table inference, substring lookup, or parser artifact lookup is allowed in EC-P1A.
- Row locator contract:
  - EC-P1A accepts only `anchor.row_locator` format `row-{zero_based_index}`, where `row-0` means `ParsedTable.rows[0]`;
  - all other non-empty row locator strings fail closed with `unsupported_row_locator_format`;
  - row index out of range fails closed with `row_locator_out_of_range`;
  - table row matching never infers by header text, first-column text, cell substring, note, or value content in EC-P1A.
- Section excerpt contract:
  - no paragraph-level fallback and no page-to-text slicing are allowed because `ReportSection` has no paragraph or page structure;
  - when no table/row locator is present, build a section reference from `parsed_report.get_section_text(anchor.section_id)`;
  - section excerpt is normalized whitespace and bounded to `request.max_section_excerpt_chars` from the current section offsets only;
  - empty, whitespace-only, invalid-offset, or missing section text fails closed with `empty_section_excerpt`;
  - `anchor.page_number` may help validate/select table references only; it must not be used to slice `raw_text`.
- Locator invariants:
  - never use a different section/year/page/table/row to close an anchor;
  - unsupported table or row locators do not fall back to section text;
  - richer table IDs, row labels, table titles, merged-cell reconstruction, section-table ownership, and paragraph/page text windows are deferred to a later documents-model/live evidence gate.
- Reference construction:
  - `anchor_id` equals current `ChapterEvidenceAnchor.anchor_id`;
  - `reference_kind="annual_report_excerpt"`;
  - `source_kind="annual_report"`;
  - `document_year=request.report_year`;
  - `section_id` copies the admitted anchor section;
  - table reference `page_number`, `table_id`, and `row_locator` copy the admitted compatible locator;
  - section reference keeps `table_id=None` and `row_locator=None`;
  - table row `excerpt_text` is built deterministically from `ParsedTable.headers` and the selected bare tuple row, padding/truncating header pairing without raising if row width differs from header width;
  - section `excerpt_text` is bounded and normalized but not summarized.
- Source truth admission:
  - request default is `source_truth_status="not_proven"` so materialized references cannot become proof-positive by omission;
  - if `request.source_truth_status != "proven"`, the materializer must return an explicit issue and no `proven` reference;
  - if EC-P1A does not implement a current metadata/source admission predicate, it must require explicit caller proof and still fail closed when the metadata predicate is unavailable or negative;
  - if EC-P1A implements the metadata predicate, `proven` may be copied only when both the request asks for `proven` and `parsed_report.metadata` satisfies the current source-provenance/admission checks;
  - candidate-only, missing metadata, negative metadata admission, or unavailable predicate cannot silently set `proven`.
- Invariants:
  - no `FundDocumentRepository` instantiation in EC-P1A;
  - no PDF path reads;
  - no filesystem reads;
  - no network;
  - no Docling/pdfplumber/EID candidate direct inputs;
  - no `EvidenceSourceKind` expansion;
  - no existing V1/V2 result shape change.

Required no-live tests:

- Builds a table-row reference for a fake parsed report with `table_id="page-3-table-0"` and `row_locator="row-0"`.
- Builds a section-only reference with `get_section_text(section_id)` and fixed max-char bounding when no table/row locator is present.
- Empty `sections` yields blocking/explicit issues for section-anchored annual-report facts.
- Empty `tables` yields blocking/explicit issues for compatible table-row anchors.
- Unsupported `table_id` formats yield `unsupported_table_id_format` and no fallback reference.
- Unsupported `row_locator` formats yield `unsupported_row_locator_format` and no inferred substring match.
- Out-of-range `row-N` yields `row_locator_out_of_range`.
- Empty or whitespace-only section text yields `empty_section_excerpt`.
- Header/row width mismatch renders a deterministic bounded table excerpt without exception.
- Produces no reference and a blocking/explicit issue for wrong report year.
- Does not create reference for `external_api`, `derived`, or `unknown` anchors.
- Does not accept candidate, missing metadata, negative metadata admission, unavailable metadata predicate, or request-level `not_proven` as proof-positive.
- Piping produced references into `confirm_projection_evidence_v2()` yields pass on same-source value and fail on value mismatch.
- Import isolation: test proves module import does not instantiate repository, touch network, or require PDF/cache.

Validation commands for EC-P1A:

- `uv run pytest tests/fund/test_evidence_confirm.py tests/fund/test_evidence_confirm_sources.py -q`
- `uv run ruff check fund_agent/fund/evidence_confirm.py fund_agent/fund/evidence_confirm_sources.py tests/fund/test_evidence_confirm.py tests/fund/test_evidence_confirm_sources.py`
- `git diff --check -- fund_agent/fund/evidence_confirm.py fund_agent/fund/evidence_confirm_sources.py tests/fund/test_evidence_confirm_sources.py fund_agent/fund/README.md tests/README.md`

Stop conditions:

- Any need to read real PDF/cache/network.
- Any need to expand `EvidenceSourceKind` or public `EvidenceAnchor`.
- Any inability to locate references without using raw parser artifacts outside Fund documents models.
- Any production behavior change in Service/UI/renderer/quality gate.

### EC-P2 Repository-bounded Live Source/PDF Evidence Gate

Objective: prove the reference materializer can be driven through `FundDocumentRepository.load_annual_report()` on explicitly authorized live samples.

Allowed changes:

- Add a Fund-layer runner/facade that accepts an injected repository or default repository and calls only `FundDocumentRepository.load_annual_report()`.
- Add fake-repository tests first.
- Live commands require separate user authorization and a reviewed execution artifact.

Required evidence:

- One controlled positive sample first, then multi-sample only after positive path is accepted.
- Source provenance must show current EID single-source policy and no fallback.
- Failure branches must classify `not_found`, `unavailable`, `schema_drift`, `identity_mismatch`, `integrity_error`; no fallback behavior change.

Stop condition: any live failure classification ambiguity routes to a source/failure-class gate, not a silent fallback.

### EC-P3 Deterministic Evidence Confirm Production Facade Gate

Objective: compose `project_chapter_facts()`, reference materialization, and `confirm_projection_evidence_v2()` into a Fund-layer production facade.

Design:

- Add `run_deterministic_evidence_confirm(...)` in Fund layer.
- Input is explicit bundle/projection plus repository-owned parsed-report reference result.
- Output is a stable summary object that can be consumed by Service and quality gate without full excerpts unless a debug/evidence artifact explicitly stores them.
- V2 remains the deterministic hard gate; V1 remains compatibility only.

Tests:

- Pass, warn, fail, and not-applicable summaries.
- No references means E3 fail, not pass.
- Candidate-only and not-proven cannot pass.

### EC-P4 Semantic Entailment Contract and Fake-provider Gate

Objective: add semantic entailment without provider/live dependency.

Design:

- Deterministic V2 remains the source/proof/value gate.
- Add a separate semantic result layer, not a mutation of V2:
  - `semantic_status`: `entailed / contradicted / insufficient / not_applicable`
  - `semantic_severity`: `block / warn / info`
  - `claim_text`, bounded excerpt ids, and reason code.
- Define `EvidenceEntailmentClient` Protocol in `fund_agent/fund/evidence_confirm_semantic.py`.
- Service constructs real provider only in later explicit provider gate; Fund accepts only Protocol client.
- Fund must not import Service, provider SDKs, API-key configuration, network clients, or Host runtime to run semantic checks.
- LLM semantic entailment cannot override:
  - missing evidence;
  - candidate-only or not-proven proof;
  - source-kind/year/locator mismatch;
  - deterministic numeric value mismatch.
- LLM can only classify semantic support for qualitative claims after source_support/missing_evidence/proof_boundary pass.

Tests:

- Fake client `entailed` passes only when deterministic proof dimensions pass.
- Fake client `contradicted` blocks.
- Fake client malformed output fails closed.
- Numeric deterministic mismatch remains block even if fake semantic client says `entailed`.
- Import isolation proves Fund semantic module imports without Service/provider/network dependencies.

### EC-P5 Controlled Semantic Provider Evidence Gate

Objective: prove provider-backed semantic entailment under explicit authorization.

Constraints:

- No default-on provider behavior.
- No API key in artifacts, repr, or errors.
- Bounded prompt and response schema.
- Provider timeout/retry budget explicit; no `extra_payload`.
- Live/provider command only in reviewed evidence gate.

Evidence:

- Fake-provider non-live suite pass.
- Provider request schema static validation.
- One controlled live semantic sample only after user authorization.

### EC-P6 Service Integration Opt-in Gate

Objective: integrate deterministic Evidence Confirm into `FundAnalysisService` as explicit opt-in policy while preserving current defaults.

Public contract changes:

- Add a flat opt-in field to `FundAnalysisDeveloperOverrides`: `evidence_confirm_policy: Literal["off", "warn", "block"] | None = None`.
- Do not add a product-mode top-level `FundAnalysisRequest` field in EC-P6. Product mode remains default-off because `FundAnalysisRequest(mode="product")` rejects developer overrides.
- Resolve the effective Service policy as `off` when `developer_overrides is None` or `developer_overrides.evidence_confirm_policy in {None, "off"}`.
- Add explicit Service result field `evidence_confirm_result: EvidenceConfirmSummary | None` on the analysis result type used by `_run_analysis_core()`.
- Product default remains `off` in this gate to preserve current behavior.
- A later EC-P9 default-decision gate may promote this to a top-level `FundAnalysisRequest` field only after accepted source/PDF, Service/UI, renderer, and quality-gate evidence.

Service behavior:

- It must call a Fund-layer facade, not repository/source helpers directly.
- It must not duplicate source extraction if a Fund-layer facade can reuse current report/bundle path; if reuse is not available, the facade may load via `FundDocumentRepository` inside Fund layer only.
- `block` policy raises a structured Service exception only after accepted tests.
- LLM path inherits the same Service policy and fail-closed behavior.

Tests:

- Default request unchanged: no Evidence Confirm result and existing analyze/checklist tests pass.
- Product-mode request with no developer overrides resolves policy `off` and does not call the Evidence Confirm facade.
- Developer override `evidence_confirm_policy="warn"` returns summary and does not block.
- Developer override `evidence_confirm_policy="block"` raises structured exception on deterministic fail.
- Product mode with developer override still raises the existing product-mode validation error.
- Multi-year request behavior remains unchanged unless the gate explicitly adds a matching developer override path and tests it.
- Service tests use fake Fund-layer Evidence Confirm runner; no PDF/network.

### EC-P7 Renderer and UI Surfacing Gate

Objective: make Evidence Confirm visible without making renderer/UI own evidence logic.

Renderer:

- Accept only a summary/status object from Service or render input.
- Add report metadata/appendix lines such as `evidence_confirm_status`, `checked_fact_count`, `failed_fact_count`, `auditability_score`.
- Do not render raw excerpts by default.
- Do not call Evidence Confirm, repository, parser, or provider.

UI:

- Add explicit CLI flags only after Service contract is accepted.
- Print stderr summary and artifact paths.
- Exit code follows Service structured exception:
  - deterministic analysis failure: existing code `1`;
  - quality/evidence gate block: planned code must be documented and tested; prefer code `2` only if aligned with existing quality gate semantics.

Tests:

- CLI default output unchanged.
- CLI opt-in warn prints summary and exits 0.
- CLI opt-in block exits structured non-zero with no report body.

### EC-P8 Quality Gate Consumption Gate

Objective: let quality gate consume Evidence Confirm status without reading documents.

Design:

- Extend `run_quality_gate_for_bundle()` with an optional `evidence_confirm_summary: EvidenceConfirmSummary | None = None` parameter.
- Do not mutate `score.json` schema in this first quality-gate consumption gate.
- The integration adapter evaluates FQ7 from the optional summary after the existing extraction-score run and writes the merged `quality_gate.json` / `quality_gate.md` outputs through the quality-gate result path; `extraction_score.py` and `score.json` remain Evidence-Confirm-unaware in EC-P8.
- `run_quality_gate()` remains a pure score-file evaluator for FQ0-FQ6 and must not read documents, repository, parser artifacts, provider clients, or Service state.
- Accept provisional rule code `FQ7` in this gate:
  - `block` when deterministic Evidence Confirm status is fail under policy block;
  - `warn` when status is warn or semantic insufficient under policy warn;
  - `info` when not configured/off.
- Quality gate does not call repository, Evidence Confirm, parser, provider, or Service.

Tests:

- Missing optional `evidence_confirm_summary` remains backward-compatible.
- Summary status `fail` under policy `block` maps to FQ7 block.
- `warn` maps to warn.
- `not_applicable/off` maps to info or no issue per accepted policy.
- `score.json` generated by `write_extraction_score_records()` is byte-for-byte schema-compatible aside from unrelated timestamp/path values.
- Existing FQ0-FQ6 behavior unchanged.

### EC-P9 Production Default Decision Gate

Objective: decide if/when Evidence Confirm becomes default-on for product paths.

Inputs required before this gate:

- EC-P1 through EC-P8 accepted.
- Controlled live source/PDF evidence accepted for the agreed sample matrix.
- Semantic provider gate accepted if semantic is included in default.
- Quality-gate integration evidence accepted.
- CLI/renderer documentation accepted.

Decision options:

- Keep default `off` and expose opt-in only.
- Set deterministic Evidence Confirm default to `warn`.
- Set deterministic Evidence Confirm default to `block`.
- Keep semantic entailment opt-in until separate calibration evidence.

No default flip is allowed without this gate.

### EC-P10 Release/readiness Evidence Matrix Gate

Objective: evaluate release/readiness without conflating implementation pass with readiness.

Required matrix:

- Static contract: schemas, request/result fields, public docs.
- No-live deterministic: Evidence Confirm V1/V2/source materializer/facade/unit tests.
- No-live semantic: fake-client and malformed-output tests.
- Service/UI/renderer/quality gate: opt-in and default behavior tests.
- Live source/PDF: controlled repository-bounded samples and failure classification evidence.
- Provider semantic: only if semantic is in release scope.
- CI: full test command, ruff, diff check.
- Artifact cleanliness: only accepted artifacts count.
- PR state: PR-39 and any new PR surfaces explicitly tracked; no mark-ready/merge unless authorized.

Verdict remains `NOT_READY` unless every required row is accepted and residuals are classified.

### EC-P11 PR/release External-state Gate

Objective: perform external state changes only if the user explicitly authorizes them.

Potential actions:

- mark relevant PR ready;
- merge;
- push bookkeeping commits;
- publish release/readiness statement.

This gate is outside implementation planning and cannot be inferred from local pass evidence.

## Affected Files and Modules

Likely production modules:

- `fund_agent/fund/evidence_confirm.py`
- `fund_agent/fund/evidence_confirm_sources.py`
- `fund_agent/fund/chapter_facts.py` only if projection summary needs additive helper, not schema replacement
- `fund_agent/fund/quality_gate.py`
- `fund_agent/fund/quality_gate_integration.py`
- `fund_agent/services/fund_analysis_service.py`
- `fund_agent/ui/cli.py`
- `fund_agent/fund/template/renderer.py`
- `fund_agent/fund/template/annual_period_renderer.py` only if annual-period summary is explicitly in scope

Likely tests:

- `tests/fund/test_evidence_confirm.py`
- `tests/fund/test_evidence_confirm_sources.py`
- `tests/fund/test_quality_gate.py`
- `tests/fund/test_quality_gate_integration.py`
- `tests/services/test_fund_analysis_service.py` or current Service test module
- `tests/ui/test_cli.py`
- `tests/fund/template/test_renderer.py`

Docs:

- `docs/design.md` after implementation gates only, with current/future/candidate status labels.
- `docs/implementation-control.md` and `docs/current-startup-packet.md` only via controller sync gates.
- `fund_agent/fund/README.md`, `fund_agent/README.md`, root `README.md`, `tests/README.md` as triggered by actual code changes.

## Public Contract and Schema Implications

- V1 and V2 result shapes are preserved unless a later schema gate explicitly creates `evidence_confirm.v3` or semantic companion schema.
- EC-P1A/EC-P3 may add additive internal Fund-layer request/result schemas.
- EC-P6 adds a flat developer-override field and an additive Service result field first; product-mode top-level request policy is deferred to EC-P9.
- EC-P8 adds the optional `evidence_confirm_summary` parameter at `quality_gate_integration.run_quality_gate_for_bundle()` and accepts provisional FQ7 behavior without mutating `score.json` in that gate.
- No `EvidenceSourceKind` / public `EvidenceAnchor` expansion in this program plan.
- No fallback/source behavior change.

## Validation Policy

No-live gates may run:

- targeted pytest;
- ruff;
- `git diff --check`;
- static `rg` / file inspection.

Live/network/PDF/provider/LLM gates may run only after explicit reviewed authorization and must write evidence artifacts. They cannot be run in this planning gate.

Full readiness gate must run the then-current project acceptance matrix, including full tests and CI evidence. Passing targeted tests is not readiness.

## Residual Owners

| Residual | Owner | Destination |
|---|---|---|
| Reference materialization over actual parsed annual report locators may expose missing locator fields beyond `page-{page}-table-{table_index}` and `row-N` | Fund documents / Evidence Confirm owner | EC-P2 or a separate documents-model locator gate |
| Live repository/PDF behavior unproven for Evidence Confirm | Fund documents / evidence owner | EC-P2 |
| Semantic entailment calibration unproven | Evidence Confirm semantic owner | EC-P4/EC-P5 |
| Service/UI/renderer quality-gate adoption changes user-visible behavior | Service/UI/renderer/quality-gate owners | EC-P6/EC-P7/EC-P8 |
| Default-on policy may increase block rate | Controller / product owner | EC-P9 |
| Release/readiness remains unproven | Release owner | EC-P10 |
| PR-39 external state remains draft/open | User / controller | EC-P11 or separate user-authorized PR gate |
| Existing unrelated untracked residue remains outside this work unit | Artifact owners / controller | Separate artifact-disposition gate if requested |

## Why This Is Not Overdesigned

The program separates risks that fail for different reasons and need different evidence:

- Source/PDF access is a repository and failure-class problem.
- Deterministic V2 is a proof-boundary and value-matching problem.
- Semantic entailment is a bounded provider/protocol problem.
- Service/UI/renderer/quality gate integration is a public contract and user-visible behavior problem.
- Release/readiness is an evidence-chain and external-state problem.

Combining these would force implementation workers to invent source ownership, public schema, LLM authority, UI behavior, and readiness criteria in one pass. The first implementation slice is intentionally small: a no-live Fund-layer reference materializer constrained to current `ParsedAnnualReport` fields and explicit fail-closed locator rules, while preserving current V2 semantics.

## Blocking Questions

No blocking question prevents plan re-review.

Remaining residual decisions are intentionally deferred to later gates:

- Which initial live sample matrix is authorized for EC-P2.
- Whether semantic entailment is required for release scope or remains opt-in after deterministic productionization.
- Whether EC-P9 promotes the developer-override policy to a product-mode top-level request field and changes the default from `off`.

## Completion Report Format

Planning worker completion report:

- artifact path;
- concise summary;
- blocking questions;
- exact recommended next gate.

## Recommended Next Gate

`Evidence Confirm Productionization Program Plan Re-review Gate`

The plan re-review should use `planreview`, verify that all seven accepted findings are closed, and confirm EC-P1A is code-generation-ready against current `ParsedAnnualReport`, `ReportSection`, and `ParsedTable` fields.
