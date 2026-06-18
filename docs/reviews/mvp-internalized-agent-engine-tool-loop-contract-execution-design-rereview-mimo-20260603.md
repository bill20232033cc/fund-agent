# MVP internalized Agent engine/tool-loop contract execution design — MiMo re-review

## Reviewer Self-Check

- Role: independent re-review worker, not controller.
- Gate: `MVP internalized Agent engine/tool-loop contract execution design gate`.
- Classification: heavy.
- Scope: adversarial re-review of design fixes; no code, no implementation, no truth-source edits, no reports/commits/push/PR.
- Required read set: completed for `AGENTS.md`, `docs/design.md`, `docs/implementation-control.md`, `docs/current-startup-packet.md`, review target `docs/reviews/mvp-internalized-agent-engine-tool-loop-contract-execution-design-20260603.md`, fix evidence `docs/reviews/mvp-internalized-agent-engine-tool-loop-contract-execution-design-review-fix-evidence-20260603.md`, prior DS review `docs/reviews/mvp-internalized-agent-engine-tool-loop-contract-execution-design-review-ds-20260603.md`, prior MiMo review `docs/reviews/mvp-internalized-agent-engine-tool-loop-contract-execution-design-review-mimo-20260603.md`, and retained `summary.json`.
- Actions taken: wrote this single `docs/reviews/` re-review artifact.
- Actions intentionally not taken: no controller start, no implementation, no source/config/runtime edits, no commit, no push, no PR.

## Review Target

`docs/reviews/mvp-internalized-agent-engine-tool-loop-contract-execution-design-20260603.md` (post-fix version)

## Fix Evidence Under Review

`docs/reviews/mvp-internalized-agent-engine-tool-loop-contract-execution-design-review-fix-evidence-20260603.md`

## Verdict

**Pass. No blocking findings.** All material findings from both prior reviews (MiMo 12 findings, DS 4 findings) are addressed by the fix evidence or by corresponding design text corrections. Fixes are text-only, introduce no new blockers, no scope leaks, no implementation/provider budget/score-loop/Ch3 calibration leakage.

---

## Finding-by-Finding Verification

### MiMo Prior Review Findings (12)

| # | Finding | Claimed Fix | Verified? | Notes |
|---|---|---|---|---|
| F1 | Ch3 evidence-to-diagnosis mismatch | Fixed | Yes | Design §Current Facts line 29 now correctly states `programmatic:C2` / `code_bug_other` and explicitly disclaims `must_not_cover` / `言行一致` as proven root cause. Matches `summary.json` ch3 `prompt_contract_diagnostics` (`issue_id_prefix_counts: {"programmatic:C2": 1}`, `primary_subcategory: code_bug_other`). |
| F2 | Provider client injection mechanism unspecified | Fixed | Yes | Design §ToolRegistry line 118 now specifies: "Service constructs writer/auditor Protocol clients and passes them to `AgentReportRun` as explicit typed per-run fields. Agent then passes those clients into Fund writer/auditor tools as typed tool inputs." Matches current `ChapterOrchestratorLLMClients` pattern. |
| F3 | Diagnostic-only semantic audit dangling clause | Partially addressed | Yes | Design §State Machine line 175 now reads: "diagnostic-only semantic audit is deferred to a post-MVP observability gate." The dangling clause is replaced with an explicit deferral. Original MiMo F3 suggested this exact fix. |
| F4 | Host cancellation/deadline observation mechanism unspecified | Fixed | Yes | Design §Runner line 102 now specifies: "Agent checks the Host cancel token and global deadline at task scheduling boundaries, before each `ChapterTask` dispatch, and after each tool-call return. Mid-tool-call interruption relies on provider client timeout rather than Agent polling." |
| F5 | Repair planner co-ownership | Fixed | Yes | Design §ToolRegistry lines 129-131 now cleanly split: Fund owns `RepairSemantics` (what can be fixed, evidence mapping), Agent owns `RepairPolicy` (attempt counting, budget enforcement, stop/retry). Table row `fund.repair_semantics` renamed from `fund.repair_planner` to reflect this. |
| F6 | Final assembly readiness ↔ Service FinalChapterAssembler mapping | Fixed | Yes | Design §Runner lines 99-100 now state: "Agent-owned `FinalAssemblyReadiness` should feed or replace the current Service `FinalChapterAssembler` readiness check only in a future implementation gate. Until that gate is accepted, Service stdout and fail-closed behavior stay unchanged." |
| F7 | Over-designed terminal states | Fixed | Yes | Terminal states simplified to three: `accepted`, `partial_fail_closed`, `host_interrupted`. Line 112 explicitly notes per-chapter failure kinds remain in `ToolTrace`. |
| F8 | Agent task graph ↔ Service ChapterOrchestrator mapping | Fixed | Yes | Design §Runner line 96 now states: "The Agent task graph subsumes the current Service `ChapterOrchestrator.orchestrate_chapters()` behavior for chapters 1-6." |
| F9 | Ch2 internal subcontracts tracing | Addressed | Yes | Residual risks table line 294 now includes: "Agent task graph should support optional sub-requirement ids within a ChapterTask for traceability and targeted repair; this is an implementation detail for the typed contract implementation gate." |
| F10 | ToolTrace `redaction_policy_id` and `artifact_safe` premature | Not explicitly in fix evidence | Acceptable | These fields remain in the ToolTrace schema table. Severity was low (over-design, not correctness). The fields are still marked "Proposed future design" and the schema note at line 166 covers phase-list completeness. This is an acceptable non-fix for a low-severity finding. |
| F11 | Evidence Confirm not referenced in ToolTrace phases | Addressed | Yes | Design §ToolTrace line 166 now reads: "The phase list is MVP-complete for this design. Evidence Confirm remains a future phase and would add an `evidence_confirm` trace phase only after a separate Evidence Confirm gate." |
| F12 | Partial-success artifact output contract unspecified | Fixed | Yes | Design §Runner lines 101 now specifies the typed `AgentRunResult` contract: "terminal state, per-chapter status matrix, per-chapter failure kinds, ToolTrace summary, and `FinalAssemblyReadiness`." |

### DS Prior Review Findings (4)

| # | Finding | Claimed Fix | Verified? | Notes |
|---|---|---|---|---|
| DS-F1 | `fund.evidence_availability_projection` tool redundant | Fixed | Yes | Removed from ToolRegistry table. Design line 40 now states `EvidenceAvailability` is "a precomputed derived input from `ChapterFactProjection` before the tool loop; it is not registered as a tool." |
| DS-F2 | ToolRegistry phase distinction unclear | Fixed | Yes | Design line 116 now includes: "ToolRegistry phasing is explicit: schema contracts in Slice A, fake-tool execution in Slice B, Fund wrapping in Slice C, migration in Slice D, and readiness integration in Slice E." |
| DS-F3 | Missing PLAN_REPAIR→STOP transition in diagram | Fixed | Yes | State machine diagram lines 188, 192 now show `PLAN_REPAIR -> STOP_FAIL_CLOSED` with annotation "repair budget exhausted or planner stop" for both programmatic and semantic audit paths. |
| DS-F4 | Mixed-failure terminal classification under-specified | Fixed | Yes | Simplified terminal states (3 instead of 6) plus line 112: "Detailed runtime, contract, semantic, missing-evidence, dependency, and repair-exhaustion classifications live at per-chapter / per-attempt level in `ToolTrace`, including mixed failures across attempts." This makes per-chapter mixed-failure classification a ToolTrace concern, not a terminal state concern. |

---

## Scope Leak / Boundary Check

| Check | Result |
|---|---|
| Implementation code introduced | No. Fix evidence explicitly states "No code changed." |
| Provider budget changed | No. Provider budget is in non-goals and residual risks. |
| Score-loop wired | No. Score-loop is in non-goals. |
| Ch3 calibration implemented | No. Ch3 calibration is deferred; design only corrects the evidence characterization. |
| Truth docs modified | No. `AGENTS.md`, `docs/design.md`, `docs/implementation-control.md`, `docs/current-startup-packet.md` are unchanged. |
| Retained report artifacts modified | No. `summary.json` is unchanged. |
| `dayu-agent` / `dayu.engine` / `dayu.host` introduced | No. Dayu mapping section unchanged; internalization is local-project-only. |
| `extra_payload` introduced | No. All explicit parameters remain typed. |
| Deterministic default changed | No. `analyze/checklist` default preserved. |
| Fail-closed semantics changed | No. Terminal states are simpler but fail-closed semantics preserved. |
| Host/Fund/Agent/Service boundary violated | No. Each fix strengthens boundary clarity. |

---

## New Blockers Check

No new blocking findings introduced by the fixes. All changes are text-only clarifications, simplifications, or explicit deferrals. No new runtime behavior, schema, contract, or ownership change was introduced.

---

## Non-Blocking Residual Risks

| Risk | Severity | Recommended destination |
|---|---|---|
| ToolTrace `redaction_policy_id` / `artifact_safe` remain in schema (MiMo F10 not fixed) | Low | Implementation planning gate can address; not a design defect |
| Provider runtime timeouts remain the primary real-run blocker | Unchanged | Provider runtime budget calibration gate (separate) |
| Ch3 `programmatic:C2` root cause needs diagnosis before calibration | Unchanged | Ch3-only calibration gate (separate) |
| Trace serializer safety testing | Open | Implementation gate with allowlist tests |
| Ch2 internal subcontracts tracing mechanism | Deferred | Typed contract implementation gate |
| ToolRegistry wiring/injection path at implementation time | Low | Implementation planning gate Slice A |
| Body chapter concurrency model (sequential vs parallel) | Low | Add explicit statement or defer to async Host runner gate |
| Tool call timeout vs global deadline interaction during blocking provider HTTP calls | Medium | Implementation planning gate — cancellation propagation for blocking I/O |
| `audit_focus` boundary enforcement mechanism | Medium | Implementation planning gate — needs typed constraint |

---

## Validation

- Review target artifact exists and is readable: pass.
- Fix evidence artifact exists and is readable: pass.
- Required read set consumed: pass.
- All MiMo prior findings (12) disposition verified against fix evidence and design text: pass (10 fixed, 1 partially addressed with explicit deferral, 1 acceptable non-fix for low severity).
- All DS prior findings (4) disposition verified against fix evidence and design text: pass (4/4 fixed).
- No code, implementation, truth-source, or runtime changes made: pass.
- No new blockers introduced by fixes: pass.
- No scope leaks detected: pass.

## Secret-Safety Statement

This review contains no API key, Authorization header, Bearer token, cookie, password, raw provider response, raw audit response, prompt body, writer draft, repair draft, hidden provider config value, or raw PDF/source text. It references only safe artifact paths, finding ids, enum labels, and high-level diagnostic categories.
