# MVP LLM Run Progress And Timeout UX Plan

## Gate Context And Self-check

- Role: planning specialist only. This artifact is a code-generation-ready handoff plan, not phaseflow/gateflow execution.
- Current phase: `MVP real LLM observability and chapter acceptance phase`.
- Current gate to plan: `MVP LLM run progress and timeout UX gate`.
- Controller truth-sync checkpoint: `6ba7608 phaseflow: accept real LLM observability truth sync` as provided by controller handoff.
- Prior accepted gate: `MVP incomplete LLM run artifact retention gate`; plan checkpoint `5f18715`, implementation checkpoint `4f7903f`, validation `156 passed` and `ruff check .` passed, AgentDS review PASS.
- Current worktree note: branch observed as `feat/mvp-llm-incomplete-run-artifacts`; unrelated untracked docs/reports exist and must remain untouched unless controller later accepts them.
- Allowed planning output for this handoff: create this plan artifact only.
- Prohibited in this handoff: no runtime/test/config/README/design/control/startup changes, no staging, no commit, no push, no PR, no ready marking.

## Goal / Motivation / Direct Evidence

Goal: make long-running `fund-analysis analyze --use-llm` runs show safe progress and timeout diagnostics on stderr, so interactive users can tell the command is alive and see the current stage without weakening fail-closed behavior.

Why this gate is needed:

- Artifact retention now preserves evidence after typed incomplete `--use-llm` failures, but does not tell users what is happening during a long provider-backed run.
- Current real-provider residual is still provider runtime timeout on small prompts. Users can wait through repeated writer timeouts with little live feedback.
- Current Host already records safe run/phase events, but the CLI only reads the final `HostRunResult` after `HostRuntimeRunner.run_sync()` returns.

Direct evidence:

- `docs/implementation-control.md` and `docs/current-startup-packet.md` identify this as the next gate and explicitly keep progress/timeout UX unimplemented.
- Current `--use-llm` route is `CLI -> Service prepares FundLLMExecutionRequest / ExecutionContract -> Host runner -> Service -> fund_agent/fund -> provider HTTP call`.
- Current latest smoke diagnostic: `006597 / 2024 --use-llm` fails closed with stdout empty, exit `1`, `orchestration_status=partial`, `final_assembly_status=incomplete`, body chapters generated independently, and writer timeouts under the current `60s x2` writer budget.

## Current Code Facts

- CLI `analyze` only enters LLM path when `use_llm` is true, then builds a Service-owned typed request, calls `_run_llm_analysis_in_host()`, handles Host failure/incomplete results, and writes the final report only after success: `fund_agent/ui/cli.py:249`.
- Deterministic `analyze` still bypasses Host and calls `FundAnalysisService().analyze(request)`: `fund_agent/ui/cli.py:266`.
- CLI incomplete LLM behavior currently writes local diagnostics for typed incomplete results, prints safe incomplete and Host summaries to stderr, exits `1`, and leaves stdout empty: `fund_agent/ui/cli.py:252`, `fund_agent/ui/cli.py:901`, `fund_agent/ui/cli.py:941`, `fund_agent/ui/cli.py:973`.
- `_run_llm_analysis_in_host()` calls `HostRuntimeRunner().run_sync(operation_name="fund_analysis_llm_report", operation=operation, timeout_seconds=execution_request.runtime_plan.host_timeout_seconds)`: `fund_agent/ui/cli.py:872`.
- Host safe diagnostics reject keys containing prompt/draft/raw response/stdout/stderr/auth-style fragments and reject complex payloads: `fund_agent/host/runtime.py:19`, `fund_agent/host/runtime.py:140`.
- Host context already supports generic `record_phase_started()` / `record_phase_completed()` with `phase`, `chapter_id`, `attempt`, `provider_attempt`, and `elapsed_ms`: `fund_agent/host/runtime.py:281`, `fund_agent/host/runtime.py:312`.
- `HostRuntimeRunner.run_sync()` currently stores events in memory and returns them only in `HostRunResult.events`: `fund_agent/host/runtime.py:409`, `fund_agent/host/runtime.py:443`, `fund_agent/host/runtime.py:490`.
- Service `analyze_with_llm()` currently runs deterministic core first, then orchestrates chapters, then records final assembly phase events: `fund_agent/services/fund_analysis_service.py:636`, `fund_agent/services/fund_analysis_service.py:646`, `fund_agent/services/fund_analysis_service.py:652`.
- Chapter orchestrator records `writer`, `auditor`, and `repair` phase started/completed events with chapter id and attempt index: `fund_agent/services/chapter_orchestrator.py:939`, `fund_agent/services/chapter_orchestrator.py:1019`, `fund_agent/services/chapter_orchestrator.py:1108`, `fund_agent/services/chapter_orchestrator.py:1231`.
- Provider adapter records provider attempt diagnostics only after provider attempts finish or fail; provider code does not receive Host context and must not be taught Host semantics in this gate: `fund_agent/services/llm_provider.py:218`, `fund_agent/services/llm_provider.py:259`.
- Existing CLI tests assert missing config fails before Host, configured `--use-llm` calls Host with generic parameters, incomplete results exit `1` with empty stdout, typed incomplete writes artifact path, and secret canaries do not leak: `tests/ui/test_cli.py:1642`, `tests/ui/test_cli.py:1692`, `tests/ui/test_cli.py:1793`, `tests/ui/test_cli.py:1833`, `tests/ui/test_cli.py:1951`, `tests/ui/test_cli.py:2048`.
- Existing Host tests assert Host does not import Service/Fund, does not contain fund business terms, rejects unsafe diagnostics, emits phase events, and keeps terminal event ordering: `tests/host/test_runtime_runner.py:22`, `tests/host/test_runtime_runner.py:41`, `tests/host/test_runtime_runner.py:84`, `tests/host/test_runtime_runner.py:135`, `tests/host/test_runtime_runner.py:248`.

## Scope / Non-goals

In scope:

- Safe live progress output for `analyze --use-llm` only.
- Stderr-only UX, preserving stdout as the final report channel.
- Generic Host event streaming callback or equivalent generic event sink.
- CLI-side progress reporter that formats only allowlisted safe scalars.
- Optional Service phase event around deterministic core preparation so long initial work is visible without making Host business-aware.
- Tests proving default deterministic `analyze` and `checklist` remain unaffected.
- Tests proving fail-closed incomplete/timeout/Host failure behavior remains unchanged.

Non-goals:

- No provider timeout budget, retry policy, backoff, max output, or prompt payload budget change.
- No provider fallback, model fallback, multi-model split, or provider endpoint calibration.
- No chapter acceptance calibration and no auditor/programmatic rule relaxation.
- No repair budget increase.
- No final judgment, score-loop, golden/fixture/readiness/PR state change.
- No quality gate semantic change.
- No artifact-retention schema change in the required slice.
- No external `dayu-agent`, `dayu.host`, or `dayu.engine` production dependency.
- No Agent engine/tool-loop migration, durable Host session/resume/memory/outbox, async Host runner, or cross-process cancellation.

## Proposed User-visible Stderr UX Contract

Progress output applies only to `fund-analysis analyze --use-llm`.

### Activation

- Add `analyze` option `--llm-progress/--no-llm-progress` with default `None` / auto.
- Auto mode:
  - If `stderr.isatty()` is true, live progress is enabled.
  - If `stderr.isatty()` is false, live progress is disabled by default to keep automation logs quiet.
- Auto detection must be a module-level CLI helper, for example `_llm_progress_auto_enabled() -> bool`, so tests can monkeypatch it instead of patching global `sys.stderr`.
- `--llm-progress` forces progress on, including non-TTY tests/logs.
- `--no-llm-progress` suppresses progress even on TTY.
- Missing/invalid config and provider construction failures happen before Host starts; they must not print progress lines because no run exists.

### Output Channel

- Progress lines must always use stderr.
- Progress lines must never be written to stdout.
- Successful LLM final report stdout stays exactly the report markdown.
- Incomplete/failed LLM stdout remains empty.

### Line Prefix And Format

Every progress line must start with:

```text
LLM progress:
```

Required line forms:

```text
LLM progress: run_started run_id=<run_id> timeout_seconds=<seconds|none>
LLM progress: phase_started phase=<phase> chapter_id=<id|none> attempt=<n|none>
LLM progress: phase_completed phase=<phase> chapter_id=<id|none> attempt=<n|none> elapsed_ms=<ms|none>
LLM progress: still_running phase=<phase> chapter_id=<id|none> attempt=<n|none> elapsed_ms=<ms>
LLM progress: run_terminal run_id=<run_id> event=<run_completed|run_failed|run_cancelled> elapsed_ms=<ms|unknown>
```

Allowed `phase` values for this gate:

- `analysis_core`: Service-level phase around the existing deterministic core inside `analyze_with_llm()`; this slice must add it when `host_context` exists.
- `writer`: existing per-chapter writer phase.
- `auditor`: existing per-chapter auditor phase.
- `repair`: existing repair-preparation phase.
- `final_assembly`: existing final assembly phase.

The CLI formatter must tolerate unknown future phase strings by printing the sanitized scalar value, but tests must lock current expected values.

### Cadence / Throttling

- Print `run_started` immediately when Host emits `RUN_STARTED`.
- Print `phase_started` and `phase_completed` immediately when Host emits those events.
- Print heartbeat `still_running` only while progress is enabled and a phase has been started but not completed.
- Heartbeat interval: minimum 30 seconds between heartbeat lines. Tests should inject or monkeypatch the reporter clock rather than sleeping.
- Do not print heartbeats when progress is disabled.
- Do not print duplicate `phase_started` or `phase_completed` lines for the same event.
- Do not print provider attempt heartbeats in this gate, because provider clients do not own Host semantics. Provider attempt counts remain in the existing final incomplete runtime summary.
- Print `run_terminal` after `HostRuntimeRunner.run_sync()` has returned a `HostRunResult`, using `HostRunResult.elapsed_ms` as the elapsed source. Do not add `elapsed_ms` to Host terminal event diagnostics just to satisfy CLI formatting.
- `run_terminal` maps Host terminal events as follows: `RUN_COMPLETED -> event=run_completed`, `RUN_FAILED -> event=run_failed`, `RUN_CANCELLED -> event=run_cancelled`. If an existing quality-gate exception path re-raises before CLI can receive a `HostRunResult`, keep existing quality-gate stderr behavior and do not fake a terminal line.

### Heartbeat Lifecycle

- The CLI reporter must own a `threading.Event` stop signal, for example `_stop_event`.
- The CLI must start the heartbeat thread immediately before entering the Host run and must stop and join it in a `finally` block around the Host run, regardless of success, incomplete result, Host failure, quality-gate exception, or other exception.
- The heartbeat thread should be daemonized only as a final process-exit fallback; correctness must come from `_stop_event.set()` plus a bounded `join()` in `finally`.
- The reporter must maintain lock-protected state using one `threading.Lock` shared by the event sink and heartbeat path. Required state includes at least:
  - `_current_phase: str | None`
  - `_current_chapter_id: int | None`
  - `_current_attempt: int | None`
  - `_phase_started_monotonic: float | None`
  - `_last_heartbeat_monotonic: float | None`
  - `_terminal_emitted: bool`
  - `_sink_failed: bool`
- The event sink must acquire the lock when updating current phase state. The heartbeat path must acquire the same lock when reading phase state and deciding whether a `still_running` line is due.
- Once terminal handling begins, the reporter must clear active phase state, set `_terminal_emitted=True`, set `_stop_event`, and join the heartbeat thread before printing or immediately around printing the terminal line. No `still_running` line may be emitted after `run_terminal`.
- Expose a deterministic test interface such as `_heartbeat_tick(now_monotonic: float | None = None) -> bool`. It should perform exactly one heartbeat decision without sleeping or requiring a background thread, return whether it emitted a line, and respect the same lock, throttle interval, stop event, terminal flag, sink-failed flag, and active-phase rules as the real thread.

### Safety Red Lines

Progress stderr must not include:

- prompt text, system prompt, user prompt
- chapter draft markdown, writer draft, repair draft
- raw provider response, raw auditor response, provider HTTP body
- API key, Authorization header, Bearer token, cookie, full provider config
- secret-bearing exception body or exception message
- model name
- arbitrary provider request/response metadata

Progress stderr may include only:

- `run_id`
- Host event type
- `timeout_seconds`
- `phase`
- `chapter_id`
- `attempt`
- `provider_attempt` only if already provided as a safe scalar by Host context
- `elapsed_ms`

Do not iterate and print arbitrary `event.diagnostics`. The CLI reporter must select allowlisted keys by name.

## Architecture And Boundary Decisions

1. Host owns generic event transport only.

   Add an optional generic event sink to `HostRuntimeRunner.run_sync()`, for example:

   ```python
   event_sink: Callable[[HostRunEvent], None] | None = None
   ```

   Host must call this sink whenever it appends a `HostRunEvent`, including `RUN_STARTED`, phase events, diagnostics, and terminal events. Host must not import Service/Fund, must not inspect `FundLLMExecutionRequest`, must not know chapter policy, and must not format CLI text.

   Exact insertion rule: create one Host-local helper/wrapper that constructs the safe `HostRunEvent`, appends it to the `events` list, and then calls `event_sink(event)` with the same event object that has just been committed to `events`. Use that helper for `RUN_STARTED`, operation-recorded phase/diagnostic events, `RUN_COMPLETED`, `RUN_FAILED`, diagnostic events, and `_cancelled_result()` terminal events. Ordering must be: construct safe event -> append to `events` -> call sink -> continue run logic. Host does not catch or translate sink exceptions.

2. Service owns safe stage emission.

   Service/orchestrator may emit generic phase labels through `HostRunContext.record_phase_started()` / `record_phase_completed()`. It may add `analysis_core` around `_run_analysis_core()` because that is Service orchestration timing, not Host business logic. Service must not write CLI stderr and must not change provider behavior.

3. CLI owns user-visible progress formatting.

   CLI decides whether progress is enabled, owns heartbeat cadence, writes stderr, and formats safe lines from Host events. CLI must not inspect prompt/provider payloads and must not use LLM result data for live progress except final existing incomplete summaries.

   CLI also owns the no-raise sink contract. The sink object passed to Host must catch all formatter/write/reporter exceptions internally, set `_sink_failed=True`, disable further progress output, and never propagate to Host. A progress formatting or stderr write failure must not change Host terminal state, LLM result handling, stdout behavior, or exit code.

4. Provider owns HTTP execution only.

   Do not pass Host context into `OpenAICompatibleChapterLLMClient`. Provider attempt diagnostics stay post-hoc scalar diagnostics in `ChapterLLMRuntimeDiagnostic` and existing incomplete summaries.

5. Artifact retention schema remains unchanged.

   Required implementation must not add progress events to `reports/llm-runs/` manifest/summary/chapter JSON. If a future reviewer argues that retained progress events are needed, classify it as optional schema expansion requiring controller approval before implementation.

## Affected Files / Modules

Allowed implementation files for the single MVP slice:

- `fund_agent/host/runtime.py`
- `fund_agent/host/__init__.py` only if a new public type alias is introduced
- `fund_agent/ui/cli.py`
- `fund_agent/services/fund_analysis_service.py`
- `tests/host/test_runtime_runner.py`
- `tests/host/test_runtime_state.py` only if public Host state helpers change
- `tests/services/test_fund_analysis_service_llm.py`
- `tests/ui/test_cli.py`
- `fund_agent/host/README.md` if Host public API changes need documentation sync
- root `README.md` if user-facing CLI option/behavior needs documentation sync
- `tests/README.md` because tests under `tests/host`, `tests/services`, and `tests/ui` will change

Do not edit:

- `docs/design.md`, `docs/implementation-control.md`, `docs/current-startup-packet.md` during implementation slice; controller syncs these after review/acceptance.
- `docs/fund-analysis-template-draft.md`.
- `fund_agent/services/llm_run_artifacts.py` unless controller approves optional artifact schema expansion.
- `fund_agent/services/llm_provider.py`.
- `fund_agent/fund/chapter_writer.py`, `fund_agent/fund/chapter_auditor.py`.
- Any score/golden/fixture/readiness/promotion files.

## Implementation Slice

### Slice P1: Live Safe Progress UX

Objective: provide safe live stderr progress for interactive or explicitly forced `analyze --use-llm` runs while preserving deterministic defaults and LLM fail-closed semantics.

Prerequisites:

- Start from accepted truth-sync checkpoint and current branch.
- Confirm no unrelated dirty files are staged.
- Do not alter provider/runtime budgets.

Exact instructions:

1. Add generic Host event sink.

   - Extend `HostRuntimeRunner.run_sync()` with optional keyword-only `event_sink`.
   - `event_sink` must receive `HostRunEvent` instances only after `_event()` has passed `build_safe_diagnostics()`.
   - Preserve `HostRunResult.events` exactly as the full event tuple.
   - Implement a single Host-local commit helper, for example `_commit_event(events, event_type, run_id, event_sink, **diagnostics)`, with this exact order:
     - construct the safe event via existing `_event(...)`
     - append it to `events`
     - call `event_sink(event)` if `event_sink is not None`
     - return the event if the caller needs it
   - Use this helper for:
     - initial `RUN_STARTED`
     - operation-recorded phase/diagnostic events
     - `RUN_COMPLETED`
     - `RUN_FAILED`
     - `RUN_CANCELLED`
   - Host must not catch, swallow, translate, or wrap `event_sink` exceptions. Production CLI safety comes from the CLI-owned no-raise sink wrapper.
   - The CLI reporter event sink must catch all exceptions from formatting, `typer.echo`, state updates, heartbeat coordination, or any other reporter code. On first reporter failure it must set `_sink_failed=True`, suppress all future progress output, and return `None`. This failure must not affect Host terminal state or final CLI success/failure handling.
   - Do not add business fields, `extra_payload`, or dict payload bags.

2. Add CLI progress activation and reporter.

   - Add `analyze` option `llm_progress: bool | None` with Typer option pair `--llm-progress/--no-llm-progress`.
   - Determine `progress_enabled` only in the `use_llm` branch:
     - `True` when `llm_progress is True`
     - `False` when `llm_progress is False`
     - `_llm_progress_auto_enabled()` when `llm_progress is None`
   - Implement `_llm_progress_auto_enabled()` as a module-level helper whose production body checks `sys.stderr.isatty()` or equivalent. Tests must monkeypatch this helper instead of using a real TTY or patching global stderr internals.
   - Build a small CLI-owned reporter/helper, preferably private module-level class or functions in `fund_agent/ui/cli.py`.
   - Reporter must only format allowlisted fields. Do not print arbitrary diagnostic mappings.
   - Reporter must write with `typer.echo(..., err=True)`.
   - Reporter must maintain current phase state for heartbeat.
   - Reporter must expose a no-op sink when disabled so Host invocation remains simple.
   - Keep function/class docstrings in Chinese and avoid nested classes/functions unless a closure is needed for the event sink.

3. Add heartbeat without changing provider execution.

   - Because sync provider calls can block between `phase_started` and `phase_completed`, use a CLI-owned lightweight heartbeat mechanism.
   - Reporter starts a heartbeat thread only when progress is enabled.
   - Reporter owns `_stop_event: threading.Event` and one `threading.Lock` shared by event handling and heartbeat.
   - Reporter state under the lock must include current active phase, chapter id, attempt, phase start monotonic time, last heartbeat monotonic time, terminal-emitted flag, and sink-failed flag.
   - CLI must call `reporter.start()` immediately before invoking the Host run and must call `reporter.stop()` in a `finally` block. `stop()` must set `_stop_event` and join the thread with a bounded timeout.
   - Heartbeat reads reporter state under the lock and prints `still_running` at most once every 30 seconds only when an active phase exists, `_sink_failed` is false, `_terminal_emitted` is false, and `_stop_event` is not set.
   - `run_terminal` must be emitted after `run_sync()` returns and must use `HostRunResult.elapsed_ms`; terminal handling must stop/join heartbeat or otherwise set the terminal flag before a terminal line can race with a heartbeat. No `still_running` line may be emitted after `run_terminal`.
   - Tests must not sleep. Implement a deterministic method such as `_heartbeat_tick(now_monotonic: float | None = None) -> bool` and test it directly for active-phase emission, throttle suppression, stop-event suppression, sink-failed suppression, and post-terminal suppression.
   - If the implementation cannot add heartbeat narrowly without thread-safety risk, stop and return to controller. Do not fake heartbeat after completion.

4. Pass reporter sink to Host.

   - In `_run_llm_analysis_in_host()`, accept an optional event sink parameter from CLI.
   - Pass that sink to `HostRuntimeRunner().run_sync(...)`.
   - CLI must start/stop/join the reporter heartbeat in a `try/finally` surrounding the `_run_llm_analysis_in_host()` call. If `_run_llm_analysis_in_host()` returns a `HostRunResult`, CLI then calls reporter terminal handling using that result before printing the final report or existing fail-closed summaries. If `_run_llm_analysis_in_host()` re-raises an existing quality-gate exception before returning a result, preserve existing quality-gate stderr and exit code without inventing a fake terminal line.
   - Preserve the current Host boundary: CLI passes `operation_name`, `operation`, `timeout_seconds`, optional `session_id`, and generic `event_sink` only.
   - Update CLI Host boundary tests so `event_sink` is treated as generic Host lifecycle plumbing, not business payload.

5. Add Service `analysis_core` event.

   - In `FundAnalysisService.analyze_with_llm()`, record `analysis_core` phase started/completed around `_run_analysis_core()` when `host_context` exists.
   - Preserve quality gate exception propagation.
   - If `_run_analysis_core()` raises, `phase_completed` may be absent; Host failure final event and existing exception handling are sufficient.
   - Do not move quality gate checks or change deterministic core behavior.

6. Keep final diagnostics unchanged except for additional progress lines when enabled.

   - Existing incomplete final stderr summary must remain.
   - Existing artifact path warning/line must remain.
   - Existing quality gate block/not-run stderr must remain.
   - Existing generic Host failure summary must remain.
   - Existing stdout contracts must remain.

7. Documentation sync inside implementation gate.

   - If the new CLI option is public, update root `README.md` minimally in the user-facing CLI command section.
   - Update `fund_agent/host/README.md` to mention optional generic event sink and that Host still does not format progress or understand fund semantics.
   - Update `tests/README.md` to mention progress event/CLI tests.
   - Do not update design/control/startup packet in the implementation worker; controller handles those after review.

Completion signal:

- `analyze --use-llm --llm-progress` emits safe progress to stderr during fake/test LLM runs.
- `analyze --use-llm` in non-TTY auto mode keeps current quiet automation behavior except existing final diagnostics.
- Deterministic `analyze` and `checklist` do not call Host or progress code.
- Incomplete/timeout/Host failure paths still exit fail-closed with empty stdout and no deterministic fallback.

## Tests / Validation Commands

### Required Unit Tests

Host tests:

- Add `test_run_sync_event_sink_receives_events_in_order`.
- Add `test_run_sync_event_sink_receives_terminal_failure_event`.
- Add `test_run_sync_event_sink_payload_is_safe`.
- Add `test_run_sync_event_sink_called_after_event_is_committed` or equivalent: the sink sees the same event object already present as the last item in the internal event list when the sink is called.
- Add `test_run_sync_event_sink_called_for_all_existing_event_types` or equivalent coverage proving the single commit helper covers run started, phase started/completed, diagnostic, completed, failed and cancelled paths.
- Keep source boundary tests proving Host does not import Service/Fund and contains no fund business/ExecutionContract terms.
- If `event_sink` is exported as a type alias, test public import only if meaningful.

Service tests:

- Update `test_host_runner_records_llm_service_phase_events` to include `analysis_core` before writer/auditor/final_assembly.
- The expected sequence must assert `analysis_core` `PHASE_STARTED` and `PHASE_COMPLETED` appear before any writer phase event. In the existing happy-path test, `analysis_core` is required, not optional.
- Add or update assertions that phase diagnostics contain only safe scalar keys.
- Keep deterministic `analyze()` / `checklist()` no-LLM tests unchanged in behavior.

CLI tests:

- Default non-TTY auto:
  - `runner.invoke(... ["analyze", "110011", "--use-llm"])` with existing fake should not contain `LLM progress:` unless the test explicitly simulates TTY.
  - Simulate TTY by monkeypatching `_llm_progress_auto_enabled()` to return `True`; do not rely on a real pseudo-TTY.
  - stdout and exit code expectations remain unchanged.
- Forced progress:
  - `runner.invoke(... ["analyze", "110011", "--use-llm", "--llm-progress"])` on a configured success fake prints progress lines to stderr and report markdown to stdout.
  - Assert progress lines include one `run_started`.
  - Assert at least one `phase_started` and at least one `phase_completed` line.
  - Assert `run_terminal` appears exactly once and uses `HostRunResult.elapsed_ms`.
  - Do not assert an exact total count of phase lines beyond current behavior needed to prove `analysis_core` precedes writer when those phases are present.
  - Heartbeat lines may or may not appear depending on injected clock; do not require them in the successful forced-progress smoke test.
  - Assert report stdout is exactly `# LLM report\n` or the current fake report.
- Forced progress incomplete:
  - Exit `1`, stdout empty.
  - Stderr contains progress lines plus existing `LLM 分析未完成：`, `LLM Host run 未完成：`, and artifact path line when typed incomplete artifact writing is enabled.
  - No deterministic report in `result.output`.
- Forced progress timeout:
  - Exit `1`, stdout empty.
  - Stderr contains current first-failed timeout scalar summary.
  - Stderr may contain progress `phase=writer`; test must keep negative assertions for prompt/raw/secret/model/body fields.
- `--no-llm-progress`:
  - Simulate TTY or monkeypatch progress auto helper to true, pass `--no-llm-progress`, and assert no `LLM progress:` lines.
- Reporter failure:
  - Add `test_event_sink_exception_does_not_affect_host_terminal_state` or equivalent CLI-level test. Simulate a reporter formatter/write failure through the CLI-owned reporter sink, assert the sink catches it, sets sink-failed state, suppresses later progress lines, and the Host run still reaches the same terminal status, stdout, stderr final diagnostics, and exit code it would have reached without reporter failure.
- Heartbeat lifecycle:
  - Add deterministic tests for `_heartbeat_tick()` covering active-phase emission, 30-second throttle, stop-event suppression, sink-failed suppression, and post-terminal suppression.
  - Add a lifecycle test proving CLI calls reporter stop/join in a `finally` path around Host run; the test should not sleep except for a bounded join timeout if unavoidable.
- Missing config / construction failure:
  - Still fail before Host; no progress lines; Service not called.
- Quality gate block/not-run in `--use-llm`:
  - Existing exit code `2`, stdout empty, quality gate stderr preserved.
  - If progress is forced and Host starts before the block, progress lines may exist, but no `LLM Host run 未完成` fake-success/fake-incomplete line should appear.
- Boundary:
  - Update fake Host runner to accept `event_sink` as a generic kwarg and still assert no business args.
  - Source boundary regression should allow `event_sink` while continuing to forbid `fund_code`, `report_year`, `chapter_policy`, `provider_runtime_budget`, `extra_payload`, etc.

Secret leakage negative assertions for progress stderr must include at least:

- `Authorization`
- `Bearer`
- `sk-`
- `api_key`
- `cookie`
- `secret_key`
- `access_key`
- `system_prompt`
- `user_prompt`
- `prompt`
- `draft_markdown`
- `raw_response`
- `provider_response`
- `provider body`
- `raw audit`
- `model_name`
- `header`

### Validation Commands

Run targeted validation:

```bash
uv run pytest tests/host/test_runtime_state.py tests/host/test_runtime_runner.py tests/services/test_fund_analysis_service_llm.py tests/services/test_chapter_orchestrator.py tests/services/test_llm_run_artifacts.py tests/ui/test_cli.py -q
```

Expected:

- All targeted tests pass.
- Existing `tests/services/test_llm_run_artifacts.py` still passes without schema changes.
- Existing incomplete LLM artifact tests still prove prompt/raw/secret canaries do not leak.

Run lint:

```bash
uv run ruff check .
```

Expected:

- Pass.

Recommended broader validation if implementation touches shared Host/CLI docs or contracts:

```bash
uv run pytest tests/services tests/host tests/ui -q
```

Expected:

- Pass.

Do not run live provider smoke unless controller separately authorizes credentials/network/cost. A live smoke failure from provider timeout must not block this UX gate if local fake/MockTransport validation passes and fail-closed behavior is preserved.

## Docs / Control Sync Plan

Implementation worker:

- Update root `README.md` only if the public `--llm-progress/--no-llm-progress` option is added.
- Update `fund_agent/host/README.md` because Host API gains a generic event sink.
- Update `tests/README.md` because Host/UI/Service test coverage changes.
- Do not update `docs/design.md`, `docs/implementation-control.md`, or `docs/current-startup-packet.md`.

Controller after implementation review acceptance:

- Update `docs/implementation-control.md` to mark this progress/timeout UX gate accepted, record checkpoint hash, validation, review result, and residual owners.
- Update `docs/current-startup-packet.md` to move the next entry point to chapter acceptance calibration or the controller-selected next gate.
- Update `docs/design.md` minimally to record current `--use-llm` progress UX facts and keep provider budget/calibration/score-loop as future.

Artifact schema decision:

- No required artifact-retention schema change in this gate.
- If implementation or review proposes adding progress events to `reports/llm-runs/`, stop and request controller approval because that changes artifact schema and lifecycle.

## Review Gates

Plan review must verify:

- UX contract is precise enough to implement without redesign.
- Host remains business-agnostic and does not import Service/Fund or inspect ExecutionContract fields.
- CLI progress is stderr-only and does not alter stdout final report channel.
- TTY/non-TTY behavior avoids automation noise.
- Non-goals exclude provider budget, retry, calibration, quality gate, score-loop, golden/readiness, and PR state changes.

Code review must verify:

- `event_sink` is generic lifecycle plumbing, not business payload.
- No prompt/raw/provider body/secrets are formatted in progress lines.
- Reporter heartbeat is bounded, stopped after run completion, and does not leave running non-daemon threads.
- Existing incomplete-result artifact writing and final diagnostics still execute.
- Deterministic `analyze/checklist` do not enter Host/progress code.
- Host terminal state is not swallowed, double-wrapped, or converted into fake success.

At least two independent reviews are recommended for this heavy gate unless controller records reviewer unavailability.

## Stop Conditions

Stop and return to controller if any of the following becomes necessary:

- Changing provider timeout, retry, backoff, max output, or prompt payload budget.
- Relaxing writer/auditor/programmatic audit rules or chapter acceptance criteria.
- Changing quality gate, final judgment, score-loop, golden/fixture/readiness, or PR state.
- Printing anything to stdout before a complete final report.
- Printing prompt text, raw provider/auditor response, provider HTTP body, API keys, Authorization headers, cookies, full provider config, or secret-bearing exception text.
- Teaching Host about fund code, report year, chapter policy, ExecutionContract business fields, provider config, CHAPTER_CONTRACT, ITEM_RULE, or preferred_lens.
- Passing explicit business parameters through `extra_payload` or arbitrary kwargs.
- Adding external `dayu-agent`, `dayu.host`, or `dayu.engine` runtime dependency.
- Requiring provider clients to know Host internals.
- Changing artifact-retention schema without controller approval.
- Implementing heartbeat requires broad async runner, durable session, cross-process cancel, or provider adapter refactor.

## Residual Risks And Owners

| Risk | Disposition | Owner / Next Gate |
|---|---|---|
| Provider endpoint may still timeout despite progress UX | Accepted residual; this gate only makes runtime observable | Future provider runtime budget/calibration gate |
| Progress does not show provider attempt boundaries live | Accepted residual; provider attempts remain post-hoc diagnostics | Future provider observability gate if needed |
| Heartbeat thread complexity | Mitigate with small CLI-owned reporter, lock, stop/finally, no provider changes | Implementation worker + code review |
| Non-TTY default may remain quiet in automation | Intentional to avoid log noise; users can force with `--llm-progress` | UX policy owner / controller |
| Artifact schema lacks retained progress timeline | Deferred; optional schema expansion needs controller approval | Future observability artifact schema gate |
| Chapter 2/3/6 acceptance remains low | Out of scope | Future chapter acceptance calibration gate |
| `analysis_core` is a broad phase label | Acceptable if Service-owned and Host-carried only; do not expose fund internals | Implementation review |

## Completion Report Format For Implementation Worker

Implementation worker should report:

```text
Gate: MVP LLM run progress and timeout UX gate
Slice: P1 Live Safe Progress UX

Changed files:
- ...

UX contract implemented:
- default auto behavior:
- --llm-progress:
- --no-llm-progress:
- stderr-only / stdout contract:
- run_terminal source/order:
- heartbeat lifecycle:

Boundary confirmation:
- deterministic analyze/checklist:
- Host business-agnostic:
- no provider budget/retry/calibration changes:
- no artifact schema change:
- no dayu runtime dependency:

Fail-closed confirmation:
- incomplete result:
- provider timeout:
- Host terminal failure:
- quality gate block/not-run:
- reporter sink failure:

Secret safety confirmation:
- prompt/raw/provider body/auth/cookie/model/config negative tests:

Validation:
- command -> result
- command -> result

Docs updated:
- root README:
- fund_agent/host/README.md:
- tests/README.md:
- design/control/startup untouched by implementation worker:

Residual risks:
- ...

Stop conditions encountered:
- none / details
```
