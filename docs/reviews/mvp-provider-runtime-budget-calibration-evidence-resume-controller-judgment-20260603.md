# MVP provider runtime budget calibration evidence resume controller judgment

## Controller Self-Check

- Role: phaseflow/gateflow controller.
- Gate: `MVP provider runtime budget calibration gate`.
- Slice: resumed evidence-only live provider slice after provider config restoration.
- Classification: heavy.
- Scope: judge live evidence result; no source/test/config/runtime/provider-budget/auditor/template/score/golden/readiness change.
- Inputs reviewed: accepted plan, prior blocker judgment, resumed evidence artifact, baseline retained `summary.json`, new retained `summary.json`, `docs/design.md`, `docs/implementation-control.md`, and `docs/current-startup-packet.md`.

## Judgment

**Evidence resume accepted.** Provider config was restored in the current shell, the default live provider evidence command ran, and fail-closed behavior was preserved. The evidence narrows the provider-runtime blocker from Ch2/Ch4/Ch6 to Ch2 only for the current default run.

Accepted findings:

- Baseline retained evidence from 2026-06-02T121553Z remains valid: Ch2/Ch4/Ch6 were small-prompt `auditor` timeouts under `60s x2`, while Ch3 was `prompt_contract`.
- Current shell provider config presence check passed without printing secret values.
- Default live command ran without higher timeout env vars, PASS-only probe, or split-audit probe.
- New retained artifact was produced at `reports/llm-runs/006597-2024-20260602T220325Z-host_run_c83e8c1adcc846a`.
- New retained artifact keeps fail-closed semantics: CLI exit `1`, no accepted full report, final assembly incomplete.
- New retained matrix:
  - Ch1 accepted.
  - Ch2 failed with `llm_timeout`, runtime operation `auditor`, approx prompt tokens `758`, budget `60s x2`.
  - Ch3 failed with `prompt_contract` / `code_bug_other`, `programmatic:C2`, `repair_budget_exhausted`.
  - Ch4 accepted.
  - Ch5 accepted.
  - Ch6 accepted.
- Secret scan over the new retained artifact had no matches.

Controller disposition:

- Provider runtime budget tuning may continue only for Ch2 small-prompt auditor timeout evidence.
- Ch4/Ch5/Ch6 are not current default-run provider-runtime blockers and must not be used to justify a broad budget/default change.
- Ch3 is not a provider-runtime issue in this run; it must route to a separate Ch3 contract/audit calibration gate.
- No provider default timeout change is authorized by this evidence.
- No score-loop, golden, quality gate, readiness, template truth, auditor relaxation, deterministic fallback, PASS-only production behavior, split-audit implementation, push or PR is authorized.

## Acceptance Evidence

| Purpose | Artifact |
|---|---|
| Accepted plan | `docs/reviews/mvp-provider-runtime-budget-calibration-plan-20260603.md` |
| Prior blocked evidence slice | `docs/reviews/mvp-provider-runtime-budget-calibration-evidence-slice-20260603.md` |
| Resumed evidence artifact | `docs/reviews/mvp-provider-runtime-budget-calibration-evidence-resume-20260603.md` |
| New retained summary | `reports/llm-runs/006597-2024-20260602T220325Z-host_run_c83e8c1adcc846a/summary.json` |

## Next Entry Point

Start `MVP Ch2 auditor timeout diagnostic design gate`.

Scope guard for the next gate:

- Design/review first.
- Decide whether a bounded higher auditor-timeout diagnostic is possible with existing explicit config, or whether a diagnostic-only operation-specific timeout override implementation plan is needed.
- Keep any implementation evidence-only and default-preserving unless a later heavy implementation gate explicitly accepts default changes.
- Do not modify current defaults from this evidence alone.
- Do not include Ch3; Ch3 belongs to a separate C2 contract/audit calibration gate.
- Do not start `chapter_generation_score` until provider runtime and Ch3 contract blockers have separate accepted dispositions.

## Validation

- Baseline `summary.json` `python -m json.tool` — pass.
- New `summary.json` `python -m json.tool` — pass.
- New `manifest.json` `python -m json.tool` — pass.
- New retained runtime matrix extracted with `jq`.
- Secret scan over new retained artifact — no matches.

## Secret Safety

This judgment contains no API key, Authorization header, Bearer token, cookie, password, provider base URL value, model value, raw provider response, raw audit response, prompt body, writer draft body, repair draft body, markdown report body, raw PDF text, or raw parsed annual-report text.
