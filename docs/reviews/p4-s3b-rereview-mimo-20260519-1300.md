# P4-S3b Targeted Re-Review

## Scope

- Mode: current changes (targeted re-review of accepted findings only)
- Branch: main (uncommitted workspace changes)
- Base: main
- Output file: `docs/reviews/p4-s3b-rereview-mimo-20260519-1300.md`
- Included scope: accepted-finding follow-up verification only — not a full P4 re-review
- Excluded scope: P4-S3a, P4-S1/S2, fee_schedule, investor_return, turnover_rate, holdings_snapshot
- Parallel review coverage: 无

## Re-Review Objectives

Controller 接受了 2 个中风险 finding 并要求修复：

1. **F1**: `performance.py` 净值表现表头匹配排除"标准差"列 + 列序变化回归测试
2. **F2**: `manager_ownership.py` 跨页持有人结构 fallback 比例值校验 + 相邻比例/非比例测试

同时确认：
- `share_change` 多份额列选择策略 deferred 是否合理
- `fee_schedule` 不以费用金额冒充费率是否合理

---

## F1 Follow-Up: `_find_header_index` 排除"标准差"

### 改动验证

**实现** (`performance.py:172-197`):

`_find_header_index` 新增 `excluded_keywords` 参数，签名从 `(headers, keywords)` 改为 `(headers, required_keywords, excluded_keywords=())`。匹配逻辑变为：

```python
if all(keyword in normalized_header for keyword in required_keywords) and not any(
    keyword in normalized_header for keyword in excluded_keywords
):
    return index
```

调用点 (`performance.py:265-266`):

```python
nav_index = _find_header_index(table.headers, ("净值增长率",), ("标准差",))
benchmark_index = _find_header_index(table.headers, ("业绩比较基准收益率",), ("标准差",))
```

排除条件正确施加于 `required_keywords` 命中后的同一 header 上，而非整表。当 header 同时包含"净值增长率"和"标准差"时会被跳过，只有纯增长率列才会命中。

**测试** (`test_performance.py:166-193`):

`test_extract_performance_ignores_standard_deviation_columns_when_order_changes` 构造了一个标准差列在增长率列之前的表头：

```
headers=("阶段", "份额净值增\n长率标准差②", "份额净值\n增长率①", "业绩比较基准收益率标准差④", "业绩比较\n基准收益\n率③")
```

断言仍正确抽到 `nav_growth_rate="17.32%"` 和 `benchmark_return_rate="14.45%"`。

### 结论

**F1 正确闭合。** 实现精确地在 header 匹配层增加排除条件，测试覆盖了列序反转的回归场景。排除逻辑无副作用：对不含"标准差"的标准表头，`excluded_keywords` 为空元组，`not any(...)` 恒为 `True`，行为不变。

---

## F2 Follow-Up: `_infer_adjacent_personal_ratio` 比例值校验

### 改动验证

**实现** (`manager_ownership.py:492-556`):

旧代码 `_infer_adjacent_personal_ratio` 直接 `return _cell_at(row, index + 2)`。新实现：

1. `_infer_adjacent_personal_ratio` (line 492-512) 找到 `institutional_value` 所在 cell index 后，调用 `_find_adjacent_ratio_value(row, (index + 1, index + 2))`。
2. `_find_adjacent_ratio_value` (line 515-533) 遍历候选下标，对每个 cell 调用 `_is_ratio_value(value)`，返回首个通过校验的值。
3. `_is_ratio_value` (line 536-556) 执行三重校验：
   - 不含逗号（排除千分位份额值如 `129,320,194.75`）
   - 匹配 `^-?\d+(?:\.\d+)?%?$` 模式
   - 解析为 Decimal 后在 `[0, 100]` 范围内

候选下标 `(index + 1, index + 2)` 的设计意图清晰：`+1` 适配"仅比例列"布局（机构比例 | 个人比例），`+2` 适配"份额+比例"标准布局（机构份额 | 机构比例 | 个人份额 | 个人比例）。优先取 `+1`，回退 `+2`。

**测试**:

- `test_extract_manager_ownership_reads_adjacent_ratio_without_share_column` (line 304-338): 表头 `("", "持有份额", "比例", "比例")`，即只有比例列无份额列。`+1` 命中"比例"列，`_is_ratio_value("13.54")` 通过校验，正确返回 `individual_holder="13.54"`。
- `test_extract_manager_ownership_does_not_return_non_ratio_adjacent_cell` (line 341-375): 表头 `("", "持有份额", "比例", "备注")`，`+1` 位置值为"未披露"，`_is_ratio_value("未披露")` 因不匹配数字模式返回 `False`；无更多候选，返回 `None`。断言 `individual_holder=None`。

### 结论

**F2 正确闭合。** 硬编码 `+2` 被替换为候选探测 + 比例值校验的组合。`_is_ratio_value` 的三重校验（无逗号、数字模式、0-100 范围）有效防止了把份额值或备注文本误当比例。两个测试分别覆盖了"仅比例列"和"非比例相邻列"两个关键场景。

---

## Residual Risk 确认

### share_change 多份额列选择策略 deferred — 合理

`holdings_share_change.py:325-328` 仍取首个非空非 `-` 值，不区分 A/C 份额级别。当前行为：

- 对 004393（A 类基金）正确，因 A 类数据始终存在
- C 份额基金代码场景会返回 A 类数据，但当前 golden set 和精选池不含纯 C 份额基金
- 后续引入份额级别选择策略需要从 fund_code 后缀或表头 A/C 标记推断，设计成本高于当前 slice 范围

**判定：deferred 合理。** 风险边界清晰，当前输入池不触发，后续 slice 有明确修复路径。

### fee_schedule 不以费用金额冒充费率 — 合理

004393 年报 §6 披露的是当期支付的管理费/托管费金额（如"当期支付管理费 1,234,567.89 元"），不是管理费率/托管费率。将金额作为费率返回会误导下游估值计算。

**判定：deferred 合理。** 保持 `missing` 比返回错误语义的值更安全。后续 slice 需要从 §6 或基金合同中寻找费率披露源。

---

## Commands Run

```bash
.venv/bin/pytest tests/fund/extractors/test_performance.py tests/fund/extractors/test_manager_ownership.py tests/fund/extractors/test_holdings_share_change.py -v
# 20 passed in 0.75s

.venv/bin/ruff check fund_agent/fund/extractors/performance.py fund_agent/fund/extractors/manager_ownership.py fund_agent/fund/extractors/holdings_share_change.py tests/fund/extractors/test_performance.py tests/fund/extractors/test_manager_ownership.py tests/fund/extractors/test_holdings_share_change.py
# All checks passed!
```

## Verdict

**PASS**

两个 accepted finding 均已正确闭合：

| Finding | 闭合状态 | 验证方式 |
|---|---|---|
| F1: 表头排除"标准差" | 已闭合 | `_find_header_index` 新增 `excluded_keywords` 参数；列序反转回归测试通过 |
| F2: 跨页 fallback 比例校验 | 已闭合 | `_is_ratio_value` 三重校验替换硬编码 `+2`；仅比例列 / 非比例列两个测试通过 |

两项 residual risk（share_change 多份额列、fee_schedule 费率缺失）deferred 判断合理，无新增 blocking finding。
