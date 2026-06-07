# MVP Agent Engine Design Slice E Implementation Planning Gate — Plan Review (AgentDS)

## 1. Review Metadata

| Field | Value |
|---|---|
| Reviewer | AgentDS |
| Target plan | `docs/reviews/mvp-agent-engine-design-slice-e-implementation-planning-gate-plan-20260608.md` |
| Review artifact | `docs/reviews/mvp-agent-engine-design-slice-e-implementation-planning-gate-plan-review-ds-20260608.md` |
| Date | 2026-06-08 |
| Scope | plan review only — no implementation, no source edits, no live commands |
| Parent context | Slice A judgment `8d50b40`, Slice B judgment `1c3c031`, Slice C judgment `bc45778`, Slice D judgment `9f6d360` |
| Current gate classification | `standard` |

## 2. Verdict

**`PASS_WITH_NON_BLOCKING_OBSERVATIONS`**

The plan is code-generation-ready in structure: it defines allowed files per slice, explicit validation commands, a complete terminal mapping table over all current `ChapterRunStopReason` values, a no-live validation matrix with 10 test scenarios, forbidden actions, stop conditions, and review route. The plan correctly preserves Service/Host/Agent/Fund boundaries, forbids live/provider/network actions, and respects all Slice A-D accepted contracts.

Three parent follow-up requirements are incompletely addressed. None blocks controller from authorizing implementation, but all should be resolved before implementation workers proceed beyond E1.

## 3. Findings

### F1 (NON_BLOCKING): `blocked_tool_contract` disposition omitted without acknowledgment

**Severity**: moderate — unresolved follow-up from Slice C DS NBO-2.

**Evidence**: Slice C controller judgment §4 DS NBO-2 requires: "The later implementation planning gate must either define concrete trigger conditions for `blocked_tool_contract` or remove/rename that terminal state from the implementation contract."

Slice E §5 terminal mapping table enumerates 22 current `ChapterRunStopReason` → future Agent terminal mappings. `blocked_tool_contract` does not appear. The plan neither defines its trigger conditions, nor explains why it was removed, nor acknowledges the Slice C requirement.

The terminal mapping is otherwise complete for all current stop reasons, so the omission is not a contract breach — but it leaves the Slice C DS NBO-2 status ambiguous for controller judgment.

**Recommendation**: Add an explicit disposition sentence in §5 or a new §11 stating that `blocked_tool_contract` is removed from the first-Agent-terminal set because current Fund tool adapters only wrap four primitive calls with no novel contract semantics beyond what existing stop reasons capture. Controller can then accept or reject the disposition.

### F2 (NON_BLOCKING): Residual owners not enumerated

**Severity**: moderate — unresolved follow-up from Slice D §5.

**Evidence**: Slice D controller judgment §5 explicitly requires Slice E to include "residual owners for any current Service behavior not yet representable by the future Agent contracts."

The plan has no residual owner section. The closest equivalent is §10 stop conditions, which cover when to return to controller but do not enumerate owners for known gaps.

Current Service behaviors that are at least partially unrepresented by the Agent contracts include:

- `repair_hint=patch` → collapsed to `regenerate` (whole-chapter) per E3; no typed patch API gate is scheduled;
- provider timeout retry remains Service/provider-client only; Agent has no visibility into retry attempts (intentional per E3, but the residual owner for provider-retry diagnostics is unstated);
- `prompt_contract` subcategories (`code_bug_other`, `l1_numerical_closure`, `unknown_anchor` etc.) are flattened to `blocked_prompt_contract` in the terminal mapping; the subcategory is preserved only in chapter-attributed blocked reasons per E1, not in the terminal state name.

**Recommendation**: Add a §11 residual owners section. Even if the list is empty (all behaviors are representable), state that explicitly so the Slice D requirement is closed rather than silently omitted.

### F3 (NON_BLOCKING): Prompt char/token derivation rule not explicitly stated

**Severity**: low — unresolved follow-up from Slice B DS NBO-1.

**Evidence**: Slice B controller judgment §4 DS NBO-1 requires: "The later implementation planning gate must specify that prompt char counts and approximate prompt token counts are derived from in-memory prompt length heuristics only."

Slice E §E2 ToolTrace safety rules say what must NOT be serialized (prompt text, draft markdown, etc.) but do not state the positive derivation rule for char/token count diagnostics. The requirement is implicit in the "allowlist-only" constraint but not explicit.

**Recommendation**: Add a sentence in §E2: "Prompt char counts and approximate token counts must be derived from in-memory prompt length heuristics only; they must not require retained prompt text, external token-count services, or network access."

### F4 (NON_BLOCKING): No pre-migration Service baseline regression test specified

**Severity**: low-moderate — implementation risk for E4.

**Evidence**: E4 authorizes modification of `fund_agent/services/chapter_orchestrator.py` and `fund_agent/services/fund_analysis_service.py`, both in the current production path. The E4 validation block runs Agent bridge tests and existing Service tests, but does not include an explicit pre-migration baseline capture step.

E4 requirement says "migrate Service `ChapterOrchestrator` execution mechanics only after parity tests pass in the same implementation gate." This is correct in principle, but the validation commands in E4 run tests after code changes, not before. An implementation worker could interpret "parity tests pass" as "new Agent bridge tests pass" without verifying that the pre-migration Service tests produce identical outcomes.

**Recommendation**: In §E4, add a sequencing requirement: capture existing Service test output before any code changes, then assert parity after migration. This can be a documentation requirement in the implementation evidence artifact rather than a code change.

### F5 (NON_BLOCKING): Validation matrix rows not explicitly mapped to test files

**Severity**: low — testability and review clarity.

**Evidence**: §6 lists 10 validation requirements but does not map each to specific test files or test function names. The validation commands in §E4 cover 5-6 test files, but a reviewer cannot verify that every matrix row has a corresponding assertion without reading the implementation tests.

**Recommendation**: Add a column to the §6 table mapping each requirement to the expected test file or a short assertion description. Example: "unsafe ToolTrace data" → `tests/agent/test_tool_adapters.py::test_trace_excludes_prompt_and_raw_response`.

### F6 (NON_BLOCKING): Overbroad allowed-files authorization in E4

**Severity**: low — boundary concern.

**Evidence**: E4 allows editing `fund_agent/services/fund_analysis_service.py`, which is the production `--use-llm` entry point (§4.4 in startup packet). The plan's requirements constrain what Service may do (keep provider construction, keep final product fail-closed mapping), but the allowed-files list gives implementation worker authority to modify any section of the file, not just the bridge integration point.

The current file also contains `analyze()` (deterministic), `analyze_with_llm()`, and `analyze_with_llm_execution()`. Only the latter method needs bridging to Agent. The plan does not specify which methods may or may not be changed.

**Recommendation**: Narrow E4 requirements to specify that only `analyze_with_llm_execution()` or a new bridge method may be changed; deterministic `analyze()` and `analyze_with_llm()` must remain unchanged unless the implementation evidence justifies the change. Alternatively, add a new bridge file (e.g., `fund_agent/services/agent_bridge.py`) and keep the existing Service files read-only in E4.

### F7 (NON_BLOCKING): No per-slice partial-acceptance mechanism

**Severity**: low — sequencing risk.

**Evidence**: §10 says "stop or return to controller if any implementation slice cannot preserve equivalence." This is correct but does not define what happens if E1-E3 succeed but E4 fails. Can E1-E3 be accepted independently (Agent contracts, tool adapters, runner exist but Service bridge is deferred)? Or does a single slice failure invalidate all previous slices?

The implementation-control.md current gate status says "No Agent runtime implementation is authorized," which implies E1-E3 code cannot be committed independently without E4 proving equivalence.

**Recommendation**: Clarify that implementation must proceed sequentially and atomically: E1-E4 code must all be written in a single implementation gate, with E4 bridge tests as the final acceptance gate. If E4 cannot achieve equivalence, all Agent code changes must be reverted before returning to controller. Or, if partial acceptance is acceptable, state the conditions explicitly.

## 4. What The Plan Gets Right

All core structural requirements are satisfied:

- **Boundaries preserved** (§3, §E1-E4): Service owns provider construction and final product mapping; Agent owns chapter task state, tool envelopes, ToolTrace, repair policy and body chapter runner; Host stays business-opaque; Fund primitives are wrapped not rewritten.
- **Terminal mapping** (§5): Exhaustive over all 22 current `ChapterRunStopReason` values with explicit failure category conditions. `llm_exception + code_bug` is correctly mapped to `blocked_internal_code_bug` (not provider/runtime), resolving the Slice D Codex blocking issue.
- **No-live validation matrix** (§6): 10 scenarios cover accepted, blocked, provider-runtime, prompt-contract, code-bug, fact-gap, budget-exhausted, mixed-chapter, duplicate-row, and unsafe-ToolTrace cases.
- **Forbidden actions** (§3, §6): Explicitly excludes live `--use-llm`, retry, endpoint probe, provider/default/runtime changes, score-loop, multi-year, golden/readiness, PR/push/release, and `dayu-agent`/LangGraph/MCP dependencies.
- **Hidden retry forbidden** (§E3): Explicitly requires every repeated action to be in attempt ledger, repair decision ledger or ToolTrace. Provider timeout retry remains Service/provider-client and does not consume Agent content repair budget.
- **ToolTrace safety** (§E2): 15-field exclusion list including prompt, draft, raw provider/audit response, API key, Authorization header, model value, base URL.
- **Repair budget separation** (§E3): Provider runtime failures do not trigger content repair; provider timeout retry does not consume Agent content repair budget.
- **Stop conditions** (§10): Eight explicit conditions covering live/provider authorization, boundary violations, terminal mapping gaps, ToolTrace unsafety, and premature live evidence.
- **Review route** (§7): Two-reviewer requirement with explicit review focus areas and artifact paths.
- **Gate classification aligned** with `AGENTS.md` standard gate requirements: plan, two independent reviews, controller judgment, and explicit validation commands.

## 5. Slice A-D Follow-Up Status Against This Plan

| Parent | Requirement | Slice E status |
|---|---|---|
| A NBO-5 | hidden retry semantics | **resolved**: §E3 "hidden Agent retry is forbidden; every repeated writer, auditor, tool or repair action must be represented in attempt ledger, repair decision ledger or ToolTrace" |
| A NBO-6 | chapter-attributed blocked reasons | **resolved**: §E1 "preserve chapter-attributed blocked reasons: chapter id, stop reason and failure category must be reconstructable without unsafe payloads" |
| A NBO-7 | diagnostic_consistency_status explicit | **resolved**: §E1 "pin `DiagnosticConsistencyStatus` to current literals or an explicit named future equivalent" |
| A Codex NBO-1 | runtime diagnostics safe projection | **resolved**: §E2 15-field allowlist exclusion |
| B DS NBO-1 | prompt char/token derivation rule | **partially resolved**: §E2 excludes prompt text but does not state positive derivation rule (see F3) |
| B DS NBO-2 | host_interrupted scheduling boundary | **resolved**: §E3 "Host interruption may enter repair policy only as an already-normalized Agent scheduler event/status; repair policy and tool adapters must not import or inspect Host context/state" |
| B Codex NBO-1 | request_id scalar allowlist shape | **resolved**: §E2 "`request_id` may only be an optional scalar from an explicit response-header allowlist" |
| C DS NBO-1 | terminal state name mapping | **resolved**: §5 complete 22-row mapping table |
| C DS NBO-2 | blocked_tool_contract disposition | **not addressed**: omitted without explanation (see F1) |
| C DS NBO-3 | contract-level repair decision mapping validation | **resolved**: §5 mapping and §6 repair budget rows |
| C Codex NBO-1 | Host interruption scheduler-normalized | **resolved**: §E3 |
| D §5 | complete terminal mapping | **resolved**: §5 |
| D §5 | no-live outcome equivalence tests | **resolved**: §6 rows 1-6 |
| D §5 | repair budget equivalence tests | **resolved**: §6 row 7 |
| D §5 | final assembly readiness tests | **resolved**: §6 rows 8-9 |
| D §5 | ToolTrace safe serialization assertions | **resolved**: §6 row 10 |
| D §5 | explicit no-live validation commands | **resolved**: §4 E1-E5 validation commands |
| D §5 | residual owners enumeration | **not addressed**: no residual owner section (see F2) |

## 6. Validation

Plan formatting check:

```text
git diff --check -- docs/reviews/mvp-agent-engine-design-slice-e-implementation-planning-gate-plan-20260608.md
```

```text
git diff --check -- docs/reviews/mvp-agent-engine-design-slice-e-implementation-planning-gate-plan-20260608.md docs/reviews/mvp-agent-engine-design-slice-e-implementation-planning-gate-plan-review-ds-20260608.md
```

No source tests were run — this is a plan review only. No live provider, endpoint, network, PR, push, commit, source edit, test edit or control-doc edit actions were performed.

## 7. Recommended Controller Disposition

Controller should accept this plan as `PLAN_ACCEPTED_WITH_PRE_IMPLEMENTATION_FIXES` or `PLAN_ACCEPTED_IMPLEMENTATION_AUTHORIZED` with explicit conditions:

If accepting as `PLAN_ACCEPTED_IMPLEMENTATION_AUTHORIZED`:

1. Implementation worker must address F1 before completing E1: add explicit `blocked_tool_contract` disposition.
2. Implementation worker must address F2 before completing E5: add residual owners section or explicit statement that none exist.
3. Implementation worker should address F3 in E2 implementation evidence: state prompt char/token derivation rule.
4. Implementation worker should address F4 in E4 implementation evidence: record pre-migration Service test baseline.
5. Implementation worker must stop and return to controller if any slice cannot achieve equivalence, per §10.
6. No live provider, network, endpoint, PR, push, merge or external state actions are authorized by this review.

## 8. Implementation Authorization Scope

If controller accepts this plan with the conditions above, implementation is authorized ONLY for:

- Creating and populating `fund_agent/agent/` package per E1-E3 allowed files;
- Modifying `fund_agent/services/chapter_orchestrator.py` and `fund_agent/services/fund_analysis_service.py` per E4 requirements;
- Creating test files per E1-E4 allowed files;
- Updating documentation per E5 allowed files;
- Running local-only validation commands per E1-E5.

Implementation remains forbidden for all actions listed in §3 and the current startup packet prohibited actions (§7).
