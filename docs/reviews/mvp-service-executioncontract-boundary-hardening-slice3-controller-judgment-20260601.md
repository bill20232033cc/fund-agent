# MVP Service ExecutionContract boundary hardening Slice 3 controller judgment

Date: 2026-06-01
Gate: `MVP Service ExecutionContract boundary hardening gate`
Slice: `Slice 3: CLI -> Host Uses Typed Execution Request`
Controller role: Gateflow controller
Decision: accepted Slice 3 checkpoint; no fix/re-review required

## Step Self-check

- Current gate / role: controller is closing the Slice 3 code review loop only; this artifact does not enter re-review, aggregate review, the next implementation slice, PR, push or release state.
- Source of truth: accepted plan `docs/reviews/mvp-service-executioncontract-boundary-hardening-plan-20260601.md`, implementation evidence `docs/reviews/mvp-service-executioncontract-boundary-hardening-slice3-implementation-evidence-20260601.md`, and AgentDS code review `docs/reviews/mvp-service-executioncontract-boundary-hardening-slice3-code-review-20260601.md`.
- Scope boundary: Slice 3 accepted files are `fund_agent/ui/cli.py`, `tests/ui/test_cli.py`, and current Slice 3 review/evidence/controller artifacts. Historical residual artifacts remain out of scope.
- Stop conditions: no accepted blocking findings, no validation failure, no unclear worktree ownership in Slice 3 files, and no external-state authorization needed.
- Evidence and validation: code review passed with no blocking findings; required combined validation, ruff, coverage and deterministic smoke validation passed.
- Next action: create local accepted Slice 3 checkpoint commit only; do not proceed to re-review or the next gate in this step.

## Review Inputs

- Implementation evidence: `docs/reviews/mvp-service-executioncontract-boundary-hardening-slice3-implementation-evidence-20260601.md`
- Code review artifact: `docs/reviews/mvp-service-executioncontract-boundary-hardening-slice3-code-review-20260601.md`
- Reviewer: AgentDS / Claude Code deepreview
- Review verdict: PASS, no blocking findings

## Controller Judgment On Review Observations

### O1: `asyncio.run()` inside sync Host closure

Judgment: `deferred-with-owner`

Reason: the current CLI path is synchronous, and the accepted Slice 3 plan explicitly keeps the CLI-owned async bridge inside the Host operation closure. This observation is a future compatibility concern for a possible async CLI, not a current boundary violation. No Slice 3 fix is justified because changing event-loop bridging now would expand scope beyond the accepted plan and risk altering fail-closed behavior.

Owner / destination: future async CLI or Host async-runner design gate, if the project introduces async Typer or calls `HostRuntimeRunner.run_sync()` from an existing event loop.

### O2: Tests use fakes exclusively for Host

Judgment: `deferred-with-owner`

Reason: Slice 3's objective is the CLI -> Service typed request boundary and the Host API call shape. The fakes assert the exact Host call contract (`operation_name`, `operation`, `timeout_seconds`, `session_id`) and no business kwargs. The accepted plan assigns broader Host boundary regression to Slice 4, including Host-focused tests and docs sync.

Owner / destination: Slice 4 Host boundary regression and docs sync.

### O3: `FundLLMExecutionRequest` type import in CLI

Judgment: `accepted`

Reason: `FundLLMExecutionRequest` is exported from `fund_agent.services` and used in CLI only as the opaque Service-owned request type. CLI construction remains delegated to `build_fund_llm_execution_request()`, and Host still receives only generic lifecycle inputs plus scalar timeout. This import does not leak Service internals or Fund business semantics into Host.

Required action: none.

## Blocking Findings Decision

Accepted blocking findings: none.

Controller decision: no fix and no re-review are required for Slice 3. The review observations above are either accepted as non-actionable in this slice or deferred with explicit owners.

## Validation

Targeted and combined validation:

```text
uv run pytest tests/host/test_runtime_state.py tests/host/test_runtime_runner.py tests/services/test_execution_contract.py tests/services/test_fund_analysis_service_llm.py tests/ui/test_cli.py -q
105 passed in 1.32s
```

Lint validation:

```text
uv run ruff check .
All checks passed!
```

Coverage gate:

```text
uv run pytest --cov=fund_agent --cov-report=term-missing --cov-fail-under=50 -q
1250 passed in 5.59s
Total coverage: 91.90%
Required test coverage of 50% reached.
```

Smoke validation:

```text
uv run fund-analysis analyze 006597 --report-year 2024 --dev-override --quality-gate-policy off
PASS: exited 0 and produced deterministic report markdown.
```

```text
uv run fund-analysis checklist 006597 --report-year 2024
PASS: exited 0 and produced checklist summary with `overall_signal: yellow` and `overall_status: watch`.
```

## Boundary Acceptance

- Service -> Host boundary: accepted. CLI obtains one Service-owned `FundLLMExecutionRequest`, and Host receives only `operation_name`, `operation`, `timeout_seconds` and `session_id`.
- Host business agnosticism: accepted for Slice 3. No Host code changed; CLI Host call carries no fund code, report year, chapter policy, ExecutionContract, provider client, or business kwargs.
- Deterministic `analyze/checklist`: accepted. Validation proves default deterministic paths do not call the LLM request builder or Host.
- `--use-llm` fail-closed behavior: accepted. Existing incomplete-result, timeout, quality-gate and Host-failure tests continue to pass.
- `extra_payload`: accepted. Slice 3 does not introduce `extra_payload` or open business payload bags.
- Negative boundary coverage: accepted for Slice 3. Default analyze/checklist and unsupported `checklist --use-llm` paths cover no-builder/no-Host behavior.

## Design/control Sync Status

`deferred by controller judgment to Slice 4 Host boundary regression and docs sync`.

Reason: Slice 3 is a CLI wiring slice. The accepted plan already assigns Host boundary regression and developer docs sync to Slice 4, including `fund_agent/README.md`, `fund_agent/host/README.md` and `tests/README.md`. Truth-source control docs must not be partially updated before the Slice 4 docs/control decision because that would describe a gate-wide boundary state before the planned Host regression/docs evidence is complete.

Owner / next entry point: Slice 4 controller handoff within the same `MVP Service ExecutionContract boundary hardening gate`.

## Residual Risks

- O1 async-in-sync closure: deferred to a future async CLI / Host async-runner design gate if async invocation becomes a real requirement.
- O2 real Host integration coverage: deferred to Slice 4 Host boundary regression and docs sync.
- Design/control truth-source sync: deferred to Slice 4 controller handoff and closeout decision.

No Slice 3 residual is blocking this accepted checkpoint.

## Accepted Checkpoint Scope

Eligible Slice 3 checkpoint files:

- `fund_agent/ui/cli.py`
- `tests/ui/test_cli.py`
- `docs/reviews/mvp-service-executioncontract-boundary-hardening-slice3-implementation-evidence-20260601.md`
- `docs/reviews/mvp-service-executioncontract-boundary-hardening-slice3-code-review-20260601.md`
- `docs/reviews/mvp-service-executioncontract-boundary-hardening-slice3-controller-judgment-20260601.md`

Historical residual artifacts are not part of this checkpoint.
