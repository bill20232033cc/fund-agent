# LLM Execution Request Validation Ordering Plan

## Scope

- Gate: `LLM execution request validation ordering gate`
- Classification: `standard`
- Mode: planning only
- Current accepted input: EID source provenance truth alignment checkpoint `2cee618`; control sync checkpoint `b934781`
- Objective: ensure Service-owned `FundLLMExecutionRequest` validation rejects invalid business request / contract inputs before provider client construction and before any Host/Agent/provider execution.

This plan does not authorize implementation until it passes independent review and controller judgment.

## Truth Inputs

- `AGENTS.md`: Service owns business use-case orchestration, prompt/ExecutionContract assembly, provider construction/runtime ceilings and final fail-closed mapping; Host remains lifecycle-only and business-opaque; explicit business parameters must not be passed through `extra_payload`.
- `docs/design.md`: current `--use-llm` path is explicit opt-in and provider-backed; Service constructs `FundLLMExecutionRequest` / `ExecutionContract`, Host only governs lifecycle/deadline/cancel/events, Agent owns no-live body-chapter mechanics.
- `docs/implementation-control.md`: current active gate is `LLM execution request validation ordering gate`; provider default/runtime changes, live provider/EID/PDF/FDR/network commands and implementation before reviewed plan acceptance are not authorized.
- `docs/current-startup-packet.md`: current entry is planning; no implementation write set is accepted yet.
- Code facts:
  - `fund_agent/services/fund_analysis_service.py:919-993` currently calls `load_llm_provider_config_from_env()` and `build_chapter_llm_clients(config)` before `_resolve_analyze_contract(request)`, `normalize_fund_llm_analysis_input(request)`, `QualityPolicyDeclaration(...)` and `FundLLMExecutionContract(...)`.
  - `tests/services/test_fund_analysis_service_llm.py` already verifies config errors and provider construction errors happen before Host run, but does not prove invalid business/contract inputs avoid provider construction.
  - `tests/services/test_execution_contract.py` already verifies dataclass boundary invariants, explicit typed path fields and no `extra_payload`/open payload bag.

## Non-Goals

- No live provider, endpoint, DNS, socket, curl, network, EID, PDF, FDR, extractor, analyze/checklist, golden/readiness, score-loop or release command.
- No provider default, model, base URL, timeout, retry, backoff, max-output, runtime budget, prompt payload mode or fail-closed semantic change.
- No Host lifecycle behavior change.
- No Agent runner/tool-loop behavior change.
- No source fallback/acquisition change.
- No `docs/design.md`, `.gitignore`, root `README.md`, control-doc or release-state edit during implementation.
- No `extra_payload`, `payload`, `metadata`, `context`, `**kwargs` or open business parameter bag.

## Proposed Implementation Write Set

Allowed implementation files:

- `fund_agent/services/fund_analysis_service.py`
- `tests/services/test_fund_analysis_service_llm.py`

Optional only if reviewer finds a direct gap in existing boundary tests:

- `tests/services/test_execution_contract.py`

No other source, test, docs, runtime artifact or config file is authorized by this plan.

## Implementation Slices

### Slice 1 - Add failing no-live ordering tests

Add focused tests in `tests/services/test_fund_analysis_service_llm.py` proving invalid Service-owned request/contract inputs fail before provider config/client construction:

1. `product` mode with `developer_overrides` raises `ValueError` before `load_llm_provider_config_from_env()` and `build_chapter_llm_clients()` are called.
2. Invalid `opt_in_mode` raises `ValueError` before provider client construction by constructing `FundLLMExecutionContract(..., llm_opt_in_mode=opt_in_mode)` before loading provider config or building LLM clients; the runtime check already lives in `FundLLMExecutionContract.__post_init__`.
3. Invalid fund identity, for example blank or non-6-digit fund code after normalization, raises `ValueError` before provider client construction.

Test technique:

- monkeypatch `fund_analysis_service_module.load_llm_provider_config_from_env` and `fund_analysis_service_module.build_chapter_llm_clients` with spy functions that append to a local `calls` list and raise `AssertionError` if reached.
- assert the expected `ValueError` message and assert `calls == []`.
- use existing fake request helpers where possible; do not introduce live config or real provider clients.

### Slice 2 - Reorder `build_fund_llm_execution_request`

Change only `build_fund_llm_execution_request()` ordering:

1. Resolve and validate business request first:
   - `_resolve_analyze_contract(request)`
   - `normalize_fund_llm_analysis_input(request)`
   - `QualityPolicyDeclaration(...)`
   - `FundLLMExecutionContract(..., llm_opt_in_mode=opt_in_mode)`
2. Load provider config only after the stable business contract is valid.
3. Build `ChapterOrchestrationPolicy`, `ProviderRuntimeBudget`, `QualityFailClosedPolicy`, `SafeDiagnosticPolicy` and then `FundLLMRuntimePlan`; `QualityFailClosedPolicy` must be constructed before `FundLLMRuntimePlan` because it depends on `resolved_contract.quality_gate_policy`.
4. Construct provider LLM clients only after the runtime plan has been successfully constructed.
5. Return `FundLLMExecutionRequest(...)` with unchanged field values for the valid path.

Expected code shape:

```python
resolved_contract = _resolve_analyze_contract(request)
analysis_input = normalize_fund_llm_analysis_input(request)
quality_policy = QualityPolicyDeclaration(...)
contract = FundLLMExecutionContract(..., llm_opt_in_mode=opt_in_mode)

config = load_llm_provider_config_from_env()
chapter_policy = ChapterOrchestrationPolicy(...)
provider_runtime_budget = ProviderRuntimeBudget(...)
quality_fail_closed_policy = QualityFailClosedPolicy(...)
safe_diagnostic_policy = SafeDiagnosticPolicy()
runtime_plan = FundLLMRuntimePlan(...)
llm_clients = build_chapter_llm_clients(config)
return FundLLMExecutionRequest(...)
```

This is an ordering hardening only. It must not change provider configuration parsing, default values, runtime budget formula, Host timeout derivation, typed template path, fail-closed flags, chapter ids or prompt payload mode.

Keep duplicate `product` mode + `developer_overrides` validation in `_resolve_analyze_contract()` and `normalize_fund_llm_analysis_input()` as defense-in-depth. This gate does not authorize cleanup or semantic deduplication of those checks.

### Slice 3 - Preserve existing behavior and boundary guards

Keep existing valid-path and failure-path tests passing:

- Existing config error still propagates before Host run.
- Existing provider construction error still propagates before Host run.
- Existing valid request still returns the same contract/runtime plan/client fields.
- Existing `test_no_extra_payload_or_free_business_payload_bag` and related boundary tests still pass.

## Acceptance Criteria

| ID | Criterion | Direct evidence |
|---|---|---|
| A1 | Invalid business request fails before provider config/client construction | New focused tests with provider spies and `calls == []` |
| A2 | Invalid `opt_in_mode` fails before provider client construction | New focused test |
| A3 | Valid execution request fields remain unchanged | Existing `test_build_fund_llm_execution_request_prepares_contract_and_runtime_plan` |
| A4 | Config/provider construction errors still fail before Host run | Existing config/construction error tests |
| A5 | No Host/Agent/provider live execution or network access | Command list and no-live test scope |
| A6 | No provider default/runtime/budget/typed path semantic change | Diff review and existing assertions |
| A7 | No `extra_payload` or open business bag introduced | Existing execution contract tests |

## Validation Matrix

Required after implementation:

```bash
uv run pytest tests/services/test_fund_analysis_service_llm.py tests/services/test_execution_contract.py -q
uv run ruff check fund_agent/services/fund_analysis_service.py tests/services/test_fund_analysis_service_llm.py tests/services/test_execution_contract.py
git diff --check
git diff --name-only
```

Optional only if implementation touches unexpected Host/Agent boundary behavior:

```bash
uv run pytest tests/host/test_runtime_runner.py tests/services/test_chapter_orchestrator.py -q
```

## Review Checklist

Reviewers must verify:

- The implementation is limited to the accepted write set.
- Invalid request/contract branches do not call provider config/client construction.
- Valid provider-backed path remains provider-backed and explicit opt-in.
- No live provider/EID/PDF/FDR/network command was run.
- Host remains lifecycle-only and receives only the existing `host_timeout_seconds` runtime scalar.
- Service remains the owner of request/contract/runtime plan/provider construction ordering.
- No `extra_payload` or free-form business payload bag appears.

## Residuals / Deferred Entries

- Provider runtime residuals and live acceptance remain deferred to separate controlled live provider gates.
- Runtime budget/default changes remain deferred.
- Host/Agent full tool-loop/runtime expansion remains deferred.
- Release-readiness cleanliness remains deferred.
- LLM path parity with deterministic `_validate_request()` checks such as `quality_gate_run_id` and `quality_gate_output_dir` is deferred to a separate consistency gate; this plan only hardens provider-construction ordering for existing request/contract validation.
