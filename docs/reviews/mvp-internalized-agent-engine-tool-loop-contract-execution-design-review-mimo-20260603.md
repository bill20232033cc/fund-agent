# MVP internalized Agent engine/tool-loop contract execution design review — MiMo

## Reviewer Self-Check

- Role: independent design review worker, not controller.
- Gate: `MVP internalized Agent engine/tool-loop contract execution design gate`.
- Classification: heavy.
- Scope: adversarial design/plan review only; no code, no implementation, no truth-source edits, no reports/commits/push/PR.
- Required read set: completed for `AGENTS.md`, `docs/design.md`, `docs/implementation-control.md`, `docs/current-startup-packet.md`, review target `docs/reviews/mvp-internalized-agent-engine-tool-loop-contract-execution-design-20260603.md`, prior controller judgments for Agent engine and template typed contract gates, and retained `summary.json`.
- Actions taken: wrote this single `docs/reviews/` review artifact.
- Actions intentionally not taken: no controller start, no implementation, no source/config/runtime edits, no commit, no push, no PR.

## Review Target

`docs/reviews/mvp-internalized-agent-engine-tool-loop-contract-execution-design-20260603.md`

## Findings

### F1. Evidence-to-diagnosis mismatch on Ch3 failure root cause

**Heading**: Ch3 failure diagnosis does not match retained diagnostic evidence.

**Direct evidence**:
- Design §Current Facts line 28: "Ch3 evidence is contract-shape evidence around `must_not_cover` / `言行一致`, not proof that fail-closed audit should be relaxed."
- Retained `summary.json` ch3 `prompt_contract_diagnostics`: `failure_subcategory=code_bug_other`, `issue_id_prefix_counts={"programmatic:C2": 1}`, `primary_subcategory=code_bug_other`.
- Retained `summary.json` ch3 runtime diagnostics: `chapter_failure_category=prompt_contract`, no `must_not_cover` or `言行一致` label in any diagnostic field.

**Impact**: The design diagnoses Ch3 as a `must_not_cover` / `言行一致` contract-shape problem, but the retained diagnostic shows `programmatic:C2` (chapter boundary violation) with `code_bug_other` subcategory. This mismatch could misdirect the Ch3-only calibration gate toward auditor relaxation on `must_not_cover` semantics, when the actual issue may be a C2 programmatic rule that fires incorrectly or a writer that outputs content outside the chapter boundary. If the next gate takes this design's diagnosis at face value, the calibration plan may target the wrong fix.

**Suggested fix**: Correct the Ch3 diagnosis line to reference the actual retained diagnostic (`programmatic:C2` / `code_bug_other`), and note that the Ch3-only calibration gate must first determine whether the C2 rule or the writer boundary is the root cause before deciding on contract-shape adjustments.

**Fix risk**: Low. Text-only correction in the design artifact.

**Severity**: medium — could misdirect a future calibration gate.

---

### F2. ToolRegistry ownership boundary for `service.provider_clients` injection mechanism undefined

**Heading**: Design lists `service.provider_clients` as "Not a registry tool" alongside registry tools without specifying the injection mechanism.

**Direct evidence**:
- Design §ToolRegistry table row for `service.provider_clients`: status "MVP accepted input for first Agent MVP", owner "Service constructs, Agent consumes Protocol clients", marked "Not a registry tool".
- Tool constraints section: "Tools receive explicit typed parameters only; no `extra_payload`."
- Budget/retry section: "Service declares ceilings: target chapter ids, max repair attempts, writer/auditor timeout ceilings, provider max attempts, max output chars, semantic audit enablement, and safe diagnostic policy."

**Impact**: The design establishes that Agent owns the tool loop and Fund tools are registered, but does not specify how Service-constructed provider clients reach Fund tools during Agent execution. Three mechanisms are plausible: (a) clients injected per-run into the Agent via `AgentReportRun` construction, (b) clients injected per-tool-call by the Agent from a Service-provided factory, (c) clients registered as a pseudo-tool that the Agent calls before invoking Fund writer/auditor tools. Each has different testability, safety, and boundary implications. Without specifying this, the implementation planning gate must re-derive the mechanism, risking ad-hoc decisions.

**Suggested fix**: Add one line to the ToolRegistry section or the Budget/retry section specifying the first Agent MVP injection model. Recommended: clients injected per-run into `AgentReportRun` by Service as explicit typed fields, then Agent passes them to Fund tools as typed tool inputs. This matches the current `ChapterOrchestratorLLMClients` pattern.

**Fix risk**: Low. One-line addition clarifying an existing pattern.

**Severity**: medium — leaves an implementation decision unresolved.

---

### F3. State machine sequential assumption for semantic audit may be over-specified

**Heading**: State machine forces semantic audit after programmatic audit pass without diagnostic-only escape.

**Direct evidence**:
- Design §Tool-Loop State Machine: `PROGRAMMATIC_AUDIT -> PLAN_REPAIR/STOP_FAIL_CLOSED -> BOUNDED_SEMANTIC_AUDIT -> PLAN_REPAIR/STOP_FAIL_CLOSED -> ACCEPT_CHAPTER`.
- Design §Tool-Loop State Machine text: "Runs only after programmatic audit has no blocking issue, unless future plan accepts diagnostic-only semantic pass."

**Impact**: The state machine as drawn enforces sequential programmatic-then-semantic audit. For the first Agent MVP, this is correct: programmatic blockers must be resolved before semantic audit to avoid wasting LLM calls. However, the design leaves a dangling "unless future plan accepts diagnostic-only semantic pass" without defining when or how this escape activates. If the implementation gate needs to support diagnostic-only semantic audit (e.g., for observability during early calibration), the state machine must be revisited. This is acceptable for an MVP design, but the dangling clause should either be made concrete or explicitly deferred.

**Suggested fix**: Replace the dangling clause with: "Diagnostic-only semantic audit is a future optimization deferred to a post-MVP observability gate; first Agent MVP always runs semantic audit sequentially after programmatic pass."

**Fix risk**: Low. Text clarification.

**Severity**: low — the current design is acceptable for first MVP, but the ambiguity could cause confusion.

---

### F4. Host cancellation/deadline observation mechanism unspecified for Agent

**Heading**: Design lists `host_cancelled` and `host_deadline_exceeded` as Agent terminal states but does not specify how Agent observes Host signals.

**Direct evidence**:
- Design §Failure Taxonomy: `host_cancelled` — "Cancel token observed"; `host_deadline_exceeded` — "Global deadline exceeded." Both listed as "Current Host concept / proposed Agent observation."
- Design §Budget/retry: "Host only enforces lifecycle/deadline/cancel and does not inspect chapter policy, provider clients, or fund business fields."
- Design §Boundary Mapping: Host owns "run lifecycle, global deadline, cancel, terminal state, safe events/diagnostics."

**Impact**: The current Host runtime governance provides a cancel token and global deadline. The design states Agent must "observe" these, but does not specify the mechanism: does Agent poll a token? Does Host inject a callback? Does the tool loop check cancellation between tool calls? Does a provider timeout interrupt trigger deadline check? Without this, the implementation gate must invent the observation mechanism, and testing strategy for cancellation/deadline mid-tool-call remains undefined.

**Suggested fix**: Add one line to the Runner/task graph section: "Agent checks Host cancel token and deadline at task-graph scheduling boundaries (before each ChapterTask dispatch and after each tool-call return); mid-tool-call cancellation is handled by provider client timeout, not by Agent polling."

**Fix risk**: Low. One-line specification matching the current Host design.

**Severity**: medium — affects testability and implementation planning.

---

### F5. Repair planner co-ownership between Agent and Fund violates single-owner boundary

**Heading**: `fund.repair_planner` lists "Fund domain semantics, Agent execution policy" as co-owners.

**Direct evidence**:
- Design §ToolRegistry table: `fund.repair_planner` — "Implementation owner: Fund domain semantics, Agent execution policy".
- AGENTS.md ownership rule: "任何'管理 tool loop / runner / trace / facts / ToolRegistry / context budget / tool execution'的代码，默认放在 Agent" and "任何'理解基金类型、财报章节、投资规则、有知有行方法论'的代码，默认放在 Agent 层的 fund_agent/fund".

**Impact**: The design places repair planning under dual ownership without defining the boundary between Fund's domain repair semantics (what can be repaired, what evidence is needed) and Agent's execution policy (attempt counting, budget enforcement, retry scheduling). This creates a gray zone: should `fund_agent/fund/repair_planner.py` or `fund_agent/agent/repair_policy.py` own the `RepairPlan` return type? Should the decision to `stop` vs `regenerate` be a Fund domain decision or an Agent budget decision?

**Suggested fix**: Clarify ownership: Fund owns `RepairSemantics` (what can be fixed, what evidence is needed, issue-to-repair-action mapping); Agent owns `RepairPolicy` (attempt counting, budget enforcement, when to stop vs retry). The tool `fund.repair_planner` calls Fund's semantic repair planner and returns a `RepairPlan`; Agent's loop decides whether to execute the plan based on remaining budget.

**Fix risk**: Low. Clarifies an existing boundary.

**Severity**: medium — ambiguous ownership will cause implementation friction.

---

### F6. Final assembly readiness interaction with current Service `FinalChapterAssembler` not mapped

**Heading**: Design proposes Agent-owned `FinalAssemblyReadiness` without mapping to the current Service-owned `FinalChapterAssembler`.

**Direct evidence**:
- Design §Runner/task graph: `FinalAssemblyReadiness` — "Typed readiness projection: ready, incomplete, or blocked, with missing accepted chapter ids and issue ids."
- Design §Next Gate Handoff Slice E: "Move readiness reporting to Agent without changing report stdout or deterministic default."
- Current fact from `docs/design.md` §5.4.1: "Route C Gate 4 Slice 4A 的 Service 层 `FinalChapterAssembler` / `assemble_final_chapters()` 已实现为 `final_chapter_assembler.v1`."

**Impact**: The current `FinalChapterAssembler` is Service-owned and already performs fail-closed readiness checks (any required body chapter not accepted blocks Ch7/Ch0). The design proposes Agent-owned `FinalAssemblyReadiness` as a separate projection. The relationship between these two is not specified: does Agent readiness replace Service readiness? Does Agent readiness feed into Service readiness? Do they coexist with Agent readiness as an earlier gate and Service readiness as the final gate? Without this mapping, the implementation plan for Slice E must resolve the duplication risk.

**Suggested fix**: Add one line to the Runner/task graph section or Slice E: "Agent-owned `FinalAssemblyReadiness` replaces the current readiness check inside Service `FinalChapterAssembler`; Service final assembler receives the readiness projection from Agent and only performs deterministic Ch7/Ch0 assembly when readiness is `ready`."

**Fix risk**: Low. One-line design decision.

**Severity**: medium — unaddressed duplication risk.

---

### F7. Over-design: `FinalAssemblyReadiness` terminal states overlap with failure taxonomy

**Heading**: Terminal states `partial_fail_closed`, `blocked_by_contract`, `blocked_by_runtime`, and `dependency_readiness_incomplete` have overlapping semantics.

**Direct evidence**:
- Design §Runner/task graph terminal states: `accepted`, `partial_fail_closed`, `cancelled`, `deadline_exceeded`, `blocked_by_contract`, `blocked_by_runtime`.
- Design §Failure taxonomy: `programmatic_contract_blocker`, `missing_evidence_blocker`, `repair_exhausted`, `dependency_readiness_incomplete`, `host_cancelled`, `host_deadline_exceeded`, `provider_runtime_timeout`.

**Impact**: A run that has one chapter blocked by `programmatic_contract_blocker` and another by `provider_runtime_timeout` would be both `partial_fail_closed` and potentially `blocked_by_contract` or `blocked_by_runtime`. The terminal state enum conflates run-level outcome with per-chapter failure kinds. This is over-designed for a first MVP where the only actionable terminal states are: "all accepted → full report" and "anything not accepted → fail-closed."

**Suggested fix**: Simplify terminal states to three for first MVP: `accepted` (all required chapters accepted), `partial_fail_closed` (at least one required chapter not accepted), and `host_interrupted` (cancel or deadline). Per-chapter failure kinds remain in the failure taxonomy and ToolTrace. A post-MVP observability gate can add richer terminal state distinctions if needed.

**Fix risk**: Low. Simplification reduces implementation scope.

**Severity**: low — over-design, not a correctness issue.

---

### F8. Missing specification for how Agent task graph maps to current Service `ChapterOrchestrator` behavior

**Heading**: Design proposes a task graph for chapters 1-6 but does not map it to the current Service-owned `orchestrate_chapters()` behavior.

**Direct evidence**:
- Design §Current Facts: "Current Gate 3 `ChapterOrchestrator` is Service-owned `chapter_orchestrator.v1` write-audit-repair facade for body chapters 1-6."
- Design §Tool-Loop State Machine: describes per-chapter write → programmatic audit → semantic audit → repair loop.
- Design §Next Gate Handoff Slice D: "Move write-audit-repair mechanics to Agent while preserving Service use case and fail-closed result mapping."

**Impact**: The current `ChapterOrchestrator.orchestrate_chapters()` runs chapters 1-6 with independent write/audit/repair, aggregates results, and returns to Service. The proposed task graph also runs chapters 1-6 independently. The design should explicitly state that the Agent task graph subsumes `orchestrate_chapters()` behavior, preserving the same fail-closed semantics, independent chapter execution, and result aggregation. Without this, the implementation gate cannot verify that the migration preserves current behavior.

**Suggested fix**: Add one line to the Runner/task graph section: "The Agent task graph subsumes the current Service `ChapterOrchestrator.orchestrate_chapters()` behavior for chapters 1-6: independent chapter execution, per-chapter write/audit/repair loops, and fail-closed result aggregation. Service final assembler continues to consume the aggregated result."

**Fix risk**: Low. Explicit behavioral equivalence statement.

**Severity**: medium — needed for migration verification.

---

### F9. Under-design: Ch2 internal subcontracts tracing mechanism unspecified

**Heading**: Design accepts Ch2 internal subcontracts (performance/attribution/cost) but does not specify how Agent traces sub-requirements within a single chapter.

**Direct evidence**:
- Design §Accepted Future Template Contract Inputs table: "Ch2 performance/attribution/cost as internal subcontracts only — Agent can trace Ch2 internal sub-requirements but must keep public chapter id 2."
- Design §Residual Risks: "Ch2 internal subcontracts without public split — Open."

**Impact**: The design says Agent "can trace" Ch2 sub-requirements but provides no mechanism. If Agent cannot distinguish between performance, attribution, and cost sub-requirements within chapter 2, it cannot: (a) identify which sub-requirement caused a failure, (b) target repair to the failing sub-section, (c) provide per-sub-requirement ToolTrace. This matters because the current summary.json shows ch2 failing with `llm_timeout` — if the timeout happens during the attribution sub-section, the repair should target that sub-section, not regenerate the entire chapter.

**Suggested fix**: Add to the Residual Risks table: "Ch2 internal subcontracts tracing: Agent task graph should support optional sub-requirement ids within a ChapterTask for traceability and targeted repair; this is an implementation detail for the typed contract implementation gate, not a blocker for the first Agent MVP design."

**Fix risk**: Low. Deferred to implementation planning.

**Severity**: low — does not block design acceptance but should be in residual risks.

---

### F10. ToolTrace `redaction_policy_id` and `artifact_safe` are implementation details

**Heading**: Two ToolTrace fields are premature implementation concerns.

**Direct evidence**:
- Design §ToolTrace: `redaction_policy_id` — "Serializer allowlist policy identity"; `artifact_safe` — "Boolean indicating the entry is safe for local retained artifact serialization."

**Impact**: These fields describe how trace entries are serialized and stored, not what the trace records. They belong in the implementation plan's serializer design, not in the trace schema. Including them in the schema risks over-specifying the serialization mechanism before the trace content is settled.

**Suggested fix**: Move `redaction_policy_id` and `artifact_safe` from the ToolTrace schema table to a note: "Trace serialization safety follows the existing retained artifact allowlist policy; specific serializer fields (`redaction_policy_id`, `artifact_safe`) are implementation details for the serialization gate."

**Fix risk**: Low. Reduces schema surface.

**Severity**: low — over-design, not a correctness issue.

---

### F11. Evidence Confirm relationship explicitly deferred but not referenced in ToolTrace phases

**Heading**: Evidence Confirm is deferred but its absence from ToolTrace phases may cause confusion.

**Direct evidence**:
- Design §Residual Risks: "Evidence Confirm relationship to bounded semantic audit — Deferred — Evidence Confirm gate; MVP uses `evidence_confirm_deferred`."
- Design §ToolTrace phases: `project_evidence`, `write`, `programmatic_audit`, `semantic_audit`, `repair_plan`, `readiness`.

**Impact**: The ToolTrace phases list does not include an `evidence_confirm` phase. This is correct for the first MVP (Evidence Confirm is deferred), but the design should explicitly note that the phase list is MVP-complete and that Evidence Confirm will add a phase in a future gate. Without this note, a reviewer or implementer might assume Evidence Confirm is forgotten rather than intentionally deferred.

**Suggested fix**: Add a note after the ToolTrace phases table: "Phase list is MVP-complete; Evidence Confirm will add an `evidence_confirm` phase in a future gate."

**Fix risk**: Low. One-line clarification.

**Severity**: low — clarity improvement.

---

### F12. Design does not address partial-success artifact output for debugging

**Heading**: When a run fails with `partial_fail_closed`, the design does not specify what Agent returns to Service for artifact retention.

**Direct evidence**:
- Design §Runner/task graph: "The Agent may still return an incomplete diagnostic artifact to Service; Service preserves empty stdout and no partial report behavior."
- Current fact from `docs/design.md` §5.4.1: incomplete `--use-llm` local artifact retention writes `manifest.json`, `summary.json`, per-chapter JSON, writer draft, repair draft, normalized auditor feedback, accepted/failed status, chapter matrix and first failed diagnostic.

**Impact**: The current Service-owned artifact retention already handles incomplete runs. The design says Agent "may still return an incomplete diagnostic artifact" but does not specify the artifact contract: what fields does Agent return? Does Agent return the same `summary.json`-like structure, or a different Agent-level trace? If the artifact contract is not specified, the implementation gate must invent it, and the migration from Service-owned to Agent-owned artifact generation becomes ambiguous.

**Suggested fix**: Add to the Runner/task graph section: "Agent returns to Service a typed `AgentRunResult` containing: terminal state, per-chapter status matrix, per-chapter failure categories, ToolTrace summary, and `FinalAssemblyReadiness`. Service maps this to the existing incomplete artifact retention format."

**Fix risk**: Low. Specifies the Agent-to-Service result contract.

**Severity**: medium — affects artifact retention migration planning.

---

## Summary

**Verdict**: pass-with-risks

The design is well-structured and correctly separates current facts, accepted future inputs, proposed design, non-goals, and residual risks. It preserves the UI/Service/Host/Agent/Fund boundary from AGENTS.md, keeps deterministic `analyze/checklist` as default, and does not authorize implementation, provider budget changes, auditor relaxation, or score-loop wiring.

No blocking findings. 12 findings total: 2 medium-high (F1 evidence mismatch, F2 injection mechanism), 5 medium (F4 cancellation, F5 co-ownership, F6 readiness mapping, F8 orchestrator mapping, F12 artifact contract), 5 low (F3 state machine ambiguity, F7 over-design, F9 subcontracts, F10 trace fields, F11 evidence confirm note).

## Residual Risks

| Risk | Status | Recommended destination |
|---|---|---|
| Ch3 diagnosis mismatch may misdirect Ch3-only calibration gate | Must fix before controller judgment | Controller judgment correction |
| Provider client injection mechanism unspecified | Should fix in design before implementation planning | Design fix or implementation planning gate |
| Host cancellation/deadline observation mechanism unspecified | Should fix in design before implementation planning | Design fix or implementation planning gate |
| Repair planner co-ownership boundary | Should clarify before implementation planning | Design fix or implementation planning gate |
| Final assembly readiness duplication with Service | Should clarify before implementation planning | Design fix or implementation planning gate |
| Agent task graph ↔ Service orchestrator behavioral equivalence | Should clarify before Slice D implementation | Implementation planning gate |
| Provider runtime timeouts remain the primary real-run blocker | Unchanged | Provider runtime budget calibration gate (separate) |
| Ch3 `programmatic:C2` root cause needs diagnosis before calibration | Unchanged | Ch3-only calibration gate (separate) |
| Trace serializer safety testing | Open | Implementation gate with allowlist tests |
| Ch2 internal subcontracts tracing | Deferred | Typed contract implementation gate |

## Validation

- Review target artifact exists and is readable: pass.
- Required read set consumed: pass.
- No code, implementation, truth-source, or runtime changes made: pass.
- Secret-safety: this review contains no API key, Authorization header, Bearer token, raw provider response, prompt body, or writer/repair draft. References only safe artifact paths, schema names, enum labels, and diagnostic categories.
