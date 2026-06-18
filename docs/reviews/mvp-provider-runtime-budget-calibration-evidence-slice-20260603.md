# MVP provider runtime budget calibration evidence slice

## Scope

- Role: evidence worker only, not controller.
- Gate: `MVP provider runtime budget calibration gate`.
- Classification: `heavy`.
- Accepted plan: `docs/reviews/mvp-provider-runtime-budget-calibration-plan-20260603.md`.
- Controller judgment: `docs/reviews/mvp-provider-runtime-budget-calibration-plan-controller-judgment-20260603.md`.
- Scope observed: evidence-only. No source, tests, config, runtime behavior, provider timeout defaults, auditor rules, template truth, quality/golden/readiness, score-loop, retained reports, PR state, staging, commit, push, or PR were changed.

## Required Inputs Read

| Input | Status |
|---|---|
| `AGENTS.md` | read |
| `docs/design.md` | read |
| `docs/implementation-control.md` | read |
| `docs/current-startup-packet.md` | read |
| `docs/reviews/mvp-provider-runtime-budget-calibration-plan-20260603.md` | read |
| `docs/reviews/mvp-provider-runtime-budget-calibration-plan-controller-judgment-20260603.md` | read |
| `reports/llm-runs/006597-2024-20260602T121553Z-host_run_1f8d428509c5431/summary.json` | read |

Branch observed: `feat/mvp-llm-incomplete-run-artifacts`.

## Retained Artifact Checks

Retained run:

`reports/llm-runs/006597-2024-20260602T121553Z-host_run_1f8d428509c5431`

### JSON Validation

Command:

```bash
python -m json.tool reports/llm-runs/006597-2024-20260602T121553Z-host_run_1f8d428509c5431/summary.json
```

Result: pass, exit code `0`.

### Runtime Matrix

Command:

```bash
jq -r '.runtime_diagnostics.chapter_runtime_matrix[] | [.chapter_id,.status,.stop_reason,.failure_category,([.runtime_diagnostics[]? | select(.provider_runtime_category=="timeout") | .operation] | unique | join("+")),([.runtime_diagnostics[]? | select(.provider_runtime_category=="timeout") | .approx_prompt_tokens] | max // ""),([.runtime_diagnostics[]? | select(.provider_runtime_category=="timeout") | .timeout_seconds] | max // ""),([.runtime_diagnostics[]? | select(.provider_runtime_category=="timeout") | .provider_max_attempts] | max // ""),([.runtime_diagnostics[]? | select(.provider_runtime_category=="timeout") | .elapsed_ms] | max // "")] | @tsv' reports/llm-runs/006597-2024-20260602T121553Z-host_run_1f8d428509c5431/summary.json
```

Exact output:

```text
1	accepted	none
2	failed	llm_timeout	llm_timeout	auditor	743	60.0	2	60035
3	failed	repair_budget_exhausted	prompt_contract
4	failed	llm_timeout	llm_timeout	auditor	584	60.0	2	60036
5	accepted	none
6	failed	llm_timeout	llm_timeout	auditor	731	60.0	2	60032
```

Retained evidence disposition:

| Chapter | Status | Stop reason | Failure category | Timeout operation | Approx tokens | Timeout seconds | Max attempts | Max elapsed ms |
|---:|---|---|---|---|---:|---:|---:|---:|
| 1 | accepted | `none` | n/a | n/a | n/a | n/a | n/a | n/a |
| 2 | failed | `llm_timeout` | `llm_timeout` | `auditor` | 743 | 60.0 | 2 | 60035 |
| 3 | failed | `repair_budget_exhausted` | `prompt_contract` | n/a | n/a | n/a | n/a | n/a |
| 4 | failed | `llm_timeout` | `llm_timeout` | `auditor` | 584 | 60.0 | 2 | 60036 |
| 5 | accepted | `none` | n/a | n/a | n/a | n/a | n/a | n/a |
| 6 | failed | `llm_timeout` | `llm_timeout` | `auditor` | 731 | 60.0 | 2 | 60032 |

Same-source retained evidence still supports the accepted plan's claim: Ch2/Ch4/Ch6 terminal retained blockers are small-prompt `auditor` runtime timeouts under `60s x2`; Ch3 remains a separate `prompt_contract` failure.

## Provider Env And Config Readiness

Presence-only check was run without printing secret values.

Command:

```bash
python -c 'import os; from fund_agent.config.llm import load_llm_provider_config_from_env, LLMProviderConfigError; required=("FUND_AGENT_LLM_PROVIDER","FUND_AGENT_LLM_MODEL","FUND_AGENT_LLM_BASE_URL"); print("required_env_presence"); [print(k + ": " + ("present" if os.environ.get(k, "").strip() else "absent")) for k in required]; custom=bool(os.environ.get("FUND_AGENT_LLM_API_KEY_ENV_VAR", "").strip()); api_var=os.environ.get("FUND_AGENT_LLM_API_KEY_ENV_VAR", "FUND_AGENT_LLM_API_KEY"); print("FUND_AGENT_LLM_API_KEY_ENV_VAR: " + ("present" if custom else "absent")); print("effective_api_key_value: " + ("present" if os.environ.get(api_var, "").strip() else "absent"));
try:
 load_llm_provider_config_from_env(); print("config_validation: pass")
except LLMProviderConfigError:
 print("config_validation: fail")'
```

Exact output:

```text
required_env_presence
FUND_AGENT_LLM_PROVIDER: absent
FUND_AGENT_LLM_MODEL: absent
FUND_AGENT_LLM_BASE_URL: absent
FUND_AGENT_LLM_API_KEY_ENV_VAR: absent
effective_api_key_value: absent
config_validation: fail
```

Disposition: live provider evidence is blocked by missing required provider configuration. Per slice stop condition, no root cause was inferred beyond config absence.

## Live Provider Evidence

Default live command authorized by the accepted plan:

```bash
uv run fund-analysis analyze 006597 --report-year 2024 --use-llm --llm-progress
```

Status: not run.

Reason: required provider env/config is absent, so the slice stop condition applies. No higher timeout env vars, PASS-only probes, or split-audit probes were run.

## New Artifact Handling

No new `reports/llm-runs/` artifact was produced because the live provider command was not run.

Therefore these conditional checks were not applicable:

- `python -m json.tool` on a new `summary.json`.
- New safe runtime matrix extraction.
- Secret-safety `rg` scan over a new report directory.
- Comparison of a new run against retained Ch2/Ch4/Ch6 evidence.

## Runtime-Budget Tuning Disposition

Runtime-budget tuning remains blocked for this evidence slice because provider config is absent. This artifact does not propose any implementation, timeout default change, auditor change, template change, quality/golden/readiness change, score-loop change, retained report mutation, or PR action.

Fail-closed semantics from retained evidence remain explicit:

- Retained CLI result was incomplete/partial, with no deterministic fallback accepted by this slice.
- Ch2/Ch4/Ch6 retained blockers did not shift in this slice because no live rerun was allowed after the provider config blocker.
- Ch3 remains separate from runtime-budget tuning based on retained evidence.

## Validation

| Command | Result |
|---|---|
| `python -m json.tool reports/llm-runs/006597-2024-20260602T121553Z-host_run_1f8d428509c5431/summary.json` | pass |
| retained `jq` runtime matrix extraction | pass |
| provider env/config presence check | config absent; blocker recorded |
| `git diff --check -- docs/reviews/mvp-provider-runtime-budget-calibration-evidence-slice-20260603.md` | pass |

## Secret Safety

This artifact contains no API key, Authorization header, Bearer token, cookie, password, provider base URL value, model value, raw provider response, raw audit response, prompt body, writer draft body, repair draft body, markdown report body, raw PDF text, or raw parsed annual-report text. It reports provider configuration only as presence or absence.
