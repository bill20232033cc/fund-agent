# MVP local acceptance / real provider smoke gate plan

Gate: `MVP local acceptance / real provider smoke gate`
Role: planning worker output accepted by controller
Branch baseline: `codex/local-reconciliation`

## Goal

Validate that the PR #21 MVP `fund-analysis analyze --use-llm` path is locally acceptable beyond fake tests: deterministic default behavior remains unchanged, missing provider config fails closed, and a real provider smoke either passes or is explicitly blocked with reason.

## Scope

Allowed:

- Local validation commands, CLI smoke commands, redacted evidence artifacts and controller judgment.
- Minimal smoke-blocking fixes only if the failure is a code/config handling defect and does not cross the current gate boundary.

Non-goals:

- No Gate 5 `dayu.host` / `dayu.engine` / Host / Agent runtime.
- No golden, fixture promotion, release readiness, push, PR status change, merge or release.
- No change to default deterministic `fund-analysis analyze` or `fund-analysis checklist`.
- No schema, quality gate, final judgment, score, snapshot, golden fixture or promotion-state change.

## Validation Matrix

| Check | Command / evidence | Expected result |
|---|---|---|
| Ruff | `uv run ruff check .` | exit `0` |
| Full pytest | `uv run pytest --cov=fund_agent --cov-report=term-missing --cov-fail-under=50 -q` | exit `0`, coverage above `50` |
| Deterministic default | `uv run fund-analysis analyze 006597 --report-year 2024` | exit `0`, no LLM provider required, report has chapters `0-7` and evidence anchors |
| Missing config fail-closed | unset LLM env and run `uv run fund-analysis analyze 006597 --report-year 2024 --use-llm` | exit `1`, empty stdout, clear config error, no deterministic fallback report |
| Real provider smoke | run `uv run fund-analysis analyze 006597 --report-year 2024 --use-llm` only when typed provider env is complete | pass with real report, or classify as `blocked_by_missing_provider_config` / provider/config/fact/audit/code failure |
| Secret check | inspect evidence for key patterns | no API key, Authorization header, raw request body or full provider response committed |

## Stop Conditions

- Provider key/base URL/model is missing and real smoke cannot run.
- Any validation failure points to public contract, default deterministic behavior, quality gate, final judgment, schema or promotion semantics.
- Any artifact contains a secret value.
- Fix scope would enter retry/backoff, multi-provider framework, prompt rewrite, Gate 5 Host/Agent/dayu, Evidence Confirm, golden promotion or release readiness.

## Controller Decision Options

- `accepted`: all validations and real provider smoke pass.
- `blocked_by_missing_provider_config`: deterministic and fail-closed checks pass, but live smoke cannot run because typed provider env is absent.
- `rejected_needs_fix`: a local bug blocks deterministic, fail-closed, provider construction or no-fallback behavior.

Self-check: planning worker did not edit files, stage, commit, push, open PR, merge or release.
