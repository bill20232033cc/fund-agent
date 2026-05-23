# Quality Gate And Final Judgment Contract Implementation

## Gate

- Work unit: quality gate and final judgment contract audit
- Branch: `codex/checklist-host-engine-design`
- Date: 2026-05-24
- Status: implementation completed locally
- Plan: `docs/reviews/quality-gate-final-judgment-contract-plan-20260524.md`

## Scope

This slice turns the current Quality Gate and `derive_final_judgment()` behavior into an explicit design contract and adds narrow regression tests for the highest-risk state combinations.

## Changed Files

- `docs/design.md`
- `docs/implementation-control.md`
- `tests/fund/analysis/test_final_judgment.py`
- `tests/services/test_fund_analysis_service.py`

## Implemented Plan Items

- Added final judgment precedence table:
  - `suggest_replace` for product/user-capacity veto evidence.
  - `needs_attention` for quality uncertainty, watch signals, gray/yellow checklist, or stress warning.
  - `worth_holding` only when checklist/risk/stress are green and quality gate is `pass` or `warn`.
  - fail-safe remains `needs_attention`.
- Added Service policy / gate state table:
  - `block + block` and `block + not_run` raise structured exceptions before final judgment.
  - `warn` continues and passes actual gate status to final judgment.
  - `off` continues as `not_run`, developer-only, and cannot produce `worth_holding` from otherwise-green signals.
- Added tests proving:
  - gate `warn` does not alone downgrade an otherwise all-green product judgment;
  - gate `not_run` prevents an otherwise-green result from becoming `worth_holding`;
  - `checklist()` shares the same block-policy Quality Gate behavior as `analyze()`.

## Validation

```bash
uv run pytest tests/fund/analysis/test_final_judgment.py tests/services/test_fund_analysis_service.py -q
# 35 passed

uv run pytest tests/fund/test_quality_gate.py tests/fund/test_quality_gate_integration.py tests/ui/test_cli.py -q
# 65 passed

uv run pytest -q
# 617 passed

uv run ruff check .
# All checks passed

uv lock --check
# Resolved 75 packages

uv run python -c "import fund_agent; print('ok')"
# ok

git diff --check
# passed
```

## Docs Decision

This gate updates only design/control documents because the behavior already existed in code. No README update is required: user-facing commands and usage did not change.

## Residual Risks

- This gate does not change or revalidate the deeper Quality Gate scoring formulas FQ0-FQ6 beyond existing tests.
- This gate does not cover future Host/Agent runtime behavior because current production flow is still deterministic UI -> Service -> `fund_agent/fund`.

## Completion Signal

Implementation is complete and ready for local code review / acceptance after coverage validation.
