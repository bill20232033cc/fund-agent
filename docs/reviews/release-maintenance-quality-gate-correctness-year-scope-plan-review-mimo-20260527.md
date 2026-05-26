# Gate 1 Plan Review: Quality Gate Correctness Report-Year Scope

> **Reviewer**: AgentMiMo
> **Date**: 2026-05-27
> **Plan artifact**: `docs/reviews/release-maintenance-quality-gate-correctness-year-scope-plan-20260526.md`
> **Gate**: Gate 1 correctness report_year scope fix (plan/review only)

---

## Verdict

**PASS_WITH_FINDINGS**

Plan is directionally correct, root cause evidence is verified against source code, non-goals are properly scoped, and test matrix covers the critical paths. Three informational findings and one low-severity finding require disposition but none block implementation.

---

## Review Scope 1: Oracle Identity Key Sufficiency

### Finding 1 — Informational: `report_year` source path in snapshot record confirmed

**Claim in plan**: `SnapshotRecord.report_year` already exists in `extraction_snapshot.py`.

**Evidence**: Confirmed. `extraction_snapshot.py` lines 100, 178, 200, 227, 238, 379, 392 all reference `report_year: int` on `SnapshotRecord` and `SelectedFundRecord`. The `build_snapshot_records()` function writes `report_year=bundle.report_year` into each snapshot record.

**Impact**: The gap is correctly identified as being only in golden-answer schema and correctness comparison, not in snapshot generation. No risk of missing a dependency.

### Finding 2 — Informational: `_snapshot_actual_index` must be extended to include `report_year`

**Evidence**: `extraction_score.py:1826-1863` — `_snapshot_actual_index()` returns `dict[tuple[str, str, str], str | None]` keyed by `(fund_code, field_name, sub_field)`. Each snapshot record already carries `report_year`, so the index builder can access it.

**Required disposition**: The plan correctly identifies this change but does not explicitly state that `_snapshot_actual_index` must extract `report_year` from each snapshot record. Implementation must read `report_year` from each record (not from an external parameter) to ensure per-record year accuracy. This is implicit in the plan but should be explicit.

**Impact**: None blocking — the plan's intent is clear and the data is available.

---

## Review Scope 2: Legacy 2024 Default Safety

### Finding 3 — Informational: Source-string inference is safe for current golden set

**Evidence**: `reports/golden-answers/golden-answer.json` confirms all 150 records across 11 funds have `source` fields containing `年报2024`. Example:
- `"source": "年报2024 §2 page-5 page-5-table-0 fund_name"`

The plan's proposal to default missing `report_year` to `2024` is correct and safe for the current curated set.

**Schema version**: The plan keeps `GOLDEN_ANSWER_SCHEMA_VERSION = "fund-agent.golden-answer.v1"` unchanged. This is acceptable because:
- The new `report_year` field is additive, not breaking
- Legacy files without `report_year` will be upgraded in-memory to 2024
- New build output will include structured `report_year` going forward

**No schema_version bump required** for this gate. A future golden maintenance gate may want to bump to v2 when multi-year coverage is added, but that is out of scope here.

---

## Review Scope 3: `year_not_covered` FQ0/Info Semantics

### Finding 4 — Low severity: `coverage_scope` domain expansion needs explicit constant

**Evidence**: `quality_gate.py:29-32` defines the current `CORRECTNESS_COVERAGE_*` constants:
- `CORRECTNESS_COVERAGE_NOT_CONFIGURED`
- `CORRECTNESS_COVERAGE_FUND_NOT_COVERED`
- `CORRECTNESS_COVERAGE_NO_COMPARABLE_FIELDS`
- `CORRECTNESS_COVERAGE_PARTIALLY_COVERED`
- `CORRECTNESS_COVERAGE_COVERED`

The plan proposes adding `year_not_covered` as a new coverage_scope value. The `quality_gate.py:_correctness_available_coverage_issue()` function (line 363-429) raises `ValueError` for unsupported `coverage_scope` values. The plan must add `CORRECTNESS_COVERAGE_YEAR_NOT_COVERED` as a new constant and handle it in `_correctness_available_coverage_issue()`.

**Impact**: Implementation detail, not a design issue. The plan mentions adding `year_not_covered` but should explicitly state the need for a new constant and gate handler. If missed, the gate will raise `ValueError` at runtime.

**Required disposition**: Implementation must:
1. Add `CORRECTNESS_COVERAGE_YEAR_NOT_COVERED: Final[str] = "year_not_covered"` constant
2. Handle it in `_correctness_available_coverage_issue()` to emit FQ0/info
3. Add corresponding constant in `extraction_score.py` for the summary

**Does this weaken same-year FQ1/block?** No. The `year_not_covered` path only activates when the fund code exists in golden but the current `report_year` does not match. Same-year mismatch still hits `CORRECTNESS_MISMATCH` → FQ1/block via `_correctness_mismatch_issue()`. The plan correctly preserves this.

---

## Review Scope 4: Test Matrix Completeness

**Assessment**: The test matrix (plan lines 89-108) covers the critical paths:

| Scenario | Covered | Notes |
|----------|---------|-------|
| Legacy JSON without `report_year` loads as 2024 | Yes | `test_golden_answer.py` |
| Build output includes `report_year` | Yes | `test_golden_answer.py` |
| Duplicate `(fund_code, report_year, field, sub_field)` rejected | Yes | `test_golden_answer.py` |
| 2024 same-year match | Yes | `test_extraction_score.py` |
| 2024 same-year mismatch → mismatch | Yes | `test_extraction_score.py` |
| 2025 missing-year → year_not_covered | Yes | `test_extraction_score.py` |
| field not comparable → no_comparable_fields | Yes | `test_extraction_score.py` |
| fund not present → fund_not_covered | Yes | `test_extraction_score.py` |
| year_not_covered → FQ0/info, not block | Yes | `test_quality_gate.py` |
| Same-year mismatch → FQ1/block | Yes | `test_quality_gate.py` |
| Integration: 2025 bundle + 2024 golden → FQ0 | Yes | `test_quality_gate_integration.py` |

**No gaps found** in the test matrix.

---

## Review Scope 5: Boundary Compliance

| Boundary | Status | Evidence |
|----------|--------|----------|
| Renderer unchanged | PASS | Plan non-goals section; no renderer files in modification list |
| Service/CLI unchanged | PASS | Plan states "current plan should not require Service/CLI changes" |
| Host/Agent/dayu unchanged | PASS | No Host/Agent files referenced |
| FundDocumentRepository unchanged | PASS | No document repository files referenced |
| NAV unchanged | PASS | No nav_data files referenced |
| turnover_rate unchanged | PASS | Plan non-goals section |
| checklist run-id unchanged | PASS | Plan explicitly records this as P3 residual |
| FQ0-FQ6 policy semantics preserved | PASS | Same-year FQ1/block preserved; year_not_covered is additive FQ0/info |

**No boundary violations detected.**

---

## Summary of Findings

| # | Severity | Finding | Required Disposition |
|---|----------|---------|---------------------|
| 1 | Info | `report_year` already exists on `SnapshotRecord` | None — confirms gap is only in golden/score |
| 2 | Info | `_snapshot_actual_index` must extract `report_year` from each record | Implementation detail; plan intent is clear |
| 3 | Info | Source-string inference safe for current 150-record golden set | None — validates legacy default approach |
| 4 | Low | `CORRECTNESS_COVERAGE_YEAR_NOT_COVERED` constant + gate handler needed | Add constant and handler in implementation |

---

## Conclusion

**PASS_WITH_FINDINGS** — Plan is accepted for implementation. The root cause analysis is verified against source code, the oracle identity key is correct, the legacy default is safe, the FQ0/info semantics do not weaken same-year FQ1/block, and the test matrix is complete. Finding 4 is an implementation detail that must be handled but does not require plan revision.
