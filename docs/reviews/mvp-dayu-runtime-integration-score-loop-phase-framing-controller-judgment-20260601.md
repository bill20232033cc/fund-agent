# MVP Dayu runtime integration and score-loop phase framing controller judgment

Date: 2026-06-01
Gate: `MVP Dayu runtime integration and score-loop phase framing gate`
Gate type: docs-only plan gate
Role: Gateflow controller
Judgment: accepted docs-only phase framing

## Decision

Accepted.

The reviewed phase plan correctly frames the long-line route as future design while preserving current implementation facts:

1. `dayu.host runtime governance adapter`
2. Service ExecutionContract boundary convergence
3. `dayu.engine` Agent/tool-loop migration
4. Fund score-loop implementation
5. Codex iterative score improvement loop

This gate does not implement code and does not change the current production path.

## Evidence

- Plan artifact: `docs/reviews/mvp-dayu-runtime-integration-score-loop-phase-framing-plan-20260601.md`
- MiMo plan review: `docs/reviews/mvp-dayu-runtime-integration-score-loop-phase-framing-plan-review-mimo-20260601.md`

MiMo review conclusion: `PASS`; no blocking findings.

## Current Fact Boundary

Current facts remain unchanged:

- Current production path is `CLI -> Service -> fund_agent/fund -> provider HTTP call`.
- Current code has no Host/Agent/dayu runtime in the production path.
- `dayu.host runtime governance adapter` is a user-facing MVP readiness prerequisite.
- `dayu.engine` migration is a later Agent/tool-loop gate.
- Gate C score-loop design remains design-only and is not connected to readiness, golden, fixtures, existing score, or quality gate.

## Controller Findings

- The plan keeps `dayu.host` before `dayu.engine`.
- The plan keeps Service as owner of business semantics and ExecutionContract assembly.
- The plan keeps Host free of fund-domain semantics.
- The plan preserves the rule that explicit parameters must not be tunneled through `extra_payload`.
- The plan keeps provider runtime timeout as `not_scored / blocked_provider_runtime` for future score-loop work.
- The plan does not change the next actual implementation entry.

## Documentation Sync Decision

No truth-source doc sync is needed in this gate.

`docs/design.md`, `docs/implementation-control.md`, and `docs/current-startup-packet.md` already state the current implementation path, lack of Host/Agent/dayu runtime, `dayu.host` readiness prerequisite, deferred `dayu.engine` migration, and Gate C score-loop design-only boundary.

## Next Entry Point

`MVP dayu.host runtime governance adapter plan gate`

## Non-Goals Preserved

- No runtime/code/tests changes.
- No `fund_agent/host` or `fund_agent/agent` package creation.
- No `dayu.host` or `dayu.engine` dependency addition.
- No README or `AGENTS.md` changes.
- No quality gate, score, golden, fixture promotion, release-readiness, PR, push, merge, mark-ready or release changes.
- No cleanup or deletion of historical untracked residuals.

## Validation

Required before accepted checkpoint:

- `git diff --check`
- `git diff --cached --name-status`
- `git diff --cached --check`
- staged files limited to this gate's plan, review and controller judgment artifacts.
