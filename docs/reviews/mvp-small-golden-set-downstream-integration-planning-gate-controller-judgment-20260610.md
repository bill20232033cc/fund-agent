# Controller Judgment: small golden set downstream integration planning gate

## Judgment

Accepted as planning artifact.

## Basis

- User explicitly authorized downstream integration planning first, with EID failure-branch evidence planning later.
- Current control truth names downstream integration planning as a valid next entry.
- The plan is code-generation-ready for later implementation gates and preserves source/fallback/provider/runtime/golden/readiness boundaries.
- Plan review reports no blocking findings.

## Accepted Planning Decisions

- `portfolio_managers` and `risk_characteristic_text` should be added as explicit `StructuredFundDataBundle` fields in a later implementation gate.
- `bond_top_holdings` and `target_fund_holdings` should remain sub-shapes of `holdings_snapshot`, not duplicated as top-level bundle fields.
- Later implementation should proceed in slices:
  - Slice A: bundle fan-in for manager/risk.
  - Slice B: snapshot and report evidence projection.
  - Slice C: chapter facts and evidence availability.
  - Slice D: docs/control sync.

## Preserved Boundaries

- No production code change in this planning gate.
- No PDF/source/repository/FDR/fallback/network/live LLM/provider/runtime/config behavior.
- No fixture projection, golden/readiness promotion, renderer/checklist/quality/score-loop change or Service/Host/Agent runtime expansion.

## Next Entry

Per user ordering, the next planning topic after this checkpoint is `EID failure-branch evidence planning`, unless the user redirects to downstream implementation first.
