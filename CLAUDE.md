# CLAUDE.md

本文件是 Claude 类 Agent 的入口适配层，不是独立规则真源。

## 必读规则

- 本仓库统一 Agent 执行规则以 `AGENTS.md` 为唯一权威来源。
- Claude Code、AgentMiMo、AgentDS、AgentOpus 等 Claude 类 Agent 启动后必须先读取并遵守 `AGENTS.md`。
- 若本文件与 `AGENTS.md` 存在冲突，以 `AGENTS.md` 为准。

## 执行提醒

- 用中文回答。
- 不要按本文件推导架构、模块边界、开发流程或基金分析规则；这些内容全部以 `AGENTS.md`、`docs/design.md`、`docs/implementation-control.md` 和当前代码为准。
- 当前生产主链路不依赖外部 `dayu-agent` 运行时。Dayu 只作为方法论和历史研究参考；后续如需要 Host、Engine、tool loop 或 runtime 能力，必须在本项目内按现有边界内化实现。
