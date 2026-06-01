# MVP Service ExecutionContract boundary hardening Slice 4 code review

Date: 2026-06-01
Reviewer: code-review agent (gateflow review worker)
Gate: `MVP Service ExecutionContract boundary hardening gate`
Slice: `Slice 4 - Host Boundary Regression And Docs / Control Sync`
Verdict: **PASS — no blocking findings**

## Review Scope

- `tests/host/test_runtime_runner.py` — 3 new Host boundary regression tests
- `tests/ui/test_cli.py` — 2 new CLI Host boundary regression tests
- `fund_agent/README.md`, `fund_agent/host/README.md`, `tests/README.md` — developer docs sync
- `docs/design.md`, `docs/implementation-control.md`, `docs/current-startup-packet.md` — truth-source docs sync
- Implementation evidence artifact `docs/reviews/mvp-service-executioncontract-boundary-hardening-slice4-implementation-evidence-20260601.md`

## Focus Check Results

### 1. Host boundary regression — PASS

`tests/host/test_runtime_runner.py:351` `test_host_package_does_not_import_service_or_fund_layers` scans every `.py` file in `fund_agent/host/` and asserts no `fund_agent.services` or `fund_agent.fund` import. Independently confirmed by grep: Host source has zero such imports.

`tests/host/test_runtime_runner.py:370` `test_host_runner_source_has_no_fund_business_semantics` concatenates all Host source and asserts none of 18 forbidden business terms appear. Independently confirmed: only `fund_agent/host/README.md` mentions these terms in prose (declaring they are forbidden), never in implementation.

### 2. ExecutionContract / FundLLMExecutionRequest ownership — PASS

The Host source test forbids `FundLLMExecutionContract`, `FundLLMExecutionRequest`, `ExecutionContract` from appearing in `fund_agent/host/` implementation files. `fund_agent/host/README.md:5` explicitly states Host "不读取 `FundLLMExecutionContract` / `FundLLMExecutionRequest` 的业务字段". `fund_agent/README.md:34` explicitly states Service owns the ExecutionContract.

### 3. extra_payload not used for business parameters — PASS

`extra_payload` is in the Host source forbidden terms list (`tests/host/test_runtime_runner.py:402`) and CLI boundary forbidden terms list (`tests/ui/test_cli.py:2070`). `fund_agent/host/README.md:18` explicitly prohibits it. Neither Host nor the CLI bridge function accept or emit `extra_payload`.

### 4. Default deterministic analyze/checklist unchanged — PASS

No production code changed. Existing tests covering the deterministic path continue to pass (1255 total, all passing). `tests/README.md:56` confirms `test_fund_analysis_service_llm.py` covers "原 `analyze/checklist` 不调用 LLM".

### 5. --use-llm fail-closed semantics — PASS

`tests/ui/test_cli.py:2002` `test_analyze_cli_use_llm_host_terminal_failure_does_not_fake_success` asserts `exit_code == 1`, `stdout == ""`, no report markdown in output, and `status=failed` in stderr. Existing fail-closed tests (missing config, provider error, incomplete result) continue to pass.

### 6. Host terminal state / safe diagnostics — PASS

`tests/host/test_runtime_runner.py:413` `test_build_safe_diagnostics_rejects_forbidden_business_payload_keys` verifies that `system_prompt`, `chapter_draft`, `raw_provider_response`, `raw_audit_response`, `Authorization`, `api_key` are each rejected with `HostRuntimeError`. The Host implementation (`fund_agent/host/runtime.py:19-30`, `140-161`) uses broader substring matching against `_FORBIDDEN_DIAGNOSTIC_KEY_PARTS` covering 10 categories.

`tests/ui/test_cli.py:2034` asserts `status=succeeded` does NOT appear in failed terminal state output, proving exceptions are not swallowed.

### 7. Docs/control sync — PASS

All five docs correctly state current facts:

| Doc | Key facts stated |
|-----|-----------------|
| `docs/design.md` (v2.6) | Service owns `FundLLMExecutionContract`/`FundLLMExecutionRequest`; Host reads only `host_timeout_seconds`; async runner/durable session are future |
| `docs/implementation-control.md` | Slice 1-3 accepted, Slice 4 in implementation handoff; Host receives only generic operation/deadline/session; O1/O2 residuals recorded |
| `docs/current-startup-packet.md` | Current gate status updated; Host does not import Service/Fund |
| `fund_agent/README.md` | `CLI -> Service prepares request -> Host runner -> Service` path correctly described |
| `fund_agent/host/README.md` | Host API surface (`operation_name`, `operation`, `timeout_seconds`, optional `session_id`) and explicit forbidden items listed |

### 8. Future gates remain future — PASS

All five docs consistently state async Host runner, durable session/resume/memory/outbox, and Agent tool-loop are future gates. `fund_agent/host/README.md:21-28` has an explicit "当前非目标" section listing all deferred capabilities.

### 9. No scope creep — PASS

Only test files (2) and doc/markdown files (6) are modified. No production source code changed. No Agent engine, provider runtime, score, quality gate, golden, fixture, release-readiness, or PR state files touched.

### 10. Implementation evidence residual owners — PASS

`docs/implementation-control.md:228-229` Open Residuals table records:
- O1 async-in-sync CLI Host closure: deferred to future async CLI / Host async-runner design gate
- O2 fake-only Host boundary coverage: addressed in Slice 4

Evidence artifact Section "Residual Risks" (`docs/reviews/...slice4-implementation-evidence...md:73-78`) records all five residual categories with owners.

## Observations (Non-Blocking)

### O1: Source-scan tests are intentionally brittle

`test_host_package_does_not_import_service_or_fund_layers` (`tests/host/test_runtime_runner.py:351`), `test_host_runner_source_has_no_fund_business_semantics` (`tests/host/test_runtime_runner.py:370`), and `test_cli_use_llm_host_boundary_only_reads_runtime_timeout_scalar` (`tests/ui/test_cli.py:2039`) all use string matching on source files. Variable renames or code reorganization would break them. This is intentional for boundary regression — the tests are designed to catch boundary violations immediately. Not a defect.

### O2: CLI `_run_llm_analysis_in_host` closure captures full execution_request

`fund_agent/ui/cli.py:818-871` — the `operation` closure captures `execution_request` (a `FundLLMExecutionRequest`) and passes it through to `service.analyze_with_llm_execution()`. The test `test_cli_use_llm_host_boundary_only_reads_runtime_timeout_scalar` verifies the function body only *reads* `host_timeout_seconds` from it. The Host runner only receives the opaque `operation` callable plus `operation_name` and `timeout_seconds` — it never sees the typed request. Design is correct.

### O3: `test_build_safe_diagnostics_rejects_forbidden_business_payload_keys` uses different key names than the implementation's internal list

The test uses specific keys like `"system_prompt"`, `"raw_provider_response"` while the implementation uses broader substring matching (`"prompt"` matches `"system_prompt"`, `"provider_response"` matches `"raw_provider_response"`). Cross-checked: all six test keys are correctly matched by at least one forbidden part. The implementation's broader matching is a defense-in-depth benefit.

## Validation Confirmation

Controller-provided validation independently confirmed:
- `uv run pytest tests/host/test_runtime_runner.py tests/ui/test_cli.py -q`: 67 passed
- `uv run pytest tests/host/test_runtime_state.py tests/host/test_runtime_runner.py tests/services/test_execution_contract.py tests/services/test_fund_analysis_service_llm.py tests/ui/test_cli.py -q`: 110 passed
- `uv run ruff check .`: All checks passed
- `uv run pytest --cov=fund_agent --cov-report=term-missing --cov-fail-under=50 -q`: 1255 passed, coverage 91.90%

## Residual Risks

| Risk | Severity | Owner |
|------|----------|-------|
| O1 async-in-sync CLI Host closure | Low — sync is sufficient for current MVP | Future async CLI / Host async-runner design gate |
| Provider endpoint runtime reliability (`provider_runtime_timeout_small_prompt`) | Medium — blocks real provider completion | Future provider endpoint calibration / runtime diagnostic gate |
| Source-scan test brittleness | Low — intentional boundary regression design | Same test suite; refactors will update tests |
| Durable Host capabilities (async runner, session/resume/memory/outbox) | Low — not required for current MVP | Future Host gates |
| Agent engine/tool-loop migration | Low — not required for current MVP | Future Agent/tool-loop gate |

## Docs Closeout Note

`docs/implementation-control.md` and `docs/current-startup-packet.md` currently describe Slice 4 as "implementation handoff in progress." This is accurate for the review target. After controller acceptance, the controller will need a final closeout update (changing status to "accepted locally" and recording the accepted checkpoint commit). This is a controller-owned action, not a code defect.

## Verdict

**PASS — no blocking findings.** Three Host boundary regression tests and two CLI boundary regression tests correctly prove the boundary. Docs/control sync accurately states all current facts. No scope creep detected. Residual risks are identified and owned.
