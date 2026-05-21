# Code Review — P8-S3 Source Fallback Policy

## Reviewed Target

- Scope: P8-S3 source fallback taxonomy, fail-closed blocking exception, integrity error, docs alignment.
- Inclusion set: `fund_agent/fund/documents/sources.py`, `tests/fund/documents/test_annual_report_sources.py`, `fund_agent/fund/README.md`, `docs/design.md`, `tests/README.md`.
- Design truth: `docs/design.md`. Plan: `docs/reviews/p8-s3-source-fallback-policy-plan-20260521.md`. Plan review: `docs/reviews/plan-review-20260521-060952.md`.

## Test Results

```
52 passed in 0.85s
tests/fund/documents/test_annual_report_sources.py — all passed
tests/fund/documents/test_repository.py — all passed
```

## Review Lenses — Verification

### 1. Source failure taxonomy covers all five categories

**PASS.** `AnnualReportSourceFailureCategory` at `sources.py:26-32` is `Literal["not_found", "unavailable", "schema_drift", "identity_mismatch", "integrity_error"]`. All five plan-accepted categories are present.

### 2. Only not_found and unavailable are fallback eligible

**PASS.** `_FALLBACK_ELIGIBLE_CATEGORIES` at `sources.py:43-45` is `frozenset({"not_found", "unavailable"})`. `_can_fallback_after_failure` at `sources.py:685-698` checks membership in this frozenset. Tests `test_orchestrator_falls_back_to_eastmoney_after_eid_not_found` (line 737), `test_orchestrator_falls_back_after_unavailable_error` (line 953), `test_orchestrator_falls_back_after_not_found_error` (line 982) confirm eligible categories continue to fallback.

### 3. Blocking categories raise AnnualReportSourceFallbackBlockedError with provenance

**PASS.** Orchestrator at `sources.py:645-656` catches `AnnualReportSourceMismatchError` → `identity_mismatch`, `AnnualReportSourceSchemaError` → `schema_drift`, `AnnualReportSourceIntegrityError` → `integrity_error`. All three call `_raise_fallback_blocked(...)` which raises `AnnualReportSourceFallbackBlockedError` with `from exc` preserving `__cause__`.

`AnnualReportSourceFallbackBlockedError` at `sources.py:141-179`:
- `failures: tuple[AnnualReportSourceFailure, ...]` — all recorded failures including blocking one.
- `blocking_failure: AnnualReportSourceFailure` — last failure with blocking category.
- Validates `failures` non-empty and `blocking_failure == failures[-1]`.
- Inherits from `Exception` (not `FileNotFoundError` or source-specific exceptions) per plan.
- `__cause__` preserved via `from exc` in `_raise_fallback_blocked`.

Tests: `test_orchestrator_does_not_fallback_after_eid_mismatch` (line 761), `test_orchestrator_stops_on_mismatch_error` (line 1009), `test_orchestrator_stops_on_schema_error` (line 1039), `test_orchestrator_stops_on_integrity_error` (line 1069) all assert `__cause__` type, blocking category, message, and that fallback source was not called.

### 4. Exhausted eligible failures preserve prior final exception behavior

**PASS.** `_raise_exhausted_sources` at `sources.py:783-809` is unchanged in logic:
- All `not_found` → `AnnualReportSourceNotFoundError` (inherits `FileNotFoundError`)
- Single `unavailable` → `AnnualReportSourceUnavailableError`
- Mixed or multi-unavailable → `AnnualReportSourceAggregateError`

Tests: `test_orchestrator_raises_file_not_found_when_all_sources_are_not_found` (line 1146), `test_orchestrator_unavailable_exhaustion_is_not_file_not_found` (line 1175), `test_orchestrator_mixed_not_found_and_unavailable_preserves_unavailable_category` (line 1203).

### 5. Successful fallback marks metadata.fallback_used=True

**PASS.** `_mark_fallback_used` at `sources.py:767-780` uses `dataclasses.replace` to set `fallback_used=True`. Called at `sources.py:657-658` when `failures` is non-empty and result succeeded. Test `test_orchestrator_falls_back_to_eastmoney_after_eid_not_found` (line 737) asserts `result.metadata.fallback_used is True`.

### 6. EID invalid PDF uses AnnualReportSourceIntegrityError

**PASS.** `_validate_pdf_response` at `sources.py:1145-1162` raises `AnnualReportSourceIntegrityError` for bad Content-Type and missing `%PDF-`. `_write_pdf_bytes_atomic` at `sources.py:1187-1221` raises `AnnualReportSourceIntegrityError` for missing `%PDF-`.

Tests:
- `test_eid_source_pdf_content_type_must_be_pdf` (line 640): direct EID source, Content-Type check → `AnnualReportSourceIntegrityError`.
- `test_eid_source_pdf_magic_bytes_must_be_pdf` (line 665): direct EID source, magic bytes check → `AnnualReportSourceIntegrityError`.
- `test_write_pdf_bytes_atomic_rejects_invalid_pdf_bytes` (line 689): direct `_write_pdf_bytes_atomic` call → `AnnualReportSourceIntegrityError`, file not created.

### 7. Boundary constraints

**PASS.**
- All changes are in `fund_agent/fund/documents/sources.py` (Fund Capability documents layer).
- No Service, UI, Engine, or API code touched.
- `FundDocumentRepository` public signature unchanged.
- Source order, cache paths, network retry, parsed-report cache unchanged.
- New symbols (`AnnualReportSourceFallbackBlockedError`, `AnnualReportSourceIntegrityError`, `AnnualReportSourceFailureCategory`, `_FALLBACK_ELIGIBLE_CATEGORIES`, `_can_fallback_after_failure`) are all module-internal or test-imported; no new public contract leaks.

### 8. Tests and docs alignment

**PASS.**
- `fund_agent/fund/README.md`: Documents the five failure categories, fallback eligibility rule, and fail-closed behavior.
- `docs/design.md`: Documents fallback policy in the architecture section and data source table.
- `tests/README.md`: Updated to mention explicit fallback classification and fail-closed blocking provenance.
- All existing orchestrator tests for mismatch/schema were updated from asserting direct source exceptions to asserting `AnnualReportSourceFallbackBlockedError` with correct `__cause__`, category, and provenance.

## Findings

### F-1. Redundant guard on always-eligible categories (Informational)

**Severity:** Informational
**Location:** `sources.py:633-644`

The `not_found` and `unavailable` except branches include `if not _can_fallback_after_failure(failure.category):` guards. Since `not_found` and `unavailable` are always in `_FALLBACK_ELIGIBLE_CATEGORIES`, these guards are statically dead code.

This is not a correctness issue — it is forward-compatible if the frozenset changes — but it adds unreachable branches that could mislead a reader into thinking `not_found` or `unavailable` could be blocking. No action required; noting for awareness.

### F-2. Prior eligible failures before blocking are preserved (Confirmed)

**Severity:** None (positive confirmation)
**Location:** `sources.py:1101-1142`, test at line 1102

`test_orchestrator_blocked_failure_preserves_prior_eligible_failures` verifies that when EID returns `not_found` and Eastmoney returns `integrity_error`, the `AnnualReportSourceFallbackBlockedError.failures` contains `[("eid", "not_found"), ("eastmoney", "integrity_error")]` and `blocking_failure` is the last entry. This matches the plan's provenance requirement.

### F-3. Exception hierarchy correctness (Confirmed)

**Severity:** None (positive confirmation)
**Location:** `sources.py:141`

`AnnualReportSourceFallbackBlockedError` inherits from `Exception` as specified. It does not inherit from `FileNotFoundError`, `AnnualReportSourceNotFoundError`, or `AnnualReportSourceUnavailableError`. This ensures repository callers that catch `FileNotFoundError` for not-found exhaustion are not affected by fallback-blocked semantics.

## No Blocking Findings

All review lenses pass. The implementation matches the accepted plan, the test coverage is comprehensive, docs are aligned, and boundary constraints are respected.

## Conclusion

**pass**

P8-S3 source fallback policy implementation is code-complete and review-accepted. No blocking findings. One informational note about statically-dead guards on always-eligible categories (F-1).
