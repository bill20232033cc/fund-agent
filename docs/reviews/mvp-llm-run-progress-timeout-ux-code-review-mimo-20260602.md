# Code Review: MVP LLM Run Progress And Timeout UX

## Gate / Role

- Gate: `MVP LLM run progress and timeout UX gate`
- Slice: `P1 Live Safe Progress UX`
- Role: independent code reviewer (`AgentMiMo`)
- Accepted plan checkpoint: `5dc865f`
- Controller sync checkpoint: `8bdac36`
- Review date: 2026-06-02

## Inputs

| Purpose | Artifact |
|---|---|
| Accepted plan | `docs/reviews/mvp-llm-run-progress-timeout-ux-plan-20260602.md` |
| Implementation evidence | `docs/reviews/mvp-llm-run-progress-timeout-ux-implementation-evidence-20260602.md` |
| Plan acceptance judgment | `docs/reviews/mvp-llm-run-progress-timeout-ux-plan-controller-judgment-20260602.md` |
| Unstaged code diff | `git diff HEAD` on all changed files |

## Validation Re-run

```bash
uv run pytest tests/host/test_runtime_state.py tests/host/test_runtime_runner.py tests/services/test_fund_analysis_service_llm.py tests/services/test_chapter_orchestrator.py tests/services/test_llm_run_artifacts.py tests/ui/test_cli.py -q
```

Result: `189 passed in 0.98s`

```bash
uv run ruff check .
```

Result: `All checks passed!`

Both match implementation evidence.

## Review Focus Areas

### 1. Progress UX scope: `--use-llm` only

**Verdict: PASS**

- `--llm-progress/--no-llm-progress` is evaluated only inside the `use_llm` branch (`cli.py:784`).
- Deterministic `analyze` and `checklist` paths remain unchanged, no Host or progress code entered.
- The CLI option is declared on the `analyze` command only.

### 2. Stdout contract: strict final-report-only

**Verdict: PASS**

- Successful LLM path: stdout receives only the report markdown via `typer.echo(result.report_markdown)` (`cli.py:808` → existing flow).
- Incomplete/failed LLM: stdout remains empty, exit code 1. Confirmed by `test_analyze_cli_use_llm_forced_progress_incomplete_keeps_fail_closed` asserting `result.stdout == ""`.
- Progress is stderr-only via `typer.echo(..., err=True)` (`cli.py:534`).
- `run_terminal` progress line is emitted after `HostRuntimeRunner.run_sync()` returns and before the success/failure branch (`cli.py:794`).

### 3. `--llm-progress` / `--no-llm-progress` / auto TTY behavior

**Verdict: PASS**

- `_resolve_llm_progress_enabled(True)` → `True` (forced on) ✓
- `_resolve_llm_progress_enabled(False)` → `False` (forced off) ✓
- `_resolve_llm_progress_enabled(None)` → `_llm_progress_auto_enabled()` → `sys.stderr.isatty()` ✓
- `--llm-progress` forces progress even in non-TTY (tested via `monkeypatch.setattr(cli, "_llm_progress_auto_enabled", lambda: False)` + `--llm-progress` flag) ✓
- `--no-llm-progress` suppresses progress even in TTY (tested via monkeypatch returning `True` + `--no-llm-progress` flag) ✓
- Module-level `_llm_progress_auto_enabled()` helper allows test monkeypatching without patching `sys.stderr` ✓

### 4. Host `event_sink` is generic, business-agnostic, append-before-sink

**Verdict: PASS**

- `HostRunEventSink = Callable[["HostRunEvent"], None]` type alias exported in `host/__init__.py` ✓
- `event_sink` parameter is keyword-only on `run_sync()` (`runtime.py:417`) ✓
- Single `_commit_event()` helper constructs safe event → appends to `events` → calls sink → returns event (`runtime.py:660-696`) ✓
- Used for all event types: `RUN_STARTED`, `PHASE_STARTED`/`PHASE_COMPLETED` (via `record_event`), `DIAGNOSTIC_RECORDED`, `RUN_COMPLETED`, `RUN_FAILED`, `RUN_CANCELLED` ✓
- Sink receives the same object already committed to `events` list (tested by `test_run_sync_event_sink_receives_committed_event_object` using `is` identity) ✓
- Host source boundary tests still pass: no `fund_agent.services`, `fund_agent.fund`, fund business terms, or `ExecutionContract` fields in Host source ✓

### 5. Host does not catch/translate `event_sink` exceptions; CLI no-raise reporter

**Verdict: PASS**

- `_commit_event` catches sink exception, records in `event_sink_errors`, then re-raises (`runtime.py:691-695`) ✓
- Host `except Exception` block has identity check `if event_sink_errors and event_sink_errors[-1] is exc: raise` to prevent broad catch from swallowing sink exceptions (`runtime.py:533-534`) ✓
- `test_run_sync_event_sink_exception_propagates_from_host` verifies sink exceptions are not swallowed ✓
- CLI `_LLMProgressReporter.handle_event()` catches all exceptions and calls `_mark_sink_failed()` (`cli.py:312-315`) ✓
- `_mark_sink_failed()` sets `_sink_failed=True`, clears phase state, sets `_stop_event` (`cli.py:549-556`) ✓
- `test_analyze_cli_progress_sink_failure_does_not_affect_success` proves sink failure does not change exit code, stdout, or host terminal state ✓
- `test_llm_progress_reporter_sink_exception_does_not_escape` proves sink exceptions are caught internally ✓

### 6. Heartbeat lifecycle: Event + Lock + deterministic `_heartbeat_tick`

**Verdict: PASS**

- `_stop_event: threading.Event` for stop signal ✓
- `_lock: threading.Lock` shared by event handling and heartbeat ✓
- Lock-protected state: `_current_phase`, `_current_chapter_id`, `_current_attempt`, `_phase_started_monotonic`, `_last_heartbeat_monotonic`, `_terminal_emitted`, `_sink_failed` ✓
- CLI starts heartbeat via `reporter.start()` immediately before Host run (`cli.py:787`) ✓
- CLI stops/joins in `finally` block (`cli.py:792-793`) ✓
- `stop()` sets `_stop_event` and joins with bounded timeout (`_LLM_PROGRESS_THREAD_JOIN_SECONDS = 2.0`) ✓
- `_terminal_emitted` is set and `_stop_event` is set before `emit_terminal` prints the terminal line (`cli.py:336-344`) ✓
- Deterministic `_heartbeat_tick(now_monotonic)` allows test injection ✓
- Heartbeat tests cover: active-phase emission, 30-second throttle, stop-event suppression, sink-failed suppression, post-terminal suppression ✓

### 7. `run_terminal` after `run_sync()` returns, uses `elapsed_ms`

**Verdict: PASS**

- `emit_terminal(host_result)` called after `host_result = _run_llm_analysis_in_host(...)` returns (`cli.py:794`) ✓
- Uses `host_result.elapsed_ms` in terminal progress line (`cli.py:351`) ✓
- Maps `HostRunStatus.SUCCEEDED` → `run_completed`, `FAILED` → `run_failed`, `CANCELLED`/`DEADLINE_EXCEEDED` → `run_cancelled` (`cli.py:579-601`) ✓
- `test_llm_progress_reporter_suppresses_heartbeat_after_terminal` verifies `elapsed_ms=42` from `HostRunResult.elapsed_ms` ✓

### 8. Secret safety

**Verdict: PASS**

- CLI progress formatter only reads allowlisted fields: `run_id`, event type, `timeout_seconds`, `phase`, `chapter_id`, `attempt`, `elapsed_ms` ✓
- `_progress_scalar()` rejects values containing forbidden fragments (`cli.py:92-109`) ✓
- CLI reporter does not iterate arbitrary `event.diagnostics` ✓
- `_LLM_PROGRESS_FORBIDDEN_VALUE_PARTS` covers: `api_key`, `authorization`, `bearer`, `cookie`, `secret_key`, `access_key`, `system_prompt`, `user_prompt`, `prompt`, `draft_markdown`, `raw_response`, `provider_response`, `provider body`, `raw audit`, `model_name`, `header` ✓
- Forced progress success test asserts all forbidden fragments absent from progress stderr ✓
- Forced progress timeout test asserts all forbidden fragments absent from progress stderr ✓
- `test_run_sync_event_sink_payload_is_safe` verifies Host event diagnostics contain only safe scalar types ✓

### 9. Host boundary remains clear

**Verdict: PASS**

- Host does not understand fund business, `ExecutionContract` fields, provider clients, `CHAPTER_CONTRACT`, `ITEM_RULE`, `preferred_lens`, or `extra_payload` business params ✓
- `event_sink` is generic lifecycle plumbing only ✓
- Host does not format CLI progress text and does not know `--use-llm` ✓
- CLI Host boundary passes only `operation_name`, operation closure, `timeout_seconds`, and generic `event_sink` ✓
- `_FakeHostRuntimeRunner` in tests accepts `event_sink` as generic kwarg and records it; `forbidden_business_args` captures only unexpected kwargs ✓
- Source boundary test `test_host_runner_source_has_no_fund_business_semantics` still passes ✓

### 10. Tests cover negative boundary and fail-closed behavior

**Verdict: PASS**

- Default non-TTY auto: no `LLM progress:` in stderr ✓
- Forced progress success: progress lines in stderr, report in stdout, exit 0 ✓
- Forced progress incomplete: exit 1, stdout empty, progress + existing diagnostics in stderr ✓
- Forced progress timeout: exit 1, stdout empty, safe progress + timeout scalar in stderr ✓
- `--no-llm-progress` overrides TTY auto: no progress lines ✓
- Reporter sink failure: sink catches exception, sets `sink_failed`, host run still succeeds ✓
- Missing config / construction failure: still fails before Host, no progress lines ✓
- Heartbeat lifecycle: deterministic tick tests for all suppression conditions ✓
- Host event sink: order, terminal events, safe payload, committed object identity, exception propagation ✓

### 11. Docs sync accuracy

**Verdict: PASS**

- Root `README.md`: `--llm-progress/--no-llm-progress` documented in CLI options table and examples ✓
- `fund_agent/host/README.md`: `event_sink` boundary and exception semantics documented ✓
- `tests/README.md`: Host event sink, Service `analysis_core` phase, CLI progress, heartbeat, and reporter failure coverage documented ✓
- No future-claiming implementation not present ✓
- `docs/design.md`, `docs/implementation-control.md`, `docs/current-startup-packet.md` not modified by implementation worker ✓

## Findings

### Non-blocking

**NB-1: `_heartbeat_tick` releases lock before `_safe_echo` — acceptable narrow race window**

`cli.py:374-403`: The `_heartbeat_tick` method acquires the lock to read phase state and update `_last_heartbeat_monotonic`, then releases the lock before calling `_safe_echo`. Between lock release and echo, `emit_terminal` could set `_terminal_emitted` and `_stop_event`. The worst case is one stale `still_running` line printed before the `run_terminal` line. This is acceptable because:

1. `emit_terminal` calls `stop()` which joins the heartbeat thread with a bounded timeout.
2. The stale heartbeat appears *before* the terminal line in stderr, not after.
3. The CLI's no-raise wrapper catches any echo failure.

**NB-2: `_FakeHostRuntimeRunner` does not exercise real sink-exception-escapes-Host path**

`tests/ui/test_cli.py`: The fake host runner calls `host_context.commit_event()` which catches sink exceptions implicitly by not propagating them. The real `HostRuntimeRunner.run_sync()` has the `event_sink_errors[-1] is exc` re-raise mechanism. The CLI test `test_analyze_cli_progress_sink_failure_does_not_affect_success` proves the CLI wrapper catches exceptions, which is the primary safety mechanism. The Host-level sink exception propagation is separately tested in `test_run_sync_event_sink_exception_propagates_from_host`.

**NB-3: `_mark_sink_failed()` calls `_stop_event.set()` inside the lock**

`cli.py:556`: `_mark_sink_failed()` sets `_stop_event` while holding the lock. The `_heartbeat_loop` calls `_stop_event.wait()` without holding the lock. This is safe because `threading.Event.set()` is thread-safe, and the heartbeat loop will exit on the next poll cycle. However, the heartbeat thread may be blocked in `_heartbeat_tick` waiting for the lock, in which case `_mark_sink_failed` will acquire the lock first, set the flag, and the heartbeat will see `_sink_failed=True` on its next check. Correct behavior.

### Blocking

None.

## Verdict

**PASS** — no blocking findings.

The implementation faithfully follows the accepted plan. All 189 targeted tests pass, ruff checks pass, Host boundary is preserved, progress UX is stderr-only with allowlisted safe fields, heartbeat lifecycle is deterministic and bounded, and fail-closed semantics are unchanged for all paths (incomplete, timeout, host failure, quality gate, reporter sink failure).

## Review Artifact Path

`docs/reviews/mvp-llm-run-progress-timeout-ux-code-review-mimo-20260602.md`
