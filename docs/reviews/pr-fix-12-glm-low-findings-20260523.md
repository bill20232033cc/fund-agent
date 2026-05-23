# PR Fix Artifact — PR 12 GLM Low Findings

## Gate

- Current gate: PR fix
- Work unit: repo-deepreview-audit-type-guards
- PR review artifact: `docs/reviews/pr-review-12-glm-20260523.md`
- PR: https://github.com/bill20232033cc/fund-agent/pull/12

## Accepted Finding Status

### 01-已修复-低-test_analyze_cli_help 宽度依赖

- Status: already fixed before this artifact.
- Evidence: latest CI run `26318095338` passed after switching the long option assertion to command metadata.

### 02-已修复-低-inception_date 测试 fixture 缺失

- Fix:
  - Added `inception_date` to the renderer `_bundle()` basic identity fixture.
  - Added a Ch0 profile assertion covering the disclosed inception date path.

### 03-已修复-低-checklist bool guard 测试仅覆盖 True

- Fix:
  - Updated the checklist bool guard test to cover both `True` and `False`.

### 04-已修复-低-thermometer_source._to_decimal 缺少 bool guard

- Fix:
  - Added explicit bool rejection in `fund_agent/fund/data/thermometer_source.py`.
  - Added a focused test for bool PE/PB source values.

## Changed Files

- `tests/fund/template/test_renderer.py`
- `tests/fund/analysis/test_checklist.py`
- `fund_agent/fund/data/thermometer_source.py`
- `tests/fund/data/test_thermometer_source.py`
- `docs/reviews/pr-fix-12-glm-low-findings-20260523.md`

## Validation

- `uv run pytest tests/fund/template/test_renderer.py tests/fund/analysis/test_checklist.py tests/fund/data/test_thermometer_source.py tests/ui/test_cli.py::test_analyze_cli_help_documents_auto_valuation_and_opt_out -q`
  - Result: `63 passed in 0.85s`
- `uv run pytest -q`
  - Result: `551 passed in 1.22s`
- `uv run ruff check .`
  - Result: `All checks passed!`

## Residual Risks

- None for the accepted PR review findings.
