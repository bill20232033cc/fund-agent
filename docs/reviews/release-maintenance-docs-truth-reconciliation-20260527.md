# Docs Truth Reconciliation

> Controller: Codex  
> Date: 2026-05-27  
> Gate: `docs-only truth reconciliation`  
> Trigger evidence: `docs/reviews/repo-review-20260527-065237.md` F1/F2/F3  
> Scope: docs-only; no production code, renderer, quality gate, final judgment, Host/Agent/dayu, baseline, golden, or GitHub mutation

## Startup Packet Replay

| Item | State |
|---|---|
| Current phase | `release maintenance` |
| Current gate before steering | `source provenance post-implementation bounded evidence rerun accepted locally` |
| Next entry point before steering | `post-provenance coverage recovery decision plan/review gate` |
| This gate | `docs-only truth reconciliation` |
| Latest accepted checkpoint before this gate | `f6a4d62 docs: accept provenance rerun evidence` |

This gate is a steering insertion before resuming post-provenance coverage recovery. It fixes current truth-source contradictions identified by repository review F1/F2 and records F3 as a deferred source-provenance hardening residual.

## Finding Judgments

| Finding | Judgment | Handling |
|---|---|---|
| F1: `docs/design.md` still described the already implemented active-fund Chapter 3 renderer minimal integration as future / not authorized | accepted | Closed by rewriting the Chapter Contract section to state current implemented scoped behavior: active-fund Chapter 3 missing-reviewed-evidence text-only path is implemented; positive reviewed-evidence branch remains future input-contract design. |
| F2: `docs/design.md` described quality gate block/not_run inconsistently for final judgment, including a stale block-to-`suggest_replace` trigger | accepted | Closed by aligning §8.2 with §4.8: quality gate `block/not_run` means data quality is insufficient and derives `needs_attention`; it does not independently trigger `suggest_replace`. |
| F3: `fallback_used` string boolean deserialization may coerce `"false"` to `True` | deferred | This is a code hardening issue, and this gate forbids production code changes. It is registered as a source provenance hardening residual for a later plan/review/implementation gate. |

## Design Truth Updates

| File | Section | Change |
|---|---|---|
| `docs/design.md` | Chapter contract / renderer minimal integration paragraph | Changed from "accepted future design / does not authorize current implementation" to "current implemented scoped behavior"; retained positive reviewed-evidence branch as future input-contract design. |
| `docs/design.md` | §8.2 Final judgment derivation | Removed stale "quality gate block triggers `suggest_replace`" wording; clarified that quality gate `block/not_run` derives `needs_attention`, while `suggest_replace` requires product/user-risk evidence such as veto item, checklist red light, or base `minus_20` pressure scenario beyond tolerance. |

## Non-Goals Observed

- No production code changes.
- No renderer changes.
- No quality gate changes.
- No `final_judgment.py` changes.
- No Host/Agent package creation.
- No `dayu.host` / `dayu.engine` integration.
- No F3 implementation.
- No baseline or golden promotion.

## Validation

- `uv run ruff check .`: passed (`All checks passed!`)
- `uv run pytest -q`: passed (`789 passed in 2.18s`)
- `git diff --check`: passed

## Next Entry Point

After this docs-only gate is accepted, resume `post-provenance coverage recovery decision plan/review gate`.

The previously generated post-provenance coverage recovery plan/review artifacts remain unaccepted until controller judgment explicitly accepts them in that gate.
