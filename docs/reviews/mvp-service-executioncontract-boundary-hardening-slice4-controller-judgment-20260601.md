# MVP Service ExecutionContract boundary hardening Slice 4 controller judgment

Date: 2026-06-01
Gate: `MVP Service ExecutionContract boundary hardening gate`
Slice: `Slice 4 - Host Boundary Regression And Docs / Control Sync`
Controller role: Gateflow controller
Decision: accepted Slice 4 checkpoint; no fix/re-review required

## Step Self-check

- Current gate / role: controller is closing the Slice 4 code review loop only; this artifact does not enter aggregate deepreview, PR, push or release state.
- Source of truth: accepted plan `docs/reviews/mvp-service-executioncontract-boundary-hardening-plan-20260601.md`, Slice 4 implementation evidence, AgentDS code review, current diff and controller-run validation.
- Scope boundary: Slice 4 accepted files are Host/UI regression tests, developer docs, design/control/startup truth-source sync, and current Slice 4 review/evidence/controller artifacts. Historical residual artifacts remain out of scope.
- Stop conditions: no accepted blocking findings, no validation failure, no unclear Slice 4 worktree ownership and no external-state authorization needed.
- Evidence and validation: code review passed with no blocking findings; required targeted validation, combined validation, ruff and coverage gate passed.
- Next action: create local accepted Slice 4 checkpoint commit, then evaluate aggregate deepreview entry because Slice 4 is the final approved implementation slice for this gate.

## Review Inputs

- Implementation evidence: `docs/reviews/mvp-service-executioncontract-boundary-hardening-slice4-implementation-evidence-20260601.md`
- Code review artifact: `docs/reviews/mvp-service-executioncontract-boundary-hardening-slice4-code-review-20260601.md`
- Reviewer: AgentDS / Claude Code deepreview
- Review verdict: PASS, no blocking findings

## Controller Judgment On Review Observations

### O1: Source-scan tests are intentionally brittle

Judgment: `accepted`

Reason: these tests intentionally act as boundary tripwires. The gate objective is to harden architectural boundaries, so failing loudly on future imports, business terms or CLI Host-closure drift is desirable. Refactors that legitimately rename or move code should update these tests in the same future change.

Required action: none.

### O2: CLI Host closure captures full execution_request

Judgment: `accepted`

Reason: the closure must pass the opaque Service-owned `FundLLMExecutionRequest` back to Service. The Host runner receives only a callable plus generic lifecycle inputs and never observes the typed request. The new CLI source regression verifies the closure reads only `runtime_plan.host_timeout_seconds` before delegating to `analyze_with_llm_execution()`.

Required action: none.

### O3: Safe diagnostics test uses specific keys while implementation uses substring matching

Judgment: `accepted`

Reason: the test keys are representative public boundary cases and are covered by broader implementation matching. Broader matching is stricter than the test examples and aligns with the safe diagnostics contract.

Required action: none.

## Blocking Findings Decision

Accepted blocking findings: none.

Controller decision: no fix and no re-review are required for Slice 4. Review observations are accepted as non-blocking boundary-test design choices.

## Validation

Targeted Slice 4 validation:

```text
uv run pytest tests/host/test_runtime_runner.py tests/ui/test_cli.py -q
67 passed in 1.79s
```

Combined gate validation:

```text
uv run pytest tests/host/test_runtime_state.py tests/host/test_runtime_runner.py tests/services/test_execution_contract.py tests/services/test_fund_analysis_service_llm.py tests/ui/test_cli.py -q
110 passed in 1.82s
```

Lint validation:

```text
uv run ruff check .
All checks passed!
```

Coverage gate:

```text
uv run pytest --cov=fund_agent --cov-report=term-missing --cov-fail-under=50 -q
1255 passed in 6.01s
Total coverage: 91.90%
Required test coverage of 50% reached.
```

## Boundary Acceptance

- Host business agnosticism: accepted. Host tests assert no Service/Fund imports and no fund business / ExecutionContract terms in Host implementation.
- Service-owned typed request: accepted. CLI tests assert Host bridge only reads the Service runtime plan timeout scalar and delegates the typed request back to Service.
- `extra_payload`: accepted. Host and CLI source regressions reject `extra_payload`; Service contract tests remain in combined validation.
- Deterministic `analyze/checklist`: accepted. Existing negative-boundary tests still prove no default LLM builder / Host execution.
- `--use-llm` fail-closed behavior: accepted. Host terminal failure, missing config, provider construction error, incomplete result and quality-gate tests remain passing.
- Safe diagnostics / terminal state: accepted. Host rejects forbidden prompt/draft/raw response/secret diagnostic keys and CLI does not fake success on failed terminal state.
- Docs/control sync: accepted. Developer docs and truth-source docs now describe current code facts only, while keeping async Host runner, durable session/resume/memory/outbox and Agent tool-loop as future gates.

## Residual Risks

- O1 async-in-sync CLI Host closure from Slice 3: deferred-with-owner to a future async CLI / Host async-runner design gate if async invocation becomes required.
- O2 fake-only Host testing from Slice 3: closed by Slice 4 Host package boundary/source regressions and CLI terminal-state regression; no remaining O2 residual.
- Source-scan test brittleness: accepted as intentional boundary regression design; future refactors must update tests with the same change.
- Provider endpoint runtime reliability: existing `provider_runtime_timeout_small_prompt`, owner remains future provider endpoint calibration / runtime diagnostic gate.
- Durable Host capabilities and Agent engine/tool-loop: future Host / Agent gates; not part of this Service ExecutionContract boundary gate.

No Slice 4 residual is blocking this accepted checkpoint.

## Accepted Checkpoint Scope

Eligible Slice 4 checkpoint files:

- `tests/host/test_runtime_runner.py`
- `tests/ui/test_cli.py`
- `fund_agent/README.md`
- `fund_agent/host/README.md`
- `tests/README.md`
- `docs/design.md`
- `docs/implementation-control.md`
- `docs/current-startup-packet.md`
- `docs/reviews/mvp-service-executioncontract-boundary-hardening-slice4-implementation-evidence-20260601.md`
- `docs/reviews/mvp-service-executioncontract-boundary-hardening-slice4-code-review-20260601.md`
- `docs/reviews/mvp-service-executioncontract-boundary-hardening-slice4-controller-judgment-20260601.md`

Historical residual artifacts are not part of this checkpoint.

## Aggregate Deepreview Decision

Slice 4 is the final implementation slice in the accepted plan. After the local Slice 4 accepted checkpoint commit is created, the controller should enter aggregate deepreview for the completed `MVP Service ExecutionContract boundary hardening gate`, using the Gateflow aggregate review path and preserving the no-push / no-PR external-state boundary.
