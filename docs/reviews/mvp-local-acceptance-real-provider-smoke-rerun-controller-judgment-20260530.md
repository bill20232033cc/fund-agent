# MVP local acceptance / real provider smoke rerun controller judgment

Gate: `MVP local acceptance / real provider smoke rerun with configured provider`
Role: Gateflow controller
Date: 2026-05-30
Decision: blocked, classification `audit_block`

## Preflight

Required preflight was run before edits:

- `git branch --show-current`: `codex/local-reconciliation`
- `git status --short`: previous smoke gate control/evidence changes plus unrelated untracked files were present. Scope was treated as known; this gate only added rerun evidence and control updates.

PR #21 status at gate start:

- state: `OPEN`
- draft: `true`
- base: `main`
- head: `codex/local-reconciliation`
- merge state: `CLEAN`
- CI `test`: success

## Agent Routing

- Smoke worker ran the real provider command in a same-shell environment after loading the local key file and explicitly exporting typed MVP provider variables.
- Review worker independently reviewed the rerun evidence and recommended `audit_block`.
- Controller ran ruff, full pytest, deterministic default smoke, missing-config fail-closed smoke, JSON validation and secret-value scan.

## Validation

| Check | Result |
|---|---|
| `uv run ruff check .` | pass |
| `uv run pytest --cov=fund_agent --cov-report=term-missing --cov-fail-under=50 -q` | pass, `1106 passed`, coverage `91.76%` |
| default `fund-analysis analyze 006597 --report-year 2024` | pass, exit `0`, chapters `0-7`, evidence anchors present |
| missing-config `fund-analysis analyze 006597 --report-year 2024 --use-llm` | expected fail-closed, exit `1`, empty stdout, no deterministic fallback |
| real provider `fund-analysis analyze 006597 --report-year 2024 --use-llm` | failed closed, exit `1`, classification `audit_block` |

## Decision

This rerun proves the previous blocker changed from missing provider configuration to real provider audit acceptance failure:

- provider config was present for the smoke;
- the command entered the `--use-llm` path;
- no provider runtime/HTTP error was observed;
- no deterministic fallback was observed;
- stdout was empty and no 0-7 report was produced;
- stderr reported `orchestration_status=blocked`, `final_assembly_status=incomplete`, `chapter_not_accepted`, `missing_accepted_draft` and `missing_accepted_conclusion`.

Therefore the gate is blocked as `audit_block`. It is not accepted/pass.

## PR Disposition

PR #21 should remain draft/open. It should not be marked ready for review, merged, released or treated as local acceptance pass based on this rerun. The deterministic default path and fail-closed config path are healthy, but the real provider MVP LLM path does not yet generate an auditable report.

## Next Entry Point

`MVP real provider audit-block diagnostic gate`

Minimum scope:

- preserve current provider config and no-fallback behavior;
- capture per-chapter audit statuses and repair hints without logging secrets or full provider responses;
- classify whether failures are prompt/format compliance, audit rule strictness, missing facts, output truncation, or code defect;
- only then decide whether a minimal fix is needed.

## Boundaries Preserved

- No runtime code was changed in this gate.
- No golden fixtures, golden answers, score, snapshot, quality gate, FQ0-FQ6, schema or final judgment semantics changed.
- No Host/Agent/dayu package or dependency was introduced.
- No push, PR status change, merge, release or promotion was performed.
- No API key value, Authorization header, full environment or full provider response was recorded.

Self-check: controller role only; specialist smoke/review were delegated; gate is blocked with classified reason and no accepted commit was created.
