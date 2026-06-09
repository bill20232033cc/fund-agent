# MVP Small Golden Set Row-field Equity-like Holdings Test Extension Controller Judgment

## Gate

- Gate: `row-field correctness test extension gate for retained equity-like holdings subset`
- Classification: `standard`
- Date: 2026-06-09
- Controller: AgentController
- Baseline checkpoint: `fc80d3d gateflow: accept row-field extractor gap decision`
- Implementation evidence: `docs/reviews/mvp-small-golden-set-row-field-equity-like-holdings-test-extension-implementation-evidence-20260609.md`

## Scope Judgment

Accepted locally as a test-only extension. The implementation adds same-source passing assertions for the retained equity-like holdings subset and does not modify extractor code, source acquisition, parser/FDR/PDF access, provider/default/runtime/budget/config, fixture projection, golden/readiness semantics, release state or PR state.

The only correctness oracle remains `docs/reviews/mvp-small-golden-set-retained-excerpt-fixture-pdf-only-20260609.json`.

## Accepted Implementation

| Area | Accepted result |
|---|---|
| Equity-like passing holdings rows | `004393` `top_stock_table_row`; `004194` `top_index_stock_table_row`; `017641` `top_equity_table_row` |
| Current extractor surface | `extract_holdings_share_change(report).holdings_snapshot.top_holdings` |
| Comparison strategy | Test-local raw-header adapter only; no production normalization |
| Blocked residuals preserved | `manager`, retained `risk`, `006597` bond top holding, `110020` target ETF holding |
| Documentation sync | `tests/README.md` updated for row-field correctness coverage |

## Review Inputs

| Reviewer | Artifact | Verdict |
|---|---|---|
| AgentDS | `docs/reviews/mvp-small-golden-set-row-field-equity-like-holdings-test-extension-code-review-ds-20260609.md` | PASS; no blocking findings |
| AgentMiMo | `docs/reviews/mvp-small-golden-set-row-field-equity-like-holdings-test-extension-code-review-mimo-20260609.md` | PASS; no blocking findings |

## Controller Finding Decisions

| Review observation | Decision | Rationale |
|---|---|---|
| DS/MiMo noted `_build_report_from_oracle_row()` now always includes a minimal §8 section and adjusts §3 end offset | Accepted as non-blocking | The helper remains test-local, the §8 text contains no extractor table keywords, existing profile/performance assertions still pass, and the change keeps section offsets monotonic after adding holdings tests |
| DS noted the raw-header adapter omits quantity | Accepted as in-scope | The accepted oracle has no quantity expected value for this gate; asserting only `code`, `name`, `fair_value_cny` and `net_asset_ratio` is the exact retained excerpt scope |
| DS noted unsupported holdings xfail uses an impossible final assertion | Accepted as existing blocked-gap pattern | This mirrors the existing strict xfail marker pattern and preserves fail-closed residual visibility for `006597` and `110020` until a future row-shape contract decision |

No fix or re-review is required because all findings are informational/non-blocking and do not change the accepted gate outcome.

## Validation

Controller reran the required local validations:

```text
uv run pytest tests/fund/test_small_golden_set_extractor_correctness.py -q
................xxxx                                                     [100%]
16 passed, 4 xfailed in 0.42s
```

```text
uv run pytest tests/fund/test_small_golden_set_manifest.py tests/fund/test_small_golden_set_fixture_shape.py tests/fund/test_small_golden_set_source_identity.py tests/fund/test_small_golden_set_parser_mechanics.py tests/fund/test_small_golden_set_extractor_correctness.py -q
.....................................xxxx                                [100%]
37 passed, 4 xfailed in 0.43s
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

| Residual | Required next gate |
|---|---|
| Portfolio-manager identity and tenure (`manager`) | Row-shape contract decision before tests |
| Retained risk-characteristic text (`risk`) | Row-shape contract decision before tests |
| `006597` bond top holding | Holdings row-shape contract decision before tests |
| `110020` target ETF holding | Holdings row-shape contract decision before tests |
| Real PDF parser fidelity | Separately authorized parser/FDR/PDF evidence gate |

## Next Entry Point

Open `row-shape contract decision gate for retained manager / risk / non-equity holdings residuals`, or a separately authorized non-extractor phase.

That next gate must not modify extractor code or write new passing correctness tests until it accepts exact output contracts and same-source test targets. If it changes public extractor output contracts or schema semantics, classify it as `heavy`.

## Final Judgment

Accepted locally.
