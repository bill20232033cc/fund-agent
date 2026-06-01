# MVP local acceptance / real provider smoke evidence

Gate: `MVP local acceptance / real provider smoke gate`
Controller status: evidence collected; live provider smoke blocked by missing provider configuration
Branch: `codex/local-reconciliation`
PR: #21 draft/open, base `main`, head `codex/local-reconciliation`

## Branch / Worktree

Initial gate preflight:

- `git branch --show-current`: `codex/local-reconciliation`
- `git status --short`: tracked clean; unrelated untracked files existed before this gate.

Current gate-created local raw evidence is under:

- `reports/mvp-local-acceptance/20260530/`

The raw report directory is untracked local evidence. This tracked artifact records only redacted summaries and paths.

## Static / Test Validation

| Check | Command | Result |
|---|---|---|
| Ruff | `uv run ruff check .` | pass, exit `0` |
| Full pytest | `uv run pytest --cov=fund_agent --cov-report=term-missing --cov-fail-under=50 -q` | pass, `1106 passed`, coverage `91.76%` |

No runtime code was changed after these validations. This gate added only documentation/control artifacts.

## Deterministic Analyze Smoke

Command:

```bash
uv run fund-analysis analyze 006597 --report-year 2024
```

Raw evidence:

- stdout: `reports/mvp-local-acceptance/20260530/deterministic-analyze-006597-2024.stdout.md`
- stderr: `reports/mvp-local-acceptance/20260530/deterministic-analyze-006597-2024.stderr.txt`
- exit code: `reports/mvp-local-acceptance/20260530/deterministic-analyze-006597-2024.exitcode`
- check JSON: `reports/mvp-local-acceptance/20260530/deterministic-analyze-006597-2024.check.json`

Result:

- exit code: `0`
- chapters `0-7`: present
- evidence anchors: `8`
- evidence appendix: present
- quality gate: `warn`, issues `6`
- classification: deterministic default path works; no LLM provider is required.

## Missing Config `--use-llm` Fail-Closed Smoke

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

- stdout: `reports/mvp-local-acceptance/20260530/missing-config-use-llm-006597-2024.stdout.md`
- stderr: `reports/mvp-local-acceptance/20260530/missing-config-use-llm-006597-2024.stderr.txt`
- exit code: `reports/mvp-local-acceptance/20260530/missing-config-use-llm-006597-2024.exitcode`
- check JSON: `reports/mvp-local-acceptance/20260530/missing-config-use-llm-006597-2024.check.json`

Result:

- exit code: `1`
- stdout empty: `true`
- stderr classification: `LLM provider 配置错误：missing FUND_AGENT_LLM_PROVIDER`
- deterministic fallback report emitted: `false`
- classification: expected fail-closed missing provider config.

## Real Provider Smoke

Command intended when provider env is complete:

```bash
uv run fund-analysis analyze 006597 --report-year 2024 --use-llm
```

Redacted provider status:

- provider: not configured
- model: not configured
- base URL configured: `false`
- API key configured: `false`
- status: `blocked_by_missing_provider_config`

Raw status:

- `reports/mvp-local-acceptance/20260530/provider-env-status.json`
- `reports/mvp-local-acceptance/20260530/live-use-llm-006597-2024.status.json`

The real provider smoke was not run because typed provider configuration was absent. This is an environment/config blocker, not evidence that the live provider path passed.

## Secret Handling

The smoke worker recorded only redacted provider state. It did not print API key values or base URL. The tracked artifact does not contain an API key, Authorization header, raw provider request body or raw provider response body.

## Worker Report

Smoke worker summary:

- `reports/mvp-local-acceptance/20260530/worker-smoke-report.md`

Key worker conclusion:

- deterministic smoke passed;
- missing-config `--use-llm` failed closed;
- live provider `--use-llm` is `blocked_by_missing_provider_config`.

## Evidence Conclusion

This gate cannot be accepted as full local acceptance because the required real provider smoke did not run. The safe classification is `blocked_by_missing_provider_config`.
