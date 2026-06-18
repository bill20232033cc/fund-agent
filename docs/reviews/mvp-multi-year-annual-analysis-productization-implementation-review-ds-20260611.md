# DS implementation review: multi-year annual analysis productization

## Scope

- Reviewer: AgentDS.
- Gate: `multi-year annual analysis productization implementation gate`.
- Mode: pane-only independent implementation review, transcribed by controller.
- Reviewed target: current uncommitted workspace diff plus `docs/reviews/mvp-multi-year-annual-analysis-productization-implementation-evidence-20260611.md`.
- Review constraints: no file edits by reviewer, no stage/commit/push/PR, no live EID/network/PDF/FDR/provider/LLM/analyze/checklist/golden/readiness/release commands.

## Initial Verdict

`ACCEPT_WITH_FINDINGS`.

## Findings

### F1

- Severity: `MEDIUM`.
- Location: `fund_agent/fund/annual_evidence.py`.
- Finding: `_AnnualReportRepository.load_annual_report` is declared async and `AnnualEvidenceLoader` awaits the default repository; reviewer requested confirmation that real `FundDocumentRepository.load_annual_report` is also async.
- Follow-up disposition: `RESOLVED`.
- Basis: `fund_agent/fund/documents/repository.py` defines `FundDocumentRepository.load_annual_report(...)` as `async def` at the current implementation.
- Controller note: this is rejected as a real blocker because the repo fact confirms the async contract.

### F2

- Severity: `LOW`.
- Location: `tests/fund/test_annual_evidence.py`.
- Finding: source failure classification tests initially covered `not_found` and `integrity_error`, but not `unavailable` and `schema_drift`.
- Follow-up disposition: `RESOLVED`.
- Fix: `tests/fund/test_annual_evidence.py` now parameterizes optional prior-year failures:
  - `not_found -> gap`
  - `unavailable -> gap`
  - `integrity_error -> failed_closed`
  - `schema_drift -> failed_closed`
- Validation after fix:
  - `uv run ruff check tests/fund/test_annual_evidence.py fund_agent/fund/annual_evidence.py` -> `All checks passed!`
  - `uv run pytest tests/fund/test_annual_evidence.py tests/fund/test_chapter_facts.py tests/services/test_fund_analysis_service.py tests/ui/test_cli.py` -> `129 passed in 1.35s`

### F3

- Severity: `LOW`.
- Location: `fund_agent/fund/annual_evidence.py`.
- Finding: current-year `source_fund_id=None`, so cross-year fund-id identity checking is limited by the current `StructuredFundDataBundle` shape.
- Follow-up disposition: `ACCEPTED_RESIDUAL`.
- Basis: current `StructuredFundDataBundle` has no public `source_fund_id` field in this gate; adding one would be a structure/data-contract expansion outside this implementation scope.
- Owner: future structured-data/source-identity extension gate.

### F4

- Severity: `INFO`.
- Location: `fund_agent/fund/chapter_facts.py`.
- Finding: nested loop for annual anchor lookup is less readable.
- Disposition: `ACCEPTED_NONBLOCKING`.
- Basis: MVP cardinality is bounded at up to five years and small field/anchor counts; no correctness or boundary issue found.

### F5

- Severity: `INFO`.
- Finding: coverage collection command fails in local environment through `akshare -> pandas -> numpy` import path.
- Disposition: `ACCEPTED_RESIDUAL`.
- Basis: functional deterministic tests pass; coverage failure is recorded in implementation evidence as measurement residual, not product failure.

## Boundary Verification

Reviewer verified:

- Service does not directly import or call `FundDocumentRepository`, PDF/cache/source helper, parser, or filesystem document path for multi-year prior years.
- Fund prior-year loading goes through `FundDocumentRepository.load_annual_report(...)` only.
- No source expansion or fallback behavior was introduced.
- Target year remains required; prior-year `not_found` / `unavailable` are degradable gaps; fail-closed categories are represented.
- Cross-year facts require value plus anchor and remain chapter 5 only.
- Public chapter ids remain `0-7`.
- No `extra_payload` or open business payload bag was introduced.
- README changes describe current behavior and do not claim live verification.

## Follow-Up Verdict

`ACCEPT`.

Final DS statement after targeted re-review:

- F1 disposition: `RESOLVED`.
- F2 disposition: `RESOLVED`.
- F3 disposition: `ACCEPTED_RESIDUAL`.
- Any remaining blocker: none.
