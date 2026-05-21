# P9 Aggregate Deepreview — AgentDS

- **Date**: 2026-05-21
- **Scope**: P9-S1 (analyze product contract hardening) + P9-S2 (quality gate / golden coverage calibration) cross-slice behavior
- **Reviewer**: AgentDS (independent aggregate review)
- **P9 commits**: `2bacdb3` (P9-S1), `ce603a0` (P9-S2), plus plan/doc commits
- **Input artifacts**:
  - `docs/reviews/post-p8-planning-20260521.md`
  - `docs/reviews/p9-s1-analyze-product-contract-plan-20260521.md`
  - `docs/reviews/p9-s1-code-review-controller-judgment-20260521.md`
  - `docs/reviews/p9-s2-quality-gate-golden-coverage-plan-20260521.md`
  - `docs/reviews/p9-s2-code-review-controller-judgment-20260521.md`
  - `docs/reviews/p9-aggregate-readiness-reconciliation-20260521.md`
  - `docs/design.md`
  - `docs/implementation-control.md`

## Verdict

**PASS**

The P9 phase successfully hardens the product analyze contract (P9-S1) and calibrates quality gate golden coverage semantics (P9-S2) without regression. The two slices work together correctly: product mode enforces `block` policy and minimal user inputs, while `FQ0/info` for missing golden coverage ensures the product path is usable for all 55 selected-pool funds, not just the 6 with human-labeled golden answers. No product-mode bypass, no gate boundary confusion, no buy/sell wording leakage. One LOW finding on documentation consistency; non-blocking.

---

## Cross-Slice Behavior Analysis

### 1. Product Mode × Developer Override Isolation

**Claim**: Product mode must not accept developer-only override fields through CLI or Service paths.

**Verification**:

| Layer | Mechanism | Evidence |
|---|---|---|
| Service | `_resolve_analyze_contract()` rejects `developer_overrides is not None` in product mode with `ValueError` | `fund_analysis_service.py:451-453` |
| CLI | `--equity-position`, `--quality-gate-policy warn/off`, `--final-judgment-override` etc. raise `typer.BadParameter` without `--dev-override` | P9-S1 CLI implementation; tested in `tests/ui/test_cli.py` |
| Product | `quality_gate_policy` hardcoded to `"block"` in product mode resolver | `fund_analysis_service.py:465` |
| Product | All dev fields (`equity_position`, `actual_style`, etc.) set to `None` in product mode | `fund_analysis_service.py:455-464` |

**Cross-slice**: P9-S2 does not modify `fund_analysis_service.py` at all. The P9-S1 product/developer isolation boundary remains intact after P9-S2 golden coverage calibration. A product user running `fund-analysis analyze 000216` cannot accidentally or intentionally switch to `warn`/`off` quality gate policy.

**Verdict**: ✅ PASS — Product mode is fail-closed against developer override leakage at both CLI and Service boundaries.

### 2. quality_gate_policy=block Default Enforcement

**Claim**: Product mode must always use `block` policy; `warn`/`off` only via `--dev-override`.

**Verification**:

| Scenario | Behavior | Evidence |
|---|---|---|
| Product mode | `quality_gate_policy="block"` hardcoded | `fund_analysis_service.py:465` |
| gate block | `QualityGateBlockedError` raised, no report | `fund_analysis_service.py:558-560` |
| gate not-run (non-member) | `QualityGateNotRunBlockedError` raised, no report | `fund_analysis_service.py:336` |
| Dev override, policy=off | gate skipped, report produced, `not_run` status in final judgment | `fund_analysis_service.py:558` |
| Dev override, policy=warn, gate=block | report produced, final judgment gets `quality_gate_status="block"` | `fund_analysis_service.py:336-340` |
| CLI `--quality-gate-policy off` without `--dev-override` | `typer.BadParameter` | CLI gating in P9-S1 |
| Service `request.mode="product"` + `quality_gate_policy="warn"` | Impossible — resolver ignores request-level policy in product mode | `_resolve_analyze_contract()` |

**Cross-slice**: P9-S2 extends the quality gate rules (FQ0/info for missing coverage) but does not alter the policy enforcement. The Service quality gate state machine (policy × gate result × not-run reason → behavior) is unchanged between P9-S1 and P9-S2.

**Verdict**: ✅ PASS — `block` default is enforced at every entry point; `warn`/`off` requires `--dev-override`.

### 3. gate_not_run Boundary Definition

**Claim**: `gate_not_run` must be strictly limited to pre-gate execution failures: CSV missing/invalid, schema validation failure, or fund not in selected pool.

**Verification**:

| Scenario | Result | Evidence |
|---|---|---|
| Fund not in CSV | `not_run_reason` returned, gate never runs | `quality_gate_integration.py:68-91` |
| CSV missing/malformed | `not_run_reason` returned | `quality_gate_integration.py:148-152` |
| Fund in CSV, no golden coverage | Gate **runs**, produces FQ0/info, status=pass/warn | `quality_gate_integration.py:123` + quality_gate FQ0/info |
| Golden file missing (default path) | Gate runs, correctness unavailable, FQ0/info with reason=not_configured | `extraction_score.py` coverage derivation + `quality_gate.py:328-345` |
| Golden file malformed | Fail-closed with ValueError/JSONDecodeError | `extraction_score.py` fail-closed path; plan §3.1 step 2-3 |

**Cross-slice critical check**: Before P9-S2, a fund not in the golden file but in the CSV could have been ambiguous — was it `gate_not_run` or just missing coverage? P9-S2 closes this gap by introducing explicit `coverage_scope` derivation and making golden coverage absence always FQ0/info. The membership short-circuit in `quality_gate_integration.py` (unchanged since P9-S1) only triggers for CSV-level failures, never for golden coverage gaps.

**Verdict**: ✅ PASS — `gate_not_run` strictly means pre-gate failure; golden coverage absence is always diagnostic FQ0/info.

### 4. Missing Strict Golden Coverage as FQ0/info

**Claim**: Selected-pool members without strict golden coverage must produce fund-scoped FQ0/info with `fund_code`, `reason`, and `coverage_scope` metadata.

**Verification**:

| Coverage scenario | FQ0/info `reason` | `coverage_scope` | `fund_code` present |
|---|---|---|---|
| No golden path configured | `not_configured` | `not_configured` | No (aggregate) |
| Golden exists, fund not in golden | `fund_not_covered` | `fund_not_covered` | Yes |
| Fund in golden, zero comparable fields | `no_comparable_fields` | `no_comparable_fields` | Yes |
| Some fields non-comparable | `field_not_comparable` | `partially_covered` | Yes (when fund-scoped) |
| Covered with matches | No FQ0/info generated | `covered`/`partially_covered` | N/A |

All FQ0/info issues carry `rule_code="FQ0"`, `severity="info"`, `golden_answer_path`, `comparable_records`, `unavailable_records`, `total_records` (`quality_gate.py:455-470`).

**Cross-slice**: P9-S1 established that final judgment derives from quality gate status. P9-S2 ensures FQ0/info issues appear in the gate result but don't block. The end-to-end flow for fund `000216` (selected-pool member, no golden coverage, good P0/P1):
1. Service resolves product contract (P9-S1)
2. `_check_pool_membership_before_extraction()` → fund is in CSV → no `not_run` (P9-S1)
3. Extraction, score, gate run (P9-S1 + P9-S2)
4. `compare_snapshot_correctness()` → `coverage_scope=fund_not_covered` (P9-S2)
5. `_evaluate_correctness()` → FQ0/info with reason=`fund_not_covered` (P9-S2)
6. Gate aggregate status = `pass` (no blocking issues)
7. Final judgment derived as `worth_holding` or `needs_attention` depending on other signals (P9-S1)
8. Report produced; stderr shows `quality_gate_info: strict golden answer not covered for fund_code 000216 reason=fund_not_covered` (P9-S2)

**Verdict**: ✅ PASS — Missing golden coverage is visible, machine-diagnostic, and non-blocking.

### 5. Mismatch and Malformed Fail-Closed

**Claim**: Explicit correctness mismatch must remain FQ1/block; malformed golden files and malformed correctness schemas must fail closed.

**Verification**:

| Scenario | Behavior | Evidence |
|---|---|---|
| Comparable value mismatch | `FQ1/block` issue | `quality_gate.py:503-530` `_correctness_mismatch_issue()` |
| Comparable value explicitly missing | Mismatch diagnostic sub-case, still FQ1/block | `extraction_score.py` status=mismatch; `quality_gate.py` treats all mismatches as FQ1 |
| Golden file malformed/invalid | `json.JSONDecodeError` or `GoldenAnswerValidationError` propagated | `extraction_score.py` loader path |
| Explicit golden path missing | `FileNotFoundError` — fail closed | `extraction_score.py` path resolution |
| `status=unavailable` with unknown `coverage_scope` | `ValueError` raised | `quality_gate.py:332-335` |
| `status=unavailable` with unknown `coverage_reason` | `ValueError` raised | `quality_gate.py:332-335` |
| Unknown `coverage_scope` on `status=available` | `ValueError` raised | `quality_gate.py:429` |
| Unknown `correctness.status` | `ValueError` raised | `quality_gate.py:346-347` |

**Cross-slice**: P9-S1 established the quality gate state machine that blocks on `block` status. P9-S2 adds FQ1/block for mismatches and fail-closed validation for malformed correctness data. The controller-identified bug (FQ-CG-1: `status=unavailable` accepting unknown coverage metadata) was fixed before acceptance — `_valid_unavailable = {None, CORRECTNESS_COVERAGE_NOT_CONFIGURED}` now gates the unavailable path.

**Verdict**: ✅ PASS — All mismatch and malformed paths fail closed; no silent degradation.

### 6. Final Judgment Prohibits Buy/Sell Wording

**Claim**: Final judgment must not output buy/sell recommendations or position ratios.

**Verification**:

| Layer | Mechanism | Evidence |
|---|---|---|
| Capability | `FinalJudgment` labels are `worth_holding` / `needs_attention` / `suggest_replace` | `final_judgment.py:16` |
| Capability | No "买入"/"卖出" in reason strings | Grep: zero hits in `final_judgment.py` |
| Renderer | `_FORBIDDEN_TERMS = ("买入", "卖出", "仓位比例", "收益预测")` | `renderer.py:43` |
| Renderer | Report markdown scanned for forbidden terms; `ValueError` if found | `renderer.py:1165-1167` |
| Design | §1.3 non-goal: "不输出买卖建议或仓位比例" | `design.md:35` |
| README | Describes final judgment as derived, never as buy/sell | README |

**Cross-slice**: P9-S1 introduced the final judgment derivation policy with `worth_holding` explicitly defined as "当前证据下值得持有，不是买入建议" (plan §3.4 table). P9-S2 doesn't touch final judgment; the renderer defense-in-depth `_FORBIDDEN_TERMS` check catches any accidental regression.

**Verdict**: ✅ PASS — No buy/sell wording at any layer; defense-in-depth forbidden terms check in renderer.

### 7. README / Documentation Consistency

**Claim**: README must describe current behavior, not future policy.

**Verification**:

| README claim | Current code reality | Status |
|---|---|---|
| `analyze` default is product mode | `FundAnalysisRequest.mode` default = `"product"` | ✅ |
| Final judgment derived by Capability | `derive_final_judgment()` in `fund_agent/fund/analysis/` | ✅ |
| Dev params require `--dev-override` | CLI rejects dev params without flag; Service rejects product + overrides | ✅ |
| quality gate `warn/off` only with `--dev-override` | CLI gating + Service resolver enforcement | ✅ |
| FQ0/info for missing golden coverage | `_correctness_available_coverage_issue()` generates FQ0/info | ✅ |
| `quality_gate_info:` stderr line | `_quality_gate_info_lines()` → `typer.echo(..., err=True)` | ✅ |
| `coverage_scope` values | All five values implemented | ✅ |
| `docs/code_20260519.csv` as default membership | `DEFAULT_SELECTED_FUNDS_CSV` unchanged | ✅ |
| Smoke commands use `--dev-override --quality-gate-policy warn` | README line 230 documents this correctly | ✅ |

**Verdict**: ✅ PASS — README describes current behavior without forward-looking policy drift.

---

## Finding

### Finding 1 — README `coverage_scope` Enumeration Missing `no_comparable_fields` (severity: LOW)

**What**: README line 169 lists `coverage_scope` values as `not_configured / fund_not_covered / partially_covered / covered`, omitting `no_comparable_fields`. The same omission was noted as Observation A in the P9-S2 plan re-review for the plan's Section 4. The implementation correctly supports all five values, but README omits one.

**Impact**: A reader of the README would not know `no_comparable_fields` exists as a distinct scope value.

**Recommendation**: Add `no_comparable_fields` to the README enumeration before or during the next slice. Not blocking — the implementation and test matrix cover this scope.

---

## Non-Findings (Verified Correct)

Items explicitly checked and found correct:

- **P9-S2 plan Observation A** (plan §4 omitted `no_comparable_fields`): noted but accepted as non-blocking in re-review; implementation correctly supports all 5 values.
- **P9-S2 plan Observation B** (`compare_snapshot_correctness()` parameter design): implementation resolved this naturally; `_correctness_coverage()` extracts fund_code from records.
- **P9-S2 code review limitation** (no independent agent review artifact): recorded as residual risk in controller judgment; aggregate review here partially mitigates by verifying cross-slice behavior.
- **CSV duplicate 016492**: Still deferred as human-owned; not introduced or worsened by P9.
- **`correctness_required` policy mechanism**: Correctly not implemented; `coverage_required=false` is diagnostic only.
- **Golden set 6 funds**: Remain human-labeled; no guessing or automated expansion in P9.

---

## Verification Commands

Executed on current workspace (HEAD = `2f82d9e`, clean):

```
.venv/bin/python -m pytest -q
→ 377 passed in 1.17s

.venv/bin/ruff check .
→ passed

git diff --check
→ clean (no whitespace errors)

git diff --stat HEAD
→ (no uncommitted changes)
```

---

## Overall Assessment

P9 achieves its design goals: product `analyze` has a minimal, user-safe contract; developer-only capabilities are behind an explicit `--dev-override` gate; final judgment is Capability-owned and never outputs buy/sell language; quality gate `block` is fail-closed at every product entry point while missing golden coverage is transparently disclosed as `FQ0/info`.

The P9-S1 → P9-S2 transition is clean: P9-S2 extends the correctness coverage model without modifying the Service orchestration, membership short-circuit, or developer override isolation established in P9-S1. The two slices together produce a coherent product path where:

- A selected-pool member **with** golden coverage gets full correctness oracle comparison (FQ1/block on mismatch).
- A selected-pool member **without** golden coverage gets FQ0/info disclosure + all other quality checks intact.
- A fund **not** in the selected pool is blocked before expensive extraction.

The one LOW finding (README `coverage_scope` enumeration) is a documentation polish item, not a correctness issue.

P9 is ready for the next phase.
