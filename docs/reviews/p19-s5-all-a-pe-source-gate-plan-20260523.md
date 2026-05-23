# P19-S5 All-A PE Source Gate Plan（2026-05-23）

## Verdict

`SOURCE_FEASIBILITY_FIRST`

P19-S5 must not implement code until the source gate proves a complete all-A PE+PB historical source contract. Current accepted evidence says all-A PB is available through akshare `stock_a_all_pb()`, and reviewer probe evidence shows an all-A PE candidate exists through akshare `stock_a_ttm_lyr()`. That PE candidate still requires source-contract validation before it can be accepted. PB-only output is explicitly rejected because `docs/design.md` §11 defines the thermometer as PE percentile plus PB percentile.

## Required Inputs Read

- `AGENTS.md`
- `docs/design.md` §11
- `docs/implementation-control.md` Startup Packet and P19-S5 exit criteria
- `docs/reviews/p19-plan-fix-data-source-20260522.md`
- `docs/reviews/p19-all-a-pe-source-decision-20260522.md`
- `docs/reviews/p19-s4-source-feasibility-controller-judgment-20260523.md`

## First-Principles Requirement

An all-A thermometer is not “any market valuation number.” It is a reproducible time series that can answer:

```text
today_all_a_temperature = percentile_rank(today_all_a_pe, historical_all_a_pe)
                          50%
                        + percentile_rank(today_all_a_pb, historical_all_a_pb)
                          50%
```

Therefore the minimum necessary facts are:

| Required fact | Why it is necessary |
|---|---|
| Exact all-A universe identity | Prevents board-level, broad-index, or partial-market data from masquerading as all-A. |
| All-A PE history | Supplies half of the thermometer signal. |
| All-A PB history | Supplies the other half of the thermometer signal. |
| Field semantics | Distinguishes median/equal-weight/market-weight/static/TTM metrics. |
| Weighting and statistic compatibility | Proves the source can satisfy the current design's equal-weight / median-oriented thermometer semantics. |
| PE/PB basis compatibility | Proves PE type and PB type match the accepted thermometer contract, or triggers a design decision before implementation. |
| Date schema | Allows strict merge and fail-closed parsing. |
| Numeric schema | Allows positive Decimal conversion and invalid-value rejection. |
| Historical coverage | Must cover enough history for percentile ranking; minimum common PE/PB dates >= current `MIN_HISTORY_POINTS`, with design preference for multiple cycles. |
| Missing-value rules | Defines whether a date is dropped, unavailable, or fail-closed. |
| License/use constraints | Ensures production use is allowed and does not depend on prohibited scraping. |
| Common date count | Proves PE and PB can be combined on the same dates. |
| Latest date | Proves freshness and cache staleness policy. |

Non-negotiable rule: PB-only, PE-only, current-only, dividend-yield-only, board-level, adjacent-index, or reconstructed data must not be presented as the P19 all-A thermometer.

## Candidate Sources To Probe

The source gate must probe every design-allowed and package-discoverable candidate below. It may add more candidates if discovered, but it must not skip these.

### Akshare / Legulegu

| Candidate | Known or suspected use | Required probe |
|---|---|---|
| `stock_a_all_pb()` | Known all-A PB history candidate | Revalidate fields, rows, date range, latest date, PB semantics, license hints. |
| `stock_a_ttm_lyr()` | Reviewer-identified all-A PE history candidate | Mandatory probe. Revalidate source module, URL/API, fields, rows, date range, latest date, PE semantics, missing rules, access/license hints, and common dates with `stock_a_all_pb()`. |
| `stock_a_lg_indicator()` | Previously assumed all-A PE/PB candidate | Confirm missing/present in installed akshare; if missing, classify `missing interface`. |
| `stock_market_pe_lg(symbol=...)` | Market/board PE history | Probe `上证`, `深证`, `创业板`, `科创版`; classify as board-level unless exact all-A is proven. |
| `stock_market_pb_lg(symbol=...)` | Market/board PB history | Probe `上证`, `深证`, `创业板`, `科创版`; classify board-level unless exact all-A is proven. |
| Direct Legulegu endpoints mirroring `stock_a_all_pb()` | Possible hidden all-A PE history | Probe likely endpoint names and `marketId=ALL`; record status/body/schema. |
| `stock_index_pe_lg` / `stock_index_pb_lg` | Index PE/PB history | Confirm not all-A; useful only as negative control. |
| `stock_a_all_pb` source implementation | PB endpoint source contract | Inspect local package implementation for URL, token, fields, and schema. |

Required direct Legulegu endpoint probes at minimum:

```text
https://legulegu.com/api/stock-data/market-ttm-lyr
https://legulegu.com/api/stock-data/market-index-pe?marketId=ALL
https://legulegu.com/api/stock-data/market-index-ttm-pe?marketId=ALL
https://legulegu.com/api/stock-data/market-index-lyr-pe?marketId=ALL
https://legulegu.com/api/stock-data/market-pe?marketId=ALL
```

Use the same token/cookie approach as the installed akshare implementation where applicable. Do not bypass auth or anti-scraping controls.

### Akshare package search

Search installed akshare for all PE/PB/valuation/index candidates:

```text
dir(akshare)
rg -n "all.*pe|pe.*all|市盈率|市净率|估值|valuation|index.*value|market.*pe|market.*pb"
  .venv/lib/python3.11/site-packages/akshare
```

Classify each discovered candidate as one of:

- exact all-A PE history candidate;
- exact all-A PB history candidate;
- board/market-level candidate;
- index-level candidate;
- stock-level candidate;
- current-only candidate;
- constituents/weights/price-only non-candidate.

### 东方财富 / 中证 / 交易所

Probe only public, design-allowed, minimal endpoints or akshare wrappers:

| Candidate | Expected risk | Required probe |
|---|---|---|
| `stock_zh_a_spot_em()` | current spot only; previous local `ProxyError` | Record availability and whether it includes current PE/PB only; not enough for history. |
| Eastmoney valuation endpoints discovered through akshare | likely stock-level or current-only | Record URL/API, fields, history availability, all-A identity. |
| `stock_zh_index_value_csindex` | index PE + dividend yield only | Confirm not all-A and no PB; negative control. |
| exchange index/value pages or downloadable files | likely price/index metadata | Minimal HEAD/GET; record auth/404/schema. |

Do not introduce paid sources or a new runtime dependency. If an official endpoint requires authentication, paid access, or browser-only flows, classify it as `auth` or `unavailable`, not as implementable.

## Probe Matrix

Every candidate must be recorded with this schema:

| Field | Description |
|---|---|
| candidate_id | Stable name, e.g. `akshare.stock_a_all_pb` or `legulegu.market-index-pe.ALL`. |
| command | Exact command or script used. |
| package_version | akshare version and Python environment. |
| url_or_api | Function name or URL. |
| identity_scope | all-A / board-level / index-level / stock-level / unknown. |
| universe_definition | Provider definition of the covered universe, including exclusions if available. |
| identity_reconciliation | Evidence that PE and PB source universes are the same or materially compatible. |
| license_or_access | public / auth required / paid / unknown. |
| pe_field | Field name and semantic meaning; `none` if absent. |
| pb_field | Field name and semantic meaning; `none` if absent. |
| weighting_method | equal-weight / market-cap-weight / unknown / other. |
| statistic_type | median / average / aggregate / unknown / other. |
| pe_basis | TTM / LYR / static / unknown / other. |
| pb_basis | PB median / PB equal-weight average / market-cap weighted PB / unknown / other. |
| rows | Number of rows returned. |
| date_min | Earliest date. |
| date_max | Latest date. |
| common_dates | PE/PB common date count if both fields exist. |
| latest_date | Latest usable date. |
| missing_rule | How null/non-positive values appear and should be handled. |
| failure_class | One of the failure classes below. |
| decision | accepted / rejected / needs design change / deferred. |

Failure classes:

| Failure class | Meaning |
|---|---|
| `missing_interface` | Function or endpoint is absent in installed akshare or source package. |
| `404` | Endpoint responds not found for the requested all-A path. |
| `auth` | Endpoint requires authentication, paid access, forbidden headers, or session not obtainable through normal public access. |
| `schema_drift` | Response structure exists but does not match documented fields or parseable table contract. |
| `no_pb` | PE exists but PB is absent. |
| `no_pe` | PB exists but PE is absent. |
| `current_only` | Only latest/current snapshot exists, no history. |
| `not_all_a` | Data is board-level, index-level, stock-level, industry-level, or otherwise not all-A. |
| `network_unavailable` | Timeout, DNS, proxy, SSL, or transient HTTP/network failure. |

## Acceptance Outcomes

### `ACCEPT_IMPLEMENTATION_PLAN`

Allowed only when the source gate proves:

- exact all-A identity;
- PE history and PB history exist from one compatible source family or two independently mergeable source contracts;
- both PE and PB fields have documented semantics;
- PE and PB match the current design's equal-weight / median-oriented thermometer semantics;
- PE type, such as TTM, LYR, or static PE, matches the existing accepted index thermometer PE basis or has an explicit design decision before implementation;
- PB basis matches the accepted PB thermometer contract;
- common PE/PB date count is sufficient;
- latest date is recent enough for cache freshness policy;
- use is public and does not violate non-goals;
- missing/null/non-positive value handling is documented;
- source-shaped fixtures can be created without live network dependence.

If accepted, the next gate is an implementation plan/review, not immediate coding. If `stock_a_ttm_lyr()` plus `stock_a_all_pb()` passes the source contract, the worker must still stop at `ACCEPT_IMPLEMENTATION_PLAN` and hand off to a separate implementation plan/review.

### `BLOCKED_DEFERRED`

Required when:

- no all-A PE candidate validates into an acceptable all-A PE history contract;
- no all-A PB history exists;
- access is not public or license/use is not acceptable;
- only current valuation is available;
- only board/index/stock-level substitutes are available;
- network failures prevent source proof and cannot be distinguished from unavailable source.

### `NEEDS_DESIGN_CHANGE`

Required when data exists but does not satisfy the current thermometer design, for example:

- PE-only official all-A series;
- PB-only all-A series;
- board-level PE/PB that could approximate market state;
- a derived rebuild path from constituents and stock-level valuations;
- separate PE and PB sources with materially different universe definitions.
- exact all-A PE/PB series whose weighting method, statistic type, PE basis, or PB basis does not match the current design.

This outcome must update `docs/design.md` before implementation and must pass a separate plan review.

## Implementation Plan Outline If Source Gate Passes

Only after `ACCEPT_IMPLEMENTATION_PLAN`, create a new implementation plan with these slices.

### Slice 1: Capability Data Adapter

Files likely touched:

- `fund_agent/fund/data/thermometer_source.py` or a new all-A source module
- `fund_agent/fund/data/thermometer_types.py`
- `tests/fund/data/...`

Plan:

- Add an all-A source adapter behind `ThermometerDataSource`-compatible protocol.
- Use explicit `market_code="wind_all_a"` or equivalent; do not overload index code semantics.
- Return `PePbHistory` with `index_code="wind_all_a"` and display name `万得全 A / 全 A 市场` only if source identity is exact.
- Preserve strict date parsing and positive Decimal validation.
- Use source-shaped fixtures for both PE and PB paths.

### Slice 2: Cache

Files likely touched:

- `fund_agent/fund/data/thermometer_cache.py`
- cache tests

Plan:

- Reuse JSON cache if row volume is moderate and no new dependency is needed.
- Consider parquet only if source gate records large data volume and plan review accepts new dependency.
- Cache by market key, e.g. `cache/thermometer/index/wind_all_a_history.json` or a clearly separated market path.

### Slice 3: Calculator Reuse

Files likely touched:

- likely none in `fund_agent/fund/analysis/thermometer_calculator.py`
- calculator tests only if source semantics require additional guard

Plan:

- Reuse existing PE/PB percentile calculator.
- Do not add PE-only calculation.
- Keep `MIN_HISTORY_POINTS` and non-positive fail-closed behavior.

### Slice 4: Service And CLI

Files likely touched:

- `fund_agent/services/thermometer_service.py`
- `fund_agent/ui/cli.py`
- Service and CLI tests

Plan:

- Make no-index `fund-analysis thermometer` default to all-A only after source and plan review accept that behavioral change.
- Preserve transitional public-page adapter either behind an explicit option or separate legacy mode if controller requires backward compatibility in CLI docs.
- Keep `--index` behavior for supported index thermometers.
- Do not change `fund-analysis analyze` automatic mapping in P19-S5 unless a later design gate explicitly does so.

### Slice 5: README And Artifact Sync

Files likely touched:

- `README.md`
- `fund_agent/fund/README.md`
- `tests/README.md`
- implementation artifact in `docs/reviews/`

Plan:

- Document current all-A source, field semantics, cache, CLI behavior, and unavailable states.
- Record non-official disclaimer.
- Record source validation and residual risks.

### Slice 6: Review Gates

Required review sequence:

- implementation plan review;
- implementation worker;
- code review by two independent reviewers;
- fix/re-review if findings;
- controller acceptance and control-doc update.

## Control Update Strategy If Source Gate Fails

If outcome is `BLOCKED_DEFERRED`:

- update `docs/implementation-control.md` Startup Packet to mark P19-S5 blocked/deferred;
- add `docs/reviews/p19-s5-all-a-pe-source-feasibility-20260523.md` as latest artifact;
- preserve P19-S1/S2/S3 as accepted current capability;
- record residual owner: future all-A PE source acquisition or design-change gate;
- do not alter runtime behavior.

If outcome is `NEEDS_DESIGN_CHANGE`:

- do not implement;
- open a design patch gate for `docs/design.md` §11;
- explicitly decide whether PE-only, board-level, or derived rebuild is a different feature name and user-facing disclaimer;
- require storage/cost/license review before any derived rebuild.

## Non-Goals

- Do not use Youzhiyouxing public-page scraping as production truth.
- Do not output all-A PB-only thermometer.
- Do not output all-A PE-only thermometer as the current thermometer.
- Do not rebuild all-A PE by iterating individual stocks unless a separate design/storage/cost/license gate accepts it.
- Do not change P19-S3 `ValuationStateResolution` automatic mapping.
- Do not introduce Dayu Host/Engine/tool loop or external Dayu API.
- Do not pass explicit parameters through `extra_payload`.
- Do not introduce paid sources without explicit authorization.
- Do not change R=A+B-C, fund-type classification, annual-report extraction, or existing audit rules.

## Validation Commands For Source Gate Worker

The source gate worker should run:

```text
.venv/bin/python - <<'PY'
import akshare as ak
print(ak.__version__)
# mandatory probes include:
# ak.stock_a_ttm_lyr()
# ak.stock_a_all_pb()
# discovered PE/PB candidates
PY

rg -n "all.*pe|pe.*all|市盈率|市净率|估值|valuation|index.*value|market.*pe|market.*pb" \
  .venv/lib/python3.11/site-packages/akshare

git diff --check
```

The source feasibility artifact must include the command outputs or concise summaries sufficient for review.

## Current Known Evidence To Carry Forward

From prior P19 artifacts:

- `stock_a_all_pb()` was verified locally as all-A PB history: 5184 rows, 2005-01-04 to 2026-05-22.
- Reviewer probe evidence found `stock_a_ttm_lyr()` in akshare `1.18.60` as an all-A PE candidate. Known evidence to revalidate and freeze:
  - module: `.venv/lib/python3.11/site-packages/akshare/stock_feature/stock_ttm_lyr.py`;
  - page URL: `https://www.legulegu.com/stockdata/a-ttm-lyr`;
  - API URL: `https://legulegu.com/api/stock-data/market-ttm-lyr`;
  - rows: about 5186;
  - date range: 2005-01-05 to 2026-05-22;
  - PE fields: `middlePETTM`, `averagePETTM`, `middlePELYR`, `averagePELYR`;
  - common dates with `stock_a_all_pb()`: about 4828.
- Source feasibility worker must re-run this `stock_a_ttm_lyr()` evidence locally, record exact values, freeze source-shaped fixture requirements, and decide whether `middlePETTM`, `middlePELYR`, `averagePETTM`, or `averagePELYR` matches the current design. The reviewer probe evidence is not by itself an implementation acceptance.
- `stock_a_lg_indicator()` is missing in akshare `1.18.60`.
- `index_value_hist_funddb()` is missing in akshare `1.18.60`.
- Direct Legulegu all-A PE-like endpoints were previously inconclusive or negative:
  - `/api/stock-data/market-index-pe?marketId=ALL`: 404
  - `/api/stock-data/market-index-ttm-pe?marketId=ALL`: 404
  - `/api/stock-data/market-index-lyr-pe?marketId=ALL`: SSL EOF in probe
  - `/api/stock-data/market-pe?marketId=ALL`: 200 with empty body
- `stock_zh_a_spot_em()` previously failed locally with `ProxyError`; even if available, it is current spot data and cannot alone provide history.
- P19-S4 feasibility showed that official 中证 indicator files can prove exact index identity and PE-only recent rows for some indexes, but no PB; this is a warning against accepting incomplete official valuation tables.

## Plan Review Checklist

Reviewers must answer:

- Does the probe matrix cover every design-allowed source family?
- Does any accepted candidate prove exact all-A identity?
- Are PE and PB semantics clear and compatible?
- Are common-date counts sufficient?
- Are source access and license/use constraints acceptable?
- Does the plan reject PB-only/current-only/board-level substitutes?
- Does the plan preserve Service/Capability/UI boundaries?
- Does the plan avoid any `analyze` mapping change?
- Are blocked/deferred outcomes explicit enough to update control docs without runtime changes?

## Validation

```text
git diff --check
passed
```
