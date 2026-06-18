# MVP Small Golden Set Row-shape Contract Decision Gate — Targeted Re-review (AgentDS)

## Re-review Metadata

- **Reviewer**: AgentDS
- **Date**: 2026-06-10
- **Reviewed artifact**: `docs/reviews/mvp-small-golden-set-row-shape-contract-decision-gate-plan-20260610.md` (revised)
- **Prior review**: `docs/reviews/mvp-small-golden-set-row-shape-contract-decision-gate-plan-review-ds-20260610.md`
- **Scope**: targeted re-review of DS F1-F4 resolution plus material scope regression check
- **Classification**: `heavy`
- **Re-review boundary**: no new broad review; no code/test/fixture/config/control/design modification; no live/network/PDF/FDR/fallback/provider/LLM

## Verdict

**PASS** — all 4 prior DS findings resolved, 0 new blockers, 0 regressions

## Resolved Findings

| # | Prior Severity | Issue | Resolution Evidence | Status |
|---|---------------|-------|---------------------|--------|
| F1 | Low | Contract 3 `rank` listed as required but conditionally available (self-contradictory). | `rank` moved from required (line 227) to optional fields with explicit constraint: "only if the bond table explicitly discloses row order. The first same-source test must not assert rank because the retained oracle has no `rank` value." Required fields (lines 219-223) now list only `code`, `name`, `fair_value_cny`, `net_asset_ratio`, `source_anchor`. | **RESOLVED** |
| F2 | Low | Contract 1 manager `role` normalization underspecified — oracle says "本基金的基金经理", expected said "基金经理" without rule. | New "Normalization Rules" section (lines 104-109): `role` explicitly defined as normalized (not verbatim), "本基金的" prefix stripped, departure semantics preserved, first test gate asserts normalized oracle string exactly. | **RESOLVED** |
| F3 | Low | Contract 2 `risk_characteristic_text` expected value for 006597 differed materially from oracle excerpt. | Lines 183-188: explicit normalization rule distinguishing oracle `expected` (assertion string) from oracle `excerpt` (source-clause evidence). Line 158: `risk_characteristic_text` must "exactly match retained oracle `fields.risk.expected`". Line 194: 006597 expected value confirmed matching oracle `fields.risk.expected`. Line 150: 006597 dual-source anchoring (§2.2 + §4.4.1) documented. Lines 167-168: first test gate scope narrowed to only schema_version, risk_characteristic_text, and source anchors. Verified: oracle expected = `债券型基金；较低预期风险和预期收益；操作中强调信用风险和流动性风险控制` matches plan line 194 exactly. | **RESOLVED** |
| F4 | Low | Contract 1 `source_anchor` row-level locator underspecified for multi-manager §4.1.2 sections. | Lines 121-125: multi-manager locator must include manager name, disclosure order within §4.1.2 for that fund, and stable section-relative row/paragraph or table-row locator when parser output exposes one. Line 119: locator must "distinguish each manager on a shared page." | **RESOLVED** |

## Scope Regression Check

The following revisions were introduced beyond F1-F4 fixes. Each reviewed for scope regression:

| Change | Location | Assessment |
|--------|----------|------------|
| New "Review Requirements" section | Lines 19-25 | Additive gate process requirement (two independent reviews, controller finding-by-finding judgment, controller boundary confirmation). Strengthens heavy gate without expanding runtime scope. No regression. |
| New "Residual Owners And Next Gates" table | Lines 304-312 | Assigns controller ownership for four failing-test gates and one implementation gate. Clarifies that controller assigns workers. Plan-only; no scope expansion. No regression. |
| Contract 2 dual-source anchoring for 006597 | Lines 150, 174-177, 194 | `§4.4.1` added as additional anchor source. Confirmed present in oracle `fields.risk.anchor`. More precise, not broader. No regression. |
| Contract 2 first test gate scope narrowed | Lines 167-168 | Excludes optional `fund_type_risk_label` and `special_risk_clauses` from first test gate. Scope narrowed, not expanded. No regression. |
| New stop condition: single-contract implementation per slice | Line 405 | "A future implementation slice would wire more than one additive contract into `StructuredFundDataBundle`." Reinforces one-contract-per-slice sequencing. Safety constraint, not regression. |
| `role` field description changed from "preserving retained role text" to "normalized retained role string" | Line 95 | Direct F2 fix. More precise semantics. No regression. |

No forbidden file lists expanded. No non-goals weakened. No live/source/fixture/golden/config boundary relaxed. No regression detected.

## Residual Risks After Revision

| Risk | Status |
|------|--------|
| Test assertion shapes may drift from oracle values if normalization rules aren't followed in next gate (prior risk) | **Mitigated**. F2 normalization rules are explicit; F3 distinguishes expected from excerpt. Reviewer in failing-test gate has clear contract to cross-check. |
| `rank` field ambiguity causing test churn (prior risk) | **Resolved**. `rank` is now optional with explicit non-assertion rule. |
| Multi-manager locator ambiguity (prior risk) | **Mitigated**. F4 locator semantics now require name + disclosure order + stable locator. |
| Contract 2 optional fields (`fund_type_risk_label`, `special_risk_clauses`) lack per-fund expected values | **Accepted**. Lines 167-168 explicitly defer optional fields beyond first test gate. No assertion will be written without a later reviewed contract revision. Low residual risk. |

## Reviewer Closeout

- **Artifact path**: `docs/reviews/mvp-small-golden-set-row-shape-contract-decision-gate-plan-rereview-ds-20260610.md`
- **Verdict**: PASS
- **Blocker count**: 0
- **Prior findings resolved**: 4 of 4
- **New findings**: 0
- **Regressions**: 0
