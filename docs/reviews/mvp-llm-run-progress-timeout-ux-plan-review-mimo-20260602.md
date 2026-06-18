# Independent Plan Review: MVP LLM Run Progress And Timeout UX

## Gate / Role / Reviewed Target

- **Gate**: `MVP LLM run progress and timeout UX gate` (heavy)
- **Role**: independent plan review agent (MiMo)
- **Reviewed target**: `docs/reviews/mvp-llm-run-progress-timeout-ux-plan-20260602.md`
- **Review date**: 2026-06-02
- **Source docs consulted**: AGENTS.md, docs/design.md, docs/implementation-control.md, docs/current-startup-packet.md, controller judgments for truth sync and artifact retention, plus direct code/test verification of all referenced file paths and line numbers

## Verdict

**PASS WITH REQUIRED PLAN FIXES**

The plan is substantially code-generation-ready. Code facts, architecture boundaries, non-goals, safety red lines, secret allowlists, and the validation matrix are all well-structured. However, three findings require plan fixes before implementation handoff: a test name mismatch, an ambiguous event_sink failure contract between Host and CLI, and underspecified heartbeat thread lifecycle semantics.

## Findings

### F1 — Test name mismatch for Service phase event test [Severity: HIGH | Type: correctness]

**Location**: Plan §Tests / Required Unit Tests / Service tests, line "Update `test_analyze_with_llm_host_context_records_phase_events`"

**Problem**: The actual test name in `tests/services/test_fund_analysis_service_llm.py` is `test_host_runner_records_llm_service_phase_events` (line 388). The plan references a non-existent test name. An implementation worker following the plan literally would fail to find the test to update.

**Evidence**: Verified via codebase search. The test at line 388 asserts PHASE_STARTED/PHASE_COMPLETED sequence for writer → auditor → final_assembly on a real `HostRuntimeRunner().run_sync()` wrapping `service.analyze_with_llm()` with `target_chapter_ids=(1,)`.

**Required fix**: Change the reference to `test_host_runner_records_llm_service_phase_events`. The update instruction should state: add `analysis_core` phase_started/phase_completed to the expected sequence, positioned before the writer phase events.

---

### F2 — Ambiguous event_sink failure contract between Host and CLI [Severity: HIGH | Type: design ambiguity]

**Location**: Plan §Implementation Slice / Slice P1 / Step 1 ("Add generic Host event sink"), and §Architecture And Boundary Decisions / Decision 1

**Problem**: The plan contains conflicting guidance on who owns sink failure behavior:

1. "If `event_sink` itself raises, fail closed as a UI/observer failure without leaking event payload. Preferred behavior: catch reporter exceptions in CLI reporter and avoid raising from the sink."
2. "Host should not swallow arbitrary sink failures unless the implementation defines and tests that behavior clearly."

Statement (1) implies CLI owns exception handling and Host should not catch. Statement (2) implies Host should not swallow but also doesn't say what Host should do if the sink raises. The implementation worker is left to choose between:

- Option A: Host wraps sink calls in try/except and silently drops (contradicts "Host should not swallow")
- Option B: Host lets sink exceptions propagate (would crash the run for a UI observer failure, contradicting fail-closed)
- Option C: Host catches and logs/re-raises as HostRuntimeError (changes terminal event semantics)
- Option D: CLI sink never raises (requires the CLI reporter to be fully self-contained in error handling)

The plan's "preferred behavior" hints at Option D but doesn't commit to it, and doesn't specify what test should prove this invariant.

**Required fix**: Commit to Option D explicitly: "The CLI reporter event_sink must catch all exceptions internally and never propagate to Host. Host calls the sink without try/except wrapping. The CLI test must prove that a sink exception does not change Host terminal event ordering or status." Add a test case: `test_event_sink_exception_does_not_affect_host_terminal_state`.

---

### F3 — Heartbeat thread lifecycle underspecified [Severity: MEDIUM | Type: design ambiguity]

**Location**: Plan §Implementation Slice / Slice P1 / Step 3 ("Add heartbeat without changing provider execution")

**Problem**: The plan says:

- "reporter starts a daemon thread only when progress is enabled and stops it after Host returns"
- "Heartbeat reads reporter state under a lock and prints `still_running` at most once every 30 seconds"
- "Tests must not sleep; inject or monkeypatch reporter clock/interval, or test reporter methods directly"

Three aspects are underspecified:

**F3a — Stop mechanism**: "Stops it after Host returns" does not specify how. A daemon thread will be killed on interpreter exit, but between `HostRuntimeRunner.run_sync()` returning and the CLI printing the final report/exit, the daemon thread could print a stale `still_running` line after `run_terminal`. The plan needs to specify: set a `_stop_event: threading.Event` before joining the thread (with a short timeout), or use a `_running: bool` flag checked under the same lock.

**F3b — Lock granularity**: "reads reporter state under a lock" — the plan should specify that the lock protects both the heartbeat state (current phase, elapsed_ms) and the stop flag, and that event_sink calls also acquire the same lock when updating state. Otherwise the heartbeat thread could read partially-updated state.

**F3c — Test strategy for heartbeat**: "Tests must not sleep; inject or monkeypatch reporter clock/interval" is correct but the plan should specify the testable interface: expose a `_heartbeat_tick()` method (or equivalent) that the test calls directly, bypassing the thread. The test then asserts that `_heartbeat_tick()` produces the expected `still_running` line and respects the 30-second throttle.

**Required fix**: Add a "Heartbeat lifecycle" subsection specifying:
1. A `threading.Event` stop signal, set before the thread is joined.
2. Lock scope: same lock for state reads/writes and stop check.
3. Post-terminal guarantee: no `still_running` line may be emitted after `run_terminal` has been printed.
4. Test interface: `_heartbeat_tick()` or equivalent for deterministic testing.

---

### F4 — `analysis_core` phase test impact ambiguity [Severity: LOW | Type: test completeness]

**Location**: Plan §Tests / Required Unit Tests / Service tests

**Problem**: The plan says "Update `test_host_runner_records_llm_service_phase_events` to include `analysis_core` before writer/auditor/final_assembly." But the `analysis_core` phase is described as "optional Service-level phase around the existing deterministic core inside `analyze_with_llm()`." The existing test at line 388 uses `target_chapter_ids=(1,)` which may skip `_run_analysis_core()` or run it very quickly. The plan should clarify whether the test should assert `analysis_core` presence unconditionally, or whether it's acceptable for `analysis_core` to be absent in test scenarios where `_run_analysis_core()` completes before the phase event can be recorded (e.g., due to timing).

**Suggested fix**: State explicitly: "The test must assert `analysis_core` phase_started and phase_completed appear in the event sequence. If `_run_analysis_core()` raises before phase_completed, the test should verify that the exception propagates and `analysis_core` phase_completed is absent (matching existing behavior for other phases)."

---

### F5 — Missing test for `--llm-progress` on successful run [Severity: LOW | Type: test completeness]

**Location**: Plan §Tests / Required Unit Tests / CLI tests / "Forced progress"

**Problem**: The plan describes "Forced progress" test: `runner.invoke(... ["analyze", "110011", "--use-llm", "--llm-progress"])` on a configured success fake. The assertion list includes `run_started`, `phase_started`, `phase_completed`, and `run_terminal`. However, it does not specify:

1. Whether `still_running` heartbeat lines should appear (since the test should inject a fast clock, likely no heartbeats fire).
2. Whether the `analysis_core` phase should be in the progress output.
3. The exact count of `phase_started` / `phase_completed` lines (one per phase? one per chapter?).

**Suggested fix**: Add: "Assert at least one `phase_started` and one `phase_completed` line. Assert `run_terminal` appears exactly once. Heartbeat lines may or may not appear depending on injected clock; do not assert their presence. If `analysis_core` is implemented, assert it appears before writer phases."

---

### F6 — Secret leakage assertion list includes `"key"` which is too broad [Severity: LOW | Type: safety concern]

**Location**: Plan §Tests / Required Unit Tests / Secret leakage negative assertions

**Problem**: The assertion list includes `"key"` as a forbidden substring in progress stderr. This is overly broad — the word "key" appears in legitimate contexts like `run_id` diagnostic keys, or in test descriptions. If the test literally asserts `"key" not in stderr_output`, it would false-positive on lines like `LLM progress: run_started run_id=host_run_abc123`.

However, checking the existing test at line 1951 in `test_cli.py`, the existing secret canary test already uses `"key"` and it passes today because the progress output doesn't exist yet. Once progress lines are added, `run_id=<value>` lines might contain substrings that match `"key"` in diagnostic key names.

**Suggested fix**: Replace `"key"` with more specific patterns: `"api_key"`, `"secret_key"`, `"access_key"`. The existing `build_safe_diagnostics()` already rejects keys containing `"api_key"` which is sufficient.

---

## Non-blocking Observations

### O1 — `event_sink` type export

The plan says "`fund_agent/host/__init__.py` only if a new public type alias is introduced." The `Callable[[HostRunEvent], None]` type alias would be useful for CLI import. The plan should state whether to export it as `HostEventSink = Callable[[HostRunEvent], None]` or let CLI use the raw `Callable` annotation. Non-blocking because the implementation worker can decide.

### O2 — Existing test `test_host_runner_records_llm_service_phase_events` needs `analysis_core` insertion

The existing test asserts writer → auditor → final_assembly sequence. Adding `analysis_core` before writer changes the expected sequence. The plan correctly flags this update but (per F1) uses the wrong test name. Once the name is fixed, the implementation worker should be aware that this test uses a real `HostRuntimeRunner` (not a fake), so the `analysis_core` phase event must actually be emitted by `analyze_with_llm()` for the test to pass.

### O3 — `TYPER` auto-completion for `--llm-progress/--no-llm-progress`

The plan uses Typer's `--llm-progress/--no-llm-progress` boolean flag pair. This follows the existing pattern of `--use-llm`. Non-blocking but the implementation worker should verify that Typer's `is_flag` behavior matches the desired `None` default (auto mode). Typer's `bool` with `--flag/--no-flag` defaults to `False`, not `None`. The implementation may need `typer.Option(None, "--llm-progress/--no-llm-progress")` or equivalent to get tri-state behavior.

### O4 — Progress output during quality gate block

The plan says "If progress is forced and Host starts before the block, progress lines may exist, but no `LLM Host run 未完成` fake-success/fake-incomplete line should appear." This is correct but the test boundary is fuzzy. The implementation worker should ensure that if Host has started and a quality gate block occurs (exit 2), the progress output includes `run_terminal` with `event=run_failed` and the existing quality gate stderr is preserved. The plan's existing assertion for this scenario is adequate.

### O5 — README sync for `--llm-progress`

The plan correctly identifies that root `README.md`, `fund_agent/host/README.md`, and `tests/README.md` need updates. Non-blocking, but the plan should note that the README update for the CLI option should follow the existing `--use-llm` documentation pattern.

### O6 — Heartbeat interval may be too long for short phases

30 seconds is appropriate for long-running provider calls but may mean no heartbeat fires during fast deterministic phases. This is acceptable UX — users won't notice silence during phases that complete in under 30 seconds. Non-blocking.

---

## Open Questions / Residual Risks

| Risk | Disposition | Notes |
|---|---|---|
| Heartbeat thread adds concurrency to a currently single-threaded CLI | Accepted residual; mitigate with daemon thread, stop event, lock, and deterministic test interface | Code review must verify no deadlocks or race conditions |
| `event_sink` type contract may evolve in future async Host runner | Accepted residual; current sync-only contract is sufficient for MVP | Future async Host gate may revisit |
| Progress output adds stderr noise that may interact with shell redirection or logging | Accepted residual; `--no-llm-progress` provides escape hatch | UX policy owner / controller |
| `analysis_core` phase label is broad and Service-owned | Acceptable per plan's Decision 2; do not expose fund internals | Implementation review must verify |
| Non-TTY default may surprise CI/CD users who expect progress | Intentional; `--llm-progress` forces on | Documented in README |

---

## Blocking Plan Findings

**Yes, blocking plan findings exist.** Three findings require plan fixes before implementation handoff:

1. **F1** (HIGH): Test name mismatch — fix the test reference from `test_analyze_with_llm_host_context_records_phase_events` to `test_host_runner_records_llm_service_phase_events`.
2. **F2** (HIGH): Ambiguous event_sink failure contract — commit to Option D (CLI sink never raises) and add a test proving sink exceptions don't affect Host terminal state.
3. **F3** (MEDIUM): Heartbeat thread lifecycle underspecified — add stop mechanism, lock scope, post-terminal guarantee, and testable interface specification.

F4, F5, and F6 are non-blocking improvements that the implementation worker can address during implementation without requiring a plan revision.

---

## Required Plan Fixes

| ID | Severity | Section | Fix |
|---|---|---|---|
| F1 | HIGH | Tests / Service tests | Change test name to `test_host_runner_records_llm_service_phase_events` (line 388) |
| F2 | HIGH | Implementation Slice / Step 1 | Commit to Option D: CLI sink catches all exceptions; Host calls sink without wrapping. Add test `test_event_sink_exception_does_not_affect_host_terminal_state` |
| F3 | MEDIUM | Implementation Slice / Step 3 | Add heartbeat lifecycle spec: `threading.Event` stop signal, lock scope, post-terminal guarantee, `_heartbeat_tick()` test interface |
| F6 | LOW | Tests / Secret leakage | Replace `"key"` with `"api_key"`, `"secret_key"`, `"access_key"` in negative assertion list |
