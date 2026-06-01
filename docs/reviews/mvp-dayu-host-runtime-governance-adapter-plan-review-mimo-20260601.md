# Plan Review: MVP dayu.host runtime governance adapter

Date: 2026-06-01
Reviewer: MiMo
Target plan: `docs/reviews/mvp-dayu-host-runtime-governance-adapter-plan-20260601.md`
Gate: `MVP dayu.host runtime governance adapter plan gate`
Classification: heavy

## Conclusion

**pass-with-risks**

Plan is code-generation-ready with no blocking findings. The architecture is sound, scope is appropriately narrow, and the Host/service boundary is correctly drawn. There are 5 moderate risks that the implementation gate should explicitly address; none require plan revision before implementation starts.

## Verification Performed

- Confirmed `dayu.host.Host`, `HostedRunSpec`, `HostedRunContext`, `RunState`, `RunCancelReason`, `CancelledError`, `CancellationToken` are importable under `uv run`.
- Confirmed `run_operation_sync` signature: `(self, *, spec: HostedRunSpec, operation: Callable[[HostedRunContext], TSyncResult], on_cancel: Callable[[], TSyncResult] | None = None) -> TSyncResult`.
- Confirmed `HostedRunContext.__init__` takes `(run_id: str, cancellation_token: CancellationToken)` — no `started_at`, `deadline_at`, or `RunState` on the context.
- Confirmed `RunState` enum: `CREATED`, `QUEUED`, `RUNNING`, `SUCCEEDED`, `FAILED`, `CANCELLED`, `UNSETTLED`.
- Confirmed `RunCancelReason` enum: `USER_CANCELLED`, `TIMEOUT`.
- Confirmed `CancellationToken` has `is_cancelled() -> bool`, `raise_if_cancelled()`, `cancel()`, `wait()`.
- Confirmed `HostedRunSpec` required field: only `operation_name`; `timeout_ms`, `session_id`, `scene_name`, `metadata` all optional.
- Confirmed current CLI `analyze --use-llm` path: `cli.py:243-251` calls `_build_llm_clients_or_fail()` then `FundAnalysisService().analyze_with_llm()` via `asyncio.run()`.
- Confirmed `FundAnalysisService.analyze_with_llm()` is async, signature at `fund_analysis_service.py:585-592`.
- Confirmed `orchestrate_chapters()` is synchronous (`chapter_orchestrator.py:585`).
- Confirmed current code has no `fund_agent/host` package and no Host/dayu runtime in production path.

## Findings

### F1 (Moderate Risk): Async/sync bridging gap

The plan specifies `dayu.host.Host.run_operation_sync()` wrapping the Service call, but `FundAnalysisService.analyze_with_llm()` is `async`. Inside `run_operation_sync`, the caller is already in a synchronous context. If the CLI's event loop is still running (e.g., nested `asyncio.run()`), this will raise `RuntimeError`.

The plan's Target Call Path shows `operation(HostedRunContext) -> FundAnalysisService.analyze_with_llm(...)` without specifying the bridging mechanism. The implementation must choose one of:
- `asyncio.run()` (works only if no outer loop is running — current CLI uses `asyncio.run()` at the top level, so the Host adapter would be called from sync CLI code, meaning this is safe)
- `loop.run_until_complete()` (works if a loop exists but isn't running)
- Use `Host.run_operation_stream()` or another async variant if available

**Recommendation**: Implementation slice H1 should explicitly document that the CLI calls the Host adapter synchronously (no outer event loop), and the adapter's `operation` callable uses `asyncio.run()` internally. Add a test confirming this works.

### F2 (Moderate Risk): Host API surface gap — adapter must compute timestamps and derive terminal state

The plan's Host Runtime Result includes `started_at`, `deadline_at`, `completed_at`, and `terminal_status` derived from Host `RunState`. However, `HostedRunContext` only provides `run_id` and `cancellation_token` — no timestamps, no `RunState`.

The adapter must:
1. Record `started_at = datetime.now(UTC)` before calling `run_operation_sync`.
2. Compute `deadline_at = started_at + timeout_seconds`.
3. Derive `terminal_status` from the operation outcome and exception handling, not from reading `RunState` directly.

For `RunState`, the adapter catches `CancelledError` (Host cancelled → `cancelled`) or inspects the result (operation completed → check assembly completeness). `UNSETTLED` is not directly observable from the adapter's perspective — it would only arise if the Host infrastructure itself is in an indeterminate state.

**Recommendation**: Slice H1 implementation should explicitly code the timestamp computation and terminal status derivation logic. The test for UNSETTLED should use a mock/fake Host that returns UNSETTLED behavior, not rely on the real Host producing it.

### F3 (Moderate Risk): `phase_timeout` requires new Service behavior

The plan defines three timeout categories: `run_deadline_exceeded`, `phase_timeout`, `provider_runtime_timeout`. The current Service has provider-level retry budgets (timeout-only bounded retry) but no phase-level timeout concept. The plan's Error Handling Rules state "Phase budget expiry at Service boundary: classify as `phase_timeout`", and Slice H2 says "Check cancellation at stable phase boundaries: before writer, before auditor, before repair, before final assembly."

The distinction between "checking cancellation at phase boundaries" (existing Host cancellation token) and "phase budget expiry" (new Service-level per-phase timeout) is not explicit. If only cancellation checks are added, `phase_timeout` can never be produced — only `run_deadline_exceeded` (Host deadline) or `provider_runtime_timeout` (provider HTTP timeout) would fire.

**Recommendation**: Slice H2 should clarify whether `phase_timeout` is in-scope for this gate. If yes, it needs a new per-phase timeout mechanism in the Service/orchestrator. If no, the timeout classification should be reduced to two classes for this gate, with `phase_timeout` deferred to a future gate. The plan currently allows this ambiguity.

### F4 (Moderate Risk): `on_cancel` callback not mentioned

`run_operation_sync` accepts an `on_cancel: Callable[[], TSyncResult] | None` parameter that the Host calls when the run is cancelled. This is the primary mechanism for producing a fail-closed cancellation result. The plan mentions `CancellationToken` for the Service to observe cancellation, but does not mention `on_cancel` for the adapter's own cancellation handling.

Without `on_cancel`, if the Host cancels the run, the operation callable would need to catch `CancelledError` internally or the adapter would get an unhandled exception.

**Recommendation**: Slice H1 should specify using `on_cancel` to return a fail-closed `HostRuntimeResult(terminal_status="cancelled", ...)` when the Host cancels. The Service-side cancellation checks (Slice H2) are complementary — they let the Service stop work early, but `on_cancel` handles the case where the Host force-cancels.

### F5 (Low Risk): `timeout_ms` vs `timeout_seconds` unit mismatch

The plan's Host Runtime Request uses `timeout_seconds: int`, but `HostedRunSpec` uses `timeout_ms: int | None`. The adapter must convert (`timeout_ms = timeout_seconds * 1000`). This is trivial but an easy implementation bug.

**Recommendation**: Slice H1 test should verify the conversion. Consider using `timeout_ms` consistently in the adapter internals to avoid confusion.

## Architecture Boundary Check

| Check | Result |
|-------|--------|
| Host does not understand fund business semantics | PASS — Host adapter wraps Service call as opaque operation; no fund code, report year, CHAPTER_CONTRACT, or prompt content in Host logic |
| Service still owns prompt/ExecutionContract semantics | PASS — Service builds orchestration input, chapter policy, and assembly policy; Host adapter only receives typed request |
| No explicit parameter in `extra_payload` | PASS — Host Runtime Request has explicit typed fields; plan explicitly forbids `extra_payload` |
| `dayu.host` used for Host lifecycle; `dayu.engine` not used | PASS — plan explicitly lists banned imports and stop conditions |
| Timeout categories remain distinct | PASS with risk (see F3) — three categories defined but `phase_timeout` may not be producible without new Service behavior |
| Cancellation/deadline propagation testable | PASS — plan specifies phase boundary checks and test cases |
| Safe diagnostics cannot leak secrets | PASS — allowed/forbidden lists are thorough; plan explicitly forbids API key, Authorization header, full prompt, full draft, raw responses |
| Implementation slices small enough for independent review | PASS — 5 slices (H0-H4) with clear allowed files, non-goals, and stop conditions per slice |
| Docs decision correct | PASS — plan correctly defers `docs/design.md` and `docs/implementation-control.md` updates until implementation is accepted |
| Stop conditions sufficient | PASS — 8 stop conditions covering dependency, boundary violation, and semantic scope |

## Slice Readiness Assessment

| Slice | Ready | Notes |
|-------|-------|-------|
| H0: API Preflight | Yes | Dayu.host confirmed available; all imports verified |
| H1: Host Runtime Adapter | Yes with F1/F2/F4/F5 risks | Must address async/sync bridging, timestamp computation, `on_cancel` callback, unit conversion |
| H2: Cancellation/Deadline Propagation | Yes with F3 risk | Must clarify whether `phase_timeout` is in-scope or deferred |
| H3: CLI Entry | Yes | Straightforward wiring change; allowed files correctly scoped |
| H4: Diagnostic Evidence | Yes | Evidence-only slice; no code changes |

## Test Matrix Adequacy

The plan's test requirements cover:
- Host-managed run lifecycle (run_id, timestamps, terminal status)
- Incomplete assembly → terminal `failed`
- Host timeout/cancel → `run_deadline_exceeded`
- Safe diagnostics leak scan
- No `extra_payload` on request/result
- Cancellation before writer, between writer and auditor
- Deadline metadata propagation
- Existing tests remain valid
- CLI routing through Host adapter
- Missing config fail-closed

**Gaps** (should be addressed in implementation gate):
- UNSETTLED state handling (use mock Host)
- Host infrastructure exception (e.g., `run_operation_sync` raises unexpected error)
- `on_cancel` callback behavior
- Async/sync bridging correctness
- `timeout_seconds` → `timeout_ms` conversion

## Residual Risks

1. **Real provider smoke may still fail closed**: The plan correctly notes this — the primary blocker is `provider_runtime_timeout_small_prompt`, which this gate does not fix. Acceptance is Host terminal-state correctness and safe classification, not provider completion.
2. **`phase_timeout` may be dead code**: If H2 only adds cancellation checks (no per-phase timeout), the `phase_timeout` classification is defined but never produced. This is acceptable if documented as future work.
3. **`UNSETTLED` may never occur in practice**: The Host would need to be in an infrastructure failure state. The plan's fail-closed handling is correct as a safety net, but the test should use a mock.
