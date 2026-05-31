# MVP Dayu capability internalization truth-source alignment controller judgment

Date: 2026-06-01
Gate: `MVP Dayu capability internalization truth-source alignment gate`
Gate type: heavy docs-only truth-source alignment
Role: Gateflow controller
Judgment: accepted

## Decision

Accepted.

The truth-source conflict is resolved: Dayu remains the four-layer architecture reference and capability source, but `dayu-agent`, `dayu.host` and `dayu.engine` are no longer accepted production runtime dependencies for this project.

## Accepted Truth

- Current implementation remains `CLI -> Service -> fund_agent/fund -> provider HTTP call`.
- Current code still has no Host/Agent/dayu runtime in the production path.
- The prior direct `dayu.host` implementation direction remains blocked and superseded.
- Host runtime governance must be internalized in this project.
- Future Agent engine/tool-loop capability must be internalized in this project.
- Upstream Dayu code is research input only.
- Copying or rewriting upstream Dayu code requires a separate license/compliance gate.

## Files Accepted

- `AGENTS.md`
- `docs/design.md`
- `docs/implementation-control.md`
- `docs/current-startup-packet.md`
- `docs/reviews/mvp-dayu-capability-internalization-truth-source-alignment-20260601.md`
- `docs/reviews/mvp-dayu-capability-internalization-truth-source-alignment-controller-judgment-20260601.md`

## Next Entry Point

`MVP internalized Host runtime governance adapter plan gate`

The next gate must design a local Host runtime governance adapter without importing `dayu.host` or adding `dayu-agent` as a dependency.

## Validation

- `git diff --check` PASS.
- `git status --short --untracked-files=all` reviewed; remaining untracked historical residuals are out of scope.
- Ruff/pytest not run because this gate is docs-only and does not modify runtime, code or tests.

## Non-Goals Preserved

- No runtime/code/tests modified.
- No `fund_agent/host` created.
- No dependency added.
- No `uv lock`.
- No score, quality gate, golden, fixture promotion, release-readiness or PR state changed.
- No push, PR, merge, mark-ready or release action occurred.
