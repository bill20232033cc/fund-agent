# LLM Execution Request Validation Ordering Implementation Evidence

## Scope

- Gate: `LLM execution request validation ordering gate`
- Plan: `docs/reviews/mvp-llm-execution-request-validation-ordering-plan-20260611-133114.md`
- Plan controller judgment: `docs/reviews/mvp-llm-execution-request-validation-ordering-plan-controller-judgment-20260611-133729.md`
- Mode: no-live implementation evidence

## Changed Files

- `fund_agent/services/fund_analysis_service.py`
- `tests/services/test_fund_analysis_service_llm.py`

No other implementation file was modified.

## Implementation Summary

- `build_fund_llm_execution_request()` now validates Service-owned business request / contract fields before provider config loading or provider client construction:
  - `_resolve_analyze_contract(request)`
  - `normalize_fund_llm_analysis_input(request)`
  - `QualityPolicyDeclaration(...)`
  - `FundLLMExecutionContract(..., llm_opt_in_mode=opt_in_mode)`
- Provider config loading now happens after the stable business contract is valid.
- Provider clients are now constructed after `FundLLMRuntimePlan` is successfully constructed.
- Valid-path runtime plan fields, provider runtime budget values, typed template path and fail-closed policy semantics remain unchanged.

## Test Coverage Added

`tests/services/test_fund_analysis_service_llm.py` adds three no-live ordering regression tests:

- invalid `product` mode plus `developer_overrides` fails before provider config/client construction;
- invalid `opt_in_mode` fails through `FundLLMExecutionContract.__post_init__` before provider config/client construction;
- invalid fund identity fails before provider config/client construction.

The tests use `_ProviderConstructionSpy`, a module-level test spy class, to prove provider config/client construction was not reached.

## Validation

```text
uv run pytest tests/services/test_fund_analysis_service_llm.py tests/services/test_execution_contract.py -q
-> 50 passed in 0.48s

uv run ruff check fund_agent/services/fund_analysis_service.py tests/services/test_fund_analysis_service_llm.py tests/services/test_execution_contract.py
-> All checks passed!

git diff --check
-> no output

git diff --name-only
-> fund_agent/services/fund_analysis_service.py
-> tests/services/test_fund_analysis_service_llm.py
```

## Boundary Confirmation

- No live provider/EID/PDF/FDR/network command was run.
- No provider default, runtime budget, retry/backoff, model, base URL, timeout, max-output, typed path, Host timeout formula or fail-closed semantic change was made.
- No Host lifecycle, Agent runner/tool-loop, fallback/source acquisition, design doc, control doc, config or release-state file was changed.
- No `extra_payload`, `payload`, `metadata`, `context`, `**kwargs` or open business parameter bag was added.

## Residuals

- Duplicate `product` mode plus `developer_overrides` validation remains as defense-in-depth.
- LLM path parity with deterministic `_validate_request()` checks such as `quality_gate_run_id` and `quality_gate_output_dir` remains deferred to a separate consistency gate.
