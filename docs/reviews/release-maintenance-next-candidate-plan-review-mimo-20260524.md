# Release Maintenance Next Candidate Plan Review — MiMo

> **审查对象**: `docs/reviews/release-maintenance-next-candidate-plan-20260524.md`
> **审查类型**: adversarial plan review
> **审查日期**: 2026-05-24
> **结论**: **PASS_WITH_FINDINGS**

---

## 审查依据

| 真源 | 核验结果 |
|------|----------|
| `AGENTS.md` | 四层 `UI -> Service -> Host -> Agent` 已确认；Host 必须 `dayu.host`，Agent 必须 `dayu.engine`；禁止 `extra_payload` 藏显式参数 |
| `docs/design.md` §1.3, §2.1, §2.2, §12 | 当前确定性主链路为 UI→Service→`fund_agent/fund`；无 `HostRun`/`AgentInput`/scene preparation；未接入前不空造 Host/Agent 包 |
| `docs/implementation-control.md` Startup Packet (line 28-30, 180-181) | 当前 gate=`release maintenance quality gate final judgment contract accepted locally`；下一入口=`ready for push authorization or next release-maintenance candidate selection`；两个候选：Host/Agent boundary decision（未选中）、Host/Agent dependency gate |
| 代码事实 | `fund_agent/host/` 和 `fund_agent/agent/` 不存在（`find` 确认）；`pyproject.toml` 无 dayu 引用（`grep` 确认） |

---

## 候选选择评估

计划选择 **Host/Agent boundary decision** 而非 dependency gate，理由充分：

1. **动机合理**：当前无具体 session/run/cancel/resume/outbox 或 runner/tool-loop/ToolTrace 需求，进入 dependency gate 会违反"不引入未使用依赖"的工程基线。
2. **与 Startup Packet 一致**：候选列表（line 180-181）明确列出两个选项，boundary decision 的描述"未选中具体 session/run 或 runner/tool-loop 需求前不得空造复杂框架"与计划动机吻合。
3. **scope 窄化得当**：只产出一个 review artifact，不触碰生产代码、依赖、包结构。

---

## 范围与守卫检查

| 检查项 | 结果 |
|--------|------|
| 不创建 `fund_agent/host` 或 `fund_agent/agent` 占位包 | ✅ 明确列为 Non-Goal 和不允许修改 |
| Host 如需落地必须使用 `dayu.host` | ✅ Decision Matrix 和 Future Gate Skeletons 均声明 |
| Agent 如需落地必须使用 `dayu.engine` | ✅ 同上 |
| 显式参数不隐藏在 `extra_payload` | ✅ Non-Goal、Stop Conditions 和 Review Gates 均声明 |
| pyproject/dayu-agent 基线纪律 | ⚠️ 见 Finding F1 |
| 不修改 source/test/config/README/design/control | ✅ 明确列出不允许修改的文件 |
| 不读 `docs/repo-audit-20260521.md` | ✅ Non-Goal 声明 |
| 不使用旧六层/Application/Runtime/Engine 口径 | ✅ Slice 1 明确排除 |

---

## Findings

### F1-未修复-中-dayu-agent pyproject baseline 缺乏具体核查路径

- **Plan 位置**: Direct Evidence 第 6 条；Slice 2 dependency gate trigger 第 2 点
- **问题类型**: 可操作性不足
- **计划当前写法**: "dependency bounds and package-data impact have been checked against current `dayu-agent` pyproject baseline"
- **为什么有问题**: `dayu-agent` 当前既非生产依赖也非可选依赖（`pyproject.toml` grep 无 dayu 引用）。计划未说明 baseline 指什么：是外部仓库 `dayu-agent` 的 `pyproject.toml`？是 `docs/design.md` §9.1 的工程基线表？还是其他文件？implementer 无法据此执行检查。
- **直接证据**: `pyproject.toml` 无 dayu 引用；`docs/design.md` §9.1 列出"Dayu-Agent 模块 / pyproject.toml / 代码导入"对照表，但标注 `dayu.host` 和 `dayu.engine` 均为"❌ 当前不声明"。
- **影响**: 后续 dependency gate 的触发条件模糊，implementer 不知道去哪里找 baseline、用什么命令验证。
- **建议改法和验证点**: 在 boundary decision artifact 中明确 baseline 定义——建议写为"以 `docs/design.md` §9.1 工程基线表和 `pyproject.toml` 当前 dependencies 为本地 baseline；如需对照外部 `dayu-agent` 仓库，必须先获取其 `pyproject.toml` 并记录版本/commit"。dependency gate trigger 应给出具体检查命令（如 `uv lock --check`、`grep -n "dayu" pyproject.toml`）。
- **修复风险（低/中/高）**: 低
- **严重程度（低/中/高/严重）**: 中

### F2-未修复-低-Decision Artifact 输出格式未提供模板结构

- **Plan 位置**: Selected Work Unit 第 2-5 点；Implementation Slices 全部
- **问题类型**: 可操作性不足
- **计划当前写法**: 列出 5 个决策问题（"当前是否继续确定性路径"、"何种需求打开 Host gate"、"何种需求打开 Agent gate"、"dependency gate 是否保持 blocked"、"最小契约/测试/文档/stop conditions"），但未给出 artifact 内部结构。
- **为什么有问题**: implementer 只知道要回答 5 个问题，不知道用什么格式组织——是否需要表格、代码块、章节标题？与现有 review artifacts（如 quality-gate-final-judgment-contract-plan）的格式是否一致？格式不一致会增加后续 review 的解析成本。
- **直接证据**: `docs/reviews/` 下有 180+ artifacts，格式多样；计划未引用任何一个作为格式参考。
- **影响**: implementer 可能产出格式不一致的 artifact，增加 controller 和 reviewer 的解析负担。
- **建议改法和验证点**: 建议在 Selected Work Unit 中给出最小章节骨架，例如：`## Direct Evidence` → `## Current-State Decision` → `## Host Gate Entry Criteria` → `## Agent Gate Entry Criteria` → `## Dependency Gate Status` → `## Future Gate Skeletons` → `## Stop Conditions` → `## Handoff Status`。或引用一个现有 artifact 作为格式参考。
- **修复风险（低/中/高）**: 低
- **严重程度（低/中/高/严重）**: 低

### F3-未修复-低-验证命令只能检查文本存在性

- **Plan 位置**: Slice 1、Slice 2、Slice 3 的 Tests / validation
- **问题类型**: 验证覆盖不足
- **计划当前写法**: 使用 `rg -n "关键词"` 检查 artifact 中是否包含特定术语。
- **为什么有问题**: `rg` 只能验证字符串出现，不能验证语义正确性。例如 artifact 可以包含 "no fund_agent/host or fund_agent/agent placeholder package" 这段文字，但实际决策可能是错的。对于纯文档 artifact，程序化验证本身有天然局限，但计划未说明哪些验证需要人工 review 覆盖。
- **直接证据**: Slice 1 验证命令 `rg -n "UI -> Service -> Host -> Agent|dayu.host|dayu.engine|extra_payload|pyproject|fund_agent/host|fund_agent/agent"` 只检查关键词。
- **影响**: 低。程序化验证 + plan review（本审查）+ 后续 code review 构成多层验证。但明确标注"程序验证只覆盖存在性，语义正确性由 plan review 覆盖"会更清晰。
- **建议改法和验证点**: 在每个 Slice 的 Tests / validation 小节末尾加一句："以上为程序化存在性检查；决策内容的语义正确性由 plan review gate 覆盖。"
- **修复风险（低/中/高）**: 低
- **严重程度（低/中/高/严重）**: 低

### F4-未修复-低-边界决策落地到真源的路径未显式声明

- **Plan 位置**: Docs Decision；Completion Report Format
- **问题类型**: 闭环缺失
- **计划当前写法**: "If the controller later accepts the decision and asks to update Startup Packet or design/control truth, that must be a separate controller-authorized docs/control update."
- **为什么有问题**: 计划产出一个 review artifact 中的决策，但决策如果被接受，如何回写到 `AGENTS.md`、`docs/design.md`、`docs/implementation-control.md` 等真源？Docs Decision 将此推迟到"后续独立 docs gate"，但 Completion Report Format 没有"Decision accepted → truth sources updated"这一行。这意味着决策可能永远停留在 review artifact 中，不被真源吸收。
- **直接证据**: `AGENTS.md` 硬约束："以代码为准，不让文档先于代码'设计未来'"；但 review artifact 中的决策记录不属于代码，也不属于真源文档。
- **影响**: 低。当前 gate 是 release maintenance，决策 artifact 的目的是为后续 gate 提供依据，不要求立即回写。但如果边界决策被接受，应有显式路径将其纳入真源。
- **建议改法和验证点**: Completion Report Format 增加一行 `Decision absorption path:`，要求 implementer 明确决策被接受后应更新哪些真源文件（如 `AGENTS.md`、`docs/implementation-control.md` Startup Packet）。
- **修复风险（低/中/高）**: 低
- **严重程度（低/中/高/严重）**: 低

### F5-未修复-低-Stop Conditions 缺少回退升级流程

- **Plan 位置**: Stop Conditions
- **问题类型**: 流程不完整
- **计划当前写法**: "Stop and return to controller if any of these occur:" + 6 个触发条件。
- **为什么有问题**: "return to controller" 是明确的中止行为，但未说明返回时应附带什么信息——是只说"触发了 Stop Condition X"，还是需要附带触发上下文、建议的 scope 调整、或替代方案？对于一个 review worker，停止并报告的格式应与 Completion Report Format 一样明确。
- **直接证据**: Completion Report Format 定义了 7 个字段；Stop Conditions 没有对应的报告格式。
- **影响**: 低。Controller 可以通过读取 review artifact 推断上下文，但显式的停止报告格式会减少沟通成本。
- **建议改法和验证点**: 在 Stop Conditions 末尾增加一个最小停止报告格式：`Triggered condition: / Context: / Suggested scope adjustment:`。
- **修复风险（低/中/高）**: 低
- **严重程度（低/中/高/严重）**: 低

---

## 总结

| 项目 | 结果 |
|------|------|
| 候选选择 | ✅ Host/Agent boundary decision 优于 dependency gate，动机充分 |
| Scope 窄化 | ✅ 只产出一个 review artifact，不触碰生产代码 |
| 占位包防护 | ✅ 不创建 `fund_agent/host` / `fund_agent/agent` |
| Dayu 四层约束 | ✅ Host=`dayu.host`，Agent=`dayu.engine` 均声明 |
| `extra_payload` 防护 | ✅ Non-Goal、Stop Conditions、Review Gates 三重声明 |
| pyproject 基线 | ⚠️ baseline 定义模糊（F1，中） |
| Artifact 格式 | ⚠️ 未提供模板结构（F2，低） |
| 验证覆盖 | ⚠️ 程序验证只覆盖存在性（F3，低） |
| 决策落地路径 | ⚠️ 未显式声明真源回写（F4，低） |
| Stop Condition 流程 | ⚠️ 缺少停止报告格式（F5，低） |

**结论**: **PASS_WITH_FINDINGS**。5 个 finding 中 1 个中等、4 个低。无 blocking finding。F1（dayu-agent baseline 定义）建议在 boundary decision artifact 实现时一并修复；F2-F5 为改进建议，不阻塞 handoff。

**残余风险**:
- 边界决策 artifact 如果格式不一致，后续 review 成本会略增。
- dayu-agent baseline 如果不澄清，dependency gate 触发时可能产生歧义。
- 纯文档决策如果不回写真源，可能在后续 phase 中被遗忘。
