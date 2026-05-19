# P4-S3b Targeted Re-Review

> **日期**: 2026-05-19
> **审查者**: GLM
> **模式**: targeted re-review of accepted-finding follow-up
> **结论**: **PASS**

---

## 1. 审查范围

仅审查 P4-S3b accepted-finding 是否正确闭合，不重开 P4 全量 review。

审查对象：

1. **Finding 1 (中)**: `performance.py` 净值表现表头匹配排除"标准差"列
2. **Finding 2 (中)**: `manager_ownership.py` 跨页持有人结构 fallback 不硬编码 `+2`、不把份额/备注当比例
3. **Residual risk 确认**: `share_change` 多份额列选择策略 deferred 是否合理
4. **Residual risk 确认**: `fee_schedule` 不以费用金额冒充费率是否合理

---

## 2. Finding 1 闭合验证：performance.py 表头排除"标准差"

### 2.1 修复方案

`performance.py:172-197` — `_find_header_index` 签名扩展为 `(headers, required_keywords, excluded_keywords=())`。命中条件改为 `all(required in header) and not any(excluded in header)`。

调用点 `performance.py:265-266`：

```python
nav_index = _find_header_index(table.headers, ("净值增长率",), ("标准差",))
benchmark_index = _find_header_index(table.headers, ("业绩比较基准收益率",), ("标准差",))
```

### 2.2 正确性

- "份额净值增长率①" 满足 `required=("净值增长率")` 且不含 `"标准差"` → 命中。
- "份额净值增长率标准差②" 满足 `required` 但含 `"标准差"` → 排除。
- "业绩比较基准收益率标准差④" 同理被排除。
- 列序无关：遍历全部 headers 逐一检查，不依赖特定顺序。

### 2.3 回归测试

- `test_extract_performance_outputs_nav_and_benchmark_from_annual_table` — 标准列序（标准差在增长率后面），断言 `nav=17.32%`、`benchmark=14.45%`。
- `test_extract_performance_ignores_standard_deviation_columns_when_order_changes` — 对抗性测试：标准差列排在增长率列之前，断言仍正确提取增长率而非标准差。

### 2.4 判定

**正确闭合**。必含/排除关键词机制解决了子串误匹配问题；对抗性列序测试提供了回归保护。

---

## 3. Finding 2 闭合验证：manager_ownership.py 跨页 fallback

### 3.1 修复方案

原 `_infer_adjacent_personal_ratio` 直接返回 `_cell_at(row, index + 2)`。修复拆为两层：

1. **候选列探测** (`manager_ownership.py:515-533` `_find_adjacent_ratio_value`): 探测 `(index + 1, index + 2)` 两个候选位置，而非硬编码 `+2`。`+1` 适配仅比例列紧凑布局，`+2` 适配"个人份额 + 个人比例"标准布局。
2. **比例值校验** (`manager_ownership.py:536-556` `_is_ratio_value`): 对候选值做三重校验：
   - 含逗号（千分位）→ 拒绝（排除份额值如 `"20,245,545.25"`）
   - 不匹配 `^-?\d+(\.\d+)?%?$` → 拒绝（排除文本如 `"未披露"`）
   - 数值不在 `[0, 100]` 范围 → 拒绝（排除异常值）

### 3.2 正确性

- **紧凑布局**（"比例", "比例" 相邻）：`index + 1` 处 `"13.54"` 通过比例校验 → 命中。
- **标准布局**（"持有份额", "比例" 相邻）：`index + 1` 处 `"20,245,545.25"` 含逗号被拒绝，`index + 2` 处 `"13.54"` 通过 → 命中。
- **备注列**：`index + 1` 处 `"未披露"` 不匹配数字模式，`index + 2` 越界或也不匹配 → 返回 `None`。
- 无有效候选时返回 `None`，不静默返回错误值。

### 3.3 回归测试

- `test_extract_manager_ownership_reads_adjacent_ratio_without_share_column` — 紧凑布局（只有比例列），断言 `individual_holder="13.54"`。
- `test_extract_manager_ownership_does_not_return_non_ratio_adjacent_cell` — 备注列替代个人比例列，断言 `individual_holder=None`（不被 "未披露" 污染）。
- `test_extract_manager_ownership_outputs_alignment_and_holder_structure_from_tables` — 标准 004393 跨页表形态，含完整表头组、份额列和比例列，断言正确提取机构/个人比例。

### 3.4 判定

**正确闭合**。硬编码偏移消除，份额值/文本备注过滤到位，三个测试分别覆盖 +1 路径、非比例拒绝路径和标准 +2 路径。

---

## 4. Residual Risk 确认

### 4.1 share_change 多份额列选择策略 deferred

`holdings_share_change.py:312-329` `_extract_share_value_from_row` 取 `row[1:]` 首个非空非"-"值。当 A 类为 "-"、C 类有值时返回 C 类值。

**Deferred 是否合理**：合理。

- 004393 为 A 类基金，A 类份额数据在真实年报中始终存在，当前不触发。
- 份额级别选择需引入 fund_code → share_class 映射基础设施，超出本 slice 范围。
- 已在 controller judgment 和 implementation control 中如实记录为 residual risk。
- 测试 `test_extract_holdings_share_change_outputs_share_change_from_subscription_redemption_table` 验证了 A 类优先取值路径正确。

### 4.2 fee_schedule 不以费用金额冒充费率

`§6` 披露的是当期支付管理费/托管费金额（如 "5,000,000.00 元"），不是费率（如 "1.50%/年"）。费率通常在基金合同/招募说明书中，不在年报正文。

**不提取是否合理**：合理。

- `fee_schedule` 语义为"管理费率/托管费率"，将金额作为费率返回是语义错误。
- 下游分析（成本侵蚀 R=A+B-C）依赖费率百分比，金额会直接误导。
- `missing` 状态显式标记，未掩盖数据缺口。

---

## 5. 验证命令

```bash
.venv/bin/pytest tests/fund/extractors/test_performance.py tests/fund/extractors/test_manager_ownership.py tests/fund/extractors/test_holdings_share_change.py -v
# 20 passed in 0.77s

.venv/bin/ruff check fund_agent/fund/extractors/performance.py fund_agent/fund/extractors/manager_ownership.py fund_agent/fund/extractors/holdings_share_change.py tests/fund/extractors/test_performance.py tests/fund/extractors/test_manager_ownership.py tests/fund/extractors/test_holdings_share_change.py
# All checks passed

git diff --check
# passed
```

---

## 6. 结论

**PASS**

两个中风险 finding 均已正确闭合，修复方案合理，回归测试充分覆盖对抗性场景。两项 residual risk deferral 决策均经代码验证确认合理。无阻塞项。
