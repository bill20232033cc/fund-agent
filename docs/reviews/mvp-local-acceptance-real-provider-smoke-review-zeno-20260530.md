# MVP local acceptance / real provider smoke review - Zeno

Role: independent Gateflow review worker
Scope: read-only acceptance risk review
Result: blocking environment residual; no runtime finding

## Findings

### Medium - real provider smoke evidence is blocked, not passed

Current durable gate evidence before this artifact did not include a real provider smoke pass. Local raw evidence records `blocked_by_missing_provider_config` because provider, model, base URL and key are not configured.

Risk: marking local acceptance complete would incorrectly treat a missing live provider run as proof that the PR works with a real provider.

Required controller handling: keep PR #21 draft/open and record the live provider smoke as blocked until provider configuration is supplied and the same single-fund smoke is rerun.

### Medium - blocked live smoke must be promoted into tracked evidence

The raw smoke directory under `reports/mvp-local-acceptance/20260530/` is local/untracked. A tracked review artifact must summarize the redacted outputs so the gate state is durable without committing secrets or raw provider traffic.

### Low - secret handling should stay explicit

Provider artifacts must record only provider type, model name if non-secret, base URL configured/not configured, key configured/not configured, exit code, output path, failure classification and redacted stderr summary. They must not record API key values, Authorization headers, raw request bodies, full prompts or raw provider response bodies.

## Open Questions

- If the user wants live provider acceptance in this PR, they must provide or enable the typed provider environment and authorize rerunning the single-fund smoke.
- If live provider smoke is allowed to remain residual, PR #21 should stay draft/open and not be marked ready based on this gate alone.

## Required Evidence

- `uv run ruff check .`: pass.
- `uv run pytest --cov=fund_agent --cov-report=term-missing --cov-fail-under=50 -q`: pass, `1106 passed`, coverage `91.76%`.
- Deterministic analyze smoke for `006597 / 2024`: exit `0`, chapters `0-7`, evidence anchors present.
- Missing-config `--use-llm`: exit `1`, empty stdout, config error, no deterministic fallback report.
- Live provider `--use-llm`: `blocked_by_missing_provider_config`.

## Controller Decision Recommendation

Do not declare full local acceptance pass. Classify this gate as `blocked_by_missing_provider_config`; do not push, mark ready, merge, release, promote golden fixtures, or enter Gate 5.

Self-check: review worker was read-only; no file edits, staging, commit, push, PR action, merge or release.
