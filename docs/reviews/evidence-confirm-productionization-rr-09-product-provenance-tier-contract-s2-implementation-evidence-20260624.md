# RR-09 Product Provenance Tier Contract S2 Implementation Evidence

## Gate

- Work unit: RR-09 Product Provenance Tier Contract
- Gate: S2 No-live Implementation Gate
- Slice: ECQ And CLI Safe Visibility
- Base accepted slice: S1 local commit `dd3c41a`

## Changed Files

- `fund_agent/fund/quality_gate_integration.py`
- `fund_agent/ui/cli.py`
- `tests/fund/test_quality_gate_integration.py`
- `tests/ui/test_cli.py`
- `fund_agent/fund/README.md`
- `docs/design.md`

## Implementation Summary

- ECQ1 repository/source/reference pathway failure now always emits `severity="block"`, including product `warn` policy.
- ECQ2 now distinguishes:
  - `provenance_missing_N`: always `block`;
  - `strict_precision_residual_N`: follows Evidence Confirm policy (`warn` under product `warn`, `block` under `block`);
  - legacy deterministic V2 fail: preserves existing policy severity.
- CLI Evidence Confirm safe summary now prints:
  - `evidence_confirm_provenance_status`
  - `evidence_confirm_minimum_provenance_tier`
  - `evidence_confirm_provenance_missing_facts`
  - `evidence_confirm_strict_precision_residuals`
- CLI tests assert raw excerpts, paths, source URLs, parser/provider payloads and issue ids are not printed.
- `fund_agent/fund/README.md` and `docs/design.md` now describe summary v2 provenance tiers, section-or-better release floor, strict precision residuals, and the current ECQ severity contract.

## Validation

- `uv run pytest tests/fund/test_quality_gate_integration.py tests/ui/test_cli.py -q`
  - Result: `107 passed`
- `uv run ruff check fund_agent/fund/quality_gate_integration.py fund_agent/ui/cli.py tests/fund/test_quality_gate_integration.py tests/ui/test_cli.py`
  - Result: `All checks passed!`
- `git diff --check -- fund_agent/fund/evidence_confirm_production.py fund_agent/services/fund_analysis_service.py fund_agent/fund/quality_gate_integration.py fund_agent/ui/cli.py tests/fund/test_evidence_confirm_production.py tests/services/test_fund_analysis_service.py tests/fund/test_evidence_confirm_semantic.py tests/fund/test_quality_gate_integration.py tests/ui/test_cli.py fund_agent/fund/README.md docs/design.md`
  - Result: passed

## Non-goals

- No live/PDF, repository/source-helper/parser, product CLI, provider/LLM command was run.
- No checklist Evidence Confirm support was added beyond existing negative help checks.
- No report-body Evidence Confirm rendering was added.
- No FDD default-on parsing, tag, release or readiness action was performed.
- No B1 `017641 / 2024` runtime re-evidence was attempted.

## Residual Risk

- S2 still requires code review before accepted slice commit.
- A6 live/PDF re-evidence and B1 runtime product CLI re-evidence remain separate gates.

## Completion Status

`RR_09_PRODUCT_PROVENANCE_TIER_CONTRACT_S2_IMPLEMENTED_READY_FOR_CODE_REVIEW_NOT_READY`

Artifact path: `docs/reviews/evidence-confirm-productionization-rr-09-product-provenance-tier-contract-s2-implementation-evidence-20260624.md`
