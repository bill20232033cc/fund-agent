# Implementation Evidence: target_fund_holding_row.v1 additive extractor fix gate

## Gate

- Gate: `target_fund_holding_row.v1 additive extractor fix gate`
- Accepted plan checkpoint: `fd29754`
- Classification: `standard`

## Implemented Changes

- Added `target_fund_holding_row.v1` extraction to `extract_holdings_share_change().holdings_snapshot`.
- Added a dedicated table detector for explicit `§8` target-fund holding rows requiring `基金名称`, `公允价值`, and `占基金资产净值比例`.
- Added `target_fund_holdings` as a dedicated sub-shape, separate from stock `top_holdings` and bond `bond_top_holdings`.
- Added serializable row-level `source_anchor` with `section_id`, `section_title`, `page_number`, `table_id`, and `row_locator`.
- Removed the dedicated strict xfail for `test_holdings_extractor_exposes_same_source_target_fund_holding_row`.
- Added a focused holdings extractor unit test for target-fund-only tables.
- Updated Fund and tests README text to describe the current extractor/test surface.

## Contract Output

For the accepted `110020 / 2024 / target_etf_holding` oracle, the extractor now outputs:

- `schema_version = target_fund_holding_row.v1`
- `fund_code = 110020`
- `report_year = 2024`
- `target_fund_holdings[0].name`
- `target_fund_holdings[0].fair_value_cny`
- `target_fund_holdings[0].net_asset_ratio`
- `target_fund_holdings[0].source_anchor`

No target ETF code is emitted or inferred.

## Validation

```text
uv run pytest tests/fund/test_small_golden_set_extractor_correctness.py -q
24 passed in 0.62s

uv run pytest tests/fund/extractors/test_holdings_share_change.py tests/fund/test_data_extractor.py -q
34 passed in 0.62s

uv run ruff check fund_agent/fund/extractors/holdings_share_change.py tests/fund/test_small_golden_set_extractor_correctness.py tests/fund/extractors/test_holdings_share_change.py
All checks passed!

uv run pytest tests/fund/test_small_golden_set_manifest.py tests/fund/test_small_golden_set_fixture_shape.py tests/fund/test_small_golden_set_source_identity.py tests/fund/test_small_golden_set_parser_mechanics.py tests/fund/test_small_golden_set_extractor_correctness.py -q
45 passed in 0.39s

git diff --check -- fund_agent/fund/extractors/holdings_share_change.py tests/fund/test_small_golden_set_extractor_correctness.py tests/fund/extractors/test_holdings_share_change.py fund_agent/fund/README.md tests/README.md docs/reviews/mvp-small-golden-set-target-fund-holding-row-additive-extractor-fix-gate-plan-20260610.md docs/reviews/mvp-small-golden-set-target-fund-holding-row-additive-extractor-fix-gate-plan-review-20260610.md docs/reviews/mvp-small-golden-set-target-fund-holding-row-additive-extractor-fix-gate-controller-judgment-20260610.md
passed
```

## Boundary Confirmation

- No PDF read, repository access, source helper, fallback, provider, network or live LLM.
- No fixture projection and no golden/readiness promotion.
- No downstream wiring into `StructuredFundDataBundle`, extraction snapshot, score, quality gate, renderer, checklist, Service, Host or Agent runtime.
- No target ETF code extraction or inference.
