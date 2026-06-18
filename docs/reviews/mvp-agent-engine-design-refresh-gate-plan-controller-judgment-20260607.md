# MVP Agent Engine Design Refresh Gate Plan Controller Judgment

## 1. Verdict

`PLAN_ACCEPTED_DESIGN_ONLY_DS_REVIEW`

The `Agent Engine Design Refresh Gate` plan is accepted as design/plan input only.

Accepted plan:

- `docs/reviews/mvp-agent-engine-design-refresh-gate-plan-20260607.md`

Accepted review:

- `docs/reviews/mvp-agent-engine-design-refresh-gate-plan-review-ds-20260607.md`

Reviewer route:

- DS-only review was authorized by operator instruction because AgentMiMo had network/API failure and should not be used tonight.

## 2. Boundary Judgment

This judgment does not authorize implementation.

Not authorized:

- Agent runtime implementation;
- `fund_agent/agent` package creation;
- ToolRegistry / ToolTrace code;
- migration of current Service `ChapterOrchestrator`;
- provider/default/runtime/budget/config change;
- live LLM command, retry, endpoint probe, curl, DNS or socket probe;
- LangGraph or MCP runtime;
- `dayu-agent`, `dayu.host` or `dayu.engine` production dependency;
- copying or rewriting upstream Dayu code;
- quality gate, golden/readiness, score-loop, multi-year runtime or public chapter ids `0-7` change;
- PR, push, merge, mark ready, reviewer request or external comment.

## 3. Accepted Plan Facts

- The next Agent design must keep Service/Host/Agent/Fund ownership explicit.
- Service retains use case, ExecutionContract, provider construction, provider runtime ceilings, quality policy and final product fail-closed mapping.
- Host remains lifecycle-only and business-opaque.
- Future Agent owns execution mechanics only after a separate implementation gate: task graph, attempt ledger, repair policy execution, ToolRegistry calls, ToolTrace and final body readiness matrix.
- Fund remains the domain owner for CHAPTER_CONTRACT, preferred_lens, ITEM_RULE, same-source `EvidenceAvailability`, writer/auditor contracts, programmatic-first audit, bounded semantic audit adapter, issue ids and repair hints.
- First ToolRegistry design must wrap existing Fund primitives and must not rewrite Fund logic.
- Provider writer/auditor clients remain Service-constructed typed per-run inputs and are not registry tools.
- Fail-closed invariants remain mandatory before any implementation planning.

## 4. DS Review Finding Disposition

### NBO-1: EvidenceAvailability Invocation Point Unresolved

Disposition: `accepted_followup_requirement`

Slice A/B design must specify whether Agent invokes `derive_evidence_availability()` once at `ChapterTaskPrepared` or at another bounded lifecycle point. It must remain same-source, must not read retained artifacts/filesystem/external state, and must not be recomputed in a way that lets repair attempts drift from the original fact projection.

### NBO-2: Equivalence Test Scope Underspecified

Disposition: `accepted_followup_requirement`

Slice D or the later implementation planning gate must define equivalence criteria before code changes. Minimum expectation: same accepted/partial/fail-closed chapter outcome matrix, same terminal failure categories, preserved repair budget semantics and no weaker final assembly readiness. Byte-for-byte internal state equivalence is not required unless the later plan explicitly justifies it.

### NBO-3: FinalAssemblyReadiness Handoff Boundary

Disposition: `accepted_followup_requirement`

Future design slices must state whether Agent `FinalAssemblyReadiness` feeds or replaces current Service final assembly readiness. Until a later implementation gate accepts a change, Service final product fail-closed mapping and stdout semantics remain unchanged.

## 5. Validation Accepted

Controller validation:

```text
git diff --check -- docs/reviews/mvp-agent-engine-design-refresh-gate-plan-20260607.md docs/reviews/mvp-llm-tool-calling-state-machine-calibration-spike-controller-judgment-20260607.md
```

Result: pass.

Reviewer validation:

- DS read required truth docs and the accepted spike chain.
- DS performed read-only review.
- DS ran no live command, provider probe, endpoint check, runtime/default change, code implementation, PR, push or external action.

## 6. Next Entry Point

Next gate remains design-only unless the operator explicitly authorizes implementation planning:

1. Optional next design artifact: `MVP Agent Engine Design Slice A Dataclass Design Plan`.
2. Or pause here with accepted Agent Engine Design Refresh plan and wait for morning controller selection.

Do not enter implementation until a separate implementation plan has review and controller judgment.
