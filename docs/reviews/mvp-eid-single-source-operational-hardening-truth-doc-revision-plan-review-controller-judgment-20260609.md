# EID Single Source Operational Hardening Truth-Doc Revision Plan Review — Controller Judgment

## Gate

| Item | Value |
|---|---|
| Gate | `EID Single Source Operational Hardening Gate` |
| Classification | `heavy` |
| Date | 2026-06-09 |
| Plan artifact | `docs/reviews/mvp-eid-single-source-operational-hardening-truth-doc-revision-plan-20260609.md` |
| DS review | `docs/reviews/mvp-eid-single-source-operational-hardening-truth-doc-revision-plan-review-ds-20260609.md` |
| MiMo review | `docs/reviews/mvp-eid-single-source-operational-hardening-truth-doc-revision-plan-review-mimo-20260609.md` |

## Controller Verdict

`BLOCKED_PENDING_TARGETED_PLAN_REVISION`

The plan is directionally correct and matches the steering decision, but it is not yet accepted. DS identified two blocking findings that must be fixed before this gate can proceed to truth-doc revision.

## Finding Decisions

| Finding | Reviewer severity | Controller decision | Reason |
|---|---:|---|---|
| DS F1: `docs/implementation-control.md` explicit conflicts are not inventoried in the conflict table or slice change lists | BLOCKING | accepted | The current control doc has explicit wording that EID is not exclusive source truth and that `not_found` / `unavailable` are fallback-eligible. A truth-doc revision plan must identify those exact conflicts so a revision worker can make the source-policy truth unambiguous. |
| DS F2: no-live validation matrix can false-pass incomplete EID policy wording | BLOCKING | accepted | A heavy source-policy gate requires falsifiable validation. The current matrix can pass if only one of `selected_source`, `single_source_only`, or `fallback_enabled` appears in a target doc. |
| DS non-blocking: Slice 0 could record exact conflicting line numbers | NON-BLOCKING | accepted as optional strengthening | Exact conflict lines reduce re-review ambiguity but are not required beyond fixing F1. |
| DS non-blocking: design section reference is accurate but incomplete standalone | NON-BLOCKING | no action required | The broader plan already covers the needed design sections. |
| MiMo F1: boundary validation check can be split more explicitly | INFO | accepted as optional strengthening | This overlaps with DS F2 and should be considered while revising the validation matrix. |
| MiMo F2-F4: consistency, operational topics, direct evidence matrix are sufficient | INFO | accepted | These support that no plan-level redesign is needed. |

## Required Targeted Revision

The planning worker must revise only `docs/reviews/mvp-eid-single-source-operational-hardening-truth-doc-revision-plan-20260609.md`.

Minimum required fixes:

1. Add explicit conflict inventory entries for:
   - the control-doc statement that EID is preferred locator but not exclusive source truth, and that official document URLs may come from EID, fund-company website/CDN, CNINFO, or other official/first-party platforms;
   - the control-doc statement that `not_found` / `unavailable` remain fallback-eligible.
2. Add corresponding revision targets in Slice 2 and Slice 3 so the control doc and startup packet are updated consistently.
3. Make the no-live validation matrix falsifiable for each target doc:
   - `selected_source=eid`;
   - `mode=single_source_only`;
   - `fallback_enabled=false`.
4. Preserve all existing boundaries:
   - no source/test/README edits;
   - no live EID/network/PDF/FDR/fallback/provider/probe;
   - no implementation authorization;
   - no commit/push/PR;
   - Eastmoney remains deferred/future risk;
   - row-shape residual gate remains queued / paused by steering.

## Next Action

Dispatch targeted plan revision to the original planning worker, then send the revised plan back to DS and MiMo for targeted re-review.
