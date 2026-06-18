# MVP internalized Agent engine implementation planning plan

## Worker Self-Check

- Role: planning worker only.
- Gate: `MVP internalized Agent engine implementation planning gate`.
- Classification: `heavy`.
- Scope: plan-only artifact for future implementation; no source code, no runtime config, no provider/default/budget, no `docs/design.md` / `docs/implementation-control.md` / `docs/current-startup-packet.md`, no commit, no push, no PR.
- Output artifact: this file.
- Required reads completed: `AGENTS.md`, `docs/design.md`, `docs/implementation-control.md`, `docs/current-startup-packet.md`, `docs/fund-analysis-template-draft.md`, accepted Agent engine/tool-loop design and controller judgment, typed template aggregate controller judgment, current Service/Fund/Host files listed by the requester.
- Observed doc gap: `fund_agent/agent/README.md` is missing because `fund_agent/agent/` does not exist yet. Record it as a future implementation docs requirement; do not create it in this planning gate.

## Goal / Motivation

Turn the accepted Agent engine/tool-loop contract execution design into a code-generation-ready implementation plan for the first internalized Agent engine MVP.

The implementation goal is not to make the provider path more permissive. The goal is to move execution mechanics out of the Service-owned `ChapterOrchestrator` transition facade and into a new internalized `fund_agent/agent` execution package while preserving current `fund-analysis analyze --use-llm` fail-closed behavior:

- current explicit opt-in remains required;
- incomplete LLM runs keep empty stdout and no deterministic fallback;
- Service still owns use case, `ExecutionContract`, provider construction, runtime ceilings, quality policy and final product mapping;
- Host remains lifecycle-only and business-opaque;
- Agent owns runner, sequential task graph, tool loop, attempt ledger, `ToolRegistry`, `ToolTrace`, `RepairPolicy` and `AgentFinalAssemblyReadiness`;
- Fund owns domain tools, typed contracts, same-source `EvidenceAvailability`, writer, programmatic-first audit, bounded semantic audit and `RepairSemantics`.

## Non-Goals

- Do not enter provider/default/runtime live probe.
- Do not change provider budgets, timeout defaults, provider max attempts, backoff, endpoint, model, base URL or provider fallback.
- Do not implement or wire `chapter_generation_score`, score-loop, golden promotion, readiness promotion or fixture promotion.
- Do not implement multi-year annual evidence runtime.
- Do not replace template truth: keep `docs/fund-analysis-template-draft.md`, `contracts.py`, current public chapter ids `0-7`, and no Ch2 public split / `0+9` / `0+10`.
- Do not implement Ch3 calibration or reinterpret retained Ch3 `programmatic:C2` evidence as root cause.
- Do not relax programmatic audit or let bounded semantic audit override programmatic blockers.
- Do not introduce `dayu-agent`, `dayu.host` or `dayu.engine` as production runtime dependency.
- Do not copy or rewrite upstream Dayu code without a separate license/compliance gate.
- Do not register provider clients as ToolRegistry tools or pseudo-tools.
- Do not pass business parameters through `extra_payload`, `kwargs` bags or free-form dict business bags.
- Do not make Host understand fund code, report year, chapter policy, provider clients, prompt, audit semantics or Fund business fields.
- Do not introduce parallel/concurrent chapter scheduling in the first MVP unless a later accepted plan provides stronger evidence. First MVP should be sequential.

## Direct Evidence

- `AGENTS.md` fixes the boundary as `UI -> Service -> Host -> Agent`; Service owns use case / prompt / ExecutionContract, Host owns lifecycle, Agent owns runner/tool-loop/ToolRegistry/ToolTrace, and Fund owns domain analysis and audit rules.
- `docs/design.md` records the accepted future Agent-engine design: Agent must own `AgentReportRun`, `ChapterTask`, task graph, tool loop, attempt ledger, `ToolRegistry`, `ToolTrace`, `RepairPolicy` and Agent-side final assembly readiness projection; Service keeps provider construction and runtime ceilings for the first MVP; provider clients are explicit per-run typed fields, not tools.
- `docs/current-startup-packet.md` says the separate Agent engine implementation planning gate is the allowed next architecture entry, while provider-runtime evidence/live probe, score-loop, and Agent runtime implementation are not authorized by the previous gate.
- `docs/reviews/mvp-internalized-agent-engine-tool-loop-contract-execution-controller-judgment-20260603.md` accepted the design-only future architecture and explicitly accepted sequential-first as a residual planning decision.
- `docs/reviews/mvp-typed-template-contract-aggregate-deepreview-controller-judgment-20260603.md` accepted typed template implementation slices while preserving non-goals: no provider/default/runtime changes, no Agent runner/tool-loop implementation, no multi-year runtime, no score-loop and no template truth replacement.
- `fund_agent/services/chapter_orchestrator.py` currently owns the write-audit-repair loop for chapters 1-6, including attempt records, repair decisions, runtime diagnostics, Host phase checks, typed availability derivation and serialization helpers. This is the main responsibility to migrate.
- `fund_agent/services/execution_contract.py` currently owns `FundLLMExecutionContract`, `FundLLMExecutionRequest`, provider runtime budget, quality fail-closed policy, safe diagnostic policy and Host timeout derivation. These should stay Service-owned.
- `fund_agent/services/final_chapter_assembler.py` currently owns deterministic final assembly and readiness checks for Ch0/Ch7. First Agent MVP can compute Agent-side readiness, but Service remains final product mapping boundary until a separate accepted replacement gate.
- `fund_agent/fund/chapter_writer.py`, `fund_agent/fund/chapter_auditor.py` and `fund_agent/fund/evidence_availability.py` already provide Fund-owned typed primitives and same-source availability. Future Agent should wrap and call these, not reimplement Fund semantics.
- `fund_agent/host/runtime.py` and `fund_agent/host/README.md` show Host is a generic run lifecycle wrapper with cancel/deadline/safe diagnostics only and must not import Service/Fund or inspect business fields.
- `fund_agent/agent/README.md` is currently absent; future Agent package creation must include it.

## Affected Files / Modules

Future implementation should be scoped to:

- New Agent package:
  - `fund_agent/agent/__init__.py`
  - `fund_agent/agent/contracts.py` or `models.py`
  - `fund_agent/agent/runner.py`
  - `fund_agent/agent/task_graph.py`
  - `fund_agent/agent/tool_registry.py`
  - `fund_agent/agent/tool_trace.py`
  - `fund_agent/agent/repair_policy.py`
  - `fund_agent/agent/final_readiness.py`
  - `fund_agent/agent/fund_tools.py` or equivalent adapter module
  - `fund_agent/agent/README.md`
- Fund domain additions:
  - `fund_agent/fund/repair_semantics.py` for issue-to-repair semantics if existing `ChapterAuditRepairHint` is insufficient as a stable typed domain contract.
  - Existing `chapter_writer.py`, `chapter_auditor.py`, `evidence_availability.py` only if adapter-facing types need narrow additive exports.
- Service migration / adapter:
  - `fund_agent/services/fund_analysis_service.py`
  - `fund_agent/services/chapter_orchestrator.py`
  - `fund_agent/services/execution_contract.py` only if explicit Agent input/ceiling fields must be added.
  - `fund_agent/services/llm_run_artifacts.py` for safe ToolTrace summary serialization only.
  - `fund_agent/services/llm_provider.py` should remain provider-client construction/adaptation only.
- Tests:
  - New `tests/agent/` package.
  - Existing `tests/services/test_chapter_orchestrator.py`, `tests/services/test_execution_contract.py`, `tests/services/test_final_chapter_assembler.py`, `tests/services/test_fund_analysis_service_llm.py`, `tests/ui/test_cli.py`.
  - Existing Fund tests for writer/auditor/evidence availability/typed contracts.
- Documentation after implementation acceptance:
  - Create `fund_agent/agent/README.md`.
  - Update `fund_agent/README.md`, `fund_agent/fund/README.md` if Fund `RepairSemantics` is added, and `tests/README.md`.
  - Update root `README.md` only if user-facing CLI behavior or command examples change. First MVP should avoid that.
  - Do not update `docs/design.md`, `docs/implementation-control.md` or `docs/current-startup-packet.md` until a separate controller-authorized docs/control sync gate.

## Public Contracts / Schema / State-Machine Changes

Additive Agent contracts:

- `AgentReportRunInput(schema_version="agent_report_run.v1")`
  - explicit `fund_code`, `report_year`;
  - explicit `ChapterFactProjection`;
  - explicit `AgentLLMClients(writer, auditor)` typed with Fund writer/auditor Protocols;
  - explicit `AgentExecutionPolicy`;
  - explicit `AgentRunControl` cancellation/deadline Protocol;
  - explicit Service-owned final judgment inputs needed for readiness, if Ch7 readiness is evaluated in Agent.
- `AgentExecutionPolicy(schema_version="agent_execution_policy.v1")`
  - `target_chapter_ids`;
  - `max_repair_attempts`;
  - `max_output_chars`;
  - `prompt_payload_mode`;
  - `run_programmatic_audit`;
  - `run_bounded_semantic_audit`;
  - `typed_template_path`;
  - `safe_diagnostic_policy_id`;
  - no provider defaults and no provider client config values.
- `ChapterTask(schema_version="agent_chapter_task.v1")`
  - `task_id`, public `chapter_id`, dependency ids, typed contract id, attempt ledger.
- `AgentRunResult(schema_version="agent_run_result.v1")`
  - run terminal state: `accepted`, `partial_fail_closed`, `host_interrupted`;
  - per-chapter matrix;
  - accepted drafts/conclusions for chapters 1-6;
  - `AgentFinalAssemblyReadiness`;
  - safe `ToolTrace` summary.
- `ToolRegistry(schema_version="agent_tool_registry.v1")`
  - stable tool ids: `fund.chapter_writer`, `fund.programmatic_audit`, `fund.bounded_semantic_audit`, `fund.repair_semantics`, `agent.final_assembly_readiness`.
  - Provider clients are excluded from registry.
  - `EvidenceAvailability` is excluded from registry and is a precomputed input.
- `ToolTrace(schema_version="agent_tool_trace.v1")`
  - allowlist-only fields: run/task/chapter/attempt/tool ids, phase, enum status, issue ids, counts, elapsed ms, timeout seconds, approx tokens/chars, repair budget counters, safe runtime category.
  - forbidden fields: prompt, draft, repair draft, raw provider response, raw audit response, API key, Authorization header, cookies, provider hidden config, raw PDF/text.
- `RepairPolicy(schema_version="agent_repair_policy.v1")`
  - Agent-owned attempt counting, remaining budget, stop/retry decision.
  - Fund-owned `RepairSemantics` maps issue ids and audit hints to domain repair meaning.
- `AgentFinalAssemblyReadiness(schema_version="agent_final_assembly_readiness.v1")`
  - `ready`, `incomplete`, `blocked`;
  - missing accepted body chapter ids;
  - missing accepted draft/conclusion ids;
  - readiness issue ids.

### Concrete RepairSemantics Contract

Fund must expose a concrete, typed `RepairSemantics` contract before Agent Slice 3 starts. It is Fund-owned because the mapping depends on audit rule codes, ITEM_RULE ids, required output clauses, evidence availability and template semantics. Agent `RepairPolicy` may consume this output, but Agent must not reinterpret Fund audit issue meaning or hardcode issue-to-correction rules.

Proposed module and placement:

- Primary location: `fund_agent/fund/repair_semantics.py`.
- Slice placement: add in Slice 3 before `fund.repair_semantics` is registered in `ToolRegistry`.
- Existing relation: this contract is an additive typed superset of current `ChapterAuditRepairHint = Literal["none", "patch", "regenerate", "needs_more_facts"]`. The current hint remains the audit-layer coarse signal; `RepairSemantics` turns the actual `ChapterAuditIssue` set into Agent-consumable repair actions and correction instructions. It should reuse the existing deterministic correction mapping currently embedded in Service repair planning as the migration source, not create a parallel Agent mapping.

Required types:

- `RepairSemanticsAction = Literal["none", "patch", "regenerate", "needs_more_facts", "stop_fail_closed"]`.
- `RepairSemanticsInput(schema_version="repair_semantics_input.v1")`
  - `chapter_id: int`.
  - `attempt_index: int`: current failed attempt index, from 0.
  - `remaining_repair_budget: int`: remaining Agent repair budget after the failed attempt; `0` means no further regenerate is allowed.
  - `audit_status: ChapterAuditStatus`.
  - `aggregate_repair_hint: ChapterAuditRepairHint`: current `ChapterAuditResult.repair_hint`.
  - `issues: tuple[ChapterAuditIssue, ...]`: all programmatic and bounded semantic issues in deterministic order.
  - `evidence_availability: EvidenceAvailability`: same-source availability derived before the tool loop.
  - `typed_chapter_contract: TypedChapterContract`: chapter contract used by writer/auditor.
- `RepairIssueSemantics(schema_version="repair_issue_semantics.v1")`
  - `issue_id: str`.
  - `rule_code: ChapterAuditRuleCode`.
  - `repairable: bool`.
  - `action: RepairSemanticsAction`.
  - `required_correction: str`: sanitized, bounded correction text suitable for writer repair context.
  - `tied_clause_ids: tuple[str, ...]`: CHAPTER_CONTRACT / must_answer / must_not_cover clause ids when known.
  - `tied_item_rule_ids: tuple[str, ...]`: copied from `ChapterAuditIssue.item_rule_ids`.
  - `tied_fact_ids: tuple[str, ...]`.
  - `tied_anchor_ids: tuple[str, ...]`.
  - `evidence_blocked: bool`: true when the issue cannot be repaired by rewriting because same-source evidence is unavailable.
- `RepairSemanticsOutput(schema_version="repair_semantics_output.v1")`
  - `chapter_id: int`.
  - `attempt_index: int`.
  - `aggregate_action: RepairSemanticsAction`.
  - `stop_reason: Literal["none", "auditor_failed", "auditor_blocked", "repair_budget_exhausted", "needs_more_facts"]`.
  - `repairable: bool`.
  - `required_corrections: tuple[str, ...]`: deduplicated, deterministic, sanitized corrections for writer repair input.
  - `issue_semantics: tuple[RepairIssueSemantics, ...]`.
  - `source_repair_hint: ChapterAuditRepairHint`.
  - `source_issue_ids: tuple[str, ...]`.

Mapping source and precedence:

- Source of truth is Fund audit output plus the deterministic correction mapping migrated from current Service repair helpers (`_required_correction_from_issue`, `_required_corrections_from_issues`, `_repair_context_from_audit`).
- `aggregate_repair_hint == "none"` with no blocking issues maps to `aggregate_action="none"` and `stop_reason="none"`.
- Any issue whose evidence requirement is unavailable in same-source `EvidenceAvailability` maps to per-issue `action="needs_more_facts"`, `repairable=False`, `evidence_blocked=True`; aggregate action becomes `needs_more_facts`, stop reason `needs_more_facts`.
- `audit_status == "blocked"` maps to aggregate `stop_fail_closed` unless the issue-level semantics prove the only blocker is `needs_more_facts`; stop reason is `auditor_blocked` or `needs_more_facts`.
- `aggregate_repair_hint in {"patch", "regenerate"}` with `remaining_repair_budget > 0` maps to aggregate `regenerate` for first MVP. `patch` is preserved in issue semantics but not executed as in-place patch in the first MVP.
- Any repairable audit failure with `remaining_repair_budget <= 0` maps to aggregate `stop_fail_closed`, stop reason `repair_budget_exhausted`.
- `aggregate_repair_hint == "needs_more_facts"` maps to aggregate `needs_more_facts`, stop reason `needs_more_facts`.

Agent `RepairPolicy` consumes only `RepairSemanticsOutput.aggregate_action`, `stop_reason`, `required_corrections`, `source_issue_ids` and `issue_semantics[*].repairable/evidence_blocked`. It may count attempts and enforce budgets, but it must not invent new rule-code mappings, correction text, item ids, clause ids or evidence blockers.

### AgentRunControl Protocol And Adapter

Agent must define an Agent-side Protocol and import only that Protocol in runner code. Agent must not import `fund_agent.host.runtime.HostRunContext`, `HostRunResult`, `HostCancellationToken`, concrete event enums or Host runner classes.

Exact Protocol shape for Slice 1:

```python
class AgentRunControl(Protocol):
    """Agent 可消费的 Host 生命周期最小子集。"""

    def raise_if_cancelled_or_deadline_exceeded(self) -> None: ...

    def deadline_exceeded(self) -> bool: ...

    def record_phase_started(
        self,
        *,
        phase: str,
        chapter_id: int | None = None,
        attempt: int | None = None,
        provider_attempt: int | None = None,
    ) -> None: ...

    def record_phase_completed(
        self,
        *,
        phase: str,
        chapter_id: int | None = None,
        attempt: int | None = None,
        provider_attempt: int | None = None,
        elapsed_ms: int | None = None,
    ) -> None: ...

    def record_diagnostic(self, **diagnostics: object) -> None: ...
```

Usage constraints:

- Runner calls `raise_if_cancelled_or_deadline_exceeded()` before each chapter task, before each tool call, after each tool call, and before returning `AgentRunResult`.
- `deadline_exceeded()` is observation-only for post-tool classification; it must not replace the raising boundary check.
- `record_phase_started()` / `record_phase_completed()` may use safe phase names only: `agent_task`, `tool_call`, `repair_policy`, `final_readiness`.
- `record_diagnostic()` may receive only allowlisted safe scalar diagnostics. It must never receive prompt, draft, repair draft, raw provider response, raw audit response, API key, Authorization header, cookies or raw document text.

Service adapter location:

- Add the adapter in `fund_agent/services/agent_adapter.py` during Slice 5.
- Adapter name: `ServiceAgentRunControlAdapter`.
- Adapter dependency direction: Service may import concrete `HostRunContext` and Agent Protocol types; Agent imports neither Service nor concrete Host runtime.
- Adapter implementation delegates the five Protocol methods to `HostRunContext` and performs no business interpretation. It must not expose `run_id`, `deadline_at`, `timeout_seconds` or `cancellation_token` to Agent.

### AgentRunResult To Service Mapping

Slice 5 must include a Service-owned adapter that converts `AgentRunResult` into the current `ChapterOrchestrationResult` / `ChapterRunResult` shape. The adapter lives in `fund_agent/services/agent_adapter.py` with `ServiceAgentResultAdapter` or equivalent. Agent must not import Service result types.

Required mapping table:

| Agent field | Service field | Mapping rule |
|---|---|---|
| `AgentReportRunInput.fund_code` | `ChapterOrchestrationResult.fund_code` | Copy from original Service input, not from trace. |
| `AgentReportRunInput.report_year` | `ChapterOrchestrationResult.report_year` | Copy from original Service input, not from trace. |
| `AgentReportRunInput.projection` | `ChapterOrchestrationResult.projection` | Copy the same `ChapterFactProjection` used to build Agent input. |
| `AgentReportRunInput.execution_policy.target_chapter_ids` | `ChapterOrchestrationResult.generated_chapter_ids` | Include every chapter id for which Agent created a `ChapterTask` and attempted execution. Failed body chapters still count as generated. |
| Agent missing task due to Service scope/dependency before Agent entry | `ChapterOrchestrationResult.skipped_chapter_ids` | Only Service-global scope/dependency skips are listed. A failed earlier body chapter must not cause later independent chapters to be skipped. |
| `AgentRunResult.terminal_state == "accepted"` | `ChapterOrchestrationResult.status` | Map to `"accepted"` only when all required body chapters have `accepted` draft and conclusion. |
| `AgentRunResult.terminal_state == "partial_fail_closed"` | `ChapterOrchestrationResult.status` | Map to `"partial"`; fail-closed policy later keeps empty stdout / exit 1. |
| `AgentRunResult.terminal_state == "host_interrupted"` | `ChapterOrchestrationResult.status` | Map to `"blocked"` if cancellation/deadline prevented a coherent result; blocked reason must identify host interruption safely. |
| `AgentRunResult.blocked_reasons` / host interruption reason | `ChapterOrchestrationResult.blocked_reasons` | Copy sanitized reasons; synthesize `("Agent run interrupted by Host lifecycle control",)` for host interruption when no safer specific reason exists. |
| `AgentRunResult.chapter_results[*].chapter_id/title` | `ChapterRunResult.chapter_id/title` | Copy title from typed chapter contract or Agent task metadata. |
| Agent per-chapter status `"accepted"` | `ChapterRunResult.status`, `stop_reason` | Map to `status="accepted"`, `stop_reason="none"`. |
| Agent per-chapter status `"blocked"` | `ChapterRunResult.status`, `stop_reason` | Map to `status="blocked"` and the typed stop reason from writer/audit/repair semantics (`writer_blocked`, `auditor_blocked`, `needs_more_facts`, etc.). |
| Agent per-chapter status `"failed"` | `ChapterRunResult.status`, `stop_reason` | Map to `status="failed"` and the typed stop reason (`auditor_failed`, `repair_budget_exhausted`, `llm_timeout`, prompt-contract reasons, etc.). |
| Agent per-chapter status `"skipped"` | `ChapterRunResult.status`, `stop_reason` | Map to `status="skipped"`, `stop_reason="chapter_not_in_scope"` or `dependency_missing`; first MVP should only produce this for explicit Service scope skips, not previous body failures. |
| Agent accepted draft | `ChapterRunResult.accepted_draft` | Copy only for accepted chapters; `None` otherwise. |
| Agent accepted conclusion | `ChapterRunResult.accepted_conclusion` | Copy only for accepted chapters; `None` otherwise. |
| Agent attempt ledger | `ChapterRunResult.attempts` | Convert each Agent attempt to `ChapterAttemptRecord` preserving attempt index, writer result, audit result, repair decision projection and safe runtime diagnostics. |
| `RepairSemanticsOutput` consumed by Agent `RepairPolicy` | `ChapterRepairDecision` inside attempts | Project `aggregate_action` to Service `ChapterRepairAction`: `none -> none`, `regenerate/patch -> regenerate`, `needs_more_facts -> needs_more_facts`, `stop_fail_closed -> stop`; copy `source_repair_hint` and `source_issue_ids`. |
| Agent per-chapter issue ids/messages | `ChapterRunResult.issues` | Copy sanitized messages or stable issue ids consistent with current artifact safety; no prompt/draft/raw response. |
| Agent per-chapter failure category/subcategory | `ChapterRunResult.failure_category/failure_subcategory` | Reuse current Service classifiers where possible; otherwise map only to existing enums and add unmapped Agent detail to additive diagnostics. Do not add new Service enum values in this MVP unless separately accepted. |
| Agent safe ToolTrace entries | `ChapterRunResult.runtime_diagnostics` / `ChapterAttemptRecord.runtime_diagnostics` / artifact additive diagnostics | ToolTrace is the Agent superset. Adapter projects currently supported safe scalar provider diagnostics into existing `ChapterLLMRuntimeDiagnostic`; Agent-only tool phases remain additive artifact diagnostics. |
| `AgentRunResult.accepted_conclusions` | `ChapterOrchestrationResult.accepted_conclusions` | Preserve chapter order and include only accepted body chapters. |
| `AgentFinalAssemblyReadiness` | Service `FinalAssemblyReadiness` inputs / additive diagnostics | Do not replace Service type. Use Agent readiness as a precomputed diagnostic/projection; Service `FinalChapterAssembler` remains final authority in first MVP. |

Terminal mapping invariants:

- `ChapterOrchestrationResult.status == "accepted"` requires every target body chapter to have `ChapterRunResult.status == "accepted"` plus non-null `accepted_draft` and `accepted_conclusion`.
- Any non-accepted target body chapter maps the orchestration to `"partial"` unless Host lifecycle interruption prevents reliable per-chapter matrix, in which case map to `"blocked"`.
- Service `QualityFailClosedPolicy.fail_on_partial_orchestration=True` must preserve current incomplete LLM behavior: empty stdout, exit code `1`, and no deterministic fallback.
- `chapter_policy` is not a field on current `ChapterOrchestrationResult`; preserve it at Service request/runtime-plan level and in existing artifact metadata if already present. Do not push policy into Host or Agent trace as a free-form business dict.
- `projection`, `fund_code`, `report_year`, `generated_chapter_ids`, `skipped_chapter_ids` are Service adapter responsibilities, not Agent-derived free text.
- Additive diagnostics may include Agent schema version, terminal state, safe ToolTrace summary, Agent task ids, safe phase statuses and repair budget counters. They must never change current fail-closed decisions.

ToolTrace compatibility note:

- `ToolTrace` must be a safe superset of currently serialized `ChapterLLMRuntimeDiagnostic` scalar fields: operation/tool id, chapter id, repair attempt index, provider attempt index, provider max attempts, runtime category, failure category, elapsed ms, status code, request id, model name, finish reason, response chars, error type, prompt char/token counts, allowed fact/anchor counts, max output chars, timeout seconds, timeout retry budget, timeout budget kind, repair timeout fallback flag, timeout root-cause hint and bounded safe message.
- The ToolTrace serializer may expose Agent-only tool phases separately, but existing safe provider diagnostics must remain projectable so incomplete-run artifacts do not lose root-cause evidence.

State machine for each body chapter:

```text
TASK_READY
  -> WRITE_DRAFT
  -> PROGRAMMATIC_AUDIT
     -> PLAN_REPAIR -> REGENERATE -> WRITE_DRAFT
     -> PLAN_REPAIR -> STOP_FAIL_CLOSED
     -> STOP_FAIL_CLOSED
  -> BOUNDED_SEMANTIC_AUDIT
     -> PLAN_REPAIR -> REGENERATE -> WRITE_DRAFT
     -> PLAN_REPAIR -> STOP_FAIL_CLOSED
     -> STOP_FAIL_CLOSED
  -> ACCEPT_CHAPTER
```

First MVP scheduling:

- Sequentially execute body chapters 1-6 in `target_chapter_ids` order.
- A failed body chapter must not skip later independent body chapters.
- Ch7/Ch0 production remains Service final assembler in the first implementation; Agent `AgentFinalAssemblyReadiness` only feeds Service mapping until a later accepted replacement gate.

## Implementation Decisions

- Create `fund_agent/agent` as a generic Agent execution package, not a Fund business package.
- Keep Service provider construction exactly where it is. Service constructs clients and maps them to `AgentLLMClients`.
- Keep `FundLLMExecutionContract` business-only. Provider runtime budget and Agent execution ceilings remain outside the stable business contract.
- Do not let Agent import Service types. Service may import Agent public contract types to construct an `AgentReportRunInput`.
- Avoid Agent importing concrete Host runtime. Define the Agent-side `AgentRunControl` Protocol exactly as specified above; Service adapts `HostRunContext` in `fund_agent/services/agent_adapter.py`. This keeps Host lifecycle-only and avoids a reverse dependency.
- Wrap Fund primitives as Agent tools without moving Fund semantics into Agent.
- Run programmatic audit before bounded semantic audit. Semantic audit runs only after programmatic pass in first MVP.
- Keep `audit_focus` as bounded semantic-audit input only. It cannot disable programmatic audit or downgrade blockers.
- Convert Agent results back to existing Service result shape during migration so `llm_run_artifacts`, CLI summaries, exit code and stdout semantics remain stable.
- Preserve current explicit typed path: first Agent MVP applies only to `typed_template_path="typed_template_contract"` for `--use-llm`; legacy Service orchestrator path can remain until a later cleanup.

## Small Implementation Slices

### Slice 0: Preflight / Baseline

Purpose: prove implementation starts from current accepted behavior.

- Confirm branch and worktree.
- Confirm `fund_agent/agent/README.md` is absent and record as implementation doc requirement.
- Run current accepted focused test matrix before code edits.
- No code behavior change.

Validation:

```bash
uv run pytest tests/fund/template/test_typed_contracts.py tests/fund/test_evidence_availability.py tests/fund/test_chapter_writer.py tests/fund/test_chapter_auditor.py tests/services/test_chapter_orchestrator.py tests/services/test_execution_contract.py tests/services/test_final_chapter_assembler.py tests/services/test_fund_analysis_service_llm.py tests/ui/test_cli.py
```

### Slice 1: Agent Package Contracts And README

Purpose: create the Agent package and typed contracts without executing Fund tools.

- Add `fund_agent/agent/` package.
- Add dataclasses / Protocols for `AgentReportRunInput`, `AgentExecutionPolicy`, `AgentLLMClients`, `AgentRunControl`, `AgentRunResult`, `ChapterTask`, `ChapterTaskResult`, `AgentRunTerminalState`.
- Add `fund_agent/agent/README.md` as the Agent package development manual.
- Add import-boundary tests proving Agent does not import Service, Host concrete runtime, UI, provider config or dayu runtime.

Validation:

```bash
uv run pytest tests/agent/test_agent_contracts.py
uv run ruff check fund_agent/agent tests/agent
```

### Slice 2: ToolRegistry And ToolTrace Foundation

Purpose: implement Agent-owned registry and safe trace using fake tools only.

- Add typed tool call/result envelope with explicit fields.
- Add registry registration/lookup/version validation.
- Add `ToolTrace` and allowlist serializer.
- Add tests for forbidden keys and forbidden payloads: prompt, draft, raw responses, API key, Authorization header, cookies.
- No Fund primitive integration yet.

Validation:

```bash
uv run pytest tests/agent/test_tool_registry.py tests/agent/test_tool_trace.py
```

### Slice 3: Fund Tool Adapters And Repair Semantics

Purpose: adapt current Fund primitives as Agent-callable tools.

- Register wrappers for:
  - `fund.chapter_writer`;
  - `fund.programmatic_audit`;
  - `fund.bounded_semantic_audit`;
  - `fund.repair_semantics`.
- Keep writer/auditor clients as explicit tool input fields, not registry tools.
- Derive `EvidenceAvailability` before tool-loop and pass it as input.
- Add Fund `RepairSemantics` as the concrete typed domain mapping described above. Current `ChapterAuditRepairHint` remains an input signal but is not sufficient by itself for Agent `RepairPolicy`.
- Ensure tools do not read repository/PDF/cache/source helper, Service, Host, provider env/config or dayu.

Validation:

```bash
uv run pytest tests/agent/test_fund_tool_adapters.py tests/fund/test_chapter_writer.py tests/fund/test_chapter_auditor.py tests/fund/test_evidence_availability.py
```

### Slice 4: Sequential Body Chapter Runner

Purpose: move the write-audit-repair state machine into Agent for chapters 1-6.

- Implement sequential `AgentReportRunner.run_body_chapters()`.
- Implement per-chapter state machine: write, programmatic audit, bounded semantic audit, repair planning, regenerate, accept, fail-closed.
- Preserve independent body execution: a failed Ch2/Ch3 must not skip Ch4/Ch5/Ch6.
- Implement Agent-owned attempt ids and repair budget enforcement.
- Observe `AgentRunControl` before each task, before each tool call, and after tool returns.
- Do not add concurrency.

Validation:

```bash
uv run pytest tests/agent/test_chapter_runner.py tests/agent/test_agent_run_control.py
```

### Slice 5: Service Adapter Side-By-Side Migration

Purpose: route the explicit typed `--use-llm` path through Agent while preserving Service result shape.

- Add a Service-owned adapter that maps `FundLLMExecutionRequest.runtime_plan.chapter_policy` and `llm_clients` into `AgentReportRunInput`.
- Keep provider construction in Service.
- Keep current `_run_analysis_core()` in Service for structured data and final judgment inputs.
- Use Agent runner for `typed_template_path="typed_template_contract"` body chapter execution.
- Convert `AgentRunResult` back to the current `ChapterOrchestrationResult` shape for `FinalChapterAssembler`, artifact retention and CLI summaries.
- Keep current Service `ChapterOrchestrator` legacy path for non-typed tests or delete only after equivalent tests prove no caller needs it.

Validation:

```bash
uv run pytest tests/services/test_chapter_orchestrator.py tests/services/test_fund_analysis_service_llm.py tests/services/test_execution_contract.py
```

### Slice 6: AgentFinalAssemblyReadiness Projection

Purpose: add Agent readiness without replacing Service final assembler.

- Implement Agent-side `AgentFinalAssemblyReadiness` over required body chapter results.
- Service adapter maps readiness to existing `FinalChapterAssembler` inputs and issue summaries.
- Preserve current final assembly fail-closed behavior: incomplete body chapters block Ch7/Ch0/full report.
- Do not make Agent generate final Ch0/Ch7 report markdown in first MVP.

Validation:

```bash
uv run pytest tests/agent/test_final_assembly_readiness.py tests/services/test_final_chapter_assembler.py
```

### Slice 7: Diagnostics And Artifact Mapping

Purpose: expose Agent trace safely through existing incomplete-run artifact path.

- Extend Service artifact serialization to include safe `ToolTrace` summary only.
- Preserve existing local ignored `reports/llm-runs/` behavior.
- Preserve empty stdout and exit code `1` for incomplete `--use-llm`.
- Ensure no prompt/draft/raw provider/audit response/API key/header is serialized by trace.

Validation:

```bash
uv run pytest tests/services/test_llm_run_artifacts.py tests/ui/test_cli.py tests/agent/test_tool_trace.py
```

### Slice 8: Boundary Cleanup And Docs

Purpose: remove migrated execution mechanics from Service only after adapter tests pass.

- Remove or deprecate Service-owned `_run_single_chapter`, `_decide_repair`, attempt loop and Agent-owned trace logic from `chapter_orchestrator.py` for typed path.
- Keep Service-owned policy construction, final product mapping, and fail-closed exception behavior.
- Update `fund_agent/agent/README.md`, `fund_agent/README.md`, `fund_agent/fund/README.md` if `RepairSemantics` was added, and `tests/README.md`.
- Do not update `docs/design.md`, `docs/implementation-control.md` or startup packet until a separate docs/control sync gate.

Validation:

```bash
uv run pytest tests/agent tests/fund/test_chapter_writer.py tests/fund/test_chapter_auditor.py tests/fund/test_evidence_availability.py tests/services/test_chapter_orchestrator.py tests/services/test_execution_contract.py tests/services/test_final_chapter_assembler.py tests/services/test_fund_analysis_service_llm.py tests/ui/test_cli.py
uv run ruff check fund_agent/agent fund_agent/services fund_agent/fund tests/agent tests/services tests/fund
git diff --check
```

## Tests / Validation Commands

No live provider command is part of this gate. Use only fake clients, monkeypatching and `httpx.MockTransport` where needed.

Focused acceptance matrix:

```bash
uv run pytest tests/agent
uv run pytest tests/fund/template/test_typed_contracts.py tests/fund/test_evidence_availability.py tests/fund/test_chapter_writer.py tests/fund/test_chapter_auditor.py
uv run pytest tests/services/test_chapter_orchestrator.py tests/services/test_execution_contract.py tests/services/test_final_chapter_assembler.py tests/services/test_fund_analysis_service_llm.py tests/services/test_llm_run_artifacts.py
uv run pytest tests/ui/test_cli.py
uv run ruff check fund_agent/agent fund_agent/services fund_agent/fund tests/agent tests/services tests/fund
git diff --check
```

Forbidden validation for this gate:

- No `fund-analysis analyze --use-llm` real provider live run.
- No PASS-only timing probe.
- No provider endpoint/config/default changes.
- No snapshot/golden/promotion commands.
- No score-loop command.

## Docs Decision

This planning gate only writes this plan artifact.

Future implementation docs requirements:

- `fund_agent/agent/README.md`: required when `fund_agent/agent/` is created; current file is missing.
- `fund_agent/README.md`: update only after accepted code changes alter the current package boundary from Service-owned orchestration to Agent-owned execution.
- `fund_agent/fund/README.md`: update if a new Fund `RepairSemantics` API is added or existing writer/auditor public adapter guidance changes.
- `tests/README.md`: update when `tests/agent/` is added and the validation matrix changes.
- Root `README.md`: update only if user-facing CLI behavior changes; first MVP should preserve behavior and likely not require it.
- `docs/design.md`, `docs/implementation-control.md`, `docs/current-startup-packet.md`: do not edit during implementation slices unless a separate controller-authorized docs/control sync gate is opened after accepted implementation evidence.

## Review Gates

Because this gate is `heavy`, future implementation should use the following review sequence:

1. Plan review of this artifact by at least two independent reviewers, then controller judgment.
2. Slice 0-2 implementation evidence and code review before Fund wrapping.
3. Slice 3-4 implementation evidence and code review focused on ToolRegistry, ToolTrace, Fund boundaries and state machine.
4. Slice 5-7 implementation evidence and code review focused on Service migration, fail-closed mapping, CLI/stdout behavior and artifact safety.
5. Slice 8 docs/boundary cleanup review.
6. Aggregate deepreview over the implementation scope.
7. Controller judgment before any accepted commit/push/PR action.

Each implementation evidence artifact must record:

- changed files;
- validation commands and exact outcomes;
- import-boundary checks;
- stdout/exit/fallback behavior checks;
- secret-safety checks for ToolTrace/artifact serialization;
- residual risks and owners.

## Stop Conditions

Stop and return to controller if any of these become necessary:

- A live provider probe is needed to prove correctness.
- Provider timeout/default/model/base URL/budget changes are needed.
- Ch3 calibration or contract-shape reinterpretation is needed.
- Multi-year evidence runtime is needed.
- Score-loop/golden/promotion/readiness changes are needed.
- Public chapter ids or template truth need to change.
- Agent implementation would need `dayu-agent`, `dayu.host`, `dayu.engine`, or copied upstream Dayu code.
- A proposed design puts provider clients in ToolRegistry.
- A proposed design passes business parameters through `extra_payload`, `kwargs` bags or free-form dicts.
- Host would need to inspect fund code/year/chapter policy/provider clients/prompt/audit semantics.
- Service would need to directly call PDF cache, source helper, downloader or concrete annual-report sources.
- ToolTrace cannot be serialized safely without prompt/draft/raw response leakage.
- Sequential scheduling is insufficient and concurrency becomes required.

## Risks / Open Questions

- `ChapterOrchestrationResult` compatibility: resolved for implementation handoff by the explicit `AgentRunResult` to Service mapping table above. Residual implementation risk is limited to proving the adapter against existing `FinalChapterAssembler`, artifact retention and CLI tests.
- Import boundary: Agent may need cancellation/deadline observation. Use an Agent-side Protocol instead of importing concrete Host runtime unless a later boundary review accepts a direct type dependency.
- Repair semantics split: resolved for implementation handoff by adding Fund-owned `RepairSemantics` in Slice 3. Existing `ChapterAuditRepairHint` remains the coarse audit hint feeding that contract.
- ToolTrace safety: serializer must be allowlist-first and tested against prompt/draft/raw response/API key/header leakage. ToolTrace must also remain projectable to the current safe `ChapterLLMRuntimeDiagnostic` fields as specified above.
- Typed path scope: first MVP should route only explicit `typed_template_contract` `--use-llm`; legacy behavior should remain until migration tests prove equivalent.
- Final readiness replacement: Agent readiness can feed Service, but replacing `FinalChapterAssembler` is a separate gate unless the implementation review explicitly accepts it.
- Service `ChapterOrchestrator` cleanup may be large; if deletion creates unrelated churn, keep a thin compatibility facade and record residual cleanup.

## Completion Report Format

Future implementation closeout should report:

```text
Gate: MVP internalized Agent engine implementation gate
Classification: heavy
Scope: Agent engine MVP implementation for typed template contract execution

Implemented:
- Slice list with accepted/blocked status.
- Files changed.
- Public contracts added or changed.
- Migration summary: what moved from Service ChapterOrchestrator to Agent.
- Fail-closed behavior summary for --use-llm.

Validation:
- Command 1 -> result.
- Command 2 -> result.
- Secret-safety / ToolTrace serializer result.
- Import-boundary result.

Non-goals preserved:
- No provider/default/runtime live probe or budget/default change.
- No score-loop.
- No multi-year runtime.
- No template truth replacement.
- No dayu-agent runtime dependency.
- No provider clients as ToolRegistry tools.
- No extra_payload/kwargs/free dict business bags.

Docs:
- README files updated or explicitly not required.
- docs/design/control/startup sync status and whether a separate docs/control sync gate is needed.

Residual risks:
- Owner and next gate for each residual.
```
