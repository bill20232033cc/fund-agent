# Plan Re-review: FundDisclosureDocument current_stage.v1 Source-truth Direct Extraction

**Role**: AgentDS targeted plan re-reviewer
**Plan artifact**: `docs/reviews/funddisclosuredocument-current-stage-source-truth-extraction-plan-20260620.md`
**Prior review**: `docs/reviews/plan-review-current-stage-source-truth-ds-20260620.md`
**Gate**: Plan Re-review Gate
**Date**: 2026-06-20
**Verdict**: `TARGETED_PLAN_REREVIEW_PASS`

## Scope

Review only whether F1–F4 from the prior review are fixed and whether any fix introduces a new blocker. F5 was an observation, not a finding requiring fix action.

## F1 [MEDIUM] Reuse-target underspecification — FIXED

Prior review: plan instructed reuse but didn't name specific module-level functions.

Plan now lines 99–104 name exact targets per key:

- `basic_identity`: `_select_product_essence_values()` → `_build_product_essence_basic_identity()`, with explicit "Do not call `_extract_product_essence_source_truth()`" guard
- `share_change`: `_select_investor_experience_share_change()` with all sub-helpers enumerated and "do not duplicate arithmetic, A-share detection, row-kind detection, or ambiguity logic" prohibition
- `holdings_snapshot`: `_select_manager_profile_holdings_snapshot()` with all sub-helpers enumerated and explicit prohibition on concentration/style/risk/stage-conclusion emission
- `portfolio_managers`: `_select_manager_profile_portfolio_managers()` with all sub-helpers enumerated and explicit prohibition on quality/stage-implication emission

Lines 106–110 also enumerate the existing owning-family call chains that must remain shape-preserving. Target functions are fully specified. No new blocker introduced.

## F2 [MEDIUM] "Small refactors" budget unbounded — FIXED

Prior review: refactor budget had no bound on which functions, how many, or how to verify.

Plan now lines 112–117 contain explicit bounds:

- Maximum new shared helpers: four, one per reused top-level key
- Maximum edit scope: move code into shared helper, replace original body/call site with direct call
- Explicitly prohibited semantic changes: no rewrites, token broadening, output key changes, status changes, gap-code changes, anchor schema changes, candidate-evidence changes
- Verification requirement: if any helper extracted, behavior-preserving tests must pass for all four existing direct family outputs (basic_identity, share_change, holdings_snapshot, portfolio_managers) on their existing focused fixtures before current-stage assertions

Budget is now bounded in count, edit scope, and verification. No new blocker introduced.

## F3 [LOW] Ambiguity/conflict detection unspecified — FIXED

Prior review: conflict detection heuristic undefined.

Plan now lines 123–124 contain precise contract:

- At most one candidate per top-level key from the exact owning helper
- Existing owning-helper ambiguity propagated and generates `ambiguous_table_or_locator`
- For internal composite resolver seeing multiple same-key candidates: compatible only when normalized values are structurally equal after recursively sorting dict keys, preserving list order, and applying `_normalize_match_text()` to scalar leaves
- Non-equal same-key candidates → conflicting stable values → `ambiguous_table_or_locator` → suppressed from public value
- Exact duplicate same-key values → deduped, emitted once with first stable anchor

Detection heuristic is fully specified with structural equality definition. No new blocker introduced.

## F4 [LOW] Facade test slice lacks processing-path integration — FIXED

Prior review: Slice 4 had no integration test feeding all six families through `_active_processor_result_to_bundle()`.

Plan now Slice 4 lines 173–174 include:

- Integration coverage for processor result containing all six families
- Assert `_active_processor_result_to_bundle()` ignores `current_stage.v1`
- Assert `basic_identity` projects only from `product_essence.v1`, `share_change` only from `investor_experience.v1`, `holdings_snapshot`/`portfolio_managers` only from `manager_profile.v1`

Integration path coverage is added. No new blocker introduced.

## New Blocker Check

All four fixes add specificity without changing plan boundaries:

- No new public keys, bundle fields, or schema expansions introduced
- No semantic stage judgment added
- Existing family contract (active_annual.py) unchanged
- State-machine paths unchanged
- core_risk.v1 isolation preserved
- Non-goals and constraints from original plan intact

No new blocker.

## Verdict

`TARGETED_PLAN_REREVIEW_PASS`
