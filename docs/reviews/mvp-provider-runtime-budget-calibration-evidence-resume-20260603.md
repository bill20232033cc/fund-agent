# MVP provider runtime budget calibration evidence resume

## Scope

- Role: controller-run evidence continuation under accepted plan.
- Gate: `MVP provider runtime budget calibration gate`.
- Classification: heavy.
- Scope observed: evidence-only. No source, tests, config, runtime behavior, provider timeout defaults, auditor rules, template truth, quality/golden/readiness, score-loop, PR state, staging, commit, push, or PR were changed.

## Baseline Retained Matrix

Baseline retained run:

`reports/llm-runs/006597-2024-20260602T121553Z-host_run_1f8d428509c5431`

Read-only checks:

- `python -m json.tool .../summary.json` — pass.
- Retained runtime matrix:

```text
1	accepted	none
2	failed	llm_timeout	llm_timeout	auditor	743	60.0	2	60035
3	failed	repair_budget_exhausted	prompt_contract
4	failed	llm_timeout	llm_timeout	auditor	584	60.0	2	60036
5	accepted	none
6	failed	llm_timeout	llm_timeout	auditor	731	60.0	2	60032
```

This preserves the accepted plan baseline: Ch2/Ch4/Ch6 were small-prompt `auditor` timeouts; Ch3 was separate `prompt_contract`.

## Provider Config Readiness

Presence-only check was run without printing secret values.

Result:

```text
required_env_presence
FUND_AGENT_LLM_PROVIDER: present
FUND_AGENT_LLM_MODEL: present
FUND_AGENT_LLM_BASE_URL: present
FUND_AGENT_LLM_API_KEY_ENV_VAR: absent
effective_api_key_value: present
config_validation: pass
```

Disposition: previous provider-config blocker no longer applies in the current shell. Live evidence under the accepted default command was allowed.

## Default Live Evidence Command

Command:

```bash
uv run fund-analysis analyze 006597 --report-year 2024 --use-llm --llm-progress
```

Result:

- Exit code: `1`.
- stdout report: empty / no accepted complete report.
- Fail-closed behavior: preserved.
- No higher timeout env var was set.
- No PASS-only probe was run.
- No split-audit probe was run.
- New retained artifact:

`reports/llm-runs/006597-2024-20260602T220325Z-host_run_c83e8c1adcc846a`

CLI safe summary reported first failed chapter:

- `first_failed_chapter_id=2`
- `first_failed_stop_reason=llm_timeout`
- `first_failed_category=llm_timeout`
- `first_failed_runtime_operation=auditor`
- `first_failed_provider_attempts=2/2`
- `first_failed_provider_runtime_category=timeout`
- `first_failed_approx_prompt_tokens=758`
- `first_failed_timeout_root_cause_hint=small_prompt_provider_timeout`

## New Retained Artifact Checks

New retained run:

`reports/llm-runs/006597-2024-20260602T220325Z-host_run_c83e8c1adcc846a`

Validation:

- `python -m json.tool .../summary.json` — pass.
- `python -m json.tool .../manifest.json` — pass.
- Secret scan:

```bash
rg -n "Authorization|Bearer |FUND_AGENT_LLM_API_KEY|api_key|sk-|raw_response|provider response|draft_markdown|system_prompt[^_]|user_prompt[^_]" reports/llm-runs/006597-2024-20260602T220325Z-host_run_c83e8c1adcc846a
```

Result: no matches.

Runtime matrix:

```text
1	accepted	none
2	failed	llm_timeout	llm_timeout	auditor	758	60.0	2	60040
3	failed	repair_budget_exhausted	prompt_contract
4	accepted	none
5	accepted	none
6	accepted	none
```

Chapter matrix from new `summary.json`:

| Chapter | Status | Stop reason | Failure category | Failure subcategory | Attempt count |
|---:|---|---|---|---|---:|
| 1 | accepted | `none` | n/a | n/a | 1 |
| 2 | failed | `llm_timeout` | `llm_timeout` | n/a | 1 |
| 3 | failed | `repair_budget_exhausted` | `prompt_contract` | `code_bug_other` | 2 |
| 4 | accepted | `none` | n/a | n/a | 1 |
| 5 | accepted | `none` | n/a | n/a | 2 |
| 6 | accepted | `none` | n/a | n/a | 1 |

First failed runtime diagnostic:

| Field | Value |
|---|---|
| chapter_id | `2` |
| runtime_operation | `auditor` |
| provider_runtime_categories | `timeout` |
| provider_attempt_count | `2` |
| provider_max_attempts | `2` |
| approx_prompt_tokens | `758` |
| timeout_seconds | `60.0` |
| timeout_budget_kind | `auditor` |
| timeout_root_cause_hint | `small_prompt_provider_timeout` |

Ch3 prompt-contract diagnostic:

- `failure_category=prompt_contract`
- `failure_subcategory=code_bug_other`
- `issue_id_prefix_counts={"programmatic:C2": 1}`
- `phase=programmatic_audit`
- `stop_reason=repair_budget_exhausted`

## Evidence Disposition

This run narrows the provider-runtime blocker:

- Ch2 remains a small-prompt `auditor` timeout under the default `60s x2` budget.
- Ch4, Ch5 and Ch6 are no longer current default-run runtime blockers in this evidence slice; they accepted.
- Ch3 remains a separate typed contract / programmatic C2 issue and must not be solved by provider runtime budget tuning.
- Final assembly remains fail-closed because Ch2 and Ch3 are not accepted.

Current supported hypotheses:

- H1 provider endpoint/runtime small-prompt auditor timeout remains supported for Ch2.
- H2 current auditor timeout budget too low remains unresolved and is now scoped to Ch2 evidence, not Ch2/Ch4/Ch6 as a group.
- H3 writer timeout is not supported for this run.
- H5 audit rules too strict is not supported for Ch2 because timeout occurs before audit result.
- Ch3 must route to Ch3-specific contract/audit calibration, not provider runtime tuning.

## Next Evidence Need

Before any implementation/default change, the next gate decision should be one of:

1. Run a bounded higher `auditor` timeout diagnostic for Ch2 only if the current code already supports an explicit auditor timeout override or if a separate diagnostic-only implementation gate first adds one.
2. If no operation-specific override exists, open a narrowly scoped implementation planning gate for evidence-only operation-specific timeout override plumbing, without changing defaults.
3. Route Ch3 to a separate Ch3 C2 contract/audit calibration gate after provider runtime evidence is recorded.

Do not proceed to default budget changes, score-loop, PASS-only probe, split-audit, or auditor relaxation from this evidence alone.

## Secret Safety

This artifact contains no API key, Authorization header, Bearer token, cookie, password, provider base URL value, model value, raw provider response, raw audit response, prompt body, writer draft body, repair draft body, markdown report body, raw PDF text, or raw parsed annual-report text.
