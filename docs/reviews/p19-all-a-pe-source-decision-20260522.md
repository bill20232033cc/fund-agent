# P19 All-A PE Source Decision（2026-05-22）

## Verdict

`SCOPE_CHANGE_ACCEPTED_BEFORE_IMPLEMENTATION`

P19 should continue, but not as the original "all-A market thermometer first" plan. The corrected implementation order is:

1. P19-S1: implement a self-owned 沪深300 index thermometer MVP with the common data-source Protocol, calculator, cache, CLI JSON output, and `unavailable` failure semantics.
2. P19-S2: add 中证500 and batch index query once the PB endpoint is revalidated under retry/cache handling.
3. P19-S5 / all-A PE source gate: implement the full all-A market thermometer only after a verified all-A PE historical source exists.

PB-only all-A output must not be presented as a complete thermometer. Youzhiyouxing public-page scraping must not be used as the production truth source.

## Evidence

Local environment:

| Item | Result |
|---|---|
| akshare package | `.venv` akshare 1.18.60 |
| `stock_a_lg_indicator()` | Missing |
| `index_value_hist_funddb()` | Missing |
| `stock_a_all_pb()` | Verified previously: 5184 rows, 2005-01-04 to 2026-05-22 |
| `stock_index_pe_lg("沪深300")` | Verified in latest run: 5130 rows, 2005-04-08 to 2026-05-22 |
| `stock_index_pe_lg("中证500")` | Verified in latest run: 4701 rows, 2007-01-15 to 2026-05-22 |
| `stock_index_pb_lg(...)` | Previously verified for 沪深300; latest live run showed SSL/Proxy instability, so implementation must add retry/cache/unavailable semantics |
| `stock_zh_a_spot_em()` | Previously failed locally with `ProxyError`; cannot be sole production path |

Direct Legulegu endpoint probes using the same token approach as `stock_a_all_pb()`:

| Endpoint | Result |
|---|---|
| `/api/stock-data/market-index-pe?marketId=ALL` | 404 |
| `/api/stock-data/market-index-ttm-pe?marketId=ALL` | 404 |
| `/api/stock-data/market-index-lyr-pe?marketId=ALL` | SSL EOF in probe |
| `/api/stock-data/market-pe?marketId=ALL` | 200 with empty body |

This is enough to reject the assumption that a symmetric all-A PE historical endpoint is available in the current akshare / Legulegu path.

## First-Principles Judgment

A thermometer reading is only useful if it has both PE and PB history, a reproducible percentile window, and a clear unavailable state. An all-A PB-only series does not satisfy the stated method, because it drops half of the valuation signal while preserving the same user-facing noun. That would create false confidence.

The smallest honest deliverable is therefore an index thermometer whose PE/PB history is directly obtainable and fixture-testable. This keeps the architecture work valuable: the same Protocol, calculator, cache, CLI, and output model can later support all-A once the all-A PE source exists.

## Accepted Scope Change

| Slice | Corrected scope |
|---|---|
| P19-S1 | 沪深300指数温度计 MVP: types, Protocol, calculator, cache, CLI, JSON, unavailable semantics |
| P19-S2 | 中证500 + batch index query |
| P19-S3 | Analyze integration gate only after supported index readings are stable |
| P19-S4 | Additional supported indices |
| P19-S5 | Full all-A market thermometer after all-A PE history source verification |

## Next Gate

`P19-S1 corrected index thermometer MVP plan/review`

The implementation plan must explicitly answer:

- Which PE/PB columns are selected from `stock_index_pe_lg()` / `stock_index_pb_lg()` and why.
- Whether cache uses parquet or a no-new-dependency format.
- How live akshare failures become `unavailable` without fallback to Youzhiyouxing scraping.
- How `ThermometerService` evolves while `FundThermometerAdapter` remains transitional comparison-only code.
