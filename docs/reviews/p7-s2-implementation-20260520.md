# P7-S2 Document Repository Source Abstraction Implementation - 2026-05-20

## Scope

Implemented the accepted P7-S2 plan as an internal Fund Capability refactor.

No EID client was implemented. Production default still uses the existing Eastmoney/akshare downloader, now wrapped as an `AnnualReportSource`.

## Changes

- Added `fund_agent/fund/documents/sources.py`
  - `AnnualReportSource` Protocol
  - `AnnualReportSourceConfig`
  - `AnnualReportSourceMetadata`
  - `AnnualReportSourceResult`
  - `EastmoneyAnnualReportSource`
  - `AnnualReportSourceOrchestrator`
  - fail-closed source errors and aggregate failure records
- Updated `fund_agent/fund/documents/adapters/annual_report_pdf.py`
  - replaced direct downloader dependency with source orchestrator dependency
  - kept parsing/text/table/section behavior unchanged
- Updated `tests/fund/documents/test_repository.py`
  - migrated PDF adapter tests from downloader injection to fake source orchestrator injection
  - repository cache behavior tests remain unchanged
- Added `tests/fund/documents/test_annual_report_sources.py`
  - covers source priority, fallback, mismatch/schema fail-closed, force refresh, adapter fetch path, and final unavailable/not-found semantics
  - covers Eastmoney wrapper mapping `httpx.HTTPError` to unavailable instead of not-found
  - covers `AnnualReportSourceOrchestrator(None)` defaulting to Eastmoney and `AnnualReportSourceOrchestrator(())` raising `ValueError`
- Updated `fund_agent/fund/README.md`
  - documents current source-backed internal PDF acquisition
- Updated `tests/README.md`
  - documents source orchestrator tests and no-real-network rule

## Final Error Semantics

The orchestrator no longer collapses all exhausted fallback-eligible failures into `FileNotFoundError`.

- all sources not-found -> `AnnualReportSourceNotFoundError`
- single unavailable source -> `AnnualReportSourceUnavailableError`
- multiple unavailable or mixed unavailable/not-found -> `AnnualReportSourceAggregateError` with per-source categories
- mismatch/schema errors stop fallback immediately

## Boundary Check

- `FundDocumentRepository.load_annual_report(...)` signature unchanged.
- Repository parsed report and PDF cache behavior unchanged.
- Service/UI/Engine/CLI unchanged.
- No `extra_payload` introduced.
- No real network tests added.
- No EID endpoints implemented.
- No parser behavior changed.

## Verification

Verification:

```text
.venv/bin/python -m pytest tests/fund/documents/test_annual_report_sources.py tests/fund/documents/test_repository.py -q
19 passed

.venv/bin/python -m pytest tests/fund/documents/test_annual_report_sources.py -q
12 passed

.venv/bin/python -m pytest tests/fund/documents tests/fund/pdf/test_downloader.py -q
28 passed

.venv/bin/python -m pytest tests/fund/audit/test_audit_programmatic.py tests/services/test_fund_analysis_service.py tests/ui/test_cli.py -q
38 passed

.venv/bin/python -m pytest tests/ -q
258 passed

.venv/bin/python -m ruff check .
All checks passed

git diff --check
passed
```
