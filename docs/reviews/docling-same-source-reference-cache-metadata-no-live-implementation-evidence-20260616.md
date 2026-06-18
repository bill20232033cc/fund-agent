# Docling Same-source Reference Cache Metadata No-live Implementation Evidence - 2026-06-16

Gate: `Docling Same-source Reference Cache Metadata No-live Implementation Gate`
Role: implementation worker
Release/readiness: `NOT_READY`
Verdict: `IMPLEMENTATION_READY_FOR_REVIEW_NOT_READY`

## Scope

Implemented a narrow metadata-only repository/cache contract for annual-report same-source reference availability.

This implementation does not execute S4/S5/S6 evidence probing, does not perform correctness review, does not read PDF/body content, does not run live/network/EID acquisition, and does not change production annual-report source policy.

## Files Changed

| File | Change |
| --- | --- |
| `fund_agent/fund/documents/models.py` | Added `AnnualReportReferenceMetadata`, `AnnualReportReferenceMetadataResult`, and status literal. |
| `fund_agent/fund/documents/cache.py` | Added `AnnualReportDocumentCache.get_reference_metadata()` and sync SQLite metadata-only implementation. |
| `fund_agent/fund/documents/repository.py` | Added repository facade `get_annual_report_reference_metadata()`. |
| `fund_agent/fund/documents/__init__.py` | Exported new metadata contract types. |
| `tests/fund/documents/test_cache.py` | Added metadata-only cache contract tests. |
| `tests/fund/documents/test_repository.py` | Added repository facade tests. |
| `fund_agent/fund/README.md` | Documented current metadata-only repository contract. |

## Contract Summary

The new contract answers only whether local cache metadata contains exact annual-report identity and EID single-source/no-fallback source metadata.

Allowed public result fields:

- `fund_code`
- `document_year`
- `report_type`
- `source`
- `selected_source`
- `source_mode`
- `fallback_enabled`
- `fallback_used`
- `primary_failure_category`
- `metadata_identity_hash`

Explicitly not returned:

- PDF path or PDF metadata
- parsed payload path
- source URL
- report name/code/description
- upload IDs
- timestamps
- raw text, sections, tables, table cells or evidence anchors
- file hashes over PDF/body bytes

## Safety Properties

- `FundDocumentRepository.get_annual_report_reference_metadata()` validates inputs and delegates only to the cache metadata method.
- `AnnualReportDocumentCache.get_reference_metadata()` queries only `documents` identity columns and `source_metadata_json`.
- It does not call `load_annual_report()`, `load_parsed_report()`, `get_pdf_entry()`, `get_pdf_path()`, `fetch_pdf()`, `fetch_pdf_path()`, `parse_pdf()`, source helpers, Docling or pdfplumber.
- `available` is returned only when exact identity matches and the source metadata satisfies current EID single-source/no-fallback policy:
  `source=eid`, `selected_source=eid`, `source_mode=single_source_only`, `fallback_enabled=false`, `fallback_used=false`, `primary_failure_category=null`.
- Missing rows return `missing`.
- Metadata rows that exist but violate identity or source-policy constraints return `unsafe_metadata`.

## Validation

Commands run:

```text
uv run pytest tests/fund/documents/test_cache.py tests/fund/documents/test_repository.py -q
uv run ruff check fund_agent/fund/documents/models.py fund_agent/fund/documents/cache.py fund_agent/fund/documents/repository.py fund_agent/fund/documents/__init__.py tests/fund/documents/test_cache.py tests/fund/documents/test_repository.py
git diff --check
uv run pytest tests/fund/documents -q
```

Results:

```text
46 passed in 0.69s
All checks passed!
git diff --check: PASS, no output
134 passed in 3.55s
```

## Non-claims

- Not source truth.
- Not field correctness.
- Not full correctness.
- Not Docling baseline promotion.
- Not production parser replacement.
- Not readiness/release proof.
- Not S4/S5/S6 evidence proof yet.

## Next Gate Recommendation

Proceed to implementation review, then controller judgment. If accepted, next gate should be:

```text
Docling Same-source Reference Cache Metadata Evidence Gate
```

That evidence gate may call only the accepted metadata-only repository facade for S4/S5/S6 and must preserve `NOT_READY`.

## Final Verdict

```text
VERDICT: IMPLEMENTATION_READY_FOR_REVIEW_NOT_READY
```
