# MiMo implementation review: multi-year annual analysis productization

## Scope

- Reviewer: AgentMiMo.
- Gate: `multi-year annual analysis productization implementation gate`.
- Mode: pane-only independent implementation review, transcribed by controller.
- Reviewed target: current uncommitted workspace diff plus `docs/reviews/mvp-multi-year-annual-analysis-productization-implementation-evidence-20260611.md`.
- Review constraints: no file edits by reviewer, no stage/commit/push/PR, no live EID/network/PDF/FDR/provider/LLM/analyze/checklist/golden/readiness/release commands.

## Verdict

`ACCEPT`.

## Findings

No blocking or non-blocking findings.

## Boundary Verification

Reviewer verified:

- `FundAnalysisService.analyze_multi_year_annual()` normalizes fund code, translates `MultiYearAnnualAnalysisRequest` to `AnnualEvidenceScopeRequest`, runs target-year `analyze()`, then invokes the injected annual evidence loader.
- Service does not directly access `FundDocumentRepository`, PDF/cache/source helpers, parsers, provider, Host, live tooling, or filesystem document paths.
- `AnnualEvidenceLoader` loads prior years through repository protocol injection; default implementation is `FundDocumentRepository()`.
- Prior-year structured extraction calls only narrow extractor functions against the already loaded `ParsedAnnualReport`, and does not call full `FundDataExtractor.extract()` for prior years.
- EID single-source policy is preserved; no fallback or source expansion is introduced.
- `AnnualEvidenceScopeRequest` enforces `required_years == (target_year,)`.
- Source failure classification maps `not_found` / `unavailable` to degradable gaps and `schema_drift` / `identity_mismatch` / `integrity_error` to fail-closed year records.
- Target-year failure propagates through the existing single-year `analyze()` path before loader invocation.
- Cross-year facts require field value and anchor, require at least two available records, and are projected only into chapter `5` under `annual_evidence.cross_year.*`.
- Public chapter ids remain `0-7`.
- Existing `cross_period_comparison_missing` remains when cross-year facts are unavailable and is removed only when eligible cross-year facts exist.
- No explicit business parameter is hidden in `extra_payload`.
- README updates describe current deterministic behavior and do not claim live verification.

## Accepted Residuals

- Single-file coverage for `annual_evidence.py` was not independently measured because coverage collection fails in this local environment through `akshare -> pandas -> numpy`; deterministic functional tests pass.
- No live 2021-2025 EID/PDF run was executed; this remains a separately authorized controlled live evidence gate.
- CLI currently outputs target-year Markdown plus evidence summary, not a full cross-year narrative report; typed evidence bundle and chapter 5 projection are available for a later writer/reporting slice.

## Validation Notes

- Static review only.
- Reviewer relied on implementation evidence for deterministic command results:
  - ruff passed.
  - py_compile passed.
  - targeted pytest passed.
