# MVP dayu.host runtime governance adapter plan

Date: 2026-06-01
Gate: `MVP dayu.host runtime governance adapter plan gate`
Gate type: heavy plan gate
Role: Gateflow controller plan artifact

## Current Facts

- Current production path is `CLI -> Service -> fund_agent/fund -> provider HTTP call`.
- Current code has no `fund_agent/host` package and no Host/Agent/dayu runtime in the production path.
- Local environment can import `dayu.host`; the available direct-operation contract is `Host.run_operation_sync()` with `HostedRunSpec` / `HostedRunContext`.
- `fund-analysis analyze --use-llm` currently builds provider clients in `fund_agent/ui/cli.py`, then calls `FundAnalysisService.analyze_with_llm()`.
- `FundAnalysisService.analyze_with_llm()` remains the transition execution body: deterministic core, chapter orchestration, final assembly, fail-closed partial result, no deterministic fallback.
- Current provider blocker is `provider_runtime_timeout_small_prompt`; this gate is not a provider parameter tuning gate.

## Goal

Introduce a minimal `dayu.host` runtime governance adapter for the explicit `fund-analysis analyze --use-llm` path so the transition Service -> Fund execution body gains Host-managed lifecycle:

- `run_id`
- `started_at`
- `deadline_at`
- `timeout_seconds`
- terminal run state
- global deadline
- cancellation
- safe lifecycle diagnostics
- timeout classification

The adapter must not migrate to `dayu.engine`, ToolRegistry, ToolTrace, Agent runner or tool loop.

## Non-Goals

- No code implementation in this plan gate.
- No `fund_agent/agent` package.
- No `dayu.engine` import, dependency or tool-loop migration.
- No provider parameter tuning, provider fallback or deterministic fallback.
- No score, quality gate, golden, fixture promotion or release-readiness semantic change.
- No PR state change, push, merge, mark-ready or release.
- No cleanup of historical untracked residuals.
- No broad Service ExecutionContract rewrite; that is the next boundary convergence gate.

## Architecture Decision

Use `dayu.host` direct-operation governance, not Agent execution:

- Host adapter wraps the current Service call as an opaque operation.
- Service still owns fund business semantics, prompt/ExecutionContract assembly, chapter policy and provider clients.
- Host owns run lifecycle, global deadline, cancellation, concurrency/deadline resources, terminal state and safe diagnostic envelope.
- Fund remains the Agent-layer domain capability package; this gate does not move Fund into a `dayu.engine` runner.

The implementation must use:

- `dayu.host.Host`
- `dayu.contracts.host_execution.HostedRunSpec`
- `dayu.contracts.host_execution.HostedRunContext`
- `dayu.contracts.run.RunState` / `RunCancelReason`
- `dayu.contracts.cancellation.CancelledError` / `CancellationToken`

Important API facts verified during this plan gate:

- `HostedRunContext` exposes `run_id` and `cancellation_token` only.
- The adapter must compute `started_at`, `deadline_at` and `completed_at`; it must not expect these fields from `HostedRunContext`.
- The adapter must derive terminal status from the operation result, Host cancellation path and safe Host state query/fake-host test seams; it must not assume `HostedRunContext` exposes `RunState`.
- `HostedRunSpec.timeout_ms` is milliseconds. Public adapter configuration may use `timeout_seconds`, but Slice H1 must test `timeout_ms = timeout_seconds * 1000`.
- `Host.run_operation_sync()` exposes `on_cancel`; Slice H1 must use it to produce a fail-closed cancelled result.

The implementation must not import:

- `dayu.engine`
- `dayu.engine.tool_registry.ToolRegistry`
- ToolTrace APIs
- Agent runner/tool-loop APIs

## Target Call Path

Current:

```text
CLI analyze --use-llm
  -> build LLM provider clients
  -> FundAnalysisService.analyze_with_llm()
  -> Service chapter orchestration
  -> fund_agent/fund writer/auditor/provider HTTP call
```

Planned:

```text
CLI analyze --use-llm
  -> build LLM provider clients
  -> build Service-owned LLM execution request
  -> fund_agent.host DayuHostRuntime.run_fund_llm_analysis()
  -> dayu.host.Host.run_operation_sync(spec=HostedRunSpec(...))
  -> operation(HostedRunContext)
  -> FundAnalysisService.analyze_with_llm(..., cancellation/deadline context)
  -> current Service -> Fund execution body
```

Deterministic `analyze` and `checklist` remain unchanged and do not enter Host in this gate.

The adapter is a synchronous CLI-facing wrapper. Because `FundAnalysisService.analyze_with_llm()` is async, the operation callable inside `run_operation_sync()` must bridge with `asyncio.run()` from the current synchronous CLI call site. If a future non-CLI caller already has an active event loop, that is outside this implementation slice and must stop for a separate async Host adapter decision.

## Contracts

### Host Runtime Request

Add a small typed request at the Service/Host boundary. It must contain explicit fields only:

- `request: FundAnalysisRequest`
- `llm_clients: ChapterOrchestratorLLMClients`
- `chapter_policy: ChapterOrchestrationPolicy | None`
- `assembly_policy: FinalChapterAssemblyPolicy | None`
- `timeout_seconds: int`
- `session_id: str | None`
- `scene_name: Literal["fund_analysis_llm_report"]`
- `operation_name: Literal["fund_analysis_llm_report"]`

No `extra_payload` is allowed. No prompt text, draft text, raw provider response or raw audit response may be stored in the request diagnostics.

### Host Runtime Result

Return a typed result wrapper:

- `analysis_result: FundLLMAnalysisResult | None`
- `run_id: str`
- `started_at: datetime | None`
- `deadline_at: datetime | None`
- `completed_at: datetime | None`
- `timeout_seconds: int`
- `terminal_status: Literal["succeeded", "failed", "cancelled", "unsettled"]`
- `failure_category: str | None`
- `timeout_classification: Literal["run_deadline_exceeded", "phase_timeout", "provider_runtime_timeout"] | None`
- `safe_diagnostics: Mapping[str, object]`

`terminal_status` is derived from Host `RunState` and the Service result:

- Host `SUCCEEDED` plus complete final assembly -> `succeeded`.
- Host `SUCCEEDED` plus incomplete final assembly -> `failed`, because partial reports are not complete reports.
- Host `FAILED` -> `failed`.
- Host `CANCELLED` with `RunCancelReason.TIMEOUT` -> `cancelled` plus `run_deadline_exceeded`.
- Host `CANCELLED` with user cancel -> `cancelled`.
- Host `UNSETTLED` -> `unsettled` and fail-closed.

`UNSETTLED` may be difficult to trigger with the real Host in unit tests. Tests may use a fake Host/executor seam to prove fail-closed mapping.

### Phase State

Phase state remains Service-emitted and Host-carried. Host may store or forward these string labels but must not interpret fund semantics:

- `writer`
- `auditor`
- `repair`
- `final_assembly`

Each phase diagnostic may include only safe scalar fields:

- `chapter_id`
- `attempt`
- `provider_attempt`
- `elapsed_ms`
- `phase`
- `operation`
- `component`
- `timeout_seconds`
- `status`
- `failure_category`
- `failure_subcategory`
- `provider_runtime_category`
- prompt-cost counters already allowed by existing serializer

### Timeout Classification

Keep three classes distinct:

- `run_deadline_exceeded`: Host global deadline cancelled the run.
- `phase_timeout`: Service-level phase budget expired before or around a phase boundary.
- `provider_runtime_timeout`: provider HTTP runtime timeout raised by writer/auditor provider client.

Small prompt timeout remains `provider_runtime_timeout` unless Host global deadline fired first. Do not reclassify it as prompt contract, fact gap, audit rule, score failure or code bug.

`phase_timeout` is in scope only as a Service-owned phase-budget classification. Slice H2 must either:

- implement explicit per-phase budget checks for non-provider phase boundaries and final assembly, with tests that can produce `phase_timeout`; or
- stop before implementation if producing `phase_timeout` would require broad chapter-orchestrator/provider redesign.

It is not acceptable to define a `phase_timeout` enum that no path can ever produce without recording that as a controller stop/defer decision.

### Safe Diagnostics

Allowed:

- run identity and timestamps
- terminal state
- timeout class
- chapter matrix
- safe prompt-cost counters
- provider attempt counts
- status codes / request IDs if already safe and scalar
- exception class names without secret-bearing payloads

Forbidden:

- API key
- Authorization header
- full prompt
- full draft
- raw provider response
- raw audit response
- provider stdout/stderr
- unredacted exception payloads that may contain request bodies or headers

## Implementation Slices

### Slice H0: Host API and Dependency Preflight

Objective: lock the exact `dayu.host` API surface before code edits.

Allowed files:

- `docs/reviews/*implementation-evidence*.md` for the later implementation gate only.

Actions:

- Confirm `dayu.host.Host`, `HostedRunSpec`, `HostedRunContext`, `RunState`, `RunCancelReason` and `CancelledError` import under `uv run`.
- Confirm current dependency declaration/lock already provides `dayu.host`; if not, stop for a dependency-declaration decision before editing runtime.
- Confirm no `dayu.engine` import is needed for direct operation execution.

Stop if `dayu.host` is not available or its direct-operation API differs from this plan.

### Slice H1: Host Runtime Adapter Package

Objective: add a thin Host package that owns lifecycle wrapping, not fund semantics.

Allowed files:

- `fund_agent/host/__init__.py`
- `fund_agent/host/runtime_governance.py`
- `tests/host/test_runtime_governance.py`
- `fund_agent/host/README.md`
- `fund_agent/README.md` only if needed to document the new current Host package boundary

Allowed changes:

- Define typed request/result dataclasses.
- Construct `HostedRunSpec` with `operation_name="fund_analysis_llm_report"`, `scene_name="fund_analysis_llm_report"`, explicit `timeout_ms`, safe metadata and no business fields in freeform payload.
- Call `Host.run_operation_sync()` for the synchronous Service operation.
- Record `started_at` and `completed_at` in the adapter; derive `deadline_at` from `started_at + timeout_seconds`.
- Convert public `timeout_seconds` to `HostedRunSpec.timeout_ms` with tested seconds-to-milliseconds conversion.
- Use `on_cancel` to return a fail-closed cancelled result when Host cancellation fires.
- Map observable Host cancellation/state and Service result completeness to terminal status.
- Surface cancellation as fail-closed result; no partial report is accepted.
- Expose a protocol-friendly entrypoint so tests can inject fake Host or fake executor.
- Bridge async `FundAnalysisService.analyze_with_llm()` with `asyncio.run()` only from the synchronous CLI adapter path; stop if the implementation would be called from inside an already-running event loop.

Non-goals:

- No provider construction.
- No Service prompt changes.
- No chapter orchestration changes except optional cancellation/deadline parameters in later slices.
- No `dayu.engine`.

Tests:

- Creates a Host-managed run and returns `run_id`, timestamps and terminal `succeeded` on complete fake result.
- Incomplete final assembly maps to terminal `failed`, no deterministic fallback.
- Host timeout/cancel maps to `run_deadline_exceeded`.
- `on_cancel` returns a fail-closed cancelled result.
- Async Service bridge works from the synchronous CLI adapter path.
- `timeout_seconds` converts to `HostedRunSpec.timeout_ms` exactly.
- Fake Host/executor can drive `UNSETTLED` mapping to fail-closed terminal `unsettled`.
- Host infrastructure exception maps to fail-closed safe runtime error.
- Safe diagnostics omit prompt, draft, raw responses and secret-like keys.
- No `extra_payload` field exists on the request/result.

### Slice H2: Service Cancellation and Deadline Propagation

Objective: let current Service execution body observe Host cancellation/deadline without moving business semantics into Host.

Allowed files:

- `fund_agent/services/fund_analysis_service.py`
- `fund_agent/services/chapter_orchestrator.py`
- `tests/services/test_fund_analysis_service_llm.py`
- `tests/services/test_chapter_orchestrator*.py` if present/needed

Allowed changes:

- Add optional explicit `cancellation_token` and `deadline_at` parameters to the LLM Service/orchestrator path.
- Check cancellation at stable phase boundaries: before writer, before auditor, before repair, before final assembly.
- Add the minimum explicit phase-budget check required to make `phase_timeout` producible, or stop with controller decision if that would require broad orchestrator/provider redesign.
- Do not require provider clients to know Host internals.
- Preserve existing provider runtime timeout taxonomy and diagnostics.
- If cancellation is observed, fail closed with terminal/cancelled state rather than returning a partial complete report.

Non-goals:

- No prompt text changes.
- No provider retry/budget tuning.
- No deterministic path changes.

Tests:

- Cancellation before writer prevents provider call and produces cancelled/fail-closed result.
- Cancellation between writer and auditor stops before auditor.
- A non-provider phase-budget breach produces `phase_timeout`.
- Deadline metadata is propagated to diagnostics without full prompt/draft/raw response.
- Existing `analyze_with_llm()` complete and incomplete tests remain valid.

### Slice H3: CLI `--use-llm` Host Entry

Objective: route explicit provider-backed CLI analysis through Host runtime governance.

Allowed files:

- `fund_agent/ui/cli.py`
- `tests/ui/test_cli.py`
- `fund_agent/README.md` only if current architecture docs need a short sync
- root `README.md` only if user-facing command behavior changes materially; otherwise no README change

Allowed changes:

- In `use_llm` branch, build provider clients as today.
- Build explicit Host runtime request.
- Call the Host adapter instead of naked `FundAnalysisService().analyze_with_llm()`.
- Preserve missing/invalid provider config fail-closed behavior.
- Preserve exit code `1` and empty stdout on incomplete LLM result.
- Ensure CLI error output includes safe `run_id`, `terminal_status`, timeout class and safe chapter matrix when available.

Non-goals:

- `checklist` does not gain `--use-llm`.
- Deterministic `analyze` does not enter Host.
- No provider tuning.

Tests:

- `--use-llm` calls Host adapter, not direct naked Service.
- Default deterministic analyze does not instantiate Host.
- Missing config still fails closed before provider execution and does not print secrets.
- Incomplete hosted result prints safe run summary and exits `1`.
- Complete hosted result prints report stdout.

### Slice H4: Diagnostic Secret Scan and Runtime Evidence

Objective: prove the adapter is safe enough for user-facing MVP readiness gating.

Allowed files:

- `docs/reviews/mvp-dayu-host-runtime-governance-adapter-implementation-evidence-20260601.md`
- `docs/reviews/mvp-dayu-host-runtime-governance-adapter-code-review-*.md`
- `docs/reviews/mvp-dayu-host-runtime-governance-adapter-controller-judgment-20260601.md`

Allowed changes:

- Evidence artifacts only.

Required validation:

- `uv run ruff check .`
- `uv run pytest --cov=fund_agent --cov-report=term-missing --cov-fail-under=50 -q`
- deterministic analyze `006597 / 2024` unchanged PASS
- deterministic checklist `006597 / 2024` unchanged PASS
- missing-config `--use-llm` fail-closed PASS
- real provider smoke: `uv run fund-analysis analyze 006597 --report-year 2024 --use-llm`
- cancellation/deadline tests PASS
- secret leak scan over changed diagnostics/artifacts PASS
- `rg -n "dayu\\.engine|ToolRegistry|ToolTrace" fund_agent tests` shows no new implementation dependency from this gate

The real provider smoke may still fail closed because the primary blocker is `provider_runtime_timeout_small_prompt`; acceptance for this implementation gate is Host terminal-state correctness and safe classification, not provider completion.

## Error Handling Rules

- Missing LLM config: fail closed; no provider execution; no deterministic fallback.
- Provider construction error: fail closed; no deterministic fallback.
- Provider timeout inside writer/auditor: classify as `provider_runtime_timeout` unless Host global deadline already fired.
- Host deadline: classify as `run_deadline_exceeded`; settle terminal state through Host cancellation.
- Phase budget expiry at Service boundary: classify as `phase_timeout`; if this cannot be implemented narrowly in Slice H2, stop rather than shipping a dead classification.
- Partial final assembly: terminal `failed`; stdout must not contain a partial report.
- Host unavailable/misconfigured: fail closed and report safe config/runtime error.

## Documentation Decision

Implementation gate must update docs only where current facts change:

- If `fund_agent/host` package is created, add `fund_agent/host/README.md`.
- If `fund_agent/README.md` currently says no Host package exists, update it briefly.
- If CLI user behavior changes only by safer diagnostics and same command, root `README.md` can remain unchanged.
- Do not update `docs/design.md`, `docs/implementation-control.md` or `docs/current-startup-packet.md` until implementation is accepted, then sync only short current-fact deltas.

## Review Requirements

Plan review must check:

- Host does not understand fund business semantics.
- Service still owns prompt/ExecutionContract semantics.
- No explicit parameter is moved into `extra_payload`.
- `dayu.host` is used for Host lifecycle; `dayu.engine` is not used.
- Timeout categories remain distinct.
- Cancellation/deadline propagation is testable.
- Safe diagnostics cannot leak secrets, full prompts, drafts or raw responses.
- Implementation slices are small enough for independent review.

## Stop Conditions

Stop before implementation if:

- `dayu.host` direct-operation API cannot support the planned lifecycle wrapper.
- Dependency declaration/lock status is unclear.
- Implementation requires `dayu.engine`, ToolRegistry, ToolTrace or Agent runner.
- Host would need to parse fund code, report year, CHAPTER_CONTRACT, prompt content or evidence anchors as business semantics.
- Any explicit parameter would be carried through `extra_payload`.
- Safe diagnostics require storing full prompt, draft, provider response or audit response.
- Provider timeout cannot be classified as one of `run_deadline_exceeded`, `phase_timeout`, `provider_runtime_timeout`.
- Any change would affect score, quality gate, golden, fixture promotion, release-readiness or PR state.

## Handoff Summary For Implementation Gate

Implement `fund_agent.host` as a thin `dayu.host` direct-operation adapter around the existing `FundAnalysisService.analyze_with_llm()` transition body. Do not migrate to Agent/tool-loop. Route only CLI `analyze --use-llm` through the adapter. Preserve deterministic default behavior and fail-closed semantics. Add tests for run lifecycle, cancellation, deadline, terminal status, CLI routing and safe diagnostics. Run full validation and real provider smoke, but do not require the provider smoke to complete 0-7 chapters unless the implementation also proves the endpoint timeout blocker disappeared.
