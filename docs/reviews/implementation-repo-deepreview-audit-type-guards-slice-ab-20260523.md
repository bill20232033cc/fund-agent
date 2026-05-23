# Implementation Artifact — repo-deepreview-audit-type-guards

## Gate

- Current gate: implementation
- Work unit: repo-deepreview-audit-type-guards
- Assigned scope: Slice A and Slice B from `docs/reviews/controller-judgment-repo-deepreview-20260523.md`
- Stop status: stopped after implementation artifact, per handoff instruction

## Scope

Implemented only accepted findings:

- AgentDS F-1: C2 `must_not_cover` missing reverse completeness validation.
- AgentDS F-2: Ch0 `required_output_items` share indistinguishable marker.
- AgentDS F-3/F-4: `bool` accepted as numeric input in ratio/decimal/quality gate helpers.

No commit, push, PR, agent dispatch, or gate transition was performed.

## Changed Files

- `fund_agent/fund/audit/contract_rules.py`
- `fund_agent/fund/template/renderer.py`
- `fund_agent/fund/analysis/_ratios.py`
- `fund_agent/fund/analysis/risk_check.py`
- `fund_agent/fund/analysis/checklist.py`
- `fund_agent/fund/quality_gate.py`
- `tests/fund/audit/test_audit_programmatic.py`
- `tests/fund/analysis/test_ratios.py`
- `tests/fund/analysis/test_risk_check.py`
- `tests/fund/analysis/test_checklist.py`
- `tests/fund/test_quality_gate.py`
- `tests/fund/integration/test_p3_cli_e2e_matrix.py`
- `docs/reviews/implementation-repo-deepreview-audit-type-guards-slice-ab-20260523.md`

## Implemented Items

### Slice A

- Added `ContractMustNotCoverCoverageRule` and `must_not_cover_coverages` to the audit coverage manifest.
- Added reverse completeness validation requiring every template `must_not_cover` item to be covered by either:
  - a programmatic forbidden marker rule, or
  - an explicit non-programmatic narrative coverage route with rationale.
- Made validation use the current `ProgrammaticContractRules.forbidden_contents`, so deleting a forbidden marker rule now fails closed unless an explicit non-programmatic route covers that exact manifest item.
- Split Ch0 markers:
  - `一句话这是什么基金` -> `这是什么基金：`
  - `基金简介` -> `基金简介：`
- Updated Ch0 rendering to output two independent bullets, preserving the low cognitive burden cover-page intent.

### Slice B

- Added explicit `bool` rejection before `int | float` handling in:
  - `parse_ratio`
  - `risk_check._parse_decimal`
  - `checklist._parse_decimal`
  - quality gate `_required_number`
  - quality gate `_required_quality_number`
- Existing accepted numeric inputs remain unchanged: numeric strings, `int`, `float`, and `Decimal` still parse through the existing routes.

## Validation

- `uv run pytest tests/fund/audit/test_audit_programmatic.py tests/fund/analysis/test_ratios.py tests/fund/analysis/test_risk_check.py tests/fund/analysis/test_checklist.py tests/fund/test_quality_gate.py -q`
  - Result: `107 passed in 0.57s`
- `uv run pytest tests/fund/template/test_renderer.py tests/fund/template/test_contracts.py tests/fund/audit/test_audit_programmatic.py -q`
  - Result: `97 passed in 0.59s`
- `uv run pytest tests/fund/integration/test_p3_cli_e2e_matrix.py -q`
  - Result: `1 passed in 0.53s`
- `uv run ruff check fund_agent/fund/audit/contract_rules.py fund_agent/fund/template/renderer.py fund_agent/fund/analysis/_ratios.py fund_agent/fund/analysis/risk_check.py fund_agent/fund/analysis/checklist.py fund_agent/fund/quality_gate.py tests/fund/audit/test_audit_programmatic.py tests/fund/analysis/test_ratios.py tests/fund/analysis/test_risk_check.py tests/fund/analysis/test_checklist.py tests/fund/test_quality_gate.py tests/fund/integration/test_p3_cli_e2e_matrix.py`
  - Result: `All checks passed!`

## Docs Decision

README files were not updated. The public CLI command surface and documented user workflows did not change. The visible report marker text changed only to make existing Ch0 contract items independently auditable; this is captured in focused tests and this implementation artifact.

## Residual Risks

- Non-programmatic `must_not_cover` routes document coverage responsibility but do not execute semantic or LLM audit. They prevent silent manifest coverage gaps, but they do not prove semantic conformance.
- Ch0 still has known broader product gaps from the controller backlog, including richer maximum-risk and upgrade/downgrade inputs; those are outside Slice A/B.
- Full repository test suite was not run in this work unit; focused and relevant existing modules passed.
