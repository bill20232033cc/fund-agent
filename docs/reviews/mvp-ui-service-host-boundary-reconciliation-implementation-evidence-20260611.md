# UI-Service-Host Boundary Reconciliation Implementation Evidence

## Scope

- Gate: `UI-Service-Host boundary reconciliation gate`
- Classification: `heavy`
- Accepted plan checkpoint: `d6fe6db`
- Control sync checkpoint before implementation: `6104ab5`
- Plan: `docs/reviews/mvp-ui-service-host-boundary-reconciliation-plan-20260611-135130.md`
- Controller judgment: `docs/reviews/mvp-ui-service-host-boundary-reconciliation-plan-controller-judgment-20260611-140916.md`
- Implementation worker: AgentCodex (`agents:0.1`)

## Files Changed

- `fund_agent/services/fund_analysis_service.py`
- `fund_agent/services/__init__.py`
- `fund_agent/ui/cli.py`
- `tests/services/test_fund_analysis_service_llm.py`
- `tests/ui/test_cli.py`
- `docs/design.md`
- `fund_agent/README.md`

All changed tracked files are within the accepted implementation write set.

## Implementation Summary

- Added Service-owned `FundLLMHostedRunResult` with safe scalar/mapping Host projection fields.
- Added `FundAnalysisService.analyze_with_llm_hosted(request, *, event_sink=None)`.
- Moved hosted LLM request building and Host invocation ownership from UI into Service:
  - Service builds `FundLLMExecutionRequest` with `opt_in_mode="explicit_cli_flag"`.
  - Service calls `HostRuntimeRunner().run_sync(...)`.
  - Host receives only generic lifecycle parameters: `operation_name`, `operation`, `timeout_seconds`, optional `event_sink`.
  - Service preserves operation name `fund_analysis_llm_report` and timeout source `execution_request.runtime_plan.host_timeout_seconds`.
- UI `analyze --use-llm` now calls `FundAnalysisService().analyze_with_llm_hosted(request, event_sink=...)`.
- UI no longer imports `fund_agent.host` symbols or `build_fund_llm_execution_request`.
- `_LLMProgressReporter` now consumes duck-typed event objects:
  - sink type is `Callable[[object], None]`
  - event matching uses event-type strings
  - optional fields are read through attributes or diagnostics mapping
  - terminal progress uses `FundLLMHostedRunResult.host_status` and `host_elapsed_ms`
- UI tests were migrated from Host runner fakes to Service hosted fakes and local fake event objects.
- Service tests now own Host runner boundary assertions for hosted LLM execution.
- `docs/design.md` and `fund_agent/README.md` were synchronized to current code facts: UI calls Service hosted LLM use case; Service invokes Host; Host remains lifecycle-only and business-opaque.

## Boundary Evidence

Command:

```bash
rg -n "from fund_agent.host|HostRuntimeRunner|HostRunStatus|HostRunResult|HostRunEventType|HostRunEventSink|build_fund_llm_execution_request" fund_agent/ui/cli.py
```

Result: no matches.

Command:

```bash
rg -n "from fund_agent.host|HostRuntimeRunner|HostRunStatus|HostRunResult|HostRunEventType|HostRunEventSink|cli\\.HostRun" tests/ui/test_cli.py
```

Result: no matches.

Command:

```bash
rg -n "HostRuntimeRunner|HostRunStatus|HostRunResult|HostRunEvent|build_fund_llm_execution_request|FundLLMExecutionRequest|analyze_with_llm_execution_called|last_execution_request|last_host_context|_FakeHostRuntimeRunner|_RaisingHostRuntimeRunner" tests/ui/test_cli.py fund_agent/ui/cli.py
```

Result: no matches.

## Validation

Command:

```bash
uv run pytest tests/ui/test_cli.py tests/services/test_fund_analysis_service_llm.py tests/services/test_execution_contract.py tests/host/test_runtime_runner.py -q
```

Result:

```text
147 passed in 0.90s
```

Command:

```bash
uv run ruff check fund_agent/ui/cli.py fund_agent/services/fund_analysis_service.py fund_agent/services/__init__.py tests/ui/test_cli.py tests/services/test_fund_analysis_service_llm.py
```

Result:

```text
All checks passed!
```

Command:

```bash
git diff --check
```

Result: passed.

Command:

```bash
git diff --name-only
```

Result:

```text
docs/design.md
fund_agent/README.md
fund_agent/services/__init__.py
fund_agent/services/fund_analysis_service.py
fund_agent/ui/cli.py
tests/services/test_fund_analysis_service_llm.py
tests/ui/test_cli.py
```

Command:

```bash
git status --branch --short
```

Result summary:

- Branch: `feat/mvp-llm-incomplete-run-artifacts`
- Tracked modified files: the seven accepted write-set files listed above
- Existing unrelated untracked workspace residue remains untouched

## Non-Goals Preserved

- No Host durable session/resume/memory/reply outbox implementation.
- No Agent full tool-loop/runtime expansion.
- No provider default/model/base URL/timeout/retry/backoff/max-output/runtime budget/prompt payload mode change.
- No fallback/source acquisition change.
- No `extra_payload`, open payload bag, hidden kwargs or metadata/context business parameter bag.
- No live provider/EID/PDF/FDR/network/extractor/analyze/checklist/golden/readiness/release command.
- No staging, commit, push, PR, merge, cleanup, delete, move or archive action by implementation worker.

## Residuals

- Existing unrelated untracked workspace residue remains and is still owned by later artifact disposition / release-readiness gates.
- LLM path parity with deterministic `_validate_request()` remains deferred per accepted plan.
- Host durable features, full Agent runtime expansion and live provider acceptance remain deferred.
