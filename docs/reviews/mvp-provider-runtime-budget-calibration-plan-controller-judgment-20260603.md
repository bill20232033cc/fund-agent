# MVP provider runtime budget calibration plan controller judgment

## Controller Self-Check

- Role: phaseflow/gateflow controller.
- Gate: `MVP provider runtime budget calibration gate`.
- Classification: heavy.
- Current step: plan review judgment only.
- Scope: accept or reject the design/plan artifact; no implementation, no live provider call, no source/test/config/runtime/provider-budget/auditor/template/score/golden/readiness change.
- Inputs reviewed: plan artifact, DS plan review, MiMo plan review, `AGENTS.md`, `docs/design.md`, `docs/implementation-control.md`, `docs/current-startup-packet.md`, and retained `summary.json` from `reports/llm-runs/006597-2024-20260602T121553Z-host_run_1f8d428509c5431`.

## Judgment

**Accepted as provider runtime budget calibration plan.** The plan has independent DS/MiMo review, both reviews are PASS with no blocking findings, and the plan preserves the current fail-closed runtime contract.

Accepted planning decisions:

- The latest same-source retained run on 2026-06-02 is the primary evidence for this gate.
- The 2026-06-02 retained run shows Ch2/Ch4/Ch6 terminal provider runtime failures at the `auditor` operation, not writer operation, with small auditor prompts and `60s x2` timeout budget.
- The 2026-05-31 writer-timeout evidence is historical context only. It must not be merged into the 2026-06-02 retained run root-cause claim.
- Provider runtime budget calibration must separate writer timeout, auditor timeout, prompt contract, audit-rule block, fact gap, code bug, and large-prompt hypotheses with same-source retained fields.
- A future evidence slice may run a bounded diagnostic matrix, but it must remain fail-closed and evidence-only until a separate implementation judgment accepts any runtime change.
- Candidate future diagnostics may include operation-specific timeout calibration, writer/auditor timing split, PASS-only auditor probe, split-audit design evaluation, and endpoint/runtime scalar diagnostics.
- PASS-only auditor output is diagnostic only and must never be accepted as production audit.
- Split-audit remains a future design option only and belongs naturally with Agent attempt ledger / ToolTrace ownership if evidence supports it.
- Current first-MVP provider construction and runtime ceilings remain Service-owned. Future Agent owns retry/budget spending/ToolTrace only after an Agent implementation gate accepts that migration.

Rejected or deferred for this plan gate:

- No provider timeout default change.
- No new provider budget env/config behavior.
- No code implementation or tests.
- No live provider call.
- No auditor relaxation, deterministic fallback, partial report stdout, score-loop, golden, quality gate, readiness, template truth, retained report mutation, push or PR.
- No Ch3 calibration implementation.

## Review Disposition

DS review: PASS with no blocking findings. DS verified the 2026-06-02 retained runtime matrix against `summary.json` and confirmed Ch2/Ch4/Ch6 are auditor timeout rows. DS noted non-blocking observations around future env-var names, future file path confirmation, Ch6 mixed evidence, and PASS-only probe sequencing.

MiMo review: PASS with no blocking findings. MiMo verified same-source evidence use and raised four non-blocking risks:

- Ch6 has mixed evidence and cannot be made accepted by budget calibration alone if prior C2/C1 blockers remain after timeout is removed.
- A first diagnostic comparison of `60s x2` versus `120s x2` may not identify the optimal lower timeout if the endpoint responds at an intermediate value.
- Future runs must keep `timeout_budget_kind` or equivalent operation identity reliable.
- Ch4 writer draft success should remain directly evidenced when claiming the terminal blocker is auditor timeout.

Controller disposition: all four MiMo risks are accepted as non-blocking residuals. They do not require plan repair because the plan already blocks default budget changes, treats Ch6 audit/contract calibration as separate residual, and makes future implementation slices conditional on evidence.

## Acceptance Evidence

| Purpose | Artifact |
|---|---|
| Provider runtime budget calibration plan | `docs/reviews/mvp-provider-runtime-budget-calibration-plan-20260603.md` |
| DS plan review | `docs/reviews/mvp-provider-runtime-budget-calibration-plan-review-ds-20260603.md` |
| MiMo plan review | `docs/reviews/mvp-provider-runtime-budget-calibration-plan-review-mimo-20260603.md` |
| Retained same-source LLM run | `reports/llm-runs/006597-2024-20260602T121553Z-host_run_1f8d428509c5431/summary.json` |

Retained same-source runtime matrix confirmed by controller:

| Chapter | Status | Stop reason | Failure category | Timeout operation | Approx tokens | Budget |
|---:|---|---|---|---|---:|---|
| 1 | accepted | `none` | n/a | n/a | n/a | n/a |
| 2 | failed | `llm_timeout` | `llm_timeout` | `auditor` | `743` | `60s x2` |
| 3 | failed | `repair_budget_exhausted` | `prompt_contract` | n/a | n/a | n/a |
| 4 | failed | `llm_timeout` | `llm_timeout` | `auditor` | `584` | `60s x2` |
| 5 | accepted | `none` | n/a | n/a | n/a | n/a |
| 6 | failed | `llm_timeout` | `llm_timeout` | `auditor` | `731` | `60s x2` |

## Next Entry Point

Start `MVP provider runtime budget calibration evidence slice`, evidence-only.

Minimum guardrails for the next slice:

- Re-run retained-artifact read-only checks before any live evidence.
- If provider env is missing, record blocker instead of guessing.
- If live provider evidence is authorized and run, it must preserve empty stdout on fail-closed incomplete results and write only safe retained/scalar diagnostics.
- If Ch2/Ch4/Ch6 shift away from timeout into prompt contract, audit-rule, fact-gap or code-bug blockers, stop runtime-budget tuning and route to the relevant calibration gate.
- If bounded higher timeout still times out on small prompts, classify provider endpoint/runtime residual and do not keep increasing budget.
- Any default budget change requires a separate heavy implementation gate with plan/review/controller judgment.

## Validation

- `git diff --check -- docs/reviews/mvp-provider-runtime-budget-calibration-plan-20260603.md` — pass.
- `git diff --check -- docs/reviews/mvp-provider-runtime-budget-calibration-plan-review-ds-20260603.md docs/reviews/mvp-provider-runtime-budget-calibration-plan-review-mimo-20260603.md` — pass.
- `python -m json.tool reports/llm-runs/006597-2024-20260602T121553Z-host_run_1f8d428509c5431/summary.json` — pass.
- Controller `jq` runtime matrix check confirmed Ch2/Ch4/Ch6 auditor timeout rows.

## Secret Safety

This judgment contains no API key, Authorization header, Bearer token, cookie, password, raw provider response, raw audit response, prompt body, writer draft body, repair draft body, hidden provider config value, raw PDF text, or raw parsed annual-report text.
