# Controller Judgment: MVP LLM Run Progress And Timeout UX Plan Review

## Self-check

- Current phase / role: `MVP real LLM observability and chapter acceptance phase`; controller only.
- Current gate: `MVP LLM run progress and timeout UX gate` plan review.
- Source of truth: plan artifact, AgentDS plan review, AgentMiMo plan review, `docs/design.md`, `docs/implementation-control.md`, and `docs/current-startup-packet.md`.
- Scope boundary: plan review judgment only; no runtime code, tests, implementation, provider budget, calibration, score-loop, push, PR, or mark ready.
- Stop conditions: blocking plan findings exist, so implementation handoff is not allowed until plan fix and re-review pass.

## Inputs

- Plan: `docs/reviews/mvp-llm-run-progress-timeout-ux-plan-20260602.md`
- AgentDS review: `docs/reviews/mvp-llm-run-progress-timeout-ux-plan-review-ds-20260602.md`
- AgentMiMo review: `docs/reviews/mvp-llm-run-progress-timeout-ux-plan-review-mimo-20260602.md`

## Review Verdicts

- AgentDS: `PASS WITH REQUIRED PLAN FIXES`
- AgentMiMo: `PASS WITH REQUIRED PLAN FIXES`

Controller judgment: accept the required plan fixes. The plan is directionally correct but not implementation-ready until the accepted specification gaps are fixed.

## Accepted Findings

| Finding | Controller judgment | Required plan fix |
|---|---|---|
| DS F1 / MiMo F3: heartbeat thread lifecycle underspecified | accepted | Add explicit stop protocol with `threading.Event`, lock-protected state, post-terminal no-heartbeat guarantee, and deterministic test interface such as `_heartbeat_tick()`. |
| DS F2 / MiMo F2: `event_sink` failure semantics ambiguous | accepted | Commit to CLI-owned no-raise sink wrapper. Host calls sink without catch/translation; CLI reporter catches formatter/write failures, disables further progress, and does not affect run terminal state. Add test coverage. |
| DS F3: `event_sink` integration point unspecified | accepted | Specify exact Host insertion point: event sink receives the same safe `HostRunEvent` after it is appended/committed to `HostRunResult.events`, preferably through a single helper/wrapper so all event types are covered. |
| MiMo F1: Service test name mismatch | accepted | Correct the plan reference to `test_host_runner_records_llm_service_phase_events` and state `analysis_core` appears before writer events. |

## Non-blocking Guidance For Plan Fix

- DS F4: specify the TTY simulation mechanism, preferably a module-level auto-detection helper that tests can monkeypatch.
- DS F5: specify terminal progress line source; prefer deferring `run_terminal` output until after `run_sync()` returns so `HostRunResult.elapsed_ms` is available.
- MiMo F4/F5: make `analysis_core` and successful forced-progress test assertions concrete enough but avoid overfitting exact phase counts beyond current behavior.
- MiMo F6: narrow the secret negative assertion from broad `"key"` to specific canaries such as `api_key`, `secret_key`, and `access_key`.

## Decision

Do not proceed to implementation. Dispatch a plan fix to update the plan artifact and write a plan-fix evidence artifact, then send both reviewers a re-review scoped to the accepted findings.
