# MVP internalized Agent engine implementation planning plan — MiMo Re-Review

## Worker Self-Check

- Role: AgentMiMo plan re-review worker only; not controller, not implementation.
- Gate: `MVP internalized Agent engine implementation planning gate`.
- Classification: `heavy`.
- CWD: /Users/maomao/fund-agent
- Output artifact: this file.
- Required reads completed: `AGENTS.md`, plan artifact, DS review, MiMo review, fix evidence.
- Actions intentionally not taken: no source code, test, config, or doc edits; no live provider probe; no runtime/provider command.

## Re-Review Focus

Reassess only the five items requested by the controller:

### 1. DS B1 — RepairSemantics contract shape sufficient for implementation workers?

**Status: FIXED.**

The plan now contains a concrete `RepairSemantics` contract (lines 135–189) with:

- Module placement: `fund_agent/fund/repair_semantics.py`.
- Slice placement: Slice 3, before `fund.repair_semantics` is registered in `ToolRegistry`.
- `RepairSemanticsAction` — 5-value `Literal` enum including `stop_fail_closed`.
- `RepairSemanticsInput` — 8 typed fields: `chapter_id`, `attempt_index`, `remaining_repair_budget`, `audit_status`, `aggregate_repair_hint`, `issues`, `evidence_availability`, `typed_chapter_contract`.
- `RepairIssueSemantics` — 10 typed fields covering issue id, rule code, repairable flag, action, required correction, tied clause/item/fact/anchor ids, evidence blocked flag.
- `RepairSemanticsOutput` — 9 typed fields including `aggregate_action`, `stop_reason`, `required_corrections`, `issue_semantics`, `source_repair_hint`, `source_issue_ids`.
- 7 explicit mapping source and precedence rules covering: hint-none, evidence-blocked, auditor-blocked, patch/regenerate with budget, budget-exhausted, and needs-more-facts cases.
- Agent consumption constraints: `RepairPolicy` consumes only `aggregate_action`, `stop_reason`, `required_corrections`, `source_issue_ids`, and `issue_semantics[*].repairable/evidence_blocked`.

**Verdict**: Sufficient for Slice 3 implementation. An implementation worker can create the module, implement the mapping rules, and produce a typed output without inventing any contract detail. The precedence rules are deterministic and testable.

**Residual**: Implementation workers must verify the migrated deterministic correction mapping against current `_required_correction_from_issue` / `_required_corrections_from_issues` / `_repair_context_from_audit` in `chapter_orchestrator.py`. This is a code-matching task, not a contract gap.

---

### 2. DS B2 — AgentRunControl Protocol signature and Service adapter location sufficient, not leaking Host internals?

**Status: FIXED.**

The plan now specifies (lines 191–239):

- Exact Protocol with 5 methods and full Python signatures:
  - `raise_if_cancelled_or_deadline_exceeded() -> None`
  - `deadline_exceeded() -> bool`
  - `record_phase_started(*, phase, chapter_id, attempt, provider_attempt) -> None`
  - `record_phase_completed(*, phase, chapter_id, attempt, provider_attempt, elapsed_ms) -> None`
  - `record_diagnostic(**diagnostics: object) -> None`
- Usage constraints: runner calls `raise_if_cancelled_or_deadline_exceeded()` before each chapter task, before/after each tool call, and before returning result.
- Safe phase names restricted to: `agent_task`, `tool_call`, `repair_policy`, `final_readiness`.
- `record_diagnostic()` restricted to allowlisted safe scalar diagnostics; forbidden fields explicitly listed.
- Adapter location: `fund_agent/services/agent_adapter.py`, class `ServiceAgentRunControlAdapter`.
- Dependency direction: Service imports concrete `HostRunContext` and Agent Protocol; Agent imports neither Service nor concrete Host.
- Host internals NOT exposed: `run_id`, `deadline_at`, `timeout_seconds`, `cancellation_token` are explicitly excluded from the Protocol.

**Verdict**: Sufficient for Slice 1 (Protocol definition) and Slice 5 (adapter implementation). The Protocol mirrors only the Host methods Agent actually needs. The forbidden fields list prevents internal leakage. Implementation workers can write both the Protocol and adapter without ambiguity.

**Residual**: `record_diagnostic(**diagnostics: object)` uses `**kwargs` which could theoretically receive unsafe keys at runtime. The plan's text constraint ("must never receive prompt, draft, …") is a documentation-level guard. Implementation workers should add an allowlist-key assertion in the adapter or Protocol implementation. This is a low-severity implementation detail, not a contract gap.

---

### 3. DS B3 — AgentRunResult → ChapterOrchestrationResult / ChapterRunResult mapping table sufficient, preserving fail-closed/artifact/CLI semantics?

**Status: FIXED.**

The plan now contains a 16-row explicit mapping table (lines 241–271) plus terminal mapping invariants (lines 273–280):

| Coverage | Detail |
|---|---|
| `fund_code`, `report_year` | Copied from original Service input, not from trace |
| `projection` | Same `ChapterFactProjection` used for Agent input |
| `generated_chapter_ids` | Every chapter with a `ChapterTask` attempted; failed chapters count |
| `skipped_chapter_ids` | Only Service-global scope skips; previous failures don't skip later chapters |
| Terminal state mapping | `accepted` → accepted, `partial_fail_closed` → partial, `host_interrupted` → blocked |
| Per-chapter status | 4 cases (accepted/blocked/failed/skipped) each with typed `stop_reason` mapping |
| `accepted_draft`, `accepted_conclusion` | Copy only for accepted chapters; `None` otherwise |
| `attempts` | Convert to `ChapterAttemptRecord` preserving attempt index, writer/audit result, repair projection, safe diagnostics |
| `RepairSemanticsOutput` → `ChapterRepairDecision` | Explicit action mapping: `none→none`, `regenerate/patch→regenerate`, `needs_more_facts→needs_more_facts`, `stop_fail_closed→stop` |
| ToolTrace → `runtime_diagnostics` | ToolTrace is superset; adapter projects safe scalars to `ChapterLLMRuntimeDiagnostic`; Agent-only phases are additive |
| `accepted_conclusions` | Preserved in chapter order, accepted body chapters only |
| `AgentFinalAssemblyReadiness` | Diagnostic/projection only; Service `FinalChapterAssembler` remains authority |
| Failure category/subcategory | Reuse existing Service classifiers; no new enum values in MVP |

Terminal mapping invariants confirm:
- `accepted` requires ALL target body chapters accepted with non-null draft and conclusion.
- Non-accepted body → `partial`, unless Host interruption → `blocked`.
- `QualityFailClosedPolicy.fail_on_partial_orchestration=True` preserves empty stdout / exit 1 / no deterministic fallback.
- `chapter_policy` stays at Service level, not pushed to Agent or Host.

**Verdict**: Sufficient for Slice 5 implementation. The mapping table covers every field currently consumed by `FinalChapterAssembler` and `llm_run_artifacts.py`. Fail-closed behavior is explicitly preserved. CLI semantics (empty stdout, exit 1) are unchanged.

**Residual**: Implementation workers must verify the adapter output against existing `FinalChapterAssembler` and artifact serializer tests. The mapping table is contract-complete; verification is an integration test task.

---

### 4. Direct clarifications: AgentFinalAssemblyReadiness naming conflict and ToolTrace safe diagnostic superset

**Status: BOTH FIXED.**

**AgentFinalAssemblyReadiness naming**: The plan consistently uses `AgentFinalAssemblyReadiness` (lines 117, 129–133, 271) for the Agent-side type. The existing Service `FinalAssemblyReadiness` in `final_chapter_assembler.py` is not renamed. The plan explicitly states: "Do not replace Service type. Use Agent readiness as a precomputed diagnostic/projection; Service `FinalChapterAssembler` remains final authority in first MVP" (line 271). No import collision risk.

**ToolTrace safe diagnostic superset**: The plan states (lines 282–285): "ToolTrace must be a safe superset of currently serialized `ChapterLLMRuntimeDiagnostic` scalar fields" and enumerates the complete field list: operation/tool id, chapter id, repair attempt index, provider attempt index, provider max attempts, runtime category, failure category, elapsed ms, status code, request id, model name, finish reason, response chars, error type, prompt char/token counts, allowed fact/anchor counts, max output chars, timeout seconds, timeout retry budget, timeout budget kind, repair timeout fallback flag, timeout root-cause hint and bounded safe message. Forbidden fields are also explicitly listed (line 125): prompt, draft, repair draft, raw provider response, raw audit response, API key, Authorization header, cookies, provider hidden config, raw PDF/text.

**Verdict**: Both clarifications are resolved with sufficient precision. No naming collision risk. ToolTrace field contract is explicit. Implementation workers can proceed.

---

### 5. No new provider/runtime/live probe/score-loop/multi-year/dayu/extra_payload risks

**Status: CONFIRMED — no new risks.**

Checked against:

- Non-Goals section (lines 28–41): explicitly prohibits live provider probe, provider budget/default changes, score-loop, multi-year runtime, template truth replacement, Ch3 calibration, dayu runtime dependency, provider clients as tools, extra_payload/kwargs, Host business inspection, parallel scheduling.
- Implementation Decisions (lines 309–321): reinforces all boundaries.
- Stop Conditions (lines 529–546): covers all prohibited scenarios with explicit halt criteria.
- Fix evidence confirms: no provider/default/runtime budget changes, no live probe, no score-loop, no dayu dependency, no extra_payload.

The fix additions (RepairSemantics, AgentRunControl, mapping table, naming clarification, ToolTrace superset) are purely additive contract specifications. They do not introduce any new provider, runtime, live probe, score-loop, multi-year, dayu, or extra_payload risk.

---

## Findings (severity ordered)

### F1. `record_diagnostic(**diagnostics: object)` runtime safety (Low, non-blocking)

**Evidence**: Plan line 224 defines `record_diagnostic(self, **diagnostics: object) -> None`. The plan text (line 232) constrains this to "allowlisted safe scalar diagnostics" and forbids prompt, draft, raw responses, API keys, etc.

**Why non-blocking**: The constraint is clear. Implementation workers can add an allowlist-key assertion in the adapter or a decorator on the Protocol method. The `**kwargs` signature gives implementation flexibility for different safe diagnostic shapes across phases.

**Why it matters**: Without a runtime assertion, a future caller could accidentally pass an unsafe key. A test in `tests/agent/test_agent_run_control.py` verifying that forbidden keys raise is a sufficient mitigation.

### F2. Migration source verification for RepairSemantics correction mapping (Low, non-blocking)

**Evidence**: Plan line 181 says the source of truth is "the deterministic correction mapping migrated from current Service repair helpers (`_required_correction_from_issue`, `_required_corrections_from_issues`, `_repair_context_from_audit`)." These functions exist in `chapter_orchestrator.py`.

**Why non-blocking**: The contract shape is complete. Implementation workers must verify that the migrated mapping produces identical corrections for existing test cases. This is a code-matching task during Slice 3.

**Why it matters**: If the migration introduces a divergent correction text, audit-driven repair will produce different writer input, potentially changing chapter output.

---

## Boundary Compliance (unchanged from original review)

All boundary checks from the original MiMo review still hold. The fix additions do not alter any layer ownership:

| Layer | Ownership | Status |
|---|---|---|
| Service | use case, ExecutionContract, provider construction, runtime ceilings, quality policy, final product mapping, `ServiceAgentRunControlAdapter`, `ServiceAgentResultAdapter` | ✓ |
| Host | lifecycle-only: global deadline, cancel, terminal state, safe diagnostics | ✓ |
| Agent | runner, task graph, tool loop, ToolRegistry, ToolTrace, RepairPolicy, AgentFinalAssemblyReadiness, AgentRunControl Protocol | ✓ |
| Fund | domain tools, typed contracts, EvidenceAvailability, writer, audit, RepairSemantics | ✓ |

---

## B1/B2/B3 Fixed Status

| Finding | Status | Evidence |
|---|---|---|
| DS B1 — RepairSemantics contract shape | **FIXED** | Lines 135–189: 3 typed types, 7 precedence rules, module/slice placement, Agent consumption constraints |
| DS B2 — AgentRunControl Protocol signature and adapter | **FIXED** | Lines 191–239: 5 Protocol methods with full signatures, adapter location/class, Host internals excluded |
| DS B3 — AgentRunResult → Service mapping | **FIXED** | Lines 241–280: 16-row mapping table, terminal invariants, fail-closed preservation, ToolTrace compatibility |

---

## Verdict

**PASS**

All three DS blocking findings (B1, B2, B3) are resolved with sufficient precision for implementation workers to execute Slices 0–5 without inventing contract details. Both direct clarifications (naming conflict, ToolTrace superset) are addressed. No new provider/runtime/live probe/score-loop/multi-year/dayu/extra_payload risks have been introduced by the fixes. The two new low-severity findings (F1, F2) are implementation-time verification tasks, not contract gaps, and do not block plan acceptance.

---

## Secret-Safety Statement

This review artifact contains no API key, Authorization header, Bearer token, cookie, password, raw provider response, raw audit response, prompt body, writer draft body, repair draft body, hidden provider config value, or raw PDF/source text. It references only safe file paths, type names, enum labels, line numbers, and architectural assessments.
