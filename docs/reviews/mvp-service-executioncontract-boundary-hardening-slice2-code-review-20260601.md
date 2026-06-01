# MVP Service ExecutionContract Boundary Hardening Slice 2 Code Review

Gate: `MVP Service ExecutionContract boundary hardening gate`
Review target: Implementation Slice 2 - Service-owned Provider Preparation
Approved plan: `docs/reviews/mvp-service-executioncontract-boundary-hardening-plan-20260601.md`
Reviewer role: Gateflow-governed code review specialist, not controller
Review date: 2026-06-01

## Findings

No code findings.

Code review verdict: accepted with no blocking findings

## Scope Evidence

- Reviewed current branch `codex/local-reconciliation`.
- Reviewed current diff for the requested files only:
  - `fund_agent/services/fund_analysis_service.py`
  - `fund_agent/services/__init__.py`
  - `tests/services/test_fund_analysis_service_llm.py`
  - `tests/services/test_execution_contract.py`
- `git diff --name-only` shows only the four Slice 2 target files are modified. No CLI, Host, docs, score, golden, fixtures, dependency, release or PR-state files are touched by the reviewed diff.
- Existing unrelated untracked residual files were observed and not reviewed for this Slice 2 code verdict.

## Contract And Boundary Review

- `build_fund_llm_execution_request()` is Service-owned and lives in `fund_agent/services/fund_analysis_service.py`.
- The helper loads typed provider config through `load_llm_provider_config_from_env()`, builds clients through `build_chapter_llm_clients(config)`, normalizes `FundLLMAnalysisInput`, constructs `QualityPolicyDeclaration`, `ChapterOrchestrationPolicy`, `FinalAssemblyPolicy`, `ProviderRuntimeBudget`, `QualityFailClosedPolicy`, `SafeDiagnosticPolicy`, `FundLLMRuntimePlan`, `FundLLMExecutionContract` and returns `FundLLMExecutionRequest`.
- Provider construction did not move into Host or UI in this slice. Host files were not modified, and `fund_agent/host` does not import Service/Fund in the reviewed diff.
- `analyze_with_llm_execution()` only reconstructs the existing `FundAnalysisRequest` from the typed normalized input, unpacks `llm_clients`, `chapter_policy` and `assembly_policy`, passes through `host_context`, and delegates to `analyze_with_llm()`. It does not reload env or rebuild provider clients.
- Runtime-only fields remain outside `FundLLMExecutionContract`; `FundLLMExecutionRequest.runtime_plan` carries runtime policies and `FundLLMExecutionRequest.llm_clients` carries clients.
- No new `extra_payload`, free business dict, `Mapping[str, Any]`, `**kwargs`, dayu dependency or provider SDK dependency was introduced in the reviewed Slice 2 diff.

## Test Review

Slice 2 tests cover:

- Service helper construction with monkeypatched config/client builder and no live credentials.
- Missing provider config as `LLMProviderConfigError`.
- Provider construction error as `LLMProviderConstructionError`.
- Hardened typed execution path matching existing `analyze_with_llm()`.
- `QualityGateBlockedError` and `QualityGateNotRunBlockedError` propagation.
- Contract shape and public signature guard for open business bags.

Tests are appropriately local to Service boundaries. I did not find false-positive coupling severe enough to block this slice.

## Validation

Ran:

```bash
uv run pytest tests/services/test_execution_contract.py tests/services/test_fund_analysis_service_llm.py -q
```

Result:

```text
37 passed in 0.76s
```

Ran:

```bash
git diff --check -- fund_agent/services/fund_analysis_service.py fund_agent/services/__init__.py tests/services/test_fund_analysis_service_llm.py tests/services/test_execution_contract.py
```

Result: passed with no whitespace errors.
