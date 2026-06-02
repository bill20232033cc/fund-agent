# MVP internalized Agent engine/tool-loop contract execution design

## Worker Self-Check

- Role: scoped design worker only, not controller.
- Gate: `MVP internalized Agent engine/tool-loop contract execution design gate`.
- Classification: heavy.
- Scope: design/review artifact only; future architecture proposal only.
- Required read set: completed for `AGENTS.md`, `docs/design.md`, `docs/implementation-control.md`, `docs/current-startup-packet.md`, `docs/fund-analysis-template-draft.md`, accepted typed template/audit design artifacts, provider-restored Slice 1 controller judgment, and retained `summary.json`.
- Optional boundary-fact read set: completed for `fund_agent/services/chapter_orchestrator.py`, `fund_agent/fund/chapter_writer.py`, `fund_agent/fund/chapter_auditor.py`, `fund_agent/host/README.md`; `fund_agent/agent/README.md` was absent or empty.
- Actions taken: wrote this single `docs/reviews/` design artifact.
- Actions intentionally not taken: no Phaseflow/Gateflow controller start, no implementation, no source/test/config/runtime edits, no prompt/provider/auditor/quality/golden/score/report mutation, no edits to `docs/design.md`, `docs/implementation-control.md`, `docs/current-startup-packet.md`, `docs/fund-analysis-template-draft.md`, `contracts.py`, retained reports, or README files, no commit, no push, no PR.
- Truth status: this artifact is proposed future design for controller/reviewer consideration. It is not current implementation fact and does not authorize implementation.

## Current Facts

The following are current facts from the required sources and optional boundary reads:

- Default production report/checklist remains deterministic `fund-analysis analyze/checklist`.
- Current deterministic path is `CLI -> Service -> fund_agent/fund`; current `--use-llm` path is `CLI -> Service prepares FundLLMExecutionRequest / ExecutionContract -> Host runner -> Service -> fund_agent/fund -> provider HTTP call`.
- `--use-llm` remains explicit opt-in, fail-closed, with empty stdout for incomplete LLM results and no deterministic fallback.
- Host currently owns process-local lifecycle, global deadline, cancel token, terminal run state, safe diagnostics, and events; Host does not understand fund business fields and does not implement Agent tool loop.
- Current Gate 3 `ChapterOrchestrator` is Service-owned `chapter_orchestrator.v1` write-audit-repair facade for body chapters 1-6.
- Current Fund primitives include `chapter_writer.py` and `chapter_auditor.py`; they consume explicit typed inputs and injected LLM Protocol clients and do not read repositories, PDF/cache/source helpers, Service, Host, or dayu.
- Current template truth is still `docs/fund-analysis-template-draft.md` with public chapter ids `0-7`.
- Current retained run `006597 / 2024` has `orchestration_status=partial` and `final_assembly_status=incomplete`.
- Retained `summary.json` shows chapters 1 and 5 accepted; chapters 2, 4, and 6 failed with `llm_timeout`; chapter 3 failed with `repair_budget_exhausted` / `prompt_contract`; final assembly blocked because chapters 2, 3, 4, and 6 lacked accepted drafts and conclusions.
- Ch2/Ch4/Ch6 timeout evidence is provider runtime evidence, not proof that auditor relaxation, chapter split, or prompt churn should be done in this gate.
- Ch3 retained evidence is `programmatic:C2` / `code_bug_other` under `prompt_contract` with `repair_budget_exhausted`. It is not proof that `must_not_cover` / `言行一致` is the root cause. A Ch3-only calibration gate must first determine whether the C2 rule, writer chapter-boundary behavior, or typed contract clause mapping is the root cause before deciding any contract-shape adjustment.
- Dayu remains architecture reference and capability source only; no production dependency on `dayu-agent`, `dayu.host`, or `dayu.engine` is allowed.

## Accepted Future Template Contract Inputs

These items are accepted future inputs from prior controller judgments, not current implementation facts:

| Input | Status | How this design consumes it |
|---|---|---|
| Typed `ChapterContract` | MVP accepted input | Agent runner receives contract identity and typed clauses from Fund; it does not parse natural-language template comments at runtime. |
| Public chapter ids `0-7` | MVP accepted input | Task graph uses body chapters `1-6`, final judgment `7`, and overview `0`; no `0+9`, `0+10`, or Ch2 public split. |
| Derived `EvidenceAvailability` | MVP accepted input | Fund precomputes availability from same-source `ChapterFactProjection` before the tool loop; Agent passes it as typed task/tool input. It is not a ToolRegistry tool. |
| Ch3 evidence-conditional `must_not_cover` | MVP accepted input | State machine treats it as typed programmatic contract input; implementation remains deferred to Ch3 calibration gate. |
| `RequiredOutputItem.when_evidence_missing` | MVP accepted input | Missing/degrade decisions are explicit writer/audit inputs and produce typed missing/degrade issues when violated. |
| Ch0 consumes Ch7 with fail-closed body readiness | MVP accepted input | Final assembly readiness blocks Ch7/Ch0 production until required body chapters are accepted. |
| Per-chapter `audit_focus` | MVP accepted input | Used only to focus bounded semantic audit and repair grouping; it cannot disable programmatic blockers. |
| Ch2 performance/attribution/cost as internal subcontracts only | MVP accepted input | Agent can trace Ch2 internal sub-requirements but must keep public chapter id `2`. |

Deferred or rejected inputs that this design must not implement:

- Ch3 calibration implementation is deferred to a Ch3-only gate.
- Provider runtime budget calibration is deferred.
- Multi-year annual evidence scope is deferred.
- `chapter_generation_score` / score-loop wiring is deferred.
- Ch2 split / `0+9` / public chapter count changes are deferred.
- Facet wiring / `first_class_facets` programmatic semantics are deferred.
- Raw multi-year PDF prompt injection is rejected for this gate.

## Proposed Agent Execution Design

This section is proposed future design. It is not current implementation fact.

### Design Principle

First principles boundary:

- Service owns the use case: user intent, report strategy, `ExecutionContract`, quality policy, provider construction for first MVP, and runtime ceilings.
- Host owns lifecycle only: run deadline, cancellation, terminal state, safe event delivery, and generic diagnostics.
- Agent owns execution mechanics: runner, task graph, tool loop, attempt state, retry/repair boundaries, budget accounting, `ToolRegistry`, `ToolTrace`, and final assembly readiness.
- Fund owns domain tools: chapter facts, template contracts, preferred_lens, ITEM_RULE, evidence availability, writer primitive, programmatic audit, bounded semantic audit adapter, and repair semantics.

### Runner And Task Graph

| Proposed object/state | Status | Purpose |
|---|---|---|
| `AgentReportRun` | Proposed future design | One Agent execution over a Service-declared report request and ceilings. |
| `ChapterTask` | Proposed future design | Single chapter execution unit with chapter id, dependencies, contract id, evidence availability, and attempt ledger. |
| `BodyChapterTask(1-6)` | Proposed future design | Independent body chapters; failure of one body chapter must not skip later independent body chapters. |
| `FinalJudgmentTask(7)` | Proposed future design | Runs only when all Service-required body chapters are accepted and final judgment inputs are complete. |
| `OverviewTask(0)` | Proposed future design | Runs after Ch7 and consumes Ch7 plus accepted body conclusions; does not derive a new judgment. |
| `FinalAssemblyReadiness` | Proposed future design | Typed readiness projection: `ready`, `incomplete`, or `blocked`, with missing accepted chapter ids and issue ids. |
| `FailClosedTerminalState` | Proposed future design | Run-level terminal state that blocks stdout report when required tasks are not accepted. |

Proposed task graph:

```text
project facts / availability
  -> ChapterTask[1], ChapterTask[2], ChapterTask[3], ChapterTask[4], ChapterTask[5], ChapterTask[6]
  -> FinalAssemblyReadiness(body chapters)
  -> ChapterTask[7] final judgment
  -> ChapterTask[0] overview
  -> report assembly readiness
```

Dependency rules:

- Body chapters 1-6 are independent unless a future accepted contract declares a typed dependency.
- The Agent task graph subsumes the current Service `ChapterOrchestrator.orchestrate_chapters()` behavior for chapters 1-6: independent chapter execution, per-chapter write/audit/repair loops, and fail-closed result aggregation.
- Ch7 depends on all Service-required body chapters being accepted plus existing final judgment policy inputs.
- Ch0 depends on accepted Ch7 and accepted body chapter conclusions.
- `FinalAssemblyReadiness` is fail-closed: any required body chapter not accepted, missing accepted draft, or missing accepted conclusion blocks Ch7/Ch0/full report assembly.
- Agent-owned `FinalAssemblyReadiness` should feed or replace the current Service `FinalChapterAssembler` readiness check only in a future implementation gate. Until that gate is accepted, Service stdout and fail-closed behavior stay unchanged, and the current Service assembler remains the final product boundary.
- The Agent may still return an incomplete diagnostic artifact to Service. The proposed typed `AgentRunResult` contains terminal state, per-chapter status matrix, per-chapter failure kinds, ToolTrace summary, and `FinalAssemblyReadiness`; Service maps that result to the existing incomplete artifact retention format while preserving empty stdout and no partial report behavior.
- Agent checks the Host cancel token and global deadline at task scheduling boundaries, before each `ChapterTask` dispatch, and after each tool-call return. Mid-tool-call interruption relies on provider client timeout rather than Agent polling.

Terminal states:

| Terminal state | Status | Meaning |
|---|---|---|
| `accepted` | Proposed future design | All required chapters, Ch7, Ch0, and report assembly readiness pass. |
| `partial_fail_closed` | Proposed future design | At least one required task failed or readiness is incomplete; no full report may be emitted. |
| `host_interrupted` | Proposed future design | Host cancellation or global deadline was observed; no full report may be emitted unless a later resume gate accepts durable partial continuation. |

First MVP intentionally keeps run terminal states simple. Detailed runtime, contract, semantic, missing-evidence, dependency, and repair-exhaustion classifications live at per-chapter / per-attempt level in `ToolTrace`, including mixed failures across attempts.

### ToolRegistry

The future `ToolRegistry` is Agent-owned as an execution registry, while the tool implementations are owned by Fund or Service as listed below. `EvidenceAvailability` is a precomputed derived input from `ChapterFactProjection` before the tool loop; it is not registered as a tool. ToolRegistry phasing is explicit: schema contracts in Slice A, fake-tool execution in Slice B, Fund wrapping in Slice C, migration in Slice D, and readiness integration in Slice E.

For the first Agent MVP, Service constructs writer/auditor Protocol clients and passes them to `AgentReportRun` as explicit typed per-run fields. Agent then passes those clients into Fund writer/auditor tools as typed tool inputs. Provider clients are not a registry tool, not a pseudo-tool, and not `extra_payload`.

| Tool | Status | Implementation owner | Registry owner | Allowed input | Allowed output |
|---|---|---|---|---|---|
| `fund.chapter_writer` | Proposed future design over current Fund primitive | Fund | Agent | `ChapterContract`, `ChapterFactProjection`, `EvidenceAvailability`, required output items, repair context, writer client, Service ceilings | `ChapterDraft`, writer runtime result, safe prompt-cost counters, writer issues |
| `fund.programmatic_audit` | Proposed future design over current Fund primitive | Fund | Agent | `AuditSubject`, draft, typed contract, evidence availability, allowed anchors/facts, ITEM_RULE decisions | deterministic `AuditResult`, stable issue ids, blocking/reviewable issues, repair hints |
| `fund.bounded_semantic_audit` | Proposed future design over current Fund primitive | Fund | Agent | Draft, allowed facts/anchors, data gaps, `audit_focus`, semantic auditor client, ceilings | semantic `AuditResult` or typed runtime failure; no override of programmatic blockers |
| `fund.repair_semantics` | Proposed future design | Fund | Agent | Prior issue ids, evidence availability, required missing/degrade rules, typed contract clauses | Issue-to-repair mapping and domain repair recommendation; tied issue ids |
| `agent.final_assembly_readiness` | Proposed future design | Agent, using Service policy and Fund domain result types | Agent | Chapter results, required chapter ids, accepted drafts/conclusions, Ch7/Ch0 dependencies | `FinalAssemblyReadiness` with missing chapter ids, issue ids, terminal recommendation |

Repair ownership split:

- Fund owns `RepairSemantics`: what an issue means, whether it is repairable, which clause/item/evidence state it is tied to, and the issue-to-repair-action mapping.
- Agent owns `RepairPolicy`: attempt counting, budget enforcement, remaining-ceiling checks, and the final stop-or-retry decision.

Tool constraints:

- Tools receive explicit typed parameters only; no `extra_payload`.
- Fund tools do not read annual-report files directly; production document access remains through `FundDocumentRepository` before projection.
- Host does not register tools and does not inspect tool inputs.
- Semantic audit tool cannot turn a programmatic failure into acceptance.
- Runtime failures are tool failures, not audit content issues.

### ToolTrace

| Trace field/schema | Status | Purpose |
|---|---|---|
| `schema_version="agent_tool_trace.v1"` | Proposed future design | Stable trace contract for safe diagnostics. |
| `run_id`, `task_id`, `chapter_id` | Proposed future design | Link trace entry to run and chapter. |
| `attempt_id` | Proposed future design | Stable id for each writer/audit/repair attempt, e.g. `ch03.attempt01`. |
| `tool_call_id` | Proposed future design | Stable id for each typed tool call. |
| `tool_name`, `tool_version` | Proposed future design | Identify registry entry without exposing implementation internals. |
| `phase` | Proposed future design | `task_prepare`, `write`, `programmatic_audit`, `semantic_audit`, `repair_plan`, `readiness`. |
| `input_metadata` | Proposed future design | Redacted scalar metadata: counts, ids, chars, token estimates; no prompt body or raw facts. |
| `output_metadata` | Proposed future design | Redacted scalar output metadata: status, response chars, accepted boolean, issue ids. |
| `issue_ids` | Proposed future design | Link trace entry to generated/consumed issues. |
| `runtime_failure` | Proposed future design | Timeout/rate limit/malformed/network/http/unavailable with safe class, no raw message unless allowlisted. |
| `budget_counters` | Proposed future design | Attempt count, max attempts, elapsed ms, timeout seconds, approx prompt tokens, output chars, repair budget spent. |
| `redaction_policy_id` | Proposed future design | Serializer allowlist policy identity. |
| `artifact_safe` | Proposed future design | Boolean indicating the entry is safe for local retained artifact serialization. |

Serialization safety:

- Serialized trace must be allowlist-first.
- Never serialize API key, Authorization header, cookies, provider config values, raw provider response, raw audit response, prompt body, draft body, repair draft body, full source fact text, or raw PDF text.
- Serialized trace may include stable ids, enum values, counts, safe categories, elapsed time, token/char estimates, and artifact-relative paths.
- `model_name` remains unsafe by default unless a later diagnostics gate explicitly allowlists it.
- Raw draft storage remains separate from trace and must follow the existing retained artifact policy; trace must be safe even if draft artifacts are absent.
- The phase list is MVP-complete for this design. Evidence Confirm remains a future phase and would add an `evidence_confirm` trace phase only after a separate Evidence Confirm gate.

### Tool-Loop State Machine

| State | Status | Owner | Transition |
|---|---|---|---|
| `TASK_READY` | Proposed future design | Agent | Contract, facts, availability, tools, and ceilings are validated. |
| `WRITE_DRAFT` | Proposed future design | Agent calls Fund writer | Writer returns draft or runtime/content failure. |
| `PROGRAMMATIC_AUDIT` | Proposed future design | Agent calls Fund audit | Runs before semantic audit; blocking deterministic issue goes to repair/stop. |
| `BOUNDED_SEMANTIC_AUDIT` | Proposed future design | Agent calls Fund semantic tool | First Agent MVP runs it only after programmatic audit has no blocking issue; diagnostic-only semantic audit is deferred to a post-MVP observability gate. |
| `PLAN_REPAIR` | Proposed future design | Agent with Fund repair semantics | Consumes issue ids, evidence availability, required missing/degrade rules, remaining budget. |
| `REGENERATE` | Proposed future design | Agent loops to writer | Uses typed repair context and increments attempt id. |
| `ACCEPT_CHAPTER` | Proposed future design | Agent | Programmatic and semantic requirements pass. |
| `STOP_FAIL_CLOSED` | Proposed future design | Agent | Runtime failure, blocker, missing evidence, repair exhausted, or dependency/readiness blocker. |

State machine:

```text
TASK_READY
  -> WRITE_DRAFT
  -> PROGRAMMATIC_AUDIT
     -> PLAN_REPAIR -> REGENERATE -> WRITE_DRAFT
     -> PLAN_REPAIR -> STOP_FAIL_CLOSED  # repair budget exhausted or planner stop
     -> STOP_FAIL_CLOSED
  -> BOUNDED_SEMANTIC_AUDIT
     -> PLAN_REPAIR -> REGENERATE -> WRITE_DRAFT
     -> PLAN_REPAIR -> STOP_FAIL_CLOSED  # repair budget exhausted or planner stop
     -> STOP_FAIL_CLOSED
  -> ACCEPT_CHAPTER
```

Typed inputs consumed by the loop:

- `ChapterContract`: gives clause ids, required output ids, `must_not_cover`, `preferred_lens`, `audit_focus`, and dependencies.
- `EvidenceAvailability`: tells whether each requirement is available, missing, unreviewed, not applicable, or degraded.
- `RequiredOutputItem.when_evidence_missing`: tells whether writer must render insufficiency, delete an inapplicable item, or emit next validation question.
- `audit_focus`: limits bounded semantic audit questions and repair grouping only; programmatic blockers are independent of it.
- Ch0/Ch7 dependency: Ch7 cannot run until required body readiness passes; Ch0 cannot run until Ch7 is accepted.

Missing/degrade handling:

- Missing required evidence is not automatically a runtime failure.
- If the contract allows degrade, writer must render the specified insufficiency or next validation question.
- If the contract requires evidence and no degrade path exists, Agent stops with `missing_evidence_blocker`.
- If writer makes a positive or quasi-positive claim where only degraded wording is allowed, programmatic audit emits a deterministic blocker tied to clause/item ids.

### Budget, Retry, And Repair Boundaries

| Budget boundary | Status | Owner |
|---|---|---|
| Provider config parsing and client construction | MVP accepted input for first Agent MVP | Service |
| Runtime ceilings declaration | MVP accepted input | Service |
| Global run deadline and cancel | Current fact / unchanged | Host |
| Per-tool attempt spending | Proposed future design | Agent |
| Context/token/char budget accounting | Proposed future design | Agent |
| Repair decision within ceilings | Proposed future design | Agent, using Fund `RepairSemantics` |
| Raising timeout, attempts, or output limits | Deferred | Separate provider/runtime budget gate |

Rules:

- Service declares ceilings: target chapter ids, max repair attempts, writer/auditor timeout ceilings, provider max attempts, max output chars, semantic audit enablement, and safe diagnostic policy.
- Agent may spend within those ceilings and must trace every spend.
- Agent cannot silently raise budgets, change provider retry policy, or reinterpret a runtime timeout as a successful semantic audit.
- Host only enforces lifecycle/deadline/cancel and does not inspect chapter policy, provider clients, or fund business fields.
- Repair exhaustion must record remaining budget, consumed attempts, issue ids, and last failure kind.
- Cancellation/deadline checks are observable at Agent scheduling boundaries and after tool returns; blocking provider calls rely on per-client timeout and then re-check Host state on return.

### Failure Taxonomy

| Failure kind | Status | Layer | Examples / required trace |
|---|---|---|---|
| `provider_runtime_timeout` | Proposed future design | Tool runtime | Writer/auditor timeout; trace timeout seconds, max attempts, elapsed ms, tool name. |
| `provider_runtime_rate_limit` | Proposed future design | Tool runtime | Rate limit; no content repair. |
| `provider_runtime_malformed` | Proposed future design | Tool runtime | Provider or auditor protocol malformed. |
| `programmatic_contract_blocker` | Proposed future design | Fund programmatic audit | C2, L1, required output, ITEM_RULE, anchor marker, missing/degrade violation. |
| `semantic_blocker` | Proposed future design | Bounded semantic audit | Unsupported interpretation, contradiction, unsafe wording after deterministic checks pass. |
| `missing_evidence_degrade_violation` | Proposed future design | Contract/audit | Evidence missing but writer omitted required insufficiency or made positive claim. |
| `missing_evidence_blocker` | Proposed future design | Contract/readiness | Required evidence absent and no accepted degrade path. |
| `repair_exhausted` | Proposed future design | Agent loop | Remaining repair budget zero; must cite attempt ids and issue ids. |
| `dependency_readiness_incomplete` | Proposed future design | Agent readiness | Ch7/Ch0/report assembly blocked by missing accepted body chapter draft/conclusion. |
| `host_cancelled` | Current Host concept / proposed Agent observation | Host lifecycle | Cancel token observed. |
| `host_deadline_exceeded` | Current Host concept / proposed Agent observation | Host lifecycle | Global deadline exceeded. |

The taxonomy must keep runtime failures, deterministic content failures, semantic blockers, missing evidence/degrade failures, repair exhaustion, and dependency readiness failures separate.

## Boundary Mapping

| Layer | Ownership in this proposed future design | Must not do |
|---|---|---|
| UI | opt-in flags, display, stdout/stderr behavior | no Agent internals, no tool registry, no audit semantics |
| Service | use case, scene/report strategy, `ExecutionContract`, quality policy, provider construction for first Agent MVP, runtime ceilings, final product fail-closed mapping | no runner/tool-loop, no per-attempt repair engine, no `ToolTrace` ownership, no Fund audit implementation |
| Host | run lifecycle, global deadline, cancel, terminal state, safe events/diagnostics | no fund semantics, no provider clients, no tool loop, no prompt or audit policy |
| Agent | runner, task graph, tool loop, ToolRegistry, ToolTrace, attempt ids, retry/repair spending, final assembly readiness | no UI rendering, no Service use-case selection, no Host lifecycle implementation, no direct dayu runtime dependency |
| Fund | facts, `ChapterContract`, `EvidenceAvailability`, preferred_lens, ITEM_RULE, writer, programmatic audit, bounded semantic audit adapter, repair semantics | no generic run lifecycle, no Service report strategy, no direct repository/PDF/cache/source helper access from tools |

Dayu mapping:

- Internalize Dayu Engine-style capabilities only as local project contracts: runner, tool loop, ToolRegistry, ToolTrace, context budget, typed tool execution contract, and event semantics.
- Do not add `dayu-agent`, `dayu.engine`, or `dayu.host` as production runtime dependency.
- Do not copy or rewrite upstream Dayu code before a separate license/compliance gate.

## Non-Goals

- No code, tests, config, prompt, provider, auditor, renderer, quality gate, golden, score, report, or retained-artifact changes.
- No update to design/control/startup truth docs.
- No current-fact statement that Agent runner/tool-loop is implemented.
- No Ch3 calibration implementation.
- No provider runtime budget tuning.
- No multi-year annual evidence implementation.
- No score-loop wiring.
- No Ch2 split or `0+9` / `0+10` public chapter structure.
- No facet wiring implementation.
- No auditor relaxation.
- No deterministic fallback.
- No stdout partial report.
- No incomplete LLM deterministic fallback.
- No change to deterministic `analyze/checklist` default.

## Residual Risks And Open Questions

| Risk / question | Status | Owner / next destination |
|---|---|---|
| Exact schema implementation form for Agent contracts | Open | Future implementation planning gate; choose dataclass/Protocol/JSON serialization boundary. |
| Programmatic `allowed_contexts` and Chinese polarity/quasi-positive detection | Deferred | Ch3-only calibration or typed contract schema gate before implementation. |
| Provider runtime timeouts may still block semantic audit after Agent migration | Open | Provider runtime budget calibration gate. |
| Trace serializer may accidentally include prompts/drafts/raw provider responses | Open | Implementation gate must include allowlist serializer tests, diff-safe fixture assertions, and secret scan. |
| ToolRegistry wiring and schemas | Open | Slice A must define registry schema contracts, typed call/result envelopes, versioning, and dependency injection shape before Fund tools are wrapped. |
| Evidence Confirm relationship to bounded semantic audit | Deferred | Evidence Confirm gate; MVP uses `evidence_confirm_deferred`; no `evidence_confirm` trace phase in first Agent MVP. |
| Ch2 internal subcontracts without public split | Open | Future typed contract implementation plan must keep chapter id `2` while tracing optional sub-requirement ids such as performance, attribution, and cost for issue targeting. |
| Final assembly readiness and current Service final assembler migration | Open | Future Agent implementation gate must decide whether Agent readiness feeds or replaces Service `FinalChapterAssembler`; stdout/fail-closed behavior must remain unchanged until accepted. |
| Ch3 same-source root cause | Deferred | Ch3-only calibration must first decide whether C2 rule, writer boundary, or typed contract clause mapping is root cause. |

## Acceptance Criteria

This design artifact should be acceptable for review if:

- It starts with worker self-check and stays under `docs/reviews/`.
- It separates current facts, accepted future inputs, proposed design, non-goals, residual risks/open questions, acceptance criteria, and next gate handoff.
- Every proposed schema/state/tool is marked as MVP accepted input, proposed future design, current fact, or deferred.
- It preserves UI/Service/Host/Agent/Fund boundaries from `AGENTS.md`.
- It keeps deterministic `analyze/checklist` default and current `--use-llm` fail-closed behavior unchanged.
- It does not authorize implementation, provider budget changes, auditor relaxation, Ch3 calibration, Ch2 split, score-loop, golden/readiness, or report stdout changes.
- It provides enough detail for a later planning gate to define Agent-owned runner/tool-loop/ToolTrace work without inventing ownership.

## Next Gate Handoff

Recommended next controller action:

1. Send this artifact to independent design review.
2. If accepted, write a controller judgment that records accepted/rejected/deferred parts explicitly.
3. Only after accepted review, open a separate implementation planning gate for `internalized Agent engine/tool-loop MVP`.

Suggested future implementation-planning slices, not authorized by this artifact:

| Slice | Status | Scope |
|---|---|---|
| Slice A: Agent execution/audit schema plan | Deferred | Define local Agent contract schemas, attempt ids, issue ids, trace serializer allowlist tests, and ToolRegistry schema contracts without runtime migration or Fund tool wrapping. |
| Slice B: Agent runner with fake tools | Deferred | Prove task graph and state machine using fake writer/auditor tools and no provider construction changes. |
| Slice C: Wrap Fund writer/programmatic/semantic tools | Deferred | Register typed Fund tools and Fund repair semantics, with `EvidenceAvailability` supplied as precomputed input while Service still owns provider construction and ceilings. |
| Slice D: Migrate Service `ChapterOrchestrator` execution mechanics | Deferred | Move write-audit-repair mechanics for chapters 1-6 to Agent while preserving Service use case, independent chapter behavior, and fail-closed result mapping. |
| Slice E: Final assembly readiness integration | Deferred | Feed or replace current Service readiness checking with Agent `FinalAssemblyReadiness` without changing report stdout, deterministic default, or fail-closed semantics. |

Must remain separate gates:

- Ch3 calibration implementation.
- Provider runtime budget calibration.
- Multi-year annual evidence scope.
- `chapter_generation_score` / score-loop.
- Ch2 structural split / `0+9`.
- Facet wiring.
- Durable Host session/resume/memory/reply outbox.

## Validation Command And Result

Validation performed for this design worker output:

- Command: `python -m json.tool reports/llm-runs/006597-2024-20260602T121553Z-host_run_1f8d428509c5431/summary.json >/dev/null && test -f docs/reviews/mvp-internalized-agent-engine-tool-loop-contract-execution-design-20260603.md`
- Result: pass.

## Secret-Safety Statement

This artifact contains no API key, Authorization header, Bearer token, cookie, password, raw provider response, raw audit response, prompt body, writer draft body, repair draft body, hidden provider config value, or raw PDF/source text. It references only safe artifact paths, schema/status names, enum labels, counts, and high-level diagnostic categories.
