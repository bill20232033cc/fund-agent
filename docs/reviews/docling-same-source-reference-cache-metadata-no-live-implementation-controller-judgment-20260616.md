# Docling Same-source Reference Cache Metadata No-live Implementation Controller Judgment - 2026-06-16

Gate: `Docling Same-source Reference Cache Metadata No-live Implementation Gate`
Controller: AgentController
Release/readiness: `NOT_READY`
Verdict: `ACCEPT_IMPLEMENTATION_READY_FOR_METADATA_EVIDENCE_GATE_NOT_READY`

## Scope

This judgment accepts the no-live implementation of a metadata-only annual-report same-source reference contract.

It does not accept S4/S5/S6 evidence yet, does not prove source truth, does not prove field correctness or full correctness, does not promote Docling baseline, does not replace the production parser, and does not change readiness/release/PR state.

## Evidence Reviewed

| Artifact | Role |
| --- | --- |
| `docs/reviews/docling-same-source-reference-cache-metadata-contract-plan-controller-judgment-20260616.md` | Accepted implementation plan |
| `docs/reviews/docling-same-source-reference-cache-metadata-no-live-implementation-evidence-20260616.md` | Implementation evidence |
| `docs/reviews/docling-same-source-reference-cache-metadata-no-live-implementation-review-ds-tmux-20260616.md` | DS implementation review |
| `fund_agent/fund/documents/models.py` | New metadata-only result models |
| `fund_agent/fund/documents/cache.py` | Metadata-only SQLite query |
| `fund_agent/fund/documents/repository.py` | Repository facade |
| `tests/fund/documents/test_cache.py` | Cache tests |
| `tests/fund/documents/test_repository.py` | Repository facade tests |
| `fund_agent/fund/README.md` | Developer documentation sync |

## Accepted Implementation

- `AnnualReportReferenceMetadata` and `AnnualReportReferenceMetadataResult` define a bodyless, pathless metadata contract.
- `AnnualReportDocumentCache.get_reference_metadata()` reads only `documents.fund_code`, `documents.year`, `documents.document_kind`, and `documents.source_metadata_json`.
- The cache method does not read parsed payloads, PDF paths, PDF file metadata, PDF bodies, source helpers, source adapters, Docling or pdfplumber.
- `FundDocumentRepository.get_annual_report_reference_metadata()` preserves the repository boundary and delegates to the metadata cache method after existing input validation.
- `load_annual_report()` behavior is unchanged.
- `available` requires exact identity plus current EID single-source/no-fallback policy fields.
- `missing` and `unsafe_metadata` fail closed.

## Review Disposition

| Finding | Disposition | Controller judgment |
| --- | --- | --- |
| DS F1 repository boundary | ACCEPT | Repository facade is the public entry point. |
| DS F2 forbidden access paths | ACCEPT | Metadata query does not select PDF path or parsed payload and does not call unsafe methods. |
| DS F3 return field scope | ACCEPT | Return fields are narrow and leak-free. |
| DS F4 tests | ACCEPT | Tests prove non-access and unsafe metadata fail-closed behavior. |
| DS F5 `documents` vs `parsed_reports` semantics | ACCEPT_WITH_RESIDUAL | Implementation intentionally proves `documents` metadata availability only; parsed body co-availability is future evidence policy if needed. |
| DS F6 no-overclaim | ACCEPT | `NOT_READY` and non-claims are preserved. |
| DS F7 public exports | ACCEPT | New public contract types are exported. |
| DS F8 README | ACCEPT | Documentation matches implementation. |
| MiMo review | DEFERRED_REVIEW_CHANNEL_RESIDUAL | MiMo pane remained blocked in a prior interactive prompt and is not counted. |

## Validation Accepted

```text
uv run pytest tests/fund/documents/test_cache.py tests/fund/documents/test_repository.py -q
46 passed

uv run ruff check fund_agent/fund/documents/models.py fund_agent/fund/documents/cache.py fund_agent/fund/documents/repository.py fund_agent/fund/documents/__init__.py tests/fund/documents/test_cache.py tests/fund/documents/test_repository.py
All checks passed!

git diff --check
PASS

uv run pytest tests/fund/documents -q
134 passed
```

## Residuals

| Residual | Owner | Handling |
| --- | --- | --- |
| S4/S5/S6 metadata evidence not executed | Next evidence gate | Must run a separate metadata evidence gate using only the accepted facade. |
| `documents` metadata does not prove parsed body co-availability | Future evidence/controller gate | Treat metadata as reference availability proof only; correctness review still requires accepted reference route decisions. |
| Missing `source_metadata.fund_code` is not itself an identity mismatch | Future hardening if needed | Row identity is exact; source policy fields still gate availability. |

## Next Gate

Proceed to:

```text
Docling Same-source Reference Cache Metadata Evidence Gate
```

That gate may call only `FundDocumentRepository.get_annual_report_reference_metadata()` for S4/S5/S6 and must preserve `NOT_READY`. It must not call `load_annual_report()`, cache internals, PDF paths, parsed body, live/network, Docling, pdfplumber or correctness review.

## Final Verdict

```text
VERDICT: ACCEPT_IMPLEMENTATION_READY_FOR_METADATA_EVIDENCE_GATE_NOT_READY
```
