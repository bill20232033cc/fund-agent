# Bond Risk Evidence Narrow False-Negative — Code Review (DS)

> Date: 2026-05-28
> Role: code review worker (DS), not controller, not fix worker
> Gate: `bond risk evidence narrow false-negative gate`
> Reviewed artifacts:
>   - `fund_agent/fund/extractors/bond_risk_evidence.py` (diff)
>   - `tests/fund/extractors/test_bond_risk_evidence.py` (diff)
>   - Accepted plan: `docs/reviews/release-maintenance-bond-risk-evidence-narrow-false-negative-plan-20260528.md`
>   - Controller judgment: `docs/reviews/release-maintenance-bond-risk-evidence-narrow-false-negative-plan-controller-judgment-20260528.md`
>   - Implementation report: `docs/reviews/release-maintenance-bond-risk-evidence-narrow-false-negative-implementation-20260528.md`

## Verdict: PASS_WITH_FINDINGS

无 HIGH 严重度发现。3 个 MEDIUM 发现和 2 个 LOW 发现，均可在后续 gate 修复，不阻断当前 gate 合入。

---

## 1. credit_risk — 基金自身评级误判检查

### 1.1 结论：未发现 fund_rating / ratings / fund_own_rating 语义

- `metric_name="持仓评级分布"`，不含 `基金评级`、`本基金评级` 等禁用语。
- `summary="年报表格披露持有债券/证券的信用评级分布"`，使用持仓/持有措辞。
- `evidence_role="holding_rating_distribution"`，未使用 `fund_rating` / `ratings` / `fund_own_rating`。
- 全文搜索未命中任何 forbidden wording。

### 1.2 基金自身评级拒止链路

`_is_holding_rating_distribution_table()` (`bond_risk_evidence.py:1135–1158`) 三层拒止：

1. `_FUND_OWN_RATING_KEYWORDS` 显式命中 → 拒止 (`"本基金评级"`, `"基金评级信息"`, `"基金自身评级"`)
2. 无 `"信用评级"` / `"短期信用评级"` / `"长期信用评级"` → 拒止
3. `"本基金"` + `"评级"` 同时出现且无 `_HOLDING_RATING_QUALIFIERS` → 拒止

三层均正确对应 plan 要求。额外加固：即使 `"本基金"` + `"评级"` 同时出现，只要存在持仓限定词（`持有/持仓/证券/债券/投资组合/组合`）也会放行，避免过度拒止正常持仓表。

### 1.3 评级标签识别

`_rating_label_from_row()` (`:1161–1178`) 使用 `in` 子串匹配，`_CREDIT_RATING_LABELS` 按「长标签优先」排列（`A-1` > `AAA以下` > `AAA` > `AA+` > `AA-` > `AA` > `A+` > `A-` > `A`），确保 `A` 不会在 `AA+` / `A-` 之前抢先匹配。所有 plan 要求的标签均已覆盖。

### 1.4 Numeric Shape 严格性

`_credit_rating_distribution_rows()` (`:1065–1132`)：

- `len(rows) < 2` 或 `non_zero_numeric_rows == 0` → 拒止 ✓
- 评级行必须同时有识别到的评级标签和可解析的当前期金额 ✓
- 百分比列被 `_current_period_value_column_index()` 跳过 ✓
- 行级锚点含 page_number / table_id / row_locator ✓
- 多张有效表保留全部锚点 ✓

### 1.5 Finding M1 (MEDIUM): `_current_period_value_column_index` 不区分本期/上期列

**文件**: `fund_agent/fund/extractors/bond_risk_evidence.py`
**函数**: `_current_period_value_column_index()` (`:1200–1218`)
**严重度**: MEDIUM

**问题**: 函数选取行中第一个非百分比可解析数值列作为「当前期」金额列。若年报表格列顺序为 `(评级标签, 上年度末公允价值, 本期末公允价值)`——即先前期后本期——函数会静默选取前期列，导致 `metric_value` 和锚点金额为前期数据。

**当前实践**: 国内年报表格惯例是本期列在前、前期列在后，006597/2024 实际表格符合此惯例。但代码未对此做任何校验或 header 语义检查。

**修复建议**: 
- 对候选列的 header 文本做 `"本期"` / `"期末"` 语义检查，优先选取含本期语义的列
- 或至少校验：若 header 含 `"上年度"` / `"上期末"` 则跳过
- 若无法区分本期/前期且有多列可选，应 fail closed 而非静默选取第一列

**Plan 对照**: Plan 要求 "Require numeric shape: at least one data row must have a recognized rating category label and a parseable current-period numeric amount"——明确要求 current-period。当前实现可在特定列序下选取前期值。

---

## 2. redemption_share_pressure — A/C/E/F 全聚合检查

### 2.1 结论：确认全类别聚合，A-only 路径已移除

旧 `_select_share_change_column()` 按当前 `fund_code` 单选一列的逻辑已完全替换。新路径：

1. `_share_class_mapping()` → 表格优先，文本回退，提取 A/C/E/F 全映射
2. `_align_share_change_columns()` → 要求值列数精确等于映射类别数，一对一消歧
3. `_calculate_share_class_changes()` → 逐类别计算并做类别级算术对账
4. `_aggregate_share_change()` → 全类别汇总 + 汇总级算术对账

### 2.2 §10 Candidate Selection Fail-Closed

`_find_share_change_table()` (`:1247–1272`) + `_share_change_table_score()` (`:1275–1302`)：

- 扫描全部表格，打分选最优 ✓
- 财务报表关键词拒止（`实收基金/未分配利润/净资产合计`）→ score=0 ✓
- 必须同时满足 boundary row + flow row + share semantics 三项 ✓
- 非唯一最优 → `ambiguous_share_change_table` ✓
- 无候选 → `na_reason=None`，由上层 `_missing_group` 兜底 ✓

打分逻辑偏重 `基金份额总额` 等强语义关键词（+2 each），实际 §10 表也应至少命中一个，不会误伤。

### 2.3 Decimal / Dash / Tolerance

- `_parse_share_decimal()` (`:1870–1883`) 调用 `_parse_plain_decimal(value, dash_as_zero=True)` ✓
- `_parse_plain_decimal()` (`:1886–1910`)：逗号去除 → 空白压缩 → dash 识别 → `%` 拒止 → `Decimal()` 转换 ✓
- `_DASH_ZERO_VALUES = ("-", "－", "—", "--")` 覆盖全角/半角/双横线 ✓
- `_DECIMAL_TOLERANCE = Decimal("0.01")` ✓
- `_decimal_close()` (`:1913–1927`) 使用绝对差 `abs(left - right) <= 0.01` ✓

### 2.4 Column Alignment

`_align_share_change_columns()` (`:1536–1583`)：

- `value_columns` 排除 index 0（行标签列）和 `_is_total_share_header` ✓
- `len(value_columns) != len(mapping.class_labels)` → `share_class_column_count_mismatch` ✓
- 逐类别按 `fund_code in header` 或 `_contains_share_class_label` 匹配，要求唯一且不重复 ✓

### 2.5 Anchor Completeness

`_share_change_row_anchor_drafts()` (`:1726–1769`) 为 `share_beginning/subscription/redemption/split_or_change/share_ending` 五种角色构锚。`_aggregate_share_change()` 要求 `len(drafts) >= 4`（split 可选，其余四行必须）。✓

### 2.6 Finding M2 (MEDIUM): `_find_share_change_row` 单关键词匹配过宽

**文件**: `fund_agent/fund/extractors/bond_risk_evidence.py`
**函数**: `_find_share_change_row()` (`:1577–1599`), `_find_share_change_rows()` (`:1544–1574`)
**严重度**: MEDIUM

**问题**: 
- `subscription = _find_share_change_row(table, required_keywords=("申购",))` ——只要行文本含 `"申购"` 即命中。
- `redemption = _find_share_change_row(table, required_keywords=("赎回",))` ——同理。

这可能在更复杂的 §10 表中首先命中 `"净申购"` 行或 `"累计申购"` 行，而非 `"本期基金总申购份额"` 行。当前 006597 表格和测试 fixture 不触发此问题，但代码未防御。

**修复建议**: 
- `subscription` 增加关键词 `("总申购",)` 或 `("申购份额",)`
- `redemption` 增加 `("总赎回",)` 或 `("赎回份额",)`
- 或使用更紧的匹配，如要求 `("本期", "申购")` 同时出现

### 2.7 Finding M3 (MEDIUM): `_next_profile_code_row` 扫描窗口仅 3 行

**文件**: `fund_agent/fund/extractors/bond_risk_evidence.py`
**函数**: `_next_profile_code_row()` (`:约 1378 行`)
**严重度**: MEDIUM

**问题**: `enumerate(rows[start_row_number : start_row_number + 4], ...)` 在简称行之后仅扫描 3 行查找交易代码行。若 §2 表格在简称行和代码行之间有间隔行（如空行、注释行），代码行将被漏掉，导致表格映射失败并回退到文本行解析。

标准年报 §2 表格结构为简称行 → 代码行紧密相邻，006597 抓取满足此假设。但容错窗口小。

**修复建议**: 扩展到 5 行或扫描到表格末尾。

---

## 3. drawdown_stress — Weak Boundary 保持检查

### 3.1 结论：未引入 NAV-derived 或 score/gate 绕过

`_extract_drawdown_stress()` (`:462–523`) 未做任何修改：

- 定性 `控制回撤` 文本 → `status="weak"`, `strength="qualitative_control_intent"` ✓
- 无 NAV 计算、无 max drawdown 推导、无 volatility 估算 ✓
- `drawdown_stress not in satisfied_group_ids` ✓

测试 `test_drawdown_control_text_alone_is_weak()` 保持不变，继续断言 weak 且 unsatisfied。✓

---

## 4. 边界越界检查

### 4.1 结论：未越界

修改范围严格限于 plan 允许的两个文件：

- `fund_agent/fund/extractors/bond_risk_evidence.py` ✓
- `tests/fund/extractors/test_bond_risk_evidence.py` ✓

未修改的文件（已确认）：
- `fund_agent/fund/extractors/models.py` — 未改动
- `fund_agent/fund/extraction_snapshot.py` — 未改动
- `fund_agent/fund/extraction_score.py` — 未改动
- `fund_agent/fund/quality_gate.py` — 未改动
- Service / UI / Host / Agent / dayu 模块 — 均未涉及

新增内部 dataclass（`_CreditRatingDistributionEvidence` / `_ShareClassMapping` / `_ShareChangeTableSelection` / `_ShareChangeColumnMapping` / `_ShareChangeRows` / `_ShareClassChange` / `_ShareChangeAggregation`）全部以 `_` 前缀，为模块私有。✓

---

## 5. 测试覆盖与过拟合检查

### 5.1 Plan 要求对照

| Plan 要求测试 | 实现 | 状态 |
|---|---|---|
| `test_holding_rating_distribution_table_is_credit_risk_portfolio_exposure_not_fund_rating` | `:1256` | PASS |
| `test_fund_own_rating_table_is_rejected_for_credit_risk` | `:1299` | PASS |
| `test_multiple_holding_rating_distribution_tables_preserve_all_anchors` | `:1323` | PASS |
| `test_credit_risk_qualitative_text_without_rating_distribution_remains_weak` | `:1356` | PASS |
| `test_credit_risk_anchor_missing_not_accepted` | `:1374` | PASS |
| `test_share_class_evidence_from_section_two_table` | `:1445` | PASS |
| `test_redemption_share_pressure_aggregates_all_a_c_e_f_classes` | `:1487` | PASS |
| `test_redemption_share_pressure_not_a_only` | `:1481` | PASS |
| `test_redemption_share_pressure_rejects_net_asset_statement_table` | `:1501` | PASS |
| `test_redemption_share_pressure_fails_closed_when_class_columns_do_not_align` | `:1521` | PASS |
| `test_redemption_share_pressure_fails_closed_on_arithmetic_mismatch` | `:1541` | PASS |
| `test_redemption_share_pressure_fails_closed_on_non_parseable_share_value` | `:1570` | PASS |
| `test_redemption_share_pressure_parses_full_width_dash_as_zero` | `:1599` | PASS |
| `test_redemption_share_pressure_anchor_missing_not_accepted` | `:1628` | PASS |
| drawdown weak test (existing) | `test_drawdown_control_text_alone_is_weak` | PASS |

15 项 plan 要求测试全部实现。另有存量测试更新（`test_table_backed_credit_risk_is_accepted_with_row_level_anchor` 等）以适配新 helper。

### 5.2 过拟合检查

- 测试 fixture 使用独立的 `_rating_distribution_table()` / `_share_change_table_ac_ef()` / `_share_class_mapping_table()` / `_net_asset_statement_like_table()` 工厂函数，不与生产路径耦合 ✓
- `test_redemption_share_pressure_not_a_only` 验证 `"all_classes: beginning=1000000" not in metric`，确保 A 单类 initial 值 1,000,000 不等于全类汇总 3,000,000 ✓
- `test_redemption_share_pressure_fails_closed_on_arithmetic_mismatch` 使用人为不一致的 E 类 ending (`-200,000.00`) 制造对账失败 ✓
- 未发现对 hardcoded 006597 具体数值的过度依赖（all-class 测试使用 fixture，非真实年报数据）

### 5.3 Finding L1 (LOW): `test_credit_risk_anchor_missing_not_accepted` 测试名称有歧义

**文件**: `tests/fund/extractors/test_bond_risk_evidence.py:1374`
**严重度**: LOW

**问题**: 测试名称为 "anchor_missing_not_accepted"，但实际验证的是「纯百分比无金额列的表不满足 credit_risk」。测试使用 `("AAA", "80.00%")` 行——百分比列被跳过，无 parseable 金额，导致 `_credit_rating_distribution_rows` 返回空元组，最终走 qualitative fallback。测试逻辑正确但命名暗示的场景（anchor missing）与实际触发路径（percentage-only rows → no numeric period value）不一致。

**修复建议**: 更名为 `test_credit_risk_percentage_only_table_not_accepted`。

### 5.4 Finding L2 (LOW): `_share_change_table_ac_ef` 默认 fixture 含负期末份额

**文件**: `tests/fund/extractors/test_bond_risk_evidence.py:1132`
**严重度**: LOW

**问题**: 默认 rows 中 E 类 `ending="-200,000.00"` 为负值，虽算术自洽（`0 + 300,000 - 500,000 + 0 = -200,000`），但真实基金不存在负期末份额。此 fixture 被多个测试复用，若后续有测试假设期末份额非负，可能被误导。

**修复建议**: 默认 fixture 使用非负值（如 `"0.00"` 或 `"500,000.00"`），仅在算术 mismatch 测试中使用非典型数据。

---

## 6. 附加观察（非 Finding）

### 6.1 `_is_holding_rating_distribution_table` 的 qualifier 使用方式

`has_holding_qualifier` 变量 (`:1155`) 被计算但仅用于 `"本基金"+"评级"` 的联合拒止条件。不构成独立门控。这意味着不含 `"本基金"` 但包含 `"信用评级"` 的表无需持仓限定词即可通过。这是合理设计：`"信用评级"` 关键词出现在表格中且有评级标签行，本身就是强信号。

### 6.2 `_find_share_change_table` 返回类型变更

旧签名返回 `ParsedTable | None`，新签名返回 `_ShareChangeTableSelection`（含 `table` 和 `na_reason` 两个字段）。调用方 `_extract_redemption_share_pressure` 已正确适配：先检查 `table_selection.table is None`，如同时有 `na_reason` 则返回 `ambiguous` 而非 `missing`。语义正确。✓

### 6.3 文本行回退的份额映射变更

`_share_class_mapping_from_profile_lines()` 不再依赖 `fund_code` 参数做单类消歧，改为提取全部类别后成对匹配。`class_labels` 和 `fund_codes` 数量必须相等且 class_labels 无重复（`len(set(class_labels)) != len(class_labels)` → 跳过）。退回 `_ShareClassMapping` 替代旧的 `_ShareClassEvidence`（后者仅返回单个 class_label）。这是设计升级，符合全类别聚合要求。✓

---

## 7. Findings 汇总

| ID | 严重度 | 位置 | 简述 |
|----|--------|------|------|
| M1 | MEDIUM | `bond_risk_evidence.py:1200–1218` `_current_period_value_column_index` | 不区分本期/前期列，可能静默选取前期值 |
| M2 | MEDIUM | `bond_risk_evidence.py:1577–1599` `_find_share_change_row` | `("申购",)` / `("赎回",)` 单关键词匹配过宽，可能先命中子类别行 |
| M3 | MEDIUM | `bond_risk_evidence.py:_next_profile_code_row` | 仅扫描简称行后 3 行查找代码行，窗口偏小 |
| L1 | LOW | `test_bond_risk_evidence.py:1374` | 测试名 "anchor_missing" 与实际触发路径不一致 |
| L2 | LOW | `test_bond_risk_evidence.py:1132` | 默认 fixture 含负期末份额，非真实场景 |

---

## 8. 总体评价

实现严格遵循 accepted plan 和 controller judgment：

- **credit_risk**: 持仓评级分布检测正确，三层基金自身评级拒止完善，numeric shape 和 anchor 要求严格。M1 为列选取在非标列表下的理论风险，实际 006597 表格不受影响。
- **redemption_share_pressure**: A/C/E/F 全聚合路径完整，table selection fail-closed，Decimal/dash/tolerance/column alignment/arithmetic/anchor missing 全部正确。M2/M3 为边界容错性不足。
- **drawdown_stress**: 未做任何升级，保持 weak qualitative 边界。✓
- **边界合规**: 未越界修改 schema/score/snapshot/quality gate/Service/UI/Host/Agent/dayu。✓
- **测试**: 15 项 plan 要求测试全部覆盖，无过拟合。✓

所有 MEDIUM 发现可在后续 gate 修复，不影响当前 gate PASS_WITH_FINDINGS 合入。
