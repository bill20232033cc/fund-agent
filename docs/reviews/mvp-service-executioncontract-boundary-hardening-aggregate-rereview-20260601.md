# Aggregate Re-review: MVP Service ExecutionContract Boundary Hardening — Accepted Findings Fix

## Scope Reviewed

- **Source artifact**: `docs/reviews/mvp-service-executioncontract-boundary-hardening-aggregate-deepreview-20260601.md`
- **Fix evidence**: `docs/reviews/mvp-service-executioncontract-boundary-hardening-aggregate-fix-evidence-20260601.md`
- **Reviewed findings**: Finding 1 (QualityFailClosedPolicy not consumed) and Finding 2 (QualityGatePolicy duplicate Literal) only
- **Reviewed diff**:
  - `fund_agent/services/fund_analysis_service.py`
  - `fund_agent/services/__init__.py`
  - `tests/services/test_execution_contract.py`
  - `tests/services/test_fund_analysis_service_llm.py`
- **Excluded**: full gate re-review, other findings, residual risks not part of the accepted fix

## Verdict

**PASS / no blocking findings.** Both accepted findings are correctly fixed. No boundary regression, no fail-closed weakening, no scope drift. Tests pass (43 passed in 0.72s).

---

## Finding 1: QualityFailClosedPolicy Runtime Consumption

### Fix Summary

`analyze_with_llm_execution()` now validates `execution_request.runtime_plan.quality_fail_closed_policy` via `_validate_llm_execution_fail_closed_policy()` (`fund_analysis_service.py:705-707`) before any extraction or LLM orchestration.

### Validation Logic (`fund_analysis_service.py:1016-1047`)

Five fields are checked with strict identity comparison:

| Field | Validation | Expected |
|---|---|---|
| `fail_on_quality_gate_block` | `is not True` | `True` |
| `fail_on_quality_gate_not_run` | `is not True` | `True` |
| `fail_on_partial_orchestration` | `is not True` | `True` |
| `fail_on_incomplete_final_assembly` | `is not True` | `True` |
| `deterministic_fallback_allowed` | `is not False` | `False` |

Any weakening raises `ValueError("LLM execution fail-closed policy 不允许放松字段：...")`. Using `is not True` / `is not False` (identity) correctly rejects any non-conforming value including `False`, `0`, `None`, `""` for the four required-True fields, and any truthy value for `deterministic_fallback_allowed`.

### Evidence Inspected

- **Placement**: validation is at line 705-707, before line 708 `analyze_with_llm()` call — confirms execution stops before extraction/LLM orchestration on policy violation
- **No bypass**: `analyze_with_llm()` (line 602) does NOT call this validation — it's a lower-level API receiving individual parameters, not a runtime plan. Validation is correctly placed only at the typed execution entry point `analyze_with_llm_execution`
- **Deterministic isolation**: `analyze()` (line 515) and `checklist()` (line 569) do NOT call `_validate_llm_execution_fail_closed_policy` — correct, as they don't accept a runtime plan
- **Hardcoded fail-closed remains**: `analyze_with_llm()` still hardcodes fail-closed via `_run_analysis_core` (throws for block/not-run), `orchestrate_chapters` (blocked on missing auditor), `assemble_final_chapters` (incomplete on missing chapters). The new validation is an additional defense layer at the typed boundary, not a replacement
- **Test coverage** (`test_fund_analysis_service_llm.py:349-385`): parametrized 5-way test covers all policy fields. Each case:
  1. Constructs weakened policy via `_unchecked_quality_fail_closed_policy` (bypasses `__post_init__` to simulate an attacker constructing a weak policy)
  2. Calls `analyze_with_llm_execution()`
  3. Asserts `ValueError` with field name in message
  4. Asserts extractor, writer, auditor were never called — confirms fail-before-execution

### Confirmed

- `analyze_with_llm_execution` 实际消费并 enforce QualityFailClosedPolicy
- 任何弱化 fail-closed 的 policy 在运行前 fail closed（extractor/writer/auditor 均未调用）
- 默认 deterministic `analyze`/`checklist` 未受影响（不调用验证函数）
- `--use-llm` fail-closed 语义保持，无 fallback 伪造 success

---

## Finding 2: QualityGatePolicy Single Source Type

### Fix Summary

`QualityGatePolicy` is now defined only in `execution_contract.py:31`. `fund_analysis_service.py` imports it (line 78) instead of redeclaring. `__init__.py` re-exports from `execution_contract` (line 42).

### Evidence Inspected

- **`execution_contract.py:31`**: `QualityGatePolicy = Literal["off", "warn", "block"]` — unchanged, remains single source
- **`fund_analysis_service.py:78`**: `QualityGatePolicy` imported via existing `from fund_agent.services.execution_contract import (...)` block — no separate Literal assignment
- **`fund_analysis_service.py:88`**: old `QualityGatePolicy = Literal[...]` line removed; `ValuationState`, `MoneyHorizon` remain as local aliases (correct — they are Service-local domain types not shared with execution contract)
- **`__init__.py:42`**: re-exports `QualityGatePolicy` from `execution_contract`, removed from `fund_analysis_service` re-exports (line 84 area)
- **No cycle**: `execution_contract.py` imports from `fund_analysis_service` only under `TYPE_CHECKING` (lines 17-25); `fund_analysis_service.py` imports from `execution_contract` at runtime (lines 71-82). This is a one-way runtime dependency (fund_analysis_service → execution_contract) with TYPE_CHECKING reverse bridge. Adding `QualityGatePolicy` to the existing runtime import does not introduce a new cycle — it uses the already-established import path.
- **Test coverage** (`test_execution_contract.py:412-436`):
  1. Identity check: `fund_analysis_service_module.QualityGatePolicy is execution_contract_module.QualityGatePolicy`
  2. AST check: no module-level `QualityGatePolicy` assignment in `fund_analysis_service.py`
  3. AST check: `QualityGatePolicy` is imported from `fund_agent.services.execution_contract`

### Confirmed

- `QualityGatePolicy` 只保留 `execution_contract.py` 作为 Service contract 单一类型来源
- `fund_analysis_service.py` 不再复制 Literal
- 测试通过 AST + identity 双重验证

---

## Forbidden Scope Check

| Check | Result |
|---|---|
| Service/Host/Agent 边界倒退 | **PASS** — Host still has zero Service/Fund imports (grep confirmed) |
| 基金业务进入 Host | **PASS** — no business fields in Host source |
| 显式参数进入 extra_payload | **PASS** — diff contains zero new extra_payload references; only pre-existing docstring declarations |
| dayu-agent/dayu.host/dayu.engine 生产依赖 | **PASS** — zero dayu references in diff |

---

## Test Execution

```
tests/services/test_execution_contract.py + tests/services/test_fund_analysis_service_llm.py
43 passed in 0.72s
```

Full suite (116 tests) confirmed passing per fix evidence.

---

## Residual Risks

1. **`_unchecked_quality_fail_closed_policy` test helper uses `object.__new__` bypass**: the helper correctly serves its narrow purpose (testing runtime defense against bypassed `__post_init__`), but this pattern confirms the defense-in-depth approach is needed — `__post_init__` alone is insufficient as a guard. The runtime validation layer now provides that defense. No production code uses `object.__new__` for dataclass construction.

2. **`analyze_with_llm` (non-execution path) not covered by policy validation**: `analyze_with_llm` (line 602) accepts individual `chapter_policy`/`assembly_policy` parameters, not a `FundLLMRuntimePlan`. It does not call `_validate_llm_execution_fail_closed_policy`. This is by design — it's an internal Service method called by the execution entry point after validation. Direct callers of `analyze_with_llm` (e.g., test helpers) bypass the validation, but this is test-only and intentional.

3. **Pre-existing residual risks unchanged**: the 3 residual risks in the aggregate deepreview (no real-provider e2e tests, CLI asyncio.run() bridge, per-chapter fail-closed granularity) remain with their existing owners and are not within scope of this fix re-review.
