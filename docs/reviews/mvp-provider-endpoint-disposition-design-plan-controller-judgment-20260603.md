# MVP provider endpoint disposition design/evidence plan controller judgment

- Role: controller
- Gate: `MVP provider endpoint disposition design/evidence gate`
- Classification: heavy
- Date: 2026-06-03
- Verdict: accepted as design/evidence plan

## Inputs

- Plan: `docs/reviews/mvp-provider-endpoint-disposition-design-plan-20260603.md`
- Independent reviews:
  - `docs/reviews/mvp-provider-endpoint-disposition-design-plan-review-ds-20260603.md`
  - `docs/reviews/mvp-provider-endpoint-disposition-design-plan-review-mimo-20260603.md`
- Truth sources:
  - `AGENTS.md`
  - `docs/design.md`
  - `docs/implementation-control.md`
  - `docs/current-startup-packet.md`
- Historical retained artifacts:
  - `reports/llm-runs/006597-2024-20260602T220325Z-host_run_c83e8c1adcc846a`
  - `reports/llm-runs/006597-2024-20260602T224137Z-host_run_4b7dddc60d084e7`

## Judgment

The plan is accepted. Both independent reviewers returned PASS with no blocking findings. The plan correctly treats old retained artifacts as pre-repair schema: they remain useful historical evidence for volatility and prompt/runtime-cost hypotheses, but cannot prove post-repair terminal lineage consistency.

The accepted next gate is `MVP post-repair provider endpoint disposition evidence slice`, heavy and evidence-only.

## Controller Answers To Open Questions

1. The next evidence gate is authorized to run exactly one default-budget live command after presence-only provider config readiness passes. No additional reviewer plan is required before that one live call because the current plan and two independent reviews provide sufficient gate-level review coverage.
2. If the post-repair default run fully accepts and produces no incomplete retained artifact, the evidence gate must stop after recording the complete-acceptance outcome. It must not automatically run PASS-only timing in the same gate.
3. A provider endpoint/config/default disposition must not be made from one default run alone. Minimum future threshold is either two post-repair default runs showing broad endpoint-level runtime failure, or one post-repair default run plus a separately accepted PASS-only timing probe showing endpoint-level latency. Any endpoint/config/default change still requires a separate heavy implementation/config gate.

## Accepted Next Evidence Scope

Allowed in the next gate:

- Run presence-only provider config readiness without printing provider values, model values, API key values, headers or endpoint paths.
- If readiness passes, run exactly:

```bash
uv run fund-analysis analyze 006597 --report-year 2024 --use-llm --llm-progress
```

- Use default provider runtime budgets. Do not set `FUND_AGENT_LLM_TIMEOUT_SECONDS`, writer/auditor/repair timeout overrides, timeout attempt overrides, provider endpoint overrides, model changes or API key changes between readiness and live run.
- Stop after one live command. Do not rerun after seeing failure details.
- Validate any retained artifact with `python -m json.tool` for `summary.json` and `manifest.json`.
- Run the accepted secret scan and report only safe matches, if any.
- Extract only safe scalar fields. Aggregate prompt-cost anchor/fact rows into counts and character-size totals; do not paste full anchor IDs, fact IDs, raw prompts, drafts, provider responses, audit responses, report bodies, provider values, model values or secrets.

If the run completes successfully with no retained incomplete artifact, the evidence artifact must record at least exit code, stdout byte count, whether stderr contained only safe progress/phase diagnostics, and the fact that no incomplete artifact is expected for an accepted result. It must not paste the final report body.

## Finding Disposition

| Finding | Disposition |
|---|---|
| DS NB-1: readiness error mapping assumes single-field config errors | Accepted as low-risk assumption for the next evidence slice. If config validation fails with ambiguous mapping, record `invalid typed config` and stop. |
| DS NB-2: operation-specific vs endpoint-wide boundary can be fuzzy | Accepted residual interpretation risk. One chapter timeout cannot justify endpoint/config disposition. |
| DS NB-3 / MiMo R2: prompt-cost diagnostics may contain full anchor/fact IDs | Accepted as evidence extraction constraint. Human evidence must aggregate IDs into counts/sizes unless a later security review accepts full IDs. |
| DS NB-4: do not over-interpret terminal lineage fields before live proof | Accepted. Next gate must first verify post-repair fields under real provider behavior. |
| MiMo R1: complete acceptance needs minimum capture fields | Accepted. Minimum capture fields are listed above; no report body may be pasted. |

## Guardrails

- No source code, tests, provider config, provider endpoint, runtime default, prompt contract, auditor rule, CHAPTER_CONTRACT, score-loop, quality gate, golden/readiness, final assembly, deterministic analyze/checklist behavior, PR/release state or fail-closed behavior is changed by this judgment.
- Incomplete `--use-llm` results must remain fail-closed with empty stdout and no deterministic fallback.
- Ch3 `programmatic:C2` remains a separate calibration gate.
- PASS-only timing, split-audit, timeout default change and provider endpoint/config change remain future gates and are not authorized by this judgment.

## Accepted Checkpoint

Accepted once this controller judgment, the plan, both plan reviews, and the control/startup sync are committed locally.
