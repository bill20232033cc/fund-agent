# P2-S9 Controller Judgment

## Gate

- 当前 gate：P2-S9 code review / fix / re-review
- controller：AgentController
- 设计真源：`docs/design.md`
- 总控文档：`docs/implementation-control.md`

## Reviewed Artifacts

- implementation：`docs/reviews/p2-s9-implementation-2026-05-18.md`
- MiMo code review：`docs/reviews/p2-s9-code-review-mimo-2026-05-18.md`
- GLM code review：`docs/reviews/p2-s9-code-review-glm-2026-05-18.md`
- fix：`docs/reviews/p2-s9-fix-2026-05-18.md`
- GLM re-review：`docs/reviews/p2-s9-rereview-glm-2026-05-18.md`

## Decision Summary

- MiMo review 结论：PASS，无阻断问题。
- GLM review 结论：FAIL，发现 1 个中严重度可见输出问题和 3 个低严重度问题。
- controller 裁决：
  - F-1 `dict_values(...)` 泄漏：accepted，必须修复。
  - F-2 第 4 章重复句号：accepted，随同修复。
  - F-3 README 重复过期 `template/` 条目：accepted，随同修复。
  - F-4 禁用词 substring 误报的潜在风险：deferred，作为 residual risk 记录，不阻断当前 MVP slice。
- GLM re-review 结论：PASS，F-1/F-2/F-3 均已修复并有回归测试；F-4 defer 无异议。

## Boundary Judgment

- `fund_agent/fund/template/renderer.py` 位于 Capability 层，只消费 P1/P2 结构化结果和显式输入，不读取年报文件、PDF、缓存、文档仓库、UI、Service、Runtime 或 Engine。
- `TemplateRenderInput` 显式声明 `StructuredFundDataBundle`、R=A+B-C、Alpha、言行一致性、投资者获得感、风险、压力测试、检查清单、最终判断和 `current_stage`，未使用 `extra_payload` 承载显式参数。
- 渲染输出固定覆盖 `docs/design.md` 第 3.1 节 0-7 共 8 章，并返回 `ProgrammaticAuditInput`，供 P1/P2/P3/L1/R1/R2 程序审计直接消费。
- 最终判断限制在 `worth_holding / needs_attention / suggest_replace`，渲染文本不输出买入、卖出、收益预测或仓位比例。
- 新增测试覆盖模板结构、证据锚点、审计兼容、缺失数据、最终判断边界、禁用交易措辞、F-1/F-2/F-3 回归。

## Validation

```bash
.venv/bin/python -m pytest tests/fund/template tests/fund/audit -q
# 18 passed

.venv/bin/python -m pytest tests/fund/analysis -q
# 40 passed
```

## Residual Risks

- F-4 deferred：`_validate_report_wording()` 当前仍使用 substring 匹配禁用词。未来模板若引入“买入前检查清单”等合法分析短语，可能误触发。当前报告不包含该短语，且该风险不阻断 P2-S9。
- 第 5 章“当前阶段与关键变化”仍只消费显式 `current_stage` 与净值记录数量；跨期年报对比需要后续 P3 或后续 phase 提供结构化输入。
- 证据锚点精度受 P1/P2 上游 `EvidenceAnchor` 完整性影响；缺少行定位时只能退化为年份 + 章节。

## Conclusion

P2-S9 implementation / code review / fix / re-review 已通过。当前 slice 可接受，下一 gate 为 `P2-S10 implementation + review`。
