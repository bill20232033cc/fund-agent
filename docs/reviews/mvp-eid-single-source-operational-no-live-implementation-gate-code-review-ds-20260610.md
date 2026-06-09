# EID Single Source Operational No-Live Implementation Gate — Code Review (AgentDS)

Date: 2026-06-10

Gate: `EID Single Source Operational No-Live Implementation Gate`

Classification: `heavy`

Reviewer: AgentDS (independent code review, no edit/commit/push/PR)

Evidence artifact under review: `docs/reviews/mvp-eid-single-source-operational-no-live-implementation-gate-implementation-evidence-20260610.md`

Planning checkpoint: `473eec3 gateflow: accept eid no-live implementation planning`

## Verdict

**PASS**

Zero blocking findings. The implementation correctly enforces EID single-source policy, terminalizes `not_found`/`unavailable`, keeps `schema_drift`/`identity_mismatch`/`integrity_error` fail-closed, rejects non-EID/legacy/fallback cache entries, and introduces no upper-layer bypass. Five non-blocking findings are recorded below.

---

## Scope / Forbidden-Action Check

| Check | Result |
|---|---|
| Forbidden files unmodified (`fund_agent/tools/`, `scripts/claude_mimo_simple.py`, `downloader.py`, extractor, UI, Service, Host, provider/runtime/config) | PASS |
| No live EID/network/PDF/FDR/fallback/provider probe | PASS |
| No `FundDocumentRepository` live acquisition | PASS |
| No stage/commit/push/PR/merge/release | PASS |
| No golden/readiness promotion | PASS |
| No fixture projection | PASS |
| No provider/default/runtime/budget/config change | PASS |

---

## No-Live Validation Run

| Command | Result |
|---|---|
| `git diff --check` | PASS (no output) |
| `uv run ruff check fund_agent/fund/documents tests/fund/documents/test_annual_report_sources.py tests/fund/documents/test_repository.py tests/fund/documents/test_cache.py` | All checks passed! |
| `uv run pytest tests/fund/documents/test_annual_report_sources.py tests/fund/documents/test_repository.py tests/fund/documents/test_cache.py -q` | 72 passed in 0.84s |
| `uv run pytest tests/fund/documents/test_annual_report_sources.py tests/fund/documents/test_repository.py tests/fund/documents/test_cache.py tests/fund/test_source_provenance.py tests/fund/test_report_quality_validation.py -q` | 118 passed in 0.53s |
| `uv run pytest tests/fund tests/services tests/ui -q` | 1338 passed, 4 xfailed in 2.48s |

All no-live validation passed. Zero regressions. The 4 xfailed tests are pre-existing and unrelated to this gate.

---

## Review Criteria Assessment

### C1: Is the implementation truly EID single-source with fallback_enabled=false?

**PASS.** `AnnualReportSourceOrchestrator(None)` constructs exactly one source: `EidAnnualReportSource` (`sources.py:596`). Multi-source tuples and empty tuples are rejected at construction time with `ValueError` (`sources.py:601-603`). `EastmoneyAnnualReportSource` is not connected to the production default path. The class remains in the module with a docstring marking it as a deferred future candidate (`sources.py:502-504`); it is only referenced in tests for direct unit testing of the wrapper itself (not via orchestrator).

### C2: Does default production orchestration avoid Eastmoney / fund-company / CNINFO fallback?

**PASS.** The default source set is exactly `(EidAnnualReportSource(config=self.config),)` (`sources.py:595-598`). No second source exists to fall back to. The loop in `fetch_annual_report_pdf` iterates over a single source; after any failure the loop terminates and `_raise_exhausted_sources` is called. The `_can_fallback_after_failure` helper still returns `True` for `not_found`/`unavailable` (see F1 below), but this is structurally harmless because there is no second source to advance to.

No Eastmoney, fund-company, CNINFO or other non-EID source is constructable from the default production path. `EastmoneyAnnualReportSource` is not imported or referenced in `repository.py`, `adapters/annual_report_pdf.py`, or `documents/__init__.py`.

### C3: Are not_found and unavailable terminal in single_source_only mode?

**PASS.** When the single EID source fails with `not_found`:
1. failure appended to `failures` list
2. `_can_fallback_after_failure("not_found")` returns `True` → `continue`
3. loop ends (only one source) → `_raise_exhausted_sources` called
4. `categories == {"not_found"}` → raises `AnnualReportSourceNotFoundError` (`sources.py:824-825`)

When the single EID source fails with `unavailable`:
1. Same flow → `categories == {"unavailable"}` and `len(failures) == 1` → raises `AnnualReportSourceUnavailableError` (`sources.py:826-827`)

Both paths are terminal and do not invoke Eastmoney or any other source. Tests confirm:
- `test_orchestrator_terminal_not_found_does_not_fallback` (`test_annual_report_sources.py:751`): asserts `AnnualReportSourceNotFoundError` raised, EID called exactly once
- `test_orchestrator_terminal_unavailable_does_not_fallback` (`test_annual_report_sources.py:990`): asserts `AnnualReportSourceUnavailableError` raised, EID called exactly once

### C4: Do schema_drift, identity_mismatch, integrity_error still fail closed?

**PASS.** These three categories immediately call `_raise_fallback_blocked` (`sources.py:649-660`) without checking `_can_fallback_after_failure`. Tests confirm:
- `test_orchestrator_does_not_fallback_after_eid_mismatch` (`test_annual_report_sources.py:783`): `AnnualReportSourceFallbackBlockedError` with `identity_mismatch`
- `test_orchestrator_stops_on_schema_error` (`test_annual_report_sources.py:1055`): fail-closed with `schema_drift`
- `test_orchestrator_stops_on_integrity_error` (`test_annual_report_sources.py:1083`): fail-closed with `integrity_error`

All three tests now use single-source orchestrator and verify the second source is never called (no fallback exists).

### C5: Does FundDocumentRepository remain the only production annual-report access boundary?

**PASS.** `FundDocumentRepository.load_annual_report()` is unchanged as the public entry point (`repository.py`). The repository delegates PDF acquisition to the injected loader/adapter, which internally uses the now-EID-only orchestrator. Public exports in `documents/__init__.py` are unchanged and expose only `FundDocumentRepository` and data models. No new public API exposes source, cache, or PDF internals.

### C6: Are UI, Service, Host, renderer, quality gate kept away from source/downloader/cache helpers?

**PASS.** No changes to any UI, Service, Host, renderer, or quality gate files. The diff is strictly limited to `fund_agent/fund/documents/` and test files. The `documents/__init__.py` public API surface is unchanged.

### C7: Does cache reuse reject legacy, Eastmoney, fallback, or metadata-less entries under current policy?

**PASS.** `_is_current_eid_single_source_metadata()` (`repository.py:158-182`) enforces a six-field check:
- `source == "eid"`
- `fallback_used is False`
- `primary_failure_category is None`
- `selected_source == "eid"`
- `source_mode == "single_source_only"`
- `fallback_enabled is False`

The helper returns `False` when metadata is `None` (`repository.py:174`).

Applied at two points:
- Parsed report cache hit (`repository.py:352-356`): cache ignored if metadata fails check
- PDF cache hit (`repository.py:371-375`): cache ignored if metadata fails check

Tests confirm all rejection scenarios:
- `test_repository_legacy_pdf_cache_without_metadata_is_ignored` (`test_repository.py:840`): legacy cache without metadata → `pdf_cache_hit is False`, fresh EID fetch triggered
- `test_repository_rejects_parsed_cache_without_current_eid_policy` (`test_repository.py:882`): parsed cache with `source_metadata=None` → ignored, fresh fetch
- `test_repository_rejects_eastmoney_fallback_pdf_cache` (`test_repository.py:928`): Eastmoney/fallback metadata → `pdf_cache_hit is False`

### C8: Are tests sufficient and no-live only?

**PASS.** All tests use fake sources, `httpx.MockTransport`, in-memory fakes, or `tmp_path`-based temporary caches. No test touches network, real EID endpoints, real PDF files, or real `FundDocumentRepository` live acquisition.

Test coverage by slice:
| Slice | Test file | Key assertions verified |
|---|---|---|
| S1 | `test_annual_report_sources.py` | default sources EID-only, multi-source rejected, not_found/unavailable terminal, schema/mismatch/integrity fail-closed |
| S2 | `test_cache.py`, `test_annual_report_sources.py` | EID metadata carries policy fields, metadata JSON round-trip, legacy metadata tolerant |
| S3 | `test_repository.py` | parsed cache admissibility, PDF cache admissibility, Eastmoney rejection, legacy rejection, force_refresh preserved |
| S4 | (covered by S1+S3) | default adapter/orchestrator EID-only, repository boundary preserved |

### C9: Did this gate avoid forbidden areas?

**PASS.** Confirmed:
- `fund_agent/fund/documents/downloader.py` — not modified
- `fund_agent/fund/pdf/parser.py` — not modified
- extractor modules — not modified
- provider/default/runtime/budget/config modules — not modified
- UI/Service/Host modules — not modified
- `fund_agent/tools/`, `scripts/claude_mimo_simple.py` — not in diff
- No live network/PDF/FDR/fallback/provider action
- No fixture projection
- No golden/readiness promotion

### C10: Overdesign, stale tests, or residual doc/control sync issues?

See findings below.

---

## Findings

### F1 (Medium — Naming Legacy): Fallback terminology survives in unreachable code paths

**Files:** `fund_agent/fund/documents/sources.py:640-667, 692-705, 752-828`

The orchestrator loop still calls `_can_fallback_after_failure()` which returns `True` for `not_found`/`unavailable` (`sources.py:692-705`). The `continue` after a `True` return advances to the next source — but there is no next source. The functions `_mark_fallback_used` (`sources.py:774`), `_raise_fallback_blocked` (`sources.py:752`), `_raise_exhausted_sources` (`sources.py:802`), and the `_FALLBACK_ELIGIBLE_CATEGORIES` constant (`sources.py:40`) all carry "fallback" naming despite fallback being structurally impossible in production.

Additionally, `_raise_exhausted_sources` line 828 (`raise AnnualReportSourceAggregateError`) and `_mark_fallback_used` line 774 are unreachable in single-source production mode. `AnnualReportSourceAggregateError` is imported in test file (`test_annual_report_sources.py:14`) but is not used in any test.

The plan §12 Slice 1 and §17 accept this as a deliberate choice: "Prefer new fail-closed exception. If retained for minimal churn, must be documented as legacy naming and reviewed as non-blocking only if no production fallback exists." Since no production fallback exists, this is **non-blocking**. However, the naming inconsistency creates a maintenance hazard: a future reader may misinterpret `_can_fallback_after_failure` returning `True` as evidence that fallback is still active.

**Recommendation:** Add a comment at `_can_fallback_after_failure` noting it is legacy naming retained for single-source structural safety. Consider renaming in a follow-up cleanup gate (not this one).

### F2 (Low — Dead Code): `_mark_fallback_used` is unreachable in production path

**File:** `fund_agent/fund/documents/sources.py:661-665`

```python
if failures:
    return _mark_fallback_used(
        result,
        primary_failure_category=failures[0].category,
    )
```

In single-source mode with exactly one source, if the source succeeds, `failures` is empty. If it fails, the loop terminates. The only way `failures` could be non-empty after a successful result is if a prior source had failed and a later source succeeded — which is impossible with one source. This is dead production code.

**Severity:** Low. No behavior impact. Retained for structural simplicity per accepted plan.

### F3 (Low — Doc Sync Deferred): Design/control still describe EID single-source as target, not code fact

**Files:** `docs/design.md:5-6`, `docs/implementation-control.md:9, 595`

Both truth documents still state EID single-source as "accepted target / not implemented code fact" or "future implementation direction." Per the accepted plan §12 Slice 5, documentation sync is intentionally deferred until code review and controller judgment accept this implementation. This is not a defect — it correctly follows the plan's sequencing. However, the implementation evidence artifact should explicitly note this deferral.

**Status:** Expected. Slice 5 will update docs after review acceptance.

### F4 (Info — Deferred Risk): EastmoneyAnnualReportSource retained in module

**File:** `fund_agent/fund/documents/sources.py:502-504`

`EastmoneyAnnualReportSource` class remains in `sources.py` with an updated docstring marking it as "deferred future source candidate." It is not imported or referenced in `repository.py`, `adapters/annual_report_pdf.py`, or `documents/__init__.py`. In tests, it is still imported (`test_annual_report_sources.py:17`) and used for two direct unit tests (`test_annual_report_sources.py:1288, 1330`) that test the wrapper itself, not orchestrator fallback behavior.

The Eastmoney integrity-classification finding from `docs/reviews/repo-review-20260609-165959.md` (where `ValueError` path can mask PDF integrity failure) remains unfixed. This is accepted per plan §2 and §17: "Do not fix or promote Eastmoney in this gate."

**Residual:** Eastmoney integrity bug remains in deferred code. Not production-reachable under EID-only default.

### F5 (Info — Test Coverage Gap): Multi-source failure-chain preservation no longer tested

**File:** `tests/fund/documents/test_annual_report_sources.py:1128-1129`

The old test `test_orchestrator_blocked_failure_preserves_prior_eligible_failures` has been replaced by `test_orchestrator_rejects_multi_source_failure_chain`, which only asserts that multi-source construction is rejected via `ValueError`. The prior behavior — where `AnnualReportSourceFallbackBlockedError` preserved a list of eligible failures before the blocking failure, and `AnnualReportSourceAggregateError` preserved mixed failure categories — is no longer tested.

This is intentional: in single-source mode, there can be no prior failures and no mixed categories. However, if multi-source construction is ever re-enabled, these behaviors would need separate regression tests.

**Residual:** Add to future fallback-reauthorization gate checklist: restore multi-source failure-chain preservation tests.

---

## Residuals / Doc Sync Notes

| Item | Status | Owner |
|---|---|---|
| Docs/control sync (Slice 5) | Deferred per plan — update `docs/design.md`, `docs/implementation-control.md`, `fund_agent/fund/README.md` after review/controller acceptance | Implementation worker |
| Live EID proof | Separate future gate requiring explicit user authorization | Future live EID smoke gate |
| Eastmoney integrity bug | Deferred; not production-reachable | Future source-candidate/fallback gate |
| Fallback naming legacy (F1) | Non-blocking; cleanup in follow-up if desired | Future cleanup gate |
| Dead code `_mark_fallback_used` (F2) | Harmless; retained for structural simplicity | — |
| Multi-source test gap (F5) | Regression risk if multi-source re-enabled | Future fallback-reauthorization gate |
| Row-shape contract decision gate | Queued/paused by steering; unrelated to this gate | — |

---

## Summary

The implementation is correct, minimal, and no-live. All ten review criteria pass. The five findings are non-blocking: two are naming/dead-code legacies accepted by the plan, one is deferred doc sync per plan sequencing, one is an accepted deferred risk, and one is a test coverage note for a hypothetical future re-expansion. No forbidden files were modified, no live actions were taken, and all no-live validation commands pass with zero regressions.

**Verdict: PASS**
