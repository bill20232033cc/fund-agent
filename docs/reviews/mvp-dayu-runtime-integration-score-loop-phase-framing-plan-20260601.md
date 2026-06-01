# MVP Dayu runtime integration and score-loop phase framing plan

Date: 2026-06-01
Gate: `MVP Dayu runtime integration and score-loop phase framing gate`
Gate type: docs-only plan gate
Role: Gateflow controller phase-framing artifact

## Current Facts

- Current production path is still `CLI -> Service -> fund_agent/fund -> provider HTTP call`.
- Current code has no Host/Agent/dayu runtime in the production path.
- `dayu.host runtime governance adapter` is already a user-facing MVP readiness prerequisite.
- `dayu.engine` migration remains a later Agent/tool-loop gate.
- Gate C chapter generation score-loop design is accepted as design-only. It is not connected to readiness, golden, fixtures, the existing score system, or the quality gate.
- The next implementation entry remains `MVP dayu.host runtime governance adapter plan gate` unless review of this framing gate explicitly changes it.

## Accepted Future Design

The future route should be sequenced as separate gates:

1. `dayu.host runtime governance adapter`
2. Service ExecutionContract boundary convergence
3. `dayu.engine` Agent/tool-loop migration
4. Fund score-loop implementation
5. Codex iterative score improvement loop

This is a future route, not current implementation.

## Candidate Inputs

- Gate C score-loop design provides a candidate scoring taxonomy and artifact lifecycle.
- Existing provider runtime budget / prompt-cost / shim diagnostics provide transitional evidence for timeout classification.
- Existing Route C LLM report path provides the current transition execution body, but does not provide Host lifecycle governance or Agent tool-loop semantics.

Candidate inputs must not override current truth-source facts.

## Why Dayu Capability Must Be Split Into Gates

A single migration would blend four different concerns:

- runtime governance: run lifecycle, deadlines, cancellation and safe terminal state;
- Service contract boundaries: business semantics, prompt/ExecutionContract ownership and typed parameter rules;
- Agent execution mechanics: runner, tool loop, ToolRegistry, ToolTrace and context budget;
- Fund scoring and improvement loops: score artifacts, fixed corpus and targeted code changes.

Splitting the work avoids treating `dayu.engine` as a fix for the current provider timeout blocker and avoids turning score-loop diagnostics into readiness/golden/quality-gate state. It also lets `dayu.host` solve the immediate user-facing runtime governance gap while keeping the current Service -> Fund transition body intact.

## Gate 1: dayu.host runtime governance adapter

### Goal

Wrap the current `fund-analysis analyze --use-llm` Service -> Fund execution path in Host-managed run lifecycle without migrating to Agent/tool-loop yet.

### Required Capabilities

- `run_id`
- `started_at`
- `deadline_at`
- global deadline
- cancel
- terminal run state
- run lifecycle transitions
- safe diagnostics
- provider timeout classification

### Boundary

- Host owns run/session lifecycle, timeout propagation, cancellation, terminal state and safe event/diagnostic framing.
- Host does not understand fund business semantics, CHAPTER_CONTRACT, evidence anchors, prompt content or score rules.
- The current Service -> `fund_agent/fund` path remains the transition execution body.
- Runtime budget / prompt-cost / dayu-compatible shim remains transitional until replaced by real Host governance.

### Timeout Taxonomy

The implementation plan must keep these classes distinct:

- `run_deadline_exceeded`
- `phase_timeout`
- `provider_runtime_timeout`

Small-prompt provider timeout must continue to be classified as provider runtime behavior, not prompt-contract failure or scoring failure.

### Validation Direction

- Host lifecycle unit tests.
- deadline/cancel propagation tests.
- safe diagnostics tests.
- missing-config `--use-llm` fail-closed unchanged.
- deterministic analyze/checklist unchanged.
- real provider smoke remains fail-closed unless complete 0-7 report is produced.
- no deterministic fallback.

## Gate 2: Service ExecutionContract boundary convergence

### Goal

Make Service-to-Host execution contracts explicit before moving Agent execution into `dayu.engine`.

### Required Decisions

- Service interprets business semantics.
- Service owns scene/prompt/ExecutionContract assembly.
- Service owns report strategy and user-facing use-case semantics.
- Host receives lifecycle-safe execution requests and delivery context, not fund-domain rules.
- Explicit parameters must remain typed fields.
- Explicit parameters must not be tunneled through `extra_payload`.

### Boundary

- Host may carry generic metadata needed for lifecycle, tracing, cancellation and delivery.
- Host must not parse fund code, year, fund type, CHAPTER_CONTRACT, audit rules or evidence anchors as business behavior.
- Service must not bypass Host for future run lifecycle once the Host adapter is accepted.

### Output

An implementation-ready contract plan that defines request/response/event boundaries and migration-safe adapters while preserving current behavior.

## Gate 3: dayu.engine Agent/tool-loop migration

### Goal

Move Agent execution mechanics into `dayu.engine` only after Host lifecycle and Service contract boundaries are explicit.

### Required Capabilities

- ToolRegistry
- ToolTrace
- context budget
- Agent runner
- tool loop
- tool execution contracts
- trace-safe failure semantics

### Boundary

- `fund_agent/fund` remains the Fund domain capability package.
- `dayu.engine` supplies execution mechanics; it does not replace Fund rules.
- Service still owns business use-case semantics.
- Host still owns lifecycle, cancellation, deadline and terminal run state.

### Non-Minimality For Current Timeout

This migration is not the minimal solution for the current small-prompt provider timeout blocker. It must not precede the `dayu.host` runtime governance adapter unless a reviewed gate changes the readiness strategy.

## Gate 4: Fund score-loop implementation

### Goal

Implement scoring artifacts after runtime and contract boundaries are clear enough to prevent score output from being misused as readiness state.

### Score Types

- `extraction_score`
- `chapter_fact_score`
- `chapter_generation_score`

### Provider Runtime Handling

Provider timeout is scored as:

- `not_scored`
- `blocked_provider_runtime`

It must not be converted into a generation quality pass/fail. It must not update existing golden, fixtures, score outputs, quality gate results or release readiness.

### Required Inputs From Earlier Gates

- Host terminal state and safe runtime diagnostics from Gate 1.
- Explicit Service ExecutionContract boundaries from Gate 2.
- ToolTrace/context budget semantics from Gate 3 if the implementation scores Agent/tool-loop behavior.

### Implementation Preconditions

Before implementation, resolve Gate C residuals:

- naming relationship between `ChapterFactProjection` and any score-loop input type;
- relationship to existing `fund_agent/fund/extraction_score.py` and `fund_agent/services/extraction_score_service.py`;
- score weights/value semantics;
- `not_scored_reason` enum;
- CLI exit-code impact;
- candidate facet / L2 source boundary.

## Gate 5: Codex iterative score improvement loop

### Goal

Use score artifacts to drive controlled code-improvement loops without turning the loop into autonomous release, PR, golden or quality-gate mutation.

### Loop

1. Fixed corpus
2. Score artifact
3. Accepted finding
4. Targeted fix
5. Rerun
6. Score delta

### Governance

- The corpus must be fixed and reviewed for the gate.
- Findings must be accepted by controller judgment before fixes.
- Fixes must be scoped to the accepted finding.
- Reruns must produce comparable score artifacts.
- Score deltas are diagnostic evidence, not automatic release readiness.
- The loop must not push, merge, mark PR ready, promote fixtures or update golden outputs without separate authorization.

## Non-Goals

- No runtime implementation.
- No code or tests.
- No `fund_agent/host` or `fund_agent/agent` package creation.
- No `dayu.host` or `dayu.engine` dependency addition.
- No README update unless a separate check proves README conflicts with current code facts.
- No `AGENTS.md` edit.
- No quality gate, score, golden, fixture promotion or release-readiness semantic change.
- No PR state change, push, merge, mark-ready or release.
- No cleanup of historical untracked residuals.

## Stop Conditions

Stop before implementation or sync if:

- the plan requires code changes;
- the plan requires a new dependency;
- the plan requires editing `AGENTS.md`;
- the plan changes the current next implementation entry away from `MVP dayu.host runtime governance adapter plan gate`;
- future route text cannot be clearly separated from current implementation facts;
- any staged file falls outside this gate's plan/controller artifact and explicitly approved minimal truth-source sync;
- any change would affect quality gate, score, golden, fixture promotion, release-readiness or PR state.

## Documentation Sync Strategy

Current truth-source docs already state the key facts:

- current implementation path;
- no Host/Agent/dayu runtime;
- `dayu.host` adapter as user-facing MVP readiness prerequisite;
- `dayu.engine` as later Agent/tool-loop migration;
- Gate C score-loop as design-only.

Therefore this gate should not update `docs/design.md`, `docs/implementation-control.md` or `docs/current-startup-packet.md` unless independent review finds a concrete mismatch. If sync is needed later, it must be short and must not append a long roadmap to control/startup docs.

## Review Requirements

This plan must be reviewed as a docs-only architecture/phase-framing plan. Review should check:

- current facts are not written as future implementation;
- future design is not written as current code fact;
- `dayu.host` remains before `dayu.engine`;
- Service ExecutionContract boundary is explicit;
- score-loop remains separate from readiness/golden/quality gate;
- next implementation entry remains `MVP dayu.host runtime governance adapter plan gate`;
- stop conditions protect runtime/code/tests/dependencies/PR state.

## Next Entry Point

Unless review explicitly finds a better sequence, the next actual implementation entry remains:

`MVP dayu.host runtime governance adapter plan gate`
