# P9-S2 Plan Re-Review — AgentDS

- **Date**: 2026-05-21
- **Review target**: `docs/reviews/p9-s2-quality-gate-golden-coverage-plan-20260521.md` (revised)
- **Reviewer**: AgentDS (independent re-review)
- **Prior review**: `docs/reviews/p9-s2-plan-review-ds-20260521.md` (verdict: PASS_WITH_FINDINGS, 6 findings)
- **Scope**: targeted re-review of High/Medium finding closure only; no fresh full-plan audit

## Verdict

**PASS**

All 6 findings from the prior review are closed. The two High findings (state model mapping, test false-positive risk) and the Medium finding (CLI diagnosis visibility) are fully addressed with explicit specification. Two minor documentation-level observations remain but neither is blocking.

---

## Finding Closure Verification

### Finding 1 — State Model Mapping Gap (was HIGH) → CLOSED

**Original**: 9 proposed states had no mapping to `CorrectnessSummary` fields.

**Revised plan**: New Section 3.1 "Mapping To Existing CorrectnessSummary" (lines 66–91) adds:
- Explicit statement that `coverage_scope` augments `status`, does not replace it
- 7-row mapping table from each proposed state → `status` / `coverage_scope` / `reason` / `record_results`
- 7-step derivation order for single-fund `analyze` target fund coverage
- Multi-fund `extraction-score` considerations for `covered_fund_codes` / `missing_fund_codes`

**Verdict**: The mapping is complete and unambiguous. Implementer can derive every field from the table.

### Finding 2 — Test Matrix False Positive Risk (was HIGH) → CLOSED

**Original**: Three test cases checked only aggregate gate status, could pass without FQ0/info generation.

**Revised plan**: Test matrix (Section 7) now:
- Row "correctness unavailable only": explicitly asserts `FQ0/info present with reason=not_configured`
- Row "correctness fund not covered only": asserts `fund-scoped FQ0/info present with reason=fund_not_covered`
- **New** row "golden fund present but no comparable fields": asserts `fund-scoped FQ0/info present with reason=no_comparable_fields`
- Row "selected-pool member without golden coverage": asserts `FQ0/info recorded with fund_code, reason, and coverage_scope`
- **New** rows for malformed golden fail-closed, explicit golden path missing, default golden path missing (edge cases from Finding 5)

Section 5.1 "FQ0/Info Metadata Contract" (lines 137–156) specifies required issue fields: `rule_code="FQ0"`, `severity="info"`, `fund_code`, `reason` (enum), `golden_answer_path`, `coverage_scope`, `comparable_records`, `unavailable_records`, `total_records`.

**Verdict**: Every relevant test case now asserts specific FQ0/info metadata, not just aggregate status. False-positive risk is eliminated.

### Finding 3 — CLI Diagnosis Visibility Gap (was MEDIUM) → CLOSED

**Original**: FQ0/info only in artifacts; stderr visibility unspecified.

**Revised plan**: 
- Section 5 (line 129): "stderr should print one short informational line when a fund-scoped `FQ0/info` correctness coverage issue exists, for example `quality_gate_info: strict golden answer not covered for fund_code xxxxxx`"
- Section 5 (line 131): "The stderr info line is not a failure, must not change exit code, and must not be phrased as a warning or block"
- Section 6 CLI plan (line 192): "Print one concise `quality_gate_info: ...` stderr line for fund-scoped correctness coverage `FQ0/info`"
- Test matrix CLI row (line 229): "stderr includes `quality_gate_info: ...` plus normal gate status/artifacts"
- Acceptance criteria (line 244): "CLI emits a concise informational stderr line for fund-scoped correctness coverage `FQ0/info` without changing exit status"

**Verdict**: CLI stderr visibility is explicitly specified at the format, behavior, and test level. A user running `fund-analysis analyze 000216` will see the info line and know correctness was skipped.

### Finding 4 — `correctness_missing_comparable_value` State Redundancy (was LOW) → CLOSED

**Original**: Named state with identical behavior to mismatch was ambiguous.

**Revised plan**:
- State renamed and clarified (line 59): "diagnostic sub-case of mismatch; still `FQ1/block`"
- Section 3 narrative (line 64): "`correctness_missing_comparable_value` is not a new non-blocking state. It is a diagnostic label for the existing mismatch path where the golden record is comparable and expected to exist, but snapshot explicitly marks the value as missing. The behavior remains `FQ1/block`"
- Mapping table (line 76): shows it maps to `status=available`, coverage `covered/partially_covered`, `record_results status=mismatch`
- Acceptance criteria (line 241): "Comparable value explicitly missing remains a mismatch diagnostic sub-case and still blocks as `FQ1`"

**Verdict**: The state is unambiguously a diagnostic label, not a new behavioral path. No implementer confusion risk.

### Finding 5 — Golden Answer File Edge Cases (was LOW) → CLOSED

**Original**: Malformed/empty golden files were unaddressed.

**Revised plan**: Comprehensive fail-closed specification:
- Section 3.1 step 2 (line 83): non-default explicit path missing/malformed/invalid → fail closed; "do not degrade it to `not_configured`"
- Section 3.1 step 3 (line 84): default path exists but malformed → also fail closed; "only default path absence is `not_configured`"
- Section 5.1 (line 156): "Invalid existing golden files are not `FQ0/info`. Empty, malformed, wrong schema version, duplicate, missing required fields, or otherwise invalid strict golden files must fail closed or raise a structured exception"
- Test matrix: new rows for "explicit golden path missing" (fail closed), "golden file exists but malformed/invalid" (fail closed)
- Section 6 extraction_score.py plan (line 167): "Keep malformed or invalid existing golden files fail-closed; only absent default path can become `not_configured`"
- Acceptance criteria (line 242): "Malformed or invalid existing golden files fail closed; only absent default golden path is `not_configured`"

**Verdict**: All edge cases covered. Fail-closed semantics prevent a broken oracle from being silently treated as absent coverage.

### Finding 6 — CSV Duplicate 016492 (was INFO) → No Change Needed

Already correctly deferred in original plan. Still correctly deferred in revised plan (§10). No action required.

---

## New Observations (Non-Blocking)

### Observation A — Section 4 Coverage Scope Enumeration Omits `no_comparable_fields` (severity: LOW)

**What**: Section 4 (line 100) lists `coverage_scope` values as `not_configured / fund_not_covered / partially_covered / covered`, omitting `no_comparable_fields`. However, Section 3.1 mapping table and derivation steps use `no_comparable_fields` as a distinct scope value.

**Impact**: Minor documentation inconsistency. The mapping table (Section 3.1) and derivation steps are authoritative; Section 4 should be updated to include all 5 values for consistency.

**Recommendation**: Add `no_comparable_fields` to the Section 4 enumeration before handing off to implementation. Not blocking — the derivation steps and test matrix already cover this scope.

### Observation B — `compare_snapshot_correctness()` Target Fund Scoping Not Explicit (severity: LOW)

**What**: The derivation steps (Section 3.1) describe how to determine `fund_not_covered` by checking the golden file's fund list, but the implementation plan for `compare_snapshot_correctness()` (Section 6) does not specify whether this function receives a `target_fund_code` parameter or derives it from the snapshot records.

**Impact**: Implementation-level detail. For single-fund `analyze`, the snapshot records are already scoped to one fund, so fund_code can be extracted from them. No architectural risk.

**Recommendation**: The implementer should note that `compare_snapshot_correctness()` must either accept `target_fund_code` or extract it from records to determine `fund_not_covered`. Either approach is fine; the plan doesn't need to prescribe which.

---

## Acceptance Criteria Traceability (Re-Verified)

| Criterion | Plan reference | Status |
|---|---|---|
| Product mode still uses block | §2, §6 | OK |
| Selected-pool member without golden answer ≠ not_run | §3, §3.1, test matrix | OK |
| Missing golden coverage visible as FQ0/info with fund_code, reason, coverage_scope | §5.1, test matrix | OK (was partial, now complete) |
| `comparable_records=0` → FQ0/info `reason=no_comparable_fields` | §3.1, test matrix | OK (new) |
| Explicit mismatch remains FQ1/block | §3, test matrix | OK |
| Comparable value explicitly missing → mismatch sub-case, still FQ1/block | §3, §3.1 | OK (was ambiguous, now explicit) |
| Malformed/invalid golden files fail closed | §3.1, §5.1, test matrix | OK (new) |
| Non-member / invalid CSV still blocks as not_run | §3, test matrix | OK |
| CLI emits stderr info line for FQ0/info without changing exit | §5, §6, test matrix | OK (was missing, now specified) |
| `docs/code_20260519.csv` remains default | §4 | OK |
| 6 covered golden funds remain human-labeled | §9 | OK |

---

## Overall Assessment

The revised plan closes all 6 findings from the prior review. The three highest-severity gaps — state model mapping, test false-positive risk, and CLI diagnosis visibility — are each addressed with explicit, verifiable specification:

- **State mapping**: a full 7-row table mapping each state to `CorrectnessSummary` fields plus a 7-step derivation order
- **Test matrix**: every FQ0/info test case now asserts specific metadata (`rule_code`, `severity`, `fund_code`, `reason`, `coverage_scope`), not just aggregate status
- **CLI visibility**: `quality_gate_info:` stderr line explicitly specified at format, behavior, test, and acceptance-criteria levels

The plan also added important fail-closed semantics for malformed golden files that were missing in the original. The two remaining observations (Section 4 coverage enumeration, function parameter design) are documentation/implementation details that can be resolved during coding without plan changes.

The plan is ready for implementation.
