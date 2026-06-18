# MVP internalized Agent engine and typed audit contract design controller judgment

## Controller Decision

- Gate: `MVP internalized Agent engine and typed audit contract design gate`
- Classification: `heavy`
- Decision: `accepted as design-only future architecture`
- Design artifact: `docs/reviews/mvp-internalized-agent-engine-typed-audit-contract-design-20260602.md`
- Review artifact: `docs/reviews/mvp-internalized-agent-engine-typed-audit-contract-design-review-20260602.md`
- Fix evidence: `docs/reviews/mvp-internalized-agent-engine-typed-audit-contract-design-review-fix-evidence-20260602.md`
- Re-review artifact: `docs/reviews/mvp-internalized-agent-engine-typed-audit-contract-design-rereview-20260602.md`

The design is accepted as a future architecture direction, not as current implementation fact. It does not authorize code changes, prompt fixes, provider runtime budget changes, score-loop wiring, deterministic fallback, stdout half-report behavior, or any relaxation of fail-closed semantics.

## Accepted Architecture Judgment

1. Service should keep use-case orchestration, scene/prompt/ExecutionContract semantics, quality policy, report strategy, and first-MVP provider construction/runtime ceilings.
2. Agent should own the future chapter execution runner, write-audit-repair task loop, retry attempt bookkeeping, Agent-side budget accounting, ToolRegistry/typed tool calls, ToolTrace, and final assembly readiness reporting.
3. Fund audit should be programmatic-first for mechanically checkable CHAPTER_CONTRACT, ITEM_RULE, evidence-anchor, marker, forbidden coverage, missing-fact downgrade, implemented L1 identity, and runtime/content failure separation rules.
4. The LLM auditor should be bounded to semantic audit: contradiction, unsupported interpretation, narrative coherence and meaning-level concerns. It must not override programmatic blockers or provider runtime failures.
5. Ch2/Ch6 timeout evidence shows a runtime-governance/provider-budget blocker that should not be patched through Service prompt churn. Ch3 `must_not_cover` evidence shows a contract-shape/programmatic audit calibration blocker caused by unsafe coverage around `言行一致`, not by auditor looseness.
6. Dayu Engine capabilities to internalize are runner, tool loop, ToolRegistry, ToolTrace, context budget, tool execution contract, cancellation/deadline observation, and event semantics. The project must not depend directly on `dayu-agent` / `dayu.engine`; copying or rewriting upstream code would require a separate license/compliance gate.

## Review Finding Disposition

| Finding | Controller decision | Re-review result |
|---|---|---|
| Agent runner vs provider client ownership ambiguous | Accepted and fixed by MVP boundary handoff: first Agent-engine MVP keeps provider construction Service-owned while Agent owns execution mechanics and trace | `fixed` |
| Typed audit contract was too conceptual | Accepted and fixed by MVP schema, enum domains, current-type mapping, programmatic-first boundary and explicit deferrals | `fixed` |
| Ch3-only calibration risked being bundled into Agent-engine slices | Accepted and fixed by removing Ch3 calibration from Agent-engine slices and keeping it as a separate controller gate | `fixed` |

## Boundary Notes

- Current production path remains `CLI -> Service prepares FundLLMExecutionRequest / ExecutionContract -> Host runner -> Service -> fund_agent/fund -> provider HTTP call`.
- Current Gate 3 `chapter_orchestrator` remains Service-owned code fact until a separate implementation gate migrates write-audit-repair mechanics into Agent.
- Future Agent MVP planning may use this accepted design, but must still produce an implementation plan, file ownership, tests, validation matrix, and review loop before code changes.
- Ch3-only must-not-cover calibration remains separate from this Agent-engine design gate.
- Ch2/Ch6 provider timeout remains separate provider runtime budget calibration scope.

## Secret Safety

This judgment contains no API key, Authorization header, Bearer token, raw provider response, prompt body, writer draft, repair draft, or raw audit response. It references only safe artifact paths and safe diagnostic labels.

## Controller Self-check

- Role: controller judgment only; design/review/fix/re-review artifacts were produced by delegated agents or scoped fix work.
- Source of truth: `AGENTS.md`, retained Slice 1 evidence, design artifact, review artifact, fix evidence and re-review artifact.
- Scope boundary: docs-only design gate; no runtime code, prompt, provider budget, score-loop, fail-closed, stdout or auditor strictness changes.
- Stop conditions: no blocking review findings remain; re-review status is `pass`.
- Next action: sync `docs/design.md`, `docs/implementation-control.md` and `docs/current-startup-packet.md` minimally as accepted future design, not current implementation fact.
