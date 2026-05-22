# P19-S3 Plan Re-review Round 2（MiMo）

- **reviewed target**: `docs/reviews/p19-s3-valuation-state-integration-plan-20260523.md`
- **scope**: 只复审上一轮 MiMo finding `PR-MIMO-RR-001` 的修复；未修改生产代码或测试。
- **review timestamp**: `20260523`
- **conclusion**: `pass`

## Scope And Sources

本轮只验证两个问题：

1. disclaimer 示例是否已去除会触发 renderer `_FORBIDDEN_TERMS` 的禁用词。
2. 是否把“不触发 `_validate_report_wording()` 且不削弱禁用词 guard”纳入 renderer 验收。

直接读取：

- `docs/reviews/p19-s3-valuation-state-integration-plan-20260523.md`
- `docs/reviews/p19-s3-plan-rereview-mimo-20260523.md`
- `fund_agent/fund/template/renderer.py`

## Finding Closure Check

### PR-MIMO-RR-001: closed

上一轮问题是计划要求渲染的 disclaimer 示例包含“买入”，但当前 renderer 在 `_FORBIDDEN_TERMS` 中禁止 `买入`、`卖出`、`仓位比例`、`收益预测`，并在 `_validate_report_wording()` 中对报告全文命中禁用词抛 `ValueError`。

本轮计划已关闭该问题：

- disclaimer 示例已改为“仅供投资前风险检查参考”，不再包含当前 `_FORBIDDEN_TERMS` 的 `买入`、`卖出`、`仓位比例`、`收益预测`。
- 计划在 disclaimer 段落明确要求 rendered disclaimer 不得包含这些 forbidden trading-advice terms，并要求使用不会触发 `_validate_report_wording()` 的等价措辞。
- Renderer coverage 明确要求增加测试：disclaimer 不触发 `_validate_report_wording()`，且不削弱既有 `买入` / `卖出` / `仓位比例` / `收益预测` 禁用词校验。
- Test matrix 增加 `Renderer | disclaimer wording` 验收项：不包含 forbidden trading-advice terms 且不触发 `_validate_report_wording()`。
- Exit Criteria 增加验收：Rendered disclaimer wording avoids forbidden trading-advice terms and passes existing report wording validation without weakening the forbidden-term guard.

代码事实仍支持该验收边界：`fund_agent/fund/template/renderer.py` 中 `_FORBIDDEN_TERMS = ("买入", "卖出", "仓位比例", "收益预测")`，`_validate_report_wording()` 会在报告全文命中任一禁用词时抛出 `ValueError`。计划没有要求白名单或放宽该 guard。

## Residual Risk

实施 review 仍需核对实际 renderer 测试是否同时覆盖两类断言：合法 disclaimer 通过 `_validate_report_wording()`，以及包含 `买入` / `卖出` / `仓位比例` / `收益预测` 的报告仍失败。当前计划层面已把这两个点纳入验收。

## Final Plan Review Conclusion

`pass`

`PR-MIMO-RR-001` 已按上一轮建议修复。计划中的 disclaimer 示例不再触发当前 renderer 禁用词校验，并且 renderer 验收已明确要求“不触发 `_validate_report_wording()` 且不削弱 forbidden-term guard”。
