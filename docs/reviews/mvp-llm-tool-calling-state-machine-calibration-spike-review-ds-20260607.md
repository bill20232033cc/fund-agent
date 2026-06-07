# MVP LLM Tool Calling And State Machine Calibration Spike — AgentDS Architecture / State Ownership / Fail-Closed Invariants Review

- Reviewer: AgentDS
- Scope: architecture/state ownership and fail-closed invariants review only
- Target: `docs/reviews/mvp-llm-tool-calling-state-machine-calibration-spike-20260607.md`
- Date: 2026-06-07
- Verdict: **PASS**

## Evidence Basis

Authoritative inputs read:
- `AGENTS.md` (full)
- `docs/design.md` §1–§2 (architecture boundaries, current/future state labels, Dayu ruling)
- `docs/current-startup-packet.md` (full)
- `docs/implementation-control.md` (control plane sections)
- `fund_agent/services/chapter_orchestrator.py` (full)
- `fund_agent/fund/chapter_writer.py` (full)
- `fund_agent/fund/chapter_auditor.py` (full)
- `fund_agent/services/execution_contract.py` (full)
- `fund_agent/services/fund_analysis_service.py` (full)
- `fund_agent/host/README.md` (full)

Code was read as read-only evidence. No code, config, runtime, provider default, PR, or external state was modified.

## Findings

### Review Question 1 — State Ownership Separation

**PASS.** The spike correctly separates state ownership under `UI → Service → Host → Agent`.

Spike §5 Service-owned state (use case, ExecutionContract, provider config, quality policy, product mapping) matches current code: `execution_contract.py` defines Service-owned `FundLLMExecutionContract` / `FundLLMExecutionRequest` / `FundLLMRuntimePlan` / `ProviderRuntimeBudget`; `fund_analysis_service.py` owns provider construction via `build_fund_llm_execution_request()`.

Spike §5 Host-owned state (lifecycle, deadline, cancel, terminal, events, safe diagnostics) matches current `host/README.md`: "Host 管 run lifecycle、cancel、deadline、terminal state、safe diagnostics、event/outbox boundary；当前 API 只接收 `operation_name`、同步 `operation`、`timeout_seconds`、可选 `session_id` 和可选通用 `event_sink`."

Spike §5 Agent-migrated state (chapter task graph, attempt ledger, repair budget, writer/auditor sequencing, ToolTrace, readiness matrix) is correctly labelled as future-only. Current `ChapterOrchestrator` (in `services/chapter_orchestrator.py`) is Service-owned, and `fund_agent/agent` does not exist. `design.md` §2.1 confirms this as accepted future design.

Spike §5 Fund-owned state (fund type, preferred_lens, CHAPTER_CONTRACT, ITEM_RULE, EvidenceAvailability, writer/auditor contracts, programmatic audit, semantic audit, issue-to-repair) matches current code: `chapter_writer.py` and `chapter_auditor.py` are in `fund_agent/fund/` with explicit docstrings stating they belong to Agent layer Fund capability.

### Review Question 2 — Future vs Current Runtime

**PASS.** The spike explicitly avoids treating future Agent/tool-loop/ToolRegistry/ToolTrace as current runtime fact.

Spike §3 line 34: "Future Agent engine/tool-loop is accepted future design only. `fund_agent/agent` runner/tool loop/ToolRegistry/ToolTrace is not current runtime fact."

Spike §10: "Do not enter Agent runtime implementation until the plan is reviewed and a controller judgment explicitly authorizes a slice."

This is consistent with Startup Packet §5 boundary guardrails: "Future Agent engine/tool loop/runner/ToolRegistry/ToolTrace and typed audit contract migration must internalize Dayu Engine capabilities and must not directly depend on `dayu-agent` / `dayu.engine` as production runtime."

### Review Question 3 — ToolRegistry Wrapping Preserving Fund Primitives

**PASS.** Spike §6 correctly proposes wrapping existing Fund primitives as typed tools without rewriting Fund logic.

Each tool in the table maps to an existing function:
- `fund.project_chapter_facts` → `project_chapter_facts()` (Startup Packet §3)
- `fund.derive_evidence_availability` → `derive_evidence_availability()` (Startup Packet §3)
- `fund.write_chapter` → `write_chapter()` (`chapter_writer.py:741`)
- `fund.audit_programmatic` → `audit_chapter_programmatic()` (`chapter_auditor.py:420`)
- `fund.audit_semantic` → `audit_chapter_llm()` (`chapter_auditor.py:452`)
- `fund.audit_combined` → `audit_chapter()` (`chapter_auditor.py:511`)

Input/output contracts in the table match current dataclass signatures. The spike correctly states provider clients should not become registry tools (§6: "Provider writer/auditor clients should not become registry tools"). This is consistent with `design.md` §2.1 accepted future ruling.

Spike §6 also correctly preserves the `EvidenceAvailability` constraint: "should be precomputed from same-source facts, not fetched by an agent tool from files or retained artifacts." This aligns with `chapter_writer.py:922`: "typed required output 写作路径必须显式传入 EvidenceAvailability."

### Review Question 4 — Fail-Closed Invariants Preservation

**PASS.** Spike §7 lists 8 non-negotiable invariants, all of which are verifiable against current code:

1. Programmatic audit first-class and not bypassable — confirmed: `audit_chapter()` (chapter_auditor.py:511) always runs programmatic before LLM; `run_programmatic` flag defaults to `True`.
2. LLM auditor bounded semantic only — confirmed: `audit_chapter_llm()` receives bounded `audit_focus` from typed contract; parse failure is `blocked` not `pass` (§1524-1530).
3. Writer parser exact markers preserved — confirmed: `_draft_from_llm_response()` (chapter_writer.py:1534) checks `_invalid_marker_issues()`, `_required_structure_issues()`, `_required_output_marker_issues()`, `_required_output_degrade_issues()`.
4. Audit line protocol exact — confirmed: `_parse_llm_audit_response()` (chapter_auditor.py:1508) rejects non-3-part lines and unknown severity text.
5. Repair bounded — confirmed: `ChapterOrchestrationPolicy` in chapter_orchestrator.py enforces bounded repair via `max_repair_attempts`.
6. Runtime vs content failure separation — confirmed: `ChapterRunResult.failure_category` distinguishes `llm_timeout` / `llm_network_error` from contract/audit blocks.
7. Safe scalar state in attempt ledger — confirmed: `ChapterPromptCostDiagnostic` omits prompt, draft, raw responses; `SafeDiagnosticPolicy` (execution_contract.py:227) enforces `forbid_prompt=True`, `forbid_draft=True`, `forbid_raw_provider_response=True`, `forbid_secrets=True`.
8. Final assembly won't accept incomplete — confirmed: `QualityFailClosedPolicy` (execution_contract.py:190) enforces `fail_on_partial_orchestration=True`, `fail_on_incomplete_final_assembly=True`, `deterministic_fallback_allowed=False`.

### Review Question 5 — Dayu Reference Only

**PASS.** Spike §8 correctly lists Dayu concepts as reference only (Host lifecycle, Engine concepts, event/outbox discipline) and explicitly forbids:
- `dayu-agent`, `dayu.host`, `dayu.engine` as production runtime dependencies
- Direct import of external Dayu runtime modules
- Copying/rewriting upstream Dayu code without license/compliance gate
- Dayu as escape hatch around `UI → Service → Host → Agent`
- LangGraph or MCP runtime

This is fully consistent with `AGENTS.md` §Dayu硬约束 and `design.md` §2.1 Dayu裁决.

### Review Question 6 — Inputs to Agent Engine Design Refresh Gate

**PASS.** Spike §9 provides 7 bounded inputs that are sufficient to open a design/plan gate without over-constraining implementation:

1. Bounded task graph framing — correct first-principles inference from current loop structure (§4)
2. Service ownership preserved — clear boundary (§5)
3. Agent execution mechanics migration — specific items listed (§5)
4. Fund primitives as stable domain tools — confirmed (§6)
5. Provider clients as explicit per-run inputs — correct constraint (§6)
6. Fail-closed semantics before concurrency — correct ordering (§7)
7. Small migration slices — reasonable incremental sequence (§9)

Spike §10 required plan sections are appropriate for a design/plan gate: phase objective, non-goals, state ownership, tool boundary, fail-closed invariants, migration slices, validation matrix, review requirements, stop conditions.

## Non-Blocking Observations

No observation in this section constitutes a blocking finding or requires spike revision before acceptance.

### NBO-1: EvidenceAvailability Production Ambiguity (Spike §6 vs §9)

Spike §6 says `EvidenceAvailability` "should be precomputed from same-source facts, not fetched by an agent tool." Spike §9 recommends only 7 migration slices and does not explicitly address where the precomputation happens: inside Agent (at task setup, from same-source `ChapterFactProjection`) or inside Service (passed to Agent as part of task input).

Current code (`chapter_orchestrator.py`) computes `EvidenceAvailability` in the Service-owned orchestrator via `derive_evidence_availability()` before calling writer/auditor. If Agent later owns task graph setup, the precomputation point should be explicitly resolved in the Agent Engine Design Refresh Gate plan.

**Severity**: informational. Does not block this spike. Resolvable during the next design gate.

### NBO-2: Service ProviderRuntimeBudget vs Agent Repair Budget Interaction (Spike §5)

Spike §5 says "repair budget accounting" migrates from Service to Agent. Current `ProviderRuntimeBudget` (execution_contract.py:133) is Service-owned and includes `writer_timeout_seconds`, `auditor_timeout_seconds`, `repair_timeout_seconds`, `timeout_max_attempts`. If Agent owns repair budget accounting, there should be a clear handshake between Service-provided provider ceilings and Agent-enforced attempt limits. The spike doesn't explicitly model this interaction.

**Severity**: informational. The Agent Engine Design Refresh Gate plan should clarify: Service sets provider runtime ceilings (timeout, max attempts per provider call); Agent enforces agent-level policy (max repair cycles, stop conditions). This is consistent with current code where `ChapterOrchestrationPolicy.max_repair_attempts` and `ProviderRuntimeBudget.timeout_max_attempts` serve different purposes.

### NBO-3: Tool Table Omits `repair_hint` Semantics (Spike §6)

Spike §6 tool table maps tools to primitives with input/output contracts but doesn't include Fund-owned `repair_hint` semantics (`ChapterAuditRepairHint`: `none` / `patch` / `regenerate` / `needs_more_facts`). This is implicit in `fund.audit_programmatic` and `fund.audit_semantic` outputs but is a critical input to the Agent's repair decision. The spike §5 correctly says "issue-to-repair semantics" stay Fund-owned, and §10 covers repair in the next gate. No change needed.

**Severity**: informational. The Agent Engine Design Refresh Gate should explicitly model how Fund audit `repair_hint` maps to Agent `RepairPolicy.decide`.

## Validation

Local no-live read-only commands used:
```text
Read: AGENTS.md, docs/design.md, docs/current-startup-packet.md, docs/implementation-control.md
Read: fund_agent/services/chapter_orchestrator.py, fund_agent/fund/chapter_writer.py, fund_agent/fund/chapter_auditor.py
Read: fund_agent/services/execution_contract.py, fund_agent/services/fund_analysis_service.py, fund_agent/host/README.md
Bash: grep design.md for Agent/tool-loop/Dayu/LangGraph/MCP/fail-closed keywords
```

No live command, provider probe, endpoint check, runtime/default change, code implementation, PR, push, or external action was performed.

## Summary

The spike correctly separates state ownership across the four layers, treats Agent/tool-loop as future design only, proposes ToolRegistry as Fund primitive wrappers without rewriting Fund logic, preserves all fail-closed invariants, keeps Dayu as reference-only, and provides sufficient bounded inputs for the next Agent Engine Design Refresh Gate. Three non-blocking observations are noted for the next gate's plan, none requiring spike revision.
