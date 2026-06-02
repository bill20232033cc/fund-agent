# MVP provider runtime budget calibration evidence slice controller judgment

## Controller Self-Check

- Role: phaseflow/gateflow controller.
- Gate: `MVP provider runtime budget calibration gate`.
- Slice: evidence-only provider runtime budget calibration evidence slice.
- Classification: heavy.
- Scope: judge evidence slice result; no source/test/config/runtime/provider-budget/auditor/template/score/golden/readiness change.
- Inputs reviewed: accepted plan, plan controller judgment, evidence slice artifact, retained `summary.json`, `docs/design.md`, `docs/implementation-control.md`, and `docs/current-startup-packet.md`.

## Judgment

**Evidence slice accepted as blocked by missing provider configuration.** The retained-artifact read-only evidence was collected and validated, but the live provider rerun was correctly not executed because required provider env/config is absent in the current shell.

Accepted evidence:

- Retained `summary.json` is valid JSON.
- Retained runtime matrix confirms the accepted plan claim:
  - Ch2 terminal timeout operation is `auditor`, approx prompt tokens `743`, budget `60s x2`.
  - Ch4 terminal timeout operation is `auditor`, approx prompt tokens `584`, budget `60s x2`.
  - Ch6 terminal timeout operation is `auditor`, approx prompt tokens `731`, budget `60s x2`.
  - Ch3 remains separate as `prompt_contract` / `repair_budget_exhausted`.
- Provider env presence-only check did not print secret values and showed required config absent:
  - `FUND_AGENT_LLM_PROVIDER`: absent.
  - `FUND_AGENT_LLM_MODEL`: absent.
  - `FUND_AGENT_LLM_BASE_URL`: absent.
  - effective API key value: absent.
  - config validation: fail.
- No live provider command was run.
- No new `reports/llm-runs/` artifact was produced.

Controller disposition:

- This slice does not provide new live runtime evidence.
- Runtime-budget tuning remains blocked on provider config restoration.
- Do not infer provider endpoint/runtime behavior from the missing-config state.
- Do not implement timeout defaults, operation-specific env vars, PASS-only probe, split-audit, score-loop, or auditor changes from this slice.

## Acceptance Evidence

| Purpose | Artifact |
|---|---|
| Accepted plan | `docs/reviews/mvp-provider-runtime-budget-calibration-plan-20260603.md` |
| Plan controller judgment | `docs/reviews/mvp-provider-runtime-budget-calibration-plan-controller-judgment-20260603.md` |
| Evidence slice artifact | `docs/reviews/mvp-provider-runtime-budget-calibration-evidence-slice-20260603.md` |
| Retained same-source summary | `reports/llm-runs/006597-2024-20260602T121553Z-host_run_1f8d428509c5431/summary.json` |

## Next Entry Point

Resume `MVP provider runtime budget calibration evidence slice` only after provider config is restored in the active shell.

Required next-slice guardrails:

- Run presence-only config check first; never print secret values.
- Re-run retained read-only matrix before live evidence.
- Run only the default live provider command unless controller explicitly authorizes a bounded higher-timeout diagnostic.
- If live evidence produces a new retained artifact, record the safe runtime matrix and secret scan before any review.
- If Ch2/Ch4/Ch6 shift away from runtime timeout into prompt contract, audit-rule, fact-gap or code-bug blockers, stop runtime-budget tuning and route to the relevant calibration gate.
- Any provider budget/default/runtime behavior change still requires a separate heavy implementation gate with plan/review/controller judgment.

## Validation

- `git diff --check -- docs/reviews/mvp-provider-runtime-budget-calibration-evidence-slice-20260603.md` — pass.
- `python -m json.tool reports/llm-runs/006597-2024-20260602T121553Z-host_run_1f8d428509c5431/summary.json` — pass.
- Controller `rg` check confirmed retained matrix rows and missing config blocker text in the evidence artifact.

## Secret Safety

This judgment contains no API key, Authorization header, Bearer token, cookie, password, provider base URL value, model value, raw provider response, raw audit response, prompt body, writer draft body, repair draft body, markdown report body, raw PDF text, or raw parsed annual-report text.
