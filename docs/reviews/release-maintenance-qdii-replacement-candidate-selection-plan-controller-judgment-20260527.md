# QDII Replacement Candidate Selection Plan — Controller Judgment

> Date: 2026-05-27
> Controller: Codex
> Gate: `QDII replacement candidate selection plan gate`
> Plan artifact: `docs/reviews/release-maintenance-qdii-replacement-candidate-selection-plan-20260527.md`
> Decision: **ACCEPTED LOCALLY**

## Startup Packet Replay

| Item | State |
|---|---|
| Current phase | `release maintenance` |
| Current gate before this judgment | `replacement/exclusion candidate selection accepted locally` |
| Startup Packet next entry point | `QDII replacement candidate selection plan gate; must use init-agents / tmux multi-agent flow` |
| Latest accepted checkpoint before this judgment | `667eed6 docs: accept replacement candidate disposition` |

This gate followed the Startup Packet next entry point. No reconciliation artifact was required.

## Accepted Plan Summary

The accepted plan preserves `017641` / 2024 as `replace`, `not_promoted`, and `disclosure_data_gap_not_baseline_ready`. It does not reinterpret the accepted P0 `manager_strategy_text` disclosure gap as an extractor gap or policy/taxonomy issue.

The plan correctly finds that no controller-approved QDII replacement candidate currently exists. Therefore the next safe cursor is plan-first:

`QDII replacement candidate enumeration plan gate`

No evidence CLI commands are authorized by this selection-plan gate.

## Reviews

| Reviewer | Artifact | Verdict |
|---|---|---|
| AgentMiMo | `docs/reviews/release-maintenance-qdii-replacement-candidate-selection-plan-review-mimo-20260527.md` | `PASS` |
| AgentDS | `docs/reviews/release-maintenance-qdii-replacement-candidate-selection-plan-review-ds-20260527.md` | `PASS_WITH_FINDINGS` |

## Finding Judgment

| Finding | Controller judgment | Reason |
|---|---|---|
| MiMo observation: "Approved inputs" wording could confuse candidate universe with approved candidate source | **accepted as enumeration-gate wording requirement** | The next plan must call `docs/code_20260519.csv` a candidate universe only, never an approved candidate list. |
| MiMo observation: accepted artifact/list wording is broad | **accepted as evidence-chain requirement** | The next plan must cite any accepted artifact path when using it as candidate context. |
| DS F1: pre-populated fund code list creates implicit shortlist risk | **accepted; enumeration must independently scan CSV** | The example codes in the plan are not a shortlist. The next gate must build its own candidate table from the CSV and must not assume those codes are exhaustive or pre-vetted. |
| DS F2: `013308` CSV category conflicts with QDII naming | **accepted as mandatory explicit check** | The enumeration table must flag and resolve QDII naming vs CSV category conflicts before a candidate can proceed. |
| DS F3: enumeration method omits source provenance pre-filter | **accepted as mandatory column / risk flag** | The enumeration table must include source-provenance status from accepted artifacts only, or `provenance_unknown` if no accepted evidence exists. |
| DS F4: QDII equity vs QDII bond subtype not addressed | **accepted as mandatory subtype/context column** | The enumeration table must include CSV category / asset-class context so the controller can decide whether bond QDII candidates can replace an equity QDII slot. |
| DS F7: future CLI flag precision unverified | **deferred to future evidence plan** | This gate does not authorize evidence; the future evidence plan must verify exact CLI flags before execution. |

No blocking finding remains. No re-review is required.

## Accepted Next Entry Point

`QDII replacement candidate enumeration plan gate`

Required next-gate constraints:

- Build a candidate-order table from `docs/code_20260519.csv` as a candidate universe, not as an approved candidate list.
- Do not run extraction, score, quality-gate, analyze, checklist, source-probing, or report-generation commands.
- Exclude `017641` and keep it `not_promoted`.
- Exclude QDII-FOF unless a separate taxonomy gate accepts QDII-FOF for this QDII slot.
- Include columns for source row identity, QDII/QDII-FOF taxonomy status, CSV category / asset-class context, source-provenance status from accepted artifacts or `provenance_unknown`, candidate-order rationale, owner, and revisit condition.
- Explicitly flag naming/category conflicts such as QDII name with domestic-stock CSV category.
- Preserve all no-promotion, fail-closed source, P0 quality, and manager_strategy_text stop conditions.

## Validation

- `git diff --check` passed before this judgment.
- This gate is docs/control/review only; no source or test code changed.

## Non-Goals Preserved

No evidence run, code, tests, renderer, FQ0-FQ6, Service/CLI, source strategy, `FundDocumentRepository`, source-helper, direct PDF/cache access, Host/Agent/dayu runtime, taxonomy implementation, extractor implementation, baseline/golden fixture promotion, GitHub mutation, push, PR, merge, or branch deletion occurred.
