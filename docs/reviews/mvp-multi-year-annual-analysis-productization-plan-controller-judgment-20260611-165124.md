# MVP multi-year annual analysis productization plan controller judgment

## Judgment

Verdict: `ACCEPT_WITH_NONBLOCKING_RESIDUALS`.

The planning gate is accepted. The plan is now handoff-ready and code-generation-ready for a future `multi-year annual analysis productization implementation gate`.

## Basis

- `AGENTS.md`: this is a heavy architecture/productization gate requiring independent review, controller judgment, explicit boundaries, and local accepted checkpoint.
- `docs/design.md`: current code remains single-year; accepted future multi-year annual evidence scope is target year plus up to four prior annual reports, with no public chapter-id expansion, no raw five-year text injection, and Fund-owned repository access.
- `docs/current-startup-packet.md`: current active gate is multi-year annual analysis productization planning; source/test/runtime/live/readiness/release changes are out of scope.
- `docs/implementation-control.md`: next entry point is planning worker for formal 2021-2025 multi-year annual analysis productization.
- `docs/reviews/mvp-multi-year-annual-evidence-scope-controller-judgment-20260603.md`: accepted design inputs require explicit typed scope, Service/Fund boundary separation, year-level degradation, additive bundle semantics, source-year anchors, and raw text prohibition.
- DS review: first review `ACCEPT_WITH_FINDINGS`, re-review `ACCEPT`.
- MiMo review: first review `ACCEPT_WITH_FINDINGS`, re-review `ACCEPT`.

## Accepted Findings And Fixes

| Finding | Controller disposition |
|---|---|
| Missing `ChapterFactProvider` / `ChapterFactProjection` extension contract | ACCEPTED_FIXED. Plan now requires `project_annual_evidence()` and maps cross-year facts into Chapter 5 `ChapterFactEntry` records under `annual_evidence.cross_year.*`. |
| `AnnualEvidenceBundle` field set under-specified | ACCEPTED_FIXED. Plan now pins required MVP fields, including current-year bundle, year records, source provenance, anchors, gaps, requirement availability, cross-year facts, degradation and fallback summaries. |
| `degradation_policy` naming drift | ACCEPTED_FIXED. Plan now uses `current_year_required_prior_years_optional`. |
| CLI surface ambiguity | ACCEPTED_FIXED. Plan now selects `fund-analysis analyze-annual-period <fund_code> --target-year 2025 --start-year 2021` and requires help text explaining the required target year and optional prior-year range. |
| Service-to-Fund scope relationship unresolved | ACCEPTED_FIXED. Plan now requires Service-to-Fund translation into a Fund-owned scope type with `required_years=(target_year,)` and `optional_years=prior_years`. |
| Prior-year extractor reuse could accidentally call full `FundDataExtractor.extract()` | ACCEPTED_FIXED. Plan now forbids optional prior-year calls to `FundDataExtractor.extract()` and requires narrow parser-to-structured-field reuse. |

## Accepted Residuals

- Concrete placement of `AnnualEvidenceScopeRequest` inside `fund_agent/fund/annual_evidence.py` is left to implementation, as long as Fund does not import the Service request type.
- Concrete collection type for `AnnualEvidenceBundle.year_records` is left to implementation, as long as canonical year ordering and tests are explicit.
- Sequential loading is accepted for correctness; concurrency remains deferred.
- Uniform `force_refresh` is accepted for MVP; per-year refresh remains deferred.
- Requirement-key-to-cross-year-fact mapping is left to implementation, but any public/typed requirement id must be explicit and tested.
- Implementation test matrix should explicitly include `integrity_error` under fail-closed category coverage.

## Rejected Or Deferred

- REJECTED for this gate: source expansion, fallback redesign, Eastmoney/fund-company/CNINFO re-entry, raw five-year text prompts, public chapter-id expansion, provider/runtime changes, score-loop, golden/readiness, release/readiness, PR state, cleanup, ignore rules, archive/delete/move.
- DEFERRED: controlled live EID evidence for multi-year availability, multi-year NAV/drawdown, concurrency, per-year refresh controls, full LLM writer integration beyond bounded typed facts, fallback/source expansion design, and readiness/release gates.

## Validation

- `git diff --check -- docs/reviews/mvp-multi-year-annual-analysis-productization-plan-20260611.md`: pass.
- Static artifact checks confirmed required plan sections and fix terms are present: `Service-to-Fund mapping`, `AnnualEvidenceBundle`, `project_annual_evidence`, `FundDataExtractor.extract()`, `analyze-annual-period`, and Chapter 5 degradation wording.
- MiMo and DS re-reviews both returned `ACCEPT`.

## Next Entry

Recommended next mainline entry: `multi-year annual analysis productization implementation gate`.

Implementation must start from the accepted plan and remain no-live by default. Any live EID/PDF/provider/LLM/analyze/checklist/golden/readiness/release command still requires a separate reviewed evidence gate.
