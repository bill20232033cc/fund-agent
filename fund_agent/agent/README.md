# Agent 包开发手册

`fund_agent/agent` 是本项目内化 Agent Engine 的执行层包。当前实现范围覆盖
模板第 1-6 章 body chapter execution 的状态契约、Fund tool adapter、ToolTrace
安全信封、repair policy、body runner 和 Service readiness handoff。

## 当前边界

- Agent 拥有 `AgentReportRun`、`ChapterTask`、`ChapterAttempt`、ToolTrace、
  repair policy 和 body readiness handoff。
- Agent 可以消费 Fund 层 `ChapterFactProjection` 与 `EvidenceAvailability`。
- Agent runner 只执行模板第 1-6 章；第 0/7 章仍由 Service final assembly 生成。
- Agent tool adapter 只包装 Fund primitives：`project_chapter_facts()`、
  `write_chapter()`、`audit_chapter_programmatic()`、`audit_chapter_llm()`。
- `derive_evidence_availability()` 是 run-level same-source precomputation，不是
  ToolRegistry tool。
- Agent 不构造 provider client，不读取环境变量，不读取文档仓库/PDF/cache/source helper。
- Agent 不导入 `fund_agent.host`；Host cancel/deadline 只能由 Service bridge 转成
  `AgentSchedulerInterruption` 后进入 Agent。
- Agent 不替代 Service final product authority；第 0/7 章最终总装仍由 Service
  `FinalChapterAssembler` 负责。

## 当前模块

| 模块 | 职责 |
|---|---|
| `contracts.py` | Agent run/task/attempt、ToolCall、ToolTrace、repair policy、scheduler interruption 和 final readiness dataclasses |
| `tools.py` | Fund primitive typed wrappers 和安全 ToolTrace 生成；不保存 prompt、draft、raw response、provider config 或 secret |
| `repair.py` | 根据 Fund audit issue / repair hint 做内容修复决策；`patch` 与 `regenerate` 当前都映射为记录在 ledger 中的整章重写 |
| `runner.py` | 从同一 `ChapterFactProjection` 执行第 1-6 章 writer / auditor / repair task graph，输出 `AgentReportRun` 与 `FinalAssemblyReadiness` |

## 当前 Service 接入

`fund_agent/services/agent_bridge.py` 是 Service 到 Agent runner 的桥接层：

- Service 仍负责 provider construction、用例语义、`FundLLMExecutionRequest`、
  quality policy、Host context 翻译和 final assembly。
- bridge 把 `HostRunContext` 的 cancel/deadline 检查翻译为
  `AgentSchedulerInterruption`，Agent 包不导入 Host。
- bridge 把 Agent accepted body conclusions、runtime diagnostics 和 prompt-contract
  diagnostics 投影回现有 Service `ChapterOrchestrationResult`，保持当前 no-live
  Service 行为等价。
