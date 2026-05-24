# Release Maintenance Runtime/Engine Boundary Decision Plan - 2026-05-23

## 1. 计划目标

本计划用于下一步 plan review，裁决在 RM-B2 已经落地 `fund_agent/application` 薄 use-case facade、当前 deterministic CLI 生产路径已经是 `UI -> Application -> Service -> Capability`、且 Runtime / Engine 尚未存在的情况下，是否应该立即创建 `fund_agent/runtime` / `fund_agent/engine` 占位包。

第一性原理判断标准：

- 层级存在的目的不是“目录齐全”，而是隔离真实职责、约束依赖方向、承载可测试契约。
- 当前没有 session/run/cancel/resume/outbox、scene registry、system prompt 渲染、tool loop、ToolRegistry、ToolTrace、context budget 或通用 runner 的生产需求。
- 没有行为契约的空包只会制造虚假的架构完成感，并诱导后续代码绕过真实需求评审。

## 2. Current State Evidence

### 2.1 `docs/design.md`

- `docs/design.md` v2.2 明确 `AGENTS.md` 是上位规则真源，设计边界统一为 `UI / Application / Runtime / Service / Engine / Capability`。
- `docs/design.md` §2.1 记录当前实现事实：RM-B2 后 CLI 生产路径走 `UI -> Application -> Service -> Capability`，Runtime / Engine 尚未接入。
- `docs/design.md` §2.1 对 Runtime 的职责定义是 Agent 生命周期管理、`system_prompt` 渲染、scene 注册、工具绑定；对 Engine 的职责定义是 Tool 执行框架、ToolTrace、状态机、事件流。
- `docs/design.md` §2.2 明确当前没有 Runtime run / Engine tool loop / scene preparation 主链路，并裁决“在没有明确 session/run/tool-loop 需求前，不应空造 Runtime 或 Engine 包”。
- `docs/design.md` 同时明确 Dayu 只作为方法论、历史研究、工程基线和手册纪律参考；当前生产主链路不得依赖外部 `dayu-agent` runtime、Host、Engine、tool loop 或外部 Dayu API。

### 2.2 `docs/implementation-control.md`

- Startup Packet 的 next entry point 是 `release maintenance Runtime/Engine boundary decision plan-review or push authorization`。
- Open residuals 记录当前 remaining boundary debt：Runtime/Engine packages 尚未实现；本地 `AGENTS.md` 有未接受冲突 diff，不能在没有用户决策时 staged。
- release-maintenance 候选表明确 Runtime/Engine boundary decision 的 scope guard：未选中具体 runner/tool-loop 需求前不得空造复杂框架。
- Accepted control impact 记录 RM-B2 后当前 deterministic CLI 生产路径经 `fund_agent.application` 薄 use-case facade 调用 Service；Runtime/Engine 是否落地仍作为独立边界债。
- Non-goal reminder 明确不要引入 Dayu Host/Engine/tool loop、LLM writing 或 external runtime dependency。

### 2.3 `fund_agent/README.md`

- `fund_agent/README.md` 把当前包说明为确定性四段生产路径：`UI -> Application -> Service -> Fund Capability`。
- 当前包边界只列出 `fund_agent/ui`、`fund_agent/application`、`fund_agent/services`、`fund_agent/fund`、`fund_agent/config`。
- README 明确当前代码不接入外部 Dayu Host、Engine、tool loop、scene registry 或 LLM prompt runtime；后续如需要这些能力，应在本项目内按当前边界实现，不通过外部 Dayu API 包装主链路。
- README 明确 `fund_agent/config/paths.py` 只是静态仓库默认路径，不代表 Host/Engine runtime 配置已接入。

### 2.4 当前目录事实

当前 `fund_agent` 二级目录只有：

- `fund_agent/application`
- `fund_agent/config`
- `fund_agent/fund`
- `fund_agent/services`
- `fund_agent/ui`

不存在 `fund_agent/runtime` 或 `fund_agent/engine` 包。当前可见生产文件也未显示需要由 Runtime / Engine 承载的通用执行契约。

### 2.5 近期 gate 事实

- RM-B2 controller judgment 已接受新增 Application facade，修复 UI 直接调用 Service 的边界债。
- Design boundary correction 已接受只修改 `docs/design.md`，恢复六层边界并排除外部 Dayu runtime；其 residual 明确 `fund_agent/runtime` 和 `fund_agent/engine` 仍未实现，并应只在有真实 runtime/tool-loop 需求时规划。

## 3. Decision Proposal

推荐方案：**现在不要创建 `fund_agent/runtime` / `fund_agent/engine` placeholder packages；先记录 defer decision 和未来触发条件，继续用 plan-review gate 约束未来真实需求。**

理由：

- 当前 deterministic CLI 已经有清晰、可运行、可测试的生产路径：`UI -> Application -> Service -> Capability`。Runtime / Engine 不在调用链上。
- Runtime / Engine 的职责不是空目录职责，而是生命周期、scene、prompt、工具绑定、runner、ToolTrace、状态机、事件流等运行时契约。当前没有被选中的需求要求这些能力。
- 占位包不能提升边界安全。真正能约束边界的是设计真源、总控 residual、README 当前事实、plan-review checklist、以及必要时的静态 guard。
- 立即创建空包会产生两个坏信号：一是让后续实现误以为 Runtime/Engine 架构已被接受；二是让 README / design / tests 必须解释“存在但无行为”的包，增加认知负担。
- 外部 Dayu runtime 已被明确排除，当前也没有项目内 Runtime / Engine 的最小可测试契约。此时落地目录属于空造框架。

未来触发条件：

- 出现真实 session/run 生命周期需求：并发、超时、取消、恢复、memory、reply outbox、事件投递等。
- 出现真实 scene registry / `system_prompt` 渲染 / prompt manifest / 工具绑定需求。
- 出现真实 tool loop / runner / ToolRegistry / ToolTrace / context budget / 工具执行状态机需求。
- 出现 LLM 审计、Evidence Confirm、Agent 化分析或异步执行路径，并且 deterministic Service/Capability 直接编排已无法表达运行时边界。
- 任一触发条件被选中后，必须先产出单独 plan-review artifact，明确 typed contracts、依赖方向、失败语义、事件流、测试策略、README 同步点，并证明不是外部 Dayu runtime 包装。

## 4. Scope

本决策计划的推荐实施 scope：

- 只产出本 plan artifact，供 plan review 使用。
- 在下一步若本计划被接受，可做 docs-only 对齐：在 `docs/design.md`、`docs/implementation-control.md`、`fund_agent/README.md` 中明确 Runtime/Engine defer decision、触发条件和当前不创建占位包的原因。
- 可选增加静态 guard，但仅在 reviewer 要求且有明确维护价值时进行。例如检查当前生产代码没有导入 `fund_agent.runtime` / `fund_agent.engine`，或检查没有外部 `dayu-agent` runtime 依赖。
- 保留当前 deterministic CLI 生产路径：`UI -> Application -> Service -> Capability`。

## 5. Non-Scope

- 不创建 `fund_agent/runtime` 或 `fund_agent/engine` 包。
- 不新增 Runtime / Engine 抽象、Protocol、基类、placeholder docstring、空 `__init__.py`。
- 不修改生产代码、测试、README、总控文档或设计文档，除非本计划后续被 plan review 接受并另开 docs-only alignment slice。
- 不引入外部 `dayu-agent`、Dayu Host、Dayu Engine、tool loop、LLM writing、scene registry 或 prompt runtime。
- 不改变年报访问路径；生产年报访问仍必须经过 `FundDocumentRepository`。
- 不修改、不暂存本地冲突中的 `AGENTS.md`。
- 不 commit、push、开 PR、请求 reviewer、关闭 PR 或执行任何外部动作。

## 6. Implementation Slices

### Slice 0 - 本计划产物

目标：产出当前文件，供下一步 plan review。

允许文件：

- `docs/reviews/release-maintenance-runtime-engine-boundary-decision-plan-20260523.md`

验证：

- `git diff --check docs/reviews/release-maintenance-runtime-engine-boundary-decision-plan-20260523.md`
- `git status --short`

### Slice 1 - Defer decision 文档对齐（仅在 plan review 接受后执行）

目标：把“当前不创建 Runtime/Engine 占位包”的裁决写入现有真源与开发总览。

候选文件：

- `docs/design.md`
- `docs/implementation-control.md`
- `fund_agent/README.md`

内容要求：

- `docs/design.md` 保留六层目标边界，同时明确 Runtime/Engine 是 future concrete capability boundary，不以空包表示当前完成状态。
- `docs/implementation-control.md` 将 Runtime/Engine boundary debt 从“是否落地”更新为“deferred until concrete runtime/tool-loop trigger”，并记录触发条件。
- `fund_agent/README.md` 继续描述当前生产路径为 `UI -> Application -> Service -> Fund Capability`，并明确 absence of runtime/engine packages is intentional。

验证：

- `git diff --check docs/design.md docs/implementation-control.md fund_agent/README.md`
- `rg -n "dayu\\.host|dayu\\.engine|external Dayu runtime|外部 Dayu runtime|Host -> Agent|UI -> Service -> Host -> Agent" docs/design.md docs/implementation-control.md fund_agent/README.md`
- `rg -n "fund_agent/runtime|fund_agent/engine|Runtime/Engine|Runtime / Engine" docs/design.md docs/implementation-control.md fund_agent/README.md`

### Slice 2 - Optional static guard（仅在 reviewer 明确要求后执行）

目标：把“不应误接 Runtime/Engine 或外部 Dayu runtime”的边界变成轻量静态检查。

可选方向：

- 在已有边界测试附近增加 AST/import guard，确认 `fund_agent/ui` 只依赖 Application，不直接导入 Service/Fund/Runtime/Engine。
- 增加依赖 guard，确认生产依赖中不包含 `dayu-agent`。
- 增加 repo guard，确认没有生产代码导入外部 `dayu.host` / `dayu.engine`。

不建议的方向：

- 不为了 guard 创建 `fund_agent/runtime` 或 `fund_agent/engine`。
- 不创建空 Protocol 或抽象基类。
- 不把未来参数放进 `extra_payload` 或自由 dict。

验证：

- `uv run pytest <新增或既有边界测试> -q`
- `ruff check fund_agent tests`
- `git diff --check <触达文件>`

## 7. Acceptance Criteria

本计划被接受时应满足：

- 明确裁决：当前不创建 `fund_agent/runtime` / `fund_agent/engine` placeholder packages。
- 明确当前生产路径：`UI -> Application -> Service -> Capability`。
- 明确 defer 不是否认六层边界，而是承认 Runtime / Engine 必须由真实运行时需求触发。
- 明确未来触发条件：session/run 生命周期、scene registry、system prompt、tool binding、tool loop、runner、ToolTrace、context budget、LLM 审计、Evidence Confirm 或 Agent 化执行路径。
- 明确禁止外部 Dayu runtime / Host / Engine / tool loop / external Dayu API 进入生产主链路。
- 明确 FundDocumentRepository 边界不变。
- 明确 docs-only alignment 和 optional static guard 的最小后续 slice。
- 不修改本地冲突 `AGENTS.md`，不恢复或删除任何文件，不 commit/push/PR。

## 8. Validation Commands

本计划产物本身：

```bash
git diff --check docs/reviews/release-maintenance-runtime-engine-boundary-decision-plan-20260523.md
git status --short
```

若后续进入 Slice 1：

```bash
git diff --check docs/design.md docs/implementation-control.md fund_agent/README.md
rg -n "dayu\\.host|dayu\\.engine|UI -> Service -> Host -> Agent|外部 Dayu runtime" docs/design.md docs/implementation-control.md fund_agent/README.md
rg -n "Runtime / Engine|Runtime/Engine|fund_agent/runtime|fund_agent/engine" docs/design.md docs/implementation-control.md fund_agent/README.md
```

若后续进入 Slice 2：

```bash
uv run pytest <boundary-test-file> -q
ruff check fund_agent tests
git diff --check <touched-files>
```

## 9. Plan Review Checklist

- 六层边界：是否以用户提供的 `AGENTS.md` 为权威，保持 `UI / Application / Runtime / Service / Engine / Capability`，并承认当前生产路径只实际经过 `UI -> Application -> Service -> Capability`？
- Runtime/Engine defer：是否证明了当前没有 session/run/tool-loop/ToolTrace/scene registry 等真实需求，因而不创建占位包？
- Dayu reference / no runtime dependency：是否只把 Dayu 当方法论、历史研究和工程纪律参考，没有引入外部 `dayu-agent` runtime、Host、Engine、tool loop 或外部 Dayu API？
- explicit-parameter / no-extra-payload：是否所有未来 scene、tool、审计开关、基金代码、年份、估值状态、缓存策略、来源选择都必须进入 typed request / contract / config，而不是 `extra_payload`？
- FundDocumentRepository 边界：是否保持生产年报访问只通过 `FundDocumentRepository` / `FundDataExtractor`，Service/UI/未来 Runtime/Engine 都不得直接读取 PDF、cache 或具体来源？
- docs sync：如果后续执行 docs-only alignment，是否只更新当前事实和 defer decision，不把未来 Runtime/Engine 写成已实现？
- scope control：是否没有修改生产代码、测试、README、总控文档或设计文档，除非 plan review 接受后另开 slice？
- repo hygiene：是否未暂存本地冲突 `AGENTS.md`，未恢复/删除任何文件，未执行 commit/push/PR？

## 10. Residual Risks / Owners

| 风险 | 影响 | Owner | 处理方式 |
|---|---|---|---|
| Runtime/Engine 空包冲动再次出现 | 架构完成感失真，后续实现可能绕过真实需求评审 | Controller / future planning worker | 通过本计划和后续 plan-review checklist 强制先证明触发条件 |
| README 当前四段生产路径与设计六层目标边界被误读为冲突 | 评审可能要求为了“目录齐全”创建空包 | Controller / docs owner | 在 docs-only alignment 中明确“六层是目标边界，当前生产路径没有 Runtime/Engine 是刻意 defer” |
| 外部 Dayu runtime 被重新包装进主链路 | 增加依赖面并破坏本项目边界 | Future implementation owner | plan review 必须执行 Dayu no-runtime-dependency checklist |
| 未来 LLM audit / Evidence Confirm 需求突然出现 | 可能需要 Runtime/Engine，但当前无契约 | Future Runtime/Engine owner | 另开独立 design + plan-review gate，先定义 typed contracts、事件流、失败语义和测试 |
| 年报访问边界被 Runtime/Engine 借口绕开 | PDF/cache/source internals 泄漏到上层 | Capability owner / reviewer | 所有文档读取仍经 `FundDocumentRepository`，新增 Runtime/Engine 只能调用稳定契约 |
| 本地 `AGENTS.md` 冲突 diff 被误纳入 | 覆盖用户提供的权威规则 | Controller / release owner | 不读取为真源、不修改、不暂存；需要用户显式决策 |

## 11. 最小下一步

把本计划送入 plan review。若 review 接受 defer decision，下一步只做 Slice 1 docs-only alignment；除非 reviewer 指出已有边界测试不足，否则不做 Slice 2。
