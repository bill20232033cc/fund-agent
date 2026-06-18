# MVP LLM Run Progress And Timeout UX Implementation Evidence

## Gate / Slice

- Gate: `MVP LLM run progress and timeout UX gate`
- Slice: `P1 Live Safe Progress UX`
- Role: implementation specialist (`AgentCodex`)
- Accepted plan checkpoint: `5dc865f`
- Controller sync checkpoint: `8bdac36`
- Status: implementation complete; no staging, commit, push, PR, or ready-state action performed.

## Self-check

- Current gate / role: implementation specialist only; implemented the assigned P1 slice.
- Source of truth: accepted plan artifact, controller judgment, `docs/implementation-control.md`, `docs/current-startup-packet.md`, and current `docs/design.md` Host / `--use-llm` facts.
- Scope boundary: touched only allowed Host / CLI / Service / tests / README / evidence files; did not edit `docs/design.md`, `docs/implementation-control.md`, `docs/current-startup-packet.md`, provider config/runtime budget, artifact schema, Fund writer/auditor, score/golden/readiness/quality gate/final judgment files, or Dayu runtime.
- Stop conditions: none triggered. No async Host runner, durable session/resume/memory/outbox, provider budget change, artifact schema expansion, Agent/tool-loop migration, chapter acceptance calibration, or auditor relaxation was required.
- Evidence and validation: required targeted pytest and ruff both passed; exact results below.

## Changed Files

- `fund_agent/host/runtime.py`
- `fund_agent/host/__init__.py`
- `fund_agent/services/fund_analysis_service.py`
- `fund_agent/ui/cli.py`
- `tests/host/test_runtime_runner.py`
- `tests/services/test_fund_analysis_service_llm.py`
- `tests/ui/test_cli.py`
- `fund_agent/host/README.md`
- `README.md`
- `tests/README.md`
- `docs/reviews/mvp-llm-run-progress-timeout-ux-implementation-evidence-20260602.md`

## Implemented Plan Items

- Added generic `HostRunEventSink` and optional `event_sink` to `HostRuntimeRunner.run_sync()`.
- Added a single Host commit helper path: construct safe event, append to `HostRunResult.events`, then call `event_sink` with the same event object.
- Routed Host run started, operation-recorded phase/diagnostic events, run completed, failed, and cancelled events through the commit helper.
- Preserved Host sink exception behavior: Host does not swallow or translate `event_sink` exceptions; CLI uses a no-raise reporter sink.
- Added Service-level `analysis_core` phase started/completed around the existing `_run_analysis_core()` when `host_context` exists.
- Added `--llm-progress/--no-llm-progress` to `fund-analysis analyze`; the option is evaluated only inside the `--use-llm` branch.
- Added TTY auto helper `_llm_progress_auto_enabled()`; auto mode enables progress only when stderr is a TTY, while `--llm-progress` forces progress in non-TTY and `--no-llm-progress` disables it.
- Added CLI-owned `_LLMProgressReporter` with `threading.Event` stop signal, one shared `threading.Lock`, lock-protected current phase state, heartbeat thread lifecycle, and deterministic `_heartbeat_tick(now_monotonic: float | None = None) -> bool`.
- Progress output is stderr-only via `typer.echo(..., err=True)` and always starts with `LLM progress:`.
- Progress line types cover `run_started`, `phase_started`, `phase_completed`, `still_running`, and `run_terminal`.
- `run_terminal` is emitted after `HostRuntimeRunner.run_sync()` returns and uses `HostRunResult.elapsed_ms`.
- CLI starts heartbeat immediately before the Host run and stops/joins it in `finally`; terminal handling clears active phase state before emitting terminal progress so no heartbeat is emitted after terminal.

## Safety / Secret Checks

- CLI progress formatter only reads allowlisted fields: `run_id`, event type, `timeout_seconds`, `phase`, `chapter_id`, `attempt`, and `elapsed_ms`.
- CLI reporter does not iterate or print arbitrary `event.diagnostics`.
- Progress formatter rejects values containing forbidden fragments including `Authorization`, `Bearer`, `api_key`, `cookie`, prompt, draft, raw response, provider response, raw audit, `model_name`, and header terms.
- Tests assert progress stderr does not include prompt/raw/secret canaries on forced progress success and timeout paths.
- Existing incomplete artifact serializer tests remain unchanged and pass; artifact schema was not expanded.

## Host Boundary Check

- Host remains business-agnostic: no Service/Fund imports, no fund code/report year/chapter policy/provider clients/ExecutionContract business inspection, and no `extra_payload`.
- `event_sink` is generic lifecycle/event plumbing only.
- Host does not format CLI progress text and does not know `--use-llm`, provider clients, CHAPTER_CONTRACT, ITEM_RULE, preferred_lens, or fund semantics.
- CLI Host boundary still passes only `operation_name`, operation closure, `timeout_seconds`, and generic `event_sink`.

## Fail-closed Check

- Default deterministic `analyze` and `checklist` remain unchanged and still do not use Host/progress.
- `--use-llm` missing config and provider construction failures still fail before Host; progress lines are not emitted.
- Incomplete `--use-llm` result still exits `1`, keeps stdout empty, writes existing local diagnostic artifact when typed, emits existing final diagnostics, and does not fall back to deterministic report.
- Host terminal failure still exits `1`, keeps stdout empty, and is not converted to fake success.
- Accepted LLM final report stdout remains only the final report markdown; progress is stderr-only.

## Validation Results

```bash
uv run pytest tests/host/test_runtime_state.py tests/host/test_runtime_runner.py tests/services/test_fund_analysis_service_llm.py tests/services/test_chapter_orchestrator.py tests/services/test_llm_run_artifacts.py tests/ui/test_cli.py -q
```

Result:

```text
189 passed in 1.40s
```

```bash
uv run ruff check .
```

Result:

```text
All checks passed!
```

No broader host/service/ui subset was run because the implementation stayed within the accepted Host / Service LLM / CLI contracts and required targeted command already covers the touched shared contracts plus related artifact/orchestrator regressions.

## Docs Sync Status

- Updated root `README.md` with `--llm-progress/--no-llm-progress` user-facing behavior.
- Updated `fund_agent/host/README.md` with generic `event_sink` boundary and exception semantics.
- Updated `tests/README.md` with Host event sink, Service `analysis_core` phase, CLI progress, heartbeat, and reporter failure coverage.
- Did not update `docs/design.md`, `docs/implementation-control.md`, or `docs/current-startup-packet.md` per implementation handoff.

## Residual Risks / Owners

| Risk | Disposition | Owner / Destination |
|---|---|---|
| Provider endpoint can still timeout despite progress UX | Accepted residual; UX only improves observability | Future provider runtime budget/calibration gate |
| Progress does not expose provider attempt boundaries live | Accepted residual; provider attempts remain post-hoc safe diagnostics | Future provider observability gate if controller chooses |
| Artifact schema does not retain progress timeline | Deferred; schema expansion was explicitly out of scope | Future observability artifact schema gate with controller approval |
| Chapter acceptance remains low under real provider | Out of scope | Future chapter acceptance calibration gate |

## Completion

Slice P1 is complete and ready for code review handoff. Self-check: pass.
