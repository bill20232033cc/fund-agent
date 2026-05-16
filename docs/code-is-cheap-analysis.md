# code-is-cheap 深入分析报告

> 项目地址：https://github.com/noho/code-is-cheap
> 许可证：Apache-2.0
> 分析日期：2026-05-15

---

## 一、项目定位与核心理念

**code-is-cheap** 是一个**面向 AI 编码的工程控制框架**，而非松散的 prompt 集合。它的核心哲学是：

> **"先准备好架构、阶段边界、准入/准出标准和实施控制计划，然后让 controller agent 自动推进每个阶段，直到本地分支达到 `ready-to-create-PR`。"**

项目名称本身就传达了理念——**代码是廉价的，工程控制才是昂贵的**。它不试图让 AI 自由发挥去"发明"架构，而是把 AI 编码放入一个严格的工程循环中：裁决设计与计划 → 按切片实施 → 审查代码 → 修复发现 → 复审 → 聚合深度审查 → 跟踪残余风险 → 创建本地验收提交。

---

## 二、工作原理

### 2.1 整体架构

项目由 **5 个核心 Skill** 组成，形成分层编排体系：

```
phaseflow（项目级 Phase 总控）
  └── gateflow（单次工作单元的 Gate 编排控制器）
        ├── planreview（计划对抗性审查）
        ├── deepreview（深度代码审查）
        └── init-agents（多 Agent 通信初始化）
```

### 2.2 技能文件结构

每个 skill 遵循统一结构：

```
skills/<skill-name>/
  SKILL.md          # 核心指令文件（YAML frontmatter + Markdown 正文）
  agents/openai.yaml # Agent 运行时接口配置（display_name, short_description, default_prompt）
```

`SKILL.md` 是整个框架的灵魂——它不是代码，而是**结构化的自然语言指令**，被 Codex CLI / Claude Code 等运行时加载为 skill 级别的行为约束。

### 2.3 Gate 顺序（核心工作流）

`gateflow` 定义了一个**固定的 Gate 顺序**，类似 CI/CD pipeline 的阶段门控：

```
plan → plan review → fix → re-review → accepted plan commit
  → implementation → code review → fix → re-review → accepted slice commit
    → [循环直到所有 slice 完成]
  → aggregate deepreview → fix → re-review → accepted deepreview commit
  → ready-to-create-PR → PR → PR review → final closeout
```

**关键设计**：这个流程默认**全自动推进**，controller agent 只在以下情况停下来问用户：

- 存在 blocking open question（影响 scope、架构、契约等）
- branch/dirty changes/scope ownership 不清
- validation failure 或需要用户决策的残余风险
- 需要执行对外可见动作（创建 PR、push、merge 等）

---

## 三、Agent 编排方案

### 3.1 角色分工

框架采用**明确的角色分离**，避免单个 Agent 既当裁判又当运动员：

| 角色 | 职责 | 可用 Agent |
|------|------|-----------|
| **Controller** | 总控：维护状态、派发 handoff、收集 artifact、裁决 finding、保护 scope boundary、推进 gate | `AgentController`（Codex） |
| **Planning Agent** | 只写 handoff-ready、code-generation-ready 的计划 | 由 controller 指定 |
| **Implementation Agent** | 只实现 approved plan 的 assigned slice | `AgentCodex`（Codex Pro）或 `AgentOpus`（Claude） |
| **Fix Agent** | 只修 controller-accepted findings | 同 Implementation Agent |
| **Review / Re-review Agent** | 只输出 evidence-based findings 或复核结果 | `AgentMiMo`、`AgentDS`、`AgentGLM`（三选二） |
| **User** | 回答 blocking open questions，授权对外动作 | 人类 |

### 3.2 多 Agent 通信机制

通过 `init-agents` skill，框架使用 **tmux pane** 作为 Agent 间通信通道：

```bash
tmux-cli status                          # 发现 Agent pane
tmux-cli send "<prompt>" --pane=<id>     # 发送指令
tmux-cli wait_idle --pane=<id>           # 等待完成
tmux-cli capture --pane=<id>             # 捕获输出
```

**通信协议要点**：

- 每次发送前重新确认目标 pane id
- 新任务先 `/clear` session，未完成任务直接发 follow-up
- 避免 prompt 中使用裸 `#数字`（会被截断）
- Worker prompt 必须明确：当前 gate、assigned scope、allowed files、artifact path、stop condition
- **严禁** worker 自行 commit、push、PR 或进入其它 gate

### 3.3 多模型异构编排

框架支持**不同 LLM 后端**的 Agent 协同工作：

| Agent | 后端模型 | 角色 |
|-------|---------|------|
| `AgentController` | Codex（OpenAI） | 总控 |
| `AgentCodex` | Codex Pro | 实施/修复 |
| `AgentDS` | DeepSeek V4 Pro | 审查/复审 |
| `AgentMiMo` | MiMo V2.5 Pro | 审查/复审 |
| `AgentGLM` | GLM-5.1 | 审查/复审 |

这种设计让**不同模型各司其职**——用 Codex 做代码生成，用 DeepSeek/MiMo/GLM 做独立审查，实现交叉验证。

### 3.4 Review 的交叉验证

`phaseflow` 要求 aggregate review 必须从 `AgentMiMo`、`AgentDS`、`AgentGLM` 中**任选其二同时做**，由 controller 整合、去重和裁决。这保证了审查的独立性和多样性。

---

## 四、全生命周期覆盖

### 4.1 头脑风暴 / 需求讨论

当用户说"使用 $gateflow 开发 <feature>"时，controller 首先判断需求是否足够写 plan：

- **需求清楚** → 直接进入 `plan` 阶段
- **需求不清** → 先进行 feature discussion，收敛：goal、success signal、motivation、alternatives、tradeoffs、likely slicing、non-goals、stop conditions、user preferences

关键约束：**不要让 discussion 变成 implementation**。

### 4.2 需求分析 / 架构设计

通过 `phaseflow`，项目要求准备两个核心文档：

1. **`design_doc`（设计真源）**：所有 phase design、plan 裁决和 review 裁决的核心依据
2. **`control_doc`（总控文档）**：记录 phase 状态、目标、追踪项、遗留问题、潜在风险和下一步入口

`planreview` skill 以**对抗性姿态**审查计划：

- 默认假设 plan 至少有一个重要问题
- 主动寻找：scope 不清、过度耦合、auth/权限漏洞、数据丢失风险、状态机缺陷、测试缺口
- 应用 5 个专项审查透镜：架构边界、最佳实践、最优方案、过度设计、过度耦合

### 4.3 开发实现

实施阶段严格遵循 **Slice Rules**：

- 每个 slice 必须足够小，适合一个 implementation pass + 一个 review pass
- slice 必须写清：id/name、objective、allowed files、prerequisites、exact allowed changes、functions/classes/types、tests、completion signal
- implementation agent 只能做当前 assigned slice，不得提前做 future-slice work

### 4.4 测试验证

测试要求贯穿整个流程：

- **Plan 阶段**：必须定义 tests/validation commands/expected assertions/failure paths
- **Implementation 阶段**：每个 slice 必须包含测试
- **Code Review 阶段**：`deepreview` 检查 tests 是否真正证明关键行为、是否遗漏 failure paths
- **Aggregate Deepreview**：对整个 branch diff 做最终审查

`deepreview` 的审查方法非常严格：

1. 理解 change intent
2. 对齐 contracts 和 sources of truth
3. 追踪 implementation paths（沿真实代码路径逐行走读）
4. 检查所有关键分支是否由真正决定该分支的事实驱动
5. 对参数展开生效链
6. 做一致性检查
7. 执行 adversarial failure pass
8. Review tests and risk

### 4.5 风险跟踪与残余管理

每个 implementation/fix report 必须列出 residual risks，controller 分类为：

- fixed in current slice
- covered by later slice
- assigned to later phase/work unit
- tracked by existing issue
- requiring new issue or user decision

**存在未分类残余风险时，不得关闭任何 gate。**

---

## 五、Artifact 体系

框架要求所有关键产出都是 **durable artifact**（持久化文件），而非仅存在于对话中：

| Artifact 类型 | 触发时机 | 内容 |
|-------------|---------|------|
| Plan artifact | plan 完成后 | 目标、范围、切片、测试、风险 |
| Plan review artifact | plan review 后 | findings、open questions、conclusion |
| Implementation artifact | 每个 slice 完成后 | changed files、validation、residual risk |
| Fix artifact | 每次 fix 完成后 | per-finding fix status、new risks |
| Code review artifact | code review 后 | evidence-based findings |
| Aggregate deepreview artifact | 所有 slice 完成后 | 完整 diff 的深度审查 |
| PR readiness report | ready-to-create-PR | branch、commits、validation、risks |

每个 finding 使用**固定格式**，包含：编号、严重程度、入口/函数、文件行号、输入场景、实际分支、预期行为、实际行为、直接证据、影响、建议改法、修复风险。

---

## 六、安装与使用

### 6.1 前置要求

- **Codex CLI** 或 **Claude Code**（或支持本地 skill 指令文件的 Agent 运行时）
- **Python 3.11+**（运行 skill 验证器）
- **tmux + tmux-cli**（多 Agent 通信，可选）

### 6.2 安装步骤

```bash
# 1. 克隆仓库
git clone https://github.com/noho/code-is-cheap.git
cd code-is-cheap

# 2. 同步 skills 到本地 Codex/Claude 目录
./scripts/sync-skills.sh
# 自动安装到：~/.codex/skills, ~/.codex-pro/skills, ~/.claude/skills 等

# 3. 重启 Codex/Claude 会话以加载 skill 列表
```

### 6.3 多 Agent 环境配置（可选）

如需使用多 Agent 协作，需要：

1. 安装 `claude-code-tools`：`uv tool install claude-code-tools`
2. 在 `~/.zshrc` 中配置各 Agent 的启动函数（`ds_claude`、`mimo_claude`、`glm_claude`、`controller_codex`、`pro_codex`）
3. 导出对应 API Key（`DEEPSEEK_API_KEY`、`MIMO_PLAN_API_KEY`、`GLM_API_KEY`）
4. 在 tmux 各 pane 中启动 Agent

### 6.4 使用方式

**单次复杂功能开发**（Gateflow）：

```text
# Codex
Use $gateflow to develop <feature>.

# Claude Code
Use /gateflow to develop <feature>.
```

**项目级 Phase 开发**（Phaseflow）：

```text
# Codex
Use $phaseflow with design_doc=docs/design.md control_doc=docs/control.md

# Claude Code
Use /phaseflow with design_doc=docs/design.md control_doc=docs/control.md
```

**计划审查**：

```text
$planreview docs/path/to/plan.md
```

**深度代码审查**：

```text
$deepreview              # 审查当前改动
$deepreview --pr 123     # 审查 PR
$deepreview --all        # 审查整个仓库
```

---

## 七、设计亮点总结

| 维度 | 设计决策 |
|------|---------|
| **控制哲学** | "代码廉价，工程控制昂贵"——先设计后执行，Agent 在明确边界内运作 |
| **自动化程度** | 从 plan 到 ready-to-create-PR 全自动，仅在 blocking question 和对外动作处停顿 |
| **角色分离** | Controller 不写代码/审查，Worker 不做裁决，User 只处理阻塞问题和授权 |
| **质量保证** | 对抗性 review + 多模型交叉审查 + 固定 finding 格式 + 残余风险强制分类 |
| **可追溯性** | 所有结论都是 durable artifact，每个 commit 有明确 gate 含义 |
| **异构协作** | 不同 LLM 后端各司其职，通过 tmux pane 实现进程级通信 |
| **可扩展性** | Skill 文件是纯 Markdown，易于修改和扩展；sync 脚本支持多目标部署 |

---

## 八、适用场景与局限

### 适用场景

- 复杂 feature 开发（涉及多模块、多文件变更）
- 大型 migration / schema change / public contract change
- 架构敏感的重构
- 需要严格质量保证和可追溯性的项目
- 多人/多 Agent 协作的工程团队

### 局限

- 依赖 Codex CLI / Claude Code 等特定运行时，不直接兼容其他 AI 编码工具
- 多 Agent 模式需要 tmux 环境和多个 API Key，配置门槛较高
- 对于 typo、小型 bugfix 等轻量改动，gated workflow 可能过重
- 项目尚处于早期阶段（仅 3 次提交，无 release），文档和生态仍在完善中

---

## 九、关键术语解释

### 9.1 核心概念

| 术语 | 含义 |
|------|------|
| **Gate** | 类似 CI/CD pipeline 的阶段门控，每个 gate 有明确的准入/准出条件，只有满足条件才能推进到下一阶段 |
| **Slice（切片）** | 把一个大的 feature 拆成的最小可验收实施单元，精确到"改哪些文件、实现哪些函数、通过哪些断言" |
| **Handoff** | controller 向 worker agent 派发的任务指令，包含当前 gate、assigned scope、allowed files、artifact path、stop condition |
| **Artifact** | 持久化的工作产出文件（如 plan、review、fix 报告），而非仅存在于对话中的结论 |
| **Finding** | 审查中发现的具体问题，使用固定格式记录，包含严重程度、直接证据、建议改法等 |
| **Residual Risk** | 每个 slice/fix 完成后仍存在的未覆盖风险，必须分类并有明确 owner，否则不得关闭 gate |
| **Blocking Open Question** | 影响 scope、架构、契约等的关键未决问题，必须在 plan re-review 通过前解决 |

### 9.2 测试验证相关术语

| 术语 | 含义 |
|------|------|
| **validation commands** | 计划中明确写出的、可执行的测试/校验命令（如 `pytest tests/test_user_service.py -v`），要求具体可运行，而非模糊的"应该测试一下" |
| **expected assertions** | 测试中期望成立的具体条件（如"调用 `create_user` 后，数据库中应存在对应记录，`status` 为 `active`"），必须写明预期结果 |
| **failure paths** | 功能在异常/边界情况下的行为路径（如网络超时、并发冲突、非法参数），框架特别强调：只覆盖 happy path 会被视为真实弱点 |

### 9.3 Agent 通信术语

| 术语 | 含义 |
|------|------|
| **裸 `#数字`** | 在 tmux prompt 中直接写 `PR #45`、`issue #123` 这类文本。`#` 在某些 tmux/shell 环境中是特殊字符（注释符），会被错误解析导致文本截断。应改写为 `PR 45`、`PR-45` 或完整 URL |
| **tmux pane** | tmux 终端复用器中的一个独立终端面板，每个 Agent 运行在各自的 pane 中，通过 `tmux-cli` 工具进行进程级文本通信 |
| **Session Clear** | 向目标 Agent pane 发送 `/clear` 命令清空上下文，确保新任务不受之前对话干扰。未完成任务则不能 clear |

---

## 十、项目级任务启动前的文件准备清单

使用 `phaseflow` 启动项目级任务前，需准备以下文件：

### 必备文件（2 个）

#### 1. 设计真源文档（`design_doc`）

例如 `docs/design.md` 或 `docs/host/design.md`。这是所有设计裁决的核心依据，内容应覆盖：

- 项目目标与动机（goal / motivation）
- 非目标与范围边界（non-goals / scope）
- 架构设计：模块划分、层级关系、依赖方向
- 公共契约：API 接口、数据模型、状态机、外部协议
- 关键技术决策及理由
- 成功信号（success signal）

#### 2. 实施总控文档（`control_doc`）

例如 `docs/implementation-control.md`。这是 phase 进度的唯一真源，内容应覆盖：

| 内容项 | 说明 |
|--------|------|
| Phase 列表 | 所有阶段的名称和顺序 |
| Phase 依赖 | 哪些 phase 必须先完成 |
| 进入条件 | 每个 phase 开始前需满足什么 |
| 退出条件 | 每个 phase 什么时候算完成 |
| 验证要求 | 每个 phase 的测试/验证标准 |
| 追踪项 | 遗留问题、潜在风险、owner 指派 |
| 下一步入口 | 当前 phase 结束后从哪里继续 |

### 推荐文件

| 文件 | 说明 |
|------|------|
| `AGENTS.md` 或 `CLAUDE.md` | 放在仓库根目录，定义项目级编码规范、架构约束。`deepreview` 审查时会自动检查 |
| `docs/reviews/` 目录 | review artifact 的输出目录，提前创建可避免首次运行时出错 |

### 推荐项目目录结构

```
你的项目/
├── docs/
│   ├── design.md                    ← 必备：设计真源
│   ├── implementation-control.md    ← 必备：实施总控
│   └── reviews/                     ← 推荐：review artifact 输出目录
├── AGENTS.md 或 CLAUDE.md           ← 推荐：项目指令
└── ...（你的项目代码）
```

准备完成后，启动命令：

```text
# Codex
Use $phaseflow with design_doc=docs/design.md control_doc=docs/implementation-control.md

# Claude Code
Use /phaseflow with design_doc=docs/design.md control_doc=docs/implementation-control.md
```
