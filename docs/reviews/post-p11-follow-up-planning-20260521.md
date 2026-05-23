# Post-P11 Follow-up Planning（2026-05-21）

## Controller Decision

Verdict: `ACCEPTED`

Next gate: `P11-S2 historical summary dedupe plan/review`

P11-S1 has achieved the primary recovery goal: the control document now exposes the current gate, next entry point, active ledger, phase index, evidence preservation rules, and archive anchors in the first screen while preserving historical evidence in the same file.

## Evidence Reviewed

- Design truth: `docs/design.md`
- Control truth: `docs/implementation-control.md`
- P11-S1 plan: `docs/reviews/p11-s1-control-doc-hygiene-recovery-plan-20260521.md`
- P11-S1 implementation artifact: `docs/reviews/p11-s1-implementation-20260521.md`
- P11-S1 controller judgment: `docs/reviews/p11-s1-code-review-controller-judgment-20260521.md`
- Accepted commit: `5f5331b`

## Residuals

| Residual | Decision | Reason |
|---|---|---|
| RR-13 duplicate `016492` | defer to human owner | This is a source-data identity conflict and must not be auto-edited by controller or code. |
| `docs/repo-audit-20260521.md` | keep excluded | It is an audit input/local draft, not an accepted project artifact. |
| Historical duplicate summary rows | address next | They are INFO-level archive noise, but still degrade resume clarity and can be cleaned without touching product behavior. |
| Future product feature selection | defer | Control recovery should be completed before opening new product surface. |

## Scope for P11-S2

P11-S2 should be a documentation-only cleanup of historical control-doc summary rows. It should update stale archive summary rows that now contradict accepted P10/P11 facts, remove duplicate old planning rows, and preserve all historical artifact paths, commits, PR references, validation results, and residual owners.

Non-goals:

- No source, tests, config, runtime, product behavior, prompt scene, Dayu Host/Engine/tool loop, or LLM-writing changes.
- No edits to `docs/design.md` unless a real design contradiction is found.
- No publication of `docs/repo-audit-20260521.md`.
- No automatic RR-13 source-data fix.

## Acceptance Signals for P11-S2 Plan

- The plan identifies the exact stale/duplicate historical rows to edit.
- The plan distinguishes summarizing stale archive prose from deleting evidence.
- The plan requires artifact reference preservation and a reference-existence check after edits.
- The plan keeps the active Startup Packet and Active Gate Ledger as the current truth.
- The plan assigns any remaining ambiguity to explicit residual owners.
