# Drawdown Stress NAV-Derived Metric Implementation Rereview — MiMo

日期：2026-05-29

角色：re-review worker only。不编辑、不 commit、不 push、不 PR、不 merge。

## Reviewed Fix

GLM L1: `_derived_drawdown_metric_group` 的 `summary` 字段硬编码 `2024`，应改为使用 `report.key.year` 动态年份。

## Fix Verification

### 代码变更

`bond_risk_evidence.py:602`:

```python
# 修复前（推断）:
summary="CSRC EID A 类累计净值路径计算 2024 年报期间最大回撤"

# 修复后:
summary=f"CSRC EID A 类累计净值路径计算 {report.key.year} 年报期间最大回撤"
```

`report.key.year` 来自 `ParsedAnnualReport.key: DocumentKey`，由上游 `FundDataExtractor.extract(fund_code, report_year)` 传入。正确。

### 测试覆盖

新增测试 `test_nav_derived_drawdown_metric_summary_uses_report_year`:

- 构造 `year=2023` 的年报 fixture。
- 调用 `extract_bond_risk_evidence(report, "bond_fund", drawdown_metric=_drawdown_metric())`。
- 断言 `group.summary == "CSRC EID A 类累计净值路径计算 2023 年报期间最大回撤"`。

`_build_report` helper 新增 `year: int = 2024` 参数，默认值保持原有测试兼容。

### 回归验证

- `uv run pytest tests/fund/extractors/test_bond_risk_evidence.py -q` → **62 passed**（原 61 + 1 新测试）。
- 其他引用 `report.key.year` 的位置（`anchor_id`、`document_year`、其他 `period_label`）均为已有动态引用，未受影响。

### 核心实现回归检查

| 检查项 | 状态 |
|---|---|
| score/quality gate/golden 未弱化 | ✓（fix 只改 summary 字符串模板） |
| 无 share-class 混合 | ✓（fix 不涉及 NAV 加载逻辑） |
| 无 extractor IO | ✓（fix 不引入新依赖） |
| contract extension 未变 | ✓（fix 不涉及 models.py） |
| fail-closed 行为未变 | ✓（fix 不涉及错误处理路径） |

## Verdict

**accepted**

GLM L1 已正确关闭。`summary` 从硬编码 `2024` 改为 `report.key.year` 动态引用，新测试覆盖非 2024 年份场景，62 测试全部通过，无回归。
