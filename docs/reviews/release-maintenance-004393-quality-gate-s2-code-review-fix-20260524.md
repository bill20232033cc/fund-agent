# Release Maintenance 004393 Quality Gate S2 Code Review Fix - 2026-05-24

## Gate

- Work unit: `004393/2024 quality gate block root-cause investigation`
- Slice: `S2 - P1 Extraction And Benchmark Correctness`
- Role: S2 fix worker
- Controller judgment: `docs/reviews/release-maintenance-004393-quality-gate-s2-code-review-controller-judgment-20260524.md`
- Result: `ready_for_rereview: true`

## Changed Files

- `fund_agent/fund/extractors/holdings_share_change.py`
- `fund_agent/fund/extraction_score.py`
- `tests/fund/extractors/test_holdings_share_change.py`
- `tests/fund/test_extraction_score.py`
- `docs/reviews/release-maintenance-004393-quality-gate-s2-code-review-fix-20260524.md`

## Finding Closure

### `004393-S2-C1`

Closed. `holdings_snapshot` score coverage now uses an explicit `(top_holdings_status, top_holdings_source)` allowlist:

- `direct_top_ten` / `top_ten`
- `direct_all_stock_details` / `all_stock_investment_details`

Missing `comparable_values`, empty status/source, unknown status/source, and inconsistent status/source pairs no longer satisfy coverage. Added score tests for absent, empty, unknown, inconsistent, and valid status/source cases.

### `004393-S2-C2`

Closed. Split share-change continuation now requires:

- bounded page/table-order evidence: same page adjacent table index, or next page first-table continuation;
- header table and data table both match their split-table semantics;
- inherited A/C class header count exactly equals data value column count.

If those checks fail, the tables are not merged. Added tests for unrelated adjacent header-like tables and mismatched header/data column count. A blank single-value data-table header also fails closed, preventing an unmerged parser fragment from being accepted as a safe one-column table.

### `004393-S2-C3`

Closed. `_select_share_change_value_column()` now evaluates exact current fund-code match and any non-current fund-code conflict before single-value fallback. A single value column whose header contains another six-digit fund code returns missing instead of being accepted. Added a regression test for the single-column non-current fund-code case.

## Validation

```bash
uv run pytest tests/fund/extractors/test_holdings_share_change.py tests/fund/test_extraction_snapshot.py tests/fund/test_extraction_score.py tests/fund/test_quality_gate.py -q
```

Result: `80 passed`.

```bash
uv run ruff check fund_agent/fund/extractors/holdings_share_change.py fund_agent/fund/extraction_snapshot.py fund_agent/fund/extraction_score.py fund_agent/fund/quality_gate.py tests/fund/extractors/test_holdings_share_change.py tests/fund/test_extraction_snapshot.py tests/fund/test_extraction_score.py tests/fund/test_quality_gate.py
```

Result: passed.

```bash
git diff --check
```

Result: passed.

## Residual Risks

- `ParsedTable` still does not expose explicit parser section metadata, so split-table bounding uses available page/table-order evidence and deterministic column mapping, not physical section provenance.
- The accepted next-page continuation pattern is conservative for the observed 004393 shape, but broader multi-page parser continuation remains outside this S2 fix.
