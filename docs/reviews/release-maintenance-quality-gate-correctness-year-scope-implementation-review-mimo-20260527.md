# Gate 1 Implementation Code Review: Correctness Report-Year Scope

> Date: 2026-05-27
> Reviewer: AgentMiMo
> Gate: correctness report_year scope fix
> Plan: `docs/reviews/release-maintenance-quality-gate-correctness-year-scope-plan-20260526.md`
> Controller judgment: `docs/reviews/release-maintenance-quality-gate-correctness-year-scope-plan-controller-judgment-20260527.md`
> Implementation evidence: `docs/reviews/release-maintenance-quality-gate-correctness-year-scope-implementation-evidence-20260527.md`

## Verdict

**PASS**

## Review Scope

Review of uncommitted changes on `codex/local-reconciliation` against the accepted plan, controller judgment, and 6 review focus areas.

## Findings

### F1 — Correctness Oracle Identity Is Year-Scoped

**Status: CORRECT**

`_snapshot_actual_index()` (extraction_score.py:1890-1934) keys by `(fund_code, report_year, field_name, sub_field)`. It reads `report_year` via `_required_snapshot_int()` from each snapshot record.

`_compare_golden_record()` (extraction_score.py:1961-2046) uses `key = (fund_code, report_year, field_name, sub_field)` for lookup.

`_correctness_coverage()` (extraction_score.py:1801-1887) constructs `golden_identities = {(fund.fund_code, fund.report_year) for fund in golden_funds}` and `target_identities = set(snapshot_fund_identities)`, then filters record_results by `(row.fund_code, row.report_year) in target_identities`.

All three layers are consistently 4-tuple keyed. The oracle identity `fund_code + report_year + field_name + sub_field` is correctly implemented.

### F2 — Coverage Classification Is Correct

**Status: CORRECT**

`_correctness_coverage()` precedence order (extraction_score.py:1825-1887):

1. Empty snapshot → `fund_not_covered`
2. All snapshot fund codes absent from golden → `fund_not_covered`
3. No snapshot `(fund_code, report_year)` identity present in golden → `year_not_covered`
4. Target results exist but no comparable match/mismatch → `no_comparable_fields`
5. Some funds covered, some not → `partially_covered`
6. All fully covered → `covered`

The `year_not_covered` check (step 3) fires when the fund code exists in golden but the specific report year does not. This is the correct priority: `fund_not_covered` (no fund at all) takes precedence over `year_not_covered` (fund exists but wrong year). Edge case: same fund code across multiple years in the same snapshot is handled by set-based identity matching.

### F3 — Legacy Golden Default 2024 Is Safe

**Status: CORRECT**

`LEGACY_GOLDEN_ANSWER_REPORT_YEAR = 2024` (golden_answer.py:23). Used in:
- `_json_optional_report_year()` (golden_answer.py:471-501): returns 2024 when `report_year` is missing or invalid
- `parse_golden_answer_markdown()`: all Markdown-parsed records get `report_year=2024`
- `_append_current_fund()`: `_ParsedFund` gets `report_year=2024`
- Duplicate key detection uses `(fund_code, 2024, field_name, sub_field)` for Markdown sources

The existing curated `golden-answer.json` has sources anchored to `年报2024`, so defaulting to 2024 is factually correct for the current corpus. This is a compatibility rule, not a new truth claim.

Same `fund_code` across different `report_year` is allowed: `seen_keys` is `(fund_code, report_year, field_name, sub_field)`, so `("004393", 2024, ...)` and `("004393", 2025, ...)` are distinct. Test `test_load_golden_answer_json_allows_same_fund_code_different_report_year` verifies this.

Duplicate detection rejects `(fund_code, report_year, field_name, sub_field)` collisions. Test `test_load_golden_answer_json_rejects_duplicate_same_year_identity` verifies this.

### F4 — Quality Gate Handles year_not_covered as FQ0/info

**Status: CORRECT**

`quality_gate.py:407-411`: `CORRECTNESS_COVERAGE_YEAR_NOT_COVERED` is in the set alongside `CORRECTNESS_COVERAGE_FUND_NOT_COVERED` and `CORRECTNESS_COVERAGE_NO_COMPARABLE_FIELDS`, all routing to the FQ0/info handler via `_correctness_coverage_issue()`.

`_correctness_coverage_message()` (quality_gate.py:501-505) has a dedicated message for `year_not_covered`: "当前年报年份尚未覆盖；本次 correctness oracle 不使用其它年份 golden answer。"

Same-year mismatch remains FQ1/block: `_evaluate_correctness()` (quality_gate.py:359-360) iterates `record_results` and generates FQ1/block for any row with `status == CORRECTNESS_MISMATCH`. This path is unchanged.

### F5 — Tests Prevent 2025 Being Killed by 2024 Golden

**Status: CORRECT**

- `test_compare_snapshot_correctness_marks_current_year_not_covered` (test_extraction_score.py:1006-1049): Constructs 2024 golden with `_golden_answer_json()` (which includes `report_year=2024`), creates a 2025 snapshot record, and asserts `coverage_scope == "year_not_covered"`, `comparable_records == 0`, `mismatched_records == 0`.
- `test_run_quality_gate_reports_correctness_year_not_covered_as_fq0_info` (test_quality_gate.py:359-431): Verifies `year_not_covered` produces FQ0/info and no FQ1/block.
- `test_run_quality_gate_for_bundle_uses_bundle_report_year_for_correctness` (test_quality_gate_integration.py:90-130): Full integration test with `report_year=2025` bundle against 2024 golden, verifies FQ0/info `year_not_covered`, not FQ1/block.

These tests directly prevent the regression where 2025 snapshots are killed by 2024 golden rows.

### F6 — No Scope Violations

**Status: CORRECT — No out-of-scope changes**

Changed files are exactly the plan-specified set:
- `fund_agent/fund/golden_answer.py` ✓
- `fund_agent/fund/extraction_score.py` ✓
- `fund_agent/fund/quality_gate.py` ✓
- `tests/fund/test_golden_answer.py` ✓
- `tests/fund/test_extraction_score.py` ✓
- `tests/fund/test_quality_gate.py` ✓
- `tests/fund/test_quality_gate_integration.py` ✓
- `fund_agent/fund/README.md` ✓
- `tests/README.md` ✓

No changes to: renderer, Service/CLI, Host/Agent/dayu, source helper, NAV, turnover_rate, checklist run-id, or FQ policy semantics.

### F7 — Additional Observations (Non-Blocking)

**F7.1 — `_required_snapshot_int` is new, mirrors existing `_required_error_int`**
Severity: INFO
Location: extraction_score.py:1048-1071
The new function follows the same pattern as `_optional_error_int` but raises on missing. This is a clean addition; no concern.

**F7.2 — `_snapshot_fund_codes` is retained alongside new `_snapshot_fund_identities`**
Severity: INFO
Location: extraction_score.py:1785-1798
`_snapshot_fund_codes` is still used in `compare_snapshot_correctness()` for the `unavailable` path (line 860) and in `_correctness_coverage()` for `snapshot_fund_codes` (line 1832). This is correct — the fund-only helper is still needed for `missing_fund_codes` output and the `golden_answer_path is None` fallback.

**F7.3 — `_json_optional_report_year` appends to errors but returns fallback value**
Severity: INFO
Location: golden_answer.py:471-501
When `report_year` is invalid (e.g., bool, non-integer string), the function appends an error and returns `LEGACY_GOLDEN_ANSWER_REPORT_YEAR`. The caller checks `if errors` and raises `GoldenAnswerValidationError`, so the fallback value is only used if no other errors exist. This is consistent with the existing `_json_required_text` pattern where invalid input returns empty string but errors are collected and checked.

**F7.4 — `report_year` in `CorrectnessRecordResult` serialized to score.json**
Severity: INFO
Location: extraction_score.py:329
The new `report_year: int` field in `CorrectnessRecordResult` is serialized via `asdict()` into `score.json` record_results. This is additive and non-breaking for downstream consumers.

## Acceptance Validation

- Focused pytest: 74 passed in 0.83s ✓
- Focused ruff: All checks passed ✓
- git diff --check: passed ✓

## Summary

Implementation correctly applies the `fund_code + report_year + field_name + sub_field` identity throughout the correctness oracle chain. Coverage classification properly distinguishes `fund_not_covered` (no fund in golden) from `year_not_covered` (fund in golden but wrong year). Legacy golden defaults to 2024 as a safe compatibility rule. Quality gate maps `year_not_covered` to FQ0/info and preserves same-year mismatch as FQ1/block. Tests directly prevent the 2025-killed-by-2024 regression. No scope violations detected.

## Artifact Path

`docs/reviews/release-maintenance-quality-gate-correctness-year-scope-implementation-review-mimo-20260527.md`
