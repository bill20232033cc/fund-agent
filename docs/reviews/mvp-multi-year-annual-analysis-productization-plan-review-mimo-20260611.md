# MVP multi-year annual analysis productization plan review - MiMo

## Review Scope

- Reviewer: AgentMiMo.
- Gate: `multi-year annual analysis productization planning gate`.
- Reviewed artifact: `docs/reviews/mvp-multi-year-annual-analysis-productization-plan-20260611.md`.
- Truth inputs: `AGENTS.md`, `docs/design.md`, `docs/current-startup-packet.md`, `docs/implementation-control.md`, `docs/reviews/mvp-multi-year-annual-evidence-scope-design-20260603.md`, `docs/reviews/mvp-multi-year-annual-evidence-scope-controller-judgment-20260603.md`.
- Review mode: pane-only output. MiMo initially attempted a write command despite handoff boundaries; controller cancelled the approval prompt and required pane-only output. No MiMo file write was approved or used as evidence.

## First Review Verdict

`ACCEPT_WITH_FINDINGS`.

## Findings

| Severity | Location | Disposition |
|---|---|---|
| material | plan Product Contract Decisions / Slice 2 | Accepted and fixed. The plan now states Service translates to Fund-owned `AnnualEvidenceScopeRequest` with `required_years=(target_year,)` and `optional_years=prior_years`. |
| minor | plan Slice 5 | Accepted and fixed. The plan now chooses `analyze-annual-period` and requires help text explaining `--start-year` as earliest optional prior year. |
| minor | plan Slice 3 | Accepted and fixed. The plan now forbids optional prior years from calling `FundDataExtractor.extract()` and requires parser-to-structured-field reuse only. |

## Re-Review Verdict

`ACCEPT`.

MiMo stated that all three prior findings are resolved. Remaining findings: none.

## Open Questions

- Whether `AnnualEvidenceScopeRequest` is a standalone dataclass in `fund_agent/fund/annual_evidence.py` or part of `AnnualEvidenceBundle` construction remains an implementation placement choice.
- Design-gate residuals for canonical per-year identity type, concurrency, requirement key extensibility, and cross-year fact algorithms remain deferred residuals; Chapter 5 degradation wording and `ChapterFactProvider` extension are now handled in the plan.

## Residual Risks

- Sequential loading may be slower for five years; concurrency remains deferred for correctness.
- The accepted design's nine suggested slices are merged into six implementation slices; implementation must treat Slice 3 and Slice 4 as multi-step slices.
- Uniform `force_refresh` across five years can be expensive; per-year refresh remains deferred.
- Implementation should explicitly include `integrity_error` in fail-closed category tests even though the plan already groups it under fail-closed categories.
