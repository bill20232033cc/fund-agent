# P19 Plan Review Findings（2026-05-22）

## P19-F1: Proposed akshare functions are missing

Severity: `BLOCKING`

The technical proposal references `ak.stock_a_lg_indicator()` and `ak.index_value_hist_funddb(...)`, but akshare `1.18.60` in the project `.venv` does not expose these functions.

Impact: implementation based on the proposal would fail immediately.

Required handling: update the plan to use verified functions only, such as `stock_a_all_pb`, `stock_index_pe_lg`, `stock_index_pb_lg`, and any separately proven all-A PE source.

## P19-F2: All-A PE history source is unproven

Severity: `BLOCKING`

`stock_a_all_pb()` provides all-A PB history, including middle PB and equal-weight average PB, but an equivalent all-A PE historical series has not been identified. `stock_market_pe_lg(symbol="上证")` is not the same as all-A PE and returned only 330 rows in local verification.

Impact: P19-S1's core PE/PB combined temperature cannot be implemented as specified.

Required handling: either find and verify an all-A PE historical source, or narrow P19-S1 to PB-only/proven-market-scope with an explicit design change and revised exit criteria.

## P19-F3: Realtime all-A spot fallback currently fails

Severity: `BLOCKING`

`ak.stock_zh_a_spot_em()` exists, but a local call failed with a `ProxyError` to Eastmoney. It may still be useful with retries or network configuration, but current evidence does not support it as a reliable P19-S1 path.

Impact: reconstructing current-day all-A PE/PB from spot data is not yet safe.

Required handling: validate network behavior, retry taxonomy, unavailable semantics, and whether the function exposes stable PE/PB columns before implementation.

## P19-F4: Parquet dependency is undecided

Severity: `NON_BLOCKING`

P19 proposes parquet cache, but neither `pyarrow` nor `fastparquet` is declared in `pyproject.toml`.

Impact: implementation would require a dependency change or a different cache format.

Required handling: decide in plan review whether parquet is necessary for P19-S1, and if yes choose one dependency with tests and lockfile update.

## P19-F5: Youzhiyouxing comparison needs a reproducible protocol

Severity: `NON_BLOCKING`

"与有知有行页面方向对比验证通过" is useful but not currently automated. It also risks reintroducing page scraping as an implicit source if not scoped carefully.

Impact: acceptance could become manual or flaky.

Required handling: use a captured fixture or explicit manual validation artifact. The comparison must remain validation/reference only, not production truth.
