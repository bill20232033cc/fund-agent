# Re-Review: Share-Change Focused Implementation (F1 Fix)

> **Reviewer**: AgentGLM (independent code reviewer)
> **Date**: 2026-05-27
> **Review scope**: targeted re-review of F1 (`endswith` false positive) fix against original review `docs/reviews/release-maintenance-share-change-focused-implementation-review-glm-20260527.md`
> **Diff**: uncommitted changes to `holdings_share_change.py` + `test_holdings_share_change.py`
> **Focus**: F1 fix correctness, ETF/LOF/NAV negative test coverage, Chinese suffix positive test coverage, no scope drift

---

## F1 Fix Verification

### Fix mechanism

Original F1 identified: `_contains_share_class_label` 的 `endswith` 检查对拉丁字母结尾的非份额类文本存在误报向量（如 "沪深300ETF" → endswith("F") → True）。

Fix: 新增 `_endswith_bare_share_class_label`（holdings_share_change.py:941-960），在 `endswith(class_label)` 匹配后增加前驱字符约束：

```python
prefix = text[: -len(class_label)]
if not prefix:
    return False
return not prefix[-1].isascii() or not prefix[-1].isalpha()
```

**逻辑分析**：

| 输入文本 | label | prefix | prefix[-1] | isascii | isalpha | 结果 | 正确? |
|----------|-------|--------|------------|---------|---------|------|-------|
| "沪深300ETF" | "F" | "沪深300ET" | "T" | True | True | False (不匹配) | ✓ |
| "场内LOF" | "F" | "场内LO" | "O" | True | True | False (不匹配) | ✓ |
| "累计NAV" | "V" | "累计NA" | "A" | True | True | False (不匹配) | ✓ |
| "国泰利享中短债债券A" | "A" | "国泰利享中短债债券" | "券" | False | — | True (匹配) | ✓ |
| "债券E" | "E" | "债券" | "券" | False | — | True (匹配) | ✓ |
| "1A" | "A" | "1" | "1" | True | False | True (匹配) | ✓ (数字前驱合理) |
| "A" (bare) | "A" | "" | — | — | — | False (空 prefix) | ✓ |

Fix 精确实现了原始 F1 recommendation 的前驱字符约束，排除了拉丁字母前驱的误报路径 ✓。

---

### Test coverage for F1 fix

两项新测试覆盖了原始 F1 描述的全部误报向量：

**Test 1**: `test_extract_holdings_share_change_does_not_treat_etf_lof_nav_suffixes_as_share_classes`
- Fixture `_english_suffix_header_table`：headers = ("项目", "目标ETF", "场内LOF", "累计NAV")
- 验证：ETF→F、LOF→F、NAV→V 均不触发份额类识别 → `_table_share_class_label_count == 0` → 不被误判为 split header table → extraction_mode="missing"
- 该测试在旧代码（无前驱约束）下会失败：ETF→F + NAV→V → count=2 → `_is_split_share_header_table` 返回 True → 可能产生错误抽取。新代码正确返回 missing ✓

**Test 2**: `test_extract_holdings_share_change_ignores_etf_suffix_but_keeps_chinese_fund_name_suffix`
- Fixture `_share_change_table_with_etf_and_bond_a_headers`：headers = ("项目", "目标ETF", "国泰利享中短债债券A")
- 验证：ETF 被忽略（"T" 为拉丁字母前驱），"债券A" 被正确识别（"券" 为中文字符前驱）→ 唯一匹配 A 类 → 通过 §2 evidence 选择 "国泰利享中短债债券A" 列
- 该测试验证了混合场景下的正负行为同时正确 ✓

ETF、LOF、NAV 三种典型英文后缀的负例 + 中文基金名后缀的正例均已覆盖 ✓。

---

### Regression check

23 tests passed（原 21 + 新 2），全部通过 ✓。

- 5 项原有 share-change tests（split-table、multi-class、total-share、other-code、ambiguity）均未回归 ✓
- 3 项 bond share-class tests（§2 mapping、subordinate-only、duplicate fail-closed）均未回归 ✓
- `ruff check` passed ✓
- `git diff --stat`：仅 2 个 authorized 文件变更 ✓

---

### Scope drift check

| 检查项 | 结果 |
|--------|------|
| 新增 `_endswith_bare_share_class_label` 函数 | 在 `holdings_share_change.py` 内，authorized scope ✓ |
| `_contains_share_class_label` 修改 | 仅替换 endswith 调用为新函数，authorized scope ✓ |
| 新增 2 个 test fixture | 在 `test_holdings_share_change.py` 内，authorized scope ✓ |
| 新增 2 个 test case | 在 `test_holdings_share_change.py` 内，authorized scope ✓ |
| 触及 models.py | 否 ✓ |
| 触及 renderer/FQ0-FQ6/Service/CLI/Host/Agent/dayu | 否 ✓ |
| 触及 FundDocumentRepository/source fallback | 否 ✓ |
| 触及 golden/fixture/package config | 否 ✓ |
| 语义变更（fail-closed → fallback） | 否，仅收窄 false positive 向量 ✓ |

无 scope drift ✓。

---

## Verdict

**PASS**

F1 修复精确到位：前驱字符约束 `not prefix[-1].isascii() or not prefix[-1].isalpha()` 完全消除了 ETF/LOF/NAV 等拉丁字母结尾的误报向量，同时保持中文字符前驱的正例匹配。两项新测试分别覆盖了纯英文后缀负例和混合 ETF+中文后缀场景。23 tests 全部通过，无 scope drift。

原始 review 中 F1 是唯一 MATERIAL finding。F1 修复后，原始 review 剩余 6 项 INFO findings 均不涉及代码问题，无需追加检查。

| Previous Finding | Status |
|-----------------|--------|
| F1: `endswith` false positive for ETF/LOF text | **RESOLVED** — `_endswith_bare_share_class_label` 前驱字符约束 + 2 项新测试 |
| F2: A/C → A-Z generalization safe | Unchanged INFO, no regression |
| F3: §2 subordinate mapping safe | Unchanged INFO, no regression |
| F4: §2 text evidence iteration safe | Unchanged INFO, no regression |
| F5: Tests sufficient, all pass | Updated — now 23 passed |
| F6: 006597 honest missing outcome | Unchanged INFO |
| F7: No forbidden boundary changes | Confirmed — still only 2 authorized files |

---

## Truth Source Alignment Confirmation

- [x] Diff 不违反 `AGENTS.md` 硬约束：无 FundDocumentRepository 直访、无 fallback 语义变更、无 extra_payload。
- [x] Diff 不违反 `docs/design.md` 非目标：无 renderer/FQ0-FQ6/Host-Agent/dayu 变更。
- [x] Diff 与 controller judgment authorized scope 一致：仅 `holdings_share_change.py` + tests。
- [x] Diff 不触及 `turnover_rate`、`holder_structure`、`investor_return`、`nav_data`、`holdings_snapshot`。
