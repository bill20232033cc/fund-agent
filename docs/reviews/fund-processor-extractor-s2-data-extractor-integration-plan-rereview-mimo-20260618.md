# Fund Processor/Extractor S2 DataExtractor Integration Plan Re-Review — AgentMiMo

> Date: 2026-06-18
> Reviewer: AgentMiMo independent adversarial plan re-reviewer
> Plan artifact: `docs/reviews/fund-processor-extractor-s2-data-extractor-integration-plan-20260618.md`
> Fix evidence: `docs/reviews/fund-processor-extractor-s2-data-extractor-integration-plan-fix-evidence-20260618.md`
> Gate: S2 plan re-review gate after plan fix
> Review type: re-review only; read-only; no code implementation

## Verdict

**PASS_NOT_READY**

Fixed plan is code-generation-ready. All 6 controller-specified fix requirements are adequately addressed. MiMo prior blocking findings F1 and F2 are closed. DS nonblocking findings are adequately addressed or residualized. No new boundary violation, overreach, contradiction, or under-specified implementation decision was introduced by the fix.

---

## Finding Disposition Table

### MiMo Prior Blocking Findings

| Finding | Description | Disposition | Evidence |
|---------|-------------|-------------|----------|
| F1 (blocking) | `core_risk.v1` fallback projection rules for non-`risk_characteristic_text` fields under-specified | **CLOSED** | Plan lines 121-123 now explicitly specify: only `risk_characteristic_text` may fallback (when `product_essence.v1` extraction_mode is `"missing"` and `core_risk.v1` has public value); `holder_structure`, `turnover_rate`, `holdings_snapshot`, `tracking_error` are explicitly marked informational/redundant and must not be merged into bundle fields. |
| F2 (blocking) | Processor `extract()` unexpected exception propagation contract not explicit | **CLOSED** | Plan line 162 now specifies: unexpected exceptions (`TypeError`, `KeyError`, `AttributeError`) must propagate or be converted to typed fail-closed error; must not be silently swallowed; must not fallback to direct extractor path for active_fund. |

### MiMo Prior Nonblocking Findings

| Finding | Description | Disposition | Evidence |
|---------|-------------|-------------|----------|
| F3 (nonblocking) | `current_stage.v1` family-to-bundle projection implicit | **CLOSED** | Plan lines 124-125 now explicitly mark `current_stage.v1` as informational/redundant; S2 does not project bundle fields from it. |
| F4 (nonblocking) | `_classified_fund_type()` returning `None` implicit residual | **RESIDUALIZED** | Plan line 147 lists "unclassified fund type" as one of the types using direct legacy path; behavior is correct (falls through to direct path). No blocking change needed. |
| F5 (nonblocking) | `source_kind` derivation from `PublicSourceProvenance` underspecified | **CLOSED** | Plan line 85 now specifies deterministic static value `"annual_report"`; explicitly forbids derivation from candidate status, `PublicSourceProvenance.selected_source`, or fallback status. |

### DS Prior Nonblocking Findings

| Finding | Description | Disposition | Evidence |
|---------|-------------|-------------|----------|
| DS-F1 (nonblocking) | Dispatch key `source_kind` derivation underspecified | **CLOSED** | Same fix as MiMo F5: deterministic `"annual_report"`. |
| DS-F2 (nonblocking) | `_tracking_error_for_fund_type()` facade-level filtering interaction rule | **NOT CHANGED** (acceptable) | Plan line 110 retains "仍必须经过 `_tracking_error_for_fund_type()`". DS correctly identified this as processor output being post-processed by facade, which is the intended design (processor does not make fund-type strategy decisions). Fix did not need to change this. |
| DS-F3 (nonblocking) | Bootstrap classification vs processor internal consistency not verified | **NOT CHANGED** (acceptable) | Plan still acknowledges the duplication as a short-term residual (line 235). Both paths consume same in-memory `ParsedAnnualReport`; deterministic extractor guarantees consistency. S3 precomputed context will eliminate. |
| DS-F4 (nonblocking) | Field family value dict to individual ExtractedField projection detail left to implementation | **NOT CHANGED** (acceptable) | Plan lines 131-136 specify anchor allocation strategy: "使用该 `FundFieldFamilyResult.anchors`". This is a reasonable whole-family-to-each-field strategy that implementation worker can follow. |
| DS-F5 (nonblocking) | `core_risk.v1` fallback rule edge case | **CLOSED** | Plan line 122 now specifies precise condition: `extraction_mode == "missing"` on the `product_essence.v1` projected field AND `core_risk.v1` projected field has public value. |
| DS-F6 (nonblocking) | Active fund field attribution test strategy | **CLOSED** | Plan line 208 now requires: "至少一个测试必须通过注入自定义 registry（返回已知特殊 marker 值的 processor）来证明 active 字段确实来自 processor 输出或 registry 路径，而非仅因 direct extractor 值相等而通过。" |
| DS-F7 (needs-more-evidence) | Non-active non-bond fund type test coverage | **RESIDUALIZED** | Plan line 214 now recommends: "至少一种非 active、非 bond 的基金类型（如 `index_fund`）走 direct path 的行为保留冒烟测试；若现有 fixture 不足以支持则记录为 residual，不作为阻塞条件。" |

### Controller Fix Requirements Verification

| # | Requirement | Status | Verification |
|---|-------------|--------|--------------|
| 1 | `core_risk.v1` must clarify only `risk_characteristic_text` may fallback; other fields informational/redundant | **MET** | Plan lines 121-123: explicit fallback rule for `risk_characteristic_text` only; other 4 fields explicitly marked informational/redundant with primary-family ownership mapping. |
| 2 | `current_stage.v1` must be informational/redundant for S2 bundle projection | **MET** | Plan lines 124-125: explicit informational/redundant designation with primary-family ownership explanation. |
| 3 | `processor.extract()` unexpected exceptions must not swallow and must never fallback for active_fund | **MET** | Plan line 162: explicit fail-closed rule covering `TypeError`/`KeyError`/`AttributeError`, prohibition on swallowing, prohibition on fallback to direct path. |
| 4 | `source_kind` must be deterministic `annual_report` | **MET** | Plan line 85: deterministic static value `"annual_report"`, explicit prohibition on candidate-derived or provenance-derived values. |
| 5 | Active fund test must prove fields from processor, not merely equal direct extractor values | **MET** | Plan line 208: injected custom registry with known marker values requirement. |
| 6 | Non-active non-bond smoke test recommended or residualized | **MET** | Plan line 214: recommended with residual-acceptance clause. |

---

## Code-Generation-Readiness Assessment

The fixed plan remains code-generation-ready:

1. **Exact write set unchanged**: `data_extractor.py`, `test_data_extractor.py`, conditional `README.md`, implementation evidence artifact.
2. **Implementation shape fully specified**: Constructor injection, active fund processor path, bundle projection rules (now complete for all 6 field families), non-active fund path, fail-closed rules.
3. **Test requirements complete**: 8 test scenarios covering active/fail-closed/NAV/repository/bond/provenance plus injected-marker attribution test.
4. **Stop condition preserved**: Implementation worker stops after code/tests/evidence within exact write set.
5. **Forbidden write set unchanged**: All sensitive paths remain blocked.

---

## Fix Quality Assessment

| Dimension | Assessment |
|-----------|------------|
| Fix completeness | All 6 controller requirements addressed |
| Fix scope discipline | Only plan artifact and evidence artifact modified; no source/test/control/design doc changes |
| Fix evidence quality | Each fix includes code evidence path (e.g., active_annual.py line numbers) and clear rationale |
| Fix consistency | No contradiction with existing plan sections; fixes integrate cleanly |
| Fix verification | git diff --check confirmed whitespace-clean on both artifacts |

---

## Residual Risk

| Risk | Severity | Owner | Mitigation |
|------|----------|-------|------------|
| Bootstrap classification vs processor internal consistency | very low | S3 planning | Both consume same in-memory `ParsedAnnualReport`; deterministic extractor |
| `index_profile` still from bootstrap extraction | residual | S3 planning | Explicitly documented in plan residuals |
| Non-active non-bond smoke test not mandatory | low | Implementation worker | Recommended but residualized; code path unchanged |
| Anchor allocation strategy (whole-family-to-each-field) | low | Implementation worker | Documented in plan; acceptable for S2 scope |
| `_tracking_error_for_fund_type()` facade override of processor output | accepted design | Implementation worker | Processor does not make fund-type strategy decisions; facade applies post-processing |

---

## Boundary Violation / Overreach / Contradiction Check

| Check | Result |
|-------|--------|
| FundDocumentRepository boundary | PASS: No new direct parser/candidate paths |
| NOT_READY boundary | PASS: Explicit throughout plan |
| Candidate-only boundary | PASS: Line 163 candidate intermediate rule preserved |
| No parser replacement | PASS: Non-goals and forbidden write set unchanged |
| Active fund fail-closed | PASS: Strengthened by F2 fix |
| Non-active behavior preservation | PASS: Direct legacy path preserved for all non-active types |
| NAV degradation | PASS: Unchanged |
| Repository failure propagation | PASS: Unchanged |
| No new boundary violations from fix | PASS: Fixes only clarified existing rules, did not introduce new behavior |

---

## Review Scope Statement

This re-review did not implement code. This re-review did not modify source files, tests, control docs, or design docs. This re-review did not claim readiness for production, golden promotion, or release. Verdict is `PASS_NOT_READY`.

---

## Artifact Path

`docs/reviews/fund-processor-extractor-s2-data-extractor-integration-plan-rereview-mimo-20260618.md`
