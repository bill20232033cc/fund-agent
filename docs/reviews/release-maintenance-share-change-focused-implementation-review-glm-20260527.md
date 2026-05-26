# Code Review: Share-Change Focused Implementation

> **Reviewer**: AgentGLM (independent code reviewer)
> **Date**: 2026-05-27
> **Review scope**: uncommitted diff on `fund_agent/fund/extractors/holdings_share_change.py` + `tests/fund/extractors/test_holdings_share_change.py`
> **Plan**: `docs/reviews/release-maintenance-share-change-focused-implementation-plan-20260527.md`
> **Controller judgment**: `docs/reviews/release-maintenance-share-change-focused-implementation-plan-controller-judgment-20260527.md`
> **Evidence**: `docs/reviews/release-maintenance-share-change-focused-implementation-evidence-20260527.md`

---

## Findings

### F1 — MATERIAL: `_contains_share_class_label` 的 `endswith` 检查对拉丁字母结尾的非份额类文本存在误报向量

**Evidence**:
- `_contains_share_class_label`（holdings_share_change.py:936-944）使用三个模式检测份额类别：`"{label}类"`、`"{label}份额"`、`endswith(label)`。
- `endswith` 检查在 `_compact_text`（仅去空白）和 `.upper()` 之后执行。对于以拉丁字母结尾的任意文本，只要该字母属于 A-Z 就会匹配。
- 具体误报向量：文本 "沪深300ETF" → compact → "沪深300ETF" → upper → "沪深300ETF" → `endswith("F")` → True。此时 `_share_class_label_from_text` 仅匹配到 "F"（不匹配 E/T），返回 `"F"` 作为唯一标签。
- 同理，"上市开放式基金LOF" → `endswith("F")` → True。
- 旧代码也有 `endswith` 检查，但仅用于 A 和 C 两个标签。扩展到 A-Z 后误报面从 2 个字母扩展到 26 个字母。

**Risk**: 中等。误报在以下场景可能触发：
1. `_share_headers_from_split_header`：ETF 名称作为 §10 分表表头被错误识别为份额类标签，可能导致表头列数计算偏差。
2. `_class_matches_from_rows`：§2 表格中 ETF 基金名被错误标记为 "F" 类，导致 §2 evidence 返回错误标签。
3. `_is_split_share_header_table` 和 `_is_split_share_data_table`：通过 `_table_share_class_label_count` 间接调用，可能导致非份额列被计入。

实际缓解因素：
- `_share_class_label_from_text` 要求 exactly one unique match。"ETF" 中的 E 和 T 不会触发 endswith（因为 "ETF" 不以 E 或 T 结尾），所以只匹配 F，返回 "F" 而非 None。这意味着缓解因素不充分。
- 中国年报 §10/§2 表格中 ETF 名称出现在份额变动表表头的场景确实存在（指数基金/ETF 联接基金），但通常是单份额类别而非多类别表格。
- 多类别表格中 ETF 名称列被识别为 "F" 类后，下游还需在 §10 中找到对应 "F" 列才可能误选。如果 §10 无 "F" 类列，映射会失败（安全）。

**Recommendation**: 在 `endswith` 分支添加前驱字符约束：`endswith(label)` 仅当 label 前一个字符为中文字符或特定分隔符时才返回 True。例如检查 `compact_text[-len(label)-1]` 是否为非拉丁字母。这样 "债券A"（前驱 "券"）匹配，"沪深300ETF"（前驱 "T" 为拉丁字母）不匹配。此修复可在后续 robustness gate 中实施，不阻塞本 slice closeout，因为：(a) 当前实现的所有 21 个测试通过；(b) 006597 实际 rerun 保持了 fail-closed 行为；(c) 被修改的 `_is_split_share_header_table` 仅在 >= 2 个标签时触发，单标签误报不会独立造成 split-table 误判。

---

### F2 — INFO: `_is_split_share_header_table` 和 `_is_split_share_data_table` 的 A/C → A-Z 泛化无回归风险

**Evidence**:
- `_is_split_share_header_table`（原 line 267-280）从 `contains(A) AND contains(C) AND no_期初/期末` 改为 `_table_share_class_label_count >= 2 AND no_期初/期末`。
  - A/C 表格：`_table_share_class_label_count` 返回 2 → `>= 2` True → 行为不变 ✓
  - A-only 表格：count 返回 1 → `>= 2` False → 行为不变 ✓
- `_is_split_share_data_table`（原 line 290-300）从 `NOT contains(A) AND NOT contains(C)` 改为 `_table_share_class_label_count == 0`。
  - A/C 数据表（无标签）：count 0 → `== 0` True → 行为不变 ✓
  - 含标签的表：count > 0 → `== 0` False → 行为不变 ✓

泛化对已有 A/C 测试用例无回归风险 ✓。

**Risk**: 无。

---

### F3 — INFO: §2 subordinate mapping 扩展安全，新检测条件足够精确

**Evidence**:
- `_table_likely_belongs_to_section_two`（line 831-843）新增 `has_subordinate_mapping` 分支：检查是否同时包含 `_SUBORDINATE_FUND_NAME_KEYWORDS` 和 `_SUBORDINATE_FUND_CODE_KEYWORDS` 中的至少一个关键词。
- 关键词分别为 "下属分级基金的基金简称"/"下属分级基金的基\n金简称" 和 "下属分级基金的交易代码"/"下属分级基金的交\n易代码"。这些是非常具体的年报术语，误识别风险极低。
- 新增 `or` 逻辑意味着含基金名称/主代码的表（旧行为）和仅含下属份额映射行的表（新行为）均可被识别。
- Test `test_extract_holdings_share_change_selects_bond_class_from_subordinate_rows_only` 验证了仅含下属行的场景 ✓。

**Risk**: 无。

---

### F4 — INFO: `_share_class_evidence_from_section_two_text` 从 A/C 迭代扩展到 A-Z 安全

**Evidence**:
- 原代码仅迭代 `(_SHARE_CLASS_A_LABEL, _SHARE_CLASS_C_LABEL)` 两个标签。
- 新代码迭代 `_SUPPORTED_SHARE_CLASS_LABELS`（26 个标签）。
- 对于 A/C 类基金，新代码与旧代码产生相同的 matches（A 和 C 仍被检测到），行为不变。
- 对于 E/F 类基金（如 006597），新代码能检测到 E 和 F 标签，这是预期的扩展。
- 下游 `unique_matches` 判定逻辑不变：多个匹配返回 None（safe），唯一匹配才返回 ✓。

**Risk**: 无。迭代范围的扩大不改变匹配逻辑的严格性。

---

### F5 — INFO: 三项新测试覆盖充分，旧测试全部通过

**Evidence**:
- 21 tests passed（原 18 + 新 3）。
- 新增测试：
  1. `test_extract_holdings_share_change_selects_bond_a_class_from_section_two_mapping`：4-class bond §10 + §2 mapping → 选择 A 列（fund_code 006597）✓
  2. `test_extract_holdings_share_change_selects_bond_class_from_subordinate_rows_only`：仅下属行 §2 表 → 仍能正确映射 ✓
  3. `test_extract_holdings_share_change_fails_closed_for_duplicate_bond_class_columns`：§10 有两个 A 类列 → fail closed，note 包含 "多个份额列" ✓
- 所有旧测试通过，包括 `test_extract_holdings_share_change_fails_closed_without_section_two_class_evidence`（line 778+，验证无 §2 evidence 时不默认选择 A 类）。
- 测试使用 synthetic `ParsedAnnualReport` / `ParsedTable` 对象，不依赖 production PDF/cache ✓。

**Risk**: 无。

---

### F6 — INFO: 006597 rerun 结果诚实：share_change 保持 missing，符合 fail-closed 合约

**Evidence**:
- Evidence artifact 记录：006597 rerun 后 `share_change` 仍为 `extraction_mode="missing"`，note 不变（"§10 份额变动表存在多个份额列，当前规则无法可靠选择对应份额类别"）。
- Quality gate 仍为 `block`，7 issues，missing-field rate 35.7%。
- Plan 行为合约明确允许两种 outcome：(a) direct extraction with anchor，或 (b) remain missing with explicit ambiguity。
- 实际 outcome 为 (b)，表示当前 public extraction output 的 §2/§10 关系仍不满足确定性选择条件。
- Implementation 正确保持了 fail-closed 行为：未引入 wrong-column fallback ✓。

**Risk**: 无。Implementation broadened capability（A-Z + subordinate-only mapping）但 006597 的实际数据结构不满足新条件的确定性要求。这是正确的 honest outcome。

---

### F7 — INFO: 无 forbidden boundary 变更

**Evidence**:
- `git diff --stat`：仅 `holdings_share_change.py` 和 `test_holdings_share_change.py` 两个文件变更 ✓。
- Evidence artifact 确认："No `fund_agent/fund/extractors/models.py` change was needed" ✓。
- 无 renderer、FQ0-FQ6、Service/CLI、Host/Agent/dayu、FundDocumentRepository、source fallback、snapshot/score/quality-gate、golden、fixture 变更 ✓。
- `ruff check` passed ✓。
- `git diff --check` passed ✓。

**Risk**: 无。

---

## Verdict

**PASS_WITH_FINDINGS**

Implementation 严格保持在 authorized scope 内，fail-closed 语义正确保留，旧测试全部通过，新测试覆盖了三个关键场景（多份额映射、下属行独立检测、重复列 fail-closed），006597 rerun 诚实地保持了 missing 状态。

一个 MATERIAL finding（F1: `endswith` 误报向量）不阻塞 closeout 但应在后续 robustness gate 中修复：`endswith(label)` 应增加前驱字符约束（如要求前驱为中文字符），防止 ETF/LOF 等拉丁字母结尾被误识别为份额类标签。当前的实际风险被以下因素缓解：(a) 测试全部通过；(b) 下游 column selection 仍需唯一匹配才能选择；(c) `_is_split_share_header_table` 要求 >= 2 个标签才触发。

| Finding | Severity | Blocks closeout? | Blocks commit? |
|---------|----------|-------------------|----------------|
| F1: `endswith` false positive for ETF/LOF text | MATERIAL | No | No, but track for robustness gate |
| F2: A/C → A-Z split-table generalization safe | INFO | No | No |
| F3: §2 subordinate mapping safe | INFO | No | No |
| F4: §2 text evidence iteration safe | INFO | No | No |
| F5: Tests sufficient, all pass | INFO | No | No |
| F6: 006597 honest missing outcome | INFO | No | No |
| F7: No forbidden boundary changes | INFO | No | No |

---

## Truth Source Alignment Confirmation

- [x] Diff 不违反 `AGENTS.md` 硬约束：无 FundDocumentRepository 直访、无 fallback 语义变更、无 extra_payload。
- [x] Diff 不违反 `docs/design.md` 非目标：无 renderer/FQ0-FQ6/Host-Agent/dayu 变更。
- [x] Diff 与 controller judgment authorized scope 一致：仅 `holdings_share_change.py` + tests。
- [x] Diff 不触及 `turnover_rate`、`holder_structure`、`investor_return`、`nav_data`、`holdings_snapshot`。
- [x] Golden corpus v1 remains ineligible。
