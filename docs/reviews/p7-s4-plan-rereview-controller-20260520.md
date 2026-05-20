# P7-S4 Plan Rereview - Controller - 2026-05-20

## Scope

Targeted rereview for `docs/reviews/p7-s4-plan-review-controller-20260520.md`.

Reviewed artifact:

- `docs/reviews/p7-s4-source-metadata-hardening-plan-20260520.md`

## Verdict

PASS.

The required amendment is complete. P7-S4 can proceed to implementation.

## Finding Closure

### P7S4-PR-1 - Closed

The plan no longer uses adapter-wide mutable `_latest_source_metadata` or `consume_latest_source_metadata()` state.

The amended plan now requires:

- `AnnualReportPdfFetchResult(pdf_path, source_metadata)` as an immutable per-call result contract.
- `AnnualReportPdfAdapter.fetch_pdf(...)` to return the explicit fetch result.
- `fetch_pdf_path(...)` to remain a compatibility wrapper returning only `Path`.
- `FundDocumentRepository` to prefer metadata-aware `fetch_pdf(...)` when present and fallback to legacy `fetch_pdf_path(...)` with `source_metadata=None`.
- A regression test, `test_repository_concurrent_loads_do_not_cross_attach_source_metadata`, proving interleaved concurrent repository loads keep per-call metadata attached to the correct fund/year.
- Metadata precedence rules for `save_parsed_report(...)` so the documents row and parsed payload cannot silently diverge.

This resolves the concurrency provenance corruption risk identified in the first review.

## Residual Risk

The implementation must still be reviewed for:

- correct additive SQLite column handling for legacy caches;
- no accidental `PARSED_REPORT_SCHEMA_VERSION` invalidation of old parsed payloads;
- no Service/UI/Engine/CLI source-specific imports;
- no metadata divergence between `documents.source_metadata_json` and `ParsedAnnualReport.metadata`.
