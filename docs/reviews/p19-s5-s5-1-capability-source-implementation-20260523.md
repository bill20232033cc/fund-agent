# P19-S5 S5-1 Capability Source Contract Implementation — 2026-05-23

## Gate

- Work unit: P19-S5 All-A Market Thermometer
- Gate: P19-S5 S5-1 Capability Source Contract implementation
- Role: AgentCodex implementation worker
- Accepted plan: `docs/reviews/p19-s5-all-a-market-thermometer-implementation-plan-20260523.md`
- Controller acceptance: `docs/reviews/p19-s5-implementation-plan-review-controller-acceptance-20260523.md`

## Scope

本切片只实现 Capability data source contract，不修改 Service、cache、CLI、README、设计文档、控制文档、P19-S4、analyze integration、renderer 或 audit。

Allowed files touched:

- `fund_agent/fund/data/thermometer_source.py`
- `tests/fund/data/test_thermometer_source.py`
- `docs/reviews/p19-s5-s5-1-capability-source-implementation-20260523.md`

未修改 `fund_agent/fund/data/thermometer_types.py`。

## Implemented Items

- 定义全 A source constants:
  - `ALL_A_MARKET_CODE = "wind_all_a"`
  - `ALL_A_MARKET_NAME = "万得全 A / 全 A 市场"`
  - `ALL_A_DATE_COLUMN = "date"`
  - `ALL_A_PE_COLUMN = "middlePETTM"`
  - `ALL_A_PB_COLUMN = "middlePB"`
  - `ALL_A_SOURCE_NAME = "akshare_legulegu_all_a_pe_pb"`
- 新增 Capability 共享分类与展示名 helper:
  - `classify_thermometer_code(code) -> "index" | "market" | "unsupported"`
  - `is_supported_thermometer_code(code)`
  - `thermometer_display_name(code)`
  - 保留 `is_supported_index_code()`，并改为委托共享分类器，确保 `wind_all_a` 不伪装成六位指数。
- 新增 `AkshareAllAMarketThermometerSource`:
  - PE no-arg fetcher 调用 `ak.stock_a_ttm_lyr()`
  - PB no-arg fetcher 调用 `ak.stock_a_all_pb()`
  - fetch 阶段使用有界重试，重试耗尽后统一抛 `ThermometerSourceError("全 A 估值数据获取失败：...")`
- 保留 `AkshareIndexThermometerSource` 的 symbol-based fetcher 行为，未合并全 A no-arg fetcher。
- 新增薄复合 source `AkshareThermometerSource`，通过共享分类器分派支持指数与全 A 市场。
- 新增全 A 严格解析路径:
  - 仅接受 `date` + `middlePETTM` / `middlePB`
  - 中文 `日期` 字段 fail-closed
  - 严格 ISO 日期校验
  - 拒绝 bool、非数值、NaN、Infinity
  - 空值和非正数行按计划丢弃；有效共同日期为空则失败
  - 相同日期相同值折叠；相同日期冲突值 fail-closed
  - PE/PB 使用共同日期交集，不插补
- 未改变现有指数 `_records_by_date()` 重复日期后写覆盖行为。

## Tests Added / Preserved

- 覆盖 `wind_all_a` 合并 `stock_a_ttm_lyr` + `stock_a_all_pb` source-shaped rows，并返回排序后的共同日期。
- 覆盖全 A fixture 误用中文 `日期` 时 fail-closed。
- 覆盖只使用 `middlePETTM` 与 `middlePB`，忽略 average/close/quantile 等无关字段。
- 覆盖重复日期冲突失败、重复日期相同值折叠。
- 覆盖非严格日期失败。
- 覆盖 bool/null/non-positive/non-numeric/NaN/Infinity 的拒绝或丢弃语义，以及共同日期不足失败。
- 覆盖第一次瞬态失败重试成功、连续瞬态失败抛 `ThermometerSourceError`。
- 保留并继续通过现有 `000300` / `000905` 指数 source 行为测试。

## Validation

```text
pytest tests/fund/data/test_thermometer_source.py -q
37 passed in 0.07s
```

```text
ruff check fund_agent/fund/data/thermometer_source.py tests/fund/data/test_thermometer_source.py
All checks passed!
```

```text
git diff --check
passed with no output
```

## Residual Risks / Later Slices

- Service/cache/CLI/default `wind_all_a` routing intentionally未实现；按 accepted plan 属于 S5-2 / S5-3。
- 本切片测试使用 fake fetchers，不跑 live akshare 网络；live availability 仍是外部数据源风险。
- 当前有界重试只覆盖 source fetch 阶段，不对 schema drift 做重试；这是 fail-closed 设计，避免字段漂移被重试掩盖。

## Scope Confirmation

本实现未 commit、未 push、未创建 PR。除本报告外，代码改动仅发生在允许的 `fund_agent/fund/data/thermometer_source.py` 与 `tests/fund/data/test_thermometer_source.py`。工作区存在进入本任务前的未跟踪文档文件，本切片未修改它们。
