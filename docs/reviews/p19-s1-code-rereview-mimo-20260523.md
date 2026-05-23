# P19-S1 Code Re-review - MiMo（2026-05-23）

## Verdict

`BLOCKED`

当前 `9ec6fd4` 已正确修复样本不足 fail-closed、cache save 失败后继续使用 fresh in-memory history、以及 Service 失败域拆分的大部分问题；但 accepted finding 3 没有被完整修复：字符串日期仍会通过截取前 10 位接受带尾随内容的非严格 ISO 字符串。这直接违反本轮复审要求“只接受 date/datetime 或严格 ISO YYYY-MM-DD 字符串”。

## Findings

### Blocking - 日期字符串 schema drift 仍未 fail-closed

- 文件：`fund_agent/fund/data/thermometer_source.py:219`
- 证据链：`_records_by_date()` 在 `fund_agent/fund/data/thermometer_source.py:193` 把 akshare 记录的 `日期` 字段传给 `_normalize_date()`；`_normalize_date()` 在 `fund_agent/fund/data/thermometer_source.py:219-224` 先执行 `text = str(value).strip()`，随后 `candidate = text[:10]`，再只对 `candidate` 做 `YYYY-MM-DD` 正则匹配。这意味着 `"2026-05-22T00:00:00"`、`"2026-05-22 00:00:00"`、`"2026-05-22abc"` 都会被截成 `"2026-05-22"` 并通过校验。
- 为什么是问题：本轮 accepted finding 明确要求字符串只接受严格 ISO `YYYY-MM-DD`。当前实现仍然允许外部 schema 从纯日期漂移成 timestamp 或附加文本而静默进入计算，破坏 P19-S1 对 akshare schema drift 的 fail-closed 语义。
- 影响：数据源字段形态变更时，系统可能继续输出确定温度读数，而不是把 drift 暴露为 `ThermometerSourceError`，后续缓存还可能保存已被静默规整的数据。
- 建议修复：对字符串使用完整 `text` 做 `ISO_DATE_PATTERN.fullmatch(text)` 和 `datetime.strptime(text, "%Y-%m-%d")`，不要先截取；补充测试覆盖 timestamp 字符串、带空格时间、带尾随字符三类反例。

## Accepted Finding Verification

| Finding | Re-review result | Evidence |
|---|---|---|
| 历史样本不足必须 fail-closed | Fixed | `calculate_thermometer_reading()` 在 `fund_agent/fund/analysis/thermometer_calculator.py:45-48` 对少于 30 个共同日期直接抛 `ThermometerCalculationError`；`tests/services/test_thermometer_service.py:297-316` 覆盖计算契约错误传播。 |
| cache save 失败不能掩盖 fresh source 数据 | Fixed | `ThermometerService._load_index_reading()` 在 `fund_agent/services/thermometer_service.py:204-208` 只捕获 `OSError` 并使用内存 `history` 继续计算；`tests/services/test_thermometer_service.py:272-294` 覆盖该路径。 |
| akshare 日期字段 schema drift 必须 fail-closed | Not fully fixed | 见 blocking finding；当前测试 `tests/fund/data/test_thermometer_source.py:131-150` 只覆盖 `20260522`，未覆盖 `YYYY-MM-DD` 后带尾随内容的反例。 |
| source/cache/calculation 失败域必须拆开 | Fixed | `ThermometerService._load_index_reading()` 在 `fund_agent/services/thermometer_service.py:189-203` 只针对 `ThermometerSourceError` 使用 stale fallback；计算发生在 source/cache try 之外，`tests/services/test_thermometer_service.py:297-316` 覆盖计算错误不被 stale cache 掩盖。 |

## Residual Risks

- 未执行 live akshare smoke；这不阻塞本轮 deterministic re-review，但仍应保留为单独 smoke gate。
- stale cache 的读取会吞掉损坏缓存异常并返回 `None`，当前符合既有缓存契约；若后续要审计 cache corruption，需要另设可观测性 gate。
- `cache.save()` 只将 `OSError` 视为非致命写失败；目前能覆盖真实文件系统写失败。非 I/O 的序列化或类型错误仍会暴露为异常，符合 fail-closed 倾向。

## Validation Notes

已在本地执行：

```text
.venv/bin/python -m pytest tests/fund/analysis/test_thermometer_calculator.py tests/fund/data/test_thermometer_source.py tests/fund/data/test_thermometer_cache.py tests/services/test_thermometer_service.py tests/ui/test_cli.py tests/fund/data/test_thermometer.py -q
54 passed in 0.49s

.venv/bin/python -m ruff check fund_agent tests
All checks passed!
```

复审范围限定在 `9ec6fd4` 相对上一版 P19-S1 implementation `b3b2bd9` 的修复；未修改生产代码或测试。
