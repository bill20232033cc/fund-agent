# P14-S1 Index Profile / Tracking Error Quality Denominator Implementation

Date: 2026-05-22

Gate: P14-S1 implementation ready for code review.

## Goal

Implement the approved P14-S1 plan for `index_profile` / `tracking_error` quality-denominator coverage without reopening P13 direct-disclosure scope.

The implementation makes these two fields part of the quality denominator only where the field is applicable:

- `index_fund` and `enhanced_index`: `index_profile` and `tracking_error` are conditional P1 fields.
- non-index fund types: these two fields are excluded from FQ2 coverage, traceability, single-fund missing count, and missing P1 fields.
- unknown or conflicting fund type: conservative scoring remains in effect; fields are not silently excluded.

`ExtractionMode` remains unchanged.

## Implemented Slices

### Slice A: Snapshot Comparable Values

Changed `fund_agent/fund/extraction_snapshot.py`.

- Added stable comparable sub-fields for `index_profile`:
  - `benchmark_text`
  - `benchmark_identity_status`
  - `benchmark_index_name`
  - `benchmark_index_code`
  - `methodology_availability`
  - `constituents_availability`
  - `source_tier`
- Added stable comparable sub-fields for `tracking_error`:
  - `value_text`
  - `period_label`
  - `annualized`
  - `source_type`
  - `calculation_method`
  - `benchmark_identity_status`
  - `benchmark_index_name`
  - `benchmark_index_code`
  - `frequency`
  - `input_period_complete`
- Loosened snapshot field typing to accept dataclass values.
- Normalized dict/dataclass values before sub-field lookup.
- Boolean comparable values serialize through existing scalar conversion as `True` / `False`.

### Slice B: FQ2 / Extraction Score Denominator

Changed `fund_agent/fund/extraction_score.py`.

- Added `index_profile` and `tracking_error` to `FIELD_PRIORITY_BY_NAME` as P1.
- Added conditional applicability filtering for index-quality fields.
- Applied the same scorable-record filtering to:
  - aggregate field scores
  - single-fund `fund_scores`
  - `fund_quality.total_field_count`
  - `fund_quality.missing_field_count`
  - `_missing_fields_by_priority`
- `_build_fund_quality_row` first resolves `classified_fund_type` with `_unique_optional_text(records, "classified_fund_type")`, then passes that resolved value into index-quality filtering.
- Conflict/unknown type remains conservative in fund quality because it does not fall back to row-level fund type after uniqueness resolution.

### Slice C: Golden Prefill / Golden Answer

Changed:

- `fund_agent/fund/golden_prefill.py`
- `docs/golden-answer-template.md`
- `reports/golden-answers/golden-answer-prefill-reviewed.md`
- `reports/golden-answers/golden-answer.json`

Implemented dict/dataclass prefill support. Added evidence-backed `001548` `index_profile` production golden rows only:

- `benchmark_text`
- `benchmark_identity_status`
- `benchmark_index_name`
- `source_tier`

No production `tracking_error` golden rows were added because this slice only had verified reviewed evidence for the benchmark-derived index profile rows.

Rebuilt strict JSON with:

```text
golden_answer: reports/golden-answers/golden-answer.json
funds: 6
records: 125
skipped: 29
```

### Slice D: Fixtures And Tests

Changed:

- `tests/fund/test_extraction_snapshot.py`
- `tests/fund/test_extraction_score.py`
- `tests/fund/test_golden_prefill.py`
- `tests/fund/test_quality_gate.py`
- `tests/fund/integration/test_p1_sample_matrix.py`

Coverage added for:

- dataclass comparable sub-fields for `IndexProfileValue` and `TrackingErrorValue`
- boolean comparable serialization as `True` / `False`
- applicable `index_fund` path
- applicable `enhanced_index` path
- non-index excluded path
- unknown/conflicting type conservative path
- correctness match/mismatch for index-quality comparable fields
- golden prefill dataclass support
- deterministic enhanced-index sample fixture `161725`, including §1/§2 classification/index profile and §3 direct tracking-error text `报告期年化跟踪误差：1.23%`

`510300` remains in the sample matrix as existing broad-index coverage.

### Slice E: Docs Sync

Changed:

- `fund_agent/fund/README.md`
- `tests/README.md`

Updated current behavior for comparable values, conditional P1 denominator semantics, dataclass golden prefill, and test ownership.

## Validation

All planned validation commands passed.

```text
$ .venv/bin/python -m pytest tests/fund/test_extraction_snapshot.py -q
.....                                                                    [100%]
5 passed in 0.60s
```

```text
$ .venv/bin/python -m pytest tests/fund/test_extraction_score.py tests/fund/test_quality_gate.py -q
.............................................                            [100%]
45 passed in 0.76s
```

```text
$ .venv/bin/python -m pytest tests/fund/test_golden_prefill.py tests/fund/test_golden_answer.py -q
.....                                                                    [100%]
5 passed in 0.60s
```

```text
$ .venv/bin/python -m pytest tests/fund/integration/test_p1_sample_matrix.py -q
.                                                                        [100%]
1 passed in 0.52s
```

```text
$ .venv/bin/python -m pytest tests/fund/test_quality_gate_integration.py tests/services/test_extraction_score_service.py tests/services/test_quality_gate_service.py -q
.........                                                                [100%]
9 passed in 0.55s
```

```text
$ .venv/bin/python -m ruff check fund_agent tests
All checks passed!
```

```text
$ .venv/bin/python -m pytest -q
427 passed in 0.98s
```

```text
$ git diff --check HEAD
<no output>
```

## Changed Files

Production:

- `fund_agent/fund/extraction_snapshot.py`
- `fund_agent/fund/extraction_score.py`
- `fund_agent/fund/golden_prefill.py`
- `reports/golden-answers/golden-answer-prefill-reviewed.md`
- `reports/golden-answers/golden-answer.json`
- `docs/golden-answer-template.md`

Tests:

- `tests/fund/test_extraction_snapshot.py`
- `tests/fund/test_extraction_score.py`
- `tests/fund/test_golden_prefill.py`
- `tests/fund/test_quality_gate.py`
- `tests/fund/integration/test_p1_sample_matrix.py`

Docs:

- `fund_agent/fund/README.md`
- `tests/README.md`
- `docs/reviews/p14-s1-index-profile-tracking-error-quality-denominator-implementation-20260522.md`

## Explicit Non-Changes

- Did not expand `ExtractionMode`.
- Did not add calculated tracking error.
- Did not add external index series adapter.
- Did not add methodology or constituents extraction.
- Did not redesign QDII subtype semantics.
- Did not introduce E1/E2/E3, Evidence Confirm, LLM audit, RepairContract, Dayu runtime, Host, Engine, or tool loop scope.
- Did not edit source data or resolve RR-13.
- Did not edit `docs/repo-audit-20260521.md`.
- Did not commit, push, or create PR.

## Residuals

- `tracking_error` golden correctness has test coverage, but no production `tracking_error` golden rows were added because no current reviewed artifact row was verified for direct tracking-error value.
- `methodology_availability` and `constituents_availability` are comparable only for currently extracted scalar status fields; this slice does not implement methodology/constituents extraction.
- Worktree contains pre-existing untracked `docs/repo-audit-20260521.md`; it was not touched.

## Completion State

`ready_for_code_review`.

Recommended next gate: P14-S1 code review.

## Fix Pass: GLM Code Review Findings

Date: 2026-05-22

Controller accepted GLM PASS_WITH_FINDINGS low-severity findings F-1 and F-2 in the same P14-S1 implementation gate.

### F-1 Fix

Changed `fund_agent/fund/extraction_score.py`.

- `_build_fund_score_row` now resolves fund-level type with `_unique_optional_text(records, "classified_fund_type")` before index-quality applicability filtering.
- `_build_fund_score_row` passes the resolved `classified_fund_type` into `_scorable_records(..., use_record_fund_type=False)`.
- `_score_records_for_single_fund` now accepts the same fund-level applicability context, avoiding a second row-level type fallback inside the per-fund scoring loop.
- Conflicting fund type therefore remains conservative in both `fund_scores` and `fund_quality`: `index_profile` / `tracking_error` are retained rather than excluded.

Added regression coverage in `tests/fund/test_extraction_score.py`:

- `test_fund_score_keeps_index_quality_fields_when_fund_type_conflicts`

### F-2 Fix

Changed:

- `fund_agent/fund/_value_utils.py`
- `fund_agent/fund/extraction_snapshot.py`
- `fund_agent/fund/golden_prefill.py`
- `fund_agent/fund/README.md`

Extracted duplicate dict/dataclass normalization into Fund Capability internal helper:

- `fund_agent.fund._value_utils.value_mapping`

Both snapshot comparable-value extraction and golden prefill now import this helper. The helper remains inside `fund_agent/fund` and introduces no Service, Engine, Runtime, or UI dependency.

### Fix Pass Validation

```text
$ .venv/bin/python -m pytest tests/fund/test_extraction_score.py tests/fund/test_extraction_snapshot.py tests/fund/test_golden_prefill.py -q
.................................                                        [100%]
33 passed in 0.40s
```

```text
$ .venv/bin/python -m ruff check fund_agent tests
All checks passed!
```

```text
$ .venv/bin/python -m pytest -q
428 passed in 0.99s
```

```text
$ git diff --check HEAD
<no output>
```

### Fix Pass Changed Files

Additional production/docs/test changes since the initial implementation report:

- `fund_agent/fund/_value_utils.py`
- `fund_agent/fund/extraction_score.py`
- `fund_agent/fund/extraction_snapshot.py`
- `fund_agent/fund/golden_prefill.py`
- `fund_agent/fund/README.md`
- `tests/fund/test_extraction_score.py`
- `docs/reviews/p14-s1-index-profile-tracking-error-quality-denominator-implementation-20260522.md`

No production `tracking_error` golden rows were added. `ExtractionMode` remains unchanged. `docs/repo-audit-20260521.md` remains untouched.

Completion state after fix pass: `ready_for_code_review`.
