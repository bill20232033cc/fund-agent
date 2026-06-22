# Evidence Confirm Productionization Default-on Policy Slice 1 Implementation Evidence

## Gate

- Work unit: Evidence Confirm Productionization default-on Evidence Confirm policy.
- Slice: EC-DO-1 Service Default-on Analyze Policy.
- Role: AgentCodex implementation worker only.
- Accepted plan: `docs/reviews/evidence-confirm-productionization-default-on-policy-plan-20260623.md`.
- Controller judgment: `docs/reviews/evidence-confirm-productionization-default-on-policy-plan-controller-judgment-20260623.md`.
- Artifact: `docs/reviews/evidence-confirm-productionization-default-on-policy-slice1-implementation-evidence-20260623.md`.

## Scope

Changed files:

- `fund_agent/services/fund_analysis_service.py`
- `tests/services/test_fund_analysis_service.py`
- `docs/reviews/evidence-confirm-productionization-default-on-policy-slice1-implementation-evidence-20260623.md`

No CLI, quality gate production code, README, design/control docs, PR state, git state, live/PDF/network/provider/LLM path, repository/source/cache/parser access, public opt-out field, or files outside the allowed write set were changed.

## Implementation

- Changed product `_resolve_analyze_contract()` default `evidence_confirm_policy` from `off` to `warn`.
- Preserved developer mode default as `overrides.evidence_confirm_policy or "off"`.
- Preserved checklist effective policy as forced `off`.
- Updated the plan-listed Service docstrings/comments for:
  - `FundAnalysisDeveloperOverrides.evidence_confirm_policy`
  - `_run_evidence_confirm_if_enabled()`
  - `_effective_evidence_confirm_policy()`
- Added service tests for:
  - product `analyze` default warn pass runner invocation and normalized runner request;
  - product `analyze` default warn fail as non-blocking summary;
  - product `analyze` runner exception converted to safe compact warn-policy summary;
  - product `analyze-annual-period` inherited warn through delegated `analyze()`;
  - product/default `checklist` staying Evidence Confirm off;
  - developer omitted/off policy staying off and not inheriting product warn.

## Validation

```text
uv run pytest tests/services/test_fund_analysis_service.py
46 passed in 0.98s
```

```text
uv run ruff check fund_agent/services/fund_analysis_service.py tests/services/test_fund_analysis_service.py
All checks passed!
```

```text
git diff --check -- fund_agent/services/fund_analysis_service.py tests/services/test_fund_analysis_service.py docs/reviews/evidence-confirm-productionization-default-on-policy-slice1-implementation-evidence-20260623.md
<no output>
```

## Residual Risks

| Residual | Classification | Owner / destination |
|---|---|---|
| CLI default-on output/help and no-opt-out guard not updated in this slice | covered by later approved slice | EC-DO-2 |
| Explicit quality gate ECQ warn-policy regression not updated in this slice | covered by later approved slice | EC-DO-3 |
| Checklist Evidence Confirm CLI/support remains absent | covered by later approved gate | Checklist Evidence Confirm gate |
| Provider-backed/live semantic quality remains unproven | covered by later approved gate | Provider-backed semantic quality gate |
| Multi-sample live source/PDF coverage remains unproven | covered by later approved gate | Multi-sample live evidence gate |
| Release/readiness remains `NOT_READY` | assigned to later work unit | Release/readiness gate after blocker closure |

No unclassified residual risk is introduced by EC-DO-1.

## Stop Condition

EC-DO-1 did not require changing files outside the allowed set, adding a public opt-out field, changing checklist behavior, or adding direct Service access to repository/PDF/cache/source/parser/provider internals.

## Verdict

IMPLEMENTATION_SLICE_READY_FOR_REVIEW
