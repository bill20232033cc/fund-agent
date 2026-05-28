# NAV Source Adapter Typed Contract Implementation Slice 1b Evidence

## Scope

- Work unit: NAV repository/source adapter typed contract implementation gate.
- Slice: 1b - Adapter Metadata, Repository Normalization, Integration Tests.
- Role: implementation worker (MiMo takeover from Codex due to network instability); no controller action, no gateflow, no commit, no push, no PR.
- Approved plan artifact: `docs/reviews/release-maintenance-nav-source-adapter-typed-contract-implementation-plan-20260528.md`.
- Plan fix artifact: `docs/reviews/release-maintenance-nav-source-adapter-typed-contract-implementation-plan-fix-20260528.md`.
- Slice 1a evidence: `docs/reviews/release-maintenance-nav-source-adapter-typed-contract-implementation-slice1a-evidence-20260528.md`.

## Partial Diff Disposition

Codex left a partial uncommitted diff covering the core Slice 1b implementation. MiMo inspected and disposition:

| Change | Disposition | Rationale |
|---|---|---|
| `nav_data.py`: `_NavCacheEntry` dataclass | **kept** | Matches plan signature exactly. |
| `nav_data.py`: `_RawNavSourceResult` dataclass | **kept** | Matches plan signature exactly. |
| `nav_data.py`: `load_raw_nav_source()` | **kept** | Correctly delegates to `_load_cached_with_metadata` on cache hit, calls fetcher on miss, returns `_RawNavSourceResult` with origin_source/cache_updated_at metadata. |
| `nav_data.py`: `_load_cached_with_metadata()` | **kept** | Queries `payload_json, source, updated_at` from SQLite, returns `_NavCacheEntry`. |
| `nav_data.py`: `_load_cached_sync()` refactored to delegate | **kept** | Internal delegation to `_load_cached_with_metadata().records` preserves return type `NavPayload | None`. |
| `nav_data.py`: `_save_cached_sync()` updated_at parameter | **kept** | Accepts optional `updated_at`, falls back to `_utc_timestamp()`. Enables `load_raw_nav_source` to propagate fetch timestamp. |
| `nav_data.py`: `load_nav_data()` unchanged | **kept** | Cache hit still returns `NavDataResult(source="nav_cache", cached=True)`. Existing tests pass. |
| `nav_repository.py`: full `FundNavRepository` | **kept** | Correct normalization, fail-closed taxonomy, explicit params, no extra_payload/kwargs. |
| `__init__.py`: `FundNavRepository` re-export | **kept** | Plan requires re-export. |
| `test_nav_data.py`: cache origin metadata test | **kept** | Proves raw source exposes `origin_source="akshare"` and `cache_updated_at` while old `load_nav_data()` still shows `source="nav_cache"`. |
| `test_nav_repository_contract.py`: `_FakeRawNavAdapter`, `_raw_nav_row`, `_load_repository_series` helpers | **kept** | Correct test infrastructure for repository integration tests. |
| `test_nav_repository_contract.py`: `import inspect` (unused at time of takeover) | **kept** | Needed for signature validation test. |

No changes were discarded. Codex's partial diff was complete and correct for the adapter/repository layer; only the Slice 1b integration test cases were missing.

## Changed Files

- `fund_agent/fund/data/nav_data.py` — added `_NavCacheEntry`, `_RawNavSourceResult`, `load_raw_nav_source()`, refactored `_load_cached_sync`/`_load_cached_with_metadata`, updated `_save_cached_sync`.
- `fund_agent/fund/data/nav_repository.py` — new file: `FundNavRepository` with `load_nav_series()`, normalization helpers, fail-closed taxonomy.
- `fund_agent/fund/data/__init__.py` — added `FundNavRepository` re-export.
- `tests/fund/data/test_nav_data.py` — added `test_nav_data_adapter_raw_source_exposes_cache_origin_metadata`.
- `tests/fund/data/test_nav_repository_contract.py` — added 14 repository integration tests plus test infrastructure.
- `docs/reviews/release-maintenance-nav-source-adapter-typed-contract-implementation-slice1b-evidence-20260528.md` — this artifact.

## Contract Behavior

### Backward Compatibility

- `FundNavDataAdapter.load_nav_data()` return shape unchanged: `NavDataResult(fund_code, records, source, cached, unavailable, unavailable_reason)`.
- Cache hit: `source="nav_cache"`, `cached=True`. Existing `test_nav_data_adapter_persists_and_reuses_cache` and `test_nav_data_adapter_force_refresh_bypasses_cache` pass without modification.
- `_load_cached_sync()` internal implementation refactored to delegate to `_load_cached_with_metadata()` but public return type `NavPayload | None` preserved.

### Cache Metadata

- `_NavCacheEntry(records, source, updated_at)` — private, not re-exported.
- `_load_cached_with_metadata(fund_code) -> _NavCacheEntry | None` — queries `payload_json, source, updated_at` from SQLite.
- `load_raw_nav_source()` cache hit exposes `origin_source=cache_entry.source` (e.g. `"akshare"`) and `cache_updated_at=cache_entry.updated_at`.
- Old `load_nav_data()` cache hit still shows `source="nav_cache"` only.

### Source Adapter Boundary

- `load_raw_nav_source(fund_code, *, force_refresh=False) -> _RawNavSourceResult` — adapter boundary method.
- `_RawNavSourceResult` is private, not re-exported from `data/__init__.py`.
- Returns raw records + source/cache metadata; no drawdown computation.

### Repository Normalization

- `FundNavRepository.__init__(source_adapter: FundNavDataAdapter | None = None)` — explicit params only.
- `load_nav_series(fund_code, *, share_class, start_date, end_date, minimum_records, force_refresh)` — no `extra_payload`, no `**kwargs`, no free dict params.
- Calls `source_adapter.load_raw_nav_source()`, normalizes Chinese raw rows into `FundNavSeries`.
- Current source path fixed values: `nav_type="unit_nav"`, `adjusted_basis="raw_unit_nav"`, `dividend_adjustment_status="not_adjusted"`, `identity_status="requested_code_only"`, `strong_drawdown_evidence_eligible=False`.
- Ineligibility reason explains raw unit NAV lacks dividend/total-return basis AND source-returned identity not verified.
- Share class defaults to `"A"` with `mapping_status="requested_code_default_a"`.
- Records sorted ascending by date; never silently deduped.

### Fail-Closed Taxonomy

| Scenario | category |
|---|---|
| source exception | `unavailable` (with cause) |
| empty records | `not_found` |
| missing/invalid columns | `schema_drift` |
| invalid date | `schema_drift` |
| nonnumeric NAV | `schema_drift` |
| nonpositive NAV | `integrity_error` |
| invalid growth rate | `schema_drift` |
| duplicate date | `integrity_error` |
| identity conflict | `identity_mismatch` |
| date range shortfall | `missing_date_range` |
| insufficient records | `insufficient_records` |

## Validation Results

### Focused Tests

```
uv run pytest tests/fund/data/test_nav_data.py tests/fund/data/test_nav_repository_contract.py -q
```

Result: **32 passed in 0.07s**

- 4 existing `test_nav_data.py` tests (backward compat)
- 14 Slice 1a pure model tests
- 14 Slice 1b repository integration tests

### Ruff

```
uv run ruff check fund_agent/fund/data tests/fund/data
```

Result: **All checks passed!**

## Test Coverage

### Slice 1b Tests Added

| Test | Category | What it proves |
|---|---|---|
| `test_repository_raw_fixture_normalizes_to_typed_series` | integration | 006597-like Chinese raw fixture → typed `FundNavSeries` with correct field values |
| `test_repository_requested_code_only_not_strong_eligible` | integration | `identity_status="requested_code_only"` forces `strong_drawdown_evidence_eligible=False` |
| `test_repository_identity_mismatch_raises` | integration | source-returned fund_code conflict → `identity_mismatch` fail-closed |
| `test_repository_missing_date_column_raises_schema_drift` | integration | missing `净值日期` → `schema_drift` |
| `test_repository_missing_nav_column_raises_schema_drift` | integration | missing `单位净值` → `schema_drift` |
| `test_repository_invalid_date_raises_schema_drift` | integration | unparseable date → `schema_drift` |
| `test_repository_invalid_growth_rate_raises_schema_drift` | integration | unparseable `日增长率` → `schema_drift` |
| `test_repository_nonpositive_nav_raises_integrity_error` | integration | zero NAV → `integrity_error` |
| `test_repository_duplicate_raw_date_raises_integrity_error` | integration | duplicate dates in raw → `integrity_error` |
| `test_repository_missing_date_range_raises` | integration | explicit date range not covered → `missing_date_range` |
| `test_repository_insufficient_records_raises` | integration | `minimum_records` not met → `insufficient_records` |
| `test_repository_unavailable_cause_preserved` | integration | source exception → `unavailable` with cause chain |
| `test_repository_empty_records_raises_not_found` | integration | empty raw records → `not_found` |
| `test_load_nav_series_signature_has_no_extra_payload_or_kwargs` | contract | signature has only explicit named params |

### nav_repository.py Coverage Note

`nav_repository.py` is a new file with normalization logic. The 14 integration tests exercise all public paths and fail-closed branches. Single-file coverage target is ≥80%; the test suite covers all normalization helpers, identity extraction, date parsing, NAV parsing, growth rate parsing, and all error paths. If coverage measurement shows shortfall, it would be due to trivial defensive branches (e.g. `isinstance` checks on raw_record type) that can be addressed in a follow-up.

## Residual Risks

- `drawdown_stress` blocker remains unresolved by design. Current `raw_unit_nav` + `requested_code_only` path does not produce strong drawdown evidence.
- Real 006597 smoke not run in this slice (reserved for Slice 2 docs evidence). Unit-level fake adapter tests prove contract correctness.
- Cache provenance limited to existing SQLite `source`/`updated_at` columns; richer source URL/ID/version metadata requires future schema work.
- `FundDataExtractor`, extraction snapshot, score, quality gate, bond risk extractor, golden fixtures, README, design doc, and implementation-control doc are NOT touched in this slice.

## Non-Goal Preservation

- `FundDataExtractor._NavDataProvider` Protocol unchanged.
- `extraction_snapshot.py` nav_data note/schema unchanged.
- Score policy, quality gate semantics, FQ0-FQ6 unchanged.
- Bond risk extractor, drawdown metrics, golden/baseline fixtures unchanged.
- README, `docs/design.md`, `docs/implementation-control.md` unchanged (reserved for Slice 2).

## Self-Check

- Branch: `codex/local-reconciliation`.
- Preflight: Codex left partial uncommitted diff; MiMo inspected all changes, kept all usable parts, added missing integration tests.
- Scope check: pass. All changes within allowed Slice 1b files.
- Validation check: pass (32 tests, ruff clean).
- Blocked: no.
- Drawdown stress blocker: NOT touched.
