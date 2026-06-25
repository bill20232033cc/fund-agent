# Evidence Confirm Productionization EC-P4 Aggregate Deepreview Fix

## Scope

- Gate: aggregate deepreview fix gate.
- Role: AgentCodex fix worker only.
- Accepted finding fixed: `docs/reviews/code-review-20260623-002000-ds-ec-p4-aggregate-deepreview.md` F1.
- Non-goals: no F2/F3 changes, no live/PDF/provider/network commands, no PR mutation, no commit, no push, no readiness claim.

## Changed Files

- `fund_agent/fund/evidence_confirm_runner.py`
- `fund_agent/services/fund_analysis_service.py`
- `fund_agent/fund/README.md`
- `docs/reviews/evidence-confirm-productionization-ec-p4-aggregate-deepreview-fix-20260623.md`

## Root Cause

`fund_agent/services/fund_analysis_service.py` imported `EvidenceConfirmRepositoryRunRequest`,
`EvidenceConfirmRepositoryRunResult`, and `run_repository_bounded_evidence_confirm` directly from
`fund_agent.fund.evidence_confirm_sources`. The LLM Service import boundary test rejects imported
module names containing forbidden fragments such as `source`. The direct import path therefore failed
the boundary test even though the intended runtime behavior was repository-bounded Fund-layer Evidence
Confirm execution.

## Fix Summary

- Added `fund_agent.fund.evidence_confirm_runner` as the explicit Fund-layer typed facade for the
  repository-bounded Evidence Confirm runner.
- Updated `fund_agent.services.fund_analysis_service` to import the request/result types and runner
  from that facade.
- Updated `fund_agent/fund/README.md` to document the new Service-facing facade while keeping the
  underlying implementation in `evidence_confirm_sources`.
- Kept the underlying implementation in `fund_agent.fund.evidence_confirm_sources`.
- Did not weaken the Service boundary test and did not add a forbidden import whitelist.

## Validation

- `uv run pytest tests/services/test_fund_analysis_service_llm.py::test_fund_analysis_service_imports_keep_llm_path_above_forbidden_boundaries -q`
  - Result: passed, `1 passed in 0.64s`.
- `uv run pytest tests/services/test_fund_analysis_service.py -q -k evidence_confirm`
  - Result: passed, `8 passed, 32 deselected in 0.57s`.
- `uv run pytest tests/fund/test_evidence_confirm_production.py tests/fund/test_quality_gate_integration.py tests/fund/test_evidence_confirm_semantic.py -q`
  - Result: passed, `47 passed in 0.54s`.
- `uv run ruff check fund_agent/services/fund_analysis_service.py fund_agent/fund/evidence_confirm_runner.py`
  - Result: passed, `All checks passed!`.
- `git diff --check -- fund_agent/services/fund_analysis_service.py fund_agent/fund/evidence_confirm_runner.py fund_agent/fund/README.md`
  - Result: passed, exit code 0 with no output.

## Residual Risks

- F2/F3 were not reviewed or fixed in this gate; classified as assigned to their existing aggregate
  deepreview finding owners.
- This fix introduces a facade naming boundary only; if future Service code imports new Fund modules
  with forbidden path fragments, the existing boundary test remains the owner for catching that.

## Completion

AGGREGATE_DEEPREVIEW_FIX_COMPLETE_NOT_READY
