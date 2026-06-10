# MVP EID Failure-Branch Evidence - 2026-06-10

## Gate

`no-live EID failure-branch evidence implementation gate`

## Scope Boundary

This evidence gate proves current EID annual-report failure classification and orchestration behavior without live source access.

No production code changed in this gate. No live EID call, network call, local annual-report PDF read, `FundDocumentRepository` live acquisition, fallback source activation, provider/LLM call, fixture projection, golden/readiness promotion, downstream implementation, release or PR action occurred.

## Evidence Matrix

| Failure category | No-live branch proved | Boundary behavior proved | Tests used as proof |
|---|---|---|---|
| `not_found` | `validate_fund.do` returns `isSuccess=false`; exact annual-report search returns empty `aaData`; fake source raises `AnnualReportSourceNotFoundError` | EID source raises `AnnualReportSourceNotFoundError`; current single-source orchestrator exhausts the only source and raises terminal not-found; no fallback source exists or is invoked | `test_eid_source_validate_fund_false_is_not_found`; `test_eid_source_search_empty_is_not_found`; `test_orchestrator_terminal_not_found_does_not_fallback`; `test_orchestrator_not_found_terminal_in_single_source`; `test_orchestrator_raises_file_not_found_when_all_sources_are_not_found` |
| `unavailable` | `httpx.MockTransport` raises timeout; fake source raises `AnnualReportSourceUnavailableError` | EID source raises `AnnualReportSourceUnavailableError`; current single-source orchestrator exhausts the only source and raises terminal unavailable; unavailable is not folded into not-found | `test_eid_source_transient_http_error_is_unavailable`; `test_orchestrator_terminal_unavailable_does_not_fallback`; `test_orchestrator_unavailable_exhaustion_is_not_file_not_found` |
| `schema_drift` | EID validate response misses `fundId`; duplicate valid candidates; unsupported attachment candidate; fake source raises `AnnualReportSourceSchemaError` | EID source raises `AnnualReportSourceSchemaError`; orchestrator maps it to `blocking_failure.category == "schema_drift"` and raises `AnnualReportSourceFallbackBlockedError` with the schema error as `__cause__` | `test_eid_source_validate_schema_error_fails_closed`; `test_eid_source_rejects_duplicate_candidates`; `test_eid_source_rejects_attachment_candidate`; `test_orchestrator_stops_on_schema_error` |
| `identity_mismatch` | EID candidate contradicts requested year, report type, table type or annual-report identity; fake source raises `AnnualReportSourceMismatchError` | EID source raises `AnnualReportSourceMismatchError`; orchestrator maps it to `blocking_failure.category == "identity_mismatch"` and raises `AnnualReportSourceFallbackBlockedError` with the mismatch error as `__cause__` | `test_eid_source_rejects_mismatched_candidates`; `test_orchestrator_does_not_fallback_after_eid_mismatch`; `test_orchestrator_stops_on_mismatch_error` |
| `integrity_error` | EID PDF response has non-PDF `Content-Type`; PDF body lacks `%PDF-`; atomic write receives invalid bytes; fake source raises `AnnualReportSourceIntegrityError` | EID source raises `AnnualReportSourceIntegrityError`; orchestrator maps it to `blocking_failure.category == "integrity_error"` and raises `AnnualReportSourceFallbackBlockedError` with the integrity error as `__cause__` | `test_eid_source_pdf_content_type_must_be_pdf`; `test_eid_source_pdf_magic_bytes_must_be_pdf`; `test_write_pdf_bytes_atomic_rejects_invalid_pdf_bytes`; `test_orchestrator_stops_on_integrity_error` |

## Single-Source Interpretation

`not_found` and `unavailable` remain fallback-eligible categories in the abstract failure taxonomy, but current production orchestration is EID single-source only. Therefore these categories are terminal in the current configured mode because the only configured source is exhausted. They are not "fallback blocked" categories in this evidence gate.

`schema_drift`, `identity_mismatch` and `integrity_error` are fail-closed categories. They are represented at the orchestration boundary as `AnnualReportSourceFallbackBlockedError` with `blocking_failure.category` set to the corresponding category.

## No-Live Proof Surface

The evidence uses only:

- `httpx.MockTransport` via `_EidMockServer` for EID HTTP behavior.
- `_FakeAnnualReportSource` for orchestrator boundary behavior.
- `_write_pdf_bytes_atomic` with pytest `tmp_path` for local invalid-byte integrity behavior.

The validation command did not read production annual-report PDFs, did not call `FundDocumentRepository`, and did not invoke Eastmoney/CNINFO/fund-company fallback sources.

## Validation

```bash
uv run pytest tests/fund/documents/test_annual_report_sources.py -q
```

Result:

```text
35 passed in 0.71s
```

```bash
uv run ruff check tests/fund/documents/test_annual_report_sources.py
```

Result:

```text
All checks passed!
```

## Residual Risk

Live EID failure branches remain unproven by design. Proving live outage, schema drift or integrity failures against the real EID endpoint would require a separate live evidence gate and explicit authorization.

This gate does not authorize fallback invocation, source-policy changes, fixture projection, golden/readiness promotion or downstream integration implementation.

## Next Recommended Gate

Controller should sync control truth for this accepted no-live evidence gate. After that, the next user-directed choices are downstream integration implementation or a separate live EID failure-branch evidence gate if explicitly authorized.
