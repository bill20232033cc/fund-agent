# P7-S4 Plan Review - Controller - 2026-05-20

## Verdict

Needs amendment before implementation.

The plan correctly identifies the current provenance break: `AnnualReportSourceResult.metadata` is lost at `AnnualReportPdfAdapter.fetch_pdf_path(...)`, and neither the documents SQLite row nor `ParsedAnnualReport` preserves source metadata. The planned scope is also correctly constrained to Fund Capability documents/cache/repository.

However, one implementation detail would create a correctness risk under async/concurrent repository calls.

## Finding

### P7S4-PR-1 - Medium - Adapter-level `latest_source_metadata` state can attach the wrong source metadata under concurrency

The plan proposes:

```python
self._latest_source_metadata: AnnualReportSourceMetadata | None = None
def consume_latest_source_metadata(self) -> AnnualReportSourceMetadata | None: ...
```

and then asks `FundDocumentRepository` to call `fetch_pdf_path(...)` followed by `consume_latest_source_metadata()`.

This is not a safe contract for an async repository. A single `FundDocumentRepository` instance owns one default `AnnualReportPdfAdapter`; if two `load_annual_report(...)` calls interleave on that adapter, the second fetch can overwrite `_latest_source_metadata` before the first call consumes it. The result is silent cross-fund/source provenance corruption: PDF path A can be parsed with source metadata B.

This conflicts with P7's design goal: provenance must be audit-friendly and not silently misleading. It also conflicts with the plan's own risk mitigation "stale loader metadata attaches to later parse"; `consume` only clears stale state after read, but does not prevent concurrent overwrite before read.

Required amendment:

- Do not use adapter-wide mutable "latest metadata" state as the metadata transport.
- Introduce an explicit fetch result contract for cache-aware loaders, for example:

```python
@dataclass(frozen=True, slots=True)
class AnnualReportPdfFetchResult:
    pdf_path: Path
    source_metadata: AnnualReportSourceMetadata | None
```

- Let `AnnualReportPdfAdapter` implement an explicit method such as `fetch_pdf(...) -> AnnualReportPdfFetchResult`.
- Keep `fetch_pdf_path(...) -> Path` as a compatibility convenience that delegates to `fetch_pdf(...)` and returns only `pdf_path`.
- Let `FundDocumentRepository` prefer the explicit metadata-aware method when present; fallback to `fetch_pdf_path(...)` with `source_metadata=None` only for legacy/custom loaders.
- Add a required test proving two interleaved/concurrent repository loads cannot cross-attach metadata. This can use a fake metadata-aware loader with per-call results and async events/barriers, or a simpler deterministic fake that returns different metadata per fund through the explicit result contract and asserts each returned `ParsedAnnualReport` carries its own source metadata.

## Non-blocking Notes

- The additive nullable `source_metadata_json` column strategy is acceptable.
- Not bumping `PARSED_REPORT_SCHEMA_VERSION` is acceptable if `ParsedAnnualReport.from_dict()` accepts missing metadata and old payloads remain usable.
- Moving `AnnualReportSourceMetadata` to `models.py` is acceptable and reduces schema drift.
- `save_parsed_report(..., source_metadata=...)` should define precedence clearly: prefer `source_metadata` when explicitly passed, otherwise use `report.metadata.source`, and ensure the documents row and parsed payload cannot diverge silently.

## Required Rereview Evidence

After amendment, the plan should explicitly show:

- The explicit fetch-result contract and where it lives.
- How `FundDocumentRepository` handles metadata-aware vs legacy cache-aware loaders.
- Why no adapter instance mutable metadata state is needed.
- The concurrency/cross-attachment regression test requirement.
