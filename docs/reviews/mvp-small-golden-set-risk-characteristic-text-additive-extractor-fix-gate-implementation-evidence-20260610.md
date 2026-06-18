# Implementation Evidence: risk_characteristic_text.v1 additive extractor fix gate

## Gate

- Gate: `risk_characteristic_text.v1 additive extractor fix gate`
- Classification: `heavy`
- Accepted plan checkpoint: `c2c7218`
- Scope: additive Fund profile extractor surface, focused tests, README and gate artifacts.

## Files Changed

- `fund_agent/fund/extractors/models.py`
- `fund_agent/fund/extractors/profile.py`
- `tests/fund/extractors/test_profile.py`
- `tests/fund/test_small_golden_set_extractor_correctness.py`
- `fund_agent/fund/README.md`
- `tests/README.md`
- `docs/reviews/mvp-small-golden-set-risk-characteristic-text-additive-extractor-fix-gate-implementation-evidence-20260610.md`

## Implementation Summary

- Added `ProfileExtractionResult.risk_characteristic_text`.
- Added dedicated `risk_characteristic_text.v1` profile builder:
  - extracts only explicit `§2` `风险收益特征` / `基金风险收益特征` labels;
  - returns `schema_version`, `fund_code`, `report_year`, exact `risk_characteristic_text`, and value-level `source_anchors`;
  - returns `missing` when no explicit risk label exists.
- Preserved existing `product_profile.style_positioning` behavior.
- Updated the small-golden retained-oracle report builder to include explicit `风险收益特征` content from `fields.risk.expected`.
- Removed the accepted strict xfail marker from `test_profile_extractor_exposes_same_source_risk_characteristic_text`; the test now passes over all five accepted rows.
- Updated README files to state that risk characteristic text is now a current profile extractor output and that remaining strict xfails are only:
  - `bond_top_holding_row.v1`
  - `target_fund_holding_row.v1`

## Validation

| Command | Result |
|---|---|
| `uv run pytest tests/fund/extractors/test_profile.py tests/fund/test_small_golden_set_extractor_correctness.py -q` | passed: `54 passed, 2 xfailed` |
| `uv run pytest tests/fund/test_small_golden_set_manifest.py tests/fund/test_small_golden_set_fixture_shape.py tests/fund/test_small_golden_set_source_identity.py tests/fund/test_small_golden_set_parser_mechanics.py tests/fund/test_small_golden_set_extractor_correctness.py -q` | passed: `43 passed, 2 xfailed` |
| `uv run pytest tests/fund/test_data_extractor.py -q` | passed: `10 passed` |
| `uv run ruff check fund_agent/fund/extractors/models.py fund_agent/fund/extractors/profile.py tests/fund/extractors/test_profile.py tests/fund/test_small_golden_set_extractor_correctness.py` | passed |
| `git diff --check -- fund_agent/fund/extractors/models.py fund_agent/fund/extractors/profile.py tests/fund/extractors/test_profile.py tests/fund/test_small_golden_set_extractor_correctness.py fund_agent/fund/README.md tests/README.md docs/reviews/mvp-small-golden-set-risk-characteristic-text-additive-extractor-fix-gate-plan-20260610.md docs/reviews/plan-review-20260610-145801.md docs/reviews/mvp-small-golden-set-risk-characteristic-text-additive-extractor-fix-gate-controller-judgment-20260610.md` | passed |

## Boundary Confirmation

- No PDF, `FundDocumentRepository`, cache/source helper, fallback, network, provider/live LLM, fixture projection, golden/readiness promotion, source/provider/runtime/config behavior or external release/PR state changed.
- No `StructuredFundDataBundle`, data extractor field wiring, snapshot, score, quality gate, report evidence, chapter facts, renderer, checklist, Service, Host or Agent runtime integration changed.
- No bond or target ETF row-shape work was performed.

## Remaining Next Entries

- same-source failing `006597` bond holding test gate for `bond_top_holding_row.v1`;
- same-source failing `110020` target ETF holding test gate for `target_fund_holding_row.v1`;
- separate downstream integration planning for `portfolio_managers` and/or `risk_characteristic_text`, if separately authorized.
