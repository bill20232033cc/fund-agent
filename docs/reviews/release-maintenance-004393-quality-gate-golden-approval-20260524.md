# Release Maintenance 004393 Quality Gate Golden Approval Decision - 2026-05-24

## Gate

- Current phase: `release maintenance`
- Current gate: `release-maintenance 004393 S4 golden approval decision`
- Work unit: `004393/2024 quality gate block root-cause investigation`
- Prerequisites:
  - S0 evidence accepted: `docs/reviews/release-maintenance-004393-quality-gate-evidence-controller-judgment-20260524.md`
  - S1 accepted: `docs/reviews/release-maintenance-004393-quality-gate-s1-rereview-controller-judgment-20260524.md`
  - S2 accepted: `docs/reviews/release-maintenance-004393-quality-gate-s2-rereview-controller-judgment-20260524.md`
- Controller conclusion: `no golden changes approved`

## Decision

No row-level golden answer edits are approved for this gate.

## Row-Level Approval Table

| Fund | Field | Subfield | Current value | New value | Evidence locator | Decision |
|---|---|---|---|---|---|---|
| `004393` | `fee_schedule` | `management_fee` | skipped | n/a | S0 confirmed `7.4.10.2.1` `1.20%` | Not approved in S4; `fee_schedule` is not currently a comparable snapshot subfield, so golden edit would not affect correctness without expanding snapshot schema. |
| `004393` | `fee_schedule` | `custody_fee` | skipped | n/a | S0 confirmed `7.4.10.2.2` `0.20%` | Not approved in S4; same reason as `management_fee`. |
| `004393` | `benchmark` | `benchmark_name` | `沪深300指数收益率×60%+恒生指数收益率（经汇率调整后）×20%+中债综 合（全价）指数收益率×20%` | n/a | S0 confirmed newline/visual whitespace only | Not approved in S4; S2 field-aware correctness normalization already handles `中债综 合` vs `中债综合` for benchmark fields. |
| `004393` | `holdings_snapshot` | `top_holdings_status` | skipped | n/a | S2 extractor/score now exposes status/source | Not approved in S4; holdings golden expansion is deferred by the accepted plan unless explicitly row-approved. |
| `004393` | `holdings_snapshot` | `top_holdings_source` | skipped | n/a | S2 extractor/score now exposes status/source | Not approved in S4; same reason as `top_holdings_status`. |
| `004393` | `turnover_rate` | any | skipped | n/a | S0 did not observe direct disclosure | Not approved in S4; turnover applicability remains a future policy/schema/gate-denominator candidate. |

## Rationale

- Golden changes are not required to verify the S1/S2 extractor and correctness-normalization fixes.
- `fee_schedule` values are now extracted, but `fee_schedule` is not currently in `COMPARABLE_SUB_FIELDS_BY_FIELD`; changing golden rows alone would not create a meaningful correctness assertion and would expand S4 beyond a row edit into snapshot schema policy.
- `benchmark` visual whitespace is already handled in correctness comparison for benchmark fields only; changing the golden value would be cosmetic and not necessary for gate resolution.
- `holdings_snapshot` status/source are newly comparable in snapshot/score, but the accepted plan explicitly makes holdings golden expansion deferred by default unless a row-level approval lists exact rows. This artifact does not approve those rows.
- `turnover_rate` must not be added or marked applicable in this work unit.

## Allowed Files For This Decision

- This approval decision artifact only.

## Explicit Non-Goals

- No `reports/golden-answers/` edits.
- No strict JSON rebuild.
- No source/test/config/runtime changes.
- No turnover applicability, denominator, or derived proxy changes.

## Next Action

Proceed to `release-maintenance 004393 S5 end-to-end quality gate verification`.
