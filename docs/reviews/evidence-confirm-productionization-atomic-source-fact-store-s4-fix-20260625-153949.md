# Atomic Source Fact Store / Composite Analysis View Split S4 Fix

## Verdict

S4_FIX_READY_FOR_RE_REVIEW_NOT_READY

## Gate

- Work unit: Atomic Source Fact Store / Composite Analysis View Split
- Current gate: S4 Fix Gate
- Role: fix worker only
- Scope: accepted finding `S4-F1`

## Finding Status

- `S4-F1`: 已修复

## Fix Summary

- `_composite_analysis_view_for_field()` now requires every configured dependency fact id for a migrated family to be present before constructing a `CompositeAnalysisView`.
- Single-child atomic scenarios still project available atomic entries unchanged.
- Partial single-child scenarios no longer add a derived composite entry/view and therefore do not introduce sibling `field_missing` for an unrequested missing dependency.
- `projection.source_facts` mirror behavior remains unchanged.

## Changed Files

- `fund_agent/fund/chapter_facts.py`
- `tests/fund/test_chapter_facts_atomic.py`
- `docs/reviews/evidence-confirm-productionization-atomic-source-fact-store-s4-fix-20260625-153949.md`

## Validation Results

- `uv run pytest tests/fund/test_chapter_facts_atomic.py tests/fund/test_chapter_facts.py -q`
  - Result: passed, `20 passed in 0.41s`
- `uv run pytest tests/fund/test_source_facts.py -q`
  - Result: passed, `17 passed in 0.37s`
- `uv run ruff check fund_agent/fund/chapter_facts.py tests/fund/test_chapter_facts_atomic.py tests/fund/test_chapter_facts.py`
  - Result: passed, `All checks passed!`
- `git diff --check`
  - Result: passed

## Regression Coverage

- Only `fee_schedule.management_fee` in the atomic store:
  - keeps the atomic management fee chapter entry;
  - does not emit a chapter fact with `derived_view_id == "fee_schedule"`;
  - does not emit a projection derived view with `view_id == "fee_schedule"`;
  - does not add `field_missing` for missing `fee_schedule.custody_fee`.
- Existing full dependency derived view test remains passing for `fee_schedule.management_fee` plus `fee_schedule.custody_fee`.

## Residual Risks

- S4 re-review still required before accepting this fix.
  - Owner/destination: S4 re-review gate.
- S5 Evidence Confirm atomic audit remains outside this fix scope.
  - Owner/destination: S5 Evidence Confirm Atomic Audit gate.
- Live/PDF/product CLI/provider/LLM behavior remains untested and unchanged in this gate.
  - Owner/destination: later explicitly authorized live/PDF and release/readiness evidence gate.
- Release/readiness remains `NOT_READY`.
  - Owner/destination: explicit release-boundary authorization and accepted readiness evidence.

## Explicit Non-goals Preserved

- No Evidence Confirm changes.
- No README/design/control docs changes.
- No unrelated plan docs or untracked artifacts edited.
- No commit, push, PR mutation, merge, tag, release, or readiness claim.

## Artifact Path

`docs/reviews/evidence-confirm-productionization-atomic-source-fact-store-s4-fix-20260625-153949.md`
