# FundDisclosureDocument S6-G Current Stage Candidate Selector Plan Controller Judgment

## Verdict

`ACCEPT_S6G_CURRENT_STAGE_CANDIDATE_SELECTOR_PLAN_NOT_READY`

## Scope

- Gate: `FundDisclosureDocument S6-G Current Stage Candidate Selector Planning Gate`
- Classification: `heavy planning gate`
- Accepted plan: `docs/reviews/funddisclosuredocument-s6g-current-stage-candidate-selector-plan-20260619.md`
- Initial plan reviews:
  - `docs/reviews/plan-review-20260619-154420.md` - AgentDS, `pass-with-risks`
  - `docs/reviews/plan-review-20260619-154527.md` - AgentMiMo, `pass`
- Targeted re-reviews:
  - `docs/reviews/plan-review-20260619-155004.md` - AgentDS, `pass`
  - `docs/reviews/plan-review-20260619-155050.md` - AgentMiMo, `pass`

## Controller Decision

The S6-G plan is accepted for exactly one field family selector: `current_stage.v1`.

The accepted implementation direction is a deterministic candidate-only locator selector for Chapter 5 current-stage and key-change disclosure. It may locate current-stage, manager-change, share/scale-change, and holding/strategy-change candidates for later extraction/evidence gates, but it must not infer Chapter 5 conclusions such as stage classification, change impact, whether prior judgments changed, tracking-variable priority, valuation status, market forecast, final holding/replacement judgment, or buy/sell/action labels.

Public field-family results must remain fail-closed: `status="missing"`, `extraction_mode="missing"`, `value={}`, `anchors=()`.

Candidate evidence remains internal `candidate_only` / `not_proven` / `not_ready` evidence and must not be projected to `StructuredFundDataBundle`, public `EvidenceAnchor`, renderer, quality gate, Service, Host, UI, LLM prompt, source truth, parser replacement, readiness, PR readiness, or release.

## Finding Disposition

AgentDS initial review findings are accepted and closed by the amended plan:

- The `holding_strategy_change` guard-token duplicate `报告期内基金投资策略和运作分析` was removed from guard tokens while remaining as a strong token.
- `_current_stage_cell_guard_context()` now explicitly follows the S6-F `_core_risk_cell_guard_context()` role-invariant inclusion tuple and always excludes `cell_text` / `cell_text_normalized`.
- The overlap regression test now requires baseline S6-E `share_change` strong-token content and asserts S6-E record count, source path order, gap codes, public `value`, and public `anchors` remain unchanged.
- Fee-adjustment under-coverage is confirmed as a residual with owner/destination and does not expand S6-G token scope.

AgentMiMo initial review findings are accepted and closed or dispositioned:

- S6-E share-change token overlap is closed by the strengthened overlap regression test requirement.
- Cell guard ambiguity is closed by the explicit inclusion tuple and S6-F role-invariant reference.
- Fee-adjustment under-coverage remains documented residual; fee tokens stay S6-C-owned for this gate.

Targeted re-reviews `docs/reviews/plan-review-20260619-155004.md` and `docs/reviews/plan-review-20260619-155050.md` both concluded `pass`; all accepted findings are closed.

## Binding Implementation Amendments

Future S6-G implementation must follow the accepted plan and these binding amendments:

1. Implement exactly one selector: `current_stage.v1`.
2. Keep all candidate evidence under `FundFieldFamilyResult.candidate_evidence`; public `status`, `extraction_mode`, `value`, and `anchors` must remain `missing`, `missing`, `{}`, and `()`.
3. Do not change accepted S6-B/S6-C/S6-D/S6-E/S6-F selector traversal, row locators, limits, source paths, gap semantics, or public value/anchor behavior.
4. Keep `_field_families_for_intermediate()` mapping style; add `current_stage.v1` to the local family-evidence mapping, do not restore nested conditional logic.
5. Do not refactor S6-B/S6-C/S6-D/S6-E/S6-F traversal helpers into shared helpers in this gate.
6. `_current_stage_cell_guard_context()` must be role-invariant and must use exactly the S6-F-style inclusion tuple: `table.heading_text`, `table.table_caption_or_nearby_heading`, `*table.heading_path`, `*cell.row_label_path`, `*cell.column_header_path`, `*cell.heading_path`; it must exclude same-cell text fields.
7. Do not add fee tokens, market/valuation external-truth tokens, Chapter 5 reasoning/output tokens, Chapter 6 risk tokens, product identity-only tokens, manager biography-only tokens, investor-experience-only tokens, or return/fee-only tokens as `current_stage.v1` locator tokens.
8. Tests must include public value/anchor leak prevention, candidate-boundary behavior, ordering/dedupe/limit/excerpt behavior, broad-token guard negative and positive cases, cell self-guard blocking, Chapter 5 forbidden reasoning/output blocking, Chapter 6 risk-token non-capture, market/valuation external-token non-capture, product/S6-C/S6-D/S6-E/S6-F overlap non-regression, and explicit S6-E share-change overlap regression.

## Boundary

This accepted plan does not authorize implementation by itself until the next implementation gate starts.

It does not prove source truth, field correctness, full coverage, parser replacement, golden/readiness, release, PR readiness, Chapter 5 conclusion quality, valuation status, market environment correctness, or upper-layer consumption.

No live/network/PDF/FDR/Docling conversion/pdfplumber export/manual reference review/provider/LLM command is accepted by this gate.

## Next Entry

After accepted plan commit, next entry point is `FundDisclosureDocument S6-G Current Stage Candidate Selector Implementation Gate`.
