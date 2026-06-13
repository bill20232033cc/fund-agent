# Provider/LLM Chapter 2 L1 Numerical Closure Root-cause Evidence Controller Judgment

Date: 2026-06-14

## Scope

Gate: `Provider/LLM Chapter 2 L1 Numerical Closure No-live Root-cause Evidence Gate`.

This judgment closes the no-live evidence gate for Chapter 2 `repair_budget_exhausted` / `prompt_contract` / `l1_numerical_closure`. It does not implement a fix, change source/tests/runtime behavior, change repair budget, change provider defaults, change annual-report source policy, run live/provider/network/source/PDF/readiness/release/PR commands, or claim readiness.

Release/readiness remains `NOT_READY`. Annual-report access remains EID single-source/no-fallback.

## Evidence Reviewed

- Evidence artifact: `docs/reviews/provider-llm-chapter2-l1-numerical-closure-root-cause-evidence-20260614.md`
- DS evidence review: `docs/reviews/provider-llm-chapter2-l1-numerical-closure-root-cause-evidence-review-ds-20260614.md`
- MiMo evidence review: `docs/reviews/provider-llm-chapter2-l1-numerical-closure-root-cause-evidence-review-mimo-20260614.md`
- Accepted plan judgment: `docs/reviews/provider-llm-chapter2-l1-numerical-closure-root-cause-plan-controller-judgment-20260614.md`
- Control truth: `docs/current-startup-packet.md`, `docs/implementation-control.md`

## Accepted Current Facts

- The current active evidence gate was opened after Chapter 2 L1 root-cause planning was accepted locally at `bcb2402`.
- The prior accepted bounded live evidence established that Chapter 3 item 01 no longer reproduces provider-before `ValueError` / `code_bug`; Chapter 3 now blocks as fact-gap, while Chapter 2 is the first failed blocker.
- The exact runtime metadata under review identifies Chapter 2 as:
  - `stop_reason=repair_budget_exhausted`
  - `failure_category=prompt_contract`
  - `failure_subcategory=l1_numerical_closure`
  - `attempt_count=2`
- Attempt 0 produced a valid L1 blocker and `patch` repair hint; current repair policy mapped `patch` to whole-chapter `regenerate`.
- Attempt 1 again produced an L1 blocker and then stopped with `repair_budget_exhausted`.
- Safe diagnostics correctly classify the failure as `prompt_contract/l1_numerical_closure`, but do not serialize complete allowed fact/anchor totals or required-output linkage.

## Review Finding Disposition

| Finding | Source | Disposition | Controller rationale |
| --- | --- | --- | --- |
| Evidence supports H3 as the strongest current root cause. | Evidence, DS, MiMo | ACCEPT | Direct safe metadata, narrow code reads and focused no-live tests prove the terminal failure path: a contract-valid L1 blocker persisted after `patch` was converted to whole-chapter regenerate, then exhausted the one-regenerate budget. |
| H1 required-output omission vs optional ITEM_RULE deletion is rejected. | Evidence, DS, MiMo | ACCEPT | `required_output_missing_count=0`, seven Chapter 2 required outputs are block-on-missing, and `chapter_2_tracking_error_analysis` deletion belongs to optional conditional ITEM_RULE behavior. |
| H2 L1 rule strictness or contract mismatch is rejected. | Evidence, DS, MiMo | ACCEPT | Writer contract and auditor enforcement share the same nearby-anchor boundary; focused no-live tests cover valid and invalid L1 cases. |
| H4 evidence/fact/anchor availability insufficiency needs more evidence. | Evidence, DS, MiMo | ACCEPT | Runtime proves some facts/anchors were used and no missing reasons were declared, but allowed totals and required-output linkage are not serialized, so H4 cannot be fully rejected. |
| H5 diagnostic serialization incompleteness is a contributing cause only. | Evidence, DS, MiMo | ACCEPT | Diagnostics classify the runtime decision correctly but leave evidence-availability ambiguity; this did not itself cause the Chapter 2 failure. |
| Evidence artifact reports one jq diagnostics query as exit 5. | MiMo F1; DS notes different recovery framing | ACCEPT_AS_NONBLOCKING_ARTIFACT_DEFECT | MiMo independently verified that the specific object-construction jq command succeeds. The later type-aware query and all substantive metadata claims are correct. This is a command-detail defect in the evidence artifact, not a blocker and not a root-cause change. |
| No-live/read boundaries were preserved. | DS, MiMo | ACCEPT | Reviews confirm no forbidden body reads, no prohibited Chapter 3 evidence/review body reads, no live/provider/network/source/PDF/readiness/release/PR commands, and no source/test/runtime edits. |
| `NOT_READY` and EID single-source/no-fallback are preserved. | Evidence, DS, MiMo | ACCEPT | No readiness, release, MVP-ready, PR-ready, fallback or source-expansion claim was made. |

## Accepted / Rejected / Residual Table

| Item | Decision | Basis | Next handling |
| --- | --- | --- | --- |
| H3 repair regenerate strategy preserving/worsening L1 | ACCEPT_ROOT_CAUSE | Attempt 0 `patch` -> regenerate, attempt 1 repeated L1 and exhausted budget; code maps patch/regenerate to regenerate while budget remains | Proceed to no-live fix planning gate scoped to Chapter 2 L1 repair behavior |
| H1 required-output omission vs optional ITEM_RULE deletion | REJECT | Direct diagnostics and code/test evidence distinguish required-output behavior from optional ITEM_RULE deletion | No fix path for H1 |
| H2 L1 rule strictness or contract mismatch | REJECT | Writer contract and auditor implementation align on nearby anchor marker requirement | Do not weaken or remove L1 |
| H4 evidence/fact/anchor availability insufficiency | ACCEPTED_RESIDUAL | Safe metadata lacks allowed fact/anchor counts and required-output linkage | Future diagnostic/projection evidence or diagnostic implementation gate if needed |
| H5 diagnostic serialization incompleteness | ACCEPT_CONTRIBUTING_CAUSE | Correct high-level classification but incomplete evidence-availability serialization | Consider safe diagnostic additions in a separate or explicitly scoped fix-planning item |
| jq exit-code attribution in evidence artifact | ACCEPTED_RESIDUAL_NONBLOCKING | MiMo verified substantive facts despite command-detail mismatch | Note in this judgment; no evidence rewrite required |

## Next Gate Recommendation

Proceed to:

`Provider/LLM Chapter 2 L1 Numerical Closure No-live Fix Planning Gate`

Required constraints for that gate:

- Planning only unless a later accepted plan authorizes implementation.
- Preserve the accepted L1 contract: numerical R/A/B/C/A-C closure assertions require nearby allowed anchor markers.
- Do not weaken L1, delete the blocker, or convert prompt-contract failure into a warning.
- Do not change repair budget defaults unless a separate repair-budget calibration gate authorizes it.
- Do not change provider defaults, source policy, fallback behavior, annual-period LLM route, readiness/release/PR state, or EID single-source/no-fallback policy.
- Treat H4/H5 as residual diagnostics scope; do not use them to dilute the accepted H3 root cause.

## Residuals

| Residual | Owner | Current blocker? | Destination |
| --- | --- | --- | --- |
| H4 safe metadata cannot prove full allowed fact/anchor availability or required-output linkage. | Service/Agent diagnostics owner | No, for proceeding to fix planning | Future diagnostic/projection evidence gate or scoped diagnostic implementation planning |
| H5 safe diagnostic serialization lacks allowed counts/linkage. | Service/LLM artifact owner | No, for proceeding to fix planning | Future safe diagnostic addition gate if needed |
| Current repair budget is not product-calibrated. | Service/Agent chapter orchestration owner | No, for this evidence closeout | Separate chapter repair budget calibration gate |
| Full LLM completion, provider acceptance, content quality, release/readiness and PR state remain unproven. | Release/provider/LLM owners | Yes, for readiness claims | Later controlled gates only |

## Control-doc Update Recommendation

After this judgment is checkpointed, update `docs/current-startup-packet.md` and `docs/implementation-control.md` to record:

- Evidence checkpoint commit for this gate.
- Controller verdict below.
- Next entry point: `Provider/LLM Chapter 2 L1 Numerical Closure No-live Fix Planning Gate`.
- Release/readiness remains `NOT_READY`.
- EID single-source/no-fallback remains unchanged.

## Final Verdict

VERDICT: ACCEPT_ROOT_CAUSE_H3_READY_FOR_NO_LIVE_FIX_PLANNING_GATE_NOT_READY
