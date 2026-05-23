# P19-S1 自建沪深300指数温度计第二份独立 Code Review（GLM, 2026-05-23）

## Verdict

PASS_WITH_FINDINGS

没有 blocking finding。P19-S1 当前实现基本符合 corrected plan 的 MVP 边界：`--index 000300` 走自建温度计路径，no-index 保留旧公开页 adapter，未接入 `fund-analysis analyze`，README 也没有把全 A 或 analyze 自动集成误写成已实现。

## Findings

### MEDIUM - F1：Service 把数据源失败、缓存写入失败和计算失败混在同一个 `unavailable` 失败域

证据：

- `fund_agent/services/thermometer_service.py:186`-`202` 中，`load_index_history()`、`cache.save()` 和 `calculate_thermometer_reading()` 位于同一个 `try/except Exception`。
- 一旦 `cache.save(history)` 在 `fund_agent/services/thermometer_service.py:188` 因权限、磁盘、路径或序列化错误失败，即使 akshare source 已成功返回 fresh history，Service 也会进入 `except`，尝试 stale cache，若无 cache 则返回 `ThermometerUnavailable(...).to_reading()`。
- 同样，如果 fresh source 返回了空历史、非正 PE/PB 或其他计算契约错误，`calculate_thermometer_reading()` 在 `fund_agent/services/thermometer_service.py:189` 抛出的计算错误也会被包装成“自建温度计数据不可用”。
- 现有 Service 测试只覆盖了真实 source 抛错后 stale fallback / unavailable：`tests/services/test_thermometer_service.py:194`-`249`，没有覆盖 cache write failure 或 calculator failure。

影响：

- 用户可见 CLI contract 会变得不稳定：README 说“上游不可用会以 `unavailable: true` 表示；只有参数校验或运行异常才非零退出”（`README.md:172`），但当前 cache 写入这类运行异常会被静默降级为数据不可用。
- 如果存在 stale cache，schema/计算/cache 写入问题还可能被 stale reading 掩盖，导致排障时看起来是一次成功的缓存读数，而不是当前刷新路径已经坏掉。
- JSON 的 `unavailable_reason` 会把非数据源错误都归为“自建温度计数据不可用”，后续监控或调用方无法区分 source unavailable、cache persistence failure、calculator contract failure。

建议：

- 把异常域拆开：只对 `index_source.load_index_history()` 的 unavailable 类错误执行 fresh/stale cache fallback；`cache.save()` 和 calculator 契约错误应走明确策略。
- 对 cache 写入失败，二选一并写测试锁定：要么用 fresh history 继续计算并输出 `cached=false`，同时不声称已缓存；要么按运行异常让 CLI 非零退出。
- 对计算契约错误，建议 fail closed，不要回退到 stale cache，避免错误 fresh 数据被旧数据掩盖。

## Residual Risks

- Unsupported index 当前在 source 层有测试（`000905` 抛 `ThermometerSourceError`），但 Service/CLI 层没有直接锁定 `--index 000905` 的用户可见 contract；当前实现会返回 `unavailable` 而非 CLI 非零。
- Schema drift 当前只在 source 单测中 fail-closed；Service 层会把它与普通 source failure 合并处理，并可能使用 stale cache。
- Corrupt cache 当前覆盖到 cache.load 降级为 miss，但没有组合测试覆盖“损坏 cache + source failure”的 CLI/Service 输出。
- JSON 字段当前测试锁定了关键字段和值为字符串的 Decimal 序列化，但没有独立 schema fixture；后续 P19-S2 扩展批量 index 时需要冻结数组/对象结构。
- 未执行 live akshare smoke；本次 review 只验证 fixture 路径和静态实现。

## Validation Notes

已验证：

- P19-S1 exit criteria 覆盖面：types、calculator、source、cache、Service no-index legacy path、`--index 000300` CLI JSON/plain、旧公开页 adapter 回归测试均存在。
- README / Fund README / tests README 与当前实现口径基本一致；没有把全 A 温度计或 `fund-analysis analyze` 自动估值集成描述成已实现。
- `fund-analysis analyze` 入口只消费显式 `--valuation-state`，未发现 `ThermometerService` 被接入分析主链路。

本地命令：

```text
.venv/bin/python -m pytest tests/fund/analysis/test_thermometer_calculator.py tests/fund/data/test_thermometer_source.py tests/fund/data/test_thermometer_cache.py tests/services/test_thermometer_service.py tests/ui/test_cli.py tests/fund/data/test_thermometer.py -q
49 passed in 0.49s

.venv/bin/python -m ruff check fund_agent tests
All checks passed!
```
