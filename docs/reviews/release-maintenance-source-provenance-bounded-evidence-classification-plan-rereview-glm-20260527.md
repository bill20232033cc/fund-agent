# Targeted Re-Review: Source Provenance Bounded Evidence Classification Plan

> Date: 2026-05-27
> Reviewer: AgentGLM
> Role: Targeted re-review — F1/F2 resolution only
> Revised plan: `docs/reviews/release-maintenance-source-provenance-bounded-evidence-classification-plan-20260527.md`
> Original review: `docs/reviews/release-maintenance-source-provenance-bounded-evidence-classification-plan-review-glm-20260527.md`
> Scope: Check only whether F1 and F2 are resolved; confirm commands and forbidden scope unchanged.

---

## F1 (中): 分类规则 3/4/5 为不可触达死路径 — 需显式承认确定性结果

### Resolution: RESOLVED

Revised plan adds three explicit acknowledgments:

1. **Gate Objective (line 42)**: "Current implementation note" paragraph states `AnnualReportSourceMetadata` does not propagate `primary_failure_category`, the expected terminal state is `provenance_unknown_public_metadata_absent`, and rules for `provenance_fail_closed`, `quality_blocked_after_provenance`, and `provenance_eligible_for_next_review` are "defensive future-capable paths" that "are not expected to trigger in the current implementation."

2. **Rule 3 (line 98)**: Added "This is the expected terminal provenance state for current fallback-backed rows because current implementation does not propagate `primary_failure_category` from repository source metadata."

3. **Rules 4, 5, 6 (lines 104, 109, 119)**: Each annotated with "Defensive future-capable path only" explaining why it won't trigger given current metadata limitations.

The evidence worker and downstream reviewers can now unambiguously determine that fallback-backed rows will classify as rule 3, without confusion about why rules 4-6 don't trigger.

---

## F2 (低): 缺少 `fallback_used=false`（主源成功）显式分类状态

### Resolution: RESOLVED

Revised plan adds:

1. **New Rule 2 `primary_succeeded_no_fallback` (lines 89-92)**: Covers `fallback_used=false`, `fallback_eligibility="not_applicable"`, `source_provenance_status="not_applicable"`. Includes quality sub-branching (`pass`/`warn` vs `block`) and `promotion_disposition=not_promoted`.

2. **Denominator rules (line 133)**: Explicit entry for `primary_succeeded_no_fallback` with no-promotion disposition and later corpus consideration clause.

3. **Rule 7 `not_promoted` (line 123)**: Updated to reference `primary_succeeded_no_fallback` alongside `provenance_eligible_for_next_review`.

Rule ordering is logically sound: `primary_succeeded_no_fallback` at position 2 correctly partitions the `fallback_used=false` case before fallback-dependent rules (3-6).

---

## Commands And Forbidden Scope Verification

Validation Commands (lines 155-161): Identical to original plan. Six bounded commands for exactly `110020`/2024 and `017641`/2024 using public CLI.

Forbidden Scope (lines 187-201): Identical to original plan. All review focus prohibitions maintained.

---

## New Issues Introduced By Revision

None detected. Rule numbering update (6 → 7 rules) is consistent across Classification Rules, Denominator And Promotion Rules, and Evidence Summary Required Shape sections.

---

## Re-Review Conclusion

**PASS**

Both findings resolved. No new issues. Plan is safe for evidence worker handoff.
