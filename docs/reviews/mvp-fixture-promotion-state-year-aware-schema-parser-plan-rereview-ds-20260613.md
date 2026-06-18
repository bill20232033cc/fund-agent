# Targeted Re-review: Amendment A/B/C Verification

Date: 2026-06-13

Gate: `Fixture Promotion State Year-aware Schema / Parser Plan Review Gate` (re-review)

Role: plan review worker (AgentDS), not controller

Reviewed artifact: `docs/reviews/mvp-fixture-promotion-state-year-aware-schema-parser-plan-20260613.md` (amended)

Reference: DS review `docs/reviews/mvp-fixture-promotion-state-year-aware-schema-parser-plan-review-ds-20260613.md` Amendments A/B/C

Verdict: `PASS`

## 1. Re-review Scope

Targeted re-review: verify only that Amendments A, B, C from the DS review have been
correctly applied to the amended plan. No new findings, no implementation, no
source/test/runtime/golden/fixture/control/design doc modifications.

## 2. Amendment Verification

### Amendment A: `promotion_identity` rationale + wrong_identity test

| Requirement | Location | Status |
|---|---|---|
| Rationale for `promotion_identity` field added to §6.1 | Plan lines 140-144 | `PASS` — exact wording matches DS review A1 recommendation |
| New test `test_preflight_rejects_year_aware_fixture_promotion_wrong_identity` in §8.2 | Plan lines 323-326 | `PASS` — asserts ValueError on `promotion_identity: "fund_code_only"` |
| Controller chose A1 (keep) over A2 (remove) | Plan §6.1 retains `promotion_identity` as required field | Confirmed |

### Amendment B: Explicit state/promotion_state/blocker mapping table

| Requirement | Location | Status |
|---|---|---|
| Table with `state` output column | Plan lines 190-196 | `PASS` |
| Table with `promotion_state` output column | Plan lines 190-196 | `PASS` |
| Table with blocker code column | Plan lines 190-196 | `PASS` |
| Five conditions covered: promoted_fixture, not_promoted, unknown, legacy exists, no legacy | Plan lines 190-196 | `PASS` |
| Legacy row: state=`legacy_fund_only`, promotion_state=`unknown`, blocker=`fixture_promotion_legacy_fund_only` | Plan line 195 | `PASS` — matches DS review recommendation |

### Amendment C: Explicit type reference changes + exclude `_derive_strict_golden_coverage`

| Requirement | Location | Status |
|---|---|---|
| `run_golden_readiness_preflight()` local `fixture_states` listed | Plan line 264 | `PASS` |
| `_build_readiness_row()` parameter `fixture_states` listed | Plan line 265 | `PASS` |
| `_derive_fixture_promotion_state()` parameter `fixture_states` and internal lookup listed | Plan lines 266-267 | `PASS` |
| Explicit exclusion: "Do not change `_derive_strict_golden_coverage()`" | Plan line 268 | `PASS` |

## 3. Disposition

All three amendments (A, B, C) are correctly applied. No new issues identified.

The plan is fit to enter controller judgment for routing to a narrow implementation gate.

## 4. Self-Check

- Role: plan review worker (AgentDS), targeted re-review only. Not controller.
- Scope: only Amendment A/B/C verification. No new review scope.
- Write: only this re-review artifact. No other files modified.
- Stop: plan is ready for controller judgment. Do not enter implementation.

Self-check: pass
