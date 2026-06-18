# Docling Same-source Reference Cache Metadata No-live Implementation Review DS - 2026-06-16

Gate: `Docling Same-source Reference Cache Metadata No-live Implementation Gate`
Reviewer: AgentDS (implementation review worker)
Release/readiness: `NOT_READY`
Verdict: `PASS_IMPLEMENTATION_READY_FOR_CONTROLLER_ACCEPTANCE_NOT_READY`

## Scope

Implementation review of the metadata-only repository/cache contract. This review checks that the implementation faithfully executes the controller-accepted plan (`docs/reviews/docling-same-source-reference-cache-metadata-contract-plan-controller-judgment-20260616.md`) and satisfies all six binding conditions. It does not authorize S4/S5/S6 evidence probing, correctness review, live/network/EID acquisition, parser replacement, or readiness/release.

## Evidence Reviewed

| Artifact | Role |
|---|---|
| `AGENTS.md` | Agent execution constraints and module boundaries |
| `docs/current-startup-packet.md` | Current gate, control state, and non-goals |
| `docs/implementation-control.md` | Current control truth |
| `docs/reviews/docling-same-source-reference-cache-metadata-contract-plan-controller-judgment-20260616.md` | Accepted plan and binding conditions |
| `docs/reviews/docling-same-source-reference-cache-metadata-no-live-implementation-evidence-20260616.md` | Implementation evidence under review |
| `fund_agent/fund/documents/models.py` | New `AnnualReportReferenceMetadata`, `AnnualReportReferenceMetadataResult`, status literal |
| `fund_agent/fund/documents/cache.py` | `get_reference_metadata()` and sync impl |
| `fund_agent/fund/documents/repository.py` | Repository facade `get_annual_report_reference_metadata()` |
| `fund_agent/fund/documents/__init__.py` | Public exports |
| `tests/fund/documents/test_cache.py` | Metadata-only cache contract tests |
| `tests/fund/documents/test_repository.py` | Repository facade tests |
| `fund_agent/fund/README.md` | Updated documentation |

## Validation Commands

| Command | Result |
|---|---|
| `git diff --check` | PASS (no output) |
| `uv run pytest tests/fund/documents/test_cache.py tests/fund/documents/test_repository.py -q` | 46 passed in 0.52s |
| `uv run ruff check fund_agent/fund/documents/models.py ...` | All checks passed! |
| `uv run pytest tests/fund/documents -q` | 134 passed in 2.96s |

## Findings

### F1: Repository boundary preserved (PASS)

`FundDocumentRepository.get_annual_report_reference_metadata()` (repository.py:421-447) is a new public method that validates inputs (`_validate_fund_code`, `_validate_year`), builds a `DocumentKey`, and delegates to `self._cache.get_reference_metadata()`. It does not call `load_annual_report()`, `fetch_pdf()`, `fetch_pdf_path()`, `parse_pdf()`, or any source adapter. The `FundDocumentRepository` boundary is the sole external entry point for evidence workers, satisfying binding condition 1.

### F2: Cache method avoids all forbidden access paths (PASS)

`AnnualReportDocumentCache.get_reference_metadata()` (cache.py:358-378) and its sync counterpart `_get_reference_metadata_sync()` (cache.py:380-432) query only the `documents` table with a narrow SELECT:

```sql
SELECT fund_code, year, document_kind, source_metadata_json
FROM documents
WHERE document_key = ?
```

The method does not:
- SELECT `pdf_path` column
- Query `parsed_reports` table
- Call `_load_parsed_report_sync()`, `_get_pdf_entry_sync()`, or `_get_pdf_path_sync()`
- Access the filesystem (no `Path` operations, no file reads)
- Import or reference Docling, pdfplumber, or source helpers
- Make network calls

This satisfies binding conditions 2, 3, and 4.

### F3: Allowed return fields are narrow and leak-free (PASS)

`AnnualReportReferenceMetadata` (models.py:292-321) contains exactly:

- `fund_code`, `document_year`, `report_type`
- `source`, `selected_source`, `source_mode`
- `fallback_enabled`, `fallback_used`, `primary_failure_category`
- `metadata_identity_hash` (SHA-256 over only the allowed fields)

The `to_dict()` method (models.py:360-386) serializes only these fields. Forbidden keys verified absent by test (test_cache.py:335-345): `pdf_path`, `payload_path`, `source_url`, `report_name`, `report_code`, `report_desp`, `upload_info_id`, `updated_at`. Satisfies binding condition 3.

### F4: Tests prove non-access and unsafe-metadata fail-closed behavior (PASS)

Six new test functions provide direct evidence:

1. **`test_cache_returns_reference_metadata_without_body_or_path_access`** (test_cache.py:278-345): Monkeypatches `_load_parsed_report_sync` and `_get_pdf_entry_sync` to `pytest.fail()` — proves the metadata query touches neither parsed payload nor PDF entry. Also asserts the result payload contains no forbidden keys.

2. **`test_cache_reference_metadata_reports_missing_without_pdf_probe`** (test_cache.py:348-378): Monkeypatches `_get_pdf_entry_sync` to fail — proves missing rows do not fall back to PDF probing.

3. **`test_cache_reference_metadata_rejects_unsafe_metadata`** (test_cache.py:381-464): Parametrized over 4 unsafe scenarios (`source_not_eid`, `fallback_enabled_not_false`, `primary_failure_category_present`, `source_metadata_fund_code_mismatch`). All return `status="unsafe_metadata"` with the correct reason.

4. **`test_repository_reference_metadata_facade_uses_cache_metadata_only`** (test_repository.py:224-282): Monkeypatches all three loader methods (`fetch_pdf`, `fetch_pdf_path`, `parse_pdf`) to raise `AssertionError`, and both cache body-access methods (`_load_parsed_report_sync`, `_get_pdf_entry_sync`) to `pytest.fail()`. Asserts `loader.fetch_pdf.assert_not_called()`, `loader.fetch_pdf_path.assert_not_called()`, `loader.parse_pdf.assert_not_called()`. Also asserts no `pdf_path` or filename in the serialized result.

5. **`test_repository_reference_metadata_preserves_validation`** (test_repository.py:285-308): Verifies empty `fund_code` and zero `year` raise `ValueError` — fail-closed input validation.

6. Implicit in `_build_reference_metadata_result()` (cache.py:171-241): All 6 EID single-source policy conditions are checked sequentially (`source_not_eid`, `selected_source_not_eid`, `source_mode_not_single_source_only`, `fallback_enabled_not_false`, `fallback_used_not_false`, `primary_failure_category_present`), each returning `unsafe_metadata` with a distinct, stable reason string. The `available` path requires all 6 conditions to pass.

Satisfies binding condition 4.

### F5: Documents vs parsed_reports row semantics decided (PASS)

The implementation queries only the `documents` table (not `parsed_reports`). Availability does not require a `parsed_reports` row to exist. This is a deliberate design choice: the metadata contract proves only that the `documents` table holds EID single-source/no-fallback identity for the requested fund/year. Whether a parsed report body also exists is a separate concern for a future evidence gate. Satisfies binding condition 5.

### F6: NOT_READY and non-claims preserved (PASS)

The implementation evidence explicitly states: not source truth, not field correctness, not full correctness, not Docling baseline promotion, not production parser replacement, not readiness/release proof, not S4/S5/S6 evidence proof. The code adds only a read-only metadata query; it does not modify `load_annual_report()`, production parse paths, source policy, or any existing behavior. Satisfies binding condition 6.

### F7: Public exports correct (PASS)

`fund_agent/fund/documents/__init__.py` exports `AnnualReportReferenceMetadata` and `AnnualReportReferenceMetadataResult` alongside existing types. No candidate or internal types are leaked.

### F8: README documentation updated (PASS)

`fund_agent/fund/README.md` (line 471, 495-496) documents the new repository method and its bodyless contract. The update is consistent with the implementation and does not overclaim.

### F9: No regressions in existing document tests (PASS)

Full `tests/fund/documents` suite: 134 passed. The new metadata methods do not break existing cache, repository, or adapter tests.

## Required Fixes

None.

## Deferred Risks

| Risk | Owner | Mitigation |
|---|---|---|
| `documents`-only semantics may be insufficient if future evidence gates need `parsed_reports` row co-availability | Controller / future gate owner | Explicitly decided in this implementation; any change requires a new gate |
| Missing `fund_code` in source_metadata is not treated as identity mismatch (only non-None mismatches are flagged) | Implementation owner | The 6 EID policy checks provide a safety net; a row with `source_metadata.fund_code=None` will still fail the `source_not_eid` check unless `source="eid"` and all other policy fields are correct |
| S4/S5/S6 metadata evidence remains unexecuted | Controller / evidence owner | Requires a separate accepted evidence gate after this implementation is accepted |

## Verdict

```text
VERDICT: PASS_IMPLEMENTATION_READY_FOR_CONTROLLER_ACCEPTANCE_NOT_READY
```
