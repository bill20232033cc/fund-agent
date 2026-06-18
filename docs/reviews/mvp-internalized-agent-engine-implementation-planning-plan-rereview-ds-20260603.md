# MVP internalized Agent engine implementation planning plan — DS Re-Review

## Worker Self-Check

- Role: AgentDS plan re-review worker only; not controller, not implementation.
- Gate: `MVP internalized Agent engine implementation planning gate`.
- Classification: `heavy`.
- CWD: /Users/maomao/fund-agent
- Output artifact: this file.
- Required reads completed: `AGENTS.md`, `docs/reviews/mvp-internalized-agent-engine-implementation-planning-plan-20260603.md`, `docs/reviews/mvp-internalized-agent-engine-implementation-planning-plan-review-ds-20260603.md`, `docs/reviews/mvp-internalized-agent-engine-implementation-planning-plan-review-mimo-20260603.md`, `docs/reviews/mvp-internalized-agent-engine-implementation-planning-plan-fix-evidence-20260603.md`.
- Actions intentionally not taken: no source/test/config/runtime edits, no live provider probe, no commit/push/PR.

## Verdict

**PASS** — All 3 original DS blocking findings (B1/B2/B3) are fixed with sufficient precision for implementation handoff. Both direct clarifications (AgentFinalAssemblyReadiness naming, ToolTrace safe diagnostic superset) are addressed. No new provider/runtime/live probe/score-loop/multi-year/dayu/extra_payload risks introduced.

---

## Re-Review Findings

### Finding 1: DS B1 — RepairSemantics Contract Shape (FIXED)

**Original finding**: Plan provided zero fields, no input/output types, no mapping format. Slice 4's `PLAN_REPAIR` state could not be implemented without the contract shape.

**What changed**: Plan now includes a complete "Concrete RepairSemantics Contract" section (plan lines 135–189) with:

- Module placement: `fund_agent/fund/repair_semantics.py`, Slice 3.
- Five typed structures: `RepairSemanticsAction` (5-value enum), `RepairSemanticsInput` (9 fields), `RepairIssueSemantics` (11 fields), `RepairSemanticsOutput` (8 fields), and the Agent consumption subset.
- Mapping source: Fund audit output + deterministic correction mapping migrated from current Service repair helpers (`_required_correction_from_issue`, `_required_corrections_from_issues`, `_repair_context_from_audit`).
- Six explicit precedence rules covering: no-issue pass, evidence-blocked, auditor-blocked, regenerate with budget, budget exhausted, needs_more_facts.
- Agent `RepairPolicy` consumption subset explicitly scoped to `aggregate_action`, `stop_reason`, `required_corrections`, `source_issue_ids`, `issue_semantics[*].repairable/evidence_blocked`.

**Assessment**: The contract shape is implementation-ready. The input captures all signals the Fund domain needs (audit status, issues, evidence availability, typed contract, remaining budget). The output provides deterministic aggregate action, per-issue semantics, and deduplicated corrections. The `patch` action is preserved at issue level but explicitly deferred ("not executed as in-place patch in the first MVP"), which is an acceptable MVP scope boundary.

**Minor observation**: `tied_clause_ids` is qualified with "when known." This is acceptable for MVP since `CHAPTER_CONTRACT` clause tracing from audit issues is bounded by current `ChapterAuditIssue` output. Implementation can return empty tuple when clause mapping is unavailable.

**Verdict: FIXED.**

---

### Finding 2: DS B2 — AgentRunControl Protocol Signature and Adapter Location (FIXED)

**Original finding**: Protocol methods, signatures, and return types were not listed. Service adapter location was unspecified. Runner cancellation observation points were ambiguous.

**What changed**: Plan now includes an "AgentRunControl Protocol And Adapter" section (plan lines 191–239) with:

- Exact Protocol shape: 5 methods with complete signatures.
- `raise_if_cancelled_or_deadline_exceeded() -> None`
- `deadline_exceeded() -> bool`
- `record_phase_started(*, phase, chapter_id, attempt, provider_attempt) -> None`
- `record_phase_completed(*, phase, chapter_id, attempt, provider_attempt, elapsed_ms) -> None`
- `record_diagnostic(**diagnostics: object) -> None`
- Adapter name: `ServiceAgentRunControlAdapter`, file: `fund_agent/services/agent_adapter.py`, Slice 5.
- Dependency direction: Service imports both concrete `HostRunContext` and Agent Protocol; Agent imports neither.
- Adapter constraint: must not expose `run_id`, `deadline_at`, `timeout_seconds`, `cancellation_token` to Agent.
- Usage constraints: call points before each chapter task, before each tool call, after each tool call, before returning `AgentRunResult`.
- Safe phase names only: `agent_task`, `tool_call`, `repair_policy`, `final_readiness`.
- Diagnostic content constraint: no prompt, draft, repair draft, raw provider/audit response, API key, Authorization header, cookies, raw document text.

**Assessment**: The Protocol is a clean subset of `HostRunContext` that excludes all Host-internal fields. The 5 methods cover Agent's lifecycle observation needs: pre/post-operation cancellation check, deadline polling for post-tool classification, phase/diagnostic recording for trace continuity. The adapter location follows AGENTS.md boundary rules (Service may import Host and Agent types). No Host internals leak into Agent.

**Verdict: FIXED.**

---

### Finding 3: DS B3 — AgentRunResult → ChapterOrchestrationResult / ChapterRunResult Mapping (FIXED)

**Original finding**: Slice 5 could not be implemented without knowing which Agent fields map to which Service fields. `FinalChapterAssembler` and `llm_run_artifacts.py` expect specific shapes.

**What changed**: Plan now includes an "AgentRunResult To Service Mapping" section (plan lines 241–285) with:

- 20-row mapping table covering: fund_code, report_year, projection, generated/skipped chapter ids, terminal state, per-chapter status, accepted drafts/conclusions, attempt ledger, repair decision projection, issues, failure categories, ToolTrace entries, accepted_conclusions, AgentFinalAssemblyReadiness.
- Terminal mapping invariants:
  - `accepted` requires every target body chapter with `accepted` status and non-null draft/conclusion.
  - Non-accepted body chapter → `partial`, unless Host interruption → `blocked`.
  - `QualityFailClosedPolicy.fail_on_partial_orchestration=True` preserves empty stdout, exit code 1, no deterministic fallback.
- ToolTrace compatibility note: must be a safe superset of current `ChapterLLMRuntimeDiagnostic` scalar fields; Agent-only tool phases remain additive artifact diagnostics.
- CLI semantics preserved: `projection`, `fund_code`, `report_year` copied from original Service input, not from Agent trace.
- Failure category constraint: reuse existing Service classifiers; no new Service enum values without separate acceptance.

**Assessment**: The mapping table is comprehensive. Every field on `ChapterOrchestrationResult` and `ChapterRunResult` that `FinalChapterAssembler` and `llm_run_artifacts.py` consume has a mapping rule. The terminal invariants correctly encode fail-closed semantics. The ToolTrace superset requirement ensures existing artifact retention does not lose root-cause evidence. The failure category constraint is slightly fuzzy ("map only to existing enums") but explicitly scoped and gated on separate acceptance for new values — acceptable for MVP.

**Overlap with MiMo F1**: MiMo's `ChapterOrchestrationResult` adapter shape gap (F1) is fully addressed by this mapping table. MiMo F2 (ToolTrace diagnostic mapping) is addressed by the ToolTrace compatibility note.

**Verdict: FIXED.**

---

### Finding 4: Direct Clarifications — Naming and Diagnostics (ADDRESSED)

**AgentFinalAssemblyReadiness naming conflict (DS O4)**:

Plan line 129 defines `AgentFinalAssemblyReadiness` (with `ready`, `incomplete`, `blocked` statuses). The existing Service type is `FinalAssemblyReadiness` (different fields). Names are now distinct. Fix evidence explicitly confirms this rename. No import collision risk.

**ToolTrace safe diagnostic superset**:

Plan lines 283–285 (ToolTrace compatibility note) explicitly states ToolTrace must be a safe superset of current `ChapterLLMRuntimeDiagnostic` scalar fields and remain projectable into existing artifact diagnostics. This addresses the original DS H1 concern about serialization contract specification and the MiMo F2 concern about lossless safe-field mapping.

**Verdict: ADDRESSED.**

---

### Finding 5: Risk Surface Check — No New Risks (CLEAN)

Checked the updated plan for any newly introduced risks against the prohibition checklist:

| Risk Vector | Status |
|---|---|
| Provider/runtime/live probe | Clean — non-goals and stop conditions unchanged; all validation uses fake clients |
| Score-loop | Clean — explicitly excluded in non-goals |
| Multi-year runtime | Clean — explicitly excluded in non-goals |
| Dayu runtime dependency | Clean — explicitly forbidden in non-goals and stop conditions |
| extra_payload / kwargs bags | Clean — all parameters typed, no free-form dicts |
| Provider clients in ToolRegistry | Clean — explicit exclusion preserved |
| Host business inspection | Clean — `AgentExecutionPolicy` excludes fund fields; Protocol hides Host internals |
| Template truth replacement | Clean — chapter ids stay 0-7, `typed_template_contract` preserved |
| Ch3 calibration | Clean — deferred |
| Programmatic audit relaxation | Clean — `audit_focus` bounded; programmatic remains authoritative |
| Parallel scheduling creep | Clean — sequential-first preserved |

No new stop conditions, risks, or open questions introduced by the fixes that weren't already present in the original plan.

**Verdict: CLEAN.**

---

## Original DS Blocking Findings Status

| Finding | Status | Evidence Location |
|---|---|---|
| B1: RepairSemantics contract shape | **FIXED** | Plan lines 135–189 |
| B2: AgentRunControl Protocol signature + adapter | **FIXED** | Plan lines 191–239 |
| B3: AgentRunResult → Service mapping table | **FIXED** | Plan lines 241–285 |

---

## Overlap with MiMo Findings

The DS B1–B3 fixes also resolve the overlapping MiMo non-blocking findings:

| MiMo Finding | Overlap | Status |
|---|---|---|
| F1: ChapterOrchestrationResult adapter shape | DS B3 | Resolved by mapping table |
| F2: ChapterRunResult.attempts diagnostic mapping | DS B3 + ToolTrace note | Resolved |
| F3: AgentRunControl Protocol shape | DS B2 | Resolved |
| F4: RepairSemantics decision | DS B1 | Resolved (committed to new module) |
| F5: ToolRegistry envelope | N/A (Slice 2 design) | Unchanged — deferred to Slice 2 |
| F6: Legacy path burden | N/A (follow-up gate) | Unchanged — correctly deferred |
| F7: Test scenario enumeration | N/A (implementation detail) | Unchanged — deferred to implementation |

---

## Residual Observations (Non-Blocking)

### RO1. `RepairSemanticsInput.remaining_repair_budget` boundary

Repair budget is an Agent concern, but `RepairSemantics` is Fund-owned. Passing `remaining_repair_budget` as input is justified (Fund needs it to decide `stop_fail_closed` when budget is exhausted), but the plan should emphasize in Slice 3 that Fund's `RepairSemantics` must not independently track or enforce repair budgets — it only reads the budget to inform its action decision. The plan already says "Agent RepairPolicy … may count attempts and enforce budgets, but it must not invent new rule-code mappings," which implicitly covers this.

### RO2. Failure category mapping fuzziness

The B3 mapping table says for failure category: "Reuse current Service classifiers where possible; otherwise map only to existing enums and add unmapped Agent detail to additive diagnostics." If Agent discovers a failure mode with no matching Service enum, the implementation worker will need to decide: map to a closest-match enum (potentially lossy) or add a new enum (blocked by plan constraint). This is a known MVP scope limitation and acceptable, but Slice 5 implementation should document any unmappable categories as residuals.

### RO3. `RepairSemantics` migration from Service repair helpers

The plan references current Service helpers (`_required_correction_from_issue`, `_required_corrections_from_issues`, `_repair_context_from_audit`) as the migration source. These are internal implementation details of `chapter_orchestrator.py`. If they contain business logic that belongs in Fund, the migration is correct. If they contain Service-orchestration logic, extracting them requires care. Slice 3 implementation should verify that only Fund-domain correction logic is migrated, not Service orchestration policy.

---

## Validation Performed

1. Compared original DS review B1/B2/B3 text against current plan to confirm all three contract gaps are filled.
2. Traced every new contract field from plan to verify it has a defined type, source, and consumer.
3. Verified `AgentRunControl` Protocol exports no Host-internal fields (`run_id`, `deadline_at`, `timeout_seconds`, `cancellation_token` are absent).
4. Verified B3 mapping table covers every `ChapterOrchestrationResult` / `ChapterRunResult` field consumed by `FinalChapterAssembler` and `llm_run_artifacts.py`.
5. Cross-referenced DS findings with MiMo findings to confirm overlapping concerns are resolved.
6. Re-checked non-goals, stop conditions, and prohibition list against updated plan for regression.
7. Confirmed no new provider/runtime/live probe/score-loop/multi-year/dayu/extra_payload language introduced.

No runtime/provider/live probe command was executed.

---

## Secret-Safety Statement

This re-review artifact contains no API key, Authorization header, Bearer token, cookie, password, raw provider response, raw audit response, prompt body, writer draft body, repair draft body, hidden provider config value, or raw PDF/source text. It references only safe file paths, type names, enum labels, and architectural assessments.
