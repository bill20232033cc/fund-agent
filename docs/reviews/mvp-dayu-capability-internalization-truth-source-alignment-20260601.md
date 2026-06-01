# MVP Dayu capability internalization truth-source alignment

Date: 2026-06-01
Gate: `MVP Dayu capability internalization truth-source alignment gate`
Gate type: heavy docs-only truth-source alignment
Role: Gateflow controller

## Trigger

`MVP dayu.host runtime governance adapter implementation gate` stopped in preflight:

- local venv can import `dayu.host`;
- `pyproject.toml` / `uv.lock` do not declare `dayu` or `dayu-agent`;
- `uv pip show dayu` fails;
- `uv pip show dayu-agent` reports local `dayu-agent==0.1.4`.

User decision: do not add `dayu-agent` as production runtime dependency. Dayu must be treated as architecture reference and capability source, not as a direct runtime interface dependency.

## Truth-Source Decision

Accepted direction:

1. Dayu remains the four-layer architecture reference for `UI -> Service -> Host -> Agent`.
2. This project does not directly depend on `dayu-agent`, `dayu.host` or `dayu.engine` as production runtime.
3. Host must internalize Dayu Host stable capabilities:
   - run lifecycle
   - global deadline
   - cancel
   - terminal state
   - safe diagnostics
   - event/outbox
   - concurrency boundary
   - resume/replay as future boundary
4. Agent engine/tool-loop must later internalize Dayu Engine stable capabilities:
   - runner
   - tool loop
   - ToolRegistry
   - ToolTrace
   - context budget
   - tool execution contract
5. Upstream Dayu code may be read as research input. Copying or rewriting upstream code must first pass a dedicated license/compliance gate.

## Files Updated

- `AGENTS.md`
- `docs/design.md`
- `docs/implementation-control.md`
- `docs/current-startup-packet.md`

## Scope Preserved

- No runtime/code/tests modified.
- No `fund_agent/host` created.
- No `dayu-agent`, `dayu`, `dayu.host` or `dayu.engine` dependency added.
- No `uv lock` run.
- No score, quality gate, golden, fixture promotion, release-readiness or PR state changed.
- Historical untracked residuals were not processed.

## Current Implementation Fact

Current production path remains:

```text
CLI -> Service -> fund_agent/fund -> provider HTTP call
```

There is still no Host/Agent/dayu runtime in the production path.

## Blocked Gate Disposition

The previous direct `dayu.host` runtime governance adapter implementation gate remains blocked and is superseded as an implementation direction.

Next entry point is no longer a dependency declaration gate. It is:

`MVP internalized Host runtime governance adapter plan gate`

## Validation

Required validation for this docs-only gate:

- `git diff --check`
- `git status --short --untracked-files=all`

Ruff and pytest are not required because this gate does not modify runtime, code or tests.
