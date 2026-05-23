# Code Review: P19-S5 PR 13 Feedback Fix

## Scope

- **Mode**: current changes (未提交 workspace diff)
- **Branch**: `phase/p19-s5-all-a-pe-source-gate`
- **Base**: `main` (implicit)
- **Output file**: `docs/reviews/p19-s5-pr-feedback-fix-code-review-ds-20260523.md`
- **Included scope**:
  - `fund_agent/fund/data/thermometer_source.py` — 消除 PE/PB 并发、全 A 重复日期折叠策略变更
  - `tests/fund/data/test_thermometer_source.py` — 新增并发检测测试、重复日期测试更新
  - `fund_agent/fund/README.md` — 行为描述同步
  - `tests/README.md` — 测试覆盖描述同步
- **Excluded scope**: Service 层、CLI、缓存、其他 Capability 模块（本次未修改）
- **Parallel review coverage**: 无（scope 紧凑，单 reviewer 可完整走读全部关键路径）

## Reviewed Evidence

- `git diff --stat`：4 files, +230/-21
- `git diff -- fund_agent/fund/data/thermometer_source.py`：完整 diff
- `git diff -- tests/fund/data/test_thermometer_source.py`：完整 diff
- `git diff -- fund_agent/fund/README.md tests/README.md`：完整 diff
- `docs/reviews/p19-s5-pr-feedback-fix-implementation-20260523.md`：implementation review doc（前 220 行）
- `fund_agent/fund/data/thermometer_source.py`：完整源文件（619 行）
- `tests/fund/data/test_thermometer_source.py`：完整测试文件（969 行）
- `AGENTS.md`：项目执行规则
- `pytest ... -q`：111 passed（Controller 复验，含后续确定性顺序调度测试）
- `ruff check ...`：All checks passed
- Controller 复验结果：真实 CLI 三项 smoke passed

## Verdict

**未发现 correctness / stability / maintainability blocker。** 改动精确、范围紧凑、测试充分。建议合并。

## Findings

### 1. 未修复-中-并发检测测试对线程池调度有时序依赖，但不足以构成回归盲区

- **入口/函数**: `test_akshare_index_source_fetches_pe_before_pb_without_concurrency`、`test_akshare_all_a_source_fetches_pe_before_pb_without_concurrency`
- **文件(行号)**: `tests/fund/data/test_thermometer_source.py:420–451`、`tests/fund/data/test_thermometer_source.py:727–758`
- **输入场景**: 正常 fake fetcher 注入，单次 `load_index_history` 调用。
- **实际分支**: `_ConcurrentEntryGuard.run()` 在 lock 内检查 `_active_label`，lock 外执行 `time.sleep(0.02)` 模拟工作区间，finally 中清除 `_active_label`。
- **预期行为**: 若生产代码恢复 `asyncio.gather`，两个 `to_thread` 任务近乎同时提交到线程池，第二个线程应在 lock 内看到 `_active_label` 非 None 而触发 `AssertionError`。
- **实际行为**: 在极端单线程 executor 或极高负载下，`asyncio.gather` 提交的两个 `to_thread` 可能被串行化执行，导致 `_active_label` 始终在第二个线程进入前被清除，`AssertionError` 不触发。
- **直接证据**: `_ConcurrentEntryGuard.run()` 行 209–220：检测窗口为 `time.sleep(0.02)` 区间。若线程池串行化两个任务，PE 的 sleep→finally→clear 会在 PB 进入 lock 之前完成，`_active_label` 已为 None（行 212 检查不触发）。
- **影响**: 测试在默认 `asyncio.to_thread` executor（多线程）下可靠检测并发回归；仅在刻意配置单线程 executor 时可能漏检。实际回归风险低，因为默认线程池线程数充足。
- **建议改法和验证点**: 可补充显式 `concurrent.futures.ThreadPoolExecutor(max_workers=1)` 场景下的测试变体，验证即使线程池串行化，事件顺序断言 `guard.events == ["pe:start", "pe:end", "pb:start", "pb:end"]` 仍能捕获 `asyncio.gather` 导致的乱序事件。当前实现已可接受。
- **修复风险（低）**:
- **严重程度（中）**: 非 correctness 问题，属测试覆盖边界；当前默认配置下该测试有效。

## Open Questions

- 无。

## Residual Risk

- 全 A `_strict_positive_records_by_date` 的 last-value-wins 策略依赖上游返回顺序（修正行在原始行之后）。若上游变更响应顺序（修正行在前），保留的将是原始值而非修正值。这是外部数据质量风险，非代码缺陷；当前策略已在 docstring 和 README 中显式声明。
- 本次只修复了 PE/PB 同一 source 内部的并发问题。若后续新增功能同时调用多个 `AkshareThermometerSource` 或混合调用 akshare 其他接口，需单独审查并发安全性。
- 批量 Service (`ThermometerService`) 当前按请求顺序逐个读取 reading，本次未修改 Service 编排。

## Non-blocking Notes

1. **延迟换稳定性是可接受的取舍**：PE/PB 顺序执行使单次 `load_index_history` 的 wall-clock 时间从 `max(PE, PB)` 变为 `PE + PB`。考虑到本次修复的 root cause 是 `libmini_racer` native fatal（macOS 下不可恢复，落在 Python 异常边界外），这个取舍合理。

2. **`_ConcurrentEntryGuard` 测试工具类设计合理**：三个新测试辅助类 (`_ConcurrentEntryGuard`、`_GuardedSymbolFetcher`、`_GuardedNoArgFetcher`) 通过 lock-protected 状态检查 + lock-external sleep 窗口实现了可靠的并发检测。关键设计点是 `_active_label` 在 sleep 期间保持设置（finally 才清除），使并发进入可被检测。这些类是测试专用，不进入生产路径。

3. **重复日期折叠不跨来源**：`_strict_positive_records_by_date` 只在单个 frame（PE 或 PB）内部折叠，PE 和 PB 的折叠相互独立。`_merge_all_a_pe_pb_rows` 再对 PE/PB 结果取共同日期交集。两层操作边界清晰，不引入跨来源推断。

4. **README 描述准确**：两处 README 修改均反映当前实现行为，没有夸大能力或承诺未来行为。Fund README 新增行明确说明了顺序执行的原因（避免 native 依赖并发）和折叠策略的边界（不跨来源插补或推断）。

## Validation

- `pytest tests/fund/data/test_thermometer_source.py tests/fund/data/test_thermometer_cache.py tests/services/test_thermometer_service.py tests/ui/test_cli.py -q` → **111 passed**
- `ruff check fund_agent/fund/data/thermometer_source.py tests/fund/data/test_thermometer_source.py tests/services/test_thermometer_service.py tests/ui/test_cli.py` → **All checks passed**
- Controller 复验（真实 CLI）：
  - `fund-analysis thermometer --json` → 退出码 0，`unavailable=false`
  - `fund-analysis thermometer --index 000300 --json` → 退出码 0，`unavailable=false`
  - `fund-analysis thermometer --index wind_all_a,000300,000905 --json` → 退出码 0，3 个 reading 均可用
- 代码走读确认：
  - `AkshareIndexThermometerSource.load_index_history()` 行 201–202：`await asyncio.to_thread(...)` 顺序执行，无并发
  - `AkshareAllAMarketThermometerSource.load_index_history()` 行 289–290：同上
  - `_strict_positive_records_by_date()` 行 529–530：`values[date_text] = value` 确定性 last-value-wins
  - 所有 fail-closed 路径保留：schema 缺失（行 508–509、521–522）、类型错误（行 512–514）、bool 拒绝（`_to_optional_positive_decimal` 行 608–609）、NaN/Infinity 拒绝（行 614–615）、空结果（行 532–533）

## Stop Status

- Review 完成，未发现 blocker。
- 建议合并。
