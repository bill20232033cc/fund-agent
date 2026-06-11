# Runtime Artifact Disposition / Ignore-rule Plan Controller Judgment

## Scope

- Gate: `Runtime artifact disposition / ignore-rule planning gate`
- Classification: `standard`
- Judgment type: plan controller judgment
- Plan: `docs/reviews/mvp-runtime-artifact-disposition-ignore-rule-plan-20260611.md`
- DS review: `docs/reviews/mvp-runtime-artifact-disposition-ignore-rule-plan-review-ds-20260611-145413.md`
- MiMo review: `docs/reviews/mvp-runtime-artifact-disposition-ignore-rule-plan-review-mimo-20260611-145413.md`
- Verdict: `ACCEPT_WITH_AMENDMENTS`

## Basis

- `AGENTS.md`: arbitrary untracked residue must not become proof, source truth, durable fixture or product scope without reviewed acceptance; delete/move/archive/cleanup requires explicit authorization.
- `docs/design.md`: production annual report access must go through `FundDocumentRepository`; local PDF corpus must not be used as production proof; `docs/design.md` remains design truth.
- `docs/current-startup-packet.md`: current active gate is planning; no cleanup, ignore-rule implementation, archive, delete, promotion or release-readiness status change is accepted yet.
- `docs/implementation-control.md`: active objective is planning runtime artifact disposition and ignore-rule handling without treating residue as evidence or changing release state.
- `docs/reviews/mvp-control-doc-compression-untracked-residue-disposition-20260611.md`: accepted prior residue disposition input, not a substitute for live current status.
- DS and MiMo both returned `ACCEPT` with non-blocking amendments.

## Controller Decision

The plan is accepted with amendments.

The accepted plan is code-generation-ready for a later implementation/disposition gate because it:

- Separates evidence-chain artifacts, research inputs, scratch/runtime outputs, user-owned unknowns, obsolete duplicates and scratch tooling residue.
- Leaves untracked residue unaccepted as proof unless exact path-level provenance is later reviewed and accepted.
- Treats `fund_agent/tools` exact source-like residue as closed by `11040bd` unless it reappears.
- Defers `.gitignore` edits to a reviewed implementation gate.
- Keeps deletion, move, archive, cleanup and ignore-rule implementation outside this planning gate.
- States release/readiness blockers without claiming release readiness.

## Accepted Amendments

The plan was patched after review to:

- Update `docs/reviews` count to 35 including the current plan artifact.
- Add explicit self-disposition for `docs/reviews/mvp-runtime-artifact-disposition-ignore-rule-plan-20260611.md`.
- Add a required promotion provenance step before any file can be promoted.
- Add a `Promotion provenance check` validation row.
- Unify `基金年报/` ignore-rule condition: it may be ignored only if classified as local runtime data that should never enter review as source; if it remains user-owned unknown or a possible durable fixture, leave it visible and untracked.

These amendments are clarifying and do not expand scope.

## Accepted Implementation Boundaries For Next Gate

The next implementation/disposition gate may only be entered after this accepted plan checkpoint and control sync. It still requires a reviewed implementation plan or handoff before any filesystem-changing action.

The accepted plan does not authorize:

- source/test/runtime behavior changes
- `.gitignore` edits yet
- delete, move, archive, cleanup, ignore, import, stage, promote, push, PR or release actions
- live provider/EID/PDF/FDR/network/analyze/checklist/golden/readiness commands
- treating residue as accepted proof without exact reviewed provenance

## Residuals

- The implementation gate must refresh live status because untracked counts can drift.
- If an implementation gate performs no tracked edits, `git diff --check` and `git diff --name-only` are still safe but may be informational rather than proving a write-set.
- External Codex skill/memory paths in the plan's command log are process context only, not repository truth inputs.
- Release/readiness cleanliness remains blocked until accepted disposition outcomes or explicit residual owners exist.

## Next Action

Create a local accepted plan checkpoint for the plan, reviews and controller judgment. Then synchronize `docs/current-startup-packet.md` and `docs/implementation-control.md` to record this plan checkpoint and set the next entry to the runtime artifact disposition / ignore-rule implementation gate under the accepted plan boundaries.
