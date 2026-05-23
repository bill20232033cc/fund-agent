# Code Review

## Scope

- Mode: current changes
- Branch: `phase/p19-s5-all-a-pe-source-gate`
- Base: main
- Output file: `docs/reviews/p19-s5-s5-2-code-review-glm-20260523.md`
- Included scope: S5-2 uncommitted changes only — Service default normalization, cache key routing, request validation, and all-A failure degradation
- Excluded scope: S5-3 CLI/docs/analyze behavior changes, UI direct source logic, thermometer_source.py (S5-1 accepted)
- Parallel review coverage: 无

## Findings

未发现实质性问题。

逐条验证 review focus 覆盖如下。

### 默认请求必须 materialize wind_all_a 并走自建全 A pipeline

**结论：正确。**

`_normalize_request` 在 `index_code=None` 且 `index_codes=None` 时返回 `_NormalizedThermometerRequest(index_code=ALL_A_MARKET_CODE, index_codes=None)`（thermometer_service.py:304）。`run()` 收到 `normalized.index_code == "wind_all_a"` 后进入 `_load_index_reading`（thermometer_service.py:169），永远不会到达 `adapter.load_thermometer()` 路径。测试 `test_thermometer_service_defaults_to_all_a_source` 注入 `forbidden_factory` 验证公开页 adapter 不被调用。

### wind_all_a 加六位 ASCII 数字接受；其他非六位 token malformed；unsupported 六位 item-level unavailable

**结论：正确。**

`_normalize_index_codes`（thermometer_service.py:307-337）用 `text != ALL_A_MARKET_CODE and not _is_six_ascii_digits(text)` 做格式守卫。`_is_six_ascii_digits`（thermometer_service.py:340-353）只接受 ASCII `0-9`，拒绝全角数字。parametrize 测试覆盖 `abc`、`wind_all_a1`、`１２３４５６`、空串、空白。`999999` 等合法六位通过格式检查后由 `_load_index_reading` 的 `classify_thermometer_code == "unsupported"` 分支返回 item-level unavailable（thermometer_service.py:218-223）。

### Service/cache/source 共享 S5-1 Capability classifier；Service 不导入 akshare 或 source 字段名

**结论：正确。**

Service 导入列表（thermometer_service.py:26-31）：`ALL_A_MARKET_CODE`、`AkshareThermometerSource`、`ThermometerSourceError`、`classify_thermometer_code`、`thermometer_display_name`。无 akshare 导入，无 `ALL_A_PE_COLUMN`/`ALL_A_PB_COLUMN` 等字段名。Cache 使用同一 `classify_thermometer_code`（thermometer_cache.py:17,70,131）。Service `_load_index_reading`（thermometer_service.py:218）和 Cache `load`（thermometer_cache.py:70）均调用 `classify_thermometer_code`，无重复支持逻辑。

### Cache namespace：wind_all_a → market/，000300/000905 → index/；unsupported 缓存不能绕过

**结论：正确。**

`_path_for`（thermometer_cache.py:131-136）按 `classify_thermometer_code` 返回 `market/wind_all_a_history.json` 或 `index/{code}_history.json`，unsupported 抛 `ValueError`。`load` 入口（thermometer_cache.py:70-71）对 unsupported 直接返回 None，即使伪造缓存文件存在也不读取。`save` 通过 `_path_for` 对 unsupported 抛 ValueError。测试覆盖：market namespace 写入与读取、index namespace 保持、unsupported load miss、unsupported save rejection。

### Source failure with stale cache 返回 stale reading；无 cache 返回 unavailable all-A

**结论：正确。**

`_load_index_reading`（thermometer_service.py:237-254）：`except ThermometerSourceError` 后 `cache.load(index_code, allow_stale=True)` 找到 stale 则返回 `calculate_thermometer_reading(cached=True, stale=True)`；无 stale 则返回 `ThermometerUnavailable(index_code="wind_all_a", index_name=thermometer_display_name("wind_all_a"), ...).to_reading()`。`thermometer_display_name("wind_all_a")` 返回 "万得全 A / 全 A 市场"。测试覆盖两条路径：`test_thermometer_service_uses_stale_all_a_cache_when_source_fails` 和 `test_thermometer_service_returns_unavailable_without_all_a_cache`。

### 计算契约错误不落入 stale-cache fallback

**结论：正确。**

Stale cache 找到后直接调用 `calculate_thermometer_reading`（thermometer_service.py:240-243）。该函数在 `len(history.points) < MIN_HISTORY_POINTS` 时抛 `ThermometerCalculationError(ValueError)`（thermometer_calculator.py:45-48）。此异常不在 `_load_index_reading` 的 `except ThermometerSourceError` 捕获范围内，直接传播到调用方。测试 `test_thermometer_service_propagates_all_a_stale_cache_calculation_error` 写入样本不足的 stale wind_all_a 缓存，验证 ValueError 传播。

### P19-S3 analyze non-regression

**结论：无回归。**

`_normalize_request` 只在 `index_code=None` 且 `index_codes=None` 时默认到 `wind_all_a`。analyze 调用链显式传入 index_code，不触发默认路径。`pytest tests/services/test_fund_analysis_service.py -q` = 20 passed，确认无回归。

### Service 默认 source 改用 AkshareThermometerSource

**结论：正确。**

`ThermometerService.__init__`（thermometer_service.py:146）使用 `AkshareThermometerSource()`，这是 S5-1 提供的复合分发器，根据 `classify_thermometer_code` 路由到 index 或 all-A 子源。Service 层不知道分发细节。

## Open Questions

无。

## Residual Risk

- 公开页 adapter 路径通过 `run()` 已不可达（dead code），属于 S5-2 设计意图，待 S5-3 或后续 gate 清理。
- 批量请求 `_load_index_batch` 顺序执行而非并发，S5-2 scope 内可接受，未来可优化。
- 测试辅助函数 `_write_history_cache` 在两个测试文件中重复定义（签名略有不同），属于测试局部辅助，不影响正确性。

## Validation

Controller 已验证：

```text
pytest tests/services/test_thermometer_service.py tests/fund/data/test_thermometer_cache.py -q
33 passed

pytest tests/services/test_fund_analysis_service.py -q
20 passed

ruff check fund_agent/services/thermometer_service.py fund_agent/fund/data/thermometer_cache.py tests/services/test_thermometer_service.py tests/fund/data/test_thermometer_cache.py
All checks passed!

git diff --check
passed with no output
```

## Conclusion

**pass** — S5-2 实现在 scope 内完整且正确，无实质性问题。
