# P19-S5 All-A Market Thermometer Implementation Plan — 2026-05-23

## Verdict

`PLAN_READY`

本 artifact 仅作为 Gateflow planning worker handoff。它不实现代码、不修改测试、不提交、不推送、不打开 PR，也不修改 `docs/design.md` 或 `docs/implementation-control.md`。

## 1. Goal

在已接受的 P19-S5 source feasibility 基础上，把全 A 市场温度计纳入现有 P19 自建温度计能力：

- `fund-analysis thermometer` 默认输出全 A 市场温度计读数。
- `fund-analysis thermometer --index wind_all_a` 显式输出全 A 市场温度计读数。
- `fund-analysis thermometer --index wind_all_a,000300,000905 --json` 支持全 A 与现有宽基指数混合批量输出。
- 全 A PE/PB 历史只使用 `akshare.stock_a_ttm_lyr()` 的 `middlePETTM` 与 `akshare.stock_a_all_pb()` 的 `middlePB`。
- 保持现有 P19-S1/S2 宽基指数温度计、P19-S3 `analyze` 自动估值边界不回归。

## 2. Motivation

`docs/design.md` v2.2 §11 把万得全 A / 全 A 市场列为 P0 温度计覆盖目标，但要求先通过 all-A PE source gate。当前 source gate 已接受：akshare 1.18.60 的 Legulegu all-A PE/PB 历史接口可提供共同日期 4828 天，满足全 A PE+PB 温度计实现前提。

从第一性原理看，本次实现的最小正确路径是复用现有 `PePbHistory`、`ThermometerCalculator`、`ThermometerHistoryCache`、`ThermometerService` 和 CLI 输出结构，仅扩展 Capability data source 与请求规范化。不要为全 A 单独建立 UI、Service 或计算管线。

## 3. Non-Goals

- 不使用有知有行页面作为生产温度计数据源；现有 `FundThermometerAdapter` 只能继续作为过渡公开页查询或对比输入。
- 不新增 P19-S4 扩展指数来源，不支持 `399006`、`000688`、`000922`、`000932`、`000933`。
- 不改变 `fund-analysis analyze` 已接受的 P19-S3 行为：只对 exact identity 映射到 `000300` 或 `000905` 的指数/指数增强基金自动调用温度计；本次不把全 A 自动映射给主动基金、复合基准或无法精确归类基准。
- 不引入 Dayu、Host、Engine/tool loop、LLM audit、Evidence Confirm、指数成分提取、方法论提取、tracking-error 计算、外部付费数据源。
- 不把显式参数塞进 `extra_payload`；所有新增请求字段必须显式声明。
- 不输出买入、卖出、仓位比例或未来收益预测。

## 4. Source Evidence

- `docs/reviews/p19-s5-source-feasibility-20260523.md`：`akshare.stock_a_ttm_lyr()` 返回 all-A PE 历史，接受字段为 `middlePETTM`；`akshare.stock_a_all_pb()` 返回 all-A PB 历史，接受字段为 `middlePB`；共同日期 4828 天，区间 2005-01-05 到 2026-05-22。
- `docs/reviews/p19-s5-source-feasibility-controller-judgment-20260523.md`：Controller verdict 为 `ACCEPT_IMPLEMENTATION_PLAN`，并要求 implementation plan 明确 source adapter ownership、`wind_all_a` 显式市场代码、fixture、严格日期/数值/重复日期/共同日期合并、retry/unavailable、cache/CLI 不回归、不得改变 P19-S3 analyze 边界。
- `docs/design.md` v2.2 §11.4：万得全 A / 全 A 市场代码为 `wind_all_a`，Phase 为 P19-S5 / all-A PE source gate 后。
- `docs/design.md` v2.2 §11.5：UI 只依赖 Service；Service 编排缓存、数据源选择和输出模型；Capability data source 读取 PE/PB；Cache 只存储；Calculator 纯计算。

## 5. Design-Boundary Checklist

| 检查项 | Plan decision |
|---|---|
| UI 不直接调用 akshare | 只改 CLI 参数说明和 payload 输出；所有数据读取经 `ThermometerService` |
| Service 不直接调用 akshare | Service 只调用 `_IndexThermometerSource.load_index_history()` 和 cache/calculator |
| Data-source adapter 留在 Capability data | all-A source 放在 `fund_agent/fund/data/thermometer_source.py` |
| Cache 不计算、不抓取 | `ThermometerHistoryCache` 只按 code 保存/读取 JSON |
| Calculator 不 IO | 复用现有 `calculate_thermometer_reading()` |
| 不使用有知有行生产来源 | 全 A adapter 只调用 akshare Legulegu all-A PE/PB |
| 不改变 analyze 行为 | 不修改 `fund_agent/services/fund_analysis_service.py`、估值解析或 renderer/audit |
| 不用 `extra_payload` | `ThermometerRequest` 显式字段承载请求 |
| 不引入未来 phase | 不实现 P19-S4、主动基金全 A映射、LLM/Evidence Confirm/Dayu |

## 6. Affected Files And Ownership

### UI Layer

- `fund_agent/ui/cli.py`
  - Ownership: UI command parsing and display only.
  - Allowed: update `thermometer --index` help text to include `wind_all_a`; make default CLI request route to self-owned all-A instead of public-page snapshot; keep JSON/plain payload shape stable.
  - Forbidden: direct akshare import, direct Capability source construction, analyze behavior changes.

### Service Layer

- `fund_agent/services/thermometer_service.py`
  - Ownership: request normalization, self-owned thermometer routing, cache/source/calculator orchestration.
  - Allowed: accept `wind_all_a` as well-formed market code; default `ThermometerRequest(index_code=None, index_codes=None)` routes to `wind_all_a`; keep public-page query only if an explicit backward-compatible path is already present or controller approves a separate flag. In this plan, no new public-page flag is required.
  - Forbidden: direct akshare calls, source-specific field parsing, analyze integration changes.

### Capability Data Layer

- `fund_agent/fund/data/thermometer_source.py`
  - Ownership: akshare source adapter and PE/PB parsing.
  - Allowed: add explicit all-A market constants and an all-A branch/class using `stock_a_ttm_lyr()` + `stock_a_all_pb()`; freeze fields to `middlePETTM` + `middlePB`; share strict parsing helpers where appropriate.
  - Forbidden: using board-level/index-level/spot/current-only substitutes; Youzhiyouxing scrape; PB-only or PE-only thermometer.

- `fund_agent/fund/data/thermometer_types.py`
  - Ownership: structured thermometer contracts.
  - Allowed: docstring/general wording change from "index" to "index or market" where existing fields are reused; no schema break required.

- `fund_agent/fund/data/thermometer_cache.py`
  - Ownership: versioned JSON history cache.
  - Allowed: cache-key path classification for `wind_all_a`, preferably `cache/thermometer/market/wind_all_a_history.json`; if implementation keeps one generic path helper, tests must assert no collision with `index/000300_history.json`.
  - Forbidden: cache-based support bypass for unsupported codes.

- `fund_agent/fund/data/__init__.py`
  - Ownership: public exports.
  - Allowed only if new public constants/types are intentionally exported; otherwise leave unchanged.

### Capability Analysis Layer

- `fund_agent/fund/analysis/thermometer_calculator.py`
  - Ownership: PE/PB percentile calculation.
  - Expected: no change. Existing calculator should work for all-A `PePbHistory`.
  - Stop if all-A requires new calculation semantics; that would be design drift.

### Tests

- `tests/fund/data/test_thermometer_source.py`
- `tests/fund/data/test_thermometer_cache.py`
- `tests/services/test_thermometer_service.py`
- `tests/ui/test_cli.py`
- `tests/README.md`

### README Docs

- `README.md`
- `fund_agent/fund/README.md`

Docs updates are needed because CLI default behavior and Fund package thermometer coverage change. `fund_agent/README.md` is only needed if implementation changes architecture boundaries; this plan should not require it.

## 7. Explicit Contract Decisions

### 7.1 All-A Code And Name

- Code: `wind_all_a`.
- Name: `万得全 A / 全 A 市场`.
- Semantics: explicit market thermometer code, not a six-digit index code and not overloaded into index-code validation.
- Support check:
  - `is_supported_index_code("000300") == True`
  - `is_supported_index_code("000905") == True`
  - Add a separate helper, for example `is_supported_thermometer_code(code)` or `is_supported_market_code(code)`, so `wind_all_a` does not pretend to be an index.

### 7.2 PePbHistory Fields

Reuse `PePbHistory.index_code` and `PePbHistory.index_name` for compatibility:

- For all-A: `index_code="wind_all_a"`, `index_name="万得全 A / 全 A 市场"`.
- No new dataclass field is required in this slice.
- Update docstrings to say "指数或市场代码/名称" where touched.
- `source="akshare_legulegu_all_a_pe_pb"`.

### 7.3 Source Adapter

- Controller decision: add a separate `AkshareAllAMarketThermometerSource`
  in this module, and keep `AkshareIndexThermometerSource` for six-digit indexes.
  Do not merge no-arg all-A fetchers into the symbol-based index source class.
- Required fetchers:
  - `pe_fetcher: Callable[[], object] | None` for `ak.stock_a_ttm_lyr()`.
  - `pb_fetcher: Callable[[], object] | None` for `ak.stock_a_all_pb()`.
- Required source fields:
  - all-A date column: `ALL_A_DATE_COLUMN = "date"` (English), because both accepted all-A PE and PB akshare outputs use `date`.
  - existing index date column remains `DATE_COLUMN = "日期"` and must not be reused for all-A fixtures.
  - PE value: `ALL_A_PE_COLUMN = "middlePETTM"`.
  - PB value: `ALL_A_PB_COLUMN = "middlePB"`.
- Do not read or use `averagePETTM`, `middlePELYR`, `averagePELYR`, `equalWeightAveragePB`, `close`, `quantile`, or any akshare precomputed quantile.
- Source fetch must be wrapped so Legulegu SSL EOF / connection resets / timeout-like exceptions become `ThermometerSourceError("全 A 估值数据获取失败：...")` after retry exhaustion.
- Expose one shared code classifier from the Capability data layer, for example
  `classify_thermometer_code(code) -> Literal["index", "market", "unsupported"]`,
  plus helper name lookups. Service and cache must import this classifier instead
  of duplicating `code == "wind_all_a"` checks.

### 7.4 Cache Key

- `wind_all_a` cache must not live under `index/`.
- Preferred path: `cache/thermometer/market/wind_all_a_history.json`.
- Existing index paths remain unchanged:
  - `cache/thermometer/index/000300_history.json`
  - `cache/thermometer/index/000905_history.json`
- Cache load/save must use the same code classifier as Service/source support checks. Unsupported well-formed codes must not be returned from cache just because a file exists.
- Implement `_path_for()` using the shared classifier. It must route `wind_all_a`
  to `market/` and supported six-digit codes to `index/`. Unsupported codes
  should not reach cache lookup until Service support checks allow that path.

### 7.5 CLI Default Behavior

- `fund-analysis thermometer` with no `--index` now queries self-owned all-A market thermometer.
- `fund-analysis thermometer --json` outputs all-A reading JSON.
- The CLI should no longer default to Youzhiyouxing public-page snapshot in P19-S5. Do not add a new public-page CLI flag unless controller explicitly asks; public-page adapter remains internal transitional/comparison capability.
- `--force-refresh` help text should refer to self-owned thermometer history data, not public page data.
- Implement the default by changing `_normalize_request()` so the no-index
  request returns `_NormalizedThermometerRequest(index_code="wind_all_a",
  index_codes=None)`. `run()` should then continue through the existing
  single-reading path. This makes the default behavior explicit in one place.
- The legacy public-page adapter path becomes internal/transitional only in this
  gate. Do not remove `FundThermometerAdapter`; keep its dedicated data-layer
  tests. Do not add a public CLI flag unless a later controller decision reopens
  comparison UX.

### 7.6 Batch Behavior

- `--index` accepts comma-separated tokens that may include `wind_all_a`, `000300`, `000905`.
- Normalize by trimming whitespace and preserve-order de-duplicate.
- Malformed tokens exit 2. For this gate, valid token shape is either:
  - exact `wind_all_a`, or
  - exactly six ASCII digits.
- Modify `_normalize_index_codes()` to accept only exact `wind_all_a` or exactly
  six ASCII digits. The error message should mention both allowed shapes. It
  must still reject empty tokens, whitespace-only tokens, `abc`, `wind`,
  `wind_all_a1`, and non-ASCII digit variants unless explicitly tested.
- Well-formed but unsupported six-digit codes remain item-level `unavailable` in batch, as current behavior does.
- Unsupported non-six-digit market-like codes other than `wind_all_a` are malformed request errors, not item-level unavailable, unless implementation deliberately adds a broader market-code grammar and tests it.

### 7.7 JSON Output

- Single all-A JSON uses existing `ThermometerReading` payload keys:
  - `source`
  - `cached`
  - `stale`
  - `unavailable`
  - `unavailable_reason`
  - `index_code`
  - `index_name`
  - `temperature`
  - `pe_percentile`
  - `pb_percentile`
  - `valuation_state_candidate`
  - `data_date`
  - `lookback_start`
  - `lookback_end`
  - `fetched_at`
  - `disclaimer`
- For `wind_all_a`, `index_code` intentionally remains the existing output key for compatibility; the value makes market semantics explicit.
- Batch JSON keeps current `ThermometerBatchResult` shape and may keep `source="self_owned_index_thermometer_batch"` for compatibility, but preferred low-risk wording is `source="self_owned_thermometer_batch"`. If changed, update tests and README together.

### 7.8 Unavailable Semantics

- Source/network/schema failures return `ThermometerSourceError` from Capability data source.
- Service behavior:
  - fresh cache hit returns cached reading.
  - source failure with stale cache returns stale cached reading.
  - source failure without cache returns `ThermometerUnavailable(...).to_reading()` with `valuation_state_candidate="unavailable"` and exit 0 at CLI.
  - calculation contract errors such as sample count below `MIN_HISTORY_POINTS` or non-positive values in saved history must continue to propagate as errors, not silently become stale-cache fallback.
- All-A partial failures in batch are item-level unavailable; other valid readings still return.
- When source support or source failure returns `ThermometerUnavailable`, resolve
  the human-readable name through the shared Capability helper. For `wind_all_a`,
  the unavailable reading must use `index_name="万得全 A / 全 A 市场"`, not
  `index_name="wind_all_a"`.

## 8. Strict Parsing Rules

### Dates

- Accept Python `datetime` and `date` objects by converting to `YYYY-MM-DD`.
- Accept only exact ISO date strings matching `^\d{4}-\d{2}-\d{2}$`.
- Reject strings with time, slash separators, compact form, leading/trailing whitespace, impossible dates, empty values, and `None`.

### Positive Decimal

- Convert values through `Decimal(str(value))`.
- Reject `None`, bool, non-numeric, NaN, Infinity and `<= 0`.
- For all-A PE/PB parsing, null or non-positive `middlePETTM` / `middlePB` rows must be dropped only if at least one valid same-date pair remains and no duplicate conflict exists. If all rows are dropped or common intersection becomes insufficient, raise `ThermometerSourceError`.
- Do not impute missing values.

### Duplicate Dates

- Duplicate same-date rows with the same normalized value may be idempotently collapsed.
- Duplicate same-date rows with conflicting positive values must fail closed with `ThermometerSourceError` mentioning duplicate/conflict.
- Do not silently let later rows overwrite earlier rows.

### Common Date Intersection

- Build PE and PB maps independently, then compute sorted common dates.
- Use only common dates for `PePbPoint`.
- Dates present in only one side are ignored, not imputed.
- If common dates are empty or below calculator minimum history (`MIN_HISTORY_POINTS`), source may raise `ThermometerSourceError` before calculator or let calculator raise; tests should prefer source-level error for empty intersection and calculator-level error for intentionally short but structurally valid histories.

### Retry And Legulegu SSL EOF

- Add bounded retry inside Capability source fetch, not UI/Service.
- Retry applies to transient fetch exceptions from akshare/requests/httpx/urllib-style connection issues, including observed Legulegu SSL EOF.
- Suggested constants:
  - `SOURCE_RETRY_ATTEMPTS = 3`
  - `SOURCE_RETRY_BACKOFF_SECONDS = 0.2`
- Tests must inject a fake fetcher that fails once with an SSL EOF-shaped exception and then succeeds.
- After retry exhaustion, raise `ThermometerSourceError`; Service handles stale cache or unavailable.

## 9. Fixture Strategy

- No test may require live network.
- Use source-shaped fake frames with `to_dict(orient="records")`.
- All-A PE fixture rows must include `date` and `middlePETTM`; may include unused fields to prove they are ignored.
- All-A PB fixture rows must include `date` and `middlePB`; may include unused fields to prove they are ignored.
- Add at least one source test whose fixture intentionally uses Chinese `日期`
  for all-A rows and assert it fails closed, so tests prove the all-A contract is
  source-shaped and not copied from the index source.
- Include at least 30 common dates in Service/CLI tests that calculate a real reading.
- Keep source tests small for parsing behavior; for calculator path, helper-generated 30 rows are fine.
- Do not check in full 4828-row live responses unless controller explicitly accepts fixture size. Minimal deterministic fixtures are enough for contract tests.

## 10. Implementation Slices

### Slice S5-1 — Capability Source Contract

Objective: Add all-A source support in Capability data while preserving existing index source behavior.

Allowed files:

- `fund_agent/fund/data/thermometer_source.py`
- `fund_agent/fund/data/thermometer_types.py` only for docstring wording if needed
- `tests/fund/data/test_thermometer_source.py`

Exact changes:

- Define all-A constants:
  - `ALL_A_MARKET_CODE = "wind_all_a"`
  - `ALL_A_MARKET_NAME = "万得全 A / 全 A 市场"`
  - `ALL_A_DATE_COLUMN = "date"`
  - `ALL_A_PE_COLUMN = "middlePETTM"`
  - `ALL_A_PB_COLUMN = "middlePB"`
  - `ALL_A_SOURCE_NAME = "akshare_legulegu_all_a_pe_pb"`
- Add support classifier that distinguishes six-digit indexes from explicit all-A market and export/import it consistently from source/cache/service code.
- Add `AkshareAllAMarketThermometerSource` with no-arg fetchers. Keep `AkshareIndexThermometerSource` unchanged for symbol-based index fetchers.
- Add a thin composite source, for example `AkshareThermometerSource`, that implements `ThermometerDataSource.load_index_history(code)` by dispatching to the index source or all-A market source using the shared classifier. Service keeps one injected thermometer source object and does not learn akshare field names.
- Add no-arg all-A fetchers that call `ak.stock_a_ttm_lyr()` and `ak.stock_a_all_pb()`.
- Add retry wrapper around fetchers for transient Legulegu failures.
- Harden all-A parsing to enforce strict `date`, positive Decimal, duplicate conflict detection, and common-date intersection. Do not change existing index `_records_by_date()` duplicate overwrite behavior in this slice unless adding explicit index regression tests proving no P19-S1/S2 behavior regression.
- Preserve existing tests for `000300` and `000905`.

Tests:

- `wind_all_a` merges `stock_a_ttm_lyr` + `stock_a_all_pb` source-shaped rows and returns sorted common dates.
- All-A source-shaped rows use exact `date`, not `日期`.
- Only `middlePETTM` and `middlePB` are used; unused fields with different values do not affect output.
- duplicate same-date conflicting PE or PB fails closed.
- duplicate same-date identical rows collapse.
- non-strict dates fail closed.
- bool/null/non-positive/non-numeric values are rejected or dropped according to §8, with empty/insufficient intersection failing.
- first Legulegu SSL EOF-shaped failure retries and succeeds.
- repeated transient failures raise `ThermometerSourceError`.

Validation commands:

```text
pytest tests/fund/data/test_thermometer_source.py -q
ruff check fund_agent/fund/data/thermometer_source.py tests/fund/data/test_thermometer_source.py
```

Stop conditions:

- Stop if akshare source-shaped fields differ from accepted artifact (`middlePETTM`, `middlePB`).
- Stop if all-A cannot be supported without making `wind_all_a` look like a six-digit index.
- Stop if implementation needs live network tests to pass.

No future-slice leakage:

- Do not change CLI default, Service default routing, README, or analyze behavior in this slice.

### Slice S5-2 — Service, Cache Key, And Request Normalization

Objective: Route self-owned all-A market thermometer through existing Service/cache/calculator boundaries.

Allowed files:

- `fund_agent/services/thermometer_service.py`
- `fund_agent/fund/data/thermometer_cache.py`
- `tests/services/test_thermometer_service.py`
- `tests/fund/data/test_thermometer_cache.py`

Exact changes:

- Default `ThermometerRequest()` should normalize to `index_code="wind_all_a"` or an internal equivalent, so no-argument thermometer uses all-A.
- Extend normalization to accept exact `wind_all_a` plus six-digit index codes.
- Modify `_normalize_request()` to materialize the default all-A code in the
  normalized request. Modify `_normalize_index_codes()` to allow exact
  `wind_all_a` or six ASCII digits; do not add broader market-code grammar.
- Keep `index_code` and `index_codes` mutually exclusive.
- Ensure unsupported six-digit codes remain item-level unavailable, including when a fresh cache file exists.
- Ensure unsupported market-like strings are request errors unless explicitly supported.
- Cache path for `wind_all_a` must be `market/wind_all_a_history.json` or another tested non-index namespace.
- Cache, Service support checks, and source dispatch must all use the same
  classifier/helper exported from Capability data. Tests must fail if
  `wind_all_a` is saved under `index/`.
- Source failure for all-A uses stale cache if available; otherwise returns unavailable reading with all-A code/name.
- Calculation errors still propagate.

Tests:

- `ThermometerService().run(ThermometerRequest(cache_dir=tmp_path))` calls source for `wind_all_a`, not public-page adapter.
- Explicit `index_code="wind_all_a"` returns all-A reading.
- `_normalize_index_codes` accepts `wind_all_a` for both single and batch paths and still rejects all other non-six-digit tokens.
- Batch `("wind_all_a", "000300", "000905")` preserves order and de-duplicates.
- Batch partial unavailable still works when one supported code source fails.
- Cache file for `wind_all_a` is under market namespace and does not collide with index namespace.
- Fresh fake cache for unsupported `999999` or unsupported market-like code cannot bypass support check.
- Stale cache fallback works for all-A source failure.
- Source failure without cache returns unavailable reading with `index_name="万得全 A / 全 A 市场"`.
- Public-page adapter tests remain in `tests/fund/data/test_thermometer.py`; Service no-arg default test is updated from public-page delegation to all-A source routing.
- Run or add P19-S3 analyze non-regression coverage proving exact `000300` analyze integration still sends `ThermometerRequest(index_code="000300", ...)`, not default `wind_all_a`.

Validation commands:

```text
pytest tests/services/test_thermometer_service.py tests/fund/data/test_thermometer_cache.py -q
pytest tests/services/test_fund_analysis_service.py -q
ruff check fund_agent/services/thermometer_service.py fund_agent/fund/data/thermometer_cache.py tests/services/test_thermometer_service.py tests/fund/data/test_thermometer_cache.py
```

Stop conditions:

- Stop if changing default thermometer behavior would require a user-facing compatibility flag not accepted by controller.
- Stop if Service needs to know source field names or import akshare.
- Stop if `analyze` tests require changes outside P19-S3 accepted boundaries.

No future-slice leakage:

- Do not update CLI help/output or README in this slice unless required to keep tests compiling.

### Slice S5-3 — CLI Output And Docs Sync

Objective: Expose all-A default behavior through CLI and synchronize user/developer docs.

Allowed files:

- `fund_agent/ui/cli.py`
- `tests/ui/test_cli.py`
- `README.md`
- `fund_agent/fund/README.md`
- `tests/README.md`
- `fund_agent/README.md` only if implementation changed layering text; expected no change

Exact changes:

- Update `thermometer --index` help to mention `wind_all_a`, `000300`, `000905`.
- Update `--force-refresh` help to say self-owned thermometer history data.
- Ensure no-argument `fund-analysis thermometer --json` emits all-A `ThermometerReading` payload.
- Keep plain output readable and include `index_code: wind_all_a`, `index_name: 万得全 A / 全 A 市场`, `source`, `temperature`, PE/PB percentiles, valuation candidate, and disclaimer.
- Batch plain/JSON must render `wind_all_a` alongside index readings.
- README root: update quick commands and temperature section so all-A is default; keep public-page snapshot wording only if still exposed, otherwise state it is no longer the default CLI path.
- `fund_agent/fund/README.md`: update self-owned thermometer coverage from P19-S1/S2 index-only to include P19-S5 all-A; mention cache namespace.
- `tests/README.md`: update thermometer source/cache/service/CLI test descriptions.

Tests:

- CLI no-argument JSON uses fake Service all-A reading and forwards `ThermometerRequest(index_code=None, index_codes=None)`; Service owns default routing.
- CLI `--index wind_all_a --json` emits all-A reading.
- CLI `--index wind_all_a,000300 --json` emits requested codes in order.
- CLI malformed `--index wind_all_a,abc` exits 2.
- Existing `--index 000300`, `--index 000300,000905`, unavailable and service-error tests still pass.

Validation commands:

```text
pytest tests/ui/test_cli.py -q
pytest tests/fund/data/test_thermometer_source.py tests/fund/data/test_thermometer_cache.py tests/services/test_thermometer_service.py tests/ui/test_cli.py -q
pytest tests/services/test_fund_analysis_service.py -q
ruff check fund_agent/fund/data/thermometer_source.py fund_agent/fund/data/thermometer_cache.py fund_agent/services/thermometer_service.py fund_agent/ui/cli.py tests/fund/data/test_thermometer_source.py tests/fund/data/test_thermometer_cache.py tests/services/test_thermometer_service.py tests/ui/test_cli.py
git diff --check
```

Stop conditions:

- Stop if docs would need to claim `analyze` uses all-A. That is out of scope.
- Stop if CLI output requires schema-breaking renames from `index_code` to `market_code`; keep compatibility for this gate.

No future-slice leakage:

- Do not modify `fund_agent/services/fund_analysis_service.py`, valuation-state mapping, renderer, audit, or design/control docs.

## 11. Review Gates

Plan review must verify:

- `wind_all_a` is explicit and not treated as a six-digit index.
- all-A fixtures use exact `date` source shape, while index fixtures continue using `日期`.
- source architecture uses separate no-arg all-A source plus composite dispatch, rather than forcing no-arg and symbol-arg fetchers into the same source class.
- `_normalize_request()` and `_normalize_index_codes()` have a precise path for default all-A and explicit `wind_all_a`.
- Service, source, and cache share one code classifier/helper.
- Adapter uses only `stock_a_ttm_lyr().middlePETTM` and `stock_a_all_pb().middlePB`.
- No UI/Service direct akshare import.
- Strict parsing covers dates, Decimal, duplicates, common-date intersection, null/non-positive rows.
- Retry/unavailable behavior handles Legulegu SSL EOF without live-network tests.
- CLI default behavior is deliberate and README-consistent.
- P19-S3 analyze behavior is untouched.
- No future-slice leakage into P19-S4 or external data/LLM/Engine scopes.

## 12. Residual Risks And Future Owners

- Legulegu public token/SSL instability: current owner P19-S5 implementation handles retry, cache, stale fallback and unavailable. Future production hardening may add source health telemetry, but not in this gate.
- Legulegu all-A universe definition is not fully enumerated per security: accepted by source feasibility; future methodology disclosure or alternative source comparison may refine wording, but current implementation should not block.
- Public-page thermometer comparison/deviation tracking: future validation/observability phase, not P19-S5 implementation.
- P19-S4 expanded index coverage remains deferred to a later source-feasibility gate.
- Active-fund all-A fallback for `analyze`: future valuation-state integration gate only; not owned by this plan.
- Cache migration from old public-page snapshot default: no migration needed because self-owned history cache uses separate files; public-page cache can remain unused.

## 13. Blocking Questions For Controller

None.

## 14. Completion Report Format For Implementation Agent

Implementation agent should report:

- Slice id completed.
- Changed files.
- Contract decisions implemented exactly or deviations with reason.
- Validation commands and results.
- Docs updated or not needed, with AGENTS.md trigger reason.
- Residual risks classified as fixed, later slice, later phase/work unit, existing issue, or user decision.
- Confirmation that no files outside allowed slice scope were modified.
