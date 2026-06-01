# MVP Service ExecutionContract boundary hardening — Slice 3 code review

Date: 2026-06-01
Gate: `MVP Service ExecutionContract boundary hardening gate`
Slice: `Slice 3: CLI -> Host Uses Typed Execution Request`
Review target: implementation diff `HEAD` (branch `codex/local-reconciliation`)
Evidence artifact: `docs/reviews/mvp-service-executioncontract-boundary-hardening-slice3-implementation-evidence-20260601.md`
Reviewer: Claude Code (deepreview)
Status: **PASS — no blocking findings**

## Verdict

Slice 3 implementation correctly hardens the Service → Host boundary by replacing CLI-owned provider preparation with Service-owned `build_fund_llm_execution_request()`. All six focus checks pass. No blocking findings. Three residual risks noted below are outside Slice 3 scope.

## Focus check results

### 1. ExecutionContract keeps Service → Host boundary clear — PASS

- CLI calls `build_fund_llm_execution_request(request, opt_in_mode="explicit_cli_flag")` (cli.py:808), delegating all provider config, client construction, and policy assembly to Service.
- `_run_llm_analysis_in_host` now accepts only `FundLLMExecutionRequest` (cli.py:818–819), removing the prior `llm_clients`, `chapter_policy`, `timeout_seconds` separate params.
- Host is invoked with only generic params: `operation_name`, `operation`, `timeout_seconds` (cli.py:862–866). No business fields flow to `HostRuntimeRunner.run_sync()`.
- `_FakeHostRuntimeRunner.run_sync` (test_cli.py:1184–1233) asserts `kwargs == {}` and records `forbidden_business_args` when non-empty — test at line 1727 confirms `forbidden_business_args == {}`.

### 2. Host does not understand fund business semantics — PASS

- `HostRuntimeRunner.run_sync` signature (`host/runtime.py:409–416`) accepts `operation_name: str`, `operation: Callable`, `timeout_seconds: int | None`, `session_id: str | None`. No fund-specific parameters.
- `operation_name` docstring states "仅用于安全诊断，不承载业务语义" (runtime.py:420).
- Grep of `fund_agent/host/` for `fund_code`, `report_year`, `fund_analysis`, `extra_payload`, `extra_params` returns zero matches.
- `HostRunContext` (runtime.py:215) contains only run lifecycle fields (`run_id`, `started_at`, `deadline_at`, `cancellation_token`).

### 3. Default deterministic analyze/checklist behavior is unaffected — PASS

- `test_analyze_cli_default_product_request` (test_cli.py:2110) monkeypatches `build_fund_llm_execution_request` with `_forbid_llm_execution_request_builder` and `HostRuntimeRunner` with `_RaisingHostRuntimeRunner` — both raise `AssertionError` if called. Test passes, proving default `analyze` (no `--use-llm`) does NOT invoke LLM path.
- `test_checklist_cli_calls_service_and_prints_summary` (test_cli.py:2445) sets the same raising fakes. Test passes, proving checklist path is isolated from LLM path.
- `test_analyze_cli_calls_service_and_prints_report` (test_cli.py:1530) — the original deterministic test — continues to pass with `analyze_with_llm_execution_called is False` assertion (line 1600).

### 4. `--use-llm` fail-closed semantics remain intact — PASS

- Incomplete result exits 1 with no deterministic fallback (test_cli.py:1771–1808). Stderr contains safe diagnostics only.
- Timeout exits 1 with no deterministic fallback (test_cli.py:1908–1975). Safe diagnostics exclude credentials and raw responses.
- Host operation failure exits 1 with `error_type=RuntimeError` in stderr, NOT double-wrapped by generic "分析失败" handler (test_cli.py:1978–1999, verified at line 1998).
- Quality gate block and not-run-block are re-raised from the Host closure (cli.py:857–860, 867–868) via `raise quality_gate_exception` (cli.py:867–868), preserving exit code 2.
- `quality_fail_closed_policy.deterministic_fallback_allowed=False` is enforced in contract validation (execution_contract.py:354–355).

### 5. No explicit parameters flow back into extra_payload — PASS

- `build_fund_llm_execution_request` (fund_analysis_service.py:909–980) normalizes `FundAnalysisRequest` into typed `FundLLMExecutionContract` with explicit fields (`fund_code`, `report_year`, `analysis_input`, `quality_policy`, `llm_opt_in_mode`).
- All LLM execution parameters flow through the typed `FundLLMExecutionRequest.runtime_plan` and `.contract`, not through unstructured dicts.
- Grep of entire codebase shows `extra_payload` only appears in docstring comments explicitly saying "不使用 `extra_payload`" — no actual usage.
- CLI source boundary test (test_cli.py:2024–2051) asserts `extra_payload` is absent from cli.py source.

### 6. Tests cover negative boundary cases — PASS

| Test | Lines | What it proves |
|------|-------|---------------|
| `test_analyze_cli_use_llm_missing_config_fails_before_service` | 1625–1667 | Missing env config fails before Service or Host is called |
| `test_analyze_cli_use_llm_construction_error_fails_before_service` | 1730–1768 | Provider construction failure fails before Service |
| `test_analyze_cli_default_product_request` | 2110–2145 | Default path invokes neither LLM builder nor Host |
| `test_checklist_cli_calls_service_and_prints_summary` | 2445–2493 | Checklist path invokes neither LLM builder nor Host |
| `test_checklist_cli_rejects_use_llm_option` | 2496–2534 | `--use-llm` not accepted by checklist; Typer-level rejection |
| `test_cli_module_llm_boundary_has_no_forbidden_runtime_imports` | 2024–2051 | No provider SDK, dayu, httpx, or `extra_payload` in CLI source |
| `test_cli_module_imports_service_but_not_agent_internals` | 2002–2021 | CLI imports services but not `fund_agent.fund.*` or `fund_agent.application` |
| `test_analyze_cli_use_llm_incomplete_result_exits_without_fallback` | 1771–1808 | Incomplete = exit 1, no deterministic fallback |
| `test_analyze_cli_use_llm_timeout_fail_closed_without_fallback` | 1908–1975 | Timeout = exit 1, no fallback |
| `test_analyze_cli_use_llm_host_failure_is_not_double_wrapped` | 1978–1999 | Host failure not re-wrapped by generic handler |
| `test_analyze_cli_use_llm_structured_quality_gate_block` | 2224–2255 | LLM quality gate block = exit 2, preserves structured output |
| `test_analyze_cli_use_llm_structured_quality_gate_not_run_block` | 2285–2316 | LLM not-run block = exit 2 |
| `test_analyze_cli_use_llm_l1_subcategory_matches_service_summary` | 1864–1905 | L1 programmatic audit subcategory preserved through to stderr |

## Non-blocking observations

### O1: `asyncio.run()` inside sync Host closure (cli.py:843)

The `operation` closure calls `asyncio.run(service.analyze_with_llm_execution(...))`. This creates a fresh event loop each invocation. If `HostRuntimeRunner.run_sync` were ever called from within an existing event loop (e.g., async Typer or future async CLI), `asyncio.run()` would raise `RuntimeError`. Not a concern for current synchronous CLI, but worth noting if CLI becomes async later.

### O2: Tests use fakes exclusively for Host

All Slice 3 tests mock `HostRuntimeRunner` with `_FakeHostRuntimeRunner` or `_RaisingHostRuntimeRunner`. The real `HostRuntimeRunner.run_sync()` is not exercised in these tests. The fake correctly mirrors the production calling convention (`operation_name`, `operation`, `timeout_seconds`, `session_id`), so parity is maintained by contract. Integration testing of Host timeout/cancellation behavior is deferred to Slice 4.

### O3: `FundLLMExecutionRequest` type import in CLI

CLI imports `FundLLMExecutionRequest` from `fund_agent.services` (cli.py:55). This is used only as a type annotation for `_build_llm_execution_request_or_fail`'s return type and `_run_llm_analysis_in_host`'s parameter type. The actual construction is fully delegated to `build_fund_llm_execution_request()`. This is acceptable — the type is part of Service's public API. No Service internals leak through this import.

## Test execution confirmation

69 tests pass (`tests/ui/test_cli.py` + `tests/services/test_fund_analysis_service_llm.py`):
```
69 passed in 0.84s
```

## Review conclusion

Slice 3 correctly shifts provider preparation and policy assembly from CLI into Service-owned `build_fund_llm_execution_request()`. The typed `FundLLMExecutionRequest` now flows through CLI as an opaque value, with Host receiving only generic governance parameters. All negative boundary cases are covered. No blocking findings.

Residual risks (O1–O3) are non-blocking and appropriately deferred to later slices or out of gate scope.
