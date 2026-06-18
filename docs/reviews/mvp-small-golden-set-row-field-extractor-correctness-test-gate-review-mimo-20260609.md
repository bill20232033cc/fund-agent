# MVP Small Golden Set Row-field Extractor Correctness Test Gate Review — MiMo

## Gate

- Gate: `row-field extractor correctness test gate after accepted retained excerpts`
- Role: final code review (independent)
- Reviewer: AgentMiMo
- Date: 2026-06-09
- Commit: `928fc86`

## Review Scope

- `tests/fund/test_small_golden_set_extractor_correctness.py`
- `tests/README.md`
- `docs/reviews/mvp-small-golden-set-row-field-extractor-correctness-test-gate-implementation-evidence-20260609.md`
- `docs/reviews/mvp-small-golden-set-row-field-extractor-correctness-test-gate-controller-judgment-20260609.md`
- `docs/current-startup-packet.md`
- `docs/implementation-control.md`

## Review Criteria Results

### 1. Correctness oracle exclusively from retained excerpt JSON

**PASS.** `ORACLE_PATH` at line 23-28 points to `docs/reviews/mvp-small-golden-set-retained-excerpt-fixture-pdf-only-20260609.json`. No other file is loaded as a correctness source. `_load_oracle()` (line 95-109) reads only that path. All passing assertions (`test_profile_extractor_matches_same_source_identity_benchmark_and_fee`, `test_performance_extractor_matches_same_source_one_year_returns`, `test_performance_extractor_matches_same_source_tracking_error_when_present`) consume values from `_expected(row, field_name)` which reads from oracle rows exclusively.

### 2. Synthetic/unmatched `expected_fields.json` excluded from correctness

**PASS.** `test_synthetic_unmatched_expected_fields_are_excluded_from_correctness_source()` (line 405-431) explicitly asserts:
- `ORACLE_PATH.name != "expected_fields.json"` (line 418)
- `SYNTHETIC_FIXTURE_ROOT not in ORACLE_PATH.parents` (line 419)
- All five synthetic fixtures have `fixture_source_kind=synthetic`, `source_identity.status=unmatched_synthetic`, `exact_numeric_correctness_allowed=False`, `promotion_allowed=False` (lines 427-431)

Verified at runtime: all five `expected_fields.json` files remain `unmatched_synthetic` with no correctness or promotion allowance.

### 3. `scale` is a passing `fund_scale` assertion, not xfail

**PASS.** `SAME_SOURCE_UNSUPPORTED_FIELDS` at line 74 contains only `{"manager", "holdings", "risk"}` — `scale` is absent. `test_profile_extractor_matches_same_source_identity_benchmark_and_fee` (line 464) asserts `profile.basic_identity.value["fund_scale"] == expected_units` where `expected_units` derives from `scale_expected.get("target_share_units") or scale_expected.get("total_share_units")`. This is a passing assertion for all five fund codes.

Controller judgment confirms Carver identified and fixed this: scale was originally misclassified as xfail and was corrected to a passing assertion.

### 4. Unsupported xfail only covers `manager`, `holdings`, `risk`

**PASS.** `SAME_SOURCE_UNSUPPORTED_FIELDS = {"manager", "holdings", "risk"}` (line 74). The xfail test `test_same_source_fields_without_current_row_consumer_are_blocked_gaps` (line 531-554) is parameterized over exactly those three fields. The xfail marker is `strict=True` (line 531), meaning if any of these fields ever start passing, the test will fail — preventing silent promotion to accepted passing correctness.

The test body (line 554) asserts `field_name not in SAME_SOURCE_UNSUPPORTED_FIELDS`, which is the expected failing assertion. No other fields are mislabeled as xfail.

### 5. Real extractor calls: `extract_profile` / `extract_performance`

**PASS.** Line 19 imports `extract_performance` and line 20 imports `extract_profile`. Both are used directly:
- `extract_profile(report)` at line 453 in the profile correctness test
- `extract_performance(report)` at line 491 in the performance correctness test
- `extract_performance(report)` at line 523 in the tracking-error test

These are real extractor invocations against minimal `ParsedAnnualReport` objects built from oracle data, not mocks or stubs.

### 6. Boundary violations check

**PASS.** No boundary violations found:
- No PDF read: `_build_report_from_oracle_row()` constructs in-memory `ParsedAnnualReport` from oracle fields only
- No network: no `httpx`, `requests`, or network imports
- No `FundDocumentRepository`: not imported or referenced
- No fallback: no source helper or fallback imports
- No live/provider probe: no provider imports
- No extractor modification: extractors are imported and called, not modified
- No provider/default/runtime/budget/config change: no config module imports
- No fixture projection: `SYNTHETIC_FIXTURE_ROOT` is referenced only for exclusion testing, not for promotion or projection
- No golden/readiness promotion: no golden answer or readiness imports

### 7. Evidence/control docs consistency with validation results

**PASS.** Implementation evidence (line 56-57) and controller judgment (line 49-50) both record `13 passed, 3 xfailed` for the standalone test and `34 passed, 3 xfailed` for the small-golden suite. Runtime verification at HEAD `928fc86` confirms both counts exactly.

## Findings

**No blocking findings.**

## Residual Risks

1. **Production PDF fidelity not proven.** The test builds minimal `ParsedTable` / `ParsedAnnualReport` objects from oracle fields. It does not prove that the production PDF parser produces the same table shape. This is by-design scope exclusion — PDF read is unauthorized in this gate.

2. **Manager / holdings / risk remain blocked gaps.** Three xfail markers record same-source fields that the current extractor cannot consume in this test shape. They require a later extractor fix or row-shape design gate. The strict xfail prevents silent promotion.

3. **Correctness coverage is field-subset only.** Passing assertions cover identity, share-unit scale, benchmark, management/custody fee, one-year return and 110020 tracking error. Other fields (investor return, turnover, holder structure, holdings snapshot, share change, nav data) remain outside this gate's correctness proof.

## Verdict

**PASS / no blocking findings.**

The gate correctly uses the retained excerpt JSON as the sole correctness oracle, explicitly excludes synthetic/unmatched fixtures, asserts `scale` as a passing field, limits xfail to `manager`/`holdings`/`risk` only, calls real extractors, respects all boundary constraints, and produces evidence/control docs consistent with observed test results.
