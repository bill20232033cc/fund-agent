# Release Maintenance Host/Agent Boundary Decision Implementation - 2026-05-24

## Gate

- Current phase: `release maintenance`.
- Current gate: `release-maintenance Host/Agent boundary decision implementation`.
- Worker role: implementation worker only; not controller.
- External actions: none.
- Commit / push / PR / merge: not performed.

## Approved Plan

- Approved plan: `docs/reviews/release-maintenance-next-candidate-plan-20260524.md`.
- Accepted plan commit: `ccde2f7`.
- Plan type: document-only boundary decision.
- Planned decision artifact: `docs/reviews/release-maintenance-host-agent-boundary-decision-20260524.md`.
- Handoff-added implementation artifact: `docs/reviews/release-maintenance-host-agent-boundary-decision-implementation-20260524.md`.

## Scope / Non-Goals

Implemented scope:

- Added a Host/Agent boundary decision artifact under `docs/reviews/`.
- Added this implementation handoff artifact under `docs/reviews/`.
- Preserved the current deterministic UI -> Service -> `fund_agent/fund` default path.
- Recorded Host, Agent execution/tool-loop, and dependency gate entry criteria.
- Recorded future gate skeletons, validation plan, review checklist, stop conditions, decision absorption path, and completion report format.

Non-goals honored:

- No source, test, config, README, `docs/design.md`, `docs/implementation-control.md`, `pyproject.toml`, or `uv.lock` changes.
- No `fund_agent/host` or `fund_agent/agent` placeholder package.
- No Host runtime implementation.
- No Agent runner, tool loop, ToolRegistry, ToolTrace, context budget, or tool execution implementation.
- No dependency change for `dayu.host` or `dayu.engine`.
- No external Dayu repository fetch.
- No explicit parameter moved into `extra_payload` or `extra_payloads`.

## Changed Files

- Added: `docs/reviews/release-maintenance-host-agent-boundary-decision-20260524.md`
- Added: `docs/reviews/release-maintenance-host-agent-boundary-decision-implementation-20260524.md`

## Implemented Plan Items

| Plan item | Status | Evidence |
|---|---|---|
| Required decision artifact section skeleton | Done | Decision artifact includes exactly the required top-level sections from the approved plan. |
| Direct evidence and current-state matrix | Done | Decision artifact cites `AGENTS.md`, `docs/design.md`, `docs/implementation-control.md`, current `pyproject.toml`, and directory fact that `fund_agent/host` / `fund_agent/agent` do not exist. |
| Keep deterministic transition path | Done | Decision artifact records UI -> Service -> `fund_agent/fund` as the current default production path. |
| Host gate entry criteria | Done | Decision artifact lists lifecycle/session/run/cancel/resume/timeout/memory/outbox/event-delivery triggers and requires `dayu.host`. |
| Agent execution gate entry criteria | Done | Decision artifact lists runner/tool-loop/ToolRegistry/ToolTrace/context budget/tool execution triggers and requires `dayu.engine`. |
| Dependency gate status | Done | Decision artifact states the dependency gate remains blocked until production implementation imports require `dayu.host` or `dayu.engine`. |
| Local/external baseline requirements | Done | Decision artifact defines local baseline as `docs/design.md` section 9.1 plus current `pyproject.toml`, and requires URL/commit/provenance for any external `dayu-agent` baseline. |
| Future gate skeletons | Done | Decision artifact includes Host implementation, Agent execution/tool-loop, and Dependency gate skeletons. |
| Stop conditions and stop report format | Done | Decision artifact includes gate stop conditions and the stop report fields required by the approved plan. |
| Decision absorption path | Done | Decision artifact records controller tracking or a separate docs/control update as the only absorption path after acceptance. |
| Completion report format | Done | Decision artifact includes command/result validation reporting requirements. |

## Validation

Validation run:

| Command | Expected assertion | Result |
|---|---|---|
| `rg -n "^## " docs/reviews/release-maintenance-host-agent-boundary-decision-20260524.md` | Decision artifact includes exactly the approved top-level section skeleton. | Pass, exit code 0; output lists the 13 required sections and no extra top-level sections. |
| `rg -n "UI -> Service -> Host -> Agent\|dayu.host\|dayu.engine\|extra_payload\|pyproject\|fund_agent/host\|fund_agent/agent" docs/reviews/release-maintenance-host-agent-boundary-decision-20260524.md` | Required boundary, dependency, package, and explicit-parameter guardrail terms are present. | Pass, exit code 0; required terms found. |
| `rg -n "dependency gate remains blocked\|blocked until implementation imports\|no fund_agent/host\|no fund_agent/agent\|extra_payload\|local baseline\|docs/design.md.*9\\.1\|external dayu-agent\|URL\|commit\|provenance" docs/reviews/release-maintenance-host-agent-boundary-decision-20260524.md` | Dependency gate remains blocked; no placeholder packages; no explicit params in `extra_payload`; local/external baseline requirements are present. | Pass, exit code 0; required terms found. |
| `rg -n "Host implementation gate\|Agent execution/tool-loop gate\|Dependency Gate\|Dependency gate\|Stop Conditions" docs/reviews/release-maintenance-host-agent-boundary-decision-20260524.md` | Future Host, Agent execution/tool-loop, Dependency gate, and Stop Conditions sections are present. | Pass, exit code 0; required terms found. |
| `rg -n "rg -n .*dayu.*pyproject\\.toml\|uv lock --check\|tool\\.setuptools\\.packages\\.find\|tool\\.setuptools\\.package-data\|package discovery\|package-data\|URL\|commit\|provenance" docs/reviews/release-maintenance-host-agent-boundary-decision-20260524.md` | Future dependency validation commands and baseline provenance checks are present. | Pass, exit code 0; required terms found. |
| `git diff --check` | No whitespace errors in the current diff. | Pass, exit code 0; no output. |
| `git status --short` | Only the two allowed files are changed. | Pass, exit code 0; output shows only the two new `docs/reviews` artifacts. |

Skipped validation:

- No source/test suite was run because this work unit is document-only and changes no runtime code.
- No `uv lock --check` was run because dependency files were not changed; the decision artifact records it as a future dependency-gate validation command.

## Docs Decision

No README, design, control, source, test, config, dependency, or lockfile docs were updated.

Reason:

- This work unit changes no runtime behavior, public CLI, package boundary, dependency graph, current design truth, or control truth.
- The approved scope is `docs/reviews/` artifacts only.
- Any future absorption into control tracking or design/control docs requires a separate controller-authorized docs/control update.

## Residual Risks

- The `rg` validation checks are existence checks only; they do not prove semantic correctness.
- Semantic correctness, boundary fit, and evidence quality remain the responsibility of the plan review / re-review gate.
- No external `dayu-agent` `pyproject.toml` was fetched; this is intentional because the current gate only records provenance requirements for a future dependency gate.

## Completion Status

Status: implementation complete; validation passed.

Blocking questions: none.
