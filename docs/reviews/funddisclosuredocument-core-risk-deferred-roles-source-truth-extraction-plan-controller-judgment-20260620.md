# FundDisclosureDocument core_risk.v1 Deferred Risk Roles Source-truth Direct Extraction Plan Controller Judgment

## Verdict

`ACCEPT_PLAN_READY_FOR_IMPLEMENTATION_NOT_READY`

Release/readiness remains `NOT_READY`.

## Work Unit

`FundDisclosureDocument core_risk.v1 Deferred Risk Roles Source-truth Direct Extraction`

## Inputs

- Plan artifact: `docs/reviews/funddisclosuredocument-core-risk-deferred-roles-source-truth-extraction-plan-20260620.md`
- Initial plan reviews:
  - `docs/reviews/plan-review-20260620-180450.md`
  - `docs/reviews/plan-review-20260620-180757.md`
- Targeted plan re-reviews:
  - `docs/reviews/plan-review-20260620-181720.md`
  - `docs/reviews/plan-review-20260620-181754.md`
- Prior closeout input: `docs/reviews/funddisclosuredocument-core-risk-source-truth-extraction-final-closeout-controller-judgment-20260620.md`

## Controller Judgment

The fixed plan is accepted as code-generation-ready for the next implementation gate.

Accepted scope:

- Promote the four previously deferred `core_risk.v1` roles into proof-positive public field-family subvalues when source-truth admission and direct disclosure selection both pass:
  - `liquidation_or_scale_risk`
  - `tracking_error_or_deviation_risk`
  - `turnover_or_style_drift_risk`
  - `concentration_risk`
- Keep these values inside `core_risk.v1` field-family public value only.
- Do not add `StructuredFundDataBundle.core_risk`.
- Keep explicit FDD facade projection limited to the existing `risk_characteristic_text` fallback.
- Remove source-truth-path `deferred_role` gaps and use valid gap/status semantics: `accepted`, `partial`, `missing`, `field_family_partial`, `field_family_missing`, and `ambiguous_table_or_locator`.
- Keep role subvalues anchor-free; public anchors remain only in `FundFieldFamilyResult.anchors`.

## Finding Disposition

| Finding | Source | Controller disposition | Outcome |
|---|---|---|---|
| Resolver algorithm underspecified | DS / MiMo | accepted | Plan now specifies duplicate handling, paragraph-vs-cell ambiguity, normalized text equality, and `ambiguous_table_or_locator` emission |
| Source-truth role boundary not code-mappable | DS / MiMo | accepted | Plan now specifies paragraph, table/cell, guard-context, heading-only, placeholder, and substantive disclosure rules |
| Role subvalue anchor duplication | DS | accepted | Plan now removes `source_anchors` from role subvalue shape and relies on `FundFieldFamilyResult.anchors` |
| Candidate union/signature dispatch underspecified | DS / MiMo | accepted | Plan now specifies `_CoreRiskValueCandidate` union, affected signatures, and dispatch-by-type rules |
| `core_risk_role_disclosure.v1` schema location unspecified | MiMo | accepted | Plan now treats it as a processor-local builder contract, not a new `contracts.py` schema |
| Status semantics test impact incomplete | MiMo | accepted | Plan now requires grep/update of all risk-text-only accepted/exact-shape assertions and names minimum tests |
| Role output path naming underspecified | DS / MiMo | accepted | Plan now uses role key as role output path and specifies role-aware `row_locator` format |

Targeted re-review result:

- DS: `PASS`, blocker count `0`
- MiMo: `PASS`, blocker count `0`

## Boundaries

Not accepted in this plan:

- Parser replacement.
- Real-report field correctness.
- Full field correctness.
- `EvidenceSourceKind` / public `EvidenceAnchor` expansion.
- `StructuredFundDataBundle.core_risk`.
- Repository/source/fallback/cache/PDF/live/provider/LLM behavior change.
- Direct Service/UI/Host/renderer/quality-gate/LLM prompt consumption of FDD candidates.
- PR 34 mutation, mark-ready, merge, release or readiness transition.

## Validation

- Plan fix static check reported by AgentCodex: `git diff --check -- docs/reviews/funddisclosuredocument-core-risk-deferred-roles-source-truth-extraction-plan-20260620.md` passed with no output.
- Controller will run `git diff --check` over accepted plan/review/controller artifacts before commit.

## Next Gate

After this accepted plan commit is created, the next entry point is:

`FundDisclosureDocument core_risk.v1 Deferred Risk Roles Source-truth Direct Extraction Implementation Gate`

Implementation must stay within the accepted plan write set and stop after implementation evidence. It must not enter code review, aggregate deepreview, PR mutation, readiness/release, parser replacement, or live/source acquisition.
