# MVP Real LLM Smoke Re-baseline Gate Configured Evidence Controller Decision

## 1. Scope

- Role: controller decision for resumed evidence execution.
- Phase: `MVP typed-template-to-agent report generation stabilization phase`.
- Gate: `Gate 2 Real LLM smoke re-baseline gate`.
- Prior plan accepted checkpoint: `4fd5b5b`.
- Prior environment-blocked evidence: `docs/reviews/mvp-real-llm-smoke-rebaseline-gate-evidence-20260604.md`.
- Configured inconclusive evidence: `docs/reviews/mvp-real-llm-smoke-rebaseline-gate-configured-evidence-20260604.md`.

This decision only resolves how to continue evidence collection after the first configured smoke attempt was interrupted before the derived Host deadline. It does not accept the gate, does not change source/test/config/runtime behavior, and does not authorize provider default/runtime/budget changes, Agent runtime, multi-year runtime, score-loop, golden/readiness, PR/push/release or chapter acceptance calibration.

## 2. Direct Facts

- Required provider/model/base-url/API-key presence is now present in the current shell.
- Optional runtime env overrides were absent in the configured preflight.
- Local non-live safety validation passed with `306 passed`.
- The first configured live smoke ran the reviewed command `uv run fund-analysis analyze 006597 --report-year 2024 --use-llm`, but was operator-terminated after approximately `900s`.
- Current code derives default Host timeout as `(60 + 60 + 60) * 2 * 6 = 2160s`.
- Because the first configured live smoke was interrupted before the derived Host deadline, it is `INCONCLUSIVE_BLOCKED`; it cannot prove accepted smoke success, accepted fail-closed incomplete behavior, provider/content residual or Host/CLI timeout defect.

## 3. Decision

Authorize exactly one replacement live smoke attempt for the same reviewed command:

```bash
uv run fund-analysis analyze 006597 --report-year 2024 --use-llm
```

Replacement attempt constraints:

- First rerun secret-safe presence preflight and record only presence booleans and env var names.
- Do not print API key, base URL value, provider/model value, Authorization header, full env, raw prompt, draft, raw provider response, raw audit response or request headers.
- Do not add timeout, attempt, backoff, model, endpoint, provider, max-output, repair-budget, prompt/debug or chapter-only override.
- Do not run another fund, another year, deterministic fallback, provider readiness probe or PASS-only probe.
- Wait for natural command termination through the derived Host deadline. The external observation window is `2400s`, which is greater than the current derived Host timeout and allows process cleanup margin.
- If the process is still running after `2400s`, classify the result as `external_observation_timeout_after_derived_host_deadline`, terminate only the replacement smoke process tree, and do not treat the run as accepted.
- If the command exits naturally, classify strictly from direct evidence: exit code, stdout empty/full-report status, stderr safe summary, retained artifact path, orchestration/final assembly status and per-chapter matrix.
- Do not enter Chapter acceptance calibration until replacement smoke evidence is written, reviewed and judged.

## 4. Evidence Requirements

The evidence owner must append or create a follow-up evidence section with:

- Pre-replacement git branch/status/diff.
- Secret-safe preflight presence results.
- Replacement command start/end facts and exit code.
- Stdout/stderr safety summary.
- New retained artifact path if one is produced.
- New `reports/llm-runs/` directory check.
- Redaction scan over the updated evidence artifact and retained artifact summaries, if any.
- A1-A9 mapping for the replacement attempt.
- A final classification using only same-run direct evidence.

## 5. Stop Conditions

Stop without live smoke if required env/config presence is absent again.

Stop and classify blocker if running the replacement attempt would require:

- provider/default/runtime/budget change;
- secret/base URL/provider/model value disclosure;
- more than one replacement live command;
- unreviewed command override;
- deterministic fallback;
- direct PDF/cache/source-helper read;
- `extra_payload` business parameters;
- Dayu production runtime dependency;
- golden/readiness/score-loop/PR/push/release action.
