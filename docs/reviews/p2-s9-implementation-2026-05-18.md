# P2-S9 Implementation - Template Renderer

## Gate

- 当前 gate：P2-S9 implementation + review
- 执行角色：AgentCodex implementation worker
- 停止边界：不提交、不推送、不创建 PR，不进入其他 gate

## Scope

- 实现 Capability 层模板渲染器，把 P1/P2 结构化结果填充为完整 8 章 Markdown 报告
- 生成可直接传给 `run_programmatic_audit` 的结构化审计输入
- 同步 Fund 包 README 的当前 API 与边界说明
- 补充模板渲染器单元测试

## Changed Files

- `fund_agent/fund/template/renderer.py`
- `fund_agent/fund/template/__init__.py`
- `tests/fund/template/test_renderer.py`
- `fund_agent/fund/README.md`
- `docs/reviews/p2-s9-implementation-2026-05-18.md`

## Implementation Summary

- 新增 `TemplateRenderInput`，显式聚合：
  - `StructuredFundDataBundle`
  - `RabcAttribution`
  - `AlphaJudgment`
  - `ConsistencyCheckResult`
  - `InvestorExperienceResult`
  - `RiskCheckResult`
  - `StressTestResult`
  - `ChecklistResult`
  - `final_judgment`
  - 可选 `current_stage`
- 新增 `TemplateRenderResult`，输出：
  - `report_markdown`
  - `audit_input`
  - `evidence_anchors`
- 新增 `render_template_report(...)`：
  - 固定渲染设计文档第 3.1 节的 0-7 共 8 章
  - 渲染章节内证据行 `> 📎 证据：年报§...`
  - 渲染附录 `## 证据与出处`
  - 缺失数据显式写为“未披露”或“数据不足”
  - 最终判断只允许 `worth_holding`、`needs_attention`、`suggest_replace`
  - 报告文本禁止出现买入、卖出、收益预测、仓位比例等交易建议措辞
- 新增 `build_programmatic_audit_input(...)`，从渲染结果提取程序审计输入。

## Validation Commands / Results

- `.venv/bin/python -m pytest tests/fund/template -q`
  - 结果：7 passed
- `.venv/bin/python -m pytest tests/fund/template tests/fund/audit -q`
  - 结果：16 passed

## Docs Decision

- 已更新 `fund_agent/fund/README.md`
- 更新范围只覆盖当前已实现的 template renderer API、输出、边界与目录定位
- 未修改 `docs/design.md` 和 `docs/implementation-control.md`，因为模板章节结构和 gate 状态未在本 slice 内变更

## Residual Risks

- 当前渲染器是 MVP 模板填充，不做 LLM 写作，因此段落表达偏结构化。
- 当前第 5 章“当前阶段与关键变化”只消费显式 `current_stage` 与现有净值记录数量，跨期年报变化仍需后续 slice 提供结构化输入。
- 证据锚点依赖 P1/P2 结构化结果携带的 `EvidenceAnchor`；缺少行定位时按要求保留年份和章节，但精确到行的复核能力受上游抽取影响。

## Stop Status

- 实现已完成
- 指定联合验证已通过
- 停止在 P2-S9 implementation + review，不进入下一 gate
