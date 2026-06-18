# Plan Review: MVP LLM Run Progress And Timeout UX Gate

- **Gate**: `MVP LLM run progress and timeout UX gate` (classification: `heavy`)
- **Role**: independent plan review agent (AgentDS)
- **Reviewed target**: `docs/reviews/mvp-llm-run-progress-timeout-ux-plan-20260602.md`
- **Review date**: 2026-06-02
- **Source of truth**: `AGENTS.md`, `docs/design.md`, `docs/implementation-control.md`, `docs/current-startup-packet.md`, accepted controller judgments, current code facts in `fund_agent/host/runtime.py`, `fund_agent/ui/cli.py`, `fund_agent/services/fund_analysis_service.py`, `fund_agent/services/chapter_orchestrator.py`, `tests/host/test_runtime_runner.py`

## Verdict: PASS WITH REQUIRED PLAN FIXES

Three required plan fixes before handoff to implementation. No structural redesign needed. The plan's architecture boundaries, non-goals, stop conditions, and secret-safety rules are sound. The issues below are specification gaps that would force the implementation worker to redesign on the fly.

---

## Assumptions Tested

1. Host `event_sink` integration is compatible with existing `_event_recorder` callback pattern.
2. Heartbeat daemon thread can be implemented narrowly without thread-safety redesign.
3. `event_sink` failure semantics are unambiguous for the implementation worker.
4. TTY detection and test simulation are specified clearly enough for implementation.
5. Chapter orchestrator phase events map cleanly to the proposed progress format.
6. `analysis_core` phase can be added around async `_run_analysis_core()` with sync Host context.

---

## Findings

### F1-REQUIRED-FIX-HIGH: heartbeat daemon thread design is underspecified

- **位置**: Implementation Slice P1, step 3 "Add heartbeat without changing provider execution" (lines 248-254)
- **问题类型**: 并发恢复风险 / 不可直接实施
- **当前写法**:
  > Acceptable implementation: reporter starts a daemon thread only when progress is enabled and stops it after Host returns.
  > Heartbeat reads reporter state under a lock and prints `still_running` at most once every 30 seconds.
  > If the implementation cannot add heartbeat narrowly without thread-safety risk, stop and return to controller.

- **反例/失败场景**:
  1. The plan delegates thread lifecycle to "starts a daemon thread … and stops it after Host returns." But `run_sync()` can raise via `HostRuntimeError` (cancel/deadline) or arbitrary operation exceptions. If the exception propagates before the `finally` block stops the daemon thread, the heartbeat continues running after the CLI exits or, worse, accesses freed reporter state.
  2. Python daemon threads are forcibly terminated on main thread exit. If the heartbeat thread holds `threading.Lock` at termination time, the lock is left in an undefined state — but since the process exits, this is only a problem if the reporter object is shared with non-daemon threads or signal handlers.
  3. The plan says "reads reporter state under a lock" but doesn't specify what state the heartbeat reads, what lock protects it, or whether the main thread also acquires this lock when updating phase state. Without this, the implementation worker must design the locking protocol from scratch.

- **为什么有问题**: The escape hatch ("stop and return to controller") proves the plan is not code-generation-ready for the thread component. It asks the implementation worker to either succeed at thread design or abort — but the plan should specify the thread contract so the worker doesn't need to design it.

- **直接证据**:
  - Plan lines 250-254: heartbeat described in 5 lines with no locking protocol, no stop protocol, no state specification.
  - `HostRuntimeRunner.run_sync()` (runtime.py:409) catches all exceptions as `except Exception` and returns `HostRunResult`, so exceptions from the operation don't propagate to the CLI's thread management code. But if the CLI starts a daemon thread before calling `run_sync()`, the CLI must stop it in a `finally` block regardless of what `run_sync()` returns.

- **影响**: Implementation worker wastes time designing thread safety, or ships a heartbeat thread with subtle races.

- **建议改法和验证点**:
  1. Specify the heartbeat thread's stop protocol explicitly: "CLI starts daemon thread before `run_sync()`, joins/stops it in a `finally` block after `run_sync()` returns, using a `threading.Event` stop signal."
  2. Specify the shared state and lock: "Reporter holds `_current_phase: str | None`, `_current_chapter_id: int | None`, `_current_attempt: int | None`, `_phase_started_monotonic: float | None`, protected by `threading.Lock`. Heartbeat thread acquires lock, checks if phase is active, prints if elapsed > 30s, releases lock. Main thread acquires same lock when updating phase state on each event."
  3. Add a test: "Heartbeat thread stops within 1 second of stop event being set (inject interval to 0.1s for test)."
  4. Keep the stop-condition escape hatch but move it to a narrower scope: only abort if the daemon thread cannot be implemented without touching provider code or Host internals.

- **修复风险**: 低 — 只需要在 plan 中补充线程契约，不改变架构。
- **严重程度**: 高

---

### F2-REQUIRED-FIX-MEDIUM: event_sink failure semantics are contradictory

- **位置**: Implementation Slice P1, step 1 "Add generic Host event sink" (lines 221-232)
- **问题类型**: 契约缺失 / 不可直接实施
- **当前写法**:
  > If `event_sink` itself raises, fail closed as a UI/observer failure without leaking event payload.
  > Preferred behavior: catch reporter exceptions in CLI reporter and avoid raising from the sink.
  > Host should not swallow arbitrary sink failures unless the implementation defines and tests that behavior clearly.

- **反例/失败场景**: These three sentences give three different directives:
  1. "fail closed as a UI/observer failure" — implies the run should fail if the sink fails.
  2. "catch reporter exceptions in CLI reporter and avoid raising from the sink" — implies the sink should never raise, and the CLI reporter should silently swallow its own errors.
  3. "Host should not swallow arbitrary sink failures unless the implementation defines and tests that behavior clearly" — implies Host might swallow or might not, depending on what the implementation worker decides.

  An implementation worker reading this cannot determine: should the sink callback be wrapped in try/except? By Host or by CLI? Should a sink failure abort the run or just stop progress output?

- **为什么有问题**: Progress output is a UX feature, not a correctness requirement. If the sink raises, aborting the entire `--use-llm` run (which may have taken minutes of provider time) over a stderr formatting error is the wrong tradeoff. But the plan doesn't make this call.

- **直接证据**: Plan lines 231-232.

- **影响**: Implementation worker either makes the wrong call (aborting runs on progress format errors) or spends time designing failure semantics that the plan should have resolved.

- **建议改法和验证点**:
  1. Decide: sink failure must never abort the run. Progress is best-effort UX.
  2. Specify: "CLI reporter's event_sink wrapper catches all exceptions from formatting/writing and silently stops further progress output (sets an internal `_sink_failed` flag). Host calls the sink unconditionally; the sink must never raise. Host must not wrap the sink in try/except — the sink's no-raise contract is enforced by the CLI wrapper."
  3. Add test: "event_sink that raises on third call: first two progress lines appear, subsequent events are silently skipped, run still completes with correct exit code and stdout."

- **修复风险**: 低 — 只需明确决策，不改变架构。
- **严重程度**: 中

---

### F3-REQUIRED-FIX-MEDIUM: event_sink type signature and integration point with internal _event_recorder are unspecified

- **位置**: Implementation Slice P1, step 1 (lines 221-232) and Architecture Decision 1 (lines 157-163)
- **问题类型**: 契约缺失
- **当前写法**:
  > Add an optional generic event sink to `HostRuntimeRunner.run_sync()`, for example:
  > `event_sink: Callable[[HostRunEvent], None] | None = None`
  > Host must call this sink whenever it appends a `HostRunEvent`

- **反例/失败场景**:
  1. The current `HostRuntimeRunner.run_sync()` signature (runtime.py:409) is `run_sync(self, *, operation_name, operation, timeout_seconds=None, session_id=None)`. The plan proposes adding `event_sink` as a fifth keyword-only parameter.
  2. Internally, Host appends events to `events: list[HostRunEvent]` through `_event()` helper and the `record_event` closure (`Callable[[HostRunEventType, Mapping[str, object]], None]`). The plan says `event_sink` receives `HostRunEvent` instances.
  3. **Critical unspecified detail**: Does `event_sink` get called BEFORE or AFTER the event is appended to the internal `events` list? If before, and the sink blocks (e.g., on a slow stderr write), the internal event list is stale. If after, the sink sees events only after they're committed.
  4. The plan says events are passed through `build_safe_diagnostics()` before being given to `event_sink`. But `_event()` (runtime.py:600) already calls `build_safe_diagnostics()`. So the `HostRunEvent` already has safe diagnostics. The plan's wording is slightly misleading — it should say "event_sink receives the same `HostRunEvent` that was appended to the internal events list."

- **为什么有问题**: The implementation worker needs to know WHERE to insert the sink call in `run_sync()`. With 6 different places where events are appended (RUN_STARTED, phase events via record_event closure, RUN_COMPLETED, RUN_FAILED, RUN_CANCELLED, DIAGNOSTIC_RECORDED), the plan should specify the exact insertion point.

- **直接证据**:
  - Plan lines 158-163 (architecture decision)
  - runtime.py:443-456 (current event recording via `record_event` closure and `_event()` helper)
  - runtime.py:488-506 (RUN_COMPLETED path appends events directly, not through closure)

- **影响**: Implementation worker may insert the sink call inconsistently, missing some event types or calling it at the wrong point in the lifecycle.

- **建议改法和验证点**:
  1. Specify: "Modify `_event()` to accept an optional `event_sink` parameter. After constructing the `HostRunEvent` and before returning it, call `event_sink(event)` if the sink is not None. This ensures every event constructed by `_event()` passes through the sink. For events constructed inline (RUN_COMPLETED success path at line 489, RUN_FAILED at line 534), wrap construction in a helper or call sink explicitly after construction."
  2. Alternately: "Keep `_event()` unchanged. After every `events.append(event)` call site in `run_sync()`, also call `event_sink(event)` if the sink is not None. This is more explicit but requires touching 6+ call sites."
  3. Recommend option 1 (modify `_event()`) as simpler and less error-prone.
  4. Add test: "`test_run_sync_event_sink_called_for_all_event_types` that counts event types received by sink and asserts all 5 expected types appear."

- **修复风险**: 低 — 只需明确插入点，不改变架构。
- **严重程度**: 中

---

### F4-NONBLOCKING-LOW: TTY simulation mechanism for tests is not specified

- **位置**: CLI tests section, lines 312-313
- **问题类型**: 测试缺口
- **当前写法**:
  > `runner.invoke(... ["analyze", "110011", "--use-llm"])` with existing fake should not contain `LLM progress:` unless the test explicitly simulates TTY.

- **反例/失败场景**: Click/Typer `CliRunner.invoke()` does not attach a real TTY to stderr by default. `sys.stderr.isatty()` returns `False` inside `invoke()`. The plan requires tests that simulate TTY to assert progress lines appear, but doesn't say how to simulate TTY. The implementation worker must discover or invent a mechanism (monkeypatch `sys.stderr.isatty`, use `pty.openpty`, or inject a `_progress_auto_enabled` callable).

- **为什么有问题**: Without specifying the TTY simulation mechanism, tests may be fragile (monkeypatching `isatty` globally affects other tests) or overly complex (pty-based testing is slow and non-portable).

- **直接证据**: Plan lines 312-313, 326-328.

- **影响**: Implementation worker may write fragile TTY tests or skip TTY test coverage.

- **建议改法和验证点**:
  1. Specify: "CLI progress auto-detection uses a module-level `_progress_tty_check: Callable[[], bool] = lambda: sys.stderr.isatty()`. Tests monkeypatch this callable. Production code is unchanged."
  2. Add test helper: "`with progress_tty_simulated(enable=True): ...` context manager."
  3. This is non-blocking because the implementation worker can discover this pattern independently, but specifying it avoids rework.

- **严重程度**: 低

---

### F5-NONBLOCKING-LOW: run_terminal format line merges three distinct Host event types without mapping specification

- **位置**: UX Contract, line 105
- **问题类型**: 契约缺失
- **当前写法**:
  > `LLM progress: run_terminal run_id=<run_id> event=<run_completed|run_failed|run_cancelled> elapsed_ms=<ms|unknown>`

- **反例/失败场景**: The Host emits `RUN_COMPLETED`, `RUN_FAILED`, and `RUN_CANCELLED` as separate `HostRunEventType` values. The CLI reporter must map these three types to a single `run_terminal` format line. This is a straightforward mapping, but the plan doesn't explicitly state the mapping rule or where `elapsed_ms` comes from for terminal events.

- **为什么有问题**: The Host's `RUN_COMPLETED` event (runtime.py:489) and `RUN_FAILED` event (runtime.py:534) don't include `elapsed_ms` in their diagnostics. The `elapsed_ms` is only in the `HostRunResult`, which is returned AFTER all events are emitted. The CLI reporter receives events one at a time through `event_sink`, so when it receives `RUN_COMPLETED`, it doesn't yet know the `elapsed_ms`. The progress format line includes `elapsed_ms=<ms|unknown>` but the implementation worker must either: (a) defer printing the terminal line until after `run_sync()` returns and `HostRunResult.elapsed_ms` is available, or (b) add `elapsed_ms` to the terminal event diagnostics in Host.

- **直接证据**: Plan line 105; runtime.py:489 (RUN_COMPLETED event has no elapsed_ms), runtime.py:496 (elapsed_ms is in HostRunResult, not in the event).

- **影响**: Implementation worker must either change Host to include elapsed_ms in terminal events or defer terminal progress output. Either is fine but should be specified.

- **建议改法和验证点**:
  1. Decide: option (a) — reporter defers `run_terminal` line until after `run_sync()` returns and `HostRunResult.elapsed_ms` is known. Specify this in the plan.
  2. Or option (b) — add `elapsed_ms` to RUN_COMPLETED/RUN_FAILED/RUN_CANCELLED events in Host. But this changes Host event schema, which the plan says not to do.
  3. Recommend option (a) as simpler and Host-agnostic.

- **严重程度**: 低

---

## Non-blocking Observations

### O1: analysis_core phase event in async context

The plan proposes adding `analysis_core` phase events around `_run_analysis_core()` (plan lines 263-268). `analyze_with_llm()` is `async def` (fund_analysis_service.py:636). The current `HostRunContext.record_phase_started()` is synchronous. This works because `record_phase_started()` doesn't await anything — it just calls the internal `_event_recorder` callback synchronously. No issue, but the implementation worker should verify this rather than assume.

### O2: Missing negative test for progress output when progress is forced but Host fails before any phase starts

The plan's test matrix covers forced progress incomplete/timeout paths, but doesn't explicitly test: `--llm-progress` with a Host that fails immediately (operation raises before any phase event). In this case, only `run_started` and `run_terminal event=run_failed` should appear in stderr, with no `phase_started` lines. The implementation worker should add this edge case.

### O3: `HostRunEventType` import for CLI

The CLI reporter will need to import `HostRunEventType` to switch on event types. The plan (lines 185-186) allows editing `fund_agent/host/__init__.py` for new type aliases. `HostRunEventType` is already exported. No plan change needed, but the implementation worker should verify the import doesn't accidentally pull in Host internals.

### O4: Heartbeat `still_running` format includes `phase=<phase|unknown>`

The plan's heartbeat format (line 104) shows `phase=<phase|unknown>`. The "unknown" fallback suggests the heartbeat thread might fire before any phase has started. But the plan also says (line 123): "Print heartbeat `still_running` only while progress is enabled and a phase has been started but not completed." If heartbeat only fires when a phase is active, the `|unknown` fallback in the format is dead code. This internal contradiction in the UX contract should be resolved: either heartbeat prints only when phase is known (remove `|unknown`), or heartbeat can fire during `analysis_core` (keep it but specify the condition).

---

## Open Questions / Residual Risks

1. **Provider timeout during heartbeat**: If all 6 chapters time out at 60s×2 each, the total run could be ~12 minutes. With 30-second heartbeat intervals, users see ~24 heartbeat lines. Is this acceptable UX, or should heartbeat interval increase after repeated timeouts? (Defer to implementation worker / code review.)

2. **Concurrent `--use-llm` runs**: Two terminal windows running `analyze --use-llm` simultaneously will interleave stderr progress lines. This is inherent to shared stderr and not a plan defect, but the `run_id` prefix in each line is the only disambiguation mechanism. Is this sufficient? (Defer to UX policy owner.)

3. **`still_running` heartbeat and `analysis_core` phase**: The plan lists `analysis_core` as an allowed phase value (line 110) but the heartbeat condition (line 123) says "a phase has been started but not completed." The deterministic core can take seconds for complex funds. During this period, heartbeat would show `phase=analysis_core`. This is correct but users may wonder why "LLM progress" shows a non-LLM phase. Consider renaming the prefix or documenting this in CLI help. (Non-blocking, defer to code review.)

---

## Explicit Statement on Blocking Plan Findings

**Yes, blocking plan findings exist.** F1 (heartbeat thread underspecified), F2 (event_sink failure semantics contradictory), and F3 (event_sink integration point unspecified) must be resolved in the plan before handoff to implementation. These are specification gaps, not design flaws — each has a straightforward resolution. The plan otherwise preserves deterministic analyze/checklist, Host business-agnostic boundary, fail-closed semantics, stdout contract, non-goals, and secret-safety rules correctly.

F4 and F5 are non-blocking; the implementation worker can resolve them during implementation without plan changes.
