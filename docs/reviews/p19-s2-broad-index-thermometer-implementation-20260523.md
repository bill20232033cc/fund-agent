# P19-S2 Broad Index Thermometer Implementation（2026-05-23）

## Scope

Implemented P19-S2 宽基指数温度计批量查询 within the accepted plan and controller constraints:

- Added `000905 -> 中证500` to the self-owned akshare index source using the same PE/PB interface family and the same columns: `滚动市盈率中位数` and `市净率中位数`.
- Added Service-owned request normalization for legacy, single-index, and batch-index modes.
- Added batch Service result type and CLI rendering for `fund-analysis thermometer --index 000300,000905`.
- Preserved no-index public-page `FundThermometerAdapter` behavior.
- Did not integrate thermometer into `fund-analysis analyze`.
- Did not implement all-A, PB-only all-A, parquet, paid source, Dayu runtime, or `extra_payload`.

## Files Changed

- `fund_agent/fund/data/thermometer_source.py`
- `fund_agent/fund/data/thermometer_types.py`
- `fund_agent/fund/data/__init__.py`
- `fund_agent/services/thermometer_service.py`
- `fund_agent/ui/cli.py`
- `tests/fund/data/test_thermometer_source.py`
- `tests/services/test_thermometer_service.py`
- `tests/ui/test_cli.py`
- `README.md`
- `fund_agent/fund/README.md`
- `tests/README.md`

## Behavior

### Source

`AkshareIndexThermometerSource` now supports:

- `000300` -> `沪深300`
- `000905` -> `中证500`

Unsupported but well-formed codes still raise `ThermometerSourceError`, allowing Service batch orchestration to represent those items as `unavailable`.

### Service

`ThermometerRequest` now supports `index_codes: tuple[str, ...] | None`.

`ThermometerService` owns the single normalization boundary:

- rejects `index_code` and `index_codes` when both are set;
- rejects empty values and non-6-digit codes;
- strips CLI padding around individual code segments;
- de-duplicates duplicate codes while preserving first occurrence order;
- keeps legacy no-index mode routed to `FundThermometerAdapter`;
- keeps single-index mode returning `ThermometerReading`;
- returns `ThermometerBatchResult` for batch mode.

Batch item source failures are converted to per-item unavailable readings. A batch with one unsupported code exits as a coherent result instead of a request error.

### CLI

`fund-analysis thermometer --index` now accepts:

- `000300`
- `000905`
- comma-separated batch values such as `000300,000905`

Malformed shape, empty segments, and blank input exit 2. Well-formed unsupported codes such as `999999` are rendered as item-level unavailable in batch JSON/plain output with exit 0.

## Tests Added Or Updated

- Source tests cover both `000300` and `000905` symbol mapping and preserve strict date fail-closed behavior.
- Service tests cover:
  - single index path;
  - batch `("000300", "000905")`;
  - well-formed unsupported `999999` as partial unavailable;
  - all item failures;
  - preserve-order de-duplication;
  - mutually exclusive request fields;
  - empty/malformed batch state.
- CLI tests cover:
  - batch JSON/plain output;
  - partial unavailable JSON exit 0 for `000300,999999`;
  - malformed input exit 2 for `000300,abc`, `000300,`, `,000905`, blank input, and blank batch segment.

## Validation

```text
.venv/bin/python -m pytest tests/fund/data/test_thermometer_source.py tests/fund/analysis/test_thermometer_calculator.py tests/fund/data/test_thermometer_cache.py tests/services/test_thermometer_service.py tests/ui/test_cli.py tests/fund/data/test_thermometer.py -q
79 passed in 0.79s

.venv/bin/python -m ruff check fund_agent tests
All checks passed!

git diff --check
passed
```

## Residual Risks

- Live akshare latency for `中证500` remains material on first refresh; JSON cache mitigates normal use, and default tests remain fixture-based.
- P19-S2 intentionally does not solve all-A market PE source uncertainty. Full all-A market thermometer remains deferred to P19-S5 / all-A PE source gate.
- P19-S2 intentionally does not auto-map thermometer readings into `fund-analysis analyze`; P19-S3 remains the earliest gate for that contract.
