# P2 Full Retrospective Deepreview - Controller Judgment

> 日期：2026-05-19  
> 范围：`a86588e..54c9e99`  
> P2 起点：`a86588e phaseflow: close P1 and enter P2`  
> P2 复核终点：`54c9e99 P2 template renderer and evidence anchors`  
> 裁决：PASS，无 blocking finding；P2 gate 不需要重开。

## 1. 本轮复核口径

本轮是 P2 full retrospective deepreview，不替代历史逐片段 review，而是在 P2 起点到 `54c9e99` 的完整 diff 上重新验证：

- P2 是否满足 `docs/design.md` 和 `docs/implementation-control.md` 对 Fund capability、CHAPTER_CONTRACT、preferred_lens、审计规则、证据锚点的边界要求。
- 已有 review 结论是否仍成立。
- 新增复核是否发现未记录的 correctness、stability、maintainability 风险。

复核代码只读 worktree：

- `/Users/maomao/fund-agent-p2-retro-54c9e99`
- HEAD：`54c9e99`
- base：`a86588e`

## 2. 已有 review 证据

已有 review 主要覆盖 P2 分片实现和 P2 聚合验证：

- P2 各 slice review：覆盖 R=A+B-C、Alpha、投资者收益、风险检查、清单、模板渲染、程序化审计、README/控制文档同步。
- P2 aggregate review：覆盖 P2 终态一致性、测试状态、残余风险整理。
- PR #1 review：覆盖 P1/P2 合并进入 main 前的 draft PR gate。

这些历史 review 的共同结论是：P2 已达到 MVP gate 要求，无 blocking finding；仍存在若干 v2/维护期 residual risks，例如审计语义需要继续细化、部分证据锚点 granularity 仍可增强、模板标题和禁止词之间存在子串误报风险。

## 3. 新增复核结论

### AgentMiMo

产出物：

- `docs/reviews/p2-full-retrospective-deepreview-mimo-20260519-0004.md`

结论：

- Verdict：PASS
- Blocking findings：0
- 新增 finding：1 个 Low

新增低风险 finding：

- `_ratios.py` 直接测试不足。当前覆盖率统计显示 `_ratios.py` 为 63%，主要缺少 `parse_ratio` 数值输入、空值、无匹配分支，以及 `normalize_numeric_ratio` 对 `abs(value) <= 1` 分支的直接测试。该问题不改变 P2 gate 结论，但应进入后续 hardening。

### AgentGLM

产出物：

- `docs/reviews/p2-full-retrospective-deepreview-glm-20260518-2358.md`

结论：

- Verdict：PASS
- Blocking findings：0
- 新增 medium latent findings：5 个
- 新增 low findings：3 个
- 同时复述了历史 residual risks：模板禁止词子串误报、审计 evidence 粒度与标题匹配仍可增强。

新增 medium latent findings：

- 多处 runtime validation 使用 `assert`，在 `python -O` 下可能被剥离。当前调用路径已有前置缺失字段检查，暂不构成 P2 blocker，但属于后续应改成显式异常的代码质量风险。
- `parse_ratio` 对数值入参 `> 1` 自动除以 100，若调用方直接传 `Decimal("2.5")` 会产生语义歧义。当前生产调用主要来自字符串解析，暂不构成 P2 blocker。
- `judge_alpha_nature` 未去重同一 period 的重复观察，重复数据可能影响结构性/阶段性判断。当前默认构造路径没有主动制造重复 period，暂不构成 P2 blocker。
- `_structural_result` 的原因文本固定提到牛市/熊市覆盖，若未来配置关闭 `require_bull_and_bear_positive`，文案会与策略不一致。当前默认规则未受影响。
- `manager_tenure_months` 负数未显式拒绝，输出会出现负月份文案；当前会触发 veto，但展示语义不佳。

新增 low findings：

- `_issue()` 当前固定 `severity="blocker"`，`reviewable` 参数未实际使用。
- `observations_from_attributions` 对缺失 attribution 的 period 静默跳过，没有审计提示。
- 行业关键词 `"制造"` 可能匹配过宽。

## 4. Controller 复核验证

本地验证命令和结果：

- `git diff --check a86588e..54c9e99`：通过。
- `/Users/maomao/fund-agent/.venv/bin/python -m pytest tests/fund/analysis tests/fund/audit tests/fund/template -q`：`63 passed`。
- `/Users/maomao/fund-agent/.venv/bin/python -m pytest tests/fund/analysis tests/fund/audit tests/fund/template --cov=fund_agent.fund.analysis --cov=fund_agent.fund.audit --cov=fund_agent.fund.template --cov-report=term-missing -q`：`63 passed`，总覆盖率 91%。
- `rg "extra_payload" fund_agent/fund tests/fund`：P2 Fund capability 相关实现未发现显式参数被塞入 `extra_payload`。
- `rg "assert " fund_agent/fund/analysis fund_agent/fund/audit fund_agent/fund/template`：确认 GLM 关于 runtime `assert` 的 finding 属实。

额外 controller observation：

- R2 当前主要约束 red checklist 不应输出 `worth_holding`、green checklist 不应输出 `suggest_replace`。对 yellow/gray 与 `worth_holding` 的组合，当前实现会放行。由于 P2 设计和已有测试没有明确 yellow/gray 的强制映射，本轮不把它判定为 defect；建议作为 v2 审计策略语义澄清项处理。

## 5. 裁决

P2 full retrospective deepreview 结论为 PASS。

理由：

- 两个新增外部复核 AgentMiMo、AgentGLM 均给出 PASS，且没有 blocking finding。
- 新增 findings 都是 latent hardening、测试覆盖或语义精化问题，没有推翻 P2 的 MVP 行为正确性。
- 本地测试、coverage、diff check、边界检查均通过。
- 已有 residual risks 与新增 findings 可以进入 P3 后续 hardening 或 v2 backlog，不要求重开 P2 gate。

后续建议进入 backlog 的事项：

- 将 Fund capability 中 runtime `assert` 改成显式异常或显式 audit issue。
- 补齐 `_ratios.py` 的直接单元测试。
- 明确 R2 对 yellow/gray checklist 与最终判断的语义映射。
- 为 `judge_alpha_nature` 增加 duplicate period 防护或显式输入契约。
- 明确 `parse_ratio` 对数值型入参的百分比/小数语义。
