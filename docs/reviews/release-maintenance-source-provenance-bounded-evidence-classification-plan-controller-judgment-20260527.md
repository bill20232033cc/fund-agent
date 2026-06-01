# Controller Judgment: source provenance bounded evidence classification plan

> Controller: Codex
> Date: 2026-05-27
> Gate: `post-implementation source provenance bounded evidence classification gate`
> Latest accepted checkpoint before gate: `a0de731 feat: expose source provenance in snapshots`

## Startup Packet Replay

| Item | State |
|---|---|
| Current phase | `release maintenance` |
| Current gate entering this judgment | `source provenance public-output implementation accepted locally` |
| Reviewed plan gate | `post-implementation source provenance bounded evidence classification gate` |
| Current truth | `AGENTS.md`, `docs/design.md` current design sections, `docs/implementation-control.md` Startup Packet / Current Gate / Next Entry Point, accepted artifacts |

## Decision

Accepted.

The plan safely limits the next evidence run to bounded public CLI commands for `110020` / 2024 and `017641` / 2024. Classification must use only public provenance fields and quality outputs. Successful extraction, score generation, or non-blocking quality gate output remains insufficient to prove fallback eligibility.

The plan was revised after review to make the current deterministic expectation explicit: production public metadata does not propagate `primary_failure_category`, so fallback-backed rows are expected to classify as `provenance_unknown_public_metadata_absent`. Future-capable eligible / fail-closed paths remain in the state machine but are not expected to trigger without a later metadata schema gate. The revised plan also adds `primary_succeeded_no_fallback` for a restored primary-source success path.

## Review Summary

| Reviewer | Initial verdict | Re-review verdict | Controller disposition |
|---|---|---|---|
| AgentMiMo | `PASS` | `PASS` | Accepted. Re-review confirmed no new issue after GLM-driven revision. |
| AgentGLM | `PASS_WITH_FINDINGS` | `PASS` | Accepted. F1/F2 resolved. |

## Finding Disposition

| Finding | Source | Status | Judgment |
|---|---|---|---|
| Rules 3-5 were future-capable but not expected to trigger under current implementation | GLM F1 | Accepted and fixed | Plan now states fallback-backed rows are expected to be `provenance_unknown_public_metadata_absent` because `primary_failure_category` is not propagated. |
| No explicit state for `fallback_used=false` primary success | GLM F2 | Accepted and fixed | Plan now includes `primary_succeeded_no_fallback`, still `promotion_disposition=not_promoted` in this gate. |

## Accepted Evidence Scope

- Run only `fund-analysis extraction-snapshot`, `fund-analysis extraction-score`, and `fund-analysis quality-gate`.
- Scope commands exactly to `110020` / 2024 and `017641` / 2024.
- Use run ids:
  - `source-provenance-bounded-110020-2024-20260527`
  - `source-provenance-bounded-017641-2024-20260527`
- Keep generated outputs under ignored `reports/extraction-snapshots/`, `reports/scoring-runs/`, and `reports/quality-gate-runs/`.
- Track only the evidence summary artifact at `docs/reviews/release-maintenance-source-provenance-bounded-evidence-classification-20260527.md`.

## Forbidden Scope

No code/test/design/control-doc changes, no direct PDF/cache/source helper access, no source strategy changes, no renderer/FQ0-FQ6/default CLI behavior changes, no Host/Agent/dayu work, no replacement search, no golden/baseline/clean-denominator promotion, no commit/push/PR/GitHub mutation in the evidence worker handoff.

## Next Entry Point

`source provenance bounded evidence run`

The evidence worker may now run the exact accepted public CLI commands and produce the tracked evidence summary. The controller must review the evidence, dispatch two independent evidence reviews, and only then update control state / commit.
