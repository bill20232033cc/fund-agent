# FundDisclosureDocument S6-F Core Risk Candidate Selector Plan Controller Judgment

## Verdict

`ACCEPT_S6F_CORE_RISK_CANDIDATE_SELECTOR_PLAN_NOT_READY`

## Scope

- Gate: `FundDisclosureDocument S6-F Single-family Candidate Evidence Selector Planning Gate`
- Classification: `heavy planning gate`
- Accepted plan: `docs/reviews/funddisclosuredocument-s6f-core-risk-candidate-selector-plan-20260619.md`
- Initial plan reviews:
  - `docs/reviews/plan-review-20260619-142152.md` - AgentDS, `pass-with-risks`
  - `docs/reviews/plan-review-20260619-142322.md` - AgentMiMo, `pass-with-risks`
- Targeted re-reviews:
  - `docs/reviews/plan-review-20260619-142935.md` - AgentDS, `pass`
  - `docs/reviews/plan-review-20260619-143027.md` - AgentMiMo, `pass`

## Controller Decision

The S6-F plan is accepted for exactly one field family selector: `core_risk.v1`.

The accepted implementation direction is a deterministic candidate-only locator selector. It may locate risk-related disclosure candidates for later extraction/evidence gates, but it must not infer Chapter 6 conclusions such as one-vote veto, risk causality, risk level, structural/cyclical risk, pressure-test conclusion, final holding/replacement judgment, or "most fatal risk".

`current_stage.v1` remains unimplemented and must not receive candidate evidence in this gate.

## Finding Disposition

AgentDS initial review findings are accepted and closed by the amended plan:

- F1 accepted and closed: `_field_families_for_intermediate()` must not add a sixth nested conditional expression. Future implementation must use a local `candidate_evidence_by_family` mapping or equivalent local mapping while preserving `_FAMILY_ORDER`; `current_stage.v1` remains absent or empty.
- F2 accepted and closed: `core_risk.v1` cell generic guard context must never include `cell_text` or `cell_text_normalized`, and implementation must not copy the S6-E default cell-guard branch.
- F3 accepted and closed: no shared helper refactor is authorized. Future implementation may add core-risk-local private helpers only.
- F4 accepted and closed: Test 10 must cover both pure forbidden Chapter 6 output/reasoning tokens and forbidden-plus-legal-strong-token mixed content.

AgentMiMo initial review finding is accepted and closed:

- The overlap regression test must use explicit baseline comparison for S6-B/S6-C/S6-D/S6-E candidate evidence before and after adding S6-F content.

Targeted re-reviews `docs/reviews/plan-review-20260619-142935.md` and `docs/reviews/plan-review-20260619-143027.md` both concluded `pass`; all original findings are closed.

## Binding Implementation Amendments

Future S6-F implementation must follow these binding amendments from the accepted plan and reviews:

1. Implement exactly one selector: `core_risk.v1`.
2. Keep all candidate evidence under `FundFieldFamilyResult.candidate_evidence`; public `status`, `extraction_mode`, `value`, and `anchors` must remain `missing`, `missing`, `{}`, and `()`.
3. Do not implement `current_stage.v1`.
4. Do not change accepted S6-B/S6-C/S6-D/S6-E selector traversal, row locators, limits, source paths, gap semantics, or public value/anchor behavior.
5. Use local family-evidence mapping in `_field_families_for_intermediate()` instead of extending the nested conditional chain.
6. Do not refactor S6-B/S6-C/S6-D/S6-E traversal helpers into shared helpers in this gate.
7. `core_risk.v1` cell generic guard context must be role-invariant and must exclude same-cell text fields.
8. Tests must include broad-token negative cases, cell self-guard blocking, Chapter 6 reasoning/output token blocking, mixed forbidden-plus-legal token behavior, candidate-boundary behavior, ordering/dedupe/limit/excerpt behavior, and comparative overlap regression for existing S6-B/S6-C/S6-D/S6-E families.

## Boundary

This accepted plan does not authorize implementation by itself until the next implementation gate starts.

It does not prove source truth, field correctness, full coverage, parser replacement, golden/readiness, release, PR readiness, pressure-test sufficiency, Chapter 6 conclusion quality, or upper-layer consumption.

No live/network/PDF/FDR/Docling conversion/pdfplumber export/manual reference review/provider/LLM command is accepted by this gate.

## Next Entry

After accepted plan commit, next entry point is `FundDisclosureDocument S6-F Core Risk Candidate Selector Implementation Gate`.
