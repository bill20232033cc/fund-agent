# MVP internalized Host runtime governance adapter plan

Date: 2026-06-01
Gate: `MVP internalized Host runtime governance adapter plan gate`
Gate type: heavy plan gate
Role: Gateflow controller plan artifact

## Current Facts

- Current production path remains `CLI -> Service -> fund_agent/fund -> provider HTTP call`.
- Current default `fund-analysis analyze` and `fund-analysis checklist` are deterministic and do not enter Host.
- `fund-analysis analyze --use-llm` is an explicit provider-backed opt-in path.
- The direct `dayu.host` adapter implementation direction is superseded.
- `dayu-agent`, `dayu.host` and `dayu.engine` must not be production runtime dependencies.
- Dayu is architecture reference and capability source only.
- Current provider blocker remains `provider_runtime_timeout_small_prompt`.

## Goal

Design the minimum local Host runtime governance adapter that wraps only the current `analyze --use-llm` transition path and internalizes Dayu Host capabilities without importing Dayu runtime.

The implementation gate should produce a local Host-managed run lifecycle:

- run identity
- started/deadline/completed timestamps
- global run deadline classification
- cooperative cancellation
- terminal run state
- safe diagnostics
- event/outbox boundary
- provider timeout classification

This plan is code-generation-ready for implementation, but this plan gate does not implement code.

## Non-Goals

- No runtime/code/tests changes in this plan gate.
- No `dayu-agent`, `dayu.host` or `dayu.engine` dependency.
- No upstream Dayu code copy or rewrite.
- No Agent runner, tool loop, ToolRegistry, ToolTrace or context budget implementation.
- No score-loop implementation.
- No provider parameter tuning.
- No deterministic fallback.
- No score, quality gate, golden, fixture promotion, release-readiness or PR state change.

## Architecture Decision

Create `fund_agent/host` as a local Host package in the implementation gate. It will be small and explicit, not a generic clone of Dayu:

- Host owns run lifecycle, deadline, cancellation token, terminal state, safe event/outbox envelope and safe diagnostics.
- Service owns business semantics, prompt/ExecutionContract assembly, provider clients, chapter policy and final assembly.
- Fund owns fund-domain rules and chapter writer/auditor behavior.
- CLI only enters Host for explicit `--use-llm`; deterministic paths do not enter Host.

MVP Host governance is process-local and single-run oriented. It does not promise cross-process cancellation, durable resume/replay, persistent event stores or background workers. Those are future Host gates.

## Important Runtime Constraint

The current LLM path contains synchronous provider operations under an async Service API. The internalized Host cannot honestly force-kill an already-running synchronous provider HTTP call without redesigning provider execution.

Therefore MVP global deadline means:

- Host computes `deadline_at` and owns the terminal classification.
- Service/orchestrator checks cancellation/deadline at stable boundaries.
- Provider HTTP calls remain bounded by existing provider timeout and retry budgets.
- If a provider call times out before Host deadline, classify `provider_runtime_timeout`.
- If Host deadline is exceeded before or between phase boundaries, classify `run_deadline_exceeded`.
- If a future per-phase budget is implemented narrowly, classify `phase_timeout`.

Do not claim hard preemption of blocking provider I/O in this gate.

## Core Types

Implementation should add small dataclasses/enums in `fund_agent/host/runtime.py` or split into `fund_agent/host/state.py` if the file becomes crowded.

### Run Identity And Status

- `HostRunStatus`: `created`, `running`, `succeeded`, `failed`, `cancelled`, `deadline_exceeded`
- terminal statuses: `succeeded`, `failed`, `cancelled`, `deadline_exceeded`
- `HostCancelReason`: `user_cancelled`, `run_deadline_exceeded`
- `HostTimeoutClassification`: `run_deadline_exceeded`, `phase_timeout`, `provider_runtime_timeout`
- `HostPhaseName`: `writer`, `auditor`, `repair`, `final_assembly`

### Runtime Context

`HostRunContext`:

- `run_id: str`
- `started_at: datetime`
- `deadline_at: datetime | None`
- `timeout_seconds: int | None`
- `cancellation_token: HostCancellationToken`

`HostCancellationToken`:

- `cancel(reason: HostCancelReason) -> None`
- `is_cancelled() -> bool`
- `raise_if_cancelled() -> None`
- `reason: HostCancelReason | None`

### Runtime Request

`FundLLMHostRunRequest`:

- `analysis_request: FundAnalysisRequest`
- `operation: Callable[[HostRunContext], FundLLMAnalysisResult]`
- `timeout_seconds: int`
- `operation_name: Literal["fund_analysis_llm_report"]`
- `session_id: str | None`

The Host request must not import Service-layer LLM client or policy types. Service/CLI owns the closure that captures `ChapterOrchestratorLLMClients`, `ChapterOrchestrationPolicy`, `FinalChapterAssemblyPolicy` and calls `FundAnalysisService.analyze_with_llm()`. Host sees an opaque operation and lifecycle metadata only.

All fields are explicit. No `extra_payload`.

### Runtime Result

`FundLLMHostRunResult`:

- `run_id`
- `status`
- `started_at`
- `deadline_at`
- `completed_at`
- `elapsed_ms`
- `timeout_classification`
- `analysis_result: FundLLMAnalysisResult | None`
- `safe_diagnostics: Mapping[str, object]`
- `events: tuple[HostRunEvent, ...]`

If final assembly is incomplete, Host result status must be `failed`, stdout must remain empty, and diagnostics must be safe.

## Safe Diagnostics Contract

Allowed:

- `run_id`, status, timestamps, elapsed ms
- deadline/cancel reason
- timeout classification
- phase names
- chapter IDs
- attempt / provider attempt counters
- existing safe prompt-cost counters
- provider runtime category
- final assembly status
- redacted exception class names

Forbidden:

- API key
- Authorization header
- full prompt
- full draft
- raw provider response
- raw audit response
- provider stdout/stderr
- unbounded exception string that may contain request/response payloads

## Event / Outbox Boundary

MVP event/outbox is an in-memory run-local tuple, not durable infrastructure.

Required event names:

- `run_started`
- `phase_started`
- `phase_completed`
- `run_completed`
- `run_failed`
- `run_cancelled`
- `diagnostic_recorded`

Event payloads must use the same safe diagnostics allowlist. Future durable outbox, replay and cross-process event delivery require later gates.

Ordering invariant:

```text
run_started
  -> (phase_started -> phase_completed)*
  -> exactly one terminal event: run_completed | run_failed | run_cancelled
```

`diagnostic_recorded` may interleave at any point before the terminal event. No event may be appended after a terminal event.

## Implementation Slices

### Slice H1: Host Domain Model

Objective: create local Host runtime types and invariants.

Allowed files:

- `fund_agent/host/__init__.py`
- `fund_agent/host/runtime.py`
- `tests/host/test_runtime_state.py`
- `fund_agent/host/README.md`

Allowed changes:

- Add enums/dataclasses for run status, cancellation, timeout classification, context, event and safe diagnostics.
- Add terminal-state invariant helpers.
- Add safe diagnostic redaction helper.
- Add process-local run ID generation.
- Do not import `fund_agent.services` or `fund_agent.fund` from `fund_agent/host`.

Tests:

- terminal states cannot transition back to non-terminal states;
- cancellation token is idempotent and preserves first reason;
- safe diagnostic helper rejects forbidden keys and truncates unsafe strings;
- generated run IDs are non-empty and prefixed consistently.
- `rg -n "fund_agent\\.services|fund_agent\\.fund" fund_agent/host` returns no matches after Slice H1.

Stop if implementation needs Dayu imports or upstream Dayu code copy.

### Slice H2: Host Runner Facade

Objective: wrap an operation in local Host run lifecycle.

Allowed files:

- `fund_agent/host/runtime.py`
- `tests/host/test_runtime_runner.py`

Allowed changes:

- Add `HostRuntimeRunner.run_sync(...)` for synchronous call sites.
- Compute `started_at`, `deadline_at`, `completed_at`, `elapsed_ms`.
- Create a cancellation token and pass `HostRunContext` into the operation.
- Map operation success, exception, cancellation and deadline breach to terminal states.
- Record safe run events in-memory.
- Treat `timeout_seconds` on the request as the only deadline input; compute `deadline_at = started_at + timeout_seconds`.
- Accept an already-synchronous operation callable. The runner must not call `asyncio.run()` itself.

Tests:

- successful operation reaches `succeeded`;
- exception reaches `failed` with redacted error type;
- pre-run cancellation reaches `cancelled`;
- deadline exceeded before operation completion reaches `deadline_exceeded` at the next boundary;
- events are emitted in legal order;
- no prompt/draft/raw response can enter events.
- `timeout_seconds` is the source of truth for computed `deadline_at`.
- event ordering follows the invariant in this plan.

Stop if hard preemption of blocking provider I/O is required.

### Slice H3: Service Cancellation / Deadline Boundary

Objective: let the current Service LLM path observe Host context without moving business semantics into Host.

Allowed files:

- `fund_agent/services/fund_analysis_service.py`
- `fund_agent/services/chapter_orchestrator.py`
- `tests/services/test_fund_analysis_service_llm.py`
- `tests/services/test_chapter_orchestrator.py` if present or needed

Allowed changes:

- Add optional explicit `host_context` or explicit `cancellation_token` / `deadline_at` parameters to `analyze_with_llm()` and chapter orchestration.
- Check cancellation/deadline before writer, before auditor, before repair and before final assembly.
- Treat MVP `repair` phase events as the current regenerate attempt boundary; there is no separate fine-grained patch repair engine in this gate.
- Preserve existing provider timeout classification and diagnostics.
- Do not let Host inspect fund code, report year, CHAPTER_CONTRACT, anchors or prompt content.

Tests:

- cancellation before writer prevents provider call;
- cancellation between writer and auditor stops before auditor;
- deadline exceeded before final assembly fails closed;
- provider timeout still classifies as `provider_runtime_timeout`;
- existing successful and incomplete LLM Service tests remain valid.

Stop if Service changes would require broad ExecutionContract refactor; that belongs to the next gate.

### Slice H4: CLI `--use-llm` Host Entry

Objective: route only explicit provider-backed CLI analysis through the local Host runner.

Allowed files:

- `fund_agent/ui/cli.py`
- `tests/ui/test_cli.py`

Allowed changes:

- Keep provider config/client construction in CLI/Service-owned path as today.
- Build `FundLLMHostRunRequest` with an opaque synchronous operation closure.
- The CLI operation closure may call `asyncio.run(FundAnalysisService().analyze_with_llm(...))` because the current CLI call site is synchronous. `HostRuntimeRunner.run_sync()` must not create or nest an event loop.
- Call local Host runner instead of naked `FundAnalysisService().analyze_with_llm()`.
- Preserve current stdout/stderr/exit-code contract:
  - complete report -> stdout report;
  - missing config -> exit `1`, empty stdout;
  - incomplete LLM result -> exit `1`, empty stdout, safe stderr summary;
  - no deterministic fallback.
- Add safe Host run fields to incomplete/error stderr summary.

Tests:

- deterministic analyze does not instantiate Host;
- deterministic checklist does not instantiate Host;
- `--use-llm` calls Host runner;
- complete hosted result prints report;
- incomplete hosted result exits `1` and prints safe run summary;
- missing config remains fail-closed and does not print secrets.
- Host runner does not call `asyncio.run()` internally; the CLI-owned operation closure is responsible for bridging the async Service call.

### Slice H5: Evidence, Docs, Validation

Objective: document accepted implementation and prove safety.

Allowed files:

- `docs/reviews/mvp-internalized-host-runtime-governance-adapter-implementation-evidence-20260601.md`
- `docs/reviews/mvp-internalized-host-runtime-governance-adapter-code-review-*.md`
- `docs/reviews/mvp-internalized-host-runtime-governance-adapter-controller-judgment-20260601.md`
- `fund_agent/host/README.md`
- `fund_agent/README.md` only if needed for current architecture fact sync
- root `README.md` only if user-facing command behavior changes materially
- `docs/design.md`, `docs/implementation-control.md`, `docs/current-startup-packet.md` only after implementation is accepted, with short current-fact sync

Required validation:

- `uv run ruff check .`
- `uv run pytest --cov=fund_agent --cov-report=term-missing --cov-fail-under=50 -q`
- deterministic analyze `006597 / 2024` unchanged PASS
- deterministic checklist `006597 / 2024` unchanged PASS
- missing-config `--use-llm` fail-closed PASS
- real provider smoke `uv run fund-analysis analyze 006597 --report-year 2024 --use-llm`
- cancellation/deadline targeted tests PASS
- secret leak scan over changed diagnostics/artifacts PASS
- `rg -n "dayu\\.host|dayu\\.engine|dayu-agent" fund_agent tests pyproject.toml uv.lock` confirms no production runtime dependency/import
- `rg -n "fund_agent\\.services|fund_agent\\.fund" fund_agent/host` confirms Host has no Service/Fund import

Real provider smoke may still fail closed due to `provider_runtime_timeout_small_prompt`. Acceptance requires stable Host run state and safe classification, not complete provider output unless the blocker disappears.

## Stop Conditions

Stop before or during implementation if:

- implementation needs `dayu-agent`, `dayu.host` or `dayu.engine` runtime dependency;
- implementation requires copying or rewriting upstream Dayu code without license/compliance gate;
- Host needs to understand fund business semantics;
- Host needs to import `fund_agent.services` or `fund_agent.fund`;
- explicit parameters would move into `extra_payload`;
- safe diagnostics require full prompt, draft, provider response or audit response;
- timeout cannot be classified as `run_deadline_exceeded`, `phase_timeout` or `provider_runtime_timeout`;
- hard cancellation of blocking provider I/O is required for acceptance;
- changes would affect score, quality gate, golden, fixtures, release-readiness or PR state.

## Review Requirements

Plan review must challenge:

- whether process-local Host lifecycle is sufficient for MVP readiness;
- whether global deadline semantics are honestly described;
- whether slices are narrow enough;
- whether Service/Host boundary avoids fund business leakage;
- whether event/outbox scope is not overbuilt;
- whether validation can prove no Dayu runtime dependency and no secret leak.

## Handoff Summary

Implement a local, process-scoped Host runtime governance adapter for explicit `analyze --use-llm`. It must internalize only the minimum Dayu Host capabilities needed now: run lifecycle, deadline/cancel classification, terminal state, safe diagnostics and run-local events. It must not import Dayu runtime, implement Agent/tool-loop, alter deterministic defaults, alter score/golden/quality gates, or claim hard preemption of synchronous provider calls.
