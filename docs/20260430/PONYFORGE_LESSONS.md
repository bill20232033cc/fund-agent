# PonyForge 项目复盘与教训

> PonyForge 是 zhixing agent 的前身项目。本文档记录其经验教训，避免在新项目中重蹈覆辙。

---

## 项目概况

- **名称**：PonyForge
- **定位**：通用 Coding Agent CLI（单模型双角色 Planner/Executor + 5 阶段状态机）
- **技术栈**：JavaScript (ESM), Node.js, DeepSeek API
- **运行时间**：约 2026-04 至 2026-05
- **最终状态**：项目终止，转向 zhixing agent

---

## 做对了什么

1. **LLM API 集成经验**——DeepSeek API 的 OpenAI-compatible 调用、流式响应、thinking mode 处理、重试策略都已调通
2. **工具注册系统**——`createTools()` 工厂函数、工具权限矩阵设计合理
3. **Prompt 模板工程**——Planner/Executor 双角色 prompt、Phase Contract 约束、JSON 输出格式控制
4. **安全设计**——路径校验 `validatePath()`、原子写入 `atomicWriteFile()`、NULL byte 检测、shell 命令安全执行
5. **状态机设计**——5 阶段状态机 + 阶段门控的概念是正确的

---

## 做错了什么

### 核心问题：追求通用 Agent 是错误方向

作为一个人的项目，追逐 Claude Code 这种由大型团队持续迭代的产品，差距只会越来越大。

### 技术层面的问题

**1. 缺少 Sub-Agent 机制**
主 Agent 直接做所有事情（探索、规划、执行），上下文窗口被工具输出塞满。Claude Code 的核心设计是 Sub-Agent 探索 → 返回摘要 → 主 Agent 行动。

**2. 无上下文压缩**
历史消息线性增长，10 万 token 时模型已经出现"上下文腐烂"——重复读同一文件、忘记早期信息。

**3. 低级工具设计**
只有原子级工具（`read_file` 一次一个文件），缺少高级语义工具。25 轮 `read_file` 才能收集完信息，而一个 `gather_context` 工具 1-2 轮就能完成。

**4. 探索无限循环**
模型在 Phase0 不断读取文件，从不推进到产出阶段。虽然有重复检测和强制推进机制，但模型会换参数绕过检测。

### 实际运行数据

**最后一次运行（2026-05-06）：**

| 指标 | 数值 |
|------|------|
| 任务 | 生成 docs/WIKI.md |
| LLM 调用 | 35 次 |
| 重复调用 | 20 次（57% 浪费） |
| 成功工具调用 | 21 次（read_file:16, code_search:2, repo_map:1, git_status:1, advance_phase:1） |
| Token 消耗 | 101,552 / 100,000 预算 |
| 最终阶段 | Phase1_Anchor（未完成） |
| 最终产出 | **无**（WIKI.md 未生成） |

**时间线**：
```
Phase0_RepoMap（~25 轮）
  ├── 有效调用: repo_map×1, git_status×1, read_file×8, code_search×1
  ├── 重复调用: repo_map×3, read_file×4（被阻止）
  └── 终于调用 advance_phase → 推进到 Phase1

Phase1_Anchor（~10 轮）
  ├── Tool 'undefined' 错误×1
  ├── 有效: read_file×3, code_search×1
  ├── 重复: read_file×6（被阻止）
  └── 预算耗尽，终止
```

---

## 迁移到 zhixing agent

### 可直接复用

| 能力 | 迁移方式 |
|------|---------|
| LLM API 调用 + 流式响应 | 概念复用（语言从 JS 转 Python） |
| 工具注册系统 | 概念复用（ToolRegistry 设计） |
| Prompt 模板工程 | 概念复用（模板驱动的 prompt 组装） |
| 状态机管理 | 概念复用（简化为 Scene 机制） |
| 安全意识 | 文件操作安全、API key 保护 |

### 不需要复用

| 能力 | 原因 |
|------|------|
| 5 阶段状态机 | zhixing 用更简单的 Scene 机制替代 |
| Sub-Agent 探索 | 模板驱动不需要自由探索 |
| 上下文压缩 | 模板驱动下上下文更可控，需要时再加 |
| 重复调用检测 | 用结果缓存 + 工具输出截断解决 |

---

## 关键教训

1. **不要追逐通用 Agent**——一个人做不了 Claude Code，但可以做 dayu-agent 这样的专业工具
2. **模板 > 架构**——dayu-agent 的成功不是因为代码多好，而是因为模板凝结了投资经验
3. **先手动验证，再自动化**——刘成岗花了很久打磨模板，确认有效后才写代码
4. **工具设计决定效率**——高级语义工具比原子工具高效 10 倍
5. **上下文是稀缺资源**——每一 token 都有隐性成本，必须精打细算
6. **投资分析 > 代码生成**——价值投资分析是一个更窄、更有价值、更适合个人项目的领域
