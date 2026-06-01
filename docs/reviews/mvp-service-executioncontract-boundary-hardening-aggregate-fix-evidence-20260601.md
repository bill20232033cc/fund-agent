# Aggregate Fix Evidence: MVP Service ExecutionContract Boundary Hardening

## Self-check

pass

- Current gate / role: aggregate deepreview fix；本 agent 只作为 fix worker。
- Source of truth: `docs/reviews/mvp-service-executioncontract-boundary-hardening-aggregate-deepreview-20260601.md`，controller accepted findings 1 和 2。
- Scope boundary: 只修改允许文件；未进入 review、re-review、next gate、commit、push、PR、merge 或 release 状态。
- Stop conditions: 未发现需要放松 fail-closed、运行时 import cycle、无法修复验证失败或 worktree ownership 不清的情况。

## Source Review Artifact

- `docs/reviews/mvp-service-executioncontract-boundary-hardening-aggregate-deepreview-20260601.md`

## Accepted Findings Fixed

- Finding 1: `QualityFailClosedPolicy` is constructed but not consumed at runtime.
- Finding 2: `QualityGatePolicy` Literal is independently defined in both `execution_contract.py` and `fund_analysis_service.py`.

## Per-finding Status

- F1: fixed
  - `analyze_with_llm_execution()` now validates `execution_request.runtime_plan.quality_fail_closed_policy` before converting the request or running extraction/LLM orchestration.
  - Any runtime policy field that would weaken current fail-closed behavior raises `ValueError` before execution:
    - `fail_on_quality_gate_block=False`
    - `fail_on_quality_gate_not_run=False`
    - `fail_on_partial_orchestration=False`
    - `fail_on_incomplete_final_assembly=False`
    - `deterministic_fallback_allowed=True`
  - Current accepted behavior remains fail-closed; deterministic `analyze()` and `checklist()` paths are unchanged.
- F2: fixed
  - `QualityGatePolicy` remains defined in `fund_agent/services/execution_contract.py`.
  - `fund_agent/services/fund_analysis_service.py` imports `QualityGatePolicy` from `execution_contract` instead of declaring a separate Literal alias.
  - `fund_agent/services/__init__.py` re-exports `QualityGatePolicy` from the execution contract source.

## Changed Files

- `fund_agent/services/execution_contract.py`
  - No content change; remains the single type source for `QualityGatePolicy`.
- `fund_agent/services/fund_analysis_service.py`
  - Consumes and validates `QualityFailClosedPolicy` in `analyze_with_llm_execution()`.
  - Imports `QualityGatePolicy` from `execution_contract`.
- `fund_agent/services/__init__.py`
  - Re-exports `QualityGatePolicy` from `execution_contract`.
- `tests/services/test_execution_contract.py`
  - Adds a guard that `fund_analysis_service.py` does not redeclare `QualityGatePolicy` and imports it from `execution_contract`.
- `tests/services/test_fund_analysis_service_llm.py`
  - Adds execution-path coverage that weakened fail-closed policy values fail before extractor or LLM clients run.
- `docs/reviews/mvp-service-executioncontract-boundary-hardening-aggregate-fix-evidence-20260601.md`
  - This evidence artifact.

## Validation Commands and Results

- `uv run pytest tests/services/test_execution_contract.py tests/services/test_fund_analysis_service_llm.py -q`
  - PASS: `43 passed in 0.78s`
- `uv run pytest tests/host/test_runtime_state.py tests/host/test_runtime_runner.py tests/services/test_execution_contract.py tests/services/test_fund_analysis_service_llm.py tests/ui/test_cli.py -q`
  - PASS: `116 passed in 0.84s`
- `uv run ruff check .`
  - PASS: `All checks passed!`
- `uv run pytest --cov=fund_agent --cov-report=term-missing --cov-fail-under=50 -q`
  - PASS: `1261 passed in 5.56s`
  - Coverage: `91.90%`, required `50%`

## New Residual Risks / Open Questions

- none

## No Stage / Commit / Push / PR Confirmation

- No `git add`, `git commit`, `git push`, PR creation, merge, release, review, re-review, or next-gate action was performed by this fix worker.
