# Implementation Evidence: risk_characteristic_text.v1 same-source failing test gate

## Gate

- Gate: `same-source failing risk test gate for risk_characteristic_text.v1`
- Classification: `standard`
- Accepted plan checkpoint: `4a25dee`
- Scope: test-only failing-test evidence for a future contract.

## Files Changed

- `tests/fund/test_small_golden_set_extractor_correctness.py`
- `tests/README.md`
- `docs/reviews/mvp-small-golden-set-risk-characteristic-text-same-source-failing-test-gate-plan-20260610.md`
- `docs/reviews/plan-review-20260610-141151.md`
- `docs/reviews/mvp-small-golden-set-risk-characteristic-text-same-source-failing-test-gate-controller-judgment-20260610.md`
- `docs/reviews/mvp-small-golden-set-risk-characteristic-text-same-source-failing-test-gate-implementation-evidence-20260610.md`

## Implementation Summary

- Replaced the generic `SAME_SOURCE_UNSUPPORTED_FIELDS = {"risk"}` xfail path with a named strict xfail:
  - `test_profile_extractor_exposes_same_source_risk_characteristic_text`
  - future contract version: `risk_characteristic_text.v1`
- Added `_risk_expected_text(row)` to read `fields.risk.expected` from the accepted retained oracle.
- The new strict xfail builds minimal reports for all five accepted fund codes and requires a future dedicated `profile.risk_characteristic_text` output surface.
- The test intentionally does not accept `product_profile.style_positioning` as passing risk evidence.
- Updated `tests/README.md` to name the remaining strict xfail contracts:
  - `risk_characteristic_text.v1`
  - `bond_top_holding_row.v1`
  - `target_fund_holding_row.v1`
- Corrected the plan/review/judgment wording from five parameterized xfail cases to one strict xfail that internally checks all five rows, preserving the accepted `21 passed, 3 xfailed` focused test summary.

## Validation

| Command | Result |
|---|---|
| `uv run pytest tests/fund/test_small_golden_set_extractor_correctness.py -q` | passed: `21 passed, 3 xfailed` |
| `uv run pytest tests/fund/test_small_golden_set_manifest.py tests/fund/test_small_golden_set_fixture_shape.py tests/fund/test_small_golden_set_source_identity.py tests/fund/test_small_golden_set_parser_mechanics.py tests/fund/test_small_golden_set_extractor_correctness.py -q` | passed: `42 passed, 3 xfailed` |
| `uv run ruff check tests/fund/test_small_golden_set_extractor_correctness.py` | passed |

## Boundary Confirmation

- No production `fund_agent/` code changed.
- No `ProfileExtractionResult` schema changed.
- No `StructuredFundDataBundle`, snapshot, renderer, quality gate, report evidence, chapter facts, checklist, Service or Host integration changed.
- No PDF, `FundDocumentRepository`, cache/source helper, fallback, network, provider/live LLM, fixture projection, golden/readiness promotion, source/provider/runtime/config behavior or release/PR external state changed.

## Remaining Next Entries

- `risk_characteristic_text.v1` additive extractor fix gate, if separately authorized.
- same-source failing `006597` bond holding test gate for `bond_top_holding_row.v1`.
- same-source failing `110020` target ETF holding test gate for `target_fund_holding_row.v1`.
- separate downstream integration planning for `portfolio_managers`, if separately authorized.
