# MVP Agent Engine Design Slice A Dataclass Design Plan

## 1. Gate Role

Role: `planning worker`.

This artifact opens Slice A under the accepted `Agent Engine Design Refresh Gate`.
It is a design-only plan for future Agent engine dataclasses. It does not
authorize implementation, source edits, tests, provider calls or runtime changes.

Accepted parent artifacts:

- `docs/reviews/mvp-agent-engine-design-refresh-gate-plan-20260607.md`
- `docs/reviews/mvp-agent-engine-design-refresh-gate-plan-review-ds-20260607.md`
- `docs/reviews/mvp-agent-engine-design-refresh-gate-plan-controller-judgment-20260607.md`

## 2. Objective

Define the future Agent-engine state model that can subsume the current Service
`ChapterOrchestrator` write-audit-repair loop without weakening current
fail-closed behavior.

The Slice A design must be precise enough for a later implementation planning
gate to generate code without redesigning:

- `AgentReportRun`
- `ChapterTask`
- `ChapterAttempt`
- `AgentRepairPolicy`
- `ToolCallRequest`
- `ToolCallResult`
- `ToolTrace`
- `FinalAssemblyReadiness`

## 3. Current Facts

Current code facts from `fund_agent/services/chapter_orchestrator.py`:

- `ChapterOrchestrationInput` receives either a `StructuredFundDataBundle` or a
  `ChapterFactProjection`.
- `ChapterOrchestrationPolicy` owns target chapter ids, repair attempts, output
  chars, prompt payload mode, audit toggles and typed template path.
- `_TypedTemplateInputs` currently derives a single same-source
  `EvidenceAvailability` from the `ChapterFactProjection`.
- `_run_single_chapter()` builds writer input once before attempt 0 and rebuilds
  it only for repair attempts with `ChapterRepairContext`.
- Each chapter produces `ChapterRunResult` with `status`, `stop_reason`,
  accepted draft/conclusion, attempt records, issue text, failure category,
  failure subcategory and safe diagnostics.
- `ChapterOrchestrationResult` aggregates projection, chapter results,
  accepted conclusions, blocked reasons, generated ids and skipped ids.

Current code facts from `fund_agent/services/final_chapter_assembler.py`:

- `FinalAssemblyPolicy` controls required body chapters and fail-closed total
  assembly behavior.
- `FinalAssemblyReadiness` checks required body chapters, accepted body chapters,
  chapter 7 readiness and blocking issues.
- `FinalChapterAssemblyResult` is Service-owned and controls whether complete
  report markdown exists.

Current accepted boundary facts:

- Service owns use case, `FundLLMExecutionContract`, provider construction,
  provider runtime ceilings, quality policy and final product fail-closed
  mapping.
- Host owns lifecycle only and must remain business-opaque.
- Fund owns CHAPTER_CONTRACT, preferred_lens, ITEM_RULE, writer/auditor
  contracts, programmatic audit, bounded semantic audit, issue ids,
  repair hints and evidence anchor semantics.
- Future Agent owns execution mechanics only after a separate implementation
  gate.

## 4. Non-Goals

This Slice A plan forbids:

- creating `fund_agent/agent`;
- implementing Agent dataclasses;
- moving `ChapterOrchestrator` code;
- changing `FundLLMExecutionContract` or provider construction;
- changing timeout, retry, provider, default model, base URL or budget behavior;
- running live `--use-llm`, retry, curl, DNS, socket or endpoint probes;
- introducing `dayu-agent`, `dayu.host`, `dayu.engine`, LangGraph or MCP runtime;
- changing quality gate, golden/readiness, score-loop, multi-year runtime,
  public chapter ids `0-7`, stdout semantics or final judgment semantics;
- copying or rewriting upstream Dayu code;
- PR, push, merge, mark-ready, reviewer request or external comment.

## 5. Slice A Design Decisions

### 5.1 AgentReportRun

Future purpose: one Agent-owned execution record for one explicit LLM report run.
It replaces only the execution mechanics currently inside Service
`ChapterOrchestrator`; it does not replace Service use-case ownership or final
product policy.

Required fields:

- `schema_version`: `agent_report_run.v1`.
- `run_id`: Agent-local stable id, not a Host session id.
- `fund_code` and `report_year`: copied from Service request for same-run
  identity checks only.
- `target_chapter_ids`: body chapters, default equivalent to current `(1,2,3,4,5,6)`.
- `status`: `accepted`, `partial_fail_closed`, `host_interrupted`.
- `chapter_tasks`: tuple of `ChapterTask` in execution order.
- `projection`: same `ChapterFactProjection` object/value used for all tasks.
- `evidence_availability`: same-source `EvidenceAvailability` derived once from
  the run projection before any chapter task is prepared.
- `repair_policy`: `AgentRepairPolicy`.
- `final_assembly_readiness`: Agent-level body readiness matrix.
- `blocked_reasons`: run-level safe reasons only.

Boundary:

- It may carry Service-constructed writer/auditor clients as explicit typed
  per-run fields in later implementation design, but these clients are not
  ToolRegistry tools and are not serialized into traces.
- It must not carry `extra_payload`, raw prompts, raw provider responses, API
  keys, Authorization headers, model values or base URL values.

Mapping to current state:

- `ChapterOrchestrationResult.status=accepted` maps to
  `AgentReportRun.status=accepted` only when all required `ChapterTask.status`
  are accepted and Agent `FinalAssemblyReadiness.status=ready`.
- `ChapterOrchestrationResult.status=partial` or `blocked` maps to
  `partial_fail_closed` unless Host cancel/deadline caused interruption.
- `projection`, `chapter_results`, `accepted_conclusions`,
  `blocked_reasons`, `generated_chapter_ids` and `skipped_chapter_ids` remain
  reconstructable from `AgentReportRun`.

### 5.2 EvidenceAvailability Invocation Point

Accepted parent finding NBO-1 is resolved here:

- Agent derives `EvidenceAvailability` exactly once after `ChapterFactProjection`
  is available and before the first `ChapterTask` enters `prepared`.
- The derived value is stored on `AgentReportRun.evidence_availability`.
- Every `ChapterTask` receives the same object/value by reference or immutable
  copy.
- Repair attempts must reuse the run-level value. They must not recompute
  availability, read retained artifacts, read filesystem state or query external
  state.
- If future multi-year evidence changes projection shape, that requires a
  separate implementation gate before this invocation point can change.

### 5.3 ChapterTask

Future purpose: Agent-owned state for one template body chapter.

Required fields:

- `schema_version`: `agent_chapter_task.v1`.
- `chapter_id` and `title`.
- `status`: `pending`, `prepared`, `running`, `accepted`, `blocked`, `failed`,
  `skipped`.
- `stop_reason`: current `ChapterRunStopReason` compatible value set.
- `writer_input_identity`: safe identity of the Fund writer input, such as
  chapter id, fund code, report year, typed template path and requirement ids;
  no prompt text.
- `attempts`: tuple of `ChapterAttempt`.
- `accepted_draft`: current `ChapterDraft | None`.
- `accepted_conclusion`: current `AcceptedChapterConclusion | None`.
- `issues`: safe issue messages or ids.
- `failure_category` and `failure_subcategory`: current category-compatible
  values.
- `tool_traces`: tuple of `ToolTrace` for writer, audit and repair-related tool
  calls.

State rules:

- Body chapters 1-6 run independently from the same projection and same
  run-level evidence availability.
- Prior body chapter failure must not skip later body chapters.
- `dependency_missing` remains reserved for a true dependency stop reason, not
  ordinary previous chapter failure.
- `skipped` is legal only for explicit scope exclusion or true global dependency
  stop.

Mapping to current state:

- `ChapterRunResult.chapter_id`, `title`, `status`, `stop_reason`,
  `accepted_draft`, `accepted_conclusion`, `attempts`, `issues`,
  `failure_category`, `failure_subcategory`, prompt diagnostics and runtime
  diagnostics map into `ChapterTask`.

### 5.4 ChapterAttempt

Future purpose: one write/audit/repair attempt ledger row.

Required fields:

- `schema_version`: `agent_chapter_attempt.v1`.
- `chapter_id`.
- `attempt_index`: current zero-based index.
- `phase_status`: `writer_blocked`, `audit_accepted`, `audit_blocked`,
  `repair_scheduled`, `runtime_failed`.
- `writer_result`: current `ChapterWriteResult`.
- `audit_result`: current `ChapterAuditResult | None`.
- `repair_decision`: Agent-owned decision projected from Fund issue ids and
  repair hints.
- `runtime_diagnostics`: safe scalar runtime diagnostics.
- `tool_trace_ids`: trace ids attached to this attempt.

Mapping to current state:

- Current `ChapterAttemptRecord` maps one-to-one to future `ChapterAttempt`.
- Writer-blocked attempts keep `audit_result=None`.
- Provider exceptions that currently produce `_exception_result()` map to a
  `runtime_failed` attempt when they occur after an attempt has a writer result,
  or to chapter-level task failure diagnostics when no attempt result exists.

### 5.5 AgentRepairPolicy

Future purpose: Agent-owned bounded repair decision policy.

Required fields:

- `schema_version`: `agent_repair_policy.v1`.
- `max_repair_attempts`: equivalent to current
  `ChapterOrchestrationPolicy.max_repair_attempts`.
- `repairable_hints`: Fund-owned hints that may trigger regenerate.
- `terminal_hints`: Fund-owned hints that must stop.
- `runtime_retry_allowed`: `false` for Agent-level repair. Provider timeout
  retry remains Service/provider client runtime behavior.
- `hidden_retry_allowed`: `false`.

Decision rules:

- Agent consumes Fund `ChapterAuditRepairHint` and issue ids.
- Agent may choose `regenerate`, `needs_more_facts` or `stop`.
- Agent must not redefine Fund issue meaning.
- Repair exhaustion maps to `repair_budget_exhausted`.
- Runtime failures are not content repair attempts.

Mapping to current state:

- Current `ChapterRepairDecision` maps to the future policy decision output.
- Current bounded regenerate behavior remains unchanged.

### 5.6 ToolCallRequest

Future purpose: typed Agent-to-Fund tool invocation request.

Required fields:

- `schema_version`: `agent_tool_call_request.v1`.
- `trace_id`.
- `tool_name`: initially one of `fund.project_chapter_facts`,
  `fund.write_chapter`, `fund.audit_programmatic`, `fund.audit_semantic`.
- `chapter_id`: optional for run-level projection, required for chapter tools.
- `attempt_index`: optional for projection, required for writer/auditor tools.
- `input_kind`: safe typed input label.
- `input_identity`: safe ids and scalar counts only.
- `deadline_observed`: whether Host deadline/cancel was checked before call.

Forbidden fields:

- prompt text;
- draft markdown in serialized trace identity;
- raw provider response;
- raw audit response;
- API key, bearer token, Authorization header;
- model value or base URL value.

### 5.7 ToolCallResult

Future purpose: typed result envelope for Agent tool calls.

Required fields:

- `schema_version`: `agent_tool_call_result.v1`.
- `trace_id`.
- `status`: `succeeded`, `blocked`, `failed`, `host_interrupted`.
- `output_kind`: safe typed output label.
- `output_identity`: safe ids, status, issue counts, anchor counts and scalar
  diagnostics only.
- `failure_category`: runtime/content/dependency category when failed.
- `safe_message`: optional redacted message.

Boundary:

- The in-memory Agent may receive full Fund result objects for continued
  execution.
- The serialized trace form must stay safe and must not store raw prompt,
  draft, raw provider response or secrets.

### 5.8 ToolTrace

Future purpose: safe per-tool trace row for Agent execution evidence.

Required fields:

- `schema_version`: `agent_tool_trace.v1`.
- `trace_id`.
- `run_id`, `chapter_id`, `attempt_index`.
- `tool_name`.
- `phase`: `projection`, `writer`, `programmatic_audit`, `semantic_audit`,
  `repair_decision`.
- `status`.
- `started_order` and `completed_order`: monotonic ordering counters, not wall
  clock source of truth.
- `safe_input_identity`.
- `safe_output_identity`.
- `runtime_category`: current provider runtime category-compatible scalar when
  applicable.
- `diagnostic_consistency_status`: current diagnostic consistency-compatible
  scalar when applicable.

Trace safety:

- May include ids, counts, categories, char counts, approximate prompt token
  counts already allowed by current safe diagnostics.
- Must not include prompt, draft, raw provider response, raw audit response,
  API key, Authorization header, bearer token, model value or base URL value.

### 5.9 FinalAssemblyReadiness

Accepted parent finding NBO-3 is resolved for Slice A:

- Agent `FinalAssemblyReadiness` is a body-readiness handoff, not a replacement
  for current Service `FinalChapterAssembler`.
- It feeds Service final assembly by exposing required body ids, accepted body
  ids, blocking body issues and source accepted conclusion ids.
- Service keeps final product fail-closed mapping, chapter 0/7 assembly,
  stdout/stderr behavior and quality policy until a later implementation gate
  explicitly changes them.

Required fields:

- `schema_version`: `agent_final_assembly_readiness.v1`.
- `status`: `ready`, `blocked`.
- `required_body_chapter_ids`.
- `accepted_body_chapter_ids`.
- `source_accepted_conclusion_ids` or equivalent chapter ids.
- `blocking_issue_ids`.
- `body_task_status_matrix`.

Mapping to current state:

- Current Service `FinalAssemblyReadiness` remains authoritative for final
  report acceptance.
- Future Agent readiness must be at least as strict as current required-body
  accepted draft plus accepted conclusion checks.

## 6. Current-to-Future Mapping Matrix

| Current Service/Fund type | Future Agent design type | Mapping requirement |
|---|---|---|
| `ChapterOrchestrationInput` | `AgentReportRun` initialization input | Identity, target chapters, projection input and policy remain explicit |
| `_TypedTemplateInputs.evidence_availability` | `AgentReportRun.evidence_availability` | Derived once before task preparation and reused for all attempts |
| `ChapterOrchestrationPolicy.max_repair_attempts` | `AgentRepairPolicy.max_repair_attempts` | Same bounded repair budget |
| `ChapterAttemptRecord` | `ChapterAttempt` | One-to-one attempt ledger mapping |
| `ChapterRunResult` | `ChapterTask` | Preserve status, stop reason, accepted outputs, issues and diagnostics |
| `ChapterOrchestrationResult` | `AgentReportRun` plus reconstructed Service result | Preserve accepted/partial/fail-closed matrix |
| `ChapterRepairDecision` | `AgentRepairPolicy` decision output | Agent decides stop/regenerate but does not redefine Fund semantics |
| writer/auditor calls | `ToolCallRequest` / `ToolCallResult` / `ToolTrace` | Trace safe ids/categories only |
| Service `FinalAssemblyReadiness` | Agent body-readiness handoff | Agent feeds, Service remains final authority |

## 7. Validation Plan

This design-only Slice A validates by artifact review and local formatting only.

Required local command:

```text
git diff --check -- docs/reviews/mvp-agent-engine-design-slice-a-dataclass-design-plan-20260608.md
```

Expected result:

- exit code `0`;
- no whitespace errors.

No source tests are required because this artifact does not edit source or tests.

Forbidden validation:

- no `uv run fund-analysis analyze --use-llm`;
- no provider readiness check;
- no endpoint/DNS/curl/socket probe;
- no test that constructs a real provider or hits network;
- no implementation scaffold.

## 8. Review Route

Because AgentMiMo is unavailable, the reviewer route may use `pro-codex` as the
second independent reviewer if available.

Minimum review expectations:

- check Service/Host/Agent/Fund ownership;
- check NBO-1 EvidenceAvailability invocation point;
- check NBO-3 final readiness handoff;
- check mapping from current Service result types to future Agent types;
- check trace safety;
- check that no implementation or live/provider scope is authorized.

Acceptable outcomes:

- `PASS`;
- `PASS_WITH_NON_BLOCKING_OBSERVATIONS`;
- `BLOCKED_BY_SCOPE_OVERREACH`;
- `BLOCKED_BY_UNRESOLVED_CONTRACT`.

## 9. Stop Conditions

Stop or return to controller judgment if:

- reviewer finds this plan authorizes implementation;
- reviewer finds provider construction moved into Agent;
- reviewer finds Host receives business semantics;
- reviewer finds `EvidenceAvailability` can drift across repair attempts;
- reviewer finds Agent final readiness replaces Service final fail-closed mapping
  without a later implementation gate;
- local validation fails;
- user redirects to live evidence or Agent runtime implementation.

MiMo absence alone is not a stop condition after operator authorization to use
available Codex reviewer capacity.

## 10. Completion Report Format

Planning worker should report:

- artifact path;
- parent artifacts read;
- validation command and result;
- review route used;
- blocking findings, if any;
- whether the artifact is ready for controller judgment.
