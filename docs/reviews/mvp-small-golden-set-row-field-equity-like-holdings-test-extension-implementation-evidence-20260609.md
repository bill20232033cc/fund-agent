# MVP Small Golden Set Row-field Equity-like Holdings Test Extension Implementation Evidence

## Gate

- Gate: `row-field correctness test extension gate for retained equity-like holdings subset`
- Classification: `standard`
- Role: implementation worker only
- Baseline checkpoint: `fc80d3d gateflow: accept row-field extractor gap decision`
- Date: 2026-06-09

## Scope

Implemented a test-only extension for the accepted equity-like holdings subset using only `docs/reviews/mvp-small-golden-set-retained-excerpt-fixture-pdf-only-20260609.json` as oracle.

In scope:

- `004393`: `top_stock_table_row`
- `004194`: `top_index_stock_table_row`
- `017641`: `top_equity_table_row`

Out of scope and preserved as blocked residuals:

- `manager`
- retained `risk`
- `006597` `top_bond_table_row`
- `110020` `target_etf_holding`

No extractor/source/provider/runtime/config/golden/readiness code was modified. No PDF, `FundDocumentRepository`, network, fallback, live LLM, endpoint/DNS/curl/socket/provider probe or fixture projection was used.

## Files Changed

- `tests/fund/test_small_golden_set_extractor_correctness.py`
  - Imported `extract_holdings_share_change`.
  - Added equity-like holdings route metadata for `004393`, `004194` and `017641`.
  - Added test-local minimal `ParsedTable` construction from retained oracle expected holdings values.
  - Added a test-local raw-header adapter from current extractor row keys to oracle canonical keys.
  - Added passing assertions for `holdings_snapshot.extraction_mode == "direct"`, non-null value, current `top_holdings_status` / `top_holdings_source`, first top holdings row equality and anchors.
  - Split unsupported markers so `manager` and `risk` remain strict xfail, while `006597` and `110020` holdings remain strict xfail outside the equity-like subset.
- `tests/README.md`
  - Updated the small golden set row-field correctness description to include equity-like holdings assertions.

## Validation Results

```text
uv run pytest tests/fund/test_small_golden_set_extractor_correctness.py -q
................xxxx                                                     [100%]
16 passed, 4 xfailed in 0.84s
```

```text
uv run pytest tests/fund/test_small_golden_set_manifest.py tests/fund/test_small_golden_set_fixture_shape.py tests/fund/test_small_golden_set_source_identity.py tests/fund/test_small_golden_set_parser_mechanics.py tests/fund/test_small_golden_set_extractor_correctness.py -q
.....................................xxxx                                [100%]
37 passed, 4 xfailed in 0.51s
```

```text
uv run ruff check tests/fund/test_small_golden_set_extractor_correctness.py
All checks passed!
```

```text
git diff --check -- tests/fund/test_small_golden_set_extractor_correctness.py tests/README.md docs/reviews/mvp-small-golden-set-row-field-equity-like-holdings-test-extension-implementation-evidence-20260609.md
<no output>
```

## Residuals

- `manager` remains blocked pending a portfolio-manager row-shape contract decision.
- retained `risk` remains blocked pending a risk-characteristic row-shape contract decision.
- `006597` bond top holding remains blocked pending a holdings row-shape contract decision.
- `110020` target ETF holding remains blocked pending a holdings row-shape contract decision.
- This gate proves only current extractor-consumable row-field behavior from a retained oracle-built minimal table. It does not prove real PDF parser fidelity or authorize extractor fixes, fixture projection, golden/readiness promotion or production source acquisition.

## Self-check

- Current role stayed implementation worker only.
- Edits stayed within allowed files.
- No commit, push, PR, merge, mark-ready or external state update was performed.
- Stop conditions did not trigger: the required comparison used only a test-local raw-header adapter and did not require production normalization.
