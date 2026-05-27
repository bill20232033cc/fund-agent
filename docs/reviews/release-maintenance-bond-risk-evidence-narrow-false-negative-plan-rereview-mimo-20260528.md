# Bond Risk Evidence Narrow False-Negative Plan — MiMo Re-Review

> Date: 2026-05-28
> Role: plan re-review worker MiMo
> Gate: `bond risk evidence narrow false-negative gate`
> Review type: re-review of amended plan after accepted first-round findings
> Status: complete

## Worker Self-Check

### Before Start

- Role confirmed: plan re-review worker only; not controller, not implementer.
- Truth sources read: amended plan (`release-maintenance-bond-risk-evidence-narrow-false-negative-plan-20260528.md`), plan-fix artifact (`release-maintenance-bond-risk-evidence-narrow-false-negative-plan-fix-20260528.md`), MiMo first-round review, DS first-round review.
- Branch: `codex/local-reconciliation`; no source modifications by this worker.

### Before Completion

- All P0/P1 findings from MiMo first-round review checked against amended plan.
- All mandatory findings from DS first-round review checked against amended plan.
- Hard constraints re-verified.

---

## Re-Review Summary

**Verdict: PASS**

All 7 MiMo findings and all 7 DS findings have been absorbed into the amended plan. The amendments are additive and tightening — no original constraint was weakened, no scope creep was introduced. The plan is code-generation ready.

---

## MiMo First-Round Findings Closure Check

| ID | Severity | Description | Closure Status | Evidence |
|---|---|---|---|---|
| F1 | P0 | fund-own-rating table false positive | CLOSED | Plan lines 139-140: explicit rejection of `本基金评级`, `基金评级信息`, `基金自身评级`, and `本基金` + `评级` without held-position qualifiers (`持有`/`持仓`/`证券`). Stop condition at line 261 requires revision if any fund-own-rating context match occurs. |
| F2 | P1 | multiple rating tables unspecified | CLOSED | Plan line 152: "retain anchors for all matching tables. Do not accept only the first table and discard the other anchors." Test `test_multiple_holding_rating_distribution_tables_preserve_all_anchors` at line 331. |
| F3 | P1 | metric_value format underspecified | CLOSED | Plan line 153: "summarize current-period values from the first representative matching table"; line 154: "Include `合计` in `metric_value` when present. Prior-period values are supplementary and may be included in anchor notes." |
| F4 | P0 | Decimal parsing contract gap | CLOSED | Dedicated "Share value parsing contract" section at lines 201-206: comma/whitespace stripping, dash variants as zero, `InvalidOperation` fail-closed with `na_reason="non_parseable_share_value"`, no custom precision. Tolerance `Decimal("0.01")` at line 193 and line 206. |
| F5 | P1 | A/C/E/F column alignment fragile | CLOSED | Plan line 182-183: §2 mapping or §10 header-label alignment, total column exclusion, count mismatch fails closed with `share_class_column_count_mismatch`. |
| F6 | P1 | F-class zero beginning edge case | CLOSED | Plan line 198: "if a class beginning is zero, set the class ratio to `None` and include note `class_beginning_zero`. This is not a failure for F 类期初 `-`; only aggregate beginning zero fails closed." |
| F7 | P1 | missing targeted import smoke | CLOSED | Validation commands at line 414: `uv run python -c "from fund_agent.fund.extractors.bond_risk_evidence import extract_bond_risk_evidence; print('import OK')"`. |

All 7 findings closed.

---

## DS First-Round Findings Closure Check

| ID | Severity | Description | Closure Status | Evidence |
|---|---|---|---|---|
| M1 | CRITICAL | async wrapper missing in validation command | CLOSED | Validation command at line 415 uses `asyncio.run(repo.load_annual_report(...))`. |
| M2 | MODERATE | extraction_mode partial vs estimated | CLOSED | Explicit decision at lines 103-105: "keep `extraction_mode=ExtractionMode.estimated` when `bond_risk_contract_status=partial`; the structured `bond_risk_contract_status` field remains authoritative." No schema change. |
| M3 | MODERATE | share table first-match problem | CLOSED | Lines 178-181: "Scan all parsed tables; do not return the first table matching..."; explicit rejection of financial-statement tables; "fail closed as `ambiguous` instead of guessing" on no unique best candidate. |
| M4 | MODERATE | rating table numeric shape too loose | CLOSED | Line 142: "Require numeric shape: at least one data row must have a recognized rating category label and a parseable current-period numeric amount. Tables with no numeric current-period amount, no row/table anchor, or fewer than two data rows must not be accepted." |
| A1 | LOW | Decimal tolerance unspecified | CLOSED | Tolerance `Decimal("0.01")` explicitly specified at line 193 and in the parsing contract at line 206. |
| A2 | LOW | missing §2 parsed mapping helper test | CLOSED | Test `test_share_class_evidence_from_section_two_table` at lines 344-346. |
| A3 | INFO | _trim_note reference | No action needed — helper exists in codebase. Confirmed. |

All 7 findings closed.

---

## Hard Constraints Re-Verification

| Constraint | Verdict | Evidence |
|---|---|---|
| credit_risk must not represent fund own rating | PASS | Detection rules (lines 136-144) reject fund-own-rating semantics; forbidden wording listed at lines 122-124; stop condition at line 261. |
| Annual-report rating distribution = held bond/security rating distribution | PASS | Contract decisions section (lines 109-125) explicitly scopes to portfolio exposure. |
| No fund_rating / ratings / fund_own_rating / 基金评级 / 本基金评级 | PASS | Forbidden list at line 123. |
| redemption_share_pressure aggregates A/C/E/F, not A-only | PASS | Lines 163-164: "Change from single-class selection to explicit all-class aggregation." Line 224: "Single-class A-only selection must not satisfy this group for `006597`." |
| A/C/E/F computation includes beginning/subscription/redemption/ending/net change/ratio/breakdown/anchors | PASS | Lines 186-198 specify all required rows and calculations. |
| Redemption aggregation fail-closed on class mapping/numeric parsing/row matching/class count/arithmetic mismatch | PASS | Line 291: "Fail closed to `ambiguous` for any missing class, missing row, non-parseable number, duplicate class mapping, column count mismatch, or arithmetic mismatch." |
| drawdown_stress remains weak | PASS | Lines 228-241: no implementation changes upgrade drawdown_stress; no NAV-derived calculation. |
| No FQ0-FQ6 weakening | PASS | Line 50. |
| No direct PDF/cache/source helper access | PASS | Line 51. |
| No schema/score/snapshot/gate changes | PASS | Lines 90-96 and 100-101. |

---

## Potential Implementation Risks (Non-Blocking)

These are not findings — they are notes for the implementation worker.

1. **Fund-own-rating pattern coverage**: The explicit rejections (`本基金评级`, `基金评级信息`, `基金自身评级`) and the broader `本基金` + `评级` without held-position qualifiers cover the known risk patterns. If an annual report uses a novel fund-rating phrasing not caught by these patterns, the stop condition at line 261 provides a safety net. Implementation should log which tables were rejected and why, to aid debugging.

2. **§10 table selection scoring**: The plan says "Score candidates and select the best §10 share-change table" (line 179) but does not define a numeric scoring rubric. This is acceptable — the implementation can use a simple preference ranking (§10 context > 基金份额 > other) as long as the rejection rules are enforced and the test `test_redemption_share_pressure_rejects_net_asset_statement_table` passes.

3. **Multiple rating tables metric_value**: The plan says `metric_value` summarizes "the first representative matching table" (line 153). "Representative" is intentionally vague — the implementation should prefer long-term over short-term ratings if both exist, as long-term is the more common analysis focus. This is a preference, not a requirement.

---

## Conclusion

The amended plan has fully absorbed all findings from both first-round reviews (MiMo: 2 P0 + 5 P1; DS: 4 mandatory + 3 advisory). No original constraints were weakened. The plan is well-bounded, implementable, and code-generation ready.

**Verdict: PASS** — no blocking findings; plan ready for implementation.

---

## Review Signature

- Reviewer: MiMo (plan re-review worker)
- Review type: re-review of amended plan after accepted first-round findings
- Artifact: `docs/reviews/release-maintenance-bond-risk-evidence-narrow-false-negative-plan-rereview-mimo-20260528.md`
- Verdict: **PASS** — all P0/P1 findings closed; plan is implementation-ready
