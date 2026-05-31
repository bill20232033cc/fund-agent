# Host 开发手册

`fund_agent.host` 是本项目内化的 Host runtime governance 包。它吸收 Dayu Host 的稳定能力边界，但不直接依赖 `dayu-agent` / `dayu.host` 生产 runtime。

当前最小实现只负责进程内单次 run 的生命周期、global deadline、cancel token、终态、run-local 安全事件和安全诊断。`fund-analysis analyze --use-llm` 经 `HostRuntimeRunner` 托管后再调用 Service。Host 不理解基金业务，不导入 Service 或 Fund，也不实现 Agent tool loop。

稳定边界：

- Host 管 run lifecycle、cancel、deadline、terminal state、safe diagnostics、event/outbox boundary。
- Service 管业务语义、prompt/ExecutionContract、provider clients、chapter policy 和 final assembly。
- Fund 管基金领域规则、CHAPTER_CONTRACT、证据锚点、writer/auditor 和审计。
- CLI/UI 负责把 async Service 调用包成同步 operation closure；Host runner 不管理 asyncio event loop。

当前非目标：

- 不提供跨进程取消。
- 不提供 durable outbox / replay / resume。
- 不提供 memory 或持久 session。
- 不强杀已经进入同步 provider HTTP 的调用。
- 不接入 `dayu.engine`、ToolRegistry 或 ToolTrace。
