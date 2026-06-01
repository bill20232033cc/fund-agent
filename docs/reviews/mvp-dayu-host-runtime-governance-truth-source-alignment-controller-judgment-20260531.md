# MVP dayu.host Runtime Governance Truth-Source Alignment Controller Judgment

- Gate: `MVP dayu.host runtime governance truth-source alignment gate`
- Role: Gateflow controller.
- Date: 2026-05-31
- Classification: `heavy`
- Judgment: accepted docs-only truth-source alignment

## Decision

This docs-only gate aligns the truth sources: `dayu.host runtime governance adapter gate` is a user-facing MVP readiness prerequisite, not optional future work.

The current implementation remains `CLI -> Service -> fund_agent/fund -> provider HTTP call`. The current runtime budget / prompt-cost / dayu-compatible shim remains transitional and does not provide full runtime governance.

`dayu.engine` migration remains deferred to a future Agent/tool-loop gate because it is not the minimum solution for the current small-prompt provider timeout blocker.

## Next Entry

`MVP dayu.host runtime governance adapter plan gate`

## Non-Goals Preserved

- No runtime implementation.
- No `AGENTS.md` edit.
- No tests/README changes.
- No golden/fixtures/score/quality gate changes.
- No PR state change, push, merge or release.
- No cleanup of unrelated untracked files.

## Validation

Completed:

- `git diff --check`

Result: PASS.

Ruff/pytest are not required for this docs-only truth-source alignment.
