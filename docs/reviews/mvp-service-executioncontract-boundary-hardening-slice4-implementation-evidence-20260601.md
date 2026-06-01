# MVP Service ExecutionContract boundary hardening Slice 4 implementation evidence

Date: 2026-06-01
Gate: `MVP Service ExecutionContract boundary hardening gate`
Slice: `Slice 4 - Host Boundary Regression And Docs / Control Sync`
Role: Gateflow-governed implementation worker, not controller
Self-check: pass

## Worker Self-check

- Current gate / role: implementation worker for Slice 4 only; did not start `$gateflow`, code review, aggregate deepreview, PR, push, merge or release state.
- Source of truth: read `AGENTS.md`, accepted plan, Slice 3 controller judgment, `docs/design.md`, `docs/implementation-control.md` and `docs/current-startup-packet.md`.
- Scope boundary: touched only allowed Slice 4 tests/docs/control/evidence files; did not edit `fund_agent/agent/**`, `fund_agent/fund/**`, provider runtime implementation, score, quality gate, golden, fixture, release-readiness or PR state files.
- Stop conditions: no need for Host to inspect fund code/year/type/chapter policy/ExecutionContract business fields; docs did not claim async Host runner, durable session/resume/memory/outbox or Agent tool-loop as implemented.
- Evidence and validation: targeted Host/UI tests, combined Service/Host/UI tests and ruff passed; optional coverage status recorded below.

## Changed Files

- `tests/host/test_runtime_runner.py`
- `tests/ui/test_cli.py`
- `fund_agent/README.md`
- `fund_agent/host/README.md`
- `tests/README.md`
- `docs/design.md`
- `docs/implementation-control.md`
- `docs/current-startup-packet.md`
- `docs/reviews/mvp-service-executioncontract-boundary-hardening-slice4-implementation-evidence-20260601.md`

## Implemented Plan Items

- Added Host package boundary regression proving `fund_agent/host` does not import `fund_agent.services` or `fund_agent.fund`.
- Added Host source regression proving Host runner has no fund business semantics, Service ExecutionContract fields, chapter policy, provider runtime budget or `extra_payload`.
- Added Host safe diagnostics regression proving prompt, draft, raw provider/audit response and secret keys are rejected.
- Added CLI regression proving `--use-llm` Host failed terminal state remains fail-closed and does not fake a successful report.
- Added CLI source boundary regression proving the Host closure reads only `execution_request.runtime_plan.host_timeout_seconds` before calling `analyze_with_llm_execution()`.
- Synced developer docs and truth-source docs to the accepted current fact: Service owns `FundLLMExecutionRequest` / `FundLLMExecutionContract`; Host remains lifecycle-only and business-agnostic.

## Validation

- `uv run pytest tests/host/test_runtime_runner.py tests/ui/test_cli.py -q`
  - Result: PASS
  - Evidence: `67 passed in 1.24s`
- `uv run pytest tests/host/test_runtime_state.py tests/host/test_runtime_runner.py tests/services/test_execution_contract.py tests/services/test_fund_analysis_service_llm.py tests/ui/test_cli.py -q`
  - Result: PASS
  - Evidence: `110 passed in 1.19s`
- `uv run ruff check .`
  - Result: PASS
  - Evidence: `All checks passed!`
- `uv run pytest --cov=fund_agent --cov-report=term-missing --cov-fail-under=50 -q`
  - Result: PASS
  - Evidence: `1255 passed in 5.87s`; total coverage `91.90%`, required `50%` reached.

## Docs / Control Sync Status

Status: synced in Slice 4.

- `fund_agent/README.md` now describes `CLI -> Service prepares FundLLMExecutionRequest / ExecutionContract -> Host runner -> Service -> Fund` for `analyze --use-llm`.
- `fund_agent/host/README.md` now states Host receives only generic operation/deadline/session inputs and must not inspect Service ExecutionContract business fields.
- `tests/README.md` now documents `tests/services/test_execution_contract.py`, typed request CLI tests and Host boundary regressions.
- `docs/design.md`, `docs/implementation-control.md` and `docs/current-startup-packet.md` now record the current completed fact: internalized process-local Host runner plus Service-owned ExecutionContract / `FundLLMExecutionRequest` boundary for `analyze --use-llm`.
- Future-only items remain explicitly future-only: async Host runner, durable session/resume/memory/outbox, Agent tool-loop / Agent engine migration and direct dayu runtime integration.

## Boundary Assertions

- Host business-agnostic: pass. Host package import/source tests assert no Service/Fund imports and no fund/ExecutionContract business terms in Host source.
- Service-owned typed request: pass. CLI regression asserts Host closure uses Service-owned request only to read `runtime_plan.host_timeout_seconds` and delegates execution to `analyze_with_llm_execution()`.
- No `extra_payload` business params: pass. Host and CLI boundary tests assert no `extra_payload`; Service contract tests remain in the required combined validation.
- Deterministic analyze/checklist unchanged: pass. Existing CLI negative-boundary tests still pass: default `analyze` and `checklist` do not call the LLM request builder or Host.
- `--use-llm` fail-closed unchanged: pass. Missing config, provider construction error, incomplete LLM result, Host terminal failure and quality gate block/not-run tests still pass.
- Safe diagnostics / terminal state preserved: pass. Host safe diagnostic forbidden-key tests and CLI failed-terminal-state tests prove exceptions are not swallowed and no success is faked.

## Residual Risks

- O1 async-in-sync closure: deferred-with-owner to future async CLI / Host async-runner design gate if async invocation becomes a real requirement.
- O2 fake-only Host testing: handled in this slice with direct Host package boundary/source regressions and Host safe diagnostics tests; no remaining O2 residual.
- Provider endpoint runtime reliability: existing residual `provider_runtime_timeout_small_prompt`; owner remains future provider endpoint calibration/runtime diagnostic gate.
- Durable Host capabilities: async runner, durable session/resume/memory/reply outbox remain future Host gates.
- Agent engine/tool-loop: future Agent/tool-loop migration gate; not part of Slice 4.

## Blocking Questions

None.
