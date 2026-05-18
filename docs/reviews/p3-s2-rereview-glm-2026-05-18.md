# P3-S2 Re-Review (GLM)

Date: 2026-05-18
Gate: P3-S2 re-review
Reviewer: AgentGLM
Scope: Verify accepted fix for GLM F3 / MiMo INFO F3 only — all-market parsing degree-preference and Celsius sign support.

---

## Fix Verification

### GLM F3: `_decimal_after_labels` 理论误匹配风险

**原问题**: `_parse_market_temperature` 先调用 `_decimal_after_labels`，当标签附近有非温度数字（如"1234 只基金"）时会误取该数字。

**修复**: `thermometer.py:338` — 调用顺序改为 `_degree_after_heading(...) or _decimal_after_labels(...)`。度数标记匹配现在优先，无标记的纯数字回退仅在无度数符号时触发。

**验证**: `thermometer.py:618` — `_degree_after_heading` 正则已从 `([-+]?\d+(?:\.\d+)?)\s*°` 改为 `([-+]?\d+(?:\.\d+)?)\s*(?:°|℃)`，同时接受度数符号和摄氏符号。

**新增测试**: `test_parse_thermometer_pages_prefers_degree_market_value_over_nearby_number` — 构造"全市场温度...1234 只基金...70℃"场景，断言 `market.value == Decimal("70")`，直接覆盖了 GLM F3 描述的误匹配路径。

**结论**: 已修复。度数符号优先策略消除了附近非温度数字的误匹配风险。Celsius 符号支持扩展了页面布局兼容性。

---

## Regression Check

- 原有 `test_parse_thermometer_pages_parses_current_market_degree_layout` 使用 `70°` 仍通过 — 度数符号路径未退化。
- 13 passed（thermometer tests），60 passed（broader regression）。`git diff --check` clean。
- `test_thermometer_adapter_fetches_and_parses_market_indexes_and_macro` 使用冒号式 `"全市场温度：32.5"` — 当 `_degree_after_heading` 未命中时回退到 `_decimal_after_labels`，冒号式路径未退化。

---

## Scope Exclusion

本 re-review 仅覆盖 GLM F3 / MiMo INFO F3 的修复。GLM F1（valuation_band 回退范围）和 F2（as_of_text 无标签回退）仍为 low-severity open findings，不在本次 fix scope 内。

---

## Verdict

**PASS**

修复正确且最小化：仅调整了解析优先级（2 行）和扩展了度数符号字符类（1 行），新增 1 个针对性测试。无回归，无新增风险。
