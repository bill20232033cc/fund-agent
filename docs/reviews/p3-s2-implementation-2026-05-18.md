# P3-S2 Implementation

## Gate

- Gate: `P3-S2 implementation + review`
- Date: 2026-05-18
- Worker: AgentCodex
- Scope: Capability data-layer thermometer adapter

## Source Observations

Controller verified the current public pages:

- `https://youzhiyouxing.cn/data`: contains update time, all-market temperature, and an index temperature table.
- `https://youzhiyouxing.cn/data/macro`: contains bond temperature and 10-year treasury yield.

P3-S2 uses those current URLs instead of the older illustrative URL shown in `docs/design.md` pseudocode.

## Changed Files

- `fund_agent/fund/data/thermometer.py`
- `fund_agent/fund/data/__init__.py`
- `tests/fund/data/test_thermometer.py`
- `fund_agent/fund/README.md`
- `tests/README.md`
- `README.md`
- `docs/implementation-control.md`
- `docs/reviews/p3-s2-implementation-2026-05-18.md`

## Implementation Summary

- Added `FundThermometerAdapter` in the Capability data layer.
- Added explicit dataclasses:
  - `ThermometerSnapshot`
  - `MarketTemperature`
  - `IndexTemperature`
  - `MacroTemperature`
- Added injectable async/sync fetcher support for tests and default httpx fetcher for production.
- Added default pages:
  - `https://youzhiyouxing.cn/data`
  - `https://youzhiyouxing.cn/data/macro`
- Added JSON cache at `cache/thermometer/thermometer.json`.
- Fresh cache TTL is 24 hours.
- Stale cache fallback is allowed up to 7 days when fetch or parse fails.
- No-cache failure returns `unavailable=True` snapshot instead of raising fetch/parse errors.
- Parsing uses normalized HTML text and table cell extraction with regex helpers, without fixed line-number assumptions.
- Adapter is exported from `fund_agent.fund.data`.
- No CLI or Service integration was added in P3-S2.

## Controller Correction

Controller ran a live-response parser smoke test against downloaded public HTML from:

- `https://youzhiyouxing.cn/data`
- `https://youzhiyouxing.cn/data/macro`

The first pass parsed index rows and bond temperature, but missed the current all-market layout because the page presents the value as `全市场温度 ... 70°` rather than `全市场温度：70`.

Accepted correction:

- Added heading-proximity parsing for degree-style all-market temperature values.
- Added fallback trend extraction for `温度不变` / `温度上升` / `温度下降` text after the degree value.
- Added index-table header selection so preceding explanatory tables are not treated as index rows.
- Added support for current index rows where the code appears inside the index-name cell.
- Added support for the current macro label `10年期国债到期收益率`.
- Cache write failures no longer turn an otherwise successful fetch/parse result into `unavailable`; cache remains a best-effort acceleration/fallback layer.
- All-market parsing now prefers degree-marked values and supports both `°` and `℃`, reducing false positives when nearby non-temperature numbers appear.
- Added targeted unit tests for the current no-colon all-market layout, current index table layout, preceding non-index tables, current treasury maturity-yield label, cache-write failure behavior, and degree-value priority.

## Validation

```bash
.venv/bin/python -m pytest tests/fund/data tests/fund/analysis -q
```

Original worker result: `49 passed in 0.50s`

```bash
.venv/bin/python -m pytest tests/fund/data/test_thermometer.py -q
```

Controller correction result: `8 passed in 0.05s`

After index-table and macro-label correction:

```bash
.venv/bin/python -m pytest tests/fund/data/test_thermometer.py -q
```

Result: `11 passed in 0.05s`

After cache-write failure correction:

```bash
.venv/bin/python -m pytest tests/fund/data/test_thermometer.py -q
```

Result: `12 passed in 0.05s`

After review finding correction for degree-value priority:

```bash
.venv/bin/python -m pytest tests/fund/data/test_thermometer.py -q
```

Result: `13 passed in 0.07s`

```bash
.venv/bin/python -m pytest tests/fund/data tests/fund/analysis tests/services tests/ui -q
```

Controller regression result after review finding correction: `60 passed in 0.97s`

```bash
.venv/bin/python -c "from pathlib import Path; from fund_agent.fund.data.thermometer import parse_thermometer_pages; s=parse_thermometer_pages(Path('/tmp/yzyx_data.html').read_text(), Path('/tmp/yzyx_macro.html').read_text()); print(s.market, len(s.indexes), s.macro)"
```

Controller live-response smoke result: parsed all-market `70`, 11 index rows, HS300 temperature `59`, HS300 intrinsic return `5.11`, HS300 dividend yield `2.42`, bond temperature `77`, and 10-year treasury maturity yield `1.77`.

```bash
git diff --check
```

Result: passed with no output.

## Residual Risks

- Public page structure can still change; parser is intentionally defensive but not a formal DOM contract.
- Tests use fake HTML snippets modeled on current public pages and do not hit the live network.
- The adapter currently parses all-market, index rows, bond temperature, and 10-year treasury yield; it does not yet map thermometer values into checklist `valuation_state`.
- Service and CLI integration are intentionally deferred to later P3 slices.

## Stop Status

- Implementation complete.
- Required validation passed.
- Ready for P3-S2 code review.
