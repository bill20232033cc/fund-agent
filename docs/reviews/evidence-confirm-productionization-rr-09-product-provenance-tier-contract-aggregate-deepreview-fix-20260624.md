# RR-09 Product Provenance Tier Contract Aggregate Deepreview Fix

## Gate

- Work unit: RR-09 Product Provenance Tier Contract
- Gate: Aggregate Deepreview Fix Gate
- Finding: `AGG-S2-001`
- Review artifact: `docs/reviews/code-review-20260624-171738.md`

## Fix Summary

- Changed `_provenance_contract_from_result()` so `pathway_status="pass"` plus existing V2 result but `reference_build_result=None` no longer returns provenance `not_run`.
- Added `_missing_reference_build_provenance_contract()`:
  - if there are checked applicable facts, returns `provenance_status="fail"`, `minimum_provenance_tier="none"`, and `provenance_missing_fact_count=<applicable_fact_count>`;
  - if all facts are `not_applicable`, keeps the existing provenance `not_run` semantics.
- Updated the regression test for missing `reference_build_result` plus V2 pass to expect provenance missing rather than not-run.

## Validation

- `uv run pytest tests/fund/test_evidence_confirm_production.py tests/services/test_fund_analysis_service.py tests/fund/test_evidence_confirm_semantic.py tests/fund/test_quality_gate_integration.py tests/ui/test_cli.py -q`
  - Result: `186 passed in 1.20s`
- `uv run ruff check fund_agent/fund/evidence_confirm_production.py tests/fund/test_evidence_confirm_production.py fund_agent/fund/quality_gate_integration.py fund_agent/ui/cli.py tests/fund/test_quality_gate_integration.py tests/ui/test_cli.py tests/services/test_fund_analysis_service.py tests/fund/test_evidence_confirm_semantic.py`
  - Result: `All checks passed!`
- `git diff --check -- fund_agent/fund/evidence_confirm_production.py tests/fund/test_evidence_confirm_production.py docs/reviews/code-review-20260624-171738.md`
  - Result: passed

## Non-goals

- No live/PDF, repository/source-helper/parser, product CLI, provider/LLM command was run.
- No ECQ severity change beyond consuming the corrected summary contract.
- No checklist support, report-body rendering, FDD default-on, tag, release or readiness action was performed.

## Residual Risk

- Requires aggregate re-review before accepted deepreview commit.
- B1 `017641 / 2024` runtime product CLI re-evidence and A6 live/PDF re-evidence remain separate gates.

## Completion Status

`RR_09_PRODUCT_PROVENANCE_TIER_CONTRACT_AGGREGATE_DEEPREVIEW_FIX_READY_FOR_REREVIEW_NOT_READY`

Artifact path: `docs/reviews/evidence-confirm-productionization-rr-09-product-provenance-tier-contract-aggregate-deepreview-fix-20260624.md`
