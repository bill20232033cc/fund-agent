# FundDisclosureDocument investor_experience.v1 Source-truth Direct Extraction Plan Controller Judgment

## Metadata

- Gate: Planning / Plan Review / Plan Fix / Plan Re-review Gate
- Work unit: FundDisclosureDocument investor_experience.v1 Source-truth Direct Extraction
- Branch: `funddisclosure-investor-experience-source-truth`
- Stacked base: PR 31 passed remote head `57c992f70dd6b7c43b799508bd69f37cf1b3cd02`
- Controller date: 2026-06-20

## Inputs

- Plan artifact: `docs/reviews/funddisclosuredocument-investor-experience-source-truth-extraction-plan-20260620.md`
- Initial plan reviews:
  - AgentDS: `docs/reviews/plan-review-investor-experience-source-truth-ds-20260620.md`
  - AgentMiMo: `docs/reviews/plan-review-investor-experience-source-truth-mimo-20260620-114946.md`
- Targeted re-reviews:
  - AgentDS: `docs/reviews/plan-rereview-investor-experience-source-truth-ds-20260620.md`
  - AgentMiMo: `docs/reviews/plan-rereview-investor-experience-source-truth-mimo-20260620.md`

## Decision

Accept the plan after targeted fix and re-review.

Verdict: `ACCEPT_PLAN_READY_FOR_IMPLEMENTATION_NOT_READY`.

The accepted implementation scope is exactly one field family: `investor_experience.v1` proof-positive FDD source-truth direct extraction for existing public/bundle keys `investor_return`, `holder_structure`, and `share_change`.

## Finding Disposition

| Source | Finding | Controller disposition | Outcome |
|---|---|---|---|
| AgentDS F1 | `share_change` FDD column selection was underspecified | accepted | Plan now defines `column_header_path` aggregation, label-column exclusion, value-column validation, exact fund-code header matching, and required tests. |
| AgentDS F2 | `holder_structure` placeholder values could be emitted | accepted | Plan now rejects empty/placeholder values and requires a placeholder filtering test. |
| AgentDS F3 | `investor_return` paragraph label/value pattern was underspecified | accepted | Plan now requires same-paragraph label plus valid percent value and negated/unavailable wording omission, with required test coverage. |
| AgentMiMo 004 | `net_change` calculation format was underspecified | accepted | Plan now requires Decimal arithmetic aligned with existing `_calculate_net_change` semantics and a computed net-change test. |
| AgentMiMo 005 | estimated `investor_return` conflict rule was underspecified | accepted | Plan now applies the ambiguity rule to conflicting estimated values and requires estimated-only / estimated-conflict tests. |
| DS open question | `current_stage.v1` / `core_risk.v1` candidate evidence non-interference should be explicit | accepted | Plan now states investor direct-route suppression must not clear those candidate evidence paths and requires a non-interference test. |
| AgentMiMo 001/002/003/006 | Scope limitations and no-change observations | rejected-with-reason | These are accepted residual/scope notes, not required plan changes. |

Both targeted re-reviews returned `TARGETED_PLAN_REREVIEW_PASS`.

## Binding Implementation Conditions

- Implement only `investor_experience.v1`.
- Emit only existing public/bundle keys: `investor_return`, `holder_structure`, `share_change`.
- Keep `subscription_redemption` and `income_distribution` candidate-only; do not create public subvalues for them.
- Suppress `investor_experience.v1` candidate evidence when the proof-positive direct route is active, including direct-route missing.
- Preserve proof-missing/proof-invalid/candidate-boundary public missing semantics.
- Do not alter `current_stage.v1` or `core_risk.v1` source-truth behavior; their candidate evidence must remain independently governed by existing selectors.
- No parser replacement, repository/source/cache/PDF/Docling/pdfplumber/live/network/provider/LLM work.
- No `EvidenceSourceKind` or public `EvidenceAnchor` expansion.
- No Service/UI/Host/renderer/quality-gate direct FDD candidate JSON consumption.
- No real-report correctness, golden/readiness, release, mark-ready, merge, or PR mutation claim.

## Next Gate

Next entry point: `FundDisclosureDocument investor_experience.v1 Source-truth Direct Extraction Implementation Gate`.

The next implementation worker must use the accepted plan artifact as binding scope and stop after implementation, validation, docs sync, and implementation evidence. No commit, push, PR, or review is authorized to the implementation worker.
