# 004393 Field-family Correctness Pilot Plan Controller Judgment - 2026-06-15

Gate: `004393 Field-family Correctness Pilot Planning Gate`
Role: controller
Release/readiness: `NOT_READY`

## 1. Scope

This judgment closes plan review for a bounded field-family correctness pilot using accepted `004393_2025` current-envelope candidate artifacts.

Reviewed plan:

- `docs/reviews/docling-baseline-qualification-004393-field-family-correctness-pilot-plan-20260615.md`

Review inputs:

- `docs/reviews/docling-baseline-qualification-004393-field-family-correctness-pilot-plan-review-ds-20260615.md`
- `docs/reviews/docling-baseline-qualification-004393-field-family-correctness-pilot-plan-review-mimo-20260615.md`

## 2. Accepted Planning Facts

- Correctness must be judged against same-source annual-report evidence, not parser-vs-parser agreement.
- Future evidence must access the source annual report through `FundDocumentRepository`.
- Field families are bounded to:
  - `fund_identity_profile`
  - `product_contract_profile`
  - `performance_indicators`
  - `expense_costs`
  - `portfolio_structure`
  - `manager_alignment`
- Pilot size is capped at 25 reviewed facts, with 3-5 facts per family.
- Long-text `partial_match` requires minimum `reference_excerpt` and `candidate_excerpt`, not broad semantic paraphrase.
- EID HTML remains blocked/deferred and is not part of correctness comparison.

## 3. Review Disposition

| Finding | Source | Disposition | Reason |
| --- | --- | --- | --- |
| Long-text partial match could become subjective. | DS review | ACCEPT_FIXED | Plan now requires minimum source/candidate excerpts for long-text partial match. |
| Future evidence must spell out exact repository-loaded excerpt command and artifact paths. | MiMo review | ACCEPT_AS_EVIDENCE_REQUIREMENT | Evidence gate must record exact commands and output paths. |
| Pilot scope is bounded and appropriate. | DS + MiMo reviews | ACCEPT | Family and fact caps prevent full-report audit creep. |
| Non-proof boundaries are preserved. | DS + MiMo reviews | ACCEPT | Plan does not authorize correctness evidence execution, production integration, parser replacement, readiness, release, or PR. |

## 4. Accepted Evidence-gate Requirements

The next evidence gate must:

- use accepted `004393_2025` current-envelope candidate artifacts;
- use same-source annual-report evidence;
- access annual report through `FundDocumentRepository`;
- record exact reference facts, candidate facts, locators, excerpts, match status, and mismatch type;
- remain within the 25-fact cap;
- stop if repository access or locator resolution fails;
- preserve `NOT_READY`;
- avoid production repository/source/parser behavior changes.

## 5. Validation

Command:

```text
git diff --check
```

Result:

```text
PASS
```

## 6. Final Verdict

`VERDICT: ACCEPT_PLAN_READY_FOR_004393_FIELD_FAMILY_CORRECTNESS_PILOT_EVIDENCE_GATE_NOT_READY`

Next gate:

`004393 Field-family Correctness Pilot Evidence Gate`

Do not proceed to production integration, parser replacement, readiness, release, PR, or EID HTML table-bearing mapping from this plan.
