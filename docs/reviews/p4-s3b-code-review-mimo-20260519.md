# Code Review

## Scope

- Mode: current changes
- Branch: main (uncommitted workspace changes)
- Base: main (staged + unstaged)
- Output file: `docs/reviews/p4-s3b-code-review-mimo-20260519.md`
- Included scope:
  - `fund_agent/fund/extractors/performance.py`
  - `fund_agent/fund/extractors/manager_ownership.py`
  - `fund_agent/fund/extractors/holdings_share_change.py`
  - `tests/fund/extractors/test_performance.py`
  - `tests/fund/extractors/test_manager_ownership.py`
  - `tests/fund/extractors/test_holdings_share_change.py`
  - `fund_agent/fund/README.md`, `tests/README.md`
  - `docs/reviews/p4-s3b-implementation-20260519.md`
  - Snapshot/score artifacts: `reports/extraction-snapshots/p4-s3b-004393-final/`, `reports/extraction-snapshots/p4-s3b-004393-final-score/`
- Excluded scope: `fee_schedule`, `investor_return`, `turnover_rate`, `holdings_snapshot` — intentionally deferred per slice boundary.
- Parallel review coverage: 无

## Findings

### 1-未修复-中-`_find_header_index` 子串匹配可误中相邻列

- **入口/函数**: `performance.py:_find_header_index` (line 172), `performance.py:_extract_nav_benchmark_table_fields` (line 238)
- **文件(行号)**: `fund_agent/fund/extractors/performance.py:172-189`
- **输入场景**: 表头同时包含 "份额净值增长率" 和 "份额净值增长率标准差" 两列（当前 004393 测试表头即为此形态）
- **实际分支**: `_find_header_index(table.headers, "净值增长率")` 遍历表头，在 "份额净值增长率①" 命中后立即返回 index 1
- **预期行为**: 应精确匹配 "净值增长率" 语义列，不误中 "标准差" 列
- **实际行为**: 因使用 `keyword in _compact_text(header)` 子串匹配，"净值增长率" 同时命中 "份额净值增长率①" 和 "份额净值增长率标准差②"；当前因遍历顺序碰巧返回正确列（index 1），但列序变化时会静默选错
- **直接证据**: `performance.py:187` — `if keyword in _compact_text(header)` 为子串包含判断
- **影响**: 静默返回错误列的数值。当前 004393 因列序正确不受影响；列序不同的基金会抽取标准差值代替增长率
- **建议改法和验证点**: 对 "净值增长率" 关键词增加排除 "标准差" 的负向条件，或改用更精确的关键词集合（如 `("份额净值", "增长率")` + 排除 `("标准差",)`）。验证：构造表头列序反转的 ParsedTable，断言仍命中增长率列
- **修复风险（低/中/高）**: 低
- **严重程度（低/中/高/严重）**: 中

### 2-未修复-中-`_infer_adjacent_personal_ratio` 硬编码 `+2` 偏移依赖列布局

- **入口/函数**: `manager_ownership.py:_infer_adjacent_personal_ratio` (line 488)
- **文件(行号)**: `fund_agent/fund/extractors/manager_ownership.py:488-508`
- **输入场景**: 跨页持有人结构续表，机构比例在 index 4，个人比例在 index 6（004393 表头：`份额级别 | 持有人户数 | 户均持有 | 机构持有份额 | 机构比例 | 个人持有份额 | 个人比例`）
- **实际分支**: 找到 institutional_value 所在 cell index 后，返回 `index + 2` 处的值
- **预期行为**: 应从表头语义推断个人比例列位置
- **实际行为**: 硬编码 `+2` 假设机构比例和个人比例之间恰好隔一列（个人持有份额列）。若续表省略持有份额列、只有比例列（`机构比例 | 个人比例`），偏移会指向越界或错误列
- **直接证据**: `manager_ownership.py:507` — `return _cell_at(row, index + 2)`
- **影响**: 跨页续表布局与 004393 不同时，个人比例静默返回错误值或 None
- **建议改法和验证点**: 增加 `_cell_at(row, index + 1)` 的探测：若 `index + 1` 处 cell 可解析为百分比，优先取之；否则回退 `+2`。或用表头 "个人投资者" 语义重新定位。验证：构造只有比例列的续表 ParsedTable，断言仍正确抽取
- **修复风险（低/中/高）**: 低
- **严重程度（低/中/高/严重）**: 中

### 3-未修复-低-`_extract_share_value_from_row` 无份额级别选择策略

- **入口/函数**: `holdings_share_change.py:_extract_share_value_from_row` (line 312)
- **文件(行号)**: `fund_agent/fund/extractors/holdings_share_change.py:312-329`
- **输入场景**: 份额变动表含 A 类和 C 类两列，A 类值为 "-"，C 类有数值
- **实际分支**: `row[1:]` 遍历跳过 "-"，命中 C 类值并返回
- **预期行为**: 按基金代码对应的份额级别选择正确列
- **实际行为**: 取首个非空非 "-" 值，不区分份额级别。当前适配 004393 A 份额场景；C 份额基金代码（如 004393C）会抽取 A 类数据
- **直接证据**: `holdings_share_change.py:325-328` — 遍历 `row[1:]` 取首个有效值
- **影响**: C 份额基金代码场景会返回 A 份额数据，静默错误
- **建议改法和验证点**: Implementation artifact 已记录此为 residual risk。后续需引入份额级别选择策略（从 fund_code 后缀或 fund_type 推断）
- **修复风险（低/中/高）**: 低
- **严重程度（低/中/高/严重）**: 低

## Open Questions

- 无

## Residual Risk

- **多基金泛化**: 当前全部 extractor 逻辑和测试围绕 004393 单一基金形态设计。`_select_nav_benchmark_row` 的 fallback 行为（无 "过去一年" 时取首个非 "自基金合同生效" 行）、`_is_holder_structure_continuation` 的跨页检测、`_extract_holder_values` 的多级回退链均未在其他基金形态上验证。加入 golden set 中 000216/007721/007360/006597 后可能暴露新的布局差异。
- **表头子串匹配泛化风险**: `performance.py` 和 `manager_ownership.py` 的 `_find_header_index` 均使用子串包含匹配。PDF 表头换行被压缩后，语义相近列（增长率 vs 标率差、持有份额 vs 占总份额比例）可能被误匹配。当前因列序碰巧正确未触发。
- **`_compact_text` 实现不一致**: `holdings_share_change.py:73` 使用 `"".join(value.split())`，`performance.py:133` 和 `manager_ownership.py:144` 使用 `re.sub(r"\s+", "", value)`。功能等价，但三文件各有一份副本，后续维护可能引入行为分歧。
- **correctness 未验证**: `score.md` 明确标注 `correctness: not_implemented`。当前 coverage/traceability 100% 仅证明值被抽取且有 anchor，不证明值正确。需后续 golden answer 对齐。
- **跨页表格顺序依赖**: `_is_holder_structure_continuation` 依赖 `report.tables` 列表中两张表相邻且前表包含组表头。若 PDF 解析器产出的表格顺序不同或中间插入其他表格，跨页检测会失败。

## Commands Run

```bash
.venv/bin/pytest tests/fund/extractors/test_performance.py tests/fund/extractors/test_manager_ownership.py tests/fund/extractors/test_holdings_share_change.py -v
# 17 passed in 0.72s

.venv/bin/ruff check fund_agent/fund/extractors/performance.py fund_agent/fund/extractors/manager_ownership.py fund_agent/fund/extractors/holdings_share_change.py
# All checks passed!

cat reports/extraction-snapshots/p4-s3b-004393-final-score/score.md
# p0_status=fail, correctness=not_implemented, pass=9, fail=5

cat reports/extraction-snapshots/p4-s3b-004393-final/summary.md
# 5 slice fields at 100% coverage/traceability
```

## Verdict

**PASS** — 无阻塞性 defect。3 项 finding 均为不同基金布局下的 latent risk，当前 004393 不触发。Implementation artifact 如实记录了 correctness 未实现和 residual risks，未 overstate。代码结构清晰，fallback 链合理，测试覆盖 004393 场景充分。
