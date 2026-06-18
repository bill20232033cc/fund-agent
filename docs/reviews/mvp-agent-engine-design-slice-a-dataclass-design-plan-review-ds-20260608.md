# MVP Agent Engine Design Slice A Dataclass Design Plan — Adversarial Review

## 1. Verdict

**PASS_WITH_NON_BLOCKING_OBSERVATIONS**

There are zero blocking findings. Four non-blocking observations are recorded below.

## 2. Review Metadata

| Field | Value |
|---|---|
| Role | `review worker` (AgentDS) |
| Review type | adversarial, design-only |
| Reviewed artifact | `docs/reviews/mvp-agent-engine-design-slice-a-dataclass-design-plan-20260608.md` |
| Parent artifacts | `mvp-agent-engine-design-refresh-gate-plan-20260607.md`, `mvp-agent-engine-design-refresh-gate-plan-controller-judgment-20260607.md` |
| Source-of-truth docs | `AGENTS.md`, `docs/design.md`, `docs/implementation-control.md`, `docs/current-startup-packet.md` |
| Source code reviewed | `fund_agent/services/chapter_orchestrator.py` (dataclass/run_single_chapter sections), `fund_agent/services/final_chapter_assembler.py` (complete) |

## 3. Findings

### 3.1 Blocking Findings

None. All stop conditions from the plan's Section 9 pass.

### 3.2 Non-Blocking Findings

#### NBO-4: ToolTrace phase field excludes parent-plan derive_evidence_availability tool candidate

- **Severity**: informational
- **Reference**: plan §5.6 `tool_name` list vs parent plan §4 tool table

The parent `Agent Engine Design Refresh Gate Plan` §4 lists `fund.derive_evidence_availability` as a tool candidate in the initial ToolRegistry design. Slice A §5.2 deliberately refines this: `EvidenceAvailability` becomes a pre-computation on `AgentReportRun` (derived once at run level, not invoked as a per-task tool). The `ToolTrace.phase` Literal (`projection`, `writer`, `programmatic_audit`, `semantic_audit`, `repair_decision`) and `ToolCallRequest.tool_name` initial set both omit `derive_evidence_availability`.

This is a valid design refinement, not a contradiction, because:
- The parent plan's tool table is a candidate list, not a binding inventory.
- Making EvidenceAvailability a run-level pre-computation rather than a tool call resolves NBO-1 more cleanly (no tool-level recomputation surface).

No action required, but the discrepancy should be noted in the controller judgment so future Slice B (Tool Adapter Contract) doesn't re-add it as a tool by accident.

#### NBO-5: AgentRepairPolicy.hidden_retry_allowed semantics undefined

- **Severity**: informational
- **Reference**: plan §5.5 `AgentRepairPolicy` fields

The plan sets `hidden_retry_allowed: false` without defining what "hidden retry" means in the Agent repair context. The current system has no concept of hidden retries (all retries are explicit: provider-level timeout bounded retry and content-level bounded repair attempts). Introducing an undefined field risks future misinterpretation.

Recommendation for Slice C (Repair And Budget Contract): define "hidden retry" explicitly or remove the field until the concept is needed.

#### NBO-6: AgentReportRun.blocked_reasons definition underspecified

- **Severity**: informational
- **Reference**: plan §5.1 `AgentReportRun.blocked_reasons`

The plan describes `blocked_reasons` as "run-level safe reasons only" without enumerating what safety constraints apply. The current `ChapterOrchestrationResult.blocked_reasons` carries rich typed `ChapterRunStopReason` values with chapter-id attribution. The future `AgentReportRun` should clarify whether it preserves the mapping from chapter-id to stop-reason or flattens to a run-level aggregate.

Recommendation: in a later implementation planning gate, specify whether `blocked_reasons` is `tuple[ChapterRunStopReason, ...]` (flattened) or `Mapping[int, ChapterRunStopReason]` (per-chapter).

#### NBO-7: ToolTrace.diagnostic_consistency_status reference vague

- **Severity**: informational
- **Reference**: plan §5.8 `ToolTrace` fields

The plan defines `diagnostic_consistency_status` as "current diagnostic consistency-compatible scalar when applicable." The current `DiagnosticConsistencyStatus` Literal is `consistent | missing_terminal_runtime_diagnostic | terminal_category_conflict | non_runtime_terminal_without_scalar` (from `chapter_orchestrator.py:99-104`). The plan should reference this explicit type rather than using the vague "compatible scalar" wording.

Recommendation: in Slice B or the implementation planning gate, pin `diagnostic_consistency_status` to the current `DiagnosticConsistencyStatus` Literal or its explicit future equivalent.

## 4. Parent NBO Follow-Up Assessment

### NBO-1: EvidenceAvailability Invocation Point

- **Parent requirement**: "Slice A/B design must specify whether Agent invokes derive_evidence_availability() once at ChapterTaskPrepared or at another bounded lifecycle point."
- **Slice A resolution**: §5.2 — Agent derives `EvidenceAvailability` exactly once after `ChapterFactProjection` is available and before the first `ChapterTask` enters `prepared`. The value is stored on `AgentReportRun.evidence_availability`. All tasks receive the same value. Repair attempts reuse the run-level value and must not recompute.
- **Assessment**: **RESOLVED**. The invocation point is bounded, unambiguous, and immune to repair-attempt drift. The additional clause that multi-year evidence shape changes require a separate implementation gate provides forward guardrail.

### NBO-2: Equivalence Test Scope

- **Parent requirement**: "Slice D or the later implementation planning gate must define equivalence criteria before code changes."
- **Slice A resolution**: Not applicable to Slice A. Section 2 correctly scopes Slice A as dataclass design only; equivalence testing belongs to Slice D.
- **Assessment**: **DEFERRED to Slice D**. This is correct — Slice A is not required to resolve NBO-2.

### NBO-3: FinalAssemblyReadiness Handoff Boundary

- **Parent requirement**: "Future design slices must state whether Agent FinalAssemblyReadiness feeds or replaces current Service final assembly readiness."
- **Slice A resolution**: §5.9 — Agent `FinalAssemblyReadiness` is a body-readiness handoff, not a replacement. It feeds Service final assembly. Service keeps final product fail-closed mapping, chapter 0/7 assembly, stdout/stderr behavior and quality policy until a later implementation gate explicitly changes them.
- **Assessment**: **RESOLVED**. The handoff boundary is explicit. The "at least as strict" clause (§5.9 mapping) prevents weakening. The "until a later implementation gate" clause preserves Service authority.

## 5. Scope and Forbidden-Action Audit

| Check | Result |
|---|---|
| No implementation authorized | PASS — plan explicitly design-only (§1, §4, §9) |
| No `fund_agent/agent` creation | PASS — explicitly forbidden (§4) |
| No `ChapterOrchestrator` migration | PASS — explicitly forbidden (§4) |
| No provider/default/runtime/budget change | PASS — explicitly forbidden (§4, §5.2 multi-year guard) |
| No live `--use-llm`, retry, probe | PASS — explicitly forbidden (§4, §7) |
| No Dayu/LangGraph/MCP runtime | PASS — explicitly forbidden (§4) |
| No quality gate, golden/readiness, score-loop change | PASS — explicitly forbidden (§4) |
| No multi-year runtime change | PASS — §5.2 explicitly defers to separate gate |
| No public chapter id `0-7` change | PASS — not mentioned, current ids preserved |
| No PR, push, merge | PASS — explicitly forbidden (§4) |
| No Host business semantics | PASS — Host stays lifecycle-only throughout |
| No provider construction in Agent | PASS — §5.1: "carry Service-constructed writer/auditor clients as explicit typed per-run fields"; provider construction stays in Service |
| No `extra_payload` business parameters | PASS — §5.1: "must not carry extra_payload" |

## 6. ToolTrace Safety Verification

The plan forbids the following from serialized `ToolTrace` (§5.8) and `ToolCallRequest` (§5.6):

| Sensitive field | Forbidden in plan |
|---|---|
| prompt | Yes (§5.6 forbidden fields, §5.8 trace safety) |
| draft | Yes (§5.6 forbidden fields: "draft markdown in serialized trace identity"; §5.8) |
| raw provider response | Yes (§5.6, §5.8) |
| raw audit response | Yes (§5.6, §5.8) |
| API key | Yes (§5.6, §5.8) |
| Authorization header | Yes (§5.6, §5.8) |
| bearer token | Yes (§5.6, §5.8) |
| model value | Yes (§5.6: "model value or base URL value"; §5.8) |
| base URL value | Yes (§5.6, §5.8) |
| secrets (generic) | Covered by specific API key / token / Authorization field exclusions |

The safety perimeter matches the current safe diagnostics rules established in the codebase (e.g., `serialize_chapter_runtime_diagnostics()` and `serialize_chapter_prompt_contract_diagnostics()` exclusions). The plan explicitly allows ids, counts, categories, char counts, and approximate prompt token counts — consistent with current safe scalar diagnostics.

## 7. Current-to-Future Mapping Sufficiency

The mapping matrix (§6) covers all 9 current types listed in the plan objective (§2):

| Current type | Future type | Mapping present |
|---|---|---|
| `ChapterOrchestrationInput` | `AgentReportRun` init | Yes |
| `_TypedTemplateInputs.evidence_availability` | `AgentReportRun.evidence_availability` | Yes |
| `ChapterOrchestrationPolicy.max_repair_attempts` | `AgentRepairPolicy.max_repair_attempts` | Yes |
| `ChapterAttemptRecord` | `ChapterAttempt` | Yes (one-to-one) |
| `ChapterRunResult` | `ChapterTask` | Yes |
| `ChapterOrchestrationResult` | `AgentReportRun` + reconstructed result | Yes |
| `ChapterRepairDecision` | `AgentRepairPolicy` decision output | Yes |
| writer/auditor calls | `ToolCallRequest/Result/Trace` | Yes |
| Service `FinalAssemblyReadiness` | Agent body-readiness handoff | Yes |

Assessment: **SUFFICIENT** for a design-only Slice A plan. The mapping is explicit enough that a later implementation planning gate can derive concrete field-level mappings without redesigning the type model.

## 8. Validation Commands and Results

```text
$ git diff --check -- docs/reviews/mvp-agent-engine-design-slice-a-dataclass-design-plan-20260608.md
(exit 0, no output — no whitespace errors)

$ git diff --check -- docs/reviews/mvp-agent-engine-design-slice-a-dataclass-design-plan-20260608.md docs/reviews/mvp-agent-engine-design-slice-a-dataclass-design-plan-review-ds-20260608.md
(exit 0, no output)
```

No forbidden validation was performed (no `--use-llm`, no provider readiness, no endpoint/DNS/curl/socket probe, no implementation scaffold).

## 9. Residual Risks and Open Questions

1. **AgentReportRun carries per-run writer/auditor clients as typed fields (§5.1)** — The plan says these are "not ToolRegistry tools and are not serialized into traces." This is correct architecturally, but the exact Python type for transporting clients across the Service→Agent boundary (Protocol vs concrete type vs wrapper) is deferred to implementation planning. No risk at design stage.

2. **ToolCallRequest.deadline_observed (§5.6)** — The plan requires Agent to record whether Host deadline/cancel was checked before each tool call. The exact mechanism (Host cancel token read, deadline comparison) is deferred. This is a boundary concern between Host and Agent that needs explicit specification in Slice B or the implementation gate.

3. **AgentRepairPolicy.repairable_hints vs terminal_hints (§5.5)** — These are described as "Fund-owned hints" but stored on the Agent-owned policy object. The plan correctly states Agent must not redefine Fund issue meaning, but the split between Fund producing hints and Agent consuming them could produce a classification gap if a new Fund issue type doesn't clearly map to repairable or terminal. Mitigation: the `stop` action in repair decisions plus the bounded attempt ceiling means unknown hints default to fail-closed.

4. **Single reviewer (AgentDS only)** — Per the plan's §8, MiMo absence is authorized with Codex reviewer capacity. This review is DS-only. The review scope is design-only with no implementation, which is within the `standard` gate classification for a single-reviewer design review.

## 10. Acceptable Outcomes Checklist

| Outcome | Status |
|---|---|
| `PASS` | — |
| `PASS_WITH_NON_BLOCKING_OBSERVATIONS` | **SELECTED** (4 informational observations, zero blocking) |
| `BLOCKED_BY_SCOPE_OVERREACH` | Not applicable |
| `BLOCKED_BY_UNRESOLVED_CONTRACT` | Not applicable |

The artifact is ready for controller judgment.
