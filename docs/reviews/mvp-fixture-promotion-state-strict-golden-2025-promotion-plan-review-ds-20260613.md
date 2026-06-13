# DS Review - Fixture Promotion State / Strict Golden 2025 Promotion Planning Gate

Date: 2026-06-13

Target: `docs/reviews/mvp-fixture-promotion-state-strict-golden-2025-promotion-plan-20260613.md`

Verdict: `FAIL_REQUIRES_AMENDMENT`

## Scope

This review checked the planning artifact only. It did not modify files and did
not run live EID, network, PDF, FDR, provider, LLM, analyze, checklist,
readiness, release, PR, push, merge, cleanup or promotion commands.

## Blockers

| Finding | Disposition required | Rationale |
|---|---|---|
| Fixture promotion runtime schema was not precise enough in the first plan draft. | Must amend before acceptance. | Current preflight loads fixture promotion state as `dict[fund_code, PromotionState]` and derives state by fund code only. It cannot safely express `004393 / 2025`-only promotion while leaving `004393 / 2024` unpromoted. |
| Future fixture promotion implementation write set was too broad. | Must amend before acceptance. | The first draft allowed a new manifest path plus optional parser/test/README changes in one route, which could let an evidence gate implicitly authorize runtime contract expansion. |

Required amendments:

- Add a repo fact that current fixture promotion parser is fund-code-only and
  year-blind.
- Require a fixture promotion evidence gate to decide whether promotion identity
  must become `(fund_code, report_year)`.
- Forbid using `{"fund_code": "004393", "promotion_state": "promoted_fixture"}`
  under the current parser as proof of `004393 / 2025`-specific promotion.
- Split future fixture promotion work into:
  - a no-parser-change path with an exact manifest path and blocking-only
    fund-code semantics; and
  - a separate schema/parser planning gate before any year-aware parser change.

## Non-blocking Findings

| Finding | Disposition required | Rationale |
|---|---|---|
| Primary next entry is correct. | Accept. | The plan correctly recommends `Strict golden 2025 answer evidence gate` instead of direct implementation or promotion. |
| Historical fixture promotion manifest is not misused. | Accept. | The plan correctly treats the 2025-05-29 manifest as control-plane-only and not runtime promotion approval. |
| Strict golden year identity facts are materially correct. | Accept. | The plan uses `fund_code + report_year + field_name + sub_field` and preserves legacy 2024 compatibility limits. |
| Evidence gate should include an exact read-only identity enumeration command. | Amend. | This makes the evidence gate code-generation-ready and prevents ad hoc residue reads. |

## Reviewer Recommendation

Do not accept the original draft. Accept only an amended plan that hardens
fixture promotion identity, narrows future write sets, and preserves
`NOT_READY`.
