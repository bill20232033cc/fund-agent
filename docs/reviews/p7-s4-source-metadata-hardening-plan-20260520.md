# P7-S4 Source Metadata Hardening Plan - 2026-05-20

## Verdict

Implement P7-S4 as a Fund Capability document-repository hardening slice: persist annual-report source metadata from `AnnualReportSourceResult` into repository cache and `ParsedAnnualReport` metadata so snapshot/report debugging can identify the exact acquisition provenance.

The stable upper entry remains:

```text
FundDocumentRepository.load_annual_report(fund_code, year, *, force_refresh=False)
```

Service/UI/Engine/CLI should not gain source-specific awareness. Source metadata may travel only through existing document result contracts inside Fund Capability.

## Inputs

- `docs/reviews/post-p6-follow-up-planning-20260520.md`
- `docs/reviews/p7-s1-eid-source-research-spike-plan-20260520.md`
- `docs/reviews/p7-s2-document-repository-source-abstraction-plan-20260520.md`
- `docs/reviews/p7-s3-eid-primary-implementation-plan-20260520.md`
- `docs/reviews/p7-s3-implementation-20260520.md`
- `docs/implementation-control-p4.md`
- `docs/design.md`
- current code at `main`
- `fund_agent/fund/documents/sources.py`
- `fund_agent/fund/documents/adapters/annual_report_pdf.py`
- `fund_agent/fund/documents/repository.py`
- `fund_agent/fund/documents/cache.py`
- `fund_agent/fund/documents/models.py`
- `tests/fund/documents/test_annual_report_sources.py`
- `tests/fund/documents/test_repository.py`
- `tests/fund/documents/test_cache.py`

## Problem Statement

P7-S2 introduced `AnnualReportSourceMetadata`; P7-S3 populates it for EID and Eastmoney fallback. Today that metadata is still lost before callers receive `ParsedAnnualReport`:

1. `EidAnnualReportSource.fetch_annual_report_pdf(...)` returns `AnnualReportSourceResult(pdf_path, metadata)`.
2. `AnnualReportSourceOrchestrator` marks fallback metadata with `fallback_used=True` when prior source attempts were skipped.
3. `AnnualReportPdfAdapter.fetch_pdf_path(...)` returns only `result.pdf_path`; P7-S4 must add an explicit metadata-aware fetch contract instead of using adapter instance state.
4. `FundDocumentRepository` records only `pdf_path` in the `documents` SQLite table.
5. `AnnualReportPdfAdapter.parse_pdf(...)` constructs `ParsedAnnualReport` without source metadata.
6. `ParsedAnnualReport.to_dict()` / `from_dict()` persist only key, raw text, sections, and tables.

Result: once parsing completes, snapshot/debugging cannot tell whether the report came from EID or Eastmoney, which EID IDs were used, whether fallback happened, or which cached PDF row produced the parsed payload.

P7-S4 must preserve source provenance without moving source knowledge above the document repository boundary.

## Non-goals

P7-S4 does not:

- Change `FundDocumentRepository.load_annual_report(...)` public signature.
- Add Service/UI/Engine/CLI source selection, source branching, or source display behavior.
- Add `extra_payload`.
- Add direct fund document filesystem access outside repository/cache/adapter internals.
- Change EID lookup, fallback eligibility, PDF validation, retry, or timeout behavior.
- Change parser, extractor, audit, template renderer, score, or quality gate logic.
- Persist source metadata in snapshots or rendered reports outside existing `ParsedAnnualReport` result flow.
- Add live network tests.
- Introduce a cache migration tool or destructive cache rewrite.

## Boundary Decision

Source metadata belongs to Fund Capability document models and cache because it describes annual-report acquisition provenance.

Allowed dependency direction:

```text
sources.py -> AnnualReportSourceMetadata
annual_report_pdf.py -> source orchestrator result, parsed report model
repository.py -> cache-aware loader metadata hook, cache APIs
cache.py -> ParsedAnnualReport serialization and documents table metadata JSON
models.py -> public ParsedAnnualReport metadata field
```

Do not import EID constants, source orchestrator internals, or source-specific classes into Service/UI/Engine/CLI.

## Current Metadata Flow Analysis

Current source metadata fields in `AnnualReportSourceMetadata`:

- `source`
- `source_url`
- `fund_code`
- `fund_id`
- `report_year`
- `report_code`
- `report_desp`
- `report_name`
- `upload_info_id`
- `upload_info_detail_id`
- `table_name`
- `report_send_date`
- `operation_upload_type`
- `corrections_num`
- `fallback_used`

Current cache tables:

```text
documents(
  document_key,
  fund_code,
  year,
  document_kind,
  pdf_path,
  updated_at
)

parsed_reports(
  document_key,
  fund_code,
  year,
  document_kind,
  payload_path,
  schema_version,
  updated_at
)
```

Current parsed payload JSON:

```json
{
  "key": {},
  "raw_text": "...",
  "sections": {},
  "tables": []
}
```

Metadata is currently visible only before `AnnualReportPdfAdapter.fetch_pdf_path(...)` returns. The fix must carry metadata in the same per-call return value as the PDF path; do not use adapter-wide mutable "latest metadata" state because concurrent async repository calls can interleave and cross-attach source metadata to the wrong PDF/report.

## Proposed Schema And API Changes

### 1. Move Source Metadata Model To Documents Model Layer

Add source metadata dataclasses to `fund_agent/fund/documents/models.py` so both source acquisition and parsed report payload can use the same public Fund document model without creating an import cycle.

Recommended shape:

```python
AnnualReportSourceName = Literal["eid", "eastmoney"]

@dataclass(frozen=True, slots=True)
class AnnualReportSourceMetadata:
    source: AnnualReportSourceName | None = None
    source_url: str | None = None
    fund_code: str | None = None
    fund_id: str | None = None
    report_year: int | None = None
    report_code: str | None = None
    report_desp: str | None = None
    report_name: str | None = None
    upload_info_id: str | None = None
    upload_info_detail_id: str | None = None
    table_name: str | None = None
    report_send_date: str | None = None
    operation_upload_type: str | None = None
    corrections_num: int | None = None
    fallback_used: bool = False

@dataclass(frozen=True, slots=True)
class AnnualReportCacheProvenance:
    pdf_path: str | None = None
    pdf_cache_hit: bool = False
    parsed_cache_hit: bool = False
    source_metadata_present: bool = False
    cache_schema_version: int | None = None

@dataclass(frozen=True, slots=True)
class AnnualReportMetadata:
    source: AnnualReportSourceMetadata | None = None
    cache: AnnualReportCacheProvenance = AnnualReportCacheProvenance()
```

Add `to_dict()` / `from_dict()` methods for each new dataclass.

Rationale:

- `ParsedAnnualReport` can expose one stable `metadata` field without depending on `sources.py`.
- `sources.py` can import `AnnualReportSourceMetadata` from `models.py`, eliminating duplicate schema definitions.
- Cache and repository can serialize/deserialize metadata without importing EID implementation.

### 2. Extend `ParsedAnnualReport`

Add field at the end:

```python
metadata: AnnualReportMetadata = field(default_factory=AnnualReportMetadata)
```

Serialization behavior:

- `to_dict()` writes `"metadata": self.metadata.to_dict()`.
- `from_dict()` accepts missing `"metadata"` and defaults to empty metadata.
- Missing legacy metadata must not invalidate otherwise usable parsed report cache.

Compatibility:

- Appending field with default keeps current constructor calls valid.
- Existing tests that compare whole `ParsedAnnualReport` objects may need expected fixtures updated only when they assert metadata.

### 3. Replace `sources.py` Local Metadata Dataclass

Update `fund_agent/fund/documents/sources.py`:

- Import `AnnualReportSourceMetadata` and `AnnualReportSourceName` from `models.py`.
- Remove duplicate local `AnnualReportSourceName` / `AnnualReportSourceMetadata` definitions.
- Keep `AnnualReportSourceResult` in `sources.py` because it is source-protocol-specific and contains a local PDF path.

This avoids two metadata classes diverging after persistence is added.

### 4. Explicit PDF Fetch Result Contract

Do not use adapter-wide mutable metadata state.

Add a per-call fetch result contract to `fund_agent/fund/documents/models.py` or `fund_agent/fund/documents/adapters/annual_report_pdf.py`. Preferred location is `models.py` because repository protocols and adapter implementation can share it without import cycles:

```python
@dataclass(frozen=True, slots=True)
class AnnualReportPdfFetchResult:
    pdf_path: Path
    source_metadata: AnnualReportSourceMetadata | None = None
```

`AnnualReportPdfAdapter` should implement:

```python
async def fetch_pdf(
    self,
    fund_code: str,
    year: int,
    *,
    force_refresh: bool = False,
) -> AnnualReportPdfFetchResult:
    ...
```

Behavior:

- `fetch_pdf(...)` calls the source orchestrator and returns `AnnualReportPdfFetchResult(result.pdf_path, result.metadata)`.
- `fetch_pdf_path(...) -> Path` remains as a compatibility wrapper:

```python
fetch_result = await self.fetch_pdf(fund_code, year, force_refresh=force_refresh)
return fetch_result.pdf_path
```

Why keep `fetch_pdf_path(...)`:

- Existing custom loaders/tests may only implement the legacy path contract.
- The public repository signature remains unchanged.
- Compatibility wrapper does not carry metadata and therefore cannot corrupt metadata.

Why this is concurrency-safe:

- `pdf_path` and `source_metadata` are returned in the same immutable per-call object.
- No adapter instance field is used as a metadata transport.
- Interleaved `load_annual_report(...)` calls cannot overwrite each other's metadata before repository attachment.

### 5. Repository Metadata Attachment

Extend repository loader protocols to prefer metadata-aware fetch when present, while retaining legacy custom loader support.

```python
class _MetadataAwareAnnualReportLoader(_AnnualReportLoader, Protocol):
    async def fetch_pdf(
        self,
        fund_code: str,
        year: int,
        *,
        force_refresh: bool = False,
    ) -> AnnualReportPdfFetchResult: ...
```

Implementation in `FundDocumentRepository.load_annual_report(...)`:

1. If parsed report cache hit:
   - return cached report with `metadata.cache.parsed_cache_hit=True`
   - do not call loader or source
2. If PDF path cache hit and parsed cache miss:
   - parse cached PDF
   - attach source metadata from cache row if present
   - set `metadata.cache.pdf_cache_hit=True`, `parsed_cache_hit=False`
3. If source fetch needed:
   - if loader has coroutine `fetch_pdf(...)`, call it and receive `AnnualReportPdfFetchResult`
   - otherwise call legacy `fetch_pdf_path(...)` and set `source_metadata=None`
   - record PDF path plus source metadata in cache
   - parse PDF
   - attach explicit source metadata and cache provenance
4. Save parsed report with metadata so later parsed cache hits keep provenance.

Recommended helper:

```python
def _with_annual_report_metadata(
    report: ParsedAnnualReport,
    *,
    source_metadata: AnnualReportSourceMetadata | None,
    pdf_path: Path | None,
    pdf_cache_hit: bool,
    parsed_cache_hit: bool,
    cache_schema_version: int,
) -> ParsedAnnualReport:
    ...
```

Use `dataclasses.replace(...)` to avoid mutating frozen dataclasses.

### 6. Cache API Changes

Extend `AnnualReportDocumentCache`:

```python
async def get_pdf_entry(key: DocumentKey) -> AnnualReportPdfCacheEntry | None: ...
async def record_pdf_path(
    key: DocumentKey,
    pdf_path: Path,
    *,
    source_metadata: AnnualReportSourceMetadata | None = None,
) -> None: ...
async def save_parsed_report(
    report: ParsedAnnualReport,
    *,
    pdf_path: Path | None = None,
    source_metadata: AnnualReportSourceMetadata | None = None,
) -> None: ...
```

Keep existing `get_pdf_path(...)` as a convenience wrapper returning only `Path | None` for current tests/callers.

Metadata precedence for `save_parsed_report(...)`:

1. If `source_metadata` argument is explicitly provided, it is the source of truth.
2. Otherwise use `report.metadata.source`.
3. Before writing parsed payload, normalize the report so `report.metadata.source` equals the source metadata written to the `documents` row.
4. If an explicit `source_metadata` conflicts with `report.metadata.source`, do not silently write divergent values. Prefer replacing the report metadata with explicit `source_metadata`; optionally raise `ValueError` if implementation chooses stricter fail-closed behavior, but tests must pin whichever behavior is chosen.

This prevents the documents row and parsed payload from silently diverging.

Recommended new dataclass in `cache.py`:

```python
@dataclass(frozen=True, slots=True)
class AnnualReportPdfCacheEntry:
    pdf_path: Path
    source_metadata: AnnualReportSourceMetadata | None
    updated_at: str
```

## Cache Schema And Migration Decision

Use an additive SQLite schema change, not a destructive migration.

Add nullable JSON column to `documents`:

```sql
source_metadata_json TEXT
```

Implementation:

- During `initialize()`, after `CREATE TABLE IF NOT EXISTS documents`, call a private `_ensure_documents_source_metadata_column(connection)`.
- Inspect `PRAGMA table_info(documents)`.
- If `source_metadata_json` is absent, run:

```sql
ALTER TABLE documents ADD COLUMN source_metadata_json TEXT
```

Do not bump `PARSED_REPORT_SCHEMA_VERSION` solely for this new parsed payload field because `ParsedAnnualReport.from_dict()` will accept missing metadata. If the implementation chooses to bump the version for strict payload shape tracking, it must ensure legacy parsed reports are not all invalidated unnecessarily. Preferred decision: no version bump.

Backward compatibility:

- Existing `documents` rows without `source_metadata_json` load successfully and return `source_metadata=None`.
- Existing parsed report JSON without `"metadata"` loads successfully with empty metadata.
- `get_pdf_path(...)` remains compatible.
- `save_parsed_report(..., pdf_path=...)` can be called without source metadata.
- When source metadata is present, parsed payload metadata and `documents.source_metadata_json` must be aligned by the precedence rules above.

## Force Refresh And Cache-Hit Behavior

### `force_refresh=False`

Parsed report cache hit:

- Return cached parsed report.
- Set/retain `metadata.source` from parsed JSON.
- Set `metadata.cache.parsed_cache_hit=True`.
- Do not call source or parse PDF.

PDF cache hit, parsed cache miss:

- Use `get_pdf_entry(...)`.
- Parse cached PDF.
- Attach `entry.source_metadata` if present.
- Set `metadata.cache.pdf_cache_hit=True`.
- Save parsed report with that metadata.

No cache hit:

- Fetch via source orchestrator.
- Record `pdf_path` and source metadata in `documents`.
- Parse PDF.
- Attach source metadata and `pdf_cache_hit=False`, `parsed_cache_hit=False`.
- Save parsed report with metadata.

### `force_refresh=True`

- Skip parsed report cache.
- Skip PDF path cache.
- Fetch via source orchestrator.
- Record fresh source metadata in `documents`.
- Parse PDF and save parsed payload with fresh metadata.
- Set `pdf_cache_hit=False`, `parsed_cache_hit=False`.

Force refresh must overwrite stale source metadata in both documents row and parsed payload.

## Eastmoney Fallback Metadata

When EID fails with fallback-eligible error and Eastmoney succeeds, the existing orchestrator returns Eastmoney metadata with:

```text
source="eastmoney"
fund_code=<requested>
report_year=<requested>
fallback_used=true
```

P7-S4 should persist exactly that metadata.

Do not fake EID IDs for fallback results:

- `fund_id=None`
- `upload_info_id=None`
- `upload_info_detail_id=None`
- `report_code=None`
- `report_desp=None`
- `table_name=None`
- `source_url=None` unless Eastmoney source later provides it explicitly

This makes debugging honest: fallback was used, but EID announcement/PDF IDs are not known.

## Owned Files

Allowed implementation files:

| File | Action |
|---|---|
| `fund_agent/fund/documents/models.py` | Add metadata dataclasses and `AnnualReportPdfFetchResult`; extend `ParsedAnnualReport` serialization |
| `fund_agent/fund/documents/sources.py` | Reuse metadata model from `models.py`; keep source result protocol |
| `fund_agent/fund/documents/adapters/annual_report_pdf.py` | Add metadata-aware `fetch_pdf(...)`; keep `fetch_pdf_path(...)` wrapper |
| `fund_agent/fund/documents/repository.py` | Prefer metadata-aware fetch result; fallback to legacy path-only loader; attach metadata and cache provenance |
| `fund_agent/fund/documents/cache.py` | Add nullable source metadata JSON column, PDF cache entry API, metadata serialization |
| `tests/fund/documents/test_cache.py` | Cache schema, legacy row, metadata round-trip tests |
| `tests/fund/documents/test_repository.py` | Repository metadata flow tests |
| `tests/fund/documents/test_annual_report_sources.py` | Update imports if metadata moves; add minimal source metadata serialization coverage only if needed |
| `fund_agent/fund/README.md` | Describe current metadata persistence behavior |
| `tests/README.md` | Describe source metadata cache tests |
| `docs/reviews/p7-s4-implementation-20260520.md` | Implementation artifact |

Do not modify control docs.

## File-Level Implementation Plan

### `models.py`

1. Import `field` and update typing as needed.
2. Add `AnnualReportSourceName`, `AnnualReportSourceMetadata`, `AnnualReportCacheProvenance`, `AnnualReportMetadata`, `AnnualReportPdfFetchResult`.
3. Implement `to_dict()` / `from_dict()` for metadata dataclasses.
4. Add `metadata` field to `ParsedAnnualReport` after `tables`.
5. Update `ParsedAnnualReport.to_dict()` / `from_dict()` with missing-metadata compatibility.

All new classes and functions need Chinese docstrings.

### `sources.py`

1. Import `AnnualReportSourceName` and `AnnualReportSourceMetadata` from `models.py`.
2. Delete local duplicate definitions.
3. Confirm EID and Eastmoney construction still fills the same fields.
4. Keep `AnnualReportSourceResult` unchanged except for imported metadata type.
5. Keep fallback semantics unchanged.

### `annual_report_pdf.py`

1. Add `fetch_pdf(...) -> AnnualReportPdfFetchResult`.
2. Implement `fetch_pdf(...)` by calling source orchestrator and returning PDF path plus source metadata in the same immutable object.
3. Keep `fetch_pdf_path(...) -> Path` as a compatibility wrapper over `fetch_pdf(...)`.
4. Do not add `_latest_source_metadata`, `consume_latest_source_metadata()`, or any adapter-wide metadata state.
5. Do not change parser behavior.

### `repository.py`

1. Add private helpers to detect metadata-aware vs legacy cache-aware loaders:

```python
def _get_metadata_aware_loader(loader: _AnnualReportLoader) -> _MetadataAwareAnnualReportLoader | None: ...
def _get_cache_aware_loader(loader: _AnnualReportLoader) -> _CacheAwareAnnualReportLoader | None: ...
```

2. When source fetch is needed, prefer `fetch_pdf(...)`; if absent, fallback to legacy `fetch_pdf_path(...)` and `source_metadata=None`.
3. Switch raw PDF cache branch from `get_pdf_path(...)` to `get_pdf_entry(...)`.
4. Attach metadata and provenance to parsed reports before saving/returning.
5. Preserve existing behavior for non-cache-aware loaders.
6. Keep `load_annual_report(...)` signature unchanged.

### `cache.py`

1. Add `AnnualReportPdfCacheEntry`.
2. Add `source_metadata_json` column if absent.
3. Add serialize/deserialize helpers:

```python
def _source_metadata_to_json(metadata: AnnualReportSourceMetadata | None) -> str | None
def _source_metadata_from_json(payload: str | None) -> AnnualReportSourceMetadata | None
```

4. Update `record_pdf_path(...)` to accept optional metadata and write JSON.
5. Add `get_pdf_entry(...)`; keep `get_pdf_path(...)` delegating to it.
6. Update `save_parsed_report(...)` to write PDF metadata when provided and to persist `report.to_dict()` metadata payload.
7. Apply explicit metadata precedence so `documents.source_metadata_json` and parsed payload metadata cannot diverge silently.

## Tests

### Cache Tests

Add/update tests in `tests/fund/documents/test_cache.py`:

1. `test_cache_persists_pdf_source_metadata`
   - record PDF path with EID metadata.
   - load `get_pdf_entry(...)`.
   - assert EID fields survive: `source`, `source_url`, `fund_id`, `upload_info_id`, `upload_info_detail_id`, `report_year`, `report_code`, `report_desp`, `report_name`, `table_name`, `fallback_used`.

2. `test_cache_loads_legacy_documents_row_without_source_metadata`
   - manually create/insert a legacy `documents` row with no `source_metadata_json` or with null value.
   - assert `get_pdf_entry(...)` returns path and `source_metadata is None`.

3. `test_parsed_report_payload_round_trips_metadata`
   - save a `ParsedAnnualReport` with metadata.
   - reload and assert metadata is preserved.

4. `test_legacy_parsed_report_without_metadata_loads_with_empty_metadata`
   - write old-style parsed JSON without `"metadata"`.
   - assert `load_parsed_report(...)` returns report with `metadata.source is None`.

5. `test_save_parsed_report_aligns_explicit_source_metadata_with_payload`
   - pass a report with source metadata A and explicit `source_metadata` B.
   - assert persisted parsed payload and documents row both use the same chosen source metadata according to the implemented precedence rule.
   - assert the test would fail if documents row uses B while parsed payload silently keeps A.

### Repository Tests

Add/update tests in `tests/fund/documents/test_repository.py`:

1. `test_repository_attaches_eid_source_metadata_on_fresh_fetch`
   - fake metadata-aware loader returns `AnnualReportPdfFetchResult(pdf_path, eid_metadata)`.
   - assert returned `ParsedAnnualReport.metadata.source.source == "eid"`.
   - assert EID IDs and `source_url` are present.
   - assert cache provenance `pdf_cache_hit=False`, `parsed_cache_hit=False`.
   - assert documents cache row persists metadata.

2. `test_repository_attaches_eastmoney_fallback_metadata_on_fresh_fetch`
   - fake loader metadata `source="eastmoney"`, `fallback_used=True`.
   - assert fallback flag persists and no fake EID IDs are invented.

3. `test_repository_parsed_cache_hit_retains_metadata`
   - first load saves report metadata.
   - second load returns parsed cache.
   - assert loader not called again.
   - assert metadata source fields remain available.
   - assert cache provenance marks `parsed_cache_hit=True`.

4. `test_repository_pdf_cache_hit_uses_cached_source_metadata`
   - manually record PDF path with source metadata.
   - parsed report cache missing.
   - assert loader `fetch_pdf_path` not called.
   - assert parse result receives cached source metadata on returned report and saved parsed payload.

5. `test_repository_legacy_cache_without_metadata_still_loads`
   - record PDF path without metadata.
   - parsed cache missing.
   - assert returned report has empty source metadata and does not raise.

6. `test_repository_force_refresh_overwrites_source_metadata`
   - first load persists EID metadata A.
   - force refresh returns metadata B.
   - assert returned and cached metadata are B, not stale A.

7. `test_repository_metadata_aware_loader_preferred_over_legacy_fetch_pdf_path`
   - fake loader implements both `fetch_pdf(...)` and `fetch_pdf_path(...)`.
   - `fetch_pdf(...)` returns source metadata; `fetch_pdf_path(...)` would return only a path.
   - assert repository calls metadata-aware `fetch_pdf(...)` and persists metadata.

8. `test_repository_legacy_fetch_pdf_path_loader_gets_empty_source_metadata`
   - fake loader implements only `fetch_pdf_path(...)` and `parse_pdf(...)`.
   - assert repository still works and returned `ParsedAnnualReport.metadata.source is None`.

9. `test_repository_concurrent_loads_do_not_cross_attach_source_metadata`
   - use one repository instance and one fake metadata-aware loader.
   - run two concurrent/interleaved `load_annual_report(...)` calls for different fund codes or years.
   - fake loader returns distinct `AnnualReportPdfFetchResult` objects with distinct source metadata per call.
   - use async events/barriers or deterministic per-call sleeps to force interleaving between fetch and parse.
   - assert each returned `ParsedAnnualReport` carries the metadata for its own fund/year.
   - assert documents cache rows also retain the correct per-call metadata.
   - this test specifically guards against any reintroduction of adapter-wide `_latest_source_metadata` style state.

### Source Tests

Update `tests/fund/documents/test_annual_report_sources.py` only for moved imports. Existing EID/Eastmoney metadata assertions should remain valid.

## README Sync

Update `fund_agent/fund/README.md`:

- `load_annual_report()` returns `ParsedAnnualReport` with `metadata`.
- `metadata.source` identifies EID or Eastmoney fallback and source IDs when available.
- `metadata.cache` identifies cache provenance such as parsed cache hit or PDF cache hit.
- Source metadata is a Fund Capability document provenance contract, not a Service/UI source-selection API.

Update `tests/README.md`:

- Document repository/cache tests cover source metadata persistence, legacy cache compatibility, fallback metadata, and cache-hit provenance.

Do not describe future report rendering or UI display as current behavior.

## Acceptance Commands

Implementation should run:

```bash
.venv/bin/python -m pytest tests/fund/documents/test_cache.py tests/fund/documents/test_repository.py tests/fund/documents/test_annual_report_sources.py -q
.venv/bin/python -m pytest tests/fund/documents tests/fund/pdf/test_downloader.py -q
.venv/bin/python -m pytest tests/fund/audit/test_audit_programmatic.py tests/services/test_fund_analysis_service.py tests/ui/test_cli.py -q
.venv/bin/python -m pytest tests/ -q
.venv/bin/python -m ruff check .
git diff --check
```

No command should require live EID, Eastmoney, or akshare network.

## Risks

| Risk | Mitigation |
|---|---|
| Metadata class duplication creates drift | Move shared dataclass to `models.py`; `sources.py` imports it |
| Parsed cache hits hide whether result came from cache | Add cache provenance fields and set `parsed_cache_hit=True` on return |
| Legacy cache rows break after schema change | Add nullable column with `ALTER TABLE`; `from_dict()` accepts missing metadata |
| Cross-call metadata attachment under async concurrency | Use explicit immutable `AnnualReportPdfFetchResult` per call; forbid adapter-wide latest-metadata state |
| Documents row and parsed payload metadata diverge | Define `save_parsed_report(...)` metadata precedence and normalize the report before writing both stores |
| Force refresh keeps stale source metadata | Explicitly overwrite documents row and parsed payload on force refresh |
| Service/UI start depending on source details | Keep all changes in Fund document models/cache/repository; no upper-layer imports |
| Eastmoney fallback appears like EID | Persist `source="eastmoney"` and `fallback_used=True`; leave EID IDs null |

## Rollback

Rollback should be non-destructive:

1. Stop attaching source metadata in repository.
2. Keep nullable `source_metadata_json` column; it is harmless for old code.
3. `ParsedAnnualReport.from_dict()` should continue accepting payloads with or without metadata.
4. Restore `sources.py` local metadata only if needed, though preferred rollback is to keep shared model to avoid schema drift.

## Ready For Implementation

P7-S4 is ready for implementation after plan review. The implementation owner should stop at source metadata persistence and cache provenance inside Fund Capability; no Service/UI/Engine/CLI source awareness or live network tests are part of this slice.
