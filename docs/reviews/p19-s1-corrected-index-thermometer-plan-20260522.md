# P19-S1 Corrected Index Thermometer MVP Plan（2026-05-22）

## Verdict

`PLAN_DRAFTED_CONTROLLER_FALLBACK`

The delegated planning agent timed out and was shut down. This artifact records the controller fallback plan so the gate can keep moving, but it is not an independent specialist review result.

## Goal

Implement the smallest self-owned thermometer slice that is honest, testable, and aligned with `docs/design.md` v2.2:

- Support `fund-analysis thermometer --index 000300` for 沪深300.
- Compute a PE/PB percentile-based thermometer reading from project-owned code, not from Youzhiyouxing page scraping.
- Keep `fund-analysis analyze` unchanged.
- Build reusable P19 foundations: types, data-source Protocol, calculator, cache, Service routing, CLI output, fixtures, and unavailable semantics.

## Non-Goals

- Do not implement all-A / Wind all-A market thermometer in P19-S1.
- Do not output PB-only all-A data as a thermometer.
- Do not add automatic `valuation_state` mapping to `fund-analysis analyze`.
- Do not remove the existing public-page `FundThermometerAdapter`; it remains transitional/comparison-only code.
- Do not add parquet dependency in P19-S1 unless a later plan review explicitly accepts it.

## Design Boundary Checklist

| Layer | P19-S1 decision |
|---|---|
| UI | `fund_agent/ui/cli.py` adds explicit `--index 000300` and `--json` behavior; it must only call `ThermometerService`. |
| Service | `ThermometerService` becomes the orchestration entry point for both legacy public-page snapshots and new self-owned index readings. It validates explicit request fields and chooses the new path only when `index_code` is provided. |
| Capability analysis | `fund_agent/fund/analysis/thermometer_calculator.py` owns percentile and temperature calculation. It is pure and has no IO. |
| Capability data | `fund_agent/fund/data/thermometer_source.py` owns akshare access through a Protocol-backed source. |
| Capability cache | `fund_agent/fund/data/thermometer_cache.py` owns index history cache and serialization. It does not calculate temperature. |
| Transitional adapter | `fund_agent/fund/data/thermometer.py` remains public-page query/cache only. P19-S1 must not route production index readings through it. |

## Implementation Slices

### Slice 1: Types and Pure Calculator

Files:

- `fund_agent/fund/data/thermometer_types.py`
- `fund_agent/fund/analysis/thermometer_calculator.py`
- `tests/fund/analysis/test_thermometer_calculator.py`

Work:

- Add `PePbPoint`, `PePbHistory`, `ThermometerReading`, and `ThermometerUnavailable`.
- Store values as `Decimal` or `float` consistently; prefer `Decimal` for output payload and JSON serialization compatibility with existing thermometer code.
- Implement percentile rank using deterministic fixture data.
- Compute:
  - `pe_percentile = percentile_rank(current_pe, historical_pe_values)`
  - `pb_percentile = percentile_rank(current_pb, historical_pb_values)`
  - `temperature = (pe_percentile + pb_percentile) / 2`
  - `valuation_state_candidate = low/fair/high` with thresholds `<=30`, `>30 and <70`, `>=70`.

Data contract:

- Use PE column `滚动市盈率中位数` from `stock_index_pe_lg("沪深300")`.
- Use PB column `市净率中位数` from `stock_index_pb_lg("沪深300")`.
- Reason: design says thermometer is based on equal-weight median PE/PB. These columns are median valuation columns and avoid market-cap-weighted valuation distortion. `等权滚动市盈率` and `等权市净率` may be kept as metadata candidates, but not the P19-S1 primary formula.

### Slice 2: Akshare Source and Fixture Boundary

Files:

- `fund_agent/fund/data/thermometer_source.py`
- `tests/fund/data/test_thermometer_source.py`

Work:

- Define `ThermometerDataSource` Protocol with `load_index_history(index_code: str) -> PePbHistory`.
- Implement `AkshareIndexThermometerSource` for `000300` only in P19-S1.
- Map `000300` to akshare symbol `沪深300`.
- Normalize date, PE, PB rows by joining on date.
- Convert akshare/network/schema failures into a typed unavailable result or exception handled by Service as `unavailable`, not a crash.
- Add tests with fake data-source callables or monkeypatched akshare functions; tests must not touch live network.

### Slice 3: Cache

Files:

- `fund_agent/fund/data/thermometer_cache.py`
- `tests/fund/data/test_thermometer_cache.py`

Work:

- Use JSON cache for P19-S1 to avoid adding `pyarrow` or `fastparquet`.
- Suggested path: `cache/thermometer/index/000300_history.json` under explicit `--cache-dir` when supplied.
- Store schema version, index code, index name, source, fetched_at, and normalized PE/PB rows.
- Reuse fresh cache unless `--force-refresh` is passed.
- On live source failure:
  - return fresh/stale cached data when usable;
  - otherwise return `unavailable` with reason.

### Slice 4: Service Routing

Files:

- `fund_agent/services/thermometer_service.py`
- `tests/services/test_thermometer_service.py`

Work:

- Extend `ThermometerRequest` with explicit `index_code: str | None = None`.
- Keep current no-index behavior as legacy public-page snapshot for compatibility.
- When `index_code == "000300"`, route to the new P19-S1 index thermometer path.
- Reject unsupported index codes with `unavailable` data state or a clear validation error; for P19-S1 prefer `unavailable` for data absence and `ValueError` for malformed input.
- Do not add `extra_payload`.

### Slice 5: CLI Contract

Files:

- `fund_agent/ui/cli.py`
- `tests/ui/test_cli.py`

Work:

- Add `--index` option to `fund-analysis thermometer`.
- `fund-analysis thermometer --index 000300` prints a plain summary with index code, index name, temperature, PE/PB percentiles, valuation state candidate, source, cached/stale/unavailable, and data date.
- `fund-analysis thermometer --index 000300 --json` prints structured JSON.
- Existing `fund-analysis thermometer` without `--index` continues the current public-page snapshot behavior.
- `--force-refresh` and `--cache-dir` remain explicit and are forwarded to Service.
- Output must include the disclaimer or a stable field equivalent:
  - `本温度计基于有知有行公开方法论独立计算，非有知有行官方数据。`

### Slice 6: README / Test Docs Sync

Files:

- `fund_agent/fund/README.md`
- `tests/README.md`
- Root `README.md` only if CLI user-facing usage changes are documented there.

Work:

- Document current P19-S1 behavior only.
- Keep public-page thermometer wording as transitional/current behavior.
- Do not document all-A market thermometer as implemented.

## Exit Criteria

- `ThermometerDataSource` Protocol exists.
- `ThermometerReading` / `PePbHistory` exist and are covered by tests.
- Calculator tests cover percentile rank, threshold mapping, missing PE/PB, and deterministic fixture history.
- Source tests cover akshare-shaped PE/PB fixtures and schema drift to unavailable/fail-closed behavior.
- Cache tests cover fresh hit, force refresh bypass, stale fallback, and corrupt cache handling.
- Service tests cover no-index legacy path and `index_code="000300"` new path.
- CLI tests cover plain and JSON `--index 000300` output.
- Existing public-page thermometer tests continue to pass.
- No `fund-analysis analyze` default behavior changes.

## Validation Commands

```bash
.venv/bin/python -m pytest tests/fund/analysis/test_thermometer_calculator.py -q
.venv/bin/python -m pytest tests/fund/data/test_thermometer_source.py tests/fund/data/test_thermometer_cache.py -q
.venv/bin/python -m pytest tests/services/test_thermometer_service.py tests/ui/test_cli.py -q
.venv/bin/python -m pytest tests/fund/data/test_thermometer.py -q
.venv/bin/python -m ruff check fund_agent tests
```

## Risks And Residuals

| Risk | Handling |
|---|---|
| akshare / Legulegu live instability | P19-S1 tests use fixtures; runtime uses cache + unavailable semantics. |
| PE/PB column ambiguity | P19-S1 fixes primary columns to median TTM PE and median PB; future review may compare equivalent weighted columns. |
| New cache format churn | Use versioned JSON in P19-S1; parquet remains deferred. |
| All-A PE source blocker | Owned by P19-S5 / all-A PE source gate. |
| Analyzer behavior drift | P19-S1 explicitly forbids `fund-analysis analyze` integration. |

## Next Gate

`P19-S1 implementation handoff`

Implementation should be delegated as specialist work. The implementer should modify source/tests/README according to the slices above and must not alter all-A market thermometer scope.
