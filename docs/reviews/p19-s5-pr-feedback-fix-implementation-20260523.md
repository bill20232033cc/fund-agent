# P19-S5 PR 13 Feedback Fix Implementation

## Scope

- 当前任务只修复 PR 13 人工测试发现的温度计 blocking regression。
- 修改范围限定在 Fund Capability 数据源、对应测试和必要 README 同步。
- 未启动完整 Gateflow workflow，未 commit，未 push，未修改 GitHub PR 状态。

## Root Cause

- 指数路径 `AkshareIndexThermometerSource.load_index_history()` 使用 `asyncio.gather(asyncio.to_thread(...), asyncio.to_thread(...))` 并发读取 PE/PB。
- 全 A 路径 `AkshareAllAMarketThermometerSource.load_index_history()` 同样并发读取 PE/PB。
- 真实 akshare/Legulegu 调用链会进入 `py_mini_racer/libmini_racer`，macOS 下该 native 初始化路径不是并发安全；native fatal 发生在 Python 异常边界外，无法通过 `except Exception` 转成 `ThermometerSourceError`。
- 全 A source 对同一来源响应内同日期不同 `middlePETTM` 正数值直接 fail-closed，导致真实数据中重复修正行触发 `全 A 估值数据重复日期冲突：2019-05-09 / middlePETTM`，默认全 A 查询不可用。

## Changed Files

- `fund_agent/fund/data/thermometer_source.py`
- `tests/fund/data/test_thermometer_source.py`
- `fund_agent/fund/README.md`
- `tests/README.md`
- `docs/reviews/p19-s5-pr-feedback-fix-implementation-20260523.md`

## Fix Details

- 指数 PE/PB 抓取改为 PE 后 PB 顺序执行，仍通过 `asyncio.to_thread()` 避免阻塞 event loop，但不再并发进入 akshare native 依赖。
- 全 A PE/PB 抓取同样改为 PE 后 PB 顺序执行。
- 全 A 同源响应内同日期多条正数记录改为按输入顺序保留最后一条，这是对同一来源重复修正行的 deterministic collapse。
- 重复日期折叠不跨来源推断、不做插补、不放宽 schema 校验；缺字段、非数值、bool、NaN/Infinity、无有效正数记录和无有效共同日期仍 fail-closed。
- Source 层仍只负责抓取和规整 PE/PB 历史，不计算温度，不处理 CLI 输出。
- README 同步记录当前 PE/PB 顺序抓取和全 A 同源重复修正行折叠策略。
- DS review 后补充了不依赖真实线程调度窗口的顺序性回归测试：替换 `asyncio.to_thread` 为同步可观察 awaitable，PE fetcher 主动失败，并断言 PB fetcher 在 PE 完成前没有被调度或调用。

## Validation

- `pytest tests/fund/data/test_thermometer_source.py -q`
  - 40 passed
- `pytest tests/fund/data/test_thermometer_source.py tests/fund/data/test_thermometer_cache.py tests/services/test_thermometer_service.py tests/ui/test_cli.py -q`
  - 111 passed
- `ruff check fund_agent/fund/data/thermometer_source.py tests/fund/data/test_thermometer_source.py tests/services/test_thermometer_service.py tests/ui/test_cli.py`
  - All checks passed
- `fund-analysis thermometer --json`
  - 退出码 0，`unavailable=false`，`index_code=wind_all_a`，`data_date=2026-05-22`
- `fund-analysis thermometer --index 000300 --json`
  - 退出码 0，`unavailable=false`，`index_code=000300`，`data_date=2026-05-22`
- `fund-analysis thermometer --index wind_all_a,000300,000905 --json`
  - 退出码 0，`unavailable=false`，`partial_unavailable=false`，3 个 reading 均可用

## Residual Risks

- 真实 smoke 依赖 akshare/Legulegu 网络和上游数据可用性，不应放入默认 CI；默认测试继续使用 fake fetcher。
- 本次顺序化修复的是 PE/PB 同一 source 内部并发进入 native 依赖的问题；回归测试已同时覆盖线程重叠检测和不依赖 executor 调度的 PB 未提前调度边界。若后续其他功能新增并发 akshare 调用，需要单独审查。
- 批量 Service 当前按请求顺序逐个读取 reading，本次未修改 Service 编排。

## Stop Status

- Implementation/fix 已完成。
- 指定验证和用户复现路径均通过。
- 未发现剩余 blocker。
