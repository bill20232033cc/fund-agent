# P7-S3 EID Primary Implementation - 2026-05-20

## Scope

Implemented the accepted P7-S3 plan in `docs/reviews/p7-s3-eid-primary-implementation-plan-20260520.md`.

Changed files:

- `fund_agent/fund/documents/sources.py`
- `tests/fund/documents/test_annual_report_sources.py`
- `fund_agent/fund/README.md`
- `tests/README.md`
- `docs/reviews/p7-s3-implementation-20260520.md`

No control docs, Service, UI, Engine, CLI, parser, cache schema, or `extra_payload` changes were made.

## Implementation Summary

- Added `EidAnnualReportSource` behind the P7-S2 `AnnualReportSource` protocol.
- Changed `AnnualReportSourceOrchestrator(None)` default order to:

```text
EID primary -> Eastmoney/akshare fallback
```

- Kept `AnnualReportSourceOrchestrator(())` fail-closed with `ValueError`.
- Implemented EID endpoint flow:
  - `validate_fund.do`
  - `advanced_search_report.do`
  - `instance_show_pdf_id.do`
- Implemented deterministic `aoData` encoding with `reportType=FB010`, requested `reportYear`, and exact `fundCode`.
- Implemented typed EID candidate parsing and fail-closed annual-report filters:
  - exact fund code
  - exact validate `fundId`
  - exact report year
  - `reportCode=FB010010`
  - `reportDesp=年度报告`
  - `tableName=PDF`
  - reject annual-report abstracts
  - reject unsupported attachment links
  - reject duplicate valid candidates
- Implemented EID PDF validation:
  - HTTP 200 required
  - `Content-Type: application/pdf` required
  - body must start with `%PDF-`
- Implemented request-level timeout semantics:
  - metadata endpoints use `metadata_timeout_seconds`
  - PDF endpoint uses `pdf_timeout_seconds`
  - one async client/session is still used per source call for cookie preservation.
- Kept fallback categories:
  - not-found and unavailable remain fallback eligible.
  - mismatch and schema errors stop fallback.
- EID metadata is returned in `AnnualReportSourceResult`; no metadata persistence or cache schema migration was added.

## Tests Added/Updated

`tests/fund/documents/test_annual_report_sources.py` now covers:

- EID 004393/2024 fixture happy path.
- `validate_fund.do` false as not-found.
- validate response schema failure.
- empty `aaData` as not-found.
- wrong year, quarterly report, non-PDF table, abstract title as fail-closed mismatch.
- duplicate valid candidates as schema error.
- unsupported attachment candidate as schema error.
- PDF Content-Type validation.
- `%PDF-` magic-byte validation.
- transient timeout as unavailable.
- default orchestrator order EID then Eastmoney.
- fallback after EID not-found.
- no fallback after EID mismatch.
- `force_refresh=True` overwrites deterministic EID PDF cache.
- non-force refresh reuses existing PDF after metadata validation.
- request-level timeout values differ between metadata and PDF requests.

All EID tests use fake network only. No live EID, Eastmoney, or akshare network is required.

## Documentation

- `fund_agent/fund/README.md` now describes current document source behavior as EID primary with Eastmoney/akshare fallback inside Fund Capability only.
- `tests/README.md` now describes fake EID network coverage and request-level timeout/PDF validation expectations.

## Verification

Commands run:

```bash
.venv/bin/python -m pytest tests/fund/documents/test_annual_report_sources.py -q
```

Result: `30 passed`

```bash
.venv/bin/python -m pytest tests/fund/documents tests/fund/pdf/test_downloader.py -q
```

Result: `47 passed`

```bash
.venv/bin/python -m pytest tests/fund/audit/test_audit_programmatic.py tests/services/test_fund_analysis_service.py tests/ui/test_cli.py -q
```

Result: `38 passed`

```bash
.venv/bin/python -m pytest tests/ -q
```

Result: `276 passed`

```bash
.venv/bin/python -m ruff check .
```

Result: `All checks passed`

```bash
git diff --check
```

Result: passed

## Risks And Notes

- EID response schema can drift; required fields and contradictory rows fail closed.
- EID outage remains fallback eligible, so Eastmoney/akshare can still serve when EID is unavailable or not-found.
- EID mismatch/schema errors intentionally stop fallback to avoid hiding source identity or report-type contradictions.
- No live-network behavior was verified in tests by design.
- No commit was created.
