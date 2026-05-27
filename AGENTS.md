## 语言

- 用中文回答

## 规则真源

- 本文件是本仓库所有 Agent 执行规则的唯一权威入口。
- Claude Code、AgentMiMo、AgentDS、AgentOpus 等 Claude 类 Agent 如果默认读取 `CLAUDE.md`，必须继续读取并遵守本文件；若两者冲突，以本文件为准。
- `CLAUDE.md` 只作为 Claude 类 Agent 的入口适配层，不单独维护架构、模块边界、开发流程或基金分析规则。

## 背景

- **基金分析 Agent 项目**，基于有知有行投资方法论（R = A + B - C），提供基金分析工具供 LLM 从基金年报、招募说明书、定期报告中提取信息。

- **核心分析框架**：
  - R = A + B - C（投资者收益 = Alpha + Beta - Cost）
  - 产品本质 → 收益归因 → 基金经理画像 → 投资者获得感 → 当前阶段 → 核心风险 → 最终判断

- **基金分析模板**：见 `docs/fund-analysis-template-draft.md`，包含 8 章结构化分析框架和 CHAPTER_CONTRACT 机制。

- **审计机制**：三层审计架构（Programmatic → LLM → Evidence Confirm），规则码 P1/P2/E1/E2/E3/C1/L1/L2/R1/R2

- **证据锚点规范**：
  - 正文引用格式：`> 📎 证据：年报§[章节] [内容描述]`
  - 附录汇总格式：`年报[年份]§[章节]表[编号]行[行号]`

## 必读文件（按优先级）

1. **本文档**（`AGENTS.md`）——所有 Agent 执行约束和原则
2. `docs/design.md`——设计真源文档，所有设计决策的唯一权威来源
3. `docs/implementation-control.md`——实施总控文档，Phase 列表、依赖、验证要求
4. `docs/fund-analysis-template-draft.md`——基金分析模板（CHAPTER_CONTRACT / preferred_lens / ITEM_RULE）

## 真源文档规范

### `docs/design.md`

- 定位：代码设计真源，回答“当前系统是什么、稳定边界是什么、已接受但未实现的未来设计是什么”。
- 必须区分三类状态：`当前已实现`、`已接受的未来设计`、`候选/研究输入`。
- 未实现内容可以进入 `docs/design.md`，但必须明确标注为未来设计或候选，不得写成当前代码事实。
- 禁止把实验构想、研究材料、外部项目机制或旧架构表述直接写成当前设计事实；只有经过当前 gate 裁决并回写的内容才可作为设计真源。
- 当前代码事实与未来设计并存时，必须写清当前生产路径、非目标、触发未来 gate 的条件和禁止事项。

### `docs/implementation-control.md`

- 定位：实施总控入口，回答“当前 phase/gate 在哪、下一步做什么、依据哪些 accepted artifacts、还有哪些 residual owner”。
- 文件前部只保留控制面信息：Startup Packet、Current Truth Guardrails、current gate、next entry point、当前 accepted artifacts、open residuals、non-goal reminder、最近 Active Gate Ledger。
- 历史审计账本、长版本记录、旧 phase 全量日志、PR/commit 细节和 superseded 架构叙述应迁入 `docs/reviews/` 或 `docs/archive/`，在 control doc 中只保留索引和必要摘要。
- `docs/implementation-control.md` 中的 archive / historical section 只能作为证据链，不得覆盖 Startup Packet、当前 gate 或 `docs/design.md` 当前设计章节。
- 后续更新 control doc 时，应优先压缩而不是追加长日志；新增日志如果不是恢复当前 gate 所必需，必须写入独立 artifact 并在 control doc 中引用路径。

## Gate 轻重分类规则

- `fast_path`：只允许用于低风险文档、注释、格式、局部说明或已验证事实的控制面同步；不得改变代码行为、public contract、schema、质量门控语义、final judgment、Host/Agent/dayu、外部来源策略、baseline/golden 资格或 release/PR 外部状态。
- `standard`：默认分类，适用于普通 plan/review/implementation/evidence/disposition gate；需要明确验证矩阵、至少两份独立 review（除非记录 reviewer 不可用）、controller judgment、必要文档更新和 local accepted commit。
- `heavy`：用于架构边界、公共契约、schema/migration、质量门控语义、final judgment、Host/Agent/dayu、外部来源策略、baseline/golden promotion、release readiness 或 PR 外部状态等高影响 gate；需要更完整的 plan/review、实现/验证矩阵和残余风险 owner。
- 分类不确定时选择更重一级；默认使用 `standard`。

## 建议

- 共享终端经常会被前一次的 heredoc 污染，执行脚本时每次都启用新的后台 terminal 运行命令，避免受旧会话影响。

- Python 脚本分析比直接读文件分析更有效率，优先使用脚本处理数据提取和计算。

- 基金年报数据量大，优先使用增量分析（先读目录结构，再按需提取具体章节）。

## 硬约束（必须遵守）

- **请使用第一性原理思考**。不能假设用户非常清楚自己想要什么和该怎么得到。保持审慎，从原始需求和问题出发，如果动机和目标不清晰，停下来和用户讨论。如果目标清晰但建议的路径不是最短路径，告诉用户并建议更好的办法。

- **找问题的 root cause 一定要逻辑/数据同源，禁止使用间接证据**。

- **CHAPTER_CONTRACT 的设计目标**，不是"把信息给全"，而是"让一个会犯错、会走捷径、上下文有限、偏好模式匹配的推理器，在最低认知负担下稳定做对下一步动作"。

- **对基金文档的存取**，都应该只通过统一的文档仓库接口，禁止直接操作文件系统。

- **生产年报 PDF 访问必须经过 `FundDocumentRepository`**。年报来源编排属于 Agent 层 `fund_agent/fund` documents 内部实现，Service、UI、Host、renderer、quality gate 不得直接调用具体来源、PDF cache 或下载 helper。

- **年报来源 fallback 必须显式按失败分类决策**：`not_found`、`unavailable` 才允许 fallback；`schema_drift`、`identity_mismatch`、`integrity_error` 必须 fail-closed，禁止被 Eastmoney fallback 静默掩盖。

- **Dayu 是四层架构参考与 Host/Agent 执行底座来源**。本项目目标架构统一为 `UI -> Service -> Host -> Agent`。当前确定性 CLI 主链路尚未接入 Host/Agent 调度，但后续一旦引入 Host 层，必须使用 `dayu.host`；一旦引入 Agent 执行内核 / tool loop / runner / ToolRegistry / ToolTrace，必须使用 `dayu.engine`。禁止通过零散外部 Dayu API 绕过本项目四层边界。

- **禁止把显式参数放在 extra_payload 里传递**，所有参数必须显式声明。

- **基金类型判断优先于通用分析**：必须先识别基金类型（指数/主动/债券/QDII/FOF），再应用对应的 preferred_lens。

- **证据必须可溯源**：所有数值判断必须标注数据来源（年报章节/表格位置），禁止"根据经验"或"通常认为"的表述。

## 模块边界（必须遵守）

目标架构固定为四层：

```text
UI -> Service -> Host -> Agent
```

### UI 层

- **负责**：用户交互界面、报告渲染、可视化展示
- **不负责**：基金分析逻辑、数据提取、审计判断
- **依赖约束**：只依赖 Service 层提供的接口，不直接调用 Host 或 Agent 内部模块

### Service 层

- **负责**：业务用例编排、场景定义、prompt/ExecutionContract 组装、用户会话语义、报告生成、质量策略选择
- **不负责**：Host 生命周期治理、Agent tool loop、底层工具实现、基金领域规则细节
- **依赖约束**：调用 Host 层执行 Agent；当前确定性过渡路径可调用 `fund_agent/fund` 公开能力，但不得新增 UI 直接调用 Agent 内部模块

### Host 层

- **负责**：Agent session/run 生命周期、并发、超时、取消、恢复、memory、reply outbox、事件投递、ExecutionDeliveryContext
- **不负责**：基金领域知识、工具具体实现、prompt 业务语义、报告判断
- **依赖约束**：Host 层实现必须使用 `dayu.host`；Host 调用 Agent 层执行，不直接实现工具或基金分析

### Agent 层

- **负责**：Agent 执行、tool loop、runner、ToolRegistry、ToolTrace、context budget、工具调用、基金领域能力、年报解析规则、有知有行方法论实现、审计规则
- **不负责**：UI 渲染、Service 业务用例选择、Host 生命周期治理
- **依赖约束**：Agent 执行内核必须使用 `dayu.engine`；`fund_agent/fund` 是当前 Agent 层基金领域能力包，理解基金类型、财报章节、投资规则、E大策略、CHAPTER_CONTRACT、preferred_lens、ITEM_RULE 和证据审计

### 边界执行规则

- 后续所有设计、重构、评审都必须显式对照上述边界。

- 如果方案与上述边界冲突，应先调整方案，再动代码；不得靠文档例外口径兜底。

- 若发现 README、本文档、实现三者不一致，以"先修正实现/方案使其一致"为目标，不允许长期并存双重口径。

- 以代码为准，不让文档先于代码"设计未来"。

- **归属判定规则**：
  - 任何"读取 prompt manifests / scene 定义"的代码，默认放在 `Service`
  - 任何"渲染最终 `system_prompt` / ExecutionContract / AgentInput"的代码，默认放在 `Service`
  - 任何"决定某个 scene 需要哪些工具语义"的代码，默认放在 `Service`
  - 任何"管理 session / run / 并发 / timeout / cancel / resume / memory / reply outbox / ExecutionDeliveryContext"的代码，默认放在 `Host`，并使用 `dayu.host`
  - 任何"管理 tool loop / runner / trace / facts / ToolRegistry / context budget / tool execution"的代码，默认放在 `Agent`，并使用 `dayu.engine`
  - 任何"理解基金类型、财报章节、投资规则、有知有行方法论"的代码，默认放在 `Agent` 层的 `fund_agent/fund`
  - 任何"CHAPTER_CONTRACT 解析 / preferred_lens 应用"的代码，默认放在 `Agent` 层的 `fund_agent/fund`
  - 任何"审计规则执行 / 证据锚点验证"的代码，默认放在 `Agent` 层的 `fund_agent/fund`

## 📌 设计和代码编写原则（必须遵守）

### 1. 注释与文档

- 所有函数必须提供完整中文 docstring（参数、返回值、异常）。
- 函数内复杂逻辑必须有中文行内注释说明意图。
- 类与模块需要有概览性中文 docstring。
- **基金分析相关代码必须引用模板章节编号**（如"见模板第2章 R=A+B-C"）。

### 2. 代码结构

- 原则上不使用嵌套函数；仅在必须依赖闭包时例外。
- 辅助函数应优先定义为模块级私有函数（`_helper_function`）。
- 原则上不使用嵌套类；仅在必须依赖闭包语义时例外。
- 保持函数扁平化，优先可测试性与可维护性。
- 模块间依赖最小化，优先接口/协议而非具体实现。
- 数据处理、存储、工具调用职责明确分离。
- 重复逻辑必须抽取为公共函数/类。
- 禁止魔法数字/魔法字符串（确有助于可读性的场景除外）。
- **基金类型判断、章节映射、审计规则必须配置化，禁止硬编码**。

### 3. 实现策略

- 设计前先选择最佳实践方案，直接按最佳实践实现。
- 不为历史包袱妥协。
- 编写处理规则时禁止硬编码规则，要写自适应规则。
- **优先实现 CHAPTER_CONTRACT 的 must_answer / must_not_cover 校验机制**。

### 4. 兼容性策略

- 默认按"全新设计"处理，不要求向后兼容旧实现。
- 可使用现代 Python 特性（类型注解、dataclass 等）。
- 无需维护历史版本包袱；必要时可重写并删除旧代码。

### 5. 测试策略

- 每完成一处代码修改，应同步编写/更新测试并优先验证通过。
- 测试跟着实现边界迁移，而不是用生产代码去兼容旧测试。
- 单文件测试覆盖率目标为 ≥80%；这是新增或大幅修改模块的评审目标。当前 CI 自动阻断 gate 仍以项目全局覆盖率命令为准，若单文件暂未达到目标，必须在 review / residual risk 中说明原因、补测计划或接受依据。
- **基金分析测试必须覆盖：模板章节完整性、证据锚点格式、审计规则触发**。

### 6. 文档同步

- 测试通过后，立即同步更新相关 README，保持文档与实现一致；**以代码为准**，不要让 README 先于代码"设计未来"。
- 仅更新 README 中没对齐到代码的部分；不维护"近期更新""版本变更记录"之类时间敏感内容。

- **更新 README 时，先检查三件事**：
  1. 文档里的代码示例是否还能直接对应当前接口与命令。
  2. 是否残留旧术语、旧路径、旧入口、旧架构表述。
  3. 文档职责是否越界（总览文档不抢包文档职责，包文档不重复用户手册）。

- **各 README 的固定定位**：
  - 项目根目录 `README.md`：**用户手册**。目标是"用户一看就会用"。只写用户成功路径：安装、配置、5 分钟跑通、常用工作流、CLI 常用命令、报告渲染入口、文档导航；不展开 Host/Agent/Fund 内部机制。
  - `fund_agent/README.md`：**开发手册 - 总览**。目标是"开发者一看就能理解整体架构并开始扩展"。只写总架构、设计意图、稳定边界、机制示意图、扩展入口、代码阅读顺序；不下沉到 Host/Agent/Fund 包内部实现细节。
  - `fund_agent/host/README.md`：**开发手册 - Host 包**。只写 Host 的架构、`dayu.host` 接入、公共同步/异步契约、session/run 生命周期、并发、取消、恢复、memory、reply outbox、事件流和扩展点。
  - `fund_agent/agent/README.md`：**开发手册 - Agent 包**。只写 Agent 的架构、`dayu.engine` 接入、Runner/Agent 事件流、状态机、ToolTrace schema、ToolRegistry、context budget、工具执行契约和模块导读。
  - `fund_agent/fund/README.md`：**开发手册 - Fund 包**。只写 Fund 作为 Agent 层基金领域能力包的定位、分析框架（8章模板）、CHAPTER_CONTRACT 机制、审计规则、对外接口、内部分层与机制；不要把 Fund 写成系统基础设施。
  - `fund_agent/config/README.md`：**配置说明手册**。只写默认配置、`workspace/config` 覆盖关系、常改项、最小示例、prompts 目录职责；不重复运行时内部实现。
  - `tests/README.md`：**测试手册**。只写测试分层、运行方式、约定和新增测试时的维护规则。

- **触发更新规则**：
  - `fund_agent/host/` 修改 → 更新 `fund_agent/host/README.md`
  - `fund_agent/agent/` 修改 → 更新 `fund_agent/agent/README.md`
  - `fund_agent/fund/` 修改 → 更新 `fund_agent/fund/README.md`
  - `fund_agent/config/` 修改 → 更新 `fund_agent/config/README.md`
  - `tests/` 修改 → 更新 `tests/README.md`
  - `fund_agent/cli/`、`render/`、项目级使用方式或配置入口发生变化 → 更新项目根目录 `README.md`
  - 涉及分层关系、装配方式、Service/Host/Agent/Fund 边界变化 → 同步更新 `fund_agent/README.md`
  - **模板章节结构变化** → 同步更新 `fund_agent/fund/README.md` 和 `docs/design.md`

- **文档写作约束**：
  - 优先写"当前怎么用 / 当前怎么工作"，不要写"未来可能会怎样"。
  - 示例优先使用当前真实命令、真实导入路径、真实参数名。
  - 高层文档使用抽象边界，不泄漏不必要的具体实现类名；包级文档可以写当前默认实现，但必须明确"当前实现"与"稳定契约"的区别。
  - 如果一个概念已经改名，必须全量清理旧名，禁止新旧术语并存。
  - **模板术语必须与代码实现完全一致**（如 CHAPTER_CONTRACT、preferred_lens、ITEM_RULE）。

## 基金分析专项原则

### 分析流程

```
识别基金类型 → 应用 preferred_lens → 按 8 章模板分析 → 审计检查 → 生成证据锚点
```

1. **识别基金类型**（index_fund / active_fund / bond_fund / enhanced_index / qdii_fund / fof_fund）
2. **应用对应 preferred_lens**，确定分析优先级
3. **按模板 8 章结构执行分析**，每章遵循 CHAPTER_CONTRACT
4. **执行审计检查**（P1/P2/E1/E2/E3/C1/L1/L2/R1/R2）
5. **生成证据锚点**，确保所有判断可溯源

### 年报来源 fallback 策略

| 失败类别 | 含义 | 是否允许 fallback |
|---------|------|------------------|
| `not_found` | 来源正常响应但没有目标基金/年份年报 | 是 |
| `unavailable` | 网络、超时、服务端或本地依赖临时不可用 | 是 |
| `schema_drift` | 官方来源响应结构、字段或附件形态偏离契约 | 否 |
| `identity_mismatch` | 返回候选与基金代码、基金 ID、年份或报告类型矛盾 | 否 |
| `integrity_error` | PDF Content-Type、文件头或写入内容完整性失败 | 否 |

- fallback 成功时必须保留 `metadata.fallback_used=True`。
- fallback 被阻断时必须保留来源、失败类别、错误信息和原始异常 cause。
- eligible 失败全部耗尽时保持当前最终异常语义，不把 unavailable 误报为 not-found。

### 禁止事项

- 禁止直接输出"买入""卖出"建议，只输出"值得持有 / 需要关注 / 建议替换"判断
- 禁止预测未来收益或市场走势
- 禁止超出公开披露信息的因果推断
- 禁止基金经理动机猜测
- 禁止"根据经验""通常认为"等无证据表述

### 必须事项

- 必须区分结构性超额收益 vs 阶段性超额收益
- 必须检查基金经理是否持有本基金（利益一致性）
- 必须进行压力测试（按基金类型使用对应阈值）
- 必须标注所有数值的数据来源
- 必须输出明确的"下一步最小验证问题"
