# MVP local acceptance / real provider smoke rerun evidence

Gate: `MVP local acceptance / real provider smoke rerun with configured provider`
Controller status: blocked by `audit_block`
Branch: `codex/local-reconciliation`
PR: #21 draft/open, merge state `CLEAN`, CI `test` success

## Scope

This gate reran the local acceptance smoke after loading a real provider configuration in the same shell. It did not change runtime code, fixtures, golden answers, score, quality gate, Host/Agent/dayu, PR state, merge state or release state.

The current worktree already contained previous gate control/evidence changes and unrelated untracked artifacts. This gate used only `reports/mvp-local-acceptance/20260530-rerun/` for raw rerun outputs and the tracked review artifacts listed below.

## Provider Loading

The controller found no project-local `.env` carrying typed `FUND_AGENT_LLM_*` config. A worker loaded a local secret file in the same shell and explicitly exported typed MVP provider variables for the smoke run:

- provider: `openai_compatible`
- model: `deepseek-chat`
- base URL configured: `true`
- API key configured: `true`
- API key environment variable name: `DEEPSEEK_API_KEY`

The artifact does not record the key value, Authorization header, full environment or full provider response.

## Required Validation

| Check | Result |
|---|---|
| `uv run ruff check .` | pass |
| `uv run pytest --cov=fund_agent --cov-report=term-missing --cov-fail-under=50 -q` | pass, `1106 passed`, coverage `91.76%` |

## Deterministic Default Smoke

Command:

```bash
uv run fund-analysis analyze 006597 --report-year 2024
```

Raw evidence:

- `reports/mvp-local-acceptance/20260530-rerun/deterministic-analyze-006597-2024.stdout.md`
- `reports/mvp-local-acceptance/20260530-rerun/deterministic-analyze-006597-2024.stderr.txt`
- `reports/mvp-local-acceptance/20260530-rerun/deterministic-analyze-006597-2024.exitcode`
- `reports/mvp-local-acceptance/20260530-rerun/deterministic-analyze-006597-2024.check.json`

Result:

- exit code: `0`
- chapters `0-7`: present
- evidence anchors: `16`

Disposition: default deterministic path remains runnable.

## Missing Config Fail-Closed Smoke

Command:

```bash
env -u FUND_AGENT_LLM_PROVIDER \
    -u FUND_AGENT_LLM_MODEL \
    -u FUND_AGENT_LLM_BASE_URL \
    -u FUND_AGENT_LLM_API_KEY_ENV_VAR \
    -u FUND_AGENT_LLM_API_KEY \
    uv run fund-analysis analyze 006597 --report-year 2024 --use-llm
```

Raw evidence:

- `reports/mvp-local-acceptance/20260530-rerun/missing-config-use-llm-006597-2024.stdout.md`
- `reports/mvp-local-acceptance/20260530-rerun/missing-config-use-llm-006597-2024.stderr.txt`
- `reports/mvp-local-acceptance/20260530-rerun/missing-config-use-llm-006597-2024.exitcode`
- `reports/mvp-local-acceptance/20260530-rerun/missing-config-use-llm-006597-2024.check.json`

Result:

- exit code: `1`
- stdout empty: `true`
- config error observed: `true`
- deterministic fallback report emitted: `false`

Disposition: missing config still fails closed.

## Real Provider Smoke

Command shape:

```bash
source local key env
export typed FUND_AGENT_LLM_* values
uv run fund-analysis analyze 006597 --report-year 2024 --use-llm
```

Raw evidence:

- `reports/mvp-local-acceptance/20260530-rerun/real-provider-use-llm-006597-2024.stdout`
- `reports/mvp-local-acceptance/20260530-rerun/real-provider-use-llm-006597-2024.stderr`
- `reports/mvp-local-acceptance/20260530-rerun/real-provider-use-llm-006597-2024.exitcode`
- `reports/mvp-local-acceptance/20260530-rerun/real-provider-use-llm-006597-2024.config-check.txt`
- `reports/mvp-local-acceptance/20260530-rerun/real-provider-use-llm-006597-2024.check.json`

Result:

- exit code: `1`
- provider config present: `true`
- stdout empty: `true`
- chapters `0-7`: not generated
- evidence anchors: `0`
- chapter audit/acceptance blockage observed: `true`
- deterministic fallback observed: `false`
- classification: `audit_block`

Redacted stderr summary:

```text
LLM 分析未完成：orchestration_status=blocked, final_assembly_status=incomplete, issues=orchestration_not_accepted, chapter_not_accepted, missing_accepted_draft, missing_accepted_conclusion, ...
```

## Secret Handling

Validation artifacts and raw rerun outputs were scanned for common secret value shapes. No API key value, Bearer token, Authorization header, full environment or full provider response was found in the rerun evidence.

## Evidence Conclusion

The real provider smoke reached the LLM path with provider configuration present, then failed closed because chapter orchestration/audit did not accept the generated chapter drafts. This is an `audit_block`, not `provider_config`, `provider_runtime`, `fact_gap` or `code_bug` based on current evidence.
