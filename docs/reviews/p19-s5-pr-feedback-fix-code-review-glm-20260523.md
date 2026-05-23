# Code Review — P19-S5 PR 13 Feedback Fix

## Scope

- **Mode**: current changes（AgentGLM 独立交叉 review）
- **Branch**: `phase/p19-s5-all-a-pe-source-gate`
- **Base**: `main`
- **Output file**: `docs/reviews/p19-s5-pr-feedback-fix-code-review-glm-20260523.md`
- **Review date**: 2026-05-23 16:08 CST
- **AgentDS 是主 review，本任务是独立交叉 review**
- **Included scope**:
  - `fund_agent/fund/data/thermometer_source.py`（PE/PB 并发消除 + 全 A 同源重复日期折叠）
  - `tests/fund/data/test_thermometer_source.py`（并发检测 + 重复日期折叠测试）
  - `fund_agent/fund/README.md`（能力描述同步）
  - `tests/README.md`（测试覆盖描述同步）
- **Excluded scope**: 未变更的 Service 层、CLI 层、缓存层、其他 Capability 模块
- **Parallel review coverage**: 无，主 reviewer 直接走读全部 diff

## Reviewed Evidence

- `git diff --stat`: 4 files changed, 230 insertions, 21 deletions
- `git diff` 全量 diff，逐行走读
- `thermometer_source.py` 完整源码（619 行）
- `test_thermometer_source.py` 完整测试（969 行）
- `docs/reviews/p19-s5-pr-feedback-fix-implementation-20260523.md` 实现 doc
- Controller 已复验：111 passed、ruff passed、三项真实 CLI smoke passed

## Verdict

**未发现 correctness / stability / maintainability blocker。** 可以 ship。

## Findings

未发现实质性问题。逐项审查结论：

### 1. PE/PB 并发进入 akshare/mini_racer 已消除

- **指数路径**（`AkshareIndexThermometerSource.load_index_history`，行 200-204）：原 `asyncio.gather(asyncio.to_thread(pe), asyncio.to_thread(pb))` 已改为顺序 `await asyncio.to_thread(pe)` 然后 `await asyncio.to_thread(pb)`。`try/except` 仍包裹两条调用，任一失败统一转为 `ThermometerSourceError`。
- **全 A 路径**（`AkshareAllAMarketThermometerSource.load_index_history`，行 289-290）：同样改为顺序。此路径无外层 `try/except`，但重试逻辑在 `_fetch_all_a_with_retry` 内部，异常已被统一包裹为 `ThermometerSourceError`，与改动前一致。
- **并发消除机制**：`await` 语义保证第一条 `asyncio.to_thread` 完成后才发起第二条。不存在协程级并发调度。生产调用链中 `ThermometerService._load_index_batch`（`thermometer_service.py:190`）使用列表推导式 `[await ... for ...]` 串行执行，不存在多个 source 并发进入 mini_racer 的路径。
- **测试验证**：`_ConcurrentEntryGuard` 使用 `threading.Lock` + `time.sleep(0.02)` 构造检测窗口，能可靠发现 `asyncio.gather` 重入。`assert guard.events == ["pe:start", "pe:end", "pb:start", "pb:end"]` 验证严格 PE→PB 顺序。指数和全 A 各有独立测试。

### 2. 全 A 同源重复日期折叠符合设计边界

- **实现**（`_strict_positive_records_by_date`，行 529-530）：原逻辑检查 `existing_value != value` 并 raise，现改为直接 `values[date_text] = value`（last-write-wins）。
- **设计边界合规**：
  - 折叠仅在 `_strict_positive_records_by_date` 内部，每个表（PE/PB）独立处理，不跨来源。
  - 值仍经过 `_to_optional_positive_decimal` 的 bool/NaN/Infinity/非正数校验，schema 和数值 fail-closed 未放松。
  - 缺字段、无有效正数记录、无有效共同日期仍 fail-closed。
  - 不做任何插补。
- **root cause 合理性**：akshare/Legulegu 全 A 接口真实返回同日期不同 `middlePETTM` 修正行（如 2019-05-09），旧逻辑直接 fail-closed 导致整个全 A 查询不可用。last-write-wins 是对同一来源重复修正行的确定性折叠，语义上保留最后一次修正值。
- **测试覆盖**：
  - `test_akshare_all_a_source_fails_on_conflicting_duplicate_date`：PE 表同日期 18.5→18.6，验证保留 18.6。断言包含 date、pe、pb 三个维度。
  - `test_akshare_all_a_source_collapses_identical_duplicate_date`：PE 表 18.50→18.5（数值相同表示不同），验证幂等折叠。
  - 指数路径 `_records_by_date` 无重复日期处理逻辑（akshare 指数接口不返回重复行），本次未改动，正确。

### 3. 新增测试能有效防止回归

- **并发回归**：`_ConcurrentEntryGuard` 是线程级检测器，若任何人将顺序调用改回 `asyncio.gather`，两个 fetcher 会同时进入 `run()`，`_active_label` 非空触发 `AssertionError`。指数和全 A 各有独立 guard 测试，覆盖两条路径。
- **重复日期回归**：`test_akshare_all_a_source_fails_on_conflicting_duplicate_date` 从 expecting-error 改为 expecting-last-value，直接验证 last-write-wins 行为。若改回 fail-closed 逻辑，此测试会 fail。
- **未引入测试替身泄漏**：`_ConcurrentEntryGuard`、`_GuardedSymbolFetcher`、`_GuardedNoArgFetcher` 仅在测试文件内定义和使用，不影响生产代码。

### 4. README 同步准确

- `fund_agent/fund/README.md` 新增一行："指数和全 A 的 PE/PB 抓取按 PE 后 PB 顺序执行，避免并发进入 akshare/Legulegu native 依赖；全 A 同源响应内同日期多条正数记录按输入顺序保留最后一条，不跨来源插补或推断"。
  - 准确描述了两个修复。
  - 未夸大能力（未声称"并发安全"或"数据修正"）。
  - 明确了设计边界（"不跨来源插补或推断"）。
- `tests/README.md` 更新测试描述，增加了"指数与全 A PE/PB 顺序抓取"和"同日期重复修正行确定性折叠"，准确反映新增测试覆盖。

### 5. Docstring / Raises 更新一致

- `_strict_positive_records_by_date` Raises 从 "schema 缺失、值不可解析或重复日期冲突" 改为 "schema 缺失或值不可解析"，与实际行为一致。
- `_merge_all_a_pe_pb_rows` Raises 从 "表结构缺列、重复日期冲突或有效共同日期为空" 改为 "表结构缺列或有效共同日期为空"，与实际行为一致。
- 新增 `_strict_positive_records_by_date` docstring 段落解释 last-write-wins 策略和边界。

## Non-blocking Notes

- **延迟倍增**：顺序执行使 PE/PB 最小延迟从 `max(pe, pb)` 变为 `pe + pb`。当前单次 akshare 调用约 1-3 秒，顺序化后全 A 查询约 2-6 秒，仍在可接受范围。若后续需要优化，可在确认 mini_racer 并发安全后恢复并发，但需充分测试。
- **批量路径串行**：`ThermometerService._load_index_batch`（`thermometer_service.py:190`）对多个指数串行 await。本次未修改，正确。若后续 batch 场景延迟敏感，可考虑并行不同指数的查询（不同 source 实例不共享 mini_racer 状态）。

## Validation

- **Controller 已复验**：111 passed、ruff passed。
- **真实 CLI smoke**：`--index 000300`、`--index wind_all_a,000300,000905`、默认全 A 三项均退出码 0。
- **本次 review 基于代码证据走读**，未重新执行测试（避免卡审批）。

## Open Questions

- 无。

## Residual Risk

- **上游数据变化**：若 akshare/Legulegu 全 A 接口返回语义变化（如重复行不再是修正行而是不同指标），last-write-wins 可能丢失数据。当前基于已知 source 行为设计，符合 YAGNI。
- **其他并发 akshare 调用**：本次修复的是同一 source 内 PE/PB 并发。若后续其他功能新增并发 akshare 调用（不同 source 实例），需独立审查 mini_racer 并发安全性。

## Stop Status

- 未发现 blocker。
- Review 完成，改动可 ship。
