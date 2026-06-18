# MVP Small Golden Set Row-shape Contract Decision Gate — Plan Review (AgentDS)

## Review Metadata

- **Reviewer**: AgentDS
- **Date**: 2026-06-10
- **Reviewed artifact**: `docs/reviews/mvp-small-golden-set-row-shape-contract-decision-gate-plan-20260610.md`
- **Gate**: `row-shape contract decision gate for retained manager / risk / non-equity holdings residuals`
- **Classification**: `heavy`
- **Review scope**: adversarial plan review only; no code/test/fixture/config modification

## Verdict

**PASS_WITH_FINDINGS** — 4 findings, 0 blockers

The plan correctly separates current code facts from future contracts, defines four additive row-shape contracts with explicit shapes and oracle mappings, consistently rejects the `style_positioning` shortcut for retained risk, mandates separate holding sub-shapes for stock/bond/target-fund, pins the same-source oracle, enforces failing-tests-before-fixes sequencing, and maintains comprehensive no-live/no-source/no-fixture/no-golden/no-config boundaries. All findings below are precision improvements to the contract definitions; none block acceptance.

## Evidence Base

- Plan artifact: `docs/reviews/mvp-small-golden-set-row-shape-contract-decision-gate-plan-20260610.md`
- Same-source oracle: `docs/reviews/mvp-small-golden-set-retained-excerpt-fixture-pdf-only-20260609.json` (verified exists, all referenced field paths present)
- Current extractor code: `fund_agent/fund/extractors/manager_ownership.py`, `profile.py`, `holdings_share_change.py`, `models.py` (verified against plan's surface claims)
- Design truth: `docs/design.md` v2.14
- Implementation control: `docs/implementation-control.md` v2.6
- AGENTS.md

## Findings

| # | Severity | Issue | Evidence | Recommendation |
|---|----------|-------|----------|----------------|
| F1 | Low | Contract 3 `bond_top_holding_row.v1` lists `rank` as required field, but spec says "first test may assert rank `1` only if table exposes it" (line 192). A required field gated on table disclosure is self-contradictory. | Plan lines 190-192: `rank` in required fields list; line 192: conditional disclosure guard. | Move `rank` to optional fields for `bond_top_holding_row.v1`, consistent with Contract 4 `target_fund_holding_row.v1` where `rank` is already optional (line 251). |
| F2 | Low | Contract 1 manager `role` normalization is underspecified. Oracle excerpt for 004393 says "本基金的基金经理" but expected role is "基金经理" (plan line 114). The plan says to "preserve retained role text" (line 87) but the expected table already normalizes away "本基金的". | Plan line 87: "preserving retained role text such as `基金经理` or `基金经理（已离任）`"; Oracle line 60: excerpt says "本基金的基金经理"; Plan line 114: expected role is "基金经理". | Clarify whether role is verbatim from §4.1.2 or normalized. If normalized, define the normalization rule (e.g., strip "本基金的" prefix). If verbatim, fix expected table entry for 004393. |
| F3 | Low | Contract 2 `risk_characteristic_text` expected value for 006597 (line 165) says "操作中强调信用风险和流动性风险控制" but the retained oracle excerpt (oracle line 279) says "严控组合信用风险和流动性风险". The two phrasings differ materially. | Plan line 165: expected = "操作中强调信用风险和流动性风险控制"; Oracle line 279: excerpt = "严控组合信用风险和流动性风险". | The plan's expected text must match the oracle excerpt verbatim, or the plan must explicitly document that the expected value is a derived/normalized form and define the derivation rule. For same-source failing tests, the assertion oracle should be the retained excerpt, not a rephrased version. |
| F4 | Low | Contract 1 `source_anchor` row-level locator is underspecified for multi-manager pages. For 004194 (2 managers on same page range), 006597 (2 managers), and 110020 (2 managers), the anchor requirement says "row-level locator containing the manager name" (line 104) but doesn't specify whether the locator is a paragraph offset, a section-relative paragraph index, or just the manager name substring. | Plan line 104: "row-level locator containing the manager name"; Oracle lines 147, 234, 322: multi-manager excerpts with distinct manager entries on shared page ranges. | Define row-level locator semantics for multi-manager §4.1.2 sections: at minimum, specify whether locator must distinguish between managers on the same page (e.g., paragraph ordinal, name-anchored position, or disclosure order). |

## Verification by Required Lens

### Lens 1: Current facts separated from future contracts — PASS

The plan cleanly partitions:
- "Accepted Facts" (lines 22-38): current code/control facts, including accepted test results (37 passed, 4 xfailed)
- "Current Extractor Surface Facts" (lines 40-46): verified against actual extractor code — all claims confirmed
- "Not Current Facts" (lines 48-52): explicit statement that contracts are not implemented
- "Decision Summary" (line 56): "Accept four future row-shape contracts for later gates"

No future contract is presented as current code fact.

### Lens 2: Contract exactness for later tests — PASS_WITH_FINDINGS

All four contracts define:
- Explicit contract name/version
- Required field names and types
- Source anchor requirements with section, page, and row-level locator
- Expected oracle mappings keyed to specific fund codes
- Sufficiency decisions explaining why current surfaces are insufficient

See F1-F4 for precision improvements. No contract is so underspecified that a later test gate could not write a failing assertion.

### Lens 3: style_positioning not misused for retained risk — PASS

The plan consistently rejects the `style_positioning` shortcut:
- Line 44: accepted gap decision documented
- Line 61 (decision table): "do not use `style_positioning`"
- Line 131: "preferably `risk_characteristics`, not `style_positioning`"
- Lines 154-155: anchor must not use `product_profile.style_positioning` as semantic substitute
- Lines 170-171: explicit sufficiency rationale
- Line 364 (stop condition): assertion must not use `style_positioning` as retained risk oracle

Verified against code: `style_positioning` is indeed populated from `风险收益特征` label (profile.py lines 45-54, table labels line 71). The plan's rejection of this mapping is correct and consistently applied.

### Lens 4: No ambiguous shared holdings schema — PASS

The plan mandates separate holding sub-shapes:
- Contract 3: `bond_top_holdings` — not `top_holdings`
- Contract 4: `target_fund_holdings` — not `top_holdings`
- Line 224: explicit rationale against shared stock/bond/target-fund semantics
- Stop condition line 365: enforced

Verified against code: current `top_holdings` is stock-only with stock-specific table header matching (holdings_share_change.py lines 496-499, keyword matching for 前十大/重仓/股票代码). The plan's separation is correct.

### Lens 5: Same-source oracle — PASS

The plan references only one oracle: `docs/reviews/mvp-small-golden-set-retained-excerpt-fixture-pdf-only-20260609.json` (line 24, line 361). All expected values in the four contracts map to existing paths in this oracle file. The oracle's `retention_boundary` (oracle lines 20-24) explicitly scopes usage to "row-field extractor correctness tests" with "extractor fixes remain a later gate after same-source failing tests."

### Lens 6: Implementation sequencing — PASS

The plan enforces:
- Failing same-source tests before any extractor fix (line 304)
- Separate gates for each of the four contracts (lines 328-339)
- Stop conditions if tests need non-oracle sources, live PDF, network, or FDR (lines 360-363)
- Forbidden files for test gate and fix gate distinctly listed (lines 287-301, 315-324)

Sequencing is ordered (line 340): manager → risk → bond → target ETF. Rationale is defensible: manager has no equivalent surface at all (highest priority), risk rejects the tempting `style_positioning` shortcut, then bond and target ETF are holding sub-shapes.

### Lens 7: No-live/no-source/no-fixture/no-golden/no-config boundaries — PASS

All boundaries are enforced through multiple mechanisms:
- "Explicit Non-goals" (lines 370-385): 15 items
- "No-live Validation Matrix" (lines 342-354): no network, PDF, FDR, fallback, live LLM, fixture projection, golden/readiness
- Forbidden files for each gate phase
- Stop conditions (lines 356-368): 9 conditions covering source, live, fixture, schema, and state boundaries

## Residual Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Test assertion shapes may drift from oracle values if normalization rules aren't pinned before the failing-test gate. | Medium | Low | F2, F3 above; reviewer in next gate should cross-check assertions against oracle excerpts. |
| `bond_top_holding_row.v1` `rank` field ambiguity could cause test assertion churn if different bond tables disclose rank differently. | Low | Low | F1 above; move to optional before failing-test gate. |
| Multi-manager row-level locator ambiguity (F4) could cause per-manager anchor imprecision in later audit checks. | Low | Medium | Define locator semantics before the manager failing-test gate writes assertions. |

## Required Changes Before Acceptance

None. All four findings are precision improvements recommended for the next gate (same-source failing test gate), not blockers for this contract decision gate. The plan's contracts are exact enough to proceed.

## Reviewer Closeout

- **Artifact path**: `docs/reviews/mvp-small-golden-set-row-shape-contract-decision-gate-plan-review-ds-20260610.md`
- **Verdict**: PASS_WITH_FINDINGS
- **Blocker count**: 0
- **Finding count**: 4 (all Low severity)
