# MVP post-repair provider endpoint disposition evidence slice

- Role: controller evidence recorder
- Gate: `MVP post-repair provider endpoint disposition evidence slice`
- Classification: heavy, evidence-only
- Date: 2026-06-03
- Verdict: evidence collected; diagnostic adequacy appears PASS; endpoint/config/default disposition not supported by this single run

## Scope

This slice executed the accepted next evidence step from `docs/reviews/mvp-provider-endpoint-disposition-design-plan-controller-judgment-20260603.md`.

No source code, tests, provider endpoint, provider config, provider timeout defaults, prompt contract, auditor rule, CHAPTER_CONTRACT, score-loop, quality gate, golden/readiness, final assembly, deterministic analyze/checklist behavior, PR/release state or fail-closed behavior was changed.

## Presence-Only Readiness

Command shape: `uv run python -c ...` using `load_llm_provider_config_from_env()`.

Safe output:

```text
required_env_presence
FUND_AGENT_LLM_PROVIDER: present
FUND_AGENT_LLM_MODEL: present
FUND_AGENT_LLM_BASE_URL: present
FUND_AGENT_LLM_API_KEY_ENV_VAR: absent
effective_api_key_value: present
FUND_AGENT_LLM_TIMEOUT_SECONDS: absent
FUND_AGENT_LLM_WRITER_TIMEOUT_SECONDS: absent
FUND_AGENT_LLM_AUDITOR_TIMEOUT_SECONDS: absent
FUND_AGENT_LLM_REPAIR_TIMEOUT_SECONDS: absent
FUND_AGENT_LLM_TIMEOUT_MAX_ATTEMPTS: absent
config_validation: pass
```

No provider value, model value, API key value, Authorization header or endpoint path was printed.

## Live Command

Exactly one default-budget live command was run:

```bash
uv run fund-analysis analyze 006597 --report-year 2024 --use-llm --llm-progress
```

Output handling:

- stdout redirected to `/tmp/mvp-post-repair-provider-endpoint-evidence.stdout`
- stderr redirected to `/tmp/mvp-post-repair-provider-endpoint-evidence.stderr`
- no timeout override env was set
- no rerun was performed

Safe terminal facts:

| Field | Value |
|---|---|
| CLI exit | `1` |
| stdout bytes | `0` |
| stderr bytes | `6701` |
| safe stderr content | progress/status lines only plus incomplete safe summary |
| Host run id | `host_run_1d6bc6c2371d4b5a` |
| Host terminal event | `run_failed` |
| Host elapsed | `938713 ms` |

## Retained Artifact

Path:

```text
reports/llm-runs/006597-2024-20260603T024235Z-host_run_1d6bc6c2371d4b5
```

Validation:

| Check | Result |
|---|---|
| `python -m json.tool .../summary.json` | PASS |
| `python -m json.tool .../manifest.json` | PASS |
| secret/payload scan | PASS; no matches |

Secret scan command:

```bash
rg -n "Authorization|Bearer |FUND_AGENT_LLM_API_KEY|api_key|sk-|raw_response|provider response|draft_markdown|system_prompt[^_]|user_prompt[^_]" reports/llm-runs/006597-2024-20260603T024235Z-host_run_1d6bc6c2371d4b5
```

The scan exited `1`, meaning no matches.

Manifest scalar fields:

| Field | Value |
|---|---|
| `artifact_kind` | `llm_incomplete_run_diagnostic` |
| `schema_version` | `llm_incomplete_run_artifact_manifest.v1` |
| `fund_code` | `006597` |
| `report_year` | `2024` |
| `orchestration_status` | `partial` |
| `final_assembly_status` | `incomplete` |
| `redaction_applied` | `false` |
| `redaction_count` | `0` |
| `retention_policy` | `manual_local_cleanup` |

## Summary Scalar Fields

Root summary:

| Field | Value |
|---|---|
| `schema_version` | `llm_incomplete_run_summary.v1` |
| `fund_code` | `006597` |
| `report_year` | `2024` |
| `run_id` | `host_run_1d6bc6c2371d4b5a` |
| `orchestration_status` | `partial` |
| `final_assembly_status` | `incomplete` |
| `redaction_applied` | `false` |
| `redaction_count` | `0` |

Chapter matrix:

| Chapter | Status | Stop | Category | Attempts | Accepted draft | Accepted conclusion |
|---|---|---|---|---:|---|---|
| 1 | `accepted` | `none` | `null` | 1 | true | true |
| 2 | `accepted` | `none` | `null` | 1 | true | true |
| 3 | `failed` | `llm_timeout` | `llm_timeout` | 1 | false | false |
| 4 | `accepted` | `none` | `null` | 1 | true | true |
| 5 | `failed` | `llm_timeout` | `llm_timeout` | 1 | false | false |
| 6 | `failed` | `llm_timeout` | `llm_timeout` | 1 | false | false |

First failed chapter:

| Field | Value |
|---|---|
| `chapter_id` | 3 |
| `status` | `failed` |
| `stop_reason` | `llm_timeout` |
| `failure_category` | `llm_timeout` |
| `attempt_count` | 1 |

Runtime first failed:

| Field | Value |
|---|---|
| `chapter_id` | 3 |
| `status` | `failed` |
| `stop_reason` | `llm_timeout` |
| `category` | `llm_timeout` |
| `runtime_operation` | `auditor` |
| `provider_runtime_categories` | `timeout` |
| `provider_attempt_count` / `provider_max_attempts` | `2 / 2` |
| `repair_attempt_index` | 0 |
| `approx_prompt_tokens` | 880 |
| `system_prompt_chars` | 54 |
| `user_prompt_chars` | 3463 |
| `timeout_seconds` | 60.0 |
| `timeout_budget_kind` | `auditor` |
| `timeout_max_attempts` | 2 |
| `timeout_backoff_seconds` | 1.0 |
| `timeout_root_cause_hint` | `small_prompt_provider_timeout` |
| `diagnostic_consistency_status` | `consistent` |
| `terminal_runtime_diagnostic_present` | true |
| `terminal_stop_reason` | `llm_timeout` |
| `terminal_failure_category` | `llm_timeout` |
| `terminal_runtime_operation` | `auditor` |
| `terminal_repair_attempt_index` | 0 |
| `terminal_issue_class` | `ReadTimeout` |

Terminal consistency by chapter:

| Chapter | Status | Stop | Category | Consistency | Terminal runtime present | Terminal op | Terminal issue |
|---|---|---|---|---|---|---|---|
| 1 | `accepted` | `none` | `null` | `consistent` | false | `null` | `null` |
| 2 | `accepted` | `none` | `null` | `consistent` | false | `null` | `null` |
| 3 | `failed` | `llm_timeout` | `llm_timeout` | `consistent` | true | `auditor` | `ReadTimeout` |
| 4 | `accepted` | `none` | `null` | `consistent` | false | `null` | `null` |
| 5 | `failed` | `llm_timeout` | `llm_timeout` | `consistent` | true | `auditor` | `ReadTimeout` |
| 6 | `failed` | `llm_timeout` | `llm_timeout` | `consistent` | true | `auditor` | `ReadTimeout` |

Runtime diagnostic rows for failed chapters:

| Chapter | Operation | Provider attempts | Elapsed max | Timeout | Budget | Error class |
|---|---|---:|---:|---:|---|---|
| 3 | `auditor` | 2 | `60138 ms` | `60.0 s` | `auditor` | `ReadTimeout` |
| 5 | `auditor` | 2 | `60112 ms` | `60.0 s` | `auditor` | `ReadTimeout` |
| 6 | `auditor` | 2 | `60332 ms` | `60.0 s` | `auditor` | `ReadTimeout` |

Prompt-contract diagnostic rows:

- 6 chapter rows were present.
- No row carried marker, unknown-anchor, required-output, L1, finish-reason or response-char counters for this run.
- Failed chapters 3, 5 and 6 are represented as `llm_timeout`, not prompt-contract failures.

Final assembly issues:

- `orchestration_not_accepted`
- chapter 3, 5 and 6: `chapter_not_accepted`, `missing_accepted_draft`, `missing_accepted_conclusion`

## Classification

Diagnostic adequacy:

- PASS. This is the first post-repair live retained artifact in this gate line.
- Terminal consistency fields are present for all failed runtime chapters.
- `runtime_diagnostics.first_failed` matches the terminal chapter lineage.
- No timeout scalar was invented from a non-terminal audit row.
- Incomplete fail-closed semantics held: exit `1`, stdout `0`, no deterministic fallback and no partial report stdout.

Root-cause classification from same-source fields:

- Endpoint/config disposition is not supported by this single run.
- The run shows auditor-clustered timeout: chapters 3, 5 and 6 all failed in `runtime_operation=auditor` with `60s x2` timeout rows and `diagnostic_consistency_status=consistent`.
- It does not show a writer-clustered timeout in the retained terminal diagnostics.
- It does not prove endpoint-wide failure because chapters 1, 2 and 4 accepted in the same run.
- It does not prove a prompt-contract or anchor-contract blocker for this run; prompt-contract counters are empty for the failed chapters.
- It does not resolve Ch3 content/C2 calibration; Ch3 is now a runtime timeout in this run, not same-source `programmatic:C2`.

Accepted next-route recommendation:

1. Do not change provider endpoint/config/default/runtime behavior from this evidence.
2. Open a separate `MVP PASS-only provider timing probe design gate` to test whether minimal provider calls show endpoint-level latency without report content artifacts.
3. If PASS-only timing does not show endpoint-wide latency, open a split-audit / auditor-specific runtime probe design gate before any auditor timeout default change.

## Residuals

- This is one post-repair default-budget run. It is enough to prove diagnostic serialization under live provider behavior, but not enough to change endpoint/config/defaults.
- Runtime remains volatile across historical artifacts: previous default post-repair-unavailable evidence accepted different chapter sets, and this run accepted Ch1/Ch2/Ch4 while Ch3/Ch5/Ch6 timed out in auditor.
- Ch3 `programmatic:C2` remains unresolved historically, but this run's terminal Ch3 failure is `auditor` timeout.

## Acceptance Criteria Status

| Criterion | Status |
|---|---|
| Presence-only readiness recorded without secrets | PASS |
| Exactly one live command | PASS |
| No code/config/default/runtime changes | PASS |
| Retained artifact exists for incomplete result | PASS |
| JSON validation passed | PASS |
| Secret scan clean | PASS |
| Post-repair terminal consistency fields present for runtime failures | PASS |
| Incomplete run fail-closed with stdout empty | PASS |
| Root-cause classification uses retained scalar fields only | PASS |
| Disposition recommends next gate only | PASS |
