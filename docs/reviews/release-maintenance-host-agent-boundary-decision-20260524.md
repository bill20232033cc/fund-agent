# Release Maintenance Host/Agent Boundary Decision - 2026-05-24

## Gate / Scope

- Current phase: `release maintenance`.
- Current gate: `release-maintenance Host/Agent boundary decision implementation`.
- Approved plan: `docs/reviews/release-maintenance-next-candidate-plan-20260524.md`.
- Accepted plan commit: `ccde2f7`.
- Work unit type: document-only boundary decision artifact.
- Decision scope: decide whether the current deterministic transition path remains default, define entry criteria for future Host and Agent execution gates, and keep the dependency gate blocked until production imports require it.
- Allowed output: this review artifact only, plus the separate implementation handoff artifact requested for this worker.

Non-goals:

- No source, test, config, README, `docs/design.md`, `docs/implementation-control.md`, `pyproject.toml`, or `uv.lock` changes.
- No `fund_agent/host` or `fund_agent/agent` placeholder package.
- No Host runtime, Agent runner, tool loop, ToolRegistry, ToolTrace, context budget, memory, outbox, cancel/resume, event delivery, LLM audit, or Evidence Confirm implementation.
- No dependency declaration for `dayu.host` or `dayu.engine`.
- No push, PR, merge, commit, issue mutation, or external state change.
- No explicit business parameter may be hidden in `extra_payload` or `extra_payloads`.

## Direct Evidence

| Evidence source | Current fact used for this decision |
|---|---|
| `AGENTS.md` | Current target boundary is `UI -> Service -> Host -> Agent`. Host owns session/run lifecycle, concurrency, timeout, cancel, resume, memory, reply outbox, event delivery, and `ExecutionDeliveryContext`; Host implementation must use `dayu.host`. |
| `AGENTS.md` | Agent owns tool loop, runner, ToolRegistry, ToolTrace, context budget, tool execution, and fund-domain capability; Agent execution kernel must use `dayu.engine`. |
| `AGENTS.md` | The current deterministic transition path may have Service call public `fund_agent/fund` capabilities; Dayu APIs must not be used as scattered bypasses around the four-layer boundary. |
| `AGENTS.md` | Explicit parameters must be explicit fields; they must not be passed through `extra_payload` or `extra_payloads`. |
| `docs/design.md` section 1.3 | Current deterministic `analyze` / `checklist` mainline must not temporarily splice in Host, tool loop, or LLM writing. Agentization requires four-layer contracts, dependency declaration, event flow, ToolTrace, failure semantics, and tests first. |
| `docs/design.md` section 2.1 | Current CLI path is UI -> Service, and Service directly calls public `fund_agent/fund` capabilities as a transition path. New session/run/cancel/resume/outbox capability must enter Host and use `dayu.host`; new tool loop, runner, ToolRegistry, ToolTrace, or context budget capability must enter Agent and use `dayu.engine`. |
| `docs/design.md` section 2.2 | There is no current `HostRun`, `AgentInput`, or scene preparation mainline. Without a concrete session/run/tool-loop requirement, the project should not create empty Host or Agent packages or add unused `dayu.host` / `dayu.engine` dependencies. |
| `docs/implementation-control.md` Startup Packet | Current phase is `release maintenance`; current gate is `release maintenance next candidate plan accepted locally`; next entry point is `release-maintenance Host/Agent boundary decision implementation`. |
| `docs/implementation-control.md` Startup Packet | Before an independent Host/Agent gate opens, no placeholder `fund_agent/host` or `fund_agent/agent` package may be created; future Host must use `dayu.host`; future Agent execution kernel/tool loop/runner/ToolRegistry/ToolTrace must use `dayu.engine`. |
| Current repository directory fact | `find fund_agent -maxdepth 2 -type d` lists `fund_agent/ui`, `fund_agent/config`, `fund_agent/services`, and `fund_agent/fund`, but no `fund_agent/host` or `fund_agent/agent`. |
| Current `pyproject.toml` | Production dependencies do not include `dayu.host`, `dayu.engine`, or other Dayu runtime dependency text. |
| Local baseline | The local engineering baseline for any future dependency gate is `docs/design.md` section 9.1 plus the current `pyproject.toml`: Python `>=3.11`, setuptools build backend, PEP 621 metadata, explicit dependencies, `test` / `dev` optional dependencies, pytest/ruff/black config entries, and package discovery excluding tests/docs/reports/scripts/workspace/cache. |
| External baseline rule | External `dayu-agent` `pyproject.toml` is not a local fact. A future comparison must record exact URL, commit or revision, fetch provenance, and the delta from the local baseline. |

Historical `docs/reviews/` artifacts and implementation-control archive text that use six-layer, Application, Runtime, or old Engine wording are historical evidence only. They are not current architecture truth.

## Current-State Decision

Decision: keep the current deterministic UI -> Service -> `fund_agent/fund` transition as the default production path.

Reasoning:

- The running product currently has a deterministic mainline for `analyze` and `checklist`.
- No current production requirement needs Host lifecycle management such as session/run/cancel/resume/timeout/memory/outbox/event delivery.
- No current production requirement needs Agent execution capabilities such as runner, tool loop, ToolRegistry, ToolTrace, context budget, or traceable tool execution.
- Adding `fund_agent/host`, `fund_agent/agent`, `dayu.host`, or `dayu.engine` without a concrete production import would create architecture surface without evidence-backed behavior.

Current default remains:

```text
UI -> Service -> fund_agent/fund
```

Target boundary remains:

```text
UI -> Service -> Host -> Agent
```

The target boundary is a future implementation direction, not authorization to create placeholder packages in this gate.

## Host Gate Entry Criteria

A Host implementation gate may open only when at least one concrete production requirement cannot be expressed by the current deterministic Service orchestration.

Allowed triggers:

| Trigger | Required evidence before opening gate |
|---|---|
| Multi-run or session lifecycle | A product use case requiring durable session/run identity, lifecycle state, or run history beyond a single deterministic command execution. |
| Cancel, resume, or timeout | A user-facing or operational requirement for cancellation, resumption, timeout policy, or lifecycle recovery. |
| Memory or reply outbox | A concrete need for memory ownership, reply buffering, delivery retries, or outbox semantics outside Service business orchestration. |
| Event delivery | A concrete `ExecutionDeliveryContext` or event stream requirement with consumers, ordering, failure, and retry semantics. |
| Service contract exhaustion | A documented case where Service would otherwise start managing Host lifecycle concerns directly. |

Required constraints once opened:

- Implementation must use `dayu.host`.
- Host may manage session/run/concurrency/timeout/cancel/resume/memory/outbox/event delivery.
- Host must not implement fund-domain logic, tool execution, prompt business semantics, report judgment, annual-report source orchestration, or quality gate rules.
- Any explicit request parameter must be declared in a typed request, contract, or config field; no explicit parameter may be moved into `extra_payload`.
- Package creation, dependency changes, tests, and README updates require their own controller-approved implementation scope.

## Agent Execution Gate Entry Criteria

An Agent execution/tool-loop gate may open only when at least one concrete production requirement needs traceable tool execution or an Agent runtime beyond the current deterministic `fund_agent/fund` domain package.

Allowed triggers:

| Trigger | Required evidence before opening gate |
|---|---|
| Runner or tool loop | A production use case requiring iterative tool selection, runner state, or model/tool orchestration. |
| ToolRegistry | A need to register, discover, authorize, or compose tools through a stable registry contract. |
| ToolTrace | A requirement to emit traceable tool execution records for audit, review, replay, or failure analysis. |
| Context budget | A concrete need to manage context windows, tool output budgets, or truncation policy as part of execution. |
| LLM audit or Evidence Confirm | A future LLM audit / Evidence Confirm path requiring traceable tool execution and failure semantics. |
| Service boundary pressure | A documented case where Service would otherwise own runner/tool-loop mechanics directly. |

Required constraints once opened:

- Implementation must use `dayu.engine`.
- Agent execution may manage runner, tool loop, ToolRegistry, ToolTrace, context budget, tool execution, facts, and execution failure semantics.
- `fund_agent/fund` remains the Agent-layer fund-domain capability package for fund type, annual-report sections, CHAPTER_CONTRACT, preferred_lens, ITEM_RULE, audit rules, and evidence anchors.
- Agent execution must not own UI rendering, Service use-case selection, Host lifecycle, or direct annual-report PDF/source access outside the established fund document repository boundary.
- Any explicit request parameter must be declared in typed contracts; no explicit parameter may be hidden in `extra_payload` or `extra_payloads`.

## Dependency Gate Status

Decision: Host/Agent dependency gate remains blocked until implementation imports require it.

Current dependency status:

- `pyproject.toml` has no current Dayu dependency text.
- No production code imports `dayu.host` or `dayu.engine`.
- No `fund_agent/host` or `fund_agent/agent` package exists.

Dependency gate may open only when:

- A controller-approved Host implementation imports `dayu.host` in production code; or
- A controller-approved Agent execution/tool-loop implementation imports `dayu.engine` in production code.

Future dependency gate must check:

- Local baseline: `docs/design.md` section 9.1 plus current `pyproject.toml`.
- External dayu-agent baseline, if used: exact URL, commit or revision, fetched content/provenance, fetch date, and delta from local baseline.
- Dependency bounds and whether production dependencies, optional `test` / `dev` dependencies, lockfile, package discovery, or package-data are affected.
- No test/development-only package is moved into production dependencies.
- No package-data entry is added unless a production package contains distributable non-Python resources.

Minimum future validation commands, where applicable:

```bash
rg -n "dayu" pyproject.toml
uv lock --check
rg -n "tool\.setuptools\.(packages\.find|package-data)|include-package-data" pyproject.toml
```

Package discovery/import smoke checks are required for any newly introduced `fund_agent/host` or `fund_agent/agent` package.

## Future Gate Skeletons

### Host implementation gate

Allowed files only after controller approval:

- `fund_agent/host/**`
- Host-specific tests under `tests/**`
- `fund_agent/host/README.md`
- Shared Service/Host contract files only if the approved plan names them explicitly
- `pyproject.toml` / `uv.lock` only if production Host imports require `dayu.host`

Required contract content:

- Session/run identity and lifecycle states.
- Timeout, cancellation, resume, memory, reply outbox, event delivery, and `ExecutionDeliveryContext` semantics if included in scope.
- Sync/async contract boundary and failure taxonomy.
- Service-to-Host and Host-to-Agent call shape.
- Explicit parameter schema with no `extra_payload` for explicit business parameters.

Required tests:

- Lifecycle state transition tests.
- Timeout/cancel/resume tests for every implemented lifecycle branch.
- Event/outbox delivery tests if included.
- Failure taxonomy tests.
- Import smoke and package discovery tests.
- Boundary tests proving Host does not implement fund-domain logic or tool execution.

README trigger:

- Any `fund_agent/host/**` change must update `fund_agent/host/README.md`.
- Any boundary or assembly change must also update `fund_agent/README.md` only within a separately approved docs scope.

Stop conditions:

- Host plan attempts to implement tool loop, ToolRegistry, ToolTrace, fund-domain rules, annual-report source orchestration, or report judgment.
- Host plan avoids `dayu.host`.
- Host plan creates package scaffolding without a concrete lifecycle requirement.
- Host plan uses `extra_payload` for explicit business parameters.

### Agent execution/tool-loop gate

Allowed files only after controller approval:

- `fund_agent/agent/**`
- Agent-execution-specific tests under `tests/**`
- `fund_agent/agent/README.md`
- Shared Host/Agent or Service/Agent contract files only if the approved plan names them explicitly
- `pyproject.toml` / `uv.lock` only if production Agent execution imports require `dayu.engine`

Required contract content:

- Runner and tool-loop lifecycle.
- ToolRegistry registration, authorization, and invocation contract.
- ToolTrace schema, failure semantics, and replay/review requirements.
- Context budget policy and tool output handling.
- Boundary between generic Agent execution and `fund_agent/fund` domain capabilities.
- Explicit parameter schema with no `extra_payload` or `extra_payloads` for explicit business parameters.

Required tests:

- Runner/tool-loop state transition tests.
- ToolRegistry registration and invocation tests.
- ToolTrace schema and failure taxonomy tests.
- Context budget truncation/error tests.
- Boundary tests proving Agent execution does not own UI, Service use-case selection, Host lifecycle, or direct annual-report source/PDF access.
- Import smoke and package discovery tests.

README trigger:

- Any `fund_agent/agent/**` change must update `fund_agent/agent/README.md`.
- Any `fund_agent/fund/**` domain-boundary change must update `fund_agent/fund/README.md` only within the approved implementation scope.

Stop conditions:

- Agent plan avoids `dayu.engine`.
- Agent plan implements Host session/run lifecycle.
- Agent plan bypasses `FundDocumentRepository` / `FundDataExtractor` for production annual-report access.
- Agent plan uses `extra_payload` for explicit business parameters.
- Agent plan creates a generic execution package without a concrete runner/tool-loop/trace requirement.

### Dependency gate

Allowed files only after controller approval:

- `pyproject.toml`
- `uv.lock`
- Dependency or package-data smoke tests if explicitly approved
- Implementation files that already require the dependency through an approved Host or Agent gate

Required checks:

- Prove the production implementation imports `dayu.host` and/or `dayu.engine`.
- Compare dependency decision to the local baseline: `docs/design.md` section 9.1 plus current `pyproject.toml`.
- If using external `dayu-agent` as evidence, record URL, commit/revision, fetched content/provenance, fetch date, and delta from local baseline.
- Check package discovery and package-data impact.
- Confirm no development/test dependency leaks into production dependencies.
- Confirm `uv lock --check` passes after lockfile update.

Required validation:

```bash
rg -n "dayu" pyproject.toml
uv lock --check
rg -n "tool\.setuptools\.(packages\.find|package-data)|include-package-data" pyproject.toml
```

Additional import smoke must cover any introduced `fund_agent/host` or `fund_agent/agent` package and any new `dayu.host` / `dayu.engine` imports.

Stop conditions:

- Dependency is added before production imports need it.
- Dependency source or external dayu-agent baseline lacks URL, commit/revision, or provenance.
- Lockfile is changed without a dependency graph reason.
- Package discovery or package-data behavior changes without tests and docs.

## Validation Plan

The following commands are programmatic existence and hygiene checks. They do not prove semantic correctness; semantic correctness, boundary fit, and evidence quality remain review responsibilities.

Required checks for this artifact:

```bash
rg -n "UI -> Service -> Host -> Agent|dayu.host|dayu.engine|extra_payload|pyproject|fund_agent/host|fund_agent/agent" docs/reviews/release-maintenance-host-agent-boundary-decision-20260524.md
rg -n "dependency gate remains blocked|blocked until implementation imports|no fund_agent/host|no fund_agent/agent|extra_payload|local baseline|docs/design.md.*9\.1|external dayu-agent|URL|commit|provenance" docs/reviews/release-maintenance-host-agent-boundary-decision-20260524.md
rg -n "Host implementation gate|Agent execution/tool-loop gate|Dependency gate|Stop Conditions" docs/reviews/release-maintenance-host-agent-boundary-decision-20260524.md
rg -n "rg -n .*dayu.*pyproject\.toml|uv lock --check|tool\.setuptools\.packages\.find|tool\.setuptools\.package-data|package discovery|package-data|URL|commit|provenance" docs/reviews/release-maintenance-host-agent-boundary-decision-20260524.md
git diff --check
git status --short
```

Expected pass criteria:

- Required boundary and guardrail terms are present.
- Future gate skeletons include Host, Agent execution/tool-loop, and dependency gates.
- Dependency gate remains conditional and blocked until implementation imports require it.
- Diff has no whitespace errors.
- `git status --short` shows only the two allowed new `docs/reviews` artifacts for this handoff.

## Review Checklist

- Confirms current truth uses Dayu four-layer `UI -> Service -> Host -> Agent`.
- Confirms current deterministic default remains UI -> Service -> `fund_agent/fund`.
- Confirms Host, if landed, must use `dayu.host`.
- Confirms Agent execution/tool-loop, if landed, must use `dayu.engine`.
- Confirms no `fund_agent/host` or `fund_agent/agent` placeholder package is created.
- Confirms dependency gate remains blocked until production implementation imports require it.
- Confirms no source/test/config/README/design/control/pyproject/lockfile changes are part of this boundary decision.
- Confirms no explicit parameter is hidden in `extra_payload` or `extra_payloads`.
- Confirms future package/dependency changes check local `docs/design.md` section 9.1 plus current `pyproject.toml`.
- Confirms any external `dayu-agent` pyproject comparison records URL, commit/revision, fetched content/provenance, and delta from the local baseline.
- Confirms production annual-report access remains through `FundDocumentRepository` / `FundDataExtractor` and not through direct PDF/source/cache calls from Service, Host, UI, renderer, or quality gate.
- Confirms License/repo hygiene is unchanged and not weakened by metadata or test relaxation.
- Confirms historical six-layer, Application, Runtime, or old Engine wording is not used as current architecture basis.

## Stop Conditions

Stop and return to controller if any of these occur:

- A reviewer asks to implement Host or Agent packages in this gate.
- A reviewer asks to add `dayu.host` or `dayu.engine` dependencies without a concrete production implementation import and test plan.
- A reviewer asks to revive six-layer, Application facade, Runtime/Engine naming, or old archive architecture as current truth.
- A concrete Host session/run or Agent tool-loop requirement is introduced that expands scope beyond a decision artifact.
- Any implementation plan requires modifying `fund_agent/**`, `tests/**`, `pyproject.toml`, `uv.lock`, README, `docs/design.md`, or `docs/implementation-control.md`.
- Any plan proposes `extra_payload` or `extra_payloads` for explicit business parameters.
- Any plan bypasses `FundDocumentRepository` / `FundDataExtractor` for production annual-report access.
- Any plan weakens License/repo hygiene or dependency/package-data discipline to make the gate pass.

Stop report format:

- Triggered condition:
- Context / evidence:
- Suggested scope adjustment:
- User decision required: yes / no

## Decision Absorption Path

If this decision is accepted by review/controller:

- Controller records the accepted Host/Agent boundary decision in control tracking.
- Controller may open a separate docs/control update only if the accepted decision changes current truth.
- This artifact alone does not modify design truth, control truth, README, package layout, dependencies, runtime behavior, CLI behavior, tests, or public contracts.
- Future implementation gates must cite this decision, the approved plan, and the current `AGENTS.md` / `docs/design.md` / `docs/implementation-control.md` truth sources before changing packages or dependencies.

## Completion Report Format

Implementation worker completion report should include:

- Artifact paths:
- Decision:
- Future gates opened / blocked:
- Changed files:
- Validation run: each command, expected assertion, exit code or observed pass signal, and skipped validation with reason.
- Docs decision:
- Residual risks:
- Decision absorption path:
- Blocking questions:
- Recommended next gate:

## Handoff Status

Handoff status: ready for plan review.

Blocking questions: none.

Recommended next gate: `release-maintenance Host/Agent boundary decision plan review`.
