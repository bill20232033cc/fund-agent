# MVP Service ExecutionContract boundary hardening Slice 1 implementation evidence

Date: 2026-06-01
Gate: `MVP Service ExecutionContract boundary hardening gate`
Slice: `Slice 1: Service ExecutionContract Types`
Approved plan: `docs/reviews/mvp-service-executioncontract-boundary-hardening-plan-20260601.md`
Baseline checkpoint: `dc5fe87 gateflow: accept plan for MVP Service ExecutionContract boundary hardening gate`
Status: implemented, reviewed, fixed, re-reviewed accepted

## Step Self-check

- Current gate / role: 当前处于 implementation slice accepted checkpoint 前；controller 只记录证据、裁决 finding、保护 scope 并创建本地 checkpoint。
- Source of truth: fixed accepted plan、Slice 1 implementation worker report、code review artifact、code re-review artifact。
- Scope boundary: 本 slice 只允许 `fund_agent/services/execution_contract.py`、`fund_agent/services/__init__.py`、`tests/services/test_execution_contract.py` 及本 slice evidence/review artifacts。
- Stop conditions: 无 unresolved blocking finding；不进入 Slice 2 前先创建 Slice 1 accepted checkpoint。
- Evidence and validation: targeted test 已复跑通过；code re-review verdict accepted with no blocking findings。
- Next action: stage only Slice 1 files/artifacts and commit accepted Slice 1 checkpoint; no push/PR/merge/mark ready.

## Changed Files

- `fund_agent/services/execution_contract.py`
- `fund_agent/services/__init__.py`
- `tests/services/test_execution_contract.py`
- `docs/reviews/mvp-service-executioncontract-boundary-hardening-slice1-code-review-20260601.md`
- `docs/reviews/mvp-service-executioncontract-boundary-hardening-slice1-code-rereview-20260601.md`
- `docs/reviews/mvp-service-executioncontract-boundary-hardening-slice1-implementation-evidence-20260601.md`

## Implemented Plan Items

- Added frozen/slotted Service-owned contract/runtime request types:
  - `FundLLMAnalysisInput`
  - `QualityPolicyDeclaration`
  - `ProviderRuntimeBudget`
  - `QualityFailClosedPolicy`
  - `SafeDiagnosticPolicy`
  - `FundLLMRuntimePlan`
  - `FundLLMExecutionContract`
  - `FundLLMExecutionRequest`
- Kept `FundLLMExecutionContract` limited to business facts and declarations:
  - fund code
  - report year
  - report mode
  - explicit LLM opt-in mode
  - normalized analysis input
  - quality policy declaration
- Kept runtime-only objects out of `FundLLMExecutionContract`:
  - chapter orchestration policy
  - final assembly policy
  - provider runtime budget
  - safe diagnostic policy
  - LLM clients
  - Host context/run/session/deadline lifecycle fields
- Added `normalize_fund_llm_analysis_input()` for explicit business input normalization from `FundAnalysisRequest`.
- Added `derive_host_timeout_seconds()` using the accepted formula:
  - `max(1, (writer_timeout + auditor_timeout + repair_timeout) * timeout_max_attempts * chapter_count)`
- Exported the new Service contract symbols from `fund_agent.services`.
- Added `tests/services/test_execution_contract.py` covering identity, fixed enum values, fail-closed policy, runtime budget validation, runtime chapter bounds, Host timeout derivation, contract field shape, and open business bag prohibitions.

## Validation

Targeted validation:

```text
uv run pytest tests/services/test_execution_contract.py -q
```

Result:

```text
23 passed
```

Controller also reran the command after the fix pass:

```text
23 passed in 0.67s
```

## Code Review Loop

- Code review artifact: `docs/reviews/mvp-service-executioncontract-boundary-hardening-slice1-code-review-20260601.md`
  - Verdict: not accepted due to 1 blocking finding.
- Accepted finding:
  - `001-未修复-[中]-开放参数袋负向测试在 future annotations 下失效`
- Fix summary:
  - Strengthened the test-side open business bag guard to detect string annotations produced by `from __future__ import annotations`, including `dict[str, Any]`, `Mapping[str, Any]`, and `typing.Mapping[str, Any]`.
  - Added focused regression coverage proving the old guard would miss string annotations.
- Re-review artifact: `docs/reviews/mvp-service-executioncontract-boundary-hardening-slice1-code-rereview-20260601.md`
  - Verdict: accepted with no blocking findings.

## Docs Decision

No README or truth-source docs update was required for Slice 1 alone because the slice adds internal Service contract types and tests without changing CLI, Host behavior, user-visible commands, or current route facts. The accepted plan still requires a design/control sync exit decision before accepted implementation of the full gate if later slices change code facts.

## Residual Risk Classification

- Service/CLI/Host integration is not implemented in Slice 1.
  - Classification: covered by later approved slices.
  - Owner/destination: Slice 2 and Slice 3 in the accepted plan.
- Developer docs and design/control sync are not updated in Slice 1.
  - Classification: covered by later approved slice / implementation-exit decision.
  - Owner/destination: Slice 4 and controller accepted implementation judgment.
- Historical untracked residual artifacts remain untouched.
  - Classification: out of scope for this gate.

## Completion Status

Slice 1 is complete and ready for accepted local checkpoint. No blocking open questions remain for this slice.
