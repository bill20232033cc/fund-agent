# P19-S1 Code Review - Mimo - 2026-05-23

## Verdict

PASS_WITH_FINDINGS

没有发现 blocking finding。当前 HEAD 未把 P19-S1 自建沪深300指数温度计接入 `fund-analysis analyze`，也未自动写入 `valuation_state`；`fund-analysis thermometer --index 000300` 走新自建指数路径，未实现全 A 市场温度计或 PB-only 全 A 温度计。

## Findings

### Medium - 历史样本不足时会输出确定的高温/高估，而不是 fail-closed

- 文件/行号：`fund_agent/fund/data/thermometer_source.py:87-95`, `fund_agent/fund/analysis/thermometer_calculator.py:44-63`, `fund_agent/fund/analysis/thermometer_calculator.py:90-95`
- 直接证据：数据源只检查合并后的 `points` 是否为空；只要 PE/PB 有一个共同日期就返回 `PePbHistory`。计算器也只拒绝空序列，随后 `percentile_rank()` 用 `less_or_equal_count / len(values)` 计算分位数。
- 触发路径：如果 akshare/Legulegu 因接口异常、分页变化或局部返回只给出 1 个共同日期，`current.pe` 和 `current.pb` 都会在长度为 1 的历史序列中得到 `100.00` 分位，最终 `temperature=100.00`、`valuation_state_candidate="high"`，且 `unavailable=False`。
- 风险：这不是“历史分位数”意义上的有效温度计，会把数据覆盖不足误报为明确高估。`docs/design.md` v2.2 §11.1/§11.2 要求基于历史 PE/PB 序列和动态窗口，P19-S1 也要求先验证可取得历史长度；当前实现没有把覆盖不足作为不可用或 fail-closed 状态。
- 建议：在 Capability data 或 calculator 增加显式最小覆盖契约，例如最少样本数、最早日期、最新日期和 PE/PB 共同日期覆盖检查；不足时返回/抛出不可用，不生成温度和估值状态候选。

### Medium - 缓存写入失败会掩盖已经成功取得的新鲜数据

- 文件/行号：`fund_agent/services/thermometer_service.py:186-202`
- 直接证据：`try` 块同时包住 `load_index_history()`、`cache.save()` 和 `calculate_thermometer_reading()`。如果数据源成功返回 `history`，但 `cache.save(history)` 因目录权限、磁盘只读或写入失败抛出异常，代码会进入 `except`，尝试加载旧缓存；无旧缓存时返回 `ThermometerUnavailable`。
- 触发路径：`fund-analysis thermometer --index 000300 --cache-dir <不可写目录>` 在 akshare 数据已成功返回的情况下，仍可能输出 `unavailable=True` 或旧 stale cache，而不是基于新鲜 `history` 输出读数。
- 风险：P19-S1 计划要求“数据源失败时”才使用 cache fallback；缓存持久化失败不等于数据不可用。当前路径会把可用的新鲜读数降级为不可用/旧读数，造成用户可见状态与真实数据获取结果不一致。
- 建议：把 source fetch、cache write、calculation 的异常边界拆开。数据源成功后，即使缓存写入失败，也应优先用内存中的 `history` 计算并返回读数；缓存写入失败可作为非致命降级信息记录，不应触发 stale fallback。

### Medium - akshare 日期字段 schema drift 未严格 fail-closed

- 文件/行号：`fund_agent/fund/data/thermometer_source.py:158-159`, `fund_agent/fund/data/thermometer_source.py:197-217`, `fund_agent/fund/data/thermometer_types.py:20-30`
- 直接证据：`PePbPoint.date` 契约写明使用 ISO `YYYY-MM-DD` 字符串，但 `_normalize_date()` 对任何非空字符串只做 `text[:10]` 截断，不校验格式；随后 `_merge_pe_pb_rows()` 对字符串日期做字典交集和字典序排序。
- 触发路径：如果 akshare 日期从 `Timestamp`/`YYYY-MM-DD` 漂移为 `20260522`、`2026/05/22`、中文日期或其他可字符串化值，当前代码不会 fail-closed，而是把截断后的非 ISO 值写入 `PePbPoint`，并可能用错误排序选择 `history.points[-1]` 作为当前日期。
- 风险：schema drift 会被静默当作正常数据，可能导致读数日期、lookback 窗口和当前温度错误。用户重点要求审查 akshare source schema drift/fail-closed 行为；当前字段缺失会 fail-closed，但日期格式漂移不会。
- 建议：日期标准化应使用严格解析，只接受 `datetime/date` 或可解析为 ISO `YYYY-MM-DD` 的字符串；无法解析或格式非预期时抛出 `ThermometerSourceError`，由 Service 转为 unavailable/cache fallback。

## Residual Risks

- 本次只审查当前 HEAD 的 P19-S1 相关实现与测试，没有做 live akshare/Legulegu smoke；外部接口字段、可用性和历史覆盖仍需独立 smoke gate 验证。
- `ThermometerService` 当前直接编排 `ThermometerHistoryCache` 与 `calculate_thermometer_reading()`，没有发现实际 UI 绕过 Service 或 analysis IO 越界，但 Service 与 Capability cache/calculator 的耦合仍比 `docs/design.md` §11.5 的“Capability data 取数/缓存、Capability analysis 纯计算”边界更紧，后续扩展到批量指数时应警惕 Service 变成缓存细节聚合点。
- 未发现 P19-S1 代码把新自建温度计静默接入 `FundAnalysisService.analyze()`；当前 `fund_agent/ui/cli.py:93-96` 仍使用显式 `--valuation-state` 默认 `unavailable`，`fund_agent/ui/cli.py:197-207` 直接把该显式值放入 `FundAnalysisRequest`。
- 未发现全 A 市场温度计或 PB-only 全 A 温度计实现；`fund_agent/fund/data/thermometer_source.py:17-20` 仅支持 `000300`，且同时要求 PE 列 `滚动市盈率中位数` 与 PB 列 `市净率中位数`。

## Validation Notes

- 阅读设计真源：`docs/design.md` v2.2 §1.3、§6.3、§10、§11；重点核对 P19-S1/S2 不接入 `analyze`、P19-S3 才允许自动 `valuation_state`、P19-S1 只做沪深300指数温度计。
- 阅读计划与实现记录：`docs/reviews/p19-s1-corrected-index-thermometer-plan-20260522.md`、`docs/reviews/p19-s1-index-thermometer-implementation-20260523.md`。
- 走读入口链路：`fund_agent/ui/cli.py:245-292` → `fund_agent/services/thermometer_service.py:139-202` → `fund_agent/fund/data/thermometer_source.py` / `thermometer_cache.py` → `fund_agent/fund/analysis/thermometer_calculator.py`。
- 验证 `analyze` 未自动接入：`fund_agent/ui/cli.py:57-220`、`fund_agent/services/fund_analysis_service.py` 中只消费请求内显式 `valuation_state`，没有调用 P19-S1 source/cache/calculator。
- 运行相关测试：

```bash
.venv/bin/python -m pytest tests/fund/analysis/test_thermometer_calculator.py tests/fund/data/test_thermometer_source.py tests/fund/data/test_thermometer_cache.py tests/services/test_thermometer_service.py tests/ui/test_cli.py -q
```

结果：`36 passed in 0.48s`。
