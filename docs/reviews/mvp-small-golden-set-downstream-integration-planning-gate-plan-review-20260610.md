# Plan Review: small golden set downstream integration planning gate

## Verdict

Pass with one non-blocking constraint.

## Findings

None blocking.

## Non-Blocking Constraint

The implementation should not add `bond_top_holdings` or `target_fund_holdings` as top-level `StructuredFundDataBundle` fields. They are already semantically part of `holdings_snapshot`; duplicating them would create two truth locations for the same holding rows.

## Review Notes

- The plan correctly distinguishes top-level missing bundle fields (`portfolio_managers`, `risk_characteristic_text`) from existing holdings sub-shapes (`bond_top_holdings`, `target_fund_holdings`).
- The plan keeps renderer, checklist, quality gate, score-loop, fixture projection and golden/readiness out of scope.
- The validation matrix covers bundle, snapshot, report evidence, chapter facts, evidence availability and retained extractor correctness.
- The planned order is implementable: bundle fan-in first, then projections.

## Residual Risk

Adding comparable subfields for holdings sub-shapes must remain descriptive only. It must not be consumed as a correctness/golden or quality-gate signal without a separate accepted gate.
