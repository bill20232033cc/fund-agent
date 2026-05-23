# P19 Plan Fix: Data Source Feasibility（2026-05-22）

## Verdict

`PARTIAL_FIX_ACCEPTED_STILL_BLOCKED`

The P19 technical proposal and phase definition have been corrected to stop assuming unavailable akshare functions. Implementation remains blocked until the all-A PE history path is proven or the P19-S1 scope is explicitly changed.

## What Changed

| File | Change |
|---|---|
| `docs/p19-thermometer-technical-proposal.md` | Replaced missing `stock_a_lg_indicator()` / `index_value_hist_funddb()` assumptions with verified akshare 1.18.60 interface evidence |
| `docs/p19-thermometer-technical-proposal.md` | Marked all-A PE history as a P19-S1 blocker |
| `docs/p19-thermometer-technical-proposal.md` | Clarified that `stock_zh_a_spot_em()` failed locally with `ProxyError` and cannot be the sole production truth |
| `docs/p19-phase-definition.md` | Updated P19-S1 entry/exit criteria to require a verified all-A PE source or an accepted scope change |

## Verified Candidate Interfaces

| Interface | Candidate use | Status |
|---|---|---|
| `stock_a_all_pb()` | all-A PB history | Verified usable locally: 5184 rows, 2005-01-04 to 2026-05-22 |
| `stock_index_pe_lg(symbol="沪深300")` | broad-index PE history | Verified usable locally: 5130 rows |
| `stock_index_pb_lg(symbol="沪深300")` | broad-index PB history | Verified usable locally: 5130 rows |
| `stock_zh_index_value_csindex(symbol="000300")` | CSIndex short-window valuation | Exists, but local sample only had 20 rows and no PB |
| `stock_zh_a_spot_em()` | realtime all-A spot fallback | Exists, but local call failed with `ProxyError` |

Additional segmented-market checks were mixed:

| Interface | Result |
|---|---|
| `stock_market_pe_lg(symbol="深证")` | Success: 342 rows, 1997-12-31 to 2026-05-22 |
| `stock_market_pe_lg(symbol="创业板")` | Success: 192 rows, 2010-06-30 to 2026-05-22 |
| `stock_market_pb_lg(symbol="上证")` | Success: 5191 rows, 2005-01-04 to 2026-05-22 |
| `stock_market_pb_lg(symbol="科创版")` | Success: 1655 rows, 2019-07-23 to 2026-05-22 |
| `stock_market_pe_lg(symbol="上证")` | Failed in batch check with SSL EOF |
| `stock_market_pe_lg(symbol="科创版")` | Failed in batch check with SSL EOF |
| `stock_market_pb_lg(symbol="深证")` | Failed in batch check with SSL EOF |
| `stock_market_pb_lg(symbol="创业板")` | Failed in batch check with `ProxyError` |

This supports a conservative conclusion: segmented market endpoints may be useful for research or fallback, but they are not yet a stable P19-S1 production plan without retries, caching, and unavailable semantics.

## Remaining Blocker

P19-S1 still lacks a proven all-A PE historical series. There are two acceptable next paths:

1. Find and verify a real all-A PE history source, then proceed with the original PE+PB all-market thermometer.
2. Propose a design/control scope change: for example, defer all-A PE, start with verified broad-index PE/PB, or make an explicit PB-only all-market experimental reading with no `analyze` integration.

## Next Gate

`P19 plan fix / all-A PE source decision`.
