# Controller judgment: multi-year annual analysis productization implementation

## Judgment

- Gate: `multi-year annual analysis productization implementation gate`.
- Classification: `heavy`.
- Verdict: `ACCEPT_WITH_RESIDUALS`.
- Decision time: `20260611-175745`.
- Accepted implementation checkpoint: pending local commit.

This gate is accepted because the implementation adds a bounded deterministic multi-year annual-report product path, preserves Service/Fund/UI boundaries, keeps current EID single-source policy, records prior-year degradation/fail-closed states, projects cross-year facts only into chapter 5, updates tests/docs, and passed deterministic local validation.

## Truth Inputs

- `AGENTS.md`.
- `docs/design.md`.
- `docs/current-startup-packet.md`.
- `docs/implementation-control.md`.
- Plan: `docs/reviews/mvp-multi-year-annual-analysis-productization-plan-20260611.md`.
- Plan controller judgment: `docs/reviews/mvp-multi-year-annual-analysis-productization-plan-controller-judgment-20260611-165124.md`.
- Implementation evidence: `docs/reviews/mvp-multi-year-annual-analysis-productization-implementation-evidence-20260611.md`.
- DS implementation review: `docs/reviews/mvp-multi-year-annual-analysis-productization-implementation-review-ds-20260611.md`.
- MiMo implementation review: `docs/reviews/mvp-multi-year-annual-analysis-productization-implementation-review-mimo-20260611.md`.

## Accepted Repo Facts

- `fund_agent/fund/annual_evidence.py` adds Fund-owned annual evidence scope, loader, yearly records, gaps, anchors, bundle, and low-risk cross-year facts.
- `AnnualEvidenceLoader` accepts the current-year `StructuredFundDataBundle` from Service and loads optional prior years only through `FundDocumentRepository.load_annual_report(...)`.
- `FundDocumentRepository.load_annual_report(...)` is an async method in current repo code, matching the loader protocol and `await` usage.
- Prior-year processing uses narrow extractor functions against already loaded `ParsedAnnualReport`; it does not call full `FundDataExtractor.extract()` for prior years.
- Optional prior-year `not_found` / `unavailable` records become `gap`; `schema_drift` / `identity_mismatch` / `integrity_error` records become `failed_closed`.
- `ChapterFactProvider.project_annual_evidence(...)` preserves public chapter ids `0-7` and projects eligible cross-year facts only into chapter `5` under `annual_evidence.cross_year.*`.
- `FundAnalysisService.analyze_multi_year_annual(...)` maps the product request to Fund-owned `AnnualEvidenceScopeRequest`, runs target-year single-year `analyze()`, then calls the injected annual evidence loader.
- `fund-analysis analyze-annual-period` is the user-facing deterministic CLI entrypoint for bounded annual-period analysis.
- README files describe current behavior only and do not claim live verification.

## Review Disposition

### DS F1: async repository contract

- Original reviewer disposition: `MEDIUM`.
- Controller disposition: `REJECTED_AS_BLOCKER / RESOLVED`.
- Basis: repo fact shows `FundDocumentRepository.load_annual_report(...)` is `async def`; no live command is required to confirm this signature.

### DS F2: failure-category test coverage

- Original reviewer disposition: `LOW`.
- Controller disposition: `ACCEPTED_AND_FIXED`.
- Fix: parameterized optional prior-year source failure tests now cover `not_found`, `unavailable`, `integrity_error`, and `schema_drift`.
- Validation: targeted ruff passed; 129 relevant tests passed.

### DS F3: current-year `source_fund_id=None`

- Original reviewer disposition: `LOW`.
- Controller disposition: `ACCEPTED_RESIDUAL`.
- Basis: current `StructuredFundDataBundle` does not expose a public `source_fund_id` field. Creating one in this gate would expand structured-data/source-identity contracts beyond the accepted implementation scope.
- Owner: future structured-data/source-identity extension gate.

### DS F4: nested anchor lookup readability

- Original reviewer disposition: `INFO`.
- Controller disposition: `ACCEPTED_NONBLOCKING`.
- Basis: bounded MVP cardinality makes this a readability preference, not a correctness, boundary, or performance blocker.

### DS F5 and MiMo coverage residual

- Controller disposition: `ACCEPTED_RESIDUAL`.
- Basis: coverage collection fails in this local environment before tests execute through `akshare -> pandas -> numpy`; deterministic functional tests pass. Single-file coverage remains unmeasured and must not be presented as satisfied.

### MiMo review

- Reviewer verdict: `ACCEPT`.
- Controller disposition: `ACCEPT`.
- Basis: MiMo found no blocking or non-blocking issues after checking Service/Fund/UI boundaries, source policy, cross-year fact eligibility, chapter id constraints, docs, and validation evidence.

## Validation

Passed:

```bash
uv run ruff check fund_agent/fund/annual_evidence.py fund_agent/fund/chapter_facts.py fund_agent/services/fund_analysis_service.py fund_agent/services/__init__.py fund_agent/ui/cli.py tests/fund/test_annual_evidence.py tests/services/test_fund_analysis_service.py tests/ui/test_cli.py
```

Result: `All checks passed!`

```bash
uv run pytest tests/fund/test_annual_evidence.py tests/fund/test_chapter_facts.py tests/services/test_fund_analysis_service.py tests/ui/test_cli.py
```

Result: `129 passed in 1.27s`.

```bash
git diff --check
```

Result: passed with no output.

No live EID/network/PDF/FDR/provider/LLM/analyze/checklist/golden/readiness/release command was run in this gate.

## Accepted Residuals

- `annual_evidence.py` single-file coverage percentage was not independently measured due local coverage import failure before test execution; deterministic tests pass.
- Current-year `source_fund_id` is not available on `StructuredFundDataBundle`; cross-year identity evidence is therefore limited by current structured bundle metadata shape.
- CLI currently outputs target-year Markdown plus multi-year evidence summary, not a full cross-year narrative report. Typed evidence bundle and chapter 5 fact projection are implemented for a later writer/reporting slice.
- No live 2021-2025 EID/PDF run was executed. Live observation remains a separately authorized controlled live evidence gate.

## Next Entry

Recommended next mainline after accepted checkpoint and truth-doc sync:

1. `multi-year annual analysis productization truth-doc sync gate`.

Deferred entries:

- `controlled live 2021-2025 EID annual-period evidence gate`.
- `multi-year annual narrative writer/reporting gate`.
- `structured-data source identity extension gate`.
- `coverage measurement environment hygiene gate`.
