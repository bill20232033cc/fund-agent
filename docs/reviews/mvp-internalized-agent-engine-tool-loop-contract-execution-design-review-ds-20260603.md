# MVP internalized Agent engine/tool-loop contract execution design — AgentDS review

## Worker Self-Check

- Role: AgentDS as independent design review worker, not controller.
- Gate: `MVP internalized Agent engine/tool-loop contract execution design gate`.
- Classification: heavy.
- Review target: `docs/reviews/mvp-internalized-agent-engine-tool-loop-contract-execution-design-20260603.md`.
- Actions taken: read required set (8 files), boundary-checked against `AGENTS.md`/`docs/design.md`/`docs/implementation-control.md`, cross-referenced prior controller judgments and `summary.json` evidence, wrote this single review artifact.
- Actions intentionally not taken: no Phaseflow/Gateflow controller start, no implementation, no source/test/config/runtime edits, no truth-doc edits, no commit, no push, no PR.
- Scope: adversarial design review only. Non-goals observed: no code, no implementation, no truth-source edits, no `contracts.py`/auditor/provider budget/score-loop/report changes.

---

## 0. Review Summary

**Conclusion: pass-with-risks.** No blocking findings. The design is structurally correct against all four prior controller judgments, preserves all required boundaries, stays within design-only scope, and provides adequate detail for a subsequent implementation-planning gate. Four residual risks noted below require explicit disposition in the controller judgment.

---

## 1. Findings

### F1. `fund.evidence_availability_projection` Tool Is Redundant with Existing Gate 1 Capability

**Severity**: info (non-blocking)

**Evidence**:
- Design proposes `fund.evidence_availability_projection` as an Agent-registered tool (ToolRegistry table, line 123).
- Prior controller judgment for `MVP fund report template typed contract redesign gate` (judgment line 19) explicitly states: `EvidenceAvailability is accepted as a derived supplemental availability view over same-source ChapterFactProjection, not a replacement unless a later gate accepts that.`
- Gate 1 `ChapterFactProvider.project()` already produces a typed projection from `StructuredFundDataBundle` that feeds chapter facts to writer/auditor (implementation-control line 24-25).
- The tool description says "no repository/PDF/cache/source helper access" — same as what Gate 1 already guarantees.

**Impact**: Creates an unnecessary tool registry entry for a computation that is naturally a Fund-layer derived projection computed once before the tool loop, not a tool call mid-loop. Registers a read-only derivation that never fails independently as a tool, which dilutes the tool-loop model.

**Suggested Fix**: Drop `fund.evidence_availability_projection` from the ToolRegistry table. Replace with a statement that `EvidenceAvailability` is derived once by Fund from `ChapterFactProjection` and passed as a typed input to the task graph (same as `ChapterContract` and `ChapterFactProjection` are passed). The runner receives it as pre-computed task input, not as a tool call.

**Fix Risk**: None. This is a design-artifact clarification with no code impact.

---

### F2. ToolRegistry Table Mixes MVP-Accepted Inputs with Proposed Future Tools Without Clear Phase Distinction

**Severity**: low (non-blocking)

**Evidence**:
- ToolRegistry table (design lines 116–125) lists 7 tools. Only `service.provider_clients` is marked `MVP accepted input`; the other six are `Proposed future design`.
- `fund.chapter_writer`, `fund.programmatic_audit`, `fund.bounded_semantic_audit` are described as "Proposed future design over current Fund primitive" — which correctly signals they wrap existing code, but does not clarify whether this wrapping is part of Slice C or a later slice.
- The next-gate-handoff slices (lines 307–314) propose Slice C as "Wrap Fund writer/programmatic/semantic tools" but Slice A is "Agent execution/audit schema plan" — which might need ToolRegistry contracts defined before Slice C can register tools.

**Impact**: A future implementation planner could mistakenly try to register all tools in a single slice without first defining the ToolRegistry contract schema, leading to undefined tool call contracts.

**Suggested Fix**: Add a column or footnote to the ToolRegistry table indicating which future implementation slice each tool belongs to (e.g., "Slice A schema only" for registry contract types, "Slice C" for Fund tool wrapping). Or add a preamble sentence: "Tools marked Proposed future design are phased: schema contracts in Slice A, Fund tool wrapping in Slice C."

**Fix Risk**: None. Only affects design artifact clarity; no boundary or ownership change.

---

### F3. State Machine Missing Explicit Repair-Budget-Exhausted Transition from `BOUNDED_SEMANTIC_AUDIT`

**Severity**: low (non-blocking)

**Evidence**:
- State machine diagram (design lines 176–185) shows:
  ```
  PROGRAMMATIC_AUDIT -> PLAN_REPAIR -> REGENERATE -> WRITE_DRAFT
  PROGRAMMATIC_AUDIT -> STOP_FAIL_CLOSED
  BOUNDED_SEMANTIC_AUDIT -> PLAN_REPAIR -> REGENERATE -> WRITE_DRAFT
  BOUNDED_SEMANTIC_AUDIT -> STOP_FAIL_CLOSED
  ```
- But the repair-exhausted path (no remaining budget) is only documented in text (design line 220: "Repair exhaustion must record remaining budget, consumed attempts, issue ids, and last failure kind") and in the failure taxonomy as `repair_exhausted`.
- The diagram does not show `PLAN_REPAIR -> STOP_FAIL_CLOSED` for the case where the repair planner returns `stop` due to exhausted budget.

**Impact**: A reader relying only on the diagram could assume repair is always attempted after audit failure, missing the budget-exhausted early-stop path.

**Suggested Fix**: Add a transition `PLAN_REPAIR -> STOP_FAIL_CLOSED` to the state machine diagram, with annotation "repair budget exhausted or planner returns stop."

**Fix Risk**: None. Diagram-only clarification.

---

### F4. Terminal State `blocked_by_contract` vs `blocked_by_runtime` Distinction Is Under-Specified for Mixed Failure Scenarios

**Severity**: low (non-blocking)

**Evidence**:
- Terminal states table (design lines 103–110) defines `blocked_by_contract` and `blocked_by_runtime` as separate terminal states.
- `summary.json` evidence shows chapter 6 with mixed failures: first attempt had `prompt_contract` / `code_bug_other` (a contract failure), second attempt had `llm_timeout` (a runtime failure). Final stop reason is `llm_timeout` but the earlier contract issue is lost in the terminal classification.
- The design failure taxonomy (lines 224–237) correctly keeps `programmatic_contract_blocker` and `provider_runtime_timeout` separate, but does not specify how the Agent should classify a chapter that hit both across attempts.

**Impact**: A chapter that fails programmatic audit on attempt 1, then times out on attempt 2, could be classified as either `blocked_by_runtime` (last failure) or `blocked_by_contract` (root cause). Without explicit multi-attempt classification rules, diagnostics could be misleading.

**Suggested Fix**: Add a rule to the failure taxonomy or terminal states section: "Terminal classification must use the most severe blocker observed across all attempts, with precedence: `programmatic_contract_blocker` > `missing_evidence_blocker` > `missing_evidence_degrade_violation` > `semantic_blocker` > `provider_runtime_*` > `repair_exhausted` > `host_cancelled` > `host_deadline_exceeded`." Or explicitly state that last-attempt stop reason is the terminal classification and prior-attempt issues are preserved in ToolTrace only.

**Fix Risk**: None. Clarification only; does not change fail-closed semantics.

---

## 2. Boundary Correctness Verification

### 2.1 Service/Host/Agent/Fund Ownership

| Ownership claim in design | Matches AGENTS.md + design.md? | Finding |
|---|---|---|
| Service owns use case, ExecutionContract, quality policy, provider construction, runtime ceilings | Yes. Matches AGENTS.md lines 132-135 and design.md lines 54,59 | Pass |
| Host owns lifecycle only | Yes. Matches AGENTS.md lines 111-113 and design.md line 55 | Pass |
| Agent owns runner, task graph, tool loop, budget, ToolRegistry, ToolTrace | Yes. Matches AGENTS.md lines 117-119 and prior controller judgment (agent-engine judgment lines 17-18) | Pass |
| Fund owns domain tools, writer, audit, repair semantics | Yes. Matches AGENTS.md lines 137-139 | Pass |
| Tool implementations owned by Fund/Service, registry owned by Agent | Yes. Correctly splits implementation ownership from execution orchestration | Pass |

### 2.2 Deferred Gate Isolation

| Deferred concern | Design references it? | Leaks into implementation scope? |
|---|---|---|
| Ch3 calibration | Listed as deferred input (line 49), non-goal (line 261), separate gate (line 318) | No |
| Provider runtime budget | Listed as deferred (line 51, 262), separate gate (line 319) | No |
| Multi-year evidence | Listed as deferred (line 52, 263), separate gate (line 320) | No |
| Score-loop | Listed as deferred (line 53, 264), separate gate (line 321) | No |
| Ch2 split / 0+9 | Listed as deferred (line 54, 265), separate gate (line 322) | No |
| Facet wiring | Listed as deferred (line 55, 266), separate gate (line 323) | No |
| Durable Host session/resume/memory/outbox | Listed as separate gate (line 324) | No |

**Verdict**: All deferred concerns are properly isolated. Design does not accidentally authorize implementation of any deferred gate.

### 2.3 Dayu Discipline

- Design explicitly states "Do not add `dayu-agent`, `dayu.engine`, or `dayu.host` as production runtime dependency" (line 253).
- Internalization is scoped to "Dayu Engine-style capabilities only as local project contracts" (line 251).
- Copy/rewrite gate requirement preserved (line 254).
- **Pass.**

### 2.4 Evidence Consistency with summary.json

| Claim in design | summary.json evidence | Consistent? |
|---|---|---|
| Ch1 and Ch5 accepted | `chapter_matrix` shows ch1 `status=accepted`, ch5 `status=accepted` | Yes |
| Ch2/Ch4/Ch6 timeout | All three show `failure_category=llm_timeout`, `stop_reason=llm_timeout` | Yes |
| Ch3 prompt_contract / repair_budget_exhausted | ch3 `failure_category=prompt_contract`, `stop_reason=repair_budget_exhausted`, `issue_id_prefix_counts: {"programmatic:C2": 1}` | Yes |
| Ch2/Ch6 timeout is provider runtime evidence, not auditor relaxation evidence | All timeout entries show `timeout_root_cause_hint: small_prompt_provider_timeout` with auditor operation, ~743 token prompts, ~60s elapsed | Yes |
| Final assembly blocked by missing ch2/3/4/6 | `final_assembly_status=incomplete`, blocking issues for ch2/3/4/6 all present | Yes |

One discrepancy: design line 27 says "chapters 1 and 5 accepted; chapters 2, 4, and 6 failed with `llm_timeout`; chapter 3 failed with `repair_budget_exhausted` / `prompt_contract`" — this is accurate. However design line 28 says "Ch3 evidence is contract-shape evidence around `must_not_cover` / `言行一致`" — but the `summary.json` shows ch3's only programmatic issue is `programmatic:C2` with `code_bug_other` subcategory, not a `must_not_cover` issue. The design's characterization of Ch3 as `must_not_cover` evidence is inherited from prior controller judgments (template-redesign judgment line 20: "Evidence-conditional must_not_cover is accepted for the retained Ch3 failure mode") and is slightly imprecise against the raw evidence. **Not a design defect** — the design correctly defers Ch3 calibration to a separate gate and does not build any design decisions on this characterization.

---

## 3. Completeness Assessment

### 3.1 ToolRegistry

| Aspect | Covered? | Note |
|---|---|---|
| Tool identity (name, owner, version) | Yes | Each tool has name, implementation owner, registry owner |
| Tool input/output contracts | Partial | "Allowed input"/"Allowed output" columns are descriptive, not typed schemas. Adequate for design phase; schemas belong in implementation planning. |
| Tool constraints | Yes | Six explicit constraints (lines 127–132) |
| Tool discovery/registration lifecycle | No | Not specified how tools are registered at Agent startup. Adequate for design phase. |
| Tool versioning | Partial | `tool_version` mentioned in ToolTrace but not in registry entries. Minor. |

### 3.2 ToolTrace

| Aspect | Covered? | Note |
|---|---|---|
| Schema version | Yes | `agent_tool_trace.v1` |
| Identity fields (run, task, chapter, attempt, tool_call) | Yes | All five ids present |
| Phase tracking | Yes | Six phases enumerated |
| Budget counters | Yes | Attempt count, max attempts, elapsed, timeout, tokens, chars, repair budget |
| Serialization safety | Yes | Allowlist-first policy, explicit deny list for secrets/raw content |
| Redaction policy | Yes | `redaction_policy_id`, `artifact_safe` boolean |
| Relationship to existing retained artifact policy | Yes | Line 158: "Raw draft storage remains separate from trace" |

### 3.3 State Machine

| Aspect | Covered? | Note |
|---|---|---|
| All states defined | Yes | 8 states with owner and transition |
| Happy path | Yes | TASK_READY -> WRITE -> PROGRAMMATIC -> SEMANTIC -> ACCEPT |
| Repair loop | Yes | AUDIT -> PLAN_REPAIR -> REGENERATE -> WRITE |
| Stop conditions | Yes | STOP_FAIL_CLOSED covers runtime, contract, evidence, repair exhaustion |
| Dependency readiness | Yes | Ch7 blocks on body, Ch0 blocks on Ch7, FinalAssemblyReadiness is fail-closed |
| Missing: repair-exhausted transition from diagram | Partial | See F3 |

### 3.4 Failure Taxonomy

| Failure kind | Layer | Recoverable? | Traced? |
|---|---|---|---|
| `provider_runtime_timeout` | Tool runtime | Yes, via bounded retry | Yes |
| `provider_runtime_rate_limit` | Tool runtime | No | Yes |
| `provider_runtime_malformed` | Tool runtime | No | Yes |
| `programmatic_contract_blocker` | Fund audit | Yes, via repair | Yes |
| `semantic_blocker` | Bounded semantic audit | Yes, via repair | Yes |
| `missing_evidence_degrade_violation` | Contract/audit | Yes, via repair | Yes |
| `missing_evidence_blocker` | Contract/readiness | No | Yes |
| `repair_exhausted` | Agent loop | No | Yes |
| `dependency_readiness_incomplete` | Agent readiness | No | Yes |
| `host_cancelled` | Host lifecycle | No | Yes |
| `host_deadline_exceeded` | Host lifecycle | No | Yes |

Taxonomy is complete and correctly separates runtime failures from content failures from dependency failures. **Pass.**

---

## 4. Over-Design / Under-Design Assessment

### Potential Over-Design

1. **`fund.evidence_availability_projection` as a tool**: As noted in F1, registering a read-only derivation as a tool is over-design. Evidence availability should be a pre-computed task input.

2. **Terminal state granularity**: Six terminal states for a design-phase artifact is thorough but not excessive — each maps to a distinct failure mode observed in real provider smoke evidence.

### Potential Under-Design

1. **Tool call timeout vs global deadline interaction**: The design says Host enforces global deadline and Agent enforces per-tool timeouts, but does not specify what happens when the global deadline fires mid-tool-call. Does Agent observe the cancel token during a blocking provider call? This is a known hard problem (provider HTTP calls are blocking I/O) and the design does not address it. **Recommendation**: Note as a residual risk for the implementation gate; not a design defect at this level.

2. **Concurrent body chapter execution**: The task graph says body chapters 1-6 are independent but does not state whether they execute sequentially or concurrently. Given current single-process Python implementation, sequential is implied but should be explicit. **Recommendation**: Add a statement: "Body chapters execute sequentially within the Agent run; concurrent execution is deferred to a future async Host runner gate."

3. **ToolRegistry initialization and dependency injection**: How does Agent receive Fund tool implementations at startup? The design says Fund owns implementation and Agent owns registry, but the wiring path (Service constructs? Agent imports Fund directly? Dependency injection?) is unspecified. **Recommendation**: Note as a residual for implementation planning; not a design defect.

---

## 5. Handoff-Readiness Assessment

The design artifact is ready for controller judgment handoff:

- Worker self-check is present and correctly scoped.
- Current facts section correctly separates implementation reality from accepted future inputs.
- Accepted future inputs table explicitly maps prior controller judgments to design consumption.
- Every proposed schema/state/tool has a status marker (MVP accepted input / proposed future design / current fact / deferred).
- Non-goals section explicitly lists all deferred concerns.
- Residual risks table is present and honest about open questions.
- Next-gate handoff section proposes a reasonable slice sequence without authorizing implementation.
- Validation command and secret-safety statement are present.

**Handoff readiness: pass.**

---

## 6. Finding Summary

| Finding | Severity | Status | Requires design fix? |
|---|---|---|---|
| F1: `evidence_availability_projection` tool redundant | info | Open | Recommended, not blocking |
| F2: ToolRegistry phase distinction unclear | low | Open | Recommended, not blocking |
| F3: Missing PLAN_REPAIR→STOP transition in diagram | low | Open | Recommended, not blocking |
| F4: Mixed-failure terminal classification under-specified | low | Open | Recommended, not blocking |

No blocking findings. All four findings are clarifications suitable for fix-before-controller-judgment or explicit controller disposition as accepted risks.

---

## 7. Residual Risks

| Risk | Severity | Recommended owner |
|---|---|---|
| Tool call timeout vs global deadline interaction during blocking provider HTTP calls | Medium | Implementation planning gate — must address cancellation propagation for blocking I/O |
| Body chapter concurrency model not stated (sequential vs parallel) | Low | Add explicit statement in design fix or controller judgment |
| ToolRegistry wiring/injection path unspecified | Low | Implementation planning gate Slice A |
| `audit_focus` boundary enforcement mechanism unspecified (how to guarantee it cannot disable programmatic blockers at runtime) | Medium | Implementation planning gate — needs a typed constraint, not just documentation |
| Ch2 internal subcontract tracing without public split — exact mechanism deferred | Low | Already in residual risks table (design line 282); acceptable |

---

## 8. Validation

- Command: verified all 8 required files readable; verified design artifact path exists; verified prior controller judgments and `summary.json` are internally consistent with design claims.
- Result: pass. Design is self-consistent against all truth sources.

---

## 9. Secret-Safety Statement

This review contains no API key, Authorization header, Bearer token, cookie, password, raw provider response, raw audit response, prompt body, writer draft, repair draft, hidden provider config value, or raw PDF/source text. It references only safe artifact paths, finding ids, and high-level diagnostic categories.
