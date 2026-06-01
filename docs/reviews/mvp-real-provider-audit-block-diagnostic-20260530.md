# MVP real provider audit-block diagnostic

Gate: `MVP real provider audit-block diagnostic gate`
Date: 2026-05-30
Branch: `codex/local-reconciliation`
PR: #21 draft/open, merge state `CLEAN`, CI `test` success
Classification: `provider_config`

## Scope

This diagnostic explains why the prior real provider smoke surfaced as `audit_block`. The gate reran the real provider path and captured same-source Service objects with redacted fields. It did not change runtime code, fixtures, golden data, score, quality gate, snapshot, Host/Agent/dayu, PR state, merge state or release state.

## Minimal Reproduction

Command shape:

```bash
source local key env
export FUND_AGENT_LLM_PROVIDER=openai_compatible
export FUND_AGENT_LLM_MODEL=deepseek-chat
export FUND_AGENT_LLM_BASE_URL=https://api.deepseek.com/v1
export FUND_AGENT_LLM_API_KEY_ENV_VAR=DEEPSEEK_API_KEY
uv run fund-analysis analyze 006597 --report-year 2024 --use-llm
```

The artifact intentionally does not record the key value, Authorization header, full environment or full provider response.

## Direct Evidence

Raw diagnostic paths:

- CLI stdout: `reports/mvp-local-acceptance/20260530-diagnostic/cli.stdout`
- CLI stderr: `reports/mvp-local-acceptance/20260530-diagnostic/cli.stderr`
- CLI exit code: `reports/mvp-local-acceptance/20260530-diagnostic/cli.exitcode`
- Service summary: `reports/mvp-local-acceptance/20260530-diagnostic/diagnostic-summary.json`
- Worker report: `reports/mvp-local-acceptance/20260530-diagnostic/worker-diagnostic-report.md`

CLI symptom:

- exit code: `1`
- stdout: empty
- stderr summary: `orchestration_status=blocked`, `final_assembly_status=incomplete`, repeated `chapter_not_accepted`, `missing_accepted_draft`, `missing_accepted_conclusion`

Service same-source diagnostic:

- orchestrator status: `blocked`
- final assembly status: `incomplete`
- chapter 1 status: `failed`
- chapter 1 stop reason: `llm_exception`
- chapter 1 attempt count: `0`
- chapter 1 issue: `LLMProviderRuntimeError: LLM provider request failed: status_code=401`
- chapters 2-6: `skipped` / `dependency_missing` because fail-fast stopped after chapter 1 failed

The CLI message is therefore a final-assembly symptom. The first causal failure is provider authentication/configuration returning HTTP `401` before any chapter draft or audit result exists.

## Failure Classification

Classification: `provider_config`

Rationale:

- `provider_config`: supported by HTTP `401` at the first provider request.
- `audit_block`: rejected as root cause because there was no draft, no audit result, no audit issue and no repair decision.
- `fact_gap`: rejected because the failure occurred before draft generation and no fact/missing-facts issue was recorded.
- `code_bug`: rejected because no traceback, contract exception or deterministic-path regression was observed.
- `provider_runtime`: less likely than `provider_config` because the direct status is HTTP `401`, normally an authentication/permission/config issue rather than transient provider availability.
- `unknown`: not needed; same-source evidence identifies the first causal failure.

## Root Cause

The real provider request for chapter 1 failed with HTTP `401`. The likely root cause is one of:

- the local key value is invalid or expired;
- the account associated with the key is not authorized;
- the configured base URL is not valid for that key;
- the configured model `deepseek-chat` is not available to that key/account.

Because the gate must not record secrets or full provider response bodies, this artifact does not distinguish among those subcases.

## Minimal Next Entry

`MVP provider auth/config verification gate`

Minimum scope:

- verify the configured key against `https://api.deepseek.com/v1` and model `deepseek-chat` in a secret-safe shell;
- keep the current no-fallback behavior;
- do not change audit semantics or provider code until the key/base URL/model permission issue is resolved;
- rerun the same `006597 / 2024 --use-llm` smoke after provider authentication succeeds.

## Code Fix Assessment

No code fix is justified from current evidence. The CLI's high-level error is less specific than the Service diagnostic, but this gate's root cause is provider auth/config. A code fix should be considered only after a valid provider credential succeeds at the transport layer and the failure moves to actual draft/audit content.

## Validation Matrix

| Validation | Required before next acceptance attempt |
|---|---|
| Provider auth/config | A minimal chat-completions request succeeds with the same base URL, model and key env var, without logging secrets |
| CLI no-fallback | `fund-analysis analyze --use-llm` still exits non-zero and emits no deterministic report on provider failure |
| Real smoke | `fund-analysis analyze 006597 --report-year 2024 --use-llm` reaches draft/audit generation after provider auth succeeds |
| Secret hygiene | No API key, Authorization header, full environment or full provider response in artifacts |
| Regression | If runtime code changes later, rerun `uv run ruff check .` and full pytest |

## Review

Independent review confirmed:

- chapter 1 failed at writer/provider call with `llm_exception` and HTTP `401`;
- chapters 2-6 were dependency skips;
- no draft/audit evidence supports true `audit_block`;
- no secret leakage was observed in reviewed artifacts.

## PR Disposition

PR #21 remains draft/open. Do not mark ready, merge, release or promote based on this diagnostic.
