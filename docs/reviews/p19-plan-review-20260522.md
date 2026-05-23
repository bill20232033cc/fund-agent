# P19 Plan Review（2026-05-22）

## Verdict

`BLOCKED_BEFORE_IMPLEMENTATION`

P19 independent thermometer direction is accepted, but the current plan cannot enter implementation yet. The blocking issue is data-source feasibility: the proposed akshare functions in the input plan do not match the currently installed akshare API surface, and the all-A PE history path is not yet proven.

## Reviewed Inputs

| Input | Role |
|---|---|
| `docs/p19-thermometer-technical-proposal.md` | Technical proposal |
| `docs/design-md-v22-changes.md` | Design change input |
| `docs/p19-phase-definition.md` | Phase definition |
| `docs/design.md` v2.2 | Design truth after P19 fusion |
| `docs/implementation-control.md` | Control truth |

## Local Feasibility Evidence

Environment:

- Project `.venv` has akshare `1.18.60`.
- `pyproject.toml` declares `akshare>=1.15` and `pandas`; it does not declare `pyarrow` or `fastparquet`.
- Bare `python` in the shell did not have akshare installed, so P19 verification and implementation must use `.venv` / project environment.

API surface checked in akshare `1.18.60`:

| API | Exists? | Review result |
|---|---:|---|
| `stock_zh_a_spot_em()` | yes | Candidate realtime all-A spot path, but current call failed with `ProxyError`; cannot be sole production truth |
| `stock_a_lg_indicator()` | no | Input proposal references a missing function |
| `index_value_hist_funddb()` | no | Input proposal references a missing function |
| `stock_a_all_pb()` | yes | All-A PB history candidate; returned 5184 rows from 2005-01-04 to 2026-05-22 |
| `stock_market_pe_lg(symbol="上证")` | yes | Market PE candidate, but not all-A and only 330 rows in local check |
| `stock_market_pb_lg(symbol="上证")` | yes | Market PB candidate; returned 5191 rows |
| `stock_index_pe_lg(symbol="沪深300")` | yes | Index PE candidate; returned 5130 rows |
| `stock_index_pb_lg(symbol="沪深300")` | yes | Index PB candidate; returned 5130 rows |
| `stock_zh_index_value_csindex(symbol="000300")` | yes | CSIndex candidate; returned only 20 rows and no PB column in local check |

## Required Checklist

| 检查项 | 结论 |
|---|---|
| 设计边界 | Pass with correction. P19-S1/S2 fit `docs/design.md` §11; P19-S3 must remain the only automatic `valuation_state` integration gate. |
| 技术可行性 | Blocked. Index PE/PB is feasible for core broad indexes, but all-A PE history is not proven. |
| Exit Criteria 可验证性 | Partial. Unit/CLI/test criteria are verifiable, but "与有知有行页面方向对比" needs a stable fixture or explicit manual validation protocol. |
| Hard Constraints | Pass. Plan correctly rejects production dependence on Youzhiyouxing page scraping. |
| 分层边界 | Pass with correction. `ThermometerService` remains Service orchestration; akshare/httpx access belongs in Capability data source. |

## Mandatory Questions

### 1. 当前 `ThermometerService` 和 `FundThermometerAdapter` 的复用策略是什么？

`ThermometerService` should be reused and evolved as the stable Service entry point for `fund-analysis thermometer`. It should orchestrate explicit request parameters, cache policy, and output models while depending on Capability protocols.

`FundThermometerAdapter` should not be the P19 production source. It remains a transitional Youzhiyouxing public-page adapter and may be used only for comparison validation or fallback display if a later gate explicitly accepts that behavior. P19 production thermometer data must come from self-owned data-source protocols.

### 2. P19-S1 首次历史数据下载的耗时和存储量预估？

Current evidence is insufficient for the full P19-S1 target:

- `stock_a_all_pb()` returned 5184 rows in about 0.28s, so all-A PB history is small and cheap.
- A full all-A daily spot scrape failed through `stock_zh_a_spot_em()` with `ProxyError`, so realtime all-A PE/PB aggregation cannot be treated as reliable yet.
- A daily all-A PE history source has not been identified. If P19-S1 must reconstruct PE from per-stock daily data, the proposal's rough scale of 5000 stocks x 15 years x 250 days is large enough to require a dedicated backfill design and storage estimate before coding.

Plan review therefore blocks implementation until the all-A PE history path is replaced by a proven API or the MVP scope is narrowed.

### 3. 等权计算与有知有行结果偏差的接受标准？

Accept direction-first validation:

- primary pass standard: low/fair/high direction matches a captured comparison sample;
- secondary signal: numerical deviation should be explained and ideally within 10 degrees for comparable dates;
- non-goal: exact parity with Youzhiyouxing, because the precise algorithm is not public.

Comparison against Youzhiyouxing may not become the production truth source.

## Findings Summary

Detailed findings are in `docs/reviews/p19-plan-review-findings-20260522.md`.

Blocking findings:

- P19-F1: Proposed akshare functions are missing.
- P19-F2: All-A PE history source is unproven.
- P19-F3: Realtime all-A spot fallback currently failed with proxy/upstream error.

Non-blocking findings:

- P19-F4: Parquet dependency is not declared and needs a plan decision.
- P19-F5: Youzhiyouxing direction comparison needs a reproducible fixture/protocol.

## Accepted Execution Order

P19 execution order remains:

1. P19 plan correction and data-source feasibility validation.
2. P19-S1 all-A thermometer MVP only after all-A PE/PB history is proven or scope is narrowed.
3. P19-S2 broad-index thermometer using proven index PE/PB APIs.
4. P19-S3 automatic `analyze` valuation integration after S1/S2 readings are stable.
5. P19-S4 expanded index coverage.

## Next Gate

`P19 plan fix / data-source feasibility`.
