# P19-S2 Broad Index Thermometer Plan（2026-05-23）

## Goal

P19-S2 在 P19-S1 已 accepted 的自建沪深300指数温度计基础上，扩展到宽基指数批量查询：

- 支持中证500 `000905` 的 PE/PB 历史获取与温度计算。
- 保持沪深300 `000300` 单指数路径可用。
- 支持 CLI `fund-analysis thermometer --index 000300,000905` 批量查询。
- JSON/plain 输出都给出逐指数结果；单个指数数据不可用时返回该项 `unavailable`，不影响其它指数输出。
- 不接入 `fund-analysis analyze`，不实现全 A 市场温度计，不做 PB-only 全 A。

## Design Boundary Check

| Boundary | P19-S2 decision |
|---|---|
| UI | 只解析 CLI 参数、选择 plain/JSON 渲染、转发显式请求到 `ThermometerService`；不得直接调用 akshare、`ThermometerCalculator` 或 cache。 |
| Service | `ThermometerService` 继续作为自建温度计用例入口；新增批量请求/结果聚合语义，负责逐项 unavailable、整体 exit-code 所需状态和缓存/source/calculator 编排。 |
| Capability data | `AkshareIndexThermometerSource` 增加 `000905 -> 中证500` 映射，继续只负责把 akshare PE/PB 表规整为 `PePbHistory`。 |
| Capability analysis | `ThermometerCalculator` 继续保持纯计算；P19-S2 不改变 PE/PB 分位数公式和 30 个共同日期下限。 |
| Capability cache | `ThermometerHistoryCache` 继续按指数代码隔离 JSON cache：`cache/thermometer/index/<index_code>_history.json`。 |
| Transitional adapter | `FundThermometerAdapter` 仍只服务无 `--index` 的公开页过渡查询；P19-S2 生产指数读数不得依赖它。 |
| Analyze integration | P19-S2 不改 `FundAnalysisService`、`fund-analysis analyze`、检查清单 `valuation_state` 或报告判断。P19-S3 才允许设计自动映射。 |
| All-A scope | P19-S2 不实现 `wind_all_a` / 全 A PE+PB，不输出 PB-only 全 A，不把有知有行页面当生产真源。 |

First-principles judgment: 批量语义不是 UI 展示细节，而是一个温度计查询 use case。UI 层拆分多次单指数调用会把逐项失败、请求去重、顺序保持和整体状态散落到展示层，违反 UI/Service 分层。因此 P19-S2 应在 Service 层增加批量契约，UI 只负责把 `--index 000300,000905` 解析为显式指数代码序列并渲染 Service 返回值。

## Data Source Feasibility

本地 `.venv` live probe 已执行，未写入仓库数据：

```text
.venv/bin/python -c '<akshare 中证500 PE/PB probe>'
akshare 1.18.60
stock_index_pe_lg("中证500"): shape=(4701, 8), elapsed=15.3s
PE columns: 日期, 指数, 等权静态市盈率, 静态市盈率, 静态市盈率中位数, 等权滚动市盈率, 滚动市盈率, 滚动市盈率中位数
PE latest: 2026-05-22, 滚动市盈率中位数=31.02
stock_index_pb_lg("中证500"): shape=(4701, 5), elapsed=22.2s
PB columns: 日期, 指数, 市净率, 等权市净率, 市净率中位数
PB latest: 2026-05-22, 市净率中位数=2.64
common PE/PB dates: 4701
```

Feasibility judgment:

- `000905` 可按 P19-S1 同一接口族接入：`stock_index_pe_lg(symbol="中证500")` + `stock_index_pb_lg(symbol="中证500")`。
- 目标列与 P19-S1 一致：PE 使用 `滚动市盈率中位数`，PB 使用 `市净率中位数`。
- 历史共同日期 4701，满足当前 `MIN_HISTORY_POINTS=30`。
- 首次强制刷新可能较慢，本次探针 PE+PB 合计约 37.5s；P19-S2 不应把 live probe 放入默认单元测试，应继续使用 fixture 测试并依赖 JSON cache 降低日常延迟。
- akshare 网络/接口抖动仍是 residual risk；运行时必须保持 source failure -> item unavailable 或 stale cache 语义，禁止 fallback 到有知有行页面抓取。

## Proposed Contract

### Request Contract

Prefer adding an explicit batch field instead of overloading `index_code`:

- Keep `ThermometerRequest.index_code: str | None` for existing single-index and no-index behavior.
- Add `ThermometerRequest.index_codes: tuple[str, ...] | None = None` for batch.
- Validation must require exactly one of these modes:
  - no `index_code` and no `index_codes`: legacy public-page snapshot;
  - `index_code` set: single self-owned index reading;
  - `index_codes` set: batch self-owned index readings.
- UI parses `--index`:
  - no `--index`: request legacy mode;
  - no comma: `index_code="000300"`;
  - comma-separated: `index_codes=("000300", "000905")`.
- Malformed codes, empty segments, non-6-digit values, or all-empty input are request errors and should exit 2.
- Duplicate codes should be removed while preserving first occurrence order, or rejected with exit 2. Preferred implementation: preserve-order de-duplication because repeated CLI values do not create new information.

### Result Contract

Add `ThermometerBatchResult` in `fund_agent/fund/data/thermometer_types.py`:

- `readings: tuple[ThermometerReading, ...]`
- `requested_index_codes: tuple[str, ...]`
- `generated_at: str | None`
- `source: str = "self_owned_index_thermometer_batch"`
- `unavailable: bool` meaning all readings are unavailable
- `partial_unavailable: bool` meaning at least one but not all readings are unavailable
- `unavailable_count: int`
- `disclaimer: str = THERMOMETER_DISCLAIMER`

`ThermometerService.run()` may return:

- `ThermometerSnapshot` for legacy no-index behavior;
- `ThermometerReading` for single index;
- `ThermometerBatchResult` for batch index.

This is an intentional public Service contract expansion for P19-S2. It is preferable to UI-layer splitting because Service owns cache/source/calculation failure semantics.

### Per-Index Failure Semantics

- Well-formed but unsupported index code, akshare/network/schema-source failure, or no usable cache should produce a per-item `ThermometerReading(unavailable=True)` via existing `ThermometerUnavailable.to_reading()` semantics.
- Existing stale cache fallback remains per index: if one index source fails and stale cache exists, that item can be available with `cached=True, stale=True`.
- Malformed CLI/request input is not an item-level unavailable state; it is a request error and exits 2.
- Unexpected programming errors that prevent Service from constructing a coherent result should still exit 1.
- P19-S2 should not add broad `except Exception` around calculation/source orchestration. If calculation-contract handling is expanded, it must catch the specific `ThermometerCalculationError` and convert only data-quality insufficiency into item unavailable with a precise reason; otherwise preserve P19-S1 fail-closed behavior.

### CLI JSON Output

Single-index JSON remains unchanged.

Batch JSON should be stable and machine-readable:

```json
{
  "source": "self_owned_index_thermometer_batch",
  "requested_index_codes": ["000300", "000905"],
  "result_count": 2,
  "unavailable": false,
  "partial_unavailable": false,
  "unavailable_count": 0,
  "generated_at": "2026-05-23T00:00:00+00:00",
  "disclaimer": "本温度计基于有知有行公开方法论独立计算，非有知有行官方数据。",
  "readings": [
    {
      "index_code": "000300",
      "index_name": "沪深300",
      "temperature": "42.50",
      "pe_percentile": "40.00",
      "pb_percentile": "45.00",
      "valuation_state_candidate": "fair",
      "unavailable": false
    },
    {
      "index_code": "000905",
      "index_name": "中证500",
      "temperature": "55.00",
      "pe_percentile": "50.00",
      "pb_percentile": "60.00",
      "valuation_state_candidate": "fair",
      "unavailable": false
    }
  ]
}
```

Decimal fields remain strings, matching P19-S1 JSON behavior.

### CLI Plain Output

Single-index plain output remains unchanged.

Batch plain output should be readable and deterministic:

```text
source: self_owned_index_thermometer_batch
requested_index_codes: 000300,000905
result_count: 2
unavailable: false
partial_unavailable: false
unavailable_count: 0
disclaimer: 本温度计基于有知有行公开方法论独立计算，非有知有行官方数据。

[000300]
index_name: 沪深300
temperature: 42.50
pe_percentile: 40.00
pb_percentile: 45.00
valuation_state_candidate: fair
data_date: 2026-05-22
cached: false
stale: false
unavailable: false

[000905]
index_name: 中证500
temperature: 55.00
pe_percentile: 50.00
pb_percentile: 60.00
valuation_state_candidate: fair
data_date: 2026-05-22
cached: false
stale: false
unavailable: false
```

### CLI Exit Code

- Exit 0: command completed and rendered a `ThermometerSnapshot`, `ThermometerReading`, or `ThermometerBatchResult`, even if one or all well-formed index items are `unavailable`.
- Exit 2: invalid request/CLI input, such as malformed index code or empty batch segment.
- Exit 1: unexpected Service/internal exception that prevents rendering a coherent response.

This matches existing thermometer behavior where data unavailable is a data state, not a process failure.

## Implementation Slices

### Slice 1: Supported Index Mapping

Files:

- `fund_agent/fund/data/thermometer_source.py`
- `tests/fund/data/test_thermometer_source.py`

Work:

- Extend `SUPPORTED_INDEX_SYMBOLS` with `"000905": "中证500"`.
- Extend `INDEX_NAMES` with `"000905": "中证500"`.
- Keep PE/PB column names unchanged.
- Update source tests:
  - `000905` maps to `中证500` and calls injected PE/PB fetchers with that symbol.
  - `000300` remains supported.
  - unsupported well-formed code still raises `ThermometerSourceError`.
  - strict date schema tests remain unchanged.

### Slice 2: Batch Result Type

Files:

- `fund_agent/fund/data/thermometer_types.py`
- `fund_agent/fund/data/__init__.py`

Work:

- Add `ThermometerBatchResult` dataclass with fields listed in Proposed Contract.
- Export it from `fund_agent.fund.data`.
- Keep `ThermometerReading` unchanged to avoid disrupting P19-S1 callers.

### Slice 3: Service Batch Orchestration

Files:

- `fund_agent/services/thermometer_service.py`
- `tests/services/test_thermometer_service.py`

Work:

- Add `ThermometerRequest.index_codes: tuple[str, ...] | None = None`.
- Update validation to support exactly one of single index, batch index, or legacy no-index.
- Add a private `_load_index_batch(request)` helper that loops over normalized codes and calls the existing single-index path or shared per-index helper.
- Preserve order and de-duplicate repeated codes.
- Ensure per-index source failures become item-level unavailable through existing `ThermometerUnavailable`.
- Keep no-index path routed to `FundThermometerAdapter`.
- Do not call Capability directly from UI; Service remains the only orchestration entry point.

Tests:

- Single `index_code="000300"` remains unchanged.
- Batch `index_codes=("000300", "000905")` returns two readings in order.
- Batch with one source failure returns one available reading and one unavailable reading, exit-state data represented by `partial_unavailable=True`.
- Batch with all source failures returns `unavailable=True`, `unavailable_count == len(readings)`.
- Batch de-duplicates `("000300", "000300", "000905")` if preserve-order de-duplication is implemented.
- `index_code` and `index_codes` both set raises `ValueError`.
- Malformed `index_codes` raises `ValueError`.
- Legacy no-index adapter behavior still works and does not touch index source.

### Slice 4: CLI Batch Parsing And Rendering

Files:

- `fund_agent/ui/cli.py`
- `tests/ui/test_cli.py`

Work:

- Change `--index` help text to mention comma-separated supported codes.
- Add `_parse_index_option(index_code: str | None) -> tuple[str | None, tuple[str, ...] | None]`.
- For comma-separated input, pass `index_codes` to `ThermometerRequest`; for single input, pass `index_code`.
- Extend `_thermometer_snapshot_payload()` to recognize `ThermometerBatchResult`.
- Add `_thermometer_batch_payload()` and plain renderer branch.
- Keep no-index public-page output unchanged.

Tests:

- `fund-analysis thermometer --index 000300,000905 --json` emits `readings` with both index codes.
- Plain batch output contains `[000300]`, `[000905]`, `partial_unavailable`, `unavailable_count`, and disclaimer.
- Partial unavailable batch exits 0 and includes per-item reason.
- Malformed batch input like `000300,abc` exits 2.
- Single-index tests continue to assert `ThermometerRequest.index_code == "000300"` rather than batch.
- No-index tests continue to use legacy public-page fake snapshot.

### Slice 5: README / Test Docs Sync

Files:

- `README.md` if user-facing thermometer command examples are present.
- `fund_agent/fund/README.md` because `fund_agent/fund/` capability behavior changes.
- `tests/README.md` because tests are added.
- `fund_agent/README.md` only if it currently describes thermometer Service/Capability boundaries in a way that becomes stale.

Work:

- Document only current P19-S2 behavior: `000300`, `000905`, and comma-separated batch.
- State explicitly that no-index still uses transitional public-page query.
- State explicitly that `fund-analysis analyze` still requires explicit `--valuation-state`; automatic thermometer mapping remains future P19-S3.
- Do not document full all-A market thermometer as implemented.

## Tests

Default validation matrix:

```bash
.venv/bin/python -m pytest tests/fund/data/test_thermometer_source.py -q
.venv/bin/python -m pytest tests/fund/analysis/test_thermometer_calculator.py -q
.venv/bin/python -m pytest tests/fund/data/test_thermometer_cache.py -q
.venv/bin/python -m pytest tests/services/test_thermometer_service.py -q
.venv/bin/python -m pytest tests/ui/test_cli.py -q
.venv/bin/python -m pytest tests/fund/data/test_thermometer.py -q
.venv/bin/python -m ruff check fund_agent tests
git diff --check
```

No default test should hit live akshare. Live probe may be repeated manually as a smoke check, but it is not an exit criterion because the interface can be slow or temporarily unavailable.

## Exit Criteria

- `AkshareIndexThermometerSource` supports `000905` using `中证500`.
- Source tests cover `000905` PE/PB fixture shape and preserve strict date fail-closed behavior.
- `ThermometerBatchResult` exists and is exported.
- `ThermometerService` supports a batch request without UI-layer splitting.
- Batch service tests cover all-available, partial-unavailable, all-unavailable, validation error, and legacy no-index behavior.
- CLI supports `fund-analysis thermometer --index 000300,000905`.
- CLI JSON output includes top-level batch metadata plus per-index `readings`.
- CLI plain output is deterministic and includes per-index blocks.
- CLI exits 0 for well-formed unavailable data states, 2 for malformed request input, and 1 for unexpected internal failure.
- P19-S1 single-index behavior remains passing.
- No `fund-analysis analyze` behavior changes.
- No all-A market thermometer, PB-only all-A, parquet dependency, paid source, Dayu runtime, or `extra_payload` usage is introduced.
- Validation matrix above passes.

## Risks/Residuals

| Risk | Handling |
|---|---|
| akshare live latency | Probe took about 37.5s for PE+PB. P19-S2 should rely on per-index JSON cache and fixture tests; live smoke remains manual. |
| akshare schema drift | Existing strict field/date checks remain. Schema drift should become item unavailable through `ThermometerSourceError` and must not silently fallback to public-page scraping. |
| Batch partial failure semantics | Service owns aggregation. Data-source failures are per-item unavailable; malformed request input remains exit 2. |
| Calculation-contract errors | Preserve P19-S1 fail-closed behavior unless implementation catches specific `ThermometerCalculationError` with a precise data-quality reason. Do not use broad exception masking. |
| Output contract churn | Keep single-index JSON/plain unchanged; add batch shape only when `--index` contains multiple codes. |
| All-A pressure | Full all-A market thermometer remains blocked on P19-S5 all-A PE source verification; P19-S2 must not create placeholder PB-only results. |
| Analyze behavior drift | Automatic `valuation_state` remains P19-S3; no Service wiring into `FundAnalysisService` in P19-S2. |

## Open Questions

- Should duplicate batch codes be rejected or de-duplicated? Recommendation: de-duplicate while preserving order because repeated codes add no information and should not force duplicate network calls.
- Should `ThermometerBatchResult.generated_at` be generated by Service using UTC now, or omitted as `None` for deterministic tests? Recommendation: generate UTC now in production and assert shape rather than exact value in tests.
- Should calculation-contract insufficiency become item unavailable in batch? Recommendation: keep P19-S1 fail-closed semantics for now; only accept a targeted conversion if implementation can prove the error is ordinary data insufficiency rather than code/schema drift.

## Next Gate

`P19-S2 plan review`

Implementation should not start until independent plan review accepts the batch Service contract, per-item unavailable semantics, and the decision not to UI-split batch calls.
