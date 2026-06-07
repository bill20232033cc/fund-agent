# MVP Post-Config Live Smoke Evidence Disposition

## 1. Scope

- Phase: `MVP typed-template-to-agent report generation stabilization phase`
- Gate: `post-config live smoke evidence disposition / control sync gate`
- Classification: `heavy`
- User authorization: direct authorization in current conversation to run exactly one real LLM smoke after LLM reconfiguration
- Role: evidence disposition and control sync only

This gate does not authorize source code changes, provider/default/runtime/budget changes, retries, endpoint probes, fallback, Chapter calibration implementation, Agent runtime, multi-year runtime, score-loop, golden/readiness, PR, push or release.

## 2. Preflight

- Branch: `feat/mvp-llm-incomplete-run-artifacts`
- Dirty workspace existed before this gate and includes unrelated tracked/untracked files.
- The gate does not clean, stage, commit or rely on unrelated dirty files.

## 3. Authorized Procedure

The user explicitly authorized one real LLM run after reporting that LLM configuration was updated.

Executed procedure:

1. Secret-safe presence-only typed config readiness check using `load_llm_provider_config_from_env()`.
2. If readiness passed, exactly one unchanged-default live command:

```bash
uv run fund-analysis analyze 006597 --report-year 2024 --use-llm
```

No retry, fallback command, endpoint probe, DNS/socket/curl/PASS-only probe, env override, timeout/default change or code change was performed.

## 4. Evidence

Readiness result:

```text
FUND_AGENT_LLM_PROVIDER: present
FUND_AGENT_LLM_MODEL: present
FUND_AGENT_LLM_BASE_URL: present
FUND_AGENT_LLM_API_KEY_ENV_VAR: absent
effective_api_key_value: present
config_validation: pass
```

Live command result:

- exit code: `1`
- retained artifact: `reports/llm-runs/006597-2024-20260606T231450Z-host_run_435c8c7c2b8d4e2/manifest.json`
- Host run id: `host_run_435c8c7c2b8d4e29`
- Host elapsed: `379001` ms
- orchestration status: `blocked`
- final assembly status: `incomplete`
- redaction applied: `true`
- redaction count: `1`

Chapter matrix from `summary.json`:

| Chapter | Status | Stop reason | Category | Subcategory | Attempts | Accepted draft/conclusion |
|---|---|---|---|---|---:|---|
| 1 | `failed` | `repair_budget_exhausted` | `prompt_contract` | `code_bug_other` | 2 | `false` / `false` |
| 2 | `failed` | `repair_budget_exhausted` | `prompt_contract` | `l1_numerical_closure` | 2 | `false` / `false` |
| 3 | `failed` | `repair_budget_exhausted` | `prompt_contract` | `code_bug_other` | 2 | `false` / `false` |
| 4 | `blocked` | `repair_budget_exhausted` | `audit_parse` | null | 2 | `false` / `false` |
| 5 | `failed` | `repair_budget_exhausted` | `prompt_contract` | `code_bug_other` | 2 | `false` / `false` |
| 6 | `blocked` | `unknown_anchor` | `prompt_contract` | `unknown_anchor` | 2 | `false` / `false` |

Secret-safety scan:

- Scope: retained artifact directory.
- Pattern family: Authorization headers, bearer tokens, common secret-key prefixes, explicit LLM API-key assignments and direct API-key field assignments.
- Result: no matches.

## 5. Disposition

Decision: `PROVIDER_RUNTIME_RESIDUAL_CLOSED_FOR_CURRENT_ROUTING`.

Reasoning:

- The same production `--use-llm` path reached provider-backed writer/auditor behavior.
- The latest failure is no longer `ConnectError`, endpoint/path unavailability, timeout, or provider network ownership evidence.
- The blocker is now chapter content/contract/audit readiness: all body chapters lack accepted draft and accepted conclusion.
- Final assembly remains correctly fail-closed and no deterministic fallback occurred.

New active residual: `chapter_content_or_contract_blocked`.

Residual breakdown:

- Chapter 1: `prompt_contract` / `code_bug_other`; best first calibration slice because it is the first failed chapter.
- Chapter 2: `prompt_contract` / `l1_numerical_closure`; likely separate numerical-closure audit calibration.
- Chapter 4: `audit_parse`; separate auditor protocol/parse gate, not a provider runtime issue.
- Chapter 6: `prompt_contract` / `unknown_anchor`; likely anchor projection/conversion-helper or writer allowed-anchor contract issue.

## 6. Non-Claims

This disposition does not claim:

- accepted report;
- Real LLM smoke re-baseline acceptance;
- Chapter calibration acceptance;
- provider default/runtime/budget adequacy beyond this one evidence run;
- permanent provider health;
- root cause for each chapter failure;
- permission to modify code without a follow-up plan/review/controller gate.

## 7. Next Entry Point

Open a `Real LLM chapter acceptance calibration gate` as the next repo work item.

Recommended first slice:

1. Use the retained artifact above as the same-source evidence input.
2. Start with Chapter 1 `prompt_contract` / `code_bug_other`.
3. Keep Chapter 6 `unknown_anchor`, Chapter 2 `l1_numerical_closure`, and Chapter 4 `audit_parse` as separately routed subproblems unless the plan proves a shared root cause.
4. Preserve fail-closed behavior, no deterministic fallback, no provider/default/runtime/budget changes, and no raw prompt/provider/audit body exposure.

## 8. Verdict

`ACCEPTED_FOR_CONTROL_SYNC`

The provider/network residual is no longer the active blocker for current routing. The active blocker is chapter content/contract/audit acceptance.
