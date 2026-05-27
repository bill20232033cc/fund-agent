# QDII Replacement Candidate Enumeration Plan — Controller Judgment

> Date: 2026-05-27
> Controller: Codex
> Gate: `QDII replacement candidate enumeration plan gate`
> Plan artifact: `docs/reviews/release-maintenance-qdii-replacement-candidate-enumeration-plan-20260527.md`
> Decision: **ACCEPTED LOCALLY**

## Startup Packet Replay

| Item | State |
|---|---|
| Current phase | `release maintenance` |
| Current gate before this judgment | `QDII replacement candidate selection plan accepted locally` |
| Startup Packet next entry point | `QDII replacement candidate enumeration plan gate; must use init-agents / tmux multi-agent flow` |
| Latest accepted checkpoint before this judgment | `8526223 docs: accept qdii replacement selection plan` |

This gate followed the Startup Packet next entry point. No reconciliation artifact was required.

## Accepted Plan Summary

The accepted enumeration plan scanned `docs/code_20260519.csv` as a candidate universe, not as an approved replacement list. It accounts for all QDII-relevant rows identified by the independent review scan and preserves the accepted dispositions for `017641`, QDII-FOF rows, index coverage, and bond follow-up rows.

`096001` / 大成标普500等权重指数(QDII)A人民币 is accepted only as the single candidate for the next future evidence **plan** gate. This does not make `096001` source-safe, quality-passing, scoring-ready, baseline-ready, golden-ready, promoted, or accepted as a replacement.

The next gate must remain plan-first and must not run evidence until that plan is reviewed and accepted.

## Reviews

| Reviewer | Artifact | Verdict |
|---|---|---|
| AgentMiMo | `docs/reviews/release-maintenance-qdii-replacement-candidate-enumeration-plan-review-mimo-20260527.md` | `PASS` |
| AgentDS | `docs/reviews/release-maintenance-qdii-replacement-candidate-enumeration-plan-review-ds-20260527.md` | `PASS_WITH_FINDINGS` |

## Finding Judgment

| Finding | Controller judgment | Reason |
|---|---|---|
| MiMo F1: validation section lists the scan command but not all QDII-signal rows | **accepted as informational; no plan patch required** | MiMo and DS independently verified the 56-row CSV scan and confirmed the candidate table accounts for all QDII-relevant rows. |
| MiMo F2: `013308` conflict resolution timeline is not specified | **accepted as future taxonomy condition** | `013308` is not the next evidence-plan candidate. It must not enter an evidence gate until a future taxonomy/controller decision resolves the QDII-name vs `国内股票类` conflict. |
| DS F1: `taxonomy_status` combines eligibility and risk flags | **deferred to future enumeration-table ergonomics** | The current table is human-reviewable and sufficient for controller judgment. Future tables may split `taxonomy_status` and `risk_flags`. |
| DS F2: bond QDII candidates have shared owner ambiguity | **accepted as controller clarification** | Bond QDII rows stay lower-priority and must not enter evidence unless equity QDII candidates fail or a later controller gate explicitly accepts asset-class replacement fitness. |
| DS F3: non-QDII-named overseas rows may classify differently in production | **deferred to future taxonomy gate** | The plan correctly marks `539003` and `000614` as `taxonomy_unknown_name_lacks_qdii`; no evidence is authorized for them in the next gate. |

No blocking or material finding remains. No re-review is required.

## Accepted Next Entry Point

`QDII replacement candidate evidence plan gate`

Required next-gate constraints:

- Use `$init-agents` / tmux multi-agent flow.
- Start with Startup Packet replay and explain that this is the accepted next entry point, not a gate switch.
- Produce a plan artifact before any evidence run.
- Select `096001` / 2024 as the single planned evidence candidate unless the controller explicitly changes the candidate.
- Verify exact public CLI flags for `extraction-snapshot`, `extraction-score`, and `quality-gate` in the plan before any later run.
- Require source provenance stop checks before quality or promotion interpretation.
- Require quality stop checks for P0 issues, especially `manager_strategy_text`.
- Keep `promotion_disposition=not_promoted` unless a later durable-baseline gate explicitly changes that state.
- Preserve fallback order only as contingency planning: `040046`, then `019172`, then remaining eligible equity QDII rows if `096001` fails in a later accepted evidence gate.

Do not run evidence, modify code, modify renderer, modify FQ0-FQ6, change Service/CLI defaults, touch `FundDocumentRepository` strategy, use direct PDF/cache/source helpers, create Host/Agent packages, introduce dayu runtime, promote fixtures/baseline/golden corpus, push, open PR, merge, or mutate GitHub in this accepted enumeration gate.

## Validation

- The enumeration plan reports `git diff --check` passed.
- AgentMiMo and AgentDS performed independent plan review.
- This gate is docs/control/review only; no production code or tests changed.

## Residual Risks

| Residual | Owner / next gate | Required handling |
|---|---|---|
| `096001` source provenance unknown | QDII replacement candidate evidence plan gate | Plan exact public evidence commands and source-provenance stop checks; do not treat candidate as source-safe before evidence. |
| `096001` quality unknown, including possible P0 `manager_strategy_text` block | QDII replacement candidate evidence plan gate | Plan quality stop checks and terminal classifications before any evidence execution. |
| `013308` QDII name vs domestic-stock CSV category conflict | future taxonomy/controller gate | Do not enter evidence for `013308` until conflict is resolved. |
| Bond QDII asset-class mismatch | future controller gate if equity QDII candidates fail | Do not use bond QDII candidates as replacement evidence without explicit asset-class fitness acceptance. |
| Non-QDII-named overseas rows classification | future taxonomy gate | Keep `539003` and `000614` out of the next evidence path. |

