# LLM Execution Request Validation Ordering Implementation Controller Judgment

## Scope

- Gate: `LLM execution request validation ordering gate`
- Classification: `standard`
- Judgment time: `2026-06-11 13:47:02`
- Verdict: `ACCEPT_WITH_RESIDUALS`

## Truth Inputs

- `AGENTS.md`: Service owns use-case orchestration, ExecutionContract assembly and provider construction/runtime ceilings; Host remains lifecycle-only; no `extra_payload` business parameter bag is allowed.
- `docs/design.md`: `--use-llm` is explicit opt-in provider-backed path; Service constructs `FundLLMExecutionRequest` / `ExecutionContract`; Host governs lifecycle; Agent owns body-chapter mechanics.
- `docs/implementation-control.md`: active gate is `LLM execution request validation ordering gate`; provider defaults/runtime changes, live provider/EID/PDF/FDR/network and Host/Agent behavior changes are out of scope.
- `docs/current-startup-packet.md`: current gate is planning/implementation for LLM execution request validation ordering; no live/provider external action is authorized.
- Plan: `docs/reviews/mvp-llm-execution-request-validation-ordering-plan-20260611-133114.md`
- Plan controller judgment: `docs/reviews/mvp-llm-execution-request-validation-ordering-plan-controller-judgment-20260611-133729.md`
- Implementation evidence: `docs/reviews/mvp-llm-execution-request-validation-ordering-implementation-evidence-20260611.md`
- MiMo review: `docs/reviews/mvp-llm-execution-request-validation-ordering-implementation-review-mimo-20260611-134702.md`
- DS review: `docs/reviews/mvp-llm-execution-request-validation-ordering-implementation-review-ds-20260611-134702.md`

## Accepted Write Set

- `fund_agent/services/fund_analysis_service.py`
- `tests/services/test_fund_analysis_service_llm.py`
- `docs/reviews/mvp-llm-execution-request-validation-ordering-implementation-evidence-20260611.md`
- `docs/reviews/mvp-llm-execution-request-validation-ordering-implementation-review-mimo-20260611-134702.md`
- `docs/reviews/mvp-llm-execution-request-validation-ordering-implementation-review-ds-20260611-134702.md`
- `docs/reviews/mvp-llm-execution-request-validation-ordering-implementation-controller-judgment-20260611-134702.md`

No optional `tests/services/test_execution_contract.py` change was needed.

## Review Disposition

| Reviewer | Verdict | Controller disposition |
|---|---|---|
| AgentMiMo | `ACCEPT` | Accepted. No blocking findings. |
| AgentDS | `ACCEPT` | Accepted. No blocking findings. |

## Acceptance Evidence

- `uv run pytest tests/services/test_fund_analysis_service_llm.py tests/services/test_execution_contract.py -q` -> `50 passed in 0.48s`
- `uv run ruff check fund_agent/services/fund_analysis_service.py tests/services/test_fund_analysis_service_llm.py tests/services/test_execution_contract.py` -> `All checks passed!`
- `git diff --check` -> no output
- `git diff --name-only` -> exactly:
  - `fund_agent/services/fund_analysis_service.py`
  - `tests/services/test_fund_analysis_service_llm.py`

## Controller Findings

- ACCEPT: Invalid business request / contract validation now occurs before provider config/client construction.
  - Basis: `fund_analysis_service.py:939-953`; MiMo and DS reviews.
- ACCEPT: Invalid `opt_in_mode` is rejected by the existing `FundLLMExecutionContract.__post_init__` runtime validation before provider construction.
  - Basis: contract construction before config load; focused spy test.
- ACCEPT: Provider clients are constructed only after `FundLLMRuntimePlan` construction succeeds.
  - Basis: `fund_analysis_service.py:976-988`.
- ACCEPT: Valid request/runtime behavior is unchanged.
  - Basis: existing valid-path assertions in `tests/services/test_fund_analysis_service_llm.py`; focused tests passed.
- ACCEPT: No provider default/runtime budget, typed path, Host, Agent, fallback/source, live provider/EID/PDF/FDR/network or open payload-bag behavior was changed.
  - Basis: diff review, ruff, tests and reviewer evidence.

## Residuals

| Residual | Disposition | Owner / next handling |
|---|---|---|
| Duplicate product-mode plus developer-overrides validation remains in `_resolve_analyze_contract()` and `normalize_fund_llm_analysis_input()` | `ACCEPTED_RESIDUAL` | Keep as defense-in-depth; future cleanup only under reviewed scope. |
| Invalid identity spy test covers a five-digit code, not an empty string | `ACCEPTED_RESIDUAL` | Non-blocking because both cases use `_validate_fund_identity`; broaden only if future tests touch this area. |
| LLM path parity with deterministic `_validate_request()` checks (`quality_gate_run_id`, `quality_gate_output_dir`) | `DEFER` | Separate consistency gate; not required for provider-construction ordering acceptance. |

## Final Judgment

`ACCEPT_WITH_RESIDUALS`.

The implementation satisfies the accepted plan: Service-owned invalid request/contract validation now fails before provider config/client construction and before any Host/Agent/provider execution path. The change is narrow, no-live, covered by focused tests and reviews, and does not alter provider runtime/defaults or Host/Agent semantics.

Next control step: create local accepted checkpoint for this implementation, sync `docs/current-startup-packet.md` and `docs/implementation-control.md`, and set the next mainline entry to `UI-Service-Host boundary reconciliation gate`.
