# Plan Review: Bond-Lens Contract + Baseline Coverage Recovery Plan

> **Reviewer**: AgentGLM
> **Review target**: `docs/reviews/release-maintenance-bond-lens-contract-baseline-coverage-plan-20260527.md`
> **Review date**: 2026-05-27
> **Truth sources**: `AGENTS.md`, `docs/design.md` v2.2, `docs/implementation-control.md` Startup Packet / Next Entry Point / Open Residuals / Active Gate Ledger
> **Evidence chain**: accepted baseline triage, share_change focused implementation, small baseline corpus v1

## Review Verdict

**PASS_WITH_FINDINGS**

5 findings, all informational or low severity. No blocking or material findings. No re-review required.

---

## Hard Constraint Compliance Matrix

| Hard constraint | Compliance | Evidence |
|---|---|---|
| No renderer changes | ✅ PASS | Plan §7 explicit forbid; Gate B/C/D/E/F allowed files exclude renderer |
| No FQ0-FQ6 weakening | ✅ PASS | Plan §7 + Gate B/C stop conditions explicitly block global FQ weakening |
| No Service/CLI changes | ✅ PASS | Plan §7 explicit forbid; Gate C test commands use existing CLI surface only |
| No Host/Agent/dayu | ✅ PASS | Plan §7 explicit forbid; no `dayu.host`/`dayu.engine` reference |
| No source strategy/helper | ✅ PASS | Plan §7 explicit forbid; Gate D uses only `FundDocumentRepository`-backed paths |
| No extractor logic changes | ✅ PASS | Plan §7 explicit forbid; Gate C scope is `extraction_score.py` (scoring module, not `fund_agent/fund/extractors/`) |
| No golden/baseline promotion | ✅ PASS | Plan §4.3 + §7 explicit forbid; no gate authorizes fixture promotion |
| No extra_payload | ✅ PASS | Plan §7 explicit forbid |
| No GitHub mutation | ✅ PASS | Plan §7 explicit forbid |
| No direct PDF/cache/source helper access | ✅ PASS | Plan §4.1 only `FundDocumentRepository`-backed paths; Gate F stop condition blocks direct access |
| No silent quality-gate weakening | ✅ PASS | Plan §3.5 failure behavior emits bond-specific issue instead of silent pass; Gate C stop condition catches evidence suppression |
| No QDII-FOF as pure FOF without taxonomy gate | ✅ PASS | Plan §4.2 explicit gate; `taxonomy_pending` classification; stop condition blocks |

---

## Review Question Checklist (per Plan §10)

### Q1: share_change reconciliation correctness

**PASS.** Plan §2 correctly reconciles two independent facts:
1. The `share_change` focused implementation was accepted because it improved deterministic A-Z share-class mapping with fail-closed ambiguity — verified against `holdings_share_change.py` line 27 `_SUPPORTED_SHARE_CLASS_LABELS` covering A-Z.
2. Real `006597` / 2024 remains quality-gate `block` because §10 still has share-class selection ambiguity — verified against implementation-control.md "real 006597 still lacks deterministic public evidence and remains missing."

Root-cause rule in §5 ("every future classification must be logic/data same-source") aligns with AGENTS.md §硬约束: "找问题的 root cause 一定要逻辑/数据同源，禁止使用间接证据."

### Q2: holdings_snapshot fund-type-dependent decision

**PASS.** Verified against current code:

- `extraction_score.py` `_record_is_covered()` (line ~1409) uses `TOP_HOLDINGS_COVERED_STATUS_SOURCE_PAIRS` requiring `("direct_top_ten", "top_ten")` or `("direct_all_stock_details", "all_stock_investment_details")` — these are equity-specific coverage semantics.
- `_scorable_records()` applies NO fund-type filter to `holdings_snapshot`; the only existing fund-type filter is `_is_non_applicable_index_quality_record()` for `index_profile`/`tracking_error`.
- `quality_gate.py` FQ4 (thresholds 0.20/0.35) applies uniformly with no fund-type differentiation.

Conclusion: requiring equity top-ten as P1 evidence for bond funds is a confirmed category error. The plan's decision to make `holdings_snapshot` fund-type-dependent is the correct first-principles response. Not marking as silent N/A is also correct — would hide bond risk evidence needs.

### Q3: bond_holdings_risk_evidence contract coverage

**PASS_WITH_FINDINGS.** The 6 evidence groups (duration/credit/leverage/liquidity/allocation/drawdown/redemption) cover the core bond-lens dimensions from design.md §5.4.3 (久期、信用、杠杆、流动性、回撤) and Chapter 4/6 core + Chapter 2/5 high priorities.

See Finding F2 for a minor gap in convertibility exposure.

### Q4: allowed_na_reason, failure behavior, issue taxonomy sufficiency

**PASS_WITH_FINDINGS.** The `allowed_na_reason` table is narrow and paired — every equity N/A must be accompanied by a bond replacement requirement. Failure behavior covers unknown type (fail closed), missing equity (don't count), missing bond evidence (emit issue), and source integrity (fail-closed). Issue taxonomy has 8 codes.

See Finding F3 for a minor taxonomy gap.

### Q5: Gate C FQ0-FQ6 preservation

**PASS.** Gate B stop condition: "plan would weaken FQ0-FQ6 globally." Gate C stop condition: "any non-bond fund field priority/coverage behavior changes unexpectedly" and "006597 becomes pass/warn only because evidence is suppressed without replacement bond issue."

The FQ4 denominator effect from excluding equity `holdings_snapshot` for bond funds is accounted for by the replacement bond issue requirement in Plan §8 step 5.

### Q6: turnover_rate and holder_structure as needs_more_evidence

**PASS.** Matches implementation-control.md residuals: "`006597` turnover_rate / holder_structure — future evidence or policy gate — Evidence remains `needs_more_evidence`; do not infer from missing public output or implement without accepted source/policy proof."

### Q7: investor_return and nav_data future work

**PASS.** Both classified as `score_contract_gap`, not bond N/A. Matches design.md §5.4.2 (nav_data excluded from initial facts projection) and implementation-control.md nav_data mapping residual.

### Q8: Source recovery fail-closed semantics

**PASS.** Plan §4.1 explicit: `not_found`/`unavailable` may fallback; `schema_drift`/`identity_mismatch`/`integrity_error` fail-closed. Stop conditions include fail-closed category, unverified identity, unknown fallback boundary, Eastmoney-only fetch. Matches AGENTS.md hard constraint and design.md §6.1 fallback table.

### Q9: FOF plan QDII-FOF exclusion

**PASS.** Verified against `classify_fund_type()` priority order: QDII check (priority 1) precedes FOF check (priority 4). A fund with both QDII and FOF keywords classifies as `qdii_fund`. Plan §4.2 correctly requires: pure FOF by stable disclosure, QDII-FOF as `taxonomy_pending`, data_gap if no pure FOF verified. Matches implementation-control.md FOF residual.

### Q10: File ranges, stop conditions, validation

**PASS_WITH_FINDINGS.** File ranges are narrow per gate. Stop conditions are specific and testable. Validation commands reference existing CLI surface. Gate C allowed files may need clarification — see Finding F4.

---

## Findings

### F1: Chapter 2 bond preferred_lens gap not addressed (Informational)

**Severity**: Informational

**Evidence**: `contracts.py` Chapter 2 (lines ~318-360) has no `bond_fund` preferred_lens entry; only `default` and `index_fund` exist. When `resolve_preferred_lens()` is called with `fund_type="bond_fund"` for Chapter 2, it falls back to `default`. Design.md §5.4.3 says Chapter 2 should be `high` priority for bond funds.

**Why not blocking**: The plan scopes itself to `holdings_snapshot` score applicability and baseline coverage recovery, not template lens design. Chapter 2 lens is a separate concern.

**Recommendation**: Record as a future residual for a bond-lens template/contract design gate. Do not expand this plan's scope.

### F2: Convertibility (转债) exposure missing from bond evidence groups (Low)

**Severity**: Low

**Evidence**: Plan §3.3 evidence groups cover duration, credit, leverage/liquidity, allocation/holdings mix, drawdown/stress, and redemption/share pressure. The template draft Chapter 1 bond lens (`contracts.py` line ~282) explicitly asks "是否有转债/股票仓位?" — convertibility exposure is a distinct risk factor for 二级债基/混合债基 and 偏债混合基金 (all three are `bond_fund` facets per the template).

Convertibility is partially covered by "Asset allocation / holdings mix" but that group is positioned as product-evidence (not risk-evidence) and doesn't emphasize the asymmetric risk profile of convertible bonds.

**Why not blocking**: The plan says "Minimum pass for future bond_holdings_risk_evidence should not require every group at once in the first implementation." Adding a convertibility subgroup is compatible with the incremental design approach.

**Recommendation**: In the next bond-lens implementation gate, consider adding a "Convertibility / equity exposure" subgroup under the evidence contract, specific to 二级债基/混合债基 facets. Current plan can proceed without this.

### F3: No taxonomy code for unknown/conflicted fund type (Informational)

**Severity**: Informational

**Evidence**: Plan §3.5 failure behavior says "If fund type is unknown or conflicted: fail closed, keep generic required fields." But the issue taxonomy in §3.6 has no code for this state. All 8 taxonomy codes assume the fund type is known.

**Why not blocking**: Unknown fund type is already handled conservatively by `_is_non_applicable_index_quality_record()` (keeps generic fields). The fail-closed behavior is well-specified even without a dedicated taxonomy code.

**Recommendation**: Consider adding `fund_type_unknown_or_conflicted` as a future taxonomy code if it becomes consumer-facing in later gates. Not needed for the current plan/design gate.

### F4: Gate C constant placement file scope (Informational)

**Severity**: Informational

**Evidence**: Plan §8 step 2 says "Add explicit constants for bond-specific applicability rather than string literals scattered through code." If these constants go in `extraction_score.py`, they're within Gate C allowed files. But canonical fund-type-related constants live in `fund_type.py` (per design.md §6.5 and the pattern of `INDEX_QUALITY_APPLICABLE_FUND_TYPES` in `extraction_score.py` lines ~123-126).

**Why not blocking**: The existing pattern in `extraction_score.py` already defines `INDEX_QUALITY_APPLICABLE_FUND_TYPES` locally (not in `fund_type.py`). Bond-specific constants can follow the same local pattern.

**Recommendation**: Implementation gate worker should decide at Gate C whether bond-applicability constants follow the existing local-constant pattern in `extraction_score.py` or are placed alongside `FundType` in `fund_type.py`. Either is acceptable; if `fund_type.py` is chosen, Gate C allowed files should be updated accordingly.

### F5: FQ4 denominator effect for 006597 not explicitly computed (Informational)

**Severity**: Informational

**Evidence**: 006597 / 2024 currently has missing-field rate 35.7% (above FQ4 block threshold of 35%). If `holdings_snapshot` equity subfields are excluded from the bond fund denominator, the missing-field count decreases by 1 while the total scorable fields also decrease by 1. The exact resulting rate depends on the implementation's denominator adjustment method.

The plan's Gate C stop condition explicitly catches the case where "006597 becomes pass/warn only because evidence is suppressed without replacement bond issue." Section 8 step 5 requires emitting a bond-specific issue for missing bond risk evidence.

**Why not blocking**: The stop condition and replacement-issue requirement are sufficient safeguards. The exact rate computation is an implementation detail for Gate C.

**Recommendation**: No plan change needed. Implementation worker should note the expected denominator change and verify the stop condition holds.

---

## Architecture Boundary Verification

| Boundary | Status | Evidence |
|---|---|---|
| Four-layer `UI -> Service -> Host -> Agent` | ✅ Preserved | Plan touches only Agent-layer scoring (`extraction_score.py`) and Agent-layer fund capability |
| `FundDocumentRepository` access | ✅ Preserved | All evidence paths use repository-backed public paths |
| Fund type before lens | ✅ Preserved | Plan §3.5 requires fund-type identification before applicability decision |
| Fail-closed source semantics | ✅ Preserved | Plan §3.5 and §4.1 preserve fail-closed for `schema_drift`/`identity_mismatch`/`integrity_error` |
| Evidence traceability | ✅ Preserved | Plan §3.6 taxonomy includes anchor-missing code; §3.3 requires annual-report provenance |

---

## Summary

The plan correctly diagnoses the equity-shaped `holdings_snapshot` scoring as a category error for bond funds and proposes a fund-type-dependent solution that neither silently passes missing evidence nor continues inappropriate equity requirements. The baseline coverage recovery plan preserves fail-closed source semantics and correctly excludes QDII-FOF from pure FOF coverage.

All 5 findings are informational or low severity. No re-review required. Controller may proceed to acceptance decision.

---

*Review completed by AgentGLM on 2026-05-27.*
