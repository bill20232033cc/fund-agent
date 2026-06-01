# Plan Review: MVP internalized Host runtime governance adapter plan

Date: 2026-06-01
Reviewer: AgentMiMo (plan review worker)
Target plan: `docs/reviews/mvp-internalized-host-runtime-governance-adapter-plan-20260601.md`
Gate: `MVP internalized Host runtime governance adapter plan gate`

## Review Scope

1. Plan handoff-readiness / code-generation-readiness
2. Correct execution of new truth: Dayu is capability source, no direct dayu-agent/dayu.host/dayu.engine dependency
3. Local Host scope: not too broad (won't become Dayu runtime copy), not too narrow
4. Global deadline / cancel semantics: honest about inability to hard-kill synchronous provider HTTP
5. Host does not understand fund business; Service retains business semantics and ExecutionContract
6. Run state / terminal invariant / event-outbox / safe diagnostics / timeout classification: implementable and testable
7. Slices, allowed files, validation, stop conditions: sufficiently narrow

## Methodology

Cross-referenced target plan against:
- `AGENTS.md` (authoritative rules)
- `docs/design.md` (design truth)
- `docs/implementation-control.md` (control truth)
- Current `fund_agent/services/fund_analysis_service.py` (Service layer fact)
- Current `fund_agent/ui/cli.py` (CLI fact)
- Current `fund_agent/services/chapter_orchestrator.py` (orchestrator fact)
- Confirmed `fund_agent/host/` and `tests/host/` do not yet exist on disk

---

## Finding 1: HostRunContext couples to Service-layer LLM client type

**Severity**: risk (not blocking)

**Location**: Plan §Core Types → `FundLLMHostRunRequest`

**Detail**: `FundLLMHostRunRequest.llm_clients: ChapterOrchestratorLLMClients` directly imports a Service-layer type into the Host package. Per `AGENTS.md` module boundary rules, Host should not depend on Service internals. `ChapterOrchestratorLLMClients` is defined in `fund_agent/services/chapter_orchestrator.py`.

**Recommendation**: Either (a) move `ChapterOrchestratorLLMClients` to a shared types location (e.g., `fund_agent/host/contracts.py` or `fund_agent/types.py`) so both Service and Host can import it without circular dependency, or (b) have the Host request carry a more generic typed mapping that Service resolves before passing to orchestrator. The current plan does not address this import direction.

**Risk if unaddressed**: Implementation will either create a circular import (Host → Service → Host) or require ad-hoc restructuring mid-slice.

---

## Finding 2: Async boundary between CLI asyncio.run() and Host runner unspecified

**Severity**: risk (not blocking)

**Location**: Plan §Slice H2, §Slice H4

**Detail**: Current CLI uses `asyncio.run(FundAnalysisService().analyze_with_llm(...))`. The plan says H2 adds `HostRuntimeRunner.run_sync(...)`. If `run_sync` internally uses `asyncio.run()` or creates its own event loop, it will conflict with the existing `asyncio.run()` in CLI. The plan does not specify whether `run_sync` is truly synchronous (blocking) or wraps an async operation.

**Recommendation**: Specify that `HostRuntimeRunner.run_sync` accepts a callable (the Service async method) and manages the event loop internally, or that H4 changes CLI to call `HostRuntimeRunner.run_async(...)` with the existing `asyncio.run()`. This needs explicit design to avoid event-loop nesting errors.

---

## Finding 3: HostPhaseName includes "repair" but current orchestrator repair is mapped to regenerate

**Severity**: informational

**Location**: Plan §Core Types → `HostPhaseName`

**Detail**: `HostPhaseName` includes `repair` as a phase. In current `chapter_orchestrator.py`, `patch` is mapped to budget-limited whole-chapter `regenerate` — there is no distinct repair phase. The plan should clarify whether `repair` phase events will fire during the regenerate cycle or whether this phase name is reserved for future fine-grained repair.

**Recommendation**: Add a note that `repair` phase events in MVP map to the regenerate attempt boundary in current orchestrator. This avoids confusion during implementation.

---

## Finding 4: deadline_at and timeout_seconds coexist without precedence rule

**Severity**: informational

**Location**: Plan §Core Types → `HostRunContext`

**Detail**: `HostRunContext` carries both `deadline_at: datetime | None` and `timeout_seconds: int | None`. `FundLLMHostRunRequest` has `timeout_seconds: int`. The plan does not specify precedence: if both `deadline_at` and `timeout_seconds` are provided, which wins? Or are they always derived from each other?

**Recommendation**: State that `timeout_seconds` on the request is the source of truth; Host computes `deadline_at = now + timeout_seconds`. `deadline_at` on context is the computed result, not an alternative input. This prevents implementor confusion.

---

## Finding 5: Stop condition "Host needs to understand fund business semantics" needs concrete test

**Severity**: informational

**Location**: Plan §Stop Conditions

**Detail**: Stop condition 3 says "Host needs to understand fund business semantics." This is a good guardrail but is not accompanied by a concrete test or lint rule. During implementation, a subtle leak (e.g., Host importing `FundType` or `CHAPTER_CONTRACT`) could slip through.

**Recommendation**: Add to H1 or H5 validation: `rg -n "from fund_agent.fund" fund_agent/host/` should return zero matches. This makes the stop condition mechanically verifiable.

---

## Finding 6: Event ordering invariant not fully specified

**Severity**: informational

**Location**: Plan §Event / Outbox Boundary

**Detail**: The plan lists required event names but does not specify ordering constraints beyond "events are emitted in legal order" (H2 test). For example: must `run_started` always precede `phase_started`? Can `diagnostic_recorded` interleave between phase events? Can `run_failed` follow `run_completed`?

**Recommendation**: Add a brief ordering invariant: `run_started` → (`phase_started` → `phase_completed`)* → one terminal (`run_completed` | `run_failed` | `run_cancelled`). `diagnostic_recorded` may interleave at any point. This makes the H2 test "events are emitted in legal order" concretely testable.

---

## Positive Assessment

The following aspects are well-done and require no changes:

1. **Dayu truth execution**: Correctly treats Dayu as capability source only. Stop conditions explicitly check for dayu imports. No runtime dependency introduced.

2. **Host scope**: Appropriately small — run lifecycle, deadline, cancel, terminal state, safe diagnostics, run-local events. Does not implement Agent runner, tool loop, or context budget. Does not become a Dayu runtime clone.

3. **Deadline honesty**: The "Important Runtime Constraint" section is admirably honest about inability to force-kill synchronous provider HTTP. Classification into `run_deadline_exceeded` / `phase_timeout` / `provider_runtime_timeout` is correct and implementable.

4. **Service/Host boundary**: Service retains business semantics (prompt/ExecutionContract, provider clients, chapter policy). Host only manages lifecycle. `HostRunContext` flows into Service as an opaque context — Host does not inspect fund code, report year, CHAPTER_CONTRACT, anchors, or prompt content.

5. **Safe diagnostics contract**: Explicit allowlist and forbidlist. Forbidden items cover the realistic leak vectors (API key, Authorization header, full prompt, full draft, raw provider response, unbounded exception strings).

6. **Event/outbox scope**: Correctly scoped as in-memory run-local tuple, not durable infrastructure. Future durable outbox properly deferred.

7. **Slice structure**: H1-H5 are well-ordered with incremental dependencies. Each slice has narrow allowed files, explicit allowed changes, concrete tests, and mechanical stop conditions. H3 correctly limits Service changes to adding optional `host_context` / `cancellation_token` / `deadline_at` parameters without broad refactor.

8. **Validation matrix (H5)**: Comprehensive — ruff, pytest with coverage, deterministic smoke unchanged, missing-config fail-closed, real provider smoke (accepting timeout blocker), cancellation/deadline tests, secret leak scan, and `rg` dayu import check.

9. **Non-goals**: Correctly excludes Agent runner, tool loop, ToolRegistry, ToolTrace, context budget, score-loop, provider parameter tuning, deterministic fallback, and score/golden/fixture promotion.

---

## Conclusion

**pass-with-risks**

The plan is handoff-ready and code-generation-ready. It correctly internalizes Dayu Host capabilities without importing Dayu runtime, maintains honest deadline semantics, preserves the Service/Host boundary, and provides sufficiently narrow slices with mechanical stop conditions.

Six findings identified, none blocking:
- **Finding 1** (risk): `ChapterOrchestratorLLMClients` import direction needs resolution before H4 implementation to avoid circular imports.
- **Finding 2** (risk): Async event-loop interaction between CLI `asyncio.run()` and `HostRuntimeRunner.run_sync` needs explicit design in H2/H4.
- **Findings 3-6** (informational): Minor clarifications on phase mapping, deadline precedence, stop condition testability, and event ordering invariants.

Findings 1 and 2 should be resolved during H2 implementation (before H4 wires CLI). Findings 3-6 are advisory and can be resolved inline during implementation.

No blocking findings. Plan may proceed to implementation gate.
