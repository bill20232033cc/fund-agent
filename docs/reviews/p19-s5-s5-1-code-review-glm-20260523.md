# Code Review — P19-S5 S5-1 Capability Source Contract

## Scope

- Mode: current changes
- Branch: `phase/p19-s5-all-a-pe-source-gate`
- Base: `main`
- Output file: `docs/reviews/p19-s5-s5-1-code-review-glm-20260523.md`
- Included scope:
  - `fund_agent/fund/data/thermometer_source.py`（+358 行，含新增 all-A source、共享分类器、复合分派、严格解析、有界重试）
  - `tests/fund/data/test_thermometer_source.py`（+488 行，22 个新测试覆盖全 A 合并、中文日期 fail-closed、字段选择、重复冲突、严格日期、非法数值、空值丢弃、重试瞬态失败、复合分派）
  - `docs/reviews/p19-s5-s5-1-capability-source-implementation-20260523.md`（implementation report）
- Excluded scope:
  - `fund_agent/fund/data/thermometer_types.py`（无 diff，确认未修改）
  - `fund_agent/services/`、`fund_agent/ui/`、`fund_agent/fund/analysis/`、`fund_agent/fund/data/thermometer_cache.py`（无 diff，确认未修改）
  - `docs/design.md`、`docs/implementation-control.md`（design/control truth 未修改）
- Parallel review coverage: 无，单 reviewer 完整走读

## Findings

未发现实质性问题。

以下为已验证无问题的审查路径和结论。

### 审查路径 1：Scope 严格性

逐文件验证 git diff：

- `thermometer_types.py`：零 diff，确认未修改。`PePbHistory` 的 `index_code`/`index_name` 字段被 all-A source 直接复用（`index_code="wind_all_a"`、`index_name="万得全 A / 全 A 市场"`），无 schema break。
- Service/cache/CLI/analyze 目录：零 diff，确认未触及 S5-2/S5-3 scope。
- `docs/design.md`、`docs/implementation-control.md`：design truth 和 control truth 未修改。
- 实现报告确认除 `thermometer_source.py` 和 `test_thermometer_source.py` 外无代码修改。

结论：严格限定在 S5-1 Capability Source Contract scope 内。

### 审查路径 2：All-A Source Contract 对齐

逐项对照 accepted plan §7.3 和 design.md §11.4：

| 要求 | 实现 | 验证 |
|------|------|------|
| `ALL_A_MARKET_CODE = "wind_all_a"` | 第 21 行，常量定义正确 | ✓ |
| `ALL_A_DATE_COLUMN = "date"`（英文） | 第 23 行，非中文 `日期` | ✓ |
| `ALL_A_PE_COLUMN = "middlePETTM"` | 第 24 行，不是 `averagePETTM` / `middlePELYR` | ✓ |
| `ALL_A_PB_COLUMN = "middlePB"` | 第 25 行，不是 `equalWeightAveragePB` / `close` | ✓ |
| `ALL_A_SOURCE_NAME = "akshare_legulegu_all_a_pe_pb"` | 第 26 行 | ✓ |
| 中文 `日期` all-A fixture fail-closed | 测试 `test_akshare_all_a_source_fails_closed_on_chinese_date_fixture`（第 421 行）断言 `match="缺少字段"` | ✓ |
| 只使用 middlePETTM / middlePB | 测试 `test_akshare_all_a_source_uses_only_middle_columns`（第 443 行）fixture 含 `averagePETTM`/`close`/`quantile` 等无关字段，断言只取 middle 值 | ✓ |

结论：all-A source 严格使用 `date` + `middlePETTM` + `middlePB`，中文 `日期` fixture fail-closed。

### 审查路径 3：No-Arg All-A 与 Symbol-Based Index 分离

- `AkshareAllAMarketThermometerSource`（第 264 行）：`AllAFetcher = Callable[[], object]`，no-arg fetcher。`_fetch_pe_frame_once` 调用 `ak.stock_a_ttm_lyr()`，`_fetch_pb_frame_once` 调用 `ak.stock_a_all_pb()`。
- `AkshareIndexThermometerSource`（第 171 行）：`PeFetcher = Callable[[str], object]`，symbol-based fetcher。`_load_pe_frame` 调用 `ak.stock_index_pe_lg(symbol=symbol)`。
- 两个类完全独立，fetcher 签名不兼容，无法混用。

复合 source `AkshareThermometerSource`（第 137 行）通过 `classify_thermometer_code` 分派：
- `code_kind == "index"` → `index_source`（symbol-based）
- `code_kind == "market"` → `all_a_source`（no-arg）

测试 `test_akshare_thermometer_source_dispatches_index_and_all_a`（第 726 行）验证 000300 走 index、`wind_all_a` 走 market、`999999` 抛错。

结论：no-arg all-A source 与 symbol-based index source 完全分离，composite dispatch 安全。

### 审查路径 4：共享分类器防止 wind_all_a 伪装为六位指数

`classify_thermometer_code`（第 52 行）：
- `code in SUPPORTED_INDEX_SYMBOLS` → `"index"`（只有 `"000300"` 和 `"000905"`）
- `code == ALL_A_MARKET_CODE` → `"market"`（只有 `"wind_all_a"`）
- 其他 → `"unsupported"`

`is_supported_index_code`（第 36 行）改为委托：`return classify_thermometer_code(index_code) == "index"`。

原实现是 `return index_code in SUPPORTED_INDEX_SYMBOLS`，行为等价。`"wind_all_a" not in SUPPORTED_INDEX_SYMBOLS`，所以 `is_supported_index_code("wind_all_a")` 为 `False`。

测试断言（第 190-191 行）：
- `is_supported_index_code(ALL_A_MARKET_CODE) is False` ✓
- `is_supported_thermometer_code(ALL_A_MARKET_CODE) is True` ✓

结论：共享分类器确保 `wind_all_a` 不会被当作六位指数处理。

### 审查路径 5：严格解析

**日期**（`_normalize_date`，第 541 行）：
- `None` → raise "日期为空" ✓
- `datetime` → `.date().isoformat()` ✓
- `date` → `.isoformat()` ✓
- 字符串 → 正则 `^\d{4}-\d{2}-\d{2}$` + `strptime` 校验 ✓
- 不允许带时间、空格、斜杠、紧凑格式、非法日期 ✓

测试覆盖 6 种非严格日期（第 549-560 行），`2026-02-30` 被拒绝 ✓。

**Decimal**（`_to_optional_positive_decimal`，第 596 行）：
- `None` → return `None`（丢弃行）✓
- `bool` → raise "不能为布尔值" ✓
- `Decimal(str(value))` 解析失败 → raise "不是有效数值" ✓
- `NaN`/`Infinity` → `is_finite()` 返回 `False` → raise ✓
- `<= 0` → return `None`（丢弃行）✓
- 正数 → return `Decimal` ✓

测试覆盖 `True`、`"not-a-number"`、`"NaN"`、`"Infinity"`、`"-Infinity"` 五种非法值（第 582-590 行），全部断言 raise ✓。

测试覆盖 `None`、`"0"`、`"-1"` 三种丢弃值（第 614-633 行），断言空交集失败 ✓。

**重复日期**（`_strict_positive_records_by_date`，第 528-534 行）：
- 首次出现：`values[date_text] = value` ✓
- 相同值再次出现：`existing_value == value` → `continue`（幂等折叠）✓
- 不同值再次出现：raise "重复日期冲突" ✓

测试 `test_akshare_all_a_source_fails_on_conflicting_duplicate_date`（第 487 行）和 `test_akshare_all_a_source_collapses_identical_duplicate_date`（第 514 行）覆盖两个分支 ✓。

注意：`Decimal("18.50") == Decimal("18.5")` 在 Python Decimal 中为 `True`（数学值相等），因此不同表示的相同数值正确折叠。

**共同日期交集**（`_merge_all_a_pe_pb_rows`，第 400 行）：
- PE 和 PB 独立构建 map ✓
- `sorted(set(pe_rows) & set(pb_rows))` ✓
- 空交集 → raise "没有有效共同日期" ✓
- 不插补 ✓

测试 `test_akshare_all_a_source_merges_source_shaped_rows_on_common_dates`（第 380 行）验证 PE 有 05-20/21/22、PB 有 05-21/22/23，交集为 05-21/22 ✓。

测试 `test_akshare_all_a_source_drops_invalid_rows_without_imputation`（第 637 行）验证 PE 05-21 null、05-22 valid、05-23 negative，PB 三天全 valid，交集只有 05-22 ✓。

结论：严格解析覆盖所有计划要求。

### 审查路径 6：Retry / Unavailable

`_fetch_all_a_with_retry`（第 430 行）：
- `ALL_A_FETCH_MAX_ATTEMPTS = 2`（2 次尝试，1 次重试）
- 循环内 `try/except Exception` 捕获所有外部异常
- 重试耗尽后 `raise ThermometerSourceError(f"全 A 估值数据获取失败：{label}：{last_error}") from last_error`
- 保留异常链 ✓

测试 `test_akshare_all_a_source_retries_first_transient_failure_and_succeeds`（第 672 行）：
- PE fetcher `failures_before_success=1`：第 1 次失败，第 2 次成功
- 断言 `pe_fetcher.calls == 2`，结果正确 ✓

测试 `test_akshare_all_a_source_raises_after_repeated_transient_failures`（第 699 行）：
- PE fetcher `failures_before_success=2`：2 次全部失败
- 断言 raise `ThermometerSourceError`，`pe_fetcher.calls == 2` ✓

`asyncio.gather` 并发执行 PE/PB 抓取。PE 失败会取消 PB 协程（PB 线程不中断但结果被丢弃），不影响正确性。PE 成功而 PB 失败同理。

retry 只覆盖 source fetch 阶段，不对 schema drift 做重试。这是 fail-closed 设计：字段漂移不应被重试掩盖 ✓。

备注：plan 建议 `SOURCE_RETRY_ATTEMPTS = 3` 和 `SOURCE_RETRY_BACKOFF_SECONDS = 0.2`，实现使用 2 次尝试无 backoff。Plan 用语为 "suggested constants"，非硬性约束。当前重试预算足以应对单次瞬态失败，连续两次瞬态失败由 Service 层 stale cache/unavailable 兜底。

结论：retry/unavailable 行为正确。

### 审查路径 7：现有 Index Source 非回归

- `is_supported_index_code` 从 `return index_code in SUPPORTED_INDEX_SYMBOLS` 改为委托 `classify_thermometer_code`。行为等价：`classify_thermometer_code` 对 `"000300"` 和 `"000905"` 返回 `"index"`（因为它们在 `SUPPORTED_INDEX_SYMBOLS` 中），对 `"wind_all_a"` 返回 `"market"`。
- 现有 15 个 index source 测试（`test_akshare_index_source_*`）全部保留且通过 ✓
- `_records_by_date`、`_merge_pe_pb_rows`、`_normalize_date`、`_to_decimal` 函数无修改 ✓
- `_records_by_date` 的后写覆盖重复日期行为保留 ✓（plan 明确要求不改变）

结论：现有 000300/000905 index source 行为无回归。

### 审查路径 8：测试充分性

测试覆盖矩阵（全部使用 fake fetcher，不依赖 live network）：

| 风险面 | 测试 | 状态 |
|--------|------|------|
| 共享分类器区分 index/market/unsupported | `test_thermometer_code_classifier_distinguishes_index_market_and_unsupported` | ✓ |
| wind_all_a 不伪装为指数 | 同上（`is_supported_index_code(ALL_A_MARKET_CODE) is False`） | ✓ |
| 全 A 按共同日期合并 | `test_akshare_all_a_source_merges_source_shaped_rows_on_common_dates` | ✓ |
| 中文日期 fail-closed | `test_akshare_all_a_source_fails_closed_on_chinese_date_fixture` | ✓ |
| 只用 middlePETTM/middlePB | `test_akshare_all_a_source_uses_only_middle_columns` | ✓ |
| 重复日期冲突 fail-closed | `test_akshare_all_a_source_fails_on_conflicting_duplicate_date` | ✓ |
| 重复日期相同值折叠 | `test_akshare_all_a_source_collapses_identical_duplicate_date` | ✓ |
| 非严格 ISO 日期拒绝 | `test_akshare_all_a_source_rejects_non_strict_dates`（6 种变体） | ✓ |
| bool/NaN/Infinity/非数值拒绝 | `test_akshare_all_a_source_rejects_invalid_numeric_values`（5 种变体） | ✓ |
| null/非正数丢弃+空交集失败 | `test_akshare_all_a_source_drops_null_or_non_positive_until_empty_fails`（3 种变体） | ✓ |
| 无效行丢弃不插补 | `test_akshare_all_a_source_drops_invalid_rows_without_imputation` | ✓ |
| 瞬态失败重试成功 | `test_akshare_all_a_source_retries_first_transient_failure_and_succeeds` | ✓ |
| 连续瞬态失败抛错 | `test_akshare_all_a_source_raises_after_repeated_transient_failures` | ✓ |
| 复合分派正确路由 | `test_akshare_thermometer_source_dispatches_index_and_all_a` | ✓ |
| 现有 index source 保持 | 15 个 `test_akshare_index_source_*` 测试保留且通过 | ✓ |

37 tests passed，ruff check 通过，git diff --check 无输出。

## Open Questions

无。

## Residual Risk

- **重试预算低于建议值**：`ALL_A_FETCH_MAX_ATTEMPTS = 2`（plan 建议 3）无 backoff。连续两次瞬态失败会触发 source error，依赖 Service stale cache 兜底。当前设计可接受，但若 Legulegu 不稳定频率升高，可考虑提高到 3 次并加入 backoff。
- **指数 source NaN/Infinity 检查缺失**：`_to_decimal`（index source 使用）不检查 `Decimal.is_finite()`，与 all-A source 的 `_to_optional_positive_decimal` 不一致。这是 P19-S1/S2 pre-existing gap，S5-1 scope 内正确选择是不修改。后续可统一。
- **Live network 未验证**：测试全部使用 fake fetcher，akshare `stock_a_ttm_lyr()` / `stock_a_all_pb()` 的真实返回格式依赖 source feasibility 报告结论。若 akshare 升级后字段名变更，schema drift 检测会 fail-closed。
- **S5-2/S5-3 依赖**：Service/cache 默认路由、CLI 输出、README 同步未实现，属于后续 slice scope。当前 all-A source contract 已就绪供 S5-2 消费。

## Validation

```text
pytest tests/fund/data/test_thermometer_source.py -q
37 passed in 0.05s

ruff check fund_agent/fund/data/thermometer_source.py tests/fund/data/test_thermometer_source.py
All checks passed!

git diff main -- fund_agent/fund/data/thermometer_types.py fund_agent/services/ fund_agent/ui/ fund_agent/fund/analysis/ fund_agent/fund/data/thermometer_cache.py
(zero diff — scope confirmed)
```

## Conclusion

**pass**

实现严格限定在 S5-1 Capability Source Contract scope 内，未触及 Service/cache/CLI/analyze/docs truth。All-A source 正确使用 `date` + `middlePETTM` + `middlePB`，中文 `日期` fixture fail-closed。No-arg all-A source 与 symbol-based index source 完全分离，composite dispatch 安全。共享分类器确保 `wind_all_a` 不会伪装为六位指数。严格解析、重复日期检测、共同日期交集、有界重试全部正确。现有 000300/000905 index source 行为无回归。37 个测试全部通过，覆盖所有计划要求的 risk surface，不依赖 live network。
