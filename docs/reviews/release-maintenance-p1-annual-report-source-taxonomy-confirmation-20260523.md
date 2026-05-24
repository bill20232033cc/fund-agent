# Release Maintenance P1 Confirmation — Annual Report Source Failure Taxonomy And Provenance

## 结论

状态：accepted locally / current-state satisfied

`docs/reviews/controller-judgment-repo-deepreview-20260523.md` 中的 P1 finding “年报来源错误分类与 fallback 追溯不足”当前已经由现有实现满足，无需再做代码修改。

## 核验证据

- `fund_agent/fund/documents/sources.py` 定义了显式失败分类：
  - `not_found`
  - `unavailable`
  - `schema_drift`
  - `identity_mismatch`
  - `integrity_error`
- `AnnualReportSourceOrchestrator` 只允许 `not_found` / `unavailable` 继续 fallback。
- `identity_mismatch`、`schema_drift`、`integrity_error` 会抛出 `AnnualReportSourceFallbackBlockedError`，并保留：
  - 已发生的逐来源 failure 列表
  - blocking failure
  - 原始异常 cause
- fallback 命中会通过 `AnnualReportSourceMetadata.fallback_used=True` 持久标记。
- 来源 metadata 会经 `AnnualReportPdfFetchResult`、`FundDocumentRepository` 和 `AnnualReportDocumentCache` 写入 parsed report / PDF cache provenance。
- eligible 失败耗尽时保留最终异常语义：纯 not_found 才返回 not-found；unavailable 或 mixed failure 不会被误报为 not-found。

## 验证

- `pytest tests/fund/documents/test_annual_report_sources.py -q`：35 passed
- `pytest tests/fund/documents/test_repository.py -q`：17 passed
- `pytest tests/fund/documents/test_cache.py -q`：14 passed
- `ruff check fund_agent/fund/documents tests/fund/documents`：passed

## 裁决

基于 `AGENTS.md` 的年报来源 fallback 硬约束和 `docs/design.md` 的文档仓库边界，当前实现已经满足：

- 年报访问仍只通过 `FundDocumentRepository` 对外暴露。
- 年报来源编排是 Fund Capability documents 层内部实现。
- fallback 决策按失败类别显式执行。
- fail-closed 类别不会被 Eastmoney fallback 静默掩盖。
- fallback provenance 可随 parsed report 进入缓存和后续结构化链路。

因此本 finding 关闭为 current-state satisfied。剩余 source 相关工作只保留低风险生产硬化项，不阻塞当前 release maintenance gate。

## 残余风险

- 当前确认不新增真实网络 smoke test；真实 EID/Eastmoney 可用性仍属于生产监控或专门 live validation。
- 外部 I/O timeout、并发写保护、重复表格解析等稳定性问题仍按 P2 backlog 单独跟踪，不混入本次语义确认。
