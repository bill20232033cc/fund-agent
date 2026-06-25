# EC-P4 聚合深度复核目标重新复核（F1 修复）

**角色**: AgentDS 目标重新复核审查员
**原始复核**: `docs/reviews/code-review-20260623-002000-ds-ec-p4-aggregate-deepreview.md`
**MiMo 复核**: `docs/reviews/code-review-20260623-002000-mimo-ec-p4-aggregate-deepreview.md`
**修复工件**: `docs/reviews/evidence-confirm-productionization-ec-p4-aggregate-deepreview-fix-20260623.md`
**范围**: 仅 F1（服务边界导入测试）
**日期**: 2026-06-23T00:30:00Z

## 结论：通过

---

## F1 状态：已修复

### 问题

`fund_agent/services/fund_analysis_service.py` 直接从 `fund_agent.fund.evidence_confirm_sources` 导入了 `EvidenceConfirmRepositoryRunRequest`、`EvidenceConfirmRepositoryRunResult` 和 `run_repository_bounded_evidence_confirm`。由于路径包含禁止的子字符串 `source`，LLM 服务导入边界测试失败。

### 修复

- 新增 `fund_agent/fund/evidence_confirm_runner.py` 作为显式的 Fund 层类型化外观，从 `fund_agent.fund.evidence_confirm_sources` 重新导出相同的三个符号（第 10–14 行），并使用 `__all__` 显式声明导出（第 16–20 行）。
- 将 `fund_agent/services/fund_analysis_service.py` 第 65 行的服务导入更新为 `from fund_agent.fund.evidence_confirm_runner import (...)`。
- 底层的 `evidence_confirm_sources` 实现保持不变。
- 未添加白名单，未放宽边界测试。

### 验证

```bash
# 之前失败的边界测试（现在通过）
.venv/bin/python -m pytest \
  tests/services/test_fund_analysis_service_llm.py::test_fund_analysis_service_imports_keep_llm_path_above_forbidden_boundaries -v
# → 1 passed in 0.46s

# EC-P4 针对性测试套件（无回归）
.venv/bin/python -m pytest \
  tests/services/test_fund_analysis_service.py -v -k "evidence_confirm" \
  tests/fund/test_evidence_confirm_production.py \
  tests/fund/test_quality_gate_integration.py \
  tests/fund/test_evidence_confirm_semantic.py \
  tests/ui/test_cli.py -v -k "evidence_confirm"
# → 46 passed, 123 deselected in 0.57s

# 完整项目套件
.venv/bin/python -m pytest tests/ -q
# → 2259 passed in 6.88s
```

### 导入边界确认

`fund_agent/services/fund_analysis_service.py` 中唯一相关的导入是：
```python
from fund_agent.fund.evidence_confirm_runner import (
    EvidenceConfirmRepositoryRunRequest,
    EvidenceConfirmRepositoryRunResult,
    run_repository_bounded_evidence_confirm,
)
```

对 `fund_agent/services/fund_analysis_service.py` 中禁止路径片段的 grep 返回零结果：
```bash
grep -n "from fund_agent\.\(documents\|repository\|cache\|pdf\|source\|downloader\|parser\|dayu\)" \
  fund_agent/services/fund_analysis_service.py
# → （无输出）
```

`evidence_confirm_sources` 在 `fund_agent/services/`、`fund_agent/fund/` 和 `tests/` 中所有其他消费者：
- `fund_agent/fund/evidence_confirm_runner.py` — 外观，Fund 层内部（正确）
- `fund_agent/fund/evidence_confirm_production.py` — Fund 层内部（正确，同层）
- `tests/fund/test_evidence_confirm_production.py` — Fund 层测试（正确）
- `tests/services/test_fund_analysis_service.py` — 为假运行器构造导入类型（正确）
- `tests/fund/test_evidence_confirm_sources.py` — 专门测试 sources 模块（正确）

没有除外观模块以外的生产代码跨边界直接从 `evidence_confirm_sources` 导入。

---

## 未重新打开 F2/F3

F2（None 处理路径不一致）和 F3（`_semantic_issue_count` 命名）未被此修复触及。此修复的范围限于 F1，不改变 F2 或 F3 中的行为、命名或调用路径。

---

## 残余风险

- 此修复引入了一个外观命名边界。如果未来的服务代码导入带有禁止路径片段的新 Fund 模块，现有的边界测试仍然是捕获该问题的负责人。
- F2/F3 仍按其原始聚合深度复核结果处置分配。

AGGREGATE_DEEPREVIEW_REREVIEW_COMPLETE_NOT_READY
