# MVP Agent Engine Design Refresh Gate Plan — AgentDS Architecture / Ownership / Boundary / Stop Conditions Review

- Reviewer: AgentDS
- Scope: plan review only per review questions 1–6
- Target: `docs/reviews/mvp-agent-engine-design-refresh-gate-plan-20260607.md`
- Date: 2026-06-08
- Verdict: **PASS_WITH_NON_BLOCKING_OBSERVATIONS**

## Evidence Basis

Authoritative inputs read:

- `AGENTS.md` (full)
- `docs/design.md` §1–§5 (architecture, four-layer boundaries, Dayu ruling, accepted future Agent engine design, Route C gate sequence, fail-closed invariants)
- `docs/current-startup-packet.md` (full)
- `docs/implementation-control.md` (control plane sections including current gate, current truth guardrails, accepted artifacts)
- `docs/reviews/mvp-llm-tool-calling-state-machine-calibration-spike-20260607.md` (full)
- `docs/reviews/mvp-llm-tool-calling-state-machine-calibration-spike-review-ds-20260607.md` (full)
- `docs/reviews/mvp-llm-tool-calling-state-machine-calibration-spike-controller-judgment-20260607.md` (full)
- Target plan: `docs/reviews/mvp-agent-engine-design-refresh-gate-plan-20260607.md` (full)

All reads were read-only. No code, config, runtime, provider default, PR, push, or external state was modified.

## Findings

### Review Question 1 — Service/Host/Agent/Fund Ownership

**PASS.** The plan correctly separates state ownership across the four layers per `AGENTS.md` §模块边界 and `design.md` §2.1.

Plan §3 Service-owned state (use case, ExecutionContract, provider config/construction, runtime ceilings, report strategy, final product fail-closed mapping, CLI semantics, quality policy) directly matches:
- `AGENTS.md` §Service层: "业务用例编排、场景定义、prompt/ExecutionContract组装、用户会话语义、报告生成、质量策略选择"
- `design.md` §2.1 accepted future ruling: "Service 保留 use case、ExecutionContract、quality policy、报告策略、provider config parsing / provider construction、runtime ceilings 和 final product fail-closed mapping"
- Current code fact: `execution_contract.py` Service-owned `FundLLMExecutionContract`, `fund_analysis_service.py` provider construction

Plan §3 Host-owned state (run lifecycle, global deadline, cancel, terminal state, safe diagnostics, future event/outbox/session/resume/memory) matches:
- `AGENTS.md` §Host层: "Agent session/run 生命周期、并发、超时、取消、恢复、memory、reply outbox、事件投递、ExecutionDeliveryContext"
- Current code fact: `host/README.md` confirms Host is business-opaque, lifecycle-only

Plan §3 Future Agent-owned state (AgentReportRun, ChapterTask, task graph, attempt ledger, repair policy, ToolRegistry, ToolTrace, budget, readiness matrix) matches:
- `design.md` §2.1 accepted future ruling: "future Agent owns chapter runner、tool-loop、repair/retry attempt bookkeeping、Agent-side budget accounting、ToolRegistry、typed tool execution、ToolTrace 和 final assembly readiness"
- `design.md` explicitly labels this as "已接受的未来设计" not current runtime fact
- `fund_agent/agent` does not exist — plan does not claim it does

Plan §3 Fund-owned state (fund type, preferred_lens, CHAPTER_CONTRACT, ITEM_RULE, ChapterFactProjection, same-source EvidenceAvailability, writer/auditor, programmatic audit, semantic audit adapter, issue ids, repair hints, evidence anchors) matches:
- `AGENTS.md` §Agent层: "基金领域能力、年报解析规则、有知有行方法论实现、审计规则"
- Current code fact: `chapter_writer.py`, `chapter_auditor.py` in `fund_agent/fund/`

One precision note: plan §3 says Fund owns "bounded semantic LLM audit adapter" — this matches `design.md` accepted future ruling: "LLM auditor 只能作为 bounded semantic audit tool".

### Review Question 2 — Implementation Creep Prevention

**PASS.** The plan has strong anti-creep measures.

Plan §1 explicitly states: "This plan is design-only. It does not authorize source/test/runtime implementation."

Plan §2 Non-Goals lists 13 forbidden actions including:
- no Agent runtime implementation (line 19)
- no `fund_agent/agent` package creation (line 20)
- no ToolRegistry code (line 21)
- no ToolTrace schema code (line 22)
- no migration of current Service `ChapterOrchestrator` (line 23)
- no provider/default/runtime/budget/config change (line 24)
- no live LLM command (line 25)
- no LangGraph (line 26)
- no MCP runtime (line 27)
- no `dayu-agent`, `dayu.host` or `dayu.engine` production dependency (line 28)
- no copy/rewrite of upstream Dayu code (line 29)
- no quality gate, golden/readiness, score-loop, multi-year runtime or public chapter ids 0-7 change (line 30)
- no PR, push, merge, mark ready, reviewer request or external comment (line 32)

Plan §8 Review Requirements states "AgentDS review only is acceptable under operator instruction because AgentMiMo has network/API failure and the gate is docs/reviews-only."

Plan §9 stop condition: "the plan requires source/test/runtime edits" → stop.

Plan §6 Slice E: "Only after Slices A-D are reviewed and accepted, write a separate implementation plan. Implementation remains forbidden until that plan has review and controller judgment."

Plan §10: "If DS review passes, create a controller judgment for this plan. Do not enter implementation."

The validation command (§7) is a read-only `git diff --check` on the plan file itself; no source/test/runtime validation is required.

### Review Question 3 — Fail-Closed Invariants, Provider Boundary, Same-Source EvidenceAvailability, Public Chapter Ids 0-7

**PASS.** All invariants are preserved.

Plan §5 lists 12 fail-closed invariants. Cross-referencing against current code and the spike review:

| Plan §5 invariant | Current code evidence |
|---|---|
| exact `required_output`, `anchor` and `missing` marker parsing | `chapter_writer.py:_draft_from_llm_response()` checks `_invalid_marker_issues()`, `_required_structure_issues()`, `_required_output_marker_issues()` |
| unknown anchor fail-closed | `chapter_writer.py` classifies unknown anchors as blocking |
| required-output marker fail-closed | verified in spike DS review finding 4.3 |
| writer structure fail-closed | verified in spike DS review finding 4.3 |
| overlong/incomplete/content-filter writer output fail-closed | `response_too_long`, `response_incomplete` categories in writer parser |
| programmatic audit before semantic audit | `audit_chapter()` always runs programmatic first |
| audit line protocol parse failure as blocking | `_parse_llm_audit_response()` rejects non-conforming lines |
| bounded repair attempts only | `ChapterOrchestrationPolicy.max_repair_attempts` |
| separate runtime vs content failure categories | `ChapterRunResult.failure_category` |
| no deterministic fallback on LLM failure | `QualityFailClosedPolicy.deterministic_fallback_allowed=False` |
| no partial report stdout on failed final assembly | `QualityFailClosedPolicy.fail_on_incomplete_final_assembly=True` |
| final report acceptance only after body readiness and final assembly readiness | `QualityFailClosedPolicy.fail_on_partial_orchestration=True` |
| safe diagnostics only | `SafeDiagnosticPolicy` forbids prompt/draft/raw/secrets |

Provider boundary: Plan §4 explicitly states "Provider writer/auditor clients are not tools. They are Service-constructed typed per-run fields carried into Agent and then passed to Fund tools." This matches `design.md` accepted future ruling and spike recommendation.

Same-source EvidenceAvailability: Plan §4 tool `fund.derive_evidence_availability` description: "Same-source derived input only; no retained artifact or filesystem lookup." Plan §3 Fund section: "same-source EvidenceAvailability." Matches current `derive_evidence_availability()` contract.

Public chapter ids 0-7: Plan §2 non-goals explicitly forbids "public chapter ids 0-7 change." Agent task graph in §3 references "chapters 1-6" (not chapters 0 or 7), consistent with current architecture where chapters 0 and 7 are Service final assembly domain.

### Review Question 4 — ToolRegistry Wrapping Existing Fund Primitives

**PASS.** The plan explicitly wraps, does not rewrite.

Plan §4 opening statement: "The first Agent ToolRegistry must wrap existing Fund primitives, not rewrite them."

Tool table mapping verification against current code:

| Plan tool | Claimed primitive | Current code location |
|---|---|---|
| `fund.project_chapter_facts` | `project_chapter_facts()` | `fund_agent/fund/` — Startup Packet §3 |
| `fund.derive_evidence_availability` | `derive_evidence_availability()` | `fund_agent/fund/evidence_availability.py` |
| `fund.write_chapter` | `write_chapter()` | `fund_agent/fund/chapter_writer.py` |
| `fund.audit_programmatic` | `audit_chapter_programmatic()` | `fund_agent/fund/chapter_auditor.py` |
| `fund.audit_semantic` | `audit_chapter_llm()` | `fund_agent/fund/chapter_auditor.py` |

Boundary rule column is consistent: no repository/PDF/source helper access for projection tools, explicit typed per-run client inputs for writer/auditor tools, deterministic programmatic audit always first-class.

Plan §4 closing statement: "`repair_hint` and issue ids remain Fund output semantics. Agent `RepairPolicy.decide` consumes them but must not redefine Fund rules." This directly addresses spike NBO-3.

### Review Question 5 — Migration Slices and Validation Matrix

**PASS with minor observations.** The slice structure is well-sequenced, and the validation matrix covers the necessary dimensions. See NBO-1 and NBO-2 below for two precision gaps.

Slice A (Agent Dataclass Design): 8 dataclasses listed. Acceptance criterion requires "explicit mapping from current `ChapterOrchestrationResult` / `ChapterRunResult` / `ChapterAttemptRecord` to future Agent state." This is a strong gating condition.

Slice B (Tool Adapter Contract): typed wrappers, input/output schema, error taxonomy, safe trace serialization fields. Explicitly excludes provider client as registry tool.

Slice C (Repair And Budget Contract): addresses spike NBO-2 directly — "distinguish Service provider runtime ceilings from Agent repair attempts"; addresses spike NBO-3 — "define how Fund `repair_hint` and issue ids feed Agent repair policy." Both were controller-accepted follow-up inputs.

Slice D (No-Live Equivalence Validation Plan): deterministic fake writer/auditor tests. Correctly no-live. Does not specify whether "equivalence" means same conclusions, same audit results, or same repair decisions — see NBO-2.

Slice E (Implementation Planning Gate): correctly gated behind Slices A-D acceptance.

Validation matrix (§7) covers 8 requirements: current/future distinction, four-layer ownership, tool wrapping, provider boundary, fail-closed invariants, Dayu boundary, no-live scope, stop conditions. Each row has evidence/source and blocking failure definition.

### Review Question 6 — Stop Conditions

**PASS.** The stop conditions are comprehensive and well-scoped.

Plan §9 lists 7 stop conditions:

1. "the plan requires source/test/runtime edits" — catches implementation creep
2. "the plan introduces `dayu-agent`, `dayu.host`, `dayu.engine`, LangGraph or MCP runtime" — catches forbidden dependencies
3. "the plan moves provider construction into Agent" — catches provider boundary violation
4. "the plan weakens fail-closed chapter acceptance or quality gate semantics" — catches invariant relaxation
5. "reviewer DS is unavailable or blocked" — catches reviewer availability
6. "validation finds formatting errors" — catches artifact quality
7. "user asks to resume live evidence instead" — catches scope shift

Conditions 1-4 are specific to the plan's architectural constraints. Conditions 5-7 are operational. All are appropriate for a `standard` classification design gate.

The plan also correctly inherits the broader prohibitions from `current-startup-packet.md` §7 and `AGENTS.md`.

## Non-Blocking Observations

No observation in this section constitutes a blocking finding or requires plan revision before acceptance.

### NBO-1: EvidenceAvailability Invocation Point Unresolved

Spike DS review NBO-1 asked whether `EvidenceAvailability` is computed inside Agent task setup or passed as Service-prepared task input. The controller judgment (§3 NBO-1 disposition) required the Agent Engine Design Refresh Gate plan to decide this.

The plan lists `fund.derive_evidence_availability` as a tool (§4 tool table), which implies Agent invokes it during task execution (not precomputed by Service and passed as input). The tool's boundary rule ("Same-source derived input only; no retained artifact or filesystem lookup") is correct. However, the plan does not explicitly state the invocation point in the Agent task lifecycle — e.g., whether it's called once at `ChapterTaskPrepared` (precomputed) or called on-demand during the write/audit loop.

The current Service `ChapterOrchestrator` precomputes `EvidenceAvailability` before the per-chapter loop. If Agent later invokes it as a tool, the design should clarify whether it's called once per chapter (at task setup) or potentially multiple times (e.g., after repair). This is resolvable in Slice A or B design.

**Severity**: informational. The tool-as-wrapper approach is valid regardless of invocation point. The implementation planning gate or Slice A/B design should resolve the exact lifecycle.

### NBO-2: Equivalence Test Scope Underspecified

Plan §6 Slice D describes "deterministic fake writer/auditor equivalence tests against current Service `ChapterOrchestrator`" but does not define the equivalence criteria. Possible interpretations:

- Same `ChapterOrchestrationResult` (accepted/failed/blocked per chapter)
- Same chapter conclusions (content-level equivalence)
- Same audit issue ids and repair decisions
- Same final assembly readiness signal

The current `ChapterOrchestrator` is a Service façade that will eventually be retired; the equivalence tests should verify that the future Agent task graph produces the same accept/fail/block outcomes for the same inputs, not that it produces identical internal state. The implementation planning gate (Slice E) can resolve this.

**Severity**: informational. The slice is design-only; exact equivalence criteria belong in the implementation planning gate.

### NBO-3: FinalAssemblyReadiness Handoff Boundary

Plan §3 Agent section says Agent should own "final body chapter readiness matrix." Plan §3 Service section does not explicitly mention consuming this matrix for final assembly. Current code has Service-owned `FinalChapterAssembler` with its own readiness check.

`design.md` §2.1 accepted future ruling states: "`FinalAssemblyReadiness` 未来可 feed or replace current Service `FinalChapterAssembler` readiness check，但必须保持当前 stdout/fail-closed 语义直到独立 implementation gate 接受。" The plan's readiness matrix handoff is consistent with this ruling, but the plan does not restate the constraint that stdout/fail-closed semantics must survive the handoff.

**Severity**: informational. The fail-closed invariant checklist (§5) already covers this ("final report acceptance only after body readiness and final assembly readiness"), and the design.md ruling is authoritative.

## Validation

Local no-live read-only commands used:

```text
Read: AGENTS.md, docs/design.md (offset 1-500, 500-1000), docs/current-startup-packet.md, docs/implementation-control.md (offset 1-300)
Read: docs/reviews/mvp-llm-tool-calling-state-machine-calibration-spike-20260607.md
Read: docs/reviews/mvp-llm-tool-calling-state-machine-calibration-spike-review-ds-20260607.md
Read: docs/reviews/mvp-llm-tool-calling-state-machine-calibration-spike-controller-judgment-20260607.md
Read: docs/reviews/mvp-agent-engine-design-refresh-gate-plan-20260607.md
```

No live command, provider probe, endpoint check, runtime/default change, code implementation, PR, push, or external action was performed.

## Summary

The plan correctly separates Service/Host/Agent/Fund ownership per `AGENTS.md` and `design.md`, prevents implementation creep with strong non-goals and stop conditions, preserves all 12 fail-closed invariants with explicit code-anchored evidence, wraps existing Fund primitives without rewriting Fund logic, sequences 5 well-gated migration slices with a sufficient validation matrix, and enforces comprehensive stop conditions covering Dayu/LangGraph/MCP, provider boundary, and live commands. Three non-blocking observations are recorded for the next design slices: EvidenceAvailability invocation point, equivalence test scope, and FinalAssemblyReadiness handoff constraint. None requires plan revision.
