# MVP multi-year annual evidence scope design — AgentMiMo independent design review

## Reviewer Self-Check

- Role: independent design review worker, not controller.
- Gate: `MVP multi-year annual evidence scope design gate`.
- Classification: `heavy`.
- Review target: `docs/reviews/mvp-multi-year-annual-evidence-scope-design-20260603.md`.
- Source of truth: `AGENTS.md`, `docs/design.md`, `docs/implementation-control.md`, `docs/current-startup-packet.md`, `docs/fund-analysis-template-draft.md`, prior controller judgments, and local code.
- Actions intentionally not taken: no code edit, no commit, no push, no PR, no implementation, no template truth replacement, no provider budget change, no score-loop wiring.

## Findings

### F1 — `AnnualEvidenceScopeRequest` uses untyped `fund_code` instead of `DocumentKey` pattern

**Severity**: minor
**Location**: §2 Service Scope Declaration, proposed `AnnualEvidenceScopeRequest` fields

Current codebase uses `DocumentKey(fund_code=..., year=..., document_kind="annual_report")` as the typed identity for annual reports (`fund_agent/fund/documents/models.py:353-404`). `FundDocumentRepository.load_annual_report()` validates and normalizes `fund_code` and `year` through `_validate_fund_code()` / `_validate_year()`. The proposed `AnnualEvidenceScopeRequest` uses raw `str` for `fund_code` and raw `int` for `target_year` / `required_years` / `optional_years`, which is consistent with `FundDataExtractor.extract()` public API but loses the typed-document identity discipline that `DocumentKey` provides.

**Recommendation**: Implementation should decide whether to reuse `DocumentKey` for per-year identity or define a narrower `AnnualReportIdentity` type. Not a blocker for design acceptance, but the implementation slice should specify which typed identity is canonical for year-level availability records.

### F2 — Cross-year `ChapterFactProvider` contract not specified

**Severity**: moderate
**Location**: §4 Future Typed Evidence Bundle Shape, §7 Template And Agent Feed

The design proposes `AnnualEvidenceBundle` as an additive wrapper over `StructuredFundDataBundle` plus year-indexed evidence. Current `ChapterFactProvider.project()` consumes exactly one `StructuredFundDataBundle` and produces `ChapterFactProjection` for chapters 0-7. Chapter 5 currently receives a synthetic `cross_period_comparison_missing` fact (`chapter_facts.py:1188-1199`). The design says Chapter 5 "may use `cross_year_facts` only when `EvidenceAvailability` shows enough typed annual evidence," but does not specify:

- Whether `ChapterFactProvider.project()` would accept `AnnualEvidenceBundle` directly or whether a new `MultiYearChapterFactProvider` would be introduced.
- How the current single-year `ChapterFactProjection` shape would be extended to carry cross-year facts for Chapter 5 without changing public chapter ids.
- Whether the Chapter 5 synthetic `cross_period_comparison_missing` fact would be replaced by a more precise year-level gap fact, or supplemented by typed cross-year facts when available.

**Recommendation**: The implementation slice plan (slice 6 "Cross-year facts slice" and slice 7 "Writer/auditor slice") should define the `ChapterFactProvider` / `ChapterFactProjection` extension contract before implementation. This is not a blocker for design acceptance but is a material gap for implementation readiness.

### F3 — Chapter 2 multi-year R=A+B-C table data source unspecified

**Severity**: minor
**Location**: §7 Template And Agent Feed, `docs/fund-analysis-template-draft.md` Chapter 2

The template Chapter 2 (`docs/fund-analysis-template-draft.md:396-408`) requires a 5-year breakdown table (`年度 | 净值增长率 R | 基准收益率 B | 超额收益 A | 判断`). Current `StructuredFundDataBundle` provides single-year `nav_benchmark_performance`. The design's §7 says "Chapter 2 can use annual performance/cost breakdown inside public chapter id `2`; this does not authorize a public Ch2 split." However, it does not specify whether:

- The multi-year performance table would be populated from per-year `StructuredFundDataBundle.nav_benchmark_performance` via `AnnualEvidenceBundle.years`.
- Missing prior-year performance data would degrade the table to fewer rows or mark years as unavailable.
- The existing `r_abc.py` `calculate_r_abc_series()` would be reused or replaced.

**Recommendation**: Implementation slice 6 should specify the data path from per-year bundles to Chapter 2's multi-year table, including degradation semantics when prior-year performance is unavailable.

### F4 — `AnnualEvidenceBundle` vs `ReportEvidenceBundle` relationship undefined

**Severity**: minor
**Location**: §4 Future Typed Evidence Bundle Shape, residual risk #3

The design acknowledges in residual risk #3 that `AnnualEvidenceBundle` could duplicate `ReportEvidenceBundle` and `ChapterFactProjection` if implemented as a parallel truth source. Current `ReportEvidenceBundle` (`report_evidence.py:611-653`) is projected from one `StructuredFundDataBundle` and records one `report_year`, `source_documents`, `facts`, `evidence_anchors`, `data_gaps`. The design proposes `AnnualEvidenceBundle` with `current_year: StructuredFundDataBundle`, `years: Mapping[int, AnnualYearEvidence]`, `source_documents`, `anchors`, `data_gaps`, `availability`, `cross_year_facts`, and `degradation`.

The design says "The safer implementation slice should make it an additive wrapper over current-year bundle plus year summaries, with one canonical source for fact/anchor ids." This is the right direction but does not define which id namespace is canonical or how anchor deduplication would work across the current-year `ReportEvidenceBundle` and the multi-year `AnnualEvidenceBundle`.

**Recommendation**: Implementation should establish a single canonical anchor id namespace (likely the existing `chapter-anchor:...` pattern from `chapter_facts.py`) and define how year-level anchors map into it. This should be specified in implementation slice 4 ("Bundle/projection slice").

### F5 — Requirement-sensitive availability needs concrete examples

**Severity**: minor
**Location**: §6 EvidenceAvailability Integration

The design correctly states that availability is requirement-sensitive: "For example, fee trend may be available across more years than holdings-style trend if holdings extraction failed or was not reviewed for a prior year." This is the right semantic. However, the proposed `EvidenceAvailability` type has `data_tier_availability: Mapping[Literal["1Y", "3Y", "5Y"], AvailabilityStatus]` which implies coarse-grained tiers, while the text describes fine-grained per-requirement availability. The interaction between coarse `1Y/3Y/5Y` flags and fine-grained `year_availability: Mapping[int, AnnualYearAvailability]` is not specified.

**Recommendation**: Implementation should clarify whether `data_tier_availability` is a convenience summary derived from `year_availability` and per-requirement fact availability, or whether it is independently asserted. The safer design is to derive it, not assert it independently.

### F6 — Year ordering for `prior_years` is unspecified

**Severity**: minor
**Location**: §1 Annual Evidence Scope

The design says `prior_years` should be "up to four immediately preceding annual report years, in descending or ascending deterministic order to be specified by implementation." This defers a potentially consequential decision: cross-year derived facts (e.g., fee trend, turnover trend) would produce different anchor id orderings depending on sort order. While this is explicitly deferred, it should be pinned before the cross-year facts slice (slice 6) to avoid non-deterministic behavior.

**Recommendation**: Implementation slice 2 ("Fund annual loader slice") should specify descending order (most recent first) as the default, consistent with the template's existing pattern of listing recent years first in performance tables.

### F7 — Multi-year repository concurrency not addressed

**Severity**: minor
**Location**: §3 Fund Loading Boundary

The design says the loader should call `FundDocumentRepository.load_annual_report(fund_code, year)` once per requested year. Current `FundDocumentRepository` is async (`async def load_annual_report`). Loading 5 years sequentially would multiply latency by 5x. The design does not address whether:

- The loader should use `asyncio.gather()` or similar for concurrent year loading.
- The repository's internal cache and PDF adapter support concurrent access safely.
- Provider timeout budgets should account for multi-year loading latency.

**Recommendation**: Implementation slice 2 should specify concurrent loading semantics. The repository cache (`AnnualReportDocumentCache`) and PDF adapter (`AnnualReportPdfAdapter`) should be verified for concurrent safety before implementation.

### F8 — `AnnualEvidenceScopeRequest.force_refresh` semantics across years

**Severity**: minor
**Location**: §2 Service Scope Declaration

The design proposes `force_refresh: bool` as a single flag forwarded across all years. This means `force_refresh=True` would re-download all 5 years of PDFs, which is expensive. The current `FundDocumentRepository.load_annual_report()` supports per-year `force_refresh`. The design does not specify whether:

- `force_refresh` should apply uniformly to all years or only to the target year.
- Prior years should use cache by default even when target year forces refresh.

**Recommendation**: Implementation should consider per-year `force_refresh` control or at minimum document the expected behavior when `force_refresh=True` with 5 years of annual reports.

## Non-Findings (Verified Correct)

1. **FundDocumentRepository boundary**: Correctly specified. All annual report access through `FundDocumentRepository.load_annual_report()`. Service/UI/Host/renderer/quality gate must not call PDF cache, download helpers, or concrete sources. Matches current code architecture.

2. **Fallback taxonomy**: Correctly preserved. `not_found`/`unavailable` allow degradation; `schema_drift`/`identity_mismatch`/`integrity_error` fail closed. Matches `models.py:15-21` `AnnualReportSourceFailureCategory` and `AGENTS.md` fallback rules.

3. **Same-fund identity**: Correctly requires same `fund_code` and repository/source identity match, fails closed on ambiguity. Matches `DocumentKey` identity model.

4. **No raw 5-year PDF/text to LLM**: Correctly and repeatedly rejected throughout the design. Matches `AGENTS.md` and prior gate rejections.

5. **Chapter ids remain 0-7**: Correctly preserved. Chapter 5 receives cross-year evidence inside chapter id 5, not by adding new chapters. Matches template typed contract redesign gate acceptance.

6. **Quarterly reports correctly deferred**: Explicitly rejected in scope. Matches prior gate scope guardrails.

7. **Provider budget / score-loop correctly deferred**: Explicitly rejected. Matches prior gate dispositions.

8. **Ch2 split correctly deferred**: Not authorized by this gate. Matches template typed contract redesign gate rejection.

9. **Current facts section accuracy**: All 8 current fact statements verified against code. `StructuredFundDataBundle` is indeed single-year. `ChapterFactProvider.project()` indeed consumes single-year bundle. Chapter 5 indeed has synthetic `cross_period_comparison_missing` fact.

10. **Boundary mapping table accuracy**: Correctly assigns responsibilities per layer. Service declares scope, Fund loads through repository, Agent consumes typed inputs, Host stays lifecycle-only, renderer/quality gate consume typed outputs only.

## Verdict

**PASS with non-blocking findings.**

The design is correct, bounded, and implementation-ready in its core architecture. It correctly preserves the `FundDocumentRepository` boundary, fallback taxonomy, same-fund identity, chapter id boundary, and raw PDF rejection. The proposed future types (`AnnualEvidenceBundle`, `AnnualYearEvidence`, `EvidenceAvailability`, `CrossYearDerivedFact`) are properly labeled as future design and have reasonable semantics.

F2 (cross-year `ChapterFactProvider` contract) is the most material gap for implementation readiness and should be addressed in the implementation planning slices before slice 6/7 are implemented. F1, F3-F8 are minor specification gaps that implementation slices can resolve.

The design does not cross scope: it does not implement code, does not change provider budget, does not wire score-loop, does not modify template truth, and does not authorize quarterly/prospectus/fund-contract evidence scope.

## Validation

- `rg -n "FundDocumentRepository|AnnualEvidenceScopeRequest|AnnualEvidenceBundle|schema_drift|identity_mismatch|integrity_error|chapter ids remain|0-7|raw five-year PDF|quarterly|score-loop" docs/reviews/mvp-multi-year-annual-evidence-scope-design-20260603.md` — pass. All required boundary concepts present.
- Code cross-reference: `fund_agent/fund/documents/repository.py` — `FundDocumentRepository.load_annual_report()` confirmed as single-year async entry point.
- Code cross-reference: `fund_agent/fund/documents/models.py` — `AnnualReportSourceFailureCategory` five-category taxonomy confirmed.
- Code cross-reference: `fund_agent/fund/data_extractor.py` — `FundDataExtractor.extract()` confirmed as single-year single-repository-call.
- Code cross-reference: `fund_agent/fund/chapter_facts.py:1188-1199` — Chapter 5 synthetic `cross_period_comparison_missing` fact confirmed.
- Code cross-reference: `fund_agent/fund/report_evidence.py:611-653` — `ReportEvidenceBundle` confirmed as single-year.

## Secret Safety

This review contains no API key, Authorization header, Bearer token, cookie, password, raw provider response, raw audit response, prompt body, writer draft body, repair draft body, hidden provider config value, raw PDF text, or raw parsed annual-report text.
