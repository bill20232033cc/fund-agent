# Bond Risk Evidence Narrow False-Negative — Code Re-Review (DS)

> Date: 2026-05-28
> Role: code re-review worker (DS), not controller, not fix worker
> Reviewed artifacts:
> - `docs/reviews/release-maintenance-bond-risk-evidence-narrow-false-negative-code-review-ds-20260528.md` (original DS review, 5 findings)
> - `docs/reviews/release-maintenance-bond-risk-evidence-narrow-false-negative-code-review-mimo-20260528.md` (MiMo review, 3 findings)
> - `docs/reviews/release-maintenance-bond-risk-evidence-narrow-false-negative-code-fix-20260528.md` (fix report)
> - `git diff -- fund_agent/fund/extractors/bond_risk_evidence.py tests/fund/extractors/test_bond_risk_evidence.py`

## Verdict: PASS

所有 DS/MiMo review findings 均已正确闭合，未引入新阻断问题。

---

## 逐 Finding 复核

### DS M1 — current-period column header semantics (MEDIUM) → CLOSED

**原问题**: `_current_period_value_column_index()` 选取第一个非百分比可解析数值列作为当前期列，若列序为「前期在前、本期在后」则静默选取前期值。

**修复**:
- 重构为优先匹配 `_CURRENT_PERIOD_HEADER_KEYWORDS`（本期/本期末/期末/报告期末）
- 排除 `_PRIOR_PERIOD_HEADER_KEYWORDS`（上年度/上年/上期/期初/年初）
- 多列无可靠当前期表头时返回 None → fail closed
- 单列非前期列仍支持

**测试**: `test_credit_risk_uses_current_period_column_when_prior_period_appears_first` — headers `("长期信用评级", "上年度末公允价值", "本期末公允价值")`，断言 `metric_value` 使用 `本期末` 列值（AAA=10000000），且不含前期值（AAA=9000000），anchor note 也使用本期值。

**判定**: 闭合。使用表头语义而非位置启发式，fail closed 在歧义场景，测试覆盖了 DS 和 MiMo 共同关注的列序反转场景。

---

### DS M2 — share-change row matching too broad (MEDIUM) → CLOSED

**原问题**: `_find_share_change_row(table, required_keywords=("申购",))` 单关键词匹配过宽，可能在含 `净申购` / `累计申购` 的表中先命中干扰行。

**修复**:
- 新增 `_SHARE_SUBSCRIPTION_KEYWORD_GROUPS = (("总申购",), ("申购份额",))`
- 新增 `_SHARE_REDEMPTION_KEYWORD_GROUPS = (("总赎回",), ("赎回份额",))`
- 新增 `_SHARE_SUBSCRIPTION_EXCLUDED_KEYWORDS = ("净申购", "累计申购")`
- 新增 `_SHARE_REDEMPTION_EXCLUDED_KEYWORDS = ("净赎回", "累计赎回")`
- `_find_share_change_row` 先过滤含排除关键词的行，再优先匹配偏好关键词组

**测试**: `test_redemption_share_pressure_uses_total_subscription_and_redemption_rows` — 表格中 `净申购份额` / `累计申购份额` / `净赎回份额` / `累计赎回份额` 行在 `本期基金总申购份额` / `本期基金总赎回份额` 之前。断言 anchor row_locator 指向 row:4（总申购）和 row:7（总赎回），aggregation 数值正确。

**判定**: 闭合。排除关键词 + 偏好关键词两层防护，测试场景直接覆盖 DS 描述的风险。

---

### DS M3 — profile code row scan window (MEDIUM) → CLOSED

**原问题**: `_next_profile_code_row()` 仅扫描简称行后 3 行，注释/空行可导致代码行漏检。

**修复**: 改为 `enumerate(rows[start_row_number:], start=start_row_number + 1)` 扫描至表格末尾。

**测试**: `test_share_class_evidence_from_section_two_table_with_intervening_rows` — 简称行后插入注释行 `("注：本表披露各份额类别简称", "", "", "", "")` 和空行 `("", "", "", "", "")`，再出现交易代码行。断言 A/C/E/F 映射成功识别。

**判定**: 闭合。窗口从固定 3 行扩展到表尾，测试含两种间隔行类型。

---

### DS L1 — test name ambiguity (LOW) → CLOSED

**原问题**: `test_credit_risk_anchor_missing_not_accepted` 实际验证的是纯百分比表不满足 credit_risk，名称暗示 anchor missing 与实际触发路径不一致。

**修复**: 重命名为 `test_credit_risk_percentage_only_table_not_accepted`。测试体不变。

**判定**: 闭合。

---

### DS L2 — negative ending shares in default fixture (LOW) → CLOSED

**原问题**: `_share_change_table_ac_ef` 默认 rows 中 E 类 `ending="-200,000.00"` 为负值，非真实场景。

**修复**: E 类 ending 改为 `"0.00"`，F 类使用 `"-"`（dash→0）。全表数值自洽：E 类 0+500000-500000+0=0，F 类 0+100000-100000+0=0。算术 mismatch 测试用独立参数构造不一致数据。

**判定**: 闭合。

---

### MiMo F1 — current-period column detection (= DS M1) → CLOSED

同 DS M1 判定。

---

### MiMo F2 — loose substring rating label matching (LOW) → CLOSED

**原问题**: `label.upper() in row_label` 子串匹配，`A` 可匹配 `AAA`、`A+`、`A-` 等。

**修复**:
- 先做精确匹配 `row_label == label.upper()`
- 再做复合标签匹配 `_is_compound_rating_label()`，要求标签前后字符不是评级 token 字符（A-Z, 0-9, +, -）
- `_CREDIT_RATING_LABELS` 保持长标签优先顺序

**关键逻辑验证**:
- `AAAA 说明行` 对 `AAA`：partition → `("", "AAA", "A 说明行")`，after[0]="A" ∈ rating_token_chars → **拒绝** ✓
- `A+评级债券` 对 `A`：partition → `("", "A", "+评级债券")`，after[0]="+" ∈ rating_token_chars → **拒绝** ✓
- `AAA 债券` 对 `AAA`：partition → `("", "AAA", " 债券")`，after[0]=" " ∉ rating_token_chars → **接受** ✓
- `AA级` 对 `A`：先匹配 `AA` → exact False, compound → after[0]="级" ∉ → 接受 `AA` → 不会到达 `A` ✓

**测试**:
- `test_compound_rating_labels_are_matched_without_loose_substring_false_positive` — `AAAA 说明行` 不产生 9999 锚点，仅 `AAA` 行产生 1000 锚点
- `test_fund_own_credit_rating_table_is_rejected_for_credit_risk` — `本基金信用评级` 表头被 `基金信用评级` 关键词拒止

**判定**: 闭合。子串匹配替换为精确+复合（字符类边界检查），不再有 `A` 误匹配 `AAA`/`A+` 的风险。新增 `基金信用评级` 拒止关键词进一步加固。

---

### MiMo F3 — missing test for prior-period-first column ordering → CLOSED

**原问题**: 所有评级分布测试表头均为本期列在前，缺少前期列在前场景的测试。

**测试**: `test_credit_risk_uses_current_period_column_when_prior_period_appears_first` 覆盖此场景。

**判定**: 闭合。

---

## 新引入问题检查

### 边界合规

仅修改 `bond_risk_evidence.py` 和 `test_bond_risk_evidence.py`。未触及 schema、score、snapshot、quality gate、Service、UI、Host、Agent、dayu。

### `_is_current_period_amount_header` 防御性

函数同时检查 `has_current_period`、`not has_percentage`、`not _is_prior_period_header(header)`。三项同时成立才判定为当前期列。百分比表头（含 `比例`/`占比`）和前期表头被显式排除，即使表头同时出现本期和前期关键词也 fail closed（前期优先拒绝）。

### `_find_share_change_row` 排除/偏好交互

排除关键词过滤先于偏好匹配执行。若一行同时含 `总申购` 和 `净申购`，会被排除关键词拒绝。此场景在真实年报中不可能出现，属于安全侧设计。

### `_is_holding_rating_distribution_table` 新增拒止关键词

`_FUND_OWN_RATING_KEYWORDS` 新增 `"基金信用评级"`。若持仓评级表的脚注中出现此短语，会误拒止。但真实年报脚注使用 `信用评级` 而非 `基金信用评级`，风险极低。

### rating label matching: `合计` / `AAA以下` / `未评级` 支持

三项均在 `_CREDIT_RATING_LABELS` 元组中，精确匹配和复合匹配路径均覆盖。`AAA以下` 在 `AAA` 之前排列，走精确匹配优先路径，不会被 `AAA` 子串捕获后短路（实际上 `AAA以下` != `AAA`，exact 不命中，compound 中 after[0]="以" ∉ rating_chars → `AAA以下` 接受）。**但需注意**：若 row_label 为 `AAA以下`，`AAA` 的 compound 匹配 partition 为 `("", "AAA", "以下")`，after[0]="以" ∉ rating_chars → 也会接受 `AAA`。然而 `AAA以下` 在 tuple 中排在 `AAA` 之前（索引 1 vs 索引 3），精确匹配先命中 `AAA以下` → 返回 `AAA以下`，不会回退到 `AAA`。**此行为正确**。

---

## 测试运行结果

Fix 报告：`uv run pytest tests/fund/extractors/test_bond_risk_evidence.py -q` → 46 passed；`uv run ruff check` → All checks passed。

---

## 汇总

| Finding | 来源 | 严重度 | 状态 |
|---------|------|--------|------|
| M1 / F1 | DS + MiMo | MEDIUM | CLOSED — header 语义选择 + prior-period-first 测试 |
| M2 | DS | MEDIUM | CLOSED — 排除关键词 + 偏好关键词组 + 测试 |
| M3 | DS | MEDIUM | CLOSED — 扫描至表尾 + 间隔行测试 |
| F2 | MiMo | LOW | CLOSED — 精确+复合匹配替代子串 + 测试 |
| F3 | MiMo | LOW | CLOSED — prior-period-first 测试已添加 |
| L1 | DS | LOW | CLOSED — 测试重命名 |
| L2 | DS | LOW | CLOSED — 默认 fixture 修正 |

结论：所有 5 个 DS finding + 3 个 MiMo finding 均已闭合，无新阻断问题。PASS。
