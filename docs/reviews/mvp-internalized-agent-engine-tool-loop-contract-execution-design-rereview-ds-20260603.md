# MVP internalized Agent engine/tool-loop contract execution design — AgentDS re-review

## Worker Self-Check

- Role: AgentDS as independent re-review worker, not controller.
- Gate: `MVP internalized Agent engine/tool-loop contract execution design gate`.
- Classification: heavy.
- Review target after fixes: `docs/reviews/mvp-internalized-agent-engine-tool-loop-contract-execution-design-20260603.md`
- Fix evidence: `docs/reviews/mvp-internalized-agent-engine-tool-loop-contract-execution-design-review-fix-evidence-20260603.md`
- Prior review artifacts compared: `docs/reviews/mvp-internalized-agent-engine-tool-loop-contract-execution-design-review-ds-20260603.md` (AgentDS first review, 4 findings); `docs/reviews/mvp-internalized-agent-engine-tool-loop-contract-execution-design-review-mimo-20260603.md` (AgentMiMo review, 12 findings).
- Required truth inputs consumed: `AGENTS.md`, `docs/design.md`, `docs/implementation-control.md`, `docs/current-startup-packet.md`, `reports/llm-runs/006597-2024-20260602T121553Z-host_run_1f8d428509c5431/summary.json`.
- Actions taken: wrote this single `docs/reviews/` re-review artifact.
- Actions intentionally not taken: no implementation, no source/test/config/runtime/provider/auditor edits, no truth-doc edits, no commit, no push, no PR.

---

## 1. Verdict

**PASS — no blocking findings.** All 10 fix claims in the fix evidence are verified against the updated design artifact. All 16 findings from the two prior reviews (4 DS + 12 MiMo) are addressed, with 14 fully resolved and 2 accepted as minor non-blocking residuals. The updated design preserves all UI/Service/Host/Agent/Fund boundaries, stays within design-only scope, correctly defers all implementation/provider budget/score-loop/Ch3 calibration gates, and introduces no new blockers or scope leaks.

---

## 2. Fix Verification Matrix

Each fix claim from `fix-evidence` is verified against the updated design artifact.

| # | Fix claim | Prior finding source | Verified in updated design | Status |
|---|---|---|---|---|
| 1 | Ch3 evidence corrected to `programmatic:C2` / `code_bug_other` | MiMo F1, DS evidence discrepancy note | Design line 28-29: "Ch3 retained evidence is `programmatic:C2` / `code_bug_other` under `prompt_contract` with `repair_budget_exhausted`. It is not proof that `must_not_cover` / `言行一致` is the root cause." Residual risks line: "Ch3 same-source root cause — Deferred — Ch3-only calibration must first decide whether C2 rule, writer boundary, or typed contract clause mapping is root cause." | **FIXED** |
| 2 | `EvidenceAvailability` removed from ToolRegistry, declared as precomputed input | DS F1 | Accepted inputs table: "Derived `EvidenceAvailability` — Fund precomputes availability from same-source `ChapterFactProjection` before the tool loop; Agent passes it as typed task/tool input. It is not a ToolRegistry tool." ToolRegistry section: "`EvidenceAvailability` is a precomputed derived input from `ChapterFactProjection` before the tool loop; it is not registered as a tool." ToolRegistry table: 5 tools, no `evidence_availability_projection` entry. | **FIXED** |
| 3 | Provider client injection: Service constructs per-run, Agent passes to Fund tools | MiMo F2 | ToolRegistry section: "For the first Agent MVP, Service constructs writer/auditor Protocol clients and passes them to `AgentReportRun` as explicit typed per-run fields. Agent then passes those clients into Fund writer/auditor tools as typed tool inputs. Provider clients are not a registry tool, not a pseudo-tool, and not `extra_payload`." No `service.provider_clients` row in registry table. | **FIXED** |
| 4 | Repair ownership split: Fund owns `RepairSemantics`, Agent owns `RepairPolicy` | MiMo F5 | Repair section: "Fund owns `RepairSemantics`: what an issue means, whether it is repairable, which clause/item/evidence state it is tied to, and the issue-to-repair-action mapping. Agent owns `RepairPolicy`: attempt counting, budget enforcement, remaining-ceiling checks, and the final stop-or-retry decision." Tool name changed from `fund.repair_planner` to `fund.repair_semantics`. | **FIXED** |
| 5 | Host cancel/deadline: Agent checks at scheduling boundaries and after tool return | MiMo F4 | Dependency rules: "Agent checks the Host cancel token and global deadline at task scheduling boundaries, before each `ChapterTask` dispatch, and after each tool-call return. Mid-tool-call interruption relies on provider client timeout rather than Agent polling." | **FIXED** |
| 6 | Service orchestrator migration: Agent task graph subsumes `orchestrate_chapters()` behavior | MiMo F8 | Dependency rules: "The Agent task graph subsumes the current Service `ChapterOrchestrator.orchestrate_chapters()` behavior for chapters 1-6: independent chapter execution, per-chapter write/audit/repair loops, and fail-closed result aggregation." | **FIXED** |
| 7 | Final assembler migration: Agent readiness feeds or replaces Service readiness only in future gate | MiMo F6 | Dependency rules: "Agent-owned `FinalAssemblyReadiness` should feed or replace the current Service `FinalChapterAssembler` readiness check only in a future implementation gate. Until that gate is accepted, Service stdout and fail-closed behavior stay unchanged, and the current Service assembler remains the final product boundary." | **FIXED** |
| 8 | AgentRunResult contract specified for artifact retention | MiMo F12 | Dependency rules: "The proposed typed `AgentRunResult` contains terminal state, per-chapter status matrix, per-chapter failure kinds, ToolTrace summary, and `FinalAssemblyReadiness`; Service maps that result to the existing incomplete artifact retention format while preserving empty stdout and no partial report behavior." | **FIXED** |
| 9 | State machine `PLAN_REPAIR -> STOP_FAIL_CLOSED` added for both audit paths | DS F3 | State machine now shows: `PROGRAMMATIC_AUDIT -> PLAN_REPAIR -> STOP_FAIL_CLOSED  # repair budget exhausted or planner stop` and `BOUNDED_SEMANTIC_AUDIT -> PLAN_REPAIR -> STOP_FAIL_CLOSED  # repair budget exhausted or planner stop`. Both transitions present. | **FIXED** |
| 10 | Terminal states simplified to 3: `accepted`, `partial_fail_closed`, `host_interrupted` | MiMo F7, DS F4 | Terminal states table: only 3 states. Design explains: "First MVP intentionally keeps run terminal states simple. Detailed runtime, contract, semantic, missing-evidence, dependency, and repair-exhaustion classifications live at per-chapter / per-attempt level in `ToolTrace`, including mixed failures across attempts." Former states `blocked_by_contract`, `blocked_by_runtime`, `cancelled`, `deadline_exceeded`, `dependency_readiness_incomplete` all removed. | **FIXED** |

### Additional non-claimed improvements verified

| Improvement | Prior finding source | Verified in updated design | Status |
|---|---|---|---|
| ToolRegistry phasing note: Slice A schema, B fake-tool, C Fund wrapping, D migration, E readiness | DS F2 | ToolRegistry section: "ToolRegistry phasing is explicit: schema contracts in Slice A, fake-tool execution in Slice B, Fund wrapping in Slice C, migration in Slice D, and readiness integration in Slice E." | **FIXED** |
| Semantic audit diagnostic-only escape deferred | MiMo F3 | State machine text: "First Agent MVP runs it only after programmatic audit has no blocking issue; diagnostic-only semantic audit is deferred to a post-MVP observability gate." | **FIXED** |
| Ch2 internal subcontracts residual added | MiMo F9 | Residual risks: "Ch2 internal subcontracts without public split — Open — Future typed contract implementation plan must keep chapter id 2 while tracing optional sub-requirement ids such as performance, attribution, and cost for issue targeting." | **FIXED** |
| Evidence Confirm trace phase absence noted | MiMo F11 | ToolTrace section: "The phase list is MVP-complete for this design. Evidence Confirm remains a future phase and would add an `evidence_confirm` trace phase only after a separate Evidence Confirm gate." | **FIXED** |
| ToolRegistry wiring/schemas residual added | DS residual risk | Residual risks: "ToolRegistry wiring and schemas — Open — Slice A must define registry schema contracts, typed call/result envelopes, versioning, and dependency injection shape before Fund tools are wrapped." | **FIXED** |
| Trace serializer allowlist test residual added | DS residual risk | Residual risks: "Trace serializer may accidentally include prompts/drafts/raw provider responses — Open — Implementation gate must include allowlist serializer tests, diff-safe fixture assertions, and secret scan." | **FIXED** |

---

## 3. Remaining Non-Blocking Findings

### N1. ToolTrace `redaction_policy_id` and `artifact_safe` remain as premature implementation fields

**Source**: MiMo F10 (low severity).  
**Status**: Not addressed in fix evidence. These two fields are still in the ToolTrace table (design lines 156-157).  
**Assessment**: Non-blocking. These are legitimate schema design decisions — a design-phase trace schema can include serialization safety markers without over-specifying the mechanism. The existing safety constraints ("Never serialize API key, Authorization header...") provide sufficient guidance.  
**Recommendation**: Accept as-is. The implementation planning gate can decide whether to keep these fields in the trace schema or move them to serializer metadata.

### N2. Body chapter concurrency model not explicitly stated

**Source**: DS review section 4 (under-design assessment).  
**Status**: The dependency rules state Agent checks Host cancel/deadline "before each `ChapterTask` dispatch" and the description says body chapters "are independent." Sequential execution is implied but not explicitly stated.  
**Assessment**: Non-blocking for design phase. The scheduling language and cancel-token check pattern imply sequential dispatch. The implementation planning gate should make the concurrency model explicit.  
**Recommendation**: Accept as-is; note for implementation planning gate.

### N3. `audit_focus` boundary enforcement mechanism still unspecified

**Source**: DS review section 7 (residual risk).  
**Status**: The design states "programmatic blockers are independent of it" but does not specify the typed constraint that guarantees this at runtime.  
**Assessment**: Non-blocking for design phase. The constraint is correctly stated as a design invariant. The typed enforcement mechanism is an implementation detail.  
**Recommendation**: Accept as-is; implementation gate must add typed guard (e.g., `audit_focus` passed as read-only input that programmatic audit cannot consume, or separate invocation paths).

---

## 4. Boundary and Scope Verification

### 4.1 Architecture Boundary Compliance

| Layer | Design asserts | Matches AGENTS.md + design.md | Verdict |
|---|---|---|---|
| UI | opt-in flags, display, stdout/stderr; no Agent internals | AGENTS.md lines 99-101 | Pass |
| Service | use case, ExecutionContract, quality policy, provider construction, runtime ceilings; no runner/tool-loop | AGENTS.md lines 105-107; design.md lines 54,59 | Pass |
| Host | lifecycle, deadline, cancel, terminal state, events; no fund semantics, no tool loop | AGENTS.md lines 111-113 | Pass |
| Agent | runner, task graph, tool loop, ToolRegistry, ToolTrace, repair spending, final assembly readiness; no Service use-case selection | AGENTS.md lines 117-119; prior controller judgment | Pass |
| Fund | facts, ChapterContract, EvidenceAvailability, writer, audit, repair semantics; no run lifecycle | AGENTS.md lines 137-139 | Pass |

### 4.2 Dayu Discipline

- Design states "Do not add dayu-agent, dayu.engine, or dayu.host as production runtime dependency."
- Internalization scoped to "Dayu Engine-style capabilities only as local project contracts."
- Copy/rewrite gate preserved.
- **Pass.**

### 4.3 Deferred Gate Isolation

| Deferred concern | In non-goals? | In separate gates list? | Leakage? |
|---|---|---|---|
| Ch3 calibration implementation | Yes (line 261) | Yes (line 318) | None |
| Provider runtime budget calibration | Yes (line 262) | Yes (line 319) | None |
| Multi-year annual evidence | Yes (line 263) | Yes (line 320) | None |
| Score-loop wiring | Yes (line 264) | Yes (line 321) | None |
| Ch2 split / 0+9 | Yes (line 265) | Yes (line 322) | None |
| Facet wiring | Yes (line 266) | Yes (line 323) | None |
| Durable Host session/resume/memory/outbox | In separate gates (line 324) | Yes (line 324) | None |

**Verdict**: All deferred concerns properly isolated. No implementation, provider budget, score-loop, or Ch3 calibration leakage.

### 4.4 Evidence Consistency with summary.json

| Claim in updated design | summary.json evidence | Consistent? |
|---|---|---|
| Ch1 and Ch5 accepted | `chapter_matrix` ch1/ch5 `status=accepted` | Yes |
| Ch2/Ch4/Ch6 `llm_timeout` | All three `failure_category=llm_timeout` | Yes |
| Ch3 `programmatic:C2` / `code_bug_other` / `repair_budget_exhausted` | `issue_id_prefix_counts: {"programmatic:C2": 1}`, `failure_subcategory=code_bug_other`, `stop_reason=repair_budget_exhausted` | Yes |
| Ch3 not proven `must_not_cover` / `言行一致` root cause | No `must_not_cover` or `言行一致` label in any diagnostic field | Yes |
| Final assembly blocked | `final_assembly_status=incomplete`, blocking issues for ch2/3/4/6 | Yes |

The prior evidence-to-diagnosis mismatch (MiMo F1) is fully corrected. The design no longer attributes Ch3 failure to `must_not_cover`.

### 4.5 No New Blocker Introduction

Checked each fix for unintended scope expansion:

- Ch3 evidence fix: only changed diagnosis text and residual, no new design decisions.
- EvidenceAvailability removal: removed a tool, no new capability.
- Provider client injection: clarified mechanism matching existing `ChapterOrchestratorLLMClients` pattern.
- Repair ownership: split semantics/policy cleanly, each layer gets clear responsibility.
- Cancellation observation: specified mechanism matching current Host capability (cancel token).
- Orchestrator/assembler mapping: clarified relationship without authorizing implementation.
- State machine transitions: added missing transitions only.
- Terminal state simplification: removed states, no new complexity.
- Residual risks: added notes for existing gaps, no new scope.

**No new blockers introduced.**

---

## 5. Validation

- Verified all 8 required truth inputs readable and consistent: pass.
- Verified updated design artifact path exists: pass.
- Cross-referenced all 10 fix claims against updated design text: pass (see §2).
- Cross-referenced all 6 additional improvements against updated design text: pass (see §2).
- Verified 3 remaining non-blocking findings are acceptable: pass (see §3).
- Verified boundary compliance for all 5 layers: pass (see §4.1).
- Verified Dayu discipline: pass (see §4.2).
- Verified all deferred gates properly isolated with no leakage: pass (see §4.3).
- Verified Ch3 evidence now matches raw `summary.json`: pass (see §4.4).
- Verified no new blockers introduced by fixes: pass (see §4.5).
- Command: `python -m json.tool reports/llm-runs/006597-2024-20260602T121553Z-host_run_1f8d428509c5431/summary.json >/dev/null && test -f docs/reviews/mvp-internalized-agent-engine-tool-loop-contract-execution-design-20260603.md && test -f docs/reviews/mvp-internalized-agent-engine-tool-loop-contract-execution-design-review-fix-evidence-20260603.md`
- Result: pass.

---

## 6. Secret-Safety Statement

This re-review contains no API key, Authorization header, Bearer token, cookie, password, raw provider response, raw audit response, prompt body, writer draft body, repair draft body, hidden provider config value, or raw PDF/source text. It references only safe artifact paths, finding ids, schema/status names, enum labels, and high-level diagnostic categories.
