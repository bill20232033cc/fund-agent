# P2-S6 Code Review Controller Judgment

> 日期：2026-05-17
> Controller：Codex
> Phase / Slice：P2 / P2-S6 压力测试
> Implementation artifact：`docs/reviews/p2-s6-implementation-2026-05-17.md`

## 1. 裁决前提

- 当前实现新增：
  - `StressTestRule`
  - `StressScenarioResult`
  - `StressTestResult`
  - `run_stress_test(...)`
- controller 本地边界检查确认：
  - 压力测试仍位于 `fund_agent/fund/analysis/risk_check.py`
  - 模块不读取 PDF、缓存文件、文档仓库或文件系统数据
  - 基金类型由上游显式传入，符合“基金类型判断优先于通用分析”
  - 投入金额和最大可承受亏损比例均为显式参数，未放入 `extra_payload`
  - 缺少最大可承受亏损比例时返回 `not_provided`，不强行判定能否承受
- 外部 reviewer 尝试：
  - `ai:review.0` / MiMo：已读取文件并执行测试、ruff，但 Claude hook/思考状态卡住，未产出 artifact
  - `roles:glm_claude.0` / GLM：已派发任务，但 Claude hook/思考状态卡住，未产出 artifact
  - 裁决：两者均不能作为 accepted independent review 依据；本 slice 暂按 controller review 收口
- controller 本地验证：

```bash
.venv/bin/python -m pytest tests/fund/analysis -q
.venv/bin/python -m ruff check fund_agent/fund/analysis tests/fund/analysis
```

结果：

```text
34 passed
All checks passed!
```

## 2. Accepted Findings

### A1-已防护-中-缺少用户承受能力时可能被误判为可承受

- **来源**：controller 自查
- **裁决**：`accepted`
- **原因**：
  - 最大可承受亏损比例是用户侧显式输入，不应由分析模块猜测
  - 若缺失时默认为可承受，会直接削弱模板第 6 章的安全阀作用
- **修复**：
  - `max_tolerable_loss_rate=None` 时每个场景输出 `capacity_status="not_provided"`
  - 下一步最小验证问题要求先补充最大可承受亏损比例
  - 单元测试覆盖缺失承受能力路径

### A2-已防护-中-压力等级阈值可能脱离基金类型 preferred_lens

- **来源**：controller 自查
- **裁决**：`accepted`
- **原因**：
  - 模板第 6 章明确要求不同基金类型使用不同压力测试阈值
  - 债券基金与 QDII 等类型不能共用权益基金阈值
- **修复**：
  - `StressTestRule` 通过 `severity_thresholds` 按 `FundType` 配置阈值
  - 默认阈值与 `docs/fund-analysis-template-draft.md` 第 6 章一致
  - 单元测试覆盖主动基金、债券基金和自定义阈值配置

### A3-已防护-低-固定场景与等级阈值容易混淆

- **来源**：controller 自查
- **裁决**：`accepted`
- **原因**：
  - `docs/design.md` 第 4.5 节要求模拟 `-20%/-40%/-60%`
  - 模板第 6 章同时定义基金类型阈值，二者职责不同
- **修复**：
  - 固定场景由 `_DEFAULT_STRESS_SCENARIOS` 表达
  - 压力等级由 `_DEFAULT_STRESS_THRESHOLDS` 表达
  - artifact 和 README 明确二者差异

## 3. Deferred Findings

### D1-未修复-中-检查清单尚未消费压力测试输出

- **裁决**：`deferred-with-owner`
- **Owner / Destination**：`P2-S7`
- **原因**：
  - P2-S7 是检查清单引擎 slice，负责把分析结果转成 7 问题红/黄/绿灯

### D2-未修复-中-压力测试与报告文字一致性尚未审计

- **裁决**：`deferred-with-owner`
- **Owner / Destination**：`P2-S8`
- **原因**：
  - P2-S8 才实现程序审计，当前只冻结压力测试计算契约

### D3-未修复-低-独立 reviewer 未产出可采纳 artifact

- **裁决**：`deferred-with-owner`
- **Owner / Destination**：`P2 aggregate review`
- **原因**：
  - 本次外部 reviewer 卡在 Claude hook/思考状态，未写入 review artifact
  - aggregate review gate 仍必须至少取得两份独立 review，或记录用户接受单 reviewer 风险

## 4. 当前 Gate 结论

- `P2-S6 controller code review` 结论：`pass`
- 当前没有 blocker
- `P2-S6` 可推进到下一 gate：`P2-S7 implementation + review`
