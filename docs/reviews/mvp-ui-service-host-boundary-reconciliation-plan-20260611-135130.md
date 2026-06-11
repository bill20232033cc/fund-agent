# UI-Service-Host Boundary Reconciliation Plan

## Scope

- Gate: `UI-Service-Host boundary reconciliation gate`
- Classification: `heavy`
- Mode: planning only
- Current accepted input: LLM execution request validation ordering checkpoint `336081e`; control sync checkpoint `d68ab39`
- Objective: reconcile current `--use-llm` execution ownership with `AGENTS.md` and design truth so UI remains a Service caller, Service owns business request/contract/provider orchestration and Host invocation, Host remains lifecycle-only, and Agent/Fund ownership is not blurred.

This plan does not authorize implementation until it passes independent review and controller judgment.

Classification note: the current control docs still list this gate as `standard`, but this plan intentionally upgrades it to `heavy` because it changes an architecture boundary and public layer ownership (`UI -> Service -> Host -> Agent`). If the plan is accepted, `docs/current-startup-packet.md` and `docs/implementation-control.md` must be synchronized after the accepted checkpoint to record the heavy classification. Implementation may not edit control docs.

## Truth Inputs

- `AGENTS.md`: UI must only depend on Service; Service owns business use-case orchestration, prompt/ExecutionContract assembly, provider construction/runtime ceilings and final product fail-closed mapping; Host owns lifecycle/deadline/cancel/events only and does not understand business fields.
- `docs/design.md`: current text still describes Route C as CLI giving a synchronous operation closure and timeout to local Host runner. That is current code fact but conflicts with the stricter UI boundary in `AGENTS.md`.
- `docs/implementation-control.md`: current gate is `UI-Service-Host boundary reconciliation gate`; Host durable session/resume/memory/outbox, Agent full tool-loop expansion, provider defaults/runtime changes and live commands are not authorized.
- `docs/current-startup-packet.md`: current entry is planning; no implementation write set is accepted yet.

## Repo Facts

- `fund_agent/ui/cli.py` imports Host types and `HostRuntimeRunner` directly.
- `fund_agent/ui/cli.py` also imports and calls `build_fund_llm_execution_request()` directly.
- `_run_llm_analysis_in_host()` currently lives in UI and instantiates `FundAnalysisService()` plus `HostRuntimeRunner()`.
- Existing UI tests assert UI passes only generic parameters to Host, but they still encode direct UI-to-Host ownership.
- Service already owns `build_fund_llm_execution_request()` and `FundAnalysisService.analyze_with_llm_execution()`.
- Host runtime tests already assert Host remains business-opaque.

## Problem Statement

Current code is internally disciplined in what it passes to Host, but ownership is still wrong by the strict architecture boundary:

```text
Current: UI -> Service request builder, UI -> Host runner -> Service operation -> Agent/Fund
Target:  UI -> Service hosted LLM use case -> Host runner -> Service operation -> Agent/Fund
```

The goal is not to add durable Host capabilities or change runtime behavior. The goal is to relocate the Host invocation boundary so UI no longer owns Host runner construction, Host run operation closure, or LLM execution request building.

## Non-Goals

- No live provider, endpoint, DNS, socket, curl, network, EID, PDF, FDR, extractor, analyze/checklist, golden/readiness, score-loop or release command.
- No provider default, model, base URL, timeout, retry, backoff, max-output, runtime budget, prompt payload mode or fail-closed semantic change.
- No Host durable session/resume/memory/reply outbox.
- No Agent full tool-loop/runtime expansion.
- No fallback/source acquisition change.
- No direct Service call to concrete source helper, PDF cache or downloader.
- No `extra_payload`, `payload`, `metadata`, `context`, `**kwargs` or open business parameter bag.
- No PR, push, merge, mark-ready or release-state change.

## Proposed Implementation Write Set

Allowed implementation files:

- `fund_agent/services/fund_analysis_service.py`
- `fund_agent/services/__init__.py`
- `fund_agent/ui/cli.py`
- `tests/services/test_fund_analysis_service_llm.py`
- `tests/ui/test_cli.py`
- `docs/design.md`
- `fund_agent/README.md`

No `fund_agent/host/runtime.py`, `fund_agent/agent/*`, `fund_agent/fund/documents/*`, provider config, `.gitignore`, root `README.md`, runtime artifact or control doc change is authorized during implementation. Control docs are updated only after acceptance.

## Proposed Design

Add a Service-owned hosted LLM use-case wrapper and make CLI call it:

1. Service defines a small return shape for hosted LLM execution, `FundLLMHostedRunResult`, containing exactly:
   - `analysis_result: FundLLMAnalysisResult | None`
   - `host_status: str`
   - `host_run_id: str`
   - `host_elapsed_ms: int | None`
   - `host_timeout_classification: str | None`
   - `host_safe_diagnostics: Mapping[str, object]`
   - `host_event_count: int`
   - `host_completed_at_iso: str | None`
   - `host_operation_result_present: bool`
   These are safe scalar or mapping fields projected by Service from `HostRunResult`; UI does not receive or inspect `HostRunResult`.
2. Service adds a public method such as `FundAnalysisService.analyze_with_llm_hosted(request, *, event_sink=None)`.
3. That Service method:
   - calls `build_fund_llm_execution_request(request, opt_in_mode="explicit_cli_flag")`;
   - creates the Host operation closure internally;
   - calls `HostRuntimeRunner().run_sync(...)` with only generic Host fields;
   - preserves existing quality gate exception propagation and incomplete-result fail-closed behavior;
   - returns the Service-owned hosted result to UI.
4. UI `analyze --use-llm` branch calls the Service hosted method and handles the returned Service result.
5. UI progress reporter stops importing Host event classes. It remains a UI-owned stderr renderer and consumes event objects by duck typing only:
   - `event_sink` returns `Callable[[object], None]`.
   - `handle_event(event: object)` accepts any object with public attributes used by the reporter.
   - A local helper `_host_event_type_name(event: object) -> str` reads `getattr(event, "event_type", None)`, then returns `event_type.value` when present, otherwise `str(event_type)`.
   - Event matching uses local string constants: `"run_started"`, `"phase_started"`, `"phase_completed"`, `"run_completed"`, `"run_failed"`, `"run_cancelled"`.
   - `_LLMProgressReporter` continues to read `event.run_id`, `event.phase`, `event.chapter_id`, `event.attempt`, `event.diagnostics` and `event.elapsed_ms` through `getattr(...)`; missing optional fields degrade to `None` and do not raise.
   - Terminal progress uses `FundLLMHostedRunResult.host_status` strings (`"succeeded"`, `"failed"`, `"cancelled"`, `"deadline_exceeded"`) instead of `HostRunStatus`.
   - No local duplicate Host enum classes are introduced in UI.
6. `docs/design.md` is updated after code/tests to state the new current fact: CLI/UI calls Service for hosted LLM execution; Service invokes Host; Host remains lifecycle-only and business-opaque.
7. `fund_agent/README.md` is updated only if its current architecture/current path wording still says CLI directly owns Host invocation.

## Implementation Slices

### Slice 1 - Service hosted LLM wrapper

- Move `_LLMIncompleteHostRunError` semantics and `_run_llm_analysis_in_host()` ownership from UI to Service.
- Keep Service as the only layer that calls `build_fund_llm_execution_request()` and `HostRuntimeRunner()`.
- Preserve current operation name `fund_analysis_llm_report`, timeout source `execution_request.runtime_plan.host_timeout_seconds`, event sink behavior and quality gate exception propagation.
- Do not change `analyze_with_llm_execution()` semantics.
- Export `FundLLMHostedRunResult` from `fund_agent/services/__init__.py` if UI imports the type or tests need it. `analyze_with_llm_hosted()` is an instance method on `FundAnalysisService` and does not require a separate function export.

### Slice 2 - UI call-site simplification

- Remove direct imports of `fund_agent.host` and `build_fund_llm_execution_request` from `fund_agent/ui/cli.py`.
- Make `--use-llm` call `FundAnalysisService().analyze_with_llm_hosted(request, event_sink=...)`.
- Keep stdout/stderr/error behavior unchanged.
- Keep progress heartbeat safe and stderr-only.
- Replace all UI uses of `HostRunResult`, `HostRunStatus`, `HostRunEvent`, `HostRunEventType`, `HostRunEventSink` and `HostRuntimeRunner` with the Service hosted result plus duck-typed event handling described above.
- Replace `_hosted_llm_incomplete_message()` and `_host_run_failed_message()` inputs so they accept the Service hosted result, not `HostRunResult`.

### Slice 3 - Tests

Update tests to prove:

- UI no longer imports `fund_agent.host`, `HostRuntimeRunner`, `HostRunStatus`, `HostRunResult`, `HostRunEventType`, `HostRunEventSink` or `build_fund_llm_execution_request`.
- UI `--use-llm` delegates to the Service hosted method and does not construct Host directly.
- Service hosted method calls Host with generic lifecycle parameters only and no business kwargs.
- Service hosted method propagates config/provider construction errors before Host run.
- Service hosted method preserves quality gate blocked/not-run exception behavior.
- Existing incomplete artifact/error behavior remains equivalent.
- Existing `tests/ui/test_cli.py` Host fake infrastructure must be migrated rather than patched around:
  - Remove `_FakeHostRuntimeRunner` and `_RaisingHostRuntimeRunner` from UI tests.
  - Replace CLI Host-run tests with fake Service objects whose `analyze_with_llm_hosted(request, event_sink=...)` records the request and event sink and returns a fake `FundLLMHostedRunResult`.
  - Replace direct `cli.HostRunEvent(...)` constructions with local tiny fake event objects in tests, for example a dataclass with `event_type`, `run_id`, `phase`, `chapter_id`, `attempt`, `elapsed_ms` and `diagnostics`; `event_type` may be a string or a tiny object with `.value`.
  - UI tests must not import `fund_agent.host` directly and must not reference `cli.HostRun*`.
  - Service tests, not UI tests, own fake Host runner assertions.

### Slice 4 - Documentation sync

- Update `docs/design.md` only after code/tests show the new current fact.
- Update `fund_agent/README.md` only if current wording describes old UI-owned Host invocation.
- Do not update `docs/implementation-control.md` or `docs/current-startup-packet.md` until post-acceptance controller sync.

## Acceptance Criteria

| ID | Criterion | Direct evidence |
|---|---|---|
| A1 | UI no longer directly imports or instantiates Host runtime | static test / `rg` evidence |
| A2 | UI no longer calls `build_fund_llm_execution_request()` | static test / `rg` evidence |
| A3 | Service owns hosted LLM request building and Host runner invocation | Service tests with fake Host runner |
| A4 | Host still receives only generic lifecycle parameters | Service tests equivalent to existing UI Host boundary tests |
| A5 | CLI output/error/progress behavior remains unchanged | focused `tests/ui/test_cli.py` |
| A6 | Provider/runtime/default/budget/typed path semantics unchanged | existing service LLM tests |
| A7 | Design truth updated after implementation to match code facts | `docs/design.md` diff review |
| A8 | No live/provider/EID/PDF/FDR/network command is run | command list / evidence |

## Validation Matrix

Required after implementation:

```bash
uv run pytest tests/ui/test_cli.py tests/services/test_fund_analysis_service_llm.py tests/services/test_execution_contract.py tests/host/test_runtime_runner.py -q
uv run ruff check fund_agent/ui/cli.py fund_agent/services/fund_analysis_service.py fund_agent/services/__init__.py tests/ui/test_cli.py tests/services/test_fund_analysis_service_llm.py
rg -n "from fund_agent.host|HostRuntimeRunner|HostRunStatus|HostRunResult|HostRunEventType|HostRunEventSink|build_fund_llm_execution_request" fund_agent/ui/cli.py
rg -n "from fund_agent.host|HostRuntimeRunner|HostRunStatus|HostRunResult|HostRunEventType|HostRunEventSink|cli\\.HostRun" tests/ui/test_cli.py
git diff --check
git diff --name-only
```

Both `rg` commands should return no matches after implementation.

## Review Checklist

Reviewers must verify:

- The plan resolves the AGENTS/design/code boundary conflict in favor of the AGENTS UI boundary.
- The plan does not move business semantics into Host.
- The plan does not introduce Host durable features or Agent runtime expansion.
- The plan does not alter provider runtime/defaults or live behavior.
- The write set is sufficient but not broader than needed.
- `docs/design.md` update is code-fact sync, not future design speculation.

## Residuals / Deferred Entries

- Host durable session/resume/memory/reply outbox remains deferred.
- Full Agent tool-loop/runtime expansion remains deferred.
- Provider live acceptance and runtime defaults remain deferred.
- LLM path parity with deterministic `_validate_request()` remains deferred unless reviewers require it as a direct boundary blocker.
