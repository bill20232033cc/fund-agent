# Code Review — P19-S5 S5-1 Capability Source Contract

## Scope

- Mode: current changes
- Branch: `phase/p19-s5-all-a-pe-source-gate`
- Base: `main` (verified via git diff against HEAD; changes are uncommitted workspace modifications)
- Output file: `docs/reviews/p19-s5-s5-1-code-review-ds-20260523.md`
- Included scope:
  - `fund_agent/fund/data/thermometer_source.py` (+356/-2)
  - `tests/fund/data/test_thermometer_source.py` (+488)
  - Implementation report: `docs/reviews/p19-s5-s5-1-capability-source-implementation-20260523.md`
- Excluded scope: Service/cache/CLI/analyze/docs truth — all verified untouched per S5-1 contract
- Reviewed against:
  - `AGENTS.md`
  - `docs/design.md` §11/§12
  - `docs/implementation-control.md` P19-S5 section
  - `docs/reviews/p19-s5-all-a-market-thermometer-implementation-plan-20260523.md` §10 Slice S5-1
  - `docs/reviews/p19-s5-implementation-plan-review-controller-acceptance-20260523.md`
- Parallel review coverage: 无

## Findings

### 1-未修复-低-retry 常数与 backoff 偏离 accepted plan 建议值

- **入口/函数**: `_fetch_all_a_with_retry` → `AkshareAllAMarketThermometerSource._load_pe_frame` / `_load_pb_frame`
- **文件(行号)**: `thermometer_source.py:31` (常量), `thermometer_source.py:430-450` (retry 循环体)
- **输入场景**: Legulegu SSL EOF 或其他瞬态网络异常连续发生
- **实际分支**: `ALL_A_FETCH_MAX_ATTEMPTS = 2`，循环体无 `asyncio.sleep` 回退
- **预期行为**: accepted plan §8 建议 `SOURCE_RETRY_ATTEMPTS = 3` 且 `SOURCE_RETRY_BACKOFF_SECONDS = 0.2`
- **实际行为**: 最多 2 次尝试（1 次初始 + 1 次重试），两次尝试之间无任何延迟
- **直接证据**:
  - plan §8: `SOURCE_RETRY_ATTEMPTS = 3`、`SOURCE_RETRY_BACKOFF_SECONDS = 0.2`（标注为 Suggested）
  - 代码 `thermometer_source.py:31`: `ALL_A_FETCH_MAX_ATTEMPTS = 2`
  - 代码 `thermometer_source.py:445`: `for _attempt in range(ALL_A_FETCH_MAX_ATTEMPTS):` 循环体内无 sleep
- **影响**: 连续 2 次瞬态失败（如 Legulegu 短暂限流或 SSL 重协商）会导致 source 层直接抛 `ThermometerSourceError`，无法利用第 3 次尝试窗口；缺少 backoff 意味着两次尝试几乎同时发出，对持续数百毫秒以上的瞬态故障无效。Service 层有 stale cache fallback 兜底，因此用户可见影响为可能更频繁触发 stale/unavailable，而非错误结果。
- **建议改法和验证点**: 将 `ALL_A_FETCH_MAX_ATTEMPTS` 改为 3，在每次重试前加 `time.sleep(0.2)`；或保持 2 但显式在 implementation report / control doc 中记录偏差理由。测试 `test_akshare_all_a_source_retries_first_transient_failure_and_succeeds` 使用 `failures_before_success=1` 在当前 2 次尝试下通过，改为 3 后仍通过；`test_akshare_all_a_source_raises_after_repeated_transient_failures` 使用 `failures_before_success=2` 验证重试耗尽，改为 3 后需将 `failures_before_success` 调整为 3。
- **修复风险（低）**: 仅改常量与加 sleep，不改变解析语义或调度逻辑。
- **严重程度（低）**: plan 标注为 Suggested 而非强制；Service 层 stale cache 提供兜底；当前测试覆盖了 1 次瞬态失败恢复路径。

## Open Questions

无。

## Residual Risk

- **retry 常数偏差**：见 F1。当前 `ALL_A_FETCH_MAX_ATTEMPTS=2` 且无 backoff 可能在 Legulegu 连续瞬态故障时过早耗尽重试，依赖 Service stale cache 兜底。建议在 S5-2 Service 集成测试中覆盖 source 连续失败 → stale cache → unavailable 的完整降级链路。
- **Legulegu all-A universe 定义**：akshare `stock_a_ttm_lyr()` 和 `stock_a_all_pb()` 返回的具体成分范围未经本切片独立验证。accepted source feasibility 已确认 4828 天共同日期覆盖，但成分股入选标准（是否包含 ST、新股、停牌等）是 akshare/Legulegu 实现细节。未来如有方法论审计需求，需补充成分覆盖验证。
- **Index source 重复日期静默覆盖**：`_records_by_date()` 对重复日期采用后写覆盖（last-write-wins），与全 A 的冲突检测语义不同。这是 plan 明确保留的现有行为，但若 akshare index PE/PB 接口未来返回重复日期且值不同，会静默使用后者。当前 fixtures 不包含 index source 重复日期场景，属于已知 gap（plan 已记录不在此 slice 修改）。
- **fetched_at=None**：两个 source 都返回 `fetched_at=None`，由 cache/service 层后续填充。这是 P19-S1/S2 的现有模式，本切片未改变。但若未来有代码在 source 返回后、cache 写入前消费 `fetched_at`，会得到 None。当前调用链无此风险。
- **Live network 未覆盖**：所有测试使用 fake fetchers。akshare `stock_a_ttm_lyr()` 和 `stock_a_all_pb()` 的真实返回结构仅通过 source feasibility 探针验证过一次。若 akshare 版本升级改变字段名或返回结构，需更新 contract 常量。这是外部数据源的固有风险，不属于本切片实现缺陷。

## Conclusion

**pass-with-findings** — 1 个低严重度 finding（retry 常数偏离 plan 建议值），无 correctness、stability 或 regression 问题。

逐项对照 review focus：

| Review Focus | Result |
|---|---|
| 严格限定 S5-1，未改 Service/cache/CLI/analyze/docs truth | 通过 — diff 仅触及 source 与 test 两个文件 |
| all-A source 使用 date + middlePETTM + middlePB，中文日期 fail-closed | 通过 — 常量定义、严格解析路径、测试 `test_akshare_all_a_source_fails_closed_on_chinese_date_fixture` 均验证 |
| no-arg all-A source 与 symbol-based index source 分离，composite dispatch 安全 | 通过 — `AkshareAllAMarketThermometerSource`（no-arg fetcher）与 `AkshareIndexThermometerSource`（symbol-based fetcher）完全独立；`AkshareThermometerSource` 通过共享 `classify_thermometer_code` 分派 |
| shared classifier 不会让 wind_all_a 伪装成六位指数 | 通过 — `classify_thermometer_code("wind_all_a")` → `"market"`，`is_supported_index_code("wind_all_a")` → `False`，`SUPPORTED_INDEX_SYMBOLS` 仅含 `000300`/`000905` |
| strict parsing、Decimal、NaN/Infinity、duplicate conflict、common-date intersection、retry/unavailable | 通过 — 所有路径均验证；retry 常数偏差见 F1（低） |
| 回归现有 000300/000905 index source 行为 | 通过 — `AkshareIndexThermometerSource` 及其辅助函数完全未修改；所有已有 index 测试保留并通过 |
| tests 覆盖风险 | 通过 — 20 个测试覆盖分类器契约、index source 回归、all-A 正序/异常/边界/重试/复合分派全路径；37 passed |

Implementation 质量高：数据契约精确、fail-closed 语义一致、分层干净、测试全面。F1 为 plan 建议值偏差，不影响合入 S5-1，建议在进入 S5-2 前统一确认 retry 参数或在 control doc 中记录偏差。
