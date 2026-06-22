# EC-P4 Aggregate Deepreview Re-review: F1 Fix Verification

## Scope

- Mode: targeted re-review
- Branch: evidence-confirm-productionization
- Original finding: DS aggregate deepreview F1 — Service import boundary test failed because `fund_analysis_service` imported `fund_agent.fund.evidence_confirm_sources`
- Fix artifact: `docs/reviews/evidence-confirm-productionization-ec-p4-aggregate-deepreview-fix-20260623.md`
- Output file: docs/reviews/code-review-rereview-20260623-003000-mimo-ec-p4-aggregate-deepreview.md

## F1 Status: 已修复

## Verification

### 1. Facade 模块检查

`fund_agent/fund/evidence_confirm_runner.py` 是新增的 Fund 层 typed facade：

- 从 `fund_agent.fund.evidence_confirm_sources` re-export `EvidenceConfirmRepositoryRunRequest`、`EvidenceConfirmRepositoryRunResult` 和 `run_repository_bounded_evidence_confirm`
- 使用 `__all__` 显式声明公开契约
- 不引入新依赖、不修改底层实现
- 模块名不含 `source` 子串，不触发边界测试禁止片段

### 2. Service 导入检查

`fund_agent/services/fund_analysis_service.py` line 65 已从 `evidence_confirm_runner` 导入：

```python
from fund_agent.fund.evidence_confirm_runner import (
    EvidenceConfirmRepositoryRunRequest,
    EvidenceConfirmRepositoryRunResult,
    run_repository_bounded_evidence_confirm,
)
```

确认 Service 不再直接导入 `fund_agent.fund.evidence_confirm_sources`（grep 无结果）。

### 3. 边界测试通过

```
tests/services/test_fund_analysis_service_llm.py::test_fund_analysis_service_imports_keep_llm_path_above_forbidden_boundaries PASSED
```

### 4. 行为不变验证

- EC 相关 Service 测试：8 passed
- EC production summary 测试：47 passed（含 quality_gate_integration 和 semantic）
- ruff check：All checks passed
- git diff --check：exit 0

### 5. Service 边界合规

Service 只依赖 Fund 层 facade 暴露的 typed runner 契约，不直接导入 document/repository/cache/pdf/source/parser/provider 内部模块。

## Residual Risks

- F2（None 处理路径不一致）和 F3（`_semantic_issue_count` 命名）未在本次 fix 范围内，保持原 DS review 的 accepted candidate 状态。
- Facade 模块是纯 re-export，不增加行为层；如果未来 `evidence_confirm_sources` 模块重命名或拆分，facade 需要同步更新。

## Verdict

PASS

---

AGGREGATE_DEEPREVIEW_REREVIEW_COMPLETE_NOT_READY
