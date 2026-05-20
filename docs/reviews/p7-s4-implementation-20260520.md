# P7-S4 Source Metadata Hardening Implementation - 2026-05-20

## Scope

Implemented the accepted P7-S4 plan in `docs/reviews/p7-s4-source-metadata-hardening-plan-20260520.md`.

Changed files:

- `fund_agent/fund/documents/models.py`
- `fund_agent/fund/documents/sources.py`
- `fund_agent/fund/documents/adapters/annual_report_pdf.py`
- `fund_agent/fund/documents/repository.py`
- `fund_agent/fund/documents/cache.py`
- `tests/fund/documents/test_cache.py`
- `tests/fund/documents/test_repository.py`
- `tests/fund/documents/test_annual_report_sources.py`
- `fund_agent/fund/README.md`
- `tests/README.md`
- `docs/reviews/p7-s4-implementation-20260520.md`

No control docs, Service, UI, Engine, CLI, parser, extractor, audit, renderer, score, quality gate, live network behavior, or `extra_payload` changes were made.

## Implementation Summary

- Added document-level metadata models:
  - `AnnualReportSourceMetadata`
  - `AnnualReportCacheProvenance`
  - `AnnualReportMetadata`
  - `AnnualReportPdfFetchResult`
- Extended `ParsedAnnualReport` with `metadata`, while keeping legacy parsed payloads without `metadata` loadable.
- Moved source metadata ownership from `documents/sources.py` to `documents/models.py` to avoid schema drift.
- Added metadata-aware `AnnualReportPdfAdapter.fetch_pdf(...) -> AnnualReportPdfFetchResult`.
- Kept `fetch_pdf_path(...) -> Path` as a compatibility wrapper.
- Added additive `documents.source_metadata_json` column with `ALTER TABLE` compatibility.
- Added `AnnualReportPdfCacheEntry` and `get_pdf_entry(...)`; kept `get_pdf_path(...)`.
- Persisted source metadata through:
  - documents PDF cache row
  - parsed report JSON payload
  - returned `ParsedAnnualReport.metadata`
- Implemented repository behavior:
  - prefer metadata-aware `fetch_pdf(...)`
  - fallback to legacy `fetch_pdf_path(...)` with empty source metadata
  - attach cache provenance on fresh fetch, PDF cache hit, and parsed cache hit
  - force refresh overwrites stale source metadata
- Defined cache save precedence:
  - explicit `source_metadata` wins
  - otherwise use `report.metadata.source`
  - normalize parsed payload and documents row to the same metadata before writing
- Avoided adapter-wide mutable metadata state; metadata travels in the per-call immutable `AnnualReportPdfFetchResult`.

## Tests Added/Updated

Cache tests now cover:

- PDF source metadata persistence.
- legacy documents row without source metadata.
- parsed report metadata round-trip.
- legacy parsed payload without metadata.
- explicit `source_metadata` precedence preventing documents row and parsed payload divergence.

Repository tests now cover:

- EID source metadata on fresh fetch.
- Eastmoney fallback metadata persistence without fake EID IDs.
- parsed cache hit retaining metadata.
- PDF cache hit using cached source metadata.
- legacy PDF cache without metadata.
- force refresh metadata overwrite.
- metadata-aware loader preferred over legacy `fetch_pdf_path`.
- legacy loader still working with empty source metadata.
- concurrent/interleaved loads do not cross-attach metadata.

Source tests were updated only for moved metadata imports.

## Verification

Commands run:

```bash
.venv/bin/python -m pytest tests/fund/documents/test_cache.py tests/fund/documents/test_repository.py tests/fund/documents/test_annual_report_sources.py -q
```

Result: `55 passed`

```bash
.venv/bin/python -m pytest tests/fund/documents tests/fund/pdf/test_downloader.py -q
```

Result: `61 passed`

```bash
.venv/bin/python -m pytest tests/fund/audit/test_audit_programmatic.py tests/services/test_fund_analysis_service.py tests/ui/test_cli.py -q
```

Result: `38 passed`

```bash
.venv/bin/python -m pytest tests/ -q
```

Result: `290 passed`

```bash
.venv/bin/python -m ruff check .
```

Result: `All checks passed`

```bash
git diff --check
```

Result: passed

## Risks And Notes

- Existing parsed cache payloads without metadata remain compatible.
- Existing documents SQLite rows gain nullable `source_metadata_json` lazily during cache initialization.
- Metadata does not leak source selection into Service/UI/Engine/CLI; it remains document provenance on `ParsedAnnualReport`.
- No live EID or Eastmoney network behavior was tested by design.
- No commit was created.
