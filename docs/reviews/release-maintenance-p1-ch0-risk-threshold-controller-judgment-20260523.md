# Release Maintenance P1 Controller Judgment — Chapter 0 Risk And Threshold Slots

## 结论

状态：accepted locally

本轮修复接受。第 0 章“当前最大的风险”和“什么变化会升级、降级或终止当前动作”不再在已有结构化输入可用时输出 blanket insufficiency placeholder，而是按风险检查、检查清单、压力测试和最终判断原因生成可验证的动作阈值。

## 范围

- Handoff：`docs/reviews/release-maintenance-p1-ch0-risk-threshold-handoff-20260523.md`
- 实现文件：`fund_agent/fund/template/renderer.py`
- 测试文件：`tests/fund/template/test_renderer.py`
- 文档同步：`fund_agent/fund/README.md`、`tests/README.md`

未修改：

- GitHub remote state
- 未跟踪历史输入文件
- 年报文档仓库、Service、Engine 或 UI 边界

## 已接受实现

- 第 0 章最大风险 slot 的优先级改为：
  - 首个 `risk_check_result.veto_items`
  - 首个 `risk_check_result.watch_items`
  - 首个压力测试 `near_limit` / `beyond_tolerance` 场景
  - 全部通过时输出基于 `overall_status` 的无否决说明
- 第 0 章动作阈值 slot 改为消费结构化信号：
  - 风险项升级目标为 `pass`
  - 检查清单升级目标为 `green/pass`
  - 压力测试升级目标为 `within_tolerance`
  - 全绿通过时仍输出后续监控阈值
- 保留最终判断约束，不输出买入、卖出、仓位或收益预测措辞。

## Review Findings 处理

专项 review 初始结论为 `PASS_WITH_FINDINGS`，发现三个问题：

- 压力测试升级阈值不能套用 `green/pass`。已改为 `within_tolerance`。
- 最大风险不能只看 risk check，否则 stress-only near-limit 会被渲染为无风险。已加入压力测试 fallback。
- 旧 placeholder 回归保护不完整。已新增覆盖 veto、watch、checklist warning、stress-only、all-green 的参数化回归测试。

复核后未发现新的边界冲突。

## 验证

- `pytest tests/fund/template/test_renderer.py -q`：50 passed
- `pytest tests/fund/audit/test_audit_programmatic.py -q`：49 passed
- `pytest tests/fund/integration/test_p3_cli_e2e_matrix.py -q`：2 passed
- `ruff check fund_agent/fund/template/renderer.py tests/fund/template/test_renderer.py fund_agent/fund/README.md tests/README.md`：passed
- `git diff --check`：passed

## 残余风险

- 当前 renderer 仍是确定性模板填充，不提供 LLM 语义审计结论。
- 第 0 章阈值来自现有结构化结果，不能替代 Evidence Confirm 对证据锚点内容的事实复核。
- 本地提交尚未推送到远端，draft PR gate 仍需用户授权后执行。
