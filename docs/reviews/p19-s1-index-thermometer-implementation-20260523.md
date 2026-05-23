# P19-S1 Index Thermometer Implementation（2026-05-23）

## Verdict

`IMPLEMENTED_PENDING_CODE_REVIEW`

P19-S1 implements the corrected self-owned 沪深300 index thermometer MVP without changing `fund-analysis analyze`.

## Scope Implemented

| Area | Files |
|---|---|
| Types | `fund_agent/fund/data/thermometer_types.py` |
| Pure calculator | `fund_agent/fund/analysis/thermometer_calculator.py` |
| akshare source | `fund_agent/fund/data/thermometer_source.py` |
| JSON cache | `fund_agent/fund/data/thermometer_cache.py` |
| Service routing | `fund_agent/services/thermometer_service.py` |
| CLI | `fund_agent/ui/cli.py` |
| Tests | `tests/fund/analysis/test_thermometer_calculator.py`, `tests/fund/data/test_thermometer_source.py`, `tests/fund/data/test_thermometer_cache.py`, `tests/services/test_thermometer_service.py`, `tests/ui/test_cli.py` |
| Docs | `README.md`, `fund_agent/fund/README.md`, `tests/README.md` |

## Behavior

- `fund-analysis thermometer` keeps the existing Youzhiyouxing public-page snapshot behavior.
- `fund-analysis thermometer --index 000300` uses self-owned index thermometer logic.
- `--json`, `--cache-dir`, and `--force-refresh` remain explicit and are forwarded through Service.
- The self-owned path uses akshare `stock_index_pe_lg("沪深300")` and `stock_index_pb_lg("沪深300")`.
- Primary columns are `滚动市盈率中位数` and `市净率中位数`.
- The cache is versioned JSON at `cache/thermometer/index/000300_history.json`.
- Source failures use fresh/stale cache when available; otherwise they return a `ThermometerReading` with `unavailable=True`.
- No `fund-analysis analyze` automatic `valuation_state` mapping was added.
- No all-A / Wind all-A market thermometer was implemented.

## Validation

```text
.venv/bin/python -m pytest tests/fund/analysis/test_thermometer_calculator.py tests/fund/data/test_thermometer_source.py tests/fund/data/test_thermometer_cache.py tests/services/test_thermometer_service.py tests/ui/test_cli.py tests/fund/data/test_thermometer.py -q
49 passed

.venv/bin/python -m pytest tests/config/test_paths.py tests/test_repo_hygiene.py tests/services/test_fund_analysis_service.py tests/fund/analysis/test_checklist.py tests/fund/analysis/test_final_judgment.py -q
34 passed

.venv/bin/python -m ruff check fund_agent tests
All checks passed

git diff --check
passed
```

## Residuals

| Residual | Owner |
|---|---|
| Independent code review still required | P19-S1 code review gate |
| Live akshare / Legulegu instability | P19-S1 code review and later smoke gate |
| 中证500 support | P19-S2 |
| all-A PE source blocker | P19-S5 / all-A PE source gate |
| Automatic analyze integration | P19-S3 |
