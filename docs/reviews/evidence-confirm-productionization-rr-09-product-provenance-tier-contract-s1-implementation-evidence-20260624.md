# RR-09 Product Provenance Tier Contract S1 Implementation Evidence

Final token:

`RR_09_PRODUCT_PROVENANCE_TIER_CONTRACT_S1_IMPLEMENTED_READY_FOR_CODE_REVIEW_NOT_READY`

## Gate

Gate: `RR-09 Product Provenance Tier Contract No-live Implementation Gate - Slice S1`.

Classification: `heavy`, inherited from the accepted plan because this slice changes the product Evidence Confirm summary contract.

This is a no-live implementation evidence artifact. It does not run live/PDF, repository/source-helper/parser, product CLI, provider/LLM, checklist, report-body, FDD default-on, tag, release or readiness actions.

## Scope

Accepted S1 files changed:

- `fund_agent/fund/evidence_confirm_production.py`
- `fund_agent/services/fund_analysis_service.py`
- `tests/fund/test_evidence_confirm_production.py`
- `tests/services/test_fund_analysis_service.py`
- `tests/fund/test_evidence_confirm_semantic.py`

No S2 files were changed. ECQ mapping, CLI safe summary lines, Fund README and `docs/design.md` are unchanged and remain S2 scope.

## Implementation Summary

Implemented summary v2 provenance contract:

- Upgraded `EvidenceConfirmProductionSummary.schema_version` to `evidence_confirm_production_summary.v2`.
- Added safe scalar fields:
  - `provenance_status`
  - `minimum_provenance_tier`
  - `provenance_missing_fact_count`
  - `strict_precision_residual_count`
  - `strict_precision_issue_ids`
- Added provenance tier/status type aliases.
- Added repository-result-only provenance helpers:
  - `_reference_tier()`
  - `_strongest_tier()`
  - `_weakest_tier()`
  - `_dimension_by_name()`
  - `_provenance_contract_from_result()`
- Kept `cell` reserved; current producer emits only `none`, `section`, `table` or `row`.
- Kept `reference_build_result=None` plus V2 pass as `provenance_status="not_run"` and `minimum_provenance_tier="none"`, not provenance pass.
- Updated runner-exception summary construction to v2 with provenance defaults.
- Updated Service and semantic shared fake repository fixtures to include minimal section-level reference build result and V2 dimensions.
- Updated semantic fixture default row locator so deterministic V2 pass fixtures remain truly pass; existing explicit degraded-reference tests still cover anchor-precision warn.

## Contract Checks

S1 binding constraints satisfied:

- Provenance derives only from `EvidenceConfirmRepositoryRunResult.reference_build_result.references`, V2 fact dimension results and existing reference metadata.
- Summary helper does not read repository, PDF/cache, source helper, parser, provider, LLM or report body.
- `candidate_only` or non-proven references are not accepted as provenance.
- `not_applicable` facts remain outside provenance blockers and strict precision residuals.
- `source_support` / `missing_evidence` failure increments `provenance_missing_fact_count`.
- `value_match` failure with section-or-better provenance increments `strict_precision_residual_count` and preserves stable issue ids.

## Validation

Focused S1 validation:

```bash
uv run pytest tests/fund/test_evidence_confirm_production.py tests/services/test_fund_analysis_service.py tests/fund/test_evidence_confirm_semantic.py
```

Result: `78 passed`.

Additional static checks:

```bash
uv run ruff check fund_agent/fund/evidence_confirm_production.py fund_agent/services/fund_analysis_service.py tests/fund/test_evidence_confirm_production.py tests/services/test_fund_analysis_service.py tests/fund/test_evidence_confirm_semantic.py
```

Result: `All checks passed!`.

```bash
git diff --check -- fund_agent/fund/evidence_confirm_production.py fund_agent/services/fund_analysis_service.py tests/fund/test_evidence_confirm_production.py tests/services/test_fund_analysis_service.py tests/fund/test_evidence_confirm_semantic.py
```

Result: passed with no output.

## Residuals

| Residual | Disposition |
|---|---|
| ECQ1/ECQ2 provenance vs strict precision split | Covered by approved Slice S2 |
| CLI safe provenance lines | Covered by approved Slice S2 |
| Fund README / design current-state wording | Covered by approved Slice S2 |
| Quality gate test helper update outside S1 | Covered by approved Slice S2 |
| Existing R1-R4 strict V2 value-match failures | Optional A6 strict-precision evidence path after S1/S2 |
| B1 `017641 / 2024` `manager_strategy_text` P0 block | Separate RR-09 B1 residual gate |
| Checklist/report-body/provider default/tag/release/readiness | Separate existing gates; remains `NOT_READY` |

## Completion

S1 implementation is complete and ready for code review.

Next gate:

`RR-09 Product Provenance Tier Contract S1 Code Review Gate`

Completion token:

`RR_09_PRODUCT_PROVENANCE_TIER_CONTRACT_S1_IMPLEMENTED_READY_FOR_CODE_REVIEW_NOT_READY`
