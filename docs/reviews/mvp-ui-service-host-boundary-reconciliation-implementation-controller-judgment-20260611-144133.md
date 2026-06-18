# UI-Service-Host Boundary Reconciliation Implementation Controller Judgment

## Scope

- Gate: `UI-Service-Host boundary reconciliation gate`
- Classification: `heavy`
- Judgment type: implementation controller judgment
- Plan checkpoint: `d6fe6db`
- Pre-implementation control sync checkpoint: `6104ab5`
- Implementation evidence: `docs/reviews/mvp-ui-service-host-boundary-reconciliation-implementation-evidence-20260611.md`
- DS review: `docs/reviews/mvp-ui-service-host-boundary-reconciliation-implementation-review-ds-20260611-144133.md`
- MiMo review: `docs/reviews/mvp-ui-service-host-boundary-reconciliation-implementation-review-mimo-20260611-144133.md`
- Verdict: `ACCEPT_WITH_RESIDUALS`

## Controller Decision

The implementation is accepted.

The implementation satisfies the accepted target:

```text
Current before gate: UI -> Service request builder, UI -> Host runner -> Service operation -> Agent/Fund
Current after gate:  UI -> Service hosted LLM use case -> Host runner -> Service operation -> Agent/Fund
```

This preserves the `AGENTS.md` and `docs/design.md` boundary:

- UI depends on Service for `--use-llm` hosted execution.
- Service owns business request/contract/provider orchestration, hosted run invocation and final fail-closed mapping.
- Host remains lifecycle-only and business-opaque.
- Agent/Fund ownership is unchanged.

## Accepted Facts

- `FundLLMHostedRunResult` is now the Service-owned safe projection consumed by UI.
- `FundAnalysisService.analyze_with_llm_hosted(request, *, event_sink=None)` is now the Service-owned hosted LLM use-case method.
- UI production code no longer imports `fund_agent.host` symbols or `build_fund_llm_execution_request`.
- UI production code no longer constructs or invokes `HostRuntimeRunner`.
- `_LLMProgressReporter` consumes duck-typed event objects and hosted result strings rather than Host types.
- UI tests no longer depend on `cli.HostRun*` or fake Host runners.
- Service tests now own hosted Host-runner boundary assertions.
- `docs/design.md` and `fund_agent/README.md` now describe the current code fact that Service invokes Host for `--use-llm`.

## Validation Basis

Controller independently verified:

```bash
uv run pytest tests/ui/test_cli.py tests/services/test_fund_analysis_service_llm.py tests/services/test_execution_contract.py tests/host/test_runtime_runner.py -q
```

Result: `147 passed in 0.90s`.

```bash
uv run ruff check fund_agent/ui/cli.py fund_agent/services/fund_analysis_service.py fund_agent/services/__init__.py tests/ui/test_cli.py tests/services/test_fund_analysis_service_llm.py
```

Result: `All checks passed!`

```bash
rg -n "from fund_agent.host|HostRuntimeRunner|HostRunStatus|HostRunResult|HostRunEventType|HostRunEventSink|build_fund_llm_execution_request" fund_agent/ui/cli.py
```

Result: no matches.

```bash
rg -n "from fund_agent.host|HostRuntimeRunner|HostRunStatus|HostRunResult|HostRunEventType|HostRunEventSink|cli\\.HostRun" tests/ui/test_cli.py
```

Result: no matches.

```bash
rg -n "HostRuntimeRunner|HostRunStatus|HostRunResult|HostRunEvent|build_fund_llm_execution_request|FundLLMExecutionRequest|analyze_with_llm_execution_called|last_execution_request|last_host_context|_FakeHostRuntimeRunner|_RaisingHostRuntimeRunner" tests/ui/test_cli.py fund_agent/ui/cli.py
```

Result: no matches.

```bash
git diff --check
```

Result: passed.

```bash
git diff --name-only
```

Result: only accepted implementation write-set files and review artifacts are modified or added.

## Review Disposition

- AgentDS: `ACCEPT`.
- AgentMiMo: `ACCEPT`.
- No blocking findings remain.

## Residuals

- Existing unrelated untracked workspace residue remains deferred to runtime artifact disposition / ignore-rule planning and release-readiness cleanliness gates.
- LLM path parity with deterministic `_validate_request()` remains deferred.
- Host durable session/resume/memory/reply outbox remains deferred.
- Full Agent tool-loop/runtime expansion remains deferred.
- Provider live acceptance and runtime default changes remain deferred.

## Non-Goals Preserved

- No live provider/EID/PDF/FDR/network command was run.
- No source/fallback expansion was introduced.
- No provider default/runtime/budget change was introduced.
- No Host durable feature or Agent full runtime expansion was introduced.
- No PR, push, merge, mark-ready or release-state action was taken.

## Next Action

Create a local accepted implementation checkpoint for the seven implementation files and this evidence/review/judgment artifact set. Then synchronize `docs/current-startup-packet.md` and `docs/implementation-control.md` to point to the accepted implementation checkpoint and advance the next mainline entry to `Runtime artifact disposition / ignore-rule planning gate`.
