# P5-S3 Snapshot Sub-Field Exposure Implementation

## Scope

- Implemented snapshot `comparable_values` as an explicit correctness comparison surface.
- Expanded correctness indexing from the legacy `classified_fund_type.fund_type` only path to a whitelist of stable scalar sub-fields.
- Preserved old snapshot compatibility: snapshots without `comparable_values` only expose the legacy classification comparison path.

## Code Changes

- `fund_agent/fund/extraction_snapshot.py`
  - Added `COMPARABLE_SUB_FIELDS_BY_FIELD`.
  - Added `SnapshotRecord.comparable_values`.
  - Exposes whitelisted scalar values for:
    - `basic_identity`: `fund_name`, `fund_code`, `fund_category`, `management_company`, `custodian`, `inception_date`, `classified_fund_type`
    - `benchmark`: `benchmark_name`, `benchmark_text`
    - `nav_benchmark_performance`: `nav_growth_rate`, `benchmark_return_rate`
    - `classified_fund_type`: `fund_type`
  - Applies the planned `benchmark_name = benchmark_text` alias when `benchmark_name` is absent.
  - Keeps `product_profile`, `fee_schedule`, and other unstable/nested fields out of the first denominator expansion.

- `fund_agent/fund/extraction_score.py`
  - Correctness now indexes snapshot `comparable_values` for whitelisted sub-fields.
  - New schema explicit missing semantics: when a record has `comparable_values` and `value_present=False`, whitelisted sub-fields become explicit `None`, so golden expectations produce mismatch.
  - Non-whitelisted fields remain unavailable and do not enter the denominator.
  - Old snapshots without `comparable_values` do not create new missing mismatches; only top-level `classified_fund_type` remains comparable for backwards compatibility.

- Tests and docs
  - Updated snapshot tests for schema and comparable sub-field extraction.
  - Updated score tests for expanded perfect-match denominator, old snapshot compatibility, and whitelist missing vs unavailable semantics.
  - Synced `README.md`, `fund_agent/fund/README.md`, and `tests/README.md`.

## Verification

- `pytest tests/fund/test_extraction_snapshot.py tests/fund/test_extraction_score.py tests/fund/test_quality_gate.py tests/fund/test_quality_gate_integration.py tests/services/test_fund_analysis_service.py tests/ui/test_cli.py -q`
  - `43 passed`
- `pytest tests/ -q`
  - `187 passed`
- `ruff check .`
  - passed
- `git diff --check`
  - passed

## Controller Judgment

P5-S3 implementation satisfies the accepted plan:

- correctness denominator is expanded only through explicit snapshot sub-field exposure;
- missing semantics are limited to whitelisted field/sub-field pairs;
- `benchmark_name` alias is field-local and does not infer across unrelated fields;
- old snapshot compatibility remains conservative;
- no UI/Application/Service boundary changes were introduced.

Next gate: `P5-S3 code review`.
