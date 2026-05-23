# P19-S2 Code Re-review GLM 2026-05-23

## Verdict

PASS.

当前 HEAD `0a0045c674421a1aa6f8dbfb1cbef6cee7908918` 已修复上一轮 blocker：well-formed 但 unsupported 的指数代码会在缓存读取前被支持性真源拒绝为 item-level unavailable，不会因 fresh/stale cache、batch、single 或 CLI JSON 路径变成 available reading。

工作区存在未跟踪文档 `docs/design0522.md`、`docs/implementation-control0522.md`、`docs/repo-audit-20260521.md`，本次只审查当前 HEAD 和 P19-S2 相关路径，未把这些未跟踪文件纳入结论。

## Scope

- Commit: `0a0045c fix: enforce thermometer supported index before cache`
- Primary files reviewed:
  - `fund_agent/fund/data/thermometer_source.py`
  - `fund_agent/services/thermometer_service.py`
  - `fund_agent/fund/data/thermometer_cache.py`
  - `fund_agent/fund/data/thermometer_types.py`
  - `fund_agent/ui/cli.py`
  - `tests/services/test_thermometer_service.py`
  - `tests/ui/test_cli.py`
  - `tests/fund/data/test_thermometer_source.py`

## Findings

No blocking or non-blocking correctness findings.

### 1. Unsupported well-formed index cannot become available through cache

Direct path evidence:

- `fund_agent/fund/data/thermometer_source.py:19-41` keeps the support set and support predicate in Fund Capability/data: `SUPPORTED_INDEX_SYMBOLS` contains only `000300` and `000905`; `is_supported_index_code()` checks membership there.
- `fund_agent/services/thermometer_service.py:216-221` calls `is_supported_index_code(index_code)` before constructing `ThermometerHistoryCache` or reading cache.
- Fresh cache path starts only after that guard at `fund_agent/services/thermometer_service.py:223-231`.
- Stale fallback path is also after the same guard at `fund_agent/services/thermometer_service.py:233-247`.
- Batch path delegates every item through `_load_index_reading()` at `fund_agent/services/thermometer_service.py:187-188`, so the same pre-cache guard covers batch items.
- Single path also delegates through `_load_index_reading()` at `fund_agent/services/thermometer_service.py:166-167`, so the same guard covers single index requests.
- CLI `--index` calls `ThermometerService().run(...)` with explicit `index_code` / `index_codes` at `fund_agent/ui/cli.py:275-285`; it does not compute availability from UI-side allowlists.

Regression tests:

- `tests/services/test_thermometer_service.py:303-342` seeds a fake fresh cache for `999999` and verifies batch `("000300", "999999")` still returns `999999` as unavailable, `cached=False`, and does not call the source for `999999`.
- `tests/ui/test_cli.py:1151-1195` seeds real cache files for `000300` and `999999`, then verifies CLI `thermometer --index 000300,999999 --json --cache-dir <tmp>` exits 0 and reports only `999999` as unavailable.

### 2. Support truth remains in Capability/data, not UI allowlist

The only production support mapping found in reviewed paths is `SUPPORTED_INDEX_SYMBOLS` in `fund_agent/fund/data/thermometer_source.py:19`. UI text mentions supported examples in help copy at `fund_agent/ui/cli.py:249`, but parsing at `fund_agent/ui/cli.py:928-945` only splits the option and leaves shape/semantic handling to Service/Capability. There is no UI-side support allowlist or direct import of `SUPPORTED_INDEX_SYMBOLS`.

### 3. P19-S2 exit semantics match plan

- Malformed shape is rejected by Service normalization via `_normalize_index_codes()` at `fund_agent/services/thermometer_service.py:297-327`.
- CLI maps `ValueError` to exit 2 at `fund_agent/ui/cli.py:287-289`.
- CLI maps unexpected exceptions to exit 1 at `fund_agent/ui/cli.py:290-292`.
- Well-formed unsupported codes return `ThermometerUnavailable(...).to_reading()` at `fund_agent/services/thermometer_service.py:216-221`, so they are data-state unavailable and do not raise `ValueError`.
- Batch aggregation computes `unavailable`, `partial_unavailable`, and `unavailable_count` from per-item readings at `fund_agent/services/thermometer_service.py:190-197`; partial unsupported therefore exits 0 through the normal CLI output path.

Test evidence:

- `tests/ui/test_cli.py:1198-1228` covers malformed `000300,abc`, `000300,`, `,000905`, blank, and `000300,   ` as exit 2.
- `tests/ui/test_cli.py:1121-1148` covers well-formed unsupported batch JSON as exit 0 with `partial_unavailable=True`.

### 4. No observed scope creep into analyze, all-A, or no-index public-page adapter

- `git diff HEAD^ HEAD -- fund_agent/services/fund_analysis_service.py fund_agent/ui/cli.py fund_agent/fund/data/thermometer.py README.md fund_agent/fund/README.md` produced no diff for these out-of-scope production/public-page paths in the fix commit.
- `fund_agent/services/fund_analysis_service.py` still consumes explicit `request.valuation_state` at line 397; no `ThermometerService` call is wired into `analyze`.
- `fund_agent/ui/cli.py:93-205` still exposes explicit `--valuation-state` for `analyze`; thermometer output only serializes `valuation_state_candidate` for the thermometer command.
- No all-A / PB-only all-A implementation, parquet dependency, Dayu runtime, or `extra_payload` usage was introduced in the reviewed P19-S2 fix path.
- No-index `ThermometerService.run()` still falls through to `FundThermometerAdapter.load_thermometer()` at `fund_agent/services/thermometer_service.py:168-169`, preserving the transitional public-page adapter path.

## Verification Commands

```bash
git status --short
git rev-parse HEAD
git show --stat --oneline --decorate HEAD
git show --name-only --format=fuller 0a0045c
git show --unified=80 0a0045c -- fund_agent/fund/data/thermometer_source.py fund_agent/services/thermometer_service.py tests/services/test_thermometer_service.py tests/ui/test_cli.py
rg -n "SUPPORTED_INDEX_SYMBOLS|is_supported_index_code|000300|000905|999999|399006" fund_agent/ui fund_agent/services fund_agent/fund tests/ui tests/services
rg -n "ThermometerService|ThermometerRequest|thermometer|valuation_state|valuation_state_candidate" fund_agent/services/fund_analysis_service.py fund_agent/ui/cli.py fund_agent/fund/analysis/checklist.py
rg -n "all-A|all A|全 A|全A|PB-only|pb-only|stock_a_all|FundThermometerAdapter|youzhiyouxing|extra_payload|dayu|Dayu|parquet|pyarrow|fastparquet" fund_agent pyproject.toml README.md fund_agent/README.md fund_agent/fund/README.md tests
git diff HEAD^ HEAD -- fund_agent/services/fund_analysis_service.py fund_agent/ui/cli.py fund_agent/fund/data/thermometer.py README.md fund_agent/fund/README.md
.venv/bin/python -m pytest tests/fund/data/test_thermometer_source.py tests/fund/analysis/test_thermometer_calculator.py tests/fund/data/test_thermometer_cache.py tests/services/test_thermometer_service.py tests/ui/test_cli.py tests/fund/data/test_thermometer.py -q
.venv/bin/python -m ruff check fund_agent/fund/data/thermometer_source.py fund_agent/fund/data/thermometer_cache.py fund_agent/fund/data/thermometer_types.py fund_agent/fund/analysis/thermometer_calculator.py fund_agent/services/thermometer_service.py fund_agent/ui/cli.py tests/fund/data/test_thermometer_source.py tests/fund/analysis/test_thermometer_calculator.py tests/fund/data/test_thermometer_cache.py tests/services/test_thermometer_service.py tests/ui/test_cli.py tests/fund/data/test_thermometer.py
```

Results:

- Target pytest suite: `81 passed in 0.65s`
- Ruff: `All checks passed!`

## Residual Risks

- There is no dedicated test that seeds a stale unsupported cache and requests unsupported single `index_code="999999"`. Static path inspection shows the pre-cache support guard covers both stale and single paths because it executes before any cache construction or source call, so this is a low residual test granularity gap rather than an observed behavioral defect.
- Live `000300` / `000905` refresh still depends on akshare and its upstream response shape. Existing source tests use fakes and validate schema fail-closed behavior; they do not prove live akshare availability on every machine.
