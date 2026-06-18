# Plan Re-Review: MVP LLM Run Progress And Timeout UX

## Gate / Role / Reviewed Target

- **Gate**: `MVP LLM run progress and timeout UX gate` (heavy)
- **Role**: plan re-review agent (MiMo)
- **Reviewed target**: `docs/reviews/mvp-llm-run-progress-timeout-ux-plan-20260602.md` (updated)
- **Fix evidence**: `docs/reviews/mvp-llm-run-progress-timeout-ux-plan-fix-evidence-20260602.md`
- **Prior review**: `docs/reviews/mvp-llm-run-progress-timeout-ux-plan-review-mimo-20260602.md`
- **Controller judgment**: `docs/reviews/mvp-llm-run-progress-timeout-ux-plan-review-controller-judgment-20260602.md`
- **Re-review date**: 2026-06-02

## Verdict

**PASS — no blocking plan findings remain.** All accepted required fixes are properly addressed. No new blocking findings were introduced.

## Accepted Finding Status

### DS F1 / MiMo F3 — Heartbeat lifecycle underspecified → FIXED

**Required**: explicit stop protocol, lock-protected state, post-terminal no-heartbeat guarantee, deterministic test interface.

**Plan now contains** (§Heartbeat Lifecycle, lines 131–147; §Slice P1 step 3, lines 279–289; §CLI tests heartbeat lifecycle, lines 376–377):

| Sub-requirement | Status | Plan location |
|---|---|---|
| `threading.Event` stop signal (`_stop_event`) | present | line 133 |
| CLI starts thread before Host run, stops/joins in `finally` | present | line 134 |
| Daemon as fallback only; correctness from `_stop_event.set()` + bounded `join()` | present | line 135 |
| One `threading.Lock` shared by event sink and heartbeat | present | line 136 |
| Lock-protected state enumerated: `_current_phase`, `_current_chapter_id`, `_current_attempt`, `_phase_started_monotonic`, `_last_heartbeat_monotonic`, `_terminal_emitted`, `_sink_failed` | present | lines 137–143 |
| Event sink acquires lock on state update; heartbeat acquires lock on state read | present | line 144 |
| Post-terminal guarantee: clear phase, set `_terminal_emitted=True`, set `_stop_event`, join thread before terminal line | present | line 145 |
| `_heartbeat_tick(now_monotonic: float | None = None) -> bool` deterministic test interface | present | line 146 |
| Test coverage: active-phase, throttle, stop-event, sink-failed, post-terminal suppression | present | line 376 |
| Lifecycle test: stop/join in `finally` path | present | line 377 |

**Assessment**: Fully fixed. The heartbeat lifecycle is now implementation-ready with a clear stop protocol, shared lock, post-terminal invariant, and deterministic test surface.

---

### DS F2 / MiMo F2 — event_sink failure semantics ambiguous → FIXED

**Required**: commit to CLI-owned no-raise sink; Host calls sink without catch/translation; test proving sink exceptions don't affect Host terminal state.

**Plan now contains** (§Architecture Decision 3, lines 191–195; §Slice P1 step 1, lines 260–261; §CLI tests reporter failure, line 374):

| Sub-requirement | Status | Plan location |
|---|---|---|
| CLI sink catches all formatter/write/state failures | present | line 195, 261 |
| Sets `_sink_failed=True`, suppresses further progress | present | line 195 |
| Does not affect Host terminal state, stdout, stderr final diagnostics, or exit code | present | line 195 |
| Host calls sink without catch/translation/wrap | present | line 260 |
| Required test: `test_event_sink_exception_does_not_affect_host_terminal_state` | present | line 374 |

**Assessment**: Fully fixed. The ownership boundary is unambiguous: CLI owns error containment, Host calls sink naked. The test requirement proves the invariant.

---

### DS F3 — event_sink integration point unspecified → FIXED

**Required**: specify exact Host insertion point; sink receives same committed event after append to `events`.

**Plan now contains** (§Architecture Decision 1, line 185; §Slice P1 step 1, lines 249–260; §Host tests, lines 337–338):

| Sub-requirement | Status | Plan location |
|---|---|---|
| Single Host-local commit helper (`_commit_event`) | present | line 249 |
| Order: construct safe event → append to `events` → call sink → continue | present | line 185, 250–253 |
| Helper used for all event types: RUN_STARTED, phase, diagnostic, COMPLETED, FAILED, CANCELLED | present | lines 254–259 |
| Test: sink sees same event object already in internal list | present | line 337 |
| Test: commit helper covers all existing event types | present | line 338 |

**Assessment**: Fully fixed. The insertion rule is precise and the ordering guarantee is explicit. Two new Host tests ensure the commit-before-sink invariant and full event-type coverage.

---

### MiMo F1 — Service test name mismatch → FIXED

**Required**: correct to `test_host_runner_records_llm_service_phase_events`; specify `analysis_core` ordering.

**Plan now contains** (§Service tests, lines 344–346):

| Sub-requirement | Status | Plan location |
|---|---|---|
| Correct test name `test_host_runner_records_llm_service_phase_events` | present | line 344 |
| `analysis_core` PHASE_STARTED/COMPLETED before writer events | present | line 345 |
| `analysis_core` is required, not optional, in happy-path test | present | line 345 |

**Assessment**: Fully fixed. Test name is corrected and `analysis_core` ordering is specified as required in the happy path.

---

### Non-blocking guidance incorporated → ALL ADDRESSED

| Guidance | Status | Evidence |
|---|---|---|
| DS F4: TTY simulation via module-level helper | incorporated | `_llm_progress_auto_enabled()` helper at line 79, 271; test monkeypatch guidance at line 353 |
| DS F5: `run_terminal` uses `HostRunResult.elapsed_ms` after `run_sync()` returns | incorporated | line 128 |
| MiMo F4/F5: concrete forced-progress assertions without overfitting | incorporated | lines 357–362 |
| MiMo F6: narrow `"key"` to `"api_key"`, `"secret_key"`, `"access_key"` | incorporated | lines 393–395; broad `"key"` removed |

**Assessment**: All non-blocking guidance incorporated without expanding scope.

---

## New Blocking Findings

**None.** No new blocking plan findings were introduced by the fix.

Verification of scope discipline:
- No provider timeout budget, retry, backoff, or prompt payload changes
- No chapter acceptance calibration or auditor rule relaxation
- No quality gate, final judgment, score-loop, golden/fixture/readiness/PR state changes
- No artifact-retention schema changes
- No external `dayu-agent`/`dayu.host`/`dayu.engine` dependency
- No Agent engine/tool-loop migration
- Heartbeat spec uses simple daemon thread + Event + Lock; no async runner, durable session, or cross-process cancel

## Residual Observations (non-blocking, no action required)

### R1 — `_heartbeat_tick()` lock contention with `typer.echo`

The heartbeat tick acquires the lock, reads state, and may call `typer.echo(..., err=True)` while holding the lock. If `typer.echo` blocks on stderr I/O (unlikely but possible with slow pipes), the event sink's state update would block. This is acceptable for MVP because stderr write latency is typically sub-millisecond, and the alternative (releasing the lock before echo) introduces a window where terminal state could change between read and write. Non-blocking.

### R2 — `_sink_failed` flag is fire-once

Once `_sink_failed=True`, all future progress is suppressed. This is correct fail-closed behavior but means a transient stderr write error (e.g., a single `BlockingIOError` on non-blocking stderr) permanently disables progress. Acceptable for MVP; a future gate could add retry if needed. Non-blocking.

### R3 — Host test for "all event types" coverage

The plan requires `test_run_sync_event_sink_called_for_all_existing_event_types`. This test must exercise `RUN_CANCELLED` which requires triggering a cancel token. The existing `test_runtime_runner.py` already has cancel tests, so the pattern exists. Non-blocking.

## Final Status Summary

| Finding | Status |
|---|---|
| DS F1 / MiMo F3: heartbeat lifecycle | **fixed** |
| DS F2 / MiMo F2: event_sink failure semantics | **fixed** |
| DS F3: event_sink integration point | **fixed** |
| MiMo F1: Service test name mismatch | **fixed** |
| Non-blocking guidance (DS F4/F5, MiMo F4/F5/F6) | **incorporated** |
| New blocking findings | **none** |

## Conclusion

The updated plan is implementation-ready. All accepted required fixes are properly addressed with concrete specifications, test requirements, and ordering guarantees. No scope expansion into provider budget, chapter acceptance, artifact schema, score/golden/readiness, or other prohibited areas. The implementation worker may proceed.
