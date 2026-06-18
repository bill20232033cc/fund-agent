# MVP Small Golden Set Row-field Equity-like Holdings Test Extension — Code Review (MiMo)

## Gate

- Gate: `row-field correctness test extension gate for retained equity-like holdings subset`
- Classification: `standard`
- Date: 2026-06-09
- Baseline checkpoint: `fc80d3d gateflow: accept row-field extractor gap decision`
- Reviewer: AgentMiMo
- Role: independent code review worker only

## Review Target

Current unstaged implementation diff only:

- `tests/fund/test_small_golden_set_extractor_correctness.py`
- `tests/README.md`
- `docs/reviews/mvp-small-golden-set-row-field-equity-like-holdings-test-extension-implementation-evidence-20260609.md`

## Source/Control Docs Read

- `AGENTS.md`
- `docs/current-startup-packet.md`
- `docs/implementation-control.md`
- `docs/design.md`
- `docs/reviews/mvp-small-golden-set-row-field-extractor-gap-decision-gate-controller-judgment-20260609.md`
- `docs/reviews/mvp-small-golden-set-row-field-extractor-gap-decision-gate-20260609.md`
- `docs/reviews/mvp-small-golden-set-row-field-equity-like-holdings-test-extension-implementation-evidence-20260609.md`
- `docs/reviews/mvp-small-golden-set-retained-excerpt-fixture-pdf-only-20260609.json`

## Findings

No blocking findings.

### F1 [INFO] `_build_report_from_oracle_row` now always includes §8 section in report structure

`_build_report_from_oracle_row` unconditionally adds `§8 投资组合报告` to `raw_text` and the `sections` dict, even when `include_holdings=False`. This means existing profile and performance tests now receive a report with a §8 section that has no corresponding table. This is benign because `extract_profile` and `extract_performance` only consume §1/§2 and §3 respectively, but it is a behavioral change to the shared test helper that differs from the prior state (which only went up to §3).

**Risk**: None — existing tests pass unchanged and §8 content does not interfere with profile/performance extractors.

### F2 [INFO] `holdings` removed from `SAME_SOURCE_UNSUPPORTED_FIELDS`

Previously `SAME_SOURCE_UNSUPPORTED_FIELDS = {"manager", "holdings", "risk"}`; now `{"manager", "risk"}`. This is correct per the gate decision: equity-like holdings now have passing assertions, and unsupported holdings (006597, 110020) are covered by the new `UNSUPPORTED_HOLDINGS_ROWS` xfail test. No residual coverage gap.

### F3 [INFO] `HOLDINGS_RAW_KEY_ADAPTER` mapping scope

The `HOLDINGS_RAW_KEY_ADAPTER` constant and `_adapt_raw_holding_row` function are test-local and explicitly documented as "仅用于本测试的 canonical 持仓字段字典". They do not leak into production code. The raw-header to canonical-key mapping (`股票代码→code`, `股票名称→name`, `公允价值→fair_value_cny`, `占基金资产净值比例→net_asset_ratio`) is used only in assertions, not in extractor logic. Consistent with gate decision stop condition: "test-local comparison adapter" approach.

### F4 [INFO] xfail test pattern for unsupported holdings

`test_same_source_holdings_rows_outside_equity_like_subset_remain_blocked` correctly uses the same xfail pattern as the existing `test_same_source_fields_without_current_row_consumer_are_blocked_gaps`: it verifies oracle data exists (expected values, anchor, excerpt) then asserts `fund_code not in UNSUPPORTED_HOLDINGS_ROWS` which always fails, marking the test as strict xfail. This correctly blocks 006597 bond and 110020 target ETF holdings from passing correctness.

## Scope Validation Notes

| Criterion | Status | Detail |
|---|---|---|
| Only test/evidence/docs changes | PASS | Diff touches only `tests/fund/test_small_golden_set_extractor_correctness.py` and `tests/README.md`; evidence doc is new untracked file |
| No extractor/source/provider/runtime/config/golden/readiness changes | PASS | Zero production code changes |
| Correctness oracle: only accepted retained excerpt JSON | PASS | `ORACLE_PATH` → accepted retained excerpt fixture; synthetic fixtures explicitly excluded by existing test |
| Holdings route: passing only for 004393/004194/017641 equity-like rows | PASS | `EQUITY_LIKE_HOLDINGS_ROWS` contains exactly these three; `test_holdings_extractor_matches_same_source_equity_like_top_row` parametrized over exactly these three |
| Blocked residuals: manager, risk, 006597, 110020 remain blocked | PASS | `manager`/`risk` in `SAME_SOURCE_UNSUPPORTED_FIELDS` xfail; `006597`/`110020` in `UNSUPPORTED_HOLDINGS_ROWS` xfail |
| Test-local raw-header mapping only | PASS | `HOLDINGS_RAW_KEY_ADAPTER` and `_adapt_raw_holding_row` are test-local, not imported by production |
| Validation evidence credible | PASS | `16 passed, 4 xfailed` confirmed (0.54s vs reported 0.84s — timing variance); full suite `37 passed, 4 xfailed` confirmed (0.48s vs 0.51s); ruff clean; `git diff --check` clean |

## Verdict

**PASS** — No blocking findings. The implementation correctly extends row-field correctness tests for the three accepted equity-like holdings rows (004393, 004194, 017641) using only the accepted retained excerpt oracle, keeps all blocked residuals (manager, risk, 006597 bond holding, 110020 target ETF holding) as strict xfail markers, uses a test-local raw-header adapter that does not imply production normalization, and stays within the authorized scope of the gap decision gate.
