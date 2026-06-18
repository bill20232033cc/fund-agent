# MVP Ch2 auditor timeout diagnostic design plan controller judgment

## Controller Self-Check

- Role: phaseflow/gateflow controller.
- Gate: `MVP Ch2 auditor timeout diagnostic design gate`.
- Classification: heavy.
- Current step: plan review judgment only.
- Scope: accept or reject the diagnostic design/plan artifact; no source/test/config/runtime/provider-default/auditor/template/score/golden/readiness change.
- Inputs reviewed: design plan, DS plan review, MiMo plan review, resumed provider evidence controller judgment, new retained `summary.json`, `docs/design.md`, `docs/implementation-control.md`, and `docs/current-startup-packet.md`.

## Judgment

**Accepted as Ch2 auditor timeout diagnostic plan.** DS and MiMo both reviewed the plan and returned PASS with no blocking findings.

Accepted plan decisions:

- Current same-source evidence narrows the provider-runtime blocker to Ch2 auditor timeout only.
- Ch4/Ch5/Ch6 accepted in the resumed default provider run and must not be used to justify broad provider default changes.
- Ch3 remains separate: `prompt_contract` / `code_bug_other` with `programmatic:C2`; it must not be handled by provider-runtime budget tuning.
- Existing code/config already supports an explicit auditor-only timeout override through `FUND_AGENT_LLM_AUDITOR_TIMEOUT_SECONDS`.
- No implementation is required before the next evidence slice.
- The next evidence slice may run a bounded auditor-only diagnostic:

```bash
FUND_AGENT_LLM_AUDITOR_TIMEOUT_SECONDS=120 \
uv run fund-analysis analyze 006597 --report-year 2024 --use-llm --llm-progress
```

Constraints for that evidence slice:

- Do not set `FUND_AGENT_LLM_TIMEOUT_SECONDS`.
- Do not set `FUND_AGENT_LLM_WRITER_TIMEOUT_SECONDS`.
- Do not set `FUND_AGENT_LLM_REPAIR_TIMEOUT_SECONDS`.
- Do not change provider defaults or code.
- Do not run PASS-only probe or split-audit probe.
- Preserve fail-closed semantics and safe retained artifact handling.

## Review Disposition

DS review: PASS with no blocking findings. DS verified same-source evidence, existing auditor-only timeout support, command safety, ownership boundaries, stop conditions, interpretation matrix, artifact handling, and secret safety.

MiMo review: PASS with no blocking findings. MiMo accepted the plan and raised three low-severity non-blocking improvements:

- Quantify host timeout impact: auditor timeout `120s` makes derived host timeout approximately `2880s` versus default approximately `1440s`.
- Clarify repair timeout fallback: repair remains at writer/global fallback because `FUND_AGENT_LLM_REPAIR_TIMEOUT_SECONDS` is not set.
- Clarify `timeout_root_cause_hint`: if Ch2 accepts the hint may be absent; if it still times out at `120s`, the hint may remain or change.

Controller disposition: accepted as non-blocking residuals for the next evidence-slice handoff and judgment. They do not require plan repair because they do not alter the diagnostic command, safety envelope, ownership boundary or stop conditions.

## Acceptance Evidence

| Purpose | Artifact |
|---|---|
| Ch2 auditor timeout diagnostic plan | `docs/reviews/mvp-ch2-auditor-timeout-diagnostic-design-plan-20260603.md` |
| DS plan review | `docs/reviews/mvp-ch2-auditor-timeout-diagnostic-design-plan-review-ds-20260603.md` |
| MiMo plan review | `docs/reviews/mvp-ch2-auditor-timeout-diagnostic-design-plan-review-mimo-20260603.md` |
| Resumed provider evidence | `docs/reviews/mvp-provider-runtime-budget-calibration-evidence-resume-20260603.md` |
| New retained summary | `reports/llm-runs/006597-2024-20260602T220325Z-host_run_c83e8c1adcc846a/summary.json` |

## Next Entry Point

Start `MVP Ch2 auditor timeout 120s evidence slice`, evidence-only.

Minimum guardrails:

- Re-run current summary JSON validation and Ch2 first-failed matrix before live command.
- Run only the auditor-only override command above.
- If the run remains incomplete and creates a new retained artifact, validate `summary.json` / `manifest.json`, extract safe matrix fields, and run the secret scan before judgment.
- If Ch2 accepts but Ch3 remains blocked, route Ch3 to a separate contract/audit calibration gate.
- If Ch2 still times out at `120s x2`, do not keep increasing budget; controller must decide between provider endpoint disposition, PASS-only timing probe design, or split-audit design gate.
- If the full report accepts, do not infer default readiness; default change/release readiness still require separate heavy gates.

## Validation

- `git diff --check -- docs/reviews/mvp-ch2-auditor-timeout-diagnostic-design-plan-20260603.md` — pass.
- DS/MiMo plan reviews — pass, no blocking findings.

## Secret Safety

This judgment contains no API key, Authorization header, Bearer token, cookie, password, provider base URL value, model value, raw provider response, raw audit response, prompt body, writer draft body, repair draft body, markdown report body, raw PDF text, or raw parsed annual-report text.
