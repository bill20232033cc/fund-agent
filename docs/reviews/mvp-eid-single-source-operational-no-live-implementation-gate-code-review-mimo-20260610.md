# EID Single Source Operational No-Live Implementation Gate Code Review — AgentMiMo

Date: 2026-06-10

Gate: `EID Single Source Operational No-Live Implementation Gate`

Classification: `heavy`

Reviewer: AgentMiMo

## Verdict

`PASS`

All ten review criteria are satisfied. Implementation correctly enforces EID single-source policy with `fallback_enabled=false`, terminalizes `not_found`/`unavailable` in single-source mode, keeps `schema_drift`/`identity_mismatch`/`integrity_error` fail-closed, preserves `FundDocumentRepository` as the only production boundary, and rejects stale/Eastmoney/fallback/unknown-source cache entries under the current policy. No forbidden files, paths or actions were touched. No-live tests pass. One informational finding about dead code retention.

## Review Criteria Results

| # | Criterion | Result | Evidence |
|---|---|---|---|
| 1 | EID single-source with fallback_enabled=false | PASS | `sources.py:596` — default is `(EidAnnualReportSource(config=self.config),)`; `sources.py:602-603` — multi-source rejected with `ValueError`; `_build_eid_metadata` sets `selected_source="eid"`, `source_mode="single_source_only"`, `fallback_enabled=False` |
| 2 | Default production orchestration avoids Eastmoney/fund-company/CNINFO fallback | PASS | `sources.py:596` — only one EID source in default; Eastmoney class retained as deferred candidate docstring `sources.py:502-503` |
| 3 | `not_found`/`unavailable` terminal in single_source_only mode | PASS | Orchestrator loop at `sources.py:630-667`: eligible failures (`not_found`/`unavailable`) continue the loop, but with single source the loop exhausts → `_raise_exhausted_sources` at `sources.py:802-828` raises `AnnualReportSourceNotFoundError` or `AnnualReportSourceUnavailableError` (single failure). Tests `test_orchestrator_terminal_not_found_does_not_fallback` and `test_orchestrator_terminal_unavailable_does_not_fallback` verify terminal behavior. |
| 4 | `schema_drift`/`identity_mismatch`/`integrity_error` fail closed | PASS | Orchestrator calls `_raise_fallback_blocked` for these categories at `sources.py:651-660`. Tests verify `AnnualReportSourceFallbackBlockedError` with correct `failure.source`, `failure.category`, and `__cause__`. |
| 5 | `FundDocumentRepository` remains only production annual-report access boundary | PASS | `repository.py:349-368` — parsed cache policy check before return; `repository.py:368-378` — PDF cache policy check before reuse; adapter docstring aligned at `annual_report_pdf.py:170,185`. |
| 6 | UI, Service, Host, renderer, quality gate kept away from source/downloader/cache helpers | PASS | No files outside `fund_agent/fund/documents/` and its tests were modified. No imports of source/downloader/cache helpers added to upper layers. |
| 7 | Cache reuse rejects legacy/Eastmoney/fallback/metadata-less entries under current policy | PASS | `_is_current_eid_single_source_metadata` at `repository.py:264-282` returns `False` for `None` metadata, non-`"eid"` source, `fallback_used=True`, non-`None` `primary_failure_category`, non-`"eid"` `selected_source`, non-`"single_source_only"` `source_mode`, or non-`False` `fallback_enabled`. Tests `test_repository_legacy_pdf_cache_without_metadata_is_ignored`, `test_repository_rejects_parsed_cache_without_current_eid_policy`, `test_repository_rejects_eastmoney_fallback_pdf_cache` verify rejection. |
| 8 | Tests sufficient and no-live only | PASS | 72 targeted tests pass, 1338 broader tests pass (4 xfailed). All tests use `_FakeAnnualReportSource`, `httpx.MockTransport`, `_FakeMetadataAwareLoader`, temp dirs. No network/PDF/FDR/fallback/provider. |
| 9 | Avoided downloader.py, provider/default/runtime/budget/config, extractor, fixture projection, source-like residue | PASS | `git diff --name-only` shows only 7 allowed files. No forbidden path (`fund_agent/tools/`, `scripts/`, `fund_agent/fund/pdf/downloader.py`, `fund_agent/fund/extractors/`, etc.) touched. |
| 10 | No overdesign, stale tests, or residual doc/control sync required | PASS with informational findings | See Findings below. |

## Findings

### F1 — Informational: `AnnualReportSourceAggregateError` dead code in single-source path

**File**: `fund_agent/fund/documents/sources.py:182, 828`

`AnnualReportSourceAggregateError` is still defined and referenced in `_raise_exhausted_sources` (line 828). In single-source mode, the mixed-failure / multiple-unavailable branch that raises this exception is unreachable from the default production orchestrator path because there is always exactly one source.

**Disposition**: Non-blocking. The class is retained as infrastructure for potential future multi-source scenarios. The code path is provably unreachable from `AnnualReportSourceOrchestrator(None)` since `len(self.sources) == 1` is enforced at construction time.

### F2 — Informational: Terminal behavior relies on loop exhaustion, not explicit single-source short-circuit

**File**: `fund_agent/fund/documents/sources.py:630-667`

For `not_found` and `unavailable`, the orchestrator still calls `_can_fallback_after_failure()` which returns `True`, then `continue` iterates past the only source, reaching `_raise_exhausted_sources()`. This is correct behavior but relies on "no more sources in the loop" rather than an explicit single-source terminal path.

**Disposition**: Non-blocking. The behavior is correct: the test suite verifies that `not_found` raises `AnnualReportSourceNotFoundError` and `unavailable` raises `AnnualReportSourceUnavailableError` in single-source mode. The `_raise_exhausted_sources` function correctly classifies single-failure exhaustion. A future refactor could add an explicit single-source short-circuit for clarity, but it is not required for correctness.

### F3 — Informational: `_optional_bool` string normalization is fail-closed

**File**: `fund_agent/fund/documents/models.py:324-346`

`_optional_bool` accepts `"true"/"1"` → `True` and `"false"/"0"` → `False`, and raises `ValueError` for all other non-None strings. This is correct for the fail-closed policy: legacy JSON payloads without `fallback_enabled` will have `None` (not `False`), which causes `_is_current_eid_single_source_metadata` to reject the entry.

**Disposition**: Non-blocking. Design is correct and consistent with the plan's "legacy metadata tolerant-to-None for deserialization, fail-closed for policy validation" contract.

## No-Live Validation Run

| Command | Result |
|---|---|
| `uv run ruff check fund_agent/fund/documents/models.py fund_agent/fund/documents/sources.py fund_agent/fund/documents/repository.py fund_agent/fund/documents/adapters/annual_report_pdf.py tests/fund/documents/test_annual_report_sources.py tests/fund/documents/test_cache.py tests/fund/documents/test_repository.py` | All checks passed! |
| `uv run pytest tests/fund/documents/test_annual_report_sources.py tests/fund/documents/test_cache.py tests/fund/documents/test_repository.py -q` | 72 passed in 0.75s |
| `uv run pytest tests/fund/ tests/services/ tests/ui/ -q` | 1338 passed, 4 xfailed in 2.46s |
| `git diff --check HEAD` | No whitespace errors |
| `git diff --name-only HEAD \| grep -E "^(fund_agent/tools/\|scripts/claude_mimo_simple)"` | No forbidden paths touched |

No live EID/network/PDF/FDR/fallback/provider/probe command was run.

## Scope / Forbidden-Action Check

| Check | Result |
|---|---|
| Modified files are within allowed set | PASS — 7 files: `adapters/annual_report_pdf.py`, `models.py`, `repository.py`, `sources.py`, `test_annual_report_sources.py`, `test_cache.py`, `test_repository.py` |
| No forbidden files touched (`fund_agent/tools/`, `scripts/`, `downloader.py`, `extractors/`, `render/`, etc.) | PASS |
| No forbidden actions (live EID, network, PDF, FDR, fallback, provider, stage, commit, push, PR) | PASS |
| No source-like residue imported or executed | PASS |
| No `dayu-agent`/`dayu.host`/`dayu.engine` dependency introduced | PASS |
| No `extra_payload` for explicit business parameters | PASS |
| No extractor, renderer, quality gate, fixture projection, golden/readiness change | PASS |
| No provider/default/runtime/budget/config change | PASS |
| Docs/control not modified in this gate (Slice 5 deferred to post-acceptance) | PASS |

## Implementation Slice Coverage

| Slice | Scope | Status |
|---|---|---|
| S1: EID-only source policy and terminal orchestration | Default sources EID-only, multi-source rejected, `not_found`/`unavailable` terminal, schema/mismatch/integrity fail-closed | Done |
| S2: Source metadata schema hardening | `selected_source`, `source_mode`, `fallback_enabled`, `discovery_contract_version` added to `AnnualReportSourceMetadata`, `_build_eid_metadata`, `to_dict`/`from_dict`, legacy tolerant | Done |
| S3: Repository/cache admissibility for EID-only policy | `_is_current_eid_single_source_metadata` helper, parsed cache and PDF cache policy gates, legacy/Eastmoney/fallback rejection tests | Done |
| S4: Adapter/default wiring and boundary regressions | Adapter docstring aligned, orchestrator source inventory verified as EID-only, repository boundary preserved | Done |
| S5: Documentation and control sync | Deferred to post-acceptance per plan. Not included in this implementation gate. | Not done (intentional) |

## Residuals / Doc Sync Notes

| Residual | Owner / Next Gate |
|---|---|
| No live EID proof | Separate live EID smoke gate, only if user explicitly authorizes live EID/network/PDF/FDR action. |
| `docs/design.md` and `docs/implementation-control.md` update | Slice 5 — post-acceptance doc sync. Must update `design.md` §6.1 source policy from "accepted target" to "current code fact" and `implementation-control.md` current gate/residual rows. |
| `fund_agent/fund/README.md` update | Slice 5 — document current EID-only production source policy in the documents section. |
| `AnnualReportSourceAggregateError` dead code | Non-blocking informational. Class retained for potential future multi-source. No action required in this gate. |
| Eastmoney wrapper integrity bug | Deferred future source-candidate/fallback-risk gate. Not production-reachable under EID-only default. |
| Legacy cache ignored may cause fresh EID fetch on first post-implementation run | Accepted operational consequence. No bulk migration. |
| Share-class / exact EID identity edge cases | Deferred to EID discovery/identity follow-up. |
