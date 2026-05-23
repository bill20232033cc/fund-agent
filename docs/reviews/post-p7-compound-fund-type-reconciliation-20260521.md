# Post-P7 Compound Fund Type Reconciliation（2026-05-21）

## 背景

Repo-level deepreview 将“QDII/FOF 与指数/增强指数身份并存时被早返回吞掉”列为 post-P7 领域语义跟进项。

当前代码事实：

- `FundType` 稳定枚举为 `index_fund`、`active_fund`、`bond_fund`、`enhanced_index`、`qdii_fund`、`fof_fund`。
- `preferred_lens`、ITEM_RULE、extraction score 的 App 类别映射均按上述顶层标签工作。
- QDII/FOF 在现有设计中是产品顶层分类，而指数/增强指数可同时是产品身份或策略特征。

## 裁决

不新增复合类型，不把 QDII/FOF 指数产品改判为 `index_fund` 或 `enhanced_index`。

理由：

1. 新增复合类型会立即牵动模板 lens、质量评分、App 类别映射、风险阈值和 golden answer 契约，超过该 follow-up 的必要范围。
2. 将 QDII/FOF 指数产品改判为 `index_fund`/`enhanced_index` 会丢失海外/FOF 顶层产品属性，反而破坏 `preferred_lens` 的主路径。
3. 当前最小正确修复是保留顶层 `classified_fund_type`，并在 `classification_basis` 中记录并发指数/增强证据，供后续 lens 或人工复核使用。

## 代码收口

变更点：

- `fund_agent/fund/fund_type.py`
  - 新增 `_build_concurrent_index_basis(...)`。
  - QDII/FOF 命中后仍返回 `qdii_fund`/`fof_fund`。
  - 若同时命中指数身份或策略证据，则追加“同时命中指数基金身份或策略证据”。
  - 若同时命中增强关键词，则追加“同时命中增强关键词”。
- `tests/fund/extractors/test_profile.py`
  - 覆盖 QDII 增强指数产品：主类型保持 `qdii_fund`，basis 保留指数与增强证据。
  - 覆盖 FOF 指数产品：主类型保持 `fof_fund`，basis 保留指数证据。
- `fund_agent/fund/README.md`
  - 明确 QDII/FOF 是顶层分类标签，并发指数/增强身份进入 `classification_basis`，不引入复合类型。

## 验证

已运行：

```bash
pytest tests/fund/extractors/test_profile.py tests/fund/test_extraction_score.py tests/fund/template/test_contracts.py -q
```

结果：

```text
37 passed
```

## 后续残余风险

`classification_basis` 已能保留并发证据，但 renderer 当前尚未把该证据升级为章节 lens 或段落结构差异。若后续要让 QDII 指数、QDII 增强、FOF 指数在模板输出中有不同分析路径，应另起 design slice，统一扩展 `preferred_lens`、ITEM_RULE、风险阈值和 golden answer。
