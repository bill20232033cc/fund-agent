# MVP multi-year annual analysis productization plan

## Worker Self-Check

- Current gate / role: `multi-year annual analysis productization planning gate`; this artifact is a planning deliverable only.
- Source of truth: `AGENTS.md`, `docs/design.md`, `docs/current-startup-packet.md`, `docs/implementation-control.md`, `docs/reviews/mvp-multi-year-annual-evidence-scope-design-20260603.md`, and `docs/reviews/mvp-multi-year-annual-evidence-scope-controller-judgment-20260603.md`.
- Scope boundary: write this plan artifact under `docs/reviews/`; do not modify source, tests, runtime behavior, README, `docs/design.md`, or control truth in this planning artifact.
- Stop conditions: stop before implementation if a slice needs live EID/network/PDF/FDR/provider/LLM/analyze/checklist/golden/readiness/release commands, source expansion, fallback redesign, public chapter-id change, or Service direct repository/cache/PDF access.
- Evidence and validation: plan must be handoff-ready, code-generation-ready, and reviewable by MiMo/DS; validation for this planning gate is static artifact review plus `git diff --check`.

## Goal

Productize the 2021-2025 annual-report analysis workflow as a formal capability.

The current user workflow is manual:

1. run the existing single-year analysis for 2021;
2. repeat for 2022, 2023, 2024, and 2025;
3. manually merge five outputs into a cross-year annual analysis.

The product goal is a single typed product path that can analyze one fund over the bounded annual-report period 2021-2025, preserve year-level evidence/provenance/gaps, and provide typed cross-year facts for report generation and audit. The implementation must not become a shell wrapper around five CLI runs.

## Current Facts

- Current CLI product surface has `fund-analysis analyze <fund_code> --report-year <year>` and `fund-analysis checklist <fund_code> --report-year <year>`.
- Current `FundAnalysisRequest` contains one `report_year`; current `FundAnalysisService._run_analysis_core()` calls one extractor invocation for that year.
- Current `FundDataExtractor.extract(fund_code, report_year, force_refresh=...)` loads exactly one annual report through `FundDocumentRepository.load_annual_report()`, then returns one `StructuredFundDataBundle`.
- Current `StructuredFundDataBundle`, `ChapterFactProjection`, `ReportEvidenceBundle`, and `EvidenceAvailability` are single-year shaped.
- Current chapter ids remain public `0-7`; Chapter 5 currently represents missing cross-period facts through `cross_period_comparison_missing`.
- Current annual-report source policy is EID single-source operational mode with public Source Provenance v2 fields `selected_source=eid`, `source_mode=single_source_only`, and `fallback_enabled=false`.

## Accepted Design Inputs

The accepted future design from the multi-year annual evidence scope gate is binding for this productization plan:

- annual evidence scope is `target_year` plus up to four immediately preceding annual reports, capped at `max_years=5`;
- the 2021-2025 use case maps to `target_year=2025` and optional prior years `2024, 2023, 2022, 2021`;
- Service may declare the annual evidence scope through explicit typed request fields, but Service must not call `FundDocumentRepository`, source helpers, PDF cache, parsers, or filesystem paths;
- Fund/Agent domain capability owns annual evidence loading, and every annual report must be loaded through `FundDocumentRepository.load_annual_report(fund_code, year, force_refresh=...)`;
- target-year failure is fail-closed for the product run;
- optional prior-year `not_found` / `unavailable` becomes year-level gap/degradation;
- optional prior-year `schema_drift` / `identity_mismatch` / `integrity_error` fails closed for that year's evidence and blocks dependent cross-year claims, without killing the current-year report unless that prior year is explicitly required by a later contract;
- future annual evidence bundle must be additive, preserving the current-year `StructuredFundDataBundle` and avoiding a parallel truth source;
- cross-year derived facts must carry `source_years` and `source_year_anchor_ids`;
- raw five-year PDF text or raw parsed text must never enter LLM prompts;
- quarterly/interim/prospectus/fund contract, new source strategy, public chapter-id expansion, provider budget/default changes, score-loop, fixture projection, golden/readiness, and release/readiness are outside this gate.

## Non-Goals

- Do not add Eastmoney, fund-company/CDN, CNINFO, fallback expansion, or alternate source strategy.
- Do not change EID single-source provenance policy.
- Do not run live EID/network/PDF/FDR/provider/LLM commands in implementation verification unless a separate controlled live evidence gate authorizes it.
- Do not change public chapter ids `0-7`, split Chapter 2 publicly, or create a public multi-year chapter taxonomy.
- Do not pass raw PDF text, raw parsed full-year text, or five annual reports directly into LLM context.
- Do not change provider/runtime budgets, provider defaults, retry semantics, quality gate semantics, final judgment semantics, score-loop, golden/readiness, release state, PR state, or cleanup/ignore rules.
- Do not use `extra_payload` for explicit business parameters.

## Product Contract Decisions

Implementation should add an explicit typed product request rather than overloading the existing single-year `FundAnalysisRequest` with ambiguous optional fields.

Recommended Service-owned request:

```python
@dataclass(frozen=True, slots=True)
class MultiYearAnnualAnalysisRequest:
    fund_code: str
    target_year: int = 2025
    prior_years: tuple[int, ...] = (2024, 2023, 2022, 2021)
    max_years: int = 5
    force_refresh: bool = False
    degradation_policy: Literal["current_year_required_prior_years_optional"] = (
        "current_year_required_prior_years_optional"
    )
```

Validation requirements:

- `fund_code` follows the same normalization and validation as current single-year analysis.
- `target_year` must be positive and is the only required current annual report in this MVP.
- `max_years` is a hard cap in `1..5`.
- canonical year order is target year first, then prior years descending.
- prior years must be strictly less than `target_year`.
- for this productization gate, prior years must be immediately preceding years after canonicalization; the user-facing 2021-2025 path is therefore `target_year=2025, prior_years=(2024, 2023, 2022, 2021)`.
- duplicate years, future years relative to target, or more than four prior years fail at request construction.
- `force_refresh` applies uniformly to every requested year; per-year refresh remains deferred.
- no explicit parameter may be hidden in `extra_payload`.

Service-to-Fund mapping:

- Service owns `MultiYearAnnualAnalysisRequest` and must not pass it directly into Fund modules if that would create a Service import dependency from Fund.
- Service must translate the product request into a Fund-owned `AnnualEvidenceScopeRequest` or equivalent type in `fund_agent/fund/annual_evidence.py`.
- MVP mapping is fixed: `required_years=(target_year,)`, `optional_years=prior_years`, `max_years=max_years`, `force_refresh=force_refresh`, and `degradation_policy="current_year_required_prior_years_optional"`.
- For the 2021-2025 product path, `target_year=2025` is the only required year and `2024, 2023, 2022, 2021` are optional prior years. Future required-prior-year behavior is deferred and must not be inferred silently.
- The Fund-owned scope type must repeat the accepted design checks for required/optional disjointness, `max_years` cap, optional-year truncation, and canonical target-then-descending-prior order, so invalid scopes cannot bypass Service validation in tests.

## Implementation Slices

### Slice 1: Service Contract and Validation

Allowed modules:

- `fund_agent/services/fund_analysis_service.py`
- `fund_agent/services/__init__.py`
- `tests/services/test_fund_analysis_service.py`

Implementation:

- add `MultiYearAnnualAnalysisRequest`;
- add a Service method stub with real validation and no document loading, for example `FundAnalysisService.analyze_multi_year_annual(request)`;
- return a typed blocked/not-implemented result only if later slices are not implemented in the same gate; the final accepted productization gate should return a real product result;
- reuse current request validation primitives where practical, but keep the contract explicit and independent from `FundAnalysisRequest.report_year`;
- prove Service still does not import or call `FundDocumentRepository`, cache helpers, source adapters, PDF helpers, or filesystem document paths.

Tests:

- valid 2021-2025 request normalizes to `(2025, 2024, 2023, 2022, 2021)`;
- invalid `max_years`, duplicate years, non-prior years, non-immediate prior years, missing target year, and more than five total years fail;
- `force_refresh` is preserved as a uniform policy;
- no `extra_payload` exists on the request/result contract.

### Slice 2: Fund-Layer Annual Evidence Loader

Allowed modules:

- new Fund-layer module, recommended `fund_agent/fund/annual_evidence.py`;
- `fund_agent/fund/__init__.py` only if export is needed;
- `tests/fund/test_annual_evidence.py`.

Implementation:

- introduce a Fund-owned scope object equivalent to accepted `AnnualEvidenceScopeRequest`; do not reuse the Service request type inside Fund modules;
- expose one translation entry from Service to Fund scope, with `required_years=(target_year,)` and all `prior_years` mapped to `optional_years`;
- load each requested annual report sequentially through `FundDocumentRepository.load_annual_report(fund_code, year, force_refresh=...)`;
- build year-level records with `year`, availability status, parsed report when available, public source provenance, source failure category, document identity status, and gaps;
- preserve EID single-source provenance and do not add new source or fallback behavior;
- classify target-year failure as run-blocking;
- classify optional prior-year `not_found` / `unavailable` as degradable year gaps;
- classify optional prior-year `schema_drift` / `identity_mismatch` / `integrity_error` as fail-closed for that year and as a blocker for dependent cross-year claims;
- keep concurrency deferred.

Tests:

- repository is called once per canonical year with the same `fund_code` and uniform `force_refresh`;
- target-year failure blocks;
- optional prior-year `not_found` and `unavailable` produce gaps;
- optional prior-year fail-closed categories isolate the year and block dependent facts;
- same-source `fund_id` mismatch, when metadata is present across years, becomes affected-year `identity_mismatch`;
- no direct PDF/cache/source helper is called outside the injected repository protocol.
- Service-to-Fund translation preserves required/optional separation and cannot be bypassed by directly passing the Service request into Fund code.

### Slice 3: Yearly Structured Evidence Bundle

Allowed modules:

- `fund_agent/fund/annual_evidence.py`;
- narrowly scoped helpers in `fund_agent/fund/data_extractor.py` only if needed to reuse existing parser-to-structured-field logic without duplicate parsing;
- `tests/fund/test_annual_evidence.py` and existing extractor tests if public behavior changes.

Implementation:

- build an additive `AnnualEvidenceBundle` with a pinned MVP field set;
- preserve the current-year `StructuredFundDataBundle` as canonical for existing single-year calculations and rendering;
- include year-indexed structured bundles or narrower annual summaries for prior years;
- include year-indexed source provenance, anchors, `ReportDataGap`-compatible gaps, and availability records;
- do not treat `AnnualEvidenceBundle` as a replacement truth source for current-year `StructuredFundDataBundle`;
- do not call `FundDataExtractor.extract()` for optional prior years, because that full façade currently loads NAV and bond drawdown side data for the requested year;
- optional prior-year extraction should call existing extractor functions against the already loaded `ParsedAnnualReport`, or use a new narrow helper that explicitly skips NAV/drawdown and quality gate work;
- avoid repeated NAV/drawdown work for prior years unless a later reviewed gate accepts multi-year NAV/drawdown evidence.

Required MVP fields for `AnnualEvidenceBundle`:

- `schema_version`;
- `fund_code`;
- `target_year`;
- `canonical_years`;
- `current_year_bundle`;
- `year_records`, keyed or ordered by year;
- `available_years`;
- `gap_years`;
- `fail_closed_years`;
- `source_provenance_by_year`;
- `source_documents_by_year` or safe document identity records;
- `anchors_by_year`;
- `data_gaps`;
- `requirement_availability`;
- `cross_year_facts`;
- `degradation_summary`;
- `fallback_summary`.

Tests:

- current-year bundle is retained exactly and remains the canonical input to existing single-year calculations;
- prior-year unavailable or fail-closed records do not remove current-year structured data;
- bundle-level summaries list available years, gap years, fail-closed years, and source provenance by year;
- no raw parsed full-report text is stored in the bundle fields intended for writer/LLM consumption.
- optional prior-year processing proves it did not call `FundDataExtractor.extract()` or trigger NAV/drawdown loading.

### Slice 4: Cross-Year Derived Facts for Chapter 5

Allowed modules:

- `fund_agent/fund/annual_evidence.py`;
- `fund_agent/fund/chapter_facts.py` only for additive projection extension;
- `fund_agent/fund/evidence_availability.py` only for additive requirement availability;
- `tests/fund/test_annual_evidence.py`;
- targeted `tests/fund/test_chapter_facts.py` / `tests/fund/test_evidence_availability.py` if those test files exist or are the local convention.

Implementation:

- compute a minimal set of low-risk cross-year facts for Chapter 5 from already extracted structured fields;
- start with fields that already have current extractor surfaces, such as fee schedule, turnover rate, share change, holdings concentration, and manager continuity, only where anchors are available across the required source years;
- every cross-year fact must include `source_years`, `source_year_anchor_ids`, dependency requirements, and fallback/fail-closed caveats;
- facts without source-year anchors are not eligible for writer/auditor consumption;
- if all prior years are unavailable, preserve current-year report availability and keep Chapter 5 in degraded cross-period-unavailable mode;
- derive coarse `1Y/3Y/5Y` summaries only from `requirement_availability`, never as independent truth.

Chapter fact extension contract:

- keep `ChapterFactProvider.project(bundle: StructuredFundDataBundle, ...)` unchanged for all current single-year callers;
- add a new explicit method, recommended `ChapterFactProvider.project_annual_evidence(bundle: AnnualEvidenceBundle, *, chapter_ids=DEFAULT_CHAPTER_FACT_IDS) -> ChapterFactProjection`, plus a module-level function with equivalent behavior if local style requires it;
- return the existing `chapter_fact_projection.v1` shape unless implementation review proves a schema bump is required;
- represent cross-year facts as `ChapterFactEntry` records in chapter id `5`, with `value` containing the structured cross-year payload including `source_years`, `source_year_anchor_ids`, dependency requirements, and caveats;
- use stable `source_field_id` values under an `annual_evidence.cross_year.*` namespace for these facts;
- map `source_year_anchor_ids` into ordinary `evidence_anchor_ids` after creating chapter evidence anchors for the referenced year-level anchors;
- when eligible cross-year facts exist, supplement or replace the current synthetic `synthetic.cross_period_comparison` missing fact so Chapter 5 no longer carries `cross_period_comparison_missing` for satisfied requirements;
- when eligibility is not satisfied, preserve the current `cross_period_comparison_missing` degradation behavior and add year-level gaps rather than over-claiming.

Requirement availability contract:

- any Chapter 5 requirement ids introduced by this implementation must be explicit typed ids in `evidence_availability.py` and tests;
- coarse `1Y/3Y/5Y` status may only be derived from those requirement-level records;
- if no typed requirement id exists for a cross-year fact type, that fact type remains internal and must not drive writer/auditor claims.

Tests:

- available five-year evidence produces cross-year facts with exact source years and anchor ids;
- partial prior years produce only claims whose requirements are satisfied;
- missing/unavailable prior years create gaps and no unsupported trend claims;
- fail-closed prior years block dependent facts;
- Chapter 5 no longer has to fake cross-period comparison when typed cross-year facts are available, and still degrades when they are not.
- the existing `ChapterFactProvider.project()` remains backward compatible for single-year callers;
- `project_annual_evidence()` produces only chapter id `5` cross-year additions and does not create public chapter ids outside `0-7`;
- coarse `1Y/3Y/5Y` summaries are absent or derived from explicit requirement availability, never asserted independently.

### Slice 5: Service Product Result and CLI Surface

Allowed modules:

- `fund_agent/services/fund_analysis_service.py`;
- `fund_agent/services/__init__.py`;
- `fund_agent/ui/cli.py`;
- `tests/services/test_fund_analysis_service.py`;
- `tests/ui/test_cli.py`.

Implementation:

- add a formal product path for multi-year annual analysis instead of telling users to run five single-year commands manually;
- implement the CLI as `fund-analysis analyze-annual-period <fund_code> --target-year 2025 --start-year 2021`;
- document in the option help that `--start-year` is the earliest optional prior annual-report year and that `--target-year` is the required current annual-report year;
- reject ranges that are not exactly target year plus immediately preceding prior years under `max_years=5`;
- result should be a typed `MultiYearAnnualAnalysisResult` that includes the current-year report output plus a bounded cross-year evidence/product summary for downstream report generation;
- CLI must display year availability, gap/fail-closed years, and source provenance summary without exposing raw PDF text or secrets;
- deterministic single-year `analyze/checklist` behavior must remain unchanged unless the user explicitly invokes the new multi-year product path.

Tests:

- CLI creates the typed request with `target_year=2025` and prior years `2024..2021`;
- invalid `--start-year` / `--target-year` combinations fail with code 2;
- CLI help text distinguishes required `--target-year` from optional prior-year range implied by `--start-year`;
- single-year `analyze` and `checklist` existing tests continue to pass;
- no `--use-llm` behavior changes are introduced in this gate unless explicitly planned and reviewed as a later slice.

### Slice 6: Audit, Reporting, and Documentation

Allowed modules:

- `fund_agent/fund/report_evidence.py`;
- `fund_agent/fund/report_quality_validation.py`;
- `fund_agent/fund/report_writing_audit.py`;
- README files only as triggered by actual source changes;
- relevant tests under `tests/fund/`, `tests/services/`, and `tests/ui/`.

Implementation:

- add audit checks that block unsupported cross-year claims when required source years or anchors are missing;
- add explicit Chapter 5 degradation wording rules: when cross-year facts are unavailable or partially available, generated/reportable text must state which years are available, which years are gaps or fail-closed, and what minimum follow-up question remains; it must not assert trend, stability, or change without the typed cross-year fact and source-year anchors;
- expose year availability and gaps in structured output so user-visible report text can say which years were used;
- preserve existing final judgment and quality gate semantics unless a later gate explicitly changes them;
- update README only for current implemented behavior after code exists:
  - root `README.md` for user command if CLI changes;
  - `fund_agent/README.md` if Service/Fund boundary changes are user-visible to developers;
  - `fund_agent/fund/README.md` if Fund annual evidence capability is added;
  - `tests/README.md` if test workflow changes.

Tests:

- report/audit blocks trend language when cross-year evidence is unavailable;
- report/audit accepts gap wording or next-minimum-validation wording;
- source provenance summary is present for every used annual report year;
- no new release/readiness or golden promotion claim is made.

## Verification Matrix

Planning gate verification:

- `git diff --check`
- MiMo independent plan review
- DS independent plan review
- controller final judgment

Future implementation gate verification:

- targeted unit tests for new Service request validation and CLI request projection;
- targeted Fund-layer tests with fake repository, not live EID/PDF;
- targeted Chapter 5 / evidence availability / audit tests for supported, partial, missing, and fail-closed year scenarios;
- existing single-year Service and CLI tests to prove no regression;
- `uv run pytest` with the agreed targeted matrix first, then broader deterministic tests if runtime budget allows;
- `git diff --check`;
- no live/network/provider/PDF/FDR/analyze/checklist/golden/readiness/release commands unless a separate reviewed evidence gate authorizes them.

## Review Questions

Reviewers should focus on these risks:

- Does the plan accidentally let Service cross the repository/cache/PDF/source boundary?
- Does the plan preserve current single-year behavior and source provenance policy?
- Is the 2021-2025 product path explicit enough to avoid five manual CLI runs plus merge?
- Are target-year and optional prior-year failure semantics precise enough for implementation?
- Does the plan avoid raw five-year text injection and unsupported cross-year claims?
- Are implementation slices small enough for review and accepted local checkpoints?

## Next Entry

If this plan is accepted after MiMo/DS review and controller judgment, the next mainline entry should be:

`multi-year annual analysis productization implementation gate`

Deferred entries:

- controlled live EID evidence for multi-year corpus availability;
- LLM/report writer integration beyond bounded typed facts;
- fallback/source expansion design;
- multi-year NAV/drawdown evidence;
- golden/readiness/release gates;
- control-doc/design-doc sync after accepted implementation evidence.
