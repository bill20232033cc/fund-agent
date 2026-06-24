# RR-09 Product Provenance Tier Contract S1 Code Review Fix

## Gate

- Work unit: RR-09 Product Provenance Tier Contract
- Gate: S1 Code Review Fix Gate
- Accepted finding: `CR-S1-001` from `docs/reviews/code-review-20260624-161429.md`
- Scope: no-live S1 summary v2 provenance contract compatibility fix only

## Fix

`CR-S1-001` is fixed.

Changed files:

- `fund_agent/fund/evidence_confirm_production.py`
- `tests/fund/test_evidence_confirm_production.py`

Implementation:

- Added conservative defaults to S1 provenance fields on `EvidenceConfirmProductionSummary`:
  - `provenance_status="not_run"`
  - `minimum_provenance_tier="none"`
  - `provenance_missing_fact_count=0`
  - `strict_precision_residual_count=0`
  - `strict_precision_issue_ids=()`
- Kept `summary_from_repository_result()` and `not_run_evidence_confirm_summary()` explicit v2 population unchanged.
- Added regression coverage proving old-shape construction defaults to `not_run/none`, not provenance pass.

## Validation

- `uv run pytest tests/fund/test_quality_gate_integration.py -q`
  - Result: `20 passed`
  - Covers: review finding repro suite that previously failed with `11 failed, 9 passed`
- `uv run pytest tests/fund/test_evidence_confirm_production.py tests/services/test_fund_analysis_service.py tests/fund/test_evidence_confirm_semantic.py -q`
  - Result: `79 passed`
  - Covers: S1 focused production summary, Service fake repository fixture, semantic fixture suite
- `uv run ruff check fund_agent/fund/evidence_confirm_production.py tests/fund/test_evidence_confirm_production.py fund_agent/services/fund_analysis_service.py tests/services/test_fund_analysis_service.py tests/fund/test_evidence_confirm_semantic.py`
  - Result: `All checks passed!`
- `git diff --check -- fund_agent/fund/evidence_confirm_production.py tests/fund/test_evidence_confirm_production.py docs/current-startup-packet.md docs/implementation-control.md docs/reviews/code-review-20260624-161429.md`
  - Result: passed

## Non-goals

- No S2 ECQ/CLI/docs behavior was implemented.
- No live/PDF, repository/source-helper/parser, product CLI, provider/LLM, checklist, report-body, FDD default-on, tag, release or readiness command was run.
- No B1 `017641 / 2024` runtime re-evidence was attempted.

## Residual Risk

- S2 quality-gate/CLI projection remains a later approved slice.
- S1 still requires targeted re-review before an accepted slice checkpoint.

## Completion Status

`RR_09_PRODUCT_PROVENANCE_TIER_CONTRACT_S1_CODE_REVIEW_FIX_READY_FOR_REREVIEW_NOT_READY`

Artifact path: `docs/reviews/evidence-confirm-productionization-rr-09-product-provenance-tier-contract-s1-code-review-fix-20260624.md`
