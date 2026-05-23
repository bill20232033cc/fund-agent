# Code Review

## Scope

- Mode: current changes (aggregate / phase readiness)
- Branch: `phase/p19-s5-all-a-pe-source-gate`
- Base: `main`
- Output file: `docs/reviews/p19-s5-aggregate-deepreview-glm-20260523.md`
- Included scope: P19-S5 S5-1 (Capability all-A source) / S5-2 (Service cache normalization) / S5-3 (CLI docs sync) 共 8 个 accepted commit (f4ee668..2ab9b33)，涉及 `thermometer_source.py`、`thermometer_service.py`、`thermometer_cache.py`、`cli.py`、三份 README 及对应的 4 个测试文件
- Excluded scope: 评审/计划 artifact 文档本身；pre-existing untracked docs；P19-S1~S4 已合入 main 的代码
- Parallel review coverage: 无 subagent；主 reviewer 逐文件走读全部实现和测试

## Findings

未发现实质性问题。

逐项验证依据如下。

### Cross-slice correctness

- **All-A source 使用 exact akshare contract**：`thermometer_source.py:23-26` 定义 `ALL_A_DATE_COLUMN = "date"`、`ALL_A_PE_COLUMN = "middlePETTM"`、`ALL_A_PB_COLUMN = "middlePB"`；`AkshareAllAMarketThermometerSource._fetch_pe_frame_once` 调用 `ak.stock_a_ttm_lyr()`（line 356），`_fetch_pb_frame_once` 调用 `ak.stock_a_all_pb()`（line 375）；`_strict_positive_records_by_date` 使用上述三个常量提取数据（lines 414-418）。与 design.md section 11.4 要求的"通过 all-A PE 来源门槛"一致。
- **Service 默认路由 no-index 到 wind_all_a**：`thermometer_service.py:304` 在 `index_code` 和 `index_codes` 均为 None 时设置 `index_code=ALL_A_MARKET_CODE`。测试 `test_thermometer_service_defaults_to_all_a_source` 验证默认请求走自建全 A 路径且不触发公开页 adapter。
- **Cache namespace market/index 分离**：`thermometer_cache.py:131-136` 按 `classify_thermometer_code` 返回值分别路由到 `market/` 和 `index/` 目录。测试 `test_thermometer_history_cache_uses_market_namespace_for_all_a` 验证 `wind_all_a` 只写入 `market/wind_all_a_history.json`，不落入 `index/`；`test_thermometer_history_cache_preserves_index_namespace` 验证既有指数路径不回归。
- **CLI/docs 反映默认 all-A**：CLI `--help` 包含 `wind_all_a`（测试 line 1015）；README 更新为"默认查询全 A 市场 `wind_all_a`"；fund README 更新覆盖范围为 P19-S1/S2/S5。

### Boundary

- **UI 只依赖 Service**：`cli.py` 仅导入 `ThermometerRequest`、`ThermometerService` 和类型 `ThermometerBatchResult`、`ThermometerReading`，不直接调用 Capability source/cache/calculator。
- **Service 无 akshare 或 source field names**：`thermometer_service.py` 导入 `ALL_A_MARKET_CODE`（Capability 代码常量）、`AkshareThermometerSource`（具体数据源类）、`classify_thermometer_code`（分类器）、`thermometer_display_name`（展示名）、`ThermometerSourceError`（错误类型）。不导入 `date`/`middlePETTM`/`middlePB`/`PE_COLUMN`/`PB_COLUMN` 等 akshare 字段名。S5-2 controller 已接受 `AkshareThermometerSource` 直接构造为 non-blocking（factory abstraction premature）。
- **Capability owns parsing/classifier**：`classify_thermometer_code` 定义在 `thermometer_source.py`，Service/cache/CLI 全部通过导入使用，不存在跨层重定义。
- **Cache stores only**：`ThermometerHistoryCache` 只做 JSON 读写和 TTL 判断，不计算温度、不决定估值状态、不访问外部数据源。
- **Analyze 行为未扩展到 all-A**：README 明确"analyze 自动估值仍只使用沪深300/中证500 exact supported-index 单指数路径，不把全 A 自动套用于主动基金或复合基准"。FundAnalysisService 的 valuation state resolution 只映射 exact benchmark 到 supported index codes，wind_all_a 不是任何基金 benchmark。

### Failure semantics

- **Schema drift / invalid rows fail closed**：`_strict_positive_records_by_date`（lines 488-538）在 schema 缺列（line 522）、日期非严格 ISO（line 563）、bool/NaN/Infinity 值（lines 612-619）、重复日期冲突（line 534）时均 raise `ThermometerSourceError`。全 A 不存在插补或静默丢弃有效行的路径。
- **Source transient failures become source error**：`_fetch_all_a_with_retry`（lines 430-450）连续失败 `ALL_A_FETCH_MAX_ATTEMPTS`(2) 次后 raise `ThermometerSourceError`，从最后一次异常 cause 链。
- **Service stale cache fallback**：`_load_index_reading`（lines 235-249）在 `ThermometerSourceError` 时先尝试 `cache.load(index_code, allow_stale=True)`，有 stale cache 则返回读数（stale=True），无 cache 则返回 `ThermometerUnavailable.to_reading()`。测试覆盖指数和全 A 两种 stale fallback 路径。
- **Service unavailable behavior**：无 fresh cache、source 失败、无 stale cache 时返回 `unavailable=True` 的 `ThermometerReading`，包含 index_code、index_name、reason。测试 `test_thermometer_service_returns_unavailable_without_all_a_cache` 验证全 A 路径。
- **Calculation contract errors propagate**：样本不足时 `calculate_thermometer_reading` raise `ThermometerCalculationError`（继承 `ValueError`），Service 不捕获该异常，不包装为 unavailable。测试 `test_thermometer_service_propagates_calculation_contract_error` 和 `test_thermometer_service_propagates_all_a_stale_cache_calculation_error` 分别验证新鲜路径和 stale cache 路径。

### Cache support bypass prevention

- **Unsupported codes 返回 None**：`ThermometerHistoryCache.load` line 70-71 在 `classify_thermometer_code(index_code) == "unsupported"` 时直接返回 None，不读文件。
- **Exact wind_all_a 和 exact six ASCII digit normalization**：`_normalize_index_codes`（lines 307-337）接受 `wind_all_a` 或恰好 6 位 ASCII 数字（`_is_six_ascii_digits`），其余 reject 为 `ValueError`。全角数字 `１２３４５６`、空字符串、带空白均被拒绝。测试覆盖 7 种 malformed 模式。
- **Unsupported well-formed codes item-level unavailable**：Service `_load_index_reading` 在 `classify_thermometer_code(index_code) == "unsupported"` 时直接返回 `ThermometerUnavailable.to_reading()`（lines 218-223），不查缓存、不调 source。测试 `test_thermometer_service_rejects_unsupported_batch_item_before_fresh_cache` 验证即使存在伪造缓存文件，unsupported code 仍返回 unavailable。

### P19-S3 non-regression

- **Exact 000300/000905 analyze 行为不变**：`classify_thermometer_code("000300")` 仍返回 `"index"`，`is_supported_index_code("000300")` 仍为 True。Analyze 路径的 valuation state resolution 未修改。
- **User explicit valuation state priority 未触碰**：CLI `--valuation-state` 仍然优先于自动温度计估值，逻辑未变。
- **Docs 无 all-A analyze claim**：README 明确"不把全 A 自动套用于主动基金或复合基准"。Fund README 保持"只对 index_fund / enhanced_index 且业绩基准 exact identity 映射到沪深300或中证500的基金调用自建温度计"。

### Tests/docs coverage

- **Source**: 37 tests 覆盖全 A PE/PB 合并、schema drift fail-closed、日期严格性、bool/NaN/Infinity 拒绝、空值/非正数丢弃、重复日期冲突/幂等折叠、重试瞬态失败、复合 source 分派、中文日期 fixture 防误用。
- **Cache**: 10 tests 覆盖 market/index namespace 分离、fresh/stale/corrupt/unsupported code 路径。
- **Service**: 23 tests 覆盖默认 all-A 路由、显式 wind_all_a 路由、指数路由、批量规范化/去重/全 A 混合批量、unsupported item-level unavailable、stale cache fallback（指数+全 A）、unavailable（指数+全 A）、cache save 失败不掩盖数据、计算契约错误传播、互斥字段、malformed 请求。
- **CLI**: 38 tests 覆盖默认全 A plain/JSON、显式 wind_all_a JSON、全 A unavailable JSON、指数 plain/JSON、批量 JSON/plain、全 A 混合批量 JSON、partial unavailable batch、help 文案、malformed input exit 2、Service 错误非零退出。
- **Combo**: 108 passed（source+cache+service+CLI），analyze regression 20 passed。
- **README 三文档同步**：root README / fund README / tests README 均更新至当前行为，无过度承诺。

## Open Questions

- 无。

## Residual Risk

- **Retry budget**: S5-1 controller 已标注 `ALL_A_FETCH_MAX_ATTEMPTS = 2`（1 次重试）低于 plan 建议的 3，留作 future production hardening。当前在 transient failure 场景下有 stale cache 兜底，风险可控。
- **Service 默认构造依赖 AkshareThermometerSource**: S5-2 controller 已接受为 non-blocking（factory abstraction premature）。Service 内部通过 `_IndexThermometerSource` protocol 消费，测试全部通过 fake 注入。未来扩展 source 类型时可抽取 factory。
- **Legacy ThermometerSnapshot CLI branch**: S5-3 controller 已标注为 transitional，默认路径不再经过。清理 deferred to separate gate。不影响 correctness。
- **Batch 请求串行执行**: `ThermometerService._load_index_batch` 串行 await 各 reading。当前 batch 规模小（2-3 项），无性能问题。大批量扩展时可改为 gather。

以上 residual 均不阻塞 ready-to-open-draft-PR。

## Verdict

**PASS**
