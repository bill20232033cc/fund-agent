# MVP local acceptance / real provider smoke controller judgment

Gate: `MVP local acceptance / real provider smoke gate`
Role: Gateflow controller
Date: 2026-05-30
Decision: `blocked_by_missing_provider_config`

## Startup / Scope

Required preflight was run before discussion or edits:

- `git branch --show-current`: `codex/local-reconciliation`
- `git status --short`: no tracked dirty; unrelated untracked artifacts existed before this gate.

Allowed scope was local acceptance, smoke, issue classification and minimal fix only if a smoke-blocking local bug appeared. This gate did not enter Gate 5, golden/fixture promotion, release readiness, push, PR status change, merge or release.

## Agent Routing

- Planning worker produced the acceptance validation matrix and stop conditions.
- Smoke worker executed deterministic and missing-config smoke, collected redacted provider state and classified the live provider smoke.
- Review worker performed independent acceptance risk review and recommended blocking rather than treating missing provider config as a pass.

## Validation Results

| Item | Result |
|---|---|
| `uv run ruff check .` | pass |
| `uv run pytest --cov=fund_agent --cov-report=term-missing --cov-fail-under=50 -q` | pass, `1106 passed`, coverage `91.76%` |
| default `fund-analysis analyze 006597 --report-year 2024` | pass, exit `0`, chapters `0-7`, evidence anchors present |
| missing-config `fund-analysis analyze 006597 --report-year 2024 --use-llm` | expected fail-closed, exit `1`, empty stdout, no deterministic fallback report |
| real provider `fund-analysis analyze 006597 --report-year 2024 --use-llm` | not run; `blocked_by_missing_provider_config` |

## Controller Decision

This gate is not a full local acceptance pass. The default deterministic path and missing-config fail-closed behavior are locally validated, but the required real provider smoke cannot run because typed provider configuration is absent:

- provider not configured;
- model not configured;
- base URL not configured;
- API key not configured.

The correct disposition is `blocked_by_missing_provider_config`. This is not a code bug based on current evidence, and there is no accepted minimal runtime fix to make in this gate.

## PR Disposition

PR #21 should remain draft/open and must not be marked ready for review or release on the basis of this gate. The next smallest entry point is to supply the typed real provider configuration and rerun the single-fund smoke for `006597 / 2024`.

## Boundaries Preserved

- No runtime code changed.
- No deterministic `analyze` / `checklist` behavior changed.
- No provider failure was converted into deterministic fallback.
- No golden fixture, golden answer, manifest, score, snapshot, quality gate, FQ0-FQ6, schema or final judgment semantics changed.
- No Host/Agent/dayu package or dependency was introduced.
- No push, PR status change, merge, release or promotion was performed.

## Accepted Artifacts

- Plan: `docs/reviews/mvp-local-acceptance-real-provider-smoke-plan-20260530.md`
- Evidence: `docs/reviews/mvp-local-acceptance-real-provider-smoke-evidence-20260530.md`
- Independent review: `docs/reviews/mvp-local-acceptance-real-provider-smoke-review-zeno-20260530.md`
- Controller judgment: `docs/reviews/mvp-local-acceptance-real-provider-smoke-controller-judgment-20260530.md`
- Raw local smoke outputs: `reports/mvp-local-acceptance/20260530/`

## Next Entry Point

`MVP local acceptance / real provider smoke rerun gate with configured provider`

Minimum required typed environment:

- `FUND_AGENT_LLM_PROVIDER`
- `FUND_AGENT_LLM_MODEL`
- `FUND_AGENT_LLM_BASE_URL`
- `FUND_AGENT_LLM_API_KEY` or `FUND_AGENT_LLM_API_KEY_ENV_VAR` pointing at a configured key variable

Self-check: controller role only; specialist work was delegated; blocked condition is environment/config, not a runtime fix; no external state changed.
