# MVP internalized Agent engine implementation planning gate — controller judgment

## Controller Self-Check

- Role: controller judgment only; not planning worker, implementation worker, review worker or release operator.
- Gate: `MVP internalized Agent engine implementation planning gate`.
- Classification: `heavy`.
- Branch baseline: `feat/mvp-llm-incomplete-run-artifacts`.
- Scope: accept or reject the plan artifact and its review/fix/re-review loop only.
- Allowed checkpoint files: this controller judgment plus the six planning/review artifacts named below.
- Prohibited actions preserved: no source code, tests, README, `docs/design.md`, `docs/implementation-control.md`, `docs/current-startup-packet.md`, provider command, live probe, score-loop, multi-year runtime, Agent implementation, push, PR or release action.

## Verdict

`PLAN_ACCEPTED`.

The plan is accepted as a code-generation-ready future implementation plan for the first internalized Agent engine MVP, with the implementation-time requirements and stop conditions below.

This judgment does not authorize Agent runtime implementation in the current repository state. Current control truth still routes the same-run non-timeout provider residual to `operator_deferred_no_repo_action`. Any later implementation must be opened by a separate controller-authorized gate.

## Accepted Artifacts

| Purpose | Artifact |
|---|---|
| Plan | `docs/reviews/mvp-internalized-agent-engine-implementation-planning-plan-20260603.md` |
| DS plan review | `docs/reviews/mvp-internalized-agent-engine-implementation-planning-plan-review-ds-20260603.md` |
| MiMo plan review | `docs/reviews/mvp-internalized-agent-engine-implementation-planning-plan-review-mimo-20260603.md` |
| Plan fix evidence | `docs/reviews/mvp-internalized-agent-engine-implementation-planning-plan-fix-evidence-20260603.md` |
| DS re-review | `docs/reviews/mvp-internalized-agent-engine-implementation-planning-plan-rereview-ds-20260603.md` |
| MiMo re-review | `docs/reviews/mvp-internalized-agent-engine-implementation-planning-plan-rereview-mimo-20260603.md` |

## Finding Decisions

| Finding | Controller decision | Required owner |
|---|---|---|
| DS B1 `RepairSemantics` contract shape | Accepted fixed. The amended plan now defines Fund-owned typed input/output, issue semantics, action enum, precedence, module placement and Agent consumption subset. | Future Slice 3 implementation must implement from this contract and avoid Agent-side audit-rule interpretation. |
| DS B2 `AgentRunControl` Protocol | Accepted fixed. The amended plan now defines exact Protocol methods and Service adapter location while excluding Host internals. | Future Slice 1 / Slice 5 implementation must prove Agent imports no concrete Host runtime. |
| DS B3 `AgentRunResult` to Service mapping | Accepted fixed. The amended plan now contains the required mapping table and fail-closed invariants. | Future Slice 5 / Slice 7 implementation must preserve `ChapterOrchestrationResult`, artifacts, empty stdout and exit `1` semantics. |
| MiMo F1/F2 adapter and diagnostics mapping | Accepted addressed by DS B3 fix plus ToolTrace safe-superset requirement. | Future Slice 5 / Slice 7 implementation tests. |
| MiMo re-review F1 `record_diagnostic(**diagnostics)` runtime safety | Accepted as non-blocking implementation requirement. | Add allowlist-key assertion/test when the adapter is implemented. |
| MiMo re-review F2 `RepairSemantics` migration-source verification | Accepted as non-blocking implementation requirement. | Prove migrated correction mapping matches current Service helper behavior before deleting or bypassing old logic. |
| DS residual failure-category mapping fuzziness | Accepted residual. | If an Agent failure mode has no current Service enum, record it as additive diagnostics or stop for a separate enum/schema gate. |

## Implementation-Time Stop Conditions

A future implementation worker must stop and return to controller if any of these occur:

- Implementation requires provider/default/runtime/budget, endpoint, model, fallback, live probe or PASS-only timing changes.
- Implementation requires `dayu-agent`, `dayu.host` or `dayu.engine` as a production runtime dependency.
- Agent needs to import concrete Host, Service, provider clients or business parameters through `extra_payload` / free-form bags.
- Provider clients would need to become ToolRegistry tools, or `EvidenceAvailability` would need to become a tool rather than a precomputed input.
- Programmatic audit would be relaxed, bypassed or overridden by bounded semantic audit.
- Service final product fail-closed mapping, empty stdout on incomplete, exit code `1`, artifact safety, deterministic fallback prohibition, public chapter ids `0-7`, quality gate, golden/readiness or score semantics would change.
- Slice 5 cannot map an Agent result into the existing Service result shape without changing public or artifact semantics.
- Any unsafe field appears in ToolTrace or diagnostics: prompt, draft, repair draft, raw provider response, raw audit response, API key, Authorization header, cookies, hidden provider config or raw PDF/source text.

## Accepted Next Entry

The accepted planning checkpoint may be recorded locally by staging only the seven planning-gate artifacts:

```text
docs/reviews/mvp-internalized-agent-engine-implementation-planning-plan-20260603.md
docs/reviews/mvp-internalized-agent-engine-implementation-planning-plan-review-ds-20260603.md
docs/reviews/mvp-internalized-agent-engine-implementation-planning-plan-review-mimo-20260603.md
docs/reviews/mvp-internalized-agent-engine-implementation-planning-plan-fix-evidence-20260603.md
docs/reviews/mvp-internalized-agent-engine-implementation-planning-plan-rereview-ds-20260603.md
docs/reviews/mvp-internalized-agent-engine-implementation-planning-plan-rereview-mimo-20260603.md
docs/reviews/mvp-internalized-agent-engine-implementation-planning-plan-controller-judgment-20260605.md
```

Do not stage unrelated dirty files such as `pyproject.toml`, `fund_agent/tools/`, `scripts/claude_mimo_simple.py`, unrelated review artifacts, manual reports or raw scratch outputs.

After checkpoint, repository work remains paused on the current provider residual unless the user opens a new controller-authorized gate.

## Validation

Read and compared:

- `AGENTS.md`
- `docs/current-startup-packet.md`
- `docs/implementation-control.md`
- Plan, DS review, MiMo review, fix evidence, DS re-review and MiMo re-review artifacts listed above.

Checks run:

```bash
git branch --show-current
git status --short
rg -n "^## Verdict|PASS|BLOCK|B1|B2|B3|F1|F2|Status:|Verdict" docs/reviews/mvp-internalized-agent-engine-implementation-planning-plan-*.md
git status --short -- docs/reviews/mvp-internalized-agent-engine-implementation-planning-plan-20260603.md docs/reviews/mvp-internalized-agent-engine-implementation-planning-plan-fix-evidence-20260603.md docs/reviews/mvp-internalized-agent-engine-implementation-planning-plan-review-ds-20260603.md docs/reviews/mvp-internalized-agent-engine-implementation-planning-plan-review-mimo-20260603.md docs/reviews/mvp-internalized-agent-engine-implementation-planning-plan-rereview-ds-20260603.md docs/reviews/mvp-internalized-agent-engine-implementation-planning-plan-rereview-mimo-20260603.md
```

No runtime/provider/live probe command was run.

## Secret-Safety Statement

This controller judgment contains no API key, Authorization header, Bearer token, cookie, password, raw provider response, raw audit response, prompt body, writer draft body, repair draft body, hidden provider config value or raw PDF/source text.
