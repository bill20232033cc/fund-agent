# P3-S2 Code Review — MiMo

> **Reviewer**: MiMo
> **Date**: 2026-05-18
> **Gate**: P3-S2 code review
> **Scope**: Uncommitted P3-S2 thermometer adapter changes
> **Files reviewed**: `fund_agent/fund/data/thermometer.py`, `fund_agent/fund/data/__init__.py`, `tests/fund/data/test_thermometer.py`, `README.md`, `fund_agent/fund/README.md`, `tests/README.md`, `docs/implementation-control.md`, `docs/reviews/p3-s2-implementation-2026-05-18.md`

---

## Controller Corrections Reviewed

The controller made three rounds of corrections after the initial implementation:

1. **All-market degree layout** — Added `_degree_after_heading` for `全市场温度 ... 70°` layout; added fallback trend extraction.
2. **Index table robustness** — Added `_find_index_table_header` to skip preceding non-index tables; added `_parse_index_row` code-column fallback to name column; added `_remove_index_code` helper; expanded `_TREASURY_YIELD_LABELS` for `到期收益率` variant.
3. **Cache write resilience** — Wrapped `_save_snapshot` call in `except OSError: pass` so cache write failures do not convert a successful fetch/parse into an unavailable snapshot.

All corrections are correct, tested, and aligned with current public page structure.

---

## Findings

### F1 — INFO — Stale cache corruption path not covered by test

**File**: `tests/fund/data/test_thermometer.py:201–227`

`test_thermometer_adapter_uses_stale_cache_when_fetch_fails` rewrites the cache timestamp to simulate age, but does not test what happens when the stale cache file is malformed (e.g., corrupted JSON). In that scenario, `_load_cache_payload` returns `None`, so the stale fallback is skipped and the adapter returns `unavailable`. The code handles this correctly (no crash), but the behavior is untested. Note: the cache-write-failure test (`test_thermometer_adapter_returns_fetched_snapshot_when_cache_write_fails`) covers the OSError path for fresh fetch, but the corrupted-stale-cache fallback path is a separate scenario.

### F2 — INFO — Test name slightly misleading

**File**: `tests/fund/data/test_thermometer.py:201`

`test_thermometer_adapter_uses_stale_cache_when_fetch_fails` uses `force_refresh=True`, which means it bypasses the fresh cache check and goes straight to fetch. The name does not convey that this is specifically the force-refresh-stale-fallback path. Consider renaming to `test_thermometer_adapter_falls_back_to_stale_cache_on_force_refresh_fetch_failure` for precision.

### F3 — INFO — `_degree_after_heading` only matches `°`, not `℃`

**File**: `fund_agent/fund/data/thermometer.py:618`

The degree-match regex `([-+]?\d+(?:\.\d+)?)\s*°` only matches the degree sign `°` (U+00B0). If the page ever uses `℃` (U+2103), the match will fail. Low risk for current page, but worth noting for future page-structure drift.

### F4 — INFO — Non-atomic cache write

**File**: `fund_agent/fund/data/thermometer.py:279`

`_save_snapshot` writes the cache file directly via `write_text`. A process crash mid-write could leave a truncated file. On next load, `_load_cache_payload` would return `None` (JSON decode error), triggering a refetch — so no data loss, just a cache miss. Acceptable for MVP; atomic write (write-to-temp + rename) could be added later if needed.

### F5 — INFO — Relative cache root path

**File**: `fund_agent/fund/data/thermometer.py:21`

`THERMOMETER_CACHE_ROOT` is `Path("cache/thermometer")`, a relative path. This is fine when the caller provides an explicit `root_dir` (as tests do) or when the process runs from the project root. The P3-S2 scope intentionally defers CLI/Service integration, so the caller will be responsible for providing the correct path. Not a blocker.

---

## Open Questions

None. All findings are INFO-level and do not block acceptance.

---

## Verdict

**PASS**

No blocking findings. The implementation correctly satisfies the P3-S2 success signal ("能获取全市场和指数温度"), respects the Capability layer boundary (no UI/Service/Engine dependency), handles cache freshness/stale-fallback/unavailable semantics correctly, and is well-aligned with tests and documentation. Controller corrections for current page structure (degree layout, index table header detection, code-in-name-cell, treasury yield label variant, cache write resilience) are all correct and tested. The 5 INFO findings are minor gaps in test coverage and robustness that can be addressed in later slices.
