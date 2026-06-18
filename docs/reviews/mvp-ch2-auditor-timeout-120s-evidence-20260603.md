# MVP Ch2 auditor timeout 120s evidence slice

## Scope And Guardrails

- Gate: `MVP Ch2 auditor timeout 120s evidence slice`.
- Parent gate: `MVP Ch2 auditor timeout diagnostic design gate`.
- Role: controller evidence collection only.
- Command intent: run the accepted auditor-only `120s` diagnostic without code, default, auditor, template, score, quality, golden, readiness or provider runtime implementation changes.
- Actions not taken: no source/test/config/default/runtime behavior edits; no PASS-only probe; no split-audit probe; no Ch3 calibration implementation; no deterministic fallback; no report body copied into this artifact.

## Baseline Evidence

Baseline retained artifact:

`reports/llm-runs/006597-2024-20260602T220325Z-host_run_c83e8c1adcc846a`

Validation:

- `python -m json.tool .../summary.json` passed.
- `python -m json.tool .../manifest.json` passed.
- Existing auditor-only config support was verified with `rg` over `fund_agent/config`, `fund_agent/services`, tests and README paths.

Baseline chapter matrix:

| Chapter | Status | Stop reason | Category | Subcategory |
|---:|---|---|---|---|
| 1 | accepted | none | | |
| 2 | failed | llm_timeout | llm_timeout | |
| 3 | failed | repair_budget_exhausted | prompt_contract | code_bug_other |
| 4 | accepted | none | | |
| 5 | accepted | none | | |
| 6 | accepted | none | | |

Baseline first failed:

- chapter: `2`
- operation: `auditor`
- provider attempts: `2/2`
- timeout: `60.0s`
- timeout budget kind: `auditor`
- approx prompt tokens: `758`
- root-cause hint: `small_prompt_provider_timeout`

## Live Diagnostic Command

Executed command:

```bash
FUND_AGENT_LLM_AUDITOR_TIMEOUT_SECONDS=120 \
uv run fund-analysis analyze 006597 --report-year 2024 --use-llm --llm-progress
```

Observed terminal-safe outcome:

- exit code: `1`
- stdout bytes: `0`
- stderr bytes: `8734`
- host timeout shown by safe progress: `2880s`
- terminal event: `run_failed`
- elapsed: `1102644ms`
- retained artifact: `reports/llm-runs/006597-2024-20260602T224137Z-host_run_4b7dddc60d084e7`
- retained manifest: `reports/llm-runs/006597-2024-20260602T224137Z-host_run_4b7dddc60d084e7/manifest.json`

The command preserved fail-closed behavior: stdout remained empty, the CLI exited `1`, and no deterministic report fallback was emitted.

## New Artifact Validation

New retained artifact:

`reports/llm-runs/006597-2024-20260602T224137Z-host_run_4b7dddc60d084e7`

Validation:

- `python -m json.tool .../summary.json` passed.
- `python -m json.tool .../manifest.json` passed.
- Secret scan command returned no matches:

```bash
rg -n "Authorization|Bearer |FUND_AGENT_LLM_API_KEY|api_key|sk-|raw_response|provider response|draft_markdown|system_prompt[^_]|user_prompt[^_]" \
  reports/llm-runs/006597-2024-20260602T224137Z-host_run_4b7dddc60d084e7
```

Artifact manifest summary:

- `schema_version`: `llm_incomplete_run_artifact_manifest.v1`
- `run_id`: `host_run_4b7dddc60d084e7b`
- `orchestration_status`: `blocked`
- `final_assembly_status`: `incomplete`
- `redaction_applied`: `false`
- `redaction_count`: `0`

## New Chapter Matrix

| Chapter | Status | Stop reason | Category | Subcategory | Attempts | Accepted draft | Accepted conclusion |
|---:|---|---|---|---|---:|---|---|
| 1 | failed | repair_budget_exhausted | audit_rule_too_strict | | 2 | false | false |
| 2 | failed | llm_timeout | llm_timeout | | 1 | false | false |
| 3 | failed | repair_budget_exhausted | prompt_contract | code_bug_other | 2 | false | false |
| 4 | failed | repair_budget_exhausted | audit_rule_too_strict | | 2 | false | false |
| 5 | failed | llm_timeout | llm_timeout | | 0 | false | false |
| 6 | blocked | unknown_anchor | prompt_contract | unknown_anchor | 1 | false | false |

New first failed:

- chapter: `1`
- status: `failed`
- stop reason: `repair_budget_exhausted`
- category: `audit_rule_too_strict`
- runtime operation: `auditor`
- provider attempts: `0/unknown`

## Evidence Interpretation

This evidence does not support a default provider budget change.

Reasons:

- The diagnostic no longer presents Ch2 as the first failed chapter; the first failed chapter is now Ch1 with `audit_rule_too_strict`.
- Ch2 still has top-level `llm_timeout`, but its chapter artifact shows an auditor row with `finish_reason=stop`, `response_chars=22`, no timeout scalar fields, and a programmatic L1 repair decision before the chapter-level timeout issue. This is a diagnostic attribution gap that must be reconciled before further budget tuning.
- Ch5 has a clear writer timeout under the unchanged writer budget: `operation=writer`, `timeout_budget_kind=writer_initial`, `timeout_seconds=60.0`, `provider_attempt_index=1/2` and `2/2`, approx prompt tokens `2518`, root-cause hint `small_prompt_provider_timeout`.
- Ch1 and Ch4 fail under `audit_rule_too_strict`; Ch6 blocks on `unknown_anchor`. These are contract/audit/anchor acceptance problems, not evidence that a broader auditor timeout default would make the report acceptable.
- The previous default run accepted Ch1/Ch4/Ch5/Ch6, while this auditor-only override run failed or blocked all body chapters. This cross-run acceptance volatility must be treated as a design diagnostic issue, not as a reason to patch prompts or relax fail-closed rules ad hoc.

## Direct Conclusions

- The accepted `120s` auditor-only diagnostic was executed and produced a valid retained incomplete-run artifact.
- Fail-closed behavior was preserved: exit `1`, stdout empty, no deterministic fallback.
- The evidence is negative/inconclusive for Ch2 timeout budget tuning: it does not prove that raising auditor timeout is sufficient, and it exposes diagnostic attribution gaps and cross-chapter acceptance volatility.
- No provider budget/default/runtime behavior change is justified by this evidence.
- Ch3 remains a separate `prompt_contract` / `code_bug_other` / `programmatic:C2` issue, but it should not enter implementation until the broader runtime/audit/anchor evidence volatility is reconciled by design.

## Recommended Next Entry

Start `MVP LLM acceptance volatility and diagnostic evidence reconciliation design gate`.

That gate should design/review how to reconcile:

- Ch2 chapter-level timeout versus missing timeout scalar diagnostics in the same artifact.
- Ch1/Ch4 `audit_rule_too_strict` volatility between adjacent live runs.
- Ch5 writer timeout under unchanged writer budget.
- Ch6 `unknown_anchor` as a typed contract/anchor issue.
- Whether the next safe probe should be provider endpoint disposition, split-audit, PASS-only timing, bounded semantic audit-focus design, or typed diagnostic serialization repair.

No implementation should start until that design gate has plan/review/controller judgment and an accepted checkpoint.
