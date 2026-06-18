# Plan Re-Review: MVP LLM Run Progress And Timeout UX Gate

- **Gate**: `MVP LLM run progress and timeout UX gate` (classification: `heavy`)
- **Role**: independent plan re-review agent (AgentDS)
- **Re-reviewed target**: updated `docs/reviews/mvp-llm-run-progress-timeout-ux-plan-20260602.md`
- **Inputs**: plan fix evidence `docs/reviews/mvp-llm-run-progress-timeout-ux-plan-fix-evidence-20260602.md`, prior AgentDS review, controller judgment `docs/reviews/mvp-llm-run-progress-timeout-ux-plan-review-controller-judgment-20260602.md`
- **Re-review date**: 2026-06-02
- **Scope**: verify only the controller-accepted required fixes and non-blocking guidance; do not re-audit unchanged plan sections.

## Verdict: ALL ACCEPTED FIXES VERIFIED — PLAN IS CODE-GENERATION-READY

No new blocking findings introduced. All four controller-accepted required fixes are properly addressed. All five non-blocking guidance items are incorporated.

---

## Fix Verification

### Fix 1 — Heartbeat Lifecycle (DS F1 / MiMo F3): FIXED

**What was required:** explicit stop protocol with `threading.Event`, lock-protected state, post-terminal no-heartbeat guarantee, deterministic `_heartbeat_tick()` test interface.

**What the plan now specifies:**

| Requirement | Plan evidence |
|---|---|
| `threading.Event` stop signal | Line 133: "CLI reporter must own a `threading.Event` stop signal, for example `_stop_event`" |
| Lock-protected state fields | Lines 136-143: seven named fields under one `threading.Lock`: `_current_phase`, `_current_chapter_id`, `_current_attempt`, `_phase_started_monotonic`, `_last_heartbeat_monotonic`, `_terminal_emitted`, `_sink_failed` |
| CLI `try/finally` start/stop/join | Line 134: "must start the heartbeat thread immediately before entering the Host run and must stop and join it in a `finally` block around the Host run" |
| Daemon as fallback only | Line 135: "daemonized only as a final process-exit fallback; correctness must come from `_stop_event.set()` plus a bounded `join()` in `finally`" |
| Post-terminal no-heartbeat | Lines 144-145: "clear active phase state, set `_terminal_emitted=True`, set `_stop_event`, and join the heartbeat thread before printing or immediately around printing the terminal line. No `still_running` line may be emitted after `run_terminal`." |
| Deterministic test interface | Line 146: "`_heartbeat_tick(now_monotonic: float | None = None) -> bool`" with exact decision rules |
| Test coverage | Lines 376-377: deterministic heartbeat tests for active-phase, throttle, stop-event, sink-failed, post-terminal suppression |

**Edge case check:** The stop sequence has two call sites (terminal handling at line 144-145, `finally` at line 134). This is idempotent (`_stop_event.set()` is safe to call twice) and the `finally` block acts as a safety net if terminal handling is skipped (e.g. quality-gate exception path at line 295). No race condition introduced.

**Verdict: FIXED.** Thread contract is precise enough that implementation worker does not need to design locking or lifecycle.

---

### Fix 2 — event_sink Failure Semantics (DS F2 / MiMo F2): FIXED

**What was required:** commit to CLI-owned no-raise sink wrapper; Host calls sink without catch; sink failure doesn't affect run.

**What the plan now specifies:**

| Requirement | Plan evidence |
|---|---|
| CLI owns no-raise contract | Line 195: "CLI also owns the no-raise sink contract. The sink object passed to Host must catch all formatter/write/reporter exceptions internally, set `_sink_failed=True`, disable further progress output, and never propagate to Host." |
| Sink failure doesn't affect run | Line 195: "A progress formatting or stderr write failure must not change Host terminal state, LLM result handling, stdout behavior, or exit code." |
| Host doesn't catch | Line 260: "Host must not catch, swallow, translate, or wrap `event_sink` exceptions. Production CLI safety comes from the CLI-owned no-raise sink wrapper." |
| CLI reporter catches all | Lines 261: "The CLI reporter event sink must catch all exceptions from formatting, `typer.echo`, state updates, heartbeat coordination, or any other reporter code. On first reporter failure it must set `_sink_failed=True`, suppress all future progress output, and return `None`." |
| Test coverage | Line 374: `test_event_sink_exception_does_not_affect_host_terminal_state` |

**Verdict: FIXED.** No ambiguity remains. The contract is unilateral (CLI guarantees no-raise; Host trusts it) with test coverage proving terminal-state independence.

---

### Fix 3 — event_sink Integration Point (DS F3): FIXED

**What was required:** exact Host insertion point specifying append-then-sink order, single helper covering all event types.

**What the plan now specifies:**

| Requirement | Plan evidence |
|---|---|
| Single commit helper | Lines 249-254: "Implement a single Host-local commit helper, for example `_commit_event(events, event_type, run_id, event_sink, **diagnostics)`, with this exact order: construct the safe event via existing `_event(...)` → append it to `events` → call `event_sink(event)` if `event_sink is not None` → return the event" |
| Exact ordering | Line 185: "construct safe event -> append to `events` -> call sink -> continue run logic" |
| All event types covered | Lines 254-260: explicitly lists RUN_STARTED, phase/diagnostic events, RUN_COMPLETED, RUN_FAILED, RUN_CANCELLED |
| Test coverage | Lines 337-338: `test_run_sync_event_sink_called_after_event_is_committed` and `test_run_sync_event_sink_called_for_all_existing_event_types` |

**Verdict: FIXED.** The single-helper approach eliminates the risk of inconsistent insertion across 6+ call sites. The ordering rule (append then sink) ensures the internal event list is never stale when the sink fires.

---

### Fix 4 — Service Test Name (MiMo F1): FIXED

**What was required:** correct test name to `test_host_runner_records_llm_service_phase_events`; `analysis_core` ordering specified.

**What the plan now specifies:**

| Requirement | Plan evidence |
|---|---|
| Correct test name | Line 344: references `test_host_runner_records_llm_service_phase_events` |
| analysis_core before writer | Lines 344-345: "The expected sequence must assert `analysis_core` `PHASE_STARTED` and `PHASE_COMPLETED` appear before any writer phase event." |
| Required, not optional | Line 345: "In the existing happy-path test, `analysis_core` is required, not optional." |

**Verdict: FIXED.** Test name matches the actual test in the test suite. Ordering constraint is explicit.

---

## Non-blocking Guidance Verification

| Guidance | Status | Plan evidence |
|---|---|---|
| DS F4: TTY simulation mechanism | Incorporated | Line 79: `_llm_progress_auto_enabled()` module-level helper; line 271: test monkeypatch guidance; line 353: explicit test instruction |
| DS F5: terminal line source | Incorporated | Line 128: emitted after `run_sync()` returns, uses `HostRunResult.elapsed_ms`; line 129: explicit mapping RUN_COMPLETED→run_completed, etc. |
| MiMo F4/F5: assertion precision | Incorporated | Lines 357-361: one `run_started`, at least one phase_started/completed, exactly one `run_terminal`, no exact phase count, heartbeat optional |
| MiMo F6: secret canary narrowing | Incorporated | Lines 394-395: `secret_key`, `access_key` added; broad `key` removed; `api_key` retained |

---

## Regression Check

The following plan invariants remain intact after fixes:

- **Deterministic analyze/checklist** bypasses Host and progress code (lines 33, 266, 325).
- **Fail-closed semantics**: incomplete → exit 1, stdout empty (lines 89, 326, 363-366); Host failure → exit 1 (line 264).
- **Host business-agnostic**: no fund_code, report_year, chapter_policy, ExecutionContract, extra_payload (lines 183, 260-261, stop conditions 493-494).
- **Stderr-only**: stdout reserved for final report (lines 86-89).
- **Non-goals preserved**: no provider budget, retry, calibration, quality gate, score-loop, golden, artifact schema changes (lines 57-67).
- **Secret-safety**: allowlisted keys only, negative assertions include 17 canaries (lines 148-171, 389-405).
- **Stop conditions**: unchanged, correctly block scope creep (lines 486-498).
- **No dayu dependency** (lines 66-67, 495).
- **No artifact schema change** (lines 65, 201-203, 460-461).

---

## Minor Observation (Non-blocking)

### O1: heartbeat stop called in two places — ordering is correct but subtle

Lines 134 and 144-145 both specify heartbeat stop. Line 134 puts it in `finally`; line 144-145 puts it in terminal handling before printing `run_terminal`. The correct sequence is: `run_sync()` returns → terminal handling stops heartbeat → prints `run_terminal` → `finally` stop is no-op (idempotent). If quality-gate re-raise skips terminal handling (line 295), `finally` still stops the heartbeat. This is correct, but an implementation worker who reads only line 134 and puts ALL stop logic exclusively in `finally` would print `run_terminal` while the heartbeat thread is still running, violating line 145's guarantee. The fix evidence's implementation instructions (lines 285-287, 294-295) are clear enough to prevent this, but code review should verify the actual sequencing.

---

## Explicit Statement

**No blocking plan findings remain.** All four controller-accepted required fixes are properly addressed in the plan. No new blocking findings were introduced by the fixes. The plan is code-generation-ready for the implementation worker.

The plan may proceed to implementation gate after controller acceptance of this re-review.
