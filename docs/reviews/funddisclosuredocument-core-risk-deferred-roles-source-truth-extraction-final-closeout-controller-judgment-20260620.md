# FundDisclosureDocument core_risk.v1 Deferred Risk Roles Source-truth Direct Extraction Final Closeout Controller Judgment

## Verdict

`ACCEPT_FINAL_CLOSEOUT`

Release/readiness remains `NOT_READY`.

## Scope

- Work unit: `FundDisclosureDocument core_risk.v1 Deferred Risk Roles Source-truth Direct Extraction`
- Gate: final closeout
- PR: 34
- PR URL: https://github.com/bill20232033cc/fund-agent/pull/34

## Accepted Evidence

- Plan accepted by `docs/reviews/funddisclosuredocument-core-risk-deferred-roles-source-truth-extraction-plan-controller-judgment-20260620.md`.
- Implementation/code-review/fix/re-review accepted by `docs/reviews/funddisclosuredocument-core-risk-deferred-roles-source-truth-extraction-code-review-controller-judgment-20260620.md`.
- Aggregate deepreview accepted by `docs/reviews/funddisclosuredocument-core-risk-deferred-roles-source-truth-extraction-aggregate-deepreview-controller-judgment-20260620.md`.
- Ready/push/draft-PR/PR-review/follow-up-push/draft-PR-pass gates are accepted by their controller judgments under `docs/reviews/`.
- Latest verified PR state: PR 34 is open/draft, base `funddisclosure-current-stage-source-truth`, head `funddisclosure-core-risk-source-truth`, head `9236e2d44ff65bb36f126b4de8ff97eb94397dc8`, CI `test` SUCCESS, merge state `CLEAN`.

## Accepted Behavior

- Proof-positive `core_risk.v1` direct extraction now emits all five required source-truth subvalues:
  - `risk_characteristic_text.v1`
  - `liquidation_or_scale_risk`
  - `tracking_error_or_deviation_risk`
  - `turnover_or_style_drift_risk`
  - `concentration_risk`
- The four role subvalues use `core_risk_role_disclosure.v1` with exactly five public keys: `schema_version`, `fund_code`, `report_year`, `role`, and `risk_disclosure_text`.
- Role subvalues do not embed `source_anchors`.
- Missing required role emits `field_family_partial`.
- Conflicting disclosure emits `ambiguous_table_or_locator`.
- `deferred_role` is no longer used.
- The explicit FDD facade route does not add `StructuredFundDataBundle.core_risk`; only the existing `risk_characteristic_text` fallback remains.

## Whole-objective Completion Audit

The active objective is: all FundDisclosureDocument source-truth direct extraction families implemented.

Current design/control/code evidence proves the six accepted FDD field families have proof-positive direct extraction:

- `product_essence.v1`
- `return_attribution.v1`
- `manager_profile.v1`
- `investor_experience.v1`
- `current_stage.v1`
- `core_risk.v1`

The accepted boundary remains narrower than readiness:

- `investor_experience.v1` public direct extraction covers `investor_return`, `holder_structure`, and `share_change`; `subscription_redemption` and `income_distribution` remain candidate locator roles only.
- `current_stage.v1` reuses existing public fact shapes and does not add bundle-level `current_stage`.
- `core_risk.v1` covers its five required public subvalues and does not add bundle-level `core_risk`.
- Candidate evidence remains candidate-only / not-proven / `NOT_READY`.

## Residual Risks And Owners

- Real-report field correctness remains unproven; owner: future field-correctness evidence gate.
- Full field correctness, golden/readiness and release remain unproven; owner: future readiness/release gate.
- Parser replacement remains unauthorized; owner: future parser/source strategy gate.
- PR mark-ready and merge remain user-directed external-state actions; owner: user/controller in a separate PR disposition gate.
- Local closeout bookkeeping commits after remote head `9236e2d44ff65bb36f126b4de8ff97eb94397dc8` are control-plane evidence only unless a future gate explicitly pushes them.

## Closeout Decision

This work unit is closed locally. The implementation objective "all family source-truth direct extraction implemented" is accepted at code/control/design evidence level while preserving `NOT_READY` and the non-goals above.

## Next Entry Point

`User-directed PR stack disposition or separate future reviewed gate`.
