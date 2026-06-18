# MVP LLM Run Progress And Timeout UX Plan Fix Evidence

## Self-check

- Role: plan fix specialist only.
- Target plan: `docs/reviews/mvp-llm-run-progress-timeout-ux-plan-20260602.md`.
- Inputs: AgentDS review, AgentMiMo review, and controller judgment for the plan review.
- Scope: update the plan artifact and write this fix evidence artifact only.
- Explicit non-actions: no runtime code, tests, config, README, design, control, startup packet, staging, commit, push, PR, implementation, or ready-state change.

## Fix Summary

The plan was updated to close the controller-accepted required findings and incorporate non-blocking guidance where it improved implementation handoff precision without expanding scope.

## Accepted Findings To Plan Changes

| Finding | Status | Plan change |
|---|---|---|
| DS F1 / MiMo F3: heartbeat lifecycle underspecified | fixed in plan | Added `Heartbeat Lifecycle` UX subsection specifying `threading.Event` stop signal, one `threading.Lock`, required lock-protected reporter state, CLI `try/finally` start/stop/join protocol around Host run, post-terminal no-heartbeat guarantee, and deterministic `_heartbeat_tick()` test interface. Updated Slice P1 step 3 and CLI tests to require active-phase/throttle/stop/sink-failed/post-terminal coverage. |
| DS F2 / MiMo F2: `event_sink` failure semantics ambiguous | fixed in plan | Committed to CLI-owned no-raise sink wrapper. Host calls sink without catch/translation; CLI reporter catches formatter/write/state failures, sets `_sink_failed=True`, suppresses later progress, and does not affect Host terminal state, stdout, stderr final diagnostics, or exit code. Added required `test_event_sink_exception_does_not_affect_host_terminal_state` coverage. |
| DS F3: `event_sink` integration point unspecified | fixed in plan | Added exact Host insertion rule: a single Host-local commit helper constructs a safe `HostRunEvent`, appends it to `events`, then calls `event_sink(event)` with that same committed event. Updated Slice P1 step 1 and Host tests to require ordering and all event-type coverage. |
| MiMo F1: Service test name mismatch | fixed in plan | Replaced the incorrect `test_analyze_with_llm_host_context_records_phase_events` reference with `test_host_runner_records_llm_service_phase_events`. Added that `analysis_core` phase started/completed must appear before writer events in the happy-path expected sequence. |

## Non-blocking Guidance Incorporated

| Guidance | Plan change |
|---|---|
| DS F4: specify TTY simulation | Added module-level `_llm_progress_auto_enabled()` helper requirement and test monkeypatch guidance. |
| DS F5: terminal progress line source | Specified `run_terminal` is emitted after `HostRuntimeRunner.run_sync()` returns and uses `HostRunResult.elapsed_ms`; no Host terminal event schema change is required. |
| MiMo F4/F5: make forced successful progress assertions concrete without overfitting | Updated CLI forced-progress test expectations to require one `run_started`, at least one `phase_started` and `phase_completed`, exactly one `run_terminal`, and no exact phase-line count beyond proving `analysis_core` precedes writer where present. |
| MiMo F6: avoid broad `key` canary | Replaced broad `key` negative assertion with `secret_key` and `access_key`, while retaining `api_key`. |

## Scope Confirmation

- Modified only `docs/reviews/mvp-llm-run-progress-timeout-ux-plan-20260602.md`.
- Added only this evidence artifact: `docs/reviews/mvp-llm-run-progress-timeout-ux-plan-fix-evidence-20260602.md`.
- Did not modify runtime code, tests, config, README, `docs/design.md`, `docs/implementation-control.md`, or `docs/current-startup-packet.md`.
- Did not stage, commit, push, create PR, mark ready, or enter implementation.

## Validation

No code validation was run because this is a plan-only fix and no runtime/tests were modified. The plan was read back after patching to verify the accepted findings are represented in the target artifact.

## Re-review Handoff

Re-review should focus on:

- Whether heartbeat lifecycle is now implementation-ready.
- Whether `event_sink` failure behavior is unambiguous and correctly owned by CLI.
- Whether Host event sink insertion point and ordering are precise enough.
- Whether the Service test reference and `analysis_core` ordering are corrected.
- Whether no required plan fix expanded into provider budget, chapter acceptance, artifact schema, score/golden/readiness, or implementation scope.
