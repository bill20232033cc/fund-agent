# MVP Agent Engine Design Refresh Gate Plan

## 1. Phase Objective

Prepare a design/plan gate for the future internalized Agent engine without implementing it.

The objective is to turn the accepted `LLM Tool Calling And State Machine Calibration Spike` into a bounded Agent-engine migration plan that preserves current report generation safety:

- Service keeps use case, ExecutionContract, provider construction, runtime ceilings, quality policy and final product fail-closed mapping.
- Host stays lifecycle-only.
- Agent will later own execution mechanics: chapter task graph, attempt ledger, repair policy execution, ToolRegistry calls, ToolTrace and readiness matrix.
- Fund keeps domain rules and tools: CHAPTER_CONTRACT, preferred_lens, ITEM_RULE, same-source `EvidenceAvailability`, writer/auditor contracts, programmatic-first audit and evidence anchors.

This plan is design-only. It does not authorize source/test/runtime implementation.

## 2. Non-Goals

Forbidden in this gate:

- no Agent runtime implementation;
- no `fund_agent/agent` package creation;
- no ToolRegistry code;
- no ToolTrace schema code;
- no migration of current Service `ChapterOrchestrator`;
- no provider/default/runtime/budget/config change;
- no live LLM command, retry, endpoint probe, curl, DNS or socket probe;
- no LangGraph;
- no MCP runtime;
- no `dayu-agent`, `dayu.host` or `dayu.engine` production dependency;
- no copy/rewrite of upstream Dayu code;
- no quality gate, golden/readiness, score-loop, multi-year runtime or public chapter ids `0-7` change;
- no PR, push, merge, mark ready, reviewer request or external comment.

## 3. State Ownership

### Service

Service must continue to own:

- user use case and explicit `--use-llm` opt-in;
- `FundLLMExecutionContract` and normalized business request;
- provider config parsing and first-MVP provider construction;
- provider runtime ceilings as typed inputs;
- report strategy and final product fail-closed mapping;
- CLI/user-facing stdout/stderr semantics;
- quality policy selection.

Service may pass an Agent run request, but must not hide business parameters in `extra_payload`.

### Host

Host must continue to own only lifecycle capabilities:

- run lifecycle;
- global deadline and cancellation;
- terminal state;
- safe diagnostics;
- future event/outbox/session/resume/memory capabilities.

Host must not inspect fund code, chapter ids, `FundLLMExecutionContract` business fields, provider clients, CHAPTER_CONTRACT, ITEM_RULE or audit results.

### Agent

Future Agent engine should own:

- `AgentReportRun` state;
- `ChapterTask` state for chapters 1-6;
- task graph sequencing;
- attempt ledger;
- repair policy execution;
- ToolRegistry invocation;
- ToolTrace construction;
- context/tool budget accounting at Agent level;
- final body chapter readiness matrix.

Agent should observe Host cancel/deadline at scheduling boundaries and after tool-call return. Mid-tool interruption remains provider timeout/client responsibility.

### Fund

Fund remains the Agent-layer domain package and owns:

- fund type recognition and preferred_lens;
- CHAPTER_CONTRACT and ITEM_RULE semantics;
- `ChapterFactProjection`;
- same-source `EvidenceAvailability`;
- writer input/output parser and exact marker contract;
- programmatic audit;
- bounded semantic LLM audit adapter;
- issue ids, repair hints and issue-to-repair semantics;
- evidence anchor validity.

## 4. Tool Boundary

The first Agent ToolRegistry must wrap existing Fund primitives, not rewrite them.

Initial tool candidates:

| Tool | Existing primitive | Boundary rule |
|---|---|---|
| `fund.project_chapter_facts` | `project_chapter_facts()` | Pure Fund projection from in-memory bundle; no repository/PDF/source helper access |
| `fund.derive_evidence_availability` | `derive_evidence_availability()` | Same-source derived input only; no retained artifact or filesystem lookup |
| `fund.write_chapter` | `write_chapter()` | Explicit writer client passed as typed per-run input |
| `fund.audit_programmatic` | `audit_chapter_programmatic()` | Deterministic, always first-class |
| `fund.audit_semantic` | `audit_chapter_llm()` | Bounded semantic audit only, explicit auditor client |

Provider writer/auditor clients are not tools. They are Service-constructed typed per-run fields carried into Agent and then passed to Fund tools.

`repair_hint` and issue ids remain Fund output semantics. Agent `RepairPolicy.decide` consumes them but must not redefine Fund rules.

## 5. Fail-Closed Invariants

The design must preserve:

- exact `required_output`, `anchor` and `missing` marker parsing;
- unknown anchor fail-closed behavior;
- required-output marker fail-closed behavior;
- writer structure fail-closed behavior;
- overlong/incomplete/content-filter writer output fail-closed behavior;
- programmatic audit before semantic audit;
- audit line protocol parse failure as blocking;
- bounded repair attempts only;
- separate runtime vs content failure categories;
- no deterministic fallback on LLM failure;
- no partial report stdout on failed final assembly;
- final report acceptance only after body readiness and final assembly readiness;
- safe diagnostics only: no raw prompt, draft, raw provider response, raw audit response, API key, Authorization header, bearer token, model value or base URL value.

## 6. Migration Slices

### Slice A: Agent Dataclass Design

Design only:

- `AgentReportRun`
- `ChapterTask`
- `ChapterAttempt`
- `AgentRepairPolicy`
- `ToolCallRequest`
- `ToolCallResult`
- `ToolTrace`
- `FinalAssemblyReadiness`

Acceptance requires explicit mapping from current `ChapterOrchestrationResult` / `ChapterRunResult` / `ChapterAttemptRecord` to future Agent state.

### Slice B: Tool Adapter Contract

Design only:

- typed wrappers for Fund primitives;
- tool input/output schema;
- error taxonomy;
- safe trace serialization fields;
- no provider client as registry tool.

### Slice C: Repair And Budget Contract

Design only:

- distinguish Service provider runtime ceilings from Agent repair attempts;
- define how Fund `repair_hint` and issue ids feed Agent repair policy;
- define repair exhaustion terminal states;
- preserve bounded repair and no hidden retries.

### Slice D: No-Live Equivalence Validation Plan

Design only:

- deterministic fake writer/auditor equivalence tests against current Service `ChapterOrchestrator`;
- accepted/partial/fail-closed matrix comparison;
- ToolTrace safe scalar assertion;
- no provider/network/live command.

### Slice E: Implementation Planning Gate

Only after Slices A-D are reviewed and accepted, write a separate implementation plan. Implementation remains forbidden until that plan has review and controller judgment.

## 7. Validation Matrix

| Requirement | Evidence / command | Blocking failure |
|---|---|---|
| Current/future distinction | plan text references current Service façade as current fact and Agent as future | Agent runtime written as current fact |
| Four-layer ownership | Service/Host/Agent/Fund section present | Host receives business state or Fund logic moves to Service |
| Tool wrapping | tool table maps to existing Fund primitives | Fund logic rewritten in Agent |
| Provider boundary | provider clients are explicit per-run inputs, not tools | provider construction moves into Agent |
| Fail-closed invariants | invariant checklist present | any invariant relaxed |
| Dayu boundary | explicit reference-only statement | dayu-agent/dayu.host/dayu.engine dependency allowed |
| No-live scope | validation commands are read-only/local | live/provider/network command required |
| Stop conditions | implementation forbidden until separate gate | plan authorizes implementation directly |

Local validation for this plan:

```text
git diff --check -- docs/reviews/mvp-agent-engine-design-refresh-gate-plan-20260607.md
```

No source/test/runtime validation is required because this is a docs/reviews-only design plan.

## 8. Review Requirements

Tonight reviewer route:

- AgentDS review only is acceptable under operator instruction because AgentMiMo has network/API failure and the gate is docs/reviews-only.

Review focus:

- state ownership;
- tool boundary;
- fail-closed invariants;
- migration slice sequencing;
- overreach into implementation;
- Dayu/LangGraph/MCP forbidden runtime boundary.

Required review artifact:

- `docs/reviews/mvp-agent-engine-design-refresh-gate-plan-review-ds-20260607.md`

## 9. Stop Conditions

Stop immediately if:

- the plan requires source/test/runtime edits;
- the plan introduces `dayu-agent`, `dayu.host`, `dayu.engine`, LangGraph or MCP runtime;
- the plan moves provider construction into Agent;
- the plan weakens fail-closed chapter acceptance or quality gate semantics;
- reviewer DS is unavailable or blocked;
- validation finds formatting errors;
- user asks to resume live evidence instead.

## 10. Next Entry Point

If DS review passes, create a controller judgment for this plan. Do not enter implementation.

Next possible artifact after accepted plan review:

- `docs/reviews/mvp-agent-engine-design-refresh-gate-plan-controller-judgment-20260607.md`
