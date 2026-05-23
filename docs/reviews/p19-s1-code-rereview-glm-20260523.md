# P19-S1 Code Re-review GLM（2026-05-23）

## Verdict

`BLOCKED`

当前 `HEAD=9ec6fd4` 相对上一版 P19-S1 implementation（`b3b2bd9`）已修复大部分 accepted findings，但日期字段 schema drift 的 fail-closed 修复不完整。该问题直接落在本次 re-review 指定的 accepted finding 3 上，因此不建议进入 P19-S1 acceptance judgment。

## Scope

本次只复审 P19-S1 沪深300指数温度计 MVP 修复：

- `fund-analysis thermometer --index 000300` 走自建指数 PE/PB 温度计。
- no-index 路径继续旧公开页 `FundThermometerAdapter`。
- 不接入 `fund-analysis analyze`。
- 不实现全 A 市场温度计或 PB-only 全 A 温度计。

对齐文档：

- `docs/design.md` v2.2：P19-S1/S2 只产出读数和估值状态候选，P19-S3 前不得自动写入 `analyze`。
- `docs/implementation-control.md`：当前 gate 为 `P19-S1 code re-review`；P19-S1 scope 为沪深300指数温度计 MVP，全 A 延后到 P19-S5。
- `docs/reviews/p19-s1-code-review-controller-judgment-20260523.md`：accepted findings 包括样本不足 fail-closed、cache save 失败语义、日期 schema drift fail-closed、Service 失败域拆分。

## Findings

### Blocking: 严格 ISO 字符串校验仍会接受带后缀的日期字符串

证据：

- `fund_agent/fund/data/thermometer_source.py:219` 把非 `date/datetime` 值转成字符串。
- `fund_agent/fund/data/thermometer_source.py:222` 使用 `candidate = text[:10]`。
- `fund_agent/fund/data/thermometer_source.py:223` 只对截断后的 `candidate` 做 `YYYY-MM-DD` 正则校验。
- `fund_agent/fund/data/thermometer_source.py:225` 只解析截断后的 `candidate`。

这意味着 `"2026-05-22T00:00:00"`、`"2026-05-22 00:00:00"`、`"2026-05-22abc"` 都会被截断为 `"2026-05-22"` 并通过校验。用户本次 re-review 明确要求“只接受 date/datetime 或严格 ISO YYYY-MM-DD 字符串”，controller judgment 也把“Date schema drift is not fail-closed”列为 accepted finding。当前实现仍允许字符串字段形态漂移后静默通过，和 accepted finding 的目标不一致。

影响：

- 外部 akshare 字段若从纯日期字符串漂移为带时间、带时区或带后缀的字符串，系统会把漂移后的协议形态当作正常数据接受。
- 这会削弱 P19 对外部协议边界的 fail-closed 语义，后续字段语义变化可能被缓存并进入温度计算。

建议修复：

- 对字符串本体做完整匹配，而不是先截断再匹配，例如 `if not ISO_DATE_PATTERN.fullmatch(text): raise ThermometerSourceError(...)`。
- 保留 `date/datetime` 对象路径；只有对象类型允许通过 `.isoformat()` 转为日期。
- 增加回归测试覆盖 `"2026-05-22T00:00:00"`、`"2026-05-22 00:00:00"`、`"2026-05-22abc"` 必须抛出 `ThermometerSourceError`。

## Accepted Findings Re-check

- 历史样本不足 fail-closed：已修复。`fund_agent/fund/analysis/thermometer_calculator.py:18` 定义 `MIN_HISTORY_POINTS = 30`，`calculate_thermometer_reading()` 在 `:45` 对少于 30 个共同日期直接抛出 `ThermometerCalculationError`，测试覆盖空历史和 1 点历史。
- cache save 失败不掩盖 fresh source：已修复。`fund_agent/services/thermometer_service.py:189` 先取得 fresh history；`:204-208` 仅对 `cache.save()` 的 `OSError` 降级为内存 history 后继续计算，测试 `test_thermometer_service_uses_fresh_history_when_cache_save_fails` 覆盖该路径。
- 日期字段 schema drift fail-closed：未完全修复，见 blocking finding。
- Service 失败域拆分：已修复。`fund_agent/services/thermometer_service.py:191` 只捕获 `ThermometerSourceError` 并在该路径读取 stale cache；计算错误在 `:183-187` 和 `:208` 直接传播，测试 `test_thermometer_service_propagates_calculation_contract_error` 覆盖。

## Scope Regression Check

- 未发现 `fund-analysis analyze` 自动调用温度计。`fund_agent/ui/cli.py:197-207` 仍只使用显式 `valuation_state` 构造 `FundAnalysisRequest`。
- no-index thermometer 路径仍走公开页 adapter。`fund_agent/services/thermometer_service.py:156-160` 仅当 `index_code is not None` 才进入自建指数路径，否则调用旧 adapter。
- P19-S1 指数源仍只支持 `000300`。`fund_agent/fund/data/thermometer_source.py:19` 的 `SUPPORTED_INDEX_SYMBOLS` 只有 `000300`。
- 未发现全 A 市场温度计或 PB-only 全 A 温度计实现。

## Residual Risks

- 未执行 live akshare smoke；当前结论仅基于静态走读和 deterministic tests。
- `MIN_HISTORY_POINTS = 30` 是当前防御性下限，能阻断明显不足样本，但不等于完整的两轮牛熊窗口验证；更长窗口校准仍属于后续 P19-S1/S2 数据质量残余。
- stale cache fallback 仍会在 source failure 时复用 7 天内缓存；这是当前设计允许的降级语义，但后续应继续补齐 source failure taxonomy 和可观测性。

## Validation Notes

已运行：

```text
.venv/bin/python -m pytest tests/fund/analysis/test_thermometer_calculator.py tests/fund/data/test_thermometer_source.py tests/fund/data/test_thermometer_cache.py tests/services/test_thermometer_service.py tests/ui/test_cli.py tests/fund/data/test_thermometer.py -q
54 passed in 0.50s

.venv/bin/python -m ruff check fund_agent tests
All checks passed
```

测试通过不覆盖 blocking finding 中的带后缀日期字符串反例。
