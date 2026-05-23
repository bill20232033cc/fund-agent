# P19-S4 Source Feasibility（2026-05-23）

## Verdict

`BLOCKED_DEFERRED`

No design-allowed source in the local akshare `1.18.60` package or minimally probed official endpoints provides complete exact-index PE+PB historical series for the P19-S4 target set:

- 创业板指 `399006`
- 科创50 `000688`
- 中证红利 `000922`
- 中证消费 `000932`
- 中证医药 `000933`

The best official 中证 path, `stock_zh_index_value_csindex`, proves exact identity and returns recent PE fields for `000688`, `000922`, `000932`, and `000933`, but it has no PB field and only returned 20 rows in the probe. 国证/CNI proves `399006` identity and current PE, but not PE+PB history. Therefore P19-S4 cannot implement the self-owned thermometer without changing the algorithm/source contract. A PE-only, dividend-yield, current-valuation, constituents, weights, or adjacent-index result is not a valid P19 thermometer.

## Inputs Read

- `docs/reviews/p19-s4-expanded-index-coverage-plan-20260523.md`
- `docs/reviews/p19-s4-plan-review-controller-judgment-20260523.md`
- `docs/design.md` §11.4 / §11.5

## Feasibility Criteria

An acceptable P19-S4 source must prove, per exact target index:

- exact index identity;
- PE history field and field semantics;
- PB history field and field semantics;
- date schema;
- numeric schema;
- historical rows and common PE/PB date count, with at least the existing thermometer minimum of 30 common dates;
- latest date;
- a source contract usable from Capability data without UI/Service scraping.

Rejected by design:

- PE without PB;
- PB without PE;
- dividend yield as PB substitute;
- current-only valuation;
- constituents or weights as valuation;
- adjacent indexes such as 创业板50, 上证红利, 深证红利, 中证1000;
- Youzhiyouxing public page scraping as production truth.

## Akshare Candidate Discovery

Environment:

```text
akshare_version 1.18.60
```

Relevant functions discovered from `dir(akshare)` and source search:

| Function | Source family | Relevant output | Feasibility decision |
|---|---|---|---|
| `stock_index_pe_lg` | Legulegu index PE | PE history for a fixed symbol map | Already blocked: P19-S4 exact targets absent |
| `stock_index_pb_lg` | Legulegu index PB | PB history for a fixed symbol map | Already blocked: P19-S4 exact targets absent |
| `stock_zh_index_value_csindex` | 中证官方 indicator XLS | PE1, PE2, dividend yield 1/2 | PE-only, no PB; insufficient |
| `index_csindex_all` | 中证官方 index list | identity/list metadata | identity only; no PE/PB history |
| `stock_zh_index_hist_csindex` | 中证官方 index performance | OHLC, sample count, rolling PE | no PB; not enough |
| `index_stock_cons_weight_csindex` | 中证官方 weights | constituents and weights | no PE/PB history |
| `index_stock_cons_csindex` | 中证官方 constituents | constituents | no PE/PB history |
| `index_all_cni` | 国证 index list/current quote | current PE rolling for `399006` | current PE only, no PB history |
| `index_hist_cni` | 国证 index history | OHLC history | no PE/PB history |
| `index_detail_cni` / `index_detail_hist_cni` | 国证 constituents | constituents, market cap, weights | not valuation history |
| `stock_market_pe_lg` / `stock_market_pb_lg` | Legulegu market-level PE/PB | 创业板/科创板 market PE/PB | market-level, not exact target index |
| `stock_hk_indicator_eniu` | Enniu HK stock indicator | HK individual security PE/PB | not A-share index source |
| `stock_zh_index_daily*` / `stock_zh_index_spot_*` | price/spot providers | OHLC/spot data | no PE/PB history |
| `stock_value_em`, `stock_zh_valuation_*` | stock-level valuation | individual stock valuation | not index source |

## Official 中证 / `stock_zh_index_value_csindex` Probe

Akshare implementation:

```text
stock_zh_index_value_csindex(symbol)
URL: https://oss-ch.csindex.com.cn/static/html/csindex/public/uploads/file/autofile/indicator/{symbol}indicator.xls
Fields after akshare normalization:
日期, 指数代码, 指数中文全称, 指数中文简称, 指数英文全称, 指数英文简称,
市盈率1, 市盈率2, 股息率1, 股息率2
```

Field semantics from raw XLS header:

- `市盈率1（总股本）P/E1`
- `市盈率2（计算用股本）P/E2`
- `股息率1（总股本）D/P1`
- `股息率2（计算用股本）D/P2`

There is no PB / 市净率 field.

| Code | Target | HEAD/GET | Exact identity | Rows | Date range | PE field | PB field | Common PE/PB dates | Decision |
|---|---|---|---|---:|---|---|---|---:|---|
| `399006` | 创业板指 | HEAD 404, GET 404, akshare HTTP 404 | no | 0 | none | unavailable | unavailable | 0 | blocked |
| `000688` | 科创50 | HEAD 200, GET 200 `application/vnd.ms-excel` | yes: `000688`, `科创50` | 20 | 2026-04-24 to 2026-05-22 | `市盈率1`, `市盈率2` | none | 0 | blocked |
| `000922` | 中证红利 | HEAD 200, GET 200 `application/vnd.ms-excel` | yes: `000922`, `中证红利` | 20 | 2026-04-24 to 2026-05-22 | `市盈率1`, `市盈率2` | none | 0 | blocked |
| `000932` | 中证消费 | HEAD 200, GET 200 `application/vnd.ms-excel` | yes: `000932`, `800消费` / 中证主要消费指数 | 20 | 2026-04-24 to 2026-05-22 | `市盈率1`, `市盈率2` | none | 0 | blocked |
| `000933` | 中证医药 | HEAD 200, GET 200 `application/vnd.ms-excel` | yes: `000933`, `800医卫` / 中证医药卫生指数 | 20 | 2026-04-24 to 2026-05-22 | `市盈率1`, `市盈率2` | none | 0 | blocked |

Conclusion: this official 中证 source is useful for identity and PE-only current/recent checks, but it cannot drive the existing PE+PB percentile thermometer.

## 中证 Identity List Probe

`index_csindex_all()` returned 2340 rows with fields including `指数代码`, `指数简称`, `指数全称`, `基日`, `发布时间`.

| Code | Target | Match | Notes |
|---|---|---|---|
| `399006` | 创业板指 | no | not a 中证 index entry |
| `000688` | 科创50 | no via list probe | indicator XLS proves identity even though list probe did not match |
| `000922` | 中证红利 | yes | `中证红利指数`, base date 2004-12-31, publish date 2008-05-26 |
| `000932` | 中证消费 | yes | `中证主要消费指数`, short name `800消费`, publish date 2009-07-03 |
| `000933` | 中证医药 | yes | `中证医药卫生指数`, short name `800医卫`, publish date 2009-07-03 |

Identity evidence alone is insufficient because the thermometer requires PE+PB history.

## 国证 / 深证 Probe For `399006`

`index_all_cni()` returned one exact row for `399006`:

```text
指数代码=399006
指数简称=创业板指
样本数=100
收盘点位=3829.7786
PE滚动=40.4603
```

This proves exact identity and a current rolling PE value, but not historical PE+PB.

`index_hist_cni(symbol="399006", start_date="20240101", end_date="20260523")` returned:

```text
rows=575
columns=日期, 开盘价, 最高价, 最低价, 收盘价, 涨跌幅, 成交量, 成交额
date range=2024-01-02 to 2026-05-22
```

Direct raw JSON check for `http://hq.cnindex.com.cn/market/market/getIndexDailyDataWithDataFormat` confirmed each row has 11 values: date, OHLC-like values, change, percent change, amount, volume, and a trailing null. No PE/PB history fields are present in this endpoint response.

`index_detail_cni` and `index_detail_hist_cni` returned 100 constituent rows with fields:

```text
日期, 样本代码, 样本简称, 所属行业, 总市值, 权重
```

Constituents and weights are not a PE+PB history source.

## Legulegu Market-Level Probe

The market-level Legulegu functions work for board/market concepts but are not exact target indexes:

| Function | Symbol | Rows | Fields | Why rejected |
|---|---|---:|---|---|
| `stock_market_pe_lg` | 创业板 | 192 | `日期`, `指数`, `平均市盈率` | market-level monthly-ish PE, not 创业板指 exact PE+PB |
| `stock_market_pb_lg` | 创业板 | 4020 | `日期`, `指数`, `市净率`, `等权市净率`, `市净率中位数` | market-level PB, not 创业板指 exact PE+PB; PE frequency/schema mismatch |
| `stock_market_pe_lg` | 科创版 | 1656 | `日期`, `总市值`, `市盈率` | market-level, not 科创50 exact index |
| `stock_market_pb_lg` | 科创版 | 1655 | `日期`, `指数`, `市净率`, `等权市净率`, `市净率中位数` | market-level, not 科创50 exact index |

These sources may be relevant to a future market/board thermometer design, but not P19-S4 expanded exact-index coverage.

## Per-Target Feasibility Matrix

| Code | Target | Exact identity proof | PE history | PB history | Rows / common dates | Latest date | Failure reason |
|---|---|---|---|---|---|---|---|
| `399006` | 创业板指 | yes via 国证 `index_all_cni` | current PE only via `PE滚动`; no verified PE history | none | 0 common PE/PB dates | current CNI row observed; OHLC latest 2026-05-22 | no exact PE+PB history source; 中证 indicator 404 |
| `000688` | 科创50 | yes via 中证 indicator XLS | PE1/PE2 recent 20 rows | none | 0 common PE/PB dates | 2026-05-22 | 中证 source lacks PB and <30 rows |
| `000922` | 中证红利 | yes via 中证 list + indicator XLS | PE1/PE2 recent 20 rows | none | 0 common PE/PB dates | 2026-05-22 | 中证 source lacks PB and <30 rows |
| `000932` | 中证消费 | yes via 中证 list + indicator XLS | PE1/PE2 recent 20 rows | none | 0 common PE/PB dates | 2026-05-22 | 中证 source lacks PB and <30 rows |
| `000933` | 中证医药 | yes via 中证 list + indicator XLS | PE1/PE2 recent 20 rows | none | 0 common PE/PB dates | 2026-05-22 | 中证 source lacks PB and <30 rows |

## Source Contract Assessment

No source contract is accepted for implementation.

Rejected candidate contract: `csindex_indicator_pe_only`

```text
API/URL: https://oss-ch.csindex.com.cn/static/html/csindex/public/uploads/file/autofile/indicator/{code}indicator.xls
akshare wrapper: stock_zh_index_value_csindex(symbol=code)
source_name candidate: csindex_indicator_pe_only
date schema: raw YYYYMMDD integer; akshare converts to date
numeric schema: 市盈率1/2 and 股息率1/2 numeric
identity: exact for 000688/000922/000932/000933
missing semantics: 399006 returns 404; no PB fields for all probed codes
fixture need if ever used: raw XLS-shaped fixture with bilingual headers
adapter need: new Capability data adapter would be required because schema differs from Legulegu PE/PB
rejection reason: no PB, only 20 rows in probe, not sufficient for current thermometer algorithm
```

Rejected candidate contract: `cni_current_pe_identity`

```text
API/URL: https://www.cnindex.com.cn/index/indexList and http://hq.cnindex.com.cn/market/market/getIndexDailyDataWithDataFormat
akshare wrappers: index_all_cni, index_hist_cni
source_name candidate: cni_current_pe_identity
date schema: mixed current row plus historical OHLC dates
numeric schema: current PE滚动 only in index list; historical endpoint has no PE/PB
identity: exact for 399006
adapter need: new adapter would be required
rejection reason: current PE only; no PB history
```

## Implementation Consequence

Do not implement P19-S4 source mappings in `fund_agent/fund/data/thermometer_source.py` from this feasibility result.

The next valid controller actions are:

- mark P19-S4 as deferred/blocked in `docs/implementation-control.md`; or
- open a new design gate to change the thermometer algorithm for PE-only official index indicators; or
- open a new source-acquisition gate for a verified PB history provider.

If the algorithm changes to PE-only, that is not P19-S4 as currently designed. It would require design and plan review because `docs/design.md` §11 defines the thermometer around PE/PB percentile synthesis.

## Residual Risks

- Official 中证 indicator files are reachable for some codes but appear to expose only recent PE and dividend-yield data, not full PE+PB history.
- 国证 provides exact `399006` identity and current PE, but no PB history.
- Akshare may add new wrappers later; this artifact is scoped to local `.venv` akshare `1.18.60` on 2026-05-23.
- Live endpoints may change schema or availability; future probes must re-record rows, fields, and exact identity.
- Future analyze automatic mapping for these indexes remains out of scope and must not be silently broadened from this feasibility work.

## Validation

```text
git diff --check
passed
```
