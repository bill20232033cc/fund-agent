# Aggregate Deep Review: drawdown_stress NAV-derived Metric Implementation

> **Review type**: aggregate deepreview (GLM worker)
> **Work unit**: drawdown_stress NAV-derived metric contract / implementation gate
> **Base commit**: `73da81b`
> **Work unit commits**: `41485d5` (accept plan), `bd1013b` (accept implementation)
> **Date**: 2026-05-29
> **Reviewer**: GLM aggregate deepreview worker

---

## 1. Review Loop Closure Verification

### Plan review loop

| Artifact | Worker | Verdict | Blocking | Non-blocking |
|---|---|---|---|---|
| Implementation plan | — | submitted | — | — |
| Plan review | GLM | accepted | 0 | 5 LOW (N1-N5) |
| Plan review | MiMo | pass-with-risks | 0 | 1 MED (M01: `quantitative_derived` + non-`derived_metric`), 3 LOW |
| Plan rereview | GLM | accepted | 0 | all N1-N5 and M01-M04 closed |
| Plan rereview | MiMo | accepted | 0 | all findings closed |

**Verdict**: Plan review loop fully closed. Plan Fix Notes address all findings from both workers.

### Implementation review loop

| Artifact | Worker | Verdict | Blocking | Non-blocking |
|---|---|---|---|---|
| Implementation evidence | — | submitted | — | — |
| Implementation review | GLM | accepted / pass | 0 | 1 LOW (L1: hardcoded "2024"), 2 INFO |
| Implementation review | MiMo | accepted | 0 | 15 non-blocking |
| Implementation rereview | GLM | accepted | 0 | L1 fix confirmed |
| Implementation rereview | MiMo | accepted | 0 | L1 fix confirmed |

**Verdict**: Implementation review loop fully closed. L1 fix (dynamic year via `report.key.year`) verified by both workers with 62 tests passed.

---

## 2. Plan-to-Code Match Verification

### Slice 1: NavMaxDrawdownMetric helper

- **Plan**: New `nav_metrics.py` with `calculate_max_drawdown_from_nav_series()`, standard running-peak algorithm, `NavMaxDrawdownMetric` frozen dataclass, fail-closed on raw-unit / non-verified / non-strong-eligible / duplicate / non-positive.
- **Code** (`fund_agent/fund/data/nav_metrics.py`, 311 lines): Matches plan exactly. Running-peak algorithm at lines 277-285. Pre-validation `_validate_metric_request` enforces `accumulated_nav / accumulated_nav / verified / strong_drawdown_evidence_eligible=True`. Period-filtered `_validate_period_records` enforces `minimum_records` independently from repository threshold. Same-drawdown preserves earliest trough via strict `<`.
- **Match**: exact.

### Slice 2: Contract extension

- **Plan**: Add `quantitative_derived` to `BondRiskEvidenceStrength`, `derived_metric` to `BondRiskEvidenceMeasurementKind`, add to accepted strengths, add cross-field validator.
- **Code** (`fund_agent/fund/extractors/models.py`):
  - Line 15: `quantitative_derived` added to `BondRiskEvidenceStrength` Literal.
  - Line 33: `derived_metric` added to `BondRiskEvidenceMeasurementKind` Literal.
  - Line 62: Added to `_BOND_RISK_EVIDENCE_STRENGTHS` frozenset.
  - Line 72: Added to `_BOND_RISK_EVIDENCE_MEASUREMENT_KINDS` frozenset.
  - Line 82: Added to `_BOND_RISK_ACCEPTED_STRENGTHS`.
  - Lines 290-291: Cross-field validator `quantitative_derived` requires `derived_metric` — addresses MiMo M01.
- **Match**: exact.

### Slice 3: DataExtractor wiring

- **Plan**: `FundDataExtractor.extract()` calls typed repository for `bond_fund` only, A-class only, `report_year` natural year window, minimum_records=30, fail-closed degradation.
- **Code** (`fund_agent/fund/data_extractor.py`):
  - Line 38: `_BOND_DRAWDOWN_SHARE_CLASS = "A"`, `_BOND_DRAWDOWN_MINIMUM_RECORDS = 30`.
  - Lines 84-120: `_NavSeriesRepository` Protocol with typed signature.
  - Lines 228-281: `_load_drawdown_metric_for_bond_fund()` — guards on exact `"bond_fund"`, constructs natural year from `report_year`, catches `NavDataContractError` and generic `Exception`, returns `(metric, error)` tuple.
  - Lines 259-270: extract() wires drawdown into `extract_bond_risk_evidence()`.
- **Match**: exact.

### Slice 4: Snapshot/score/quality tests

- **Plan**: snapshot narrow compatibility for derived-only anchors; score regression; quality gate no-FQ2F when seven groups satisfied.
- **Code**:
  - `extraction_snapshot.py`: `_first_annual_report_anchor` → `_first_traceable_anchor` (lines 1364-1379), falls back to first anchor when no `annual_report` anchor exists. Test: `test_build_snapshot_records_projects_derived_bond_risk_anchor_when_no_annual_anchor`.
  - `test_quality_gate.py`: `test_run_quality_gate_has_no_bond_risk_fq2f_when_score_issue_absent` — verifies no FQ2F generated when score has no `bond_risk_evidence_missing` issue.
- **Match**: exact.

### Slice 5: Docs

- **Plan**: Update `design.md`, `implementation-control.md`, `fund_agent/fund/README.md`, `tests/README.md`.
- **Code**: All four docs updated with accurate descriptions of accumulated NAV path, max drawdown metric, CSRC EID source, and remaining residuals.
- **Match**: exact.

---

## 3. Scope Creep Check

| Scope boundary | Status |
|---|---|
| Only `006597` / A-class in production path | **No creep** — `_BOND_DRAWDOWN_SHARE_CLASS = "A"` hardcoded; `CsrcEidNavSource` keeps A/C/E/F separated |
| Max drawdown only, no volatility | **No creep** — `nav_metrics.py` only implements `calculate_max_drawdown_from_nav_series()`; `_CALCULATION_METHOD` is fixed `Literal["max_drawdown_on_accumulated_nav_path"]` |
| No score/quality/golden semantic change | **No creep** — quality gate test proves FQ2F only fires from score issue; no score algorithm changed |
| No PR/push/release/golden promotion | **No creep** — no `git push`, no golden corpus change, no release tag |
| Fail-closed on NAV source/metric failure | **No creep** — `_load_drawdown_metric_for_bond_fund` catches errors and degrades gracefully; `drawdown_stress` stays weak |

---

## 4. 006597/2024 Blocker Verification

### Implementation evidence assertions (verified from evidence document):

1. **Real CSRC EID smoke**: `006597/A` 2024 max drawdown = `-0.10%` (peak 2024-09-26, trough 2024-10-09).
2. **Real 006597 extraction**: all 7 bond risk groups satisfied after drawdown_stress receives derived metric.
3. **No `bond_risk_evidence_missing`**: score no longer issues this for 006597/2024 because all 7 groups are satisfied.
4. **No corresponding FQ2F**: quality gate test confirms no FQ2F when score has no `bond_risk_evidence_missing` issue.

### Blocker解除 mechanism:

- `drawdown_stress` was the last unsatisfied group in `bond_risk_evidence.v1`.
- The derived max drawdown metric produces `status="accepted"`, `strength="quantitative_derived"`, `measurement_kind="derived_metric"`.
- This is included in `_BOND_RISK_ACCEPTED_STRENGTHS`, so `satisfied_group_ids` now includes `"drawdown_stress"`.
- With all 7 groups satisfied, `contract_status` becomes `"satisfied"`.
- Score therefore does not issue `bond_risk_evidence_missing`.
- Quality gate therefore does not issue FQ2F.

**Verdict**: 006597/2024 `bond_risk_evidence_missing` blocker is naturally解除 through satisfied evidence, not through weakening score/quality semantics.

---

## 5. Residual Risks Verification

Residual risks in `implementation-control.md` Open Residuals section are accurate:

| Residual | Accuracy |
|---|---|
| `006597` bond risk blocker entry now points to drawdown metric gate | ✅ Updated correctly |
| CSRC EID NAV provenance cleanup (`source_query_params` mixing HTTP and context) | ✅ Acknowledged as low risk |
| CSRC EID source generalization (hardcoded 006597 constants, F direct-search gap) | ✅ Correctly scoped to future gate |
| CSRC EID parser/source resilience (detail-page text parsing, endpoint availability) | ✅ Existing fail-closed behavior adequate |
| Source metadata strict bool parsing | ✅ Unchanged, correctly listed |
| Golden answer corpus v1 blocked | ✅ Unchanged |

---

## 6. Aggregate-Level Findings

### INFO-1: `_first_traceable_anchor` fallback scope (informational)

**File**: `fund_agent/fund/extraction_snapshot.py` (renamed from `_first_annual_report_anchor`)
**Lines**: 1364-1379 (diff lines 1503-1523)
**Severity**: informational
**Description**: The fallback from `return None` to `return anchors[0] if anchors else None` applies to all bond_risk_evidence groups in snapshot projection, not only `drawdown_stress`. In practice, non-drawdown groups always produce at least one `annual_report` anchor, so the fallback only triggers for `drawdown_stress` with pure derived anchors. The behavior change is correct for the intended use case, but the function name change signals a broader semantic shift than strictly necessary.
**Impact**: None in practice. Test coverage confirms correct behavior for both annual-report-anchored and derived-anchored fields.

### No other aggregate findings

The following areas were specifically checked and found clean:

1. **Max drawdown algorithm correctness**: Running-peak with strict `<` preserves earliest trough for identical max drawdowns. Division by zero is prevented by `_validate_period_records` rejecting non-positive NAV. ✅
2. **Cross-field validator**: `quantitative_derived` + non-`derived_metric` is rejected at validation time (MiMo M01). Test `test_quantitative_derived_drawdown_requires_derived_metric_kind` covers reject cases. ✅
3. **Error degradation path**: When NAV source or metric fails, `drawdown_stress` falls to `weak` (control intent text) or `missing`, never promotes to `accepted`. Test `test_nav_metric_error_keeps_drawdown_control_text_weak` and `test_data_extractor_raw_unit_nav_error_keeps_drawdown_weak` confirm. ✅
4. **Period boundary**: `_BOND_DRAWDOWN_MINIMUM_RECORDS = 30` is checked independently in `_validate_period_records` after period filtering, not on full series. Test `test_period_filtered_records_are_checked_independently` confirms. ✅
5. **Anchor provenance completeness**: Derived anchor note includes all 20 required provenance fields (source, source_id, source_url, source_query_params, retrieved_at, fund_code, share_class, date_range, record_count, nav_type, adjusted_basis, dividend_adjustment_status, identity_status, calculation_method, peak_date, peak_value, trough_date, trough_value, max_drawdown_ratio). Test `test_nav_derived_drawdown_metric_satisfies_drawdown_group` asserts all tokens present. ✅

---

## 7. Validation Summary

| Check | Result |
|---|---|
| `ruff check .` | All checks passed |
| `pytest -q` | 939 passed |
| Real CSRC EID smoke | 006597/A 2024 max drawdown = -0.10% |
| Real 006597 extraction | 7/7 groups satisfied, no `bond_risk_evidence_missing` |
| No score/quality/golden weakening | Verified by tests and code inspection |
| No PR/push/release/golden promotion | No git push or golden corpus change in diff |

---

## 8. Verdict

**accepted**

The plan review loop, implementation review loop, and rereview loop are all fully closed. Code matches the accepted plan with no scope creep. The 006597/2024 `bond_risk_evidence_missing` blocker is naturally解除 through satisfied quantitative derived evidence, not through weakening any gate. One informational finding (INFO-1) about the `_first_traceable_anchor` fallback scope has no practical impact. No aggregate-level findings escaped code review.
