# Host 开发手册

`fund_agent.host` 是本项目内化的 Host runtime governance 包。它吸收 Dayu Host 的稳定能力边界，但不直接依赖 `dayu-agent` / `dayu.host` 生产 runtime。

当前最小实现只负责进程内单次 run 的生命周期、global deadline、cancel token、终态、run-local 安全事件和安全诊断。`fund-analysis analyze --use-llm` 经 `HostRuntimeRunner` 托管后再调用 Service。Host 不理解基金业务，不导入 Service 或 Fund，不读取 `FundLLMExecutionContract` / `FundLLMExecutionRequest` 的业务字段，也不实现 Agent tool loop。

稳定边界：

- Host 管 run lifecycle、cancel、deadline、terminal state、safe diagnostics、event/outbox boundary；当前 API 只接收 `operation_name`、同步 `operation`、`timeout_seconds`、可选 `session_id` 和可选通用 `event_sink`。
- Service 管业务语义、prompt/ExecutionContract、provider clients、chapter policy 和 final assembly；`--use-llm` 的 typed request 和 runtime plan 均由 Service 准备。
- Fund 管基金领域规则、CHAPTER_CONTRACT、证据锚点、writer/auditor 和审计。
- CLI/UI 负责把 async Service 调用包成同步 operation closure，并只把 Service runtime plan 中的 `host_timeout_seconds` 作为 Host deadline 标量；Host runner 不管理 asyncio event loop。

`event_sink` 是通用 Host 事件投递钩子：Host 先构造安全 `HostRunEvent`，追加到 `HostRunResult.events`，再把同一个事件对象传给 sink。Host 不捕获或翻译 sink 异常；CLI 若用于 progress，必须在自己的 sink wrapper 内捕获异常并关闭后续 progress。Host 不格式化 progress 文案，也不理解基金业务 phase 之外的语义。

Host 禁止事项：

- 不导入 `fund_agent.services` 或 `fund_agent.fund`。
- 不检查基金代码、年报年份、基金类型、章节策略、quality policy、provider runtime budget 或 final assembly policy。
- 不接收 `extra_payload`、自由 dict 或业务参数袋。
- 不输出 prompt、draft、raw provider response、raw audit response、API key 或 Authorization header。

当前非目标：

- 不提供跨进程取消。
- 不提供 durable outbox / replay / resume。
- 不提供 memory 或持久 session。
- 不强杀已经进入同步 provider HTTP 的调用。
- 不提供 async Host runner。
- 不接入 `dayu.engine`、ToolRegistry 或 ToolTrace。
