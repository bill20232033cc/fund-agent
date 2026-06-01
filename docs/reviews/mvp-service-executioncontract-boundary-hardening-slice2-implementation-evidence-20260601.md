# MVP Service ExecutionContract boundary hardening Slice 2 implementation evidence

Date: 2026-06-01
Gate: `MVP Service ExecutionContract boundary hardening gate`
Slice: `Slice 2: Service-owned Provider Preparation`
Approved plan: `docs/reviews/mvp-service-executioncontract-boundary-hardening-plan-20260601.md`
Prior slice checkpoint: `4691da5 gateflow: accept MVP Service ExecutionContract boundary hardening slice 1`
Status: implemented and code-reviewed accepted

## Step Self-check

- Current gate / role: 当前处于 Slice 2 accepted checkpoint 前；controller 记录证据、确认 review 通过并保护 stage/commit 范围。
- Source of truth: accepted plan Slice 2、worker completion report、Slice 2 code review artifact。
- Scope boundary: 本 slice 只触碰 Service-owned provider preparation、Service LLM tests、Service exports 和本 slice review/evidence artifacts；未触碰 CLI、Host、docs、score、golden、fixtures、release/PR 状态或历史 residual。
- Stop conditions: 无 blocking code findings；Slice 3 CLI/Host integration 尚未开始。
- Evidence and validation: targeted Service tests 通过；review verdict accepted with no blocking findings。
- Next action: stage only Slice 2 files/artifacts and commit accepted Slice 2 checkpoint; no push/PR/merge/mark ready.

## Changed Files

- `fund_agent/services/fund_analysis_service.py`
- `fund_agent/services/__init__.py`
- `tests/services/test_fund_analysis_service_llm.py`
- `tests/services/test_execution_contract.py`
- `docs/reviews/mvp-service-executioncontract-boundary-hardening-slice2-code-review-20260601.md`
- `docs/reviews/mvp-service-executioncontract-boundary-hardening-slice2-implementation-evidence-20260601.md`

## Implemented Plan Items

- Added Service-owned `build_fund_llm_execution_request(...)`.
- The helper loads provider config through `load_llm_provider_config_from_env()` and builds clients through `build_chapter_llm_clients(config)`.
- The helper constructs:
  - normalized `FundLLMAnalysisInput`
  - `QualityPolicyDeclaration`
  - compact `ChapterOrchestrationPolicy`
  - `FinalAssemblyPolicy`
  - `ProviderRuntimeBudget`
  - `QualityFailClosedPolicy`
  - `SafeDiagnosticPolicy`
  - `FundLLMRuntimePlan` with scalar `host_timeout_seconds`
  - `FundLLMExecutionContract`
  - `FundLLMExecutionRequest`
- Added `FundAnalysisService.analyze_with_llm_execution(...)`.
- `analyze_with_llm_execution(...)` delegates to existing `analyze_with_llm(...)` using only `execution_request.runtime_plan` and `execution_request.llm_clients`; it does not reload env or reconstruct provider clients.
- Exported the Service helper from `fund_agent.services`.

## Boundary Assertions

- Provider construction remains in Service, not Host or UI.
- Host files were not modified in this slice.
- CLI files were not modified in this slice.
- Runtime-only fields remain outside `FundLLMExecutionContract` and inside `FundLLMExecutionRequest.runtime_plan` / `llm_clients`.
- No `extra_payload`, free business dict, `Mapping[str, Any]`, `**kwargs`, `dayu-agent`, `dayu.host` or `dayu.engine` dependency was introduced.
- Existing fail-closed semantics are preserved by delegating to the current `analyze_with_llm(...)` path.

## Validation

Targeted validation:

```text
uv run pytest tests/services/test_execution_contract.py tests/services/test_fund_analysis_service_llm.py -q
```

Results:

```text
37 passed in 0.84s
37 passed in 0.75s
```

Code review validation also ran:

```text
git diff --check -- fund_agent/services/fund_analysis_service.py fund_agent/services/__init__.py tests/services/test_fund_analysis_service_llm.py tests/services/test_execution_contract.py
```

Result: passed with no whitespace errors.

## Code Review Loop

- Code review artifact: `docs/reviews/mvp-service-executioncontract-boundary-hardening-slice2-code-review-20260601.md`
- Verdict: accepted with no blocking findings.
- Accepted findings: none.
- Re-review: not required.

## Docs Decision

No README or design/control update was required for Slice 2 alone because CLI/Host/user-visible route behavior has not changed. The accepted plan still requires a design/control sync exit decision before accepting the full implementation if later slices change code facts.

## Residual Risk Classification

- CLI `--use-llm` still calls the old ad hoc LLM client/policy preparation path.
  - Classification: covered by later approved slice.
  - Owner/destination: Slice 3.
- Host boundary regression and docs sync are not done in Slice 2.
  - Classification: covered by later approved slice / implementation-exit decision.
  - Owner/destination: Slice 4 and controller final implementation judgment.
- Historical untracked residual artifacts remain untouched.
  - Classification: out of scope for this gate.

## Completion Status

Slice 2 is complete and ready for accepted local checkpoint. No blocking open questions remain for this slice.
