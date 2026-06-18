# MVP Agent Engine Design Slice A Dataclass Design Plan Controller Judgment

## 1. Verdict

`PLAN_ACCEPTED_DESIGN_ONLY_WITH_FOLLOWUP_REQUIREMENTS`

Accepted plan:

- `docs/reviews/mvp-agent-engine-design-slice-a-dataclass-design-plan-20260608.md`

Accepted reviews:

- `docs/reviews/mvp-agent-engine-design-slice-a-dataclass-design-plan-review-ds-20260608.md`
- `docs/reviews/mvp-agent-engine-design-slice-a-dataclass-design-plan-review-codex-20260608.md`

Reviewer route:

- AgentMiMo remained unavailable for this gate.
- AgentDS provided the first independent review.
- AgentCodex was used as the operator-authorized Codex reviewer capacity in MiMo's absence.

Both reviews returned `PASS_WITH_NON_BLOCKING_OBSERVATIONS`.

## 2. Boundary Judgment

This judgment accepts Slice A as design-only planning input.

This judgment does not authorize:

- Agent runtime implementation;
- `fund_agent/agent` package creation;
- dataclass/source/test implementation;
- ToolRegistry, ToolTrace or Tool adapter code;
- migration of current Service `ChapterOrchestrator`;
- provider/default/runtime/budget/config change;
- live `--use-llm`, retry, endpoint probe, curl, DNS, socket probe or provider readiness check;
- LangGraph or MCP runtime;
- `dayu-agent`, `dayu.host` or `dayu.engine` production dependency;
- copying or rewriting upstream Dayu code;
- quality gate, golden/readiness, score-loop, multi-year runtime or public chapter ids `0-7` change;
- PR, push, merge, mark-ready, reviewer request or external comment.

## 3. Accepted Slice A Design Facts

- Future `AgentReportRun` is an Agent-owned execution record for one explicit LLM report run. It may later subsume Service `ChapterOrchestrator` execution mechanics, but it does not replace Service use-case ownership, provider construction, runtime ceilings, quality policy or final product fail-closed mapping.
- `EvidenceAvailability` invocation point is accepted for Slice A: derive exactly once after `ChapterFactProjection` exists and before the first `ChapterTask` enters `prepared`; store the value on `AgentReportRun`; pass the same value to all tasks and all repair attempts; no recomputation from retained artifacts, filesystem or external state.
- Future `ChapterTask` preserves current `ChapterRunResult` status, stop reason, accepted draft/conclusion, issue, failure category/subcategory and diagnostics semantics.
- Future `ChapterAttempt` maps one-to-one from current `ChapterAttemptRecord`.
- Future `AgentRepairPolicy` consumes Fund-owned issue ids and repair hints, preserves bounded repair attempts and must not redefine Fund issue meaning.
- Future `ToolCallRequest`, `ToolCallResult` and `ToolTrace` are safe Agent-to-Fund tool evidence envelopes; serialized trace surfaces must not include prompt, draft, raw provider response, raw audit response, API key, Authorization header, bearer token, model value or base URL value.
- Future Agent `FinalAssemblyReadiness` is accepted only as a body-readiness handoff into current Service final assembly. It does not replace current Service `FinalChapterAssembler`, stdout/stderr behavior, quality policy or final product fail-closed authority.

## 4. Review Finding Disposition

### DS NBO-4: `derive_evidence_availability` omitted from ToolTrace candidate phases

Disposition: `accepted_design_refinement`

Slice A intentionally refines parent tool-candidate wording: `EvidenceAvailability` is a run-level same-source precomputation rather than a per-task ToolRegistry call. Slice B must preserve this decision unless a later controller judgment explicitly reopens the tool boundary.

### DS NBO-5: `hidden_retry_allowed` semantics undefined

Disposition: `accepted_followup_requirement`

Slice C or the later implementation planning gate must define `hidden_retry` explicitly or remove the field from the implementation contract. Current accepted invariant remains: Agent repair attempts are explicit and bounded; provider timeout retry remains Service/provider-client runtime behavior; hidden Agent retries are not allowed.

### DS NBO-6: `AgentReportRun.blocked_reasons` underspecified

Disposition: `accepted_followup_requirement`

The later implementation planning gate must specify whether `blocked_reasons` is flattened or chapter-attributed. The accepted minimum is that chapter id, stop reason and failure category remain reconstructable without storing unsafe provider payloads.

### DS NBO-7: `diagnostic_consistency_status` wording vague

Disposition: `accepted_followup_requirement`

Slice B or the later implementation planning gate must pin `diagnostic_consistency_status` to the current `DiagnosticConsistencyStatus` literal set or a named explicit future equivalent.

### Codex NBO-1: Runtime diagnostics safe projection must be explicit

Disposition: `accepted_followup_requirement`

Slice B, Slice D or the implementation planning gate must define an Agent serialized diagnostics allowlist. It must not reuse current runtime diagnostic dataclasses wholesale if they contain unsafe fields such as model value. Minimum accepted rule: Agent serialized state and ToolTrace may retain only safe scalar categories, ids, counts, timing, char/token counts and diagnostic consistency values; they must exclude prompt, draft, raw provider response, raw audit response, API key, Authorization header, bearer token, model value and base URL value.

## 5. Parent NBO Status

| Parent finding | Slice A status | Judgment |
|---|---|---|
| NBO-1 EvidenceAvailability invocation point unresolved | resolved | accepted: derive once at run level before first task preparation and reuse across attempts |
| NBO-2 equivalence test scope underspecified | deferred | still owned by Slice D or implementation planning before code changes |
| NBO-3 FinalAssemblyReadiness handoff boundary | resolved | accepted: Agent readiness feeds Service final assembly, does not replace Service authority |

## 6. Validation Accepted

Controller validation:

```text
git diff --check -- docs/reviews/mvp-agent-engine-design-slice-a-dataclass-design-plan-20260608.md
```

Result: pass.

DS reviewer validation:

```text
git diff --check -- docs/reviews/mvp-agent-engine-design-slice-a-dataclass-design-plan-20260608.md
git diff --check -- docs/reviews/mvp-agent-engine-design-slice-a-dataclass-design-plan-20260608.md docs/reviews/mvp-agent-engine-design-slice-a-dataclass-design-plan-review-ds-20260608.md
```

Result: pass.

Codex reviewer validation:

```text
git branch --show-current
git status --short
git diff --check -- docs/reviews/mvp-agent-engine-design-slice-a-dataclass-design-plan-20260608.md
git diff --check -- docs/reviews/mvp-agent-engine-design-slice-a-dataclass-design-plan-20260608.md docs/reviews/mvp-agent-engine-design-slice-a-dataclass-design-plan-review-codex-20260608.md
```

Result: pass.

No reviewer ran live provider, endpoint, network, PR, push, commit, source edit, test edit or control-doc edit actions.

## 7. Next Entry Point

Next authorized local entry is design-only:

- `MVP Agent Engine Design Slice B Tool Adapter Contract Plan`

Slice B must consume the follow-up requirements in Section 4. It remains design-only unless a later implementation plan receives review and controller judgment.

Still not authorized:

- Agent runtime implementation;
- live evidence;
- provider/runtime/default changes;
- score-loop, multi-year runtime, golden/readiness or quality gate changes;
- external PR/push/release actions.
