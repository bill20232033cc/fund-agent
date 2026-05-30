# Drawdown Stress NAV-Derived Metric Implementation — Re-Review (GLM)

日期：2026-05-29

角色：re-review worker only。未编辑文件、未 commit、未 push、未建 PR、未 merge、未运行破坏性命令。

Gate：`drawdown_stress NAV-derived metric contract / implementation gate`

---

## 0. Re-Review Scope

### 0.1 Prior Reviews

- GLM review：`docs/reviews/release-maintenance-drawdown-stress-nav-derived-metric-implementation-review-glm-20260529.md`
  - Verdict：Accepted / Pass
  - L1 (low severity)：`_derived_drawdown_metric_group` summary 硬编码 "2024"，应使用 `report.key.year` 动态拼接。
- MiMo review：`docs/reviews/release-maintenance-drawdown-stress-nav-derived-metric-implementation-review-mimo-20260529.md`

### 0.2 Controller-Accepted Fix

- 修复 L1：summary 使用 `report.key.year` 替换硬编码 "2024"。
- 新增测试：非 2024 年份（`year=2023`）的 summary 动态断言。
- Focused validation：ruff + pytest `test_bond_risk_evidence.py` 62 passed。

### 0.3 Re-Review Method

验证 L1 修复是否正确闭合，检查修复引入的 diff 是否产生新问题，确认核心实现（score/quality/golden/share-class/extractor IO）未被回归影响。不重做完整 review。

---

## 1. L1 Fix Verification

### 1.1 Production Fix

**Before**（GLM review 时）：

```python
summary="CSRC EID A 类累计净值路径计算 2024 年报期间最大回撤",
```

**After**（当前 diff）：

```python
summary=f"CSRC EID A 类累计净值路径计算 {report.key.year} 年报期间最大回撤",
```

`report.key.year` 来自 `ParsedAnnualReport.key`，是年报上下文的权威年份。`_derived_drawdown_metric_group(report, drawdown_metric)` 已持有 `report` 参数，无需新增依赖。修复正确、最小。

### 1.2 Test Fix

**新增测试**：`test_nav_derived_drawdown_metric_summary_uses_report_year`

- 构造 `year=2023` 的 `_build_report`（通过新增 `year` 参数，默认 `2024`）。
- 传入相同的 `_drawdown_metric()` fixture（period 仍为 2024）。
- 断言 `group.summary == "CSRC EID A 类累计净值路径计算 2023 年报期间最大回撤"`。

该测试证明 summary 来自年报上下文而非 metric period 或硬编码值。非 2024 年份正确覆盖。

**Helper 变更**：`_build_report` 新增 `year: int = 2024` 关键字参数，默认值保持向后兼容。`DocumentKey` 使用 `year=year` 替代硬编码 `year=2024`。

**现有测试 `test_nav_derived_drawdown_metric_satisfies_drawdown_group`**：新增 `assert group.summary == "CSRC EID A 类累计净值路径计算 2024 年报期间最大回撤"`，确认 2024 默认路径 summary 仍然正确。

### 1.3 L1 Closure Status

**Closed。** 硬编码 "2024" 已替换为 `report.key.year`，动态年份测试覆盖非 2024 场景。

---

## 2. Regression Check

### 2.1 Touched Files

仅 `bond_risk_evidence.py` 和 `test_bond_risk_evidence.py` 被修改。未触及 `data_extractor.py`、`extraction_snapshot.py`、`extraction_score.py`、`quality_gate.py`、`nav_metrics.py`、`models.py` 或 golden fixtures。

### 2.2 Fix Scope Analysis

修复涉及的生产代码仅一行（summary 字符串格式化）。`_build_group_anchors`、anchor note、metric_value、period_label、status/strength/measurement_kind、fail-closed 逻辑均未变动。

### 2.3 Core Invariants Confirmed

| 不变量 | 状态 |
|---|---|
| Score / quality gate / golden 未被弱化 | 未触及，确认 |
| Share-class 不混合（仅 A） | 未触及，确认 |
| Extractor 不执行 IO | 未触及，确认 |
| 弱文本不提升为定量 | 未触及，确认 |
| Fail-closed 行为不变 | 未触及，确认 |
| Contract extension 语义不变 | 未触及，确认 |
| Anchor provenance 不变 | 未触及，确认 |

### 2.4 New Issues Introduced by Fix

无。`_build_report` 的 `year` 参数有默认值 `2024`，不影响任何现有测试。`_drawdown_metric()` fixture period 仍为 2024-01-01..2024-12-31，与 `report.key.year` 解耦的测试恰好验证了 summary 使用的是年报年份而非 metric period 年份。

---

## 3. Validation Evidence Verification

Controller reported：

- `ruff check bond_risk_evidence.py + test_bond_risk_evidence.py`：All checks passed。
- `pytest test_bond_risk_evidence.py -q`：62 passed（原 61 + 1 新增）。

测试计数增量与新增的 `test_nav_derived_drawdown_metric_summary_uses_report_year` 一致。

---

## 4. Verdict

**Accepted。**

L1 已正确闭合，无新问题引入。核心实现不变。

---

## 5. Self-Check

pass。

- 角色合规：仅做 re-review，未编辑代码、未 commit、未 push、未运行破坏性命令。
- 范围合规：仅审查 L1 修复 diff 和回归风险。
- Verdict 明确：Accepted。
