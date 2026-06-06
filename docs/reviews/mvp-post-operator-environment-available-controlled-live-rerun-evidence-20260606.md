# MVP Post-Operator Environment-Available Controlled Live Rerun Evidence

## 1. Scope

- Phase: `MVP typed-template-to-agent report generation stabilization phase`
- Gate: `post-operator environment-available controlled live rerun evidence gate`
- Classification: `heavy`
- Role: evidence capture after operator-provided provider/environment availability evidence; not implementation, endpoint diagnostic, provider default change, retry loop, fallback, Chapter calibration, Agent runtime, PR, push, or release
- Operator evidence date: `2026-06-06`

This evidence records one controlled repo live rerun after the operator stated that config/account, provider console, env inheritance, proxy/VPN/firewall, TLS/cert, DNS/egress and minimal provider check were available in the same machine, same shell and same network. The operator evidence is treated as an external availability assertion, not as direct proof that the repo's openai-compatible live path can complete.

## 2. Preflight

Branch:

```text
feat/mvp-llm-incomplete-run-artifacts
```

Pre-run process check:

```text
no matching fund-analysis analyze / uv run fund-analysis process found
```

`git status --short` before evidence collection included unrelated tracked `pyproject.toml` and multiple unrelated untracked files. Those files were not used as evidence, staged, cleaned, deleted, or modified by this gate.

## 3. E1 Presence-Only Readiness

Readiness check used `fund_agent.config.llm.load_llm_provider_config_from_env()` and printed only presence/coarse validation labels:

```text
FUND_AGENT_LLM_PROVIDER: present
FUND_AGENT_LLM_MODEL: present
FUND_AGENT_LLM_BASE_URL: present
FUND_AGENT_LLM_API_KEY_ENV_VAR: absent
effective_api_key_value: present
config_validation: pass
```

No HTTP call, endpoint probe, DNS/socket probe, account metadata query, PASS-only probe, provider call, retry, fallback, override, or default change was performed by E1.

## 4. E2 Single Controlled Live Rerun

Command:

```bash
uv run fund-analysis analyze 006597 --report-year 2024 --use-llm
```

Execution capture:

| Field | Value |
|---|---|
| command count | `1` |
| exit code | `1` |
| elapsed seconds | `71.813` |
| stdout capture | `reports/llm-runs/controlled-rerun-20260606T101500Z/stdout.txt` |
| stdout byte count | `0` |
| stderr capture | `reports/llm-runs/controlled-rerun-20260606T101500Z/stderr.txt` |
| stderr byte count | `1734` |
| retained artifact | `reports/llm-runs/006597-2024-20260606T142143Z-host_run_55732009db674b9/manifest.json` |
| retry command used | `no` |
| endpoint/DNS/socket/curl/PASS-only probe used | `no` |
| fallback used | `no` |
| provider/model/base-url/API-key/runtime-budget/default override used | `no` |

Safe stderr summary:

```text
LLM incomplete diagnostic artifacts: reports/llm-runs/006597-2024-20260606T142143Z-host_run_55732009db674b9/manifest.json
LLM 分析未完成：orchestration_status=blocked, final_assembly_status=incomplete, first_failed_chapter_id=1, first_failed_status=failed, first_failed_stop_reason=llm_network_error, first_failed_category=provider_runtime, first_failed_subcategory=unknown, first_failed_runtime_operation=writer, first_failed_provider_attempts=1/2, first_failed_provider_runtime_category=network, first_failed_timeout_root_cause_hint=non_timeout_provider_runtime, chapter_matrix=1:failed/llm_network_error/provider_runtime/unknown;2:failed/llm_network_error/provider_runtime/unknown;3:failed/llm_network_error/provider_runtime/unknown;4:failed/llm_network_error/provider_runtime/unknown;5:failed/llm_network_error/provider_runtime/unknown;6:failed/llm_network_error/provider_runtime/unknown; LLM Host run 未完成：status=failed; timeout_classification=none; cancel_reason=none; error_type=_LLMIncompleteHostRunError
```

The summary above is abbreviated to preserve safety and readability; the captured stderr file contains only safe CLI diagnostics and no prompt, draft, raw provider response, raw audit response, API key, Authorization header, model value, or base URL value.

## 5. Retained Artifact Inspection

Manifest:

| Field | Value |
|---|---|
| artifact_kind | `llm_incomplete_run_diagnostic` |
| schema_version | `llm_incomplete_run_artifact_manifest.v1` |
| fund_code | `006597` |
| report_year | `2024` |
| run_id | `host_run_55732009db674b9b` |
| orchestration_status | `blocked` |
| final_assembly_status | `incomplete` |
| chapter_count | `6` |
| redaction_policy | `llm_incomplete_artifact_redaction.v1` |
| redaction_applied | `false` |
| redaction_count | `0` |
| retention_policy | `manual_local_cleanup` |

Summary:

| Field | Value |
|---|---|
| schema_version | `llm_incomplete_run_summary.v1` |
| fund_code | `006597` |
| report_year | `2024` |
| run_id | `host_run_55732009db674b9b` |
| orchestration_status | `blocked` |
| final_assembly_status | `incomplete` |
| first_failed_chapter_id | `1` |
| first_failed_stop_reason | `llm_network_error` |
| first_failed_category | `provider_runtime` |

Chapter matrix:

| Chapter | Status | Stop reason | Category | Accepted draft | Accepted conclusion |
|---|---|---|---|---|---|
| 1 | `failed` | `llm_network_error` | `provider_runtime` | `false` | `false` |
| 2 | `failed` | `llm_network_error` | `provider_runtime` | `false` | `false` |
| 3 | `failed` | `llm_network_error` | `provider_runtime` | `false` | `false` |
| 4 | `failed` | `llm_network_error` | `provider_runtime` | `false` | `false` |
| 5 | `failed` | `llm_network_error` | `provider_runtime` | `false` | `false` |
| 6 | `failed` | `llm_network_error` | `provider_runtime` | `false` | `false` |

Runtime diagnostics summary:

| Field | Value |
|---|---|
| terminal operation | `writer` |
| terminal issue class | `ConnectError` |
| provider runtime category | `network` |
| provider attempt count | `1` |
| provider max attempts | `2` |
| timeout classification | `none` in Host summary |
| timeout root-cause hint | `non_timeout_provider_runtime` |
| max output chars | `12000` |

No body chapter reached accepted draft or accepted conclusion. The run did not produce an accepted report.

## 6. Redaction And Scope Scan

Artifact/capture scan found no API key value, Authorization header, bearer token, model value, base URL value, writer draft, raw provider response, or raw audit response. Matches for `prompt` / `raw_provider` are limited to diagnostic field names and the manifest redaction-policy category names, not raw payload content.

No source, test, config, README, template, design doc, quality gate, golden/readiness, Host/Agent, score-loop, PR, push, or release change was made by this evidence run.

## 7. Outcome Classification

Outcome: `provider_runtime_error_non_timeout`.

Direct evidence:

- Operator evidence asserted environment/provider availability from the operator side in the same machine, shell and network.
- Repo E1 typed config presence/readiness passed in the current shell.
- Exactly one unchanged-default live command ran after E1.
- The command exited `1` with stdout byte count `0`.
- Retained artifact exists at `reports/llm-runs/006597-2024-20260606T142143Z-host_run_55732009db674b9/`.
- `orchestration_status=blocked` and `final_assembly_status=incomplete`.
- Chapters 1-6 all failed before accepted draft/conclusion with writer `llm_network_error`, `provider_runtime`, runtime category `network`, terminal issue class `ConnectError`, and timeout root-cause hint `non_timeout_provider_runtime`.
- No fallback, retry, probe, provider/default/runtime-budget override, or deterministic report fallback was used.

Controller implication: this rerun does not unlock Chapter acceptance calibration, because no body chapter has accepted draft or accepted conclusion. It also does not prove a repo code/template/content/audit-rule root cause. It narrows the next action to provider runtime / endpoint-path / environment-owner diagnosis or a separately reviewed diagnostic gate; no further live retry is authorized by this evidence artifact.
