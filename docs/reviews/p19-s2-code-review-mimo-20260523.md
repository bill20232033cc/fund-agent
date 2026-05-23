# P19-S2 Code Review - MiMo

## Verdict

PASS

当前 HEAD `8ddad68` 的 P19-S2 宽基指数温度计批量查询实现可以接受。未发现阻塞性或非阻塞性 finding。

## Scope

- Reviewed commit: `8ddad68 feat: add p19 s2 broad index thermometer`
- Reviewed paths:
  - `fund_agent/fund/data/thermometer_source.py`
  - `fund_agent/fund/data/thermometer_types.py`
  - `fund_agent/fund/data/thermometer_cache.py`
  - `fund_agent/fund/analysis/thermometer_calculator.py`
  - `fund_agent/services/thermometer_service.py`
  - `fund_agent/ui/cli.py`
  - `tests/fund/data/test_thermometer_source.py`
  - `tests/services/test_thermometer_service.py`
  - `tests/ui/test_cli.py`
  - `README.md`
  - `fund_agent/fund/README.md`
  - `tests/README.md`

## Findings

No findings.

## Evidence Notes

### 1. Source Mapping And Fail-Closed Schema

PASS.

- `000905 -> 中证500` mapping is present in both `SUPPORTED_INDEX_SYMBOLS` and `INDEX_NAMES` at `fund_agent/fund/data/thermometer_source.py:19-20`.
- The akshare calls still use `stock_index_pe_lg(symbol=symbol)` and `stock_index_pb_lg(symbol=symbol)` through `_load_pe_frame()` / `_load_pb_frame()` at `fund_agent/fund/data/thermometer_source.py:119-142`.
- PE/PB schema remains strict: required columns are `日期`, `滚动市盈率中位数`, and `市净率中位数`; missing columns raise `ThermometerSourceError` at `fund_agent/fund/data/thermometer_source.py:191-194`.
- Date schema remains fail-closed for strings: `_normalize_date()` accepts only a full `YYYY-MM-DD` match, validates calendar correctness via `datetime.strptime`, and does not truncate or trim at `fund_agent/fund/data/thermometer_source.py:219-228`.
- Tests cover both `000300` and `000905`, unsupported code, missing field schema drift, non-strict date strings, whitespace date strings, and `date` objects at `tests/fund/data/test_thermometer_source.py:88-246`.

### 2. Batch Result Contract

PASS.

- `ThermometerBatchResult` is a frozen slotted dataclass with stable fields for requested codes, readings, generated timestamp, aggregate unavailable flags, count, source, and disclaimer at `fund_agent/fund/data/thermometer_types.py:93-115`.
- CLI serialization converts Decimal values to strings and unavailable numeric fields to `null` through `_thermometer_reading_payload()` at `fund_agent/ui/cli.py:861-895`.
- Batch JSON includes `requested_index_codes`, `result_count`, aggregate unavailable flags, `generated_at`, disclaimer, and per-reading payloads at `fund_agent/ui/cli.py:835-858`.

### 3. Service Normalization Boundary

PASS.

- `ThermometerService.run()` calls one normalization helper before routing at `fund_agent/services/thermometer_service.py:162-168`.
- Mutual exclusion between `index_code` and `index_codes` is enforced at `fund_agent/services/thermometer_service.py:286-287`.
- Empty batch, empty item, non-six-digit input, and preserve-order de-duplication are centralized in `_normalize_index_codes()` at `fund_agent/services/thermometer_service.py:297-327`.
- State routing is explicit:
  - `index_codes` -> batch path
  - `index_code` -> single self-owned index path
  - neither -> existing public-page adapter path
  Evidence: `fund_agent/services/thermometer_service.py:162-168`.
- Tests cover mutual exclusion, malformed batch values, preserve-order de-duplication, single-index routing, and batch ordering at `tests/services/test_thermometer_service.py:195-424`.

### 4. Failure Semantics And Exit Codes

PASS.

- Source/unsupported failures that raise `ThermometerSourceError` become item-level unavailable readings when no usable cache exists at `fund_agent/services/thermometer_service.py:225-239`.
- Batch aggregation derives `unavailable`, `partial_unavailable`, and `unavailable_count` from per-item readings at `fund_agent/services/thermometer_service.py:186-197`.
- CLI maps `ValueError` request problems to exit 2 and unexpected exceptions to exit 1 at `fund_agent/ui/cli.py:275-292`.
- Tests cover partial unavailable batch exit 0 and malformed index exit 2 at `tests/ui/test_cli.py:1090-1150`.
- A direct CLI unsupported-only probe also returned exit 0 with all-item unavailable:
  - `.venv/bin/python -m fund_agent.ui.cli thermometer --index 999999,888888 --json --cache-dir /tmp/fund-agent-p19-s2-review-cache`

### 5. UI Boundary

PASS.

- UI parses `--index` into explicit `ThermometerRequest.index_code` or `index_codes` fields and delegates execution to `ThermometerService` at `fund_agent/ui/cli.py:275-285`.
- UI does not import or call `AkshareIndexThermometerSource`, `ThermometerHistoryCache`, `SUPPORTED_INDEX_SYMBOLS`, or calculator functions.
- `_parse_index_option()` only splits comma-separated CLI input and leaves validation to Service at `fund_agent/ui/cli.py:928-945`.
- No `fund-analysis analyze` path was wired to thermometer readings; `analyze()` still consumes explicit `--valuation-state` at `fund_agent/ui/cli.py:93-96` and `fund_agent/ui/cli.py:197-205`.

### 6. Regression Surfaces

PASS.

- No-index `fund-analysis thermometer` still constructs `FundThermometerAdapter` and calls `load_thermometer()` when neither index field is present at `fund_agent/services/thermometer_service.py:167-168`.
- `force_refresh=True` still skips fresh-cache reads but can fall back to stale cache on source failure through `cache.load(index_code, allow_stale=True)` at `fund_agent/services/thermometer_service.py:216-239`.
- Batch cache behavior is per index code because `_load_index_batch()` delegates each normalized code through `_load_index_reading()` at `fund_agent/services/thermometer_service.py:186-188`, and cache paths are index-scoped at `fund_agent/fund/data/thermometer_cache.py:113-126`.
- All-failed unavailable flags are covered by `test_thermometer_service_batch_marks_all_failed_items_unavailable` at `tests/services/test_thermometer_service.py:303-330`.
- Single-index output shape is preserved by the `ThermometerReading` serialization path at `fund_agent/ui/cli.py:804-805` and covered by CLI tests at `tests/ui/test_cli.py:967-1027`.

### 7. Tests And README

PASS.

- README describes current behavior only: public-page no-index query remains transitional, self-owned `--index` supports `000300` and `000905`, malformed index exits 2, unexpected failure exits 1, and `analyze --valuation-state` is still explicit. Evidence: `README.md:157-176`.
- Fund README describes current P19-S1/S2 modules, JSON cache, no public-page fallback for self-owned data, no analyze integration, and all-A deferral. Evidence: `fund_agent/fund/README.md:300-315`.
- Tests README was updated to mention 中证500, batch normalization, partial unavailable, and malformed index exit 2. Evidence: `tests/README.md:25-45`.
- No Dayu runtime, parquet dependency, PB-only all-A output, all-A thermometer, or `extra_payload` was introduced in the reviewed implementation paths.

## Residual Risks

- Live supported-index queries still depend on akshare and its transitive native/runtime dependencies. Unit tests intentionally use fakes and do not prove live service availability for `000300` or `000905` on every local machine.
- During review, one mixed live probe with a supported code (`000300,999999`) aborted in a native `libmini_racer` fatal path while other validations were running. This is not a static P19-S2 logic defect, but it confirms the accepted residual risk that live akshare availability can fail outside Python exception handling.
- `generated_at` is intentionally dynamic. Existing tests assert shape and behavior around batch outputs but do not freeze the timestamp value.

## Validation Notes

Passed:

```bash
.venv/bin/python -m pytest tests/fund/data/test_thermometer_source.py tests/fund/data/test_thermometer_cache.py tests/fund/analysis/test_thermometer_calculator.py tests/services/test_thermometer_service.py tests/ui/test_cli.py -q
```

Result:

```text
66 passed in 0.55s
```

Passed:

```bash
.venv/bin/python -m ruff check fund_agent tests
```

Result:

```text
All checks passed!
```

Additional direct CLI probe:

```bash
.venv/bin/python -m fund_agent.ui.cli thermometer --index 999999,888888 --json --cache-dir /tmp/fund-agent-p19-s2-review-cache
```

Result: exit `0`; payload contained `unavailable=true`, `partial_unavailable=false`, `unavailable_count=2`, and both items had `unavailable=true`.
