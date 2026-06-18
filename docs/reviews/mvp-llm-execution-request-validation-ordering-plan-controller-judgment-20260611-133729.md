# LLM Execution Request Validation Ordering Plan Controller Judgment

## Scope

- Gate: `LLM execution request validation ordering gate`
- Classification: `standard`
- Judgment time: `2026-06-11 13:37:29`
- Mode: plan controller judgment only
- Verdict: `ACCEPT_WITH_AMENDMENTS`

## Truth Inputs

- `AGENTS.md`: Service owns request/ExecutionContract assembly and provider construction/runtime ceilings; Host remains lifecycle-only; explicit business parameters must not be hidden in `extra_payload`.
- `docs/design.md`: current `--use-llm` path is explicit opt-in and provider-backed; Service constructs `FundLLMExecutionRequest` / `ExecutionContract`, Host governs lifecycle/deadline/cancel/events, Agent owns current no-live body-chapter mechanics.
- `docs/implementation-control.md`: active gate is `LLM execution request validation ordering gate`; provider defaults/runtime changes and live provider/EID/PDF/FDR/network commands are out of scope.
- `docs/current-startup-packet.md`: current entry is planning; no implementation write set existed before this plan acceptance.
- Plan: `docs/reviews/mvp-llm-execution-request-validation-ordering-plan-20260611-133114.md`
- MiMo review: `docs/reviews/mvp-llm-execution-request-validation-ordering-plan-review-mimo-20260611-133729.md`
- DS review: `docs/reviews/mvp-llm-execution-request-validation-ordering-plan-review-ds-20260611-133729.md`

## Review Disposition

| Reviewer | Verdict | Controller disposition |
|---|---|---|
| AgentMiMo | `ACCEPT` | Accepted. Low finding on `opt_in_mode` validation source was addressed by plan amendment. |
| AgentDS | `ACCEPT` | Accepted. Low findings on explicit runtime-plan construction details and duplicate validation were addressed by plan amendment. |

## Accepted Amendments

- The plan now states that invalid `opt_in_mode` is validated by constructing `FundLLMExecutionContract(..., llm_opt_in_mode=opt_in_mode)` before provider config/client construction.
- The plan now makes `QualityFailClosedPolicy` and `SafeDiagnosticPolicy` construction explicit before `FundLLMRuntimePlan`.
- The plan now keeps duplicate `product` mode plus `developer_overrides` validation as defense-in-depth and forbids semantic deduplication in this gate.
- The plan now defers LLM path parity with deterministic `_validate_request()` checks to a separate consistency gate.

## Accepted Implementation Write Set

Implementation may modify only:

- `fund_agent/services/fund_analysis_service.py`
- `tests/services/test_fund_analysis_service_llm.py`

Optional only if a direct test-boundary gap is found:

- `tests/services/test_execution_contract.py`

No other source, test, docs, config, runtime artifact, control doc or design doc file is authorized during implementation.

## Implementation Acceptance Requirements

Implementation must satisfy the plan's acceptance criteria:

- invalid business request fails before provider config/client construction;
- invalid `opt_in_mode` fails before provider client construction through the existing contract runtime check;
- valid execution request fields remain unchanged;
- config/provider construction errors still fail before Host run;
- no live provider/EID/PDF/FDR/network command is run;
- no provider default/runtime/budget/typed path/Host/Agent/fallback/source behavior changes are introduced;
- no `extra_payload` or open business payload bag appears.

Required validation:

```bash
uv run pytest tests/services/test_fund_analysis_service_llm.py tests/services/test_execution_contract.py -q
uv run ruff check fund_agent/services/fund_analysis_service.py tests/services/test_fund_analysis_service_llm.py tests/services/test_execution_contract.py
git diff --check
git diff --name-only
```

## Residuals

| Residual | Disposition | Owner / next handling |
|---|---|---|
| Duplicate `product` mode plus `developer_overrides` validation | `ACCEPTED_RESIDUAL` | Keep as defense-in-depth for this gate; possible future cleanup only with reviewed scope. |
| LLM path parity with deterministic `_validate_request()` checks such as `quality_gate_run_id` / `quality_gate_output_dir` | `DEFER` | Separate consistency gate; not required to prove provider-construction ordering. |
| Provider runtime/live acceptance residuals | `DEFER` | Separate controlled live provider gates. |

## Final Judgment

`ACCEPT_WITH_AMENDMENTS`.

The plan is accepted for bounded implementation. The next gate may implement the accepted write set only, with no live/provider/network execution and no provider runtime/default/Host/Agent semantic changes.
