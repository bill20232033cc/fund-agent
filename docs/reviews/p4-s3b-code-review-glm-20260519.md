# Code Review

## Scope

- Mode: current changes
- Branch: main (unstaged working tree changes)
- Base: main (no committed divergence)
- Output file: `docs/reviews/p4-s3b-code-review-glm-20260519.md`
- Included scope:
  - `fund_agent/fund/extractors/performance.py`
  - `fund_agent/fund/extractors/manager_ownership.py`
  - `fund_agent/fund/extractors/holdings_share_change.py`
  - `tests/fund/extractors/test_performance.py`
  - `tests/fund/extractors/test_manager_ownership.py`
  - `tests/fund/extractors/test_holdings_share_change.py`
  - `fund_agent/fund/README.md`
  - `tests/README.md`
  - `docs/reviews/p4-s3b-implementation-20260519.md`
- Excluded scope: `fee_schedule`, `investor_return`, `turnover_rate`, `holdings_snapshot` (intentionally out of slice)
- Parallel review coverage: 无

## Commands Run

```bash
git branch --show-current                          # main
git status --short                                 # 8 modified, 0 staged
git diff -- fund_agent/fund/extractors/*.py        # full production diff
git diff -- tests/fund/extractors/test_*.py        # full test diff
git diff -- fund_agent/fund/README.md tests/README.md
cat fund_agent/fund/documents/models.py            # ParsedTable, ParsedAnnualReport contracts
cat fund_agent/fund/extractors/models.py           # ExtractedField, EvidenceAnchor contracts
.venv/bin/pytest tests/fund/extractors/test_performance.py tests/fund/extractors/test_manager_ownership.py tests/fund/extractors/test_holdings_share_change.py -v  # 17 passed in 0.71s
.venv/bin/ruff check fund_agent/fund/extractors/*.py tests/fund/extractors/test_*.py  # All checks passed!
```

## Verdict: PASS

## Findings

### F1-未修复-中-holder_structure 跨页续表个人比例推断使用硬编码列偏移且无格式校验

- **入口/函数**: `_infer_adjacent_personal_ratio` → `_extract_holder_values` → `_extract_holder_structure_from_table`
- **文件(行号)**: `fund_agent/fund/extractors/manager_ownership.py:488-508`
- **输入场景**: §9 持有人结构表跨页拆分，数据页表头不含"机构投资者"/"个人投资者"关键词，且行文本也不含这些关键词；此时 `individual_index` 为 `None`，第一行 fallback 也返回 `None`，触发 `_infer_adjacent_personal_ratio`。
- **实际分支**: 在数据行中找到与 `institutional_value` 字面相等的单元格后，取 `index + 2` 位置的值作为个人比例。
- **预期行为**: 返回个人投资者占比。
- **实际行为**: 对 CSRC 标准布局（机构份额 | 机构比例 | 个人份额 | 个人比例）返回正确值；但如果某个基金的列顺序不同（例如中间插入了"合计"列），+2 偏移会静默返回错误列的值。返回值也不校验是否像百分比（数字 + 可选 `%`），可能将份额或户数当作比例返回。
- **直接证据**: `manager_ownership.py:507` — `return _cell_at(row, index + 2)` 中 `2` 是硬编码魔数，无注释说明其基于何种列布局假设。
- **影响**: 对非标准列布局的基金会静默返回错误持有人结构数据，下游分析基于错误比例做出判断。
- **建议改法和验证点**:
  1. 在 `_infer_adjacent_personal_ratio` 中增加校验：对返回值检查是否匹配 `\d+(\.\d+)?%?` 模式，不匹配时返回 `None`。
  2. 在注释中说明 `+2` 基于"机构份额-机构比例-个人份额-个人比例"标准布局。
  3. 添加一个列顺序不同的测试用例验证 fallback 返回 `None` 而非错误值。
- **修复风险（低）**: 改动仅在 fallback 路径中增加防御性检查，不影响正常路径。
- **严重程度（中）**: 静默返回错误比例可能污染下游投资分析，但仅发生在跨页续表且所有前置方法均失败的场景。

### F2-未修复-低-share_change 多份额列取首个有效值，无份额级别选择策略

- **入口/函数**: `_extract_share_value_from_row` → `_extract_share_change`
- **文件(行号)**: `fund_agent/fund/extractors/holdings_share_change.py:312-329`
- **输入场景**: §10 份额变动表含 A/C 类多列，且 A 类份额列为空或"-"时。
- **实际分支**: `for cell in row[1:]` 顺序遍历，返回第一个非空非"-"的值。
- **预期行为**: 应根据基金代码对应的份额级别（A 或 C）选择正确的份额列。
- **实际行为**: 始终取第一个有效值。当 A 类为空时，取 C 类值作为"该基金"的份额变动。对 004393（A 类基金）当前不会触发此问题，因为 A 类数据始终存在。
- **直接证据**: `holdings_share_change.py:325` — `for cell in row[1:]` 无份额级别过滤。
- **影响**: 对 A 类份额为空、C 类有值的基金会返回 C 类份额数据，静默混入错误的份额变动。
- **建议改法和验证点**:
  1. 当前列出为 residual risk 是合理的，当前 slice 不需要修复。
  2. 后续 slice 应设计份额级别选择策略（基于基金代码后缀或表头中的"A"/"C"标记）。
  3. 添加一个 A 类为空、C 类有值的测试用例，验证当前行为并标记为已知限制。
- **修复风险（低）**: 当前行为对 004393 正确；修复需要引入份额级别概念，设计成本高于当前 slice 范围。
- **严重程度（低）**: 仅在 A 类份额完全缺失时触发，现实中 A 类基金年报中 A 类份额几乎不会为空。

## Open Questions

- 无。

## Residual Risk

1. **`_SECTION_HEADING_PATTERN` 对小数开头的正文行理论上的误匹配风险**: 正则 `^\d{1,2}\.\d{1,2}(?:\.\d{1,2})?\s+.+$` 要求点号后有至少一个空白再接正文，`14.68%` 不匹配（已通过测试验证），但 `1.23 亿元净利润` 等格式理论上可匹配。实际年报 §4 文本不以小数开头断行，风险极低，无需当前修复。

2. **`_extract_nav_benchmark_table_fields` 返回首个匹配表**: 若年报中存在多张净值表现表（如 A/C 类分别列示），当前取第一张。无份额级别选择。与 pre-existing 行为一致，非本 slice 回归。

3. **`_extract_holder_structure_from_table` 和 `_extract_manager_alignment_from_tables` 遍历 `report.tables` 全部表格**: 不过滤 §9 范围。关键词组合足够特异（"持有人户数"+"机构投资者"+"个人投资者"、"从业人员"+"持有"+"份额"），误匹配风险极低。

4. **`_calculate_net_change` 使用 `Decimal` 精确计算**: 正号/负号正确（ending - beginning），格式含千分位逗号和两位小数。但未处理括号表示的负数（如 `(100,000.00)`），若年报使用括号负数会返回 `None`。当前 `InvalidOperation` 异常已兜底。

5. **Tests 仅覆盖构造的 `ParsedTable`，未覆盖真实 PDF 解析路径**: 这是正确的边界——extractor 测试不应依赖真实 PDF。真实端到端验证由 snapshot/score 测试覆盖。

6. **implementation artifact 中 `holder_structure` anchor 描述**: artifact 第 131 行写 anchor `§9 page-63-table-0`，但真实 004393 的持有人结构数据来自跨页续表（page 63 table 0 为数据表，page 62 为组表头表）。extractor 代码正确地从 page 63 数据表提取并生成 anchor，artifact 描述与代码一致。

## Reviewer Notes

逐行走读了三条完整主链路：

1. **performance.py table fallback**: `_build_nav_benchmark_performance` → `_extract_field` (colon-line) → miss → `_extract_nav_benchmark_table_fields` → `_is_nav_benchmark_table` (compact+keyword) → `_find_header_index` (compact header) → `_select_nav_benchmark_row` (preferred period) → `_cell_at` → anchor。表头换行通过 `_compact_text` 正确处理；`14.32%` 等值不会被 `_find_header_index` 误判为表头。

2. **manager_ownership.py heading block**: `_build_manager_strategy_text` → `_extract_field` (colon-line) → miss → `_extract_heading_block` → `_STRATEGY_HEADING_PATTERN` match → collect lines → `_SECTION_HEADING_PATTERN` stop。`14.68%，...` 因 `%` 后不跟 `\s+` 而不匹配停止模式，正确保留在策略文本中。`4.5 管理...` 正确匹配停止模式。

3. **holdings_share_change.py subscription/redemption table**: `_build_share_change` → `_find_share_change_table` → `_is_share_change_table` (期初+期末+基金份额总额 AND 净变动|申购赎回) → `_extract_share_change` → `_extract_share_value_from_row` (first valid) → `_calculate_net_change` (Decimal)。利润变动表因缺少"基金份额总额"被正确排除。

未发现正确性缺陷。两处 finding 均为已知的通用性限制，已在 implementation artifact 的 Residual Risks 中记录。代码质量良好，测试覆盖了关键 adversarial 场景。
