# Aggregate Fix Artifact — repo-deepreview-audit-type-guards

## Gate

- Current gate: aggregate fix
- Work unit: repo-deepreview-audit-type-guards
- Source aggregate review: `docs/reviews/aggregate-deepreview-repo-deepreview-audit-type-guards-ds-20260523.md`
- Stop status: fixed accepted aggregate finding and stopped for aggregate re-review.

## Accepted Finding Status

### 1-已修复-低-`validate_programmatic_contract_rules` 重复加载 coverage manifest 引入冗余校验但无 correctness 风险

- Source: AgentDS aggregate finding 1.
- Decision: accepted.
- Fix:
  - Added `_build_contract_audit_coverage_manifest()` to construct the coverage manifest without validating it.
  - Updated `load_contract_audit_coverage_manifest()` to build then validate for public/default loading.
  - Updated `validate_programmatic_contract_rules()` to validate the coverage manifest once with the actual `rules.forbidden_contents`.
  - Removed the extra `load_contract_audit_coverage_manifest()` call from `load_programmatic_contract_rules()`.
- Rationale: Keeps fail-closed validation behavior while separating construction from validation and eliminating the confusing duplicate validation path.

## Changed Files

- `fund_agent/fund/audit/contract_rules.py`
- `docs/reviews/aggregate-fix-repo-deepreview-audit-type-guards-20260523.md`

## Validation

- `uv run pytest tests/fund/audit/test_audit_programmatic.py tests/fund/template/test_contracts.py tests/fund/template/test_renderer.py -q`
  - Result: `97 passed in 0.45s`
- `uv run pytest -q`
  - Result: `549 passed in 1.08s`
- `uv run ruff check .`
  - Result: `All checks passed!`

## Residual Risks

- Non-programmatic `must_not_cover` routes remain declaration-only semantic coverage by design.
- Ch0 broader product improvements remain outside this work unit.
