# MVP LLM Tool Calling And State Machine Calibration Spike

## 1. Scope And Classification

- Phase: `MVP typed-template-to-agent report generation stabilization phase`
- Gate: `LLM Tool Calling And State Machine Calibration Spike`
- Classification: `standard`
- Artifact type: non-live learning / evidence spike

This spike is not production implementation. It changes no source code, tests, config, provider defaults, runtime budget, schema, quality gate, golden/readiness state, Host runtime, Agent runtime, MCP, LangGraph, dayu-agent runtime, PR, push, merge or external state.

## 2. Authoritative Inputs

- `AGENTS.md`
- `docs/design.md`
- `docs/current-startup-packet.md`
- `docs/implementation-control.md`
- `docs/fund-analysis-template-draft.md`
- Current code references:
  - `fund_agent/services/chapter_orchestrator.py`
  - `fund_agent/fund/chapter_writer.py`
  - `fund_agent/fund/chapter_auditor.py`
  - `fund_agent/services/execution_contract.py`
  - `fund_agent/services/fund_analysis_service.py`
  - `fund_agent/host/README.md`

## 3. Starting Facts

- Current deterministic production path remains `fund-analysis analyze/checklist`.
- Current explicit LLM path is `CLI -> Service prepares FundLLMExecutionRequest / ExecutionContract -> Host runner -> Service -> fund_agent/fund -> provider HTTP call`.
- Current body chapter loop is Service-owned: `ChapterOrchestrator` calls Fund writer and auditor primitives for chapters 1-6, tracks attempts, applies a bounded repair budget and returns fail-closed `ChapterOrchestrationResult`.
- Fund owns domain semantics: CHAPTER_CONTRACT, preferred_lens, ITEM_RULE, typed required-output items, same-source `EvidenceAvailability`, writer contracts, programmatic audit, bounded semantic LLM audit and evidence anchors.
- Host is currently lifecycle-only: deadline, cancel, terminal state, safe diagnostics and phase events. Host must not inspect fund business semantics.
- Future Agent engine/tool-loop is accepted future design only. `fund_agent/agent` runner/tool loop/ToolRegistry/ToolTrace is not current runtime fact.

## 4. Question 1: Current Loop As Tool-Calling / State-Machine Structure

The current writer/auditor/repair loop is already a small deterministic state machine wrapped in Service code:

| Current state | Current owner | Transition trigger | Future Agent state analogue |
|---|---|---|---|
| `prepare_chapter_input` | Service + Fund projection | target chapter id and typed policy selected | `ChapterTaskPrepared` |
| `write_initial` | Service orchestrator invokes Fund writer | writer LLM client returns draft or writer failure | `ToolCall(writer.write_chapter)` |
| `programmatic_audit` | Fund auditor | draft exists | `ToolCall(fund.audit_programmatic)` |
| `semantic_audit` | Fund auditor with explicit LLM client | programmatic audit permits bounded semantic audit | `ToolCall(fund.audit_semantic)` |
| `decide_repair` | Service orchestrator | audit status, repair hint and remaining budget | `AgentRepairPolicy.decide` |
| `write_repair` | Service orchestrator invokes Fund writer with `ChapterRepairContext` | repair action is regenerate and budget remains | `ToolCall(writer.write_chapter)` with attempt lineage |
| `accept_chapter` | Service orchestrator | audits pass | `ChapterTaskAccepted` |
| `fail_closed_chapter` | Service orchestrator | writer block, runtime failure, audit block, no facts, repair exhausted or budget stop | `ChapterTaskFailedClosed` |
| `assemble_or_block` | Service final assembly | body chapter matrix | `FinalAssemblyReadiness` / Service final product mapping |

First-principles inference: the loop is not mainly an open-ended autonomous agent problem yet. It is a bounded task graph with typed state, explicit stop reasons, deterministic audit gates and one semantic LLM audit tool. The Agent migration should preserve that bounded shape before adding broader tool-loop generality.

## 5. Question 2: Service State vs Future Agent State

State that should remain Service-owned:

- user use case selection: analyze/checklist, explicit `--use-llm`, report mode;
- `FundLLMExecutionContract` and user/business input normalization;
- provider config parsing and first-MVP provider construction;
- quality policy and final product fail-closed mapping;
- final user-visible result selection and CLI stdout/stderr semantics;
- decision to invoke Host and pass only generic lifecycle/deadline fields.

State that should remain Host-owned:

- run lifecycle, deadline, cancel, terminal state, event emission, safe diagnostics and future durable session/resume/memory/reply outbox;
- Host must receive only generic operation/deadline/session/event fields, not chapter policy, provider client internals or fund semantics.

State that should migrate from current Service façade to future Agent:

- per-chapter task graph for chapters 1-6;
- attempt ledger and repair budget accounting;
- writer/auditor tool-call sequencing;
- stop/retry decision within accepted policy;
- per-attempt ToolTrace records;
- final body chapter readiness matrix that can feed Service final assembly;
- Agent-side cancellation observation at task scheduling boundaries and after tool return.

State that should stay Fund-owned:

- fund type / preferred_lens interpretation;
- CHAPTER_CONTRACT, ITEM_RULE and typed required-output semantics;
- `ChapterFactProjection` and derived same-source `EvidenceAvailability`;
- writer input contract and output parser;
- programmatic audit rules;
- bounded semantic audit prompt / line protocol;
- issue-to-repair semantics.

## 6. Question 3: ToolRegistry Wrapping Existing Fund Primitives

The future ToolRegistry should wrap existing Fund primitives as typed tools instead of rewriting Fund logic.

Recommended initial tool shape:

| Tool | Wrapped primitive | Input contract | Output contract | Boundary |
|---|---|---|---|---|
| `fund.project_chapter_facts` | `project_chapter_facts()` | `StructuredFundDataBundle`, target chapter ids, template contract version | `ChapterFactProjection` | Fund |
| `fund.derive_evidence_availability` | `derive_evidence_availability()` | `ChapterFactProjection` | `EvidenceAvailability` | Fund |
| `fund.write_chapter` | `write_chapter()` | `ChapterWriterInput`, explicit writer client, optional `ChapterRepairContext` | `ChapterWriteResult` | Fund tool invoked by Agent |
| `fund.audit_programmatic` | `audit_chapter_programmatic()` | `ChapterAuditInput` | `ChapterProgrammaticAuditResult` | Fund deterministic tool |
| `fund.audit_semantic` | `audit_chapter_llm()` or bounded adapter | `ChapterAuditInput`, explicit auditor client | `ChapterLLMAuditResult` | Fund semantic tool invoked only after programmatic context |
| `fund.audit_combined` | `audit_chapter()` only if useful | `ChapterAuditInput`, optional auditor client | `ChapterAuditResult` | Convenience wrapper, not the only source of trace |

Provider writer/auditor clients should not become registry tools. They are Service-constructed per-run typed fields injected into Agent run state, then passed as explicit tool input to Fund tools. This keeps provider construction in Service and keeps ToolRegistry focused on domain tools and execution contracts.

`EvidenceAvailability` should be precomputed from same-source facts, not fetched by an agent tool from files or retained artifacts. This preserves the root-cause and evidence同源 constraint.

## 7. Question 4: Fail-Closed / Structured Output / Audit Line Protocol In Agent Loop

Non-negotiable invariants for the future Agent loop:

- Programmatic audit remains first-class and cannot be bypassed by LLM semantic audit.
- LLM auditor remains bounded semantic audit only; it cannot override programmatic blockers or turn missing evidence into positive claims.
- Writer output parser keeps exact markers for `required_output`, `anchor` and `missing`; unknown anchors, missing required-output markers, malformed structure, overlong output and unsafe finish reasons remain fail-closed.
- Audit line protocol remains exact: one-line `PASS|chapter|no issues` or three-part `BLOCKING/REVIEWABLE/INFO|LOCATION|MESSAGE`; parse failure remains blocking.
- Repair remains bounded by explicit policy; no unbounded retry loop, no silent deterministic fallback and no hidden budget expansion.
- Runtime failures remain separate from content failures in state and trace.
- Attempt ledger must record enough safe scalar state to explain outcome without raw prompt, raw draft, raw provider response, raw audit response, API key, Authorization header, model value or base URL value.
- Final assembly cannot accept a report unless required body chapter readiness is satisfied under explicit criteria.

Agent migration should improve traceability, not loosen acceptance.

## 8. Question 5: Dayu Reference vs Forbidden Runtime Dependency

Dayu concepts that are useful references:

- Host lifecycle: run id, terminal state, deadline, cancel and safe diagnostics.
- Engine concepts: runner, task graph, tool loop, ToolRegistry, ToolTrace, context budget and structured tool execution contract.
- Event/outbox discipline for future durable Host capabilities.

Forbidden in this project without a separate license/compliance and implementation gate:

- adding `dayu-agent`, `dayu.host` or `dayu.engine` as production runtime dependencies;
- directly importing external Dayu runtime modules to execute current report generation;
- copying or rewriting upstream Dayu code into this repository;
- using Dayu as an escape hatch around `UI -> Service -> Host -> Agent`;
- introducing LangGraph or MCP runtime to solve the first Agent MVP before this project has accepted its own Agent engine contract.

The safe route is concept internalization: define local interfaces and state transitions, then implement only the minimum accepted subset inside this repository.

## 9. Question 6: Input To Agent Engine Design Refresh Gate

This spike provides the following inputs for `Agent Engine Design Refresh Gate`:

1. Treat the current loop as a bounded task graph, not an open-ended autonomous agent.
2. Preserve Service ownership of use case, ExecutionContract, provider construction and final product mapping.
3. Migrate only execution mechanics to Agent: chapter task graph, attempt ledger, repair policy, ToolRegistry calls, ToolTrace and readiness matrix.
4. Keep Fund primitives as domain tools and keep their contracts stable.
5. Keep provider clients explicit per-run inputs, not ToolRegistry tools.
6. Preserve fail-closed semantics and structured output contracts before adding concurrency or richer scheduling.
7. Require a migration plan with small slices:
   - design local Agent run/task/trace dataclasses;
   - wrap existing Fund primitives as typed tool adapters;
   - port attempt ledger and repair decision from Service façade into Agent;
   - add no-live deterministic equivalence tests against current Service orchestration;
   - only then consider Service façade retirement or final assembly readiness handoff.

## 10. Recommended Next Gate

Open `Agent Engine Design Refresh Gate` as a design/plan gate only.

Required plan sections:

- phase objective;
- non-goals;
- state ownership;
- tool boundary;
- fail-closed invariants;
- migration slices;
- validation matrix;
- review requirements;
- stop conditions.

Do not enter Agent runtime implementation until the plan is reviewed and a controller judgment explicitly authorizes a slice.

## 11. Validation

Local no-live commands used for this spike:

```text
rg -n "class ChapterOrchestrator|def orchestrate_chapters|def _run_chapter|repair|attempt|ChapterRunResult|ChapterOrchestrationResult|ChapterRepairContext|audit_chapter|write_chapter" fund_agent/services/chapter_orchestrator.py fund_agent/fund/chapter_writer.py fund_agent/fund/chapter_auditor.py
rg -n "class FundLLMExecutionRequest|FundLLMExecutionContract|build_fund_llm_execution_request|analyze_with_llm_execution|host_timeout_seconds|ChapterOrchestrationPolicy" fund_agent/services fund_agent/host fund_agent/ui
```

No live command, provider probe, endpoint check, runtime/default change, code implementation, PR, push or external action was performed.

## 12. Review Request

Request two independent reviews where available:

- AgentDS: architecture/state ownership and fail-closed invariants.
- AgentMiMo: overreach, Dayu/runtime boundary, and whether the next Agent Engine Design Refresh Gate inputs are sufficient.

If two reviewers are unavailable, preserve the reviewer availability evidence and stop before accepting this spike.
