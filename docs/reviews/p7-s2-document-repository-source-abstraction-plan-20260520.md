# P7-S2 Document Repository Source Abstraction Plan - 2026-05-20

## Verdict

Implement P7-S2 as an internal Fund Capability refactor: introduce an annual-report source protocol and source orchestrator behind `FundDocumentRepository`, while preserving the public repository API and current behavior for callers.

P7-S2 must not implement the EID client. It should prepare the source boundary so P7-S3 can add EID as primary and keep Eastmoney/akshare as fallback without leaking source-specific details into Service/UI/Engine/CLI.

## Inputs

- `docs/reviews/p7-s1-eid-source-research-spike-plan-20260520.md`
- `docs/implementation-control-p4.md`
- `docs/design.md`
- `fund_agent/fund/documents/repository.py`
- `fund_agent/fund/documents/adapters/annual_report_pdf.py`
- `fund_agent/fund/documents/cache.py`
- `fund_agent/fund/documents/models.py`
- `fund_agent/fund/pdf/downloader.py`

## Problem Statement

Current code has the right upper boundary but the wrong lower-level extension point:

- Good: `FundDocumentRepository.load_annual_report(fund_code, year, *, force_refresh=False)` is already the only public annual-report read path.
- Good: Service/UI/Engine/CLI do not need to know where PDFs come from.
- Problem: `AnnualReportPdfAdapter.fetch_pdf_path(...)` directly calls `_download_annual_report_pdf`, which is currently Eastmoney/akshare-specific.
- Problem: there is no typed place to express source priority, fallback eligibility, timeout/retry policy, or source metadata.

P7-S2 should introduce that internal place without changing report parsing, extractor behavior, service orchestration, or user-facing CLI behavior.

## Non-goals

P7-S2 does not:

- Implement `validate_fund.do`, `advanced_search_report.do`, or `instance_show_pdf_id.do`.
- Add real EID network calls.
- Change `FundDocumentRepository.load_annual_report(...)` public signature.
- Change Service, UI, Engine, CLI, extraction, audit, quality gate, template renderer, or fund type logic.
- Change PDF parser behavior or annual-report section extraction.
- Add real-network tests.
- Put explicit parameters into `extra_payload`.
- Change cache schema unless strictly necessary for a tiny metadata placeholder.
- Make 巨潮 a public-fund annual-report primary source.

## Owned Files

Allowed implementation files for P7-S2:

| File | Action |
|---|---|
| `fund_agent/fund/documents/sources.py` | New internal source protocol, result model, config, errors, and orchestrator |
| `fund_agent/fund/documents/adapters/annual_report_pdf.py` | Replace direct downloader dependency with source orchestrator dependency |
| `fund_agent/fund/documents/repository.py` | Keep public signature unchanged; only adjust private typing/docstrings if needed |
| `fund_agent/fund/documents/models.py` | Optional tiny source metadata dataclass only if needed; avoid changing `ParsedAnnualReport` in P7-S2 unless tests justify |
| `fund_agent/fund/documents/cache.py` | Prefer no schema change; only add metadata no-op/placeholder if plan review requires it |
| `fund_agent/fund/pdf/downloader.py` | Keep as Eastmoney/akshare fallback helper; optional adapter wrapper only |
| `tests/fund/documents/test_annual_report_sources.py` | New focused tests for orchestrator/source protocol behavior |
| Existing document adapter/cache/repository tests | Update only if constructor injection or docstrings require it |
| `fund_agent/fund/README.md` | Update only to describe current source abstraction behavior after code changes |
| `tests/README.md` | Update only if new test module/category is added |
| `docs/reviews/p7-s2-implementation-20260520.md` | Implementation artifact for the next implementation gate |

Do not modify control docs in P7-S2 implementation.

## Protocol And Model Boundary

Add `fund_agent/fund/documents/sources.py`.

### Publicness

The new module is internal to Fund Capability. It may be imported by `AnnualReportPdfAdapter` and tests, but should not be exported as an application-level API.

`FundDocumentRepository` remains the stable public read interface.

### Core Types

Use dataclasses and Protocols with Chinese docstrings.

Recommended types:

```python
AnnualReportSourceName = Literal["eid", "eastmoney"]

class AnnualReportSourceUnavailableError(Exception): ...
class AnnualReportSourceNotFoundError(FileNotFoundError): ...
class AnnualReportSourceMismatchError(ValueError): ...
class AnnualReportSourceSchemaError(ValueError): ...
class AnnualReportSourceAggregateError(Exception): ...

@dataclass(frozen=True, slots=True)
class AnnualReportSourceConfig:
    metadata_timeout_seconds: float = 10.0
    pdf_timeout_seconds: float = 60.0
    retry_attempts: int = 2
    max_concurrency: int = 1

@dataclass(frozen=True, slots=True)
class AnnualReportSourceMetadata:
    source: AnnualReportSourceName
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
    fallback_used: bool = False

@dataclass(frozen=True, slots=True)
class AnnualReportSourceResult:
    pdf_path: Path
    metadata: AnnualReportSourceMetadata

class AnnualReportSource(Protocol):
    name: AnnualReportSourceName

    async def fetch_annual_report_pdf(
        self,
        fund_code: str,
        year: int,
        *,
        force_refresh: bool = False,
    ) -> AnnualReportSourceResult: ...
```

### Metadata Scope

P7-S2 only introduces metadata as a returned internal value. It should not over-implement persistence.

Recommended P7-S2 behavior:

- `AnnualReportSourceResult.metadata` exists and is testable.
- `AnnualReportPdfAdapter.fetch_pdf_path(...)` may store the latest metadata privately for future use only if needed.
- `ParsedAnnualReport` remains unchanged in P7-S2.
- Cache schema remains unchanged unless implementation shows a minimal compatibility-safe reason.

Rationale: P7-S3/P7-S4 can persist EID-specific metadata after the EID client proves real source fields and cache compatibility. P7-S2 should keep the refactor low-risk.

## Source Orchestrator

Add `AnnualReportSourceOrchestrator`.

Responsibilities:

- Receive ordered sources.
- Call each source with explicit `fund_code`, `year`, and `force_refresh`.
- Return first successful `AnnualReportSourceResult`.
- Convert fallback source metadata to `fallback_used=True` when any previous source was attempted and skipped.
- Aggregate source errors for diagnostics.
- Raise a final error that preserves source-failure categories when all sources are exhausted without a valid PDF.

Source priority for P7-S2:

```text
future default: EID primary -> Eastmoney/akshare fallback
P7-S2 code default: Eastmoney/akshare only, unless a fake/test EID source is injected
```

This preserves current production behavior while making P7-S3 a narrow addition.

## Fallback Error Categories

P7-S2 must make fallback semantics explicit before EID implementation.

Fallback-eligible errors:

- `AnnualReportSourceUnavailableError`: network timeout, HTTP 5xx, rate limit, transient source outage.
- `AnnualReportSourceNotFoundError`: source has no candidate for the requested fund/year.
- Existing `FileNotFoundError` from the Eastmoney/akshare helper should be treated as not-found when wrapping that source.

Fail-closed, not fallback-eligible by default:

- `AnnualReportSourceMismatchError`: source returned a contradictory fund code, report year, report type, or non-PDF candidate.
- `AnnualReportSourceSchemaError`: source response shape is missing required fields or cannot be parsed.
- `ValueError` from validation of explicit inputs.

Orchestrator behavior:

- If a fallback-eligible error occurs, try next source.
- If a fail-closed error occurs, stop and raise it.
- If all exhausted source failures are `AnnualReportSourceNotFoundError`, raise `FileNotFoundError` / `AnnualReportSourceNotFoundError` with a concise message that includes source names.
- If any exhausted source failure is `AnnualReportSourceUnavailableError` and no source succeeded, do not collapse the result into not-found. Raise `AnnualReportSourceUnavailableError` or an explicit `AnnualReportSourceAggregateError` that preserves per-source categories.
- Mixed not-found/unavailable failures must preserve the unavailable category in the final exception so callers can distinguish “official source temporarily unavailable” from “no annual report exists”.

P7-S2 tests should pin this state machine with fake sources.

## Eastmoney/Akshare Wrapper

Add an internal `EastmoneyAnnualReportSource` in `sources.py` or a small `documents/adapters/eastmoney_source.py`.

Recommended simpler P7-S2 implementation:

- Keep `_download_annual_report_pdf(...)` in `fund_agent/fund/pdf/downloader.py`.
- Wrap it in `EastmoneyAnnualReportSource.fetch_annual_report_pdf(...)`.
- Return metadata:

```text
source="eastmoney"
fund_code=<requested>
report_year=<requested>
fallback_used=<set by orchestrator if not first source>
```

Do not rewrite the akshare query or Eastmoney URL logic in P7-S2.

## AnnualReportPdfAdapter Changes

Current constructor:

```python
def __init__(
    self,
    downloader: AnnualReportDownloader = _download_annual_report_pdf,
    text_extractor: TextExtractor = extract_text,
    table_extractor: TableExtractor = extract_tables,
    section_locator: SectionLocator = locate_sections,
) -> None:
```

Recommended P7-S2 constructor:

```python
def __init__(
    self,
    source_orchestrator: AnnualReportSourceOrchestrator | None = None,
    text_extractor: TextExtractor = extract_text,
    table_extractor: TableExtractor = extract_tables,
    section_locator: SectionLocator = locate_sections,
) -> None:
```

Compatibility note:

- Existing tests may inject a downloader callable. P7-S2 can either update tests to inject a fake source/orchestrator, or temporarily support `downloader` as an internal compatibility parameter if many tests depend on it.
- Prefer updating tests to the new source abstraction because this is an internal API and the project does not require historical compatibility.

`fetch_pdf_path(...)` should call:

```python
result = await self._source_orchestrator.fetch_annual_report_pdf(
    fund_code,
    year,
    force_refresh=force_refresh,
)
return result.pdf_path
```

`parse_pdf(...)` should remain unchanged.

## Repository And Cache Behavior

`FundDocumentRepository.load_annual_report(...)` behavior must remain:

- Validate fund code and year.
- If loader is cache-aware and `force_refresh=False`, first try parsed report cache.
- If no parsed report cache and `force_refresh=False`, try cached PDF path.
- If no cached PDF path or `force_refresh=True`, call loader `fetch_pdf_path(...)`.
- Parse PDF.
- Save parsed report and PDF path.
- Return `ParsedAnnualReport`.

P7-S2 should not change these semantics.

`force_refresh` semantics with source abstraction:

- `force_refresh=False`:
  - repository may reuse parsed report cache.
  - repository may reuse cached PDF path.
  - source orchestrator is not called if cache hits.
- `force_refresh=True`:
  - repository skips parsed report cache and PDF path cache.
  - source orchestrator receives `force_refresh=True`.
  - source implementations must bypass their own local cached file if they manage one.

Cache schema:

- Prefer no schema migration in P7-S2.
- Existing `documents` SQLite stores `document_key`, `fund_code`, `year`, `document_kind`, `pdf_path`, `updated_at`.
- Existing `parsed_reports` schema remains valid.
- Source metadata persistence is deferred to P7-S4 unless P7-S2 implementation needs a tiny backward-compatible placeholder. If added, it must be nullable and older cache rows must remain readable.

## Timeout And Retry Configuration

P7-S2 should define configuration but only exercise it through fake sources.

Recommended location:

- `AnnualReportSourceConfig` in `fund_agent/fund/documents/sources.py`.
- `AnnualReportSourceOrchestrator(config=AnnualReportSourceConfig())`.
- Future EID source will consume `metadata_timeout_seconds`, `pdf_timeout_seconds`, `retry_attempts`, and `max_concurrency`.

P7-S2 should not add environment-variable or CLI configuration. That would leak source concerns upward before the EID implementation exists.

## Dependency Direction

Allowed dependencies:

```text
FundDocumentRepository
  -> AnnualReportPdfAdapter
  -> AnnualReportSourceOrchestrator
  -> AnnualReportSource implementations
  -> fund_agent.fund.pdf.downloader Eastmoney helper
```

Forbidden dependencies:

- Service/UI/Engine/CLI importing `documents.sources`.
- Source implementations importing Service/UI/Engine/CLI.
- Quality gate, audit, template, or extraction modules importing concrete EID/Eastmoney source classes.
- Any explicit source configuration stored in `extra_payload`.

## File-Level Implementation Plan

### 1. Add `fund_agent/fund/documents/sources.py`

Implement:

- source error classes
- `AnnualReportSourceName`
- `AnnualReportSourceConfig`
- `AnnualReportSourceMetadata`
- `AnnualReportSourceResult`
- `AnnualReportSource` Protocol
- `EastmoneyAnnualReportSource`
- `AnnualReportSourceOrchestrator`

All classes/functions need Chinese docstrings with Args/Returns/Raises where applicable.

Orchestrator should have focused private helpers only if needed; avoid nested functions.

### 2. Update `annual_report_pdf.py`

Replace direct downloader dependency with `AnnualReportSourceOrchestrator`.

Keep:

- text extraction
- table extraction
- section locating
- `ParsedAnnualReport` construction

Do not modify parser logic.

### 3. Update `repository.py`

Prefer no behavior change.

Only update docstrings/private typing if the loader protocol references source-backed fetch semantics.

### 4. Keep `cache.py` unchanged unless necessary

Do not add metadata persistence in P7-S2 unless implementation tests expose an unavoidable need.

### 5. Keep `models.py` unchanged unless necessary

If metadata must be modeled outside `sources.py`, add a tiny independent dataclass and do not attach it to `ParsedAnnualReport` yet.

### 6. Keep `pdf/downloader.py` behavior unchanged

The existing Eastmoney/akshare helper remains fallback implementation.

Do not rewrite `_find_annual_report_id(...)` in P7-S2.

## Mock-Network Test Plan

Add `tests/fund/documents/test_annual_report_sources.py`.

Tests must use fake source objects and temporary local PDF paths. They must not call EID, Eastmoney, akshare, or real PDF network.

Required tests:

1. `test_orchestrator_returns_first_successful_source`
   - fake primary returns `AnnualReportSourceResult`
   - fallback is not called

2. `test_orchestrator_falls_back_after_unavailable_error`
   - primary raises `AnnualReportSourceUnavailableError`
   - fallback returns result
   - returned metadata has `fallback_used=True`

3. `test_orchestrator_falls_back_after_not_found_error`
   - primary raises `AnnualReportSourceNotFoundError`
   - fallback returns result

4. `test_orchestrator_stops_on_mismatch_error`
   - primary raises `AnnualReportSourceMismatchError`
   - fallback is not called

5. `test_orchestrator_stops_on_schema_error`
   - primary raises `AnnualReportSourceSchemaError`
   - fallback is not called

6. `test_orchestrator_raises_file_not_found_when_all_sources_are_not_found`
   - all sources raise `AnnualReportSourceNotFoundError`
   - final exception is `FileNotFoundError` / `AnnualReportSourceNotFoundError`
   - final exception message includes source names

7. `test_orchestrator_unavailable_exhaustion_is_not_file_not_found`
   - all sources raise `AnnualReportSourceUnavailableError`
   - final exception is `AnnualReportSourceUnavailableError` or `AnnualReportSourceAggregateError`
   - final exception is not `FileNotFoundError`

8. `test_orchestrator_mixed_not_found_and_unavailable_preserves_unavailable_category`
   - one source raises `AnnualReportSourceNotFoundError`
   - another source raises `AnnualReportSourceUnavailableError`
   - final exception preserves the unavailable category and is not reported as plain not-found

9. `test_orchestrator_passes_force_refresh_to_source`
   - fake source records `force_refresh=True`

10. `test_annual_report_pdf_adapter_fetch_pdf_path_uses_source_orchestrator`
   - adapter receives fake orchestrator
   - returned `Path` is the source result path

11. `test_repository_cache_hit_does_not_call_source_orchestrator`
   - use fake cache/loader or existing repository injection pattern
   - when parsed report cache hits, source is not called

12. `test_repository_force_refresh_calls_source_even_with_cache`
    - proves existing force refresh semantics remain intact

If tests 11-12 are too coupled to cache internals, keep them in existing repository/cache tests and use fake cache-aware loader to assert call sequence.

Update existing tests only where constructor injection changes.

## README Sync

P7-S2 modifies `fund_agent/fund/` and adds tests, so implementation should update:

- `fund_agent/fund/README.md`
- `tests/README.md`

README content should describe current implementation only:

- Fund document repository remains the only public annual-report read entry.
- Annual-report PDF acquisition is internally source-backed.
- Current production source remains Eastmoney/akshare until P7-S3 adds EID.
- Source priority/fallback is internal to documents layer.
- Tests use fake sources and do not hit real EID.

Do not write future promises beyond the next accepted implementation.

## Acceptance Commands

P7-S2 implementation should run:

```bash
.venv/bin/python -m pytest tests/fund/documents/test_annual_report_sources.py -q
.venv/bin/python -m pytest tests/fund/documents tests/fund/pdf/test_downloader.py -q
.venv/bin/python -m pytest tests/fund/audit/test_audit_programmatic.py tests/services/test_fund_analysis_service.py tests/ui/test_cli.py -q
.venv/bin/python -m pytest tests/ -q
.venv/bin/python -m ruff check .
git diff --check
```

If a listed path does not exist, implementation should report that fact and run the nearest existing focused tests.

## Risks

| Risk | Mitigation |
|---|---|
| Refactor accidentally changes repository public behavior | Keep `FundDocumentRepository.load_annual_report` signature and cache sequence unchanged; add fake tests |
| Fallback masks official mismatch in P7-S3 | Define fail-closed error categories now; mismatch/schema errors stop fallback |
| Metadata overreach causes cache migration churn | Keep metadata internal and non-persistent in P7-S2 |
| Existing downloader tests depend on direct callable injection | Update tests to fake source/orchestrator; avoid compatibility shim unless needed |
| Timeout/retry config is defined but unused | Document that P7-S2 only owns config boundary; P7-S3 EID source consumes it |
| Source classes leak into Service/UI | Keep imports under `fund_agent/fund/documents`; grep in review |
| Real network sneaks into tests | All source tests use fakes/tmp paths; no EID/Eastmoney/akshare calls |

## Rollback

Rollback path:

1. Revert `AnnualReportPdfAdapter` to direct `_download_annual_report_pdf` injection.
2. Remove `documents/sources.py` and source tests.
3. Keep repository/cache/models unchanged.

Because P7-S2 does not change the public repository API or cache schema, rollback should not require data migration.

## Ready For Implementation

P7-S2 is ready for implementation when this plan is accepted by controller review. The implementation owner should stop at the source abstraction and fake-test coverage; EID client implementation belongs to P7-S3.
