# Small Golden Set / Extractor Correctness Plan Review A

Reviewer: independent sub-agent A

Scope: `docs/reviews/mvp-small-golden-set-extractor-correctness-planning-gate-plan-20260608.md`

Mode: read-only plan review. The reviewer reported no file edits, no stage, no commit, and no live/network/provider command.

## Blocking Findings

### A1. Fallback wording was not closed enough

Status: accepted and fixed in plan revision.

Finding:

The plan prohibited fallback in the gate constraints, but the source identity section and field matrix used wording such as "when fallback is involved" and "fallback eligibility / fallback used". That could let the next implementation gate interpret the plan as permission to invoke repository fallback.

Required fix:

- State that this planning gate and the immediate extractor correctness gate must not invoke fallback.
- Permit only historical offline provenance metadata if it already exists.
- Require `fallback_used=false` otherwise.
- If source identity would require fallback execution, mark the row unavailable or route through controller replacement decision.
- Add no-fallback-invocation evidence to the source identity acceptance item.

## Non-Blocking Observations

- The five-fund selection covers active, index, enhanced index, bond and QDII pressure points.
- Field coverage satisfies the required source document, report year, fund type, benchmark, manager, scale, fee, return, holdings and risk dimensions.
- Offline fixture strategy is executable as manifest plus minimal local fixture excerpts or synthetic parser fixtures if source retention is constrained.
- The plan clearly separates this gate from full golden/readiness promotion.
- The extractor correctness acceptance matrix is concrete enough for the next gate.

## Questions

No blocking questions.

## Verdict

Original verdict: not passed because of A1.

Re-review required after fallback wording fix.
