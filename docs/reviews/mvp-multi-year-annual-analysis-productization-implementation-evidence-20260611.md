# MVP multi-year annual analysis productization implementation evidence

## Scope

- Gate: `multi-year annual analysis productization implementation gate`.
- Classification: `heavy`.
- Accepted input:
  - Plan: `docs/reviews/mvp-multi-year-annual-analysis-productization-plan-20260611.md`.
  - DS plan review: `docs/reviews/mvp-multi-year-annual-analysis-productization-plan-review-ds-20260611.md`.
  - MiMo plan review: `docs/reviews/mvp-multi-year-annual-analysis-productization-plan-review-mimo-20260611.md`.
  - Controller plan judgment: `docs/reviews/mvp-multi-year-annual-analysis-productization-plan-controller-judgment-20260611-165124.md`.
- Non-goals preserved: no live EID/network/PDF/FDR/provider/LLM/analyze/checklist/golden/readiness/release command; no source expansion; no fallback redesign; no public chapter-id expansion; no PR/push.

## Implemented Repo Facts

- Added Fund-layer `fund_agent/fund/annual_evidence.py`.
  - Defines `AnnualEvidenceScopeRequest`, `AnnualEvidenceLoader`, `AnnualEvidenceBundle`, `AnnualYearEvidenceRecord`, `AnnualEvidenceGap`, `AnnualEvidenceAnchor`, and `CrossYearDerivedFact`.
  - `AnnualEvidenceScopeRequest` keeps MVP required years as `(target_year,)`, optional years as consecutive prior years, and enforces `max_years <= 5`.
  - `AnnualEvidenceLoader` receives the current-year `StructuredFundDataBundle` from Service and loads optional prior years only through `FundDocumentRepository.load_annual_report(...)`.
  - Optional prior-year `not_found` / `unavailable` becomes a `gap`; optional prior-year `schema_drift` / `identity_mismatch` / `integrity_error` becomes `failed_closed`.
  - Prior-year structured data uses narrow existing extractor functions against the already loaded `ParsedAnnualReport`: `extract_profile()`, `extract_manager_ownership()`, and `extract_holdings_share_change()`. It does not call full `FundDataExtractor.extract()` for prior years.
  - Derived cross-year facts are limited to `fee_schedule_trend`, `turnover_rate_trend`, `share_change_trend`, `holdings_snapshot_trend`, and `manager_continuity`, each requiring at least two available year records with value and anchor.
- Extended `fund_agent/fund/chapter_facts.py`.
  - Added `ChapterFactProvider.project_annual_evidence(...)` and `project_annual_evidence_chapter_facts(...)`.
  - Public chapter ids remain `0-7`.
  - Cross-year facts are projected only into chapter `5`, under `annual_evidence.cross_year.*` source field ids.
  - When cross-year facts are available, the prior single-year synthetic `cross_period_comparison_missing` gap is removed from chapter 5; otherwise the existing single-year gap remains.
- Extended Service.
  - Added `MultiYearAnnualAnalysisRequest` and `MultiYearAnnualAnalysisResult` in `fund_agent/services/fund_analysis_service.py`, exported from `fund_agent/services/__init__.py`.
  - Added `FundAnalysisService.analyze_multi_year_annual(...)`.
  - Service normalizes the fund code, maps product request to Fund-owned `AnnualEvidenceScopeRequest`, runs the target-year single-year `analyze()`, then invokes the injected annual evidence loader.
  - Service does not directly read `FundDocumentRepository`, PDF/cache/source helper, parser, or filesystem document paths in the multi-year method.
- Extended CLI.
  - Added `fund-analysis analyze-annual-period FUND_CODE --target-year 2025 --start-year 2021`.
  - CLI maps user parameters to `MultiYearAnnualAnalysisRequest`, calls Service `analyze_multi_year_annual(...)`, prints current-year quality gate summary and multi-year evidence summary, then prints the target-year Markdown report.
- Added/updated tests and docs.
  - Added `tests/fund/test_annual_evidence.py`.
  - `tests/fund/test_annual_evidence.py` explicitly covers optional prior-year `not_found` and `unavailable` as gaps, and `integrity_error` and `schema_drift` as fail-closed year records.
  - Updated `tests/services/test_fund_analysis_service.py` and `tests/ui/test_cli.py`.
  - Updated `README.md`, `fund_agent/README.md`, `fund_agent/fund/README.md`, and `tests/README.md` to describe current behavior only.
- Review follow-up repo fact: `fund_agent/fund/documents/repository.py` defines `FundDocumentRepository.load_annual_report(...)` as `async def`, so `AnnualEvidenceLoader` awaiting the default repository matches the existing repository contract.

## Validation

Passed:

```bash
uv run ruff check fund_agent/fund/annual_evidence.py fund_agent/fund/chapter_facts.py fund_agent/services/fund_analysis_service.py fund_agent/services/__init__.py fund_agent/ui/cli.py tests/fund/test_annual_evidence.py tests/services/test_fund_analysis_service.py tests/ui/test_cli.py
```

Result: `All checks passed!`

```bash
uv run pytest tests/fund/test_annual_evidence.py tests/fund/test_chapter_facts.py tests/services/test_fund_analysis_service.py tests/ui/test_cli.py
```

Result after review follow-up test expansion: `129 passed in 1.35s`.

```bash
uv run python -m py_compile fund_agent/fund/annual_evidence.py fund_agent/fund/chapter_facts.py fund_agent/services/fund_analysis_service.py fund_agent/ui/cli.py tests/fund/test_annual_evidence.py
```

Result: passed with no output.

```bash
uv run pytest tests/fund/test_annual_evidence.py
```

Result before review follow-up expansion: `6 passed in 0.37s`.

```bash
uv run ruff check tests/fund/test_annual_evidence.py fund_agent/fund/annual_evidence.py
```

Result after review follow-up test expansion: `All checks passed!`

Attempted but not accepted as functional failure:

```bash
uv run pytest tests/fund/test_annual_evidence.py --cov=fund_agent.fund.annual_evidence --cov-report=term-missing --cov-fail-under=80
uv run coverage run --source=fund_agent.fund.annual_evidence -m pytest tests/fund/test_annual_evidence.py
```

Both coverage collection commands failed during collection with local import failure through `akshare -> pandas -> numpy`: `ImportError: cannot load module more than once per process`. The same test file passed without coverage immediately afterward. This is recorded as a coverage-measurement residual, not as evidence of product test failure.

## Residuals

- `annual_evidence.py` single-file coverage percentage was not independently measured because coverage collection fails in this local environment before tests run. Functional deterministic tests for the new module pass.
- The CLI currently outputs the target-year Markdown report plus evidence summary; it does not yet render a new full cross-year narrative report. The current implementation provides the typed evidence bundle and chapter 5 fact projection needed by a later writer/reporting slice.
- No live 2021-2025 EID/PDF run was executed in this implementation gate; live observation remains a separately authorized controlled evidence gate.

## Review Request

Implementation review should focus on:

- Whether Service/Fund/UI boundaries match `AGENTS.md`, `docs/design.md`, and the accepted plan.
- Whether optional prior-year degradation and fail-closed categories are represented correctly.
- Whether cross-year facts have sufficient anchors and do not over-claim when prior years are missing or failed-closed.
- Whether CLI/docs describe current behavior without implying a live-verified or fully narrative cross-year report.
- Whether the coverage residual is acceptable for this gate or requires a narrow follow-up before controller final judgment.
