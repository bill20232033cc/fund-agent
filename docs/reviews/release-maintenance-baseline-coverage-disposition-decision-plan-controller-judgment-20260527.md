# Baseline Coverage Disposition Decision Plan — Controller Judgment

> Date: 2026-05-27
> Controller: Codex
> Gate: `baseline coverage disposition decision gate`
> Plan artifact: `docs/reviews/release-maintenance-baseline-coverage-disposition-decision-plan-20260527.md`
> Decision: **ACCEPTED LOCALLY**

## Startup Packet Replay

| Item | State |
|---|---|
| Current phase | `release maintenance` |
| Current gate before this judgment | `017641 manager_strategy_text public evidence triage accepted locally` |
| Startup Packet next entry point | `baseline coverage disposition decision gate; must use init-agents / tmux multi-agent flow` |
| Latest accepted checkpoint before this judgment | `71f1aa4 docs: accept 017641 public evidence triage` |

This gate followed the Startup Packet next entry point. No reconciliation artifact was required.

## Accepted Plan Summary

The accepted plan reconciles the current baseline/golden blockers without running new evidence or changing code:

- `110020` / 2024 remains `reviewed_coverage_candidate_input_accepted`, `index_fund`, quality `warn`, complete eligible fallback after primary `unavailable`, and `not_promoted`; methodology / constituents sufficiency, strict golden absence, and reviewed fact freeze remain residuals.
- `017641` / 2024 remains `qdii_fund`, complete eligible fallback after primary `unavailable`, quality `block` on P0 `manager_strategy_text`, terminal `disclosure_data_gap_not_baseline_ready`, and `not_promoted`.
- `006597` / 2024 bond-lens applicability improvement is accepted, but `bond_risk_evidence_missing.baseline_blocking=true` and residual P1 gaps remain; it is not golden-ready.
- FOF remains `data_gap` / `taxonomy_pending`; QDII-FOF evidence cannot be counted as pure `fof_fund` without a separate accepted taxonomy decision.
- `004393` / active and `004194` / enhanced-index are already accepted clean evaluated candidates and remain carry-forward inputs only; this gate does not promote them to durable baseline or golden corpus.

The accepted next cursor is:

`replacement/exclusion candidate selection gate for QDII/index/FOF coverage`

## Reviews

| Reviewer | Artifact | Verdict |
|---|---|---|
| AgentMiMo | `docs/reviews/release-maintenance-baseline-coverage-disposition-decision-plan-review-mimo-20260527.md` | `PASS_WITH_FINDINGS` |
| AgentGLM | `docs/reviews/release-maintenance-baseline-coverage-disposition-decision-plan-review-glm-20260527.md` | `PASS_WITH_FINDINGS` |

## Finding Judgment

| Finding | Controller judgment | Reason |
|---|---|---|
| MiMo F1: clean candidates `004393` / `004194` are not listed in the reconciliation table | **accepted as carry-forward clarification** | They do not need disposition in this gate, but future baseline/golden preflight must remember they are evaluated candidates, not promoted fixtures. |
| MiMo F2: candidate options lack explicit owner assignment | **accepted as next-gate requirement** | The next disposition matrix must assign owner and revisit condition for every slot outcome. |
| MiMo F3: FOF v1 requirement is not pre-decided | **accepted as intended scope** | The disposition gate should decide whether FOF is required for v1 or deferred with owner/revisit condition. |
| GLM F1: bond disposition should be explicit follow-up | **accepted as next-gate requirement** | The accepted cursor focuses QDII/index/FOF, but bond must remain an explicit separate follow-up and golden blocker until `bond_risk_evidence_missing.baseline_blocking=true` is resolved or dispositioned. |
| GLM F2: plan-only gate could explicitly protect `AGENTS.md` / `docs/design.md` | **accepted as future wording guidance** | This gate did not edit them; future plan-only gates should list those truth docs in no-edit scope when relevant. |
| GLM F3: all slots may land on `needs_evidence_gate` | **accepted as valid outcome** | The next matrix may still conclude more evidence is needed, but it must record owners and revisit conditions instead of silently looping. |

No blocking finding remains. No re-review is required.

## Accepted Next Entry Point

`replacement/exclusion candidate selection gate for QDII/index/FOF coverage`

Required next-gate output:

- A reviewed candidate disposition matrix for index, QDII, and FOF coverage, using values such as `include_for_later_review`, `replace`, `exclude_from_v1`, `needs_taxonomy_gate`, or `needs_evidence_gate`.
- Explicit owner and revisit condition for every slot outcome.
- Explicit carry-forward state for `004393`, `004194`, and `006597`; bond disposition remains a separate follow-up and golden blocker until resolved.
- No durable baseline, clean denominator, fixture, report-quality corpus, or golden answer corpus promotion.

## Validation

- `git diff --check` passed before this judgment.
- This gate is docs/control/review only; no source or test code changed.

## Non-Goals Preserved

No code, renderer, FQ0-FQ6, Service/CLI, source strategy, `FundDocumentRepository`, source-helper, direct PDF/cache access, Host/Agent/dayu runtime, taxonomy implementation, extractor implementation, baseline/golden fixture promotion, GitHub mutation, push, PR, merge, or branch deletion occurred.
