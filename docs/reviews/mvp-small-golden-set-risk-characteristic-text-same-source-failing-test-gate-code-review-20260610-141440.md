# Code Review: risk_characteristic_text.v1 same-source failing test gate

## Verdict

PASS. No blocking findings.

## Scope Reviewed

- `tests/fund/test_small_golden_set_extractor_correctness.py`
- `tests/README.md`
- Gate plan/review/judgment/evidence artifacts under `docs/reviews/`

## Findings

No issues found.

## Review Notes

- The implementation is test-only and does not modify production extractor code.
- The old generic `risk` unsupported-field xfail was replaced by a contract-named strict xfail for `risk_characteristic_text.v1`.
- The new test constructs reports from the accepted retained oracle for all five accepted fund codes.
- The current failure condition is the absence of a dedicated `profile.risk_characteristic_text` surface, not mismatch against `style_positioning`.
- Focused xfail count is preserved at three:
  - `risk_characteristic_text.v1`
  - `bond_top_holding_row.v1`
  - `target_fund_holding_row.v1`
- `tests/README.md` now names the remaining future-contract gaps.

## Validation Reviewed

- `uv run pytest tests/fund/test_small_golden_set_extractor_correctness.py -q` -> `21 passed, 3 xfailed`
- `uv run pytest tests/fund/test_small_golden_set_manifest.py tests/fund/test_small_golden_set_fixture_shape.py tests/fund/test_small_golden_set_source_identity.py tests/fund/test_small_golden_set_parser_mechanics.py tests/fund/test_small_golden_set_extractor_correctness.py -q` -> `42 passed, 3 xfailed`
- `uv run ruff check tests/fund/test_small_golden_set_extractor_correctness.py` -> passed

## Residual Risk

The production risk-characteristic surface is still unimplemented by design. A future additive extractor fix gate must make the strict xfail pass without conflating risk text with `product_profile.style_positioning`.
