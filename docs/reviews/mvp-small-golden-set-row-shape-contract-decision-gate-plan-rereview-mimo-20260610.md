# MVP Small Golden Set Row-shape Contract Decision Gate Plan Re-Review — AgentMiMo

## Gate

- Review target: `docs/reviews/mvp-small-golden-set-row-shape-contract-decision-gate-plan-20260610.md`
- Prior review: `docs/reviews/mvp-small-golden-set-row-shape-contract-decision-gate-plan-review-mimo-20260610.md`
- Reviewer: AgentMiMo
- Date: 2026-06-10
- Role: targeted re-review only; check prior findings F1–F7 and scope regressions

## Scope

This re-review checks only whether the revised plan resolves the 7 findings from the prior MiMo review and whether the revision introduces material scope regressions. No broad re-review.

## Prior Findings Resolution

| Finding | Summary | Status | Evidence |
|---|---|---|---|
| F1 | 006597 risk dual-source anchor: contract said §2.2 only, but oracle anchor is §2.2 + §4.4.1 | **RESOLVED** | Contract 2 scope (line 150): "Most rows are anchored in `§2.2 基金产品说明`; `006597` is dual-source and also uses `§4.4.1`." Source anchor requirements (line 175): "additional sections when the retained oracle anchor names them; for `006597`, include `§4.4.1`." Per-fund table (line 194): "`PDF p5 §2.2 and p21 §4.4.1`; clause 1 from `§2.2` risk-return type, clause 2 from `§4.4.1` credit/liquidity risk control wording". |
| F2 | Plan dropped explicit two-reviewer requirement from 0609 plan | **RESOLVED** | New "Review Requirements" section (lines 19–26): "This heavy contract gate requires all of the following before any implementation or test gate may open: 1. Two independent plan reviews, one from AgentDS and one from AgentMiMo or equivalent independent reviewers. 2. Controller judgment that explicitly accepts, rejects or defers each review finding." |
| F3 | Manager `role_status` derivation ambiguity for 004194 departed manager | **RESOLVED** | New "Normalization Rules" section (lines 104–109). Line 108: "First manager failing-test gate should assert the retained oracle `role` string exactly, including `基金经理（已离任）` for `004194` 王平." Line 109: "`end_date` remains optional at the contract level, but when the retained oracle entry includes `end_date`, the first manager test gate should assert it for that entry." |
| F4 | Risk contract optional fields `special_risk_clauses` and `fund_type_risk_label` had no first-test guidance | **RESOLVED** | Line 168: "First test gate asserts only `schema_version`, `risk_characteristic_text` and source anchors. It must not assert `fund_type_risk_label` or `special_risk_clauses` unless a later reviewed contract revision enumerates their per-fund expected values." |
| F5 | Bond holding `rank` listed as required but oracle has no `rank` value | **RESOLVED** | Line 227: "`rank`: integer or string, only if the bond table explicitly discloses row order. The first same-source test must not assert rank because the retained oracle has no `rank` value." Moved to optional with explicit first-test guidance. |
| F6 | `StructuredFundDataBundle` wiring scope not bounded for four additive contracts | **RESOLVED** | Stop Conditions (line 405): "A future implementation slice would wire more than one additive contract into `StructuredFundDataBundle`." Prevents wiring more than one contract per slice. |
| F7 | Plan removed "Residual Owners" table from 0609 plan | **RESOLVED** | New "Residual Owners And Next Gates" table (lines 304–312) with explicit controller-owned next gate, owner role, and acceptance destination for each residual. |

## Scope Regression Check

| Change in revision | Regression? | Notes |
|---|---|---|
| Added "Review Requirements" section (lines 19–26) | No | Positive addition; restores heavy gate discipline |
| Contract 1: added "Normalization Rules" (lines 104–109) | No | Positive addition; clarifies role text and end_date assertion |
| Contract 2: expanded scope to mention dual-source (line 150) | No | Positive addition; resolves F1 |
| Contract 2: added per-fund expected table with source anchors (lines 190–196) | No | Positive addition; removes ambiguity |
| Contract 2: added first-test assertion guidance for optional fields (line 168) | No | Positive addition; resolves F4 |
| Contract 3: `rank` moved to optional with first-test guidance (line 227) | No | Positive change; resolves F5 |
| Added "Residual Owners And Next Gates" table (lines 304–312) | No | Positive addition; resolves F7 |
| Stop conditions: added bundle wiring constraint (line 405) | No | Positive addition; resolves F6 |
| No fields, contracts, non-goals, or boundaries removed | No | All original content preserved |

No material scope regressions detected. The revision is strictly additive/corrective.

## New Blockers

None.

## Residual Risks

| Risk | Severity | Tracking Destination |
|---|---|---|
| Risk text normalization strategy (exact match vs. clause extraction) deferred to implementation | Low | Contract review gate |
| `StructuredFundDataBundle` growth from four additive contracts (now bounded by stop condition) | Low | Implementation gates for each contract |

## Self-Check

- [x] Only prior findings F1–F7 checked
- [x] Scope regression check performed
- [x] No broad re-review opened
- [x] Output path uses system-clock timestamp

## Verdict: PASS

All 7 prior findings resolved. No new blockers. No scope regressions.
