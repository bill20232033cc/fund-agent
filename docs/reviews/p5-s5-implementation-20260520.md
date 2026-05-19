# P5-S5 Share Change Hardening Implementation - 2026-05-20

## Scope

Implemented explicit share-change value-column selection for multi-share-class tables.

The old extractor selected the first non-empty value after the row label, which made A/C share table behavior depend on column order. P5-S5 replaces that with conservative same-source column selection.

## Code Changes

- `fund_agent/fund/extractors/holdings_share_change.py`
  - Added `_ShareColumnSelection`.
  - Added explicit selection rules:
    - single value column: `single_value_column`
    - exact fund-code header match: `fund_code_header_match`
    - strict A-class fallback: `single_a_class_fallback`
  - Rejected fund-code suffix inference.
  - Total columns (`合计`, `总计`, `基金份额总额`, `总份额`) are ignored for class fallback but still accepted when they are the only value column.
  - Beginning, ending, and net change now use the same selected column.
  - Ambiguous multi-value tables return `missing` instead of silently taking the first value.
  - `share_change.value` now includes `share_class_column` and `share_class_selection_reason` metadata when extraction succeeds.

- `tests/fund/extractors/test_holdings_share_change.py`
  - Updated existing share-change assertions for metadata.
  - Added exact fund-code header match test.
  - Added ambiguous multi-class missing test.
  - Added total + A/C fallback test.
  - Added regression coverage that A-class fallback is not used when another fund-code-specific header exists.

- Docs
  - Updated `fund_agent/fund/README.md`.
  - Updated `tests/README.md`.

## Verification

- `pytest tests/fund/extractors/test_holdings_share_change.py tests/fund/integration/test_p1_sample_matrix.py tests/fund/integration/test_p3_cli_e2e_matrix.py tests/fund/analysis/test_investor_return.py tests/fund/template/test_renderer.py -q`
  - `31 passed`
- `pytest tests/ -q`
  - `195 passed`
- `ruff check .`
  - passed
- `git diff --check`
  - passed

## Controller Judgment

P5-S5 implementation satisfies the accepted plan:

- no unreliable A/C inference from fund-code suffix;
- no implicit first-value fallback for ambiguous multi-column tables;
- selection metadata is stable and traceable;
- downstream investor-return/template tests continue to pass with the extra metadata keys.

Next gate: `P5-S5 code review`.
