# MVP Agent Engine Design Slice C Repair And Budget Contract Plan Review (DS)

## 1. Verdict

`PASS`

This plan artifact is accepted as design-only with zero blocking findings. All nine
assigned scope items are satisfied. No implementation, live provider, runtime
change, or forbidden action is authorized.

## 2. Scope Findings

### 2.1 Service provider runtime budget separate from Agent content repair budget — PASS

Plan Section 5.1 (line 88–106) keeps Service ownership of `ProviderRuntimeBudget`
(writer timeout, auditor timeout, repair timeout, timeout max attempts, timeout
backoff, max output chars, prompt payload mode, Host timeout scalar). Plan Section
5.2 (line 108–126) assigns Agent ownership of `max_repair_attempts`, attempt
index, remaining content repair budget, repair exhaustion terminal state, and
repair decision ledger.

The articulation rule at line 122–124 is precise: "one writer attempt plus one
audit pass is attempt index 0; a regenerate decision consumes one content repair
attempt; provider timeout retry attempts inside one provider request do not
consume Agent content repair budget."

Current code confirms separation: `ProviderRuntimeBudget` lives in
`execution_contract.py:133` (Service-owned); `max_repair_attempts` lives in
`ChapterOrchestrationPolicy` at `chapter_orchestrator.py:351`; provider timeout
retry is isolated in `_complete()` at `llm_provider.py:259–292`.

### 2.2 Provider timeout retry remains provider-client behavior only — PASS

Plan Section 5.1 (line 103–105): "Agent must observe only the final provider
result or provider runtime exception category, plus safe scalar diagnostics."

Current code: `_complete()` handles timeout retry internally;
`orchestrate_chapters()` receives only final result or exception via
`_provider_runtime_stop_reason()` at `chapter_orchestrator.py:1343`. Agent never
sees intermediate provider retry state.

### 2.3 Hidden retry explicitly defined and forbidden — PASS

Plan Section 5.3 (line 129–142) provides an explicit definition:

> `hidden_retry` means any Agent-initiated repeated writer, auditor, tool call or
> repair action that is not represented in the chapter attempt ledger, tool trace
> or repair decision ledger.

Rule `hidden_retry_allowed=false`. Three concrete corollaries:
- Every Agent-initiated repeated writer/auditor/tool action must have a new
  attempt ledger entry or explicit ToolTrace row.
- Provider client internal timeout attempts remain provider runtime diagnostics,
  not hidden Agent retries.
- Host re-entry/resume is future Host scope and must not silently duplicate an
  Agent content attempt.

This satisfies the Slice A DS NBO-5 follow-up requirement ("hidden_retry_allowed
semantics undefined").

### 2.4 Fund issue ids and repair hints remain Fund-owned semantics — PASS

Plan Section 6 (line 157): "Agent must not redefine Fund issue meaning. Fund
remains owner of issue ids, rule codes, `repair_hint`, repair messages and
required correction semantics."

Current code confirms: `ChapterAuditIssue.issue_id`, `.rule_code`, `.repair_hint`
are defined in `chapter_auditor.py` (Fund layer). Repair context is derived from
Fund-owned issue semantics via `_required_correction_from_issue()` at
`chapter_orchestrator.py:2389`. The plan decision mapping (lines 162–173) consumes
Fund-owned `ChapterAuditResult.status`, `.accepted`, `.repair_hint`,
`ChapterAuditIssue.issue_id`, `.rule_code`, `.repair_hint` — all Fund-layer types.

### 2.5 needs_more_facts does not source-probe — PASS

Plan Section 6 decision mapping (line 167): `aggregate repair_hint=needs_more_facts`
→ action `needs_more_facts`, stop reason `needs_more_facts`.

Plan Section 8: `blocked_needs_more_facts` means "same-source facts are
insufficient; no source probing in Agent" (line 207).

Plan Section 7 (line 194): ChapterRepairContext explicitly excludes "source
probing instructions."

Current code: `_decide_repair()` at `chapter_orchestrator.py:2280–2287` returns
`needs_more_facts` with reason "审计要求更多同源事实，Service 不进行 source
probing。"

### 2.6 Provider runtime failures do not trigger content repair — PASS

Plan Section 5.2 (line 125): "provider runtime failure does not trigger content
repair." Plan Section 6 decision mapping (line 172): provider runtime
timeout/rate-limit/malformed/network/http error → stop, mapped provider runtime
stop reason.

Current code: provider runtime exceptions are caught in the orchestration loop
and mapped to terminal stop reasons via `_provider_runtime_stop_reason()`. They
never enter the `_decide_repair()` content repair path.

### 2.7 Host interruption stays scheduling/lifecycle boundary — PASS

Plan Section 6 decision mapping (line 173): "Host cancel/deadline observed →
stop, host_interrupted."

Plan Section 8 (line 211): `host_interrupted` means "Host cancel/deadline
observed at scheduling boundary or after tool return."

Plan Section 5.3 (line 141–142): "Host re-entry/resume is future Host scope and
must not silently duplicate an Agent content attempt."

This satisfies the Slice B DS NBO-2 follow-up: cancel/deadline detection stays in
Host/Agent scheduling boundaries; tool adapters do not implement Host lifecycle
logic.

### 2.8 Diagnostics remain allowlist-only — PASS

Plan Section 9 (lines 223–243) specifies a strictly bounded diagnostic surface:
chapter id, attempt index, previous issue ids, aggregate repair hint, action,
remaining budget before/after, terminal stop reason, provider runtime category
when applicable, `DiagnosticConsistencyStatus` when applicable.

Prompt char/token counts: "derived from in-memory prompt length heuristics only.
They must not serialize prompt text, call external token-count services or read
retained prompts" (lines 238–239).

`request_id`: "optional scalar from an explicit response header allowlist only.
No arbitrary header map, provider URL, cookie, Authorization header or provider
config value may be serialized" (lines 241–243).

This satisfies the Slice B Codex NBO-1 follow-up for `request_id` safe projection
shape and the Slice B DS NBO-1 follow-up for prompt count derivation.

### 2.9 No implementation or live/provider scope is authorized — PASS

Plan Section 4 (lines 68–82) enumerates a comprehensive non-goal list covering:
no `fund_agent/agent` creation, no repair/budget/ToolRegistry/ToolTrace
implementation, no provider/runtime/default/budget/config change, no live
`--use-llm`/retry/probe, no dayu/LangGraph/MCP runtime, no quality
gate/golden/score-loop/multi-year/public chapter id change, no PR/push/merge.

All stop conditions (Section 12) and forbidden validations (Section 10) reinforce
this boundary.

## 3. Parent Slice B Follow-Up Assessment

| Parent requirement | Slice A/B source | Slice C status | Evidence |
|---|---|---|---|
| Hidden retry semantics | Slice A DS NBO-5 | **Resolved** | §5.3 defines `hidden_retry`, forbids it, and gives three concrete corollaries |
| Prompt char/token count derivation | Slice B DS NBO-1 | **Resolved** | §9 requires in-memory length heuristics only; forbids external token services |
| `host_interrupted` scheduling boundary | Slice B DS NBO-2 | **Resolved** | §6/§8 keep it at Host/Agent scheduling; tool adapters surface but don't implement |
| `request_id` scalar allowlist shape | Slice B Codex NBO-1 | **Resolved** | §9: optional scalar from explicit response-header allowlist only |
| Chapter-attributed blocked reasons | Slice A DS NBO-6 | **Deferred** | Still owned by implementation planning or later state-model gate |
| Equivalence testing scope | Parent NBO-2 | **Deferred** | Still owned by Slice D or implementation planning before code changes |

## 4. Adversarial Failure Pass

The following adversarial probes were applied and all passed:

| Probe | Result |
|---|---|
| Could Agent mutate `ProviderRuntimeBudget` fields? | No — §5.1: "must not construct providers, infer defaults, mutate budgets, perform endpoint probes or fallback to another runtime" |
| Could a provider timeout retry be counted as content repair? | No — §5.2 line 123–124 explicitly separates them |
| Could an Agent retry without a ledger entry? | No — §5.3: `hidden_retry_allowed=false`; every repeated action needs a ledger entry |
| Could `needs_more_facts` trigger a source fetch? | No — §6 line 167, §7 line 194, §8 line 207 all block source probing |
| Could provider runtime failure accidentally enter the repair loop? | No — §5.2 line 125 and §6 line 172 map it to terminal stop |
| Could a tool adapter implement Host cancel logic? | No — §6 line 173 and Slice B NBO-2 keep Host cancel at scheduling boundary |
| Could diagnostics leak prompts or headers? | No — §9 lines 238–243 are strictly allowlist-only |
| Does the plan authorize implementation? | No — §4 non-goals and §12 stop conditions forbid it |

## 5. Scope And Forbidden-Action Audit

Confirmed no authorization for:
- creating `fund_agent/agent`
- implementing repair policy, budget objects, ToolRegistry, ToolTrace, adapters, schemas
- changing `ProviderRuntimeBudget`, timeout defaults, retry behavior
- changing `ChapterOrchestrationPolicy.max_repair_attempts`
- changing Fund `ChapterAuditRepairHint` semantics
- source probing, repository/PDF access, retained artifact lookup
- provider/default/runtime/budget/config change
- live `--use-llm`, retry, curl, DNS, socket, endpoint probe
- `dayu-agent`, `dayu.host`, `dayu.engine`, LangGraph, MCP runtime
- quality gate, golden/readiness, score-loop, multi-year runtime, public chapter ids
- PR, push, merge, commit, source edit, test edit, control-doc edit

No forbidden files were modified. No live providers were accessed.

## 6. Validation Commands And Results

```text
$ git diff --check -- docs/reviews/mvp-agent-engine-design-slice-c-repair-and-budget-contract-plan-20260608.md
(exit 0, no output — no whitespace errors)

$ git branch --show-current
feat/mvp-llm-incomplete-run-artifacts

$ git status --short
(plan artifact is untracked, as expected; no source edits detected)
```

## 7. Non-Blocking Observations

### NBO-1: Terminal state name mapping not explicit

Plan Section 8 introduces future Agent terminal state names (`blocked_content`,
`blocked_needs_more_facts`, `blocked_provider_runtime`,
`blocked_repair_budget_exhausted`, `blocked_tool_contract`). Current code uses
`ChapterRunStopReason` literals (`auditor_failed`, `auditor_blocked`,
`repair_budget_exhausted`, `needs_more_facts`, etc.). The mapping from current to
future names is derivable from context but not stated explicitly. The
implementation planning gate should provide a mapping table.

Severity: informational. Does not block design-only acceptance.

### NBO-2: blocked_tool_contract may be premature

The `blocked_tool_contract` terminal state ("adapter/Fund tool invariant
conflict") at line 210 has no current-code analogue. The Slice B tool adapter
contract defines adapter error taxonomy but does not define tool invariant
conflict as a terminal category. This terminal state is plausible future-proofing
but the implementation gate should confirm a concrete trigger condition exists
before adding it to the state model.

Severity: informational. Does not block design-only acceptance.

### NBO-3: Section 10 validation is minimal

The plan's validation section (line 247–265) only requires `git diff --check`.
This is appropriate for a design-only plan, but the implementation planning gate
should add contract-level validation that the repair decision mapping exhaustively
covers all current `ChapterRunStopReason` values.

Severity: informational. Current validation is sufficient for design-only scope.

## 8. Residual Risks And Open Questions

1. The mapping from `patch` repair hint to whole-chapter regenerate (line 175)
   will eventually need a typed patch API gate. The decision to defer this is
   acceptable but adds implementation complexity to the eventual Agent migration.

2. Chapter-attributed blocked reasons (Slice A DS NBO-6) and equivalence testing
   (parent NBO-2) remain deferred. Neither blocks Slice C acceptance.

3. No residual risk of scope creep: the plan's non-goal list and stop conditions
   are comprehensive and enforceable.

## 9. Conclusion

The Slice C plan cleanly separates Service provider runtime budget from Agent
content repair budget, explicitly defines and forbids hidden retry, preserves Fund
ownership of issue semantics, keeps provider runtime failures out of content
repair, keeps Host interruption at the scheduling boundary, and enforces
allowlist-only diagnostics. It satisfies all four Slice B follow-up requirements.

Zero blocking findings. The artifact is ready for controller judgment.
