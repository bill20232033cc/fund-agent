# Code Review — P8-S3 Source Fallback Policy

## Scope

- Mode: current changes (P8-S3 inclusion set)
- Branch: main
- Base: design plan `docs/reviews/p8-s3-source-fallback-policy-plan-20260521.md` + plan review `docs/reviews/plan-review-20260521-060952.md`
- Output file: `docs/reviews/code-review-p8-s3-ds-20260521.md`
- Included scope:
  - `fund_agent/fund/documents/sources.py` (1317 lines) — full P8-S3 implementation: source failure taxonomy types, constants, exception classes (`AnnualReportSourceIntegrityError`, `AnnualReportSourceFallbackBlockedError`), orchestrator semantics, helper functions (`_build_failure`, `_can_fallback_after_failure`, `_format_blocked_failure`, `_raise_fallback_blocked`, `_mark_fallback_used`, `_raise_exhausted_sources`), EID source with PDF integrity checks, Eastmoney wrapper
  - `tests/fund/documents/test_annual_report_sources.py` (1362 lines) — 35 tests covering all 5 failure categories, fallback policy, blocking, exhaustion, concurrency, force_refresh, PDF adapter integration
  - `fund_agent/fund/README.md` (lines 57-58) — source failure taxonomy documentation
  - `docs/design.md` (lines 64-65) — fallback policy documentation
  - `tests/README.md` (line 8) — test scope documentation
- Excluded scope: all other files (pre-existing or untracked outside the inclusion set)
- Parallel review coverage: 无

## Review Walkthrough

### Entry point: `AnnualReportSourceOrchestrator.fetch_annual_report_pdf` (sources.py:601-660)

The orchestrator iterates sources in priority order. Each source's `fetch_annual_report_pdf` is called inside a try/except that maps 5 exception types to failure categories:

| Source exception | Failure category | Fallback? | Branch |
|---|---|---|---|
| `AnnualReportSourceNotFoundError` | `not_found` | yes | line 633-638 |
| `AnnualReportSourceUnavailableError` | `unavailable` | yes | line 639-644 |
| `AnnualReportSourceMismatchError` | `identity_mismatch` | no | line 645-648 |
| `AnnualReportSourceSchemaError` | `schema_drift` | no | line 649-652 |
| `AnnualReportSourceIntegrityError` | `integrity_error` | no | line 653-656 |

After a successful result, if any prior failures exist, `_mark_fallback_used` (line 767-780) sets `metadata.fallback_used=True` via `dataclasses.replace`. If no prior failures, the result is returned directly.

### EID source exception mapping (sources.py:547-564)

The `EidAnnualReportSource.fetch_annual_report_pdf` internal try/except maps:
- `FileNotFoundError` → `AnnualReportSourceNotFoundError` (line 553-554)
- `(httpx.HTTPError, OSError, ValueError)` → `AnnualReportSourceUnavailableError` (line 555-556)

`FileNotFoundError` is caught before `OSError` (its parent), so filesystem-not-found is correctly classified as `not_found` rather than `unavailable`. This ordering is deliberate and correct.

### PDF integrity validation (sources.py:1145-1162, 1187-1221)

Two independent integrity checkpoints:
1. `_validate_pdf_response` (line 1145) — checks HTTP `Content-Type: application/pdf` and `%PDF-` magic bytes on response body, raising `AnnualReportSourceIntegrityError` on mismatch
2. `_write_pdf_bytes_atomic` (line 1187) — re-checks `%PDF-` magic bytes before atomic write, raising `AnnualReportSourceIntegrityError` before any bytes hit disk

Atomic write uses `NamedTemporaryFile` + `os.fsync` + `os.replace`, with temp file cleanup on exception (line 1218-1220).

### Exhaustion semantics (sources.py:783-809)

`_raise_exhausted_sources` handles three terminal cases:
- All `not_found` → `AnnualReportSourceNotFoundError` (subclass of `FileNotFoundError`)
- Single `unavailable` → `AnnualReportSourceUnavailableError`
- Mixed or multiple `unavailable` → `AnnualReportSourceAggregateError` (carries structured `failures` tuple)

Empty failures raises `AnnualReportSourceNotFoundError` as a defensive fallback (line 801).

### Concurrent serialization (sources.py:112-197 area — `EidAnnualReportSource`)

Per-key `asyncio.Lock` guards cache check → download → write for the same fund/year combination. Concurrent callers for the same key reuse the first caller's downloaded PDF.

## Findings

未发现实质性问题。

### Architecture boundary confirmation

- Implementation ownership stays entirely in `fund_agent/fund/documents/sources.py` and its tests.
- No new imports into Service, UI, Engine, or CLI layers.
- `AnnualReportSourceFallbackBlockedError` and `AnnualReportSourceIntegrityError` are internal to the documents layer; the repository layer allows exceptions to propagate naturally.
- `dataclasses.replace` import confirmed at line 13 — used by `_mark_fallback_used` (line 780).

### Design plan compliance

- All 5 failure categories from the design plan are implemented as `Literal` types and used in orchestrator branching.
- `_FALLBACK_ELIGIBLE_CATEGORIES = frozenset({"not_found", "unavailable"})` — only these allow fallback (defense-in-depth: the `_can_fallback_after_failure` check on not_found/unavailable branches is harmless redundancy).
- `AnnualReportSourceFallbackBlockedError` carries `failures: tuple[AnnualReportSourceFailure, ...]` and `blocking_failure: AnnualReportSourceFailure`, with `__cause__` preserving the original exception via `from exc`.
- `AnnualReportSourceIntegrityError(ValueError)` for PDF Content-Type and `%PDF-` magic bytes validation.
- `fallback_used=True` metadata set on successful fallback; no success metadata invented for blocked or exhausted paths.

### Test coverage

35 tests, all passing:

- **Direct EID source**: `test_eid_source_fetches_004393_annual_report_with_validated_metadata`, `test_eid_source_validate_fund_false_is_not_found`, `test_eid_source_validate_schema_error_fails_closed`, `test_eid_source_search_empty_is_not_found`, `test_eid_source_rejects_mismatched_candidates` (4 parametrized cases), `test_eid_source_rejects_duplicate_candidates`, `test_eid_source_rejects_attachment_candidate`
- **Integrity errors**: `test_eid_source_pdf_content_type_must_be_pdf`, `test_eid_source_pdf_magic_bytes_must_be_pdf`, `test_write_pdf_bytes_atomic_rejects_invalid_pdf_bytes`
- **Unavailable**: `test_eid_source_transient_http_error_is_unavailable`, `test_eastmoney_source_maps_http_error_to_unavailable`, `test_eastmoney_source_maps_os_error_to_unavailable`
- **Orchestrator fallback**: `test_orchestrator_falls_back_to_eastmoney_after_eid_not_found`, `test_orchestrator_falls_back_after_unavailable_error`, `test_orchestrator_falls_back_after_not_found_error`, `test_orchestrator_returns_first_successful_source`
- **Orchestrator blocking**: `test_orchestrator_does_not_fallback_after_eid_mismatch`, `test_orchestrator_stops_on_mismatch_error`, `test_orchestrator_stops_on_schema_error`, `test_orchestrator_stops_on_integrity_error`
- **Blocked provenance**: `test_orchestrator_blocked_failure_preserves_prior_eligible_failures` (asserts prior failures tuple order and blocking failure pointer)
- **Exhaustion**: `test_orchestrator_raises_file_not_found_when_all_sources_are_not_found`, `test_orchestrator_unavailable_exhaustion_is_not_file_not_found`, `test_orchestrator_mixed_not_found_and_unavailable_preserves_unavailable_category`
- **Concurrency**: `test_eid_source_serializes_same_document_downloads` (asserts single PDF download for concurrent requests)
- **Cache/refresh**: `test_eid_source_force_refresh_overwrites_cached_pdf`, `test_eid_source_without_force_refresh_reuses_existing_pdf_after_metadata_validation`, `test_orchestrator_passes_force_refresh_to_source`
- **Timeouts**: `test_eid_source_uses_distinct_request_level_timeouts` (asserts metadata vs PDF timeout separation)
- **PDF adapter**: `test_annual_report_pdf_adapter_fetch_pdf_path_uses_source_orchestrator`
- **Default sources**: `test_orchestrator_rejects_empty_sources_but_none_uses_default`

### Plan review residual risks — addressed

The plan review identified two residual risks:

1. "Existing orchestrator tests currently assert direct `AnnualReportSourceMismatchError` / `AnnualReportSourceSchemaError` from the orchestrator" → **Resolved**: orchestrator tests (`test_orchestrator_does_not_fallback_after_eid_mismatch`, `test_orchestrator_stops_on_mismatch_error`, `test_orchestrator_stops_on_schema_error`) assert `AnnualReportSourceFallbackBlockedError`, while direct EID source tests (`test_eid_source_rejects_mismatched_candidates`) continue to assert source-level `AnnualReportSourceMismatchError`.

2. "`AnnualReportSourceIntegrityError` changes direct EID invalid-PDF tests from schema-style failure to integrity-style failure" → **Resolved**: `test_eid_source_pdf_content_type_must_be_pdf` and `test_eid_source_pdf_magic_bytes_must_be_pdf` assert `AnnualReportSourceIntegrityError`. `test_write_pdf_bytes_atomic_rejects_invalid_pdf_bytes` tests the integrity check at the atomic write level.

### Doc alignment

- `fund_agent/fund/README.md` line 57: describes 5 failure categories + fail-closed behavior + provenance preservation. ✓
- `docs/design.md` lines 64-65: describes fallback policy with explicit category classification. ✓
- `tests/README.md` line 8: describes test scope covering "显式 fallback 分类、fail-closed 阻断 provenance". ✓

## Open Questions

无。

## Residual Risk

- `_can_fallback_after_failure` check on not_found/unavailable orchestrator branches is always True by construction (these categories are in `_FALLBACK_ELIGIBLE_CATEGORIES`). The redundancy is harmless defense-in-depth; changing `_FALLBACK_ELIGIBLE_CATEGORIES` to exclude either would cause `AnnualReportSourceFallbackBlockedError` to be raised with a misleading message for those categories. Low risk given the constant's explicit purpose.
- No integration test exercises the full chain: real EID HTTP → orchestrator → Eastmoney fallback → repository → parsed report. Current tests use fake sources, which is correct for unit-level coverage. End-to-end fallback behavior under real network conditions remains a manual/smoke verification concern.
