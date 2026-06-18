# MVP internalized Agent engine implementation planning plan — DS Review

## Worker Self-Check

- Role: AgentDS plan review worker only; not controller, not implementation.
- Gate: `MVP internalized Agent engine implementation planning gate`.
- Classification: `heavy`.
- Scope: review-only artifact; no source code, runtime config, provider, or truth doc edits.
- Required reads completed: `AGENTS.md`, `docs/design.md`, `docs/implementation-control.md`, `docs/current-startup-packet.md`, plan artifact, tool-loop design artifact and controller judgment, `chapter_orchestrator.py`, `execution_contract.py`, `final_chapter_assembler.py`, `chapter_writer.py`, `chapter_auditor.py`, `evidence_availability.py`, `host/runtime.py`.
- Actions intentionally not taken: no source/test/config/runtime edits, no live provider probe, no commit/push/PR.

## Verdict

**PASS-WITH-RISKS** — 3 blocking findings, 5 high-severity non-blocking findings.

The plan is structurally sound, correctly maps the accepted design to implementation slices, and preserves all boundary, fail-closed, and non-goal constraints. However, three contracts are underspecified to the point that an implementation worker would need to invent them, and several details lack the precision needed for code-generation-ready handoff.

---

## Blocking Findings

### B1. `RepairSemantics` contract shape is undefined

- Evidence: plan lines 229–230, 398–399; design artifact lines 130–131.
- Detail: The plan proposes registering `fund.repair_semantics` as a tool in Slice 3 (line 229), and the design artifact says "Fund owns `RepairSemantics`: what an issue means, whether it is repairable, which clause/item/evidence state it is tied to, and the issue-to-repair-action mapping." But the plan provides zero fields, no input/output types, no mapping format. The current `ChapterAuditRepairHint` is a `Literal["none", "patch", "regenerate", "needs_more_facts"]` — a four-value enum. The plan acknowledges (line 399) that this "may be too coarse for stable Agent `RepairPolicy`."
- Why blocking: Slice 4's `PLAN_REPAIR` state consumes `RepairSemantics` output to decide stop/retry. Without the contract shape, the state machine cannot be implemented. The plan itself lists this as an open risk (line 399).
- Required fix: Define at minimum: `RepairSemanticsInput` (issue_ids, audit_hints, evidence_availability, remaining_budget), `RepairSemanticsOutput` (per-issue repairable boolean, repair action, required corrections, tied clause/item ids), and `RepairSemantics` function/class signature. This must be done before Slice 3 implementation starts.

### B2. `AgentRunControl` Protocol signature is unspecified

- Evidence: plan lines 163–164, 247; design artifact lines 102–103.
- Detail: The plan says "Define an Agent-side `AgentRunControl` Protocol with `raise_if_cancelled_or_deadline_exceeded()` and safe phase event methods." The current `HostRunContext` (host/runtime.py:216–368) exposes: `run_id`, `deadline_at`, `timeout_seconds`, `cancellation_token`, `raise_if_cancelled_or_deadline_exceeded()`, `record_phase_started()`, `record_phase_completed()`, `record_diagnostic()`, `cancel_if_deadline_exceeded()`, `deadline_exceeded()`. The Agent Protocol must subset these to avoid leaking Host internals (e.g., `run_id`, `cancellation_token` raw access). The plan does not list which methods are on the Protocol, their signatures, or return types.
- Why blocking: Slice 4 runner observes `AgentRunControl` before each task, before each tool call, and after tool returns (plan line 247). Without the Protocol signature, the runner's cancellation observation points are ambiguous, and the Service adapter that bridges `HostRunContext` → `AgentRunControl` cannot be written.
- Required fix: Specify the exact Protocol methods: at minimum `raise_if_cancelled_or_deadline_exceeded() -> None`, `record_phase_started(*, phase, chapter_id, attempt) -> None`, `record_phase_completed(*, phase, chapter_id, attempt, elapsed_ms) -> None`. Confirm whether Agent also needs `deadline_exceeded() -> bool` for mid-tool-call checks.

### B3. `AgentRunResult` → `ChapterOrchestrationResult` mapping is not specified

- Evidence: plan lines 264–265, 397; current `ChapterOrchestrationResult` fields in chapter_orchestrator.py (output object with `status`, `fund_code`, `report_year`, `chapter_results`, `failure_category`, `first_failed_category`, `first_failed_subcategory`, `runtime_diagnostics`, `chapter_policy`, etc.).
- Detail: The proposed `AgentRunResult` (plan lines 113–118) has: `terminal_state` (enum), `per-chapter matrix`, `accepted drafts/conclusions` for chapters 1-6, `FinalAssemblyReadiness`, `safe ToolTrace summary`. The current `ChapterOrchestrationResult` consumed by `FinalChapterAssembler` (final_chapter_assembler.py:109) and artifact serialization (`llm_run_artifacts.py`) has a different shape with `status`, `chapter_results: tuple[ChapterRunResult, ...]`, `fund_code`, `report_year`, etc. The plan says Slice 5 must "convert `AgentRunResult` back to the current `ChapterOrchestrationResult` shape" (line 264) but provides no field mapping table.
- Why blocking: Slice 5 cannot be implemented without knowing which Agent fields map to which Service fields. The `FinalChapterAssembler` (final_chapter_assembler.py:263) expects `ChapterOrchestrationResult` with specific fields; the artifact serializer expects per-chapter results with specific shapes. A wrong mapping would break fail-closed behavior silently.
- Required fix: Provide an explicit field mapping table: `AgentRunResult.terminal_state -> ChapterOrchestrationResult.status`, `AgentRunResult.per_chapter_matrix[ch_id].status -> ChapterRunResult.status`, etc. Identify any Agent fields that have no Service counterpart and must be carried as additive diagnostics only.

---

## High-Severity Non-Blocking Findings

### H1. ToolTrace allowlist serializer described but not specified

- Evidence: plan lines 123–125, 297–301, 400.
- Detail: The plan says "allowlist-only fields" and lists forbidden fields (prompt, draft, raw provider response, raw audit response, API key, Authorization header). But the actual serialization function contract — input type, output format, error behavior on forbidden field, relationship to existing `serialize_chapter_runtime_diagnostics()` / `serialize_chapter_prompt_contract_diagnostics()` in chapter_orchestrator.py — is not specified. The plan itself calls this out as an open risk (line 400).
- Why non-blocking: Slice 2 (ToolTrace foundation) is explicitly scoped to implement this with fake tools and tests, so the contract can be refined during implementation. But the plan should at minimum declare the function signature.
- Recommendation: Add `serialize_tool_trace(entries: tuple[ToolTraceEntry, ...]) -> dict[str, object]` with explicit return shape and allowlist validation error behavior before Slice 2 starts.

### H2. `audit_focus` typed enforcement mechanism not specified

- Evidence: plan line 165–166; design artifact line 205.
- Detail: The plan says "Keep `audit_focus` as bounded semantic-audit input only. It cannot disable programmatic audit or downgrade blockers." Current code at `chapter_auditor.py:1455–1481` already validates `audit_focus` against `SUPPORTED_AUDIT_FOCUS` closed set. But the plan doesn't specify whether this existing guard is sufficient, or whether a new typed enforcement layer is needed at the Agent `RepairPolicy` level to prevent a semantic audit pass from overriding a programmatic failure.
- Why non-blocking: The current Fund auditor already separates programmatic/semantic audit and aggregates status correctly (chapter_auditor.py:539–552: `blocked > fail > pass`). The Agent runner can preserve this with `programmatic status == fail -> skip semantic audit or semantic result cannot override`. The design controller judgment (line 28) already accepted that programmatic audit remains authoritative.
- Recommendation: In Slice 4, explicitly encode the rule: "if programmatic audit status is `fail` or `blocked`, semantic audit result does not change chapter acceptance." Add a test for this in `tests/agent/test_chapter_runner.py`.

### H3. Slice 3 scope is conditional on RepairSemantics decision

- Evidence: plan lines 229–230: "Add or expose Fund `RepairSemantics` if current `ChapterAuditRepairHint` is insufficient as a stable typed domain contract."
- Detail: The plan lists `fund.repair_semantics` as a tool to register in Slice 3, but makes it conditional. If `ChapterAuditRepairHint` is deemed sufficient, Slice 3 has one less tool to wrap. If not, a new Fund module must be designed first (see B1). This ambiguity means Slice 3's implementation scope is undecided.
- Why non-blocking: The Slice 0 preflight can decide this by auditing current `ChapterAuditRepairHint` usage across `chapter_orchestrator.py` repair planning. If the four-value enum covers all cases, Slice 3 can skip `RepairSemantics` creation.
- Recommendation: Add to Slice 0: audit all `_decide_repair` / repair planning logic in `chapter_orchestrator.py` and confirm whether `ChapterAuditRepairHint` alone suffices. Record the decision before Slice 3 starts.

### H4. Agent → Service import boundary adapter location unspecified

- Evidence: plan lines 162–164, 260–261.
- Detail: The plan says "Avoid Agent importing concrete Host runtime. Define an Agent-side `AgentRunControl` Protocol … Service can adapt `HostRunContext` to that Protocol." But it doesn't say where the adapter lives. If in Service (e.g., a new `fund_agent/services/agent_adapter.py`), Service would import both `HostRunContext` (Host) and `AgentRunControl` (Agent), which is allowed but must be explicit. If elsewhere, the dependency direction must be confirmed.
- Why non-blocking: The adapter is a straightforward Protocol implementation. The AGENTS.md boundary rules permit Service to import Host and Agent types. But the file location and import path affect Slice 5's test boundary checks.
- Recommendation: In Slice 5, create the adapter in `fund_agent/services/agent_adapter.py` or inline in `fund_analysis_service.py`, and add an import-boundary test proving Agent does not import the adapter.

### H5. Slice 8 cleanup scope too vague for reviewability

- Evidence: plan lines 307–309: "Remove or deprecate Service-owned `_run_single_chapter`, `_decide_repair`, attempt loop and Agent-owned trace logic from `chapter_orchestrator.py` for typed path."
- Detail: `chapter_orchestrator.py` is a large module with interleaved concerns: orchestration policy construction, per-chapter write-audit-repair loop, attempt counting, repair decisions, diagnostic serialization, failure classification, Host phase recording, typed availability derivation. The plan lists three method names but says "and Agent-owned trace logic" as a catch-all. This is too vague to assess whether the cleanup would accidentally remove Service-owned concerns (policy construction, fail-closed exception behavior, result serialization).
- Why non-blocking: Slice 8 is the last slice and explicitly gated on adapter tests passing first. The cleanup scope can be refined during implementation.
- Recommendation: Before Slice 8, produce a one-page cleanup inventory listing every function/method/class in `chapter_orchestrator.py` with a keep/remove/deprecate decision. This inventory can be produced as part of Slice 5–7 evidence.

---

## Validation / Checks Performed

1. **Boundary audit**: Traced every proposed Agent-owned type against the AGENTS.md boundary table. Confirmed:
   - `AgentReportRun`, `ChapterTask`, task graph, tool loop, `ToolRegistry`, `ToolTrace` → Agent (correct)
   - `AgentLLMClients` as Service-constructed per-run fields → not tools (correct)
   - `EvidenceAvailability` as precomputed input → not a tool (correct)
   - `RepairPolicy` → Agent, `RepairSemantics` → Fund (correct split)
   - `FinalAssemblyReadiness` → Agent computes, Service maps to final product (correct per design judgment)
   - `AgentRunControl` Protocol in Agent, adapted from `HostRunContext` in Service → no reverse dependency (correct)

2. **Non-goal compliance**: Verified every non-goal in the plan (lines 27–40) against plan content:
   - No live provider probe — confirmed, all test commands use fake clients only
   - No provider budget/default changes — confirmed, `AgentExecutionPolicy` has no provider config
   - No score-loop — confirmed, explicitly excluded
   - No multi-year runtime — confirmed, explicitly excluded
   - No template truth replacement — confirmed, chapter ids stay 0-7
   - No Ch3 calibration — confirmed, deferred
   - No programmatic audit relaxation — confirmed, `audit_focus` bounded only
   - No dayu runtime dependency — confirmed, explicitly forbidden
   - No provider clients as ToolRegistry tools — confirmed, explicit exclusion
   - No extra_payload/kwargs — confirmed, all parameters typed
   - No Host business inspection — confirmed, `AgentExecutionPolicy` excludes fund fields
   - No parallel scheduling — confirmed, sequential first MVP

3. **Fail-closed audit**: Confirmed plan preserves:
   - `--use-llm` explicit opt-in → `typed_template_path` gate in Slice 5
   - Empty stdout on incomplete → Slice 7 "Preserve empty stdout and exit code 1"
   - No deterministic fallback → `QualityFailClosedPolicy.deterministic_fallback_allowed=False`
   - Provider construction fail-before-execution → Service owns construction (unchanged)
   - Incomplete artifacts local-only → Slice 7 "Preserve existing local ignored `reports/llm-runs/`"

4. **Current code cross-reference**: Verified plan's understanding of current state:
   - `fund_agent/agent/` does not exist → confirmed
   - `chapter_orchestrator.py` owns write-audit-repair loop → confirmed (lines 200+)
   - `execution_contract.py` is Service-owned → confirmed (line 1 docstring)
   - `final_chapter_assembler.py` consumes `ChapterOrchestrationResult` → confirmed (line 117)
   - `host/runtime.py` has no Service/Fund imports → confirmed (zero business imports)
   - `chapter_writer.py`, `chapter_auditor.py`, `evidence_availability.py` are Fund-owned primitives → confirmed

5. **Slice sequence implementability**: Verified each slice's prerequisites are met by prior slices:
   - Slice 0 (preflight) → no dependencies, standalone ✓
   - Slice 1 (contracts) → only needs Slice 0 confirmation ✓
   - Slice 2 (ToolRegistry/ToolTrace) → only needs Slice 1 types ✓
   - Slice 3 (Fund adapters) → needs Slice 2 registry + B1 resolution ⚠
   - Slice 4 (runner) → needs Slice 3 adapters + B2 resolution ⚠
   - Slice 5 (Service adapter) → needs Slice 4 runner + B3 resolution ⚠
   - Slice 6 (readiness) → needs Slice 4 results ✓
   - Slice 7 (diagnostics) → needs Slice 5 adapter ✓
   - Slice 8 (cleanup) → needs Slice 5–7 pass ✓

---

## Non-Blocking Observations

### O1. `AgentExecutionPolicy` field overlap with `ProviderRuntimeBudget`

Plan line 103–110 lists `max_repair_attempts` and `max_output_chars` in `AgentExecutionPolicy`. Currently these live in Service's `ProviderRuntimeBudget` (execution_contract.py:133–152). The plan should clarify: does `AgentExecutionPolicy.max_repair_attempts` shadow `ProviderRuntimeBudget.timeout_max_attempts`, or are these semantically different ceilings (repair attempts vs timeout retry attempts)? Current code uses `timeout_max_attempts` for provider-level timeout retries and a separate repair loop for audit-driven regeneration. The plan's naming must avoid conflation.

### O2. Per-chapter attempt id format

Plan line 147 mentions `attempt_id` format like `ch03.attempt01`. The current orchestrator uses a different attempt tracking (per-chapter attempt index in repair loop). The plan should specify the id format contract so ToolTrace entries are consistently keyed across Agent and Service artifact serialization.

### O3. `_ALLOWED_RUNTIME_CHAPTER_IDS` hardcoded as `(1,2,3,4,5,6)`

Plan line 102 defines `target_chapter_ids` in `AgentExecutionPolicy`. Current Service code (execution_contract.py:46) hardcodes `_ALLOWED_RUNTIME_CHAPTER_IDS = frozenset((1, 2, 3, 4, 5, 6))`. If Agent's `target_chapter_ids` can differ from Service's allowed set, there's a validation gap. The plan should specify whether Agent validates against the same constraint or delegates to Service.

### O4. `FinalAssemblyReadiness` dual definition risk

Plan proposes Agent-owned `FinalAssemblyReadiness` (lines 129–133) with `ready/incomplete/blocked` status. Service already has `FinalAssemblyReadiness` in `final_chapter_assembler.py` (lines 157–177) with `ready/blocked` status and different fields (`chapter7_required`, `chapter7_ready`, `evidence_status`). These are different types with the same name. The plan should rename one or clarify the relationship to avoid import confusion when Agent readiness feeds Service mapping.

---

## Residual Risks for Controller

1. **B1–B3 must be resolved before Slice 3–5 implementation.** These are contract gaps, not implementation details. The controller should either accept them as implementation-worker decisions or request plan amendment.

2. **H3 (RepairSemantics conditional scope) should be decided at Slice 0.** The controller may want to pre-approve the decision criteria.

3. **O4 (FinalAssemblyReadiness naming collision) is a refactor risk.** The controller should decide naming before Slice 1 contract definitions are frozen.

4. **Slice 8 cleanup scope** is inherently uncertain until migration code exists. The controller should accept that the cleanup inventory will be produced as a mid-implementation artifact rather than pre-specified.

---

## Secret-Safety Statement

This review artifact contains no API key, Authorization header, Bearer token, cookie, password, raw provider response, raw audit response, prompt body, writer draft body, repair draft body, hidden provider config value, or raw PDF/source text. It references only safe file paths, type names, enum labels, and high-level architectural assessments.
