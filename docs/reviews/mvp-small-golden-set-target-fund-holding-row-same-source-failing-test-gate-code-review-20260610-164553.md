# MVP Small Golden Set Target Fund Holding Row Same-Source Failing Test Gate Code Review - 2026-06-10

## Scope Reviewed

- `tests/fund/test_small_golden_set_extractor_correctness.py`
- `docs/reviews/mvp-small-golden-set-target-fund-holding-row-same-source-failing-test-gate-implementation-evidence-20260610.md`

## Findings

No blocking findings.

## Review Notes

- The change is test-only and does not alter production extractor behavior.
- The dedicated strict xfail is row-scoped to `110020 / 2024 / target_etf_holding`.
- The test uses only the accepted retained excerpt oracle and an in-memory parsed annual report.
- The future contract avoids inventing target ETF code identity and only asserts oracle-backed `name`, `fair_value_cny`, `net_asset_ratio`, and source anchor.
- Existing bond/equity-like holdings assertions remain passing.

## Verification Reviewed

- `uv run pytest tests/fund/test_small_golden_set_extractor_correctness.py -q` -> `23 passed, 1 xfailed`.
- `uv run pytest tests/fund/test_small_golden_set_manifest.py tests/fund/test_small_golden_set_fixture_shape.py tests/fund/test_small_golden_set_source_identity.py tests/fund/test_small_golden_set_parser_mechanics.py tests/fund/test_small_golden_set_extractor_correctness.py -q` -> `44 passed, 1 xfailed`.
- `uv run ruff check tests/fund/test_small_golden_set_extractor_correctness.py` -> passed.
- `git diff --check -- ...` -> passed.

## Residual Risk

- The target-fund holding extractor output surface remains unimplemented by design.
